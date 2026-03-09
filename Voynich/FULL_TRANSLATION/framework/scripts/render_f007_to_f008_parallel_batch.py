from __future__ import annotations

from pathlib import Path
from textwrap import dedent


ROOT = Path(__file__).resolve().parents[2]
FOLIOS_DIR = ROOT / "folios"

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

KERNEL_EQUATIONS = dedent(
    """\
    \\[\\mathcal H := L^2(\\widehat{\\mathbb C}, \\mu), \\qquad \\rho \\in \\mathcal T_1(\\mathcal H), \\qquad \\rho \\succeq 0, \\qquad \\mathrm{Tr}(\\rho)=1\\]

    \\[\\mathcal H_{\\mathrm{tot}} = \\left(\\bigoplus_r \\mathcal H_r\\right) \\oplus \\left(\\bigoplus_e \\mathcal H_{\\Lambda_e}\\right) \\oplus \\mathcal H_{\\mathrm{fail}}\\]

    \\[x_{n+1}^{\\mathrm{chem}} = K_n x_n^{\\mathrm{chem}}, \\qquad \\mathbf{1}^T K_n = \\mathbf{1}^T\\]

    \\[g = \\mathrm{Coll}(X), \\qquad X = \\mathrm{Expand}(g) \\oplus r\\]

    \\[\\Phi_j^{(\\lambda)} = T_\\lambda^{-1} \\circ \\Phi_j^{(\\mathrm{AQM})} \\circ T_\\lambda\\]
    """
).rstrip()

DIRECT_SOURCES = [
    "NEW/SECTION I - BOOK I_ THE HERBAL _ MATERIA MEDICA.md",
    "NEW/working/VML_RIGOROUS_RETRANSCRIPTION_QUIRES_ABCDEFG.md",
    "NEW/working/VML_RECIPE_CROSSREF.md",
    "NEW/working/VML_CONSISTENCY_PROOF.md",
    "eva/EVA TRANSCRIPTION ORIGIONAL.txt",
]

DERIVED_SOURCES = [
    "FULL_TRANSLATION/framework/FORMAL_MULTILENS_FRAMEWORK.md",
    "FULL_TRANSLATION/framework/registry/lenses.json",
    "FULL_TRANSLATION/framework/registry/math_kernel_registry.md",
    "FRESH/_extracted/The Holographic Manuscript Brain.txt",
]


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


def identity_table(rows: list[tuple[str, str]]) -> str:
    lines = ["| Field | Value |", "| --- | --- |"]
    lines.extend(f"| {left} | {right} |" for left, right in rows)
    return "\n".join(lines)


def direct_ledger(folio: dict[str, object]) -> str:
    lines_by_id = {line[0]: line for line in folio["lines"]}
    out: list[str] = []
    for group in folio["groups"]:
        out += [f"### {group['title']}", ""]
        for line_id in group["line_ids"]:
            _line_id, eva, literal, operational, _summary, _confidence = lines_by_id[line_id]
            out += [
                f"- `{line_id}`",
                f"  EVA: `{eva}`",
                f"  Literal chain: {literal}",
                f"  Operational English: {operational}",
                "",
            ]
    return "\n".join(out).rstrip()


def formal_sections(folio: dict[str, object]) -> str:
    out: list[str] = []
    for lens, title in FORMAL_LENSES:
        out += [f"### {title}", ""]
        for line_id, eva, _literal, _operational, summary, confidence in folio["lines"]:
            out += [
                f"- `{line_id}`",
                "  Equation:",
                "",
                f"  {eq(lens, line_id, eva)}",
                "",
                f"  Variable legend: {LEGEND[lens]}",
                f"  Reading: {summary}.",
                f"  Confidence: {confidence}",
                "",
            ]
    return "\n".join(out).rstrip()


def mythic_sections(folio: dict[str, object]) -> str:
    story = folio.get("story_frames", folio["movements"])
    hero = folio.get("hero_frames", folio["movements"])

    def frame_at(frames: list[str], idx: int, fallback: str) -> str:
        if frames:
            if idx < len(frames):
                return frames[idx]
            return frames[-1]
        return fallback

    frames_map = {
        "Tarot": folio["tarot_cards"],
        "Juggling": folio["movements"],
        "Story Writing": story,
        "Hero's Journey": hero,
    }
    out: list[str] = []
    for title, frames in frames_map.items():
        out += [f"### {title}", ""]
        for idx, (line_id, _eva, _literal, _operational, summary, confidence) in enumerate(folio["lines"]):
            movement = frame_at(folio["movements"], idx, summary)
            out += [
                f"- `{line_id}`",
                f"  Frame: {frame_at(frames, idx, movement)}",
                f"  Movement: {movement}",
                f"  Reading: {summary}.",
                f"  Confidence: {confidence}",
                "",
            ]
    return "\n".join(out).rstrip()


def operator_matrix(folio: dict[str, object]) -> str:
    out: list[str] = []
    for line_id, eva, *_rest in folio["lines"]:
        out += [f"- `{line_id}`", "", f"\\[\\Phi_{{\\mathrm{{{slug(line_id)}}}}}^{{\\mathrm{{AQM}}}} = {op_chain(eva)}\\]", ""]
    return "\n".join(out).rstrip()


def paragraph_compositions(folio: dict[str, object]) -> str:
    out: list[str] = []
    for group in folio["groups"]:
        ops = " \\circ ".join(
            rf"\Phi_{{\mathrm{{{slug(line_id)}}}}}^{{\mathrm{{AQM}}}}" for line_id in reversed(group["line_ids"])
        )
        out.append(f"\\[\\Psi_{{{group['label']}}} = {ops}\\]")
        out.append("")
    labels = [group["label"] for group in folio["groups"]]
    state_chain = ", \\qquad ".join(
        rf"\rho_{{{labels[idx]}}} = \Psi_{{{labels[idx]}}}(\rho_0)" if idx == 0 else rf"\rho_{{{labels[idx]}}} = \Psi_{{{labels[idx]}}}(\rho_{{{labels[idx-1]}}})"
        for idx in range(len(labels))
    )
    out.append(f"\\[{state_chain}, \\qquad \\rho_* = \\rho_{{{labels[-1]}}}\\]")
    return "\n".join(out).rstrip()


def render_pointer(folio: dict[str, object]) -> str:
    direct_sources = folio.get("direct_sources", DIRECT_SOURCES)
    derived_sources = folio.get("derived_sources", DERIVED_SOURCES)
    return dedent(
        f"""# {folio["folio_id"]} - {folio["pointer_title"]}

## Authoritative Final Draft

For the authoritative final-draft folio, see `{folio["folio_id"]}_FINAL_DRAFT.md`.

## Production Status

- Folio lane: `Agent {folio["folio_id"]}`
- Manuscript position: {folio["pointer_position"]}
- Page type: {folio["pointer_page_type"]}
- Working conclusion: {folio["pointer_conclusion"]}
- Final-draft status: complete

## Source Stack

### Direct folio sources
"""
    ).rstrip() + "\n" + "\n".join(f"- `{source}`" for source in direct_sources) + "\n\n### Derived renderer support\n\n" + "\n".join(
        f"- `{source}`" for source in derived_sources
    ) + "\n\n## Folio Identity\n\n" + identity_table(folio["pointer_identity"]) + "\n\n## Full EVA Transcription\n\n```text\n" + folio["full_eva"] + "\n```\n\n## Working Judgment\n\n" + folio["pointer_judgment"] + "\n"


def render_folio(folio: dict[str, object]) -> str:
    ledger = direct_ledger(folio)
    formal = formal_sections(folio)
    mythic = mythic_sections(folio)
    ops = operator_matrix(folio)
    compositions = paragraph_compositions(folio)
    direct_sources = folio.get("direct_sources", DIRECT_SOURCES)
    derived_sources = folio.get("derived_sources", DERIVED_SOURCES)
    source_stack = "\n".join(f"- `{path}`" for path in list(direct_sources) + list(derived_sources))
    reading_contract = "\n".join(f"- {line}" for line in folio["reading_contract"])
    visual = "\n".join(f"- {line}" for line in folio["visual_grammar"])
    core_vml = "\n".join(f"- {line}" for line in folio["core_vml"])
    audit = "\n".join(f"- {line}" for line in folio["audit"])
    crystal = "\n".join(f"- {line}" for line in folio["crystal_contribution"])
    book_label = folio.get("book_label", "Book I - Herbal / materia medica")
    release_target = folio.get("release_target", "Plant Crystal, unified corpus, metro layer, and master manuscript")

    return dedent(
        f"""# {folio["folio_id"]} Final Draft - Dense Multilens Translation Atlas

## Final Draft Status

- Status: `authoritative final-draft folio`
- Manuscript role: `{folio["manuscript_role"]}`
- Book: `{book_label}`
- Production standard: `framework-governed dense folio with full symbolic matrix`
- Source baseline: `{folio["folio_id"]}.md`
- Release target: `{release_target}`

## Purpose

This file is the authoritative final-draft version of `{folio["folio_id"].lower()}`.

{folio["purpose"]}

## Source Stack

{source_stack}

## Reading Contract

{reading_contract}

## Folio Zero Claim

`{folio["folio_id"].lower()}` means: {folio["zero_claim"]}

## Folio Identity

{identity_table(folio["identity_rows"])}

## Visual Grammar and Codicology

{visual}

## Full EVA

```text
{folio["full_eva"]}
```

## Core VML Machinery Active On {folio["folio_short"]}

{core_vml}

## Direct Line-By-Line Literal Ledger

{ledger}

## Multilens Translation Atlas

{formal}

{mythic}

## Direct Operational Meaning

{folio["direct_operational_meaning"]}

## Mathematical Extraction

{folio["mathematical_extraction"]}

## Mythic Extraction

{folio["mythic_extraction"]}

## All-Lens Zero Point

`{folio["all_lens_zero_point"]}`

## Dense One-Sentence Compression

{folio["dense_compression"]}

## Formal Mathematical Overlay For {folio["folio_short"]}

### Imported Kernel Equations

{KERNEL_EQUATIONS}

### Typed State Machine

{folio["typed_state_machine"]}

### Canonical AQM Line Operators

{ops}

### Paragraph Compositions

{compositions}

### Invariants And Counts

{folio["invariants"]}

### Cross-Lens Transport

\\[\\Phi_j^{{(\\mathrm{{CUT}})}} = T_{{\\mathrm{{CUT}}}}^{{-1}} \\Phi_j^{{(\\mathrm{{AQM}})}} T_{{\\mathrm{{CUT}}}}, \\qquad \\Phi_j^{{(\\mathrm{{phys}})}} = T_{{\\mathrm{{phys}}}}^{{-1}} \\Phi_j^{{(\\mathrm{{AQM}})}} T_{{\\mathrm{{phys}}}}\\]

\\[\\Phi_j^{{(\\mathrm{{wave}})}} = T_{{\\mathrm{{wave}}}}^{{-1}} \\Phi_j^{{(\\mathrm{{AQM}})}} T_{{\\mathrm{{wave}}}}, \\qquad \\Phi_j^{{(\\mathrm{{wavemath}})}} = T_{{\\mathrm{{wavemath}}}}^{{-1}} \\Phi_j^{{(\\mathrm{{AQM}})}} T_{{\\mathrm{{wavemath}}}}\\]

\\[\\Phi_j^{{(\\lambda)}} = T_\\lambda^{{-1}} \\Phi_j^{{(\\mathrm{{AQM}})}} T_\\lambda, \\qquad \\lambda \\in \\{{\\mathrm{{CUT}}, \\mathrm{{phys}}, \\mathrm{{wave}}, \\mathrm{{wavemath}}\\}}\\]

### Folio Theorem

{folio["theorem"]}

## Final Draft Audit

{audit}

## Crystal Contribution

{crystal}
"""
    ).rstrip() + "\n"


