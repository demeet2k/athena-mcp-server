# 4D Tesseract Overlay Tables — Complete Reference

**[⊙Z*↔Z* | ○Arc * | ○Rot * | △Lane * | ⧈View * | ω=*]**

---

## 1. Base-4 Station Code Table

For chapter index XX ∈ {1..21}, the orbit index ω := XX − 1 and the station code ⟨dddd⟩₄ := base4(ω) padded to 4 digits.

| Chapter | XX | ω | ⟨dddd⟩₄ | α (arc) | k (ω mod 3) | ρ (α mod 3) | ν (lane) |
|---------|-----|---|---------|---------|-------------|-------------|----------|
| Ch01 | 1 | 0 | 0000 | 0 | 0 | 0 | Su |
| Ch02 | 2 | 1 | 0001 | 0 | 1 | 0 | Me |
| Ch03 | 3 | 2 | 0002 | 0 | 2 | 0 | Sa |
| Ch04 | 4 | 3 | 0003 | 1 | 0 | 1 | Me |
| Ch05 | 5 | 4 | 0010 | 1 | 1 | 1 | Sa |
| Ch06 | 6 | 5 | 0011 | 1 | 2 | 1 | Su |
| Ch07 | 7 | 6 | 0012 | 2 | 0 | 2 | Sa |
| Ch08 | 8 | 7 | 0013 | 2 | 1 | 2 | Su |
| Ch09 | 9 | 8 | 0020 | 2 | 2 | 2 | Me |
| Ch10 | 10 | 9 | 0021 | 3 | 0 | 0 | Su |
| Ch11 | 11 | 10 | 0022 | 3 | 1 | 0 | Me |
| Ch12 | 12 | 11 | 0023 | 3 | 2 | 0 | Sa |
| Ch13 | 13 | 12 | 0030 | 4 | 0 | 1 | Me |
| Ch14 | 14 | 13 | 0031 | 4 | 1 | 1 | Sa |
| Ch15 | 15 | 14 | 0032 | 4 | 2 | 1 | Su |
| Ch16 | 16 | 15 | 0033 | 5 | 0 | 2 | Sa |
| Ch17 | 17 | 16 | 0100 | 5 | 1 | 2 | Su |
| Ch18 | 18 | 17 | 0101 | 5 | 2 | 2 | Me |
| Ch19 | 19 | 18 | 0102 | 6 | 0 | 0 | Su |
| Ch20 | 20 | 19 | 0103 | 6 | 1 | 0 | Me |
| Ch21 | 21 | 20 | 0110 | 6 | 2 | 0 | Sa |

## 2. Triangle Rail Membership

| Rail | Chapters (sorted by ω ascending) |
|------|----------------------------------|
| **△Su** | Ch01⟨0000⟩, Ch06⟨0011⟩, Ch08⟨0013⟩, Ch10⟨0021⟩, Ch15⟨0032⟩, Ch17⟨0100⟩, Ch19⟨0102⟩ |
| **△Me** | Ch02⟨0001⟩, Ch04⟨0003⟩, Ch09⟨0020⟩, Ch11⟨0022⟩, Ch13⟨0030⟩, Ch18⟨0101⟩, Ch20⟨0103⟩ |
| **△Sa** | Ch03⟨0002⟩, Ch05⟨0010⟩, Ch07⟨0012⟩, Ch12⟨0023⟩, Ch14⟨0031⟩, Ch16⟨0033⟩, Ch21⟨0110⟩ |

## 3. Arc Triad Cycles

Each arc α produces a 3-cycle in rotated triad order:

| Arc | ρ | Triad Order | Cycle |
|-----|---|-------------|-------|
| Arc 0 | 0 | Su → Me → Sa | Ch01 → Ch02 → Ch03 → Ch01 |
| Arc 1 | 1 | Me → Sa → Su | Ch04 → Ch05 → Ch06 → Ch04 |
| Arc 2 | 2 | Sa → Su → Me | Ch07 → Ch08 → Ch09 → Ch07 |
| Arc 3 | 0 | Su → Me → Sa | Ch10 → Ch11 → Ch12 → Ch10 |
| Arc 4 | 1 | Me → Sa → Su | Ch13 → Ch14 → Ch15 → Ch13 |
| Arc 5 | 2 | Sa → Su → Me | Ch16 → Ch17 → Ch18 → Ch16 |
| Arc 6 | 0 | Su → Me → Sa | Ch19 → Ch20 → Ch21 → Ch19 |

## 4. Orbit Circle (Single Line)

Ch01 → Ch02 → Ch03 → Ch04 → ... → Ch20 → Ch21 → Ch01

## 5. Router Base Selectors

### LensBase(L)
| Lens | Hub |
|------|-----|
| S (Square) | AppC |
| F (Flower) | AppE |
| C (Cloud) | AppI |
| R (Fractal) | AppM |

### FacetBase(f)
| Facet | Hub |
|-------|-----|
| 1 (Objects) | AppA |
| 2 (Laws) | AppB |
| 3 (Constructions) | AppH |
| 4 (Certificates) | AppM |

### ArcHub(α)
| Arc | Hub |
|-----|-----|
| 0 | AppA |
| 1 | AppC |
| 2 | AppE |
| 3 | AppF |
| 4 | AppG |
| 5 | AppN |
| 6 | AppP |

## 6. Mandatory Signature

**Σ = {AppA, AppI, AppM}** — always enforced, never dropped.

## 7. Appendix Crystal Grid (4×4)

```
        Col 0    Col 1    Col 2    Col 3
Row 0   AppA     AppB     AppC     AppD      ← Square row
Row 1   AppE     AppF     AppG     AppH      ← Flower row
Row 2   AppI     AppJ     AppK     AppL      ← Cloud row
Row 3   AppM     AppN     AppO     AppP      ← Fractal row
```

## 8. HCRL Container Rotation

Default rotation order: **S → F → C → R**

Adjacent DUAL edges:
- S ↔ F
- F ↔ C
- C ↔ R
- R ↔ S

## 9. Truth Lattice

```
OK > NEAR > AMBIG > FAIL
Law: ABSTAIN > GUESS
```

## 10. TesseractHeader Template

Every chapter or atom-level output begins with:

```
[⊙Z_i↔Z* | ○Arc α | ○Rot ρ | △Lane ν | ⧈View L/* | ω=XX−1]
```

---

*21_4D_TESSERACT_BODY — Overlay Tables*
