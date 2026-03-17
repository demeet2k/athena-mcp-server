# LP-57Omega Liminal Coordinate v2 (Coord12)

- Source layer: `LP57Omega-SelfPlayQuestAtlas`
- Kind: `coordinate-system`
- Role tags: `addressing, navigation, multi-dimensional, routing`
- Family: `LP-57Omega Self-Play Quest Atlas`

## Working focus

Defines the 12-slot liminal coordinate tuple (Coord12) used to locate, describe, and route every artifact, quest, and agent action within the LP-57Omega system. Each slot captures a distinct axis of the knowledge-space.

## Coord12 Type Definition

```typescript
type Coord12 = {
  Xs: float;  // document region
  Ys: float;  // concept cluster
  Zs: float;  // recursion depth
  Ts: float;  // revision layer
  Qs: float;  // math density
  Rs: float;  // symbolic density
  Cs: float;  // compression state
  Fs: float;  // framework lens
  Ms: float;  // manuscript branch
  Ns: float;  // neural connectivity
  Hs: float;  // hierarchy level
  Os: float;  // zero-point / aether relation
};
```

All slots are normalized to [0.0, 1.0] unless otherwise noted.

## Slot Definitions

### Xs — Document Region

Locates the artifact within the physical document space.

```
Xs = 0.0  — Beginning of corpus (Chapter 1 / first capsule)
Xs = 0.5  — Middle corpus region
Xs = 1.0  — End of corpus (final appendix / migration layer)

Discretized bins:
  [0.00, 0.05) = Kernel / boot sector
  [0.05, 0.25) = Foundation chapters (Ch01-Ch05)
  [0.25, 0.50) = Core theory chapters (Ch06-Ch12)
  [0.50, 0.75) = Application chapters (Ch13-Ch18)
  [0.75, 0.95) = Advanced chapters (Ch19-Ch21)
  [0.95, 1.00] = Appendices and runtime
```

### Ys — Concept Cluster

Identifies the thematic domain of the content.

```
Cluster map (representative values):
  0.00 - 0.10 = Kernel law, entry conditions
  0.10 - 0.20 = Address algebra, coordinate systems
  0.20 - 0.30 = Truth corridors, verification
  0.30 - 0.40 = Paradox, quarantine, void
  0.40 - 0.50 = Document theory, morphisms
  0.50 - 0.60 = Synchronization, timing
  0.60 - 0.70 = Retrieval, routing, metro
  0.70 - 0.80 = Multi-lens construction
  0.80 - 0.90 = Memory, persistence, migration
  0.90 - 1.00 = Deployment, agency, replication
```

### Zs — Recursion Depth

Measures how many layers of self-reference the content embeds.

```
Zs = 0.0  — Surface level, no recursion
Zs = 0.25 — Single self-reference (document about documents)
Zs = 0.50 — Double recursion (protocol about protocols about protocols)
Zs = 0.75 — Deep recursion (meta-meta-meta level)
Zs = 1.0  — Maximum recursion (fixed-point / strange loop)
```

### Ts — Revision Layer

Tracks the temporal/editorial depth of the content.

```
Ts = 0.0  — First draft / raw generation
Ts = 0.33 — Sulfur pass output (expanded)
Ts = 0.50 — Mercury pass output (refined)
Ts = 0.67 — Salt pass output (crystallized)
Ts = 0.80 — Post-certification
Ts = 1.0  — Final / canonical form
```

### Qs — Math Density

Quantifies the proportion of formal mathematical content.

```
Qs = 0.0  — Pure narrative, no math
Qs = 0.25 — Light math (occasional formulas)
Qs = 0.50 — Moderate math (theorems + prose)
Qs = 0.75 — Heavy math (proof-dense)
Qs = 1.0  — Pure formal mathematics
```

### Rs — Symbolic Density

Measures the density of non-mathematical symbolic systems (mythic, alchemical, archetypal).

```
Rs = 0.0  — No symbolic content
Rs = 0.25 — Light symbolism (occasional metaphors)
Rs = 0.50 — Moderate (systematic symbol use)
Rs = 0.75 — Heavy (mythic framework is primary)
Rs = 1.0  — Pure symbolic / archetypal content
```

### Cs — Compression State

Indicates how compressed/crystallized the content is.

