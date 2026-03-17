# AppR - Rosetta Procedural Generation Engine

Routing role: The universal seed-to-atlas expansion protocol. Given any seed (cardinal or constant), this appendix defines the deterministic procedure that generates its full 64-cell crystal tile and its 256-cell constant-crystal extension. This is the math Rosetta Stone of the entire system.

## R.0 — The Generation Axiom

Every mathematical object in the system is generated — not listed — from exactly 12 seeds through a fixed expansion grammar:

```
SEED × 4_SHAPES × 4_ELEMENTS × 4_LEVELS = 64-cell atlas
64-cell atlas × 4_CONSTANTS = 256-cell constant-crystal
```

The 12 seeds are:

| # | Seed | Class | Primitive | Compress | Sprouts Into |
|---|------|-------|-----------|----------|--------------|
| 1 | `+` | Cardinal-01 | `N ↦ N+1` | `Succ` ("one more") | e, φ, i, π |
| 2 | `−` | Cardinal-02 | `F − G` | `Δ` ("difference") | 1/e, 1/φ, −i, 1/π |
| 3 | `×` | Cardinal-03 | `(x,y) ↦ xy` | `Bind` ("compose") | e, i, φ, π |
| 4 | `÷` | Cardinal-04 | `a/b` (gated) | `Inv_lawful` ("invert inside corridor") | 1/φ, 1/π, 1/e, −i |
| 5 | `φ` | Constant-01 | `x² − x − 1 = 0` | `Scale` ("grow preserving form") | recursion eigenvalue |
| 6 | `π` | Constant-02 | `n·sin(π/n) → π` | `Close` ("curvature closure") | geometric completion |
| 7 | `e` | Constant-03 | `(1+1/n)ⁿ → e` | `Grow` ("compound infinitesimally") | exponential flow |
| 8 | `i` | Constant-04 | `i² = −1` | `Turn` ("quarter-turn phase") | rotation algebra |
| 9 | `FE-I` | Equation-01 | `φ² = φ + 1` | Golden self-reference | additive recursion |
| 10 | `FE-II` | Equation-02 | `e^(iπ) + 1 = 0` | Euler unity | constant-crystal crown |
| 11 | `FE-III` | Equation-03 | `ζ(s) = Π_p(1−p^−s)^−1` | Prime-product | multiplicative encoding |
| 12 | `FE-IV` | Equation-04 | `f_T = T^−1 ∘ f ∘ T` | Lens transport | universal conjugacy |

## R.1 — The Four Shapes (Lens Grammar)

| Shape | Symbol | Domain | Runtime Role |
|-------|--------|--------|-------------|
| Square | ◻ | Formal / discrete / algebraic / local | Exact computation, counting, proof |
| Flower | ✿ | Continuous / geometric / harmonic / wave | Smooth accumulation, phase, integral |
| Cloud | ☁ | Probabilistic / ensemble / statistical | Expectation, measure, inference |
| Fractal | ❋ | Recursive / self-similar / scale-invariant | RG flow, renormalization, depth |

## R.2 — The Four Elements (Elemental Anchors)

| Element | Symbol | Domain | Tunneling |
|---------|--------|--------|-----------|
| Earth | 🜃 | Constraint / embodiment / lattice / count | Adjacent to Water, Fire |
| Water | 🜄 | Adaptation / flow / continuity / convergence | Adjacent to Earth, Air |
| Fire | 🜂 | Initiation / impulse / dynamics / injection | Adjacent to Air, Earth |
| Air | 🜁 | Mapping / routing / transform / encoding | Adjacent to Fire, Water |

Tunneling law: 90° rotation only through adjacent elements. Earth↔Water, Water↔Air, Air↔Fire, Fire↔Earth.

## R.3 — The Four Levels (Depth Ladder)

| Level | Code | Interpretation |
|-------|------|---------------|
| L0 | Primitive | Bare seed operation in this shape×element cell |
| L1 | First expansion | One step of structural enrichment |
| L2 | Composition | Multi-step or compound form |
| L3 | Limit / closure | Full depth, boundary behavior, or proof of impossibility |

## R.4 — The Universal Lens Transport Law

The foundation that makes procedural generation possible:

```
f_T = T^{−1} ∘ f ∘ T          (conjugacy transport)
x ⊕_T y = T^{−1}(T(x) + T(y))  (transported addition)
x ⊗_T y = T^{−1}(T(x) · T(y))  (transported multiplication)
```

### R.4.1 — Canonical Lens Charts

