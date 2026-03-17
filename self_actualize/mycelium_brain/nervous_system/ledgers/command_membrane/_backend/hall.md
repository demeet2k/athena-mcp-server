# Command Membrane Protocol

- Docs gate: `BLOCKED`
- Canonical ingress: `GLOBAL COMMAND`
- Flow: `GLOBAL COMMAND -> Scout -> Router -> Worker -> Archivist`
- Watch mode: `event-driven` primary, `polling` explicit fallback
- Routing policy: `goal+salience+pheromone+coord`
- Packet fields: `event_id, sensor_event_id, ant_id, source_root, relative_path, event_kind, file_family, tag, goal, change_summary, priority, confidence, earth_ts_utc, liminal_ts, coord12, delta_tau, velocity_tau, parent_event_id, ttl, pheromone, state_hash, route_class, lineage, scheduler_refs, hsigma_ref, status, claim_state`
- Coord12: `earth_utc_anchor, earth_rotation_phase, earth_orbital_phase, earth_geospatial_anchor, solar_phase, lunar_phase, local_sidereal_phase, canonical_sky_anchor, runtime_region, queue_pressure, goal_salience_vector, change_novelty_vector`
- Latency law: `T_sugar = T_detect + T_encode + T_route + T_claim + T_commit`
- Capillary law: `C_next = clamp(0,1, rho*C + alpha*U + beta*F - gamma*D - delta*N)`

## Recent Projected Events

- `EVT-20260314-0011` `vein_promoted` `ATHENA/SELF/mindsweeper_v2K_exact_weighted_betweenness.csv`
- `EVT-20260314-0010` `capillary_promoted` `ATHENA/SELF/athena_prime_mindsweeper_board_v2N.md`
- `EVT-20260314-0010` `worker_success_human_visible` `ATHENA/SELF/athena_prime_mindsweeper_board_v2N.md`
- `EVT-20260314-0010` `worker_success_human_visible` `ATHENA/SELF/athena_prime_mindsweeper_board_v2N.md`
- `EVT-20260313-0007` `worker_success_human_visible` `_command_membrane_probe_4.txt`
- `EVT-20260313-0007` `worker_success_human_visible` `_command_membrane_probe_4.txt`
- `EVT-20260313-0003` `worker_success_human_visible` `_command_membrane_probe.txt`
- `EVT-20260313-0003` `worker_success_human_visible` `_command_membrane_probe.txt`
- `EVT-20260313-0002` `worker_success_human_visible` `ATHENA/codex_command_membrane_test.txt`
- `EVT-20260313-0002` `worker_success_human_visible` `ATHENA/codex_command_membrane_test.txt`
- `EVT-20260313-0001` `worker_success_human_visible` `_command_membrane_probe.txt`
