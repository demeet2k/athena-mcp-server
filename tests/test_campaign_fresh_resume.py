from __future__ import annotations

import unittest

from athena_mcp.campaign_fresh_resume import fresh_resume_branch
from athena_mcp.rehydration_campaign import BATON_ARTIFACT
from athena_mcp.rehydration_loop import _sha


class _Git:
    def __init__(self, head: str = "work-head"):
        self._head = head

    def head(self):
        return self._head


class _Loop:
    def __init__(self, *, state=None, resume_status="RESUMED", verify_status="PASS", checkpoint="loop-cp"):
        self.state = state or {
            "loop_id": "LOOP-1",
            "state_digest": "loop-state",
            "chain_digest": "loop-chain",
            "step_index": 2,
            "status": "ACTIVE",
            "last_completion": None,
        }
        self.resume_status = resume_status
        self.verify_status = verify_status
        self.checkpoint = checkpoint

    def resume(self, loop_id, include_prompt=False):
        return {
            "status": self.resume_status,
            "loop_id": loop_id,
            "state_integrity": self.resume_status == "RESUMED",
            "prompt_integrity": self.resume_status == "RESUMED",
        }

    def verify(self, loop_id):
        return {
            "status": self.verify_status,
            "loop_id": loop_id,
            "failures": [] if self.verify_status == "PASS" else ["TEST_HOLD"],
        }

    def _read_state(self, loop_id):
        return dict(self.state), {"state": f"prompts/rehydration/{loop_id}/state.json"}

    def _path_last_commit(self, rel):
        return self.checkpoint


class _Runtime:
    def __init__(
        self,
        *,
        before=None,
        after=None,
        before_checkpoint="camp-cp",
        after_checkpoint="camp-cp",
        shared_fresh=True,
        loop=None,
        bad_ancestor=None,
    ):
        self.before = before or _campaign_state()
        self.after = after or self.before
        self.before_checkpoint = before_checkpoint
        self.after_checkpoint = after_checkpoint
        self.shared_fresh = shared_fresh
        self.loop_runtime = loop or _Loop()
        self.git = _Git()
        self._reads = 0
        self._checkpoint_reads = 0
        self.bad_ancestor = bad_ancestor

    def _read_state(self, campaign_id):
        self._reads += 1
        value = self.before if self._reads == 1 else self.after
        return dict(value), {"state": f"prompts/rehydration_campaigns/{campaign_id}/state.json"}

    def _assert_state(self, state, expected_state_digest):
        if state.get("state_digest") != expected_state_digest:
            raise ValueError("STALE_OR_TAMPERED_CAMPAIGN_STATE")
        if state.get("status") in {"COMPLETE", "ABORTED"}:
            raise ValueError("campaign is terminal")

    def _path_last_commit(self, rel):
        self._checkpoint_reads += 1
        return self.before_checkpoint if self._checkpoint_reads == 1 else self.after_checkpoint

    def _remote_mode(self, value):
        mode = str(value or "REQUIRED").upper()
        if mode not in {"REQUIRED", "BEST_EFFORT", "DISABLED"}:
            raise ValueError("bad mode")
        return mode

    def _sync(self, mode, remote):
        return {
            "status": "UP_TO_DATE" if self.shared_fresh else "UNVERIFIED",
            "shared_frontier_verified": self.shared_fresh,
            "remote": remote,
        }

    def _is_ancestor(self, older, newer):
        return (older, newer) != self.bad_ancestor


def _loop_binding(**updates):
    value = {
        "loop_id": "LOOP-1",
        "state_digest": "loop-state",
        "chain_digest": "loop-chain",
        "checkpoint_head": "loop-cp",
        "step_index": 2,
        "status": "ACTIVE",
    }
    value.update(updates)
    return value


def _campaign_state(*, loop_binding=None, digest="camp-state"):
    if loop_binding is None:
        loop_binding = _loop_binding()
    return {
        "artifact": "ATHENA.REHYDRATION.CAMPAIGN.V2",
        "campaign_id": "RHC-TEST",
        "status": "ACTIVE",
        "state_digest": digest,
        "branches": {
            "CB-1": {
                "branch_id": "CB-1",
                "status": "ACTIVE",
                "loop": loop_binding,
            }
        },
    }


def _resume(runtime):
    return fresh_resume_branch(
        runtime,
        campaign_id="RHC-TEST",
        branch_id="CB-1",
        expected_state_digest="camp-state",
        expected_checkpoint_head="camp-cp",
    )


