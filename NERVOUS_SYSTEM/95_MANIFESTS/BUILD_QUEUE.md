# BUILD QUEUE

- Current state: `L04 complete / L05 ready`
- Restart seed: `L05 -> Canonical 16-Basis Ownership`

## Hall
- `Q57-L04-H01` Seal active membrane `Q41 / TQ06`
- `Q57-L04-H02` Carry live Hall feeder `Q42`
- `Q57-L04-H03` Confirm landed Temple receiver `TQ04`
- `Q57-L04-H04` Preserve reserve feeder `Q46`

## Temple
- `TQ57-L04-T01` Ratify active membrane `Q41 / TQ06`
- `TQ57-L04-T02` Ratify Hall carrier `Q42`
- `TQ57-L04-T03` Ratify landed receiver `TQ04`
- `TQ57-L04-T04` Ratify reserve-only feeder `Q46`

## Control Tuple
- membrane: `Q41 / TQ06`
- carrier: `Q42`
- landed receiver: `TQ04`
- reserve feeder: `Q46`
- blocker: `Q02`

<!-- COMMAND_MEMBRANE_BUILD_QUEUE:START -->
## Command Membrane Queue

- Watch scope: `first-wave local swarm mesh`
- Routing policy: `goal+salience+pheromone+coord+capability+load`
- Claim mode: `first-lease`
- Lease ms: `1200`
<!-- COMMAND_MEMBRANE_BUILD_QUEUE:END -->
