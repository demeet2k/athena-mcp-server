# Exploration Packet Runbook

Date: `2026-03-13`
Derivation version: `2026-03-12.phase4-fabric-v1`

## Traversal Modes

- `direct lookup`: exact or near-exact authoritative retrieval
- `bounded neighborhood`: browse one zone or one family without exploding scope
- `bridge walk`: cross a small number of zones or interfaces
- `metro walk`: follow higher-yield transit surfaces across the fabric
- `regeneration path`: move from seed surfaces toward writeback targets
- `audit sweep`: prefer risk and drift surfaces rather than high-authority summaries

## Example Packets

| Packet | Intent | Traversal Mode | Visited Zones | Result | Route Summary |
| --- | --- | --- | --- | --- | --- |
| KFP-001 | locate | direct lookup | CapsuleLayer, Cortex, GraphLayer | answer | ANSWER through Cortex using GRAND CENTRAL STATION AND BILATERAL HEMISPHERES -> GRAND CENTRAL STATION METRO MAP -> Grand Central Station Schema |
| KFP-002 | browse | bounded neighborhood | DeepRoot | answer | ANSWER through DeepRoot using The Holographic Manuscript Brain -> The Holographic Manuscript Brain -> The Holographic Manuscript Brain -> Self-Routing Meta-Framework -> The Holographic Manuscript Brain -> Quantum Computing on Standard Hardware |
| KFP-003 | compare | bridge walk | Cortex | answer | ANSWER through Cortex using GRAND CENTRAL STATION AND BILATERAL HEMISPHERES -> Phase 3 Self-Hosting Kernel -> GRAND CENTRAL STATION METRO MAP |
| KFP-004 | synthesize | metro walk | Cortex, GraphLayer, RuntimeMirror | answer | ANSWER through Cortex, GraphLayer using Phase 4 Knowledge Fabric -> Knowledge Fabric Schema -> Knowledge Fabric Dashboard |
| KFP-005 | audit | audit sweep | Cortex | answer | ANSWER through Cortex using DOCS GATE VERIFIER -> GATE STATUS -> # Live Docs Gate Status |
| KFP-006 | repair | bridge walk |  | abstain | No lawful witness-bearing route resolved; abstain and widen through fallback zones or stronger witnesses. |
| KFP-007 | regenerate | regeneration path | Cortex, RuntimeMirror | answer | ANSWER through Cortex using Phase 3 Self-Hosting Kernel -> Phase 4 Knowledge Fabric -> Self-Hosting Kernel Schema |
| KFP-008 | publish | regeneration path | Cortex | answer | ANSWER through Cortex using Phase 4 Knowledge Fabric -> Knowledge Fabric Schema -> Knowledge Fabric Dashboard |
