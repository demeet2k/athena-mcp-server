# Architecture

0. Git causal persistence — literal history and checkpoint CAS.
1. CCR — deterministic functional identity for reusable capability.
2. JSPACE — typed semantic multigraph over objects, versions, events, manifestations, agents and mutations.
3. SCALE — `S0 event → S1 delta → S2 relation → S3 motif → S4 generator → S5 organ law`.
4. KC144 — immutable 12×12 host topology; coordinate is never identity.
5. Polycoordinate/transform runtime — open-world charts, executable derivations, measured holonomy, exact visible-output coordinates.
6. COLLECTIVE V1 — HIVE/SWARM/PACK/FLOCK/HERD/POD geometry, dynamic width, roles, bounded topology, quorum/inhibition, reserve and homeostasis.
7. COLLECTIVE GROWTH — demand allocation, bridge accounting, FISSION/FUSE/HOLD pressure, alarm propagation, lifecycle/apoptosis.
8. COLLECTIVE MEMORY V2 — persistent pheromones, typed JSPACE invalidation, observed-RGO calibration, topology CAS/rollback, failure antibodies.
9. COLLECTIVE LEARNING V3 — measured resource metabolism, bounded rollbackable learned policy, counterfactuals, elder authority, antibody evolution, multiscale pheromones.
10. COLLECTIVE ECOLOGY V4 — task regimes, contextual-UCB experiment selection, causal-confidence credit/residual, worker budget scheduling, learned diffusion, executable regression witnesses, uncertainty-banded rollouts, topology→JSPACE recovery sagas.
11. COLLECTIVE SCIENCE V5 — full-covariance contextual uncertainty + empirical interval calibration, information-gain experiment design, factorial interaction/delayed credit, learned transition dynamics, multi-period scheduling, stronger constrained witness cells, learned regime geometry, Pareto-front search, projection-edge compensation.
12. COLLECTIVE DISCOVERY V6 — degree-2 nonlinear Bayesian lift + empirical OOD geometry, factor-space experiment generation, supplied-DAG back-door identification, higher-order factorial contrasts, multivariate transition covariance, receding-horizon MPC, exact small-model schedule certification, fail-closed namespace witness capsules, Pareto experiment selection, and replication/falsification science shadows.
13. Runtime — hydrate, conditional writes, telemetry, adoption, replayable sessions, exact final emission.

## Objective hierarchy

Base:

`J = w_O·O - w_C·C`.

Normalized organization comparison:

`RGO = mean(O)/(1+mean(C))`.

V2: `predicted_RGO -> observed_RGO -> calibrated_RGO`.

V3: `explicit observed reward -> bounded versioned policy update -> rollbackable policy state`.

V4: `context + regime + arm history -> <mean,uncertainty,UCB>` plus `outcome -> <credit,causal confidence,residual>`.

V5: `correlated context -> <posterior mean,covariance,calibrated interval>`; `hypotheses + candidate experiments -> expected information gain`; `factorial/delayed outcomes -> qualified credit`; `observed transitions -> shrinkage dynamics`; `candidate organizations -> Pareto frontier`.

V6: `raw context -> <nonlinear basis, empirical OOD pressure>`; `hypotheses + finite factor space -> generated experiment frontier`; `supplied causal DAG -> conditional back-door adjustment sets`; `observed transition vectors -> multivariate delta covariance`; `model + uncertainty -> receding-horizon plan`; `small fully declared schedule -> exact finite-model certificate`; `claim -> independent replication/falsification witness graph`.

## Current developmental metabolism

`HYDRATE`
`-> MEMORY/ANTIBODY/ELDER/SCIENCE-SHADOW`
`-> COARSE+LEARNED REGIME + OOD`
`-> BAYES/CALIBRATION/NONLINEAR BASIS`
`-> LIVE HYPOTHESES`
`-> GENERATE/RANK EXPERIMENTS`
`-> CONDITIONAL CAUSAL IDENTIFICATION`
`-> PARETO EXPERIMENT FRONTIER`
`-> COLLECTIVE PLAN`
`-> CERTIFIED/HEURISTIC MULTIPERIOD SCHEDULE`
`-> EXECUTE/METER`
`-> QUORUM/FALSIFICATION/WITNESS`
`-> OBSERVE`
`-> DIRECT/HIGHER-INTERACTION/DELAYED CREDIT`
`-> BAYES/BANDIT/POLICY UPDATE`
`-> MULTIVARIATE TRANSITION UPDATE`
`-> MPC REPLAN`
`-> PHEROMONE/DIFFUSION/IMMUNE/ELDER/REPLICATION UPDATE`
`-> JSPACE/TOPOLOGY/PROJECTION/COMPENSATION`
`-> LIFECYCLE`
`-> FINALIZE/VERIFY/COMMIT`.

## Authority surfaces

- semantic state: expected-VID / semantic event-head authority;
- Git state: expected Git HEAD;
- topology state: expected topology version;
- V3 learned policy: expected policy version;
- V4–V6 statistical/control state: observational predictive/design evidence only, never semantic authority;
- causal-identification state: a theorem/query result relative to a supplied graph/assumption surface, never independent proof that the supplied graph is true;
- science-shadow replication/falsification state: evidence-navigation metadata, never a hidden canonical-object mutation;
- diffusion/pheromone: routing priors, not dependency truth;
- learned regimes/OOD: transfer/calibration neighborhoods, not semantic identity or truth labels;
- Pareto surfaces: tradeoff/experiment sets, not a canonical single winner;
- projection/compensation: semantic recovery operations with separate Git consequences.

## Nonlinear/OOD boundary

V6 transparently applies a degree-2 polynomial feature lift over the V5 full-covariance Bayesian model. This captures squares/pair interactions in the predictive basis but is not labeled a GP, neural posterior or universal function approximator.

