# Record Locator Index

Docs gate: `BLOCKED`

## Top-Level Root Shards

| Top Level Root | Records | Shard |
| --- | --- | --- |
| 4-Bit | 2 | [VA-LOCATOR-4_bit](visual_atlas/record_locator_4_bit.md) |
| Algorithms | 15 | [VA-LOCATOR-algorithms](visual_atlas/record_locator_algorithms.md) |
| COMPLETE TOMES | 93 | [VA-LOCATOR-complete_tomes](visual_atlas/record_locator_complete_tomes.md) |
| FRAMEWORKS CODE | 6 | [VA-LOCATOR-frameworks_code](visual_atlas/record_locator_frameworks_code.md) |
| GLOBAL MATH - MYTH | 17 | [VA-LOCATOR-global_math_myth](visual_atlas/record_locator_global_math_myth.md) |
| Hybrid Equations | 15 | [VA-LOCATOR-hybrid_equations](visual_atlas/record_locator_hybrid_equations.md) |
| Hybrid Equations for Algorithmic Shortcuts.docx | 1 | [VA-LOCATOR-hybrid_equations_for_algorithmic_shortcuts_docx](visual_atlas/record_locator_hybrid_equations_for_algorithmic_shortcuts_docx.md) |
| Latin Rose Math | 3 | [VA-LOCATOR-latin_rose_math](visual_atlas/record_locator_latin_rose_math.md) |
| MATH GOD | 33 | [VA-LOCATOR-math_god](visual_atlas/record_locator_math_god.md) |
| MYTH - MATH | 137 | [VA-LOCATOR-myth_math](visual_atlas/record_locator_myth_math.md) |
| Matrix Multiplication | 66 | [VA-LOCATOR-matrix_multiplication](visual_atlas/record_locator_matrix_multiplication.md) |
| Q shrink | 17 | [VA-LOCATOR-q_shrink](visual_atlas/record_locator_q_shrink.md) |
| THE THEORY OF TEXTURE.docx | 1 | [VA-LOCATOR-the_theory_of_texture_docx](visual_atlas/record_locator_the_theory_of_texture_docx.md) |
| The Crystal | 31 | [VA-LOCATOR-the_crystal](visual_atlas/record_locator_the_crystal.md) |
| Tri-Solenoidal Engine (TSE)_ Geometric Nested Compression Fractals.docx | 1 | [VA-LOCATOR-tri_solenoidal_engine_tse_geometric_nested_compression_fractals_docx](visual_atlas/record_locator_tri_solenoidal_engine_tse_geometric_nested_compression_fractals_docx.md) |
| Tunneling | 64 | [VA-LOCATOR-tunneling](visual_atlas/record_locator_tunneling.md) |

## Locator Contract

- every canonical record appears once in exactly one top-level locator shard
- each locator row links to primary and secondary hemisphere atlas shards
- each locator row carries both route ids plus composer and synthesis seed ids

## Commands

```powershell
python -m self_actualize.runtime.query_myth_math_hemisphere_brain record --record-id <record_id>
python -m self_actualize.runtime.compose_myth_math_hemisphere_routes record --record-id <record_id>
python -m self_actualize.runtime.synthesize_myth_math_hemisphere_routes record --record-id <record_id>
```
