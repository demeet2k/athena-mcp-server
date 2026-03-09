from __future__ import annotations

from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "folios" / "F005R_FINAL_DRAFT.md"

LINES = [
    (
        "P1.1",
        "kchody.fchoy.chkoy.oaiin.oar.olsy.chody.dkchy.dy",
        "`kchody` body-volatile-heat-fix-active and page-name bridge token; `fchoy` fire-volatile-heat-active; `chkoy` volatile-contain-heat-active; `oaiin` heat-cycle-complete; `oar` heat-root; `olsy` fluid-dissolve-active; `chody` volatile-heat-fix-active; `dkchy` fix-contain-volatile-active; `dy` fixed.",
        "Name the dangerous volatile body, strike it directly with fire, contain and complete the heat-cycle at the root, dissolve it into fluid, then fix and contain the volatile until it reaches a first terminal fixed state.",
        "open the page with the Dwale bridge token and direct fire catalysis",
        "strong",
    ),
    (
        "P1.2",
        "ochey.okey.qokaiin.sho.ckhoy.cthey.chey.oka*os.otol",
        "`ochey` heat-volatile-essence-active; `okey` heat-contain-essence-active; `qokaiin` extract-contain-cycle-complete; `sho` transition-heat; `ckhoy` valve-heat-active; `cthey` conduit-essence-active; `chey` volatile-essence-active; `oka*os` heat-contain-[damaged]-dissolve; `otol` temporal-heat-fluid.",
        "Heat the volatile essence, keep the essence under containment, complete extraction, shift into a heated transition state, perform the valve check, move active essence through the conduit, preserve the damaged dissolve cluster honestly, and keep the product in timed heated liquid form.",
        "pass from fire ignition into valve-governed extraction and conduit handling",
        "mixed",
    ),
    (
        "P1.3",
        "qoaiin.otan.chy.daiin.oteee*.chocthy.otchy.qotchody",
        "`qoaiin` transmute-cycle-complete; `otan` heat-driven-cycle; `chy` volatile-active; `daiin` checkpoint; `oteee*` temporal-triple-essence-[damaged]; `chocthy` volatile-heat-conduit-bind; `otchy` temporal-volatile-active; `qotchody` transmute-driven-volatile-heat-fix-active.",
        "Complete the first transmutation cycle, drive the volatile under timed heat, mark the checkpoint, enter the damaged but legible triple-essence cluster, bind the volatile heat into the conduit, keep the timed volatile state active, and end in driven volatile heat-fix.",
        "cross the first checkpoint and enter the page's timed triple-essence regime",
        "mixed",
    ),
    (
        "P1.4",
        "otain.cheody.chan.s.cheor.chocthy",
        "`otain` temporal-complete; `cheody` volatile-essence-heat-fix-active with F-witness variant `sheody`; `chan` volatile-cycle; `s` dissolve; `cheor` volatile-essence-outlet; `chocthy` volatile-heat-conduit-bind.",
        "Complete the timed phase, fix volatile essence under heat, run the volatile cycle into dissolution, send volatile essence to the outlet, and seal the first movement in a bound volatile-heat conduit.",
        "close the ignition movement by sealing the first volatile cycle",
        "mixed",
    ),
    (
        "P2.5",
        "teey.shody.qoaiin.cholols.sho.qotcheo.daiin.shodaiin",
        "`teey` driven-double-essence-active; `shody` transition-heat-fix-active; `qoaiin` transmute-cycle-complete; `cholols` volatile-heat-fluid-heat-fluid-dissolve; `sho` transition-heat; `qotcheo` transmute-driven-volatile-essence-heat; `daiin` checkpoint; `shodaiin` transition-heat-fix-cycle-complete.",
        "Restart the process under driven double essence, hold the transition in heat-fix, complete another transmutation cycle, dissolve the volatile repeatedly through heated liquid, reapply transition heat, drive volatile essence under transmuting heat, and close the line with a checkpointed transition-fix completion.",
        "restart the recipe under doubled essence and a second checkpoint",
        "strong",
    ),
    (
        "P2.6",
        "sho.cheor.chey.qoeeey.qoykeeey.qoeor.cthy.shotshy.dy",
        "`sho` transition-heat; `cheor` volatile-essence-outlet; `chey` volatile-essence-active; `qoeeey` transmute-triple-essence-active; `qoykeeey` transmute-moist-contain-triple-essence-active; `qoeor` transmute-essence-outlet; `cthy` conduit-bind-active; `shotshy` transition-heat-driven-transition-active; `dy` fixed.",
        "Enter the page's triple-essence storm: keep transition heat alive at the volatile outlet, intensify volatile essence through triple-essence transmutation, compound it with a moist-contained triple-essence burst, drive essence to the outlet through the conduit, and land the storm in a fixed state.",
        "execute the maximum-intensity triple-essence storm and force it into fixation",
        "strong",
    ),
    (
        "P3.7",
        "qotoeey.keey.cheokchy.shody",
        "`qotoeey` transmute-heat-double-essence-active; `keey` contain-double-essence-active; `cheokchy` volatile-essence-heat-contain-volatile-active with split F-witness `cheo.kchy`; `shody` transition-heat-fix-active.",
        "Close by driving heated double essence through transmutation, contain that doubled essence, hold volatile essence under heated containment, and end in active transition heat-fix.",
        "land the storm as a fixed doubled-essence narcotic terminal",
        "strong",
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
        "The Devil",
        "The Tower",
        "Justice",
        "Death",
        "Strength",
        "Temperance",
        "Judgment",
    ],
    "Juggling": [
        "ignite the toxic torch",
        "valve the flame",
        "catch the checkpoint pulse",
        "seal the first poison loop",
        "restart the doubled-essence throw",
        "survive the triple storm flourish",
        "land the fixed dose",
    ],
    "Story Writing": [
        "danger-name opening",
        "valve-check escalation",
        "first checkpoint storm beat",
        "sealed first closure",
        "double-essence restart",
        "triple-essence climax",
        "fixed narcotic ending",
    ],
    "Hero's Journey": [
        "accept the dangerous name",
        "enter the fire gate",
        "cross the checkpoint threshold",
        "seal the first ordeal",
        "take up doubled essence",
        "survive the triple storm",
        "return with a bounded poison-medicine",
    ],
}

