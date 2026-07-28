# KC144 Hybrid Harness V8 — Release Gates and Conjugate Audit

V8 adds the missing published-runtime controls:

- deterministic source-span claim matrices;
- direct, inferred, and generated claim separation;
- source-lineage independence;
- contradiction preservation;
- conjugate audit receipts;
- bounded repair budgets;
- per-model circuit breakers;
- authority-neutral release-gate receipts;
- pull-request review receipts;
- FastMCP claim-matrix, audit, and gate tools.

## Release semantics

A release can be structurally **promotable** while remaining unpromoted:

```text
PROMOTABLE != PROMOTED
```

`I10_PROMOTION` and `M12_SUCCESSOR` are external, non-self-authorizing gates.
They remain HOLD and cannot be changed by test success.

## Run

```bash
cd MCP
PYTHONPATH=. python -m unittest discover -v -s tests
```

## Current boundary

```text
PRODUCTION STATUS  HOLD
AUTHORITY EFFECT   NONE
I10 RECEIPT        NONE
M12 CERTIFICATE    HOLD
```
