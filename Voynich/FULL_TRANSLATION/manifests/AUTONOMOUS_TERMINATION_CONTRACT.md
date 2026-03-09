# Autonomous Termination Contract

The autonomous manuscript runtime terminates only when both conditions are true:

1. there is no remaining macro step in `framework/registry/autonomous_master_plan.json`
2. every terminal completion action below is complete

## Terminal Completion Actions

- finalize every section synthesis crystal with synthesis, metro map, and emergent metro map
- finalize crystals/VOYNICH_FULL_CRYSTAL.md
- append the author's final line after 116r
- finalize unified/VOYNICH_MASTER_MANUSCRIPT.md
- finalize unified/VOYNICH_GIANT_MANUSCRIPT.md
- write terminal completion state into manifests/ACTIVE_MICRO_PLAN.md
- stop the agent when no master-plan steps remain

## Stop Rule

The terminal micro plan must hand off into terminal-complete state on its penultimate step, then the final micro step reads that terminal state and stops only because no successor macro step exists.
