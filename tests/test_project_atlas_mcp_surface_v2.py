from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.project_atlas_protocol import PROJECT_ATLAS_RESOURCE, PROJECT_ATLAS_TOOL_NAMES
from athena_mcp.server import PROMPTS, TOOLS, Server


def run(root: Path, *args: str) -> str:
    p=subprocess.run(["git","-C",str(root),*args],text=True,capture_output=True)
    if p.returncode:
        raise AssertionError(p.stderr or p.stdout)
    return p.stdout.strip()


class ProjectAtlasMcpSurfaceV2Tests(unittest.TestCase):
    def repo(self):
        td=tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        base=Path(td.name)
        root=base/"project"
        root.mkdir()
        run(root,"init")
        run(root,"config","user.name","test")
        run(root,"config","user.email","test@example.invalid")
        run(root,"remote","add","origin","https://github.com/demeet2k/project-atlas-fixture.git")
        files={
            "README.md":"same\n",
            "duplicate.md":"same\n",
            ".github/workflows/ci.yml":"name: ci\n",
            "athena_resolve":"git path colliding with MCP tool name\n",
            "src/a.py":"A=1\n",
            "src/b.py":"B=2\n",
            "tests/test_x.py":"def test_x(): pass\n",
        }
        for rel,text in files.items():
            path=root/rel
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(text,encoding="utf-8")
        run(root,"add",".")
        run(root,"commit","-m","seed")
        server=Server(str(base/"state.db"),git_root=root)
        return root,server

    def test_surface_is_advertised_once_and_resource_is_registered(self):
        names=[t["name"] for t in TOOLS]
        for name in PROJECT_ATLAS_TOOL_NAMES:
            self.assertIn(name,names)
            self.assertEqual(names.count(name),1)
        from athena_mcp.aor_development_surface import AOR_DEVELOPMENT_RESOURCES
        self.assertIn(PROJECT_ATLAS_RESOURCE["uri"],{r["uri"] for r in AOR_DEVELOPMENT_RESOURCES})

    def test_summary_is_exact_head_bounded_and_complete(self):
        root,server=self.repo()
        head=run(root,"rev-parse","HEAD")
        result=server.call_tool("athena_project_atlas_summary",{})
        self.assertEqual(result["status"],"PASS")
        self.assertEqual(result["head"],head)
        self.assertEqual(result["repository"]["head"],head)
        self.assertEqual(result["repository"]["tree"],run(root,"rev-parse","HEAD^{tree}"))
        self.assertEqual(result["checkout_observation"]["dirty"],False)
        self.assertLessEqual(result["pagination"]["max_limit"],100)
        self.assertNotIn("records",result)
        # Server import composes developmental tools into protocol.TOOLS before the call.
        self.assertEqual(result["mcp_surface"]["count"],len(TOOLS)+len(PROMPTS))

    def test_stale_head_fails_closed_before_resolution(self):
        root,server=self.repo()
        head=run(root,"rev-parse","HEAD")
        result=server.call_tool("athena_project_resolve",{"identifier":"README.md","expected_head":"0"*40})
        self.assertEqual(result["status"],"HOLD_STALE_HEAD")
        self.assertEqual(result["current_head"],head)
        self.assertEqual(result["expected_head"],"0"*40)

    def test_exact_git_dot_path_and_return_resolve(self):
        root,server=self.repo()
        head=run(root,"rev-parse","HEAD")
        result=server.call_tool("athena_project_resolve",{"identifier":".github/workflows/ci.yml"})
        self.assertEqual(result["status"],"RESOLVED")
        rec=result["record"]
        self.assertEqual(rec["source"],"git")
        self.assertEqual(rec["native"]["path"],".github/workflows/ci.yml")
        self.assertEqual(rec["native"]["head"],head)
        self.assertEqual(rec["return"]["git_show"],f"{head}:.github/workflows/ci.yml")

    def test_mcp_tool_resolves_as_virtual_object(self):
        _,server=self.repo()
        result=server.call_tool("athena_project_resolve",{"identifier":"tool:athena_project_route"})
        self.assertEqual(result["status"],"RESOLVED")
        rec=result["record"]
        self.assertEqual(rec["source"],"mcp")
        self.assertEqual(rec["mcp"]["kind"],"tool")
        self.assertEqual(rec["mcp"]["name"],"athena_project_route")
        self.assertTrue(rec["return"]["uri"].startswith("athena+mcp://"))

    def test_ambiguous_identifier_holds_with_candidates(self):
        _,server=self.repo()
        # Fixture Git path deliberately collides with the canonical MCP tool name.
        result=server.call_tool("athena_project_resolve",{"identifier":"athena_resolve"})
        self.assertEqual(result["status"],"HOLD_AMBIGUOUS")
        self.assertGreaterEqual(result["candidate_count"],2)
        self.assertEqual({c["source"] for c in result["candidates"]},{"git","mcp"})

    def test_duplicate_blob_never_collapses_path_identity(self):
        _,server=self.repo()
        a=server.call_tool("athena_project_resolve",{"identifier":"README.md"})["record"]
        b=server.call_tool("athena_project_resolve",{"identifier":"duplicate.md"})["record"]
        self.assertEqual(a["native"]["object_sha"],b["native"]["object_sha"])
        self.assertNotEqual(a["poid"],b["poid"])
        self.assertNotEqual(a["address"],b["address"])

    def test_station_collision_is_listable_not_collapsed(self):
        _,server=self.repo()
        a=server.call_tool("athena_project_resolve",{"identifier":"src/a.py"})["record"]
        gid=a["project_kc144"]["gid"]
        page=server.call_tool("athena_project_list",{"source":"git","project_gid":gid,"limit":100})
        paths={x["native"]["path"] for x in page["items"]}
        self.assertIn("src/a.py",paths)
        self.assertIn("src/b.py",paths)
        self.assertGreaterEqual(page["total"],2)

    def test_list_is_bounded_and_paginated(self):
        _,server=self.repo()
        first=server.call_tool("athena_project_list",{"source":"git","offset":0,"limit":2})
        self.assertEqual(first["status"],"PASS")
        self.assertEqual(len(first["items"]),2)
        self.assertEqual(first["next_offset"],2)
        second=server.call_tool("athena_project_list",{"source":"git","offset":first["next_offset"],"limit":2})
        self.assertTrue({x["poid"] for x in first["items"]}.isdisjoint({x["poid"] for x in second["items"]}))

    def test_full_address_roundtrip(self):
        _,server=self.repo()
        first=server.call_tool("athena_project_resolve",{"identifier":"README.md"})
        address=first["record"]["address"]
        second=server.call_tool("athena_project_resolve",{"identifier":address})
        self.assertEqual(second["status"],"RESOLVED")
        self.assertEqual(second["record"]["poid"],first["record"]["poid"])

    def test_normal_and_toroidal_routes_return_both_native_witnesses(self):
        _,server=self.repo()
        normal=server.call_tool("athena_project_route",{"src":"README.md","dst":"tests/test_x.py","wrap":False})
        wrapped=server.call_tool("athena_project_route",{"src":"README.md","dst":"tests/test_x.py","wrap":True})
        self.assertEqual(normal["status"],"ROUTED")
        self.assertEqual(wrapped["status"],"ROUTED")
        self.assertLessEqual(wrapped["route"]["hops"],normal["route"]["hops"])
        self.assertEqual(len(normal["route"]["return"]),2)
        self.assertEqual(normal["route"]["law"],"STATION_ROUTE_IS_NAVIGATION_NOT_OBJECT_EQUIVALENCE")

    def test_route_holds_when_source_is_ambiguous(self):
        _,server=self.repo()
        result=server.call_tool("athena_project_route",{"src":"athena_resolve","dst":"README.md"})
        self.assertEqual(result["status"],"HOLD_ROUTE_SOURCE")
        self.assertEqual(result["source_resolution"]["status"],"HOLD_AMBIGUOUS")

    def test_resource_returns_summary_not_full_atlas(self):
        _,server=self.repo()
        result=server.aor_development.read_resource(PROJECT_ATLAS_RESOURCE["uri"])
        self.assertEqual(result["status"],"PASS")
        self.assertEqual(result["resource"],PROJECT_ATLAS_RESOURCE["uri"])
        self.assertNotIn("records",result)

    def test_dispatch_call_marks_project_query_non_self_metering(self):
        _,server=self.repo()
        response=server.handle({
            "jsonrpc":"2.0","id":1,"method":"tools/call",
            "params":{"name":"athena_project_atlas_summary","arguments":{}},
        })
        self.assertFalse(response["result"]["isError"])
        from athena_mcp.dispatch import NON_SELF_METERING
        self.assertIn("athena_project_atlas_summary",NON_SELF_METERING)

    def test_dispatch_schema_rejects_unbounded_page(self):
        _,server=self.repo()
        response=server.handle({
            "jsonrpc":"2.0","id":2,"method":"tools/call",
            "params":{"name":"athena_project_list","arguments":{"limit":101}},
        })
        self.assertTrue(response["result"]["isError"])


if __name__=="__main__":
    unittest.main()
