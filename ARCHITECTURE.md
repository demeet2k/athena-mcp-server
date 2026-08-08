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
16. COLLECTIVE PROBABILISTIC V10 — fixed-kernel exact GP regression, bounded Gaussian PC-stable discovery, binary TMLE, E-value sensitivity, exact bounded finite-POMDP policies and empirically calibrated evidence-dependence models.
17. Runtime — hydrate, conditional writes, telemetry, sessions, finalization and exact emission verification.

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

`EVSI(e) ~= E_y[max_a EU(a|y,e)] - max_a EU(a)`.

V10 nonlinear predictive and exact finite-control surfaces add:

`mu_GP(x*)=k_*^T(K+sigma_n^2 I)^-1 y`

`var_GP(f*)=k(x*,x*)-k_*^T(K+sigma_n^2 I)^-1 k_*`

and, for a fully declared finite POMDP,

`V_H(b)=max_a [R(b,a)+gamma sum_o P(o|b,a)V_(H-1)(tau(b,a,o))]`.

The progression is:

`uncertainty bonus → entropy information → control+information proxy → finite belief/decision value → continuous parameter belief → nonlinear probabilistic prediction + certified bounded belief control`.

## Current developmental metabolism

`HYDRATE`
`→ CHOOSE MINIMUM-SUFFICIENT DEPTH`
`→ MEMORY/ANTIBODY/ELDER/SCIENCE-SHADOW`
`→ REGIME/OOD/PREDICTIVE STATE`
`→ OPTIONAL FINITE/GAUSSIAN/GP MODEL`
`→ LIVE HYPOTHESES`
`→ EIG/EVI/EVPI/EVSI DESIGN`
`→ CONDITIONAL CAUSAL IDENTIFICATION`
`→ OPTIONAL LINEAR/AIPW/TMLE ESTIMATION + SENSITIVITY`
`→ OPTIONAL ASSOCIATION/PC STRUCTURE HYPOTHESIS`
`→ PARETO/SCHEDULE`
`→ STATE MODEL/SCENARIO/DUAL/BELIEF/POMDP PLAN`
`→ EXECUTE FIRST AUTHORIZED ACTION`
`→ OBSERVE/METER`
`→ EXPLICIT BELIEF/BAYES/GP/TRANSITION UPDATE`
`→ REPLICATION/FALSIFICATION/EVIDENCE-DEPENDENCE CALIBRATION`
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
- V4–V10 predictive, belief, GP, experiment, causal-estimation, scenario, graph-hypothesis and evidence-dependence state: advisory/evidential/control surfaces only.

A higher-resolution posterior, estimator, graph algorithm or certified finite control computation never inherits semantic mutation authority.

## Belief / probabilistic model ladder

V8 stores a finite categorical model distribution.

V9 stores a finite-dimensional Gaussian linear parameter posterior.

V10 stores a scoped exact small-data GP posterior for a **fixed declared RBF kernel** and bounded observations.

These are different model families; none silently migrates into another.

Only explicit observations update belief/GP state. Prediction, EVSI and control calls remain read-only.

`BELIEF_POSTERIOR != CANONICAL_TRUTH`.

`GAUSSIAN_LINEAR_POSTERIOR != GENERAL_CONTINUOUS_BAYES`.

`FIXED_KERNEL_GP != GENERAL_WORLD_TRUTH`.

## GP boundary

For RBF kernel

`k(x,z)=sigma_f^2 exp(-||x-z||^2/(2l^2))`,

V10 performs exact matrix GP regression over at most 128 stored rows. Hyperparameters are not automatically learned. Posterior variance is conditional on the kernel/noise model.

`GP_POSTERIOR != OBSERVATION`.

## Causal structure ladder

V7 association skeleton: transparent heuristic hypothesis generation.

V8 bootstrap: resampling stability for that heuristic.

V9 partial graph: stable `o-o` endpoint uncertainty.

V10 bounded Gaussian PC-stable: explicit Fisher-z conditional-independence search, separation sets, collider orientation and bounded Meek R1/R2 closure.

The V10 graph is still relative to Gaussian/linear CI assumptions and bounded conditioning depth.

`BOUNDED_PC_STABLE != FCI_OR_HIDDEN_CONFOUNDER_DISCOVERY`.

No discovery layer writes canonical JSPACE edges without a separate authority path.

## Causal estimation ladder

V8 provides transparent linear/Wald/mediation estimates.

V9 adds cross-fitted AIPW with influence-function SE.

V10 adds binary-treatment/binary-outcome TMLE with logistic nuisance fits, propensity clipping, a one-dimensional targeting fluctuation and an influence-curve interval.

Every estimator remains conditional on causal identification/positivity/consistency/model regularity.

`TMLE_ESTIMATE != IDENTIFICATION_PROOF`.

V10 additionally exposes the standard risk-ratio E-value sensitivity metric. It is a scoped unmeasured-confounding strength metric, not a universal sensitivity bound.

## Finite belief-control certificate

V9 recurses over finite model/outcome policy trees with `H<=3`.

V10's POMDP surface additionally models hidden-state transitions and observation emissions. For at most 8 states/actions and horizon `H<=4`, exhaustive recursion yields:

`FINITE_POMDP_EXACT_HORIZON_CERTIFIED`

only if every explored action/observation branch completes before the node limit.

The certificate is exactly:

`EXACT_FOR_SUPPLIED_FINITE_MODEL_AND_HORIZON`.

It does not certify omitted real-world dynamics or infinite-horizon optimality.

## Evidence dependence calibration

V8/V9 provide metadata similarity/effective-rank and caller-declared logistic dependence surfaces.

V10 can fit a scoped logistic dependence model only from externally labelled pair examples. Predictions never generate labels. Training loss/accuracy are evidence about fit to that calibration population, not a formal independence theorem.

## Resource, witness and projection boundaries

`UNKNOWN_COST != ZERO_COST`.

V4 immediate allocation, V5 finite-horizon beam scheduling and V6 small-model exact scheduling remain available. V10 does not claim globally certified stochastic resource scheduling.

V5 witness cells are process-constrained; V6 stronger capsules fail closed without bubblewrap. Neither proves kernel/native-runtime security.

SQLite semantic state and Git remain separate stores. Topology→JSPACE uses recovery sagas; semantic compensation remains distinct from Git rollback.

## Non-negotiable epistemic firewall

- identity != coordinate
- UNKNOWN != N/A
- UNKNOWN_COST != ZERO_COST
- prediction != observation
- posterior/belief != canonical truth
- GP posterior != observation/world truth
- Gaussian linear posterior != general continuous Bayes
- EIG/EVI/EVPI/EVSI != evidence
- experiment design != result
- association/bootstrap/partial/PC graph != unrestricted causal truth
- bounded PC-stable != FCI/hidden-confounder discovery
- causal estimate/AIPW/TMLE != identification proof
- E-value != universal hidden-confounding bound
- state model != world truth
- scenario/policy tree != observed future/history
- finite POMDP certificate != infinite-horizon/real-world optimum
- Pareto frontier != single best action
- evidence dependence model != formal independence
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

`COLLECTIVE_INFERENCE=<GB,EVPI,EVSI,MP,AIPW,RB,PG,ED,L>`

`COLLECTIVE_PROBABILISTIC=<GP,PC,TM,SV,PM,ED,L>`.
