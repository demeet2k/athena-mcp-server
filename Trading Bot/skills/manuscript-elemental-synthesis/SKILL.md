---
name: manuscript-elemental-synthesis
description: Build a four-element synthesis network for a manuscript corpus, including source extraction, individual manuscript cards, ordered pairwise cross-syntheses, neutral and elemental observation fields, symmetry docs, metro maps, appendix crystal scaffolds, and zero-point compression. Use when Codex needs to deeply integrate many related manuscripts or long-form documents into a reusable markdown knowledge lattice rather than a one-off summary.
---

# Manuscript Elemental Synthesis

## Family-Local Boundary

This skill is valid for manuscript-corpus lattice builds inside the local Trading Bot
family and similar bounded corpora.

It is not the authoritative whole-corpus deep-root router for Athena.

For current whole-corpus deep-network requests, use:

- `self_actualize/mycelium_brain/dynamic_neural_network/14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK/09_SKILLS/00_SKILL_ROUTER.md`

Use this skill when a user wants deep corpus integration, large-scale cross-synthesis, metro-map style navigation, appendix scaffolds, or an explicit element-lens framework over many manuscripts.

## Quick Start

1. Confirm the source corpus location.
2. Decide which texts are primary lattice manuscripts and which are auxiliary overlays.
3. Run `scripts/build_manuscript_elemental_net.py --workspace-root <repo-root>`.
4. Read `references/pipeline.md` if the corpus split or output logic needs adjustment.
5. Read `references/crystal-grid.md` if the user asks about the element/mode/appendix logic.
6. Read `references/output-topology.md` if you need the generated file layout.

## Workflow

### 1. Establish the corpus

Inspect the candidate documents first.
Prefer `.docx`, `.md`, `.txt`, and `.pdf` sources that behave like manuscripts, design tomes, or formal notes.

Promote a source into the primary lattice when it:

- defines primitives, transforms, invariants, routes, or systemic laws
- can seed one or more appendix slots
- cross-synthesizes directly with the rest of the formal corpus

Keep a source in the auxiliary layer when it acts more like an interpretive overlay, UI lens, or symbolic projection than a generative kernel manuscript.

### 2. Build the lattice

Run:

```powershell
python skills/manuscript-elemental-synthesis/scripts/build_manuscript_elemental_net.py --workspace-root .
```

The script writes a `MANUSCRIPT_ELEMENTAL_NET_4X4` folder under the workspace root.

### 3. Read the control layer first

Open, in order:

- `00_CONTROL/01_CORPUS_CANON.md`
- `00_CONTROL/02_EXECUTION_MODEL.md`
- `00_CONTROL/04_deep_synthesis.md`
- `06_METRO_MAPS/00_level_1_metro_map.md`

Only then branch into the pairwise matrix, elemental folders, and appendices.

### 4. Deepen the interpretive layer

The build script creates the scaffold and first-pass synthesis.
If the user asks for deeper interpretation, patch the top-level control docs rather than exploding every pair file into essay form.

Prefer enriching:

- `00_CONTROL/04_deep_synthesis.md`
- `00_CONTROL/05_deep_synthesis_expanded.md`
- `06_METRO_MAPS/*.md`
- selected appendix files

### 5. Preserve indexed structure

When the user asks for huge combinatorics, do not dump unreadable prose.
Represent the combinatorics as:

- ordered matrices
- observation fields
- symmetry docs
- appendix grids
- metro maps

The point of the skill is navigable density, not token bloat.

## Resources

### `scripts/build_manuscript_elemental_net.py`

Use this to extract `.docx` sources and generate the synthesis network.

### `references/pipeline.md`

Read this when you need the step-by-step algorithm, corpus-selection logic, or rebuild rules.

### `references/crystal-grid.md`

Read this when you need the element, mode, symmetry, and appendix-slot definitions.

### `references/output-topology.md`

Read this when you need the exact folder and file layout produced by the build.
