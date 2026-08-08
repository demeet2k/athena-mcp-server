# ATHENA Canonical MCP v2.7 — Polycoordinate Crystal + Finite Belief-State Decision Runtime

ATHENA's executable Git/MCP nervous substrate combines canonical identity/versioning, typed JSPACE, SCALE, KC144/polycoordinates, exact visible-output crystallization, collective organization/memory/learning, causal experimental science, active discovery, stochastic/dual control, and V8 finite belief-state decision machinery.

## Runtime cycle

`HYDRATE → CHOOSE MINIMUM-SUFFICIENT DEPTH → MEMORY/SCIENCE-SHADOW → REGIME/OOD → PREDICT/CALIBRATE → OPTIONAL FINITE BELIEF → LIVE HYPOTHESES → EIG OR DECISION-EVI EXPERIMENT DESIGN → CONDITIONAL CAUSAL IDENTIFICATION → OPTIONAL CAUSAL EFFECT ESTIMATE → PARETO/SCHEDULE → STATE MODEL/SCENARIO/DUAL OR BELIEF-DUAL PLAN → EXECUTE FIRST AUTHORIZED ACTION → OBSERVE/METER → EXPLICIT BELIEF/MODEL UPDATE → REPLICATE/FALSIFY → CREDIT → MEMORY/IMMUNE/ELDER → JSPACE/TOPOLOGY/PROJECTION/COMPENSATION → LIFECYCLE → FINALIZE/VERIFY → CONDITIONAL COMMIT → REPLAN/REATTACK`.

## Authority

- semantic state: expected-VID / semantic-head CAS;
- Git state: expected Git-head CAS;
- collective topology: expected topology version;
- learned V3 policy: expected policy version;
- topology→JSPACE remains a recovery saga, not a fictional cross-store transaction;
- V5 semantic compensation retracts only active projection-owned semantic effects and never implies Git rollback;
- V4–V8 statistical, belief, causal-estimation, scenario, experiment-design and replication state is evidential/control state and has no independent semantic-mutation authority.

`SID != OID != MID != VID != CID != EID != CRYS != ENV`.

## Exact visible output

`athena_finalize_output` crystallizes the exact visible body, derives its header, assembles `HEADER+BODY`, creates an emission manifestation and indexes visible lexemes. `athena_verify_emission` recomputes the exact visible-byte digest.

`LOOKUP != DERIVATION`; coordinate lists are navigation, not identity.

---

## V1–V4 — organization → memory → bounded experimental ecology

- **V1:** HIVE/SWARM/PACK/FLOCK/HERD/POD, dynamic width, roles, reserve, sparse topology, quorum/inhibition, homeostasis.
- **Growth:** demand allocation, bridge economics, FISSION/FUSE/HOLD, dependency alarms, lineage-preserving lifecycle.
- **V2:** persistent pheromones, typed JSPACE invalidation, RGO calibration, topology CAS/rollback, failure antibodies.
- **V3:** observed budgets, bounded rollbackable learned policy, counterfactuals, elder authority, antibody evolution, multiscale pheromones.
- **V4:** contextual UCB, causal-confidence credit/residual, worker-cost scheduling, learned diffusion, executable regressions, explicit-transition rollouts and topology→JSPACE sagas.

Resources:

`athena://collective/runtime`, `athena://collective/growth`, `athena://collective/v2`, `athena://collective/v3`, `athena://collective/v4`.

Core laws: `MAX_GROWTH != MAX_ACTIVITY`; `MAX_INTEGRATION != MAX_CONNECTIVITY`; `UCB != TRUTH`; `UNKNOWN_COST != ZERO_COST`; `PROJECTION_SAGA != ATOMIC_TRANSACTION`.

## V5 — causal experimental operating system

Full-covariance Bayesian context state, retained pre-update interval calibration, expected-information-gain experiment ranking, factorial/delayed credit, learned transition summaries, multi-period beam scheduling, process-constrained witness cells, learned regimes, Pareto frontiers and narrow semantic compensation.

Resource: `athena://collective/v5`  
Spec: `spec/COLLECTIVE_RUNTIME_V5.md`

