# Voynich Metro Map Working

This working metro surface is now machine-current. Every corridor shown below is derived only from recorded line operator chains plus the transport registry; no corridor is hand-invented.

- Docs gate: `BLOCKED`
- Edge packets: `5772`
- Companion witness: `FULL_TRANSLATION/metro/VOYNICH_METRO_MAP_ROSETTA_COMPANION.md`

## Metro Principles

- Corridor weights come from recorded line counts, not from hand-ranked symbolism.
- Notation routes are lawful fan-outs through the transport registry, so ties within a book are expected.
- Node routes are the manuscript-to-neural attachments already recorded by the Rosetta machine.

## Top Book -> Notation Corridors

| Source Book | Target Notation | Class | Carrier | Weight |
| --- | --- | --- | --- | ---: |
| `Book V` | `aqm` | `domain` | AQM carrier | 1561 |
| `Book V` | `astrology` | `domain` | timing and house packet | 1561 |
| `Book V` | `biology` | `domain` | biological process packet | 1561 |
| `Book V` | `c` | `code` | C function | 1561 |
| `Book V` | `chemistry` | `domain` | chemical composition vector | 1561 |
| `Book V` | `cpp` | `code` | C++ function | 1561 |
| `Book V` | `cut` | `domain` | CUT boundary-flow carrier | 1561 |
| `Book V` | `flow_dsl` | `code` | flow graph DSL | 1561 |
| `Book V` | `geometry` | `domain` | geometric path | 1561 |
| `Book V` | `html` | `code` | HTML article | 1561 |

## Top Book -> Node Corridors

| Source Book | Target Node | Node Label | Weight |
| --- | --- | --- | ---: |
| `Book V` | `N09` | Pharmaceutical Folio Corpus | 1561 |
| `Book I` | `N05` | Plant Folio Corpus | 1403 |
| `Book III` | `N07` | Bath Folio Corpus | 818 |
| `Book II` | `N06` | Astrology Folio Corpus | 312 |
| `Book IV` | `N08` | Cosmology Folio Corpus | 138 |

## Bottlenecks

| Source Book | Target Notation | Class | Carrier | Weight |
| --- | --- | --- | --- | ---: |
| `Book IV` | `aqm` | `domain` | AQM carrier | 138 |
| `Book IV` | `astrology` | `domain` | timing and house packet | 138 |
| `Book IV` | `biology` | `domain` | biological process packet | 138 |
| `Book IV` | `c` | `code` | C function | 138 |
| `Book IV` | `chemistry` | `domain` | chemical composition vector | 138 |
| `Book IV` | `cpp` | `code` | C++ function | 138 |
| `Book IV` | `cut` | `domain` | CUT boundary-flow carrier | 138 |
| `Book IV` | `flow_dsl` | `code` | flow graph DSL | 138 |
| `Book IV` | `geometry` | `domain` | geometric path | 138 |
| `Book IV` | `html` | `code` | HTML article | 138 |

## Corridor Notes

Because the current transport layer exports each recorded line-chain into every notation family, notation corridors tie at the source-book line total. This is not a bug in the metro: it is the current lawful transport geometry of the Rosetta compiler.
