# Grand Central Weight Exchange

Date: `2026-03-12`
Generated: `2026-03-12T19:09:36.577589+00:00`
Docs gate: `BLOCKED`
Verdict: `OK`

This ledger defines the unified internal weight vector for Grand Central Station.

## Weight Fields

- `salience`: how much corpus mass or strategic centrality the route carries
- `proof`: how much witness-bearing authority the route currently owns
- `freshness`: how alive and current the route is in the runtime organism
- `cost`: how expensive the route is to maintain or metabolize
- `continuity`: how well the route preserves lawful carry-through across changes
- `confidence`: confidence floor derived from proof and freshness together
- `replay_value`: how well the route closes through replay, receipt, and rerun

## Dispatch Law

`dispatch = 2.5*salience + 2*proof + 1.5*freshness + 1.25*continuity + 1.5*confidence + 1.5*replay - 1.5*cost`

## Route Weights

| ID | Route | Salience | Proof | Freshness | Cost | Continuity | Confidence | Replay | Dispatch |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C-007 | `Trading Bot` -> `self_actualize` | 1.000 | 0.917 | 0.770 | 0.845 | 0.860 | 0.844 | 0.930 | 7.958 |
| C-008 | `DEEPER CRYSTALIZATION` -> `self_actualize` | 0.619 | 0.937 | 0.890 | 0.669 | 0.930 | 0.914 | 0.930 | 7.681 |
| C-011 | `NERUAL NETWORK` -> `self_actualize` | 0.619 | 0.917 | 0.890 | 0.583 | 0.860 | 0.904 | 0.930 | 7.666 |
| C-002 | `self_actualize` -> `NERVOUS_SYSTEM` | 0.619 | 0.917 | 0.890 | 0.595 | 0.860 | 0.904 | 0.930 | 7.649 |
| C-003 | `QSHRINK - ATHENA (internal use)` -> `self_actualize` | 0.686 | 0.917 | 0.890 | 0.794 | 0.860 | 0.904 | 0.930 | 7.518 |
| C-013 | `mycelial_unified_nervous_system_bundle` -> `self_actualize` | 0.619 | 0.717 | 0.810 | 0.537 | 0.930 | 0.764 | 0.930 | 7.094 |
| C-006 | `Voynich` -> `Athenachka Collective Books` | 0.359 | 0.907 | 0.890 | 0.506 | 0.900 | 0.899 | 0.820 | 6.992 |
| C-001 | `MATH` -> `Voynich` | 0.359 | 0.927 | 0.890 | 0.589 | 0.840 | 0.909 | 0.820 | 6.847 |
| C-010 | `ECOSYSTEM` -> `MATH` | 0.314 | 0.927 | 0.890 | 0.507 | 0.820 | 0.909 | 0.820 | 6.830 |
| C-004 | `ORGIN` -> `I AM ATHENA` | 0.080 | 0.937 | 0.890 | 0.345 | 0.960 | 0.914 | 0.820 | 6.692 |
| C-005 | `Athena FLEET` -> `NERVOUS_SYSTEM` | 0.081 | 0.917 | 0.890 | 0.386 | 0.860 | 0.904 | 0.930 | 6.617 |
| C-012 | `CLEAN` -> `DEEPER CRYSTALIZATION` | 0.231 | 0.823 | 0.760 | 0.498 | 0.930 | 0.791 | 0.820 | 6.195 |
| C-009 | `GAMES` -> `Stoicheia (Element Sudoku)` | 0.260 | 0.793 | 0.760 | 0.492 | 0.880 | 0.776 | 0.820 | 6.132 |

## Thresholds

- promotion threshold: `6.35`
- live interchange threshold: `7.0`
- soft demotion threshold: `5.4`
- route baseline freshness: `0.81`

## Promotion Law

- routes above the promotion threshold may claim live interchange attention
- routes above the live interchange threshold are first-wave station priorities
- routes below the soft demotion threshold stay readable, but should not outrank fresher corridors
