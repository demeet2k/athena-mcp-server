from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from self_actualize.runtime.command_spine import (
    COMMAND_CAPILLARY_LAW_ID_V2,
    COMMAND_PACKET_SCHEMA_ID_V2,
    COMMAND_PROTOCOL_ID_V2,
    COMMAND_REWARD_FIELD_ID_V2,
    COMMAND_ROUTE_POLICY,
    CommandMembraneService,
)
from self_actualize.runtime.derive_command_membrane_protocol import derive_command_membrane_protocol


ROOT = Path(__file__).resolve().parents[2]
SELF_ROOT = ROOT / "self_actualize"
REGISTRY_ROOT = SELF_ROOT / "mycelium_brain" / "registry"
VERIFY_PATH = SELF_ROOT / "command_membrane_protocol_verification.json"
LEGACY_VERIFY_PATH = REGISTRY_ROOT / "command_membrane_protocol_v1_verification.json"
EXPECTED_RANKING_TERMS = [
    "goal_fit",
    "priority",
    "gold_signal",
    "bridge_signal",
    "coord_proximity",
    "freshness",
]
EXPECTED_PACKET_BLOCKS = ["reward_state", "verification_state", "pheromone_state"]
EXPECTED_RECEIPT_BLOCKS = ["reward_state", "verification_state", "pheromone_state", "reward_allocations"]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def contains_all(path: Path, snippets: list[str]) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8").lower()
    return all(snippet.lower() in text for snippet in snippets)


