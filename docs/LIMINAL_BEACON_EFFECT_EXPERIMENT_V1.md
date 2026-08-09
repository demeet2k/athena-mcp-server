# Liminal Beacon Effect Experiment V1

**Contract:** #289  
**Execution PR:** #290  
**Semantic parent:** Beacon runtime candidate #279 at `87b5f3b34271e68f5c2d6e712ea8efeab49740df`  
**Frozen before results:** yes  
**Runtime code modified by this experiment:** no  
**Standing:** deterministic matched fixture; not general causal evidence

## Question

Does the current Liminal Beacon V1 autohook reduce missed sibling deltas / duplicate work under the frozen three-agent fixture while preserving attention, scope, correction, persistence and compatibility boundaries?

## Arms

`B0`: deliberate manual Message-Board surrogate with one frozen poll at `t=40`.

`B1`: current process-local Beacon autohook for primary crossings. The primary discovery and primary correction are **not** rescued with manual semantic Beacon emits. Explicit cognition receipts are allowed because the protocol requires them to distinguish presentation from consumption/incorporation.

## Critical discriminator

The current V1 autohook emits bounded tool-result metadata and event references, but does not infer `correction_of(D1)` from arbitrary result metadata. The experiment intentionally tests whether a correction-like C1 can reach B through the **reverse-consumer causal route** after B leaves the original topology.

A C1 capsule appearing through the scout channel does not count as reverse correction reach.

Therefore:

```text
SCOUT_PRESENTATION != REVERSE_CORRECTION_REACH
EXPERIMENT_FAIL != CI_FAIL
```

A CI-green experiment whose frozen comparison returns `FAIL` is a valid observed negative result and should generate the next repair hypothesis rather than a rewritten scoring rule.

## Frozen primary rule

Full PASS requires all of:

1. challenger missed-delta rate <= baseline;
2. challenger duplicate action count <= baseline;
3. scripted reverse correction reach = 1.0;
4. no stale/scope-invalid presentation;
5. no existing-tool regression under the parent CI witness;
6. no durable Git write from routine fast-plane activity;
7. context bytes/useful consumed packet <= 1.5× baseline when both denominators are observed;
8. at least one strict primary improvement in missed delta, duplicate action, or discovery latency.

Any false required criterion -> `FAIL`. Any required unknown with no false criterion -> `PARTIAL_UNKNOWN`. Otherwise -> `PASS`.

## Additional probes

- high-threshold low-salience filtering;
- high-threshold critical blocker passage;
- direct-recipient backpressure;
- cross-guild scope isolation;
- process-local implicit epoch rotation on rebind;
- hidden/independent process count stays `UNKNOWN`.

## Artifacts

- `tests/fixtures/liminal_beacon_effect_v1.json`
- `scripts/liminal_beacon_effect_v1.py`
- `tests/test_liminal_beacon_effect_experiment_v1.py`

## Execution-base note

Repository CI is filtered to PRs targeting `master`. PR #290 may therefore be temporarily based on master solely to obtain the standard execution witness, then returned to its semantic parent branch after scoring.

`TEMPORARY_CI_BASE != INTEGRATION_INTENT != MERGE_AUTHORITY`.
