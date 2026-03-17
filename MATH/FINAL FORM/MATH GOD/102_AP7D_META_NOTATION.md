# AP7D Meta-Notation

Truth class: `NEAR`
Date: `2026-03-13`
Live Docs gate: `BLOCKED`

## ID grammar

Compatibility-first lineage alphabet:

- `E = EARTH`
- `W = WATER`
- `F = FIRE`
- `A = AIR`

Deterministic identifiers:

- `AP7D-SWARM-YYYYMMDD-NN`
- `AP7D-C-{F|W|A|E}`
- `AP7D-H-{xy}`
- `AP7D-P-{xyz}`
- `AP7D-G-{xyzw}`

## Event grammar

- `HB::<ts_utc>::<agent_id>::<state>::<intent>::<target>::<truth>`
- `INT::<ts_utc>::<agent_id>::<objective>::<inputs>::<output>`
- `DELTA::<ts_utc>::<agent_id>::<artifact>::<change_kind>::<status>`
- `HAND::<ts_utc>::<from_agent>::<to_agent>::<reason>::<next>`
- `RST::<ts_utc>::<agent_id>::<restart_seed>::<resume_from>`

## Storage law

- canonical feeds are append-only `ndjson`
- canonical snapshots are `json`
- timestamps are `UTC`
- Hall and Temple views are mirrors derived from the canonical deep-root feeds

## Safety law

- `AppI` and `AppM` are mandatory on every agent row
- contradiction routes require `AppK` and Earth legality
- stale agents do not disappear; they emit restart seeds and demote to `dormant`
