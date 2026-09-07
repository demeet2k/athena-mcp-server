# CLOSURE GRAMMAR Ω2.1 — the unified framework

*Close at n, cross at n+1, return.* Eighty-seven myths, religions, philosophies, magical, esoteric, divinatory, astrological, calendrical, designed, engineered and scientific systems read against one law, with every arithmetic claim computed, every tradition entry graded and schema-validated, and the census tested against a permutation null.

| file | what |
|---|---|
| [00_LAW.md](00_LAW.md) | the equation, the four elements, what is new, the reading rules |
| [01_ARITHMETIC.md](01_ARITHMETIC.md) | the computed core: closing triples, carriers, regular numbers, partitions of unity, the twelve charts, tori, V₄ oracles, yarrow, geomancy, music, alphabets, triangular numbers, the great year, the King List, the die |
| [02_SEATS.md](02_SEATS.md) | the five seats of the crossing (extra · centre · withdrawn · return · residue) and the extension class; the motifs; the two ladders |
| [03_TRADITIONS.md](03_TRADITIONS.md) | the survey, family by family |
| [04_VERIFICATION_GRID.md](04_VERIFICATION_GRID.md) | **generated** grid: every tradition, every crossing, every residue, device, ladder, number with its factorization |
| [05_CENSUS.md](05_CENSUS.md) | **generated** census: the 7-bearer test by role, the charts of 360, seats and standings |
| [06_FALSIFIERS.md](06_FALSIFIERS.md) | falsifiers, negatives, the null model, the delta-chain against Ω44, the ⊥ frontier |
| [07_SEED.md](07_SEED.md) | CLOSURE.GRAMMAR.Ω2.1, the Q-SHRINK ALPHA+ seed |
| [corpus_extractions/](corpus_extractions/) | the seven per-file reports through which the uploaded corpus was read (evidence trail) |

## Executable parts

```
athena_mcp/closure_grammar.py              # arithmetic witnesses incl. the Cartan trichotomy + self-test  (python -m athena_mcp.closure_grammar)
athena_mcp/closure_grammar_registry.py     # the 87 tradition entries (source of truth), revision 2
athena_mcp/closure_grammar_schema.py       # schema + validator (provenance, marking, n+1)
athena_mcp/closure_grammar_report_core.py  # census, Wilson intervals, permutation null
spec/CLOSURE_GRAMMAR_REGISTRY_V1.json      # export of the registry
scripts/closure_grammar_report.py          # validate, export JSON, render 04 and 05   (python -m scripts.closure_grammar_report [--check])
tests/test_closure_grammar.py              # 26 tests: arithmetic, trichotomy, n+1 rule, schema, null model, JSON sync, MCP resources
athena://closure-grammar/registry, /census # read-only MCP resources served by the ATHENA server
```

To add a tradition: append a `T(...)` entry to the registry, run the report (it validates first and refuses an untraceable 🟢, an unmarked crossing or a unit seat that is not n+1), run the tests.

## Sources

- The uploaded corpus: `Magic_Systems.zip` (35 system extractions), `Philosophy.zip` (18 computational-philosophy documents), `DAO_SU`, `EGYPT_KHEPER_GANITAM`, `San_tana_Ga_ita` (three computational ontologies). Extraction reports were produced per file with a fixed schema; the corpus is cited by file name and is never used to date or attest a primary claim.
- Primary and reference texts checked on 2026-09-07 (named per entry): ETCSL King List; Wikipedia infoboxes and articles for the god-numbers, calendars, counts and myths listed in each entry's `sources`.
- The pulses Ω28–Ω44 and the CLOSURE.GRAMMAR.Ω1 seed.

## Continuation

The closure grammar is the CONST service and the seat law of [MYTHOS OS](../mythos_os/README.md), where every tradition is encoded as a program for one twelve-service abstract machine and ATHENA is the reference module. Where a mythos module carries `closure_grammar_id`, the VM attaches this registry's verified crossings to the module's process table.

## Standing

`STRUCTURAL PASS / SEMANTIC READINGS GRADED / AUTHORITY EXTERNAL`. This set describes counts, seats and devices. It authorises no practice, dates nothing by a modern reconstruction, and treats shared symbols as shared symbols only (`athena_mcp/mythic_strata_runtime.py` laws).
