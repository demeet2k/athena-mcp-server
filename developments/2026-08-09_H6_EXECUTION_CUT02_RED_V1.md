# H6 EXECUTION CUT-02 — executable RED boundary

## Frozen coordinates

- runtime parent: `429a480a80eeefb9e2bff1ea3015adf571d76b0e`
- semantic brain: `demeet2k/Athena@f32eb817d48de73a0c591b0f7fb3561e4f08e7da`
- constitutional seats: H01–H06 / GID001–006
- treatment code: **none**

## Purpose

Convert the six source-audited H6 contract gaps into executable, parent-bound RED witnesses before any GREEN H6 facade is implemented.

Each RED first demonstrates a real current-parent capability and then asks for the missing constitutional decision:

1. `H6G01_IDENTITY_DECISION` — exact IDs/navigation exist, but no semantic IdentityDecision ABI.
2. `H6G02_PROJECTION_AUTHORITY` — KC144 projection resolves, but hash/index projection is not classified against frozen constitutional seating authority.
3. `H6G04_BRIDGE_ADMISSION` — transforms/programs/executions exist, but transform registration is not H04 bridge admission.
4. `H6G05_EVIDENCE_GRAPH` — raw evidence payload/provenance mechanisms exist, but no unified read-only H05 evidence-decision projection.
5. `H6G03_ROUTE_NAVRUN_ABI` — graph/frontier routes exist, but no shared constitutional RouteProposal/NAVRUN ABI.
6. `H6G06_QUERYBUNDLE_ROOT_FACADE` — hydration/reconstruction/rehydration/successor machinery exists, but no one H6 QueryBundle/root compile receipt.

## Witness semantics

`tests/red/test_h6_cut02_executable_red.py` is intentionally outside ordinary test discovery.  `scripts/h6_cut02_red_witness.py` executes each case independently and succeeds only when exactly one failure/error is observed for each case **and** that failure contains the expected gap ID.  Therefore a random crash or unrelated failing test is not accepted as the RED witness.

The workflow `.github/workflows/h6-cut02-red.yml` produces the provider-side RED receipt artifact.

## Firewalls

```text
RED_WITNESS != TREATMENT
PARENT_BEHAVIOR_FIRST
PARTIAL != MISSING
COORDINATE != IDENTITY
HASH_PROJECTION != CONSTITUTIONAL_SEATING
GRAPH_PATH != ROUTE_PROPOSAL
TRANSFORM_REGISTRATION != BRIDGE_ADMISSION
RAW_EVIDENCE_PAYLOAD != H05_EVIDENCE_DECISION
HYDRATE_SNAPSHOT != QUERYBUNDLE
OBSERVED_RED != FUTURE_TREATMENT_BENEFIT
NO_GREEN_UNTIL_ALL_SIX_INTENDED_REDS_OBSERVED
```

## Successor

After exact provider RED confirmation and a final freshness check, CUT-03 may start from the then-current `master` and implement the smallest `H6RootRuntime` facade plus thin projections required to make these same six tests GREEN.  This RED branch must not be merged as treatment code.
