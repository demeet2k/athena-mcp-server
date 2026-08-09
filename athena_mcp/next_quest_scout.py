from __future__ import annotations

from typing import Any

from .message_board import MessageBoardRuntime
from .next_quest_pipeline import RollingQuestPipelineRuntime
from .next_quest_pipeline_breadth import NextQuestBreadthRuntime
from .prompt_runtime import PromptRuntime

VERSION = "ATHENA.NEXT.SCOUT.EXECUTION.3"
SCOUT_PREFIX = "next-prep"


def _work_key(pipeline_id: str, plan_id: str) -> str:
    return f"{SCOUT_PREFIX}:{pipeline_id}:{plan_id}"


def _target_path(pipeline_id: str, plan_id: str) -> str:
    return f"prompts/next_quest_pipelines/{pipeline_id}/breadth/packets/{plan_id}.json"


class NextQuestScoutRuntime:
    """Claim and return explicit staged-preparation work through Message Board.

    A scout owns one prep plan, never the parent quest. The runtime does not
    execute arbitrary scout code; it validates/shared-claims the prep unit and
    records an externally observed result through Breadth V2.
    """

    def __init__(
        self,
        pipeline: RollingQuestPipelineRuntime,
        breadth: NextQuestBreadthRuntime,
        board: MessageBoardRuntime | None = None,
    ):
        self.pipeline = pipeline
        self.breadth = breadth
        self.git = pipeline.git
        self.board = board or MessageBoardRuntime(self.git)

    def _plan(self, pipeline_id: str, plan_id: str, expected_pipeline_state_digest: str) -> tuple[dict, dict]:
        pipeline_state = self.pipeline.state(pipeline_id)
        if pipeline_state.get("state_digest") != expected_pipeline_state_digest:
            raise ValueError("STALE_PIPELINE_STATE_FOR_SCOUT")
        breadth, _ = self.breadth._read_breadth(pipeline_id)
        plan = dict((breadth.get("plans") or {}).get(plan_id) or {})
        if not plan:
            raise ValueError("unknown scout prep plan")
        if plan.get("pipeline_state_digest") != expected_pipeline_state_digest:
            raise ValueError("scout prep plan belongs to another pipeline state")
        rows = list(pipeline_state.get("window", {}).get("execution_order") or [])
        focus_id = (pipeline_state.get("window", {}).get("focus") or {}).get("quest_id")
        quest_id = (plan.get("quest") or {}).get("quest_id")
        active = {row.get("quest_id"): row for row in rows}
        if quest_id not in active:
            raise ValueError("scout prep quest is no longer in active rolling window")
        if quest_id == focus_id:
            raise ValueError("scout cannot claim the active Q1 focus quest")
        return pipeline_state, plan

    @staticmethod
    def _find_claim(snapshot: dict, agent_id: str, work_key: str) -> dict | None:
        for row in snapshot.get("active") or []:
            if row.get("agent_id") == agent_id and row.get("work_key") == work_key:
                return dict(row)
        return None

    def claim(
        self,
        *,
        pipeline_id: str,
        plan_id: str,
        expected_pipeline_state_digest: str,
        agent_id: str,
        lease_seconds: int = 1800,
        remote: str = "origin",
    ) -> dict:
        pipeline_state, plan = self._plan(pipeline_id, plan_id, expected_pipeline_state_digest)
        if (self.breadth._read_breadth(pipeline_id)[0].get("observations") or {}).get(plan_id):
            return {
                "status": "PREP_ALREADY_OBSERVED",
                "pipeline_id": pipeline_id,
                "plan_id": plan_id,
                "agent_id": agent_id,
                "authority": "NONE",
            }
        work_key = _work_key(pipeline_id, plan_id)
        task = f"SCOUT {plan.get('kind')}: {(plan.get('quest') or {}).get('task')}"
        details = f"prep_plan={plan_id}; packet_digest={plan.get('packet_digest')}; parent_quest={(plan.get('quest') or {}).get('quest_id')}"
        board_result = self.board.present(
            agent_id=agent_id,
            task=task,
            work_key=work_key,
            targets=[_target_path(pipeline_id, plan_id)],
            details=details,
            mode="PRIMARY",
            lease_seconds=lease_seconds,
            remote=remote,
        )
        status = board_result.get("status")
        if status not in {"PRESENT", "ALREADY_PRESENT"}:
            return {
                "status": "SCOUT_CLAIM_HOLD",
                "pipeline_id": pipeline_id,
                "plan_id": plan_id,
                "agent_id": agent_id,
                "message_board": board_result,
                "authority": "NONE",
            }
        presence = board_result.get("presence") or {}
        if presence.get("work_key") != work_key:
            return {
                "status": "SCOUT_CLAIM_IDENTITY_HOLD",
                "pipeline_id": pipeline_id,
                "plan_id": plan_id,
                "message_board": board_result,
                "authority": "NONE",
            }
        return {
            "status": "SCOUT_CLAIMED",
            "artifact": VERSION,
            "pipeline_id": pipeline_id,
            "pipeline_state_digest": expected_pipeline_state_digest,
            "plan_id": plan_id,
            "plan_digest": plan.get("packet_digest"),
            "quest": plan.get("quest"),
            "prep_kind": plan.get("kind"),
            "instruction": plan.get("instruction"),
            "agent_id": agent_id,
            "claim_id": presence.get("claim_id"),
            "work_key": work_key,
            "allowed_target": _target_path(pipeline_id, plan_id),
            "message_board": board_result,
            "authority": "PREPARATION_ONLY",
            "execution_scope": "EXTERNAL_EXPLICIT_SCOUT_WORK_ONLY",
            "laws": [
                "SCOUT_CLAIM != QUEST_CLAIM",
                "SCOUT_MAY_NOT_MUTATE_Q1",
                "SCOUT_MAY_NOT_COMPLETE_STAGED_QUEST",
                "SCOUT_RESULT != EVIDENCE_PROMOTION",
            ],
        }

    def status(
        self,
        *,
        pipeline_id: str,
        plan_id: str,
        agent_id: str,
        remote: str = "origin",
        shared_remote_mode: str = "REQUIRED",
    ) -> dict:
        snapshot = self.board.read(
            agent_id=agent_id,
            remote=remote,
            shared_remote_mode=shared_remote_mode,
        )
        work_key = _work_key(pipeline_id, plan_id)
        claim = self._find_claim(snapshot, agent_id, work_key)
        return {
            "status": "SCOUT_ACTIVE" if claim else "SCOUT_NOT_ACTIVE",
            "pipeline_id": pipeline_id,
            "plan_id": plan_id,
            "agent_id": agent_id,
            "work_key": work_key,
            "claim": claim,
            "shared_frontier_verified": snapshot.get("shared_frontier_verified"),
            "message_board_status": snapshot.get("status"),
            "authority": "OBSERVATION_ONLY",
        }

    def return_result(
        self,
        *,
        pipeline_id: str,
        plan_id: str,
        expected_pipeline_state_digest: str,
        expected_git_head: str,
        agent_id: str,
        result: dict,
        remote: str = "origin",
        release_after_publish: bool = True,
    ) -> dict:
        pipeline_state, plan = self._plan(pipeline_id, plan_id, expected_pipeline_state_digest)
        snapshot = self.board.read(agent_id=agent_id, remote=remote, shared_remote_mode="REQUIRED")
        if snapshot.get("status") != "OK" or not snapshot.get("shared_frontier_verified"):
            return {
                "status": "SCOUT_SHARED_FRONTIER_HOLD",
                "pipeline_id": pipeline_id,
                "plan_id": plan_id,
                "message_board": snapshot,
                "authority": "NONE",
            }
        work_key = _work_key(pipeline_id, plan_id)
        claim = self._find_claim(snapshot, agent_id, work_key)
        if not claim:
            return {
                "status": "SCOUT_CLAIM_REQUIRED_HOLD",
                "pipeline_id": pipeline_id,
                "plan_id": plan_id,
                "agent_id": agent_id,
                "work_key": work_key,
                "authority": "NONE",
            }
        if _target_path(pipeline_id, plan_id) not in set(claim.get("targets") or []):
            return {
                "status": "SCOUT_SCOPE_HOLD",
                "pipeline_id": pipeline_id,
                "plan_id": plan_id,
                "claim": claim,
                "authority": "NONE",
            }
        if self.git.head() != expected_git_head:
            return {
                "status": "STALE_GIT_HEAD_FOR_SCOUT_RETURN",
                "expected_git_head": expected_git_head,
                "current_git_head": self.git.head(),
                "claim_preserved": True,
                "authority": "NONE",
            }
        observed = dict(result or {})
        observed["observed"] = True
        if str(observed.get("status") or "").upper() not in {"OBSERVED", "HOLD"}:
            observed["status"] = "OBSERVED"
        record = self.breadth.record(
            pipeline_id=pipeline_id,
            plan_id=plan_id,
            expected_pipeline_state_digest=expected_pipeline_state_digest,
            expected_git_head=expected_git_head,
            result=observed,
            actor=agent_id,
        )
        record_head = record.get("checkpoint_head") or self.git.head()
        published = self.board.remote_sync.publish(record_head, remote)
        if not published.get("shared_frontier_verified"):
            return {
                "status": "SCOUT_RESULT_LOCAL_PUBLISH_HOLD",
                "pipeline_id": pipeline_id,
                "plan_id": plan_id,
                "agent_id": agent_id,
                "claim_preserved": True,
                "record": record,
                "remote_publish": published,
                "authority": "CONTEXT_ONLY",
            }
        release = None
        if release_after_publish:
            release = self.board.release(
                agent_id=agent_id,
                release_status="DONE" if observed["status"] == "OBSERVED" else "PAUSED",
                outcome=f"prep {plan_id}: {observed.get('summary')}",
                remote=remote,
            )
        return {
            "status": "SCOUT_RETURNED" if release_after_publish else "SCOUT_RESULT_SHARED_CLAIM_ACTIVE",
            "artifact": VERSION,
            "pipeline_id": pipeline_id,
            "pipeline_state_digest": pipeline_state.get("state_digest"),
            "plan_id": plan_id,
            "plan_digest": plan.get("packet_digest"),
            "agent_id": agent_id,
            "claim_id": claim.get("claim_id"),
            "record": record,
            "remote_publish": published,
            "release": release,
            "authority": "CONTEXT_ONLY",
            "quest_completion": False,
            "focus_mutation": False,
            "promotion_authority": False,
            "laws": [
                "RESULT_PERSISTED_BEFORE_SCOUT_RELEASE",
                "SCOUT_RETURN != STAGED_QUEST_COMPLETION",
                "SCOUT_RETURN != Q1_MUTATION",
                "SCOUT_RETURN != PROMOTION_AUTHORITY",
            ],
        }

    def release(
        self,
        *,
        pipeline_id: str,
        plan_id: str,
        agent_id: str,
        release_status: str = "PAUSED",
        outcome: str | None = None,
        remote: str = "origin",
    ) -> dict:
        snapshot = self.board.read(agent_id=agent_id, remote=remote, shared_remote_mode="REQUIRED")
        claim = self._find_claim(snapshot, agent_id, _work_key(pipeline_id, plan_id))
        if not claim:
            return {
                "status": "SCOUT_NOT_ACTIVE",
                "pipeline_id": pipeline_id,
                "plan_id": plan_id,
                "agent_id": agent_id,
                "authority": "NONE",
            }
        result = self.board.release(
            agent_id=agent_id,
            release_status=release_status,
            outcome=outcome,
            remote=remote,
        )
        return {
            "status": "SCOUT_RELEASED" if result.get("status") == "RELEASED" else "SCOUT_RELEASE_HOLD",
            "pipeline_id": pipeline_id,
            "plan_id": plan_id,
            "agent_id": agent_id,
            "message_board": result,
            "authority": "NONE",
        }


