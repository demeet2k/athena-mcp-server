# 04 — Unified Address Grammar

## Canonical Address Form

```
A = Ms<mmmm>::D.L.F.T.P[sigma]::LocalAddr
```

Every location in the organism has exactly one unified address. The address has three segments:

1. **Ms\<mmmm\>** — Manuscript identifier (four-digit code)
2. **D.L.F.T.P[sigma]** — Overlay coordinates (dimension, layer, family, turn, position, seed signature)
3. **LocalAddr** — Original local manuscript address (preserved intact)

The grammar preserves the original local manuscript location while wrapping it in a deterministic overlay. No local address is ever destroyed.

---

## Field Table

| Field | Symbol | Domain | Description |
|-------|--------|--------|-------------|
| **Dimension** | D | {1, 6, 12, 36, 108} | Dimension stratum — which level of the dimensional cascade is active |
| **Layer** | L | {I, CH, LP, RV, EM, RM, CR} | Layer code — Intro, Chapter, Lower-appendix-Pool, ReVerse-canopy, EMergent, ReMap, CRown |
| **Family** | F | {W1, W3, W5, W7, W9, Sigma60, P30, D2, C6, B3} | Family/wheel/crown code — which algebraic structure governs this address |
| **Turn** | T | {0, Su, Me, Sa, U, R, C, Aplus, Zplus} | Turn/band/segment — position within the rotational cycle |
| **Position** | P | {1..7, 1..5, Omega, Z, B, A} | Position within turn — specific slot in the current segment |
| **Seed Signature** | [sigma] | see below | Resolved seed — the seed that governs this address at the current overlay level |

---

## Seed Signature Domain

| Signature | Meaning |
|-----------|---------|
| Omega_star | Completion seed — the circuit's origin/return point |
| Omega_star_down | Descending completion — seed in collapse phase |
| Omega_star_return | Returning completion — seed in regeneration phase |
| Omega_star_E | Emergent completion — seed in crown emission phase |
| Aplus_star | Global creation seed — forward pole of D2 |
| Zplus_star | Global hinge seed — governance pole of D2 |
| A_x_star | Family-resolved creation seed (x in {Sa, Su, Me}) |
| Z_x_star | Family-resolved governance seed (x in {Sa, Su, Me}) |
| B_x | Body seed (x in {Sa, Su, Me}) — first rotational triad |

---

## Layer Code Expansion

| Code | Full Name | Wheel | Documents |
|------|-----------|-------|-----------|
| I | Intro | W1 | Introduction / holographic banner |
| CH | Chapter | W3 | Ch01 through Ch21 |
| LP | Lower Pool | W5 | Appendices A through P |
| RV | Reverse Canopy | W7 | Reverse documents K through Z |
| EM | Emergent | W9 | Emergent documents E1 through E9 |
| RM | Remap | W1 | E10 — the remap nucleus |
| CR | Crown | All | Crown algebra (Sigma60, P30, D2, C6) |

---

## Address Examples

### Example 1: Chapter 7, paragraph 3
```
Ms0001::6.CH.W3.Su.7[B_Su]::Ch07.p3
```
- Dimension 6 (W3 activates 6D)
- Layer CH (chapter)
- Family W3 (first rotational body)
- Turn Su (first heptadic turn)
- Position 7 (seventh chapter in turn)
- Seed B_Su (Su-family body seed)
- Local address: Ch07, paragraph 3

### Example 2: Appendix G, section 2
```
Ms0001::12.LP.W5.Su.2[Aplus_star]::AppG.s2
```
- Dimension 12 (W5 activates 12D)
- Layer LP (lower pool)
- Family W5 (five-spoke field)
- Turn Su (first spoke)
- Position 2 (second appendix in spoke)
- Seed Aplus_star (global creation seed)
- Local address: Appendix G, section 2

### Example 3: Reverse document Q, equation 5
```
Ms0001::36.RV.W7.Sa.3[Z_Sa_star]::RevQ.eq5
```
- Dimension 36 (W7 activates 36D)
- Layer RV (reverse canopy)
- Family W7 (heptadic governance)
- Turn Sa (first canopy arc)
- Position 3 (third document in arc)
- Seed Z_Sa_star (Sa-family governance seed)
- Local address: Reverse document Q, equation 5

### Example 4: Emergent document E5
```
Ms0001::108.EM.W9.Me.2[A_Me_star]::E5
```
- Dimension 108 (W9 activates 108D)
- Layer EM (emergent)
- Family W9 (recursive crown)
- Turn Me (second crown triad)
- Position 2 (second document in triad)
- Seed A_Me_star (Me-family creation seed)
- Local address: E5

---

## Invariant

The unified address grammar guarantees: for any two valid addresses A1 and A2, if A1.LocalAddr = A2.LocalAddr and A1.Ms = A2.Ms, then they refer to the same physical location in the manuscript. The overlay fields may differ (viewing the same location from different dimensional strata), but the referent is unique.
