# AtlasForge v4 — Final Integrated Manual

**Version:** `4.0.0-ABSOLUTE-FINAL-ULTIMATE`  
**Build date:** `2026-01-01`  

```
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                                                      ║
║                                           ATLASFORGE                                                                 ║
║                                                                                                                      ║
║                              UNIVERSAL HARMONIC FRAMEWORK  +  PROOF-CARRYING KERNEL                                  ║
║                                        +  MEMORY ATLAS / BOOK COMPILER                                               ║
║                                                                                                                      ║
║     “Every mathematical object can be compressed into a finite SEED that, when expanded through deterministic        ║
║      OPERATIONS under explicit CONSTRAINTS, regenerates the complete object with CERTIFICATES proving correctness.”  ║
║                                                                                                                      ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
```

This document is the **final draft** reference for the AtlasForge framework as it exists in this repository.

It integrates **three layers**:

1. **Universal Harmonic Framework (UHF)** — the encoded 4×4×4×4 crystal taxonomy and its “math doctrine”
2. **Proof-carrying computation kernel** — Blueprint → Plan → Recipe → Certificates → Verification → Replay
3. **Memory Atlas layer** — structured notes + search + dependency graph + sessions + book export

The goal is not only to “do math”, but to **retain** it: every result can be captured as a **replayable artifact** and every idea can be stored as **searchable, linked knowledge**.

---

## Table of contents