FOLIOS: list[dict[str, object]] = [
    {
        "folio_id": "F007R",
        "folio_short": "F7r",
        "manuscript_role": "direct fire-to-product maximum-essence page",
        "purpose": "`f7r` is the quire's pure bloom page. It begins with `fchodaiin`, where fire and completion appear in the very first token, then escalates through `oeeees` and `deeeese`, the strongest essence-intensity cluster yet translated in Quire A. The no-leaf huge-flower image and the compressed two-part text field both support the same reading: this folio suppresses intermediate handling and privileges direct conversion from source to maximized product.",
        "reading_contract": [
            "The operational signature is far stronger than the inherited botanical naming.",
            "The no-leaf visual grammar is treated as evidence for omitted intermediate stages, not for absolute species identity.",
            "Currier and Friedman witness splits remain visible where they materially affect sequence shape.",
            "The strongest claim is process identity: fire-opened direct conversion under quadruple and quintuple essence intensification.",
        ],
        "zero_claim": "open with fire, accelerate the source into quadruple and quintuple essence density, use reflux only as a control surface, and end with a direct concentrated flower-product rather than a staged intermediate.",
        "identity_rows": [
            ("Folio", "`f7r`"),
            ("Quire", "`A`"),
            ("Bifolio", "`bA2 = f2 + f7`"),
            ("Currier language", "`A`"),
            ("Currier hand", "`1`"),
            ("Illustration", "single giant flower with no leaves"),
            ("Botanical candidate", "`Trientalis europaea` is inherited but weak; operationally the page behaves like a maximum-output flower concentrate rather than a securely named species page"),
            ("Risk level", "moderate"),
            ("Direct confidence", "high on direct fire-to-product concentration; low on exact species"),
        ],
        "visual_grammar": [
            "`no leaves` = the page suppresses intermediary processing stages",
            "`single giant flower` = product emphasis overwhelms source detail",
            "`paired with the f2 leaf` = the safe fundamentals leaf is answered by a maximum-essence leaf",
            "`short second half` = once the concentration event lands, the page closes quickly",
        ],
        "full_eva": dedent(
            """\
            P1:  fchodaiin.shopchey.qko.shey.qoos.sheey.charochy-
            P2:  dcheey.keo.r.shor.dold.dchey.kchey.otchy.cheody-
            P3:  oeeees.cheodaiin.sheey.ytcheey.qotchy.chald-
            P4:  qokcho.cho.lochey.daiin.ychey.kchos.odaiin-
            P5:  oaiir.otaiin=

            P6:  ksholochey.qotoees.chkoldy.otchor.choaiin-
            P7:  dshoy.cthol.chol.otchol.dain.shody.shol.chotchy-
            P8:  okchey.deeeese.choty.qotchy.chol.keey.choky.chain-
            P9:  qokechy.ol.choiin.chol.cphey.shckhy.chochy.kchod-
            P10: s.chain.chor.daiin.chckhy=
            """
        ).rstrip(),
        "core_vml": [
            "`fchodaiin` = fire opens and certifies the first movement in one token",
            "`dold` = the reflux-control vocabulary from `f1v` returns inside a hotter page",
            "`oeeees` = quadruple-essence activation",
            "`deeeese` = fix-quintuple-essence-dissolve-essence, the strongest essence spike yet translated in Quire A",
            "`kchod` = contained volatile-fix close rather than salt precipitation",
            "the page has no true salt terminal; it finishes as intensified product, not as residue",
        ],
        "groups": [
            {
                "label": "P1",
                "title": "Paragraph 1 - fire opening, reflux control, and first bloom seal",
                "line_ids": ["P1", "P2", "P3", "P4", "P5"],
            },
            {
                "label": "P2",
                "title": "Paragraph 2 - restarted conversion and quintuple-essence climax",
                "line_ids": ["P6", "P7", "P8", "P9", "P10"],
            },
        ],
        "lines": [
            (
                "P1",
                "fchodaiin.shopchey.qko.shey.qoos.sheey.charochy",
                "`fchodaiin` fire-volatile-heat-fix-complete; `shopchey` transition-press-volatile-essence-active; `qko` circulated containment; `shey` transition-essence-active; `qoos` circulated heat-dissolve; `sheey` transition-double-essence-active; `charochy` volatile-root-heated-active close.",
                "Open with fire and immediate certification, press the volatile essence into transition, circulate the heated dissolve, and aim the doubled essence directly toward root-bloom product.",
                "fire-open the page and drive the volatile root directly toward product",
                "strong",
            ),
            (
                "P2",
                "dcheey.keo.r.shor.dold.dchey.kchey.otchy.cheody",
                "`dcheey` fixed volatile double-essence-active; `keo.r` contained essence outlet; `shor` transition outlet; `dold` fix-fluid-fix reflux; `dchey` fixed volatile essence-active; `kchey` contained volatile essence-active; `otchy` timed volatile-active; `cheody` volatile-essence-heat-fix-active.",
                "Fix the doubled essence at the outlet, run a reflux turn through the fluid channel, and keep the timed volatile essence under active heat-fix.",
                "hold the intensifying stream under reflux and outlet control",
                "strong",
            ),
            (
                "P3",
                "oeeees.cheodaiin.sheey.ytcheey.qotchy.chald",
                "`oeeees` heated quadruple-essence dissolve; `cheodaiin` volatile-essence-heat completion; `sheey` transition-double-essence-active; `ytcheey` moist-driven volatile double-essence-active; `qotchy` circulated driven volatile-active; `chald` volatile-structure-fix.",
                "Push the material into quadruple-essence activation, certify the heated essence, and carry the doubled volatile into structural fix.",
                "execute the first major essence spike and begin product fixation",
                "strong",
            ),
            (
                "P4",
                "qokcho.cho.lochey.daiin.ychey.kchos.odaiin",
                "`qokcho` circulated contained volatile-heat; `cho` volatile-heat; `lochey` liquid volatile-essence-active; `daiin` checkpoint; `ychey` moist volatile-essence-active; `kchos` contained volatile-dissolve; `odaiin` heated completion.",
                "Checkpoint the contained heated volatile, moisten the essence, dissolve it inside containment, and close the first section with heated completion.",
                "checkpoint the concentrated stream and carry it into heated completion",
                "strong",
            ),
            (
                "P5",
                "oaiir.otaiin",
                "`oaiir` heated doubled-cycle token; `otaiin` timed completion.",
                "Seal the brief first movement with a doubled heated cycle and timed completion.",
                "end the first bloom movement quickly and decisively",
                "mixed",
            ),
            (
                "P6",
                "ksholochey.qotoees.chkoldy.otchor.choaiin",
                "`ksholochey` contained transition-fluid volatile-essence-active; `qotoees` circulated driven double-essence; `chkoldy` volatile-valve-fluid-fix-active; `otchor` timed volatile outlet; `choaiin` volatile-heat completion.",
                "Restart under contained transition fluid, circulate doubled essence, keep the valve and fluid-fix alive, and drive the volatile outlet into completion.",
                "restart the product stream under contained transition law",
                "strong",
            ),
            (
                "P7",
                "dshoy.cthol.chol.otchol.dain.shody.shol.chotchy",
                "`dshoy` fixed transition-heat-active; `cthol` conduit fluid; `chol` volatile fluid; `otchol` timed volatile fluid; `dain` completion; `shody` transition-heat-fix-active; `shol` transition fluid; `chotchy` driven volatile-active.",
                "Drive the conduit and fluid path through one more heated volatile cycle, mark completion, and keep the transition channel active for the final ascent.",
                "carry the restart through conduit and fluid law before the climax",
                "mixed",
            ),
            (
                "P8",
                "okchey.deeeese.choty.qotchy.chol.keey.choky.chain",
                "`okchey` heated contained volatile-essence-active; `deeeese` fix-quintuple-essence-dissolve-essence; `choty` volatile-timed-active; `qotchy` circulated driven volatile-active; `chol` volatile fluid; `keey` contained doubled essence-active; `choky` volatile-heat-contain-active; `chain` volatile cycle-complete.",
                "Enter the page's quintuple-essence climax, keep the volatile timed and circulating, contain the doubled essence, and end the main reaction in a completed heated containment state.",
                "execute the folio's quintuple-essence climax and bind the product",
                "strong",
            ),
            (
                "P9",
                "qokechy.ol.choiin.chol.cphey.shckhy.chochy.kchod",
                "`qokechy` circulated contained volatile-essence-active; `ol` fluid; `choiin` volatile completion; `chol` volatile fluid; `cphey` pressed essence-active; `shckhy` transition-valve-active; `chochy` volatile-heat-active; `kchod` contained volatile-heat-fix.",
                "Send the concentrated fluid through a pressed essence and valve-governed route, keep the volatile heated, and land it in contained product fixation.",
                "finalize the concentrated bloom through alembic and valve discipline",
                "strong",
            ),
            (
                "P10",
                "s.chain.chor.daiin.chckhy",
                "`s` dissolve; `chain` volatile cycle-complete; `chor` volatile outlet; `daiin` checkpoint; `chckhy` volatile-valve-active.",
                "Wash once more, prove the volatile outlet, checkpoint the run, and leave the valve alive at the close.",
                "finish with one last wash and outlet check",
                "strong",
            ),
        ],
        "tarot_cards": [
            "The Tower",
            "Justice",
            "Strength",
            "Judgment",
            "The Sun",
            "Temperance",
            "The Chariot",
            "The Star",
            "The Magician",
            "The World",
        ],
        "movements": [
            "ignite the bloom stream",
            "reflux the rising essence",
            "strike the quadruple concentration",
            "checkpoint the contained bloom",
            "seal the first flare",
            "restart the transition channel",
            "carry the conduit ascent",
            "unleash the quintuple essence",
            "press the finished concentrate through the valve",
            "prove the outlet one last time",
        ],
        "story_frames": [
            "fire-sigil opening",
            "reflux control beat",
            "quadruple-essence escalation",
            "checkpoint consolidation",
            "first flare close",
            "second-wave restart",
            "conduit ascent beat",
            "quintuple-essence climax",
            "product-throat resolution",
            "live-valve ending",
        ],
        "hero_frames": [
            "accept the fire opening",
            "endure the reflux test",
            "survive the first intensity jump",
            "submit to verification",
            "close the first labor",
            "restart the ascent",
            "keep the conduit road",
            "take the highest essence ordeal",
            "return through the narrow throat",
            "leave the gate awake",
        ],
        "direct_operational_meaning": "The first half of `f7r` is a direct flower-conversion route: fire, reflux control, quadruple essence, checkpoint, seal. The second half restarts without slowing down, then lands the page's defining event: `deeeese`, quintuple essence fixed and dissolved into product. Unlike the safe paired leaf at `f2`, this page is not about pedagogy by balance. It is about how to force a source into maximized bloom output with as few intermediates as possible while still keeping one valve and one checkpoint alive.",
        "mathematical_extraction": "Across the formal math lenses, `f7r` is a short-horizon concentration maximizer with a hard nonlinear gain event. The operator trajectory injects fire at the opening, passes through one reflux stabilization turn, then crosses two amplitude jumps: quadruple essence and quintuple essence. The control problem is not long-term equilibrium; it is keeping the concentrated stream admissible long enough to convert directly into bounded product. The dominant invariant is maximal essence gain under minimal staging.",
        "mythic_extraction": "Across the mythic lenses, `f7r` is the bloom rite. Nothing here wants to wander or deliberate. The source is thrown into fire, swells beyond ordinary measure, and becomes flower-product at once. It is the myth of sudden flowering under dangerous heat, not of cultivation over time.",
        "all_lens_zero_point": "when the desired medicine is bloom intensity itself, the route is direct fire, brief reflux discipline, and a controlled leap into maximal essence before immediate product fixation",
        "dense_compression": "Open with fire, drive the source through quadruple and quintuple essence concentration, and bind the direct bloom product before the intensified stream escapes.",
        "typed_state_machine": dedent(
            """\
            \\[\\mathcal R_{f7r} = \\{r_{\\mathrm{fireopen}}, r_{\\mathrm{reflux}}, r_{\\mathrm{quad}}, r_{\\mathrm{checkpoint}}, r_{\\mathrm{restart}}, r_{\\mathrm{quint}}, r_{\\mathrm{product}}\\}\\]

            \\[\\mathcal E_\\Lambda = \\{e_{\\mathrm{fire}}, e_{\\mathrm{reflux}}, e_{\\mathrm{quad}}, e_{\\mathrm{quint}}\\}\\]

            \\[\\delta(e_{\\mathrm{fire}}): r_{\\mathrm{fireopen}} \\to r_{\\mathrm{reflux}}\\]

            \\[\\delta(e_{\\mathrm{quad}}): r_{\\mathrm{reflux}} \\to r_{\\mathrm{quad}} \\to r_{\\mathrm{checkpoint}}\\]

            \\[\\delta(e_{\\mathrm{reflux}}): r_{\\mathrm{checkpoint}} \\to r_{\\mathrm{restart}}\\]

            \\[\\delta(e_{\\mathrm{quint}}): r_{\\mathrm{restart}} \\to r_{\\mathrm{quint}} \\to r_{\\mathrm{product}}\\]

            \\[\\rho_0 \\in \\mathcal H_{r_{\\mathrm{fireopen}}}, \\qquad x_0^{\\mathrm{chem}} = \\begin{bmatrix} m_{\\mathrm{source}}^0 \\\\ m_{\\mathrm{volatile}}^0 \\\\ m_{\\mathrm{liquid}}^0 \\\\ 0 \\\\ 0 \\end{bmatrix}, \\qquad g_0 = \\mathrm{Coll}(\\rho_0)\\]
            """
        ).rstrip(),
        "invariants": dedent(
            """\
            \\[N_{\\mathrm{fire}}(f7r) = 1, \\qquad N_{\\mathrm{quad}}(f7r) = 1, \\qquad N_{\\mathrm{quint}}(f7r) = 1\\]

            \\[N_{\\mathrm{reflux}}(f7r) = 1, \\qquad N_{\\mathrm{daiin}}(f7r) = 2, \\qquad N_{\\mathrm{salt}}(f7r) = 0\\]

            \\[\\mathrm{Tr}(\\Pi_{\\mathrm{product}} \\rho_*) \\gg \\mathrm{Tr}(\\Pi_{\\mathrm{fail}} \\rho_*), \\qquad \\mathbf{1}^T x_*^{\\mathrm{chem}} = \\mathbf{1}^T x_0^{\\mathrm{chem}}\\]
            """
        ).rstrip(),
        "theorem": dedent(
            """\
            \\[\\rho_* = (\\Psi_{P2} \\circ \\Psi_{P1})(\\rho_0)\\]

            \\[\\forall \\rho_0 \\in \\mathcal H_{r_{\\mathrm{fireopen}}} : \\bigl(N_{\\mathrm{fire}}=1 \\land N_{\\mathrm{quad}}=1 \\land N_{\\mathrm{quint}}=1\\bigr) \\Rightarrow \\rho_* \\in \\mathcal H_{r_{\\mathrm{product}}}\\]

            \\[x_*^{\\mathrm{chem}} = \\begin{bmatrix} m_{\\mathrm{source}}^* \\\\ m_{\\mathrm{volatile}}^* \\\\ m_{\\mathrm{liquid}}^* \\\\ m_{\\mathrm{essence}}^* \\\\ m_{\\mathrm{fixed}}^* \\end{bmatrix}, \\qquad m_{\\mathrm{essence}}^* \\gg m_{\\mathrm{essence}}^0, \\qquad m_{\\mathrm{fixed}}^* > 0\\]

            The formal theorem of `f7r` is therefore:

            1. fire opens and verifies the route immediately
            2. one reflux turn prevents the bloom stream from escaping
            3. the route crosses a quadruple-essence spike and then a quintuple-essence spike
            4. the page closes in direct product fixation rather than in salt precipitation or extended recirculation
            """
        ).rstrip(),
        "audit": [
            "EVA inventory complete for all 10 visible lines",
            "direct literal ledger present for each line",
            "16 formal math lenses populated with per-line equations",
            "4 mythic lenses populated with per-line readings",
            "key signatures preserved explicitly: `fchodaiin`, `dold`, `oeeees`, `deeeese`, and the no-leaf bloom grammar",
            "major unresolved issue preserved honestly: inherited species naming remains weak and secondary to the process reading",
        ],
        "crystal_contribution": [
            "maximum-essence direct-conversion station",
            "quadruple-to-quintuple escalation line",
            "fire-open bloom route",
            "reflux-controlled flower concentrate",
            "direct product close without salt",
        ],
        "pointer_title": "Maximum-Essence Direct Conversion",
        "pointer_position": "the `f2/f7` leaf's fire-open maximum-essence counterpart to the safe instructional pair",
        "pointer_page_type": "single-plant illustrated procedure page",
        "pointer_conclusion": "direct fire opening, one reflux turn, quadruple and quintuple essence spikes, and bounded direct bloom-product fixation",
        "pointer_identity": [
            ("Folio", "`f7r`"),
            ("Quire", "`A`"),
            ("Bifolio", "`bA2 = f2 + f7`"),
            ("Currier language", "`A`"),
            ("Currier hand", "`1`"),
            ("Illustration", "single giant flower with no leaves"),
            ("Botanical consensus", "weak inherited `Starflower` label; process reading is much stronger than species naming"),
            ("Risk level", "moderate"),
            ("Direct confidence", "high on maximum-essence direct conversion"),
        ],
        "pointer_judgment": "`f7r` is a maximum-essence direct-conversion page. It opens with `fchodaiin`, carries one explicit reflux-control turn, climbs through `oeeees` and `deeeese`, and ends as a direct flower-product fix rather than as a long staged extraction.",
    },
    {
        "folio_id": "F007V",
        "folio_short": "F7v",
        "manuscript_role": "equilibrium crystallization and triple-mode fixation page",
        "purpose": "`f7v` is the balancing answer to `f7r`. Where the recto forces a bloom straight through fire, the verso sets volatile and fixation at parity, floods the page with `daiin` checkpoints, and ends by fixing structure, fluid, and source in a single `dal.dol.dor` sequence. The cross-reference layer supports the reading of a long cold oil capture, especially a St. John's Wort style red oil, more strongly than the inherited low-confidence bog-myrtle label.",
        "reading_contract": [
            "The visible parity of `d-` and `ch-` is treated as primary evidence, not as a metaphor layered afterward.",
            "The inherited botanical names remain visible, but the operational cross-reference toward `Hypericum` is explicitly stronger than the older `Myrica` guess.",
            "Damaged tokens are preserved as damaged, especially in the double-essence and shotch clusters.",
            "The strongest claim is process identity: controlled crystallization / oil fixation by repeated verification rather than heat escalation.",
        ],
        "zero_claim": "balance volatile and fixation forces exactly, verify the route more than once per line, then lock structure, fluid, and source in sequence so that the essence survives as fixed liquid rather than vapor.",
        "identity_rows": [
            ("Folio", "`f7v`"),
            ("Quire", "`A`"),
            ("Bifolio", "`bA2 = f2 + f7`"),
            ("Currier language", "`A`"),
            ("Currier hand", "`1`"),
            ("Illustration", "single Herbal A plant with ordinary text field and no extreme visual warnings"),
            ("Botanical candidate", "inherited `Myrica gale` remains visible, but operationally `Hypericum perforatum` cold oil maceration is the stronger fit"),
            ("Risk level", "moderate"),
            ("Direct confidence", "high on equilibrium fixation and liquid quintessence capture; moderate on exact species"),
        ],
        "visual_grammar": [
            "`ordinary page geometry` = the drama is inside the text profile rather than in the image",
            "`paired with f7r` = maximum bloom output is answered by balanced liquid fixation",
            "`nine lines with ten completions` = verification itself becomes visual rhythm",
            "`no major fire display` = the page privileges patience and locking over ignition",
        ],
        "full_eva": dedent(
            """\
            P1:  polyshy.shey.tchody.qopchy.otshol.dy.daiin.tshodody-
            P2:  chochy.cthy.daiin.qoky.ch**y.daiin.cthol.cthy.cthd-
            P3:  qokchy.dykchy.chkeey.kshy.ky.ty.dor.cheey.ol.cheol.dy-
            P4:  chotee**.ochan.choschy.dain.sho.kshy.shol.deees.dol-
            P5:  dchadaiin.qotchy.cheey.tcheey=

            P6:  kchor.sheod.sh*odaiin.shodaiin.oksholshol.dair.qos-
            P7:  okshodain.chor.cheor.odaiin.shotch*.dal.dol.dor.aiin-
            P8:  qoteeeo.r.cho.cheeody.qotchey.tey.okchor.daiin-
            P9:  shokeeo.daiin.chokchy.dor.deol.dy.dol.daiin=
            """
        ).rstrip(),
        "core_vml": [
            "`d-` and `ch-` are in exact parity across the folio profile",
            "`10 daiin in 9 lines` = the page verifies itself more densely than any translated Quire A leaf so far",
            "`dal.dol.dor` = triple-mode fixation of structure, fluid, and source",
            "`deol` = essence captured and fixed in liquid",
            "`deees` = triple-essence dissolve inside a fixation-heavy regime",
            "heat remains present but subordinate; long fixation dominates the page's control law",
        ],
        "groups": [
            {
                "label": "P1",
                "title": "Paragraph 1 - parity setup and first completion wall",
                "line_ids": ["P1", "P2", "P3", "P4", "P5"],
            },
            {
                "label": "P2",
                "title": "Paragraph 2 - restarted fixation, triple-mode lock, and liquid quintessence close",
                "line_ids": ["P6", "P7", "P8", "P9"],
            },
        ],
        "lines": [
            (
                "P1",
                "polyshy.shey.tchody.qopchy.otshol.dy.daiin.tshodody",
                "`polyshy` press-fluid-transition-active; `shey` transition-essence-active; `tchody` driven volatile-heat-fix-active; `qopchy` circulated press-volatile-active; `otshol` timed transition fluid; `dy` fixed; `daiin` checkpoint; `tshodody` driven transition-heat-fix-heat-fix.",
                "Press the heated fluid into driven volatile fixation, circulate the pressed stream, and land the first movement in checkpointed double heat-fix.",
                "set the parity regime under immediate verification",
                "strong",
            ),
            (
                "P2",
                "chochy.cthy.daiin.qoky.ch**y.daiin.cthol.cthy.cthd",
                "`chochy` volatile-heat-active; `cthy` conduit-bind-active; `daiin` checkpoint; `qoky` circulated containment-active; `ch**y` damaged volatile-active cluster; `daiin` checkpoint again; `cthol` conduit fluid; `cthy` conduit bind; `cthd` conduit heat-fix.",
                "Keep the volatile alive inside the bound conduit, preserve the damaged cluster honestly, and reinforce the route with two checkpoints before the fluid bind is fixed again.",
                "double-check the conduit before deeper fixation",
                "strong",
            ),
            (
                "P3",
                "qokchy.dykchy.chkeey.kshy.ky.ty.dor.cheey.ol.cheol.dy",
                "`qokchy` circulated contained volatile-active; `dykchy` fixed contained volatile-active; `chkeey` volatile-contained double-essence-active; `kshy` contained transition-active; `ky` contain-active; `ty` drive-active; `dor` fix-source; `cheey` volatile double-essence-active; `ol` fluid; `cheol` volatile-essence-fluid; `dy` fixed.",
                "Convert the contained volatile into a bound and fixed liquid essence stream, anchor it at the source, and keep the doubled essence alive inside fluid fixation.",
                "translate volatile parity into fixed liquid essence",
                "strong",
            ),
            (
                "P4",
                "chotee**.ochan.choschy.dain.sho.kshy.shol.deees.dol",
                "`chotee**` damaged volatile-heat-double-essence cluster; `ochan` heated volatile cycle; `choschy` volatile-dissolve-active; `dain` completion; `sho` transition-heat; `kshy` contained transition-active; `shol` transition fluid; `deees` fixed triple-essence dissolve; `dol` fix-fluid.",
                "Carry the damaged double-essence cluster through heated volatile dissolve, complete the line, and force triple essence to settle into fixed fluid.",
                "drive the page into triple-essence fluid fixation",
                "mixed",
            ),
            (
                "P5",
                "dchadaiin.qotchy.cheey.tcheey",
                "`dchadaiin` fixed volatile cycle-complete; `qotchy` circulated driven volatile-active; `cheey` volatile double-essence-active; `tcheey` driven volatile double-essence-active.",
                "Close the first half as a driven volatile completion where doubled essence is retained rather than burned off.",
                "seal the first fixation movement under doubled essence",
                "strong",
            ),
            (
                "P6",
                "kchor.sheod.sh*odaiin.shodaiin.oksholshol.dair.qos",
                "`kchor` contained volatile outlet; `sheod` transition-essence-fix; `sh*odaiin` damaged transition-fix completion; `shodaiin` transition-heat-fix completion; `oksholshol` heated contained double-transition fluid; `dair` fix-rotation; `qos` circulated dissolve.",
                "Restart under fixed transition law, keep the outlet contained, and rotate the doubled transition fluid through one more circulated dissolve.",
                "restart the page as a controlled rotation instead of a fire spike",
                "mixed",
            ),
            (
                "P7",
                "okshodain.chor.cheor.odaiin.shotch*.dal.dol.dor.aiin",
                "`okshodain` heated contained transition completion; `chor` volatile outlet; `cheor` volatile-essence outlet; `odaiin` heated completion; `shotch*` damaged driven transition-volatile cluster; `dal` fix-structure; `dol` fix-fluid; `dor` fix-source; `aiin` cycle-complete.",
                "Heat-complete the contained transition, hold both volatile outlets open, and then apply the page's defining triple-mode fixation: structure, fluid, and source in sequence.",
                "execute the decisive triple-mode fixation",
                "strong",
            ),
            (
                "P8",
                "qoteeeo.r.cho.cheeody.qotchey.tey.okchor.daiin",
                "`qoteeeo` circulated driven triple-essence heat; `r` root marker; `cho` volatile-heat; `cheeody` volatile-double-essence-heat-fix-active; `qotchey` circulated driven volatile-essence-active; `tey` driven essence-active; `okchor` heated contained volatile outlet; `daiin` checkpoint.",
                "Drive one last triple-essence return through heated volatile essence-fix, keep the outlet contained, and checkpoint the stabilized stream.",
                "stabilize the triple-essence return under contained outlet law",
                "strong",
            ),
            (
                "P9",
                "shokeeo.daiin.chokchy.dor.deol.dy.dol.daiin",
                "`shokeeo` transition-heat-contained double-essence; `daiin` checkpoint; `chokchy` volatile-heat-contain-active; `dor` fix-source; `deol` fixed essence-fluid; `dy` fixed; `dol` fix-fluid; `daiin` checkpoint again.",
                "Hold the doubled essence in contained transition heat, fix the source, capture the essence as fluid, and end with both fixed liquid and a final checkpoint.",
                "fix the quintessence in liquid form and close under doubled verification",
                "strong",
            ),
        ],
        "tarot_cards": [
            "Justice",
            "The Hierophant",
            "Temperance",
            "Strength",
            "Judgment",
            "The Hermit",
            "The Emperor",
            "The Star",
            "The World",
        ],
        "movements": [
            "set the parity mixture",
            "double-check the conduit",
            "thicken the liquid essence",
            "fix the triple-essence fluid",
            "seal the first half",
            "restart the rotation",
            "lock structure fluid and source",
            "stabilize the returning essence",
            "capture the quintessence in liquid",
        ],
        "story_frames": [
            "balanced opening",
            "conduit-proof beat",
            "liquid-thickening beat",
            "triple-essence fixation turn",
            "halfway seal",
            "rotational restart",
            "triple-lock climax",
            "contained return beat",
            "liquid-quintessence ending",
        ],
        "hero_frames": [
            "enter the balanced chamber",
            "submit to doubled proof",
            "learn the liquid body",
            "survive the triple fix",
            "seal the first ordeal",
            "walk the turning road",
            "master the three locks",
            "carry the return flame",
            "return with fixed liquid essence",
        ],
        "direct_operational_meaning": "`f7v` is the manuscript's first true equilibrium page. The first half builds parity and makes the operator prove it repeatedly. The second half restarts under rotational discipline and then lands the defining lock: `dal.dol.dor`. The final line does not seek a dry residue. It fixes the essence in liquid form. That makes the page read less like calcination and more like a long cold oil or tincture whose success is measured by stable capture, not by burn or ash.",
        "mathematical_extraction": "Across the formal math lenses, `f7v` behaves like a damped convergence procedure. The system is engineered so that volatile amplitude and fixation amplitude remain matched rather than runaway. The repeated checkpoints reduce admissible drift, `dal.dol.dor` acts as a three-axis lock, and `deol` is the final state where essence remains in the liquid channel. The dominant invariant is parity-preserving convergence toward fixed fluid essence.",
        "mythic_extraction": "Across the mythic lenses, `f7v` is not an ordeal of force but of patience. The hero proves the vessel again and again, then seals the world in three directions and returns not with a spark or a plume but with a living liquid kept from escape.",
        "all_lens_zero_point": "if the aim is a stable living liquid, the lawful route is parity, repeated proof, and threefold fixation rather than maximal heat",
        "dense_compression": "Balance volatile and fixation, verify the route more than once per line, apply three locks to structure fluid and source, and keep the essence alive as fixed liquid.",
        "typed_state_machine": dedent(
            """\
            \\[\\mathcal R_{f7v} = \\{r_{\\mathrm{parity}}, r_{\\mathrm{conduitproof}}, r_{\\mathrm{liquidfix}}, r_{\\mathrm{restart}}, r_{\\mathrm{triplelock}}, r_{\\mathrm{deolclose}}\\}\\]

            \\[\\mathcal E_\\Lambda = \\{e_{\\mathrm{verify}}, e_{\\mathrm{rotate}}, e_{\\mathrm{triplelock}}, e_{\\mathrm{deol}}\\}\\]

            \\[\\delta(e_{\\mathrm{verify}}): r_{\\mathrm{parity}} \\to r_{\\mathrm{conduitproof}} \\to r_{\\mathrm{liquidfix}}\\]

            \\[\\delta(e_{\\mathrm{rotate}}): r_{\\mathrm{liquidfix}} \\to r_{\\mathrm{restart}}\\]

            \\[\\delta(e_{\\mathrm{triplelock}}): r_{\\mathrm{restart}} \\to r_{\\mathrm{triplelock}}\\]

            \\[\\delta(e_{\\mathrm{deol}}): r_{\\mathrm{triplelock}} \\to r_{\\mathrm{deolclose}}\\]

            \\[\\rho_0 \\in \\mathcal H_{r_{\\mathrm{parity}}}, \\qquad x_0^{\\mathrm{chem}} = \\begin{bmatrix} m_{\\mathrm{source}}^0 \\\\ m_{\\mathrm{volatile}}^0 \\\\ m_{\\mathrm{liquid}}^0 \\\\ 0 \\\\ 0 \\end{bmatrix}, \\qquad g_0 = \\mathrm{Coll}(\\rho_0)\\]
            """
        ).rstrip(),
        "invariants": dedent(
            """\
            \\[N_d(f7v) = N_{\\mathrm{ch}}(f7v), \\qquad N_{\\mathrm{daiin}}(f7v) = 10, \\qquad N_{\\mathrm{triplelock}}(f7v) = 1\\]

            \\[N_{\\mathrm{deol}}(f7v) = 1, \\qquad N_{\\mathrm{lowheat}}(f7v) > N_{\\mathrm{fire}}(f7v), \\qquad N_{\\mathrm{salt}}(f7v) = 0\\]

            \\[\\mathrm{Tr}(\\Pi_{\\mathrm{deolclose}} \\rho_*) \\gg \\mathrm{Tr}(\\Pi_{\\mathrm{fail}} \\rho_*), \\qquad \\mathbf{1}^T x_*^{\\mathrm{chem}} = \\mathbf{1}^T x_0^{\\mathrm{chem}}\\]
            """
        ).rstrip(),
        "theorem": dedent(
            """\
            \\[\\rho_* = (\\Psi_{P2} \\circ \\Psi_{P1})(\\rho_0)\\]

            \\[\\forall \\rho_0 \\in \\mathcal H_{r_{\\mathrm{parity}}} : \\bigl(N_d=N_{\\mathrm{ch}} \\land N_{\\mathrm{daiin}}=10 \\land N_{\\mathrm{deol}}=1\\bigr) \\Rightarrow \\rho_* \\in \\mathcal H_{r_{\\mathrm{deolclose}}}\\]

            \\[x_*^{\\mathrm{chem}} = \\begin{bmatrix} m_{\\mathrm{source}}^* \\\\ m_{\\mathrm{volatile}}^* \\\\ m_{\\mathrm{liquid}}^* \\\\ m_{\\mathrm{essence}}^* \\\\ m_{\\mathrm{fixed}}^* \\end{bmatrix}, \\qquad m_{\\mathrm{liquid}}^* > 0, \\qquad m_{\\mathrm{essence}}^* > 0, \\qquad m_{\\mathrm{fixed}}^* > 0\\]

            The formal theorem of `f7v` is therefore:

            1. the page holds volatile and fixation in explicit parity
            2. it proves that parity through the densest checkpoint pattern yet translated in Quire A
            3. it applies structure, fluid, and source fixation in sequence
            4. it closes by trapping essence in liquid instead of venting or burning it away
            """
        ).rstrip(),
        "audit": [
            "EVA inventory complete for all 9 visible lines",
            "direct literal ledger present for each line",
            "16 formal math lenses populated with per-line equations",
            "4 mythic lenses populated with per-line readings",
            "key signatures preserved explicitly: d/ch parity, `10 daiin`, `dal.dol.dor`, and `deol`",
            "major unresolved issue preserved honestly: inherited bog-myrtle naming remains weaker than the operational Hypericum-style oil reading",
        ],
        "crystal_contribution": [
            "equilibrium crystallization station",
            "verification-dense fixation line",
            "triple-mode lock sequence",
            "liquid quintessence capture route",
            "cold-oil balance counterpart to the `f7r` bloom page",
        ],
        "pointer_title": "Equilibrium Crystallization",
        "pointer_position": "the `f2/f7` leaf's balance counterpart to `f7r` and the fixation answer to the earlier safe pair",
        "pointer_page_type": "single-plant illustrated procedure page",
        "pointer_conclusion": "volatile-fixation parity, dense verification, triple-mode fixation, and final liquid quintessence capture",
        "pointer_identity": [
            ("Folio", "`f7v`"),
            ("Quire", "`A`"),
            ("Bifolio", "`bA2 = f2 + f7`"),
            ("Currier language", "`A`"),
            ("Currier hand", "`1`"),
            ("Illustration", "standard Herbal A single plant"),
            ("Botanical consensus", "operationally closer to `Hypericum` oil fixation than to the inherited bog-myrtle guess"),
            ("Risk level", "moderate"),
            ("Direct confidence", "high on equilibrium fixation and liquid essence capture"),
        ],
        "pointer_judgment": "`f7v` is an equilibrium-crystallization page. It balances volatile and fixation forces exactly, proves the route through ten completion markers in nine lines, applies `dal.dol.dor`, and closes by fixing essence in liquid form.",
    },
    {
        "folio_id": "F008R",
        "folio_short": "F8r",
        "manuscript_role": "three-product formulary and labeled output page",
        "purpose": "`f8r` is the first fully explicit formulary sheet in the translated manuscript. Three distinct product paragraphs are each followed by a title line, and the first paragraph reintroduces `cfhodar`, the fire-seal vocabulary from `f1r`, on the same outer bifolio. The page reads less like a single extraction and more like a product board: three named outputs derived from one plant-source family, with the third route salted and vesselized at the close.",
        "reading_contract": [
            "The folio's structural uniqueness - three paragraph/title pairs - is treated as primary evidence for product labeling.",
            "Inherited species names remain weak; the page's formulary role is far stronger than any single botanical claim.",
            "Damaged glyphs remain visible where they affect line certainty, especially in the third paragraph.",
            "The strongest claim is process identity: one plant base, three labeled outputs, and an outer-bifolio fire-seal bookend with `f1r`.",
        ],
        "zero_claim": "take one plant source through three distinct product routes, label each output explicitly, and use the returning fire-seal of the outer bifolio to close Quire A's recto side as a formulary reference page.",
        "identity_rows": [
            ("Folio", "`f8r`"),
            ("Quire", "`A`"),
            ("Bifolio", "`bA1 = f1 + f8`"),
            ("Currier language", "`A`"),
            ("Currier hand", "`1`"),
            ("Illustration", "standard Herbal A plant with three interleaved title lines"),
            ("Botanical candidate", "inherited IDs split between `Pisum sativum` and `Borago officinalis`; operationally the page behaves as a carrier or formulary plant sheet"),
            ("Risk level", "moderate"),
            ("Direct confidence", "high on three-product formulary structure; low on exact species"),
        ],
        "visual_grammar": [
            "`three title lines` = the page openly names outputs rather than merely implying them",
            "`outer bifolio position` = the fire seal on `f1r` returns here as a structural bookend",
            "`paragraph segmentation` = the plant is treated as a source family with multiple product forms",
            "`title after paragraph` = label follows process, suggesting finished-output naming rather than chapter heading",
        ],
        "full_eva": dedent(
            """\
            P1.1:  pshol.chor.otshol.chopin.cphol.chodin.shy.cfhodar.shor-
            P1.2:  tchty.sh.kcheals.sho.okche.do.dchy.dain.al-
            P1.3:  chodar.shy.sy.chodaiin.shokchy.chor.dy-
            P1.4:  qotor.chor.chor.sheey.dchol.shesed.chof.chy.dam-
            P1.5:  okchey.do.r.cheeey.dy.ky.scho.chky.*ooaiin.chataiin-
            P1.6:  tosh.*cheey.kol.toldy.shy.choety.cheeody.sol-
            P1.7:  choto.kchoiin.choor.dain=
            T1.8:  ocho.dain=

            P2.9:  tchoep.sho.pcheey.pchey.ofchey.dsheey.shol.daiin.shor-
            P2.10: daiin.cheey.teeodan.dy.cheocthy.oksheo.dol.dairg-
            P2.11: shol.cheodaiin.daiin.do.ytchody.chot.choty.otariin-
            P2.12: qochodaiin.shotokody.chotol=
            T2.13: okokchodg=

            P3.14: *o.*ey.shol.chofydy.sho.chey.kshey.lody.cholal-
            P3.15: dchey.ckhol.chol.chey.kchs.chy.*daiin.dol.daiiinchy.ckhy-
            P3.16: ychey.kchokchy.chsey.kchy.s.cheaiin.cthaichar.cthy.dar-
            P3.17: chol.dey.qokar.chl.aiin.chean.*y.char.chaiin-
            P3.18: okar.cphaiin.chaiin.*l.daiin.chor.cha.rcheal.cham-
            P3.19: sair.cheain.cphol.dar.shol.kaiin.shol.daikam-
            P3.20: or.chokesey.shey.okal.chal=
            T3.21: schol.saim=
            """
        ).rstrip(),
        "core_vml": [
            "`cfhodar` = the furnace/fire-seal vocabulary of `f1r` returns on the same outer bifolio",
            "`T1/T2/T3` = product labels, not ordinary paragraph continuations",
            "`dam` in paragraph 1 = first product includes a chemical wedding marker",
            "`daiiinchy` in paragraph 3 = extended completion inside the most elaborate product path",
            "`sair` and `saim` = salt-earth rotation and salt completion in the third product family",
            "the page behaves as a source-to-products board rather than as a single extraction recipe",
        ],
        "groups": [
            {
                "label": "P1",
                "title": "Paragraph 1 and Title 1 - fire-sealed first product and wedding label",
                "line_ids": ["P1.1", "P1.2", "P1.3", "P1.4", "P1.5", "P1.6", "P1.7", "T1.8"],
            },
            {
                "label": "P2",
                "title": "Paragraph 2 and Title 2 - doubled-essence second product",
                "line_ids": ["P2.9", "P2.10", "P2.11", "P2.12", "T2.13"],
            },
            {
                "label": "P3",
                "title": "Paragraph 3 and Title 3 - salted third product and vessel close",
                "line_ids": ["P3.14", "P3.15", "P3.16", "P3.17", "P3.18", "P3.19", "P3.20", "T3.21"],
            },
        ],
        "lines": [
            ("P1.1", "pshol.chor.otshol.chopin.cphol.chodin.shy.cfhodar.shor", "`pshol` press-transition-fluid; `chor` volatile outlet; `otshol` timed transition fluid; `chopin` volatile-press completion; `cphol` pressed fluid; `chodin` volatile-heat completion; `shy` transition-active; `cfhodar` furnace-heat-fix-root; `shor` transition outlet.", "Open the first product by pressing transition fluid toward the outlet, complete the volatile press, and re-engage the outer-bifolio fire seal.", "open product one with the returning furnace-seal", "strong"),
            ("P1.2", "tchty.sh.kcheals.sho.okche.do.dchy.dain.al", "`tchty` driven volatile-active; `sh` transition cluster; `kcheals` contained volatile-essence-liquid-dissolve; `sho` transition-heat; `okche` heated contained volatile-essence; `do` fix-heat; `dchy` fixed volatile-active; `dain` completion; `al` structure.", "Drive the first product through contained volatile essence, apply transition heat, and complete the fixed structure.", "thicken and fix the first product body", "mixed"),
            ("P1.3", "chodar.shy.sy.chodaiin.shokchy.chor.dy", "`chodar` volatile-heat-fix-root; `shy` transition-active; `sy` dissolve-active; `chodaiin` volatile-heat completion; `shokchy` transition-heated containment-active; `chor` volatile outlet; `dy` fixed.", "Fix the first product at the root, dissolve through transition, and carry the heated contained volatile to a fixed outlet.", "stabilize product one as fixed heated output", "strong"),
            ("P1.4", "qotor.chor.chor.sheey.dchol.shesed.chof.chy.dam", "`qotor` circulated driven outlet-root; `chor.chor` doubled volatile outlet; `sheey` transition-double-essence-active; `dchol` fixed volatile fluid; `shesed` transition-essence-dissolve; `chof` volatile-heat-fire; `chy` volatile-active; `dam` union.", "Circulate the doubled outlet stream, push double essence through fixed volatile fluid, and land the first product in a chemical wedding.", "carry product one into union under doubled outlet law", "strong"),
            ("P1.5", "okchey.do.r.cheeey.dy.ky.scho.chky.*ooaiin.chataiin", "`okchey` heated contained volatile-essence-active; `do.r` fix-heat-root; `cheeey` volatile-triple-essence-active; `dy` fixed; `ky` contain-active; `scho` dissolve-volatile-heat; `chky` volatile-contain-active; `*ooaiin` damaged heated completion; `chataiin` volatile-driven-cycle-complete.", "Intensify the essence, keep the product fixed inside containment, preserve the damaged completion honestly, and finish the first output as a contained volatile cycle.", "push product one through its highest-essence passage", "mixed"),
            ("P1.6", "tosh.*cheey.kol.toldy.shy.choety.cheeody.sol", "`tosh` driven transition-heat; `*cheey` damaged volatile double-essence-active; `kol` contained fluid; `toldy` driven-fluid-fix-active; `shy` transition-active; `choety` volatile-heat-essence-active; `cheeody` volatile-double-essence-heat-fix-active; `sol` dissolve-fluid.", "Run one last damaged double-essence turn through contained fluid, then fix the volatile essence into dissolving liquid.", "liquefy and polish the first product before its label", "mixed"),
            ("P1.7", "choto.kchoiin.choor.dain", "`choto` volatile-driven-heat; `kchoiin` contained volatile completion; `choor` volatile-heat outlet-root; `dain` completion.", "Drive the first product to contained completion and certify the outlet-root route.", "close product one", "strong"),
            ("T1.8", "ocho.dain", "`ocho` heated volatile-heat label; `dain` completion.", "Label the first output as a completed heated volatile product.", "name the first finished product", "strong"),
            ("P2.9", "tchoep.sho.pcheey.pchey.ofchey.dsheey.shol.daiin.shor", "`tchoep` driven volatile-essence press; `sho` transition-heat; `pcheey` pressed volatile double-essence-active; `pchey` pressed volatile-essence-active; `ofchey` fire-volatile-essence-active; `dsheey` fixed transition-double-essence-active; `shol` transition fluid; `daiin` checkpoint; `shor` transition outlet.", "Open the second product with driven press-volatile essence, apply fire, and checkpoint the doubled transition before the outlet.", "restart as product two under press and fire assistance", "strong"),
            ("P2.10", "daiin.cheey.teeodan.dy.cheocthy.oksheo.dol.dairg", "`daiin` checkpoint; `cheey` volatile double-essence-active; `teeodan` driven-double-essence-heat-fix cycle; `dy` fixed; `cheocthy` volatile-essence-heat-conduit-bind; `oksheo` heated contained transition-essence; `dol` fix-fluid; `dairg` fix-rotation-growth.", "Checkpoint the second product, fix its doubled essence through the conduit, and rotate the fluid toward a growth-bearing finish.", "bind and rotate the second product through the conduit", "strong"),
            ("P2.11", "shol.cheodaiin.daiin.do.ytchody.chot.choty.otariin", "`shol` transition fluid; `cheodaiin` volatile-essence-heat completion; `daiin` checkpoint; `do` fix-heat; `ytchody` moist-driven volatile-heat-fix-active; `chot` volatile-driven heat; `choty` volatile-driven-active; `otariin` timed-root cycle-complete.", "Hold the second product in transition fluid, verify heated volatile essence, and drive the moist active route to a timed root completion.", "carry product two to timed root completion", "strong"),
            ("P2.12", "qochodaiin.shotokody.chotol", "`qochodaiin` circulated volatile-heat completion; `shotokody` transition-driven-heated-fix-active; `chotol` volatile-driven fluid.", "Close the second product as a circulated heated volatile completion with a fixed active fluid body.", "seal product two", "strong"),
            ("T2.13", "okokchodg", "`okokchodg` heated-contained-heated-contained-volatile-fix-growth label.", "Label the second output as a doubled heated contained volatile-growth product.", "name the second finished product", "strong"),
            ("P3.14", "*o.*ey.shol.chofydy.sho.chey.kshey.lody.cholal", "`*o.*ey` damaged heated essence opener; `shol` transition fluid; `chofydy` volatile-fire-active-fix; `sho` transition-heat; `chey` volatile-essence-active; `kshey` contained transition-essence-active; `lody` liquid-fix-active; `cholal` volatile-fluid-structure.", "Reopen the third product through a damaged heated essence cluster, fix the volatile-fire path, and establish a liquid structural body.", "open product three under damaged but workable fire-liquid conditions", "mixed"),
            ("P3.15", "dchey.ckhol.chol.chey.kchs.chy.*daiin.dol.daiiinchy.ckhy", "`dchey` fixed volatile-essence-active; `ckhol` valve fluid; `chol` volatile fluid; `chey` volatile-essence-active; `kchs` contained volatile-dissolve; `chy` volatile-active; `*daiin` damaged checkpoint; `dol` fix-fluid; `daiiinchy` extended completion with volatile-active tail; `ckhy` valve-active.", "Run the third product through valve and fluid law, keep the volatile essence active, preserve the damaged checkpoint, and extend completion under valve control.", "prove the third product through valve-governed repeated completion", "mixed"),
            ("P3.16", "ychey.kchokchy.chsey.kchy.s.cheaiin.cthaichar.cthy.dar", "`ychey` moist volatile-essence-active; `kchokchy` contained volatile-heat-contain-active; `chsey` volatile-dissolve-essence-active; `kchy` contained volatile-active; `s` dissolve; `cheaiin` volatile-essence completion; `cthaichar` conduit-bind-cycle-volatile-root; `cthy` conduit-bind-active; `dar` fix-root.", "Moisten the third product, keep it inside strict containment, carry volatile essence to completion through the conduit-root line, and fix it at the root.", "bind the third product to the root through conduit law", "strong"),
            ("P3.17", "chol.dey.qokar.chl.aiin.chean.*y.char.chaiin", "`chol` volatile fluid; `dey` fixed essence-active; `qokar` circulated contained outlet-root; `chl` volatile-liquid contraction; `aiin` completion; `chean` volatile-essence cycle; `*y` damaged active marker; `char` volatile-root; `chaiin` volatile cycle-complete.", "Circulate the third product's fluid and essence back to the root, preserve the damaged activity marker honestly, and keep the volatile-root cycle complete.", "recirculate the third product through root completion", "mixed"),
            ("P3.18", "okar.cphaiin.chaiin.*l.daiin.chor.cha.rcheal.cham", "`okar` heated contained outlet-root; `cphaiin` pressed cycle-complete; `chaiin` volatile cycle-complete; `*l` damaged fluid marker; `daiin` checkpoint; `chor` volatile outlet; `cha` volatile cycle; `rcheal` root-volatile-essence-liquid; `cham` union vessel.", "Keep the third product's outlet-root contained, run pressed and volatile completion, checkpoint the route, and enter the union vessel through a root-essence-liquid bridge.", "cross the checkpoint into the third product's union vessel", "mixed"),
            ("P3.19", "sair.cheain.cphol.dar.shol.kaiin.shol.daikam", "`sair` salt-earth-rotation; `cheain` volatile-essence completion; `cphol` pressed fluid; `dar` fix-root; `shol` transition fluid; `kaiin` contained completion; `shol` transition fluid; `daikam` fixed contained union.", "Add the salt-earth rotation, fix the root, and carry the third product into a contained union body.", "salt and vesselize the third product", "strong"),
            ("P3.20", "or.chokesey.shey.okal.chal", "`or` heat outlet; `chokesey` volatile-heat-contained-dissolve-essence-active; `shey` transition-essence-active; `okal` heated contained structure; `chal` volatile-structure.", "Heat the final outlet, keep volatile essence under contained dissolve, and stabilize the third product as a structured body.", "land the third product in structured closure", "strong"),
            ("T3.21", "schol.saim", "`schol` dissolve-volatile-fluid label; `saim` salt-cycle-complete label.", "Label the third output as the salted fluid completion.", "name the third finished product", "strong"),
        ],
        "tarot_cards": ["The Magician", "The Emperor", "Justice", "The Lovers", "Strength", "Temperance", "Judgment", "The Sun", "The Chariot", "The Hierophant", "Wheel of Fortune", "The World", "The Star", "The Moon", "The Hermit", "The Emperor", "Justice", "The Lovers", "Temperance", "The World", "The Sun"],
        "movements": ["ignite the first labeled product", "thicken the first product body", "stabilize the first product root", "marry the first product", "push the first product through essence gain", "liquefy the first product", "close the first product", "name the first output", "open the second product", "bind the second product in the conduit", "carry the second product to root completion", "seal the second product", "name the second output", "open the third product", "prove the third product through the valve", "bind the third product to root", "recirculate the third product", "enter the union vessel", "salt and vesselize the third product", "structure the final outlet", "name the third output"],
        "story_frames": ["product-one ignition", "product-one body build", "product-one stabilization", "product-one wedding", "product-one intensity beat", "product-one polish", "product-one close", "first label reveal", "product-two opening", "product-two conduit bind", "product-two root turn", "product-two seal", "second label reveal", "product-three damaged opening", "product-three valve test", "product-three root bind", "product-three recirculation", "product-three vessel crossing", "product-three salt turn", "product-three structural close", "third label reveal"],
        "hero_frames": ["call the first medicine into being", "give it a body", "fix it at its root", "bind it in union", "survive its intensification", "wash it into liquid form", "close the first labor", "receive the first name", "begin the second labor", "learn the conduit bind", "carry the root to completion", "seal the second labor", "receive the second name", "enter the damaged third road", "pass the valve test", "anchor the root line", "turn back through circulation", "cross into the vessel", "salt the body", "give it structure", "receive the third name"],
        "direct_operational_meaning": "`f8r` is not a normal single-folio herb page. It is a lookup board. The first route is fire-sealed and union-marked, the second route is doubled-essence and conduit-bound, and the third route is the most elaborate: valve-governed, root-bound, recirculated, salted, and finally labeled as a finished salt-fluid body. The return of `cfhodar` to the same outer bifolio as `f1r` makes the whole leaf behave like a frame closure: apparatus on the opening side, labeled outputs on the closing side.",
        "mathematical_extraction": "Across the formal math lenses, `f8r` is a branching product map. One source state is pushed through three different operator compositions, each terminating in a labeled output manifold. Product one optimizes fast fire-sealed union, product two optimizes conduit-bound doubled essence, and product three optimizes salt-bearing structured closure. The dominant invariant is not one terminal product but a controlled branching from one source into three named result classes.",
        "mythic_extraction": "Across the mythic lenses, `f8r` is the artisan's shelf. The work is no longer just ordeal or proof; it is classification after mastery. The hero makes three medicines, names them, and thereby turns process knowledge into transmissible inventory.",
        "all_lens_zero_point": "once the operator can survive the quire, one plant is no longer one procedure but a family of named outputs",
        "dense_compression": "Re-engage the fire seal, derive three distinct outputs from one plant source, and label each product openly, with the third route salted and vesselized at the close.",
        "typed_state_machine": dedent(
            """\
            \\[\\mathcal R_{f8r} = \\{r_{\\mathrm{source}}, r_{\\mathrm{product1}}, r_{\\mathrm{label1}}, r_{\\mathrm{product2}}, r_{\\mathrm{label2}}, r_{\\mathrm{product3}}, r_{\\mathrm{label3}}\\}\\]

            \\[\\mathcal E_\\Lambda = \\{e_{\\mathrm{fireseal}}, e_{\\mathrm{union}}, e_{\\mathrm{label}}, e_{\\mathrm{salt}}\\}\\]

            \\[\\delta(e_{\\mathrm{fireseal}}): r_{\\mathrm{source}} \\to r_{\\mathrm{product1}} \\to r_{\\mathrm{label1}}\\]

            \\[\\delta(e_{\\mathrm{label}}): r_{\\mathrm{label1}} \\to r_{\\mathrm{product2}} \\to r_{\\mathrm{label2}}\\]

            \\[\\delta(e_{\\mathrm{salt}}): r_{\\mathrm{label2}} \\to r_{\\mathrm{product3}} \\to r_{\\mathrm{label3}}\\]

            \\[\\rho_0 \\in \\mathcal H_{r_{\\mathrm{source}}}, \\qquad x_0^{\\mathrm{chem}} = \\begin{bmatrix} m_{\\mathrm{source}}^0 \\\\ m_{\\mathrm{volatile}}^0 \\\\ m_{\\mathrm{liquid}}^0 \\\\ 0 \\\\ 0 \\end{bmatrix}, \\qquad g_0 = \\mathrm{Coll}(\\rho_0)\\]
            """
        ).rstrip(),
        "invariants": dedent(
            """\
            \\[N_{\\mathrm{titles}}(f8r) = 3, \\qquad N_{\\mathrm{paragraphs}}(f8r) = 3, \\qquad N_{\\mathrm{fireseal}}(f8r) = 1\\]

            \\[N_{\\mathrm{union}}(f8r) = 1, \\qquad N_{\\mathrm{saltlabel}}(f8r) = 1, \\qquad N_{\\mathrm{extendedcompletion}}(f8r) = 1\\]

            \\[\\mathrm{Tr}(\\Pi_{\\mathrm{label1}} \\rho_*) + \\mathrm{Tr}(\\Pi_{\\mathrm{label2}} \\rho_*) + \\mathrm{Tr}(\\Pi_{\\mathrm{label3}} \\rho_*) > 0, \\qquad \\mathbf{1}^T x_*^{\\mathrm{chem}} = \\mathbf{1}^T x_0^{\\mathrm{chem}}\\]
            """
        ).rstrip(),
        "theorem": dedent(
            """\
            \\[\\rho_* = (\\Psi_{P3} \\circ \\Psi_{P2} \\circ \\Psi_{P1})(\\rho_0)\\]

            \\[\\forall \\rho_0 \\in \\mathcal H_{r_{\\mathrm{source}}} : \\bigl(N_{\\mathrm{titles}}=3 \\land N_{\\mathrm{fireseal}}=1\\bigr) \\Rightarrow \\rho_* \\in \\mathcal H_{r_{\\mathrm{label3}}}\\]

            \\[x_*^{\\mathrm{chem}} = x_{\\mathrm{label1}} \\oplus x_{\\mathrm{label2}} \\oplus x_{\\mathrm{label3}}, \\qquad x_{\\mathrm{label3}}^{\\mathrm{salt}} > 0\\]

            The formal theorem of `f8r` is therefore:

            1. one source plant is branched into three explicit product paths
            2. each product path receives its own terminal label
            3. the outer-bifolio fire seal returns in the first branch, linking the page back to `f1r`
            4. the third product lands as the strongest structured salt-bearing closure
            """
        ).rstrip(),
        "audit": ["EVA inventory complete for all 21 visible line-label units", "direct literal ledger present for each line and title", "16 formal math lenses populated with per-line equations", "4 mythic lenses populated with per-line readings", "key signatures preserved explicitly: `cfhodar`, three title lines, `dam`, `daiiinchy`, `sair`, and `saim`", "major unresolved issue preserved honestly: botanical identity remains much weaker than the page's obvious formulary structure"],
        "crystal_contribution": ["labeled formulary station", "three-product branching line", "outer-bifolio fire-seal return", "named-output inventory route", "salted third-product closure"],
        "pointer_title": "Three-Product Formulary",
        "pointer_position": "the `f1/f8` outer bifolio's recto closure, turning the opening apparatus page into a three-output reference sheet",
        "pointer_page_type": "single-plant illustrated formulary page with three title lines",
        "pointer_conclusion": "three explicit product routes, one returning fire-seal, and a final salted labeled output",
        "pointer_identity": [("Folio", "`f8r`"), ("Quire", "`A`"), ("Bifolio", "`bA1 = f1 + f8`"), ("Currier language", "`A`"), ("Currier hand", "`1`"), ("Illustration", "standard Herbal A with three separate title lines"), ("Botanical consensus", "species unresolved; operationally a three-output formulary plant"), ("Risk level", "moderate"), ("Direct confidence", "high on three-product labeled structure")],
        "pointer_judgment": "`f8r` is a formulary page. It splits one plant source into three distinct output paths, labels each product explicitly, and returns the `cfh-` fire-seal from `f1r` on the same outer bifolio.",
    },
    {
        "folio_id": "F008V",
        "folio_short": "F8v",
        "manuscript_role": "root-anchored triple-wash quire-closing healing page",
        "purpose": "`f8v` is the healing seal of Quire A. It is the last page of the quire, it repeats root fixation three times through `dar`, it uniquely triples `chol.chol.chol`, and it splits its work with a one-word section break `sorain` before closing on `dain.chear.daiin`. The page reads as a controlled root washing and final dressing route whose pedagogical role is as important as its chemistry: after the quire's dangers and instabilities, the manuscript closes on root-healing fixity.",
        "reading_contract": [
            "The codicological fact that this is the last page of Quire A is treated as semantically meaningful.",
            "The operational reading is stronger than the inherited species label, but comfrey remains one of the better plant matches because root-healing dominates both image and process.",
            "The one-word `sorain` line is preserved as a true section break, not flattened into surrounding prose.",
            "The strongest claim is process identity: root-anchored repeated wash and final dressing closure rather than volatile escalation.",
        ],
        "zero_claim": "work the root through repeated volatile-fluid washing, seal the first phase with `sorain`, then finish the medicine by re-binding volatile essence at the root so that the entire quire closes in healing fixation.",
        "identity_rows": [
            ("Folio", "`f8v`"),
            ("Quire", "`A`"),
            ("Bifolio", "`bA1 = f1 + f8`"),
            ("Currier language", "`A`"),
            ("Currier hand", "`1`"),
            ("Illustration", "root-weighted Herbal A plant and final page of Quire A"),
            ("Botanical candidate", "`Symphytum officinale` remains the strongest inherited match because the page is repeatedly root-anchored and healing-coded"),
            ("Risk level", "safe"),
            ("Direct confidence", "high on quire-closing root wash and final seal; moderate on exact species"),
        ],
        "visual_grammar": [
            "`last page of Quire A` = this folio carries closure load beyond its plant identity",
            "`root-heavy drawing` = the medicine is anchored at the root throughout the route",
            "`chol.chol.chol` = repeated wash is visually mirrored by repeated lexical identity",
            "`sorain` on a line by itself = a real phase boundary inside the page",
        ],
        "full_eva": dedent(
            """\
            P1:  *od.soo*.sol.shol.otol.chol.opcheaiin.opydaiin.saiin-
            P2:  shcthol.sar.chor.shoaiin.shor.chykchy.otaiin.ety-
            P3:  qody.cheal.sy.chor.chear.shol.chaiin.shaiin.dolar-
            P4:  *shol.shol.dol.chean.cthar.shey.daiin.chary-
            P5:  chol.chol.dar.otchar.otaiin.cthol.dar-
            P6:  daiin.cthan.ytchy.cheykaiin.dain.ar-
            P7:  sho.kchol.dar.shey.cthar.chotain.ry-
            P8:  okcholksh.chol.chol.chol.cthaiin.dain-
            P9:  shol.orchl.chokchy.chol.cthor.chaiin-
            P10: scharchy.oeesody.kchey.pchy.cpharom-
            P11: sorain=

            P12: pchar.cho.rol.dal.shear.chchotaiin.chal.daiin-
            P13: kchor.otchor.oky.chokain.keoky.otorchy.sytar-
            P14: shor.okol.lokoiin.shol.kol.char.cthey.tchy.ckham-
            P15: or.chol.chan.ch*y.chor.cheain.char.che*y.chor.ry-
            P16: chor.cheor.chear.oteey.dchor.chodey.cho.raiin-
            P17: dain.chear.daiin=
            """
        ).rstrip(),
        "core_vml": [
            "`chol.chol.chol` = the unique triple-wash marker in Quire A",
            "`dar` appears three times as repeated root fixation",
            "`cthar` returns the conduit-root apparatus vocabulary from the opening quire lessons",
            "`sorain` = one-word section break that seals the first phase",
            "`dain.chear.daiin` = double fixation bracketing volatile essence at the root",
            "the page closes as healing seal, not as danger escalation",
        ],
        "groups": [
            {"label": "P1", "title": "Paragraph 1 - root extraction, repeated wash, and section break", "line_ids": ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9", "P10", "P11"]},
            {"label": "P2", "title": "Paragraph 2 - final dressing route and quire-closing seal", "line_ids": ["P12", "P13", "P14", "P15", "P16", "P17"]},
        ],
        "lines": [
            ("P1", "*od.soo*.sol.shol.otol.chol.opcheaiin.opydaiin.saiin", "`*od` damaged fix-heat opener; `soo*` damaged dissolve cluster; `sol` dissolve-fluid; `shol` transition fluid; `otol` timed fluid; `chol` volatile fluid; `opcheaiin` heated-press volatile-essence completion; `opydaiin` heated-press-active completion; `saiin` salt cycle-complete.", "Open the root work by dissolving and pressing volatile essence into timed fluid, then land the first phase in salt-sealed completion.", "begin root extraction and salt-seal the first wash", "mixed"),
            ("P2", "shcthol.sar.chor.shoaiin.shor.chykchy.otaiin.ety", "`shcthol` transition-conduit-fluid; `sar` salt-root; `chor` volatile outlet; `shoaiin` transition-heat completion; `shor` transition outlet; `chykchy` volatile-active-contain-active; `otaiin` timed completion; `ety` essence-drive-active.", "Run the root fluid through the conduit, keep salt and outlet law together, and carry the active volatile to timed completion.", "establish conduit-root outlet law for the wash sequence", "strong"),
            ("P3", "qody.cheal.sy.chor.chear.shol.chaiin.shaiin.dolar", "`qody` circulated fix-active; `cheal` volatile-essence-structure; `sy` dissolve-active; `chor` volatile outlet; `chear` volatile-essence-root; `shol` transition fluid; `chaiin` volatile cycle-complete; `shaiin` transition completion; `dolar` fixed-fluid-root.", "Circulate the essence-root stream through transition fluid, complete both volatile and transition cycles, and root the liquid in fixation.", "root the moving essence inside the wash cycle", "strong"),
            ("P4", "*shol.shol.dol.chean.cthar.shey.daiin.chary", "`*shol.shol` damaged doubled transition-fluid cluster; `dol` fix-fluid; `chean` volatile-essence cycle; `cthar` conduit-heat-root; `shey` transition-essence-active; `daiin` checkpoint; `chary` volatile-root-active.", "Double the steeping fluid, fix the liquid, run the conduit-root check, and checkpoint the volatile root activity.", "double-steep and verify the root channel", "mixed"),
            ("P5", "chol.chol.dar.otchar.otaiin.cthol.dar", "`chol.chol` doubled volatile fluid; `dar` fix-root; `otchar` timed volatile-root; `otaiin` timed completion; `cthol` conduit fluid; `dar` fix-root again.", "Repeat the volatile-fluid wash, fix the root twice around a timed root pass, and keep the conduit fluid aligned.", "apply doubled wash with repeated root fixation", "strong"),
            ("P6", "daiin.cthan.ytchy.cheykaiin.dain.ar", "`daiin` checkpoint; `cthan` conduit-heat cycle; `ytchy` moist-driven volatile-active; `cheykaiin` volatile-essence-active-contained completion; `dain` completion; `ar` root.", "Checkpoint the conduit cycle, moisten the volatile stream, and complete another contained volatile-essence pass at the root.", "verify the moist conduit pass at the root", "strong"),
            ("P7", "sho.kchol.dar.shey.cthar.chotain.ry", "`sho` transition-heat; `kchol` contained volatile fluid; `dar` fix-root; `shey` transition-essence-active; `cthar` conduit-heat-root; `chotain` driven volatile completion; `ry` active-root.", "Return to transition heat, keep the volatile fluid contained, fix the root again, and drive the conduit-root line to completion.", "restate the root anchor before the triple wash", "strong"),
            ("P8", "okcholksh.chol.chol.chol.cthaiin.dain", "`okcholksh` heated contained volatile-fluid-contain cluster; `chol.chol.chol` triple volatile fluid; `cthaiin` conduit-bind completion; `dain` completion.", "Execute the page's unique triple wash, hold the fluid in hot containment, and complete the conduit bind.", "run the unique triple-wash center of the folio", "strong"),
            ("P9", "shol.orchl.chokchy.chol.cthor.chaiin", "`shol` transition fluid; `orchl` heated-root-liquid; `chokchy` volatile-heat-contain-active; `chol` volatile fluid; `cthor` conduit outlet; `chaiin` volatile cycle-complete.", "Carry the washed root-liquid through contained volatile fluid and narrow it through the conduit outlet to completion.", "send the triple-washed liquid through the conduit throat", "strong"),
            ("P10", "scharchy.oeesody.kchey.pchy.cpharom", "`scharchy` dissolve-volatile-root-active; `oeesody` heated-double-essence-fix-active; `kchey` contained volatile-essence-active; `pchy` pressed volatile-active; `cpharom` pressed-root-vessel.", "Dissolve the volatile root, fix the double essence, and press the contained medicine toward the vessel form.", "prepare the washed root into a vessel-ready body", "mixed"),
            ("P11", "sorain", "`sorain` salt-heat-root-cycle-complete.", "Seal the first phase in a one-word salt-root completion and mark a real section break.", "close the wash phase and break the page in two", "strong"),
            ("P12", "pchar.cho.rol.dal.shear.chchotaiin.chal.daiin", "`pchar` pressed volatile-root; `cho` volatile-heat; `rol` root-fluid; `dal` fix-structure; `shear` transition-essence-root; `chchotaiin` doubled volatile-driven completion; `chal` volatile-structure; `daiin` checkpoint.", "Reopen with a pressed root stream, fix the structure, and checkpoint the doubled volatile completion as the final dressing begins.", "begin the final dressing route with structural fixation", "strong"),
            ("P13", "kchor.otchor.oky.chokain.keoky.otorchy.sytar", "`kchor` contained volatile outlet; `otchor` timed volatile outlet; `oky` heated contained-active; `chokain` volatile-heat-contained completion; `keoky` contained-essence-heated-active; `otorchy` timed-outlet-volatile-active; `sytar` dissolve-active-driven-root.", "Contain the outlet, keep the volatile timed and heated, and drive the rooted active stream onward under containment.", "narrow the outlet and keep the dressing stream alive", "strong"),
            ("P14", "shor.okol.lokoiin.shol.kol.char.cthey.tchy.ckham", "`shor` transition outlet; `okol` heated contained fluid; `lokoiin` liquid-contained completion; `shol` transition fluid; `kol` contained fluid; `char` volatile-root; `cthey` conduit-essence-active; `tchy` driven volatile-active; `ckham` valve-union.", "Lock the liquid cycle through transition fluid, carry volatile root through the conduit, and end the line in valve-governed union.", "bind the dressing route through liquid, conduit, and union", "strong"),
            ("P15", "or.chol.chan.ch*y.chor.cheain.char.che*y.chor.ry", "`or` heat outlet; `chol` volatile fluid; `chan` volatile cycle; `ch*y` damaged volatile-active cluster; `chor` volatile outlet; `cheain` volatile-essence completion; `char` volatile-root; `che*y` damaged volatile-essence-active cluster; `chor` outlet; `ry` active-root.", "Keep heat at the outlet, carry the volatile root through damaged but legible essence turns, and preserve root activity as the dressing nears closure.", "sustain the living root-essence route through damaged final channels", "mixed"),
            ("P16", "chor.cheor.chear.oteey.dchor.chodey.cho.raiin", "`chor` volatile outlet; `cheor` volatile-essence outlet; `chear` volatile-essence-root; `oteey` timed double-essence-active; `dchor` fixed volatile outlet; `chodey` volatile-heat-fix-essence-active; `cho` volatile-heat; `raiin` root completion.", "Bring volatile and essence to the outlet and the root at once, time the doubled essence, then fix the outlet and return the process to root completion.", "gather volatile essence at root and outlet together before the seal", "strong"),
            ("P17", "dain.chear.daiin", "`dain` completion; `chear` volatile-essence-root; `daiin` cycle-complete.", "Complete the page by fixing volatile essence at the root and certifying the whole route once more.", "close Quire A in root-anchored volatile-essence fixation", "strong"),
        ],
        "tarot_cards": ["Temperance", "The Chariot", "Justice", "The Hermit", "Strength", "The Hierophant", "The Emperor", "The Star", "Wheel of Fortune", "The Magician", "Judgment", "The Sun", "The Chariot", "The Lovers", "The Moon", "The World", "The Star"],
        "movements": ["open the root wash", "set conduit and salt law", "root the circulating essence", "double-steep and verify", "fix the root twice", "verify the moist conduit pass", "restate the root anchor", "run the triple wash", "narrow the washed liquid through the conduit", "press the root medicine toward vessel form", "mark the section break", "reopen the final dressing route", "narrow and contain the outlet", "bind liquid conduit and union", "carry the damaged final channels", "gather root essence for closure", "seal the quire"],
        "story_frames": ["root-wash opening", "salt-conduit setup", "rooted-circulation beat", "double-steep checkpoint", "double-root fixation", "moist conduit proof", "anchor restatement", "triple-wash climax", "conduit narrowing beat", "vessel-preparation turn", "section-break hinge", "final-dressing restart", "outlet-containment beat", "union-binding beat", "damaged-channel endurance", "essence-gathering close", "quire-seal ending"],
        "hero_frames": ["enter the healing wash", "learn the conduit law", "root the moving essence", "submit to repeated proof", "fix the root again", "pass the moist channel", "renew the anchor", "cross the triple wash", "narrow the living stream", "shape the vessel body", "cross the boundary stone", "begin the final dressing", "guard the outlet", "bind the union", "carry the wounded route", "gather the essence home", "seal the journey"],
        "direct_operational_meaning": "The first phase of `f8v` is a root washing and rooting route. It opens with dissolution and salt-sealed completion, uses conduit-root checks repeatedly, and reaches its center at `chol.chol.chol`, the unique triple wash of Quire A. The one-word `sorain` then clearly breaks the page. The second phase is a dressing and closure route: press the root, re-bind structure, narrow the outlet, enter union, and then finish on `dain.chear.daiin`. The last translated line of Quire A is therefore not danger but healed fixity at the root.",
        "mathematical_extraction": "Across the formal math lenses, `f8v` is a two-phase boundary-value problem. Phase one reduces impurity by repeated liquid application while preserving root anchoring. `sorain` acts as a discrete boundary operator that changes the governing regime. Phase two then takes the washed root state and maps it into structured dressing closure. The dominant invariants are repeated root fixation, one explicit phase boundary, and a final state where essence is retained at the root rather than at a free outlet.",
        "mythic_extraction": "Across the mythic lenses, `f8v` is the healing seal. The apprentice leaves the quire not with a weapon or a storm but with a root dressing that closes the wound. The page's myth is closure, return, and binding back together.",
        "all_lens_zero_point": "the quire closes by washing the root repeatedly, breaking the work in two with salt-root completion, and then fixing volatile essence back at the root as healing closure",
        "dense_compression": "Wash the root three times, seal the first phase with `sorain`, then re-bind the medicine through outlet, conduit, and union until the quire closes on `dain.chear.daiin`.",
        "typed_state_machine": dedent(
            """\
            \\[\\mathcal R_{f8v} = \\{r_{\\mathrm{rootwash}}, r_{\\mathrm{rootproof}}, r_{\\mathrm{triplewash}}, r_{\\mathrm{sectionbreak}}, r_{\\mathrm{dressing}}, r_{\\mathrm{union}}, r_{\\mathrm{quireseal}}\\}\\]

            \\[\\mathcal E_\\Lambda = \\{e_{\\mathrm{wash}}, e_{\\mathrm{triplewash}}, e_{\\mathrm{sorain}}, e_{\\mathrm{seal}}\\}\\]

            \\[\\delta(e_{\\mathrm{wash}}): r_{\\mathrm{rootwash}} \\to r_{\\mathrm{rootproof}}\\]

            \\[\\delta(e_{\\mathrm{triplewash}}): r_{\\mathrm{rootproof}} \\to r_{\\mathrm{triplewash}}\\]

            \\[\\delta(e_{\\mathrm{sorain}}): r_{\\mathrm{triplewash}} \\to r_{\\mathrm{sectionbreak}} \\to r_{\\mathrm{dressing}}\\]

            \\[\\delta(e_{\\mathrm{seal}}): r_{\\mathrm{dressing}} \\to r_{\\mathrm{union}} \\to r_{\\mathrm{quireseal}}\\]

            \\[\\rho_0 \\in \\mathcal H_{r_{\\mathrm{rootwash}}}, \\qquad x_0^{\\mathrm{chem}} = \\begin{bmatrix} m_{\\mathrm{source}}^0 \\\\ m_{\\mathrm{volatile}}^0 \\\\ m_{\\mathrm{liquid}}^0 \\\\ 0 \\\\ 0 \\end{bmatrix}, \\qquad g_0 = \\mathrm{Coll}(\\rho_0)\\]
            """
        ).rstrip(),
        "invariants": dedent(
            """\
            \\[N_{\\mathrm{dar}}(f8v) = 3, \\qquad N_{\\mathrm{triplewash}}(f8v) = 1, \\qquad N_{\\mathrm{sectionbreak}}(f8v) = 1\\]

            \\[N_{\\mathrm{cthar}}(f8v) = 2, \\qquad N_{\\mathrm{saiin/sorain}}(f8v) = 2, \\qquad N_{\\mathrm{finalseal}}(f8v) = 1\\]

            \\[\\mathrm{Tr}(\\Pi_{\\mathrm{quireseal}} \\rho_*) \\gg \\mathrm{Tr}(\\Pi_{\\mathrm{fail}} \\rho_*), \\qquad \\mathbf{1}^T x_*^{\\mathrm{chem}} = \\mathbf{1}^T x_0^{\\mathrm{chem}}\\]
            """
        ).rstrip(),
        "theorem": dedent(
            """\
            \\[\\rho_* = (\\Psi_{P2} \\circ \\Psi_{P1})(\\rho_0)\\]

            \\[\\forall \\rho_0 \\in \\mathcal H_{r_{\\mathrm{rootwash}}} : \\bigl(N_{\\mathrm{dar}}=3 \\land N_{\\mathrm{triplewash}}=1 \\land N_{\\mathrm{sectionbreak}}=1\\bigr) \\Rightarrow \\rho_* \\in \\mathcal H_{r_{\\mathrm{quireseal}}}\\]

            \\[x_*^{\\mathrm{chem}} = \\begin{bmatrix} m_{\\mathrm{source}}^* \\\\ m_{\\mathrm{volatile}}^* \\\\ m_{\\mathrm{liquid}}^* \\\\ m_{\\mathrm{essence}}^* \\\\ m_{\\mathrm{fixed}}^* \\end{bmatrix}, \\qquad m_{\\mathrm{fixed}}^* > 0, \\qquad m_{\\mathrm{essence}}^* > 0\\]

            The formal theorem of `f8v` is therefore:

            1. the root medicine is washed repeatedly without abandoning its root anchor
            2. `sorain` marks a true phase change from washing to dressing
            3. the second phase narrows outlet, conduit, and union into one bound route
            4. Quire A closes by fixing volatile essence back at the root
            """
        ).rstrip(),
        "audit": ["EVA inventory complete for all 17 visible lines", "direct literal ledger present for each line", "16 formal math lenses populated with per-line equations", "4 mythic lenses populated with per-line readings", "key signatures preserved explicitly: `chol.chol.chol`, `dar x 3`, `cthar`, `sorain`, and `dain.chear.daiin`", "major unresolved issue preserved honestly: species fit remains moderate, but the healing root-closure role is strong"],
        "crystal_contribution": ["quire-closing healing-seal station", "root-anchored triple-wash line", "section-break boundary operator", "final dressing and union route", "root-essence closure of Quire A"],
        "pointer_title": "Root-Anchored Triple-Wash Closure",
        "pointer_position": "the last page of Quire A and the healing closure of the `f1/f8` outer bifolio",
        "pointer_page_type": "single-plant illustrated procedure page and quire-closing seal",
        "pointer_conclusion": "root washing, triple volatile-fluid application, section break at `sorain`, and final `dain.chear.daiin` quire seal",
        "pointer_identity": [("Folio", "`f8v`"), ("Quire", "`A`"), ("Bifolio", "`bA1 = f1 + f8`"), ("Currier language", "`A`"), ("Currier hand", "`1`"), ("Illustration", "root-weighted Herbal A plant and last page of the quire"), ("Botanical consensus", "`Symphytum officinale` remains the strongest inherited match"), ("Risk level", "safe"), ("Direct confidence", "high on root-anchored quire-closing wash and seal")],
        "pointer_judgment": "`f8v` is the quire-closing healing page. It performs repeated root washing, centers on the unique `chol.chol.chol` triple wash, breaks phase at `sorain`, and seals Quire A on `dain.chear.daiin`.",
    },
]


def main() -> None:
    for folio in FOLIOS:
        (FOLIOS_DIR / f"{folio['folio_id']}_FINAL_DRAFT.md").write_text(render_folio(folio), encoding="utf-8")
        (FOLIOS_DIR / f"{folio['folio_id']}.md").write_text(render_pointer(folio), encoding="utf-8")


if __name__ == "__main__":
    main()
