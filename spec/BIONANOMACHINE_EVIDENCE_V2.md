# BIONANOMACHINE EVIDENCE ADAPTER V2

Stable MCP ABI: `BNMK.V1`

Evidence layer: `BNMK.ADAPTER20.V2`

Resource remains: `athena://bio/nanomachines/v1`

## Purpose

V2 upgrades the BNMK mechanism library from a user-seeded/generic model to a primary-source-conditioned adapter layer without changing the six-tool namespace or granting any new execution authority.

```text
STABLE_API != FROZEN_KNOWLEDGE
PRIMARY_SOURCE_SUPPORT != UNIVERSAL_CONSTANT
PRIMARY_SOURCE_SUPPORT != EXECUTION_AUTHORITY
BIOLOGICAL_MECHANISM != COMPUTATIONAL_EQUIVALENCE
```

## Population

```text
14 original seed machine identities
+ 6 bounded evidence-backed expansions
= 20 source-backed adapters

20 primary research witnesses
15 conditioned quantitative claims
12 mechanism rows x 12 facets = 144 populated evidence cells
```

Expansions:

```text
RNA_POLYMERASE
SPLICEOSOME
ABC_TRANSPORTER
FTSK_TRANSLOCASE
PHI29_DNA_PACKAGING_MOTOR
CONDENSIN
```

They do not renumber the 12 stable archetype rows. A machine may project into multiple rows while retaining one semantic identity.

```text
MULTI_ROW_ASSOCIATION != DUPLICATED_OBJECT
```

## Quantitative membrane

Every promoted numeric record has:

```text
property
value
unit
qualifier
conditions[]
source_id
standing=PRIMARY_CONDITIONED
universal_constant=false
```

The original user-seed claims `9000 RPM`, `100000 RPM`, and `1000 bases/s` remain explicit `UNVERIFIED_USER_SEED` records rather than being silently upgraded.

## Runtime composition

`EvidenceBionanomachineRuntime` subclasses the original V1 runtime. This preserves `interface_match` and `convergence_gate` behavior and adds evidence-aware catalog, compile, transfer, assembly and benchmark behavior.

### catalog

Backward-compatible call:

```text
athena_bionano_catalog({include_atlas:false})
```

still returns the stable V1 shape including the 14 `seed_machines` entries. V2 additive fields report source-backed counts, expansions, operator phylogeny and evidence version.

Optional:

```text
include_evidence=true
```

adds the 20 source-backed machine/source/claim packets and the explicit unpromoted user numeric claims.

`include_atlas=true` returns 144 populated cells with non-empty `value`, `adapter_ids`, and `source_ids`.

### compile

Known machine compile returns:

```text
COMPILED_SOURCE_BACKED_MODEL
primary_source
quantitative_claims[]
row_associations[]
4D lift
12D primary-row kernel
all associated KC144 row projections
state cycle
portable operators
```

Authority remains:

```text
PRIMARY_SOURCE_CONDITIONED_MECHANISM_MODEL_NOT_CANONICAL_BIOLOGICAL_TRUTH
```

### transfer

Always:

```text
authority=COMPUTATIONAL_ANALOGY_ONLY
```

Source support does not leak into software execution authorization.

### assembly

T4 returns a dual-provenance packet:

```text
USER_VISUAL 15-part BOM
+
PRIMARY_RESEARCH conditioned infection transition sequence
```

Those sources remain distinct.

All other machines expose generic functional modules plus source-conditioned functional sequence. The runtime does not fabricate a native molecular subunit inventory.

## Operator phylogeny

The evidence layer exposes six overlapping mechanism clades:

```text
ENERGY_TRANSDUCERS
TRACK_AND_POLYMER_MOTORS
TEMPLATE_INFORMATION_MACHINES
TOPOLOGY_MACHINES
PROTEOSTASIS
BOUNDARY_DELIVERY
```

and twelve second-order candidate operators:

```text
ATTACH_GATE_COMMIT
PROCESSIVE_CARGO_WALK
REVERSIBLE_ASSEMBLY_WITH_RISING_COMMITMENT
ALTERNATING_ACCESS_TRANSPORT
RING_MOTOR_WITH_BACKPRESSURE
LOOP_EXTRUSION_TOPOLOGY_CONTROL
UNFOLD_TRANSLOCATE_DEGRADE
CAPTURE_ISOLATE_REFOLD_RELEASE
CUT_PASS_RESEAL
TEMPLATE_READ_ASSEMBLE_ADVANCE
SEQUENCE_DIRECTED_ROUTE_REVERSAL
COLLISION_TRAVERSE_INSTEAD_OF_DEADLOCK
```

Names are reusable mechanism abstractions, not learned behavioral policy and not proof of biological homology.

## Tests

`tests/test_bionanomachine_evidence_v2.py` proves:

- 14 original + 6 expansion = 20 source-backed adapters;
- all 20 compile with primary-source DOI and row identity;
- all 15 numerical records are conditioned and non-universal;
- three seed speed/rate claims stay unpromoted;
- exactly 144 unique, non-empty evidence cells;
- multi-row projection preserves one semantic identity;
- primary source support never changes transfer authority;
- visual T4 BOM remains distinct from source-supported transition sequence;
- original and expansion assembly remain non-native-BOM abstractions;
- catalog evidence is opt-in while stable V1 fields remain present;
- interface/convergence V1 semantics remain unchanged.

## Promotion boundary

```text
DATA_CREATED != VALIDATED
TEST_PASS != WORLD_TRUTH
BRANCH_PASS != MERGED_CURRENT
MERGED_CURRENT != CANONICAL_MANIFEST_PIN
```
