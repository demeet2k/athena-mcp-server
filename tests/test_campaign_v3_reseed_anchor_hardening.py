from __future__ import annotations

import hashlib
import json
import unittest

from athena_mcp.campaign_v3_ledger import PULSE_ARTIFACT
from athena_mcp.campaign_v3_reseed_anchor import (
    compile_campaign_v3_reseed_anchor,
    reseed_anchor_digest,
)


def _sha(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _pulse(*, head="H", shared_fresh=True):
    pulse = {
        "artifact": PULSE_ARTIFACT,
        "ledger_digest": "ledger",
        "pulse_index": 100,
        "actions": [],
        "holds": [],
        "current_coordinates": {
            "git_head": head,
            "shared_fresh": shared_fresh,
        },
        "execution_authorized": False,
        "must_reseed_from_then_current_state": True,
        "mission_complete_claim_allowed": False,
    }
    pulse["pulse_digest"] = _sha(pulse)
    return pulse


def _kwargs(*, pulse=None, primary_head="H"):
    return {
        "pulse": pulse or _pulse(head=primary_head),
        "campaign_id": "RHC-X",
        "campaign_state_digest": "state",
        "campaign_checkpoint_head": primary_head,
        "loop_id": None,
        "loop_state_digest": None,
        "anchor_id": "RA-X",
        "run_id": "RUN-X",
        "agent_coordinate_name": "SOL-LIM-X",
        "reseed_epoch": 1,
        "pulse_age_before": 100,
        "git_positions": [
            {"repo": "demeet2k/athena-mcp-server", "ref": "refs/heads/master", "head": primary_head, "tree": "TREE"}
        ],
        "primary_repo": "demeet2k/athena-mcp-server",
        "primary_ref": "refs/heads/master",
        "primary_head_before": primary_head,
        "prompt_digest": "prompt",
        "issue_pressure_digest": "pressure",
        "durable_returns": ["git:current"],
        "witnesses": ["rehydration:current-head-readback"],
        "continuation_value_class": "NONPOSITIVE",
        "selected_successor": None,
        "stop_class": "NO_POSITIVE_FRONTIER",
        "then_current_rehydrated": True,
    }


class CampaignV3ReseedAnchorHardeningTests(unittest.TestCase):
    def test_pulse_100_rejects_self_asserted_rehydration_across_head_mismatch(self):
        kwargs = _kwargs(pulse=_pulse(head="OLD"), primary_head="NEW")
        with self.assertRaisesRegex(ValueError, "then-current head must equal primary Git head"):
            compile_campaign_v3_reseed_anchor(**kwargs)

    def test_pulse_100_rejects_nonfresh_current_coordinates_even_with_boolean_true(self):
        kwargs = _kwargs(pulse=_pulse(head="H", shared_fresh=False), primary_head="H")
        with self.assertRaisesRegex(ValueError, "shared-fresh then-current coordinates"):
            compile_campaign_v3_reseed_anchor(**kwargs)

    def test_pulse_100_accepts_exact_fresh_head_and_remains_nonterminal(self):
        anchor = compile_campaign_v3_reseed_anchor(**_kwargs())
        self.assertEqual(anchor["git"]["head_after"], "H")
        self.assertEqual(anchor["pulse_age_after"], 0)
        self.assertFalse(anchor["platform_counter_reset_claimed"])
        self.assertEqual(anchor["stop_class"], "NO_POSITIVE_FRONTIER")
        self.assertTrue(reseed_anchor_digest(anchor))

    def test_anchor_run_and_agent_identities_must_be_nonempty(self):
        for field in ("anchor_id", "run_id", "agent_coordinate_name"):
            kwargs = _kwargs()
            kwargs[field] = "  "
            with self.subTest(field=field):
                with self.assertRaisesRegex(ValueError, "anchor/run/agent identities are required"):
                    compile_campaign_v3_reseed_anchor(**kwargs)


if __name__ == "__main__":
    unittest.main()
