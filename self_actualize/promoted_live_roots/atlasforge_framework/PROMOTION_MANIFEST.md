# ATLAS FORGE Promotion Manifest

## Source Archive

- Archive:
  `C:/Users/dmitr/Documents/Athena Agent/MATH/FINAL FORM/FRAMEWORKS CODE/ATLAS FORGE  - Framework.zip`
- Archive sha256:
  `0697e4a31eb52fb18fb3f8c995d2bebf4ec759b9e7a8e1216870a7296a54f1f7`
- Archive witness:
  `self_actualize/archive_manifest.json`

## Live Root

- Destination:
  `C:/Users/dmitr/Documents/Athena Agent/self_actualize/promoted_live_roots/atlasforge_framework`
- Promotion date:
  `2026-03-09`
- Canonical package root:
  `atlasforge/`
- Adjacent docs preserved:
  `docs/`
- Root contracts preserved:
  `README.md`
  `pyproject.toml`
  `setup.py`

## Extraction Summary

- Extracted files:
  `314`
- Skipped cache artifacts:
  `41`
- Skip law:
  omit `__pycache__/` and `.pyc` only; preserve code, docs, root metadata, and adjacent manuals

## Validation

- Command:
  `PYTHONIOENCODING=utf-8 python -m atlasforge.verify_installation`
- Result:
  `NEAR`
- Passing checks:
  import, symbol export, core types, solvers, lenses, certificates, recipe pipeline, crystal combat, hybrid system, utilities
- Residual blocker:
  Windows temp cleanup in the package verifier leaves `index.sqlite` handles open during memory-bank cleanup, producing `WinError 32` on three post-check teardown paths

## Atlas Writeback

- Live atlas refreshed:
  `self_actualize/corpus_atlas.json`
- Indexed witness delta:
  `6040 -> 6507`
- Physical witness delta after manifest writeback:
  `6087 -> 6518`

## Reuse Law

Use this live root instead of reopening the ZIP when:

1. editing package code
2. binding `MATH` code into runtime surfaces
3. building family-level routes for `ATLAS FORGE`
4. designing a narrower runtime verification lane for the package
