from __future__ import annotations

import subprocess
from typing import Any

from .rehydration_loop import RehydrationLoopRuntime
from .rehydration_successor import SuccessorCompiler
from .next_quest_pipeline import (
    NEXT_PIPELINE_TOOLS,
    NEXT_PIPELINE_TOOL_NAMES,
    RESEED_HOLD,
    RollingQuestPipelineRuntime,
    _canon_task,
)

BRIDGE_TOOL = {
    "name": "athena_next_pipeline_advance_focus",
    "description": "Composite NEXT operation: derive far-end Q4 from the canonical successor compiler, force staged Q2 to become the next loop focus, advance the explicit rehydration loop, then rotate/reseed the rolling three-quest pipeline.",
    "inputSchema": {
        "type": "object",
        "required": [
            "pipeline_id", "pipeline_state_digest", "pipeline_checkpoint_head",
            "loop_id", "loop_state_digest", "loop_prompt_digest", "loop_checkpoint_head",
            "completed_quest_id", "completion"
        ],
        "properties": {
            "pipeline_id": {"type": "string"},
            "pipeline_state_digest": {"type": "string"},
            "pipeline_checkpoint_head": {"type": "string"},
            "loop_id": {"type": "string"},
            "loop_state_digest": {"type": "string"},
            "loop_prompt_digest": {"type": "string"},
            "loop_checkpoint_head": {"type": "string"},
            "completed_quest_id": {"type": "string"},
            "completion": {"type": "object"},
            "reseed_candidates": {"type": "array", "items": {"type": ["object", "string"]}},
            "reseed_policy": {"type": ["object", "null"]},
            "reseed_candidate_id": {"type": ["string", "null"]},
            "allow_revisit": {"type": "boolean"},
            "allow_no_git_change": {"type": "boolean"},
            "shared_remote_mode": {"type": "string", "enum": ["REQUIRED", "BEST_EFFORT", "DISABLED"]},
            "remote": {"type": "string"},
            "actor": {"type": "string"}
        },
        "additionalProperties": False
    }
}


