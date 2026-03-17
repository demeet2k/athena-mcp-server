# 2/65-65/65 RQT Z-Star Aether Nesting Layer

## Fixed Law Header

- Docs gate: `BLOCKED`
- Ring gauge: `A=Fire, C=Air, B=Water, D=Earth`
- Ring order: `A -> C -> B -> D -> A`
- Opposite-pole law: `forbidden_direct_opposite_except_via_zstar`
- Sigma: `{AppA, AppI, AppM}`
- Rotation carrier: `AppF`
- Rail and antispin carrier: `AppG`
- Bridge hub: `AppC`
- Hide default: `first missing pole in ring order A->C->B->D`, default `A` when none is missing

## Address Law

- Dense-shell family prefix: `2`
- Class digits: `R=1`, `Q=2`, `T=3`
- Record gate form: `Gate<2 c mu>`
- Examples: `R01 -> Gate<2101>`, `Q13 -> Gate<2213>`, `T33 -> Gate<2333>`
- Visible `21/65` through `65/65` shell slots remain presentation indices only.

## R Table

| id | gate | mu | src | hide | hub | z* / aether signature | prior metro witness | truth |
|---|---|---|---|---|---|---|---|---|
| `R01` | `Gate<2101>` | `01` | `A` | `-` | `AppF` | `Z(Fire) -> Z* -> Aether via AppA -> AppF -> AppC -> AppI -> AppM` | `S01 :: AppA -> AppF -> AppC -> AppI -> AppM` | `NEAR` |
| `R02` | `Gate<2102>` | `02` | `B` | `-` | `AppF` | `Z(Water) -> Z* -> Aether via AppA -> AppF -> AppC -> AppI -> AppM` | `S02 :: AppA -> AppF -> AppC -> AppI -> AppM` | `NEAR` |
| `R03` | `Gate<2103>` | `03` | `A,B` | `-` | `AppF` | `Z(Fire) + Z(Water) -> Z* -> Aether via AppA -> AppF -> AppC -> AppI -> AppM` | `S03 :: AppA -> AppF -> AppC -> AppI -> AppM` | `NEAR` |
| `R10` | `Gate<2110>` | `10` | `C` | `-` | `AppF` | `Z(Air) -> Z* -> Aether via AppA -> AppF -> AppC -> AppI -> AppM` | `S10 :: AppA -> AppF -> AppC -> AppI -> AppM` | `NEAR` |
| `R11` | `Gate<2111>` | `11` | `A,C` | `-` | `AppF` | `Z(Fire) + Z(Air) -> Z* -> Aether via AppA -> AppF -> AppC -> AppI -> AppM` | `S11 :: AppA -> AppF -> AppC -> AppI -> AppM` | `NEAR` |
| `R12` | `Gate<2112>` | `12` | `B,C` | `-` | `AppF` | `Z(Air) + Z(Water) -> Z* -> Aether via AppA -> AppF -> AppC -> AppI -> AppM` | `S12 :: AppA -> AppF -> AppC -> AppI -> AppM` | `NEAR` |
| `R13` | `Gate<2113>` | `13` | `A,B,C` | `-` | `AppF` | `Z(Fire) + Z(Air) + Z(Water) -> Z* -> Aether via AppA -> AppF -> AppC -> AppI -> AppM` | `S13 :: AppA -> AppF -> AppC -> AppI -> AppM` | `NEAR` |
| `R20` | `Gate<2120>` | `20` | `D` | `-` | `AppF` | `Z(Earth) -> Z* -> Aether via AppA -> AppF -> AppC -> AppI -> AppM` | `S20 :: AppA -> AppF -> AppC -> AppI -> AppM` | `NEAR` |
| `R21` | `Gate<2121>` | `21` | `A,D` | `-` | `AppF` | `Z(Fire) + Z(Earth) -> Z* -> Aether via AppA -> AppF -> AppC -> AppI -> AppM` | `S21 :: AppA -> AppF -> AppC -> AppI -> AppM` | `NEAR` |
| `R22` | `Gate<2122>` | `22` | `B,D` | `-` | `AppF` | `Z(Water) + Z(Earth) -> Z* -> Aether via AppA -> AppF -> AppC -> AppI -> AppM` | `S22 :: AppA -> AppF -> AppC -> AppI -> AppM` | `NEAR` |
| `R23` | `Gate<2123>` | `23` | `A,B,D` | `-` | `AppF` | `Z(Fire) + Z(Water) + Z(Earth) -> Z* -> Aether via AppA -> AppF -> AppC -> AppI -> AppM` | `S23 :: AppA -> AppF -> AppC -> AppI -> AppM` | `NEAR` |
| `R30` | `Gate<2130>` | `30` | `C,D` | `-` | `AppF` | `Z(Air) + Z(Earth) -> Z* -> Aether via AppA -> AppF -> AppC -> AppI -> AppM` | `S30 :: AppA -> AppF -> AppC -> AppI -> AppM` | `NEAR` |
| `R31` | `Gate<2131>` | `31` | `A,C,D` | `-` | `AppF` | `Z(Fire) + Z(Air) + Z(Earth) -> Z* -> Aether via AppA -> AppF -> AppC -> AppI -> AppM` | `S31 :: AppA -> AppF -> AppC -> AppI -> AppM` | `NEAR` |
| `R32` | `Gate<2132>` | `32` | `B,C,D` | `-` | `AppF` | `Z(Air) + Z(Water) + Z(Earth) -> Z* -> Aether via AppA -> AppF -> AppC -> AppI -> AppM` | `S32 :: AppA -> AppF -> AppC -> AppI -> AppM` | `NEAR` |
| `R33` | `Gate<2133>` | `33` | `A,B,C,D` | `-` | `AppF` | `Z(Fire) + Z(Air) + Z(Water) + Z(Earth) -> Z* -> Aether via AppA -> AppF -> AppC -> AppI -> AppM` | `S33 :: AppA -> AppF -> AppC -> AppI -> AppM` | `NEAR` |

