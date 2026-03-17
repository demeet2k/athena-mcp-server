# Control Plane Grammar

## Purpose

This document aligns the five main nervous-system control surfaces:

1. queue
2. ledger or receipt
3. packet
4. adjudication
5. manifest

The goal is not to make them identical.
The goal is to make them interoperable so one front can move across them without losing:

- front identity
- truth state
- witness path
- writeback destination
- restart continuity

## Upstream Selection Note

`MotionConstitution_L1` sits upstream of queue pressure and upstream of adjudication.
It is the local-first selection membrane that decides which candidate motion should activate,
hold, request witnesses, request help, replay first, compress, escalate, quarantine, or refuse
before packet transport hardens into queue heat and before committee bundles enter the merge membrane.

## Canonical Shared Fields

Every serious control-plane surface should expose the same core grammar, even if the
headings differ slightly:

1. `SurfaceClass`
   queue, ledger, packet, adjudication, manifest, or receipt
2. `Front`
   the named front, quest, or bridge being worked
3. `State`
   `OPEN`, `ACTIVE`, `BLOCKED`, `COMPLETE`, `PROMOTED` for social fronts, or
   `OK`, `NEAR`, `AMBIG`, `FAIL` for corridor truth
4. `Objective`
   what the surface is trying to achieve
5. `Targets`
   the files, families, hubs, or bodies being changed
6. `Witness`
   the evidence, measurements, receipts, or source surfaces that justify the state
7. `Residual`
   what is still weak, missing, or blocked
8. `Writeback`
   where the next hardening step must land
9. `RestartSeed`
   the lawful next step if this surface cannot close fully

## Surface-Specific Minimums

### Queue

Queue surfaces must name:

- front
- why now
- next concrete action
- writeback destination

Queues are pressure surfaces, not proof surfaces.
They should point to proof rather than impersonate it.

### Ledger Or Receipt

Ledgers and receipts must name:

- front
- state transition
- witness basis
- residual drift
- next writeback

Ledgers are memory surfaces.
They preserve what changed and what still has to close.

### Packet

Packets must name:

- front
- packet class
- state or truth class
- active surfaces or targets
- witness
- expected outputs
- restart seed

Packets are transport surfaces.
They move meaning between bodies without losing execution intent.

### Adjudication

Adjudication surfaces must name:

- front
- merge state
- lawful destination or next admissible state
- witness and replay basis
- residual conflict or blocker
- writeback destination
- restart seed

Adjudication surfaces are decision membranes.
They turn packet transport into a lawful merge outcome without letting promotion bypass dissent,
verification, governance, or ledger memory.

### Manifest

Manifests must name:

- active front
- state
- primary targets
- priority order or stop condition
- witness basis
- writeback expectation
- restart seed

Manifests are control surfaces.
They keep a front alive across multiple passes.

## Minimal Translation Table

| Shared field | Queue phrasing | Ledger phrasing | Packet phrasing | Adjudication phrasing | Manifest phrasing |
| --- | --- | --- | --- | --- | --- |
| `Front` | immediate check | front | front | merge front | active front |
| `State` | priority or block | current state | truth class | merge state | state |
| `Objective` | next action | active rule | bridge purpose | lawful decision membrane | objective |
| `Targets` | target files | active surfaces | active surfaces | committee pack or decision target | primary targets |
| `Witness` | linked proof surface | witness | witness | witness and replay basis | witness |
| `Residual` | blocker or drift | current residual | missing outputs | unresolved dissent or blocker | stop condition |
| `Writeback` | queue destination | next writeback | expected outputs | lawful destination writeback | writeback |
| `RestartSeed` | next check | next action | restart seed | continuation seed | restart seed |

## Alignment Rule

When a quest moves from hall to runtime:

1. queue names the front
2. manifest keeps it alive
3. packet carries it across surfaces
4. adjudication decides whether it commits, defers, refuses, or quarantines
5. ledger or receipt proves what changed

If any one of those is missing, the front is only partially real.

## First Aligned Example Set

The first explicit aligned set under this grammar is:

- `06_active_queue.md`
- `ledgers/LEDGER_truth_promotion_control_plane.md`
- `packets/PKT_2026-03-09_root_runtime_governance_bridge.md`
- `manifests/DEEPER_ENHANCEMENT_ACTIVE_FRONT.md`
- `receipts/2026-03-09_control_plane_grammar_alignment.md`

## Zero Point

The control plane is coherent when queue pressure, packet transport, adjudication,
manifest continuity, and ledger memory all describe the same front in the same operational language.
