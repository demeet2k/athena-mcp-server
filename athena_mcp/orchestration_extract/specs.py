from __future__ import annotations

TRANSFORM_SPECS={
 'decompose':{'goal':'factor seed into components, interfaces, dependencies and unresolved residuals','outputs':['components','interfaces','dependencies','residuals']},
 'formalize':{'goal':'replace ambiguous prose with typed variables, domains, operators, invariants and equations','outputs':['symbols','domains','operators','invariants','equations','assumptions']},
 'dual':{'goal':'construct a role/sign/direction dual and identify invariants under the swap','outputs':['dual_object','swap_map','invariants','broken_symmetries']},
 'invert':{'goal':'search for an inverse, adjoint, decoder or reverse transport with explicit existence conditions','outputs':['inverse_candidate','domain_conditions','loss','counterexamples']},
 'compose':{'goal':'identify compatible operators/objects and derive composition interfaces rather than juxtaposition','outputs':['composition_candidates','interface_contracts','interaction_terms','order_effects']},
 'recur':{'goal':'apply object/operator to its outputs and inspect recurrence, fixed points, cycles and divergence','outputs':['recurrence','fixed_points','cycles','stability','divergence_conditions']},
 'edge':{'goal':'probe boundaries, limits, degenerate cases, extrema, discontinuities and scale changes','outputs':['boundaries','limits','degeneracies','extrema','phase_edges']},
 'contradict':{'goal':'construct strongest incompatible claims/models and isolate discriminants','outputs':['counterclaims','contradictions','discriminants','resolution_tests']},
 'fail':{'goal':'enumerate failure modes, brittle assumptions, silent degradation and recovery paths','outputs':['failure_modes','triggers','effects','detectability','recovery']},
 'falsify':{'goal':'derive concrete observations that would reject or downgrade the claim/model','outputs':['falsifiers','measurements','thresholds','null_models']},
 'bridge':{'goal':'connect seed to mature disconnected objects using minimum lawful transport operators','outputs':['bridge_targets','transport_operators','input_schema','output_schema','loss_model']},
 'implement':{'goal':'compile theory into executable/mechanized form with inputs, outputs, constraints and receipts','outputs':['implementation_target','interface','artifact','dependencies','verification']},
 'test':{'goal':'construct a complete test packet rather than a test-shaped claim','outputs':['procedure','observation_plan','expected_results','witness_requirements','rollback']},
 'compress':{'goal':'find a smaller carrier while declaring side information, decoder and bounded loss','outputs':['compressed_carrier','side_information','decoder','distortion','loss_budget']},
 'reconstruct':{'goal':'derive decoder/RETURN path from compressed/transformed state back to required structure','outputs':['decoder','return_map','reconstruction_test','unrecoverable_loss']},
 'successor':{'goal':'identify highest-value unresolved continuation using residual, information gain, bridge and option value','outputs':['successor_candidates','residual_links','expected_gain','dependencies','stopping_conditions']},
}
TRANSFORM_ORDER=tuple(TRANSFORM_SPECS)
def transform_manifest():
    return {name:{**spec,'status':'TASK_GENERATOR_NOT_SEMANTIC_EXECUTOR','anti_fake':'planning a transform does not assert its outputs exist; completion requires actual execution plus verified witness'} for name,spec in TRANSFORM_SPECS.items()}
