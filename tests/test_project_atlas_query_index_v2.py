from __future__ import annotations

import unittest

from athena_mcp.project_atlas import mcp_surface_atlas, project_coordinate
from athena_mcp.project_atlas_query_index import build_query_index, lookup_identifier, seed_list_candidates


class ProjectAtlasQueryIndexV2Tests(unittest.TestCase):
    def entries(self):
        base=dict(repo_key="github.com/demeet2k/brain",ref="main",head="a"*40,tree="b"*40,git_type="blob",mode="100644")
        git_tool_trap=project_coordinate(path="tool:athena_resolve",object_sha="1"*40,**base)
        git_raw_trap=project_coordinate(path="athena_resolve",object_sha="2"*40,**base)
        git_alpha=project_coordinate(path="src/alpha.py",object_sha="3"*40,**base)
        surface=mcp_surface_atlas(
            repo_key="github.com/demeet2k/athena-mcp-server",
            head="c"*40,
            server_name="athena-canonical-mcp",
            tools=[{"name":"athena_resolve","description":"resolve","inputSchema":{"type":"object"}}],
            prompts=[],
        )
        return [("configured_git",git_tool_trap),("configured_git",git_raw_trap),("configured_git",git_alpha),("mcp",surface["records"][0])]

    def test_index_digest_is_order_invariant_and_duplicate_invariant(self):
        entries=self.entries()
        a=build_query_index(entries)
        b=build_query_index(list(reversed(entries)))
        c=build_query_index(entries+[entries[0],entries[-1]])
        self.assertEqual(a["digest"],b["digest"])
        self.assertEqual(a["digest"],c["digest"])
        self.assertEqual(a["counts"]["records"],4)
        self.assertEqual(c["counts"]["records"],4)

    def test_typed_mcp_namespace_does_not_match_git_path_collision(self):
        idx=build_query_index(self.entries())
        rows,mode=lookup_identifier(idx,"tool:athena_resolve")
        self.assertEqual(mode,"TYPED_MCP")
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0][0],"mcp")
        self.assertEqual(rows[0][1]["mcp"]["name"],"athena_resolve")

    def test_open_world_raw_name_preserves_git_mcp_ambiguity(self):
        idx=build_query_index(self.entries())
        rows,mode=lookup_identifier(idx,"athena_resolve")
        self.assertEqual(mode,"OPEN_WORLD")
        self.assertEqual({source for source,_ in rows},{"configured_git","mcp"})
        self.assertEqual(len(rows),2)

    def test_exact_poid_address_and_return_are_direct_indexes(self):
        entries=self.entries();idx=build_query_index(entries);_,rec=entries[2]
        for identifier,expected_mode in (
            (rec["poid"],"POID"),
            (rec["address"],"PROJECT_ADDRESS"),
            (rec["return"]["uri"],"RETURN_URI"),
        ):
            rows,mode=lookup_identifier(idx,identifier)
            self.assertEqual(mode,expected_mode)
            self.assertEqual(len(rows),1)
            self.assertEqual(rows[0][1]["poid"],rec["poid"])

    def test_station_and_directory_seed_narrow_candidates(self):
        entries=self.entries();idx=build_query_index(entries);_,alpha=entries[2]
        rows,seed=seed_list_candidates(idx,{"project_gid":alpha["project_kc144"]["gid"]},False)
        self.assertEqual(seed,"project_gid")
        self.assertIn(alpha["poid"],{r["poid"] for _,r in rows})
        rows,seed=seed_list_candidates(idx,{"directory":"src"},False)
        self.assertEqual(seed,"directory")
        self.assertEqual({r["native"]["path"] for _,r in rows},{"src/alpha.py"})

    def test_git_source_union_and_runtime_alias_rules(self):
        entries=self.entries();idx=build_query_index(entries)
        rows,seed=seed_list_candidates(idx,{"source":"git"},False)
        self.assertEqual(seed,"source")
        self.assertTrue(rows)
        self.assertEqual({source for source,_ in rows},{"configured_git"})
        rows,seed=seed_list_candidates(idx,{"source":"runtime_git"},True)
        self.assertEqual(seed,"source")
        self.assertEqual({source for source,_ in rows},{"configured_git"})


if __name__=="__main__":unittest.main()
