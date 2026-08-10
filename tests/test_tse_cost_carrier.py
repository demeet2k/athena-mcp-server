from __future__ import annotations

from pathlib import Path

from athena_mcp.tse_cost_carrier import COST_CARRIER_VERSION, REENTRY_COST_MARKER, _normalize_cost
from tests.test_tse_circulation import TseCirculationTests, _run, _write


class TseCostCarrierNormalizationTests(TseCirculationTests.__bases__[0]):
    def test_normalize_known_and_unknown(self):
        self.assertEqual({"known": True, "total": 2.5}, _normalize_cost({"known": True, "total": 2.5}))
        self.assertEqual({"known": False}, _normalize_cost({"known": False}))
        self.assertEqual({"known": False}, _normalize_cost({"known": False, "total": "UNKNOWN"}))

    def test_normalize_rejects_false_precision_and_bad_totals(self):
        bad = [
            {},
            {"known": "yes", "total": 1},
            {"known": False, "total": 0},
            {"known": True, "total": -1},
            {"known": True, "total": float("nan")},
            {"known": True, "total": True},
            {"known": True, "total": 1, "tokens": 2},
        ]
        for value in bad:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    _normalize_cost(value)


class TseCostCarrierCompleteTests(TseCirculationTests):
    """Reuse the exact real-Git circulation fixture but carry rehydration cost."""

    def advance_productive_rehydration(self):
        loop_result = self.reentry_started["rehydration"]
        root = Path(self.server.git.root)
        _write(root, "reentry-work.txt", "observed bounded productive work\n")
        _run(root, "add", "reentry-work.txt")
        _run(root, "commit", "-m", "perform productive reentry work with carried cost")
        _run(root, "push", "origin", "master")

        loop = self.server.aor_development.transport.tse_helix.reentry._loop_runtime()
        result = loop.advance(
            loop_id=loop_result["loop_id"],
            expected_checkpoint_head=loop_result["checkpoint_head"],
            expected_state_digest=loop_result["state_digest"],
            expected_prompt_digest=loop_result["prompt_digest"],
            actor="observer",
            completion={
                "status": "PARTIAL",
                "observed": True,
                "terminal": False,
                "hard_hold": False,
                "summary": "one bounded productive rehydration step completed",
                "progress_delta": 1.0,
                "cost": {"known": True, "total": 0.3},
                "passes": [
                    {"kind": "reconstruct", "summary": "reconstructed exact shared coordinates", "evidence_refs": []},
                    {"kind": "execute", "summary": "committed bounded work", "evidence_refs": ["git:reentry-work"]},
                    {"kind": "verify", "summary": "observed work commit and push", "evidence_refs": ["git:shared"]},
                ],
                "tests": [{"name": "fixture", "status": "PASS", "evidence_ref": "test:fixture"}],
                "evidence_refs": ["git:reentry-work"],
                "residuals": ["spawn next bounded child"],
                "next_task": "spawn next bounded child",
                "handoff_to": None,
            },
            shared_remote_mode="REQUIRED",
        )
        self.assertEqual("ACTIVE", result["status"], result)
        self.assertEqual(0, result["no_progress_count"])
        return result

    def test_reentry_cost_is_persisted_but_not_presented_as_stop_semantics(self):
        self.assertEqual({"known": True, "total": 0.2}, self.reentry_started["reentry_cost_carrier"])
        prompt = self.reentry_started["rehydration"]["compiled_self_prompt"]
        self.assertNotIn(REENTRY_COST_MARKER, prompt)
        loop = self.server.aor_development.transport.tse_helix.reentry._loop_runtime()
        state, _ = loop._read_state(self.loop_id)
        markers = [
            value for value in state.get("stop_conditions") or []
            if isinstance(value, str) and value.startswith(REENTRY_COST_MARKER)
        ]
        self.assertEqual(1, len(markers))

    def test_complete_cost_sidecar_closes_structural_denominator(self):
        self.assertEqual({"known": True, "total": 0.2}, self.reentry_started["reentry_cost_carrier"])
        result = self.tool("athena_tse_circulation_observe", self.observe_args(cycle_id="CYCLE.COST.COMPLETE"))
        self.assertEqual("TSE_CIRCULATION_OBSERVED", result["status"], result)
        self.assertEqual("TSE_COST_CARRIER_OBSERVED", result["cost_carrier_status"])
        sidecar = result["cost_carrier"]
        self.assertEqual(COST_CARRIER_VERSION, sidecar["version"])
        self.assertTrue(sidecar["cost_complete"])
        self.assertEqual({"known": True, "total": 0.2}, sidecar["reentry_start_cost"])
        self.assertAlmostEqual(0.2, sidecar["known_reentry_control_cost_total"], places=9)
        self.assertAlmostEqual(0.3, sidecar["known_rehydration_cost_total"], places=9)
        self.assertAlmostEqual(1.6, sidecar["known_source_bound_tse_cost_total"], places=9)
        self.assertAlmostEqual(2.1, sidecar["known_total_carried_cost"], places=9)
        self.assertAlmostEqual(2.1, sidecar["total_carried_cost"], places=9)
        self.assertAlmostEqual(9.0 / 2.1, sidecar["incorporated_delta_per_total_cost"], places=9)
        self.assertEqual([], sidecar["unknown_cost_components"])
        self.assertFalse(sidecar["host_resource_cost_complete"])
        self.assertEqual("UNKNOWN", sidecar["incorporated_delta_per_host_resource_cost"])
        self.assertEqual("UNKNOWN", sidecar["causal_effect"])
        self.assertFalse(sidecar["execution_authority"])

    def test_cost_sidecar_replay_is_idempotent(self):
        first = self.tool("athena_tse_circulation_observe", self.observe_args(cycle_id="CYCLE.COST.REPLAY"))
        self.assertEqual("TSE_COST_CARRIER_OBSERVED", first["cost_carrier_status"])
        head = self.server.git.head()
        replay = self.tool("athena_tse_circulation_observe", self.observe_args(cycle_id="CYCLE.COST.REPLAY"))
        self.assertEqual("TSE_CIRCULATION_ALREADY_OBSERVED", replay["status"], replay)
        self.assertEqual("TSE_COST_CARRIER_ALREADY_OBSERVED", replay["cost_carrier_status"])
        self.assertEqual(first["cost_carrier"]["cost_carrier_digest"], replay["cost_carrier"]["cost_carrier_digest"])
        self.assertEqual(head, self.server.git.head())

    def test_report_does_not_invent_pending_denominator_or_total_cost(self):
        self.tool("athena_tse_circulation_observe", self.observe_args(cycle_id="CYCLE.REPORT"))
        report = self.tool("athena_tse_circulation_report", {"mission_id": self.mission})
        self.assertEqual("TSE_CIRCULATION_REPORT", report["status"], report)
        self.assertEqual(1, report["closed_cycles"])
        self.assertEqual("UNKNOWN", report["pending_cycles"])
        self.assertEqual("UNKNOWN", report["closure_rate"])
        self.assertTrue(report["cost_complete"])
        self.assertAlmostEqual(2.1, report["total_carried_cost"], places=9)
        self.assertAlmostEqual(9.0 / 2.1, report["incorporated_delta_per_total_cost"], places=9)
        self.assertFalse(report["host_resource_cost_complete"])
        self.assertEqual("UNKNOWN", report["incorporated_delta_per_host_resource_cost"])
        self.assertEqual("UNKNOWN", report["causal_effect"])

    def test_schema_and_resource_expose_cost_carrier_without_host_truth(self):
        tools = {row["name"]: row for row in self.rpc("tools/list")["result"]["tools"]}
        completion = tools["athena_rehydration_advance"]["inputSchema"]["properties"]["completion"]
        self.assertIn("cost", completion["properties"])
        resource = self.server.aor_development.transport.tse_circulation.resource()
        self.assertEqual(COST_CARRIER_VERSION, resource["cost_carrier_version"])
        self.assertEqual("DECLARED_STRUCTURAL_ACCOUNTING_ONLY", resource["cost_authority"])
        self.assertFalse(resource["host_resource_cost_complete"])
        self.assertEqual("UNKNOWN", resource["incorporated_delta_per_host_resource_cost"])


if __name__ == "__main__":
    import unittest

    unittest.main()
