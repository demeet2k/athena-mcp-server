# AETHER Symbolic Resolver

Source basis: `00_CONTROL/14_AETHER_RESOLVER_LAW.md + ORCHESTRATION_57_LOOP/10_AETHER_FLOWER_OPERATOR_SHELL.md + ORCHESTRATION_57_LOOP/11_AETHER_WITNESS_REPLAY_PAYLOADS.md`
Docs gate note: local-only evidence because Google Docs is blocked. Google Docs access is blocked locally because `Trading Bot/credentials.json` and `Trading Bot/token.json` are missing.

This file is the local symbolic-plus-local resolver layer above the Flower shell. It dereferences checkpoint atoms into elemental anchors, parses every `loc(...)` expression as an ordered chain, resolves route aliases into local appendix nodes plus the explicit external-symbolic `Ch21⟨0110⟩` tail, and keeps `Z*` as wildcard rather than forcing it into false concreteness.

## Checkpoint Atom Map

| Atom | Local elemental anchor |
|---|---|
| `A` | `FIRE/01_fire_full_corpus_pass.md` |
| `B` | `WATER/01_water_full_corpus_pass.md` |
| `C` | `AIR/01_air_full_corpus_pass.md` |
| `D` | `EARTH/01_earth_full_corpus_pass.md` |

## Route Alias Map

| Alias | Local appendix chain | External tail | Hub count | Sigma ok |
|---|---|---|---|---|
| `rtL` | `AppA:APPENDIX_CRYSTAL/AppA_addressing_and_grammar.md -> AppI:APPENDIX_CRYSTAL/AppI_corridor_lattice.md -> AppM:APPENDIX_CRYSTAL/AppM_replay_kernel.md -> AppF:APPENDIX_CRYSTAL/AppF_transport_and_dual_law.md -> AppN:APPENDIX_CRYSTAL/AppN_container_and_compression_formats.md` | `Ch21⟨0110⟩` | `6` | `True` |
| `rtZ` | `AppA:APPENDIX_CRYSTAL/AppA_addressing_and_grammar.md -> AppI:APPENDIX_CRYSTAL/AppI_corridor_lattice.md -> AppM:APPENDIX_CRYSTAL/AppM_replay_kernel.md -> AppF:APPENDIX_CRYSTAL/AppF_transport_and_dual_law.md -> AppG:APPENDIX_CRYSTAL/AppG_triangle_control_and_recursion.md` | `Ch21⟨0110⟩` | `6` | `True` |

## Resolved Record Table

