# Athena FLEET Tesseract Metro Map

- Active basis documents: `F01-F10`
- Active element or symmetry: `Origin x Crystal x Transit x Governance`
- Metro resolution used: `local 4D organism`
- Docs gate: `BLOCKED`
- Result source: `generated from exhaustive local matrix`

## Major Lines

- `Origin`: `F01 -> F04 -> F02 -> F10`
- `Crystal`: `F04 -> F03 -> F07 -> F02`
- `Transit`: `F05 -> F06 -> F07 -> F08 -> F09`
- `Governance`: `F09 -> F08 -> F10 -> F07 -> F02 -> F01`

## Promoted Hubs

- `F02` manifestation hub
- `F03` extraction hub
- `F08` repair hub
- `F10` carrier hub

## Transfer Hubs

- `F02` crosses `Origin`, `Crystal`, and `Governance`
- `F07` crosses `Crystal`, `Transit`, and `Governance`

```mermaid
flowchart LR
  F01["F01 SelfWeAm"] -->|"seed"| F02["F02 Athenachka"]
  F04["F04 LiftB"] -->|"lift"| F03["F03 Crystal256"]
  F03 -->|"publish"| F02
  F05["F05 Transit"] -.->|"mirror"| F06["F06 TransitMirror"]
  F05 -->|"route"| F07["F07 MetroC"]
  F07 -->|"repair"| F08["F08 RepairA"]
  F09["F09 GitBrain"] -->|"govern"| F08
  F08 -->|"compress"| F10["F10 StdRecord"]
  F10 -->|"publish"| F02
  F07 -->|"transfer"| F02
```
