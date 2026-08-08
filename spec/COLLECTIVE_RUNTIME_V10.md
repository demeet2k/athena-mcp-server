# ATHENA COLLECTIVE RUNTIME V10 — PROBABILISTIC WORLD MODEL + CAUSAL CONTROL

V10 extends V9 continuous linear inference with a bounded set of stronger probabilistic operators that are implementable and auditable in the zero-dependency runtime: exact small-data fixed-kernel Gaussian-process regression, bounded Gaussian PC-stable graph discovery, binary-outcome TMLE, the standard risk-ratio E-value sensitivity metric, exact finite-horizon finite-state POMDP tree search when exhaustive completion is witnessed, and empirically calibratable evidence-dependence probabilities.

The design objective is **stronger nonlinear/statistical control without upgrading the authority of model outputs**.

## 0. Constitutional boundaries

`FIXED_KERNEL_GP != GENERAL_WORLD_TRUTH`

`BOUNDED_PC_STABLE != FCI_OR_HIDDEN_CONFOUNDER_DISCOVERY`

`TMLE_ESTIMATE != IDENTIFICATION_PROOF`

`E_VALUE != UNIVERSAL_HIDDEN_CONFOUNDING_BOUND`

`FINITE_POMDP_CERTIFICATE != INFINITE_HORIZON_OR_REAL_WORLD_OPTIMALITY`

`LEARNED_DEPENDENCE_MODEL != FORMAL_INDEPENDENCE_PROOF`.

All V1–V9 semantic/Git/topology/policy/projection authority surfaces remain unchanged.

## 1. ΩGP — exact fixed-kernel Gaussian process

Tools:

- `athena_gp_register`
- `athena_gp_state`
- `athena_gp_observe`
- `athena_gp_predict`.

V10 stores up to 128 observed rows per scoped model with declared feature order and fixed RBF hyperparameters.

For points `x,z`, kernel

`k(x,z)=sigma_f^2 exp(-||x-z||^2/(2 l^2))`.

With observation kernel matrix

`K_y = K + sigma_n^2 I`,

posterior latent mean at `x*` is

`mu*=k_*^T K_y^-1 y`

and latent variance

`var(f*)=k(x*,x*)-k_*^T K_y^-1 k_*`.

Observation-noise variance can be reported separately/additively.

The implemented calculation is exact for the stored dataset and fixed hyperparameters up to floating-point/jitter effects. Hyperparameters are not learned automatically. Predictions never become observations.

`GP_POSTERIOR != OBSERVATION`.

## 2. ΩPC — bounded Gaussian PC-stable

Tool:

- `athena_pc_stable_discover`.

V10 starts from a complete undirected graph over at most 10 numeric variables. It runs stable-level conditional-independence search for conditioning-set sizes up to caller-declared `max_conditioning<=3`.

For correlation `r` conditional on `k` variables and `n` rows, Fisher-z statistic is

`z=atanh(r)*sqrt(n-k-3)`

with two-sided standard-normal tail probability computed through `erfc`.

When conditional independence is accepted, the edge is removed and the separating set retained. Unshielded triples whose middle node is absent from the separating set are oriented as collider candidates. A bounded Meek R1/R2 closure then propagates additional compelled orientations.

Output:

`PC_STABLE_BOUNDED_PARTIAL_GRAPH`.

The result is relative to Gaussian/linear CI assumptions, alpha, conditioning-depth cap and finite data. It is not FCI, hidden-confounder discovery, or canonical JSPACE truth.

No graph-discovery call writes canonical semantic edges.

## 3. ΩTMLE — binary-treatment/binary-outcome targeted estimator

Tool:

- `athena_causal_tmle_binary`.

The current estimator is deliberately scoped to binary treatment and binary outcome.

It uses deterministic two-fold cross-fitting:

1. logistic propensity nuisance `e(X)=P(T=1|X)`;
2. logistic outcome nuisance `Q(T,X)=P(Y=1|T,X)`;
3. held-out nuisance predictions;
4. clever covariate

`H=T/e(X)-(1-T)/(1-e(X))`;

5. one-dimensional logistic fluctuation

`logit Q*(T,X)=logit Q(T,X)+epsilon H`;

6. targeted counterfactual predictions `Q*(1,X),Q*(0,X)`;
7. ATE

`psi=mean(Q*(1,X)-Q*(0,X))`;

8. influence-curve standard error and 95% large-sample interval.

Propensities are explicitly clipped. Declared latent-confounding risk fails closed.

