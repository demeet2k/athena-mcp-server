# Knowledge Fabric Schema

Date: `2026-03-13`
Derivation version: `2026-03-12.phase4-fabric-v1`
Command: `python -m self_actualize.runtime.derive_knowledge_fabric`

## Equation

`KnowledgeFabric = StorageOntology + FabricRecordAtlas + ShortcutIndex + TraversalEngine + BridgeGraph + ReplayReceipts + HumanMaps`

## Core Interfaces

- `StorageZone`: `zone_id`, `zone_name`, `purpose`, `authority_surface`, `witness_floor`, `canonical_paths`, `artifact_classes`, `query_methods`
- `FabricRecord`: `record_id`, `relative_path`, `root_id`, `root_name`, `family_id`, `surface_class`, `storage_zone`, `witness_class`, `truth_role`, `authority_rank`, `semantic_role`, `query_tags`, `freshness`, `proof_state`, `replay_class`
- `FabricEdge`: `source_record`, `target_record`, `edge_kind`, `bridge_reason`, `weight`, `witness_basis`
- `ShortcutPlan`: `shortcut_id`, `intent_class`, `entry_filters`, `preferred_zones`, `preferred_surface_classes`, `ranking_stack`, `stop_condition`
- `ExplorationPacket`: `query_intent`, `seed_records`, `traversal_mode`, `budget`, `shortcut_chain`, `visited_zones`, `result_class`

## Deterministic Filter Order

`authority -> witness -> zone -> surface class -> root -> family -> tags`

Weighted ranking only begins after deterministic filtering.

## Storage Zones

| Zone | Purpose | Authority Surface | Witness Floor |
| --- | --- | --- | --- |
| Cortex | canonical law, publishable overview matter, and live source corpus bodies | C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\00_INDEX.md | indexed |
| RuntimeMirror | live runtime mirrors, generated json artifacts, and executable routing surfaces | C:\Users\dmitr\Documents\Athena Agent\self_actualize\mycelium_brain\nervous_system\00_active_nervous_system_index.md | generated |
| GovernanceMirror | reusable governance doctrine mirrored outside the canonical cortex | C:\Users\dmitr\Documents\Athena Agent\ECOSYSTEM\NERVOUS_SYSTEM\README.md | indexed |
| DeepRoot | live deeper cross-synthesis basis, matrix, symmetry, metro, and appendix control | C:\Users\dmitr\Documents\Athena Agent\self_actualize\mycelium_brain\dynamic_neural_network\14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK\README.md | indexed |
| CorpusAtlas | the primary indexed record substrate for the live workspace | C:\Users\dmitr\Documents\Athena Agent\self_actualize\corpus_atlas.json | indexed |
| ArchiveAtlas | archive-backed indexed reserve implementation substrate | C:\Users\dmitr\Documents\Athena Agent\self_actualize\archive_atlas.json | archive |
| BoardScope | realtime coordination slice and board-visible witness surfaces | C:\Users\dmitr\Documents\Athena Agent\DEEPER CRYSTALIZATION\ACTIVE_NERVOUS_SYSTEM\07_FULL_PROJECT_INTEGRATION_256\06_REALTIME_BOARD\00_STATUS\00_BOARD_STATUS.md | board |
| PromotedSlice | the bronze promoted nervous-system slice and its declared witness surfaces | C:\Users\dmitr\Documents\Athena Agent\DEEPER CRYSTALIZATION\_build\nervous_system\manifests\STATE_HEADER.md | promoted |
| CapsuleLayer | canonical domain contractions that explain large roots through stable summaries | C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\50_CORPUS_CAPSULES\INDEX.md | indexed |
| GraphLayer | neurons, synapses, bridges, and explicit edge-bearing topology | C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\90_LEDGERS\NEURON_LIBRARY.md | indexed |
| ReceiptLineage | receipts, writebacks, promotion traces, and continuity proof | C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\90_LEDGERS\22_SELF_LINEAGE_LEDGER.md | generated |
| ReserveQuarantine | honest storage for sparse, blocked, contradictory, or reserve surfaces | C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\95_MANIFESTS\ROOT_BASIS_MAP.md | physical |

## Authority And Witness Registry

| Authority | Zone | Rank | Witness Floor |
| --- | --- | --- | --- |
| AUTH-Z01 | Cortex | 5 | indexed |
| AUTH-Z02 | RuntimeMirror | 4 | generated |
| AUTH-Z03 | GovernanceMirror | 3 | indexed |
| AUTH-Z04 | DeepRoot | 4 | indexed |
| AUTH-Z05 | CorpusAtlas | 3 | indexed |
| AUTH-Z06 | ArchiveAtlas | 3 | archive |
| AUTH-Z07 | BoardScope | 2 | board |
| AUTH-Z08 | PromotedSlice | 2 | promoted |
| AUTH-Z09 | CapsuleLayer | 4 | indexed |
| AUTH-Z10 | GraphLayer | 4 | indexed |
| AUTH-Z11 | ReceiptLineage | 3 | generated |
| AUTH-Z12 | ReserveQuarantine | 1 | physical |
