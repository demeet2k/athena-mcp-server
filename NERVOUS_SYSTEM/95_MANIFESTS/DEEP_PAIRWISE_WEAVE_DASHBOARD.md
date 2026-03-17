# DEEP PAIRWISE WEAVE DASHBOARD

Date: `2026-03-13`
Truth: `OK`
Docs gate: `blocked-by-missing-credentials`

## Counts

| Measure | Count |
| --- | --- |
| deep_pairwise_families | 6 |
| deep_pairwise_packets | 18 |
| deep_pairwise_slices | 18 |
| promoted_weaves | 6 |

## Metro law

- primary metro level: `Level 3`
- transit spine: `GCW -> GCZ`
- appendix `Q` mandatory: `True`

## Verifiers

| Verifier | Truth |
| --- | --- |
| aqm_runtime_lane | OK |
| atlasforge_runtime_lane | OK |
| runtime_waist | OK |

## Restart seed

`source-pair replay -> GCW-GCZ transit -> target-pair writeback -> verify -> seed-next-pair`
