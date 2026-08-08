# ATHENA COLLECTIVE RUNTIME V12 — JOINT STRUCTURAL WORLD-MODEL BELIEF

V12 extends V11 adaptive world modeling by preserving uncertainty across **multiple model components at once** instead of collapsing each component to a single local winner. The executable scope is deliberately bounded: finite-grid GP hyperparameter posteriors, Bayesian-model-averaged GP prediction and measurement value, deterministic subset-of-data GP approximation, bounded PAG-like structural candidates, a two-timepoint parametric causal g-formula, and small finite chance-constrained resource selection.

The design objective is **joint model uncertainty without semantic laundering**.

## 0. Constitutional boundaries

`FINITE_GRID_HYPERPOSTERIOR != CONTINUOUS_HYPERPARAMETER_BAYES`

`BMA_GP_POSTERIOR != WORLD_TRUTH`

`SUBSET_GP_APPROXIMATION != FULL_GP_POSTERIOR`

`BOUNDED_PAG_CANDIDATE != FCI_RFCI_PAG_THEOREM`

`TWO_TIMEPOINT_GFORMULA != LONGITUDINAL_TMLE_OR_IDENTIFICATION_PROOF`

`BMA_GP_EVSI != OBSERVATION`

`GAUSSIAN_INDEPENDENT_CHANCE_CERTIFICATE != DISTRIBUTION_FREE_RESOURCE_GUARANTEE`.

All V1–V11 semantic/Git/topology/policy/Y1 authority surfaces remain unchanged.

## 1. ΩHYPERPOSTERIOR — finite-grid GP model belief

Tool:

- `athena_gp_hyperposterior`.

For candidate GP hyperparameters

`theta_i=(ell_i,sigma_f,i^2,sigma_n,i^2)`

with explicit prior mass `p(theta_i)>0`, V12 computes the exact Gaussian GP log marginal likelihood on the currently stored observed rows:

`L_i = -1/2 y^T K_i^-1 y - 1/2 log|K_i| - n/2 log(2pi)`.

Finite-grid posterior weights are

`w_i = p(theta_i) exp(L_i) / sum_j p(theta_j) exp(L_j)`.

The result reports entropy and effective model count

`N_eff = 1 / sum_i w_i^2`.

The posterior is exact only over the supplied finite candidate grid and prior; it is not a continuous posterior over kernel parameters.

## 2. ΩBMA-GP — kernel-uncertainty-aware nonlinear prediction

Tool:

- `athena_gp_bma_predict`.

For each finite candidate model `M_i`, obtain GP posterior mean `mu_i(x)` and variance `v_i(x)`. V12 returns the mixture mean

`mu(x)=sum_i w_i mu_i(x)`

and law-of-total-variance decomposition

`Var(Y|D)=sum_i w_i v_i(x) + sum_i w_i (mu_i(x)-mu(x))^2`.

The first term is within-model predictive uncertainty. The second is between-model/kernel uncertainty.

A narrow BMA posterior remains conditional on the finite GP family, prior and observed rows.

## 3. ΩSUBSET-GP — deterministic bounded approximation

Tool:

- `athena_gp_sparse_predict`.

V12 selects at most 64 stored observations by deterministic farthest-point traversal, beginning with the observed point farthest from the empirical feature centroid and repeatedly adding the point maximizing distance to the selected set.

The GP posterior is then calculated exactly on that selected subset. The full current bounded V10 GP prediction is also computed as a reference, and the result exposes absolute mean and variance error against that reference.

This is a transparent subset-of-data approximation. It is **not** sparse variational GP inference, inducing-point optimization, or a scalable-GP theorem.

## 4. ΩBMA-GP-EVSI — decision value under kernel uncertainty

Tool:

- `athena_gp_bma_decision_evsi`.

For each candidate model, V12 builds the joint GP posterior over action locations and candidate measurement locations. Monte Carlo simulation proceeds by:

1. sampling a candidate GP model from the finite hyperparameter posterior;
2. sampling a hypothetical measurement under that model;
3. updating finite model weights from the measurement likelihood;
4. conditionally updating action posterior means within each candidate GP;
5. selecting the best downstream action under the updated mixture.

`EVSI(e) ~= E_y[max_a EU(a|y,e)] - max_a EU(a)`.

Cost, risk, feasibility and ethics remain explicit independent gates.

Status:

`FINITE_GRID_BMA_GP_EVSI_DESIGN_ONLY`.

No simulated measurement enters GP observations or model history.

## 5. ΩPAG-CANDIDATE — uncertainty-preserving observed structure

Tool:

