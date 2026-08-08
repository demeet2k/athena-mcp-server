# ATHENA Runtime Migration

## Active-tree provenance

The active `master` tree was rebuilt during the 2026-08-07 rebuild. Previous state remains pinned at `archive/pre-rebuild-2026-08-07` and in Git history, but legacy presence is never sufficient for canonical status.

Legacy admission:

`DISCOVER → HASH → CLASSIFY → CCR SEARCH → OID/VID → SOURCE → KC144 → JSPACE → SCALE → TEST/EVIDENCE → STATUS`.

Do not bulk-copy legacy folders into the runtime.

---

# 2.4.0 -> 2.5.0

`athena-canonical-mcp 2.5.0` adds Collective Discovery V6 on top of the V1–V5 organization/memory/learning/ecology/science stack.

The upgrade is additive. V6 tables are created with `CREATE TABLE IF NOT EXISTS` when the discovery layer is initialized. Existing canonical objects, events, JSPACE edges, V2 memory, V3 policy/budget state, V4 ecology state and V5 science state are not bulk rewritten.

## New persistent V6 surfaces

- empirical raw-feature OOD reference models by scope/regime;
- conditional causal-analysis records over supplied DAGs;
- science-shadow claim records;
- replication/test/falsifier witnesses with explicit independence keys.

V6 additionally reuses existing V5 Bayesian and transition observation stores rather than silently migrating them into incompatible new semantics.

## New V6 MCP tools

- `athena_ood_observe`
- `athena_ood_score`
- `athena_nonlinear_predict`
- `athena_nonlinear_observe`
- `athena_experiment_generate`
- `athena_causal_identify`
- `athena_interaction_higher_order`
- `athena_transition_distribution`
- `athena_mpc_plan`
- `athena_schedule_certified`
- `athena_witness_capsule`
- `athena_pareto_bandit_select`
- `athena_claim_register`
- `athena_claim_witness`
- `athena_claim_state`.

New resource:

`athena://collective/v6`.

## Nonlinear/OOD migration

V6 nonlinear prediction uses a degree-2 polynomial lift over the V5 full-covariance Bayesian engine. Existing V5 Bayesian observations are not rewritten as nonlinear observations.

The nonlinear/OOD reference therefore begins empty and grows only from explicit `athena_nonlinear_observe` / `athena_ood_observe` calls.

`V5_LINEAR_HISTORY != V6_NONLINEAR_HISTORY` unless an explicit future compatibility migration proves equivalence.

OOD state is also separate from semantic truth. Historical task records are not retrospectively relabeled in-distribution or OOD.

## Experiment-generation migration

V5 accepts caller-supplied experiment likelihoods under the `positive_probability` contract.

V6 generates candidate experiments only from declared finite factor levels and hypothesis `base_p` / `factor_effects`. The V6 adapter translates the generated likelihood surface into V5's tested `positive_probability` contract before EIG ranking.

This adapter is intentional and regression-tested because the first V6 promotion attempt exposed a contract mismatch where generated candidates used the wrong likelihood field and therefore appeared structurally incomplete to the V5 EIG engine.

No prior policy/counterfactual score is silently converted into a hypothesis likelihood.

## Causal-identification migration

V6 adds a supplied-DAG back-door identification query. Existing V4/V5 causal-confidence credit remains unchanged and is not retroactively promoted to identified causal effect.

A V6 `IDENTIFIED_BACKDOOR` result means only that an adjustment set satisfies the implemented criterion **under the supplied graph and assumptions**. It does not prove:

- the supplied graph is correct;
- hidden confounding is absent unless declared/justified;
- every relevant variable is observed;
- the measured causal effect itself is nonzero.

If the caller declares latent-confounding risk, V6 fails closed with an unidentified state.

## Higher-order interaction migration

V5 pairwise interactions remain valid under their original 2×2 semantics.

V6 extends the factorial contrast surface through order four. It does not derive missing cells from V5 pairwise summaries. Every required `2^k` cell must be present in the explicit observation set; missing cells remain `UNIDENTIFIED`.

