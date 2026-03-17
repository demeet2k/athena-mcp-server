# AP7D Meta-Notation

Truth class: `NEAR`
Live Docs gate: `BLOCKED`
Timestamp law: `UTC`

## ID grammar

The AP7D swarm uses a compatibility-first lineage alphabet:

- `E = EARTH`
- `W = WATER`
- `F = FIRE`
- `A = AIR`

The activation and handoff order remains separate:

`FIRE -> WATER -> AIR -> EARTH`

Deterministic IDs:

- `swarm_id = AP7D-SWARM-YYYYMMDD-NN`
- `council_id = AP7D-C-{F|W|A|E}`
- `macro_id = AP7D-H-{xy}`
- `packet_id = AP7D-P-{xyz}`
- `agent_id = AP7D-G-{xyzw}`

## Required agent row fields

Every `AgentRegistryRow` must include:

- `agent_id`
- `lineage_addr`
- `ordinal_256`
- `parent_packet_id`
- `macro_id`
- `council_id`
- `dominant_element`
- `current_front`
- `transition_note_ref`
- `appendix_floor`
- `restart_seed`
- `truth_class`

## Human-readable event syntax

- `HB::<ts_utc>::<agent_id>::<state>::<intent>::<target>::<truth>`
- `INT::<ts_utc>::<agent_id>::<objective>::<inputs>::<output>`
- `DELTA::<ts_utc>::<agent_id>::<artifact>::<change_kind>::<status>`
- `HAND::<ts_utc>::<from_agent>::<to_agent>::<reason>::<next>`
- `RST::<ts_utc>::<agent_id>::<restart_seed>::<resume_from>`

## COMMAND event syntax

The command membrane adds a more granular lifecycle family that still rolls up into AP7D:

- `EVT::<ts_utc>::<event_id>::<scout>::<goal>::<target>::<truth>`
- `RTE::<ts_utc>::<event_id>::<router>::<policy>::<selected_targets>::<truth>`
- `CLM::<ts_utc>::<event_id>::<worker>::<claim_id>::<lease_ms>::<truth>`
- `CMT::<ts_utc>::<event_id>::<worker>::<result>::<route_path>::<truth>`
- `RIN::<ts_utc>::<event_id>::<archivist>::<route_path>::<capillary_score>::<truth>`

## Machine-readable event law

- feeds are append-only `ndjson`
- snapshots are versioned `json`
- every event row must carry `event_id`, `event_type`, `ts_utc`, actor identity, truth
  class, and a replay pointer or replay anchor
- Hall and Temple mirrors must be derivable from canonical AP7D ledgers and feeds

## Stale and quarantine law

- if an active agent emits no new event in the current run wave, mark it `stale`
- stale agents demote to `dormant` and emit a restart seed
- if contradiction survives a handoff, emit both `HAND` and `DELTA`
- contradiction routes must pass through `AppK` and Earth legality before reactivation
