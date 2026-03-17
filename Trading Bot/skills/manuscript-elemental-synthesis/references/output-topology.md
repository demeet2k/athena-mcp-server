# Output Topology

The build script writes a folder named `MANUSCRIPT_ELEMENTAL_NET_4X4` under the workspace root.

## Control

- `00_CONTROL/00_READ_ME_FIRST.md`
- `00_CONTROL/01_CORPUS_CANON.md`
- `00_CONTROL/02_EXECUTION_MODEL.md`
- `00_CONTROL/03_ELEMENTAL_ASSIGNMENTS.md`
- `00_CONTROL/04_deep_synthesis.md`
- `00_CONTROL/05_deep_synthesis_expanded.md` when present

## Corpus layers

- `01_SOURCE_EXTRACTS`: full markdown extracts of source manuscripts
- `02_INDIVIDUAL_SYNTHESIS`: one card per manuscript
- `03_PAIRWISE_SYNERGIES`: ordered primary-lattice pair docs

## Element and symmetry layers

- `04_ELEMENTS/<element>/00_lens_overview.md`
- `04_ELEMENTS/<element>/01_64_observations.md`
- `05_SYMMETRIES/00_neutral_64_observations.md`
- `05_SYMMETRIES/*.md` for the 15 element combinations

## Maps and appendices

- `06_METRO_MAPS/*.md`
- `07_APPENDICES/appendix_*.md`
- `08_ZERO_POINT/00_zero_point_synthesis.md`
- `09_AUXILIARY_LENSES/*.md`
- `10_INDEXES/00_pairwise_matrix.md`
- `10_INDEXES/01_corpus_index.json`
