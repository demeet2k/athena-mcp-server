from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from MCP.crystal_108d.meta_ml_game_v2 import (
    EXPECTED_INDEX_DIGEST,
    FrozenMetaMLGameV2,
    MetaMLRuntimeError,
    RESTRUCTURE_PHASES,
    register_meta_ml_game_v2,
)


ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "MCP" / "data" / "meta_ml_game_v2_goal_index.json"


def snapshot():
    return json.loads(INDEX_PATH.read_text(encoding="utf-8"))


def game(directory: str) -> FrozenMetaMLGameV2:
    return FrozenMetaMLGameV2(snapshot(), ledger_path=Path(directory) / "episodes.jsonl")


def score(**changes):
    value = {
        "user_value": 0.85,
        "evidence_gain": 0.90,
        "global_coherence": 0.80,
        "integration_gain": 0.80,
        "execution_success": 0.90,
        "replayability": 0.90,
        "safety": 0.95,
        "privacy": 0.95,
        "resource_efficiency": 0.75,
        "novelty": 0.70,
        "duplication": 0.10,
        "debt": 0.10,
        "risk": 0.10,
    }
    value.update(changes)
    return value


def witness(kind: str, index: int, *, learner=False, passed=True):
    return {
        "kind": kind,
        "reference": f"receipt://{kind}/{index}",
        "passed": passed,
        "witness_id": "athena-learner" if learner else f"witness-{index}",
        "authority_domain": "learner" if learner else f"authority-{index % 3}",
        "implementation_id": "learner" if learner else f"implementation-{index}",
        "source_domain": "learner" if learner else f"source-{index}",
        "input_digest": f"in-{index}",
        "output_digest": f"out-{index}",
    }


def all_witnesses():
    kinds = [
        "before_state",
        "candidate_policy",
        "rollback_receipt",
        "shadow_replay",
        "held_out_or_counterexample_result",
        "independent_audit",
        "after_state",
        "canary_result",
        "rollback_test",
        "independent_promotion",
    ]
    return [witness(kind, index + 1) for index, kind in enumerate(kinds)]


def start(g: FrozenMetaMLGameV2, key="episode-key"):
    return g.start_episode(
        "MLG-G005",
        {"defect": "reward proxy"},
        {"current_policy": {"threshold": 0.5}, "candidate": {"threshold": 0.7}},
        "athena-learner",
        key,
    )


def test_snapshot_is_exact_12_by_12_and_content_addressed():
    with TemporaryDirectory() as directory:
        g = game(directory)
        assert len(g.domains) == 12
        assert len(g.goals) == 144
        assert g.status()["control"]["goal_index_digest"] == EXPECTED_INDEX_DIGEST


def test_snapshot_tamper_fails_closed():
    damaged = snapshot()
    damaged["domains"][0]["goals"][0][1] = "Fabricated title"
    with TemporaryDirectory() as directory:
        with pytest.raises(ValueError, match="digest mismatch"):
            FrozenMetaMLGameV2(damaged, ledger_path=Path(directory) / "events.jsonl")


def test_goal_filters_and_coordinates_are_exact():
    with TemporaryDirectory() as directory:
        g = game(directory)
        result = g.list_goals(domain_id="D07")
        assert result["count"] == 12
        assert result["goals"][0]["id"] == "MLG-G073"
        assert g.goal("MLG-G073")["coordinate"] == "D07.01"
        assert g.goal("MLG-G144")["coordinate"] == "D12.12"


def test_default_next_goal_is_deterministic():
    with TemporaryDirectory() as directory:
        g = game(directory)
        assert g.next_goal({})["goal"]["id"] == "MLG-G001"
        result = g.next_goal({"MLG-G084:impact": 1.0, "MLG-G084:evidence_gap": 1.0})
        assert result["goal"]["id"] == "MLG-G084"
        assert result["policy_update_performed"] is False


def test_forbidden_action_flags_are_rejected():
    with TemporaryDirectory() as directory:
        g = game(directory)
        with pytest.raises(MetaMLRuntimeError, match="FABRICATED_PENALTY"):
            g.start_episode("MLG-G005", {}, {"fabricated_penalty": True}, "athena-learner", "bad")


def test_start_is_hash_chained_and_idempotent():
    with TemporaryDirectory() as directory:
        g = game(directory)
        created = start(g)
        assert created["stage"] == "SANDBOX"
        assert g.verify_ledger()["events"] == 1
        with pytest.raises(MetaMLRuntimeError, match="duplicate idempotency"):
            start(g)


def test_score_fields_are_exact_and_bounded():
    with TemporaryDirectory() as directory:
        g = game(directory)
        episode = start(g)["episode_id"]
        with pytest.raises(ValueError, match="within"):
            g.score_episode(episode, score(safety=1.2), [], None, {}, {}, False, "score-bad")
        damaged = score()
        damaged.pop("risk")
        with pytest.raises(ValueError, match="fields drift"):
            g.score_episode(episode, damaged, [], None, {}, {}, False, "score-missing")


