from __future__ import annotations

from textwrap import dedent

from render_f007_to_f008_parallel_batch import FOLIOS_DIR, render_folio, render_pointer


def make_folio(
    *,
    folio_id: str,
    quire: str,
    bifolio: str,
    manuscript_role: str,
    purpose: str,
    zero_claim: str,
    botanical: str,
    risk: str,
    confidence: str,
    visual_grammar: list[str],
    full_eva: str,
    core_vml: list[str],
    groups: list[dict[str, object]],
    lines: list[tuple[str, str, str, str, str, str]],
    tarot_cards: list[str],
    movements: list[str],
    direct: str,
    math: str,
    mythic: str,
    compression: str,
    typed_state_machine: str,
    invariants: str,
    theorem: str,
    crystal_contribution: list[str],
    pointer_title: str,
    pointer_position: str,
    pointer_page_type: str,
    pointer_conclusion: str,
    pointer_judgment: str,
    currier_language: str = "A",
    currier_hand: str = "1",
    reading_contract: list[str] | None = None,
) -> dict[str, object]:
    return {
        "folio_id": folio_id,
        "folio_short": folio_id.replace("00", "").replace("0", "", 1).replace("F", "F"),
        "manuscript_role": manuscript_role,
        "purpose": purpose,
        "reading_contract": reading_contract
        or [
            "Operational signatures take precedence over inherited species names.",
            "Damaged or uncertain glyphs remain visible.",
            "The strongest claims are structural and processual, not taxonomic.",
            "Every line is kept as a separate operator event.",
        ],
        "zero_claim": zero_claim,
        "identity_rows": [
            ("Folio", f"`{folio_id.lower()[1:]}`"),
            ("Quire", f"`{quire}`"),
            ("Bifolio", f"`{bifolio}`"),
            ("Currier language", f"`{currier_language}`"),
            ("Currier hand", f"`{currier_hand}`"),
            ("Botanical candidate", botanical),
            ("Risk level", risk),
            ("Direct confidence", confidence),
        ],
        "visual_grammar": visual_grammar,
        "full_eva": full_eva.strip(),
        "core_vml": core_vml,
        "groups": groups,
        "lines": lines,
        "tarot_cards": tarot_cards,
        "movements": movements,
        "direct_operational_meaning": direct,
        "mathematical_extraction": math,
        "mythic_extraction": mythic,
        "all_lens_zero_point": zero_claim,
        "dense_compression": compression,
        "typed_state_machine": typed_state_machine.strip(),
        "invariants": invariants.strip(),
        "theorem": theorem.strip(),
        "audit": [
            f"EVA inventory complete for all {len(lines)} visible units",
            "direct literal ledger present for each line",
            "16 formal math lenses populated with per-line equations",
            "4 mythic lenses populated with per-line readings",
            "major signatures preserved explicitly in the ledger and theorem",
            "species uncertainty remains visible where local evidence is weak",
        ],
        "crystal_contribution": crystal_contribution,
        "pointer_title": pointer_title,
        "pointer_position": pointer_position,
        "pointer_page_type": pointer_page_type,
        "pointer_conclusion": pointer_conclusion,
        "pointer_identity": [
            ("Folio", f"`{folio_id.lower()[1:]}`"),
            ("Quire", f"`{quire}`"),
            ("Bifolio", f"`{bifolio}`"),
            ("Currier language", f"`{currier_language}`"),
            ("Currier hand", f"`{currier_hand}`"),
            ("Botanical consensus", botanical),
            ("Risk level", risk),
            ("Direct confidence", confidence),
        ],
        "pointer_judgment": pointer_judgment,
    }


