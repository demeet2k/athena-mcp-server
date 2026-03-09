from __future__ import annotations

from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "folios" / "F004V_FINAL_DRAFT.md"

LINES = [
    (
        "P1.1",
        "pchooiin.ksheo.kchoy.chopchy.dolds.dlod",
        "`pchooiin` press-volatile-double-heat-cycle; `ksheo` body-transition-essence-heat; `kchoy` body-volatile-heat-active; `chopchy` volatile-heat-press-volatile-active; `dolds` fix-fluid-lock-dissolve; `dlod` fix-lock-heat-fix.",
        "Press the volatile through a double-heated cycle, charge the body and transition essence with heat, intensify the volatile under pressure, then run the distinctive forward-and-reverse lock sequence that dissolves and re-fixes the fluid.",
        "open the page with double-heated pressurization and the palindromic reflux-reversal pair",
        "strong",
    ),
    (
        "P1.2",
        "ol.chey.chy.cthy.chkchor.sheo.cheory.choldy",
        "`ol` fluid; `chey` volatile-essence-active; `chy` volatile-active; `cthy` conduit-bind-active; `chkchor` volatile-contain-volatile-outlet; `sheo` transition-essence-heat; `cheory` volatile-essence-outlet-active; `choldy` volatile-heat-fluid-fix-active.",
        "Keep the work fluid, activate the volatile essence, bind it into the conduit, hold the volatile at the outlet in containment, add heated transition essence, and finish the line in a heat-fixed volatile liquid state.",
        "route active volatile essence through a bound conduit to the outlet",
        "strong",
    ),
    (
        "P1.3",
        "cho.sho.chaiin.shaiin.daiin.qodaiin.o.ar.am",
        "`cho` volatile-heat; `sho` transition-heat; `chaiin` volatile-cycle-complete; `shaiin` transition-cycle-complete; `daiin` fix-cycle-complete; `qodaiin` retort-fix-cycle-complete; `o` heat; `ar` root; `am` union.",
        "Run the volatile and transition heats together, complete the volatile cycle, complete the transition cycle, complete fixation, complete the retort-fix cycle, then root the result and land it in union.",
        "execute the page's completion cascade and first explicit union closure",
        "strong",
    ),
    (
        "P1.4",
        "qokchy.qocthy.choteol.daiin.cthey.choaiin",
        "`qokchy` extract-contain-volatile-active; `qocthy` transmute-conduit-bind-active; `choteol` volatile-heat-driven-essence-fluid; `daiin` checkpoint; `cthey` conduit-essence-active; `choaiin` volatile-heat-cycle-complete.",
        "Extract the contained volatile, transmute it through the bound conduit, drive the volatile-essence fluid forward, mark a checkpoint, keep the conduit essence active, and close the paragraph with a completed volatile-heat cycle.",
        "seal paragraph one with checkpointed conduit extraction",
        "strong",
    ),
    (
        "P2.5",
        "shor.sheey.**.otoiin.shey.qotchoiin.chodain",
        "`shor` transition-outlet; `sheey` transition-double-essence; `**` damaged witness; `otoiin` temporal-heat-cycle; `shey` transition-essence-active; `qotchoiin` transmute-driven-volatile-heat-cycle; `chodain` volatile-heat-fix-complete.",
        "Return to the transition outlet, raise double essence, preserve the damaged witness honestly, run the temporal heat-cycle, reactivate the transition essence, drive the volatile heat-cycle again, and complete the volatile heat-fix.",
        "restart the process with transition double-essence under damaged but still readable witness",
        "mixed",
    ),
    (
        "P2.6",
        "ytchoy.shokchy.cphody",
        "`ytchoy` moist-driven-volatile-heat-active; `shokchy` transition-heat-contain-volatile-active; `cphody` alembic-heat-fix-active.",
        "Keep the volatile moist, driven, and heated, contain it within a transition-heat boundary, and fix it actively through the alembic.",
        "compress the volatile into alembic heat-fix",
        "strong",
    ),
    (
        "P3.7",
        "torchy.sheeor.chor.chokchy.pydy",
        "`torchy` driven-outlet-volatile-active; `sheeor` transition-double-essence-outlet; `chor` volatile-outlet; `chokchy` volatile-heat-contain-volatile-active; `pydy` press-moist-fix-active.",
        "Drive the volatile actively toward the outlet, bring double essence outward, keep the volatile route heated and contained, and press the resulting moist fraction into fixation.",
        "open the third paragraph with outward double-essence routing and moist fixation",
        "mixed",
    ),
    (
        "P3.8",
        "olain.chor.cthol.sho.otor.cthory",
        "`olain` fluid-complete; `chor` volatile-outlet; `cthol` conduit-fluid; `sho` transition-heat; `otor` temporal-heat-outlet; `cthory` conduit-heat-outlet-active.",
        "Complete the fluid state, hold the volatile at the outlet, carry it through conduit-liquid, reapply transition heat, time the outlet heating, and keep the conduit-outlet channel active.",
        "maintain timed outlet heating across the conduit-liquid channel",
        "mixed",
    ),
    (
        "P3.9",
        "qookoiiin.cheod.chcthy.shoky.daiin",
        "`qookoiiin` transmute-heat-contain-heat-triple-cycle; `cheod` volatile-essence-heat-fix; `chcthy` volatile-conduit-bind-active; `shoky` transition-heat-contain-active; `daiin` checkpoint.",
        "Enter the page's longest triple-cycle retort token, fix the volatile essence under heat, bind the volatile back into the conduit, keep the transition-heat containment active, and checkpoint the result.",
        "run the triple-cycle retort extraction and checkpoint the bound volatile essence",
        "strong",
    ),
    (
        "P3.10",
        "otaiin.sheo.okeody.chol.chokeody",
        "`otaiin` temporal-cycle-complete; `sheo` transition-essence-heat; `okeody` heat-contain-essence-heat-fix-active; `chol` volatile-fluid; `chokeody` volatile-heat-contain-essence-heat-fix-active.",
        "Complete the timed cycle, reintroduce heated transition essence, keep the essence contained and heat-fixed, hold the work in volatile liquid form, and intensify that heat-fixed containment inside the volatile channel.",
        "turn the retorted essence into a stable heat-fixed volatile liquid",
        "strong",
    ),
    (
        "P3.11",
        "shokcheor.shooy.shtaiin.qotol.daiin",
        "`shokcheor` transition-heat-contain-volatile-essence-outlet; `shooy` transition-heat-heat-active; `shtaiin` transition-driven-cycle-complete; `qotol` transmute-heat-fluid; `daiin` checkpoint.",
        "Hold heated transition essence at the outlet in containment, intensify the thermal regime, complete the driven transition cycle, move the work through transmuting heat-fluid, and checkpoint the state again.",
        "stabilize the outlet regime through contained heated transition and checkpointing",
        "mixed",
    ),
    (
        "P3.12",
        "qokoy.sho.okeol.s.keey.shar.char.ody",
        "`qokoy` extract-contain-heat-active; `sho` transition-heat; `okeol` heat-contain-essence-fluid; `s` dissolve; `keey` contain-double-essence-active; `shar` transition-root; `char` volatile-root; `ody` heat-fix-active.",
        "Extract and contain the heated work, keep transition heat alive, hold the essence in heated liquid, dissolve it, raise contained double essence, then root both transition and volatile lanes and end in active heat-fix.",
        "dissolve the extracted essence into rooted double-essence fixation",
        "strong",
    ),
    (
        "P3.13",
        "shody.s.cheor.chokody.shodaiin.qoty",
        "`shody` transition-heat-fix-active; `s` dissolve; `cheor` volatile-essence-outlet; `chokody` volatile-heat-contain-heat-fix-active; `shodaiin` transition-heat-fix-cycle-complete; `qoty` transmute-heat-active.",
        "Fix the heated transition, dissolve again, bring volatile essence to the outlet, contain and heat-fix the volatile path, complete the transition heat-fix cycle, and keep the transmuting heat active.",
        "prepare the terminal state through dissolved heat-fix and active transmutation",
        "strong",
    ),
    (
        "P3.14",
        "ochody.chykey.chtody",
        "`ochody` heat-volatile-heat-fix-active; `chykey` volatile-active-contain-essence-active; `chtody` volatile-driven-heat-fix-active.",
        "Close the page with volatile heat-fix held active, contained essence still alive inside the volatile lane, and one final driven volatile heat-fix.",
        "seal the page in an active volatile heat-fixed state",
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
        "Judgment",
        "Justice",
        "The Moon",
        "The Hermit",
        "The Chariot",
        "Wheel of Fortune",
        "Strength",
        "The Emperor",
        "The High Priestess",
        "Death",
        "The Star",
        "The World",
    ],
    "Juggling": [
        "double-heat launch",
        "conduit carry",
        "completion cascade catch",
        "checkpoint seal",
        "damaged restart throw",
        "alembic lock",
        "outward double-essence pass",
        "timed outlet hold",
        "triple-cycle flourish",
        "dense containment recover",
        "heated checkpoint reset",
        "rooting dissolve",
        "pre-terminal fix",
        "active final hold",
    ],
    "Story Writing": [
        "double-heat opening",
        "bound channel scene",
        "completion cascade climax",
        "checkpoint paragraph close",
        "damaged testimony beat",
        "short alembic seal",
        "third-act expansion",
        "timed route scene",
        "major extraction set piece",
        "stabilization beat",
        "regime-control beat",
        "rooting transformation",
        "terminal preparation",
        "live-state ending",
    ],
    "Hero's Journey": [
        "enter the heated vessel",
        "take the conduit road",
        "win the first great proof",
        "bind the gained power",
        "cross the damaged threshold",
        "seal the compact lesson",
        "drive outward again",
        "hold the timed channel",
        "face the triple ordeal",
        "secure the volatile boon",
        "master the heated boundary",
        "root the doubled essence",
        "prepare the final fire",
        "return with active medicine",
    ],
}

