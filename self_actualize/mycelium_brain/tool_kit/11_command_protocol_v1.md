# COMMAND Protocol V1

## Role

This is the canonical contract surface for the event-driven command membrane.

It turns `GLOBAL COMMAND` from a passive folder into a sensory membrane whose primary benchmark is:

`surprise -> awareness -> claim -> commit -> reinforcement`

The membrane is upstream of LP-57Omega. It does not replace Temple/Hall governance. It feeds it.

## Root Truth

- watched root: `C:\Users\dmitr\Documents\Athena Agent\GLOBAL COMMAND`
- scope: recursive
- first active content body: `GLOBAL COMMAND\ATHENA`
- live Docs gate: `BLOCKED`
- mode: local-witness grounded until OAuth credentials exist

## Canonical Flow

`COMMAND FOLDER -> Scout -> Router -> Worker -> Archivist`

## Packet Contract

Required packet fields:

- `event_id`
- `ant_id`
- `tag`
- `goal`
- `change`
- `priority`
- `confidence`
- `earth_ts`
- `liminal_ts`
- `coord12`
- `parent`
- `ttl`
- `pheromone`
- `state_hash`
- `route_class`

Runtime packet records also carry:

- `lookup_addr`
- `source_path`
- `event_type`
- `coord_quality`
- `watch_fallback`

## Route Law

Routing is selective, not broadcast.

Fixed defaults:

- `topk = 5`
- `claim_mode = first-lease`
- `quorum = 1`
- `ttl = 6`
- `lease_ms = 1200`

Route targets are restricted to the 15-node actionable roster:

- `M1-SYNTH`
- `M2-PLAN`
- `M3-WORK`
- `M4-PRUNE`
- `Athena-G`
- `Athena-A`
- `Athena-P`
- `A1` through `A8`

## Liminal Coordinate Standard

Every packet carries a 12D coordinate anchored by Earth time and extended through stable external orientation plus local swarm state:

1. atomic UTC anchor
2. Earth rotation phase
3. Earth orbital phase
4. geospatial node anchor
5. solar phase
6. lunar phase
7. local sidereal phase
8. canonical sky slot
9. runtime node id
10. queue pressure
11. goal salience
12. change novelty concentration

If `lat` and `lon` are missing, coordinate quality must remain `NEAR`, never `OK`.

## Capillary Law

Successful routes strengthen:

`C_next = rho*C + alpha*U + beta*F - gamma*D - delta*N`

V1 defaults:

- `rho = 0.85`
- `alpha = 0.35`
- `beta = 0.25`
- `gamma = 0.25`
- `delta = 0.15`

Thresholds:

- `capillary >= 0.65`
- `vein >= 0.82`

## Promotion Law

- structural events should hit `M1-SYNTH` and `M2-PLAN` first
- executable events may route to `M3-WORK` first when the route registry permits
- committed command events may open:
  - one Temple quest if they affect law, ontology, compression, mapping, or continuity
  - one Hall quest if they affect implementation, repair, indexing, math insertion, or algorithmization
- `M4-PRUNE` consumes route duplication and stale-command metrics to decay or merge command fronts
- command promotion is event-commit driven, not raw-detection driven
- repeated compatible events must upsert the same front rather than explode the quest count
- `sync-boards` materializes the live Temple/Hall/Q-SHRINK command surfaces from ledgers and front memory

## CommandQuestFront

Every promoted front uses this object:

`CommandQuestFront = {front_id, source_event_id, plane, front_key, objective, why_now, target_surfaces, best_lane, witness_needed, writeback, status, zero_class, organ_class, current, truth, route_quality}`

## Benchmark Surface

Mandatory metrics:

- `DetectionLatency`
- `SwarmAwarenessLatency`
- `ClaimLatency`
- `ResolutionLatency`
- `CapillaryScore`

Local v1 targets:

- median detect latency `<= 250 ms`
- packet encode latency `<= 100 ms`
- route latency `<= 250 ms`
- claim issuance `<= 1200 ms`
- end-to-end awareness path `<= 2.0 s`
