# VML Operator Registry

## Purpose

This registry turns recurring VML token families into reusable operator families so each folio can be rendered as a formal composition instead of a loose paraphrase.

## Core Parse Rule

Working parse:

\[
\text{token} = \text{operation} + \text{target} + \text{modifier} + \text{result}
\]

Working line law:

\[
\Phi_j^{\mathrm{tot}} = O_{j,m_j} \circ \cdots \circ O_{j,1}
\]

The token does not need to expose every slot explicitly. Missing pieces are allowed, but the operator family assignment must still be stated.

## Canonical Operator Families

| Symbol | Family | Default role |
| --- | --- | --- |
| `\mathsf W` | wet/prime | moisten, activate, prime carrier |
| `\mathsf L` | load substrate | load base, root, starting matter |
| `\mathsf H` | heat/drive | energize, heat, propel transition |
| `\mathsf T` | throat transfer | move through conduit or neck |
| `\mathsf C` | capture | catch, collect, retain a fraction |
| `\mathsf S` | seal/contain | close, hold, clamp, contain |
| `\mathsf V` | verify | check, repeat-check, validate |
| `\mathsf B` | bind conduit | bind, ligature, connect and secure line |
| `\mathsf P` | pressure secure | place or stabilize in pressure vessel |
| `\mathsf F` | fire-seal secure | hard seal under furnace or active heat |
| `\mathsf R` | recirculate/phase-shift | rotate, phase-shift, return through circuit |
| `\mathsf D` | fix | stabilize, lock, complete fixation |
| `\mathsf Q` | checkpoint | mark stage complete, certify passage |
| `\mathsf X` | triple-fix | repeated or emphatic fixation |
| `\mathsf G` | collect/output gate | final output, route to outlet, finish pass |

## Default Token Family Assignments

| Token family | Default operator | Working meaning |
| --- | --- | --- |
| `y`, `sy`, `sair`, `yshey` | `\mathsf W` | active, wet, solvent-bearing, live carrier |
| `ar`, `dar`, `chear` | `\mathsf L` or `\mathsf C` | root, base, captured root essence |
| `o`, `ot`, `sho`, `sho*` | `\mathsf H` | heat, timed drive, active heating |
| `cth`, `cht`, `cthol` | `\mathsf T` | conduit, throat, neck transfer |
| `kor`, `chor`, `keey` | `\mathsf C` or `\mathsf G` | capture, outlet, gathered output |
| `k`, `ckh`, `kos`, `kaiin` | `\mathsf S` | containment, valve, seal, held phase |
| `cthar`, `sckhey`, `ckhey` | `\mathsf V` | check, valve-check, repeated verification |
| `cthy`, `daicthy`, `chod` | `\mathsf B` | bind, conduit-ligature, line fastening |
| `cph`, `psh`, `cpho` | `\mathsf P` | pressure chamber, pressed fluid, aludel state |
| `cfh`, `far`, `cfhoaiin` | `\mathsf F` | fire-seal, furnace lock, high-heat closure |
| `ok`, `okol`, `okchoy` | `\mathsf R` | phase shift, recirculation, contained rotation |
| `d`, `dan`, `dal`, `shody` | `\mathsf D` | fix, finish, stabilize, set state |
| `dain`, `daiin`, `daiiin` | `\mathsf Q` | checkpoint, full-cycle checkpoint, extended verification |
| `dydyd` | `\mathsf X` | triple fixation or intensified lock |
| `chtor`, `chor`, `ro` | `\mathsf G` | outlet gate, routed finish, discharge |

## Suffix And Cycle Rules

| Form | Working rule |
| --- | --- |
| `-aiin` | full cycle completion |
| `-daiin` | full-cycle checkpoint or stabilization |
| `-daiiin` | extended or triple verification |
| doubled token | repeat the operator or raise confidence weight |
| damaged token | preserve the token and mark uncertainty in the equation note |

## Composition Rules

The default line equation should be assembled right-to-left in operational completion order:

\[
\Phi_j^{\mathrm{tot}} = O_{\mathrm{final}} \circ \cdots \circ O_{\mathrm{first}}
\]

Paragraph equation:

\[
\rho_{P_r} = \Phi_{b_r}^{\mathrm{tot}} \circ \cdots \circ \Phi_{a_r}^{\mathrm{tot}}(\rho_{P_{r-1}})
\]

Title equation:

\[
\theta_r = \Pi_r(\rho_{P_r})
\]

Folio equation:

\[
\rho_* = \Phi_N^{\mathrm{tot}} \circ \cdots \circ \Phi_1^{\mathrm{tot}}(\rho_0)
\]

## Confidence Policy

Use these labels when uncertainty exists:

- `direct` - explicitly grounded in local folio evidence
- `derived` - compiled from corpus-level VML rules
- `mixed` - partly direct and partly derived
- `uncertain` - damaged or low-confidence token family assignment

The operator family may still be assigned under uncertainty, but the uncertainty must remain visible.
