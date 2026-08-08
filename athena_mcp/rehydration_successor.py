from __future__ import annotations

import math
from typing import Any

from .rehydration_loop import RehydrationLoopRuntime, _sha, _state_digest

ARTIFACT = "ATHENA.REHYDRATION.SUCCESSOR.BATON.V1"
GOOD_METRICS = ("utility", "dependency_unblocking", "uncertainty_reduction", "novelty")
BAD_METRICS = ("risk", "cost", "repetition")
ALL_METRICS = GOOD_METRICS + BAD_METRICS
DEFAULT_WEIGHTS = {
    "utility": 1.0,
    "dependency_unblocking": 1.2,
    "uncertainty_reduction": 0.8,
    "novelty": 0.25,
    "risk": -1.0,
    "cost": -0.6,
    "repetition": -1.0,
}
SOURCE_DEFAULTS = {
    "AGENT_NEXT_TASK": {
        "utility": 0.85, "dependency_unblocking": 0.65, "uncertainty_reduction": 0.45,
        "novelty": 0.25, "risk": 0.20, "cost": 0.35, "repetition": 0.15,
    },
    "COMPLETION_RESIDUAL": {
        "utility": 0.75, "dependency_unblocking": 0.90, "uncertainty_reduction": 0.75,
        "novelty": 0.40, "risk": 0.15, "cost": 0.35, "repetition": 0.10,
    },
    "EXPLICIT_CANDIDATE": {
        "utility": 0.50, "dependency_unblocking": 0.50, "uncertainty_reduction": 0.50,
        "novelty": 0.50, "risk": 0.50, "cost": 0.50, "repetition": 0.50,
    },
    "CURRENT_TASK_CONTINUATION": {
        "utility": 0.40, "dependency_unblocking": 0.25, "uncertainty_reduction": 0.20,
        "novelty": 0.05, "risk": 0.25, "cost": 0.45, "repetition": 0.85,
    },
}


def _clamp(value: Any, default: float) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return default
    if not math.isfinite(out):
        return default
    return max(0.0, min(1.0, out))


def _task_from_raw(raw: Any) -> str:
    if isinstance(raw, str):
        return raw.strip()
    if not isinstance(raw, dict):
        return ""
    for key in ("task", "next_task", "title", "description", "summary", "value", "code", "kind"):
        value = raw.get(key)
        if isinstance(value, str) and value.strip():
            if key in {"code", "kind"}:
                return f"Resolve {value.strip()}"
            return value.strip()
    return ""


def _explicit_metrics(raw: Any) -> dict[str, float]:
    if not isinstance(raw, dict):
        return {}
    merged = {}
    if isinstance(raw.get("metrics"), dict):
        merged.update(raw["metrics"])
    for key in ALL_METRICS:
        if key in raw:
            merged[key] = raw[key]
    return {key: _clamp(value, 0.5) for key, value in merged.items() if key in ALL_METRICS}


def _dominates(left: dict, right: dict) -> bool:
    lm = left["metrics"]
    rm = right["metrics"]
    weak = all(lm[k] >= rm[k] for k in GOOD_METRICS) and all(lm[k] <= rm[k] for k in BAD_METRICS)
    strict = any(lm[k] > rm[k] for k in GOOD_METRICS) or any(lm[k] < rm[k] for k in BAD_METRICS)
    return weak and strict


