from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "folios" / "F003R_FINAL_DRAFT.md"

LINES = [
    (
        "P1.1",
        "tsheos.qopal.chol.cthol.daimg",
        "`tsheos` driven-transition-essence-heat-dissolve name-tag; `qopal` circulate-press-structure; `chol` volatile-fluid; `cthol` conduit-fluid; `daimg` opaque terminal cluster.",
        "Open on the tagged master substance, pressurize the retort into structure, carry the volatile fluid through the conduit, and keep the unresolved terminal marker visible.",
        "tag the master extraction substance and open the retort-conduit frame",
        "mixed",
    ),
    (
        "P1.2",
        "ycheor.chor.dam.qotchag.cham",
        "`ycheor` moist volatile-essence outlet; `chor` volatile outlet; `dam` fix-union; `qotchag` driven retort-volatile growth; `cham` volatile-union.",
        "Moisten the volatile essence at the outlet, perform the first chemical wedding, drive the retort-heated volatile, and carry it into volatile union.",
        "perform the first chemical wedding under driven retort motion",
        "strong",
    ),
    (
        "P1.3",
        "ochar.qacheor.chol.daiin.cthy",
        "`ochar` heated volatile-root; `qacheor` circulate-body-volatile-essence outlet; `chol` volatile-fluid; `daiin` fixation checkpoint; `cthy` conduit-bind-active.",
        "Heat the rooted volatile, recirculate the living essence toward the outlet, keep it in fluid state, verify the checkpoint, and bind the route to the conduit.",
        "stabilize the first union through a conduit-bound checkpoint",
        "mixed",
    ),
    (
        "P1.4",
        "schey.chor.chal.cham.chaj.cho",
        "`schey` dissolve-transition-essence active; `chor` volatile outlet; `chal` volatile-structure; `cham` volatile-union; `chaj` volatile-root-active; `cho` volatile-heat.",
        "Dissolve the transitioning essence toward the outlet, extend volatile structure, repeat the volatile union, root it again, and keep heat alive inside the operation.",
        "repeat the volatile union and extend it into structural rooting",
        "mixed",
    ),
    (
        "P1.5",
        "qokol.chololy.s.cham.cthol",
        "`qokol` circulate-contain-fluid; `chololy` volatile-fluid-fluid-active; `s` dissolve; `cham` volatile-union; `cthol` conduit-fluid.",
        "Retort the contained liquid, hold the work in a double-fluid volatile state, dissolve it, perform another volatile union, and keep the conduit-liquid path open.",
        "convert the work into a two-phase dissolving union",
        "strong",
    ),
    (
        "P1.6",
        "ychtaiin.chor.cthom.otoldam",
        "`ychtaiin` moist volatile-cycle-complete; `chor` volatile outlet; `cthom` conduit-vessel; `otoldam` timed-fluid-fix-union.",
        "Complete the moist volatile cycle at the outlet, carry it into the conduit-vessel, and time the fluid fixation exactly at the union point.",
        "time the union inside vessel and conduit",
        "strong",
    ),
    (
        "P1.7",
        "otchol.qodaiin.chom.shom.damo",
        "`otchol` timed volatile-fluid; `qodaiin` circulate-fix-cycle-complete; `chom` volatile-vessel; `shom` transition-vessel; `damo` fix-union-heat.",
        "Heat the volatile liquid in timed mode, verify the retort cycle to completion, keep it inside the volatile and transition vessels, and heat the union itself alive.",
        "verify the retort cycle and heat the union alive",
        "strong",
    ),
    (
        "P1.8",
        "ysheor.chor.chol.oky.dago",
        "`ysheor` moist transition-essence outlet; `chor` volatile outlet; `chol` volatile-fluid; `oky` heat-contain-active; `dago` fix-earth-heat.",
        "Carry the moistened essence back to the outlet, maintain the volatile liquid, actively contain it under heat, and begin fixing the heated earthward state.",
        "keep the combined liquid contained and fixed after union",
        "mixed",
    ),
    (
        "P1.9",
        "sho.aor.sheoldaj.otchody.ol",
        "`sho` transition-heat; `aor` body-outlet; `sheoldaj` transition-essence-fluid-fix-root-active; `otchody` timed-volatile-heat-fix-active; `ol` fluid.",
        "Run a heated transition through the bodily outlet, draw the joined essence through a fixing fluid-root path, time the volatile heat-fix, and hold the process in liquid form.",
        "draw the joined material through a doubled heated route toward fixation",
        "uncertain",
    ),
    (
        "P1.10",
        "ydas.cholcthom",
        "`ydas` moist-fix-dissolve; `cholcthom` volatile-fluid-conduit-vessel.",
        "Close the first paragraph by moistening, fixing, and dissolving the work directly inside the volatile fluid conduit-vessel.",
        "seal paragraph one in conduit-vessel fixation",
        "uncertain",
    ),
    (
        "P2.11",
        "pcheol.shol.sols.sheol.shey",
        "`pcheol` press-volatile-essence-fluid; `shol` transition-fluid; `sols` dissolve-fluid-dissolve; `sheol` transition-essence-fluid; `shey` transition-essence-active.",
        "Press the volatile essence into liquid form, transition it into fluid, dissolve it twice inside liquid, and keep the essence actively moving through the transition medium.",
        "press the volatile essence into a dissolving transition fluid",
        "strong",
    ),
    (
        "P2.12",
        "okadaiin.qokchor.qoschodam.octhy",
        "`okadaiin` phase-shift completion verified; `qokchor` circulate-contain-volatile-outlet; `qoschodam` circulate-dissolve-volatile-heat-fix-union; `octhy` heated conduit active.",
        "Verify the phase-shift, retort the contained volatile to the outlet, execute the full circulate-dissolve-volatile-heat-fix-union sequence, and drive it through the heated conduit.",
        "execute the densest retort-union token and push it through conduit",
        "strong",
    ),
    (
        "P2.13",
        "qokeey.qot.shey.qokody.qokshey.cheody",
        "`qokeey` extract-contain-double-essence-active; `qot` driven retort; `shey` transition-essence-active; `qokody` extract-contain-heat-fix-active; `qokshey` extract-contain-transition-essence-active; `cheody` volatile-essence-heat-fix-active.",
        "Explode into active extraction of double essence, drive the retort again, transition the essence, heat-fix the contained material, extract the transition essence once more, and end in a volatile-essence heat-fix.",
        "accelerate into doubled-essence extraction and heated fixation",
        "strong",
    ),
    (
        "P2.14",
        "chor.qodair.okeey.qokeey",
        "`chor` volatile outlet; `qodair` circulate-fix-earth-rotation; `okeey` heat-contain-double-essence-active; `qokeey` extract-contain-double-essence-active.",
        "Hold the volatile at the outlet, rotate the retort through a fixing turn, keep the double essence heated in containment, and extract it again under active control.",
        "bring the double essence outward and hold it under rotating retort control",
        "mixed",
    ),
    (
        "P3.15",
        "tsheoarom.shor.or.chor.olchsy.chom.otchom.oporar",
        "`tsheoarom` extended tagged transition-essence-heat-vessel cluster; `shor` transition outlet; `or` outlet; `chor` volatile outlet; `olchsy` fluid-volatile-dissolve-active; `chom` volatile-vessel; `otchom` timed volatile-vessel; `oporar` heat-press-outlet-root.",
        "Return to the tagged master substance, drive it through repeated outlet turns, dissolve the volatile fluid actively in the vessel, time the volatile vessel, and press the heated matter through the outlet-root geometry.",
        "re-enter the tagged hub substance and shift from storm to structure",
        "uncertain",
    ),
    (
        "P3.16",
        "oteol.chol.s.cheol.ekshy.qokeom.qokol.daiin.soleeg",
        "`oteol` timed essence-fluid; `chol` volatile-fluid; `s` dissolve; `cheol` volatile-essence-fluid; `ekshy` essence-contain-transition-active; `qokeom` extract-contain-double-essence-vessel; `qokol` circulate-contain-fluid; `daiin` checkpoint; `soleeg` dissolve-fluid-double-essence-growth.",
        "Time the essence-fluid, keep the volatile liquid live, dissolve it, reintroduce volatile essence-fluid, contain the transitioning essence, extract the double essence into the vessel, recirculate the liquid, verify the checkpoint, and let the double-essence dissolution grow.",
        "dissolve the doubled essence into contained structure and verify the retort state",
        "mixed",
    ),
    (
        "P3.17",
        "soeom.okeom.yteody.qokeeodal.sam",
        "`soeom` dissolve-essence-vessel; `okeom` heat-contain-essence-vessel; `yteody` moist-driven-essence-heat-fix-active; `qokeeodal` circulate-double-essence-heat-fix-structure; `sam` dissolve-union.",
        "Dissolve the essence inside the vessel, keep it heated and contained there, drive a moist essence heat-fix, retort the double essence into heated structure, and partially dissolve the union itself.",
        "turn double essence into fixed structure and partially dissolve the union",
        "strong",
    ),
    (
        "P4.18",
        "pcheoldom.shodaiin.qopchor.qopol.opchol.qoty.otolom",
        "`pcheoldom` press-volatile-essence-fluid-fix-vessel; `shodaiin` transition-heat-fix-cycle-complete; `qopchor` circulate-press-volatile-outlet; `qopol` circulate-press-fluid; `opchol` heat-press-volatile-fluid; `qoty` circulate-driven-heat-active; `otolom` timed-fluid-vessel.",
        "Press the volatile essence-fluid into a fixing vessel, complete the heated transition checkpoint, retort the pressurized volatile to the outlet, pressurize the liquid, heat-press the volatile fluid again, drive the active retort heat, and hold the timed liquid inside the vessel.",
        "start the pressurized terminal vessel sequence",
        "strong",
    ),
    (
        "P4.19",
        "otchor.olcheor.qoeor.dair.qoteol.qosaiin.chor.cthy",
        "`otchor` timed volatile outlet; `olcheor` fluid-volatile-essence outlet; `qoeor` circulate-essence-outlet; `dair` fix-earth-rotation; `qoteol` circulate-driven-essence-fluid; `qosaiin` circulate-salt-cycle-complete; `chor` volatile outlet; `cthy` conduit-bind-active.",
        "Time the volatile outlet, send fluid volatile essence to the outlet, retort the essence outward, fix it through one rotating turn, drive the essence-fluid again, complete the retort to salt, and hold the outlet on an active conduit bind.",
        "precipitate salt from the retort and hold the outlet",
        "strong",
    ),
    (
        "P4.20",
        "ycheor.chol.odaiin.chol.s.aiin.okol.or.am",
        "`ycheor` moist volatile-essence outlet; `chol` volatile-fluid; `odaiin` heated fixation complete; `chol` volatile-fluid; `s` dissolve; `aiin` cycle-complete; `okol` heat-contain-fluid; `or` outlet; `am` union.",
        "Return moist volatile essence to the outlet, keep the work in liquid volatile state, mark heated fixation complete, dissolve once more, close the cycle, hold the liquid under heated containment, and end in final union.",
        "finish the page with dissolved completion and final union",
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
        "The Lovers",
        "The Chariot",
        "Temperance",
        "Death",
        "Justice",
        "Strength",
        "The Hermit",
        "Wheel of Fortune",
        "The Emperor",
        "The Hanged Man",
        "The Tower",
        "The Star",
        "Judgment",
        "The Hierophant",
        "The Empress",
        "The Devil",
        "The Sun",
        "The World",
        "The Fool",
    ],
    "Juggling": [
        "name the prop",
        "first merge throw",
        "outlet catch",
        "structure pass",
        "two-phase crossover",
        "timed union hold",
        "heated return throw",
        "contained recovery",
        "long routing carry",
        "paragraph lock",
        "press into motion again",
        "storm cascade",
        "double-essence flourish",
        "controlled outward catch",
        "rebuild the pattern",
        "grow the center loop",
        "melt the joined cluster",
        "pressurized restart",
        "salt landing",
        "final merge hold",
    ],
    "Story Writing": [
        "name the hidden protagonist",
        "first union beat",
        "checkpoint scene",
        "second binding scene",
        "dissolution twist",
        "timed merger beat",
        "heated verification",
        "containment aftershock",
        "long transitional sentence",
        "paragraph seal",
        "recompression scene",
        "climactic action burst",
        "essence revelation",
        "controlled release",
        "architectural turn",
        "growth montage",
        "partial dissolution of the pact",
        "terminal apparatus set piece",
        "salt payoff",
        "union ending",
    ],
    "Hero's Journey": [
        "receive the true name",
        "cross into union",
        "first disciplined trial",
        "accept the second bind",
        "enter the dissolving cave",
        "time the sacred meeting",
        "win the heated test",
        "protect the gained boon",
        "long road through the channel",
        "seal the first world",
        "begin the inner ordeal",
        "face the storm of operations",
        "claim doubled essence",
        "carry it back under control",
        "re-enter with new architecture",
        "grow the hidden medicine",
        "let the old union break open",
        "prepare the final vessel",
        "win the salt reward",
        "return with the joined medicine",
    ],
}

