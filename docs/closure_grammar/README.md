# CLOSURE GRAMMAR Ω2 — the unified framework

*Close at n, cross at n+1, return.* Sixty-three myths, religions, philosophies, magical, esoteric, divinatory, astrological, calendrical and game systems read against one law, with every arithmetic claim computed and every tradition entry graded.

| file | what |
|---|---|
| [00_LAW.md](00_LAW.md) | the equation, the four elements, what is new, the reading rules |
| [01_ARITHMETIC.md](01_ARITHMETIC.md) | the computed core: closing triples, carriers, regular numbers, partitions of unity, the twelve charts, tori, V₄ oracles, yarrow, geomancy, music, alphabets, triangular numbers, the great year, the King List, the die |
| [02_SEATS.md](02_SEATS.md) | the five seats of the crossing (extra · centre · withdrawn · return · residue) and the extension class; the motifs; the two ladders |
| [03_TRADITIONS.md](03_TRADITIONS.md) | the survey, family by family |
| [04_VERIFICATION_GRID.md](04_VERIFICATION_GRID.md) | **generated** grid: every tradition, every crossing, every residue, device, ladder, number with its factorization |
| [05_CENSUS.md](05_CENSUS.md) | **generated** census: the 7-bearer test by role, the charts of 360, seats and standings |
| [06_FALSIFIERS.md](06_FALSIFIERS.md) | falsifiers, negatives, the null model, the delta-chain against Ω44, the ⊥ frontier |
| [07_SEED.md](07_SEED.md) | CLOSURE.GRAMMAR.Ω2, the Q-SHRINK ALPHA+ seed |

## Executable parts

```
athena_mcp/closure_grammar.py            # arithmetic witnesses + self-test  (python -m athena_mcp.closure_grammar)
athena_mcp/closure_grammar_registry.py   # the 63 tradition entries (source of truth)
spec/CLOSURE_GRAMMAR_REGISTRY_V1.json    # export of the registry
scripts/closure_grammar_report.py        # export JSON, render 04 and 05     (python -m scripts.closure_grammar_report [--check])
tests/test_closure_grammar.py            # 18 tests: arithmetic, n+1 rule, JSON sync, report
```

To add a tradition: append a `T(...)` entry to the registry, run the report, run the tests. A crossing must have a seat and be *marked* by its source; the tests enforce `cross == n + 1` for the four unit seats and `cross > n` for residue and extension.

## Sources

- The uploaded corpus: `Magic_Systems.zip` (35 system extractions), `Philosophy.zip` (18 computational-philosophy documents), `DAO_SU`, `EGYPT_KHEPER_GANITAM`, `San_tana_Ga_ita` (three computational ontologies). Extraction reports were produced per file with a fixed schema; the corpus is cited by file name and is never used to date or attest a primary claim.
- Primary and reference texts checked on 2026-09-07 (named per entry): ETCSL King List; Wikipedia infoboxes and articles for the god-numbers, calendars, counts and myths listed in each entry's `sources`.
- The pulses Ω28–Ω44 and the CLOSURE.GRAMMAR.Ω1 seed.

## Standing

`STRUCTURAL PASS / SEMANTIC READINGS GRADED / AUTHORITY EXTERNAL`. This set describes counts, seats and devices. It authorises no practice, dates nothing by a modern reconstruction, and treats shared symbols as shared symbols only (`athena_mcp/mythic_strata_runtime.py` laws).
