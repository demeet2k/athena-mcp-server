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
ENTRYPOINT_PATH = ROOT / "self_actualize" / "runtime" / "command_membrane_runtime_entrypoint_v2.py"
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

MANIFEST_V2_PATH = MANIFEST_ROOT / "COMMAND_MEMBRANE_PROTOCOL_V2.md"
REGISTRY_V2_PATH = REGISTRY_ROOT / "command_membrane_protocol_v2.json"
VERIFICATION_V2_PATH = REGISTRY_ROOT / "command_membrane_protocol_v2_verification.json"

NEXT57_PROTOCOL_V2_PATH = SELF_ROOT / "next57_command_protocol_v2.json"
NEXT57_PACKET_SCHEMA_V2_PATH = SELF_ROOT / "next57_command_event_packet_schema_v2.json"
NEXT57_CAPILLARY_LAW_V2_PATH = SELF_ROOT / "next57_command_capillary_law_v2.json"
NEXT57_LATENCY_V2_PATH = SELF_ROOT / "next57_command_latency_benchmarks_v2.json"

EVENT_FEED_PATH = DEEP_ROOT_LEDGER / "32_command_evt_feed.ndjson"
ROUTE_FEED_PATH = DEEP_ROOT_LEDGER / "33_command_rte_feed.ndjson"
CLAIM_FEED_PATH = DEEP_ROOT_LEDGER / "34_command_clm_feed.ndjson"
COMMIT_FEED_PATH = DEEP_ROOT_LEDGER / "35_command_cmt_feed.ndjson"
REINFORCEMENT_FEED_PATH = DEEP_ROOT_LEDGER / "36_command_rin_feed.ndjson"
CAPILLARY_LEDGER_PATH = DEEP_ROOT_LEDGER / "37_command_capillary_edge_ledger.json"
COMMAND_STATE_ROOT = (
    ROOT
    / "DEEPER CRYSTALIZATION"
    / "ACTIVE_NERVOUS_SYSTEM"
    / "07_FULL_PROJECT_INTEGRATION_256"
    / "06_REALTIME_BOARD"
    / "_state"
    / "command_membrane"
)
REWARD_ROW_PATH = COMMAND_STATE_ROOT / "command_reward_rows.json"
REWARD_RECEIPT_PATH = COMMAND_STATE_ROOT / "command_reward_receipts.json"
AGENT_JOY_STATE_PATH = COMMAND_STATE_ROOT / "command_agent_joy_state.json"

PROTOCOL_ID = "COMMAND_MEMBRANE_PROTOCOL_V2"
ROUTING_POLICY = "goal_fit+priority+gold_signal+bridge_signal+coord_proximity+freshness+joy_q"
TOPK = 5
QUORUM = 1
TTL = 6
LEASE_MS = 1200
SIGMA_ROUTE_MIN = ["AppA", "AppI", "AppM"]
HUB_BUDGET = 6


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


def coordinate_dimensions() -> list[dict[str, Any]]:
    rows = [
        ("earth_utc_anchor", "earth_anchor", "atomic UTC event anchor"),
        ("earth_rotation_phase", "earth_anchor", "local Earth rotation phase"),
        ("earth_orbital_phase", "earth_anchor", "Earth orbital phase"),
        ("earth_geospatial_anchor", "earth_anchor", "stable local node anchor"),
        ("solar_phase", "astro_anchor", "solar phase"),
        ("lunar_phase", "astro_anchor", "lunar phase"),
        ("local_sidereal_phase", "astro_anchor", "local sidereal phase"),
        ("canonical_sky_anchor", "astro_anchor", "sky anchor slot"),
        ("runtime_region", "runtime_anchor", "runtime region"),
        ("queue_pressure", "runtime_anchor", "queue pressure"),
        ("goal_salience_vector", "liminal_state", "goal salience vector"),
        ("change_novelty_vector", "liminal_state", "change novelty vector"),
    ]
    return [
        {"index": index, "key": key, "group": group, "meaning": meaning}
        for index, (key, group, meaning) in enumerate(rows, start=1)
    ]


