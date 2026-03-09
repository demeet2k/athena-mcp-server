from __future__ import annotations

from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "folios" / "F006R_FINAL_DRAFT.md"

LINES = [
    (
        "P1",
        "poar.y.shol.cholor.cphol.chor.chckh.chopchol.oteeam",
        "`poar` press-root-heat opener with F witness `foar`; `y` moist-active; `shol` transition-fluid; `cholor` volatile-fluid-outlet; `cphol` projected press-fluid; `chor` volatile-outlet; `chckh` volatile-valve; `chopchol` volatile-driven-press-fluid; `oteeam` timed-heat-essence vessel cluster with F witness `otcham`.",
        "Charge the root material into moist transition fluid, move volatile liquid toward the outlet, engage the valve, and press the first fluid through a timed essence-vessel state.",
        "start the pressurized root charge under valve-governed volatile fluid",
        "mixed",
    ),
    (
        "P2",
        "daiin.chckhy.chor.chor.kar.cthy.cthor.chotols",
        "`daiin` checkpoint; `chckhy` volatile-valve-active; `chor.chor` doubled volatile outlet; `kar` contain-root; `cthy` conduit-bind-active; `cthor` conduit-outlet; `chotols` volatile-heat-fluid-dissolve.",
        "Checkpoint the valve, keep the doubled volatile outlet open, clamp the root, and push heated volatile liquid through the conduit into dissolving flow.",
        "prove the clamp-and-conduit regime before ignition",
        "strong",
    ),
    (
        "P3",
        "foeear.kshor.choky.os.cheoeees.ykeor.ytaiin.dam",
        "`foeear` fire-heat-quadruple-essence-root; `kshor` contained transition-outlet; `choky` volatile-heat-contain-active; `os` heat-dissolve; `cheoeees` volatile-essence-triple-intensity dissolve cluster; `ykeor` moist-contain-essence-outlet; `ytaiin` moist-driven cycle-complete; `dam` union.",
        "Apply fire to quadruple-intensified root essence, hold the transition under containment, dissolve the triple-essence stream, complete the moist cycle, and land in the first chemical wedding.",
        "ignite the root essence at quadruple intensity and end in first chemical wedding",
        "strong",
    ),
    (
        "P4",
        "dar.chos.sheor.cho*y.otcham.yaiir.chy",
        "`dar` fix-root; `chos` volatile-dissolve; `sheor` transition-essence-outlet; `cho*y` damaged volatile-heat-active token; `otcham` timed volatile union vessel; `yaiir` moist-driven doubled cycle; `chy` volatile-active.",
        "Fix the root, route dissolved volatile essence through a damaged heated outlet, enter the timed union vessel, and keep the doubled moist cycle volatile and active.",
        "fix the root and keep the first union channel alive through a damaged heated outlet",
        "mixed",
    ),
    (
        "P5",
        "tor.okoiin.shees.ytaly.cthaiin.odam",
        "`tor` driven outlet-root opener with F witness `tar`; `okoiin` heat-contain-cycle-complete; `shees` transition-double-essence-dissolve; `ytaly` moist-driven structural line; `cthaiin` conduit-bind-complete; `odam` heat-activated union.",
        "Restart under contained heat, dissolve doubled essence into the moist structure, complete the conduit bind, and activate the second union by heat.",
        "restart the page under contained heat and heat-activated union",
        "strong",
    ),
    (
        "P6",
        "or.al.daiin.ckham.okam.cthaiin.ydaiin",
        "`or` heat-outlet; `al` structure; `daiin` checkpoint; `ckham` valve-union; `okam` heat-contain-union with F witness `okom`; `cthaiin` conduit-bind-complete; `ydaiin` moist completion.",
        "Hold the heated structure at the outlet, checkpoint the union under valve containment, complete the conduit bind, and certify the moist cycle.",
        "checkpoint the union while the apparatus stays clamped and sealed",
        "strong",
    ),
    (
        "P7",
        "daiin.qodaiin.cho.s.chol.okaiin.s",
        "`P7` survives only in the F witness; `daiin` checkpoint; `qodaiin` circulated completion; `cho` volatile-heat; `s` dissolve; `chol` volatile-fluid; `okaiin` heat-contain-cycle-complete; `s` dissolve.",
        "Add the Friedman-only extra rinse line: checkpoint once more, circulate to completion, dissolve the heated volatile into liquid, and close another contained cycle with one more wash.",
        "extra witness-only dissolution cycle that extends the wash phase",
        "low",
    ),
    (
        "P8",
        "ychol.ckhor.pchar.sheo.ckhaiin",
        "`ychol` moist volatile-fluid; `ckhor` valve-outlet; `pchar` pressed volatile-root; `sheo` transition-essence-heat; `ckhaiin` valve-cycle-complete.",
        "Moisten the volatile fluid, narrow it through the valve outlet, press the root again, pass through heated essence transition, and close another valve cycle.",
        "repeat the press and valve cycle on a moist volatile stream",
        "mixed",
    ),
    (
        "P9",
        "dar.sheol.skaiiodar.otaiin.chory",
        "`dar` fix-root; `sheol` transition-fluid; `skaiiodar` dissolve-contain-quadruple-cycle-fix-root; `otaiin` timed cycle-complete; `chory` volatile-outlet-active.",
        "Fix the root, keep the work in transition fluid, run the unique four-cycle salt dissolution, complete the timed cycle, and reopen the volatile outlet in active form.",
        "execute the folio's unique four-cycle salt dissolution before releasing the outlet",
        "strong",
    ),
    (
        "P10",
        "tchor.ctheod.chy.shor.od.she.od",
        "`tchor` driven volatile-outlet; `ctheod` conduit-essence-heat-fix; `chy` volatile-active; `shor` transition-outlet; `od` heat-fix; `she` transition-heat; `od` heat-fix again.",
        "Drive the volatile through the outlet, bind essence in the conduit under heat-fix, keep the volatile active, and pulse the route through repeated transition-heat fixation.",
        "run the conduit under repeated heat-fix pulses after the quad-cycle wash",
        "mixed",
    ),
    (
        "P11",
        "ychar.olcham.ol.chokaiin",
        "`ychar` moist volatile-root; `olcham` fluid-vessel bridge token; `ol` fluid; `chokaiin` volatile-heat-contain-cycle-complete, with F witness split `olchad.olchokaiin`.",
        "Bring the moist volatile root into the `olcham` vessel state, keep the product fluid, and complete another volatile heat-containment cycle.",
        "enter the olcham bridge state and complete volatile containment",
        "strong",
    ),
    (
        "P12",
        "or.shol.cthom.chor.cthy",
        "`or` heat-outlet; `shol` transition-fluid; `cthom` conduit-heat-vessel; `chor` volatile-outlet; `cthy` conduit-bind-active.",
        "Keep the heated transition inside the conduit vessel, preserve the volatile outlet, and maintain the bind.",
        "stabilize the retort route inside conduit and vessel law",
        "strong",
    ),
    (
        "P13",
        "qocthol.qodaiin.cthy",
        "`qocthol` circulated conduit-fluid; `qodaiin` circulated completion; `cthy` conduit-bind-active.",
        "Circulate the conduit fluid, mark the cycle complete, and lock the bind again.",
        "prove that the conduit loop can circulate and still remain bound",
        "strong",
    ),
    (
        "P14",
        "osho.taiin.y.kaiim",
        "`osho` heated transition opener with F witness `ysho`; `taiin` cycle-complete; `y` moist-active; `kaiim` contained multiplied cycle terminal.",
        "Close the heated transition, certify the cycle, keep the moist state active, and land the page in a contained completed terminal.",
        "close the pressure page in a done-state containment cycle",
        "mixed",
    ),
]

