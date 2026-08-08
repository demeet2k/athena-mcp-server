from __future__ import annotations

import unittest

from athena_mcp.campaign_v3_ledger import (
    LEDGER_ARTIFACT,
    PULSE_ARTIFACT,
    compile_current_pulse,
    compile_verified_ledger_source,
)


def _horizon(step: int) -> str:
    pos = ((step - 1) % 10) + 1
    return "I" if pos <= 4 else "M" if pos <= 7 else "L"


def _ledger_comments() -> list[dict]:
    rows = []
    for ledger_index in range(1, 11):
        start = (ledger_index - 1) * 100 + 1
        end = ledger_index * 100
        lines = [f"# LEDGER {ledger_index}/10 — STEPS {start:04d}–{end:04d}"]
        for step in range(start, end + 1):
            lines.append(f"{step:04d} `[{_horizon(step)}]` action {step:04d}")
        rows.append(
            {
                "id": 1000 + ledger_index,
                "url": f"https://github.com/demeet2k/Athena/issues/177#issuecomment-{1000 + ledger_index}",
                "body": "\n".join(lines),
            }
        )
    return rows


def _verification() -> dict:
    return {
        "id": 2001,
        "url": "https://github.com/demeet2k/Athena/issues/185#issuecomment-2001",
        "body": "LEDGER_VERIFIED=PASS\nLEDGER_EXECUTED=NOT ESTABLISHED\nCAMPAIGN_SUCCESS=NOT ESTABLISHED",
    }


class CampaignV3LedgerTests(unittest.TestCase):
    def test_compiles_exact_verified_1000_step_source(self):
        source = compile_verified_ledger_source(_ledger_comments(), _verification())
        self.assertEqual(source["artifact"], LEDGER_ARTIFACT)
        self.assertEqual(source["source_issue"], 177)
        self.assertEqual(source["verification_issue"], 185)
        self.assertEqual(source["pulse_count"], 100)
        self.assertEqual(source["action_count"], 1000)
        self.assertEqual(source["horizon_totals"], {"I": 400, "M": 300, "L": 300})
        self.assertEqual(source["pulses"][0]["horizon_coverage"], {"I": 4, "M": 3, "L": 3})
        self.assertEqual(source["pulses"][-1]["step_end"], 1000)
        self.assertEqual(source["execution_authority"], "NOT_DERIVED_FROM_LEDGER")

    def test_rejects_gap_or_duplicate_even_when_comment_count_is_ten(self):
        comments = _ledger_comments()
        comments[0]["body"] = comments[0]["body"].replace("0002 `[I]` action 0002", "0001 `[I]` duplicate")
        with self.assertRaisesRegex(ValueError, "exact contiguous range"):
            compile_verified_ledger_source(comments, _verification())

    def test_rejects_horizon_grammar_drift(self):
        comments = _ledger_comments()
        comments[0]["body"] = comments[0]["body"].replace("0005 `[M]` action 0005", "0005 `[I]` action 0005")
        with self.assertRaisesRegex(ValueError, "4I/3M/3L"):
            compile_verified_ledger_source(comments, _verification())

    def test_requires_verification_firewalls_not_just_pass_token(self):
        verification = _verification()
        verification["body"] = "LEDGER_VERIFIED=PASS"
        with self.assertRaisesRegex(ValueError, "execution/success distinction"):
            compile_verified_ledger_source(_ledger_comments(), verification)

    def test_current_pulse_preserves_satisfied_and_superseded_history(self):
        source = compile_verified_ledger_source(_ledger_comments(), _verification())
        pulse = compile_current_pulse(
            source,
            1,
            current_coordinates={"git_head": "abc", "prompt_digest": "p", "frontier_digest": "f"},
            action_states={1: "SATISFIED", 2: "SUPERSEDED", 3: "HOLD"},
            operational_basis={"status": "PASS", "basis_digest": "basis"},
        )
        self.assertEqual(pulse["artifact"], PULSE_ARTIFACT)
        self.assertEqual([row["current_state"] for row in pulse["actions"][:4]], [
            "SATISFIED", "SUPERSEDED", "HOLD", "RESIDUAL"
        ])
        self.assertTrue(all(row["history_preserved"] for row in pulse["actions"]))
        self.assertIn("PULSE_ACTION_HOLD", pulse["holds"])
        self.assertEqual(pulse["historical_horizon_coverage"], {"I": 4, "M": 3, "L": 3})
        self.assertFalse(pulse["execution_authorized"])

    def test_missing_operational_basis_holds_without_converting_issue_pressure_to_authority(self):
        source = compile_verified_ledger_source(_ledger_comments(), _verification())
        pulse = compile_current_pulse(
            source,
            37,
            current_coordinates={"git_head": "abc"},
        )
        self.assertIn("OPERATIONAL_BASIS_UNAVAILABLE_HOLD", pulse["holds"])
        self.assertTrue(pulse["authority_resolution_required"])
        self.assertFalse(pulse["execution_authorized"])
        self.assertEqual(pulse["residual_steps"], list(range(361, 371)))

    def test_operational_basis_presence_still_does_not_grant_execution_authority(self):
        source = compile_verified_ledger_source(_ledger_comments(), _verification())
        pulse = compile_current_pulse(
            source,
            2,
            current_coordinates={"git_head": "abc"},
            operational_basis={
                "status": "PASS",
                "basis_digest": "basis",
                "descriptors": [{"operation": "athena_frontier_claim", "effect": "GIT_WRITE_BOUNDED"}],
            },
        )
        self.assertEqual(pulse["operational_basis_digest"], "basis")
        self.assertFalse(pulse["execution_authorized"])
        self.assertTrue(pulse["authority_resolution_required"])
        self.assertNotIn("OPERATIONAL_BASIS_UNAVAILABLE_HOLD", pulse["holds"])

    def test_pulse_100_requires_then_current_reseed_and_cannot_self_certify_mission(self):
        source = compile_verified_ledger_source(_ledger_comments(), _verification())
        pulse = compile_current_pulse(
            source,
            100,
            current_coordinates={"git_head": "then-current"},
            operational_basis={"status": "PASS", "basis_digest": "basis"},
            action_states={step: "SATISFIED" for step in range(991, 1001)},
        )
        self.assertTrue(pulse["must_reseed_from_then_current_state"])
        self.assertFalse(pulse["mission_complete_claim_allowed"])
        self.assertEqual(pulse["residual_steps"], [])
        self.assertFalse(pulse["authority_resolution_required"])

    def test_source_digest_detects_post_compile_mutation(self):
        source = compile_verified_ledger_source(_ledger_comments(), _verification())
        source["pulses"][0]["actions"][0]["text"] = "mutated"
        with self.assertRaisesRegex(ValueError, "tampered"):
            compile_current_pulse(source, 1, current_coordinates={"git_head": "abc"})


if __name__ == "__main__":
    unittest.main()
