from __future__ import annotations

import copy
import hashlib
import itertools
import json
import statistics
from datetime import datetime, timezone
from typing import Any

from .next_scout_causal_promotion import NextScoutCausalPromotionRuntime
from .next_scout_calibrated_economy import NextScoutCalibratedEconomyRuntime
from .next_scout_economy import RESOURCE_KEYS, VALUE_KEYS, RESOURCE_PROFILE

VERSION = "ATHENA.NEXT.SCOUT.BENEFIT.CANARY.10"
PLAN_ARTIFACT = "ATHENA.NEXT.SCOUT.BENEFIT.CANARY.PLAN.10"
DECISION_ARTIFACT = "ATHENA.NEXT.SCOUT.BENEFIT.CANARY.DECISION.10"
TOOLS = {
    "start": "athena_next_scout_canary_start",
    "preview": "athena_next_scout_canary_preview",
    "apply": "athena_next_scout_canary_apply",
    "rollback": "athena_next_scout_canary_rollback",
    "state": "athena_next_scout_canary_state",
}


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _benefit_table() -> dict[str, dict[str, float]]:
    return {
        kind: {key: float(RESOURCE_PROFILE[kind][key]) for key in VALUE_KEYS}
        for kind in sorted(RESOURCE_PROFILE)
    }


def _sum_profiles(rows: list[dict], profiles: dict[str, dict]) -> dict[str, float]:
    out = {key: 0.0 for key in (*RESOURCE_KEYS, *VALUE_KEYS)}
    for row in rows:
        profile = profiles.get(str(row.get("kind")))
        if not profile:
            continue
        for key in out:
            out[key] += float(profile[key])
    return out


def _dominates(a: dict, b: dict) -> bool:
    benefits_ge = all(a[key] >= b[key] for key in VALUE_KEYS)
    costs_le = all(a[key] <= b[key] for key in RESOURCE_KEYS)
    strict = any(a[key] > b[key] for key in VALUE_KEYS) or any(a[key] < b[key] for key in RESOURCE_KEYS)
    return benefits_ge and costs_le and strict


