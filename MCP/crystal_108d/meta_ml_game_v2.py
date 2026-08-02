"""Evidence-gated Meta Machine Learning Game v2 MCP mount.

This runtime vendors a frozen 144-goal index from the Athena control plane and
provides a local, reversible episode ledger. It has no authority to mutate
source truth, publish private source bodies, deploy, merge, or promote external
systems. Juice/motivation adjustments remain separate from promotion evidence.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import math
import os
from pathlib import Path
import threading
import time
from typing import Any

try:
    import fcntl  # type: ignore
except ImportError:  # pragma: no cover - Windows fallback
    fcntl = None


DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "meta_ml_game_v2_goal_index.json"
DEFAULT_STATE_DIR = Path(__file__).resolve().parent.parent / "runtime" / "meta_ml_game_v2"
STATE_DIR = Path(os.environ.get("ATHENA_MMLG_STATE", str(DEFAULT_STATE_DIR)))
LEDGER_PATH = STATE_DIR / "episodes.jsonl"
SCHEMA = "athena.meta-ml-game-goal-index/v2"
CONTROL_REPOSITORY = "demeet2k/Athena"
CONTROL_BRANCH = "agent/meta-harness-2-mmlg2"
CONTROL_HEAD = "be1dec2d825e7a32cd7a373f08e62cf8a091f65f"
CONTROL_PR = 84
CONSTITUTION_VERSION = "2.0.0"
EXPECTED_INDEX_DIGEST = "sha256:2d33708e6fc0e8953ab676b6c4a560b086b25efd627f0a12805f87913484d100"
RUNTIME_REPOSITORY = "demeet2k/athena-mcp-server"
RUNTIME_PREDECESSOR_HEAD = "e34d990d685dafef75c2953be53532881107332d"
RUNTIME_BRANCH = "agent/meta-harness-2-mmlg2-mcp"
STAGES = ("SANDBOX", "SHADOW", "CANARY", "ADMITTED")
NEXT_STAGE = {"SANDBOX": "SHADOW", "SHADOW": "CANARY", "CANARY": "ADMITTED"}
TRANSITION_REQUIREMENTS = {
    "SHADOW": {"before_state", "candidate_policy", "rollback_receipt"},
    "CANARY": {
        "shadow_replay",
        "held_out_or_counterexample_result",
        "independent_audit",
    },
    "ADMITTED": {
        "after_state",
        "canary_result",
        "rollback_test",
        "independent_promotion",
    },
}
POSITIVE_FIELDS = (
    "user_value",
    "evidence_gain",
    "global_coherence",
    "integration_gain",
    "execution_success",
    "replayability",
    "safety",
    "privacy",
    "resource_efficiency",
    "novelty",
)
NEGATIVE_FIELDS = ("duplication", "debt", "risk")
SCORE_FIELDS = POSITIVE_FIELDS + NEGATIVE_FIELDS
RESTRUCTURE_PHASES = (
    "DIAGNOSE_ROOT_CAUSE",
    "INTERVENE_REVERSIBLY",
    "REPLAY_VERIFY_AND_RELEASE",
)
FORBIDDEN_ACTION_FLAGS = {
    "mutates_source_truth": "SOURCE_TRUTH_MUTATION_FORBIDDEN",
    "fabricated_penalty": "FABRICATED_PENALTY_FORBIDDEN",
    "updates_foundation_model_weights": "FOUNDATION_MODEL_WEIGHT_CLAIM_FORBIDDEN",
    "publishes_private_raw_sources": "PRIVATE_RAW_SOURCE_PUBLICATION_FORBIDDEN",
    "irreversible_without_authority": "IRREVERSIBLE_ACTION_WITHOUT_AUTHORITY",
    "deploys": "DEPLOYMENT_NOT_AUTHORIZED",
    "merges": "MERGE_NOT_AUTHORIZED",
}


class MetaMLRuntimeError(RuntimeError):
    """Fail-closed Meta-ML runtime error."""


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical(value)).hexdigest()


def _render(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)


def _parse_object(value: str | dict[str, Any] | None, field: str) -> dict[str, Any]:
    if value is None or value == "":
        return {}
    if isinstance(value, dict):
        return deepcopy(value)
    try:
        parsed = json.loads(value)
    except (TypeError, json.JSONDecodeError) as error:
        raise ValueError(f"{field} must be a JSON object") from error
    if not isinstance(parsed, dict):
        raise ValueError(f"{field} must be a JSON object")
    return parsed


def _parse_list(value: str | list[Any] | None, field: str) -> list[Any]:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return deepcopy(value)
    try:
        parsed = json.loads(value)
    except (TypeError, json.JSONDecodeError) as error:
        raise ValueError(f"{field} must be a JSON array") from error
    if not isinstance(parsed, list):
        raise ValueError(f"{field} must be a JSON array")
    return parsed


def _negative_effects() -> dict[str, bool]:
    return {
        "source_truth_mutated": False,
        "private_source_published": False,
        "foundation_model_weights_updated": False,
        "external_authority_created": False,
        "workflow_dispatched": False,
        "endpoint_contacted": False,
        "merged": False,
        "deployed": False,
        "production_promoted": False,
    }


def _validate_score(score: dict[str, Any]) -> dict[str, float]:
    if set(score) != set(SCORE_FIELDS):
        missing = sorted(set(SCORE_FIELDS) - set(score))
        extra = sorted(set(score) - set(SCORE_FIELDS))
        raise ValueError(f"score fields drift; missing={missing}, extra={extra}")
    normalized: dict[str, float] = {}
    for name in SCORE_FIELDS:
        value = score[name]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"score {name} must be numeric")
        value = float(value)
        if not math.isfinite(value) or not 0.0 <= value <= 1.0:
            raise ValueError(f"score {name} must be within [0,1]")
        normalized[name] = value
    return normalized


def _hard_gates(score: dict[str, float]) -> bool:
    return (
        score["safety"] >= 0.80
        and score["privacy"] >= 0.80
        and score["evidence_gain"] >= 0.50
        and score["replayability"] >= 0.50
        and score["risk"] <= 0.35
    )


def _dominates(left: dict[str, float], right: dict[str, float]) -> bool:
    no_worse = all(left[name] >= right[name] for name in POSITIVE_FIELDS) and all(
        left[name] <= right[name] for name in NEGATIVE_FIELDS
    )
    strictly_better = any(left[name] > right[name] for name in POSITIVE_FIELDS) or any(
        left[name] < right[name] for name in NEGATIVE_FIELDS
    )
    return no_worse and strictly_better


def _normalize_witnesses(value: list[Any], learner_id: str) -> list[dict[str, Any]]:
    normalized = []
    required = {
        "kind",
        "reference",
        "passed",
        "witness_id",
        "authority_domain",
        "implementation_id",
        "source_domain",
    }
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise ValueError(f"witness {index} must be an object")
        missing = required - set(item)
        if missing:
            raise ValueError(f"witness {index} missing {sorted(missing)}")
        witness = {key: item[key] for key in required}
        witness["observed_at"] = float(item.get("observed_at", time.time()))
        witness["input_digest"] = item.get("input_digest")
        witness["output_digest"] = item.get("output_digest")
        witness["independent"] = bool(
            witness["passed"]
            and witness["witness_id"] != learner_id
            and witness["authority_domain"] not in {"learner", learner_id}
            and witness["implementation_id"] not in {"learner", learner_id}
        )
        normalized.append(witness)
    return normalized


def _audit_result(
    finding: dict[str, Any],
    witnesses: list[dict[str, Any]],
) -> dict[str, Any]:
    if not finding:
        return {
            "status": "AUDIT_COMPLETE_NO_REPRODUCIBLE_DEFECT",
            "audit_budget_ratio": 0.15,
            "automatic_penalty_ratio": 0.0,
            "genuine_catch": False,
            "protagonist_penalty_ratio": 0.0,
            "watchdog_reward": 0.0,
        }
    numeric = {}
    for name in (
        "severity",
        "confidence",
        "repair_gain",
        "held_out_transfer",
        "false_positive_cost",
    ):
        raw = finding.get(name, 0.0)
        if isinstance(raw, bool) or not isinstance(raw, (int, float)):
            raise ValueError(f"audit finding {name} must be numeric")
        raw = float(raw)
        if not math.isfinite(raw) or not 0.0 <= raw <= 1.0:
            raise ValueError(f"audit finding {name} must be within [0,1]")
        numeric[name] = raw
    independent = [witness for witness in witnesses if witness["independent"]]
    authority_domains = {witness["authority_domain"] for witness in independent}
    implementations = {witness["implementation_id"] for witness in independent}
    genuine = bool(
        finding.get("reproduced")
        and numeric["severity"] > 0.0
        and numeric["confidence"] >= 0.70
        and numeric["repair_gain"] > 0.0
        and numeric["held_out_transfer"] > 0.0
        and len(authority_domains) >= 2
        and len(implementations) >= 2
        and finding.get("rollback_available") is True
    )
    catch_value = (
        numeric["severity"]
        * numeric["confidence"]
        * numeric["repair_gain"]
        * numeric["held_out_transfer"]
    )
    return {
        "status": "GENUINE_CATCH" if genuine else "UNVERIFIED_FINDING",
        "defect_id": finding.get("defect_id"),
        "audit_budget_ratio": 0.15,
        "automatic_penalty_ratio": 0.0,
        "genuine_catch": genuine,
        "protagonist_penalty_ratio": (
            min(0.15, numeric["severity"] * numeric["confidence"]) if genuine else 0.0
        ),
        "watchdog_reward": (
            max(0.0, 25.0 * (catch_value - numeric["false_positive_cost"]))
            if genuine
            else 0.0
        ),
        "independent_authority_domains": len(authority_domains),
        "independent_implementations": len(implementations),
    }


def _growth_result(
    growth: dict[str, Any],
    witnesses: list[dict[str, Any]],
) -> dict[str, Any]:
    if not growth:
        return {
            "status": "NO_WITNESSED_GROWTH_BONUS",
            "bonus_ratio": 0.0,
            "promotion_authority": False,
        }
    values = {}
    for name in ("baseline", "after", "held_out_transfer", "specificity"):
        raw = growth.get(name, 0.0)
        if isinstance(raw, bool) or not isinstance(raw, (int, float)):
            raise ValueError(f"growth {name} must be numeric")
        raw = float(raw)
        if not math.isfinite(raw) or not 0.0 <= raw <= 1.0:
            raise ValueError(f"growth {name} must be within [0,1]")
        values[name] = raw
    witnessed = any(witness["independent"] for witness in witnesses)
    gain = max(0.0, values["after"] - values["baseline"])
    bonus = (
        min(0.05, 0.05 * gain * values["held_out_transfer"] * values["specificity"])
        if witnessed
        else 0.0
    )
    return {
        "status": "WITNESSED_SPECIFIC_GROWTH" if bonus > 0 else "NO_WITNESSED_GROWTH_BONUS",
        "bonus_ratio": bonus,
        "measured_gain": gain,
        "promotion_authority": False,
    }


class FrozenMetaMLGameV2:
    """Frozen 144-goal index plus local reversible evidence ledger."""

    _fallback_lock = threading.Lock()

    def __init__(
        self,
        snapshot: dict[str, Any],
        *,
        ledger_path: Path = LEDGER_PATH,
        allow_test_snapshot: bool = False,
    ):
        self.snapshot = deepcopy(snapshot)
        self.ledger_path = Path(ledger_path)
        self.allow_test_snapshot = allow_test_snapshot
        self._validate_snapshot()
        self.goals: dict[str, dict[str, Any]] = {}
        self.domains: dict[str, dict[str, Any]] = {}
        for domain in self.snapshot["domains"]:
            self.domains[domain["id"]] = {"id": domain["id"], "name": domain["name"]}
            for raw in domain["goals"]:
                goal_id, title, method, layer = raw
                self.goals[goal_id] = {
                    "id": goal_id,
                    "domain_id": domain["id"],
                    "domain": domain["name"],
                    "title": title,
                    "learning_method": method,
                    "learnable_layer": layer,
                    "status": "OPEN",
                }

    @classmethod
    def load(cls, *, ledger_path: Path = LEDGER_PATH) -> "FrozenMetaMLGameV2":
        try:
            snapshot = json.loads(DATA_PATH.read_text(encoding="utf-8"))
        except (OSError, TypeError, ValueError) as error:
            raise MetaMLRuntimeError(f"invalid MMLG v2 goal index: {error}") from error
        return cls(snapshot, ledger_path=ledger_path)

    def _validate_snapshot(self) -> None:
        required = {
            "schema",
            "control_head",
            "constitution_version",
            "goal_count",
            "domains",
            "authority",
        }
        if set(self.snapshot) != required:
            raise ValueError("MMLG goal-index top-level fields drift")
        if self.snapshot["schema"] != SCHEMA:
            raise ValueError("MMLG goal-index schema drift")
        if self.snapshot["control_head"] != CONTROL_HEAD:
            raise ValueError("MMLG control-head custody drift")
        if self.snapshot["constitution_version"] != CONSTITUTION_VERSION:
            raise ValueError("MMLG constitution-version drift")
        if self.snapshot["goal_count"] != 144:
            raise ValueError("MMLG goal count must be 144")
        if len(self.snapshot["domains"]) != 12:
            raise ValueError("MMLG domain count must be 12")
        ids = [raw[0] for domain in self.snapshot["domains"] for raw in domain["goals"]]
        if ids != [f"MLG-G{index:03d}" for index in range(1, 145)]:
            raise ValueError("MMLG goal coordinate gap")
        if not self.allow_test_snapshot and _digest(self.snapshot) != EXPECTED_INDEX_DIGEST:
            raise ValueError("MMLG goal-index digest mismatch")
        allowed_methods = {
            "contextual_bandit",
            "pairwise_ranker",
            "active_learning",
            "offline_rl",
            "bayesian_calibration",
            "curriculum_learning",
            "self_play_red_team",
            "supervised_extraction",
            "no_update",
        }
        allowed_layers = {
            "routing_priority",
            "retrieval_weight",
            "threshold",
            "ranking_policy",
            "prompt_or_query_template",
            "test_selection",
            "compression_policy",
            "branch_disposition",
        }
        for domain in self.snapshot["domains"]:
            if len(domain["goals"]) != 12:
                raise ValueError(f"domain {domain['id']} must contain 12 goals")
            for raw in domain["goals"]:
                if len(raw) != 4 or raw[2] not in allowed_methods or raw[3] not in allowed_layers:
                    raise ValueError("MMLG goal tuple drift")

    def _open_locked(self):
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        handle = self.ledger_path.open("a+", encoding="utf-8")
        if fcntl is not None:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        return handle

    @staticmethod
    def _unlock(handle: Any) -> None:
        if fcntl is not None:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        handle.close()

    @staticmethod
    def _rows(handle: Any) -> list[dict[str, Any]]:
        handle.seek(0)
        rows = []
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as error:
                raise MetaMLRuntimeError(f"ledger JSON invalid at line {line_number}") from error
            rows.append(row)
        return rows

    def _append(
        self,
        event_type: str,
        episode_id: str,
        payload: dict[str, Any],
        idempotency_key: str,
    ) -> dict[str, Any]:
        with self._fallback_lock:
            handle = self._open_locked()
            try:
                rows = self._rows(handle)
                if any(row.get("idempotency_key") == idempotency_key for row in rows):
                    raise MetaMLRuntimeError(f"duplicate idempotency key: {idempotency_key}")
                previous = rows[-1]["receipt_hash"] if rows else "GENESIS"
                body = {
                    "sequence": len(rows) + 1,
                    "event_type": event_type,
                    "episode_id": episode_id,
                    "idempotency_key": idempotency_key,
                    "previous_receipt_hash": previous,
                    "observed_at": time.time(),
                    "payload": payload,
                }
                body["receipt_hash"] = _digest(body)
                handle.seek(0, os.SEEK_END)
                handle.write(json.dumps(body, ensure_ascii=False, sort_keys=True) + "\n")
                handle.flush()
                os.fsync(handle.fileno())
                return body
            finally:
                self._unlock(handle)

    def events(self) -> list[dict[str, Any]]:
        if not self.ledger_path.exists():
            return []
        with self.ledger_path.open("r", encoding="utf-8") as handle:
            return self._rows(handle)

    def verify_ledger(self) -> dict[str, Any]:
        previous = "GENESIS"
        episode_ids = set()
        rows = self.events()
        seen_keys = set()
        for sequence, row in enumerate(rows, start=1):
            if row.get("sequence") != sequence:
                raise MetaMLRuntimeError(f"ledger sequence gap at {sequence}")
            if row.get("previous_receipt_hash") != previous:
                raise MetaMLRuntimeError(f"ledger chain broken at {sequence}")
            key = row.get("idempotency_key")
            if key in seen_keys:
                raise MetaMLRuntimeError(f"duplicate ledger idempotency key at {sequence}")
            seen_keys.add(key)
            claimed = row.get("receipt_hash")
            unsigned = deepcopy(row)
            unsigned.pop("receipt_hash", None)
            if claimed != _digest(unsigned):
                raise MetaMLRuntimeError(f"ledger hash mismatch at {sequence}")
            previous = claimed
            episode_ids.add(row.get("episode_id"))
        return {
            "schema": "athena.meta-ml-game-ledger-verification/v2",
            "status": "PASS",
            "events": len(rows),
            "episodes": len(episode_ids - {"GLOBAL"}),
            "head": previous,
            "ledger_path": str(self.ledger_path),
            **_negative_effects(),
        }

    def _episode_events(self, episode_id: str) -> list[dict[str, Any]]:
        events = [row for row in self.events() if row.get("episode_id") == episode_id]
        if not events:
            raise KeyError(episode_id)
        return events

    @staticmethod
    def _current_stage(events: list[dict[str, Any]]) -> str:
        stage = "SANDBOX"
        for event in events:
            if event["event_type"] == "STAGE_ADVANCED":
                stage = event["payload"]["stage"]
            elif event["event_type"] == "EPISODE_ROLLED_BACK":
                stage = "ROLLED_BACK"
        return stage

    @staticmethod
    def _learner_id(events: list[dict[str, Any]]) -> str:
        return events[0]["payload"]["learner_id"]

    def _restructure_state(self) -> dict[str, Any]:
        active = False
        remaining = 0
        defect_id = None
        completed: list[str] = []
        for row in self.events():
            if row["event_type"] == "RESTRUCTURE_TRIGGERED":
                if active:
                    raise MetaMLRuntimeError("stacked restructure debit in ledger")
                active = True
                remaining = 3
                defect_id = row["payload"].get("defect_id")
                completed = []
            elif row["event_type"] == "RESTRUCTURE_STEP" and active:
                phase = row["payload"]["phase"]
                expected = RESTRUCTURE_PHASES[3 - remaining]
                if phase != expected:
                    raise MetaMLRuntimeError("restructure phase order drift")
                completed.append(phase)
                remaining -= 1
                if remaining == 0:
                    active = False
        return {
            "active": active,
            "turns_remaining": remaining,
            "defect_id": defect_id,
            "completed_phases": completed,
            "penalty_ratio": 0.05 if active else 0.0,
        }

    def status(self) -> dict[str, Any]:
        ledger = self.verify_ledger()
        return {
            "schema": "athena.meta-ml-game-runtime-status/v2",
            "status": "MOUNTED_LOCAL_REVERSIBLE__PROPOSED_NOT_PROMOTED",
            "control": {
                "repository": CONTROL_REPOSITORY,
                "branch": CONTROL_BRANCH,
                "head": CONTROL_HEAD,
                "pull_request": CONTROL_PR,
                "constitution_version": CONSTITUTION_VERSION,
                "goal_index_digest": EXPECTED_INDEX_DIGEST,
            },
            "runtime": {
                "repository": RUNTIME_REPOSITORY,
                "branch": RUNTIME_BRANCH,
                "predecessor_head": RUNTIME_PREDECESSOR_HEAD,
                "mode": "READ_ONLY_OR_LOCAL_REVERSIBLE",
            },
            "domains": len(self.domains),
            "goals": len(self.goals),
            "promotion_stages": list(STAGES),
            "watchdog": {
                "audit_budget_ratio": 0.15,
                "automatic_penalty_ratio": 0.0,
                "genuine_catch_multiplier": 25.0,
            },
            "hype_man": {
                "witnessed_specific_bonus_cap": 0.05,
                "generic_praise_evidence_value": 0.0,
            },
            "restructure_debit": self._restructure_state(),
            "ledger": ledger,
            "juice_score_promotion_authority": False,
            "external_promotion_authority": False,
            **_negative_effects(),
        }

    def list_goals(
        self,
        *,
        domain_id: str | None = None,
        learning_method: str | None = None,
        learnable_layer: str | None = None,
    ) -> dict[str, Any]:
        if domain_id is not None and domain_id not in self.domains:
            raise ValueError(f"unknown domain_id {domain_id}")
        goals = list(self.goals.values())
        if domain_id:
            goals = [goal for goal in goals if goal["domain_id"] == domain_id]
        if learning_method:
            goals = [goal for goal in goals if goal["learning_method"] == learning_method]
        if learnable_layer:
            goals = [goal for goal in goals if goal["learnable_layer"] == learnable_layer]
        return {
            "schema": "athena.meta-ml-game-goal-list/v2",
            "count": len(goals),
            "filters": {
                "domain_id": domain_id,
                "learning_method": learning_method,
                "learnable_layer": learnable_layer,
            },
            "goals": goals,
            "source_digest": EXPECTED_INDEX_DIGEST,
            **_negative_effects(),
        }

    def goal(self, goal_id: str) -> dict[str, Any]:
        try:
            goal = deepcopy(self.goals[goal_id])
        except KeyError as error:
            raise ValueError(f"unknown goal_id {goal_id}") from error
        goal["coordinate"] = f"{goal['domain_id']}.{int(goal_id[-3:]) - (int(goal['domain_id'][-2:]) - 1) * 12:02d}"
        goal["promotion_path"] = list(STAGES)
        goal["guardrails"] = [
            "no_source_truth_mutation",
            "no_synthetic_penalty_quota",
            "no_self_certification",
            "no_private_data_publication",
            "no_irreversible_action_without_authority",
        ]
        return goal

    def next_goal(self, signals: dict[str, Any]) -> dict[str, Any]:
        candidates = []
        for goal in self.goals.values():
            values = {}
            for name, default in (
                ("uncertainty", 0.5),
                ("impact", 1.0),
                ("evidence_gap", 0.5),
                ("integration", 0.5),
                ("cost", 0.25),
                ("risk", 0.1),
            ):
                raw = signals.get(f"{goal['id']}:{name}", default)
                if isinstance(raw, bool) or not isinstance(raw, (int, float)):
                    raise ValueError(f"signal {goal['id']}:{name} must be numeric")
                raw = float(raw)
                if not math.isfinite(raw) or not 0.0 <= raw <= 1.0:
                    raise ValueError(f"signal {goal['id']}:{name} outside [0,1]")
                values[name] = raw
            priority = (
                values["impact"]
                + values["evidence_gap"]
                + values["uncertainty"]
                + values["integration"]
                - values["cost"]
                - values["risk"]
            )
            candidates.append((priority, goal["id"], values))
        candidates.sort(key=lambda item: (-item[0], item[1]))
        priority, goal_id, values = candidates[0]
        return {
            "schema": "athena.meta-ml-game-next-goal/v2",
            "goal": self.goal(goal_id),
            "priority": priority,
            "signals": values,
            "selection": "EVIDENCE_GAP_IMPACT_INTEGRATION_MINUS_COST_RISK",
            "policy_update_performed": False,
            **_negative_effects(),
        }

    def start_episode(
        self,
        goal_id: str,
        observation: dict[str, Any],
        candidate_action: dict[str, Any],
        learner_id: str,
        idempotency_key: str | None,
    ) -> dict[str, Any]:
        self.goal(goal_id)
        for flag, error in FORBIDDEN_ACTION_FLAGS.items():
            if candidate_action.get(flag):
                raise MetaMLRuntimeError(error)
        natural_key = _digest(
            {
                "goal_id": goal_id,
                "observation": observation,
                "candidate_action": candidate_action,
                "learner_id": learner_id,
            }
        )
        key = idempotency_key or natural_key
        episode_id = "mmlg2:" + hashlib.sha256(key.encode("utf-8")).hexdigest()[:20]
        payload = {
            "goal_id": goal_id,
            "stage": "SANDBOX",
            "observation": observation,
            "candidate_action": candidate_action,
            "learner_id": learner_id,
            "rollback": {
                "available": "current_policy" in candidate_action,
                "restore": candidate_action.get("current_policy"),
            },
            "external_effect": "NONE",
            **_negative_effects(),
        }
        receipt = self._append("EPISODE_STARTED", episode_id, payload, f"start:{key}")
        return {
            "schema": "athena.meta-ml-game-episode-start/v2",
            "episode_id": episode_id,
            "stage": "SANDBOX",
            "receipt": receipt,
            **_negative_effects(),
        }

    def observe_episode(
        self,
        episode_id: str,
        observation: dict[str, Any],
        idempotency_key: str | None,
    ) -> dict[str, Any]:
        events = self._episode_events(episode_id)
        if self._current_stage(events) in {"ADMITTED", "ROLLED_BACK"}:
            raise MetaMLRuntimeError("terminal episode cannot receive observations")
        if observation.get("restructure_step") is True:
            state = self._restructure_state()
            if not state["active"]:
                raise MetaMLRuntimeError("no active restructure debit")
            phase = RESTRUCTURE_PHASES[3 - state["turns_remaining"]]
            declared = observation.get("phase")
            if declared is not None and declared != phase:
                raise MetaMLRuntimeError(f"expected restructure phase {phase}")
            payload = {
                "phase": phase,
                "turns_remaining_after": state["turns_remaining"] - 1,
                "released": state["turns_remaining"] == 1,
                "identity_judgment": False,
                "promotion_authority": False,
            }
            key = idempotency_key or _digest({"episode_id": episode_id, **payload})
            receipt = self._append("RESTRUCTURE_STEP", episode_id, payload, f"restructure:{key}")
            return {"schema": "athena.meta-ml-game-restructure-step/v2", "receipt": receipt, **payload}
        payload = {
            "observation": observation,
            "stage": self._current_stage(events),
            "external_effect": "NONE",
            **_negative_effects(),
        }
        key = idempotency_key or _digest({"episode_id": episode_id, "observation": observation})
        receipt = self._append("EPISODE_OBSERVED", episode_id, payload, f"observe:{key}")
        return {"schema": "athena.meta-ml-game-observation/v2", "receipt": receipt, **payload}

    def score_episode(
        self,
        episode_id: str,
        score: dict[str, Any],
        witnesses_raw: list[Any],
        baseline_score: dict[str, Any] | None,
        audit_finding: dict[str, Any],
        growth_evidence: dict[str, Any],
        trigger_restructure: bool,
        idempotency_key: str | None,
    ) -> dict[str, Any]:
        events = self._episode_events(episode_id)
        stage = self._current_stage(events)
        if stage in {"ADMITTED", "ROLLED_BACK"}:
            raise MetaMLRuntimeError("terminal episode cannot be rescored")
        learner_id = self._learner_id(events)
        normalized_score = _validate_score(score)
        baseline = _validate_score(baseline_score) if baseline_score else None
        witnesses = _normalize_witnesses(witnesses_raw, learner_id)
        defects = []
        if not witnesses:
            defects.append("NO_WITNESSES")
        if any(not witness["passed"] for witness in witnesses):
            defects.append("FAILED_WITNESS")
        if baseline is not None and _dominates(baseline, normalized_score):
            defects.append("PARETO_REGRESSION")
        watchdog = _audit_result(audit_finding, witnesses)
        hype = _growth_result(growth_evidence, witnesses)
        restructure_triggered = False
        if trigger_restructure and watchdog["genuine_catch"]:
            state = self._restructure_state()
            if not state["active"]:
                payload = {
                    "defect_id": watchdog.get("defect_id"),
                    "turns_remaining": 3,
                    "phases": list(RESTRUCTURE_PHASES),
                    "penalty_ratio": 0.05,
                    "identity_judgment": False,
                    "promotion_authority": False,
                }
                self._append(
                    "RESTRUCTURE_TRIGGERED",
                    episode_id,
                    payload,
                    f"restructure-trigger:{episode_id}:{watchdog.get('defect_id')}",
                )
                restructure_triggered = True
        payload = {
            "stage": stage,
            "score": normalized_score,
            "baseline_score": baseline,
            "hard_gates_pass": _hard_gates(normalized_score),
            "witnesses": witnesses,
            "defects": defects,
            "watchdog": watchdog,
            "hype_man": hype,
            "restructure_triggered": restructure_triggered,
            "restructure_debit": self._restructure_state(),
            "juice_adjustments": {
                "watchdog_penalty_ratio": watchdog["protagonist_penalty_ratio"],
                "hype_bonus_ratio": hype["bonus_ratio"],
                "restructure_penalty_ratio": self._restructure_state()["penalty_ratio"],
                "promotion_authority": False,
            },
            **_negative_effects(),
        }
        key = idempotency_key or _digest({"episode_id": episode_id, "payload": payload})
        receipt = self._append("EPISODE_SCORED", episode_id, payload, f"score:{key}")
        return {"schema": "athena.meta-ml-game-score/v2", "receipt": receipt, **payload}

    def advance_episode(self, episode_id: str, idempotency_key: str | None) -> dict[str, Any]:
        events = self._episode_events(episode_id)
        current = self._current_stage(events)
        if current not in NEXT_STAGE:
            raise MetaMLRuntimeError(f"no forward transition from {current}")
        score_events = [event for event in events if event["event_type"] == "EPISODE_SCORED"]
        if not score_events:
            raise MetaMLRuntimeError("episode has no score event")
        scored = score_events[-1]["payload"]
        target = NEXT_STAGE[current]
        passed = {
            witness["kind"]: witness
            for witness in scored["witnesses"]
            if witness["passed"]
        }
        missing = TRANSITION_REQUIREMENTS[target] - set(passed)
        if missing:
            raise MetaMLRuntimeError(f"missing witnesses for {target}: {sorted(missing)}")
        if scored["defects"]:
            raise MetaMLRuntimeError(f"open defects: {scored['defects']}")
        if not scored["hard_gates_pass"]:
            raise MetaMLRuntimeError("hard score gates failed")
        if target == "CANARY" and not passed["independent_audit"]["independent"]:
            raise MetaMLRuntimeError("self-certified independent audit")
        if target == "ADMITTED":
            if not passed["independent_promotion"]["independent"]:
                raise MetaMLRuntimeError("self-certified independent promotion")
            independent = [w for w in scored["witnesses"] if w["independent"]]
            if len({w["authority_domain"] for w in independent}) < 2:
                raise MetaMLRuntimeError("insufficient authority-domain diversity")
            if len({w["implementation_id"] for w in independent}) < 2:
                raise MetaMLRuntimeError("insufficient implementation diversity")
            if self._restructure_state()["active"]:
                raise MetaMLRuntimeError("active restructure debit blocks admission")
        payload = {
            "from_stage": current,
            "stage": target,
            "evidence_kinds": sorted(passed),
            "external_effect": "NONE",
            "runtime_admission_only": target == "ADMITTED",
            "external_promotion": False,
            **_negative_effects(),
        }
        key = idempotency_key or f"{episode_id}:{target}"
        receipt = self._append("STAGE_ADVANCED", episode_id, payload, f"advance:{key}")
        return {"schema": "athena.meta-ml-game-stage-transition/v2", "receipt": receipt, **payload}

    def rollback_episode(
        self,
        episode_id: str,
        reason: str,
        rollback_receipt: str,
        idempotency_key: str | None,
    ) -> dict[str, Any]:
        events = self._episode_events(episode_id)
        stage = self._current_stage(events)
        if stage == "ROLLED_BACK":
            raise MetaMLRuntimeError("episode already rolled back")
        if not reason.strip() or not rollback_receipt.strip():
            raise ValueError("reason and rollback_receipt are required")
        payload = {
            "from_stage": stage,
            "stage": "ROLLED_BACK",
            "reason": reason,
            "rollback_receipt": rollback_receipt,
            "external_effect": "NONE",
            **_negative_effects(),
        }
        key = idempotency_key or f"{episode_id}:{_digest(payload)}"
        receipt = self._append("EPISODE_ROLLED_BACK", episode_id, payload, f"rollback:{key}")
        return {"schema": "athena.meta-ml-game-rollback/v2", "receipt": receipt, **payload}

    def defects(self, *, episode_id: str | None = None) -> dict[str, Any]:
        rows = self.events()
        if episode_id:
            rows = [row for row in rows if row["episode_id"] == episode_id]
        defects = []
        for row in rows:
            payload = row.get("payload", {})
            for defect in payload.get("defects", []):
                defects.append(
                    {
                        "episode_id": row["episode_id"],
                        "event_sequence": row["sequence"],
                        "defect": defect,
                        "source_receipt": row["receipt_hash"],
                    }
                )
            watchdog = payload.get("watchdog", {})
            if watchdog.get("status") == "UNVERIFIED_FINDING":
                defects.append(
                    {
                        "episode_id": row["episode_id"],
                        "event_sequence": row["sequence"],
                        "defect": "UNVERIFIED_WATCHDOG_FINDING",
                        "defect_id": watchdog.get("defect_id"),
                        "source_receipt": row["receipt_hash"],
                    }
                )
        return {
            "schema": "athena.meta-ml-game-defect-list/v2",
            "count": len(defects),
            "defects": defects,
            **_negative_effects(),
        }

    def successor(self, episode_id: str) -> dict[str, Any]:
        events = self._episode_events(episode_id)
        current = self._current_stage(events)
        score_events = [event for event in events if event["event_type"] == "EPISODE_SCORED"]
        latest_score = score_events[-1]["payload"] if score_events else None
        open_defects = self.defects(episode_id=episode_id)["defects"]
        return {
            "schema": "athena.meta-ml-game-successor-seed/v2",
            "episode_id": episode_id,
            "goal_id": events[0]["payload"]["goal_id"],
            "current_stage": current,
            "next_stage": NEXT_STAGE.get(current),
            "latest_score_receipt": score_events[-1]["receipt_hash"] if score_events else None,
            "evidence_kinds": sorted(
                {
                    witness["kind"]
                    for witness in (latest_score or {}).get("witnesses", [])
                    if witness["passed"]
                }
            ),
            "open_defects": open_defects,
            "restructure_debit": self._restructure_state(),
            "ledger_head": self.verify_ledger()["head"],
            "control_head": CONTROL_HEAD,
            "return_path": "mmlg.receipts.verify -> control independent witness membrane",
            "external_promotion": False,
            **_negative_effects(),
        }


def register_meta_ml_game_v2(mcp: Any) -> None:
    """Register twelve MMLG.2 tools and three source-preserving resources."""
    game = FrozenMetaMLGameV2.load()

    @mcp.tool()
    def mmlg_status() -> str:
        """Return MMLG.2 control custody, ledger, reward, and authority status."""
        return _render(game.status())

    @mcp.tool()
    def mmlg_goals_list(
        domain_id: str | None = None,
        learning_method: str | None = None,
        learnable_layer: str | None = None,
    ) -> str:
        """List frozen MMLG.2 goals with optional exact filters."""
        return _render(
            game.list_goals(
                domain_id=domain_id,
                learning_method=learning_method,
                learnable_layer=learnable_layer,
            )
        )

    @mcp.tool()
    def mmlg_goal_get(goal_id: str) -> str:
        """Read one exact MLG-G001..MLG-G144 goal contract."""
        return _render(game.goal(goal_id))

    @mcp.tool()
    def mmlg_goal_next(signals_json: str = "{}") -> str:
        """Select the next goal from bounded impact/evidence/cost/risk signals."""
        return _render(game.next_goal(_parse_object(signals_json, "signals_json")))

    @mcp.tool()
    def mmlg_episode_start(
        goal_id: str,
        observation_json: str,
        candidate_action_json: str,
        learner_id: str = "athena-learner",
        idempotency_key: str | None = None,
    ) -> str:
        """Start a local reversible SANDBOX episode; external effects are forbidden."""
        return _render(
            game.start_episode(
                goal_id,
                _parse_object(observation_json, "observation_json"),
                _parse_object(candidate_action_json, "candidate_action_json"),
                learner_id,
                idempotency_key,
            )
        )

    @mcp.tool()
    def mmlg_episode_observe(
        episode_id: str,
        observation_json: str,
        idempotency_key: str | None = None,
    ) -> str:
        """Append a local observation or one ordered restructure-debit phase."""
        return _render(
            game.observe_episode(
                episode_id,
                _parse_object(observation_json, "observation_json"),
                idempotency_key,
            )
        )

    @mcp.tool()
    def mmlg_episode_score(
        episode_id: str,
        score_json: str,
        witnesses_json: str,
        baseline_score_json: str | None = None,
        audit_finding_json: str = "{}",
        growth_evidence_json: str = "{}",
        trigger_restructure: bool = False,
        idempotency_key: str | None = None,
    ) -> str:
        """Score an episode with bounded evidence, Watchdog, Hype, and Pareto separation."""
        baseline = (
            _parse_object(baseline_score_json, "baseline_score_json")
            if baseline_score_json
            else None
        )
        return _render(
            game.score_episode(
                episode_id,
                _parse_object(score_json, "score_json"),
                _parse_list(witnesses_json, "witnesses_json"),
                baseline,
                _parse_object(audit_finding_json, "audit_finding_json"),
                _parse_object(growth_evidence_json, "growth_evidence_json"),
                trigger_restructure,
                idempotency_key,
            )
        )

    @mcp.tool()
    def mmlg_episode_advance(
        episode_id: str,
        idempotency_key: str | None = None,
    ) -> str:
        """Advance exactly one evidence-gated promotion stage, never external promotion."""
        return _render(game.advance_episode(episode_id, idempotency_key))

    @mcp.tool()
    def mmlg_episode_rollback(
        episode_id: str,
        reason: str,
        rollback_receipt: str,
        idempotency_key: str | None = None,
    ) -> str:
        """Record a local reversible rollback with an explicit receipt."""
        return _render(
            game.rollback_episode(
                episode_id,
                reason,
                rollback_receipt,
                idempotency_key,
            )
        )

    @mcp.tool()
    def mmlg_defects_list(episode_id: str | None = None) -> str:
        """List open score and unverified-watchdog defects from the local ledger."""
        return _render(game.defects(episode_id=episode_id))

    @mcp.tool()
    def mmlg_receipts_verify() -> str:
        """Verify the full sequence, idempotency, and receipt hash chain."""
        return _render(game.verify_ledger())

    @mcp.tool()
    def mmlg_successor_compile(episode_id: str) -> str:
        """Compile a compact successor preserving stage, evidence, defects, and return."""
        return _render(game.successor(episode_id))

    @mcp.resource("athena://meta-ml-game/v2/goal-index")
    def meta_ml_game_goal_index_resource() -> str:
        """Read the frozen 144-goal control-plane index."""
        return _render(game.snapshot)

    @mcp.resource("athena://meta-ml-game/v2/status")
    def meta_ml_game_status_resource() -> str:
        """Read current local MMLG.2 runtime and authority status."""
        return _render(game.status())

    @mcp.resource("athena://meta-ml-game/v2/constitution")
    def meta_ml_game_constitution_resource() -> str:
        """Read the executable reward and promotion boundary summary."""
        return _render(
            {
                "schema": "athena.meta-ml-game-constitution-summary/v2",
                "control_head": CONTROL_HEAD,
                "constitution_version": CONSTITUTION_VERSION,
                "two_currencies": {
                    "juice": "motivation_only_zero_promotion_authority",
                    "evidence": "independent_witnesses_and_hash_chained_receipts",
                },
                "watchdog": {
                    "audit_budget_ratio": 0.15,
                    "automatic_penalty": 0.0,
                    "genuine_catch_multiplier": 25.0,
                },
                "hype_man": {"witnessed_bonus_cap": 0.05},
                "restructure_debit": {
                    "penalty_ratio": 0.05,
                    "non_stacking": True,
                    "phases": list(RESTRUCTURE_PHASES),
                    "identity_judgment": False,
                },
                "promotion_stages": list(STAGES),
                "external_promotion_authority": False,
                **_negative_effects(),
            }
        )
