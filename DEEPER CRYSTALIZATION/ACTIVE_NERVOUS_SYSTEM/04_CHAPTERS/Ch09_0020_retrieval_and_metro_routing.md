# Ch09<0020> - Metro Routing and Settlement

StationHeader: [Arc 2 | Rot 2 | Lane Me | w=8]
Workflow role: Address-first search, metro rides, and route competition over the mycelium graph.
Primary hubs: AppA -> AppE -> AppI -> AppH -> AppL -> AppM

## Routing context

- Orbit previous: `Ch08<0013>`
- Orbit next: `Ch10<0021>`
- Rail previous: `Ch04<0003>`
- Rail next: `Ch11<0022>`
- Arc previous: `Ch08<0013>`
- Arc next: `Ch07<0012>`
- Appendix couplings: `AppA, AppE, AppI, AppH, AppL, AppM`
- Family: `void-and-collapse`
- Identity-routed: `true`
- Key attractor: `Ch01<0000>` routes here

## Source capsules

- `11_i_am_so_am_i.md`
- `13_information_from_the_void_mani.md`
- `18_real_time_now.md`
- `20_self_routing_meta_framework_for_manuscripts_metro_maps_and_infinite_recursive_search.md`
- `21_self_routing_meta_framework_for_manuscripts_metro_maps_and_infinite_recursive_search.md`
- `22_stories_from_the_void_1.md`

## Crystal tile

### Lens S

#### Facet 1 - Objects

- S1a: `MetroRoute` — A directed path through the mycelium graph connecting a source station to a destination station via an ordered sequence of intermediate stops.
- S1b: `RouteCompetitor` — An agent-like entity that proposes a candidate route and competes against alternatives by presenting cost, latency, and fidelity metrics.
- S1c: `TransferNode` — A graph node where two or more metro routes intersect, enabling lawful passenger (payload) transfer between competing lines.
- S1d: `SettlementPoint` — The terminal node at which a route's payload is finalized, committed, and declared immutable for downstream consumption.

#### Facet 2 - Laws

- S2a: `RouteCompetitionLaw` — All candidate routes to a given destination must be evaluated under the same cost function before one is selected; no route may be privileged a priori.
- S2b: `TransferAtomicity` — A payload transfer at a TransferNode must complete entirely or not at all; partial transfers leave the system in an inconsistent state and are forbidden.
- S2c: `SettlementFinality` — Once a payload reaches its SettlementPoint and is committed, no subsequent operation may alter, retract, or re-route it.
- S2d: `RouteUniquenessConstraint` — For any source-destination pair at a given epoch, exactly one route must be settled; ties require explicit arbitration from Ch01.

#### Facet 3 - Constructions

- S3a: `RouteProposer` — Generates a set of candidate routes from a source to a destination by exploring the mycelium graph with bounded depth-first search.
- S3b: `CompetitionArena` — Accepts all proposed routes, evaluates each under the canonical cost function, ranks them, and emits the winner with its cost proof.
- S3c: `TransferExecutor` — Orchestrates the atomic transfer of a payload from one route to another at a TransferNode, rolling back on any detected anomaly.
- S3d: `SettlementCommitter` — Takes the winning route's payload at its terminal node, applies finality seals, and writes the settlement record to the immutable log.

#### Facet 4 - Certificates

- S4a: `RouteSelectionCertificate` — Proves that the selected route won fair competition against all alternatives under the declared cost function.
- S4b: `TransferAtomicityReceipt` — Attests that a payload transfer at a TransferNode completed atomically with no partial state observable.
- S4c: `SettlementFinalitySeal` — Certifies that a settled payload has been committed and no further modifications are possible.
- S4d: `RouteUniquenessProof` — Proves that exactly one route was settled for the given source-destination pair at the specified epoch.

### Lens F

#### Facet 1 - Objects

- F1a: `RoutePhaseVector` — A vector encoding the current phase of each active route (proposal, competition, transfer, settlement) as a cyclic state variable.
- F1b: `CompetitionWave` — The propagating wavefront of route proposals expanding through the mycelium graph from a source node.
- F1c: `SettlementEquilibrium` — The steady-state configuration reached when all active routes have settled and no further competition is pending.
- F1d: `TransferResonance` — The harmonic alignment achieved when multiple transfer events at the same node synchronize their timing for minimal latency.

#### Facet 2 - Laws

- F2a: `PhaseDeterminism` — The phase of every route must advance monotonically through the cycle (proposal -> competition -> transfer -> settlement) without regression.
- F2b: `WavePropagationBound` — A competition wave must not propagate beyond the declared horizon without explicit extension authorization.
- F2c: `EquilibriumConvergence` — The system must reach settlement equilibrium within a bounded number of competition rounds for any finite route set.
- F2d: `ResonanceStabilityLaw` — Transfer resonance at a node must remain stable under small perturbations to route timing.

#### Facet 3 - Constructions

- F3a: `PhaseAdvancer` — Steps each active route's phase to the next stage in the cycle, verifying preconditions before each transition.
- F3b: `WavefrontExpander` — Extends the competition wave by one hop through the mycelium graph, adding newly reachable nodes to the candidate set.
- F3c: `EquilibriumSolver` — Iteratively resolves competition among active routes until a global settlement equilibrium is reached or the round limit is hit.
- F3d: `ResonanceTuner` — Adjusts transfer timing at a node to achieve or maintain harmonic alignment among intersecting routes.

