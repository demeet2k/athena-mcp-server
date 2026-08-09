from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from .git_backend import GitStateError
from .next_quest_pipeline import RollingQuestPipelineRuntime, _sha
from .prompt_runtime import PromptRuntime

VERSION = "ATHENA.NEXT.QUEST.PIPELINE.BREADTH.2"
PREP_KINDS = (
    "DEPENDENCY_MAP",
    "RETRIEVAL_PLAN",
    "TEST_DESIGN",
    "RISK_SCAN",
    "SOURCE_REVIEW",
    "INTERFACE_MAP",
)
PREP_STATES = {"PLANNED", "OBSERVED", "HOLD", "SUPERSEDED"}


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _digest(value: Any) -> str:
    return _sha(value)


def _packet_digest(packet: dict) -> str:
    return _digest({k: v for k, v in packet.items() if k != "packet_digest"})


def _quest_snapshot(quest: dict) -> dict:
    return {
        "quest_id": quest.get("quest_id"),
        "ordinal": quest.get("ordinal"),
        "task": quest.get("task"),
        "task_key": quest.get("task_key"),
        "source": quest.get("source"),
        "source_ref": quest.get("source_ref"),
    }


def _plan_id(pipeline_id: str, quest_id: str, kind: str, pipeline_state_digest: str) -> str:
    return "PREP-" + _digest({
        "pipeline_id": pipeline_id,
        "quest_id": quest_id,
        "kind": kind,
        "pipeline_state_digest": pipeline_state_digest,
    })[:20]


def _default_instruction(kind: str, quest: dict) -> str:
    task = str(quest.get("task") or "")
    return {
        "DEPENDENCY_MAP": f"Map explicit dependencies, blockers, prerequisite artifacts, and handoff boundaries for staged quest: {task}",
        "RETRIEVAL_PLAN": f"Identify the exact sources, repository paths, issues, receipts, and queries that should be retrieved before staged quest execution: {task}",
        "TEST_DESIGN": f"Design falsifiable tests, adversarial cases, and acceptance gates for staged quest without executing or mutating its focus lane: {task}",
        "RISK_SCAN": f"Enumerate likely failure modes, authority boundaries, freshness hazards, and rollback requirements for staged quest: {task}",
        "SOURCE_REVIEW": f"Review already available source/evidence coordinates relevant to staged quest and record gaps without promoting claims: {task}",
        "INTERFACE_MAP": f"Map the organs, tools, schemas, state namespaces, and ownership boundaries touched by staged quest: {task}",
    }[kind]


