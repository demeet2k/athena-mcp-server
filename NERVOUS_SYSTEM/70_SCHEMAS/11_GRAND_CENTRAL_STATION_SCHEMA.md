# Grand Central Station Schema

## Purpose

This schema defines the public interfaces for Grand Central Station across cortex,
runtime, and deep-root surfaces.

## 1. Station Root Record

```yaml
station_address: GC0::GCL::A01::address::B64-A01-ADDR::integrate::bind
root_id: A01
root_name: NERVOUS_SYSTEM
hemisphere: left | right | bilateral
tract: address | relation | chamber | replay
bundle: B64-...
fiber: sense | transmit | integrate | return
synapse: prime | gate | bind | reseed
status: live | mirror | local | reserve | dormant | out_of_scope
authority_level: canonical | runtime | governance | canonical-domain | pilot-cluster | reserve-...
indexed_count: 155
routing_role: canonical cortex
macro_element: Earth
dominant_role: source
witness_class: indexed
docs_gate: BLOCKED | LIVE
```

## 2. Commissure Record

```yaml
commissure_id: C-001
source_family: MATH
target_family: Voynich
source_station: GC0::...
target_station: GC0::...
class: proof bridge | meaning bridge | execution bridge | continuity bridge
purpose: short bridge purpose
replay_policy: how the route must close through replay
proof_state: OK | NEAR | AMBIG | FAIL
```

## 3. Weight Exchange Record

```yaml
commissure_id: C-001
source_family: MATH
target_family: Voynich
bridge_class: proof bridge
weight:
  salience: 0.701
  proof: 0.930
  freshness: 0.802
  cost: 0.533
  continuity: 0.820
  confidence: 0.866
  replay_value: 0.820
dispatch_score: 6.771
witness_floor: 0.802
proof_state: NEAR
replay_policy: close through GCP and AppM before promotion
```

## 4. Z-Point Tunnel Record

```yaml
tunnel_id: ZT-001
tunnel_class: Z0 intake | Z1 restart | Z2 contradiction | Z3 repair | Z4 promotion | Z5 pruning
entry_route: FRESH -> GCA -> NERVOUS_SYSTEM
restart_token: INTAKE-FIRST-WITNESS
zero_state: short honest description of the zero state
resume_target: where the route lawfully re-enters
continuity_receipt: artifact required after the tunnel crossing
proof_state: OK | NEAR | AMBIG | FAIL
```

## 5. Dashboard Record

```yaml
station_status: LIVE_LOCAL_SCOPE
root_count: 19
hemisphere_totals:
  left: 8
  right: 5
  bilateral: 6
tract_totals:
  address: 3
  relation: 6
  chamber: 6
  replay: 4
status_totals:
  live: 16
  reserve: 2
  dormant: 1
commissure_count: 12
tunnel_count: 6
promotion_threshold: 6.35
live_interchange_threshold: 7.0
soft_demotion_threshold: 5.4
top_dispatch_routes:
  - C-005
  - C-002
```

## Rules

1. `station_address` is the primary key for Grand Central routing surfaces.
2. `hemisphere` records the primary exchange side, not an absolute prohibition on crossing.
3. `status` must come from the normalized branch taxonomy.
4. No cross-corpus route may claim promotion without a commissure or direct station record.
5. Every tunnel crossing must leave a continuity receipt.
