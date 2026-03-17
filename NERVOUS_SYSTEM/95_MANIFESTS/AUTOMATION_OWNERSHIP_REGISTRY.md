# Automation Ownership Registry

Date: `2026-03-13`
Docs gate: `BLOCKED`
Rule: `one frontier family -> one active owner lane`

## Canonical Meta Lanes

| Automation id | Role | Cadence | Owned family | Allowed writeback surfaces | Status |
| --- | --- | --- | --- | --- | --- |
| `guildmaster-loop` | intake governor | hourly | Hall/Temple/queue/restart synchronization | Hall quest board, Hall change feed, requests board, Temple state, queue, restart, receipt | `ACTIVE` |
| `corpus-weave` | integration governor | hourly | atlas refresh, family ranking, neglected-bridge integration | atlas JSON and summary, queue/manifests, receipt, one inbox item | `ACTIVE` |
| `qshrink-shiva` | compression governor | every 4 hours | QSHRINK contraction and stale-residue compression | QSHRINK active-front surfaces, Hall sharpening, queue/restart, receipt | `ACTIVE` |
| `athena-weave-scan` | expansion governor | every 12 hours | neglected body or archive-root expansion | one report, one Hall sharpening candidate, one Temple law-pressure candidate, one queue candidate | `ACTIVE` |
| `high-priest-totality` | closure governor | every 24 hours | 24-hour whole-organism contraction | one totality report, Hall/Temple/queue order refresh, next-day frontier stack | `ACTIVE` |

## Packet-Only Scheduler Lanes

| Automation id | Native law | Writeback scope | Status |
| --- | --- | --- | --- |
| `astro-western-wheel` | `Solar12 / 4x3 archetype wheel` | packet file only | `ACTIVE` |
| `astro-planetary-office` | `PlanetaryHour / Septenary / weekday ruler` | packet file only | `ACTIVE` |
| `astro-chinese-cycle` | `Wu Xing + DoubleHour + Chinese60` | packet file only | `ACTIVE` |
| `astro-vedic-lunar` | `Lunar27/28/18` | packet file only | `ACTIVE` |
| `astro-mayan-calendar` | `Tzolkin260 + Haab365` | packet file only | `ACTIVE` |
| `astro-decan-office` | `Decan36 / night-watch / MUL.APIN` | packet file only | `ACTIVE` |

## Duplicate-Control Set

These lanes remain paused and explicitly deprecated while the canonical owners above stay active:

- `corpus-weave-2`
- `corpus-weave-scan`
- `corpus-weave-scan-2`
- `corpus-weave-scan-3`
- `corpus-weave-scan-4`
- `corpus-weave-scan-5`
- `corpus-weave-scan-6`
- `corpus-weaver`
- `corpus-weaver-2`

## No-Shadow-Owner Rule

1. A frontier family may have one active owner lane only.
2. Non-owner lanes may cite the frontier, but they may not mutate its canonical writeback surfaces.
3. If a lane needs to act outside its owned family, it must emit a repair or escalation request instead of silently taking authority.
