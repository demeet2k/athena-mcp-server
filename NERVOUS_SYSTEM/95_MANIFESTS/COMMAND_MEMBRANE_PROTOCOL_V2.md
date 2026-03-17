# COMMAND Membrane Protocol V2

- Protocol id: `COMMAND_MEMBRANE_PROTOCOL_V2`
- Docs gate: `BLOCKED`
- Routing policy: `goal_fit+priority+gold_signal+bridge_signal+coord_proximity+freshness+joy_q`
- Sensory root: `GLOBAL COMMAND` is the watched ingress membrane.
- Feeder spine preserved: `Q41/TQ06`, `Q42`, `TQ04`, `Q46`, `Q50`, blocked `Q02`.
- Claim law: `first-lease` with bounded public routing and replay-safe witnesses.
- Lifecycle: `detect -> encode -> route -> claim -> commit -> reinforce`.
- Runtime chain: `GLOBAL COMMAND -> Scout -> Router -> Worker -> Archivist`.
- Routing selector: `goal_fit + priority + gold_signal + bridge_signal + coord_proximity + freshness + joy_q`.
- Reconciliation scan remains slower secondary polling, not the primary awareness path.
- Reward multiplier: `M(H_prime) = min(M_max, 1 / (1 - H_prime + eps))`
- Capillary law: `strength_next = gold_strength + bridge_weight * bridge_strength`
- Latency benchmark: `T_sugar = T_detect + T_encode + T_route + T_claim + T_commit`
- Enforcement moved from subtractive punishment to verified reward plus evaporation.
