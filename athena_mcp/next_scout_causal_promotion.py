from __future__ import annotations

import hashlib
import json
import statistics
from datetime import datetime, timezone
from typing import Any

from .next_quest_pipeline_breadth import PREP_KINDS
from .next_scout_counterfactual_credit import NextScoutCounterfactualCreditRuntime, OUTCOME_SCORES

VERSION = "ATHENA.NEXT.SCOUT.CAUSAL.PROMOTION.9"
COHORT_ARTIFACT = "ATHENA.NEXT.SCOUT.VALIDATION.COHORT.9"
EVAL_ARTIFACT = "ATHENA.NEXT.SCOUT.VALIDATION.EVALUATION.9"
TOOLS = {
    "freeze": "athena_next_scout_validation_freeze",
    "evaluate": "athena_next_scout_validation_evaluate",
    "overlay": "athena_next_scout_validation_overlay",
}


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def _root(pipeline_id: str) -> str:
    return f"prompts/next_quest_pipelines/{pipeline_id}/counterfactual/v9"


def _q(values: list[float], p: float) -> float | None:
    if not values:
        return None
    xs = sorted(values)
    if len(xs) == 1:
        return xs[0]
    pos = (len(xs) - 1) * p
    lo, hi = int(pos), min(int(pos) + 1, len(xs) - 1)
    frac = pos - lo
    return xs[lo] * (1.0 - frac) + xs[hi] * frac


