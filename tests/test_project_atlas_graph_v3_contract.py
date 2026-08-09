from __future__ import annotations

import json
import unittest
from pathlib import Path

from athena_mcp.project_atlas_graph import (
    EDGE_KINDS,
    GEOMETRIC_EDGE_KINDS,
    GRAPH_ID_PREFIX,
    GRAPH_LAWS,
    GRAPH_SCHEMA,
    GRAPH_VERSION,
    MAX_DEPTH,
    MAX_EXPANSIONS,
    MAX_QUERY_LIMIT,
    STRUCTURAL_EDGE_KINDS,
)

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "spec" / "KC144_PROJECT_RELATION_GRAPH_V3.json"


class ProjectAtlasGraphV3ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = json.loads(CONTRACT.read_text(encoding="utf-8"))

    def test_exact_identity_and_parent_frontier(self):
        c = self.c
        self.assertEqual(c["schema"], "ATHENA.KC144.PROJECT_RELATION_GRAPH.CONTRACT.v3")
        self.assertEqual(c["version"], GRAPH_VERSION)
        self.assertEqual(c["status"], "CANDIDATE_CHILD_OF_UNMERGED_V2")
        self.assertEqual(c["private_work_order"], {"repository": "demeet2k/Athena", "issue": 508})
        self.assertEqual(c["parent_v2"]["pull_request"], 310)
        self.assertEqual(c["parent_v2"]["head_at_branch_creation"], "c7445bcd70a354e5deb912add6716d7e5191e02c")
        self.assertEqual(c["integration"]["branch"], "agent/kc144-project-atlas-graph-v3")

    def test_graph_and_edge_namespaces_match_implementation(self):
        i = self.c["identity"]
        self.assertEqual(GRAPH_SCHEMA, "ATHENA.KC144.PROJECT_RELATION_GRAPH.v3")
        self.assertEqual(i["snapshot_prefix"], "PATLASV2.")
        self.assertEqual(i["graph_prefix"], GRAPH_ID_PREFIX)
        self.assertEqual(i["edge_prefix"], "PEDGE.")
        self.assertEqual(i["vertex_identity"], "Project Atlas POID")
        self.assertEqual(i["authority"], "NONE")

    def test_edge_lattice_is_exact_and_geometric_is_not_structural(self):
        declared_structural = set(self.c["edge_kinds"]["structural_default"])
        declared_geometric = set(self.c["edge_kinds"]["geometric_optional"])
        self.assertEqual(declared_structural, STRUCTURAL_EDGE_KINDS)
        self.assertEqual(declared_geometric, GEOMETRIC_EDGE_KINDS)
        self.assertEqual(declared_structural | declared_geometric, EDGE_KINDS)
        self.assertTrue(declared_structural.isdisjoint(declared_geometric))
        self.assertNotIn("DEPENDS_ON", EDGE_KINDS)
        self.assertEqual(set(self.c["extractors"]), EDGE_KINDS)
        self.assertEqual(set(self.c["evidence_classes"]), EDGE_KINDS)

    def test_query_bounds_and_no_hidden_scalarization(self):
        q = self.c["queries"]
        self.assertFalse(q["mcp_rpc_promoted"])
        self.assertEqual(q["max_page"], MAX_QUERY_LIMIT)
        self.assertEqual(q["max_depth"], MAX_DEPTH)
        self.assertEqual(q["max_expansions"], MAX_EXPANSIONS)
        self.assertTrue(q["dijkstra_requires_explicit_weights"])
        self.assertEqual(q["default_route_edge_domain"], "structural_default")

    def test_graph_laws_are_machine_locked(self):
        laws = set(self.c["laws"])
        self.assertTrue(set(GRAPH_LAWS).issubset(laws))
        for law in (
            "STRUCTURAL_GRAPH_ROUTE != KC144_GEOMETRIC_ROUTE != EXECUTION",
            "V3_CHILD_HEAD != ACCEPTED_V2_ANCESTRY",
        ):
            self.assertIn(law, laws)

    def test_hold_lattice_and_promotion_are_fail_closed(self):
        required = {
            "HOLD_EDGE",
            "HOLD_STALE_SNAPSHOT",
            "HOLD_STALE_GRAPH",
            "HOLD_UNKNOWN_VERTEX",
            "HOLD_EXPANSION_LIMIT",
            "HOLD_DEPTH_LIMIT",
            "HOLD_NO_PATH",
        }
        self.assertEqual(set(self.c["hold_statuses"]), required)
        p = self.c["promotion"]
        self.assertEqual(p["standing"], "HOLD_PENDING_V2_ACCEPTANCE_REBASE_AND_V3_QUALIFICATION")
        self.assertFalse(p["canonical_rpc_promotion"])
        self.assertFalse(p["package_version_change_in_child"])
        self.assertFalse(p["publication"])
        self.assertFalse(p["deployment"])


if __name__ == "__main__":
    unittest.main()