SCOUT_TOOLS = [
    {
        "name": "athena_next_scout_claim",
        "description": "Claim exactly one staged PREP plan through Message Board. The claim is preparation-only and never claims or completes the parent quest.",
        "inputSchema": {
            "type": "object",
            "required": ["pipeline_id", "plan_id", "expected_pipeline_state_digest", "agent_id"],
            "properties": {
                "pipeline_id": {"type": "string"},
                "plan_id": {"type": "string"},
                "expected_pipeline_state_digest": {"type": "string"},
                "agent_id": {"type": "string"},
                "lease_seconds": {"type": "integer", "minimum": 60, "maximum": 86400},
                "remote": {"type": "string"}
            },
            "additionalProperties": False
        }
    },
    {
        "name": "athena_next_scout_status",
        "description": "Read shared Message Board standing for one staged prep-plan scout claim.",
        "inputSchema": {
            "type": "object",
            "required": ["pipeline_id", "plan_id", "agent_id"],
            "properties": {
                "pipeline_id": {"type": "string"}, "plan_id": {"type": "string"}, "agent_id": {"type": "string"},
                "remote": {"type": "string"}, "shared_remote_mode": {"type": "string", "enum": ["REQUIRED", "BEST_EFFORT", "DISABLED"]}
            },
            "additionalProperties": False
        }
    },
    {
        "name": "athena_next_scout_return",
        "description": "Verify an active exact scout claim, persist one observed prep result, publish it to shared Git, then optionally release the Message Board claim. The parent quest remains incomplete.",
        "inputSchema": {
            "type": "object",
            "required": ["pipeline_id", "plan_id", "expected_pipeline_state_digest", "expected_git_head", "agent_id", "result"],
            "properties": {
                "pipeline_id": {"type": "string"}, "plan_id": {"type": "string"}, "expected_pipeline_state_digest": {"type": "string"},
                "expected_git_head": {"type": "string"}, "agent_id": {"type": "string"}, "result": {"type": "object"},
                "remote": {"type": "string"}, "release_after_publish": {"type": "boolean"}
            },
            "additionalProperties": False
        }
    },
    {
        "name": "athena_next_scout_release",
        "description": "Explicitly release a staged prep-plan scout claim without claiming quest completion.",
        "inputSchema": {
            "type": "object",
            "required": ["pipeline_id", "plan_id", "agent_id"],
            "properties": {
                "pipeline_id": {"type": "string"}, "plan_id": {"type": "string"}, "agent_id": {"type": "string"},
                "release_status": {"type": "string", "enum": ["DONE", "PAUSED", "HANDOFF", "ABANDONED"]},
                "outcome": {"type": ["string", "null"]}, "remote": {"type": "string"}
            },
            "additionalProperties": False
        }
    }
]
SCOUT_TOOL_NAMES = {tool["name"] for tool in SCOUT_TOOLS}


