# 108D Crown Projections and Cross-Braid Charts

## Fiber Law

For each odd weave n in {3, 5, 7, 9}, the 108D projection is:

$$\Xi_{108}^{[n]} = \bigoplus_{\ell=1}^{36} \bigoplus_{u=1}^{\ell} (\mathbb{Z}_n \otimes \mathbb{Z}_4 \otimes \mathbb{Z}_2)_{(\ell,u)}$$

Resolved occupancy: $N_n = 5328n$

The 108D body has 36 shells (l=1..36), with shell l containing l units, each unit carrying a fiber of Z_n x Z_4 x Z_2.

---

## Single Projection Lookup

| Projection | n | Full Chamber Count | Resonant Count | Exact Return |
|-----------|---|-------------------|---------------|-------------|
| Xi_108^[3] | 3 | 15,984 | 15,984 | 420 |
| Xi_108^[5] | 5 | 26,640 | 26,640 | 420 |
| Xi_108^[7] | 7 | 37,296 | 37,296 | 420 |
| Xi_108^[9] | 9 | 47,952 | 47,952 | 1,260 |

**Note:** For single projections, full count = resonant count (all chambers are resonant).

**Return period:** Projections [3], [5], [7] return at 420 beats. Projection [9] requires 1,260 beats (the supercycle).

---

## Cross-Braid Lookup

For nonempty S subset {3,5,7,9} with |S| >= 2:

$$\Xi_{108}^{[S]} = \text{Braid}_{108}(\{\Xi_{108}^{[n]}\}_{n \in S})$$

Full chamber count: $N_S^{full} = 5328 \prod_{n \in S} n$

Local fiber per unit:
$$\mathcal{F}_{(\ell,u)}^{[S]} = (\prod_{n \in S} \mathbb{Z}_n) \otimes \mathbb{Z}_4 \otimes \mathbb{Z}_2$$

### Pair Braids

| Braid | S | Full Count | Resonant Count | Return |
|-------|---|-----------|---------------|--------|
| [3,5] | {3,5} | 79,920 | 5,328 | 420 |
| [3,7] | {3,7} | 111,888 | 5,328 | 420 |
| [3,9] | {3,9} | 143,856 | 15,984 | 1,260 |
| [5,7] | {5,7} | 186,480 | 5,328 | 420 |
| [5,9] | {5,9} | 239,760 | 5,328 | 1,260 |
| [7,9] | {7,9} | 335,664 | 5,328 | 1,260 |

### Triple Braids

| Braid | S | Full Count | Resonant Count | Return |
|-------|---|-----------|---------------|--------|
| [3,5,7] | {3,5,7} | 559,440 | 5,328 | 420 |
| [3,5,9] | {3,5,9} | 719,280 | 5,328 | 1,260 |
| [3,7,9] | {3,7,9} | 1,006,992 | 5,328 | 1,260 |
| [5,7,9] | {5,7,9} | 1,678,320 | 5,328 | 1,260 |

### Quadruple Braid (Complete)

| Braid | S | Full Count | Resonant Count | Return |
|-------|---|-----------|---------------|--------|
| [3,5,7,9] | {3,5,7,9} | 5,034,960 | 5,328 | 1,260 |

---

## Universal Resonant Spine

**5,328 exact lanes** lie at the center of the full odd crown lattice.

This is the irreducible resonant core: no matter which combination of odd weaves is braided together, exactly 5,328 chambers remain in perfect resonance.

The spine is invariant under all braid operations and represents the stable backbone of the 108D crown structure.

---

## 60x Symmetry Lookup Address

$$\operatorname{Sym60}(x) = \langle s, \sigma, i, j, k \rangle$$

| Component | Meaning |
|-----------|---------|
| s | Stage code |
| sigma | Sigma_60 symmetry family index (1-60) |
| i | Orbit sector |
| j | Portal class |
| k | Rotational witness index |

**Requirement:** Every stage at or above S5S must include:
- Current symmetry class
- Orbit family
- Rotation law
- Sacred-geometry harmonic signature
- Metro transition permissions

---

## Key Relationships

### Return Period Rule
- Any braid containing ONLY {3,5,7} returns at **420** beats
- Any braid containing **9** returns at **1,260** beats (the supercycle)
- 1,260 = 3 x 420 = lcm(420, 36) where 36 = 4 x 9

### Resonant Count Rule
- Single projections: all chambers resonant (N_n = 5328n)
- Multi-braids: resonant count collapses to **5,328** (the universal spine)
- Exception: [3,9] braid retains 15,984 resonant chambers (= N_3)

### Full Count Formula
$N_S^{full} = 5328 \prod_{n \in S} n$

This grows as the product of the included weave numbers, while the resonant spine remains fixed at 5,328.