FORMAL_LENSES = [
    ("aqm", "AQM"),
    ("cut", "CUT"),
    ("liminal", "Liminal"),
    ("aetheric", "Aetheric"),
    ("chemistry", "Chemistry"),
    ("physics", "Physics"),
    ("quantum", "Quantum Physics"),
    ("wave_mechanics", "Wave Mechanics"),
    ("wave_math", "Wave Math"),
    ("music", "Music Theory and Music Math"),
    ("light", "Color and Light"),
    ("geometry", "Geometry"),
    ("number", "Number Theory"),
    ("compression", "Compression"),
    ("hacking", "Hacking Theory"),
    ("game", "Game Theory"),
]

MYTHIC_LENSES = {
    "Tarot": [
        "The Emperor",
        "Justice",
        "The Tower",
        "The Lovers",
        "Temperance",
        "Strength",
        "The Hermit",
        "The Chariot",
        "Wheel of Fortune",
        "Judgment",
        "The Hierophant",
        "The Star",
        "The World",
        "The Sun",
    ],
    "Juggling": [
        "load the press",
        "check the double outlet",
        "light the essence torch",
        "carry the first wedding catch",
        "heat the second union",
        "lock the clamp mid-run",
        "add the hidden rinse beat",
        "repeat the root press",
        "spin the four-cycle wash",
        "pulse the retort throat",
        "enter the bridge vessel",
        "hold the conduit line",
        "prove the circulating bind",
        "land the contained finish",
    ],
    "Story Writing": [
        "pressurized opening",
        "apparatus proof beat",
        "fire-root escalation",
        "damaged union channel",
        "second wedding turn",
        "checkpointed bind",
        "hidden witness extension",
        "repeat press sequence",
        "quad-cycle wash climax",
        "heat-fix aftermath",
        "bridge-token reveal",
        "retort stabilization",
        "circulation proof",
        "contained ending",
    ],
    "Hero's Journey": [
        "enter the pressure vessel",
        "accept the first law",
        "take the fire test",
        "cross the damaged gate",
        "bind the second marriage",
        "submit to the clamp",
        "receive the hidden lesson",
        "repeat the labor",
        "endure the fourfold wash",
        "survive the heat pulses",
        "reach the bridge chamber",
        "stabilize the road",
        "prove the circulation",
        "return with the bound plaster",
    ],
}