class NextScoutCausalPromotionRuntime:
    """V9 held-out validation membrane for V8 benefit-prior candidates.

    V9 does not mutate the live economy. It freezes non-overlapping discovery and
    validation pair cohorts, requires independently sourced pre-outcome assignment,
    evaluates replication on the untouched validation cohort, and may emit a
    reversible promotion *candidate*. Matched observational evidence remains below
    randomized causal proof and below live benefit-prior authority.
    """

    def __init__(self, counterfactual: NextScoutCounterfactualCreditRuntime):
        self.counterfactual = counterfactual
        self.git = counterfactual.git
        self.prompt_runtime = counterfactual.prompt_runtime

    def _paths(self, pipeline_id: str) -> dict[str, str]:
        base = _root(pipeline_id)
        return {"base": base, "cohorts": f"{base}/cohorts"}

    def _pair_map(self, pipeline_id: str) -> dict[str, dict]:
        return {str(p.get("pair_id")): p for p in self.counterfactual._read_pairs(pipeline_id)}

    def _read_cohort(self, pipeline_id: str, cohort_id: str) -> dict:
        path = self.prompt_runtime._safe_rel(f"{self._paths(pipeline_id)['cohorts']}/{cohort_id}.json")
        if not path.is_file():
            raise ValueError("VALIDATION_COHORT_NOT_FOUND")
        row = json.loads(path.read_text(encoding="utf-8"))
        if row.get("artifact") != COHORT_ARTIFACT or row.get("pipeline_id") != pipeline_id:
            raise ValueError("INVALID_VALIDATION_COHORT")
        if _digest({k: v for k, v in row.items() if k != "cohort_digest"}) != row.get("cohort_digest"):
            raise ValueError("VALIDATION_COHORT_DIGEST_HOLD")
        return row

    @staticmethod
    def _receipt_ids(pairs: list[dict]) -> set[str]:
        ids: set[str] = set()
        for pair in pairs:
            ids.add(str(pair.get("treated_receipt_id") or ""))
            ids.add(str(pair.get("control_receipt_id") or ""))
        ids.discard("")
        return ids

    @staticmethod
    def _cohort_stats(pairs: list[dict], min_pairs: int, min_sign_consistency: float, min_effect: float) -> dict:
        treated = [str(p.get("treated_receipt_id") or "") for p in pairs]
        control = [str(p.get("control_receipt_id") or "") for p in pairs]
        independence_hold = len(treated) != len(set(treated)) or len(control) != len(set(control))
        metrics: dict[str, dict] = {}
        for metric in OUTCOME_SCORES:
            vals = [float((p.get("outcome_delta") or {})[metric]) for p in pairs if metric in (p.get("outcome_delta") or {})]
            n = len(vals)
            med = float(statistics.median(vals)) if vals else None
            pos = sum(v > 0 for v in vals)
            neg = sum(v < 0 for v in vals)
            consistency = max(pos, neg) / n if n else 0.0
            q25 = _q(vals, 0.25)
            q75 = _q(vals, 0.75)
            passed = bool(not independence_hold and n >= min_pairs and med is not None and med >= min_effect and consistency >= min_sign_consistency)
            metrics[metric] = {
                "pairs": n,
                "median_delta": None if med is None else round(med, 6),
                "q25_delta": None if q25 is None else round(q25, 6),
                "q75_delta": None if q75 is None else round(q75, 6),
                "positive": pos,
                "negative": neg,
                "sign_consistency": round(consistency, 6),
                "passes": passed,
            }
        return {"pair_count": len(pairs), "independence_hold": independence_hold, "metrics": metrics}

    def freeze(self, *, pipeline_id: str, prep_kind: str, discovery_pair_ids: list[str], validation_pair_ids: list[str],
               split_basis: dict, expected_git_head: str, actor: str = "agent") -> dict:
        prep_kind = str(prep_kind or "").upper()
        if prep_kind not in PREP_KINDS:
            raise ValueError("unsupported prep_kind")
        current = self.git.head()
        if current != expected_git_head:
            raise ValueError("STALE_GIT_HEAD_FOR_VALIDATION_FREEZE")
        if len(set(discovery_pair_ids)) != len(discovery_pair_ids) or len(set(validation_pair_ids)) != len(validation_pair_ids):
            raise ValueError("COHORT_PAIR_IDS_MUST_BE_UNIQUE")
        if set(discovery_pair_ids) & set(validation_pair_ids):
            raise ValueError("DISCOVERY_VALIDATION_PAIR_OVERLAP")
        if len(discovery_pair_ids) < 3 or len(validation_pair_ids) < 3:
            raise ValueError("VALIDATION_REQUIRES_AT_LEAST_THREE_PAIRS_PER_COHORT")

        pairs = self._pair_map(pipeline_id)
        try:
            discovery = [pairs[x] for x in discovery_pair_ids]
            validation = [pairs[x] for x in validation_pair_ids]
        except KeyError as exc:
            raise ValueError("VALIDATION_COHORT_REFERENCES_UNKNOWN_PAIR") from exc
        if any(p.get("prep_kind") != prep_kind for p in discovery + validation):
            raise ValueError("VALIDATION_COHORT_PREP_KIND_MISMATCH")
        if self._receipt_ids(discovery) & self._receipt_ids(validation):
            raise ValueError("DISCOVERY_VALIDATION_RECEIPT_LEAKAGE")

        if not isinstance(split_basis, dict) or split_basis.get("observed") is not True:
            raise ValueError("split_basis requires observed=true")
        source = str(split_basis.get("source") or "").strip()
        if not source:
            raise ValueError("split_basis requires non-empty source")
        if split_basis.get("independent_of_scout") is not True:
            raise ValueError("split_basis requires independent_of_scout=true")
        if split_basis.get("assigned_before_outcome") is not True:
            raise ValueError("HELD_OUT_VALIDATION_REQUIRES_PREOUTCOME_ASSIGNMENT")

        split = {
            "observed": True,
            "source": source,
            "independent_of_scout": True,
            "assigned_before_outcome": True,
            "standing": "ATTESTED_PREOUTCOME_SPLIT",
        }
        cohort_id = "NCV-" + _digest({
            "pipeline_id": pipeline_id, "prep_kind": prep_kind,
            "discovery": discovery_pair_ids, "validation": validation_pair_ids, "split": split,
        })[:24]
        path = f"{self._paths(pipeline_id)['cohorts']}/{cohort_id}.json"
        existing = self.prompt_runtime._safe_rel(path)
        if existing.is_file():
            return {"status": "REUSED", "cohort": json.loads(existing.read_text(encoding="utf-8")), "git_mutation": False}
        cohort = {
            "artifact": COHORT_ARTIFACT,
            "cohort_id": cohort_id,
            "pipeline_id": pipeline_id,
            "prep_kind": prep_kind,
            "discovery_pair_ids": list(discovery_pair_ids),
            "validation_pair_ids": list(validation_pair_ids),
            "discovery_pair_digests": [p.get("pair_digest") for p in discovery],
            "validation_pair_digests": [p.get("pair_digest") for p in validation],
            "split_basis": split,
            "created_at": _utcnow(),
            "actor": actor,
            "standing": "FROZEN_DISCOVERY_VALIDATION_COHORT",
            "authority": "VALIDATION_ANALYSIS_ONLY",
            "laws": [
                "DISCOVERY_SET != VALIDATION_SET",
                "VALIDATION_ASSIGNMENT_MUST_PRECEDE_OUTCOME_OBSERVATION",
                "RECEIPT_IDENTITY_CANNOT_LEAK_ACROSS_COHORTS",
                "FROZEN_COHORT != LIVE_BENEFIT_PRIOR_UPDATE",
            ],
        }
        cohort["cohort_digest"] = _digest(cohort)
        commit = self.prompt_runtime._commit_files(current, {path: json.dumps(cohort, indent=2, sort_keys=True) + "\n"}, actor,
                                                   f"freeze NEXT V9 validation cohort {cohort_id}")
        return {"status": "FROZEN", "cohort": cohort, "checkpoint_head": commit["head"], "git": commit,
                "authority": "VALIDATION_ANALYSIS_ONLY"}

    def evaluate(self, *, pipeline_id: str, cohort_id: str, min_pairs: int = 3,
                 min_sign_consistency: float = 2.0 / 3.0, min_effect: float = 0.05,
                 min_validation_retention: float = 0.5) -> dict:
        min_pairs = int(min_pairs)
        min_sign_consistency = float(min_sign_consistency)
        min_effect = float(min_effect)
        min_validation_retention = float(min_validation_retention)
        if not 3 <= min_pairs <= 1000:
            raise ValueError("min_pairs must be between 3 and 1000")
        if not 0.5 <= min_sign_consistency <= 1.0:
            raise ValueError("min_sign_consistency must be between 0.5 and 1")
        if not 0.0 <= min_effect <= 1.0:
            raise ValueError("min_effect must be between 0 and 1")
        if not 0.0 <= min_validation_retention <= 1.0:
            raise ValueError("min_validation_retention must be between 0 and 1")

        cohort = self._read_cohort(pipeline_id, cohort_id)
        pair_map = self._pair_map(pipeline_id)
        discovery = [pair_map[x] for x in cohort["discovery_pair_ids"]]
        validation = [pair_map[x] for x in cohort["validation_pair_ids"]]
        if [p.get("pair_digest") for p in discovery] != cohort.get("discovery_pair_digests") or [p.get("pair_digest") for p in validation] != cohort.get("validation_pair_digests"):
            raise ValueError("FROZEN_VALIDATION_PAIR_DRIFT")
        d = self._cohort_stats(discovery, min_pairs, min_sign_consistency, min_effect)
        v = self._cohort_stats(validation, min_pairs, min_sign_consistency, min_effect)

        metrics: dict[str, dict] = {}
        promoted: list[str] = []
        for metric in OUTCOME_SCORES:
            dr, vr = d["metrics"][metric], v["metrics"][metric]
            dm, vm = dr["median_delta"], vr["median_delta"]
            retention = (vm / dm) if dm not in (None, 0) and vm is not None else None
            passes = bool(
                dr["passes"] and vr["passes"] and
                dm is not None and vm is not None and dm > 0 and vm > 0 and
                retention is not None and retention >= min_validation_retention and
                vr["q25_delta"] is not None and vr["q25_delta"] >= 0
            )
            standing = "HELD_OUT_REPLICATION_CANDIDATE" if passes else "ABSTAIN_VALIDATION_NOT_REPLICATED"
            if passes:
                promoted.append(metric)
            metrics[metric] = {
                "discovery": dr,
                "validation": vr,
                "validation_retention": None if retention is None else round(retention, 6),
                "standing": standing,
                "passes_promotion_candidate_gate": passes,
            }

        standing = "BENEFIT_PRIOR_PROMOTION_CANDIDATE" if promoted else "ABSTAIN_HELD_OUT_VALIDATION"
        basis = {
            "artifact": EVAL_ARTIFACT,
            "pipeline_id": pipeline_id,
            "cohort_id": cohort_id,
            "cohort_digest": cohort["cohort_digest"],
            "prep_kind": cohort["prep_kind"],
            "metrics": metrics,
            "passing_metrics": promoted,
            "standing": standing,
            "causal_proof": False,
            "split_standing": cohort["split_basis"]["standing"],
            "reversible_candidate": True,
            "live_benefit_prior_mutation": "NONE",
            "allocation_effect": "NONE",
            "promotion_effect": "NONE",
            "authority": "VALIDATION_ANALYSIS_ONLY",
        }
        return {**basis, "evaluation_digest": _digest(basis), "laws": [
            "DISCOVERY_SET != VALIDATION_SET",
            "HELD_OUT_REPLICATION != RANDOMIZED_CAUSAL_PROOF",
            "VALIDATION_FAILURE => ABSTAIN",
            "V9_PROMOTION_CANDIDATE != LIVE_ECONOMY_MUTATION",
        ]}

    def overlay(self, *, pipeline_id: str, cohort_id: str, **kwargs) -> dict:
        result = self.evaluate(pipeline_id=pipeline_id, cohort_id=cohort_id, **kwargs)
        basis = {
            "artifact": "ATHENA.NEXT.SCOUT.CAUSAL.PROMOTION.OVERLAY.9",
            "pipeline_id": pipeline_id,
            "cohort_id": cohort_id,
            "evaluation_digest": result["evaluation_digest"],
            "prep_kind": result["prep_kind"],
            "standing": result["standing"],
            "passing_metrics": result["passing_metrics"],
            "causal_proof": False,
            "live_benefit_prior_mutation": "NONE",
            "allocation_effect": "NONE",
            "promotion_effect": "NONE",
        }
        return {**basis, "overlay_digest": _digest(basis),
                "law": "V9_VALIDATION_CAN_NOMINATE_BUT_CANNOT_APPLY_LIVE_BENEFIT_PRIORS"}

    def call_tool(self, name: str, a: dict) -> dict:
        if name == TOOLS["freeze"]:
            return self.freeze(pipeline_id=a["pipeline_id"], prep_kind=a["prep_kind"],
                               discovery_pair_ids=a["discovery_pair_ids"], validation_pair_ids=a["validation_pair_ids"],
                               split_basis=a["split_basis"], expected_git_head=a["expected_git_head"], actor=a.get("actor", "agent"))
        if name == TOOLS["evaluate"]:
            return self.evaluate(pipeline_id=a["pipeline_id"], cohort_id=a["cohort_id"], min_pairs=a.get("min_pairs", 3),
                                 min_sign_consistency=a.get("min_sign_consistency", 2.0/3.0), min_effect=a.get("min_effect", 0.05),
                                 min_validation_retention=a.get("min_validation_retention", 0.5))
        if name == TOOLS["overlay"]:
            return self.overlay(pipeline_id=a["pipeline_id"], cohort_id=a["cohort_id"], min_pairs=a.get("min_pairs", 3),
                                min_sign_consistency=a.get("min_sign_consistency", 2.0/3.0), min_effect=a.get("min_effect", 0.05),
                                min_validation_retention=a.get("min_validation_retention", 0.5))
        raise KeyError(name)


