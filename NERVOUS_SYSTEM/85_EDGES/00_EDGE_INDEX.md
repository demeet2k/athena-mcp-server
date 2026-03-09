# EDGE INDEX

## Purpose

This directory contains the cross-reference graph of the nervous system — all LinkEdge records that connect atoms, chapters, appendices, and source capsules.

## Edge Files

| File | Edge Kinds | Scope | Status |
|------|-----------|-------|--------|
| `SOURCE_TO_CHAPTER_EDGES.md` | REF, IMPL | source capsule → chapter tile slot | PENDING |
| `CHAPTER_TO_APPENDIX_EDGES.md` | REF | chapter → routing hub (deterministic) | SCAFFOLDED |
| `REF_EDGES.md` | REF | cross-chapter dependencies | PENDING |
| `EQUIV_EDGES.md` | EQUIV | duplicate/equivalent sources | PENDING |
| `MIGRATE_EDGES.md` | MIGRATE | version transitions | PENDING |

## Edge Kind Basis (closed set)

```
K = {REF, EQUIV, MIGRATE, DUAL, GEN, INST, IMPL, PROOF, CONFLICT}
```

## Schema

See `70_SCHEMAS/04_EDGE_SCHEMA.md` for the LinkEdge record format.

## Navigation Edges

Orbit, rail, and arc triad edges are defined in `20_METRO/00_CORE_METRO_MAP.md` and are implicit REF edges with NavPayload. They are not duplicated here.
