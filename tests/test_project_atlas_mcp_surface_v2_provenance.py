from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import athena_mcp.project_atlas_surface as surface_module
from athena_mcp.project_atlas_runtime_provenance import _normalize_repo, runtime_frontier
from athena_mcp.server import Server


def run(root: Path, *args: str) -> str:
    p=subprocess.run(["git","-C",str(root),*args],text=True,capture_output=True)
    if p.returncode:raise AssertionError(p.stderr or p.stdout)
    return p.stdout.strip()


class ProjectAtlasMcpSurfaceV2ProvenanceTests(unittest.TestCase):
    def fixture(self):
        td=tempfile.TemporaryDirectory();self.addCleanup(td.cleanup);base=Path(td.name);root=base/"brain";root.mkdir()
        run(root,"init");run(root,"config","user.name","test");run(root,"config","user.email","test@example.invalid")
        run(root,"remote","add","origin","https://github.com/demeet2k/project-atlas-fixture.git")
        (root/"README.md").write_text("brain readme\n",encoding="utf-8")
        run(root,"add",".");run(root,"commit","-m","seed")
        return root,Server(str(base/"state.db"),git_root=root)

    def configured_readme(self,server):
        page=server.call_tool("athena_project_list",{"source":"configured_git","path_prefix":"README.md","limit":20})
        rows=[r for r in page["items"] if r["native"]["path"]=="README.md"]
        self.assertEqual(len(rows),1)
        return rows[0]

    def test_head_attestation_coordinates_mcp_but_preserves_unknown_runtime_tree(self):
        _,server=self.fixture()
        attested={
            "status":"RESOLVED","source":"ENV_ATTESTATION","mode":"HEAD_ATTESTATION",
            "attestation_level":"HOST_CONFIGURED_UNVERIFIED","root":None,
            "repo_key":"github.com/demeet2k/athena-mcp-server","head":"a"*40,
            "branch":None,"dirty":None,
        }
        original=surface_module.runtime_frontier;surface_module.runtime_frontier=lambda:dict(attested)
        try:
            server.aor_development.project_atlas._invalidate_cache()
            summary=server.call_tool("athena_project_atlas_summary",{})
            self.assertEqual(summary["status"],"PARTIAL_RUNTIME_TREE_UNAVAILABLE")
            self.assertFalse(summary["runtime_tree_available"])
            self.assertIsNone(summary["runtime_git"])
            self.assertEqual(summary["runtime_head"],"a"*40)
            self.assertEqual(summary["mcp_surface"]["head"],"a"*40)
            self.assertEqual(summary["mcp_surface"]["repo_key"],"github.com/demeet2k/athena-mcp-server")
            self.assertEqual(summary["runtime_provenance"]["attestation_level"],"HOST_CONFIGURED_UNVERIFIED")

            # Unscoped path uniqueness cannot be proven without the runtime tree.
            plain=server.call_tool("athena_project_resolve",{"identifier":"README.md"})
            self.assertEqual(plain["status"],"HOLD_RUNTIME_TREE_UNAVAILABLE")
            self.assertEqual(plain["candidate"]["source"],"configured_git")

            # Exact configured RETURN remains resolvable despite unknown runtime tree.
            exact=self.configured_readme(server)["return"]["uri"]
            resolved=server.call_tool("athena_project_resolve",{"identifier":exact})
            self.assertEqual(resolved["status"],"RESOLVED")
            self.assertEqual(resolved["record"]["source"],"configured_git")

            # Typed MCP namespace is also exact from the attested runtime head.
            mcp=server.call_tool("athena_project_resolve",{"identifier":"tool:athena_project_route"})
            self.assertEqual(mcp["status"],"RESOLVED")
            self.assertEqual(mcp["record"]["source"],"mcp")
            self.assertEqual(mcp["record"]["native"]["head"],"a"*40)

            runtime_list=server.call_tool("athena_project_list",{"source":"runtime_git","limit":20})
            self.assertEqual(runtime_list["status"],"HOLD_RUNTIME_TREE_UNAVAILABLE")
            union=server.call_tool("athena_project_list",{"source":"git","limit":20})
            self.assertEqual(union["status"],"PARTIAL_RUNTIME_TREE_UNAVAILABLE")
        finally:
            surface_module.runtime_frontier=original

    def test_missing_runtime_provenance_never_borrows_configured_head(self):
        root,server=self.fixture();configured_head=run(root,"rev-parse","HEAD")
        missing={
            "status":"HOLD_RUNTIME_PROVENANCE","source":"NONE","mode":"UNRESOLVED","attestation_level":"NONE",
            "repo_key":None,"head":None,"reason":"test missing runtime provenance",
        }
        original=surface_module.runtime_frontier;surface_module.runtime_frontier=lambda:dict(missing)
        try:
            server.aor_development.project_atlas._invalidate_cache()
            summary=server.call_tool("athena_project_atlas_summary",{})
            self.assertEqual(summary["status"],"PARTIAL_RUNTIME_PROVENANCE_HOLD")
            self.assertEqual(summary["configured_head"],configured_head)
            self.assertIsNone(summary["runtime_head"])
            self.assertEqual(summary["mcp_surface"]["status"],"HOLD_RUNTIME_PROVENANCE")
            self.assertIsNone(summary["mcp_surface"]["head"])
            self.assertEqual(summary["mcp_surface"]["count"],0)
            mcp=server.call_tool("athena_project_resolve",{"identifier":"tool:athena_project_route"})
            self.assertEqual(mcp["status"],"HOLD_RUNTIME_PROVENANCE")
        finally:
            surface_module.runtime_frontier=original

    def test_same_checkout_deduplicates_git_plane_but_keeps_mcp_plane(self):
        root,server=self.fixture();head=run(root,"rev-parse","HEAD")
        same={
            "status":"RESOLVED","source":"ATHENA_RUNTIME_GIT_ROOT","mode":"GIT_CHECKOUT","attestation_level":"OBSERVED_LOCAL_GIT",
            "root":str(root.resolve()),"repo_key":"github.com/demeet2k/project-atlas-fixture","head":head,"branch":"master","dirty":False,
        }
        original=surface_module.runtime_frontier;surface_module.runtime_frontier=lambda:dict(same)
        try:
            server.aor_development.project_atlas._invalidate_cache()
            summary=server.call_tool("athena_project_atlas_summary",{})
            self.assertEqual(summary["status"],"PASS")
            self.assertTrue(summary["runtime_git_is_configured"])
            self.assertTrue(summary["runtime_tree_available"])
            self.assertEqual(summary["configured_head"],summary["runtime_head"])
            self.assertEqual(summary["federation"]["count"],2)
            rows=server.call_tool("athena_project_list",{"source":"git","path_prefix":"README.md","limit":20})
            exact=[r for r in rows["items"] if r["native"]["path"]=="README.md"]
            self.assertEqual(len(exact),1)
            runtime_rows=server.call_tool("athena_project_list",{"source":"runtime_git","path_prefix":"README.md","limit":20})
            self.assertEqual(len([r for r in runtime_rows["items"] if r["native"]["path"]=="README.md"]),1)
        finally:
            surface_module.runtime_frontier=original

    def test_github_owner_repo_attestation_normalizes_to_checkout_repo_key(self):
        self.assertEqual(_normalize_repo("demeet2k/athena-mcp-server"),"github.com/demeet2k/athena-mcp-server")
        self.assertEqual(_normalize_repo("https://github.com/demeet2k/athena-mcp-server.git"),"github.com/demeet2k/athena-mcp-server")
        self.assertEqual(_normalize_repo("git@github.com:demeet2k/athena-mcp-server.git"),"github.com/demeet2k/athena-mcp-server")

    def test_env_head_attestation_is_exact_identity_not_promotion_verification(self):
        env={
            "ATHENA_RUNTIME_GIT_ROOT":"",
            "ATHENA_RUNTIME_REPOSITORY":"demeet2k/athena-mcp-server",
            "ATHENA_RUNTIME_GIT_HEAD":"B"*40,
        }
        with patch("athena_mcp.project_atlas_runtime_provenance._source_checkout_root",return_value=None),patch.dict(os.environ,env,clear=False):
            result=runtime_frontier()
        self.assertEqual(result["status"],"RESOLVED")
        self.assertEqual(result["repo_key"],"github.com/demeet2k/athena-mcp-server")
        self.assertEqual(result["head"],"b"*40)
        self.assertEqual(result["attestation_level"],"HOST_CONFIGURED_UNVERIFIED")
        self.assertIn("not independent promotion verification",result["boundary"])

    def test_invalid_env_attestation_holds(self):
        env={
            "ATHENA_RUNTIME_GIT_ROOT":"",
            "ATHENA_RUNTIME_REPOSITORY":"demeet2k/athena-mcp-server",
            "ATHENA_RUNTIME_GIT_HEAD":"not-a-sha",
        }
        with patch("athena_mcp.project_atlas_runtime_provenance._source_checkout_root",return_value=None),patch.dict(os.environ,env,clear=False):
            result=runtime_frontier()
        self.assertEqual(result["status"],"HOLD_RUNTIME_PROVENANCE")
        self.assertEqual(result["attestation_level"],"NONE")


if __name__=="__main__":unittest.main()
