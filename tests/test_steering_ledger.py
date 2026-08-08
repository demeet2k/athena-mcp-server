from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from athena_mcp.steering_ledger import extract_pulse, validate_source_bundle

CONTRACT_PATH = Path("spec/STEERING_LEDGER_V1.json")


def _contract() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def _step_text(step: int) -> str:
    if step == 991:
        return "Recheck current HEAD, prompt stack, operational basis, frontier, issue pressure, and sibling deltas."
    if step == 992:
        return "Verify the full sequence and repair numbering or coverage defects without rewriting history."
    if step == 1000:
        return "ULTIMATE RETURN: do NOT terminate at 1000/1000; rehydrate newest Git, compute current CUT, and reseed the highest-value lawful successor."
    if step % 10 == 0:
        return f"Bounded long-horizon game/challenge for pulse {step // 10}."
    return f"Steering action {step:04d}."


def _tag(step: int) -> str:
    position = (step - 1) % 10 + 1
    if position <= 4:
        return "I"
    if position <= 7:
        return "M"
    return "L"


def _source_comments(contract: dict) -> list[dict]:
    comments = []
    for block in contract["source"]["blocks"]:
        start = int(block["step_start"])
        end = int(block["step_end"])
        ledger = int(block["ledger"])
        lines = [f"# LEDGER {ledger}/10 · steps {start:04d}–{end:04d}"]
        for step in range(start, end + 1):
            lines.append(f"{step:04d} `[{_tag(step)}]` {_step_text(step)}")
        comments.append(
            {
                "id": int(block["comment_id"]),
                "updated_at": f"2026-08-08T{ledger:02d}:00:00Z",
                "body": "\n".join(lines),
            }
        )
    return comments


def _verification(contract: dict) -> dict:
    return {
        "id": int(contract["verification"]["comment_id"]),
        "updated_at": "2026-08-08T20:00:00Z",
        "body": "\n".join(
            [
                "LEDGER_VERIFIED = PASS",
                "LEDGER_EXECUTED = NOT ESTABLISHED",
                "CAMPAIGN_SUCCESS = NOT ESTABLISHED",
            ]
        ),
    }


class SteeringLedgerTests(unittest.TestCase):
    def test_verified_source_bundle_passes_exact_1000_step_433_structure(self):
        contract = _contract()
        result = validate_source_bundle(contract, _source_comments(contract), _verification(contract))
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["action_count"], 1000)
        self.assertEqual(result["pulse_count"], 100)
        self.assertEqual(result["tag_counts"], {"I": 400, "M": 300, "L": 300})
        self.assertEqual(result["failures"], [])
        self.assertEqual(len(result["blocks"]), 10)
        self.assertTrue(result["source_bundle_digest"])

    def test_missing_step_fails_global_and_block_sequence(self):
        contract = _contract()
        comments = _source_comments(contract)
        comments[4]["body"] = comments[4]["body"].replace(
            "0500 `[L]` Bounded long-horizon game/challenge for pulse 50.\n",
            "",
        )
        result = validate_source_bundle(contract, comments, _verification(contract))
        self.assertEqual(result["status"], "HOLD")
        self.assertTrue(any(item.startswith("BLOCK_SEQUENCE:") for item in result["failures"]))
        self.assertIn("GLOBAL_SEQUENCE", result["failures"])

    def test_wrong_tag_breaks_pulse_pattern_and_global_count(self):
        contract = _contract()
        comments = _source_comments(contract)
        comments[0]["body"] = comments[0]["body"].replace(
            "0005 `[M]` Steering action 0005.",
            "0005 `[I]` Steering action 0005.",
        )
        result = validate_source_bundle(contract, comments, _verification(contract))
        self.assertEqual(result["status"], "HOLD")
        self.assertIn("PULSE_TAG_PATTERN:1", result["failures"])
        self.assertTrue(any(item.startswith("GLOBAL_I_COUNT:") for item in result["failures"]))
        self.assertTrue(any(item.startswith("GLOBAL_M_COUNT:") for item in result["failures"]))

    def test_comment_identity_and_verification_receipt_fail_closed(self):
        contract = _contract()
        comments = _source_comments(contract)
        comments[-1]["id"] = 999999
        verification = _verification(contract)
        verification["body"] = "LEDGER_EXECUTED = NO"
        result = validate_source_bundle(contract, comments, verification)
        self.assertEqual(result["status"], "HOLD")
        self.assertTrue(any(item.startswith("MISSING_SOURCE_COMMENTS:") for item in result["failures"]))
        self.assertTrue(any(item.startswith("UNEXPECTED_SOURCE_COMMENTS:") for item in result["failures"]))
        self.assertIn("VERIFICATION_MARKER:LEDGER_VERIFIED=PASS", result["failures"])
        self.assertIn("VERIFICATION_MARKER:CAMPAIGN_SUCCESS", result["failures"])

    def test_source_order_does_not_change_verified_content_digest(self):
        contract = _contract()
        comments = _source_comments(contract)
        a = validate_source_bundle(contract, comments, _verification(contract))
        b = validate_source_bundle(contract, reversed(comments), _verification(contract))
        self.assertEqual(a["status"], "PASS")
        self.assertEqual(b["status"], "PASS")
        self.assertEqual(a["source_bundle_digest"], b["source_bundle_digest"])

    def test_source_edit_changes_bundle_digest_even_when_structure_still_passes(self):
        contract = _contract()
        comments = _source_comments(contract)
        a = validate_source_bundle(contract, comments, _verification(contract))
        edited = copy.deepcopy(comments)
        edited[2]["body"] = edited[2]["body"].replace(
            "Steering action 0201.", "Steering action 0201 with revised wording."
        )
        edited[2]["updated_at"] = "2026-08-08T23:59:59Z"
        b = validate_source_bundle(contract, edited, _verification(contract))
        self.assertEqual(b["status"], "PASS")
        self.assertNotEqual(a["source_bundle_digest"], b["source_bundle_digest"])

    def test_extract_pulse_returns_only_one_curriculum_bundle(self):
        contract = _contract()
        comments = _source_comments(contract)
        pulse = extract_pulse(contract, comments, 61)
        self.assertEqual(pulse["pulse_index"], 61)
        self.assertEqual(pulse["step_start"], 601)
        self.assertEqual(pulse["step_end"], 610)
        self.assertEqual(len(pulse["actions"]), 10)
        self.assertEqual(pulse["horizon_counts"], {"I": 4, "M": 3, "L": 3})
        self.assertEqual(pulse["standing"], "CURRICULUM_BUNDLE_NOT_EXECUTION_AUTHORITY")

    def test_final_reseed_markers_are_required(self):
        contract = _contract()
        comments = _source_comments(contract)
        comments[-1]["body"] = comments[-1]["body"].replace(
            _step_text(1000), "ULTIMATE RETURN: stop here."
        )
        result = validate_source_bundle(contract, comments, _verification(contract))
        self.assertEqual(result["status"], "HOLD")
        self.assertIn("FINAL_RESEED_1000", result["failures"])


if __name__ == "__main__":
    unittest.main()