MOVEMENTS = [
    "drive the double-heat press",
    "bind the conduit route",
    "stack completions into union",
    "seal the checkpoint",
    "restart under damage",
    "compress into alembic fix",
    "push the volatile outward",
    "hold the timed conduit",
    "run the triple retort",
    "stabilize the essence fluid",
    "govern the boundary",
    "root the extraction",
    "prepare the final state",
    "close while still active",
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
    out = ["### Paragraph 1 - double-heat launch, completion cascade, and checkpointed seal", ""]
    for line_id, eva, literal, operational, *_ in LINES[:4]:
        out += [f"- `{line_id}`", f"  EVA: `{eva}`", f"  Literal chain: {literal}", f"  Operational English: {operational}", ""]
    out += ["### Paragraph 2 - damaged restart and alembic compression", ""]
    for line_id, eva, literal, operational, *_ in LINES[4:6]:
        out += [f"- `{line_id}`", f"  EVA: `{eva}`", f"  Literal chain: {literal}", f"  Operational English: {operational}", ""]
    out += ["### Paragraph 3 - triple retort monitoring and active volatile closure", ""]
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
        f"""# F004V Final Draft - Dense Multilens Translation Atlas

## Final Draft Status

- Status: `authoritative final-draft folio`
- Manuscript role: `checkpoint-monitored volatile processing / rue-style redistillation page`
- Book: `Book I - Herbal / materia medica`
- Production standard: `framework-governed dense folio with full symbolic matrix`
- Source baseline: `F004V.md`
- Release target: `Plant Crystal`, unified corpus, metro layer, and master manuscript

## Purpose

This file is the authoritative final-draft version of `f004v`.

Where `f4r` teaches patient repeated steeping, `f4v` swings the bifolio back into volatile concentration. The page opens with a doubled-heat press, immediately exposes the `dolds/dlod` reflux-reversal pair, runs a four-stage completion cascade into union, then restarts through damaged witnesses, passes a triple-cycle retort, and closes with an active volatile heat-fixed state. Across the local corpus, this fits rue-style volatile oil processing and redistillation better than a calm edible root herb.

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
- Botanical identity remains partially disputed between rue and the visual campanula/rampion family.
- The strongest claim is process identity: monitored volatile distillation with reflux reversal, completion cascades, checkpoint density, and triple retort correction.

## Folio Zero Claim

`f4v` means: double-heat and press the volatile route, reverse the lock state through reflux, verify every regime in sequence, then redistill the active spirit under repeated checkpoints until the volatile medicine is fixed yet still alive.

## Folio Identity

| Field | Value |
| --- | --- |
| Folio | `f4v` |
| Quire | `A` |
| Bifolio | `bA4 = f4 + f5` |
| Currier language | `A` |
| Currier hand | `1` |
| Illustration | single plant with herculeaf and mixed leaf shapes |
| Botanical candidate | `Ruta graveolens` operationally favored; `Campanula/Phyteuma` remains the strongest visual rival |
| Risk level | moderate |
| Direct confidence | high on checkpoint-heavy volatile processing, moderate on exact species |

## Visual Grammar and Codicology

- `mixed leaf shapes` = multi-regime extraction rather than one simple carrier route
- `center-bifolio placement` = the quire alternates stable infusion and volatile rectification on the same leaf pair
- `process-spike logic in the local notes` = repeated checkpoints and operator interventions
- `text density higher than calm herb pages` = quality-control burden is part of the recipe identity

## Full EVA

```text
P1.1: pchooiin.ksheo.kchoy.chopchy.dolds.dlod-
P1.2: ol.chey.chy.cthy.chkchor.sheo.cheory.choldy-
P1.3: cho.sho.chaiin.shaiin.daiin.qodaiin.o.ar.am-
P1.4: qokchy.qocthy.choteol.daiin.cthey.choaiin-

P2.5: shor.sheey.**.otoiin.shey.qotchoiin.chodain-
P2.6: ytchoy.shokchy.cphody=

P3.7: torchy.sheeor.chor.chokchy.pydy-
P3.8: olain.chor.cthol.sho.otor.cthory-
P3.9: qookoiiin.cheod.chcthy.shoky.daiin-
P3.10: otaiin.sheo.okeody.chol.chokeody-
P3.11: shokcheor.shooy.shtaiin.qotol.daiin-
P3.12: qokoy.sho.okeol.s.keey.shar.char.ody-
P3.13: shody.s.cheor.chokody.shodaiin.qoty-
P3.14: ochody.chykey.chtody=
```

## Core VML Machinery Active On F4v

- `pchooiin` = doubled-heat volatile pressing at the page opening
- `dolds / dlod` = palindromic reflux-reversal marker unique in the local corpus
- `chaiin + shaiin + daiin + qodaiin` = the page's four-step completion cascade
- `qokchy / qocthy` = active extraction plus conduit-bound transmutation
- `qotchoiin` = driven volatile heat-cycle restart after damage
- `qookoiiin` = triple-cycle transmutation under containment, one of the page's highest-intensity tokens
- `daiin` checkpoints recur through every later phase
- no salt closure appears; the output remains volatile and active

## Direct Line-By-Line Literal Ledger

{ledger}

## Multilens Translation Atlas

{formal}

{mythic}

## Direct Operational Meaning

Paragraph 1 starts under deliberate pressure: doubled heat, body loading, and a forward-reverse reflux pair that makes this page read like monitored volatile rectification rather than simple infusion. The line `cho.sho.chaiin.shaiin.daiin.qodaiin.o.ar.am` then performs the folio's core didactic act by completing volatile, transition, fixation, and retort regimes in one cascade before union. Paragraph 2 restarts the work through damaged witnesses but compresses it quickly back into alembic fixation. Paragraph 3 expands again into outward routing, timed outlet control, a triple-cycle retort, repeated checkpoints, and a terminal active volatile fix. The page therefore reads as a moderate-risk aromatic poison or medicinal volatile that must be redistilled under close supervision.

## Mathematical Extraction

Across the formal math lenses, `f4v` is a checkpoint-saturated volatile controller. It alternates pressure, bind, verify, and repeat. Unlike `f4r`, it does not seek proof through soaking alone; it seeks proof through monitored state transitions and explicit completion cascades. The dominant invariant is bounded regime verification under active volatile load.

## Mythic Extraction

Across the mythic lenses, `f4v` is the examiner's page. The operator is not just extracting a medicine but proving at every stage that the vessel, route, and state remain admissible. Its myth is disciplined volatility rather than patience or marriage.

## All-Lens Zero Point

`f4v` means: when the medicine is volatile and moderately dangerous, you do not merely distill it, you interrogate it, reverse it, verify it, and only then permit it to remain active.

## Dense One-Sentence Compression

Double-heat the volatile path, reverse it through reflux, complete every regime in sequence, then redistill under repeated checkpoints until the volatile product is fixed but still alive.

## Formal Mathematical Overlay For F4v

### Imported Kernel Equations

\\[\\mathcal H := L^2(\\widehat{{\\mathbb C}}, \\mu), \\qquad \\rho \\in \\mathcal T_1(\\mathcal H), \\qquad \\rho \\succeq 0, \\qquad \\mathrm{{Tr}}(\\rho)=1\\]

\\[\\mathcal H_{{\\mathrm{{tot}}}} = \\left(\\bigoplus_r \\mathcal H_r\\right) \\oplus \\left(\\bigoplus_e \\mathcal H_{{\\Lambda_e}}\\right) \\oplus \\mathcal H_{{\\mathrm{{fail}}}}\\]

\\[x_{{n+1}}^{{\\mathrm{{chem}}}} = K_n x_n^{{\\mathrm{{chem}}}}, \\qquad \\mathbf{{1}}^T K_n = \\mathbf{{1}}^T\\]

\\[g = \\mathrm{{Coll}}(X), \\qquad X = \\mathrm{{Expand}}(g) \\oplus r\\]

\\[\\Phi_j^{{(\\lambda)}} = T_\\lambda^{{-1}} \\circ \\Phi_j^{{(\\mathrm{{AQM}})}} \\circ T_\\lambda\\]

### Typed State Machine

\\[\\mathcal R_{{f4v}} = \\{{r_{{\\mathrm{{press}}}}, r_{{\\mathrm{{reflux}}}}, r_{{\\mathrm{{cascade}}}}, r_{{\\mathrm{{restart}}}}, r_{{\\mathrm{{triple}}}}, r_{{\\mathrm{{monitor}}}}, r_{{\\mathrm{{activefix}}}}\\}}\\]

\\[\\mathcal E_\\Lambda = \\{{e_{{\\mathrm{{reflux}}}}, e_{{\\mathrm{{verify}}}}, e_{{\\mathrm{{retort}}}}\\}}\\]

\\[\\delta(e_{{\\mathrm{{reflux}}}}): r_{{\\mathrm{{press}}}} \\to r_{{\\mathrm{{reflux}}}} \\to r_{{\\mathrm{{cascade}}}}\\]

\\[\\delta(e_{{\\mathrm{{verify}}}}): r_{{\\mathrm{{cascade}}}} \\to r_{{\\mathrm{{restart}}}} \\to r_{{\\mathrm{{monitor}}}} \\to r_{{\\mathrm{{activefix}}}}\\]

\\[\\delta(e_{{\\mathrm{{retort}}}}): r_{{\\mathrm{{restart}}}} \\to r_{{\\mathrm{{triple}}}} \\to r_{{\\mathrm{{monitor}}}}\\]

\\[\\rho_0 \\in \\mathcal H_{{r_{{\\mathrm{{press}}}}}}, \\qquad x_0^{{\\mathrm{{chem}}}} = \\begin{{bmatrix}} m_{{\\mathrm{{source}}}}^0 \\\\ m_{{\\mathrm{{volatile}}}}^0 \\\\ m_{{\\mathrm{{liquid}}}}^0 \\\\ 0 \\\\ 0 \\end{{bmatrix}}, \\qquad g_0 = \\mathrm{{Coll}}(\\rho_0)\\]

### Canonical AQM Line Operators

{ops}

### Paragraph Compositions

\\[\\Psi_{{P1}} = \\Phi_{{\\mathrm{{P1_4}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P1_3}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P1_2}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P1_1}}}}^{{\\mathrm{{AQM}}}}\\]

\\[\\Psi_{{P2}} = \\Phi_{{\\mathrm{{P2_6}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P2_5}}}}^{{\\mathrm{{AQM}}}}\\]

\\[\\Psi_{{P3}} = \\Phi_{{\\mathrm{{P3_14}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P3_13}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P3_12}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P3_11}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P3_10}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P3_9}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P3_8}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P3_7}}}}^{{\\mathrm{{AQM}}}}\\]

\\[\\rho_{{P1}} = \\Psi_{{P1}}(\\rho_0), \\qquad \\rho_{{P2}} = \\Psi_{{P2}}(\\rho_{{P1}}), \\qquad \\rho_* = \\Psi_{{P3}}(\\rho_{{P2}})\\]

### Invariants And Counts

\\[N_{{\\mathrm{{daiin}}}}(f4v) = 5, \\qquad N_{{\\mathrm{{union}}}}(f4v) = 1, \\qquad N_{{\\mathrm{{triple}}}}(f4v) = 1\\]

\\[N_{{\\mathrm{{refluxpair}}}}(f4v) = 1, \\qquad N_{{\\mathrm{{salt}}}}(f4v) = 0\\]

\\[\\mathrm{{Tr}}\\!\\left(\\Pi_{{\\mathrm{{monitor}}}} \\rho_*\\right) \\gg \\mathrm{{Tr}}\\!\\left(\\Pi_{{\\mathrm{{fail}}}} \\rho_*\\right), \\qquad \\mathbf{{1}}^T x_*^{{\\mathrm{{chem}}}} = \\mathbf{{1}}^T x_0^{{\\mathrm{{chem}}}}\\]

### Cross-Lens Transport

\\[\\Phi_j^{{(\\mathrm{{CUT}})}} = T_{{\\mathrm{{CUT}}}}^{{-1}} \\Phi_j^{{(\\mathrm{{AQM}})}} T_{{\\mathrm{{CUT}}}}, \\qquad \\Phi_j^{{(\\mathrm{{phys}})}} = T_{{\\mathrm{{phys}}}}^{{-1}} \\Phi_j^{{(\\mathrm{{AQM}})}} T_{{\\mathrm{{phys}}}}\\]

\\[\\Phi_j^{{(\\mathrm{{wave}})}} = T_{{\\mathrm{{wave}}}}^{{-1}} \\Phi_j^{{(\\mathrm{{AQM}})}} T_{{\\mathrm{{wave}}}}, \\qquad \\Phi_j^{{(\\mathrm{{wavemath}})}} = T_{{\\mathrm{{wavemath}}}}^{{-1}} \\Phi_j^{{(\\mathrm{{AQM}})}} T_{{\\mathrm{{wavemath}}}}\\]

\\[\\Phi_j^{{(\\lambda)}} = T_\\lambda^{{-1}} \\Phi_j^{{(\\mathrm{{AQM}})}} T_\\lambda, \\qquad \\lambda \\in \\{{\\mathrm{{CUT}}, \\mathrm{{phys}}, \\mathrm{{wave}}, \\mathrm{{wavemath}}\\}}\\]

### Folio Theorem

\\[\\rho_* = (\\Psi_{{P3}} \\circ \\Psi_{{P2}} \\circ \\Psi_{{P1}})(\\rho_0)\\]

\\[\\forall \\rho_0 \\in \\mathcal H_{{r_{{\\mathrm{{press}}}}}} : \\bigl(N_{{\\mathrm{{refluxpair}}}}=1 \\land N_{{\\mathrm{{triple}}}}=1 \\land N_{{\\mathrm{{salt}}}}=0\\bigr) \\Rightarrow \\rho_* \\in \\mathcal H_{{r_{{\\mathrm{{activefix}}}}}}\\]

\\[x_*^{{\\mathrm{{chem}}}} = \\begin{{bmatrix}} m_{{\\mathrm{{source}}}}^* \\\\ m_{{\\mathrm{{volatile}}}}^* \\\\ m_{{\\mathrm{{liquid}}}}^* \\\\ m_{{\\mathrm{{essence}}}}^* \\\\ m_{{\\mathrm{{fixed}}}}^* \\end{{bmatrix}}, \\qquad m_{{\\mathrm{{volatile}}}}^* > 0, \\qquad m_{{\\mathrm{{fixed}}}}^* > 0\\]

The formal theorem of `f4v` is therefore:

1. the page opens with double-heated pressure and a reflux reversal
2. it proves admissibility through a multi-regime completion cascade
3. it restarts under damage, then survives a triple retort under repeated checkpoints
4. it closes as an active fixed volatile without salt precipitation

## Final Draft Audit

- EVA inventory complete for all 14 visible lines
- direct literal ledger present for each line
- 16 formal math lenses populated with per-line equations
- 4 mythic lenses populated with per-line readings
- key signatures preserved explicitly: `dolds/dlod`, completion cascade, `qookoiiin`, and repeated `daiin`
- major unresolved issue preserved honestly: visual rampion/campanula remains possible, but operational evidence strongly favors rue-style volatile processing

## Plant Crystal Contribution

- checkpoint-monitored volatile station
- reflux-reversal signature
- completion cascade line
- triple-retort monitoring branch
- active volatile close without salt
"""
    ).rstrip() + "\n"


def main() -> None:
    OUTPUT.write_text(render(), encoding="utf-8")


if __name__ == "__main__":
    main()