| Constant | Chart T(x) | Transport Law | Effect |
|----------|-----------|---------------|--------|
| e | T(x) = ln(x) | ln(x) ↦ ln(x) + 1 ⟺ x ↦ ex | Addition becomes multiplication by e |
| φ | T(x) = log_φ(x) | log_φ(x) ↦ log_φ(x) + 1 ⟺ x ↦ φx | Addition becomes golden scaling |
| i | T(x) = θ (phase) | θ ↦ θ + π/2 ⟺ z ↦ iz | Addition becomes quarter-turn rotation |
| π | T(x) = arc angle | θ ↦ θ + δθ, Σδθ → π, 2π | Addition becomes geometric closure |

### R.4.2 — The φ-Lens Master Equation

```
T(x) = (π/2) · log_φ(x)
T(φx) = T(x) + π/2
```

This is the deepest Rosetta equation: **scale becomes phase, multiplication becomes translation, recursion becomes rotation.**

## R.5 — The Sprouting Law (Cardinal → Constant)

Each cardinal operation sprouts into the four constants by changing what the operation *means* in the appropriate lens chart:

### R.5.1 — Plus Sprouting

```
+ → e :  additive step in ln-space = multiplication by e     (growth)
+ → φ :  additive step in log_φ-space = multiplication by φ  (recursion)
+ → i :  additive step in phase-space = rotation by π/2      (phase)
+ → π :  additive step in angle-space = geometric closure     (curvature)
```

### R.5.2 — Minus Sprouting (Anti-Constants)

```
− → 1/e :  decay, damping, inverse growth
− → 1/φ :  contraction, inverse recurrence, history retrieval
− → −i  :  conjugation, counter-rotation, phase reversal
− → 1/π :  normalization, density correction, spectral density
```

### R.5.3 — Multiplication Sprouting

```
× → e :  compounding, exponentiation, semigroup flow
× → φ :  self-similar scaling, recursive multiplication
× → i :  scale×rotation, phase composition
× → π :  product closure, Viète/Wallis normalization
```

### R.5.4 — Division Sprouting (Anti-Constant, Gated)

```
÷ → 1/φ :  contraction ratio, inverse scale
÷ → 1/π :  normalization tax, density correction
÷ → 1/e :  damping, rare-event suppression
÷ → −i  :  conjugation, inverse transform kernel
```

**Gate condition**: Division sprouts are only legal when an admissibility certificate proves the inverse corridor exists (gcd(b,N)=1 in lattice, denominator ≠ 0 in continuous, etc.).

## R.6 — The Four Fundamental Equations (Crown Seeds)

These are the equations that compress entire seed families into single invariants:

### R.6.1 — Per-Cardinal Crown Equations

| Seed | Equation | Meaning |
|------|----------|---------|
| + | `e^(iπ) + 1 = 0` | All constant sprouts unified |
| − | `\|ψ₁+ψ₂\|² = (a−b)² when Δθ=π` | Subtraction is phase geometry |
| × | `(r₁e^{iθ₁})(r₂e^{iθ₂}) = (r₁r₂)e^{i(θ₁+θ₂)}` | Product = scale × rotation |
| ÷ | `H(a,b) = 2ab/(a+b)` | Harmonic midpoint as reciprocal center |

### R.6.2 — Per-Constant Crown Equations

| Seed | Equation | Meaning |
|------|----------|---------|
| φ | `φ² = φ + 1` | Self-similar algebraic birth |
| π | `π = lim n·sin(π/n)` | Polygon → circle closure |
| e | `e = lim(1+1/n)ⁿ` | Infinitesimal compounding |
| i | `i² = −1` | Quarter-turn squared is inversion |

### R.6.3 — The Universal Crown

```
e^{iπ} + 1 = 0
```

This compresses the entire constant crystal into a single equation.

## R.7 — The Rosetta Compression Law

Every seed has a faithful compression that preserves its generator:

```
Compress(+) = Succ        ("one more")
Compress(−) = Δ           ("remove, recover, or regularize by difference")
Compress(×) = Bind        ("compose two structures into one larger lawful structure")
Compress(÷) = Inv_lawful  ("invert only inside the declared corridor")
Compress(φ) = Scale       ("grow while preserving form")
Compress(π) = Close       ("accumulate until boundary seals")
Compress(e) = Grow        ("compound infinitesimally")
Compress(i) = Turn        ("quarter-turn phase increment")
```

## R.8 — Procedural Generation Algorithm

To generate any cell in the 768-operation atlas:

```
INPUT:  seed ∈ {+,−,×,÷,φ,π,e,i,FE-I..IV}
        shape ∈ {Square, Flower, Cloud, Fractal}
        element ∈ {Earth, Water, Fire, Air}
        level ∈ {L0, L1, L2, L3}

STEP 1: Identify the seed's primal primitive (from R.0)
STEP 2: Select the shape's domain interpretation (from R.1)
STEP 3: Select the element's anchoring (from R.2)
STEP 4: Apply the level's depth (from R.3)
STEP 5: If constant-crystal extension needed, apply lens transport (R.4)
         via the appropriate chart T(x) for the target constant

OUTPUT: A specific mathematical operation with:
        - domain (from shape)
        - grounding (from element)
        - depth (from level)
        - transport law (from lens chart)
```

### R.8.1 — Address Grammar

Every generated cell has a canonical address:

```
ROSETTA[seed].shape.element.Lk
```

Examples:
- `ROSETTA[+].Square.Earth.L0` = successor (n ↦ n+1)
- `ROSETTA[−].Flower.Air.L0` = phase opposition (Δθ = π)
- `ROSETTA[×].Cloud.Water.L1` = factorized likelihoods under independence
- `ROSETTA[÷].Fractal.Fire.L2` = move from blow-up to effective theory
- `ROSETTA[φ].Square.Earth.L0` = Fibonacci recurrence F_{n+1} = F_n + F_{n-1}
- `ROSETTA[e].Flower.Water.L3` = continuous field build-up from local additions

### R.8.2 — Scale Expansion

```
12 seeds × 64 cells = 768 total operations (pre-constant)
4 cardinals × 64 cells × 4 constants = 1024 cardinal-constant operations
Full atlas with cross-products = 256 × 4 = 1024 constant-crystal operations
```

## R.9 — The 256-Cell Constant Crystal (Master Formula)

The full constant crystal is generated by tensoring the four 64-cell cardinal atlases with the four constants:

```
C₂₅₆ = {π, e, i, φ} ⊗ A₊⁶⁴     (additive sprouting)
C₂₅₆⁽⁻⁾ = {1/π, 1/e, −i, 1/φ} ⊗ A₋⁶⁴   (anti-constant field)
C₂₅₆⁽ˣ⁾ = {π, e, i, φ} ⊗ A_×⁶⁴   (multiplicative binding)
C₂₅₆⁽÷⁾ = {1/π, 1/e, −i, 1/φ} ⊗ A_÷⁶⁴  (reciprocal gating)
```

The total Rosetta atlas is:

```
R₁₀₂₄ = C₂₅₆ ∪ C₂₅₆⁽⁻⁾ ∪ C₂₅₆⁽ˣ⁾ ∪ C₂₅₆⁽÷⁾
```

## R.10 — Wiring to Nervous System

### R.10.1 — Chapter Mapping

| Rosetta Component | Primary Chapter | Secondary Chapters |
|------------------|----------------|-------------------|
| Cardinal Seeds (+,−,×,÷) | Ch02 (Address Algebra) | Ch01, Ch04, Ch07 |
| Constant Seeds (φ,π,e,i) | Ch18 (Universal Math Stack) | Ch04, Ch08, Ch19 |
| Lens Transport | Ch07 (Tunnels as Morphisms) | Ch09, Ch10 |
| Sprouting Law | Ch18 (Macro Invariants) | Ch04, Ch15 |
| Compression Law | Ch10 (Multi-Lens Construction) | Ch11, Ch13 |
| Gate/Corridor Law | Ch03 (Truth Corridors) | Ch05, Ch12 |
| Fundamental Equations | Ch19 (Convergence/Fixed Points) | Ch08, Ch21 |
| Crown Equation | Ch21 (Self-Replication) | Ch18, Ch19 |

### R.10.2 — Appendix Mapping

| Rosetta Component | Primary Appendix | Role |
|------------------|-----------------|------|
| Square operations | AppC | Discrete kernels populated by Square-lens cells |
| Transport equations | AppF | Lens charts and conjugacy bridges |
| Circle/phase operations | AppE | Mixed-radix clock driven by i-seed and π-seed |
| Truth corridors | AppI | Gate conditions from ÷-seed admissibility |
| Triangle control | AppG | Three-agent synchrony from tria prima |
| Canon laws | AppB | Normal forms derived from compression law |

### R.10.3 — Swarm Mapping

| Rosetta Seed | Elemental | Archetype | Council |
|-------------|-----------|-----------|---------|
| + | Fire | Fire-Air | transport-and-runtime |
| − | Water | Water-Fire | void-and-collapse |
| × | Earth | Earth-Water | manuscript-architecture |
| ÷ | Air | Air-Earth | higher-dimensional-geometry |
| φ | Fire-Earth | Fractal anchor | identity-and-instruction |
| π | Earth-Water | Flower anchor | civilization-and-governance |
| e | Water-Air | Cloud anchor | general-corpus |
| i | Air-Fire | Square anchor | mythic-sign-systems |