MOVEMENTS = [
    "charge the root slurry",
    "verify the apparatus",
    "ignite the root essence",
    "carry the first union",
    "activate the second union",
    "checkpoint the clamp",
    "add the hidden rinse",
    "repeat the press cycle",
    "run the quad-cycle wash",
    "pulse the conduit throat",
    "enter the olcham bridge",
    "stabilize the retort route",
    "prove bound circulation",
    "close in contained completion",
]

LEGEND = {
    "aqm": "`rho^-` incoming folio line state; `rho^+` outgoing line state; `Phi_line^(AQM)` source operator chain.",
    "cut": "`X=(kappa,varphi,ell,b)` with containment, phase, liquid flux, and boundary integrity.",
    "liminal": "`p(r)` regime mass, `lambda(e)` liminal-edge load, `f` fail-space mass.",
    "aetheric": "`g` compressed seed, `X` expanded state, `r_line` residual address.",
    "chemistry": "`x=[m_source,m_volatile,m_liquid,m_essence,m_fixed]^T`; `K_line` conserves total material.",
    "physics": "`X^(phys)` tracks containment geometry, phase, pressure, and seal integrity.",
    "quantum": "`rho^(qm)` is the line state on the total carrier with boundary sectors.",
    "wave_mechanics": "`u` is the wave profile; `U_line` is the contraction-compatible update.",
    "wave_math": "`mathcal U_line` is the semigroup block for the line.",
    "music": "`m in R^12` is the pitch-tension vector; `tau` is post-line tension.",
    "light": "`I(lambda)` is spectral intensity; `K_line(lambda,mu)` is the transport kernel.",
    "geometry": "`gamma` is the route through the folio manifold.",
    "number": "`a` counts active resources across channels; `A_line` is an integer update matrix.",
    "compression": "`g` is the replay seed and `rho` the expanded state.",
    "hacking": "`pi` is the route, `e_line` the next admissible edge, `B_line` the seal budget.",
    "game": "`y` is the strategy distribution; `R_line` is risk and `C` the control-cost.",
}


def slug(line_id: str) -> str:
    return line_id.replace(".", "_")


def op_chain(eva: str) -> str:
    tokens = [token for token in eva.split(".") if token]
    ops = [rf"\mathsf O_{{\texttt{{{token}}}}}" for token in reversed(tokens)]
    return " \\circ ".join(ops)


