from __future__ import annotations

import hashlib
import inspect
import json
import unittest

from athena_mcp.campaign_v3_binding import ARTIFACT, bind_current_pulse_branch_to_loop
from athena_mcp.campaign_v3_ledger import PULSE_ARTIFACT
from athena_mcp.rehydration_campaign import RehydrationCampaignRuntime
from athena_mcp.rehydration_loop import RehydrationLoopRuntime


def _sha(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


class _Git:
    def __init__(self, head: str = "H0"):
        self.value = head

    def head(self) -> str:
        return self.value


class _Campaign:
    def __init__(self, git: _Git, *, fail_claim: bool = False, fail_bind: bool = False, advance_claim: bool = True):
        self.git = git
        self.fail_claim = fail_claim
        self.fail_bind = fail_bind
        self.advance_claim = advance_claim
        self.claim_calls = []
        self.bind_calls = []

    def claim(self, **kwargs):
        self.claim_calls.append(kwargs)
        if self.fail_claim:
            raise ValueError("claim failed")
        if self.advance_claim:
            self.git.value = "H1"
        return {"status": "ACTIVE", "state_digest": "C1", "checkpoint_head": self.git.head()}

    def bind_loop(self, **kwargs):
        self.bind_calls.append(kwargs)
        if self.fail_bind:
            raise ValueError("bind failed")
        if kwargs["expected_checkpoint_head"] != "H1":
            raise AssertionError("bind must use lease checkpoint, not loop head")
        if kwargs["expected_state_digest"] != "C1":
            raise AssertionError("bind must use post-lease campaign state")
        if kwargs["loop_state_digest"] != "L1":
            raise AssertionError("bind must carry exact loop state")
        self.git.value = "H3"
        return {"status": "ACTIVE", "state_digest": "C2", "checkpoint_head": "H3"}


class _Loop:
    def __init__(self, git: _Git, *, fail_start: bool = False, bad_receipt: bool = False):
        self.git = git
        self.fail_start = fail_start
        self.bad_receipt = bad_receipt
        self.start_calls = []

    def start(self, **kwargs):
        self.start_calls.append(kwargs)
        if kwargs["expected_git_head"] != "H1":
            raise AssertionError("loop start must consume post-lease head")
        if self.fail_start:
            raise ValueError("loop start failed")
        self.git.value = "H2"
        if self.bad_receipt:
            return {"status": "STARTED", "loop_id": "L", "state_digest": "L1", "checkpoint_head": "wrong"}
        return {"status": "STARTED", "loop_id": "L", "state_digest": "L1", "checkpoint_head": "H2"}


def _pulse(head: str = "H0") -> dict:
    value = {
        "artifact": PULSE_ARTIFACT,
        "execution_authorized": False,
        "current_coordinates": {"git_head": head},
        "residual_steps": [1],
        "actions": [
            {"step": 1, "horizon": "I", "text": "execute verified residual", "current_state": "RESIDUAL", "history_preserved": True}
        ],
    }
    value["pulse_digest"] = _sha(value)
    return value


def _reseal(pulse: dict) -> dict:
    pulse = dict(pulse)
    pulse.pop("pulse_digest", None)
    pulse["pulse_digest"] = _sha(pulse)
    return pulse


def _bind(**overrides):
    git = overrides.pop("git", _Git())
    campaign = overrides.pop("campaign", _Campaign(git))
    loop = overrides.pop("loop", _Loop(git))
    kwargs = dict(
        campaign_runtime=campaign,
        loop_runtime=loop,
        pulse=_pulse(),
        residual_step=1,
        campaign_id="RHC-test",
        branch_id="b1",
        expected_campaign_state_digest="C0",
        expected_campaign_checkpoint_head="H0",
        expected_git_head="H0",
        agent="agent-a",
        actor="agent-a",
        shared_remote_mode="DISABLED",
        fetch=False,
        use_frontier=False,
        required_passes=["reconstruct", "execute", "verify"],
    )
    kwargs.update(overrides)
    return git, campaign, loop, bind_current_pulse_branch_to_loop(**kwargs)


class CampaignV3BindingTests(unittest.TestCase):
    def test_success_path_proves_h0_h1_h2_h3_without_execution_authority(self):
        git, campaign, loop, result = _bind()
        self.assertEqual(result["artifact"], ARTIFACT)
        self.assertEqual(result["status"], "BOUND")
        self.assertEqual(result["standing"], "BOUND_LOOP_NOT_WORK_EXECUTED")
        self.assertEqual(result["pulse_digest"], _pulse()["pulse_digest"])
        self.assertIn("BOUND_RECEIPT_RETAINS_VERIFIED_PULSE_DIGEST", result["laws"])
        self.assertEqual(
            [result["pre_lease_head"], result["post_lease_head"], result["post_loop_start_head"], result["post_bind_head"]],
            ["H0", "H1", "H2", "H3"],
        )
        self.assertFalse(result["execution_authority_granted"])
        self.assertFalse(result["work_executed"])
        self.assertEqual(loop.start_calls[0]["expected_git_head"], "H1")
        self.assertEqual(campaign.bind_calls[0]["expected_checkpoint_head"], "H1")
        self.assertEqual(git.head(), "H3")

    def test_tampered_pulse_digest_holds_before_mutation(self):
        pulse = _pulse()
        pulse["actions"][0]["text"] = "tampered after compilation"
        _, campaign, loop, result = _bind(pulse=pulse)
        self.assertEqual(result["status"], "HOLD_INVALID_BINDING_INPUT")
        self.assertIn("PULSE_DIGEST_INVALID", result["failures"])
        self.assertEqual(campaign.claim_calls, [])
        self.assertEqual(loop.start_calls, [])

    def test_stale_pulse_head_holds_before_mutation(self):
        git = _Git("H0")
        campaign = _Campaign(git)
        loop = _Loop(git)
        _, _, _, result = _bind(git=git, campaign=campaign, loop=loop, pulse=_pulse("OLD"))
        self.assertEqual(result["status"], "HOLD_INVALID_BINDING_INPUT")
        self.assertTrue(any(x.startswith("STALE_PULSE_HEAD") for x in result["failures"]))
        self.assertEqual(campaign.claim_calls, [])
        self.assertEqual(loop.start_calls, [])

    def test_non_residual_step_cannot_bind(self):
        pulse = _pulse()
        pulse["residual_steps"] = []
        pulse["actions"][0]["current_state"] = "SATISFIED"
        pulse = _reseal(pulse)
        _, campaign, loop, result = _bind(pulse=pulse)
        self.assertEqual(result["status"], "HOLD_INVALID_BINDING_INPUT")
        self.assertIn("STEP_NOT_RESIDUAL", result["failures"])
        self.assertEqual(campaign.claim_calls, [])
        self.assertEqual(loop.start_calls, [])

    def test_unexposed_required_operation_holds_before_campaign_lease(self):
        _, campaign, loop, result = _bind(
            required_operation="athena_frontier_claim",
            execution_surface={"exposed_operations": ["athena_agent_bootstrap"]},
        )
        self.assertEqual(result["status"], "HOLD")
        self.assertEqual(result["holds"][0]["kind"], "UNEXPOSED_REQUIRED_OPERATION")
        self.assertEqual(campaign.claim_calls, [])
        self.assertEqual(loop.start_calls, [])

    def test_exposed_operation_still_does_not_grant_execution_authority(self):
        _, _, _, result = _bind(
            required_operation="athena_frontier_claim",
            execution_surface={
                "operational_basis": {
                    "descriptors": [{"operation": "athena_frontier_claim", "current_exposure": True}]
                }
            },
        )
        self.assertEqual(result["status"], "BOUND")
        self.assertFalse(result["execution_authority_granted"])
        self.assertFalse(result["work_executed"])

    def test_campaign_lease_must_advance_git_head(self):
        git = _Git()
        campaign = _Campaign(git, advance_claim=False)
        _, _, loop, result = _bind(git=git, campaign=campaign, loop=_Loop(git))
        self.assertEqual(result["status"], "HOLD_CAMPAIGN_LEASE_RECEIPT")
        self.assertEqual(loop.start_calls, [])

    def test_loop_start_failure_preserves_exact_release_coordinates(self):
        git = _Git()
        campaign = _Campaign(git)
        loop = _Loop(git, fail_start=True)
        _, _, _, result = _bind(git=git, campaign=campaign, loop=loop)
        self.assertEqual(result["status"], "HOLD_LOOP_START_FAILED")
        self.assertEqual(result["standing"], "LEASED_NOT_BOUND")
        recovery = result["holds"][0]["recovery"]
        self.assertEqual(recovery["expected_state_digest"], "C1")
        self.assertEqual(recovery["expected_checkpoint_head"], "H1")
        self.assertEqual(git.head(), "H1")

    def test_bad_loop_checkpoint_holds_and_forbids_blind_second_start(self):
        git = _Git()
        campaign = _Campaign(git)
        loop = _Loop(git, bad_receipt=True)
        _, _, _, result = _bind(git=git, campaign=campaign, loop=loop)
        self.assertEqual(result["status"], "HOLD_LOOP_START_RECEIPT")
        self.assertEqual(result["holds"][0]["kind"], "LEASED_LOOP_RECEIPT_INCOMPLETE")
        self.assertEqual(len(loop.start_calls), 1)
        self.assertEqual(campaign.bind_calls, [])

    def test_bind_failure_preserves_existing_loop_for_rebind_not_duplicate_start(self):
        git = _Git()
        campaign = _Campaign(git, fail_bind=True)
        loop = _Loop(git)
        _, _, _, result = _bind(git=git, campaign=campaign, loop=loop)
        self.assertEqual(result["status"], "HOLD_CAMPAIGN_BIND_FAILED")
        self.assertEqual(result["holds"][0]["kind"], "LOOP_EXISTS_CAMPAIGN_UNBOUND")
        self.assertEqual(result["loop_id"], "L")
        self.assertEqual(len(loop.start_calls), 1)
        self.assertEqual(git.head(), "H2")

    def test_current_runtime_signatures_expose_exact_transaction_semantics(self):
        claim = inspect.signature(RehydrationCampaignRuntime.claim).parameters
        bind = inspect.signature(RehydrationCampaignRuntime.bind_loop).parameters
        start = inspect.signature(RehydrationLoopRuntime.start).parameters
        for name in ("expected_state_digest", "expected_checkpoint_head", "branch_id", "agent"):
            self.assertIn(name, claim)
        for name in ("expected_state_digest", "expected_checkpoint_head", "branch_id", "loop_id", "loop_state_digest"):
            self.assertIn(name, bind)
        for name in ("expected_git_head", "goal", "task"):
            self.assertIn(name, start)


if __name__ == "__main__":
    unittest.main()
