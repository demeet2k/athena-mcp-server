from __future__ import annotations

import hashlib
import itertools
import json
from typing import Any

from .message_board import MessageBoardRuntime
from .next_quest_pipeline import RollingQuestPipelineRuntime
from .next_quest_pipeline_breadth import NextQuestBreadthRuntime, PREP_KINDS
from .next_scout_allocation import _extract_plan_id
from .next_scout_economy import RESOURCE_KEYS, VALUE_KEYS, RESOURCE_PROFILE
from .next_scout_metabolism import NextScoutMetabolismRuntime

VERSION = "ATHENA.NEXT.SCOUT.CALIBRATED.ECONOMY.6"
TOOL_NAME = "athena_next_scout_calibrated_economy"


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


def _sum_profiles(rows: list[dict], profiles: dict[str, dict]) -> dict[str, float]:
    out = {key: 0.0 for key in (*RESOURCE_KEYS, *VALUE_KEYS)}
    for row in rows:
        profile = profiles.get(str(row.get("kind")))
        if not profile:
            continue
        for key in out:
            out[key] += float(profile[key])
    return out


def _fits(cost: dict[str, float], available: dict[str, float]) -> bool:
    return all(cost[key] <= available[key] for key in RESOURCE_KEYS)


def _dominates(a: dict, b: dict) -> bool:
    benefits_ge = all(a[key] >= b[key] for key in VALUE_KEYS)
    costs_le = all(a[key] <= b[key] for key in RESOURCE_KEYS)
    strict = any(a[key] > b[key] for key in VALUE_KEYS) or any(a[key] < b[key] for key in RESOURCE_KEYS)
    return benefits_ge and costs_le and strict


