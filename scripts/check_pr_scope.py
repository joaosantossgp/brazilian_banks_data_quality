"""Deterministic offline PR scope observation; Python 3.12, standard library.

The caller MUST supply validator/policy from an independently trusted base and
an independently collected complete filename inventory. This program cannot
authenticate the origin of arbitrary local files. It never reads PR contents.
Proposal: https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/17
"""
import argparse
import json
from pathlib import Path
import re
import sys
import unicodedata

ROLES = {"role:research", "role:implementation", "role:review", "role:integration"}
AREAS = {"area:converter", "area:contract-2025", "area:academic-indicators"}
# Defense in depth: ordinary tasks cannot edit these even if a scope is broad.
CONTROL = ("AGENTS.md", "README.md", ".github/", ".gitignore",
           "scripts/check_pr_scope.py", "tests/test_pr_scope.py", "tests/fixtures/pr_scope/",
           "docs/agents/issue-tracker.md",
           "docs/engineering/pr-scope-observation.md",
           "docs/superpowers/specs/2026-10-02-governance-research-design.md",
           "docs/superpowers/plans/2026-10-02-governance-foundation-plan.md")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def fields(value, names):
    require(isinstance(value, dict) and set(value) == set(names.split()), "invalid object fields")


def label(value):
    require(isinstance(value, str) and 0 < len(value) <= 200
            and all(ord(c) >= 32 and ord(c) != 127 for c in value), "invalid identifier")


def path(value, scope=False):
    require(isinstance(value, str) and 0 < len(value) <= 4096, "invalid path")
    require(unicodedata.normalize("NFC", value) == value, "noncanonical Unicode path")
    require(not any(ord(c) < 32 or ord(c) == 127 for c in value), "control character in path")
    require(not any(c in value for c in "\\:*?[]"), "unsupported path syntax")
    name = value[:-1] if scope and value.endswith("/") else value
    require(all(part not in ("", ".", "..") for part in name.split("/")), "noncanonical path")
    require(all(not part.endswith((".", " ")) for part in name.split("/")),
            "noncanonical Windows path component")
    return value


def scopes(value):
    require(isinstance(value, list), "scopes must be a list")
    for item in value:
        path(item, scope=True)
    require(len({item.casefold() for item in value}) == len(value), "duplicate or case-colliding scope")
    return value


def matches(name, scope):
    return name.startswith(scope) if scope.endswith("/") else name == scope


def overlaps(a, b):
    # Portable ownership/deny rules cannot rely on a case-sensitive filesystem.
    a, b = a.casefold(), b.casefold()
    if a.endswith("/") and b.endswith("/"):
        return a.startswith(b) or b.startswith(a)
    return matches(b, a) or matches(a, b)


def validate_policy(policy):
    fields(policy, "schema_version version mode integrator forbidden_paths sensitive_paths shared_paths tasks pr_bindings")
    require(type(policy["schema_version"]) is int and policy["schema_version"] == 1, "unsupported policy schema")
    require(policy["mode"] == "observation", "only observation mode is supported")
    label(policy["version"])
    label(policy["integrator"])
    for name in ("forbidden_paths", "sensitive_paths", "shared_paths"):
        scopes(policy[name])
    require(isinstance(policy["tasks"], dict) and len(policy["tasks"]) <= 500, "invalid tasks")
    tasks = policy["tasks"]
    for task_id, task in tasks.items():
        label(task_id)
        fields(task, "owner role area state issue branch allowed_paths forbidden_paths dependencies")
        for name in ("owner", "issue", "branch"):
            label(task[name])
        require(task["role"] in ROLES and task["area"] in AREAS, "unknown role or area")
        require(task["state"] in ("ready", "blocked", "done"), "unknown task state")
        require(scopes(task["allowed_paths"]), "empty task allowlist")
        scopes(task["forbidden_paths"])
        require(isinstance(task["dependencies"], list), "invalid dependencies")
        for dependency in task["dependencies"]:
            require(isinstance(dependency, str) and dependency in tasks, "unknown dependency")
        require(len(set(task["dependencies"])) == len(task["dependencies"]), "duplicate dependency")
        is_integrator = task["owner"] == policy["integrator"] and task["role"] == "role:integration"
        if not is_integrator:
            for scope in task["allowed_paths"]:
                require(not any(overlaps(scope, shared) for shared in policy["shared_paths"]),
                        "shared scopes belong only to the named integrator")
    # Completed tasks retain history but no longer reserve their paths.
    active = [(name, task) for name, task in tasks.items() if task["state"] != "done"]
    for index, (left_id, left) in enumerate(active):
        for right_id, right in active[index + 1:]:
            require(not any(overlaps(a, b) for a in left["allowed_paths"] for b in right["allowed_paths"]),
                    f"OVERLAP: {left_id} / {right_id}")
    visited, visiting = set(), set()

    def visit(name):
        require(name not in visiting, "dependency cycle")
        if name in visited:
            return
        visiting.add(name)
        for dependency in tasks[name]["dependencies"]:
            visit(dependency)
        visiting.remove(name)
        visited.add(name)

    for task_id in tasks:
        visit(task_id)
    require(isinstance(policy["pr_bindings"], dict), "invalid PR bindings")
    for number, task_id in policy["pr_bindings"].items():
        require(isinstance(number, str) and re.fullmatch(r"[1-9][0-9]*", number), "invalid PR number")
        require(isinstance(task_id, str) and task_id in tasks, "unknown task binding")