The estimator does not establish exchangeability, positivity, consistency, transportability or graph validity.

`TMLE_ESTIMATE != CAUSAL_IDENTIFICATION`.

## 4. ΩE-VALUE — formal risk-ratio sensitivity metric

Tool:

- `athena_sensitivity_evalue`.

For risk ratio `RR>=1`, point E-value is

`E = RR + sqrt(RR(RR-1))`.

For a protective association `RR<1`, the reciprocal risk ratio is used. An optional closest-to-null confidence-interval limit receives the same transformation; an interval crossing the null has E-value 1 for that limit.

This is the standard risk-ratio E-value interpretation: the minimum strength of association an unmeasured confounder would need with exposure and outcome, conditional on measured covariates, to explain away the observed association under the metric's assumptions.

It is not a universal sensitivity theorem and does not itself identify the causal effect.

## 5. ΩPOMDP — exact bounded finite-horizon belief control

Tool:

- `athena_pomdp_solve`.

The solver accepts an explicit finite model:

- at most 8 hidden states;
- at most 8 actions;
- action reward by state;
- complete state-transition probabilities;
- complete observation probabilities by next state;
- initial belief;
- horizon `H<=4`;
- discount factor.

For belief `b`, action `a`, transition `T_a` and observation model `O_a`:

`b^-(s')=sum_s b(s)T_a(s,s')`

`P(o|b,a)=sum_s' b^-(s')O_a(o|s')`

`b'(s'|o)=b^-(s')O_a(o|s')/P(o|b,a)`.

The runtime recursively enumerates every action and every nonzero observation branch. If the entire bounded tree completes before `max_nodes`, status is

`FINITE_POMDP_EXACT_HORIZON_CERTIFIED`

with certificate

`EXACT_FOR_SUPPLIED_FINITE_MODEL_AND_HORIZON`.

If the node limit is reached, status is

`NODE_LIMIT_NO_EXACT_CERTIFICATE`.

The certificate says nothing about omitted real-world states/actions, model misspecification, infinite-horizon optimality or execution authorization.

The operation is `PLAN_ONLY`; no branch becomes observation/history automatically.

## 6. ΩDEPENDENCE-CALIBRATION — externally labelled evidence dependence

Tools:

- `athena_evidence_dependence_observe`
- `athena_evidence_dependence_fit`
- `athena_evidence_dependence_predict`.

V9 could apply caller-declared logistic dependence coefficients. V10 can learn a scoped logistic model from explicit labelled pair examples.

For feature vector `z`:

`P(dep=1|z)=sigmoid(beta_0+beta^T z)`.

Labels are external calibration observations and are persisted separately from predictions. At least 20 labelled rows with a complete shared feature schema are required before fitting. Training log loss and accuracy are exposed.

Predictions never create labels or retrain the model.

A fitted probability remains population/model conditional; it is not a theorem of statistical dependence or independence.

## 7. V10 coordinate fiber

A materially governing V10 run may expose

`COLLECTIVE_PROBABILISTIC=<GP,PC,TM,SV,PM,ED,L>`

where:

- `GP`: fixed-kernel Gaussian-process model/prediction;
- `PC`: bounded PC-stable structural hypothesis;
- `TM`: TMLE causal-effect estimate;
- `SV`: E-value sensitivity surface;
- `PM`: finite-POMDP policy/certificate;
- `ED`: empirically calibrated evidence-dependence state;
- `L`: lineage/native context.

This coordinate is additive to all V1–V9 fibers.

## 8. V11 residual boundary — not claimed by V10

1. learned GP hyperparameters / sparse scalable GP inference;
2. neural Bayesian world models;
3. full FCI/RFCI hidden-confounder PAG discovery and calibrated structure uncertainty;
4. complete Meek closure / unrestricted PC conditioning depth at large dimension;
5. continuous-treatment/outcome TMLE and flexible Super Learner nuisance ensembles;
6. formal Rosenbaum/sensitivity-function bounds beyond the E-value metric;
7. exact infinite-horizon or large-state POMDP solvers;
8. continuous-state/action belief-MDP control;
9. decision-theoretic experiment design directly over GP/POMDP belief state;
10. independently calibrated evidence-dependence labels at scale and uncertainty over calibration coefficients;
11. globally certified stochastic resource scheduling/control;
12. microVM/VM attested hostile-code witnesses;
13. distributed semantic/Git transactional commit and policy-authorized Git compensation.

These remain explicit successor work rather than being renamed complete by adjacency.