def eq(lens: str, line_id: str, eva: str) -> str:
    s = slug(line_id)
    if lens == "aqm":
        return f"\\[\\rho_{{\\mathrm{{{s}}}}}^+ = \\Phi_{{\\mathrm{{{s}}}}}^{{\\mathrm{{AQM}}}}(\\rho_{{\\mathrm{{{s}}}}}^-), \\qquad \\Phi_{{\\mathrm{{{s}}}}}^{{\\mathrm{{AQM}}}} = {op_chain(eva)}\\]"
    if lens == "cut":
        return f"\\[X_{{\\mathrm{{{s}}}}}^+ = A_{{\\mathrm{{{s}}}}} X_{{\\mathrm{{{s}}}}}^-, \\qquad A_{{\\mathrm{{{s}}}}} = T_{{\\mathrm{{CUT}}}}^{{-1}} \\Phi_{{\\mathrm{{{s}}}}}^{{\\mathrm{{AQM}}}} T_{{\\mathrm{{CUT}}}}\\]"
    if lens == "liminal":
        return f"\\[\\bigl(p_{{\\mathrm{{{s}}}}}^+, \\lambda_{{\\mathrm{{{s}}}}}^+, f_{{\\mathrm{{{s}}}}}^+\\bigr) = L_{{\\mathrm{{{s}}}}}\\bigl(p_{{\\mathrm{{{s}}}}}^-, \\lambda_{{\\mathrm{{{s}}}}}^-, f_{{\\mathrm{{{s}}}}}^-\\bigr), \\qquad f_{{\\mathrm{{{s}}}}}^+ = \\mathrm{{Tr}}(\\Pi_{{\\mathrm{{fail}}}}\\rho_{{\\mathrm{{{s}}}}}^+)\\]"
    if lens == "aetheric":
        return f"\\[X_{{\\mathrm{{{s}}}}}^+ = \\mathrm{{Expand}}(g_{{\\mathrm{{{s}}}}}^-) \\oplus r_{{\\mathrm{{{s}}}}}, \\qquad g_{{\\mathrm{{{s}}}}}^+ = \\mathrm{{Coll}}(X_{{\\mathrm{{{s}}}}}^+)\\]"
    if lens == "chemistry":
        return f"\\[x_{{\\mathrm{{{s}}}}}^{{+,\\mathrm{{chem}}}} = K_{{\\mathrm{{{s}}}}} x_{{\\mathrm{{{s}}}}}^{{-,\\mathrm{{chem}}}}, \\qquad \\mathbf{{1}}^T K_{{\\mathrm{{{s}}}}} = \\mathbf{{1}}^T\\]"
    if lens == "physics":
        return f"\\[X_{{\\mathrm{{{s}}}}}^{{+,\\mathrm{{phys}}}} = P_{{\\mathrm{{{s}}}}} X_{{\\mathrm{{{s}}}}}^{{-,\\mathrm{{phys}}}}, \\qquad P_{{\\mathrm{{{s}}}}} = T_{{\\mathrm{{phys}}}}^{{-1}} \\Phi_{{\\mathrm{{{s}}}}}^{{\\mathrm{{AQM}}}} T_{{\\mathrm{{phys}}}}\\]"
    if lens == "quantum":
        return f"\\[\\rho_{{\\mathrm{{{s}}}}}^{{+,\\mathrm{{qm}}}} = \\Phi_{{\\mathrm{{{s}}}}}^{{\\mathrm{{tot}}}}(\\rho_{{\\mathrm{{{s}}}}}^{{-,\\mathrm{{qm}}}})\\]"
    if lens == "wave_mechanics":
        return f"\\[u_{{\\mathrm{{{s}}}}}^+ = U_{{\\mathrm{{{s}}}}}u_{{\\mathrm{{{s}}}}}^-, \\qquad U_{{\\mathrm{{{s}}}}} = T_{{\\mathrm{{wave}}}}^{{-1}} \\Phi_{{\\mathrm{{{s}}}}}^{{\\mathrm{{AQM}}}} T_{{\\mathrm{{wave}}}}, \\qquad \\|U_{{\\mathrm{{{s}}}}}\\| \\le 1\\]"
    if lens == "wave_math":
        return f"\\[\\mathcal{{U}}_{{\\mathrm{{{s}}}}} = T_{{\\mathrm{{wavemath}}}}^{{-1}} \\Phi_{{\\mathrm{{{s}}}}}^{{\\mathrm{{AQM}}}} T_{{\\mathrm{{wavemath}}}}\\]"
    if lens == "music":
        return f"\\[m_{{\\mathrm{{{s}}}}}^+ = M_{{\\mathrm{{{s}}}}}m_{{\\mathrm{{{s}}}}}^-, \\qquad \\tau_{{\\mathrm{{{s}}}}} = \\|L m_{{\\mathrm{{{s}}}}}^+\\|_2\\]"
    if lens == "light":
        return f"\\[I_{{\\mathrm{{{s}}}}}^+(\\lambda) = \\int K_{{\\mathrm{{{s}}}}}(\\lambda,\\mu) I_{{\\mathrm{{{s}}}}}^-(\\mu)\\, d\\mu\\]"
    if lens == "geometry":
        return f"\\[\\gamma_{{\\mathrm{{{s}}}}}^+ = G_{{\\mathrm{{{s}}}}}(\\gamma_{{\\mathrm{{{s}}}}}^-)\\]"
    if lens == "number":
        return f"\\[a_{{\\mathrm{{{s}}}}}^+ = A_{{\\mathrm{{{s}}}}} a_{{\\mathrm{{{s}}}}}^-, \\qquad A_{{\\mathrm{{{s}}}}} \\in M_k(\\mathbb{{Z}}_{{\\ge 0}})\\]"
    if lens == "compression":
        return f"\\[g_{{\\mathrm{{{s}}}}}^+ = \\mathrm{{Coll}}\\!\\left(\\Phi_{{\\mathrm{{{s}}}}}^{{\\mathrm{{AQM}}}}(\\mathrm{{Expand}}(g_{{\\mathrm{{{s}}}}}^-))\\right)\\]"
    if lens == "hacking":
        return f"\\[\\pi_{{\\mathrm{{{s}}}}}^+ = \\pi_{{\\mathrm{{{s}}}}}^- \\oplus e_{{\\mathrm{{{s}}}}}, \\qquad e_{{\\mathrm{{{s}}}}} \\in E_{{\\mathrm{{safe}}}} \\iff \\mathrm{{seal}}(e_{{\\mathrm{{{s}}}}})=1 \\land \\mathrm{{budget}}(e_{{\\mathrm{{{s}}}}})\\le B_{{\\mathrm{{{s}}}}}\\]"
    return f"\\[y_{{\\mathrm{{{s}}}}}^+ = \\operatorname*{{argmin}}_{{y \\in \\Delta(\\mathcal{{A}})}}\\{{R_{{\\mathrm{{{s}}}}}(y) + \\lambda_{{\\mathrm{{{s}}}}} C(y, y_{{\\mathrm{{{s}}}}}^-)\\}}\\]"