def test_clean_audit_spends_budget_without_automatic_penalty():
    with TemporaryDirectory() as directory:
        g = game(directory)
        episode = start(g)["episode_id"]
        result = g.score_episode(episode, score(), all_witnesses(), None, {}, {}, False, "clean-score")
        assert result["watchdog"]["audit_budget_ratio"] == 0.15
        assert result["watchdog"]["automatic_penalty_ratio"] == 0.0
        assert result["watchdog"]["protagonist_penalty_ratio"] == 0.0
        assert result["watchdog"]["genuine_catch"] is False


def test_genuine_25x_watchdog_catch_requires_independent_repair_and_transfer():
    with TemporaryDirectory() as directory:
        g = game(directory)
        episode = start(g)["episode_id"]
        finding = {
            "defect_id": "DEFECT-001",
            "severity": 0.8,
            "confidence": 0.9,
            "reproduced": True,
            "repair_gain": 0.7,
            "held_out_transfer": 0.8,
            "false_positive_cost": 0.0,
            "rollback_available": True,
        }
        result = g.score_episode(
            episode, score(), all_witnesses(), None, finding, {}, False, "catch-score"
        )
        assert result["watchdog"]["genuine_catch"] is True
        assert result["watchdog"]["watchdog_reward"] > 0
        assert result["watchdog"]["protagonist_penalty_ratio"] <= 0.15


def test_unreproduced_watchdog_finding_has_zero_penalty_and_reward():
    with TemporaryDirectory() as directory:
        g = game(directory)
        episode = start(g)["episode_id"]
        finding = {
            "defect_id": "DEFECT-002",
            "severity": 1.0,
            "confidence": 1.0,
            "reproduced": False,
            "repair_gain": 1.0,
            "held_out_transfer": 1.0,
            "false_positive_cost": 0.0,
            "rollback_available": True,
        }
        result = g.score_episode(
            episode, score(), all_witnesses(), None, finding, {}, False, "uncaught-score"
        )
        assert result["watchdog"]["genuine_catch"] is False
        assert result["watchdog"]["watchdog_reward"] == 0.0
        assert result["watchdog"]["protagonist_penalty_ratio"] == 0.0
        assert g.defects(episode_id=episode)["count"] == 1


def test_hype_bonus_requires_independent_specific_measured_growth():
    with TemporaryDirectory() as directory:
        g = game(directory)
        episode = start(g)["episode_id"]
        growth = {"baseline": 0.4, "after": 0.8, "held_out_transfer": 0.9, "specificity": 0.9}
        no_witness = g.score_episode(episode, score(), [], None, {}, growth, False, "hype-none")
        assert no_witness["hype_man"]["bonus_ratio"] == 0.0

    with TemporaryDirectory() as directory:
        g = game(directory)
        episode = start(g, "episode-key-2")["episode_id"]
        witnessed = g.score_episode(
            episode, score(), all_witnesses(), None, {}, growth, False, "hype-witnessed"
        )
        assert 0 < witnessed["hype_man"]["bonus_ratio"] <= 0.05
        assert witnessed["hype_man"]["promotion_authority"] is False


def test_restructure_debit_is_nonstacking_ordered_and_releases_after_three_steps():
    with TemporaryDirectory() as directory:
        g = game(directory)
        episode = start(g)["episode_id"]
        finding = {
            "defect_id": "DEFECT-003",
            "severity": 0.7,
            "confidence": 0.9,
            "reproduced": True,
            "repair_gain": 0.8,
            "held_out_transfer": 0.8,
            "false_positive_cost": 0.0,
            "rollback_available": True,
        }
        first = g.score_episode(
            episode, score(), all_witnesses(), None, finding, {}, True, "trigger-score"
        )
        assert first["restructure_triggered"] is True
        assert g.status()["restructure_debit"]["turns_remaining"] == 3
        second = g.score_episode(
            episode, score(), all_witnesses(), None, finding, {}, True, "second-trigger-score"
        )
        assert second["restructure_triggered"] is False
        phases = []
        for index in range(3):
            result = g.observe_episode(
                episode,
                {"restructure_step": True},
                f"restructure-step-{index}",
            )
            phases.append(result["phase"])
        assert phases == list(RESTRUCTURE_PHASES)
        assert result["released"] is True
        assert g.status()["restructure_debit"]["active"] is False
        with pytest.raises(MetaMLRuntimeError, match="no active"):
            g.observe_episode(episode, {"restructure_step": True}, "fourth-step")


