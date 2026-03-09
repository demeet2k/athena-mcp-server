from __future__ import annotations

from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "folios" / "F002R_FINAL_DRAFT.md"

LINES = [
    ("P1.1", "kydainy.ypchol.daiin.otchal.ypchaiin.ckholsy", "`kydainy` moist-body-fix-complete-active; `ypchol` moist pressed volatile fluid; `daiin` standard fixation checkpoint; `otchal` timed volatile structure; `ypchaiin` moist pressed volatile through full cycle; `ckholsy` valve fluid dissolve active.", "Wet the body material, press it into volatile fluid, checkpoint the first cycle, time the volatile into structure, complete the moist press cycle, and open the liquid valve so dissolution can begin.", "prime the safe herb in a wet press-to-liquid start and open dissolution", "mixed"),
    ("P1.2", "dorchory.chkar.s.shor.cthy.***", "`dorchory` fixed double-outlet volatile active; `chkar` volatile contained at the root; `s` dissolve; `shor` transition outlet; `cthy` active conduit bind; `***` damaged terminal.", "Fix the rare double-outlet route, hold the volatile at the rooted container, dissolve it, transition it toward the outlet through the active conduit, and preserve the damaged remainder as unresolved.", "stabilize the double-outlet route and keep the volatile under conduit control despite damage", "uncertain"),
    ("P1.3", "qotaiin.cthey.y.chor.chy.ydy.chaiin", "`qotaiin` transmute-driven cycle complete; `cthey` conduit essence active; `y` active state marker; `chor` volatile outlet; `chy` volatile active; `ydy` moist fix active; `chaiin` volatile cycle complete.", "Send the work through a transmutive cycle, move energized essence through the conduit to the outlet, keep the volatile active, apply a moist fixing action, and mark the volatile cycle complete.", "move active essence through a successful transmutive outlet cycle", "mixed"),
    ("P1.4", "*aiidy.chtod.dy.cphy.dal.s.chokaiin.d", "`*aiidy` damaged cycle-fix-active opener; `chtod` volatile driven heat-fix; `dy` fix active; `cphy` alembic active; `dal` structural fixation; `s` dissolve; `chokaiin` volatile heat contain cycle complete; `d` fix.", "Under a damaged opening, drive the volatile by heat, reinforce fixation, keep the alembic active, set the structure, dissolve, bring the volatile-heat containment cycle to completion, and fix again.", "drive the alembic stage under partial damage but end in renewed fixation", "uncertain"),
    ("P1.5", "otochor.al.shodaiin.chol.chan.ytchaiin.dan", "`otochor` timed heated volatile at outlet; `al` structure; `shodaiin` transition heat fix cycle complete; `chol` volatile fluid; `chan` volatile cycle; `ytchaiin` moist driven volatile cycle complete; `dan` fix-cycle close.", "Time the heated volatile at the outlet into structure, complete the heated transition checkpoint, keep the volatile fluid cycling, run the moist-driven volatile cycle, and finish the cycle fix.", "time and structure the volatile fluid into the first completed cycle", "mixed"),
    ("P1.6", "saiin.daind.d.kol.sor.ytoldy.dchol.dchy.cthy", "`saiin` salt-cycle-complete; `daind` fix-complete-fix; `d` standalone fix; `kol` contain fluid; `sor` salt outlet; `ytoldy` moist driven fluid fixed active; `dchol` fixed volatile fluid; `dchy` fixed volatile active; `cthy` active conduit bind.", "Salt-seal the first closure, verify the fix twice, hold the fluid at the salt outlet, convert the moistened driven liquid into a fixed volatile fluid, and keep the conduit bound.", "mark the first salt closure and convert liquid handling into fixed conduit flow", "strong"),
    ("P1.7", "shor.ckhy.daiiny.chol.dan", "`shor` transition outlet; `ckhy` valve active; `daiiny` fix cycle complete active; `chol` volatile fluid; `dan` fix-cycle close.", "Move the transition to the outlet, touch the valve, register the active completion state, keep the volatile fluid present, and seal the first paragraph.", "seal the paragraph after a valve-verified volatile fix", "mixed"),
    ("P2.8", "kydain.shaiin.qoy.s.shol.fodan.ytsh.olsheey.daiildy", "`kydain` moist body fix complete; `shaiin` transition cycle complete; `qoy` transmute active; `s` dissolve; `shol` transition fluid; `fodan` formative heat fix complete; `ytsh` moist driven transition; `olsheey` fluid transition double essence active; `daiildy` extended cycle fix active.", "Restart from the moist body, complete the transition cycle, transmute, dissolve into the transition fluid, apply the rare growth-force heat-fix, drive the moist transition into double essence, and close the extended cycle.", "restart the herb under gentle transition and invoke the growth-force cycle variant", "mixed"),
    ("P2.9", "dlssho.kol.sheey.qokey.ykody.so.chol.yky.dain.daiirdl", "`dlssho` fix-lock-dissolve transition heat; `kol` contain fluid; `sheey` transition double essence active; `qokey` extract contain essence active; `ykody` moist contain heat fix active; `so` dissolve heat; `chol` volatile fluid; `yky` moist contained active; `dain` checkpoint; `daiirdl` rotating extended cycle lock.", "Fix-lock-dissolve the stream, hold the fluid, raise double essence through active extraction, moisten and heat-fix containment, dissolve the volatile fluid again, contain it, checkpoint it, and register the rotating extended cycle.", "perform the extended lock-dissolve extraction and register rotating completion", "mixed"),
    ("P2.10", "qoky.cholaiin.shol.sheky.daiin.cthey.keol.saiin.saiin", "`qoky` extract contain active; `cholaiin` volatile fluid cycle complete; `shol` transition fluid; `sheky` transition essence contain active; `daiin` fixation checkpoint; `cthey` conduit essence active; `keol` quintessence fluid; `saiin.saiin` doubled salt completion.", "Extract under active containment, complete the volatile-fluid cycle, transition the fluid while holding the essence, verify the fix, carry the quintessence through the conduit, and mark salt completion twice.", "produce quintessence-fluid and double salt verification", "strong"),
    ("P2.11", "ychain.dal.chy.dalor.shan.**saiin.sheey.ckhor", "`ychain` moist volatile complete; `dal` fix structure; `chy` volatile active; `dalor` fix-structure-outlet; `shan` transition cycle; `**saiin` damaged salt completion; `sheey` transition double essence; `ckhor` valve outlet.", "Moisten the volatile completion, structure it, project the fixed structure toward the outlet, run one more transition cycle, register the damaged third salt seal, and close the outlet valve state.", "carry the structured volatile to outlet and register the damaged third salt seal", "uncertain"),
    ("P2.12", "okol.chy.chor.cthor.yor.an.chan.saiin.chety.chyky.sal", "`okol` phase-heated contained fluid; `chy` volatile active; `chor` volatile outlet; `cthor` conduit outlet; `yor` moist outlet; `an` cycle; `chan` volatile cycle; `saiin` fourth salt completion; `chety` volatile essence driven active; `chyky` volatile active contain active; `sal` direct salt residue.", "Hold the heated liquid, send the volatile to the outlet through the conduit, route the moist outlet through a cycle, complete the volatile cycle, register the fourth salt seal, drive the essence in contained form, and expose the direct salt residue.", "expose the fourth salt completion and direct mineral residue", "mixed"),
    ("P2.13", "sho.ykeey.chey.daiin.chcthy", "`sho` transition heat; `ykeey` moist contained double essence active; `chey` volatile essence active; `daiin` final fixation checkpoint; `chcthy` volatile conduit bind active.", "Run the heated transition, energize the moistened double essence, keep the volatile essence active, make the final checkpoint, bind it to the conduit, and seal the page.", "finish with heated conduit-bound quintessence under final fixation", "mixed"),
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
    "Tarot": ["Temperance", "Justice", "The Chariot", "The Magician", "The Emperor", "The Hierophant", "The World", "The Empress", "The Hermit", "The Star", "Judgment", "Strength", "The Sun"],
    "Juggling": ["soft start", "split lane", "driven carry", "recovery catch", "timed pass", "first clean catch", "seal beat", "restart with variation", "tight lock", "double confirmation", "third catch", "show the prop", "final hold"],
    "Story Writing": ["gentle opening image", "route complication", "active progression", "craft scene", "structuring beat", "first closure", "scene seal", "renewed movement", "iterative refinement", "revelation", "penultimate verification", "material payoff", "quiet resolution"],
    "Hero's Journey": ["call in a safe domain", "crossing with caution", "first successful test", "trial with obscurity", "discipline gained", "first boon", "return from first circuit", "second departure", "road of trials", "reward", "road back", "mastery of two worlds", "return with medicine"],
}

