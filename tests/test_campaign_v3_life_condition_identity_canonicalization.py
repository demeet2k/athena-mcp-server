from __future__ import annotations

import copy
import hashlib
import json
import unittest

from athena_mcp.campaign_v3_life_condition_identity import (
    ARTIFACT,
    validate_campaign_v3_life_condition_identity,
)


def _sha(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _envelope(conditions):
    basis = {
        "packet_digest": "packet-digest",
        "quest_id": "Q-CANON",
        "quest_version": "1",
        "identity_ref": "quest-contract://Q-CANON@1",
        "conditions": copy.deepcopy(conditions),
    }
    value = {
        "artifact": ARTIFACT,
        "status": "FROZEN_PREPLAY_PACKET_BOUND",
        **basis,
        "condition_identity_digest": _sha(basis),
        "outcomes_observed": False,
        "temporal_creation_proof": False,
        "execution_authority": False,
        "life_consumption_authority": False,
        "reward_issuance_authority": False,
        "reseed_anchor_consumption_authority": False,
        "platform_counter_reset_claimed": False,
    }
    value["envelope_digest"] = _sha(value)
    return value


class CampaignV3LifeConditionIdentityCanonicalizationTests(unittest.TestCase):
    def test_reordered_semantically_identical_forgery_is_rejected_even_with_recomputed_digests(self):
        canonical = [
            {"id": "A", "definition": "first"},
            {"id": "B", "definition": "second"},
        ]
        self.assertEqual([], validate_campaign_v3_life_condition_identity(_envelope(canonical)))

        forged = _envelope(list(reversed(canonical)))
        errors = validate_campaign_v3_life_condition_identity(forged)
        self.assertIn("conditions_not_canonical_order", errors)


if __name__ == "__main__":
    unittest.main()
