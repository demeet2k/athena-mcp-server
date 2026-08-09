from __future__ import annotations

import json
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .git_backend import GitBackend, GitStaleHead, GitStateError
from .prompt_runtime import PromptRuntime
from .rehydration_loop import _sha

VERSION = "ATHENA.NEXT.QUEST.PIPELINE.1"
ROOT = "prompts/next_quest_pipelines"
SUCCESSOR_ARTIFACT = "ATHENA.REHYDRATION.SUCCESSOR.BATON.V1"
ACTIVE = "ACTIVE"
RESEED_HOLD = "RESEED_HOLD"
COMPLETE = "COMPLETE"
ABORTED = "ABORTED"
TERMINAL = {COMPLETE, ABORTED}


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canon_task(value: Any) -> str:
    if isinstance(value, str):
        return " ".join(value.strip().split())
    if isinstance(value, dict):
        for key in ("task", "title", "description", "summary"):
            text = value.get(key)
            if isinstance(text, str) and text.strip():
                return " ".join(text.strip().split())
    return ""


def _task_key(task: str) -> str:
    return " ".join(task.lower().split())


def _state_digest(state: dict) -> str:
    return _sha({k: v for k, v in state.items() if k not in {"state_digest", "chain_digest"}})


def _event_digest(event: dict) -> str:
    return _sha({k: v for k, v in event.items() if k not in {"event_digest", "chain_digest"}})


def _valid_baton(baton: dict | None) -> bool:
    return bool(
        isinstance(baton, dict)
        and baton.get("artifact") == SUCCESSOR_ARTIFACT
        and isinstance(baton.get("baton_digest"), str)
        and baton["baton_digest"] == _sha({k: v for k, v in baton.items() if k != "baton_digest"})
    )


