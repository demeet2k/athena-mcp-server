from __future__ import annotations

import inspect
import unittest

from athena_mcp.rehydration_campaign import RehydrationCampaignRuntime
from athena_mcp.steering_binding import bind_campaign_branch_to_loop


class _Git:
    def __init__(self, head: str = "H0"):
        self.value = head

    def head(self) -> str:
        return self.value

    def advance(self, value: str) -> None:
        self.value = value


class _Campaign:
    def __init__(self, git: _Git, *, move_on_claim: bool = True, fail_bind: bool = False):
        self.git = git
        self.move_on_claim = move_on_claim
        self.fail_bind = fail_bind
        self.claim_calls = []
        self.bind_calls = []

    def claim_branch(self, campaign_id, branch_id, actor, expected_campaign_digest):
        self.claim_calls.append(
            {
                "campaign_id": campaign_id,
                "branch_id": branch_id,
                "actor": actor,
                "expected_campaign_digest": expected_campaign_digest,
                "head_before": self.git.head(),
            }
        )
        if self.move_on_claim:
            self.git.advance("H1")
        return {"campaign_digest": "C1", "branch_id": branch_id}

    def bind_loop(
        self,
        campaign_id,
        branch_id,
        loop_id,
        expected_loop_state_digest,
        actor,
        expected_campaign_digest,
    ):
        self.bind_calls.append(
            {
                "campaign_id": campaign_id,
                "branch_id": branch_id,
                "loop_id": loop_id,
                "expected_loop_state_digest": expected_loop_state_digest,
                "actor": actor,
                "expected_campaign_digest": expected_campaign_digest,
                "head_before": self.git.head(),
            }
        )
        if self.fail_bind:
            raise RuntimeError("bind failed")
        if expected_campaign_digest != "C1":
            raise AssertionError("bind must use post-lease campaign digest")
        if expected_loop_state_digest != "S1":
            raise AssertionError("bind must use exact loop state digest")
        self.git.advance("H3")
        return {"campaign_digest": "C2", "branch_id": branch_id, "loop_id": loop_id}


class _Loop:
    def __init__(self, git: _Git, *, fail_start: bool = False, bad_checkpoint: bool = False):
        self.git = git
        self.fail_start = fail_start
        self.bad_checkpoint = bad_checkpoint
        self.start_calls = []

    def start(self, **kwargs):
        self.start_calls.append(dict(kwargs))
        if self.fail_start:
            raise RuntimeError("loop start failed")
        if kwargs["expected_git_head"] != self.git.head():
            raise AssertionError(
                f"loop start expected stale head {kwargs['expected_git_head']} while current is {self.git.head()}"
            )
        if kwargs["expected_git_head"] != "H1":
            raise AssertionError("loop must start from post-campaign-lease head H1")
        self.git.advance("H2")
        return {
            "loop_id": "L1",
            "state_digest": "S1",
            "checkpoint_head": "OTHER" if self.bad_checkpoint else "H2",
        }


def _compilation(*, head: str = "H0", required_operation=None):
    candidate = {
        "candidate_id": "ledger-p001-s0001",
        "task": "Execute one bounded current residual.",
        "metrics": {"utility": 0.9},
        "source": {"kind": "STEERING_LEDGER_RESIDUAL", "pulse_index": 1, "step": 1},
        "required_capability_class": "FRONTIER_READ_SELECT" if required_operation else None,
        "required_operation": required_operation,
        "standing": "CAMPAIGN_CANDIDATE_NOT_EXECUTION_AUTHORITY",
    }
    return {
        "status": "RESIDUAL_CANDIDATES",
        "current_address": {"git_head": head, "shared_fresh": True},
        "candidates": [candidate],
    }


def _bind(campaign, loop, compilation=None, execution_surface=None, expected_git_head="H0"):
    return bind_campaign_branch_to_loop(
        campaign_runtime=campaign,
        loop_runtime=loop,
        campaign_id="CAMP1",
        branch_id="B1",
        expected_campaign_digest="C0",
        expected_git_head=expected_git_head,
        compilation=compilation or _compilation(head=expected_git_head),
        candidate_id="ledger-p001-s0001",
        actor="agent-a",
        execution_surface=execution_surface or {},
        shared_remote_mode="DISABLED",
        fetch=False,
        use_frontier=False,
    )


