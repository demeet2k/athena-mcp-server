# ATHENA Runtime Migration

## Active-tree provenance

The active `master` tree was rebuilt during the 2026-08-07 rebuild. Previous state remains pinned at `archive/pre-rebuild-2026-08-07` and in Git history, but legacy presence is never sufficient for canonical status.

Legacy admission:

`DISCOVER → HASH → CLASSIFY → CCR SEARCH → OID/VID → SOURCE → KC144 → JSPACE → SCALE → TEST/EVIDENCE → STATUS`.

Do not bulk-copy legacy folders into the runtime.

---

# 2.3.0 -> 2.4.0

`athena-canonical-mcp 2.4.0` adds Collective Science V5 on top of V1 organization, Growth metabolism, V2 memory, V3 bounded adaptation and V4 experimental ecology.

No destructive database rewrite is required. V5 is lazily initialized through the collective dispatcher and uses additive `CREATE TABLE IF NOT EXISTS` state.

## New persistent V5 surfaces

- full-covariance contextual Bayesian models;
- retained pre-update prediction/coverage observations for uncertainty calibration;
- pairwise interaction-credit records;
- delayed confidence-weighted credit records;
- action-conditioned transition statistics/observations;
- learned task-regime centroids;
- semantic projection-compensation records.

Existing semantic objects/events/edges, V2 memory, V3 policy/budget state and V4 bandit/credit/worker/diffusion/projection state are not bulk rewritten.

## V5 tool migration

New MCP operations:

- `athena_bayes_predict`
- `athena_bayes_observe`
- `athena_uncertainty_calibrate`
- `athena_experiment_design`
- `athena_interaction_credit`
- `athena_delayed_credit_record`
- `athena_delayed_credit_summary`
- `athena_transition_observe`
- `athena_transition_predict`
- `athena_rollout_learned`
- `athena_schedule_multiperiod`
- `athena_witness_cell`
- `athena_regime_geometry_observe`
- `athena_regime_geometry_resolve`
- `athena_pareto_frontier`
- `athena_projection_compensate`.

New resource:

`athena://collective/v5`.

## Bayesian-state migration

V4 diagonal bandit observations are **not** relabeled as V5 full-covariance observations. V5 begins with its own model state so covariance and calibration semantics remain clean.

V5 may coexist with V4:

- V4 UCB remains useful for simple experiment selection;
- V5 Bayesian state is preferred when correlated feature uncertainty or empirical interval coverage matters;
- both update only from explicit observed reward.

`BANDIT_HISTORY != BAYES_HISTORY` unless an explicit future migration proves compatible sufficient statistics.

## Calibration migration

V5 interval calibration requires a prediction made **before** observing the corresponding reward. Therefore historical rows that lack a retained pre-update interval are not silently counted as coverage observations.

Old observations remain valid outcome history; they simply do not retroactively become interval-calibration trials.

## Experiment-design migration

No historical policy prediction is automatically converted into a hypothesis likelihood.

Active experiment design requires explicit:

- hypothesis IDs;
- normalized priors or weights;
- candidate experiment outcome likelihoods;
- cost/risk/feasibility metadata where relevant;
- ethics eligibility.

Missing likelihoods remain `INCOMPLETE_PREDICTIONS`. Experiment design returns `DESIGN_ONLY` and never becomes an observation until the experiment is actually run.

## Causal-credit migration

V4 intervention credit remains valid according to its original design/confidence semantics.

V5 adds interaction and delayed-credit surfaces rather than rewriting earlier credit:

- pair interaction requires all four `00/01/10/11` cells;
- missing factorial cells stay `UNIDENTIFIED`;
- delayed credit requires explicit causal confidence and temporal discount;
- no old event receives interaction/delayed credit automatically.

## Transition-model migration

V4 explicit rollout `context_delta` values are not silently treated as empirical transition observations.

V5 transition statistics update only after an observed before/after context pair is explicitly recorded through `athena_transition_observe`.

Thus:

`SIMULATED_DELTA != OBSERVED_TRANSITION`.

## Scheduling migration

The V4 scheduler remains the default for immediate one-step task allocation.

Use V5 `athena_schedule_multiperiod` only when time structure materially matters: dependencies, durations, deadlines, finite horizon or shared resource budgets.

V5 uses bounded beam search and deliberately exposes that it has no general global-optimality proof.

Unknown constrained resource costs continue to remain unknown/penalized rather than becoming zero.

## Witness migration

Both V4 and V5 use the same repository-owned unittest reference grammar:

`tests/<path>.py::TestCase::test_method`.

V5 `athena_witness_cell` adds stronger process constraints, but remains non-hermetic. It should replace V4 execution when those extra resource/environment constraints matter; it should not be used as justification for running hostile arbitrary code.

## Learned-regime migration

V4 coarse task regimes remain deterministic stable routing partitions.

V5 learned centroids are an additional similarity/transfer surface. They do not rename semantic objects or replace the coarse regime identifier.

`LEARNED_REGIME != IDENTITY`.

## Pareto migration

Existing scalar RGO/policy scores remain usable. V5 Pareto search should be used when a forced scalar score would discard meaningful tradeoffs.

Frontier membership is relative to the exact candidate set and metric directions supplied in the call. It is not a universal ranking.

## Projection compensation migration

V4 projection sagas historically ended in:

`COMPLETED | ABORTED | COMPENSATION_REQUIRED`.

V5 extends the recovery vocabulary with `COMPENSATED` only after a lawful semantic inverse has been applied.

The current inverse is deliberately narrow: it retracts active JSPACE edges whose parsed attributes contain the exact projection ID.

It does not:

- delete unrelated semantic edges;
- erase compensation events/history;
- rewrite Git history;
- claim to invert arbitrary semantic mutations.

If a projection has an associated Git commit, V5 returns `git_compensation_required=true` so Git recovery remains explicit.

## Authority compatibility

The upgrade does not weaken previous authority boundaries:

- semantic writes retain semantic/VID authority;
- Git checkpointing retains Git-head CAS;
- topology retains topology-version CAS;
- V3 policy retains policy-version CAS;
- V4/V5 predictive models remain observational/advisory surfaces;
- V5 compensation requires exact current semantic-event head.

## Science firewall during migration

Do not map old state into new labels merely to populate tables:

- prediction != observation;
- posterior != truth;
- coverage != model validity;
- design != result;
- counterfactual != observation;
- correlation/interaction contrast != causal proof;
- delay != causation;
- simulated transition != observed transition;
- learned regime != identity;
- bounded schedule != optimum;
- Pareto frontier != single best;
- semantic compensation != Git rollback.

## Deployment check

After upgrade verify:

1. package version and MCP `SERVER_INFO.version` are both `2.4.0`;
2. `athena://collective/v5` appears in resources and reads successfully;
3. V5 tool names appear in `tools/list`;
4. full constructive V5 tests pass;
5. full adversarial V5 tests pass;
6. legacy V1–V4 regression tests still pass;
7. `athena://transforms` resource still reads successfully;
8. stdio `python -m athena_mcp` smoke crosses a V5 science tool/resource plus exact emission verification;
9. canonical brain is pinned only after the final runtime/documentation head passes CI.
