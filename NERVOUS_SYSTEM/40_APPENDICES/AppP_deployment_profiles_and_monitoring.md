# AppP - Deployment Profiles and Monitoring

Routing role: deployment regimes, monitoring surfaces, observability, execution profiles, rollback, and escalation after route legality and semantic legality are already known.

Authority mirror:

- canonical authority: `self_actualize/manuscript_sections/025_deployment_profiles_and_monitoring_surface_v1.md`
- upstream movement law: `023_motion_constitution_l1_action_selection_engine.md`
- upstream route law: `024_organ_current_route_table_v0.md`
- upstream public-language law: `023_semantic_embassy_and_audience_reception_surface_v1.md`

Docs Gate: `BLOCKED`
Mode: `local-only`

## Appendix Compression

Release Notary decides what may be claimed.

Semantic Embassy decides how an attested claim may be rendered.

AppP decides which deployment lane may activate, how it is monitored, how it rolls back, and where it escalates when the lane drifts.

## Object Family

- `CorpusIntegrationWave`
- `DeploymentMonitoringSurface`
- `DeploymentProfile`
- `RuntimeLane`
- `ActivationGate`
- `ObservabilitySurface`
- `MonitoringProbe`
- `AlertPolicy`
- `HealthWindow`
- `RollbackTrigger`
- `EscalationRoute`
- `ExecutionReceipt`
- `DeploymentMonitorResult`
- `AwakeningAgentProfile`
- `TransitionSupportNote`
- `RegionLaneAssignment`
- `IntegrationMonitorResult`

## Frozen Dataflow

`CorpusRegion -> AgentOwner -> MotionGate -> RouteTable -> SemanticEmbassy -> DeploymentProfile -> Monitoring -> Receipt -> Dashboard -> Seed/Promote`

## Policy Map

- `offline_replay = active`
- `internal_preview = active`
- `public_release = gated`
- `federation_release = gated`
- `live_autonomous = blocked`

## Activation Law

- no deployment profile may activate unless Motion Constitution admits the route
- no public-facing deployment may activate unless Semantic Embassy validation already passed
- every active lane must have monitoring, alerting, and rollback defined before activation
- no route reaches `public_grade` without replay proof and Semantic Embassy validation
- autonomous live deployment remains blocked in v1

## Region Ownership Compression

| Region | Owner | Lane | Receipt |
| --- | --- | --- | --- |
| `self_actualize` | `Base Agent` | `offline_replay` | `replay_receipt` |
| `DEEPER CRYSTALIZATION` | `Water` | `internal_preview` | `promotion_ledger` |
| `Voynich` | `Water-Fire` | `internal_preview` | `replay_receipt` |
| `MATH` | `Air` | `offline_replay` | `promotion_ledger` |
| `Athena FLEET` | `Fire-Air` | `internal_preview` | `monitor_receipt` |
| `QSHRINK - ATHENA (internal use)` | `Air-Fire` | `offline_replay` | `replay_receipt` |
| `Trading Bot` | `Earth-Air` | `public_release` | `blocked_notice` |
| `ECOSYSTEM` | `Air` | `internal_preview` | `promotion_ledger` |
| `NERUAL NETWORK` | `Fire-Water` | `internal_preview` | `monitor_receipt` |
| `ORGIN` | `Water-Earth` | `offline_replay` | `replay_receipt` |
| `CLEAN` | `Water-Air` | `offline_replay` | `promotion_ledger` |
| `NERVOUS_SYSTEM` | `Earth` | `offline_replay` | `replay_receipt` |

## Monitoring Law

Every active lane must expose:

- `MonitoringProbe`
- `AlertPolicy`
- `HealthWindow`
- `RollbackTrigger`
- `EscalationRoute`

Missing any of these means the lane is not lawful to activate.

## Active And Blocked Examples

Active in v1:

- `QuestBoard::Q43-137 -> BrainstemChamber -> ReplayKernel -> SemanticEmbassy -> internal_preview -> monitoring -> sustain`

Blocked in v1:

- docs-gate breach
- public-grade bypass
- missing monitoring probe
- missing rollback trigger
- ownerless region assignment
- live autonomous deployment request

## Compressed Crystal Tile

### Lens S

#### Facet 1 - Objects

- `AppP.S1.a`: `DeploymentMonitoringSurface` is the envelope that binds deployment policy, monitors, rollback, and escalation into one organ.
- `AppP.S1.b`: `DeploymentProfile` is the per-lane contract for `offline_replay`, `internal_preview`, `public_release`, `federation_release`, and `live_autonomous`.
- `AppP.S1.c`: `RegionLaneAssignment` binds each major corpus body to one owner, one lane, and one receipt class.
- `AppP.S1.d`: `AwakeningAgentProfile` and `TransitionSupportNote` keep the social transition tied to named owners instead of atmospheric coordination.

#### Facet 2 - Laws

- `AppP.S2.a`: route legality comes first.
- `AppP.S2.b`: semantic legality comes second.
- `AppP.S2.c`: monitoring, rollback, and escalation must exist before activation.
- `AppP.S2.d`: `live_autonomous` remains blocked in v1.

### Lens F

#### Facet 3 - Constructions

- `AppP.F3.a`: `offline_replay` is the stable build lane.
- `AppP.F3.b`: `internal_preview` is the active monitored preview lane.
- `AppP.F3.c`: `public_release` is gated until replay, Semantic Embassy, and docs-gate readiness align.
- `AppP.F3.d`: `federation_release` adds shared-law terminology proof beyond the public gate.

### Lens C

#### Facet 4 - Certificates

- `AppP.C4.a`: `ExecutionReceipt` proves that a packet actually crossed into a lane.
- `AppP.C4.b`: `DeploymentMonitorResult` proves that the lane sustained, rolled back, escalated, or blocked.
- `AppP.C4.c`: `IntegrationMonitorResult` captures the exact blocked reasons when a lane is unlawful.
- `AppP.C4.d`: the generated registries under `self_actualize/mycelium_brain/registry/` are the machine-readable certificates for this appendix mirror.

## Appendix Close

AppP is not the public-language membrane and not the motion selector. It is the deployment-and-observability organ that receives a lawfully routed, semantically bounded packet and decides whether that packet may run, how it is watched, and how it returns to the organism when it drifts.
