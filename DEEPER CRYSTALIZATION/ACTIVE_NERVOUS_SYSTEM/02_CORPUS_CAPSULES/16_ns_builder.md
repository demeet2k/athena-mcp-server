
# ns_builder

- Relative path: `LocalProject/ns_builder.py`
- Source layer: `LocalProject`
- Kind: `code`
- Role tags: `executable`
- Text extractable: `True`
- Family: `Civilization design, hierarchy, governance, and law`

## Working focus

Defines hierarchy, councils, law, calendars, and civilization-scale governance for multi-agent continuity.

## Suggested chapter anchors

- `Ch17`
- `Ch18`
- `Ch20`
- `Ch21`

## Suggested appendix anchors

- `AppA`
- `AppD`
- `AppG`
- `AppP`

## Heading candidates

- `#!/usr/bin/env python3`
- `LENSES = ("S", "F", "C", "R")`
- `FACETS = (`
- `FAMILY_LABELS = {`
- `PENTADIC_LANES = (`
- `SWARM_LAYERS = (`
- `TRUTH_DEFAULT = "AMBIG"`
- `GOVERNANCE_SIGNS = (`

## Excerpt

#!/usr/bin/env python3 from __future__ import annotations import json import re import shutil from dataclasses import dataclass from datetime import datetime, timezone from pathlib import Path LENSES = ("S", "F", "C", "R") FACETS = ( ("1", "Objects"), ("2", "Laws"), ("3", "Constructions"), ("4", "Certificates"), ) ATOMS = ("a", "b", "c", "d") FAMILY_LABELS = { "live-orchestration": "Live orchestration and prompt control", "void-and-collapse": "Void, Chapter 11, and collapse engines", "helical-recursion-engine": "Helical recursion, lift law, and manifestation engine", "manuscript-architecture": "Manuscript architecture and routing law", "higher-dimensional-geometry": "Higher-dimensional geometry and holographic kernel", "civilization-and-governance": "Civilization design, hierarchy, governa
