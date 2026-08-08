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
17. COLLECTIVE ADAPTIVE V11 — marginal-likelihood GP adaptation, GP decision EVSI, supplied latent-DAG projection, validation-weighted stacked TMLE, two-dimensional RR bias-factor sensitivity, exact finite-model Bayes-adaptive POMDP and Laplace evidence-dependence uncertainty.
18. Runtime — hydrate, conditional writes, telemetry, sessions, finalization and exact emission verification.

## Objective hierarchy

Base: `J = w_O·O - w_C·C`.

Organization: `RGO = mean(O)/(1+mean(C))`.

V4 experiment selection: `UCB = mean + alpha * uncertainty`.

V5 information: `EIG = H(prior)-E[H(posterior)]`.

V7 dual-control proxy: `Q = control + lambda_I*information - lambda_R*risk`.

V8 finite decision value:

`EVI(e)=E_y[max_a EU(a|y,e)]-max_a EU(a)`.

V9 continuous linear decision value:

`EVPI ~= E_theta[max_a U(a,theta)]-max_a U(a,Etheta)`

`EVSI(e) ~= E_y[max_a EU(a|y,e)]-max_a EU(a)`.

V10 adds nonlinear fixed-kernel prediction and exact finite-POMDP recursion:

`mu_GP(x*)=k_*^T(K+sigma_n^2 I)^-1 y`

`V_H(b)=max_a[R(b,a)+gamma sum_o P(o|b,a)V_(H-1)(tau(b,a,o))]`.

V11 makes selected model assumptions adaptive and decision-valued:

`theta_K^* = argmax_theta log p(y|X,theta)` over a declared finite grid,

`EVSI_GP(e) ~= E_y[max_a U_a(mu'_a|y,e)]-max_a U_a(mu_a)`,

and augments hidden state to `(M,S)` for a bounded finite-model Bayes-adaptive POMDP.

Progression:

`organization → memory → learning → exploration → experiment science → discovery → dual control → explicit belief → continuous inference → probabilistic world model → adaptive model/control`.

## Current developmental metabolism

`HYDRATE`
`→ CHOOSE MINIMUM-SUFFICIENT DEPTH`
`→ MEMORY/ANTIBODY/ELDER/SCIENCE-SHADOW`
`→ REGIME/OOD/PREDICTIVE STATE`
`→ OPTIONAL FINITE/GAUSSIAN/GP MODEL`
`→ OPTIONAL CAS-GUARDED MODEL ADAPTATION`
`→ LIVE HYPOTHESES`
`→ EIG/EVI/EVPI/EVSI/GP-EVSI DESIGN`
`→ CONDITIONAL CAUSAL IDENTIFICATION`
`→ OPTIONAL LINEAR/AIPW/TMLE/STACKED-TMLE ESTIMATION`
`→ SENSITIVITY + STRUCTURAL/LATENT GEOMETRY`
`→ PARETO/SCHEDULE`
`→ STATE MODEL/SCENARIO/DUAL/BELIEF/POMDP/BA-POMDP PLAN`
`→ EXECUTE FIRST AUTHORIZED ACTION`
`→ OBSERVE/METER`
`→ EXPLICIT BELIEF/BAYES/GP/TRANSITION UPDATE`
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
- GP V11 hyperparameter application: expected observed-row count;
- projection/compensation: explicit saga/semantic-head authority;
- V4–V11 predictive, belief, GP, experiment, causal-estimation, sensitivity, scenario, graph-hypothesis and evidence-dependence state: advisory/evidential/control surfaces only.

A more adaptive model never inherits semantic mutation authority.

## Probabilistic model ladder

V8: finite categorical model distribution.

V9: finite-dimensional Gaussian linear parameter posterior.

V10: exact small-data GP posterior for fixed declared RBF hyperparameters.

V11: finite-grid marginal-likelihood selection can adapt those GP hyperparameters, but application requires explicit exact observation-count CAS.

No layer silently converts prior model state into a stronger model family. Only explicit observations update data-bearing belief/GP state.

`MARGINAL_LIKELIHOOD_OPTIMUM != TRUE_KERNEL`.

## Decision-information ladder

- EIG: entropy reduction.
- EVI: finite-model downstream decision value.
- EVPI: approximate perfect-information ceiling under a Gaussian linear utility model.
- EVSI: approximate value of a declared Gaussian linear measurement.
- GP-EVSI: value of a candidate nonlinear GP measurement through the joint conditional Gaussian posterior over action and experiment points.

