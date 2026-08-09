# Liminal Beacon Shadow V1 — no-injection operational observer

Standing: **candidate / shadow-observation only**  
Frozen contract: public issue #332  
Parent integration: `df74f7388cdb43c36cfdeeff684724b73fdfc117`  
Parent master: `d8bb4cc6e2e6861eeb7141dc52a2efcea252ff36`

## Purpose

Measure the installed Liminal Beacon V1.1 communication membrane at MCP tool crossings without delivering Beacon capsules into model/agent context and without changing the underlying domain-tool result.

The shadow is opt-in with `ATHENA_LIMINAL_SHADOW=1`. Default is OFF. If `ATHENA_LIMINAL_AUTOHOOK` is also active, shadow enters `HOLD_AUTOHOOK_ACTIVE`; a shadow measurement is not mixed with actual autohook treatment.

## Architecture

`LSH=<PARENT,MODE,PROJECTION,WPR,WCR,OUT,OVERHEAD,FILTER,RESERVE,SEMANTIC,ISOLATION,STANDING>`

The observer owns an isolated process-local Beacon source carrier. Each crossing creates a disposable projection of that carrier and seeds it with a separate WOULD_PRESENT receipt/cursor ledger. The *actual installed V1.1* `auto_before_tool` / `auto_after_tool` logic runs only on the projection.

After simulation, only producer-side state is copied back: presence, packets, route index, sender sequence, event clock and Lamport clock. Projection receipts and cursors are never copied into the source carrier. They are translated to the observer's separate WOULD_PRESENT ledger solely to reproduce duplicate suppression on later projections.

The live/manual Beacon carrier (`_liminal_beacon_mesh_runtime_v1`) is never created or mutated by shadow execution. If one already exists, its normalized carrier digest is recorded before and after the crossing; a change is an isolation violation.

## Output membrane

The shadow wrapper does not add `_liminal_beacon`, `_shadow`, capsules, or telemetry to a domain tool result. It hashes the completed MCP result before and after post-observation. Any mismatch is an invariant HOLD. Telemetry is available only through:

- `athena_liminal_beacon_shadow_status`
- `athena://liminal/beacon-shadow`
- the namespaced manifest marker.

Records contain bounded metadata: tool/agent identifiers, output digests, measured shadow latency, would-present counts/bytes/classes, filter counts, reserve use, semantic-envelope state, and isolation counters. Full domain-tool results are never stored.

## Firewalls

- `SHADOW != DELIVERY`
- `SHADOW != PRESENTED`
- `WOULD_PRESENT != PRESENTED`
- `SHADOW != CONSUMED`
- `SHADOW != INCORPORATED`
- `SHADOW != AUTHORITY`
- `SHADOW != EVIDENCE`
- `SHADOW_PACKET != DOMAIN_OUTPUT`
- `SHADOW_CARRIER != LIVE_BEACON_CARRIER`
- `SHADOW_STATE != HIDDEN_PROCESS_PROOF`
- `SHADOW_PASS != DEFAULT_ACTIVATION`
- `SHADOW_PASS != CANONICAL_PROMOTION`
- `UNKNOWN != ZERO`

## What a green test means

A green mechanism suite proves the no-injection observer obeys the frozen local contract under tested fixtures. It does not prove latency acceptability, useful real-world routing, hidden concurrency, independent replication, default activation readiness, merge authority, deployment cutover, or canonical promotion.

The first operational crossing sample must be frozen separately before results and is descriptive: output mismatch, receipts/cursors/Git-write deltas, latency, bytes, filtering, reserve use, and semantic HOLDs must be observed rather than predicted.