class RollingQuestPipelineRuntime:
    """A three-slot rolling focus window over explicit quest work.

    The pipeline is routing/persistence only. It does not execute quests in the
    background and it does not replace Rehydration Successor, Campaign, Message
    Board, Freshness Train, Promotion, or merge authority.
    """

    def __init__(self, git: GitBackend, prompt_runtime: PromptRuntime | None = None):
        self.git = git
        self.prompt_runtime = prompt_runtime or PromptRuntime(git)

    @property
    def available(self) -> bool:
        return bool(self.git.enabled and self.prompt_runtime.available)

    def _root(self) -> Path:
        if not self.git.enabled:
            raise GitStateError("ATHENA_GIT_ROOT is required for NEXT quest pipelines")
        return self.git.root

    def _safe_rel(self, rel: str) -> Path:
        return self.prompt_runtime._safe_rel(rel)

    @staticmethod
    def _base(pipeline_id: str) -> str:
        if not isinstance(pipeline_id, str) or not pipeline_id.startswith("NQP-"):
            raise ValueError("invalid pipeline_id")
        return f"{ROOT}/{pipeline_id}"

    def _paths(self, pipeline_id: str) -> dict[str, str]:
        base = self._base(pipeline_id)
        return {"base": base, "state": f"{base}/state.json", "events": f"{base}/events"}

    def _read_state(self, pipeline_id: str) -> tuple[dict, dict[str, str]]:
        paths = self._paths(pipeline_id)
        path = self._safe_rel(paths["state"])
        if not path.is_file():
            raise ValueError("pipeline not found")
        state = json.loads(path.read_text(encoding="utf-8"))
        if state.get("artifact") != VERSION or state.get("pipeline_id") != pipeline_id:
            raise ValueError("invalid pipeline state")
        return state, paths

    def _path_last_commit(self, rel: str) -> str | None:
        p = subprocess.run(
            ["git", "-C", str(self._root()), "log", "-n", "1", "--format=%H", "--", rel],
            text=True,
            capture_output=True,
        )
        if p.returncode:
            raise GitStateError(p.stderr.strip() or p.stdout.strip())
        return p.stdout.strip() or None

    def _is_ancestor(self, older: str, newer: str) -> bool:
        p = subprocess.run(
            ["git", "-C", str(self._root()), "merge-base", "--is-ancestor", older, newer],
            text=True,
            capture_output=True,
        )
        if p.returncode not in (0, 1):
            raise GitStateError(p.stderr.strip() or p.stdout.strip())
        return p.returncode == 0

    @staticmethod
    def _quest(task: str, ordinal: int, source: str, source_ref: str | None = None) -> dict:
        basis = {"task": task, "ordinal": ordinal, "source": source, "source_ref": source_ref}
        return {
            "quest_id": "Q-" + _sha(basis)[:16],
            "ordinal": int(ordinal),
            "task": task,
            "task_key": _task_key(task),
            "source": source,
            "source_ref": source_ref,
            "created_at": _utcnow(),
        }

    @staticmethod
    def _window(state: dict) -> dict:
        queue = list(state.get("queue") or [])
        execution = []
        for i, quest in enumerate(queue):
            row = dict(quest)
            row["role"] = "FOCUS_Q1" if i == 0 else f"STAGED_Q{i+1}"
            execution.append(row)
        return {
            "execution_order": execution,
            "display_window": list(reversed(execution)),
            "focus": execution[0] if execution else None,
            "depth": len(execution),
            "reseed_hold": state.get("reseed_hold"),
        }

    @staticmethod
    def _assert_state(state: dict, expected_state_digest: str) -> None:
        if state.get("state_digest") != expected_state_digest or _state_digest(state) != state.get("state_digest"):
            raise GitStateError("STALE_OR_TAMPERED_NEXT_PIPELINE_STATE")
        if state.get("status") in TERMINAL:
            raise ValueError(f"pipeline is terminal: {state.get('status')}")

    @staticmethod
    def _active_keys(state: dict) -> set[str]:
        return {str(q.get("task_key") or "") for q in state.get("queue") or []}

    @staticmethod
    def _completed_keys(state: dict) -> set[str]:
        return {str(q.get("task_key") or "") for q in state.get("completed") or []}

    @classmethod
    def _candidate_rows(cls, baton: dict, state: dict) -> list[dict]:
        if not _valid_baton(baton):
            raise ValueError("invalid successor baton")
        status = str(baton.get("status") or "")
        if status == "SELECTED" and baton.get("selected"):
            rows = [dict(baton["selected"])]
            for row in baton.get("candidates") or []:
                if row.get("candidate_id") != baton["selected"].get("candidate_id"):
                    rows.append(dict(row))
            return rows
        if status == "AMBIGUOUS":
            return [dict(row) for row in baton.get("ties") or []]
        if status in {"NO_SUCCESSOR", "TERMINAL"}:
            return []
        raise ValueError("successor baton has unsupported status")

    @classmethod
    def _choose_reseed(
        cls,
        baton: dict,
        state: dict,
        reseed_candidate_id: str | None,
        allow_revisit: bool,
    ) -> tuple[dict | None, dict | None]:
        rows = cls._candidate_rows(baton, state)
        active = cls._active_keys(state)
        completed = cls._completed_keys(state)
        seen = active | (set() if allow_revisit else completed)

        def usable(row: dict) -> bool:
            task = _canon_task(row)
            return bool(task and _task_key(task) not in seen)

        if str(baton.get("status")) == "AMBIGUOUS":
            if reseed_candidate_id:
                matched = [r for r in rows if r.get("candidate_id") == reseed_candidate_id]
                if len(matched) != 1:
                    raise ValueError("reseed_candidate_id is not one of the preserved ties")
                if not usable(matched[0]):
                    raise ValueError("selected reseed candidate duplicates active/completed work")
                return matched[0], None
            usable_rows = [r for r in rows if usable(r)]
            if len(usable_rows) == 1:
                return usable_rows[0], None
            return None, {
                "status": "AMBIGUOUS",
                "candidate_ids": [r.get("candidate_id") for r in usable_rows],
                "candidates": usable_rows,
                "baton_digest": baton.get("baton_digest"),
                "law": "AMBIGUITY != HIDDEN_TIE_BREAK",
            }

        for row in rows:
            if usable(row):
                return row, None
        return None, {
            "status": "NO_NOVEL_RESEED",
            "candidate_ids": [],
            "candidates": [],
            "baton_digest": baton.get("baton_digest"),
            "law": "DUPLICATE_SUCCESSOR != AUTOMATIC_REVISIT",
        }

    def _commit_transition(
        self,
        *,
        state: dict,
        paths: dict[str, str],
        expected_checkpoint_head: str,
        actor: str,
        event_type: str,
        event_payload: dict,
    ) -> dict:
        checkpoint = self._path_last_commit(paths["state"])
        if checkpoint != expected_checkpoint_head:
            raise GitStaleHead(json.dumps({"status": "STALE_NEXT_PIPELINE_CHECKPOINT", "expected": expected_checkpoint_head, "current": checkpoint}, sort_keys=True))
        current = self.git.head()
        if not self._is_ancestor(expected_checkpoint_head, current):
            raise GitStaleHead("pipeline checkpoint is not an ancestor of current Git head")
        before = state.get("state_digest")
        previous_chain = state.get("chain_digest")
        state["logical_clock"] = int(state.get("logical_clock", 0)) + 1
        state["updated_at"] = _utcnow()
        state["previous_chain_digest"] = previous_chain
        state["state_digest"] = _state_digest(state)
        event = {
            "artifact": "ATHENA.NEXT.QUEST.PIPELINE.EVENT.1",
            "pipeline_id": state["pipeline_id"],
            "event_type": event_type,
            "sequence": state["logical_clock"],
            "actor": actor,
            "created_at": _utcnow(),
            "checkpoint_head": expected_checkpoint_head,
            "work_head": current,
            "before_state_digest": before,
            "after_state_digest": state["state_digest"],
            "previous_chain_digest": previous_chain,
            "payload": event_payload,
        }
        event["event_digest"] = _event_digest(event)
        state["chain_digest"] = _sha({"previous": previous_chain, "event_digest": event["event_digest"], "state_digest": state["state_digest"]})
        event["chain_digest"] = state["chain_digest"]
        seq = int(state["logical_clock"])
        files = {
            paths["state"]: json.dumps(state, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            f"{paths['events']}/{seq:04d}-{event_type.lower()}.json": json.dumps(event, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        }
        git_result = self.prompt_runtime._commit_files(current, files, actor, f"next pipeline {state['pipeline_id']} {event_type.lower()}")
        return {
            "status": state["status"],
            "pipeline_id": state["pipeline_id"],
            "state_digest": state["state_digest"],
            "chain_digest": state["chain_digest"],
            "checkpoint_head": git_result["head"],
            "logical_clock": state["logical_clock"],
            "window": self._window(state),
            "completed_count": len(state.get("completed") or []),
            "git": git_result,
            "authority": "ROUTING_ONLY",
        }

    def start(self, *, goal: str, quests: list[Any], expected_git_head: str, actor: str = "agent", max_completed: int = 256) -> dict:
        goal = _canon_task(goal)
        if not goal:
            raise ValueError("goal is required")
        tasks = [_canon_task(q) for q in quests]
        tasks = [q for q in tasks if q]
        if len(tasks) != 3:
            raise ValueError("rolling NEXT pipeline requires exactly three initial quests")
        if len({_task_key(q) for q in tasks}) != 3:
            raise ValueError("initial quests must be distinct")
        current = self.git.head()
        if current != expected_git_head:
            raise GitStaleHead(json.dumps({"status": "STALE_GIT_HEAD", "expected": expected_git_head, "current": current}, sort_keys=True))
        max_completed = int(max_completed)
        if not 3 <= max_completed <= 4096:
            raise ValueError("max_completed must be between 3 and 4096")
        pipeline_id = f"NQP-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}"
        paths = self._paths(pipeline_id)
        queue = [self._quest(task, i + 1, "INITIAL") for i, task in enumerate(tasks)]
        state = {
            "artifact": VERSION,
            "pipeline_id": pipeline_id,
            "status": ACTIVE,
            "goal": goal,
            "created_at": _utcnow(),
            "updated_at": _utcnow(),
            "base_head": current,
            "logical_clock": 0,
            "previous_chain_digest": None,
            "next_ordinal": 4,
            "max_completed": max_completed,
            "queue": queue,
            "completed": [],
            "reseed_hold": None,
            "laws": [
                "Q1_IS_SOLE_FOCUS",
                "Q2_Q3_ARE_STAGED_NOT_BACKGROUND_EXECUTION",
                "Q1_COMPLETE => Q2_FOCUS + Q3_STAGE + Q4_RESEED",
                "RESEED_USES_CANONICAL_SUCCESSOR_BATON",
                "AMBIGUITY != HIDDEN_TIE_BREAK",
                "PIPELINE_ROUTING != EXECUTION_AUTHORITY",
                "PIPELINE_ROUTING != PROMOTION_OR_MERGE_AUTHORITY",
            ],
        }
        state["state_digest"] = _state_digest(state)
        event = {
            "artifact": "ATHENA.NEXT.QUEST.PIPELINE.EVENT.1",
            "pipeline_id": pipeline_id,
            "event_type": "PIPELINE_STARTED",
            "sequence": 0,
            "actor": actor,
            "created_at": _utcnow(),
            "checkpoint_head": current,
            "work_head": current,
            "before_state_digest": None,
            "after_state_digest": state["state_digest"],
            "previous_chain_digest": None,
            "payload": {"initial_quest_ids": [q["quest_id"] for q in queue]},
        }
        event["event_digest"] = _event_digest(event)
        state["chain_digest"] = _sha({"previous": None, "event_digest": event["event_digest"], "state_digest": state["state_digest"]})
        event["chain_digest"] = state["chain_digest"]
        files = {
            paths["state"]: json.dumps(state, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            f"{paths['events']}/0000-pipeline_started.json": json.dumps(event, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        }
        git_result = self.prompt_runtime._commit_files(current, files, actor, f"start NEXT quest pipeline {pipeline_id}")
        return {"status": ACTIVE, "pipeline_id": pipeline_id, "state_digest": state["state_digest"], "chain_digest": state["chain_digest"], "checkpoint_head": git_result["head"], "window": self._window(state), "git": git_result, "authority": "ROUTING_ONLY"}

    def rotate(
        self,
        *,
        pipeline_id: str,
        expected_state_digest: str,
        expected_checkpoint_head: str,
        completed_quest_id: str,
        completion: dict,
        successor_baton: dict,
        reseed_candidate_id: str | None = None,
        allow_revisit: bool = False,
        actor: str = "agent",
    ) -> dict:
        state, paths = self._read_state(pipeline_id)
        self._assert_state(state, expected_state_digest)
        queue = list(state.get("queue") or [])
        if not queue:
            raise ValueError("pipeline has no focus quest")
        focus = queue[0]
        if focus.get("quest_id") != completed_quest_id:
            raise ValueError("only current Q1 focus may complete/rotate the pipeline")
        if not isinstance(completion, dict) or completion.get("observed") is not True:
            raise ValueError("rotation requires observed completion")
        status = str(completion.get("status") or "").upper()
        if status not in {"SUCCEEDED", "PARTIAL", "HELD", "FAILED", "NO_PROGRESS"}:
            raise ValueError("unsupported completion status")
        if not str(completion.get("summary") or "").strip():
            raise ValueError("completion summary is required")

        completed = dict(focus)
        completed.update({
            "completed_at": _utcnow(),
            "completion_status": status,
            "completion_summary": str(completion.get("summary")),
            "evidence_refs": list(completion.get("evidence_refs") or []),
        })
        state["completed"] = list(state.get("completed") or []) + [completed]
        state["queue"] = queue[1:]

        if len(state["completed"]) >= int(state["max_completed"]):
            state["status"] = COMPLETE
            state["reseed_hold"] = {"status": "MAX_COMPLETED_REACHED"}
        elif completion.get("terminal") is True and not state["queue"]:
            state["status"] = COMPLETE
            state["reseed_hold"] = None
        else:
            candidate, hold = self._choose_reseed(successor_baton, state, reseed_candidate_id, bool(allow_revisit))
            if candidate:
                task = _canon_task(candidate)
                quest = self._quest(task, int(state["next_ordinal"]), "SUCCESSOR_BATON", candidate.get("candidate_id"))
                state["next_ordinal"] = int(state["next_ordinal"]) + 1
                state["queue"].append(quest)
                state["reseed_hold"] = None
                state["status"] = ACTIVE
            else:
                state["reseed_hold"] = hold
                state["status"] = RESEED_HOLD

        if len(state["queue"]) > 3:
            raise AssertionError("rolling window exceeded three active quests")
        result = self._commit_transition(
            state=state,
            paths=paths,
            expected_checkpoint_head=expected_checkpoint_head,
            actor=actor,
            event_type="FOCUS_COMPLETED_ROTATED",
            event_payload={
                "completed_quest_id": completed_quest_id,
                "completion_status": status,
                "successor_baton_digest": successor_baton.get("baton_digest"),
                "reseed_candidate_id": reseed_candidate_id,
                "queue_ids": [q["quest_id"] for q in state["queue"]],
                "reseed_hold": state.get("reseed_hold"),
            },
        )
        result["completed_quest"] = completed
        return result

    def resolve_reseed(
        self,
        *,
        pipeline_id: str,
        expected_state_digest: str,
        expected_checkpoint_head: str,
        candidate_id: str,
        actor: str = "agent",
    ) -> dict:
        state, paths = self._read_state(pipeline_id)
        self._assert_state(state, expected_state_digest)
        hold = dict(state.get("reseed_hold") or {})
        if state.get("status") != RESEED_HOLD or hold.get("status") != "AMBIGUOUS":
            raise ValueError("pipeline does not have an ambiguous reseed hold")
        rows = [r for r in hold.get("candidates") or [] if r.get("candidate_id") == candidate_id]
        if len(rows) != 1:
            raise ValueError("candidate_id is not an ambiguous reseed candidate")
        task = _canon_task(rows[0])
        if not task or _task_key(task) in self._active_keys(state) or _task_key(task) in self._completed_keys(state):
            raise ValueError("reseed candidate is no longer novel")
        quest = self._quest(task, int(state["next_ordinal"]), "AMBIGUITY_RESOLVED", candidate_id)
        state["next_ordinal"] = int(state["next_ordinal"]) + 1
        state["queue"].append(quest)
        if len(state["queue"]) > 3:
            raise AssertionError("rolling window exceeded three active quests")
        state["reseed_hold"] = None
        state["status"] = ACTIVE
        return self._commit_transition(
            state=state,
            paths=paths,
            expected_checkpoint_head=expected_checkpoint_head,
            actor=actor,
            event_type="RESEED_RESOLVED",
            event_payload={"candidate_id": candidate_id, "quest_id": quest["quest_id"]},
        )

    def state(self, pipeline_id: str) -> dict:
        state, paths = self._read_state(pipeline_id)
        return {
            "status": state.get("status"),
            "pipeline_id": pipeline_id,
            "goal": state.get("goal"),
            "state_digest": state.get("state_digest"),
            "chain_digest": state.get("chain_digest"),
            "checkpoint_head": self._path_last_commit(paths["state"]),
            "logical_clock": state.get("logical_clock"),
            "window": self._window(state),
            "completed_count": len(state.get("completed") or []),
            "completed_tail": list(state.get("completed") or [])[-10:],
            "authority": "ROUTING_ONLY",
        }

    def verify(self, pipeline_id: str) -> dict:
        state, paths = self._read_state(pipeline_id)
        failures = []
        if _state_digest(state) != state.get("state_digest"):
            failures.append("STATE_DIGEST")
        queue = list(state.get("queue") or [])
        if len(queue) > 3:
            failures.append("WINDOW_WIDTH")
        keys = [q.get("task_key") for q in queue]
        if len(keys) != len(set(keys)):
            failures.append("ACTIVE_DUPLICATE")
        if state.get("status") == ACTIVE and len(queue) != 3:
            failures.append("ACTIVE_WINDOW_NOT_FULL")
        if state.get("status") == RESEED_HOLD and len(queue) not in {1, 2}:
            failures.append("RESEED_HOLD_WIDTH")
        if queue and self._window(state)["focus"]["quest_id"] != queue[0]["quest_id"]:
            failures.append("FOCUS_IDENTITY")
        return {
            "status": "PASS" if not failures else "HOLD",
            "pipeline_id": pipeline_id,
            "failures": failures,
            "state_digest": state.get("state_digest"),
            "checkpoint_head": self._path_last_commit(paths["state"]),
            "window": self._window(state),
            "laws": [
                "PASS != QUEST_SUCCESS_TRUTH",
                "PASS != EXECUTION_AUTHORITY",
                "PASS verifies rolling-window/state invariants only",
            ],
        }

    def call_tool(self, name: str, a: dict):
        if name == "athena_next_pipeline_start":
            return self.start(goal=a["goal"], quests=a["quests"], expected_git_head=a["expected_git_head"], actor=a.get("actor", "agent"), max_completed=a.get("max_completed", 256))
        if name == "athena_next_pipeline_rotate":
            return self.rotate(
                pipeline_id=a["pipeline_id"], expected_state_digest=a["expected_state_digest"], expected_checkpoint_head=a["expected_checkpoint_head"],
                completed_quest_id=a["completed_quest_id"], completion=a["completion"], successor_baton=a["successor_baton"],
                reseed_candidate_id=a.get("reseed_candidate_id"), allow_revisit=a.get("allow_revisit", False), actor=a.get("actor", "agent"),
            )
        if name == "athena_next_pipeline_resolve_reseed":
            return self.resolve_reseed(
                pipeline_id=a["pipeline_id"], expected_state_digest=a["expected_state_digest"], expected_checkpoint_head=a["expected_checkpoint_head"],
                candidate_id=a["candidate_id"], actor=a.get("actor", "agent"),
            )
        if name == "athena_next_pipeline_state":
            return self.state(a["pipeline_id"])
        if name == "athena_next_pipeline_verify":
            return self.verify(a["pipeline_id"])
        raise KeyError(name)


NEXT_PIPELINE_TOOLS = [
    {
        "name": "athena_next_pipeline_start",
        "description": "Start a persistent three-quest rolling NEXT pipeline. Q1 is the sole focus; Q2/Q3 are staged future quests and are not background execution.",
        "inputSchema": {"type": "object", "required": ["goal", "quests", "expected_git_head"], "properties": {"goal": {"type": "string"}, "quests": {"type": "array", "minItems": 3, "maxItems": 3, "items": {"type": ["string", "object"]}}, "expected_git_head": {"type": "string"}, "actor": {"type": "string"}, "max_completed": {"type": "integer", "minimum": 3, "maximum": 4096}}, "additionalProperties": False},
    },
    {
        "name": "athena_next_pipeline_rotate",
        "description": "Complete the current Q1, promote Q2 to focus, promote Q3 to staged Q2, and reseed Q4 from the canonical Rehydration Successor baton. Ambiguous batons are preserved as a reseed hold.",
        "inputSchema": {"type": "object", "required": ["pipeline_id", "expected_state_digest", "expected_checkpoint_head", "completed_quest_id", "completion", "successor_baton"], "properties": {"pipeline_id": {"type": "string"}, "expected_state_digest": {"type": "string"}, "expected_checkpoint_head": {"type": "string"}, "completed_quest_id": {"type": "string"}, "completion": {"type": "object"}, "successor_baton": {"type": "object"}, "reseed_candidate_id": {"type": ["string", "null"]}, "allow_revisit": {"type": "boolean"}, "actor": {"type": "string"}}, "additionalProperties": False},
    },
    {
        "name": "athena_next_pipeline_resolve_reseed",
        "description": "Resolve a preserved ambiguous Q4 reseed by explicitly selecting one candidate; no hidden tie-break is performed.",
        "inputSchema": {"type": "object", "required": ["pipeline_id", "expected_state_digest", "expected_checkpoint_head", "candidate_id"], "properties": {"pipeline_id": {"type": "string"}, "expected_state_digest": {"type": "string"}, "expected_checkpoint_head": {"type": "string"}, "candidate_id": {"type": "string"}, "actor": {"type": "string"}}, "additionalProperties": False},
    },
    {
        "name": "athena_next_pipeline_state",
        "description": "Read the current rolling quest window in execution order and the requested reverse display order (Q3,Q2,Q1).",
        "inputSchema": {"type": "object", "required": ["pipeline_id"], "properties": {"pipeline_id": {"type": "string"}}, "additionalProperties": False},
    },
    {
        "name": "athena_next_pipeline_verify",
        "description": "Verify rolling-window width, focus identity, duplicate exclusion, and state digest invariants. PASS is orchestration integrity only, not quest truth.",
        "inputSchema": {"type": "object", "required": ["pipeline_id"], "properties": {"pipeline_id": {"type": "string"}}, "additionalProperties": False},
    },
]
NEXT_PIPELINE_TOOL_NAMES = {tool["name"] for tool in NEXT_PIPELINE_TOOLS}


def install_next_pipeline_extension(runtime_cls=PromptRuntime, tool_list=None, tool_names=None) -> None:
    if getattr(runtime_cls, "_athena_next_pipeline_v1_registered", False):
        return
    if tool_list is not None and tool_names is not None:
        for tool in NEXT_PIPELINE_TOOLS:
            if tool["name"] not in tool_names:
                tool_list.append(tool)
                tool_names.add(tool["name"])
    original_call = runtime_cls.call_tool

    def call_with_next_pipeline(self, name, arguments):
        if name in NEXT_PIPELINE_TOOL_NAMES:
            runtime = getattr(self, "_next_pipeline_runtime_v1", None)
            if runtime is None:
                runtime = RollingQuestPipelineRuntime(self.git, self)
                self._next_pipeline_runtime_v1 = runtime
            return runtime.call_tool(name, arguments)
        return original_call(self, name, arguments)

    runtime_cls.call_tool = call_with_next_pipeline
    runtime_cls._athena_next_pipeline_v1_registered = True


__all__ = [
    "VERSION",
    "RollingQuestPipelineRuntime",
    "NEXT_PIPELINE_TOOLS",
    "NEXT_PIPELINE_TOOL_NAMES",
    "install_next_pipeline_extension",
]
