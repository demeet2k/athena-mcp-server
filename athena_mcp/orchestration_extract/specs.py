from __future__ import annotations

TRANSFORM_SPECS = {
    "decompose": {"goal":"factor the seed into components, interfaces, dependencies and unresolved residuals","outputs":["components","interfaces","dependencies","residuals"],"questions":["what are the irreducible parts?","what depends on what?","which interfaces carry behavior?"]},
    "formalize": {"goal":"replace ambiguous prose with typed variables, domains, operators, invariants and equations","outputs":["symbols","domains","operators","invariants","equations","assumptions"],"questions":["what is the state space?","what maps to what?","which assumptions are required?"]},
    "dual": {"goal":"construct a role/sign/direction dual and identify what is invariant under the swap","outputs":["dual_object","swap_map","invariants","broken_symmetries"],"questions":["what roles can be exchanged?","what survives the exchange?","where does duality fail?"]},
    "invert": {"goal":"search for an inverse, adjoint, decoder or reverse transport with explicit existence conditions","outputs":["inverse_candidate","domain_conditions","loss","counterexamples"],"questions":["is the map injective/surjective/invertible?","what side information is needed?","where is reversal impossible?"]},
    "compose": {"goal":"identify compatible operators/objects and derive composition interfaces rather than juxtaposition","outputs":["composition_candidates","interface_contracts","interaction_terms","order_effects"],"questions":["what can lawfully compose?","does order matter?","what new capability appears only jointly?"]},
    "recur": {"goal":"apply the object/operator to its own outputs and inspect recurrence, fixed points, cycles and divergence","outputs":["recurrence","fixed_points","cycles","stability","divergence_conditions"],"questions":["what is x_(t+1)=F(x_t)?","where are fixed points?","which regimes contract or diverge?"]},
    "edge": {"goal":"probe boundaries, limits, degenerate cases, extrema, discontinuities and scale changes","outputs":["boundaries","limits","degeneracies","extrema","phase_edges"],"questions":["what happens at zero/infinity/min/max?","where do assumptions break?","which edge cases change type?"]},
    "contradict": {"goal":"construct strongest incompatible claims/models and isolate discriminants","outputs":["counterclaims","contradictions","discriminants","resolution_tests"],"questions":["what would make this false?","which alternative explains the same observations?","what observation separates them?"]},
    "fail": {"goal":"enumerate failure modes, unsafe assumptions, brittleness, silent degradation and recovery paths","outputs":["failure_modes","triggers","effects","detectability","recovery"],"questions":["how can it fail?","how would failure be detected?","what fails silently?"]},
    "falsify": {"goal":"derive concrete observations that would reject or downgrade the claim/model","outputs":["falsifiers","measurements","thresholds","null_models"],"questions":["which observation would count against it?","what threshold changes authority?","what is the null?"]},
    "bridge": {"goal":"connect the seed to mature disconnected objects using minimum lawful transport operators","outputs":["bridge_targets","transport_operators","input_schema","output_schema","loss_model"],"questions":["what valuable object cannot yet talk to this one?","what minimum interface connects them?","what meaning is lost?"]},
    "implement": {"goal":"compile theory into executable/mechanized form with inputs, outputs, constraints and receipts","outputs":["implementation_target","interface","artifact","dependencies","verification"],"questions":["what can be mechanized now?","what observable artifact proves execution?","which dependencies block it?"]},
    "test": {"goal":"construct a complete test packet rather than a test-shaped claim","outputs":["procedure","observation_plan","expected_results","witness_requirements","rollback"],"questions":["what exact procedure runs?","what is observed?","what witnesses success/failure?"]},
    "compress": {"goal":"find a smaller carrier while declaring side information, decoder and bounded loss","outputs":["compressed_carrier","side_information","decoder","distortion","loss_budget"],"questions":["what can be removed lawfully?","what side information is required?","can useful structure be reconstructed?"]},
    "reconstruct": {"goal":"derive the decoder/RETURN path from compressed or transformed state back to required structure","outputs":["decoder","return_map","reconstruction_test","unrecoverable_loss"],"questions":["what reconstructs the source?","what cannot be recovered?","what witness proves reconstruction?"]},
    "successor": {"goal":"identify highest-value unresolved continuation using residual, information gain, bridge value and option value","outputs":["successor_candidates","residual_links","expected_gain","dependencies","stopping_conditions"],"questions":["what remains unresolved?","which continuation creates the most future option value?","what is blocked?"]},
}

TRANSFORM_ORDER = tuple(TRANSFORM_SPECS)


def transform_manifest():
    return {
        name: {
            **spec,
            "status": "TASK_GENERATOR_NOT_SEMANTIC_EXECUTOR",
            "anti_fake": "planning a transform does not assert its outputs exist; completion requires external/agent execution plus verified witness",
        }
        for name, spec in TRANSFORM_SPECS.items()
    }
