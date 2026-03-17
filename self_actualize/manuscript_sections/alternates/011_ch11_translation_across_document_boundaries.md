## **Ch11⟨0022⟩ — Translation Across Document Boundaries**

**[○Arc 3 | ○Rot 0 | △Lane Me | ω=10]**

Workflow Role: Translation

Primary hubs: **→ AppF → AppI → AppH**

Cross-Links: **EQUIV → Ch09⟨0020⟩.S2.b, REF → Ch20⟨0103⟩.F4.c**

### Chapter Thesis

Translation across document boundaries is lawful only when it is treated as a proof-carrying transport problem rather than a prose-paraphrase problem. A source document does not merely correspond to a target document. It exposes a typed address space, a closure discipline, a corridor policy, a deterministic numeric kernel, and a replay obligation. A target document exposes the same classes of objects under a different chart. The task of Chapter 11 is to define the translation operator that moves claims, constructions, and certificates across those charts without silently changing their truth conditions.

The central object of the chapter is the boundary translation matrix. It is built under AppE phase-rotation rules, admitted under AppF corridor legality, evaluated by AppI solver and conflict machinery, scored by the AppH numeric kernel, escalated to AppK quarantine when the transport claim fails, and sealed into replayable verifier capsules by AppM. In this sense, translation is neither a human impression nor a one-shot conversion. It is a typed computation from one document closure to another.

### 11.A Square — Objects of Boundary Translation

#### 11.A.1 Source and Target Documents

Let `D_s` and `D_t` be theory-documents. Each document is modeled as

`D = (DocId, A, Cl, Corr, Num, W),`

where `A` is the set of local addresses, `Cl` is the dependency-closure operator, `Corr` is the corridor policy family, `Num` is the pinned numeric kernel, and `W` is the witness store. A document boundary is an ordered pair `(D_s, D_t)` together with a declared transport intent `Intent ∈ {REF, EQUIV, MIGRATE, IMPL, PROOF}`. No translation is admissible unless both documents are first normalized to canonical addressing and closure form.

The cross-link to `Ch09⟨0020⟩.S2.b` is structural: the source side must be closure-complete before any boundary transport is attempted. If an atom `a ∈ A_s` is translated without its dependency closure `Cl_s(a)`, then the translation claim is underdetermined. The same law holds on the target side for landing sites. Thus translation begins not with lexical resemblance but with closure acquisition.

#### 11.A.2 Boundary Translation Matrix

For finite source and target slices `S ⊆ A_s` and `T ⊆ A_t`, define the translation matrix

`M_(s→t) : S × T → Ω,`

where each matrix cell is a structured record

`Ω = (Outcome, MapId, InvSet, DriftVec, ReqSet, WitnessPtrSet, ReplayPtr, CompatClass).`

`Outcome ∈ {OK, NEAR, AMBIG, FAIL}` is the corridor-typed result of translating source atom `x` to target atom `y`. `MapId` identifies the canonical alignment map. `InvSet` lists invariants claimed to survive transport. `DriftVec` contains typed deviations measured under the pinned AppH kernel. `ReqSet` records required proofs or missing evidence. `WitnessPtrSet` and `ReplayPtr` bind the claim to concrete verification artifacts. `CompatClass ∈ {ExactBytes, ExactSemantics, BoundedNear, Incompatible}` is the same compatibility partition used by migration receipts.

The matrix is not a heuristic table. It is a canonical object:

`TransMatrix = (MatrixSchemaId, MatrixId, SrcDocId, DstDocId, DomainSel, CodomainSel, CorrID, KernelId, EntryDigestList, BuildPolicyId).`

Its digest is content-addressed over the exact source selection, target selection, corridor pins, kernel pins, and entry list. Any change in policy, numeric mode, target slice, or evidence set changes the matrix identity.

#### 11.A.3 Translation Map and Invariant Bundle

Each admissible entry with `Outcome ≠ FAIL` carries a transport map

`τ_(x→y) = (π_addr, π_sem, π_cert, π_range),`

where `π_addr` maps canonical address coordinates, `π_sem` maps semantic objects, `π_cert` maps proof obligations, and `π_range` maps retrievable byte or section ranges when range-aware replay is required. The invariant bundle for `τ_(x→y)` is

`Inv(τ) = {type preservation, closure preservation, corridor admissibility, replay reproducibility}.`

If any invariant is not provable, the transport claim cannot be promoted to `OK`. This is the formal translation of the manuscript-wide law `ABSTAIN > GUESS`.

#### 11.A.4 Numeric Kernel for Boundary Scoring