class NextScoutBenefitCanaryRuntime:
    """V10 bounded application membrane for V9 benefit-prior promotion candidates.

    The canonical V5 benefit table is immutable. V10 creates a scoped canary lane
    over V6 calibrated costs, applies a small uniform benefit multiplier to exactly
    one V9-validated prep kind, compares control/canary recommendations, and may
    persist a routing decision. It never claims scout work or mutates the live
    canonical benefit table.
    """

    def __init__(self, v9: NextScoutCausalPromotionRuntime,
                 calibrated: NextScoutCalibratedEconomyRuntime):
        self.v9 = v9
        self.calibrated = calibrated
        self.git = v9.git
        self.prompt_runtime = v9.prompt_runtime
        self.pipeline = calibrated.pipeline
        self.breadth = calibrated.breadth

    @staticmethod
    def _root(pipeline_id: str) -> str:
        return f"prompts/next_quest_pipelines/{pipeline_id}/canary/v10"

    def _plan_path(self, pipeline_id: str, canary_id: str) -> str:
        return f"{self._root(pipeline_id)}/plans/{canary_id}.json"

    def _decision_path(self, pipeline_id: str, canary_id: str, ordinal: int) -> str:
        return f"{self._root(pipeline_id)}/decisions/{canary_id}-{ordinal:04d}.json"

    def _read_plan(self, pipeline_id: str, canary_id: str) -> dict:
        path = self.prompt_runtime._safe_rel(self._plan_path(pipeline_id, canary_id))
        if not path.is_file():
            raise ValueError("BENEFIT_CANARY_NOT_FOUND")
        row = json.loads(path.read_text(encoding="utf-8"))
        if row.get("artifact") != PLAN_ARTIFACT or row.get("pipeline_id") != pipeline_id:
            raise ValueError("INVALID_BENEFIT_CANARY_PLAN")
        if _digest({k: v for k, v in row.items() if k != "plan_digest"}) != row.get("plan_digest"):
            raise ValueError("BENEFIT_CANARY_PLAN_DIGEST_HOLD")
        return row

    @staticmethod
    def _validated_effect(evaluation: dict) -> tuple[list[str], float]:
        if evaluation.get("standing") != "BENEFIT_PRIOR_PROMOTION_CANDIDATE":
            raise ValueError("V10_REQUIRES_V9_PROMOTION_CANDIDATE")
        passing = list(evaluation.get("passing_metrics") or [])
        vals = []
        for metric in passing:
            row = (evaluation.get("metrics") or {}).get(metric) or {}
            validation = row.get("validation") or {}
            value = validation.get("median_delta")
            if value is not None and float(value) > 0:
                vals.append(float(value))
        if not vals:
            raise ValueError("V9_CANDIDATE_HAS_NO_POSITIVE_VALIDATION_EFFECT")
        return passing, max(0.0, min(1.0, float(statistics.median(vals))))

    def start(self, *, pipeline_id: str, cohort_id: str, expected_git_head: str,
              lambda_weight: float = 0.10, max_cycles: int = 6,
              max_changed_plan_ids: int = 2, actor: str = "agent",
              min_pairs: int = 3, min_sign_consistency: float = 2.0 / 3.0,
              min_effect: float = 0.05, min_validation_retention: float = 0.5) -> dict:
        current = self.git.head()
        if current != expected_git_head:
            raise ValueError("STALE_GIT_HEAD_FOR_BENEFIT_CANARY_START")
        lambda_weight = float(lambda_weight)
        if not 0.01 <= lambda_weight <= 0.25:
            raise ValueError("lambda_weight must be between 0.01 and 0.25")
        max_cycles = int(max_cycles)
        if not 1 <= max_cycles <= 20:
            raise ValueError("max_cycles must be between 1 and 20")
        max_changed_plan_ids = int(max_changed_plan_ids)
        if not 0 <= max_changed_plan_ids <= 6:
            raise ValueError("max_changed_plan_ids must be between 0 and 6")

        evaluation = self.v9.evaluate(
            pipeline_id=pipeline_id, cohort_id=cohort_id,
            min_pairs=min_pairs, min_sign_consistency=min_sign_consistency,
            min_effect=min_effect, min_validation_retention=min_validation_retention,
        )
        passing, effect = self._validated_effect(evaluation)
        prep_kind = str(evaluation.get("prep_kind") or "")
        multiplier = 1.0 + lambda_weight * effect
        baseline = _benefit_table()
        baseline_digest = _digest(baseline)
        thresholds = {
            "min_pairs": int(min_pairs),
            "min_sign_consistency": float(min_sign_consistency),
            "min_effect": float(min_effect),
            "min_validation_retention": float(min_validation_retention),
        }
        basis_id = {
            "pipeline_id": pipeline_id,
            "cohort_id": cohort_id,
            "evaluation_digest": evaluation["evaluation_digest"],
            "prep_kind": prep_kind,
            "lambda_weight": lambda_weight,
            "max_cycles": max_cycles,
            "max_changed_plan_ids": max_changed_plan_ids,
            "baseline_benefit_digest": baseline_digest,
            "thresholds": thresholds,
        }
        canary_id = "NBC-" + _digest(basis_id)[:24]
        path = self._plan_path(pipeline_id, canary_id)
        existing = self.prompt_runtime._safe_rel(path)
        if existing.is_file():
            return {"status": "REUSED", "canary": json.loads(existing.read_text(encoding="utf-8")), "git_mutation": False}

        plan = {
            "artifact": PLAN_ARTIFACT,
            "canary_id": canary_id,
            "pipeline_id": pipeline_id,
            "cohort_id": cohort_id,
            "v9_evaluation_digest": evaluation["evaluation_digest"],
            "prep_kind": prep_kind,
            "passing_metrics": passing,
            "validated_effect_index": round(effect, 9),
            "lambda_weight": lambda_weight,
            "benefit_multiplier": round(multiplier, 9),
            "baseline_benefit_digest": baseline_digest,
            "baseline_benefit_table": baseline,
            "thresholds": thresholds,
            "max_cycles": max_cycles,
            "cycles_used": 0,
            "max_changed_plan_ids": max_changed_plan_ids,
            "status": "ACTIVE",
            "created_at": _utcnow(),
            "updated_at": _utcnow(),
            "actor": actor,
            "standing": "BOUNDED_ROUTING_CANARY",
            "authority": "ROUTING_CANARY_ONLY",
            "canonical_benefit_prior_mutation": "NONE",
            "claim_effect": "NONE",
            "promotion_effect": "NONE",
            "laws": [
                "CONTROL_LANE_RETAINS_V5_V6_BENEFIT_PRIORS",
                "CANARY_MULTIPLIER != DIMENSIONAL_CAUSAL_MAPPING",
                "CANARY_ROUTING != CLAIM_AUTHORITY",
                "V10_CANARY != GLOBAL_REWARD_FUNCTION_REWRITE",
                "BASELINE_DRIFT_OR_V9_DRIFT => ROLLBACK",
            ],
        }
        plan["plan_digest"] = _digest(plan)
        commit = self.prompt_runtime._commit_files(
            current, {path: json.dumps(plan, indent=2, sort_keys=True) + "\n"}, actor,
            f"start NEXT V10 benefit canary {canary_id}",
        )
        return {"status": "STARTED", "canary": plan, "checkpoint_head": commit["head"], "git": commit,
                "authority": "ROUTING_CANARY_ONLY"}

    def _revalidate(self, plan: dict) -> dict:
        thresholds = dict(plan.get("thresholds") or {})
        evaluation = self.v9.evaluate(
            pipeline_id=plan["pipeline_id"], cohort_id=plan["cohort_id"],
            min_pairs=thresholds.get("min_pairs", 3),
            min_sign_consistency=thresholds.get("min_sign_consistency", 2.0 / 3.0),
            min_effect=thresholds.get("min_effect", 0.05),
            min_validation_retention=thresholds.get("min_validation_retention", 0.5),
        )
        return evaluation

    @staticmethod
    def _canary_profiles(control: dict, prep_kind: str, multiplier: float) -> dict[str, dict]:
        profiles = copy.deepcopy(control.get("calibrated_profiles") or {})
        if prep_kind not in profiles:
            raise ValueError("CANARY_PREP_KIND_NOT_IN_CALIBRATED_PROFILE")
        for key in VALUE_KEYS:
            profiles[prep_kind][key] = float(profiles[prep_kind][key]) * float(multiplier)
        return profiles

    def _allocate_with_profiles(self, *, control: dict, profiles: dict[str, dict], prep_kind: str,
                                canary_choice_plan_ids: list[str] | None = None) -> dict:
        breadth, _ = self.breadth._read_breadth(control["pipeline_id"])
        plans = dict(breadth.get("plans") or {})
        candidate_ids = list(control.get("candidate_plan_ids") or [])
        active_ids = list(control.get("active_plan_ids") or [])
        active_rows = [dict(plans[x]) for x in active_ids if x in plans]
        candidates = [dict(plans[x]) for x in candidate_ids if x in plans]
        available = {k: float((control.get("available_after_active") or {}).get(k, 0.0)) for k in RESOURCE_KEYS}
        new_slots = int(control.get("new_slots") or 0)
        roles = self.calibrated._roles(self.pipeline.state(control["pipeline_id"]))

        feasible: list[dict] = []
        max_take = min(new_slots, len(candidates))
        for size in range(0, max_take + 1):
            for combo in itertools.combinations(candidates, size):
                rows = list(combo)
                new_profile = _sum_profiles(rows, profiles)
                if any(new_profile[k] > available[k] for k in RESOURCE_KEYS):
                    continue
                combined = active_rows + rows
                cp = _sum_profiles(combined, profiles)
                quest_ids = {str((r.get("quest") or {}).get("quest_id")) for r in combined}
                kinds = {str(r.get("kind")) for r in combined}
                near = sum(1 for r in combined if roles.get(str((r.get("quest") or {}).get("quest_id"))) == 1)
                feasible.append({
                    "plan_ids": sorted(str(r.get("plan_id")) for r in rows),
                    "new_profile": new_profile,
                    "combined_profile": cp,
                    "coverage": len(quest_ids),
                    "diversity": len(kinds),
                    "near_count": near,
                })

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
            return (
                row["coverage"], cp["blocker_removal"], cp["reconstruction_reduction"], cp["information_gain"],
                row["diversity"], row["near_count"], -total_cost, -np["tokens"],
            )

        best_key = max((policy_key(row) for row in pareto), default=tuple())
        optima = [row for row in pareto if policy_key(row) == best_key] if pareto else []
        optimal_sets = [list(x) for x in sorted({tuple(row["plan_ids"]) for row in optima})]
        selected = None
        status = "NO_SCOUT_WORK" if not candidate_ids and not active_ids else "SELECTED"
        if optimal_sets:
            if len(optimal_sets) == 1:
                selected = optimal_sets[0]
            else:
                status = "AMBIGUOUS_CANARY_ALLOCATION"
                if canary_choice_plan_ids is not None:
                    choice = sorted(set(str(x) for x in canary_choice_plan_ids))
                    if choice not in optimal_sets:
                        raise ValueError("CANARY_CHOICE_NOT_OPTIMAL")
                    selected = choice
                    status = "RESOLVED_CANARY_ALLOCATION"
        if candidate_ids and selected == []:
            status = "BUDGET_HOLD_NO_FEASIBLE_NEW_WORK"
        basis = {
            "artifact": "ATHENA.NEXT.SCOUT.BENEFIT.CANARY.ALLOCATION.10",
            "pipeline_id": control["pipeline_id"],
            "prep_kind": prep_kind,
            "candidate_plan_ids": candidate_ids,
            "active_plan_ids": active_ids,
            "pareto_allocations": [row["plan_ids"] for row in pareto],
            "optimal_allocations": optimal_sets,
            "selected_plan_ids": selected,
            "policy_key": list(best_key),
        }
        return {**basis, "status": status, "allocation_digest": _digest(basis)}

    def preview(self, *, pipeline_id: str, canary_id: str, expected_pipeline_state_digest: str,
                prior_strength: int = 3, max_scouts: int = 4, reserve_slots: int = 1,
                token_budget: int = 24000, reserve_tokens: int = 4000,
                minute_budget: int = 60, reserve_minutes: int = 10,
                tool_call_budget: int = 16, reserve_tool_calls: int = 2,
                coordination_budget: int = 10, reserve_coordination: int = 2,
                git_risk_budget: int = 8, reserve_git_risk: int = 1,
                agent_id: str | None = None, remote: str = "origin", shared_remote_mode: str = "REQUIRED",
                control_choice_plan_ids: list[str] | None = None,
                canary_choice_plan_ids: list[str] | None = None) -> dict:
        plan = self._read_plan(pipeline_id, canary_id)
        if plan.get("status") != "ACTIVE":
            return {"artifact": VERSION, "status": f"CANARY_{plan.get('status')}", "canary": plan,
                    "routing_lane": "CONTROL", "authority": "ROUTING_CANARY_ONLY"}
        if int(plan.get("cycles_used") or 0) >= int(plan.get("max_cycles") or 0):
            return {"artifact": VERSION, "status": "CANARY_CYCLE_BUDGET_EXHAUSTED",
                    "rollback_required": True, "routing_lane": "CONTROL", "canary": plan,
                    "authority": "ROUTING_CANARY_ONLY"}
        if _digest(_benefit_table()) != plan.get("baseline_benefit_digest"):
            return {"artifact": VERSION, "status": "CANARY_BASELINE_BENEFIT_DRIFT",
                    "rollback_required": True, "routing_lane": "CONTROL", "canary": plan,
                    "authority": "ROUTING_CANARY_ONLY"}
        evaluation = self._revalidate(plan)
        if evaluation.get("evaluation_digest") != plan.get("v9_evaluation_digest") or evaluation.get("standing") != "BENEFIT_PRIOR_PROMOTION_CANDIDATE":
            return {"artifact": VERSION, "status": "CANARY_V9_EVALUATION_DRIFT",
                    "rollback_required": True, "routing_lane": "CONTROL", "canary": plan,
                    "current_v9": evaluation, "authority": "ROUTING_CANARY_ONLY"}

        control = self.calibrated.economy(
            pipeline_id=pipeline_id, expected_pipeline_state_digest=expected_pipeline_state_digest,
            prior_strength=prior_strength, max_scouts=max_scouts, reserve_slots=reserve_slots,
            token_budget=token_budget, reserve_tokens=reserve_tokens,
            minute_budget=minute_budget, reserve_minutes=reserve_minutes,
            tool_call_budget=tool_call_budget, reserve_tool_calls=reserve_tool_calls,
            coordination_budget=coordination_budget, reserve_coordination=reserve_coordination,
            git_risk_budget=git_risk_budget, reserve_git_risk=reserve_git_risk,
            agent_id=agent_id, remote=remote, shared_remote_mode=shared_remote_mode,
            choice_plan_ids=control_choice_plan_ids,
        )
        if "selected_plan_ids" not in control:
            return {"artifact": VERSION, "status": "CANARY_CONTROL_LANE_HOLD", "control": control,
                    "routing_lane": "CONTROL", "authority": "ROUTING_CANARY_ONLY"}
        profiles = self._canary_profiles(control, plan["prep_kind"], float(plan["benefit_multiplier"]))
        canary = self._allocate_with_profiles(
            control=control, profiles=profiles, prep_kind=plan["prep_kind"],
            canary_choice_plan_ids=canary_choice_plan_ids,
        )
        cset = control.get("selected_plan_ids")
        kset = canary.get("selected_plan_ids")
        if cset is None or kset is None:
            return {"artifact": VERSION, "status": "CANARY_AMBIGUOUS_ALLOCATION_HOLD",
                    "control": control, "canary_allocation": canary, "routing_lane": "CONTROL",
                    "authority": "ROUTING_CANARY_ONLY"}
        changed = sorted(set(cset) ^ set(kset))
        rollback_required = len(changed) > int(plan.get("max_changed_plan_ids") or 0)
        status = "CANARY_DIVERGENCE_LIMIT_HOLD" if rollback_required else "CANARY_PREVIEW_READY"
        basis = {
            "artifact": VERSION,
            "pipeline_id": pipeline_id,
            "canary_id": canary_id,
            "plan_digest": plan["plan_digest"],
            "pipeline_state_digest": expected_pipeline_state_digest,
            "control_allocation_digest": control.get("allocation_digest"),
            "canary_allocation_digest": canary.get("allocation_digest"),
            "control_selected_plan_ids": cset,
            "canary_selected_plan_ids": kset,
            "changed_plan_ids": changed,
            "rollback_required": rollback_required,
            "routing_lane": "CONTROL" if rollback_required else "CANARY",
        }
        return {**basis, "status": status, "preview_digest": _digest(basis),
                "control": control, "canary_allocation": canary,
                "benefit_profiles": profiles, "authority": "ROUTING_CANARY_ONLY",
                "claim_effect": "NONE", "promotion_effect": "NONE",
                "law": "CANARY_RECOMMENDATION_STILL_REQUIRES_NORMAL_MESSAGE_BOARD_SCOUT_CLAIM"}

    def _write_plan_state(self, plan: dict, *, current: str, actor: str, decision: dict | None = None,
                          message: str) -> dict:
        plan = dict(plan)
        plan["updated_at"] = _utcnow()
        plan["plan_digest"] = _digest({k: v for k, v in plan.items() if k != "plan_digest"})
        files = {self._plan_path(plan["pipeline_id"], plan["canary_id"]): json.dumps(plan, indent=2, sort_keys=True) + "\n"}
        if decision is not None:
            ordinal = int(plan.get("cycles_used") or 0)
            files[self._decision_path(plan["pipeline_id"], plan["canary_id"], ordinal)] = json.dumps(decision, indent=2, sort_keys=True) + "\n"
        commit = self.prompt_runtime._commit_files(current, files, actor, message)
        return {"plan": plan, "checkpoint_head": commit["head"], "git": commit}

    def rollback(self, *, pipeline_id: str, canary_id: str, expected_git_head: str,
                 reason: str, actor: str = "agent", automatic: bool = False) -> dict:
        current = self.git.head()
        if current != expected_git_head:
            raise ValueError("STALE_GIT_HEAD_FOR_BENEFIT_CANARY_ROLLBACK")
        reason = str(reason or "").strip()
        if not reason:
            raise ValueError("rollback reason is required")
        plan = self._read_plan(pipeline_id, canary_id)
        if plan.get("status") == "ROLLED_BACK":
            return {"status": "ALREADY_ROLLED_BACK", "canary": plan, "git_mutation": False}
        plan["status"] = "ROLLED_BACK"
        plan["rollback"] = {"reason": reason, "automatic": bool(automatic), "at": _utcnow()}
        result = self._write_plan_state(plan, current=current, actor=actor,
                                        message=f"rollback NEXT V10 benefit canary {canary_id}")
        return {"status": "ROLLED_BACK", "canary": result["plan"], "checkpoint_head": result["checkpoint_head"],
                "git": result["git"], "routing_lane": "CONTROL", "canonical_benefit_prior_mutation": "NONE"}

    def apply(self, *, pipeline_id: str, canary_id: str, expected_pipeline_state_digest: str,
              expected_git_head: str, actor: str = "agent", **kwargs) -> dict:
        current = self.git.head()
        if current != expected_git_head:
            raise ValueError("STALE_GIT_HEAD_FOR_BENEFIT_CANARY_APPLY")
        preview = self.preview(
            pipeline_id=pipeline_id, canary_id=canary_id,
            expected_pipeline_state_digest=expected_pipeline_state_digest, **kwargs,
        )
        if preview.get("rollback_required") is True:
            rolled = self.rollback(
                pipeline_id=pipeline_id, canary_id=canary_id, expected_git_head=current,
                reason=str(preview.get("status")), actor=actor, automatic=True,
            )
            return {"status": "AUTO_ROLLED_BACK", "trigger": preview.get("status"),
                    "preview": preview, "rollback": rolled, "routing_lane": "CONTROL"}
        if preview.get("status") != "CANARY_PREVIEW_READY":
            return {"status": preview.get("status"), "preview": preview,
                    "routing_lane": "CONTROL", "git_mutation": False}

        plan = self._read_plan(pipeline_id, canary_id)
        plan["cycles_used"] = int(plan.get("cycles_used") or 0) + 1
        decision = {
            "artifact": DECISION_ARTIFACT,
            "canary_id": canary_id,
            "pipeline_id": pipeline_id,
            "cycle": plan["cycles_used"],
            "pipeline_state_digest": expected_pipeline_state_digest,
            "preview_digest": preview["preview_digest"],
            "control_selected_plan_ids": preview["control_selected_plan_ids"],
            "canary_selected_plan_ids": preview["canary_selected_plan_ids"],
            "changed_plan_ids": preview["changed_plan_ids"],
            "routing_lane": "CANARY",
            "created_at": _utcnow(),
            "actor": actor,
            "authority": "ROUTING_CANARY_ONLY",
            "claim_effect": "NONE",
            "canonical_benefit_prior_mutation": "NONE",
        }
        decision["decision_digest"] = _digest(decision)
        if plan["cycles_used"] >= int(plan["max_cycles"]):
            plan["status"] = "EXPIRED"
            plan["expiry"] = {"reason": "MAX_CYCLES_REACHED_AFTER_DECISION", "at": _utcnow()}
        result = self._write_plan_state(
            plan, current=current, actor=actor, decision=decision,
            message=f"apply NEXT V10 benefit canary {canary_id} cycle {plan['cycles_used']}",
        )
        return {
            "status": "CANARY_APPLIED",
            "decision": decision,
            "canary": result["plan"],
            "checkpoint_head": result["checkpoint_head"],
            "git": result["git"],
            "routing_lane": "CANARY",
            "selected_plan_ids": decision["canary_selected_plan_ids"],
            "claim_effect": "NONE",
            "canonical_benefit_prior_mutation": "NONE",
            "law": "APPLIED_ROUTING_CANARY != SCOUT_CLAIM_OR_GLOBAL_PRIOR_MUTATION",
        }

    def state(self, *, pipeline_id: str, canary_id: str) -> dict:
        plan = self._read_plan(pipeline_id, canary_id)
        return {
            "artifact": VERSION,
            "status": plan.get("status"),
            "canary": plan,
            "git_head": self.git.head(),
            "routing_lane": "CANARY" if plan.get("status") == "ACTIVE" else "CONTROL",
            "canonical_benefit_prior_mutation": "NONE",
            "authority": "ROUTING_CANARY_ONLY",
        }

    def call_tool(self, name: str, a: dict) -> dict:
        if name == TOOLS["start"]:
            return self.start(**a)
        if name == TOOLS["preview"]:
            return self.preview(**a)
        if name == TOOLS["apply"]:
            return self.apply(**a)
        if name == TOOLS["rollback"]:
            return self.rollback(**a)
        if name == TOOLS["state"]:
            return self.state(**a)
        raise KeyError(name)


