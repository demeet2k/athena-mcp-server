from __future__ import annotations

import unittest

from athena_mcp.rehydration_campaign import RehydrationCampaignRuntime
from athena_mcp.steering_pulse import compile_pulse


def _pulse(index: int = 1, digest: str = "source-digest") -> dict:
    start = (index - 1) * 10 + 1
    tags = ["I", "I", "I", "I", "M", "M", "M", "L", "L", "L"]
    return {
        "artifact": "ATHENA.STEERING.LEDGER.PULSE.V1",
        "pulse_index": index,
        "step_start": start,
        "step_end": start + 9,
        "source_comment_id": 5228254659 + index,
        "source_body_digest": digest,
        "actions": [
            {
                "step": start + offset,
                "tag": tag,
                "text": f"Historical steering action {start + offset:04d}.",
            }
            for offset, tag in enumerate(tags)
        ],
        "horizon_counts": {"I": 4, "M": 3, "L": 3},
        "standing": "CURRICULUM_BUNDLE_NOT_EXECUTION_AUTHORITY",
    }


def _satisfied_assessments(pulse: dict) -> list[dict]:
    return [
        {
            "step": row["step"],
            "status": "SATISFIED",
            "evidence_refs": [f"evidence:{row['step']}"],
        }
        for row in pulse["actions"]
    ]


def _address(**updates) -> dict:
    value = {
        "git_head": "current-head",
        "prompt_stack_digest": "prompt-digest",
        "frontier_digest": "frontier-digest",
        "shared_fresh": True,
    }
    value.update(updates)
    return value


