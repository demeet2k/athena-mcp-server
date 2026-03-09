# chapter-map-ledger

## address
0122

## priority
P1

## lane
manuscript

## description
Map chapter, appendix, arc, and station relationships across the routed manuscript bodies into one durable ledger.

## triggers
- chapter map ledger
- route this
- map the dependencies
- where does this belong

## inputs
- manuscript source paths
- atlas records
- chapter or section context

## outputs
- decision ledger entry
- status receipt
- next obligation list

## procedure
1. Parse the active objective and source surfaces.
2. Compute the most lawful route or dependency ordering.
3. Preserve any unresolved ambiguity instead of forcing collapse.
4. Emit the route artifact and the next recommended move.

## validation
- status and obligations are explicit
- downstream users can replay the decision basis

## failure modes
- If multiple routes compete, keep the shortlist instead of forcing one path.
- If the route depends on missing evidence, surface the dependency as a blocker.

## references
- `C:\Users\dmitr\Documents\Athena Agent\MYCELIUM_TOME_PART1.md`
- `C:\Users\dmitr\Documents\Athena Agent\DEEPER CRYSTALIZATION\_build\nervous_system\00_NERVOUS_SYSTEM_MAP.md`

## rationale
The chapter and metro structure is strong but still distributed across many files.
