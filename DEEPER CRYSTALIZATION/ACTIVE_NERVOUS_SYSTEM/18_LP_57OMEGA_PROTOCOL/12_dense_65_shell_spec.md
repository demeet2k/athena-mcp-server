# LP-57Omega Dense 65-Shell

- Truth status: `NEAR-derived`
- LP-57 role: `L01-closed substrate enhancement`
- Packet sync role: `L02 Packet Truth Sync input witness`
- Reserved slot: `1/65 = prior seed/header shell`
- Active dense range: `2/65 -> 65/65`
- Sigma path: `AppA -> AppI -> AppM`
- Rotation carriers: `AppF / AppG`
- Base-3 antispin lock: `deterministic packaging choice layered on top of corpus law`
- Operator lens lock: `Flower / F`
- Phase map: `Phi0=R+ / Phi1=R- / Phi2=Q4 / Phi3=T3`
- Route presets: `rtL=AppA>AppI>AppM>AppF>AppN>Ch21<0110>` and `rtZ=AppA>AppI>AppM>AppF>AppG>Ch21<0110>`
- Pole gauge: `A=Fire, C=Air, B=Water, D=Earth`
- Lawful adjacency cycle: `Fire -> Air -> Water -> Earth -> Fire`
- Opposite-pole shortcuts are forbidden except by adjacent bridging or `Z*` tunneling.

## Counts

- Total shell slots: `65`
- Active dense records: `64`
- Partition: `4 P + 15 S + 15 R + 15 Q + 15 T`
- Enriched operator records: `45`
- Phase bindings: `60`
- Concrete pointers: `60`

## Dense Block