| Record | AE refs | z resolution | ck resolution | route alias | external tail | hidden pole | continuity |
|---|---|---|---|---|---|---|---|
| R01 | `+:AE=(F,Φ0,B01;Core), -:AE=(F,Φ1,B01;Core)` | `ZA:1` | `A` | `rtL` | `Ch21⟨0110⟩` | `none` | `AppI,AppM,AppQ,AppO` |
| R02 | `+:AE=(F,Φ0,B02;Core), -:AE=(F,Φ1,B02;Core)` | `ZB:1` | `B` | `rtL` | `Ch21⟨0110⟩` | `none` | `AppI,AppM,AppQ,AppO` |
| R03 | `+:AE=(F,Φ0,B03;Core), -:AE=(F,Φ1,B03;Core)` | `ZA+ZB:2` | `*` | `rtZ` | `Ch21⟨0110⟩` | `none` | `AppI,AppM,AppQ,AppO` |
| R10 | `+:AE=(F,Φ0,B10;Core), -:AE=(F,Φ1,B10;Core)` | `ZC:1` | `C` | `rtL` | `Ch21⟨0110⟩` | `none` | `AppI,AppM,AppQ,AppO` |
| R11 | `+:AE=(F,Φ0,B11;Core), -:AE=(F,Φ1,B11;Core)` | `ZA+ZC:2` | `A>C` | `rtL` | `Ch21⟨0110⟩` | `none` | `AppI,AppM,AppQ,AppO` |
| R12 | `+:AE=(F,Φ0,B12;Core), -:AE=(F,Φ1,B12;Core)` | `ZB+ZC:2` | `C>B` | `rtL` | `Ch21⟨0110⟩` | `none` | `AppI,AppM,AppQ,AppO` |
| R13 | `+:AE=(F,Φ0,B13;Core), -:AE=(F,Φ1,B13;Core)` | `ZA+ZB+ZC:3` | `A>C>B` | `rtL` | `Ch21⟨0110⟩` | `none` | `AppI,AppM,AppQ,AppO` |
| R20 | `+:AE=(F,Φ0,B20;Core), -:AE=(F,Φ1,B20;Core)` | `ZD:1` | `D` | `rtL` | `Ch21⟨0110⟩` | `none` | `AppI,AppM,AppQ,AppO` |
| R21 | `+:AE=(F,Φ0,B21;Core), -:AE=(F,Φ1,B21;Core)` | `ZA+ZD:2` | `D>A` | `rtL` | `Ch21⟨0110⟩` | `none` | `AppI,AppM,AppQ,AppO` |
| R22 | `+:AE=(F,Φ0,B22;Core), -:AE=(F,Φ1,B22;Core)` | `ZB+ZD:2` | `B>D` | `rtL` | `Ch21⟨0110⟩` | `none` | `AppI,AppM,AppQ,AppO` |
| R23 | `+:AE=(F,Φ0,B23;Core), -:AE=(F,Φ1,B23;Core)` | `ZA+ZB+ZD:3` | `B>D>A` | `rtL` | `Ch21⟨0110⟩` | `none` | `AppI,AppM,AppQ,AppO` |
| R30 | `+:AE=(F,Φ0,B30;Core), -:AE=(F,Φ1,B30;Core)` | `ZC+ZD:2` | `*` | `rtZ` | `Ch21⟨0110⟩` | `none` | `AppI,AppM,AppQ,AppO` |
| R31 | `+:AE=(F,Φ0,B31;Core), -:AE=(F,Φ1,B31;Core)` | `ZA+ZC+ZD:3` | `D>A>C` | `rtL` | `Ch21⟨0110⟩` | `none` | `AppI,AppM,AppQ,AppO` |
| R32 | `+:AE=(F,Φ0,B32;Core), -:AE=(F,Φ1,B32;Core)` | `ZB+ZC+ZD:3` | `C>B>D` | `rtL` | `Ch21⟨0110⟩` | `none` | `AppI,AppM,AppQ,AppO` |
| R33 | `+:AE=(F,Φ0,B33;Core), -:AE=(F,Φ1,B33;Core)` | `ZA+ZB+ZC+ZD:4` | `*` | `rtZ` | `Ch21⟨0110⟩` | `none` | `AppI,AppM,AppQ,AppO` |
| Q01 | `single:AE=(F,Φ2,B01;Core)` | `ZA:1` | `A` | `rtL` | `Ch21⟨0110⟩` | `none` | `AppI,AppM,AppQ,AppO` |
| Q02 | `single:AE=(F,Φ2,B02;Core)` | `ZB:1` | `B` | `rtL` | `Ch21⟨0110⟩` | `none` | `AppI,AppM,AppQ,AppO` |
| Q03 | `single:AE=(F,Φ2,B03;Core)` | `ZA+ZB:2` | `*` | `rtZ` | `Ch21⟨0110⟩` | `none` | `AppI,AppM,AppQ,AppO` |
| Q10 | `single:AE=(F,Φ2,B10;Core)` | `ZC:1` | `C` | `rtL` | `Ch21⟨0110⟩` | `none` | `AppI,AppM,AppQ,AppO` |
| Q11 | `single:AE=(F,Φ2,B11;Core)` | `ZA+ZC:2` | `A>C` | `rtL` | `Ch21⟨0110⟩` | `none` | `AppI,AppM,AppQ,AppO` |
| Q12 | `single:AE=(F,Φ2,B12;Core)` | `ZB+ZC:2` | `C>B` | `rtL` | `Ch21⟨0110⟩` | `none` | `AppI,AppM,AppQ,AppO` |
| Q13 | `single:AE=(F,Φ2,B13;Core)` | `ZA+ZB+ZC:3` | `A>C>B` | `rtL` | `Ch21⟨0110⟩` | `none` | `AppI,AppM,AppQ,AppO` |
| Q20 | `single:AE=(F,Φ2,B20;Core)` | `ZD:1` | `D` | `rtL` | `Ch21⟨0110⟩` | `none` | `AppI,AppM,AppQ,AppO` |
| Q21 | `single:AE=(F,Φ2,B21;Core)` | `ZA+ZD:2` | `D>A` | `rtL` | `Ch21⟨0110⟩` | `none` | `AppI,AppM,AppQ,AppO` |
| Q22 | `single:AE=(F,Φ2,B22;Core)` | `ZB+ZD:2` | `B>D` | `rtL` | `Ch21⟨0110⟩` | `none` | `AppI,AppM,AppQ,AppO` |
| Q23 | `single:AE=(F,Φ2,B23;Core)` | `ZA+ZB+ZD:3` | `B>D>A` | `rtL` | `Ch21⟨0110⟩` | `none` | `AppI,AppM,AppQ,AppO` |
| Q30 | `single:AE=(F,Φ2,B30;Core)` | `ZC+ZD:2` | `*` | `rtZ` | `Ch21⟨0110⟩` | `none` | `AppI,AppM,AppQ,AppO` |
| Q31 | `single:AE=(F,Φ2,B31;Core)` | `ZA+ZC+ZD:3` | `D>A>C` | `rtL` | `Ch21⟨0110⟩` | `none` | `AppI,AppM,AppQ,AppO` |
| Q32 | `single:AE=(F,Φ2,B32;Core)` | `ZB+ZC+ZD:3` | `C>B>D` | `rtL` | `Ch21⟨0110⟩` | `none` | `AppI,AppM,AppQ,AppO` |
| Q33 | `single:AE=(F,Φ2,B33;Core)` | `ZA+ZB+ZC+ZD:4` | `*` | `rtZ` | `Ch21⟨0110⟩` | `none` | `AppI,AppM,AppQ,AppO` |
| T01 | `single:AE=(F,Φ3,B01:h=C;Residual)` | `ZA:1` | `A` | `rtZ` | `Ch21⟨0110⟩` | `C` | `AppI,AppM,AppQ,AppO` |
| T02 | `single:AE=(F,Φ3,B02:h=A;Residual)` | `ZB:1` | `B` | `rtZ` | `Ch21⟨0110⟩` | `A` | `AppI,AppM,AppQ,AppO` |
| T03 | `single:AE=(F,Φ3,B03:h=C;Residual)` | `ZA+ZB:2` | `*` | `rtZ` | `Ch21⟨0110⟩` | `C` | `AppI,AppM,AppQ,AppO` |
| T10 | `single:AE=(F,Φ3,B10:h=A;Residual)` | `ZC:1` | `C` | `rtZ` | `Ch21⟨0110⟩` | `A` | `AppI,AppM,AppQ,AppO` |
| T11 | `single:AE=(F,Φ3,B11:h=B;Residual)` | `ZA+ZC:2` | `A>C` | `rtZ` | `Ch21⟨0110⟩` | `B` | `AppI,AppM,AppQ,AppO` |
| T12 | `single:AE=(F,Φ3,B12:h=A;Residual)` | `ZB+ZC:2` | `C>B` | `rtZ` | `Ch21⟨0110⟩` | `A` | `AppI,AppM,AppQ,AppO` |
| T13 | `single:AE=(F,Φ3,B13:h=D;Residual)` | `ZA+ZB+ZC:3` | `A>C>B` | `rtZ` | `Ch21⟨0110⟩` | `D` | `AppI,AppM,AppQ,AppO` |
| T20 | `single:AE=(F,Φ3,B20:h=A;Residual)` | `ZD:1` | `D` | `rtZ` | `Ch21⟨0110⟩` | `A` | `AppI,AppM,AppQ,AppO` |
| T21 | `single:AE=(F,Φ3,B21:h=C;Residual)` | `ZA+ZD:2` | `D>A` | `rtZ` | `Ch21⟨0110⟩` | `C` | `AppI,AppM,AppQ,AppO` |
| T22 | `single:AE=(F,Φ3,B22:h=A;Residual)` | `ZB+ZD:2` | `B>D` | `rtZ` | `Ch21⟨0110⟩` | `A` | `AppI,AppM,AppQ,AppO` |
| T23 | `single:AE=(F,Φ3,B23:h=C;Residual)` | `ZA+ZB+ZD:3` | `B>D>A` | `rtZ` | `Ch21⟨0110⟩` | `C` | `AppI,AppM,AppQ,AppO` |
| T30 | `single:AE=(F,Φ3,B30:h=A;Residual)` | `ZC+ZD:2` | `*` | `rtZ` | `Ch21⟨0110⟩` | `A` | `AppI,AppM,AppQ,AppO` |
| T31 | `single:AE=(F,Φ3,B31:h=B;Residual)` | `ZA+ZC+ZD:3` | `D>A>C` | `rtZ` | `Ch21⟨0110⟩` | `B` | `AppI,AppM,AppQ,AppO` |
| T32 | `single:AE=(F,Φ3,B32:h=A;Residual)` | `ZB+ZC+ZD:3` | `C>B>D` | `rtZ` | `Ch21⟨0110⟩` | `A` | `AppI,AppM,AppQ,AppO` |
| T33 | `single:AE=(F,Φ3,B33:h=A;Residual)` | `ZA+ZB+ZC+ZD:4` | `*` | `rtZ` | `Ch21⟨0110⟩` | `A` | `AppI,AppM,AppQ,AppO` |

## Continuity Guardrails

- The Flower shell remains authoritative; the resolver is downstream of it.
- `AppI`, `AppM`, `AppQ`, and canonical `AppO` remain continuity floors.
- `Z*` remains explicit wildcard, not a fabricated local pointer.
- `Ch21⟨0110⟩` remains an external-symbolic witness tail because no canonical local package target exists yet.

## Zero-point Compression

At zero point, the resolver keeps only the lawful dereference surface that can turn symbolic AETHER fields into honest local lookup paths without collapsing what remains external.
