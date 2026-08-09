# Liminal Beacon Mesh V1.1 — observed-failure repair candidate

**Standing:** `REPAIR_CANDIDATE_NON_AUTHORITATIVE`  
**Current implementation base:** `429a480a80eeefb9e2bff1ea3015adf571d76b0e`  
**Parent V1:** PR #279 / `87b5f3b34271e68f5c2d6e712ea8efeab49740df`  
**Observed behavioral witness:** issue #289 / CI `31306636702`  
**Repair contract:** issue #297

V1.1 preserves the process-local V1 carrier, identity, scope, receipt, reverse-consumer, bridge and opt-in autohook boundaries. It repairs only two defects observed by the frozen three-agent experiment.

## 1. Typed semantic handoff

Generic V1 autoshare remains unchanged when a tool result has no `_liminal_publish` field.

A tool may intentionally expose a strict machine-readable envelope:

```json
{
  "_liminal_publish": {
    "message_class": "CORRECTION",
    "summary": "D1 requires correction",
    "payload_ref": "event:C1",
    "changed_refs": ["event:C1"],
    "affected_refs": ["object:X"],
    "correction_of": "LBM...."
  }
}
```

Only these envelope keys are accepted: `message_class`, `summary`, `payload_ref`, `changed_refs`, `affected_refs`, `reply_to`, `correction_of`, `retraction_of`.

`CORRECTION` requires a local `correction_of` packet. `RETRACTION` requires a local `retraction_of` packet. Unknown keys, invalid types or missing lineage fail the communication share closed. The already-completed underlying tool call remains fail-open through the existing extension boundary.

The autohook never infers semantic lineage from arbitrary prose or ordinary top-level result fields and never broadcasts the complete result. Its evidence ceiling is fixed to `RUNTIME_METADATA_ONLY` and cannot be raised by the caller.

## 2. Bounded critical reserve

The V1 salience gate remains primary. A receiver may additionally admit a finite number of otherwise-filtered critical packets already selected by the base routing/context pass.

- parameter: `critical_quota`;
- default: `1`;
- hard cap: `2`;
- eligible classes: `BLOCKER`, `CORRECTION`, `RETRACTION`, `HANDOFF`;
- true reverse corrections/retractions remain separately protected by causal routing;
- scout quota remains separate;
- reserve packets still consume context budget and create only `PRESENTED` receipts;
- excess critical packets are filtered;
- direct addressing creates no additional bypass.

A critical label is routing metadata, not truth, evidence or authority.

## Observed parent result

The V1 frozen fixture improved matched discovery behavior (`missed delta 1.0 -> 0.0`, duplicates `1 -> 0`, discovery latency `30s -> 10s`, routine durable-write proxy `0`) but failed the complete behavioral guard because:

1. correction-like C1 did not preserve `correction_of(D1)` and therefore had reverse correction reach `0.0`;
2. an overloaded receiver filtered the scripted critical blocker.

Those failures justify this bounded repair but do not establish generalized causal benefit or permission for default activation.

## Firewalls

```text
STRUCTURED_SEMANTIC_ENVELOPE != TRUTH
SEMANTIC_ENVELOPE != EVIDENCE_PROMOTION
CORRECTION_OF != CORRECTION_ACCEPTED
AUTOHOOK != PROSE_INFERENCE
SEMANTIC_SHARE != FULL_RESULT_BROADCAST
CRITICAL_CLASS != AUTHORITY
CRITICAL_RESERVE != UNBOUNDED_BYPASS
DIRECT_RECIPIENT != ATTENTION_BYPASS
PRESENTED != CONSUMED
PROCESS_LOCAL_COLONY != FEDERATED_RUNTIME
REPAIR_TEST_PASS != GENERAL_CAUSAL_EFFECT
V1.1_CANDIDATE != DEFAULT_ACTIVATION
```
