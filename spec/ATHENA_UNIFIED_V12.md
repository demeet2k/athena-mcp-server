# ATHENA UNIFIED V12 — AΩR × COLLECTIVE JOINT STRUCTURAL WORLD-MODEL RUNTIME

Package: `athena-canonical-mcp 3.1.0`

Live architecture artifact: `ATHENA.RUNTIME.UNIFIED.7`

Runtime root: one composed `Server`.

## 1. Constitutional braid

`AOR = WHAT is developmentally eligible`

`COLLECTIVE V1–V12 = HOW scarce execution / science / inference / control / model-uncertainty capacity is organized`

`Y1 = canonical claim authority`

`EQ1 = witnessed equivalence collapse`

`OMEGA = current accessible whole-state projection`

`PROMOTION = exact-head local predicates + external CI/smoke attestations`.

Canonical authority RPCs remain `athena_claim_*`.

Collective science-shadow replication/falsification remains `athena_discovery_claim_*`.

`athena_claim_* != athena_discovery_claim_*`.

V12 model posterior, graph candidate, causal-policy estimate, EVSI and optimization output has no implicit Y1 mutation path.

## 2. Unified ladder

`V1 organization`
`→ V2 memory`
`→ V3 empirical policy adaptation`
`→ V4 experimental ecology`
`→ V5 causal science`
`→ V6 active discovery`
`→ V7 dual control`
`→ V8 finite belief`
`→ V9 Gaussian-linear inference`
`→ V10 nonlinear probabilistic world model`
`→ V11 adaptive model components`
`→ V12 joint structural world-model uncertainty`.

V12 is lazy and instantiated only on tool/resource access.

## 3. V12 executable organs

- `athena_gp_hyperposterior`
- `athena_gp_bma_predict`
- `athena_gp_sparse_predict`
- `athena_gp_bma_decision_evsi`
- `athena_pag_candidate_discover`
- `athena_longitudinal_gformula`
- `athena_chance_resource_select`.

Resource:

`athena://collective/v12`.

Coordinate:

`COLLECTIVE_JOINT=<HP,BM,SG,PG,LC,JV,CC,L>`.

## 4. Joint GP model uncertainty

V11 can select/apply one finite-grid RBF hyperparameter winner under observed-row CAS.

V12 can instead preserve the whole supplied finite-grid posterior:

`w_i ∝ p(theta_i) exp(log p(y|X,theta_i))`.

`FINITE_GRID_HYPERPOSTERIOR != CONTINUOUS_HYPERPARAMETER_BAYES`.

BMA prediction uses

`E[Y|D]=sum_i w_i mu_i`

and

`Var(Y|D)=sum_i w_i v_i + sum_i w_i(mu_i-E[Y])^2`.

The between-model term is not discarded merely because one candidate has the largest marginal likelihood.

`BMA_GP_POSTERIOR != WORLD_TRUTH`.

## 5. Approximation surface

`athena_gp_sparse_predict` uses deterministic farthest-point subset selection over observed rows and compares the subset posterior to the exact bounded current GP prediction.

Its returned error is an observed approximation error for that query relative to the current bounded GP, not a theorem about future queries.

`SUBSET_GP_APPROXIMATION != FULL_GP_POSTERIOR`.

It is not sparse variational GP or inducing-point optimality.

## 6. Joint decision value

`athena_gp_bma_decision_evsi` values a candidate measurement while preserving kernel uncertainty. Hypothetical observations update finite model weights and within-model GP action means only inside the simulation tree.

`BMA_GP_EVSI != OBSERVATION`.

No EVSI call appends GP observations, changes GP hyperparameters, creates Y1 evidence, or mutates canonical semantics.

## 7. Structural uncertainty

V12 `athena_pag_candidate_discover` creates circle/arrow/tail endpoint candidates from bounded Gaussian CI search, separation sets, unshielded-collider logic and limited conservative propagation.

It explicitly lacks full FCI/RFCI possible-d-sep search and complete PAG orientation semantics.

`BOUNDED_PAG_CANDIDATE != FCI_RFCI_PAG_THEOREM`.

`PAG_CANDIDATE != CANONICAL_JSPACE_GRAPH`.

The pre-existing V11 supplied-DAG ADMG projection remains a distinct model-transform operator and is not silently combined with observational PAG candidates into stronger causal truth.

## 8. Longitudinal causal-policy estimate

`athena_longitudinal_gformula` implements a two-timepoint static-regime parametric g-formula for binary `A1`, binary intermediate `L1`, binary `A2`, and binary `Y`, with optional numeric baseline covariates.

For regime `(a1,a2)`:

