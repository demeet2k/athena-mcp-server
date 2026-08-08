from __future__ import annotations

import unittest

from athena_mcp.steering_pulse_operational_basis import (
    compile_pulse_with_operational_basis,
)


def _pulse() -> dict:
    tags = ["I", "I", "I", "I", "M", "M", "M", "L", "L", "L"]
    return {
        "artifact": "ATHENA.STEERING.LEDGER.PULSE.V1",
        "pulse_index": 1,
        "step_start": 1,
        "step_end": 10,
        "source_comment_id": 5228254659,
        "source_body_digest": "source-digest",
        "actions": [
            {"step": step, "tag": tag, "text": f"historical action {step}"}
            for step, tag in enumerate(tags, start=1)
        ],
    }


def _satisfied() -> list[dict]:
    return [
        {"step": step, "status": "SATISFIED", "evidence_refs": [f"e:{step}"]}
        for step in range(1, 11)
    ]


def _address(digest: str | None = "basis-A") -> dict:
    out = {
        "git_head": "current-head",
        "prompt_stack_digest": "prompt-A",
        "frontier_digest": "frontier-A",
        "shared_fresh": True,
    }
    if digest is not None:
        out["operational_basis_digest"] = digest
    return out


def _basis(
    operations: list[tuple[str, bool]],
    *,
    digest: str = "basis-A",
    status: str = "OPERATIONAL_BASIS_READY",
) -> dict:
    return {
        "artifact": "OPERATIONAL_BASIS_V1",
        "status": status,
        "basis_digest": digest,
        "descriptors": [
            {
                "operation": name,
                "current_exposure": exposed,
                "capability_class": (
                    "CLAIM_EXECUTION" if name == "athena_frontier_claim" else "FRONTIER_READ_SELECT"
                ),
                "authority_class": "OBSERVATION_ONLY",
            }
            for name, exposed in operations
        ],
        "source_witness": {"surface": "PROTOCOL_TOOLS_CONTROL_FILTER"},
    }


def _residual(operation: str) -> list[dict]:
    rows = _satisfied()
    rows[0] = {
        "step": 1,
        "status": "RESIDUAL",
        "task": f"Use {operation} for the current bounded residual.",
        "evidence_refs": ["current:residual"],
        "required_operation": operation,
        "requires_execution_authority": operation == "athena_frontier_claim",
    }
    return rows


class SteeringPulseOperationalBasisTests(unittest.TestCase):
    def _compile(self, assessments, *, basis, address=None):
        return compile_pulse_with_operational_basis(
            _pulse(),
            assessments,
            expected_source_body_digest="source-digest",
            current_address=address or _address(),
            operational_basis=basis,
        )

    def test_exposed_descriptor_can_project_residual_candidate_without_minting_authority(self):
        result = self._compile(
            _residual("athena_frontier_select"),
            basis=_basis([("athena_frontier_select", True)]),
        )
        self.assertEqual("RESIDUAL_CANDIDATES", result["status"])
        self.assertEqual(["athena_frontier_select"], result["exposed_operations"])
        self.assertEqual(1, len(result["candidates"]))
        self.assertEqual(
            "CAMPAIGN_CANDIDATE_NOT_EXECUTION_AUTHORITY",
            result["candidates"][0]["standing"],
        )

    def test_unexposed_claim_descriptor_is_typed_hold(self):
        result = self._compile(
            _residual("athena_frontier_claim"),
            basis=_basis(
                [
                    ("athena_frontier_select", True),
                    ("athena_frontier_claim", False),
                ]
            ),
        )
        self.assertEqual("HOLD", result["status"])
        self.assertEqual([], result["candidates"])
        self.assertTrue(
            any(row["kind"] == "UNEXPOSED_REQUIRED_OPERATION" for row in result["holds"])
        )

    def test_basis_digest_mismatch_fails_before_pulse_routing(self):
        result = self._compile(
            _residual("athena_frontier_select"),
            basis=_basis([("athena_frontier_select", True)], digest="basis-B"),
        )
        self.assertEqual("HOLD_INVALID_COMPILATION_INPUT", result["status"])
        self.assertIn("STALE_OPERATIONAL_BASIS_DIGEST:basis-A!=basis-B", result["failures"])
        self.assertEqual([], result["candidates"])
        self.assertEqual("REHYDRATE_OPERATIONAL_BASIS", result["next"])

    def test_unready_basis_fails_closed(self):
        result = self._compile(
            _satisfied(),
            basis=_basis([], status="OPERATIONAL_BASIS_HOLD"),
        )
        self.assertEqual("HOLD_INVALID_COMPILATION_INPUT", result["status"])
        self.assertIn("OPERATIONAL_BASIS_NOT_READY", result["failures"])
        self.assertFalse(result["can_advance_pulse"])

    def test_feature_branch_claim_name_does_not_create_exposure(self):
        basis = _basis([("athena_frontier_select", True)])
        basis["feature_branch_only"] = ["athena_frontier_claim"]
        result = self._compile(_residual("athena_frontier_claim"), basis=basis)
        self.assertEqual("HOLD", result["status"])
        self.assertNotIn("athena_frontier_claim", result["exposed_operations"])

    def test_missing_address_basis_digest_fails_closed(self):
        result = self._compile(
            _satisfied(),
            basis=_basis([]),
            address=_address(digest=None),
        )
        self.assertEqual("HOLD_INVALID_COMPILATION_INPUT", result["status"])
        self.assertIn("MISSING_CURRENT_OPERATIONAL_BASIS_DIGEST", result["failures"])


if __name__ == "__main__":
    unittest.main()
