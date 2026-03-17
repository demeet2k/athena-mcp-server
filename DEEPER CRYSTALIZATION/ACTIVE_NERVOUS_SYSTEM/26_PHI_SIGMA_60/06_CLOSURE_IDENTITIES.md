# Closure Identities and Invariant Laws

## The 4 Primary Closure Identities

### Identity 1: Real Pole Product
```
Phi_a * Phi_b = phi^(1/phi) * phi^(-phi) = phi^(1/phi - phi) = phi^(-1)
```
The two real poles (expansion and contraction) compress to the golden inverse. This is the first balanced bridge.

### Identity 2: Phase Pole Product
```
Phi_c * Phi_d = phi^(i/phi) * phi^(-i*phi) = phi^(i/phi - i*phi) = phi^(-i)
```
The two phase poles (forward and reverse resonance) compress to the imaginary golden inverse.

### Identity 3: Phase Bridge Quarter-Turn (MAJOR CLOSURE)
```
(Phi_c * Phi_d)^i = (phi^(-i))^i = phi^(-i*i) = phi^(1) = phi
```
**The phase bridge of the two shadow poles quarter-turns back into the primal golden constant.** This is the major structural closure of the codex.

### Identity 4: Real Bridge Quarter-Turn
```
(Phi_a * Phi_b)^i = (phi^(-1))^i = phi^(-i)
```
The real bridge quarter-turns to the imaginary golden inverse (which is Identity 2's product).

---

## Crown Closure

The full 4-way product:
```
Phi_a * Phi_b * Phi_c * Phi_d = phi^(1/phi - phi + i/phi - i*phi) = phi^(-1 - i)
```

Crown coordinates:
```
15S = phi^(-1-i)     (native crown aether)
15F = phi^(1-i)      (phase-lifted crown — note real part flips positive)
15C = -1-i           (crown zero coordinate)
15R(k) = phi^(k-1-i) (crown replay rail)
```

---

## Linking Laws

### Real-Phase Symmetry
```
z_A + z_B = -1        (real poles sum to -1)
z_C + z_D = -i        (phase poles sum to -i)
z_A + z_B + z_C + z_D = -1-i   (total sum)
```

### Magnitude Relations
```
|z_A| = |z_C| = 1/phi = phi - 1
|z_B| = |z_D| = phi
|z_A| * |z_B| = |z_C| * |z_D| = 1   (golden conjugate product)
```

### Lens Closure at Mask 10
```
10F = (phi^(-i))^i = phi   (Flower of CD equals primal phi)
```
This means the phase-equator bridge, when quarter-turned, returns to the fundamental constant.

### Lens Closure at Mask 05
```
05F = (phi^(-1))^i = phi^(-i)   (Flower of AB equals native CD)
```
The real bridge's Flower form equals the phase bridge's Square form.

---

## Conservation Laws

### Over any closed lens cycle (S -> F -> C -> R -> S):
- The mask is preserved
- The zero point z_S is preserved
- The geometry class is preserved
- Only the lens interpretation changes

### Over any mask adjacency step:
- Exactly one primitive is added or removed
- The exponent z_S changes by exactly one primitive vector
- The geometry class changes by exactly one level (pole <-> bridge <-> chamber <-> crown)

### Global zero tunnel:
- From any Cloud node: Z_S -> Z* = 0 (subtraction of z_S)
- Rebuild: Z* = 0 -> z_S -> phi^(z_S) = A_S (aether reconstruction)

---

## Numerical Verification Targets

| Identity | LHS | RHS | Residual Target |
|----------|-----|-----|----------------|
| Phi_a * Phi_b = phi^(-1) | product of two reals | 1/phi | < 1e-15 |
| Phi_c * Phi_d = phi^(-i) | product of two unit-modulus complex | phi^(-i) | < 1e-12 |
| (Phi_c * Phi_d)^i = phi | complex exponentiation | phi | < 1e-12 |
| Crown product = phi^(-1-i) | 4-way complex product | phi^(-1-i) | < 1e-12 |
| 10F = phi | computed Flower of mask 10 | phi | < 1e-12 |
| 05F = phi^(-i) | computed Flower of mask 05 | phi^(-i) | < 1e-12 |
