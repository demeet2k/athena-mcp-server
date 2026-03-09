# Voynich Formal Translation Framework

## Purpose

This framework standardizes how every Voynich folio is translated into a dense, line-by-line atlas with:

1. direct evidence
2. literal VML parsing
3. operational English
4. per-lens symbolic renderers
5. cross-lens synthesis
6. a formal folio theorem

The goal is not just to summarize a folio. The goal is to force every folio through the same full contract so the corpus can later be compiled, cross-synthesized, and metro-mapped without format drift.

## Entry Points

- `registry/lenses.json` - canonical ordered lens list and per-line output requirements
- `registry/math_kernel_registry.md` - imported mathematical kernels from the local `MATH` corpus
- `registry/folio_sequence.json` - canonical folio-side order derived from the EVA corpus
- `registry/autonomous_master_plan.json` - full manuscript-order master control ledger with every folio work item and milestone
- `registry/vml_operator_registry.md` - VML token families, operator families, and composition rules
- `schemas/folio_line_schema.json` - machine-readable schema for line records
- `templates/FOLIO_DENSE_TEMPLATE.md` - dense folio markdown contract
- `templates/SECTION_SYNTHESIS_TEMPLATE.md` - section-wide synthesis contract
- `templates/METRO_MAP_TEMPLATE.md` - metro-map build contract
- `scripts/bootstrap_dense_folio.py` - generator for new dense folio files
- `scripts/build_folio_sequence_registry.py` - rebuilds the canonical folio queue from the EVA corpus
- `scripts/build_autonomous_master_plan.py` - rebuilds the master-plan registry, human-readable master plan, and termination contract
- `scripts/update_autonomous_cursor.py` - rewrites the live cursor, live queue, next-folio self-prompt, active micro plan, and active run task list
- `FORMAL_MULTILENS_FRAMEWORK.md` - prose specification of the full system

The autonomy layer is now step-explicit:

- macro plan: one explicit macro step per folio plus synthesis and terminal steps
- micro plan: emitted from the active macro step
- penultimate micro step: hand off to the next macro step
- final micro step: successor intake, not completion
- run task list: five visible tasks whose fifth task reboots the cycle by reading the rewritten successor list

## Canonical Output Order

Every dense folio file should follow this order:

1. purpose
2. source stack
3. reading contract
4. folio zero claim
5. full EVA
6. core VML machinery
7. direct line-by-line literal ledger
8. multilens translation atlas
9. direct operational meaning
10. mathematical extraction
11. mythic extraction
12. all-lens zero point
13. dense one-sentence compression
14. imported kernel equations
15. typed state machine
16. line operators
17. formal safety invariants
18. conjugacy law
19. concrete transport targets
20. formal restatement of the folio theorem

## Lens Classes

The framework uses three lens classes:

- `direct evidence` - EVA, codicology, visual grammar, literal VML, operational English
- `formal math` - AQM, CUT, Liminal, Aetheric, Chemistry, Physics, Quantum Physics, Wave Mechanics, Wave Math, Music Theory and Music Math, Color and Light, Geometry, Number Theory, Compression, Hacking Theory, Game Theory
- `mythic` - Tarot, Juggling, Story Writing, Hero's Journey

Every `formal math` lens must contain explicit equations. Prose is explanatory only and cannot replace the equation layer.

## Quick Start

Generate a new dense folio scaffold:

```powershell
python "C:\Users\dmitr\Documents\Athena Agent\Voynich\FULL_TRANSLATION\framework\scripts\bootstrap_dense_folio.py" `
  --folio F002R `
  --book "Book I" `
  --section-role "Herbal / materia medica" `
  --line-ids-file "C:\path\to\f2r_line_ids.txt" `
  --eva-file "C:\path\to\f2r_eva.txt" `
  --direct-source "NEW/working/VML_RIGOROUS_RETRANSCRIPTION_QUIRES_ABCDEFG.md" `
  --derived-source "FULL_TRANSLATION/MATH/AQM - LM - N+7/AQM MASTER TOME.docx" `
  --output "C:\Users\dmitr\Documents\Athena Agent\Voynich\FULL_TRANSLATION\folios\F002R_DENSE_MULTILENS.md"
```

Minimal usage:

```powershell
python "C:\Users\dmitr\Documents\Athena Agent\Voynich\FULL_TRANSLATION\framework\scripts\bootstrap_dense_folio.py" `
  --folio F002R `
  --book "Book I" `
  --output "C:\Users\dmitr\Documents\Athena Agent\Voynich\FULL_TRANSLATION\folios\F002R_DENSE_MULTILENS.md"
```

## Build Rules

- Keep direct evidence and derived renderers visibly separate.
- Preserve damaged glyphs and uncertainty markers.
- Treat AQM as the primary formal source lens unless local evidence forces otherwise.
- Transport into other mathematical lenses by explicit conjugacy or typed state translation.
- Treat mythic and narrative lenses as controlled projections, not as direct folio evidence.
- Update `unified/VOYNICH_FULL_TRANSLATION.md` only after the folio file is complete.
- Update the relevant section synthesis file and metro file after each finished folio.
- Rewrite `manifests/AUTONOMOUS_CURSOR.md` and `manifests/NEXT_FOLIO_SELF_PROMPT.md` after each finished folio.
- Rewrite `manifests/AUTONOMOUS_QUEUE.md` after each finished folio.
- Rewrite `manifests/ACTIVE_RUN_TASK_LIST.md` after each finished folio.
- Rewrite `manifests/PARALLEL_AGENT_QUEUE.md` after each finished folio so successor lanes stay staged.
- Append the finished folio to `unified/VOYNICH_MASTER_MANUSCRIPT.md` after each authoritative completion.

## No-Stop Runtime Recovery

The no-stop loop now has four persistent runtime artifacts:

- `manifests/AUTONOMOUS_CURSOR.md`
- `manifests/AUTONOMOUS_QUEUE.md`
- `manifests/NEXT_FOLIO_SELF_PROMPT.md`
- `manifests/ACTIVE_RUN_TASK_LIST.md`
- `manifests/PARALLEL_AGENT_QUEUE.md`

If the session is interrupted, rebuild all three from disk with:

```powershell
python "C:\Users\dmitr\Documents\Athena Agent\Voynich\FULL_TRANSLATION\framework\scripts\update_autonomous_cursor.py" --sync-from-disk
```

## Immediate Use

The framework is designed so the next upgrade pass can do two things quickly:

1. rebuild existing folios with stricter symbolic line entries
2. generate future folios with the full dense contract already in place
