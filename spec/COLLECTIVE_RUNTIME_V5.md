# ATHENA COLLECTIVE RUNTIME V5 — CAUSAL EXPERIMENTAL OPERATING SYSTEM

V5 extends V4's uncertainty-aware experimental ecology into a stronger causal/scientific control plane. It implements correlated-feature Bayesian uncertainty, empirical interval calibration, active experiment design, identified pair-interaction and delayed credit, learned transition dynamics, finite-horizon resource scheduling, stronger constrained witness cells, learned regime geometry, Pareto organization search, and explicit semantic compensation for topology-projection edges.

The objective is **better experimental design and stronger evidence accounting**, not a hidden authority upgrade.

---

## 0. Constitutional boundaries

V5 preserves all earlier authority separations and adds:

`POSTERIOR != TRUTH`

`COVERAGE_CALIBRATION != MODEL_VALIDITY`

`EXPECTED_INFORMATION_GAIN != EVIDENCE`

`EXPERIMENT_DESIGN != EXPERIMENT_RESULT`

`INTERACTION_CONTRAST != CAUSAL_INTERACTION` unless design confidence identifies it

`TEMPORAL_DELAY != CAUSATION`

`TRANSITION_MODEL != WORLD_TRUTH`

`ROLLOUT != EXECUTION`

`BOUNDED_SCHEDULE != GLOBAL_OPTIMUM`

`WITNESS_CELL != OS_HERMETIC_SANDBOX`

`LEARNED_REGIME != SEMANTIC_IDENTITY`

`PARETO_FRONTIER != SINGLE_BEST_ACTION`

`SEMANTIC_COMPENSATION != GIT_ROLLBACK`.

Canonical semantic writes still require semantic-head/VID authority. Git remains its own causal store. Topology and learned policy retain their existing CAS planes.

---

# 1. ΩBAYES — full-covariance contextual uncertainty

V4 uses a diagonal contextual uncertainty surface. V5 stores a ridge-regularized full precision matrix so correlated features contribute to uncertainty geometry.

For feature vector

`phi = [1,x_1,...,x_d]^T`

maintain

`A = lambda I + sum_t w_t phi_t phi_t^T`

and

`b = sum_t w_t phi_t r_t`.

Posterior coefficient estimate:

`theta_hat = A^{-1} b`.

Context prediction:

`mu_raw = phi^T theta_hat`.

The implementation clips the reward-space mean to `[0,1]` for the organization-reward surface.

Residual variance is estimated from retained pre-update prediction errors once sufficient observations exist. Before that, a conservative reward-space prior is used.

Predictive leverage:

`h(phi) = phi^T A^{-1} phi`.

Raw predictive uncertainty:

`sigma_raw = sqrt(sigma_e^2 (1 + h(phi)))`.

The full covariance matrix

`Sigma_theta = A^{-1}`

is returned so callers can inspect correlated uncertainty rather than receiving a scalar score only.

Tools:

- `athena_bayes_predict`
- `athena_bayes_observe`

A Bayesian prediction is advisory. Only an explicit observed reward may update the posterior.

---

# 2. ΩCAL — empirical uncertainty calibration

Every V5 Bayesian observation stores the **pre-update** prediction:

`<mu_t, sigma_t, L_t, U_t, r_t>`.

For a target interval coverage `q`, empirical coverage after `n` scored prior predictions is

`c_hat = covered / n`.

A Beta(1,1)-smoothed coverage estimate is

`c_post = (covered + 1)/(n + 2)`.

Calibration reliability:

`rho_cal = n/(n+20)`.

Raw scale correction:

`s_raw = q / max(epsilon,c_post)`.

Reliability-shrunk uncertainty multiplier:

`s_cal = clip(1 + rho_cal(s_raw - 1), 0.5, 3.0)`.

Then

`sigma = s_cal sigma_raw`.

This is intentionally simple: it corrects interval width against prior out-of-sample coverage without claiming the underlying linear/reward model is correct.

Tool:

- `athena_uncertainty_calibrate`.

---

# 3. ΩDESIGN — active experiment design by expected information gain

