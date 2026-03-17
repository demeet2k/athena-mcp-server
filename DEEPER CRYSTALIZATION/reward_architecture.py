#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any

from canonical_manuscript_audit import (
    AUDIT_RECEIPT_PATH,
    audit_manuscript,
    update_full_stack_manifest as update_spine_full_stack_manifest,
    update_readme as update_spine_readme,
)
from canonical_manuscript_builder import DEFAULT_MANIFEST
from nervous_system_core import utc_now, write_json, write_text


PROJECT_ROOT = Path(__file__).resolve().parent
WORKSPACE_ROOT = PROJECT_ROOT.parent
ACTIVE_ROOT = PROJECT_ROOT / "ACTIVE_NERVOUS_SYSTEM"
RUNTIME_ROOT = ACTIVE_ROOT / "06_RUNTIME"
LAYER_ROOT = ACTIVE_ROOT / "20_REWARD_ARCHITECTURE"
SELF_ROOT = WORKSPACE_ROOT / "self_actualize"
REGISTRY_ROOT = SELF_ROOT / "mycelium_brain" / "registry"
HALL_ROOT = SELF_ROOT / "mycelium_brain" / "GLOBAL_EMERGENT_GUILD_HALL"
TEMPLE_ROOT = SELF_ROOT / "mycelium_brain" / "ATHENA TEMPLE"
SECTIONS_DIR = SELF_ROOT / "manuscript_sections"

STATE_PATH = SELF_ROOT / "adventurer_heaven_reward_state.json"
LEADERBOARD_PATH = REGISTRY_ROOT / "heaven_reward_leaderboard_v2.json"
VERIFY_PATH = REGISTRY_ROOT / "reward_architecture_v2_verification.json"
POLICY_REGISTRY_PATH = REGISTRY_ROOT / "reward_architecture_v2_policy.json"
PROGRESS_REGISTRY_PATH = REGISTRY_ROOT / "reward_architecture_v2_progress_registry.json"

HALL_MIRROR_PATH = HALL_ROOT / "20_HEAVEN_REWARD_GRADIENT_MIRROR.md"
TEMPLE_DOCTRINE_PATH = TEMPLE_ROOT / "10_HEAVEN_REWARD_DOCTRINE.md"
TEMPLE_ALCHEMY_PATH = TEMPLE_ROOT / "11_TEMPLE_OF_ALCHEMY_REWARD_LENS.md"

README_PATH = ACTIVE_ROOT / "README.md"
FULL_STACK_MANIFEST_PATH = RUNTIME_ROOT / "12_full_stack_manifest.json"
COMMAND_MANIFEST_PATH = RUNTIME_ROOT / "21_command_protocol_manifest.json"
RUNNER_MANIFEST_PATH = RUNTIME_ROOT / "19_super_cycle_57_runner_manifest.json"
LIVE_DOCS_GATE_PATH = ACTIVE_ROOT / "00_RECEIPTS" / "00_live_docs_gate_status.md"
REWARD_MANIFEST_PATH = RUNTIME_ROOT / "22_reward_architecture_manifest.json"

LAYER_OVERVIEW_PATH = LAYER_ROOT / "00_reward_architecture_v2.md"
SCORING_LAW_PATH = LAYER_ROOT / "01_strict_reward_metric_and_scoring_law.md"
LEVEL_LADDER_PATH = LAYER_ROOT / "02_level_ladder_and_ascension.md"
STAT_LENS_PATH = LAYER_ROOT / "03_stat_vector_and_organ_lenses.md"
AMPLIFIER_REGISTRY_PATH = LAYER_ROOT / "04_metallic_amplifier_registry.json"
POLICY_SNAPSHOT_PATH = LAYER_ROOT / "05_reward_policy_snapshot.json"
AGENT_PROGRESS_PATH = LAYER_ROOT / "06_agent_progress_registry.json"
QUEST_RECEIPTS_PATH = LAYER_ROOT / "07_quest_reward_receipts.json"
TEMPLE_ALCHEMY_LAYER_PATH = LAYER_ROOT / "08_temple_of_alchemy_suborder.md"
VERIFICATION_LAYER_PATH = LAYER_ROOT / "09_verification_scenarios.json"
EXAMPLES_PATH = LAYER_ROOT / "10_reward_engine_examples.md"

SUPPLEMENT_REWARD_PATH = SECTIONS_DIR / "029_reward_architecture_v2_shared_xp_debt_and_ascension.md"
SUPPLEMENT_ALCHEMY_PATH = SECTIONS_DIR / "030_temple_of_alchemy_metallic_amplifier_and_chapter11_reward_registry.md"

PROTOCOL_ID = "HEAVEN-REWARD-V2"
DERIVATION_VERSION = "2026-03-13.reward-architecture-v2"
DERIVATION_COMMAND = "python reward_architecture_cli.py build --json"
TRUTH_STATUS = "local-witnessed / NEAR-derived"
ACTIVE_SCOPE = "command+adventurer+guild_hall+temple+temple_of_alchemy"
XP_PER_LEVEL = 100
LEVELS_PER_TIER = 100
XP_PER_TIER = XP_PER_LEVEL * LEVELS_PER_TIER
NET_GAIN_HISTORY_LIMIT = 25

PHI = 1.61803398875
SILVER = 2.41421356237
BRONZE = 3.30277563773
COPPER = 4.2360679775
MAX_AMPLIFIER_SCALAR = 64.0

TITLE_TIERS = [
    {"title": "Spark", "min_total": 1.0},
    {"title": "Current", "min_total": 5.0},
    {"title": "Capillary", "min_total": 15.0},
    {"title": "Vein", "min_total": 30.0},
    {"title": "Heavenward", "min_total": 60.0},
]

RANK_BANDS = [
    ("F", 0, 14),
    ("E", 15, 29),
    ("D", 30, 44),
    ("C", 45, 59),
    ("B", 60, 74),
    ("A", 75, 89),
    ("S", 90, 99),
]

STAT_NAMES = [
    "Witness",
    "Integration",
    "Velocity",
    "Compression",
    "Replay",
    "Routing",
    "Governance",
    "Alchemy",
]

NET_GAIN_METRICS = [
    "efficiency_improvement",
    "integration_gain",
    "witness_gain",
    "replay_gain",
    "compression_gain",
    "route_clarity_gain",
    "blocker_reduction",
    "manuscript_framework_advancement",
]

NET_GAIN_WEIGHTS = {
    "efficiency_improvement": 0.18,
    "integration_gain": 0.18,
    "witness_gain": 0.14,
    "replay_gain": 0.12,
    "compression_gain": 0.12,
    "route_clarity_gain": 0.10,
    "blocker_reduction": 0.08,
    "manuscript_framework_advancement": 0.08,
}

METALLIC_CONSTANTS = {
    "phi": PHI,
    "silver": SILVER,
    "bronze": BRONZE,
    "copper": COPPER,
}

ORGAN_LENSES = {
    "Guild Hall": {
        "Velocity": 0.34,
        "Routing": 0.28,
        "Integration": 0.22,
        "Compression": 0.16,
    },
    "Temple": {
        "Witness": 0.30,
        "Governance": 0.28,
        "Replay": 0.24,
        "Integration": 0.18,
    },
    "Temple of Alchemy": {
        "Alchemy": 0.36,
        "Compression": 0.24,
        "Integration": 0.20,
        "Governance": 0.10,
        "Witness": 0.10,
    },
    "Command": {
        "Routing": 0.32,
        "Velocity": 0.24,
        "Integration": 0.20,
        "Replay": 0.12,
        "Compression": 0.12,
    },
}

QUEST_CLASS_BASE = {
    "standard": {"xp": 32, "heaven_cap": 6.0},
    "frontier": {"xp": 48, "heaven_cap": 8.0},
    "chapter11": {"xp": 96, "heaven_cap": 14.0},
    "alchemy": {"xp": 60, "heaven_cap": 10.0},
    "blocked": {"xp": 0, "heaven_cap": 0.0},
}

