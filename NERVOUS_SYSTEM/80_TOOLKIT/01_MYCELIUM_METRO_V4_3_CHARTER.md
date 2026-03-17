# Mycelium Metro v4.3 Charter

Status: Canonical routing law for additive tesseract v4.3.
Profile: mycelium-metro-v4.3

## Invariants

- Local address syntax remains canonical:
  - `ChXX<dddd>.<Lens><Facet>.<Atom>`
  - `AppX.<Lens><Facet>.<Atom>`
- Global address syntax remains canonical:
  - `Ms<mmmm>::LocalAddr`
- The local crystal remains a full `4^4` tile with lenses `S/F/C/R`, facets `1..4`, and atoms `a..d`.
- New behavior is overlay-only and does not rewrite `LocalAddr`.

## Tesseract Header

`[Z_i <-> Z* | Arc alpha | Rot rho | Lane nu | View L/* | omega=n]`

## Overlay Coordinates

- `omega = XX - 1`
- `alpha = floor(omega / 3)`
- `rho = alpha mod 3`
- `nu = Triad[(k + rho) mod 3]` with `Triad = [Su, Me, Sa]`

## Chapter Overlay Table

| Chapter | Station | omega | Arc | Rot | Lane |
| --- | --- | ---: | ---: | ---: | --- |
| Ch01 | Ch01<0000> | 0 | 0 | 0 | Su |
| Ch02 | Ch02<0001> | 1 | 0 | 0 | Me |
| Ch03 | Ch03<0002> | 2 | 0 | 0 | Sa |
| Ch04 | Ch04<0003> | 3 | 1 | 1 | Me |
| Ch05 | Ch05<0010> | 4 | 1 | 1 | Sa |
| Ch06 | Ch06<0011> | 5 | 1 | 1 | Su |
| Ch07 | Ch07<0012> | 6 | 2 | 2 | Sa |
| Ch08 | Ch08<0013> | 7 | 2 | 2 | Su |
| Ch09 | Ch09<0020> | 8 | 2 | 2 | Me |
| Ch10 | Ch10<0021> | 9 | 3 | 0 | Su |
| Ch11 | Ch11<0022> | 10 | 3 | 0 | Me |
| Ch12 | Ch12<0023> | 11 | 3 | 0 | Sa |
| Ch13 | Ch13<0030> | 12 | 4 | 1 | Me |
| Ch14 | Ch14<0031> | 13 | 4 | 1 | Sa |
| Ch15 | Ch15<0032> | 14 | 4 | 1 | Su |
| Ch16 | Ch16<0033> | 15 | 5 | 2 | Sa |
| Ch17 | Ch17<0100> | 16 | 5 | 2 | Su |
| Ch18 | Ch18<0101> | 17 | 5 | 2 | Me |
| Ch19 | Ch19<0102> | 18 | 6 | 0 | Su |
| Ch20 | Ch20<0103> | 19 | 6 | 0 | Me |
| Ch21 | Ch21<0110> | 20 | 6 | 0 | Sa |

## Router Constants

- `S -> AppC`, `F -> AppE`, `C -> AppI`, `R -> AppM`
- `1 -> AppA`, `2 -> AppB`, `3 -> AppH`, `4 -> AppM`
- `Arc0 -> AppA`, `Arc1 -> AppC`, `Arc2 -> AppE`, `Arc3 -> AppF`, `Arc4 -> AppG`, `Arc5 -> AppN`, `Arc6 -> AppP`
- `Sigma = {AppA, AppI, AppM}`
- `unique hubs <= 6`
- `S -> F -> C -> R`

## RoutePlan Contract

Every executable route plan in v4.3 must expose `Target`, `TesseractHeader`, `HubsSeq`, `HCRLPass`, `TunnelPlan`, `TruthIntent`, `Obligations`, and `DropLog`.