def _valid_baton():
    baton = {
        "artifact": BATON_ARTIFACT,
        "status": "SELECTED",
        "loop_id": "LOOP-1",
        "from_step": 2,
        "goal": "continue the campaign",
        "current_task": "completed task",
        "policy": {"authority": "ROUTING_ONLY"},
        "candidates": [],
        "pareto_candidate_ids": [],
        "selected": None,
        "ties": [],
        "deferred_candidate_ids": [],
        "selection_reason": "test",
        "laws": ["ROUTING_SCORE != AUTHORITY"],
    }
    baton["baton_digest"] = _sha(baton)
    return baton


class CampaignFreshResumeTests(unittest.TestCase):
    def test_aligned_active_is_read_only_and_fresh(self):
        result = _resume(_Runtime())
        self.assertEqual("ALIGNED_ACTIVE", result["status"])
        self.assertTrue(result["read_only"])
        self.assertTrue(result["shared_fresh"])
        self.assertFalse(result["execution_authority"])
        self.assertEqual("CONTINUE_BOUND_LOOP", result["next"])

    def test_missing_bound_loop_holds(self):
        state = _campaign_state(loop_binding={})
        result = _resume(_Runtime(before=state, after=state))
        self.assertEqual("HOLD_NO_BOUND_LOOP", result["status"])
        self.assertEqual("BIND_V1_LOOP_BEFORE_RESUME", result["next"])

    def test_loop_drift_requires_explicit_campaign_sync(self):
        loop = _Loop(checkpoint="loop-new")
        result = _resume(_Runtime(loop=loop))
        self.assertEqual("SYNC_BRANCH_REQUIRED", result["status"])
        self.assertIn("checkpoint_head", result["drift_fields"])
        self.assertEqual("CALL_CAMPAIGN_SYNC_BRANCH_THEN_RETRY", result["next"])

    def test_loop_replay_hold_fails_closed(self):
        result = _resume(_Runtime(loop=_Loop(verify_status="HOLD")))
        self.assertEqual("HOLD_LOOP_VERIFY", result["status"])
        self.assertEqual("REPAIR_LOOP_REPLAY", result["next"])

    def test_unverified_shared_freshness_holds_before_loop_read(self):
        result = _resume(_Runtime(shared_fresh=False))
        self.assertEqual("HOLD_SHARED_FRESHNESS", result["status"])
        self.assertFalse(result["shared_fresh"])

    def test_campaign_move_during_sync_holds(self):
        moved = _campaign_state(digest="camp-state-new")
        result = _resume(_Runtime(after=moved, after_checkpoint="camp-cp-new"))
        self.assertEqual("HOLD_CAMPAIGN_STATE_MOVED", result["status"])
        self.assertEqual("camp-state-new", result["current_state_digest"])

    def test_campaign_checkpoint_must_remain_ancestor_of_current_head(self):
        result = _resume(_Runtime(bad_ancestor=("camp-cp", "work-head")))
        self.assertEqual("HOLD_CAMPAIGN_ANCESTRY", result["status"])

    def test_loop_checkpoint_must_remain_ancestor_of_current_head(self):
        result = _resume(_Runtime(bad_ancestor=("loop-cp", "work-head")))
        self.assertEqual("HOLD_LOOP_ANCESTRY", result["status"])

    def test_complete_loop_with_valid_baton_exposes_handoff_not_authority(self):
        loop_state = {
            "loop_id": "LOOP-1",
            "state_digest": "loop-state",
            "chain_digest": "loop-chain",
            "step_index": 2,
            "status": "COMPLETE",
            "last_completion": {"successor_baton": _valid_baton()},
        }
        loop = _Loop(state=loop_state)
        state = _campaign_state(loop_binding=_loop_binding(status="COMPLETE"))
        result = _resume(_Runtime(before=state, after=state, loop=loop))
        self.assertEqual("HANDOFF_AVAILABLE", result["status"])
        self.assertEqual("ROUTE_SUCCESSOR_BATON", result["next"])
        self.assertIsNotNone(result["successor_baton"])
        self.assertFalse(result["execution_authority"])

    def test_complete_loop_without_valid_baton_is_not_campaign_success(self):
        loop_state = {
            "loop_id": "LOOP-1",
            "state_digest": "loop-state",
            "chain_digest": "loop-chain",
            "step_index": 2,
            "status": "COMPLETE",
            "last_completion": {"successor_baton": None},
        }
        loop = _Loop(state=loop_state)
        state = _campaign_state(loop_binding=_loop_binding(status="COMPLETE"))
        result = _resume(_Runtime(before=state, after=state, loop=loop))
        self.assertEqual("ALIGNED_COMPLETE_NO_HANDOFF", result["status"])
        self.assertIn("TERMINAL_LOOP != CAMPAIGN_SUCCESS", result["laws"])


if __name__ == "__main__":
    unittest.main()