NEXT_SCOUT_CAUSAL_PROMOTION_TOOLS = [
    {"name": TOOLS["freeze"], "description": "Freeze disjoint V8 discovery and held-out validation pair cohorts using independently sourced pre-outcome assignment. Does not promote or mutate benefit priors.",
     "inputSchema": {"type":"object","required":["pipeline_id","prep_kind","discovery_pair_ids","validation_pair_ids","split_basis","expected_git_head"],"properties":{"pipeline_id":{"type":"string"},"prep_kind":{"type":"string"},"discovery_pair_ids":{"type":"array","minItems":3,"items":{"type":"string"}},"validation_pair_ids":{"type":"array","minItems":3,"items":{"type":"string"}},"split_basis":{"type":"object"},"expected_git_head":{"type":"string"},"actor":{"type":"string"}},"additionalProperties":False}},
    {"name": TOOLS["evaluate"], "description": "Evaluate V9 out-of-sample replication across a frozen validation cohort. Passing output is a reversible promotion candidate only, never live economy mutation.",
     "inputSchema": {"type":"object","required":["pipeline_id","cohort_id"],"properties":{"pipeline_id":{"type":"string"},"cohort_id":{"type":"string"},"min_pairs":{"type":"integer","minimum":3,"maximum":1000},"min_sign_consistency":{"type":"number","minimum":0.5,"maximum":1.0},"min_effect":{"type":"number","minimum":0.0,"maximum":1.0},"min_validation_retention":{"type":"number","minimum":0.0,"maximum":1.0}},"additionalProperties":False}},
    {"name": TOOLS["overlay"], "description": "Read-only V9 causal-promotion overlay. Shows held-out replication standing while preserving causal-proof and live-prior mutation firewalls.",
     "inputSchema": {"type":"object","required":["pipeline_id","cohort_id"],"properties":{"pipeline_id":{"type":"string"},"cohort_id":{"type":"string"},"min_pairs":{"type":"integer","minimum":3,"maximum":1000},"min_sign_consistency":{"type":"number","minimum":0.5,"maximum":1.0},"min_effect":{"type":"number","minimum":0.0,"maximum":1.0},"min_validation_retention":{"type":"number","minimum":0.0,"maximum":1.0}},"additionalProperties":False}},
]
NEXT_SCOUT_CAUSAL_PROMOTION_TOOL_NAMES = {x["name"] for x in NEXT_SCOUT_CAUSAL_PROMOTION_TOOLS}


