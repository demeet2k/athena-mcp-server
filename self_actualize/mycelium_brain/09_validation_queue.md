# Validation Queue

## Gate Checks

### Google Docs Gate

- check whether `Trading Bot\credentials.json` exists
- check whether `Trading Bot\token.json` exists
- run `docs_search.py`
- record success or failure
- preserve the exact query and stderr in both `live_docs_gate_status.md` and the receipt surface

### Atlas Integrity Gate

- confirm `corpus_atlas.json` is readable
- confirm `archive_atlas.json` is readable
- confirm merged atlas search still works through `self_actualize\runtime`

### Map Integrity Gate

- confirm all map files exist in `self_actualize\mycelium_brain`
- confirm the metro index points to each core surface
- confirm queue files match the current highest-yield frontier

### Toolkit Integrity Gate

- confirm `tool_kit/` exists
- confirm toolkit files `01` through `09` exist
- confirm `registry/00_toolkit_registry.md` references them
- confirm `11_nervous_system_topology.md` points to the toolkit and receipts
- confirm toolkit file `07_tandem_agentic_loop_protocol.md` exists
- confirm toolkit file `08_archive_promotion_protocol.md` exists
- confirm toolkit file `09_cross_agent_contraction_receipt_protocol.md` exists
- confirm `registry/01_tandem_frontier_claims.md` exists and is linked

### Tandem Coordination Gate

- confirm parallel fronts are claimable through `registry/01_tandem_frontier_claims.md`
- confirm new tandem prompt receipt exists
- confirm build queue references the frontier claim law
- confirm contraction receipts can be written without colliding with the frontier claims ledger

### Nervous-System Gate

- confirm `nervous_system/09_parallel_execution_loop.md` exists
- confirm `nervous_system/10_family_frontier_matrix.md` exists
- confirm the active nervous-system index points to both
- confirm family fronts align with the current atlas distribution

### Runtime Gate

- run `python -m self_actualize.runtime.cli` on one new objective
- confirm a route packet is produced
- append findings to `route_quality_ledger.json`

## Review Rhythm

### Daily

- one gate check
- one artifact-producing move
- one writeback

### Weekly

- refresh build queue
- refresh metro maps
- refresh validation queue

## Failure Classes

- FAIL: blocked or contradictory with no admissible route
- AMBIG: partial structure but insufficient witness
- NEAR: executable with residuals
- OK: replay-safe enough to commit

## Immediate Checks To Run Next

1. Google Docs auth bootstrap after credentials arrive
2. one archive framework promotion decision
3. one fresh runtime episode logged in the route ledger
4. one toolkit-guided manuscript pass with receipt writeback
5. one archive-promotion rehearsal or live extraction using the canonical protocol