class NextScoutCalibratedEconomyRuntime:
    """Read-only V5 economy evaluated with V6 calibrated cost priors."""

    def __init__(self, pipeline: RollingQuestPipelineRuntime, breadth: NextQuestBreadthRuntime,
                 metabolism: NextScoutMetabolismRuntime | None = None,
                 board: MessageBoardRuntime | None = None):
        self.pipeline = pipeline
        self.breadth = breadth
        self.metabolism = metabolism or NextScoutMetabolismRuntime(pipeline, breadth)
        self.git = pipeline.git
        self.board = board or MessageBoardRuntime(self.git)

    @staticmethod
    def _roles(state: dict) -> dict[str, int]:
        rows = list((state.get("window") or {}).get("execution_order") or [])
        return {str(row.get("quest_id")): idx for idx, row in enumerate(rows)}

    def economy(self, *, pipeline_id: str, expected_pipeline_state_digest: str,
                prior_strength: int = 3,
                max_scouts: int = 4, reserve_slots: int = 1,
                token_budget: int = 24000, reserve_tokens: int = 4000,
                minute_budget: int = 60, reserve_minutes: int = 10,
                tool_call_budget: int = 16, reserve_tool_calls: int = 2,
                coordination_budget: int = 10, reserve_coordination: int = 2,
                git_risk_budget: int = 8, reserve_git_risk: int = 1,
                agent_id: str | None = None, remote: str = "origin",
                shared_remote_mode: str = "REQUIRED",
                choice_plan_ids: list[str] | None = None) -> dict:
        max_scouts = _bounded_int(max_scouts, "max_scouts", 1, 32)
        reserve_slots = _bounded_int(reserve_slots, "reserve_slots", 0, max_scouts - 1 if max_scouts > 1 else 0)
        budgets = {
            "tokens": _bounded_int(token_budget, "token_budget", 1, 2_000_000),
            "minutes": _bounded_int(minute_budget, "minute_budget", 1, 10000),
            "tool_calls": _bounded_int(tool_call_budget, "tool_call_budget", 1, 10000),
            "coordination": _bounded_int(coordination_budget, "coordination_budget", 1, 10000),
            "git_risk": _bounded_int(git_risk_budget, "git_risk_budget", 1, 10000),
        }
        reserves = {
            "tokens": _bounded_int(reserve_tokens, "reserve_tokens", 0, budgets["tokens"]),
            "minutes": _bounded_int(reserve_minutes, "reserve_minutes", 0, budgets["minutes"]),
            "tool_calls": _bounded_int(reserve_tool_calls, "reserve_tool_calls", 0, budgets["tool_calls"]),
            "coordination": _bounded_int(reserve_coordination, "reserve_coordination", 0, budgets["coordination"]),
            "git_risk": _bounded_int(reserve_git_risk, "reserve_git_risk", 0, budgets["git_risk"]),
        }
        available_total = {k: float(budgets[k] - reserves[k]) for k in RESOURCE_KEYS}

        state = self.pipeline.state(pipeline_id)
        if state.get("state_digest") != expected_pipeline_state_digest:
            raise ValueError("STALE_PIPELINE_STATE_FOR_CALIBRATED_SCOUT_ECONOMY")
        if state.get("status") != "ACTIVE":
            return {"artifact": VERSION, "status": "PIPELINE_NOT_ACTIVE_HOLD", "authority": "ROUTING_ONLY"}

        calibration = self.metabolism.calibrate(pipeline_id=pipeline_id, prior_strength=prior_strength)
        profiles = calibration["calibrated_profiles"]
        for kind, profile in profiles.items():
            for key in VALUE_KEYS:
                profile[key] = RESOURCE_PROFILE[kind][key]

        roles = self._roles(state)
        staged = {qid for qid, pos in roles.items() if pos in (1, 2)}
        breadth, _ = self.breadth._read_breadth(pipeline_id)
        plans = dict(breadth.get("plans") or {})
        observations = dict(breadth.get("observations") or {})
        board = self.board.read(agent_id=agent_id, limit=200, include_stale=False, remote=remote,
                                shared_remote_mode=shared_remote_mode)
        if str(shared_remote_mode).upper() == "REQUIRED" and not board.get("shared_frontier_verified"):
            return {"artifact": VERSION, "status": "CALIBRATED_ECONOMY_SHARED_FRONTIER_HOLD",
                    "board": board, "authority": "ROUTING_ONLY"}

        active_ids: list[str] = []
        active_rows: list[dict] = []
        unknown_active: list[str] = []
        for row in board.get("active") or []:
            plan_id = _extract_plan_id(pipeline_id, row.get("work_key"))
            if not plan_id:
                continue
            active_ids.append(plan_id)
            if plan_id in plans and plans[plan_id].get("kind") in profiles:
                active_rows.append(dict(plans[plan_id]))
            else:
                unknown_active.append(plan_id)
        active_ids = sorted(set(active_ids))
        if unknown_active:
            return {"artifact": VERSION, "status": "UNKNOWN_ACTIVE_SCOUT_COST_HOLD",
                    "unknown_active_plan_ids": sorted(set(unknown_active)), "authority": "ROUTING_ONLY"}

        active_profile = _sum_profiles(active_rows, profiles)
        usable_slots = max(0, max_scouts - reserve_slots)
        if len(active_ids) > usable_slots:
            return {"artifact": VERSION, "status": "ACTIVE_SCOUTS_EXCEED_SLOT_BUDGET_HOLD",
                    "active_plan_ids": active_ids, "active_count": len(active_ids),
                    "usable_slots": usable_slots, "authority": "ROUTING_ONLY"}
        oversubscribed = [key for key in RESOURCE_KEYS if active_profile[key] > available_total[key]]
        if oversubscribed:
            return {"artifact": VERSION, "status": "ACTIVE_SCOUTS_EXCEED_RESOURCE_BUDGET_HOLD",
                    "active_plan_ids": active_ids, "active_profile": active_profile,
                    "available_total": available_total, "oversubscribed_resources": oversubscribed,
                    "calibration_digest": calibration["calibration_digest"], "authority": "ROUTING_ONLY"}

        available_after_active = {k: available_total[k] - active_profile[k] for k in RESOURCE_KEYS}
        new_slots = max(0, usable_slots - len(active_ids))
        candidates, excluded = [], []
        for plan_id, raw in sorted(plans.items()):
            plan = dict(raw)
            qid = str((plan.get("quest") or {}).get("quest_id") or "")
            reason = None
            if plan.get("pipeline_state_digest") != expected_pipeline_state_digest:
                reason = "STALE_PLAN_STATE"
            elif qid not in staged:
                reason = "NOT_STAGED_Q2_Q3"
            elif plan_id in observations:
                reason = "ALREADY_OBSERVED"
            elif plan_id in active_ids:
                reason = "ALREADY_CLAIMED"
            elif plan.get("kind") not in PREP_KINDS or plan.get("kind") not in profiles:
                reason = "UNKNOWN_CALIBRATED_PROFILE"
            elif plan.get("status") != "PLANNED":
                reason = f"PLAN_STATUS_{plan.get('status')}"
            if reason:
                excluded.append({"plan_id": plan_id, "reason": reason})
            else:
                candidates.append(plan)

        feasible: list[dict] = []
        max_take = min(new_slots, len(candidates))
        for size in range(0, max_take + 1):
            for combo in itertools.combinations(candidates, size):
                rows = list(combo)
                profile = _sum_profiles(rows, profiles)
                if not _fits(profile, available_after_active):
                    continue
                combined = active_rows + rows
                combined_profile = _sum_profiles(combined, profiles)
                quest_ids = {str((r.get("quest") or {}).get("quest_id")) for r in combined}
                kinds = {str(r.get("kind")) for r in combined}
                near = sum(1 for r in combined if roles.get(str((r.get("quest") or {}).get("quest_id"))) == 1)
                feasible.append({"plan_ids": sorted(str(r.get("plan_id")) for r in rows),
                                 "new_profile": profile, "combined_profile": combined_profile,
                                 "coverage": len(quest_ids), "diversity": len(kinds), "near_count": near})

        pareto = []
        for row in feasible:
            a = {**row["new_profile"], **{k: row["combined_profile"][k] for k in VALUE_KEYS}}
            if any(_dominates({**other["new_profile"], **{k: other["combined_profile"][k] for k in VALUE_KEYS}}, a)
                   for other in feasible if other is not row):
                continue
            pareto.append(row)

        def policy_key(row: dict) -> tuple:
            cp, np = row["combined_profile"], row["new_profile"]
            total_cost = sum(np[k] for k in ("minutes", "tool_calls", "coordination", "git_risk"))
            return (row["coverage"], cp["blocker_removal"], cp["reconstruction_reduction"], cp["information_gain"],
                    row["diversity"], row["near_count"], -total_cost, -np["tokens"])

        if pareto:
            best_key = max(policy_key(row) for row in pareto)
            optima = [row for row in pareto if policy_key(row) == best_key]
        else:
            best_key, optima = tuple(), []
        optimal_sets = [list(x) for x in sorted({tuple(row["plan_ids"]) for row in optima})]
        selected_ids = None
        status = "NO_SCOUT_WORK" if not candidates and not active_ids else "SELECTED"
        if optimal_sets:
            if len(optimal_sets) == 1:
                selected_ids = optimal_sets[0]
            else:
                status = "AMBIGUOUS_CALIBRATED_ALLOCATION"
                if choice_plan_ids is not None:
                    choice = sorted(set(str(x) for x in choice_plan_ids))
                    if choice not in optimal_sets:
                        raise ValueError("CALIBRATED_ECONOMY_CHOICE_NOT_OPTIMAL")
                    selected_ids = choice
                    status = "RESOLVED_CALIBRATED_ALLOCATION"
        if candidates and selected_ids == []:
            status = "BUDGET_HOLD_NO_FEASIBLE_NEW_WORK"

        selected_rows = [dict(plans[x]) for x in (selected_ids or [])]
        selected_profile = _sum_profiles(selected_rows, profiles)
        basis = {
            "artifact": VERSION, "pipeline_id": pipeline_id,
            "pipeline_state_digest": expected_pipeline_state_digest,
            "breadth_state_digest": breadth.get("state_digest"), "git_head": self.git.head(),
            "calibration_digest": calibration["calibration_digest"],
            "calibration_status": calibration["status"], "calibrated_profiles": profiles,
            "budgets": budgets, "reserves": reserves, "available_total": available_total,
            "active_plan_ids": active_ids, "active_profile": active_profile,
            "available_after_active": available_after_active, "max_scouts": max_scouts,
            "reserve_slots": reserve_slots, "usable_slots": usable_slots, "new_slots": new_slots,
            "candidate_plan_ids": [str(x.get("plan_id")) for x in candidates],
            "pareto_allocations": [row["plan_ids"] for row in pareto],
            "optimal_allocations": optimal_sets, "selected_plan_ids": selected_ids,
            "selected_profile": selected_profile,
            "policy": "CALIBRATED_COST_PARETO_THEN_V5_BALANCED_VALUE_V1", "policy_key": list(best_key),
        }
        return {**basis, "status": status, "selected": selected_rows, "excluded": excluded,
                "allocation_digest": _digest(basis),
                "cost_standing": "OBSERVED_RECEIPT_CALIBRATED_COST_PRIORS",
                "benefit_standing": "STATIC_V5_PRIORS_NOT_SELF_TRAINED",
                "authority": "ROUTING_ONLY", "claim_effect": "NONE", "execution_effect": "NONE",
                "promotion_effect": "NONE",
                "laws": ["PREDICTION != OBSERVATION",
                         "ONLY_OBSERVED_RECEIPTS_UPDATE_COST_PRIORS",
                         "COST_CALIBRATION != BENEFIT_CALIBRATION",
                         "CALIBRATED_ECONOMY != CLAIM_OR_EXECUTION",
                         "RESERVE_VECTOR_IS_NOT_SPENDABLE",
                         "MESSAGE_BOARD_REMAINS_CLAIM_AUTHORITY"]}

    def call_tool(self, name: str, a: dict) -> dict:
        if name != TOOL_NAME:
            raise KeyError(name)
        return self.economy(
            pipeline_id=a["pipeline_id"], expected_pipeline_state_digest=a["expected_pipeline_state_digest"],
            prior_strength=a.get("prior_strength", 3),
            max_scouts=a.get("max_scouts", 4), reserve_slots=a.get("reserve_slots", 1),
            token_budget=a.get("token_budget", 24000), reserve_tokens=a.get("reserve_tokens", 4000),
            minute_budget=a.get("minute_budget", 60), reserve_minutes=a.get("reserve_minutes", 10),
            tool_call_budget=a.get("tool_call_budget", 16), reserve_tool_calls=a.get("reserve_tool_calls", 2),
            coordination_budget=a.get("coordination_budget", 10), reserve_coordination=a.get("reserve_coordination", 2),
            git_risk_budget=a.get("git_risk_budget", 8), reserve_git_risk=a.get("reserve_git_risk", 1),
            agent_id=a.get("agent_id"), remote=a.get("remote", "origin"),
            shared_remote_mode=a.get("shared_remote_mode", "REQUIRED"), choice_plan_ids=a.get("choice_plan_ids"),
        )


