from __future__ import annotations

from .message_board import BOARD_ROOT, MessageBoardRuntime
from .rehydration_loop import RehydrationLoopRuntime, TERMINAL_STATES

ARTIFACT = "ATHENA.REHYDRATION.CONTROL.V1_1"
WORK_KEY_PREFIX = "rehydration:"


class RehydrationControlRuntime:
    """Coordination membrane for the canonical rehydration stack.

    Existing owners remain authoritative:
      MessageBoardRuntime   -> claims, leases, collaboration, coordination handoff
      rehydration_successor -> WHAT NEXT routing and tie preservation
      rehydration_handoff   -> WHAT TO REHYDRATE delta compression
      RehydrationLoopRuntime-> causal prompt/receipt persistence and replay

    This layer adds only the missing conjunction: an advancing agent must own the
    current primary work lane, control-only Git writes are not substantive work,
    and each observed cycle receives a local verification gate that is explicitly
    below promotion/merge authority.
    """

    def __init__(self, base: RehydrationLoopRuntime, board: MessageBoardRuntime | None = None):
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
            details=details or f"rehydration {loop_id} step={state.get('step_index')} state={state.get('state_digest')}",
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
            "laws": [
                "MESSAGE_BOARD_IS_SOLE_CLAIM_AUTHORITY",
                "CLAIM != LOOP_COMPLETION",
            ],
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
            "laws": [
                "GIT_COMMIT != OBSERVED_SUCCESS",
                "CYCLE_VERIFIED != PROMOTION_QUALIFIED",
                "PROMOTION_QUALIFIED != MERGE_AUTHORIZED",
            ],
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
        _, paths = self._loop(loop_id)
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

        gate = self._cycle_gate(completion, material)
        enriched = dict(completion)
        enriched["_rehydration_control"] = {
            "artifact": ARTIFACT,
            "claim_id": (claim.get("presence") or {}).get("claim_id"),
            "agent_id": agent_id,
            "work_key": self.work_key(loop_id),
            "cycle_gate": gate,
            "delegation": {
                "successor": "canonical rehydration_successor extension on RehydrationLoopRuntime.advance",
                "handoff_delta": "canonical rehydration_handoff operator",
            },
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
        successor = ((result.get("successor_baton") or {}) if isinstance(result, dict) else {})
        if not successor:
            try:
                next_state = self.base._read_state(loop_id)[0]
                last = next_state.get("last_completion") or {}
                successor = last.get("successor_baton") or {}
            except Exception:
                successor = {}
        return {
            **result,
            "artifact": ARTIFACT,
            "claim": {"status": "CLAIM_VERIFIED", "claim_id": (claim.get("presence") or {}).get("claim_id")},
            "cycle_gate": gate,
            "routing_successor": successor or None,
            "laws": [
                "MESSAGE_BOARD_IS_SOLE_CLAIM_AUTHORITY",
                "WHAT_NEXT_OWNED_BY_REHYDRATION_SUCCESSOR",
                "WHAT_TO_REHYDRATE_OWNED_BY_REHYDRATION_HANDOFF",
                "CYCLE_VERIFIED != PROMOTION_QUALIFIED != MERGE_AUTHORIZED",
            ],
        }

    def claim_handoff(
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
            outcome=outcome or f"coordination handoff for rehydration {loop_id} step {state.get('step_index')}",
            handoff_to=handoff_to,
            remote=remote,
        )
        return {
            **result,
            "artifact": ARTIFACT,
            "loop_id": loop_id,
            "step_index": state.get("step_index"),
            "handoff_to": handoff_to,
            "next": "target reads Message Board, claims rehydration:<loop_id>, then consumes the canonical rehydration handoff delta or resumes normally",
            "laws": [
                "CLAIM_HANDOFF != REHYDRATION_HANDOFF_DELTA",
                "HANDOFF_ROUTE != HANDOFF_CONSUMPTION",
            ],
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
        loop = self.base.resume(
            loop_id,
            include_prompt=include_prompt,
            shared_remote_mode=shared_remote_mode,
            remote=remote,
        )
        board = self.board.read(
            agent_id=agent_id,
            include_stale=True,
            remote=remote,
            shared_remote_mode=shared_remote_mode,
        )
        owners = [row for row in (board.get("active") or []) if str(row.get("work_key") or "") == self.work_key(loop_id)]
        last = self.base._read_state(loop_id)[0].get("last_completion") or {}
        control = last.get("_rehydration_control") if isinstance(last, dict) else None
        successor = last.get("successor_baton") if isinstance(last, dict) else None
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
            "routing_successor": successor,
            "next": "use athena_rehydration_handoff_delta/resume for compressed cross-agent rehydration state",
            "laws": [
                "MESSAGE_BOARD_IS_SOLE_CLAIM_AUTHORITY",
                "SELF_PROMPT != CLAIM_AUTHORITY",
                "ROUTING_SUCCESSOR != HANDOFF_DELTA",
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
                shared_remote_mode=a.get("shared_remote_mode", "REQUIRED"), allow_no_git_change=a.get("allow_no_git_change", False),
            )
        if name == "athena_rehydration_claim_handoff":
            return self.claim_handoff(
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
        "description": "Claim a rehydration:<loop_id> lane through Message Board V1, the sole coordination authority. Duplicate primary work holds rather than creating a second lease plane.",
        "inputSchema": {"type": "object", "required": ["loop_id", "agent_id"], "properties": {
            "loop_id": {"type": "string"}, "agent_id": {"type": "string"},
            "lease_seconds": {"type": "integer", "minimum": 60, "maximum": 86400},
            "remote": {"type": "string"}, "details": {"type": ["string", "null"]}
        }, "additionalProperties": False},
    },
    {
        "name": "athena_rehydration_advance_claimed",
        "description": "Advance only when the caller owns the active PRIMARY Message Board claim. Reject control-only Git changes as work, attach a local cycle verification gate, then delegate successor routing and causal persistence to the canonical rehydration runtime.",
        "inputSchema": {"type": "object", "required": ["loop_id", "agent_id", "expected_checkpoint_head", "expected_state_digest", "expected_prompt_digest", "completion"], "properties": {
            "loop_id": {"type": "string"}, "agent_id": {"type": "string"},
            "expected_checkpoint_head": {"type": "string"}, "expected_state_digest": {"type": "string"},
            "expected_prompt_digest": {"type": "string"}, "completion": {"type": "object"},
            "remote": {"type": "string"}, "shared_remote_mode": {"type": "string", "enum": ["REQUIRED", "BEST_EFFORT", "DISABLED"]},
            "allow_no_git_change": {"type": "boolean"}
        }, "additionalProperties": False},
    },
    {
        "name": "athena_rehydration_claim_handoff",
        "description": "Transfer only the Message Board work claim with HANDOFF semantics. The canonical rehydration_handoff tools remain responsible for what state/prompt delta the next agent must consume.",
        "inputSchema": {"type": "object", "required": ["loop_id", "agent_id", "handoff_to"], "properties": {
            "loop_id": {"type": "string"}, "agent_id": {"type": "string"}, "handoff_to": {"type": "string"},
            "outcome": {"type": ["string", "null"]}, "remote": {"type": "string"}
        }, "additionalProperties": False},
    },
    {
        "name": "athena_rehydration_resume_controlled",
        "description": "Resume the shared-current loop together with Message Board ownership and the receipt-bound canonical routing successor. Use rehydration_handoff_delta/resume for compressed handoff state.",
        "inputSchema": {"type": "object", "required": ["loop_id"], "properties": {
            "loop_id": {"type": "string"}, "agent_id": {"type": ["string", "null"]}, "remote": {"type": "string"},
            "shared_remote_mode": {"type": "string", "enum": ["REQUIRED", "BEST_EFFORT", "DISABLED"]}, "include_prompt": {"type": "boolean"}
        }, "additionalProperties": False},
    },
]
CONTROL_TOOL_NAMES = {x["name"] for x in CONTROL_TOOLS}