```text
1/65) H00 | prior_seed_header_shell | status=reserved | truth=NEAR-derived
2/65) P0 | A=Fire | theta=0deg | rot+=C | inv=B | rot-=D | z=Z(Fire) | ae=AE[F]
3/65) P2 | B=Water | theta=180deg | rot+=D | inv=A | rot-=C | z=Z(Water) | ae=AE[W]
4/65) P1 | C=Air | theta=90deg | rot+=B | inv=D | rot-=A | z=Z(Air) | ae=AE[A]
5/65) P3 | D=Earth | theta=270deg | rot+=A | inv=C | rot-=B | z=Z(Earth) | ae=AE[E]
6/65) S01 | mu=01 | set=['A'] | card=1
7/65) S02 | mu=02 | set=['B'] | card=1
8/65) S03 | mu=03 | set=['A', 'B'] | card=2
9/65) S10 | mu=10 | set=['C'] | card=1
10/65) S11 | mu=11 | set=['A', 'C'] | card=2
11/65) S12 | mu=12 | set=['B', 'C'] | card=2
12/65) S13 | mu=13 | set=['A', 'B', 'C'] | card=3
13/65) S20 | mu=20 | set=['D'] | card=1
14/65) S21 | mu=21 | set=['A', 'D'] | card=2
15/65) S22 | mu=22 | set=['B', 'D'] | card=2
16/65) S23 | mu=23 | set=['A', 'B', 'D'] | card=3
17/65) S30 | mu=30 | set=['C', 'D'] | card=2
18/65) S31 | mu=31 | set=['A', 'C', 'D'] | card=3
19/65) S32 | mu=32 | set=['B', 'C', 'D'] | card=3
20/65) S33 | mu=33 | set=['A', 'B', 'C', 'D'] | card=4
21/65) R01 | set=['A'] | AE+=AE=(F,R+,B01;Core) | AE-=AE=(F,R-,B01;Core) | z=ZA | ck=loc(A) | rt=rtL
22/65) R02 | set=['B'] | AE+=AE=(F,R+,B02;Core) | AE-=AE=(F,R-,B02;Core) | z=ZB | ck=loc(B) | rt=rtL
23/65) R03 | set=['A', 'B'] | AE+=AE=(F,R+,B03;Core) | AE-=AE=(F,R-,B03;Core) | z=ZA+ZB | ck=Z* | rt=rtZ
24/65) R10 | set=['C'] | AE+=AE=(F,R+,B10;Core) | AE-=AE=(F,R-,B10;Core) | z=ZC | ck=loc(C) | rt=rtL
25/65) R11 | set=['A', 'C'] | AE+=AE=(F,R+,B11;Core) | AE-=AE=(F,R-,B11;Core) | z=ZA+ZC | ck=loc(A>C) | rt=rtL
26/65) R12 | set=['B', 'C'] | AE+=AE=(F,R+,B12;Core) | AE-=AE=(F,R-,B12;Core) | z=ZB+ZC | ck=loc(C>B) | rt=rtL
27/65) R13 | set=['A', 'B', 'C'] | AE+=AE=(F,R+,B13;Core) | AE-=AE=(F,R-,B13;Core) | z=ZA+ZB+ZC | ck=loc(A>C>B) | rt=rtL
28/65) R20 | set=['D'] | AE+=AE=(F,R+,B20;Core) | AE-=AE=(F,R-,B20;Core) | z=ZD | ck=loc(D) | rt=rtL
29/65) R21 | set=['A', 'D'] | AE+=AE=(F,R+,B21;Core) | AE-=AE=(F,R-,B21;Core) | z=ZA+ZD | ck=loc(D>A) | rt=rtL
30/65) R22 | set=['B', 'D'] | AE+=AE=(F,R+,B22;Core) | AE-=AE=(F,R-,B22;Core) | z=ZB+ZD | ck=loc(B>D) | rt=rtL
31/65) R23 | set=['A', 'B', 'D'] | AE+=AE=(F,R+,B23;Core) | AE-=AE=(F,R-,B23;Core) | z=ZA+ZB+ZD | ck=loc(B>D>A) | rt=rtL
32/65) R30 | set=['C', 'D'] | AE+=AE=(F,R+,B30;Core) | AE-=AE=(F,R-,B30;Core) | z=ZC+ZD | ck=Z* | rt=rtZ
33/65) R31 | set=['A', 'C', 'D'] | AE+=AE=(F,R+,B31;Core) | AE-=AE=(F,R-,B31;Core) | z=ZA+ZC+ZD | ck=loc(D>A>C) | rt=rtL
34/65) R32 | set=['B', 'C', 'D'] | AE+=AE=(F,R+,B32;Core) | AE-=AE=(F,R-,B32;Core) | z=ZB+ZC+ZD | ck=loc(C>B>D) | rt=rtL
35/65) R33 | set=['A', 'B', 'C', 'D'] | AE+=AE=(F,R+,B33;Core) | AE-=AE=(F,R-,B33;Core) | z=ZA+ZB+ZC+ZD | ck=Z* | rt=rtZ
36/65) Q01 | set=['A'] | AE=AE=(F,Q4,B01;Core) | z=ZA | ck=loc(A) | rt=rtL
37/65) Q02 | set=['B'] | AE=AE=(F,Q4,B02;Core) | z=ZB | ck=loc(B) | rt=rtL
38/65) Q03 | set=['A', 'B'] | AE=AE=(F,Q4,B03;Core) | z=ZA+ZB | ck=Z* | rt=rtZ
39/65) Q10 | set=['C'] | AE=AE=(F,Q4,B10;Core) | z=ZC | ck=loc(C) | rt=rtL
40/65) Q11 | set=['A', 'C'] | AE=AE=(F,Q4,B11;Core) | z=ZA+ZC | ck=loc(A>C) | rt=rtL
41/65) Q12 | set=['B', 'C'] | AE=AE=(F,Q4,B12;Core) | z=ZB+ZC | ck=loc(C>B) | rt=rtL
42/65) Q13 | set=['A', 'B', 'C'] | AE=AE=(F,Q4,B13;Core) | z=ZA+ZB+ZC | ck=loc(A>C>B) | rt=rtL
43/65) Q20 | set=['D'] | AE=AE=(F,Q4,B20;Core) | z=ZD | ck=loc(D) | rt=rtL
44/65) Q21 | set=['A', 'D'] | AE=AE=(F,Q4,B21;Core) | z=ZA+ZD | ck=loc(D>A) | rt=rtL
45/65) Q22 | set=['B', 'D'] | AE=AE=(F,Q4,B22;Core) | z=ZB+ZD | ck=loc(B>D) | rt=rtL
46/65) Q23 | set=['A', 'B', 'D'] | AE=AE=(F,Q4,B23;Core) | z=ZA+ZB+ZD | ck=loc(B>D>A) | rt=rtL
47/65) Q30 | set=['C', 'D'] | AE=AE=(F,Q4,B30;Core) | z=ZC+ZD | ck=Z* | rt=rtZ
48/65) Q31 | set=['A', 'C', 'D'] | AE=AE=(F,Q4,B31;Core) | z=ZA+ZC+ZD | ck=loc(D>A>C) | rt=rtL
49/65) Q32 | set=['B', 'C', 'D'] | AE=AE=(F,Q4,B32;Core) | z=ZB+ZC+ZD | ck=loc(C>B>D) | rt=rtL
50/65) Q33 | set=['A', 'B', 'C', 'D'] | AE=AE=(F,Q4,B33;Core) | z=ZA+ZB+ZC+ZD | ck=Z* | rt=rtZ
51/65) T01 | hide=C | set=['A'] | AE=AE=(F,T3,B01:h=C;Residual) | z=ZA | ck=loc(A) | rt=rtZ
52/65) T02 | hide=A | set=['B'] | AE=AE=(F,T3,B02:h=A;Residual) | z=ZB | ck=loc(B) | rt=rtZ
53/65) T03 | hide=C | set=['A', 'B'] | AE=AE=(F,T3,B03:h=C;Residual) | z=ZA+ZB | ck=Z* | rt=rtZ
54/65) T10 | hide=A | set=['C'] | AE=AE=(F,T3,B10:h=A;Residual) | z=ZC | ck=loc(C) | rt=rtZ
55/65) T11 | hide=B | set=['A', 'C'] | AE=AE=(F,T3,B11:h=B;Residual) | z=ZA+ZC | ck=loc(A>C) | rt=rtZ
56/65) T12 | hide=A | set=['B', 'C'] | AE=AE=(F,T3,B12:h=A;Residual) | z=ZB+ZC | ck=loc(C>B) | rt=rtZ
57/65) T13 | hide=D | set=['A', 'B', 'C'] | AE=AE=(F,T3,B13:h=D;Residual) | z=ZA+ZB+ZC | ck=loc(A>C>B) | rt=rtZ
58/65) T20 | hide=A | set=['D'] | AE=AE=(F,T3,B20:h=A;Residual) | z=ZD | ck=loc(D) | rt=rtZ
59/65) T21 | hide=C | set=['A', 'D'] | AE=AE=(F,T3,B21:h=C;Residual) | z=ZA+ZD | ck=loc(D>A) | rt=rtZ
60/65) T22 | hide=A | set=['B', 'D'] | AE=AE=(F,T3,B22:h=A;Residual) | z=ZB+ZD | ck=loc(B>D) | rt=rtZ
61/65) T23 | hide=C | set=['A', 'B', 'D'] | AE=AE=(F,T3,B23:h=C;Residual) | z=ZA+ZB+ZD | ck=loc(B>D>A) | rt=rtZ
62/65) T30 | hide=A | set=['C', 'D'] | AE=AE=(F,T3,B30:h=A;Residual) | z=ZC+ZD | ck=Z* | rt=rtZ
63/65) T31 | hide=B | set=['A', 'C', 'D'] | AE=AE=(F,T3,B31:h=B;Residual) | z=ZA+ZC+ZD | ck=loc(D>A>C) | rt=rtZ
64/65) T32 | hide=A | set=['B', 'C', 'D'] | AE=AE=(F,T3,B32:h=A;Residual) | z=ZB+ZC+ZD | ck=loc(C>B>D) | rt=rtZ
65/65) T33 | hide=A | set=['A', 'B', 'C', 'D'] | AE=AE=(F,T3,B33:h=A;Residual) | z=ZA+ZB+ZC+ZD | ck=Z* | rt=rtZ
```
