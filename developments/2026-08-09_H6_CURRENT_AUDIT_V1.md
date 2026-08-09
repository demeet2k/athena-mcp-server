# H6 CUT-01 — CURRENT-AUDIT REBIND

The original RED lineage was frozen at `114790cf5173ca5ab78d1b505849708b209f81a0`.

At PR publication time current `master` had advanced to `429a480a80eeefb9e2bff1ea3015adf571d76b0e`.

This branch exists only to audit that intervening master movement before any treatment is authorized.

Rules:

```text
FROZEN_RED_PARENT != CURRENT_SOURCE_AUDIT_PARENT
MASTER_MOVED != AUTOMATIC_GLOBAL_INVALIDATION
CHANGED_PATHS -> H6_DEPENDENCY_AUDIT -> REUSE_OR_RESPIN
NO_TREATMENT_IN_CURRENT_AUDIT_BRANCH
```
