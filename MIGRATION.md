# ATHENA Runtime Migration

## Active-tree provenance

The active `master` tree was rebuilt during the 2026-08-07 rebuild. Previous state remains pinned at `archive/pre-rebuild-2026-08-07` and in Git history, but legacy presence is never sufficient for canonical status.

Legacy admission:

`DISCOVER → HASH → CLASSIFY → CCR SEARCH → OID/VID → SOURCE → KC144 → JSPACE → SCALE → TEST/EVIDENCE → STATUS`.

Do not bulk-copy legacy folders into the runtime.

---

# 2.5.0 -> 2.6.0

`athena-canonical-mcp 2.6.0` adds Collective Dual Control V7 on top of the V1–V6 organization/memory/learning/ecology/science/discovery stack.

The migration is additive. V7 creates only its extended-identification journal table with `CREATE TABLE IF NOT EXISTS`; uncertainty decomposition, prequential bands, observational skeletons, state-dependent dynamics, scenarios, dual-control plans and replication-independence/design surfaces are derived from or read existing V5/V6 observations unless explicitly recorded as V7 identification witnesses.

Existing canonical semantic objects, JSPACE state, V2 memory, V3 policy, V4 ecology, V5 Bayesian/transition state and V6 OOD/science-shadow state are not bulk rewritten.

## New V7 MCP tools

- `athena_uncertainty_decompose`
- `athena_prequential_interval`
- `athena_causal_skeleton_discover`
- `athena_state_transition_model`
- `athena_scenario_evaluate`
- `athena_dual_control_plan`
- `athena_causal_identify_extended`
- `athena_replication_independence`
- `athena_replication_design`.

New resource:

`athena://collective/v7`.

## Uncertainty migration

No historical prediction is relabeled with a unique aleatoric/epistemic decomposition. V7 derives model-conditional diagnostics from V5/V6 state only at query time:

- residual-noise proxy;
- posterior-leverage parameter proxy;
- current V6 OOD shift proxy;
- retained empirical calibration-error proxy.

`UNCERTAINTY_DECOMPOSITION != UNIQUE_PHYSICAL_DECOMPOSITION`.

## Prequential interval migration

V7 reuses only V5 observations that already contain errors from predictions retained **before** their outcomes were observed. It does not reconstruct pseudo-prequential residuals from post-update fitted values.

If fewer than the caller-required scores exist, V7 returns `INSUFFICIENT_PREQUENTIAL_SCORES` and preserves the existing Bayesian/OOD interval without a stronger coverage label.

`EMPIRICAL_PREQUENTIAL_BAND != DISTRIBUTION_FREE_CONFORMAL_GUARANTEE UNDER ARBITRARY SHIFT`.

## Observational graph migration

No existing JSPACE edge or semantic relation is reinterpreted as a causal edge. `athena_causal_skeleton_discover` consumes explicit caller-supplied numeric samples and returns a transient association-skeleton/v-structure hypothesis surface only.

It does not mutate the canonical registry or write a discovered DAG.

`ASSOCIATION_SKELETON != CAUSAL_DAG`.

## State-dependent transition migration

V6 action-conditioned transition means/covariances remain valid. V7 fits query-time ridge state-dependent delta regressions from the original retained V5 before/after transition observations. V6 summaries are not silently turned into new training rows.

Planning/simulation operations do not create transition observations.

`STATE_DEPENDENT_MODEL != OBSERVED_TRANSITION` and `PLAN != TRAINING_DATA`.

## Scenario / dual-control migration

V7 scenario evaluation and dual-control planning are read-only model operations.

Scenario trees are bounded moment approximations over caller-declared fixed trajectories. Dual-control score combines immediate control value, a parameter-information proxy and predictive risk. Neither surface executes an action.

The lawful loop remains:

`PLAN -> EXECUTE FIRST AUTHORIZED ACTION -> OBSERVE REAL NEXT STATE -> RECORD -> REPLAN`.

`DUAL_CONTROL_PROXY != EXACT_BAYES_ADAPTIVE_CONTROL`.

