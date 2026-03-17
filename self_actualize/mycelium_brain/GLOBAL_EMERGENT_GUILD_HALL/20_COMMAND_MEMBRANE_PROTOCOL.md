# Command Membrane Protocol

- Docs gate: `BLOCKED`
- Canonical ingress: `GLOBAL COMMAND`
- Flow: `GLOBAL COMMAND -> Scout -> Router -> Worker -> Archivist`
- Watch mode: `EVENT_DRIVEN` primary, `DEGRADED_POLLING` explicit fallback
- Routing policy: `goal+file_family+coord12_proximity+queue_pressure+capillary_strength+role_compatibility`
- Packet fields: `event_id, source_root, relative_path, event_kind, tag, goal, change, priority, confidence, earth_ts, liminal_ts, coord12, delta_tau, velocity_tau, parent, ttl, pheromone, state_hash, route_class, lineage, claim_state`
- Coord12: `utc_atomic, earth_rotation_phase, earth_orbital_phase, node_anchor, solar_phase, lunar_phase, shared12_phase, planetary_slot, runtime_region, queue_pressure, goal_salience, novelty_concentration`
- Latency law: `T_sugar = T_detect + T_encode + T_route + T_claim + T_commit`
- Capillary law: `C_next = clamp01(0.82*C + 0.30*U + 0.18*F - 0.16*D - 0.14*N)`

## Recent Projected Events

- none yet
