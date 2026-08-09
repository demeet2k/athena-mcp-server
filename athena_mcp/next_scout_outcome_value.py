from __future__ import annotations

import hashlib
import json
import statistics
from datetime import datetime, timezone
from typing import Any

from .next_quest_pipeline import RollingQuestPipelineRuntime
from .next_quest_pipeline_breadth import NextQuestBreadthRuntime, PREP_KINDS

VERSION = "ATHENA.NEXT.SCOUT.OUTCOME.VALUE.7"
OUTCOME_ARTIFACT = "ATHENA.NEXT.FOCUS.OUTCOME.RECEIPT.7"
TOOLS = {
    "record": "athena_next_focus_outcome_record",
    "calibrate": "athena_next_scout_value_calibrate",
    "overlay": "athena_next_scout_value_overlay",
}
METRICS = ("focus_success", "test_pass_ratio", "rework_count", "blocker_resolution_ratio")


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _receipt_root(pipeline_id: str) -> str:
    return f"prompts/next_quest_pipelines/{pipeline_id}/outcomes/v7"


def _measurement(name: str, raw: Any) -> dict | None:
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise ValueError(f"{name} measurement must be an object")
    if raw.get("observed") is not True:
        raise ValueError(f"{name} requires observed=true")
    source = str(raw.get("source") or "").strip()
    if not source:
        raise ValueError(f"{name} requires a non-empty source")
    value = raw.get("value")
    if name == "focus_success":
        if not isinstance(value, bool):
            raise ValueError("focus_success value must be boolean")
    elif name in {"test_pass_ratio", "blocker_resolution_ratio"}:
        try:
            value = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{name} value must be numeric") from exc
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"{name} value must be between 0 and 1")
    elif name == "rework_count":
        try:
            value = int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("rework_count value must be integer") from exc
        if value < 0:
            raise ValueError("rework_count must be >= 0")
    return {"observed": True, "source": source, "value": value}


def _scores(measurements: dict[str, dict]) -> dict[str, float]:
    out: dict[str, float] = {}
    if "focus_success" in measurements:
        out["downstream_success"] = 1.0 if measurements["focus_success"]["value"] else 0.0
    if "test_pass_ratio" in measurements:
        out["test_quality"] = float(measurements["test_pass_ratio"]["value"])
    if "rework_count" in measurements:
        out["low_rework"] = 1.0 / (1.0 + int(measurements["rework_count"]["value"]))
    if "blocker_resolution_ratio" in measurements:
        out["blocker_resolution"] = float(measurements["blocker_resolution_ratio"]["value"])
    return out


