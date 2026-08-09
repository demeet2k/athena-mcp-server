from __future__ import annotations

import json
from typing import Any

from .message_board import BOARD_ROOT, MessageBoardRuntime
from .rehydration_loop import RehydrationLoopRuntime, TERMINAL_STATES

ARTIFACT = "ATHENA.REHYDRATION.CONTROL.V1_1"
WORK_KEY_PREFIX = "rehydration:"


def _text(value: Any) -> str | None:
    if isinstance(value, str):
        value = " ".join(value.split())
        return value or None
    if isinstance(value, dict):
        for key in ("task", "objective", "summary", "value", "message", "code", "kind"):
            candidate = value.get(key)
            if isinstance(candidate, str) and candidate.strip():
                return " ".join(candidate.split())
    return None


class RehydrationControlRuntime:
    """V1.1 coordination and successor layer for the Git rehydration loop.

    Message Board remains the sole claim/lease authority. This layer only proves
    that the advancing agent currently owns the loop work lane, derives a bounded
    successor task, annotates the observed cycle with a local verification gate,
    and delegates causal persistence to RehydrationLoopRuntime.
    """

    def __init__(
        self,
        base: RehydrationLoopRuntime,
        board: MessageBoardRuntime | None = None,
    ):
        self.base = base
        self.git = base.git
        self.board = board or MessageBoardRuntime(self.git)

    @staticmethod
    def work_key(loop_id: str) -> str:
        return WORK_KEY_PREFIX + str(loop_id)

    def _loop(self, loop_id: str) -> tuple[dict, dict[str, str]]:
        state, paths = self.base._read_state(loop_id)
        if state.get("status") in TERMINAL_STATES:
            raise ValueError(f"rehydration loop is terminal: {state.get('status')}")
        return state, paths

    def claim(
        self,
        *,
        loop_id: str,
        agent_id: str,
        lease_seconds: int = 1800,
        remote: str = "origin",
        details: str | None = None,
    ) -> dict:
        state, paths = self._loop(loop_id)
        result = self.board.present(
            agent_id=agent_id,
            task=str(state.get("task") or state.get("goal") or loop_id),
            work_key=self.work_key(loop_id),
            targets=[paths["base"]],
            details=details or f"rehydration loop {loop_id} step {state.get('step_index')} state {state.get('state_digest')}",
            mode="PRIMARY",
            lease_seconds=lease_seconds,
            remote=remote,
        )
        return {
            **result,
            "artifact": ARTIFACT,
            "loop_id": loop_id,
            "step_index": state.get("step_index"),
            "loop_state_digest": state.get("state_digest"),
            "work_key": self.work_key(loop_id),
            "law": "MESSAGE_BOARD_IS_SOLE_CLAIM_AUTHORITY",
        }

    def _claim_snapshot(self, *, loop_id: str, agent_id: str, remote: str, shared_remote_mode: str) -> dict:
        snapshot = self.board.read(
            agent_id=agent_id,
            include_stale=True,
            remote=remote,
            shared_remote_mode=shared_remote_mode,
        )
        if snapshot.get("status") not in {"OK", "OK_UNVERIFIED"}:
            return {"ok": False, "status": snapshot.get("status"), "snapshot": snapshot}
        row = snapshot.get("self")
        if not isinstance(row, dict):
            return {"ok": False, "status": "REHYDRATION_CLAIM_REQUIRED_HOLD", "snapshot": snapshot}
        if self.board._lease_state(row) != "ACTIVE":
            return {"ok": False, "status": "REHYDRATION_CLAIM_STALE_HOLD", "snapshot": snapshot, "presence": row}
        if str(row.get("work_key") or "") != self.work_key(loop_id):
            return {"ok": False, "status": "REHYDRATION_WRONG_CLAIM_HOLD", "snapshot": snapshot, "presence": row}
        if str(row.get("mode")) != "PRIMARY":
            return {"ok": False, "status": "REHYDRATION_PRIMARY_CLAIM_REQUIRED_HOLD", "snapshot": snapshot, "presence": row}
        return {"ok": True, "status": "CLAIM_VERIFIED", "snapshot": snapshot, "presence": row}

    @staticmethod
    def _candidate(source: str, value: Any, order: int) -> dict | None:
        text = _text(value)
        if not text:
            return None
        return {"source": source, "task": text[:2000], "order": order, "digest_basis": value}

    def _successor(self, state: dict, completion: dict, frontier: dict) -> dict:
        explicit = _text(completion.get("next_task"))
        if explicit:
            return {
                "status": "EXPLICIT_SUCCESSOR",
                "task": explicit,
                "selected_source": "completion.next_task",
                "candidates": [{"source": "completion.next_task", "task": explicit, "order": 0}],
                "law": "EXPLICIT_SUCCESSOR != PROMOTION_AUTHORITY",
            }

        candidates: list[dict] = []
        order = 0
        for value in completion.get("residuals") or []:
            candidate = self._candidate("completion.residual", value, order)
            order += 1
            if candidate:
                candidates.append(candidate)
        selected = frontier.get("selected")
        candidate = self._candidate("frontier.selected", selected, order)
        order += 1
        if candidate:
            candidates.append(candidate)
        for value in frontier.get("residuals") or []:
            candidate = self._candidate("frontier.residual", value, order)
            order += 1
            if candidate:
                candidates.append(candidate)

        if candidates:
            chosen = sorted(candidates, key=lambda x: (x["order"], x["source"], x["task"]))[0]
            task = chosen["task"]
            source = chosen["source"]
            status = "DERIVED_SUCCESSOR"
        else:
            task = str(state.get("task") or state.get("goal") or "Continue the current bounded objective")
            source = "current.task"
            status = "FALLBACK_SUCCESSOR"
        return {
            "status": status,
            "task": task,
            "selected_source": source,
            "candidates": [{"source": x["source"], "task": x["task"], "order": x["order"]} for x in candidates],
            "law": "DERIVED_SUCCESSOR != PROMOTION_AUTHORITY",
        }

    @staticmethod
    def _cycle_gate(completion: dict, material_work_paths: list[str]) -> dict:
        status = str(completion.get("status") or "").upper()
        tests = completion.get("tests") or []
        evidence = [str(x) for x in (completion.get("evidence_refs") or []) if str(x).strip()]
        test_statuses = [str((row or {}).get("status") or "").upper() for row in tests if isinstance(row, dict)]
        all_tests_pass = bool(test_statuses) and all(x == "PASS" for x in test_statuses)
        if status in {"FAILED", "HELD", "NO_PROGRESS"} or completion.get("hard_hold"):
            gate = "HOLD_CYCLE"
        elif status == "SUCCEEDED" and material_work_paths and evidence and all_tests_pass:
            gate = "VERIFIED_CYCLE"
        elif status in {"SUCCEEDED", "PARTIAL"} and material_work_paths:
            gate = "WORK_COMMITTED"
        else:
            gate = "OBSERVED_CYCLE"
        return {
            "state": gate,
            "material_work_paths": material_work_paths,
            "evidence_count": len(evidence),
            "test_statuses": test_statuses,
            "all_tests_pass": all_tests_pass,
            "promotion_qualified": False,
            "authority": "LOCAL_CYCLE_ONLY",
            "law": "CYCLE_VERIFIED != PROMOTION_QUALIFIED != MERGE_AUTHORIZED",
        }

    def advance_claimed(
        self,
        *,
        loop_id: str,
        agent_id: str,
        expected_checkpoint_head: str,
        expected_state_digest: str,
        expected_prompt_digest: str,
        completion: dict,
        remote: str = "origin",
        shared_remote_mode: str = "REQUIRED",
        allow_no_git_change: bool = False,
    ) -> dict:
        state, paths = self._loop(loop_id)
        claim = self._claim_snapshot(
            loop_id=loop_id,
            agent_id=agent_id,
            remote=remote,
            shared_remote_mode=shared_remote_mode,
        )
        if not claim.get("ok"):
            return {
                "artifact": ARTIFACT,
                "status": claim.get("status"),
                "loop_id": loop_id,
                "claim": claim,
                "durable_return": False,
                "law": "NO_PRIMARY_MESSAGE_BOARD_CLAIM => NO_CONTROLLED_ADVANCE",
            }

        current_head = self.git.head()
        if not self.base._is_ancestor(expected_checkpoint_head, current_head):
            raise ValueError("current Git head is not a descendant of the loop checkpoint")
        changed_paths = self.base._changed_paths(expected_checkpoint_head, current_head)
        material = [
            path for path in changed_paths
            if not path.startswith(paths["base"] + "/")
            and not path.startswith(BOARD_ROOT + "/")
        ]
        if not material and not allow_no_git_change:
            raise ValueError("controlled advance requires substantive work outside loop and message-board control paths")

        frontier = self.base._frontier_snapshot(
            task=str(state.get("task") or state.get("goal") or ""),
            profile=state.get("profile"),
            source_ref=(state.get("source") or {}).get("source_ref") or "main",
            remote=remote,
            fetch=bool((state.get("source") or {}).get("fetch", True)),
            use_frontier=bool((state.get("source") or {}).get("use_frontier", True)),
        )
        successor = self._successor(state, completion, frontier)
        gate = self._cycle_gate(completion, material)
        enriched = dict(completion)
        enriched["next_task"] = successor["task"]
        enriched["_rehydration_control"] = {
            "artifact": ARTIFACT,
            "claim_id": (claim.get("presence") or {}).get("claim_id"),
            "agent_id": agent_id,
            "work_key": self.work_key(loop_id),
            "successor": successor,
            "cycle_gate": gate,
        }
        result = self.base.advance(
            loop_id=loop_id,
            expected_checkpoint_head=expected_checkpoint_head,
            expected_state_digest=expected_state_digest,
            expected_prompt_digest=expected_prompt_digest,
            completion=enriched,
            actor=agent_id,
            allow_no_git_change=allow_no_git_change,
            shared_remote_mode=shared_remote_mode,
            remote=remote,
        )
        return {
            **result,
            "artifact": ARTIFACT,
            "claim": {"status": "CLAIM_VERIFIED", "claim_id": (claim.get("presence") or {}).get("claim_id")},
            "successor": successor,
            "cycle_gate": gate,
        }

    def handoff(
        self,
        *,
        loop_id: str,
        agent_id: str,
        handoff_to: str,
        outcome: str | None = None,
        remote: str = "origin",
    ) -> dict:
        state, _ = self._loop(loop_id)
        result = self.board.release(
            agent_id=agent_id,
            release_status="HANDOFF",
            outcome=outcome or f"handoff rehydration loop {loop_id} step {state.get('step_index')}",
            handoff_to=handoff_to,
            remote=remote,
        )
        return {
            **result,
            "artifact": ARTIFACT,
            "loop_id": loop_id,
            "step_index": state.get("step_index"),
            "handoff_to": handoff_to,
            "next": "target agent reads board, claims the released rehydration work_key, then resumes the loop",
            "law": "HANDOFF_ROUTE != HANDOFF_CONSUMPTION",
        }

    def resume_controlled(
        self,
        *,
        loop_id: str,
        agent_id: str | None = None,
        remote: str = "origin",
        shared_remote_mode: str = "REQUIRED",
        include_prompt: bool = True,
    ) -> dict:
        loop = self.base.resume(loop_id, include_prompt=include_prompt)
        board = self.board.read(
            agent_id=agent_id,
            include_stale=True,
            remote=remote,
            shared_remote_mode=shared_remote_mode,
        )
        owners = [
            row for row in (board.get("active") or [])
            if str(row.get("work_key") or "") == self.work_key(loop_id)
        ]
        last = self.base._read_state(loop_id)[0].get("last_completion") or {}
        control = last.get("_rehydration_control") if isinstance(last, dict) else None
        return {
            "artifact": ARTIFACT,
            "status": loop.get("status") if board.get("status") in {"OK", "OK_UNVERIFIED"} else board.get("status"),
            "loop": loop,
            "coordination": {
                "work_key": self.work_key(loop_id),
                "active_owners": owners,
                "self": board.get("self"),
                "unread_messages": board.get("unread_messages") or [],
                "shared_frontier_verified": board.get("shared_frontier_verified"),
            },
            "last_control": control,
            "laws": [
                "MESSAGE_BOARD_IS_SOLE_CLAIM_AUTHORITY",
                "SELF_PROMPT != CLAIM_AUTHORITY",
                "CYCLE_VERIFIED != PROMOTION_QUALIFIED",
            ],
        }

    def call_tool(self, name: str, a: dict):
        if name == "athena_rehydration_claim":
            return self.claim(
                loop_id=a["loop_id"], agent_id=a["agent_id"], lease_seconds=a.get("lease_seconds", 1800),
                remote=a.get("remote", "origin"), details=a.get("details"),
            )
        if name == "athena_rehydration_advance_claimed":
            return self.advance_claimed(
                loop_id=a["loop_id"], agent_id=a["agent_id"], expected_checkpoint_head=a["expected_checkpoint_head"],
                expected_state_digest=a["expected_state_digest"], expected_prompt_digest=a["expected_prompt_digest"],
                completion=a["completion"], remote=a.get("remote", "origin"),
                shared_remote_mode=a.get("shared_remote_mode", "REQUIRED"),
                allow_no_git_change=a.get("allow_no_git_change", False),
            )
        if name == "athena_rehydration_handoff":
            return self.handoff(
                loop_id=a["loop_id"], agent_id=a["agent_id"], handoff_to=a["handoff_to"],
                outcome=a.get("outcome"), remote=a.get("remote", "origin"),
            )
        if name == "athena_rehydration_resume_controlled":
            return self.resume_controlled(
                loop_id=a["loop_id"], agent_id=a.get("agent_id"), remote=a.get("remote", "origin"),
                shared_remote_mode=a.get("shared_remote_mode", "REQUIRED"), include_prompt=a.get("include_prompt", True),
            )
        raise KeyError(name)