`Risk(a1,a2)=E_X[(1-p_L)Q(X,a1,0,a2)+p_L Q(X,a1,1,a2)]`.

Declared latent-confounding risk fails closed.

`TWO_TIMEPOINT_GFORMULA != LONGITUDINAL_TMLE_OR_IDENTIFICATION_PROOF`.

No regime ranking is execution authorization.

## 9. Chance-constrained resource control

For candidate resource consumption approximated independently as Gaussian, V12 enforces one-sided bounds

`mu_r(S)+z_(1-alpha)sigma_r(S) <= budget_r`.

For small candidate sets it exhaustively enumerates all subsets and certifies only:

`EXACT_ENUMERATION_UNDER_DECLARED_INDEPENDENT_GAUSSIAN_RESOURCE_MODEL`.

Above the exact threshold it uses a deterministic greedy fallback with **no optimality certificate**.

`GAUSSIAN_INDEPENDENT_CHANCE_CERTIFICATE != DISTRIBUTION_FREE_RESOURCE_GUARANTEE`.

`OPTIMIZATION_PLAN != EXECUTION`.

## 10. No self-training / no semantic laundering

Forbidden transitions include:

`BMA prediction -> GP observation`

`BMA EVSI simulated measurement -> GP observation`

`PAG candidate -> JSPACE edge`

`g-formula estimate -> causal identification`

`chance plan -> resource execution`

`model/science-shadow result -> Y1 authority`.

General law:

`MODEL_OUTPUT --X--> OBSERVATION_OR_AUTHORITY_WITHOUT_EXTERNAL_WITNESS`.

## 11. State and transaction domains

V12 adds no new canonical transaction domain.

Existing independent authority/CAS planes remain:

`CAS_semantic(VID) × CAS_git(HEAD) × CAS_topology(version)`.

V11 GP observed-row CAS remains local model-state protection.

V12 finite hyperposteriors, BMA predictions, structural candidates, causal-policy estimates and resource plans are read-only/model-state computations and do not collapse these domains.

## 12. Live architecture and SURFACE.2

`ATHENA.RUNTIME.UNIFIED.7` advertises `COLLECTIVE_JOINT_V12`, preserves compatibility with `.1` through `.6`, and includes V12 invariants/unresolved boundaries.

SURFACE.2 requires the seven V12 tools and `athena://collective/v12` resource. Deleting V12 from discovery therefore fails local promotion readiness rather than appearing as harmless extra-surface drift.

COMPOSITION.2 continues to verify one composed `Server`; V12 is explicitly lazy rather than falsely represented as a resident duplicate runtime.

## 13. MAXDEV V12

The runtime must choose the shallowest sufficient layer.

Use V12 only when at least one of the following materially changes the action:

- preserving finite GP kernel uncertainty rather than choosing one kernel;
- decomposing within-model vs between-model nonlinear predictive variance;
- measuring bounded subset-GP approximation error;
- valuing a GP measurement while retaining kernel uncertainty;
- preserving circle/arrow/tail structural uncertainty;
- comparing two-timepoint causal treatment regimes;
- planning under explicit Gaussian resource-consumption uncertainty.

Higher numeric sophistication never grants higher semantic authority.

## 14. CI / promotion contract

Release gate:

`syntax ∧ full-unit-suite ∧ critical-invariants ∧ dependent-smoke`.

The critical-invariant job names V12 explicitly and runs constructive, adversarial and unified authority tests.

Repository documentation consistency is itself a critical invariant.

`CI_PASS != LIVE_PROMRUN`.

A green Actions run proves the exact tested Git head passed the configured workflow; it does not fabricate a runtime PROMRUN record and does not prove real-world model correctness.

Final canonical promotion requires the exact master head, not merely the feature-branch head, to pass all gates after merge.

## 15. External control-plane boundary

GitHub branch protection, repository settings/description, tags, Releases, PR state and merge state are **external control-plane state**. They must be read or changed with GitHub control-plane capabilities.

`RUNTIME_CI != GITHUB_CONTROL_PLANE_STATE`.

No runtime resource, OMEGA snapshot, SELFTEST or PROMOTION predicate may claim an external setting was changed without an actual control-plane witness.

## 16. Residual frontier

`UNRESOLVED_EXTERNAL_CONTROL_PLANE` remains a valid state when required GitHub control-plane capabilities are unavailable.

Technical V13 residuals include continuous GP hyperparameter Bayes, scalable sparse/variational GP inference, full FCI/RFCI, calibrated PAG uncertainty, longitudinal TMLE/dynamic regimes, general off-policy causal policy value, joint long-horizon GP/POMDP experimental design, correlated/distributionally robust chance constraints, and dynamic stochastic resource control.
