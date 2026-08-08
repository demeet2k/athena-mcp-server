# ATHENA COLLECTIVE RUNTIME V2 — PERSISTENT ORGANIZATIONAL MEMORY

V2 closes the largest persistence/learning residuals from Collective Runtime V1 and Collective Growth V1. It adds durable stigmergic priority, typed JSPACE-derived invalidation transport, empirical RGO calibration, transactional collective topology with rollback witnesses, and a reusable failure-antibody registry.

## Authority boundary

`COLLECTIVE_RUNTIME_V2` is a persistent control plane, not a hidden rewrite channel.

- canonical semantic mutation still requires ATHENA expected-VID CAS;
- Git persistence still requires Git-head CAS;
- collective topology has its own expected-version CAS;
- collective topology transactions do not silently mutate canonical JSPACE;
- empirical calibration records observations but does not retroactively falsify historical outputs;
- failure antibodies are reusable operational memory, not proof that a new event has the same cause.

## 1. Persistent stigmergic field

For route/artifact key `r`, durable priority evolves through the existing stigmergic law:

`rho = exp(-lambda * age)`

`evaporated = p_t * rho`

`deposit = weighted(quality, novelty, evidence, reuse, bridge_value, downstream_gain) - penalties(staleness, contradiction)`

`p_(t+1) = clamp(evaporated + gain * deposit * available_headroom)`.

The persistent table stores current score, version, last observation, actor, and timestamps. Reuse/evidence can therefore make a path easier to retrieve, while age/staleness/contradiction can remove inherited routing privilege.

Tools:

- `athena_pheromone_reinforce`
- `athena_pheromone_field`

## 2. JSPACE dependency compiler

`athena_jspace_alarm` reads the canonical JSPACE edge table and compiles only relations whose invalidation orientation is known.

Default orientation examples:

- `A DEPENDS_ON B` => reverse for invalidation: failure of B propagates toward A;
- `A REQUIRES B` => reverse;
- `A DERIVED_FROM B` => reverse;
- `A SUPPORTED_BY B` => reverse;
- `A USES B` => reverse;
- `A IMPLIES B` => outbound;
- unknown relation => IGNORE unless the caller supplies an explicit mode.

For a propagated severity:

`s_(h+1) = s_h * edge_weight * hop_decay`.

Propagation is bounded by hop count and severity threshold. This changes the prior Growth-V1 alarm from caller-supplied graph transport into typed JSPACE-derived transport while refusing to invent semantics for unknown relation types.

## 3. Observational RGO calibration

Predicted organization quality is not self-certifying.

Each completed organization can record:

`e_t = observed_RGO_t - predicted_RGO_t`.

The runtime stores sufficient statistics:

`n, sum(pred), sum(obs), sum(pred^2), sum(pred*obs), sum(|error|)`.

It derives a linear calibration surface and shrinks it toward the identity predictor according to sample reliability:

`reliability = n / (n + 10)`.

Low-sample history therefore cannot violently rewrite the predictor; accumulated observations increasingly influence the calibrated estimate.

Tools:

- `athena_rgo_observe`
- `athena_rgo_calibrate`

The calibration layer corrects prediction bias. It does not yet learn the full internal cost/output coefficient vector.

## 4. Transactional collective topology

A collective control topology is:

`T = <modules, bridges, meta, version>`.

Every write requires:

`expected_version == current_version`.

Otherwise the runtime returns `STALE_TOPOLOGY` as a failed operation.

Supported operations:

- `INIT`
- `REPLACE`
- `FISSION`
- `FUSE`
- `PATCH_MODULE`

Each committed mutation records:

`TX = <txid, topology_id, from_version, to_version, operation, before, after, actor, time>`.

FISSION preserves the parent as an inactive reference and creates active children with `fission_parent` lineage. FUSE preserves source modules as inactive references, creates the fused module, and can rewire external bridges to the new module. Required historical identity is therefore retained rather than destructively overwritten.

Rollback is itself a new transaction:

`ROLLBACK(txid)` restores the selected transaction's `before` state under current-version CAS and increments topology version. History is never erased.

Tools:

- `athena_topology_get`
- `athena_topology_apply`
- `athena_topology_rollback`

## 5. Failure antibodies

A material diagnosed failure becomes:

`AB = <signature, scope, trigger, detector, repair, evidence, regression_refs, hits>`.

Registration is deterministic by `scope + normalized signature`, allowing a known antibody to be upgraded rather than duplicated.

Matching uses detector keywords when supplied, otherwise signature tokens. A match returns the stored repair, evidence surface, and regression/replay references so a future agent can reuse the defense and rerun its witness.

Tools:

- `athena_failure_antibody_register`
- `athena_failure_antibody_match`

An antibody match is a routing hypothesis, not causal proof. The witness/regression should still be executed when relevant.

## 6. MAXDEV integration

The MAXDEV prompt now performs the following additional cycle:

`HYDRATE -> PHEROMONE/FALSE-PATH MEMORY -> FAILURE-ANTIBODY MATCH -> PLAN -> RGO CALIBRATION -> EXECUTE -> JSPACE ALARM IF INVALIDATED -> TOPOLOGY CAS IF STRUCTURAL -> PHEROMONE REINFORCEMENT -> FAILURE ANTIBODY REGISTRATION -> OBSERVED RGO -> FINALIZE/COMMIT`.

Resource:

`athena://collective/v2`.

## 7. Remaining V3 residuals

Not claimed as implemented in V2:

1. learning the full organization cost/output coefficient vector rather than only output calibration;
2. automatic causal validation of JSPACE relation orientation beyond explicit typed rules;
3. direct transactional projection of accepted collective topology mutations into canonical JSPACE under semantic/Git CAS;
4. counterfactual A/B simulation of candidate organizations before topology mutation;
5. longitudinal elder/cultural authority derived from repeated prediction, reuse and repair success;
6. automatic compute/token/tool-time accounting attached to each worker and organization;
7. antibody expiry/variant families and automatic regression execution;
8. multi-scale pheromone fields spanning token/object/module/system coordinates.
