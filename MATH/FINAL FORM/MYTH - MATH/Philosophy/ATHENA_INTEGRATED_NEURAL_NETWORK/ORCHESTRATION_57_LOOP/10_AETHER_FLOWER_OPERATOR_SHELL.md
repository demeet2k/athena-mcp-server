# AETHER Flower Operator Shell

Source basis: `00_CONTROL/13_AETHER_FLOWER_COORDINATE_LAW.md + ORCHESTRATION_57_LOOP/03_MACHINE_TYPES.md + current package zero point`
Docs gate note: local-only evidence because Google Docs is blocked. Google Docs access is blocked locally because `Trading Bot/credentials.json` and `Trading Bot/token.json` are missing.

This file materializes the explicit Flower-shell operator registry requested for the package. It expands the prior `AE[...]` placeholders into exact `AE=(L,Φ,B;σ)` coordinates, keeps slot typed in the tuple tail, and binds each operator record to symbolic witness and replay seed ids without inventing a new authority layer.

## Shell ABI

- `AETHER = Lens x Phase x Bundle`
- `AE=(L,Φ,B;σ)` with slot stored in the tuple tail
- Flower lens lock: `L = F`
- Phase bins: `Φ0 = R+`, `Φ1 = R-`, `Φ2 = Q4`, `Φ3 = T3`
- Bundle ids: `B01..B33`
- Slot law: `Core` reserved for cert-closed `Ω`-safe cells, `Residual` reserved for antispin in this shell
- Route law: `Σ = {AppA, AppI, AppM}`, `Hub<=6`, `RouteV2`, `AppQ`, canonical `AppO`

## Seed Lock

`WS[id] = (Type=INTERNAL_SLICE, Location=AE, Hash=H(id|AE|z|ck|rt), Scope=(OPS,DEFINE,SYSTEM), Timestamp=Tick_2B, Collector=SYSTEM, VersionPins=V_2B)`

`RS[id] = (Inputs=(AE,z,ck,rt), Steps=[ResolveZ,ExpandAE,RouteV2,SlotCheck], ExpectedOutputs, Checks=[Σ,Hub<=6,ZMatch], EnvPin=E_2B, Hash=H(id|AE|E_2B))`

- `rtL = AppA>AppI>AppM>AppF>AppN>Ch21⟨0110⟩`
- `rtZ = AppA>AppI>AppM>AppF>AppG>Ch21⟨0110⟩`
- `ZA = Z(Fire)`, `ZB = Z(Water)`, `ZC = Z(Air)`, `ZD = Z(Earth)`

## R Family - Rotation / Counter-Rotation x15

