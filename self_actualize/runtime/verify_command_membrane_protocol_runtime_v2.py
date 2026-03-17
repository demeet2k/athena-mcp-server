from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .derive_command_membrane_protocol_v2 import (
    CAPILLARY_LEDGER_PATH,
    CLAIM_FEED_PATH,
    COMMIT_FEED_PATH,
    ENTRYPOINT_PATH,
    EVENT_FEED_PATH,
    MANIFEST_V2_PATH,
    NEXT57_CAPILLARY_LAW_V2_PATH,
    NEXT57_LATENCY_V2_PATH,
    NEXT57_PACKET_SCHEMA_V2_PATH,
    NEXT57_PROTOCOL_V2_PATH,
    PROTOCOL_ID,
    REGISTRY_V2_PATH,
    REINFORCEMENT_FEED_PATH,
    ROUTE_FEED_PATH,
    ROUTING_POLICY,
    SIGMA_ROUTE_MIN,
    VERIFICATION_V2_PATH,
    derive_command_membrane_protocol_v2,
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def verify_command_membrane_protocol_runtime_v2() -> dict[str, Any]:
    derive_command_membrane_protocol_v2()

    registry = load_json(REGISTRY_V2_PATH)
    protocol = load_json(NEXT57_PROTOCOL_V2_PATH)
    schema = load_json(NEXT57_PACKET_SCHEMA_V2_PATH)
    capillary = load_json(NEXT57_CAPILLARY_LAW_V2_PATH)
    latency = load_json(NEXT57_LATENCY_V2_PATH)
    manifest = MANIFEST_V2_PATH.read_text(encoding="utf-8")

    required_packet_fields = {
        "event_id",
        "source_root",
        "relative_path",
        "detected_by",
        "goal",
        "change",
        "priority",
        "confidence",
        "earth_ts_utc",
        "earth_anchor",
        "liminal_ts",
        "coord12",
        "parent_event_id",
        "ttl",
        "pheromone",
        "state_hash",
        "route_class",
        "witness_ptr",
        "replay_ptr",
    }
    required_claim_fields = {
        "claim_id",
        "event_id",
        "ant_id",
        "role",
        "lease_ms",
        "lease_expires_at",
        "claim_source_event",
        "route_path",
        "claim_rank",
        "claim_mode",
    }
    required_route_fields = {
        "event_id",
        "policy_id",
        "candidate_targets",
        "selected_targets",
        "ranked_routes",
        "route_inputs",
        "topk",
        "claim_mode",
        "quorum",
        "route_path",
        "worker_choice",
        "generated_at",
    }
    required_commit_fields = {
        "event_id",
        "claim_ant_id",
        "result",
        "route_path",
        "detection_latency_ms",
        "swarm_awareness_latency_ms",
        "claim_latency_ms",
        "resolution_latency_ms",
        "capillary_score",
        "t_sugar_ms",
        "liminal_distance",
        "liminal_velocity",
        "replay_ptr",
        "committed_at",
    }
    required_capillary_fields = {
        "edge_id",
        "from_node",
        "to_node",
        "strength",
        "usefulness_score",
        "success_count",
        "failure_count",
        "latency_avg_ms",
        "noise_count",
        "last_used_at",
        "class",
    }

    packet_types = registry.get("packet_types", {})
    packet_fields = set(packet_types.get("CommandEventPacketV2", {}).get("required_fields", []))
    claim_fields = set(packet_types.get("ClaimLeaseV2", packet_types.get("ClaimLeaseV1", {})).get("required_fields", []))
    route_fields = set(packet_types.get("RouteDecisionV2", {}).get("required_fields", []))
    commit_fields = set(packet_types.get("CommitReceiptV2", {}).get("required_fields", []))
    capillary_fields = set(packet_types.get("CapillaryEdgeV2", {}).get("required_fields", []))

    checks = {
        "protocol_id_match": registry.get("protocol_id") == PROTOCOL_ID,
        "entrypoint_exists": ENTRYPOINT_PATH.is_file(),
        "docs_gate_honest": registry.get("docs_gate", {}).get("state") == "BLOCKED"
        and registry.get("docs_gate", {}).get("reason") == "blocked-by-missing-credentials",
        "policy_frozen": registry.get("routing_policy", {}).get("policy_id") == ROUTING_POLICY
        and registry.get("routing_policy", {}).get("selector_terms") == ["goal", "salience", "pheromone", "coord", "availability"],
        "routing_boundary": registry.get("routing_boundary", {}).get("sigma_route_min") == SIGMA_ROUTE_MIN
        and registry.get("routing_boundary", {}).get("hub_budget") == 6,
        "routing_defaults": registry.get("defaults", {}).get("topk") == 5
        and registry.get("defaults", {}).get("quorum") == 1
        and registry.get("defaults", {}).get("ttl") == 6
        and registry.get("defaults", {}).get("default_lease_ms") == 1200
        and registry.get("defaults", {}).get("claim_mode") == "first-lease",
        "board_caps": registry.get("board_caps", {}).get("guild_hall_visible_max") == 8
        and registry.get("board_caps", {}).get("temple_visible_max") == 8,
        "packet_fields_present": required_packet_fields.issubset(packet_fields),
        "claim_fields_present": required_claim_fields.issubset(claim_fields),
        "route_fields_present": required_route_fields.issubset(route_fields),
        "commit_fields_present": required_commit_fields.issubset(commit_fields),
        "capillary_fields_present": required_capillary_fields.issubset(capillary_fields),
        "edge_classes": registry.get("capillary_reinforcement", {}).get("edge_classes") == ["weak", "capillary", "vein"],
        "coord12_keys": schema.get("coord12_keys") == [
            "earth_utc_anchor",
            "earth_rotation_phase",
            "earth_orbital_phase",
            "earth_geospatial_anchor",
            "solar_phase",
            "lunar_phase",
            "local_sidereal_phase",
            "canonical_sky_anchor",
            "runtime_region",
            "queue_pressure",
            "goal_salience_vector",
            "change_novelty_vector",
        ],
        "protocol_mirror_consistency": protocol.get("mirror_of") == PROTOCOL_ID
        and protocol.get("routing_policy", {}).get("policy_id") == ROUTING_POLICY,
        "capillary_mirror_consistency": capillary.get("mirror_of") == PROTOCOL_ID
        and capillary.get("edge_classes") == ["weak", "capillary", "vein"],
        "latency_mirror_consistency": latency.get("mirror_of") == PROTOCOL_ID
        and latency.get("formula") == "T_sugar = T_detect + T_encode + T_route + T_claim + T_commit",
        "feed_family_exists": all(
            path.exists()
            for path in [
                EVENT_FEED_PATH,
                ROUTE_FEED_PATH,
                CLAIM_FEED_PATH,
                COMMIT_FEED_PATH,
                REINFORCEMENT_FEED_PATH,
                CAPILLARY_LEDGER_PATH,
            ]
        ),
        "manifest_mentions_lifecycle": "detect -> encode -> route -> claim -> commit -> reinforce" in manifest
        and "GLOBAL COMMAND -> Scout -> Router -> Worker -> Archivist" in manifest
        and "Docs gate: `BLOCKED`" in manifest,
    }

    result = {
        "generated_at": utc_now(),
        "truth": "OK" if all(checks.values()) else "NEAR",
        "checks": checks,
        "protocol_id": registry.get("protocol_id"),
        "registry_path": str(REGISTRY_V2_PATH),
        "manifest_path": str(MANIFEST_V2_PATH),
    }
    VERIFICATION_V2_PATH.parent.mkdir(parents=True, exist_ok=True)
    VERIFICATION_V2_PATH.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def main() -> int:
    print(json.dumps(verify_command_membrane_protocol_runtime_v2(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
