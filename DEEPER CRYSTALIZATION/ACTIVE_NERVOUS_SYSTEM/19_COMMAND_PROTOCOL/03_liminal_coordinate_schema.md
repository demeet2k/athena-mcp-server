# 12D Liminal Coordinate Schema

Command packets carry a 12-dimensional coordinate tuple. Each slot is persisted as a normalized scalar in `[0,1]` plus a named stamp.

1. `utc_time_fraction`
2. `local_earth_rotation_phase`
3. `earth_orbital_phase`
4. `local_node_anchor`
5. `solar_phase`
6. `lunar_phase`
7. `sidereal_phase`
8. `sky_anchor_slot`
9. `runtime_node_anchor`
10. `queue_pressure`
11. `goal_salience_vector`
12. `novelty_routing_concentration`

The first eight dimensions provide Earth and astro anchoring. The last four encode runtime and liminal state.

- Prompt-level liminal GPS: `supported now`
- Keystroke-level liminal GPS: `future instrumentation only`
