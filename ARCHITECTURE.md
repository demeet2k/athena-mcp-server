# Architecture

0. Git causal persistence — literal history and checkpoint CAS.
1. CCR — deterministic reusable capability identity.
2. JSPACE — typed semantic graph/hypergraph.
3. SCALE — `S0 event → S1 delta → S2 relation → S3 motif → S4 generator → S5 organ law`.
4. KC144 — immutable host topology; coordinate is never identity.
5. Polycoordinate/transform runtime — open-world charts, executable derivations, measured holonomy and exact visible-output coordinates.
6. COLLECTIVE V1 — form, dynamic width, roles, reserve, bounded topology, quorum/inhibition and homeostasis.
7. COLLECTIVE GROWTH — demand, bridge economics, fission/fusion pressure, alarms and lifecycle.
8. COLLECTIVE MEMORY V2 — persistent pheromones, typed invalidation, RGO calibration, topology CAS/rollback, antibodies.
9. COLLECTIVE LEARNING V3 — measured budgets, bounded policy learning, counterfactuals, elders, immune evolution, multiscale pheromones.
10. COLLECTIVE ECOLOGY V4 — contextual UCB, causal-confidence credit/residual, worker cost, adaptive diffusion, regression execution, rollouts, projection sagas.
11. COLLECTIVE SCIENCE V5 — full-covariance contextual Bayes, empirical calibration, EIG design, interaction/delayed credit, learned transitions, multi-period scheduling, regime geometry, Pareto, semantic compensation.
12. COLLECTIVE DISCOVERY V6 — nonlinear/OOD, generated experiment spaces, supplied-DAG back-door ID, higher-order interactions, multivariate transitions, MPC, schedule certificates, fail-closed capsules, Pareto experiment selection, replication/falsification shadows.
13. COLLECTIVE DUAL CONTROL V7 — uncertainty decomposition, prequential bands, association-skeleton hypotheses, state-dependent dynamics, scenario/CVaR evaluation, control+information planning, BACKDOOR/FRONTDOOR/IV checks, replication independence/design.
14. COLLECTIVE BELIEF V8 — persistent finite model beliefs, explicit Bayes observation updates, decision EVI, depth-1 belief-aware control, assumption-scoped effect estimates, bootstrap structure stability, contingent policies and spectral evidence diversity.
15. COLLECTIVE INFERENCE V9 — finite-dimensional Gaussian parameter beliefs, Monte-Carlo EVPI/EVSI, bounded multistage finite-belief policies, cross-fitted AIPW, specification robustness, uncertainty-preserving partial graphs and explicit evidence-dependence probability models.
16. Runtime — hydrate, conditional writes, telemetry, sessions, finalization and exact emission verification.

## Objective hierarchy

Base: `J = w_O·O - w_C·C`.

Organization: `RGO = mean(O)/(1+mean(C))`.

V4 experiment selection: `UCB = mean + alpha * uncertainty`.

V5 information: `EIG = H(prior)-E[H(posterior)]`.

V7 dual-control proxy: `Q = control + lambda_I*information - lambda_R*risk`.

V8 finite decision value:

`EU(a)=sum_i p_i U(a,M_i)`

`EVI(e)=E_y[max_a EU(a|y,e)]-max_a EU(a)`.

V9 continuous decision value under `theta~N(mu,Sigma)`:

`EVPI ~= E_theta[max_a U(a,theta)] - max_a U(a,E[theta])`

and for measurement design `e`

`EVSI(e) ~= E_y[max_a EU(a|y,e)] - max_a EU(a)`.

The progression is:

`uncertainty bonus → entropy information → control+information proxy → finite belief/decision value → continuous parameter belief + sample/perfect-information value`.

## Current developmental metabolism

`HYDRATE`
`→ CHOOSE MINIMUM-SUFFICIENT DEPTH`
`→ MEMORY/ANTIBODY/ELDER/SCIENCE-SHADOW`
`→ REGIME/OOD/PREDICTIVE STATE`
`→ OPTIONAL FINITE OR GAUSSIAN BELIEF`
`→ LIVE HYPOTHESES`
`→ EIG/EVI/EVPI/EVSI DESIGN`
`→ CONDITIONAL CAUSAL IDENTIFICATION`
`→ OPTIONAL EFFECT/AIPW ESTIMATION + ROBUSTNESS`
`→ PARETO/SCHEDULE`
`→ STATE MODEL/SCENARIO/DUAL OR MULTISTAGE BELIEF POLICY`
`→ EXECUTE FIRST AUTHORIZED ACTION`
`→ OBSERVE/METER`
`→ EXPLICIT BELIEF/BAYES/TRANSITION UPDATE`
`→ REPLICATION/FALSIFICATION/EVIDENCE-DEPENDENCE UPDATE`
`→ CREDIT`
`→ MEMORY/IMMUNE/ELDER`
`→ JSPACE/TOPOLOGY/PROJECTION/COMPENSATION`
`→ LIFECYCLE`
`→ FINALIZE/VERIFY/CONDITIONAL COMMIT`
`→ REPLAN`.

## Authority planes

- canonical semantic state: expected VID / semantic event head;
- Git state: expected Git HEAD;
- topology: expected topology version;
- learned policy: expected policy version;
- projection/compensation: explicit saga/semantic-head authority;
- V4–V9 predictive, belief, experiment, causal-estimation, scenario, graph-hypothesis and evidence-dependence state: advisory/evidential/control surfaces only.

A higher-resolution posterior or estimator never inherits semantic mutation authority.

## Finite versus continuous belief

