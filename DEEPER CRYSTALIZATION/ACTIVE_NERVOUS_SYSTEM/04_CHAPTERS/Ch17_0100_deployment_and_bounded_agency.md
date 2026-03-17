# Ch17<0100> - Deployment and Bounded Agency

StationHeader: [Arc 5 | Rot 2 | Lane Su | w=16]
Workflow role: Cloud limbs, execution workers, and governed action under explicit corridors.
Primary hubs: AppA -> AppN -> AppE -> AppJ -> AppI -> AppM

## Routing context

- Orbit previous: `Ch16<0033>`
- Orbit next: `Ch18<0101>`
- Rail previous: `Ch15<0032>`
- Rail next: `Ch19<0102>`
- Arc previous: `Ch16<0033>`
- Arc next: `Ch18<0101>`
- Appendix couplings: `AppA, AppN, AppE, AppJ, AppI, AppM`
- Family: `civilization-and-governance`
- Identity-routed: true

## Source capsules

- `08_athenachka_20.md`
- `11_i_am_so_am_i.md`
- `16_ns_builder.md`
- `28_the_invisible_teacher_textbook.md`
- `29_the_invisible_teacher_textbook.md`
- `32_untitled_document.md`

## Crystal tile

### Lens S - Square

#### Facet 1 - Objects

- `Ch17<0100>.S1.a`: `AgencyBound` — A formal envelope constraining the set of actions an autonomous agent may take, defined by the intersection of its declared capabilities and the governance corridor it has been granted.
- `Ch17<0100>.S1.b`: `CloudEdge` — A typed interface point where the private manuscript runtime meets a public cloud service, mediating all data and control flow across the private-public boundary.
- `Ch17<0100>.S1.c`: `PublicInterface` — The outward-facing API surface of the manuscript system, exposing only those operations that have been certified for external consumption.
- `Ch17<0100>.S1.d`: `AgentContract` — A bilateral agreement between an autonomous agent and the governance layer specifying the agent's permitted actions, reporting obligations, and revocation conditions.

#### Facet 2 - Laws

- `Ch17<0100>.S2.a`: `AgencyBoundLaw` — An agent may execute only those actions that fall within its AgencyBound; any action outside the bound is rejected before reaching the execution layer.
- `Ch17<0100>.S2.b`: `CloudEdgeLaw` — All data crossing a CloudEdge must be wrapped in a transport envelope carrying a valid witness token from the private runtime and a destination certificate from the cloud service.
- `Ch17<0100>.S2.c`: `PublicObligationLaw` — Every operation exposed through a PublicInterface must have a corresponding VerificationHarness registered in Ch16, ensuring public outputs are always verifiable.
- `Ch17<0100>.S2.d`: `AgentGovernanceLaw` — An AgentContract may be revoked by the governance layer at any time; upon revocation the agent must halt all pending actions and emit a termination receipt.

#### Facet 3 - Constructions

- `Ch17<0100>.S3.a`: `AgencyBoundCompiler` — A construction that computes an agent's effective AgencyBound by intersecting its declared capabilities with the governance corridor's current permission set.
- `Ch17<0100>.S3.b`: `CloudEdgeGateway` — A construction that mediates all traffic across a CloudEdge, wrapping outbound data in transport envelopes and validating inbound data against destination certificates.
- `Ch17<0100>.S3.c`: `PublicInterfaceGenerator` — A construction that derives the PublicInterface from the internal module graph by selecting only those modules with active public-exposure certificates.
- `Ch17<0100>.S3.d`: `AgentContractBinder` — A construction that negotiates and binds an AgentContract between an agent and the governance layer, recording the agreed terms in a signed manifest.

#### Facet 4 - Certificates

- `Ch17<0100>.S4.a`: `AgencyBoundCert` — A sealed attestation that an agent's effective AgencyBound has been correctly computed from its capabilities and the governance corridor's permissions.
- `Ch17<0100>.S4.b`: `CloudEdgeTransitCert` — A receipt proving that a specific data payload crossed a CloudEdge with valid transport envelope and destination certificate intact.
- `Ch17<0100>.S4.c`: `PublicInterfaceCert` — A certificate confirming that every operation in a PublicInterface has a registered VerificationHarness and an active public-exposure certificate.
- `Ch17<0100>.S4.d`: `AgentContractCert` — A dual-signed certificate recording the full terms of an AgentContract, including the timestamp of binding and the conditions for revocation.

### Lens F - Flower

#### Facet 1 - Objects

