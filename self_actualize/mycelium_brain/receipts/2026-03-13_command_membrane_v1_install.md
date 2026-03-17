# COMMAND Membrane v1 Install Receipt

- Date: `2026-03-13`
- Canonical authority: `NEXT57`
- Command surface: `GLOBAL COMMAND`
- Docs gate: `BLOCKED`
- Active loop: `L02`
- Active family: `A02 self_actualize`
- Restart seed: `L03 Survey A03 ECOSYSTEM`

## Implemented

- Rewired `self_actualize.runtime.command_membrane` to remain canonical without depending on the corrupted `command_spine.py`.
- Aligned the backend runtime with the published protocol:
  - settle window `1500 ms`
  - routing policy `goal+file_family+coord12_proximity+queue_pressure+capillary_strength+role_compatibility`
  - capillary law `C_next = clamp01(0.82*C + 0.30*U + 0.18*F - 0.16*D - 0.14*N)`
  - coord12 labels `utc_atomic, earth_rotation_phase, earth_orbital_phase, node_anchor, solar_phase, lunar_phase, shared12_phase, planetary_slot, runtime_region, queue_pressure, goal_salience, novelty_concentration`
- Added backward-compatible coord12 decoding so older packets and new packets can coexist during transition.
- Fixed stale-route behavior so expired routed packets can be rerouted lawfully instead of remaining stuck.
- Replaced the broken derivation helper with a wrapper-based implementation rooted in the live package.
- Reconciled the visible Hall, queue, active-run, and next-prompt surfaces to `NEXT57` instead of the old `master_loop_state_57` story.

## Verified

- Protocol verification: `python -m self_actualize.runtime.verify_command_membrane_protocol`
- Runtime verification: `python -m self_actualize.runtime.verify_command_membrane`
- Derivation helper: `python -m self_actualize.runtime.derive_command_membrane_protocol`
- End-to-end probe: `EVT-20260313-0007`
  - route: `SCOUT-01>ROUTER-01>WORKER-02>ARCHIVIST-01`
  - result: `success`
  - capillary class: `vein`

## Current State

- Queue depth: `0`
- Active leases: `0`
- Last committed event: `EVT-20260313-0007`
- Replay ptr: `self_actualize/mycelium_brain/nervous_system/packets/command_membrane/EVT-20260313-0007.json`
- Feeder truth preserved: `Q42 / Q46 / TQ04 / TQ06 / Q02(blocked)`