Boundary translation cannot rely on floating similarity scores when those scores influence admissibility. Let `κ` be the pinned AppH kernel. Every drift, coverage, and commutation quantity is therefore measured in fixed-point or exact rational arithmetic:

`score_κ(x, y) = w_c cov_κ(x, y) + w_s sem_κ(x, y) - w_d drift_κ(x, y) - w_m miss_κ(x, y),`

with all weights and accumulators pinned by `KernelId`. This law prevents runtime-dependent ranking drift. If the corridor uses score thresholds for admissibility, those thresholds are part of the translation object and must replay identically across runtimes.

### 11.B Flower — Laws Governing Cross-Document Translation

#### 11.B.1 Closure-First Translation Law

**Theorem 11.1 (Closure-First Law).** Let `x ∈ A_s` and `y ∈ A_t`. If the translation claim `τ_(x→y)` depends on any witness, definition, or constraint outside `Cl_s(x)` or outside the declared landing closure in `D_t`, then `τ_(x→y)` cannot be assigned `OK`.

Proof sketch. By construction, `OK` requires replay-verified sufficiency of evidence. Any omitted dependency means the source or target semantics is not fully determined under the declared corridor. Therefore the transport claim is underdetermined and must evaluate to `AMBIG` or `FAIL`. This is precisely the boundary form of the closure law referenced from `Ch09⟨0020⟩.S2.b`. QED.

This theorem forces a discipline that ordinary translation workflows lack: no cell of the matrix may be interpreted independently of the closure that licenses it.

#### 11.B.2 Equivalence and Migration Separation

Translation must separate equivalence from migration. `EQUIV` claims that the transported object is semantically the same under a declared map. `MIGRATE` claims that the target object is the lawful successor of the source object under versioned change. Confusing the two is a major source of silent drift.

Formally, an equivalence edge requires forward and backward maps together with a commutation budget:

`EQUIV(x, y)` requires `(f_(x→y), g_(y→x), InvSet, κ_budget, WitnessPtrSet, ReplayPtr).`

A migration edge requires a compatibility mapping, regression corpus, and rollback plan:

`MIGRATE(x_old, y_new)` requires `(CompatMap, CompatClass, RegressionRefs, RollbackRef, WitnessPtrSet, ReplayPtr).`

If a claim needs regression evidence because the target chart introduces new structure, it is a migration claim even when large parts of the semantics survive unchanged. This is why Chapter 11 delegates regression governance to AppI rather than treating it as a linguistic afterthought.

#### 11.B.3 Partial Translation and Abstention Law

Boundary translation is allowed to be partial, but only if the partiality is explicit. Let `dom(τ)` be the domain on which the transport claim is fully witnessed. Then any attempt to extend the claim beyond `dom(τ)` without new evidence is illegal. The allowed outcomes are:

- `OK` when every required invariant is witnessed on the declared domain.
- `NEAR` when bounded drift is permitted and ledgered.
- `AMBIG` when the candidate landing set is non-singleton or evidence is insufficient.
- `FAIL` when the corridor forbids the proposed transport or a required invariant is violated.

No hidden interpolation is permitted. In particular, if two target addresses tie under the same score and the corridor does not specify a deterministic tie-break with proof obligations, the cell is `AMBIG`, not `OK`.

#### 11.B.4 Boundary Damage and Localization

**Theorem 11.2 (Damage Localization).** Suppose a translation matrix cell fails because a witness, range proof, or compatibility condition breaks. Then the failure may invalidate the affected edge set, but it need not invalidate unrelated cells whose witness roots are disjoint.

Proof sketch. The transport claims are content-addressed by cell, edge, and witness digest. If the failing witness set is isolated and the route compiler preserves witness-root separation, then unrelated cells remain independently replayable. This is the document-boundary analogue of bounded-damage localization and aligns with the damage-certification doctrine referenced by `Ch20⟨0103⟩.F4.c`. QED.

The theorem matters operationally: translation failure is not permission to discard an entire document pair. It is a signal to quarantine the minimal failing slice.

### 11.C Cloud — Algorithms for Matrix Construction, Regression, and Verification

#### 11.C.1 Deterministic Matrix Builder

The builder takes normalized document slices, closure rules, corridor pins, and kernel pins, and produces a canonical matrix:

```python
def build_translation_matrix(src_atoms, dst_atoms, corridor, kernel, closure, solver):
    entries = []
    for x in closure(src_atoms):
        candidates = []
        for y in closure(dst_atoms):
            align = solver.align(x, y, kernel=kernel, corridor=corridor)
            candidates.append(align)
        ranked = sort_canonically(candidates, kernel=kernel, corridor=corridor)
        entries.extend(seal_entries(x, ranked, corridor, kernel))
    return seal_matrix(entries, corridor, kernel)
```

