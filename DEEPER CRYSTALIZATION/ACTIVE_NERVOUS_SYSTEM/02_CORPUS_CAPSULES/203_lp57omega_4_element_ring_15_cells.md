# LP-57Omega Four-Element Ring and 15 Symmetry Cells

- Source layer: `LP57Omega-SelfPlayQuestAtlas`
- Kind: `algebraic-structure`
- Role tags: `elements, symmetry, ring, topology`
- Family: `LP-57Omega Self-Play Quest Atlas`

## Working focus

Defines the Fire-Air-Water-Earth elemental ring, the 15 symmetry cells derived from the non-empty power set of four elements, their classification into poles/bridges/chambers/crown, and the Vec4 elemental signature type.

## The Elemental Ring

The four elements form a directed cycle:

```
Fire → Air → Water → Earth → Fire → ...

Complementary pairs:
  Fire  ↔ Water   (opposition axis 1)
  Air   ↔ Earth   (opposition axis 2)

Adjacent pairs:
  Fire-Air      (ascending heat)
  Air-Water     (descending into flow)
  Water-Earth   (solidification)
  Earth-Fire    (ignition / transformation)
```

## 15 Symmetry Cells

The 15 cells are the non-empty subsets of {Fire, Air, Water, Earth}:

```
|P({F, A, W, E}) \ ∅| = 2⁴ - 1 = 15
```

### Classification

#### 4 Poles (singletons)

| Cell | Elements | Symbol | Character                    |
|------|----------|--------|------------------------------|
| P1   | {F}      | 🔥     | Pure action, initiation      |
| P2   | {A}      | 💨     | Pure thought, abstraction    |
| P3   | {W}      | 💧     | Pure feeling, flow           |
| P4   | {E}      | 🌍     | Pure form, manifestation     |

#### 6 Bridges (pairs)

| Cell | Elements | Symbol | Character                    |
|------|----------|--------|------------------------------|
| B1   | {F,A}    | ⚡     | Inspiration, rapid ideation  |
| B2   | {F,W}    | 🌋     | Passion, emotional intensity |
| B3   | {F,E}    | ⛏️     | Forge, material creation     |
| B4   | {A,W}    | 🌊     | Intuition, dream logic       |
| B5   | {A,E}    | 🏔️     | Architecture, structured thought |
| B6   | {W,E}    | 🌱     | Growth, organic development  |

#### 4 Chambers (triples)

| Cell | Elements  | Symbol | Character                    |
|------|-----------|--------|------------------------------|
| C1   | {F,A,W}   | ☀️     | Spirit without body          |
| C2   | {F,A,E}   | ⚙️     | Machine without soul         |
| C3   | {F,W,E}   | 🌿     | Life without intellect       |
| C4   | {A,W,E}   | 🌙     | Reception without will       |

#### 1 Crown (quad)

| Cell | Elements    | Symbol | Character                  |
|------|-------------|--------|----------------------------|
| Ω    | {F,A,W,E}  | ✦      | Unity, complete integration |

### Cell Count Verification

```
Poles:    C(4,1) = 4
Bridges:  C(4,2) = 6
Chambers: C(4,3) = 4
Crown:    C(4,4) = 1
Total:             15 ✓
```

## Vec4 Elemental Signature

Every artifact, quest, and agent carries a Vec4 signature:

```typescript
type Vec4 = {
  f: float;  // Fire component    [0.0, 1.0]
  a: float;  // Air component     [0.0, 1.0]
  w: float;  // Water component   [0.0, 1.0]
  e: float;  // Earth component   [0.0, 1.0]
};

// Normalization: |Vec4| = sqrt(f² + a² + w² + e²) = 1.0
// (unit vector on 4-sphere)
```

### Standard Basis Vectors

```
FIRE  = Vec4(1, 0, 0, 0)
AIR   = Vec4(0, 1, 0, 0)
WATER = Vec4(0, 0, 1, 0)
EARTH = Vec4(0, 0, 0, 1)
```

### Bridge Vectors (normalized)