class SteeringPulseCompilerTests(unittest.TestCase):
    def test_all_accounted_actions_advance_nonfinal_pulse(self):
        pulse = _pulse(1)
        result = compile_pulse(
            pulse,
            _satisfied_assessments(pulse),
            expected_source_body_digest="source-digest",
            current_address=_address(),
            execution_surface={},
        )
        self.assertEqual(result["status"], "ACCOUNTED")
        self.assertTrue(result["can_advance_pulse"])
        self.assertEqual(result["next"], "ADVANCE_TO_NEXT_PULSE")
        self.assertEqual(result["coverage"]["source"], {"I": 4, "M": 3, "L": 3})
        self.assertEqual(result["coverage"]["assessment_status"]["SATISFIED"]["total"], 10)

    def test_final_pulse_reseeds_instead_of_terminalizing(self):
        pulse = _pulse(100)
        result = compile_pulse(
            pulse,
            _satisfied_assessments(pulse),
            expected_source_body_digest="source-digest",
            current_address=_address(),
            execution_surface={},
        )
        self.assertEqual(result["status"], "ACCOUNTED")
        self.assertTrue(result["can_advance_pulse"])
        self.assertEqual(result["next"], "REHYDRATE_AND_RESEED_CURRENT_CUT")

    def test_missing_assessment_fails_closed(self):
        pulse = _pulse(2)
        assessments = _satisfied_assessments(pulse)[:-1]
        result = compile_pulse(
            pulse,
            assessments,
            expected_source_body_digest="source-digest",
            current_address=_address(),
        )
        self.assertEqual(result["status"], "HOLD_INVALID_COMPILATION_INPUT")
        self.assertTrue(any(item.startswith("MISSING_ASSESSMENTS:") for item in result["failures"]))
        self.assertFalse(result["can_advance_pulse"])

    def test_stale_source_digest_fails_closed(self):
        pulse = _pulse(3)
        result = compile_pulse(
            pulse,
            _satisfied_assessments(pulse),
            expected_source_body_digest="old-digest",
            current_address=_address(),
        )
        self.assertEqual(result["status"], "HOLD_INVALID_COMPILATION_INPUT")
        self.assertIn("STALE_PULSE_SOURCE_DIGEST", result["failures"])

    def test_satisfied_without_evidence_is_invalid(self):
        pulse = _pulse(4)
        assessments = _satisfied_assessments(pulse)
        assessments[0]["evidence_refs"] = []
        result = compile_pulse(
            pulse,
            assessments,
            expected_source_body_digest="source-digest",
            current_address=_address(),
        )
        self.assertEqual(result["status"], "HOLD_INVALID_COMPILATION_INPUT")
        self.assertIn(
            f"ASSESSMENT_EVIDENCE_REQUIRED:{pulse['step_start']}:SATISFIED",
            result["failures"],
        )

    def test_residual_with_exposed_operation_becomes_campaign_candidate(self):
        pulse = _pulse(5)
        assessments = _satisfied_assessments(pulse)
        step = pulse["step_start"]
        assessments[0] = {
            "step": step,
            "status": "RESIDUAL",
            "task": "Execute the current bounded residual through the exposed operation.",
            "evidence_refs": ["current:residual"],
            "required_capability_class": "FRONTIER_READ_SELECT",
            "required_operation": "athena_frontier_select",
            "routing_metrics": {"utility": 0.9, "cost": 0.1},
        }
        result = compile_pulse(
            pulse,
            assessments,
            expected_source_body_digest="source-digest",
            current_address=_address(),
            execution_surface={"frontier_tools": ["athena_frontier_select"]},
        )
        self.assertEqual(result["status"], "RESIDUAL_CANDIDATES")
        self.assertFalse(result["can_advance_pulse"])
        self.assertEqual(len(result["candidates"]), 1)
        candidate = result["candidates"][0]
        self.assertEqual(candidate["required_operation"], "athena_frontier_select")
        self.assertEqual(candidate["standing"], "CAMPAIGN_CANDIDATE_NOT_EXECUTION_AUTHORITY")
        branch = RehydrationCampaignRuntime._new_branch(
            candidate["task"],
            depth=0,
            parent=None,
            candidate=candidate,
        )
        self.assertEqual(branch["candidate_id"], candidate["candidate_id"])
        self.assertEqual(branch["source"]["step"], step)

    def test_unexposed_claim_operation_becomes_typed_hold_not_candidate(self):
        pulse = _pulse(6)
        assessments = _satisfied_assessments(pulse)
        step = pulse["step_start"]
        assessments[0] = {
            "step": step,
            "status": "RESIDUAL",
            "task": "Claim the current scheduler node.",
            "evidence_refs": ["frontier:ready-node"],
            "required_capability_class": "CLAIM_EXECUTION",
            "required_operation": "athena_frontier_claim",
            "requires_execution_authority": True,
        }
        result = compile_pulse(
            pulse,
            assessments,
            expected_source_body_digest="source-digest",
            current_address=_address(),
            execution_surface={
                "frontier_tools": ["athena_frontier_hydrate", "athena_frontier_select"],
                "claim_tool_exposed": False,
            },
        )
        self.assertEqual(result["status"], "HOLD")
        self.assertEqual(result["candidates"], [])
        self.assertTrue(any(row["kind"] == "UNEXPOSED_REQUIRED_OPERATION" for row in result["holds"]))
        self.assertFalse(result["can_advance_pulse"])

    def test_feature_branch_existence_is_not_an_execution_surface(self):
        pulse = _pulse(7)
        assessments = _satisfied_assessments(pulse)
        step = pulse["step_start"]
        assessments[0] = {
            "step": step,
            "status": "RESIDUAL",
            "task": "Use feature-only claim implementation.",
            "evidence_refs": ["github:feature-pr"],
            "required_capability_class": "CLAIM_EXECUTION",
            "required_operation": "athena_frontier_claim",
            "requires_execution_authority": True,
        }
        result = compile_pulse(
            pulse,
            assessments,
            expected_source_body_digest="source-digest",
            current_address=_address(),
            execution_surface={
                "exposed_operations": [],
                "feature_branch_only": ["athena_frontier_claim"],
            },
        )
        self.assertEqual(result["status"], "HOLD")
        self.assertEqual(result["candidates"], [])

    def test_unbound_execution_authority_is_invalid(self):
        pulse = _pulse(8)
        assessments = _satisfied_assessments(pulse)
        step = pulse["step_start"]
        assessments[0] = {
            "step": step,
            "status": "RESIDUAL",
            "task": "Execute something privileged.",
            "evidence_refs": ["current:residual"],
            "requires_execution_authority": True,
        }
        result = compile_pulse(
            pulse,
            assessments,
            expected_source_body_digest="source-digest",
            current_address=_address(),
        )
        self.assertEqual(result["status"], "HOLD_INVALID_COMPILATION_INPUT")
        self.assertIn(f"EXECUTION_OPERATION_REQUIRED:{step}", result["failures"])

    def test_stale_target_vid_is_invalid(self):
        pulse = _pulse(9)
        assessments = _satisfied_assessments(pulse)
        step = pulse["step_start"]
        assessments[0].update({"expected_vid": "v1", "current_vid": "v2"})
        result = compile_pulse(
            pulse,
            assessments,
            expected_source_body_digest="source-digest",
            current_address=_address(),
        )
        self.assertEqual(result["status"], "HOLD_INVALID_COMPILATION_INPUT")
        self.assertIn(f"STALE_TARGET:{step}:v1!=v2", result["failures"])

    def test_unverified_shared_freshness_is_invalid(self):
        pulse = _pulse(10)
        result = compile_pulse(
            pulse,
            _satisfied_assessments(pulse),
            expected_source_body_digest="source-digest",
            current_address=_address(shared_fresh=False),
        )
        self.assertEqual(result["status"], "HOLD_INVALID_COMPILATION_INPUT")
        self.assertIn("UNVERIFIED_SHARED_FRESHNESS", result["failures"])

    def test_generator_assessment_iterable_matches_list_compilation_digest(self):
        pulse = _pulse(11)
        assessments = _satisfied_assessments(pulse)
        list_result = compile_pulse(
            pulse,
            assessments,
            expected_source_body_digest="source-digest",
            current_address=_address(),
        )
        generator_result = compile_pulse(
            pulse,
            (dict(row) for row in assessments),
            expected_source_body_digest="source-digest",
            current_address=_address(),
        )
        self.assertEqual(generator_result["status"], "ACCOUNTED")
        self.assertEqual(list_result["compilation_digest"], generator_result["compilation_digest"])


if __name__ == "__main__":
    unittest.main()
