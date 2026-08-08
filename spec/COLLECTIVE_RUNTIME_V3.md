# ATHENA COLLECTIVE RUNTIME V3 — SELF-LEARNING COLLECTIVE ECOLOGY

V3 converts the persistent organizational memory introduced in V2 into a bounded, measured learning layer. The runtime can now meter observable resources, learn a rollbackable organization policy from explicit outcomes, simulate alternative organizations before mutation, derive longitudinal elder authority from repeated success, evolve failure-antibody families, and propagate stigmergic reinforcement across token/artifact/module/domain/system coordinates.

## Authority boundary

`COLLECTIVE_RUNTIME_V3` is a learning control plane, not autonomous canonical authority.

- semantic mutation still requires expected-VID CAS;
- Git persistence still requires Git-head CAS;
- collective topology still requires topology-version CAS;
- learned policy writes require policy-version CAS;
- policy updates require an explicit observed reward;
- counterfactual simulation cannot mutate topology;
- unavailable resource dimensions remain unknown rather than inferred;
- elder authority is defeasible evidence, not rank by age;
- antibody matching/selection is routing evidence, not causal proof.

## 1. Resource metabolism / ΩBUDGET

Measured resource vector:

`C_real = <tokens, wall_time_s, tool_calls, compute_units, retrieval_ops, storage_bytes, human_attention_min>`.

The MCP dispatch layer automatically records `tool_calls` and measured wall-clock execution time for MCP tool calls. The server cannot directly observe model-token or external-compute usage, so those dimensions are accepted only when a caller supplies an observable measurement.

For every resource with a positive explicit budget:

`ratio_k = used_k / budget_k`.

Budget pressure is the mean capped consumption fraction:

`P_budget = mean(min(1,ratio_k))`.

A dimension is over budget iff `ratio_k > 1`.

When a normalized useful-output observation `U` is supplied:

`efficiency = U / (1 + P_budget)`.

No scalar budget pressure is fabricated when no comparable budget denominator exists.

Tools:

- `athena_budget_record`
- `athena_budget_summary`

## 2. Bounded learned organization policy / ΩPOLICY

The policy consumes an open normalized feature map `x`, with each numeric feature clipped to `[-1,1]`.

Current policy state:

`Pi = <scope,version,b,w,n,eta_0,lambda>`.

Prediction:

`z = b + w·x`

`p = sigmoid(z)`.

An explicit normalized reward `r in [0,1]` produces error:

`e = r - p`.

Learning rate decays with observation count:

`eta_n = eta_0 / sqrt(n+1)`.

Using the local logistic derivative:

`g = e p(1-p)`.

Bounded update:

`b' = clip(b + eta_n g, -3, 3)`

`w'_j = clip(w_j + eta_n(g x_j - lambda w_j), -3, 3)`.

This gives three anti-runaway constraints simultaneously:

1. coefficient bounds;
2. sample-count learning-rate decay;
3. L2 shrinkage.

Every update requires:

`expected_policy_version == current_policy_version`.

Otherwise the write fails with `STALE_POLICY`.

Every successful update stores a before/after witness. `athena_policy_rollback` restores a selected historical before-state as a **new** policy version; rollback never erases history.

Policy reliability is exposed as:

`rho_policy = n / (n + 20)`.

Thus a young policy may advise but cannot silently dominate an established non-learned baseline.

Tools:

- `athena_policy_state`
- `athena_policy_score`
- `athena_policy_update`
- `athena_policy_rollback`

## 3. Counterfactual organization simulator / ΩCOUNTERFACTUAL

Candidate organization `i` first receives the deterministic V1 organization evaluation:

`R_i = RGO(configuration_i)`.

V2 empirical calibration produces:

`C_i = Calibrate(R_i)`.

V3 learned policy produces:

`P_i = Pi(x_i)`.

The learned mixture is:

`L_i = 0.60 C_i + 0.40 P_i`.

Policy reliability controls how much that learned term may influence selection:

`M_i = (1-rho_policy) C_i + rho_policy L_i`.

Risk and budget pressure then produce:

`U_i = max(0, M_i - 0.15 Risk_i - 0.10 BudgetPressure_i)`.

Candidates are ranked by `U_i`, but the result is always:

`decision = SIMULATE_ONLY`.

The simulator does not call topology mutation and cannot convert its own prediction into an observation. The selected candidate must be executed and measured before becoming policy evidence.

Tool:

- `athena_counterfactual_simulate`

## 4. Longitudinal elder authority / ΩELDER

Elder authority tracks repeated outcomes across five dimensions:

- reuse success: weight `0.20`;
- prediction success: `0.25`;
- repair success: `0.20`;
- regression success: `0.20`;
- cross-context generalization success: `0.15`.

