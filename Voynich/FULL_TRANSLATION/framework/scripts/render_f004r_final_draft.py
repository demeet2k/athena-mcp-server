from __future__ import annotations

from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "folios" / "F004R_FINAL_DRAFT.md"

LINES = [
    (
        "P1.1",
        "kodalchy.chpady.sheol.ol.sheey.qotey.doiin.chor.ytoy",
        "`kodalchy` contain-heat-fix-structure-volatile-active; `chpady` volatile-press-earth-fix-active; `sheol` transition-essence-fluid; `ol` fluid; `sheey` transition-double-essence-active; `qotey` transmute-driven-essence-active; `doiin` fix-heat-cycle; `chor` volatile-outlet; `ytoy` moist-driven-heat-active.",
        "Open with a compact process-header that contains, heats, fixes, and structures the volatile, then press the earthy material, move the essence into fluid medium, activate double essence, drive the transmutation, and send the heated moist stream toward the outlet.",
        "encode the whole infusion program in a single opening header and begin moist heated outlet flow",
        "strong",
    ),
    (
        "P1.2",
        "dchor.shol.shol.cthol.shtchy.chaiin.*s.choraiin.chom",
        "`dchor` fix-volatile-outlet; `shol.shol` doubled transition-fluid; `cthol` conduit-fluid; `shtchy` transition-driven-volatile-active; `chaiin` volatile-cycle-complete; `*s` damaged dissolve marker; `choraiin` volatile-outlet-cycle-complete; `chom` volatile-vessel.",
        "Fix the volatile at the outlet, steep it twice in heated liquid, carry the flow through the conduit, drive the volatile transition, complete the volatile cycle, preserve the damaged dissolve witness, then close the route back into the volatile vessel.",
        "perform the first doubled steeping and return the liquid to vessel",
        "strong",
    ),
    (
        "P1.3",
        "otchol.chol.chy.chaiin.qotaiin.daiin.shain",
        "`otchol` timed-volatile-fluid; `chol` volatile-fluid; `chy` volatile-active; `chaiin` volatile-cycle-complete; `qotaiin` transmute-driven-cycle-complete; `daiin` checkpoint; `shain` transition-complete.",
        "Time the volatile liquid, keep it active, complete the volatile cycle, complete the driven transmutation cycle, checkpoint the result, and mark the transition complete.",
        "verify that the first steeping transferred the volatile fraction completely",
        "strong",
    ),
    (
        "P1.4",
        "qotchol.chy.yty.daiin.qokaiin.cthy",
        "`qotchol` transmute-driven-volatile-fluid; `chy` volatile-active; `yty` moist-driven-active; `daiin` checkpoint; `qokaiin` extract-contain-cycle-complete; `cthy` conduit-bind-active.",
        "Drive the volatile liquid again, keep the material moist and active, mark another checkpoint, extract the contained cycle to completion, and bind the work back into the conduit.",
        "seal paragraph one with extraction-complete conduit binding",
        "strong",
    ),
    (
        "P2.5",
        "pydaiin.qotchy.*tydy",
        "`pydaiin` press-moist-fix-cycle-complete; `qotchy` transmute-driven-volatile-active; `*tydy` damaged driven-fix-active cluster.",
        "Re-press the moist fixed cycle, restart driven volatile motion, and preserve the damaged fixation cluster without pretending more certainty than the witness allows.",
        "restart the maceration branch under damaged but still readable fixation logic",
        "mixed",
    ),
    (
        "P2.6",
        "chor.shytchy.dy*cheey",
        "`chor` volatile-outlet; `shytchy` transition-moist-driven-volatile-active; `dy*cheey` damaged fixed double-essence cluster.",
        "Carry the work to the outlet, keep the transition moist, driven, and volatile, then move into a damaged fixed double-essence cluster whose exact tail remains uncertain.",
        "keep the moist volatile branch moving while preserving the damaged essence witness",
        "uncertain",
    ),
    (
        "P2.7",
        "qotoiin.cthol.daiin.cthom",
        "`qotoiin` transmute-heat-cycle; `cthol` conduit-fluid; `daiin` checkpoint; `cthom` conduit-vessel.",
        "Drive the heat-cycle of transmutation through the conduit-fluid, checkpoint the result, and rehouse it in the conduit-vessel.",
        "re-stabilize the macerated flow inside the conduit-vessel",
        "strong",
    ),
    (
        "P2.8",
        "shor.shol.shol.cthy.cpholdy",
        "`shor` transition-outlet; `shol.shol` doubled transition-fluid; `cthy` conduit-bind-active; `cpholdy` alembic-fluid-fix-active.",
        "Return to the outlet, steep the work a second time through doubled transition fluid, bind the conduit again, and fix the resulting liquid through the alembic.",
        "perform the second doubled steeping and alembic fixation",
        "strong",
    ),
    (
        "P2.9",
        "daiin.ckhochy.tchy.koraiin",
        "`daiin` checkpoint; `ckhochy` valve-heat-volatile-active; `tchy` driven-volatile-active; `koraiin` contain-outlet-cycle-complete.",
        "Checkpoint the second steeping, perform a valve check on the heated volatile, keep the driven volatile active, and close the outlet cycle in containment.",
        "validate the heated volatile through an explicit valve check",
        "strong",
    ),
    (
        "P2.10",
        "odal.shor.shyshol.cphaiin",
        "`odal` heat-fix-structure; `shor` transition-outlet; `shyshol` transition-moist-transition-fluid; `cphaiin` alembic-cycle-complete.",
        "Fix the structure under heat, carry the transition to the outlet, keep the medium moist and transitional, and complete the alembic cycle.",
        "turn repeated steeping into stable structured infusion",
        "mixed",
    ),
    (
        "P2.11",
        "qotchoiin.shear.qoty",
        "`qotchoiin` transmute-driven-volatile-heat-cycle; `shear` transition-essence-root; `qoty` transmute-heat-active.",
        "Drive the volatile heat-cycle once more through transmutation, root the transition-essence, and keep the transmuting heat alive.",
        "root the infused essence before final verification",
        "mixed",
    ),
    (
        "P2.12",
        "soiin.chaiin.chaiin",
        "`soiin` dissolve-heat-cycle; `chaiin.chaiin` volatile-cycle-complete x2.",
        "Dissolve through a heat-cycle and then verify the volatile cycle twice in immediate succession.",
        "perform the folio's unique doubled volatile verification",
        "strong",
    ),
    (
        "P2.13",
        "daiin.cthey",
        "`daiin` final checkpoint; `cthey` conduit-essence-active.",
        "Land the page on a final checkpoint and leave the conduit-essence state active rather than dead or mineralized.",
        "close the page with active conduit essence after final verification",
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
        "Temperance",
        "Justice",
        "The Hierophant",
        "The Fool",
        "The Moon",
        "Strength",
        "The Star",
        "Judgment",
        "The Emperor",
        "The Hermit",
        "Wheel of Fortune",
        "The World",
    ],
    "Juggling": [
        "declare the recipe",
        "first double steep",
        "verify the first pass",
        "bind the extract",
        "restart the pattern",
        "carry the damaged throw",
        "re-center in vessel",
        "second double steep",
        "valve check catch",
        "fix the frame",
        "root the return",
        "double confirm",
        "final live hold",
    ],
    "Story Writing": [
        "process-header opening",
        "first infusion scene",
        "first proof beat",
        "paragraph seal",
        "second-act restart",
        "damaged witness scene",
        "recovery beat",
        "second infusion scene",
        "checkpoint suspense",
        "stabilization beat",
        "rooting beat",
        "double-proof climax",
        "active ending",
    ],
    "Hero's Journey": [
        "receive the method",
        "enter the first bath",
        "complete the first trial",
        "bind the gained route",
        "cross into repetition",
        "survive the damaged passage",
        "recover the vessel",
        "enter the second bath",
        "pass the gate test",
        "stabilize the boon",
        "root the lesson",
        "win double confirmation",
        "return with active essence",
    ],
}

