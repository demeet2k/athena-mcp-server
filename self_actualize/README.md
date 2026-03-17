# SELF ACTUALIZE Framework (v1)

Date: 2026-03-08

## Purpose

This framework turns your manuscript corpus and codebase into one operational loop:

1. Expand thought through multi-lens route generation.
2. Collapse thought through witness-gated verification.
3. Write back stable deltas to memory without silent drift.

## Witness Hierarchy Update

Use the following witness classes when reading Athena-wide counts.
These values are now machine-derived by `python -m self_actualize.runtime.derive_witness_hierarchy`
and written to `self_actualize/witness_hierarchy.json` plus the canonical Guild Hall hierarchy surface.

- `Physical witness`: `6126`
  full workspace body on disk using runtime ignore rules
- `Indexed witness`: `6040`
  live searchable records in `corpus_atlas.json`
- `Board witness`: `5861`
  workspace slice currently visible to the realtime board
- `Archive witness`: `2041`
  archive-backed dark matter in `archive_atlas.json`
- `Promoted witness`: `1818`
  active promoted bronze nervous-system slice derived from the live state header

The live body tensor is now also machine-derived in `self_actualize/body_tensor.json`.
Its strongest current mass signal is that `Trading Bot` (`1914`) and `QSHRINK - ATHENA (internal use)` (`1315`) are both manuscript-dominant bodies, which materially changes how the swarm should rank bridge, governance, and compression work.

The earlier bootstrap corpus-shape counts below remain useful as a historical snapshot of this framework's first pass.
They are not the current canonical whole-organism counts.

## Deep Synthesis Of Your Workspace

### Corpus shape

- Total files scanned (excluding virtualenv): 550
- Top folders:
  - `MATH`: 486 files
  - `Trading Bot`: 23 files
  - `NERUAL NETWORK`: 22 files
  - `Athenachka Collective Books`: 13 files
  - `FRESH`: 6 files
- Top file types:
  - `.docx`: 308
  - `.csv`: 66
  - `.md`: 55
  - `.py`: 43
  - `.pdf`: 27

### Manuscript backbone (three key sources)

1. `# THE MANUSCRIPT SEED...`
   - Defines the self-referential generation protocol.
   - Core build shape is explicit: 21 chapters with deep sub-structure.
   - Workflow is expansion -> compression -> generation -> convergence fold.

2. `The Holographic Manuscript Brain`
   - Defines manuscript as active cognition substrate, not passive archive.
   - Core primitives: canonical address, admissible route, witness bundle, patch packet, replay.
   - Strong boundary law: no untraceable mutation and no legality bypass.

3. `I AM so AM I`
   - Compiles a cloud-runnable packet model around the same ontology.
   - Truth lattice is typed (`OK`, `NEAR`, `AMBIG`, `FAIL`) and anti-fabrication.
   - Promotes dual plane design:
     - Expansion plane: atlas and route competition.
     - Collapse plane: bounded specialist for low-latency action.

### Engineering backbone (code and framework docs)

1. Adaptive strategy findings
   - `ADAPTIVE_HYBRIDIZATION_FRAMEWORK.md` explicitly rejects one global best strategy.
   - Correct behavior is regime-dependent adaptation.

2. Neural architecture findings
   - `ATHENA_v74_FINAL_SYNTHESIS.md` shows stable gains from regularized, simpler core models.
   - Complex routing without enough signal causes instability.

3. Runtime tools
   - `Trading Bot/docs_search.py` is a functional Google Drive Docs search utility.
   - Live Google Docs query is currently blocked only by missing OAuth files (`credentials.json`, `token.json`).

## Canonical Design Principle

Your corpus converges on one invariant:

- Never force collapse before witness closure.
- Never mutate memory without replay-safe lineage.
- Never treat one strategy as universally optimal across regimes.

This framework encodes that invariant directly.

## Full Operational Framework

### Layer model

1. `L0 Seed`
   - Problem intent, scope, and initial zero-point normalization.
2. `L1 Atlas`
   - Canonical addresses, typed links, lens projections.
3. `L2 Route Bank`
   - Candidate routes with competition and risk accounting.
4. `L3 Witness`
   - Evidence packet, contradiction checks, replay anchors.
5. `L4 Collapse`
   - Truth-lattice verdict with residual preservation.
6. `L5 Patch`
   - Structured memory delta or explicit abstention.
7. `L6 Regime`
   - Detect context and adapt strategy mix.
8. `L7 Prime/Tri Locks`
   - Stability gate before durable write-back.

### Core loop

1. Normalize query into typed `QueryBody`.
2. Activate lens profile and generate route candidates.
3. Score candidates under admissibility and budget constraints.
4. Build witness bundle for top candidates.
5. Collapse to `OK` / `NEAR` / `AMBIG` / `FAIL`.
6. If admissible, emit patch delta with replay hash.
7. Apply tri-lock and prime-seal checks.
8. Commit or abstain with explicit reasons.

