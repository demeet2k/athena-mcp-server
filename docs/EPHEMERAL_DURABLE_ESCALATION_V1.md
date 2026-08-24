# ATHENA Ephemeral → Durable Escalation V1

`ATHENA.EPHEMERAL.DURABLE.ESCALATION.1` closes one already-declared coordination seam:

```text
process-local EphemeralCoordinationRuntime
        MATERIAL_CANDIDATE
              ↓ explicit caller action
Git-backed Message Board MESSAGE event
```

It does **not** create a second fast plane or a second durable coordination authority. The bridge reuses the existing `EphemeralCoordinationRuntime` owned by `AorDevelopmentSurface` and the existing Git-backed `MessageBoardRuntime` mutation path.

## Operations

- `athena_ephemeral_durable_plan` — validates the source packet, actor role, optional recipient receipt threshold, durable Message Board actor, route, and shared frontier without mutation.
- `athena_ephemeral_durable_escalate` — revalidates on the Message Board's fresh shared frontier and appends one idempotent durable `MESSAGE` event.

Resource: `athena://coordination/ephemeral-durable-bridge/v1`.

## Identity boundary

The caller supplies both an ephemeral AID and a durable Message Board agent ID plus an opaque `actor_binding_ref`. The bridge never turns that reference into identity proof:

```text
EPHEMERAL_AID != MESSAGE_BOARD_AGENT_ID
CALLER_BINDING_REF != IDENTITY_PROOF
```

The durable actor must already have an active Message Board claim. Escalation never creates presence, claims, assignments, or execution authority.

## Receipt boundary

A source sender may escalate only at `ROUTED`. A recipient may require an explicit minimum receipt stage:

```text
ROUTED
→ DELIVERED
→ PRESENTED
→ CONSUMED
→ INCORPORATED
→ DECISION_CHANGED
```

The observed stage is recorded; no missing stage is inferred.

## Federation composition

When `packet_digest_or_ref` is an `athena-federation-handoff-v1` projection from the parent Federation bridge, the durable packet records the handoff digest, source-cursor digest, LOSSY_AUX standing, and reconstruction token. It explicitly preserves:

```text
FEDERATION_SOURCE_CURSOR != MCP_PROCESS_CURSOR
MCP_ROUTE != FEDERATION_ADMISSION
FEDERATION_PROJECTION != SOURCE_CURRENTNESS_PROOF
```

This creates a lawful path:

```text
Federation source-cursor-bound handoff
  → LOSSY_AUX process-local ephemeral projection
  → explicit MATERIAL_CANDIDATE durable escalation
  → Git Message Board route
```

without turning any transport step into provider currentness, consumption, truth, or execution.

## Idempotency

The escalation identity is deterministically bound to:

- source ephemeral packet ID;
- explicit ephemeral actor AID + role;
- opaque actor binding reference;
- durable Message Board actor;
- explicit durable recipients;
- minimum receipt threshold;
- optional note.

An exact replay returns the already-existing durable event rather than appending a second message. Once the first durable return exists, an exact replay may still resolve after the ephemeral source TTL has expired.

## Authority ceiling

```text
MATERIAL_CANDIDATE != DURABLE_CLAIM_OR_TRUTH
MESSAGE_BOARD_ROUTE != CONSUMPTION
DURABLE_ESCALATION != CLAIM != ASSIGNMENT != EXECUTION_AUTHORITY
```

The bridge's only write authority is the pre-existing Message Board write path, including its shared-frontier verification and CAS/publish behavior.