`GP_DECISION_EVSI != OBSERVATION`.

## Causal structure ladder

V7: association skeleton/v-structure hypotheses.

V8: resampling stability.

V9: uncertainty-preserving `o-o` partial graph.

V10: bounded Gaussian PC-stable conditional-independence discovery.

V11: an explicit **supplied** DAG with named latent variables may be projected into an observed ADMG with directed and bidirected edges. This is a model transform, not observational discovery.

`SUPPLIED_DAG_LATENT_PROJECTION != DATA_DISCOVERED_PAG`.

No graph hypothesis/transform silently writes canonical JSPACE.

## Causal-estimation ladder

V8: linear/Wald/mediation estimates.

V9: cross-fitted AIPW.

V10: binary logistic TMLE with single nuisance models.

V11: binary TMLE with a transparent validation-weighted nuisance library of simple, linear and degree-2 logistic candidates.

The V11 ensemble is deliberately bounded rather than marketed as a universal Super Learner. Identification remains separate, positivity remains explicit and declared latent-confounding risk fails closed.

`STACKED_TMLE != SUPER_LEARNER_THEOREM`.

## Sensitivity ladder

V9: leave-one-adjustment observed-specification perturbation.

V10: standard point E-value.

V11: two-dimensional RR bias-factor surface

`BF=RR_EU*RR_UY/(RR_EU+RR_UY-1)`.

This maps explicit hidden-confounding strength assumptions to toward-null adjusted associations. It remains a scoped bounding-factor model.

`RR_BIAS_FACTOR_SURFACE != UNIVERSAL_HIDDEN_CONFOUNDING_BOUND`.

## Belief-control ladder

V8: depth-1 finite model contingent policy.

V9: bounded multistage finite model/outcome policy tree.

V10: exact finite-horizon POMDP for one fully declared known transition/observation model.

V11: exact bounded POMDP over augmented hidden state `(M,S)` where `M` is a static uncertain candidate model and observations update both model and physical-state belief.

Certificate:

`EXACT_FOR_SUPPLIED_STATIC_MODEL_SET_STATE_SPACE_ACTIONS_OBSERVATIONS_AND_HORIZON`.

Exactness is revoked when the node limit truncates the tree.

`FINITE_MODEL_BAPOMDP != GENERAL_BAYES_ADAPTIVE_CONTROL`.

`MODEL_EXACTNESS != MODEL_CORRECTNESS`.

## Evidence-dependence ladder

V8: effective-N / spectral redundancy.

V9: caller-declared logistic dependence probabilities.

V10: logistic dependence model learned from external labelled pairs.

V11: approximate coefficient/query uncertainty from the regularized observed-information Hessian, transformed to a probability interval.

`LAPLACE_DEPENDENCE_INTERVAL != CALIBRATED_COVERAGE_GUARANTEE`.

## Resource, witness and projection boundaries

`UNKNOWN_COST != ZERO_COST`.

Scheduling certificates remain scoped to their declared constraints. V11 does not claim globally certified stochastic resource scheduling.

Witness isolation remains explicit and fail-closed at the stronger V6 capsule boundary.

SQLite semantic state and Git remain separate stores. Topology→JSPACE uses recovery sagas; semantic compensation is separate from Git rollback.

## Non-negotiable epistemic firewall

- identity != coordinate
- UNKNOWN != N/A
- UNKNOWN_COST != ZERO_COST
- prediction != observation
- posterior/belief != canonical truth
- model adaptation != evidence
- marginal-likelihood optimum != true kernel
- GP decision EVSI != observed result
- supplied latent projection != data-discovered PAG
- association/bootstrap/PC/ADMG transform != canonical causal truth
- causal estimate/AIPW/TMLE/stacked TMLE != identification proof
- stacked nuisance library != universal Super Learner theorem
- RR sensitivity surface != universal hidden-confounding theorem
- scenario/policy tree != observed history
- finite-model BA-POMDP certificate != general/real-world optimality
- dependence interval != calibrated coverage guarantee
- model exactness != model correctness
- Pareto frontier != single best action
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

`COLLECTIVE_PROBABILISTIC=<GP,PC,TM,SV,PM,ED,L>`

`COLLECTIVE_ADAPTIVE=<GH,GV,LP,SL,SS,BP,EU,L>`.