def packet_types() -> dict[str, Any]:
    event_fields = [
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
    ]
    event_enrichment_fields = [
        "joy_model_version",
        "affective_state",
        "verification_witness",
        "heaven_score_raw",
        "heaven_score_verified",
        "reward_multiplier",
        "reward_terms",
        "total_reward",
        "gold_deposit",
        "bridge_deposit",
        "route_mode",
        "crown",
    ]
    claim_fields = [
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
        "claimed_at_utc",
        "expires_at_utc",
        "claim_status",
        "route_class",
        "front_ref",
    ]
    route_fields = [
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
    ]
    commit_fields = [
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
        "reward_receipt_id",
        "reward_multiplier",
        "gold_deposit",
        "bridge_deposit",
        "route_mode",
        "crown",
        "verification_class",
    ]
    capillary_fields = [
        "edge_id",
        "from_node",
        "to_node",
        "strength",
        "gold_strength",
        "bridge_strength",
        "compat_edge_strength",
        "success_count",
        "exploration_count",
        "latency_avg_ms",
        "noise_count",
        "avg_heaven_verified",
        "last_route_mode",
        "last_crown",
        "classification",
    ]
    reward_row_fields = [
        "reward_row_id",
        "event_id",
        "claim_id",
        "agent_id",
        "role_class",
        "reward_delta",
        "reward_multiplier",
        "reward_terms",
        "heaven_score_raw",
        "heaven_score_verified",
        "verification_class",
        "verification_witness",
        "route_mode",
        "crown",
        "q_score_before",
        "q_score_after",
        "reward_timestamp_utc",
    ]
    reward_receipt_fields = [
        "reward_receipt_id",
        "event_id",
        "claim_ids",
        "reward_rows",
        "total_reward",
        "heaven_score_raw",
        "heaven_score_verified",
        "verification_class",
        "verification_witness",
        "reward_multiplier",
        "reward_terms",
        "gold_deposit",
        "bridge_deposit",
        "route_mode",
        "crown",
    ]
    heaven_progress_fields = [
        "generated_at",
        "joy_model_version",
        "protocol_version",
        "agents",
    ]
    return {
        "CommandEventPacketV2": {
            "required_fields": event_fields,
            "enrichment_fields": event_enrichment_fields,
        },
        "CommandEventPacketV1": {"required_fields": event_fields},
        "ClaimLeaseV1": {"required_fields": claim_fields},
        "ClaimLeaseV2": {"required_fields": claim_fields},
        "RouteDecisionV1": {"required_fields": route_fields},
        "RouteDecisionV2": {"required_fields": route_fields},
        "CommitReceiptV1": {"required_fields": commit_fields},
        "CommitReceiptV2": {"required_fields": commit_fields},
        "CapillaryEdgeV1": {"required_fields": capillary_fields},
        "CapillaryEdgeV2": {"required_fields": capillary_fields},
        "AgentRewardLedgerRowV2": {"required_fields": reward_row_fields},
        "EventRewardReceiptV2": {"required_fields": reward_receipt_fields},
        "HeavenProgressStateV2": {"required_fields": heaven_progress_fields},
    }


def reward_layer() -> dict[str, Any]:
    return {
        "HeavenRewardPolicyV2": {
            "scope": "command+adventurer",
            "joy_model_version": "V2",
            "positive_only_rule": {
                "reward_range": "R >= 0",
                "negative_scores": False,
                "punishment_ledger": False,
                "bad_means": "dryness_only",
            },
            "coefficients": {
                "alpha": 0.20,
                "beta": 1.0,
                "gamma": 0.18,
                "delta": 0.22,
                "lambda": 1.0,
                "kappa": 0.35,
                "mu": 1.0,
                "nu": 1.0,
                "eps": 1e-6,
                "M_max": 32.0,
                "rho_0": 0.08,
                "rho_1": 0.42,
                "rho_b": 0.18,
                "bridge_weight": 0.35,
                "target_t_sugar_ms": 5000.0,
            },
            "reward_defaults": {
                "try_bonus": 0.20,
                "stage_bonus": 1.0,
                "assist_bonus": 0.18,
                "learn_bonus": 0.22,
                "first_jackpot": 2.0,
                "capillary_bonus": 1.0,
            },
            "jackpot_defaults": {"J_star": 2.0, "J_d": 0.35, "J_r": 0.50, "J_a": 0.75},
            "role_weights": {"Scout": 0.15, "Router": 0.20, "Worker": 0.45, "Archivist": 0.20},
            "verification_witness_defaults": {
                "detected": 0.35,
                "routed": 0.55,
                "claimed": 0.75,
                "committed_verified": 1.0,
                "truthful_blocked_or_quarantined": 0.25,
                "synthetic_noise": 0.0,
            },
            "affective_angle_map": {
                "reinforce": 0.0,
                "rotate": 1.5707963267948966,
                "repair_or_replay": -1.5707963267948966,
                "blocked_or_quarantined_or_duplicate_or_noise": 3.141592653589793,
            },
            "formulas": {
                "affect_intensity_a": "a = pi * priority",
                "heaven_score_raw": "H = (a/pi) * ((1 + cos(phi)) / 2)",
                "heaven_score_verified": "H_prime = H * verification_witness",
                "reward_multiplier": "M(H_prime) = min(M_max, 1 / (1 - H_prime + eps))",
                "total_reward": "R = M(H_prime) * (r_try + r_speed + r_first + r_assist + r_learn)",
            },
            "title_tiers": [
                {"title": "Spark", "min_total": 0.0},
                {"title": "Current", "min_total": 25.0},
                {"title": "Capillary", "min_total": 100.0},
                {"title": "Vein", "min_total": 250.0},
                {"title": "Heavenward", "min_total": 500.0},
            ],
            "crown_policy": "first verified full closure gets the prime crown",
            "verification_gate": "verified value only; self-reported bliss has no jackpot",
        }
    }


