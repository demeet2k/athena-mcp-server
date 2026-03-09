from __future__ import annotations

from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "folios" / "F002V_FINAL_DRAFT.md"

LINES = [
    ("P1.1", "kooiin.cheopchor.otaiin.odain.chor.dair.shty", "`kooiin` double-heated containment through full cycle; `cheopchor` compressed volatile essence to outlet; `otaiin` timed cycle complete; `odain` heated fixation complete; `chor` volatile outlet; `dair` fixation through one breathing cycle; `shty` active transition.", "Contain the material in a double-heated vessel, press the volatile essence toward the outlet, complete the timed cycle, fix through one breathing turn, and keep the transition active.", "establish the double-heated vessel and project compressed volatile essence toward the outlet", "mixed"),
    ("P1.2", "kchokchy.sho.shol.qotcho.loeees.qoty.chor.daiin", "`kchokchy` phase-shifted body-volatile active; `sho` forced heat; `shol` transition fluid; `qotcho` driven retort heat; `loeees` locked triple-essence dissolve; `qoty` transmute heat active; `chor` volatile outlet; `daiin` checkpoint.", "Phase-shift the body-volatile into active state, force heat into the retort, lock the triple-intensified essence into solution, drive it to the outlet, and mark the checkpoint.", "drive the retort heat and lock triple-intensified volatile essence into solution", "strong"),
    ("P1.3", "otchy.chor.lshy.chol.chody.chodain.chcthy.daiin", "`otchy` timed volatile active; `chor` volatile outlet; `lshy` locked transition active; `chol` volatile fluid; `chody` volatile heat-fix active; `chodain` volatile heat-fix complete; `chcthy` volatile conduit bind active; `daiin` checkpoint.", "Time the volatile operation, lock the transition, maintain the volatile fluid in heated fixation, bind it into the conduit, and checkpoint the completed cycle.", "time and fix the volatile fluid through conduit binding", "mixed"),
    ("P1.4", "sho.cholo.cheor.chodaiin", "`sho` transition heat; `cholo` volatile heated fluid; `cheor` volatile essence outlet; `chodaiin` volatile heat-fix cycle complete.", "Force heat, convert the volatile into heated fluid, carry the volatile essence to the outlet, and seal paragraph one with a fully completed volatile heat-fix cycle.", "close the first paragraph with a completed volatile heat-fix at the outlet", "strong"),
    ("P2.5", "kchor.shy.daiiin.chckhy.sshey.dor.chol.daiin", "`kchor` contained volatile outlet; `shy` active transition; `daiiin` triple-cycle fixation complete; `chckhy` volatile conduit valve active; `sshey` dissolving transition essence active; `dor` fixed outlet; `chol` volatile fluid; `daiin` checkpoint.", "Contain the volatile at the outlet, run the active transition through three complete verification cycles, keep the volatile valve alive, dissolve the essence vigorously, fix at the outlet, and mark the checkpoint.", "run triple-cycle verification through the volatile valve and outlet fix", "strong"),
    ("P2.6", "dor.chol.chor.chol.keol.chy.chty.daiin.otchor.chan", "`dor.chol.chor.chol` alternating washing loop; `keol` quintessence in liquid form; `chy` volatile active; `chty` volatile driven active; `daiin` checkpoint; `otchor` timed volatile outlet; `chan` volatile cycle.", "Wash by alternating fixed outlet and volatile fluid states, reveal the liquid quintessence, keep the volatile active and driven, checkpoint the result, and send it through the timed outlet cycle.", "execute the washing loop and reveal quintessence-fluid", "strong"),
    ("P2.7", "daiin.chotchey.qoteeey.chokeos.chees.chr.cheaiin", "`daiin` checkpoint; `chotchey` heated timed volatile active; `qoteeey` triple-driven essence retort cycle; `chokeos` phase-shifted volatile essence heated and dissolved; `chees` volatile essence dissolve; `chr` volatile outlet; `cheaiin` volatile essence cycle complete.", "Checkpoint the process, retort-cycle the triple-driven essence, heat and dissolve the phase-shifted volatile, carry the essence to the outlet, and complete the volatile-essence cycle.", "triple-retort the driven essence to completed volatile purification", "strong"),
    ("P2.8", "chokoishe.chor.chiol.chol.dolody", "`chokoishe` distributed volatile phase; `chor` volatile outlet; `chiol` spirit in fluid form; `chol` volatile fluid; `dolody` permanently heat-fixed fluid.", "Distribute the volatile phase through the material, hold it at the outlet as spirit-fluid, keep it in volatile liquid form, and permanently fix the fluid under heat.", "distribute the volatile spirit through fluid and permanently fix it", "strong"),
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
    "Tarot": ["The Magician", "The Star", "Justice", "The Sun", "Judgment", "Temperance", "The World", "The Hermit"],
    "Juggling": ["vessel start", "high-energy throw", "locked carry", "first clean land", "triple check", "wash exchange", "retort flourish", "final hold"],
    "Story Writing": ["charged opening", "climactic intensification", "control beat", "sealed act close", "verification passage", "washing montage", "high-intensity set piece", "quiet finish"],
    "Hero's Journey": ["entry to the vessel", "capture the volatile boon", "discipline under flow", "seal the first threshold", "tests of repetition", "road of washes", "apotheosis", "return with purified spirit"],
}