V8 stores finite model probabilities `p_i` and updates from complete likelihood witnesses.

V9 stores `theta~N(mu,Sigma)` for a finite-dimensional linear observation model. In natural coordinates `A=Sigma^-1`, `b=A mu`, one observed `y=x^T theta+epsilon` updates

`A'=A+wxx^T/sigma^2`

`b'=b+wxy/sigma^2`.

Only explicit observations update either belief system. Query, EVPI, EVSI and planning operations are read-only.

`BELIEF_POSTERIOR != CANONICAL_TRUTH`.

`GAUSSIAN_LINEAR_POSTERIOR != GENERAL_CONTINUOUS_BAYES`.

## EIG, EVI, EVPI and EVSI

- V5 EIG values entropy reduction.
- V8 EVI values information only when it improves the downstream finite-model decision.
- V9 EVPI estimates the model-conditional upper value of perfect parameter information.
- V9 EVSI estimates the value of a specific noisy linear measurement design.

EVPI/EVSI are Monte Carlo estimates with reported sampling error and fixed seed; they are not exact analytic values or universal values of truth.

## Causal identification versus estimation

V6/V7 graph checks remain identification witnesses under explicit assumptions.

V8 adds narrow BACKDOOR_LINEAR, IV_WALD and FRONTDOOR_LINEAR estimates.

V9 adds cross-fitted AIPW for binary treatment:

`psi=m1(X)-m0(X)+T(Y-m1(X))/e(X)-(1-T)(Y-m0(X))/(1-e(X))`.

Estimate `tau_hat=mean(psi)`; influence-function `SE≈sd(psi)/sqrt(n)`.

AIPW's double-robust interpretation remains conditional on identification, positivity, consistency and nuisance regularity. Explicit latent-confounding risk fails closed.

`AIPW_ESTIMATE != IDENTIFICATION_PROOF`.

V9 leave-one-adjustment robustness measures observed specification sensitivity only; it is not a hidden-confounding bound.

## Structural uncertainty

V7 association skeletons and V8 bootstrap support remain hypothesis surfaces.

V9 expresses stable undirected hypotheses as `X o-o Y`, explicitly preserving unresolved endpoints. `HEURISTIC_PARTIAL_GRAPH` is not an FCI PAG, CPDAG theorem or causal posterior and creates no JSPACE edge.

## Multistage policy boundary

V8 exposes depth-1 contingent policies. V9 exactly recurses over finite caller-declared model/outcome spaces for horizon `H<=3`.

The returned policy tree is `PLAN_ONLY`; no hypothetical posterior becomes history. This remains bounded finite recursion rather than a general POMDP or belief-MDP solver.

## Evidence dependence

V8 metadata similarity matrix `S` yields effective-N and participation-ratio redundancy measures.

V9 optionally applies a caller-declared logistic metadata model to produce pairwise dependence probabilities. The result is conditional on that declared model; missing metadata remains ambiguity/dependence pressure rather than independence.

`DEPENDENCE_PROBABILITY_MODEL != FORMAL_EVIDENCE_INDEPENDENCE`.

## Resource and scheduling boundary

Automatically observable: MCP call count and wall time. Other dimensions remain caller/host observable only when actually available. `UNKNOWN_COST != ZERO_COST`.

V4 immediate allocation, V5 finite-horizon beam scheduling and V6 small-model exact scheduling remain available. V9 does not claim globally certified stochastic scheduling.

## Witness and projection boundaries

V5 witness cells are process-constrained; V6 stronger capsules fail closed without bubblewrap. Neither proves kernel/native-runtime security.

SQLite semantic state and Git remain separate stores. Topology→JSPACE uses recovery sagas; semantic compensation remains distinct from Git rollback.

## Non-negotiable epistemic firewall

- identity != coordinate
- UNKNOWN != N/A
- UNKNOWN_COST != ZERO_COST
- prediction != observation
- posterior/belief != canonical truth
- Gaussian linear posterior != general continuous Bayes
- likelihood/model != observation
- EIG/EVI/EVPI/EVSI design value != evidence
- Monte-Carlo information value != exact analytic value
- experiment design != result
- association/bootstrap/partial graph != causal DAG/PAG truth
- causal estimate/AIPW != identification proof
- robustness perturbation != hidden-confounding bound
- state model != world truth
- scenario/policy tree != observed future/history
- dual/belief-control plan != execution
- multistage finite belief policy != general POMDP
- Pareto frontier != single best action
- evidence effective-rank/dependence model != formal independence
- witness pass != universal proof
- projection saga != atomic distributed transaction
- semantic compensation != Git rollback
- local success != global authority

## Coordinate fibers

`COLLECTIVE=<F,R,N,D,Q,C,O,H,L>`

`COLLECTIVE_LEARNING=<B,P,CF,E,A,MS,L>`

`COLLECTIVE_ECOLOGY=<RG,X,CR,WS,DF,RW,RO,PS,L>`

`COLLECTIVE_SCIENCE=<BY,CAL,ED,IX,DL,TR,SC,WC,RG,PF,CP,L>`

`COLLECTIVE_DISCOVERY=<NL,OOD,EG,CI,HI,TD,MPC,CS,HC,PB,RF,L>`

`COLLECTIVE_DUAL_CONTROL=<UD,PI,CG,SM,SC,DC,CX,RI,RD,L>`

`COLLECTIVE_BELIEF=<BS,EVI,BD,CE,CB,CP,ER,L>`

`COLLECTIVE_INFERENCE=<GB,EVPI,EVSI,MP,AIPW,RB,PG,ED,L>`.