## Transition/MPC migration

V6 reads actual V5 transition-observation rows to reconstruct multivariate empirical delta covariance. Existing V5 mean/shrinkage summaries are not treated as new observations.

MPC planning is a read-only model operation. Repeated planning does not create transition rows. The lawful control cycle is:

`PLAN -> EXECUTE FIRST AUTHORIZED ACTION -> OBSERVE -> RECORD TRANSITION -> REPLAN`.

`MPC_PLAN != OBSERVED_TRANSITION`.

## Scheduling migration

Use the scheduling layers by required authority:

- V4 immediate budget-aware assignment — simple near-term allocation;
- V5 multi-period beam scheduler — larger finite-horizon planning without optimality proof;
- V6 certified scheduler — small finite models where exhaustive enumeration and an exact certificate are valuable.

V6 exact certification requires every resource dimension constrained by the supplied budget to be declared for every task. Missing constrained cost removes the certificate and returns an explicit non-certified fallback state.

`UNKNOWN_COST != ZERO_COST` remains unchanged.

## Witness migration

V5 `athena_witness_cell` remains the stronger portable process-constrained unittest runner and always reports non-hermetic status.

V6 `athena_witness_capsule` is opt-in for stronger Linux namespace isolation. It requires `bubblewrap` (`bwrap`). If unavailable, it returns `HERMETIC_UNAVAILABLE` and executes nothing.

It never silently falls back to V5. This preserves the meaning of requesting a stronger containment boundary.

## Pareto migration

V5 exact/robust finite Pareto frontiers remain useful for static tradeoff inspection.

V6 `athena_pareto_bandit_select` overlays experiment-selection pressure on an interval-possible frontier. Uncertainty can make a frontier candidate valuable to measure; it does not create a universal scalar ranking.

## Replication/falsification migration

V6 science-shadow claims are deliberately separate from canonical semantic objects. No existing semantic object is automatically converted into a science-shadow claim.

When a claim shadow is explicitly registered, witness independence is caller-declared through `independence_key`. Multiple witnesses sharing hidden dependencies must not be given distinct keys merely to inflate replication counts.

Science-shadow states route future verification:

`UNRESOLVED | PRELIMINARY_SUPPORT | REPLICATED_SUPPORT | FALSIFICATION_SIGNAL | CONTESTED`.

They never silently mutate canonical object status.

## Authority compatibility

2.5.0 does not weaken previous authority planes:

- semantic writes retain semantic/VID authority;
- Git writes retain Git-head CAS;
- topology retains topology-version CAS;
- V3 policy retains policy-version CAS;
- V4/V5/V6 predictive/control surfaces remain advisory/evidential;
- V5 projection compensation retains semantic-head CAS;
- V6 causal identification is conditional on supplied graph/assumption authority, not a semantic mutation path.

## Discovery firewall during migration

Do not map old state into stronger V6 labels merely to populate new surfaces:

- nonlinear basis != universal inference;
- OOD score != factual falsehood;
- generated experiment != executed result;
- supplied-DAG back-door set != real-world causal truth;
- higher-order contrast != causal interaction without identifying design;
- simulated/MPC transition != observed transition;
- certified schedule != universal optimum outside its exact declared model;
- hermetic capsule request != permission to run a weaker fallback;
- Pareto experiment selection != single best action;
- replication/falsification state != canonical truth.

## Deployment check

After upgrade verify:

1. package version and MCP `SERVER_INFO.version` both equal `2.5.0`;
2. `athena://collective/v6` appears in resources and reads successfully;
3. all V6 tool names appear in `tools/list`;
4. legacy V1–V5 constructive/adversarial regression tests pass;
5. V6 constructive tests pass;
6. V6 adversarial tests pass;
7. named V6 diagnostics pass;
8. `athena://transforms` still reads successfully;
9. stdio `python -m athena_mcp` smoke crosses V5 science, V6 generated experiment + causal-ID tools, and exact emission verification;
10. canonical brain is pinned only after the final runtime/version/documentation head passes CI.
