# NEURON-06: quest_atlas → self_actualize

**Neuron ID**: `NEURON-06`
**Source Ganglion**: `quest_atlas`
**Target Ganglion**: `self_actualize`
**Edge Kind**: `feeds`
**Status**: ACTIVE

## Signal

Board kernel output (guild boards, temple boards, settlement capsules) feeds into the self-actualization loop as concrete work items with scored priorities and verified receipts.

## Data Flow

```
quest_atlas.emit_orbit_boards()
  → guild_board (scored, queued)
  → temple_board (scored, queued)
    → self_actualize picks highest-scored entries
    → executes quests
    → settlement produces PoPhiXCapsules
    → receipts chain into SealedReceiptBundles
```

## Coupling

- **Weak**: Board output is advisory; self_actualize retains execution autonomy
- **Strong**: Receipt chain must close before next orbit advances