class NextScoutOutcomeValueRuntime:
    """Delayed downstream outcome association for prep kinds.

    V7 binds prep that existed before a quest reached focus to later observed focus
    outcomes. It reports associations only. Co-occurrence is not causal effect and
    never grants evidence, promotion, claim, execution, merge, or release authority.
    """

    def __init__(self, pipeline: RollingQuestPipelineRuntime, breadth: NextQuestBreadthRuntime):
        self.pipeline = pipeline
        self.breadth = breadth
        self.git = pipeline.git
        self.prompt_runtime = pipeline.prompt_runtime

    def _paths(self, pipeline_id: str) -> dict[str, str]:
        base = _receipt_root(pipeline_id)
        return {"base": base, "receipts": f"{base}/receipts"}

    def _receipt_files(self, pipeline_id: str) -> list:
        root = self.prompt_runtime._safe_rel(self._paths(pipeline_id)["receipts"])
        return sorted(root.glob("*.json")) if root.is_dir() else []

    def _read_receipts(self, pipeline_id: str) -> list[dict]:
        rows = []
        for path in self._receipt_files(pipeline_id):
            value = json.loads(path.read_text(encoding="utf-8"))
            if value.get("artifact") == OUTCOME_ARTIFACT and value.get("pipeline_id") == pipeline_id:
                basis = {k: v for k, v in value.items() if k != "receipt_digest"}
                if _digest(basis) != value.get("receipt_digest"):
                    raise ValueError(f"OUTCOME_RECEIPT_DIGEST_HOLD:{path.name}")
                rows.append(value)
        return rows

    def record(self, *, pipeline_id: str, quest_id: str, expected_pipeline_state_digest: str,
               expected_git_head: str, measurements: dict, actor: str = "agent") -> dict:
        state = self.pipeline.state(pipeline_id)
        if state.get("state_digest") != expected_pipeline_state_digest:
            raise ValueError("STALE_PIPELINE_STATE_FOR_FOCUS_OUTCOME")
        current = self.git.head()
        if current != expected_git_head:
            raise ValueError("STALE_GIT_HEAD_FOR_FOCUS_OUTCOME")
        completed = next((dict(x) for x in state.get("completed") or [] if str(x.get("quest_id")) == quest_id), None)
        if not completed:
            raise ValueError("OUTCOME_REQUIRES_COMPLETED_FOCUS_QUEST")
        if str(completed.get("completion_status") or "") not in {"SUCCEEDED", "PARTIAL", "HELD", "FAILED", "NO_PROGRESS"}:
            raise ValueError("COMPLETED_QUEST_HAS_UNSUPPORTED_STATUS")

        breadth, _ = self.breadth._read_breadth(pipeline_id)
        plans = dict(breadth.get("plans") or {})
        observations = dict(breadth.get("observations") or {})
        associated = []
        for plan_id, observation in sorted(observations.items()):
            plan = plans.get(plan_id) or {}
            if str((plan.get("quest") or {}).get("quest_id")) != quest_id:
                continue
            associated.append({
                "plan_id": plan_id,
                "kind": plan.get("kind"),
                "plan_digest": plan.get("packet_digest"),
                "observation_digest": observation.get("result_digest") or observation.get("packet_digest"),
            })
        if not associated:
            raise ValueError("OUTCOME_VALUE_REQUIRES_PREFOCUS_PREP_OBSERVATIONS")

        clean = {}
        for name in METRICS:
            row = _measurement(name, (measurements or {}).get(name))
            if row is not None:
                clean[name] = row
        if not clean:
            raise ValueError("at least one observed downstream metric is required")

        completed_basis = {
            "quest_id": completed.get("quest_id"),
            "ordinal": completed.get("ordinal"),
            "task": completed.get("task"),
            "completion_status": completed.get("completion_status"),
            "completion_summary": completed.get("completion_summary"),
            "completed_at": completed.get("completed_at"),
            "evidence_refs": completed.get("evidence_refs") or [],
        }
        receipt_id = "NVO-" + _digest({
            "pipeline_id": pipeline_id,
            "quest": completed_basis,
            "associated_plan_ids": [x["plan_id"] for x in associated],
            "measurements": clean,
        })[:24]
        path = f"{self._paths(pipeline_id)['receipts']}/{receipt_id}.json"
        existing_path = self.prompt_runtime._safe_rel(path)
        if existing_path.is_file():
            existing = json.loads(existing_path.read_text(encoding="utf-8"))
            return {"status": "REUSED", "receipt": existing, "git_mutation": False,
                    "law": "SAME_OUTCOME_IDENTITY => SAME_RECEIPT"}

        receipt = {
            "artifact": OUTCOME_ARTIFACT,
            "receipt_id": receipt_id,
            "pipeline_id": pipeline_id,
            "pipeline_state_digest": expected_pipeline_state_digest,
            "git_head_before": current,
            "quest": completed_basis,
            "associated_prep": associated,
            "measurements": clean,
            "outcome_scores": _scores(clean),
            "created_at": _utcnow(),
            "actor": actor,
            "standing": "OBSERVED_DOWNSTREAM_ASSOCIATION",
            "authority": "ASSOCIATIONAL_ROUTING_ONLY",
            "causal_effect": False,
            "laws": [
                "SCOUT_SELF_REPORT != VALUE_EVIDENCE",
                "OBSERVED_ASSOCIATION != CAUSAL_EFFECT",
                "FOCUS_OUTCOME != PREP_CAUSAL_CREDIT",
                "OUTCOME_RECEIPT != EVIDENCE_PROMOTION",
            ],
        }
        receipt["receipt_digest"] = _digest(receipt)
        commit = self.prompt_runtime._commit_files(current, {path: json.dumps(receipt, indent=2, sort_keys=True) + "\n"}, actor,
                                                   f"record NEXT focus outcome {quest_id}")
        return {"status": "RECORDED", "receipt": receipt, "checkpoint_head": commit["head"], "git": commit,
                "authority": "ASSOCIATIONAL_ROUTING_ONLY"}

    def calibrate(self, *, pipeline_id: str, prior_strength: int = 3) -> dict:
        prior_strength = int(prior_strength)
        if not 1 <= prior_strength <= 100:
            raise ValueError("prior_strength must be between 1 and 100")
        rows = self._read_receipts(pipeline_id)
        by_kind: dict[str, dict[str, list[float]]] = {kind: {} for kind in PREP_KINDS}
        for receipt in rows:
            for prep in receipt.get("associated_prep") or []:
                kind = str(prep.get("kind") or "")
                if kind not in by_kind:
                    continue
                for metric, value in (receipt.get("outcome_scores") or {}).items():
                    by_kind[kind].setdefault(metric, []).append(float(value))

        # Neutral prior 0.5 is an explicit associational prior, not a causal-value prior.
        calibrated = {}
        for kind in PREP_KINDS:
            metrics = {}
            for metric in ("downstream_success", "test_quality", "low_rework", "blocker_resolution"):
                values = by_kind[kind].get(metric) or []
                if values:
                    med = float(statistics.median(values))
                    n = len(values)
                    score = (prior_strength * 0.5 + n * med) / (prior_strength + n)
                else:
                    med, n, score = None, 0, 0.5
                metrics[metric] = {"observations": n, "median": med, "association_prior": round(score, 6)}
            calibrated[kind] = metrics
        basis = {
            "artifact": VERSION,
            "pipeline_id": pipeline_id,
            "receipt_count": len(rows),
            "prior_strength": prior_strength,
            "calibrated_associations": calibrated,
            "standing": "OBSERVATIONAL_ASSOCIATION_ONLY",
            "causal_effect": False,
            "authority": "ROUTING_ANALYSIS_ONLY",
        }
        return {**basis, "calibration_digest": _digest(basis),
                "laws": ["OBSERVED_ASSOCIATION != CAUSAL_EFFECT", "NO_SCOUT_SELF_RATED_VALUE", "CALIBRATION != CLAIM_OR_PROMOTION"]}

    def overlay(self, *, pipeline_id: str, prior_strength: int = 3) -> dict:
        calibration = self.calibrate(pipeline_id=pipeline_id, prior_strength=prior_strength)
        summary = {}
        for kind, metrics in calibration["calibrated_associations"].items():
            observed = [v["association_prior"] for v in metrics.values() if v["observations"] > 0]
            summary[kind] = {
                "observed_metric_count": sum(1 for v in metrics.values() if v["observations"] > 0),
                "association_index": round(sum(observed) / len(observed), 6) if observed else 0.5,
            }
        basis = {
            "artifact": "ATHENA.NEXT.SCOUT.VALUE.OVERLAY.7",
            "pipeline_id": pipeline_id,
            "calibration_digest": calibration["calibration_digest"],
            "kind_association_overlay": summary,
            "standing": "EXPLANATORY_ASSOCIATION_OVERLAY_ONLY",
            "allocation_effect": "NONE",
            "claim_effect": "NONE",
            "promotion_effect": "NONE",
        }
        return {**basis, "overlay_digest": _digest(basis),
                "law": "V7_ASSOCIATION_OVERLAY_DOES_NOT_CHANGE_V5_V6_ECONOMY"}

    def call_tool(self, name: str, a: dict) -> dict:
        if name == TOOLS["record"]:
            return self.record(pipeline_id=a["pipeline_id"], quest_id=a["quest_id"],
                               expected_pipeline_state_digest=a["expected_pipeline_state_digest"],
                               expected_git_head=a["expected_git_head"], measurements=a["measurements"], actor=a.get("actor", "agent"))
        if name == TOOLS["calibrate"]:
            return self.calibrate(pipeline_id=a["pipeline_id"], prior_strength=a.get("prior_strength", 3))
        if name == TOOLS["overlay"]:
            return self.overlay(pipeline_id=a["pipeline_id"], prior_strength=a.get("prior_strength", 3))
        raise KeyError(name)


