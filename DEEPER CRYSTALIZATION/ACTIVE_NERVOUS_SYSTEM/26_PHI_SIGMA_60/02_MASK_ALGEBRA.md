# Mask Algebra and Master Registry

## The 15 Masks

Every nonempty subset of {A, B, C, D} is a mask. The powerset minus empty set gives 15 masks organized by cardinality.

| # | Mask | Members | Exponent z_S = u + iv | Class |
|---|------|---------|----------------------|-------|
| 01 | A | {A} | 1/phi | pole |
| 02 | B | {B} | -phi | pole |
| 03 | C | {C} | i/phi | pole |
| 04 | D | {D} | -i*phi | pole |
| 05 | AB | {A,B} | -1 | bridge |
| 06 | AC | {A,C} | (1+i)/phi | bridge |
| 07 | AD | {A,D} | 1/phi - i*phi | bridge |
| 08 | BC | {B,C} | -phi + i/phi | bridge |
| 09 | BD | {B,D} | -phi*(1+i) | bridge |
| 10 | CD | {C,D} | -i | bridge |
| 11 | ABC | {A,B,C} | -1 + i/phi | chamber |
| 12 | ABD | {A,B,D} | -1 - i*phi | chamber |
| 13 | ACD | {A,C,D} | 1/phi - i | chamber |
| 14 | BCD | {B,C,D} | -phi - i | chamber |
| 15 | ABCD | {A,B,C,D} | -1 - i | crown |

## Exponent Vector Computation

For any mask S, the exponent is the sum of primitive vectors:

```
z_S = sum_{p in S} z_p
```

where:
```
z_A = 1/phi       (positive real axis)
z_B = -phi         (negative real axis)
z_C = i/phi        (positive imaginary axis)
z_D = -i*phi       (negative imaginary axis)
```

### Real part: u_S = (1/phi if A in S else 0) + (-phi if B in S else 0)
### Imaginary part: v_S = (1/phi if C in S else 0) + (-phi if D in S else 0)

---

## Master Registry

| # | Mask | z_S | Aether A_S = phi^(z_S) | Geometry | Metro Neighbors |
|---|------|-----|----------------------|----------|----------------|
| 01 | A | 1/phi | phi^(1/phi) | outward manifest petal | 05, 06, 07 |
| 02 | B | -phi | phi^(-phi) | inward refinement petal | 05, 08, 09 |
| 03 | C | i/phi | phi^(i/phi) | forward phase halo | 06, 08, 10 |
| 04 | D | -i*phi | phi^(-i*phi) | reverse phase halo | 07, 09, 10 |
| 05 | AB | -1 | phi^(-1) | mandorla / hinge spindle | 01, 02, 11, 12 |
| 06 | AC | (1+i)/phi | phi^((1+i)/phi) | forward growth helix | 01, 03, 11, 13 |
| 07 | AD | 1/phi - i*phi | phi^(1/phi - i*phi) | counter-growth arm | 01, 04, 12, 13 |
| 08 | BC | -phi + i/phi | phi^(-phi + i/phi) | inward helical fold | 02, 03, 11, 14 |
| 09 | BD | -phi*(1+i) | phi^(-phi*(1+i)) | return vortex | 02, 04, 12, 14 |
| 10 | CD | -i | phi^(-i) | phase equator ring | 03, 04, 13, 14 |
| 11 | ABC | -1 + i/phi | phi^(-1 + i/phi) | forward bridge chamber | 05, 06, 08, 15 |
| 12 | ABD | -1 - i*phi | phi^(-1 - i*phi) | return bridge chamber | 05, 07, 09, 15 |
| 13 | ACD | 1/phi - i | phi^(1/phi - i) | growth-phase braided | 06, 07, 10, 15 |
| 14 | BCD | -phi - i | phi^(-phi - i) | refine-phase braided | 08, 09, 10, 15 |
| 15 | ABCD | -1 - i | phi^(-1 - i) | total rosette / crown | 11, 12, 13, 14 |

---

## Metro Adjacency Rule

Two masks are metro-adjacent if and only if they differ by exactly one primitive letter. This gives:
- Each singleton (|S|=1) has exactly 3 bridge neighbors
- Each pair (|S|=2) has 2 singleton + 2 triple neighbors = 4
- Each triple (|S|=3) has 3 pair + 1 quad neighbors = 4
- The quad (|S|=4) has exactly 4 triple neighbors

Total metro edges in the mask lattice: 32 (undirected).

Each mask also has a local 4-station lens cycle:
```
mu_S -> mu_F -> mu_C -> mu_R -> mu_S
```

So total stations: 15 masks x 4 lenses = 60. Total edges: 32 inter-mask + 60 intra-lens = 92.
