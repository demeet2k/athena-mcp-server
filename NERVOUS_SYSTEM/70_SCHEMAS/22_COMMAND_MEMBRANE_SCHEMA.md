# COMMAND Membrane Schema

## Purpose

`COMMAND Membrane` freezes the packet, lease, route, archivist, capillary, and latency contracts for `GLOBAL COMMAND` as an event-driven ingress membrane.

- Surface: `GLOBAL COMMAND`
- Core coordinate law: `coord12` + `coord12_frame`

It is additive to [19_ROUTE_PLAN_SCHEMA.md](/Users/dmitr/Documents/Athena Agent/NERVOUS_SYSTEM/70_SCHEMAS/19_ROUTE_PLAN_SCHEMA.md) and does not replace existing route headers or proof surfaces.

## CommandEventPacket

- Required fields: `event_id, source_folder, source_path, event_kind, tag, goal, change, priority, confidence, earth_ts, liminal_ts, coord12, seat_addr_6d, front_ref, parent, ttl, pheromone, state_hash, route_class, lineage, seed_mode, dual_reference`

## CommandClaimLease

- Required fields: `lease_id, event_id, worker_ant_id, router_ant_id, role, claim_mode, quorum, lease_ms, status, claimed_at, expires_at, mirrored_claim_id, route_path`

## RouteDecision

- Required fields: `event_id, policy_id, selector_terms, candidate_targets, selected_targets, topk, claim_mode, quorum, route_path, worker_choice, duplicate_penalty, routed_at`

## ArchivistReceipt

- Required fields: `event_id, claim_ant_id, result, route_path, replay_ptr, committed_at, summary`

## CapillaryEdgeRecord

- Required fields: `edge_id, source_ant_id, target_ant_id, strength, success_count, failure_count, noise_count, grade, last_event_id, updated_at`

## Latency Benchmarks

- Equation: `T_sugar = T_detect + T_encode + T_route + T_claim + T_commit`
- Fields: `detect_latency, awareness_latency, claim_latency, resolution_latency, commit_latency, capillary_score, liminal_delta, earth_delta, liminal_velocity, T_detect_ms, T_encode_ms, T_route_ms, T_claim_ms, T_commit_ms, T_sugar_ms, duplicate_suppression_rate, lease_collision_rate, route_win_rate, capillary_half_life`