def direct_ledger() -> str:
    out = ["### Paragraph 1 - pressurized loading, apparatus proof, and fire-root ignition", ""]
    for line_id, eva, literal, operational, *_ in LINES[:4]:
        out += [f"- `{line_id}`", f"  EVA: `{eva}`", f"  Literal chain: {literal}", f"  Operational English: {operational}", ""]
    out += ["### Paragraph 2 - second union, hidden rinse, and four-cycle salt dissolution", ""]
    for line_id, eva, literal, operational, *_ in LINES[4:9]:
        out += [f"- `{line_id}`", f"  EVA: `{eva}`", f"  Literal chain: {literal}", f"  Operational English: {operational}", ""]
    out += ["### Paragraph 3 - bridge-vessel completion, conduit circulation, and done-state close", ""]
    for line_id, eva, literal, operational, *_ in LINES[9:]:
        out += [f"- `{line_id}`", f"  EVA: `{eva}`", f"  Literal chain: {literal}", f"  Operational English: {operational}", ""]
    return "\n".join(out).rstrip()


def formal_sections() -> str:
    out: list[str] = []
    for lens, title in FORMAL_LENSES:
        out += [f"### {title}", ""]
        for line_id, eva, _literal, _oper, summary, confidence in LINES:
            out += [f"- `{line_id}`", "  Equation:", "", f"  {eq(lens, line_id, eva)}", "", f"  Variable legend: {LEGEND[lens]}", f"  Reading: {summary}.", f"  Confidence: {confidence}", ""]
    return "\n".join(out).rstrip()


