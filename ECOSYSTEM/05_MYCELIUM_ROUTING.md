# MYCELIUM ROUTING - ADDRESSING AND CORRIDOR TRUTH

## 1. Canonical Addressing

Definition 1.1 (Local Address).
- Chapter atom: ChXX<dddd>.LensFacet.Atom
- Appendix atom: AppX.LensFacet.Atom

Lens in {S, F, C, R}, Facet in {1,2,3,4}, Atom in {a,b,c,d}.

Definition 1.2 (Base-4 Station Code).
Let omega = XX - 1, then <dddd> = base4(omega) padded to 4 digits.

Definition 1.3 (Global Address).
GlobalAddr := Ms<mmmm>::LocalAddr

Definition 1.4 (Ms Derivation).
Ms<mmmm> = base4_4(h(T)) where h(T) = sum_{i=1..n} i * ord(T_i) mod 256.

## 2. Mycelium Graph

Definition 2.1 (Graph).
G = (V, E) with V = {GlobalAddr} and E = {LinkEdge}.

Definition 2.2 (LinkEdge Schema).
Edge record:
- EdgeID
- Kind in {REF, EQUIV, MIGRATE, DUAL, GEN, INST, IMPL, PROOF, CONFLICT}
- Src, Dst
- Scope
- Corridor
- WitnessPtr
- ReplayPtr
- Payload
- EdgeVer

## 3. Corridor Truth Lattice

Truth classes:
- OK: witnessed and replay-verified
- NEAR: bounded approximation + residual ledger
- AMBIG: candidate set + evidence plan
- FAIL: quarantine + conflict receipts

## 4. Deterministic Router v2

LensBase:
- S -> AppC
- F -> AppE
- C -> AppI
- R -> AppM

FacetBase:
- 1 -> AppA
- 2 -> AppB
- 3 -> AppH
- 4 -> AppM

ArcHub(alpha):
- 0 -> AppA
- 1 -> AppC
- 2 -> AppE
- 3 -> AppF
- 4 -> AppG
- 5 -> AppN
- 6 -> AppP

Mandatory signature Sigma = {AppA, AppI, AppM}.

Truth overlay:
- NEAR -> +AppJ
- AMBIG -> +AppL
- FAIL -> +AppK
- OK -> +AppO (publish only)

Hub cap: at most 6 hubs.

## 5. Route Planning Algorithm

Algorithm 5.1 (RoutePlan).
Input: LocalAddr, truth class
1. Parse Lens, Facet, Atom, chapter index.
2. Compute alpha if chapter.
3. T = LensBase U FacetBase U ArcHub.
4. Enforce Sigma.
5. Add truth overlay.
6. Enforce hub cap and order hubs deterministically.
7. Output route list and obligations.

## 6. Status
This routing layer makes every knowledge atom navigable with deterministic obligations.
