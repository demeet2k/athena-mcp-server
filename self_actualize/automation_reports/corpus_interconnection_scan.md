# Corpus Interconnection Scan

Date: 2026-03-12
Run: corpus-weave-scan-5 (first automation run)
Scope: Full local Athena corpus in `C:/Users/dmitr/.codex/worktrees/d939/Athena Agent` with cortex/runtime/governance + domain surfaces.
Google Docs Gate: BLOCKED.

## Highest-Yield Interconnections (6)

### 1) Gate status -> live docs runtime -> obligation closure
- Interconnect:
  - Gate manifest, runtime queue, and self-actualize gate receipt need one shared state transition.
- Exact paths:
  - `C:/Users/dmitr/.codex/worktrees/d939/Athena Agent/NERVOUS_SYSTEM/95_MANIFESTS/GATE_STATUS.md`
  - `C:/Users/dmitr/.codex/worktrees/d939/Athena Agent/NERVOUS_SYSTEM/90_LEDGERS/OBLIGATIONS_LEDGER.md`
  - `C:/Users/dmitr/.codex/worktrees/d939/Athena Agent/self_actualize/live_docs_gate_status.md`
  - `C:/Users/dmitr/.codex/worktrees/d939/Athena Agent/self_actualize/mycelium_brain/nervous_system/06_active_queue.md`
  - `C:/Users/dmitr/.codex/worktrees/d939/Athena Agent/Trading Bot/docs_search.py`
- Rationale: This is still the dominant global blocker and propagates into capsule promotion, validation, and replay evidence.
- Blockers: `Trading Bot/credentials.json` and `Trading Bot/token.json` are absent.
- Next actions:
  1. Add OAuth files and run one authenticated `docs_search.py` query.
  2. Update all four gate surfaces in one commit.
  3. Record receipt in `PROMOTION_LEDGER.md`.

### 2) Atlas contract surfaces -> missing atlas artifacts
- Interconnect:
  - Nervous-system/metro/runtime docs repeatedly depend on atlas JSON files that are currently missing in this workspace.
- Exact paths:
  - `C:/Users/dmitr/.codex/worktrees/d939/Athena Agent/self_actualize/corpus_atlas_summary.md`
  - `C:/Users/dmitr/.codex/worktrees/d939/Athena Agent/self_actualize/archive_manifest.json`
  - `C:/Users/dmitr/.codex/worktrees/d939/Athena Agent/self_actualize/scan_reconciliation_report.md`
  - `C:/Users/dmitr/.codex/worktrees/d939/Athena Agent/NERVOUS_SYSTEM/90_LEDGERS/OBLIGATIONS_LEDGER.md`
  - `C:/Users/dmitr/.codex/worktrees/d939/Athena Agent/self_actualize/corpus_atlas.json` (missing)
  - `C:/Users/dmitr/.codex/worktrees/d939/Athena Agent/self_actualize/archive_atlas.json` (missing)
- Rationale: Multiple control surfaces cite atlas data, but the primary atlas artifacts are absent, isolating replay and evidence routing.
- Blockers: Atlas refresh output files were not generated in this worktree.
- Next actions:
  1. Rebuild atlas outputs into `self_actualize/corpus_atlas.json` and `self_actualize/archive_atlas.json`.
  2. Align summary counts (`559` vs newer receipts) after refresh.
  3. Mark O-003 status progression in obligations + validation queue.

### 3) Domain-scale families -> capsule coverage gap
- Interconnect:
  - High-volume families in runtime matrices must connect to corpus capsules and promotion ledgers.
- Exact paths:
  - `C:/Users/dmitr/.codex/worktrees/d939/Athena Agent/self_actualize/mycelium_brain/nervous_system/10_family_frontier_matrix.md`
  - `C:/Users/dmitr/.codex/worktrees/d939/Athena Agent/NERVOUS_SYSTEM/50_CORPUS_CAPSULES/INDEX.md`
  - `C:/Users/dmitr/.codex/worktrees/d939/Athena Agent/NERVOUS_SYSTEM/95_MANIFESTS/SOURCE_SURFACE_ATLAS.md`
  - `C:/Users/dmitr/.codex/worktrees/d939/Athena Agent/NERVOUS_SYSTEM/95_MANIFESTS/ACTIVE_RUN.md`
  - `C:/Users/dmitr/.codex/worktrees/d939/Athena Agent/NERVOUS_SYSTEM/90_LEDGERS/PROMOTION_LEDGER.md`
- Rationale: Runtime weights (Voynich/MATH/Trading Bot) are explicit, but only `deeper_crystalization` capsules are present, leaving R1/R3/R4/R6 weakly coupled.
- Blockers: Phases 4-6 are still pending; no promoted capsule directories for `math/`, `voynich/`, `neural_network/`, `ecosystem/`.
- Next actions:
  1. Create capsule stubs for `math`, `voynich`, and `neural_network` first.
  2. Add per-domain promotion receipts and update `SOURCE_SURFACE_ATLAS.md`.
  3. Move V-003 from broad pending to per-domain validation items.