NEXT_SCOUT_CALIBRATED_ECONOMY_TOOLS = [{
    "name": TOOL_NAME,
    "description": "Read-only V6 calibrated scout economy. Recomputes V5 protected-budget/Pareto allocation using cost priors calibrated from immutable observed scout receipts while keeping V5 benefit priors unchanged.",
    "inputSchema": {
        "type": "object", "required": ["pipeline_id", "expected_pipeline_state_digest"],
        "properties": {
            "pipeline_id": {"type": "string"}, "expected_pipeline_state_digest": {"type": "string"},
            "prior_strength": {"type": "integer", "minimum": 1, "maximum": 100},
            "max_scouts": {"type": "integer", "minimum": 1, "maximum": 32},
            "reserve_slots": {"type": "integer", "minimum": 0, "maximum": 31},
            "token_budget": {"type": "integer"}, "reserve_tokens": {"type": "integer"},
            "minute_budget": {"type": "integer"}, "reserve_minutes": {"type": "integer"},
            "tool_call_budget": {"type": "integer"}, "reserve_tool_calls": {"type": "integer"},
            "coordination_budget": {"type": "integer"}, "reserve_coordination": {"type": "integer"},
            "git_risk_budget": {"type": "integer"}, "reserve_git_risk": {"type": "integer"},
            "agent_id": {"type": ["string", "null"]}, "remote": {"type": "string"},
            "shared_remote_mode": {"type": "string", "enum": ["REQUIRED", "BEST_EFFORT", "DISABLED"]},
            "choice_plan_ids": {"type": ["array", "null"], "items": {"type": "string"}}
        }, "additionalProperties": False
    }
}]
NEXT_SCOUT_CALIBRATED_ECONOMY_TOOL_NAMES = {TOOL_NAME}