def verify_command_membrane_protocol() -> dict[str, Any]:
    derive_result = derive_command_membrane_protocol()
    service = CommandMembraneService()
    protocol = read_json(service.config.protocol_json_path, {})
    schema = read_json(service.config.packet_schema_json_path, {})
    reward = read_json(service.config.reward_field_json_path, {})
    capillary = read_json(service.config.capillary_law_json_path, {})
    latency = read_json(service.config.latency_benchmark_json_path, {})
    compat_registry = read_json(service.config.protocol_v1_registry_path, {})

    packet_types = schema.get("packet_types", {})
    reward_formulas = reward.get("formulas", {})
    reward_coeffs = reward.get("coefficients", {})
    capillary_formulas = capillary.get("formulas", {})
    compatibility_projection = capillary.get("compatibility_projection", {})

    heaven_state = service.heaven_score(math.pi, 0.0)
    hell_state = service.heaven_score(math.pi, math.pi)
    pole_pos = service.heaven_score(math.pi, math.pi / 2.0)
    pole_neg = service.heaven_score(math.pi, -(math.pi / 2.0))

    verify_success = service.verification_defaults("commit", "success")
    verify_blocked = service.verification_defaults("commit", "blocked")
    verify_duplicate = service.verification_defaults("commit", "duplicate")
    reward_success = service.finalize_reward_state(
        service.compose_reward_state(
            stage="commit",
            result="success",
            priority=1.0,
            confidence=1.0,
            effort_quality=1.0,
            tau_seconds=0.0,
            novelty_score=1.0,
            contribution_share=0.45,
            verification_state=verify_success,
        )
    )
    reward_blocked = service.finalize_reward_state(
        service.compose_reward_state(
            stage="commit",
            result="blocked",
            priority=0.8,
            confidence=0.9,
            effort_quality=1.0,
            tau_seconds=0.5,
            novelty_score=0.2,
            contribution_share=0.45,
            verification_state=verify_blocked,
        )
    )
    reward_duplicate = service.finalize_reward_state(
        service.compose_reward_state(
            stage="commit",
            result="duplicate",
            priority=0.8,
            confidence=0.9,
            effort_quality=0.0,
            tau_seconds=0.5,
            novelty_score=0.0,
            contribution_share=0.45,
            verification_state=verify_duplicate,
        )
    )
    pheromone_blocked = service.compose_pheromone_state(
        reward_blocked,
        0.45,
        reward_blocked.verified_alignment_score,
    )
    pheromone_duplicate = service.compose_pheromone_state(
        reward_duplicate,
        0.45,
        reward_duplicate.verified_alignment_score,
    )

    checks = {
        "derive_runs": bool(derive_result.get("protocol_id")),
        "protocol_id_v2": protocol.get("protocol_id") == COMMAND_PROTOCOL_ID_V2,
        "schema_id_v2": schema.get("schema_id") == COMMAND_PACKET_SCHEMA_ID_V2,
        "reward_id_v2": reward.get("law_id") == COMMAND_REWARD_FIELD_ID_V2,
        "capillary_id_v2": capillary.get("law_id") == COMMAND_CAPILLARY_LAW_ID_V2,
        "docs_gate_blocked": protocol.get("docs_gate_status") == "BLOCKED"
        and protocol.get("docs_gate", {}).get("state") == "BLOCKED"
        and protocol.get("docs_gate", {}).get("credentials_exists") is False
        and protocol.get("docs_gate", {}).get("token_exists") is False,
        "route_policy_nonnegative": protocol.get("routing_defaults", {}).get("policy_id") == COMMAND_ROUTE_POLICY
        and protocol.get("routing_defaults", {}).get("ranking_terms") == EXPECTED_RANKING_TERMS
        and protocol.get("routing_defaults", {}).get("selector_terms") == EXPECTED_RANKING_TERMS
        and protocol.get("routing_defaults", {}).get("duplicate_guard", {}).get("score_mode") == "nonnegative",
        "reward_blocks_present": schema.get("packet_blocks") == EXPECTED_PACKET_BLOCKS
        and set(packet_types.get("CommandEventPacketV2", {}).get("blocks", [])) == set(EXPECTED_PACKET_BLOCKS)
        and set(packet_types.get("CommandEventPacketV2", {}).get("required", []))
        >= {"reward_state", "verification_state", "pheromone_state"},
        "receipt_blocks_present": schema.get("receipt_blocks") == EXPECTED_RECEIPT_BLOCKS
        and set(packet_types.get("CommandExecutionReceiptV2", {}).get("required", []))
        >= {"reward_state", "verification_state", "pheromone_state", "reward_allocations"}
        and set(packet_types.get("CommandReinforcementReceiptV2", {}).get("required", []))
        >= {"reward_state", "verification_state", "pheromone_state", "reward_allocations", "edge_allocations"},
        "v2_types_present": set(packet_types.keys())
        >= {
            "CommandEventPacketV2",
            "CommandRouteDecisionV2",
            "CommandExecutionReceiptV2",
            "CommandReinforcementReceiptV2",
            "LatencySampleV2",
            "CapillaryEdgeV2",
        },
        "formula_invariants": heaven_state == 1.0 and hell_state == 0.0 and pole_pos == 0.5 and pole_neg == 0.5,
        "verified_multiplier_gate": reward_formulas.get("verified_alignment_score") == "H_prime = H * verification_witness"
        and reward_formulas.get("reward_multiplier") == "min(64.0, 1 / (1 - H_prime + 0.01))",
        "reward_terms_nonnegative": min(
            reward_success.attempt_reward,
            reward_success.latency_reward,
            reward_success.first_reward,
            reward_success.assist_reward,
            reward_success.learning_reward,
            reward_success.total_reward,
            reward_blocked.attempt_reward,
            reward_blocked.total_reward,
            reward_duplicate.total_reward,
            pheromone_blocked.gold_deposit,
            pheromone_blocked.bridge_deposit,
            pheromone_duplicate.gold_deposit,
            pheromone_duplicate.bridge_deposit,
        )
        >= 0.0,
        "verification_defaults_exact": verify_success.verification_witness == 1.0
        and verify_blocked.verification_witness == 0.7
        and verify_duplicate.verification_witness == 0.0,
        "crown_rules": service.crown_tier_for_stage("detect", "observe", service.verification_defaults("detect", "observe")) == "detect"
        and service.crown_tier_for_stage("route", "observe", service.verification_defaults("route", "observe")) == "route"
        and service.crown_tier_for_stage("claim", "observe", service.verification_defaults("claim", "observe")) == "act"
        and service.crown_tier_for_stage("commit", "success", verify_success) == "prime"
        and service.crown_tier_for_stage("commit", "blocked", verify_blocked) == "none",
        "blocked_and_dry_behaviour": reward_blocked.route_mode == "rotate"
        and reward_blocked.affect_direction_phi == round(-(math.pi / 2.0), 6)
        and pheromone_blocked.bridge_deposit > 0.0
        and reward_duplicate.route_mode == "dry"
        and reward_duplicate.affect_direction_phi == round(math.pi, 6)
        and reward_duplicate.verified_alignment_score == 0.0
        and pheromone_duplicate.gold_deposit >= 0.0
        and pheromone_duplicate.bridge_deposit == 0.0
        and pheromone_duplicate.evaporation_rate >= pheromone_blocked.evaporation_rate,
        "reward_coefficients_exact": reward_coeffs
        == {
            "epsilon": 0.01,
            "M_max": 64.0,
            "alpha_try": 0.25,
            "beta_speed": 1.0,
            "lambda_speed": 1.0,
            "gamma_assist": 0.5,
            "delta_learn": 0.5,
            "J_star": 4.0,
            "J_d": 0.5,
            "J_r": 0.75,
            "J_a": 1.0,
            "mu": 1.0,
            "nu": 0.35,
            "rho_0": 0.05,
            "rho_1": 0.2,
            "rho_b": 0.1,
            "bridge_weight": 1.0,
        },
        "capillary_formula_nonnegative": capillary_formulas.get("gold_strength_next")
        == "gold_strength_next = (1 - evaporation_rate) * gold_strength + gold_deposit"
        and capillary_formulas.get("bridge_strength_next")
        == "bridge_strength_next = (1 - 0.10) * bridge_strength + bridge_deposit"
        and capillary_formulas.get("compat_edge_strength")
        == "compat_edge_strength = gold_strength_next + bridge_strength_next"
        and capillary_formulas.get("evaporation_rate")
        == "0.05 + 0.20 * (1 - average_verified_alignment_score)",
        "compatibility_projection_present": compatibility_projection
        == {
            "packet.pheromone": "clamp(verified_alignment_score, 0, 1)",
            "receipt.capillary_delta": "max(0, gold_deposit + bridge_deposit)",
            "edge_strength": "compat_edge_strength",
        }
        and set(protocol.get("compatibility_aliases", {}).keys())
        == {"packet.pheromone", "receipt.capillary_delta", "edge.edge_strength"},
        "v1_marked_compatibility_only": compat_registry.get("canonical_protocol_id") == COMMAND_PROTOCOL_ID_V2
        and "compatibility" in str(compat_registry.get("compatibility_role", "")).lower(),
        "protocol_manifest_mentions_v2": contains_all(
            service.config.protocol_manifest_path,
            ["canonical protocol", "v2", "verification-gated", "first verified full closure gets the crown"],
        )
        and contains_all(
            service.config.packet_manifest_path,
            ["canonical packet schema", "reward_state", "verification_state", "pheromone_state"],
        )
        and contains_all(
            service.config.capillary_manifest_path,
            ["canonical law", "no negative reward", "compatibility aliases"],
        ),
        "reward_manifest_mentions_no_punishment": contains_all(
            service.config.reward_field_manifest_path,
            ["no punishment ledger", "trying still earns nectar", "first verified full closure gets the crown"],
        ),
        "latency_equation_present": latency.get("benchmark_id") == "NEXT57_COMMAND_LATENCY_BENCHMARKS_V2"
        and latency.get("equation") == "T_sugar = T_detect + T_encode + T_route + T_claim + T_commit"
        and set(latency.get("fields", []))
        >= {"tau_seconds", "alignment_score", "verified_alignment_score", "reward_multiplier", "crown_tier"},
    }

    result = {
        "generated_at": utc_now(),
        "truth": "OK" if all(checks.values()) else "NEAR",
        "checks": checks,
        "artifacts": {
            "protocol": str(service.config.protocol_json_path),
            "schema": str(service.config.packet_schema_json_path),
            "reward": str(service.config.reward_field_json_path),
            "capillary": str(service.config.capillary_law_json_path),
            "latency": str(service.config.latency_benchmark_json_path),
            "compat_registry": str(service.config.protocol_v1_registry_path),
        },
    }
    VERIFY_PATH.parent.mkdir(parents=True, exist_ok=True)
    VERIFY_PATH.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    LEGACY_VERIFY_PATH.parent.mkdir(parents=True, exist_ok=True)
    LEGACY_VERIFY_PATH.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result


def main() -> int:
    result = verify_command_membrane_protocol()
    print(json.dumps(result, indent=2, ensure_ascii=True))
    return 0 if result.get("truth") == "OK" else 1
