# EQUIV EDGES

## Purpose

Records semantic equivalences between sources that cover the same concept, enabling de-duplication and cross-validation.

## Edge Table

| EdgeID | Kind | Source A | Source B | Equivalence | Truth |
|--------|------|---------|---------|-------------|-------|
| E-EQ-001 | EQUIV | CC-DC-01 (Manuscript Seed v1) | CC-DC-02 (Manuscript Seed v2) | Same document, different versions | NEAR |
| E-EQ-002 | EQUIV | CC-DC-07 (Ch11 Perpetual Motion v1) | CC-DC-08 (Ch11 Perpetual Motion v2) | Same chapter, different drafts | NEAR |
| E-EQ-003 | EQUIV | CC-DC-10 (Info from Void v1) | CC-DC-11 (Info from Void v2) | Same manuscript, different versions | NEAR |
| E-EQ-004 | EQUIV | CC-DC-17 (Self-Routing Meta v1) | CC-DC-18 (Self-Routing Meta v2) | Same framework, different versions | NEAR |
| E-EQ-005 | EQUIV | CC-DC-20 (Athena Framework v1) | CC-DC-21 (Athena Framework v2) | Same synthesis, different versions | NEAR |
| E-EQ-006 | EQUIV | CC-DC-25 (Invisible Teacher v1) | CC-DC-26 (Invisible Teacher v2) | Same textbook, different versions | NEAR |

## Notes

- EQUIV edges require explicit forward/backward maps showing what changed
- Version pairs should be resolved during tile population: use the most complete version as primary
- Additional EQUIV edges will be discovered across domains (e.g., AQM tome vs. AQM capsule in DEEPER CRYSTALIZATION)
