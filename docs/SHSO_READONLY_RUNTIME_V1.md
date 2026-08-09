# SHSO READ-ONLY RUNTIME V1

Issue: `athena-mcp-server#346`

Public runtime base:

`d8bb4cc6e2e6861eeb7141dc52a2efcea252ff36`

Private semantic contract:

`ATHENA.SHSO.READONLY.BRIDGE.V1`

Private V2d semantic head observed for this port:

`0aa81433ee35ef27a819023594f621ab1dfe909c`

Private reconciliation commit:

`98bda154c3c99de82d047b13b1aaaf4944772102`

Runtime artifact:

`ATHENA.SHSO.READONLY.RUNTIME.V1`

Standing:

`READ_ONLY_RUNTIME_EXTENSION_CANDIDATE / BEHAVIORAL EFFECT UNKNOWN / SHSO TREATMENT DEPLOYMENT HOLD / RELEASE PROMOTION HOLD`

## Purpose

Private SHSO V2d reconciled the swarm/hive coordination lineage against the current Brain V3.7 semantic frontier and defined a read-only SHSO→mass-agency pressure seam. This public runtime lane exposes only that narrow seam.

It does **not** port the full private V2a/V2b/V2c reducer family, create a public SHSO state store, change scheduling authority, or deploy an SHSO treatment.

The runtime surface is intentionally:

```text
caller-supplied HEALTH_ADVISORY
    +
caller-supplied ECOLOGY_ADVISORY
    +
bounded work-state facts
    ->
SHSO_ORGANISM_PRESSURE_ADVISORY
```

`CALLER_SUPPLIED_ADVISORY != WORLD_TRUTH`.

## MCP tool

`athena_shso_project_organism_pressure`

Inputs:

- `health_advisory`;
- `ecology_advisory`;
- `ready_build_exists`;
- `previous_transition_classes`;
- `verification_barrier_due`;
- `verification_barrier_mandatory`.

The bridge validates the semantic standing of the health/ecology packets before projection. Health must remain a heuristic diagnostic (`criticality_proven=false`, `phase_is_heuristic=true`, `behavioral_gain_proven=false`). Ecology must remain advisory (`world_truth_proven=false`). Authority-bearing assertions and private-reasoning fields fail closed.

## Pressure ordering

```text
HARD_GATE_COMPROMISED
  > mandatory verification
  > builder-starvation build pivot
  > coherent batch verification
  > organism maintenance
  > ready build continuation
  > no organism action
```

This ordering intentionally composes two independently developed ideas:

- SHSO contributes organism health, ecology uncertainty, neutral reserve and hard-gate precedence;
- the newer mass-agency/work-first candidate contributes the builder-starvation observation that repeated verification/control/meta transitions should not consume a ready lawful build frontier forever.

The public runtime does not activate that private prompt candidate. It only exposes a compatible advisory pressure vocabulary.

## Pressure vocabulary

```text
HOLD_HARD_GATE
VERIFY_MANDATORY_BARRIER_ADVISORY
BUILD_PIVOT_ADVISORY
VERIFY_BATCH_ADVISORY
PRESERVE_NEUTRAL_SCOUT
PRESERVE_RESERVE_ADVISORY
BRIDGE_LOCAL_GUILDS_ADVISORY
REDUCE_COORDINATION_ADVISORY
RECOVERY_RESERVE_ADVISORY
BUILD_CONTINUE_ADVISORY
NO_ORGANISM_ACTION
```

Health-maintenance projections:

```text
HERDED      -> PRESERVE_NEUTRAL_SCOUT
BRITTLE     -> PRESERVE_RESERVE_ADVISORY
FRAGMENTED  -> BRIDGE_LOCAL_GUILDS_ADVISORY
SATURATED   -> REDUCE_COORDINATION_ADVISORY
RECOVERING  -> RECOVERY_RESERVE_ADVISORY
```

These are pressure labels, not scheduler commands.

## Ecology gate

The bridge reports:

```text
morphology_action_allowed =
  ecology.status == CLASSIFIED
  AND health.phase != HARD_GATE_COMPROMISED
```

For `AMBIGUOUS` or `UNKNOWN_*` ecology states, morphology action remains false. The bridge may still expose a health-maintenance pressure such as preserving neutral scouts, but it does not infer a morphology transition.

`UNKNOWN_ECOLOGY -> NO_MORPHOLOGY_ACTION`.

## Authority firewall

Every tool result and manifest preserves:

```text
external_side_effects_performed=false
git_mutation_performed=false
scheduler_mutation_performed=false
claim_authority_granted=false
dispatch_authority_granted=false
execution_authority_granted=false
merge_authority_granted=false
morphology_mutation_performed=false
prompt_promotion_authority_granted=false
world_truth_proven=false
authority_truth_proven=false
behavioral_gain_proven=false
```

The runtime can project pressure. It cannot enact the pressure.

`SHSO_PRESSURE != DISPATCH`.

`READY_BUILD_SIGNAL != EXECUTION_PERMISSION`.

## Runtime integration

The extension follows the existing additive extension pattern:

1. register the tool with `PROMPT_RUNTIME_TOOLS` and `protocol.TOOLS` without duplication;
2. register `athena://shso/readonly` with the AOR development resources;
3. wrap `PromptRuntime.call_tool` for the SHSO tool only;
4. wrap `AorDevelopmentSurface.read_resource` for the SHSO resource only;
5. add deterministic contract checks to the development benchmark;
6. append `shso_readonly` metadata and `SHSO_READONLY_RUNTIME_V1` to `athena://manifest` without changing the manifest/release identity;
7. install before Collective V15 so V15 remains the final current release identity.

## Behavioral boundary

Private V2e separately defines an A0–A5 matched behavioral assay. At the time of this runtime port, that campaign has not produced a qualified causal result.

Therefore:

`behavioral_treatment_effect = UNKNOWN`.

Publishing a read-only bridge is engineering evidence only. It is not evidence that adaptive SHSO improves ATHENA mission outcomes.

`READ_ONLY_RUNTIME_EXTENSION != TREATMENT_DEPLOYMENT`.

`PRIVATE_SEMANTIC_CONTRACT != PUBLIC_RUNTIME_RELEASE_QUALIFICATION`.

## Successor

The next runtime step, if the exact branch passes its relevant tests/CI, is a review of whether this read-only surface should be merged as an additive extension. Expanding the public SHSO API to include private reducers or stateful morphology control requires a separate current-head work claim and evidence gate.