For dimension `j` with success sum `s_j` over `c_j` observations, use a Beta(1,1) posterior mean:

`p_j = (s_j + 1)/(c_j + 2)`.

Weighted base authority:

`A_base = sum(w_j p_j) / sum(w_j)`.

Evidence confidence:

`q = N_evidence/(N_evidence + 10)`.

Contradiction rate:

`k = contradiction_sum / observations`.

Final authority:

`A = clip((1-q)*0.5 + q*(A_base - 0.30 k),0,1)`.

This law intentionally prevents seniority from being created by age, repetition, popularity, or mere survival. Authority rises only through measured usefulness and can fall through contradiction.

Tools:

- `athena_elder_observe`
- `athena_elder_rank`

## 5. Evolving failure-antibody families / ΩIMMUNE++

V2 antibodies store signature, detector, repair, evidence and regression references. V3 adds empirical outcome state:

`AB+ = <family,parent,status,successes,failures,false_positives,regression_passes,regression_failures,expiry>`.

Observed outcomes are one of:

- `SUCCESS`;
- `FAILURE`;
- `FALSE_POSITIVE`;
- `REGRESSION_PASS`;
- `REGRESSION_FAIL`.

Smoothed repair reliability:

`R_ab = (successes + 1)/(successes + failures + false_positives + 2)`.

Regression reliability:

`R_reg = (regression_passes + 1)/(regression_passes + regression_failures + 2)`.

A high false-positive rate moves an antibody to `WATCH`; sufficiently poor empirical reliability can retire it; expiry removes active selection while preserving lineage/history.

A distinct signature may become a child variant of an existing family. Variant selection combines semantic match, repair reliability, regression reliability, status and expiry:

`SelectionScore = SemanticMatch * (0.55 + 0.30 R_ab + 0.15 R_reg) * StatusFactor`.

The winning antibody remains a hypothesis about the appropriate repair, not proof that the present failure has identical cause.

Tools:

- `athena_antibody_record_outcome`
- `athena_antibody_evolve`
- `athena_antibody_select`

## 6. Multiscale pheromone field / ΩPHEROMONE^N

The scale ladder is:

`token -> artifact -> module -> domain -> system`.

A reinforcement event declares a source scale and whatever lawful related coordinates are known. No missing coordinate is synthesized.

If a target is `d` scales above the source:

`gain_target = gain_source * upward_decay^d`.

If it is `d` scales below:

`gain_target = gain_source * downward_decay^d`.

Each scaled route is persisted through the existing V2 pheromone law as:

`MSP/<scale>/<coordinate>`.

Consequently a successful artifact can reinforce its module/domain/system context without giving every level equal weight, while token-local evidence can remain predominantly local.

Tools:

- `athena_pheromone_multiscale_reinforce`
- `athena_pheromone_multiscale_field`

## 7. Integrated V3 developmental cycle

`HYDRATE`
`-> MEMORY/ANTIBODY QUERY`
`-> BUDGET STATE`
`-> COLLECTIVE PLAN`
`-> RGO CALIBRATION`
`-> POLICY SCORE`
`-> COUNTERFACTUAL ORGANIZATION RANKING`
`-> DEMAND ALLOCATION`
`-> EXECUTION + AUTOMATIC TOOL/WALLTIME METERING`
`-> QUORUM/VERIFY`
`-> OBSERVED RGO + EXPLICIT REWARD`
`-> BOUNDED POLICY UPDATE`
`-> MULTISCALE PHEROMONE UPDATE`
`-> ELDER OUTCOME UPDATE`
`-> ANTIBODY OUTCOME/VARIANT UPDATE`
`-> JSPACE INVALIDATION IF NEEDED`
`-> TOPOLOGY CAS/ROLLBACK IF NEEDED`
`-> LIFECYCLE`
`-> FINALIZE/VERIFY/CANONICAL COMMIT`.

Resource:

`athena://collective/v3`.

## 8. V4 residuals — not claimed as implemented

1. automatic model-token accounting when the MCP host does not expose token telemetry;
2. direct GPU/CPU/energy accounting without a supplied external measurement;
3. contextual-bandit or Bayesian exploration policies with calibrated uncertainty rather than the current bounded online logistic surface;
4. causal credit assignment when multiple simultaneous organization changes affect one outcome;
5. per-task-regime policy families and hierarchical transfer between them;
6. automatic execution of antibody regression witnesses in a sandbox after a match;
7. learned scale-to-scale pheromone diffusion coefficients rather than fixed attenuation;
8. direct projection of accepted collective topology into canonical JSPACE under joint semantic/Git CAS;
9. uncertainty-aware counterfactual rollouts over multi-step organization trajectories rather than one-step rankings;
10. budget-aware worker scheduling that closes the loop between observed per-worker cost and future allocation.
