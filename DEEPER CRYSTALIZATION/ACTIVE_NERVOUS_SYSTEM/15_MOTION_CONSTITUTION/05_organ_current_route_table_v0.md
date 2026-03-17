# OrganCurrentRouteTable.v0

Truth state: `NEAR-derived`

## Admissible Routes

| Route | Current | Packet family | Law |
| --- | --- | --- | --- |
| QuestBoard -> BrainstemChamber | governance | quest_packet | all candidate motion enters the brainstem through typed queues |
| AgentRegistry -> BrainstemChamber | governance | help_request | role mismatch may be converted into lawful help requests |
| ImmuneScheduler -> BrainstemChamber | immune | quarantine_packet | immune pressure may veto activation before execution |
| BrainstemChamber -> ReplayKernel | replay | replay_job | replay-first obligations leave the brainstem through ReplayKernel |
| BrainstemChamber -> CommitteeChamber | governance | committee_escalation | branch-limit and stewardship violations require committee routing |
| BrainstemChamber -> QuarantineManifold | immune | quarantine_packet | forbidden contradiction classes are routed to containment instead of activation |
| BrainstemChamber -> ContinuationSeedVault | continuation | continuation_seed | blocked motion with preserved continuation value emits a successor seed |
| BrainstemChamber -> PublicCommitSurface | transport | action_receipt | public-grade closure is lawful only when replay obligations are already satisfied |
| ReplayKernel -> ContinuationSeedVault | continuation | continuation_seed | verified replay may crystallize into a successor seed for the next lawful pass |

## Forbidden Routes

| Route | Law |
| --- | --- |
| QuarantineManifold -> PublicCommitSurface | quarantined contradiction cannot be promoted as public closure |
| BrainstemChamber -> PublicCommitSurface | forbidden when replay readiness is below threshold or Omega denies |
| QuestBoard -> PublicCommitSurface | no direct public promotion without brainstem scoring and replay |
| QuarantineManifold -> BrainstemChamber | recent quarantine may not reactivate until trust or replay improves |
| BrainstemChamber -> parallel_conflicting_commit | committee-pending items suppress parallel conflicting commits |

## Committee-Required Routes

| Route | Trigger |
| --- | --- |
| BrainstemChamber -> CommitteeChamber | branch burden exceeds stewardship limit |
| BrainstemChamber -> CommitteeChamber | multi-agent merge or governance membrane required |
| BrainstemChamber -> CommitteeChamber | carrier envelope exceeded for current truth burden |

## Seed Fallback Routes

| Route | Trigger |
| --- | --- |
| BrainstemChamber -> ContinuationSeedVault | continuation value remains but lawful forward motion does not |
| ReplayKernel -> ContinuationSeedVault | replay clarifies the next lawful seed even if activation stays blocked |
