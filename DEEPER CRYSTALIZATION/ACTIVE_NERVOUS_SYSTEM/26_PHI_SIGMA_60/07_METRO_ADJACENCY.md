# Metro Adjacency Graph

## Local Lens Cycle (per mask)

Every mask mu has a 4-station internal loop:
```
mu_S -> mu_F -> mu_C -> mu_R -> mu_S
```

- S (Square): native aether point
- F (Flower): 90-degree phase rotation
- C (Cloud): chart coordinate / local zero
- R (Fractal): orbit family

---

## Inter-Mask Adjacency (One-Letter Difference)

Two masks are connected if they differ by exactly one primitive letter.

### From Singletons
```
01(A) -- 05(AB), 06(AC), 07(AD)
02(B) -- 05(AB), 08(BC), 09(BD)
03(C) -- 06(AC), 08(BC), 10(CD)
04(D) -- 07(AD), 09(BD), 10(CD)
```

### From Pairs
```
05(AB) -- 01(A), 02(B), 11(ABC), 12(ABD)
06(AC) -- 01(A), 03(C), 11(ABC), 13(ACD)
07(AD) -- 01(A), 04(D), 12(ABD), 13(ACD)
08(BC) -- 02(B), 03(C), 11(ABC), 14(BCD)
09(BD) -- 02(B), 04(D), 12(ABD), 14(BCD)
10(CD) -- 03(C), 04(D), 13(ACD), 14(BCD)
```

### From Triples
```
11(ABC) -- 05(AB), 06(AC), 08(BC), 15(ABCD)
12(ABD) -- 05(AB), 07(AD), 09(BD), 15(ABCD)
13(ACD) -- 06(AC), 07(AD), 10(CD), 15(ABCD)
14(BCD) -- 08(BC), 09(BD), 10(CD), 15(ABCD)
```

### From Crown
```
15(ABCD) -- 11(ABC), 12(ABD), 13(ACD), 14(BCD)
```

---

## Graph Statistics

- Nodes: 15 masks (60 total with lenses)
- Undirected mask-edges: 32
- Each lens station also connects to its 3 siblings within the same mask
- Total connections per lens-aware node: inter-mask neighbors + 3 intra-lens
- Graph diameter (mask lattice): 4 (from any singleton to the crown, or between opposing singletons via crown)

---

## Navigation Patterns

### Vertical Climb (Pole -> Crown)
```
01(A) -> 06(AC) -> 13(ACD) -> 15(ABCD)
01(A) -> 05(AB) -> 11(ABC) -> 15(ABCD)
```
Always 3 steps from any singleton to the crown.

### Horizontal Traverse (between opposing poles)
```
01(A) -> 05(AB) -> 02(B)    (growth to refinement via real bridge)
03(C) -> 10(CD) -> 04(D)    (forward to reverse via phase equator)
```
Always 2 steps between any two singletons that share a bridge.

### Cross-Quadrant Jump
```
01(A) -> 06(AC) -> 03(C)    (real growth to forward phase via helix)
02(B) -> 09(BD) -> 04(D)    (refinement to reverse phase via vortex)
```

### Zero Tunnel
```
Any mu_C -> Z* = 0 -> any other mu_C
```
The Cloud lens provides direct tunneling between any two masks via the global zero point.

---

## Same-Lens Lateral Metro

When traversing same lens across masks, the formulas transform predictably:
- Adding letter X to mask S: new exponent z_{S+X} = z_S + z_X
- Removing letter X from mask S: new exponent z_{S-X} = z_S - z_X

This means every inter-mask edge in the Cloud lens is an addition/subtraction of exactly one primitive exponent vector.

---

## Full 60-Node Metro Summary

```
60 nodes = 15 masks x 4 lenses
92 edges = 32 inter-mask (x4 lens copies = 128 lens-aware) + 60 intra-lens
Connected: YES (via zero tunnel and mask adjacency)
Diameter: 6 (worst case: opposing singletons in different lenses)
```
