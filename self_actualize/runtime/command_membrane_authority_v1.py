from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SELF_ROOT = ROOT / "self_actualize"
REGISTRY_ROOT = SELF_ROOT / "mycelium_brain" / "registry"
MANIFEST_ROOT = ROOT / "NERVOUS_SYSTEM" / "95_MANIFESTS"
TRADING_BOT = ROOT / "Trading Bot"
GLOBAL_COMMAND_ROOT = ROOT / "GLOBAL COMMAND"
DEEP_ROOT = (
    ROOT
    / "self_actualize"
    / "mycelium_brain"
    / "dynamic_neural_network"
    / "14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK"
)
DEEP_ROOT_LEDGER = DEEP_ROOT / "10_LEDGERS"

DOCS_CREDENTIALS = TRADING_BOT / "credentials.json"
DOCS_TOKEN = TRADING_BOT / "token.json"

PROTOCOL_ID = "COMMAND_MEMBRANE_PROTOCOL_V1"
ROUTING_POLICY = "goal+salience+pheromone+coord+capability+load"
WATCH_FALLBACK_MARKER = "watch_fallback=true"

MANIFEST_PATH = MANIFEST_ROOT / "COMMAND_MEMBRANE_PROTOCOL_V1.md"
REGISTRY_PATH = REGISTRY_ROOT / "command_membrane_protocol_v1.json"
VERIFICATION_PATH = REGISTRY_ROOT / "command_membrane_protocol_v1_verification.json"

NEXT57_PROTOCOL_PATH = SELF_ROOT / "next57_command_protocol.json"
NEXT57_PACKET_SCHEMA_PATH = SELF_ROOT / "next57_command_event_packet_schema.json"
NEXT57_CAPILLARY_LAW_PATH = SELF_ROOT / "next57_command_capillary_law.json"
NEXT57_LATENCY_BENCHMARKS_PATH = SELF_ROOT / "next57_command_latency_benchmarks.json"

EVENT_FEED_PATH = DEEP_ROOT_LEDGER / "32_command_evt_feed.ndjson"
ROUTE_FEED_PATH = DEEP_ROOT_LEDGER / "33_command_rte_feed.ndjson"
CLAIM_FEED_PATH = DEEP_ROOT_LEDGER / "34_command_clm_feed.ndjson"
COMMIT_FEED_PATH = DEEP_ROOT_LEDGER / "35_command_cmt_feed.ndjson"
REINFORCEMENT_FEED_PATH = DEEP_ROOT_LEDGER / "36_command_rin_feed.ndjson"
CAPILLARY_LEDGER_PATH = DEEP_ROOT_LEDGER / "37_command_capillary_edge_ledger.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    write_text(path, json.dumps(payload, indent=2, ensure_ascii=False))