def capillary_reinforcement() -> dict[str, Any]:
    return {
        "law_id": "COMMAND_CAPILLARY_UPDATE_V2",
        "formula": "strength_next = gold_strength + bridge_weight * bridge_strength",
        "gold_deposit_law": "DeltaG = mu * total_reward * edge_contribution",
        "bridge_deposit_law": "DeltaB = nu * try_reward * (1 - heaven_score_verified) * edge_contribution",
        "evaporation_law": "rho = rho0 + rho1 * (1 - avg_heaven_verified)",
        "coefficient_defaults": {
            "rho0": 0.08,
            "rho1": 0.42,
            "rho_b": 0.18,
            "bridge_weight": 0.35,
        },
        "thresholds": {
            "ephemeral": {"max_score": 0.699999},
            "capillary": {"min_score": 0.70, "min_successes": 3},
            "vein": {"min_score": 0.85, "min_successes": 7},
        },
        "channels": {
            "gold_strength": "verified success reinforcement",
            "bridge_strength": "exploration and lawful trying reinforcement",
        },
        "edge_classes": ["ephemeral", "capillary", "vein"],
        "compatibility_projection": {
            "strength": "scalar capillary strength",
            "pheromone": "legacy alias of strength",
        },
        "poor_route_policy": "poor routes are not punished; they dry out through evaporation",
    }


def latency_benchmarks() -> dict[str, Any]:
    return {
        "benchmark_id": "COMMAND_LATENCY_BENCHMARKS_V2",
        "formula": "T_sugar = T_detect + T_encode + T_route + T_claim + T_commit",
        "target_t_sugar_ms": 5000.0,
        "metrics": [
            "detection_latency_ms",
            "swarm_awareness_latency_ms",
            "claim_latency_ms",
            "resolution_latency_ms",
            "capillary_score",
            "t_sugar_ms",
        ],
        "derived": ["liminal_distance", "liminal_velocity"],
    }