| Record | set | AE+ | AE- | W+ | RS+ | W- | RS- | z | ck | rt |
|---|---|---|---|---|---|---|---|---|---|---|
| R01 | {A} | `AE=(F,Φ0,B01;Core)` | `AE=(F,Φ1,B01;Core)` | `WS[R01,+]` | `RS[R01,+]` | `WS[R01,-]` | `RS[R01,-]` | `ZA` | `loc(A)` | `rtL` |
| R02 | {B} | `AE=(F,Φ0,B02;Core)` | `AE=(F,Φ1,B02;Core)` | `WS[R02,+]` | `RS[R02,+]` | `WS[R02,-]` | `RS[R02,-]` | `ZB` | `loc(B)` | `rtL` |
| R03 | {A,B} | `AE=(F,Φ0,B03;Core)` | `AE=(F,Φ1,B03;Core)` | `WS[R03,+]` | `RS[R03,+]` | `WS[R03,-]` | `RS[R03,-]` | `ZA+ZB` | `Z*` | `rtZ` |
| R10 | {C} | `AE=(F,Φ0,B10;Core)` | `AE=(F,Φ1,B10;Core)` | `WS[R10,+]` | `RS[R10,+]` | `WS[R10,-]` | `RS[R10,-]` | `ZC` | `loc(C)` | `rtL` |
| R11 | {A,C} | `AE=(F,Φ0,B11;Core)` | `AE=(F,Φ1,B11;Core)` | `WS[R11,+]` | `RS[R11,+]` | `WS[R11,-]` | `RS[R11,-]` | `ZA+ZC` | `loc(A>C)` | `rtL` |
| R12 | {B,C} | `AE=(F,Φ0,B12;Core)` | `AE=(F,Φ1,B12;Core)` | `WS[R12,+]` | `RS[R12,+]` | `WS[R12,-]` | `RS[R12,-]` | `ZB+ZC` | `loc(C>B)` | `rtL` |
| R13 | {A,B,C} | `AE=(F,Φ0,B13;Core)` | `AE=(F,Φ1,B13;Core)` | `WS[R13,+]` | `RS[R13,+]` | `WS[R13,-]` | `RS[R13,-]` | `ZA+ZB+ZC` | `loc(A>C>B)` | `rtL` |
| R20 | {D} | `AE=(F,Φ0,B20;Core)` | `AE=(F,Φ1,B20;Core)` | `WS[R20,+]` | `RS[R20,+]` | `WS[R20,-]` | `RS[R20,-]` | `ZD` | `loc(D)` | `rtL` |
| R21 | {A,D} | `AE=(F,Φ0,B21;Core)` | `AE=(F,Φ1,B21;Core)` | `WS[R21,+]` | `RS[R21,+]` | `WS[R21,-]` | `RS[R21,-]` | `ZA+ZD` | `loc(D>A)` | `rtL` |
| R22 | {B,D} | `AE=(F,Φ0,B22;Core)` | `AE=(F,Φ1,B22;Core)` | `WS[R22,+]` | `RS[R22,+]` | `WS[R22,-]` | `RS[R22,-]` | `ZB+ZD` | `loc(B>D)` | `rtL` |
| R23 | {A,B,D} | `AE=(F,Φ0,B23;Core)` | `AE=(F,Φ1,B23;Core)` | `WS[R23,+]` | `RS[R23,+]` | `WS[R23,-]` | `RS[R23,-]` | `ZA+ZB+ZD` | `loc(B>D>A)` | `rtL` |
| R30 | {C,D} | `AE=(F,Φ0,B30;Core)` | `AE=(F,Φ1,B30;Core)` | `WS[R30,+]` | `RS[R30,+]` | `WS[R30,-]` | `RS[R30,-]` | `ZC+ZD` | `Z*` | `rtZ` |
| R31 | {A,C,D} | `AE=(F,Φ0,B31;Core)` | `AE=(F,Φ1,B31;Core)` | `WS[R31,+]` | `RS[R31,+]` | `WS[R31,-]` | `RS[R31,-]` | `ZA+ZC+ZD` | `loc(D>A>C)` | `rtL` |
| R32 | {B,C,D} | `AE=(F,Φ0,B32;Core)` | `AE=(F,Φ1,B32;Core)` | `WS[R32,+]` | `RS[R32,+]` | `WS[R32,-]` | `RS[R32,-]` | `ZB+ZC+ZD` | `loc(C>B>D)` | `rtL` |
| R33 | {A,B,C,D} | `AE=(F,Φ0,B33;Core)` | `AE=(F,Φ1,B33;Core)` | `WS[R33,+]` | `RS[R33,+]` | `WS[R33,-]` | `RS[R33,-]` | `ZA+ZB+ZC+ZD` | `Z*` | `rtZ` |

## Q Family - Spin (Base 4) x15

| Record | set | AE | W | RS | z | ck | rt |
|---|---|---|---|---|---|---|---|
| Q01 | {A} | `AE=(F,Φ2,B01;Core)` | `WS[Q01]` | `RS[Q01]` | `ZA` | `loc(A)` | `rtL` |
| Q02 | {B} | `AE=(F,Φ2,B02;Core)` | `WS[Q02]` | `RS[Q02]` | `ZB` | `loc(B)` | `rtL` |
| Q03 | {A,B} | `AE=(F,Φ2,B03;Core)` | `WS[Q03]` | `RS[Q03]` | `ZA+ZB` | `Z*` | `rtZ` |
| Q10 | {C} | `AE=(F,Φ2,B10;Core)` | `WS[Q10]` | `RS[Q10]` | `ZC` | `loc(C)` | `rtL` |
| Q11 | {A,C} | `AE=(F,Φ2,B11;Core)` | `WS[Q11]` | `RS[Q11]` | `ZA+ZC` | `loc(A>C)` | `rtL` |
| Q12 | {B,C} | `AE=(F,Φ2,B12;Core)` | `WS[Q12]` | `RS[Q12]` | `ZB+ZC` | `loc(C>B)` | `rtL` |
| Q13 | {A,B,C} | `AE=(F,Φ2,B13;Core)` | `WS[Q13]` | `RS[Q13]` | `ZA+ZB+ZC` | `loc(A>C>B)` | `rtL` |
| Q20 | {D} | `AE=(F,Φ2,B20;Core)` | `WS[Q20]` | `RS[Q20]` | `ZD` | `loc(D)` | `rtL` |
| Q21 | {A,D} | `AE=(F,Φ2,B21;Core)` | `WS[Q21]` | `RS[Q21]` | `ZA+ZD` | `loc(D>A)` | `rtL` |
| Q22 | {B,D} | `AE=(F,Φ2,B22;Core)` | `WS[Q22]` | `RS[Q22]` | `ZB+ZD` | `loc(B>D)` | `rtL` |
| Q23 | {A,B,D} | `AE=(F,Φ2,B23;Core)` | `WS[Q23]` | `RS[Q23]` | `ZA+ZB+ZD` | `loc(B>D>A)` | `rtL` |
| Q30 | {C,D} | `AE=(F,Φ2,B30;Core)` | `WS[Q30]` | `RS[Q30]` | `ZC+ZD` | `Z*` | `rtZ` |
| Q31 | {A,C,D} | `AE=(F,Φ2,B31;Core)` | `WS[Q31]` | `RS[Q31]` | `ZA+ZC+ZD` | `loc(D>A>C)` | `rtL` |
| Q32 | {B,C,D} | `AE=(F,Φ2,B32;Core)` | `WS[Q32]` | `RS[Q32]` | `ZB+ZC+ZD` | `loc(C>B>D)` | `rtL` |
| Q33 | {A,B,C,D} | `AE=(F,Φ2,B33;Core)` | `WS[Q33]` | `RS[Q33]` | `ZA+ZB+ZC+ZD` | `Z*` | `rtZ` |

