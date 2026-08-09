from __future__ import annotations

import hashlib
import json
import statistics
from datetime import datetime, timezone
from typing import Any

from .next_quest_pipeline import RollingQuestPipelineRuntime
from .next_quest_pipeline_breadth import NextQuestBreadthRuntime, PREP_KINDS
from .next_scout_outcome_value import NextScoutOutcomeValueRuntime

VERSION = "ATHENA.NEXT.SCOUT.COUNTERFACTUAL.CREDIT.8"
PAIR_ARTIFACT = "ATHENA.NEXT.SCOUT.COUNTERFACTUAL.PAIR.8"
ESTIMATE_ARTIFACT = "ATHENA.NEXT.SCOUT.COUNTERFACTUAL.ESTIMATE.8"
OVERLAY_ARTIFACT = "ATHENA.NEXT.SCOUT.COUNTERFACTUAL.OVERLAY.8"
TOOLS = {
    "pair": "athena_next_scout_counterfactual_pair_record",
    "estimate": "athena_next_scout_counterfactual_estimate",
    "overlay": "athena_next_scout_counterfactual_overlay",
}
OUTCOME_SCORES = ("downstream_success", "test_quality", "low_rework", "blocker_resolution")
FORBIDDEN_MATCH_KEYS = {
    "completion_status", "completion_summary", "completed_at", "evidence_refs",
    "focus_success", "test_pass_ratio", "rework_count", "blocker_resolution_ratio",
    "downstream_success", "test_quality", "low_rework", "blocker_resolution",
    "outcome", "outcomes", "result", "results", "success", "failure",
}


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _root(pipeline_id: str) -> str:
    return f"prompts/next_quest_pipelines/{pipeline_id}/counterfactual/v8"


def _contains_forbidden_key(value: Any) -> bool:
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key).strip().lower() in FORBIDDEN_MATCH_KEYS:
                return True
            if _contains_forbidden_key(child):
                return True
    elif isinstance(value, list):
        return any(_contains_forbidden_key(x) for x in value)
    return False


def _prep_kinds(receipt: dict) -> set[str]:
    return {str(row.get("kind") or "") for row in receipt.get("associated_prep") or [] if row.get("kind")}


def _score_delta(treated: dict, control: dict) -> dict[str, float]:
    t = dict(treated.get("outcome_scores") or {})
    c = dict(control.get("outcome_scores") or {})
    common = sorted(set(t) & set(c) & set(OUTCOME_SCORES))
    return {metric: round(float(t[metric]) - float(c[metric]), 9) for metric in common}


