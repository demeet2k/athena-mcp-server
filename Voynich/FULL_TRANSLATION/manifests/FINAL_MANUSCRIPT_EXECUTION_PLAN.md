# Final Manuscript Execution Plan

## Mission

This plan governs continuous production from the current state through the completed final-draft Voynich manuscript.

The agent should continue folio by folio without stopping for replanning unless a true blocker appears.

The live queue is canonicalized in:

- `framework/registry/folio_sequence.json`
- `framework/registry/autonomous_master_plan.json`
- `manifests/AUTONOMOUS_QUEUE.md`
- `manifests/AUTONOMOUS_MASTER_PLAN.md`
- `manifests/ACTIVE_MICRO_PLAN.md`
- `manifests/PARALLEL_AGENT_QUEUE.md`

## Two-Level Control Rule

The runtime now operates with a master-plan and micro-plan handshake:

1. the master plan enumerates every canonical folio side, every section milestone, and the terminal completion actions
2. the active micro plan is generated from the master plan for the current folio
3. once the micro plan completes, the cursor updater regenerates the next micro plan from the master plan
4. when no folio work items remain, the runtime emits the terminal completion micro plan and stops

This prevents the loop from depending on ad hoc restatement between folios.

Current macro-plan scale:

- `181` folio steps
- `5` section/crystal completion steps
- `1` terminal manuscript completion step
- `187` total macro steps

## No-Stop Rule

Do not pause between folios for strategic reconsideration.

Move automatically to the next manuscript side once all of the following are true for the current folio:

1. authoritative final-draft folio file exists
2. folio passed confidence audit
3. unified corpus is updated
4. section synthesis is updated
5. section crystal is updated
6. working metro map is updated
7. build status is updated

Only stop if one of these hard blockers occurs:

- the local corpus has no readable transcription witness for the folio
- local sources disagree so strongly that manuscript order or line structure cannot be resolved honestly
- a required local source file is corrupted or unavailable
- the project owner explicitly changes the framework

## Perpetual Motion Rule

The manuscript build should behave like an open reciprocal engine, not a closed loop that waits to be restarted from outside.

After a folio completes, its completion output becomes the intake for the next folio:

1. finished folio = current exhaust
2. corpus roll-up = recovery loop
3. master plan emits the next micro plan
4. next-folio self-prompt = renewed intake
5. next folio execution = immediate continuation

Persistence therefore comes from lawful handoff, not from pretending the loop is self-sustaining without intake.

## Canonical Per-Folio Algorithm

For every folio side, execute this exact sequence.

### Phase 1: Intake

1. Run `voynich-eva-normalizer`.
2. Build stable line ids and full EVA.
3. Preserve damaged glyphs, red markers, title markers, and uncertainty.

### Phase 2: Scaffold

1. Bootstrap the dense folio file from `framework/scripts/bootstrap_dense_folio.py`.
2. Name the authoritative target `folios/F###R_FINAL_DRAFT.md` or `folios/F###V_FINAL_DRAFT.md`.
3. Keep a short pointer file `folios/F###R.md` or `folios/F###V.md` when useful.

### Phase 3: Direct Evidence

1. Fill source stack.
2. Fill reading contract.
3. Fill folio zero claim.
4. Fill core VML machinery.
5. Complete the direct line-by-line literal ledger for every visible line.

### Phase 4: Visual Pass

If the folio is illustrated or diagrammatic:

1. run `voynich-visual-codicologist`
2. add visual grammar
3. bind image evidence back to line ids and labels

If the folio is text-only, state that directly and skip image overreach.

### Phase 5: Multilens Rendering

Populate every canonical lens in order:

1. `AQM`
2. `CUT`
3. `Liminal`
4. `Aetheric`
5. `Chemistry`
6. `Physics`
7. `Quantum Physics`
8. `Wave Mechanics`
9. `Wave Math`
10. `Music Theory and Music Math`
11. `Color and Light`
12. `Geometry`
13. `Number Theory`
14. `Compression`
15. `Hacking Theory`
16. `Game Theory`
17. `Tarot`
18. `Juggling`
19. `Story Writing`
20. `Hero's Journey`

Every formal-math lens must contain true symbolic equations for every line.

### Phase 6: Formal Compilation

1. Run `voynich-equation-compiler`.
2. Build canonical AQM line operators.
3. Build paragraph compositions.
4. Build typed state machine.
5. Build safety invariants.
6. Build cross-lens transport laws.
7. Build the formal folio theorem.