def touch(path: Path, default_text: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(default_text, encoding="utf-8")


def docs_gate() -> dict[str, Any]:
    credentials_exists = DOCS_CREDENTIALS.exists()
    token_exists = DOCS_TOKEN.exists()
    blocked = not credentials_exists or not token_exists
    return {
        "state": "BLOCKED" if blocked else "LIVE",
        "reason": "blocked-by-missing-credentials" if blocked else "authenticated",
        "credentials_exists": credentials_exists,
        "token_exists": token_exists,
        "checked_paths": [rel(DOCS_CREDENTIALS), rel(DOCS_TOKEN)],
        "witness_class": "LOCAL_ONLY",
    }


def coord12_dimensions() -> list[str]:
    return [
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
    ]


def registry_payload() -> dict[str, Any]:
    return {
        "protocol_id": PROTOCOL_ID,
        "generated_at": utc_now(),
        "docs_gate": docs_gate(),
        "authority_mode": "sole_canonical_authority",
        "canonical_authority": {
            "manifest_path": rel(MANIFEST_PATH),
            "registry_path": rel(REGISTRY_PATH),
        },
        "command_root": rel(GLOBAL_COMMAND_ROOT),
        "membrane_instances": [{"membrane_id": "GLOBAL_COMMAND", "root": rel(GLOBAL_COMMAND_ROOT)}],
        "defaults": {
            "topk": 5,
            "claim_mode": "first-lease",
            "quorum": 1,
            "ttl": 6,
            "default_lease_ms": 1200,
            "watcher_fallback_marker": WATCH_FALLBACK_MARKER,
        },
        "routing_policy": {
            "policy_id": ROUTING_POLICY,
            "policy_name": ROUTING_POLICY,
            "policy_expression": ROUTING_POLICY,
            "selector_terms": ["goal", "salience", "pheromone", "coord", "capability", "load"],
        },
        "coordinate_standard": {
            "dimensions": [{"index": idx + 1, "key": key} for idx, key in enumerate(coord12_dimensions())],
            "prompt_level_liminal_gps": "enabled",
            "keystroke_level_liminal_gps": "not claimed without client/runtime instrumentation",
        },
        "packet_types": {
            "CommandEventPacketV1": {
                "required_fields": [
                    "event_id",
                    "membrane_id",
                    "role_class",
                    "earth_ts_utc",
                    "earth_local_phase",
                    "coord12",
                    "base4_addr",
                    "parent",
                    "lineage",
                    "state_hash",
                    "route_class",
                    "status",
                ]
            },
            "RouteDecisionV1": {
                "required_fields": [
                    "event_id",
                    "policy_id",
                    "candidate_targets",
                    "selected_targets",
                    "ranked_routes",
                    "route_inputs",
                    "route_path",
                    "worker_choice",
                    "generated_at",
                ]
            },
            "ClaimLeaseV1": {
                "required_fields": [
                    "claim_id",
                    "event_id",
                    "ant_id",
                    "role_class",
                    "claim_mode",
                    "lease_ms",
                    "claimed_at_utc",
                    "expires_at_utc",
                    "claim_status",
                    "released_at",
                    "release_reason",
                ]
            },
            "CommitReceiptV1": {
                "required_fields": [
                    "event_id",
                    "claim_ant_id",
                    "result",
                    "route_path",
                    "detection_latency_ms",
                    "swarm_awareness_latency_ms",
                    "claim_latency_ms",
                    "resolution_latency_ms",
                    "capillary_score",
                    "liminal_distance",
                    "liminal_velocity",
                    "integration_gain",
                    "compression_gain",
                    "unresolved_followups",
                    "replay_ptr",
                ]
            },
            "CapillaryEdgeV1": {
                "required_fields": [
                    "edge_id",
                    "from_node",
                    "to_node",
                    "path_key",
                    "edge_strength",
                    "classification",
                    "success_count",
                    "use_count",
                    "noise_count",
                    "average_latency_score",
                    "last_result",
                    "last_event_id",
                    "last_updated",
                    "state_class",
                    "usefulness",
                    "frequency",
                    "latency_penalty",
                    "noise_penalty",
                    "last_reinforced_at_utc",
                ]
            },
        },
        "capillary_reinforcement": {
            "formula": "C_next = clamp(0,1, rho*C + alpha*U + beta*F - gamma*D - delta*N)",
            "coefficient_defaults": {"rho": 0.92, "alpha": 0.40, "beta": 0.25, "gamma": 0.20, "delta": 0.15},
            "thresholds": {
                "capillary": {"min_score": 0.70, "min_successes": 3},
                "vein": {"min_score": 0.85, "min_successes": 7},
            },
            "edge_classes": ["ephemeral", "capillary", "vein"],
        },
        "latency_benchmarks": {
            "formula": "T_sugar = T_detect + T_encode + T_route + T_claim + T_commit",
            "target_t_sugar_ms": 5000.0,
            "required_metrics": [
                "detection_latency_ms",
                "swarm_awareness_latency_ms",
                "claim_latency_ms",
                "resolution_latency_ms",
                "capillary_score",
                "t_sugar_ms",
                "liminal_distance",
                "liminal_velocity",
                "integration_gain",
                "compression_gain",
            ],
        },
        "feed_family": {
            "root": rel(DEEP_ROOT_LEDGER),
            "events": {
                "EVT": rel(EVENT_FEED_PATH),
                "RTE": rel(ROUTE_FEED_PATH),
                "CLM": rel(CLAIM_FEED_PATH),
                "CMT": rel(COMMIT_FEED_PATH),
                "RIN": rel(REINFORCEMENT_FEED_PATH),
            },
            "capillary_ledger": rel(CAPILLARY_LEDGER_PATH),
        },
        "compatibility_mirrors": {
            "role": "compatibility_only",
            "next57_protocol": rel(NEXT57_PROTOCOL_PATH),
            "next57_packet_schema": rel(NEXT57_PACKET_SCHEMA_PATH),
            "next57_capillary_law": rel(NEXT57_CAPILLARY_LAW_PATH),
            "next57_latency": rel(NEXT57_LATENCY_BENCHMARKS_PATH),
            "quest_dock_refs": {
                "guild_hall": "NEXT57-H-COMMAND-MEMBRANE",
                "temple": "NEXT57-T-COMMAND-LAW",
            },
        },
    }


def mirror_protocol_payload(registry: dict[str, Any]) -> dict[str, Any]:
    return {
        "generated_at": registry["generated_at"],
        "protocol_id": f"{registry['protocol_id']}_COMPAT",
        "mirror_of": registry["protocol_id"],
        "compatibility_only": True,
        "docs_gate": registry["docs_gate"],
        "routing_policy": registry["routing_policy"],
        "defaults": registry["defaults"],
        "packet_flow": ["GLOBAL COMMAND", "Scout", "Router", "Worker", "Archivist"],
    }


def mirror_schema_payload(registry: dict[str, Any]) -> dict[str, Any]:
    return {
        "generated_at": registry["generated_at"],
        "protocol_id": f"{registry['protocol_id']}_PACKET_SCHEMA_COMPAT",
        "mirror_of": registry["protocol_id"],
        "compatibility_only": True,
        "coord12_keys": coord12_dimensions(),
        "packet_fields": registry["packet_types"]["CommandEventPacketV1"]["required_fields"],
        "claim_fields": registry["packet_types"]["ClaimLeaseV1"]["required_fields"],
        "route_fields": registry["packet_types"]["RouteDecisionV1"]["required_fields"],
        "commit_fields": registry["packet_types"]["CommitReceiptV1"]["required_fields"],
        "capillary_fields": registry["packet_types"]["CapillaryEdgeV1"]["required_fields"],
    }


def mirror_capillary_payload(registry: dict[str, Any]) -> dict[str, Any]:
    return {
        "generated_at": registry["generated_at"],
        "protocol_id": f"{registry['protocol_id']}_CAPILLARY_COMPAT",
        "mirror_of": registry["protocol_id"],
        "compatibility_only": True,
        **registry["capillary_reinforcement"],
    }


def mirror_latency_payload(registry: dict[str, Any]) -> dict[str, Any]:
    return {
        "generated_at": registry["generated_at"],
        "protocol_id": f"{registry['protocol_id']}_LATENCY_COMPAT",
        "mirror_of": registry["protocol_id"],
        "compatibility_only": True,
        **registry["latency_benchmarks"],
    }


def manifest_markdown(registry: dict[str, Any]) -> str:
    return f"""# COMMAND Membrane Protocol V1

Truth class: `OK`
Authority: `{registry["protocol_id"]}`
Docs gate: `{registry["docs_gate"]["state"]}` (`{registry["docs_gate"]["reason"]}`)
Witness class: `LOCAL_ONLY`
Command root: `{registry["command_root"]}`

## Canonical Authority

- Canonical manifest: `{registry["canonical_authority"]["manifest_path"]}`
- Canonical registry: `{registry["canonical_authority"]["registry_path"]}`
- `NEXT57` packet, capillary, latency, and protocol JSON surfaces are `compatibility_only` mirrors.
- `NEXT57-H-COMMAND-MEMBRANE` and `NEXT57-T-COMMAND-LAW` remain quest-dock references only.

## Flow

`GLOBAL COMMAND -> Scout -> Router -> Worker -> Archivist`

## Selective Propagation

- Policy: `{registry["routing_policy"]["policy_id"]}`
- Top-k: `{registry["defaults"]["topk"]}`
- Claim mode: `{registry["defaults"]["claim_mode"]}`
- Quorum: `{registry["defaults"]["quorum"]}`
- TTL: `{registry["defaults"]["ttl"]}`
- Lease: `{registry["defaults"]["default_lease_ms"]}ms`
- Event watch is canonical; polling is honest fallback only (`{registry["defaults"]["watcher_fallback_marker"]}`).

## Capillary Law

- Formula: `{registry["capillary_reinforcement"]["formula"]}`
- Edge classes: `{", ".join(registry["capillary_reinforcement"]["edge_classes"])}`

## Latency Law

- Formula: `{registry["latency_benchmarks"]["formula"]}`
"""


def build_protocol_artifacts() -> dict[str, Any]:
    registry = registry_payload()
    touch(EVENT_FEED_PATH)
    touch(ROUTE_FEED_PATH)
    touch(CLAIM_FEED_PATH)
    touch(COMMIT_FEED_PATH)
    touch(REINFORCEMENT_FEED_PATH)
    touch(CAPILLARY_LEDGER_PATH, "{}\n")
    write_json(REGISTRY_PATH, registry)
    write_json(NEXT57_PROTOCOL_PATH, mirror_protocol_payload(registry))
    write_json(NEXT57_PACKET_SCHEMA_PATH, mirror_schema_payload(registry))
    write_json(NEXT57_CAPILLARY_LAW_PATH, mirror_capillary_payload(registry))
    write_json(NEXT57_LATENCY_BENCHMARKS_PATH, mirror_latency_payload(registry))
    write_text(MANIFEST_PATH, manifest_markdown(registry))
    return registry


def verify_protocol_artifacts() -> dict[str, Any]:
    registry = build_protocol_artifacts()
    protocol = json.loads(NEXT57_PROTOCOL_PATH.read_text(encoding="utf-8"))
    schema = json.loads(NEXT57_PACKET_SCHEMA_PATH.read_text(encoding="utf-8"))
    capillary = json.loads(NEXT57_CAPILLARY_LAW_PATH.read_text(encoding="utf-8"))
    latency = json.loads(NEXT57_LATENCY_BENCHMARKS_PATH.read_text(encoding="utf-8"))
    manifest = MANIFEST_PATH.read_text(encoding="utf-8")
    checks = {
        "protocol_id_match": registry.get("protocol_id") == PROTOCOL_ID,
        "docs_gate_honest": registry.get("docs_gate", {}).get("state") == "BLOCKED",
        "policy_frozen": registry.get("routing_policy", {}).get("policy_id") == ROUTING_POLICY,
        "coord12_keys": schema.get("coord12_keys") == coord12_dimensions(),
        "next57_protocol_is_mirror": protocol.get("compatibility_only") is True and protocol.get("mirror_of") == PROTOCOL_ID,
        "next57_schema_is_mirror": schema.get("compatibility_only") is True and schema.get("mirror_of") == PROTOCOL_ID,
        "next57_capillary_is_mirror": capillary.get("compatibility_only") is True and capillary.get("mirror_of") == PROTOCOL_ID,
        "next57_latency_is_mirror": latency.get("compatibility_only") is True and latency.get("mirror_of") == PROTOCOL_ID,
        "capillary_classes": registry.get("capillary_reinforcement", {}).get("edge_classes") == ["ephemeral", "capillary", "vein"],
        "manifest_mentions_authority": "compatibility_only" in manifest and ROUTING_POLICY in manifest,
    }
    result = {"generated_at": utc_now(), "truth": "OK" if all(checks.values()) else "NEAR", "checks": checks}
    write_json(VERIFICATION_PATH, result)
    return result
