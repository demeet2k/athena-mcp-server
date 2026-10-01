# ATHENA Synapse ↔ Liminal Beacon Bridge V1

This bridge connects the existing process-local Liminal Beacon Mesh to the shared `ATHENA.SYNAPSE.ENVELOPE.V1` boundary without creating a second communication bus.

## Export surfaces

### Packet capsule

`athena_synapse_liminal_export_packet` projects the existing public Liminal packet capsule into profile `LIMINAL_BEACON_CAPSULE_V1`.

The projection is deliberately `LOSSY_AUX` relative to the full ephemeral packet. Public capsule fields are preserved; runtime-only/full-packet fields such as route-index keys, reverse targets, capabilities, needs/offers/provides and capacity metadata are declared lost. `athena://liminal/beacon-mesh` is the return token for native reconstruction/readback.

The packet's process-local `event_seq` is exported only as an origin-local sequence. Its Lamport/parent/correction/retraction structure remains native packet data and explicit cross-envelope causal edges. Wall time is not promoted into causal order.

### Recipient receipt

`athena_synapse_liminal_export_receipt` projects an explicit native receipt record into profile `LIMINAL_BEACON_RECEIPT_V1`.

Receipt projection is `LOSSLESS` relative to that receipt record. The causal chain is explicit:

`packet → PRESENTED → CONSUMED → INCORPORATED → DECISION_CHANGED → PROPAGATED`

A stage export references the packet and, after `PRESENTED`, the immediately prior receipt-stage envelope. The bridge never infers a stage merely because a packet was routed.

## Source revision

Cross-repository identity requires the MCP source revision that produced the native runtime event. Export therefore requires either the explicit `source_revision` tool argument or `ATHENA_MCP_SOURCE_REVISION`.

Missing source revision is a HOLD:

`SYNAPSE_SOURCE_REVISION_REQUIRED_HOLD`

The bridge does not substitute `server.git.head()` because that Git checkout may be a state/coordination repository rather than the MCP package revision.

## Ingress

`athena_synapse_liminal_plan_ingress` validates and translates a foreign Synapse envelope but performs **no runtime mutation**.

`athena_synapse_liminal_ingest` is the explicit mutation operator. It feeds the plan into the existing `LiminalBeaconMeshRuntime.emit()` and therefore creates one **new local ephemeral coordination signal**. It never claims that the local Liminal packet is the foreign source event.

Foreign Synapse causal IDs are retained as `causal_refs`; they are not forged into native Liminal `parent_ids`, `correction_of`, or `retraction_of`, because the native packet hash is not invertible to a foreign source identity. Likewise, foreign recipient IDs are not assumed to name local Liminal agents.

## Truth and authority firewalls

- `EXPORT != DELIVERY != CONSUMPTION`
- `INGRESS_PLAN != RUNTIME_MUTATION`
- `INGEST != SOURCE_EVENT_IDENTITY`
- `INGEST != CONSUMPTION`
- `INGEST != EXECUTION_AUTHORITY`
- `FOREIGN_CAUSAL_ID != LOCAL_PACKET_PARENT`
- `FOREIGN_RECIPIENT_NAMESPACE != LOCAL_AGENT_NAMESPACE`
- `ROUTING_STATE != WORLD_TRUTH`

The bridge carries coordination state only. It does not promote foreign authority, evidence standing, truth, assignment, merge permission, or execution permission.

## Review dependency

The canonical shared schema/conformance source of truth is proposed in `demeet2k/guild-hall#27`. The companion Core adapter is proposed in `demeet2k/Athena#3413`.
