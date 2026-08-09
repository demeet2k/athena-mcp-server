from __future__ import annotations

import hashlib
import itertools
import json
from typing import Any

from .message_board import MessageBoardRuntime
from .next_quest_pipeline import RollingQuestPipelineRuntime
from .next_quest_pipeline_breadth import NextQuestBreadthRuntime, PREP_KINDS

VERSION = "ATHENA.NEXT.SCOUT.ALLOCATION.4"
TOOL_NAME = "athena_next_scout_allocate"
SCOUT_PREFIX = "next-prep"

KIND_VALUE = {
    "DEPENDENCY_MAP": 6,
    "TEST_DESIGN": 5,
    "RISK_SCAN": 4,
    "RETRIEVAL_PLAN": 3,
    "INTERFACE_MAP": 2,
    "SOURCE_REVIEW": 1,
}


def _digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _bounded_int(value: Any, field: str, lower: int, upper: int) -> int:
    try:
        out = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"invalid {field}") from exc
    if not lower <= out <= upper:
        raise ValueError(f"{field} must be between {lower} and {upper}")
    return out


def _work_key(pipeline_id: str, plan_id: str) -> str:
    return f"{SCOUT_PREFIX}:{pipeline_id}:{plan_id}"


def _extract_plan_id(pipeline_id: str, work_key: str | None) -> str | None:
    prefix = f"{SCOUT_PREFIX}:{pipeline_id}:"
    value = str(work_key or "")
    return value[len(prefix):] if value.startswith(prefix) and len(value) > len(prefix) else None