class NextScoutCounterfactualCreditRuntime:
    """Matched-pair quasi-experimental credit over delayed V7 outcome receipts.

    V8 does not convert observational history into proof of causation. It validates
    a stronger comparison membrane: distinct completed-focus outcome receipts,
    target-prep treatment contrast, independently sourced pre-treatment matching
    covariates, and explicit abstention when support is weak or inconsistent.
    Passing estimates are benefit-prior *candidates* only; they do not mutate the
    V5/V6 economy, claim work, promote evidence, merge code, or release artifacts.
    """

    def __init__(self, pipeline: RollingQuestPipelineRuntime, breadth: NextQuestBreadthRuntime,
                 outcomes: NextScoutOutcomeValueRuntime):
        self.pipeline = pipeline
        self.breadth = breadth
        self.outcomes = outcomes
        self.git = pipeline.git
        self.prompt_runtime = pipeline.prompt_runtime

    def _paths(self, pipeline_id: str) -> dict[str, str]:
        base = _root(pipeline_id)
        return {"base": base, "pairs": f"{base}/pairs"}

    def _read_pairs(self, pipeline_id: str) -> list[dict]:
        root = self.prompt_runtime._safe_rel(self._paths(pipeline_id)["pairs"])
        if not root.is_dir():
            return []
        rows: list[dict] = []
        for path in sorted(root.glob("*.json")):
            row = json.loads(path.read_text(encoding="utf-8"))
            if row.get("artifact") != PAIR_ARTIFACT or row.get("pipeline_id") != pipeline_id:
                continue
            basis = {k: v for k, v in row.items() if k != "pair_digest"}
            if _digest(basis) != row.get("pair_digest"):
                raise ValueError(f"COUNTERFACTUAL_PAIR_DIGEST_HOLD:{path.name}")
            rows.append(row)
        return rows

    def _receipt_map(self, pipeline_id: str) -> dict[str, dict]:
        return {str(r.get("receipt_id")): r for r in self.outcomes._read_receipts(pipeline_id)}

    def record_pair(
        self,
        *,
        pipeline_id: str,
        prep_kind: str,
        treated_receipt_id: str,
        control_receipt_id: str,
        matching_basis: dict,
        expected_git_head: str,
        actor: str = "agent",
    ) -> dict:
        prep_kind = str(prep_kind or "").upper()
        if prep_kind not in PREP_KINDS:
            raise ValueError("unsupported prep_kind")
        current = self.git.head()
        if current != expected_git_head:
            raise ValueError("STALE_GIT_HEAD_FOR_COUNTERFACTUAL_PAIR")
        receipts = self._receipt_map(pipeline_id)
        treated = receipts.get(str(treated_receipt_id))
        control = receipts.get(str(control_receipt_id))
        if not treated or not control:
            raise ValueError("COUNTERFACTUAL_PAIR_REQUIRES_EXISTING_V7_RECEIPTS")
        if treated_receipt_id == control_receipt_id:
            raise ValueError("COUNTERFACTUAL_PAIR_REQUIRES_DISTINCT_RECEIPTS")
        tq = str((treated.get("quest") or {}).get("quest_id") or "")
        cq = str((control.get("quest") or {}).get("quest_id") or "")
        if not tq or tq == cq:
            raise ValueError("COUNTERFACTUAL_PAIR_REQUIRES_DISTINCT_QUESTS")
        if prep_kind not in _prep_kinds(treated):
            raise ValueError("TREATED_RECEIPT_LACKS_TARGET_PREP")
        if prep_kind in _prep_kinds(control):
            raise ValueError("CONTROL_RECEIPT_CONTAINS_TARGET_PREP")

        if not isinstance(matching_basis, dict):
            raise ValueError("matching_basis must be an object")
        if matching_basis.get("observed") is not True:
            raise ValueError("matching_basis requires observed=true")
        source = str(matching_basis.get("source") or "").strip()
        if not source:
            raise ValueError("matching_basis requires a non-empty source")
        if matching_basis.get("independent_of_scout") is not True:
            raise ValueError("matching_basis requires independent_of_scout=true")
        covariates = matching_basis.get("pre_treatment_covariates")
        if not isinstance(covariates, dict) or not covariates:
            raise ValueError("matching_basis requires non-empty pre_treatment_covariates")
        if _contains_forbidden_key(covariates):
            raise ValueError("POST_TREATMENT_MATCHING_COVARIATE_FORBIDDEN")
        treated_cov = covariates.get("treated")
        control_cov = covariates.get("control")
        if not isinstance(treated_cov, dict) or not isinstance(control_cov, dict) or not treated_cov or not control_cov:
            raise ValueError("pre_treatment_covariates requires treated/control objects")
        if set(treated_cov) != set(control_cov):
            raise ValueError("MATCHING_COVARIATE_SCHEMA_MISMATCH")
        if _digest(treated_cov) != _digest(control_cov):
            raise ValueError("PRE_TREATMENT_COVARIATES_DO_NOT_EXACTLY_MATCH")

        deltas = _score_delta(treated, control)
        if not deltas:
            raise ValueError("COUNTERFACTUAL_PAIR_HAS_NO_COMMON_OUTCOME_SCORE")
        matching = {
            "observed": True,
            "source": source,
            "independent_of_scout": True,
            "pre_treatment_covariates": {"treated": treated_cov, "control": control_cov},
            "covariate_digest": _digest(treated_cov),
        }
        pair_id = "NCP-" + _digest({
            "pipeline_id": pipeline_id,
            "prep_kind": prep_kind,
            "treated_receipt_id": treated_receipt_id,
            "control_receipt_id": control_receipt_id,
            "matching": matching,
        })[:24]
        path = f"{self._paths(pipeline_id)['pairs']}/{pair_id}.json"
        existing_path = self.prompt_runtime._safe_rel(path)
        if existing_path.is_file():
            existing = json.loads(existing_path.read_text(encoding="utf-8"))
            return {"status": "REUSED", "pair": existing, "git_mutation": False,
                    "law": "SAME_COUNTERFACTUAL_IDENTITY => SAME_PAIR"}

        pair = {
            "artifact": PAIR_ARTIFACT,
            "pair_id": pair_id,
            "pipeline_id": pipeline_id,
            "prep_kind": prep_kind,
            "treated_receipt_id": treated_receipt_id,
            "control_receipt_id": control_receipt_id,
            "treated_quest_id": tq,
            "control_quest_id": cq,
            "matching_basis": matching,
            "outcome_delta": deltas,
            "created_at": _utcnow(),
            "actor": actor,
            "standing": "MATCHED_OBSERVATIONAL_CONTRAST",
            "causal_proof": False,
            "authority": "COUNTERFACTUAL_ANALYSIS_ONLY",
            "laws": [
                "POST_TREATMENT_VARIABLES_CANNOT_DEFINE_MATCHES",
                "SCOUT_SELF_REPORT != MATCHING_AUTHORITY",
                "MATCHED_OBSERVATIONAL_CONTRAST != RANDOMIZED_CAUSAL_PROOF",
                "COUNTERFACTUAL_PAIR != BENEFIT_PRIOR_UPDATE",
            ],
        }
        pair["pair_digest"] = _digest(pair)
        commit = self.prompt_runtime._commit_files(
            current, {path: json.dumps(pair, indent=2, sort_keys=True) + "\n"}, actor,
            f"record NEXT V8 counterfactual pair {pair_id}",
        )
        return {"status": "RECORDED", "pair": pair, "checkpoint_head": commit["head"], "git": commit,
                "authority": "COUNTERFACTUAL_ANALYSIS_ONLY"}

    def estimate(
        self,
        *,
        pipeline_id: str,
        prep_kind: str,
        prior_strength: int = 3,
        min_pairs: int = 3,
        min_sign_consistency: float = 2.0 / 3.0,
        min_effect: float = 0.05,
    ) -> dict:
        prep_kind = str(prep_kind or "").upper()
        if prep_kind not in PREP_KINDS:
            raise ValueError("unsupported prep_kind")
        prior_strength = int(prior_strength)
        min_pairs = int(min_pairs)
        min_sign_consistency = float(min_sign_consistency)
        min_effect = float(min_effect)
        if not 1 <= prior_strength <= 100:
            raise ValueError("prior_strength must be between 1 and 100")
        if not 2 <= min_pairs <= 1000:
            raise ValueError("min_pairs must be between 2 and 1000")
        if not 0.5 <= min_sign_consistency <= 1.0:
            raise ValueError("min_sign_consistency must be between 0.5 and 1")
        if not 0.0 <= min_effect <= 1.0:
            raise ValueError("min_effect must be between 0 and 1")

        pairs = [p for p in self._read_pairs(pipeline_id) if p.get("prep_kind") == prep_kind]
        # A receipt may not be reused on the same side to manufacture pseudo-replication.
        treated_ids = [p.get("treated_receipt_id") for p in pairs]
        control_ids = [p.get("control_receipt_id") for p in pairs]
        independence_hold = len(treated_ids) != len(set(treated_ids)) or len(control_ids) != len(set(control_ids))

        metrics: dict[str, dict] = {}
        for metric in OUTCOME_SCORES:
            values = [float(p["outcome_delta"][metric]) for p in pairs if metric in (p.get("outcome_delta") or {})]
            n = len(values)
            if values:
                median = float(statistics.median(values))
                positive = sum(1 for v in values if v > 0)
                negative = sum(1 for v in values if v < 0)
                zero = sum(1 for v in values if v == 0)
                directional = max(positive, negative) / n
                shrunk = (n * median) / (prior_strength + n)  # zero-effect prior
            else:
                median, positive, negative, zero, directional, shrunk = None, 0, 0, 0, 0.0, 0.0
            passed = bool(
                not independence_hold
                and n >= min_pairs
                and directional >= min_sign_consistency
                and median is not None
                and median >= min_effect
            )
            metrics[metric] = {
                "pairs": n,
                "median_delta": None if median is None else round(median, 6),
                "positive": positive,
                "negative": negative,
                "zero": zero,
                "sign_consistency": round(directional, 6),
                "shrunk_effect_candidate": round(shrunk, 6),
                "passes_candidate_gate": passed,
            }

        passing = [name for name, row in metrics.items() if row["passes_candidate_gate"]]
        standing = "BENEFIT_PRIOR_CANDIDATE" if passing else "ABSTAIN_INSUFFICIENT_COUNTERFACTUAL_SUPPORT"
        basis = {
            "artifact": ESTIMATE_ARTIFACT,
            "pipeline_id": pipeline_id,
            "prep_kind": prep_kind,
            "pair_count": len(pairs),
            "unique_treated_count": len(set(treated_ids)),
            "unique_control_count": len(set(control_ids)),
            "independence_hold": independence_hold,
            "prior_strength": prior_strength,
            "min_pairs": min_pairs,
            "min_sign_consistency": min_sign_consistency,
            "min_effect": min_effect,
            "metrics": metrics,
            "passing_metrics": passing,
            "standing": standing,
            "causal_proof": False,
            "benefit_prior_mutation": "NONE",
            "allocation_effect": "NONE",
            "authority": "COUNTERFACTUAL_ANALYSIS_ONLY",
        }
        return {**basis, "estimate_digest": _digest(basis), "laws": [
            "MATCHED_OBSERVATIONAL_ESTIMATE != RANDOMIZED_CAUSAL_PROOF",
            "PSEUDOREPLICATION => ABSTAIN",
            "WEAK_OR_INCONSISTENT_EFFECT => ABSTAIN",
            "V8_CANDIDATE != LIVE_ECONOMY_MUTATION",
        ]}

    def overlay(self, *, pipeline_id: str, prior_strength: int = 3, min_pairs: int = 3,
                min_sign_consistency: float = 2.0 / 3.0, min_effect: float = 0.05) -> dict:
        estimates = {
            kind: self.estimate(
                pipeline_id=pipeline_id,
                prep_kind=kind,
                prior_strength=prior_strength,
                min_pairs=min_pairs,
                min_sign_consistency=min_sign_consistency,
                min_effect=min_effect,
            ) for kind in PREP_KINDS
        }
        candidates = {}
        for kind, estimate in estimates.items():
            passed = [estimate["metrics"][m]["shrunk_effect_candidate"] for m in estimate["passing_metrics"]]
            if passed:
                candidates[kind] = {
                    "candidate": True,
                    "effect_index": round(sum(passed) / len(passed), 6),
                    "passing_metrics": list(estimate["passing_metrics"]),
                    "estimate_digest": estimate["estimate_digest"],
                }
            else:
                candidates[kind] = {
                    "candidate": False,
                    "effect_index": 0.0,
                    "passing_metrics": [],
                    "estimate_digest": estimate["estimate_digest"],
                }
        basis = {
            "artifact": OVERLAY_ARTIFACT,
            "pipeline_id": pipeline_id,
            "benefit_prior_candidates": candidates,
            "standing": "COUNTERFACTUAL_CANDIDATE_OVERLAY_ONLY",
            "benefit_prior_mutation": "NONE",
            "allocation_effect": "NONE",
            "claim_effect": "NONE",
            "promotion_effect": "NONE",
        }
        return {**basis, "overlay_digest": _digest(basis),
                "law": "V8_MAY_PROPOSE_BENEFIT_PRIOR_CANDIDATES_BUT_CANNOT_INSTALL_THEM"}

    def call_tool(self, name: str, a: dict) -> dict:
        if name == TOOLS["pair"]:
            return self.record_pair(
                pipeline_id=a["pipeline_id"], prep_kind=a["prep_kind"],
                treated_receipt_id=a["treated_receipt_id"], control_receipt_id=a["control_receipt_id"],
                matching_basis=a["matching_basis"], expected_git_head=a["expected_git_head"],
                actor=a.get("actor", "agent"),
            )
        if name == TOOLS["estimate"]:
            return self.estimate(
                pipeline_id=a["pipeline_id"], prep_kind=a["prep_kind"],
                prior_strength=a.get("prior_strength", 3), min_pairs=a.get("min_pairs", 3),
                min_sign_consistency=a.get("min_sign_consistency", 2.0 / 3.0),
                min_effect=a.get("min_effect", 0.05),
            )
        if name == TOOLS["overlay"]:
            return self.overlay(
                pipeline_id=a["pipeline_id"], prior_strength=a.get("prior_strength", 3),
                min_pairs=a.get("min_pairs", 3), min_sign_consistency=a.get("min_sign_consistency", 2.0 / 3.0),
                min_effect=a.get("min_effect", 0.05),
            )
        raise KeyError(name)