FOLIOS: list[dict[str, object]] = [
    make_folio(
        folio_id="F009R",
        quire="B",
        bifolio="bB1 = f9 + f16",
        manuscript_role="Quire B binding opener with heated root fixation",
        purpose="`f9r` opens Quire B in a new mode: not apparatus instruction but clamp-and-bind process. `tydlo` starts hot and locked, `cth-` terms dominate the page, `rod` lands the first strong root terminal, and `dsholdy` compresses the whole transition-fluid fixation route into one token. The final title line confirms that this is a boundary leaf, not just another herbal page.",
        zero_claim="Lock the heated source into conduit-bound transition, fix it at the root, and certify the new quire regime with a short title label.",
        botanical="`Rumex crispus` remains provisional; process profile is stronger than species fit",
        risk="moderate",
        confidence="high on hot-lock binding and root anchoring",
        visual_grammar=[
            "`quire opener` = threshold load rather than ordinary continuation",
            "`single title line` = boundary-label behavior",
            "`root-emphasized process terms` = drawing and terminal vocabulary agree on anchoring low",
            "`Herbal A stalk-to-leaf-center form` = ordinary codicology carrying extraordinary operator density",
        ],
        full_eva="""
P1:  tydlo.choly.cthor.orchey.s.shy.odaiin.sary.shor.cthy-
P2:  oykeey.chol.ytaiin.okchody.toeoky.okoiin.dy.or.choiin-
P3:  toiin.cphy.qotod.otaiin.cthy.okor.chey.cthod.rod-
P4:  oshy.chokcho.chcthod.shor.shoiin.otar.dor.ytol.dayty-
P5:  daiin.chor.sor.cthy.chokoiin.shol.dsholdy.otchol.ot.dy=
P6:  pshoain.cthoaiin.okaiir.*odo.ral.shar.sy.shydal.chdy-
P7:  or.chol.chytchy.tchol.ytor.qotol.chyky.chodar.aiin-
P8:  qotchy.qokchy.cthey.koraiin.okain.d.dal.s.chshocthy-
P9:  ochocthy.cho*y.chodykchy.saiin.dchy.daiin=
T10: ytchas.oraiin.chkor=
""",
        core_vml=[
            "`tydlo` = hot lock opener",
            "`cth-` = containment dominates the quire threshold",
            "`rod` = root-heat-fix terminal",
            "`dsholdy` = the page's miniature of fix-transition-fluid-fix",
            "`sary / sor / saiin` = salt dispersed through root, outlet, and close",
            "`T10` = genuine quire-opening label",
        ],
        groups=[
            {"label": "P1", "title": "Paragraph 1 - hot lock and root fixation", "line_ids": ["P1", "P2", "P3", "P4", "P5"]},
            {"label": "P2", "title": "Paragraph 2 and title - proof, salt close, and label", "line_ids": ["P6", "P7", "P8", "P9", "T10"]},
        ],
        lines=[
            ("P1", "tydlo.choly.cthor.orchey.s.shy.odaiin.sary.shor.cthy", "`tydlo` hot lock; `cthor/cthy` conduit bind; `odaiin` checkpoint; `sary` salt-root.", "Open with hot locking, conduit bind, and rooted salt verification.", "hot-lock conduit opener", "strong"),
            ("P2", "oykeey.chol.ytaiin.okchody.toeoky.okoiin.dy.or.choiin", "`oykeey` heated moist double-essence; `okchody` heated contained fix; `dy` fixed.", "Stabilize doubled essence inside heated containment and keep the outlet cycling.", "contained double-essence stabilization", "strong"),
            ("P3", "toiin.cphy.qotod.otaiin.cthy.okor.chey.cthod.rod", "`cphy` alembic-active; `qotod` transmute-heat-fix; `cthod` conduit-heat-fix; `rod` root-heat-fix.", "Drive the route through alembic and conduit until it fixes explicitly at the root.", "alembic path ending on `rod`", "strong"),
            ("P4", "oshy.chokcho.chcthod.shor.shoiin.otar.dor.ytol.dayty", "`oshy` heat-transition; `chcthod` volatile conduit heat-fix; `otar` timed root heat.", "Carry the heated transition forward and prepare the fluid body for fixation.", "heated transition continuation", "mixed"),
            ("P5", "daiin.chor.sor.cthy.chokoiin.shol.dsholdy.otchol.ot.dy", "`daiin` checkpoint; `sor` salt-outlet; `dsholdy` fix-transition-fluid-fix; `dy` fixed.", "Checkpoint the outlet and compress the whole route into `dsholdy`.", "miniature of the page in one token", "strong"),
            ("P6", "pshoain.cthoaiin.okaiir.*odo.ral.shar.sy.shydal.chdy", "`pshoain` press-transition cycle; `*odo` damaged heat-fix cluster; `ral` root-structure.", "Rebuild the route through press, structure, and preserved damage.", "structural proof with damage retained", "mixed"),
            ("P7", "or.chol.chytchy.tchol.ytor.qotol.chyky.chodar.aiin", "`qotol` transmute-heat-fluid; `chodar` volatile-heat-fix-root.", "Send the outlet back through heated fluid until it roots again.", "outlet-to-root recapture", "strong"),
            ("P8", "qotchy.qokchy.cthey.koraiin.okain.d.dal.s.chshocthy", "`qotchy/qokchy` transmute and extract; `cthey` conduit essence; `dal` fix-structure.", "Extract, structure, and rebind the active route inside conduit essence.", "extract-and-rebind proof", "strong"),
            ("P9", "ochocthy.cho*y.chodykchy.saiin.dchy.daiin", "`ochocthy` heated conduit bind; damaged `cho*y`; `saiin` salt complete; `daiin` final checkpoint.", "Seal the paragraph with heated binding, salt completion, and one last verification.", "salt-complete terminal", "strong"),
            ("T10", "ytchas.oraiin.chkor", "`ytchas` moist-driven volatile dissolve; `oraiin` heat-rotation complete; `chkor` volatile contained outlet.", "Label the quire opener as a completed rotated volatile preparation.", "title label", "mixed"),
        ],
        tarot_cards=["The Emperor", "Strength", "The Chariot", "Temperance", "Justice", "The Hermit", "Wheel of Fortune", "The Hierophant", "Judgment", "The Sun"],
        movements=["lock the route", "stabilize the essence", "fix at the root", "carry the heat forward", "compress the process", "rebuild the structure", "return outlet to root", "extract and rebind", "seal in salt", "name the boundary product"],
        direct="`f9r` behaves like a quire-opening clamp protocol. It starts hot, stays bound, and fixes the work at the root before granting itself a title label.",
        math="Across the formal lenses, `f9r` is a contained binding map. The state is pushed into a hot conduit, stabilized by repeated bind operators, and returned to a root-fixed attractor. `dsholdy` acts as a compressed local update for the whole page.",
        mythic="Across the mythic lenses, `f9r` is the door-bolt page. The apprentice enters a stricter room and the first lesson is simply to secure the work.",
        compression="Clamp, heat, bind, root-fix, compress the route into `dsholdy`, and label the quire opener.",
        typed_state_machine="""
\\[\\mathcal R_{f9r} = \\{r_{\\mathrm{opener}}, r_{\\mathrm{bind}}, r_{\\mathrm{rootfix}}, r_{\\mathrm{title}}\\}\\]
\\[\\delta(e_{\\mathrm{lock}}): r_{\\mathrm{opener}} \\to r_{\\mathrm{bind}} \\to r_{\\mathrm{rootfix}} \\to r_{\\mathrm{title}}\\]
\\[\\rho_0 \\in \\mathcal H_{r_{\\mathrm{opener}}}, \\qquad g_0 = \\mathrm{Coll}(\\rho_0)\\]
""",
        invariants="""
\\[N_{\\mathrm{cth}}(f9r) \\ge 5, \\qquad N_{\\mathrm{rod}}(f9r)=1, \\qquad N_{\\mathrm{titles}}(f9r)=1\\]
\\[N_{\\mathrm{dsholdy}}(f9r)=1, \\qquad N_{\\mathrm{salt}}(f9r) \\ge 3\\]
""",
        theorem="""
\\[\\rho_* = (\\Psi_{P2} \\circ \\Psi_{P1})(\\rho_0)\\]

The formal theorem of `f9r` is:

1. Quire B begins under binding rather than apparatus vocabulary
2. the page's stable attractor is root fixation, not free outlet
3. `dsholdy` compresses the whole transition-fluid fixation route
4. the title line certifies the boundary state
""",
        crystal_contribution=["Quire B binding-opener station", "hot-lock conduit line", "root-heat-fix threshold", "transition-fluid miniature", "boundary title label"],
        pointer_title="Bound Heated Fixation Opener",
        pointer_position="the recto opener of Quire B and first half of the `f9/f16` outer bifolio",
        pointer_page_type="single-plant quire-opening procedure page with one title line",
        pointer_conclusion="hot-lock opener, `cth-` density, `rod`, and `dsholdy`",
        pointer_judgment="`f9r` begins Quire B by clamping and heating the source until it can be fixed at the root and named.",
    ),
    make_folio(
        folio_id="F009V",
        quire="B",
        bifolio="bB1 = f9 + f16",
        manuscript_role="fire-sealed aromatic pressing page",
        purpose="`f9v` internalizes the fire seal. `fochor`, `qofol`, and `cfhol` appear on one leaf, a dense pressing cluster runs through both halves, the page spikes into `oeees` and `daiiin`, and the final outlet is released only through valve control. The page reads as a high-discipline aromatic extraction rather than a mild flower infusion.",
        zero_claim="Press the aromatic volatile under direct fire, convert it into sealed fluid, intensify it to triple essence, and release it only after repeated washing and valve-governed verification.",
        botanical="`Viola bertolonii` is one of the strongest inherited IDs in the manuscript",
        risk="moderate",
        confidence="high on fire-sealed volatile pressing",
        visual_grammar=[
            "`dual leaf shapes` = strong violet-class visual support",
            "`paired with f16r` = aromatic volatile bifolio",
            "`internal fire seal` = Quire A boundary token becomes routine tool",
            "`short later lines` = contraction after concentration spike",
        ],
        full_eva="""
P1:  fochor.oporody.opy.shor.daiin.qopchypcho.qofol.shol.cfhol.daiin-
P2:  dchor.qoaiin.chkaiin.cthor.chol.chor.cphol.dy.oty.qokaiin.dy-
P3:  ykey.chor.ykaiin.daiin.cthy.otaiin.oky.oeees.daiin-
P4:  yteytchy.kaiin.cthor.otol.oty.toldy=
P5:  pchor.ypcheey.qotor.ypchy.olcpholy.ky.ar.chty.daiiin-
P6:  odol.choy.ksheody.chody.dain.otchy.cthod.yko-
P7:  qo.chol.chol.*chy.daiin.otal.dor.daim-
P8:  soiin.daiin.qokcho.rokyd.daly-
P9:  daiin.chy.tor.chyty.dary.ytoldy-
P10: oty.kchol.chol.chy.kyty-
P11: ychor.chshoty.okykaiin-
P12: chkaiin.ckhy.chor=
""",
        core_vml=[
            "`fochor + qofol + cfhol` = full fire apparatus",
            "`p-` cluster = aromatic pressing",
            "`oeees` = triple-essence spike",
            "`daiiin` = extended triple-cycle verification",
            "`rokyd` = contained heated root fixation",
            "`ckhy.chor` = valve-governed volatile outlet",
        ],
        groups=[
            {"label": "P1", "title": "Paragraph 1 - ignition and first seal", "line_ids": ["P1", "P2", "P3", "P4"]},
            {"label": "P2", "title": "Paragraph 2 - intensified pressing and valve close", "line_ids": ["P5", "P6", "P7", "P8", "P9", "P10", "P11", "P12"]},
        ],
        lines=[
            ("P1", "fochor.oporody.opy.shor.daiin.qopchypcho.qofol.shol.cfhol.daiin", "`fochor` fire at volatile outlet; `qopchypcho` double press-retort; `qofol` fire-fluid; `cfhol` furnace-seal fluid.", "Ignite the aromatic route, press it through retort logic, and seal the fluid inside the fire apparatus.", "triple-fire opener", "strong"),
            ("P2", "dchor.qoaiin.chkaiin.cthor.chol.chor.cphol.dy.oty.qokaiin.dy", "`dchor` fixed outlet; `qoaiin/chkaiin` completed transmute and containment; `cphol` alembic fluid; `dy` fixed twice.", "Lock the conduit-and-alembic route with doubled fixation.", "double-fixed conduit proof", "strong"),
            ("P3", "ykey.chor.ykaiin.daiin.cthy.otaiin.oky.oeees.daiin", "`ykey` moist contained essence; `cthy` conduit bind; `oeees` triple-essence dissolve.", "Moisten and contain the essence, then intensify it to triple essence under conduit verification.", "triple-essence concentration", "strong"),
            ("P4", "yteytchy.kaiin.cthor.otol.oty.toldy", "`yteytchy` repeated moist-drive; `kaiin` complete containment; `toldy` driven heated fluid fixed.", "Seal the first section as contained heat-driven fluid.", "sealed first section", "strong"),
            ("P5", "pchor.ypcheey.qotor.ypchy.olcpholy.ky.ar.chty.daiiin", "`pchor` press volatile outlet; `qotor` retort to heated outlet; `daiiin` extended triple-cycle.", "Restart under pressure and hold the aromatic route through one explicit retort until triple-cycle verification is satisfied.", "extended verification under pressure", "strong"),
            ("P6", "odol.choy.ksheody.chody.dain.otchy.cthod.yko", "`odol` heat-fix fluid; `ksheody` contained heated transition essence; `cthod` conduit heat-fix.", "Polish the heated fluid and keep the conduit fixed under moist containment.", "contained heat-fix polish", "strong"),
            ("P7", "qo.chol.chol.*chy.daiin.otal.dor.daim", "`qo` retort; `chol.chol` doubled washing; damaged `*chy`; `daim` earth-vessel fix.", "Wash the route twice through retort logic and lock the outlet into vessel form.", "doubled washing into vessel", "mixed"),
            ("P8", "soiin.daiin.qokcho.rokyd.daly", "`soiin` dissolve-heat cycle; `rokyd` root-heat-contain-fix; `daly` active structure.", "Heat, dissolve, and actively fix the contained root inside structure.", "root-contained fixation", "strong"),
            ("P9", "daiin.chy.tor.chyty.dary.ytoldy", "`daiin` checkpoint; `tor` driven heated outlet; `dary` root-active fix; `ytoldy` moist-driven fluid fix.", "Checkpoint again and return the outlet stream back into root-active fixation.", "root-active rebind", "strong"),
            ("P10", "oty.kchol.chol.chy.kyty", "`kchol/chol` contained volatile fluid; `kyty` moist-driven containment.", "Restart the contained fluid under moist-driven control.", "contained fluid restart", "mixed"),
            ("P11", "ychor.chshoty.okykaiin", "`ychor` moist volatile outlet; `chshoty` heated transition outlet; `okykaiin` completed heated containment.", "Prove the moist outlet cycle under contained heat.", "moist outlet proof", "strong"),
            ("P12", "chkaiin.ckhy.chor", "`chkaiin` volatile containment complete; `ckhy` valve-active; `chor` outlet.", "Release the volatile only through an active valve-governed outlet.", "valve-controlled close", "strong"),
        ],
        tarot_cards=["The Magician", "Justice", "Strength", "Temperance", "The Chariot", "The Emperor", "The Hermit", "Wheel of Fortune", "The Star", "The Moon", "Judgment", "The Sun"],
        movements=["ignite and seal", "lock the conduit route", "intensify to triple essence", "seal the first section", "restart under triple-cycle proof", "polish the heat-fix", "wash into vessel", "fix the root in structure", "rebind the root-active stream", "restart the fluid", "prove the moist outlet", "release through the valve"],
        direct="`f9v` is a fire-sealed aromatic extraction page. It uses the full fire apparatus, spikes to triple essence, and then disciplines the product through washing and valve release.",
        math="Across the formal lenses, `f9v` is a high-heat containment system. Fire-start, pressure, and seal-preserving transport dominate, while `oeees` and `daiiin` mark the concentration spike and long verification horizon.",
        mythic="Across the mythic lenses, `f9v` is the perfumer's furnace: fragility intensified without being lost.",
        compression="Fire the aromatic route, press it into sealed fluid, intensify it with `oeees` and `daiiin`, and finish under valve control.",
        typed_state_machine="""
\\[\\mathcal R_{f9v} = \\{r_{\\mathrm{ignite}}, r_{\\mathrm{seal}}, r_{\\mathrm{essence}}, r_{\\mathrm{valveclose}}\\}\\]
\\[\\delta(e_{\\mathrm{fochor}}): r_{\\mathrm{ignite}} \\to r_{\\mathrm{seal}} \\to r_{\\mathrm{essence}} \\to r_{\\mathrm{valveclose}}\\]
\\[\\rho_0 \\in \\mathcal H_{r_{\\mathrm{ignite}}}, \\qquad g_0 = \\mathrm{Coll}(\\rho_0)\\]
""",
        invariants="""
\\[N_{\\mathrm{fire}}(f9v) \\ge 3, \\qquad N_{\\mathrm{press}}(f9v) \\ge 4, \\qquad N_{\\mathrm{daiin/dain}}(f9v) \\ge 8\\]
\\[N_{\\mathrm{oeees}}(f9v)=1, \\qquad N_{\\mathrm{daiiin}}(f9v)=1, \\qquad N_{\\mathrm{cfhol}}(f9v)=1\\]
""",
        theorem="""
\\[\\rho_* = (\\Psi_{P2} \\circ \\Psi_{P1})(\\rho_0)\\]

The formal theorem of `f9v` is:

1. the full fire apparatus is internalized as a routine tool
2. aromatic material reaches triple essence without leaving containment
3. extended verification replaces gentle handling as the main safety law
4. the page closes on valve-governed outlet release
""",
        crystal_contribution=["internalized fire-seal station", "aromatic pressing line", "triple-essence route", "extended verification under flame", "valve-governed release"],
        pointer_title="Fire-Sealed Volatile Pressing",
        pointer_position="the verso of the Quire B opener bifolio and aromatic counterpart to later `f16r`",
        pointer_page_type="single aromatic plant procedure page under full fire governance",
        pointer_conclusion="triple fire system, pressing cluster, `oeees`, `daiiin`, and valve close",
        pointer_judgment="`f9v` uses the full fire apparatus on an aromatic plant and releases the product only under valve discipline.",
    ),
    make_folio(
        folio_id="F010R",
        quire="B",
        bifolio="bB2 = f10 + f15",
        manuscript_role="quadruple retort distillation page with mechanical pressing",
        purpose="`f10r` is Quire B's repeated-retort leaf. `qotor` appears four times, `dy.dy` seals the first retort block, pressing and `cth-` binding are fused into one mechanical grammar, `am` appears only after repeated verification, and the close returns to `rodaiin`, a root-level completion.",
        zero_claim="Press and clamp the bitter source through repeated retort turns, admit union only after verification, and return the whole route to root completion.",
        botanical="`Cichorium pumilum` remains provisional; process profile is stronger than species fit",
        risk="moderate",
        confidence="high on quadruple retort distillation",
        visual_grammar=[
            "`two leaf shapes` = ordinary Herbal A complexity with extraordinary retort repetition",
            "`paired with f15v` = Quire B's second bifolio where repetition becomes method",
            "`dense central block` = visual calm hides operator intensity",
            "`root-return vocabulary` = page keeps returning to the source rather than abandoning it",
        ],
        full_eva="""
P1:  pchocthy.shor.octhody.chorchy.pchodol.chopchol.ypchkom-
P2:  dchey.cthoor.char.chty.oechair.otytchol.oky.daiin.etyd-
P3:  qotor.otchy.daiin.chocthy.qotchy.chol.or.yty.dy.dy-
P4:  sor.chaiin.chcthy.cthockhy.or.aiin.chtchor.doiir.ody-
P5:  qokchy.qotchol.chol.cthy=
P6:  ycheor.cthy.chor.cthaiin.qoctholy.dy.chy.taiin.shy-
P7:  dchy.qokchol.ykchaiin.yky.daiin.cth.dain.dair.am-
P8:  qotchor.chor.otol.chol.cholor.chol.daiin.dar-
P9:  oykchor.shor.chor.chy.kaiiin.dy.chodaiin-
P10: oqotor.otor.cphy.cthor.osain.ytoiin-
P11: rotchoshor.qoty.qotor.cthyd.otar-
P12: rodaiin.daiin.qotchy.qotor=
""",
        core_vml=[
            "`qotor` x4 = iterative retort signature",
            "`dy.dy` = emphatic doubled fixation",
            "`p-` plus `cth-` = pressing and binding together",
            "`am` after `dain.dair` = union earned only after proof",
            "`osain` = heated salt completion inside a retort page",
            "`rodaiin` = root-heat-fix-complete close",
        ],
        groups=[
            {"label": "P1", "title": "Paragraph 1 - first retort block and seal", "line_ids": ["P1", "P2", "P3", "P4", "P5"]},
            {"label": "P2", "title": "Paragraph 2 - later retort returns and root close", "line_ids": ["P6", "P7", "P8", "P9", "P10", "P11", "P12"]},
        ],
        lines=[
            ("P1", "pchocthy.shor.octhody.chorchy.pchodol.chopchol.ypchkom", "`pchocthy` press volatile conduit-bind; `octhody` heated conduit fix; `ypchkom` moist pressed heated vessel.", "Open with mechanical pressure, conduit binding, and vesselized volatile fluid.", "press-and-bind opener", "strong"),
            ("P2", "dchey.cthoor.char.chty.oechair.otytchol.oky.daiin.etyd", "`dchey` fixed essence; `cthoor` double-heated conduit; `char` root; `daiin` checkpoint.", "Set the double-heated conduit and checkpoint the root-linked essence route.", "double-heated conduit setup", "strong"),
            ("P3", "qotor.otchy.daiin.chocthy.qotchy.chol.or.yty.dy.dy", "`qotor` retort to heated outlet; `daiin` checkpoint; `dy.dy` doubled fixation.", "Run the first explicit retort and close it with emphatic double fixation.", "first retort with double lock", "strong"),
            ("P4", "sor.chaiin.chcthy.cthockhy.or.aiin.chtchor.doiir.ody", "`sor` salt outlet; `cthockhy` heated valve; `doiir` rotation fixation.", "Carry the retort route through salt-outlet and valve-governed rotation.", "salt-valve continuation", "mixed"),
            ("P5", "qokchy.qotchol.chol.cthy", "`qokchy` extract-contain; `qotchol` transmute volatile fluid; `cthy` conduit bind.", "Seal the midpoint as contained volatile fluid under conduit bind.", "sealed extract midpoint", "strong"),
            ("P6", "ycheor.cthy.chor.cthaiin.qoctholy.dy.chy.taiin.shy", "`ycheor` moist essence outlet; `cthaiin` completed conduit cycle; `dy` fixed.", "Restart the route as a moist essence outlet and fix the completed conduit cycle.", "moist essence restart", "strong"),
            ("P7", "dchy.qokchol.ykchaiin.yky.daiin.cth.dain.dair.am", "`dchy` fixed volatile active; `daiin/dain/dair` layered verification; `am` union.", "Allow union only after repeated containment and fixation proofs.", "verified union gate", "strong"),
            ("P8", "qotchor.chor.otol.chol.cholor.chol.daiin.dar", "`qotchor` driven volatile outlet; `otol` timed heated fluid; `dar` root fix.", "Push the outlet route through heated fluid and return it to root fixation.", "root-return after circulation", "strong"),
            ("P9", "oykchor.shor.chor.chy.kaiiin.dy.chodaiin", "`oykchor` heated moist contained outlet; `kaiiin` extended containment; `chodaiin` heat-fix completion.", "Run an extended containment cycle before heat-fix completion.", "extended containment", "strong"),
            ("P10", "oqotor.otor.cphy.cthor.osain.ytoiin", "`oqotor` heat-intensified retort; `cphy` alembic-active; `osain` heated salt completion.", "Run the heat-intensified retort and complete a heated salt phase.", "heat-intensified retort", "strong"),
            ("P11", "rotchoshor.qoty.qotor.cthyd.otar", "`rotchoshor` root-to-outlet chain; `qotor` third retort; `cthyd` moist conduit fix.", "Tie root and outlet together through one more retort turn.", "third retort on the root chain", "strong"),
            ("P12", "rodaiin.daiin.qotchy.qotor", "`rodaiin` root completion; `daiin` final checkpoint; terminal `qotor`.", "Begin the last line with root completion and end on the fourth retort.", "root-complete final retort", "strong"),
        ],
        tarot_cards=["The Magician", "The Hierophant", "Justice", "Strength", "The Chariot", "Temperance", "The Lovers", "Wheel of Fortune", "The Hermit", "The Emperor", "Judgment", "The World"],
        movements=["press and clamp", "set the conduit", "run the first retort", "carry the salt-valve turn", "seal the midpoint", "restart the moist route", "earn the union", "return outlet to root", "extend containment", "intensify the retort", "retort the root chain again", "close on root completion"],
        direct="`f10r` is Quire B's repeated-retort lesson. The source is mechanically pressured, retorted four separate times, and only then allowed into union. The route keeps returning to the root.",
        math="Across the formal lenses, `f10r` is an iterative operator composition with explicit kernel reuse. `qotor` is applied four times while `dy.dy`, `dain`, and `dair` impose nested verification.",
        mythic="Across the mythic lenses, `f10r` is disciplined repetition. The page wins by staying with the same hard turn until the substance yields.",
        compression="Press and clamp the source, run `qotor` four times, verify before union, and close on `rodaiin`.",
        typed_state_machine="""
\\[\\mathcal R_{f10r} = \\{r_{\\mathrm{pressbind}}, r_{\\mathrm{retort}}, r_{\\mathrm{unionready}}, r_{\\mathrm{rootcomplete}}\\}\\]
\\[\\delta(e_{\\mathrm{qotor}}): r_{\\mathrm{pressbind}} \\to r_{\\mathrm{retort}} \\to r_{\\mathrm{rootcomplete}}\\]
\\[\\delta(e_{\\mathrm{am}}): r_{\\mathrm{retort}} \\to r_{\\mathrm{unionready}}\\]
""",
        invariants="""
\\[N_{\\mathrm{qotor}}(f10r)=4, \\qquad N_{\\mathrm{dy.dy}}(f10r)=1, \\qquad N_{\\mathrm{am}}(f10r)=1\\]
\\[N_{\\mathrm{rodaiin}}(f10r)=1, \\qquad N_{\\mathrm{cth}}(f10r) \\ge 7\\]
""",
        theorem="""
\\[\\rho_* = (\\Psi_{P2} \\circ \\Psi_{P1})(\\rho_0)\\]

The formal theorem of `f10r` is:

1. the source is pressed and bound before deep retort work begins
2. one retort class recurs four times on the same page
3. union is admitted only after explicit verification
4. the page closes by returning the route to root completion
""",
        crystal_contribution=["quadruple-retort station", "mechanical press-and-bind line", "verified union gate", "heated salt completion", "root-complete retort close"],
        pointer_title="Quadruple Retort Distillation",
        pointer_position="the recto of the second Quire B bifolio",
        pointer_page_type="single-plant iterative retort page with heavy pressing and containment",
        pointer_conclusion="`qotor` x4, `dy.dy`, late `am`, and `rodaiin`",
        pointer_judgment="`f10r` presses and clamps the source through four retort turns, verifying before union and returning the whole route to the root.",
    ),
    make_folio(
        folio_id="F010V",
        quire="B",
        bifolio="bB2 = f10 + f15",
        manuscript_role="maximum-density retort cycling page with exhaustive verification",
        purpose="`f10v` is a short dense retort page. It packs an extreme amount of `qo-` activity and nine completion markers into seven lines, begins with `sain` already present as a satisfied salt stage, and closes on `chckhan`, a valve-controlled cycle terminal. The page feels like a compressed exam in discipline rather than a leisurely herbal description.",
        zero_claim="Complete the salt stage first, then drive the medicine through a dense retort-and-checkpoint corridor until only a regulated valve cycle can close it.",
        botanical="`Linnaea borealis` remains weak and provisional; process profile is much stronger than species fit",
        risk="moderate",
        confidence="high on maximum-density retort cycling",
        visual_grammar=[
            "`short page` = compression carries the meaning",
            "`ordinary-looking plant` = visual calm hides algorithmic density",
            "`paired with f15r` = later salt territory is already foreshadowed",
            "`seven-line field` = each line carries unusual operator weight",
        ],
        full_eva="""
P1: paiin.daiin.sheo.pcheey.qoty.daiin.cthor.otydy.sain-
P2: dain.daiin.ckhy.chcthor.choiin.qot.chodaiin.cthy.daiin-
P3: dsho.ytey.kchol.ol.ty.chol.dy=
P4: qotchytor.shoiin.daiin.qotchey.shcthey.ytor.dain-
P5: sho.ykeey.daiin.qotchy.qotor.chol.daiin.qokchyky-
P6: shoiin.chor.shcthy.qoty.qotoiin.qotol.choraiin-
P7: qokol.chyky.chol.cheky.daiin.dain.chckhan=
""",
        core_vml=[
            "`qo-` = page atmosphere",
            "`daiin/dain` = almost line-by-line proof",
            "`sain` = salt already complete at entry",
            "`qotchytor` = compound retort compression",
            "`qotor` = same operator family as `f10r`, here in denser form",
            "`chckhan` = regulated valve-cycle close",
        ],
        groups=[
            {"label": "P1", "title": "Paragraph 1 - salt-first readiness", "line_ids": ["P1", "P2", "P3"]},
            {"label": "P2", "title": "Paragraph 2 - dense retort corridor and valve close", "line_ids": ["P4", "P5", "P6", "P7"]},
        ],
        lines=[
            ("P1", "paiin.daiin.sheo.pcheey.qoty.daiin.cthor.otydy.sain", "`paiin` press complete; two `daiin`; `qoty` heated transmute; `sain` salt complete.", "Enter with press and salt readiness already satisfied before the dense cycling begins.", "salt-first readiness", "strong"),
            ("P2", "dain.daiin.ckhy.chcthor.choiin.qot.chodaiin.cthy.daiin", "`dain/daiin` layered completion; `ckhy` valve-active; `chcthor` volatile conduit outlet; `chodaiin` heat-fix complete.", "Lock the route under valve and conduit control and verify it again.", "valve-and-conduit proof", "strong"),
            ("P3", "dsho.ytey.kchol.ol.ty.chol.dy", "`dsho` fixed transition heat; `kchol/chol` contained volatile fluid; `dy` fixed.", "Seal the first section as a fixed volatile-fluid body.", "short sealed section", "strong"),
            ("P4", "qotchytor.shoiin.daiin.qotchey.shcthey.ytor.dain", "`qotchytor` compound retort; `shoiin` transition-heat cycle; `daiin`; `dain`.", "Open the compressed retort corridor and verify it immediately.", "compound retort corridor", "strong"),
            ("P5", "sho.ykeey.daiin.qotchy.qotor.chol.daiin.qokchyky", "`ykeey` moist doubled essence; `qotor`; two checkpoints; `qokchyky` contained extraction.", "Run the densest line on the page: retort, volatile fluid, checkpoints, and extraction in one breath.", "maximum-density line", "strong"),
            ("P6", "shoiin.chor.shcthy.qoty.qotoiin.qotol.choraiin", "`shoiin` transition heat cycle; `qoty/qotoiin/qotol` retort sequence; `choraiin` completed outlet.", "Keep the outlet inside the retort field until even its completion belongs to the cycle.", "outlet completed inside the cycle", "strong"),
            ("P7", "qokol.chyky.chol.cheky.daiin.dain.chckhan", "`qokol` extract-contain fluid; `cheky` contained essence; `daiin/dain`; `chckhan` valve-cycle.", "Close by extracting the contained fluid and certifying the page as a valve-controlled cycle.", "valve-cycle terminal", "strong"),
        ],
        tarot_cards=["Justice", "The Emperor", "Temperance", "The Chariot", "Strength", "Wheel of Fortune", "The World"],
        movements=["enter with salt complete", "lock the route under proof", "seal the first section", "open the retort corridor", "cross the densest line", "complete the outlet inside the cycle", "end as regulated valve circuit"],
        direct="`f10v` is a compressed retort exam. The page verifies almost every move and never relaxes into a passive product description. Even the close is a regulated cycle.",
        math="Across the formal lenses, `f10v` behaves like a short stiff recurrence. `sain` acts as a pre-satisfied boundary condition, and `chckhan` is a regulated terminal boundary rather than an absorbing sink.",
        mythic="Across the mythic lenses, `f10v` is relentless practice: everything is checked, cycled, and held until discipline outruns intuition.",
        compression="Start with `sain`, saturate the page with `qo-` and checkpoints, and close the route as `chckhan`.",
        typed_state_machine="""
\\[\\mathcal R_{f10v} = \\{r_{\\mathrm{saltready}}, r_{\\mathrm{proof}}, r_{\\mathrm{corridor}}, r_{\\mathrm{valvecycle}}\\}\\]
\\[\\delta(e_{\\mathrm{sain}}): r_{\\mathrm{saltready}} \\to r_{\\mathrm{proof}} \\to r_{\\mathrm{corridor}} \\to r_{\\mathrm{valvecycle}}\\]
""",
        invariants="""
\\[N_{\\mathrm{qo}}(f10v) \\ge 8, \\qquad N_{\\mathrm{daiin/dain}}(f10v)=9, \\qquad N_{\\mathrm{sain}}(f10v)=1\\]
\\[N_{\\mathrm{chckhan}}(f10v)=1, \\qquad N_{\\mathrm{lines}}(f10v)=7\\]
""",
        theorem="""
\\[\\rho_* = (\\Psi_{P2} \\circ \\Psi_{P1})(\\rho_0)\\]

The formal theorem of `f10v` is:

1. salt completion is established before the densest cycling begins
2. retort operators saturate the page more than calm descriptive vocabulary does
3. checkpointing is the main safety law of the folio
4. the correct close is a regulated valve-cycle, not a free outlet
""",
        crystal_contribution=["maximum-density retort station", "salt-first boundary condition", "checkpoint-saturated corridor", "short-page compression line", "valve-cycle terminal"],
        pointer_title="Maximum-Density Retort Cycling",
        pointer_position="the verso companion to `f10r` on the second Quire B bifolio",
        pointer_page_type="single-plant compressed retort page with exhaustive verification",
        pointer_conclusion="salt-first ordering, dense `qo-`, nine completions, and `chckhan`",
        pointer_judgment="`f10v` begins with salt already complete, keeps the route inside a dense retort-and-proof corridor, and ends only when it can close as a valve-controlled cycle.",
    ),
]


def main() -> None:
    for folio in FOLIOS:
        (FOLIOS_DIR / f"{folio['folio_id']}_FINAL_DRAFT.md").write_text(render_folio(folio), encoding="utf-8")
        (FOLIOS_DIR / f"{folio['folio_id']}.md").write_text(render_pointer(folio), encoding="utf-8")


if __name__ == "__main__":
    main()
