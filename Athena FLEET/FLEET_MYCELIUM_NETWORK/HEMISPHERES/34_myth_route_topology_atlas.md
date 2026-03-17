# MYTH Route Topology Atlas

Docs gate: `BLOCKED`

## Route Topology

```mermaid
flowchart LR
  HUB["HC-MYTH"]
  GC0["GC0-UNIFIED-CORPUS"]
  HUB --> GC0
  SYS-myth_grandcentral["GrandCentral (300)"]
  HUB --> SYS-myth_grandcentral
  SYS-myth_crosscorpusmycelial["CrossCorpusMycelial (46)"]
  HUB --> SYS-myth_crosscorpusmycelial
  SYS-myth_coremetro["CoreMetro (44)"]
  HUB --> SYS-myth_coremetro
  SYS-myth_deeprootmetrostack["DeepRootMetroStack (29)"]
  HUB --> SYS-myth_deeprootmetrostack
  SYS-myth_mycelial4d["Mycelial4D (28)"]
  HUB --> SYS-myth_mycelial4d
  SYS-myth_l2deepemergence["L2DeepEmergence (25)"]
  HUB --> SYS-myth_l2deepemergence
  SYS-myth_hdsctmetro["HDSCTMetro (21)"]
  HUB --> SYS-myth_hdsctmetro
  SYS-myth_emergentsupermap["EmergentSupermap (9)"]
  HUB --> SYS-myth_emergentsupermap
```

## Family Shards

| Family | Primary | Secondary | Shard |
| --- | --- | --- | --- |
| civilization-and-governance | 13 | 51 | [VA-FAMILY-civilization_and_governance](visual_atlas/family_civilization_and_governance.md) |
| general-corpus | 12 | 86 | [VA-FAMILY-general_corpus](visual_atlas/family_general_corpus.md) |
| helical-recursion-engine | 0 | 2 | [VA-FAMILY-helical_recursion_engine](visual_atlas/family_helical_recursion_engine.md) |
| higher-dimensional-geometry | 0 | 22 | [VA-FAMILY-higher_dimensional_geometry](visual_atlas/family_higher_dimensional_geometry.md) |
| identity-and-instruction | 12 | 8 | [VA-FAMILY-identity_and_instruction](visual_atlas/family_identity_and_instruction.md) |
| live-orchestration | 0 | 2 | [VA-FAMILY-live_orchestration](visual_atlas/family_live_orchestration.md) |
| manuscript-architecture | 4 | 67 | [VA-FAMILY-manuscript_architecture](visual_atlas/family_manuscript_architecture.md) |
| mythic-sign-systems | 28 | 8 | [VA-FAMILY-mythic_sign_systems](visual_atlas/family_mythic_sign_systems.md) |
| transport-and-runtime | 2 | 140 | [VA-FAMILY-transport_and_runtime](visual_atlas/family_transport_and_runtime.md) |
| void-and-collapse | 28 | 17 | [VA-FAMILY-void_and_collapse](visual_atlas/family_void_and_collapse.md) |

## Target-System Shards

| Target System | Route Refs | Shard |
| --- | --- | --- |
| GrandCentral | 300 | [VA-TARGET-grandcentral](visual_atlas/target_system_grandcentral.md) |
| CrossCorpusMycelial | 46 | [VA-TARGET-crosscorpusmycelial](visual_atlas/target_system_crosscorpusmycelial.md) |
| CoreMetro | 44 | [VA-TARGET-coremetro](visual_atlas/target_system_coremetro.md) |
| DeepRootMetroStack | 29 | [VA-TARGET-deeprootmetrostack](visual_atlas/target_system_deeprootmetrostack.md) |
| Mycelial4D | 28 | [VA-TARGET-mycelial4d](visual_atlas/target_system_mycelial4d.md) |
| L2DeepEmergence | 25 | [VA-TARGET-l2deepemergence](visual_atlas/target_system_l2deepemergence.md) |
| HDSCTMetro | 21 | [VA-TARGET-hdsctmetro](visual_atlas/target_system_hdsctmetro.md) |
| EmergentSupermap | 9 | [VA-TARGET-emergentsupermap](visual_atlas/target_system_emergentsupermap.md) |

## Commands

```powershell
python -m self_actualize.runtime.query_myth_math_hemisphere_brain record --record-id <record_id>
python -m self_actualize.runtime.compose_myth_math_hemisphere_routes record --record-id <record_id>
python -m self_actualize.runtime.synthesize_myth_math_hemisphere_routes record --record-id <record_id>
```