## Extended causal-identification migration

V6 back-door results remain unchanged. V7 adds supplied-DAG FRONTDOOR and INSTRUMENT criterion checks and records their witness/assumption surface in the V7 identification journal.

No older causal-confidence credit or observational association is retroactively promoted to front-door or IV identification.

A passing status means only that the supplied graph, observed-node declaration and assumptions satisfy the bounded implemented criterion. It does not prove the graph is correct or estimate the causal effect.

Explicit latent-confounding risk fails closed.

## Replication-independence migration

V6 explicit independence keys remain preserved. V7 adds metadata-similarity effective-N diagnostics across dimensions such as dataset, implementation, method, operator, environment and seed family.

Multiple old witnesses are not automatically treated as independent merely because their keys differ. Identical evidence metadata can collapse effective N toward 1. Missing comparable metadata receives a conservative similarity prior rather than assumed independence.

`ESTIMATED_REPLICATION_INDEPENDENCE != FORMAL_STATISTICAL_INDEPENDENCE`.

## Replication/falsifier design migration

V7 can rank proposed next witness designs by expected power, metadata novelty/diversity, feasibility, cost and risk. The output is always `DESIGN_ONLY` and is not inserted as a witness.

`REPLICATION_DESIGN != REPLICATION_RESULT`.

## Authority compatibility

2.6.0 does not weaken any earlier authority plane:

- semantic writes retain semantic/VID authority;
- Git writes retain Git-head CAS;
- topology retains topology-version CAS;
- V3 policy retains policy-version CAS;
- V4–V7 predictive/design/control surfaces remain advisory/evidential;
- V5 projection compensation retains semantic-head CAS;
- V6/V7 causal identification remains conditional on supplied graph/assumption authority;
- V7 observational skeleton, scenario, dual-control and replication-design outputs have no hidden semantic mutation path.

## V7 firewall during migration

Do not map older state into stronger labels merely because V7 can now compute adjacent diagnostics:

- uncertainty decomposition != unique physical truth;
- prequential empirical band != universal conformal coverage;
- observational association skeleton != causal DAG;
- candidate v-structure != oriented causal truth;
- state-dependent transition model != world truth;
- scenario tree != observed future;
- dual-control proxy != exact Bayes-adaptive control;
- front-door/IV criterion pass != real-world causal truth outside supplied DAG/assumptions;
- estimated replication effective-N != formal independence proof;
- replication/falsifier design != result.

## Deployment check

After upgrade verify:

1. package version and MCP `SERVER_INFO.version` both equal `2.6.0`;
2. `athena://collective/v7` appears in resources and reads successfully;
3. all V7 tool names appear in `tools/list`;
4. legacy V1–V6 regression tests pass;
5. V7 constructive tests pass;
6. V7 adversarial tests pass;
7. `athena://transforms` still reads successfully;
8. stdio `python -m athena_mcp` crosses V5 science, V6 discovery, V7 state-dependent dynamics + dual-control + extended causal-ID, and exact emission verification;
9. canonical brain is pinned only after the final runtime/version/documentation head passes CI.

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

New resource: `athena://collective/v6`.

## V6 compatibility summary

V6 nonlinear prediction uses a degree-2 lift over V5 Bayesian state but does not relabel V5 linear history as V6 nonlinear observations. OOD references grow only from explicit observations. Generated experiment likelihoods are adapted into V5's tested `positive_probability` contract. Back-door identification is conditional on the supplied DAG and latent-confounding assumptions. Every required `2^k` higher-order factorial cell must exist. V6 transition/MPC uses real V5 before/after rows and planning never self-trains. Exact schedule certificates require exhaustive completion and complete constrained-cost declarations. The stronger witness capsule fails closed if bubblewrap is unavailable. Science-shadow replication states never mutate canonical objects.

## V6 deployment invariant

The 2.5.0 release required package/server version alignment, V6 resource/tool exposure, constructive/adversarial tests, diagnostics, stdio V6 smoke, and a final CI-passing immutable runtime head before canonical promotion.
