# Architecture

0. Git causal persistence — literal history and checkpoint CAS.
1. CCR — deterministic functional identity for every reusable capability.
2. JSPACE — typed semantic multigraph over objects, versions, events, agents, manifestations and mutations.
3. SCALE — `S0 event → S1 delta → S2 relation → S3 motif → S4 generator → S5 organ law`.
4. KC144 — immutable 12×12 host topology; coordinate is never identity.
5. Polycoordinate/transform runtime — open-world charts, executable transforms, measured holonomy, exact output coordinates.
6. COLLECTIVE runtime — selects HIVE/SWARM/PACK/FLOCK/HERD/POD execution geometry, right-sizes worker count from marginal utility, preserves reserve capacity, allocates roles and bounded-neighbor topology, performs evidence-sensitive quorum/inhibition, advisory stigmergic reinforcement/evaporation, and homeostatic overload control.
7. COLLECTIVE GROWTH — demand-sensitive task allocation, living-bridge accounting, FISSION/FUSE/HOLD structural pressure, dependency-scoped alarm waves, and lineage-preserving artifact lifecycle/apoptosis.
8. COLLECTIVE MEMORY V2 — persistent pheromone field, typed JSPACE invalidation compiler, observed-RGO calibration, versioned/CAS collective topology transactions with rollback witnesses, and failure-antibody detector/repair/regression memory.
9. COLLECTIVE LEARNING V3 — measured resource metabolism, bounded versioned organization-policy learning with rollback, counterfactual organization ranking, evidence-backed elder authority, empirical antibody-family evolution, and attenuated multiscale pheromone transport.
10. COLLECTIVE ECOLOGY V4 — observable task-regime partitioning, uncertainty-aware contextual-bandit experiment selection, causal-confidence credit assignment with unattributed residual, measured per-worker budget scheduling, shrinkage-learned scale diffusion, restricted executable regression witnesses, uncertainty-banded multi-step rollouts, and recoverable topology→JSPACE projection sagas.
11. Runtime — hydrate, conditional writes, telemetry, adoption, replayable session state and exact final emission.

## Collective objective hierarchy

Base organization objective:

`J = w_O·O - w_C·C`.

Normalized comparison:

`RGO = mean(O)/(1+mean(C))`.

V2 adds empirical correction:

`predicted_RGO -> observed_RGO -> calibrated_RGO`.

V3 adds bounded learned policy:

`explicit observed reward -> versioned policy update -> rollbackable policy state`.

V4 adds experimental uncertainty and causal-credit surfaces:

`context + regime + arm history -> <mean,uncertainty,UCB>`

and

`outcome_delta -> <credited interventions, causal confidence, unattributed residual>`.

A high exploration score is allowed to increase the probability of **testing** an option; it is forbidden from increasing the option's factual authority merely because it was explored.

## Growth metabolism

`HYDRATE`
`-> MEMORY/ANTIBODY/ELDER QUERY`
`-> TASK REGIME`
`-> BUDGET/POLICY/POSTERIOR STATE`
`-> COLLECTIVE PLAN`
`-> RGO CALIBRATION`
`-> UCB EXPERIMENT SELECTION`
`-> OPTIONAL UNCERTAINTY-BANDED ROLLOUT`
`-> BUDGET-AWARE WORKER SCHEDULING`
`-> EXECUTION + RESOURCE METERING`
`-> QUORUM / VERIFICATION / FALSIFICATION`
`-> OBSERVED OUTCOME`
`-> CAUSAL-CONFIDENCE CREDIT`
`-> BANDIT / POLICY / WORKER-COST UPDATE`
`-> DIFFUSION / PHEROMONE / ELDER / ANTIBODY UPDATE`
`-> JSPACE INVALIDATION`
`-> TOPOLOGY CAS / OPTIONAL PROJECTION SAGA`
`-> LIFECYCLE`
`-> FINALIZE / VERIFY / COMMIT`.

## Authority surfaces

- semantic state: expected-VID CAS;
- Git state: expected-Git-head CAS;
- collective topology: expected-topology-version CAS;
- learned organization policy: expected-policy-version CAS;
- contextual bandit state: observational action/reward memory, not canonical semantic authority;
- causal-credit state: evidential attribution surface, never silent proof of causality;
- diffusion state: empirical routing prior, not JSPACE dependency truth;
- projection state: recovery saga that may bridge topology to JSPACE only after exact head preflight.

