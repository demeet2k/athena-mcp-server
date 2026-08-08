# ATHENA Canonical MCP v2.4 — Polycoordinate Crystal + Causal Experimental Collective Runtime

ATHENA's executable Git/MCP nervous substrate: canonical identity/versioning, typed JSPACE, SCALE, KC144/polycoordinates, exact visible-output crystallization, and a layered collective-intelligence runtime that now extends from organization through memory, bounded learning, uncertainty-aware ecology, and causal experimental science.

## Runtime cycle

`HYDRATE → RECONSTRUCT → MEMORY/ANTIBODY/ELDER → COARSE+LEARNED REGIME → BAYES/CALIBRATION → LIVE HYPOTHESES → EIG EXPERIMENT DESIGN → PARETO FRONTIER → COLLECTIVE PLAN → MULTIPERIOD BUDGET SCHEDULE → EXECUTE/METER → QUORUM/FALSIFY/WITNESS → OBSERVE → MAIN/INTERACTION/DELAYED CREDIT → BAYES/BANDIT/POLICY UPDATE → TRANSITION UPDATE/ROLLOUT → PHEROMONE/DIFFUSION/IMMUNE/ELDER → JSPACE/TOPOLOGY/PROJECTION/COMPENSATION → LIFECYCLE → FINALIZE/VERIFY → CONDITIONAL COMMIT → REATTACK`

## Authority

- semantic state: expected-VID / semantic-head CAS;
- Git state: expected-Git-head CAS;
- collective topology: expected-topology-version CAS;
- learned V3 policy: expected-policy-version CAS;
- topology→JSPACE uses a recovery saga, not a fictional SQLite+Git distributed transaction;
- V5 semantic compensation only retracts currently active edges owned by the exact projection and never pretends to rewrite Git history.

`SID != OID != MID != VID != CID != EID != CRYS != ENV`.

## Exact visible output

`athena_finalize_output` crystallizes the body, derives the header, assembles the exact visible envelope, creates an emission manifestation, indexes every visible lexeme, and returns bytes that can be verified by `athena_verify_emission`.

Coordinate lists are navigation only. `LOOKUP != DERIVATION`; measured holonomy is promoted only for all-derivational routes.

---

## Collective Runtime V1 — organization

HIVE/SWARM/PACK/FLOCK/HERD/POD selection, dynamic worker width, role allocation, bounded-neighbor topology, protected reserve, evidence-sensitive quorum/cross-inhibition, advisory stigmergy and homeostasis.

Resource: `athena://collective/runtime`  
Spec: `spec/COLLECTIVE_RUNTIME.md`

Core law: `MAX_GROWTH != MAX_ACTIVITY` and `MAX_INTEGRATION != MAX_CONNECTIVITY`.

## Collective Growth V1 — metabolism

Demand-sensitive allocation, living-bridge economics, FISSION/FUSE/HOLD pressure, dependency alarm transport and lineage-preserving artifact lifecycle.

Resource: `athena://collective/growth`  
Spec: `spec/COLLECTIVE_GROWTH.md`

## Collective Runtime V2 — persistent organizational memory

Database-backed pheromone field; typed JSPACE invalidation compiler; predicted-vs-observed RGO calibration; versioned topology CAS/rollback; reusable failure antibodies containing detector, repair, evidence and regression references.

Resource: `athena://collective/v2`  
Spec: `spec/COLLECTIVE_RUNTIME_V2.md`

## Collective Runtime V3 — bounded empirical adaptation

Observed budget memory; rollbackable regularized learned policy; simulate-only one-step counterfactual ranking; evidence-backed elder authority; empirical antibody families/expiry; multiscale pheromones across token→artifact→module→domain→system.

Resource: `athena://collective/v3`  
Spec: `spec/COLLECTIVE_RUNTIME_V3.md`

## Collective Runtime V4 — uncertainty-aware experimental ecology

### ΩREGIME / ΩBANDIT
Deterministic task regimes plus diagonal contextual-UCB selection with local evidence, bounded cross-regime transfer, explicit uncertainty, and V3 policy prior. Only explicit observed reward updates the posterior.

### ΩCREDIT
Design-dependent causal confidence, intervention credit and preserved unattributed residual.

### ΩSCHEDULER
Measured per-worker cost/efficiency and one-step budget-aware allocation. `UNKNOWN_COST != ZERO_COST`.

### ΩDIFFUSION
Shrinkage-learned scale-to-scale pheromone transfer utility with causal confidence stored separately from routing usefulness.

### ΩREGRESSION
Restricted repository-owned unittest execution; no arbitrary commands; not claimed OS-hermetic.

### ΩROLLOUT
Explicit-transition multi-step simulate-only organization trajectories.

### ΩPROJECTION
Topology→JSPACE plan/preflight/saga with `ABORTED` vs `COMPENSATION_REQUIRED` recovery states.

Resource: `athena://collective/v4`  
Spec: `spec/COLLECTIVE_RUNTIME_V4.md`

---

# Collective Runtime V5 — Causal Experimental Operating System

V5 converts the V4 experiment selector into a stronger scientific operating layer while retaining every evidence firewall.

## ΩBAYES — correlated uncertainty