MOVEMENTS = [
    "name the narcotic and ignite it",
    "govern the valve under heat",
    "cross the first checkpoint",
    "seal the first poison loop",
    "restart under doubled essence",
    "survive the triple-essence storm",
    "close in fixed dose form",
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
    out = ["### Paragraph 1 - direct fire ignition, valve governance, and first seal", ""]
    for line_id, eva, literal, operational, *_ in LINES[:4]:
        out += [f"- `{line_id}`", f"  EVA: `{eva}`", f"  Literal chain: {literal}", f"  Operational English: {operational}", ""]
    out += ["### Paragraph 2 - doubled-essence restart and triple-essence storm", ""]
    for line_id, eva, literal, operational, *_ in LINES[4:6]:
        out += [f"- `{line_id}`", f"  EVA: `{eva}`", f"  Literal chain: {literal}", f"  Operational English: {operational}", ""]
    out += ["### Paragraph 3 - fixed doubled-essence terminal", ""]
    for line_id, eva, literal, operational, *_ in LINES[6:]:
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
        f"""# F005R Final Draft - Dense Multilens Translation Atlas

## Final Draft Status

- Status: `authoritative final-draft folio`
- Manuscript role: `fire-catalyzed concentrated poison extraction / henbane page`
- Book: `Book I - Herbal / materia medica`
- Production standard: `framework-governed dense folio with full symbolic matrix`
- Source baseline: `F005R.md`
- Release target: `Plant Crystal`, unified corpus, metro layer, and master manuscript

## Purpose

This file is the authoritative final-draft version of `f005r`.

`f5r` returns Quire A to lethal material. It opens with `kchody`, the page-name bridge token that later enters Dwale, and immediately ignites the volatile with `fchoy`, where fire is not merely a seal but the operation itself. The page then passes through valve governance, a checkpointed triple-essence cluster, a sealed first cycle, a doubled-essence restart, and the violent `qoeeey / qoykeeey` storm before landing in fixed heat-bounded narcotic form. Across the local corpus, this fits henbane-class anesthetic extraction better than Arnica because the bridge behavior is narcotic, not merely toxic.

## Source Stack

- `NEW/SECTION I - BOOK I_ THE HERBAL _ MATERIA MEDICA.md`
- `NEW/working/VML_RECIPE_CROSSREF.md`
- `NEW/working/VML_CONSISTENCY_PROOF.md`
- `NEW/working/THE VML ROSETTA STONE.md`
- `FULL_TRANSLATION/framework/FORMAL_MULTILENS_FRAMEWORK.md`
- `FULL_TRANSLATION/framework/registry/lenses.json`
- `FULL_TRANSLATION/framework/registry/math_kernel_registry.md`

## Reading Contract

- The EVA and VML layers below are the closest direct translation claims.
- Direct evidence and derived renderers remain separate.
- Damaged witnesses and Currier/Friedman splits remain visible where they materially affect the line.
- Botanical identity remains partially disputed between `Henbane/Hyoscyamus` and `Arnica`, but the `kchody` Dwale bridge and narcotic recipe family strongly favor henbane.
- The strongest claim is process identity: short lethal fire-catalyzed narcotic extraction with a triple-essence concentration storm.

## Folio Zero Claim

`f5r` means: name the henbane-class narcotic, ignite the volatile directly with fire, drive it through checkpointed triple-essence circulation, then fix the concentrated poison quickly enough that it becomes usable medicine before it escapes lethal control.

## Folio Identity

| Field | Value |
| --- | --- |
| Folio | `f5r` |
| Quire | `A` |
| Bifolio | `bA4 = f4 + f5` |
| Currier language | `A` |
| Currier hand | `1` |
| Illustration | single truncated plant with shaggy drooping flower, bubble core, and oddly placed tubers |
| Botanical candidate | `Hyoscyamus niger` operationally favored; `Arnica montana` remains the strongest visual rival |
| Risk level | lethal |
| Direct confidence | high on lethal fire-catalyzed poison extraction, moderate-high on exact species |

## Visual Grammar and Codicology

- `short page and truncated plant` = brevity is part of the danger grammar
- `shaggy drooping petals` = diffused toxic volatile rather than calm nutritive concentrate
- `bubble core and dark overpaint` = sealed active principle under pressure
- `center-bifolio placement` = the quire pairs patient proof with lethal extraction on the same leaf

## Full EVA

```text
P1.1: kchody.fchoy.chkoy.oaiin.oar.olsy.chody.dkchy.dy-
P1.2: ochey.okey.qokaiin.sho.ckhoy.cthey.chey.oka*os.otol-
P1.3: qoaiin.otan.chy.daiin.oteee*.chocthy.otchy.qotchody-
P1.4: otain.cheody.chan.s.cheor.chocthy=

P2.5: teey.shody.qoaiin.cholols.sho.qotcheo.daiin.shodaiin-
P2.6: sho.cheor.chey.qoeeey.qoykeeey.qoeor.cthy.shotshy.dy-

P3.7: qotoeey.keey.cheokchy.shody=
```

## Core VML Machinery Active On F5r

- `kchody` = page-opening name tag and confirmed Dwale bridge token
- `fchoy` = direct fire catalysis, where fire is the operation rather than a seal
- `ckhoy` = valve-heat governance inside the lethal regime
- `oteee*` = damaged but readable triple-essence cluster at the first checkpoint
- `qoeeey / qoykeeey` = the page's highest-intensity triple-essence storm
- `daiin + shodaiin` = checkpoint plus late transition-fix completion
- `qotoeey + keey + cheokchy` = terminal doubled-essence containment and narcotic closure
- no salt closure appears; the output remains volatile, fixed, and dangerous

## Direct Line-By-Line Literal Ledger

{ledger}

## Multilens Translation Atlas

{formal}

{mythic}

## Direct Operational Meaning

Paragraph 1 is an ignition chamber. It names the narcotic, applies direct fire to the volatile, then forces the operator through containment, valve control, and the first checkpointed triple-essence cluster before sealing the cycle. Paragraph 2 restarts the work under doubled essence, dissolves it through heated liquid, then detonates the folio's strongest event: `qoeeey` and `qoykeeey`, a concentrated triple-essence storm driven through the conduit into fixation. Paragraph 3 is short because the procedure is short: once the doubled essence is contained and the volatile has been heat-fixed, the page stops. This reads as a lethal narcotic intensifier extracted fast, hot, and under strict bounds for later compound use.

## Mathematical Extraction

Across the formal math lenses, `f5r` is a burst-concentration controller. The folio maximizes volatile and essence gain over a short horizon while keeping the lethal route inside a bounded admissibility window. Fire is injected once, checkpoints are sparse but decisive, triple-essence amplitudes spike sharply, and fixation is sufficient to terminate the run without salt precipitation. The dominant invariant is: short high-energy concentration must end before the system drifts into toxic failure space.

## Mythic Extraction

Across the mythic lenses, `f5r` is the poison ordeal. The operator steals useful medicine from a lethal plant by entering fire, surviving the storm, and returning not with abundance but with a bounded dose. Its myth is disciplined theft from danger, not patience or union.

## All-Lens Zero Point

`f5r` means: when the medicine is lethal, the only lawful path is brief violent concentration under valve control, followed by immediate fixation before the poison escapes its bounds.

## Dense One-Sentence Compression

Name the narcotic, strike it with direct fire, push it through checkpointed triple-essence circulation, and seal the fixed toxic volatile before the lethal spirit escapes.

## Formal Mathematical Overlay For F5r

### Imported Kernel Equations

\\[\\mathcal H := L^2(\\widehat{{\\mathbb C}}, \\mu), \\qquad \\rho \\in \\mathcal T_1(\\mathcal H), \\qquad \\rho \\succeq 0, \\qquad \\mathrm{{Tr}}(\\rho)=1\\]

\\[\\mathcal H_{{\\mathrm{{tot}}}} = \\left(\\bigoplus_r \\mathcal H_r\\right) \\oplus \\left(\\bigoplus_e \\mathcal H_{{\\Lambda_e}}\\right) \\oplus \\mathcal H_{{\\mathrm{{fail}}}}\\]

\\[x_{{n+1}}^{{\\mathrm{{chem}}}} = K_n x_n^{{\\mathrm{{chem}}}}, \\qquad \\mathbf{{1}}^T K_n = \\mathbf{{1}}^T\\]

\\[g = \\mathrm{{Coll}}(X), \\qquad X = \\mathrm{{Expand}}(g) \\oplus r\\]

\\[\\Phi_j^{{(\\lambda)}} = T_\\lambda^{{-1}} \\circ \\Phi_j^{{(\\mathrm{{AQM}})}} \\circ T_\\lambda\\]

### Typed State Machine

\\[\\mathcal R_{{f5r}} = \\{{r_{{\\mathrm{{tag}}}}, r_{{\\mathrm{{ignite}}}}, r_{{\\mathrm{{valve}}}}, r_{{\\mathrm{{checkpoint}}}}, r_{{\\mathrm{{seal}}}}, r_{{\\mathrm{{storm}}}}, r_{{\\mathrm{{terminalfix}}}}\\}}\\]

\\[\\mathcal E_\\Lambda = \\{{e_{{\\mathrm{{fire}}}}, e_{{\\mathrm{{checkpoint}}}}, e_{{\\mathrm{{storm}}}}\\}}\\]

\\[\\delta(e_{{\\mathrm{{fire}}}}): r_{{\\mathrm{{tag}}}} \\to r_{{\\mathrm{{ignite}}}} \\to r_{{\\mathrm{{valve}}}}\\]

\\[\\delta(e_{{\\mathrm{{checkpoint}}}}): r_{{\\mathrm{{valve}}}} \\to r_{{\\mathrm{{checkpoint}}}} \\to r_{{\\mathrm{{seal}}}}\\]

\\[\\delta(e_{{\\mathrm{{storm}}}}): r_{{\\mathrm{{seal}}}} \\to r_{{\\mathrm{{storm}}}} \\to r_{{\\mathrm{{terminalfix}}}}\\]

\\[\\rho_0 \\in \\mathcal H_{{r_{{\\mathrm{{tag}}}}}}, \\qquad x_0^{{\\mathrm{{chem}}}} = \\begin{{bmatrix}} m_{{\\mathrm{{source}}}}^0 \\\\ m_{{\\mathrm{{volatile}}}}^0 \\\\ m_{{\\mathrm{{liquid}}}}^0 \\\\ 0 \\\\ 0 \\end{{bmatrix}}, \\qquad g_0 = \\mathrm{{Coll}}(\\rho_0)\\]

### Canonical AQM Line Operators

{ops}

### Paragraph Compositions

\\[\\Psi_{{P1}} = \\Phi_{{\\mathrm{{P1_4}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P1_3}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P1_2}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P1_1}}}}^{{\\mathrm{{AQM}}}}\\]

\\[\\Psi_{{P2}} = \\Phi_{{\\mathrm{{P2_6}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P2_5}}}}^{{\\mathrm{{AQM}}}}\\]

\\[\\Psi_{{P3}} = \\Phi_{{\\mathrm{{P3_7}}}}^{{\\mathrm{{AQM}}}}\\]

\\[\\rho_{{P1}} = \\Psi_{{P1}}(\\rho_0), \\qquad \\rho_{{P2}} = \\Psi_{{P2}}(\\rho_{{P1}}), \\qquad \\rho_* = \\Psi_{{P3}}(\\rho_{{P2}})\\]

### Invariants And Counts

\\[N_{{\\mathrm{{fire}}}}(f5r) = 1, \\qquad N_{{\\mathrm{{daiin}}}}(f5r) = 2, \\qquad N_{{\\mathrm{{triple}}}}(f5r) = 3\\]

\\[N_{{\\mathrm{{bridge}}}}(f5r) = 1, \\qquad N_{{\\mathrm{{seal}}}}(f5r) = 2, \\qquad N_{{\\mathrm{{salt}}}}(f5r) = 0\\]

\\[\\mathrm{{Tr}}\\!\\left(\\Pi_{{\\mathrm{{terminalfix}}}} \\rho_*\\right) \\gg \\mathrm{{Tr}}\\!\\left(\\Pi_{{\\mathrm{{fail}}}} \\rho_*\\right), \\qquad \\mathbf{{1}}^T x_*^{{\\mathrm{{chem}}}} = \\mathbf{{1}}^T x_0^{{\\mathrm{{chem}}}}\\]

### Cross-Lens Transport

\\[\\Phi_j^{{(\\mathrm{{CUT}})}} = T_{{\\mathrm{{CUT}}}}^{{-1}} \\Phi_j^{{(\\mathrm{{AQM}})}} T_{{\\mathrm{{CUT}}}}, \\qquad \\Phi_j^{{(\\mathrm{{phys}})}} = T_{{\\mathrm{{phys}}}}^{{-1}} \\Phi_j^{{(\\mathrm{{AQM}})}} T_{{\\mathrm{{phys}}}}\\]

\\[\\Phi_j^{{(\\mathrm{{wave}})}} = T_{{\\mathrm{{wave}}}}^{{-1}} \\Phi_j^{{(\\mathrm{{AQM}})}} T_{{\\mathrm{{wave}}}}, \\qquad \\Phi_j^{{(\\mathrm{{wavemath}})}} = T_{{\\mathrm{{wavemath}}}}^{{-1}} \\Phi_j^{{(\\mathrm{{AQM}})}} T_{{\\mathrm{{wavemath}}}}\\]

\\[\\Phi_j^{{(\\lambda)}} = T_\\lambda^{{-1}} \\Phi_j^{{(\\mathrm{{AQM}})}} T_\\lambda, \\qquad \\lambda \\in \\{{\\mathrm{{CUT}}, \\mathrm{{phys}}, \\mathrm{{wave}}, \\mathrm{{wavemath}}\\}}\\]

### Folio Theorem

\\[\\rho_* = (\\Psi_{{P3}} \\circ \\Psi_{{P2}} \\circ \\Psi_{{P1}})(\\rho_0)\\]

\\[\\forall \\rho_0 \\in \\mathcal H_{{r_{{\\mathrm{{tag}}}}}} : \\bigl(N_{{\\mathrm{{fire}}}}=1 \\land N_{{\\mathrm{{triple}}}}=3 \\land N_{{\\mathrm{{salt}}}}=0\\bigr) \\Rightarrow \\rho_* \\in \\mathcal H_{{r_{{\\mathrm{{terminalfix}}}}}}\\]

\\[x_*^{{\\mathrm{{chem}}}} = \\begin{{bmatrix}} m_{{\\mathrm{{source}}}}^* \\\\ m_{{\\mathrm{{volatile}}}}^* \\\\ m_{{\\mathrm{{liquid}}}}^* \\\\ m_{{\\mathrm{{essence}}}}^* \\\\ m_{{\\mathrm{{fixed}}}}^* \\end{{bmatrix}}, \\qquad m_{{\\mathrm{{volatile}}}}^* > 0, \\qquad m_{{\\mathrm{{fixed}}}}^* > 0\\]

The formal theorem of `f5r` is therefore:

1. the page opens by naming the narcotic and igniting it directly with fire
2. it crosses one decisive checkpoint into a damaged but still legible triple-essence regime
3. it restarts under doubled essence and survives the violent `qoeeey / qoykeeey` concentration storm
4. it closes as a fixed volatile narcotic without salt precipitation

## Final Draft Audit

- EVA inventory complete for all 7 visible lines
- direct literal ledger present for each line
- 16 formal math lenses populated with per-line equations
- 4 mythic lenses populated with per-line readings
- key signatures preserved explicitly: `kchody`, `fchoy`, `oteee*`, `qoeeey / qoykeeey`, and the Dwale bridge
- major unresolved issue preserved honestly: `Arnica` remains a visual rival, but operational and bridge evidence strongly favors henbane

## Plant Crystal Contribution

- lethal fire-catalysis station
- narcotic intensifier bridge into Dwale
- triple-essence storm line
- short-page danger marker
- fixed toxic volatile close without salt
"""
    ).rstrip() + "\n"


def main() -> None:
    OUTPUT.write_text(render(), encoding="utf-8")


if __name__ == "__main__":
    main()