An independent empirical context distribution tracks raw features. Ridge-regularized Mahalanobis distance plus unseen-feature pressure produces OOD state. OOD inflates inherited predictive intervals and reduces transfer confidence; it is not evidence that a factual claim is false.

`NONLINEAR_BASIS != UNIVERSAL_INFERENCE`; `OOD_SCORE != FACTUAL_FALSEHOOD`.

## Experiment-generation boundary

V6 generates only the finite Cartesian product of caller-declared factor levels. Hypothesis likelihoods are derived only from supplied `base_p + factor_effects`; the runtime does not invent causal mechanisms to fill missing models. Candidate cost/risk/feasibility/ethics are carried into V5 EIG ranking.

Generated experiments remain `DESIGN_ONLY`.

## Conditional causal-identification boundary

V6 back-door search removes treatment out-edges, excludes treatment descendants, then tests d-separation in the moralized relevant ancestral graph. A returned adjustment set is valid only relative to the supplied DAG, observed-node declaration, causal semantics and confounding assumptions.

Explicit latent-confounding risk blocks promotion.

`IDENTIFIED_BACKDOOR_UNDER_DAG != CAUSE_PROVEN_IN_REALITY`.

## Higher-order interaction boundary

For order `k<=4`, all `2^k` binary factorial cells are required. The inclusion-exclusion contrast is not computed when a cell is missing. Numerical contrasts remain associational unless design confidence supplies identification support.

## Transition/MPC boundary

V6 reconstructs multivariate empirical action-conditioned delta covariance directly from measured V5 before/after rows, with shrinkage toward no change while evidence is sparse. Unseen actions/features remain unmodeled.

MPC uses this surface for bounded receding-horizon planning. The lawful loop is:

`PLAN_H -> EXECUTE_FIRST_AUTHORIZED_ACTION -> OBSERVE_REAL_NEXT_STATE -> UPDATE -> REPLAN`.

MPC never creates transition observations itself.

`STOCHASTIC_TRANSITION_MODEL != WORLD_TRUTH`; `MPC_PLAN != EXECUTION`.

## Resource/scheduling boundary

Automatically observable: MCP tool calls and wall time. Optional caller-observable dimensions include tokens, compute, retrieval, storage, attention, CPU/GPU time, energy, memory and network bytes. Unknown dimensions remain `UNKNOWN`, never zero.

V5 provides bounded beam scheduling. V6 can exhaustively enumerate small fully declared finite schedules and issue `EXACT_ENUMERATION_CERTIFIED` only when enumeration finishes before the node bound. If search truncates, task count exceeds the exact limit, or a supplied constrained budget dimension is missing from any task cost model, the exact certificate is removed.

A certificate proves optimality only inside the declared finite scheduling model.

## Witness boundary

V5 witness cells are process-constrained but non-hermetic. V6's stronger capsule requires Linux bubblewrap. When unavailable it fails closed with `HERMETIC_UNAVAILABLE` and executes nothing; it never silently falls back.

When bubblewrap is used, `hermetic=true` means the declared mount/network namespace isolation ran. It is not a kernel/interpreter/native-runtime security proof.

## Pareto experiment boundary

V6 treats interval-valued objective candidates as robustly dominated only when one candidate's worst-case vector dominates another candidate's best-case vector across all directed objectives. The interval-possible frontier may be prioritized by uncertainty for measurement. That selection remains an experiment-selection surface, not a universal value ordering.

## Replication/falsification boundary

Science-shadow claims are separate from canonical objects. TEST/REPLICATION/FALSIFIER witnesses carry result, confidence, actor/evidence and explicit `independence_key`. States such as `REPLICATED_SUPPORT`, `FALSIFICATION_SIGNAL` and `CONTESTED` route future verification but cannot silently modify the canonical registry.

## Projection/compensation boundary

V4 projection remains a cross-store recovery saga. V5 adds a narrow semantic inverse for active projection-owned edges under semantic-head CAS. Git compensation remains separate; history is never erased.

## Non-negotiable discovery firewall

- identity != coordinate
- tested != current != canonical != integrated
- UNKNOWN != N/A
- UNKNOWN_COST != ZERO_COST
- prediction != observation
- posterior != truth
- calibration != model validity
- nonlinear basis != universal inference
- OOD score != factual falsehood
- expected information gain != evidence
- generated/design experiment != result
- back-door set != causal truth outside supplied DAG/assumptions
- association != causation
- attribution != causal proof
- missing factorial cell != zero interaction
- higher-order contrast != causal interaction without identification
- temporal delay != causation
- learned policy != canonical truth
- learned regime != semantic identity
- transition model != world truth
- MPC plan != execution
- rollout != execution/commit/training observation
- bounded/certified schedule claims are scoped to the declared search/model
- diffusion posterior != causal path
- pheromone != authority
- elder != oracle
- regression pass != universal proof
- witness cell/capsule != kernel/VM security proof
- Pareto frontier/experiment selection != single best action
- replication/falsification state != canonical truth
- projection saga != atomic transaction
- semantic compensation != Git rollback
- local success != global authority
- pruning removes active routing privilege, never required lineage

## Coordinate fibers

`COLLECTIVE=<F,R,N,D,Q,C,O,H,L>`

`COLLECTIVE_LEARNING=<B,P,CF,E,A,MS,L>`

`COLLECTIVE_ECOLOGY=<RG,X,CR,WS,DF,RW,RO,PS,L>`

`COLLECTIVE_SCIENCE=<BY,CAL,ED,IX,DL,TR,SC,WC,RG,PF,CP,L>`

`COLLECTIVE_DISCOVERY=<NL,OOD,EG,CI,HI,TD,MPC,CS,HC,PB,RF,L>`.
