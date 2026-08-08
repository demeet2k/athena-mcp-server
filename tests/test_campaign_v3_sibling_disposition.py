from __future__ import annotations

import hashlib
import json
import unittest

from athena_mcp.campaign_v3_ledger import ACTION_STATES, PULSE_ARTIFACT
from athena_mcp.campaign_v3_sibling_disposition import (
    ARTIFACT,
    apply_sibling_disposition,
    bind_sibling_disposition,
)


def _sha(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _pulse(head: str = "H0", shared_fresh: bool = True) -> dict:
    actions = []
    for step in range(1, 11):
        horizon = "I" if step <= 4 else "M" if step <= 7 else "L"
        actions.append(
            {
                "step": step,
                "horizon": horizon,
                "text": f"historical action {step}",
                "current_state": "RESIDUAL",
                "history_preserved": True,
            }
        )
    value = {
        "artifact": PULSE_ARTIFACT,
        "ledger_digest": "ledger",
        "source_issue": 177,
        "verification_issue": 185,
        "pulse_index": 1,
        "step_start": 1,
        "step_end": 10,
        "historical_horizon_coverage": {"I": 4, "M": 3, "L": 3},
        "current_status_counts": {
            h: {state: (count if state == "RESIDUAL" else 0) for state in ACTION_STATES}
            for h, count in {"I": 4, "M": 3, "L": 3}.items()
        },
        "actions": actions,
        "residual_steps": list(range(1, 11)),
        "hold_steps": [],
        "current_coordinates": {"git_head": head, "shared_fresh": shared_fresh},
        "operational_basis_status": "PASS",
        "operational_basis_digest": "basis",
        "execution_authorized": False,
        "authority_resolution_required": True,
        "holds": [],
        "must_reseed_from_then_current_state": False,
        "mission_complete_claim_allowed": False,
        "laws": [
            "HISTORICAL_ACTION != CURRENT_READY_WORK",
            "SATISFIED/SUPERSEDED != ERASED_HISTORY",
        ],
    }
    value["pulse_digest"] = _sha(value)
    return value


def _delta(*, relation="SATISFIES", step=1, recipient_head="H0", consumed=True, expected_vid=None, current_vid=None):
    value = {
        "relation": relation,
        "target_step": step,
        "source_ref": "github://sibling/delta/1",
        "source_head": "S1",
        "recipient_head": recipient_head,
        "recipient_readback_ref": "github://recipient/readback/1",
        "consumed": consumed,
        "reason": "sibling result now closes the historical action",
        "evidence_refs": ["test://evidence/1"],
    }
    if expected_vid is not None:
        value["expected_vid"] = expected_vid
    if current_vid is not None:
        value["current_vid"] = current_vid
    return value


class CampaignV3SiblingDispositionTests(unittest.TestCase):
    def test_consumed_current_sibling_satisfies_and_reseals_canonical_pulse(self):
        pulse = _pulse()
        receipt = bind_sibling_disposition(pulse=pulse, sibling_delta=_delta())
        self.assertEqual(receipt["artifact"], ARTIFACT)
        self.assertEqual(receipt["status"], "BOUND")
        self.assertEqual(receipt["assessment"]["status"], "SATISFIED")
        self.assertFalse(receipt["execution_authority"])

        updated = apply_sibling_disposition(pulse, receipt)
        self.assertEqual(updated["artifact"], PULSE_ARTIFACT)
        self.assertNotEqual(updated["pulse_digest"], pulse["pulse_digest"])
        self.assertEqual(updated["actions"][0]["current_state"], "SATISFIED")
        self.assertEqual(updated["actions"][0]["text"], "historical action 1")
        self.assertTrue(updated["actions"][0]["history_preserved"])
        self.assertNotIn(1, updated["residual_steps"])
        self.assertEqual(updated["current_status_counts"]["I"]["SATISFIED"], 1)
        self.assertEqual(updated["current_status_counts"]["I"]["RESIDUAL"], 3)
        self.assertFalse(updated["execution_authorized"])
        self.assertTrue(updated["authority_resolution_required"])
        check = dict(updated)
        digest = check.pop("pulse_digest")
        self.assertEqual(digest, _sha(check))

    def test_supersedes_preserves_historical_text_and_horizon(self):
        pulse = _pulse()
        receipt = bind_sibling_disposition(
            pulse=pulse,
            sibling_delta=_delta(relation="SUPERSEDES", step=5),
        )
        updated = apply_sibling_disposition(pulse, receipt)
        row = updated["actions"][4]
        self.assertEqual(row["current_state"], "SUPERSEDED")
        self.assertEqual(row["horizon"], "M")
        self.assertEqual(row["text"], "historical action 5")
        self.assertIn("SUPERSEDED != ERASED", updated["laws"])

    def test_delivery_without_consumption_holds(self):
        result = bind_sibling_disposition(pulse=_pulse(), sibling_delta=_delta(consumed=False))
        self.assertEqual(result["status"], "HOLD_INVALID_SIBLING_EVIDENCE")
        self.assertIn("RECIPIENT_CONSUMPTION_READBACK_REQUIRED", result["failures"])
        self.assertIsNone(result["assessment"])

    def test_stale_recipient_head_holds(self):
        result = bind_sibling_disposition(
            pulse=_pulse(head="CURRENT"),
            sibling_delta=_delta(recipient_head="OLD"),
        )
        self.assertEqual(result["status"], "HOLD_INVALID_SIBLING_EVIDENCE")
        self.assertTrue(any(x.startswith("STALE_RECIPIENT_HEAD") for x in result["failures"]))

    def test_unverified_shared_freshness_holds(self):
        result = bind_sibling_disposition(pulse=_pulse(shared_fresh=False), sibling_delta=_delta())
        self.assertEqual(result["status"], "HOLD_INVALID_SIBLING_EVIDENCE")
        self.assertIn("SHARED_FRESHNESS_REQUIRED", result["failures"])

    def test_target_vid_drift_holds(self):
        result = bind_sibling_disposition(
            pulse=_pulse(),
            sibling_delta=_delta(expected_vid="v1", current_vid="v2"),
        )
        self.assertEqual(result["status"], "HOLD_INVALID_SIBLING_EVIDENCE")
        self.assertTrue(any(x.startswith("STALE_TARGET") for x in result["failures"]))

    def test_unknown_relation_holds(self):
        result = bind_sibling_disposition(pulse=_pulse(), sibling_delta=_delta(relation="RELATED"))
        self.assertEqual(result["status"], "HOLD_INVALID_SIBLING_EVIDENCE")
        self.assertIn("RELATION_MUST_BE_SATISFIES_OR_SUPERSEDES", result["failures"])

    def test_tampered_pulse_holds_before_evidence_binding(self):
        pulse = _pulse()
        pulse["actions"][0]["text"] = "tampered"
        result = bind_sibling_disposition(pulse=pulse, sibling_delta=_delta())
        self.assertEqual(result["status"], "HOLD_INVALID_SIBLING_EVIDENCE")
        self.assertIn("PULSE_DIGEST_INVALID", result["failures"])

    def test_receipt_is_bound_to_exact_pulse_digest(self):
        pulse = _pulse()
        receipt = bind_sibling_disposition(pulse=pulse, sibling_delta=_delta())
        other = _pulse(head="H1")
        with self.assertRaisesRegex(ValueError, "different pulse"):
            apply_sibling_disposition(other, receipt)

    def test_receipt_historical_source_drift_is_rejected(self):
        pulse = _pulse()
        receipt = bind_sibling_disposition(pulse=pulse, sibling_delta=_delta())
        receipt = json.loads(json.dumps(receipt))
        receipt["source_action"]["text"] = "rewritten history"
        receipt.pop("receipt_digest")
        receipt["receipt_digest"] = _sha(receipt)
        with self.assertRaisesRegex(ValueError, "historical source action drift"):
            apply_sibling_disposition(pulse, receipt)


if __name__ == "__main__":
    unittest.main()
