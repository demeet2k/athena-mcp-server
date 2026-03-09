# Archive Promotion Protocol

Use this protocol when a high-yield framework is trapped inside a ZIP-backed archive and needs to become a live, editable source tree without losing lineage.

## Goal

Promote one archive-backed framework into a canonical live tree that future agents can read, edit, validate, and route without repeatedly unpacking the archive by hand.

## Preconditions

1. Confirm the current highest-yield archive candidate from the build queue.
2. Confirm the live Docs gate status if the promotion is in service of a manuscript front.
3. Record the source archive path and intended live destination before extraction.

## Promotion Steps

1. Choose the smallest archive that unlocks the largest downstream surface.
2. Inspect the archive structure and identify:
   - entry files
   - code roots
   - docs roots
   - assets that must stay adjacent
3. Define the canonical live destination.
4. Extract without mutating or deleting the source archive.
5. Write a manifest that binds:
   - source archive
   - extraction date
   - promoted live root
   - any skipped files
   - any rename or normalization decisions
6. Refresh the atlas or equivalent search surface if the live root changes the searchable body.
7. Write a receipt and queue update so another agent can immediately reuse the new tree.

## Required Writeback

Every archive promotion should leave behind:

- a live tree
- a manifest or receipt
- an updated queue or index
- a route-ledger entry if runtime was used to validate the front

## Failure Law

If promotion would create ambiguous lineage, naming collisions, or an unclear live root:

1. do not perform a destructive extraction;
2. record the ambiguity;
3. leave a narrower proposal artifact instead of a bad promotion.
