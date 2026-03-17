# SWARM PACKET SCHEMA

## V2 Supersession Note

`COMMAND_MEMBRANE_PROTOCOL_V2` is now the active command-membrane reward and routing law.
This schema remains valid as a structural packet shell, but any older subtractive command
scoring should be treated as historical `V1` doctrine rather than the live membrane rule.

## Purpose

This schema normalizes higher-dimensional swarm artifacts so sibling agents can write compatible packets across runtime, cortex, and governance surfaces.

## Swarm Packet

```yaml
swarm_id: SWARM-2026-03-09-01
title: higher-dimensional nervous system bridge
goal: merge cortex, runtime hub, and governance mirror
kernel:
  objective: one-sentence objective
  contraction_target: stable artifact set
  truth_policy: ABSTAIN_OVER_GUESS
surface_stack:
  - Cortex
  - RuntimeHub
  - GovernanceMirror
regions:
  - R1
  - R5
  - R6
  - R7
depth_plan:
  current: D3
  target: D1
  fanout: 64
pods:
  - pod_id: POD-01
    frontier: higher-dimensional mapping
    owners:
      - Earth
      - Air
    packet_family: overview
    contraction_target: overview doc
    status: NEAR
ganglia:
  - MATH
  - self_actualize
  - ECOSYSTEM
  - NERVOUS_SYSTEM
metro_lines:
  - Crystal-to-Tunnel
  - Swarm Runtime
  - Canonical-Bridge
witness:
  direct_support:
    - absolute path
  atlas_record_count: 1768
  replay_hint: rerun atlas refresh and compare manifests
writeback:
  cortex:
    - absolute path
  runtime:
    - absolute path
  governance:
    - absolute path
unresolved:
  - blocker or ambiguity
status: NEAR
```

## Wave Packet

```yaml
wave_id: WAVE-2026-03-09-01
goal: project the supermap into runtime and cortex
active_swarm: SWARM-2026-03-09-01
pods:
  - POD-01
  - POD-02
  - POD-03
start_surface: RuntimeHub
end_surface: Cortex
stop_condition:
  - at least one runtime packet exists
  - at least one cortex manifest exists
  - bridge note updated
status: OK | NEAR | AMBIG | FAIL
```

## Pod Packet

```yaml
pod_id: POD-01
frontier: bridge the three nervous-system surfaces
lane: Air
depth: D3
sources:
  - absolute path
packet_type: pod
output_target: absolute path
contraction_target: one sentence
witness_target: absolute path
status: NEAR
```

## Ganglion Packet

```yaml
ganglion_id: GANGLION-self-actualize
family: self_actualize
local_maps:
  - absolute path
local_queues:
  - absolute path
active_pods:
  - POD-01
bridges:
  - NERVOUS_SYSTEM/00_INDEX.md
status: NEAR
```

## Command Event Packet

```yaml
event_id: EVT-20260313-0001
source_path: GLOBAL COMMAND/ATHENA/example.md
active_surface: GLOBAL COMMAND/ATHENA
change_type: created | updated | deleted
change_summary: created md at GLOBAL COMMAND/ATHENA/example.md
goal: detect-classify-assign
priority: 1.0
confidence: 0.98
earth_ts: 2026-03-13T12:45:10.482000+00:00
detected_ts: 2026-03-13T12:45:10.482000+00:00
emitted_ts: 2026-03-13T12:45:10.611000+00:00
liminal_ts: LT-000001.000
seat_addr_6d: A1.B1.C1.D1.E1.F1
coordinate_stamp:
  Xs: GLOBAL_COMMAND
  Ys: ATHENA
  Zs: GLOBAL COMMAND/ATHENA/example.md
  Ts: C02
  Qs: EVT-20260313-0001
  Rs: D3
  Cs: DETECTED
  Fs: CREATED
  Ms: M100
  Ns: GLOBAL COMMAND/ATHENA
  Hs: command-event
  Ωs: OMEGA-LOCAL-WITNESS
parent_event_id: ROOT
ttl: 6
pheromone: 0.91
state_hash: H:91AF...
route_class: scout.router.worker.archivist
witness_class: LOCAL_WITNESS_ONLY
lineage:
  parent_event_id: ROOT
  loop_id: C02
  docs_gate_detail: blocked-by-missing-credentials
deferred_dimensions:
  solar_phase: DEFERRED_LOCAL_EPHEMERIS
  lunar_phase: DEFERRED_LOCAL_EPHEMERIS
  sidereal_phase: DEFERRED_LOCAL_EPHEMERIS
  planetary_anchor_slot: DEFERRED_LOCAL_EPHEMERIS
coord12:
  earth_atomic_utc: 1773405910.482
  earth_rotation_phase: 0.532
  earth_orbital_phase: 0.194
  earth_geospatial_anchor: America/Los_Angeles::charlie-local-node
  solar_phase: null
  lunar_phase: null
  sidereal_phase: null
  planetary_anchor_slot: null
  server_region: ATHENA_LOCAL_RUNTIME
  queue_pressure: 0.0625
  goal_salience_vector:
    - 1.0
    - 0.91
  novelty_routing_concentration: 1.0
```

Rules:
- Scope for v1 is `GLOBAL COMMAND/ATHENA` only.
- All command packets stay `LOCAL_WITNESS_ONLY` until the Docs gate clears.
- No promoted writeback is valid without both `seat_addr_6d` and `coordinate_stamp`.

## Command Claim Lease

```yaml
claim_id: CLM-20260313T124510Z-91af3c
event_id: EVT-20260313-0001
ant_id: C02.A3.D1.A1.B1.C1.D1.E1.F1.WORKER-ADVENTURER
role: worker
lease_ms: 1200
claimed_at: 2026-03-13T12:45:10.700000+00:00
expires_at: 2026-03-13T12:45:11.900000+00:00
status: active | expired | committed
claim_mode: first-lease
owner_surface: command-folder
board_claim_id: CLM-...
```

Rule:
- Duplicate live claims are illegal while an active lease exists for the same `event_id`.

## Latency Sample

```yaml
event_id: EVT-20260313-0001
detection_latency_ms: 41.0
awareness_latency_ms: 12.0
claim_latency_ms: 18.0
resolution_latency_ms: 0.0
commit_latency_ms: 104.0
t_sugar_ms: 175.0
delta_tau: 0.214
delta_earth_ms: 510.0
liminal_velocity: 0.4196078431
resolution_class: transitional
recorded_at: 2026-03-13T12:45:10.900000+00:00
capillary_score: 1.42
```

## Capillary Edge

```yaml
edge_id: SCOUT-01>ROUTER-01
from_node: SCOUT-01
to_node: ROUTER-01
path_key: SCOUT-01>ROUTER-01
edge_strength: 1.42
classification: reinforced route | capillary | vein
success_count: 4
use_count: 5
noise_count: 1
average_latency_score: 0.93
last_result: success
last_event_id: EVT-20260313-0001
last_updated: 2026-03-13T12:45:10.950000+00:00
rho: 0.90
alpha: 1.00
beta: 0.50
gamma: 0.50
delta: 0.50
```

Rule:
- Compression or cleanup must never delete the only witness of a live or unresolved command event.
