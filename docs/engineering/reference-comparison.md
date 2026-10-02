# Selective IF.data reference inspection

Four repositories were cloned read-only into task-specific temporary directories. Their source, relevant mechanisms and MIT license were inspected before implementing the first-party pilot. No implementation text was copied into `bank_quality` or `scripts`. Retained upstream licenses and pinned revisions are in `third_party/references`.

| Source | Inspected revision | Useful mechanism | Pilot decision |
|---|---|---|---|
| [enzoomoreira/ifdata-bcb](https://github.com/enzoomoreira/ifdata-bcb/tree/58a1d98f911c22a104e99d5350823e83bf0ffa2d) | `58a1d98f911c22a104e99d5350823e83bf0ffa2d` | Documented OData discovery, individual type 3, period/report parameters | Use evidenced endpoint contracts; omit full-history/all-report download and casts that discard raw Saldo |
| [wilsonfreitas/python-bcb](https://github.com/wilsonfreitas/python-bcb/tree/c431f1dd4c5321658d7879f9ef825df427bdd3fb) | `c431f1dd4c5321658d7879f9ef825df427bdd3fb` | IFdata OData/report discovery and consolidation cautions | Keep explicit institution scope, raw tokens and original pages; no wholesale library dependency |
| [alexcamargos/bacen-ifdata-scraper](https://github.com/alexcamargos/bacen-ifdata-scraper/tree/e443842fe742a1df4adae7fb57eae13e703af655) | `e443842fe742a1df4adae7fb57eae13e703af655` | Official portal report selection/schema mechanisms | Use portal as labeled fallback; omit broad warehouse/ETL scope |
| [knuppe/bacen_ifdata](https://github.com/knuppe/bacen_ifdata/tree/842008b65f768aa534401e2644d1bc4e799d31f1) | `842008b65f768aa534401e2644d1bc4e799d31f1` | Browser CSV export and header handling | Preserve immutable exports; reject source CSV rewriting and NA/NI removal |

All four licenses verified MIT at the inspected revisions. This pilot retains attribution/provenance while using a small standard-library Python implementation and an optional first-party browser transport. Matt Pocock skills are separately pinned to `d81f3a183412e71a5b1e84ca21bc1a35eea03a60`; their per-file hashes and MIT notice are retained.