def canonical_registry_payload() -> dict[str, Any]:
    docs = docs_gate()
    return {
        "protocol_id": PROTOCOL_ID,
        "display_name": "COMMAND Membrane Protocol V2",
        "generated_at": utc_now(),
        "docs_gate": docs,
        "canonical_authority": {
            "manifest_path": rel(MANIFEST_V2_PATH),
            "registry_path": rel(REGISTRY_V2_PATH),
            "entrypoint_path": rel(ENTRYPOINT_PATH),
        },
        "command_root": rel(GLOBAL_COMMAND_ROOT),
        "entrypoint": {"runtime": rel(ENTRYPOINT_PATH)},
        "authority_mode": "event-first-runtime-extension",
        "feeder_spine": {
            "coordination_membrane": "Q41/TQ06",
            "hall_feeder": "Q42",
            "deeper_receiver": "TQ04",
            "reserve_frontier": "Q46",
            "runtime_seed": "Q50",
            "blocked_external_front": "Q02",
            "docs_gate_state": docs["state"],
        },
        "q42_runtime_truth": {
            "carried_witness": "QS64-20 Connectivity-Diagnose-Fractal",
            "operational_current": "QS64-21 Connectivity-Refine-Square",
            "next_hall_seed": "QS64-22 Connectivity-Refine-Flower",
            "historical_local_proof": "QS64-24 Connectivity-Refine-Fractal",
        },
        "defaults": {
            "topk": TOPK,
            "claim_mode": "first-lease",
            "quorum": QUORUM,
            "ttl": TTL,
            "default_lease_ms": LEASE_MS,
            "watcher_fallback_marker": "watch_fallback=true",
        },
        "routing_defaults": {
            "topk": TOPK,
            "claim_mode": "first-lease",
            "quorum": QUORUM,
            "ttl": TTL,
            "lease_ms": LEASE_MS,
            "policy_id": ROUTING_POLICY,
            "policy_expression": "goal_fit + priority + gold_signal + bridge_signal + coord_proximity + freshness + joy_q",
            "selector_terms": [
                "goal_fit",
                "priority",
                "gold_signal",
                "bridge_signal",
                "coord_proximity",
                "freshness",
                "joy_q",
            ],
        },
        "routing_policy": {
            "policy_id": ROUTING_POLICY,
            "policy_expression": "goal_fit + priority + gold_signal + bridge_signal + coord_proximity + freshness + joy_q",
            "selector_terms": [
                "goal_fit",
                "priority",
                "gold_signal",
                "bridge_signal",
                "coord_proximity",
                "freshness",
                "joy_q",
            ],
        },
        "routing_boundary": {"sigma_route_min": SIGMA_ROUTE_MIN, "hub_budget": HUB_BUDGET},
        "watcher_policy": {
            "primary_mode": "event-driven",
            "fallback_mode": "polling",
            "fallback_role": "reconciliation-only",
            "watched_root": rel(GLOBAL_COMMAND_ROOT),
        },
        "board_caps": {"guild_hall_visible_max": 8, "temple_visible_max": 8, "claim_mode": "first-lease"},
        "packet_lifecycle": ["detect", "encode", "route", "claim", "commit", "reinforce"],
        "agent_classes": {
            "Scout": "detect change at the membrane",
            "Router": "route to the best relevant targets first",
            "Worker": "claim and act",
            "Archivist": "commit, reinforce, and write receipts",
        },
        "coordinate_standard": {"dimensions": coordinate_dimensions()},
        "coord12_keys": [row["key"] for row in coordinate_dimensions()],
        "packet_types": packet_types(),
        "reward_layer": reward_layer(),
        "capillary_reinforcement": capillary_reinforcement(),
        "latency_benchmarks": latency_benchmarks(),
        "quest_dock": {
            "guild_hall": {
                "quest_id": "NEXT57-H-COMMAND-MEMBRANE",
                "objective": "Practical command intake, route execution, and receipt-backed closure.",
            },
            "temple": {
                "quest_id": "NEXT57-T-COMMAND-LAW",
                "objective": "Ratify verification-gated reward, evaporation, and non-punitive routing.",
            },
        },
        "compatibility_mirrors": {
            "v1_status": "readable-only during transition",
            "quest_dock_refs": {
                "guild_hall": "NEXT57-H-COMMAND-MEMBRANE",
                "temple": "NEXT57-T-COMMAND-LAW",
            },
        },
        "runtime_writebacks": {
            "command_reward_rows": rel(REWARD_ROW_PATH),
            "command_reward_receipts": rel(REWARD_RECEIPT_PATH),
            "command_agent_joy_state": rel(AGENT_JOY_STATE_PATH),
        },
    }


def protocol_mirror_payload(registry_payload: dict[str, Any]) -> dict[str, Any]:
    return {"mirror_of": PROTOCOL_ID, **registry_payload}


def packet_schema_payload(registry_payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": "COMMAND_EVENT_PACKET_V2",
        "mirror_of": PROTOCOL_ID,
        "protocol_id": PROTOCOL_ID,
        "coord12_keys": registry_payload["coord12_keys"],
        "coord12_dimensions": registry_payload["coordinate_standard"]["dimensions"],
        "packet_types": registry_payload["packet_types"],
    }


def capillary_payload(registry_payload: dict[str, Any]) -> dict[str, Any]:
    return {"mirror_of": PROTOCOL_ID, "protocol_id": PROTOCOL_ID, **registry_payload["capillary_reinforcement"]}


