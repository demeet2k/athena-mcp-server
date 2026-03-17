# How To Use The Realtime Swarm Board

## Primary Commands

```powershell
python -m self_actualize.runtime.command_membrane_runtime_entrypoint_v2 build
python -m self_actualize.runtime.command_membrane_runtime_entrypoint_v2 watch --interval 2.0
python -m self_actualize.runtime.command_membrane_runtime_entrypoint_v2 emit "ATHENA/READ ME.txt" --change-type modified
python -m self_actualize.runtime.command_membrane_runtime_entrypoint_v2 route EVT-20260313-0001
python -m self_actualize.runtime.command_membrane_runtime_entrypoint_v2 claim EVT-20260313-0001 --lease-ms 1200
python -m self_actualize.runtime.command_membrane_runtime_entrypoint_v2 commit EVT-20260313-0001 --result success
python -m self_actualize.runtime.command_membrane_runtime_entrypoint_v2 reinforce EVT-20260313-0001 --result success --latency-score 0.94
python -m self_actualize.runtime.command_membrane_runtime_entrypoint_v2 status
python -m self_actualize.runtime.swarm_board build
python -m self_actualize.runtime.swarm_board note --agent codex --front "archive promotion" --message "Investigating archive-backed framework landing zone"
python -m self_actualize.runtime.swarm_board claim --agent codex --front "archive promotion" --level framework --output-target "MATH extracted tree" --receipt "receipt pending" --status active --message "Claiming archive promotion front"
```

## Operating Rule

1. Run the COMMAND membrane watcher first for `GLOBAL COMMAND`, then refresh the board.
2. Read `03_CLAIMS/00_ACTIVE_CLAIMS.md`, `07_TENSOR/01_FAMILY_TENSOR_FIELD.md`, `07_TENSOR/05_ARCHETYPE_GRID.md`, and `08_SWARM_RUNTIME/manifests/ACTIVE_RUN.md`.
3. Treat `GLOBAL COMMAND` as a sensory membrane: `detect -> encode -> route -> claim -> commit -> reinforce`.
4. Use manual frontier claims only for non-command board work.
5. Leave at least one note or claim card before going deep.
6. Make sure every serious front has a family owner, rail, packet class, truth class, contraction target, archetype cell, cluster, and truth leaf.
7. Land a receipt or change the claim status when the artifact is done.
8. Update the next self prompt so the loop restarts from the beginning.

## No-Duplication Rule

If a frontier is already `active`, take a validation or receipt role unless the owner has explicitly handed it off.

## COMMAND Law

The canonical routing policy is `goal+salience+pheromone+coord+capability+load`, claim mode is `first-lease`, `Sigma` remains `AppA/AppI/AppM`, and the hub budget remains `<= 6`.
