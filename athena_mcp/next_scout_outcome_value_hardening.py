from __future__ import annotations

import json

from .next_scout_outcome_value import NextScoutOutcomeValueRuntime, METRICS, OUTCOME_ARTIFACT, _digest, _measurement, _scores, _utcnow


def install_next_scout_outcome_value_completion_ledger_hardening() -> None:
    """Make V7 outcome recording read the exact persisted completion ledger.

    `RollingQuestPipelineRuntime.state()` is a bounded public projection and exposes
    only `completed_count` + `completed_tail`. V7 needs the exact persisted
    `completed[]` ledger to bind an arbitrary historical quest. This hardening keeps
    that full ledger private and validates its state digest before attribution.
    """
    cls = NextScoutOutcomeValueRuntime
    if getattr(cls, "_athena_v7_exact_completion_ledger_hardened", False):
        return

    def record(self, *, pipeline_id: str, quest_id: str, expected_pipeline_state_digest: str,
               expected_git_head: str, measurements: dict, actor: str = "agent") -> dict:
        state, _ = self.pipeline._read_state(pipeline_id)
        # Use the same canonical state digest law as the rolling pipeline without
        # broadening the public state projection.
        from .next_quest_pipeline import _state_digest
        if state.get("state_digest") != expected_pipeline_state_digest or _state_digest(state) != state.get("state_digest"):
            raise ValueError("STALE_PIPELINE_STATE_FOR_FOCUS_OUTCOME")
        current = self.git.head()
        if current != expected_git_head:
            raise ValueError("STALE_GIT_HEAD_FOR_FOCUS_OUTCOME")

        completed = next((dict(x) for x in state.get("completed") or [] if str(x.get("quest_id")) == quest_id), None)
        if not completed:
            raise ValueError("OUTCOME_REQUIRES_COMPLETED_FOCUS_QUEST")
        if str(completed.get("completion_status") or "") not in {"SUCCEEDED", "PARTIAL", "HELD", "FAILED", "NO_PROGRESS"}:
            raise ValueError("COMPLETED_QUEST_HAS_UNSUPPORTED_STATUS")

        breadth, _ = self.breadth._read_breadth(pipeline_id)
        plans = dict(breadth.get("plans") or {})
        observations = dict(breadth.get("observations") or {})
        associated = []
        for plan_id, observation in sorted(observations.items()):
            plan = plans.get(plan_id) or {}
            if str((plan.get("quest") or {}).get("quest_id")) != quest_id:
                continue
            associated.append({
                "plan_id": plan_id,
                "kind": plan.get("kind"),
                "plan_digest": plan.get("packet_digest"),
                "observation_digest": observation.get("result_digest") or observation.get("packet_digest"),
            })
        if not associated:
            raise ValueError("OUTCOME_VALUE_REQUIRES_PREFOCUS_PREP_OBSERVATIONS")

        clean = {}
        for name in METRICS:
            row = _measurement(name, (measurements or {}).get(name))
            if row is not None:
                clean[name] = row
        if not clean:
            raise ValueError("at least one observed downstream metric is required")

        completed_basis = {
            "quest_id": completed.get("quest_id"),
            "ordinal": completed.get("ordinal"),
            "task": completed.get("task"),
            "completion_status": completed.get("completion_status"),
            "completion_summary": completed.get("completion_summary"),
            "completed_at": completed.get("completed_at"),
            "evidence_refs": completed.get("evidence_refs") or [],
        }
        receipt_id = "NVO-" + _digest({
            "pipeline_id": pipeline_id,
            "quest": completed_basis,
            "associated_plan_ids": [x["plan_id"] for x in associated],
            "measurements": clean,
        })[:24]
        path = f"{self._paths(pipeline_id)['receipts']}/{receipt_id}.json"
        existing_path = self.prompt_runtime._safe_rel(path)
        if existing_path.is_file():
            existing = json.loads(existing_path.read_text(encoding="utf-8"))
            return {"status": "REUSED", "receipt": existing, "git_mutation": False,
                    "law": "SAME_OUTCOME_IDENTITY => SAME_RECEIPT"}

        receipt = {
            "artifact": OUTCOME_ARTIFACT,
            "receipt_id": receipt_id,
            "pipeline_id": pipeline_id,
            "pipeline_state_digest": expected_pipeline_state_digest,
            "git_head_before": current,
            "quest": completed_basis,
            "associated_prep": associated,
            "measurements": clean,
            "outcome_scores": _scores(clean),
            "created_at": _utcnow(),
            "actor": actor,
            "standing": "OBSERVED_DOWNSTREAM_ASSOCIATION",
            "authority": "ASSOCIATIONAL_ROUTING_ONLY",
            "causal_effect": False,
            "laws": [
                "SCOUT_SELF_REPORT != VALUE_EVIDENCE",
                "OBSERVED_ASSOCIATION != CAUSAL_EFFECT",
                "FOCUS_OUTCOME != PREP_CAUSAL_CREDIT",
                "OUTCOME_RECEIPT != EVIDENCE_PROMOTION",
                "EXACT_COMPLETION_LEDGER != BOUNDED_PUBLIC_PROJECTION",
            ],
        }
        receipt["receipt_digest"] = _digest(receipt)
        commit = self.prompt_runtime._commit_files(
            current,
            {path: json.dumps(receipt, indent=2, sort_keys=True) + "\n"},
            actor,
            f"record NEXT focus outcome {quest_id}",
        )
        return {
            "status": "RECORDED",
            "receipt": receipt,
            "checkpoint_head": commit["head"],
            "git": commit,
            "authority": "ASSOCIATIONAL_ROUTING_ONLY",
        }

    cls.record = record
    cls._athena_v7_exact_completion_ledger_hardened = True


__all__ = ["install_next_scout_outcome_value_completion_ledger_hardening"]