_ECON_PROPS = {
    "prior_strength": {"type": "integer", "minimum": 1, "maximum": 100},
    "max_scouts": {"type": "integer", "minimum": 1, "maximum": 32},
    "reserve_slots": {"type": "integer", "minimum": 0, "maximum": 31},
    "token_budget": {"type": "integer", "minimum": 1}, "reserve_tokens": {"type": "integer", "minimum": 0},
    "minute_budget": {"type": "integer", "minimum": 1}, "reserve_minutes": {"type": "integer", "minimum": 0},
    "tool_call_budget": {"type": "integer", "minimum": 1}, "reserve_tool_calls": {"type": "integer", "minimum": 0},
    "coordination_budget": {"type": "integer", "minimum": 1}, "reserve_coordination": {"type": "integer", "minimum": 0},
    "git_risk_budget": {"type": "integer", "minimum": 1}, "reserve_git_risk": {"type": "integer", "minimum": 0},
    "agent_id": {"type": ["string", "null"]}, "remote": {"type": "string"},
    "shared_remote_mode": {"type": "string", "enum": ["REQUIRED", "BEST_EFFORT", "DISABLED"]},
    "control_choice_plan_ids": {"type": ["array", "null"], "items": {"type": "string"}},
    "canary_choice_plan_ids": {"type": ["array", "null"], "items": {"type": "string"}},
}

