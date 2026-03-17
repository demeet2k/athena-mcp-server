# LP57Ω Quest Atlas v1.8 — Sealed Receipt Bundle Format

- Kind: `schema-specification`
- Role tags: `receipts, bundles, cryptographic-chain, quest-atlas`
- Version: `1.8`
- Family: `LP57Ω Quest Engine`

## Purpose

Defines the canonical receipt bundle format for the Quest Atlas. All quest lifecycle events are captured as chain-linked receipt entries with SHA-256 digests, enabling tamper-evident audit trails from claim through publication.

---

## 1. ClaimPack.v1

The initial receipt generated when an agent claims a quest.

```typescript
interface ClaimPack_v1 {
  schema:        "ClaimPack.v1";
  claim_id:      string;          // UUID v4
  quest_id:      string;          // Quest identifier
  agent_id:      string;          // Claiming agent
  quest_class:   QuestClass;      // Solo | Community | TempleRite | Storm
  element:       Element4;        // Fire | Water | Earth | Air
  corridor:      Coord12[];       // Ordered corridor stations
  timestamp:     ISO8601;         // Claim time
  epoch:         uint;            // Current epoch number
  prev_digest:   string | null;   // null for genesis claim
  digest:        string;          // SHA-256(canonical(this))
}
```

### Digest Computation

```
digest = SHA-256(
  claim_id || quest_id || agent_id || quest_class ||
  element || corridor_canonical || timestamp || epoch ||
  prev_digest
)
```

The `corridor_canonical` is the sorted, pipe-delimited corridor list.

---

## 2. WitnessBundle.v1

Collects witness attestations for a quest. Required for Community and TempleRite quests.

```typescript
interface WitnessBundle_v1 {
  schema:         "WitnessBundle.v1";
  bundle_id:      string;           // UUID v4
  quest_id:       string;
  witnesses:      WitnessEntry[];   // min 2 for Community, min 1 for Solo
  quorum_met:     boolean;
  timestamp:      ISO8601;
  prev_digest:    string;           // Links to prior receipt
  digest:         string;           // SHA-256(canonical(this))
}

interface WitnessEntry {
  agent_id:       string;
  attestation:    Truth4;           // OK | NEAR | ZERO | FAIL
  corridor_ref:   Coord12;         // Station witnessed
  signed_at:      ISO8601;
  entry_digest:   string;          // SHA-256 of this entry
}
```

### Quorum Rules

| Quest Class | Minimum Witnesses | Attestation Threshold |
|-------------|------------------|-----------------------|
| Solo        | 1 (self)         | OK or NEAR            |
| Community   | 2                | Majority OK           |
| TempleRite  | 2 + certifier    | Unanimous OK or NEAR  |
| Storm       | 1 per coalition  | Majority OK           |

---

## 3. ReplayBundle.v1

Captures the full replay trace for reproducibility verification.

```typescript
interface ReplayBundle_v1 {
  schema:         "ReplayBundle.v1";
  bundle_id:      string;
  quest_id:       string;
  replay_steps:   ReplayStep[];
  deterministic:  boolean;         // true if replay reproduces identical output
  timestamp:      ISO8601;
  prev_digest:    string;
  digest:         string;
}

interface ReplayStep {
  step_index:     uint;
  station:        Coord12;
  input_hash:     string;          // SHA-256 of step input
  output_hash:    string;          // SHA-256 of step output
  duration_ms:    uint;
  truth_gate:     Truth4;
}
```

### Determinism Check

A replay is deterministic if and only if:
```
∀ step ∈ replay_steps:
  SHA-256(step.input) → step.output_hash is reproducible
```

---

## 4. ReceiptEntry

The atomic unit of the receipt chain. Every lifecycle event produces one ReceiptEntry.

```typescript
interface ReceiptEntry {
  entry_id:       string;          // UUID v4
  quest_id:       string;
  entry_type:     ReceiptType;     // CLAIM | WITNESS | REPLAY | SEAL | PUBLISH | REPAIR | MIGRATE
  payload_ref:    string;          // Reference to ClaimPack, WitnessBundle, etc.
  timestamp:      ISO8601;
  epoch:          uint;
  prev_digest:    string;          // Previous entry's digest (chain link)
  digest:         string;          // SHA-256(canonical(this))
}

enum ReceiptType {
  CLAIM    = "CLAIM",
  WITNESS  = "WITNESS",
  REPLAY   = "REPLAY",
  SEAL     = "SEAL",
  PUBLISH  = "PUBLISH",
  REPAIR   = "REPAIR",
  MIGRATE  = "MIGRATE",
  CERTIFY  = "CERTIFY",
  STORM    = "STORM"
}
```

