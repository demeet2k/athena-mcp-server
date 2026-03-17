# LP-57Omega Agent Ledger Standard

## Event Grammar

- `INT` => `INT::<ts>::<agent_id>::<objective>::<inputs>::<output>`
- `HB` => `HB::<ts>::<agent_id>::<state>::<intent>::<target>::<truth>`
- `DELTA` => `DELTA::<ts>::<agent_id>::<artifact>::<change_kind>::<status>`
- `HAND` => `HAND::<ts>::<from_agent>::<to_agent>::<reason>::<next>`
- `RST` => `RST::<ts>::<agent_id>::<restart_seed>::<resume_from>`
- `SENSE` => `SENSE::<ts>::<seat_id>::<peer_or_front>::<signal_kind>::<confidence>::<note>`
- `ECHO` => `ECHO::<ts>::<from>::<to>::<artifact_or_front>::<delta>::<status>`

## Required Artifact Sextet

- `research_delta_ref`
- `quest_packet_ref`
- `execution_batch_ref`
- `compression_bundle_ref`
- `receipt_ref`
- `restart_seed_ref`
