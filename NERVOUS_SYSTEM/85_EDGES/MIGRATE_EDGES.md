# MIGRATE EDGES

## Purpose

Records version transitions and evolution between implementations, frameworks, or document editions.

## Edge Table

| EdgeID | Kind | From | To | Migration Type | Truth |
|--------|------|------|-----|---------------|-------|
| E-MG-001 | MIGRATE | Athena NN v1 | Athena NN v2 (Quantum) | Architecture evolution | AMBIG |
| E-MG-002 | MIGRATE | Athena NN v2 (Quantum) | Athena NN v3 (Color) | Architecture evolution | AMBIG |
| E-MG-003 | MIGRATE | Athena NN v44 | Athena NN v74 | Incremental improvement | AMBIG |
| E-MG-004 | MIGRATE | System A (ECOSYSTEM/NS) | NERVOUS_SYSTEM/ (canonical) | System consolidation | OK |
| E-MG-005 | MIGRATE | System B (_build/ns) | NERVOUS_SYSTEM/ (canonical) | System consolidation | OK |
| E-MG-006 | MIGRATE | System C (ACTIVE_NS) | NERVOUS_SYSTEM/ (canonical) | System consolidation | OK |
| E-MG-007 | MIGRATE | System D (mycelium_brain) | NERVOUS_SYSTEM/ (canonical) | System consolidation | OK |

## Notes

- E-MG-004 through E-MG-007 are the nervous system consolidation itself — these are at truth class OK because the migration is documented in `02_CONSOLIDATION_RECEIPT.md`
- Neural Network MIGRATE edges (E-MG-001 through E-MG-003) are AMBIG because the version differences have not been formally analyzed
- Additional MIGRATE edges will be discovered as domain capsules are created