CONTROL_TOOLS = [
    {
        "name": "athena_rehydration_claim",
        "description": "Claim one rehydration loop through Message Board V1, the sole shared coordination authority. Exact work_key is rehydration:<loop_id>; duplicate primary claims hold.",
        "inputSchema": {
            "type": "object", "required": ["loop_id", "agent_id"],
            "properties": {
                "loop_id": {"type": "string"}, "agent_id": {"type": "string"},
                "lease_seconds": {"type": "integer", "minimum": 60, "maximum": 86400},
                "remote": {"type": "string"}, "details": {"type": ["string", "null"]},
            }, "additionalProperties": False,
        },
    },
    {
        "name": "athena_rehydration_advance_claimed",
        "description": "Advance a rehydration loop only when the agent owns the active primary Message Board claim. Derives a bounded successor from explicit next_task, observed residuals, or the fresh frontier; annotates a local cycle verification gate; then delegates persistence to the V1 loop.",
        "inputSchema": {
            "type": "object",
            "required": ["loop_id", "agent_id", "expected_checkpoint_head", "expected_state_digest", "expected_prompt_digest", "completion"],
            "properties": {
                "loop_id": {"type": "string"}, "agent_id": {"type": "string"},
                "expected_checkpoint_head": {"type": "string"}, "expected_state_digest": {"type": "string"},
                "expected_prompt_digest": {"type": "string"}, "completion": {"type": "object"},
                "remote": {"type": "string"},
                "shared_remote_mode": {"type": "string", "enum": ["REQUIRED", "BEST_EFFORT", "DISABLED"]},
                "allow_no_git_change": {"type": "boolean"},
            }, "additionalProperties": False,
        },
    },
    {
        "name": "athena_rehydration_handoff",
        "description": "Release the current rehydration claim through Message Board with HANDOFF semantics and route the lane to another agent without marking the work complete.",
        "inputSchema": {
            "type": "object", "required": ["loop_id", "agent_id", "handoff_to"],
            "properties": {
                "loop_id": {"type": "string"}, "agent_id": {"type": "string"}, "handoff_to": {"type": "string"},
                "outcome": {"type": ["string", "null"]}, "remote": {"type": "string"},
            }, "additionalProperties": False,
        },
    },
    {
        "name": "athena_rehydration_resume_controlled",
        "description": "Resume a rehydration loop together with its Message Board ownership/handoff state and the prior cycle's successor/gate annotation.",
        "inputSchema": {
            "type": "object", "required": ["loop_id"],
            "properties": {
                "loop_id": {"type": "string"}, "agent_id": {"type": ["string", "null"]},
                "remote": {"type": "string"},
                "shared_remote_mode": {"type": "string", "enum": ["REQUIRED", "BEST_EFFORT", "DISABLED"]},
                "include_prompt": {"type": "boolean"},
            }, "additionalProperties": False,
        },
    },
]
CONTROL_TOOL_NAMES = {x["name"] for x in CONTROL_TOOLS}
