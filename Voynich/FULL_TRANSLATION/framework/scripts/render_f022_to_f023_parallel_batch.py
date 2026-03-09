from __future__ import annotations

from render_f007_to_f008_parallel_batch import FOLIOS_DIR, render_folio, render_pointer
from render_f009_to_f010_parallel_batch import make_folio


FOLIOS: list[dict[str, object]] = [
    make_folio(
        folio_id="F022R",
        quire="C",
        bifolio="bC3 = f19 + f22",
        manuscript_role="ritual-precision sacred-herb page with completion on every line and one active fire-seal threshold",
        purpose="`f22r` is one of the most overtly checkpointed folios in early Book I. The page keeps completion grammar active across all thirteen lines, opens with an already ritualized press-fluid-fire arrangement, and only later introduces the unique `cfhy` active fire-seal form once the route is fully stabilized. The close is equally explicit: `oldam` gives fluid-fix-union-vessel, `dom` names the vessel terminal, and `daiin.ydaiin` proves the final product in both dry and moist states. The local corpus is right to read this page as a precise sacred-herb preparation rather than a casual plant note.",
        zero_claim="Move the vervain-class sacred herb through completion-saturated preparation, keep every phase ritually verified, introduce active fire seal only after the corridor is stable, and close by fixing the united fluid body in vessel plus dual-state proof.",
        botanical="`Verbena officinalis` / vervain / holy herb remains the strongest local identification because the folio reads like a ritualized preparation rather than a merely botanical note",
        risk="moderate",
        confidence="high on completion-saturated sacred-herb preparation and active fire-seal handling",
        visual_grammar=[
            "`13 completions in 13 lines` = verification is the dominant law of the page",
            "`three expanding paragraphs` = P1-3, P4-6, and P7-13 behave as staged operational corridors",
            "`single `cfhy` threshold` = active fire seal appears only after the page is already stabilized",
            "``dom` and `oldam`` = the page visibly cares about vessel finish, not only intermediate transformation",
        ],
        full_eva="""
P1: pol.olshy.fcholy.shol.dpchy.oty.okoly.daiin.opchy.s.ocphy-
P2: ol.aiin.shol.o.kor.qokchol.daiin.okaiin.cthor.dain.ckhy.dom-
P3: qokol.dykaiin.okchy.daiin.cthol.ctholo.dar.shain=
P4: pchaiin.okchy.daiin.cfhy.doroiin.ypchol.sy.schor.daiin-
P5: ol.daiin.qokchy.dar.daiin.chor.oldor.oky.y.choldchy-
P6: y.chokshchy.cthan=
P7: kchol.shol.dsheor.*.chdoly.ytaiin.ol.otchy.cphal-
P8: dchor.oty.daiin.ctholy.qoky.chotaiin.chocthy.do*iin.dchor-
P9: odaiin.dain.cthy.ctheor.o*aiino=
P10: kchol.chor.daiin.cthoiin.dchor.chey.qokol.dy.opchol.oldam-
P11: doiin.yckhody.qokchy.oky.otoldy.yty.dol.or.dochy.daiin-
P12: odchaiin.cthy.okchy.kchy.dchol.daiin.ydaiin-
P13: dchor.dy.dain.qockhy.ykol.okain=
""",
        core_vml=[
            "`13 completions in 13 lines` = verification is the dominant law of the page",
            "`cfhy` = unique active fire-seal threshold introduced only after prior stabilization",
            "`dom` = explicit vessel terminal early in the first paragraph",
            "`oldam` = fluid-fix-union-vessel close near the end of the page",
            "`daiin.ydaiin` = dry and moist completion proved back-to-back",
            "`cthan` = conduit-completion seal marking the end of the second paragraph",
        ],
        groups=[
            {"label": "P1", "title": "Paragraph 1 - ritual opening, vessel set, and first completion field", "line_ids": ["P1", "P2", "P3"]},
            {"label": "P2", "title": "Paragraph 2 - active fire-seal threshold and conduit completion", "line_ids": ["P4", "P5", "P6"]},
            {"label": "P3", "title": "Paragraph 3 - expanded sacred-herb corridor, vessel union, and dual-state proof", "line_ids": ["P7", "P8", "P9", "P10", "P11", "P12", "P13"]},
        ],
        lines=[
            ("P1", "pol.olshy.fcholy.shol.dpchy.oty.okoly.daiin.opchy.s.ocphy", "`pol` presses fluid; `olshy/shol` transition-fluid field; `fcholy` embeds fire inside volatile fluid; `dpchy` fixed pressed volatile; `okoly` contained fluid; `daiin`; `opchy`; `s`; `ocphy` alembic-active.", "Open by ritual pressing and fluid transition, but immediately keep the fire-bearing volatile inside containment and alembic law.", "ritual press-fluid opener", "strong"),
            ("P2", "ol.aiin.shol.o.kor.qokchol.daiin.okaiin.cthor.dain.ckhy.dom", "`ol.aiin` fluid completion; `qokchol` extracted contained volatile fluid; `okaiin` completed containment; `cthor` conduit-outlet bind; `ckhy` valve-active; `dom` vessel.", "The second line proves that the sacred route is not abstract devotion: it is already being fixed into conduit, valve, and vessel form.", "vessel-and-valve early set", "strong"),
            ("P3", "qokol.dykaiin.okchy.daiin.cthol.ctholo.dar.shain", "`qokol` transmuted heated fluid; `dykaiin` fixed moist containment complete; `okchy` heated contained volatile; `cthol/ctholo` conduit-fluid pair; `dar` root fix; `shain` transition completion.", "Finish the first paragraph by rooting the fluid-conduit route and certifying it as a completed transition rather than a loose extract.", "rooted conduit-fluid seal", "strong"),
            ("P4", "pchaiin.okchy.daiin.cfhy.doroiin.ypchol.sy.schor.daiin", "`pchaiin` pressed volatile completion; `okchy`; `daiin`; `cfhy` active fire seal; `doroiin` fixed outlet-cycle; `ypchol` moist pressed volatile fluid; `sy`; `schor`; final `daiin`.", "Only after strong completion grammar is already established does the folio admit the active fire-seal token `cfhy`.", "active fire-seal threshold", "strong"),
            ("P5", "ol.daiin.qokchy.dar.daiin.chor.oldor.oky.y.choldchy", "`ol`; `daiin`; `qokchy` extracted contained volatile active; `dar`; another `daiin`; `chor`; `oldor` fluid-fixed outlet root; `oky`; `y`; `choldchy` volatile-fluid-fix active.", "The fifth line forces extraction, root fixation, outlet, and fluid-fix grammar into one corridor, showing how the fire-sealed route is immediately re-anchored.", "re-anchored active corridor", "strong"),
            ("P6", "y.chokshchy.cthan", "`y` moist activation; `chokshchy` contained volatile-heat transition active; `cthan` conduit completion.", "Seal the second paragraph quickly: the dangerous middle is acceptable only if it ends in conduit completion.", "conduit-completion miniature", "strong"),
            ("P7", "kchol.shol.dsheor.*.chdoly.ytaiin.ol.otchy.cphal", "`kchol` body-volatile fluid; `shol` transition fluid; `dsheor` fixed transition-essence outlet; damaged witness; `chdoly` volatile-fix-fluid active; `ytaiin`; `ol`; `otchy`; `cphal` alembic-structure.", "The expanded final paragraph restarts from body-volatile fluid, keeps the witness damage visible, and still lands in a lawful alembic-structure field.", "expanded sacred-herb restart", "mixed"),
            ("P8", "dchor.oty.daiin.ctholy.qoky.chotaiin.chocthy.do*iin.dchor", "`dchor` fixed outlet; `oty`; `daiin`; `ctholy` conduit-fluid active; `qoky` extracted contained active; `chotaiin`; `chocthy`; damaged `do*iin`; closing `dchor`.", "This line duplicates the fixed outlet at both ends, proving that the expanded corridor stays bounded even while it intensifies.", "doubled outlet-bounded line", "mixed"),
            ("P9", "odaiin.dain.cthy.ctheor.o*aiino", "`odaiin/dain` heated and ordinary completion pair; `cthy` conduit bind; `ctheor` conduit-essence outlet; damaged `o*aiino` preserved.", "The page continues to privilege proof over flourish, even when the witness is imperfect.", "checkpoint pair with damage retained", "mixed"),
            ("P10", "kchol.chor.daiin.cthoiin.dchor.chey.qokol.dy.opchol.oldam", "`kchol`; `chor`; `daiin`; `cthoiin` conduit-heat cycle complete; `dchor`; `chey`; `qokol`; `dy`; `opchol`; `oldam` fluid-fix-union-vessel.", "Here the folio states its vessel theology most clearly: the fluid body is not complete until union and vessel closure arrive together in `oldam`.", "union-vessel theorem line", "strong"),
            ("P11", "doiin.yckhody.qokchy.oky.otoldy.yty.dol.or.dochy.daiin", "`doiin` double-cycle fixation; `yckhody` moist valve-heat-fix active; `qokchy`; `oky`; `otoldy`; `yty`; `dol`; `or`; `dochy`; `daiin`.", "The eleventh line reworks the vessel theorem as a moist, valve-governed fixative corridor before the final proof pair.", "moist valve-fix corridor", "strong"),
            ("P12", "odchaiin.cthy.okchy.kchy.dchol.daiin.ydaiin", "`odchaiin` heated fixed completion; `cthy`; `okchy`; `kchy`; `dchol`; `daiin.ydaiin` dry and moist completion.", "The folio explicitly certifies the product in two states, showing that sacred precision here means repeatable admissibility across conditions.", "dual-state proof line", "strong"),
            ("P13", "dchor.dy.dain.qockhy.ykol.okain", "`dchor`; `dy`; `dain`; `qockhy` transmuted valve-active; `ykol` moist contained fluid; `okain` complete containment.", "Close by returning fixed outlet to contained active fluid under one last completion rather than leaving the vessel open.", "contained active terminal", "strong"),
        ],
        tarot_cards=["The Hierophant", "Justice", "Temperance", "Strength", "The Emperor", "Judgment", "The Hermit", "The Chariot", "The Moon", "The Lovers", "The Star", "The World", "The Sun"],
        movements=["open the ritual press-fluid field", "set the valve and vessel", "root the conduit-fluid route", "admit the active fire seal", "re-anchor the active corridor", "seal conduit completion", "restart the expanded sacred route", "hold outlet at both boundaries", "checkpoint under damage", "unite the fluid body in vessel", "govern the moist valve-fix corridor", "prove the route in dry and moist states", "close in contained active fluid"],
        direct="`f22r` is a ritual-precision sacred-herb page. Its real teaching is not the plant's name but the demand that every line be checkpointed before one active fire-seal threshold and one vessel-union finish are allowed to stand.",
        math="Across the formal lenses, `f22r` behaves like a completion-saturated control corridor. The state is repeatedly projected into verified submanifolds, and the single fire-seal event functions as a bounded perturbation inside an otherwise heavily constrained vessel-building process.",
        mythic="Across the mythic lenses, `f22r` is the consecration page. Flame is admitted, but only inside a ritual whose deeper law is proof.",
        compression="Checkpoint the sacred herb on every line, admit active fire only after stabilization, close the fluid body in union-vessel form, and certify the product in both dry and moist completion states.",
        typed_state_machine=r"""
\[\mathcal R_{f22r} = \{r_{\mathrm{ritual}}, r_{\mathrm{verify}}, r_{\mathrm{fireseal}}, r_{\mathrm{vessel}}, r_{\mathrm{dualstate}}\}\]
\[\delta(e_{\mathrm{cfhy}}): r_{\mathrm{verify}} \to r_{\mathrm{fireseal}}\]
\[\delta(e_{\mathrm{oldam}}): r_{\mathrm{fireseal}} \to r_{\mathrm{vessel}} \to r_{\mathrm{dualstate}}\]
""",
        invariants=r"""
\[N_{\mathrm{completion}}(f22r)=13, \qquad N_{\mathrm{cfhy}}(f22r)=1, \qquad N_{\mathrm{dom}}(f22r)=1\]
\[N_{\mathrm{oldam}}(f22r)=1, \qquad N_{\mathrm{daiin.ydaiin}}(f22r)=1, \qquad N_{\mathrm{paragraph\ seals}}(f22r)=3\]
""",
        theorem=r"""
\[\rho_* = (\Psi_{P3} \circ \Psi_{P2} \circ \Psi_{P1})(\rho_0)\]

The formal theorem of `f22r` is:

1. sacred-herb handling is defined by uninterrupted completion grammar rather than by loose herbal description
2. active fire seal is lawful only after multiple prior checkpoints have stabilized the route
3. vessel closure is not optional but encoded explicitly in `dom` and `oldam`
4. the page's true completion criterion is dual-state admissibility, proved in `daiin.ydaiin`
""",
        crystal_contribution=[
            "ritual-precision sacred-herb station",
            "thirteen-completion verification line",
            "active fire-seal threshold",
            "union-vessel closure route",
            "dual-state proof terminal",
        ],
        pointer_title="Ritual-Precision Sacred Herb with Active Fire Seal",
        pointer_position="the recto half of bifolio `bC3 = f19 + f22` and first post-center continuation page of Quire C",
        pointer_page_type="single-herb sacred-preparation page with 13 visible completions and one bounded active fire-seal event",
        pointer_conclusion="`cfhy`, `dom`, `oldam`, and `daiin.ydaiin` inside an all-lines-complete corridor",
        pointer_judgment="`f22r` teaches that sacred preparation is not vagueness but relentless verification: every line completes, then one fire-seal event is admitted, then vessel and dual-state proof finish the work.",
    ),
    make_folio(
        folio_id="F023V",
        quire="C",
        bifolio="bC2 = f18 + f23",
        manuscript_role="maximum-fluid triple-essence tincture page with doubled unions and extreme `ol-` saturation",
        purpose="`f23v` closes the current Quire C inner-bifolio run by shifting from toxic structured fire work into maximum-fluid tincture logic. The folio is saturated with `ol-` forms, introduces `eees` and terminal `eeeoly`, and brackets one line with two `dam` union markers around `olol`. This is the strongest fluid-saturation page in the current three-quire run, so the tincture reading is stronger than any narrow species claim. The page does not deny structure; it dissolves structure into a lawful fluid body capable of bearing triple essence.",
        zero_claim="Carry the borage-class material into an extreme fluid state, circulate essence and salt through repeated fluid carriers, bracket union inside doubled fluid, and finish the tincture as a triple-essence fluid-active body.",
        botanical="`Borago officinalis` / borage / starflower remains plausible locally, though the folio's dominant identity is as a maximum-fluid tincture preparation",
        risk="moderate",
        confidence="high on fluid saturation, doubled union, and triple-essence tincture closure",
        visual_grammar=[
            "`~12 `ol-` tokens` = the page is visibly fluid-dominant",
            "``dam ... olol ... dam`` line` = union is bracketed by doubled fluid in the middle of the page",
            "``eees` and `eeeoly`` = triple essence appears before the final fluid-active seal",
            "`paired with f18r on bC2` = the bifolio contrasts structure-first scaffolding with fluid-saturated tincture finish",
        ],
        full_eva="""
P1: p**irol.odaiiily.sho.al.dy.opchol.otol.ol.chcphy.qotchar.s-
P2: qot*tor.chy.okchaldy.qokchey.dol.otchol.chal.otchm-
P3: ycho.okaiin.okeol.eees.ol.daiin.okeeor.daiin.qotchold-
P4: okchey.dair.sholol.ol.dal.otchor.dar-
P5: dor.chear.shor.dol.oaldary=
P6: tshol.shor.shkshy.okol.daiin.otshor.olsar-
P7: otor.oiin.sho.shol.qokol.daiin.sol.daiin.yly-
P8: qokaiin.dain.qokor.okal.m.dam.chor.olol.dam-
P9: otshy.dal.dar.oldar.ar.or.qotol.chees.m-
P10: dor.chy.kshol.chol.cthol.otol.oloiir-
P11: yokaiin.doroiin.olols.oiin.ol.cheen.ols-
P12: ol.aiior.ol.oro.eeeoly=
""",
        core_vml=[
            "`ol-` saturation` = fluid carrying is the primary law of the page",
            "`eees` and `eeeoly` = triple essence appears within fluid, not apart from it",
            "`dam ... olol ... dam` = doubled union brackets doubled fluid",
            "`sol` and `olsar` = salt remains dissolved inside the fluid corridor",
            "`okeeor` = contained double-essence/source token in the heart of the tincture line",
            "`sholol` = doubled transition-fluid pattern early in the page",
        ],
        groups=[
            {"label": "P1", "title": "Paragraph 1 - fluid-saturated opening and first triple-essence rise", "line_ids": ["P1", "P2", "P3", "P4", "P5"]},
            {"label": "P2", "title": "Paragraph 2 - salt-fluid circulation, doubled union, and triple-essence close", "line_ids": ["P6", "P7", "P8", "P9", "P10", "P11", "P12"]},
        ],
        lines=[
            ("P1", "p**irol.odaiiily.sho.al.dy.opchol.otol.ol.chcphy.qotchar.s", "damaged opener `p**irol`; `odaiiily` heated completion with extended moist-fluid trace; `sho`; `al`; `dy`; `opchol`; `otol`; `ol`; `chcphy`; `qotchar`; `s`.", "Even through damage, the page declares itself fluid-heavy immediately and routes that fluid through alembic and transmuted source grammar.", "fluid-saturated opener", "mixed"),
            ("P2", "qot*tor.chy.okchaldy.qokchey.dol.otchol.chal.otchm", "damaged `qot*tor`; `chy`; `okchaldy` contained volatile-structure-fix active; `qokchey`; `dol`; `otchol`; `chal`; `otchm` medium-bearing heated volatile.", "The second line proves that fluid saturation does not cancel structure; it dissolves structure into a mobile but still fixed tincture body.", "fluid-structure fusion line", "mixed"),
            ("P3", "ycho.okaiin.okeol.eees.ol.daiin.okeeor.daiin.qotchold", "`ycho` moist volatile heat; `okaiin`; `okeol` contained essence fluid; `eees` triple essence; `ol`; `daiin`; `okeeor` contained double-essence source; second `daiin`; `qotchold` transmuted conduit-fluid-fix.", "Triple essence appears here only inside an already fluidized and repeatedly checkpointed body.", "triple-essence tincture rise", "strong"),
            ("P4", "okchey.dair.sholol.ol.dal.otchor.dar", "`okchey`; `dair`; `sholol` doubled transition fluid; `ol`; `dal`; `otchor`; `dar`.", "The folio doubles fluid and structure together, showing that liquidity here is disciplined, not chaotic.", "doubled-fluid structural proof", "strong"),
            ("P5", "dor.chear.shor.dol.oaldary", "`dor`; `chear` essence-root; `shor`; `dol`; `oaldary` fluid-structure-root-active.", "Seal the first paragraph as a fluid-structured root-active product rather than a free wash.", "fluid-root active first seal", "strong"),
            ("P6", "tshol.shor.shkshy.okol.daiin.otshor.olsar", "`tshol`; `shor`; `shkshy` transition-contained-transition active; `okol`; `daiin`; `otshor`; `olsar` fluid-salt-root.", "The second paragraph makes clear that salt is not absent from the tincture; it is dissolved into the fluid corridor itself.", "salt-dissolved fluid restart", "strong"),
            ("P7", "otor.oiin.sho.shol.qokol.daiin.sol.daiin.yly", "`otor`; `oiin`; `sho/shol`; `qokol`; `daiin`; `sol`; second `daiin`; `yly` moist-fluid active.", "This line is the tincture miniature: timed fluid, transition, transmuted heated fluid, salt, and moist fluid activity held under double checkpoint.", "tincture miniature with salt", "strong"),
            ("P8", "qokaiin.dain.qokor.okal.m.dam.chor.olol.dam", "`qokaiin`; `dain`; `qokor`; `okal`; `m`; `dam`; `chor`; `olol`; second `dam`.", "The folio's central union theorem brackets outlet and doubled fluid between two explicit unions, making conjunction itself a fluid envelope.", "doubled-union fluid bracket", "strong"),
            ("P9", "otshy.dal.dar.oldar.ar.or.qotol.chees.m", "`otshy`; `dal`; `dar`; `oldar` fluid-root structure; `ar`; `or`; `qotol`; `chees` volatile triple essence active; `m`.", "After the doubled union, the page returns to structure and root before allowing another triple-essence touch.", "post-union root-structured essence", "strong"),
            ("P10", "dor.chy.kshol.chol.cthol.otol.oloiir", "`dor`; `chy`; `kshol` contained transition fluid; `chol`; `cthol`; `otol`; `oloiir` fluid-fluid completion variant.", "The tenth line keeps the tincture moving through layered fluid carriers and conduit fluid rather than through high fire.", "layered fluid-carrier corridor", "strong"),
            ("P11", "yokaiin.doroiin.olols.oiin.ol.cheen.ols", "`yokaiin`; `doroiin`; `olols` fluid-fluid dissolve; `oiin`; `ol`; `cheen`; `ols` fluid-salt dissolve.", "The route dissolves itself further without losing containment, as if the page were teaching how fluid medicine stays coherent while becoming ever more mobile.", "late fluid-dissolve corridor", "strong"),
            ("P12", "ol.aiior.ol.oro.eeeoly", "`ol`; `aiior` completion-outlet rotation; second `ol`; `oro`; `eeeoly` triple-essence fluid-active.", "Close by naming the tincture as triple essence borne in active fluid rather than as dry fixed compound.", "triple-essence fluid terminal", "strong"),
        ],
        tarot_cards=["The Moon", "Temperance", "The Star", "Justice", "The World", "The Hermit", "The Empress", "The Lovers", "Strength", "The Chariot", "Judgment", "The Sun"],
        movements=["open the fluid-saturated route", "fuse fluid and structure", "raise triple essence inside fluid", "double fluid with structure", "seal the root-active tincture", "restart with salt dissolved in fluid", "compress the tincture law", "bracket union around doubled fluid", "re-root the post-union essence", "carry the medicine on layered fluids", "dissolve further without losing coherence", "close as triple-essence active fluid"],
        direct="`f23v` is a maximum-fluid tincture page. Its key insight is that triple essence can be borne safely not only by rigid structure but by a sufficiently disciplined fluid body.",
        math="Across the formal lenses, `f23v` behaves like a fluid-dominant transport manifold. The state is repeatedly projected onto liquid carriers, while union and structure act as intermittent braces that keep the high-essence tincture from decohering.",
        mythic="Across the mythic lenses, `f23v` is the star-water page. What was venom and furnace on the recto becomes drinkable sky on the verso.",
        compression="Fluidize the route almost completely, keep salt and essence dissolved inside repeated carriers, bracket the union inside doubled fluid, and close the tincture as a triple-essence active liquid body.",
        typed_state_machine=r"""
\[\mathcal R_{f23v} = \{r_{\mathrm{fluidopen}}, r_{\mathrm{triple}}, r_{\mathrm{saltflow}}, r_{\mathrm{unionbrace}}, r_{\mathrm{liquidclose}}\}\]
\[\delta(e_{\mathrm{eees}}): r_{\mathrm{fluidopen}} \to r_{\mathrm{triple}}\]
\[\delta(e_{\mathrm{dam\cdots olol \cdots dam}}): r_{\mathrm{saltflow}} \to r_{\mathrm{unionbrace}}\]
\[\delta(e_{\mathrm{eeeoly}}): r_{\mathrm{unionbrace}} \to r_{\mathrm{liquidclose}}\]
""",
        invariants=r"""
\[N_{\mathrm{ol\text{-}forms}}(f23v)\approx 12, \qquad N_{\mathrm{dam}}(f23v)=2, \qquad N_{\mathrm{eees/eeeoly}}(f23v)=2\]
\[N_{\mathrm{sol/olsar/ols}}(f23v)\ge 3, \qquad N_{\mathrm{paragraph\ seals}}(f23v)=2, \qquad N_{\mathrm{lines}}(f23v)=12\]
""",
        theorem=r"""
\[\rho_* = (\Psi_{P2} \circ \Psi_{P1})(\rho_0)\]

The formal theorem of `f23v` is:

1. the page's dominant invariant is fluid carrying, not rigid fixation
2. triple essence appears inside liquid carriers and repeated checkpoints rather than in opposition to them
3. the middle doubled-union line proves that conjunction can be treated as a fluid envelope
4. the final attractor is `eeeoly`: triple essence borne as active fluid rather than dry compound
""",
        crystal_contribution=[
            "maximum-fluid triple-essence tincture station",
            "fluid-saturated transport line",
            "doubled-union fluid bracket corridor",
            "salt-dissolved carrier route",
            "triple-essence liquid terminal",
        ],
        pointer_title="Maximum-Fluid Triple-Essence Tincture Preparation",
        pointer_position="the verso half of bifolio `bC2 = f18 + f23` and fluid answer to the toxic compound on `f23r`",
        pointer_page_type="single-herb maximum-fluid tincture page with heavy `ol-` density, doubled union, and terminal `eeeoly`",
        pointer_conclusion="`eees`, `dam ... olol ... dam`, `sol`, `olsar`, and terminal `eeeoly`",
        pointer_judgment="`f23v` shows that Quire C can answer toxic structure with fluid grace: the medicine survives not by becoming less active, but by becoming more lawfully liquid.",
    ),
    make_folio(
        folio_id="F023R",
        quire="C",
        bifolio="bC2 = f18 + f23",
        manuscript_role="triple-fire-sealed toxic-compound page with heavy structural fixation and repeated union markers",
        purpose="`f23r` is the most overt toxic-compound handling page in the current Quire C run after the center cluster. The folio opens with `fcholdy`, then builds to the concentrated fire-seal cluster `ofchol.dain.yfchor.olfchor`, giving three fire variants in one line and four across the page. Structural fixation is equally dense: `-dal` forms recur across the folio, `dam` appears twice and `alm` once, and the compound is clearly being taken through repeated binding rather than casually described. The page reads like a dangerous but law-bound multi-fire preparation rather than a botanical inventory item.",
        zero_claim="Take the pasque-flower-class toxic material through repeated fixed and union-bearing corridors, apply triple fire seal only inside a heavily structured route, and finish the compound as a lawfully bound toxic preparation rather than a loose hazard.",
        botanical="`Pulsatilla vulgaris` / pasque flower remains plausible locally because the page reads like a toxic but medicinally useful compound requiring intense discipline",
        risk="moderate",
        confidence="high on multi-fire toxic-compound handling and structural fixation",
        visual_grammar=[
            "`four fire-seal/fire-volatile forms` = `fcholdy` plus the `ofchol.dain.yfchor.olfchor` cluster",
            "`-dal` saturation` = repeated structure endings show the page is fixative as much as fiery",
            "`three unions` = `dam`, `dam`, and `alm` keep conjunction explicit",
            "`long lines with dense compounds` = the danger grammar is embedded in structured corridors, not isolated spikes",
        ],
        full_eva="""
P1: pydchdom.chy.fcholdy.oty.otchol.shy.opyaiin.*yfchy.daiin.olooy.dal-
P2: to.ar.chor.daiin.chkdain.otchy.lolchos.daiin.dam.okchol.dain.g-
P3: dchar.ykor.y.kaiin.daiin.ctho.m=
P4: qokoldy.okaiir.ykaiil.m.qokeey.ofchol.dain.yfchor.olfchor.otchald-
P5: ychor.qokchol.ytym.chol.dain.chol.ar.ol.ol.dol.dain-
P6: tshol.ykor.qokaiin.yky.dar.okol.dchey.daiidal.dam.ytcho.ldals-
P7: okar.olchar.chaiin.qokchol.dar.qokchol.dairo.r.ol.daiin.alm-
P8: qokshy.char.daiir.qokaiin.olol.qoaiin.ykchy.s.dal.okchy-
P9: okol.ok.shy.qokoldy.dal.dsho.qokeees.y.oly.daiin.dal-
P10: q*k.okaiin.chkchy.s.yteain.odal.chaldy.dar.ykain-
P11: ykyko.dalory=
""",
        core_vml=[
            "`fcholdy` = fire-volatile-fluid-fix active at the opening threshold",
            "`ofchol.dain.yfchor.olfchor` = the folio's triple-fire cluster in one line",
            "`dam` x2 + `alm` x1 = explicit union grammar appears three times",
            "`-dal` saturation` = structural fixation is the real counterweight to toxicity",
            "`qokeees` = high essence concentration appears only late and under strong structure",
            "`daiidal` = unique completion fused directly into structure",
        ],
        groups=[
            {"label": "P1", "title": "Paragraph 1 - opening fire seal, first union, and toxic route establishment", "line_ids": ["P1", "P2", "P3"]},
            {"label": "P2", "title": "Paragraph 2 - triple-fire cluster and dense structural binding", "line_ids": ["P4", "P5", "P6", "P7"]},
            {"label": "P3", "title": "Paragraph 3 - late high essence, final structure, and toxic close", "line_ids": ["P8", "P9", "P10", "P11"]},
        ],
        lines=[
            ("P1", "pydchdom.chy.fcholdy.oty.otchol.shy.opyaiin.*yfchy.daiin.olooy.dal", "`pydchdom` pressed moist fix-vessel; `fcholdy` fire-volatile-fluid-fix active; `otchol`; `shy`; `opyaiin`; damaged `*yfchy`; `daiin`; `olooy`; `dal`.", "Open the toxic page under vessel and fixation grammar first, then place the fire-sealed volatile inside that prepared container.", "fire-sealed toxic opener", "mixed"),
            ("P2", "to.ar.chor.daiin.chkdain.otchy.lolchos.daiin.dam.okchol.dain.g", "`to.ar` driven root; `chor`; `daiin`; `chkdain` volatile-contained completion; `otchy`; `lolchos` doubled lock / dissolve compound; second `daiin`; `dam`; `okchol` contained volatile fluid.", "The second line proves that conjunction arrives early, but only after doubled locking and repeated completion have constrained the route.", "locked-union early corridor", "strong"),
            ("P3", "dchar.ykor.y.kaiin.daiin.ctho.m", "`dchar` fixed root-outlet; `ykor`; `y`; `kaiin`; `daiin`; `ctho`; `m` medium/vessel witness.", "Close the first paragraph by fixing the outlet back into rooted containment and conduit.", "rooted first seal", "mixed"),
            ("P4", "qokoldy.okaiir.ykaiil.m.qokeey.ofchol.dain.yfchor.olfchor.otchald", "`qokoldy` extracted contained fluid-fix active; `okaiir/ykaiil` variant containment completions; `qokeey` extracted contained double essence; `ofchol`; `dain`; `yfchor`; `olfchor`; `otchald` heated driven volatile-structure.", "This is the folio's fire theorem: three fire-bearing operators appear inside one already structured line, so flame is present only as a disciplined multiplication inside containment.", "triple-fire cluster line", "strong"),
            ("P5", "ychor.qokchol.ytym.chol.dain.chol.ar.ol.ol.dol.dain", "`ychor`; `qokchol`; `ytym`; `chol`; `dain`; second `chol`; `ar`; `ol.ol`; `dol`; `dain`.", "After the fire cluster, the page immediately sinks back into fluid, root, and fixation grammar, showing structure is the true governor of danger.", "post-fire fluid re-grounding", "strong"),
            ("P6", "tshol.ykor.qokaiin.yky.dar.okol.dchey.daiidal.dam.ytcho.ldals", "`tshol`; `ykor`; `qokaiin`; `yky`; `dar`; `okol`; `dchey`; `daiidal` completion fused to structure; `dam`; `ytcho`; `ldals` locked-structural ending.", "This line binds completion directly into structure and union, making it one of the clearest toxic-discipline lines on the page.", "completion-to-structure union line", "strong"),
            ("P7", "okar.olchar.chaiin.qokchol.dar.qokchol.dairo.r.ol.daiin.alm", "`okar` contained root; `olchar` fluid-source root; `chaiin`; `qokchol`; `dar`; second `qokchol`; `dairo`; `r`; `ol`; `daiin`; `alm` union-structure.", "The second paragraph closes by tying repeated extracted fluid to root fix and an `alm` conjunction, extending union beyond the earlier `dam` events.", "union-structure second seal", "strong"),
            ("P8", "qokshy.char.daiir.qokaiin.olol.qoaiin.ykchy.s.dal.okchy", "`qokshy` extracted contained transition active; `char`; `daiir`; `qokaiin`; `olol`; `qoaiin`; `ykchy`; `s`; `dal`; `okchy`.", "The final paragraph opens as a transition-active extracted state, but quickly doubles fluid and structure again before any free escalation can occur.", "doubled-fluid structured restart", "strong"),
            ("P9", "okol.ok.shy.qokoldy.dal.dsho.qokeees.y.oly.daiin.dal", "`okol/ok` contained fluid and containment; `shy`; `qokoldy`; `dal`; `dsho`; `qokeees` high essence; `y.oly`; `daiin`; terminal `dal`.", "High essence only appears this late and only bracketed by structure, proving that concentration is permitted here only inside a heavily fixed compound.", "high-essence structural bracket", "strong"),
            ("P10", "q*k.okaiin.chkchy.s.yteain.odal.chaldy.dar.ykain", "damaged opener `q*k`; `okaiin`; `chkchy`; `s`; `yteain`; `odal`; `chaldy`; `dar`; `ykain`.", "Even with damage, the line still reads as the same law: containment, dissolution, moist completion, structure, and root fix.", "damaged toxic closure corridor", "mixed"),
            ("P11", "ykyko.dalory", "`ykyko` moist-contained-contained active; `dalory` structure-fluid-outlet-active.", "Close by turning the toxic preparation into an actively structured outlet rather than a free poison.", "structured toxic terminal", "strong"),
        ],
        tarot_cards=["The Devil", "Justice", "The Hermit", "The Tower", "Temperance", "Strength", "The Lovers", "The Chariot", "The Star", "Judgment", "The World"],
        movements=["contain the toxic fire in vessel", "lock and unite the early route", "fix the rooted first seal", "run the triple-fire cluster inside structure", "re-ground the route in fluid and root", "bind completion directly into structure and union", "close the second paragraph in conjunction", "restart under doubled fluid and structure", "allow late high essence only inside brackets", "carry the damaged line through root fix", "close as structured toxic outlet"],
        direct="`f23r` is a toxic-compound page whose central law is that multiple fire events are only admissible when structure, conjunction, and repeated fixing outweigh them at every turn.",
        math="Across the formal lenses, `f23r` behaves like a multi-forcing toxic control system. Fire terms act as intermittent high-energy injections, but the dominant invariants are structural fixation and conjunction count, which keep the compound inside a stable bound manifold.",
        mythic="Across the mythic lenses, `f23r` is the serpent-in-the-crucible page. Venom is welcomed only after the vessel has learned how to hold it without flinching.",
        compression="Contain the toxic source in vessel, run the compound through repeated fire-seal events only inside structured unions, and finish the high-essence route as a lawfully bound outlet instead of loose hazard.",
        typed_state_machine=r"""
\[\mathcal R_{f23r} = \{r_{\mathrm{contain}}, r_{\mathrm{union}}, r_{\mathrm{multifire}}, r_{\mathrm{structure}}, r_{\mathrm{close}}\}\]
\[\delta(e_{\mathrm{fcholdy}}): r_{\mathrm{contain}} \to r_{\mathrm{union}}\]
\[\delta(e_{\mathrm{ofchol.dain.yfchor.olfchor}}): r_{\mathrm{union}} \to r_{\mathrm{multifire}} \to r_{\mathrm{structure}}\]
""",
        invariants=r"""
\[N_{\mathrm{fire\ variants}}(f23r)=4, \qquad N_{\mathrm{union}}(f23r)=3, \qquad N_{\mathrm{dal}}(f23r)\ge 7\]
\[N_{\mathrm{qokeees}}(f23r)=1, \qquad N_{\mathrm{daiidal}}(f23r)=1, \qquad N_{\mathrm{lines}}(f23r)=11\]
""",
        theorem=r"""
\[\rho_* = (\Psi_{P3} \circ \Psi_{P2} \circ \Psi_{P1})(\rho_0)\]

The formal theorem of `f23r` is:

1. toxic-compound work begins under vessel and fixative grammar, not under naked fire
2. the page's central triple-fire cluster is admissible only because the route is already union-bearing and structurally dense
3. high essence appears only late and only inside structural brackets
4. the page closes by converting toxicity into structured active outlet rather than uncontrolled release
""",
        crystal_contribution=[
            "triple-fire-sealed toxic-compound station",
            "opening fire-seal containment line",
            "multi-fire structural bracket corridor",
            "completion-to-structure union route",
            "late high-essence toxic close",
        ],
        pointer_title="Triple-Fire-Sealed Toxic Compound Preparation",
        pointer_position="the recto half of bifolio `bC2 = f18 + f23` and the first toxic-compound answer to Quire C scaffolding work",
        pointer_page_type="single-herb toxic page with four fire variants, repeated `-dal` fixation, and triple conjunction grammar",
        pointer_conclusion="`fcholdy`, `ofchol.dain.yfchor.olfchor`, `daiidal`, `qokeees`, and triple union markers",
        pointer_judgment="`f23r` teaches that toxicity is not opposed to law; it is what forces law to become visibly structural.",
    ),
    make_folio(
        folio_id="F022V",
        quire="C",
        bifolio="bC3 = f19 + f22",
        manuscript_role="converging salt-volatile page with doubled structural title and narrowing-to-closing line architecture",
        purpose="`f22v` behaves like an answer page to `f22r`: the ritual-completion corridor is reworked into salt-volatile convergence and then condensed toward a title that names the product structurally. The line lengths contract through most of the leaf, the title `saiinchy.daldalol` names a salt-active structural-fluid object, and the page keeps union and fire-transition markers present without allowing them to dominate. The local reading as a doubled structural product is well supported by the title line and by the repeated movement from salt-completed input toward fixed fluid embodiment.",
        zero_claim="Gather the tulip-class material through a salt-bearing volatile corridor, keep the route convergent and heat-managed, and finish by naming the product as a doubled structural fluid-active body.",
        botanical="`Tulipa gesneriana x suaveolens` remains plausible locally, though the folio's stronger identity is processual: converging salt-volatile preparation with structural naming",
        risk="moderate",
        confidence="high on converging salt-volatile handling and doubled structural finish",
        visual_grammar=[
            "`contracting line lengths` = the folio visibly narrows toward a named product",
            "`title line T16` = `saiinchy.daldalol` overtly names the final state",
            "`salt appears early and late` = `posaiinor`, `odaiin`, and title `saiinchy` keep salt active across the page",
            "``daldalol`` = doubled structure plus fluid close, unique on the folio title",
        ],
        full_eva="""
P1: posaiinor.ofchar.oky.tchy.otdy.sor.shy.q*d-
P2: daiin.ykaiin.qotchy.kchy.otchyd.dshor.ychy-
P3: qoky.kchorl.otchy.cthy.otchyky.ytchol.otam-
P4: otchaiin.shoty.qoky.saiin.odaiin.ytaiin-
P5: dor.ykcheor.daiin=
P6: fshor.shytchor.otaiin-
P7: ychor.chor.qokchol.chory-
P8: qotchy.cthy.qokol.daiin.dam-
P9: okshor.shody.chol.tchol.otaiin.daiin-
P10: qokchy.daiin.s.or.ytal-
P11: sokaiin.oty.dy-
P12: ykchy.daiin.cthy-
P13: okchain.chkoldy.shotoly-
P14: qotchy.olshly.shol.daiin-
P15: sho.cthy.chocthy.qokchy.dory=
T16: saiinchy.daldalol=
""",
        core_vml=[
            "`posaiinor` = opener already embedding salt-completion into the outlet field",
            "`otam` = heat-energy-union-vessel appears in the first half of the page",
            "`dam` = explicit union marker at the end of the converging middle",
            "`fshor` = fire-transition-heat-source begins the second paragraph",
            "`saiinchy.daldalol` = salt-active product named as doubled structure plus fluid",
            "`contraction toward title` = the page narrows as it converges",
        ],
        groups=[
            {"label": "P1", "title": "Paragraph 1 - salt-bearing convergence and first vessel union", "line_ids": ["P1", "P2", "P3", "P4", "P5"]},
            {"label": "P2", "title": "Paragraph 2 - fire-transition restart and explicit union corridor", "line_ids": ["P6", "P7", "P8", "P9", "P10", "P11", "P12", "P13", "P14", "P15", "T16"]},
        ],
        lines=[
            ("P1", "posaiinor.ofchar.oky.tchy.otdy.sor.shy.q*d", "`posaiinor` pressed outlet with salt-completion embedded; `ofchar` heated fire-source outlet; `oky`; `tchy`; `otdy`; `sor`; `shy`; damaged terminal `q*d`.", "Open with an already salted outlet field, but keep damage visible so the convergence law is not faked into false certainty.", "salted-outlet convergence opener", "mixed"),
            ("P2", "daiin.ykaiin.qotchy.kchy.otchyd.dshor.ychy", "`daiin`; `ykaiin` moist containment complete; `qotchy`; `kchy`; `otchyd`; `dshor`; `ychy`.", "The second line confirms that the converging route is admissible only under completion, moist containment, and fixed outlet transition.", "contained convergence proof", "strong"),
            ("P3", "qoky.kchorl.otchy.cthy.otchyky.ytchol.otam", "`qoky` extracted contained active; `kchorl` body-outlet lock; `otchy`; `cthy`; `otchyky`; `ytchol`; `otam` heat-energy-union-vessel.", "The first major payoff arrives early: a contained active route is carried all the way into an energy-union-vessel state.", "first union-vessel payoff", "strong"),
            ("P4", "otchaiin.shoty.qoky.saiin.odaiin.ytaiin", "`otchaiin` heated fixed completion; `shoty` transition-driven active; `qoky`; `saiin`; `odaiin`; `ytaiin`.", "Salt remains explicit through the page's first half, showing that the convergence is not merely volatile but salt-active from within.", "salt-active midpoint", "strong"),
            ("P5", "dor.ykcheor.daiin", "`dor` fixed outlet root; `ykcheor` moist contained essence outlet; `daiin`.", "Close the first paragraph by rooting the essence outlet under one more checkpoint.", "rooted essence seal", "strong"),
            ("P6", "fshor.shytchor.otaiin", "`fshor` fire-transition-heat-source; `shytchor` transition-moist volatile outlet; `otaiin`.", "Restart the page by allowing fire back in, but only as a source term embedded inside transition and timed completion.", "fire-transition restart", "strong"),
            ("P7", "ychor.chor.qokchol.chory", "`ychor` moist outlet; `chor`; `qokchol` extracted contained volatile fluid; `chory` active outlet.", "The line keeps the route moving through outlet grammar without abandoning fluid containment.", "outlet-fluid carry", "strong"),
            ("P8", "qotchy.cthy.qokol.daiin.dam", "`qotchy`; `cthy`; `qokol`; `daiin`; `dam` union.", "This is the clearest convergence line: transmuted active route, conduit bind, heated fluid, checkpoint, and explicit union.", "convergence-to-union theorem", "strong"),
            ("P9", "okshor.shody.chol.tchol.otaiin.daiin", "`okshor` contained transition outlet; `shody` transition heat-fix active; `chol/tchol` volatile and driven fluids; `otaiin`; `daiin`.", "After union, the page continues by disciplining the fluid body through transition and repeated timed proof.", "post-union fluid discipline", "strong"),
            ("P10", "qokchy.daiin.s.or.ytal", "`qokchy`; `daiin`; `s`; `or`; `ytal` moist-driven structure.", "The tenth line briefly compresses the route into a tiny formula: extract, verify, dissolve, outlet, structure.", "compressed convergence formula", "strong"),
            ("P11", "sokaiin.oty.dy", "`sokaiin` salt-heated containment complete; `oty`; `dy`.", "Salt returns as completed containment, proving it remains active even in the short closing lines.", "salted containment miniature", "strong"),
            ("P12", "ykchy.daiin.cthy", "`ykchy` moist contained volatile active; `daiin`; `cthy`.", "The page narrows to pure essentials: contained volatile, checkpoint, conduit bind.", "narrowing essential bind", "strong"),
            ("P13", "okchain.chkoldy.shotoly", "`okchain` heated contained completion; `chkoldy` volatile-contained-fluid-fix active; `shotoly` transition-driven-fluid-active.", "Even the late narrow lines preserve the same law: containment, fluid fixation, and active transition.", "late narrow fluid-fix line", "strong"),
            ("P14", "qotchy.olshly.shol.daiin", "`qotchy`; `olshly` fluid-transition-fluid active; `shol`; `daiin`.", "The penultimate route is almost pure convergence and proof, as if the page were distilling itself into the title.", "penultimate convergence braid", "strong"),
            ("P15", "sho.cthy.chocthy.qokchy.dory", "`sho`; `cthy`; `chocthy`; `qokchy`; `dory` root-active fix.", "One last transition-conduit line returns the active extract to root-fixed form before naming the product.", "root-active pre-title seal", "strong"),
            ("T16", "saiinchy.daldalol", "`saiinchy` salt-complete volatile active; `daldalol` doubled structure plus fluid.", "Name the product as a salt-active body whose defining character is doubled structure embodied in fluid form.", "doubled-structure title", "strong"),
        ],
        tarot_cards=["Temperance", "Justice", "The Lovers", "Strength", "The Emperor", "The Tower", "The Chariot", "The Hierophant", "The Star", "The Hermit", "Judgment", "The Moon", "Wheel of Fortune", "The Sun", "The World", "The Empress"],
        movements=["open the salted outlet field", "verify moist containment", "enter the first union-vessel state", "keep salt active through the midpoint", "root the essence outlet", "restart with fire-transition source", "carry the outlet through fluid containment", "force convergence into union", "discipline the post-union fluid body", "compress the route to essentials", "reassert salted containment", "bind the narrowed active route", "preserve late fluid-fix transition", "braid convergence into proof", "root the active route before naming", "name the doubled-structure product"],
        direct="`f22v` is a converging salt-volatile page whose real climax is its title: the product is not named as raw flower or free volatile, but as a salt-active doubled structure embodied in fluid form.",
        math="Across the formal lenses, `f22v` behaves like a narrowing convergence map. The state contracts toward a fixed attractor in which union, salt completion, and structural embodiment are progressively compressed until the title becomes the terminal state label.",
        mythic="Across the mythic lenses, `f22v` is the vow page. What began as dispersed active material ends as a named body with doubled bones.",
        compression="Open with salt already embedded in the outlet, converge the route through union and fluid discipline, then name the finished product as a salt-active doubled-structure body in fluid form.",
        typed_state_machine=r"""
\[\mathcal R_{f22v} = \{r_{\mathrm{saltedopen}}, r_{\mathrm{converge}}, r_{\mathrm{union}}, r_{\mathrm{narrow}}, r_{\mathrm{title}}\}\]
\[\delta(e_{\mathrm{otam}}): r_{\mathrm{converge}} \to r_{\mathrm{union}}\]
\[\delta(e_{\mathrm{daldalol}}): r_{\mathrm{narrow}} \to r_{\mathrm{title}}\]
""",
        invariants=r"""
\[N_{\mathrm{title}}(f22v)=1, \qquad N_{\mathrm{dam}}(f22v)=1, \qquad N_{\mathrm{daldalol}}(f22v)=1\]
\[N_{\mathrm{salt\ markers}}(f22v)\ge 4, \qquad N_{\mathrm{daiin/dain}}(f22v)\ge 8, \qquad N_{\mathrm{lines}}(f22v)=16\]
""",
        theorem=r"""
\[\rho_* = (\Psi_{P2} \circ \Psi_{P1})(\rho_0)\]

The formal theorem of `f22v` is:

1. the page begins with salt already embedded in the outlet field rather than added only at the end
2. convergence becomes lawful through conduit, transition, and one explicit union event
3. the late short lines are not filler but deliberate narrowing toward a terminal attractor
4. the title declares the attractor: a salt-active doubled structure embodied in fluid form
""",
        crystal_contribution=[
            "converging salt-volatile station",
            "fire-transition restart line",
            "explicit union corridor",
            "narrowing structural convergence route",
            "doubled-structure title seal",
        ],
        pointer_title="Converging Salt-Volatile Product with Doubled Structural Title",
        pointer_position="the verso half of bifolio `bC3 = f19 + f22` and answer page to the ritual sacred-herb corridor on `f22r`",
        pointer_page_type="single-herb convergence page with contracting line lengths and a named doubled-structure title",
        pointer_conclusion="`posaiinor`, `otam`, `dam`, and title `saiinchy.daldalol`",
        pointer_judgment="`f22v` takes the sacred-herb corridor and condenses it into a converging salt-volatile product whose title names the final doubled structure directly.",
    ),
]


def main() -> None:
    for folio in FOLIOS:
        (FOLIOS_DIR / f"{folio['folio_id']}_FINAL_DRAFT.md").write_text(render_folio(folio), encoding="utf-8")
        (FOLIOS_DIR / f"{folio['folio_id']}.md").write_text(render_pointer(folio), encoding="utf-8")


if __name__ == "__main__":
    main()