NEXT_SCOUT_COUNTERFACTUAL_TOOLS = [
    {"name": TOOLS["pair"], "description": "Record one exact-matched V8 treated/control contrast between completed-focus V7 outcome receipts. Matching must be independently sourced, pre-treatment, and exact; post-treatment matching is rejected.",
     "inputSchema": {"type": "object", "required": ["pipeline_id", "prep_kind", "treated_receipt_id", "control_receipt_id", "matching_basis", "expected_git_head"],
                     "properties": {"pipeline_id": {"type": "string"}, "prep_kind": {"type": "string"}, "treated_receipt_id": {"type": "string"}, "control_receipt_id": {"type": "string"}, "matching_basis": {"type": "object"}, "expected_git_head": {"type": "string"}, "actor": {"type": "string"}}, "additionalProperties": False}},
    {"name": TOOLS["estimate"], "description": "Estimate a conservative V8 matched observational effect candidate for one prep kind. Reused treated/control receipts trigger pseudoreplication abstention; weak support never updates benefit priors.",
     "inputSchema": {"type": "object", "required": ["pipeline_id", "prep_kind"],
                     "properties": {"pipeline_id": {"type": "string"}, "prep_kind": {"type": "string"}, "prior_strength": {"type": "integer", "minimum": 1, "maximum": 100}, "min_pairs": {"type": "integer", "minimum": 2, "maximum": 1000}, "min_sign_consistency": {"type": "number", "minimum": 0.5, "maximum": 1.0}, "min_effect": {"type": "number", "minimum": 0.0, "maximum": 1.0}}, "additionalProperties": False}},
    {"name": TOOLS["overlay"], "description": "Return V8 benefit-prior candidates across prep kinds. This overlay is explanatory/candidate-only and cannot mutate the V5/V6 economy or allocation.",
     "inputSchema": {"type": "object", "required": ["pipeline_id"],
                     "properties": {"pipeline_id": {"type": "string"}, "prior_strength": {"type": "integer", "minimum": 1, "maximum": 100}, "min_pairs": {"type": "integer", "minimum": 2, "maximum": 1000}, "min_sign_consistency": {"type": "number", "minimum": 0.5, "maximum": 1.0}, "min_effect": {"type": "number", "minimum": 0.0, "maximum": 1.0}}, "additionalProperties": False}},
]
NEXT_SCOUT_COUNTERFACTUAL_TOOL_NAMES = {x["name"] for x in NEXT_SCOUT_COUNTERFACTUAL_TOOLS}


