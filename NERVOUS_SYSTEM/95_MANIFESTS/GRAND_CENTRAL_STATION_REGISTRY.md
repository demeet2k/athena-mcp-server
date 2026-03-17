# Grand Central Station Registry

Date: `2026-03-12`
Generated: `2026-03-12T19:09:36.577589+00:00`
Docs gate: `BLOCKED`
Verdict: `OK`

This manifest is the canonical root registry for Grand Central Station.
It is keyed by station address, root ID, hemisphere, tract, bundle, fiber, synapse,
status, and authority level.

## Station Law

`GC0` is the common hall.
Every major root now receives one lawful docking coordinate inside that hall.

## Registry

| Root | Name | Station Address | Hemisphere | Tract | Bundle | Fiber | Synapse | Status | Authority |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A01 | `NERVOUS_SYSTEM` | GC0::GCL::A01::address::B64-A01-ADDR::integrate::bind | left | address | B64-A01-ADDR | integrate | bind | live | canonical |
| A02 | `self_actualize` | GC0::GCL+GCR::A02::replay::B64-A02-REPLAY::return::reseed | bilateral | replay | B64-A02-REPLAY | return | reseed | live | runtime |
| A03 | `ECOSYSTEM` | GC0::GCL::A03::relation::B64-A03-RELATE::transmit::gate | left | relation | B64-A03-RELATE | transmit | gate | live | governance |
| A04 | `DEEPER CRYSTALIZATION` | GC0::GCL+GCR::A04::chamber::B64-A04-QUAR::integrate::gate | bilateral | chamber | B64-A04-QUAR | integrate | gate | live | historical-absorbed |
| A05 | `MATH` | GC0::GCL::A05::chamber::B64-A05-PROOF::integrate::bind | left | chamber | B64-A05-PROOF | integrate | bind | live | canonical-domain |
| A06 | `Voynich` | GC0::GCR::A06::relation::B64-A06-MEAN::sense::bind | right | relation | B64-A06-MEAN | sense | bind | live | canonical-domain |
| A07 | `Trading Bot` | GC0::GCL+GCR::A07::replay::B64-A07-GATE::transmit::gate | bilateral | replay | B64-A07-GATE | transmit | gate | live | external-bridge |
| A08 | `Quadrant Binary` | GC0::GCL::A08::address::B64-A08-BIT4::sense::prime | left | address | B64-A08-BIT4 | sense | prime | live | ancestor-kernel |
| A09 | `QSHRINK - ATHENA (internal use)` | GC0::GCL::A09::chamber::B64-A09-COMP::integrate::gate | left | chamber | B64-A09-COMP | integrate | gate | live | compression-shell |
| A10 | `NERUAL NETWORK` | GC0::GCL+GCR::A10::relation::B64-A10-ADAPT::transmit::bind | bilateral | relation | B64-A10-ADAPT | transmit | bind | live | runtime-lab |
| A11 | `FRESH` | GC0::GCR::A11::address::B64-A11-INTAKE::sense::prime | right | address | B64-A11-INTAKE | sense | prime | live | intake-fringe |
| A12 | `Athenachka Collective Books` | GC0::GCR::A12::replay::B64-A12-PUBLISH::return::bind | right | replay | B64-A12-PUBLISH | return | bind | live | publication-halo |
| A13 | `I AM ATHENA` | GC0::GCR::A13::chamber::B64-A13-IDENT::integrate::bind | right | chamber | B64-A13-IDENT | integrate | bind | live | identity-shell |
| A14 | `GAMES` | GC0::GCR::A14::relation::B64-A14-SIM::transmit::gate | right | relation | B64-A14-SIM | transmit | gate | live | simulation-lab |
| A15 | `ORGIN` | GC0::GCR::A15::chamber::B64-A15-SEED::sense::reseed | right | chamber | B64-A15-SEED | sense | reseed | live | seed-reservoir |
| A16 | `Athena FLEET` | GC0::GCL+GCR::A16::relation::B64-A16-FLEET::transmit::bind | bilateral | relation | B64-A16-FLEET | transmit | bind | live | pilot-cluster |
| A17 | `Stoicheia (Element Sudoku)` | GC0::GCL::A17::relation::B64-A17-PLAY::sense::prime | left | relation | B64-A17-PLAY | sense | prime | reserve | reserve-visual |
| A18 | `CLEAN` | GC0::GCL::A18::chamber::B64-A18-STAGE::integrate::prime | left | chamber | B64-A18-STAGE | integrate | prime | reserve | reserve-staging |
| A19 | `mycelial_unified_nervous_system_bundle` | GC0::GCL+GCR::A19::replay::B64-A19-BUNDLE::return::gate | bilateral | replay | B64-A19-BUNDLE | return | gate | dormant | dormant-bundle |

## Summary

- root count: `19`
- hemisphere totals:
  `left 7`, `right 6`, `bilateral 6`
- tract totals:
  `address 3`, `relation 6`, `chamber 6`, `replay 4`
- branch states:
  `live 16`, `reserve 2`, `dormant 1`

## Derivation

- command:
  `python -m self_actualize.runtime.derive_grand_central_station`
- sources:
  `ROOT_BASIS_MAP`, `body_tensor.json`, `semantic_mass_ledger.json`, and `live_docs_gate_status.md`

## Interpretation

- `hemisphere` records the primary exchange side, not an absolute exclusion of cross-traffic
- `tract` records the main station duty through Address, Relation, Chamber, or Replay
- `status` uses the normalized branch taxonomy: `live`, `reserve`, or `dormant`
- `authority_level` records how strongly the root may speak inside the station