V4 chooses organizational experiments based on reward uncertainty. V5 can instead ask which experiment best separates explicit live hypotheses.

For hypotheses `H_i` with normalized priors `p_i`:

`H_prior = -sum_i p_i log_2 p_i`.

For binary experiment `e`, caller supplies

`P(Y=1 | H_i,e)`.

Marginal positive probability:

`P(Y=1|e) = sum_i p_i P(Y=1|H_i,e)`.

Bayes posterior after either outcome gives entropies

`H_+` and `H_-`.

Expected posterior entropy:

`E[H|e] = P(+)H_+ + P(-)H_-`.

Expected information gain:

`EIG(e) = H_prior - E[H|e]`.

Selection score in the implemented design surface:

`Score(e) = EIG(e)*Feasibility(e) - lambda_C Cost(e) - lambda_R Risk(e)`

when the experiment is ethically eligible.

An unethical experiment receives `ETHICS_BLOCK` even if EIG is high. An experiment missing required hypothesis likelihoods receives `INCOMPLETE_PREDICTIONS`.

When the experiment is randomizable, V5 also proposes an explicit treatment/control allocation for the requested sample size. The allocation is a design proposal, not execution.

Tool:

- `athena_experiment_design`.

Every result is `DESIGN_ONLY`.

---

# 4. ΩINTERACTION — identified interaction credit

Single-action credit is insufficient when interventions interact.

For intervention `A`, the V5 main contrast is

`Effect_A = E[Y | A present] - E[Y | A absent]`

over supplied weighted observations.

For a pair `(A,B)`, all four factorial cells are required:

`mu_11 = E[Y|A=1,B=1]`

`mu_10 = E[Y|A=1,B=0]`

`mu_01 = E[Y|A=0,B=1]`

`mu_00 = E[Y|A=0,B=0]`.

Pair interaction contrast:

`I_AB = mu_11 - mu_10 - mu_01 + mu_00`.

If any cell is missing, the interaction is explicitly `UNIDENTIFIED`; no effect is fabricated.

Evidence confidence scales with cell support and caller-supplied experimental/quasi-experimental design confidence. Even a numerical interaction remains `ASSOCIATIONAL` unless design support is sufficient for `CAUSAL_SUPPORTED`.

Tool:

- `athena_interaction_credit`.

---

# 5. ΩDELAY — long-horizon credit with explicit decay

For a later observed outcome change `DeltaY`, action `a`, causal-confidence `c`, delay `d` cycles and discount `gamma`:

`Credit_delayed = DeltaY * c * gamma^d`.

This does not assert that delay identifies cause. It only prevents a high-confidence delayed link from being treated identically to an immediate link while preserving confidence as a separate factor.

Tools:

- `athena_delayed_credit_record`
- `athena_delayed_credit_summary`.

---

# 6. ΩTRANSITION — learned organization dynamics

V4 rollouts accept only explicit context deltas. V5 can learn empirical action-conditioned context deltas.

For action `a`, context feature `k`, observation `t`:

`delta_tk = x_(t+1,k) - x_(t,k)`.

Maintain weighted sufficient statistics:

`W = sum_t w_t`

`D = sum_t w_t delta_t`

`D2 = sum_t w_t delta_t^2`.

Observed mean delta:

`m = D/W`.

V5 shrinks the transition toward zero with prior strength `kappa`:

`delta_hat = W m / (W + kappa)`.

Reliability:

`rho = W/(W+kappa)`.

Observed variance:

`v = max(0,D2/W - m^2)`.

Transition uncertainty combines empirical variance and residual prior uncertainty.

Only observed context features receive learned deltas. Missing/unseen features remain unchanged/unknown; they are not synthesized.

Tools:

- `athena_transition_observe`
- `athena_transition_predict`.

---

# 7. ΩMODEL-ROLLOUT — multi-step learned-transition simulation

For trajectory

`tau = (a_0,...,a_T)`

V5 repeatedly applies the learned action-conditioned context transition surface.

