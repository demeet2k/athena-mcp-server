# FAMILY AQM QPHI Live Root

Date: `2026-03-09`
Truth: `NEAR`
Owner family: `MATH`

## Role

This family surface pins the promoted AQM + Q-PHI live root as a reusable `MATH` code body rather than a dark archive artifact.

## Source lineage

- archive:
  `MATH/FINAL FORM/COMPLETE TOMES/AQM - LM - N+7/Q-Phi  Optimization/aqm_kernel_qphi_planet9_v0.2.2_final.zip`
- live root:
  `MATH/LIVE_PROMOTED/aqm_kernel_qphi_planet9`
- manifest:
  `MATH/LIVE_PROMOTED/aqm_kernel_qphi_planet9/PROMOTION_MANIFEST.md`

## Witness

- `python -m aqm.cli demo`
- `python -m aqm.apps.planet9.cli --help`

Both commands pass locally from the promoted live root.

## Current front

The replay-safe runtime lane is now landed:

- verifier:
  `self_actualize/runtime/verify_aqm_runtime_lane.py`
- machine witness:
  `self_actualize/aqm_runtime_lane.json`
- active-front manifest:
  `nervous_system/manifests/AQM_ACTIVE_FRONT.md`

The next lawful step is no longer runtime binding.
It is to reuse this lane across Hall, family, and runtime surfaces without reopening
archive drift.
