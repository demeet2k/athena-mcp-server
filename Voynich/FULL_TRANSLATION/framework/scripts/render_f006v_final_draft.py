from __future__ import annotations

from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "folios" / "F006V_FINAL_DRAFT.md"

LINES = [
    (
        "P1",
        "koarysaroeeekar.qoad.shor.chapchy.s.chear.char.otchy",
        "`koarysaroeeekar` longest opening token in Quire A, a triple-anchored root containment-dissolution cycle; `qoad` driven extraction; `shor` transition-outlet; `chapchy` volatile-project-active; `s` dissolve; `chear` volatile-essence-root; `char` volatile-root; `otchy` heated volatile-active.",
        "Begin with triple-anchored root containment, drive the heated extract toward the outlet, dissolve and project the volatile root fraction, and keep the heated volatile active.",
        "open the page with triple-anchored root extraction under maximum care",
        "mixed",
    ),
    (
        "P2",
        "oees.chor.chckhy.qokchas.cheas.odaiiin.kchey.chor.chaiin",
        "`oees` essence-dissolve cluster; `chor` volatile-outlet; `chckhy` volatile-valve-active; `qokchas` extract-contain-valve-dissolve; `cheas` volatile-essence-dissolve; `odaiiin` heated completion; `kchey` contained volatile-essence-active; `chor` outlet; `chaiin` volatile cycle-complete.",
        "Bring essence to the volatile outlet, engage the valve, run the extractive valve-dissolve pass, complete the heated cycle, and keep volatile essence contained through completion.",
        "establish the outlet and valve law before deeper toxicity handling",
        "strong",
    ),
    (
        "P3",
        "qoeir.ckhy.chol.**eockhy.chekchoy.ckhy.okol.rychos",
        "`qoeir` transmuted essence stream; `ckhy` valve-active; `chol` volatile-fluid; `**eockhy` damaged high-valve cluster; `chekchoy` volatile-essence-contain-heat-active; `ckhy` valve again; `okol` heat-fluid; `rychos` rotating volatile-dissolve with witness variation.",
        "Transmute the essence through the valve, keep the material in volatile fluid, preserve the damaged high-valve cluster honestly, and continue the contained heated route through one more rotating dissolve.",
        "triple-check the toxic stream under repeated valve control",
        "mixed",
    ),
    (
        "P4",
        "yshckhy.ykchoy.s.iiirs.y.dajy.dchy.dey.okody.ytody",
        "`yshckhy` moist transition-valve-active; `ykchoy` moist-contain-heat-active; `s` dissolve; `iiirs` rare triple-rotation dissolve cluster; `y` moist-active; `dajy` earth-fix-active; `dchy` volatile-fix-active; `dey` essence-fix-active; `okody` contained heat-fix-active; `ytody` moist-driven heat-fix-active.",
        "Move moist transition through the valve, dissolve it into the rare rotating `iiirs` cycle, then apply earth-fix, volatile-fix, essence-fix, contained heat-fix, and moist heat-fix in one sustained sequence.",
        "execute the page's great fixation cascade after the valve storm",
        "strong",
    ),
    (
        "P5",
        "dain.**.chodam.dam.okor.oty.doldom",
        "`dain` completion marker; `**` damaged witness; `chodam` volatile-heat-union; `dam` union; `okor` contained outlet-root; `oty` timed-active; `doldom` fixed-fluid-fixed-vessel.",
        "Mark completion, preserve the damage honestly, run the double union, contain the outlet-root, keep the timed active state alive, and seal the product inside the vessel.",
        "close the first half in doubled union and permanent vessel seal",
        "strong",
    ),
    (
        "P6",
        "tchody.shocthol.chocthey.s",
        "`tchody` driven volatile-heat-fix-active; `shocthol` transition-conduit-fluid; `chocthey` volatile-heat-conduit-essence-active; `s` dissolve.",
        "Reopen the sealed product through a controlled conduit wash, keeping the volatile heat fixed while the essence moves through the throat.",
        "restart inside the sealed apparatus without losing containment",
        "mixed",
    ),
    (
        "P7",
        "ychos.ychol.daiin.cthol.dol",
        "`ychos` moist volatile-dissolve; `ychol` moist volatile-fluid; `daiin` checkpoint; `cthol` conduit-fluid; `dol` fix-fluid.",
        "Moisten and dissolve the volatile liquid, checkpoint the route, pass through the conduit fluid, and fix the liquid again.",
        "wash and re-fix the expressed liquid under conduit law",
        "strong",
    ),
    (
        "P8",
        "ychor.chor.okchey.qokom",
        "`ychor` moist volatile-outlet; `chor` volatile-outlet; `okchey` heat-contain-volatile-essence-active; `qokom` circulated contained vessel.",
        "Return to the outlet, hold volatile essence under heat-containment, and circulate the product inside the vessel.",
        "keep the outlet alive while contained essence circulates",
        "strong",
    ),
    (
        "P9",
        "oeeodal.chor.cthom.s",
        "`oeeodal` essence-structure-fix cluster; `chor` volatile-outlet; `cthom` conduit-heat-vessel; `s` dissolve.",
        "Structurally fix the essence stream at the outlet and dissolve it again through the conduit vessel.",
        "restructure the essence stream without opening the system",
        "mixed",
    ),
    (
        "P10",
        "qokchod.ychear.kchdy",
        "`qokchod` circulated contained volatile-heat-fix; `ychear` moist volatile-essence-root; `kchdy` contained volatile heat fixed.",
        "Drive the contained volatile heat-fix forward, moisten the essence-root fraction, and land in a controlled fixed volatile state.",
        "pull the toxic stream toward a safer contained fix-state",
        "strong",
    ),
    (
        "P11",
        "lorchar.otam.ctho.mdy",
        "`lorchar` liquid-outlet-volatile-root; `otam` timed union; `ctho` conduit-heat; `mdy` medicinal fixed output.",
        "Bring the liquid root fraction to timed union through the conduit heat and stabilize it into medicinal fixed output.",
        "convert the dangerous stream into usable medicine without dropping the conduit guard",
        "mixed",
    ),
    (
        "P12",
        "ytchos.shy.qokam.cthy",
        "`ytchos` moist volatile-dissolve; `shy` transition-active; `qokam` circulated contained union; `cthy` conduit-bind-active.",
        "Drive moist volatile dissolve through active transition, circulate the contained union, and keep the conduit bound.",
        "carry the medicated stream through another active union cycle",
        "strong",
    ),
    (
        "P13",
        "yodaiin.cthy.s.chor.oees.or",
        "`yodaiin` moist completion; `cthy` conduit-bind-active; `s` dissolve; `chor` volatile-outlet; `oees` essence-dissolve; `or` heat-outlet.",
        "Mark moist completion, maintain the conduit bind, dissolve again, reopen the volatile outlet, and return to a heated outlet state.",
        "checkpoint the reopened outlet without surrendering the bind",
        "strong",
    ),
    (
        "P14",
        "qokor.chol.cthol.tchalody",
        "`qokor` circulated contained outlet-root; `chol` volatile-fluid; `cthol` conduit-fluid; `tchalody` driven volatile-structure-heat-fix.",
        "Circulate the root outlet through volatile fluid and conduit fluid and drive it into a structural heat-fix terminal.",
        "route the toxic liquid into a structural fixed body",
        "mixed",
    ),
    (
        "P15",
        "chockhy.s.or.chy.sain.or",
        "`chockhy` volatile-heat-valve-active; `s` dissolve; `or` heat-outlet; `chy` volatile-active; `sain` completion marker; `or` heat-outlet.",
        "Run another valve dissolve, reopen heat at the outlet, keep the volatile active, and pass through one more completion outlet.",
        "repeat the valve discipline even after apparent stabilization",
        "mixed",
    ),
    (
        "P16",
        "ochy.cthar.cthor.cthy",
        "`ochy` heat-volatile-active; `cthar` conduit-heat-root; `cthor` conduit-outlet; `cthy` conduit-bind-active.",
        "Return the page to full apparatus law: active volatile, root conduit, outlet conduit, and final bind all aligned at once.",
        "restate the apparatus contract before the carrier close",
        "strong",
    ),
    (
        "P17",
        "y.chaiir.ckhal.cthodam.dy",
        "`y` moist-active; `chaiir` volatile cycle-complete; `ckhal` castor-oil bridge token; `cthodam` conduit-heat-fix-union; `dy` fixed.",
        "Complete the active volatile cycle, invoke the `ckhal` carrier token, bind the heated union in the conduit, and reach a fixed usable carrier state.",
        "reveal the castor-oil carrier bridge and secure a fixed union",
        "strong",
    ),
    (
        "P18",
        "ytchocthol.ches.cthor",
        "`ytchocthol` moist-driven volatile-heat-conduit-fluid; `ches` volatile-essence-dissolve; `cthor` conduit-outlet.",
        "Drive moist volatile heat through conduit fluid, carry volatile essence in dissolve mode, and keep the outlet narrow.",
        "send the carrier through one more narrowed conduit passage",
        "strong",
    ),
    (
        "P19",
        "ocholykchos.chy.dor",
        "`ocholykchos` heated volatile-fluid moist containment-dissolve cluster; `chy` volatile-active; `dor` fixed outlet-root.",
        "Keep the volatile fluid heated, moist, contained, and dissolving, preserve active volatile, and root the outlet in fixation.",
        "hold the near-final liquid in active but rooted control",
        "mixed",
    ),
    (
        "P20",
        "dchor.choldar.okol.daiin",
        "`dchor` fixed volatile-outlet; `choldar` volatile-fluid-fix-root; `okol` heated fluid; `daiin` completion marker.",
        "Fix the volatile outlet, root the volatile fluid, keep the product heated in liquid form, and checkpoint the result.",
        "root the fixed liquid before the final vessel closure",
        "strong",
    ),
    (
        "P21",
        "ycheor.chor.octham",
        "`ycheor` moist volatile-essence-outlet; `chor` volatile-outlet; `octham` heated conduit vessel.",
        "End with moist volatile essence at the outlet and close the product inside the heated conduit vessel.",
        "seal the carrier in its final vessel",
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
        "Justice",
        "The Moon",
        "Strength",
        "The World",
        "Temperance",
        "The Hermit",
        "Wheel of Fortune",
        "The Star",
        "Judgment",
        "The Hierophant",
        "The Chariot",
        "Justice",
        "The Emperor",
        "The Hermit",
        "The Magician",
        "The Sun",
        "Temperance",
        "Strength",
        "Judgment",
        "The World",
    ],
    "Juggling": [
        "set the toxic seed bundle",
        "tighten the first valve check",
        "survive the damaged valve cluster",
        "run the great fixation cascade",
        "seal the first vessel",
        "reopen the wash throat",
        "wash and re-fix the oil",
        "circulate the contained essence",
        "restructure the stream",
        "pull toward safe fix",
        "turn danger into medicine",
        "carry the union onward",
        "reopen under checkpoint",
        "drive the structural fix",
        "repeat the safety drill",
        "restate the apparatus",
        "reveal the carrier token",
        "narrow the outlet again",
        "hold the live liquid",
        "root the fixed product",
        "seal the last vessel",
    ],
    "Story Writing": [
        "triple-anchor opening",
        "valve-law establishment",
        "damaged-control escalation",
        "fixation cascade climax",
        "sealed midpoint close",
        "controlled restart beat",
        "washed-oil proof",
        "contained-circulation beat",
        "restructuring passage",
        "safe-fix turn",
        "medicine conversion beat",
        "continued union",
        "checkpointed reopening",
        "structural terminal drive",
        "repeated discipline beat",
        "apparatus reprise",
        "carrier reveal",
        "narrow-channel aftermath",
        "held-liquid suspense",
        "root-fix resolution",
        "sealed ending",
    ],
    "Hero's Journey": [
        "enter the toxic root gate",
        "accept the valve law",
        "cross the damaged checkpoint",
        "survive the fixation trial",
        "seal the first boon",
        "re-enter the vessel",
        "purify the oil path",
        "learn contained circulation",
        "reshape the essence stream",
        "approach safe fix",
        "transform poison into medicine",
        "carry the union onward",
        "pass the renewed proof",
        "give the body structure",
        "repeat discipline willingly",
        "remember the apparatus law",
        "take up the carrier gift",
        "thread the narrow passage",
        "hold the living liquid",
        "root the final medicine",
        "return with the sealed vessel",
    ],
}