## Q Table

| id | gate | mu | src | hide | hub | z* / aether signature | prior metro witness | truth |
|---|---|---|---|---|---|---|---|---|
| `Q01` | `Gate<2201>` | `01` | `A` | `-` | `AppF` | `Z(Fire) -> Z* -> Aether via AppA -> AppF -> AppC -> AppI -> AppM` | `R01 :: AppA -> AppF -> AppC -> AppI -> AppM` | `NEAR` |
| `Q02` | `Gate<2202>` | `02` | `B` | `-` | `AppF` | `Z(Water) -> Z* -> Aether via AppA -> AppF -> AppC -> AppI -> AppM` | `R02 :: AppA -> AppF -> AppC -> AppI -> AppM` | `NEAR` |
| `Q03` | `Gate<2203>` | `03` | `A,B` | `-` | `AppF` | `Z(Fire) + Z(Water) -> Z* -> Aether via AppA -> AppF -> AppC -> AppI -> AppM` | `R03 :: AppA -> AppF -> AppC -> AppI -> AppM` | `NEAR` |
| `Q10` | `Gate<2210>` | `10` | `C` | `-` | `AppF` | `Z(Air) -> Z* -> Aether via AppA -> AppF -> AppC -> AppI -> AppM` | `R10 :: AppA -> AppF -> AppC -> AppI -> AppM` | `NEAR` |
| `Q11` | `Gate<2211>` | `11` | `A,C` | `-` | `AppF` | `Z(Fire) + Z(Air) -> Z* -> Aether via AppA -> AppF -> AppC -> AppI -> AppM` | `R11 :: AppA -> AppF -> AppC -> AppI -> AppM` | `NEAR` |
| `Q12` | `Gate<2212>` | `12` | `B,C` | `-` | `AppF` | `Z(Air) + Z(Water) -> Z* -> Aether via AppA -> AppF -> AppC -> AppI -> AppM` | `R12 :: AppA -> AppF -> AppC -> AppI -> AppM` | `NEAR` |
| `Q13` | `Gate<2213>` | `13` | `A,B,C` | `-` | `AppF` | `Z(Fire) + Z(Air) + Z(Water) -> Z* -> Aether via AppA -> AppF -> AppC -> AppI -> AppM` | `R13 :: AppA -> AppF -> AppC -> AppI -> AppM` | `NEAR` |
| `Q20` | `Gate<2220>` | `20` | `D` | `-` | `AppF` | `Z(Earth) -> Z* -> Aether via AppA -> AppF -> AppC -> AppI -> AppM` | `R20 :: AppA -> AppF -> AppC -> AppI -> AppM` | `NEAR` |
| `Q21` | `Gate<2221>` | `21` | `A,D` | `-` | `AppF` | `Z(Fire) + Z(Earth) -> Z* -> Aether via AppA -> AppF -> AppC -> AppI -> AppM` | `R21 :: AppA -> AppF -> AppC -> AppI -> AppM` | `NEAR` |
| `Q22` | `Gate<2222>` | `22` | `B,D` | `-` | `AppF` | `Z(Water) + Z(Earth) -> Z* -> Aether via AppA -> AppF -> AppC -> AppI -> AppM` | `R22 :: AppA -> AppF -> AppC -> AppI -> AppM` | `NEAR` |
| `Q23` | `Gate<2223>` | `23` | `A,B,D` | `-` | `AppF` | `Z(Fire) + Z(Water) + Z(Earth) -> Z* -> Aether via AppA -> AppF -> AppC -> AppI -> AppM` | `R23 :: AppA -> AppF -> AppC -> AppI -> AppM` | `NEAR` |
| `Q30` | `Gate<2230>` | `30` | `C,D` | `-` | `AppF` | `Z(Air) + Z(Earth) -> Z* -> Aether via AppA -> AppF -> AppC -> AppI -> AppM` | `R30 :: AppA -> AppF -> AppC -> AppI -> AppM` | `NEAR` |
| `Q31` | `Gate<2231>` | `31` | `A,C,D` | `-` | `AppF` | `Z(Fire) + Z(Air) + Z(Earth) -> Z* -> Aether via AppA -> AppF -> AppC -> AppI -> AppM` | `R31 :: AppA -> AppF -> AppC -> AppI -> AppM` | `NEAR` |
| `Q32` | `Gate<2232>` | `32` | `B,C,D` | `-` | `AppF` | `Z(Air) + Z(Water) + Z(Earth) -> Z* -> Aether via AppA -> AppF -> AppC -> AppI -> AppM` | `R32 :: AppA -> AppF -> AppC -> AppI -> AppM` | `NEAR` |
| `Q33` | `Gate<2233>` | `33` | `A,B,C,D` | `-` | `AppF` | `Z(Fire) + Z(Air) + Z(Water) + Z(Earth) -> Z* -> Aether via AppA -> AppF -> AppC -> AppI -> AppM` | `R33 :: AppA -> AppF -> AppC -> AppI -> AppM` | `NEAR` |

