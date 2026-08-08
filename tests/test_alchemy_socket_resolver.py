from __future__ import annotations

import copy
import unittest

from athena_mcp.alchemy_socket_resolver import ARTIFACT, compile_socket_recipe


def _descriptor(
    operation: str,
    *,
    effect: str = "READ_ONLY",
    authority: str = "OBSERVATION_ONLY",
    auto_select: bool = True,
    capability_class: str = "BOOTSTRAP_REFRESH",
    current_exposure: bool = True,
    schema_digest: str = "schema-1",
):
    return {
        "operation": operation,
        "capability_class": capability_class,
        "component": "test_component",
        "effect": effect,
        "authority_class": authority,
        "freshness_dependencies": ["registered_runtime_surface"],
        "preconditions": ["operation is currently registered"],
        "replayability": effect == "READ_ONLY",
        "rollback_or_compensation": "NOT_REQUIRED_READ_ONLY" if effect == "READ_ONLY" else "COMPENSATE",
        "current_exposure": current_exposure,
        "auto_select": auto_select,
        "source_witness": {"surface": "PROTOCOL_TOOLS_CONTROL_FILTER", "tool_schema_digest": schema_digest},
    }


def _basis(*descriptors, status="OPERATIONAL_BASIS_READY", digest="basis-1"):
    return {
        "artifact": "OPERATIONAL_BASIS_V1",
        "status": status,
        "basis_digest": digest,
        "descriptors": list(descriptors),
        "unclassified": [],
        "laws": ["DESCRIPTOR != PERMISSION"],
        "source_witness": {
            "surface": "PROTOCOL_TOOLS_CONTROL_FILTER",
            "registered_count": len(descriptors),
            "registered_names_digest": "names",
            "registered_schema_digest": "schemas",
        },
    }