NEXT_SCOUT_BENEFIT_CANARY_TOOLS = [
    {"name": TOOLS["start"], "description": "Start a bounded reversible V10 routing canary from a V9 held-out promotion candidate. Does not mutate the canonical V5 benefit table.",
     "inputSchema": {"type":"object","required":["pipeline_id","cohort_id","expected_git_head"],"properties":{"pipeline_id":{"type":"string"},"cohort_id":{"type":"string"},"expected_git_head":{"type":"string"},"lambda_weight":{"type":"number","minimum":0.01,"maximum":0.25},"max_cycles":{"type":"integer","minimum":1,"maximum":20},"max_changed_plan_ids":{"type":"integer","minimum":0,"maximum":6},"actor":{"type":"string"},"min_pairs":{"type":"integer","minimum":3,"maximum":1000},"min_sign_consistency":{"type":"number","minimum":0.5,"maximum":1.0},"min_effect":{"type":"number","minimum":0.0,"maximum":1.0},"min_validation_retention":{"type":"number","minimum":0.0,"maximum":1.0}},"additionalProperties":False}},
    {"name": TOOLS["preview"], "description": "Compare V6 control and bounded V10 canary scout allocations side-by-side. Read-only; ambiguity or drift routes to control.",
     "inputSchema": {"type":"object","required":["pipeline_id","canary_id","expected_pipeline_state_digest"],"properties":{"pipeline_id":{"type":"string"},"canary_id":{"type":"string"},"expected_pipeline_state_digest":{"type":"string"},**_ECON_PROPS},"additionalProperties":False}},
    {"name": TOOLS["apply"], "description": "Persist one bounded V10 canary routing decision. The returned plan IDs still require normal Message Board scout claims; no global prior mutation occurs.",
     "inputSchema": {"type":"object","required":["pipeline_id","canary_id","expected_pipeline_state_digest","expected_git_head"],"properties":{"pipeline_id":{"type":"string"},"canary_id":{"type":"string"},"expected_pipeline_state_digest":{"type":"string"},"expected_git_head":{"type":"string"},"actor":{"type":"string"},**_ECON_PROPS},"additionalProperties":False}},
    {"name": TOOLS["rollback"], "description": "Manually or automatically roll back a V10 routing canary to the unchanged control lane.",
     "inputSchema": {"type":"object","required":["pipeline_id","canary_id","expected_git_head","reason"],"properties":{"pipeline_id":{"type":"string"},"canary_id":{"type":"string"},"expected_git_head":{"type":"string"},"reason":{"type":"string"},"actor":{"type":"string"},"automatic":{"type":"boolean"}},"additionalProperties":False}},
    {"name": TOOLS["state"], "description": "Read V10 canary state and current routing lane without mutation.",
     "inputSchema": {"type":"object","required":["pipeline_id","canary_id"],"properties":{"pipeline_id":{"type":"string"},"canary_id":{"type":"string"}},"additionalProperties":False}},
]
NEXT_SCOUT_BENEFIT_CANARY_TOOL_NAMES = {x["name"] for x in NEXT_SCOUT_BENEFIT_CANARY_TOOLS}


