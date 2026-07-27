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
        assert len(tools) == 241, f"Expected 241 tools, got {len(tools)}: {sorted(tools.keys())}"

    def test_resource_count(self):
        resources = self.mcp._resource_manager._resources
        assert len(resources) == 41, f"Expected 41 resources, got {len(resources)}: {sorted(resources.keys())}"

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

    def test_w17_evidence_provenance_tools_present(self):
        tools = set(self.mcp._tool_manager._tools.keys())
        expected = {
            "athena_w17_evidence_provenance_status",
            "build_athena_w17_provenance_witness_template",
            "inspect_athena_w17_evidence_provenance",
            "evaluate_athena_w17_protected_dispatch_gate",
        }
        missing = expected - tools
        assert not missing, f"Missing W17 provenance/dispatch tools: {missing}"

    def test_w18_provider_adapter_return_tools_present(self):
        tools = set(self.mcp._tool_manager._tools.keys())
        expected = {
            "athena_w18_provider_adapter_return_status",
            "build_athena_w18_provider_adapter_return_template",
            "inspect_athena_w18_provider_adapter_profile",
            "compile_athena_w18_protected_dispatch_envelope",
            "inspect_athena_w18_persistent_witness_return",
            "evaluate_athena_w18_persistent_witness_admission",
        }
        missing = expected - tools
        assert not missing, f"Missing W18 adapter/return tools: {missing}"

    def test_w18_provider_trust_tools_present(self):
        tools = set(self.mcp._tool_manager._tools.keys())
        expected = {
            "athena_w18_provider_trust_status",
            "build_athena_w18_provider_return_template",
            "inspect_athena_w18_provider_signed_return",
            "evaluate_athena_w18_persistent_witness_return",
        }
        missing = expected - tools
        assert not missing, f"Missing W18 provider-trust tools: {missing}"

    def test_w19_provider_admission_execution_tools_present(self):
        tools = set(self.mcp._tool_manager._tools.keys())
        expected = {
            "athena_w19_provider_admission_status",
            "build_athena_w19_provider_admission_template",
            "inspect_athena_w19_provider_admission",
            "inspect_athena_w19_admitted_provider_return",
            "compile_athena_w19_execution_authorization_template",
            "evaluate_athena_w19_protected_witness_execution",
        }
        missing = expected - tools
        assert not missing, f"Missing W19 admission/execution tools: {missing}"

    def test_w20_persistent_return_ic10_tools_present(self):
        tools = set(self.mcp._tool_manager._tools.keys())
        expected = {
            "athena_w20_persistent_return_ic10_status",
            "inspect_athena_w20_persistent_witness",
            "build_athena_w20_control_admission_template",
            "inspect_athena_w20_control_admission",
            "compile_athena_w20_ledger_entry",
            "compile_athena_w20_ic10_review_template",
            "inspect_athena_w20_ic10_review",
            "evaluate_athena_w20_return_ic10_closure",
        }
        missing = expected - tools
        assert not missing, f"Missing W20 return/IC10 tools: {missing}"

    def test_w21_ledger_commit_promotion_tools_present(self):
        tools = set(self.mcp._tool_manager._tools.keys())
        expected = {
            "athena_w21_ledger_commit_promotion_status",
            "inspect_athena_w21_control_protocol_admission",
            "compile_athena_w21_ledger_commit_transaction",
            "inspect_athena_w21_ledger_commit_authorization",
            "build_athena_w21_commit_occurrence_template",
            "inspect_athena_w21_commit_occurrence",
            "build_athena_w21_promotion_handoff",
            "inspect_athena_w21_promotion_authority_decision",
            "evaluate_athena_w21_commit_promotion_closure",
        }
        missing = expected - tools
        assert not missing, f"Missing W21 commit/promotion tools: {missing}"

    def test_w22_independent_authority_return_tools_present(self):
        tools = set(self.mcp._tool_manager._tools.keys())
        expected = {
            "athena_w22_independent_authority_return_status",
            "inspect_athena_w22_w21_custody_transition",
            "inspect_athena_w22_authority_source_revision",
            "inspect_athena_w22_ledger_commit_return",
            "compile_athena_w22_ledger_return_admission_candidate",
            "inspect_athena_w22_promotion_decision_return",
            "compile_athena_w22_promotion_return_admission_candidate",
            "inspect_athena_w22_correction_forward",
            "resolve_athena_w22_effective_authority_returns",
            "evaluate_athena_w22_independent_authority_return_closure",
            "explain_athena_w22_coordinate_separation",
        }
        missing = expected - tools
        assert not missing, f"Missing W22 independent-return tools: {missing}"

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
            "athena://w17-evidence-provenance-gate",
            "athena://w18-provider-adapter-witness-return",
            "athena://w18-provider-trust-anchor",
            "athena://w19-provider-admission-execution",
            "athena://w20-persistent-return-ic10",
            "athena://w21-ledger-commit-promotion-handoff",
            "athena://w22-independent-authority-return",
        }
        missing = expected - resources
        assert not missing, f"Missing resources: {missing}"