class SteeringBindingTests(unittest.TestCase):
    def test_success_binds_loop_using_post_lease_head_without_execution_authority(self):
        git = _Git("H0")
        campaign = _Campaign(git)
        loop = _Loop(git)
        result = _bind(campaign, loop)

        self.assertEqual(result["status"], "BOUND")
        self.assertEqual(result["pre_lease_head"], "H0")
        self.assertEqual(result["post_lease_head"], "H1")
        self.assertEqual(result["loop_start_expected_head"], "H1")
        self.assertEqual(result["post_loop_start_head"], "H2")
        self.assertEqual(result["post_bind_head"], "H3")
        self.assertEqual(loop.start_calls[0]["expected_git_head"], "H1")
        self.assertEqual(campaign.bind_calls[0]["head_before"], "H2")
        self.assertFalse(result["execution_authority_granted"])
        self.assertFalse(result["work_executed"])
        self.assertEqual(result["standing"], "BOUND_LOOP_NOT_WORK_EXECUTED")
        self.assertEqual(result["next"], "RESUME_EXPLICIT_LOOP_AND_EXECUTE_ONE_LAWFUL_CYCLE")

    def test_unexposed_required_operation_holds_before_campaign_mutation(self):
        git = _Git("H0")
        campaign = _Campaign(git)
        loop = _Loop(git)
        compilation = _compilation(required_operation="athena_frontier_claim")
        result = _bind(
            campaign,
            loop,
            compilation=compilation,
            execution_surface={"frontier_tools": ["athena_frontier_select"], "claim_tool_exposed": False},
        )
        self.assertEqual(result["status"], "HOLD")
        self.assertEqual(git.head(), "H0")
        self.assertEqual(campaign.claim_calls, [])
        self.assertEqual(loop.start_calls, [])
        self.assertEqual(result["holds"][0]["kind"], "UNEXPOSED_REQUIRED_OPERATION")

    def test_stale_pre_lease_head_holds_without_mutation(self):
        git = _Git("H1-current")
        campaign = _Campaign(git)
        loop = _Loop(git)
        result = _bind(campaign, loop, expected_git_head="H0")
        self.assertEqual(result["status"], "HOLD_INVALID_BINDING_INPUT")
        self.assertTrue(any(item.startswith("STALE_PRE_LEASE_HEAD:") for item in result["failures"]))
        self.assertEqual(campaign.claim_calls, [])
        self.assertEqual(loop.start_calls, [])

    def test_compilation_head_mismatch_holds_without_mutation(self):
        git = _Git("H0")
        campaign = _Campaign(git)
        loop = _Loop(git)
        result = _bind(campaign, loop, compilation=_compilation(head="OLD"), expected_git_head="H0")
        self.assertEqual(result["status"], "HOLD_INVALID_BINDING_INPUT")
        self.assertTrue(any(item.startswith("STALE_COMPILATION_HEAD:") for item in result["failures"]))
        self.assertEqual(campaign.claim_calls, [])

    def test_campaign_lease_must_advance_git_head(self):
        git = _Git("H0")
        campaign = _Campaign(git, move_on_claim=False)
        loop = _Loop(git)
        result = _bind(campaign, loop)
        self.assertEqual(result["status"], "HOLD_CAMPAIGN_LEASE_RECEIPT")
        self.assertIn("CAMPAIGN_LEASE_DID_NOT_ADVANCE_GIT_HEAD", result["failures"])
        self.assertEqual(loop.start_calls, [])

    def test_loop_start_failure_preserves_explicit_leased_not_bound_hold(self):
        git = _Git("H0")
        campaign = _Campaign(git)
        loop = _Loop(git, fail_start=True)
        result = _bind(campaign, loop)
        self.assertEqual(result["status"], "HOLD_LOOP_START_FAILED")
        self.assertEqual(result["post_lease_head"], "H1")
        self.assertEqual(result["standing"], "LEASED_NOT_BOUND")
        self.assertEqual(campaign.bind_calls, [])
        self.assertEqual(result["holds"][0]["kind"], "CAMPAIGN_BRANCH_LEASE_HELD_WITHOUT_LOOP")

    def test_loop_checkpoint_mismatch_holds_before_campaign_bind(self):
        git = _Git("H0")
        campaign = _Campaign(git)
        loop = _Loop(git, bad_checkpoint=True)
        result = _bind(campaign, loop)
        self.assertEqual(result["status"], "HOLD_LOOP_START_RECEIPT")
        self.assertTrue(any(item.startswith("LOOP_CHECKPOINT_HEAD_MISMATCH:") for item in result["failures"]))
        self.assertEqual(campaign.bind_calls, [])

    def test_bind_failure_preserves_existing_loop_and_forbids_duplicate_start(self):
        git = _Git("H0")
        campaign = _Campaign(git, fail_bind=True)
        loop = _Loop(git)
        result = _bind(campaign, loop)
        self.assertEqual(result["status"], "HOLD_CAMPAIGN_BIND_FAILED")
        self.assertEqual(result["loop_id"], "L1")
        self.assertEqual(len(loop.start_calls), 1)
        self.assertEqual(result["holds"][0]["kind"], "LOOP_STARTED_BUT_CAMPAIGN_UNBOUND")
        self.assertEqual(result["standing"], "LOOP_EXISTS_CAMPAIGN_UNBOUND")

    def test_actual_campaign_internal_methods_expose_required_semantic_slots(self):
        claim = inspect.signature(RehydrationCampaignRuntime.claim_branch).parameters
        bind = inspect.signature(RehydrationCampaignRuntime.bind_loop).parameters
        for name in ("campaign_id", "branch_id", "actor", "expected_campaign_digest"):
            self.assertIn(name, claim)
        for name in ("campaign_id", "branch_id", "loop_id", "actor", "expected_campaign_digest"):
            self.assertIn(name, bind)
        self.assertTrue(
            any(name in bind for name in ("loop_state_digest", "expected_loop_state_digest", "expected_loop_digest"))
        )


if __name__ == "__main__":
    unittest.main()
