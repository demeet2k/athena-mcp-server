from __future__ import annotations

import copy
import unittest

from athena_mcp.campaign_v3_life_dispatch_bridge import (
    DISPATCH_SCHEMA_VERSION,
    LIFE_POLICY,
    compute_pinned_dispatch_clear_condition_digest,
    validate_pinned_dispatch_packet_shape,
)


QUEST_ID = "Q-SCHEMA-STRICT"
QUEST_VERSION = "1"
AGENT_ID = "A-SCHEMA-STRICT"


def _condition():
    return {"id": "C1", "definition": "verification passes", "satisfied": False}


def _packet(result_class: str = "FAIL_CLEAR"):
    conditions = [_condition()]
    packet = {
        "dispatch_schema_version": DISPATCH_SCHEMA_VERSION,
        "agent_id": AGENT_ID,
        "quest_id": QUEST_ID,
        "quest_version": QUEST_VERSION,
        "life_policy": LIFE_POLICY,
        "frozen_clear_conditions": conditions,
        "clear_condition_digest": compute_pinned_dispatch_clear_condition_digest(
            QUEST_ID, QUEST_VERSION, conditions
        ),
        "result_class": result_class,
        "extra_life_reward_eligibility": False,
        "platform_counter_reset_claimed": False,
    }
    if result_class in {"CLEAR", "FAIL_CLEAR"}:
        packet.update(
            {
                "executed": True,
                "hard_gate_status": "PASS" if result_class == "CLEAR" else "FAIL",
                "witnesses": ["execution://event-1"],
            }
        )
    return packet


def _valid_anchor():
    return {
        "schema_version": "ATHENA.RESEED_ANCHOR.V1",
        "anchor_id": "ANCHOR-1",
        "run_id": "RUN-1",
        "agent_coordinate_name": AGENT_ID,
        "reseed_epoch": 1,
        "pulse_age_before": 1,
        "pulse_age_after": 0,
        "git": {"head_after": "a" * 40, "changed": False},
        "prompt_digest": None,
        "issue_pressure_digest": None,
        "target_versions": [{"id": QUEST_ID, "version": QUEST_VERSION}],
        "durable_returns": ["issue:149"],
        "satisfied_work": [],
        "residuals": [],
        "holds": [],
        "continuation_value_class": "POSITIVE",
        "selected_successor": None,
        "stop_class": None,
        "reverse_route": [],
        "witnesses": ["readback:anchor"],
        "platform_counter_reset_claimed": False,
    }


class CampaignV3LifeDispatchStrictSchemaTests(unittest.TestCase):
    def assert_schema_invalid(self, packet, expected_fragment: str) -> None:
        errors = validate_pinned_dispatch_packet_shape(packet)
        self.assertTrue(
            any(expected_fragment in error for error in errors),
            f"expected strict schema error containing {expected_fragment!r}; got {errors!r}",
        )

    def test_control_packet_is_valid(self):
        self.assertEqual([], validate_pinned_dispatch_packet_shape(_packet()))

    def test_condition_additional_property_is_rejected(self):
        packet = _packet()
        packet["frozen_clear_conditions"][0]["authority"] = True
        self.assert_schema_invalid(packet, "frozen_clear_conditions")

    def test_current_git_position_additional_property_is_rejected(self):
        packet = _packet()
        packet["current_git_positions"] = [
            {
                "repo": "demeet2k/athena-mcp-server",
                "ref": "refs/heads/master",
                "head": "b" * 40,
                "platform_counter_reset": True,
            }
        ]
        self.assert_schema_invalid(packet, "current_git_positions")

    def test_current_git_position_tree_null_is_rejected(self):
        packet = _packet()
        packet["current_git_positions"] = [
            {
                "repo": "demeet2k/athena-mcp-server",
                "ref": "refs/heads/master",
                "head": "b" * 40,
                "tree": None,
            }
        ]
        self.assert_schema_invalid(packet, "current_git_positions")

    def test_played_witness_item_must_be_nonempty_string(self):
        numeric = _packet()
        numeric["witnesses"] = [1]
        self.assert_schema_invalid(numeric, "witnesses")

        blank = _packet()
        blank["witnesses"] = [""]
        self.assert_schema_invalid(blank, "witnesses")

    def test_optional_hold_fields_still_obey_schema_types(self):
        packet = _packet("EVIDENCE_HOLD")
        packet["executed"] = "false"
        self.assert_schema_invalid(packet, "executed")

        packet = _packet("EVIDENCE_HOLD")
        packet["hard_gate_status"] = "UNKNOWN"
        self.assert_schema_invalid(packet, "hard_gate_status")

        packet = _packet("EVIDENCE_HOLD")
        packet["witnesses"] = [1]
        self.assert_schema_invalid(packet, "witnesses")

    def test_reseed_anchor_additional_property_is_rejected(self):
        packet = _packet()
        packet["reseed_anchor"] = _valid_anchor()
        self.assertEqual([], validate_pinned_dispatch_packet_shape(packet))

        tampered = copy.deepcopy(packet)
        tampered["reseed_anchor"]["runtime_only"] = "must-not-cross-semantic-abi"
        self.assert_schema_invalid(tampered, "reseed_anchor")

    def test_reseed_anchor_nested_git_additional_property_is_rejected(self):
        packet = _packet()
        packet["reseed_anchor"] = _valid_anchor()
        packet["reseed_anchor"]["git"]["authority"] = True
        self.assert_schema_invalid(packet, "reseed_anchor")


if __name__ == "__main__":
    unittest.main()
