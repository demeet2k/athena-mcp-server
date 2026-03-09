# corpus-atlas-builder

## address
0030

## priority
P0

## lane
manuscript

## description
Build and refresh the canonical manuscript-first atlas across markdown, docx, pdf, txt, code, and archive mirrors.

## triggers
- corpus atlas builder
- ingest this
- bring this into the system
- capture this source

## inputs
- manuscript source paths
- atlas records
- chapter or section context

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
- `C:\Users\dmitr\Documents\Athena Agent\self_actualize\corpus_atlas.json`
- `C:\Users\dmitr\Documents\Athena Agent\self_actualize\DEEPER_SKILLS_CORPUS_SYNTHESIS.md`
- `C:\Users\dmitr\Documents\Athena Agent\ECOSYSTEM\16_CORPUS_ATLAS.md`

## rationale
Atlas construction is the front door to the whole workspace.