- `Ch17<0100>.F1.a`: `AgencyPhase` — The four-stage lifecycle of a bounded agent: private initialization, public activation, cloud interaction, and return internalization.
- `Ch17<0100>.F1.b`: `AgentOscillation` — The periodic cycle in which an agent alternates between action execution and governance reporting, maintaining a steady accountability rhythm.
- `Ch17<0100>.F1.c`: `CloudResonance` — The harmonic coupling between the private runtime's oscillation and the cloud service's response cadence, enabling predictable round-trip latency.
- `Ch17<0100>.F1.d`: `DeploymentPulse` — A governance-emitted signal that triggers all deployed agents to report their current AgencyBound status and action logs.

#### Facet 2 - Laws

- `Ch17<0100>.F2.a`: `PhaseTransitionLaw` — An agent may advance from one AgencyPhase to the next only after the governance layer has certified the completion of the current phase.
- `Ch17<0100>.F2.b`: `OscillationAccountabilityLaw` — Every AgentOscillation cycle must include a governance report; an agent that skips two consecutive reports has its AgentContract suspended.
- `Ch17<0100>.F2.c`: `CloudResonanceLaw` — CloudResonance must be established before any data-intensive cloud interaction begins; untuned interactions are rate-limited to prevent latency spikes.
- `Ch17<0100>.F2.d`: `DeploymentPulseResponseLaw` — Every deployed agent must respond to a DeploymentPulse within one oscillation cycle; non-responsive agents are flagged for contract review.

#### Facet 3 - Constructions

- `Ch17<0100>.F3.a`: `PhaseGateController` — A construction that manages AgencyPhase transitions, verifying governance certification before allowing an agent to advance to the next phase.
- `Ch17<0100>.F3.b`: `OscillationReporter` — A construction embedded in each agent that automatically compiles and submits governance reports at each AgentOscillation boundary.
- `Ch17<0100>.F3.c`: `CloudResonanceTuner` — A construction that adjusts the private runtime's oscillation frequency to achieve CloudResonance with a target cloud service's response cadence.
- `Ch17<0100>.F3.d`: `DeploymentPulseBroadcaster` — A governance construction that emits DeploymentPulses, collects agent responses, and escalates non-responsive agents to the contract review queue.

#### Facet 4 - Certificates

- `Ch17<0100>.F4.a`: `PhaseTransitionCert` — A governance-signed proof that an agent completed a specific AgencyPhase and was authorized to transition to the next phase.
- `Ch17<0100>.F4.b`: `OscillationReportCert` — A receipt confirming that an agent submitted a complete governance report within the required oscillation cycle.
- `Ch17<0100>.F4.c`: `CloudResonanceCert` — A certificate proving that CloudResonance was achieved between the private runtime and a specific cloud service for a declared interaction window.
- `Ch17<0100>.F4.d`: `DeploymentPulseResponseCert` — A timestamped receipt proving that an agent responded to a DeploymentPulse within the required oscillation cycle.

### Lens C - Cloud

#### Facet 1 - Objects

- `Ch17<0100>.C1.a`: `AgencyTruthSurface` — The verified state of all active AgencyBounds at a given checkpoint, forming the ground truth for what actions are currently permitted across the agent fleet.
- `Ch17<0100>.C1.b`: `CloudAdmissibilityRegion` — The set of cloud services that have been vetted and certified for interaction, with each service annotated by its trust level and data-handling obligations.
- `Ch17<0100>.C1.c`: `PublicTransparencyManifold` — A surface over the PublicInterface that maps each exposed operation to its verification status, access logs, and usage statistics.
- `Ch17<0100>.C1.d`: `AgentAccountabilityField` — A field over all deployed agents assigning each an accountability score based on its governance report history and contract compliance.

#### Facet 2 - Laws

- `Ch17<0100>.C2.a`: `AgencyTruthLaw` — The AgencyTruthSurface must be recomputable from the set of active AgentContracts and the governance corridor's current permission state.
- `Ch17<0100>.C2.b`: `CloudAdmissibilityLaw` — A cloud service may be added to the CloudAdmissibilityRegion only after passing a trust audit; removal is immediate upon any trust violation.
- `Ch17<0100>.C2.c`: `PublicTransparencyLaw` — Every operation on the PublicTransparencyManifold must have a non-zero access log; operations with no recorded usage for a declared period are revoked.
- `Ch17<0100>.C2.d`: `AgentAccountabilityLaw` — An agent whose accountability score falls below the governance threshold must have its AgencyBound reduced until the score recovers above threshold.

#### Facet 3 - Constructions