### Chain Integrity

Each ReceiptEntry's `prev_digest` must equal the `digest` of the immediately preceding entry in the chain. The genesis entry has `prev_digest = SHA-256("GENESIS")`.

---

## 5. ReceiptRegistry (JointAtlas.v1)

The top-level registry that indexes all receipt chains across quests.

```typescript
interface ReceiptRegistry_JointAtlas_v1 {
  schema:          "JointAtlas.v1";
  registry_id:     string;
  quest_chains:    Map<string, ReceiptChain>;  // quest_id → chain
  total_entries:   uint;
  total_quests:    uint;
  last_updated:    ISO8601;
  root_digest:     string;         // Merkle root of all chain tips
}

interface ReceiptChain {
  quest_id:        string;
  genesis_digest:  string;         // First entry digest
  tip_digest:      string;         // Latest entry digest
  chain_length:    uint;
  entries:         ReceiptEntry[];
  sealed:          boolean;
}
```

### Merkle Root Computation

```
root_digest = MerkleRoot(
  sort_by_quest_id(
    all_chains.map(c => c.tip_digest)
  )
)
```

Binary Merkle tree with SHA-256 at each node. Odd leaves are promoted.

---

## 6. ReleaseManifest.v1

Generated when a quest transitions to Published state.

```typescript
interface ReleaseManifest_v1 {
  schema:          "ReleaseManifest.v1";
  manifest_id:     string;
  quest_id:        string;
  quest_class:     QuestClass;
  truth_gate:      Truth4;
  chain_length:    uint;
  genesis_digest:  string;
  tip_digest:      string;
  reward_summary:  RewardSummary;
  published_at:    ISO8601;
  published_epoch: uint;
  manifest_digest: string;        // SHA-256(canonical(this))
}

interface RewardSummary {
  base_reward:     number;
  truth_factor:    number;        // γ value
  quality_factor:  number;
  community_mult:  number;        // 1 + β*N
  total_reward:    number;
}
```

---

## 7. SealedReceiptBundle.v1

The final, immutable package containing the complete receipt chain and all referenced bundles.

```typescript
interface SealedReceiptBundle_v1 {
  schema:          "SealedReceiptBundle.v1";
  bundle_id:       string;
  quest_id:        string;
  claim_pack:      ClaimPack_v1;
  witness_bundle:  WitnessBundle_v1 | null;
  replay_bundle:   ReplayBundle_v1 | null;
  receipt_chain:   ReceiptEntry[];
  release_manifest: ReleaseManifest_v1 | null;
  sealed_at:       ISO8601;
  sealed_epoch:    uint;
  chain_root:      string;         // SHA-256 of genesis
  chain_tip:       string;         // SHA-256 of final entry
  bundle_digest:   string;         // SHA-256(canonical(entire bundle))
}
```

### Sealing Rules

1. Once sealed, no entries may be appended (except MIGRATE entries during policy migration)
2. The `bundle_digest` covers the entire canonical serialization
3. Any mutation invalidates the `bundle_digest`
4. Verification: recompute chain from genesis, compare tip and bundle digests

---

## Chain Digest Verification Algorithm

```python
def verify_chain(bundle: SealedReceiptBundle_v1) -> bool:
    entries = bundle.receipt_chain
    if len(entries) == 0:
        return False

    # Verify genesis
    if entries[0].prev_digest != sha256("GENESIS"):
        return False

    # Verify chain links
    for i in range(1, len(entries)):
        if entries[i].prev_digest != entries[i-1].digest:
            return False

    # Verify each entry's self-digest
    for entry in entries:
        expected = sha256(canonical(entry, exclude=["digest"]))
        if entry.digest != expected:
            return False

    # Verify tip matches
    if entries[-1].digest != bundle.chain_tip:
        return False

    return True
```

---

## Canonical Serialization

All digest computations use deterministic canonical serialization:

1. Keys sorted lexicographically
2. No whitespace in JSON
3. Numbers as decimal (no scientific notation)
4. Strings UTF-8 encoded
5. Null values included as `null`
6. Arrays preserve order
