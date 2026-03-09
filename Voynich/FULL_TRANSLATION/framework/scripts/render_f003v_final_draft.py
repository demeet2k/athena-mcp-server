from __future__ import annotations

from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "folios" / "F003V_FINAL_DRAFT.md"

LINES = [
    (
        "P1.1",
        "koaiin.cphor.qotoy.sha.ckhol.ykoaiin.s.oly",
        "`koaiin` contain-heat-cycle-complete; `cphor` alembic-outlet; `qotoy` transmute-heat-active; `sha` transition-earth; `ckhol` valve-fluid; `ykoaiin` moist-contain-heat-cycle-complete; `s` dissolve; `oly` fluid-active.",
        "Establish sealed containment, open the alembic outlet, drive active heat into the work, keep the valve-fluid path under control, moisten the vessel state, and dissolve the matter into active liquid.",
        "build the containment apparatus and gate the first volatile liquid through the valve line",
        "strong",
    ),
    (
        "P1.2",
        "daiidy.qotchol.okeeor.okor.olytol.dol.dar",
        "`daiidy` fix-cycle-fix-active; `qotchol` transmute-driven-volatile-fluid; `okeeor` heat-contain-double-essence-outlet; `okor` heat-contain-outlet; `olytol` fluid-moist-driven-fluid; `dol` fix-fluid; `dar` fix-root.",
        "Hold fixation active, drive the volatile fluid through retort motion, bring double essence to the outlet under heated containment, keep the fluid route moist and driven, then fix both liquid and root.",
        "drive the volatile toward the outlet while fixing both fluid and root channels",
        "mixed",
    ),
    (
        "P1.3",
        "okom.chol.shol.seees.chom.cheeykam.oai*",
        "`okom` heat-contain-vessel; `chol` volatile-fluid; `shol` transition-fluid; `seees` dissolve-triple-essence; `chom` volatile-vessel; `cheeykam` volatile-double-essence-moist-contain-vessel; `oai*` damaged heated-cycle cluster.",
        "Heat and contain the vessel, keep volatile and transition fluids in play, dissolve the work into triple essence, hold it inside the volatile vessel, and concentrate double essence in a moistened containment state while leaving the damaged tail explicit.",
        "dissolve the contained liquid into triple essence inside the volatile vessel",
        "strong",
    ),
    (
        "P1.4",
        "qiiirdar.chs.eey.kcheol.okal.do.r.cheareen",
        "`qiiirdar` triple-i retort-fix-root; `chs` volatile-dissolve; `eey` double-essence-active; `kcheol` body-volatile-essence-fluid; `okal` heat-contain-structure; `do` fix-heat; `r` outlet; `cheareen` volatile-essence-root-essence-cycle.",
        "Enter the first rare extended retort cycle, dissolve the volatile, activate double essence, keep the body-volatile essence in liquid form, contain it structurally under heat-fix, then send it toward the outlet through a root-essence cycle.",
        "run the first extended triple retort under strong structural control",
        "mixed",
    ),
    (
        "P1.5",
        "ychear.otchal.chor.char.ckha",
        "`ychear` moist-volatile-essence-root; `otchal` timed-volatile-structure; `chor` volatile-outlet; `char` volatile-root; `ckha` valve-earth.",
        "Moisten the volatile root-essence, time the volatile structure, hold the outlet and root together, and secure the earthy valve boundary.",
        "stabilize the outlet-root boundary at the valve-earth threshold",
        "mixed",
    ),
    (
        "P1.6",
        "os.cheor.kar.chodaly.chom",
        "`os` heat-dissolve; `cheor` volatile-essence-outlet; `kar` contain-root; `chodaly` volatile-heat-fix-structure-active; `chom` volatile-vessel.",
        "Dissolve under heat, send volatile essence toward the outlet, contain the root, convert the work into active volatile heat-fixed structure, and seal the paragraph inside the volatile vessel.",
        "seal the first paragraph in active volatile structure inside the vessel",
        "strong",
    ),
    (
        "P2.7",
        "tchor.otcham.chor.cpham.ch",
        "`tchor` driven-volatile-outlet; `otcham` timed-volatile-vessel; `chor` volatile-outlet; `cpham` alembic-vessel; `ch` volatile.",
        "Restart the process with a driven volatile outlet, time the volatile vessel, hold the outlet again, and pass the work through the alembic vessel as pure volatile matter.",
        "restart the second branch through driven outlet and alembic vessel",
        "strong",
    ),
    (
        "P2.8",
        "ykchy.kchom.chor.chckhol.oka",
        "`ykchy` moist-contain-volatile-active; `kchom` body-volatile-vessel; `chor` volatile-outlet; `chckhol` volatile-valve-fluid; `oka` heat-contain-earth.",
        "Keep the volatile active in moist containment, hold it in the body-volatile vessel, guide it to the outlet, maintain the volatile valve-fluid path, and keep the earthy containment warm and bounded.",
        "hold the volatile route under moist containment and valve control",
        "mixed",
    ),
    (
        "P2.9",
        "ytcheear.okeol.cthodoaly.chor.cthy",
        "`ytcheear` moist-driven-volatile-double-essence-root; `okeol` heat-contain-essence-fluid; `cthodoaly` conduit-heat-fix-heat-structure-active; `chor` volatile-outlet; `cthy` conduit-bind-active.",
        "Drive moist double essence through the rooted volatile lane, keep the essence-fluid heated in containment, run it through an actively heat-fixed conduit structure, and bind the outlet back into the conduit.",
        "carry double essence through conduit-bound structural fixation",
        "mixed",
    ),
    (
        "P2.10",
        "ochas.daiin.qokshol.daiim.chol.okary",
        "`ochas` heat-volatile-earth-dissolve; `daiin` fix-cycle-complete; `qokshol` extract-contain-transition-fluid; `daiim` fix-cycle-vessel bridge token; `chol` volatile-fluid; `okary` heat-contain-root-active.",
        "Dissolve heated volatile matter into the earthward phase, mark the checkpoint complete, extract the contained transition fluid, introduce the `daiim` vessel bridge, keep the work in volatile liquid form, and reactivate the heated root-containment.",
        "checkpoint the process and inject the corrective vessel-bridge into the volatile stream",
        "strong",
    ),
    (
        "P2.11",
        "sho.shockho.ckhy.tchor.chodaiin.chom",
        "`sho` transition-heat; `shockho` transition-heat-volatile-contain-heat; `ckhy` valve-active; `tchor` driven-volatile-outlet; `chodaiin` volatile-heat-fix-cycle-complete; `chom` volatile-vessel.",
        "Run heated transition through a volatile containment loop, keep the valve active, drive the volatile to the outlet, complete the volatile heat-fix cycle, and hold the result in the vessel.",
        "perform the active valve check and complete the heated volatile cycle",
        "strong",
    ),
    (
        "P2.12",
        "osh.chodair.ytchy.tchor.kcham.s",
        "`osh` heat-transition; `chodair` volatile-heat-fix-earth-rotation; `ytchy` moist-driven-volatile-active; `tchor` driven-volatile-outlet; `kcham` body-volatile-vessel; `s` dissolve.",
        "Rotate the volatile heat-fix through one earthward turn, keep the driven volatile moist and active, send it to the outlet, return it to the body-volatile vessel, and dissolve once more.",
        "rotate the heated volatile outward and redissolve it in the body vessel",
        "mixed",
    ),
    (
        "P2.13",
        "shar.shkaiin.qiiirkchy.yty.cthal.chky",
        "`shar` transition-root; `shkaiin` transition-contain-cycle-complete; `qiiirkchy` triple-i retort-contain-volatile-active; `yty` moist-driven-active; `cthal` conduit-structure; `chky` volatile-contain-active.",
        "Move to the rooted transition state, complete the contained transition cycle, enter the second rare extended retort, keep the motion moist and driven, build the conduit structure, and maintain active volatile containment.",
        "run the second extended triple retort and lock it into conduit structure",
        "strong",
    ),
    (
        "P2.14",
        "dain.sheam.ykeam",
        "`dain` fix-complete; `sheam` transition-essence-union; `ykeam` moist-contain-essence-union.",
        "Close the page by marking fixation complete and then landing in two successive union states: transition-essence union and moist-contained essence union.",
        "finish in double union after complete fixation",
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
        "The Magician",
        "Justice",
        "Temperance",
        "The Hermit",
        "Strength",
        "The Emperor",
        "The Chariot",
        "The High Priestess",
        "The Star",
        "The Lovers",
        "Judgment",
        "Wheel of Fortune",
        "Death",
        "The World",
    ],
    "Juggling": [
        "build the rig",
        "first guided outlet throw",
        "triple-essence carry",
        "long controlled orbit",
        "earth-valve catch",
        "first seal",
        "restart the cascade",
        "wet containment hold",
        "double-essence pass",
        "insert the corrective prop",
        "valve check flourish",
        "turn-and-return throw",
        "rare orbit reprise",
        "double landing",
    ],
    "Story Writing": [
        "apparatus opening",
        "driven outlet scene",
        "triple-essence chamber",
        "rare retort escalation",
        "boundary test",
        "first act seal",
        "second-act restart",
        "containment tension beat",
        "double-essence corridor",
        "corrective reveal",
        "discipline checkpoint",
        "return turn",
        "second rare ordeal",
        "healing close",
    ],
    "Hero's Journey": [
        "receive the vessel",
        "cross the heated threshold",
        "enter the deep chamber",
        "survive the first rare ordeal",
        "guard the boundary",
        "seal the first gain",
        "re-enter the road",
        "carry the volatile boon",
        "walk the narrow conduit",
        "receive the corrective ally",
        "pass the discipline trial",
        "turn back with the medicine",
        "survive the second ordeal",
        "return in union",
    ],
}