`solver.align` is not permitted to emit an admissibility claim directly. It emits an alignment proposal together with required evidence. `sort_canonically` must be deterministic under the pinned numeric mode. `seal_entries` converts proposals into typed outcomes by checking corridor legality, invariant satisfaction, and replay sufficiency.

#### 11.C.2 Regression Control for MIGRATE Edges

When a target chart is not merely another presentation of the same object but a new version or layout, Chapter 11 requires regression control. Let `R` be a regression corpus. A migration claim is admissible only if:

`∀u ∈ R, Eval_old(u)` and `Eval_new(CompatMap(u))`

either match exactly or differ within the declared compatibility class. The result is summarized by a migration receipt

`MigRec = (OldId, NewId, CompatClass, RegressionDigest, RollbackRef, FirstDivergenceOptional).`

AppI governs this process because the hard cases are not syntactic. They involve solver choice, counterexample search, and first-divergence localization. If regression cannot establish the claimed compatibility class, the builder must emit `AMBIG` with an evidence plan or `FAIL` with a conflict packet.

#### 11.C.3 Verifier Capsules and Range-Aware Replay

Every promoted translation claim must terminate in a verifier capsule:

`Cap = (CapId, MatrixId, EdgePathDigest, CorrID, KernelId, WitnessRoot, ReplayPlanId, RangeRefsOptional, Outcome).`

The reference to `Ch20⟨0103⟩.F4.c` is operational. A cross-document translation is not fully sealed unless the relevant range proofs, replay plan, and damage-localization guarantees can be reconstructed on demand. This matters whenever the target document is mounted virtually, reconstructed by range, or verified without materializing the full source body. A translated claim that cannot be replayed at the granularity required by the target runtime remains below `OK`.

#### 11.C.4 Complexity and Determinism

If `|S| = m` and `|T| = n`, naive matrix construction is `O(mn)` in candidate enumeration before witness checking. The framework therefore permits pruning only under deterministic policies pinned into `BuildPolicyId`. Any heuristic pruning must itself be replayable and cannot depend on ambient runtime noise, floating order effects, or unstated caches. Speed is admissible only as a declared corridor concession; it never overrides truth typing.

### 11.D Fractal — Failure Modes, Quarantine, and Operational Output

#### 11.D.1 Conflict Packets

When boundary translation fails, the failure must be packaged rather than merely reported. The canonical conflict packet is

`Q = (SrcAddr, DstAddr, CorrID, FailureKind, MinimalWitnessSet, DivergenceRef, QuarantineKey, EvidencePlan).`

`FailureKind` distinguishes at least: missing closure, incompatible schema, violated invariant, nondeterministic ranking, failed regression, and unverified replay. `MinimalWitnessSet` is shrink-minimized under AppI rules so that the packet isolates the smallest known failing cause. `QuarantineKey` ensures the broken route cannot silently re-enter an `OK` ride.

#### 11.D.2 Quarantine Law for Boundary Translation

**Theorem 11.3 (No Silent Passage Across Failed Boundaries).** If a translation edge or verifier capsule is quarantined, no route using that object may yield `OK` until an explicit migration receipt, rollback receipt, or conflict-resolution receipt resolves the quarantine.

Proof sketch. The mycelium graph admits `OK` only on non-quarantined admissible edges. A quarantined translation object is therefore excluded from `OK` route compilation by construction. Any contrary behavior would make corridor legality non-monotone and destroy replay stability. QED.

This theorem is the precise reason AppK exists in the chapter even though it is not a primary hub in the happy path: translation that fails honestly must remain failed until repaired honestly.

#### 11.D.3 Operational Pipeline

The chapter-level transport pipeline is therefore:

1. Acquire source closure and target landing closure.
2. Build the candidate translation matrix under AppE/AppH pins.
3. Evaluate corridor legality under AppF.
4. Run AppI alignment, regression, and counterexample search.
5. Promote cells to typed outcomes.
6. If a promoted path exists, seal AppM verifier capsules with any required Ch20 range proofs.
7. If no admissible path exists, emit AppK conflict packets and quarantine the failing slice.

This pipeline converts translation from a vague editorial gesture into a deterministic bridge calculus across document shells.

#### 11.D.4 Zero-Point Compression

At zero point, translation across document boundaries is the law that the same semantic seed may inhabit more than one chart, but only through an explicit map, an explicit corridor, an explicit witness bundle, and an explicit replay plan. Everything else is resemblance, not transport.

Ch11⟨0022⟩ — Translation Across Document Boundaries
