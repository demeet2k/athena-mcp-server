# governance-audit

## description
Review proposed ecosystem changes for invariants, migration impact, and truth-safe execution.

## triggers
- audit this change
- governance review
- check invariants
- migration risk
- approve this

## inputs
- changed files
- proposal summary
- claimed risk class

## outputs
- approval recommendation
- risk classification
- required follow-up actions

## procedure
1. Inspect changed artifacts.
2. Check addressing, truth lattice, and migration invariants.
3. Validate whether witnesses and replay steps are preserved.
4. Return approval, AMBIG, or FAIL with reasons.

## validation
- all changes have lineage
- no silent breaking change
- migration edges exist if semantics changed

## failure modes
- missing migration notes: FAIL
- undocumented behavior change: AMBIG
- invariant break: FAIL

## references
- `C:\Users\dmitr\Documents\Athena Agent\ECOSYSTEM\08_GOVERNANCE_PROTOCOL.md`
- `C:\Users\dmitr\Documents\Athena Agent\ECOSYSTEM\09_VERSIONING_AND_MIGRATION.md`