class NextScoutAllocationRuntime:
    """Read-only bounded allocation policy over staged prep plans.

    The allocator selects which prep-plan identities are worth claiming next. It
    creates no Message Board claim, performs no scout work, mutates no Git state,
    and grants no execution/evidence/promotion authority.
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

    @staticmethod
    def _role_map(pipeline_state: dict) -> dict[str, int]:
        rows = list((pipeline_state.get("window") or {}).get("execution_order") or [])
        return {str(row.get("quest_id")): index for index, row in enumerate(rows)}

    @staticmethod
    def _allocation_key(rows: list[dict], role_map: dict[str, int]) -> tuple[int, int, int, int]:
        if not rows:
            return (0, 0, 0, 0)
        quest_ids = {str((row.get("quest") or {}).get("quest_id")) for row in rows}
        staged_coverage = len(quest_ids)
        diversity = len({str(row.get("kind")) for row in rows})
        structural_value = 0
        near_count = 0
        for row in rows:
            quest_id = str((row.get("quest") or {}).get("quest_id"))
            position = role_map.get(quest_id, 99)
            proximity = 2 if position == 1 else 1 if position == 2 else 0
            near_count += 1 if position == 1 else 0
            structural_value += proximity * 10 + KIND_VALUE.get(str(row.get("kind")), 0)
        # Lexicographic policy: cover both staged quests where capacity permits,
        # then maximize structural readiness, then kind diversity, then nearness.
        return (staged_coverage, structural_value, diversity, near_count)

    def _board_snapshot(self, *, agent_id: str | None, remote: str, shared_remote_mode: str) -> dict:
        return self.board.read(
            agent_id=agent_id,
            limit=200,
            include_stale=False,
            remote=remote,
            shared_remote_mode=shared_remote_mode,
        )

    def allocate(
        self,
        *,
        pipeline_id: str,
        expected_pipeline_state_digest: str,
        max_scouts: int = 4,
        reserve_slots: int = 1,
        agent_id: str | None = None,
        remote: str = "origin",
        shared_remote_mode: str = "REQUIRED",
        choice_plan_ids: list[str] | None = None,
    ) -> dict:
        max_scouts = _bounded_int(max_scouts, "max_scouts", 1, 32)
        reserve_slots = _bounded_int(reserve_slots, "reserve_slots", 0, max_scouts - 1 if max_scouts > 1 else 0)
        pipeline_state = self.pipeline.state(pipeline_id)
        if pipeline_state.get("state_digest") != expected_pipeline_state_digest:
            raise ValueError("STALE_PIPELINE_STATE_FOR_SCOUT_ALLOCATION")
        if pipeline_state.get("status") != "ACTIVE":
            return {
                "artifact": VERSION,
                "status": "PIPELINE_NOT_ACTIVE_HOLD",
                "pipeline_id": pipeline_id,
                "pipeline_state_digest": pipeline_state.get("state_digest"),
                "authority": "ROUTING_ONLY",
            }

        role_map = self._role_map(pipeline_state)
        staged_ids = {quest_id for quest_id, pos in role_map.items() if pos in (1, 2)}
        breadth_state, _ = self.breadth._read_breadth(pipeline_id)
        plans = dict(breadth_state.get("plans") or {})
        observations = dict(breadth_state.get("observations") or {})

        board = self._board_snapshot(agent_id=agent_id, remote=remote, shared_remote_mode=shared_remote_mode)
        if str(shared_remote_mode).upper() == "REQUIRED" and not board.get("shared_frontier_verified"):
            return {
                "artifact": VERSION,
                "status": "SCOUT_ALLOCATION_SHARED_FRONTIER_HOLD",
                "pipeline_id": pipeline_id,
                "pipeline_state_digest": expected_pipeline_state_digest,
                "board": board,
                "authority": "ROUTING_ONLY",
            }

        active_plan_ids: list[str] = []
        active_rows: list[dict] = []
        for row in board.get("active") or []:
            plan_id = _extract_plan_id(pipeline_id, row.get("work_key"))
            if plan_id:
                active_plan_ids.append(plan_id)
                if plan_id in plans:
                    active_rows.append(dict(plans[plan_id]))
        active_plan_ids = sorted(set(active_plan_ids))

        usable_capacity = max(0, max_scouts - reserve_slots)
        available_new_slots = max(0, usable_capacity - len(active_plan_ids))
        candidates: list[dict] = []
        excluded: list[dict] = []
        for plan_id, plan_raw in sorted(plans.items()):
            plan = dict(plan_raw)
            quest_id = str((plan.get("quest") or {}).get("quest_id") or "")
            reason = None
            if plan.get("pipeline_state_digest") != expected_pipeline_state_digest:
                reason = "STALE_PLAN_STATE"
            elif quest_id not in staged_ids:
                reason = "NOT_STAGED_Q2_Q3"
            elif plan_id in observations:
                reason = "ALREADY_OBSERVED"
            elif plan_id in active_plan_ids:
                reason = "ALREADY_CLAIMED"
            elif plan.get("kind") not in PREP_KINDS:
                reason = "UNKNOWN_PREP_KIND"
            elif plan.get("status") not in {"PLANNED"}:
                reason = f"PLAN_STATUS_{plan.get('status')}"
            if reason:
                excluded.append({"plan_id": plan_id, "reason": reason})
            else:
                candidates.append(plan)

        take = min(available_new_slots, len(candidates))
        fixed = active_rows
        optimal_sets: list[list[dict]] = []
        best_key: tuple[int, int, int, int] | None = None
        if take > 0:
            for combo in itertools.combinations(candidates, take):
                combined = fixed + list(combo)
                key = self._allocation_key(combined, role_map)
                if best_key is None or key > best_key:
                    best_key = key
                    optimal_sets = [list(combo)]
                elif key == best_key:
                    optimal_sets.append(list(combo))
        else:
            best_key = self._allocation_key(fixed, role_map)
            optimal_sets = [[]]

        normalized_optima = [
            sorted(str(row.get("plan_id")) for row in combo)
            for combo in optimal_sets
        ]
        normalized_optima = sorted({tuple(rows) for rows in normalized_optima})
        normalized_optima_lists = [list(rows) for rows in normalized_optima]

        selected_ids: list[str] | None = None
        status = "SELECTED"
        if len(normalized_optima_lists) == 1:
            selected_ids = normalized_optima_lists[0]
        else:
            status = "AMBIGUOUS_ALLOCATION"
            if choice_plan_ids is not None:
                choice = sorted(set(str(x) for x in choice_plan_ids))
                if choice not in normalized_optima_lists:
                    raise ValueError("SCOUT_ALLOCATION_CHOICE_NOT_PARETO_OPTIMAL")
                selected_ids = choice
                status = "RESOLVED_ALLOCATION"

        selected_rows = [dict(plans[plan_id]) for plan_id in (selected_ids or [])]
        allocation_basis = {
            "artifact": VERSION,
            "pipeline_id": pipeline_id,
            "pipeline_state_digest": expected_pipeline_state_digest,
            "breadth_state_digest": breadth_state.get("state_digest"),
            "git_head": self.git.head(),
            "max_scouts": max_scouts,
            "reserve_slots": reserve_slots,
            "usable_capacity": usable_capacity,
            "active_plan_ids": active_plan_ids,
            "available_new_slots": available_new_slots,
            "candidate_plan_ids": [str(row.get("plan_id")) for row in candidates],
            "optimal_allocations": normalized_optima_lists,
            "selected_plan_ids": selected_ids,
            "policy": "BALANCED_STAGED_COVERAGE_THEN_STRUCTURAL_READINESS_V1",
            "policy_key": list(best_key or (0, 0, 0, 0)),
        }
        allocation_digest = _digest(allocation_basis)
        return {
            **allocation_basis,
            "status": status if candidates or active_plan_ids else "NO_SCOUT_WORK",
            "selected": selected_rows,
            "ambiguous_allocations": normalized_optima_lists if len(normalized_optima_lists) > 1 else [],
            "excluded": excluded,
            "board_status": board.get("status"),
            "shared_frontier_verified": bool(board.get("shared_frontier_verified")),
            "allocation_digest": allocation_digest,
            "authority": "ROUTING_ONLY",
            "claim_effect": "NONE",
            "execution_effect": "NONE",
            "promotion_effect": "NONE",
            "laws": [
                "ALLOCATION != CLAIM",
                "ALLOCATION != EXECUTION",
                "RESERVE_CAPACITY_IS_NOT_ALLOCATED",
                "ACTIVE_SCOUT_CLAIMS_CONSUME_CAPACITY",
                "AMBIGUOUS_OPTIMAL_ALLOCATION != HIDDEN_TIE_BREAK",
                "MESSAGE_BOARD_REMAINS_CLAIM_AUTHORITY",
            ],
        }

    def call_tool(self, name: str, a: dict) -> dict:
        if name != TOOL_NAME:
            raise KeyError(name)
        return self.allocate(
            pipeline_id=a["pipeline_id"],
            expected_pipeline_state_digest=a["expected_pipeline_state_digest"],
            max_scouts=a.get("max_scouts", 4),
            reserve_slots=a.get("reserve_slots", 1),
            agent_id=a.get("agent_id"),
            remote=a.get("remote", "origin"),
            shared_remote_mode=a.get("shared_remote_mode", "REQUIRED"),
            choice_plan_ids=a.get("choice_plan_ids"),
        )


NEXT_SCOUT_ALLOCATION_TOOLS = [{
    "name": TOOL_NAME,
    "description": "Read-only bounded scout allocation for rolling NEXT staged prep plans. Accounts for active Message Board scout claims and reserve capacity, excludes stale/observed/claimed plans, preserves equally optimal allocations instead of hidden tie-breaking, and never claims or executes work.",
    "inputSchema": {
        "type": "object",
        "required": ["pipeline_id", "expected_pipeline_state_digest"],
        "properties": {
            "pipeline_id": {"type": "string"},
            "expected_pipeline_state_digest": {"type": "string"},
            "max_scouts": {"type": "integer", "minimum": 1, "maximum": 32},
            "reserve_slots": {"type": "integer", "minimum": 0, "maximum": 31},
            "agent_id": {"type": ["string", "null"]},
            "remote": {"type": "string"},
            "shared_remote_mode": {"type": "string", "enum": ["REQUIRED", "BEST_EFFORT", "DISABLED"]},
            "choice_plan_ids": {"type": ["array", "null"], "items": {"type": "string"}},
        },
        "additionalProperties": False,
    },
}]
NEXT_SCOUT_ALLOCATION_TOOL_NAMES = {TOOL_NAME}


def install_next_scout_allocation_extension(prompt_runtime_cls, tool_list: list[dict], tool_names: set[str]) -> None:
    if getattr(prompt_runtime_cls, "_athena_next_scout_allocation_v4_registered", False):
        return
    from .next_quest_pipeline import RollingQuestPipelineRuntime
    from .next_quest_pipeline_breadth import NextQuestBreadthRuntime

    previous_call = prompt_runtime_cls.call_tool

    def call_with_allocation(self, name, arguments):
        if name in NEXT_SCOUT_ALLOCATION_TOOL_NAMES:
            runtime = getattr(self, "_next_scout_allocation_runtime_v4", None)
            if runtime is None:
                pipeline = getattr(self, "_next_pipeline_runtime_v1", None)
                if pipeline is None:
                    pipeline = RollingQuestPipelineRuntime(self.git, self)
                    self._next_pipeline_runtime_v1 = pipeline
                breadth = getattr(self, "_next_pipeline_breadth_runtime_v2", None)
                if breadth is None:
                    breadth = NextQuestBreadthRuntime(pipeline)
                    self._next_pipeline_breadth_runtime_v2 = breadth
                runtime = NextScoutAllocationRuntime(pipeline, breadth)
                self._next_scout_allocation_runtime_v4 = runtime
            return runtime.call_tool(name, arguments)
        return previous_call(self, name, arguments)

    prompt_runtime_cls.call_tool = call_with_allocation
    prompt_runtime_cls._athena_next_scout_allocation_v4_registered = True
    for tool in NEXT_SCOUT_ALLOCATION_TOOLS:
        if tool["name"] not in tool_names:
            tool_list.append(tool)
            tool_names.add(tool["name"])


__all__ = [
    "VERSION",
    "TOOL_NAME",
    "KIND_VALUE",
    "NextScoutAllocationRuntime",
    "NEXT_SCOUT_ALLOCATION_TOOLS",
    "NEXT_SCOUT_ALLOCATION_TOOL_NAMES",
    "install_next_scout_allocation_extension",
]
