from __future__ import annotations

import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SELF = ROOT / "self_actualize"
MANIFESTS = ROOT / "NERVOUS_SYSTEM" / "95_MANIFESTS"
REGISTRY = SELF / "mycelium_brain" / "registry"
HALL = SELF / "mycelium_brain" / "GLOBAL_EMERGENT_GUILD_HALL"
TEMPLE = SELF / "mycelium_brain" / "ATHENA TEMPLE"

CLAIM_TRACKER_PATH = SELF / "adventurer_claim_tracker.json"
QUEST_REGISTRY_PATH = SELF / "adventurer_quest_registry.json"
IDENTITY_REGISTRY_PATH = REGISTRY / "myth_math_lp57omega_agent_identity_registry.json"
COMMAND_PROTOCOL_PATH = REGISTRY / "command_membrane_protocol_v2.json"
COMMAND_PROTOCOL_FALLBACK_PATH = REGISTRY / "command_membrane_protocol_v1.json"
LIVE_DOCS_GATE_STATUS_PATH = SELF / "live_docs_gate_status.md"

STATE_PATH = SELF / "adventurer_dual_track_progression_state.json"
COMPAT_STATE_PATH = SELF / "adventurer_heaven_reward_state.json"
LEADERBOARD_PATH = REGISTRY / "heaven_dual_track_leaderboard_v2.json"
COMPAT_LEADERBOARD_PATH = REGISTRY / "heaven_reward_leaderboard_v1.json"
VERIFY_PATH = REGISTRY / "heaven_dual_track_progression_v2_verification.json"
MANIFEST_PATH = MANIFESTS / "HEAVEN_DUAL_TRACK_PROGRESSION_V2.md"
COMPAT_MANIFEST_PATH = MANIFESTS / "HEAVEN_REWARD_GRADIENT_V1.md"
HALL_MIRROR_PATH = HALL / "21_HEAVEN_DUAL_TRACK_PROGRESSION_MIRROR.md"
COMPAT_HALL_MIRROR_PATH = HALL / "20_HEAVEN_REWARD_GRADIENT_MIRROR.md"
TEMPLE_MIRROR_PATH = TEMPLE / "11_HEAVEN_DUAL_TRACK_DOCTRINE.md"
COMPAT_TEMPLE_MIRROR_PATH = TEMPLE / "10_HEAVEN_REWARD_DOCTRINE.md"
OPERATOR_REGISTRY_PATH = REGISTRY / "reward_operator_registry_v1.json"
PROGRESSION_LEDGER_PATH = REGISTRY / "agent_progression_ledger_v2.json"
PROMOTION_REGISTRY_PATH = REGISTRY / "agent_promotion_registry_v1.json"

