from __future__ import annotations

import hashlib
import json
from typing import Any


CONTRACT_ARTIFACT = "ATHENA.SYNAPSE.MCP.BINDING.CONTRACT.V1"
ENDPOINT_IDENTITY_ARTIFACT = "ATHENA.FEDERATION.ENDPOINT.IDENTITY.V1"
SYNAPSE_MCP_CONTRACT = {
    "artifact": CONTRACT_ARTIFACT,
    "endpoint_identity_artifact": ENDPOINT_IDENTITY_ARTIFACT,
    "message_board": {
        "tool": "athena_message_board",
        "post_status": "POSTED",
        "post_delivery": "ROUTED_NOT_CONSUMED",
        "message_actor_field": "actor_endpoint_identity_digest",
        "message_recipient_field": "recipient_endpoint_identity_digests",
        "ack_status": "ACKED",
        "ack_actor_field": "actor_endpoint_identity_digest",
        "contract_digest_field": "synapse_contract_digest",
    },
}


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


SYNAPSE_MCP_CONTRACT_DIGEST = "sha256:" + hashlib.sha256(
    _canonical(SYNAPSE_MCP_CONTRACT).encode("utf-8")
).hexdigest()
