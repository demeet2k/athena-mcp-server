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
13. COLLECTIVE DUAL CONTROL V7 — model-conditional uncertainty decomposition, prequential empirical coverage bands, observational association-skeleton/v-structure hypotheses, ridge state-dependent stochastic transition models, bounded moment scenario/CVaR evaluation, control+information dual-control proxy planning, supplied-DAG BACKDOOR/FRONTDOOR/INSTRUMENT identification checks, replication effective-N geometry and diverse replication/falsifier design.
14. Runtime — hydrate, conditional writes, telemetry, adoption, replayable sessions, exact final emission.

## Objective hierarchy

Base:

`J = w_O·O - w_C·C`.

Normalized organization comparison:

`RGO = mean(O)/(1+mean(C))`.

V2: `predicted_RGO -> observed_RGO -> calibrated_RGO`.

V3: `explicit observed reward -> bounded versioned policy update -> rollbackable policy state`.

V4: `context + regime + arm history -> <mean,uncertainty,UCB>` plus `outcome -> <credit,causal confidence,residual>`.

V5: `correlated context -> <posterior mean,covariance,calibrated interval>`; `hypotheses + candidate experiments -> expected information gain`; `factorial/delayed outcomes -> qualified credit`; `observed transitions -> shrinkage dynamics`; `candidate organizations -> Pareto frontier`.

V6: `raw context -> <nonlinear basis, empirical OOD pressure>`; `hypotheses + finite factor space -> generated experiment frontier`; `supplied causal DAG -> conditional back-door adjustment sets`; `observed transition vectors -> multivariate delta covariance`; `model + uncertainty -> receding-horizon plan`; `small fully declared schedule -> exact finite-model certificate`; `claim -> replication/falsification witness graph`.

V7: `Bayesian/OOD/calibration state -> uncertainty-source diagnostic`; `retained pre-update residuals -> empirical prequential band`; `observational samples -> association skeleton/v-structure hypotheses`; `before-state + action -> state-dependent delta distribution`; `state model -> finite scenario/CVaR surface`; `control reward + parameter information - predictive risk -> bounded dual-control proxy`; `supplied DAG -> BACKDOOR/FRONTDOOR/INSTRUMENT conditional identification`; `witness metadata -> replication effective-N + diverse next-test design`.

## Current developmental metabolism

`HYDRATE`
`-> MINIMUM-SUFFICIENT RUNTIME DEPTH`
`-> MEMORY/ANTIBODY/ELDER/SCIENCE-SHADOW`
`-> COARSE+LEARNED REGIME + OOD`
`-> BAYES/CALIBRATION/NONLINEAR BASIS`
`-> OPTIONAL UNCERTAINTY DECOMPOSITION/PREQUENTIAL BAND`
`-> LIVE CAUSAL/MECHANISTIC HYPOTHESES`
`-> OPTIONAL ASSOCIATION-SKELETON HYPOTHESIS GENERATION`
`-> GENERATE/RANK EXPERIMENTS`
`-> CONDITIONAL BACKDOOR/FRONTDOOR/IV IDENTIFICATION`
`-> PARETO EXPERIMENT FRONTIER`
`-> COLLECTIVE PLAN`
`-> CERTIFIED/HEURISTIC MULTIPERIOD SCHEDULE`
`-> STATE-DEPENDENT TRANSITION MODEL`
`-> OPTIONAL SCENARIO/CVAR EVALUATION`
`-> OPTIONAL DUAL-CONTROL PLAN`
`-> EXECUTE FIRST AUTHORIZED ACTION`
`-> OBSERVE/METER`
`-> QUORUM/FALSIFICATION/WITNESS`
`-> DIRECT/HIGHER-INTERACTION/DELAYED CREDIT`
`-> BAYES/BANDIT/POLICY/TRANSITION UPDATE`
`-> REPLICATION-INDEPENDENCE/REPLICATION-DESIGN UPDATE`
`-> PHEROMONE/DIFFUSION/IMMUNE/ELDER UPDATE`
`-> JSPACE/TOPOLOGY/PROJECTION/COMPENSATION`
`-> LIFECYCLE`
`-> FINALIZE/VERIFY/COMMIT`
`-> REPLAN/REATTACK`.

## Authority surfaces

- semantic state: expected-VID / semantic event-head authority;
- Git state: expected Git HEAD;
- topology state: expected topology version;
- V3 learned policy: expected policy version;
- V4–V7 statistical/control/design state: observational predictive/design evidence only, never semantic authority;
- V6/V7 causal-identification state: a theorem/query result relative to a supplied graph/assumption surface, never independent proof that the supplied graph is true;
- V7 observational skeleton/v-structure output: hypothesis-generation metadata only, not a causal graph authority;
- science-shadow replication/falsification state: evidence-navigation metadata, never a hidden canonical-object mutation;
- V7 replication effective-N: metadata-similarity diagnostic, not formal independence proof;
- diffusion/pheromone: routing priors, not dependency truth;
- learned regimes/OOD: transfer/calibration neighborhoods, not semantic identity or truth labels;
- Pareto/scenario/dual-control surfaces: planning/tradeoff simulations, not execution or canonical fact;
- projection/compensation: semantic recovery operations with separate Git consequences.

## V7 uncertainty boundary

V7 separates useful diagnostics without pretending uncertainty has a unique physical factorization. Using V5/V6 ridge posterior leverage `h(phi)=phi^T A^-1 phi`, residual noise, OOD pressure and empirical calibration error, it exposes aleatoric/noise, parameter-epistemic, distribution-shift and calibration-error proxies. The quadrature total is routing evidence only.

