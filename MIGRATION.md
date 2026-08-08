# ATHENA Runtime Migration

## Active-tree provenance

The active `master` tree was rebuilt from scratch during the 2026-08-07 rebuild. Previous repository state remains pinned at `archive/pre-rebuild-2026-08-07` and in Git history, but no legacy file is canonical merely because it existed before the rebuild.

Legacy admission remains:

`DISCOVER → HASH → CLASSIFY → CCR SEARCH → OID/VID → SOURCE → KC144 → JSPACE → SCALE → TEST/EVIDENCE → STATUS`.

Do not bulk-copy legacy folders into the runtime.

## 2.2.x -> 2.3.0

`athena-canonical-mcp 2.3.0` adds Collective Ecology V4 on top of the existing V1/V2/V3 collective stack.

No destructive database migration is required for the V4 tables. `Server(...)` initializes the collective runtime layers and executes `CREATE TABLE IF NOT EXISTS` for the new persistent control-plane surfaces.

New persistent V4 surfaces include:

- contextual-bandit arm/posterior state and reward observations;
- causal-credit events;
- per-worker resource/cost observations and aggregate profiles;
- learned scale-diffusion observations/statistics;
- restricted antibody regression-run evidence;
- topology→JSPACE projection-saga journal.

Existing semantic objects, versions, events, JSPACE edges, manifestations, coordinate tables, V2 pheromones/topologies/antibodies and V3 budgets/policy/elder/antibody-variant state are not bulk-rewritten by the upgrade.

## Authority compatibility

The upgrade does not weaken existing CAS boundaries:

- semantic writes still require current expected VID where applicable;
- Git checkpoint writes still require expected Git HEAD;
- collective topology writes still require expected topology version;
- learned V3 policy writes still require expected policy version.

V4 contextual-bandit and causal-credit tables are observational learning state. They do not acquire semantic mutation authority.

## New projection bridge

V4 adds an explicit route from accepted collective topology into JSPACE. This is not automatic on topology mutation.

Recommended sequence:

1. read current topology/version;
2. read current semantic global event head;
3. optionally read current Git HEAD;
4. call `athena_projection_prepare` or `athena_topology_project_jspace(..., dry_run=true)`;
5. inspect the derived structural edges;
6. re-read heads if the environment is concurrent;
7. call live `athena_topology_project_jspace` with exact expected heads;
8. inspect projection saga status;
9. if `COMPENSATION_REQUIRED`, resolve explicitly rather than assuming rollback occurred.

The current runtime cannot turn SQLite semantic mutation plus Git commit into one distributed ACID transaction; it therefore journals a recovery saga instead of mislabeling sequential commits as atomic.

## Regression-witness migration

Legacy failure antibodies may contain free-form regression references. V4 executes only references matching:

`tests/<repository path>.py::TestCase::test_method`.

Older non-executable references remain useful as human/replay metadata but will be returned as `INVALID_REF` by the restricted executor. They should be upgraded to exact unittest witnesses when an executable regression is available.

## Resource telemetry migration

V4 extends observable resource vocabulary with CPU time, GPU time, energy, peak memory and network bytes. These are optional observed dimensions.

Do not migrate missing values to zero.

`UNKNOWN_COST != ZERO_COST`.

Historical worker/resource rows without a dimension simply remain unknown for that dimension.

## Learning migration

The V4 contextual bandit begins with no direct arm observations. When no local/global bandit evidence exists it can use the bounded V3 organization-policy score as a prior; that prior is not copied into the bandit observation table.

Cross-regime GLOBAL transfer is distinguishable from local regime evidence. Existing V3 policy observations are therefore not silently relabeled as V4 arm trials.

## Deployment check

After upgrade, verify:

1. package version and MCP `SERVER_INFO.version` both equal `2.3.0`;
2. `athena://collective/v4` appears in resources;
3. V4 tool names appear in `tools/list`;
4. `python -m unittest discover -s tests -v` passes;
5. `python smoke.py` passes;
6. existing `athena://transforms` resource still reads successfully;
7. canonical brain manifest points only to a CI-passing immutable runtime SHA.
