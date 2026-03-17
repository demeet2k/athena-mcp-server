# Deterministic Router v3

> Pure algebraic routing with hub budget. No randomness, no heuristics, no machine learning.

---

## 1. Router Inputs

Given a query Q with:

| Parameter | Symbol | Domain | Description |
|-----------|--------|--------|-------------|
| Source chapter | ChXX | Ch01..Ch21 | Chapter with station code (dddd)_4 |
| Target lens | L | {S, F, C, R} | Which HCRL container face |
| Target facet | f | {1, 2, 3, 4} | Which facet within the lens |
| Intent | I | {VERIFY, BUILD, MIGRATE, RESOLVE, PUBLISH} | What the query wants to accomplish |
| Arc | alpha | {0, 1, 2, 3, 4, 5, 6} | The arc containing the source chapter |

The arc alpha is derived from the chapter number: alpha = floor((omega) / 3) where omega = chapter_number - 1.

---

## 2. Hub Selection Algorithm

### Step 1: Mandatory Signature

Always include:

```
Sigma = {AppA, AppI, AppM}
```

These three hubs are non-negotiable and appear in every route.

### Step 2: Add LensBase(L)

The hub that anchors the target lens:

| Lens | LensBase |
|------|----------|
| S (Square) | AppC |
| F (Flower) | AppE |
| C (Cloud) | AppI |
| R (Fractal) | AppM |

Note: LensBase(C) = AppI and LensBase(R) = AppM overlap with Sigma. This is by design and handled by deduplication.

### Step 3: Add FacetBase(f)

The hub that anchors the target facet:

| Facet | FacetBase |
|-------|-----------|
| 1 | AppA |
| 2 | AppB |
| 3 | AppH |
| 4 | AppM |

Note: FacetBase(1) = AppA and FacetBase(4) = AppM overlap with Sigma.

### Step 4: Add ArcHub(alpha)

The hub that anchors the source chapter's arc:

| Arc | Chapters | ArcHub |
|-----|----------|--------|
| 0 | Ch01, Ch02, Ch03 | AppA |
| 1 | Ch04, Ch05, Ch06 | AppC |
| 2 | Ch07, Ch08, Ch09 | AppE |
| 3 | Ch10, Ch11, Ch12 | AppF |
| 4 | Ch13, Ch14, Ch15 | AppG |
| 5 | Ch16, Ch17, Ch18 | AppN |
| 6 | Ch19, Ch20, Ch21 | AppP |

### Step 5: Deduplicate

```
hubs = unique(Sigma ∪ {LensBase(L)} ∪ {FacetBase(f)} ∪ {ArcHub(alpha)})
```

### Step 6: Enforce Hub Cap

```
hub_cap = 6
```

If |hubs| > 6, drop the lowest-priority non-mandatory hub until |hubs| <= 6.

Priority order (highest to lowest):
1. **Mandatory Sigma** = {AppA, AppI, AppM} -- never dropped
2. **ArcHub** -- dropped last among non-mandatory
3. **LensBase** -- dropped before ArcHub
4. **FacetBase** -- dropped first among non-mandatory

---

## 3. Truth Overlay

After routing, apply truth evaluation from the C (Cloud) face:

| Truth Status | Condition | Additional Hub |
|--------------|-----------|----------------|
| **OK** | All corridor checks pass | None |
| **NEAR** | Within epsilon of passing | AppJ |
| **AMBIG** | Multiple valid interpretations | AppL |
| **FAIL** | Corridor check fails | AppK |

**Critical rule:** Truth hubs do NOT count against hub_cap. They are appended after the cap enforcement step.

Final route:
```
route = capped_hubs ∪ truth_hubs
```

Maximum possible route size: 6 (capped) + 1 (truth) = 7 hubs.

---

## 4. Route Examples

### Example 1: Ch05, Lens=S, Facet=2, Truth=OK

```
Chapter:   Ch05 --> omega=4, arc=floor(4/3)=1
Lens:      S
Facet:     2

Step 1 (Sigma):      {AppA, AppI, AppM}
Step 2 (LensBase S): {AppC}
Step 3 (FacetBase 2):{AppB}
Step 4 (ArcHub 1):   {AppC}

Union:    {AppA, AppI, AppM, AppC, AppB}
Dedup:    {AppA, AppB, AppC, AppI, AppM}  -- 5 hubs
Cap check: 5 <= 6  --> PASS

Truth:    OK --> no additional hub

FINAL ROUTE: {AppA, AppB, AppC, AppI, AppM}  -- 5 hubs
```

### Example 2: Ch14, Lens=F, Facet=3, Truth=NEAR