class SuccessorCompiler:
    """Compile a replayable successor baton from observed cycle outputs.

    Scores are routing heuristics, not evidence or authority. Ambiguous maxima are
    preserved by default; the compiler never turns a tie into a hidden lexical
    decision.
    """

    def __init__(self, runtime: RehydrationLoopRuntime):
        self.runtime = runtime

    @staticmethod
    def _policy(value: dict | None) -> dict:
        raw = dict(value or {})
        weights = dict(DEFAULT_WEIGHTS)
        if isinstance(raw.get("weights"), dict):
            for key, val in raw["weights"].items():
                if key not in ALL_METRICS:
                    continue
                try:
                    number = float(val)
                except (TypeError, ValueError):
                    continue
                if math.isfinite(number):
                    weights[key] = number
        epsilon = raw.get("tie_epsilon", 1e-9)
        try:
            epsilon = max(0.0, float(epsilon))
        except (TypeError, ValueError):
            epsilon = 1e-9
        return {
            "weights": weights,
            "tie_epsilon": epsilon,
            "tie_policy": "PRESERVE",
            "authority": "ROUTING_ONLY",
        }

    @staticmethod
    def _candidate(raw: Any, source: str, ordinal: int) -> dict | None:
        task = _task_from_raw(raw)
        if not task:
            return None
        defaults = dict(SOURCE_DEFAULTS[source])
        explicit = _explicit_metrics(raw)
        metrics = {key: explicit.get(key, defaults[key]) for key in ALL_METRICS}
        source_ref = None
        if isinstance(raw, dict):
            source_ref = raw.get("source_ref") or raw.get("id") or raw.get("run_id") or raw.get("node_id")
        origin = "MIXED" if explicit and len(explicit) < len(ALL_METRICS) else "EXPLICIT" if len(explicit) == len(ALL_METRICS) else "SOURCE_HEURISTIC"
        basis = {
            "task": task,
            "source": source,
            "source_ref": source_ref,
            "metrics": metrics,
            "ordinal": ordinal,
        }
        return {
            "candidate_id": "SC-" + _sha(basis)[:16],
            "task": task,
            "source": source,
            "source_ref": source_ref,
            "metrics": metrics,
            "metric_origin": origin,
            "routing_only": True,
        }

    @staticmethod
    def _dedupe(candidates: list[dict]) -> list[dict]:
        # Source priority is explicit so duplicate task wording cannot silently
        # inherit an optimistic blend of metrics from several origins.
        priority = {
            "EXPLICIT_CANDIDATE": 0,
            "AGENT_NEXT_TASK": 1,
            "COMPLETION_RESIDUAL": 2,
            "CURRENT_TASK_CONTINUATION": 3,
        }
        chosen: dict[str, dict] = {}
        sources: dict[str, set[str]] = {}
        for candidate in candidates:
            key = " ".join(candidate["task"].lower().split())
            sources.setdefault(key, set()).add(candidate["source"])
            old = chosen.get(key)
            if old is None or priority[candidate["source"]] < priority[old["source"]]:
                chosen[key] = candidate
        rows = []
        for key, candidate in chosen.items():
            row = dict(candidate)
            row["supporting_sources"] = sorted(sources[key])
            rows.append(row)
        return sorted(rows, key=lambda x: (x["task"].lower(), x["candidate_id"]))

    @staticmethod
    def _score(candidate: dict, policy: dict) -> float:
        return sum(candidate["metrics"][key] * policy["weights"][key] for key in ALL_METRICS)

    def compile(
        self,
        *,
        loop_id: str,
        expected_state_digest: str,
        completion: dict | None = None,
        candidates: list[Any] | None = None,
        policy: dict | None = None,
    ) -> dict:
        state, _ = self.runtime._read_state(loop_id)
        if _state_digest(state) != state.get("state_digest") or state.get("state_digest") != expected_state_digest:
            raise ValueError("STALE_OR_TAMPERED_REHYDRATION_STATE")
        completion = dict(completion or state.get("last_completion") or {})
        route_policy = self._policy(policy or completion.get("successor_policy"))

        if completion.get("terminal"):
            baton = {
                "artifact": ARTIFACT,
                "status": "TERMINAL",
                "loop_id": loop_id,
                "from_step": state.get("step_index"),
                "goal": state.get("goal"),
                "current_task": state.get("task"),
                "policy": route_policy,
                "candidates": [],
                "pareto_candidate_ids": [],
                "selected": None,
                "ties": [],
                "deferred_candidate_ids": [],
                "laws": ["TERMINAL_COMPLETION => NO_SUCCESSOR", "ROUTING_SCORE != EVIDENCE", "ROUTING_SCORE != AUTHORITY"],
            }
            baton["baton_digest"] = _sha(baton)
            return baton

        rows: list[dict] = []
        ordinal = 0
        next_task = completion.get("next_task")
        if isinstance(next_task, str) and next_task.strip():
            row = self._candidate({"task": next_task}, "AGENT_NEXT_TASK", ordinal)
            ordinal += 1
            if row:
                rows.append(row)

        for raw in completion.get("residuals") or []:
            row = self._candidate(raw, "COMPLETION_RESIDUAL", ordinal)
            ordinal += 1
            if row:
                rows.append(row)

        explicit = candidates if candidates is not None else completion.get("successor_candidates") or []
        if not isinstance(explicit, list):
            raise ValueError("successor_candidates must be an array")
        for raw in explicit:
            row = self._candidate(raw, "EXPLICIT_CANDIDATE", ordinal)
            ordinal += 1
            if row:
                rows.append(row)

        if str(completion.get("status") or "").upper() in {"PARTIAL", "HELD", "NO_PROGRESS"}:
            row = self._candidate({"task": state.get("task")}, "CURRENT_TASK_CONTINUATION", ordinal)
            if row:
                rows.append(row)

        rows = self._dedupe(rows)
        for row in rows:
            row["routing_score"] = self._score(row, route_policy)

        pareto = [row for row in rows if not any(_dominates(other, row) for other in rows if other is not row)]
        pareto = sorted(pareto, key=lambda x: (-x["routing_score"], x["task"].lower(), x["candidate_id"]))
        status = "NO_SUCCESSOR"
        selected = None
        ties: list[dict] = []
        if pareto:
            best = pareto[0]["routing_score"]
            ties = [row for row in pareto if abs(row["routing_score"] - best) <= route_policy["tie_epsilon"]]
            if len(ties) == 1:
                status = "SELECTED"
                selected = ties[0]
            else:
                status = "AMBIGUOUS"

        baton = {
            "artifact": ARTIFACT,
            "status": status,
            "loop_id": loop_id,
            "from_step": state.get("step_index"),
            "goal": state.get("goal"),
            "current_task": state.get("task"),
            "policy": route_policy,
            "candidates": rows,
            "pareto_candidate_ids": [row["candidate_id"] for row in pareto],
            "selected": selected,
            "ties": ties,
            "deferred_candidate_ids": [row["candidate_id"] for row in rows if selected is None or row["candidate_id"] != selected["candidate_id"]],
            "selection_reason": (
                "unique highest routing score on the nondominated frontier"
                if status == "SELECTED"
                else "multiple nondominated successors share the highest routing score; preserve ambiguity"
                if status == "AMBIGUOUS"
                else "no concrete successor candidates were observed"
            ),
            "laws": [
                "SUCCESSOR_BATON != TASK_TRUTH",
                "ROUTING_SCORE != EVIDENCE",
                "ROUTING_SCORE != AUTHORITY",
                "AMBIGUITY != FAILURE",
                "TIE => PRESERVE_UNTIL_NEW_EVIDENCE_OR_POLICY",
            ],
        }
        baton["baton_digest"] = _sha(baton)
        return baton


