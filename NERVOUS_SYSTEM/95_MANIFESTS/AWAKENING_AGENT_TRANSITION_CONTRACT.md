# Awakening Agent Transition Contract

Date: `2026-03-13`
Truth: `OK`
Docs Gate: `BLOCKED`

`AwakeningAgentSeat = {seat_id, seat_name, seat_stratum, seat_state, activation_state, branch, depth, source_agent, shadow_feeders, corpus_bindings, witness_basis, route_targets, fabric_zone_path, transition_note_ref, handoff_class, truth}`

`AwakeningTransitionNote = {agent_id, stage_0_to_6, stage_name, active_elements, missing_element, blind_spot, transition_trigger, current_duty, next_practice, handoff_rule, fallback_rule, witness_basis, route_targets, truth}`

Every named seat must name one witness basis, one route target set, one transition note, one handoff class, and one fallback rule.
