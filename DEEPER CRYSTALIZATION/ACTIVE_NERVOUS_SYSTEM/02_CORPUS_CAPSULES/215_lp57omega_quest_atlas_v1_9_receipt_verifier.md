# LP57Ω Quest Atlas v1.9 — Receipt-Chain Verifier and Linter

- Kind: `verification-spec`
- Role tags: `linter, verifier, receipt-chain, quest-atlas`
- Version: `1.9`
- Family: `LP57Ω Quest Engine`

## Purpose

Specifies the receipt-chain verification engine and lint rule set for validating SealedReceiptBundle.v1 instances. Covers 21 lint codes (L001-L021), a required/forbidden field matrix, chain root verification, and sealed bundle digest verification.

---

## 1. Lint Codes

### Structural Lint Rules

| Code  | Severity | Rule |
|-------|----------|------|
| L001  | ERROR    | Missing `schema` field on any receipt object |
| L002  | ERROR    | Invalid `schema` version string (must match `*.v1` pattern) |
| L003  | ERROR    | Missing `digest` field on any chain-linked object |
| L004  | ERROR    | Digest mismatch: recomputed digest does not match stored digest |
| L005  | ERROR    | Broken chain link: `entry[i].prev_digest != entry[i-1].digest` |
| L006  | ERROR    | Genesis entry `prev_digest` is not `SHA-256("GENESIS")` |
| L007  | ERROR    | Empty receipt chain (zero entries) |

### Semantic Lint Rules

| Code  | Severity | Rule |
|-------|----------|------|
| L008  | ERROR    | Quest class mismatch between ClaimPack and ReceiptEntry metadata |
| L009  | ERROR    | Truth gate value not in {OK, NEAR, ZERO, FAIL} |
| L010  | ERROR    | Witness quorum not met for quest class |
| L011  | WARNING  | Witness attestation timestamps out of epoch bounds |
| L012  | ERROR    | ReplayBundle marked deterministic but step hashes are not reproducible |
| L013  | ERROR    | Corridor station references non-existent chapter |
| L014  | WARNING  | Reward exceeds per-capsule clamp (16 * base) |

### Bundle Integrity Rules

| Code  | Severity | Rule |
|-------|----------|------|
| L015  | ERROR    | SealedReceiptBundle `bundle_digest` does not match recomputed value |
| L016  | ERROR    | `chain_root` does not match genesis entry digest |
| L017  | ERROR    | `chain_tip` does not match final entry digest |
| L018  | ERROR    | ReleaseManifest present but quest status is not Published |
| L019  | WARNING  | MIGRATE entry present in a non-migration context |
| L020  | ERROR    | Duplicate `entry_id` within a single receipt chain |
| L021  | WARNING  | Timestamp regression: entry timestamp earlier than predecessor |

---

## 2. Required / Forbidden Field Matrix

### ClaimPack.v1

| Field           | Required | Forbidden When     |
|-----------------|----------|--------------------|
| schema          | YES      | never              |
| claim_id        | YES      | never              |
| quest_id        | YES      | never              |
| agent_id        | YES      | never              |
| quest_class     | YES      | never              |
| element         | YES      | never              |
| corridor        | YES      | never              |
| timestamp       | YES      | never              |
| epoch           | YES      | never              |
| prev_digest     | YES      | never (null OK for genesis) |
| digest          | YES      | never              |

### WitnessBundle.v1

| Field           | Required            | Forbidden When        |
|-----------------|---------------------|-----------------------|
| schema          | YES                 | never                 |
| bundle_id       | YES                 | never                 |
| quest_id        | YES                 | never                 |
| witnesses       | YES (min 1)         | never                 |
| quorum_met      | YES                 | never                 |
| timestamp       | YES                 | never                 |
| prev_digest     | YES                 | never                 |
| digest          | YES                 | never                 |

### WitnessEntry

| Field           | Required | Forbidden When        |
|-----------------|----------|-----------------------|
| agent_id        | YES      | never                 |
| attestation     | YES      | never                 |
| corridor_ref    | YES      | never                 |
| signed_at       | YES      | never                 |
| entry_digest    | YES      | never                 |

### ReplayBundle.v1

| Field           | Required               | Forbidden When        |
|-----------------|------------------------|-----------------------|
| schema          | YES                    | never                 |
| bundle_id       | YES                    | never                 |
| quest_id        | YES                    | never                 |
| replay_steps    | YES (min 1)            | never                 |
| deterministic   | YES                    | never                 |
| timestamp       | YES                    | never                 |
| prev_digest     | YES                    | never                 |
| digest          | YES                    | never                 |

### ReceiptEntry

| Field           | Required | Forbidden When                    |
|-----------------|----------|-----------------------------------|
| entry_id        | YES      | never                             |
| quest_id        | YES      | never                             |
| entry_type      | YES      | never                             |
| payload_ref     | YES      | never                             |
| timestamp       | YES      | never                             |
| epoch           | YES      | never                             |
| prev_digest     | YES      | never                             |
| digest          | YES      | never                             |

### SealedReceiptBundle.v1

