from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

if __package__ in {None, ""}:
    ROOT = Path(__file__).resolve().parents[2]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from self_actualize.runtime.command_spine import CommandMembraneService, read_json, rel
else:
    from .command_spine import CommandMembraneService, read_json, rel
    ROOT = Path(__file__).resolve().parents[2]


VERIFY_PATH = ROOT / "self_actualize" / "mycelium_brain" / "registry" / "command_membrane_protocol_v1_verification.json"
EXPECTED_PROTOCOL_ID = "NEXT57_COMMAND_PROTOCOL_V2"
EXPECTED_SCHEMA_ID = "NEXT57_COMMAND_EVENT_PACKET_V2"
EXPECTED_CAPILLARY_ID = "NEXT57_COMMAND_CAPILLARY_UPDATE_V2"
EXPECTED_ROUTE_POLICY = "goal_fit+priority+gold_signal+bridge_signal+coord_proximity+freshness"
EXPECTED_SELECTOR_TERMS = [
    "goal_fit",
    "priority",
    "gold_signal",
    "bridge_signal",
    "coord_proximity",
    "freshness",
    "capillary_strength",
    "source_class",
]
EXPECTED_COORD12 = [
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
EXPECTED_PACKET_TYPES = [
    "CommandEventPacket",
    "RouteDecision",
    "ClaimLease",
    "ArchivistReceipt",
    "CapillaryEdge",
    "LatencyBenchmarkRecord",
]
EXPECTED_METRICS = [
    "detection_latency_ms",
    "swarm_awareness_latency_ms",
    "claim_latency_ms",
    "resolution_latency_ms",
    "commit_latency_ms",
    "t_sugar_ms",
    "capillary_score",
    "liminal_distance",
    "liminal_velocity",
]
EXPECTED_ACTIVE_SURFACE = "LOCAL SWARM MESH"
EXPECTED_WATCH_SCOPE = "first-wave local swarm mesh"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def contains_all(path: Path, snippets: list[str]) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8").lower()
    return all(snippet.lower() in text for snippet in snippets)


def verify_command_membrane_protocol() -> dict[str, object]:
    svc = CommandMembraneService()
    artifacts = svc.ensure_protocol_artifacts()
    public_state = svc.sync_public_surfaces()
    protocol = read_json(svc.config.protocol_json_path, {})
    schema = read_json(svc.config.packet_schema_json_path, {})
    capillary = read_json(svc.config.capillary_law_json_path, {})
    latency = read_json(svc.config.latency_benchmark_json_path, {})
    registry = read_json(svc.config.protocol_v1_registry_path, {})

    checks = {
        "protocol_id_exact": protocol.get("protocol_id") == EXPECTED_PROTOCOL_ID,
        "registry_protocol_id_exact": registry.get("protocol_id") == EXPECTED_PROTOCOL_ID,
        "canonical_authority_exact": protocol.get("canonical_authority") == "LP57OMEGA / NEXT57",
        "active_surface_exact": protocol.get("active_surface") == EXPECTED_ACTIVE_SURFACE,
        "watch_scope_exact": protocol.get("watch_policy", {}).get("watch_scope") == EXPECTED_WATCH_SCOPE,
        "watched_surface_count_exact": protocol.get("watched_surfaces", {}).get("source_count") == 7,
        "watch_policy_exact": protocol.get("watch_policy", {}).get("primary_mode") == "event-driven"
        and protocol.get("watch_policy", {}).get("fallback_mode") == "polling",
        "route_policy_exact": protocol.get("routing_defaults", {}).get("policy_id") == EXPECTED_ROUTE_POLICY,
        "selector_terms_exact": protocol.get("routing_defaults", {}).get("selector_terms") == EXPECTED_SELECTOR_TERMS,
        "schema_id_exact": schema.get("schema_id") == EXPECTED_SCHEMA_ID,
        "coord12_labels_exact": schema.get("coord12_labels") == EXPECTED_COORD12,
        "coord12_frame_groups_exact": schema.get("coord12_frame_groups") == ["earth", "astro", "runtime", "liminal"],
        "packet_types_exact": list(schema.get("packet_types", {}).keys()) == EXPECTED_PACKET_TYPES,
        "lookup_envelope_exact": schema.get("lookup_envelope") == "NodeStamp = AgentTag @ CoordinateStamp + WitnessClass + QuestRefs + ArtifactRefs",
        "capillary_id_exact": capillary.get("law_id") == EXPECTED_CAPILLARY_ID,
        "capillary_formula_exact": capillary.get("formula") == "C_next = clamp(0,1, rho*C + alpha*U + beta*F - gamma*D - delta*N)",
        "latency_equation_exact": latency.get("equation") == "T_sugar = T_detect + T_encode + T_route + T_claim + T_commit",
        "latency_metrics_exact": latency.get("metrics") == EXPECTED_METRICS,
        "docs_gate_honest": protocol.get("docs_gate", {}).get("state") == "BLOCKED"
        and protocol.get("docs_gate", {}).get("credentials_exists") is False
        and protocol.get("docs_gate", {}).get("token_exists") is False
        and public_state.get("docs_gate", {}).get("state") == "BLOCKED",
        "runtime_witness_exists": svc.config.command_manifest_path.exists(),
        "schema_doc_aligned": contains_all(
            svc.config.packet_manifest_path,
            ["local swarm mesh", "typed packet", "coord12", "lookup envelope"],
        ),
        "toolkit_doc_aligned": contains_all(
            svc.config.protocol_v1_manifest_path,
            ["single-node swarm membrane", "first-wave local swarm mesh", "event-driven", "polling"],
        ),
    }

    return {
        "generated_at": utc_now(),
        "truth": "OK" if all(checks.values()) else "NEAR",
        "checks": checks,
        "artifacts": {
            "protocol": rel(Path(artifacts["protocol"])),
            "schema": rel(Path(artifacts["schema"])),
            "reward": rel(Path(artifacts["reward"])),
            "capillary": rel(Path(artifacts["capillary"])),
            "latency": rel(Path(artifacts["latency"])),
            "registry": rel(svc.config.protocol_v1_registry_path),
            "public_state": rel(ROOT / "NERVOUS_SYSTEM" / "95_MANIFESTS" / "COMMAND_MEMBRANE_STATE.json"),
            "runtime_witness": rel(svc.config.command_manifest_path),
        },
    }


def main() -> int:
    result = verify_command_membrane_protocol()
    VERIFY_PATH.parent.mkdir(parents=True, exist_ok=True)
    VERIFY_PATH.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result.get("truth") == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
