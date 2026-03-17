# Voynich Rosetta Machine

## Purpose

This layer compiles the prose-first Voynich translation corpus into a machine-readable Rosetta surface.

The machine authority lives here:

- `schemas/` - explicit JSON schemas for the core machine records
- `scripts/` - deterministic build, export, companion-build, canonical-promotion, giant-package, and validation entrypoints
- `registries/` - generated atom, morpheme, operator, transport, and notation registries
- `build/` - generated token, line, folio, book, corpus, and manifest outputs
- `build/consumers/` - generated rollups for manuscript, crystal, metro, node, integration, and canonical promotion consumers
- `archive/` - archived pre-overwrite canonical witnesses for promotion runs that actually change content
- `mirrors/` - generated markdown summaries derived from machine data

The build is intentionally honest about source status:

- local corpus grounded
- Google Docs gate currently `BLOCKED`
- no jurisdiction-specific legal advice

## Entry Points

```powershell
python "C:\Users\dmitr\Documents\Athena Agent\Voynich\FULL_TRANSLATION\rosetta_machine\scripts\build_rosetta_machine.py"
python "C:\Users\dmitr\Documents\Athena Agent\Voynich\FULL_TRANSLATION\rosetta_machine\scripts\export_rosetta_notations.py"
python "C:\Users\dmitr\Documents\Athena Agent\Voynich\FULL_TRANSLATION\rosetta_machine\scripts\build_rosetta_companions.py"
python "C:\Users\dmitr\Documents\Athena Agent\Voynich\FULL_TRANSLATION\rosetta_machine\scripts\promote_rosetta_canon.py"
python "C:\Users\dmitr\Documents\Athena Agent\Voynich\FULL_TRANSLATION\rosetta_machine\scripts\build_giant_manuscript.py"
python "C:\Users\dmitr\Documents\Athena Agent\Voynich\FULL_TRANSLATION\rosetta_machine\scripts\validate_rosetta_machine.py"
```

## Contract

- Parse the current `222` authoritative final-draft folio files as they exist.
- Preserve damaged glyphs and uncertainty markers instead of normalizing them away.
- Convert the Rosetta theory into machine registries and algorithm records.
- Reuse the existing `16`-node neural precedent for corpus attachment.
- Generate markdown mirrors from compiled data instead of hand-authoring them.
- Publish companion markdown surfaces into `unified/`, `crystals/`, `metro/`, `neural_network/`, and `manifests/`.
- Promote machine-fed canonical longforms into the top-level unified, crystal, metro, and neural master files with archived witness snapshots under `rosetta_machine/archive/`.
- Build the true inline whole-manuscript package at `unified/VOYNICH_GIANT_MANUSCRIPT.md` with archived witness snapshots and an explicit `BLOCKED/MISSING` closure-witness section.
