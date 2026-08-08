# ATHENA Canonical MCP v2

A from-first-principles rebuild of the ATHENA Git/MCP nervous substrate.

**Invariant:** one canonical state, explicit versions, exact ancestry, conditional mutations, typed JSPACE edges, SCALE compression, KC144 navigation, public liminal telemetry, and lossless RETURN to native artifacts.

The active repo is executable infrastructure only. Historical prose/corpora do not live in the runtime tree; they are referenced by immutable source locators and remain available in Git history or external source systems.

## Runtime cycle

`HYDRATE → RECONSTRUCT → JSPACE → SCALE → KC144 → CUT/MAXDEV → CRYSTALLIZE → CONDITIONAL COMMIT → GLOBAL DIFFUSION`

## Identity

`SID != OID != MID != VID != CID != EID`

## Two freshness gates

1. Semantic mutation: `expected VID == current VID` else `STALE_TARGET`.
2. Git checkpoint: `expected Git HEAD == current Git HEAD` else `STALE_GIT_HEAD`.

No shadow-organ mutation can silently become canonical.

## Exact text navigation

Every ingested text manifestation receives deterministic lexeme/character coordinates:

`KC144.G###.R##.C##/OID:.../VID:.../MID:.../P:#####/S:#####/T:#######/C:#########-#########`

Run: `python -m athena_mcp --db ./state/athena.db`

Protocol revision: `2025-11-25`.
