from __future__ import annotations

from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "folios" / "F005V_FINAL_DRAFT.md"

LINES = [
    (
        "P1.1",
        "kocheor.chor.ytchey.pshod.chols.chodaiin.ytoiiin.daiin",
        "`kocheor` contain-heat-volatile-essence-outlet with split witnesses; `chor` volatile-outlet; `ytchey` moist-driven-volatile-essence-active; `pshod` press-transition-heat-fix; `chols` volatile-fluid-dissolve; `chodaiin` volatile-heat-fix-cycle-complete; `ytoiiin` moist-driven-heat-triple-cycle; `daiin` checkpoint.",
        "Open the dual-input page by containing heated volatile essence at the outlet, drive moist volatile essence through a pressed transition-heat-fix, dissolve it into fluid, complete one volatile heat-fix cycle, then run the work through a triple-cycle moisture-heated pass and mark the first checkpoint.",
        "open the dual-source merger under pressure, triple-cycle heating, and first verification",
        "strong",
    ),
    (
        "P1.2",
        "dchol.**.chol.otaiin.dain.cthor.chot*.ychopordg",
        "`dchol` fix-volatile-fluid; `**` damaged witness; `chol` volatile-fluid; `otaiin` temporal-cycle-complete; `dain` fix-complete; `cthor` conduit-outlet; `chot*` damaged volatile-heat-driven token with F/U witness variants; `ychopordg` moist-volatile-heat-press-outlet-rotation-fix-growth.",
        "Fix the volatile fluid, preserve the damage honestly, keep the work in volatile liquid form, complete the timed cycle, fix the state again, push it through the conduit outlet, then drive the moist volatile through a rotating press-to-fix maneuver that still shows witness instability.",
        "stabilize the first merged liquid through damage, conduit control, and rotational press-fix",
        "mixed",
    ),
    (
        "P1.3",
        "qotcho.ytor.daiin.daiin.otchor.daiin.qo*.darchor.dd",
        "`qotcho` transmute-driven-volatile-heat; `ytor` moist-driven-outlet; `daiin.daiin` back-to-back checkpoints; `otchor` temporal-volatile-outlet; `daiin` third checkpoint in one line; `qo*` damaged transmutation token; `darchor` fix-root-volatile-outlet; `dd` double-fix with F/U witness variants `do` and `do{dy?}`.",
        "Drive the volatile under transmuting heat toward the moist outlet, verify it twice in immediate succession, pass it through the timed volatile outlet, verify it again, preserve the damaged transmutation token honestly, root the volatile outlet in fixation, and end in the folio's unique doubled fixation.",
        "trigger the page's verification overload and unprecedented double-fix terminal",
        "mixed",
    ),
    (
        "P1.4",
        "qotor.shees.otol.ykoiin.shol.daiin.cthor.okchykaiin",
        "`qotor` transmute-heat-outlet; `shees` transition-double-essence-dissolve; `otol` temporal-heat-fluid with F witness `otof`; `ykoiin` moist-contain-heat-cycle; `shol` transition-fluid; `daiin` checkpoint; `cthor` conduit-outlet; `okchykaiin` heat-contain-volatile-active-contain-cycle-complete with split witness `okchy.taiin`.",
        "Move the work through a heated outlet transmutation, dissolve double essence into timed heated liquid, run a moist containment cycle, keep the transition fluid alive, mark another checkpoint, then complete the active volatile containment cycle at the conduit outlet.",
        "carry the merged product through timed double-essence dissolution and another containment proof",
        "mixed",
    ),
    (
        "P2.5",
        "shokeeol.chor.cheotol.otchol.daiin.dal.chol.chotaiin",
        "`shokeeol` transition-heat-contain-double-essence-fluid; `chor` volatile-outlet; `cheotol` volatile-essence-heat-driven-fluid; `otchol` temporal-volatile-fluid; `daiin` checkpoint; `dal` fix-structure; `chol` volatile-fluid; `chotaiin` volatile-heat-driven-cycle-complete.",
        "Raise the merged work into contained double-essence fluid, keep the volatile outlet open, drive volatile essence through heated liquid and timed volatile flow, checkpoint the regime again, fix the structure, and end with a completed volatile heat-driven cycle.",
        "consolidate the merged distillate into structured double-essence fluid under another checkpoint",
        "strong",
    ),
    (
        "P2.6",
        "otol.chol.dairodg",
        "`otol` temporal-heat-fluid with F witness `otof`; `chol` volatile-fluid; `dairodg` fix-earth-rotation-heat-fix-growth with witness variants `dairodd` and `dairodm`.",
        "Close the page in timed heated liquid, keep the product as volatile fluid, and end in a rotating earthward heat-fix-growth token whose witnesses preserve the folio's terminal instability rather than a clean stable fix.",
        "seal the page as a rotating but never fully stabilized merged narcotic liquid",
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
        "The Lovers",
        "The Moon",
        "Justice",
        "Temperance",
        "The Devil",
        "Wheel of Fortune",
    ],
    "Juggling": [
        "merge the first two throws",
        "hold the damaged carry",
        "triple-check the dangerous catch",
        "thread the shared channel",
        "lock the doubled pattern",
        "spin the unstable finish",
    ],
    "Story Writing": [
        "dual-input opening",
        "damaged merger beat",
        "verification overload climax",
        "shared-channel continuation",
        "structured union phase",
        "unstable terminal ending",
    ],
    "Hero's Journey": [
        "accept the twin roots",
        "carry the damaged medicine",
        "survive the threefold trial",
        "move through the shared gate",
        "bind the merged essence",
        "return with an unstable boon",
    ],
}

