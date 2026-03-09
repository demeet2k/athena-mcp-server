# CHAPTER TO APPENDIX EDGES

## Purpose

Maps each chapter to its deterministic routing hub chain (computed via Router v2).

## Edge Table

| EdgeID | Kind | Chapter | Primary Hub Chain | Hub Count |
|--------|------|---------|-------------------|-----------|
| E-CA-01 | REF | Ch01<0000> | AppA → AppC → AppI → AppM | 4 |
| E-CA-02 | REF | Ch02<0001> | AppA → AppC → AppB → AppI → AppM | 5 |
| E-CA-03 | REF | Ch03<0002> | AppA → AppI → AppM → AppJ | 4 |
| E-CA-04 | REF | Ch04<0003> | AppA → AppC → AppE → AppJ → AppI → AppM | 6 |
| E-CA-05 | REF | Ch05<0010> | AppA → AppC → AppI → AppB → AppL → AppM | 6 |
| E-CA-06 | REF | Ch06<0011> | AppA → AppC → AppI → AppM | 4 |
| E-CA-07 | REF | Ch07<0012> | AppA → AppE → AppH → AppL → AppI → AppM | 6 |
| E-CA-08 | REF | Ch08<0013> | AppA → AppE → AppM → AppB → AppJ → AppI | 6 |
| E-CA-09 | REF | Ch09<0020> | AppA → AppE → AppI → AppH → AppL → AppM | 6 |
| E-CA-10 | REF | Ch10<0021> | AppA → AppF → AppM → AppH → AppJ → AppI | 6 |
| E-CA-11 | REF | Ch11<0022> | AppA → AppF → AppM → AppL → AppI | 5 |
| E-CA-12 | REF | Ch12<0023> | AppA → AppF → AppC → AppM → AppI | 5 |
| E-CA-13 | REF | Ch13<0030> | AppA → AppG → AppE → AppM → AppJ → AppI | 6 |
| E-CA-14 | REF | Ch14<0031> | AppA → AppG → AppM → AppH → AppK → AppI | 6 |
| E-CA-15 | REF | Ch15<0032> | AppA → AppG → AppC → AppJ → AppI → AppM | 6 |
| E-CA-16 | REF | Ch16<0033> | AppA → AppN → AppM → AppK → AppI | 5 |
| E-CA-17 | REF | Ch17<0100> | AppA → AppN → AppE → AppJ → AppI → AppM | 6 |
| E-CA-18 | REF | Ch18<0101> | AppA → AppN → AppC → AppL → AppI → AppM | 6 |
| E-CA-19 | REF | Ch19<0102> | AppA → AppP → AppI → AppB → AppJ → AppM | 6 |
| E-CA-20 | REF | Ch20<0103> | AppA → AppP → AppE → AppL → AppI → AppM | 6 |
| E-CA-21 | REF | Ch21<0110> | AppA → AppP → AppM → AppL → AppI | 5 |

## Appendix Usage Frequency

| Appendix | Chapters Using It | Role |
|----------|-------------------|------|
| AppA | All 21 | Mandatory Σ (addressing) |
| AppI | All 21 | Mandatory Σ (corridors/truth) |
| AppM | All 21 | Mandatory Σ (replay) |
| AppC | Ch01-06, Ch12, Ch15, Ch18 (9) | LensBase(S) + ArcHub(1) |
| AppE | Ch04, Ch07-09, Ch13, Ch17, Ch20 (7) | LensBase(F) + ArcHub(2) |
| AppJ | Ch03-04, Ch08, Ch10, Ch13, Ch15, Ch17, Ch19 (8) | Truth overlay: NEAR |
| AppL | Ch05, Ch07, Ch09, Ch11, Ch18, Ch20-21 (7) | Truth overlay: AMBIG |
| AppF | Ch10-12 (3) | ArcHub(3) |
| AppG | Ch13-15 (3) | ArcHub(4) |
| AppN | Ch16-18 (3) | ArcHub(5) |
| AppP | Ch19-21 (3) | ArcHub(6) |
| AppB | Ch02, Ch05, Ch08, Ch19 (4) | FacetBase(2) |
| AppH | Ch07, Ch09-10, Ch14 (4) | FacetBase(3) |
| AppK | Ch14, Ch16 (2) | Truth overlay: FAIL |
| AppO | 0 (publish only) | Publication |
| AppD | 0 (registry) | Internal |