MOVEMENTS = [
    "anchor the root extraction",
    "lock the valve law",
    "survive the damaged cluster",
    "run the fixation cascade",
    "seal the first vessel",
    "reopen inside the conduit",
    "wash and re-fix the oil",
    "circulate the contained essence",
    "restructure the stream",
    "pull toward controlled fix",
    "turn toxicity into medicine",
    "continue the union",
    "reopen with proof",
    "drive the structural terminal",
    "repeat the safety drill",
    "restate the apparatus",
    "reveal the carrier token",
    "narrow the outlet",
    "hold the live liquid",
    "root the fixed product",
    "seal the final vessel",
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
    out = ["### Paragraph 1 - triple-anchor opening, valve storm, and first vessel seal", ""]
    for line_id, eva, literal, operational, *_ in LINES[:5]:
        out += [f"- `{line_id}`", f"  EVA: `{eva}`", f"  Literal chain: {literal}", f"  Operational English: {operational}", ""]
    out += ["### Paragraph 2 - conduit restart, washing, circulation, and medicine conversion", ""]
    for line_id, eva, literal, operational, *_ in LINES[5:11]:
        out += [f"- `{line_id}`", f"  EVA: `{eva}`", f"  Literal chain: {literal}", f"  Operational English: {operational}", ""]
    out += ["### Paragraph 3 - continued union, structural fixing, and apparatus reprise", ""]
    for line_id, eva, literal, operational, *_ in LINES[11:16]:
        out += [f"- `{line_id}`", f"  EVA: `{eva}`", f"  Literal chain: {literal}", f"  Operational English: {operational}", ""]
    out += ["### Paragraph 4 - carrier reveal, narrowed conduit, rooted fix, and final vessel", ""]
    for line_id, eva, literal, operational, *_ in LINES[16:]:
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
        f"""# F006V Final Draft - Dense Multilens Translation Atlas

## Final Draft Status

- Status: `authoritative final-draft folio`
- Manuscript role: `maximum-security toxic extraction / castor carrier page`
- Book: `Book I - Herbal / materia medica`
- Production standard: `framework-governed dense folio with full symbolic matrix`
- Source baseline: `F006V.md`

## Purpose

`f6v` is the longest verso in early Quire A and reads like a maximum-security toxic separation protocol. Its signatures are the gigantic opening token `koarysaroeeekar`, the highest valve density in Quire A, the rare `iiirs` rotational dissolve, the first major vessel seal `doldom`, and the later bridge token `ckhal` that marks castor-oil carrier logic. The page handles poison in order to produce a safe vehicle.

## Source Stack

- `NEW/SECTION I - BOOK I_ THE HERBAL _ MATERIA MEDICA.md`
- `NEW/working/VML_RECIPE_CROSSREF.md`
- `NEW/working/VML_CONSISTENCY_PROOF.md`
- `NEW/working/VML_RIGOROUS_RETRANSCRIPTION_QUIRES_ABCDEFG.md`
- `eva/EVA TRANSCRIPTION ORIGIONAL.txt`

## Reading Contract

- preserve damaged clusters honestly
- preserve the long-form line inventory; length is part of the meaning
- keep toxic handling distinct from final medicinal carrier output

## Folio Zero Claim

`f6v` means: extract the useful carrier from an extremely toxic source by locking every pathway under valve law, repeatedly fixing and filtering the product, sealing it, reopening it under control, and only then releasing a usable oil-like medicine.

## Folio Identity

| Field | Value |
| --- | --- |
| Folio | `f6v` |
| Quire | `A` |
| Bifolio | `bA3 = f3 + f6` |
| Currier language | `A` |
| Currier hand | `1` |
| Illustration | single Herbal A plant with long text field |
| Botanical consensus | `Ricinus communis` operationally favored as castor-oil separation |
| Risk level | lethal source / medicinal carrier goal |
| Direct confidence | high on valve-sealed toxic extraction, moderate-high on castor-oil carrier reading |

## Visual Grammar and Codicology

- unusually long text block = elaborate precaution procedure
- standard plant body with no dramatic flourish = toxicity is managed by protocol, not imagery
- paired with `f6r` = binding on recto, maximum-security separation on verso

## Full EVA

```text
P1:  koarysaroeeekar.qoad.shor.chapchy.s.chear.char.otchy-
P2:  oees.chor.chckhy.qokchas.cheas.odaiiin.kchey.chor.chaiin-
P3:  qoeir.ckhy.chol.**eockhy.chekchoy.ckhy.okol.rychos-
P4:  yshckhy.ykchoy.s.iiirs.y.dajy.dchy.dey.okody.ytody-
P5:  dain.**.chodam.dam.okor.oty.doldom=
P6:  tchody.shocthol.chocthey.s-
P7:  ychos.ychol.daiin.cthol.dol-
P8:  ychor.chor.okchey.qokom-
P9:  oeeodal.chor.cthom.s-
P10: qokchod.ychear.kchdy-
P11: lorchar.otam.ctho.mdy-
P12: ytchos.shy.qokam.cthy-
P13: yodaiin.cthy.s.chor.oees.or-
P14: qokor.chol.cthol.tchalody-
P15: chockhy.s.or.chy.sain.or-
P16: ochy.cthar.cthor.cthy-
P17: y.chaiir.ckhal.cthodam.dy-
P18: ytchocthol.ches.cthor-
P19: ocholykchos.chy.dor-
P20: dchor.choldar.okol.daiin-
P21: ycheor.chor.octham=
```

## Core VML Machinery Active On F6v

- `koarysaroeeekar` = triple-anchored root extraction under containment
- `ckh-` maximum = every flow path is valve-disciplined
- `iiirs` = rare rotational dissolve inside the toxic-control regime
- `doldom` = first strong vessel seal
- `cthar.cthor` = apparatus vocabulary returns explicitly
- `ckhal` = castor-oil carrier bridge token
- `octham` = final heated conduit vessel closure

## Direct Line-By-Line Literal Ledger

{ledger}

## Multilens Translation Atlas

{formal}

{mythic}

## Direct Operational Meaning

Paragraph 1 opens under triple-anchored root extraction, then immediately tightens into valve law and the great fixation cascade before sealing the first vessel with `doldom`. Paragraph 2 restarts the sealed product inside a conduit wash, proves that the liquid can be washed, circulated, and turned toward medicinal output without losing control, and keeps the toxic stream narrowed at every step. Paragraph 3 continues the union and structural fixing, then restates the apparatus vocabulary before the carrier reveal. Paragraph 4 gives that reveal directly: `ckhal`, a fixed union, narrowed conduit work, rooted liquid fixation, and final vessel closure. The page reads like castor-oil separation from lethal seed matter, where the useful oil is only lawful if every opening is disciplined.

## Mathematical Extraction

Across the formal math lenses, `f6v` is a maximum-security flow network. The state trajectory is dominated by boundary control, repeated fixation, and vessel sealing. The critical invariant is selective release: useful carrier mass increases only while toxic contamination remains below the admissible boundary budget enforced by the valve stack.

## Mythic Extraction

Across the mythic lenses, `f6v` is poison domesticated into service. The operator does not conquer toxicity by force alone, but by never leaving a path ungoverned.

## All-Lens Zero Point

`f6v` means: the safest medicine may come from the most dangerous source, but only if every channel is narrower than the poison's will to spread.

## Dense One-Sentence Compression

Lock the toxic root stream under maximum valve law, fix and filter it through repeated seals and washes, then reveal the castor carrier only after the liquid can survive the narrowed conduit without contaminating itself.

## Formal Mathematical Overlay For F6v

### Imported Kernel Equations

\\[\\mathcal H := L^2(\\widehat{{\\mathbb C}}, \\mu), \\qquad \\rho \\in \\mathcal T_1(\\mathcal H), \\qquad \\rho \\succeq 0, \\qquad \\mathrm{{Tr}}(\\rho)=1\\]

\\[\\mathcal H_{{\\mathrm{{tot}}}} = \\left(\\bigoplus_r \\mathcal H_r\\right) \\oplus \\left(\\bigoplus_e \\mathcal H_{{\\Lambda_e}}\\right) \\oplus \\mathcal H_{{\\mathrm{{fail}}}}\\]

\\[x_{{n+1}}^{{\\mathrm{{chem}}}} = K_n x_n^{{\\mathrm{{chem}}}}, \\qquad \\mathbf{{1}}^T K_n = \\mathbf{{1}}^T\\]

\\[g = \\mathrm{{Coll}}(X), \\qquad X = \\mathrm{{Expand}}(g) \\oplus r\\]

### Typed State Machine

\\[\\mathcal R_{{f6v}} = \\{{r_{{\\mathrm{{tripleanchor}}}}, r_{{\\mathrm{{valvemax}}}}, r_{{\\mathrm{{fixcascade}}}}, r_{{\\mathrm{{vesselseal}}}}, r_{{\\mathrm{{conduitwash}}}}, r_{{\\mathrm{{medicine}}}}, r_{{\\mathrm{{carrierbridge}}}}, r_{{\\mathrm{{terminalseal}}}}\\}}\\]

\\[\\delta(e_{{\\mathrm{{anchor}}}}): r_{{\\mathrm{{tripleanchor}}}} \\to r_{{\\mathrm{{valvemax}}}}, \\qquad \\delta(e_{{\\mathrm{{fix}}}}): r_{{\\mathrm{{valvemax}}}} \\to r_{{\\mathrm{{fixcascade}}}} \\to r_{{\\mathrm{{vesselseal}}}}\\]

\\[\\delta(e_{{\\mathrm{{wash}}}}): r_{{\\mathrm{{vesselseal}}}} \\to r_{{\\mathrm{{conduitwash}}}} \\to r_{{\\mathrm{{medicine}}}}, \\qquad \\delta(e_{{\\mathrm{{bridge}}}}): r_{{\\mathrm{{medicine}}}} \\to r_{{\\mathrm{{carrierbridge}}}} \\to r_{{\\mathrm{{terminalseal}}}}\\]

\\[\\rho_0 \\in \\mathcal H_{{r_{{\\mathrm{{tripleanchor}}}}}}, \\qquad x_0^{{\\mathrm{{chem}}}} = \\begin{{bmatrix}} m_{{\\mathrm{{toxic\\_source}}}}^0 \\\\ m_{{\\mathrm{{volatile}}}}^0 \\\\ m_{{\\mathrm{{liquid}}}}^0 \\\\ 0 \\\\ 0 \\end{{bmatrix}}\\]

### Canonical AQM Line Operators

{ops}

### Paragraph Compositions

\\[\\Psi_{{A}} = \\Phi_{{\\mathrm{{P5}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P4}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P3}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P2}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P1}}}}^{{\\mathrm{{AQM}}}}\\]

\\[\\Psi_{{B}} = \\Phi_{{\\mathrm{{P11}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P10}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P9}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P8}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P7}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P6}}}}^{{\\mathrm{{AQM}}}}\\]

\\[\\Psi_{{C}} = \\Phi_{{\\mathrm{{P16}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P15}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P14}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P13}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P12}}}}^{{\\mathrm{{AQM}}}}\\]

\\[\\Psi_{{D}} = \\Phi_{{\\mathrm{{P21}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P20}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P19}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P18}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P17}}}}^{{\\mathrm{{AQM}}}}\\]

\\[\\rho_* = (\\Psi_{{D}} \\circ \\Psi_{{C}} \\circ \\Psi_{{B}} \\circ \\Psi_{{A}})(\\rho_0)\\]

### Invariants And Counts

\\[N_{{\\mathrm{{ckh}}}}(f6v) = 7, \\qquad N_{{\\mathrm{{cth}}}}(f6v) = 8, \\qquad N_{{\\mathrm{{dy}}}}(f6v) = 7\\]

\\[N_{{\\mathrm{{union}}}}(f6v) = 3, \\qquad N_{{\\mathrm{{seal}}}}(f6v) = 2, \\qquad N_{{\\mathrm{{carrier}}}}(f6v) = 1\\]

### Cross-Lens Transport

\\[\\Phi_j^{{(\\lambda)}} = T_\\lambda^{{-1}} \\Phi_j^{{(\\mathrm{{AQM}})}} T_\\lambda, \\qquad \\lambda \\in \\{{\\mathrm{{CUT}}, \\mathrm{{phys}}, \\mathrm{{wave}}, \\mathrm{{wavemath}}\\}}\\]

### Folio Theorem

\\[\\forall \\rho_0 \\in \\mathcal H_{{r_{{\\mathrm{{tripleanchor}}}}}} : \\bigl(N_{{\\mathrm{{ckh}}}}=7 \\land N_{{\\mathrm{{seal}}}}=2 \\land N_{{\\mathrm{{carrier}}}}=1\\bigr) \\Rightarrow \\rho_* \\in \\mathcal H_{{r_{{\\mathrm{{terminalseal}}}}}}\\]

The formal theorem of `f6v` is therefore:

1. the page opens by triple-anchoring the toxic root stream
2. maximum valve control and fixation cascades make the first vessel seal possible
3. the sealed product is restarted and converted toward medicine without losing conduit discipline
4. `ckhal` reveals the carrier bridge
5. the carrier is released only as a final vessel-sealed product

## Final Draft Audit

- EVA inventory complete for all 21 visible lines
- direct literal ledger present for each line
- 16 formal math lenses populated with per-line equations
- 4 mythic lenses populated with per-line readings
- key signatures preserved explicitly: `koarysaroeeekar`, valve maximum, `iiirs`, `doldom`, `ckhal`, and `octham`

## Plant Crystal Contribution

- maximum-security toxic extraction station
- valve-maximum line
- vessel-seal carrier route
- `ckhal` bridge line
- castor-oil separation page
"""
    ).rstrip() + "\n"


def main() -> None:
    OUTPUT.write_text(render(), encoding="utf-8")


if __name__ == "__main__":
    main()
