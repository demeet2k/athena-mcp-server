# Federation Ephemeral Cursor Bridge V1

This bridge connects the ATHENA Federation cursor-bound handoff model to the existing MCP ephemeral request/poll membrane without identifying their cursors.

## Type distinction

The MCP coordination membrane exposes a monotonically increasing **process-local SQLite event cursor**. It is useful for polling, changed-since checks, and bounded replay. Garbage collection can truncate its replay history.

The Federation cursor identifies an exact supplied append-only **source prefix** under a source epoch. It is used to decide whether a handoff was derived from a source occurrence admitted by the consumer.

These are related but not isomorphic objects:

```text
MCP process cursor != Federation source cursor
changed_since_cursor != source-prefix proof
transport freshness != provider currentness
```

The bridge therefore declares `LOSSY_AUX`, not `LOSSLESS`.

## Wire projection

`athena_ephemeral_federation_post` encodes two identities into the existing `packet_digest_or_ref` carrier:

```text
handoff_digest
source_cursor_digest
```

The full Federation handoff is **not** copied into SQLite. Its canonical `handoff_digest` is the reconstruction token. The consumer must reconstruct/read the full handoff through the durable Federation surface and run Federation cursor admission there.

The MCP `causal_parents` field remains untouched. A Federation source cursor is not silently inserted as a causal parent.

## Receive path

`athena_ephemeral_federation_poll` delegates to the existing bounded poll and decodes only packets using the Federation bridge reference form.

Each decoded row is returned as:

```text
TRANSPORT_OBSERVED_REQUIRES_FEDERATION_CURSOR_ADMISSION
```

If the MCP replay window has been truncated, the bridge also returns:

```text
HOLD_TRANSPORT_REPLAY_TRUNCATED
```

That HOLD is about transport-history continuity. It is not evidence that the Federation source changed.

## Consumption witness

After the durable Federation layer has produced an exact cursor-admission receipt, `athena_ephemeral_federation_witness` builds a typed witness containing:

```text
handoff_digest
source_cursor_digest
federation_admission_receipt_digest
consumer_ref
projection_loss_class = LOSSY_AUX
authority = NONE
```

That witness may then be supplied to the existing MCP receipt ladder. The witness tool does not mint or simulate Federation admission.

## Delivery semantics

The two protocols retain separate stages:

```text
MCP ROUTED
MCP DELIVERED
MCP PRESENTED
Federation cursor admission
MCP CONSUMED
MCP INCORPORATED
MCP DECISION_CHANGED
```

No stage implies a later stage.

```text
ROUTED != DELIVERED != CONSUMED != APPLIED
MCP receipt != source currentness
MCP route != Federation admission
```

## Deployment boundary

This source bridge inherits the existing MCP membrane's deployment ceiling. Repository implementation does not prove that multiple agents share the same process-local SQLite runtime or that these tools are exposed in a deployed product instance.
