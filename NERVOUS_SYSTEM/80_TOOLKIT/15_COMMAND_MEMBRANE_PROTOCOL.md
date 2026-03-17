# COMMAND Membrane Protocol

## Purpose

Turn `GLOBAL COMMAND` into a sensory membrane instead of a passive folder.

## Canonical Flow

```text
COMMAND FOLDER -> SCOUT -> ROUTER -> WORKER -> ARCHIVIST
```

`powershell-filesystemwatcher` watcher intake is primary. If the backend is unavailable, the board poll loop becomes the degraded fallback and reconciliation path.

This sensory membrane stays additive to the board runtime and capillary ledgers.

## Route Law

- Policy: `goal+salience+pheromone+coord`
- Selector terms: `goal_fit, salience, capillary_strength, coordinate_proximity, freshness, duplicate_penalty`
- Defaults: `topk=5`, `claim_mode=first-lease`, `quorum=1`, `ttl=6`, `lease_ms=1200`

## Capillary Update Law

```text
C_next = clamp(0,1, rho*C + alpha*U + beta*F - gamma*D - delta*N)
```

Grades: `candidate_path`, `capillary`, `vein`

## Truth Boundary

- Google Docs remains BLOCKED because Trading Bot/credentials.json and Trading Bot/token.json are missing.
- Prompt-level liminal GPS is supported.
- Keystroke-level liminal GPS requires external client/runtime instrumentation.
