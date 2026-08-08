from __future__ import annotations

import unittest

from athena_mcp.steering_campaign_loop import bind_candidate_to_v1_loop


def _compilation() -> dict:
    return {
        "artifact": "ATHENA.STEERING.PULSE.COMPILATION.V1",
        "status": "RESIDUAL_CANDIDATES",
        "failures": [],
        "holds": [],
        "candidates": [
            {
                "candidate_id": "C1",
                "task": "Do current residual",
                "standing": "CAMPAIGN_CANDIDATE_NOT_EXECUTION_AUTHORITY",
            }
        ],
    }


class _CampaignWithDifferentLoopRuntime:
    def __init__(self):
        self.loop_runtime = object()
        self.calls = []

    def resume(self, campaign_id):
        self.calls.append(("resume", campaign_id))
        raise AssertionError("runtime mismatch must HOLD before campaign mutation/read")


class SteeringCampaignLoopRuntimeIdentityTests(unittest.TestCase):
    def test_mismatched_campaign_and_supplied_loop_runtime_holds_before_campaign_access(self):
        campaign = _CampaignWithDifferentLoopRuntime()
        supplied_loop_runtime = object()

        result = bind_candidate_to_v1_loop(
            campaign,
            supplied_loop_runtime,
            compilation=_compilation(),
            campaign_id="RHC-TEST",
            branch_id="B1",
            candidate_id="C1",
            actor="agent-a",
            expected_campaign_state_digest="CS1",
            expected_campaign_checkpoint_head="H0",
            expected_git_head="H0",
            shared_remote_mode="DISABLED",
        )

        self.assertEqual("HOLD", result["status"])
        self.assertEqual("LOOP_RUNTIME_MISMATCH", result["hold_kind"])
        self.assertEqual([], campaign.calls)
        self.assertIn("CAMPAIGN_LOOP_RUNTIME = BIND_LOOP_RUNTIME", result["laws"])


if __name__ == "__main__":
    unittest.main()
