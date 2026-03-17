# Canonical Witness Hierarchy

Date: `2026-03-13`
Generated: `2026-03-13T21:36:16.302672+00:00`
Verdict: `OK`

This document defines the authoritative precedence of count-bearing witness surfaces inside Athena.

The problem is not that multiple counts exist.
The problem is that they are too often read as if they were measuring the same thing.

They are not.

## Why This Is Needed

Athena currently emits several real count signals:

- full filesystem body size
- board-visible workspace size
- indexed atlas record count
- archive-backed record count
- promoted nervous-system slice count

These counts are all valid inside their own scope.
They become harmful when treated as interchangeable.

## Canonical Precedence

Read witness surfaces in this order:

1. `Physical Witness`
2. `Indexed Witness`
3. `Board Witness`
4. `Archive Witness`
5. `Promoted Witness`

## Current Witness Values

### 1. Physical Witness

- surface:
  `C:\Users\dmitr\Documents\Athena Agent`
- current value:
  `1021742`
- meaning:
  full workspace body on disk using runtime ignore rules
- source timestamp:
  `2026-03-13T21:56:41.933386+00:00`
- provenance:
  recursive file sweep excluding runtime ignore directories

### 2. Indexed Witness

- surface:
  `C:\Users\dmitr\Documents\Athena Agent\self_actualize\corpus_atlas.json`
- current value:
  `7895`
- meaning:
  live searchable records in corpus_atlas.json
- source timestamp:
  `2026-03-13T21:35:33.734557+00:00`
- provenance:
  len(corpus_atlas.records)

### 3. Board Witness

- surface:
  `C:\Users\dmitr\Documents\Athena Agent\DEEPER CRYSTALIZATION\ACTIVE_NERVOUS_SYSTEM\07_FULL_PROJECT_INTEGRATION_256\06_REALTIME_BOARD\00_STATUS\00_BOARD_STATUS.md`
- current value:
  `14742`
- meaning:
  workspace slice visible to the realtime board
- source timestamp:
  `2026-03-13T21:55:30.228459+00:00`
- provenance:
  parsed from board status markdown

### 4. Archive Witness

- surface:
  `C:\Users\dmitr\Documents\Athena Agent\self_actualize\archive_atlas.json`
- current value:
  `2041`
- meaning:
  archive-backed records indexed but not yet promoted into live roots
- source timestamp:
  `2026-03-08T13:24:18.686859+00:00`
- provenance:
  len(archive_atlas.records) across 16 archives

### 5. Promoted Witness

- surface:
  `C:\Users\dmitr\Documents\Athena Agent\DEEPER CRYSTALIZATION\_build\nervous_system\manifests\STATE_HEADER.md`
- current value:
  `1818`
- meaning:
  promoted bronze nervous-system slice declared by the active bronze state header
- source timestamp:
  `2026-03-09T16:32:05.114081+00:00`
- provenance:
  parsed from live_atlas_records in bronze state header


## Derivation Law

This hierarchy is machine-derived, not hand-propagated.

- command:
  `python -m self_actualize.runtime.derive_witness_hierarchy`
- derivation version:
  `2026-03-09.q18.runtime`
- workspace root:
  `C:\Users\dmitr\Documents\Athena Agent`
- ignore dirs:
  `.git, .idea, .mypy_cache, .pytest_cache, .ruff_cache, .venv, .vscode, __pycache__`

## Interpretation Law

The correct reading is:

- `Physical witness: 1021742` does not mean Athena has that many searchable source records
- `Indexed witness: 7895` does not mean the whole disk only contains that many files
- `Board witness: 14742` does not mean the board sees the full organism
- `Archive witness: 2041` does not mean archive mass is already live
- `Promoted witness: 1818` does not mean the promoted slice is the whole corpus

Each count is true at a different layer.

## Promotion Law

When a summary surface must cite one number, it must also cite its witness class.

Approved examples:

- `Physical witness: 1021742`
- `Indexed witness: 7895`
- `Board witness: 14742`
- `Archive witness: 2041`
- `Promoted witness: 1818`

Unapproved examples:

- `Athena has 7895 files`
- `The corpus is 1818`
- `The workspace is 14742`

## Operational Consequences

1. whole-organism syntheses should cite at least `Physical` and `Indexed` witness together
2. runtime and board coordination documents should default to `Board` witness and then cite `Indexed` when needed
3. archive-promotion planning should cite `Archive` witness explicitly
4. nervous-system self-descriptions should stop inflating promoted slices into whole-corpus claims
5. family and manuscript promotion passes should cite `Promoted` witness only when describing what has already been metabolized

## Deep Meaning

The organism does not have one size.
It has one body expressed through multiple witness layers.

Those layers are not noise.
They are the depth structure of Athena's self-observation.