Collective topology does not silently rewrite canonical JSPACE. Learned policy does not silently rewrite semantic truth or topology. Bandit posterior does not certify a claim. Credit confidence does not erase unattributed outcome residual. Rollback is a new witnessed transaction, never deletion of history. Counterfactual and rollout rankings are simulation outputs, not commits. Failure-antibody matches route verification/repair but do not prove common cause. Elder authority is measured and defeasible, never conferred by age alone.

## Measured-resource boundary

Automatically observable in this MCP runtime:

- tool-call count;
- tool-call wall time.

Stored when an observable caller supplies them:

- token count;
- compute units;
- retrieval operations;
- storage bytes;
- human attention minutes;
- CPU time;
- GPU time;
- energy joules;
- peak memory;
- network bytes.

Unobserved dimensions remain `UNKNOWN`. `UNKNOWN_COST != ZERO_COST`. Worker scheduling applies uncertainty pressure instead of converting missing measurements into free resources.

## Experimental-learning boundary

The V4 contextual-bandit layer is an experiment selector. Its upper confidence bound is:

`UCB = mean + alpha * uncertainty`.

This creates lawful exploration pressure without conflating option value with truth. Posterior updates require explicit observed reward.

The V4 causal-credit layer preserves the distinction between a useful association and an identified causal effect. Randomization, controls, direct measurement, isolation, replication, and counterfactual evidence raise confidence; otherwise credit remains explicitly associational and a residual term remains unassigned.

## Projection boundary

Topology and JSPACE are distinct stores. A projection plan derives structural edges from topology state, then preflights exact topology version and semantic event head. Optional Git persistence also preflights exact Git HEAD.

Because semantic SQLite mutation and Git commit cannot be made one physical ACID transaction by the current runtime, V4 uses a saga:

`PREPARED -> SEMANTIC_APPLIED -> GIT_COMMITTED? -> COMPLETED`.

Failure before semantic application gives `ABORTED`. Failure after partial semantic application gives `COMPENSATION_REQUIRED`.

The runtime MUST NOT describe this sequence as atomic distributed rollback.

## Non-negotiable laws

- same namespace != same lineage
- delivered != hydrated != consumed != adopted
- coordinate != identity
- tested != current != canonical != integrated
- UNKNOWN != N/A
- UNKNOWN cost != zero cost
- compression requires RETURN
- global mutations require next-cycle adoption
- public telemetry never stores private chain-of-thought
- maximum growth != maximum activity
- maximum integration != maximum connectivity
- consensus != evidence
- prediction != observation
- learned policy != canonical truth
- counterfactual != commit
- rollout != commit
- exploration score != evidence
- UCB != truth
- bandit prediction != reward
- association != causation
- attribution != causal proof
- regime transfer != identity
- measured cost != estimated cost
- diffusion posterior != causal path
- regression pass != universal proof
- projection saga != atomic transaction
- preserve reserve when feasible
- stop adding workers when marginal output <= marginal coordination cost
- recruitment requires inhibition/contradiction/evaporation
- allocate by demand × fit × available capacity, not equal participation
- budget-aware scheduling must distinguish EXPLICIT / MEASURED_HISTORY / UNKNOWN resource models
- build bridges only when expected saved work exceeds build + maintenance + locked capacity
- invalidation transport must use typed relation semantics; unknown relation orientation is ignored rather than fabricated
- persistent route priority must remain erasable by age/staleness/contradiction
- predicted organizational fitness must be reconciled against observed outcomes
- organization-policy learning is bounded, regularized, versioned and rollbackable
- bandit state updates only from explicit observed reward
- multi-intervention outcomes require credit decomposition before per-action learning when causal attribution is uncertain
- topology mutation requires CAS + before/after witness + rollback path
- topology→JSPACE projection requires exact head preflight + recovery journal
- diagnosed failures should become detector + repair + regression antibodies
- executable regression witnesses are restricted to repository-owned unittest references; arbitrary commands are prohibited
- antibody variants require empirical outcome tracking and remain hypotheses
- multiscale pheromone propagation attenuates or learns through shrinkage; local success cannot receive global-strength promotion without evidence
- elder authority derives from repeated reuse/prediction/repair/regression/generalization success with contradiction penalty
- pruning removes active priority, never required lineage
