from __future__ import annotations

import unittest

from athena_mcp.sibling_disposition import bind_sibling_disposition
from athena_mcp.steering_pulse import compile_pulse


def _action(step=1, tag="I", text="Read current shared Git HEAD."):
    return {"step": step, "tag": tag, "text": text}


def _address(**updates):
    value = {
        "git_head": "head-current",
        "prompt_stack_digest": "prompt-current",
        "frontier_digest": "frontier-current",
        "shared_fresh": True,
    }
    value.update(updates)
    return value


def _delta(**updates):
    value = {
        "target_step": 1,
        "relation": "SATISFIES",
        "source_ref": "github://sibling/receipt-1",
        "source_head": "head-parent",
        "recipient_head": "head-current",
        "consumed": True,
        "recipient_readback_ref": "github://recipient/readback-1",
        "reason": "Current recipient readback confirms the sibling delta closes this historical action.",
        "evidence_refs": ["github://evidence/current-head"],
    }
    value.update(updates)
    return value


def _pulse():
    tags = ["I", "I", "I", "I", "M", "M", "M", "L", "L", "L"]
    return {
        "artifact": "ATHENA.STEERING.LEDGER.PULSE.V1",
        "pulse_index": 1,
        "step_start": 1,
        "step_end": 10,
        "source_comment_id": 5228254659,
        "source_body_digest": "pulse-source-digest",
        "actions": [
            {
                "step": step,
                "tag": tag,
                "text": f"Historical steering action {step:04d} remains immutable source text.",
            }
            for step, tag in enumerate(tags, start=1)
        ],
        "horizon_counts": {"I": 4, "M": 3, "L": 3},
    }


class SiblingDispositionTests(unittest.TestCase):
    def test_current_consumed_sibling_delta_can_bind_satisfied(self):
        result = bind_sibling_disposition(
            pulse_action=_action(), current_address=_address(), sibling_delta=_delta()
        )
        self.assertEqual("BOUND", result["status"])
        self.assertEqual("SATISFIED", result["assessment"]["status"])
        self.assertFalse(result["execution_authority"])
        self.assertIn("github://sibling/receipt-1", result["assessment"]["evidence_refs"])
        self.assertIn("github://recipient/readback-1", result["assessment"]["evidence_refs"])

    def test_superseded_preserves_historical_action(self):
        action = _action(text="Historical action that is now replaced by a stronger current path.")
        result = bind_sibling_disposition(
            pulse_action=action,
            current_address=_address(),
            sibling_delta=_delta(
                relation="SUPERSEDES",
                reason="A stronger current descendant replaces the old route while retaining lineage.",
            ),
        )
        self.assertEqual("SUPERSEDED", result["assessment"]["status"])
        self.assertEqual(action["text"], result["source_action"]["text"])
        self.assertIn("SUPERSEDED != ERASED", result["laws"])

    def test_delivery_without_recipient_consumption_holds(self):
        result = bind_sibling_disposition(
            pulse_action=_action(),
            current_address=_address(),
            sibling_delta=_delta(consumed=False),
        )
        self.assertEqual("HOLD_INVALID_SIBLING_EVIDENCE", result["status"])
        self.assertIn("RECIPIENT_CONSUMPTION_READBACK_REQUIRED", result["failures"])
        self.assertIsNone(result["assessment"])

    def test_stale_recipient_head_holds(self):
        result = bind_sibling_disposition(
            pulse_action=_action(),
            current_address=_address(),
            sibling_delta=_delta(recipient_head="head-old"),
        )
        self.assertEqual("HOLD_INVALID_SIBLING_EVIDENCE", result["status"])
        self.assertTrue(any(x.startswith("STALE_RECIPIENT_HEAD:") for x in result["failures"]))

    def test_target_vid_drift_holds(self):
        result = bind_sibling_disposition(
            pulse_action=_action(),
            current_address=_address(),
            sibling_delta=_delta(expected_vid="v1", current_vid="v2"),
        )
        self.assertEqual("HOLD_INVALID_SIBLING_EVIDENCE", result["status"])
        self.assertIn("STALE_TARGET:v1!=v2", result["failures"])

    def test_unknown_relation_cannot_create_disposition(self):
        result = bind_sibling_disposition(
            pulse_action=_action(),
            current_address=_address(),
            sibling_delta=_delta(relation="SIMILAR_TO"),
        )
        self.assertEqual("HOLD_INVALID_SIBLING_EVIDENCE", result["status"])
        self.assertIn("RELATION_MUST_BE_SATISFIES_OR_SUPERSEDES", result["failures"])

    def test_compiler_retains_source_text_and_evidence_after_selective_satisfaction(self):
        pulse = _pulse()
        first = bind_sibling_disposition(
            pulse_action=pulse["actions"][0],
            current_address=_address(),
            sibling_delta=_delta(target_step=1),
        )
        second = bind_sibling_disposition(
            pulse_action=pulse["actions"][1],
            current_address=_address(),
            sibling_delta=_delta(
                target_step=2,
                relation="SUPERSEDES",
                source_ref="github://sibling/receipt-2",
                recipient_readback_ref="github://recipient/readback-2",
                reason="Current descendant route supersedes the historical step.",
            ),
        )
        assessments = [first["assessment"], second["assessment"]]
        assessments.extend(
            {
                "step": step,
                "status": "DEFERRED",
                "reason": "Not selected in this bounded selective-satisfaction fixture.",
            }
            for step in range(3, 11)
        )
        result = compile_pulse(
            pulse,
            assessments,
            expected_source_body_digest="pulse-source-digest",
            current_address=_address(),
            execution_surface={},
        )
        self.assertEqual("ACCOUNTED", result["status"])
        self.assertEqual("SATISFIED", result["actions"][0]["status"])
        self.assertEqual("SUPERSEDED", result["actions"][1]["status"])
        self.assertEqual(pulse["actions"][0]["text"], result["actions"][0]["source_text"])
        self.assertEqual(pulse["actions"][1]["text"], result["actions"][1]["source_text"])
        self.assertIn("github://sibling/receipt-1", result["actions"][0]["evidence_refs"])
        self.assertEqual({"I": 4, "M": 3, "L": 3}, result["coverage"]["source"])


if __name__ == "__main__":
    unittest.main()
