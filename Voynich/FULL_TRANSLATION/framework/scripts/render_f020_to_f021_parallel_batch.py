from __future__ import annotations

from render_f007_to_f008_parallel_batch import FOLIOS_DIR, render_folio, render_pointer
from render_f009_to_f010_parallel_batch import make_folio


FOLIOS: list[dict[str, object]] = [
    make_folio(
        folio_id="F020R",
        quire="C",
        bifolio="bC4 = f20 + f21 (center bifolio)",
        manuscript_role="three-phase essence extraction page with fire-compound catalysis at the quire center",
        purpose="`f20r` is the first true center-bifolio theorem page of Quire C. It begins with dense double-essence extraction, pivots into pressing plus repeated verification, and culminates in the six-morpheme fire compound `fchodees`, which compresses an entire pyrolytic essence sub-procedure into a single token. The page is visibly sectioned into three phases and behaves like the core excipient or tonic essence route around which the rest of the center bifolio is organized.",
        zero_claim="Extract the milk-vetch-class material into repeated essence-bearing states, stabilize it through explicit phase seals and checkpoints, then ignite the fully prepared route through `fchodees` so the resulting double essence can be fixed at the root and sealed as active outlet product.",
        botanical="`Astragalus hypoglottis` / milk vetch remains plausible, but the process profile of excipient-like essence capture is stronger than species certainty",
        risk="moderate",
        confidence="high on three-phase essence extraction and fire-compound catalysis",
        visual_grammar=[
            "`center bifolio` = the page occupies Quire C's geometric core and behaves like a technique center",
            "`three explicit paragraph seals` = P1-4, P5-8, and P9-13 are operational phases rather than arbitrary scribal breaks",
            "`~12 essence markers` = the page is saturated with `-eey/-ees` forms more than with raw danger grammar",
            "`fchodees` in paragraph three` = the longest single Quire C token appears only after two full setup phases",
        ],
        full_eva="""
P1: kdchody.chopy.cheey.qotchol.qotoeey.dchor.choiin-
P2: chodey.cthey.chotol.odaiin.qotchy.cthody.chodchy-
P3: qoteey.cho.chodaiin.sho.qochy.chey.tcheodal.daral-
P4: ochol.ol.teey.otol.chey=
P5: pchocthy.chokoaiin.*y.cheee*.opchey.shoraiin.*-
P6: choiis.okchor.qotol.cheey.daiin.chy.choiin.daiin-
P7: ocho.lshod.dair.choteol.chol.dol.shol.otaiin-
P8: schodain.cheo.r.cheody=
P9: fchodees.shody.qotchey.qokchey.qocphy.chokoldy-
P10: ochaiin.chor.shody.pchodaiin.chetody.choky.dchy.toy-
P11: dchod.qoteeody.ytchy.qotshey.dchaiin.cholody-
P12: shoiin.cheody.otchey.otchy.tchy.qoteey.daiin.dar-
P13: ochaiin.chor.chor.cheey.tchey=
""",
        core_vml=[
            "`fchodees` = fire-volatile-heat-fix-double-essence-dissolve, a whole recipe compressed into one token",
            "`three paragraph seals` = extraction, pressing-plus-verification, then catalytic fire-completion",
            "`daral` = anchored structural fixation at the end of the first paragraph",
            "`cheee*` = damaged triple-essence witness inside the second phase",
            "`qoteeody` = retort-style double-essence plus heat-fix refinement late in the page",
            "`~12 essence markers` = the folio is about capture and concentration more than danger display",
        ],
        groups=[
            {"label": "P1", "title": "Paragraph 1 - double-essence extraction and structural anchoring", "line_ids": ["P1", "P2", "P3", "P4"]},
            {"label": "P2", "title": "Paragraph 2 - pressing, damaged triple essence, and checkpointed stabilization", "line_ids": ["P5", "P6", "P7", "P8"]},
            {"label": "P3", "title": "Paragraph 3 - fire-compound catalysis and active terminal seal", "line_ids": ["P9", "P10", "P11", "P12", "P13"]},
        ],
        lines=[
            ("P1", "kdchody.chopy.cheey.qotchol.qotoeey.dchor.choiin", "`kdchody` contained fix-volatile-heat-fix active; `chopy` volatile heat-press active; `cheey` volatile double-essence active; `qotchol/qotoeey` transmuted fluid and double essence; `dchor` fixed outlet.", "Open by containing and pressing the volatile body until the first double-essence fraction can be fixed at the outlet.", "double-essence extraction opener", "strong"),
            ("P2", "chodey.cthey.chotol.odaiin.qotchy.cthody.chodchy", "`chodey` volatile heat-fix essence active; `cthey` conduit essence; `odaiin` heat-fix completion; `qotchy` transmuted driven volatile active; `cthody` and `chodchy` keep fixation wrapped around conduit and volatile.", "Drive the newly extracted essence through conduit and immediately checkpoint it so the page begins under controlled fixation.", "conduit-essence checkpoint", "strong"),
            ("P3", "qoteey.cho.chodaiin.sho.qochy.chey.tcheodal.daral", "`qoteey` transmuted heat double-essence active; `chodaiin` volatile heat-fix complete; `sho` transition heat; `qochy` transmuted volatile active; `tcheodal` driven volatile essence heat-fix structure; `daral` fixed root structure.", "The first paragraph lands by turning double essence into anchored structure, rooting the volatile route before the next phase begins.", "anchored structural seal", "strong"),
            ("P4", "ochol.ol.teey.otol.chey", "`ochol/ol/otol` layered heated fluid states; `teey` driven double-essence active; `chey` volatile essence active.", "Seal the first phase as a fluid essence state that remains active but already structurally contained.", "fluid seal of paragraph one", "strong"),
            ("P5", "pchocthy.chokoaiin.*y.cheee*.opchey.shoraiin.*", "`pchocthy` press-volatile-heat conduit-bind; `chokoaiin` contained heat-cycle complete; damaged `cheee*` preserves a triple-essence spike; `opchey` heated press volatile essence active; `shoraiin` transition outlet complete.", "Restart under pressure, pass through a damaged but still legible triple-essence event, and bring the route to a completed outlet state.", "pressing plus damaged triple essence", "mixed"),
            ("P6", "choiis.okchor.qotol.cheey.daiin.chy.choiin.daiin", "`choiis` volatile heat cycle dissolve; `okchor` heated contained outlet; `qotol` transmuted heat fluid; `cheey` volatile double essence; two `daiin` checkpoints bracket the active volatile.", "The second paragraph verifies the essence route twice, proving the middle phase is about stabilization as much as concentration.", "double-checkpoint middle corridor", "strong"),
            ("P7", "ocho.lshod.dair.choteol.chol.dol.shol.otaiin", "`ocho` heated volatile heat; `lshod` lock-transition-heat-fix; `dair` fixed earth rotation; `choteol` volatile heat essence-fluid; `dol/shol` fixed and transitioned fluid; `otaiin` timed completion.", "Lock the transition, rotate and fix the route, and turn the essence toward a timed fluid completion.", "locked transition-fluid rotation", "strong"),
            ("P8", "schodain.cheo.r.cheody", "`schodain` salt-volatile-heat-fix complete; `cheo` volatile essence heat; `r` outlet; `cheody` volatile essence heat-fix active.", "Seal the second phase with a salted, heat-fixed outlet so the catalytic fire sequence has a prepared feedstock.", "salted phase-two seal", "strong"),
            ("P9", "fchodees.shody.qotchey.qokchey.qocphy.chokoldy", "`fchodees` six-morpheme fire compound; `shody` transition heat-fix active; `qotchey/qokchey` transmuted and extracted volatile essence; `qocphy` retort-alembic active; `chokoldy` contained fluid fix active.", "This is the center-bifolio ignition line: fire catalysis is introduced only after the page has already built a stable essence corridor.", "fire-compound catalytic theorem", "strong"),
            ("P10", "ochaiin.chor.shody.pchodaiin.chetody.choky.dchy.toy", "`ochaiin` heated volatile cycle complete; `chor` outlet; `shody` transition heat-fix; `pchodaiin` pressed volatile heat-fix completion; `chetody` volatile essence driven heat-fix active; `dchy` fixed volatile active; `toy` driven heat active.", "The catalytic output is immediately pressed and refixed rather than allowed to bloom uncontrolled.", "post-fire press-and-fix", "strong"),
            ("P11", "dchod.qoteeody.ytchy.qotshey.dchaiin.cholody", "`dchod` fixed volatile heat-fix; `qoteeody` transmuted heat double-essence heat-fix; `ytchy` moist driven volatile active; `qotshey` transmuted heat transition essence active; `dchaiin` fixed volatile completion; `cholody` volatile fluid heat-fix active.", "The eleventh line turns the catalytic product into a moist, fixed, double-essence stream under continued retort-style correction.", "moist double-essence correction line", "strong"),
            ("P12", "shoiin.cheody.otchey.otchy.tchy.qoteey.daiin.dar", "`shoiin` transition heat cycle; `cheody` volatile essence heat-fix active; `otchey/otchy/tchy` timed and driven volatile activity; `qoteey` transmuted heat double-essence; `daiin`; `dar` fixed root.", "One last checkpoint returns the process to its root, proving the catalytic sequence still resolves into anchored essence rather than free hazard.", "final checkpoint to the root", "strong"),
            ("P13", "ochaiin.chor.chor.cheey.tchey", "`ochaiin` heated volatile cycle complete; doubled `chor`; `cheey` volatile double-essence active; `tchey` driven volatile essence active.", "Seal the page as an active double-essence outlet rather than as a cooled inert body.", "active double-essence terminal", "strong"),
        ],
        tarot_cards=["The Magician", "Justice", "The Emperor", "Temperance", "Strength", "The Hierophant", "Wheel of Fortune", "Judgment", "The Tower", "The Chariot", "The Star", "The Hermit", "The World"],
        movements=["contain and press the essence", "drive it through conduit proof", "anchor the first phase in structure", "seal the fluid body", "restart under pressure", "verify twice in the middle", "lock and rotate the transition", "salt the second seal", "ignite the fire compound", "press the catalytic output", "correct the moist double essence", "checkpoint back to the root", "seal the active outlet"],
        direct="`f20r` is Quire C's center-bifolio essence core. It is the page where three clean phases culminate in `fchodees`, the longest compressed fire-compound token yet seen, and the surrounding lines make clear that this token only becomes lawful after two prior stages of extraction and verification.",
        math="Across the formal lenses, `f20r` behaves like a staged catalytic system with three operator blocks. Paragraph one establishes an essence basis, paragraph two conditions that basis through repeated verification, and paragraph three applies a high-energy catalytic map that remains constrained by root-return and outlet fixation.",
        mythic="Across the mythic lenses, `f20r` is the hidden furnace at the center of the quire. It does not merely gather essence; it teaches when gathered essence is finally ready to meet fire.",
        compression="Extract the essence in three phases, verify the middle state repeatedly, ignite the center with `fchodees`, and bring the double-essence product back to a rooted active outlet.",
        typed_state_machine=r"""
\[\mathcal R_{f20r} = \{r_{\mathrm{extract}}, r_{\mathrm{verify}}, r_{\mathrm{catalyze}}, r_{\mathrm{rootreturn}}\}\]
\[\delta(e_{\mathrm{fchodees}}): r_{\mathrm{verify}} \to r_{\mathrm{catalyze}}\]
\[\delta(e_{\mathrm{dar}}): r_{\mathrm{catalyze}} \to r_{\mathrm{rootreturn}}\]
""",
        invariants=r"""
\[N_{\mathrm{essence}}(f20r)\approx 12, \qquad N_{\mathrm{paragraph\ seals}}(f20r)=3, \qquad N_{\mathrm{fchodees}}(f20r)=1\]
\[N_{\mathrm{daiin}}(f20r)\ge 4, \qquad N_{\mathrm{daral/dar}}(f20r)\ge 2, \qquad N_{\mathrm{damaged\ triple\ essence}}(f20r)=1\]
""",
        theorem=r"""
\[\rho_* = (\Psi_{P3} \circ \Psi_{P2} \circ \Psi_{P1})(\rho_0)\]

The formal theorem of `f20r` is:

1. center-bifolio work begins with essence accumulation, not immediate heat escalation
2. the page contains an explicit conditioning phase with preserved damage and repeated checkpoints
3. `fchodees` is lawful only because the first two phases have already prepared a stable catalytic substrate
4. the catalytic product remains rooted and active rather than escaping as uncontrolled volatile excess
""",
        crystal_contribution=[
            "three-phase essence-core station",
            "center-bifolio catalytic line",
            "six-morpheme fire-compound threshold",
            "middle-phase double-check corridor",
            "root-return active outlet close",
        ],
        pointer_title="Three-Phase Essence Core with Fire-Compound Catalysis",
        pointer_position="the first center-bifolio page of Quire C and recto core of the `f20/f21` advanced-technique cluster",
        pointer_page_type="single-herb center page with three explicit phases and one maximally compressed fire token",
        pointer_conclusion="`fchodees`, `daral`, damaged `cheee*`, three seals, and a double-essence active outlet close",
        pointer_judgment="`f20r` is the center-bifolio essence core. It teaches that catalytic fire belongs at the end of preparation, not at the beginning of desire.",
    ),
    make_folio(
        folio_id="F020V",
        quire="C",
        bifolio="bC4 = f20 + f21 (center bifolio)",
        manuscript_role="complex fire-managed soaking page with maximum transition density and salt made by fire",
        purpose="`f20v` answers `f20r` by shifting from essence-core buildup into explicit fire management. It opens with `faiis`, where fire completes a salt, then spreads four different compound fire operations across a page dominated by `sh-/sho-` transition grammar. The center-bifolio theorem here is not raw ignition but governed phase change: the volatile body is soaked, cycled, and refixed under multiple kinds of fire until `choraly` gives structure to the source itself.",
        zero_claim="Make the salt with fire first, then move the artichoke-class material through repeated soaking and conduit transitions, using distinct fire operators for each phase until the volatile source acquires stable active structure.",
        botanical="`Cynara cardunculus` / cardoon-artichoke remains plausible because the page reads like bitter extraction by repeated soaking and fire-managed cycling",
        risk="moderate",
        confidence="high on compound-fire management and transition saturation",
        visual_grammar=[
            "`center-bifolio verso` = the core essence page on `f20r` is answered by operational fire management here",
            "`four distinct fire compounds` = fire is never simple on this folio; every appearance is embedded in another operation",
            "`sh-/sho- density` = transition and soaking dominate the leaf more than fixation density alone",
            "`short close after long transition corridor` = the page compresses the terminal handling once the phase law is established",
        ],
        full_eva="""
P1: faiis.ar.okoy.shy.pofochey.opchy.qopy.choldy.opydy.cphy-
P2: sos.ykaiin.cheol.chol.choiin.checthy.otol.chol.chodaiin.oty-
P3: okchy.sho.kchol.shol.chcthy.qoty.chy.tolshy.qotchy-
P4: sho.or.aiin.shol.daiin=
P5: tshol.folchol.otor.shol.shor.fshodchy.otchy.chcphy.dy-
P6: doiiin.chockhy.dan.cheo*y.shos.cheos.char.cthaiin-
P7: shocthy.sho.cthy.daiin.sheoy.tey.s.soaiin-
P8: shain.choraly.sho.ar.chy.daiin.d.e-
P9: ykchy.keody.cho.cthy.chol.shd*oty.d*-
P10: shokaiin.chocthy.chol.daiin.chy.chor.ety-
P11: okoiin.chey.*ol.chory=
""",
        core_vml=[
            "`faiis` = fire completes a salt as the very first move",
            "`pofochey`, `folchol`, and `fshodchy` = distinct compound fire operators distributed across the page",
            "`sh-/sho-` x12 = maximum transition/soaking density in Quire C",
            "`doiiin` = triple-i fixation inside the heated middle corridor",
            "`soaiin` = salt fraction finalized after prolonged conduit work",
            "`choraly` = volatile source granted active structure rather than remaining pure vapor",
        ],
        groups=[
            {"label": "P1", "title": "Paragraph 1 - fire-made salt and transition-field opening", "line_ids": ["P1", "P2", "P3", "P4"]},
            {"label": "P2", "title": "Paragraph 2 - compound fire, triple-i fixation, and structured volatile source", "line_ids": ["P5", "P6", "P7", "P8", "P9", "P10", "P11"]},
        ],
        lines=[
            ("P1", "faiis.ar.okoy.shy.pofochey.opchy.qopy.choldy.opydy.cphy", "`faiis` fire completes salt; `ar` root; `okoy` heated contained active; `pofochey` press-heat-fire-volatile essence active; `opchy/qopy` heat-press and transmute-press activity; `cphy` alembic active.", "Open by making salt with fire itself, then immediately embed fire inside pressing and alembic work rather than treating it as an external later step.", "fire-made salt opener", "strong"),
            ("P2", "sos.ykaiin.cheol.chol.choiin.checthy.otol.chol.chodaiin.oty", "`sos` salt-heat dissolve; `ykaiin` moist contained completion; `cheol/chol` volatile-essence fluid and fluid; `checthy` essence-conduit bind; `chodaiin` volatile heat-fix completion; `oty` heated driven active.", "Dissolve the salt into a moist fluid corridor and bind the essence to conduit before the next fire sequence intensifies.", "salted conduit-fluid field", "strong"),
            ("P3", "okchy.sho.kchol.shol.chcthy.qoty.chy.tolshy.qotchy", "`okchy` heated contained volatile active; `sho/shol` transition heat and transition fluid; `kchol` body-volatile fluid; `chcthy` volatile-conduit bind; `qoty/qotchy` transmuted active states.", "The third line establishes the folio's rule: every active volatile move is paired with transition and fluid carrying, not naked burning.", "transition-saturated active carry", "strong"),
            ("P4", "sho.or.aiin.shol.daiin", "`sho` transition heat; `or` outlet; `aiin` cycle complete; `shol` transition fluid; `daiin` checkpoint.", "Seal the first section as a completed transition-outlet rather than as an exhausted fire event.", "transition-outlet seal", "strong"),
            ("P5", "tshol.folchol.otor.shol.shor.fshodchy.otchy.chcphy.dy", "`tshol` driven transition fluid; `folchol` fire-heat-lock volatile fluid; `otor` heat-driven outlet; `shor` transition outlet; `fshodchy` fire-transition-heat-fix volatile active; `chcphy` volatile alembic active; `dy` fixed.", "The second paragraph spreads fire through locked fluid, outlet work, and active fixation, showing distinct fire modes instead of one generic burn.", "multi-fire middle corridor", "strong"),
            ("P6", "doiiin.chockhy.dan.cheo*y.shos.cheos.char.cthaiin", "`doiiin` triple-i fixation; `chockhy` volatile heat-contained active; `dan` fix-cycle; damaged `cheo*y`; `shos/cheos` dissolved transition and dissolved volatile essence; `char` volatile root; `cthaiin` conduit completion.", "After the fire sequence, the page insists on extended fixation and dissolving transition before it trusts the root again.", "triple-i fixation after fire", "mixed"),
            ("P7", "shocthy.sho.cthy.daiin.sheoy.tey.s.soaiin", "`shocthy` transition-heat conduit-bind; `sho/cthy` repeat the binding field; `daiin`; `sheoy/tey` transition and driven essence activity; `s`; `soaiin` salt-heat cycle complete.", "This line formalizes the soaking law and then finalizes the salt fraction explicitly.", "conduit soaking to salt completion", "strong"),
            ("P8", "shain.choraly.sho.ar.chy.daiin.d.e", "`shain` transition-complete; `choraly` volatile outlet root structure active; `sho` transition heat; `ar` root; `chy` volatile active; `daiin`; trailing `d.e` preserved.", "The page's signature line makes transition itself the completion and grants structure to the volatile source so it can persist beyond vapor.", "source structure from transition", "strong"),
            ("P9", "ykchy.keody.cho.cthy.chol.shd*oty.d*", "`ykchy` moist contained volatile active; `keody` body-essence heat-fix active; `cho` volatile heat; `cthy` conduit bind; `chol` volatile fluid; damaged `shd*oty`; damaged terminal fix.", "Even with damage, the line clearly continues the same pattern: moist containment, body-essence fixing, and conduit-bound fluid handling.", "damaged moist containment line", "mixed"),
            ("P10", "shokaiin.chocthy.chol.daiin.chy.chor.ety", "`shokaiin` transition-contained completion; `chocthy` volatile-heat conduit-bind; `chol`; `daiin`; `chy/chor` active volatile and outlet; `ety` essence-driven active.", "Checkpoint the transition-contained state and let the volatile outlet reappear only after the conduit field is stabilized again.", "late checkpointed outlet return", "strong"),
            ("P11", "okoiin.chey.*ol.chory", "`okoiin` heated contained cycle; `chey` volatile essence active; damaged `*ol`; `chory` volatile heat outlet active.", "The page closes shortly and precisely: contain the heated cycle, preserve the essence, and release only an active controlled outlet.", "short active outlet seal", "mixed"),
        ],
        tarot_cards=["The Emperor", "Temperance", "The Chariot", "Justice", "Strength", "The Hermit", "Judgment", "The Star", "The Moon", "The Hierophant", "The World"],
        movements=["make the salt with fire", "dissolve it into conduit fluid", "carry the active volatile through transition", "seal the first transition field", "apply multiple fire modes", "fix the heated middle three times", "bind and finish the salt fraction", "give structure to the source", "preserve the damaged moist line", "checkpoint the contained outlet", "seal the active release"],
        direct="`f20v` is the center-bifolio fire-management leaf. It does not simply burn; it differentiates fire into several embedded operators, uses soaking and transition as equal partners to heat, and culminates in `choraly`, where volatile source is given active structure.",
        math="Across the formal lenses, `f20v` behaves like a controlled phase-transition network. Fire terms act as local forcings, but the dominant state variable is transition density, which keeps the system from collapsing into a one-step combustion model.",
        mythic="Across the mythic lenses, `f20v` is the page that teaches the operator to hold flame without becoming flame. Fire is useful here only because it is braided into patience.",
        compression="Make the salt with fire, push the material through repeated soaking and conduit transitions, distribute distinct fire operators across the route, and give the volatile source stable structure in `choraly`.",
        typed_state_machine=r"""
\[\mathcal R_{f20v} = \{r_{\mathrm{firesalt}}, r_{\mathrm{transition}}, r_{\mathrm{multifire}}, r_{\mathrm{structure}}\}\]
\[\delta(e_{\mathrm{faiis}}): r_{\mathrm{firesalt}} \to r_{\mathrm{transition}}\]
\[\delta(e_{\mathrm{choraly}}): r_{\mathrm{multifire}} \to r_{\mathrm{structure}}\]
""",
        invariants=r"""
\[N_{\mathrm{fire\ compounds}}(f20v)=4, \qquad N_{\mathrm{sh/sho}}(f20v)\approx 12, \qquad N_{\mathrm{daiin}}(f20v)\ge 4\]
\[N_{\mathrm{doiiin}}(f20v)=1, \qquad N_{\mathrm{soaiin}}(f20v)=1, \qquad N_{\mathrm{choraly}}(f20v)=1\]
""",
        theorem=r"""
\[\rho_* = (\Psi_{P2} \circ \Psi_{P1})(\rho_0)\]

The formal theorem of `f20v` is:

1. the folio begins by manufacturing salt through fire rather than merely applying fire to existing product
2. transition density is the real stabilizer of the page's many fire operations
3. `doiiin` and `soaiin` show that extended fixation and salt completion are required before structural volatile work
4. `choraly` is the payoff: volatile source is given active structure instead of being left as transient vapor
""",
        crystal_contribution=[
            "quadruple-fire transition station",
            "fire-made salt opening line",
            "triple-i fixation corridor",
            "salt-fraction completion threshold",
            "volatile-source structuring close",
        ],
        pointer_title="Complex Fire-Managed Soaking with Quadruple Fire",
        pointer_position="the second center-bifolio page of Quire C and fire-management answer to the essence core on `f20r`",
        pointer_page_type="single-herb fire-and-transition page with high `sh-/sho-` density and multiple embedded fire compounds",
        pointer_conclusion="`faiis`, `folchol`, `fshodchy`, `doiiin`, `soaiin`, and `choraly`",
        pointer_judgment="`f20v` teaches that the center of Quire C is not raw flame but governed phase change: fire works only because transition keeps teaching it how to behave.",
    ),
    make_folio(
        folio_id="F021R",
        quire="C",
        bifolio="bC4 = f20 + f21 (center bifolio)",
        manuscript_role="expert-compressed essence extraction page with the highest density of mega-compound instructions in Quire C",
        purpose="`f21r` is the most compressed instruction leaf in the current manuscript run. It opens already at high intensity with `oeeockhy`, distributes multiple six-to-eight-morpheme compounds across all three paragraphs, and treats procedural compression itself as the operator law. The page assumes an expert reader who can unpack valve-controlled triple essence, fire-active volatile compounds, and the longest non-fire instruction `otolosheey` without needing the slow pedagogical pacing of earlier folios.",
        zero_claim="Begin at maximum controlled essence intensity, compress whole procedures into single compound tokens, and move the pimpernel-class route through expert-only retort and conduit shorthand until the page can close on contained double essence without ever dropping back to beginner grammar.",
        botanical="`Anagallis arvensis` / scarlet pimpernel remains plausible as a mildly toxic wound herb whose preparation rewards precision",
        risk="moderate",
        confidence="high on expert-compressed technique and mega-compound density",
        visual_grammar=[
            "`center bifolio terminal recto` = the advanced-technique cluster intensifies toward maximum compression here",
            "`pinwheel / Herculeaf structure` = local corpus marks the drawing as unusual inside Herbal A",
            "`five mega-compounds` = the page reads like shorthand notes for a trained operator rather than onboarding material",
            "`three section architecture` = despite compression, the page still preserves visible operational paragraphing",
        ],
        full_eva="""
P1: pchor.oeeockhy.o.fychey.ypchey.qopcheody.otaiin.chan-
P2: saiin.chcphy.oky.sheaiin.qotchol.oteos.sheey.cthy.daiin-
P3: qotyl.shy.ol.cheor.chy.qokchey.chey.keey.dy=
P4: pchofychy.daiin.cthain.otolosheey.qocthey.tol.chory-
P5: okeey.daiin.chosy.qokoiin.otol.chol.qot.cheol.okeoaiin-
P6: dchor.y.koly.ky.chol.tol.qokeol.chol.ol.qoteeol.dady-
P7: shoeor.cheor.chokeody.chocthor.shy=
P8: fchokshy.otor.sheol.ocphal.ocphsheas.cthodaiin.oty-
P9: okaiin.sho.tshaiin.chkaiin.shcthey.cthody.cthy.s-
P10: totchy.keor.chy.ky.qotaiin.qotchol.ty.ctheey.otaiin-
P11: shol.chol.shol.tchol.chcthy.otyky.shey.yteol.shody-
P12: ykeey.chor.sheey.ysheol.chor.chol.daiin.chkaiin=
""",
        core_vml=[
            "`oeeockhy` = valve-controlled triple essence right at the opening",
            "`pchofychy` and `fchokshy` = fire embedded inside already compressed volatile operations",
            "`otolosheey` = the longest non-fire compound in Quire C, carrying a whole cycle in one word",
            "`ocphsheas` = multi-prefix alembic-transition compound",
            "`keey`, `okeey`, `ykeey`, and `qoteeol` = body/double-essence grammar saturates the page",
            "`three paragraph seals` = even expert shorthand still preserves section law",
        ],
        groups=[
            {"label": "P1", "title": "Paragraph 1 - high-intensity opening and first seal", "line_ids": ["P1", "P2", "P3"]},
            {"label": "P2", "title": "Paragraph 2 - longest mega-compound cycle and essence-fluid carry", "line_ids": ["P4", "P5", "P6", "P7"]},
            {"label": "P3", "title": "Paragraph 3 - fire-contained transition shorthand and contained double-essence close", "line_ids": ["P8", "P9", "P10", "P11", "P12"]},
        ],
        lines=[
            ("P1", "pchor.oeeockhy.o.fychey.ypchey.qopcheody.otaiin.chan", "`pchor` pressed volatile outlet; `oeeockhy` heated triple essence under valve control; `fychey` fire-active volatile essence active; `ypchey` moist pressed volatile essence; `qopcheody` transmuted press volatile essence heat-fix active; `otaiin`; `chan` volatile cycle.", "Open at an intensity that earlier folios would reserve for a climax: the operator is expected to manage triple essence and embedded fire immediately.", "maximum-intensity expert opener", "strong"),
            ("P2", "saiin.chcphy.oky.sheaiin.qotchol.oteos.sheey.cthy.daiin", "`saiin` salt cycle complete; `chcphy` volatile alembic active; `oky` heated contained active; `sheaiin` transition-essence completion; `qotchol` transmuted volatile fluid; `oteos` timed essence dissolve; `sheey` transition double essence; `cthy`; `daiin`.", "Even at expert compression, the page still checkpoints the first section and makes salt plus conduit law explicit.", "salt and conduit proof", "strong"),
            ("P3", "qotyl.shy.ol.cheor.chy.qokchey.chey.keey.dy", "`qotyl` transmuted heat-active lock; `shy` transition active; `ol` fluid; `cheor` volatile essence outlet; `qokchey` extracted contained volatile essence; `keey` body double essence active; `dy` fixed.", "Seal the opening paragraph by locking the fluid essence into embodied double-essence form rather than leaving it as free outlet alone.", "embodied double-essence seal", "strong"),
            ("P4", "pchofychy.daiin.cthain.otolosheey.qocthey.tol.chory", "`pchofychy` press-volatile-heat-fire-active volatile active; `daiin`; `cthain` conduit completion; `otolosheey` the longest non-fire compressed cycle; `qocthey` transmuted conduit essence active; `tol`; `chory` volatile heat outlet active.", "This line is the page's compression theorem: press-fire shorthand and the longest non-fire cycle are placed side by side and treated as a single coherent step.", "compression theorem line", "strong"),
            ("P5", "okeey.daiin.chosy.qokoiin.otol.chol.qot.cheol.okeoaiin", "`okeey` heated contained double essence active; `daiin`; `chosy` volatile heat-salt active; `qokoiin` extracted contained heat cycle; `otol/chol` timed and volatile fluids; `qot`; `cheol`; `okeoaiin` heated contained essence cycle complete.", "Carry the compressed instruction forward as a double-essence fluid route that remains salted, cycled, and contained.", "double-essence fluid carry", "strong"),
            ("P6", "dchor.y.koly.ky.chol.tol.qokeol.chol.ol.qoteeol.dady", "`dchor` fixed outlet; `koly/ky` body-heat fluid active and contained active; `chol/tol` volatile and driven fluids; `qokeol` extracted contained essence fluid; `qoteeol` transmuted heat double-essence fluid; `dady` fixed earth-fix active.", "The sixth line shows that even compressed expert work still closes each micro-sequence by grounding the fluid essence in fixation.", "grounded fluid fixation", "strong"),
            ("P7", "shoeor.cheor.chokeody.chocthor.shy", "`shoeor` transition-heat essence outlet; `cheor` volatile essence outlet; `chokeody` volatile heat-contained essence heat-fix active; `chocthor` volatile heat conduit outlet; `shy`.", "Seal the second paragraph as a tightly compressed outlet-and-conduit essence corridor rather than a rest state.", "essence corridor seal", "strong"),
            ("P8", "fchokshy.otor.sheol.ocphal.ocphsheas.cthodaiin.oty", "`fchokshy` fire-volatile-heat-contain transition active; `otor` heat-driven outlet; `sheol` transition essence fluid; `ocphal` heat alembic structure; `ocphsheas` heat alembic transition essence dissolve; `cthodaiin`; `oty`.", "Restart under fire-contained transition and immediately stack alembic structure plus multi-prefix dissolution shorthand into one line.", "fire-contained alembic shorthand", "strong"),
            ("P9", "okaiin.sho.tshaiin.chkaiin.shcthey.cthody.cthy.s", "`okaiin` heated contained cycle complete; `sho/tshaiin` transition heat and driven transition completion; `chkaiin` volatile containment completion; `shcthey` transition-conduit essence active; `cthody/cthy`; `s` dissolve.", "The ninth line restores explicit completion density so the compressed fire corridor remains admissible.", "compressed corridor checkpoint", "strong"),
            ("P10", "totchy.keor.chy.ky.qotaiin.qotchol.ty.ctheey.otaiin", "`totchy` driven-heat volatile active; `keor` body-essence outlet; `chy/ky` volatile and contained active; `qotaiin`; `qotchol`; `ty`; `ctheey` conduit double essence active; `otaiin`.", "Keep body, outlet, and double essence braided together inside a timed retort-fluent state.", "timed body-outlet braid", "strong"),
            ("P11", "shol.chol.shol.tchol.chcthy.otyky.shey.yteol.shody", "alternating `shol/chol/shol/tchol` transition-fluid and volatile-fluid pattern; `chcthy` volatile conduit bind; `otyky` heated driven contained active; `shey`; `yteol`; `shody`.", "The alternating fluid pattern is a rare visible rhythm in the page, showing that even shorthand still preserves deliberate cadence.", "alternating fluid cadence", "strong"),
            ("P12", "ykeey.chor.sheey.ysheol.chor.chol.daiin.chkaiin", "`ykeey` moist contained double essence active; `chor`; `sheey` transition double essence active; `ysheol` moist transition essence fluid; `chor/chol`; `daiin`; `chkaiin` volatile containment completion.", "Close by lowering the expert shorthand back into a moist, contained double-essence finish under one final checkpoint.", "contained double-essence close", "strong"),
        ],
        tarot_cards=["The Magician", "The Emperor", "Justice", "Temperance", "Strength", "The Hermit", "Judgment", "The Tower", "The Chariot", "The Star", "The Moon", "The World"],
        movements=["open at maximum controlled intensity", "bind salt and conduit early", "seal the embodied double essence", "execute the compression theorem", "carry the double-essence fluid", "ground the fluid in fixation", "seal the essence corridor", "restart the fire-contained shorthand", "checkpoint the compressed corridor", "braid body and outlet", "maintain the fluid cadence", "close in moist containment"],
        direct="`f21r` is the expert-only shorthand page. It assumes the reader already knows the grammar well enough to unpack seven- and eight-morpheme tokens without losing the operational sequence, and it treats that compression itself as a mark of mastery.",
        math="Across the formal lenses, `f21r` behaves like a high-information-density control law. Multiple operator compositions are fused into single tokens, so the page minimizes explicit step count while maximizing semantic payload per event.",
        mythic="Across the mythic lenses, `f21r` is the master's notebook. Nothing is explained slowly because nothing here is meant for the uninitiated.",
        compression="Begin at valve-controlled triple essence, compress full procedures into mega-compounds, preserve conduit and fluid cadence through shorthand, and finish on contained moist double essence.",
        typed_state_machine=r"""
\[\mathcal R_{f21r} = \{r_{\mathrm{maxopen}}, r_{\mathrm{compressed1}}, r_{\mathrm{compressed2}}, r_{\mathrm{containedclose}}\}\]
\[\delta(e_{\mathrm{oeeockhy}}): r_{\mathrm{maxopen}} \to r_{\mathrm{compressed1}}\]
\[\delta(e_{\mathrm{otolosheey}}): r_{\mathrm{compressed1}} \to r_{\mathrm{compressed2}}\]
\[\delta(e_{\mathrm{chkaiin}}): r_{\mathrm{compressed2}} \to r_{\mathrm{containedclose}}\]
""",
        invariants=r"""
\[N_{\mathrm{mega\ compounds}}(f21r)\ge 5, \qquad N_{\mathrm{paragraph\ seals}}(f21r)=3, \qquad N_{\mathrm{daiin}}(f21r)\ge 4\]
\[N_{\mathrm{oeeockhy}}(f21r)=1, \qquad N_{\mathrm{otolosheey}}(f21r)=1, \qquad N_{\mathrm{fchokshy}}(f21r)=1, \qquad N_{\mathrm{ocphsheas}}(f21r)=1\]
""",
        theorem=r"""
\[\rho_* = (\Psi_{P3} \circ \Psi_{P2} \circ \Psi_{P1})(\rho_0)\]

The formal theorem of `f21r` is:

1. the center bifolio reaches a threshold where compression becomes a first-class operator
2. the opening already presumes mastery because triple-essence valve control appears before any simple warm-up
3. `otolosheey` demonstrates that full cyclic instructions can be collapsed into one token without losing lawful sequencing
4. the close remains contained and moist, proving shorthand does not abandon control
""",
        crystal_contribution=[
            "expert-compressed instruction station",
            "valve-controlled triple-essence opening line",
            "longest non-fire mega-compound threshold",
            "alternating fluid-cadence corridor",
            "contained moist double-essence close",
        ],
        pointer_title="Expert-Compressed Mega-Compound Operations",
        pointer_position="the third center-bifolio page of Quire C and the manuscript's current peak of procedural shorthand",
        pointer_page_type="single-herb expert page with five mega-compounds and three visible section seals",
        pointer_conclusion="`oeeockhy`, `pchofychy`, `otolosheey`, `fchokshy`, `ocphsheas`, and alternating fluid cadence on P11",
        pointer_judgment="`f21r` does not slow down to teach. It writes as if the operator is already expert, and the density of the compounds is the proof.",
    ),
    make_folio(
        folio_id="F021V",
        quire="C",
        bifolio="bC4 = f20 + f21 (center bifolio)",
        manuscript_role="quintuple-essence flammable-oil extraction page with staged concentration and doubled verification pairs",
        purpose="`f21v` is the flashpoint page of the center bifolio. It opens as a continuation route, embeds fire directly inside the volatile medium with `chofchy` and `qofshey`, then escalates from triple essence in `oeeesoy` to quintuple essence in `keeees`. The short eight-line structure reads like a danger signal: concentrated flammable oils require brief handling, repeated double checks, and decisive closure.",
        zero_claim="Continue the volatile route under fire inside the retort, raise concentration from triple to quintuple essence, verify the dangerous middle twice over, and close the burning-bush-class product before the flammable active body can outrun containment.",
        botanical="`Dictamnus albus` / burning bush is one of the strongest process-botanical fits in the local corpus because the page explicitly behaves like maximum volatile concentration under controlled fire",
        risk="moderate",
        confidence="high on staged concentration, fire-in-volatile handling, and quintuple essence",
        visual_grammar=[
            "`short 8-line page` = the procedure is brief in the way dangerous handling pages often are",
            "`center bifolio terminal verso` = the advanced-technique cluster resolves as concentrated volatile closure",
            "`quintuple-e token` = one of the manuscript's two strongest visible essence escalations",
            "`doubled completion pairs` = the leaf distrusts single verification at maximum concentration",
        ],
        full_eva="""
P1: toldshy.chofchy.qofshey.shckhol.odaiin.shey.ckholy-
P2: oeeesoy.qokchy.chody.motchy.qokchy.choty.tchol.daiin-
P3: qotal.keeees.chotchy.tcho.choty.chor.qotol.daiin.dal-
P4: sho.chodaiin.choty.chol.daiin.daiin.chty.chtol-
P5: ysho.deey.ctho.l.sho.cthy.daiin.dait.oky-
P6: sho.tsho.chotshol.chol.todaiin.daiin-
P7: ykcho.lchol.chol.chaiin.otchy.s.sheaiin-
P8: cho.l.kchochaiin=
""",
        core_vml=[
            "`toldshy` = continuation opener, so the page inherits an already prepared state",
            "`chofchy` and `qofshey` = fire embedded inside volatile and retort-transition operations",
            "`oeeesoy` -> `keeees` = staged concentration from triple to quintuple essence",
            "`daiin.daiin` and `todaiin.daiin` = two doubled verification pairs",
            "`motchy` = rare m-prefix, likely medium or vessel-specific handling during concentration",
            "`kchochaiin` = the page closes as a contained body-volatile completion rather than open flame",
        ],
        groups=[
            {"label": "P1", "title": "Paragraph 1 - continuation, fire-in-volatile opening, and triple-essence rise", "line_ids": ["P1", "P2", "P3", "P4"]},
            {"label": "P2", "title": "Paragraph 2 - doubled verification pairs and decisive volatile closure", "line_ids": ["P5", "P6", "P7", "P8"]},
        ],
        lines=[
            ("P1", "toldshy.chofchy.qofshey.shckhol.odaiin.shey.ckholy", "`toldshy` continuation opener; `chofchy` fire between volatiles; `qofshey` fire inside retort-transition essence; `shckhol/ckholy` transition valve-fluid forms; `odaiin`; `shey`.", "Open as though the material is already live, then place fire directly inside the volatile medium while keeping the route under valve-fluid governance.", "fire-in-volatile continuation opener", "strong"),
            ("P2", "oeeesoy.qokchy.chody.motchy.qokchy.choty.tchol.daiin", "`oeeesoy` triple-essence heated active; `qokchy` extracted contained active twice across the line; `chody` volatile heat-fix active; `motchy` rare medium/vessel token; `choty` volatile heat driven active; `tchol`; `daiin`.", "The page first raises the route to triple essence, but still ends the line under explicit containment and checkpointing.", "triple-essence checkpoint rise", "strong"),
            ("P3", "qotal.keeees.chotchy.tcho.choty.chor.qotol.daiin.dal", "`qotal` transmuted heat structure; `keeees` quintuple essence; `chotchy/tcho/choty/chor` active volatile heat and outlet chain; `qotol`; `daiin`; `dal` fixed structure.", "This is the flashpoint line: quintuple essence appears only alongside structural fixation and checkpointing, not as naked climax.", "quintuple-essence structural theorem", "strong"),
            ("P4", "sho.chodaiin.choty.chol.daiin.daiin.chty.chtol", "`sho` transition heat; `chodaiin` volatile heat-fix completion; `choty/chol`; doubled `daiin`; `chty/chtol` volatile-driven active and fluid.", "After the quintuple spike, the folio immediately double-checks the route rather than celebrating the escalation.", "first doubled verification pair", "strong"),
            ("P5", "ysho.deey.ctho.l.sho.cthy.daiin.dait.oky", "`ysho` moist transition heat; `deey` fixed double essence active; `ctho` conduit heat; `l` lock; `sho/cthy`; `daiin`; `dait`; `oky` heated contained active.", "Pull the route down from maximum concentration into locked conduit and fixed double essence so it can stay admissible.", "descent into locked conduit", "strong"),
            ("P6", "sho.tsho.chotshol.chol.todaiin.daiin", "`sho/tsho` transition heat and driven transition heat; `chotshol` volatile heat-driven transition fluid; `chol`; `todaiin`; `daiin`.", "The second doubled verification pair arrives here: an energized completion followed by an ordinary one, confirming the dangerous middle twice.", "second doubled verification pair", "strong"),
            ("P7", "ykcho.lchol.chol.chaiin.otchy.s.sheaiin", "`ykcho` moist contained volatile heat; `lchol/chol` locked and ordinary volatile fluid; `chaiin` volatile completion; `otchy`; `s`; `sheaiin` transition-essence completion.", "Keep the volatile fluid locked, complete it, dissolve what must dissolve, and let the essence transition itself close lawfully.", "locked volatile-fluid recovery", "strong"),
            ("P8", "cho.l.kchochaiin", "`cho` volatile heat; `l` lock; `kchochaiin` body-volatile heat-volatile cycle complete.", "Close by locking the volatile body into a complete cycle rather than allowing the flammable route to remain open.", "locked body-volatile terminal", "strong"),
        ],
        tarot_cards=["The Tower", "Temperance", "The Sun", "Justice", "Strength", "Judgment", "The Star", "The World"],
        movements=["continue the live route under fire", "raise it to triple essence", "push to quintuple essence with structure", "double-check the dangerous crest", "descend into locked conduit", "double-check again", "recover the locked volatile fluid", "seal the body-volatile cycle"],
        direct="`f21v` is the center-bifolio flashpoint page. It stages concentration from triple to quintuple essence under fire contained within the volatile medium, then treats doubled verification as the price of handling the most flammable product in the quire.",
        math="Across the formal lenses, `f21v` behaves like a staged concentration ladder with hard safety gates. The state ascends from triple to quintuple essence, but every ascent is immediately followed by paired verification events that project the process back into a stable containment manifold.",
        mythic="Across the mythic lenses, `f21v` is the page of the captured lightning. It proves that the highest essence is not freedom from control but obedience to a stronger container.",
        compression="Continue the live volatile route, escalate from triple to quintuple essence under internal fire, verify twice in pairs, and close the flammable product as a locked body-volatile cycle.",
        typed_state_machine=r"""
\[\mathcal R_{f21v} = \{r_{\mathrm{continuation}}, r_{\mathrm{triple}}, r_{\mathrm{quintuple}}, r_{\mathrm{verifypair}}, r_{\mathrm{lockedclose}}\}\]
\[\delta(e_{\mathrm{oeeesoy}}): r_{\mathrm{continuation}} \to r_{\mathrm{triple}}\]
\[\delta(e_{\mathrm{keeees}}): r_{\mathrm{triple}} \to r_{\mathrm{quintuple}}\]
\[\delta(e_{\mathrm{daiin.daiin}}): r_{\mathrm{quintuple}} \to r_{\mathrm{verifypair}} \to r_{\mathrm{lockedclose}}\]
""",
        invariants=r"""
\[N_{\mathrm{keeees}}(f21v)=1, \qquad N_{\mathrm{oeeesoy}}(f21v)=1, \qquad N_{\mathrm{daiin}}(f21v)=9\]
\[N_{\mathrm{doubled\ completion\ pairs}}(f21v)=2, \qquad N_{\mathrm{fire\ in\ volatile}}(f21v)\ge 2, \qquad N_{\mathrm{lines}}(f21v)=8\]
""",
        theorem=r"""
\[\rho_* = (\Psi_{P2} \circ \Psi_{P1})(\rho_0)\]

The formal theorem of `f21v` is:

1. the page inherits a live volatile route rather than beginning from raw intake
2. concentration is staged from triple to quintuple essence rather than jumped in one move
3. each dangerous ascent is followed by doubled verification, making paired checking the real safety law
4. the product closes not as free flame but as a locked body-volatile completion
""",
        crystal_contribution=[
            "quintuple-essence flashpoint station",
            "fire-in-volatile transition line",
            "triple-to-quintuple concentration ladder",
            "doubled verification-pair corridor",
            "locked body-volatile closure",
        ],
        pointer_title="Quintuple-Essence Flammable Oil Extraction",
        pointer_position="the final center-bifolio page of Quire C and volatile flashpoint answer to the compressed expert page on `f21r`",
        pointer_page_type="short high-danger single-herb page with quintuple essence, embedded fire, and two doubled-check pairs",
        pointer_conclusion="`chofchy`, `qofshey`, `oeeesoy`, `keeees`, `daiin.daiin`, `todaiin.daiin`, and `kchochaiin`",
        pointer_judgment="`f21v` is the quire's flashpoint page. It shows that maximum essence can only survive inside a container strong enough to make doubled verification feel ordinary.",
    ),
]


def main() -> None:
    for folio in FOLIOS:
        (FOLIOS_DIR / f"{folio['folio_id']}_FINAL_DRAFT.md").write_text(render_folio(folio), encoding="utf-8")
        (FOLIOS_DIR / f"{folio['folio_id']}.md").write_text(render_pointer(folio), encoding="utf-8")


if __name__ == "__main__":
    main()
