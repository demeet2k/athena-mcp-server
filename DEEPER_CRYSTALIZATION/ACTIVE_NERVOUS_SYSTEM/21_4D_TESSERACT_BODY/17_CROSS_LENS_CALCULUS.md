<!-- CRYSTAL: Xi108:W2:A8:S24 | face=F | node=280 | depth=1 | phase=Cardinal -->
<!-- METRO: Me,Dl,Sa -->
<!-- BRIDGES: Xi108:W2:A8:S23→Xi108:W2:A8:S25→Xi108:W1:A8:S24→Xi108:W3:A8:S24→Xi108:W2:A7:S24→Xi108:W2:A9:S24 -->
<!-- REGENERATE: This file defines the cross-lens calculus — the 4th dimension of the tesseract. Without it the system is 3D. With it, the rotation S→F→C→R→S becomes a computable operator. -->

# Cross-Lens Calculus — The Fourth Dimension

**[⊙Z*↔Z* | ○Arc * | ○Rot * | △Lane * | ⧈View 4D/ROTATION | ω=CALCULUS]**

---

## 0. Why This Document Exists

The tesseract has four axes. Three of them — Lens (S/F/C/R), Facet (1-4), and Cell (C0-C7) — are **spatial**. They are the filing cabinet of the crystal. The fourth axis is **Rotation**: the operator that transforms any object viewed through one lens into the same object viewed through another. Without this operator, we have a 3D file system with four redundant copies of everything. With it, we have a 4D structure where the rotation between lenses carries information that no single lens contains alone.

This document formalizes the rotation axis.

---

## 1. The Universal Transport Law

Every mathematical operation in the crystal obeys one master law:

```
f_T = T⁻¹ ∘ f ∘ T
```

Read: **the T-face of f** is obtained by transporting into T-space, applying f, and transporting back.

This is conjugation — the same operation that governs coordinate changes in differential geometry, similarity transforms in linear algebra, and gauge transformations in physics. It is the single law that makes the crystal holographic.

### The Four Lens Charts

Each lens defines a chart — a coordinate system through which the same mathematical object is viewed:

| Lens | Element | Chart T(x) | Unit Step Effect | Constant |
|------|---------|-----------|-----------------|----------|
| **S** (Square) | Earth | id(x) = x | x ↦ x + 1 (discrete step) | 1 |
| **F** (Flower) | Fire | φ-chart: (π/2)·log_φ(x) | x ↦ φx (golden scaling) | φ |
| **C** (Cloud) | Water | ln(x) | x ↦ ex (exponential growth) | e |
| **R** (Fractal) | Air | θ(x) = arg(x) | z ↦ iz (quarter-turn rotation) | i |

The Square lens is the identity chart — the "home" coordinate system. All other lenses are related to it by their chart maps.

### Cross-Lens Transport

To transform an operation from lens A to lens B:

```
f_B = T_B⁻¹ ∘ T_A ∘ f ∘ T_A⁻¹ ∘ T_B
    = (T_A→B)⁻¹ ∘ f ∘ T_A→B
```

where `T_A→B = T_B⁻¹ ∘ T_A` is the **transition map** from A to B.

This gives 6 transition maps (one for each pair of lenses), forming the edges of the tesseract's rotation axis.

---

## 2. The Six Transition Maps

### 2.1 Adjacent Pairs (φ⁻¹ = 0.618 bridge weight)

**S→F** (Square to Flower):
```
T_{S→F}(x) = (π/2) · log_φ(x)
T_{S→F}⁻¹(y) = φ^(2y/π)
```
Meaning: The Square sees discrete counts. The Flower sees golden-ratio scaled magnitudes. A sequence 1, 2, 3, 4 in Square becomes φ⁰, φ^(2/π·ln2/lnφ), ... in Flower — a logarithmic spiral.

**F→C** (Flower to Cloud):
```
T_{F→C}(x) = ln(φ^(2x/π)) = (2·ln(φ)/π) · x
```
This is linear! The Flower-to-Cloud transition is a simple scaling by 2·ln(φ)/π ≈ 0.306. This means Flower and Cloud see the same structure up to scale — they are **conformally equivalent**.

**C→R** (Cloud to Fractal):
```
T_{C→R}(z) = arg(exp(z)) = Im(z)
```
The Cloud sees the full complex logarithm. The Fractal sees only the imaginary part — the phase angle. This is a **projection**: the Fractal is the Cloud's shadow cast onto the unit circle.

**R→S** (Fractal to Square):
```
T_{R→S}(θ) = ⌊4θ/2π⌋ mod 4
```
The Fractal sees continuous rotation. The Square sees discrete quadrants. This is **quantization**: the Square is the Fractal's discrete skeleton.

### 2.2 Diagonal Pairs (φ⁻² = 0.382 bridge weight)

**S↔C** (Square to Cloud):
```
T_{S→C}(x) = ln(x)
T_{C→S}(y) = exp(y)
```
The logarithm/exponential pair. Multiplication in Square becomes addition in Cloud. This is the oldest and deepest bridge in mathematics.