### 4) Edge graph scaffolding -> executable cross-domain edges
- Interconnect:
  - Existing edge schemas and files need real non-deeper domain edges to unlock tile population.
- Exact paths:
  - `C:/Users/dmitr/.codex/worktrees/d939/Athena Agent/NERVOUS_SYSTEM/85_EDGES/00_EDGE_INDEX.md`
  - `C:/Users/dmitr/.codex/worktrees/d939/Athena Agent/NERVOUS_SYSTEM/85_EDGES/SOURCE_TO_CHAPTER_EDGES.md`
  - `C:/Users/dmitr/.codex/worktrees/d939/Athena Agent/NERVOUS_SYSTEM/85_EDGES/REF_EDGES.md`
  - `C:/Users/dmitr/.codex/worktrees/d939/Athena Agent/NERVOUS_SYSTEM/95_MANIFESTS/BUILD_QUEUE.md`
- Rationale: Edge infrastructure exists, but non-deeper edge rows are still pending, keeping Phase 8 crystal-tile work disconnected.
- Blockers: Missing upstream capsules for major domains; edge files remain scaffold-heavy.
- Next actions:
  1. Add first REF/IMPL rows for one MATH and one Voynich capsule.
  2. Populate `REF_EDGES.md` with at least 10 cross-chapter dependencies.
  3. Reclassify Phase 7 from PENDING to IN PROGRESS once first cross-domain edge pack lands.

### 5) Validation queue granularity -> real progress signals
- Interconnect:
  - Validation queue should be bound to current phase obligations and domain-level completions.
- Exact paths:
  - `C:/Users/dmitr/.codex/worktrees/d939/Athena Agent/NERVOUS_SYSTEM/95_MANIFESTS/VALIDATION_QUEUE.md`
  - `C:/Users/dmitr/.codex/worktrees/d939/Athena Agent/NERVOUS_SYSTEM/95_MANIFESTS/BUILD_QUEUE.md`
  - `C:/Users/dmitr/.codex/worktrees/d939/Athena Agent/NERVOUS_SYSTEM/90_LEDGERS/OBLIGATIONS_LEDGER.md`
  - `C:/Users/dmitr/.codex/worktrees/d939/Athena Agent/self_actualize/route_quality_ledger.json`
- Rationale: Queue entries are still broad and all pending; they do not expose per-domain completion or replay quality.
- Blockers: No domain-level validation IDs and no completed entries yet.
- Next actions:
  1. Split V-003 into `V-003a` (MATH), `V-003b` (Voynich), `V-003c` (Neural), `V-003d` (Ecosystem).
  2. Add explicit checks for atlas artifact presence and edge-pack density.
  3. Log first completed validation with receipt link.

### 6) Runtime family ganglia -> canonical cortex visibility
- Interconnect:
  - Active runtime ganglia and family tensor surfaces should be directly discoverable from canonical cortex manifests.
- Exact paths:
  - `C:/Users/dmitr/.codex/worktrees/d939/Athena Agent/self_actualize/mycelium_brain/nervous_system/ganglia/GANGLION_math.md`
  - `C:/Users/dmitr/.codex/worktrees/d939/Athena Agent/self_actualize/mycelium_brain/nervous_system/ganglia/GANGLION_voynich.md`
  - `C:/Users/dmitr/.codex/worktrees/d939/Athena Agent/self_actualize/mycelium_brain/nervous_system/13_family_tensor_field.md`
  - `C:/Users/dmitr/.codex/worktrees/d939/Athena Agent/NERVOUS_SYSTEM/95_MANIFESTS/ACTIVE_RUN.md`
  - `C:/Users/dmitr/.codex/worktrees/d939/Athena Agent/NERVOUS_SYSTEM/00_INDEX.md`
- Rationale: Runtime family operations are mature, but canonical manifests mostly reference them indirectly, reducing discoverability and replay continuity.
- Blockers: Missing direct cortex pointers for ganglion-level active fronts.
- Next actions:
  1. Add a “Runtime Family Fronts” subsection in `ACTIVE_RUN.md` with direct ganglion links.
  2. Mirror one family state snapshot into `NERVOUS_SYSTEM/95_MANIFESTS/`.
  3. Add a promotion receipt tying runtime ganglia updates to canonical manifest updates.

## Metro Pattern (cross-boundary)
- Line A: Gate pressure (OAuth blocker).
- Line B: Atlas presence vs atlas dependency.
- Line C: Domain mass vs capsule coverage.
- Line D: Scaffolded graph vs executable edges.
- Line E: Runtime maturity vs cortex visibility.
- Zero-point hub: `C:/Users/dmitr/.codex/worktrees/d939/Athena Agent/NERVOUS_SYSTEM/90_LEDGERS/OBLIGATIONS_LEDGER.md`.

## Delta vs Existing Report
- Material change: removed previously cited QSHRINK/Phase5/athenachka-specific fronts not present in this worktree state.
- Material change: elevated missing atlas artifact contract as a top interconnection blocker.
- Material change: reframed highest-yield actions around capsule coverage, edge execution, and validation granularity in the current corpus snapshot.