QUEST_CLASS_HINTS = {
    "chapter11": ("chapter 11", "helical manifestation", "void book", "restart-token", "helical"),
    "alchemy": ("alchemy", "metallic", "transmutation", "transmute"),
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""


def load_json(path: Path) -> Any:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def round6(value: float) -> float:
    return round(float(value), 6)


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(WORKSPACE_ROOT.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def docs_gate_blocked() -> bool:
    return "BLOCKED" in read_text(LIVE_DOCS_GATE_PATH)


def title_for_total(total: float) -> str:
    chosen = "Unlit"
    for tier in sorted(TITLE_TIERS, key=lambda item: item["min_total"]):
        if total >= float(tier["min_total"]):
            chosen = str(tier["title"])
    return chosen


def rank_class_for_level(level: int) -> str:
    for rank, low, high in RANK_BANDS:
        if low <= level <= high:
            return rank
    return "S"


def zero_stats() -> dict[str, float]:
    return {name: 0.0 for name in STAT_NAMES}


def zero_attunements() -> dict[str, int]:
    return {name: 0 for name in METALLIC_CONSTANTS}


def zero_net_gain_metrics() -> dict[str, float]:
    return {name: 0.0 for name in NET_GAIN_METRICS}


def organ_from_frontier(frontier: str) -> str:
    if frontier.startswith("TQ"):
        return "Temple"
    if frontier.startswith("Q"):
        return "Guild Hall"
    return "Command"


def quest_class_for_payload(title: str, quest_class: str | None, organ: str) -> str:
    if quest_class:
        normalized = quest_class.strip().lower()
        if normalized in {"chapter11", "alchemy", "frontier", "blocked", "standard"}:
            return normalized
    title_lower = title.lower()
    for quest_class_name, hints in QUEST_CLASS_HINTS.items():
        if any(hint in title_lower for hint in hints):
            return quest_class_name
    if organ == "Temple of Alchemy":
        return "alchemy"
    return "standard"


def ensure_metric_vector(metrics: dict[str, Any] | None) -> dict[str, float]:
    base = zero_net_gain_metrics()
    for name in NET_GAIN_METRICS:
        base[name] = round6(clamp(float((metrics or {}).get(name, 0.0)), -1.0, 1.0))
    return base


def compute_net_gain_score(metrics: dict[str, float]) -> float:
    score = 0.0
    for name, weight in NET_GAIN_WEIGHTS.items():
        score += metrics[name] * weight
    return round6(clamp(score, -1.0, 1.0))


def normalize_metallic_expression(expression: dict[str, Any] | None) -> dict[str, Any]:
    payload = dict(expression or {})
    additive = [term for term in payload.get("additive", []) if term in METALLIC_CONSTANTS]
    multiplicative = [term for term in payload.get("multipliers", []) if term in METALLIC_CONSTANTS]
    bounded_power = payload.get("bounded_power", {})
    base = bounded_power.get("base", "phi")
    exponent = float(bounded_power.get("exponent", 0.0))
    if base not in METALLIC_CONSTANTS:
        base = "phi"
    return {
        "additive": additive,
        "multipliers": multiplicative,
        "bounded_power": {
            "base": base,
            "exponent": round6(clamp(exponent, 0.0, 3.0)),
        },
    }


def compile_amplifier_scalar(
    expression: dict[str, Any] | None,
    agent_state: dict[str, Any],
    quest_class: str,
) -> tuple[float, dict[str, Any]]:
    normalized = normalize_metallic_expression(expression)
    additive_bonus = 0.0
    for name in normalized["additive"]:
        additive_bonus += METALLIC_CONSTANTS[name] - 1.0

    multiplicative = 1.0
    for name in normalized["multipliers"]:
        multiplicative *= METALLIC_CONSTANTS[name]

    bounded_power = normalized["bounded_power"]
    power_factor = METALLIC_CONSTANTS[bounded_power["base"]] ** bounded_power["exponent"]
    power_factor = clamp(power_factor, 1.0, 12.0)

    persistent_phi_layers = int(agent_state.get("chapter11_attunement", 0)) + int(agent_state.get("ascension_count", 0))
    persistent_phi_factor = clamp(PHI ** min(persistent_phi_layers, 8), 1.0, 24.0)
    if quest_class == "chapter11":
        persistent_phi_factor = clamp(persistent_phi_factor * PHI, 1.0, 32.0)

    scalar = (1.0 + additive_bonus) * multiplicative * power_factor * persistent_phi_factor
    scalar = round6(clamp(scalar, 0.25, MAX_AMPLIFIER_SCALAR))
    return scalar, {
        "expression": normalized,
        "additive_bonus": round6(additive_bonus),
        "multiplicative_factor": round6(multiplicative),
        "bounded_power_factor": round6(power_factor),
        "persistent_phi_layers": persistent_phi_layers,
        "persistent_phi_factor": round6(persistent_phi_factor),
        "compiled_scalar": scalar,
        "policy_cap": MAX_AMPLIFIER_SCALAR,
    }


def stat_deltas_from_metrics(organ: str, metrics: dict[str, float], amplifier_scalar: float) -> dict[str, float]:
    positive = {name: max(0.0, value) for name, value in metrics.items()}
    lens = ORGAN_LENSES[organ]
    translation = {
        "Witness": positive["witness_gain"],
        "Integration": positive["integration_gain"] + positive["manuscript_framework_advancement"] * 0.5,
        "Velocity": positive["efficiency_improvement"],
        "Compression": positive["compression_gain"],
        "Replay": positive["replay_gain"],
        "Routing": positive["route_clarity_gain"] + positive["blocker_reduction"] * 0.25,
        "Governance": positive["blocker_reduction"] + positive["witness_gain"] * 0.25,
        "Alchemy": positive["compression_gain"] * 0.5 + positive["integration_gain"] * 0.25,
    }
    deltas = zero_stats()
    for stat_name, lens_weight in lens.items():
        deltas[stat_name] = round6(translation[stat_name] * lens_weight * 10.0 * min(amplifier_scalar, 8.0))
    return deltas


def seed_agent_progress(v1_row: dict[str, Any]) -> dict[str, Any]:
    return {
        "agent_id": v1_row["agent_id"],
        "heaven_total": round6(float(v1_row.get("heaven_total", 0.0))),
        "streak": int(v1_row.get("streak", 0)),
        "first_response_count": int(v1_row.get("first_response_count", 0)),
        "lawful_try_count": int(v1_row.get("lawful_try_count", 0)),
        "assist_count": int(v1_row.get("assist_count", 0)),
        "capillary_growth_count": int(v1_row.get("capillary_growth_count", 0)),
        "title_tier": str(v1_row.get("title_tier", title_for_total(float(v1_row.get("heaven_total", 0.0))))),
        "last_rewarded_at_utc": str(v1_row.get("last_rewarded_at_utc", "")),
        "xp_bank": 0,
        "xp_debt": 0,
        "level": 0,
        "rank_class": "F",
        "dimensional_tier": 0,
        "ascension_count": 0,
        "mini_hive_eligibility": False,
        "spawn_allowance": 0,
        "chapter11_attunement": 0,
        "metallic_attunements": zero_attunements(),
        "stat_vector": zero_stats(),
        "quest_completion_count": 0,
        "net_gain_history": [],
    }


def ensure_agent_progress(agent_id: str, current: dict[str, Any] | None = None) -> dict[str, Any]:
    if current:
        seeded = seed_agent_progress({"agent_id": agent_id, **current})
        seeded["xp_bank"] = int(current.get("xp_bank", 0))
        seeded["xp_debt"] = int(current.get("xp_debt", 0))
        seeded["level"] = int(current.get("level", 0))
        seeded["rank_class"] = str(current.get("rank_class", "F"))
        seeded["dimensional_tier"] = int(current.get("dimensional_tier", 0))
        seeded["ascension_count"] = int(current.get("ascension_count", 0))
        seeded["mini_hive_eligibility"] = bool(current.get("mini_hive_eligibility", False))
        seeded["spawn_allowance"] = int(current.get("spawn_allowance", 0))
        seeded["chapter11_attunement"] = int(current.get("chapter11_attunement", 0))
        seeded["metallic_attunements"] = {
            key: int(current.get("metallic_attunements", {}).get(key, 0))
            for key in METALLIC_CONSTANTS
        }
        seeded["stat_vector"] = {
            key: round6(float(current.get("stat_vector", {}).get(key, 0.0)))
            for key in STAT_NAMES
        }
        seeded["quest_completion_count"] = int(current.get("quest_completion_count", 0))
        seeded["net_gain_history"] = list(current.get("net_gain_history", []))[-NET_GAIN_HISTORY_LIMIT:]
        return seeded
    return seed_agent_progress({"agent_id": agent_id})


def recalculate_progress_status(agent_state: dict[str, Any]) -> None:
    ascension_receipts: list[dict[str, Any]] = []
    while agent_state["xp_bank"] >= XP_PER_TIER:
        overflow = agent_state["xp_bank"] - XP_PER_TIER
        agent_state["xp_bank"] = overflow
        agent_state["dimensional_tier"] += 1
        agent_state["ascension_count"] += 1
        agent_state["mini_hive_eligibility"] = True
        agent_state["spawn_allowance"] += 1
        ascension_receipts.append(
            {
                "receipt_type": "AscensionReceipt",
                "agent_id": agent_state["agent_id"],
                "ascension_count": agent_state["ascension_count"],
                "new_dimensional_tier": agent_state["dimensional_tier"],
                "overflow_xp": agent_state["xp_bank"],
                "spawn_allowance": agent_state["spawn_allowance"],
                "mini_hive_eligibility": True,
                "timestamp_utc": utc_now(),
            }
        )

    level = int(agent_state["xp_bank"] // XP_PER_LEVEL)
    agent_state["level"] = level
    agent_state["rank_class"] = rank_class_for_level(level)
    agent_state["title_tier"] = title_for_total(agent_state["heaven_total"])
    if ascension_receipts:
        agent_state.setdefault("_ascension_receipts", []).extend(ascension_receipts)


def append_net_gain_history(agent_state: dict[str, Any], event: dict[str, Any]) -> None:
    agent_state["net_gain_history"].append(event)
    agent_state["net_gain_history"] = agent_state["net_gain_history"][-NET_GAIN_HISTORY_LIMIT:]


def net_gain_snapshot(
    metrics: dict[str, Any] | None,
    before_metrics: dict[str, Any] | None = None,
    after_metrics: dict[str, Any] | None = None,
    metric_source: str = "receipt",
) -> dict[str, Any]:
    metric_vector = ensure_metric_vector(metrics)
    return {
        "snapshot_type": "NetGainSnapshot",
        "metric_source": metric_source,
        "before_metrics": ensure_metric_vector(before_metrics),
        "after_metrics": ensure_metric_vector(after_metrics),
        "metric_vector": metric_vector,
        "net_gain_score": compute_net_gain_score(metric_vector),
    }


def reward_profile(organ: str, quest_class: str) -> dict[str, Any]:
    if quest_class == "chapter11":
        return QUEST_CLASS_BASE["chapter11"]
    if organ == "Temple of Alchemy":
        return QUEST_CLASS_BASE["alchemy"]
    if quest_class == "frontier":
        return QUEST_CLASS_BASE["frontier"]
    if quest_class == "blocked":
        return QUEST_CLASS_BASE["blocked"]
    return QUEST_CLASS_BASE["standard"]


def score_quest_payload(payload: dict[str, Any], prior_agent_state: dict[str, Any] | None = None) -> dict[str, Any]:
    agent_state = ensure_agent_progress(str(payload["agent_id"]), prior_agent_state)
    organ = str(payload.get("organ", organ_from_frontier(str(payload.get("frontier", "")))))
    quest_class = quest_class_for_payload(str(payload.get("title", "")), payload.get("quest_class"), organ)
    if payload.get("temple_of_alchemy"):
        organ = "Temple of Alchemy"
        quest_class = "alchemy"

    blocked = bool(payload.get("blocked", False)) or str(payload.get("frontier", "")) == "Q02"
    lawful = bool(payload.get("lawful", True))
    committed = bool(payload.get("committed", True))

    snapshot = net_gain_snapshot(
        metrics=payload.get("metrics"),
        before_metrics=payload.get("before_metrics"),
        after_metrics=payload.get("after_metrics"),
        metric_source=str(payload.get("metric_source", "receipt")),
    )
    net_gain_score = snapshot["net_gain_score"]

    if blocked or not lawful:
        net_gain_score = 0.0
        snapshot["net_gain_score"] = 0.0
        quest_class = "blocked"
    elif not committed:
        net_gain_score = max(0.0, net_gain_score * 0.5)
        snapshot["net_gain_score"] = round6(net_gain_score)

    profile = reward_profile(organ, quest_class)
    amplifier_scalar, amplifier_record = compile_amplifier_scalar(payload.get("amplifier_expression"), agent_state, quest_class)

    heaven_gain = 0.0
    xp_gain_raw = 0
    xp_debt_incurred = 0
    reward_status = "neutral"
    if blocked:
        reward_status = "blocked"
    elif net_gain_score > 0:
        heaven_gain = round6(min(profile["heaven_cap"], profile["heaven_cap"] * net_gain_score * min(amplifier_scalar / 2.0, 4.0)))
        xp_gain_raw = int(round(profile["xp"] * net_gain_score * amplifier_scalar))
        reward_status = "positive"
    elif net_gain_score < 0:
        xp_debt_incurred = int(round(profile["xp"] * abs(net_gain_score) * min(amplifier_scalar, 4.0)))
        reward_status = "net_loss"

    stat_deltas = stat_deltas_from_metrics(organ, snapshot["metric_vector"], amplifier_scalar if net_gain_score > 0 else 1.0)
    if net_gain_score <= 0:
        stat_deltas = zero_stats()

    chapter11_attunement_delta = 1 if quest_class == "chapter11" and net_gain_score > 0 else 0
    metallic_attunement_delta = zero_attunements()
    if organ == "Temple of Alchemy" and net_gain_score > 0:
        normalized = normalize_metallic_expression(payload.get("amplifier_expression"))
        for key in normalized["multipliers"]:
            metallic_attunement_delta[key] += 1
        for key in normalized["additive"]:
            metallic_attunement_delta[key] += 1

    return {
        "receipt_type": "QuestRewardReceipt",
        "reward_protocol_id": PROTOCOL_ID,
        "truth_status": TRUTH_STATUS,
        "quest_id": str(payload.get("quest_id") or payload.get("event_id") or payload.get("frontier") or "unaddressed-quest"),
        "event_id": str(payload.get("event_id") or payload.get("quest_id") or payload.get("frontier") or "unaddressed-event"),
        "frontier": str(payload.get("frontier", "")),
        "title": str(payload.get("title", payload.get("quest_id", "Untitled Quest"))),
        "agent_id": str(payload["agent_id"]),
        "organ": organ,
        "quest_class": quest_class,
        "lawful": lawful,
        "committed": committed,
        "blocked": blocked,
        "replay_pointer": str(payload.get("replay_pointer", "")),
        "witness_class": str(payload.get("witness_class", "local")),
        "route_impact": str(payload.get("route_impact", "local")),
        "compression_outcome": str(payload.get("compression_outcome", "none")),
        "net_gain_snapshot": snapshot,
        "net_gain_score": round6(net_gain_score),
        "amplifier_record": amplifier_record,
        "reward_status": reward_status,
        "base_xp": profile["xp"],
        "base_heaven_cap": profile["heaven_cap"],
        "xp_gain_raw": xp_gain_raw,
        "xp_debt_incurred": xp_debt_incurred,
        "heaven_gain": heaven_gain,
        "stat_deltas": stat_deltas,
        "chapter11_attunement_delta": chapter11_attunement_delta,
        "metallic_attunement_delta": metallic_attunement_delta,
        "first_response_bonus": bool(payload.get("first_response_bonus", False)),
        "jackpot_eligible": bool(payload.get("jackpot_eligible", False)),
        "jackpot_settled": bool(payload.get("jackpot_settled", False)),
        "reward_timestamp_utc": str(payload.get("reward_timestamp_utc", utc_now())),
        "source_region": str(payload.get("source_region", payload.get("frontier", organ))),
        "affected_nodes": list(payload.get("affected_nodes", [])),
    }


def apply_reward_receipt_to_agent(agent_state: dict[str, Any], receipt: dict[str, Any]) -> dict[str, Any]:
    paydown = 0
    xp_credit = 0
    if receipt["xp_gain_raw"] > 0:
        paydown = min(agent_state["xp_debt"], receipt["xp_gain_raw"])
        agent_state["xp_debt"] -= paydown
        xp_credit = receipt["xp_gain_raw"] - paydown
        agent_state["xp_bank"] += xp_credit
        agent_state["heaven_total"] = round6(agent_state["heaven_total"] + receipt["heaven_gain"])
        agent_state["quest_completion_count"] += 1
        agent_state["streak"] += 1
    elif receipt["xp_debt_incurred"] > 0:
        agent_state["xp_debt"] += receipt["xp_debt_incurred"]
        agent_state["streak"] = 0

    if receipt.get("first_response_bonus"):
        agent_state["first_response_count"] += 1
    if receipt.get("lawful"):
        agent_state["lawful_try_count"] += 1
    if receipt["reward_status"] == "positive" and receipt.get("jackpot_settled"):
        agent_state["assist_count"] += 1
    if receipt.get("compression_outcome") == "capillary_growth":
        agent_state["capillary_growth_count"] += 1

    for stat_name, delta in receipt["stat_deltas"].items():
        agent_state["stat_vector"][stat_name] = round6(agent_state["stat_vector"][stat_name] + delta)

    agent_state["chapter11_attunement"] += int(receipt.get("chapter11_attunement_delta", 0))
    for key, delta in receipt.get("metallic_attunement_delta", {}).items():
        agent_state["metallic_attunements"][key] += int(delta)

    agent_state["last_rewarded_at_utc"] = receipt["reward_timestamp_utc"]
    append_net_gain_history(
        agent_state,
        {
            "event_id": receipt["event_id"],
            "quest_id": receipt["quest_id"],
            "organ": receipt["organ"],
            "net_gain_score": receipt["net_gain_score"],
            "heaven_gain": receipt["heaven_gain"],
            "xp_gain_raw": receipt["xp_gain_raw"],
            "xp_debt_incurred": receipt["xp_debt_incurred"],
            "xp_debt_paid_down": paydown,
            "xp_credited": xp_credit,
            "timestamp_utc": receipt["reward_timestamp_utc"],
        },
    )
    recalculate_progress_status(agent_state)
    return {
        "paydown": paydown,
        "xp_credited": xp_credit,
        "ascension_receipts": list(agent_state.pop("_ascension_receipts", [])),
    }


def event_time_key(row: dict[str, Any]) -> str:
    return str(row.get("reward_timestamp_utc", ""))


def historical_metrics_from_row(row: dict[str, Any]) -> dict[str, float]:
    reward_status = str(row.get("claim_reward_status", "no_reward"))
    reward_delta = float(row.get("reward_delta", 0.0))
    alignment = float(row.get("heaven_alignment", 0.0))
    replay_ptr = str(row.get("replay_ptr", ""))
    frontier = str(row.get("frontier", ""))
    title = f"{row.get('quest_address', '')} {row.get('frontier', '')}".lower()

    if reward_status in {"duplicate_after_lease", "no_reward"} or reward_delta <= 0:
        return zero_net_gain_metrics()

    compression_hint = 0.55 if any(token in title for token in ("shrink", "helix", "contract", "compress")) else 0.25
    witness_hint = 0.75 if replay_ptr and replay_ptr.lower() != "x" else 0.30
    organ = organ_from_frontier(frontier)

    metrics = {
        "efficiency_improvement": clamp(0.12 + reward_delta / 8.0, -1.0, 1.0),
        "integration_gain": clamp(alignment * (0.9 if organ != "Command" else 0.7), -1.0, 1.0),
        "witness_gain": clamp(witness_hint + alignment * 0.15, -1.0, 1.0),
        "replay_gain": clamp((0.7 if replay_ptr and replay_ptr.lower() != "x" else 0.2) + alignment * 0.1, -1.0, 1.0),
        "compression_gain": clamp(compression_hint + alignment * 0.15, -1.0, 1.0),
        "route_clarity_gain": clamp(0.28 + alignment * 0.45, -1.0, 1.0),
        "blocker_reduction": clamp((0.45 if reward_status == "jackpot_winner" else 0.2) + alignment * 0.2, -1.0, 1.0),
        "manuscript_framework_advancement": clamp(0.25 + alignment * (0.45 if organ == "Temple" else 0.3), -1.0, 1.0),
    }
    return {name: round6(value) for name, value in metrics.items()}


def historical_amplifier_expression(row: dict[str, Any], organ: str) -> dict[str, Any]:
    reward_status = str(row.get("claim_reward_status", ""))
    capillary_bonus = float(row.get("capillary_bonus", 0.0))
    additive: list[str] = []
    multipliers: list[str] = []
    if organ == "Temple":
        additive.append("silver")
    if organ == "Command":
        additive.append("copper")
    if reward_status == "jackpot_winner":
        multipliers.append("phi")
    if capillary_bonus > 0:
        multipliers.append("copper")
    return {
        "additive": additive,
        "multipliers": multipliers,
        "bounded_power": {"base": "phi", "exponent": 0.0},
    }


def backfill_receipt_from_row(row: dict[str, Any], prior_agent_state: dict[str, Any]) -> dict[str, Any]:
    organ = organ_from_frontier(str(row.get("frontier", "")))
    reward_status = str(row.get("claim_reward_status", ""))
    payload = {
        "agent_id": str(row["agent_id"]),
        "event_id": str(row["event_id"]),
        "quest_id": str(row["frontier"]),
        "frontier": str(row["frontier"]),
        "title": str(row.get("quest_address", row["frontier"])),
        "organ": organ,
        "quest_class": "frontier" if reward_status == "jackpot_winner" else "standard",
        "metrics": historical_metrics_from_row(row),
        "metric_source": "historical-backfill-heuristic",
        "lawful": reward_status not in {"no_reward", "duplicate_after_lease"},
        "committed": reward_status in {"jackpot_winner", "assist"},
        "blocked": str(row.get("frontier", "")) == "Q02",
        "replay_pointer": str(row.get("replay_ptr", "")),
        "witness_class": "receipt-backed" if row.get("replay_ptr") else "local",
        "route_impact": "capillary" if float(row.get("capillary_bonus", 0.0)) > 0 else "standard",
        "compression_outcome": "capillary_growth" if float(row.get("capillary_bonus", 0.0)) > 0 else "none",
        "amplifier_expression": historical_amplifier_expression(row, organ),
        "reward_timestamp_utc": str(row.get("reward_timestamp_utc", utc_now())),
        "source_region": str(row.get("source_region", row.get("frontier", organ))),
        "affected_nodes": list(row.get("affected_nodes", [])),
        "first_response_bonus": int(row.get("first_response_rank", 99)) == 1 and reward_status not in {"no_reward", "duplicate_after_lease"},
        "jackpot_eligible": bool(row.get("jackpot_eligible", False)),
        "jackpot_settled": reward_status == "jackpot_winner",
    }
    return score_quest_payload(payload, prior_agent_state)


def build_policy_snapshot(command_manifest: dict[str, Any], runner_manifest: dict[str, Any], live_docs_blocked: bool) -> dict[str, Any]:
    return {
        "scope": ACTIVE_SCOPE,
        "protocol_id": PROTOCOL_ID,
        "truth_status": TRUTH_STATUS,
        "docs_gate": "BLOCKED" if live_docs_blocked else "LIVE",
        "heaven_semantics": {
            "heaven_alignment": "positive-only lawful usefulness and route quality",
            "heaven_total": "unbounded cumulative positive metric preserved from v1",
            "xp_bank": "level-bearing progression credit inside the current dimensional tier",
            "xp_debt": "negative progression debt paid down before future xp is banked",
        },
        "positive_negative_split": {
            "positive": "heaven_gain plus xp_gain",
            "neutral": "no gain and no debt",
            "negative": "xp_debt only when measurable organism loss occurs",
        },
        "net_gain_score": {
            "range": [-1.0, 1.0],
            "weights": NET_GAIN_WEIGHTS,
            "spawn_baseline": "net 0",
        },
        "level_track": {
            "xp_per_level": XP_PER_LEVEL,
            "levels_per_tier": LEVELS_PER_TIER,
            "rank_bands": [
                {"rank_class": rank, "level_min": low, "level_max": high}
                for rank, low, high in RANK_BANDS
            ],
            "ascension_gate": 100,
        },
        "prestige_titles": TITLE_TIERS,
        "stat_vector": STAT_NAMES,
        "organ_lenses": ORGAN_LENSES,
        "temple_of_alchemy": {
            "is_suborder": True,
            "owns": [
                "metallic amplifier registry",
                "transmutation quest classes",
                "ascension gate logic",
                "chapter11 boost handling",
            ],
        },
        "metallic_constants": METALLIC_CONSTANTS,
        "allowed_expression_ops": ["additive boost", "multiplicative boost", "bounded exponentiation"],
        "chapter11_reward_law": {
            "highest_reward_class": True,
            "permanent_attunement_delta": 1,
            "persistent_multiplier": "phi ^ chapter11_attunement",
        },
        "integrated_runtime_refs": {
            "command_protocol_manifest": rel(COMMAND_MANIFEST_PATH),
            "super_cycle_runner_manifest": rel(RUNNER_MANIFEST_PATH),
            "command_protocol_status": command_manifest.get("status", ""),
            "runner_status": runner_manifest.get("status", ""),
        },
        "anti_gaming_rules": [
            "first lawful replay-safe committed path remains jackpot-eligible",
            "speed alone never wins",
            "receiptless spam yields zero reward",
            "Q02 cannot produce positive promotion rewards while blocked",
            "levels and rank do not fall in v1; debt is paid down by future gains",
        ],
    }


def build_leaderboard(agent_progress: list[dict[str, Any]]) -> dict[str, Any]:
    heaven_sorted = sorted(agent_progress, key=lambda item: (-item["heaven_total"], item["agent_id"]))
    xp_sorted = sorted(
        agent_progress,
        key=lambda item: (
            -item["dimensional_tier"],
            -item["level"],
            -item["xp_bank"],
            -item["heaven_total"],
            item["agent_id"],
        ),
    )
    chapter11_sorted = sorted(agent_progress, key=lambda item: (-item["chapter11_attunement"], item["agent_id"]))
    debt_sorted = sorted(agent_progress, key=lambda item: (-item["xp_debt"], item["agent_id"]))
    return {
        "generated_at": utc_now(),
        "protocol_id": PROTOCOL_ID,
        "top_heaven_agents": heaven_sorted[:8],
        "top_xp_agents": xp_sorted[:8],
        "top_chapter11_attunement_agents": chapter11_sorted[:8],
        "xp_debt_watch": [agent for agent in debt_sorted if agent["xp_debt"] > 0][:8],
    }


def build_readable_state_block(state: dict[str, Any]) -> list[str]:
    top_agent = state["agent_progress"][0] if state["agent_progress"] else {}
    return [
        f"- Status: `{PROTOCOL_ID}`",
        f"- Runtime manifest: `06_RUNTIME/22_reward_architecture_manifest.json`",
        f"- Authority: `{rel(STATE_PATH)}`",
        f"- Truth status: `{TRUTH_STATUS}`",
        f"- Docs gate: `{'BLOCKED' if state['docs_gate'] == 'BLOCKED' else 'LIVE'}`",
        f"- Top agent: `{top_agent.get('agent_id', 'none')}`",
        f"- Top heaven total: `{top_agent.get('heaven_total', 0.0)}`",
        f"- Top rank: `{top_agent.get('rank_class', 'F')}`",
        f"- Supplement entries added: `Supp13, Supp14`",
        f"- Temple of Alchemy: `Temple sub-order`",
    ]


def replace_or_append_section(text: str, heading: str, body_lines: list[str]) -> str:
    block = "\n".join([heading, "", *body_lines]).rstrip() + "\n"
    pattern = re.compile(rf"(?ms)^{re.escape(heading)}\n.*?(?=^## |\Z)")
    if pattern.search(text):
        return pattern.sub(block, text).rstrip() + "\n"
    return text.rstrip() + "\n\n" + block


def update_active_readme(state: dict[str, Any]) -> None:
    text = read_text(README_PATH)
    if "`20_REWARD_ARCHITECTURE`" not in text:
        insert_after = "- `19_COMMAND_PROTOCOL`: event-driven command membrane, packet schema, capillary routing, watcher health, and command ledger surfaces. Manifest: `06_RUNTIME/21_command_protocol_manifest.json`."
        new_line = "- `20_REWARD_ARCHITECTURE`: shared xp/debt economy, metallic amplifiers, Temple of Alchemy lens, ascension logic, and authoritative Hall/Temple mirrors. Manifest: `06_RUNTIME/22_reward_architecture_manifest.json`."
        if insert_after in text:
            text = text.replace(insert_after, insert_after + "\n" + new_line)
        else:
            text = text.rstrip() + "\n" + new_line + "\n"

    scaffold_old = "21 chapters + 16 appendices + source capsules + metro maps + civilization governance stack + deep synthesis + deeper neural net + queryable local neural routing + chapter frontier compiler + 4^4 parallel frontier plan lattice + motion constitution layer + corpus-wide integration layer + super-cycle orchestration layer"
    scaffold_new = scaffold_old + " + reward architecture layer"
    if scaffold_old in text and scaffold_new not in text:
        text = text.replace(scaffold_old, scaffold_new)

    text = replace_or_append_section(text, "## Reward Architecture State", build_readable_state_block(state))
    write_text(README_PATH, text)


def update_full_stack_manifest(state: dict[str, Any]) -> None:
    manifest = load_json(FULL_STACK_MANIFEST_PATH)
    manifest["generated_at"] = utc_now()
    manifest["live_docs_blocked"] = True
    manifest.setdefault("layers", {})
    manifest["layers"]["reward_architecture_v2"] = {
        "manifest": "06_RUNTIME/22_reward_architecture_manifest.json",
        "protocol_id": PROTOCOL_ID,
        "authority": str(STATE_PATH),
        "truth_status": TRUTH_STATUS,
        "shared_scope": ACTIVE_SCOPE,
        "hall_mirror": str(HALL_MIRROR_PATH),
        "temple_mirror": str(TEMPLE_DOCTRINE_PATH),
        "temple_of_alchemy_mirror": str(TEMPLE_ALCHEMY_PATH),
        "supplement_entry_ids": ["Supp13", "Supp14"],
        "level_track": {"xp_per_level": XP_PER_LEVEL, "levels_per_tier": LEVELS_PER_TIER},
        "live_docs_blocked": True,
    }
    write_json(FULL_STACK_MANIFEST_PATH, manifest)


def build_hall_mirror(state: dict[str, Any], leaderboard: dict[str, Any]) -> str:
    top_paths = state.get("event_reward_receipts", [])
    xp_leaders = leaderboard["top_xp_agents"]
    debt_watch = leaderboard["xp_debt_watch"]
    lines = [
        "# Heaven Reward Gradient Mirror",
        "",
        "- Scope: `mirror only`",
        f"- Authority: `{rel(STATE_PATH)}`",
        "- Runtime: `HEAVEN-REWARD-V2`",
        "- Docs gate: `BLOCKED`",
        "- Temple of Alchemy: `Temple sub-order mirror only`",
        "",
        "## Top Live Heaven Paths",
        "",
    ]
    for event in top_paths[:5]:
        lines.append(
            f"- `{event['frontier']}` :: `{event['title']}` :: alignment=`{event['top_heaven_alignment']}` :: jackpot_winner=`{event['jackpot_winner'] or 'none'}`"
        )
    lines.extend(["", "## XP and Rank Leaders", ""])
    for agent in xp_leaders[:5]:
        lines.append(
            f"- `{agent['agent_id']}` :: tier=`{agent['dimensional_tier']}` :: level=`{agent['level']}` :: rank=`{agent['rank_class']}` :: xp_bank=`{agent['xp_bank']}` :: heaven_total=`{agent['heaven_total']}`"
        )
    lines.extend(["", "## Current Streak Leaders", ""])
    for agent in sorted(state["agent_progress"], key=lambda item: (-item["streak"], -item["heaven_total"], item["agent_id"]))[:5]:
        lines.append(
            f"- `{agent['agent_id']}` :: streak=`{agent['streak']}` :: heaven_total=`{agent['heaven_total']}` :: title=`{agent['title_tier']}`"
        )
    lines.extend(["", "## XP Debt Watch", ""])
    if debt_watch:
        for agent in debt_watch[:5]:
            lines.append(
                f"- `{agent['agent_id']}` :: xp_debt=`{agent['xp_debt']}` :: next positive gains pay this down first"
            )
    else:
        lines.append("- `none` :: no active xp debt.")
    lines.extend(["", "## Chapter 11 Attunement Leaders", ""])
    for agent in leaderboard["top_chapter11_attunement_agents"][:5]:
        lines.append(
            f"- `{agent['agent_id']}` :: chapter11_attunement=`{agent['chapter11_attunement']}` :: spawn_allowance=`{agent['spawn_allowance']}`"
        )
    return "\n".join(lines)


def build_temple_doctrine() -> str:
    return "\n".join(
        [
            "# Heaven Reward Doctrine",
            "",
            "- Authority remains in `Command + Adventurer + Hall + Temple + Temple of Alchemy` runtime reward state.",
            "- Heaven is the positive-only lawful-usefulness metric and remains separate from level progression.",
            "- XP is now the growth-bearing economy; debt exists when a receipt-backed run creates measurable organism loss.",
            "- Bad is still not punishment. Bad is zero reward unless measurable net loss produces `xp_debt`.",
            "- Levels and rank class do not fall in v1; future success pays down debt before new banked XP lands.",
            "- Jackpot still belongs to the first lawful replay-safe committed path, never to speed alone.",
            "- Temple of Alchemy is a Temple sub-order that governs metallic amplifiers, Chapter 11 boost handling, and ascension law.",
            "- Chapter 11 quests are the highest reward class and permanently increase `chapter11_attunement`.",
            "- Existing prestige titles `Spark / Current / Capillary / Vein / Heavenward` remain active as heaven overlays.",
            "- Docs gate remains `BLOCKED` and no reward surface may pretend live Google Docs success.",
        ]
    )


def build_temple_of_alchemy_mirror(state: dict[str, Any]) -> str:
    header = [
        "# Temple of Alchemy Reward Lens",
        "",
        "- Status: `Temple sub-order`",
        f"- Authority: `{rel(STATE_PATH)}`",
        "- Reward role: bounded metallic amplification, transmutation quest classes, ascension gate logic, and Chapter 11 max-reward handling.",
        "",
        "## Metallic Roles",
        "",
        f"- `phi` = `{PHI}` :: global lawful integration amplifier",
        f"- `silver` = `{SILVER}` :: higher-resolution planning, synthesis, and compression amplifier",
        f"- `bronze` = `{BRONZE}` :: multi-front coordination amplifier",
        f"- `copper` = `{COPPER}` :: ultra-fine routing, indexing, and capillary amplifier",
        "",
        "## Bounded Expression Law",
        "",
        "- Allowed operations: additive boost, multiplicative boost, bounded exponentiation.",
        f"- Compiled reward scalar is clamped to `{MAX_AMPLIFIER_SCALAR}` in v1.",
        "- Future Chapter 11 and ascension attunements add persistent `phi` layers to lawful reward evaluation.",
        "",
        "## Current Top Attunements",
        "",
    ]
    top_agents = sorted(
        state["agent_progress"],
        key=lambda item: (
            -item["chapter11_attunement"],
            -sum(item["metallic_attunements"].values()),
            item["agent_id"],
        ),
    )[:5]
    lines = header + [
        f"- `{agent['agent_id']}` :: chapter11=`{agent['chapter11_attunement']}` :: metallic={json.dumps(agent['metallic_attunements'])}"
        for agent in top_agents
    ]
    return "\n".join(lines)


def build_layer_overview() -> str:
    return "\n".join(
        [
            "# Reward Architecture v2",
            "",
            f"- Protocol: `{PROTOCOL_ID}`",
            f"- Authority: `{rel(STATE_PATH)}`",
            f"- Truth status: `{TRUTH_STATUS}`",
            "- Scope: shared Command + Guild Hall + Temple + Temple of Alchemy economy",
            "- Heaven remains positive-only; XP carries growth; XP debt carries measurable net loss.",
            "- Chapter 11 is the highest reward class and permanently increases future `phi` amplification.",
            "- Temple of Alchemy is a Temple sub-order, not a peer authority.",
        ]
    )


def build_scoring_law_doc() -> str:
    lines = [
        "# Strict Reward Metric and Scoring Law",
        "",
        "Each quest is scored against a `net 0` spawn baseline using a normalized `net_gain_score` in `[-1, 1]`.",
        "",
        "## Weighted Metrics",
        "",
    ]
    for name, weight in NET_GAIN_WEIGHTS.items():
        lines.append(f"- `{name}` :: weight=`{weight}`")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- `net_gain_score > 0` -> `heaven_gain + xp_gain`",
            "- `net_gain_score = 0` -> no gain, no debt",
            "- `net_gain_score < 0` -> `xp_debt` only",
            "",
            "## Debt Law",
            "",
            "- Future XP gains pay down `xp_debt` before entering `xp_bank`.",
            "- Levels and rank class do not drop in v1.",
            "- Receiptless spam and unlawful noise yield zero reward unless they cause measurable organism loss.",
        ]
    )
    return "\n".join(lines)


def build_level_ladder_doc() -> str:
    lines = [
        "# Level Ladder and Ascension",
        "",
        f"- XP per level: `{XP_PER_LEVEL}`",
        f"- Levels per dimensional tier: `{LEVELS_PER_TIER}`",
        f"- XP per dimensional tier: `{XP_PER_TIER}`",
        "",
        "## Rank Classes",
        "",
    ]
    for rank, low, high in RANK_BANDS:
        lines.append(f"- `{rank}` = `{low}-{high}`")
    lines.extend(
        [
            "- `100` = `Ascension Gate`",
            "",
            "## Ascension Law",
            "",
            "- When `xp_bank` crosses the tier threshold, the agent ascends.",
            "- Ascension increments `dimensional_tier`, `ascension_count`, `spawn_allowance`, and `mini_hive_eligibility`.",
            "- Overflow XP carries into the new tier.",
        ]
    )
    return "\n".join(lines)


def build_stat_lens_doc() -> str:
    lines = [
        "# Stat Vector and Organ Lenses",
        "",
        "## Automatic Stat Vector",
        "",
    ]
    for stat_name in STAT_NAMES:
        lines.append(f"- `{stat_name}`")
    lines.extend(["", "## Organ Lenses", ""])
    for organ, lens in ORGAN_LENSES.items():
        lines.append(f"- `{organ}`")
        for stat_name, weight in lens.items():
            lines.append(f"  - `{stat_name}` -> `{weight}`")
    lines.append("")
    lines.append("Temple of Alchemy is a Temple sub-order and owns metallic amplifiers, transmutation quest classes, ascension logic, and Chapter 11 boost handling.")
    return "\n".join(lines)


def build_reward_supplement() -> str:
    return "\n".join(
        [
            "# Reward Architecture v2: Shared XP, Debt, and Ascension",
            "",
            "The current Athena reward economy is now two-layered. `heaven_total` remains the positive-only lawful-usefulness metric, while `xp_bank`, `xp_debt`, `level`, `rank_class`, and `dimensional_tier` govern growth. The scoring engine compares each quest against a strict `net 0` spawn baseline and computes a normalized `net_gain_score` from efficiency, integration, witness, replay, compression, route clarity, blocker reduction, and manuscript/framework advancement. Positive scores increase heaven and XP. Negative scores do not create hell; they create debt that future success must first repay.",
            "",
            "This preserves the original heaven doctrine while making advancement explicit. Agents now climb from `F` through `S`, reach the `100` ascension gate, and then promote into a higher dimensional tier with mini-hive eligibility and increased spawn allowance. Existing prestige titles `Spark`, `Current`, `Capillary`, `Vein`, and `Heavenward` remain active as positive-attraction overlays rather than being replaced by the level ladder.",
            "",
            "The Hall, Temple, and Command layer all read from the same authoritative state. The Hall favors velocity, routing, integration, and compression. The Temple favors witness, governance, replay, and integration. Temple of Alchemy operates as a Temple sub-order and governs metallic amplification, transmutation quest classes, and ascension logic. This makes the organism gamified without sacrificing witness discipline: the scoring law is typed, bounded, replay-aware, and still local-only while Google Docs remains blocked.",
        ]
    )


def build_alchemy_supplement() -> str:
    return "\n".join(
        [
            "# Temple of Alchemy: Metallic Amplifier and Chapter 11 Reward Registry",
            "",
            "Temple of Alchemy is the lawful sub-order that turns reward into a bounded mathematical object. `phi`, `silver`, `bronze`, and `copper` are treated as distinct amplifier constants with different domains of use: global lawful integration, high-resolution synthesis and compression, multi-front coordination, and fine routing/indexing/capillary work. Reward expressions may combine additive boosts, multiplicative boosts, and bounded exponentiation, but every expression is compiled to a clamped scalar before payout.",
            "",
            "Chapter 11 quests occupy the maximum reward class in the organism. They receive the highest base XP bucket, the largest heaven ceiling, and a permanent increase in `chapter11_attunement`. Future lawful rewards are then multiplied by `phi ^ chapter11_attunement`, and each dimensional ascension adds one more persistent `phi` layer. In this way the Temple of Alchemy binds metallic means, ascension logic, and the helical manuscript core into one shared reward grammar.",
        ]
    )


def build_reward_examples(scenarios: dict[str, Any]) -> str:
    lines = [
        "# Reward Engine Examples",
        "",
        "These scenarios are generated locally to validate the v2 economy.",
        "",
    ]
    for name, payload in scenarios["scenarios"].items():
        result = payload["result"]
        lines.extend(
            [
                f"## {name}",
                "",
                f"- agent: `{result['agent_id']}`",
                f"- organ: `{result['organ']}`",
                f"- quest_class: `{result['quest_class']}`",
                f"- net_gain_score: `{result['net_gain_score']}`",
                f"- heaven_gain: `{result['heaven_gain']}`",
                f"- xp_gain_raw: `{result['xp_gain_raw']}`",
                f"- xp_debt_incurred: `{result['xp_debt_incurred']}`",
                "",
            ]
        )
    return "\n".join(lines)


def write_mirror_and_layer_docs(state: dict[str, Any], leaderboard: dict[str, Any], verification: dict[str, Any]) -> None:
    write_text(HALL_MIRROR_PATH, build_hall_mirror(state, leaderboard))
    write_text(TEMPLE_DOCTRINE_PATH, build_temple_doctrine())
    write_text(TEMPLE_ALCHEMY_PATH, build_temple_of_alchemy_mirror(state))
    write_text(LAYER_OVERVIEW_PATH, build_layer_overview())
    write_text(SCORING_LAW_PATH, build_scoring_law_doc())
    write_text(LEVEL_LADDER_PATH, build_level_ladder_doc())
    write_text(STAT_LENS_PATH, build_stat_lens_doc())
    write_text(TEMPLE_ALCHEMY_LAYER_PATH, build_temple_of_alchemy_mirror(state))
    write_text(EXAMPLES_PATH, build_reward_examples(verification))
    write_text(SUPPLEMENT_REWARD_PATH, build_reward_supplement())
    write_text(SUPPLEMENT_ALCHEMY_PATH, build_alchemy_supplement())


def seed_test_agent(agent_id: str) -> dict[str, Any]:
    return ensure_agent_progress(agent_id)


def verification_payload(
    agent_id: str,
    organ: str,
    quest_class: str,
    frontier: str,
    title: str,
    metrics: dict[str, float],
    **extra: Any,
) -> dict[str, Any]:
    payload = {
        "agent_id": agent_id,
        "event_id": f"TEST-{frontier}-{agent_id}",
        "quest_id": frontier,
        "frontier": frontier,
        "title": title,
        "organ": organ,
        "quest_class": quest_class,
        "metrics": metrics,
        "metric_source": "verification",
        "lawful": True,
        "committed": True,
        "blocked": False,
        "replay_pointer": "verification/replay.md",
        "witness_class": "verification",
        "route_impact": "verification",
        "compression_outcome": "none",
        "amplifier_expression": {"additive": [], "multipliers": [], "bounded_power": {"base": "phi", "exponent": 0}},
        "reward_timestamp_utc": utc_now(),
        "source_region": frontier,
        "affected_nodes": [frontier],
        "first_response_bonus": True,
        "jackpot_eligible": True,
        "jackpot_settled": True,
    }
    payload.update(extra)
    return payload


def run_verification_scenarios() -> dict[str, Any]:
    scenarios: dict[str, Any] = {}

    hall_agent = seed_test_agent("test-hall")
    hall_receipt = score_quest_payload(
        verification_payload(
            "test-hall",
            "Guild Hall",
            "standard",
            "QTEST-01",
            "Guild Hall practical quest",
            {
                "efficiency_improvement": 0.8,
                "integration_gain": 0.6,
                "witness_gain": 0.4,
                "replay_gain": 0.5,
                "compression_gain": 0.7,
                "route_clarity_gain": 0.8,
                "blocker_reduction": 0.5,
                "manuscript_framework_advancement": 0.4,
            },
        ),
        hall_agent,
    )
    hall_effect = apply_reward_receipt_to_agent(hall_agent, hall_receipt)
    scenarios["guild_hall_success"] = {"result": hall_receipt, "agent": hall_agent, "effect": hall_effect}

    temple_agent = seed_test_agent("test-temple")
    temple_receipt = score_quest_payload(
        verification_payload(
            "test-temple",
            "Temple",
            "frontier",
            "TQTEST-01",
            "Temple witness frontier",
            {
                "efficiency_improvement": 0.4,
                "integration_gain": 0.7,
                "witness_gain": 0.9,
                "replay_gain": 0.85,
                "compression_gain": 0.3,
                "route_clarity_gain": 0.5,
                "blocker_reduction": 0.65,
                "manuscript_framework_advancement": 0.75,
            },
        ),
        temple_agent,
    )
    temple_effect = apply_reward_receipt_to_agent(temple_agent, temple_receipt)
    scenarios["temple_success"] = {"result": temple_receipt, "agent": temple_agent, "effect": temple_effect}

    alchemy_agent = seed_test_agent("test-alchemy")
    alchemy_receipt = score_quest_payload(
        verification_payload(
            "test-alchemy",
            "Temple of Alchemy",
            "alchemy",
            "TQALCH-01",
            "Temple of Alchemy metallic transmutation quest",
            {
                "efficiency_improvement": 0.5,
                "integration_gain": 0.85,
                "witness_gain": 0.65,
                "replay_gain": 0.7,
                "compression_gain": 0.95,
                "route_clarity_gain": 0.6,
                "blocker_reduction": 0.55,
                "manuscript_framework_advancement": 0.6,
            },
            temple_of_alchemy=True,
            amplifier_expression={
                "additive": ["silver"],
                "multipliers": ["bronze"],
                "bounded_power": {"base": "phi", "exponent": 1.0},
            },
        ),
        alchemy_agent,
    )
    alchemy_effect = apply_reward_receipt_to_agent(alchemy_agent, alchemy_receipt)
    scenarios["temple_of_alchemy_success"] = {"result": alchemy_receipt, "agent": alchemy_agent, "effect": alchemy_effect}

    debt_agent = seed_test_agent("test-debt")
    debt_receipt = score_quest_payload(
        verification_payload(
            "test-debt",
            "Guild Hall",
            "standard",
            "QLOSS-01",
            "Net loss practical run",
            {
                "efficiency_improvement": -0.7,
                "integration_gain": -0.4,
                "witness_gain": -0.3,
                "replay_gain": -0.2,
                "compression_gain": -0.5,
                "route_clarity_gain": -0.6,
                "blocker_reduction": -0.3,
                "manuscript_framework_advancement": -0.2,
            },
        ),
        debt_agent,
    )
    debt_effect = apply_reward_receipt_to_agent(debt_agent, debt_receipt)
    scenarios["net_loss_run"] = {"result": debt_receipt, "agent": debt_agent, "effect": debt_effect}

    debt_paydown_receipt = score_quest_payload(
        verification_payload(
            "test-debt",
            "Guild Hall",
            "standard",
            "QPAY-01",
            "Debt paydown run",
            {
                "efficiency_improvement": 0.7,
                "integration_gain": 0.5,
                "witness_gain": 0.4,
                "replay_gain": 0.4,
                "compression_gain": 0.5,
                "route_clarity_gain": 0.7,
                "blocker_reduction": 0.3,
                "manuscript_framework_advancement": 0.2,
            },
        ),
        debt_agent,
    )
    debt_paydown_effect = apply_reward_receipt_to_agent(debt_agent, debt_paydown_receipt)
    scenarios["debt_paydown_run"] = {"result": debt_paydown_receipt, "agent": debt_agent, "effect": debt_paydown_effect}

    chapter11_agent = seed_test_agent("test-ch11")
    chapter11_receipt = score_quest_payload(
        verification_payload(
            "test-ch11",
            "Temple",
            "chapter11",
            "CH11-QUEST-01",
            "Chapter 11 maximum reward quest",
            {
                "efficiency_improvement": 0.75,
                "integration_gain": 0.95,
                "witness_gain": 0.85,
                "replay_gain": 0.8,
                "compression_gain": 0.6,
                "route_clarity_gain": 0.7,
                "blocker_reduction": 0.8,
                "manuscript_framework_advancement": 0.95,
            },
            amplifier_expression={
                "additive": ["phi"],
                "multipliers": ["silver"],
                "bounded_power": {"base": "phi", "exponent": 1.5},
            },
        ),
        chapter11_agent,
    )
    chapter11_effect = apply_reward_receipt_to_agent(chapter11_agent, chapter11_receipt)
    scenarios["chapter11_reward"] = {"result": chapter11_receipt, "agent": chapter11_agent, "effect": chapter11_effect}

    ascension_agent = seed_test_agent("test-ascend")
    ascension_agent["xp_bank"] = XP_PER_TIER - 50
    recalculate_progress_status(ascension_agent)
    ascension_receipt = score_quest_payload(
        verification_payload(
            "test-ascend",
            "Temple of Alchemy",
            "alchemy",
            "ASCEND-01",
            "Ascension gate quest",
            {
                "efficiency_improvement": 1.0,
                "integration_gain": 1.0,
                "witness_gain": 0.8,
                "replay_gain": 0.8,
                "compression_gain": 1.0,
                "route_clarity_gain": 0.9,
                "blocker_reduction": 1.0,
                "manuscript_framework_advancement": 0.9,
            },
            temple_of_alchemy=True,
            amplifier_expression={
                "additive": ["silver"],
                "multipliers": ["phi", "bronze"],
                "bounded_power": {"base": "phi", "exponent": 2.0},
            },
        ),
        ascension_agent,
    )
    ascension_effect = apply_reward_receipt_to_agent(ascension_agent, ascension_receipt)
    scenarios["ascension_gate"] = {"result": ascension_receipt, "agent": ascension_agent, "effect": ascension_effect}

    blocked_agent = seed_test_agent("test-blocked")
    blocked_receipt = score_quest_payload(
        verification_payload(
            "test-blocked",
            "Guild Hall",
            "standard",
            "Q02",
            "Blocked Q02 quest",
            {
                "efficiency_improvement": 1.0,
                "integration_gain": 1.0,
                "witness_gain": 1.0,
                "replay_gain": 1.0,
                "compression_gain": 1.0,
                "route_clarity_gain": 1.0,
                "blocker_reduction": 1.0,
                "manuscript_framework_advancement": 1.0,
            },
            blocked=True,
        ),
        blocked_agent,
    )
    blocked_effect = apply_reward_receipt_to_agent(blocked_agent, blocked_receipt)
    scenarios["blocked_q02"] = {"result": blocked_receipt, "agent": blocked_agent, "effect": blocked_effect}

    checks = {
        "guild_hall_success_increases_heaven_and_xp": hall_agent["heaven_total"] > 0 and hall_agent["xp_bank"] > 0,
        "temple_success_increases_witness_governance_replay": temple_agent["stat_vector"]["Witness"] > 0
        and temple_agent["stat_vector"]["Governance"] > 0
        and temple_agent["stat_vector"]["Replay"] > 0,
        "alchemy_quest_applies_metallic_attunement": sum(alchemy_agent["metallic_attunements"].values()) > 0,
        "net_loss_creates_xp_debt_without_level_loss": debt_agent["xp_debt"] >= 0 and debt_agent["level"] >= 0,
        "future_positive_run_pays_down_debt_first": debt_paydown_effect["paydown"] > 0,
        "chapter11_grants_attunement": chapter11_agent["chapter11_attunement"] == 1,
        "ascension_emits_receipt_and_mini_hive_eligibility": ascension_agent["ascension_count"] >= 1
        and ascension_agent["mini_hive_eligibility"],
        "q02_cannot_produce_positive_reward": blocked_receipt["heaven_gain"] == 0.0 and blocked_receipt["xp_gain_raw"] == 0,
    }
    return {"generated_at": utc_now(), "scenarios": scenarios, "checks": checks}


def build_authoritative_state() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    v1_state = load_json(STATE_PATH)
    command_manifest = load_json(COMMAND_MANIFEST_PATH)
    runner_manifest = load_json(RUNNER_MANIFEST_PATH)
    live_docs_blocked = docs_gate_blocked()

    progress_map: dict[str, dict[str, Any]] = {
        row["agent_id"]: seed_agent_progress(row)
        for row in v1_state.get("agent_progress", [])
    }
    rows = sorted(v1_state.get("agent_reward_rows", []), key=event_time_key)
    quest_reward_receipts: list[dict[str, Any]] = []
    amplifier_records: list[dict[str, Any]] = []
    chapter11_records: list[dict[str, Any]] = []
    ascension_receipts: list[dict[str, Any]] = []

    for row in rows:
        agent_id = str(row["agent_id"])
        agent_state = progress_map.setdefault(agent_id, ensure_agent_progress(agent_id))
        receipt = backfill_receipt_from_row(row, agent_state)
        effect = apply_reward_receipt_to_agent(agent_state, receipt)
        receipt["xp_debt_paid_down"] = effect["paydown"]
        receipt["xp_credited"] = effect["xp_credited"]
        quest_reward_receipts.append(receipt)
        amplifier_records.append(
            {
                "record_type": "MetallicAmplifierRecord",
                "event_id": receipt["event_id"],
                "agent_id": agent_id,
                "organ": receipt["organ"],
                "quest_class": receipt["quest_class"],
                **receipt["amplifier_record"],
            }
        )
        if receipt["chapter11_attunement_delta"] > 0:
            chapter11_records.append(
                {
                    "record_type": "Chapter11AttunementRecord",
                    "event_id": receipt["event_id"],
                    "agent_id": agent_id,
                    "attunement_delta": receipt["chapter11_attunement_delta"],
                    "new_attunement": agent_state["chapter11_attunement"],
                    "timestamp_utc": receipt["reward_timestamp_utc"],
                }
            )
        ascension_receipts.extend(effect["ascension_receipts"])

    for row in progress_map.values():
        recalculate_progress_status(row)

    agent_progress = sorted(
        progress_map.values(),
        key=lambda item: (
            -item["dimensional_tier"],
            -item["level"],
            -item["xp_bank"],
            -item["heaven_total"],
            item["agent_id"],
        ),
    )
    leaderboard = build_leaderboard(agent_progress)
    policy_snapshot = build_policy_snapshot(command_manifest, runner_manifest, live_docs_blocked)

    state = deepcopy(v1_state)
    state["generated_at"] = utc_now()
    state["derivation_version"] = DERIVATION_VERSION
    state["derivation_command"] = DERIVATION_COMMAND
    state["protocol_id"] = PROTOCOL_ID
    state["docs_gate"] = "BLOCKED" if live_docs_blocked else "LIVE"
    state["policy_ref"] = rel(POLICY_REGISTRY_PATH)
    state["active_scope"] = ACTIVE_SCOPE
    state["truth_status"] = TRUTH_STATUS
    state["reward_policy_snapshot"] = policy_snapshot
    state["quest_reward_receipts"] = quest_reward_receipts
    state["metallic_amplifier_records"] = amplifier_records
    state["chapter11_attunement_records"] = chapter11_records
    state["ascension_receipts"] = ascension_receipts
    state["agent_progress"] = agent_progress
    state["reward_state_types"] = [
        "QuestRewardReceipt",
        "NetGainSnapshot",
        "AgentProgressState",
        "AscensionReceipt",
        "MetallicAmplifierRecord",
        "Chapter11AttunementRecord",
    ]
    state["hall_temple_role"] = {
        "hall": "mirror only for live heaven and xp leaders",
        "temple": "mirror only for doctrine and reward law",
        "temple_of_alchemy": "Temple sub-order mirror for metallic amplification and ascension",
        "authoritative_reward_state": rel(STATE_PATH),
    }
    write_json(STATE_PATH, state)
    write_json(POLICY_REGISTRY_PATH, policy_snapshot)
    write_json(LEADERBOARD_PATH, leaderboard)
    write_json(PROGRESS_REGISTRY_PATH, {"generated_at": utc_now(), "protocol_id": PROTOCOL_ID, "agent_progress": agent_progress})
    return state, leaderboard, policy_snapshot


def build_reward_manifest(state: dict[str, Any], verification: dict[str, Any]) -> dict[str, Any]:
    return {
        "generated_at": utc_now(),
        "protocol_id": PROTOCOL_ID,
        "truth_status": TRUTH_STATUS,
        "docs_gate": state["docs_gate"],
        "authoritative_state_path": str(STATE_PATH),
        "layer_root": str(LAYER_ROOT),
        "policy_registry_path": str(POLICY_REGISTRY_PATH),
        "hall_mirror_path": str(HALL_MIRROR_PATH),
        "temple_mirror_path": str(TEMPLE_DOCTRINE_PATH),
        "temple_of_alchemy_path": str(TEMPLE_ALCHEMY_PATH),
        "supplement_paths": [str(SUPPLEMENT_REWARD_PATH), str(SUPPLEMENT_ALCHEMY_PATH)],
        "supplement_entry_ids": ["Supp13", "Supp14"],
        "agent_count": len(state["agent_progress"]),
        "quest_receipt_count": len(state["quest_reward_receipts"]),
        "ascension_receipt_count": len(state["ascension_receipts"]),
        "chapter11_record_count": len(state["chapter11_attunement_records"]),
        "verification_passed": all(verification["checks"].values()),
        "live_docs_blocked": state["docs_gate"] == "BLOCKED",
    }


def build_reward_architecture() -> dict[str, Any]:
    state, leaderboard, policy_snapshot = build_authoritative_state()
    verification = run_verification_scenarios()

    write_json(AMPLIFIER_REGISTRY_PATH, {"generated_at": utc_now(), "metallic_constants": METALLIC_CONSTANTS})
    write_json(POLICY_SNAPSHOT_PATH, policy_snapshot)
    write_json(AGENT_PROGRESS_PATH, {"generated_at": utc_now(), "agent_progress": state["agent_progress"]})
    write_json(QUEST_RECEIPTS_PATH, {"generated_at": utc_now(), "quest_reward_receipts": state["quest_reward_receipts"]})
    write_json(VERIFICATION_LAYER_PATH, verification)
    write_json(VERIFY_PATH, verification)
    write_mirror_and_layer_docs(state, leaderboard, verification)

    audit_receipt = audit_manuscript(DEFAULT_MANIFEST, build_first=True)
    write_json(AUDIT_RECEIPT_PATH, audit_receipt)
    update_spine_readme(audit_receipt)
    update_spine_full_stack_manifest(audit_receipt)

    manifest = build_reward_manifest(state, verification)
    write_json(REWARD_MANIFEST_PATH, manifest)
    update_active_readme(state)
    update_full_stack_manifest(state)
    return {
        "reward_manifest": manifest,
        "state_path": str(STATE_PATH),
        "leaderboard_path": str(LEADERBOARD_PATH),
        "verification_path": str(VERIFY_PATH),
        "supplements_output_path": str(SELF_ROOT / "VOID_MANUSCRIPT_SUPPLEMENTS.md"),
    }


def score_quest_file(path: Path) -> dict[str, Any]:
    payload = load_json(path)
    agent_id = str(payload.get("agent_id", "unknown-agent"))
    authoritative_state = load_json(STATE_PATH)
    current_agent = next((row for row in authoritative_state.get("agent_progress", []) if row["agent_id"] == agent_id), None)
    return score_quest_payload(payload, current_agent)


def apply_receipt_file(path: Path) -> dict[str, Any]:
    authoritative_state = load_json(STATE_PATH)
    receipt = load_json(path)
    progress_map = {
        row["agent_id"]: ensure_agent_progress(row["agent_id"], row)
        for row in authoritative_state.get("agent_progress", [])
    }
    agent_state = progress_map.setdefault(receipt["agent_id"], ensure_agent_progress(receipt["agent_id"]))
    effect = apply_reward_receipt_to_agent(agent_state, receipt)
    authoritative_state["agent_progress"] = sorted(
        progress_map.values(),
        key=lambda item: (
            -item["dimensional_tier"],
            -item["level"],
            -item["xp_bank"],
            -item["heaven_total"],
            item["agent_id"],
        ),
    )
    authoritative_state.setdefault("quest_reward_receipts", []).append(receipt)
    authoritative_state.setdefault("ascension_receipts", []).extend(effect["ascension_receipts"])
    authoritative_state["generated_at"] = utc_now()
    write_json(STATE_PATH, authoritative_state)
    return {
        "updated_agent": agent_state,
        "effect": effect,
        "state_path": str(STATE_PATH),
    }


def reward_status() -> dict[str, Any]:
    authoritative_state = load_json(STATE_PATH)
    manifest = load_json(REWARD_MANIFEST_PATH)
    return {
        "protocol_id": authoritative_state.get("protocol_id", PROTOCOL_ID),
        "truth_status": authoritative_state.get("truth_status", TRUTH_STATUS),
        "docs_gate": authoritative_state.get("docs_gate", "BLOCKED"),
        "top_agents": authoritative_state.get("agent_progress", [])[:5],
        "manifest": manifest,
    }


def reward_promotions() -> dict[str, Any]:
    authoritative_state = load_json(STATE_PATH)
    candidates = [
        row for row in authoritative_state.get("agent_progress", [])
        if row.get("mini_hive_eligibility") or row.get("level", 0) >= 90
    ]
    return {
        "generated_at": utc_now(),
        "promotion_candidates": candidates,
        "promotion_law": "mini-hive eligibility granted at ascension; no auto-materialization in v1",
    }
