# Prop Channel Algebra Receipt

- Generated: `2026-03-09T20:31:39.127816+00:00`
- Command: `python -m self_actualize.runtime.derive_prop_channel_algebra`
- Verdict: `OK`

## Proved Structure

- prop families: `5`
- VTG monitoring modes: `5`
- station: `<0100>`
- selection law: `Channel* = argmax[(BW(C) * Match(C, message)) / (Risk(C) * (1 + DR_C))]`

## Bandwidth Ladder

- `ring`: `0.618`
- `poi`: `0.618`
- `ball`: `1.0`
- `club`: `1.618`
- `staff`: `2.618`

## Why This Matters

- the chapter now exists as a typed schema the local runtime can cite
- prop metaphors are converted into explicit channel classes with risk, bandwidth, and recovery profiles
- the next implementation frontier is to bind actual agent handoffs and board coordination surfaces to these channel types