Step reward may come from an explicit supplied base reward or the deterministic organization evaluation when a concrete organization configuration is supplied.

Transition uncertainty creates a bounded penalty/band around the step reward. Discounted return:

`R_mean(tau) = sum_t gamma^t mu_t`

with corresponding lower/upper surfaces.

The result is always

`decision = SIMULATE_ONLY`.

No rollout automatically creates transition observations, policy reward, causal evidence or topology mutation.

Tool:

- `athena_rollout_learned`.

---

# 8. ΩSCHEDULE — finite-horizon multi-period resource scheduling

V4 schedules one assignment layer. V5 represents task execution over time.

Each task may specify:

- duration;
- dependencies;
- required capabilities;
- utility;
- deadline;
- observable resource cost.

Each worker has a capability set and at most one active task in the current scheduler model.

For candidate assignment `(task j, worker i)`:

`start_ij = max(worker_free_i, max_finish(dependencies_j))`

`finish_ij = start_ij + duration_j`.

Assignment must satisfy:

- `finish_ij <= horizon`;
- capability fit > 0;
- all dependencies already scheduled;
- known explicit remaining resource budget is not violated.

The objective combines discounted utility, capability fit, deadline penalties and uncertainty penalty for unknown constrained cost.

V5 uses bounded beam search over schedule states. Therefore it explicitly returns:

`optimality = BOUNDED_BEAM_SEARCH_NO_GLOBAL_OPTIMALITY_PROOF`.

Tool:

- `athena_schedule_multiperiod`.

---

# 9. ΩCELL — stronger executable regression cells

V4's regression runner already rejects arbitrary commands. V5 adds additional process constraints while retaining the same repository-owned unittest reference grammar:

`tests/<repo-file>.py::TestCase::test_method`.

Current witness cell uses:

- current Python interpreter with `-I` isolated mode;
- `shell=False`;
- fixed repository cwd;
- sanitized minimal environment and temporary HOME;
- hard wall timeout;
- Python-level replacement of `socket.socket` to deny ordinary Python socket creation;
- on POSIX where available: CPU, address-space, file-size and open-file descriptor rlimits.

The result always reports the actual isolation mechanisms applied.

V5 does **not** call this OS-hermetic. Native code, alternative network mechanisms, filesystem namespace isolation and kernel attack surface require a stronger container/VM boundary.

Tool:

- `athena_witness_cell`.

---

# 10. ΩREGIME-GEOMETRY — learned routing neighborhoods

V4 task regimes are deterministic coarse bins. V5 retains those bins but can accumulate learned centroids over the same observable task-signal vector.

For cluster `c`, weighted centroid:

`mu_c = sum_t w_t x_t / sum_t w_t`.

For query signal `x`, normalized squared distance over the signal dimensions is converted into a similarity surface:

`Similarity(c,x) = exp(-4 d^2(c,x))`.

Reliability:

`rho_c = W_c/(W_c+10)`.

Clusters are ranked by evidence-weighted similarity.

The learned cluster is a routing/transfer neighborhood. It does not replace semantic object identity or canonical task meaning.

Tools:

- `athena_regime_geometry_observe`
- `athena_regime_geometry_resolve`.

---

# 11. ΩPARETO — organization frontier instead of forced scalar collapse

For candidate metric vector `J(a)`, V5 supports per-metric direction `max` or `min`.

Candidate `a` dominates `b` when it is no worse across every metric and strictly better by more than epsilon on at least one metric.

The returned exact frontier is computed over the supplied finite candidate set.

Optional robust interval mode requires the candidate's worst case to dominate the competitor's best-case comparison value, making uncertain candidates harder—not easier—to declare dominant.

V5 also computes crowding distance over the frontier as a diversity/navigation surface.

Tool:

- `athena_pareto_frontier`.

The frontier is deliberately plural. V5 does not invent one scalar winner when tradeoffs remain genuinely non-dominated.

---

# 12. ΩCOMPENSATION — explicit inverse algebra for projection-created semantic edges

V4 can detect a partially applied topology→JSPACE projection and mark `COMPENSATION_REQUIRED`, but cannot generically invert arbitrary semantic changes.