- `athena_bayes_predict`
- `athena_bayes_observe`
- `athena_uncertainty_calibrate`

V5 maintains a full ridge precision matrix

`A = λI + Σ w φφᵀ`

with

`θ̂ = A⁻¹b`

and predictive leverage

`h(φ)=φᵀA⁻¹φ`.

Unlike the V4 diagonal bandit, correlated feature uncertainty is retained through the returned posterior covariance matrix. Every observation stores its **pre-update** interval so empirical coverage calibration cannot cheat by measuring the posterior after learning the answer.

`POSTERIOR != TRUTH` and `COVERAGE_CALIBRATION != MODEL_VALIDITY`.

## ΩDESIGN — active hypothesis discrimination

- `athena_experiment_design`

For caller-supplied hypotheses/priors and binary outcome likelihoods, V5 computes expected posterior entropy and expected information gain. Cost, risk, feasibility and an explicit ethics gate modify eligibility/ranking. Missing likelihoods remain `INCOMPLETE_PREDICTIONS`; unethical candidates remain `ETHICS_BLOCK` even when maximally informative.

Results are always `DESIGN_ONLY`.

`EXPECTED_INFORMATION_GAIN != EVIDENCE` and `DESIGN != RESULT`.

## ΩINTERACTION / ΩDELAY — stronger causal credit

- `athena_interaction_credit`
- `athena_delayed_credit_record`
- `athena_delayed_credit_summary`

Main effects use present-vs-absent contrasts. Pair interactions use the full 2×2 contrast

`μ11 - μ10 - μ01 + μ00`.

If any factorial cell is missing the effect remains `UNIDENTIFIED`; numerical contrasts are not promoted to causal without adequate design confidence.

Delayed credit is explicitly

`ΔY × causal_confidence × discount^delay`.

Temporal delay alone never identifies cause.

## ΩTRANSITION — learned organization dynamics

- `athena_transition_observe`
- `athena_transition_predict`
- `athena_rollout_learned`

Observed action-conditioned context deltas are stored as weighted sufficient statistics and shrunk toward zero until evidence accumulates. Unseen features remain unchanged/unknown rather than fabricated. Learned-transition rollouts expose uncertainty-banded discounted return and are always `SIMULATE_ONLY`.

`TRANSITION_MODEL != WORLD_TRUTH` and `ROLLOUT != EXECUTION`.

## ΩSCHEDULE — finite-horizon operating schedule

- `athena_schedule_multiperiod`

V5 schedules bounded task sets across time while respecting explicit dependencies, durations, worker capability/capacity, horizon, deadlines and observable resource budgets. It uses bounded beam search and explicitly returns

`BOUNDED_BEAM_SEARCH_NO_GLOBAL_OPTIMALITY_PROOF`.

## ΩCELL — stronger witness isolation

- `athena_witness_cell`

The witness grammar remains repository-owned Python unittests only. V5 adds isolated Python mode, sanitized environment/temp HOME, `shell=False`, timeout, Python socket denial, and POSIX CPU/address-space/file-size/fd limits when available. The result reports the exact isolation controls actually applied.

It is deliberately **not** labeled OS-hermetic.

## ΩREGIME-GEOMETRY

- `athena_regime_geometry_observe`
- `athena_regime_geometry_resolve`

Weighted task-signal centroids create evidence-backed transfer neighborhoods around the coarse V4 regime partition. Learned regime geometry is routing context, never semantic identity.

## ΩPARETO

- `athena_pareto_frontier`

V5 computes the exact finite non-dominated frontier for caller-supplied metrics/directions. Optional interval-robust mode requires worst-case dominance against the competitor's best-case values. Crowd distance provides a frontier-diversity surface rather than inventing one scalar winner.

## ΩCOMPENSATION

- `athena_projection_compensate`

V5 supplies a real inverse for the narrow semantic side effect of V4 projection: active edges bearing the exact projection ID. Compensation is semantic-head-CAS protected, emits compensation events, retracts only projection-owned active edges, leaves unrelated edges intact, and surfaces whether separate Git compensation remains necessary.

`SEMANTIC_COMPENSATION != GIT_ROLLBACK`.

Resource: `athena://collective/v5`  
Spec: `spec/COLLECTIVE_RUNTIME_V5.md`

## V5 science firewall

- `POSTERIOR != TRUTH`
- `CALIBRATION != VALIDITY`
- `EIG != EVIDENCE`
- `DESIGN != RESULT`
- `INTERACTION != CAUSATION WITHOUT IDENTIFICATION`
- `DELAY != CAUSATION`
- `TRANSITION_MODEL != WORLD`
- `ROLLOUT != EXECUTION`
- `BOUNDED_SCHEDULE != GLOBAL_OPTIMUM`
- `WITNESS_CELL != HERMETIC_SANDBOX`
- `LEARNED_REGIME != IDENTITY`
- `PARETO_FRONTIER != SINGLE_BEST`
- `SEMANTIC_COMPENSATION != GIT_ROLLBACK`

## Run

`python -m athena_mcp --db ./state/athena.db`

MCP server package: `athena-canonical-mcp 2.4.0`  
MCP protocol revision: `2025-11-25`.
