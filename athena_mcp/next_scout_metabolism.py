from __future__ import annotations

import hashlib
import json
import math
import os
import statistics
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .git_backend import GitStateError, GitStaleHead
from .next_quest_pipeline import RollingQuestPipelineRuntime
from .next_quest_pipeline_breadth import NextQuestBreadthRuntime
from .next_scout_economy import RESOURCE_KEYS, RESOURCE_PROFILE
from .prompt_remote import PromptRemoteSync

VERSION = "ATHENA.NEXT.SCOUT.METABOLISM.6"
RECEIPT_ARTIFACT = "ATHENA.NEXT.SCOUT.OBSERVED.COST.RECEIPT.6"
RECORD_TOOL = "athena_next_scout_receipt_record"
CALIBRATE_TOOL = "athena_next_scout_calibrate"
ROOT = "prompts/next_quest_pipelines"
METRICS = tuple(RESOURCE_KEYS)


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_number(value: Any, field: str) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"invalid {field}") from exc
    if not math.isfinite(out) or out < 0:
        raise ValueError(f"{field} must be finite and nonnegative")
    return out


def _metric(raw: Any, name: str) -> dict | None:
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise ValueError(f"measurement {name} must be an object")
    if raw.get("observed") is not True:
        raise ValueError(f"measurement {name} requires observed=true")
    source = str(raw.get("source") or "").strip()
    if not source:
        raise ValueError(f"measurement {name} requires source")
    value = _safe_number(raw.get("value"), f"measurement {name}.value")
    evidence_ref = str(raw.get("evidence_ref") or "").strip() or None
    return {
        "value": value,
        "observed": True,
        "source": source,
        "evidence_ref": evidence_ref,
    }


