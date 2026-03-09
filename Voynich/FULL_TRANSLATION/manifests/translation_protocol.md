# Voynich Full Translation Protocol

## Scope

This directory is the production workspace for the systematic full translation of MS 408.

The autonomous no-stop production charter lives in:

- `manifests/FINAL_MANUSCRIPT_EXECUTION_PLAN.md`
- `manifests/AUTONOMOUS_MASTER_PLAN.md`
- `manifests/ACTIVE_MICRO_PLAN.md`
- `manifests/ACTIVE_RUN_TASK_LIST.md`
- `manifests/PARALLEL_AGENT_QUEUE.md`
- `manifests/AUTONOMOUS_TERMINATION_CONTRACT.md`
- `manifests/AUTONOMOUS_QUEUE.md`

The current macro plan is explicit and finite:

- `187` total macro steps
- `181` folio steps
- `6` non-folio synthesis / terminal steps

The working rule is:

1. One folio = one primary markdown file.
2. One folio file must contain the full EVA transcription first.
3. Each folio file must then be rendered through every codified translation layer currently grounded in the local corpus.
4. The unified corpus file must accumulate the folios in manuscript order.
5. Section synthesis files must track the deeper cross-folio structures as the folios land.
6. The metro map must be built from the finished whole, but early working lines can be tracked during production.
7. The live queue must be recoverable from disk without manual next-folio guessing.
8. The active micro plan must always be generated from the master plan rather than improvised from scratch.
9. The penultimate micro step must hand off to the next macro step before the final micro step performs successor intake.
10. The active run task list must always contain five tasks, and Task 5 must reboot the cycle by reading the rewritten successor task list before completion can be inferred.

## Parallel Folio Lanes

Current parallel lanes:

- `Agent F001R`: apparatus specification, codicology, safety-chain, non-illustrated page logic.
- `Agent F001V`: first illustrated plant page, dangerous extraction, reflux loop, toxic pharmacology.

Future rule:

- One lane per folio.
- Each lane must end with a finished folio file before its output is folded into the unified manuscript.

## Codified Translation Stack

These are the renderer layers implemented in this production pass.

### Direct local evidence layers

These are grounded directly in folio-specific material already present in the workspace:

1. `EVA transcription`
2. `Codicology and page grammar`
3. `Visual grammar`
4. `VML decomposition`
5. `Operational English`
6. `Alchemical / pharmaceutical reading`
7. `Workflow position in the five-book manuscript`
8. `Cross-reference and confidence notes`

### Derived corpus renderer layers

These are systematic renderers derived from corpus-wide compiler claims visible in the local workspace, especially the broader language/backend framing summarized in `NEW/VOYNICH JAZZ.docx`, the manuscript-brain routing texts in `FRESH/_extracted`, and the VML operator grammar in `NEW/working`.

These layers are allowed, but they must be labeled as derived renderers rather than directly attested folio-native outputs:

1. `Universal process IR`
2. `Chemistry-native renderer`
3. `Mathematical / systems-native renderer`
4. `Music-native renderer`
5. `Light / spectrum-native renderer`

## Honesty Rule

Every folio file must clearly distinguish between:

- `directly supported by local folio sources`
- `derived from corpus-wide codified translation rules`
- `open questions / unresolved readings`

## Production Tree

- `folios/` individual folio manuscripts
- `unified/` accumulating full manuscript
- `sections/` deep synthesis layers by major manuscript domain
- `crystals/` section crystals with synthesis, metro map, and emergent metro map
- `metro/` explicit and emergent transit maps
- `manifests/` protocol and queue material
- `framework/` canonical dense folio framework, lens registry, operator registry, schema, templates, and bootstrap script

## Preflight Skill Layer

Before scaling translation work, use the project-specific skill stack documented in `manifests/VOYNICH_SKILL_WISHLIST.md`.

Current preflight skills:

- `voynich-meta-observer`
- `voynich-eva-normalizer`
- `voynich-visual-codicologist`
- `voynich-equation-compiler`
- `voynich-confidence-auditor`
- `voynich-corpus-conductor`

Current Chapter 11 runtime skills:

- `voynich-autopoietic-continuator`
- `voynich-boundary-ledger`
- `voynich-reciprocal-rollup`
- `voynich-contradiction-preserver`

Use these runtime skills during long corpus execution:

1. `voynich-autopoietic-continuator` after each folio release
2. `voynich-boundary-ledger` when a stop appears
3. `voynich-reciprocal-rollup` when propagating folio outputs upward
4. `voynich-contradiction-preserver` when multiple admissible readings must coexist honestly

## Formal Multilens Rule

The dense folio standard is now governed by the framework in `framework/`.

Mandatory constraints:

1. Every canonical formal-math lens must contain explicit equations.
2. The per-line lens stack must follow `framework/registry/lenses.json`.
3. Operator naming and line composition should follow `framework/registry/vml_operator_registry.md`.
4. Imported mathematical kernels should be drawn from `framework/registry/math_kernel_registry.md`.
5. New dense folio files should be bootstrapped from `framework/scripts/bootstrap_dense_folio.py` or from the matching template.

## Book Structure

- `Book I`: Herbal / materia medica (`f1r-f57r`)
- `Book II`: Astronomical and astrological (`f58r-f73v`)
- `Book III`: Bath / balneological (`f75r-f84v`)
- `Book IV`: Cosmological / rosette (`f85r-f86v`)
- `Book V`: Pharmaceutical / formulary (`f87r-f116v`)

## Deep Synthesis Files

The section files in `sections/` are the long-form syntheses requested for:

- full plant
- full astrology
- full cosmology
- full bath
- pharmaceutical 1
- pharmaceutical 1 synthesis
- pharmaceutical 2
- pharmaceutical 2 synthesis
- pharmaceutical 1/2 synthesis

## Crystal Files

Each major manuscript domain now also has a crystal file in `crystals/`.

Each crystal must contain:

1. synthesis
2. metro map
3. emergent metro map
4. zero point
5. growth queue

## Current Production Status

- `F001R`: authoritative final draft complete
- `F001V`: authoritative final draft complete
- `F002R`: authoritative final draft complete
- `F002V`: authoritative final draft complete
- `F001R` dense atlas: upgraded with formal math overlay from the `MATH` corpus
- unified corpus: initialized with the first four authoritative folios
- canonical folio queue: derived from EVA and recoverable from disk
- section synthesis files: scaffolded
- metro map: scaffolded, preliminary early lines only
- framework: installed for future dense folio production
