# witness-bundle-assembler

## address
2010

## priority
P0

## lane
runtime

## description
Assemble route evidence, source excerpts, lineage pointers, and replay hooks into one packet-level witness bundle.

## triggers
- witness bundle assembler
- ingest this
- bring this into the system
- capture this source

## inputs
- runtime contracts
- route packets
- ledger or profile data

## outputs
- witness-bearing artifact
- source linkage
- replay note

## procedure
1. Identify the correct source surface and its current boundaries.
2. Capture the highest-yield evidence without hiding extraction limits.
3. Normalize the result into the target Athena schema.
4. Emit the resulting artifact together with lineage and next gaps.

## validation
- artifact cites real source paths or live-memory provenance
- lineage is preserved without silent rewrite

## failure modes
- If the source cannot be fully extracted, keep metadata and log the limit.
- If the source boundary is unclear, record the ambiguity before proceeding.

## references
- `C:\Users\dmitr\Documents\Athena Agent\self_actualize\runtime\contracts.py`
- `C:\Users\dmitr\Documents\Athena Agent\self_actualize\runtime\engine.py`

## rationale
The runtime contracts exist, but the reusable assembly layer is still thin.
