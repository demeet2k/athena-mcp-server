from __future__ import annotations

from .next_quest_pipeline_breadth import (
    NextQuestBreadthRuntime,
    _packet_digest,
    _plan_id,
)


def _planned_identity_basis(packet: dict) -> dict:
    basis = dict(packet)
    # Observation annotations belong to the plan ledger state, not to the
    # immutable PLANNED packet identity that originally minted packet_digest.
    if basis.get("status") in {"OBSERVED", "HOLD"}:
        basis["status"] = "PLANNED"
        basis.pop("result_digest", None)
        basis.pop("updated_at", None)
    return basis


def install_next_pipeline_breadth_idempotency_hardening() -> None:
    if getattr(NextQuestBreadthRuntime, "_athena_breadth_idempotency_v2_registered", False):
        return

    original_plan = NextQuestBreadthRuntime.plan

    def plan_idempotent(
        self,
        *,
        pipeline_id: str,
        expected_pipeline_state_digest: str,
        expected_git_head: str,
        kinds=None,
        actor: str = "agent",
    ):
        pipeline_state = self.pipeline.state(pipeline_id)
        if pipeline_state.get("state_digest") != expected_pipeline_state_digest:
            raise ValueError("STALE_PIPELINE_STATE_FOR_BREADTH_PLAN")
        staged = self._staged(pipeline_state["window"])
        if len(staged) != 2:
            raise ValueError("breadth planning requires exactly Q2 and Q3 staged quests")
        kinds_clean = self._validate_kinds(kinds)
        breadth, _ = self._read_breadth(pipeline_id)
        existing = dict(breadth.get("plans") or {})
        desired_ids = [
            _plan_id(pipeline_id, quest["quest_id"], kind, expected_pipeline_state_digest)
            for quest in staged
            for kind in kinds_clean
        ]
        present = [plan_id for plan_id in desired_ids if plan_id in existing]
        if present and len(present) != len(desired_ids):
            raise ValueError("PARTIAL_PREP_PLAN_SET_HOLD")
        if present:
            current = self.git.head()
            if current != expected_git_head:
                raise ValueError("STALE_GIT_HEAD_FOR_BREADTH_REUSE")
            rows = []
            for plan_id in desired_ids:
                packet = dict(existing[plan_id])
                if packet.get("plan_id") != plan_id:
                    raise ValueError("PREP_PLAN_IDENTITY_HOLD")
                if packet.get("pipeline_state_digest") != expected_pipeline_state_digest:
                    raise ValueError("PREP_PLAN_STATE_BINDING_HOLD")
                if packet.get("packet_digest") != _packet_digest(_planned_identity_basis(packet)):
                    raise ValueError("PREP_PLAN_DIGEST_HOLD")
                rows.append(packet)
            return {
                "status": "REUSED",
                "pipeline_id": pipeline_id,
                "pipeline_state_digest": expected_pipeline_state_digest,
                "staged_quests": staged,
                "plans": rows,
                "plan_count": len(rows),
                "reused": True,
                "git_mutation": False,
                "checkpoint_head": current,
                "breadth_state_digest": breadth.get("state_digest"),
                "revision": breadth.get("revision", 0),
                "authority": "PREPARATION_ONLY",
                "law": "SAME_PREP_IDENTITY => REUSE_EXISTING_PACKET_SET_WITHOUT_MUTATION",
            }
        return original_plan(
            self,
            pipeline_id=pipeline_id,
            expected_pipeline_state_digest=expected_pipeline_state_digest,
            expected_git_head=expected_git_head,
            kinds=kinds_clean,
            actor=actor,
        )

    NextQuestBreadthRuntime.plan = plan_idempotent
    NextQuestBreadthRuntime._athena_breadth_idempotency_v2_registered = True


__all__ = ["install_next_pipeline_breadth_idempotency_hardening"]