MOVEMENTS = [
    "start the dual-source merge",
    "carry the damaged fix-fluid",
    "survive verification overload",
    "thread the shared conduit",
    "lock the double-essence structure",
    "spin the unstable terminal",
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
    out = ["### Paragraph 1 - dual-input opening, triple-cycle start, and verification overload", ""]
    for line_id, eva, literal, operational, *_ in LINES[:4]:
        out += [f"- `{line_id}`", f"  EVA: `{eva}`", f"  Literal chain: {literal}", f"  Operational English: {operational}", ""]
    out += ["### Paragraph 2 - structured merger and unstable terminal", ""]
    for line_id, eva, literal, operational, *_ in LINES[4:6]:
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
        f"""# F005V Final Draft - Dense Multilens Translation Atlas

## Final Draft Status

- Status: `authoritative final-draft folio`
- Manuscript role: `dual-input combination distillation / mandrake page`
- Book: `Book I - Herbal / materia medica`
- Production standard: `framework-governed dense folio with full symbolic matrix`
- Source baseline: `F005V.md`
- Release target: `Plant Crystal`, unified corpus, metro layer, and master manuscript

## Purpose

This file is the authoritative final-draft version of `f005v`.

`f5v` completes the center bifolio by turning lethal single-source extraction into lethal combination distillation. The page shows two roots converging into one product, floods the text with fixation attempts and completion markers, and then refuses to grant a normal `-dy` stable ending. Instead it closes with `dd` and unstable witness variants. Across the local corpus, this fits mandrake-class dual-input narcotic processing far better than mallow because the entire page is about dangerous merger, repeated verification, and chronic instability.

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
- Botanical identity remains partially disputed between `Mandrake/Mandragora` and `Mallow/Malva`, but the dual-root visual, lethal risk, and `dy=0` instability strongly favor mandrake.
- The strongest claim is process identity: dual-input lethal merger with fixation overload, seven verification markers, and no stable terminal endpoint.

## Folio Zero Claim

`f5v` means: take two dangerous source streams, merge them through maximum caution and repeated fixation, and keep cycling the product because the medicine can be prepared but never fully stabilized.

## Folio Identity

| Field | Value |
| --- | --- |
| Folio | `f5v` |
| Quire | `A` |
| Bifolio | `bA4 = f4 + f5` |
| Currier language | `A` |
| Currier hand | `1` |
| Illustration | dual-root plant or two plants merging into one stem and shared output |
| Botanical candidate | `Mandragora officinarum` operationally favored; `Malva sylvestris` remains the strongest visual rival |
| Risk level | lethal |
| Direct confidence | high on dual-input lethal merger and instability, moderate on exact species |

## Visual Grammar and Codicology

- `dual roots / convergent stems` = two input streams processed toward one output
- `fantastic loop in the stalk` = merger architecture rather than simple linear extraction
- `dark overpaint and dangerous symmetry` = the two-source route requires maximum caution
- `center-bifolio placement` = after proving restart on `f4v`, the manuscript escalates to two-source lethal compounding

## Full EVA

```text
P1.1: kocheor.chor.ytchey.pshod.chols.chodaiin.ytoiiin.daiin-
P1.2: dchol.**.chol.otaiin.dain.cthor.chot*.ychopordg-
P1.3: qotcho.ytor.daiin.daiin.otchor.daiin.qo*.darchor.dd-
P1.4: qotor.shees.otol.ykoiin.shol.daiin.cthor.okchykaiin-

P2.5: shokeeol.chor.cheotol.otchol.daiin.dal.chol.chotaiin-
P2.6: otol.chol.dairodg=
```

## Core VML Machinery Active On F5v

- `dual-root visual` = two-source merger logic
- `d-` at extreme density = fixation overload rather than calm stabilization
- `daiin` appears seven times in six lines = maximum caution processing
- `ytoiiin` = one triple-cycle start token early in the recipe
- `daiin.daiin ... daiin` in P1.3 = verification overload
- `dd` = unprecedented doubled-fix terminal with unstable witness variants
- `dy=0` across the folio = the page tries to fix but never reaches a clean stable endpoint

## Direct Line-By-Line Literal Ledger

{ledger}

## Multilens Translation Atlas

{formal}

{mythic}

## Direct Operational Meaning

Paragraph 1 establishes the merger: one contained volatile outlet, then damage, then extreme oververification, then the unique `dd` doubled-fix marker. The page reads less like a single extraction than a dangerous convergence protocol. Paragraph 2 then carries the merged substance through double-essence fluid, structural fixation, and a rotating terminal token that still does not resolve into `-dy`. This is why `f5v` is so important: the recipe keeps trying to fix the product but never claims full stability. It therefore reads as a mandrake-class medicine that must be used fresh or constantly reworked.

## Mathematical Extraction

Across the formal math lenses, `f5v` is an unstable fixed-point seeker. The system repeatedly applies fixation operators and checkpoint operators to a dual-source liquid, yet the stable-endpoint observable never fires. The dominant invariant is not stable closure but bounded instability: the product remains admissible only while it is continually cycled, verified, and kept in motion.

## Mythic Extraction

Across the mythic lenses, `f5v` is the impossible marriage. Two roots are brought together, bound, and tested again and again, yet the union never becomes fully still. Its myth is dangerous conjunction without rest.

## All-Lens Zero Point

`f5v` means: some medicines can be prepared only as a living unstable union, and the manuscript marks that truth by recording fixation attempts without ever granting stable finality.

## Dense One-Sentence Compression

Merge the two lethal roots, verify every stage, redouble fixation, and keep the resulting narcotic liquid alive because it never truly settles into permanent stability.

## Formal Mathematical Overlay For F5v

### Imported Kernel Equations

\\[\\mathcal H := L^2(\\widehat{{\\mathbb C}}, \\mu), \\qquad \\rho \\in \\mathcal T_1(\\mathcal H), \\qquad \\rho \\succeq 0, \\qquad \\mathrm{{Tr}}(\\rho)=1\\]

\\[\\mathcal H_{{\\mathrm{{tot}}}} = \\left(\\bigoplus_r \\mathcal H_r\\right) \\oplus \\left(\\bigoplus_e \\mathcal H_{{\\Lambda_e}}\\right) \\oplus \\mathcal H_{{\\mathrm{{fail}}}}\\]

\\[x_{{n+1}}^{{\\mathrm{{chem}}}} = K_n x_n^{{\\mathrm{{chem}}}}, \\qquad \\mathbf{{1}}^T K_n = \\mathbf{{1}}^T\\]

\\[g = \\mathrm{{Coll}}(X), \\qquad X = \\mathrm{{Expand}}(g) \\oplus r\\]

\\[\\Phi_j^{{(\\lambda)}} = T_\\lambda^{{-1}} \\circ \\Phi_j^{{(\\mathrm{{AQM}})}} \\circ T_\\lambda\\]

### Typed State Machine

\\[\\mathcal R_{{f5v}} = \\{{r_{{\\mathrm{{dualinput}}}}, r_{{\\mathrm{{pressfix}}}}, r_{{\\mathrm{{tripcycle}}}}, r_{{\\mathrm{{verifyburst}}}}, r_{{\\mathrm{{merge}}}}, r_{{\\mathrm{{doublefix}}}}, r_{{\\mathrm{{unstableterminal}}}}\\}}\\]

\\[\\mathcal E_\\Lambda = \\{{e_{{\\mathrm{{merge}}}}, e_{{\\mathrm{{verify}}}}, e_{{\\mathrm{{fix}}}}\\}}\\]

\\[\\delta(e_{{\\mathrm{{merge}}}}): r_{{\\mathrm{{dualinput}}}} \\to r_{{\\mathrm{{pressfix}}}} \\to r_{{\\mathrm{{tripcycle}}}}\\]

\\[\\delta(e_{{\\mathrm{{verify}}}}): r_{{\\mathrm{{tripcycle}}}} \\to r_{{\\mathrm{{verifyburst}}}} \\to r_{{\\mathrm{{merge}}}}\\]

\\[\\delta(e_{{\\mathrm{{fix}}}}): r_{{\\mathrm{{merge}}}} \\to r_{{\\mathrm{{doublefix}}}} \\to r_{{\\mathrm{{unstableterminal}}}}\\]

\\[\\rho_0 \\in \\mathcal H_{{r_{{\\mathrm{{dualinput}}}}}}, \\qquad x_0^{{\\mathrm{{chem}}}} = \\begin{{bmatrix}} m_{{\\mathrm{{source_1}}}}^0 \\\\ m_{{\\mathrm{{source_2}}}}^0 \\\\ m_{{\\mathrm{{liquid}}}}^0 \\\\ 0 \\\\ 0 \\end{{bmatrix}}, \\qquad g_0 = \\mathrm{{Coll}}(\\rho_0)\\]

### Canonical AQM Line Operators

{ops}

### Paragraph Compositions

\\[\\Psi_{{P1}} = \\Phi_{{\\mathrm{{P1_4}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P1_3}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P1_2}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P1_1}}}}^{{\\mathrm{{AQM}}}}\\]

\\[\\Psi_{{P2}} = \\Phi_{{\\mathrm{{P2_6}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P2_5}}}}^{{\\mathrm{{AQM}}}}\\]

\\[\\rho_{{P1}} = \\Psi_{{P1}}(\\rho_0), \\qquad \\rho_* = \\Psi_{{P2}}(\\rho_{{P1}})\\]

### Invariants And Counts

\\[N_{{\\mathrm{{daiin}}}}(f5v) = 7, \\qquad N_{{\\mathrm{{dd}}}}(f5v) = 1, \\qquad N_{{\\mathrm{{dy}}}}(f5v) = 0\\]

\\[N_{{\\mathrm{{dualinput}}}}(f5v) = 1, \\qquad N_{{\\mathrm{{tripcycle}}}}(f5v) = 1, \\qquad N_{{\\mathrm{{salt}}}}(f5v) = 0\\]

\\[\\mathrm{{Tr}}\\!\\left(\\Pi_{{\\mathrm{{unstableterminal}}}} \\rho_*\\right) \\gg \\mathrm{{Tr}}\\!\\left(\\Pi_{{\\mathrm{{fail}}}} \\rho_*\\right), \\qquad \\mathbf{{1}}^T x_*^{{\\mathrm{{chem}}}} = \\mathbf{{1}}^T x_0^{{\\mathrm{{chem}}}}\\]

### Cross-Lens Transport

\\[\\Phi_j^{{(\\mathrm{{CUT}})}} = T_{{\\mathrm{{CUT}}}}^{{-1}} \\Phi_j^{{(\\mathrm{{AQM}})}} T_{{\\mathrm{{CUT}}}}, \\qquad \\Phi_j^{{(\\mathrm{{phys}})}} = T_{{\\mathrm{{phys}}}}^{{-1}} \\Phi_j^{{(\\mathrm{{AQM}})}} T_{{\\mathrm{{phys}}}}\\]

\\[\\Phi_j^{{(\\mathrm{{wave}})}} = T_{{\\mathrm{{wave}}}}^{{-1}} \\Phi_j^{{(\\mathrm{{AQM}})}} T_{{\\mathrm{{wave}}}}, \\qquad \\Phi_j^{{(\\mathrm{{wavemath}})}} = T_{{\\mathrm{{wavemath}}}}^{{-1}} \\Phi_j^{{(\\mathrm{{AQM}})}} T_{{\\mathrm{{wavemath}}}}\\]

\\[\\Phi_j^{{(\\lambda)}} = T_\\lambda^{{-1}} \\Phi_j^{{(\\mathrm{{AQM}})}} T_\\lambda, \\qquad \\lambda \\in \\{{\\mathrm{{CUT}}, \\mathrm{{phys}}, \\mathrm{{wave}}, \\mathrm{{wavemath}}\\}}\\]

### Folio Theorem

\\[\\rho_* = (\\Psi_{{P2}} \\circ \\Psi_{{P1}})(\\rho_0)\\]

\\[\\forall \\rho_0 \\in \\mathcal H_{{r_{{\\mathrm{{dualinput}}}}}} : \\bigl(N_{{\\mathrm{{dd}}}}=1 \\land N_{{\\mathrm{{dy}}}}=0 \\land N_{{\\mathrm{{daiin}}}}=7\\bigr) \\Rightarrow \\rho_* \\in \\mathcal H_{{r_{{\\mathrm{{unstableterminal}}}}}}\\]

\\[x_*^{{\\mathrm{{chem}}}} = \\begin{{bmatrix}} m_{{\\mathrm{{merged}}}}^* \\\\ m_{{\\mathrm{{volatile}}}}^* \\\\ m_{{\\mathrm{{liquid}}}}^* \\\\ m_{{\\mathrm{{essence}}}}^* \\\\ m_{{\\mathrm{{fixattempt}}}}^* \\end{{bmatrix}}, \\qquad m_{{\\mathrm{{merged}}}}^* > 0, \\qquad m_{{\\mathrm{{fixattempt}}}}^* > 0\\]

The formal theorem of `f5v` is therefore:

1. the page opens by initiating a two-source volatile merger under triple-cycle moisture-heat
2. it overloads verification and reaches the unique `dd` doubled-fix regime
3. it continues to apply fixation and structure through the merged double-essence fluid
4. it closes in a bounded but unstable terminal state, not a clean stable endpoint

## Final Draft Audit

- EVA inventory complete for all 6 visible lines
- direct literal ledger present for each line
- 16 formal math lenses populated with per-line equations
- 4 mythic lenses populated with per-line readings
- key signatures preserved explicitly: dual-root merger, `ytoiiin`, verification overload, `dd`, and `dy=0`
- major unresolved issue preserved honestly: `Malva` remains the inherited visual rival, but process evidence strongly favors mandrake

## Plant Crystal Contribution

- dual-input lethal merger station
- fixation overload line
- `dd` double-fix signature
- unstable terminal product class
- mandrake-class narcotic conjunction
"""
    ).rstrip() + "\n"


def main() -> None:
    OUTPUT.write_text(render(), encoding="utf-8")


if __name__ == "__main__":
    main()