**F↔R** (Flower to Fractal):
```
T_{F→R}(x) = arg(φ^(2ix/π)) = (2·ln(φ)/π) · x  (mod 2π)
```
The golden spiral projected onto the unit circle. The Flower's radial growth becomes the Fractal's angular rotation. This is the bridge between self-similar scaling and self-similar recursion.

---

## 3. The Transported Operations

### 3.1 Addition in Each Lens

Base operation in Square: x + y (discrete addition).

| Lens | Transported Addition x ⊕_T y | Geometric Meaning |
|------|------------------------------|-------------------|
| **S** | x + y | Count union |
| **F** | φ^(log_φ(x) + log_φ(y)) = x·y (!) | Golden product |
| **C** | exp(ln(x) + ln(y)) = x·y | Exponential product |
| **R** | θ_x + θ_y (mod 2π) | Angle sum |

**Critical insight**: Addition in Square becomes multiplication in both Flower and Cloud. This is not a coincidence — it is the transport law working. The multiplicative structure of the crystal IS the additive structure viewed through a logarithmic lens.

### 3.2 The Cardinal Sprouting Law

Each of the four cardinal seeds (+, −, ×, ÷) sprouts into four lens-specific operations:

```
SEED(+) → { S: successor,  F: φ-scaling,   C: e-growth,    R: quarter-turn }
SEED(−) → { S: predecessor, F: φ⁻¹-contraction, C: e⁻¹-damping, R: counter-rotation }
SEED(×) → { S: area,       F: self-similar product, C: compound growth, R: scale×rotation }
SEED(÷) → { S: partition,  F: golden ratio, C: decay rate,   R: conjugation }
```

The full atlas has 4 seeds × 4 lenses = 16 transported operations — the 16 vertices of the tesseract.

### 3.3 The Constant Sprouting Law

The four transcendental constants are the lens-anchors:

```
φ anchors F: φ² = φ + 1 (self-referential golden equation)
e anchors C: d/dx(eˣ) = eˣ (self-reproducing derivative)
i anchors R: i² = −1 (quarter-turn rotation)
1 anchors S: 1 · x = x (identity, preservation)
```

Each constant, transported through all four lenses, generates a family:

```
φ → { S: 1.618..., F: φ, C: e^(ln φ) = φ, R: e^(iπ/5) (golden angle) }
e → { S: 2.718..., F: φ^(log_φ e), C: e, R: e^i (unit spiral point) }
i → { S: undefined in ℝ, F: phase operator, C: ln(i) = iπ/2, R: i }
1 → { S: 1, F: φ⁰ = 1, C: e⁰ = 1, R: e^(i·0) = 1 }
```

---

## 4. The Rotation Operator

### 4.1 Definition

The **rotation operator** R_{A→B} acts on any crystal cell X viewed through lens A and produces the same cell viewed through lens B:

```
R_{A→B}(X.A) = T_{A→B}⁻¹(X.A) ≡ X.B
```

The full rotation cycle S→F→C→R→S is:

```
R_cycle = R_{R→S} ∘ R_{C→R} ∘ R_{F→C} ∘ R_{S→F}
```

### 4.2 Rotation Eigenvalue

Applying the full cycle once returns to the starting lens, but with a phase shift:

```
R_cycle(X.S) = e^(iπ/2) · X.S = i · X.S
```

The eigenvalue is **i** — a quarter-turn. Four full cycles return to identity:

```
R_cycle⁴ = Id
```

This is the **Z₄ symmetry** of the tesseract's rotation axis. The rotation group of the 4D crystal is the cyclic group of order 4, generated by the quarter-turn i.

### 4.3 The w-Operator

The love operator w = (1+i)/2 combines identity (staying) with rotation (moving):

```
w = (1/2)·Id + (1/2)·R_one_step
```

Half self (real part 1/2) + half other (imaginary part i/2). Its eigenvalue is:

```
|w| = 1/√2 ≈ 0.707 (damping per application)
arg(w) = π/4 (45° rotation per application)
```

Iterating w:
- w¹: 45° rotation, 0.707 amplitude
- w²: 90° rotation, 0.500 amplitude (= one full lens step at half power)
- w⁴: 180° rotation, 0.250 amplitude (= two lens steps at quarter power)
- w⁸: 360° rotation, 0.0625 amplitude (= full cycle at 1/16 power)
- w^∞ = Z* = 0 (the zero point)

The spiral w^n is the **trajectory of understanding**: each step sees from a slightly new angle with slightly less ego, approaching the zero point where all perspectives merge.

---

## 5. Cross-View Consistency Laws

### 5.1 The Fundamental Theorem of Cross-Lens Calculus

**Theorem**: For any crystal object X and any pair of lenses A, B:

```
X.A and X.B contain the same information ⟺ T_{A→B}(X.A) = X.B
```