def install_next_scout_benefit_canary_extension(prompt_runtime_cls, tool_list: list[dict], tool_names: set[str]) -> None:
    if getattr(prompt_runtime_cls, "_athena_next_scout_benefit_canary_v10_registered", False):
        return
    previous_call = prompt_runtime_cls.call_tool

    def call_with_v10(self, name, arguments):
        if name in NEXT_SCOUT_BENEFIT_CANARY_TOOL_NAMES:
            runtime = getattr(self, "_next_scout_benefit_canary_runtime_v10", None)
            if runtime is None:
                v9 = getattr(self, "_next_scout_causal_promotion_runtime_v9", None)
                calibrated = getattr(self, "_next_scout_calibrated_economy_runtime_v6", None)
                if v9 is None or calibrated is None:
                    from .next_quest_pipeline import RollingQuestPipelineRuntime
                    from .next_quest_pipeline_breadth import NextQuestBreadthRuntime
                    from .next_scout_metabolism import NextScoutMetabolismRuntime
                    from .next_scout_outcome_value import NextScoutOutcomeValueRuntime
                    from .next_scout_counterfactual_credit import NextScoutCounterfactualCreditRuntime
                    pipeline = getattr(self, "_next_pipeline_runtime_v1", None) or RollingQuestPipelineRuntime(self.git, self)
                    breadth = getattr(self, "_next_pipeline_breadth_runtime_v2", None) or NextQuestBreadthRuntime(pipeline)
                    if calibrated is None:
                        metabolism = getattr(self, "_next_scout_metabolism_runtime_v6", None) or NextScoutMetabolismRuntime(pipeline, breadth)
                        calibrated = NextScoutCalibratedEconomyRuntime(pipeline, breadth, metabolism=metabolism)
                        self._next_scout_calibrated_economy_runtime_v6 = calibrated
                    if v9 is None:
                        outcomes = getattr(self, "_next_scout_outcome_value_runtime_v7", None) or NextScoutOutcomeValueRuntime(pipeline, breadth)
                        cf = getattr(self, "_next_scout_counterfactual_credit_runtime_v8", None) or NextScoutCounterfactualCreditRuntime(pipeline, breadth, outcomes)
                        v9 = NextScoutCausalPromotionRuntime(cf)
                        self._next_scout_causal_promotion_runtime_v9 = v9
                runtime = NextScoutBenefitCanaryRuntime(v9, calibrated)
                self._next_scout_benefit_canary_runtime_v10 = runtime
            return runtime.call_tool(name, arguments)
        return previous_call(self, name, arguments)

    prompt_runtime_cls.call_tool = call_with_v10
    prompt_runtime_cls._athena_next_scout_benefit_canary_v10_registered = True
    for tool in NEXT_SCOUT_BENEFIT_CANARY_TOOLS:
        if tool["name"] not in tool_names:
            tool_list.append(tool)
            tool_names.add(tool["name"])


__all__ = [
    "VERSION", "PLAN_ARTIFACT", "DECISION_ARTIFACT", "TOOLS",
    "NextScoutBenefitCanaryRuntime", "NEXT_SCOUT_BENEFIT_CANARY_TOOLS",
    "NEXT_SCOUT_BENEFIT_CANARY_TOOL_NAMES", "install_next_scout_benefit_canary_extension",
]