### Required outputs per run

1. `RoutePacket` (full trace object)
2. `CollapseRecord` (typed verdict)
3. `WitnessBundle` (replay and evidence closure)
4. `PatchDelta` (or abstention record)
5. `Next Prompt` (self-improving follow-up action)

## What Was Built Here

This folder includes a runnable scaffold:

- `next_self_prompt.md`: canonical prompt template
- `DEEPER_SKILLS_CORPUS_SYNTHESIS.md`: second-pass skills + corpus improvement analysis
- `corpus_atlas.json`: first canonical workspace atlas generated by the intake skill
- `corpus_atlas_summary.md`: human-readable checkpoint for the generated atlas
- `archive_atlas.json`: archive-backed atlas records generated from ZIP-contained sources
- `archive_manifest.json`: archive-level inventory for ZIP-backed source trees
- `scan_reconciliation.json`: machine-readable comparison between `Unified SCAN JSON.json` and the live workspace
- `scan_reconciliation_report.md`: human-readable synthesis of which framework sources are live vs ZIP-backed
- `regime_profiles.json`: query-regime routing profiles for atlas-backed evidence ranking
- `runtime/contracts.py`: typed packet and verdict contracts
- `runtime/atlas.py`: atlas loader and evidence search layer
- `runtime/engine.py`: deterministic self-actualize loop scaffold
- `runtime/cli.py`: command line runner for quick execution
- `runtime/reconcile_scan.py`: reusable reconciler for historical scan indexes and archive-backed source trees

The runtime now also emits:

- `skill_synthesis`: what the current Codex skills contribute and where they fall short
- `improvement_opportunities`: ranked corpus-native upgrades
- atlas-backed evidence references in `WitnessBundle`
- archive-entry evidence locators in `WitnessBundle`
- regime-tagged query assumptions and dynamic lens mixes
- merged live + archive atlas loading when `archive_atlas.json` is present

## How To Run

From `C:\Users\dmitr\Documents\Athena Agent`:

```powershell
python -m self_actualize.runtime.cli "next self prompt: self actualize build full framework"
```

The CLI outputs a full `RoutePacket` JSON object.

To regenerate the source reconciliation artifacts:

```powershell
python -m self_actualize.runtime.reconcile_scan
```

This writes `scan_reconciliation.json` and `scan_reconciliation_report.md`.

To regenerate the archive-backed evidence layer:

```powershell
python "C:\Users\dmitr\.codex\skills\archive-atlas-ingestor\scripts\ingest_archives.py" `
  --root "C:\Users\dmitr\Documents\Athena Agent" `
  --output-atlas "C:\Users\dmitr\Documents\Athena Agent\self_actualize\archive_atlas.json" `
  --output-manifest "C:\Users\dmitr\Documents\Athena Agent\self_actualize\archive_manifest.json"
```

The runtime automatically merges `corpus_atlas.json` and `archive_atlas.json` when both exist.

## Source Reconciliation Status

The historical framework scan is now reconciled against the live workspace:

- `840 / 840` scanned records resolved
- `831` records resolve as exact matches inside ZIP archives
- `9` records resolve as live extracted files under `PoleStarGEMM_Release_v1`

The key result is that the problem is not missing framework lineage. The real bottleneck is archive visibility: major projects like `Athena OS`, `ATLAS FORGE`, and `Q-SHRINK` are preserved in the workspace, but remain mostly outside the current atlas because they live as ZIP-backed sources instead of first-class extracted records.

## Archive Visibility Status

The archive-backed source layer is now indexed:

- `16` ZIP archives scanned
- `2041` archive-entry records generated
- `1706` archive code records made atlas-visible
- runtime evidence search now surfaces archive-backed framework files such as `athena_os/core/integrity.py` and `atlasforge/verify_installation.py`

## Google Docs Search Status

Attempted live search command:

```powershell
.\.venv\Scripts\python.exe docs_search.py manuscript holographic time --max-results 25
```

Result:

- Blocked because OAuth client file is missing: `credentials.json`
- The search code itself is valid and ready once credentials are present

## Integration Map To Existing Folders

1. `FRESH`
   - Keep as manuscript intake and extracted source layer.
2. `MATH`
   - Keep as formal theorem, framework, and algorithm registry.
3. `NERUAL NETWORK`
   - Keep as adaptive engine and benchmark layer.
4. `Trading Bot`
   - Keep as external retrieval (Google Docs) ingestion layer.
5. `self_actualize` (this folder)
   - Runtime contract, orchestration loop, and next-prompt generator.

## Immediate Next Move

Use `next_self_prompt.md` as the controlling prompt text, and run the runtime scaffold on each new objective so every reasoning episode is typed, witness-bearing, and replay-safe.
