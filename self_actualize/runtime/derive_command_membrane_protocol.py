from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    ROOT = Path(__file__).resolve().parents[2]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from self_actualize.runtime.command_spine import (
        COMMAND_CAPILLARY_LAW_ID_V2,
        COMMAND_PACKET_SCHEMA_ID_V2,
        COMMAND_PROTOCOL_ID_V2,
        COMMAND_REWARD_FIELD_ID_V2,
        CommandMembraneService,
        read_json,
        rel,
    )
else:
    from .command_spine import (
        COMMAND_CAPILLARY_LAW_ID_V2,
        COMMAND_PACKET_SCHEMA_ID_V2,
        COMMAND_PROTOCOL_ID_V2,
        COMMAND_REWARD_FIELD_ID_V2,
        CommandMembraneService,
        read_json,
        rel,
    )
    ROOT = Path(__file__).resolve().parents[2]


SELF_ROOT = ROOT / "self_actualize"
DERIVATION_PATH = SELF_ROOT / "command_membrane_protocol_derivation.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def derive_command_membrane_protocol() -> dict[str, Any]:
    service = CommandMembraneService()
    artifacts = service.ensure_protocol_artifacts()
    public_state = service.sync_public_surfaces()
    protocol = read_json(service.config.protocol_json_path, {})
    schema = read_json(service.config.packet_schema_json_path, {})
    reward = read_json(service.config.reward_field_json_path, {})
    capillary = read_json(service.config.capillary_law_json_path, {})
    latency = read_json(service.config.latency_benchmark_json_path, {})

    result = {
        "generated_at": utc_now(),
        "truth": "OK",
        "protocol_id": protocol.get("protocol_id", COMMAND_PROTOCOL_ID_V2),
        "packet_schema_id": schema.get("schema_id", COMMAND_PACKET_SCHEMA_ID_V2),
        "reward_field_id": reward.get("law_id", COMMAND_REWARD_FIELD_ID_V2),
        "capillary_law_id": capillary.get("law_id", COMMAND_CAPILLARY_LAW_ID_V2),
        "latency_benchmark_id": latency.get("benchmark_id", ""),
        "docs_gate_status": protocol.get("docs_gate_status", ""),
        "docs_gate_detail": protocol.get("docs_gate", {}).get("detail", ""),
        "routing_policy": protocol.get("routing_defaults", {}).get("policy_id", ""),
        "compatibility_note": "Legacy swarm mirrors remain readable, but the NEXT57 command membrane stays subordinate to the LP-57 Omega control plane.",
        "public_state": {
            "active_surface": public_state.get("active_surface", ""),
            "watch_scope": public_state.get("watch_scope", ""),
            "queue_depth": public_state.get("queue_depth", 0),
            "active_membrane": public_state.get("active_membrane", ""),
            "last_event": public_state.get("last_event", {}),
        },
        "artifacts": {
            key: rel(Path(value)) if isinstance(value, (str, os.PathLike)) else value
            for key, value in artifacts.items()
        },
    }
    DERIVATION_PATH.parent.mkdir(parents=True, exist_ok=True)
    DERIVATION_PATH.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result


def main() -> int:
    print(json.dumps(derive_command_membrane_protocol(), indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
