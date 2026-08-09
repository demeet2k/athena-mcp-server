from __future__ import annotations

import copy
import hashlib
import json
import unittest

from athena_mcp.campaign_v3_ledger import PULSE_ARTIFACT
from athena_mcp.campaign_v3_life_binding import (
    compile_campaign_v3_life_quest_packet,
    validate_campaign_v3_life_quest_packet,
)
from athena_mcp.campaign_v3_reseed_anchor import compile_campaign_v3_reseed_anchor


def _sha(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _pulse() -> dict:
    pulse = {
        "artifact": PULSE_ARTIFACT,
        "ledger_digest": "ledger-anchor-abi",
        "pulse_index": 1,
        "execution_authorized": False,
        "current_coordinates": {"git_head": "runtime-anchor-abi-head", "shared_fresh": True},
        "residual_steps": [3],
        "actions": [
            {
                "step": 3,
                "horizon": "I",
                "text": "verify schema-valid reseed anchor pass-through",
                "current_state": "RESIDUAL",
                "history_preserved": True,
            }
        ],
    }
    pulse["pulse_digest"] = _sha(pulse)
    return pulse


def _anchor(pulse: dict) -> dict:
    return compile_campaign_v3_reseed_anchor(
        pulse=pulse,
        campaign_id="RHC-ANCHOR-ABI-1",
        campaign_state_digest="campaign-state-anchor-abi",
        campaign_checkpoint_head="campaign-head-anchor-abi",
        loop_id="LOOP-ANCHOR-ABI-1",
        loop_state_digest="loop-state-anchor-abi",
        anchor_id="RA-ANCHOR-ABI-1",
        run_id="RUN-ANCHOR-ABI-1",
        agent_coordinate_name="ATHENA-ANCHOR-ABI-1",
        reseed_epoch=1,
        pulse_age_before=4,
        git_positions=[
            {
                "repo": "demeet2k/athena-mcp-server",
                "ref": "refs/heads/master",
                "head": "runtime-anchor-abi-head",
                "tree": "runtime-anchor-abi-tree",
            }
        ],
        primary_repo="demeet2k/athena-mcp-server",
        primary_ref="refs/heads/master",
        primary_head_before="runtime-anchor-abi-old",
        prompt_digest="prompt-anchor-abi",
        issue_pressure_digest="issue-149-anchor-abi",
        durable_returns=["runtime:issue:149:anchor-abi"],
        witnesses=["test:anchor-pass-through"],
        continuation_value_class="CONTINUE_POSITIVE_FRONTIER",
        selected_successor="campaign-life:semantic-dispatch",
        stop_class="CONTINUE_POSITIVE_FRONTIER",
        reverse_route=["campaign-v3:pulse:1"],
        then_current_rehydrated=True,
        extra_target_versions=[{"id": "QUEST-ANCHOR-ABI-1", "version": "1"}],
    )


class CampaignV3LifeAnchorAbiTests(unittest.TestCase):
    def test_compiler_wraps_but_does_not_mutate_validated_anchor(self):
        pulse = _pulse()
        anchor = _anchor(pulse)
        source_anchor = copy.deepcopy(anchor)

        packet = compile_campaign_v3_life_quest_packet(
            pulse=pulse,
            residual_step=3,
            campaign_id="RHC-ANCHOR-ABI-1",
            branch_id="B-ANCHOR-ABI-1",
            agent_coordinate_name="ATHENA-ANCHOR-ABI-1",
            quest_id="QUEST-ANCHOR-ABI-1",
            quest_version="1",
            clear_conditions=["semantic dispatch accepts the unchanged reseed anchor"],
            reseed_anchor=anchor,
        )

        self.assertEqual("COMPILED", packet["status"])
        self.assertEqual(source_anchor, anchor)
        self.assertEqual(source_anchor, packet["RESEED_ANCHOR"])
        self.assertNotIn("anchor_digest", packet["RESEED_ANCHOR"])
        self.assertEqual(_sha(source_anchor), packet["RESEED_ANCHOR_DIGEST"])
        self.assertEqual([], validate_campaign_v3_life_quest_packet(packet))

    def test_anchor_tamper_breaks_external_anchor_digest_and_packet_digest(self):
        pulse = _pulse()
        anchor = _anchor(pulse)
        packet = compile_campaign_v3_life_quest_packet(
            pulse=pulse,
            residual_step=3,
            campaign_id="RHC-ANCHOR-ABI-1",
            branch_id="B-ANCHOR-ABI-1",
            agent_coordinate_name="ATHENA-ANCHOR-ABI-1",
            quest_id="QUEST-ANCHOR-ABI-1",
            quest_version="1",
            clear_conditions=["semantic dispatch accepts the unchanged reseed anchor"],
            reseed_anchor=anchor,
        )
        packet["RESEED_ANCHOR"]["anchor_id"] = "RA-TAMPERED"
        errors = validate_campaign_v3_life_quest_packet(packet)
        self.assertIn("reseed_anchor_digest", errors)
        self.assertIn("packet_digest", errors)


if __name__ == "__main__":
    unittest.main()