class NextPipelineFocusBridge:
    def __init__(self, prompt_runtime):
        self.prompt_runtime = prompt_runtime
        self.git = prompt_runtime.git
        pipeline = getattr(prompt_runtime, "_next_pipeline_runtime_v1", None)
        if pipeline is None:
            pipeline = RollingQuestPipelineRuntime(self.git, prompt_runtime)
            prompt_runtime._next_pipeline_runtime_v1 = pipeline
        self.pipeline = pipeline
        loop = getattr(prompt_runtime, "_rehydration_loop_runtime_v1", None)
        if loop is None:
            loop = RehydrationLoopRuntime(self.git, prompt_runtime)
            prompt_runtime._rehydration_loop_runtime_v1 = loop
        self.loop = loop
        self.successor = SuccessorCompiler(loop)

    def _changed_paths(self, older: str, newer: str) -> list[str]:
        if older == newer:
            return []
        out = self.git._git("diff", "--name-only", f"{older}..{newer}")
        return sorted(line.strip() for line in out.splitlines() if line.strip())

    @staticmethod
    def _material_paths(paths: list[str], pipeline_id: str, loop_id: str) -> list[str]:
        control_prefixes = (
            f"prompts/next_quest_pipelines/{pipeline_id}/",
            f"prompts/rehydration/{loop_id}/",
            "prompts/message_board/",
        )
        return [path for path in paths if not path.startswith(control_prefixes)]

    def advance_focus(self, a: dict) -> dict:
        pipeline_state, _ = self.pipeline._read_state(a["pipeline_id"])
        self.pipeline._assert_state(pipeline_state, a["pipeline_state_digest"])
        if pipeline_state.get("status") == RESEED_HOLD:
            raise ValueError("resolve current pipeline reseed hold before completing another focus quest")
        queue = list(pipeline_state.get("queue") or [])
        if len(queue) != 3:
            raise ValueError("composite NEXT advance requires a full three-quest window")
        focus, staged_q2 = queue[0], queue[1]
        if focus.get("quest_id") != a["completed_quest_id"]:
            raise ValueError("completed_quest_id is not current Q1 focus")

        loop_state, _ = self.loop._read_state(a["loop_id"])
        if loop_state.get("state_digest") != a["loop_state_digest"]:
            raise ValueError("loop state digest mismatch")
        if _canon_task(loop_state.get("task")) != _canon_task(focus.get("task")):
            raise ValueError("loop current task and pipeline Q1 focus disagree")

        current_head = self.git.head()
        changed = self._changed_paths(a["loop_checkpoint_head"], current_head)
        material = self._material_paths(changed, a["pipeline_id"], a["loop_id"])
        completion = dict(a.get("completion") or {})
        status = str(completion.get("status") or "").upper()
        allow_no_git_change = bool(a.get("allow_no_git_change", False))
        if status in {"SUCCEEDED", "PARTIAL"} and not material and not allow_no_git_change:
            raise ValueError("composite NEXT advance requires substantive work outside orchestration bookkeeping namespaces")

        # Compile Q4 from observed residual/candidate evidence only. Q2 is staged
        # pipeline state and therefore deliberately omitted from this compiler input.
        reseed_completion = dict(completion)
        reseed_completion["next_task"] = None
        reseed_completion["terminal"] = False
        reseed_completion["self_steer"] = False
        baton = self.successor.compile(
            loop_id=a["loop_id"],
            expected_state_digest=a["loop_state_digest"],
            completion=reseed_completion,
            candidates=a.get("reseed_candidates") if a.get("reseed_candidates") is not None else reseed_completion.get("successor_candidates"),
            policy=a.get("reseed_policy") or reseed_completion.get("successor_policy"),
        )

        # Immediate focus is Q2 by pipeline law. Disable Rehydration Successor
        # auto-steering for this call so Q4 cannot steal Q2's position.
        loop_completion = dict(completion)
        loop_completion["terminal"] = False
        loop_completion["next_task"] = staged_q2["task"]
        loop_completion["self_steer"] = False
        loop_result = self.loop.advance(
            loop_id=a["loop_id"],
            expected_checkpoint_head=a["loop_checkpoint_head"],
            expected_state_digest=a["loop_state_digest"],
            expected_prompt_digest=a["loop_prompt_digest"],
            completion=loop_completion,
            actor=a.get("actor", "agent"),
            allow_no_git_change=allow_no_git_change,
            shared_remote_mode=a.get("shared_remote_mode", "REQUIRED"),
            remote=a.get("remote"),
        )

        pipeline_result = self.pipeline.rotate(
            pipeline_id=a["pipeline_id"],
            expected_state_digest=a["pipeline_state_digest"],
            expected_checkpoint_head=a["pipeline_checkpoint_head"],
            completed_quest_id=a["completed_quest_id"],
            completion=completion,
            successor_baton=baton,
            reseed_candidate_id=a.get("reseed_candidate_id"),
            allow_revisit=a.get("allow_revisit", False),
            actor=a.get("actor", "agent"),
        )
        return {
            "status": pipeline_result["status"],
            "pipeline": pipeline_result,
            "loop": loop_result,
            "reseed_baton": baton,
            "previous_focus": focus,
            "new_focus": pipeline_result["window"].get("focus"),
            "material_work_paths": material,
            "laws": [
                "Q1_COMPLETE => Q2_IS_NEXT_FOCUS",
                "Q4_RESEED != Q2_FOCUS",
                "RESEED_USES_CANONICAL_SUCCESSOR_COMPILER",
                "BOOKKEEPING_COMMIT != SUBSTANTIVE_QUEST_PROGRESS",
                "COMPOSITE_NEXT != BACKGROUND_EXECUTION",
                "COMPOSITE_NEXT != CLAIM_OR_PROMOTION_AUTHORITY",
            ],
        }


def install_next_pipeline_bridge(runtime_cls, tool_list=None, tool_names=None) -> None:
    if getattr(runtime_cls, "_athena_next_pipeline_bridge_v1_registered", False):
        return
    if BRIDGE_TOOL["name"] not in NEXT_PIPELINE_TOOL_NAMES:
        NEXT_PIPELINE_TOOLS.append(BRIDGE_TOOL)
        NEXT_PIPELINE_TOOL_NAMES.add(BRIDGE_TOOL["name"])
    if tool_list is not None and tool_names is not None and BRIDGE_TOOL["name"] not in tool_names:
        tool_list.append(BRIDGE_TOOL)
        tool_names.add(BRIDGE_TOOL["name"])
    original_call = runtime_cls.call_tool

    def call_with_bridge(self, name: str, arguments: dict):
        if name == BRIDGE_TOOL["name"]:
            bridge = getattr(self, "_next_pipeline_focus_bridge_v1", None)
            if bridge is None:
                bridge = NextPipelineFocusBridge(self)
                self._next_pipeline_focus_bridge_v1 = bridge
            return bridge.advance_focus(arguments)
        return original_call(self, name, arguments)

    runtime_cls.call_tool = call_with_bridge
    runtime_cls._athena_next_pipeline_bridge_v1_registered = True


__all__ = ["BRIDGE_TOOL", "NextPipelineFocusBridge", "install_next_pipeline_bridge"]
