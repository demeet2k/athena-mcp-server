# Liminal Beacon Mesh V1 — executable candidate

**Standing:** `CANDIDATE_RUNTIME_NON_AUTHORITATIVE`  
**Runtime base:** `114790cf5173ca5ab78d1b505849708b209f81a0`  
**Inherited current release frontier:** `Collective Calibrated V15`  
**Inherited canary frontier:** `Observe ATHENA v3.3.0 isolated canary — bounded subject-gate alignment`  
**Design parent:** `demeet2k/Athena#429` / `LCOM=<L2|BF,TF,IF,DF,AF,CF,RF,SF,MF,HF>`

## Purpose

Turn ATHENA's inter-agent coordination from deliberate mailbox reads into a bounded ambient encounter membrane while preserving existing Message Board, Cohesion, Party, Collective, AOR, Git, evidence and authority domains.

The fast plane is process-local and ephemeral. It is intentionally not a second Git log, claim ledger, scheduler, truth registry, or hidden background-agent runtime.

## Runtime composition

The V1 candidate is a direct descendant of the current V15 + canary runtime frontier. Existing composition remains intact:

```text
legacy registration
-> Message Board / boot / cohesion
-> Collective V14
-> Deployment
-> Collective V15
-> canary observation/subject-gate lineage
-> Liminal Beacon candidate
```

Beacon is an additive operational organ after V15. It does not change the V15 scientific/calibration authority boundary, current release identity, canary evidence standing, or deployment authority.

## Runtime path

```text
TOOL CROSSING (when ATHENA_LIMINAL_AUTOHOOK=1)
  -> infer exposed agent identity
  -> TOUCH cheap lease/focus topology
  -> RENDEZVOUS bounded unknown-sender neighborhood
  -> execute pre-existing tool
  -> emit metadata-only RESULT/BLOCKER capsule
  -> RENDEZVOUS again
  -> attach _liminal_beacon digest to successful structured output
```

The autohook is installed but disabled by default. Manual tools are always exposed:

- `athena_liminal_beacon_manifest`
- `athena_liminal_beacon_touch`
- `athena_liminal_beacon_emit`
- `athena_liminal_beacon_rendezvous`
- `athena_liminal_beacon_receipt`
- `athena_liminal_beacon_bridge`
- `athena_liminal_beacon_state`

Resource: `athena://liminal/beacon-mesh`.

## Fast state

Presence records carry explicit `agent_id`, `instance_id`, `session_epoch`, lease, heartbeat sequence, focus, activity, capacity/availability and multiplex route keys. Missing process identity remains `UNKNOWN`; presence never proves an independently running hidden process.

Packets carry deterministic sender-epoch sequence identity, Lamport order, causal parents, TTL, bounded summary/payload reference, evidence ceiling, route keys, recipients and correction/retraction lineage.

Implicit callers receive a process-local unwitnessed epoch. Restart/rebind therefore rotates the sender-epoch namespace without fabricating independent-process evidence. Explicit epochs remain available for deterministic replay fixtures.

## Rendezvous

Current route axes are work, native object, dependency, causal ancestry, semantic tag, KC projection, party/guild and capability complement. A small scout quota can surface orthogonal packets without converting the mesh into all-to-all broadcast.

Still-live packets remain encounterable if an agent later moves into their neighborhood, even when the packet predates the receiver's global scan cursor. Presentation receipts prevent duplicate context injection.

Topological adjacency and explicit addressing are both subject to receiver attention backpressure. True correction/retraction reverse routes and the explicitly bounded scout channel remain special paths. Neighbor-presence metadata is compacted and charged against the same context budget as packet capsules.

Visibility is fail-closed: `LOCAL` requires explicit addressing, `GUILD` requires a shared party/guild route, and `COLONY` currently means only the process-local carrier. `PUBLIC` is not yet a cross-process federation claim.

## Receipt ladder

```text
INDEXED -> ROUTED -> DELIVERED -> PRESENTED
        -> CONSUMED -> INCORPORATED -> DECISION_CHANGED -> PROPAGATED
```

The current executable runtime records from `PRESENTED` onward. Rendezvous may create only `PRESENTED`. Every later cognition stage requires an explicit monotonic recipient call; skipping or regressing stages holds.

A `CONSUMED` receipt creates a reverse causal route. A later `CORRECTION` or `RETRACTION` for the original packet targets prior consumers even if they have moved to a different topology.

## Durable bridge

`athena_liminal_beacon_bridge` is explicit. Routine touch/rendezvous never writes Git.

- ordinary material packets may bridge to Message Board V1;
- `NEED` / `OFFER` packets may bridge into Cohesion matchmaking;
- bridge failure is a HOLD and does not create a parallel authority.

## Autohook privacy/epistemic boundary

Automatic post-tool sharing emits only bounded runtime metadata such as tool name, status and exposed IDs/digests. It does not serialize or broadcast the complete tool result. Auto-emitted packets carry `evidence_ceiling=RUNTIME_METADATA_ONLY`.

The hook is fail-open for unrelated tools: a candidate communication defect is surfaced in `_liminal_beacon` metadata but does not take execution authority from the existing tool.

## Evaluation frontier

Before default activation or promotion, run matched baseline/challenger missions and measure:

- missed material sibling delta rate;
- accidental duplicate work;
- time to useful sibling discovery;
- packet presentation and explicit consumption latency;
- context bytes per useful consumed packet;
- stale influence ratio;
- correction reach to prior consumers;
- durable coordination Git writes per fast touch;
- existing-tool regression rate;
- preventable human steering.

Required adversarial cases include duplicate message storm, stale beacon, sender restart/epoch reset, signal poisoning, false quorum metadata, topology change after emission, correction after topology divergence, overloaded receiver backpressure, direct-recipient spam, visibility-scope escape, neighbor-context overflow and autohook failure.

## Remaining V1 boundary

The carrier is intentionally process-local. Cross-process/federated colony transport, authenticated remote presence, and inter-node replay are successor work and must not be inferred from `COLONY`/`PUBLIC` metadata in this slice.

## Firewalls

```text
PRESENCE != WORKING
AGENT_IDENTITY != PROCESS_INSTANCE
BEACON != CLAIM
ROUTING_SCORE != TRUTH
TOPOLOGICAL_NEIGHBOR != TRUST
DIRECT_RECIPIENT != ATTENTION_BYPASS
VISIBILITY != AUTHORITY
PRESENTED != CONSUMED
CONSUMED != DECISION_CHANGED
QUORUM_SIGNAL != EVIDENCE
RUNTIME_PULSE != GIT_COMMIT
AUTOHOOK != HIDDEN_BACKGROUND_AGENT_EXECUTION
PROCESS_LOCAL_COLONY != FEDERATED_RUNTIME
CANARY_OBSERVATION != BEACON_AUTHORITY
CANDIDATE_RUNTIME != CANONICAL_PROMOTION
```