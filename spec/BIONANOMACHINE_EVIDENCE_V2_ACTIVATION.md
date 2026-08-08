# BNMK V2 PUBLIC ACTIVATION

Stable API: `BNMK.V1`
Evidence layer: `BNMK.ADAPTER20.V2`
Base master: `18773939da9949d84e44db6e4818d225ab8facab`

## Activation delta

The six existing BNMK RPC names remain unchanged. `BionanomachineSurface` switches from `BionanomachineRuntime` to the already-tested `EvidenceBionanomachineRuntime`.

`athena_bionano_catalog` gains one optional additive argument:

```text
include_evidence: boolean
```

Omitted/false preserves the stable 14-seed catalog surface while additive V2 summary fields report the evidence-layer counts. True returns primary-source/claim packets for all 20 adapters.

## Required invariants

```text
SIX_TOOL_NAMESPACE_STABLE
MCK_TOOL_AND_RESOURCE_UNION_PRESERVED
14_ORIGINAL_SEEDS_PRESERVED
20_SOURCE_BACKED_ADAPTERS
20_PRIMARY_SOURCES
15_PRIMARY_CONDITIONED_NUMERIC_CLAIMS
3_UNPROMOTED_USER_SEED_SPEED_RATE_CLAIMS
144_NONEMPTY_UNIQUE_KC144_CELLS
PRIMARY_SOURCE_SUPPORT != EXECUTION_AUTHORITY
COMPUTATIONAL_TRANSFER_AUTHORITY = ANALOGY_ONLY
INTERFACE_MATCH_V1_SEMANTICS_UNCHANGED
CONVERGENCE_GATE_V1_SEMANTICS_UNCHANGED
USER_VISUAL_T4_BOM != PRIMARY_VERIFIED_NATIVE_SUBUNIT_INVENTORY
ASSEMBLY_GRAPH != FUNCTION_GRAPH
```

## MCK seam

The current runtime uses `bionanomachine_surface.py` as a compatibility union for the independently implemented Mythic Computation Kernel. Activation changes only the BNMK runtime instance and BNMK resource metadata. It preserves:

```text
MythicComputationSurface
MYTHIC_COMPUTATION_TOOLS
MYTHIC_COMPUTATION_RESOURCES
MYTHIC_COMPUTATION_TOOL_NAMES
MYTHIC_COMPUTATION_RESOURCE_URIS
```

This is a regression test because the predecessor stale-branch attempt copied the seam without the sibling `mythic_computation_*` lineage and failed host qualification with `ModuleNotFoundError`.

## Promotion law

```text
EVIDENCE_RUNTIME_TESTED != PUBLICLY_ACTIVE
ACTIVATION_BRANCH_PASS != MERGED_CURRENT
MERGED_CURRENT != MERGED_HEAD_CI_PASS
MERGED_HEAD_CI_PASS != CANONICAL_ATHENA_RUNTIME_PIN
```

The canonical Athena runtime pin remains a separate mutation and is not implied by this activation.
