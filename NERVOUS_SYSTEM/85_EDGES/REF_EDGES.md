# REF EDGES (Cross-Chapter)

## Purpose

Records cross-chapter dependencies where one chapter explicitly depends on another's content to be interpreted correctly.

## Edge Table

| EdgeID | Kind | Src | Dst | Justification | Truth |
|--------|------|-----|-----|---------------|-------|
| E-REF-001 | REF | Ch02 (Addressing) | Ch01 (Kernel) | Address algebra requires kernel definitions | NEAR |
| E-REF-002 | REF | Ch03 (Truth) | Ch01 (Kernel) | Truth corridors require kernel entry law | NEAR |
| E-REF-003 | REF | Ch04 (Zero-Point) | Ch03 (Truth) | Stabilization requires truth lattice | NEAR |
| E-REF-004 | REF | Ch05 (Paradox) | Ch03 (Truth) | Quarantine requires corridor truth | NEAR |
| E-REF-005 | REF | Ch05 (Paradox) | Ch04 (Zero-Point) | Quarantine extends stabilization | NEAR |
| E-REF-006 | REF | Ch07 (Tunnels) | Ch06 (Docs-as-Theories) | Tunnels are morphisms between theory-documents | NEAR |
| E-REF-007 | REF | Ch08 (Sync) | Ch07 (Tunnels) | Synchronization operates over tunnels | NEAR |
| E-REF-008 | REF | Ch09 (Retrieval) | Ch02 (Addressing) | Metro routing requires address algebra | NEAR |
| E-REF-009 | REF | Ch09 (Retrieval) | Ch08 (Sync) | Retrieval uses synchronization calculus | NEAR |
| E-REF-010 | REF | Ch11 (Void) | Ch07 (Tunnels) | Void transport is a tunnel type | NEAR |
| E-REF-011 | REF | Ch11 (Void) | Ch03 (Truth) | Restart-token requires truth corridors | NEAR |
| E-REF-012 | REF | Ch12 (Legality) | Ch03 (Truth) | Certificates verify truth class | NEAR |
| E-REF-013 | REF | Ch12 (Legality) | Ch11 (Void) | Closure covers void-based reset | NEAR |
| E-REF-014 | REF | Ch14 (Migration) | Ch12 (Legality) | Migration requires legality certificates | NEAR |
| E-REF-015 | REF | Ch15 (CUT) | Ch01 (Kernel) | CUT implements kernel contracts | NEAR |
| E-REF-016 | REF | Ch16 (Verification) | Ch12 (Legality) | Replay harnesses verify certificates | NEAR |
| E-REF-017 | REF | Ch18 (Macro) | Ch04 (Zero-Point) | Global invariants build on stabilization | NEAR |
| E-REF-018 | REF | Ch19 (Convergence) | Ch08 (Sync) | Fixed points extend synchronization | NEAR |
| E-REF-019 | REF | Ch20 (Collective) | Ch09 (Retrieval) | Multi-agent sync uses metro routing | NEAR |
| E-REF-020 | REF | Ch21 (Self-Replication) | Ch01 (Kernel) | Next crystal seeds from kernel | NEAR |
| E-REF-021 | REF | Ch21 (Self-Replication) | Ch06 (Docs-as-Theories) | Self-replication requires doc-theory model | NEAR |

## Notes

- Truth class NEAR indicates these dependencies are structurally clear but the actual content binding is not yet replay-verified
- Promotion to OK requires populating both source and destination tile slots