class NextQuestBreadthRuntime:
    """Read/record preparation for Q2/Q3 while preserving Q1 as the sole focus.

    Preparation packets are contextual work products only. They never complete a
    staged quest, mutate its focus status, claim work, grant evidence standing, or
    imply background execution.
    """

    def __init__(self, pipeline: RollingQuestPipelineRuntime):
        self.pipeline = pipeline
        self.git = pipeline.git
        self.prompt_runtime = pipeline.prompt_runtime

    @staticmethod
    def _breadth_paths(pipeline_id: str) -> dict[str, str]:
        base = f"prompts/next_quest_pipelines/{pipeline_id}/breadth"
        return {"base": base, "state": f"{base}/state.json", "packets": f"{base}/packets"}

    def _read_breadth(self, pipeline_id: str) -> tuple[dict, dict[str, str]]:
        paths = self._breadth_paths(pipeline_id)
        path = self.prompt_runtime._safe_rel(paths["state"])
        if not path.is_file():
            return {
                "artifact": VERSION,
                "pipeline_id": pipeline_id,
                "created_at": _utcnow(),
                "updated_at": _utcnow(),
                "revision": 0,
                "pipeline_state_digest": None,
                "plans": {},
                "observations": {},
                "history": [],
            }, paths
        value = json.loads(path.read_text(encoding="utf-8"))
        if value.get("artifact") != VERSION or value.get("pipeline_id") != pipeline_id:
            raise ValueError("invalid breadth state")
        return value, paths

    @staticmethod
    def _staged(window: dict) -> list[dict]:
        rows = list(window.get("execution_order") or [])
        return [dict(row) for row in rows[1:3]]

    @staticmethod
    def _validate_kinds(kinds: list[str] | None) -> list[str]:
        values = list(kinds or PREP_KINDS)
        clean = []
        for value in values:
            value = str(value).upper()
            if value not in PREP_KINDS:
                raise ValueError(f"unsupported prep kind: {value}")
            if value not in clean:
                clean.append(value)
        if not clean:
            raise ValueError("at least one prep kind is required")
        return clean

    def _commit(self, pipeline_id: str, expected_git_head: str, state: dict, files: dict[str, str], actor: str, message: str) -> dict:
        current = self.git.head()
        if current != expected_git_head:
            raise GitStateError(json.dumps({"status": "STALE_GIT_HEAD", "expected": expected_git_head, "current": current}, sort_keys=True))
        state["updated_at"] = _utcnow()
        state["revision"] = int(state.get("revision") or 0) + 1
        state["state_digest"] = _digest({k: v for k, v in state.items() if k != "state_digest"})
        paths = self._breadth_paths(pipeline_id)
        files = dict(files)
        files[paths["state"]] = json.dumps(state, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
        result = self.prompt_runtime._commit_files(current, files, actor, message)
        return {
            "git": result,
            "checkpoint_head": result["head"],
            "breadth_state_digest": state["state_digest"],
            "revision": state["revision"],
        }

    def plan(
        self,
        *,
        pipeline_id: str,
        expected_pipeline_state_digest: str,
        expected_git_head: str,
        kinds: list[str] | None = None,
        actor: str = "agent",
    ) -> dict:
        pipeline_state = self.pipeline.state(pipeline_id)
        if pipeline_state.get("state_digest") != expected_pipeline_state_digest:
            raise GitStateError("STALE_PIPELINE_STATE_FOR_BREADTH_PLAN")
        window = pipeline_state["window"]
        staged = self._staged(window)
        if len(staged) != 2:
            raise ValueError("breadth planning requires exactly Q2 and Q3 staged quests")
        kinds = self._validate_kinds(kinds)
        breadth, paths = self._read_breadth(pipeline_id)
        plans = dict(breadth.get("plans") or {})
        created = []
        for quest in staged:
            for kind in kinds:
                plan_id = _plan_id(pipeline_id, quest["quest_id"], kind, expected_pipeline_state_digest)
                packet = {
                    "artifact": "ATHENA.NEXT.QUEST.PREP.PACKET.2",
                    "plan_id": plan_id,
                    "pipeline_id": pipeline_id,
                    "pipeline_state_digest": expected_pipeline_state_digest,
                    "quest": _quest_snapshot(quest),
                    "quest_role": quest.get("role"),
                    "kind": kind,
                    "status": "PLANNED",
                    "instruction": _default_instruction(kind, quest),
                    "created_at": _utcnow(),
                    "authority": "PREPARATION_ONLY",
                    "execution_effect": "NONE",
                    "claim_effect": "NONE",
                    "promotion_effect": "NONE",
                    "laws": [
                        "PREP_PACKET != QUEST_EXECUTION",
                        "STAGED_QUEST != ACTIVE_FOCUS",
                        "PREP_RESULT != EVIDENCE_PROMOTION",
                        "PREP_RESULT_MAY_ENRICH_FUTURE_REHYDRATION_CONTEXT",
                    ],
                }
                packet["packet_digest"] = _packet_digest(packet)
                plans[plan_id] = packet
                created.append(packet)
        breadth["pipeline_state_digest"] = expected_pipeline_state_digest
        breadth["plans"] = plans
        breadth.setdefault("history", []).append({
            "event": "PREP_PLANNED",
            "at": _utcnow(),
            "pipeline_state_digest": expected_pipeline_state_digest,
            "plan_ids": [p["plan_id"] for p in created],
        })
        commit = self._commit(pipeline_id, expected_git_head, breadth, {}, actor, f"plan staged quest breadth {pipeline_id}")
        return {
            "status": "PLANNED",
            "pipeline_id": pipeline_id,
            "pipeline_state_digest": expected_pipeline_state_digest,
            "staged_quests": staged,
            "plans": created,
            "plan_count": len(created),
            "authority": "PREPARATION_ONLY",
            **commit,
        }

    def record(
        self,
        *,
        pipeline_id: str,
        plan_id: str,
        expected_pipeline_state_digest: str,
        expected_git_head: str,
        result: dict,
        actor: str = "agent",
    ) -> dict:
        pipeline_state = self.pipeline.state(pipeline_id)
        if pipeline_state.get("state_digest") != expected_pipeline_state_digest:
            raise GitStateError("STALE_PIPELINE_STATE_FOR_PREP_RESULT")
        breadth, paths = self._read_breadth(pipeline_id)
        plan = dict((breadth.get("plans") or {}).get(plan_id) or {})
        if not plan:
            raise ValueError("unknown prep plan")
        if plan.get("pipeline_state_digest") != expected_pipeline_state_digest:
            raise ValueError("prep plan belongs to a different pipeline state")
        active_ids = {row.get("quest_id") for row in pipeline_state["window"].get("execution_order") or []}
        if plan.get("quest", {}).get("quest_id") not in active_ids:
            raise ValueError("prep plan quest is no longer in the active rolling window")
        if not isinstance(result, dict) or result.get("observed") is not True:
            raise ValueError("prep result requires observed=true")
        status = str(result.get("status") or "").upper()
        if status not in {"OBSERVED", "HOLD"}:
            raise ValueError("prep result status must be OBSERVED or HOLD")
        summary = str(result.get("summary") or "").strip()
        if not summary:
            raise ValueError("prep result summary is required")
        packet = {
            "artifact": "ATHENA.NEXT.QUEST.PREP.RESULT.2",
            "plan_id": plan_id,
            "pipeline_id": pipeline_id,
            "pipeline_state_digest": expected_pipeline_state_digest,
            "quest": plan["quest"],
            "kind": plan["kind"],
            "status": status,
            "observed": True,
            "summary": summary,
            "findings": list(result.get("findings") or []),
            "evidence_refs": list(result.get("evidence_refs") or []),
            "artifact_refs": list(result.get("artifact_refs") or []),
            "blockers": list(result.get("blockers") or []),
            "recorded_at": _utcnow(),
            "authority": "CONTEXT_ONLY",
            "quest_completion": False,
            "focus_mutation": False,
            "promotion_authority": False,
        }
        packet["packet_digest"] = _packet_digest(packet)
        observations = dict(breadth.get("observations") or {})
        observations[plan_id] = packet
        breadth["observations"] = observations
        plans = dict(breadth.get("plans") or {})
        plans[plan_id] = {**plan, "status": status, "result_digest": packet["packet_digest"], "updated_at": _utcnow()}
        breadth["plans"] = plans
        breadth.setdefault("history", []).append({"event": "PREP_RESULT_RECORDED", "at": _utcnow(), "plan_id": plan_id, "result_digest": packet["packet_digest"]})
        result_path = f"{paths['packets']}/{plan_id}.json"
        commit = self._commit(
            pipeline_id,
            expected_git_head,
            breadth,
            {result_path: json.dumps(packet, indent=2, sort_keys=True, ensure_ascii=False) + "\n"},
            actor,
            f"record staged quest prep {plan_id}",
        )
        return {"status": status, "pipeline_id": pipeline_id, "plan_id": plan_id, "result": packet, "authority": "CONTEXT_ONLY", **commit}

    def context(self, *, pipeline_id: str, quest_id: str | None = None) -> dict:
        pipeline_state = self.pipeline.state(pipeline_id)
        breadth, _ = self._read_breadth(pipeline_id)
        focus = pipeline_state["window"].get("focus")
        target_id = quest_id or (focus or {}).get("quest_id")
        if not target_id:
            raise ValueError("no target quest")
        plans = [dict(p) for p in (breadth.get("plans") or {}).values() if p.get("quest", {}).get("quest_id") == target_id]
        observations = []
        for plan in plans:
            row = (breadth.get("observations") or {}).get(plan["plan_id"])
            if row:
                observations.append(dict(row))
        observations.sort(key=lambda x: (str(x.get("kind")), str(x.get("plan_id"))))
        context_digest = _digest({
            "pipeline_id": pipeline_id,
            "pipeline_state_digest": pipeline_state.get("state_digest"),
            "quest_id": target_id,
            "observations": [{k: v for k, v in row.items() if k != "recorded_at"} for row in observations],
        })
        return {
            "status": "AVAILABLE" if observations else "EMPTY",
            "pipeline_id": pipeline_id,
            "pipeline_state_digest": pipeline_state.get("state_digest"),
            "quest_id": target_id,
            "focus_quest_id": (focus or {}).get("quest_id"),
            "is_current_focus": target_id == (focus or {}).get("quest_id"),
            "observations": observations,
            "context_digest": context_digest,
            "authority": "CONTEXT_ONLY",
            "law": "PREP_CONTEXT_MAY_REDUCE_RECONSTRUCTION_COST_BUT_DOES_NOT_COMPLETE_OR_AUTHORIZE_THE_QUEST",
        }

    def verify(self, pipeline_id: str) -> dict:
        pipeline_state = self.pipeline.state(pipeline_id)
        breadth, _ = self._read_breadth(pipeline_id)
        failures = []
        if breadth.get("state_digest"):
            recomputed = _digest({k: v for k, v in breadth.items() if k != "state_digest"})
            if recomputed != breadth.get("state_digest"):
                failures.append("BREADTH_STATE_DIGEST")
        for plan_id, plan in (breadth.get("plans") or {}).items():
            if plan.get("plan_id") != plan_id:
                failures.append(f"PLAN_ID:{plan_id}")
            if plan.get("kind") not in PREP_KINDS:
                failures.append(f"PLAN_KIND:{plan_id}")
            if plan.get("status") not in PREP_STATES:
                failures.append(f"PLAN_STATUS:{plan_id}")
        for plan_id, row in (breadth.get("observations") or {}).items():
            if row.get("plan_id") != plan_id or row.get("observed") is not True:
                failures.append(f"OBSERVATION_ID:{plan_id}")
            if row.get("quest_completion") is not False or row.get("focus_mutation") is not False or row.get("promotion_authority") is not False:
                failures.append(f"AUTHORITY_BOUNDARY:{plan_id}")
        return {
            "status": "PASS" if not failures else "HOLD",
            "pipeline_id": pipeline_id,
            "pipeline_state_digest": pipeline_state.get("state_digest"),
            "breadth_state_digest": breadth.get("state_digest"),
            "failures": failures,
            "plan_count": len(breadth.get("plans") or {}),
            "observation_count": len(breadth.get("observations") or {}),
            "authority": "NONE",
        }


BREADTH_TOOLS = [
    {
        "name": "athena_next_pipeline_prepare_staged",
        "description": "Create bounded preparation packets for staged Q2/Q3 quests without executing, claiming, completing, or promoting them.",
        "inputSchema": {
            "type": "object",
            "required": ["pipeline_id", "expected_pipeline_state_digest", "expected_git_head"],
            "properties": {
                "pipeline_id": {"type": "string"},
                "expected_pipeline_state_digest": {"type": "string"},
                "expected_git_head": {"type": "string"},
                "kinds": {"type": "array", "items": {"type": "string", "enum": list(PREP_KINDS)}},
                "actor": {"type": "string"},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_next_pipeline_record_prep",
        "description": "Persist an observed PREP/SCOUT result for one staged quest. The result is context-only and cannot complete or mutate the focus lane.",
        "inputSchema": {
            "type": "object",
            "required": ["pipeline_id", "plan_id", "expected_pipeline_state_digest", "expected_git_head", "result"],
            "properties": {
                "pipeline_id": {"type": "string"},
                "plan_id": {"type": "string"},
                "expected_pipeline_state_digest": {"type": "string"},
                "expected_git_head": {"type": "string"},
                "result": {"type": "object"},
                "actor": {"type": "string"},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_next_pipeline_prep_context",
        "description": "Read prep packets accumulated for a quest, defaulting to current Q1. This is rehydration context only.",
        "inputSchema": {"type": "object", "required": ["pipeline_id"], "properties": {"pipeline_id": {"type": "string"}, "quest_id": {"type": ["string", "null"]}}, "additionalProperties": False},
    },
    {
        "name": "athena_next_pipeline_verify_breadth",
        "description": "Verify staged preparation packet identity/digest and authority boundaries.",
        "inputSchema": {"type": "object", "required": ["pipeline_id"], "properties": {"pipeline_id": {"type": "string"}}, "additionalProperties": False},
    },
]
BREADTH_TOOL_NAMES = {tool["name"] for tool in BREADTH_TOOLS}


def install_next_pipeline_breadth(runtime_cls=PromptRuntime, tool_list=None, tool_names=None) -> None:
    if getattr(runtime_cls, "_athena_next_pipeline_breadth_v2_registered", False):
        return
    if tool_list is not None and tool_names is not None:
        for tool in BREADTH_TOOLS:
            if tool["name"] not in tool_names:
                tool_list.append(tool)
                tool_names.add(tool["name"])
    original_call = runtime_cls.call_tool

    def call_with_breadth(self, name, arguments):
        if name in BREADTH_TOOL_NAMES:
            pipeline = getattr(self, "_next_pipeline_runtime_v1", None)
            if pipeline is None:
                pipeline = RollingQuestPipelineRuntime(self.git, self)
                self._next_pipeline_runtime_v1 = pipeline
            runtime = getattr(self, "_next_pipeline_breadth_v2", None)
            if runtime is None:
                runtime = NextQuestBreadthRuntime(pipeline)
                self._next_pipeline_breadth_v2 = runtime
            if name == "athena_next_pipeline_prepare_staged":
                return runtime.plan(
                    pipeline_id=arguments["pipeline_id"],
                    expected_pipeline_state_digest=arguments["expected_pipeline_state_digest"],
                    expected_git_head=arguments["expected_git_head"],
                    kinds=arguments.get("kinds"),
                    actor=arguments.get("actor", "agent"),
                )
            if name == "athena_next_pipeline_record_prep":
                return runtime.record(
                    pipeline_id=arguments["pipeline_id"],
                    plan_id=arguments["plan_id"],
                    expected_pipeline_state_digest=arguments["expected_pipeline_state_digest"],
                    expected_git_head=arguments["expected_git_head"],
                    result=arguments["result"],
                    actor=arguments.get("actor", "agent"),
                )
            if name == "athena_next_pipeline_prep_context":
                return runtime.context(pipeline_id=arguments["pipeline_id"], quest_id=arguments.get("quest_id"))
            if name == "athena_next_pipeline_verify_breadth":
                return runtime.verify(arguments["pipeline_id"])
        return original_call(self, name, arguments)

    runtime_cls.call_tool = call_with_breadth
    runtime_cls._athena_next_pipeline_breadth_v2_registered = True


__all__ = ["VERSION", "PREP_KINDS", "NextQuestBreadthRuntime", "BREADTH_TOOLS", "BREADTH_TOOL_NAMES", "install_next_pipeline_breadth"]