`POSTERIOR != TRUTH`; `EIG != EVIDENCE`; `DESIGN != RESULT`; `INTERACTION != CAUSATION WITHOUT IDENTIFICATION`; `TRANSITION_MODEL != WORLD`; `PARETO_FRONTIER != SINGLE_BEST`.

## V6 — active discovery + stochastic control

Degree-2 nonlinear Bayesian lift, empirical OOD geometry, finite factor-space experiment generation, supplied-DAG back-door identification, order-2..4 factorial contrasts, multivariate transition covariance, receding-horizon MPC, exact small-model schedule certification, fail-closed bubblewrap witness capsules, interval-Pareto experiment selection and science-shadow replication/falsification claims.

Resource: `athena://collective/v6`  
Spec: `spec/COLLECTIVE_RUNTIME_V6.md`

`NONLINEAR_BASIS != UNIVERSAL_INFERENCE`; `OOD != FALSEHOOD`; `GENERATED_EXPERIMENT != RESULT`; `MPC_PLAN != EXECUTION`; `REPLICATION_STATE != CANON`.

## V7 — dual control + conditional causal discovery

V7 adds uncertainty-source diagnostics, empirical prequential bands, a bounded observational association-skeleton/v-structure hypothesis generator, state-dependent ridge transition models, three-branch moment scenario/CVaR evaluation, a bounded control+information proxy, supplied-DAG BACKDOOR/FRONTDOOR/INSTRUMENT checks, and metadata-based replication-independence/design surfaces.

Resource: `athena://collective/v7`  
Spec: `spec/COLLECTIVE_RUNTIME_V7.md`

Coordinate:

`COLLECTIVE_DUAL_CONTROL=<UD,PI,CG,SM,SC,DC,CX,RI,RD,L>`.

Key laws:

- `UNCERTAINTY_DECOMPOSITION != UNIQUE_PHYSICAL_TRUTH`
- `PREQUENTIAL_BAND != DISTRIBUTION_FREE_ARBITRARY-SHIFT GUARANTEE`
- `ASSOCIATION_SKELETON != CAUSAL_DAG`
- `STATE_DEPENDENT_TRANSITION_MODEL != WORLD_TRUTH`
- `SCENARIO_TREE != OBSERVED_FUTURE`
- `DUAL_CONTROL_PROXY != EXACT_BAYES_ADAPTIVE_CONTROL`
- `FRONTDOOR/IV IDENTIFICATION != CAUSAL TRUTH OUTSIDE SUPPLIED DAG/ASSUMPTIONS`
- `ESTIMATED_REPLICATION_INDEPENDENCE != FORMAL INDEPENDENCE`.

---

# V8 — Finite Belief State + Decision Value

V8 attacks the next tractable residual: instead of valuing uncertainty only through a parameter-information proxy, the runtime can maintain an explicit finite distribution over competing models and value information by how much it improves the downstream decision.

Resource: `athena://collective/v8`  
Spec: `spec/COLLECTIVE_RUNTIME_V8.md`

## ΩBELIEF

Tools:

- `athena_belief_register`
- `athena_belief_state`
- `athena_belief_observe`

For models `M_i` with probabilities `p_i`, an explicit observed outcome with caller-supplied likelihood witness `L_i=P(y|M_i)` produces

`p_i' = p_i L_i / Σ_j p_j L_j`.

Likelihood is required for every model. Design/planning operations never mutate belief automatically.

`BELIEF_POSTERIOR != CANONICAL_TRUTH` and `LIKELIHOOD_MODEL != OBSERVATION`.

## ΩEVI — decision-theoretic value of information

Tool:

- `athena_decision_evi`

For action utilities `U(a,M_i)`:

`EU(a)=Σ_i p_i U(a,M_i)`

and

`V0=max_a EU(a)`.

For experiment `e` with finite outcomes:

`V(e)=Σ_y P(y|e) max_a EU(a|y,e)`

and

`EVI(e)=max(0,V(e)-V0)`.

This differs from entropy-only EIG: information receives value only if it can improve the supplied downstream decision. Ethics remains a hard gate; cost/risk/feasibility remain explicit. Result is `DESIGN_ONLY`.