## T Table

| id | gate | mu | src | hide | hub | z* / aether signature | prior metro witness | truth |
|---|---|---|---|---|---|---|---|---|
| `T01` | `Gate<2301>` | `01` | `A` | `C` | `AppG` | `Z(Fire) -> Z* -> Aether via AppA -> AppG -> AppC -> AppI -> AppM` | `S01 :: AppA -> AppG -> AppC -> AppI -> AppM` | `NEAR` |
| `T02` | `Gate<2302>` | `02` | `B` | `A` | `AppG` | `Z(Water) -> Z* -> Aether via AppA -> AppG -> AppC -> AppI -> AppM` | `S02 :: AppA -> AppG -> AppC -> AppI -> AppM` | `NEAR` |
| `T03` | `Gate<2303>` | `03` | `A,B` | `C` | `AppG` | `Z(Fire) + Z(Water) -> Z* -> Aether via AppA -> AppG -> AppC -> AppI -> AppM` | `S03 :: AppA -> AppG -> AppC -> AppI -> AppM` | `NEAR` |
| `T10` | `Gate<2310>` | `10` | `C` | `A` | `AppG` | `Z(Air) -> Z* -> Aether via AppA -> AppG -> AppC -> AppI -> AppM` | `S10 :: AppA -> AppG -> AppC -> AppI -> AppM` | `NEAR` |
| `T11` | `Gate<2311>` | `11` | `A,C` | `B` | `AppG` | `Z(Fire) + Z(Air) -> Z* -> Aether via AppA -> AppG -> AppC -> AppI -> AppM` | `S11 :: AppA -> AppG -> AppC -> AppI -> AppM` | `NEAR` |
| `T12` | `Gate<2312>` | `12` | `B,C` | `A` | `AppG` | `Z(Air) + Z(Water) -> Z* -> Aether via AppA -> AppG -> AppC -> AppI -> AppM` | `S12 :: AppA -> AppG -> AppC -> AppI -> AppM` | `NEAR` |
| `T13` | `Gate<2313>` | `13` | `A,B,C` | `D` | `AppG` | `Z(Fire) + Z(Air) + Z(Water) -> Z* -> Aether via AppA -> AppG -> AppC -> AppI -> AppM` | `S13 :: AppA -> AppG -> AppC -> AppI -> AppM` | `NEAR` |
| `T20` | `Gate<2320>` | `20` | `D` | `A` | `AppG` | `Z(Earth) -> Z* -> Aether via AppA -> AppG -> AppC -> AppI -> AppM` | `S20 :: AppA -> AppG -> AppC -> AppI -> AppM` | `NEAR` |
| `T21` | `Gate<2321>` | `21` | `A,D` | `C` | `AppG` | `Z(Fire) + Z(Earth) -> Z* -> Aether via AppA -> AppG -> AppC -> AppI -> AppM` | `S21 :: AppA -> AppG -> AppC -> AppI -> AppM` | `NEAR` |
| `T22` | `Gate<2322>` | `22` | `B,D` | `A` | `AppG` | `Z(Water) + Z(Earth) -> Z* -> Aether via AppA -> AppG -> AppC -> AppI -> AppM` | `S22 :: AppA -> AppG -> AppC -> AppI -> AppM` | `NEAR` |
| `T23` | `Gate<2323>` | `23` | `A,B,D` | `C` | `AppG` | `Z(Fire) + Z(Water) + Z(Earth) -> Z* -> Aether via AppA -> AppG -> AppC -> AppI -> AppM` | `S23 :: AppA -> AppG -> AppC -> AppI -> AppM` | `NEAR` |
| `T30` | `Gate<2330>` | `30` | `C,D` | `A` | `AppG` | `Z(Air) + Z(Earth) -> Z* -> Aether via AppA -> AppG -> AppC -> AppI -> AppM` | `S30 :: AppA -> AppG -> AppC -> AppI -> AppM` | `NEAR` |
| `T31` | `Gate<2331>` | `31` | `A,C,D` | `B` | `AppG` | `Z(Fire) + Z(Air) + Z(Earth) -> Z* -> Aether via AppA -> AppG -> AppC -> AppI -> AppM` | `S31 :: AppA -> AppG -> AppC -> AppI -> AppM` | `NEAR` |
| `T32` | `Gate<2332>` | `32` | `B,C,D` | `A` | `AppG` | `Z(Air) + Z(Water) + Z(Earth) -> Z* -> Aether via AppA -> AppG -> AppC -> AppI -> AppM` | `S32 :: AppA -> AppG -> AppC -> AppI -> AppM` | `NEAR` |
| `T33` | `Gate<2333>` | `33` | `A,B,C,D` | `A` | `AppG` | `Z(Fire) + Z(Air) + Z(Water) + Z(Earth) -> Z* -> Aether via AppA -> AppG -> AppC -> AppI -> AppM` | `S33 :: AppA -> AppG -> AppC -> AppI -> AppM` | `NEAR` |

## Compact Witness And Replay Notes

- Every record inherits `Sigma = {AppA, AppI, AppM}` and adds the lawful carrier hub plus `AppC` as bridge hub.
- `R(mu)` witnesses back to `S(mu)`; `Q(mu)` witnesses back to `R(mu)`; `T(mu)` witnesses back to `S(mu)`.
- `R/Q` land through `AppA -> AppF -> AppC -> AppI -> AppM`.
- `T` lands through `AppA -> AppG -> AppC -> AppI -> AppM`.
- This shell is metadata attachment only. It does not rewrite the sealed `P` or `S` records and does not alter the user-fixed `R/Q/T` math.

SUPPLEMENT - RQT Z-Star Aether Transfer Shell