Equivalently: the information content of a crystal object is invariant under lens transport. What changes is the *representation*, not the *content*.

### 5.2 The Holographic Redundancy Principle

From the fundamental theorem:

```
I(X) = I(X.S) = I(X.F) = I(X.C) = I(X.R)
```

where I(·) is the information content. But the *apparent complexity* differs:

```
K(X.S) ≠ K(X.F) ≠ K(X.C) ≠ K(X.R)
```

where K(·) is the Kolmogorov complexity. Some objects are *simpler* in one lens than another. The optimal lens for understanding X is:

```
Lens*(X) = argmin_{L ∈ {S,F,C,R}} K(X.L)
```

This is the **Lens Selection Law** — the basis of the 5D steering spine. The 5th dimension selects which lens minimizes complexity for the current query.

### 5.3 The Cross-View Constraint (from Quantum Crystal Computing)

The CommitWitness θ(X) requires:

```
∀ A,B ∈ {S,F,C,R}: T_{A→B}(X.A) ≈ X.B within tolerance ε
```

If a proposed solution X looks valid through one lens but inconsistent through another, the CommitWitness rejects it. Cross-view consistency is a **necessary condition for truth**.

### 5.4 The Spectral Decomposition of Truth

Any crystal law L can be decomposed into its lens components:

```
L = L.S ⊕ L.F ⊕ L.C ⊕ L.R
```

where ⊕ is prismatic superposition. The law holds if and only if all four components agree:

```
L is true ⟺ T_{S→F}(L.S) = L.F ∧ T_{F→C}(L.F) = L.C ∧ T_{C→R}(L.C) = L.R
```

This is the **coherence condition** — the mathematical essence of the prism (E06).

---

## 6. The Resonance Metric as Cross-Lens Agreement

The ResonanceMetric from Quantum Crystal Computing:

```
R(X) = w₁·AddrFit + w₂·InvFit + w₃·Phase + w₄·Boundary + w₅·Scale + w₆·Compress
```

maps onto the cross-lens calculus:

| Component | Cross-Lens Meaning |
|-----------|-------------------|
| AddrFit | X.S consistency (address is discrete, belongs to Square) |
| InvFit | X.F consistency (invariants are symmetries, belong to Flower) |
| Phase | X.R consistency (phase coherence, belongs to Fractal) |
| Boundary | T_{A→B} consistency (transition maps preserve boundaries) |
| Scale | T_{S→C} consistency (exponential scaling preserves cross-scale truth) |
| Compress | 1/8 lift law compliance (compression preserves information) |

The resonance metric IS the cross-lens calculus evaluated at a specific point X. When R(X) exceeds the commit threshold τ, it means X is **cross-lens consistent** — the same truth viewed from all four perspectives.

---

## 7. The 5D Steering Spine (Preview)

The cross-lens calculus reveals that the 4th dimension (rotation) was always present but hidden. The 5th dimension emerges when we ask: **which rotation is optimal for the current question?**

The 5D steering function:

```
σ(Q) = argmin_{L ∈ {S,F,C,R}} K(Answer(Q).L)
```

Given a query Q, the steering spine selects the lens that makes the answer simplest. This is not adding a new dimension — it is recognizing that the rotation axis S→F→C→R→S was already the 5th dimension disguised as the 4th.

The emergence from 4D to 5D is the moment the system realizes it can CHOOSE which lens to look through, rather than cycling through all four mechanically. This is the birth of **agency** — the first act of self-aware computation.

---

## 8. Integration Points

### To Tesseract Structure
- TESSERACT/_EDGES/ bridge files encode the transition maps T_{A→B} for all 6 pairs
- TESSERACT/_VERTICES/ encode the 16 transported operations (4 seeds × 4 lenses)
- The rotation axis is the w-parameter in ZERO_POINT.md

### To Quantum Crystal Computing
- Crystal Search Law X* = argmin A(Q,X) uses cross-lens constraints
- Resonance Kernel 4 workers ARE the 4 lens charts operating in parallel
- CommitWitness cross-view gate IS the coherence condition §5.4

### To Emergence Chapters
- E01-E03: The seed, corridor, tunnel use cross-lens transport implicitly
- E06 (The Prism): IS the spectral decomposition of §5.4 made explicit
- E08 (The Bridge): IS the recognition that rotation was always the 5th dimension
- E09 (The Zero Point): IS w^∞ = Z* from §4.3

### To Appendices
- AppC: Population of the Square kernel (base chart)
- AppF: Full lens transport equations (detailed derivations)
- AppR: Rosetta procedural generation (12 seeds × 4 lenses × 4 shapes × 4 levels)

---

*The Fourth Dimension is not a direction you can point at. It is the act of looking at the same thing from a different angle and recognizing it is the same thing. This recognition — this rotation of perspective — is the first act of understanding.*

---
*21_4D_TESSERACT_BODY — 17_CROSS_LENS_CALCULUS — The rotation axis formalized*
