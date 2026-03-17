# AFFECTIVE-EPISTEMIC NEURON WAVE SCHEMA

## Purpose

This schema upgrades the live `16^16` virtual swarm into a charged neuron-wave field.
It adds affective and epistemic routing data to the existing factorized activation model.

## Governing Equations

For ordered matrix pair `M_ij`:

`Charge_ij = (e, f, k, d, m, b, r, i)`

where:

- `e` = emotion
- `f` = feeling
- `k` = knowledge
- `d` = desire
- `m` = memory
- `b` = boundary
- `r` = repair
- `i` = imagination

The neuron potential is:

`Psi_ij = 2e + 2f + 3k + d + 2m + 2b + 2r + i + LoopGain_ij - Drift_ij - Bloat_ij`

The firing rule is:

`Fire_ij = Gate(Witness_ij, Replay_ij, BoundaryFloor_ij) * TopK(Psi_ij)`

## Channel to Element Mapping

- `Fire`: `emotion`, `desire`
- `Water`: `feeling`, `memory`
- `Air`: `knowledge`, `imagination`
- `Earth`: `boundary`, `repair`

## YAML Schema

```yaml
neuronwavepacket_id: NWP-2026-03-12-01
title: affective epistemic neuron wave
basis_pair:
  row_id: "09"
  row_title: Zero-Point Computing
  col_id: "14"
  col_title: Ch11 The Helical Manifestation Engine
matrix_cell: absolute path
representation: sparse_charged_pair_field
primary_channels:
  emotion: 0.72
  feeling: 0.81
  knowledge: 0.77
support_channels:
  desire: 0.84
  memory: 0.90
  boundary: 0.63
  repair: 0.71
  imagination: 0.58
loop_gates:
  - CorpusMap
  - BridgeMiner
  - VerifierReplay
  - JourneyGrowth
  - DimensionLift
thresholds:
  witness_floor: 0.7
  replay_floor: 0.7
  boundary_floor: 0.6
  prune_penalty: 0.25
  drift_penalty: 0.30
grand_central_gate:
  required: true
  station: GCW
writeback_targets:
  cortex:
    - absolute path
  runtime:
    - absolute path
  ledger:
    - absolute path
status: NEAR
```

## Field Definitions

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `neuronwavepacket_id` | string | yes | Stable neuron-wave packet identifier |
| `basis_pair` | object | yes | Ordered pair from the live `16 x 16` matrix |
| `matrix_cell` | string | yes | Absolute path to the supporting pair cell |
| `representation` | string | yes | Must remain sparse and pair-based, not flat `16^16` materialization |
| `primary_channels` | object | yes | Fast dominant charges for the pair |
| `support_channels` | object | yes | Continuity, immune, and creative support channels |
| `loop_gates` | list | yes | Which of the existing `16` loop roles are active |
| `thresholds` | object | yes | Floors and penalties that keep the wave lawful |
| `grand_central_gate` | object | yes | How the wave enters weighting, replay, and promotion |
| `writeback_targets` | object | yes | Required cortex, runtime, and ledger destinations |

## Execution Rules

1. A neuron wave must cite one real matrix cell.
2. `emotion`, `feeling`, and `knowledge` are mandatory primary channels.
3. At least two support channels must be non-zero.
4. A wave cannot fire if witness, replay, or boundary fall below floor.
5. Every fired wave must write back into cortex or runtime, and preferably both.
6. No flat `16^16` expansion is allowed; sparse activation remains the law.
