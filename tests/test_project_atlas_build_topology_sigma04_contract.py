from __future__ import annotations

import json
import unittest
from pathlib import Path

from athena_mcp.project_atlas_build_topology import (
    BUILD_EDGE_KINDS,
    BUILD_EDGE_PREFIX,
    BUILD_GRAPH_PREFIX,
    BUILD_LAWS,
    BUILD_SCHEMA,
    BUILD_VERSION,
    ENTRYPOINT_EDGE,
    SYMBOL_PREFIX,
    SYMBOL_SCHEMA,
)

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "spec" / "SIGMA04_BUILD_TOPOLOGY_V1.json"


class Sigma04BuildTopologyContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = json.loads(CONTRACT.read_text(encoding="utf-8"))

    def test_exact_parent_and_work_order(self):
        c = self.c
        self.assertEqual(c["schema"], "ATHENA.SIGMA04.BUILD_TOPOLOGY.CONTRACT.v1")
        self.assertEqual(c["status"], "CANDIDATE_CHILD_OF_QUALIFIED_UNMERGED_V3")
        self.assertEqual(c["version"], BUILD_VERSION)
        self.assertEqual(c["coordinate"], "SIGMA04.BUILD-TOPOLOGY")
        self.assertEqual(c["private_work_order"], {"repository": "demeet2k/Athena", "issue": 528})
        self.assertEqual(c["parent_v3"]["pull_request"], 335)
        self.assertEqual(c["parent_v3"]["head"], "48a9af3deef7bb5db31fa7188b61b5e0cd0b932d")
        self.assertEqual(c["parent_v3"]["qualification_ci_run"], 31336608806)
        self.assertEqual(c["parent_v3"]["qualification_release_v34_run"], 31336608789)

    def test_identity_namespaces_match_implementation(self):
        i = self.c["identity"]
        self.assertEqual(SYMBOL_SCHEMA, "ATHENA.SIGMA04.PYTHON_SYMBOL.v1")
        self.assertEqual(BUILD_SCHEMA, "ATHENA.SIGMA04.BUILD_TOPOLOGY.v1")
        self.assertEqual(i["symbol_prefix"], SYMBOL_PREFIX)
        self.assertEqual(i["build_edge_prefix"], BUILD_EDGE_PREFIX)
        self.assertEqual(i["build_graph_prefix"], BUILD_GRAPH_PREFIX)
        self.assertEqual(i["symbol_identity"], "PSYM = digest(PVTX, qualified_symbol, source_span_digest)")
        self.assertEqual(i["authority"], "NONE")

    def test_symbol_index_contract_is_bounded_and_exact(self):
        s = self.c["symbol_index"]
        self.assertEqual(s["carrier"], "Python AST")
        self.assertEqual(s["plane_scope"], ["configured_git", "runtime_git"])
        self.assertEqual(s["duplicate_binding"], "HOLD_AMBIGUOUS_SYMBOL")
        self.assertEqual(s["source_failure"], "HOLD_SYMBOL_SOURCE")
        self.assertEqual(
            s["source_span_digest_basis"],
            ["exact Git object SHA", "symbol kind", "AST source span", "exact AST source segment"],
        )

    def test_entrypoint_contract_matches_edge_kind_and_extractor(self):
        e = self.c["entrypoint_extractor"]
        self.assertEqual(BUILD_EDGE_KINDS, {ENTRYPOINT_EDGE})
        self.assertEqual(e["kind"], ENTRYPOINT_EDGE)
        self.assertEqual(e["extractor"], "pep621_toml_entrypoint_to_python_ast_symbol_v1")
        self.assertEqual(e["syntax"], "module:top_level_attribute")
        self.assertIn("same exact <plane,repo,head>", e["module_resolution_scope"])
        self.assertEqual(e["edge_evidence"], "EXACT_TOML_DECLARATION+EXACT_PVTX_MODULE+PYTHON_AST_SYMBOL")
        self.assertEqual(e["nested_attribute"], "HOLD_NESTED_ENTRYPOINT_SYMBOL")

    def test_live_repository_witness_locks_real_script_targets(self):
        scripts = self.c["live_repository_witness"]["expected_scripts"]
        self.assertEqual(set(scripts), {"athena-mcp", "athena-project-atlas"})
        self.assertEqual(scripts["athena-mcp"]["target"], "athena_mcp.server:main")
        self.assertEqual(scripts["athena-mcp"]["qualified_symbol"], "athena_mcp.server.main")
        self.assertEqual(scripts["athena-project-atlas"]["target"], "athena_mcp.project_atlas:_main")
        self.assertEqual(scripts["athena-project-atlas"]["qualified_symbol"], "athena_mcp.project_atlas._main")

    def test_workflow_layer_is_explicitly_deferred(self):
        d = self.c["deferred"]
        self.assertEqual(d["workflow_yaml"], "DEFERRED_PENDING_PARSER_AND_SHELL_AMBIGUITY_CONTRACT")
        self.assertIn("hidden YAML dependency", d["reason"])
        self.assertIn("WORKFLOW_STEP_USES_ACTION", d["workflow_edge_kinds"])
        self.assertIn("WORKFLOW_SELECTS_TEST", d["workflow_edge_kinds"])

    def test_hold_lattice_and_laws_are_fail_closed(self):
        holds = set(self.c["holds"])
        required = {
            "HOLD_SYMBOL_SOURCE",
            "HOLD_AMBIGUOUS_SYMBOL",
            "HOLD_PYPROJECT_SOURCE",
            "HOLD_ENTRYPOINT_SYNTAX",
            "HOLD_ENTRYPOINT_MODULE",
            "HOLD_AMBIGUOUS_MODULE",
            "HOLD_ENTRYPOINT_SYMBOL",
            "HOLD_NESTED_ENTRYPOINT_SYMBOL",
        }
        self.assertEqual(holds, required)
        laws = set(self.c["laws"])
        self.assertTrue(set(BUILD_LAWS).issubset(laws))
        self.assertIn("COMMAND_TEXT != EXECUTED_EFFECT", laws)
        self.assertIn("UNRESOLVED_INTERPOLATION -> CONSERVE_UNKNOWN", laws)

    def test_promotion_is_non_authoritative(self):
        p = self.c["promotion"]
        self.assertEqual(p["standing"], "HOLD_PENDING_SIGMA04_EXACT_HEAD_QUALIFICATION_AND_PRIVATE_REVIEW")
        self.assertFalse(p["canonical_rpc_promotion"])
        self.assertFalse(p["package_version_change"])
        self.assertFalse(p["publication"])
        self.assertFalse(p["deployment"])


if __name__ == "__main__":
    unittest.main()
