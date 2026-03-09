# TRUTH LATTICE

## 1. The Corridor Truth Lattice T

Truth is not boolean. The nervous system uses a four-valued lattice:

```
T = {OK, NEAR, AMBIG, FAIL}
```

### 1.1 Non-Negotiable Law

**ABSTAIN > GUESS**

No atom, capsule, edge, or neuron may be promoted to a higher truth class without explicit witness evidence. Fabricating certainty to fill a gap is a system failure.

## 2. Truth Class Definitions

### 2.1 OK

- **Meaning**: Witnessed + replay-verified closure within corridor budgets.
- **Requirements**:
  - `WitnessPtr` points to concrete evidence artifact
  - `ReplayPtr` provides deterministic re-check recipe
  - Both verified within declared budget constraints
- **Obligations**: None remaining. May be published.
- **Routing overlay**: No additional hubs (or +AppO for publishing intent)

### 2.2 NEAR

- **Meaning**: Bounded approximation with known residual.
- **Requirements**:
  - Residual ledger entry specifying what is missing
  - Obligations list for upgrade path to OK
  - Explicit budget for the approximation bound
- **Obligations**: Residual must be tracked in `90_LEDGERS/OBLIGATIONS_LEDGER.md`
- **Routing overlay**: +AppJ (Residual Ledgers hub)

### 2.3 AMBIG

- **Meaning**: Underdetermined. Multiple candidates, no single winner.
- **Requirements**:
  - Candidate set must be listed (not suppressed)
  - Evidence plan specifying how to resolve
  - No guessing — AMBIG is the correct class when evidence is insufficient
- **Obligations**: Evidence plan must be tracked. Promotion requires new evidence.
- **Routing overlay**: +AppL (Evidence Promotion hub)

### 2.4 FAIL

- **Meaning**: Illegal, unverifiable, or contradictory.
- **Requirements**:
  - Quarantine receipts documenting the failure
  - Conflict packet with minimal witness set proving the failure
  - No silent suppression — FAIL must be visible
- **Obligations**: Must be recorded in `90_LEDGERS/CONFLICT_LEDGER.md`
- **Routing overlay**: +AppK (Quarantine hub)

## 3. Promotion Rules

```
FAIL → AMBIG:  requires conflict resolution + new evidence plan
AMBIG → NEAR:  requires candidate reduction + bounded approximation
NEAR → OK:     requires residual closure + replay verification
```

No class may skip levels. `FAIL → OK` requires passing through both AMBIG and NEAR.

## 4. Demotion Rules

```
OK → NEAR:     if replay fails or budget is exceeded
OK → FAIL:     if witness is invalidated or contradiction found
NEAR → AMBIG:  if residual grows beyond bound
NEAR → FAIL:   if contradiction found in approximation
```

Demotions are recorded in `90_LEDGERS/PROMOTION_LEDGER.md` with timestamped receipts.

## 5. Default Truth Class

- New atoms: `AMBIG`
- New capsules: `AMBIG`
- New edges: `AMBIG`
- New neurons: `AMBIG`

Everything starts underdetermined and earns its truth class through evidence.
