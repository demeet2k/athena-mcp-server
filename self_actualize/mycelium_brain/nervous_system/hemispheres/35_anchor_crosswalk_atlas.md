# Anchor Crosswalk Atlas

Docs gate: `BLOCKED`

## Crosswalk Graph

```mermaid
flowchart LR
  HM["HC-MATH"]
  HY["HC-MYTH"]
  A-dn01["DN01 (251)"]
  HM --> A-dn01
  HY --> A-dn01
  A-dn02["DN02 (35)"]
  HM --> A-dn02
  HY --> A-dn02
  A-dn03["DN03 (175)"]
  HM --> A-dn03
  HY --> A-dn03
  A-dn04["DN04 (114)"]
  HM --> A-dn04
  HY --> A-dn04
  A-dn05["DN05 (331)"]
  HM --> A-dn05
  HY --> A-dn05
  A-dn06["DN06 (24)"]
  HM --> A-dn06
  HY --> A-dn06
  A-dn07["DN07 (31)"]
  HM --> A-dn07
  HY --> A-dn07
  A-dn08["DN08 (27)"]
  HM --> A-dn08
  HY --> A-dn08
  A-dn09["DN09 (29)"]
  HM --> A-dn09
  HY --> A-dn09
  A-dn10["DN10 (13)"]
  HM --> A-dn10
  HY --> A-dn10
  A-dn11["DN11 (10)"]
  HM --> A-dn11
  HY --> A-dn11
  A-dn12["DN12 (1)"]
  HM --> A-dn12
  A-dn13["DN13 (5)"]
  HM --> A-dn13
  HY --> A-dn13
  A-dn14["DN14 (220)"]
  HM --> A-dn14
  HY --> A-dn14
  A-dn15["DN15 (138)"]
  HM --> A-dn15
  HY --> A-dn15
  A-dn16["DN16 (102)"]
  HM --> A-dn16
  HY --> A-dn16
```

## Anchor Shards

| Anchor | Primary MATH | Primary MYTH | Shard |
| --- | --- | --- | --- |
| DN01 | 199 | 52 | [VA-ANCHOR-DN01](visual_atlas/anchor_dn01.md) |
| DN02 | 27 | 8 | [VA-ANCHOR-DN02](visual_atlas/anchor_dn02.md) |
| DN03 | 141 | 34 | [VA-ANCHOR-DN03](visual_atlas/anchor_dn03.md) |
| DN04 | 91 | 23 | [VA-ANCHOR-DN04](visual_atlas/anchor_dn04.md) |
| DN05 | 267 | 64 | [VA-ANCHOR-DN05](visual_atlas/anchor_dn05.md) |
| DN06 | 19 | 5 | [VA-ANCHOR-DN06](visual_atlas/anchor_dn06.md) |
| DN07 | 30 | 1 | [VA-ANCHOR-DN07](visual_atlas/anchor_dn07.md) |
| DN08 | 26 | 1 | [VA-ANCHOR-DN08](visual_atlas/anchor_dn08.md) |
| DN09 | 18 | 11 | [VA-ANCHOR-DN09](visual_atlas/anchor_dn09.md) |
| DN10 | 9 | 4 | [VA-ANCHOR-DN10](visual_atlas/anchor_dn10.md) |
| DN11 | 7 | 3 | [VA-ANCHOR-DN11](visual_atlas/anchor_dn11.md) |
| DN12 | 1 | 0 | [VA-ANCHOR-DN12](visual_atlas/anchor_dn12.md) |
| DN13 | 3 | 2 | [VA-ANCHOR-DN13](visual_atlas/anchor_dn13.md) |
| DN14 | 171 | 49 | [VA-ANCHOR-DN14](visual_atlas/anchor_dn14.md) |
| DN15 | 117 | 21 | [VA-ANCHOR-DN15](visual_atlas/anchor_dn15.md) |
| DN16 | 83 | 19 | [VA-ANCHOR-DN16](visual_atlas/anchor_dn16.md) |

## Commands

```powershell
python -m self_actualize.runtime.query_myth_math_hemisphere_brain record --record-id <record_id>
python -m self_actualize.runtime.compose_myth_math_hemisphere_routes record --record-id <record_id>
python -m self_actualize.runtime.synthesize_myth_math_hemisphere_routes record --record-id <record_id>
```
