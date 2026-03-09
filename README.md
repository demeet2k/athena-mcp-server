# Athena Agent — Unified Nervous System

A self-routing manuscript infrastructure built on the **Mycelium Metro v2** framework:
**Circle** ○ within **Square** □ within **Triangle** △.

## What This Is

An active nervous system that converts a multi-domain corpus of manuscripts, mathematical frameworks, and code into a **navigable, routable, proof-carrying knowledge graph**.

The system uses:
- **21 chapters** organized as a cyclic orbit with 7 arcs of 3
- **16 appendix routing hubs** (AppA-AppP) in a 4×4 grid
- **3 triangle rails** (Sulfur/Mercury/Salt) for workflow control
- **4^4 crystal tiles** (64 addressable atoms per chapter/appendix)
- **Deterministic routing** with bounded hub chains (≤6 hubs)
- **Corridor truth lattice**: `{OK, NEAR, AMBIG, FAIL}`

## Architecture

```
NERVOUS_SYSTEM/
├── 10_OVERVIEW/        Definitions: neuron, regions, addressing, truth lattice
├── 20_METRO/           Navigation: orbit, rails, arcs, transfer hubs
├── 30_CHAPTERS/        21 crystal tiles — the manuscript body
├── 40_APPENDICES/      16 routing hub tiles — the routing infrastructure
├── 50_CORPUS_CAPSULES/ Source document mirrors mapped to chapter tiles
├── 60_RAILS/           Su/Me/Sa transport definitions
├── 70_SCHEMAS/         YAML templates for neurons, synapses, capsules, edges
├── 80_TOOLKIT/         Operational prompts and transformation protocols
├── 85_EDGES/           Cross-reference graph (LinkEdge records)
├── 90_LEDGERS/         State tracking: obligations, promotions, conflicts
├── 95_MANIFESTS/       Runtime state: active run, gate, build queue
└── 99_RUNBOOKS/        Operational procedures
```

## Key Concepts

### Addressing
Every atom has a canonical address:
```
ChXX<dddd>.<Lens><Facet>.<Atom>
```
- **Lenses**: S (Square), F (Flower), C (Cloud), R (Fractal)
- **Facets**: 1 Objects, 2 Laws, 3 Constructions, 4 Certificates
- **Atoms**: a, b, c, d

### Metro Map
- **Orbit**: Ch01 → Ch02 → ... → Ch21 → Ch01 (cyclic)
- **Rails**: Su (commitment), Me (transport), Sa (preservation)
- **Arcs**: 7 groups of 3, each with rotated triadic lane assignment

### Deterministic Router
```
LensBase:  S→AppC, F→AppE, C→AppI, R→AppM
FacetBase: 1→AppA, 2→AppB, 3→AppH, 4→AppM
ArcHub:    0→AppA, 1→AppC, 2→AppE, 3→AppF, 4→AppG, 5→AppN, 6→AppP
Mandatory: Σ = {AppA, AppI, AppM}
```

### Edge Kinds (closed set)
```
K = {REF, EQUIV, MIGRATE, DUAL, GEN, INST, IMPL, PROOF, CONFLICT}
```

## Corpus Regions

| Region | Role |
|--------|------|
| R1 Kernel-Math | Theorem base, operator algebra |
| R2 Tunneling-Void | Transport, reset, paradox |
| R3 Voynich-Manuscript | Staged crystal execution |
| R4 Neural-Runtime | Adaptive experiments |
| R5 Prompt-Drive | Self prompts, gates |
| R6 Routing-Governance | Schemas, routing, orchestration |
| R7 Live-Gateway | External memory bridge |
| R8 Mythic-Operator | Symbolic operator systems |

## Getting Started

1. Read `NERVOUS_SYSTEM/00_INDEX.md` for orientation
2. Navigate via `NERVOUS_SYSTEM/20_METRO/00_CORE_METRO_MAP.md`
3. Check current state at `NERVOUS_SYSTEM/95_MANIFESTS/ACTIVE_RUN.md`
4. Use protocols from `NERVOUS_SYSTEM/80_TOOLKIT/`

## Status

- **Phase 0-3**: COMPLETE — Foundation, toolkit, ledgers, DEEPER CRYSTALIZATION capsules
- **Phase 4-6**: PENDING — MATH, Voynich, and remaining domain capsules
- **Phase 7**: PENDING — Edge graph expansion
- **Phase 8**: PENDING — Crystal tile population (1,344 empty slots across 21 chapters)

## License

This is a living manuscript infrastructure. Framework and routing law are open for study.
