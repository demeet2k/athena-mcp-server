# ATHENA Canonical MCP v2.1 — Polycoordinate Crystal Runtime

A from-first-principles rebuild of the ATHENA Git/MCP nervous substrate.

**Invariant:** one canonical state, explicit versions, exact ancestry, conditional mutations, typed JSPACE edges, SCALE compression, KC144 navigation, public liminal telemetry, and lossless RETURN to native artifacts.

The active repo is executable infrastructure only. Historical prose/corpora do not live in the runtime tree; they are referenced by immutable source locators and remain available in Git history or external source systems.

## Runtime cycle

`HYDRATE → RECONSTRUCT → JSPACE → SCALE → KC144 → CUT/MAXDEV → CRYSTALLIZE → CONDITIONAL COMMIT → GLOBAL DIFFUSION`

## Identity

`SID != OID != MID != VID`

- `SID`: immutable KC144 station identity
- `OID`: semantic object identity
- `MID`: carrier manifestation identity
- `VID`: object version identity
- `CID`: canonical capability identity
- `EID`: causal event identity

## Stale-write law

`expected VID == current VID` or the mutation returns `STALE_TARGET`. No shadow-organ mutation can silently become canonical.

## Exact text navigation

Every ingested text manifestation is stored with deterministic token/character coordinates:

`KC144.G###.R##.C##/OID:.../VID:.../MID:.../P:#####/S:#####/T:#######/C:#########-#########`

The source manifestation remains canonical; coordinates index it without replacing it.

## Run

```bash
python -m athena_mcp --db ./state/athena.db
```

The stdio server implements MCP JSON-RPC lifecycle plus tools, resources, and prompts for protocol revision `2025-11-25`.

## v2.1 crystal compiler

`athena_crystallize_output` compiles one exact visible payload into identity/version/manifestation, exact lexeme addresses, a complete open-world coordinate atlas, mathematical objects, JSPACE edges/hyperedges, SCALE state, time/liminal/lineage state, CUT/evidence state, and a derived separately-indexed crystal header.

Cross-coordinate navigation is no longer a list: `athena_register_transform` stores `T_ij`, `athena_coordinate_matrix` measures transform coverage, `athena_record_holonomy` stores measured `H_gamma`, and `athena_graph_path` performs typed directed JSPACE routing.