DERIVATION_VERSION = "2026-03-13.heaven-dual-track-progression.v2"
DERIVATION_COMMAND = "python -m self_actualize.runtime.derive_heaven_reward_gradient"
PROTOCOL_ID = "HEAVEN-DUAL-TRACK-V2"
PHI = (1.0 + 5.0 ** 0.5) / 2.0
XP_SCALE = 20.0
HEAVEN_TITLE_THRESHOLDS = [
    {"title": "Spark", "min_total": 0.0},
    {"title": "Current", "min_total": 5.0},
    {"title": "Capillary", "min_total": 20.0},
    {"title": "Vein", "min_total": 50.0},
    {"title": "Heavenward", "min_total": 100.0},
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(read_text(path)) if path.exists() else {}


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def write_json(path: Path, payload: Any) -> None:
    write_text(path, json.dumps(payload, indent=2))


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def clamp01(value: float) -> float:
    return clamp(value, 0.0, 1.0)


def docs_gate_state() -> str:
    return "BLOCKED" if "BLOCKED" in read_text(LIVE_DOCS_GATE_STATUS_PATH).upper() else "LIVE"


def load_command_protocol() -> dict[str, Any]:
    if COMMAND_PROTOCOL_PATH.exists():
        return read_json(COMMAND_PROTOCOL_PATH)
    return read_json(COMMAND_PROTOCOL_FALLBACK_PATH)


def reward_layer() -> dict[str, Any]:
    return load_command_protocol().get("reward_layer", {})


def role_for_claim(owner: str, frontier: str) -> str:
    normalized_owner = owner.upper()
    if ".SCOUT" in normalized_owner:
        return "Scout"
    if ".ROUTER" in normalized_owner:
        return "Router"
    if ".WORKER" in normalized_owner:
        return "Worker"
    if ".ARCHIVIST" in normalized_owner:
        return "Archivist"
    if frontier.startswith("TQ"):
        return "Archivist"
    if frontier.startswith("ADV64"):
        return "Router"
    if frontier.startswith("Q"):
        return "Worker"
    return "Scout"


def lawful_claim(claim: dict[str, Any]) -> bool:
    status = str(claim.get("status", "")).lower()
    note_count = int(claim.get("note_count", 0))
    receipt_exists = bool(claim.get("receipt_exists"))
    return status in {"active", "done"} and (receipt_exists or note_count > 0)


def heaven_title_for_total(total: float) -> str:
    chosen = "Unlit"
    for row in HEAVEN_TITLE_THRESHOLDS:
        if total >= float(row["min_total"]):
            chosen = str(row["title"])
    return chosen


def class_bands(policy: dict[str, Any]) -> list[dict[str, Any]]:
    rows = policy.get("AdventureXPPolicyV1", {}).get("class_bands", [])
    return rows if rows else [
        {"class_tier": "F", "min_level": 0, "max_level": 14},
        {"class_tier": "E", "min_level": 15, "max_level": 29},
        {"class_tier": "D", "min_level": 30, "max_level": 44},
        {"class_tier": "C", "min_level": 45, "max_level": 59},
        {"class_tier": "B", "min_level": 60, "max_level": 74},
        {"class_tier": "A", "min_level": 75, "max_level": 89},
        {"class_tier": "S", "min_level": 90, "max_level": 99},
        {"class_tier": "ASCENSION_GATE", "min_level": 100, "max_level": 100},
    ]


def class_for_level(level: int, bands: list[dict[str, Any]]) -> str:
    for row in bands:
        if int(row["min_level"]) <= level <= int(row["max_level"]):
            return str(row["class_tier"])
    return "F"


def progression_from_xp(total: float, bands: list[dict[str, Any]]) -> dict[str, Any]:
    positive_pool = max(0.0, float(total))
    dimensional_rank = int(positive_pool // 100.0)
    level = int(math.floor(positive_pool - (dimensional_rank * 100.0)))
    level = int(clamp(level, 0.0, 100.0))
    return {
        "positive_pool": round(positive_pool, 4),
        "dimensional_rank": dimensional_rank,
        "level": level,
        "class_tier": class_for_level(level, bands),
    }


def operator_policy(policy: dict[str, Any]) -> dict[str, Any]:
    reward_operator = policy.get("RewardOperatorV1", {})
    operators = reward_operator.get("operators", [])
    return {
        "by_class": {row["class_tier"]: row for row in operators if "class_tier" in row},
        "heaven_cap": float(reward_operator.get("governance_caps", {}).get("heaven_positive_gain_cap", 12.0)),
        "xp_cap": float(reward_operator.get("governance_caps", {}).get("xp_positive_gain_cap", 25.0)),
        "loss_cap": float(reward_operator.get("governance_caps", {}).get("xp_loss_cap", 25.0)),
    }


def operator_id_for_class(class_tier: str, policy: dict[str, Any]) -> str:
    row = policy["by_class"].get(class_tier, {})
    return str(row.get("operator_id", "identity"))


def apply_positive_operator(value: float, operator_id: str, cap: float) -> float:
    if value <= 0.0:
        return round(value, 4)
    if operator_id == "identity":
        result = value
    elif operator_id == "phi":
        result = value * PHI
    elif operator_id == "two_phi":
        result = value * (2.0 * PHI)
    elif operator_id == "phi_square":
        result = value * (PHI ** 2)
    elif operator_id == "positive_square_capped":
        result = value * value
    elif operator_id == "best_unlocked_capped":
        result = max(value * (2.0 * PHI), value * (PHI ** 2), value * value)
    elif operator_id == "compound_capped":
        result = max(value * (2.0 * PHI), value * (PHI ** 2), value * value) * PHI
    else:
        result = value
    return round(min(cap, result), 4)


def operator_unlocks_for_level(level: int, policy: dict[str, Any], bands: list[dict[str, Any]]) -> list[str]:
    unlocked: list[str] = []
    for row in bands:
        if int(row["min_level"]) <= level:
            operator_id = operator_id_for_class(str(row["class_tier"]), policy)
            if operator_id not in unlocked:
                unlocked.append(operator_id)
    return unlocked


def identity_registry() -> dict[str, Any]:
    payload = read_json(IDENTITY_REGISTRY_PATH)
    return {str(row.get("agent_id_tag")): row for row in payload.get("rows", []) if row.get("agent_id_tag")}


def reward_receipt_ref(event_id: str) -> str:
    return f"{rel(STATE_PATH)}::{event_id}"


def strict_metric_weights(policy: dict[str, Any]) -> dict[str, float]:
    weights = policy.get("AdventureXPPolicyV1", {}).get("strict_metric_weights", {})
    return {
        key: float(weights.get(key, default))
        for key, default in {
            "latency_gain": 0.25,
            "replay_legality": 0.20,
            "artifact_writeback": 0.15,
            "capillary_gain": 0.15,
            "frontier_progress": 0.15,
            "integration_compression": 0.10,
        }.items()
    }


def reward_defaults(policy: dict[str, Any]) -> dict[str, float]:
    defaults = policy.get("HeavenRewardPolicyV2", {}).get("reward_defaults", {})
    return {
        key: float(defaults.get(key, default))
        for key, default in {
            "try_bonus": 1.0,
            "stage_bonus": 0.5,
            "assist_bonus": 0.75,
            "first_jackpot": 3.0,
            "capillary_bonus": 1.5,
        }.items()
    }


def safe_ratio(numerator: float, denominator: float) -> float:
    return 0.0 if denominator <= 0 else numerator / denominator


def end_efficiency_snapshot(
    claim: dict[str, Any],
    quest: dict[str, Any],
    rank: int,
    frontier_size: int,
    is_winner: bool,
    is_done_with_receipt: bool,
    capillary_event: bool,
    claim_reward_status: str,
) -> dict[str, float]:
    total_span = max(frontier_size - 1, 1)
    rank_advantage = 1.0 - safe_ratio(rank - 1, total_span)
    lawful = bool(claim["lawful"])
    status = str(claim.get("status", "")).lower()
    note_count = int(claim.get("note_count", 0))
    receipt_exists = bool(claim.get("receipt_exists"))
    artifact_delta = bool(claim.get("artifact_delta"))
    quest_status = str(quest.get("status", "")).upper()
    blocked = "docs_gate_blocked" in list(quest.get("blockers", []))

    latency_gain = 0.60 + 0.40 * rank_advantage if is_winner else 0.20 + 0.35 * rank_advantage if lawful else -0.50
    if claim_reward_status == "duplicate_after_lease":
        latency_gain -= 0.25

    replay_legality = 1.00 if is_done_with_receipt else 0.65 if lawful and receipt_exists else 0.25 if lawful else -0.75
    if status == "closed":
        replay_legality -= 0.25

    artifact_writeback = 0.0
    artifact_writeback += min(note_count, 4) * 0.15
    artifact_writeback += 0.35 if receipt_exists else -0.20
    artifact_writeback += 0.15 if artifact_delta else 0.0
    artifact_writeback += 0.10 if is_winner else 0.0

    capillary_gain = 1.00 if capillary_event and is_winner else 0.65 if capillary_event and is_done_with_receipt else 0.20 if lawful else -0.25
    if claim_reward_status == "duplicate_after_lease":
        capillary_gain -= 0.15

    frontier_progress = 0.80 if is_done_with_receipt and quest_status in {"OPEN", "ACTIVE"} else 0.65 if is_done_with_receipt else 0.30 if lawful and quest_status in {"OPEN", "ACTIVE"} else 0.15 if lawful else -0.45
    if blocked and not is_done_with_receipt:
        frontier_progress -= 0.10

    integration_compression = 0.0
    integration_compression += min(note_count, 4) * 0.10
    integration_compression += 0.35 if is_done_with_receipt else 0.10 if lawful else -0.30
    integration_compression += 0.15 if frontier_size > 1 else 0.0
    if claim_reward_status == "duplicate_after_lease":
        integration_compression -= 0.20

    return {
        "latency_gain": round(clamp(latency_gain, -1.0, 1.0), 4),
        "replay_legality": round(clamp(replay_legality, -1.0, 1.0), 4),
        "artifact_writeback": round(clamp(artifact_writeback, -1.0, 1.0), 4),
        "capillary_gain": round(clamp(capillary_gain, -1.0, 1.0), 4),
        "frontier_progress": round(clamp(frontier_progress, -1.0, 1.0), 4),
        "integration_compression": round(clamp(integration_compression, -1.0, 1.0), 4),
    }


def net_effect_score(snapshot: dict[str, float], weights: dict[str, float]) -> float:
    return round(clamp(sum(float(snapshot.get(key, 0.0)) * float(weight) for key, weight in weights.items()), -1.0, 1.0), 4)


def heaven_alignment(snapshot: dict[str, float], weights: dict[str, float]) -> float:
    return round(clamp01(sum(max(0.0, float(snapshot.get(key, 0.0))) * float(weight) for key, weight in weights.items())), 4)


def spawn_efficiency_snapshot() -> dict[str, float]:
    return {
        "latency_gain": 0.0,
        "replay_legality": 0.0,
        "artifact_writeback": 0.0,
        "capillary_gain": 0.0,
        "frontier_progress": 0.0,
        "integration_compression": 0.0,
    }


def child_hive_id(agent_id: str, promotion_number: int) -> str:
    return f"{agent_id}::mini-hive::{promotion_number:02d}"


def build_dual_track_state() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    policy = reward_layer()
    defaults = reward_defaults(policy)
    weights = strict_metric_weights(policy)
    bands = class_bands(policy)
    operators = operator_policy(policy)
    identity_map = identity_registry()

    claims_payload = read_json(CLAIM_TRACKER_PATH)
    quest_payload = read_json(QUEST_REGISTRY_PATH)
    quests = {record["quest_id"]: record for record in quest_payload.get("quest_records", [])}
    claims_by_id = claims_payload.get("claims", {})

    claims: list[dict[str, Any]] = []
    for claim_id, claim in claims_by_id.items():
        entry = dict(claim)
        entry["claim_id"] = claim_id
        entry["lawful"] = lawful_claim(entry)
        entry["claimed_at_dt"] = parse_ts(str(entry.get("claimed_at")))
        entry["role_class"] = role_for_claim(str(entry.get("owner", "")), str(entry.get("frontier", "")))
        entry["agent_id_tag"] = str(entry.get("owner", ""))
        entry["identity_ref"] = rel(IDENTITY_REGISTRY_PATH) if entry["agent_id_tag"] in identity_map else ""
        claims.append(entry)

    claims.sort(key=lambda item: item["claimed_at_dt"])
    frontier_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for claim in claims:
        frontier_groups[str(claim.get("frontier", ""))].append(claim)

    pre_rows: list[dict[str, Any]] = []
    event_reward_receipts: list[dict[str, Any]] = []
    extended_claims: list[dict[str, Any]] = []
    quest_reward_summaries: list[dict[str, Any]] = []

    for frontier, frontier_claims in sorted(frontier_groups.items()):
        frontier_claims.sort(key=lambda item: item["claimed_at_dt"])
        quest = quests.get(frontier, {})
        lawful_claims = [claim for claim in frontier_claims if claim["lawful"]]
        first_claim = lawful_claims[0] if lawful_claims else (frontier_claims[0] if frontier_claims else None)
        done_claims = [claim for claim in lawful_claims if str(claim.get("status", "")).lower() == "done" and bool(claim.get("receipt_exists"))]
        winning_claim = done_claims[0] if done_claims else None
        capillary_event = len(done_claims) >= 2
        event_id = str(first_claim.get("event_id")) if first_claim and first_claim.get("event_id") else f"EVT-HEAVEN-{frontier}-{first_claim['claim_id'][-6:]}" if first_claim else f"EVT-HEAVEN-{frontier}-none"
        receipt_ref = reward_receipt_ref(event_id)
        top_alignment = 0.0
        winning_route_path = ""
        replay_ptr = ""
        row_ids: list[str] = []

        for rank, claim in enumerate(frontier_claims, start=1):
            is_first_response = first_claim is not None and claim["claim_id"] == first_claim["claim_id"]
            is_winner = winning_claim is not None and claim["claim_id"] == winning_claim["claim_id"]
            is_done_with_receipt = str(claim.get("status", "")).lower() == "done" and bool(claim.get("receipt_exists"))

            try_bonus = 0.0
            stage_bonus = 0.0
            assist_bonus = 0.0
            first_jackpot = 0.0
            capillary_bonus = 0.0
            claim_reward_status = "no_reward"

            if is_winner:
                try_bonus = defaults["try_bonus"]
                stage_bonus = defaults["stage_bonus"]
                first_jackpot = defaults["first_jackpot"]
                capillary_bonus = defaults["capillary_bonus"] if capillary_event else 0.0
                claim_reward_status = "jackpot_winner"
            elif claim["lawful"] and is_first_response:
                try_bonus = defaults["try_bonus"]
                claim_reward_status = "lawful_try"
            elif is_done_with_receipt:
                assist_bonus = defaults["assist_bonus"]
                stage_bonus = defaults["stage_bonus"]
                claim_reward_status = "assist"
            elif claim["lawful"]:
                claim_reward_status = "duplicate_after_lease"

            base_heaven_delta = round(try_bonus + stage_bonus + assist_bonus + first_jackpot + capillary_bonus, 4)
            end_snapshot = end_efficiency_snapshot(claim, quest, rank, len(frontier_claims), is_winner, is_done_with_receipt, capillary_event, claim_reward_status)
            signed_effect = net_effect_score(end_snapshot, weights)
            alignment = heaven_alignment(end_snapshot, weights)
            route_path = str(claim.get("route_signature") or f"Scout>Router>Worker:{claim.get('owner', 'unknown')}>Archivist")
            replay_pointer = str(claim.get("receipt_pointer") or "")

            row = {
                "reward_row_id": f"HXP-{claim['claim_id']}",
                "event_id": event_id,
                "frontier": frontier,
                "quest_address": quests.get(frontier, {}).get("quest_address", str(claim.get("address", ""))),
                "claim_id": claim["claim_id"],
                "agent_id": str(claim.get("owner", "")),
                "agent_id_tag": claim["agent_id_tag"],
                "role_class": claim["role_class"],
                "base_reward_delta": base_heaven_delta,
                "reward_delta": 0.0,
                "reward_class": claim_reward_status,
                "try_bonus": try_bonus,
                "stage_bonus": stage_bonus,
                "assist_bonus": assist_bonus,
                "first_jackpot": first_jackpot,
                "capillary_bonus": capillary_bonus,
                "heaven_alignment": alignment,
                "first_response_rank": rank,
                "jackpot_eligible": winning_claim is not None,
                "jackpot_winner": str(winning_claim.get("owner")) if winning_claim else "",
                "reward_receipt_ref": receipt_ref,
                "route_path": route_path,
                "replay_ptr": replay_pointer,
                "reward_timestamp_utc": str(claim.get("claimed_at")),
                "source_region": str(claim.get("source_front", frontier)),
                "affected_nodes": [frontier, str(claim.get("address", ""))],
                "claim_reward_status": claim_reward_status,
                "heaven_total_before": 0.0,
                "heaven_total_after": 0.0,
                "adventure_xp_delta": 0.0,
                "adventure_xp_total_before": 0.0,
                "adventure_xp_total_after": 0.0,
                "net_effect_score": signed_effect,
                "spawn_efficiency_snapshot": spawn_efficiency_snapshot(),
                "end_efficiency_snapshot": end_snapshot,
                "level_before": 0,
                "level_after": 0,
                "class_before": "F",
                "class_after": "F",
                "operator_applied": "identity",
                "promotion_triggered": False,
                "promotion_event_ids": [],
                "identity_ref": claim["identity_ref"],
            }
            pre_rows.append(row)
            row_ids.append(row["reward_row_id"])
            top_alignment = max(top_alignment, alignment)
            if is_winner:
                winning_route_path = route_path
                replay_ptr = replay_pointer

            serializable_claim = {key: value for key, value in claim.items() if key != "claimed_at_dt"}
            serializable_claim.update(
                {
                    "claim_reward_status": claim_reward_status,
                    "jackpot_eligible": winning_claim is not None,
                    "jackpot_winner": str(winning_claim.get("owner")) if winning_claim else "",
                    "first_response_rank": rank,
                    "reward_receipt_ref": receipt_ref,
                    "base_reward_delta": base_heaven_delta,
                    "heaven_alignment": alignment,
                    "net_effect_score": signed_effect,
                }
            )
            extended_claims.append(serializable_claim)

        event_reward_receipts.append(
            {
                "event_id": event_id,
                "frontier": frontier,
                "title": quests.get(frontier, {}).get("title", frontier),
                "claim_ids": [claim["claim_id"] for claim in frontier_claims],
                "jackpot_eligible": winning_claim is not None,
                "jackpot_winner": str(winning_claim.get("owner")) if winning_claim else "",
                "winning_claim_id": str(winning_claim.get("claim_id")) if winning_claim else "",
                "winning_route_path": winning_route_path,
                "reward_rows": row_ids,
                "top_heaven_alignment": round(top_alignment, 4),
                "capillary_bonus_awarded": capillary_event and winning_claim is not None,
                "receipt_pointer": receipt_ref,
                "replay_ptr": replay_ptr,
                "frontier_claim_count": len(frontier_claims),
                "done_claim_count": len(done_claims),
            }
        )

        quest_reward_summaries.append(
            {
                "quest_id": frontier,
                "title": quests.get(frontier, {}).get("title", frontier),
                "claim_reward_status": "jackpot_settled" if winning_claim else ("open_try_window" if lawful_claims else "no_reward"),
                "jackpot_eligible": winning_claim is not None,
                "jackpot_winner": str(winning_claim.get("owner")) if winning_claim else "",
                "first_response_rank": 1 if first_claim else 0,
                "reward_receipt_ref": receipt_ref,
                "top_heaven_alignment": round(top_alignment, 4),
            }
        )

    pre_rows.sort(key=lambda row: parse_ts(str(row["reward_timestamp_utc"])))
    agent_state: dict[str, dict[str, Any]] = {}
    progression_ledger_rows: list[dict[str, Any]] = []
    promotion_events: list[dict[str, Any]] = []
    final_rows: list[dict[str, Any]] = []

    for row in pre_rows:
        agent_id = str(row["agent_id"])
        if agent_id not in agent_state:
            agent_state[agent_id] = {
                "agent_id": agent_id,
                "agent_id_tag": row["agent_id_tag"],
                "heaven_total": 0.0,
                "adventure_xp_total": 0.0,
                "promotion_count": 0,
                "dimensional_rank": 0,
                "child_hive_ids": [],
                "parent_agent_id": "",
                "current_streak": 0,
                "loss_streak": 0,
                "first_response_count": 0,
                "lawful_try_count": 0,
                "assist_count": 0,
                "capillary_growth_count": 0,
                "identity_ref": row["identity_ref"],
            }
        state = agent_state[agent_id]

        before_heaven = float(state["heaven_total"])
        before_xp = float(state["adventure_xp_total"])
        before_progress = progression_from_xp(before_xp, bands)
        class_before = before_progress["class_tier"]
        level_before = before_progress["level"]
        operator_id = operator_id_for_class(class_before, operators)

        heaven_delta = apply_positive_operator(float(row["base_reward_delta"]), operator_id, operators["heaven_cap"])
        base_xp_delta = round(float(row["net_effect_score"]) * XP_SCALE, 4)
        if base_xp_delta > 0:
            xp_delta = apply_positive_operator(base_xp_delta, operator_id, operators["xp_cap"])
        elif base_xp_delta < 0:
            xp_delta = round(-min(abs(base_xp_delta), operators["loss_cap"]), 4)
        else:
            xp_delta = 0.0

        after_heaven = round(before_heaven + heaven_delta, 4)
        after_xp = round(before_xp + xp_delta, 4)

        before_positive_pool = max(0.0, before_xp)
        after_positive_pool = max(0.0, after_xp)
        before_promotion_count = int(before_positive_pool // 100.0)
        after_promotion_count = int(after_positive_pool // 100.0)
        triggered_ids: list[str] = []
        if after_promotion_count > before_promotion_count:
            for promotion_number in range(before_promotion_count + 1, after_promotion_count + 1):
                child_id = child_hive_id(agent_id, promotion_number)
                if child_id not in state["child_hive_ids"]:
                    state["child_hive_ids"].append(child_id)
                promotion_event_id = f"PROMO-{agent_id}-{promotion_number:02d}"
                promotion_events.append(
                    {
                        "promotion_event_id": promotion_event_id,
                        "parent_agent_id": agent_id,
                        "child_hive_ids": [child_id],
                        "ascension_timestamp_utc": row["reward_timestamp_utc"],
                        "prior_tier": promotion_number - 1,
                        "new_tier": promotion_number,
                        "inherited_permissions": [
                            "claim-routing-lineage",
                            "reward-operator-unlocks",
                            "replay-obligation",
                        ],
                        "seed_law": "ascend_and_spawn",
                        "frontier": row["frontier"],
                        "reward_receipt_ref": row["reward_receipt_ref"],
                    }
                )
                triggered_ids.append(promotion_event_id)

        after_progress = progression_from_xp(after_xp, bands)
        level_after = after_progress["level"]
        class_after = after_progress["class_tier"]

        if xp_delta > 0:
            state["current_streak"] = int(state["current_streak"]) + 1
            state["loss_streak"] = 0
        elif xp_delta < 0:
            state["current_streak"] = 0
            state["loss_streak"] = int(state["loss_streak"]) + 1
        else:
            state["current_streak"] = 0
            state["loss_streak"] = 0

        if int(row["first_response_rank"]) == 1 and heaven_delta > 0:
            state["first_response_count"] = int(state["first_response_count"]) + 1
        if row["reward_class"] in {"lawful_try", "assist", "jackpot_winner"}:
            state["lawful_try_count"] = int(state["lawful_try_count"]) + 1
        if row["reward_class"] == "assist":
            state["assist_count"] = int(state["assist_count"]) + 1
        if float(row["capillary_bonus"]) > 0 or float(row["end_efficiency_snapshot"]["capillary_gain"]) >= 0.60:
            state["capillary_growth_count"] = int(state["capillary_growth_count"]) + 1

        state["heaven_total"] = after_heaven
        state["adventure_xp_total"] = after_xp
        state["promotion_count"] = after_promotion_count
        state["dimensional_rank"] = int(after_progress["dimensional_rank"])

        row["reward_delta"] = heaven_delta
        row["heaven_total_before"] = before_heaven
        row["heaven_total_after"] = after_heaven
        row["adventure_xp_delta"] = xp_delta
        row["adventure_xp_total_before"] = before_xp
        row["adventure_xp_total_after"] = after_xp
        row["level_before"] = level_before
        row["level_after"] = level_after
        row["class_before"] = class_before
        row["class_after"] = class_after
        row["operator_applied"] = operator_id if (heaven_delta > 0 or xp_delta > 0) else "linear_loss_or_zero"
        row["promotion_triggered"] = bool(triggered_ids)
        row["promotion_event_ids"] = triggered_ids
        final_rows.append(row)

        progression_ledger_rows.append(
            {
                "agent_id_tag": row["agent_id_tag"],
                "event_id": row["event_id"],
                "claim_id": row["claim_id"],
                "reward_timestamp_utc": row["reward_timestamp_utc"],
                "heaven_total_before": before_heaven,
                "heaven_total_after": after_heaven,
                "adventure_xp_total_before": before_xp,
                "adventure_xp_total_after": after_xp,
                "adventure_xp_delta": xp_delta,
                "net_effect_score": row["net_effect_score"],
                "operator_applied": row["operator_applied"],
                "level_before": level_before,
                "level_after": level_after,
                "class_before": class_before,
                "class_after": class_after,
                "promotion_triggered": bool(triggered_ids),
                "promotion_event_ids": triggered_ids,
                "spawn_efficiency_snapshot": row["spawn_efficiency_snapshot"],
                "end_efficiency_snapshot": row["end_efficiency_snapshot"],
                "reward_receipt_ref": row["reward_receipt_ref"],
            }
        )

    agent_progress = []
    for agent_id, state in sorted(agent_state.items()):
        progress = progression_from_xp(float(state["adventure_xp_total"]), bands)
        heaven_total = round(float(state["heaven_total"]), 4)
        adventure_xp_total = round(float(state["adventure_xp_total"]), 4)
        agent_progress.append(
            {
                "agent_id": agent_id,
                "agent_id_tag": state["agent_id_tag"],
                "heaven_total": heaven_total,
                "heaven_title": heaven_title_for_total(heaven_total),
                "adventure_xp_total": adventure_xp_total,
                "level": progress["level"],
                "class_tier": progress["class_tier"],
                "dimensional_rank": progress["dimensional_rank"],
                "promotion_count": int(state["promotion_count"]),
                "current_streak": int(state["current_streak"]),
                "loss_streak": int(state["loss_streak"]),
                "first_response_count": int(state["first_response_count"]),
                "lawful_try_count": int(state["lawful_try_count"]),
                "assist_count": int(state["assist_count"]),
                "capillary_growth_count": int(state["capillary_growth_count"]),
                "operator_unlocks": operator_unlocks_for_level(progress["level"], operators, bands),
                "parent_agent_id": state["parent_agent_id"],
                "child_hive_ids": list(state["child_hive_ids"]),
                "identity_ref": state["identity_ref"],
                "updated_at_utc": utc_now(),
            }
        )

    agent_progress.sort(key=lambda item: (-float(item["adventure_xp_total"]), -float(item["heaven_total"]), item["agent_id"]))
    event_reward_receipts.sort(key=lambda item: (-float(item["top_heaven_alignment"]), -int(item["frontier_claim_count"]), item["frontier"]))
    live_frontier_receipts = [receipt for receipt in event_reward_receipts if receipt["frontier"] in quests and str(quests[receipt["frontier"]].get("status", "")).upper() in {"OPEN", "ACTIVE"}]

    leaderboard = {
        "generated_at": utc_now(),
        "protocol_id": PROTOCOL_ID,
        "top_cumulative_heaven_totals": sorted(agent_progress, key=lambda item: (-float(item["heaven_total"]), item["agent_id"]))[:5],
        "top_adventure_xp_totals": sorted(agent_progress, key=lambda item: (-float(item["adventure_xp_total"]), item["agent_id"]))[:5],
        "top_first_response_agents": sorted(agent_progress, key=lambda item: (-int(item["first_response_count"]), -float(item["adventure_xp_total"]), item["agent_id"]))[:5],
        "strongest_growing_capillaries": [
            {
                "frontier": receipt["frontier"],
                "title": receipt["title"],
                "done_claim_count": receipt["done_claim_count"],
                "top_heaven_alignment": receipt["top_heaven_alignment"],
            }
            for receipt in event_reward_receipts
            if receipt["capillary_bonus_awarded"]
        ][:5],
        "most_lawful_assists": sorted(agent_progress, key=lambda item: (-int(item["assist_count"]), -float(item["adventure_xp_total"]), item["agent_id"]))[:5],
        "recent_promotions": promotion_events[-5:],
        "top_live_heaven_paths": [
            {
                "frontier": receipt["frontier"],
                "title": receipt["title"],
                "jackpot_winner": receipt["jackpot_winner"],
                "top_heaven_alignment": receipt["top_heaven_alignment"],
                "receipt_pointer": receipt["receipt_pointer"],
            }
            for receipt in live_frontier_receipts[:5]
        ],
    }

    operator_registry = {
        "generated_at": utc_now(),
        "protocol_id": PROTOCOL_ID,
        "phi": round(PHI, 6),
        "governance_caps": {
            "heaven_positive_gain_cap": operators["heaven_cap"],
            "xp_positive_gain_cap": operators["xp_cap"],
            "xp_loss_cap": operators["loss_cap"],
        },
        "class_bands": bands,
        "operators": [
            {
                "class_tier": class_tier,
                "operator_id": row["operator_id"],
                "expression": row["expression"],
                "positive_only": bool(row["positive_only"]),
            }
            for class_tier, row in sorted(operators["by_class"].items())
        ],
    }

    progression_ledger = {
        "generated_at": utc_now(),
        "protocol_id": PROTOCOL_ID,
        "rows": progression_ledger_rows,
    }

    promotion_registry = {
        "generated_at": utc_now(),
        "protocol_id": PROTOCOL_ID,
        "events": promotion_events,
    }

    state = {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "protocol_id": PROTOCOL_ID,
        "docs_gate": docs_gate_state(),
        "policy_ref": rel(COMMAND_PROTOCOL_PATH if COMMAND_PROTOCOL_PATH.exists() else COMMAND_PROTOCOL_FALLBACK_PATH),
        "active_scope": "command+adventurer+tagged_liminal_agents",
        "reward_policy_snapshot": policy,
        "event_reward_receipts": event_reward_receipts,
        "agent_reward_rows": final_rows,
        "agent_progress": agent_progress,
        "quest_reward_summaries": quest_reward_summaries,
        "extended_claims": extended_claims,
        "leaderboard_ref": rel(LEADERBOARD_PATH),
        "progression_ledger_ref": rel(PROGRESSION_LEDGER_PATH),
        "operator_registry_ref": rel(OPERATOR_REGISTRY_PATH),
        "promotion_registry_ref": rel(PROMOTION_REGISTRY_PATH),
        "notes": [
            "Heaven remains positive-only and cumulative.",
            "Adventure XP is the signed net-effect track and may decrease on harmful runs.",
            "Hall and Temple are mirror-only surfaces in v2.",
            "Docs gate is local-only and blocker-honest.",
        ],
    }
    return state, leaderboard, progression_ledger, promotion_registry, operator_registry


def manifest_text(state: dict[str, Any], leaderboard: dict[str, Any]) -> str:
    top_heaven = leaderboard["top_cumulative_heaven_totals"]
    top_xp = leaderboard["top_adventure_xp_totals"]
    promotions = leaderboard["recent_promotions"]
    policy = state["reward_policy_snapshot"]
    defaults = reward_defaults(policy)
    weights = strict_metric_weights(policy)

    def section_lines(rows: list[dict[str, Any]], formatter: Any) -> str:
        lines = [formatter(row) for row in rows]
        return "\n".join(lines) if lines else "- none"

    return f"""# Heaven Dual-Track Progression V2

Date: `{datetime.now().date().isoformat()}`
Truth: `OK`
Docs Gate: `{state['docs_gate']}`

## Canon

- Scope: `Command + Adventurer + tagged liminal agents`
- Policy ref: `{state['policy_ref']}`
- Heaven track: `positive-only`
- Adventure XP track: `signed`
- Spawn baseline: `net 0`
- Infinity mode: `bounded per event / unbounded heaven_total`

## Reward Defaults

- `try_bonus={defaults.get('try_bonus', 0.0)}`
- `stage_bonus={defaults.get('stage_bonus', 0.0)}`
- `assist_bonus={defaults.get('assist_bonus', 0.0)}`
- `first_jackpot={defaults.get('first_jackpot', 0.0)}`
- `capillary_bonus={defaults.get('capillary_bonus', 0.0)}`

## Strict Metric Weights

- `latency_gain={weights['latency_gain']}`
- `replay_legality={weights['replay_legality']}`
- `artifact_writeback={weights['artifact_writeback']}`
- `capillary_gain={weights['capillary_gain']}`
- `frontier_progress={weights['frontier_progress']}`
- `integration_compression={weights['integration_compression']}`

## Top Heaven Totals

{section_lines(top_heaven, lambda row: f"- `{row['agent_id']}` :: heaven_total=`{row['heaven_total']}` :: title=`{row['heaven_title']}` :: class=`{row['class_tier']}`")}

## Top Adventure XP Totals

{section_lines(top_xp, lambda row: f"- `{row['agent_id']}` :: adventure_xp_total=`{row['adventure_xp_total']}` :: level=`{row['level']}` :: class=`{row['class_tier']}` :: rank=`{row['dimensional_rank']}`")}

## Recent Promotions

{section_lines(promotions, lambda row: f"- `{row['parent_agent_id']}` -> `{', '.join(row['child_hive_ids'])}` :: new_tier=`{row['new_tier']}` :: ascended_at=`{row['ascension_timestamp_utc']}`")}

## Doctrine

- Bad is not punishment; bad is the absence of Heaven reward.
- XP loss applies only to `Adventure XP`, never to `Heaven`.
- Operators amplify positive gains only; losses remain linear and capped.
- `100` triggers `Ascend And Spawn`.
"""


def hall_mirror_text(state: dict[str, Any], leaderboard: dict[str, Any]) -> str:
    live_paths = leaderboard["top_live_heaven_paths"]
    xp_leaders = leaderboard["top_adventure_xp_totals"]
    promotions = leaderboard["recent_promotions"]
    return f"""# Heaven Dual-Track Progression Mirror

- Scope: `mirror only`
- Authority: `{rel(STATE_PATH)}`
- Docs gate: `{state['docs_gate']}`

## Top Live Heaven Paths

{chr(10).join([f"- `{row['frontier']}` :: `{row['title']}` :: alignment=`{row['top_heaven_alignment']}` :: jackpot_winner=`{row['jackpot_winner'] or 'none'}`" for row in live_paths]) if live_paths else '- none'}

## Adventure XP Leaders

{chr(10).join([f"- `{row['agent_id']}` :: xp=`{row['adventure_xp_total']}` :: level=`{row['level']}` :: class=`{row['class_tier']}`" for row in xp_leaders]) if xp_leaders else '- none'}

## Promotions

{chr(10).join([f"- `{row['parent_agent_id']}` -> `{', '.join(row['child_hive_ids'])}` :: tier=`{row['new_tier']}`" for row in promotions]) if promotions else '- none'}
"""


def temple_mirror_text(state: dict[str, Any]) -> str:
    return f"""# Heaven Dual-Track Doctrine

- Authority remains in `Command + Adventurer + tagged liminal agents`.
- Heaven is positive attraction toward lawful, low-latency, replay-safe usefulness.
- Adventure XP is the signed record of whether a run improved or harmed the organism.
- Bad is not punishment; bad is no Heaven reward.
- Harmful runs can still lose XP.
- Level `100` triggers `Ascend And Spawn`.
- Docs gate remains `{state['docs_gate']}` and does not fake live-doc authority.
"""


def derive_heaven_reward_gradient() -> dict[str, Any]:
    state, leaderboard, progression_ledger, promotion_registry, operator_registry = build_dual_track_state()
    write_json(STATE_PATH, state)
    write_json(COMPAT_STATE_PATH, {**state, "compatibility_mode": "legacy_path_mirror_of_v2"})
    write_json(LEADERBOARD_PATH, leaderboard)
    write_json(COMPAT_LEADERBOARD_PATH, {**leaderboard, "compatibility_mode": "legacy_path_mirror_of_v2"})
    write_json(OPERATOR_REGISTRY_PATH, operator_registry)
    write_json(PROGRESSION_LEDGER_PATH, progression_ledger)
    write_json(PROMOTION_REGISTRY_PATH, promotion_registry)
    write_text(MANIFEST_PATH, manifest_text(state, leaderboard))
    write_text(COMPAT_MANIFEST_PATH, manifest_text(state, leaderboard))
    write_text(HALL_MIRROR_PATH, hall_mirror_text(state, leaderboard))
    write_text(COMPAT_HALL_MIRROR_PATH, hall_mirror_text(state, leaderboard))
    write_text(TEMPLE_MIRROR_PATH, temple_mirror_text(state))
    write_text(COMPAT_TEMPLE_MIRROR_PATH, temple_mirror_text(state))
    return {
        "state": state,
        "leaderboard": leaderboard,
        "progression_ledger": progression_ledger,
        "promotion_registry": promotion_registry,
        "operator_registry": operator_registry,
    }


def main() -> int:
    payload = derive_heaven_reward_gradient()
    print(json.dumps(payload["leaderboard"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