`EVI_DESIGN != EXPERIMENT_RESULT`.

## ΩBELIEF-DUAL

Tool:

- `athena_belief_dual_control`

A bounded depth-1 finite-belief controller combines immediate expected utility, expected best next-decision utility, information gain, risk and cost:

`Q(a)=EU_now(a)+γ E[V_next|a]+λ_I EIG(a)-λ_R Risk(a)-Cost(a)`.

Result is `BELIEF_DUAL_CONTROL_DEPTH1_PLAN_ONLY`.

It executes nothing and does not update belief.

`BELIEF_DUAL_CONTROL != EXACT_BAYES_ADAPTIVE_POMDP`.

## ΩCAUSAL-EFFECT

Tool:

- `athena_causal_effect_estimate`

Implemented assumption-scoped estimators:

- `BACKDOOR_LINEAR`: treatment coefficient in `Y=β0+τT+γᵀZ+ε`;
- `IV_WALD`: `τ=Cov(Z,Y)/Cov(Z,T)` with weak-first-stage rejection;
- `FRONTDOOR_LINEAR`: linear mediation proxy `α_(T→M) β_(M→Y|T)`.

These estimate only under the declared model/assumption surface. They do not replace V6/V7 identification checks or establish the causal graph. Explicit latent-confounding risk fails closed.

`CAUSAL_ESTIMATE != IDENTIFICATION_PROOF`.

## ΩBOOTSTRAP-GRAPH

Tool:

- `athena_causal_structure_bootstrap`

The runtime repeatedly resamples observations and reruns V7's transparent association-skeleton procedure. Edge support is

`support(e)=#bootstrap runs containing e / B`.

Stable undirected edges and collider candidates are returned as graph hypotheses. No canonical JSPACE edge is created.

`BOOTSTRAP_ASSOCIATION_STABILITY != CAUSAL_EDGE_PROBABILITY`.

## ΩCONTINGENT-POLICY

Tool:

- `athena_contingent_policy`

For one experiment, V8 returns a depth-1 policy tree:

`outcome → hypothetical posterior → best action`.

Status: `CONTINGENT_POLICY_DEPTH1_DESIGN_ONLY`.

No branch becomes observation or history until measured.

## ΩEVIDENCE-SPECTRAL

Tool:

- `athena_evidence_spectral`

Science-shadow witness similarity matrix `S` yields weighted effective count

`N_eff=(Σ_i w_i)^2 / Σ_ij w_i w_j S_ij`

and spectral participation-ratio proxy

`D_PR=Tr(S)^2 / ||S||_F^2`.

Identical witness pipelines collapse toward one effective dimension; diverse metadata can increase effective evidence dimension. Missing comparable metadata is treated conservatively.

`SPECTRAL_EVIDENCE_DIVERSITY != FORMAL_STATISTICAL_INDEPENDENCE`.

## V8 coordinate

`COLLECTIVE_BELIEF=<BS,EVI,BD,CE,CB,CP,ER,L>`

- `BS`: finite belief state
- `EVI`: decision-value-of-information surface
- `BD`: belief-aware dual-control plan
- `CE`: conditional effect estimate
- `CB`: bootstrap causal-structure stability
- `CP`: contingent policy design
- `ER`: evidence redundancy/effective-rank geometry
- `L`: lineage/native context

## V8 firewall

- `BELIEF_POSTERIOR != CANONICAL_TRUTH`
- `LIKELIHOOD_MODEL != OBSERVATION`
- `EVI_DESIGN != RESULT`
- `BELIEF_DUAL_CONTROL != EXACT_BAYES_ADAPTIVE_POMDP`
- `CAUSAL_ESTIMATE != IDENTIFICATION_PROOF`
- `BOOTSTRAP_STABILITY != CAUSAL_EDGE_PROBABILITY`
- `CONTINGENT_POLICY != EXECUTION_HISTORY`
- `SPECTRAL_EVIDENCE_DIVERSITY != FORMAL_INDEPENDENCE`

## Run

`python -m athena_mcp --db ./state/athena.db`

MCP server package: `athena-canonical-mcp 2.7.0`  
MCP protocol revision: `2025-11-25`.
