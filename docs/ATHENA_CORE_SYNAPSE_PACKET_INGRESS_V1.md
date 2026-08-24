# ATHENA Core SynapsePacket -> MCP Liminal Ingress Contract V1

## Integration boundary

This contract exercises a foreign `FEDERATION_SYNAPSE_PACKET_V1` envelope produced by `demeet2k/Athena#3431` against the shared-envelope ingress path implemented by MCP #379.

It does not add a new bus and does not change `synapse_liminal_adapter.py`. The MCP Liminal bridge remains the transport owner; Core remains the OID/fingerprint/typed-coordinate/claim owner; Guild Hall remains the `ATHENA.SYNAPSE.ENVELOPE.V1` owner.

## Observed mapping

For the frozen Core vector:

- envelope `CLAIM` -> Liminal `CLAIM`;
- envelope subject `OID-144` -> `goal_ref=OID-144`;
- Core packet return routes -> `dependency_refs`;
- foreign envelope parent IDs -> `synapse:<event-id>` causal refs;
- foreign event identity -> source-event ID and object reference only;
- Core target domains remain routing keys and never become MCP recipient identities;
- foreign recipient namespace is discarded at ingress;
- null/unknown foreign visibility is normalized to local `COLONY` visibility;
- evidence ceiling is reset to `SYNAPSE_ENVELOPE_ROUTING_STATE_ONLY`;
- output standing remains `PROPOSAL_ONLY_NO_RUNTIME_MUTATION`.

## Identity firewall

`FOREIGN_SYNAPSE_EVENT != LOCAL_LIMINAL_PACKET`.

The ingress plan never writes a `packet_id`, `parent_ids`, `reply_to`, `correction_of`, or `retraction_of` into the future local emit request from foreign envelope IDs. Foreign causality stays addressable as `causal_refs` only.

## Authority firewall

`FOREIGN_AUTHORITY != LOCAL_EXECUTION_AUTHORITY`.

The Core profile advertises `ZERO_AUTHORITY_INTEROP`; MCP still caps the ingress plan at routing state. The plan itself is read-only and does not establish delivery, consumption, incorporation, execution, truth, scheduling authority, or propagation.

## Verification

The frozen cross-repository vector lives at:

`tests/fixtures/athena_core_synapse_packet_envelope_v1.json`

Consumer regressions live at:

`tests/test_synapse_core_packet_profile_v1.py`

The tests cover the positive mapping plus namespace, causality, authority, visibility, tamper, and target-agent failure boundaries.
