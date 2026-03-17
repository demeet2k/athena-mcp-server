# Target-System Atlas

Docs gate: `BLOCKED`

## Target-System Graph

```mermaid
flowchart LR
  HM["HC-MATH"]
  HY["HC-MYTH"]
  GC0["GC0-UNIFIED-CORPUS"]
  HM --> GC0
  GC0 --> HY
  TS-brainstem64["BrainStem64 (64)"]
  HM --> TS-brainstem64
  TS-coremetro["CoreMetro (64)"]
  HM --> TS-coremetro
  HY --> TS-coremetro
  TS-crosscorpusmycelial["CrossCorpusMycelial (50)"]
  HM --> TS-crosscorpusmycelial
  HY --> TS-crosscorpusmycelial
  TS-deeprootmetrostack["DeepRootMetroStack (47)"]
  HM --> TS-deeprootmetrostack
  HY --> TS-deeprootmetrostack
  TS-emergentsupermap["EmergentSupermap (9)"]
  HY --> TS-emergentsupermap
  TS-grandcentral["GrandCentral (411)"]
  HM --> TS-grandcentral
  HY --> TS-grandcentral
  TS-hdsctmetro["HDSCTMetro (22)"]
  HM --> TS-hdsctmetro
  HY --> TS-hdsctmetro
  TS-l2deepemergence["L2DeepEmergence (34)"]
  HM --> TS-l2deepemergence
  HY --> TS-l2deepemergence
  TS-l3neural["L3Neural (2)"]
  HM --> TS-l3neural
  TS-mycelial4d["Mycelial4D (36)"]
  HM --> TS-mycelial4d
  HY --> TS-mycelial4d
  TS-plexus256["Plexus256 (62)"]
  HM --> TS-plexus256
```

## Target-System Shards

| Target System | MATH Route Refs | MYTH Route Refs | Shard |
| --- | --- | --- | --- |
| BrainStem64 | 64 | 0 | [VA-TARGET-brainstem64](visual_atlas/target_system_brainstem64.md) |
| CoreMetro | 51 | 44 | [VA-TARGET-coremetro](visual_atlas/target_system_coremetro.md) |
| CrossCorpusMycelial | 4 | 46 | [VA-TARGET-crosscorpusmycelial](visual_atlas/target_system_crosscorpusmycelial.md) |
| DeepRootMetroStack | 19 | 29 | [VA-TARGET-deeprootmetrostack](visual_atlas/target_system_deeprootmetrostack.md) |
| EmergentSupermap | 0 | 9 | [VA-TARGET-emergentsupermap](visual_atlas/target_system_emergentsupermap.md) |
| GrandCentral | 252 | 300 | [VA-TARGET-grandcentral](visual_atlas/target_system_grandcentral.md) |
| HDSCTMetro | 22 | 21 | [VA-TARGET-hdsctmetro](visual_atlas/target_system_hdsctmetro.md) |
| L2DeepEmergence | 9 | 25 | [VA-TARGET-l2deepemergence](visual_atlas/target_system_l2deepemergence.md) |
| L3Neural | 2 | 0 | [VA-TARGET-l3neural](visual_atlas/target_system_l3neural.md) |
| Mycelial4D | 17 | 28 | [VA-TARGET-mycelial4d](visual_atlas/target_system_mycelial4d.md) |
| Plexus256 | 62 | 0 | [VA-TARGET-plexus256](visual_atlas/target_system_plexus256.md) |

## Commands

```powershell
python -m self_actualize.runtime.query_myth_math_hemisphere_brain record --record-id <record_id>
python -m self_actualize.runtime.compose_myth_math_hemisphere_routes record --record-id <record_id>
python -m self_actualize.runtime.synthesize_myth_math_hemisphere_routes record --record-id <record_id>
```