class NextScoutMetabolismRuntime:
    """Observed-cost receipts and robust calibration for NEXT scout economics.

    V6 calibrates cost priors only. It does not let scouts award themselves
    utility, evidence, truth, promotion standing, or execution authority.
    """

    def __init__(self, pipeline: RollingQuestPipelineRuntime, breadth: NextQuestBreadthRuntime):
        self.pipeline = pipeline
        self.breadth = breadth
        self.git = pipeline.git
        self.remote_sync = PromptRemoteSync(self.git)

    def _root(self) -> Path:
        if not self.git.enabled:
            raise GitStateError("ATHENA_GIT_ROOT is required for scout metabolism")
        return self.git.root

    @staticmethod
    def _base(pipeline_id: str) -> str:
        if not pipeline_id or any(ch not in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_.-" for ch in pipeline_id):
            raise ValueError("invalid pipeline_id")
        return f"{ROOT}/{pipeline_id}/metabolism"

    def _receipt_dir(self, pipeline_id: str) -> Path:
        return self._root() / self._base(pipeline_id) / "receipts"

    def _commit_file(self, *, expected_git_head: str, rel: str, text: str, actor: str) -> dict:
        current = self.git.head()
        if current != expected_git_head:
            raise GitStaleHead(json.dumps({"status": "STALE_GIT_HEAD_FOR_SCOUT_RECEIPT", "expected": expected_git_head, "current": current}))
        if self.git._git("status", "--porcelain"):
            raise GitStateError("DIRTY_GIT_ROOT: scout metabolism refuses unrelated working-tree state")
        if not rel.startswith(ROOT + "/") or "/metabolism/receipts/" not in rel:
            raise ValueError("scout metabolism may write only receipt files")
        path = self._root() / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            path.write_text(text, encoding="utf-8")
            self.git._git("add", "--", rel)
            env = os.environ.copy()
            env.setdefault("GIT_AUTHOR_NAME", actor)
            env.setdefault("GIT_AUTHOR_EMAIL", "athena@local")
            env.setdefault("GIT_COMMITTER_NAME", actor)
            env.setdefault("GIT_COMMITTER_EMAIL", "athena@local")
            p = subprocess.run(
                ["git", "-C", str(self._root()), "commit", "-m", f"record scout metabolism receipt {Path(rel).stem}"],
                text=True, capture_output=True, env=env,
            )
            if p.returncode:
                raise GitStateError(p.stderr.strip() or p.stdout.strip())
        except Exception:
            self.git._git("reset", "--hard", current)
            raise
        return {"status": "COMMITTED_LOCAL", "previous_head": current, "head": self.git.head(), "path": rel}

    def _load_receipts(self, pipeline_id: str) -> list[dict]:
        root = self._receipt_dir(pipeline_id)
        if not root.is_dir():
            return []
        rows = []
        for path in sorted(root.glob("*.json")):
            try:
                row = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if row.get("artifact") != RECEIPT_ARTIFACT:
                continue
            expected = _digest({k: v for k, v in row.items() if k != "receipt_digest"})
            if expected != row.get("receipt_digest"):
                continue
            rows.append(row)
        return rows

    def record(
        self,
        *,
        pipeline_id: str,
        plan_id: str,
        expected_pipeline_state_digest: str,
        expected_git_head: str,
        measurements: dict,
        actor: str = "agent",
        remote: str = "origin",
        shared_remote_mode: str = "REQUIRED",
    ) -> dict:
        pipeline = self.pipeline.state(pipeline_id)
        if pipeline.get("state_digest") != expected_pipeline_state_digest:
            raise ValueError("STALE_PIPELINE_STATE_FOR_SCOUT_RECEIPT")
        breadth, _ = self.breadth._read_breadth(pipeline_id)
        plan = (breadth.get("plans") or {}).get(plan_id)
        observation = (breadth.get("observations") or {}).get(plan_id)
        if not plan:
            raise ValueError("SCOUT_RECEIPT_PLAN_NOT_FOUND")
        if not observation:
            raise ValueError("SCOUT_RECEIPT_REQUIRES_OBSERVED_PREP_RESULT")
        kind = str(plan.get("kind") or "")
        if kind not in RESOURCE_PROFILE:
            raise ValueError("SCOUT_RECEIPT_UNKNOWN_RESOURCE_PROFILE")
        if not isinstance(measurements, dict) or not measurements:
            raise ValueError("measurements are required")
        normalized = {}
        for name in METRICS:
            value = _metric(measurements.get(name), name)
            if value is not None:
                normalized[name] = value
        extra = sorted(set(measurements) - set(METRICS))
        if extra:
            raise ValueError(f"unknown measurement keys: {extra}")
        if not normalized:
            raise ValueError("at least one observed measurement is required")

        observation_digest = _digest(observation)
        identity = {
            "pipeline_id": pipeline_id,
            "plan_id": plan_id,
            "plan_digest": plan.get("packet_digest"),
            "observation_digest": observation_digest,
            "kind": kind,
            "measurements": normalized,
        }
        receipt_id = "SMR-" + _digest(identity)[:24]
        receipt = {
            "artifact": RECEIPT_ARTIFACT,
            "receipt_id": receipt_id,
            **identity,
            "quest_id": (plan.get("quest") or {}).get("quest_id"),
            "recorded_at": _utcnow(),
            "actor": str(actor or "agent"),
            "standing": "OBSERVED_MEASUREMENT_ASSERTION",
            "authority": "COST_CALIBRATION_ONLY",
            "laws": [
                "PREDICTION != OBSERVATION",
                "OBSERVED_COST != TASK_VALUE",
                "SCOUT_RECEIPT != EVIDENCE_PROMOTION",
                "ONLY_OBSERVED_MEASUREMENTS_ENTER_CALIBRATION",
            ],
        }
        receipt["receipt_digest"] = _digest(receipt)
        rel = f"{self._base(pipeline_id)}/receipts/{receipt_id}.json"
        path = self._root() / rel
        if path.is_file():
            existing = json.loads(path.read_text(encoding="utf-8"))
            if existing.get("receipt_digest") == receipt["receipt_digest"]:
                return {"status": "REUSED", "receipt": existing, "git_mutation": False}
            return {"status": "SCOUT_RECEIPT_IDENTITY_CONFLICT_HOLD", "receipt_id": receipt_id, "git_mutation": False}

        mode = str(shared_remote_mode or "REQUIRED").upper()
        if mode not in {"REQUIRED", "BEST_EFFORT", "DISABLED"}:
            raise ValueError("shared_remote_mode must be REQUIRED, BEST_EFFORT, or DISABLED")
        if mode != "DISABLED":
            sync = self.remote_sync.sync(remote)
            if mode == "REQUIRED" and not sync.get("shared_frontier_verified"):
                return {"status": "SCOUT_RECEIPT_SHARED_FRONTIER_HOLD", "remote_sync": sync, "git_mutation": False}
            expected_git_head = self.git.head()
        commit = self._commit_file(
            expected_git_head=expected_git_head,
            rel=rel,
            text=json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            actor=str(actor or "agent"),
        )
        publish = {"status": "DISABLED", "shared_frontier_verified": False}
        if mode != "DISABLED":
            publish = self.remote_sync.publish(commit["head"], remote)
            if mode == "REQUIRED" and not publish.get("shared_frontier_verified"):
                return {
                    "status": "SCOUT_RECEIPT_LOCAL_PUBLISH_HOLD",
                    "receipt": receipt,
                    "git": commit,
                    "remote_publish": publish,
                    "durable_return": False,
                }
        return {
            "status": "RECORDED",
            "receipt": receipt,
            "git": commit,
            "remote_publish": publish,
            "durable_return": bool(publish.get("shared_frontier_verified")) if mode != "DISABLED" else False,
        }

    @staticmethod
    def _median(values: list[float]) -> float | None:
        return float(statistics.median(values)) if values else None

    def calibrate(self, *, pipeline_id: str, prior_strength: int = 3) -> dict:
        prior_strength = int(prior_strength)
        if not 1 <= prior_strength <= 100:
            raise ValueError("prior_strength must be between 1 and 100")
        receipts = self._load_receipts(pipeline_id)
        grouped: dict[str, dict[str, list[float]]] = {
            kind: {metric: [] for metric in METRICS} for kind in RESOURCE_PROFILE
        }
        for receipt in receipts:
            kind = str(receipt.get("kind") or "")
            if kind not in grouped:
                continue
            for metric, measurement in (receipt.get("measurements") or {}).items():
                if metric in METRICS and isinstance(measurement, dict) and measurement.get("observed") is True:
                    grouped[kind][metric].append(float(measurement["value"]))

        calibrated = {}
        evidence = {}
        for kind, prior in RESOURCE_PROFILE.items():
            profile = dict(prior)
            counts = {}
            medians = {}
            for metric in METRICS:
                values = grouped[kind][metric]
                counts[metric] = len(values)
                med = self._median(values)
                medians[metric] = med
                if med is None:
                    continue
                n = len(values)
                profile[metric] = round((prior_strength * float(prior[metric]) + n * med) / (prior_strength + n), 4)
            calibrated[kind] = profile
            evidence[kind] = {"observation_counts": counts, "observed_medians": medians}

        basis = {
            "artifact": VERSION,
            "pipeline_id": pipeline_id,
            "prior_strength": prior_strength,
            "receipt_count": len(receipts),
            "prior_profiles": RESOURCE_PROFILE,
            "calibrated_profiles": calibrated,
            "evidence": evidence,
            "method": "PRIOR_SHRINKAGE_TOWARD_OBSERVED_MEDIAN_V1",
        }
        return {
            **basis,
            "status": "CALIBRATED" if receipts else "PRIOR_ONLY",
            "calibration_digest": _digest(basis),
            "authority": "ROUTING_CALIBRATION_ONLY",
            "mutation": "NONE",
            "laws": [
                "PREDICTION != OBSERVATION",
                "MISSING_MEASUREMENT != ZERO",
                "ONLY_OBSERVED_RECEIPTS_UPDATE_COST_PRIORS",
                "COST_CALIBRATION != BENEFIT_CALIBRATION",
                "CALIBRATION != CLAIM_OR_EXECUTION_AUTHORITY",
            ],
        }

    def call_tool(self, name: str, a: dict) -> dict:
        if name == RECORD_TOOL:
            return self.record(
                pipeline_id=a["pipeline_id"],
                plan_id=a["plan_id"],
                expected_pipeline_state_digest=a["expected_pipeline_state_digest"],
                expected_git_head=a["expected_git_head"],
                measurements=a["measurements"],
                actor=a.get("actor", "agent"),
                remote=a.get("remote", "origin"),
                shared_remote_mode=a.get("shared_remote_mode", "REQUIRED"),
            )
        if name == CALIBRATE_TOOL:
            return self.calibrate(pipeline_id=a["pipeline_id"], prior_strength=a.get("prior_strength", 3))
        raise KeyError(name)


NEXT_SCOUT_METABOLISM_TOOLS = [
    {
        "name": RECORD_TOOL,
        "description": "Record an immutable observed scout cost receipt only after the prep result exists. Measurements require observed=true and a source; receipts calibrate cost priors only and grant no truth, value, claim, execution, or promotion authority.",
        "inputSchema": {
            "type": "object",
            "required": ["pipeline_id", "plan_id", "expected_pipeline_state_digest", "expected_git_head", "measurements"],
            "properties": {
                "pipeline_id": {"type": "string"},
                "plan_id": {"type": "string"},
                "expected_pipeline_state_digest": {"type": "string"},
                "expected_git_head": {"type": "string"},
                "measurements": {"type": "object"},
                "actor": {"type": "string"},
                "remote": {"type": "string"},
                "shared_remote_mode": {"type": "string", "enum": ["REQUIRED", "BEST_EFFORT", "DISABLED"]},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": CALIBRATE_TOOL,
        "description": "Read-only robust scout-cost calibration from immutable observed-cost receipts. Uses prior shrinkage toward observed medians; missing metrics remain prior values and benefit priors are not self-trained.",
        "inputSchema": {
            "type": "object",
            "required": ["pipeline_id"],
            "properties": {
                "pipeline_id": {"type": "string"},
                "prior_strength": {"type": "integer", "minimum": 1, "maximum": 100},
            },
            "additionalProperties": False,
        },
    },
]
NEXT_SCOUT_METABOLISM_TOOL_NAMES = {x["name"] for x in NEXT_SCOUT_METABOLISM_TOOLS}


def install_next_scout_metabolism_extension(prompt_runtime_cls, tool_list: list[dict], tool_names: set[str]) -> None:
    if getattr(prompt_runtime_cls, "_athena_next_scout_metabolism_v6_registered", False):
        return
    previous_call = prompt_runtime_cls.call_tool

    def call_with_metabolism(self, name, arguments):
        if name in NEXT_SCOUT_METABOLISM_TOOL_NAMES:
            runtime = getattr(self, "_next_scout_metabolism_runtime_v6", None)
            if runtime is None:
                pipeline = getattr(self, "_next_pipeline_runtime_v1", None)
                if pipeline is None:
                    pipeline = RollingQuestPipelineRuntime(self.git, self)
                    self._next_pipeline_runtime_v1 = pipeline
                breadth = getattr(self, "_next_pipeline_breadth_runtime_v2", None)
                if breadth is None:
                    breadth = NextQuestBreadthRuntime(pipeline)
                    self._next_pipeline_breadth_runtime_v2 = breadth
                runtime = NextScoutMetabolismRuntime(pipeline, breadth)
                self._next_scout_metabolism_runtime_v6 = runtime
            return runtime.call_tool(name, arguments)
        return previous_call(self, name, arguments)

    prompt_runtime_cls.call_tool = call_with_metabolism
    prompt_runtime_cls._athena_next_scout_metabolism_v6_registered = True
    for tool in NEXT_SCOUT_METABOLISM_TOOLS:
        if tool["name"] not in tool_names:
            tool_list.append(tool)
            tool_names.add(tool["name"])


__all__ = [
    "VERSION", "RECEIPT_ARTIFACT", "RECORD_TOOL", "CALIBRATE_TOOL",
    "NextScoutMetabolismRuntime", "NEXT_SCOUT_METABOLISM_TOOLS",
    "NEXT_SCOUT_METABOLISM_TOOL_NAMES", "install_next_scout_metabolism_extension",
]
