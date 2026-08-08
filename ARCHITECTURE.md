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
15. Runtime — hydrate, conditional writes, telemetry, sessions, finalization and exact emission verification.

## Objective hierarchy

Base:

`J = w_O·O - w_C·C`.

Organization comparison:

`RGO = mean(O)/(1+mean(C))`.

V4 experiment selection:

`UCB = mean + alpha * uncertainty`.

V5 experiment information:

`EIG = H(prior)-E[H(posterior)]`.

V7 dual-control proxy:

`Q = control + lambda_I*information - lambda_R*risk`.

V8 finite decision value:

`EU(a)=sum_i p_i U(a,M_i)`

`V0=max_a EU(a)`

`EVI(e)=max(0, sum_y P(y|e) max_a EU(a|y,e) - V0)`.

V8 belief-control depth-1 score:

`Q_B(a)=EU_now(a)+gamma E[V_next|a]+lambda_I EIG(a)-lambda_R risk(a)-cost(a)`.

The key progression is:

`uncertainty bonus → entropy information → control+information proxy → explicit finite belief + downstream decision value`.

## Current developmental metabolism

`HYDRATE`
`→ CHOOSE MINIMUM-SUFFICIENT DEPTH`
`→ MEMORY/ANTIBODY/ELDER/SCIENCE-SHADOW`
`→ REGIME/OOD/PREDICTIVE STATE`
`→ OPTIONAL FINITE MODEL BELIEF`
`→ LIVE HYPOTHESES`
`→ EIG OR EVI EXPERIMENT DESIGN`
`→ CONDITIONAL CAUSAL IDENTIFICATION`
`→ OPTIONAL ASSUMPTION-SCOPED EFFECT ESTIMATE`
`→ PARETO/SCHEDULE`
`→ STATE MODEL/SCENARIO/DUAL OR BELIEF-DUAL PLAN`
`→ EXECUTE FIRST AUTHORIZED ACTION`
`→ OBSERVE/METER`
`→ EXPLICIT BELIEF/BAYES/TRANSITION UPDATE`
`→ REPLICATION/FALSIFICATION/EVIDENCE-DIVERSITY UPDATE`
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
- V4–V8 predictive, belief, experiment, causal-estimation, scenario and evidence-diversity state: advisory/evidential/control surfaces only.

A V8 posterior or estimator never inherits semantic mutation authority simply because it is more mathematically sophisticated.

## Belief-state boundary

V8 stores a finite model distribution:

`p_i >= 0`, `sum_i p_i=1`.

An actual declared observation with explicit likelihood witness updates by

`p_i' = p_i L_i / sum_j p_j L_j`.

Planning, EVI, contingent-policy and belief-dual calls are read-only with respect to belief. Only `athena_belief_observe` mutates the belief distribution.

`BELIEF_POSTERIOR != CANONICAL_TRUTH`.

`LIKELIHOOD_MODEL != OBSERVATION`.

## EIG versus EVI

V5 EIG values entropy reduction in the supplied hypothesis model.

V8 EVI values information according to whether it changes the optimal downstream decision:

`EVI=E[max_a EU(a|new evidence)]-max_a EU(a|current evidence)`.

Thus a high-information experiment may have near-zero EVI when every possible result implies the same action.

`EVI_DESIGN != RESULT`.

## Causal identification versus estimation

V6/V7 identification checks remain assumption/graph witnesses.

V8 estimation adds narrow numeric estimators:

- BACKDOOR_LINEAR: treatment coefficient after supplied adjustment;
- IV_WALD: covariance ratio with weak-first-stage rejection;
- FRONTDOOR_LINEAR: product-of-coefficients mediation proxy.

Identification and estimation remain distinct:

`IDENTIFICATION != ESTIMATION`.

`CAUSAL_ESTIMATE != IDENTIFICATION_PROOF`.

Explicit latent-confounding risk fails closed.

## Bootstrap graph boundary

V7 generates an observational association skeleton/v-structure candidate surface.

V8 bootstrap repeatedly resamples observations and recomputes that heuristic. Support

`support(e)=count(e present)/B`

is a stability score for the procedure, not a causal edge posterior or PAG theorem. No bootstrap call creates JSPACE edges.

`BOOTSTRAP_STABILITY != CAUSAL_EDGE_PROBABILITY`.

## Contingent-policy boundary

For one finite experiment V8 can construct

`outcome → hypothetical posterior → best action`.

That is a depth-1 policy design. It is not an executed branch, observation or historical fact.

`CONTINGENT_POLICY != EXECUTION_HISTORY`.

## Evidence spectral boundary

Witness metadata induces similarity matrix `S`. V8 reports

`N_eff=(sum_i w_i)^2 / sum_ij w_i w_j S_ij`

and participation-ratio proxy

`D_PR=Tr(S)^2 / ||S||_F^2`.

This measures redundancy/effective evidence dimension. It does not prove formal statistical independence.

`SPECTRAL_EVIDENCE_DIVERSITY != FORMAL_INDEPENDENCE`.

## Resource and scheduling boundary

Automatically observable: MCP call count and wall time. Other dimensions remain caller/host observable only when actually available.

`UNKNOWN_COST != ZERO_COST`.

V4 provides immediate allocation, V5 finite-horizon beam scheduling, V6 small-model exact enumeration certificates. A certificate is scoped to its declared model and constraints.

## Witness boundary

V5 witness cells are process-constrained but non-hermetic. V6 stronger capsules require bubblewrap and fail closed when unavailable. Neither gives a theorem about kernel/native-runtime security.

## Projection boundary

SQLite semantic state and Git remain separate stores. Topology→JSPACE uses explicit saga states. V5 compensation is a narrow event-sourced semantic inverse for active projection-owned edges; Git recovery remains separate.

## Non-negotiable epistemic firewall

- identity != coordinate
- UNKNOWN != N/A
- UNKNOWN_COST != ZERO_COST
- prediction != observation
- posterior/belief != canonical truth
- likelihood model != observation
- calibration != model validity
- EIG/EVI != evidence
- experiment design != result
- association skeleton != causal DAG
- bootstrap stability != causal edge probability
- back-door/front-door/instrument ID != graph-independent causal truth
- causal estimate != identification proof
- missing factorial cell != zero effect
- state model != world truth
- scenario tree != observed future
- dual/belief-control plan != execution
- bounded dual control != exact Bayes-adaptive POMDP
- contingent policy != execution history
- Pareto frontier != single best action
- evidence effective-rank != formal independence
- replication design != replication result
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

`COLLECTIVE_BELIEF=<BS,EVI,BD,CE,CB,CP,ER,L>`.
