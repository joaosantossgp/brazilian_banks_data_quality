"""Offline behavior tests. Fixtures contain no financial data or PR code."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import tracemalloc
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/check_pr_scope.py"
FIXTURES = ROOT / "tests/fixtures/pr_scope"
BASE = "1" * 40
HEAD = "2" * 40


class ScopeTests(unittest.TestCase):
    def setUp(self):
        self.policy = json.loads((FIXTURES / "policy.json").read_text(encoding="utf-8"))
        self.changes = json.loads((FIXTURES / "changes.json").read_text(encoding="utf-8"))

    def check(self):
        # RED is a useful assertion when the production entrypoint does not exist yet.
        self.assertTrue(SCRIPT.is_file(), "Missing production checker")
        spec = importlib.util.spec_from_file_location("scope_checker", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.validate(self.policy, self.changes, BASE, HEAD, self.changes["pr_number"])

    def change(self, name, status="modified", previous=None):
        entry = {"filename": name, "status": status}
        if previous is not None:
            entry["previous_filename"] = previous
        self.changes["files"] = [entry]
        self.changes["changed_files"] = 1

    def reject(self, code):
        result = self.check()
        self.assertEqual(result["verdict"], "fail", result)
        self.assertTrue(any(code in error for error in result["errors"]), result)

    def test_complete_allowed_added_modified_pass(self):
        self.assertEqual(self.check()["verdict"], "pass")

    def test_all_supported_operations_checked(self):
        for status in ["added", "modified", "removed", "renamed"]:
            with self.subTest(status=status):
                self.change("bank_quality/parquet.py", status,
                            "tests/test_parquet.py" if status == "renamed" else None)
                self.assertEqual(self.check()["verdict"], "pass")

    def test_removed_unknown_rejected(self):
        self.change("unknown.txt", "removed")
        self.reject("OUT_OF_SCOPE")

    def test_rename_old_path_checked(self):
        self.change("tests/test_parquet.py", "renamed", "bank_quality/archive.py")
        self.reject("FORBIDDEN")

    def test_rename_new_path_checked(self):
        self.change("docs/unknown.md", "renamed", "bank_quality/parquet.py")
        self.reject("OUT_OF_SCOPE")

    def test_rename_from_policy_is_sensitive(self):
        self.change("tests/test_parquet.py", "renamed", ".github/governance/scope-policy.json")
        self.reject("CONTROL")

    def test_candidate_policy_cannot_self_grant(self):
        self.change(".github/governance/scope-policy.json")
        # The changed file's bytes are intentionally never read. Even a self-granting
        # policy in the head is just a path against the independently supplied base.
        self.reject("CONTROL")

    def test_head_cannot_supply_a_policy_field(self):
        self.changes["policy"] = {"allowed_paths": ["*"]}
        self.reject("INPUT")

    def test_integrator_has_explicit_limited_allowlist(self):
        self.changes["pr_number"] = 44
        self.change("AGENTS.md")
        self.assertEqual(self.check()["verdict"], "pass")
        self.change(".github/workflows/ci.yml")
        self.reject("OUT_OF_SCOPE")

    def test_non_integrator_cannot_claim_shared_control(self):
        self.policy["tasks"]["converter-fixture"]["allowed_paths"].append("AGENTS.md")
        self.change("AGENTS.md")
        self.reject("POLICY")

    def test_global_forbidden_beats_integrator_allowlist(self):
        self.changes["pr_number"] = 44
        self.policy["tasks"]["integration-fixture"]["allowed_paths"].append("data/raw/x.json")
        self.change("data/raw/x.json")
        self.reject("FORBIDDEN")

    def test_overlapping_reservations_fail_even_when_diff_is_elsewhere(self):
        self.policy["tasks"]["research-fixture"]["allowed_paths"].append("bank_quality/")
        self.reject("OVERLAP")

    def test_prefix_is_component_bounded(self):
        self.changes["pr_number"] = 43
        self.change("docs/research/contract-2025evil/source.md")
        self.reject("OUT_OF_SCOPE")
        self.change("docs/research/contract-2025/source.md")
        self.assertEqual(self.check()["verdict"], "pass")

    def test_case_variant_cannot_bypass_forbidden_paths(self):
        self.policy["tasks"]["converter-fixture"]["allowed_paths"] = ["DATA/raw/x.json"]
        self.change("DATA/raw/x.json")
        self.reject("FORBIDDEN")

    def test_case_variant_reservations_overlap(self):
        self.policy["tasks"]["research-fixture"]["allowed_paths"] = ["BANK_QUALITY/parquet.py"]
        self.reject("OVERLAP")

    def test_case_variant_shared_reservation_requires_integrator(self):
        self.policy["tasks"]["converter-fixture"]["allowed_paths"].append("agents.md")
        self.reject("POLICY")

    def test_bad_paths_fail_closed(self):
        for name in ["../AGENTS.md", "/AGENTS.md", "C:/file", "docs\\x.md",
                     "docs//x.md", "docs/./x.md", "docs/x/../x.md", "docs/x\n.md",
                     "docs/x\x00.md", "docs/x\u007f.md", "docs/e\u0301.md",
                     "docs/x.md/", "docs/*.md", "docs/x?.md", ""]:
            with self.subTest(name=repr(name)):
                self.change(name)
                self.reject("INPUT")

    def test_windows_trailing_aliases_in_inventory_fail_closed(self):
        self.policy["tasks"]["converter-fixture"]["allowed_paths"] = ["scripts/"]
        for name in ["scripts/check_pr_scope.py.", "scripts/check_pr_scope.py ",
                     "scripts./check_pr_scope.py", "scripts /check_pr_scope.py"]:
            with self.subTest(name=name, endpoint="filename"):
                self.change(name)
                self.reject("INPUT")
            with self.subTest(name=name, endpoint="previous_filename"):
                self.change("scripts/new.py", "renamed", name)
                self.reject("INPUT")

    def test_windows_trailing_aliases_in_policy_fail_closed(self):
        original = copy.deepcopy(self.policy)
        for field in ["forbidden_paths", "sensitive_paths", "shared_paths",
                      "allowed_paths", "task_forbidden_paths"]:
            for name in ["scripts/check_pr_scope.py.", "scripts/check_pr_scope.py ",
                         "scripts./", "scripts /", "docs./research/", "docs /research/"]:
                with self.subTest(field=field, name=name):
                    self.policy = copy.deepcopy(original)
                    if field == "allowed_paths":
                        self.policy["tasks"]["converter-fixture"][field] = [name]
                    elif field == "task_forbidden_paths":
                        self.policy["tasks"]["converter-fixture"]["forbidden_paths"] = [name]
                    else:
                        self.policy[field] = [name]
                    self.reject("POLICY")

    def test_missing_rename_source_fails(self):
        self.change("bank_quality/parquet.py", "renamed")
        self.reject("INPUT")

    def test_previous_path_on_non_rename_fails(self):
        self.change("bank_quality/parquet.py", "modified", "tests/test_parquet.py")
        self.reject("INPUT")

    def test_unknown_status_fails(self):
        for status in ["copied", "changed", "unmerged", "T", "", None]:
            with self.subTest(status=status):
                self.change("bank_quality/parquet.py", status)
                self.reject("INPUT")

    def test_incomplete_or_truncated_list_fails(self):
        self.changes["complete"] = False
        self.reject("INPUT")
        self.changes["complete"] = True
        self.changes["changed_files"] = 3
        self.reject("INPUT")
        self.changes["changed_files"] = 3001
        self.reject("INPUT")

    def test_duplicate_and_case_collision_fail(self):
        for name in ["bank_quality/parquet.py", "BANK_QUALITY/parquet.py"]:
            self.changes["files"][1] = {"filename": name, "status": "added"}
            self.reject("INPUT")

    def test_rename_same_path_fails(self):
        self.change("bank_quality/parquet.py", "renamed", "bank_quality/parquet.py")
        self.reject("INPUT")

    def test_unknown_pr_fails(self):
        self.changes["pr_number"] = 999
        self.reject("UNKNOWN_PR")

    def test_base_head_mismatch_fails(self):
        for field in ["base_sha", "head_sha"]:
            original = self.changes[field]
            self.changes[field] = "3" * 40
            self.reject("REVISION")
            self.changes[field] = original

    def test_version_mismatch_fails(self):
        self.changes["policy_version"] = "candidate-v999"
        self.reject("VERSION")

    def test_open_dependency_fails(self):
        self.policy["tasks"]["converter-fixture"]["dependencies"] = ["research-fixture"]
        self.reject("DEPENDENCY")
        self.policy["tasks"]["research-fixture"]["state"] = "done"
        self.assertEqual(self.check()["verdict"], "pass")

    def test_unknown_dependency_and_cycle_fail(self):
        self.policy["tasks"]["converter-fixture"]["dependencies"] = ["missing"]
        self.reject("POLICY")
        self.policy["tasks"]["converter-fixture"]["dependencies"] = ["research-fixture"]
        self.policy["tasks"]["research-fixture"]["dependencies"] = ["converter-fixture"]
        self.reject("POLICY")

    def test_not_ready_fails(self):
        for state in ["blocked", "done"]:
            self.policy["tasks"]["converter-fixture"]["state"] = state
            self.reject("TASK_STATE")

    def test_bad_policy_schema_paths_bindings_and_unknown_fields_fail(self):
        original = copy.deepcopy(self.policy)
        mutations = [lambda p: p.update(version=""), lambda p: p.update(mode="required"),
                     lambda p: p.update(allow_everything=True),
                     lambda p: p["pr_bindings"].update({"45": "missing"}),
                     lambda p: p["tasks"]["converter-fixture"].update(allowed_paths=["*"]),
                     lambda p: p["tasks"]["converter-fixture"].update(role="role:admin"),
                     lambda p: p["tasks"]["converter-fixture"].update(area="area:all"),
                     lambda p: p["tasks"]["converter-fixture"].update(owner=""),
                     lambda p: p["tasks"]["converter-fixture"].update(allowed_paths=[])]
        for mutation in mutations:
            self.policy = copy.deepcopy(original)
            mutation(self.policy)
            self.reject("POLICY")

    def test_empty_diff_and_boolean_count_fail(self):
        self.changes["files"] = []
        self.changes["changed_files"] = 0
        self.reject("INPUT")
        self.changes["changed_files"] = True
        self.reject("INPUT")

    def test_cli_exit_codes_json_and_duplicate_keys(self):
        self.assertTrue(SCRIPT.is_file(), "Missing production checker")
        with tempfile.TemporaryDirectory() as folder:
            policy = Path(folder) / "policy.json"
            changes = Path(folder) / "changes.json"
            policy.write_text(json.dumps(self.policy), encoding="utf-8")
            command = [sys.executable, "-B", str(SCRIPT), "--policy", str(policy),
                       "--changes", str(changes), "--base-sha", BASE, "--head-sha", HEAD, "--pr", "42"]
            for name, expected in [("bank_quality/parquet.py", 0), ("unknown.txt", 1)]:
                self.change(name)
                changes.write_text(json.dumps(self.changes), encoding="utf-8")
                result = subprocess.run(command, text=True, capture_output=True, check=False)
                self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
                self.assertEqual(json.loads(result.stdout)["verdict"], "pass" if expected == 0 else "fail")
            changes.write_text('{"schema_version":1,"schema_version":2}', encoding="utf-8")
            result = subprocess.run(command, text=True, capture_output=True, check=False)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(json.loads(result.stdout)["verdict"], "fail")

    def test_oversized_json_rejected_with_bounded_memory(self):
        spec = importlib.util.spec_from_file_location("scope_checker", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as folder:
            oversized = Path(folder) / "oversized.json"
            oversized.write_bytes(b" " * 6_000_000)
            tracemalloc.start()
            try:
                with self.assertRaises(ValueError):
                    module.load_json(oversized)
                _, peak = tracemalloc.get_traced_memory()
                self.assertLess(peak, 5_000_000, "Input limit must bound reads before parsing")
            finally:
                tracemalloc.stop()


if __name__ == "__main__":
    unittest.main()
