# IF.data Two-Quarter Pilot Implementation Plan

> **For agentic workers:** Use Superpowers executing-plans inline, TDD, verification-before-completion and a final independent code review. Steps use checkboxes. João explicitly authorized execution and local adjustments; no further broad-direction or plan approval pause. Keep the plan and ledger locally, with no push/PR/merge/deploy.

**Goal:** Collect and inventory the individual Resumo report for 201012 and 202412, preserving evidence and a small temporal CVM/B3 metadata sample.

**Architecture:** A standard-library HTTP archive saves every body and manifest before interpretation. IF.data discovery and bounded collection feed a token-preserving inventory. Temporal metadata evidence stays separate from financial observations.

**Tech Stack:** Python 3.12+, urllib, csv, json, hashlib, decimal, unittest. No global package installation.

**Spec:** `docs/superpowers/specs/2026-10-01-ifdata-pilot-design.md`.

## Global Constraints

- Exact collection scope: periods 201012 and 202412, TipoInstituicao 3, Resumo only.
- Financial observations: IF.data only. CVM/B3: metadata only. No COSIF or issuer financial statements.
- Keep identifiers as strings and retain original rows and value tokens in derived records.
- No push/PR/merge/deploy, full history, academic prose, calendar, security or unrelated project changes.

## Review Focus

HTTP 200 with an error/HTML body must remain a failed dataset. Missing pages must not imply structural absence. Account identifiers with different labels must not collapse. Duplicates must be flagged rather than aggregated. Current CVM/B3 facts must not become historical listed-state assertions. Each condition is covered by the owning task's tests.

### Task 1: Reproducible acquisition evidence

**Files:** `bank_quality/archive.py`, `tests/test_archive.py`, `docs/engineering/reference-comparison.md`.

**Interfaces:** `fetch(url: str, root: Path, label: str, context: dict | None = None, timeout: float = 30) -> dict`; `load_body(manifest: dict, root: Path) -> bytes` verifies the saved hash.

- [x] Write offline HTTP-server tests proving exact bytes/hash/URL preservation, failure-body retention and no overwrite on repeated acquisition.
- [x] Run `python -m unittest discover -s tests -p test_archive.py -v`; observe missing-feature failures before implementation.
- [x] Implement immutable UUID-named body/manifest files and structured network diagnostics; preserve query and endpoint parameters.
- [x] Run the archive tests; expected all pass. Record inspected source revisions and MIT licenses. No reference code is imported wholesale.

### Task 2: Bounded real collector and fallback diagnostics

**Files:** `bank_quality/ifdata.py`, `bank_quality/__main__.py`, `tests/test_ifdata.py`, `scripts/run-pilot.ps1`.

**Interfaces:** `collect(root: Path) -> dict` returns per-quarter source outcomes with archived manifests, parsed rows and complete/incomplete state; `parse_odata(body: bytes) -> tuple[list[dict], str | None]` exposes continuation links.

- [x] Write tests for periods outside {201012,202412}, JSON shape/HTML errors, mismatched period/type, pagination links and failed cadastro with retained values.
- [x] Observe RED, implement validated report discovery and OData requests limited to TipoInstituicao 3/Resumo; preserve each page and capped retries.
- [x] Run tests to GREEN; run live discovery and both quarters. If service failures persist, inspect official portal assets, implement/test only an evidenced official CSV fallback, label it separately and record its raw export and source provenance.
- [x] Record actual outcomes without treating service failure as zero rows or historical absence.

### Task 3: Reproducible coverage and missingness

**Files:** `bank_quality/inventory.py`, `tests/test_inventory.py`, `data/derived/<run>/`, `reports/<run>/pilot.md`.

**Interfaces:** `classify(value: object) -> str`; `inventory(quarters: dict, output: Path) -> dict` writes source-row-preserving observations, institutions, variables, missingness and structural-comparison tables.

- [x] Write tests separating NA/NI/null/blank/zero/invalid values, string IDs, duplicate keys and unavailable structures; observe RED.
- [x] Implement Decimal-based value classification, explicit observed denominators, expected institution-variable grid and separate unobserved/structural states. Flag duplicates instead of summing.
- [x] Run tests to GREEN; regenerate inventories from archived real bodies. Verify counts, raw hashes and accepted schema, including fallback header evidence.

### Task 4: Small temporal CVM/B3 evidence and final verification

**Files:** `bank_quality/metadata.py`, `tests/test_metadata.py`, `data/derived/<run>/temporal-sample.csv`, `docs/engineering/pilot-execution.md`.

**Interfaces:** temporal records include entity, CNPJ/CVM code when actually observed, reference date, fact type, known/unknown state, evidence URL/hash, source date and limitation. No financial values.

- [x] Write tests showing current registration/listing cannot imply historical state and event-after-reference cannot prove registration at reference; observe RED.
- [x] Save a small official CVM registration/B3 equity evidence sample, with historical unknowns and separate registration/listing fields. Do not guess identity mappings.
- [x] Run `python -m unittest discover -s tests -v`; expected all pass. Run CLI replay against the raw archive; verify reproducibility and bounded scope.
- [x] Obtain independent review of implementation, plan/spec and result evidence; fix material defects with RED/GREEN tests and a green suite. Leave local changes reviewable and report factual blockers.