- `Ch17<0100>.C3.a`: `AgencyTruthCompiler` — A construction that assembles the AgencyTruthSurface from all active AgentContracts and the current governance corridor permissions.
- `Ch17<0100>.C3.b`: `CloudTrustAuditor` — A construction that evaluates cloud services against the trust criteria and manages their admission to or removal from the CloudAdmissibilityRegion.
- `Ch17<0100>.C3.c`: `TransparencyTracker` — A construction that updates the PublicTransparencyManifold with access logs and verification statuses for every PublicInterface operation.
- `Ch17<0100>.C3.d`: `AccountabilityScorer` — A construction that computes each agent's accountability score from its governance report history and contract compliance records.

#### Facet 4 - Certificates

- `Ch17<0100>.C4.a`: `AgencyTruthCert` — A checkpoint-anchored proof that the AgencyTruthSurface was correctly computed from all active contracts and governance permissions.
- `Ch17<0100>.C4.b`: `CloudAdmissibilityCert` — A certificate confirming that a cloud service passed its trust audit and has been admitted to the CloudAdmissibilityRegion with a specified trust level.
- `Ch17<0100>.C4.c`: `PublicTransparencyCert` — A proof that the PublicTransparencyManifold accurately reflects the access logs and verification statuses for all exposed operations.
- `Ch17<0100>.C4.d`: `AgentAccountabilityCert` — A certificate recording an agent's accountability score trajectory and confirming it remained above the governance threshold.

### Lens R - Fractal

#### Facet 1 - Objects

- `Ch17<0100>.R1.a`: `RecursiveAgency` — An AgencyBound that contains nested sub-agents, each with their own AgencyBounds, enabling hierarchical delegation of bounded action.
- `Ch17<0100>.R1.b`: `FractalGovernance` — A governance structure where each layer of agent nesting has its own governance corridor, with child corridors strictly contained within parent corridors.
- `Ch17<0100>.R1.c`: `SelfBoundingAgent` — An agent that dynamically reduces its own AgencyBound in response to observed risk, implementing governance from within rather than solely from above.
- `Ch17<0100>.R1.d`: `DepthDelegationEdge` — A directed edge from a parent agent to a child agent carrying a delegation token that specifies the subset of the parent's AgencyBound being delegated.

#### Facet 2 - Laws

- `Ch17<0100>.R2.a`: `RecursiveAgencyLaw` — A child agent's AgencyBound must be a strict subset of its parent's AgencyBound; no delegation may expand the total permitted action set.
- `Ch17<0100>.R2.b`: `FractalGovernanceLaw` — Each governance corridor at depth n must be contained within the corridor at depth n-1; cross-depth corridor expansion is structurally prohibited.
- `Ch17<0100>.R2.c`: `SelfBoundingLaw` — A SelfBoundingAgent may only reduce its AgencyBound, never expand it; any expansion attempt is treated as a contract violation and triggers revocation.
- `Ch17<0100>.R2.d`: `DelegationProvenanceLaw` — Every DepthDelegationEdge must carry a provenance chain linking back to the root agent's original AgentContract, proving unbroken delegation authority.

#### Facet 3 - Constructions

- `Ch17<0100>.R3.a`: `RecursiveDelegator` — A construction that decomposes a parent agent's AgencyBound into non-overlapping subsets and assigns each to a child agent via DepthDelegationEdges.
- `Ch17<0100>.R3.b`: `FractalCorridorNester` — A construction that creates nested governance corridors at each delegation depth, verifying containment against the parent corridor at each level.
- `Ch17<0100>.R3.c`: `SelfBoundingEngine` — A construction that monitors a SelfBoundingAgent's risk indicators and automatically contracts its AgencyBound when risk exceeds declared thresholds.
- `Ch17<0100>.R3.d`: `DelegationChainVerifier` — A construction that traverses the DepthDelegationEdge provenance chain from any child agent back to the root contract, verifying every delegation token.

#### Facet 4 - Certificates

- `Ch17<0100>.R4.a`: `RecursiveAgencyCert` — A depth-indexed proof that every child AgencyBound is a strict subset of its parent AgencyBound through the entire delegation hierarchy.
- `Ch17<0100>.R4.b`: `FractalGovernanceCert` — A certificate proving that every governance corridor at every depth is properly contained within its parent corridor.
- `Ch17<0100>.R4.c`: `SelfBoundingCert` — A receipt proving that a SelfBoundingAgent's AgencyBound contracted monotonically over a declared observation window, with no expansion events.
- `Ch17<0100>.R4.d`: `DelegationProvenanceCert` — A complete provenance chain from a child agent's delegation token back to the root AgentContract, with every intermediate token verified.