- `athena_pag_candidate_discover`.

Current bounds:

- 3..8 observed numeric variables;
- at least 20 rows;
- Gaussian/linear partial-correlation CI tests;
- conditioning depth <=3.

The runtime begins with a complete observed skeleton, removes edges under accepted conditional independences, stores separation sets, and marks endpoints initially as circles. Unshielded triples whose middle node is absent from the corresponding separation set receive arrowheads into the middle:

`X o-> Z <-o Y`.

A limited conservative propagation rule can orient additional tail/arrowhead candidates.

Output:

`BOUNDED_PAG_CANDIDATE`.

This output lacks full FCI/RFCI possible-d-sep search, complete PAG orientation rules, selection-bias semantics and hidden-confounder completeness. It never creates canonical JSPACE edges.

## 6. ΩLONGITUDINAL — two-timepoint parametric causal g-formula

Tool:

- `athena_longitudinal_gformula`.

The implemented time structure is:

`X -> A1 -> L1 -> A2 -> Y`

with optional baseline `X`, binary `A1`, binary intermediate `L1`, binary `A2`, and binary outcome `Y`.

V12 fits:

`P(L1=1 | X,A1)`

and

`P(Y=1 | X,A1,L1,A2)`

with transparent logistic models. For a static treatment regime `(a1,a2)`, estimated risk is

`E_X[(1-p_L(X,a1))Q(X,a1,0,a2) + p_L(X,a1)Q(X,a1,1,a2)]`.

The default evaluates all four binary static regimes.

Status:

`TWO_TIMEPOINT_PARAMETRIC_GFORMULA_ESTIMATED_UNDER_ASSUMPTIONS`.

Declared latent-confounding risk fails closed. Sequential exchangeability, positivity, consistency and nuisance-model correctness remain external assumptions.

## 7. ΩCHANCE — finite chance-constrained resource selection

Tool:

- `athena_chance_resource_select`.

Each candidate has value and resource consumption model

`R_ir ~ N(mu_ir,sigma_ir^2)`

under the explicit approximation that candidate resource consumptions are independent within each resource dimension.

For selected subset `S`:

`mu_r(S)=sum_i in S mu_ir`

`sigma_r(S)=sqrt(sum_i in S sigma_ir^2)`.

The one-sided Gaussian chance approximation requires

`mu_r(S)+z_(1-alpha)sigma_r(S) <= B_r`

for every resource budget `B_r`.

For up to `exact_limit<=18` candidates, every subset is enumerated and the maximum total value feasible subset is returned with certificate

`EXACT_ENUMERATION_UNDER_DECLARED_INDEPENDENT_GAUSSIAN_RESOURCE_MODEL`.

Above that threshold, a deterministic greedy fallback returns

`CHANCE_CONSTRAINED_GREEDY_NO_OPTIMALITY_CERTIFICATE`.

The exact certificate is about the declared finite optimization problem and Gaussian approximation only, not distribution-free real-world feasibility.

## 8. V12 coordinate fiber

A materially governing V12 output may expose

`COLLECTIVE_JOINT=<HP,BM,SG,PG,LC,JV,CC,L>`

where:

- `HP`: finite GP hyperparameter posterior;
- `BM`: Bayesian-model-averaged GP prediction;
- `SG`: subset/sparse-GP approximation witness;
- `PG`: bounded PAG candidate;
- `LC`: longitudinal causal-policy/g-formula state;
- `JV`: joint/BMA GP decision value;
- `CC`: chance-constrained resource control state;
- `L`: lineage/native context.

This fiber is additive to all V1–V11 coordinates and has no independent canonical mutation authority.

## 9. V13 residual boundary — not claimed by V12

1. continuous posterior integration over GP hyperparameters;
2. sparse variational/inducing-point GP inference with scalable complexity guarantees;
3. neural Bayesian world models;
4. full FCI/RFCI/PAG discovery with possible-d-sep and complete orientation rules;
5. calibrated posterior structural-edge uncertainty;
6. longitudinal TMLE and dynamic treatment regimes;
7. continuous/multivalued treatment causal policy estimation;
8. general off-policy causal policy value/evaluation;
9. joint GP/POMDP long-horizon experiment optimization;
10. continuous-state/action Bayes-adaptive control;
11. correlated/resource-coupled chance constraints and distributionally robust stochastic optimization;
12. dynamic chance-constrained resource control;
13. finite-sample calibrated evidence-dependence intervals;
14. microVM/VM hostile-code attestation;
15. distributed semantic/Git transactional commit and policy-authorized Git compensation.

These remain successor work rather than being promoted by adjacency.
