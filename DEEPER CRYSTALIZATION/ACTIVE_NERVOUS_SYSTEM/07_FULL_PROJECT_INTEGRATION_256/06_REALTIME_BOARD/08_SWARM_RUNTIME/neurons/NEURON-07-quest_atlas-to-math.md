# NEURON-07: quest_atlas → math

**Neuron ID**: `NEURON-07`
**Source Ganglion**: `quest_atlas`
**Target Ganglion**: `math`
**Edge Kind**: `shares_constants`
**Status**: ACTIVE

## Signal

Phi constants and element ring geometry from the quest atlas board kernel share the same mathematical foundation as the PhiSigma60 engine. Pheromone decay uses phi-inverse; reward amplifiers use log-phi; the 15 symmetry cells mirror the 15 masks of the 60-state atlas.

## Data Flow

```
constants.py (PHI, PHI_INV, LN_PHI)
  ↔ phi_sigma_60_engine.py (same constants)

15 symmetry cells (4 poles, 6 bridges, 4 chambers, 1 crown)
  ↔ 15 masks of PhiSigma60
```

## Coupling

- **Structural**: Both systems derive from the same phi-constant family
- **Operational**: Independent execution, shared verification