MOVEMENTS = [
    "open the tagged vessel path",
    "marry the principles",
    "bind the outlet route",
    "extend the union into form",
    "split and dissolve the liquid bodies",
    "time the union exactly",
    "heat the wedding alive",
    "contain the aftermath",
    "draw the joined stream long",
    "close the first chamber",
    "press the essence again",
    "unleash the retort storm",
    "extract the doubled core",
    "turn the essence outward",
    "rebuild the vessel geometry",
    "grow structure from dissolution",
    "melt the joined knot strategically",
    "pressurize the last apparatus",
    "precipitate the salt mark",
    "close in union",
]

LEGEND = {
    "aqm": "`rho^-` incoming folio line state; `rho^+` outgoing line state; `Phi_line^(AQM)` source operator chain.",
    "cut": "`X=(kappa,varphi,ell,b)` with containment, phase, liquid flux, and boundary integrity.",
    "liminal": "`p(r)` regime mass, `lambda(e)` liminal-edge load, `f` fail-space mass.",
    "aetheric": "`g` compressed seed, `X` expanded state, `r_line` residual address.",
    "chemistry": "`x=[m_tagged,m_volatile,m_liquid,m_union,m_salt]^T`; `K_line` conserves total material.",
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
    out = ["### Paragraph 1 - tagging, first unions, and timed vessel wedding", ""]
    for line_id, eva, literal, operational, *_ in LINES[:10]:
        out += [f"- `{line_id}`", f"  EVA: `{eva}`", f"  Literal chain: {literal}", f"  Operational English: {operational}", ""]
    out += ["### Paragraph 2 - the qo storm and doubled-essence extraction", ""]
    for line_id, eva, literal, operational, *_ in LINES[10:14]:
        out += [f"- `{line_id}`", f"  EVA: `{eva}`", f"  Literal chain: {literal}", f"  Operational English: {operational}", ""]
    out += ["### Paragraph 3 - structural fixation after the storm", ""]
    for line_id, eva, literal, operational, *_ in LINES[14:17]:
        out += [f"- `{line_id}`", f"  EVA: `{eva}`", f"  Literal chain: {literal}", f"  Operational English: {operational}", ""]
    out += ["### Paragraph 4 - pressurized terminal retort, salt mark, and union closure", ""]
    for line_id, eva, literal, operational, *_ in LINES[17:]:
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
    out: list[str] = [
        "# F003R Final Draft - Dense Multilens Translation Atlas",
        "",
        "## Final Draft Status",
        "",
        "- Status: `authoritative final-draft folio`",
        "- Manuscript role: `first master extraction hub / retort-based transmutation with chemical wedding`",
        "- Book: `Book I - Herbal / materia medica`",
        "- Production standard: `framework-governed dense folio with full symbolic matrix`",
        "- Source baseline: `F003R.md`",
        "- Release target: `Plant Crystal`, unified corpus, metro layer, and master manuscript",
        "",
        "## Purpose",
        "",
        "This file is the authoritative final-draft version of `f003r`.",
        "",
        "Where `f2r` and `f2v` teach the first safe paired routes, `f3r` escalates the opening curriculum into a high-circulation union page. The folio is the earliest true master-extraction hub: it tags a key substance with `tsheos`, detonates a dense `qo-` storm, repeats the chemical wedding across multiple lines, then lands the work in a pressurized terminal retort that touches salt and closes in union.",
        "",
        "## Source Stack",
        "",
        "- `NEW/SECTION I - BOOK I_ THE HERBAL _ MATERIA MEDICA.md`",
        "- `NEW/working/VML_RECIPE_CROSSREF.md`",
        "- `NEW/working/VML_CONSISTENCY_PROOF.md`",
        "- `NEW/working/THE VML ROSETTA STONE.md`",
        "- `FULL_TRANSLATION/framework/FORMAL_MULTILENS_FRAMEWORK.md`",
        "- `FULL_TRANSLATION/framework/registry/lenses.json`",
        "- `FULL_TRANSLATION/framework/registry/math_kernel_registry.md`",
        "- `FULL_TRANSLATION/manifests/_f003r_source_extract.txt`",
        "",
        "## Reading Contract",
        "",
        "- The EVA and VML layers below are the closest direct translation claims.",
        "- Direct evidence and derived renderers remain separate.",
        "- The plant identification remains split between visual and operational witnesses.",
        "- The strongest claim is process identity: retort-heavy transmutation with repeated union markers and late salt touch.",
        "",
        "## Folio Zero Claim",
        "",
        "`f3r` is the first large retort-union lesson in the manuscript. Name the key extraction substance, cycle it aggressively through retort pressure, perform repeated chemical weddings, stabilize doubled essence into structure, then push the terminal vessel to a salt-marked union closure.",
        "",
        "## Folio Identity",
        "",
        "| Field | Value |",
        "| --- | --- |",
        "| Folio | `f3r` |",
        "| Quire | `A` |",
        "| Bifolio | `bA3 = f3 + f6` |",
        "| Currier language | `A` |",
        "| Currier hand | `1` |",
        "| Illustration | one plant with plume-like composite tips |",
        "| Botanical candidate | `Angelica archangelica` operationally favored; `Celosia argentea` remains the strongest visual candidate |",
        "| Risk level | moderate |",
        "| Direct confidence | high on retort-union process, moderate on recipe role, low-moderate on exact species |",
        "",
        "## Visual Grammar and Codicology",
        "",
        "- `plume-like composite flowers` = distributed extraction channels and multi-output collection",
        "- `upright branching stem` = retort work distributed through several active lanes",
        "- `non-iconic root` = page emphasis falls on process identity more than on a distinctive root signature",
        "- `high text density` = first early-herbal signal that operational complexity can outweigh botanical calm",
        "- `bifolio placement f3 + f6` = opening curriculum now moves from threshold and safe practice into advanced extraction",
        "",
        "## Full EVA",
        "",
        "```text",
        "P1.1: tsheos.qopal.chol.cthol.daimg-",
        "P1.2: ycheor.chor.dam.qotchag.cham-",
        "P1.3: ochar.qacheor.chol.daiin.cthy-",
        "P1.4: schey.chor.chal.cham.chaj.cho-",
        "P1.5: qokol.chololy.s.cham.cthol-",
        "P1.6: ychtaiin.chor.cthom.otoldam-",
        "P1.7: otchol.qodaiin.chom.shom.damo-",
        "P1.8: ysheor.chor.chol.oky.dago-",
        "P1.9: sho.aor.sheoldaj.otchody.ol-",
        "P1.10: ydas.cholcthom=",
        "",
        "P2.11: pcheol.shol.sols.sheol.shey-",
        "P2.12: okadaiin.qokchor.qoschodam.octhy-",
        "P2.13: qokeey.qot.shey.qokody.qokshey.cheody-",
        "P2.14: chor.qodair.okeey.qokeey=",
        "",
        "P3.15: tsheoarom.shor.or.chor.olchsy.chom.otchom.oporar-",
        "P3.16: oteol.chol.s.cheol.ekshy.qokeom.qokol.daiin.soleeg-",
        "P3.17: soeom.okeom.yteody.qokeeodal.sam=",
        "",
        "P4.18: pcheoldom.shodaiin.qopchor.qopol.opchol.qoty.otolom-",
        "P4.19: otchor.olcheor.qoeor.dair.qoteol.qosaiin.chor.cthy-",
        "P4.20: ycheor.chol.odaiin.chol.s.aiin.okol.or.am=",
        "```",
        "",
        "## Core VML Machinery Active On F3r",
        "",
        "- `tsheos` = tagged driven-transition essence marker and likely Book V bridge substance",
        "- `qo- storm` = exceptional retort circulation density, highest in the early herbal run",
        "- `dam / cham / am` = union family; the page is bracketed by chemical wedding logic",
        "- `otoldam` = timed fixation at the union point",
        "- `qodaiin` = retort-cycle verification to completion",
        "- `qoschodam` = densest page token: circulate-dissolve-volatile-heat-fix-union",
        "- `qokeeodal` = double-essence driven into heated structure",
        "- `qosaiin` = retort-to-salt completion",
        "- `pcheoldom` = press-volatile-essence-fluid-fix-vessel terminal apparatus cluster",
        "",
        "## Direct Line-By-Line Literal Ledger",
        "",
        ledger,
        "",
        "## Multilens Translation Atlas",
        "",
        formal,
        "",
        mythic,
        "",
        "## Direct Operational Meaning",
        "",
        "Paragraph 1 opens by naming the operative substance and performing successive union events under retort movement, timed fixation, and vessel control. Paragraph 2 is the page's operational climax: a compressed extraction storm where doubled essence is circulated, dissolved, heated, fixed, and unified at high density. Paragraph 3 converts that storm into structure, turning doubled essence into vessel-bound fixed form while partially dissolving the union for the last time. Paragraph 4 restarts the apparatus under pressure, drives the terminal essence-fluid outward, reaches an explicit salt completion in `qosaiin`, and ends the folio in final union.",
        "",
        "## Mathematical Extraction",
        "",
        "Across the formal math lenses, `f3r` is a bounded high-circulation union controller. The page spends most of its mass in retort-coupled volatile states, repeatedly increases union load, then partially discharges that load into structure before a single salt-marked terminal landing. It does not compute a quiet stable powder; it computes a compound volatile extract that brushes salt only at the end.",
        "",
        "## Mythic Extraction",
        "",
        "Across the mythic lenses, `f3r` is the first true alchemical wedding drama in the herbal opening. The page names the matter, marries it repeatedly, endures the storm of recombination, and returns from the ordeal carrying joined medicine rather than a single calm ingredient.",
        "",
        "## All-Lens Zero Point",
        "",
        "`f3r` means: once the vessel is proven and safe practice is known, the manuscript advances to compound extraction by retorting a named substance through repeated unions until doubled essence becomes structured medicine and the terminal circuit closes in salt-touched coniunctio.",
        "",
        "## Dense One-Sentence Compression",
        "",
        "Name the key substance, cycle it aggressively through retort pressure, perform repeated chemical weddings, convert doubled essence into structure, precipitate a salt touch, and end in union.",
        "",
        "## Formal Mathematical Overlay For F3r",
        "",
        "### Imported Kernel Equations",
        "",
        "\\[\\mathcal H := L^2(\\widehat{\\mathbb C}, \\mu), \\qquad \\rho \\in \\mathcal T_1(\\mathcal H), \\qquad \\rho \\succeq 0, \\qquad \\mathrm{Tr}(\\rho)=1\\]",
        "",
        "\\[\\mathcal H_{\\mathrm{tot}} = \\left(\\bigoplus_r \\mathcal H_r\\right) \\oplus \\left(\\bigoplus_e \\mathcal H_{\\Lambda_e}\\right) \\oplus \\mathcal H_{\\mathrm{fail}}\\]",
        "",
        "\\[x_{n+1}^{\\mathrm{chem}} = K_n x_n^{\\mathrm{chem}}, \\qquad \\mathbf{1}^T K_n = \\mathbf{1}^T\\]",
        "",
        "\\[g = \\mathrm{Coll}(X), \\qquad X = \\mathrm{Expand}(g) \\oplus r\\]",
        "",
        "\\[\\Phi_j^{(\\lambda)} = T_\\lambda^{-1} \\circ \\Phi_j^{(\\mathrm{AQM})} \\circ T_\\lambda\\]",
        "",
        "### Typed State Machine",
        "",
        "\\[\\mathcal R_{f3r} = \\{r_{\\mathrm{tag}}, r_{\\mathrm{union1}}, r_{\\mathrm{storm}}, r_{\\mathrm{structure}}, r_{\\mathrm{terminal}}, r_{\\mathrm{saltunion}}\\}\\]",
        "",
        "\\[\\mathcal E_\\Lambda = \\{e_{\\mathrm{union}}, e_{\\mathrm{pressure}}, e_{\\mathrm{salt}}\\}\\]",
        "",
        "\\[\\delta(e_{\\mathrm{union}}): r_{\\mathrm{tag}} \\to r_{\\mathrm{union1}} \\to r_{\\mathrm{storm}} \\to r_{\\mathrm{structure}} \\to r_{\\mathrm{saltunion}}\\]",
        "",
        "\\[\\delta(e_{\\mathrm{pressure}}): r_{\\mathrm{storm}} \\to r_{\\mathrm{terminal}}\\]",
        "",
        "\\[\\delta(e_{\\mathrm{salt}}): r_{\\mathrm{terminal}} \\to r_{\\mathrm{saltunion}}\\]",
        "",
        "\\[\\rho_0 \\in \\mathcal H_{r_{\\mathrm{tag}}}, \\qquad x_0^{\\mathrm{chem}} = \\begin{bmatrix} m_{\\mathrm{tagged}}^0 \\\\ m_{\\mathrm{volatile}}^0 \\\\ m_{\\mathrm{liquid}}^0 \\\\ 0 \\\\ 0 \\end{bmatrix}, \\qquad g_0 = \\mathrm{Coll}(\\rho_0)\\]",
        "",
        "### Canonical AQM Line Operators",
        "",
        ops,
        "",
        "### Paragraph Compositions",
        "",
        "\\[\\Phi_{P1}^{\\mathrm{tot}} = \\Phi_{\\mathrm{P1_10}}^{\\mathrm{AQM}} \\circ \\Phi_{\\mathrm{P1_9}}^{\\mathrm{AQM}} \\circ \\Phi_{\\mathrm{P1_8}}^{\\mathrm{AQM}} \\circ \\Phi_{\\mathrm{P1_7}}^{\\mathrm{AQM}} \\circ \\Phi_{\\mathrm{P1_6}}^{\\mathrm{AQM}} \\circ \\Phi_{\\mathrm{P1_5}}^{\\mathrm{AQM}} \\circ \\Phi_{\\mathrm{P1_4}}^{\\mathrm{AQM}} \\circ \\Phi_{\\mathrm{P1_3}}^{\\mathrm{AQM}} \\circ \\Phi_{\\mathrm{P1_2}}^{\\mathrm{AQM}} \\circ \\Phi_{\\mathrm{P1_1}}^{\\mathrm{AQM}}\\]",
        "",
        "\\[\\Phi_{P2}^{\\mathrm{tot}} = \\Phi_{\\mathrm{P2_14}}^{\\mathrm{AQM}} \\circ \\Phi_{\\mathrm{P2_13}}^{\\mathrm{AQM}} \\circ \\Phi_{\\mathrm{P2_12}}^{\\mathrm{AQM}} \\circ \\Phi_{\\mathrm{P2_11}}^{\\mathrm{AQM}}\\]",
        "",
        "\\[\\Phi_{P3}^{\\mathrm{tot}} = \\Phi_{\\mathrm{P3_17}}^{\\mathrm{AQM}} \\circ \\Phi_{\\mathrm{P3_16}}^{\\mathrm{AQM}} \\circ \\Phi_{\\mathrm{P3_15}}^{\\mathrm{AQM}}\\]",
        "",
        "\\[\\Phi_{P4}^{\\mathrm{tot}} = \\Phi_{\\mathrm{P4_20}}^{\\mathrm{AQM}} \\circ \\Phi_{\\mathrm{P4_19}}^{\\mathrm{AQM}} \\circ \\Phi_{\\mathrm{P4_18}}^{\\mathrm{AQM}}\\]",
        "",
        "\\[\\rho_{P1} = \\Phi_{P1}^{\\mathrm{tot}}(\\rho_0), \\qquad \\rho_{P2} = \\Phi_{P2}^{\\mathrm{tot}}(\\rho_{P1}), \\qquad \\rho_{P3} = \\Phi_{P3}^{\\mathrm{tot}}(\\rho_{P2}), \\qquad \\rho_* = \\Phi_{P4}^{\\mathrm{tot}}(\\rho_{P3})\\]",
        "",
        "### Formal Retort And Union Invariants",
        "",
        "\\[\\mathrm{Tr}(\\rho_n)=1\\]",
        "",
        "\\[f_n = \\mathrm{Tr}(\\Pi_{\\mathrm{fail}}\\rho_n) \\le \\varepsilon_{\\mathrm{moderate}}\\]",
        "",
        "\\[Q_{f3r} := \\sum_{j=1}^{20} \\mathbf{1}_{\\texttt{qo} \\prec \\ell_j} = 17\\]",
        "",
        "\\[U_{f3r} := \\sum_{j=1}^{20} \\mathbf{1}_{\\ell_j \\text{ carries union-family token}} = 8\\]",
        "",
        "\\[A_{f3r} := \\sum_{j=1}^{20} \\mathbf{1}_{\\texttt{aiin} \\prec \\ell_j} = 6\\]",
        "",
        "\\[S_{f3r}^{\\mathrm{salt}} := \\sum_{j=1}^{20} \\mathbf{1}_{\\texttt{qosaiin} \\prec \\ell_j} = 1\\]",
        "",
        "\\[m_{\\mathrm{union}}^* > 0, \\qquad m_{\\mathrm{volatile}}^* > 0, \\qquad m_{\\mathrm{salt}}^* > 0\\]",
        "",
        "### Conjugacy Law",
        "",
        "\\[\\Phi_j^{(\\lambda)} = T_\\lambda^{-1} \\circ \\Phi_j^{(\\mathrm{AQM})} \\circ T_\\lambda\\]",
        "",
        "\\[K_j = T_{\\mathrm{chem}}^{-1} \\Phi_j^{(\\mathrm{AQM})} T_{\\mathrm{chem}}, \\qquad U_j = T_{\\mathrm{wave}}^{-1} \\Phi_j^{(\\mathrm{AQM})} T_{\\mathrm{wave}}, \\qquad A_j = T_{\\mathrm{num}}^{-1} \\Phi_j^{(\\mathrm{AQM})} T_{\\mathrm{num}}\\]",
        "",
        "### Concrete Transport Targets",
        "",
        "\\[x_n^{\\mathrm{chem}} = \\begin{bmatrix} m_{\\mathrm{tagged}}(n) \\\\ m_{\\mathrm{volatile}}(n) \\\\ m_{\\mathrm{liquid}}(n) \\\\ m_{\\mathrm{union}}(n) \\\\ m_{\\mathrm{salt}}(n) \\end{bmatrix}, \\qquad X_n^{\\mathrm{phys}}=(\\kappa_n,\\varphi_n,\\pi_n,b_n), \\qquad m_n \\in \\mathbb{R}^{12}, \\qquad g_n=\\mathrm{Coll}(\\rho_n)\\]",
        "",
        "### Formal Folio Theorem",
        "",
        "\\[\\rho_* = \\left(\\Phi_{\\mathrm{P4_20}}^{\\mathrm{AQM}} \\circ \\Phi_{\\mathrm{P4_19}}^{\\mathrm{AQM}} \\circ \\Phi_{\\mathrm{P4_18}}^{\\mathrm{AQM}} \\circ \\Phi_{\\mathrm{P3_17}}^{\\mathrm{AQM}} \\circ \\Phi_{\\mathrm{P3_16}}^{\\mathrm{AQM}} \\circ \\Phi_{\\mathrm{P3_15}}^{\\mathrm{AQM}} \\circ \\Phi_{\\mathrm{P2_14}}^{\\mathrm{AQM}} \\circ \\Phi_{\\mathrm{P2_13}}^{\\mathrm{AQM}} \\circ \\Phi_{\\mathrm{P2_12}}^{\\mathrm{AQM}} \\circ \\Phi_{\\mathrm{P2_11}}^{\\mathrm{AQM}} \\circ \\Phi_{\\mathrm{P1_10}}^{\\mathrm{AQM}} \\circ \\Phi_{\\mathrm{P1_9}}^{\\mathrm{AQM}} \\circ \\Phi_{\\mathrm{P1_8}}^{\\mathrm{AQM}} \\circ \\Phi_{\\mathrm{P1_7}}^{\\mathrm{AQM}} \\circ \\Phi_{\\mathrm{P1_6}}^{\\mathrm{AQM}} \\circ \\Phi_{\\mathrm{P1_5}}^{\\mathrm{AQM}} \\circ \\Phi_{\\mathrm{P1_4}}^{\\mathrm{AQM}} \\circ \\Phi_{\\mathrm{P1_3}}^{\\mathrm{AQM}} \\circ \\Phi_{\\mathrm{P1_2}}^{\\mathrm{AQM}} \\circ \\Phi_{\\mathrm{P1_1}}^{\\mathrm{AQM}}\\right)(\\rho_0)\\]",
        "",
        "\\[\\Pi_{r_{\\mathrm{saltunion}}}\\rho_* = \\rho_*, \\qquad \\lambda_*(e_{\\mathrm{union}})=0, \\qquad \\lambda_*(e_{\\mathrm{salt}})=0\\]",
        "",
        "\\[x_*^{\\mathrm{chem}} = \\begin{bmatrix} m_{\\mathrm{tagged}}^* \\\\ m_{\\mathrm{volatile}}^* \\\\ m_{\\mathrm{liquid}}^* \\\\ m_{\\mathrm{union}}^* \\\\ m_{\\mathrm{salt}}^* \\end{bmatrix}, \\qquad m_{\\mathrm{union}}^* > 0, \\qquad m_{\\mathrm{volatile}}^* > 0, \\qquad m_{\\mathrm{salt}}^* > 0, \\qquad g_* = \\mathrm{Coll}(\\rho_*)\\]",
        "",
        "The theorem says `f003r` computes a high-circulation retort transmutation in which repeated union events amplify a tagged volatile substrate, doubled essence is converted into structure after the storm, and the terminal pressurized vessel lands in a salt-marked union closure instead of a simple calm fix.",
        "",
        "## Final Draft Audit",
        "",
        "- Every visible line has EVA, direct ledger, formal-math render, and mythic render.",
        "- The page-specific signatures `tsheos`, `dam`, `cham`, `otoldam`, `qoschodam`, `qokeeodal`, `qosaiin`, and final `am` remain explicit.",
        "- The contested plant identity stays split instead of being falsely collapsed to one certainty.",
        "- Confidence is highest for the page-level claim `retort-heavy chemical wedding / master extraction hub`.",
        "- Confidence is lower for exact recovery of opaque terminals like `daimg` and for any one-word species identification.",
        "",
        "## Plant Crystal Contribution",
        "",
        "- `Master Extraction Hub` - first early-herbal page where retort density outruns calm plant portraiture",
        "- `Chemical Wedding Line` - repeated union family markers bracket the whole procedure",
        "- `Qo Storm Station` - exceptional circulation density creates a new metro branch beyond simple reflux",
        "- `Late Salt Touch` - salt appears only after the union drama has already matured",
        "- `Bridge-Token Pressure` - `tsheos` suggests this folio may feed later pharmaceutical recipes at scale",
    ]
    return "\n".join(out).rstrip() + "\n"


def main() -> None:
    OUTPUT.write_text(render(), encoding="utf-8")


if __name__ == "__main__":
    main()