`UNCERTAINTY_DECOMPOSITION != UNIQUE_PHYSICAL_DECOMPOSITION`.

## V7 prequential-coverage boundary

V5 retained pre-update prediction errors are reused as prequential nonconformity scores. A finite empirical residual quantile forms a current prediction band, widened by V6 OOD pressure. Too few scores returns `INSUFFICIENT_PREQUENTIAL_SCORES` rather than a fabricated coverage claim.

`PREQUENTIAL_EMPIRICAL_INTERVAL != DISTRIBUTION_FREE_CONFORMAL_GUARANTEE UNDER ARBITRARY SHIFT`.

## V7 causal-skeleton boundary

Marginal and one-variable partial correlations can remove weak association edges and produce candidate collider motifs. This is transparent bounded hypothesis generation, not calibrated PC/FCI causal discovery.

`ASSOCIATION_SKELETON != CAUSAL_DAG`; `V_STRUCTURE_CANDIDATE != CAUSAL_ORIENTATION`.

## State-dependent transition boundary

V7 fits ridge action-specific delta models

`Delta = B phi(x) + epsilon`

from real V5 before/after observations. Residual covariance plus query-state leverage yields a predictive covariance surface. Unseen actions remain unmodeled.

`STATE_DEPENDENT_TRANSITION_MODEL != WORLD_TRUTH`.

## Scenario / dual-control boundary

V7 scenario evaluation uses a bounded three-branch dominant-covariance moment tree for caller-supplied short action sequences and reports expected return plus lower-tail CVaR. It is `SIMULATE_ONLY`.

V7 dual control optimizes a bounded proxy:

`control + lambda_I * information - lambda_R * risk`.

Parameter information is derived from state-model leverage. The lawful loop remains:

`PLAN -> EXECUTE_FIRST_AUTHORIZED_ACTION -> OBSERVE_REAL_NEXT_STATE -> RECORD -> REPLAN`.

`SCENARIO_TREE != OBSERVED_FUTURE`; `DUAL_CONTROL_PROXY != EXACT_BELIEF_STATE_OPTIMAL_CONTROL`.

## Extended causal-identification boundary

V7 retains V6 BACKDOOR checks and adds supplied-DAG FRONTDOOR and INSTRUMENT criterion checks. A passing result means the declared graph/observability/assumption surface satisfies the runtime's bounded criterion. It does not prove the graph is the real data-generating graph and does not estimate the causal effect itself.

`FRONTDOOR_OR_IV_IDENTIFICATION != CAUSAL_TRUTH OUTSIDE SUPPLIED DAG/ASSUMPTIONS`.

## Replication independence/design boundary

Witness evidence metadata is compared across dataset, implementation, method, operator, environment and seed-family dimensions. Confidence-weighted effective evidence count is

`N_eff = (sum_i w_i)^2 / sum_ij w_i w_j s_ij`.

Identical pipelines collapse toward effective `N=1`; diverse evidence can approach raw witness count. Missing comparable metadata defaults conservatively rather than assuming independence.

Replication/falsifier design uses expected evidential power × diversity × feasibility minus cost/risk. It returns `DESIGN_ONLY`.

`ESTIMATED_REPLICATION_INDEPENDENCE != FORMAL_STATISTICAL_INDEPENDENCE`; `REPLICATION_DESIGN != REPLICATION_RESULT`.

## V1–V6 boundaries retained

V6 nonlinear/OOD, experiment-generation, back-door, higher-order interaction, MPC, exact-small scheduling, witness-capsule, Pareto and science-shadow laws remain in force. V5 projection compensation remains a narrow semantic inverse; Git compensation remains separate. Unknown resource costs and missing factorial cells never become favorable zeros.

## Non-negotiable V7 firewall

- identity != coordinate
- tested != current != canonical != integrated
- UNKNOWN != N/A
- UNKNOWN_COST != ZERO_COST
- prediction != observation
- posterior != truth
- calibration != model validity
- uncertainty decomposition != unique physical decomposition
- prequential empirical band != universal distribution-free coverage
- nonlinear basis != universal inference
- OOD score != factual falsehood
- generated/design experiment != result
- association skeleton != causal DAG
- v-structure candidate != causal orientation
- back-door/front-door/IV identification != causal truth outside supplied DAG/assumptions
- attribution != causal proof
- missing factorial cell != zero interaction
- transition/state model != world truth
- scenario tree != observed future
- MPC/dual-control plan != execution
- dual-control proxy != exact Bayes-adaptive optimal control
- rollout != training observation
- bounded/certified schedule claims are scoped to the declared search/model
- witness cell/capsule != kernel/VM security proof
- Pareto frontier/experiment selection != single best action
- replication/falsification state != canonical truth
- estimated replication independence != formal independence proof
- replication/falsifier design != result
- projection saga != atomic transaction
- semantic compensation != Git rollback
- local success != global authority
- pruning removes active routing privilege, never required lineage

## Coordinate fibers

`COLLECTIVE=<F,R,N,D,Q,C,O,H,L>`

`COLLECTIVE_LEARNING=<B,P,CF,E,A,MS,L>`

`COLLECTIVE_ECOLOGY=<RG,X,CR,WS,DF,RW,RO,PS,L>`

`COLLECTIVE_SCIENCE=<BY,CAL,ED,IX,DL,TR,SC,WC,RG,PF,CP,L>`

`COLLECTIVE_DISCOVERY=<NL,OOD,EG,CI,HI,TD,MPC,CS,HC,PB,RF,L>`

`COLLECTIVE_DUAL_CONTROL=<UD,PI,CG,SM,SC,DC,CX,RI,RD,L>`.
