# Target-System Atlas: L3Neural

Docs gate: `BLOCKED`

## Topology

```mermaid
flowchart LR
  SYS["L3Neural (2)"]
  HM["HC-MATH"]
  HY["HC-MYTH"]
  HM --> SYS
  HY --> SYS
```

## Family Mix

| Family | Records |
| --- | --- |
| live-orchestration | 2 |

## Top Records

| Record | Title | MATH Target | MYTH Target |
| --- | --- | --- | --- |
| 2a6d682e0889b1ecc5b60011 | Always On: HPC tasks typically run 24/7 (... | L3Neural | GrandCentral |
| a43c1d991769591908a4ae82 | Meltdown means a task or service that dem... | L3Neural | GrandCentral |

## Commands

```powershell
python -m self_actualize.runtime.query_myth_math_hemisphere_brain record --record-id <record_id>
python -m self_actualize.runtime.compose_myth_math_hemisphere_routes record --record-id <record_id>
python -m self_actualize.runtime.synthesize_myth_math_hemisphere_routes record --record-id <record_id>
```