MOVEMENTS = [
    "double-heat and contain",
    "raise the volatile to maximum intensity",
    "lock the active route",
    "seal the first movement",
    "verify through three cycles",
    "wash and reveal quintessence",
    "retort the triple essence",
    "fix the fluid forever",
]

LEGEND = {
    "aqm": "`rho^-` incoming folio line state; `rho^+` outgoing line state; `Phi_line^(AQM)` source operator chain.",
    "cut": "`X=(kappa,varphi,ell,b)` with containment, phase, liquid flux, and boundary integrity.",
    "liminal": "`p(r)` regime mass, `lambda(e)` liminal-edge load, `f` fail-space mass.",
    "aetheric": "`g` compressed seed, `X` expanded state, `r_line` residual address.",
    "chemistry": "`x=[m_source,m_volatile,m_liquid,m_fixed]^T`; `K_line` conserves total material.",
    "physics": "`X^(phys)` tracks containment geometry, phase, flow, and seal integrity.",
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
    out = ["### Paragraph 1 - driven volatile extraction", ""]
    for line_id, eva, literal, operational, *_ in LINES[:4]:
        out += [f"- `{line_id}`", f"  EVA: `{eva}`", f"  Literal chain: {literal}", f"  Operational English: {operational}", ""]
    out += ["### Paragraph 2 - washing loop, triple verification, and final fluid fixation", ""]
    for line_id, eva, literal, operational, *_ in LINES[4:]:
        out += [f"- `{line_id}`", f"  EVA: `{eva}`", f"  Literal chain: {literal}", f"  Operational English: {operational}", ""]
    return "\n".join(out).rstrip()


def formal_sections() -> str:
    out = []
    for lens, title in FORMAL_LENSES:
        out += [f"### {title}", ""]
        for line_id, eva, _literal, _oper, summary, confidence in LINES:
            out += [f"- `{line_id}`", "  Equation:", "", f"  {eq(lens, line_id, eva)}", "", f"  Variable legend: {LEGEND[lens]}", f"  Reading: {summary}.", f"  Confidence: {confidence}", ""]
    return "\n".join(out).rstrip()


def mythic_sections() -> str:
    out = []
    for title, frames in MYTHIC_LENSES.items():
        out += [f"### {title}", ""]
        for idx, (line_id, _eva, _literal, _oper, summary, confidence) in enumerate(LINES):
            out += [f"- `{line_id}`", f"  Frame: {frames[idx]}", f"  Movement: {MOVEMENTS[idx]}", f"  Reading: {summary}.", f"  Confidence: {confidence}", ""]
    return "\n".join(out).rstrip()


def operator_matrix() -> str:
    out = []
    for line_id, eva, *_ in LINES:
        out += [f"- `{line_id}`", "", f"\\[\\Phi_{{\\mathrm{{{slug(line_id)}}}}}^{{\\mathrm{{AQM}}}} = {op_chain(eva)}\\]", ""]
    return "\n".join(out).rstrip()


def render() -> str:
    ledger = direct_ledger()
    formal = formal_sections()
    mythic = mythic_sections()
    ops = operator_matrix()
    return dedent(f"""# F002V Final Draft - Dense Multilens Translation Atlas

## Final Draft Status

- Status: `authoritative final-draft folio`
- Manuscript role: `volatile-mercury bifolio mate to f2r / purified spirit page`
- Book: `Book I - Herbal / materia medica`
- Production standard: `framework-governed dense folio with full symbolic matrix`
- Source baseline: `F002V.md`
- Release target: `Plant Crystal`, unified corpus, metro layer, and master manuscript

## Purpose

This file is the authoritative final-draft version of `f002v`.

Where `f2r` demonstrates safe salt closure, `f2v` demonstrates the complementary mercury or volatile route on the opposite side of the same leaf. The page is saturated with volatile handling, contains zero salt operations, and drives the active principle through triple-intensity washing and retort purification until the fluid itself is permanently fixed.

## Source Stack

- `NEW/SECTION I — BOOK I_ THE HERBAL _ MATERIA MEDICA.md`
- `NEW/working/VML_RIGOROUS_RETRANSCRIPTION_QUIRES_ABCDEFG.md`
- `NEW/working/VML_RECIPE_CROSSREF.md`
- `NEW/working/VML_CONSISTENCY_PROOF.md`
- `NEW/working/THE VML ROSETTA STONE.md`
- `FULL_TRANSLATION/framework/FORMAL_MULTILENS_FRAMEWORK.md`
- `FULL_TRANSLATION/framework/registry/lenses.json`
- `FULL_TRANSLATION/framework/registry/math_kernel_registry.md`

## Reading Contract

- The EVA and VML layers below are the closest direct translation claims.
- Direct evidence and derived renderers remain separate.
- The folio is read as the mercury-side complement to `f2r`, not as an isolated plant page.
- The strongest claim is process identity: zero-salt volatile purification through washing, triple verification, and permanent fluid fixation.

## Folio Zero Claim

`f2v` is the first pure volatile-spirit lesson in the manuscript. Capture the essence in a double-heated vessel, intensify it to triple strength, wash it repeatedly through the outlet loop, retain the quintessence in liquid form, and permanently fix the fluid without ever entering the salt regime.

## Folio Identity

| Field | Value |
| --- | --- |
| Folio | `f2v` |
| Quire | `A` |
| Bifolio | `bA2 = f2 + f7` |
| Currier language | `A` |
| Currier hand | `1` |
| Illustration | one plant |
| Botanical candidate | aquatic plant, water-lily / floating-heart class |
| Risk level | safe |
| Direct confidence | high on volatile-process identity, moderate on exact species |

## Visual Grammar and Codicology

- `horizontal rhizome with scars` = sequential repeated washing or iteration
- `dark vertical stem` = one loaded saturated channel
- `cut branch stub` = pruned side path, only one active route remains
- `single dark leaf` = saturated collection surface
- `one white flower` = purified albedo product
- `hidden core and long stamen` = diffused active essence rather than a mineral core

## Full EVA

```text
P1.1: kooiin.cheopchor.otaiin.odain.chor.dair.shty-
P1.2: kchokchy.sho.shol.qotcho.loeees.qoty.chor.daiin-
P1.3: otchy.chor.lshy.chol.chody.chodain.chcthy.daiin-
P1.4: sho.cholo.cheor.chodaiin=

P2.5: kchor.shy.daiiin.chckhy.sshey.dor.chol.daiin-
P2.6: dor.chol.chor.chol.keol.chy.chty.daiin.otchor.chan-
P2.7: daiin.chotchey.qoteeey.chokeos.chees.chr.cheaiin-
P2.8: chokoishe.chor.chiol.chol.dolody=
```

## Core VML Machinery Active On F2v

- `ch-` = dominant volatile-spirit handling family
- `loeees` = locked triple-essence dissolve
- `daiiin` = triple-cycle verification
- `qoteeey` = triple-driven retort cycle
- `keol` = quintessence in liquid form
- `dor.chol.chor.chol` = explicit washing loop
- `dolody` = permanently heat-fixed fluid terminal
- `saiin = 0` = no salt phase at all on this page

## Direct Line-By-Line Literal Ledger

{ledger}

## Multilens Translation Atlas

{formal}

{mythic}

## Direct Operational Meaning

Paragraph 1 builds the volatile route: double-heated containment, driven retort heat, and the lock point `loeees` where triple-intensified essence is dissolved and captured. Paragraph 2 extends the process through triple verification, an explicit washing loop, liquid quintessence retention in `keol`, another triple retort in `qoteeey`, and final permanent fluid fixation in `dolody`.

## Mathematical Extraction

Across the formal math lenses, `f2v` is a spirit-dominant liquid purification controller. It has zero salt mass, unusually high volatile density, triple-intensity checkpoints, and a terminal condition in which the fluid itself becomes the fixed product instead of precipitating mineral residue.

## Mythic Extraction

Across the mythic lenses, `f2v` is the white-product ascent of the same lesson `f2r` teaches through salt. The page is about washing, clarifying, and carrying spirit until it can return in a purified transmissible form.

## All-Lens Zero Point

`f2v` means: the active spirit is made medicinal by capturing it at high intensity, washing it repeatedly, retaining its quintessence in liquid form, and fixing the fluid without ever letting the process collapse into salt closure.

## Dense One-Sentence Compression

Contain the volatile in a double-heated vessel, lock the triple essence, wash it through the outlet loop, carry quintessence as liquid, and permanently fix the purified fluid.

## Formal Mathematical Overlay For F2v

### Imported Kernel Equations

\\[\\mathcal H := L^2(\\widehat{{\\mathbb C}}, \\mu), \\qquad \\rho \\in \\mathcal T_1(\\mathcal H), \\qquad \\rho \\succeq 0, \\qquad \\mathrm{{Tr}}(\\rho)=1\\]

\\[\\mathcal H_{{\\mathrm{{tot}}}} = \\left(\\bigoplus_r \\mathcal H_r\\right) \\oplus \\left(\\bigoplus_e \\mathcal H_{{\\Lambda_e}}\\right) \\oplus \\mathcal H_{{\\mathrm{{fail}}}}\\]

\\[x_{{n+1}}^{{\\mathrm{{chem}}}} = K_n x_n^{{\\mathrm{{chem}}}}, \\qquad \\mathbf{{1}}^T K_n = \\mathbf{{1}}^T\\]

\\[g = \\mathrm{{Coll}}(X), \\qquad X = \\mathrm{{Expand}}(g) \\oplus r\\]

\\[\\Phi_j^{{(\\lambda)}} = T_\\lambda^{{-1}} \\circ \\Phi_j^{{(\\mathrm{{AQM}})}} \\circ T_\\lambda\\]

### Typed State Machine

\\[\\mathcal R_{{f2v}} = \\{{r_{{\\mathrm{{contain}}}}, r_{{\\mathrm{{intensify}}}}, r_{{\\mathrm{{wash}}}}, r_{{\\mathrm{{triple}}}}, r_{{\\mathrm{{fixfluid}}}}\\}}\\]

\\[\\mathcal E_\\Lambda = \\{{e_{{\\mathrm{{triple}}}}, e_{{\\mathrm{{wash}}}}, e_{{\\mathrm{{zeroSalt}}}}\\}}\\]

\\[\\delta(e_{{\\mathrm{{wash}}}}): r_{{\\mathrm{{contain}}}} \\to r_{{\\mathrm{{intensify}}}} \\to r_{{\\mathrm{{wash}}}} \\to r_{{\\mathrm{{triple}}}} \\to r_{{\\mathrm{{fixfluid}}}}\\]

\\[\\rho_0 \\in \\mathcal H_{{r_{{\\mathrm{{contain}}}}}}, \\qquad x_0^{{\\mathrm{{chem}}}} = \\begin{{bmatrix}} m_{{\\mathrm{{source}}}}^0 \\\\ m_{{\\mathrm{{volatile}}}}^0 \\\\ m_{{\\mathrm{{liquid}}}}^0 \\\\ 0 \\end{{bmatrix}}, \\qquad g_0 = \\mathrm{{Coll}}(\\rho_0)\\]

### Canonical AQM Line Operators

{ops}

### Paragraph Compositions

\\[\\Phi_{{P1}}^{{\\mathrm{{tot}}}} = \\Phi_{{\\mathrm{{P1_4}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P1_3}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P1_2}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P1_1}}}}^{{\\mathrm{{AQM}}}}\\]

\\[\\Phi_{{P2}}^{{\\mathrm{{tot}}}} = \\Phi_{{\\mathrm{{P2_8}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P2_7}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P2_6}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P2_5}}}}^{{\\mathrm{{AQM}}}}\\]

\\[\\rho_{{P1}} = \\Phi_{{P1}}^{{\\mathrm{{tot}}}}(\\rho_0), \\qquad \\rho_* = \\Phi_{{P2}}^{{\\mathrm{{tot}}}}(\\rho_{{P1}})\\]

### Formal Safety And Yield Invariants

\\[\\mathrm{{Tr}}(\\rho_n)=1\\]

\\[f_n = \\mathrm{{Tr}}(\\Pi_{{\\mathrm{{fail}}}}\\rho_n) \\le \\varepsilon_{{\\mathrm{{safe}}}}\\]

\\[S_{{f2v}} = 0\\]

\\[\\chi_{{f2v}} := \\frac{{28}}{{51}} \\approx 0.549\\]

\\[T_{{f2v}}^{{\\mathrm{{triple}}}} = 3\\]

\\[m_{{\\mathrm{{volatile}}}}^* > 0, \\qquad m_{{\\mathrm{{liquid}}}}^* > 0, \\qquad m_{{\\mathrm{{fixed}}}}^* > 0\\]

### Conjugacy Law

\\[\\Phi_j^{{(\\lambda)}} = T_\\lambda^{{-1}} \\circ \\Phi_j^{{(\\mathrm{{AQM}})}} \\circ T_\\lambda\\]

\\[K_j = T_{{\\mathrm{{chem}}}}^{{-1}} \\Phi_j^{{(\\mathrm{{AQM}})}} T_{{\\mathrm{{chem}}}}, \\qquad U_j = T_{{\\mathrm{{wave}}}}^{{-1}} \\Phi_j^{{(\\mathrm{{AQM}})}} T_{{\\mathrm{{wave}}}}, \\qquad A_j = T_{{\\mathrm{{num}}}}^{{-1}} \\Phi_j^{{(\\mathrm{{AQM}})}} T_{{\\mathrm{{num}}}}\\]

### Concrete Transport Targets

\\[x_n^{{\\mathrm{{chem}}}} = \\begin{{bmatrix}} m_{{\\mathrm{{source}}}}(n) \\\\ m_{{\\mathrm{{volatile}}}}(n) \\\\ m_{{\\mathrm{{liquid}}}}(n) \\\\ m_{{\\mathrm{{fixed}}}}(n) \\end{{bmatrix}}, \\qquad X_n^{{\\mathrm{{phys}}}}=(\\kappa_n,\\varphi_n,\\ell_n,b_n), \\qquad m_n \\in \\mathbb{{R}}^{{12}}, \\qquad g_n=\\mathrm{{Coll}}(\\rho_n)\\]

### Formal Folio Theorem

\\[\\rho_* = \\left(\\Phi_{{\\mathrm{{P2_8}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P2_7}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P2_6}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P2_5}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P1_4}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P1_3}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P1_2}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P1_1}}}}^{{\\mathrm{{AQM}}}}\\right)(\\rho_0)\\]

\\[\\Pi_{{r_{{\\mathrm{{fixfluid}}}}}}\\rho_* = \\rho_*, \\qquad \\lambda_*(e_{{\\mathrm{{zeroSalt}}}})=0, \\qquad \\lambda_*(e_{{\\mathrm{{triple}}}})=0\\]

\\[x_*^{{\\mathrm{{chem}}}} = \\begin{{bmatrix}} m_{{\\mathrm{{source}}}}^* \\\\ m_{{\\mathrm{{volatile}}}}^* \\\\ m_{{\\mathrm{{liquid}}}}^* \\\\ m_{{\\mathrm{{fixed}}}}^* \\end{{bmatrix}}, \\qquad m_{{\\mathrm{{volatile}}}}^* > 0, \\qquad m_{{\\mathrm{{liquid}}}}^* > 0, \\qquad g_* = \\mathrm{{Coll}}(\\rho_*)\\]

The theorem says `f2v` computes a zero-salt, spirit-dominant purification route in which triple-intensity retort cycling and washing converge to one permanently fixed fluid product.

## Final Draft Audit

- Every visible line has EVA, direct ledger, formal-math render, and mythic render.
- The page-specific signatures `loeees`, `daiiin`, `dor.chol.chor.chol`, `keol`, `qoteeey`, and `dolody` remain explicit.
- The zero-salt condition is preserved rather than normalized away.
- Confidence is highest for the page-level claim `volatile purification page with washing loop and permanent fluid fixation`.
- Confidence is lower for exact species identity and for whether the aquatic plant should be named `Nymphaea` or `Nymphoides`.

## Plant Crystal Contribution

- `Mercury Counterpart Station` - the volatile complement to `f2r`'s salt route
- `Washing Loop` - explicit `dor.chol.chor.chol` iteration
- `Triple-Intensity Purification` - `loeees`, `daiiin`, and `qoteeey`
- `White Product Closure` - one purified albedo-style output
- `Salt-Mercury Bifolio Pair` - `f2r + f2v` now encode the two foundational extraction modes on one leaf
""").strip() + "\n"


def main() -> None:
    OUTPUT.write_text(render(), encoding="utf-8")


if __name__ == "__main__":
    main()