### Phase 7: Synthesis

Complete:

1. direct operational meaning
2. mathematical extraction
3. mythic extraction
4. all-lens zero point
5. dense one-sentence compression

### Phase 8: Audit

Run `voynich-confidence-auditor`.

A folio is not final draft unless:

- all visible lines are present
- all formal-math lenses have explicit equations
- direct and derived evidence are kept separate
- unresolved glyphs remain visible
- the folio theorem composes the actual line order

### Phase 9: Corpus Roll-Up

Run `voynich-corpus-conductor`.

Update:

1. `unified/VOYNICH_FULL_TRANSLATION.md`
2. relevant `sections/` file
3. relevant `crystals/` file
4. `metro/VOYNICH_METRO_MAP_WORKING.md`
5. `manifests/CORPUS_BUILD_STATUS.md`
6. `unified/VOYNICH_MASTER_MANUSCRIPT.md`

Then immediately advance to the next folio side.

### Phase 10: Autonomous Self-Handoff

After every successful folio completion:

1. update `manifests/AUTONOMOUS_CURSOR.md`
2. rewrite `manifests/AUTONOMOUS_QUEUE.md`
3. rewrite `manifests/NEXT_FOLIO_SELF_PROMPT.md`
4. regenerate `manifests/ACTIVE_MICRO_PLAN.md` from the master plan
5. regenerate `manifests/ACTIVE_RUN_TASK_LIST.md` as a five-task ouroboros list for the successor step
6. regenerate `manifests/PARALLEL_AGENT_QUEUE.md` so the successor and shadow-successor lanes are already staged
7. append the authoritative folio to `unified/VOYNICH_MASTER_MANUSCRIPT.md`
8. begin the next folio without waiting for a fresh user prompt

Inside each emitted micro plan:

1. the penultimate micro step performs the macro handoff and emits the next micro plan
2. the final micro step performs successor intake and must not be interpreted as completion

Inside each emitted run task list:

1. tasks 1-3 complete the current folio
2. task 4 rewrites the runtime into the successor state
3. task 5 reads the rewritten successor task list and reboots the cycle before completion can be inferred

### Phase 10b: Recovery And Re-Synchronization

If a session breaks or the cursor drifts from the actual files on disk:

1. rebuild the canonical queue from `eva/EVA TRANSCRIPTION ORIGIONAL.txt` when needed
2. run `framework/scripts/update_autonomous_cursor.py --sync-from-disk`
3. recover:
   - `AUTONOMOUS_CURSOR.md`
   - `AUTONOMOUS_QUEUE.md`
   - `NEXT_FOLIO_SELF_PROMPT.md`
   - `ACTIVE_RUN_TASK_LIST.md`
   - `PARALLEL_AGENT_QUEUE.md`

No manual next-folio guesswork should be required after interruption.

## Naming Rules

### Folio Files

- `folios/F001R_FINAL_DRAFT.md`
- `folios/F001V_FINAL_DRAFT.md`
- continue that pattern through the full corpus

### Section Synthesis Files

Keep using the existing `sections/` files and deepen them after each folio.

### Crystal Files

Keep using:

- `crystals/PLANT_CRYSTAL.md`
- `crystals/ASTROLOGY_CRYSTAL.md`
- `crystals/COSMOLOGY_CRYSTAL.md`
- `crystals/BATH_CRYSTAL.md`
- `crystals/PHARMACEUTICAL_1_CRYSTAL.md`
- `crystals/PHARMACEUTICAL_2_CRYSTAL.md`
- `crystals/VOYNICH_FULL_CRYSTAL.md`

### Final Packaging

The packaging targets are:

- `unified/VOYNICH_GIANT_MANUSCRIPT.md`
- `unified/VOYNICH_MASTER_MANUSCRIPT.md`

## Manuscript Order Rule

Advance in manuscript side order:

`F001R -> F001V -> F002R -> F002V -> ...`

Continue through the extant manuscript while preserving any real gaps or special insertions visible in the local corpus.

## Book-Level Execution Sequence

### Stage 0: Threshold Pair

- `F001R` final draft complete
- `F001V` final draft complete
- threshold pair now feeds directly into `F002R`

### Stage 1: Book I - Plant Crystal Build

Process all remaining Book I folios in manuscript order.

Working range:

- `F002R` through the end of the herbal section

