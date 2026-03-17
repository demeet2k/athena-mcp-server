# MATH Route Topology Atlas

Docs gate: `BLOCKED`

## Route Topology

```mermaid
flowchart LR
  HUB["HC-MATH"]
  GC0["GC0-UNIFIED-CORPUS"]
  HUB --> GC0
  SYS-math_grandcentral["GrandCentral (252)"]
  HUB --> SYS-math_grandcentral
  SYS-math_brainstem64["BrainStem64 (64)"]
  HUB --> SYS-math_brainstem64
  SYS-math_plexus256["Plexus256 (62)"]
  HUB --> SYS-math_plexus256
  SYS-math_coremetro["CoreMetro (51)"]
  HUB --> SYS-math_coremetro
  SYS-math_hdsctmetro["HDSCTMetro (22)"]
  HUB --> SYS-math_hdsctmetro
  SYS-math_deeprootmetrostack["DeepRootMetroStack (19)"]
  HUB --> SYS-math_deeprootmetrostack
  SYS-math_mycelial4d["Mycelial4D (17)"]
  HUB --> SYS-math_mycelial4d
  SYS-math_l2deepemergence["L2DeepEmergence (9)"]
  HUB --> SYS-math_l2deepemergence
  SYS-math_crosscorpusmycelial["CrossCorpusMycelial (4)"]
  HUB --> SYS-math_crosscorpusmycelial
  SYS-math_l3neural["L3Neural (2)"]
  HUB --> SYS-math_l3neural
```

## Family Shards

| Family | Primary | Secondary | Shard |
| --- | --- | --- | --- |
| civilization-and-governance | 51 | 13 | [VA-FAMILY-civilization_and_governance](visual_atlas/family_civilization_and_governance.md) |
| general-corpus | 86 | 12 | [VA-FAMILY-general_corpus](visual_atlas/family_general_corpus.md) |
| helical-recursion-engine | 2 | 0 | [VA-FAMILY-helical_recursion_engine](visual_atlas/family_helical_recursion_engine.md) |
| higher-dimensional-geometry | 22 | 0 | [VA-FAMILY-higher_dimensional_geometry](visual_atlas/family_higher_dimensional_geometry.md) |
| identity-and-instruction | 8 | 12 | [VA-FAMILY-identity_and_instruction](visual_atlas/family_identity_and_instruction.md) |
| live-orchestration | 2 | 0 | [VA-FAMILY-live_orchestration](visual_atlas/family_live_orchestration.md) |
| manuscript-architecture | 67 | 4 | [VA-FAMILY-manuscript_architecture](visual_atlas/family_manuscript_architecture.md) |
| mythic-sign-systems | 8 | 28 | [VA-FAMILY-mythic_sign_systems](visual_atlas/family_mythic_sign_systems.md) |
| transport-and-runtime | 140 | 2 | [VA-FAMILY-transport_and_runtime](visual_atlas/family_transport_and_runtime.md) |
| void-and-collapse | 17 | 28 | [VA-FAMILY-void_and_collapse](visual_atlas/family_void_and_collapse.md) |

## Target-System Shards

| Target System | Route Refs | Shard |
| --- | --- | --- |
| GrandCentral | 252 | [VA-TARGET-grandcentral](visual_atlas/target_system_grandcentral.md) |
| BrainStem64 | 64 | [VA-TARGET-brainstem64](visual_atlas/target_system_brainstem64.md) |
| Plexus256 | 62 | [VA-TARGET-plexus256](visual_atlas/target_system_plexus256.md) |
| CoreMetro | 51 | [VA-TARGET-coremetro](visual_atlas/target_system_coremetro.md) |
| HDSCTMetro | 22 | [VA-TARGET-hdsctmetro](visual_atlas/target_system_hdsctmetro.md) |
| DeepRootMetroStack | 19 | [VA-TARGET-deeprootmetrostack](visual_atlas/target_system_deeprootmetrostack.md) |
| Mycelial4D | 17 | [VA-TARGET-mycelial4d](visual_atlas/target_system_mycelial4d.md) |
| L2DeepEmergence | 9 | [VA-TARGET-l2deepemergence](visual_atlas/target_system_l2deepemergence.md) |
| CrossCorpusMycelial | 4 | [VA-TARGET-crosscorpusmycelial](visual_atlas/target_system_crosscorpusmycelial.md) |
| L3Neural | 2 | [VA-TARGET-l3neural](visual_atlas/target_system_l3neural.md) |

## Commands

```powershell
python -m self_actualize.runtime.query_myth_math_hemisphere_brain record --record-id <record_id>
python -m self_actualize.runtime.compose_myth_math_hemisphere_routes record --record-id <record_id>
python -m self_actualize.runtime.synthesize_myth_math_hemisphere_routes record --record-id <record_id>
```
