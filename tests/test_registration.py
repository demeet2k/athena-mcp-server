# CRYSTAL: Xi108:W3:A9:S15 | face=F | node=411 | depth=2 | phase=Fixed
# METRO: Sa
# BRIDGES: Xi108:W3:A9:S14→Xi108:W3:A9:S16→Xi108:W2:A9:S15→Xi108:W3:A8:S15→Xi108:W3:A10:S15

"""Test that the MCP server registers all expected tools and resources."""

import importlib.util
import sys
from pathlib import Path

def _load_server():
    """Load the MCP server module without calling mcp.run()."""
    server_path = Path(__file__).resolve().parent.parent / "MCP" / "athena_mcp_server.py"
    momentum_path = server_path.parent / "data" / "momentum_field.json"
    original_momentum = momentum_path.read_bytes()
    spec = importlib.util.spec_from_file_location("athena_mcp_server", server_path)
    mod = importlib.util.module_from_spec(spec)
    mod.__name__ = "athena_mcp_server"  # prevent if __name__ == "__main__"
    try:
        spec.loader.exec_module(mod)
    finally:
        momentum_path.write_bytes(original_momentum)
    return mod

class TestRegistration:
    @classmethod
    def setup_class(cls):
        cls.mod = _load_server()
        cls.mcp = cls.mod.mcp

    def test_tool_count(self):
        tools = self.mcp._tool_manager._tools
        assert len(tools) >= 150, f"Expected >= 150 tools, got {len(tools)}: {sorted(tools.keys())}"

    def test_resource_count(self):
        resources = self.mcp._resource_manager._resources
        assert len(resources) == 34, f"Expected 34 resources, got {len(resources)}: {sorted(resources.keys())}"

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
            "query_shard", "query_graph", "query_node", "query_promotion",
            "query_quest", "query_synthesis", "query_promotion_membrane",
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

    def test_source_mount_tools_present(self):
        tools = set(self.mcp._tool_manager._tools.keys())
        expected = {
            "athena_source_mount_status",
            "resolve_athena_source_mount",
            "return_athena_source_mount",
        }
        missing = expected - tools
        assert not missing, f"Missing source-mount tools: {missing}"

    def test_memory_digest_capsule_tools_present(self):
        tools = set(self.mcp._tool_manager._tools.keys())
        expected = {
            "athena_memory_digest_capsule_status",
            "resolve_athena_memory_digest_capsule",
            "verify_athena_memory_digest_capsule",
            "athena_endpoint_binding_status",
        }
        missing = expected - tools
        assert not missing, f"Missing W14 capsule tools: {missing}"

    def test_capsule_replay_and_authority_ingress_tools_present(self):
        tools = set(self.mcp._tool_manager._tools.keys())
        expected = {
            "athena_capsule_blind_replay_status",
            "replay_athena_capsule_blind",
            "inspect_athena_authority_packet",
            "athena_authority_packet_ingress_status",
        }
        missing = expected - tools
        assert not missing, f"Missing W15 replay/ingress tools: {missing}"

    def test_w16_capsule_index_repair_tools_present(self):
        tools = set(self.mcp._tool_manager._tools.keys())
        expected = {
            "athena_w16_replay_ledger_status",
            "resolve_athena_w16_capsule_index",
            "athena_w16_authorized_witness_ingress_status",
        }
        missing = expected - tools
        assert not missing, f"Missing W16 capsule-index tools: {missing}"

    def test_replay_authority_ledger_tools_present(self):
        tools = set(self.mcp._tool_manager._tools.keys())
        expected = {
            "athena_replay_authority_ledger_status",
            "read_athena_replay_ledger_row",
            "verify_athena_replay_authority_ledger",
            "replay_athena_capsule_from_ledger",
            "inspect_athena_authority_evidence_adjunction",
        }
        missing = expected - tools
        assert not missing, f"Missing W16 replay/authority tools: {missing}"

    def test_w17_evidence_provenance_gate_tools_present(self):
        tools = set(self.mcp._tool_manager._tools.keys())
        expected = {
            "athena_w17_evidence_provenance_gate_status",
            "inspect_athena_w17_evidence_provenance",
        }
        missing = expected - tools
        assert not missing, f"Missing W17 provenance gate tools: {missing}"

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
            "athena://mycelium",
            "athena://node-registry",
            "athena://guild-hall",
            "athena://quest-board",
            "athena://federation-v2",
            "athena://federation-v2/cutover",
            "athena://federation-v2/lock",
            "athena://source-mounts",
            "athena://memory-digest-capsules",
            "athena://replay-authority-ledger",
            "athena://authority-evidence-adjunction",
            "athena://capsule-blind-replay",
            "athena://authority-packet-ingress",
            "athena://w16-replay-ledger",
            "athena://w17/evidence-provenance-dispatch-gate",
        }
        missing = expected - resources
        assert not missing, f"Missing resources: {missing}"

