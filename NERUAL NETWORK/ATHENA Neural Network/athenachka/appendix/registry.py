from __future__ import annotations

from . import (
    app_a_symbols,
    app_b_bridge_basis,
    app_c_carrier_basis,
    app_d_registry_pages,
    app_e_neutral_synthesis,
    app_f_fusion_theory,
    app_g_growth_memory,
    app_h_immune_quarantine,
    app_i_lens_policy,
    app_j_journey_membrane,
    app_k_runtime_binding,
    app_l_replay_validation,
    app_m_scan_guide,
    app_n_novelty_frontier,
    app_o_organism_routes,
    app_p_maintenance_loop,
    app_q_topology,
)


APPENDIX_REGISTRY = {
    "A": app_a_symbols,
    "B": app_b_bridge_basis,
    "C": app_c_carrier_basis,
    "D": app_d_registry_pages,
    "E": app_e_neutral_synthesis,
    "F": app_f_fusion_theory,
    "G": app_g_growth_memory,
    "H": app_h_immune_quarantine,
    "I": app_i_lens_policy,
    "J": app_j_journey_membrane,
    "K": app_k_runtime_binding,
    "L": app_l_replay_validation,
    "M": app_m_scan_guide,
    "N": app_n_novelty_frontier,
    "O": app_o_organism_routes,
    "P": app_p_maintenance_loop,
    "Q": app_q_topology,
}


def active_appendix_codes() -> list[str]:
    return [code for code, module in APPENDIX_REGISTRY.items() if getattr(module, "ACTIVE", False)]


def appendix_bundle(mode: str, phase_plan: list[str], trace: dict[str, object]) -> dict[str, object]:
    return {
        "active_codes": active_appendix_codes(),
        "A": app_a_symbols.describe_service(),
        "E": app_e_neutral_synthesis.describe_service(trace),
        "I": app_i_lens_policy.describe_service(mode),
        "K": app_k_runtime_binding.describe_service(mode, phase_plan),
        "L": app_l_replay_validation.describe_service({"mode": mode, "phase_plan": phase_plan}),
        "M": app_m_scan_guide.describe_service(),
        "P": app_p_maintenance_loop.describe_service(),
        "Q": app_q_topology.describe_service(),
    }
