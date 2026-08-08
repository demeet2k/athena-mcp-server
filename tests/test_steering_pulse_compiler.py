from __future__ import annotations

import unittest

from athena_mcp.steering_pulse_compiler import compile_current_state_pulse


def _pulse(index: int = 1) -> dict:
    start = (index - 1) * 10 + 1
    tags = ["I", "I", "I", "I", "M", "M", "M", "L", "L", "L"]
    return {
        "pulse_index": index,
        "source_comment_id": 5228254659 if index <= 10 else 5228293760,
        "source_body_digest": "BODY-DIGEST",
        "actions": [
            {"step": start + offset, "tag": tag, "text": f"Historical action {start + offset:04d}."}
            for offset, tag in enumerate(tags)
        ],
        "standing": "CURRICULUM_BUNDLE_NOT_EXECUTION_AUTHORITY",
    }


def _validation(pulse: dict, status: str = "PASS") -> dict:
    return {
        "status": status,
        "source_bundle_digest": "SOURCE-BUNDLE-DIGEST",
        "blocks": [
            {
                "comment_id": pulse["source_comment_id"],
                "body_digest": pulse["source_body_digest"],
            }
        ],
    }


def _state() -> dict:
    return {
        "git_head": "abc123",
        "prompt_stack_digest": "prompt-1",
        "frontier_digest": "frontier-1",
        "operational_basis_digest": "basis-1",
        "issue_pressure_digest": "pressure-1",
    }


def _deferred(pulse: dict) -> list[dict]:
    return [
        {"step": row["step"], "disposition": "DEFERRED", "reason": "reserve"}
        for row in pulse["actions"]
    ]


def _satisfied(pulse: dict) -> list[dict]:
    return [
        {
            "step": row["step"],
            "disposition": "SATISFIED",
            "evidence_refs": [f"receipt://{row['step']}"],
        }
        for row in pulse["actions"]
    ]