SUCCESSOR_TOOLS = [
    {
        "name": "athena_rehydration_successor_preview",
        "description": "Compile a replayable successor baton from the current rehydration state plus observed completion/residual candidates. Scores are routing-only; ties are preserved.",
        "inputSchema": {
            "type": "object",
            "required": ["loop_id", "expected_state_digest"],
            "properties": {
                "loop_id": {"type": "string"},
                "expected_state_digest": {"type": "string"},
                "completion": {"type": ["object", "null"]},
                "candidates": {"type": "array", "items": {"type": ["object", "string"]}},
                "policy": {"type": ["object", "null"]},
            },
            "additionalProperties": False,
        },
    }
]
SUCCESSOR_TOOL_NAMES = {tool["name"] for tool in SUCCESSOR_TOOLS}


def install_successor_extension(runtime_cls=RehydrationLoopRuntime, tool_list=None, tool_names=None) -> None:
    """Install auto-steering and preview without creating another control plane."""
    if getattr(runtime_cls, "_athena_successor_v1_registered", False):
        return
    if tool_list is not None and tool_names is not None:
        for tool in SUCCESSOR_TOOLS:
            if tool["name"] not in tool_names:
                tool_list.append(tool)
                tool_names.add(tool["name"])
        # Document the auto-steer membrane on the already registered advance tool.
        for tool in tool_list:
            if tool.get("name") != "athena_rehydration_advance":
                continue
            completion = (((tool.get("inputSchema") or {}).get("properties") or {}).get("completion") or {})
            props = completion.setdefault("properties", {})
            props.setdefault("self_steer", {"type": "boolean", "description": "Default true. Compile a successor baton before generating the next prompt."})
            props.setdefault("successor_candidates", {"type": "array", "items": {"type": ["object", "string"]}})
            props.setdefault("successor_policy", {"type": "object"})

    original_advance = runtime_cls.advance
    original_resume = runtime_cls.resume
    original_call = runtime_cls.call_tool

    def _compiler(self):
        compiler = getattr(self, "_successor_compiler_v1", None)
        if compiler is None:
            compiler = SuccessorCompiler(self)
            self._successor_compiler_v1 = compiler
        return compiler

    def advance_with_successor(self, *args, **kwargs):
        completion = dict(kwargs.get("completion") or {})
        baton = None
        if completion.get("self_steer", True):
            loop_id = kwargs.get("loop_id")
            expected_state_digest = kwargs.get("expected_state_digest")
            if loop_id and expected_state_digest:
                baton = _compiler(self).compile(
                    loop_id=loop_id,
                    expected_state_digest=expected_state_digest,
                    completion=completion,
                    candidates=completion.get("successor_candidates"),
                    policy=completion.get("successor_policy"),
                )
                completion["successor_baton"] = baton
                if not completion.get("terminal"):
                    if baton["status"] == "SELECTED":
                        completion["next_task"] = baton["selected"]["task"]
                    elif baton["status"] == "AMBIGUOUS":
                        tasks = [row["task"] for row in baton["ties"][:6]]
                        completion["next_task"] = "Resolve successor ambiguity among: " + " | ".join(tasks)
                    elif baton["status"] == "NO_SUCCESSOR":
                        completion["next_task"] = "Reconstruct the remaining objective and produce a lawful successor candidate set"
        kwargs["completion"] = completion
        result = original_advance(self, *args, **kwargs)
        if baton is not None:
            result["successor_baton"] = baton
        return result

    def resume_with_successor(self, *args, **kwargs):
        result = original_resume(self, *args, **kwargs)
        loop_id = kwargs.get("loop_id") if "loop_id" in kwargs else args[0] if args else None
        if loop_id:
            state, _ = self._read_state(loop_id)
            completion = state.get("last_completion") or {}
            result["successor_baton"] = completion.get("successor_baton")
        return result

    def call_tool_with_successor(self, name, a):
        if name == "athena_rehydration_successor_preview":
            return _compiler(self).compile(
                loop_id=a["loop_id"],
                expected_state_digest=a["expected_state_digest"],
                completion=a.get("completion"),
                candidates=a.get("candidates"),
                policy=a.get("policy"),
            )
        return original_call(self, name, a)

    runtime_cls.advance = advance_with_successor
    runtime_cls.resume = resume_with_successor
    runtime_cls.call_tool = call_tool_with_successor
    runtime_cls._athena_successor_v1_registered = True
