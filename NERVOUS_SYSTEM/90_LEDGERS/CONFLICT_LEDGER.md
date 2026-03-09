# CONFLICT LEDGER

## Purpose
Tracks FAIL-class conflict receipts: contradictions, quarantined atoms, and revocation records.

## Active Conflicts

(none declared yet)

## Conflict Record Schema

| Field | Description |
|-------|-------------|
| Conflict ID | `CF-XXXX` |
| Atoms involved | GlobalAddr list |
| Kind | CONFLICT edge |
| Minimal witness set | Paths proving the contradiction |
| Quarantine status | ACTIVE / RESOLVED / REVOKED |
| Resolution plan | Steps to resolve |
| Resolution date | Date resolved (if applicable) |

## Rules

1. Every FAIL truth class must have a corresponding conflict ledger entry
2. Conflicts cannot be silently suppressed
3. Resolution requires passing through AMBIG and NEAR before reaching OK
4. Quarantined atoms must not be used in downstream synthesis