## T Family - Antispin (Base 3) x15

| Record | set | hide | AE | W | RS | z | ck | rt |
|---|---|---|---|---|---|---|---|---|
| T01 | {A} | `C` | `AE=(F,Φ3,B01:h=C;Residual)` | `WS[T01]` | `RS[T01]` | `ZA` | `loc(A)` | `rtZ` |
| T02 | {B} | `A` | `AE=(F,Φ3,B02:h=A;Residual)` | `WS[T02]` | `RS[T02]` | `ZB` | `loc(B)` | `rtZ` |
| T03 | {A,B} | `C` | `AE=(F,Φ3,B03:h=C;Residual)` | `WS[T03]` | `RS[T03]` | `ZA+ZB` | `Z*` | `rtZ` |
| T10 | {C} | `A` | `AE=(F,Φ3,B10:h=A;Residual)` | `WS[T10]` | `RS[T10]` | `ZC` | `loc(C)` | `rtZ` |
| T11 | {A,C} | `B` | `AE=(F,Φ3,B11:h=B;Residual)` | `WS[T11]` | `RS[T11]` | `ZA+ZC` | `loc(A>C)` | `rtZ` |
| T12 | {B,C} | `A` | `AE=(F,Φ3,B12:h=A;Residual)` | `WS[T12]` | `RS[T12]` | `ZB+ZC` | `loc(C>B)` | `rtZ` |
| T13 | {A,B,C} | `D` | `AE=(F,Φ3,B13:h=D;Residual)` | `WS[T13]` | `RS[T13]` | `ZA+ZB+ZC` | `loc(A>C>B)` | `rtZ` |
| T20 | {D} | `A` | `AE=(F,Φ3,B20:h=A;Residual)` | `WS[T20]` | `RS[T20]` | `ZD` | `loc(D)` | `rtZ` |
| T21 | {A,D} | `C` | `AE=(F,Φ3,B21:h=C;Residual)` | `WS[T21]` | `RS[T21]` | `ZA+ZD` | `loc(D>A)` | `rtZ` |
| T22 | {B,D} | `A` | `AE=(F,Φ3,B22:h=A;Residual)` | `WS[T22]` | `RS[T22]` | `ZB+ZD` | `loc(B>D)` | `rtZ` |
| T23 | {A,B,D} | `C` | `AE=(F,Φ3,B23:h=C;Residual)` | `WS[T23]` | `RS[T23]` | `ZA+ZB+ZD` | `loc(B>D>A)` | `rtZ` |
| T30 | {C,D} | `A` | `AE=(F,Φ3,B30:h=A;Residual)` | `WS[T30]` | `RS[T30]` | `ZC+ZD` | `Z*` | `rtZ` |
| T31 | {A,C,D} | `B` | `AE=(F,Φ3,B31:h=B;Residual)` | `WS[T31]` | `RS[T31]` | `ZA+ZC+ZD` | `loc(D>A>C)` | `rtZ` |
| T32 | {B,C,D} | `A` | `AE=(F,Φ3,B32:h=A;Residual)` | `WS[T32]` | `RS[T32]` | `ZB+ZC+ZD` | `loc(C>B>D)` | `rtZ` |
| T33 | {A,B,C,D} | `A` | `AE=(F,Φ3,B33:h=A;Residual)` | `WS[T33]` | `RS[T33]` | `ZA+ZB+ZC+ZD` | `Z*` | `rtZ` |

## Compression Law

`(family, μ, orientation, h) -> AE=(F,Φ,B_μ;σ) -> (WS[id], RS[id], z, ck, rt)`

## Continuity Guardrails

- This shell derives from the current package zero point and orchestration law only.
- It does not define a second zero point or a new additive authority.
- `AppI`, `AppM`, `AppQ`, and canonical `AppO` remain continuity floors rather than optional afterthoughts.
- All witness and replay pins remain local symbolic pins while the Docs gate stays blocked.