class AlchemySocketResolverV1Tests(unittest.TestCase):
    def test_auto_read_only_socket_seats_without_execution_authority(self):
        basis = _basis(_descriptor("athena_operational_basis"))
        result = compile_socket_recipe(
            ["athena_operational_basis"], basis, expected_basis_digest="basis-1"
        )
        self.assertEqual(result["artifact"], ARTIFACT)
        self.assertEqual(result["status"], "RECIPE")
        self.assertTrue(result["auto_executable"])
        self.assertFalse(result["execution_authority"])
        self.assertFalse(result["invocation_performed"])
        self.assertEqual(result["sockets"][0]["socket_state"], "AUTO_READ_ONLY")

    def test_write_socket_auto_mode_holds(self):
        basis = _basis(
            _descriptor(
                "athena_prompt_propose",
                effect="REPOSITORY_CANDIDATE_WRITE",
                authority="CANDIDATE_REPOSITORY_WRITE",
                auto_select=False,
                capability_class="PROMPT",
            )
        )
        result = compile_socket_recipe(
            ["athena_prompt_propose"], basis, expected_basis_digest="basis-1"
        )
        self.assertEqual(result["status"], "HOLD")
        self.assertIn("AUTHORITY_GATE_REQUIRED", {row["code"] for row in result["holds"]})

    def test_write_socket_plan_mode_preserves_gate_but_never_becomes_execution_ready(self):
        basis = _basis(
            _descriptor(
                "athena_prompt_propose",
                effect="REPOSITORY_CANDIDATE_WRITE",
                authority="CANDIDATE_REPOSITORY_WRITE",
                auto_select=False,
                capability_class="PROMPT",
            )
        )
        result = compile_socket_recipe(
            [{"operation": "athena_prompt_propose", "mode": "PLAN"}],
            basis,
            expected_basis_digest="basis-1",
        )
        self.assertEqual(result["status"], "RECIPE")
        self.assertFalse(result["auto_executable"])
        self.assertFalse(result["sockets"][0]["execution_ready"])
        self.assertEqual(result["sockets"][0]["socket_state"], "GATED_PLAN_ONLY")
        self.assertFalse(result["execution_authority"])

    def test_missing_operation_holds_instead_of_inventing_socket(self):
        result = compile_socket_recipe(
            ["athena_nonexistent_superpower"], _basis(), expected_basis_digest="basis-1"
        )
        self.assertEqual(result["status"], "HOLD")
        self.assertIn("SOCKET_NOT_EXPOSED", {row["code"] for row in result["holds"]})

    def test_basis_digest_drift_holds(self):
        basis = _basis(_descriptor("athena_operational_basis"), digest="new-basis")
        result = compile_socket_recipe(
            ["athena_operational_basis"], basis, expected_basis_digest="old-basis"
        )
        self.assertEqual(result["status"], "HOLD")
        self.assertIn("BASIS_DIGEST_DRIFT", {row["code"] for row in result["holds"]})

    def test_descriptor_semantic_or_schema_drift_holds(self):
        basis = _basis(_descriptor("athena_operational_basis", schema_digest="schema-new"))
        result = compile_socket_recipe(
            [{
                "operation": "athena_operational_basis",
                "expected_effect": "BOUNDED_RUNTIME_WRITE",
                "expected_tool_schema_digest": "schema-old",
            }],
            basis,
            expected_basis_digest="basis-1",
        )
        self.assertEqual(result["status"], "HOLD")
        codes = {row["code"] for row in result["holds"]}
        self.assertIn("SOCKET_EFFECT_DRIFT", codes)

    def test_global_basis_hold_fails_closed_even_when_requested_row_looks_safe(self):
        basis = _basis(_descriptor("athena_operational_basis"), status="OPERATIONAL_BASIS_HOLD")
        result = compile_socket_recipe(
            ["athena_operational_basis"], basis, expected_basis_digest="basis-1"
        )
        self.assertEqual(result["status"], "HOLD")
        self.assertIn("OPERATIONAL_BASIS_HOLD", {row["code"] for row in result["holds"]})

    def test_duplicate_operation_holds_and_input_basis_is_not_mutated(self):
        basis = _basis(_descriptor("athena_operational_basis"))
        before = copy.deepcopy(basis)
        result = compile_socket_recipe(
            ["athena_operational_basis", "athena_operational_basis"],
            basis,
            expected_basis_digest="basis-1",
        )
        self.assertEqual(result["status"], "HOLD")
        self.assertIn("DUPLICATE_OPERATION", {row["code"] for row in result["holds"]})
        self.assertEqual(basis, before)

    def test_expected_authority_and_schema_can_freeze_socket_contract(self):
        basis = _basis(_descriptor("athena_operational_basis", schema_digest="schema-1"))
        result = compile_socket_recipe(
            [{
                "socket_id": "basis-reader",
                "operation": "athena_operational_basis",
                "mode": "AUTO",
                "expected_effect": "READ_ONLY",
                "expected_authority_class": "OBSERVATION_ONLY",
                "expected_tool_schema_digest": "schema-1",
            }],
            basis,
            expected_basis_digest="basis-1",
        )
        self.assertEqual(result["status"], "RECIPE")
        self.assertEqual(result["sockets"][0]["socket_id"], "basis-reader")

    def test_live_basis_integration_preserves_write_gate(self):
        from athena_mcp import dispatch as _dispatch  # noqa: F401 - complete registration
        from athena_mcp.operational_basis import build_operational_basis, install

        install()
        basis = build_operational_basis()
        self.assertEqual(basis["status"], "OPERATIONAL_BASIS_READY")

        read_result = compile_socket_recipe(
            ["athena_operational_basis"],
            basis,
            expected_basis_digest=basis["basis_digest"],
        )
        self.assertEqual(read_result["status"], "RECIPE")
        self.assertTrue(read_result["auto_executable"])

        write_result = compile_socket_recipe(
            ["athena_prompt_propose"],
            basis,
            expected_basis_digest=basis["basis_digest"],
        )
        self.assertEqual(write_result["status"], "HOLD")
        self.assertIn("AUTHORITY_GATE_REQUIRED", {row["code"] for row in write_result["holds"]})


if __name__ == "__main__":
    unittest.main()
