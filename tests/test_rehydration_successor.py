import unittest

from athena_mcp.rehydration_loop import _state_digest
from athena_mcp.rehydration_successor import (
    SuccessorCompiler,
    install_successor_extension,
)


class _Runtime:
    def __init__(self):
        self.state = {
            "artifact": "ATHENA.REHYDRATION.LOOP.V1",
            "loop_id": "LOOP-1",
            "status": "ACTIVE",
            "goal": "Complete the whole Git framework upgrade",
            "task": "Implement the current bounded slice",
            "step_index": 3,
            "last_completion": None,
        }
        self.state["state_digest"] = _state_digest(self.state)

    def _read_state(self, loop_id):
        if loop_id != self.state["loop_id"]:
            raise ValueError("loop not found")
        return dict(self.state), {"base": "prompts/rehydration/LOOP-1"}


class SuccessorCompilerTests(unittest.TestCase):
    def setUp(self):
        self.runtime = _Runtime()
        self.compiler = SuccessorCompiler(self.runtime)

    def compile(self, completion, candidates=None, policy=None):
        return self.compiler.compile(
            loop_id="LOOP-1",
            expected_state_digest=self.runtime.state["state_digest"],
            completion=completion,
            candidates=candidates,
            policy=policy,
        )

    def test_residual_dominates_partial_continuation(self):
        baton = self.compile({
            "status": "PARTIAL",
            "residuals": ["Implement exact-head promotion witness"],
        })
        self.assertEqual(baton["status"], "SELECTED")
        self.assertEqual(baton["selected"]["task"], "Implement exact-head promotion witness")
        self.assertEqual(baton["selected"]["source"], "COMPLETION_RESIDUAL")
        self.assertIn(baton["selected"]["candidate_id"], baton["pareto_candidate_ids"])

    def test_equal_explicit_candidates_preserve_ambiguity(self):
        baton = self.compile(
            {"status": "SUCCEEDED", "residuals": []},
            candidates=["Build transport A", "Build transport B"],
        )
        self.assertEqual(baton["status"], "AMBIGUOUS")
        self.assertIsNone(baton["selected"])
        self.assertEqual(len(baton["ties"]), 2)
        self.assertIn("preserve ambiguity", baton["selection_reason"])

    def test_explicit_metrics_can_select_without_becoming_authority(self):
        baton = self.compile(
            {"status": "SUCCEEDED", "residuals": []},
            candidates=[
                {
                    "task": "High leverage repair",
                    "metrics": {
                        "utility": 1.0,
                        "dependency_unblocking": 1.0,
                        "uncertainty_reduction": 0.9,
                        "novelty": 0.7,
                        "risk": 0.1,
                        "cost": 0.2,
                        "repetition": 0.0,
                    },
                },
                {
                    "task": "Low leverage cleanup",
                    "metrics": {
                        "utility": 0.2,
                        "dependency_unblocking": 0.1,
                        "uncertainty_reduction": 0.1,
                        "novelty": 0.1,
                        "risk": 0.8,
                        "cost": 0.8,
                        "repetition": 0.8,
                    },
                },
            ],
        )
        self.assertEqual(baton["status"], "SELECTED")
        self.assertEqual(baton["selected"]["task"], "High leverage repair")
        self.assertTrue(baton["selected"]["routing_only"])
        self.assertIn("ROUTING_SCORE != AUTHORITY", baton["laws"])

    def test_candidate_order_does_not_change_baton_identity(self):
        completion = {"status": "SUCCEEDED", "residuals": []}
        a = self.compile(completion, candidates=["One", "Two"])
        b = self.compile(completion, candidates=["Two", "One"])
        self.assertEqual(a["baton_digest"], b["baton_digest"])
        self.assertEqual(a["pareto_candidate_ids"], b["pareto_candidate_ids"])

    def test_terminal_completion_emits_no_successor(self):
        baton = self.compile({"status": "SUCCEEDED", "terminal": True, "residuals": ["ignored"]})
        self.assertEqual(baton["status"], "TERMINAL")
        self.assertEqual(baton["candidates"], [])
        self.assertIsNone(baton["selected"])

    def test_stale_state_digest_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "STALE_OR_TAMPERED"):
            self.compiler.compile(
                loop_id="LOOP-1",
                expected_state_digest="bad",
                completion={"status": "SUCCEEDED", "residuals": []},
            )

    def test_extension_auto_steers_advance_and_documents_schema(self):
        class FakeRuntime(_Runtime):
            def advance(self, *args, **kwargs):
                return {"status": "ACTIVE", "completion": kwargs["completion"]}

            def resume(self, loop_id, include_prompt=True):
                return {"status": "RESUMED", "loop_id": loop_id}

            def call_tool(self, name, a):
                return {"legacy": name}

        runtime = FakeRuntime()
        tools = [{
            "name": "athena_rehydration_advance",
            "inputSchema": {"type": "object", "properties": {"completion": {"type": "object", "properties": {}}}},
        }]
        names = {"athena_rehydration_advance"}
        install_successor_extension(FakeRuntime, tools, names)

        out = runtime.advance(
            loop_id="LOOP-1",
            expected_state_digest=runtime.state["state_digest"],
            completion={
                "status": "SUCCEEDED",
                "observed": True,
                "summary": "finished current slice",
                "residuals": ["Build the next causal receipt"],
            },
        )
        self.assertEqual(out["successor_baton"]["status"], "SELECTED")
        self.assertEqual(out["completion"]["next_task"], "Build the next causal receipt")
        self.assertIn("successor_baton", out["completion"])
        self.assertIn("athena_rehydration_successor_preview", names)
        props = tools[0]["inputSchema"]["properties"]["completion"]["properties"]
        self.assertIn("self_steer", props)
        self.assertIn("successor_candidates", props)
        self.assertIn("successor_policy", props)

    def test_extension_routes_preview_tool(self):
        class FakeRuntime(_Runtime):
            def advance(self, *args, **kwargs):
                return kwargs

            def resume(self, loop_id, include_prompt=True):
                return {"status": "RESUMED"}

            def call_tool(self, name, a):
                return {"legacy": name}

        runtime = FakeRuntime()
        install_successor_extension(FakeRuntime, [], set())
        out = runtime.call_tool("athena_rehydration_successor_preview", {
            "loop_id": "LOOP-1",
            "expected_state_digest": runtime.state["state_digest"],
            "completion": {"status": "SUCCEEDED", "residuals": ["Next bounded slice"]},
        })
        self.assertEqual(out["status"], "SELECTED")
        self.assertEqual(out["selected"]["task"], "Next bounded slice")


if __name__ == "__main__":
    unittest.main()
