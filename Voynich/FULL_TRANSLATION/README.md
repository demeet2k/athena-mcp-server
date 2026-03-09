# Voynich Full Translation Suite

## Entry Points

- `folios/` - one markdown manuscript per folio
- `unified/VOYNICH_FULL_TRANSLATION.md` - accumulating manuscript-order compilation
- `unified/VOYNICH_GIANT_MANUSCRIPT.md` - final packaging target for the complete project
- `unified/VOYNICH_MASTER_MANUSCRIPT.md` - live accumulating master manuscript packaging target
- `sections/` - section-wide ledgers and synthesis files
- `crystals/` - section crystals and the full-manuscript crystal layer
- `metro/VOYNICH_METRO_MAP_WORKING.md` - hidden transit topology across folios and sections
- `manifests/translation_protocol.md` - translation stack and production rules
- `manifests/CORPUS_BUILD_STATUS.md` - current build status and next queue
- `manifests/AUTONOMOUS_CURSOR.md` - live no-stop manuscript cursor
- `manifests/AUTONOMOUS_QUEUE.md` - canonical queue state, recent completions, and upcoming folios
- `manifests/AUTONOMOUS_MASTER_PLAN.md` - full manuscript-order master control plan
- `manifests/ACTIVE_MICRO_PLAN.md` - currently executable micro plan emitted from the master plan
- `manifests/ACTIVE_RUN_TASK_LIST.md` - five-task run-level ouroboros list that must reboot itself before completion
- `manifests/PARALLEL_AGENT_QUEUE.md` - live alpha/beta/gamma folio lanes so the successor and shadow-successor are already staged
- `manifests/AUTONOMOUS_TERMINATION_CONTRACT.md` - stop rule for terminal manuscript completion
- `manifests/NEXT_FOLIO_SELF_PROMPT.md` - regenerated next-folio handoff prompt
- `manifests/VOYNICH_SKILL_WISHLIST.md` - project-specific preflight skill stack and gap analysis
- `manifests/FINAL_MANUSCRIPT_EXECUTION_PLAN.md` - no-stop execution charter through the full final manuscript
- `framework/README.md` - canonical dense folio framework, registries, templates, and bootstrap tooling

## Current Completion

- `f1r` translated
- `f1r` dense multilens atlas translated
- `f1v` translated
- `f1r` authoritative final draft complete
- `f1v` authoritative final draft complete
- `f2r` authoritative final draft complete
- `f2v` authoritative final draft complete
- `f3r` authoritative final draft complete
- `f3v` authoritative final draft complete
- `f4r` authoritative final draft complete
- unified corpus initialized
- live master manuscript target initialized
- section scaffolds initialized
- metro scaffold initialized
- formal translation framework installed
- project-specific Voynich skill stack installed
- crystal file family initialized
- macro-step autonomy engine installed (`187` explicit macro steps)

## Next Queue

- `f004v` final draft
- `f005r` final draft
- continue through Quire A in canonical EVA order
- use the autonomous cursor, active run task list, and next-folio prompt after every completion

## No-Stop Recovery

If a session breaks, rebuild the live no-stop state from disk with:

```powershell
python "C:\Users\dmitr\Documents\Athena Agent\Voynich\FULL_TRANSLATION\framework\scripts\update_autonomous_cursor.py" --sync-from-disk
```
