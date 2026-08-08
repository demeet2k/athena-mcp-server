import copy
import unittest
from unittest.mock import patch

from athena_mcp import campaign_v3_life_dispatch as life
from athena_mcp.campaign_v3_binding import ARTIFACT as BIND_ARTIFACT

QUEST = "Q-LIFE"
VERSION = "1"


def anchor(epoch=1):
    head = "a" * 40
    return {
        "schema_version": "ATHENA.RESEED_ANCHOR.V1",
        "anchor_id": f"RA-CV3-LIFE-E{epoch}",
        "parent_anchor_id": None,
        "parent_reseed_epoch": None,
        "run_id": f"RUN-CV3-LIFE-{epoch}",
        "agent_coordinate_name": "AID-CV3-LIFE-1",
        "reseed_epoch": epoch,
        "pulse_age_before": 1,
        "pulse_age_after": 0,
        "git": {
            "repo": "demeet2k/athena-mcp-server",
            "ref": "refs/heads/agent/campaign-v3-life-dispatch-v1",
            "head_before": head,
            "head_after": head,
            "tree_after": "tree-a",
            "changed": False,
        },
        "git_positions": [
            {
                "repo": "demeet2k/athena-mcp-server",
                "ref": "refs/heads/agent/campaign-v3-life-dispatch-v1",
                "head": head,
                "tree": "tree-a",
            }
        ],
        "prompt_digest": "prompt-life-v1",
        "issue_pressure_digest": "issue-278",
        "target_versions": [{"id": "campaign-v3-life-dispatch-v1", "version": "candidate"}],
        "durable_returns": ["issue:278"],
        "satisfied_work": [],
        "residuals": ["continue verified quest"],
        "holds": [],
        "continuation_value_class": "POSITIVE",
        "selected_successor": "issue:278/successor",
        "stop_class": "CONTINUE_POSITIVE_FRONTIER",
        "reverse_route": ["issue:278"],
        "witnesses": ["readback:campaign-v3-life-test"],
        "platform_counter_reset_claimed": False,
    }


def bound_result():
    return {
        "artifact": BIND_ARTIFACT,
        "status": "BOUND",
        "standing": "BOUND_LOOP_NOT_WORK_EXECUTED",
        "campaign_id": "GAME",
        "branch_id": "b1",
        "loop_id": "L1",
        "execution_authority_granted": False,
        "work_executed": False,
    }


def binding(*, eligible=True):
    with patch.object(life, "bind_current_pulse_branch_to_loop", return_value=bound_result()) as mocked:
        receipt = life.bind_current_pulse_branch_with_life_policy(
            binding_kwargs={"campaign_id": "GAME", "branch_id": "b1", "agent": "A1"},
            quest_id=QUEST,
            quest_version=VERSION,
            agent_id="A1",
            clear_condition_ids=["tests_pass", "readback_pass"],
            reseed_anchor=anchor(),
            extra_life_reward_eligibility=eligible,
        )
        mocked.assert_called_once()
        return receipt


def completion(status="SUCCEEDED"):
    return {"status": status, "observed": True, "summary": "observed"}


def reward(receipt_id="R1", *, self_scored=False):
    return {
        "receipt_id": receipt_id,
        "delta": 1,
        "verified": True,
        "self_scored": self_scored,
        "witnesses": ["w"],
    }


def outcome(
    receipt,
    world,
    *,
    status="SUCCEEDED",
    executed=True,
    hard="PASS",
    conditions=None,
    witnesses=None,
    gtc=None,
    reward_value=None,
    reseed=None,
):
    return life.resolve_observed_gtc_outcome(
        dispatch_receipt=receipt,
        world=world,
        completion=completion(status),
        executed=executed,
        hard_gate_status=hard,
        clear_condition_outcomes=(
            conditions if conditions is not None else {"tests_pass": True, "readback_pass": True}
        ),
        witnesses=["witness"] if witnesses is None else witnesses,
        gtc_stop_class=gtc,
        reseed_anchor=reseed,
        extra_life_reward=reward_value,
    )


