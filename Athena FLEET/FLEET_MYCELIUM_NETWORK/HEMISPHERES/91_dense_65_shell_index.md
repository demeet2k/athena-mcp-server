# Dense 65 Shell Index

- `prior_seed_position`: `1/65`
- `header_record_id`: `H00`
- `docs_gate_status`: `BLOCKED`
- sealed shell rows: `65`
- sigma path: `AppA -> AppI -> AppM`
- rotation authority: `AppF`
- antispin authority: `AppG`
- hidden pole rule: `first missing pole in A -> C -> B -> D, default A`
- primary witness cap per cell: `8`
- matched records: `32`
- abstained records: `1193`

| Family | Row Count |
| --- | --- |
| H | 1 |
| P | 4 |
| S | 15 |
| R | 15 |
| Q | 15 |
| T | 15 |

## Sealed Shell

| Address | Record | Family | Payload |
| --- | --- | --- | --- |
| 1/65 | H00 | H | prior seed/header shell |
| 2/65 | P0 | P | A=Fire | θ=0deg | rot+=C | inv=B | rot-=D | z=Z(Fire) | ae=AE[F] |
| 3/65 | P2 | P | B=Water | θ=180deg | rot+=D | inv=A | rot-=C | z=Z(Water) | ae=AE[W] |
| 4/65 | P1 | P | C=Air | θ=90deg | rot+=B | inv=D | rot-=A | z=Z(Air) | ae=AE[A] |
| 5/65 | P3 | P | D=Earth | θ=270deg | rot+=A | inv=C | rot-=B | z=Z(Earth) | ae=AE[E] |
| 6/65 | S01 | S | μ=01 | set={A} | card=1 |
| 7/65 | S02 | S | μ=02 | set={B} | card=1 |
| 8/65 | S03 | S | μ=03 | set={A,B} | card=2 |
| 9/65 | S10 | S | μ=10 | set={C} | card=1 |
| 10/65 | S11 | S | μ=11 | set={A,C} | card=2 |
| 11/65 | S12 | S | μ=12 | set={B,C} | card=2 |
| 12/65 | S13 | S | μ=13 | set={A,B,C} | card=3 |
| 13/65 | S20 | S | μ=20 | set={D} | card=1 |
| 14/65 | S21 | S | μ=21 | set={A,D} | card=2 |
| 15/65 | S22 | S | μ=22 | set={B,D} | card=2 |
| 16/65 | S23 | S | μ=23 | set={A,B,D} | card=3 |
| 17/65 | S30 | S | μ=30 | set={C,D} | card=2 |
| 18/65 | S31 | S | μ=31 | set={A,C,D} | card=3 |
| 19/65 | S32 | S | μ=32 | set={B,C,D} | card=3 |
| 20/65 | S33 | S | μ=33 | set={A,B,C,D} | card=4 |
| 21/65 | R01 | R | src={A} | rot+={C} | rot-={D} |
| 22/65 | R02 | R | src={B} | rot+={D} | rot-={C} |
| 23/65 | R03 | R | src={A,B} | rot+={C,D} | rot-={C,D} |
| 24/65 | R10 | R | src={C} | rot+={B} | rot-={A} |
| 25/65 | R11 | R | src={A,C} | rot+={B,C} | rot-={A,D} |
| 26/65 | R12 | R | src={B,C} | rot+={B,D} | rot-={A,C} |
| 27/65 | R13 | R | src={A,B,C} | rot+={B,C,D} | rot-={A,C,D} |
| 28/65 | R20 | R | src={D} | rot+={A} | rot-={B} |
| 29/65 | R21 | R | src={A,D} | rot+={A,C} | rot-={B,D} |
| 30/65 | R22 | R | src={B,D} | rot+={A,D} | rot-={B,C} |
| 31/65 | R23 | R | src={A,B,D} | rot+={A,C,D} | rot-={B,C,D} |
| 32/65 | R30 | R | src={C,D} | rot+={A,B} | rot-={A,B} |
| 33/65 | R31 | R | src={A,C,D} | rot+={A,B,C} | rot-={A,B,D} |
| 34/65 | R32 | R | src={B,C,D} | rot+={A,B,D} | rot-={A,B,C} |
| 35/65 | R33 | R | src={A,B,C,D} | rot+={A,B,C,D} | rot-={A,B,C,D} |
| 36/65 | Q01 | Q | base4 orbit={A} -> {C} -> {B} -> {D} |
| 37/65 | Q02 | Q | base4 orbit={B} -> {D} -> {A} -> {C} |
| 38/65 | Q03 | Q | base4 orbit={A,B} -> {C,D} -> {A,B} -> {C,D} |
| 39/65 | Q10 | Q | base4 orbit={C} -> {B} -> {D} -> {A} |
| 40/65 | Q11 | Q | base4 orbit={A,C} -> {B,C} -> {B,D} -> {A,D} |
| 41/65 | Q12 | Q | base4 orbit={B,C} -> {B,D} -> {A,D} -> {A,C} |
| 42/65 | Q13 | Q | base4 orbit={A,B,C} -> {B,C,D} -> {A,B,D} -> {A,C,D} |
| 43/65 | Q20 | Q | base4 orbit={D} -> {A} -> {C} -> {B} |
| 44/65 | Q21 | Q | base4 orbit={A,D} -> {A,C} -> {B,C} -> {B,D} |
| 45/65 | Q22 | Q | base4 orbit={B,D} -> {A,D} -> {A,C} -> {B,C} |
| 46/65 | Q23 | Q | base4 orbit={A,B,D} -> {A,C,D} -> {A,B,C} -> {B,C,D} |
| 47/65 | Q30 | Q | base4 orbit={C,D} -> {A,B} -> {C,D} -> {A,B} |
| 48/65 | Q31 | Q | base4 orbit={A,C,D} -> {A,B,C} -> {B,C,D} -> {A,B,D} |
| 49/65 | Q32 | Q | base4 orbit={B,C,D} -> {A,B,D} -> {A,C,D} -> {A,B,C} |
| 50/65 | Q33 | Q | base4 orbit={A,B,C,D} -> {A,B,C,D} -> {A,B,C,D} -> {A,B,C,D} |
| 51/65 | T01 | T | hide=C | triad={A,B,D} | anti+={A} -> {B} -> {D} | anti-={A} -> {D} -> {B} |
| 52/65 | T02 | T | hide=A | triad={C,B,D} | anti+={B} -> {D} -> {C} | anti-={B} -> {C} -> {D} |
| 53/65 | T03 | T | hide=C | triad={A,B,D} | anti+={A,B} -> {B,D} -> {A,D} | anti-={A,B} -> {A,D} -> {B,D} |
| 54/65 | T10 | T | hide=A | triad={C,B,D} | anti+={C} -> {B} -> {D} | anti-={C} -> {D} -> {B} |
| 55/65 | T11 | T | hide=B | triad={A,C,D} | anti+={A,C} -> {C,D} -> {A,D} | anti-={A,C} -> {A,D} -> {C,D} |
| 56/65 | T12 | T | hide=A | triad={C,B,D} | anti+={B,C} -> {B,D} -> {C,D} | anti-={B,C} -> {C,D} -> {B,D} |
| 57/65 | T13 | T | hide=D | triad={A,C,B} | anti+={A,B,C} -> {A,B,C} -> {A,B,C} | anti-={A,B,C} -> {A,B,C} -> {A,B,C} |
| 58/65 | T20 | T | hide=A | triad={C,B,D} | anti+={D} -> {C} -> {B} | anti-={D} -> {B} -> {C} |
| 59/65 | T21 | T | hide=C | triad={A,B,D} | anti+={A,D} -> {A,B} -> {B,D} | anti-={A,D} -> {B,D} -> {A,B} |
| 60/65 | T22 | T | hide=A | triad={C,B,D} | anti+={B,D} -> {C,D} -> {B,C} | anti-={B,D} -> {B,C} -> {C,D} |
| 61/65 | T23 | T | hide=C | triad={A,B,D} | anti+={A,B,D} -> {A,B,D} -> {A,B,D} | anti-={A,B,D} -> {A,B,D} -> {A,B,D} |
| 62/65 | T30 | T | hide=A | triad={C,B,D} | anti+={C,D} -> {B,C} -> {B,D} | anti-={C,D} -> {B,D} -> {B,C} |
| 63/65 | T31 | T | hide=B | triad={A,C,D} | anti+={A,C,D} -> {A,C,D} -> {A,C,D} | anti-={A,C,D} -> {A,C,D} -> {A,C,D} |
| 64/65 | T32 | T | hide=A | triad={C,B,D} | anti+={B,C,D} -> {B,C,D} -> {B,C,D} | anti-={B,C,D} -> {B,C,D} -> {B,C,D} |
| 65/65 | T33 | T | hide=A | triad={C,B,D} | anti+={A,B,C,D} -> {A,B,C,D} -> {A,B,C,D} | anti-={A,B,C,D} -> {A,B,C,D} -> {A,B,C,D} |

## Outputs

- shell registry: `myth_math_dense_65_shell_registry.json`
- primary witness registry: `myth_math_dense_65_rqt_witness_registry.json`
- overflow registry: `myth_math_dense_65_rqt_overflow_registry.json`
- manifest: `myth_math_dense_65_manifest.json`
