# SOURCE TO CHAPTER EDGES

## Purpose

Maps corpus capsules to the chapter tile slots they feed. These edges are created during capsule creation and tile population.

## Edge Table

### DEEPER CRYSTALIZATION Domain

| EdgeID | Kind | Source Capsule | Target Chapter(s) | Scope | Truth |
|--------|------|---------------|-------------------|-------|-------|
| E-SC-001 | REF | CC-DC-01 (Manuscript Seed) | Ch01, Ch06, Ch20 | source-chapter | AMBIG |
| E-SC-002 | REF | CC-DC-03 (AQM Text Book) | Ch01, Ch04, Ch18 | source-chapter | AMBIG |
| E-SC-003 | REF | CC-DC-04 (AQM_LM_CUT Hybrid) | Ch01, Ch04, Ch15, Ch18 | source-chapter | AMBIG |
| E-SC-004 | REF | CC-DC-05 (Architect's Core Init) | Ch01, Ch11 | source-chapter | AMBIG |
| E-SC-005 | REF | CC-DC-07 (Ch11 Perpetual Motion) | Ch11 | source-chapter | AMBIG |
| E-SC-006 | REF | CC-DC-09 (I AM so AM I) | Ch01, Ch21 | source-chapter | AMBIG |
| E-SC-007 | REF | CC-DC-10 (Info from Void) | Ch11, Ch03 | source-chapter | AMBIG |
| E-SC-008 | REF | CC-DC-12 (Legal Transport) | Ch01, Ch07, Ch12 | source-chapter | AMBIG |
| E-SC-009 | REF | CC-DC-13 (Megalithic Tome) | Ch01, Ch07, Ch08, Ch18 | source-chapter | AMBIG |
| E-SC-010 | REF | CC-DC-17 (Self-Routing Meta) | Ch09, Ch11, Ch21 | source-chapter | AMBIG |
| E-SC-011 | REF | CC-DC-20 (Athena Framework) | Ch01, Ch06, Ch15 | source-chapter | AMBIG |
| E-SC-012 | REF | CC-DC-22 (Crystal Live) | Ch02, Ch06, Ch10 | source-chapter | AMBIG |
| E-SC-013 | REF | CC-DC-23 (External Crystal) | Ch06, Ch20, Ch21 | source-chapter | AMBIG |
| E-SC-014 | REF | CC-DC-24 (Holographic Brain) | Ch06, Ch09, Ch13 | source-chapter | AMBIG |
| E-SC-015 | REF | CC-DC-25 (Invisible Teacher) | Ch06, Ch21 | source-chapter | AMBIG |
| E-SC-016 | REF | CC-DC-27 (Solenoidal Engine) | Ch11, Ch13, Ch17 | source-chapter | AMBIG |
| E-SC-017 | REF | CC-DC-28 (Unified Cyclical Time) | Ch08, Ch19 | source-chapter | AMBIG |
| E-SC-018 | REF | CC-DC-30 (Voynich Jazz) | Ch07, Ch09 | source-chapter | AMBIG |

### Other Domains (PENDING)

MATH, Voynich, Neural Network, Ecosystem, published books, and root file edges will be added as those domain capsules are created.

## Notes

- All edges default to truth class AMBIG until tile slots are populated with synthesized content
- Specific tile slot assignments (e.g., `Ch01<0000>.S1.a`) will be refined during Phase 8
- Edge IDs follow pattern: `E-SC-XXX` for source-to-chapter