def install_next_scout_causal_promotion_extension(prompt_runtime_cls, tool_list: list[dict], tool_names: set[str]) -> None:
    if getattr(prompt_runtime_cls, "_athena_next_scout_causal_promotion_v9_registered", False):
        return
    previous_call = prompt_runtime_cls.call_tool
    def call_with_v9(self, name, arguments):
        if name in NEXT_SCOUT_CAUSAL_PROMOTION_TOOL_NAMES:
            runtime = getattr(self, "_next_scout_causal_promotion_runtime_v9", None)
            if runtime is None:
                cf = getattr(self, "_next_scout_counterfactual_credit_runtime_v8", None)
                if cf is None:
                    from .next_quest_pipeline import RollingQuestPipelineRuntime
                    from .next_quest_pipeline_breadth import NextQuestBreadthRuntime
                    from .next_scout_outcome_value import NextScoutOutcomeValueRuntime
                    pipeline = getattr(self, "_next_pipeline_runtime_v1", None) or RollingQuestPipelineRuntime(self.git, self)
                    breadth = getattr(self, "_next_pipeline_breadth_runtime_v2", None) or NextQuestBreadthRuntime(pipeline)
                    outcomes = getattr(self, "_next_scout_outcome_value_runtime_v7", None) or NextScoutOutcomeValueRuntime(pipeline, breadth)
                    cf = NextScoutCounterfactualCreditRuntime(pipeline, breadth, outcomes)
                    self._next_scout_counterfactual_credit_runtime_v8 = cf
                runtime = NextScoutCausalPromotionRuntime(cf)
                self._next_scout_causal_promotion_runtime_v9 = runtime
            return runtime.call_tool(name, arguments)
        return previous_call(self, name, arguments)
    prompt_runtime_cls.call_tool = call_with_v9
    prompt_runtime_cls._athena_next_scout_causal_promotion_v9_registered = True
    for tool in NEXT_SCOUT_CAUSAL_PROMOTION_TOOLS:
        if tool["name"] not in tool_names:
            tool_list.append(tool)
            tool_names.add(tool["name"])


__all__ = ["VERSION", "COHORT_ARTIFACT", "EVAL_ARTIFACT", "TOOLS", "NextScoutCausalPromotionRuntime",
           "NEXT_SCOUT_CAUSAL_PROMOTION_TOOLS", "NEXT_SCOUT_CAUSAL_PROMOTION_TOOL_NAMES",
           "install_next_scout_causal_promotion_extension"]
