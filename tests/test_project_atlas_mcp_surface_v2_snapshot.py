from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

import athena_mcp.project_atlas_surface as surface_module
from athena_mcp.server import TOOLS, Server


def run(root: Path, *args: str) -> str:
    p=subprocess.run(["git","-C",str(root),*args],text=True,capture_output=True)
    if p.returncode:raise AssertionError(p.stderr or p.stdout)
    return p.stdout.strip()


class ProjectAtlasMcpSurfaceV2SnapshotTests(unittest.TestCase):
    def fixture(self):
        td=tempfile.TemporaryDirectory();self.addCleanup(td.cleanup);base=Path(td.name);root=base/"brain";root.mkdir()
        run(root,"init");run(root,"config","user.name","test");run(root,"config","user.email","test@example.invalid")
        run(root,"remote","add","origin","https://github.com/demeet2k/project-atlas-snapshot-fixture.git")
        for rel,text in {
            "alpha.txt":"a\n",
            "beta.txt":"b\n",
            "tool:athena_project_route":"typed namespace collision trap\n",
        }.items():
            path=root/rel;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text,encoding="utf-8")
        run(root,"add",".");run(root,"commit","-m","seed")
        return root,Server(str(base/"state.db"),git_root=root)

    def configured_record(self,server,path):
        page=server.call_tool("athena_project_list",{"source":"configured_git","path_prefix":path,"limit":20})
        rows=[r for r in page["items"] if r["native"]["path"]==path]
        self.assertEqual(len(rows),1);return rows[0]

    def test_typed_mcp_locator_is_namespace_not_git_lookup_order(self):
        _,server=self.fixture()
        # A legal Linux Git filename deliberately equals the typed MCP locator.
        mcp=server.call_tool("athena_project_resolve",{"identifier":"tool:athena_project_route"})
        self.assertEqual(mcp["status"],"RESOLVED")
        self.assertEqual(mcp["record"]["source"],"mcp")
        self.assertEqual(mcp["record"]["mcp"]["name"],"athena_project_route")

        git=self.configured_record(server,"tool:athena_project_route")
        exact=server.call_tool("athena_project_resolve",{"identifier":git["return"]["uri"]})
        self.assertEqual(exact["status"],"RESOLVED")
        self.assertEqual(exact["record"]["source"],"configured_git")

    def test_snapshot_id_is_stable_and_shared_across_query_forms(self):
        _,server=self.fixture()
        s1=server.call_tool("athena_project_atlas_summary",{})
        s2=server.call_tool("athena_project_atlas_summary",{})
        self.assertTrue(s1["snapshot_id"].startswith("PATLASV2."))
        self.assertEqual(s1["snapshot_id"],s2["snapshot_id"])
        self.assertIn("PROJECT_ATLAS_SNAPSHOT_ID != PROMOTION_RECEIPT",s1["laws"])

        alpha=self.configured_record(server,"alpha.txt")
        resolved=server.call_tool("athena_project_resolve",{"identifier":alpha["return"]["uri"]})
        listed=server.call_tool("athena_project_list",{"source":"configured_git","path_prefix":"alpha.txt"})
        routed=server.call_tool("athena_project_route",{"src":alpha["return"]["uri"],"dst":"tool:athena_project_route","wrap":True})
        self.assertEqual(resolved["snapshot_id"],s1["snapshot_id"])
        self.assertEqual(listed["snapshot_id"],s1["snapshot_id"])
        self.assertEqual(routed["snapshot_id"],s1["snapshot_id"])
        self.assertEqual(resolved["authority"],"NONE")
        self.assertEqual(listed["authority"],"NONE")
        self.assertEqual(routed["authority"],"NONE")

    def test_live_mcp_surface_change_changes_snapshot_id_without_git_change(self):
        root,server=self.fixture();head=run(root,"rev-parse","HEAD");first=server.call_tool("athena_project_atlas_summary",{})
        fake={"name":"athena_snapshot_probe_test_only","description":"snapshot probe","inputSchema":{"type":"object","additionalProperties":False}}
        TOOLS.append(fake)
        try:
            second=server.call_tool("athena_project_atlas_summary",{})
            self.assertEqual(second["configured_head"],head)
            self.assertEqual(second["runtime_head"],first["runtime_head"])
            self.assertNotEqual(second["snapshot_id"],first["snapshot_id"])
        finally:TOOLS.remove(fake)
        third=server.call_tool("athena_project_atlas_summary",{})
        self.assertEqual(third["snapshot_id"],first["snapshot_id"])

    def test_configured_git_head_change_changes_snapshot_id(self):
        root,server=self.fixture();first=server.call_tool("athena_project_atlas_summary",{})
        (root/"gamma.txt").write_text("g\n",encoding="utf-8");run(root,"add",".");run(root,"commit","-m","advance configured frontier")
        second=server.call_tool("athena_project_atlas_summary",{})
        self.assertNotEqual(second["configured_head"],first["configured_head"])
        self.assertEqual(second["runtime_head"],first["runtime_head"])
        self.assertNotEqual(second["snapshot_id"],first["snapshot_id"])
        self.assertNotEqual(second["configured_git"]["atlas_digest"],first["configured_git"]["atlas_digest"])

    def test_attested_runtime_head_change_changes_snapshot_and_mcp_return(self):
        _,server=self.fixture()
        state={"head":"a"*40}
        def frontier():
            return {
                "status":"RESOLVED","source":"ENV_ATTESTATION","mode":"HEAD_ATTESTATION","attestation_level":"HOST_CONFIGURED_UNVERIFIED",
                "root":None,"repo_key":"github.com/demeet2k/athena-mcp-server","head":state["head"],"branch":None,"dirty":None,
            }
        original=surface_module.runtime_frontier;surface_module.runtime_frontier=frontier
        try:
            server.aor_development.project_atlas._invalidate_cache()
            first=server.call_tool("athena_project_atlas_summary",{})
            first_tool=server.call_tool("athena_project_resolve",{"identifier":"tool:athena_project_route"})
            state["head"]="b"*40
            second=server.call_tool("athena_project_atlas_summary",{})
            second_tool=server.call_tool("athena_project_resolve",{"identifier":"tool:athena_project_route"})
            self.assertNotEqual(first["snapshot_id"],second["snapshot_id"])
            self.assertEqual(first["mcp_surface"]["head"],"a"*40)
            self.assertEqual(second["mcp_surface"]["head"],"b"*40)
            self.assertNotEqual(first_tool["record"]["return"]["uri"],second_tool["record"]["return"]["uri"])
        finally:surface_module.runtime_frontier=original


if __name__=="__main__":unittest.main()
