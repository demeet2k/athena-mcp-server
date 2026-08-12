import tempfile
import unittest

from athena_mcp.server import Server
from athena_mcp.tool_activation_consumer import CanonicalToolActivationConsumer, ToolActivationError


TOOL_NAME = "athena_qhug_pareto_solve"

QHUG_ACTIVATION_SPEC = {
    "patches": [
        {"id": "USE_CANONICAL_DISPATCH", "value": 5, "proof_cost": 1},
        {"id": "BIND_RESULT", "value": 4, "proof_cost": 1},
        {"id": "ADD_PARALLEL_EXECUTOR", "value": 1, "proof_cost": 5, "governance": 5},
    ],
    "conflicts": [["USE_CANONICAL_DISPATCH", "ADD_PARALLEL_EXECUTOR"]],
    "dependencies": [
        {"patch": "BIND_RESULT", "alternatives": [["USE_CANONICAL_DISPATCH"]]},
    ],
    "mode": "governed",
    "policy": {"lambda_patch": 0, "mu_proof_cost": 0, "nu_governance": 0},
}


def measured_candidate(
    target_ref=f"tool:{TOOL_NAME}",
    *,
    tool_name=TOOL_NAME,
    purpose="choose the minimal activation repair",
    source_ref="task://tool-activation/qhug-repair-choice",
):
    return {
        "kind": "IMPLEMENT",
        "operation": "activate_selected_existing_tool",
        "target_ref": target_ref,
        "payload": {"tool_name": tool_name, "purpose": purpose},
        "source_refs": [source_ref],
        "readiness": 1,
        "gain": 2,
        "independence": 1,
        "bridge": 2,
        "cost": 1,
        "resource_cost": 1,
        "delta_j": 2,
        "information_gain": 1,
        "option_value": 1,
        "evidence": 1,
        "connection": 2,
        "replay": 2,
        "navigation": 1,
        "reconstruction": 1,
        "implementation": 2,
        "novelty": 0,
        "duplicate": 0,
        "fake": 0,
        "bloat": 0,
        "unsupported": 0,
        "unhandled_contradiction": 0,
        "coordinate_loss": 0,
        "required_capabilities": ["analysis"],
        "collective_metrics": {
            "utility": 0.95,
            "gap": 0.8,
            "bridge_value": 1.0,
            "saturation": 0.0,
            "urgency": 0.8,
        },
    }


class ToolActivationConsumerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db")
        self.server = Server(self.tmp.name)
        self.consumer = CanonicalToolActivationConsumer(self.server)
        self.worker = {"id": "ACTIVATOR", "capabilities": ["analysis"], "load": 0}

    def tearDown(self):
        self.server.store.close()
        self.tmp.close()

    @staticmethod
    def verify_qhug(result):
        optimum = result["optimum"]
        witnesses = [row["witness"] for row in optimum["profiles"]]
        passed = optimum["score"] == 9 and ["BIND_RESULT", "USE_CANONICAL_DISPATCH"] in witnesses
        return {
            "passed": passed,
            "observation": "QHUG selected canonical dispatch + result binding and rejected the conflicting parallel executor",
        }

    def activate(
        self,
        tool_name,
        tool_arguments,
        *,
        task_ref,
        purpose,
        verify_result,
        replay_safe=False,
    ):
        return self.consumer.activate(
            task_ref=task_ref,
            seed={"goal": purpose},
            candidate=measured_candidate(
                f"tool:{tool_name}",
                tool_name=tool_name,
                purpose=purpose,
                source_ref=task_ref,
            ),
            tool_name=tool_name,
            tool_arguments=tool_arguments,
            workers=[self.worker],
            collective_signals={"reuse": 1, "evidence_sensitivity": 1, "coupling": 0.2},
            verify_result=verify_result,
            replay_safe=replay_safe,
        )

    def assert_witnessed_without_reuse(self, out):
        for stage, reached in out["lifecycle"].items():
            if stage != "REUSED":
                self.assertTrue(reached, (stage, out["lifecycle"]))
        self.assertFalse(out["lifecycle"]["REUSED"])

    def test_selected_qhug_tool_reaches_complete_lifecycle_and_safe_reuse(self):
        out = self.activate(
            TOOL_NAME,
            QHUG_ACTIVATION_SPEC,
            task_ref="task://tool-activation/qhug-repair-choice",
            purpose="activate existing tools through the canonical runtime path",
            verify_result=self.verify_qhug,
            replay_safe=True,
        )
        self.assertEqual(out["final_cycle"]["status"], "COMPLETE")
        self.assertTrue(all(out["lifecycle"].values()), out["lifecycle"])
        self.assertTrue(out["runtime_usage_observed"])
        self.assertTrue(out["reuse_evidence"]["stable_result_digest"])
        self.assertEqual(out["result_digest"], out["replay_result_digest"])
        receipt = out["at_test"]["state"]["artifacts"]["execution_receipt"]
        self.assertEqual(receipt["tool_name"], TOOL_NAME)
        self.assertEqual(receipt["result_digest"], out["result_digest"])
        self.assertEqual(receipt["result"], out["result"])
        self.assertEqual(receipt["authority"], "IN_PROCESS_MCP_OBSERVATION_ONLY")
        self.assertEqual(out["result"]["optimum"]["score"], 9)

    def test_existing_tool_chain_migrates_verifies_and_consumes_health_replays(self):
        migration = self.activate(
            "athena_schema_migrate",
            {"actor": "canonical-tool-activation-consumer"},
            task_ref="task://tool-activation/schema-migrate",
            purpose="apply the runtime's explicit additive schema migration before organism health synthesis",
            verify_result=lambda result: {
                "passed": result.get("status") == "APPLIED"
                and result.get("to_version") == 2
                and result.get("verification", {}).get("status") == "PASS",
                "observation": "schema migration reached v2 and its built-in required table/column verification passed",
            },
        )
        self.assert_witnessed_without_reuse(migration)

        schema_verify = self.activate(
            "athena_schema_verify",
            {},
            task_ref="task://tool-activation/schema-verify",
            purpose="independently verify the migrated runtime schema through the installed verification tool",
            verify_result=lambda result: {
                "passed": result.get("status") == "PASS"
                and result.get("up_to_date") is True
                and not result.get("missing_required_tables")
                and not result.get("missing_required_columns"),
                "observation": "independent schema verifier observed current v2 state with no required table or column defects",
            },
            replay_safe=True,
        )
        self.assertTrue(all(schema_verify["lifecycle"].values()), schema_verify["lifecycle"])
        self.assertTrue(schema_verify["reuse_evidence"]["stable_result_digest"])
        self.assertEqual(schema_verify["result_digest"], schema_verify["replay_result_digest"])

        self_test = self.activate(
            "athena_self_test",
            {"replay_limit": 10, "run_composition_probes": True},
            task_ref="task://tool-activation/organism-health",
            purpose="consume the activated runtime state and replay prior persisted work as organism health evidence",
            verify_result=lambda result: {
                "passed": result.get("status") == "PASS"
                and all(value == "PASS" for value in result.get("gates", {}).values())
                and not result.get("replay_failures")
                and result.get("replay_samples", {}).get("cycle", {}).get("status") == "PASS"
                and result.get("replay_samples", {}).get("cycle", {}).get("checked", 0) >= 3,
                "observation": "organism self-test passed surface/composition/schema/omega/replay gates and replayed the prior activation cycles",
            },
        )
        self.assert_witnessed_without_reuse(self_test)
        self.assertEqual(self_test["result"]["status"], "PASS")
        self.assertEqual(self_test["result"]["replay_failures"], [])
        self.assertGreaterEqual(self_test["result"]["replay_samples"]["cycle"]["checked"], 3)
        self.assertTrue(migration["runtime_usage_observed"])
        self.assertFalse(schema_verify["runtime_usage_observed"])
        self.assertFalse(self_test["runtime_usage_observed"])

    def test_public_polycoordinate_derivation_chain_is_selected_consumed_and_reused(self):
        semantic = {
            "kind": "ARTIFACT",
            "domain": "TOOL_ACTIVATION",
            "verb": "WITNESS",
            "object_name": "CANONICAL_TRANSFORM_CHAIN",
            "method": "POLYCOORDINATE_CRYSTAL",
            "input_contract": {"source": "object"},
            "output_contract": {"coordinate": "object"},
        }
        crystal = self.activate(
            "athena_crystallize_output",
            {
                "semantic": semantic,
                "text": "Canonical transform activation witness.",
                "native_locator": "task://tool-activation/coordinate-derivation",
                "agent": "ACTIVATOR",
                "task": "activate declared coordinate transforms",
                "seq": 1,
                "coordinates": {"ACTIVATION_COPY": {"status": "UNKNOWN", "family": "TEST"}},
            },
            task_ref="task://tool-activation/crystallize-transform-subject",
            purpose="materialize a real crystal subject for the existing polycoordinate transform tools",
            verify_result=lambda result: {
                "passed": str(result.get("crystal_id", "")).startswith("CRYS.")
                and result.get("manifest", {}).get("coordinates", {}).get("KC144", {}).get("status") == "RESOLVED",
                "observation": "crystallization created an addressable subject with a resolved KC144 coordinate",
            },
        )
        self.assert_witnessed_without_reuse(crystal)
        oid = crystal["result"]["manifest"]["identity"]["OID"]

        forward = self.activate(
            "athena_register_transform",
            {
                "src_chart": "KC144",
                "dst_chart": "ACTIVATION_COPY",
                "status": "TESTED",
                "mode": "ISOMORPHISM",
                "program": {"op": "identity"},
                "metric": {"type": "EXACT"},
                "actor": "canonical-tool-activation-consumer",
            },
            task_ref="task://tool-activation/register-forward-transform",
            purpose="register an already-supported safe declarative identity derivation from KC144 into the activation chart",
            verify_result=lambda result: {
                "passed": result.get("status") == "TESTED"
                and result.get("mode") == "ISOMORPHISM"
                and result.get("src_chart") == "KC144"
                and result.get("dst_chart") == "ACTIVATION_COPY",
                "observation": "forward transform is TESTED, derivational and bound to the intended chart pair",
            },
        )
        self.assert_witnessed_without_reuse(forward)

        derived = self.activate(
            "athena_apply_transform",
            {
                "subject_id": oid,
                "src_chart": "KC144",
                "dst_chart": "ACTIVATION_COPY",
                "persist": True,
                "actor": "canonical-tool-activation-consumer",
            },
            task_ref="task://tool-activation/apply-forward-transform",
            purpose="execute the declared transform over the crystal and persist its derived target coordinate",
            verify_result=lambda result: {
                "passed": result.get("status") == "DERIVED_NO_TARGET"
                and result.get("comparison", {}).get("status") == "NO_RESOLVED_TARGET"
                and result.get("result") is not None,
                "observation": "the runtime derived a target value instead of substituting a lookup result",
            },
        )
        self.assert_witnessed_without_reuse(derived)

        inverse = self.activate(
            "athena_register_transform",
            {
                "src_chart": "ACTIVATION_COPY",
                "dst_chart": "KC144",
                "status": "TESTED",
                "mode": "ISOMORPHISM",
                "program": {"op": "identity"},
                "metric": {"type": "EXACT"},
                "actor": "canonical-tool-activation-consumer",
            },
            task_ref="task://tool-activation/register-inverse-transform",
            purpose="register the declared inverse derivation needed for a closed executable coordinate route",
            verify_result=lambda result: {
                "passed": result.get("status") == "TESTED"
                and result.get("mode") == "ISOMORPHISM"
                and result.get("src_chart") == "ACTIVATION_COPY"
                and result.get("dst_chart") == "KC144",
                "observation": "inverse transform is TESTED, derivational and bound to the intended chart pair",
            },
        )
        self.assert_witnessed_without_reuse(inverse)

        route = self.activate(
            "athena_apply_transform_route",
            {
                "subject_id": oid,
                "route": ["KC144", "ACTIVATION_COPY", "KC144"],
                "actor": "canonical-tool-activation-consumer",
            },
            task_ref="task://tool-activation/execute-closed-transform-route",
            purpose="execute the closed derivational route and measure rather than assume its holonomy defect",
            verify_result=lambda result: {
                "passed": result.get("all_derivational") is True
                and result.get("holonomy", {}).get("metric") == 0.0
                and all(step.get("mode") == "ISOMORPHISM" for step in result.get("steps", [])),
                "observation": "closed route executed only derivational edges and measured zero holonomy defect",
            },
        )
        self.assert_witnessed_without_reuse(route)

        matrix = self.activate(
            "athena_coordinate_matrix",
            {"subject_id": oid},
            task_ref="task://tool-activation/consume-transform-matrix",
            purpose="consume the persisted derivations, execution history and holonomy through the public coordinate matrix",
            verify_result=lambda result: {
                "passed": result.get("derivation_coverage", 0) > 0
                and any(obs.get("metric") == 0.0 for obs in result.get("holonomy_observations", []))
                and len(result.get("recent_executions", [])) >= 2,
                "observation": "coordinate matrix consumed nonzero derivation coverage, zero-defect holonomy and recorded executions",
            },
            replay_safe=True,
        )
        self.assertTrue(all(matrix["lifecycle"].values()), matrix["lifecycle"])
        self.assertEqual(matrix["result_digest"], matrix["replay_result_digest"])
        self.assertTrue(matrix["reuse_evidence"]["stable_result_digest"])

    def test_candidate_binding_mismatch_fails_before_execution(self):
        with self.assertRaises(ToolActivationError):
            self.consumer.activate(
                task_ref="task://tool-activation/mismatch",
                seed="S",
                candidate=measured_candidate("tool:athena_qhug_kernel_analyze"),
                tool_name=TOOL_NAME,
                tool_arguments=QHUG_ACTIVATION_SPEC,
                workers=[self.worker],
            )

    def test_cycle_tools_are_not_recursively_executable(self):
        with self.assertRaises(ValueError):
            self.consumer.activate(
                task_ref="task://tool-activation/recursion",
                seed="S",
                candidate=measured_candidate(
                    "tool:athena_cycle_recent",
                    tool_name="athena_cycle_recent",
                    purpose="prove recursive cycle execution is blocked",
                    source_ref="task://tool-activation/recursion",
                ),
                tool_name="athena_cycle_recent",
                tool_arguments={"limit": 1},
                workers=[self.worker],
            )


if __name__ == "__main__":
    unittest.main()