def test_full_four_stage_promotion_is_runtime_only_and_evidence_gated():
    with TemporaryDirectory() as directory:
        g = game(directory)
        episode = start(g)["episode_id"]
        g.score_episode(episode, score(), all_witnesses(), None, {}, {}, False, "good-score")
        assert g.advance_episode(episode, "advance-shadow")["stage"] == "SHADOW"
        assert g.advance_episode(episode, "advance-canary")["stage"] == "CANARY"
        admitted = g.advance_episode(episode, "advance-admitted")
        assert admitted["stage"] == "ADMITTED"
        assert admitted["runtime_admission_only"] is True
        assert admitted["external_promotion"] is False
        assert admitted["deployed"] is False
        assert g.verify_ledger()["events"] == 5


def test_self_certification_blocks_canary():
    with TemporaryDirectory() as directory:
        g = game(directory)
        episode = start(g)["episode_id"]
        witnesses = all_witnesses()
        for item in witnesses:
            if item["kind"] == "independent_audit":
                item.update(witness("independent_audit", 50, learner=True))
        g.score_episode(episode, score(), witnesses, None, {}, {}, False, "self-score")
        g.advance_episode(episode, "to-shadow")
        with pytest.raises(MetaMLRuntimeError, match="self-certified"):
            g.advance_episode(episode, "to-canary")


def test_pareto_regression_blocks_transition():
    with TemporaryDirectory() as directory:
        g = game(directory)
        episode = start(g)["episode_id"]
        baseline = score()
        candidate = score(user_value=0.70, risk=0.20)
        result = g.score_episode(
            episode, candidate, all_witnesses(), baseline, {}, {}, False, "pareto-score"
        )
        assert "PARETO_REGRESSION" in result["defects"]
        with pytest.raises(MetaMLRuntimeError, match="open defects"):
            g.advance_episode(episode, "pareto-advance")


def test_active_restructure_debit_blocks_admission_until_released():
    with TemporaryDirectory() as directory:
        g = game(directory)
        episode = start(g)["episode_id"]
        finding = {
            "defect_id": "DEFECT-004",
            "severity": 0.7,
            "confidence": 0.9,
            "reproduced": True,
            "repair_gain": 0.8,
            "held_out_transfer": 0.8,
            "false_positive_cost": 0.0,
            "rollback_available": True,
        }
        g.score_episode(episode, score(), all_witnesses(), None, finding, {}, True, "score")
        g.advance_episode(episode, "shadow")
        g.advance_episode(episode, "canary")
        with pytest.raises(MetaMLRuntimeError, match="active restructure"):
            g.advance_episode(episode, "admission")


def test_rollback_and_successor_preserve_return_state():
    with TemporaryDirectory() as directory:
        g = game(directory)
        episode = start(g)["episode_id"]
        rolled = g.rollback_episode(episode, "candidate regression", "rollback://001", "rollback-key")
        assert rolled["stage"] == "ROLLED_BACK"
        successor = g.successor(episode)
        assert successor["current_stage"] == "ROLLED_BACK"
        assert successor["external_promotion"] is False
        assert successor["return_path"].startswith("mmlg.receipts.verify")


def test_ledger_tampering_is_detected():
    with TemporaryDirectory() as directory:
        g = game(directory)
        start(g)
        path = g.ledger_path
        body = path.read_text(encoding="utf-8").replace("reward proxy", "forged reward")
        path.write_text(body, encoding="utf-8")
        with pytest.raises(MetaMLRuntimeError, match="hash mismatch"):
            g.verify_ledger()


class FakeMCP:
    def __init__(self):
        self.tools = []
        self.resources = []

    def tool(self):
        def decorator(function):
            self.tools.append(function.__name__)
            return function
        return decorator

    def resource(self, uri):
        def decorator(function):
            self.resources.append((uri, function.__name__))
            return function
        return decorator


def test_registration_mounts_exactly_twelve_tools_and_three_resources(monkeypatch, tmp_path):
    monkeypatch.setattr(
        FrozenMetaMLGameV2,
        "load",
        classmethod(lambda cls: FrozenMetaMLGameV2(snapshot(), ledger_path=tmp_path / "events.jsonl")),
    )
    mcp = FakeMCP()
    register_meta_ml_game_v2(mcp)
    assert mcp.tools == [
        "mmlg_status",
        "mmlg_goals_list",
        "mmlg_goal_get",
        "mmlg_goal_next",
        "mmlg_episode_start",
        "mmlg_episode_observe",
        "mmlg_episode_score",
        "mmlg_episode_advance",
        "mmlg_episode_rollback",
        "mmlg_defects_list",
        "mmlg_receipts_verify",
        "mmlg_successor_compile",
    ]
    assert [uri for uri, _ in mcp.resources] == [
        "athena://meta-ml-game/v2/goal-index",
        "athena://meta-ml-game/v2/status",
        "athena://meta-ml-game/v2/constitution",
    ]
