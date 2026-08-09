# ATHENA Continuation Raw Observer V1

Artifact: `ATHENA.CONTINUATION.RAW.TRACE.V1`

## Purpose

Expose one read-only, replayable source boundary over continuation and coordination facts that the runtime already persists. The observer joins existing runtime metabolism to downstream evidence tooling without adding a scheduler, controller, classifier, treatment, or promotion path.

## Native sources

The observer reads only fixed Git-backed namespaces:

```text
prompts/rehydration/*/receipts/*.json
prompts/rehydration/*/events/*.json
runtime/message_board/v1/events/**/*.json
```

Accepted native artifacts are:

```text
ATHENA.REHYDRATION.RECEIPT.V1
ATHENA.REHYDRATION.EVENT.V1
ATHENA.MESSAGE.BOARD.EVENT.V1
```

Every returned source row binds:

```text
category
source_path
git_blob_sha
record_sha256
observed_at
record
```

The trace additionally binds exact current Git HEAD, a timezone-aware half-open window `[start,end)`, coverage status, malformed-source inventory, a record limit, and a deterministic trace digest.

## Fail-closed rules

```text
expected HEAD mismatch -> HOLD_STALE_GIT_HEAD
dirty Git root -> HOLD_DIRTY_GIT_ROOT
untracked source record -> TRACE_INTEGRITY_HOLD
invalid JSON -> TRACE_INTEGRITY_HOLD
artifact mismatch -> TRACE_INTEGRITY_HOLD
invalid/missing timezone -> TRACE_INTEGRITY_HOLD
record limit exceeded -> TRACE_INTEGRITY_HOLD
```

A partial/truncated trace is never silently represented as complete coverage.

## Authority membrane

The observer returns raw runtime facts only:

```text
classification = false
behavioral_effect = false
causal_effect = false
promotion = false
mutation = false
external_mutation_performed = false
```

Permanent laws:

```text
RAW_TRACE != ASSAY_CLASSIFICATION
RAW_RUNTIME_FACT != BEHAVIORAL_EFFECT
REHYDRATION_RECEIPT != USER_UI_EVENT
MESSAGE_BOARD_EVENT != COORDINATION_SUCCESS
TERMINAL_GATE_REJECTION != HUMAN_REENTRY_WITHOUT_EXPLICIT_CLASSIFIER
TRACE_DIGEST != SIGNATURE
TRACKED_FILE != WORLD_TRUTH
DIRTY_OR_MALFORMED_SOURCE => COVERAGE_HOLD
HALF_OPEN_WINDOW = [window_start, window_end)
READ_ONLY_OBSERVER != CONTROLLER
```

## Public MCP surface

Tool:

```text
athena_continuation_raw_trace
```

Inputs:

```text
window_start        required timezone-aware ISO-8601
window_end          required timezone-aware ISO-8601
expected_git_head   optional immutable 40-hex SHA CAS coordinate
max_records         optional [1,100000], default 50000
```

The tool is registered additively through the existing `PromptRuntime` composition membrane. It does not modify the central `Server.call_tool` switch and does not create a second runtime control plane.

## Downstream contract

Semantic/behavioral repositories may consume this trace only through an explicit validator/classifier that binds the exact trace digest and classification-policy digest. Any mapping from raw events into assay metrics is a separate semantic act and must retain residual/unknown fields when the runtime cannot observe the requested fact.
