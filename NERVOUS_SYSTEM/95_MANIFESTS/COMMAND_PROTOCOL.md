# COMMAND Protocol

- Protocol id: `COMMAND_MEMBRANE_V1`
- Surface: `GLOBAL COMMAND`
- Command spine: `athena emit`, `athena route`, `athena claim`, `athena reinforce`
- Routing policy: `goal+salience+pheromone+coord`
- Selector terms: `goal_fit, salience, capillary_strength, coordinate_proximity, freshness, duplicate_penalty`
- Claim law: `first-lease`, `quorum=1`, `ttl=6`, `lease_ms=1200`
- Watch scope: `GLOBAL COMMAND only`
- Watcher mode: `powershell-filesystemwatcher`; board poll loop remains the degraded fallback and reconciliation path
- Explicit reconcile remains available, but watcher mode never silently downgrades into polling
- Existing board claim and route surfaces remain additive, not replaced.