def install_next_scout_counterfactual_credit_extension(prompt_runtime_cls, tool_list: list[dict], tool_names: set[str]) -> None:
    if getattr(prompt_runtime_cls, "_athena_next_scout_counterfactual_v8_registered", False):
        return
    previous_call = prompt_runtime_cls.call_tool

    def call_with_counterfactual(self, name, arguments):
        if name in NEXT_SCOUT_COUNTERFACTUAL_TOOL_NAMES:
            runtime = getattr(self, "_next_scout_counterfactual_runtime_v8", None)
            if runtime is None:
                pipeline = getattr(self, "_next_pipeline_runtime_v1", None)
                if pipeline is None:
                    pipeline = RollingQuestPipelineRuntime(self.git, self)
                    self._next_pipeline_runtime_v1 = pipeline
                breadth = getattr(self, "_next_pipeline_breadth_runtime_v2", None)
                if breadth is None:
                    breadth = NextQuestBreadthRuntime(pipeline)
                    self._next_pipeline_breadth_runtime_v2 = breadth
                outcomes = getattr(self, "_next_scout_outcome_value_runtime_v7", None)
                if outcomes is None:
                    outcomes = NextScoutOutcomeValueRuntime(pipeline, breadth)
                    self._next_scout_outcome_value_runtime_v7 = outcomes
                runtime = NextScoutCounterfactualCreditRuntime(pipeline, breadth, outcomes)
                self._next_scout_counterfactual_runtime_v8 = runtime
            return runtime.call_tool(name, arguments or {})
        return previous_call(self, name, arguments)

    prompt_runtime_cls.call_tool = call_with_counterfactual
    prompt_runtime_cls._athena_next_scout_counterfactual_v8_registered = True
    for tool in NEXT_SCOUT_COUNTERFACTUAL_TOOLS:
        if tool["name"] not in tool_names:
            tool_list.append(tool)
            tool_names.add(tool["name"])