NEXT_SCOUT_OUTCOME_VALUE_TOOLS = [
    {"name": TOOLS["record"], "description": "Record a delayed downstream focus-outcome receipt after a quest actually completed focus. Binds prior prep observations to sourced outcome measurements as association only, never causal credit.",
     "inputSchema": {"type": "object", "required": ["pipeline_id", "quest_id", "expected_pipeline_state_digest", "expected_git_head", "measurements"],
                     "properties": {"pipeline_id": {"type": "string"}, "quest_id": {"type": "string"}, "expected_pipeline_state_digest": {"type": "string"}, "expected_git_head": {"type": "string"}, "measurements": {"type": "object"}, "actor": {"type": "string"}}, "additionalProperties": False}},
    {"name": TOOLS["calibrate"], "description": "Read-only V7 delayed outcome association calibration by prep kind. Uses completed-focus outcome receipts; does not claim causal effect or modify V5/V6 benefit priors.",
     "inputSchema": {"type": "object", "required": ["pipeline_id"], "properties": {"pipeline_id": {"type": "string"}, "prior_strength": {"type": "integer", "minimum": 1, "maximum": 100}}, "additionalProperties": False}},
    {"name": TOOLS["overlay"], "description": "Read-only explanatory association overlay for prep kinds. It does not alter allocation, claims, evidence, promotion, or the V5/V6 economy.",
     "inputSchema": {"type": "object", "required": ["pipeline_id"], "properties": {"pipeline_id": {"type": "string"}, "prior_strength": {"type": "integer", "minimum": 1, "maximum": 100}}, "additionalProperties": False}},
]
NEXT_SCOUT_OUTCOME_VALUE_TOOL_NAMES = {x["name"] for x in NEXT_SCOUT_OUTCOME_VALUE_TOOLS}


