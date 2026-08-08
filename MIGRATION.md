# ATHENA Unified Migration Law

This repository has undergone both a destructive historical active-tree reset and a subsequent **non-destructive runtime braid**. The governing migration policy is therefore explicit:

`UNKNOWN/LEGACY != GARBAGE`

`PRUNE/HIBERNATE != ERASE`

`OLD API NAME != PERMANENT AUTHORITY`

`CONTENT COPIED != LINEAGE MERGED`

## 1. Historical reset boundary

Previous pre-rebuild repository state remains pinned in Git history. A legacy file is not canonical merely because it once existed.

Legacy admission remains:

`DISCOVER → HASH → CLASSIFY → CCR SEARCH → OID/VID → SOURCE → KC144 → JSPACE → SCALE → TEST/EVIDENCE → STATUS`.

Do not bulk-copy unclassified legacy folders into the active runtime.

## 2. Current migration target

The current executable target is:

`athena-canonical-mcp 2.5.0`

with one composed runtime containing:

- base identity/JSPACE/SCALE/KC144/polycoordinate/crystal/Git substrate;
- Collective Runtime V1 + Growth V1 + Memory V2 + Learning V3 + Ecology V4 + Science V5 + Discovery V6;
- AOR.3 + branch evolution + Y.1 authority;
- EQ.1 / SX.1 / RAG.1 / HUG.ABI.1 / GAP.1 / FIELD.1;
- typed AOR×Collective transport;
- CYCLE.1;
- SCHEMA.2 / OMEGA.1 / RECON.1;
- SELFTEST.1 / STARTUP.1 / SURFACE.2 / COMPOSITION.2 / PROMOTION.1;
- live unified manifest/MAXDEV.

## 3. Database migration — SCHEMA.2

Schema adoption is additive and receipt-bearing.

### v1 — inventory existing modular schema

The first migration records the already-created modular tables and component versions. It does not destructively rebuild existing data.

### v2 — RECONRUN expected-ref contract

Legacy intermediate databases may contain `reconstruction_runs` without `expected_refs_json`. V2 performs an explicit additive column migration:

`ALTER TABLE reconstruction_runs ADD COLUMN expected_refs_json ...`

RECON persistence uses **named-column inserts**, so logical field meaning does not depend on SQLite physical column order after `ALTER TABLE`.

Verification checks critical tables and critical columns, not only a version integer.

If:

`database_schema_version > runtime_supported_version`

then startup returns a future-schema block rather than silently downgrading.

Unknown legacy tables/rows survive migration unchanged unless a separately authorized migration explicitly owns them.

## 4. Restart migration

Persistent ledgers are expected to survive close/reopen:

- AORRUN;
- FIELDRUN;
- TRANSPORTRUN;
- RECONRUN;
- CYCLE/CYCLEEV;
- PROMRUN;
- migration receipts.

A CYCLE halted in `WAITING_*` must resume at that phase without replaying fictional semantic work.

## 5. Claim namespace migration — critical V6 correction

Upstream V6 originally reused names that overlap AOR Y.1 canonical authority.

The unified runtime **does not** preserve that collision.

Canonical authority remains:

- `athena_claim_register`
- `athena_claim_state`
- `athena_claim_promote`
- `athena_claim_challenge`
- `athena_claim_resolve_canonical_challenge`.

V6 science-shadow replication/falsification is migrated to:

- `athena_discovery_claim_register`
- `athena_discovery_claim_witness`
- `athena_discovery_claim_state`.

There is intentionally no compatibility alias from old V6 shadow `athena_claim_*` names because those names are already occupied by a stronger, canonical Y.1 authority contract. Silent first-wins dispatch would be semantically unsafe.

Migration law:

`V6_SHADOW_CLAIM --explicit evidence/witness route--> Y1 consideration`

never:

`V6_SHADOW_CLAIM --implicit RPC alias--> Y1 mutation`.

## 6. Collective V3 telemetry migration

V3 runtime metering is retained for operational tools. Canonical introspection is excluded from self-metering:

- OMEGA state;
- schema status/plan/verify;
- SELFTEST / STARTUP / SURFACE;
- runtime manifest/MAXDEV;
- benchmark/Git status;
- reconstruction reads/verifies.

Reason:

`OBSERVE(OMEGA) != MUTATE(OMEGA)`.

Without this exclusion, reading OMEGA would record runtime usage and change the next OMEGA digest, creating an observer-effect loop.

## 7. AOR + Collective migration law

Do not merge the systems by sharing untyped scores.

- AOR determines developmental eligibility and successor frontier;
- Collective determines execution/science organization after eligibility;
- Collective predictions/posteriors/credits are model/organizational state;
- Y1 remains the canonical claim authority surface;
- transport between organs must be explicit and replayable.

Specifically:

`pheromone != evidence`

`consensus != authority`

`posterior != truth`

`EIG != evidence`

`discovery shadow != Y1 authority`.

## 8. Runtime surface migration

A module is not considered integrated merely because its file exists.

Integration requires:

1. tool schema advertised;
2. dispatcher route exists;
3. runtime organ is initialized or explicitly classified lazy;
4. resource surface exists when applicable;
5. SURFACE.2 requires it;
6. COMPOSITION.2 verifies resident organs;
7. regression/smoke witness exercises it;
8. live manifest/OMEGA describe it.

This rule was introduced after post-GAP module files existed but were not wired into the live registry.

## 9. CI migration

The release gate is split into independent jobs:

`syntax ∧ unit ∧ critical-invariants ∧ dependent-smoke`.

Critical invariants include:

- schema migration/restart;
- unknown legacy-state preservation;
- three-domain CAS isolation;
- whole CYCLE fail-closed behavior;
- SURFACE/COMPOSITION;
- SELFTEST/STARTUP;
- live manifest/MAXDEV;
- package/server metadata + RPC uniqueness;
- V6 discovery↔Y1 namespace firewall;
- AOR×Collective transport;
- promotion predicate.

Smoke runs only after the first three jobs pass.

## 10. Git lineage migration

Copying current-master files into a branch is not sufficient lineage reconciliation.

Final braid procedure:

1. establish a fully green unified content checkpoint;
2. identify current `master` SHA;
3. integrate every current-master runtime/spec/test/document semantic change, resolving conflicts explicitly;
4. create a **true two-parent merge commit** whose tree is the verified unified content and whose parents are the unified pre-merge head and exact current-master head;
5. confirm branch is no longer behind that master head;
6. re-run syntax/unit/critical/smoke on the merge head;
7. only then provide exact-head CI/smoke attestations to PROMOTION.1;
8. keep the PR draft until the post-merge head is qualified.

If `master` advances again before qualification, repeat from step 2. Do not reuse a PROMRUN from an older head.

## 11. Post-merge verification

The ancestry-complete head should be exercised against:

- fresh zero-state database;
- migrated intermediate database;
- unknown legacy-state fixture;
- close/reopen restart;
- stale semantic VID;
- stale topology version;
- stale Git HEAD;
- V1–V6 Collective regression suites;
- AOR/Y/EQ/SX/RAG/HUG/GAP/FIELD suites;
- V6/Y1 namespace firewall;
- combined V6 science + AOR + fail-closed CYCLE + final-emission smoke.

No release/promotion claim is made until those witnesses belong to the **same exact merge head**.