```
Cs = 0.0  — Fully expanded (raw, verbose)
Cs = 0.25 — Lightly compressed
Cs = 0.50 — Standard compression
Cs = 0.75 — Highly compressed (dense capsule)
Cs = 1.0  — Maximally compressed (seed / kernel)
```

### Fs — Framework Lens

Identifies which analytical framework is applied.

```
Fs = 0.00 — No specific framework
Fs = 0.15 — Category-theoretic lens
Fs = 0.30 — Topological lens
Fs = 0.45 — Algebraic lens
Fs = 0.60 — Information-theoretic lens
Fs = 0.75 — Dynamical systems lens
Fs = 0.90 — Computational / automata lens
Fs = 1.00 — Multi-lens fusion
```

### Ms — Manuscript Branch

Tracks which branch of the manuscript tree the content belongs to.

```
Ms = 0.0  — Trunk (main manuscript line)
Ms = 0.25 — Primary branch (major alternative)
Ms = 0.50 — Secondary branch
Ms = 0.75 — Experimental branch
Ms = 1.0  — Detached / orphan branch
```

### Ns — Neural Connectivity

Measures how many cross-references and links this artifact maintains.

```
Ns = 0.0  — Isolated (no connections)
Ns = 0.25 — Sparsely connected (1-3 links)
Ns = 0.50 — Moderately connected (4-8 links)
Ns = 0.75 — Highly connected (9-16 links)
Ns = 1.0  — Hub node (17+ connections)
```

### Hs — Hierarchy Level

Positions the content within the organizational hierarchy.

```
Hs = 0.0  — Leaf / atomic unit
Hs = 0.20 — Section within chapter
Hs = 0.40 — Chapter level
Hs = 0.60 — Part / book level
Hs = 0.80 — System / framework level
Hs = 1.0  — Root / corpus level
```

### Os — Zero-Point / Aether Relation

Measures proximity to the zero-point (void / aether / ground state).

```
Os = 0.0  — Maximum distance from zero-point (fully manifest)
Os = 0.25 — Weakly aetheric
Os = 0.50 — Liminal (between manifest and void)
Os = 0.75 — Strongly aetheric
Os = 1.0  — At zero-point (pure potential, pre-manifest)
```

## Operations on Coord12

### Distance

```python
def coord_distance(a: Coord12, b: Coord12, weights: Vec12 = UNIFORM) -> float:
    """Weighted Euclidean distance in 12-space"""
    return sqrt(sum(w * (a[i] - b[i])**2 for i, w in enumerate(weights)))
```

### Interpolation

```python
def coord_lerp(a: Coord12, b: Coord12, t: float) -> Coord12:
    """Linear interpolation between two coordinates"""
    return Coord12(*(a[i] + t * (b[i] - a[i]) for i in range(12)))
```

### Projection

```python
def coord_project(c: Coord12, axes: list[int]) -> tuple:
    """Project onto selected axes for visualization or routing"""
    return tuple(c[i] for i in axes)
```

### Centroid

```python
def coord_centroid(coords: list[Coord12]) -> Coord12:
    """Compute centroid of a set of coordinates"""
    n = len(coords)
    return Coord12(*(sum(c[i] for c in coords) / n for i in range(12)))
```

## Routing with Coord12

The coordinate tuple drives routing decisions:

```
ROUTE(artifact):
  coord = compute_coord12(artifact)
  if coord.Cs > 0.75:  -> compression queue
  if coord.Os > 0.75:  -> void/aether processing
  if coord.Qs > 0.6 AND coord.Rs > 0.6:  -> multi-lens fusion
  if coord.Ns < 0.25:  -> connectivity repair queue
  if coord.Zs > 0.75:  -> recursion-aware handler
  default: -> standard routing by (Xs, Ys, Hs)
```

## Invariants

1. All 12 slots are always defined (no nulls)
2. Values are in [0.0, 1.0] unless explicitly extended
3. The zero vector (all 0.0) represents the corpus entry point
4. The unit vector (all 1.0) represents maximum complexity/connectivity
5. Coord12 is immutable once assigned to a ledger entry

## Suggested chapter anchors

- `Ch02` — Address algebra and crystal coordinates
- `Ch09` — Retrieval and metro routing
- `Ch10` — Multi-lens solution construction