| Field              | Required          | Forbidden When              |
|--------------------|-------------------|-----------------------------|
| schema             | YES               | never                       |
| bundle_id          | YES               | never                       |
| quest_id           | YES               | never                       |
| claim_pack         | YES               | never                       |
| witness_bundle     | if Community/Rite | Solo without witnesses      |
| replay_bundle      | if required       | Solo without replay         |
| receipt_chain      | YES (min 1)       | never                       |
| release_manifest   | if Published      | if not Published            |
| sealed_at          | YES               | never                       |
| sealed_epoch       | YES               | never                       |
| chain_root         | YES               | never                       |
| chain_tip          | YES               | never                       |
| bundle_digest      | YES               | never                       |

---

## 3. Chain Root Verification

### Algorithm

```python
def verify_chain_root(bundle: SealedReceiptBundle) -> LintResult:
    chain = bundle.receipt_chain

    # L007: Empty chain
    if len(chain) == 0:
        return LintResult(code="L007", passed=False)

    genesis = chain[0]

    # L006: Genesis prev_digest
    expected_genesis_prev = sha256("GENESIS")
    if genesis.prev_digest != expected_genesis_prev:
        return LintResult(code="L006", passed=False,
            detail=f"Expected {expected_genesis_prev}, got {genesis.prev_digest}")

    # L016: chain_root matches genesis digest
    if bundle.chain_root != genesis.digest:
        return LintResult(code="L016", passed=False,
            detail=f"chain_root={bundle.chain_root}, genesis.digest={genesis.digest}")

    # L004: Verify genesis self-digest
    recomputed = sha256(canonical(genesis, exclude=["digest"]))
    if genesis.digest != recomputed:
        return LintResult(code="L004", passed=False, entry_index=0)

    return LintResult(code="L016", passed=True)
```

### Chain Walk

```python
def verify_chain_links(bundle: SealedReceiptBundle) -> list[LintResult]:
    results = []
    chain = bundle.receipt_chain

    for i in range(1, len(chain)):
        # L005: Chain link integrity
        if chain[i].prev_digest != chain[i-1].digest:
            results.append(LintResult(code="L005", passed=False, entry_index=i))

        # L004: Self-digest verification
        recomputed = sha256(canonical(chain[i], exclude=["digest"]))
        if chain[i].digest != recomputed:
            results.append(LintResult(code="L004", passed=False, entry_index=i))

        # L020: Duplicate entry_id check
        ids_seen = set()
        if chain[i].entry_id in ids_seen:
            results.append(LintResult(code="L020", passed=False, entry_index=i))
        ids_seen.add(chain[i].entry_id)

        # L021: Timestamp regression
        if chain[i].timestamp < chain[i-1].timestamp:
            results.append(LintResult(code="L021", passed=False, entry_index=i))

    # L017: Chain tip
    if chain[-1].digest != bundle.chain_tip:
        results.append(LintResult(code="L017", passed=False))

    return results
```

---

## 4. Sealed Bundle Digest Verification

```python
def verify_bundle_digest(bundle: SealedReceiptBundle) -> LintResult:
    # Recompute bundle digest over entire canonical form
    canonical_bundle = canonical(bundle, exclude=["bundle_digest"])
    recomputed = sha256(canonical_bundle)

    if bundle.bundle_digest != recomputed:
        return LintResult(
            code="L015",
            passed=False,
            detail=f"Expected {recomputed}, got {bundle.bundle_digest}"
        )

    return LintResult(code="L015", passed=True)
```

---

## 5. Full Verification Pipeline

```python
def verify_sealed_bundle(bundle: SealedReceiptBundle) -> VerificationReport:
    report = VerificationReport()

    # Phase 1: Structural checks (L001-L007)
    report.add(check_schema_fields(bundle))        # L001, L002
    report.add(check_digest_fields(bundle))         # L003
    report.add(verify_chain_root(bundle))           # L006, L007, L016
    report.add(verify_chain_links(bundle))          # L004, L005, L020, L021

    # Phase 2: Semantic checks (L008-L014)
    report.add(check_quest_class_consistency(bundle))  # L008
    report.add(check_truth_gate_values(bundle))        # L009
    report.add(check_witness_quorum(bundle))           # L010, L011
    report.add(check_replay_determinism(bundle))       # L012
    report.add(check_corridor_validity(bundle))        # L013
    report.add(check_reward_clamps(bundle))            # L014

    # Phase 3: Bundle integrity (L015-L019)
    report.add(verify_bundle_digest(bundle))           # L015
    report.add(check_release_manifest(bundle))         # L017, L018
    report.add(check_migration_context(bundle))        # L019

    return report
```

---

## 6. LintResult Schema

```typescript
interface LintResult {
  code:        string;      // L001-L021
  passed:      boolean;
  severity:    "ERROR" | "WARNING";
  entry_index: uint | null;
  detail:      string | null;
}

interface VerificationReport {
  bundle_id:    string;
  total_checks: uint;
  passed:       uint;
  failed:       uint;
  warnings:     uint;
  results:      LintResult[];
  verdict:      "PASS" | "FAIL" | "WARN";
}
```

### Verdict Rules

- **PASS**: Zero ERRORs, zero WARNINGs
- **WARN**: Zero ERRORs, one or more WARNINGs
- **FAIL**: One or more ERRORs