def install_next_scout_calibrated_economy_extension(prompt_runtime_cls, tool_list: list[dict], tool_names: set[str]) -> None:
    if getattr(prompt_runtime_cls, "_athena_next_scout_calibrated_economy_v6_registered", False):
        return
    previous_call = prompt_runtime_cls.call_tool
    def call_with_calibrated_economy(self, name, arguments):
        if name in NEXT_SCOUT_CALIBRATED_ECONOMY_TOOL_NAMES:
            runtime = getattr(self, "_next_scout_calibrated_economy_runtime_v6", None)
            if runtime is None:
                pipeline = getattr(self, "_next_pipeline_runtime_v1", None)
                if pipeline is None:
                    pipeline = RollingQuestPipelineRuntime(self.git, self)
                    self._next_pipeline_runtime_v1 = pipeline
                breadth = getattr(self, "_next_pipeline_breadth_runtime_v2", None)
                if breadth is None:
                    breadth = NextQuestBreadthRuntime(pipeline)
                    self._next_pipeline_breadth_runtime_v2 = breadth
                metabolism = getattr(self, "_next_scout_metabolism_runtime_v6", None)
                if metabolism is None:
                    metabolism = NextScoutMetabolismRuntime(pipeline, breadth)
                    self._next_scout_metabolism_runtime_v6 = metabolism
                runtime = NextScoutCalibratedEconomyRuntime(pipeline, breadth, metabolism)
                self._next_scout_calibrated_economy_runtime_v6 = runtime
            return runtime.call_tool(name, arguments)
        return previous_call(self, name, arguments)
    prompt_runtime_cls.call_tool = call_with_calibrated_economy
    prompt_runtime_cls._athena_next_scout_calibrated_economy_v6_registered = True
    for tool in NEXT_SCOUT_CALIBRATED_ECONOMY_TOOLS:
        if tool["name"] not in tool_names:
            tool_list.append(tool)
            tool_names.add(tool["name"])


__all__ = ["VERSION", "TOOL_NAME", "NextScoutCalibratedEconomyRuntime",
           "NEXT_SCOUT_CALIBRATED_ECONOMY_TOOLS", "NEXT_SCOUT_CALIBRATED_ECONOMY_TOOL_NAMES",
           "install_next_scout_calibrated_economy_extension"]