class SteeringPulseCompilerTests(unittest.TestCase):
    def test_compiles_residuals_and_preserves_433_without_authority(self):
        pulse = _pulse()
        assessments = _deferred(pulse)
        assessments[0] = {
            "step": 1,
            "disposition": "SATISFIED",
            "evidence_refs": ["git://receipt/1"],
        }
        assessments[2] = {
            "step": 3,
            "disposition": "RESIDUAL",
            "current_task": "Rehydrate current frontier.",
        }
        assessments[4] = {
            "step": 5,
            "disposition": "RESIDUAL",
            "current_task": "Build next compiler primitive.",
        }
        assessments[7] = {
            "step": 8,
            "disposition": "RESIDUAL",
            "current_task": "Measure stale-state failures.",
        }
        result = compile_current_state_pulse(pulse, _validation(pulse), _state(), assessments)
        self.assertEqual(result["status"], "COMPILED")
        self.assertEqual(result["coverage"]["source_horizon_counts"], {"I": 4, "M": 3, "L": 3})
        self.assertEqual(result["coverage"]["classified_horizon_counts"], {"I": 4, "M": 3, "L": 3})
        self.assertEqual(
            {row["horizon"] for row in result["work_order"]["candidates"]},
            {"I", "M", "L"},
        )
        self.assertTrue(
            all(row["standing"] == "ROUTING_CANDIDATE_NOT_SCHED_READY"
                for row in result["work_order"]["candidates"])
        )
        self.assertEqual(
            result["work_order"]["authority"],
            {
                "standing": "ROUTING_ONLY",
                "sched_ready": False,
                "claim_authority": False,
                "execution_authority": False,
            },
        )
        self.assertFalse(result["mission_complete"])

    def test_source_validation_and_digest_mismatch_fail_closed(self):
        pulse = _pulse()
        held = compile_current_state_pulse(pulse, _validation(pulse, "HOLD"), _state(), _deferred(pulse))
        self.assertEqual(held["status"], "HOLD")
        self.assertIn("SOURCE_VALIDATION_NOT_PASS", held["failures"])
        validation = _validation(pulse)
        validation["blocks"][0]["body_digest"] = "EDITED"
        edited = compile_current_state_pulse(pulse, validation, _state(), _deferred(pulse))
        self.assertEqual(edited["status"], "HOLD")
        self.assertIn("PULSE_SOURCE_DIGEST_MISMATCH", edited["failures"])

    def test_missing_current_coordinate_or_assessment_holds(self):
        pulse = _pulse()
        state = _state()
        del state["operational_basis_digest"]
        missing_state = compile_current_state_pulse(pulse, _validation(pulse), state, _deferred(pulse))
        self.assertIn("CURRENT_STATE_MISSING:operational_basis_digest", missing_state["failures"])
        missing_assessment = compile_current_state_pulse(
            pulse, _validation(pulse), _state(), _deferred(pulse)[:-1]
        )
        self.assertIn("ASSESSMENT_MISSING:10", missing_assessment["failures"])
        self.assertEqual(missing_assessment["status"], "HOLD")

    def test_evidence_current_task_and_hold_reason_are_enforced(self):
        pulse = _pulse()
        assessments = _deferred(pulse)
        assessments[0] = {"step": 1, "disposition": "SATISFIED"}
        assessments[1] = {"step": 2, "disposition": "SUPERSEDED"}
        assessments[2] = {"step": 3, "disposition": "RESIDUAL"}
        assessments[3] = {"step": 4, "disposition": "HOLD"}
        result = compile_current_state_pulse(pulse, _validation(pulse), _state(), assessments)
        self.assertEqual(result["status"], "HOLD")
        self.assertIn("EVIDENCE_REQUIRED:1:SATISFIED", result["failures"])
        self.assertIn("EVIDENCE_REQUIRED:2:SUPERSEDED", result["failures"])
        self.assertIn("CURRENT_TASK_REQUIRED:3", result["failures"])
        self.assertIn("HOLD_REASON_REQUIRED:4", result["failures"])

    def test_input_cannot_launder_sched_claim_or_execution_authority(self):
        pulse = _pulse()
        assessments = _deferred(pulse)
        assessments[0] = {
            "step": 1,
            "disposition": "RESIDUAL",
            "current_task": "Current residual",
            "sched_ready": True,
            "claim_authority": True,
            "execution_authority": True,
        }
        result = compile_current_state_pulse(pulse, _validation(pulse), _state(), assessments)
        candidate = result["work_order"]["candidates"][0]
        self.assertEqual(result["status"], "COMPILED")
        self.assertFalse(candidate["claim_authority"])
        self.assertFalse(candidate["execution_authority"])
        self.assertFalse(result["work_order"]["authority"]["sched_ready"])

    def test_deferred_is_reserve_not_false_satisfaction(self):
        pulse = _pulse()
        result = compile_current_state_pulse(pulse, _validation(pulse), _state(), _deferred(pulse))
        self.assertEqual(result["status"], "PULSE_DEFERRED")
        self.assertEqual(result["next"]["mode"], "ADVANCE_PULSE_WITH_RESERVE")
        self.assertEqual(result["coverage"]["disposition_counts"]["DEFERRED"], 10)

    def test_nonfinal_all_satisfied_advances_but_never_completes_mission(self):
        pulse = _pulse(1)
        result = compile_current_state_pulse(pulse, _validation(pulse), _state(), _satisfied(pulse))
        self.assertEqual(result["status"], "PULSE_SATISFIED")
        self.assertEqual(result["next"]["mode"], "ADVANCE_PULSE")
        self.assertEqual(result["next"]["pulse_index"], 2)
        self.assertFalse(result["mission_complete"])

    def test_pulse_100_always_rehydrates_and_reseeds(self):
        pulse = _pulse(100)
        result = compile_current_state_pulse(pulse, _validation(pulse), _state(), _satisfied(pulse))
        self.assertEqual(result["status"], "RESEED_REQUIRED")
        self.assertEqual(result["next"]["mode"], "REHYDRATE_NEWEST_GIT_AND_RESEED")
        self.assertIsNone(result["next"]["pulse_index"])
        self.assertFalse(result["mission_complete"])
        self.assertFalse(result["work_order"]["authority"]["execution_authority"])


if __name__ == "__main__":
    unittest.main()
