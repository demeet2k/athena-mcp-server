from __future__ import annotations

import json
import tempfile
import unittest

from athena_mcp.server import Server


EXPECTED_EXISTING = {
    "athena_cohesion_request_offer",
    "athena_cohesion_matchmake",
    "athena_cohesion_coalition",
    "athena_cohesion_solo_party_compare",
    "athena_cohesion_duplicate_guard",
}

CUT02_MISSING = {
    "athena_cohesion_consume",
    "athena_cohesion_dependency_cone",
    "athena_cohesion_outcome_credit",
    "athena_cohesion_pulse",
}


class ClosureCut02RedSurfaceTests(unittest.TestCase):
    """Intentionally RED against the frozen CUT-02 base.

    Run explicitly with:
      python -m unittest -v tests.red.test_closure_cut02_red

    This module is kept under tests/red so the ordinary repository test discovery
    is not made red merely by recording the pre-treatment defect witness.
    """

    def setUp(self):
        self.db = tempfile.NamedTemporaryFile(suffix=".db")
        self.server = Server(self.db.name)

    def tearDown(self):
        self.server.store.close()
        self.db.close()

    def tool_names(self):
        response = self.server.handle({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
        })
        return {tool["name"] for tool in response["result"]["tools"]}

    def cohesion_resource(self):
        response = self.server.handle({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "resources/read",
            "params": {"uri": "athena://cohesion/v1"},
        })
        return json.loads(response["result"]["contents"][0]["text"])

    def test_red_00_existing_cohesion_and_evidence_guard_are_present(self):
        names = self.tool_names()
        self.assertTrue(EXPECTED_EXISTING <= names)
        resource = self.cohesion_resource()
        self.assertEqual(resource["evidence_guard_version"], "COHESION.EVIDENCE.GUARD.1")
        self.assertEqual(resource["duplicate_guard_version"], "COHESION.DUPLICATE.GUARD.1")
        self.assertIn(
            "PARTIAL_MATCHED_SUBSET_OR_REUSED_EVIDENCE != SUFFICIENT_COMPARATIVE_EVIDENCE",
            resource["laws"],
        )

    def test_red_01_consume_surface_is_missing(self):
        # RED on the frozen base; GREEN only when C1-4 is actually registered.
        self.assertIn("athena_cohesion_consume", self.tool_names())

    def test_red_02_dependency_cone_surface_is_missing(self):
        # RED on the frozen base; the old C3-12 candidate is not current runtime state.
        self.assertIn("athena_cohesion_dependency_cone", self.tool_names())

    def test_red_03_outcome_credit_surface_is_missing(self):
        # RED on the frozen base; Party reward provenance is not generic outcome credit.
        self.assertIn("athena_cohesion_outcome_credit", self.tool_names())

    def test_red_04_collective_pulse_surface_is_missing(self):
        # RED on the frozen base; do not confuse this with QUEST::PULSE in Athena.
        self.assertIn("athena_cohesion_pulse", self.tool_names())

    def test_red_05_cohesion_resource_does_not_yet_advertise_cut02(self):
        # RED until all four runtime operators are discoverable from the canonical
        # Cohesion resource. This ensures implementation is not file-only/orphaned.
        resource = self.cohesion_resource()
        advertised = set(resource.get("tools") or [])
        self.assertTrue(CUT02_MISSING <= advertised)


if __name__ == "__main__":
    unittest.main()