def validate_changes(changes):
    fields(changes, "schema_version pr_number policy_version base_sha head_sha complete changed_files files")
    require(type(changes["schema_version"]) is int and changes["schema_version"] == 1, "unsupported change schema")
    require(type(changes["pr_number"]) is int and changes["pr_number"] > 0, "invalid PR number")
    label(changes["policy_version"])
    for name in ("base_sha", "head_sha"):
        require(isinstance(changes[name], str) and re.fullmatch(r"[a-f0-9]{40}", changes[name]), "invalid SHA")
    require(changes["complete"] is True, "incomplete filename inventory")
    require(type(changes["changed_files"]) is int and 0 < changes["changed_files"] <= 3000, "invalid file count")
    require(isinstance(changes["files"], list) and len(changes["files"]) == changes["changed_files"], "truncated filename inventory")
    seen = set()
    for entry in changes["files"]:
        require(isinstance(entry, dict), "invalid change entry")
        status = entry.get("status")
        require(status in ("added", "modified", "removed", "renamed"), "unsupported change status")
        fields(entry, "filename status previous_filename" if status == "renamed" else "filename status")
        names = [path(entry["filename"])]
        if status == "renamed":
            names.append(path(entry["previous_filename"]))
        for name in names:
            folded = name.casefold()
            require(folded not in seen, "duplicate or case-colliding changed path")
            seen.add(folded)


def validate(policy, changes, expected_base, expected_head, expected_pr):
    result = {"mode": "observation", "verdict": "fail", "errors": []}
    try:
        validate_policy(policy)
    except (ValueError, TypeError, KeyError, RecursionError) as error:
        result["errors"].append(f"POLICY: {error}")
        return result
    result["policy_version"] = policy["version"]
    try:
        validate_changes(changes)
        require(isinstance(expected_base, str) and re.fullmatch(r"[a-f0-9]{40}", expected_base), "invalid expected base")
        require(isinstance(expected_head, str) and re.fullmatch(r"[a-f0-9]{40}", expected_head), "invalid expected head")
        require(type(expected_pr) is int and expected_pr > 0, "invalid expected PR")
    except (ValueError, TypeError, KeyError) as error:
        result["errors"].append(f"INPUT: {error}")
        return result
    result.update(base_sha=changes["base_sha"], head_sha=changes["head_sha"], pr_number=changes["pr_number"])
    errors = result["errors"]
    if (changes["base_sha"], changes["head_sha"], changes["pr_number"]) != (expected_base, expected_head, expected_pr):
        errors.append("REVISION: inventory does not match independently selected PR/base/head")
    if changes["policy_version"] != policy["version"]:
        errors.append("VERSION: inventory does not match base policy version")
    task_id = policy["pr_bindings"].get(str(expected_pr))
    if task_id is None:
        errors.append("UNKNOWN_PR: no binding in trusted base policy")
        return result
    task = policy["tasks"][task_id]
    result.update(task=task_id, owner=task["owner"])
    if task["state"] != "ready":
        errors.append("TASK_STATE: task is not ready")
    for dependency in task["dependencies"]:
        if policy["tasks"][dependency]["state"] != "done":
            errors.append(f"DEPENDENCY: {dependency} is not done")
    integrator = task["owner"] == policy["integrator"] and task["role"] == "role:integration"
    for entry in changes["files"]:
        names = [entry["filename"]]
        if entry["status"] == "renamed":
            names.append(entry["previous_filename"])
        for name in names:
            if any(matches(name.casefold(), scope.casefold()) for scope in policy["forbidden_paths"] + task["forbidden_paths"]):
                errors.append(f"FORBIDDEN: {name}")
            if any(matches(name.casefold(), scope.casefold()) for scope in
                   list(CONTROL) + policy["sensitive_paths"] + policy["shared_paths"]) and not integrator:
                errors.append(f"CONTROL: {name} requires the named integrator and an explicit allowlist")
            if not any(matches(name, scope) for scope in task["allowed_paths"]):
                errors.append(f"OUT_OF_SCOPE: {name}")
    if not errors:
        result["verdict"] = "pass"
    return result


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def load_json(filename):
    with Path(filename).open("rb") as source:
        body = source.read(4_000_001)
    require(len(body) <= 4_000_000, "JSON input exceeds size limit")
    return json.loads(body.decode("utf-8"), object_pairs_hook=unique_object)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", required=True, help="JSON from trusted base, never PR head")
    parser.add_argument("--changes", required=True, help="Complete filename inventory, never executable content")
    parser.add_argument("--base-sha", required=True)
    parser.add_argument("--head-sha", required=True)
    parser.add_argument("--pr", required=True, type=int)
    args = parser.parse_args()
    try:
        result = validate(load_json(args.policy), load_json(args.changes), args.base_sha, args.head_sha, args.pr)
        exit_code = 0 if result["verdict"] == "pass" else 1
    except (OSError, ValueError, TypeError, RecursionError):
        # Do not disclose local paths or echo untrusted parser input in published output.
        result = {"mode": "observation", "verdict": "fail", "errors": ["INPUT: unreadable or invalid JSON"]}
        exit_code = 2
    print(json.dumps(result, ensure_ascii=True, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
