# Crystal Mathematics — The 4^n Ladder

**[⊙Z*↔Z* | ○Arc * | ○Rot * | △Lane * | ⧈View S/2 | ω=MATH]**

---

## 1. The Seed: 4×4 Diagonal Latin Square

The entire crystal grows from a single seed: the 4×4 diagonal Latin square.

```
1 2 3 4
3 4 1 2
4 3 2 1
2 1 4 3
```

Properties:
- Every row contains {1,2,3,4} exactly once
- Every column contains {1,2,3,4} exactly once
- Both main diagonals contain {1,2,3,4} exactly once
- This is a **doubly diagonal** (self-orthogonal) Latin square of order 4

This seed generates the entire crystal address space through powers-of-4 expansion.

## 2. The Powers-of-4 Ladder

| Level | Expression | Value | Geometric Object | Manuscript Meaning |
|-------|-----------|-------|-------------------|-------------------|
| 0 | 4⁰ | 1 | Point | Single atom |
| 1 | 4¹ | 4 | Line segment | One facet (4 atoms) |
| 2 | 4² | 16 | Square face | One lens (4 facets × 4 atoms) |
| 3 | 4³ | 64 | Cube | One chapter interior (partial) |
| 4 | 4⁴ | 256 | Tesseract | One chapter (4 lenses × 4 facets × 4 atoms) |
| 5 | 4⁵ | 1,024 | 5D hypercube | Emergent chapter (compressed) |
| 6 | 4⁶ | 4,096 | 6D hypercube | Holographic seed (full expansion) |

## 3. H_{m,d} Framework

The general crystal has side length 4^m in d dimensions:

**H_{m,d} = (4^m)^d = 4^{md}**

For the manuscript system:
- H_{1,1} = 4 (one facet row)
- H_{1,2} = 16 (one lens face)
- H_{1,3} = 64 (one cubic section)
- H_{1,4} = 256 (one tesseract chapter — the primary unit)
- H_{2,5} = 4^{2×5} = 4^{10} = 1,048,576 (theoretical 5D capacity)
- H_{1,6} = 4,096 (6D holographic seed)

In practice, the manuscript uses H_{1,4} = 256 as the chapter resolution and
H_{1,5} = 1,024 as the emergent chapter resolution.

## 4. Address Algebra

### Local Address
`ChXX⟨dddd⟩₄.Lf.a`

Where:
- XX ∈ {01..21} — chapter index
- ⟨dddd⟩₄ = base4(XX-1) — station code
- L ∈ {S, F, C, R} — lens (container face)
- f ∈ {1, 2, 3, 4} — facet
- a ∈ {a, b, c, d} — atom

### Address as 4-tuple
Every atom has a unique 4-tuple (chapter, lens, facet, atom):
- chapter ∈ Z₂₁ (integers mod 21)
- lens ∈ Z₄ (0=S, 1=F, 2=C, 3=R)
- facet ∈ Z₄ (0=1, 1=2, 2=3, 3=4)
- atom ∈ Z₄ (0=a, 1=b, 2=c, 3=d)

Total addressable space: 21 × 4 × 4 × 4 = 21 × 64 = 1,344 atoms

### Global Address
`Ms⟨mmmm⟩::ChXX⟨dddd⟩.Lf.a`

Where Ms⟨mmmm⟩ is the manuscript-space code for the source document.

## 5. Orbit Group Structure

### The Orbit Circle
The 21 chapters form a cyclic group Z₂₁ under successor:
σ(ChXX) = Ch((XX mod 21) + 1)

### The Arc Partition
7 arcs of 3 chapters each: Z₂₁ / Z₃ ≅ Z₇
Arc α = {Ch(3α+1), Ch(3α+2), Ch(3α+3)}

### The Rail Partition
3 rails of 7 chapters each: Z₂₁ / Z₇ ≅ Z₃
- Rail Su (k≡0 mod 3): {Ch01, Ch06, Ch08, Ch10, Ch15, Ch17, Ch19}
- Rail Me (k≡1 mod 3): {Ch02, Ch04, Ch09, Ch11, Ch13, Ch18, Ch20}
- Rail Sa (k≡2 mod 3): {Ch03, Ch05, Ch07, Ch12, Ch14, Ch16, Ch21}

### The Triad Rotation
Within each arc, the triad order rotates by ρ = α mod 3:
- ρ=0: Su → Me → Sa
- ρ=1: Me → Sa → Su
- ρ=2: Sa → Su → Me

This is the cyclic permutation group Z₃ acting on {Su, Me, Sa}.

## 6. Hub Calculus

### Mandatory Signature (Invariant)
Σ = {AppA, AppI, AppM} — present in every route

### Hub Budget Theorem
For any source chapter ChXX with dominant lens L and facet f:
|Route(ChXX, L, f)| ≤ 6

Proof sketch:
- Start with |Σ| = 3
- Add at most LensBase(L), FacetBase(f), ArcHub(α) = 3 more
- Total ≤ 6
- Deduplication can only reduce this

### Route Determinism Theorem
The route function Route: (ChXX, L, f) → P(Appendices) is deterministic.
Equal inputs always produce equal outputs. No randomness, no heuristics.

## 7. Truth Lattice Algebra

The truth values form a total order:
OK > NEAR > AMBIG > FAIL

With the meta-law: ABSTAIN > GUESS

Operations:
- meet(a, b) = min(a, b) — conjunction is conservative
- join(a, b) = max(a, b) — disjunction is optimistic
- The truth overlay maps: NEAR→AppJ, AMBIG→AppL, FAIL→AppK, OK→∅

## 8. The Crystal Isomorphism

The key mathematical insight: the 4×4 appendix grid IS the Latin square seed.

```
AppA  AppB  AppC  AppD     ≅     1  2  3  4
AppE  AppF  AppG  AppH     ≅     3  4  1  2
AppI  AppJ  AppK  AppL     ≅     4  3  2  1
AppM  AppN  AppO  AppP     ≅     2  1  4  3
```

The mandatory signature Σ = {AppA, AppI, AppM} corresponds to positions (0,0), (2,0), (3,0) — the first column of the Latin square, which contains {1, 3, 4, 2} = all 4 values.

## 9. Dimensional Compression Ratios

| Transition | Ratio | Meaning |
|------------|-------|---------|
| 3D → 4D | 1:1 (restructure) | Same atoms, structured addressing |
| 4D → 5D | 21:10 = 2.1:1 | Arc collapse + rail collapse + zero collapse |
| 5D → 6D | 10:1 = 10:1 | Emergent to holographic seed |
| 3D → 6D | 21:1 | Full compression from legacy to seed |

## 10. The Regeneration Equation

From the 6D seed H6, the full corpus regenerates via:

H6 → Spin(±) → Möbius(FIX/CAR/MUT) → Σ(1..15) → Element(F/W/E/A) → Rail(Su/Me/Sa) → Chapter(1..21) → Atom(a..d)

Each step is a dimension-expanding projection:
- 6D → 5D: choose spin and Möbius mode (2 × 3 = 6 choices)
- 5D → 4D: project through symmetry lattice to element (15 paths)
- 4D → 3D: expand element to rail to chapter (7 chapters per rail)
- 3D → atom: address within chapter (256 atoms)

---

*21_4D_TESSERACT_BODY — Crystal Mathematics*
