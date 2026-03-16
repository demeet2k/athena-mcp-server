"""Test that the MCP server registers all expected tools and resources."""

import importlib.util
import sys
from pathlib import Path


def _load_server():
    """Load the MCP server module without calling mcp.run()."""
    server_path = Path(__file__).resolve().parent.parent / "MCP" / "athena_mcp_server.py"
    spec = importlib.util.spec_from_file_location("athena_mcp_server", server_path)
    mod = importlib.util.module_from_spec(spec)
    mod.__name__ = "athena_mcp_server"  # prevent if __name__ == "__main__"
    spec.loader.exec_module(mod)
    return mod


class TestRegistration:
    def setup_method(self):
        self.mod = _load_server()
        self.mcp = self.mod.mcp

    def test_tool_count(self):
        tools = self.mcp._tool_manager._tools
        assert len(tools) == 64, f"Expected 64 tools, got {len(tools)}: {sorted(tools.keys())}"

    def test_resource_count(self):
        resources = self.mcp._resource_manager._resources
        assert len(resources) == 19, f"Expected 19 resources, got {len(resources)}: {sorted(resources.keys())}"

    def test_core_tools_present(self):
        tools = set(self.mcp._tool_manager._tools.keys())
        core = {
            "navigate_crystal", "athena_status", "search_everywhere",
            "read_chapter", "read_appendix", "search_corpus",
            "route_metro", "read_thread", "read_swarm_element",
            "explore_nervous_system", "read_nervous_system_file",
        }
        missing = core - tools
        assert not missing, f"Missing core tools: {missing}"

    def test_108d_tools_present(self):
        tools = set(self.mcp._tool_manager._tools.keys())
        expected_108d = {
            "query_shell", "query_superphase", "query_archetype",
            "read_hologram_chapter", "resolve_dimensional_body",
            "dimensional_lift", "query_containment", "query_organ",
            "navigate_108d", "compute_live_lock", "query_clock_beat",
            "check_route_legality", "query_metro_line", "resolve_z_point",
            "query_conservation", "query_overlay", "query_sigma15",
            "query_transport_stack", "query_mobius_lens", "query_sfcr_station",
            "query_stage_code", "query_angel",
            "query_brain_network", "compute_bridge_weight", "route_brain",
            "query_live_cell", "query_emergence",
            "query_hologram", "query_hologram_rosetta",
            "query_angel_geometry", "query_angel_conservation",
            "query_4d_seed", "query_3d_crystal",
            "query_octave_stage", "query_crown_transform",
            "query_projection_stack", "query_weave_operator",
        }
        missing = expected_108d - tools
        assert not missing, f"Missing 108D tools: {missing}"

    def test_nav_tools_present(self):
        tools = set(self.mcp._tool_manager._tools.keys())
        nav = {
            "explore_nervous_system", "read_nervous_system_file",
            "read_motion_constitution", "read_dimensional_body",
            "read_command_protocol", "read_civilization",
            "read_synthesis", "read_super_cycle",
        }
        missing = nav - tools
        assert not missing, f"Missing nav tools: {missing}"

    def test_resources_present(self):
        resources = set(self.mcp._resource_manager._resources.keys())
        expected = {
            "athena://status", "athena://board", "athena://loop",
            "athena://crystal-108d", "athena://dimensional-ladder",
            "athena://organ-atlas", "athena://live-helm",
            "athena://conservation", "athena://mobius-lenses",
            "athena://stage-ladder", "athena://angel",
            "athena://brain-network",
            "athena://live-cell",
            "athena://emergence",
            "athena://hologram-reading",
            "athena://hologram-rosetta",
            "athena://angel-geometry",
            "athena://inverse-seed",
            "athena://inverse-octave",
        }
        missing = expected - resources
        assert not missing, f"Missing resources: {missing}"
