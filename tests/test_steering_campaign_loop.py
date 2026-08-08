from __future__ import annotations

import unittest

from athena_mcp.steering_campaign_loop import bind_candidate_to_v1_loop


class _Git:
    def __init__(self, head="H0"):
        self.value = head

    def head(self):
        return self.value


class _Campaign:
    def __init__(self, *, verify_before="PASS", verify_after="PASS", branch_candidate="C1"):
        self.git = _Git()
        self.calls = []
        self.verify_before = verify_before
        self.verify_after = verify_after
        self.branch = {
            "branch_id": "B1",
            "status": "OPEN",
            "candidate_id": branch_candidate,
            "task": "Do current residual",
            "loop": None,
        }
        self.state_digest = "CS1"
        self.checkpoint = "H0"
        self.chain_digest = "CC1"
        self.verify_count = 0

    def resume(self, campaign_id):
        self.calls.append(("resume", campaign_id))
        return {
            "status": "RESUMED",
            "campaign_id": campaign_id,
            "goal": "Campaign goal",
            "state_digest": self.state_digest,
            "checkpoint_head": self.checkpoint,
            "chain_digest": self.chain_digest,
            "branches": [dict(self.branch)],
        }

    def verify(self, campaign_id):
        self.calls.append(("verify", campaign_id))
        self.verify_count += 1
        status = self.verify_before if self.verify_count == 1 else self.verify_after
        return {"status": status, "campaign_id": campaign_id, "failures": [] if status == "PASS" else ["TEST_HOLD"]}

    def claim(self, **kwargs):
        self.calls.append(("claim", kwargs))
        assert kwargs["expected_state_digest"] == "CS1"
        assert kwargs["expected_checkpoint_head"] == "H0"
        assert kwargs["branch_id"] == "B1"
        self.branch["status"] = "CLAIMED"
        self.state_digest = "CS2"
        self.checkpoint = "H-CLAIM"
        self.chain_digest = "CC2"
        self.git.value = self.checkpoint
        return {
            "status": "ACTIVE",
            "campaign_id": kwargs["campaign_id"],
            "state_digest": self.state_digest,
            "checkpoint_head": self.checkpoint,
            "chain_digest": self.chain_digest,
        }

    def bind_loop(self, **kwargs):
        self.calls.append(("bind_loop", kwargs))
        assert kwargs["expected_state_digest"] == "CS2"
        assert kwargs["expected_checkpoint_head"] == "H-CLAIM"
        assert kwargs["loop_id"] == "L1"
        assert kwargs["loop_state_digest"] == "LS1"
        self.branch["status"] = "ACTIVE"
        self.branch["loop"] = {
            "loop_id": "L1",
            "state_digest": "LS1",
            "checkpoint_head": "H-LOOP",
            "status": "ACTIVE",
        }
        self.state_digest = "CS3"
        self.checkpoint = "H-BIND"
        self.chain_digest = "CC3"
        self.git.value = self.checkpoint
        return {
            "status": "ACTIVE",
            "campaign_id": kwargs["campaign_id"],
            "state_digest": self.state_digest,
            "checkpoint_head": self.checkpoint,
            "chain_digest": self.chain_digest,
            "loop_id": "L1",
        }


class _Loop:
    def __init__(self, campaign, *, verify="PASS", drift=False):
        self.campaign = campaign
        self.calls = []
        self.verify_status = verify
        self.drift = drift
        self.advance_called = False

    def start(self, **kwargs):
        self.calls.append(("start", kwargs))
        assert kwargs["expected_git_head"] == "H-CLAIM"
        self.campaign.git.value = "H-LOOP"
        return {
            "status": "STARTED",
            "loop_id": "L1",
            "state_digest": "LS1",
            "checkpoint_head": "H-LOOP",
            "prompt_digest": "P1",
            "chain_digest": "LC1",
            "compiled_self_prompt": "explicit handoff prompt",
            "law": "STARTED_LOOP != BACKGROUND_EXECUTION; invoke each explicit cycle",
        }

    def resume(self, loop_id, include_prompt=True):
        self.calls.append(("resume", loop_id, include_prompt))
        return {
            "status": "RESUMED",
            "loop_id": loop_id,
            "loop_status": "ACTIVE",
            "state_digest": "LS-DRIFT" if self.drift else "LS1",
            "checkpoint_head": "H-LOOP",
            "prompt_digest": "P1",
            "chain_digest": "LC1",
            "compiled_self_prompt": "explicit handoff prompt",
        }

    def verify(self, loop_id):
        self.calls.append(("verify", loop_id))
        return {"status": self.verify_status, "loop_id": loop_id, "failures": [] if self.verify_status == "PASS" else ["CHAIN"]}

    def advance(self, **kwargs):
        self.advance_called = True
        raise AssertionError("Step 4 must not advance the V1 loop")