def install_next_scout_outcome_value_extension(prompt_runtime_cls, tool_list: list[dict], tool_names: set[str]) -> None:
    if getattr(prompt_runtime_cls, "_athena_next_scout_outcome_value_v7_registered", False):
        return
    previous_call = prompt_runtime_cls.call_tool
    def call_with_outcome_value(self, name, arguments):
        if name in NEXT_SCOUT_OUTCOME_VALUE_TOOL_NAMES:
            runtime = getattr(self, "_next_scout_outcome_value_runtime_v7", None)
            if runtime is None:
                pipeline = getattr(self, "_next_pipeline_runtime_v1", None)
                if pipeline is None:
                    pipeline = RollingQuestPipelineRuntime(self.git, self)
                    self._next_pipeline_runtime_v1 = pipeline
                breadth = getattr(self, "_next_pipeline_breadth_runtime_v2", None)
                if breadth is None:
                    breadth = NextQuestBreadthRuntime(pipeline)
                    self._next_pipeline_breadth_runtime_v2 = breadth
                runtime = NextScoutOutcomeValueRuntime(pipeline, breadth)
                self._next_scout_outcome_value_runtime_v7 = runtime
            return runtime.call_tool(name, arguments)
        return previous_call(self, name, arguments)
    prompt_runtime_cls.call_tool = call_with_outcome_value
    prompt_runtime_cls._athena_next_scout_outcome_value_v7_registered = True
    for tool in NEXT_SCOUT_OUTCOME_VALUE_TOOLS:
        if tool["name"] not in tool_names:
            tool_list.append(tool)
            tool_names.add(tool["name"])


__all__ = ["VERSION", "OUTCOME_ARTIFACT", "TOOLS", "NextScoutOutcomeValueRuntime",
           "NEXT_SCOUT_OUTCOME_VALUE_TOOLS", "NEXT_SCOUT_OUTCOME_VALUE_TOOL_NAMES",
           "install_next_scout_outcome_value_extension"]