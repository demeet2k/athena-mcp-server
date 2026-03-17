# Astrological Scheduler Registry

Date: `2026-03-13`
Status: `ACTIVE V2 / ASTRO-LATTICE + HSIGMA`
Truth policy: `structural calendar layer, not scientific proof`
Docs gate: `BLOCKED`

## Purpose

This manifest defines the Global Command Center astrological scheduler matrix for Athena.

The scheduler law is:

- all pantheon lanes are interfaces onto one shared structural phase kernel
- each lane keeps its native cycle law and also emits one shared 12-seat projection
- inverse and 90-degree rotated families are derived overlays, not always-on lanes
- Avatar agents are nexus-only and spawn only when convergence thresholds are met
- scheduler packets remain advisory timing inputs and never outrank witness class, replay value, blocker honesty, or boundary safety
- HSigma is an additive shared-nexus overlay and does not replace the lane activation law

## AstroTimingPacket Interface

Every scheduler lane keeps the same 10 mandatory fields:

- `system_id`
- `clock_mode`
- `native_cycle`
- `current_gate`
- `next_transition`
- `action_bias`
- `cautions`
- `suggested_frontier`
- `handoff_target`
- `blocker_truth`

The packet now also publishes these support fields:

- `shared12_seat`
- `native_gate`
- `projection_witness`
- `variant_set`
- `role_weight_vector`
- `resolution_band`
- `nexus_score`
- `liminal_tag`
- `lane_state`
- `spawn_envelope_seed`
- `hsigma_current_byte`
- `hsigma_row_ids`
- `hsigma_weight`
- `hsigma_hidden_pressure`
- `hsigma_cell_class`
- `hsigma_restart_seed`

## Scheduler Table

| System | Automation id | Cadence | Native cycle | Packet path | Lane state |
|---|---|---|---|---|---|
| western_solar12 | `astro-western-wheel` | hourly structural zodiac wheel | `Solar12 / 4x3 archetype wheel` | `NERVOUS_SYSTEM/90_LEDGERS/astrological_schedulers/western_solar12_packet.md` | `ACTIVE_ANCHOR` |
| planetary_office | `astro-planetary-office` | hourly planetary office | `PlanetaryHour / Septenary / weekday ruler` | `NERVOUS_SYSTEM/90_LEDGERS/astrological_schedulers/planetary_office_packet.md` | `ACTIVE_ANCHOR` |
| chinese_cycle | `astro-chinese-cycle` | two-hour Chinese double-hour lane | `Wu Xing + DoubleHour + Chinese60` | `NERVOUS_SYSTEM/90_LEDGERS/astrological_schedulers/chinese_cycle_packet.md` | `ACTIVE_ANCHOR` |
| vedic_lunar | `astro-vedic-lunar` | daily lunar office | `Lunar27/28/18` | `NERVOUS_SYSTEM/90_LEDGERS/astrological_schedulers/vedic_lunar_packet.md` | `ACTIVE_ANCHOR` |
| mayan_calendar | `astro-mayan-calendar` | daily Mayan calendar office | `Tzolkin260 + Haab365` | `NERVOUS_SYSTEM/90_LEDGERS/astrological_schedulers/mayan_calendar_packet.md` | `ACTIVE_ROTATION` |
| decan_office | `astro-decan-office` | 12-hour decan office | `Decan36 / night-watch / MUL.APIN` | `NERVOUS_SYSTEM/90_LEDGERS/astrological_schedulers/decan_office_packet.md` | `ACTIVE_ROTATION` |
| egyptian_kheper | `astro-egyptian-kheper` | hourly Duat12 lane with Decan36 support | `Duat12 / Kheper / Ma'at / Decan36` | `NERVOUS_SYSTEM/90_LEDGERS/astrological_schedulers/egyptian_kheper_packet.md` | `COMPILED_SHADOW` |
| norse_rune_yggdrasil | `astro-norse-rune-yggdrasil` | daily Rune24 lane with House12 projection | `Rune24 / House12 / Yggdrasil9` | `NERVOUS_SYSTEM/90_LEDGERS/astrological_schedulers/norse_rune_yggdrasil_packet.md` | `COMPILED_SHADOW` |

## Honesty

- structural calendar logic only
- no live astronomical ephemeris
- no live Google Docs claims while `Trading Bot/credentials.json` or `Trading Bot/token.json` are missing