class CampaignV3LifeDispatchTests(unittest.TestCase):
    def test_bind_reuses_existing_campaign_binder_and_enters_with_three_lives(self):
        receipt = binding()
        self.assertEqual("BOUND_LIFE_POLICY", receipt["status"])
        self.assertEqual(life.LIFE_POLICY, receipt["LIFE_POLICY"])
        self.assertEqual(3, receipt["initial_world"]["agents"]["A1"]["base_lives_remaining"])
        self.assertFalse(receipt["execution_authority_granted"])
        self.assertFalse(receipt["work_executed"])
        self.assertFalse(receipt["platform_counter_reset_claimed"])
        self.assertEqual([], life.validate_dispatch_binding(receipt))

    def test_campaign_bind_hold_does_not_create_life_world(self):
        hold = {"artifact": BIND_ARTIFACT, "status": "HOLD", "failures": ["x"], "holds": []}
        with patch.object(life, "bind_current_pulse_branch_to_loop", return_value=hold):
            receipt = life.bind_current_pulse_branch_with_life_policy(
                binding_kwargs={"campaign_id": "GAME"},
                quest_id=QUEST,
                quest_version=VERSION,
                agent_id="A1",
                clear_condition_ids=["tests_pass"],
                reseed_anchor=anchor(),
                extra_life_reward_eligibility=False,
            )
        self.assertEqual("HOLD_CAMPAIGN_NOT_BOUND", receipt["status"])
        self.assertNotIn("initial_world", receipt)

    def test_invalid_anchor_holds_before_campaign_binder(self):
        bad = {"schema_version": "BROKEN"}
        with patch.object(life, "bind_current_pulse_branch_to_loop") as mocked:
            receipt = life.bind_current_pulse_branch_with_life_policy(
                binding_kwargs={"campaign_id": "GAME"},
                quest_id=QUEST,
                quest_version=VERSION,
                agent_id="A1",
                clear_condition_ids=["tests_pass"],
                reseed_anchor=bad,
                extra_life_reward_eligibility=False,
            )
            mocked.assert_not_called()
        self.assertEqual("HOLD_INVALID_LIFE_BINDING", receipt["status"])

    def test_tampered_dispatch_digest_holds_without_life(self):
        receipt = binding()
        world = receipt["initial_world"]
        receipt["quest_id"] = "tampered"
        out = outcome(receipt, world)
        self.assertEqual("HOLD_INVALID_DISPATCH_BINDING", out["status"])
        self.assertFalse(out["life_consumed"])

    def test_clear_mints_verified_extra_life_when_eligible(self):
        receipt = binding()
        out = outcome(receipt, receipt["initial_world"], reward_value=reward())
        self.assertEqual("CLEARED", out["status"])
        self.assertEqual("EXTRA_LIFE_EARNED", out["reward_status"])
        self.assertEqual(1, out["world"]["agents"]["A1"]["extra_lives_remaining"])

    def test_reward_is_suppressed_when_dispatch_not_eligible_but_clear_stands(self):
        receipt = binding(eligible=False)
        out = outcome(receipt, receipt["initial_world"], reward_value=reward())
        self.assertEqual("CLEARED", out["status"])
        self.assertEqual("REWARD_SUPPRESSED_NOT_ELIGIBLE", out["reward_policy_status"])
        self.assertEqual(0, out["world"]["agents"]["A1"]["extra_lives_remaining"])

    def test_false_clear_condition_rejects_succeeded_completion_without_consuming_life(self):
        receipt = binding()
        world = receipt["initial_world"]
        out = outcome(receipt, world, conditions={"tests_pass": True, "readback_pass": False})
        self.assertEqual("HOLD_COMPLETION_GATE_CONTRADICTION", out["status"])
        self.assertEqual(3, out["world"]["agents"]["A1"]["base_lives_remaining"])

    def test_failed_play_consumes_exactly_one_base_life_and_local_reseeds(self):
        receipt = binding()
        out = outcome(
            receipt,
            receipt["initial_world"],
            status="FAILED",
            hard="FAIL",
            conditions={"tests_pass": True, "readback_pass": False},
        )
        self.assertEqual("AUTO_RESEED_LOCAL", out["status"])
        self.assertEqual("BASE", out["life_source"])
        self.assertEqual(2, out["world"]["agents"]["A1"]["base_lives_remaining"])
        self.assertFalse(out["platform_counter_reset_claimed"])

    def test_three_failed_plays_without_extra_end_game(self):
        receipt = binding()
        world = receipt["initial_world"]
        for _ in range(2):
            out = outcome(
                receipt,
                world,
                status="FAILED",
                hard="FAIL",
                conditions={"tests_pass": False, "readback_pass": True},
            )
            self.assertEqual("AUTO_RESEED_LOCAL", out["status"])
            world = out["world"]
        out = outcome(
            receipt,
            world,
            status="FAILED",
            hard="FAIL",
            conditions={"tests_pass": False, "readback_pass": True},
        )
        self.assertEqual("GAME_OVER_OUT_OF_LIVES", out["status"])
        self.assertEqual(0, out["world"]["agents"]["A1"]["base_lives_remaining"])

    def test_extra_life_prevents_default_exhaustion_and_resets_only_logical_age(self):
        receipt = binding()
        world = outcome(receipt, receipt["initial_world"], reward_value=reward())["world"]
        for _ in range(2):
            world = outcome(
                receipt,
                world,
                status="FAILED",
                hard="FAIL",
                conditions={"tests_pass": False, "readback_pass": True},
            )["world"]
        out = outcome(
            receipt,
            world,
            status="FAILED",
            hard="FAIL",
            conditions={"tests_pass": False, "readback_pass": True},
        )
        self.assertEqual("AUTO_RESEED_GLOBAL_EXTRA_LIFE", out["status"])
        self.assertEqual(1, out["world"]["global_reseed_epoch"])
        self.assertEqual(0, out["world"]["global_game_age"])
        self.assertFalse(out["platform_counter_reset_claimed"])

    def test_evidence_hold_is_gtc_hold_and_consumes_no_life(self):
        receipt = binding()
        world = receipt["initial_world"]
        out = outcome(
            receipt,
            world,
            status="HELD",
            executed=False,
            hard=None,
            conditions={},
            witnesses=[],
            gtc="EVIDENCE_HOLD",
        )
        self.assertEqual("EVIDENCE_HOLD", out["status"])
        self.assertFalse(out["life_consumed"])
        self.assertEqual(3, out["world"]["agents"]["A1"]["base_lives_remaining"])

    def test_no_positive_frontier_stops_without_life_or_world_age_change(self):
        receipt = binding()
        world = receipt["initial_world"]
        out = outcome(
            receipt,
            world,
            status="HELD",
            executed=False,
            hard=None,
            conditions={},
            witnesses=[],
            gtc="NO_POSITIVE_FRONTIER",
        )
        self.assertEqual("GTC_STOP_NO_LIFE", out["status"])
        self.assertEqual("NO_POSITIVE_FRONTIER", out["gtc_stop_class"])
        self.assertEqual(world, out["world"])

    def test_premature_model_stop_is_diagnostic_not_played_failure(self):
        receipt = binding()
        out = outcome(
            receipt,
            receipt["initial_world"],
            status="HELD",
            executed=False,
            hard=None,
            conditions={},
            witnesses=[],
            gtc="PREMATURE_MODEL_STOP",
        )
        self.assertEqual("GTC_STOP_NO_LIFE", out["status"])
        self.assertFalse(out["life_consumed"])

    def test_unplayed_failed_completion_does_not_consume_life(self):
        receipt = binding()
        out = outcome(
            receipt,
            receipt["initial_world"],
            status="FAILED",
            executed=False,
            hard="FAIL",
            conditions={"tests_pass": False, "readback_pass": True},
        )
        self.assertEqual("HOLD_UNPLAYED_COMPLETION", out["status"])
        self.assertEqual(3, out["world"]["agents"]["A1"]["base_lives_remaining"])

    def test_missing_witness_does_not_consume_life(self):
        receipt = binding()
        out = outcome(
            receipt,
            receipt["initial_world"],
            status="FAILED",
            hard="FAIL",
            conditions={"tests_pass": False, "readback_pass": True},
            witnesses=[],
        )
        self.assertEqual("HOLD_INVALID_ATTEMPT", out["status"])
        self.assertEqual(3, out["world"]["agents"]["A1"]["base_lives_remaining"])

    def test_invalid_reseed_anchor_consumes_life_but_cannot_fabricate_continuation(self):
        receipt = binding()
        out = outcome(
            receipt,
            receipt["initial_world"],
            status="FAILED",
            hard="FAIL",
            conditions={"tests_pass": False, "readback_pass": True},
            reseed={"schema_version": "BROKEN"},
        )
        self.assertEqual("LIFE_CONSUMED_ANCHOR_HOLD", out["status"])
        self.assertEqual(2, out["world"]["agents"]["A1"]["base_lives_remaining"])

    def test_extra_life_reward_is_idempotent(self):
        receipt = binding()
        world = outcome(receipt, receipt["initial_world"], reward_value=reward("R1"))["world"]
        out = outcome(receipt, world, reward_value=reward("R1"))
        self.assertEqual("REWARD_IDEMPOTENT_REPLAY", out["reward_status"])
        self.assertEqual(1, out["world"]["agents"]["A1"]["extra_lives_remaining"])

    def test_self_scored_reward_is_rejected(self):
        receipt = binding()
        out = outcome(receipt, receipt["initial_world"], reward_value=reward("R1", self_scored=True))
        self.assertEqual("REWARD_REJECTED:reward_self_scored_forbidden", out["reward_status"])
        self.assertEqual(0, out["world"]["agents"]["A1"]["extra_lives_remaining"])

    def test_clear_condition_digest_is_ordered_and_deterministic(self):
        ids, digest = life.freeze_clear_condition_digest(["a", "b"])
        self.assertEqual(["a", "b"], ids)
        self.assertEqual(digest, life.freeze_clear_condition_digest(["a", "b"])[1])
        self.assertNotEqual(digest, life.freeze_clear_condition_digest(["b", "a"])[1])


if __name__ == "__main__":
    unittest.main()
