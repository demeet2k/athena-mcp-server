---
node_id: "EC01"
body_id: "EC"
source_path: "C:\\Users\\dmitr\\Documents\\Athena Agent\\ECOSYSTEM\\05_MYCELIUM_ROUTING.md"
source_hash: "995ca41f95494916ee9710093754ebbdb912a4e166cd16f64c6d22d1d199acae"
witness_class: "source"
duplicate_group: ""
word_count: 332
coordinate_4d: [1, 2, 3, 3]
dominant_role: "ecosystem routing and tissue transport law"
line_membership: ["Transit", "Governance"]
hub_rank: 2
tissue_class: "nerves"
tesseract_address: "O1-C2-T3-G3::nerves::H2::Transit+Governance"
source_size_bytes: 1898
extracted_at: "2026-03-12T10:57:40-07:00"
---

# EC01 Mycelium Routing

## Overview

- body: `EC`
- witness_class: `source`
- duplicate_group: `none`
- tissue_class: `nerves`
- tesseract_address: `O1-C2-T3-G3::nerves::H2::Transit+Governance`
- role: `ecosystem routing and tissue transport law`
- lines: `Transit, Governance`

## Motif Ledger

| axis | score | evidence_anchor | reach |
| --- | --- | --- | --- |
| Origin | 1 | P0001 | latent |
| Crystal | 2 | P0003 | latent |
| Transit | 3 | P0001 | active |
| Governance | 3 | P0010 | active |

- secondary_motifs: `corridor, quarantine, replay`

## Direct Witness Claims

- The witness surface opens with `# MYCELIUM ROUTING - ADDRESSING AND CORRIDOR TRUTH` and preserves paragraph-level anchors beginning at `P0001`.
- The dominant motif field concentrates around `corridor, quarantine, replay` and supports the declared role `ecosystem routing and tissue transport law`.
- The strongest axis witnesses currently anchor at Origin=P0001, Crystal=P0003, Transit=P0001, Governance=P0010.

## Derived Synthesis Claims

- EC01 functions as `ecosystem_route` tissue and routes primarily through `Transit, Governance`.
- The tesseract coordinate `1, 2, 3, 3` places this node in a `nerves` role inside the mycelium.
- This node remains `source` evidence while all downstream edits should occur on the mirror only.

## Contradiction Table

| topic | status | related | note |
| --- | --- | --- | --- |
| route proliferation vs replay stability | reconcile | F10 | transport density must still close back into a replayable carrier |
| speed vs witness burden | preserve | F09 | fast transit cannot erase governance proof load |

## Anchor Index

- `P0001` # MYCELIUM ROUTING - ADDRESSING AND CORRIDOR TRUTH


## Inbound Corridors

| source | relation | weight | priority | lines | anchors | contradiction |
| --- | --- | --- | --- | --- | --- | --- |
| EC01 | recurse | 0.880 | primary | Transit,Governance | P0001,P0001 | none |
| EC02 | route | 0.730 | secondary | Governance | P0005,P0001 | none |
| F01 | govern | 0.660 | secondary | Governance | P0004,P0001 | none |
| F02 | govern | 0.640 | tertiary | Governance | P0002,P0001 | none |
| F03 | govern | 0.660 | secondary | Governance | P0005,P0001 | none |
| F04 | constrain | 0.580 | tertiary | Origin,Crystal | P0052,P0012 | none |
| F05 | govern | 0.740 | secondary | Transit,Governance | P0005,P0001 | none |
| F06 | govern | 0.740 | secondary | Transit,Governance | P0005,P0001 | none |
| F07 | govern | 0.740 | secondary | Transit,Governance | P0002,P0001 | none |
| F08 | govern | 0.740 | secondary | Transit,Governance | P0012,P0001 | none |
| F09 | govern | 0.740 | secondary | Transit,Governance | P0003,P0001 | none |
| F10 | govern | 0.640 | tertiary | Governance | P0003,P0001 | none |

## Outbound Corridors

| target | relation | weight | priority | lines | anchors | contradiction |
| --- | --- | --- | --- | --- | --- | --- |
| EC01 | recurse | 0.880 | primary | Transit,Governance | P0001,P0001 | none |
| EC02 | repair | 0.730 | secondary | Governance | P0010,P0009 | none |

## Witness Surface

[P0001] # MYCELIUM ROUTING - ADDRESSING AND CORRIDOR TRUTH
[P0002] ## 1. Canonical Addressing
[P0003] Definition 1.1 (Local Address). - Chapter atom: ChXX<dddd>.LensFacet.Atom - Appendix atom: AppX.LensFacet.Atom
[P0004] Lens in {S, F, C, R}, Facet in {1,2,3,4}, Atom in {a,b,c,d}.
[P0005] Definition 1.2 (Base-4 Station Code). Let omega = XX - 1, then <dddd> = base4(omega) padded to 4 digits.
[P0006] Definition 1.3 (Global Address). GlobalAddr := Ms<mmmm>::LocalAddr
[P0007] Definition 1.4 (Ms Derivation). Ms<mmmm> = base4_4(h(T)) where h(T) = sum_{i=1..n} i * ord(T_i) mod 256.
[P0008] ## 2. Mycelium Graph
[P0009] Definition 2.1 (Graph). G = (V, E) with V = {GlobalAddr} and E = {LinkEdge}.
[P0010] Definition 2.2 (LinkEdge Schema). Edge record: - EdgeID - Kind in {REF, EQUIV, MIGRATE, DUAL, GEN, INST, IMPL, PROOF, CONFLICT} - Src, Dst - Scope - Corridor - WitnessPtr - ReplayPtr - Payload - EdgeVer
[P0011] ## 3. Corridor Truth Lattice
[P0012] Truth classes: - OK: witnessed and replay-verified - NEAR: bounded approximation + residual ledger - AMBIG: candidate set + evidence plan - FAIL: quarantine + conflict receipts
[P0013] ## 4. Deterministic Router v2
[P0014] LensBase: - S -> AppC - F -> AppE - C -> AppI - R -> AppM
[P0015] FacetBase: - 1 -> AppA - 2 -> AppB - 3 -> AppH - 4 -> AppM
[P0016] ArcHub(alpha): - 0 -> AppA - 1 -> AppC - 2 -> AppE - 3 -> AppF - 4 -> AppG - 5 -> AppN - 6 -> AppP
[P0017] Mandatory signature Sigma = {AppA, AppI, AppM}.
[P0018] Truth overlay: - NEAR -> +AppJ - AMBIG -> +AppL - FAIL -> +AppK - OK -> +AppO (publish only)
[P0019] Hub cap: at most 6 hubs.
[P0020] ## 5. Route Planning Algorithm
[P0021] Algorithm 5.1 (RoutePlan). Input: LocalAddr, truth class 1. Parse Lens, Facet, Atom, chapter index. 2. Compute alpha if chapter. 3. T = LensBase U FacetBase U ArcHub. 4. Enforce Sigma. 5. Add truth overlay. 6. Enforce hub cap and order hubs deterministically. 7. Output route list and obligations.
[P0022] ## 6. Status
[P0023] This routing layer makes every knowledge atom navigable with deterministic obligations.