MOVEMENTS = [
    "wet and proportion",
    "stabilize the fork",
    "carry essence onward",
    "operate through uncertainty",
    "time the route",
    "register the first salt seal",
    "seal the first circuit",
    "restart with healing force",
    "repeat the careful lock",
    "verify quintessence twice",
    "carry the third closure outward",
    "show the fixed residue",
    "bind the current and finish",
]

LEGEND = {
    "aqm": "`rho^-` incoming folio line state; `rho^+` outgoing line state; `Phi_line^(AQM)` source operator chain.",
    "cut": "`X=(kappa,varphi,ell,b)` with containment, phase, liquid flux, and boundary integrity.",
    "liminal": "`p(r)` regime mass, `lambda(e)` liminal-edge load, `f` fail-space mass.",
    "aetheric": "`g` compressed seed, `X` expanded state, `r_line` residual address.",
    "chemistry": "`x=[m_herb,m_volatile,m_liquid,m_salt]^T`; `K_line` conserves total material.",
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
    op = op_chain(eva)
    if lens == "aqm":
        return f"\\[\\rho_{{\\mathrm{{{s}}}}}^+ = \\Phi_{{\\mathrm{{{s}}}}}^{{\\mathrm{{AQM}}}}(\\rho_{{\\mathrm{{{s}}}}}^-), \\qquad \\Phi_{{\\mathrm{{{s}}}}}^{{\\mathrm{{AQM}}}} = {op}\\]"
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
    out = ["### Paragraph 1 - wet start, routing, and first salt closure", ""]
    for line_id, eva, literal, operational, *_ in LINES[:7]:
        out += [f"- `{line_id}`", f"  EVA: `{eva}`", f"  Literal chain: {literal}", f"  Operational English: {operational}", ""]
    out += ["### Paragraph 2 - cycle variants, quintessence, and distributed salt closure", ""]
    for line_id, eva, literal, operational, *_ in LINES[7:]:
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
    return dedent(f"""# F002R Final Draft - Dense Multilens Translation Atlas

## Final Draft Status

- Status: `authoritative final-draft folio`
- Manuscript role: `first standard safe herbal page / low-heat salt-closure demonstration`
- Book: `Book I - Herbal / materia medica`
- Production standard: `framework-governed dense folio with full symbolic matrix`
- Source baseline: `F002R.md`
- Release target: `Plant Crystal`, unified corpus, metro layer, and master manuscript

## Purpose

This file is the authoritative final-draft version of `f002r`.

It is the first fully articulated gentle-herb procedure after the threshold pair. Where `f1r` defines apparatus and `f1v` proves that apparatus under danger, `f2r` shows what ordinary successful healing work looks like: wet handling, minimal heat, repeated salt closure, protected quintessence, and distributed outputs.

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
- Damaged glyphs remain visible.
- The strongest claim is process identity: gentle low-heat salt crystallization with protected distributed outputs.

## Folio Zero Claim

`f2r` is the manuscript's first standard safe-herb lesson. Wet the healing herb, press and route it gently, drive repeated salt closures under minimal heat, carry the quintessence in liquid form, and distribute the medicine across multiple protected outcomes rather than one dangerous terminal core.

## Folio Identity

| Field | Value |
| --- | --- |
| Folio | `f2r` |
| Quire | `A` |
| Bifolio | `bA2 = f2 + f7` |
| Currier language | `A` |
| Currier hand | `1` |
| Illustration | one plant |
| Botanical candidate | `Centaurea` genus / cornflower-knapweed class |
| Risk level | safe |
| Direct confidence | moderate-high on process type, moderate on exact species |

## Visual Grammar and Codicology

- `symmetrical reaching root` = safe feedstock and measured handling
- `darkened root` = loaded source ready for work
- `short thin stem` = low-volume precision extraction
- `dark mid-vein` = essence path inside the larger channel
- `three brush flowers` = three graded or repeated output closures
- `hidden flower cores` = protected essence held inside distributed product form

## Full EVA

```text
P1.1: kydainy.ypchol.daiin.otchal.ypchaiin.ckholsy-
P1.2: dorchory.chkar.s.shor.cthy.***-
P1.3: qotaiin.cthey.y.chor.chy.ydy.chaiin-
P1.4: *aiidy.chtod.dy.cphy.dal.s.chokaiin.d-
P1.5: otochor.al.shodaiin.chol.chan.ytchaiin.dan-
P1.6: saiin.daind.d.kol.sor.ytoldy.dchol.dchy.cthy-
P1.7: shor.ckhy.daiiny.chol.dan=

P2.8: kydain.shaiin.qoy.s.shol.fodan.ytsh.olsheey.daiildy-
P2.9: dlssho.kol.sheey.qokey.ykody.so.chol.yky.dain.daiirdl-
P2.10: qoky.cholaiin.shol.sheky.daiin.cthey.keol.saiin.saiin-
P2.11: ychain.dal.chy.dalor.shan.**saiin.sheey.ckhor-
P2.12: okol.chy.chor.cthor.yor.an.chan.saiin.chety.chyky.sal-
P2.13: sho.ykeey.chey.daiin.chcthy=
```

## Core VML Machinery Active On F2r

- `saiin` = salt-phase completion checkpoint
- `sal` = direct fixed salt residue
- `keol` = quintessence in liquid form
- `ky / y` = moist, receptive, gentle activation and containment
- `qo` = circulate, extract, or retort-cycle
- `fodan` = rare formative-growth heat-fix marker
- `cth` = conduit, throat, or transport line
- `ckh` = valve or seal checkpoint
- `cph` = alembic / pressure chamber
- `daiin` = standard fixation checkpoint
- `daiiny`, `daiildy`, `daiirdl` = extended or variant cycle completions

## Direct Line-By-Line Literal Ledger

{ledger}

## Multilens Translation Atlas

{formal}

{mythic}

## Direct Operational Meaning

Paragraph 1 wets and presses the herb into a gentle fluid route, pushes it through conduit and outlet control, stabilizes the alembic stage, and reaches the first explicit salt closure in `saiin`. Paragraph 2 restarts the body in a second cycle, invokes the rare healing-growth marker `fodan`, runs extended cycle variants, brings `keol` into view as liquid quintessence, doubles salt verification, then exposes direct salt residue in `sal` before sealing the page.

## Mathematical Extraction

Across the formal math lenses, `f2r` is a bounded low-energy salt-crystallization controller. The state never enters the dangerous fire-seal regime of `f1v`; instead it conserves a gentle heat budget, executes four line-level salt checkpoints, carries a liquid quintessence, and terminates in a distributed fixed-principle output family.

## Mythic Extraction

Across the mythic lenses, `f2r` is the healer's ordinary craft scene rather than the poison-master's ordeal. The page teaches how to turn a safe living body into transmissible medicine through patience, moisture, iteration, and repeated proof of closure.

## All-Lens Zero Point

`f2r` means: healing material becomes stable medicine when it is handled gently, cycled repeatedly, fixed through salt closure, and distributed in protected grades rather than concentrated into one dangerous singular core.

## Dense One-Sentence Compression

Wet the safe herb, press it into volatile liquid, pass it through low-heat cycles, register four salt closures around a liquid quintessence, and finish with protected distributed medicine plus fixed salt residue.

## Formal Mathematical Overlay For F2r

### Imported Kernel Equations

\\[\\mathcal H := L^2(\\widehat{{\\mathbb C}}, \\mu), \\qquad \\rho \\in \\mathcal T_1(\\mathcal H), \\qquad \\rho \\succeq 0, \\qquad \\mathrm{{Tr}}(\\rho)=1\\]

\\[\\mathcal H_{{\\mathrm{{tot}}}} = \\left(\\bigoplus_r \\mathcal H_r\\right) \\oplus \\left(\\bigoplus_e \\mathcal H_{{\\Lambda_e}}\\right) \\oplus \\mathcal H_{{\\mathrm{{fail}}}}\\]

\\[x_{{n+1}}^{{\\mathrm{{chem}}}} = K_n x_n^{{\\mathrm{{chem}}}}, \\qquad \\mathbf{{1}}^T K_n = \\mathbf{{1}}^T\\]

\\[g = \\mathrm{{Coll}}(X), \\qquad X = \\mathrm{{Expand}}(g) \\oplus r\\]

\\[\\Phi_j^{{(\\lambda)}} = T_\\lambda^{{-1}} \\circ \\Phi_j^{{(\\mathrm{{AQM}})}} \\circ T_\\lambda\\]

### Typed State Machine

\\[\\mathcal R_{{f2r}} = \\{{r_{{\\mathrm{{wet}}}}, r_{{\\mathrm{{press}}}}, r_{{\\mathrm{{salt1}}}}, r_{{\\mathrm{{variant}}}}, r_{{\\mathrm{{quint}}}}, r_{{\\mathrm{{distribute}}}}\\}}\\]

\\[\\mathcal E_\\Lambda = \\{{e_{{\\mathrm{{damage}}}}, e_{{\\mathrm{{salt}}}}, e_{{\\mathrm{{variant}}}}\\}}\\]

\\[\\delta(e_{{\\mathrm{{salt}}}}): r_{{\\mathrm{{press}}}} \\to r_{{\\mathrm{{salt1}}}} \\to r_{{\\mathrm{{variant}}}} \\to r_{{\\mathrm{{quint}}}} \\to r_{{\\mathrm{{distribute}}}}\\]

\\[\\delta(e_{{\\mathrm{{variant}}}}): \\{{\\texttt{{daiiny}}, \\texttt{{daiildy}}, \\texttt{{daiirdl}}\\}}\\]

\\[\\rho_0 \\in \\mathcal H_{{r_{{\\mathrm{{wet}}}}}}, \\qquad x_0^{{\\mathrm{{chem}}}} = \\begin{{bmatrix}} m_{{\\mathrm{{herb}}}}^0 \\\\ m_{{\\mathrm{{volatile}}}}^0 \\\\ m_{{\\mathrm{{liquid}}}}^0 \\\\ 0 \\end{{bmatrix}}, \\qquad g_0 = \\mathrm{{Coll}}(\\rho_0)\\]

### Canonical AQM Line Operators

{ops}

### Paragraph Compositions

\\[\\Phi_{{P1}}^{{\\mathrm{{tot}}}} = \\Phi_{{\\mathrm{{P1_7}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P1_6}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P1_5}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P1_4}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P1_3}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P1_2}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P1_1}}}}^{{\\mathrm{{AQM}}}}\\]

\\[\\Phi_{{P2}}^{{\\mathrm{{tot}}}} = \\Phi_{{\\mathrm{{P2_13}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P2_12}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P2_11}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P2_10}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P2_9}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P2_8}}}}^{{\\mathrm{{AQM}}}}\\]

\\[\\rho_{{P1}} = \\Phi_{{P1}}^{{\\mathrm{{tot}}}}(\\rho_0), \\qquad \\rho_* = \\Phi_{{P2}}^{{\\mathrm{{tot}}}}(\\rho_{{P1}})\\]

### Formal Safety And Yield Invariants

\\[\\mathrm{{Tr}}(\\rho_n)=1\\]

\\[f_n = \\mathrm{{Tr}}(\\Pi_{{\\mathrm{{fail}}}}\\rho_n) \\le \\varepsilon_{{\\mathrm{{damage}}}}\\]

\\[H_{{f2r}} := \\sum_j h_j = 4\\]

\\[S_{{f2r}}^{{\\mathrm{{lines}}}} := \\sum_{{j \\in \\{{P1.6,P2.10,P2.11,P2.12\\}}}} 1 = 4, \\qquad v_{{P2.10}}^{{\\mathrm{{salt}}}} = 2\\]

\\[N_{{\\mathrm{{flower}}}} = 3\\]

\\[m_{{\\mathrm{{quint}}}}^* > 0, \\qquad m_{{\\mathrm{{salt}}}}^* > 0, \\qquad m_{{\\mathrm{{liquid}}}}^* > 0\\]

### Conjugacy Law

\\[\\Phi_j^{{(\\lambda)}} = T_\\lambda^{{-1}} \\circ \\Phi_j^{{(\\mathrm{{AQM}})}} \\circ T_\\lambda\\]

\\[K_j = T_{{\\mathrm{{chem}}}}^{{-1}} \\Phi_j^{{(\\mathrm{{AQM}})}} T_{{\\mathrm{{chem}}}}, \\qquad U_j = T_{{\\mathrm{{wave}}}}^{{-1}} \\Phi_j^{{(\\mathrm{{AQM}})}} T_{{\\mathrm{{wave}}}}, \\qquad A_j = T_{{\\mathrm{{num}}}}^{{-1}} \\Phi_j^{{(\\mathrm{{AQM}})}} T_{{\\mathrm{{num}}}}\\]

### Concrete Transport Targets

\\[x_n^{{\\mathrm{{chem}}}} = \\begin{{bmatrix}} m_{{\\mathrm{{herb}}}}(n) \\\\ m_{{\\mathrm{{volatile}}}}(n) \\\\ m_{{\\mathrm{{liquid}}}}(n) \\\\ m_{{\\mathrm{{salt}}}}(n) \\end{{bmatrix}}, \\qquad X_n^{{\\mathrm{{phys}}}}=(\\kappa_n,\\varphi_n,\\ell_n,b_n), \\qquad m_n \\in \\mathbb{{R}}^{{12}}, \\qquad g_n=\\mathrm{{Coll}}(\\rho_n)\\]

### Formal Folio Theorem

\\[\\rho_* = \\left(\\Phi_{{\\mathrm{{P2_13}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P2_12}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P2_11}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P2_10}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P2_9}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P2_8}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P1_7}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P1_6}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P1_5}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P1_4}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P1_3}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P1_2}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P1_1}}}}^{{\\mathrm{{AQM}}}}\\right)(\\rho_0)\\]

\\[\\Pi_{{r_{{\\mathrm{{distribute}}}}}}\\rho_* = \\rho_*, \\qquad \\lambda_*(e_{{\\mathrm{{salt}}}})=0, \\qquad \\lambda_*(e_{{\\mathrm{{variant}}}})=0\\]

\\[x_*^{{\\mathrm{{chem}}}} = \\begin{{bmatrix}} m_{{\\mathrm{{herb}}}}^* \\\\ m_{{\\mathrm{{quint}}}}^* \\\\ m_{{\\mathrm{{liquid}}}}^* \\\\ m_{{\\mathrm{{salt}}}}^* \\end{{bmatrix}}, \\qquad m_{{\\mathrm{{quint}}}}^* > 0, \\qquad m_{{\\mathrm{{salt}}}}^* > 0, \\qquad g_* = \\mathrm{{Coll}}(\\rho_*)\\]

The theorem says `f2r` computes a gentle low-heat multi-cycle salt-crystallization process whose terminal object is not one dangerous singularity but a protected quintessence-plus-salt output family distributed across three grades.

## Final Draft Audit

- Every visible line has EVA, direct ledger, formal-math render, and mythic render.
- The page-specific signatures `saiin`, `saiin.saiin`, `sal`, `keol`, and `fodan` remain explicit.
- Damage markers on `P1.2`, `P1.4`, and `P2.11` remain visible instead of being silently normalized away.
- Confidence is highest for the page-level claim `safe low-heat salt crystallization with distributed healing outputs`.
- Confidence is lower for the first-word plant-label hypothesis and for exact recovery of the damaged tokens.

## Plant Crystal Contribution

- `First Safe Herb Station` - the manuscript finally shows ordinary non-lethal practice
- `Salt Signature` - four line-level salt closures with doubled verification at `P2.10`
- `Growth Force Marker` - rare `fodan` aligns the page with healing and regeneration
- `Distributed Product Logic` - three flowers map to graded protected outputs
- `Threshold Triptych Completion` - `f1r + f1v + f2r` now reads as apparatus, danger, and standard practice
""").strip() + "\n"


def main() -> None:
    OUTPUT.write_text(render(), encoding="utf-8")


if __name__ == "__main__":
    main()
