# Approved IF.data two-quarter pilot design

Reconstructed on 2026-10-01 from João's explicitly approved verbal and written design. The previous computer's files were not accessed. Autonomous implementation, runs, tests and local adjustments were subsequently authorized.

## Problem Statement

Before collecting the thesis dataset, João needs evidence that IF.data can support a reproducible quality inventory across distant quarters, without erasing missing-value meanings or selecting historical banks by current survival. The thesis focus/title remains capital aberto; its final unit of analysis is not yet settled.

## Solution

A small first-party Python collector retrieves official IF.data material for 201012 and 202412, initially individual institutions and the Resumo report. An immutable raw archive records every successful or failed acquisition. Reproducible derived inventories expose institutions, identifiers, report variables, observed values, missingness and structural differences. A separate small CVM/B3 metadata sample records dated facts and unknowns.

## User Stories

1. As the researcher, I can reproduce each request from its exact URL and parameters.
2. As the researcher, I can verify the SHA-256 of every raw body and see its retrieval time and HTTP outcome.
3. As the researcher, I can retain failures instead of mistaking service downtime for historical absence.
4. As the researcher, I can compare institutions and raw identifiers in December 2010 and December 2024 without assuming an identity mapping.
5. As the researcher, I can inspect variable identities and indicators in the individual Resumo report.
6. As the researcher, I can distinguish NA, NI, literal null, JSON null, blank, zero, unparsable values and unobserved cells.
7. As the researcher, I can see structural differences separately from cell-level missingness.
8. As the researcher, I can inspect CVM registration events and B3 equity-listing evidence separately, with unknown historical states where evidence is insufficient.
9. As the researcher, I can see which outputs are provisional and which requests succeeded.

## Implementation Decisions

- Python 3.12 or later; standard-library collector and offline tests, avoiding global dependency installation.
- Exact collection scope: periods 201012 and 202412, TipoInstituicao 3, Resumo only. Discover the report code from official metadata where possible; fail explicitly if it cannot be verified.
- Financial observations: IF.data only. CVM/B3: metadata only. No COSIF or issuer financial statements.
- Append-only raw files plus request manifests containing URL, decoded query parameters, explicit endpoint parameters, requested and final URL, UTC start/retrieval times, status, headers, byte count, SHA-256 and diagnostics.
- Preserve failures and network exceptions. Bound retries and request timeouts. Never silently accept truncated or failed bodies as datasets.
- OData is preferred. If failures persist, investigate and test an explicitly labeled official IF.data portal CSV fallback. Save its source assets/export and provenance before accepting its structure.
- Keep identifiers as strings and retain original rows and value tokens in derived records. Do not pad, reinterpret or merge identifiers without evidence.
- Inventory observed variables by report/account/column identity; compare presence between periods. Infer structural absence only when both requested report structures were actually acquired.
- A cadastro failure does not discard financial rows; it makes name/registration coverage explicitly incomplete. No guessed conglomerate or issuer matches.
- CVM's current cadastro is not a historical panel. Event dates may support specific assertions; current status cannot establish a historical state. B3 current company pages cannot establish 2010/2024 listing without dated evidence.
- Four reference repositories are inspected at recorded revisions, licenses retained if anything is reused. Selective source-informed first-party implementation; reject cleaning that conflates NA/NI/null/zero.
- Wider IF.data entities can inform a cheap secondary comparison only; they do not redefine the thesis population.

## Testing Decisions

Use public behavior seams: archive acquisition through a local HTTP server; parser/inventory from synthetic source-shaped responses; complete bounded CLI runs from injected fixture responses. Test HTTP failure retention, duplicate acquisition without overwrite, malformed and mismatched-period responses, duplicate institution-variable cells, missing-value distinctions, partial-source failure and out-of-scope periods. Then run the real two-quarter pilot and verify raw hashes, row counts, complete pages and metadata evidence. Synthetic fixtures are always labeled as such and never counted as collected data.

## Out of Scope

Full historical collection, final institution/conglomerate unit selection, guessed issuer mapping, academic prose, separate CVM normalization work, calendar edits, security changes, global skill edits and any code push/PR/merge/deploy.

## Further Notes

Collection target: October 9. Complete manuscript: October 21. Advisor review: October 22 through November 5, the approved 15-day window. No calendar action is part of this task. Existing Project 3 is retained. Local git state and published state must always be described separately.
