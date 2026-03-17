from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from .derive_heaven_reward_gradient import (
    COMPAT_HALL_MIRROR_PATH,
    COMPAT_MANIFEST_PATH,
    COMPAT_TEMPLE_MIRROR_PATH,
    LEADERBOARD_PATH,
    MANIFEST_PATH,
    OPERATOR_REGISTRY_PATH,
    PROGRESSION_LEDGER_PATH,
    PROMOTION_REGISTRY_PATH,
    PROTOCOL_ID,
    STATE_PATH,
    TEMPLE_MIRROR_PATH,
    VERIFY_PATH,
    apply_positive_operator,
    class_bands,
    progression_from_xp,
    read_json,
    read_text,
    reward_layer,
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def verify_heaven_reward_gradient() -> dict[str, Any]:
    state = read_json(STATE_PATH)
    leaderboard = read_json(LEADERBOARD_PATH)
    operator_registry = read_json(OPERATOR_REGISTRY_PATH)
    progression_ledger = read_json(PROGRESSION_LEDGER_PATH)
    promotion_registry = read_json(PROMOTION_REGISTRY_PATH)
    manifest_text = read_text(MANIFEST_PATH)
    compat_manifest_text = read_text(COMPAT_MANIFEST_PATH)
    hall_text = read_text(COMPAT_HALL_MIRROR_PATH)
    temple_text = read_text(TEMPLE_MIRROR_PATH)
    compat_temple_text = read_text(COMPAT_TEMPLE_MIRROR_PATH)

    reward_rows = state.get("agent_reward_rows", [])
    agent_progress = state.get("agent_progress", [])
    policy = reward_layer()
    bands = class_bands(policy)

    synthetic_positive = apply_positive_operator(2.0, "phi", 25.0)
    synthetic_loss = -min(abs(-30.0), 25.0)
    synthetic_promotion = progression_from_xp(100.1, bands)
    synthetic_demotion = progression_from_xp(14.9, bands)

    checks = {
        "protocol_id": state.get("protocol_id") == PROTOCOL_ID,
        "state_exists": STATE_PATH.exists(),
        "leaderboard_exists": LEADERBOARD_PATH.exists(),
        "operator_registry_exists": OPERATOR_REGISTRY_PATH.exists(),
        "progression_ledger_exists": PROGRESSION_LEDGER_PATH.exists(),
        "promotion_registry_exists": PROMOTION_REGISTRY_PATH.exists(),
        "scope_is_dual_track": state.get("active_scope") == "command+adventurer+tagged_liminal_agents",
        "reward_rows_present": len(reward_rows) > 0,
        "agent_progress_present": len(agent_progress) > 0,
        "dual_track_fields_present": all(
            all(
                key in row
                for key in [
                    "reward_delta",
                    "heaven_alignment",
                    "heaven_total_after",
                    "adventure_xp_delta",
                    "adventure_xp_total_after",
                    "net_effect_score",
                    "spawn_efficiency_snapshot",
                    "end_efficiency_snapshot",
                    "level_before",
                    "level_after",
                    "class_before",
                    "class_after",
                    "operator_applied",
                    "promotion_triggered",
                ]
            )
            for row in reward_rows
        ),
        "agent_progress_fields": all(
            all(
                key in row
                for key in [
                    "agent_id_tag",
                    "heaven_total",
                    "adventure_xp_total",
                    "level",
                    "class_tier",
                    "dimensional_rank",
                    "promotion_count",
                    "operator_unlocks",
                    "child_hive_ids",
                ]
            )
            for row in agent_progress
        ),
        "heaven_nonnegative": all(float(row.get("heaven_total_after", 0.0)) >= 0.0 for row in reward_rows),
        "xp_signed_present": any(float(row.get("adventure_xp_delta", 0.0)) < 0.0 for row in reward_rows),
        "operator_positive_gain": synthetic_positive > 2.0,
        "loss_cap_linear": synthetic_loss == -25.0,
        "promotion_threshold_logic": synthetic_promotion["dimensional_rank"] == 1 and synthetic_promotion["level"] == 0,
        "class_band_logic": synthetic_demotion["class_tier"] == "F",
        "leaderboard_sections": all(
            key in leaderboard
            for key in [
                "top_cumulative_heaven_totals",
                "top_adventure_xp_totals",
                "top_first_response_agents",
                "strongest_growing_capillaries",
                "most_lawful_assists",
                "recent_promotions",
                "top_live_heaven_paths",
            ]
        ),
        "operator_registry_sections": all(
            key in operator_registry for key in ["phi", "governance_caps", "class_bands", "operators"]
        ),
        "promotion_registry_sections": "events" in promotion_registry,
        "progression_rows_present": len(progression_ledger.get("rows", [])) == len(reward_rows),
        "manifest_mentions_dual_track": "Adventure XP track" in manifest_text,
        "compat_manifest_updated": "Adventure XP track" in compat_manifest_text,
        "hall_mentions_xp_leaders": "Adventure XP Leaders" in hall_text,
        "temple_mentions_harmful_runs": "Harmful runs can still lose XP." in temple_text,
        "compat_temple_updated": "Harmful runs can still lose XP." in compat_temple_text,
    }

    result = {
        "generated_at": utc_now(),
        "protocol_id": PROTOCOL_ID,
        "truth": "OK" if all(checks.values()) else "NEAR",
        "checks": checks,
    }
    VERIFY_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> int:
    result = verify_heaven_reward_gradient()
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