- [0. Orientation](#0-orientation)
- [1. Universal Harmonic Framework](#1-universal-harmonic-framework)
  - [1.1 The four poles](#11-the-four-poles)
  - [1.2 The four lenses](#12-the-four-lenses)
  - [1.3 Layers and depths](#13-layers-and-depths)
  - [1.4 Crystal address and linear index](#14-crystal-address-and-linear-index)
  - [1.5 Meta poles vs operational poles](#15-meta-poles-vs-operational-poles)
  - [1.6 Master equation and tome decomposition](#16-master-equation-and-tome-decomposition)
- [2. Encoded laws and operators](#2-encoded-laws-and-operators)
  - [2.1 Interference law](#21-interference-law)
  - [2.2 Quadrature / boxplus operator ⊞](#22-quadrature--boxplus-operator-)
  - [2.3 Pivot equation](#23-pivot-equation)
  - [2.4 Gateway algebra](#24-gateway-algebra)
  - [2.5 OICF emergence coordinates](#25-oicf-emergence-coordinates)
  - [2.6 Crystal Merge protocol CM0→CM6](#26-crystal-merge-protocol-cm0cm6)
- [3. The invariant spine](#3-the-invariant-spine)
- [4. Proof-carrying computation kernel](#4-proof-carrying-computation-kernel)
- [5. Memory bank](#5-memory-bank)
- [6. Atlas façade](#6-atlas-façade)
- [7. Workflows](#7-workflows)
- [8. Extending AtlasForge](#8-extending-atlasforge)
- [9. Appendix](#9-appendix)

---

# 0. Orientation

AtlasForge is best understood as a **compiler** and an **atlas**:

- **Compiler:** You feed in a *seed* (a problem specification). The system expands it deterministically into a *recipe* (a computation trace), plus **certificates** that justify the output.
- **Atlas:** You store the outputs and the concepts as **content-addressed entries**, link them via dependencies, and export them into a coherent “book”.

### What AtlasForge is *not*
- It is not a single-purpose numerical library.
- It is not a theorem prover (yet). It carries **evidence levels** (L0–L3) and supports certified numerical enclosures (L2) even when full formal proof (L3) is not present.

### The central promise
> If you can state the constraint, AtlasForge can produce a replayable artifact and attach verifiable evidence.

---

# 1. Universal Harmonic Framework

The Universal Harmonic Framework (UHF) is an **encoded address space** for mathematical work:

- **4 poles** × **4 lenses** × **4 layers** × **4 depths** = **256 crystal cells**
- Every object, operator, invariant, or certificate can be assigned an address in that crystal.

The UHF exists so that:
- you can *retrieve by structure* (not only by keyword),
- multiple representations of the same object can co-exist and be navigated,
- “deep work” can be organized into a stable taxonomy.

In code, the canonical UHF enums live in:

- `atlasforge.Pole` (glyph poles D, Ω, Σ, Ψ)
- `atlasforge.Lens` (□, ✿, ☁, ❋)
- `atlasforge.Layer` (OBJECTS / OPERATORS / INVARIANTS / CERTIFICATES)
- `atlasforge.Depth` (0–3)
- `atlasforge.CrystalAddress`

---

## 1.1 The four poles

In UHF, a “pole” is the **realm** you are operating in.

```
                              Ψ (Air/Λ)
                                    │
                                    │
        D (Earth/α) ────────────────┼────────────── Ω (Water/𝔇)
                                    │
                                    │
                              Σ (Fire/Θ)
```

| Meta pole | Glyph | Archetype | UHF meaning |
|---|---:|---|---|
| Discrete | **D** | Earth / α | counting, lattices, integers, combinatorics |
| Continuous | **Ω** | Water / 𝔇 | flow, limits, analysis, geometry |
| Stochastic | **Σ** | Fire / Θ | probability, measurement, uncertainty |
| Hierarchical | **Ψ** | Air / Λ | recursion, emergence, renormalization |

These are encoded in `atlasforge.Pole`:

```python
from atlasforge import Pole
Pole.DISCRETE.value      # "D"
Pole.CONTINUOUS.value    # "Ω"
Pole.STOCHASTIC.value    # "Σ"
Pole.HIERARCHICAL.value  # "Ψ"
```

---

## 1.2 The four lenses

A “lens” is a **viewing mode**: how you choose to represent and interrogate an object.

| Lens | Glyph | Core idea |
|---|---:|---|
| Square | □ | structural / static / invariants / discrete scaffolding |
| Flower | ✿ | cyclic / phase / transport / dynamics |
| Cloud | ☁ | probabilistic / bounds / uncertainty / distributions |
| Fractal | ❋ | recursion / multiscale / self-similarity |

In code:

```python
from atlasforge import Lens
Lens.SQUARE.value   # "□"
Lens.FLOWER.value   # "✿"
Lens.CLOUD.value    # "☁"
Lens.FRACTAL.value  # "❋"
```

A useful integration principle:

- **Square** tends to generate **IR, normal forms, proofs as data**
- **Flower** tends to generate **transforms / coordinate transport**
- **Cloud** tends to generate **bounds, distributions, uncertainty propagation**
- **Fractal** tends to generate **search, recursion, bracketing, multiscale refinement**

---

## 1.3 Layers and depths

UHF treats each crystal cell as one of four “layers”:

| Layer | Enum | Meaning |
|---|---:|---|
| Objects | `Layer.OBJECTS (0)` | what exists |
| Operators | `Layer.OPERATORS (1)` | what transforms |
| Invariants | `Layer.INVARIANTS (2)` | what stays true across transformations |
| Certificates | `Layer.CERTIFICATES (3)` | what justifies a claim |

Depth is a 0–3 index describing how far “into” a layer you are:
- **0:** surface / direct / definition-level
- **1:** derived / composed
- **2:** canonicalized / normalized
- **3:** certified / stabilized / “publication-ready”

Depth is intentionally lightweight: it is a *navigation axis*, not a hard theorem.

---

## 1.4 Crystal address and linear index

A crystal address is:

```
Pole · Lens · Layer · Depth
```

In code:

```python
from atlasforge import CrystalAddress, Pole, Lens, Layer, Depth
addr = CrystalAddress(Pole.CONTINUOUS, Lens.SQUARE, Layer.INVARIANTS, Depth.D2)
print(str(addr))            # Ω·□·INVARIANTS·2
print(addr.to_index())      # 0..255
```

The linear index mapping is:

```
index = pole_index * 64 + lens_index * 16 + layer_value * 4 + depth_value
```

This is the bridge between:
- human readable addresses (`Ω·□·INVARIANTS·2`)
- a compact integer cell id (`0..255`)
- navigation and indexing (MemoryStore uses `extra["crystal_index"]`)

### Address parsing (Memory Bank)
The memory subsystem can parse best-effort address strings:

- `"D·□·OBJECTS·0"`
- `"Ω·✿·OPERATORS·2"`
- `"Σ·☁·INVARIANTS·1"`
- `"12"` (treated as a raw index)

See: `atlasforge.memory.addressing.parse_crystal_address_string`.

---

## 1.5 Meta poles vs operational poles

**Important integration point.**  
AtlasForge contains *two pole systems* with the same word “Pole”:

### (A) Meta poles (UHF)
- `atlasforge.Pole`
- values are glyphs: `"D", "Ω", "Σ", "Ψ"`
- used for **classification / navigation / memory indexing**

### (B) Operational poles (solver/simplex theory)
- `atlasforge.core.enums.Pole`
- values are descriptive: `"dissipative", "oscillatory", "stochastic", "recursive"`
- used for **algorithmic behavior** and “operator simplex” mixing

Think of it like:

- Meta poles answer **“what realm am I describing?”**
- Operational poles answer **“what dynamical mode does this operator express?”**

This split is intentional and is one of the cleanest ways to preserve both:
- symbolic/glyph indexing (human navigation)
- behavioral mode semantics (solver policy)

---

## 1.6 Master equation and tome decomposition

AtlasForge’s doc layer uses a “master equation” as a **module decomposition**.

From the framework banner:

```
S = (T,Ψ,Σ,C,D;Ω) + AQM[ρ,Φ,J,Λ,K] + LM[D,R,C,T,P] + QCM[Θ,Λ] + PROOF[Σ,C,V]
```

Interpretation:
- The **core scaffold** `(T,Ψ,Σ,C,D;Ω)` is the universal structure.
- AQM is the quantum-number “extended arithmetic” scaffold.
- LM is the liminal/emergence/closure scaffold.
- QCM is the Θ–Λ interference / cyclotomic scaffold.
- PROOF is the certificate/verification scaffold.

This is not a single formula to “compute”; it is a **map** of the books.

---

# 2. Encoded laws and operators

This section preserves the **encoded mathematical identities** that act as the “mnemonic spine” for the framework.

---

## 2.1 Interference law

In `atlasforge.qcm.qcm`, the master law is:

```
|ψ₁ + ψ₂|² = a² + b² + 2ab·cos(Δθ)
```

Interpretation:
- amplitudes `a, b`
- phase separation `Δθ`
- interference term `2ab cos(Δθ)`

Key special cases:

1. **Constructive** `Δθ = 0`  
   `|ψ₁ + ψ₂|² = (a + b)²`

2. **Destructive** `Δθ = π`  
   `|ψ₁ + ψ₂|² = (a - b)²`

3. **Orthogonal** `Δθ = π/2`  
   `|ψ₁ + ψ₂|² = a² + b²`

That orthogonal case is where the ⊞ operator arises.

---

## 2.2 Quadrature / boxplus operator ⊞

Your “compression operator” is:

```
a ⊞ b := √(a² + b²)
```

It is:
- the orthogonal slice of interference
- a Pythagorean addition law
- a stable “quadrature merge” operator

In code, this is exposed via QCM’s `InterferenceLaw.quadrature(...)`:

```python
from atlasforge.qcm.qcm import InterferenceLaw
InterferenceLaw.quadrature(3, 4)  # 5.0
```

---

## 2.3 Pivot equation

AtlasForge encodes a commutator-like pivot identity:

```
∂∫ − ∫∂ = Ω
```

Read as:
- EXPAND then COMPRESS ≠ COMPRESS then EXPAND
- the “non-commutativity residue” is recursion/looping (**Ω**)

This is captured in Crystal Merge / meta-operation discussions and is used as a conceptual engine for:
- normal forms (Square lens)
- recursion (Fractal lens)
- tunneling between representations (Flower ↔ Fractal)

---

## 2.4 Gateway algebra

The Gateway subsystem (`atlasforge.gateway.gateway`) formalizes hyperbolic/SL(2,R) scale transport:

- Gateway scalar `T ∈ (-1,1)`
- Scale ratio `R = (1+T)/(1-T) > 0`
- Rapidity `α = artanh(T) = (1/2) ln(R)`
- Boost matrix `B(T) ∈ SL(2,ℝ)`

Key idea:
- composing gateways uses velocity-addition / hyperbolic composition rules
- this creates a stable calculus for **calibrated scale changes**

---

## 2.5 OICF emergence coordinates

Emergence is indexed by the OICF coordinates (in code: `atlasforge.EmergenceCoordinates`):

| Coordinate | Symbol | Meaning |
|---|---:|---|
| Omega | Ω | viability / margin-to-failure |
| Iota | ι | integration / coupling |
| Chi | χ | coherence / cross-scale consistency |
| Phi | φ | function / goal-directedness |

Emergence potential:

```
E = Ω · I · C · F
```

This gives the framework an explicit numeric axis for “how emergent is this system?”, and it’s used in LM/Tower reasoning.

---

## 2.6 Crystal Merge protocol CM0→CM6

The Crystal Merge protocol (`atlasforge.crystal_merge.crystal_merge`) is a **problem-solving compiler** with stages:

- **CM0:** Z* Core Lock — no leaks, define objects and degeneracy
- **CM1:** Four-Lens Parallel Zoom — □ ✿ ☁ ❋ in parallel
- **CM2:** S-Tier Pivot — tunneling / representation swap
- **CM3:** Math God Finish — master equation collapse
- **CM4:** Meta-Duality Discovery — higher structure
- **CM5:** Proof Packaging — bundle certificates into proof packs
- **CM6:** Publication Gate — final verification and release

In practice, the kernel implements CM5/CM6 as:
- `CertificateBundle` + `ProofPack`
- `Verifier` enforcement + truth profile gating
- replay + content-addressed storage

---

# 3. The invariant spine

AtlasForge’s stable integration axis is the **Invariant Spine**:

> **Ledger · Corridor · Proof · Replay**

This exists explicitly as `atlasforge.core.enums.InvariantSpineComponent`.

### LEDGER — irreversible history
- content-addressed artifacts
- append-only mindset (even if stored on disk as files)
- reproducibility is the primitive, not “state”

Implemented via:
- `core.base.ContentAddressed`
- registry skeleton in `registry/`

### CORRIDOR — admissibility constraints
- domains, intervals, chart constraints
- any solution must remain in its corridor

Implemented via:
- `core.types.Interval` and domains
- chart/lens transport (`lenses/`)
- `CorridorCertificate`

### PROOF — evidence for correctness
- L0 claim
- L1 empirical
- L2 certified numeric
- L3 formal

Implemented via:
- `certificates/`
- `verifier/`
- `core.enums.CertificateLevel`, `TruthProfile`

### REPLAY — deterministic re-derivation
- the computation log is part of the artifact identity
- results are replayable under the same seed/plan

Implemented via:
- `recipes/ReplayLog`
- `ReplayCertificate`

---

# 4. Proof-carrying computation kernel

The kernel is the “compiler backend”. It transforms:

> **Blueprint → IR → Normal Form → SolvePlan → Solver → Output → Certificates → Verification**

Key modules:

- `atlasforge.core` — content addressing, canonical hashing, types
- `atlasforge.constraints` — constraint objects + IR lowering
- `atlasforge.recipes` — Blueprint/SolvePlan/Recipe/Executor
- `atlasforge.certificates` — certificate types, bundles, proof packs
- `atlasforge.verifier` — validation and enclosure verification
- `atlasforge.registry` — content store skeleton

---

## 4.1 Core types

### Interval
`atlasforge.core.types.Interval` is the corridor primitive:

- closed/open bounds
- containment checks
- intersection
- conservative operations used by certified verification

Example:

```python
from atlasforge import Interval
I = Interval.closed(1,2)
I.contains(1.5)  # True
```

---

## 4.2 Constraints and IR

Constraints capture “what is to be solved”.

Example: root finding:

```python
from atlasforge import RootConstraint, Interval
c = RootConstraint(H=lambda x: x*x - 2, domain=Interval.closed(1,2))
```

Lowering pipeline:
- `Constraint` → `ConstraintIR`
- `ConstraintIR.normal_form` → `NormalForm` object used by solvers

This enables multiple constraints to share a uniform solver interface.

---

## 4.3 Solvers (and auto-bracketing)

Solvers include:
- Brent (robust bracketed root finder)
- Bisection
- Newton / Secant
- Interval Newton (certifying enclosure)

Bracketing is often the missing ingredient. AtlasForge includes a practical “Fractal lens” bracketer:

- `atlasforge.constraints.bracketing.find_bracket`

If `SolvePlan.auto_bracket=True` the executor will:
1) attempt solve
2) if it fails, search for a sign-change bracket
3) re-run Brent on the bracket
4) store metadata explaining what happened

---

## 4.4 Recipe artifacts and replay

`Recipe` is the artifact:
- blueprint (seed)
- plan (compiler flags)
- output (solution/enclosure/metadata)
- replay log (deterministic trace)
- proof pack (bundled certificates)

This makes results **portable and verifiable**.

---

## 4.5 Certificates and proof packs

Certificates live in `atlasforge.certificates.certificate`.

Core types:

- `EnclosureCertificate`
- `UniquenessCertificate`
- `CorridorCertificate`
- `ReplayCertificate`
- `StabilityCertificate`
- `CertificateBundle`
- `ProofPack`

A `CertificateBundle` is the authoritative container:
- stores certificates by type
- tracks evidence level
- can be verified

A `ProofPack` is the “publication-ready wrapper”:
- binds `result_hash` to the bundle
- ensures consistency and completeness

---

## 4.6 Verification

Verification is not monolithic; AtlasForge supports layered verification:

- **Validator** (basic plausibility checks)
- **EnclosureVerifier** (interval Newton enclosure)
- **CrossValidator** (multi-check policies)
- **Kernel verifier** (ties recipe + proof pack + replay together)

Evidence levels are enforced via `TruthProfile`:
- `EXPLORE`: store candidates, no promotion
- `VALIDATE`: empirical checks
- `PROVE`: requires L2+ for obligations

---



## 4.7 The Tome Library

Beyond the kernel, AtlasForge contains a large set of **domain tomes**.  
Think of these as *mathematical books* that share the UHF encoding, even when they are not all wired into the recipe pipeline.

The most “encoded frameworks” (the ones that carry your mathematical doctrine) are:

- **AQM** (Axiomatic Quantum Mathematics): Q-numbers, meaning transport, kernel closure  
- **LM** (Liminal Mathematics / Tower): regimes, frames, desire, closure and emergence  
- **QCM** (Quadrature–Cyclotomic Manifold): Θ–Λ plane, interference, cyclotomics, bridges  
- **Gateway**: SL(2,ℝ) hyperbolic navigation of scale  
- **Crystal Merge**: CM0→CM6 problem-solving compiler  
- **Proof Engine**: a parallel (heavier) proof scaffolding

The kernel + memory atlas layer are designed to **absorb** these tomes over time: you can already store and link their results today, even when their internal types are not fully normalized to the kernel’s IR.

---

### 4.7.1 QCM — Quadrature–Cyclotomic Manifold (Θ–Λ)

**File:** `atlasforge/qcm/qcm.py`  
**Core theme:** phase (Θ) + lattice (Λ) + bridges between them.

Key classes:
- `ThetaScalar`, `ThetaVector` — complex amplitudes and their phase geometry  
- `LambdaIndex`, `LambdaPattern` — discrete phase lattice structures  
- `RotationOperator` — phase rotation
- `InterferenceLaw` — the master law, plus derived operations like quadrature
- `CyclotomicPhases`, `CyclicGroup` — discrete phase structure
- Bridges:
  - `AmpMeasBridge` (amplitude → measurement)
  - `QuantizeBridge` (continuous → discrete)
  - `FourierGearbox` (phase ↔ frequency representations)
- `QCMEngine` — orchestration / “engine object”

Minimal example:

```python
from atlasforge.qcm.qcm import ThetaScalar, InterferenceLaw

ψ1 = ThetaScalar.from_polar(3.0, 0.0)      # 3·e^{i·0}
ψ2 = ThetaScalar.from_polar(4.0, 1.57)     # 4·e^{i·π/2} approx

# Orthogonal interference slice → Pythagorean / ⊞ merge
q = InterferenceLaw.quadrature(ψ1.magnitude, ψ2.magnitude)  # 5.0
```

---

### 4.7.2 Gateway — SL(2,ℝ) hyperbolic scale transport

**File:** `atlasforge/gateway/gateway.py`  
**Core theme:** *calibrated scale ratios* encoded as bounded hyperbolic coordinates.

Key objects:
- `GatewayScalar(T)` with `T ∈ (-1,1)`  
- `BoostMatrix` representing an SL(2,ℝ) “hyperbolic rotation”
- `PellGateway`, `PellSolution` — discrete/calibrated gateways from Pell orbits
- `velocity_addition`, `rapidity_from_velocity`, `velocity_from_rapidity`

Typical use is to treat “scale change” as **composition**, not ad-hoc multiplication.

---

### 4.7.3 Crystal Merge — CM0→CM6 compiler stages

**File:** `atlasforge/crystal_merge/crystal_merge.py`

Key encoded objects:
- `MetaOperation`:  
  - EXPAND `∂`  
  - COMPRESS `∫`  
  - RECURSE `Ω`  
  - EQUILIBRATE `Φ`
- `FundamentalProcess`: 16 processes (constants × operations)
- `CrystalMergeProtocol`: runs CM0…CM6

The key integration is: **CM5/CM6 correspond to proof packaging and publication**, which the kernel implements as:
- certificate bundles (`CertificateBundle`)
- proof packs (`ProofPack`)
- verifier policies (`TruthProfile`)

---

### 4.7.4 AQM — Axiomatic Quantum Mathematics (Tomes I–V)

AQM is the framework for treating “numbers” as **quantum states** rather than points.

**Tome map (implementation modules):**
- Tome I: `aqm_foundation` — Q-numbers on the Riemann sphere, meaning transport, classical shadows  
- Tome II: `aqm_arithmetic` — arithmetic on Q-numbers  
- Tome III: `aqm_realization` — bridges to classical structures  
- Tome IV: `aqm_kernel` — infinite-resolution kernel closure  
- Tome V: `aqm_liminal` — liminal corridor / emergence interface  
- Bridges: `aqm_integration`, `aqm_synthesis`

**Encoded definitions (from AQM foundation):**
- Value space: **Riemann sphere** `Ĉ = ℂ ∪ {∞}`
- Q-number: **state** `ρ` on `H = L²(Ĉ, μ)`
- Classical shadow: measurement → probability distribution
- Inversion duality: `J(z) = 1/z` (near ↔ far)
- Scale symmetry: `z ↦ λz`

Key classes in `aqm_foundation`:
- `RiemannSphere`
- `QNumber` (with constructors like `QNumber.classical(z, sigma=...)`)
- `MeaningTransport`
- `POVM`, `ClassicalShadow`
- `QNumberNormalForm`
- `CorridorConstraint`

Minimal “classical limit” example:

```python
from atlasforge.aqm_foundation.aqm_foundation import QNumber

ρ = QNumber.classical(1+0j, sigma=0.01)   # “almost scalar”
print(ρ.center)                           # classical shadow center
```

**Integration note:** AQM tomes define their own crystal enums (`CrystalLens`, `CrystalLayer`, …).  
The memory atlas layer can still store AQM results using the global UHF address space.

---

### 4.7.5 LM — Liminal Mathematics / The Tower (Tomes I–V)

LM is the emergence/closure doctrine: how “objects that enforce persistence rules” arise.

**Tome map:**
- Tome I: `lm_foundations`
- Tome II: `lm_dynamics`
- Tome III: `lm_mechanization`
- Tome IV: `lm_renormalization`
- Tome V: `lm_tower`
- Bridge: `lm_synthesis`

Key thesis (as encoded in `lm_tower` docstring):
> Life/Agency/Sentience is a topological inversion of control: persistence rules migrate inward.

Key classes in `lm_tower`:
- `Frame` (Q, Pred, Sem)
- `Regime`, `Individual`
- `LiminalStateSpace`, `LiftOperator`
- `DesireOperator` (lookahead / closure operator)
- `FeasibilityLandscape`, `MiracleEvent`
- `ClosureMetrics` (Ω, ι, χ, φ)

Minimal closure metrics example:

```python
from atlasforge.lm_tower.lm_tower import ClosureMetrics
m = ClosureMetrics(omega=0.8, iota=0.7, chi=0.5, phi=0.9)
print(m.closure_potential)  # Ω·I·C·F
```

---

### 4.7.6 Proof Engine (parallel proof scaffold)

**File:** `atlasforge/proof_engine/proof_engine.py`

This subsystem defines a heavier proof apparatus:
- seeds, constraint IR, environment fingerprints
- replay transcripts and procedures
- proof standards, publishable artifacts

The kernel certificate system (`atlasforge.certificates`) is the lightweight path currently integrated into `RecipeExecutor`.  
The proof engine can be treated as an upstream “formal layer” that can later replace or enrich certificate bundles (L3).



# 5. Memory bank

The memory subsystem turns AtlasForge into a real “math memory bank”:

- store structured knowledge (definition/lemma/theorem/operator/identity/…)
- attach crystal addresses and tags
- search quickly (SQLite FTS when available)
- link dependencies as a graph
- group work into sessions
- export into books (Markdown/PDF/DOCX/LaTeX)

Key modules:

- `atlasforge.memory.entry` — `MemoryEntry`
- `atlasforge.memory.knowledge` — `KnowledgeRecord`, `KnowledgeKind`
- `atlasforge.memory.store` — `MemoryStore`
- `atlasforge.memory.index` — `MemoryIndex` + hits
- `atlasforge.memory.graph` — `GraphStore`
- `atlasforge.memory.session` — `SessionStore`
- `atlasforge.memory.bootstrap` — seed entries

---

## 5.1 MemoryEntry schema

A `MemoryEntry` is stored as JSON:

```json
{
  "title": "Interference law",
  "content": "...markdown...",
  "tags": ["qcm", "identity", "kind:identity"],
  "links": {"recipe": "<hash>", "proof_pack": "<hash>"},
  "extra": {"crystal_address": "Σ·✿·INVARIANTS·1", "crystal_index": 123}
}
```

Entries are content-addressed:
- identical content → identical hash
- hash is stable across machines

---

## 5.2 Structured knowledge (KnowledgeRecord)

`KnowledgeRecord` is a thin schema that compiles to `MemoryEntry`.

Kinds include:
- definition
- lemma
- theorem
- identity
- operator
- proof
- derivation
- note

Convenience methods exist on `MemoryStore` and `Atlas`:

```python
from atlasforge import Atlas
atlas = Atlas.from_env()

h = atlas.identity(
    title="Quadrature",
    statement="a ⊞ b := √(a² + b²)",
    tags=["qcm","operator"],
    address="Σ·✿·OPERATORS·0"
)
```

Dependencies become graph edges automatically:
- `depends_on` → `depends_on` edge
- `see_also` → `see_also` edge
- `links` → `link:<key>` edges

---

## 5.3 Index, graph, and sessions

- **Index:** keyword search (SQLite FTS5 if available)  
  `store.search("Newton", tags=[...], kinds=[...])`

- **Graph:** explicit edges between entries, recipes, and artifacts  
  `store.graph.add_edge(...)` and automatic edges from dependencies

- **Sessions:** group a working day into a record  
  `with store.session("January 1 — verification") as sess: ...`

---

## 5.4 Bootstrap seed entries

On first use, the memory bank seeds core framework anchors (unless `ATLASFORGE_NO_BOOTSTRAP=1`), including:

- Interference law (identity)
- ⊞ quadrature operator (operator)
- Pivot equation (identity)
- Invariant spine (definition)
- CM0→CM6 protocol (definition)
- OICF coordinates (definition)

These ensure a new memory directory immediately contains the “spine” of your framework.

---

# 6. Atlas façade

`Atlas` is the high-level façade that binds:

- the kernel executor
- the memory store
- sessions and linking
- book export and crystal navigation

It is the simplest way to operate AtlasForge as “the full understanding of our math”.

---

## 6.1 Configuration

```python
from atlasforge import Atlas, AtlasConfig
atlas = Atlas(AtlasConfig(memory_dir="~/.atlasforge_memory"))
```

Or via environment variable:

```bash
export ATLASFORGE_MEMORY_DIR=~/.atlasforge_memory
```

Then:

```python
atlas = Atlas.from_env()
```

---

## 6.2 Solve + remember

```python
from atlasforge import RootConstraint, Interval

bp = atlas.blueprint(
    name="sqrt(2)",
    constraint=RootConstraint(H=lambda x: x*x - 2, domain=Interval.closed(1,2))
)

recipe = atlas.solve(bp, verified=True, note="Certified by interval Newton enclosure.")
```

If memory is configured, the solve will automatically log:
- a recipe memory entry
- links to blueprint/output hashes
- verification metadata

---

## 6.3 Recall + crystal navigation

Keyword recall:

```python
hits = atlas.recall("interference", tags=["qcm"])
```

Crystal navigation:

```python
from atlasforge import CrystalNavigator
nav = CrystalNavigator(atlas.store)
cell = nav.cell("Σ·✿·OPERATORS·0")
```

---

## 6.4 Exporting your atlas as a book

```python
atlas.export_book(
    "my_atlas.pdf",
    title="My Math Atlas",
    fmt="pdf",
    include_crystal_map=True,
    include_graph_edges=True
)
```

Export only a theorem packet + dependencies:

```python
atlas.export_book(
    "packet.tex",
    fmt="tex",
    roots=[theorem_hash],
    include_dependencies=True,
    dependency_relations=["depends_on"]
)
```

---

# 7. Workflows

This section describes recommended “operating modes”.

---

## 7.1 Explore → Validate → Prove

Use `TruthProfile` as your mental switch:

- **EXPLORE**  
  store conjectures and computational candidates; do not promote.

- **VALIDATE**  
  require empirical checks and replay.

- **PROVE**  
  require L2 certified evidence for obligations; enforce corridor + enclosure.

This is the bridge between:
- research notebook
- publishable artifact

---

## 7.2 Encode everything twice: artifact + meaning

Best practice in AtlasForge:

1. Run a recipe to compute a result (artifact)
2. Store a knowledge entry that states *what it means* (meaning)
3. Link them (dependency graph / links)

This creates an “executable textbook”:
- the book reads like math
- but every claim has a trail to computations and certificates

---

## 7.3 Use crystal addresses deliberately

When you store something, assign:

- pole: the realm
- lens: how it’s represented
- layer: object/operator/invariant/certificate
- depth: maturity

This is how your memory bank becomes an atlas rather than a pile of notes.

---

# 8. Extending AtlasForge

AtlasForge is designed to grow by adding modules that attach to the spine.

---

## 8.1 Add a new constraint
- subclass `Constraint`
- implement lowering to `ConstraintIR`
- define normal form expectations

---

## 8.2 Add a new solver
- implement a `solve(...)` method that consumes a normal form
- register in the solver factory / plan

---

## 8.3 Add a new certificate
- subclass `Certificate`
- implement `verify()`
- register with `CertificateFactory`

---

## 8.4 Add a new lens/chart
- implement forward/inverse coordinate maps
- define corridor admissibility
- let `Blueprint.chart` transport the solve

---

## 8.5 Add a new knowledge kind
- extend `KnowledgeKind`
- render it as a book section in `AtlasBookBuilder`

---

# 9. Appendix

## 9.1 Key entry points

- Kernel: `atlasforge.recipes.recipe.RecipeExecutor`
- Memory: `atlasforge.memory.store.MemoryStore`
- Atlas façade: `atlasforge.atlas.atlas.Atlas`
- Book compiler: `atlasforge.atlas.book.AtlasBookBuilder`
- Crystal navigation: `atlasforge.atlas.navigator.CrystalNavigator`

## 9.2 Directory map (selected)

| Package | Role |
|---|---|
| `core/` | content addressing, types, enums |
| `constraints/` | constraint definitions, solvers, bracketing |
| `recipes/` | artifact compiler pipeline |
| `certificates/` | certificates + proof packs |
| `verifier/` | validation + enclosure verification |
| `memory/` | memory bank (entries/index/graph/sessions) |
| `atlas/` | solve+remember façade, navigation, book export |
| `qcm/` | Θ–Λ interference / cyclotomic scaffold |
| `gateway/` | SL(2,R) scale transport / rapidity |
| `crystal_merge/` | CM0→CM6 protocol and meta-ops |
| `aqm_*` | AQM tomes (quantum-number arithmetic) |
| `lm_*` / `lm_tower/` | LM tomes (liminal tower / emergence / closure) |
| `proof_engine/` + `proofs/` | larger proof scaffolding (conceptual / partial integration) |

## 9.3 Glossary (micro)

- **Seed:** minimal representation of an object/problem sufficient to regenerate it
- **Corridor:** admissible domain constraints for a solve
- **Enclosure:** interval guaranteed to contain the true solution
- **Certificate:** machine-checkable evidence object
- **ProofPack:** bundle of certificates bound to a result hash
- **Crystal cell:** one of the 256 Pole×Lens×Layer×Depth addresses

---



## 9.4 Kernel artifact schemas (dataclass fields)

These are the “shape contracts” you can rely on when scripting AtlasForge.

### Blueprint (`atlasforge.recipes.recipe.Blueprint`)
- `constraint: Optional[Constraint]` — the mathematical condition
- `chart: Optional[Chart]` — optional coordinate transport (lens)
- `truth_profile: TruthProfile` — EXPLORE / VALIDATE / PROVE
- `search_domain: Optional[Interval]` — optional override domain
- `hints: Dict[str, Any]` — solver hints / metadata
- `name: str` — human name
- `description: str` — human description

### SolvePlan (`atlasforge.recipes.recipe.SolvePlan`)
- `primary_solver: SolverType` (default: BRENT)
- `fallback_solvers: List[SolverType]`
- `tolerance: float`
- `max_iterations: int`
- Auto-bracketing:
  - `auto_bracket: bool`
  - `bracket_samples: int`
  - `bracket_expand_steps: int`
  - `bracket_expand_factor: float`
- Verification:
  - `verify_solution: bool`
  - `verification_solver: SolverType` (default: INTERVAL_NEWTON)
- Numerical policy:
  - `float_policy: FloatPolicy`
- Bookkeeping:
  - `status: PlanStatus`
  - `metadata: Dict[str, Any]`

### RecipeOutput (`atlasforge.recipes.recipe.RecipeOutput`)
- `solution: Optional[float]`
- `residual: float`
- `enclosure: Optional[Interval]` (certifying corridor)
- `all_solutions: List[float]`
- `solver_result: Optional[SolverResult]`
- `certificates: CertificateBundle`
- `success: bool`
- `verified: bool`
- `solve_time: float`
- `metadata: Dict[str, Any]`

### Recipe (`atlasforge.recipes.recipe.Recipe`)
- `blueprint: Optional[Blueprint]`
- `plan: Optional[SolvePlan]`
- `output: Optional[RecipeOutput]`
- `replay_log: Optional[ReplayLog]`
- `proof_pack: Optional[ProofPack]`
- `created_at: datetime`
- `complete: bool`

---

## 9.5 Certificate types (what they mean)

Certificate classes live in `atlasforge.certificates.certificate`:

- **EnclosureCertificate**  
  Verifies that the returned `solution` lies in a conservative `Interval` enclosure and that the enclosure is valid.

- **UniquenessCertificate**  
  Captures a sufficient condition that there is only one solution in the corridor.

- **CorridorCertificate**  
  Captures domain admissibility: the solution respects the corridor constraints.

- **ReplayCertificate**  
  Ensures the computation can be deterministically replayed and that a replay run matches the recorded result hash.

- **StabilityCertificate**  
  Captures local stability (e.g., contraction criteria).

- **CertificateBundle**  
  Container (with evidence level) that stores and verifies certificates.

- **ProofPack**  
  Publication-ready wrapper binding a `result_hash` to a `CertificateBundle`.

---

## 9.6 Recommended crystal conventions (practical)

These are conventions (not hard requirements) that make crystal navigation consistent:

- **QCM**
  - interference identities → `Σ·✿·INVARIANTS·{0..2}`
  - phase lattice objects → `Ψ·✿·OBJECTS·{0..2}`
  - bridges (Amp/Meas/Fourier) → `Ω·✿·OPERATORS·{1..3}`

- **Gateway**
  - gateway scalars / boosts → `Ω·✿·OPERATORS·0`
  - invariants / calibration identities → `Ω·□·INVARIANTS·{1..3}`

- **AQM**
  - Q-number objects → `Ω·☁·OBJECTS·{0..2}`
  - meaning transport operators → `Ω·✿·OPERATORS·{0..2}`
  - classical shadows / measurement invariants → `Σ·☁·INVARIANTS·{0..2}`

- **LM**
  - frames/regimes/state spaces → `Ψ·□·OBJECTS·{0..2}`
  - desire/lookahead operators → `Ψ·❋·OPERATORS·{1..3}`
  - closure metrics / OICF invariants → `Ψ·☁·INVARIANTS·{0..2}`

- **Kernel / Proof**
  - solver outputs → `D·□·CERTIFICATES·{1..3}`
  - replay/cert bundles → `D·□·CERTIFICATES·3`

The best workflow is:
1) start with “reasonable” assignments,  
2) refine as your atlas grows,  
3) rely on dependency edges + tags to keep everything searchable during refactors.



_End of manual._
