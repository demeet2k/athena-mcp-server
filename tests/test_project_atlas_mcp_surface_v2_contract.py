from __future__ import annotations

import json
import unittest
from pathlib import Path

from athena_mcp.project_atlas_protocol import PROJECT_ATLAS_RESOURCE, PROJECT_ATLAS_TOOLS
from athena_mcp.project_atlas_surface import PROJECT_ATLAS_LAWS, PROJECT_ATLAS_MAX_PAGE, PROJECT_ATLAS_SURFACE_VERSION


ROOT=Path(__file__).resolve().parents[1]
CONTRACT_PATH=ROOT/"spec"/"KC144_PROJECT_ATLAS_MCP_SURFACE_V2.json"
SCHEMA_PATH=ROOT/"schemas"/"project_atlas_mcp_surface_v2.schema.json"


class ProjectAtlasMcpSurfaceV2ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract=json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.schema=json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    def test_identity_and_v1_ancestry_are_exact(self):
        c=self.contract
        self.assertEqual(c["schema"],"ATHENA.KC144.PROJECT_ATLAS.MCP_SURFACE.CONTRACT.v2")
        self.assertEqual(c["surface_version"],PROJECT_ATLAS_SURFACE_VERSION)
        self.assertEqual(c["status"],"CANDIDATE_CHILD_OF_UNMERGED_V1")
        self.assertEqual(c["base_v1"]["head"],"fc376ffa76864f173049164db9206295b96ec85b")
        self.assertEqual(c["base_v1"]["pull_request"],295)
        self.assertEqual(c["integration"]["child_pull_request"],310)
        self.assertEqual(c["integration"]["qualification_only_pull_request"],311)
        self.assertEqual(c["integration"]["law"],"QUALIFICATION_PR != INTEGRATION_PR")

    def test_declared_tool_resource_surface_matches_protocol(self):
        declared=set(self.contract["surface"]["tools"])
        actual={tool["name"] for tool in PROJECT_ATLAS_TOOLS}
        self.assertEqual(declared,actual)
        self.assertEqual(len(declared),4)
        self.assertEqual(self.contract["surface"]["resource"],PROJECT_ATLAS_RESOURCE["uri"])
        self.assertEqual(self.contract["surface"]["max_page"],PROJECT_ATLAS_MAX_PAGE)
        self.assertTrue(self.contract["surface"]["read_only"])
        self.assertFalse(self.contract["surface"]["self_metering"])

    def test_frontier_factorization_preserves_three_clocks(self):
        frontier=self.contract["frontier"]
        self.assertEqual(frontier["factorization"],["CONFIGURED_GIT_HEAD","RUNTIME_SOURCE_FRONTIER","LIVE_MCP_SURFACE_SIGNATURE"])
        self.assertEqual(frontier["configured_git_source"],"ATHENA_GIT_ROOT")
        self.assertEqual(frontier["bounded_retry"],1)
        self.assertEqual(frontier["unknown_runtime_tree_law"],"UNKNOWN_RUNTIME_TREE != EMPTY_RUNTIME_TREE")
        self.assertIn("ATHENA_RUNTIME_GIT_ROOT",frontier["runtime_source_priority"])
        self.assertIn("PACKAGE_SOURCE_CHECKOUT",frontier["runtime_source_priority"])
        self.assertIn("ATHENA_RUNTIME_REPOSITORY+ATHENA_RUNTIME_GIT_HEAD",frontier["runtime_source_priority"])
        self.assertEqual(frontier["runtime_source_priority"][-1],"HOLD_RUNTIME_PROVENANCE")

    def test_snapshot_and_plane_contract(self):
        snapshot=self.contract["snapshot"]
        self.assertEqual(snapshot["prefix"],"PATLASV2.")
        self.assertEqual(snapshot["authority"],"NONE")
        self.assertEqual(snapshot["law"],"PROJECT_ATLAS_SNAPSHOT_ID != PROMOTION_RECEIPT")
        self.assertEqual(self.contract["planes"],["configured_git","runtime_git","mcp"])
        self.assertEqual(self.contract["list_sources"],["all","git","configured_git","runtime_git","mcp"])
        self.assertIn("federation_digest",snapshot["basis"])
        self.assertIn("live_mcp_surface_signature",snapshot["basis"])

    def test_hold_lattice_is_explicit(self):
        holds=set(self.contract["hold_statuses"])
        required={
            "HOLD_GIT_UNAVAILABLE","HOLD_STALE_CONFIGURED_HEAD","HOLD_STALE_RUNTIME_HEAD","HOLD_RUNTIME_PROVENANCE",
            "HOLD_RUNTIME_TREE_UNAVAILABLE","HOLD_VOLATILE_FRONTIER","HOLD_NOT_FOUND","HOLD_AMBIGUOUS","HOLD_ROUTE_SOURCE","HOLD_ROUTE_DESTINATION",
        }
        self.assertEqual(holds,required)
        self.assertEqual(self.contract["resolve"]["ambiguous"],"HOLD_AMBIGUOUS")
        self.assertEqual(self.contract["resolve"]["not_found_runtime_tree_unknown"],"HOLD_RUNTIME_TREE_UNAVAILABLE")

    def test_runtime_implemented_laws_are_preserved_by_machine_contract(self):
        laws=set(self.contract["laws"])
        self.assertTrue(set(PROJECT_ATLAS_LAWS).issubset(laws))
        for law in (
            "V2_DEPENDS_ON_V1","GREEN_CHILD_HEAD != ACCEPTED_ANCESTRY","QUALIFICATION_PR != INTEGRATION_PR",
            "RPC_SURFACE_EXISTENCE != CANONICAL_RPC_PROMOTION","MOVING_PROJECT_FRONTIER -> BOUNDED_RETRY -> HOLD",
        ):
            self.assertIn(law,laws)

    def test_promotion_state_is_fail_closed(self):
        p=self.contract["promotion"]
        self.assertEqual(p["standing"],"HOLD_PENDING_V1_ACCEPTANCE_REBASE_AND_NEW_ABI_QUALIFICATION")
        self.assertFalse(p["package_version_change_in_child"])
        self.assertFalse(p["canonical_rpc_promotion"])
        self.assertFalse(p["publication"])
        self.assertFalse(p["deployment"])
        self.assertIn("new canonical package/protocol/release coordinate",p["requirements"])
        self.assertIn("exact runtime-source provenance configuration",p["requirements"])

    def test_schema_locks_core_contract_identity(self):
        s=self.schema
        self.assertEqual(s["properties"]["schema"]["const"],self.contract["schema"])
        self.assertEqual(s["properties"]["surface_version"]["const"],self.contract["surface_version"])
        self.assertEqual(s["properties"]["surface"]["properties"]["resource"]["const"],PROJECT_ATLAS_RESOURCE["uri"])
        self.assertEqual(s["properties"]["surface"]["properties"]["max_page"]["const"],PROJECT_ATLAS_MAX_PAGE)
        self.assertEqual(s["properties"]["promotion"]["properties"]["canonical_rpc_promotion"]["const"],False)


if __name__=="__main__":unittest.main()