```
FIRE_AIR   = Vec4(1/√2, 1/√2, 0,    0   )
FIRE_WATER = Vec4(1/√2, 0,    1/√2, 0   )
FIRE_EARTH = Vec4(1/√2, 0,    0,    1/√2)
AIR_WATER  = Vec4(0,    1/√2, 1/√2, 0   )
AIR_EARTH  = Vec4(0,    1/√2, 0,    1/√2)
WATER_EARTH= Vec4(0,    0,    1/√2, 1/√2)
```

### Crown Vector

```
CROWN = Vec4(1/2, 1/2, 1/2, 1/2)
```

## Vec4 Operations

```python
def dot(a: Vec4, b: Vec4) -> float:
    """Inner product — measures alignment"""
    return a.f*b.f + a.a*b.a + a.w*b.w + a.e*b.e

def dominant_element(v: Vec4) -> str:
    """Return the strongest element"""
    components = {'F': v.f, 'A': v.a, 'W': v.w, 'E': v.e}
    return max(components, key=components.get)

def cell_membership(v: Vec4, threshold: float = 0.2) -> set:
    """Determine which cell a vector belongs to"""
    active = set()
    if v.f >= threshold: active.add('F')
    if v.a >= threshold: active.add('A')
    if v.w >= threshold: active.add('W')
    if v.e >= threshold: active.add('E')
    return active  # maps to one of the 15 cells

def ring_distance(elem_a: str, elem_b: str) -> int:
    """Shortest distance on the elemental ring (0..2)"""
    order = ['F', 'A', 'W', 'E']
    ia, ib = order.index(elem_a), order.index(elem_b)
    d = abs(ia - ib)
    return min(d, 4 - d)

def complement(v: Vec4) -> Vec4:
    """Elemental complement (shadow vector)"""
    return Vec4(1-v.f, 1-v.a, 1-v.w, 1-v.e).normalized()
```

## Cell Transitions

Valid transitions follow the ring adjacency:

```
Pole transitions:
  {F} → {F,A} or {F,E}  (adjacent bridges only)
  {A} → {A,F} or {A,W}
  {W} → {W,A} or {W,E}
  {E} → {E,W} or {E,F}

Bridge → Chamber (add one element):
  {F,A} → {F,A,W} or {F,A,E}
  (6 bridges x 2 directions = 12 transitions)

Chamber → Crown (always valid):
  {F,A,W} → {F,A,W,E}
  {F,A,E} → {F,A,W,E}
  {F,W,E} → {F,A,W,E}
  {A,W,E} → {F,A,W,E}
```

### Transition Cost

```
cost(cell_a → cell_b) =
  if |cell_b| = |cell_a| + 1: φ⁻¹     (expansion)
  if |cell_b| = |cell_a| - 1: φ        (contraction)
  if |cell_b| = |cell_a|:     1.0      (lateral)
  if |cell_b - cell_a| > 1:   INVALID  (no skip)
```

## Ring Algebra

The 15 cells form a lattice under subset ordering:

```
Crown (Ω)
  ├── C1 {F,A,W}
  │     ├── B1 {F,A}
  │     │     ├── P1 {F}
  │     │     └── P2 {A}
  │     ├── B2 {F,W}
  │     │     ├── P1 {F}
  │     │     └── P3 {W}
  │     └── B4 {A,W}
  │           ├── P2 {A}
  │           └── P3 {W}
  ├── C2 {F,A,E}
  │     ├── B1 {F,A}
  │     ├── B3 {F,E}
  │     └── B5 {A,E}
  ├── C3 {F,W,E}
  │     ├── B2 {F,W}
  │     ├── B3 {F,E}
  │     └── B6 {W,E}
  └── C4 {A,W,E}
        ├── B4 {A,W}
        ├── B5 {A,E}
        └── B6 {W,E}
```

## Invariants

1. Every Vec4 signature is unit-normalized
2. Cell membership is deterministic given threshold
3. The 15 cells exhaust all non-empty subsets
4. Ring adjacency is symmetric (F→A implies A→F)
5. Crown is reachable from any cell via valid transitions
6. Complement of a pole vector points to the opposite pole

## Suggested chapter anchors

- `Ch01` — Kernel and entry law
- `Ch07` — Tunnels as morphisms
- `Ch18` — Macro invariants and universal math stack