def mythic_sections() -> str:
    out: list[str] = []
    for title, frames in MYTHIC_LENSES.items():
        out += [f"### {title}", ""]
        for idx, (line_id, _eva, _literal, _oper, summary, confidence) in enumerate(LINES):
            out += [f"- `{line_id}`", f"  Frame: {frames[idx]}", f"  Movement: {MOVEMENTS[idx]}", f"  Reading: {summary}.", f"  Confidence: {confidence}", ""]
    return "\n".join(out).rstrip()


def operator_matrix() -> str:
    out: list[str] = []
    for line_id, eva, *_ in LINES:
        out += [f"- `{line_id}`", "", f"\\[\\Phi_{{\\mathrm{{{slug(line_id)}}}}}^{{\\mathrm{{AQM}}}} = {op_chain(eva)}\\]", ""]
    return "\n".join(out).rstrip()


def render() -> str:
    ledger = direct_ledger()
    formal = formal_sections()
    mythic = mythic_sections()
    ops = operator_matrix()
    return dedent(
        f"""# F006R Final Draft - Dense Multilens Translation Atlas

## Final Draft Status

- Status: `authoritative final-draft folio`
- Manuscript role: `pressurized fire-catalyzed binding / wound-plaster herb page`
- Book: `Book I - Herbal / materia medica`
- Production standard: `framework-governed dense folio with full symbolic matrix`
- Source baseline: `F006R.md`

## Purpose

`f6r` is the first post-`f5` page that turns danger back toward constructive structure. Its signature is clamp-plus-valve density, `foeear` fire at intensified root essence, two union events, the unique `skaiiodar` four-cycle salt wash, and the later bridge token `olcham`. The page reads as pressured structural binding rather than narcotic storm work.

## Source Stack

- `NEW/SECTION I - BOOK I_ THE HERBAL _ MATERIA MEDICA.md`
- `NEW/working/VML_RECIPE_CROSSREF.md`
- `NEW/working/VML_CONSISTENCY_PROOF.md`
- `NEW/working/VML_DEEP_RECIPE_CALLBACK_ANALYSIS.md`
- `NEW/working/VML_RIGOROUS_RETRANSCRIPTION_QUIRES_ABCDEFG.md`
- `eva/EVA TRANSCRIPTION ORIGIONAL.txt`

## Reading Contract

- preserve witness splits and the Friedman-only `P7`
- keep species uncertainty explicit
- keep direct evidence separate from derived math and myth renderers

## Folio Zero Claim

`f6r` means: clamp the structural herb under pressure, ignite intensified root essence, force two heat-activated unions, wash the body through a four-cycle salt route, and bridge the resulting medicine into a bound vessel state.

## Folio Identity

| Field | Value |
| --- | --- |
| Folio | `f6r` |
| Quire | `A` |
| Bifolio | `bA3 = f3 + f6` |
| Currier language | `A` |
| Currier hand | `1` |
| Illustration | single veined Herbal A plant |
| Botanical consensus | operationally wound-plaster / structural herb; inherited IDs split between `Acanthus mollis` and `Plantago major` |
| Risk level | moderate |
| Direct confidence | high on pressurized binding and heat-activated union, low-moderate on exact species |

## Visual Grammar and Codicology

- broad veined leaf body = structural or mucilaginous matter
- standard Herbal A layout = danger is process-coded, not monstrous
- bA3 pairing = experimental retort logic continues, but in a constructive register

## Full EVA

```text
P1:  poar.y.shol.cholor.cphol.chor.chckh.chopchol.oteeam-
P2:  daiin.chckhy.chor.chor.kar.cthy.cthor.chotols-
P3:  foeear.kshor.choky.os.cheoeees.ykeor.ytaiin.dam-
P4:  dar.chos.sheor.cho*y.otcham.yaiir.chy-
P5:  tor.okoiin.shees.ytaly.cthaiin.odam-
P6:  or.al.daiin.ckham.okam.cthaiin.ydaiin-
P7:  daiin.qodaiin.cho.s.chol.okaiin.s-   [F witness only]
P8:  ychol.ckhor.pchar.sheo.ckhaiin-
P9:  dar.sheol.skaiiodar.otaiin.chory-
P10: tchor.ctheod.chy.shor.od.she.od-
P11: ychar.olcham.ol.chokaiin-
P12: or.shol.cthom.chor.cthy-
P13: qocthol.qodaiin.cthy-
P14: osho.taiin.y.kaiim=
```

## Core VML Machinery Active On F6r

- `foeear` = fire applied to quadruple-intensified root essence
- `cth- + ckh-` = simultaneous clamp and valve law
- `dam + odam` = two unions, with the second explicitly heat-activated
- `skaiiodar` = singular four-cycle salt dissolution
- `olcham` = bridge-vessel token that later reappears in recipe-space

## Direct Line-By-Line Literal Ledger

{ledger}

## Multilens Translation Atlas

{formal}

{mythic}

## Direct Operational Meaning

The page loads a structural herb into a pressurized apparatus, proves the clamp-and-conduit geometry, applies fire directly to intensified root essence, and forces the material through two weddings before allowing release. The decisive move is `skaiiodar`: the product is washed through a four-cycle salt route, then cooled into `olcham` bridge-vessel containment and a done-state close. This is how the manuscript turns reactive body matter into usable structural medicine.

## Mathematical Extraction

Across the formal math lenses, `f6r` is a delayed-release pressure reactor. Boundary load is intentionally high, the fire operator is singular, union happens twice, and admissible output appears only after a long wash cycle reduces instability enough for bridge containment.

## Mythic Extraction

Across the mythic lenses, `f6r` is the forge of adhesion: matter is clamped, married, washed, and only then allowed to set.

## All-Lens Zero Point

`f6r` means: structural medicine is made by forcing body and route into trust under pressure.

## Dense One-Sentence Compression

Clamp the structural herb, ignite intensified root essence, force the unions, wash the body through the four-cycle salt route, and bridge it into a bound vessel state that can hold.

## Formal Mathematical Overlay For F6r

### Imported Kernel Equations

\\[\\mathcal H := L^2(\\widehat{{\\mathbb C}}, \\mu), \\qquad \\rho \\in \\mathcal T_1(\\mathcal H), \\qquad \\rho \\succeq 0, \\qquad \\mathrm{{Tr}}(\\rho)=1\\]

\\[\\mathcal H_{{\\mathrm{{tot}}}} = \\left(\\bigoplus_r \\mathcal H_r\\right) \\oplus \\left(\\bigoplus_e \\mathcal H_{{\\Lambda_e}}\\right) \\oplus \\mathcal H_{{\\mathrm{{fail}}}}\\]

\\[x_{{n+1}}^{{\\mathrm{{chem}}}} = K_n x_n^{{\\mathrm{{chem}}}}, \\qquad \\mathbf{{1}}^T K_n = \\mathbf{{1}}^T\\]

\\[g = \\mathrm{{Coll}}(X), \\qquad X = \\mathrm{{Expand}}(g) \\oplus r\\]

### Typed State Machine

\\[\\mathcal R_{{f6r}} = \\{{r_{{\\mathrm{{pressload}}}}, r_{{\\mathrm{{clampvalve}}}}, r_{{\\mathrm{{fireroot}}}}, r_{{\\mathrm{{firstunion}}}}, r_{{\\mathrm{{secondunion}}}}, r_{{\\mathrm{{quadwash}}}}, r_{{\\mathrm{{bridgebind}}}}, r_{{\\mathrm{{done}}}}\\}}\\]

\\[\\delta(e_{{\\mathrm{{press}}}}): r_{{\\mathrm{{pressload}}}} \\to r_{{\\mathrm{{clampvalve}}}}, \\qquad \\delta(e_{{\\mathrm{{fire}}}}): r_{{\\mathrm{{clampvalve}}}} \\to r_{{\\mathrm{{fireroot}}}} \\to r_{{\\mathrm{{firstunion}}}}\\]

\\[\\delta(e_{{\\mathrm{{union}}}}): r_{{\\mathrm{{firstunion}}}} \\to r_{{\\mathrm{{secondunion}}}}, \\qquad \\delta(e_{{\\mathrm{{wash}}}}): r_{{\\mathrm{{secondunion}}}} \\to r_{{\\mathrm{{quadwash}}}} \\to r_{{\\mathrm{{bridgebind}}}} \\to r_{{\\mathrm{{done}}}}\\]

\\[\\rho_0 \\in \\mathcal H_{{r_{{\\mathrm{{pressload}}}}}}, \\qquad x_0^{{\\mathrm{{chem}}}} = \\begin{{bmatrix}} m_{{\\mathrm{{source}}}}^0 \\\\ m_{{\\mathrm{{volatile}}}}^0 \\\\ m_{{\\mathrm{{liquid}}}}^0 \\\\ m_{{\\mathrm{{structure}}}}^0 \\\\ 0 \\end{{bmatrix}}\\]

### Canonical AQM Line Operators

{ops}

### Paragraph Compositions

\\[\\Psi_{{A}} = \\Phi_{{\\mathrm{{P4}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P3}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P2}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P1}}}}^{{\\mathrm{{AQM}}}}\\]

\\[\\Psi_{{B}} = \\Phi_{{\\mathrm{{P9}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P8}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P7}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P6}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P5}}}}^{{\\mathrm{{AQM}}}}\\]

\\[\\Psi_{{C}} = \\Phi_{{\\mathrm{{P14}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P13}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P12}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P11}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P10}}}}^{{\\mathrm{{AQM}}}}\\]

\\[\\rho_* = (\\Psi_{{C}} \\circ \\Psi_{{B}} \\circ \\Psi_{{A}})(\\rho_0)\\]

### Invariants And Counts

\\[N_{{\\mathrm{{cth}}}}(f6r) = 6, \\qquad N_{{\\mathrm{{ckh}}}}(f6r) = 4, \\qquad N_{{\\mathrm{{fire}}}}(f6r) = 1\\]

\\[N_{{\\mathrm{{union}}}}(f6r) = 2, \\qquad N_{{\\mathrm{{quadwash}}}}(f6r) = 1, \\qquad N_{{\\mathrm{{bridge}}}}(f6r) = 1\\]

### Cross-Lens Transport

\\[\\Phi_j^{{(\\lambda)}} = T_\\lambda^{{-1}} \\Phi_j^{{(\\mathrm{{AQM}})}} T_\\lambda, \\qquad \\lambda \\in \\{{\\mathrm{{CUT}}, \\mathrm{{phys}}, \\mathrm{{wave}}, \\mathrm{{wavemath}}\\}}\\]

### Folio Theorem

\\[\\forall \\rho_0 \\in \\mathcal H_{{r_{{\\mathrm{{pressload}}}}}} : \\bigl(N_{{\\mathrm{{fire}}}}=1 \\land N_{{\\mathrm{{union}}}}=2 \\land N_{{\\mathrm{{quadwash}}}}=1\\bigr) \\Rightarrow \\rho_* \\in \\mathcal H_{{r_{{\\mathrm{{done}}}}}}\\]

The formal theorem of `f6r` is therefore:

1. the page begins under explicit press-and-valve constraint
2. `foeear` ignites intensified root essence rather than volatile narcotic spirit
3. two union events occur before release is permitted
4. `skaiiodar` performs the decisive four-cycle salt wash
5. the product exits only after the `olcham` bridge-vessel regime is secured

## Final Draft Audit

- EVA inventory complete for all 14 visible lines, with the Friedman-only `P7` preserved explicitly
- direct literal ledger present for each line
- 16 formal math lenses populated with per-line equations
- 4 mythic lenses populated with per-line readings
- key signatures preserved explicitly: `foeear`, `dam`, `odam`, `skaiiodar`, and `olcham`

## Plant Crystal Contribution

- pressurized binding station
- fire-root intensifier line
- heat-activated double-union page
- four-cycle salt dissolution station
- `olcham` bridge-vessel line
"""
    ).rstrip() + "\n"


def main() -> None:
    OUTPUT.write_text(render(), encoding="utf-8")


if __name__ == "__main__":
    main()
