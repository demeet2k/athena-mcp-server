# How Athena Thinks Through The Fabric

The fabric does not begin from a whole-corpus sweep by default.
It begins from a shortcut, then uses deterministic filters before weighted ranking.

## Shared Filter Order

`authority -> witness -> zone -> surface class -> root -> family -> tags`

## Shortcut Lexicon

| Shortcut | Intent | Preferred Zones | Ranking Stack | Stop Condition |
| --- | --- | --- | --- | --- |
| Authoritative Locate | locate | Cortex, RuntimeMirror, DeepRoot, CorpusAtlas | authority, witness, proof, text_match, freshness, replay, zone_priority | first top witness-bearing authoritative match |
| Zone Browse | browse | Cortex, DeepRoot, RuntimeMirror, CapsuleLayer | zone_priority, authority, witness, freshness, tag_overlap, replay | bounded neighborhood reached |
| Paired Compare | compare | Cortex, DeepRoot, GraphLayer, RuntimeMirror | authority, witness, proof, tag_overlap, freshness, replay | paired closure or contradiction preserved |
| Cross-Surface Synthesize | synthesize | Cortex, DeepRoot, RuntimeMirror, CapsuleLayer | authority, witness, proof, freshness, replay, tag_overlap, zone_priority | sufficient witnessed synthesis reached |
| Drift Audit | audit | ReceiptLineage, GraphLayer, RuntimeMirror, ReserveQuarantine | proof, freshness, cost, zone_priority, tag_overlap | highest-risk surfaces surfaced |
| Repair Corridor | repair | RuntimeMirror, ReceiptLineage, ReserveQuarantine, GraphLayer | cost, proof, freshness, tag_overlap, replay | next-front route selected |
| Regeneration Path | regenerate | Cortex, RuntimeMirror, ReceiptLineage | authority, witness, replay, freshness, zone_priority, tag_overlap | mapped regeneration route found |
| Publication Return | publish | Cortex, RuntimeMirror, GovernanceMirror, ReceiptLineage | authority, witness, proof, replay, freshness, zone_priority | cortex-runtime-receipt closure reached |