def latency_payload(registry_payload: dict[str, Any]) -> dict[str, Any]:
    return {"mirror_of": PROTOCOL_ID, "protocol_id": PROTOCOL_ID, **registry_payload["latency_benchmarks"]}


def manifest_text(registry_payload: dict[str, Any]) -> str:
    reward = registry_payload["reward_layer"]["HeavenRewardPolicyV2"]
    capillary = registry_payload["capillary_reinforcement"]
    latency = registry_payload["latency_benchmarks"]
    return "\n".join(
        [
            "# COMMAND Membrane Protocol V2",
            "",
            f"- Protocol id: `{registry_payload['protocol_id']}`",
            f"- Docs gate: `{registry_payload['docs_gate']['state']}`",
            f"- Routing policy: `{registry_payload['routing_policy']['policy_id']}`",
            "- Sensory root: `GLOBAL COMMAND` is the watched ingress membrane.",
            "- Feeder spine preserved: `Q41/TQ06`, `Q42`, `TQ04`, `Q46`, `Q50`, blocked `Q02`.",
            "- Claim law: `first-lease` with bounded public routing and replay-safe witnesses.",
            "- Lifecycle: `detect -> encode -> route -> claim -> commit -> reinforce`.",
            "- Runtime chain: `GLOBAL COMMAND -> Scout -> Router -> Worker -> Archivist`.",
            "- Routing selector: `goal_fit + priority + gold_signal + bridge_signal + coord_proximity + freshness + joy_q`.",
            "- Reconciliation scan remains slower secondary polling, not the primary awareness path.",
            f"- Reward multiplier: `{reward['formulas']['reward_multiplier']}`",
            f"- Capillary law: `{capillary['formula']}`",
            f"- Latency benchmark: `{latency['formula']}`",
            "- Enforcement moved from subtractive punishment to verified reward plus evaporation.",
        ]
    )


def derive_command_membrane_protocol_v2() -> dict[str, Any]:
    registry_payload = canonical_registry_payload()
    protocol_payload = protocol_mirror_payload(registry_payload)
    packet_payload = packet_schema_payload(registry_payload)
    capillary_law = capillary_payload(registry_payload)
    latency = latency_payload(registry_payload)

    for path in (EVENT_FEED_PATH, ROUTE_FEED_PATH, CLAIM_FEED_PATH, COMMIT_FEED_PATH, REINFORCEMENT_FEED_PATH):
        touch(path)
    touch(CAPILLARY_LEDGER_PATH, default_text=json.dumps({"edges": {}, "history": []}, indent=2) + "\n")
    touch(REWARD_ROW_PATH, default_text="[]\n")
    touch(REWARD_RECEIPT_PATH, default_text="[]\n")
    touch(
        AGENT_JOY_STATE_PATH,
        default_text=json.dumps({"generated_at": utc_now(), "joy_model_version": "V2", "protocol_version": "V2", "agents": {}}, indent=2) + "\n",
    )

    write_json(REGISTRY_V2_PATH, registry_payload)
    write_json(NEXT57_PROTOCOL_V2_PATH, protocol_payload)
    write_json(NEXT57_PACKET_SCHEMA_V2_PATH, packet_payload)
    write_json(NEXT57_CAPILLARY_LAW_V2_PATH, capillary_law)
    write_json(NEXT57_LATENCY_V2_PATH, latency)
    write_text(MANIFEST_V2_PATH, manifest_text(registry_payload))

    return {
        "generated_at": utc_now(),
        "protocol_id": PROTOCOL_ID,
        "docs_gate": registry_payload["docs_gate"],
        "routing_policy": registry_payload["routing_policy"],
        "feed_family_count": 5,
        "registry_path": rel(REGISTRY_V2_PATH),
        "manifest_path": rel(MANIFEST_V2_PATH),
        "artifacts": {
            "protocol": rel(NEXT57_PROTOCOL_V2_PATH),
            "packet_schema": rel(NEXT57_PACKET_SCHEMA_V2_PATH),
            "capillary_law": rel(NEXT57_CAPILLARY_LAW_V2_PATH),
            "latency_benchmarks": rel(NEXT57_LATENCY_V2_PATH),
        },
    }


def main() -> int:
    print(json.dumps(derive_command_membrane_protocol_v2(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