def _compilation(status="RESIDUAL_CANDIDATES"):
    return {
        "artifact": "ATHENA.STEERING.PULSE.COMPILATION.V1",
        "status": status,
        "failures": [],
        "holds": [],
        "candidates": [
            {
                "candidate_id": "C1",
                "task": "Do current residual",
                "metrics": {"utility": 1.0},
                "source": {"kind": "STEERING_LEDGER_RESIDUAL", "pulse_index": 1, "step": 1},
                "standing": "CAMPAIGN_CANDIDATE_NOT_EXECUTION_AUTHORITY",
            }
        ],
    }


def _bind(campaign, loop, **overrides):
    kwargs = {
        "compilation": _compilation(),
        "campaign_id": "RHC-TEST",
        "branch_id": "B1",
        "candidate_id": "C1",
        "actor": "agent-a",
        "expected_campaign_state_digest": "CS1",
        "expected_campaign_checkpoint_head": "H0",
        "expected_git_head": "H0",
        "shared_remote_mode": "DISABLED",
        "fetch": False,
        "use_frontier": False,
    }
    kwargs.update(overrides)
    return bind_candidate_to_v1_loop(campaign, loop, **kwargs)


class SteeringCampaignLoopTests(unittest.TestCase):
    def test_success_binds_fresh_loop_and_returns_resume_handoff_without_advance(self):
        campaign = _Campaign()
        loop = _Loop(campaign)
        result = _bind(campaign, loop)
        self.assertEqual("BOUND", result["status"])
        self.assertEqual("BOUND_NOT_EXECUTED", result["standing"])
        self.assertEqual("L1", result["handoff"]["loop_id"])
        self.assertEqual("L1", result["campaign_after"]["branch"]["loop"]["loop_id"])
        self.assertFalse(loop.advance_called)
        self.assertEqual(
            ["resume", "verify", "claim", "bind_loop", "resume", "verify"],
            [row[0] for row in campaign.calls],
        )
        self.assertEqual(["start", "resume", "verify"], [row[0] for row in loop.calls])

    def test_non_residual_compilation_holds_before_mutation(self):
        campaign = _Campaign()
        loop = _Loop(campaign)
        result = _bind(campaign, loop, compilation=_compilation(status="ACCOUNTED"))
        self.assertEqual("HOLD", result["status"])
        self.assertEqual("COMPILATION_NOT_RESIDUAL", result["hold_kind"])
        self.assertEqual([], campaign.calls)
        self.assertEqual([], loop.calls)

    def test_branch_candidate_mismatch_holds_before_claim(self):
        campaign = _Campaign(branch_candidate="OTHER")
        loop = _Loop(campaign)
        result = _bind(campaign, loop)
        self.assertEqual("HOLD", result["status"])
        self.assertEqual("BRANCH_CANDIDATE_MISMATCH", result["hold_kind"])
        self.assertNotIn("claim", [row[0] for row in campaign.calls])
        self.assertEqual([], loop.calls)

    def test_stale_git_head_holds_before_claim(self):
        campaign = _Campaign()
        campaign.git.value = "H-NEW"
        loop = _Loop(campaign)
        result = _bind(campaign, loop)
        self.assertEqual("HOLD", result["status"])
        self.assertEqual("STALE_GIT_HEAD", result["hold_kind"])
        self.assertNotIn("claim", [row[0] for row in campaign.calls])
        self.assertEqual([], loop.calls)

    def test_loop_verify_failure_holds_after_start_without_binding(self):
        campaign = _Campaign()
        loop = _Loop(campaign, verify="HOLD")
        result = _bind(campaign, loop)
        self.assertEqual("HOLD", result["status"])
        self.assertEqual("LOOP_VERIFY", result["hold_kind"])
        self.assertIn("claim", [row[0] for row in campaign.calls])
        self.assertNotIn("bind_loop", [row[0] for row in campaign.calls])
        self.assertFalse(loop.advance_called)

    def test_loop_state_drift_holds_before_binding(self):
        campaign = _Campaign()
        loop = _Loop(campaign, drift=True)
        result = _bind(campaign, loop)
        self.assertEqual("HOLD", result["status"])
        self.assertEqual("LOOP_STATE_DRIFT", result["hold_kind"])
        self.assertNotIn("bind_loop", [row[0] for row in campaign.calls])

    def test_post_bind_campaign_verify_failure_is_typed_hold_with_binding_receipt(self):
        campaign = _Campaign(verify_after="HOLD")
        loop = _Loop(campaign)
        result = _bind(campaign, loop)
        self.assertEqual("HOLD", result["status"])
        self.assertEqual("CAMPAIGN_VERIFY_POST", result["hold_kind"])
        self.assertEqual("L1", result["details"]["loop_id"])
        self.assertIn("bind_loop", [row[0] for row in campaign.calls])
        self.assertFalse(loop.advance_called)


if __name__ == "__main__":
    unittest.main()
