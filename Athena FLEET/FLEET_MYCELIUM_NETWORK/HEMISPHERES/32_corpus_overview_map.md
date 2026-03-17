# Corpus Overview Map

Docs gate: `BLOCKED`

## Hub Spine

```mermaid
flowchart LR
  HM["HC-MATH"]
  GC0["GC0-UNIFIED-CORPUS"]
  HY["HC-MYTH"]
  HM --> GC0
  GC0 --> HY
  HY --> GC0
  GC0 --> HM
```

## Family Lines

```mermaid
flowchart LR
  GC0["GC0-UNIFIED-CORPUS"]
  HM["HC-MATH (403 primary)"]
  HY["HC-MYTH (99 primary)"]
  HM --> GC0
  GC0 --> HY
  FAM-civilization_and_governance["civilization-and-governance (64)"]
  HM --> FAM-civilization_and_governance
  FAM-general_corpus["general-corpus (98)"]
  HM --> FAM-general_corpus
  FAM-helical_recursion_engine["helical-recursion-engine (2)"]
  HM --> FAM-helical_recursion_engine
  FAM-higher_dimensional_geometry["higher-dimensional-geometry (22)"]
  HM --> FAM-higher_dimensional_geometry
  FAM-identity_and_instruction["identity-and-instruction (20)"]
  HY --> FAM-identity_and_instruction
  FAM-live_orchestration["live-orchestration (2)"]
  HM --> FAM-live_orchestration
  FAM-manuscript_architecture["manuscript-architecture (71)"]
  HM --> FAM-manuscript_architecture
  FAM-mythic_sign_systems["mythic-sign-systems (36)"]
  HY --> FAM-mythic_sign_systems
  FAM-transport_and_runtime["transport-and-runtime (142)"]
  HM --> FAM-transport_and_runtime
  FAM-void_and_collapse["void-and-collapse (45)"]
  HY --> FAM-void_and_collapse
```

## Target Systems

```mermaid
flowchart LR
  HM["HC-MATH"]
  GC0["GC0-UNIFIED-CORPUS"]
  HY["HC-MYTH"]
  HM --> GC0
  GC0 --> HY
  SYS-brainstem64["BrainStem64 (64)"]
  HM --> SYS-brainstem64
  SYS-coremetro["CoreMetro (64)"]
  HM --> SYS-coremetro
  HY --> SYS-coremetro
  SYS-crosscorpusmycelial["CrossCorpusMycelial (50)"]
  HM --> SYS-crosscorpusmycelial
  HY --> SYS-crosscorpusmycelial
  SYS-deeprootmetrostack["DeepRootMetroStack (47)"]
  HM --> SYS-deeprootmetrostack
  HY --> SYS-deeprootmetrostack
  SYS-emergentsupermap["EmergentSupermap (9)"]
  HY --> SYS-emergentsupermap
  SYS-grandcentral["GrandCentral (411)"]
  HM --> SYS-grandcentral
  HY --> SYS-grandcentral
  SYS-hdsctmetro["HDSCTMetro (22)"]
  HM --> SYS-hdsctmetro
  HY --> SYS-hdsctmetro
  SYS-l2deepemergence["L2DeepEmergence (34)"]
  HM --> SYS-l2deepemergence
  HY --> SYS-l2deepemergence
  SYS-l3neural["L3Neural (2)"]
  HM --> SYS-l3neural
  SYS-mycelial4d["Mycelial4D (36)"]
  HM --> SYS-mycelial4d
  HY --> SYS-mycelial4d
  SYS-plexus256["Plexus256 (62)"]
  HM --> SYS-plexus256
```

## Anchor Lattice

```mermaid
flowchart LR
  GC0["GC0-UNIFIED-CORPUS"]
  ANC-dn01["DN01 (251)"]
  GC0 --> ANC-dn01
  ANC-dn02["DN02 (35)"]
  GC0 --> ANC-dn02
  ANC-dn03["DN03 (175)"]
  GC0 --> ANC-dn03
  ANC-dn04["DN04 (114)"]
  GC0 --> ANC-dn04
  ANC-dn05["DN05 (331)"]
  GC0 --> ANC-dn05
  ANC-dn06["DN06 (24)"]
  GC0 --> ANC-dn06
  ANC-dn07["DN07 (31)"]
  GC0 --> ANC-dn07
  ANC-dn08["DN08 (27)"]
  GC0 --> ANC-dn08
  ANC-dn09["DN09 (29)"]
  GC0 --> ANC-dn09
  ANC-dn10["DN10 (13)"]
  GC0 --> ANC-dn10
  ANC-dn11["DN11 (10)"]
  GC0 --> ANC-dn11
  ANC-dn12["DN12 (1)"]
  GC0 --> ANC-dn12
  ANC-dn13["DN13 (5)"]
  GC0 --> ANC-dn13
  ANC-dn14["DN14 (220)"]
  GC0 --> ANC-dn14
  ANC-dn15["DN15 (138)"]
  GC0 --> ANC-dn15
  ANC-dn16["DN16 (102)"]
  GC0 --> ANC-dn16
```

## Jump Points

- [MATH Route Topology Atlas](33_math_route_topology_atlas.md)
- [MYTH Route Topology Atlas](34_myth_route_topology_atlas.md)
- [Anchor Crosswalk Atlas](35_anchor_crosswalk_atlas.md)
- [Target-System Atlas](36_target_system_atlas.md)
- [Record Locator Index](37_record_locator_index.md)

## Commands

```powershell
python -m self_actualize.runtime.query_myth_math_hemisphere_brain record --record-id <record_id>
python -m self_actualize.runtime.compose_myth_math_hemisphere_routes record --record-id <record_id>
python -m self_actualize.runtime.synthesize_myth_math_hemisphere_routes record --record-id <record_id>
```
