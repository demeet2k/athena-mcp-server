# TesseractHeader Schema v4.3

## Purpose

`TesseractHeader` is the public routing banner for chapter-level and atom-level outputs.

## Canonical Form

`[Z_i <-> Z* | Arc alpha | Rot rho | Lane nu | View L/* | omega=n]`

## Fields

- `Z_i`: local zero point identifier
- `Z*`: absolute zero bridge point
- `Arc`: arc index
- `Rot`: rotation index
- `Lane`: rail label in `{Su, Me, Sa}`
- `View`: actual lens in `{S, F, C, R}` or `*` for chapter scope
- `omega`: `chapter_index - 1`