#### Facet 4 - Certificates

- F4a: `PhaseMonotonicityCertificate` — Proves that a route's phase advanced strictly forward through the cycle without any regression event.
- F4b: `WaveBoundReceipt` — Attests that the competition wave did not exceed its declared propagation horizon.
- F4c: `EquilibriumConvergenceProof` — Certifies that settlement equilibrium was reached within the declared round bound.
- F4d: `ResonanceStabilitySeal` — Proves that transfer resonance at a given node remained stable throughout the settlement epoch.

### Lens C

#### Facet 1 - Objects

- C1a: `RouteDeterminismPredicate` — A decidable boolean asserting whether the route selection outcome is uniquely determined by the inputs and cost function.
- C1b: `TransferValidityState` — A truth value recording whether a given transfer event satisfied all atomicity and consistency preconditions.
- C1c: `SettlementFinalityFlag` — A write-once boolean that, once set, certifies the payload as immutable and blocks all further modification attempts.
- C1d: `RouteTruthCorridor` — The narrow band of consistent truth assignments through which all competing routes must pass to be considered lawful.

#### Facet 2 - Laws

- C2a: `DeterminismDecidability` — Route determinism must be decidable in finite time given the cost function and the full set of competing routes.
- C2b: `TransferValidityCompleteness` — Every transfer event must have its validity evaluated; no transfer may proceed with an unknown validity state.
- C2c: `FinalityIrreversibility` — The settlement finality flag, once written, cannot be cleared, overwritten, or circumvented by any operation in the system.
- C2d: `TruthCorridorExclusivity` — At most one consistent truth assignment may exist for each route-selection decision; multiplicity forces arbitration.

#### Facet 3 - Constructions

- C3a: `DeterminismVerifier` — Evaluates the route-selection inputs and cost function to determine whether the outcome is uniquely fixed, emitting a proof or counterexample.
- C3b: `TransferValidityChecker` — Audits a transfer event against all preconditions and produces a validity certificate or a detailed failure trace.
- C3c: `FinalityEnforcer` — Monitors the settlement finality flag and actively blocks any operation that attempts to modify a settled payload.
- C3d: `TruthCorridorResolver` — Eliminates inconsistent truth assignments from the route corridor until at most one remains, escalating ties to Ch01.

#### Facet 4 - Certificates

- C4a: `DeterminismProof` — Certifies that the route selection outcome was uniquely determined by the declared inputs.
- C4b: `TransferValidityCertificate` — Proves that a specific transfer event satisfied all required preconditions for atomicity and consistency.
- C4c: `FinalityIntegritySeal` — Attests that the settlement finality flag has not been tampered with since its initial write.
- C4d: `TruthCorridorResolutionReceipt` — Proves that the truth corridor resolved to exactly one assignment or was correctly escalated.

### Lens R

#### Facet 1 - Objects

- R1a: `RecursiveRouteSeed` — A route definition that generates sub-routes at each level of recursion, creating a fractal metro topology from a single specification.
- R1b: `FractalMetroGraph` — A self-similar graph structure where each node, when expanded, reveals a complete sub-metro with the same topological properties as the parent.
- R1c: `SelfSettlingPath` — A route that carries its own settlement logic internally and can commit its payload at any node satisfying the settlement predicate.
- R1d: `MetroFixedPoint` — A routing configuration where the output of the route-selection process, when fed back as input, reproduces the same route.

#### Facet 2 - Laws

- R2a: `RecursiveRouteTermination` — Every recursive route seed must terminate its expansion within a declared depth bound to prevent infinite metro growth.
- R2b: `FractalTopologyPreservation` — The sub-metro revealed by expanding any node must be isomorphic in topology to the parent metro up to a declared scale factor.
- R2c: `SelfSettlementValidity` — A self-settling path's internal settlement logic must satisfy the same finality guarantees as the global SettlementCommitter.
- R2d: `FixedPointUniqueness` — For a given cost function and route set, the metro fixed point must be unique; multiple fixed points require explicit disambiguation.

#### Facet 3 - Constructions

- R3a: `RecursiveRouteExpander` — Unfolds a recursive route seed to a specified depth, emitting the complete sub-route hierarchy for execution.
- R3b: `FractalGraphBuilder` — Constructs a fractal metro graph from a topology template, replicating it at each scale level with appropriate edge rewiring.
- R3c: `SelfSettlementEngine` — Executes the internal settlement logic of a self-settling path, applying finality seals upon reaching a qualifying node.
- R3d: `MetroFixedPointIterator` — Repeatedly applies the route-selection process to its own output until convergence to the metro fixed point is detected.

#### Facet 4 - Certificates

- R4a: `RecursiveTerminationProof` — Proves that a recursive route seed completed its expansion within the declared depth bound.
- R4b: `TopologyPreservationCertificate` — Certifies that fractal sub-metros maintain topological isomorphism with the parent at all generated levels.
- R4c: `SelfSettlementReceipt` — Attests that a self-settling path's internal commitment satisfied the global finality invariants.
- R4d: `FixedPointConvergenceSeal` — Proves that the metro fixed-point iterator converged to a unique stable configuration within the declared iteration bound.
