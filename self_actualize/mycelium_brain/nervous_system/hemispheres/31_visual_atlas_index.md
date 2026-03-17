# Visual Atlas Index

Docs gate: `BLOCKED`

## Summary

- records: `502`
- visual atlas nodes: `544`
- visual atlas edges: `4321`
- fixed atlas pages: `8`
- family shards: `10`
- anchor shards: `16`
- target-system shards: `11`
- record-locator shards: `16`

## Main Surfaces

| Page | Page ID | Type |
| --- | --- | --- |
| [Corpus Overview Map](32_corpus_overview_map.md) | VA-OVERVIEW | overview |
| [MATH Route Topology Atlas](33_math_route_topology_atlas.md) | VA-HEM-MATH | hemisphere |
| [MYTH Route Topology Atlas](34_myth_route_topology_atlas.md) | VA-HEM-MYTH | hemisphere |
| [Anchor Crosswalk Atlas](35_anchor_crosswalk_atlas.md) | VA-ANCHOR | anchor index |
| [Target-System Atlas](36_target_system_atlas.md) | VA-TARGET-SYSTEM | target system index |
| [Record Locator Index](37_record_locator_index.md) | VA-LOCATOR | record locator index |
| [Atlas Coverage Receipt](38_atlas_coverage_receipt.md) | VA-COVERAGE | coverage |

## Machine Outputs

- `C:\Users\dmitr\Documents\Athena Agent\self_actualize\myth_math_hemisphere_visual_atlas_node_registry.json`
- `C:\Users\dmitr\Documents\Athena Agent\self_actualize\myth_math_hemisphere_visual_atlas_edge_registry.json`
- `C:\Users\dmitr\Documents\Athena Agent\self_actualize\myth_math_hemisphere_visual_atlas_page_registry.json`
- `C:\Users\dmitr\Documents\Athena Agent\self_actualize\myth_math_hemisphere_visual_atlas_record_locator_registry.json`
- `C:\Users\dmitr\Documents\Athena Agent\self_actualize\myth_math_hemisphere_visual_atlas_manifest.json`

## Commands

```powershell
python -m self_actualize.runtime.query_myth_math_hemisphere_brain record --record-id <record_id>
python -m self_actualize.runtime.compose_myth_math_hemisphere_routes record --record-id <record_id>
python -m self_actualize.runtime.synthesize_myth_math_hemisphere_routes record --record-id <record_id>
```
