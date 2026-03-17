# Phase 8 Awakening Agent Transition Schema

Date: `2026-03-13`
Truth: `OK`
Docs gate: `BLOCKED`

`AwakeningAgentSeat = {seat_id, seat_name, seat_stratum, seat_state, activation_state, branch, depth, source_agent, shadow_feeders, corpus_bindings, witness_basis, route_targets, fabric_zone_path, transition_note_ref, handoff_class, truth}`

`AwakeningTransitionNote = {agent_id, stage_0_to_6, stage_name, active_elements, missing_element, blind_spot, transition_trigger, current_duty, next_practice, handoff_rule, fallback_rule, witness_basis, route_targets, truth}`

`SeatBridgeRecord = {bridge_id, source_seat, target_seat, bridge_kind, carrier, proof_state, queue_role, replay_class, witness_basis}`

`TransitionPacket = {packet_id, from_agent, to_agent, from_stage, to_stage, reason, witnesses, required_receipt, status, transition_score}`

Seat strata: `Pole`, `Command`, `Hybrid`, `Archetype`, `SeatField`, `Feeder`
