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


def measured_candidate(target_ref=F"tool:{TOOL_NAME}"):
    return {
        "kind": "IMPLEMENT",
        "operation": "activate_selected_existing_tool",
        "target_ref": target_ref,
        "payload": {"tool_name": TOOL_NAME, "purpose": "choose the minimal activation repair"},
        "source_refs": ["task://tool-activation/qhug-repair-choice"],
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

    def test_selected_qhug_tool_reaches_complete_lifecycle_and_safe_reuse(self):
        out = self.consumer.activate(
            task_ref="task://tool-activation/qhug-repair-choice",
            seed={"goal": "activate existing tools through the canonical runtime path"},
            candidate=measured_candidate(),
            tool_name=TOOL_NAME,
            tool_arguments=QHUG_ACTIVATION_SPEC,
            workers=[{"id": "ACTIVATOR", "capabilities": ["analysis"], "load": 0}],
            collective_signals={"reuse": 1, "evidence_sensitivity": 1, "coupling": 0.2},
            verify_result=self.verify_qhug,
            replay_safe=True,
        )
        self.assertEqual(out["final_cycle"]["status"], "COMPLETE")
        self.assertTrue(all(out["lifecycle"].values()), out["lifecycle"])
        self.assertTrue(out["runtime_usage_observed"])
        self.assertEqual(out["result_digest"], out["replay_result_digest"])
        receipt = out["at_test"]["state"]["artifacts"]["execution_receipt"]
        self.assertEqual(receipt["tool_name"], TOOL_NAME)
        self.assertEqual(receipt["result_digest"], out["result_digest"])
        self.assertEqual(receipt["result"], out["result"])
        self.assertEqual(receipt["authority"], "IN_PROCESS_MCP_OBSERVATION_ONLY")
        self.assertEqual(out["result"]["optimum"]["score"], 9)

    def test_candidate_binding_mismatch_fails_before_execution(self):
        with self.assertRaises(ToolActivationError):
            self.consumer.activate(
                task_ref="task://tool-activation/mismatch",
                seed="S",
                candidate=measured_candidate("tool:athena_qhug_kernel_analyze"),
                tool_name=TOOL_NAME,
                tool_arguments=QHUG_ACTIVATION_SPEC,
                workers=[{"id": "ACTIVATOR", "capabilities": ["analysis"], "load": 0}],
            )

    def test_cycle_tools_are_not_recursively_executable(self):
        with self.assertRaises(ValueError):
            self.consumer.activate(
                task_ref="task://tool-activation/recursion",
                seed="S",
                candidate=measured_candidate("tool:athena_cycle_recent"),
                tool_name="athena_cycle_recent",
                tool_arguments={"limit": 1},
                workers=[{"id": "ACTIVATOR", "capabilities": ["analysis"], "load": 0}],
            )


if __name__ == "__main__":
    unittest.main()
