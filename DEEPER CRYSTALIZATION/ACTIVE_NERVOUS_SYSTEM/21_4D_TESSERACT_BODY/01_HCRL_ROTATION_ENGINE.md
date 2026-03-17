# HCRL Container Rotation Engine

> The w-axis of the 4D tesseract body. Every chapter atom passes through four container faces in strict cyclic order.

---

## 1. The Four Container Faces

| Face | Symbol | Domain | Core Objects |
|------|--------|--------|--------------|
| **Square** | **S** | Discrete structure | Addresses, index algebra, finite objects, station codes, bijections |
| **Flower** | **F** | Phase geometry | Symmetry, rotation, orbit, transformation, harmonic phase |
| **Cloud** | **C** | Corridor truth | Uncertainty, candidate clouds, admissibility, truth lattice evaluation |
| **Fractal** | **R** | Recursive compression | Self-similarity, compression, replay, regeneration, seed encoding |

Each face is a complete lens through which any chapter atom can be examined. No face is privileged; the rotation is what creates depth.

---

## 2. Rotation Order

**Default cycle:** S --> F --> C --> R --> S (cyclic, period 4)

```
        S -------- F
        |  \    /  |
        |    \/    |
        |    /\    |
        |  /    \  |
        R -------- C
```

### Edge Classification

**Adjacent DUAL edges (4):**
- S <-> F : Structure-to-Phase (discrete objects acquire orbital character)
- F <-> C : Phase-to-Truth (symmetries enter admissibility evaluation)
- C <-> R : Truth-to-Fractal (evaluated corridors compress to seeds)
- R <-> S : Fractal-to-Structure (seeds expand back to discrete objects)

**Diagonal DUAL edges (2):**
- S <-> C : Structure-to-Truth (direct address verification)
- F <-> R : Phase-to-Fractal (symmetry compression shortcut)

Total edges: 6 (complete graph K4)

---

## 3. Rotation Semantics

When processing any chapter atom through the 4 lenses:

### Pass 1 -- S (Square)
- Enumerate all discrete objects in the atom scope
- Assign addresses using the 4D coordinate system ChXX(dddd).Lf.a
- Compute index properties: parity, prime factorization of omega, mod-4 class
- Identify structural dependencies and cross-references
- Output: object table with addresses

### Pass 2 -- F (Flower)
- Identify symmetries within the atom's object table
- Map phase relationships: which objects rotate into which under arc permutation
- Determine orbital structure: fixed points, 2-cycles, 3-cycles
- Compute harmonic signatures and resonance with adjacent chapters
- Output: symmetry group descriptor and orbit decomposition

### Pass 3 -- C (Cloud)
- Evaluate truth status for each object: OK / NEAR / AMBIG / FAIL
- Compute admissibility corridors: which object combinations are jointly consistent
- Assess uncertainty boundaries and candidate cloud density
- Generate truth lattice projection for the atom
- Output: truth vector and corridor map

### Pass 4 -- R (Fractal)
- Compress the evaluated atom to its fractal seed
- Verify self-similarity: the seed must regenerate the full atom under expansion
- Encode replay instructions for regeneration
- Compute compression ratio and information density
- Output: fractal seed with replay certificate

---

## 4. HCRL as Tesseract Axis

The tesseract body has four axes:

| Axis | Dimension | Range | Meaning |
|------|-----------|-------|---------|
| **z** | Chapter | Ch01..Ch21 | Which chapter (omega = 0..20) |
| **x** | Facet | f in {1,2,3,4} | Which facet within the chapter |
| **y** | Atom | a in {a,b,c,d} | Which atom within the facet |
| **w** | Lens | L in {S,F,C,R} | Which container face (HCRL rotation) |

### Full 4D Address Format

```
ChXX(dddd).Lf.a
```

Where:
- `ChXX` = chapter number (01-21)
- `(dddd)` = station code (base-4 encoding of omega, padded to 4 digits)
- `L` = lens face: S, F, C, or R
- `f` = facet number: 1, 2, 3, or 4
- `a` = atom label: a, b, c, or d

**Total addressable atoms:** 21 chapters x 4 lenses x 4 facets x 4 atoms = **1344 atoms**

**Per chapter:** 4 x 4 x 4 = **64 addressable atoms**

---

## 5. Rotation Invariants

These properties hold across all HCRL rotations:

### INV-1: Completeness
Every complete HCRL rotation must touch all 4 faces. A partial rotation (e.g., S -> F only) is flagged as incomplete and cannot produce a valid fractal seed.

### INV-2: Mandatory Signature Preservation
The mandatory signature Sigma = {AppA, AppI, AppM} is rotation-invariant. Regardless of which face the router enters from, these three appendices remain in the hub set.

### INV-3: Truth Propagation
Truth lattice values are computed on the C face and propagated to all faces:
- S receives truth as address validity flags
- F receives truth as symmetry-breaking indicators
- R receives truth as compression eligibility gates

### INV-4: Fractal Reversibility
Fractal compression (R face) must be reversible to S expansion. For any atom A:

```
expand(compress(A)) = A
```

This is the fundamental round-trip guarantee of the tesseract body.

### INV-5: Lens Commutativity of Invariants
While the rotation order S -> F -> C -> R is the default processing sequence, the *invariant properties* (truth values, mandatory signature) are order-independent. Re-entering at any face yields the same invariants.

---

## 6. Edge Adjacency Matrix

The 4x4 adjacency matrix of container faces:

```
       S    F    C    R
  S  [ 0    1    1    1 ]
  F  [ 1    0    1    1 ]
  C  [ 1    1    0    1 ]
  R  [ 1    1    1    0 ]
```

All entries are 1 (off-diagonal) because K4 is complete. However, edges carry different weights:

### Weighted Adjacency (by transition frequency)

```
       S    F    C    R
  S  [ --   ADJ  DIA  ADJ ]
  F  [ ADJ  --   ADJ  DIA ]
  C  [ DIA  ADJ  --   ADJ ]
  R  [ ADJ  DIA  ADJ  --  ]
```

Where:
- **ADJ** = Adjacent dual edge (primary rotation path, weight 1)
- **DIA** = Diagonal dual edge (shortcut path, weight sqrt(2))

### Edge Table

| Edge | Type | Transition Semantics |
|------|------|---------------------|
| S-F | Adjacent | Structure acquires phase |
| F-C | Adjacent | Phase enters truth evaluation |
| C-R | Adjacent | Truth compresses to fractal |
| R-S | Adjacent | Fractal expands to structure |
| S-C | Diagonal | Direct verification shortcut |
| F-R | Diagonal | Symmetry compression shortcut |

---

## 7. Rotation Protocol

### Entry Conditions
A rotation begins when a chapter atom is submitted for processing. The atom must have:
1. A valid 4D address
2. A specified entry face (default: S)
3. An intent tag from {VERIFY, BUILD, MIGRATE, RESOLVE, PUBLISH}

### Exit Conditions
A rotation completes when:
1. All 4 faces have been visited
2. The fractal seed has been generated (R face)
3. The round-trip check passes: expand(seed) matches original
4. The truth vector has been propagated to all faces

### Failure Modes
- **Incomplete rotation**: fewer than 4 faces visited --> retry from missed face
- **Compression failure**: R face cannot produce reversible seed --> flag AMBIG on C face, re-evaluate
- **Truth propagation failure**: C face values inconsistent across faces --> escalate to AppK

---

*Engine version: HCRL-v1.0 | Tesseract axis: w | Rotation period: 4*