MOVEMENTS = [
    "build the sealed alembic path",
    "drive the outlet under fixation",
    "dissolve into triple essence",
    "orbit through the rare retort",
    "secure the valve boundary",
    "seal the first chamber",
    "restart the volatile lane",
    "hold the wet containment",
    "bind double essence to conduit",
    "introduce the corrective bridge",
    "complete the valve check",
    "rotate and redissolve",
    "repeat the rare retort safely",
    "land in double union",
]

LEGEND = {
    "aqm": "`rho^-` incoming folio line state; `rho^+` outgoing line state; `Phi_line^(AQM)` source operator chain.",
    "cut": "`X=(kappa,varphi,ell,b)` with containment, phase, liquid flux, and boundary integrity.",
    "liminal": "`p(r)` regime mass, `lambda(e)` liminal-edge load, `f` fail-space mass.",
    "aetheric": "`g` compressed seed, `X` expanded state, `r_line` residual address.",
    "chemistry": "`x=[m_source,m_volatile,m_essence,m_corrective,m_union]^T`; `K_line` conserves total material.",
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
    out = ["### Paragraph 1 - containment apparatus, triple essence dissolve, and first rare retort", ""]
    for line_id, eva, literal, operational, *_ in LINES[:6]:
        out += [f"- `{line_id}`", f"  EVA: `{eva}`", f"  Literal chain: {literal}", f"  Operational English: {operational}", ""]
    out += ["### Paragraph 2 - restart, corrective bridge, second rare retort, and double union close", ""]
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
        f"""# F003V Final Draft - Dense Multilens Translation Atlas

## Final Draft Status

- Status: `authoritative final-draft folio`
- Manuscript role: `controlled volatile corrective page / chamomile-leaning bridge folio`
- Book: `Book I - Herbal / materia medica`
- Production standard: `framework-governed dense folio with full symbolic matrix`
- Source baseline: `F003V.md`
- Release target: `Plant Crystal`, unified corpus, metro layer, and master manuscript

## Purpose

This file is the authoritative final-draft version of `f003v`.

Where `f3r` detonates the first major retort-union storm, `f3v` shows how that danger is disciplined. The page builds a tightly gated volatile apparatus, dissolves the work into triple essence, enters two rare extended retort cycles under valve control, introduces the `daiim` bridge token that points forward into Dwale, and closes in double union without ever entering a salt regime. Across the local corpus, this makes `f3v` read less like a poison page and more like a controlled corrective distillate, with chamomile operationally favored over hellebore or monkshood.

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
- Visual identification and operational identification remain partially split on this folio.
- The strongest claim is process identity: controlled volatile handling with rare retort excursions, valve caution, and a corrective bridge into later pharmaceutical work.

## Folio Zero Claim

`f3v` means: construct a bounded volatile pathway, dissolve the matter into triple essence, survive two rare extended retort cycles under valve control, inject the corrective vessel-bridge at checkpoint, and land the page in double union as a liquid balancing medicine rather than a salt-fixed poison residue.

## Folio Identity

| Field | Value |
| --- | --- |
| Folio | `f3v` |
| Quire | `A` |
| Bifolio | `bA3 = f3 + f6` |
| Currier language | `A` |
| Currier hand | `1` |
| Illustration | one plant with two unequal flowers and telescoping root |
| Botanical candidate | `Matricaria chamomilla` operationally favored; `Helleborus foetidus` remains the strongest visual rival |
| Risk level | moderate in operation; toxic only if the visual hellebore identification dominates |
| Direct confidence | high on controlled volatile process, moderate on corrective role, moderate on exact species |

## Visual Grammar and Codicology

- `two unequal flowers` = two outputs of unequal scale, plausibly oil plus hydrosol
- `dotted core` = granular flower-head material rather than a heavy mineral seed
- `telescoping root` = nested containment or inside-out process architecture
- `tight page rhythm with two rare qiiir tokens` = caution plus technical escalation rather than relaxed herb handling
- `paired position after f3r` = the manuscript answers the first retort storm with a controlled balancing page

## Full EVA

```text
P1.1: koaiin.cphor.qotoy.sha.ckhol.ykoaiin.s.oly-
P1.2: daiidy.qotchol.okeeor.okor.olytol.dol.dar-
P1.3: okom.chol.shol.seees.chom.cheeykam.oai*-
P1.4: qiiirdar.chs.eey.kcheol.okal.do.r.cheareen-
P1.5: ychear.otchal.chor.char.ckha-
P1.6: os.cheor.kar.chodaly.chom=

P2.7: tchor.otcham.chor.cpham.ch-
P2.8: ykchy.kchom.chor.chckhol.oka-
P2.9: ytcheear.okeol.cthodoaly.chor.cthy-
P2.10: ochas.daiin.qokshol.daiim.chol.okary-
P2.11: sho.shockho.ckhy.tchor.chodaiin.chom-
P2.12: osh.chodair.ytchy.tchor.kcham.s-
P2.13: shar.shkaiin.qiiirkchy.yty.cthal.chky-
P2.14: dain.sheam.ykeam=
```

## Core VML Machinery Active On F3v

- `koaiin` = containment cycle completed before the page risks volatile escalation
- `cphor` = explicit alembic outlet, so this is apparatus-forward from the first line
- `ckhol / ckha / ckhy / chckhol` = elevated valve-control family
- `seees` = dissolve-triple-essence, the page's first major intensifier
- `qiiirdar` = first rare extended retort-fix-root marker
- `daiim` = fix-cycle-vessel bridge token connecting this folio forward to `f87r` Dwale
- `chodaiin` = volatile-heat-fix cycle completed under active valve discipline
- `qiiirkchy` = second rare extended retort marker
- `sheam + ykeam` = double union close
- `saiin = 0` = no explicit salt regime despite the page's complexity

## Direct Line-By-Line Literal Ledger

{ledger}

## Multilens Translation Atlas

{formal}

{mythic}

## Direct Operational Meaning

Paragraph 1 establishes the apparatus and boundary logic before the page permits any serious danger. The work is contained, passed through the alembic outlet, dissolved into triple essence, and pushed through the first rare extended retort while the valve-earth boundary remains explicit. Paragraph 2 restarts the volatile branch, keeps the route wet and bounded, binds double essence into conduit structure, reaches a decisive checkpoint at `daiin`, inserts the `daiim` vessel bridge that links this folio to later Dwale correction logic, then survives a second rare extended retort before closing in two union markers. The page therefore reads as a controlled volatile corrective distillate, not as a reckless poison purge.

## Mathematical Extraction

Across the formal math lenses, `f3v` is a bounded high-risk controller that permits two rare excursions into extended retort space but never relinquishes boundary integrity. The page maximizes containment, valve discipline, and conduit binding while keeping the final state liquid and relational rather than salt-fixed. Its dominant invariant is not raw extraction power but safe passage through unstable regions plus one bridge insertion into a later compound medicine.

## Mythic Extraction

Across the mythic lenses, `f3v` is the balancing answer to the prior storm. The operator receives a dangerous volatile charge, survives two ordeals, meets a corrective ally at the checkpoint, and returns carrying a medicine whose purpose is not domination but moderation, healing, and rebalancing.

## All-Lens Zero Point

`f3v` means: if volatile matter must be handled near danger, first lock the vessel, then allow controlled rare excursions, then insert the corrective bridge before closure, so the final product can later temper stronger compounds instead of amplifying their violence.

## Dense One-Sentence Compression

Build the sealed volatile route, dissolve the work into triple essence, survive two rare retort excursions under valve control, inject the corrective bridge at checkpoint, and close in double union as a balancing liquid medicine.

## Formal Mathematical Overlay For F3v

### Imported Kernel Equations

\\[\\mathcal H := L^2(\\widehat{{\\mathbb C}}, \\mu), \\qquad \\rho \\in \\mathcal T_1(\\mathcal H), \\qquad \\rho \\succeq 0, \\qquad \\mathrm{{Tr}}(\\rho)=1\\]

\\[\\mathcal H_{{\\mathrm{{tot}}}} = \\left(\\bigoplus_r \\mathcal H_r\\right) \\oplus \\left(\\bigoplus_e \\mathcal H_{{\\Lambda_e}}\\right) \\oplus \\mathcal H_{{\\mathrm{{fail}}}}\\]

\\[x_{{n+1}}^{{\\mathrm{{chem}}}} = K_n x_n^{{\\mathrm{{chem}}}}, \\qquad \\mathbf{{1}}^T K_n = \\mathbf{{1}}^T\\]

\\[g = \\mathrm{{Coll}}(X), \\qquad X = \\mathrm{{Expand}}(g) \\oplus r\\]

\\[\\Phi_j^{{(\\lambda)}} = T_\\lambda^{{-1}} \\circ \\Phi_j^{{(\\mathrm{{AQM}})}} \\circ T_\\lambda\\]

### Typed State Machine

\\[\\mathcal R_{{f3v}} = \\{{r_{{\\mathrm{{contain}}}}, r_{{\\mathrm{{triple}}}}, r_{{\\mathrm{{retort1}}}}, r_{{\\mathrm{{checkpoint}}}}, r_{{\\mathrm{{bridge}}}}, r_{{\\mathrm{{retort2}}}}, r_{{\\mathrm{{union}}}}\\}}\\]

\\[\\mathcal E_\\Lambda = \\{{e_{{\\mathrm{{valve}}}}, e_{{\\mathrm{{retort}}}}, e_{{\\mathrm{{corrective}}}}\\}}\\]

\\[\\delta(e_{{\\mathrm{{valve}}}}): r_{{\\mathrm{{contain}}}} \\to r_{{\\mathrm{{checkpoint}}}} \\to r_{{\\mathrm{{bridge}}}} \\to r_{{\\mathrm{{union}}}}\\]

\\[\\delta(e_{{\\mathrm{{retort}}}}): r_{{\\mathrm{{contain}}}} \\to r_{{\\mathrm{{triple}}}} \\to r_{{\\mathrm{{retort1}}}} \\to r_{{\\mathrm{{retort2}}}}\\]

\\[\\delta(e_{{\\mathrm{{corrective}}}}): r_{{\\mathrm{{checkpoint}}}} \\to r_{{\\mathrm{{bridge}}}} \\to r_{{\\mathrm{{union}}}}\\]

\\[\\rho_0 \\in \\mathcal H_{{r_{{\\mathrm{{contain}}}}}}, \\qquad x_0^{{\\mathrm{{chem}}}} = \\begin{{bmatrix}} m_{{\\mathrm{{source}}}}^0 \\\\ m_{{\\mathrm{{volatile}}}}^0 \\\\ 0 \\\\ 0 \\\\ 0 \\end{{bmatrix}}, \\qquad g_0 = \\mathrm{{Coll}}(\\rho_0)\\]

### Canonical AQM Line Operators

{ops}

### Paragraph Compositions

\\[\\Psi_{{P1}} = \\Phi_{{\\mathrm{{P1_6}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P1_5}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P1_4}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P1_3}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P1_2}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P1_1}}}}^{{\\mathrm{{AQM}}}}\\]

\\[\\Psi_{{P2}} = \\Phi_{{\\mathrm{{P2_14}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P2_13}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P2_12}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P2_11}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P2_10}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P2_9}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P2_8}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P2_7}}}}^{{\\mathrm{{AQM}}}}\\]

\\[\\rho_{{P1}} = \\Psi_{{P1}}(\\rho_0), \\qquad \\rho_* = \\Psi_{{P2}}(\\rho_{{P1}})\\]

### Invariants And Counts

\\[N_{{\\mathrm{{qiiir}}}}(f3v) = 2, \\qquad N_{{\\mathrm{{daiim}}}}(f3v) = 1, \\qquad N_{{\\mathrm{{saiin}}}}(f3v) = 0\\]

\\[N_{{\\mathrm{{valve}}}}(f3v) = 4, \\qquad N_{{\\mathrm{{union}}}}(f3v) = 2\\]

\\[\\mathrm{{Tr}}\\!\\left(\\Pi_{{\\mathrm{{fail}}}} \\rho_*\\right) \\ll \\mathrm{{Tr}}\\!\\left(\\Pi_{{\\mathrm{{bridge}}}} \\rho_*\\right), \\qquad \\mathbf{{1}}^T x_*^{{\\mathrm{{chem}}}} = \\mathbf{{1}}^T x_0^{{\\mathrm{{chem}}}}\\]

### Cross-Lens Transport

\\[\\Phi_j^{{(\\mathrm{{CUT}})}} = T_{{\\mathrm{{CUT}}}}^{{-1}} \\Phi_j^{{(\\mathrm{{AQM}})}} T_{{\\mathrm{{CUT}}}}, \\qquad \\Phi_j^{{(\\mathrm{{phys}})}} = T_{{\\mathrm{{phys}}}}^{{-1}} \\Phi_j^{{(\\mathrm{{AQM}})}} T_{{\\mathrm{{phys}}}}\\]

\\[\\Phi_j^{{(\\mathrm{{wave}})}} = T_{{\\mathrm{{wave}}}}^{{-1}} \\Phi_j^{{(\\mathrm{{AQM}})}} T_{{\\mathrm{{wave}}}}, \\qquad \\Phi_j^{{(\\mathrm{{wavemath}})}} = T_{{\\mathrm{{wavemath}}}}^{{-1}} \\Phi_j^{{(\\mathrm{{AQM}})}} T_{{\\mathrm{{wavemath}}}}\\]

\\[\\Phi_j^{{(\\lambda)}} = T_\\lambda^{{-1}} \\Phi_j^{{(\\mathrm{{AQM}})}} T_\\lambda, \\qquad \\lambda \\in \\{{\\mathrm{{CUT}}, \\mathrm{{phys}}, \\mathrm{{wave}}, \\mathrm{{wavemath}}\\}}\\]

### Folio Theorem

\\[\\rho_* = (\\Psi_{{P2}} \\circ \\Psi_{{P1}})(\\rho_0)\\]

\\[\\forall \\rho_0 \\in \\mathcal H_{{r_{{\\mathrm{{contain}}}}}} : \\bigl(N_{{\\mathrm{{qiiir}}}}=2 \\land N_{{\\mathrm{{daiim}}}}=1 \\land N_{{\\mathrm{{saiin}}}}=0\\bigr) \\Rightarrow \\rho_* \\in \\mathcal H_{{r_{{\\mathrm{{union}}}}}}\\]

\\[x_*^{{\\mathrm{{chem}}}} = \\begin{{bmatrix}} m_{{\\mathrm{{source}}}}^* \\\\ m_{{\\mathrm{{volatile}}}}^* \\\\ m_{{\\mathrm{{essence}}}}^* \\\\ m_{{\\mathrm{{corrective}}}}^* \\\\ m_{{\\mathrm{{union}}}}^* \\end{{bmatrix}}, \\qquad m_{{\\mathrm{{corrective}}}}^* > 0, \\qquad m_{{\\mathrm{{union}}}}^* > 0\\]

The formal theorem of `f3v` is therefore:

1. the page begins only after containment is secured
2. it permits two bounded excursions into rare retort space
3. it injects exactly one corrective bridge token before completion
4. it closes in double union without salt precipitation

## Final Draft Audit

- EVA inventory complete for all 14 visible lines
- direct literal ledger present for each line
- 16 formal math lenses populated with per-line equations
- 4 mythic lenses populated with per-line readings
- rare markers preserved explicitly: `seees`, `qiiirdar`, `daiim`, `qiiirkchy`
- major unresolved issue preserved honestly: visual hellebore rival remains, but operational evidence favors chamomile corrective

## Plant Crystal Contribution

- controlled volatile corrective station
- first explicit Dwale corrective bridge token
- rare retort discipline line
- valve-caution reinforcement
- double-union closure without salt
"""
    ).rstrip() + "\n"


def main() -> None:
    OUTPUT.write_text(render(), encoding="utf-8")


if __name__ == "__main__":
    main()
