# PARALLEL NERVOUS SYSTEM RUNBOOK

## Purpose
Step-by-step guide for running parallel agents to build or extend the nervous system.

## Prerequisites

1. The canonical `NERVOUS_SYSTEM/` directory exists at project root
2. `00_INDEX.md` is current and accurate
3. `95_MANIFESTS/ACTIVE_RUN.md` reflects the current run

## Parallel Build Procedure

### Step 1: Check Gate Status
Read `95_MANIFESTS/GATE_STATUS.md`. If live Docs gate is OPEN, run Live Docs presearch first.

### Step 2: Identify Build Front
Read `95_MANIFESTS/BUILD_QUEUE.md` to determine the highest-priority pending phase.

### Step 3: Launch Parallel Agents
For independent domains (e.g., MATH, Voynich, Neural Network), launch separate agents:
- Each agent handles one domain's capsule creation
- Each agent follows `70_SCHEMAS/03_CAPSULE_SCHEMA.md`
- Each agent records its work in `90_LEDGERS/PROMOTION_LEDGER.md`

### Step 4: Merge Results
After agents complete:
- Update `50_CORPUS_CAPSULES/INDEX.md` with new capsules
- Update `95_MANIFESTS/SOURCE_SURFACE_ATLAS.md` with new domain status
- Record promotions in `90_LEDGERS/PROMOTION_LEDGER.md`

### Step 5: Build Edges
Once capsules exist, create edge files in `85_EDGES/`:
- SOURCE_TO_CHAPTER_EDGES.md
- CHAPTER_TO_APPENDIX_EDGES.md

### Step 6: Populate Tiles
Begin filling crystal tile slots in chapter files, starting with priority chapters.

### Step 7: Update Run Manifest
Update `95_MANIFESTS/ACTIVE_RUN.md` with phase completion status.
