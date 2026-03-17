# Witness Hierarchy Derivation Receipt

- Generated: `2026-03-13T21:36:16.302672+00:00`
- Quest: `Q18 Machine-Derive The Witness Hierarchy`
- Verdict: `OK`
- Command: `python -m self_actualize.runtime.derive_witness_hierarchy`
- Derivation version: `2026-03-09.q18.runtime`

## Measured Values

- `Physical witness`: `1021742`
- `Indexed witness`: `7895`
- `Board witness`: `14742`
- `Archive witness`: `2041`
- `Promoted witness`: `1818`

## Source Provenance

- physical witness:
  `recursive file sweep excluding runtime ignore directories`
- indexed witness:
  `len(corpus_atlas.records)` from `C:\Users\dmitr\Documents\Athena Agent\self_actualize\corpus_atlas.json` at `2026-03-13T21:35:33.734557+00:00`
- board witness:
  `parsed from board status markdown` from `C:\Users\dmitr\Documents\Athena Agent\DEEPER CRYSTALIZATION\ACTIVE_NERVOUS_SYSTEM\07_FULL_PROJECT_INTEGRATION_256\06_REALTIME_BOARD\00_STATUS\00_BOARD_STATUS.md` at `2026-03-13T21:55:30.228459+00:00`
- archive witness:
  `len(archive_atlas.records) across 16 archives` from `C:\Users\dmitr\Documents\Athena Agent\self_actualize\archive_atlas.json` at `2026-03-08T13:24:18.686859+00:00`
- promoted witness:
  `parsed from live_atlas_records in bronze state header` from `C:\Users\dmitr\Documents\Athena Agent\DEEPER CRYSTALIZATION\_build\nervous_system\manifests\STATE_HEADER.md` at `2026-03-09T16:32:05.114081+00:00`

## Derivation Notes

- archive count observed alongside archive witness: `16`
- board witness is intentionally smaller than indexed witness because the board is a control-plane-visible slice, not the whole searchable corpus
- promoted witness is intentionally smaller than indexed witness because it measures the currently metabolized nervous-system slice, not the whole organism