V5 implements an inverse for the narrow projection class whose semantic side effect is a set of active JSPACE edges tagged with the exact `projection_id`.

Preconditions:

1. projection saga exists and is in a compensable state;
2. exact current semantic event head equals caller's `expected_semantic_eid`;
3. candidate active edges contain attributes whose parsed `projection_id` exactly matches the saga.

For each owned active edge, V5 emits a `COMPENSATE_EDGE` event and retracts that edge from the active edge table. Unrelated edges are untouched.

The projection saga then moves to `COMPENSATED` under the V5 extension.

If the original saga has a Git commit witness, V5 returns

`git_compensation_required = true`.

It does not rewrite Git history and does not claim cross-store rollback.

Tool:

- `athena_projection_compensate`.

---

# 13. Ω5 evidence/control loop

`HYDRATE`
`-> MEMORY/ELDER/ANTIBODY`
`-> COARSE + LEARNED REGIME GEOMETRY`
`-> BAYES/INTERVAL CALIBRATION`
`-> LIVE HYPOTHESES`
`-> EXPECTED-INFORMATION-GAIN EXPERIMENT DESIGN`
`-> PARETO ORGANIZATION FRONTIER`
`-> MULTI-PERIOD RESOURCE SCHEDULE`
`-> EXECUTION + RESOURCE METERING`
`-> WITNESS/FALSIFICATION`
`-> OBSERVED OUTCOMES`
`-> MAIN/INTERACTION/DELAYED CREDIT`
`-> BAYES/BANDIT/POLICY UPDATE FROM JUSTIFIED OBSERVATION`
`-> TRANSITION MODEL UPDATE`
`-> LEARNED-TRANSITION ROLLOUT FOR NEXT PLAN`
`-> PHEROMONE/DIFFUSION/IMMUNE/ELDER UPDATE`
`-> TOPOLOGY/JSPACE + EXPLICIT COMPENSATION IF REQUIRED`
`-> LIFECYCLE`
`-> FINALIZE/VERIFY/COMMIT`.

---

# 14. V5 coordinate fiber

A materially governing V5 run may expose:

`COLLECTIVE_SCIENCE=<BY,CAL,ED,IX,DL,TR,SC,WC,RG,PF,CP,L>`

where:

- `BY`: full-covariance Bayesian posterior;
- `CAL`: empirical uncertainty calibration;
- `ED`: active experiment design/EIG surface;
- `IX`: interaction-effect identification/credit;
- `DL`: delayed credit surface;
- `TR`: learned transition dynamics;
- `SC`: multi-period schedule state;
- `WC`: constrained witness-cell evidence;
- `RG`: learned regime geometry;
- `PF`: Pareto frontier/tradeoff surface;
- `CP`: compensation state;
- `L`: lineage/native caller context.

This fiber is additive to earlier `COLLECTIVE`, `COLLECTIVE_LEARNING`, and `COLLECTIVE_ECOLOGY` coordinates.

---

# 15. Ω6 residual boundary — not claimed by V5

1. nonlinear Gaussian-process/neural posterior inference with calibrated epistemic/OOD uncertainty;
2. causal discovery or identification without adequate experimental/quasi-experimental assumptions;
3. higher-than-pairwise interaction identification at scale;
4. exact long-horizon causal credit under hidden confounding;
5. globally optimal large-scale mixed-integer scheduling with proof certificates;
6. a true OS/VM-level hermetic witness sandbox;
7. distributed transaction protocols spanning SQLite and Git rather than recovery sagas;
8. automatic Git inverse/forward compensation with policy-authorized history semantics;
9. learned stochastic transition distributions beyond independent feature delta summaries;
10. adaptive experiment generation rather than ranking caller-supplied candidate experiments;
11. formal uncertainty calibration guarantees under distribution shift;
12. online Pareto-bandit selection over continuous organization spaces;
13. exact host-level token/GPU/energy telemetry when the host does not expose it.

These remain explicit residuals. V5 does not rename them as completed merely because adjacent mechanisms now exist.
