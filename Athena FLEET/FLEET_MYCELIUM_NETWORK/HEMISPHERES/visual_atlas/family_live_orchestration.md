# Family Atlas: live-orchestration

Docs gate: `BLOCKED`

## Topology

```mermaid
flowchart LR
  FAM["live-orchestration (2)"]
  HM["HC-MATH"]
  HY["HC-MYTH"]
  FAM --> HM
  FAM --> HY
  TSF-grandcentral["GrandCentral"]
  FAM --> TSF-grandcentral
  TSF-l3neural["L3Neural"]
  FAM --> TSF-l3neural
```

## Stats

- label: `Live orchestration and prompt control`
- records: `2`
- primary MATH: `2`
- primary MYTH: `0`
- bridge records: `0`
- composer starter groups present: `0`
- synthesis starter groups present: `0`

## Top Records

| Record | Title | Primary | MATH Route | MYTH Route |
| --- | --- | --- | --- | --- |
| 2a6d682e0889b1ecc5b60011 | Always On: HPC tasks typically run 24/7 (... | MATH | RTE-2a6d682e0889b1ecc5b60011-MATH | RTE-2a6d682e0889b1ecc5b60011-MYTH |
| a43c1d991769591908a4ae82 | Meltdown means a task or service that dem... | MATH | RTE-a43c1d991769591908a4ae82-MATH | RTE-a43c1d991769591908a4ae82-MYTH |

## Commands

```powershell
python -m self_actualize.runtime.query_myth_math_hemisphere_brain facet --family live-orchestration
python -m self_actualize.runtime.compose_myth_math_hemisphere_routes facet --family live-orchestration
python -m self_actualize.runtime.synthesize_myth_math_hemisphere_routes facet --family live-orchestration
```