MOVEMENTS = [
    "encode the method",
    "steep twice",
    "verify transfer",
    "bind the conduit",
    "restart maceration",
    "carry the damaged essence",
    "return to vessel",
    "steep twice again",
    "check the valve",
    "fix the structure",
    "root the essence",
    "confirm twice",
    "leave the conduit alive",
]

LEGEND = {
    "aqm": "`rho^-` incoming folio line state; `rho^+` outgoing line state; `Phi_line^(AQM)` source operator chain.",
    "cut": "`X=(kappa,varphi,ell,b)` with containment, phase, liquid flux, and boundary integrity.",
    "liminal": "`p(r)` regime mass, `lambda(e)` liminal-edge load, `f` fail-space mass.",
    "aetheric": "`g` compressed seed, `X` expanded state, `r_line` residual address.",
    "chemistry": "`x=[m_source,m_liquid,m_volatile,m_fixed,m_active]^T`; `K_line` conserves total material.",
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
    out = ["### Paragraph 1 - process header, first doubled steeping, and first complete transfer", ""]
    for line_id, eva, literal, operational, *_ in LINES[:4]:
        out += [f"- `{line_id}`", f"  EVA: `{eva}`", f"  Literal chain: {literal}", f"  Operational English: {operational}", ""]
    out += ["### Paragraph 2 - maceration restart, second doubled steeping, and final verification", ""]
    for line_id, eva, literal, operational, *_ in LINES[4:]:
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
        f"""# F004R Final Draft - Dense Multilens Translation Atlas

## Final Draft Status

- Status: `authoritative final-draft folio`
- Manuscript role: `warm infusion / maceration page with progressive fixation`
- Book: `Book I - Herbal / materia medica`
- Production standard: `framework-governed dense folio with full symbolic matrix`
- Source baseline: `F004R.md`
- Release target: `Plant Crystal`, unified corpus, metro layer, and master manuscript

## Purpose

This file is the authoritative final-draft version of `f004r`.

Where `f3r` and `f3v` revolve around retort stress and corrective containment, `f4r` quiets the curriculum back into repeated liquid transfer. The page is dominated by transition-fluid logic, doubled steeping markers, progressive fixation, explicit checkpoints, conduit re-binding, and a unique doubled volatile verification at the end. Across the local corpus, this fits warm wine or oil maceration better than hard distillation, with mugwort operationally favored over saxifrage.

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
- Botanical identity remains partially disputed between saxifrage and mugwort.
- The strongest claim is process identity: repeated steeping or maceration under low heat, conduit filtering, progressive fixation, and doubled verification.

## Folio Zero Claim

`f4r` means: encode the infusion method in the opening header, steep the volatile material twice, verify the transfer, restart the maceration branch, steep it twice again, run valve and alembic checks, and do not stop until the volatile extraction is verified complete two times in a row.

## Folio Identity

| Field | Value |
| --- | --- |
| Folio | `f4r` |
| Quire | `A` |
| Bifolio | `bA4 = f4 + f5` |
| Currier language | `A` |
| Currier hand | `1` |
| Illustration | single plant with herculeaf and two leaf-shape families |
| Botanical candidate | `Artemisia vulgaris` operationally favored; `Saxifraga cespitosa` remains the strongest visual rival |
| Risk level | moderate |
| Direct confidence | high on maceration process, moderate on recipe role, lower on exact species |

## Visual Grammar and Codicology

- `herculeaf attachment` = centralized carrier medium or one dominant infusion body
- `two leaf-shape families` = two stages or textures of material release
- `center bifolio placement` = the quire pauses after storm/correction and re-teaches stable transfer discipline
- `compact four-line first paragraph` = recipe header plus first complete infusion loop
- `long second paragraph` = repetition, filtration, and verification outweigh novelty

## Full EVA

```text
P1.1: kodalchy.chpady.sheol.ol.sheey.qotey.doiin.chor.ytoy-
P1.2: dchor.shol.shol.cthol.shtchy.chaiin.*s.choraiin.chom-
P1.3: otchol.chol.chy.chaiin.qotaiin.daiin.shain-
P1.4: qotchol.chy.yty.daiin.qokaiin.cthy=

P2.5: pydaiin.qotchy.*tydy-
P2.6: chor.shytchy.dy*cheey-
P2.7: qotoiin.cthol.daiin.cthom-
P2.8: shor.shol.shol.cthy.cpholdy-
P2.9: daiin.ckhochy.tchy.koraiin-
P2.10: odal.shor.shyshol.cphaiin-
P2.11: qotchoiin.shear.qoty-
P2.12: soiin.chaiin.chaiin-
P2.13: daiin.cthey=
```

## Core VML Machinery Active On F4r

- `kodalchy` = one-token process header for containment, heat, fixation, structure, and volatile activation
- `shol.shol` appears twice and behaves like doubled heated-liquid steeping
- `daiin` checkpoints dominate the page and regulate each transfer stage
- `cpholdy` = alembic-fluid fixation after the second steeping
- `ckhochy` = explicit valve check on heated volatile medium
- `chaiin.chaiin` = the unique doubled volatile verification closing the page
- `saiin = 0` = no salt regime; this is liquid transfer, not crystallization

## Direct Line-By-Line Literal Ledger

{ledger}

## Multilens Translation Atlas

{formal}

{mythic}

## Direct Operational Meaning

Paragraph 1 acts like a complete method card: it names the process in compressed form, performs the first doubled steeping, verifies that volatile transfer has completed, then binds the extract back into the conduit. Paragraph 2 restarts the cycle, preserves damaged witness points honestly, rehouses the work in the conduit-vessel, performs a second doubled steeping, checks the valve, stabilizes the liquid through the alembic, roots the essence, then ends on the page's decisive signature: `soiin.chaiin.chaiin`, a doubled proof that the volatile cycle is done. The page therefore reads as progressive warm maceration or infusion rather than hard retort violence.

## Mathematical Extraction

Across the formal math lenses, `f4r` is a low-heat repeated-transfer controller. It prefers convergence by iteration over convergence by force. The state moves through liquid media, conduit binds, and active checkpoints, while the terminal invariant is repeated verification rather than union or salt precipitation. The page optimizes confidence of extraction completeness.

## Mythic Extraction

Across the mythic lenses, `f4r` is the patient craft chapter after ordeal. The operator learns not to rush. Instead of storm, the manuscript teaches soak, wait, decant, verify, and only then move on. Mastery here is repetition plus proof.

## All-Lens Zero Point

`f4r` means: when a medicine needs gentle transfer rather than aggressive separation, run repeated steeping cycles through a bounded conduit, verify each cycle, and do not trust the extract until the volatile completion has been witnessed twice.

## Dense One-Sentence Compression

Steep the volatile medium twice, verify the transfer, restart the maceration, steep twice again, run valve and alembic checks, and close only after doubled volatile verification.

## Formal Mathematical Overlay For F4r

### Imported Kernel Equations

\\[\\mathcal H := L^2(\\widehat{{\\mathbb C}}, \\mu), \\qquad \\rho \\in \\mathcal T_1(\\mathcal H), \\qquad \\rho \\succeq 0, \\qquad \\mathrm{{Tr}}(\\rho)=1\\]

\\[\\mathcal H_{{\\mathrm{{tot}}}} = \\left(\\bigoplus_r \\mathcal H_r\\right) \\oplus \\left(\\bigoplus_e \\mathcal H_{{\\Lambda_e}}\\right) \\oplus \\mathcal H_{{\\mathrm{{fail}}}}\\]

\\[x_{{n+1}}^{{\\mathrm{{chem}}}} = K_n x_n^{{\\mathrm{{chem}}}}, \\qquad \\mathbf{{1}}^T K_n = \\mathbf{{1}}^T\\]

\\[g = \\mathrm{{Coll}}(X), \\qquad X = \\mathrm{{Expand}}(g) \\oplus r\\]

\\[\\Phi_j^{{(\\lambda)}} = T_\\lambda^{{-1}} \\circ \\Phi_j^{{(\\mathrm{{AQM}})}} \\circ T_\\lambda\\]

### Typed State Machine

\\[\\mathcal R_{{f4r}} = \\{{r_{{\\mathrm{{header}}}}, r_{{\\mathrm{{steep1}}}}, r_{{\\mathrm{{checkpoint1}}}}, r_{{\\mathrm{{restart}}}}, r_{{\\mathrm{{steep2}}}}, r_{{\\mathrm{{verify2}}}}, r_{{\\mathrm{{activeclose}}}}\\}}\\]

\\[\\mathcal E_\\Lambda = \\{{e_{{\\mathrm{{steep}}}}, e_{{\\mathrm{{filter}}}}, e_{{\\mathrm{{verify}}}}\\}}\\]

\\[\\delta(e_{{\\mathrm{{steep}}}}): r_{{\\mathrm{{header}}}} \\to r_{{\\mathrm{{steep1}}}} \\to r_{{\\mathrm{{checkpoint1}}}} \\to r_{{\\mathrm{{restart}}}} \\to r_{{\\mathrm{{steep2}}}}\\]

\\[\\delta(e_{{\\mathrm{{filter}}}}): r_{{\\mathrm{{steep1}}}} \\to r_{{\\mathrm{{checkpoint1}}}} \\to r_{{\\mathrm{{steep2}}}} \\to r_{{\\mathrm{{activeclose}}}}\\]

\\[\\delta(e_{{\\mathrm{{verify}}}}): r_{{\\mathrm{{checkpoint1}}}} \\to r_{{\\mathrm{{verify2}}}} \\to r_{{\\mathrm{{activeclose}}}}\\]

\\[\\rho_0 \\in \\mathcal H_{{r_{{\\mathrm{{header}}}}}}, \\qquad x_0^{{\\mathrm{{chem}}}} = \\begin{{bmatrix}} m_{{\\mathrm{{source}}}}^0 \\\\ m_{{\\mathrm{{liquid}}}}^0 \\\\ 0 \\\\ 0 \\\\ 0 \\end{{bmatrix}}, \\qquad g_0 = \\mathrm{{Coll}}(\\rho_0)\\]

### Canonical AQM Line Operators

{ops}

### Paragraph Compositions

\\[\\Psi_{{P1}} = \\Phi_{{\\mathrm{{P1_4}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P1_3}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P1_2}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P1_1}}}}^{{\\mathrm{{AQM}}}}\\]

\\[\\Psi_{{P2}} = \\Phi_{{\\mathrm{{P2_13}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P2_12}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P2_11}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P2_10}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P2_9}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P2_8}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P2_7}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P2_6}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P2_5}}}}^{{\\mathrm{{AQM}}}}\\]

\\[\\rho_{{P1}} = \\Psi_{{P1}}(\\rho_0), \\qquad \\rho_* = \\Psi_{{P2}}(\\rho_{{P1}})\\]

### Invariants And Counts

\\[N_{{\\mathrm{{steep}}}}(f4r) = 2, \\qquad N_{{\\mathrm{{daiin}}}}(f4r) = 5, \\qquad N_{{\\mathrm{{saiin}}}}(f4r) = 0\\]

\\[N_{{\\mathrm{{doubleverify}}}}(f4r) = 1, \\qquad N_{{\\mathrm{{chaiin}}}}(f4r) = 4\\]

\\[\\mathrm{{Tr}}\\!\\left(\\Pi_{{\\mathrm{{verify}}}} \\rho_*\\right) > \\mathrm{{Tr}}\\!\\left(\\Pi_{{\\mathrm{{union}}}} \\rho_*\\right), \\qquad \\mathbf{{1}}^T x_*^{{\\mathrm{{chem}}}} = \\mathbf{{1}}^T x_0^{{\\mathrm{{chem}}}}\\]

### Cross-Lens Transport

\\[\\Phi_j^{{(\\mathrm{{CUT}})}} = T_{{\\mathrm{{CUT}}}}^{{-1}} \\Phi_j^{{(\\mathrm{{AQM}})}} T_{{\\mathrm{{CUT}}}}, \\qquad \\Phi_j^{{(\\mathrm{{phys}})}} = T_{{\\mathrm{{phys}}}}^{{-1}} \\Phi_j^{{(\\mathrm{{AQM}})}} T_{{\\mathrm{{phys}}}}\\]

\\[\\Phi_j^{{(\\mathrm{{wave}})}} = T_{{\\mathrm{{wave}}}}^{{-1}} \\Phi_j^{{(\\mathrm{{AQM}})}} T_{{\\mathrm{{wave}}}}, \\qquad \\Phi_j^{{(\\mathrm{{wavemath}})}} = T_{{\\mathrm{{wavemath}}}}^{{-1}} \\Phi_j^{{(\\mathrm{{AQM}})}} T_{{\\mathrm{{wavemath}}}}\\]

\\[\\Phi_j^{{(\\lambda)}} = T_\\lambda^{{-1}} \\Phi_j^{{(\\mathrm{{AQM}})}} T_\\lambda, \\qquad \\lambda \\in \\{{\\mathrm{{CUT}}, \\mathrm{{phys}}, \\mathrm{{wave}}, \\mathrm{{wavemath}}\\}}\\]

### Folio Theorem

\\[\\rho_* = (\\Psi_{{P2}} \\circ \\Psi_{{P1}})(\\rho_0)\\]

\\[\\forall \\rho_0 \\in \\mathcal H_{{r_{{\\mathrm{{header}}}}}} : \\bigl(N_{{\\mathrm{{steep}}}}=2 \\land N_{{\\mathrm{{doubleverify}}}}=1 \\land N_{{\\mathrm{{saiin}}}}=0\\bigr) \\Rightarrow \\rho_* \\in \\mathcal H_{{r_{{\\mathrm{{activeclose}}}}}}\\]

\\[x_*^{{\\mathrm{{chem}}}} = \\begin{{bmatrix}} m_{{\\mathrm{{source}}}}^* \\\\ m_{{\\mathrm{{liquid}}}}^* \\\\ m_{{\\mathrm{{volatile}}}}^* \\\\ m_{{\\mathrm{{fixed}}}}^* \\\\ m_{{\\mathrm{{active}}}}^* \\end{{bmatrix}}, \\qquad m_{{\\mathrm{{liquid}}}}^* > 0, \\qquad m_{{\\mathrm{{active}}}}^* > 0\\]

The formal theorem of `f4r` is therefore:

1. the page computes transfer by repeated steeping, not by violent separation
2. convergence is enforced through frequent checkpoints and conduit re-binding
3. the decisive terminal act is doubled verification, not union or salt closure
4. the product remains an active liquid essence

## Final Draft Audit

- EVA inventory complete for all 13 visible lines
- direct literal ledger present for each line
- 16 formal math lenses populated with per-line equations
- 4 mythic lenses populated with per-line readings
- key page signatures preserved explicitly: `kodalchy`, doubled `shol.shol`, `cpholdy`, `ckhochy`, and `chaiin.chaiin`
- major unresolved issue preserved honestly: saxifrage remains a visual rival, but operational evidence favors mugwort-style maceration

## Plant Crystal Contribution

- repeated steeping station
- progressive fixation line
- doubled verification signature
- valve-checked maceration route
- active liquid close without salt
"""
    ).rstrip() + "\n"


def main() -> None:
    OUTPUT.write_text(render(), encoding="utf-8")


if __name__ == "__main__":
    main()
