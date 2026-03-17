# Athena FLEET Local 4D Organism Map

## Coordinate Body

`Theta_fleet = (Origin, Crystal, Transit, Governance)`

## Tissue Map

- `chamber`: `F01`, `F02`
- `skeleton`: `F03`, `F04`
- `nerves`: `F05`, `F06`, `F07`
- `immune_fascia`: `F08`, `F09`
- `carrier_shell`: `F10`

## Relay Paths

- `seed -> lift -> formalize`: `F01 -> F04 -> F03`
- `formalize -> transit -> emergence`: `F03 -> F05/F06 -> F07`
- `emergence -> repair -> governance`: `F07 -> F08 -> F09`
- `repair -> carrier -> manifestation`: `F08 -> F10 -> F02`

## Replay Return Paths

- `F02 -> F03 -> F10 -> F02`
- `F05 <-> F06 -> F07 -> F08 -> F10`
- `F09 -> F08 -> F10 -> F02 -> F01`

## Growth Law

No new file may join the mesh before it receives a node ID, mirror, coordinate, and corridor set.

## Retirement Law

No file disappears; it only changes to `archive_witness`, `dormant_node`, or `mirror_twin`.