def install_next_scout_extension(runtime_cls=PromptRuntime, tool_list=None, tool_names=None) -> None:
    if getattr(runtime_cls, "_athena_next_scout_v3_registered", False):
        return
    if tool_list is not None and tool_names is not None:
        for tool in SCOUT_TOOLS:
            if tool["name"] not in tool_names:
                tool_list.append(tool)
                tool_names.add(tool["name"])
    original_call = runtime_cls.call_tool

    def call_with_scout(self, name: str, arguments: dict):
        if name in SCOUT_TOOL_NAMES:
            pipeline = getattr(self, "_next_pipeline_runtime_v1", None)
            if pipeline is None:
                pipeline = RollingQuestPipelineRuntime(self.git, self)
                self._next_pipeline_runtime_v1 = pipeline
            breadth = getattr(self, "_next_pipeline_breadth_v2", None)
            if breadth is None:
                breadth = NextQuestBreadthRuntime(pipeline)
                self._next_pipeline_breadth_v2 = breadth
            board = getattr(self, "_message_board_runtime_v1", None)
            if board is None:
                board = MessageBoardRuntime(self.git)
                self._message_board_runtime_v1 = board
            scout = getattr(self, "_next_scout_runtime_v3", None)
            if scout is None:
                scout = NextQuestScoutRuntime(pipeline, breadth, board)
                self._next_scout_runtime_v3 = scout
            if name == "athena_next_scout_claim":
                return scout.claim(
                    pipeline_id=arguments["pipeline_id"], plan_id=arguments["plan_id"],
                    expected_pipeline_state_digest=arguments["expected_pipeline_state_digest"], agent_id=arguments["agent_id"],
                    lease_seconds=arguments.get("lease_seconds", 1800), remote=arguments.get("remote", "origin")
                )
            if name == "athena_next_scout_status":
                return scout.status(
                    pipeline_id=arguments["pipeline_id"], plan_id=arguments["plan_id"], agent_id=arguments["agent_id"],
                    remote=arguments.get("remote", "origin"), shared_remote_mode=arguments.get("shared_remote_mode", "REQUIRED")
                )
            if name == "athena_next_scout_return":
                return scout.return_result(
                    pipeline_id=arguments["pipeline_id"], plan_id=arguments["plan_id"],
                    expected_pipeline_state_digest=arguments["expected_pipeline_state_digest"], expected_git_head=arguments["expected_git_head"],
                    agent_id=arguments["agent_id"], result=arguments["result"], remote=arguments.get("remote", "origin"),
                    release_after_publish=arguments.get("release_after_publish", True)
                )
            if name == "athena_next_scout_release":
                return scout.release(
                    pipeline_id=arguments["pipeline_id"], plan_id=arguments["plan_id"], agent_id=arguments["agent_id"],
                    release_status=arguments.get("release_status", "PAUSED"), outcome=arguments.get("outcome"), remote=arguments.get("remote", "origin")
                )
        return original_call(self, name, arguments)

    runtime_cls.call_tool = call_with_scout
    runtime_cls._athena_next_scout_v3_registered = True


__all__ = ["VERSION", "NextQuestScoutRuntime", "SCOUT_TOOLS", "SCOUT_TOOL_NAMES", "install_next_scout_extension"]