```
Chapter:   Ch14 --> omega=13, arc=floor(13/3)=4
Lens:      F
Facet:     3

Step 1 (Sigma):      {AppA, AppI, AppM}
Step 2 (LensBase F): {AppE}
Step 3 (FacetBase 3):{AppH}
Step 4 (ArcHub 4):   {AppG}

Union:    {AppA, AppI, AppM, AppE, AppH, AppG}
Dedup:    {AppA, AppE, AppG, AppH, AppI, AppM}  -- 6 hubs
Cap check: 6 <= 6  --> PASS

Truth:    NEAR --> add AppJ

FINAL ROUTE: {AppA, AppE, AppG, AppH, AppI, AppJ, AppM}  -- 7 hubs
```

### Example 3: Ch19, Lens=R, Facet=4, Truth=OK

```
Chapter:   Ch19 --> omega=18, arc=floor(18/3)=6
Lens:      R
Facet:     4

Step 1 (Sigma):      {AppA, AppI, AppM}
Step 2 (LensBase R): {AppM}          -- already in Sigma
Step 3 (FacetBase 4):{AppM}          -- already in Sigma
Step 4 (ArcHub 6):   {AppP}

Union:    {AppA, AppI, AppM, AppP}
Dedup:    {AppA, AppI, AppM, AppP}  -- 4 hubs
Cap check: 4 <= 6  --> PASS

Truth:    OK --> no additional hub

FINAL ROUTE: {AppA, AppI, AppM, AppP}  -- 4 hubs
```

This example shows maximum overlap: both LensBase(R) and FacetBase(4) collapse into the mandatory signature.

### Example 4: Ch10, Lens=C, Facet=1, Truth=FAIL

```
Chapter:   Ch10 --> omega=9, arc=floor(9/3)=3
Lens:      C
Facet:     1

Step 1 (Sigma):      {AppA, AppI, AppM}
Step 2 (LensBase C): {AppI}          -- already in Sigma
Step 3 (FacetBase 1):{AppA}          -- already in Sigma
Step 4 (ArcHub 3):   {AppF}

Union:    {AppA, AppI, AppM, AppF}
Dedup:    {AppA, AppF, AppI, AppM}  -- 4 hubs
Cap check: 4 <= 6  --> PASS

Truth:    FAIL --> add AppK

FINAL ROUTE: {AppA, AppF, AppI, AppK, AppM}  -- 5 hubs
```

Maximum overlap case with a truth escalation.

---

## 5. Determinism Guarantee

The router is **fully deterministic**:

1. **No randomness**: Every step uses lookup tables with fixed mappings
2. **No heuristics**: Hub selection follows exact algebraic rules
3. **No machine learning**: No weights, no training, no inference
4. **Pure functions**: identical inputs always produce identical hub sets

### Formal Property

For any two invocations with identical (ChXX, L, f, alpha, truth_status):

```
route(ChXX, L, f, alpha, truth) = route(ChXX, L, f, alpha, truth)
```

This is guaranteed by construction: every step is a deterministic lookup or set operation.

### Verification

The determinism guarantee can be verified exhaustively:
- 21 chapters x 4 lenses x 4 facets = 336 base combinations
- x 4 truth statuses = 1344 total combinations
- Each combination produces exactly one hub set
- The full routing table can be precomputed and cached

---

## 6. Priority Order for Hub Dropping

When hub_cap is exceeded (|hubs| > 6), hubs are dropped in this order (first dropped = lowest priority):

| Priority | Source | Droppable? | Rationale |
|----------|--------|------------|-----------|
| 1 (highest) | Mandatory Sigma | NEVER | Foundation of every route |
| 2 | ArcHub | Last resort | Provides chapter-group context |
| 3 | LensBase | Before ArcHub | Can be inferred from lens parameter |
| 4 (lowest) | FacetBase | First to drop | Can be inferred from facet parameter |

### Theoretical Maximum Before Cap

```
Sigma:     3 hubs (AppA, AppI, AppM)
LensBase:  1 hub  (may overlap with Sigma)
FacetBase: 1 hub  (may overlap with Sigma)
ArcHub:    1 hub  (may overlap with Sigma)
```

Maximum unique hubs = 6 (when all three non-Sigma hubs are distinct from Sigma and from each other). This means the hub_cap of 6 is **tight**: it is the maximum possible without any overlap, so dropping is only needed in edge cases where the cap is set lower than 6.

In practice, overlap with Sigma is common (LensBase(C)=AppI, LensBase(R)=AppM, FacetBase(1)=AppA, FacetBase(4)=AppM, ArcHub(0)=AppA), making most routes 4-5 hubs before truth overlay.

---

*Router version: v3.0 | Hub cap: 6 | Truth overlay: uncapped | Determinism: guaranteed*
