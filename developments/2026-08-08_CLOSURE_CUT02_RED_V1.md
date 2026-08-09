# ATHENA ΩCLOSURE CUT-02 — PRE-TREATMENT RED WITNESS

Status: `RED_WITNESS_BRANCH`

Frozen source base at branch creation:

- runtime: `demeet2k/athena-mcp-server@82a519ffe25f9eacbbec0e119345ec395bf88c83`
- semantic brain: `demeet2k/Athena@40c3a2fa43f4cc971c0a7bfb8b22794710c62707`
- parent runtime work order: `#147 Cohesion Mesh V1`
- evaluation membrane: `demeet2k/Athena#192 GTC V1`

## Purpose

Record the exact pre-treatment CUT-02 defects before implementing any new runtime operator.

The cut contains six conceptual operators:

1. EvidenceCoverage — already canonical; regression substrate only.
2. Consume — absent from current Cohesion public surface.
3. DependencyCone — developed historically in draft PR #242 but absent from current master; replay/requalification target, not redesign target.
4. CohesionPulse — absent from current Cohesion public surface; distinct from private `QUEST::PULSE` execution multiplexing.
5. OutcomeCredit — absent as a generic Cohesion operator; Party Reward Provenance remains reusable lineage/anti-double-counting substrate only.
6. ContinuationBraid — private semantic composition problem across GTC/QPM/QUEST::PULSE/ΩOPERATE/QMR; not a new runtime authority.

## Existing substrate witness

Current Cohesion already carries:

- `athena_cohesion_request_offer`
- `athena_cohesion_matchmake`
- `athena_cohesion_coalition`
- `athena_cohesion_solo_party_compare`
- `athena_cohesion_duplicate_guard`
- `COHESION.EVIDENCE.GUARD.1`

EvidenceCoverage must remain fail-closed:

```text
UNMATCHED_MISSION_KEYS -> UNKNOWN_INSUFFICIENT_EVIDENCE
DUPLICATE_EVIDENCE_REF -> UNKNOWN_INSUFFICIENT_EVIDENCE
causal_effect = UNKNOWN
promotion_authority = false
```

## RED contract

The exact RED contract is machine-readable at:

`spec/CLOSURE_CUT02_RED_V1.json`

The intentionally failing surface tests are isolated from ordinary repository discovery at:

`tests/red/test_closure_cut02_red.py`

The self-witnessing exact-runtime probe is:

`scripts/closure_cut02_red_witness.py`

and writes:

`closure-cut02-red-witness.json`

The dedicated workflow runs both the passing surface-gap witness and the intentionally failing RED unittest cartridge:

`.github/workflows/closure-cut02-red.yml`

## Firewalls

```text
RED_WITNESS != TREATMENT
MISSING_SURFACE != PROOF_OF_BENEFIT
ROUTED != CONSUMED != COMPLIED != TRUE
PARTY_MEMBERSHIP != UNIVERSAL_DEPENDENCY
EXECUTION != OBSERVED_OUTCOME
COHESION_PULSE != QUEST_PULSE
UNKNOWN != ZERO
MECHANISM_PASS != BEHAVIORAL_GAIN
```

## Treatment prohibition

This branch contains no CUT-02 treatment implementation. It must remain a frozen pre-treatment witness. Green implementation should be performed on a separate current-master descendant after this RED state is observed.

## Successor

`CUT02.RED -> observe exact workflow receipt -> fresh-current treatment branch -> replay DependencyCone -> implement Consume -> implement OutcomeCredit -> implement CohesionPulse -> integration/behavioral evaluation`.