Primary outputs:

- finished Book I folio files
- expanded `sections/FULL_PLANT.md`
- matured `crystals/PLANT_CRYSTAL.md`

Milestone at section completion:

- finalize Plant synthesis
- finalize Plant metro map
- finalize Plant emergent metro map

### Stage 2: Book II - Astrology Crystal Build

Process the astronomical and astrological folios in order.

Primary outputs:

- finished Book II folio files
- expanded `sections/FULL_ASTROLOGY.md`
- matured `crystals/ASTROLOGY_CRYSTAL.md`

Milestone at section completion:

- finalize Astrology synthesis
- finalize Astrology metro map
- finalize Astrology emergent metro map

### Stage 3: Book III - Bath Crystal Build

Process the balneological folios in order.

Primary outputs:

- finished Book III folio files
- expanded `sections/FULL_BATH.md`
- matured `crystals/BATH_CRYSTAL.md`

Milestone at section completion:

- finalize Bath synthesis
- finalize Bath metro map
- finalize Bath emergent metro map

### Stage 4: Book IV - Cosmology Crystal Build

Process the rosette and cosmological folios in order.

Primary outputs:

- finished Book IV folio files
- expanded `sections/FULL_COSMOLOGY.md`
- matured `crystals/COSMOLOGY_CRYSTAL.md`

Milestone at section completion:

- finalize Cosmology synthesis
- finalize Cosmology metro map
- finalize Cosmology emergent metro map

### Stage 5: Book V Part 1 - Pharmaceutical 1 Crystal Build

Process early recipe folios in order up to the Part 1 threshold.

Primary outputs:

- finished early Book V folio files
- expanded `sections/PHARMACEUTICAL_1_FULL.md`
- expanded `sections/PHARMACEUTICAL_1_SYNTHESIS.md`
- matured `crystals/PHARMACEUTICAL_1_CRYSTAL.md`

Milestone at section completion:

- finalize Pharmaceutical 1 synthesis
- finalize Pharmaceutical 1 metro map
- finalize Pharmaceutical 1 emergent metro map

### Stage 6: Book V Part 2 - Pharmaceutical 2 Crystal Build

Process late recipe and terminal curriculum folios in order through the manuscript close.

Primary outputs:

- finished late Book V folio files
- expanded `sections/PHARMACEUTICAL_2_FULL.md`
- expanded `sections/PHARMACEUTICAL_2_SYNTHESIS.md`
- matured `crystals/PHARMACEUTICAL_2_CRYSTAL.md`

Milestone at section completion:

- finalize Pharmaceutical 2 synthesis
- finalize Pharmaceutical 2 metro map
- finalize Pharmaceutical 2 emergent metro map

### Stage 7: Pharmaceutical Join

Complete:

- `sections/PHARMACEUTICAL_1_2_SYNTHESIS.md`

This stage joins:

- bridge tokens
- curricular escalation
- correction logic
- final-recipe closure

### Stage 8: Authorial Closure

After the manuscript body is complete:

1. include the author's final line after `116r`
2. place it in the unified corpus
3. place it in the giant manuscript
4. interpret its relation to the full crystal

### Stage 9: Full Corpus Closure

Complete:

1. `crystals/VOYNICH_FULL_CRYSTAL.md`
2. final full-manuscript synthesis
3. final full metro map
4. final emergent metro map
5. final package into `unified/VOYNICH_GIANT_MANUSCRIPT.md`

## Section Completion Rule

A section is not complete until both of these are true:

1. every folio in that section has an authoritative final-draft file
2. the section synthesis and section crystal both contain:
   - synthesis
   - metro map
   - emergent metro map
   - zero point
   - forward links to adjacent sections

## Full Manuscript Completion Rule

The manuscript is not complete until all of the following exist:

1. authoritative final-draft folio file for every folio side
2. complete section synthesis files
3. complete section crystal files
4. complete `VOYNICH_FULL_CRYSTAL.md`
5. authorial final line after `116r`
6. complete `VOYNICH_GIANT_MANUSCRIPT.md`

## Immediate Cursor

Current cursor:

- completed: `F001V`
- next final-draft target: `F002R`
- after that: continue strictly in manuscript order with autonomous self-handoff

## Standing Instruction

Once a folio is complete, continue automatically to the next folio under this plan and rewrite the live cursor manifests so the next step is already on disk.

Do not stop between folios unless a hard blocker appears.
