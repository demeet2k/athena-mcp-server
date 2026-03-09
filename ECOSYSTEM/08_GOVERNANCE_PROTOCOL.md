# GOVERNANCE PROTOCOL

## 1. Roles

- Steward: owns coherence and long-term direction
- Maintainer: implements changes
- Reviewer: validates mathematical and operational correctness
- Auditor: ensures traceability and compliance

## 2. Change Proposal Workflow

1. Proposal drafted with rationale, scope, and risk.
2. Review for correctness and corridor classification.
3. Test and validation results attached.
4. Approval and merge into registry.

## 3. Decision Rules

- Low risk: maintainer + reviewer approval
- Medium risk: steward + reviewer approval
- High risk: steward + reviewer + auditor approval

## 4. Governance Invariants

- Address grammar is stable.
- Truth lattice definitions are stable.
- Migration must be explicit and replayable.

## 5. Conflict Resolution

- If ambiguous, return AMBIG with an evidence plan.
- If unverifiable, return FAIL with quarantine receipts.

## 6. Status
This protocol governs all modifications to the ecosystem.
