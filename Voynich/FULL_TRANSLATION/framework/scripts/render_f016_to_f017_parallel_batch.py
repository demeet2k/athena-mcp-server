from __future__ import annotations

from render_f007_to_f008_parallel_batch import FOLIOS_DIR, render_folio, render_pointer
from render_f009_to_f010_parallel_batch import make_folio


FOLIOS: list[dict[str, object]] = [
    make_folio(
        folio_id="F016R",
        quire="B",
        bifolio="bB1 = f9 + f16",
        manuscript_role="double-locked triple-essence cannabis extraction with title-line certification",
        purpose="`f16r` closes the outer `f9/f16` bifolio by turning Quire B's aromatic fire discipline toward a longer cannabis-class extraction. The page is unusually explicit about naming its threshold and its concentration law: it contains a title line, announces the strongest local `oeees -> deeeod` transition on one line, repeats driven energy as `ty.ty`, and reintroduces `fchol` only after salt completion has already been certified. The leaf reads like a controlled intoxicant extraction that keeps labeling, checking, and relocking the route instead of allowing one uncontrolled essence bloom.",
        zero_claim="Press and contain the cannabis route, force it through triple essence until that essence becomes double-locked, complete the salt side as a separate certifiable fraction, then return to fire-fluid correction before the page closes.",
        botanical="`Cannabis sativa` is one of the stronger inherited IDs in the local corpus and the process profile fits the plant well",
        risk="safe",
        confidence="high on triple-essence double-locking and dual-output discipline",
        visual_grammar=[
            "`flat root with stalk-to-leaf-center rise` = one of the local corpus' clearer cannabis-class visual supports",
            "`outer-bifolio pairing with f9r` = hot-lock opening on one face answered by long controlled intoxicant processing on the other",
            "`single title line` = explicit threshold-label behavior inside Quire B rather than an accidental scribal flourish",
            "`dense second paragraph` = local structure agrees with a page whose decisive work happens after the label rather than before it",
        ],
        full_eva="""
P1.1: pocheody.qopchey.sykaiin.opchydor.ychy.daiin.dy.chor.orom-
P1.2: ychykchy.otly.kol.shor.ody.otody.qoy.oeesordy-
P1.3: ydor.sheal.okchy.qoy.koiin.choky.ykair=
T1.4: dainod.ychealod=
P2.5: tchor.chor.chl.ykch.chocthy.opchy.ty.ty-
P2.6: oshaiin.dyky.oeees.deeeod.aiin.d.toaiin-
P2.7: daiin.dalchy.dy.ky.s.chy.s.aiin.doal.qoky-
P2.8: shotchy.ydain.yky.shody.otol.daiin-
P2.9: saiin.ytaiin=
P2.10: toror.daly.dal.opchy.fchol.ypcho*.okal-
P2.11: sokchy.qokol.choty.okchy.cthy.chy.kchy-
P2.12: dy.chokchy.shcthy.shtshy.sho.tchokyd-
P2.13: qok*or.dl.dy.shey=
""",
        core_vml=[
            "`T1.4` = explicit title-line certification inside a highly technical herb page",
            "`oeees.deeeod` = raw triple essence transformed into double-locked triple essence on one line",
            "`ty.ty` = doubled driven energy rather than simple repetition",
            "`saiin.ytaiin` = salt completion and moist-driven completion paired as a miniature product close",
            "`fchol` returns only late = fire-fluid correction is delayed until after essence and salt discipline have been established",
            "`qok*or` preserves damage in the terminal outlet line instead of smoothing it away",
        ],
        groups=[
            {"label": "P1", "title": "Paragraph 1 and title - intake, outlet shaping, and folio certification", "line_ids": ["P1.1", "P1.2", "P1.3", "T1.4"]},
            {"label": "P2", "title": "Paragraph 2 - driven concentration, salt closure, and late fire-fluid correction", "line_ids": ["P2.5", "P2.6", "P2.7", "P2.8", "P2.9", "P2.10", "P2.11", "P2.12", "P2.13"]},
        ],
        lines=[
            ("P1.1", "pocheody.qopchey.sykaiin.opchydor.ychy.daiin.dy.chor.orom", "`pocheody` pressed volatile-essence heat-fix active; `qopchey` extracted pressed volatile essence active; `sykaiin` salt-contained completion; terminal `orom` vessel-outlet-heat vessel.", "Open by pressing and extracting the volatile essence while already containing the salt side of the route and steering the product toward a vessel outlet.", "pressed intake into vessel-oriented outlet", "strong"),
            ("P1.2", "ychykchy.otly.kol.shor.ody.otody.qoy.oeesordy", "`ychykchy` moist volatile body-active; `otly` timed fluid active; `kol` body-fluid; `ody/otody` heat-fix and timed heat-fix; `oeesordy` essence spike tied to fixed outlet law.", "Keep the moist body-fluid alive while converting the first essence surge into a controlled fixed outlet rather than letting it bloom freely.", "early essence-to-outlet control", "mixed"),
            ("P1.3", "ydor.sheal.okchy.qoy.koiin.choky.ykair", "`ydor` moist fixed outlet; `sheal` transition-essence structure; `okchy` heated contained body-active; `koiin` body cycle complete; `ykair` moist contained timed root.", "Return the first outlet stream to a contained body and timed root address so the extraction stays grounded before certification.", "rooted body-containment reset", "strong"),
            ("T1.4", "dainod.ychealod", "`dainod` complete heat-fix; `ychealod` moist volatile essence structure-fix.", "Certify the page as a completed structured volatile route before the main concentration corridor begins.", "title-line certification", "strong"),
            ("P2.5", "tchor.chor.chl.ykch.chocthy.opchy.ty.ty", "`tchor` driven outlet; `chor` outlet heat; `chl` fluid dissolve; `ykch` moist contained body-active; `chocthy` volatile heat conduit bind; `ty.ty` doubled driven energy.", "Restart the second paragraph under doubled drive, binding the volatile fluid to the conduit while the body remains actively contained.", "double-driven conduit restart", "strong"),
            ("P2.6", "oshaiin.dyky.oeees.deeeod.aiin.d.toaiin", "`oshaiin` heated transition complete; `dyky` fixed contained active; `oeees` triple essence; `deeeod` double-locked triple essence; `toaiin` driven heat cycle complete.", "This is the folio's decisive line: triple essence is not merely reached but reworked into a double-locked state and then completed under driven heat-cycle law.", "triple-essence to double-lock conversion", "strong"),
            ("P2.7", "daiin.dalchy.dy.ky.s.chy.s.aiin.doal.qoky", "`daiin` checkpoint; `dalchy` fixed-structure active; `dy.ky` fixed contained-active body; salt and volatile markers flank `aiin`; `doal` fixed heated structure-fluid; `qoky` extracted contained active.", "After the essence spike, the page rebuilds structure, containment, and salt balance so the extract can remain active without destabilizing.", "post-spike structural rebalance", "mixed"),
            ("P2.8", "shotchy.ydain.yky.shody.otol.daiin", "`shotchy` transition-driven volatile active; `ydain` moist completion; `yky` moist contained active; `shody` transition heat-fix active; `otol` timed heated fluid; `daiin` checkpoint.", "Move the active volatile through a moist transitional correction and then checkpoint the timed fluid body that results.", "moist transition correction", "strong"),
            ("P2.9", "saiin.ytaiin", "`saiin` salt cycle complete; `ytaiin` moist-driven completion.", "Certify the salt fraction as a completed partner stream before reintroducing harder fire logic.", "salt-side miniature close", "strong"),
            ("P2.10", "toror.daly.dal.opchy.fchol.ypcho*.okal", "`toror` driven heat outlet heat outlet; `daly/dal` active structure then fixed structure; `opchy` pressed volatile active; `fchol` fire-fluid; damaged `ypcho*`; `okal` heated contained structure.", "Only after completion markers does the page reopen under fire-fluid correction, turning the pressed volatile back into heated contained structure while keeping the damaged token visible.", "late fire-fluid structural correction", "strong"),
            ("P2.11", "sokchy.qokol.choty.okchy.cthy.chy.kchy", "`sokchy` salt-contained body-active; `qokol` extracted contained fluid; `choty` volatile heat driven active; `okchy` heated contained body-active; `cthy` conduit bind; terminal `kchy` body-volatile active.", "Rejoin salt, extract, conduit, and body-volatile handling so the corrected product remains embodied rather than merely distilled away.", "rejoined embodied extract", "strong"),
            ("P2.12", "dy.chokchy.shcthy.shtshy.sho.tchokyd", "`dy` fixed; `chokchy` volatile heat-contained body-active; `shcthy` transition conduit bind; `shtshy` transition-driven transition active; `tchokyd` driven volatile heat-contained active-fix.", "Fix the embodied volatile again and run it through one more transition-heavy conduit corridor before the last close.", "transition-heavy refixation", "mixed"),
            ("P2.13", "qok*or.dl.dy.shey", "damaged `qok*or` extracted contained outlet; `dl` fixed fluid; `dy` fixed; `shey` transition essence active.", "Close with a damaged-but-preserved extracted outlet whose fluid and fixity are both explicit, leaving the transition essence active but governed.", "damaged governed terminal outlet", "mixed"),
        ],
        tarot_cards=["The Magician", "Justice", "The Emperor", "The Hierophant", "The Chariot", "Strength", "Temperance", "The Hermit", "The Star", "Judgment", "The Lovers", "Death", "The World"],
        movements=["press the intake", "discipline the first essence", "return to the root", "certify the page", "restart under doubled drive", "double-lock the triple essence", "rebuild the structure", "correct the moist transition", "complete the salt side", "reopen the fire-fluid route", "rejoin body and extract", "refix the embodied volatile", "close on governed damage"],
        direct="`f16r` is a cannabis-class essence page whose real achievement is not intoxication but control. It reaches triple essence, relocks that essence into `deeeod`, certifies a separate salt completion, and only then allows late fire-fluid correction before the final governed outlet.",
        math="Across the formal lenses, `f16r` behaves like a concentration-and-relocking controller with a labeled regime break. The page first establishes a stable intake manifold, then passes through a high-energy triple-essence operator, then projects the result back into structured, salt-balanced, body-bearing subspaces before termination.",
        mythic="Across the mythic lenses, `f16r` is the leaf where power is not denied but trained. The bright spirit is asked to become lawful enough to live in a vessel.",
        compression="Press the cannabis route, turn triple essence into double-locked triple essence, certify the salt fraction, reopen late fire-fluid correction, and close the embodied outlet under control.",
        typed_state_machine=r"""
\[\mathcal R_{f16r} = \{r_{\mathrm{intake}}, r_{\mathrm{label}}, r_{\mathrm{triple}}, r_{\mathrm{relock}}, r_{\mathrm{saltclose}}, r_{\mathrm{latefire}}\}\]
\[\delta(e_{\mathrm{T1.4}}): r_{\mathrm{intake}} \to r_{\mathrm{label}}\]
\[\delta(e_{\mathrm{oeees \to deeeod}}): r_{\mathrm{label}} \to r_{\mathrm{triple}} \to r_{\mathrm{relock}}\]
\[\delta(e_{\mathrm{saiin.ytaiin}}): r_{\mathrm{relock}} \to r_{\mathrm{saltclose}} \to r_{\mathrm{latefire}}\]
""",
        invariants=r"""
\[N_{\mathrm{title}}(f16r)=1, \qquad N_{\mathrm{oeees}}(f16r)=1, \qquad N_{\mathrm{deeeod}}(f16r)=1\]
\[N_{\mathrm{ty.ty}}(f16r)=1, \qquad N_{\mathrm{fchol}}(f16r)=1, \qquad N_{\mathrm{daiin/dain/aiin}}(f16r)\ge 8\]
""",
        theorem=r"""
\[\rho_* = (\Psi_{P2} \circ \Psi_{P1})(\rho_0)\]

The formal theorem of `f16r` is:

1. the page explicitly certifies its own route before deep concentration begins
2. triple essence is admissible only if it is immediately relocked into `deeeod`
3. salt completion forms a parallel stability channel rather than a decorative afterthought
4. late fire-fluid correction is allowed only after essence and salt have both been disciplined
""",
        crystal_contribution=[
            "double-locked triple-essence station",
            "title-line certification threshold",
            "doubled-driven concentration line",
            "salt-side miniature closure",
            "late fire-fluid correction route",
        ],
        pointer_title="Double-Locked Triple-Essence Cannabis",
        pointer_position="the recto close of the `f9/f16` outer Quire B bifolio and answer to the hot-lock opener on `f9r`",
        pointer_page_type="single-herb controlled intoxicant extraction page with one title line and one decisive triple-essence conversion",
        pointer_conclusion="`T1.4`, `oeees -> deeeod`, `ty.ty`, `saiin.ytaiin`, and late `fchol`",
        pointer_judgment="`f16r` teaches that cannabis power is not useful when merely intensified. It becomes medicinal only when triple essence is relocked, the salt stream is separately closed, and the late fire-fluid route remains governed.",
    ),
    make_folio(
        folio_id="F016V",
        quire="B",
        bifolio="bB1 = f9 + f16",
        manuscript_role="maximum-press safflower-thistle oil page with graduated fixation and quire-closing heat maximum",
        purpose="`f16v` is the final surviving page of Quire B and it behaves like a deliberate quire close. The page carries one of the heaviest `pch-` concentrations in the translated corpus, doubles `chkar`, doubles `okaiin`, moves through `dal -> dan -> dairin`, and saves `oaoror` for the last line as a terminal heat-maximum seal. Rather than intensifying essence the way `f16r` does, this page keeps pressing, binding, and heating an oil-bearing body until fixation, form, and heat can agree.",
        zero_claim="Press the thistle/oil route harder than the earlier leaves, graduate the fixation from `dal` to `dan` to `dairin`, verify the doubled contained body twice over, and close the quire under maximum heat-outlet law.",
        botanical="`Carthamus lanatus` / safflower thistle remains moderate, but the oil-pressing profile is strong",
        risk="moderate",
        confidence="high on maximum pressing and graduated fixation",
        visual_grammar=[
            "`final surviving Quire B leaf` = codicological position agrees with deliberate closure pressure",
            "`ordinary Herbal A drawing` = visual calm masking a highly mechanical pressing page",
            "`paired with f9v on the outer bifolio` = internal fire aromatic work at the opening answered by maximum pressing at the close",
            "`thistle-class form` = local corpus plant guess aligns with an oil-bearing, pressure-loving process profile",
        ],
        full_eva="""
P1: pchroiin.otchor.chpchol.chpchey.s.pcho*y-
P2: ytchor.y.ky.chokchy.qokchocthor.shory-
P3: ykchy.dy.choy.qoty.chykchy.koshet-
P4: dchol.chcthody.cphod.chotol.dal-
P5: ytchy.chyty.chor.chol.ykchy.dan-
P6: sor.chkar.oty.chkar.chol.dairin=
P7: pchocth.chypchy.qotchy.ch*y.sy-
P8: daiin.chol.y.daiin.chcthy.qot.char.chor.sholo-
P9: dshy.okaiin.okaiin.chol.chor.cthor.ty.chody-
P10: qokchy.chy.dy.ykchy.chckhy.otain.cthor.*y-
P11: okytaiin.chkchy.saiin-
P12: daiin.yky.otor.chody-
P13: sokar.oaoror=
""",
        core_vml=[
            "`pch-` dominance = maximum press / squeeze logic rather than gentle maceration",
            "`chkar.chkar` = duplicated carrier-body route in the quire-closing core line",
            "`okaiin.okaiin` = doubled contained completion, unusually explicit",
            "`dal -> dan -> dairin` = graduated fixation sequence across the page",
            "`koshet` = resistant or obstructive pocket preserved as such, not normalized away",
            "`oaoror` = terminal heat-maximum quire close",
        ],
        groups=[
            {"label": "P1", "title": "Paragraph 1 - pressure intake and first structure gradient", "line_ids": ["P1", "P2", "P3", "P4", "P5", "P6"]},
            {"label": "P2", "title": "Paragraph 2 - doubled containment, salt completion, and heat-maximum close", "line_ids": ["P7", "P8", "P9", "P10", "P11", "P12", "P13"]},
        ],
        lines=[
            ("P1", "pchroiin.otchor.chpchol.chpchey.s.pcho*y", "`pchroiin` pressed heat-cycle; `otchor` timed outlet; `chpchol/chpchey` pressed volatile fluid and pressed volatile essence; damaged `pcho*y` preserved.", "Open by pressing the source into both fluid and essence forms at once, while keeping the damaged press token visible as evidence rather than noise.", "maximum-pressure intake", "strong"),
            ("P2", "ytchor.y.ky.chokchy.qokchocthor.shory", "`ytchor` moist-driven outlet; `y.ky` moist active contained body; `chokchy` volatile heat-contained body-active; `qokchocthor` extracted contained volatile conduit outlet; `shory` transition outlet active.", "Keep the pressed body moist and contained while pushing the extract through a bound outlet corridor instead of a free pour.", "moist bound outlet corridor", "strong"),
            ("P3", "ykchy.dy.choy.qoty.chykchy.koshet", "`ykchy` moist contained body-active; `dy` fixed; `choy` volatile heat active; `qoty` transmuted driven active; `koshet` resistant obstructive token.", "The page acknowledges resistance directly: the active volatile is fixed and driven, but the obstruction remains part of the process rather than vanishing from the record.", "resistance-aware fixing line", "mixed"),
            ("P4", "dchol.chcthody.cphod.chotol.dal", "`dchol` fixed volatile fluid; `chcthody` volatile conduit heat-fix active; `cphod` alembic heat-fix; `chotol` volatile heat-fluid; `dal` fixed structure.", "Convert the pressed volatile into structured fluid under conduit and alembic governance, landing the first clear structural fixation marker.", "first structural landing", "strong"),
            ("P5", "ytchy.chyty.chor.chol.ykchy.dan", "`ytchy` moist-driven active; `chyty` volatile active-driven active; `chor/chol` outlet and fluid; `ykchy` moist contained body-active; `dan` fixed joined state.", "Escalate from fixed structure toward joined form, showing that the oil route must become relational before it can close.", "structure-to-union gradient", "strong"),
            ("P6", "sor.chkar.oty.chkar.chol.dairin", "`sor` salt outlet; `chkar` volatile body-root; `oty` timed active; repeated `chkar`; `dairin` timed fixation complete.", "This line doubles the body-root carrier and times the fix so the route can survive as a real stored preparation.", "doubled body-root timed fix", "strong"),
            ("P7", "pchocth.chypchy.qotchy.ch*y.sy", "`pchocth` pressed volatile conduit bind; `chypchy` volatile-active pressed body-active; `qotchy` transmuted driven volatile; damaged `ch*y`; `sy` dissolve active.", "Restart under press-conduit logic and keep even the damaged volatile token inside a dissolving but governed route.", "press-conduit restart with damage", "mixed"),
            ("P8", "daiin.chol.y.daiin.chcthy.qot.char.chor.sholo", "`daiin` twice; `chol` volatile fluid; `chcthy` volatile conduit bind; `qot` transmuted heat; `char/chor` volatile root and outlet; `sholo` transition fluid outlet.", "Checkpoint the fluid twice, then send it through conduit, root, and outlet addresses so the pressed oil does not collapse into a single uncontrolled stream.", "double-checkpoint redistribution", "strong"),
            ("P9", "dshy.okaiin.okaiin.chol.chor.cthor.ty.chody", "`dshy` fixed transition active; doubled `okaiin`; `chol/chor` fluid and outlet; `cthor` conduit outlet; `ty` driven energy; `chody` volatile heat-fix active.", "The folio's containment thesis becomes explicit here: double completion comes before the final driven heating and fixation.", "doubled completion thesis", "strong"),
            ("P10", "qokchy.chy.dy.ykchy.chckhy.otain.cthor.*y", "`qokchy` extracted contained body-active; `dy`; `ykchy`; `chckhy` valve-active body-volatile; `otain` timed completion; damaged terminal `*y`.", "Extract and fix the body again, then put it under valve law before permitting timed completion.", "valve-governed penultimate extraction", "strong"),
            ("P11", "okytaiin.chkchy.saiin", "`okytaiin` heated contained moist-driven completion; `chkchy` volatile body-active; `saiin` salt cycle complete.", "Heat-contained completion and salt completion are paired so the product is both bodily and minerally stabilized.", "salted heated completion", "strong"),
            ("P12", "daiin.yky.otor.chody", "`daiin` checkpoint; `yky` moist contained active; `otor` timed heated outlet; `chody` volatile heat-fix active.", "Checkpoint the nearly finished product one last time before the quire-closing heat maximum.", "pre-close verification", "strong"),
            ("P13", "sokar.oaoror", "`sokar` salt body-root; `oaoror` heat-maximum outlet-heat outlet.", "Close Quire B by fusing salt, body-root, and maximum heat-outlet law into one terminal seal.", "heat-maximum quire close", "strong"),
        ],
        tarot_cards=["The Emperor", "The Chariot", "Strength", "Justice", "The Lovers", "Temperance", "The Hermit", "Wheel of Fortune", "Judgment", "The Hierophant", "The Star", "The Sun", "The World"],
        movements=["press the oil route", "bind the moist outlet", "work through resistance", "land the first structure", "join the route", "double the body-root carrier", "restart under conduit pressure", "checkpoint and redistribute", "double the completion", "put the product under valve law", "pair heat with salt completion", "verify before closure", "seal at maximum heat"],
        direct="`f16v` is Quire B's oil-pressing close. It values pressure, duplication, and graded fixation more than sudden concentration, and it ends by proving that the quire can close under `oaoror` only after the body-root and salt fractions have both been disciplined.",
        math="Across the formal lenses, `f16v` behaves like a pressure-dominated control problem with monotone structural ascent. The state is pressed into multiple coupled channels, then carried through a graded sequence of structural attractors until it reaches doubled completion and a terminal heat-maximum seal.",
        mythic="Across the mythic lenses, `f16v` is the page where patience becomes pressure. The medicine is squeezed until it finally agrees to hold together.",
        compression="Press harder, climb from `dal` to `dan` to `dairin`, double the contained completion, pair it with salt, and close Quire B under `oaoror`.",
        typed_state_machine=r"""
\[\mathcal R_{f16v} = \{r_{\mathrm{press}}, r_{\mathrm{structure}}, r_{\mathrm{union}}, r_{\mathrm{doublecomplete}}, r_{\mathrm{heatmax}}\}\]
\[\delta(e_{\mathrm{dal \to dan \to dairin}}): r_{\mathrm{press}} \to r_{\mathrm{structure}} \to r_{\mathrm{union}}\]
\[\delta(e_{\mathrm{okaiin.okaiin}}): r_{\mathrm{union}} \to r_{\mathrm{doublecomplete}} \to r_{\mathrm{heatmax}}\]
""",
        invariants=r"""
\[N_{\mathrm{pch}}(f16v)\ge 4, \qquad N_{\mathrm{chkar}}(f16v)=2, \qquad N_{\mathrm{okaiin}}(f16v)=2\]
\[N_{\mathrm{dal}}(f16v)=1, \qquad N_{\mathrm{dan}}(f16v)=1, \qquad N_{\mathrm{dairin}}(f16v)=1, \qquad N_{\mathrm{oaoror}}(f16v)=1\]
""",
        theorem=r"""
\[\rho_* = (\Psi_{P2} \circ \Psi_{P1})(\rho_0)\]

The formal theorem of `f16v` is:

1. Quire B closes on pressure and graded fixation rather than on a new apparatus novelty
2. body-root carrying is doubled before the product is allowed to become terminal
3. doubled containment and salt completion are the immediate preconditions of the close
4. `oaoror` marks not merely strong heat but the quire's chosen maximum admissible outlet law
""",
        crystal_contribution=[
            "maximum-press oil station",
            "graded fixation ascent line",
            "doubled body-root carrier route",
            "double-completion containment gate",
            "heat-maximum quire closure",
        ],
        pointer_title="Maximum-Press Oil Closure",
        pointer_position="the verso close of the `f9/f16` outer Quire B bifolio and final surviving page of the quire",
        pointer_page_type="single-herb oil-pressing closure page with doubled containment and terminal heat maximum",
        pointer_conclusion="heavy `pch-`, `chkar.chkar`, `okaiin.okaiin`, `dal -> dan -> dairin`, and `oaoror`",
        pointer_judgment="`f16v` finishes Quire B by squeezing the route through repeated containment and graded fixation until maximum heat can close it without breaking it.",
    ),
    make_folio(
        folio_id="F017R",
        quire="C",
        bifolio="bC1 = f17 + f24",
        manuscript_role="Quire C open-ended vessel-packing page with calcination and zero completion markers",
        purpose="`f17r` opens Quire C by refusing the closure habits of Quire B. No `daiin`, `dain`, or `daim` completions appear at all. Instead the page saturates itself with `-om` vessel terminals and `-am` union terminals, names `qof` in the middle as direct fire-inside-retort logic, and keeps staging the material instead of finishing it. The page reads like a preparation or loading folio for a more complex extraction sequence rather than a self-contained product leaf.",
        zero_claim="Load, bind, and combine the source into vessels, fire it internally with `qof`, and keep the route open-ended on purpose because this folio is preparing a later completion rather than producing one now.",
        botanical="`Catananche caerulea` / Cupid's dart remains moderate; the preparatory process profile is stronger than the species fit",
        risk="moderate",
        confidence="high on open-ended vessel staging and calcination",
        visual_grammar=[
            "`first surviving Quire C leaf` = codicological threshold behavior aligns with a new regime",
            "`zero completion markers` = the strongest structural signature on the page, stronger than any plant guess",
            "`-om and -am density` = vessel and union terminals dominate the reading even before line-level parsing",
            "`paired with f24 on the outer bifolio` = staging and later answer are structurally implied by placement",
        ],
        full_eva="""
P1: fshody.daram.ydar.chom.opydy.ypod.otchy.dody.oldckhy-
P2: odair.choky.okshy.qodar.ckhody.dor.otchol.qodcthy.ods-
P3: chol.or.chy.qodam.okor.chor.okchom=
P4: tchom.shol.qokol.qor.olaiin.otydd.som.ypchy.ypaim-
P5: ychekchy.cthy.chor.shor.cphor.cphaldy.dair.otay.qody-
P6: tsho.qof.cho.qokcheor.choto*=
P7: ksheo.qokchy.choldshy.mpchy.d*.opchordy-
P8: dchchy.dychear.schar.ykchy-
P9: siiiry.chckhy.o.das.chypcham-
P10: dar.chear.dcheor.*ain.y.dol-
P11: otchol.cthar.okaiin.chol.doiiin-
P12: ychody.chotom=
""",
        core_vml=[
            "`N_{completion}=0` = no `daiin`, `dain`, or `daim` anywhere on the folio",
            "`-om` saturation = vessel terminals dominate the page",
            "`-am` saturation = unions are staged but not yet resolved into completed product",
            "`qof` = explicit internal fire / calcination event near the structural center of the folio",
            "`fshody` = quire-opening transition heat-fix signal",
            "`siiiry`, `mpchy`, and `doiiin` = unusual staging tokens kept visible rather than flattened",
        ],
        groups=[
            {"label": "P1", "title": "Paragraph 1 - vessel loading and union staging", "line_ids": ["P1", "P2", "P3", "P4", "P5", "P6"]},
            {"label": "P2", "title": "Paragraph 2 - calcination aftermath and still-open vessel route", "line_ids": ["P7", "P8", "P9", "P10", "P11", "P12"]},
        ],
        lines=[
            ("P1", "fshody.daram.ydar.chom.opydy.ypod.otchy.dody.oldckhy", "`fshody` transition heat-fix active; `daram` fixed root union; `chom` volatile vessel; `opydy/ypod/dody` pressed active-fix clusters; `oldckhy` fluid-fixed valve-active body.", "Open Quire C not by closing anything, but by fixing the source into union and vessel form while already preparing a valve-governed body.", "quire-opening vessel staging", "strong"),
            ("P2", "odair.choky.okshy.qodar.ckhody.dor.otchol.qodcthy.ods", "`odair` timed heat-fix; `choky` volatile heat-contained active; `okshy` heated contained transition active; `qodar` extracted heat-root; `ckhody` valve-active heat-fix; `qodcthy` extracted heat conduit bind.", "Load the route through containment, root extraction, and valve-governed bind without granting it completion language.", "contained root-extract bind", "strong"),
            ("P3", "chol.or.chy.qodam.okor.chor.okchom", "`chol.or.chy` volatile fluid outlet active; `qodam` extracted heat union; `okor/chor` heated contained outlet and outlet heat; `okchom` heated contained vessel.", "This line makes the page's thesis explicit: extraction is being joined to vessel form, not finished into product.", "extraction-to-vessel union", "strong"),
            ("P4", "tchom.shol.qokol.qor.olaiin.otydd.som.ypchy.ypaim", "`tchom` driven volatile vessel; `shol` transition fluid; `qokol` extracted contained fluid; `qor` extracted outlet heat; `som` salt vessel; `ypaim` moist pressed union.", "Drive the volatile into vessels and unions while salt, fluid, and press logic all remain active and unresolved.", "driven vessel-loading corridor", "mixed"),
            ("P5", "ychekchy.cthy.chor.shor.cphor.cphaldy.dair.otay.qody", "`ychekchy` moist volatile essence body-active; `cthy` conduit bind; `chor/shor` outlet heat and transition outlet; `cphor` alembic outlet; `cphaldy` alembic-structure-fix active; `dair` timed fixation.", "The page momentarily looks like a normal distillation leaf, but every route is still being staged for later use rather than terminally closed.", "apparent distillation without closure", "strong"),
            ("P6", "tsho.qof.cho.qokcheor.choto*", "`tsho` driven transition outlet; `qof` internal fire-fluid; `cho` volatile heat; `qokcheor` extracted contained volatile essence outlet; damaged `choto*` timed volatile fluid.", "At the center of the page, direct fire is introduced inside the apparatus, but even here the outcome is an outlet state, not a finished completion.", "calcination centerline", "strong"),
            ("P7", "ksheo.qokchy.choldshy.mpchy.d*.opchordy", "`ksheo` contained transition essence outlet; `qokchy` extracted contained body-active; `choldshy` volatile fluid fixed-transition active; `mpchy` compressed pressed body-active; damaged `d*`; `opchordy` pressed outlet fixed active.", "After calcination, the page keeps compressing and repacking the route instead of settling it, as though the fired material still has another life ahead.", "post-calcination repacking", "mixed"),
            ("P8", "dchchy.dychear.schar.ykchy", "`dchchy` fixed volatile body-active; `dychear` fixed essence-root; `schar` salt body-root; `ykchy` moist contained body-active.", "Fix body and root relations without letting those relations become terminal completion markers.", "root-body fixation without closure", "strong"),
            ("P9", "siiiry.chckhy.o.das.chypcham", "`siiiry` extended completion-like stream without real closure; `chckhy` valve-active body-volatile; `das` fixed salt; `chypcham` volatile-active pressed union.", "Even the strangest line on the page preserves the same logic: valve, salt, and union are present, but completion is still withheld.", "strange-token valve union", "mixed"),
            ("P10", "dar.chear.dcheor.*ain.y.dol", "`dar` root fix; `chear` volatile essence root; `dcheor` fixed volatile essence outlet; damaged `*ain`; `y.dol` moist active fixed fluid.", "Root and essence are bound together again, but the page still stops short of the normal complete-state vocabulary.", "root-essence return", "mixed"),
            ("P11", "otchol.cthar.okaiin.chol.doiiin", "`otchol` timed volatile fluid; `cthar` conduit root; `okaiin` heated contained completion-like state; `doiiin` fixed heat cycle chain.", "The folio comes nearest to ordinary closure here, but even this near-complete state remains a timed staging corridor rather than a finished terminal.", "near-completion staging", "strong"),
            ("P12", "ychody.chotom", "`ychody` moist volatile heat-fix active; `chotom` volatile heat-fluid vessel.", "End by leaving the material inside a heated vessel body, ready for whatever Quire C intends next.", "heated vessel open close", "strong"),
        ],
        tarot_cards=["The Fool", "The Magician", "Justice", "The Chariot", "Temperance", "Strength", "The Hermit", "Wheel of Fortune", "The Moon", "Death", "Judgment", "The World"],
        movements=["open the quire with vessel law", "bind the root extract", "join extraction to vessel", "load the vessels under salt and press", "distill without terminal closure", "ignite the internal fire", "repack after calcination", "fix root and body relations", "hold the strange valve union", "return essence to root", "approach completion without crossing it", "leave the material in the heated vessel"],
        direct="`f17r` is not a normal finished herbal page. It is a staging leaf that loads matter into vessels, fires it internally, and refuses closure vocabulary because Quire C begins by preparing operations that will only complete later.",
        math="Across the formal lenses, `f17r` behaves like an open boundary-value problem. Most earlier folios converge to completed attractors; this one instead accumulates vessel, union, and bind operators while keeping the terminal completion projectors switched off.",
        mythic="Across the mythic lenses, `f17r` is the workshop before dawn. The vessels are loaded, the fire is lit, and nothing is declared finished because the real work is about to begin.",
        compression="Load the vessels, join the source, fire it internally with `qof`, and keep the route intentionally unfinished so Quire C can continue the work later.",
        typed_state_machine=r"""
\[\mathcal R_{f17r} = \{r_{\mathrm{load}}, r_{\mathrm{union}}, r_{\mathrm{calcine}}, r_{\mathrm{repack}}, r_{\mathrm{openvessel}}\}\]
\[\delta(e_{\mathrm{qof}}): r_{\mathrm{union}} \to r_{\mathrm{calcine}}\]
\[\delta(e_{\mathrm{chotom}}): r_{\mathrm{repack}} \to r_{\mathrm{openvessel}}\]
""",
        invariants=r"""
\[N_{\mathrm{daiin/dain/daim}}(f17r)=0, \qquad N_{\mathrm{-om}}(f17r)\ge 5, \qquad N_{\mathrm{-am}}(f17r)\ge 4\]
\[N_{\mathrm{qof}}(f17r)=1, \qquad N_{\mathrm{fshody}}(f17r)=1, \qquad N_{\mathrm{calcination\ center}}(f17r)=1\]
""",
        theorem=r"""
\[\rho_* = (\Psi_{P2} \circ \Psi_{P1})(\rho_0)\]

The formal theorem of `f17r` is:

1. Quire C begins by suspending normal completion grammar
2. vessel and union terminals dominate because the folio is preparing state, not closing it
3. `qof` marks the decisive internal-fire intervention that changes the preparation without terminating it
4. the correct close is an open heated vessel rather than a completed medicine
""",
        crystal_contribution=[
            "open-ended vessel-packing station",
            "zero-completion boundary law",
            "internal-fire calcination line",
            "vessel-and-union saturation route",
            "heated-vessel open close",
        ],
        pointer_title="Open-Ended Vessel Packing",
        pointer_position="the recto opener of Quire C and first half of the `f17/f24` outer bifolio",
        pointer_page_type="single-herb preparatory page that stages vessels and unions rather than finished product",
        pointer_conclusion="no completion markers, `-om/-am` saturation, `qof`, `fshody`, and terminal `chotom`",
        pointer_judgment="`f17r` starts Quire C by withholding closure. The page packs, binds, calcines, and repacks matter into vessels because the quire wants preparation before resolution.",
    ),
    make_folio(
        folio_id="F017V",
        quire="C",
        bifolio="bC1 = f17 + f24",
        manuscript_role="extended essence-fluid distillation page with longest-line saturation and vessel-seal close",
        purpose="`f17v` answers the open staging page on the recto with Quire C's first great long-form distillation corridor. The leaf is the longest page in the first three quires, heavily saturates `-eol`, `-eey`, and `-eeor` essence-fluid markers, preserves rare signatures like `oteoloj`, moves through a mid-page heat chain, and culminates in `eees`, `qokeee`, and final `okeom`. Where `f17r` refuses completion, `f17v` shows how an extended route can keep moving until essence-fluid capture and vessel seal finally coincide.",
        zero_claim="Extend the volatile fluid route across many small contained corrections, preserve the essence-fluid saturation instead of simplifying it away, spike the late corridor into triple and quadruple essence states, and seal the capture inside a heated contained vessel.",
        botanical="`Fallopia convolvulus` / wild buckwheat remains moderate; the elongated distillation profile is stronger than the plant ID",
        risk="moderate",
        confidence="high on long-form essence-fluid distillation",
        visual_grammar=[
            "`23 lines` = the longest page in the first three quires, matching an intentionally extended process corridor",
            "`outer-bifolio pairing with f17r` = staging on the recto answered by a long operational release on the verso",
            "`ordinary Herbal A image` = visual understatement while the text carries unusually long operator density",
            "`late vessel seal` = quire-opening recto and verso form a deliberate open/closed pair",
        ],
        full_eva="""
P1: pchodol.chor.pchy.opydaiin.odaldy-
P2: ycheey.kshor.cthodal.okol.odaiin.okal-
P3: oldaim.odaiin.okal.oldaiin.chockhol.olol-
P4: kchor.fchol.cphol.olcheol.okeey-
P5: ychol.chol.dol.cheey.tchol.dar.ckhy-
P6: oekor.or.okaiin.or.otaiind-
P7: sor.chkeey.poiis.cheor.os.s.aiin-
P8: qokeey.kchor.ol.dy.choldaiin.sy-
P9: ycheol.shol.kchol.cholkaiin.ol-
P10: oytor.okeor.okor.okol.dair.ym-
P11: qokcheo.qokoiir.ctheol.chol-
P12: oy.choy.keaiin.chckhey.ol.chor-
P13: ykeor.chol.chol.cthol.chkor.sheol-
P14: olo.r.okeeol.chodaiin.okeol.tchory-
P15: ychor.cthy.cheeky.cheo.otor.oteol-
P16: okchol.chol.okeol.cthol.oteoloj-
P17: qoain.*ar.she.dol.qopchaiin.cthor-
P18: otar.cheeor.ol.chol.dor.chr.or.eees-
P19: dain.chey.qoaiin.cthor.chol.chom-
P20: ykeey.okeey.cheor.chol.sho.odaiin-
P21: oal.sheor.sholor.or.shecthy.peor.daiin-
P22: qokeee.dar.chey.keeor.cheeol.ctheoy.cthy-
P23: chkeey.okeor.shor.okeom=
""",
        core_vml=[
            "`23 lines` = the manuscript's first truly extended essence-fluid corridor",
            "`-eol/-eey/-eeor` saturation = essence-fluid and doubled-essence vocabulary dominates the leaf",
            "`oldaim.odaiin.okal.oldaiin` = explicit heat-chain and repeated completion cluster near the start",
            "`fchol` returns early = fire-fluid intervention remains active inside the distillation corridor",
            "`eees` and `qokeee` = late triple and extracted quadruple essence spikes",
            "`okeom` = heated contained vessel terminal that finally resolves the long route",
        ],
        groups=[
            {"label": "P1", "title": "Paragraph 1 - opening heat chain and first essence-fluid saturation", "line_ids": ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8"]},
            {"label": "P2", "title": "Paragraph 2 - middle corridor of repeated essence-fluid corrections", "line_ids": ["P9", "P10", "P11", "P12", "P13", "P14", "P15", "P16"]},
            {"label": "P3", "title": "Paragraph 3 - late concentration spike and vessel seal", "line_ids": ["P17", "P18", "P19", "P20", "P21", "P22", "P23"]},
        ],
        lines=[
            ("P1", "pchodol.chor.pchy.opydaiin.odaldy", "`pchodol` pressed volatile heat-fluid; `chor` outlet heat; `pchy` pressed active volatile; `opydaiin` pressed active completion; `odaldy` heat-structure-fix active.", "Open with a pressed volatile fluid that is already being shaped toward structured fixation rather than free dispersion.", "pressed fluid-structure opener", "strong"),
            ("P2", "ycheey.kshor.cthodal.okol.odaiin.okal", "`ycheey` moist double-essence active; `kshor` contained transition outlet; `cthodal` conduit heat-structure; `odaiin`; `okal` heated contained structure.", "Immediately saturate the route with doubled essence and structural containment so the long corridor starts inside discipline, not improvisation.", "double-essence structural intake", "strong"),
            ("P3", "oldaim.odaiin.okal.oldaiin.chockhol.olol", "`oldaim/odaiin/oldaiin` chained fluid-heat completions; `okal` heated contained structure; `chockhol` volatile contained fluid; `olol` doubled fluid.", "Run the manuscript's explicit early heat chain and then double the fluid itself, establishing that this page will extend rather than abbreviate the process.", "explicit heat-chain escalation", "strong"),
            ("P4", "kchor.fchol.cphol.olcheol.okeey", "`kchor` body-volatile outlet; `fchol` fire-fluid; `cphol` alembic fluid; `olcheol` fluid-volatile essence fluid; `okeey` heated contained double essence.", "Introduce fire-fluid and alembic logic without abandoning the essence-fluid saturation that defines the page.", "fire-fluid alembic saturation", "strong"),
            ("P5", "ychol.chol.dol.cheey.tchol.dar.ckhy", "`ychol/chol` moist volatile fluid and volatile fluid; `dol` fixed fluid; `cheey` volatile double essence; `tchol` driven volatile fluid; `dar` root fix; `ckhy` valve-active body.", "Keep the fluid moving through doubled essence, but root it and put it under valve law before it can disperse.", "rooted valve-governed fluid", "strong"),
            ("P6", "oekor.or.okaiin.or.otaiind", "`oekor` heated contained essence outlet; repeated `or`; `okaiin` heated contained completion; `otaiind` timed completion fixed.", "The page compresses outlet control into a short line, proving that long-form distillation is built from many tiny successful containments.", "short outlet-control compression", "mixed"),
            ("P7", "sor.chkeey.poiis.cheor.os.s.aiin", "`sor` salt outlet; `chkeey` volatile body-double essence; `poiis` pressed heat cycle; `cheor` volatile essence outlet; `os` heated dissolve; `aiin` completion.", "Salt briefly enters the corridor, but only as another way to support the essence outlet rather than diverting the page into a separate salt procedure.", "salt-assisted essence outlet", "mixed"),
            ("P8", "qokeey.kchor.ol.dy.choldaiin.sy", "`qokeey` extracted contained double essence; `kchor` body-volatile outlet; `ol` fluid; `dy` fixed; `choldaiin` volatile fluid completion; `sy` dissolve active.", "Extract the doubled essence, fix the fluid, and immediately keep it dissolving so the route does not harden too early.", "extracted double-essence fix", "strong"),
            ("P9", "ycheol.shol.kchol.cholkaiin.ol", "`ycheol` moist volatile essence fluid; `shol` transition fluid; `kchol` body-volatile fluid; `cholkaiin` volatile-fluid cycle complete; `ol` fluid.", "The middle corridor keeps braiding essence-fluid, transition-fluid, and body-fluid states instead of letting one dominate.", "middle-corridor fluid braid", "strong"),
            ("P10", "oytor.okeor.okor.okol.dair.ym", "`oytor` heated moist driven outlet; `okeor/okor` heated contained essence outlet and heated contained outlet; `okol` heated contained fluid; `dair` timed fixation; `ym` moist union.", "Outlet, essence, fluid, fixation, and union are compressed into one timed bundle so the long route can keep moving without losing form.", "timed union bundle", "strong"),
            ("P11", "qokcheo.qokoiir.ctheol.chol", "`qokcheo` extracted contained volatile essence outlet; `qokoiir` extracted contained heat-cycle root; `ctheol` conduit essence fluid; `chol` volatile fluid.", "Keep extraction and containment tied directly to essence-fluid transport, not to terminal collection.", "extract-to-essence-fluid transport", "strong"),
            ("P12", "oy.choy.keaiin.chckhey.ol.chor", "`oy/choy` heated moist active and volatile heat active; `keaiin` contained essence completion; `chckhey` valve-active body-double essence; `ol/chor` fluid and outlet.", "The page briefly proves that completion and valve-governed doubled essence can coexist inside the long corridor without ending it.", "completion without ending", "strong"),
            ("P13", "ykeor.chol.chol.cthol.chkor.sheol", "`ykeor` moist contained essence outlet; `chol.chol` doubled volatile fluid; `cthol` conduit fluid; `chkor` volatile contained outlet; `sheol` transition essence fluid.", "Double washing returns here as doubled fluid inside an essence-fluid corridor, not as simple cleanup.", "doubled washing in essence corridor", "strong"),
            ("P14", "olo.r.okeeol.chodaiin.okeol.tchory", "`olo` fluid-fluid; `okeeol` heated contained double-essence fluid; `chodaiin` volatile heat-fix complete; `okeol` heated contained essence fluid; `tchory` driven volatile outlet active.", "The corridor thickens into layered essence-fluid states while still preserving driven outlet activity.", "layered essence-fluid thickening", "strong"),
            ("P15", "ychor.cthy.cheeky.cheo.otor.oteol", "`ychor` moist volatile outlet; `cthy` conduit bind; `cheeky` volatile double-essence body-active; `cheo` volatile essence outlet; `otor` timed heated outlet; `oteol` timed essence fluid.", "This line is a compact summary of the whole page: outlet, conduit, doubled essence, timed heat, and timed essence-fluid all held together at once.", "whole-page miniature", "strong"),
            ("P16", "okchol.chol.okeol.cthol.oteoloj", "`okchol/chol` heated contained volatile fluid and volatile fluid; `okeol` heated contained essence fluid; `cthol` conduit fluid; `oteoloj` rare timed essence-fluid-vessel logic.", "Preserve the rare `oteoloj` rather than paraphrasing it away: the page is still moving toward vessel resolution, but in a distinctive idiom.", "rare timed vessel-fluid line", "mixed"),
            ("P17", "qoain.*ar.she.dol.qopchaiin.cthor", "`qoain` extracted heat-cycle complete; damaged `*ar`; `she` transition essence; `dol` fixed fluid; `qopchaiin` extracted pressed cycle complete; `cthor` conduit outlet.", "The late corridor restarts extraction under fixed fluid law, as though the long distillation must reconfirm itself before the final spike.", "late reconfirmation restart", "mixed"),
            ("P18", "otar.cheeor.ol.chol.dor.chr.or.eees", "`otar` timed root heat; `cheeor` volatile double-essence outlet; `ol/chol` fluid pair; `dor` fixed outlet; `eees` triple essence.", "After the long corridor, triple essence finally appears as a late event tied to timed root heat and double-essence outlet, not as an early burst.", "late triple-essence spike", "strong"),
            ("P19", "dain.chey.qoaiin.cthor.chol.chom", "`dain` completion; `chey` volatile essence active; `qoaiin` extracted heat-cycle complete; `cthor` conduit outlet; `chom` volatile vessel.", "The page now permits ordinary completion language because the essence has finally been directed into a vessel form.", "completion enters with vessel", "strong"),
            ("P20", "ykeey.okeey.cheor.chol.sho.odaiin", "`ykeey/okeey` moist double essence and heated contained double essence; `cheor` volatile essence outlet; `chol` fluid; `sho` transition; `odaiin` heat-fix complete.", "Double essence returns after completion, but now as a stabilized post-spike state rather than as raw escalation.", "post-spike double-essence stabilization", "strong"),
            ("P21", "oal.sheor.sholor.or.shecthy.peor.daiin", "`oal` heated structure-fluid; `sheor` transition essence outlet; `sholor` transition fluid outlet; `shecthy` transition essence conduit bind; `peor` pressed essence outlet; `daiin` completion.", "The page broadens outward one last time, letting structure-fluid, essence-outlet, and press-outlet all coexist before the final extraction spike.", "preterminal broad corridor", "strong"),
            ("P22", "qokeee.dar.chey.keeor.cheeol.ctheoy.cthy", "`qokeee` extracted contained quadruple essence; `dar` root fix; `chey` volatile essence active; `keeor` contained double-essence outlet; `cheeol` double-essence fluid; `ctheoy` conduit essence active moist; `cthy` conduit bind.", "This is the folio's culminating concentration theorem: extraction reaches quadruple essence, but the result is immediately re-rooted, fluidized, moistened, and bound.", "quadruple-essence culmination", "strong"),
            ("P23", "chkeey.okeor.shor.okeom", "`chkeey` volatile body-double essence; `okeor` heated contained essence outlet; `shor` transition outlet; `okeom` heated contained vessel.", "Seal the long distillation by carrying doubled essence through outlet transition into a heated contained vessel.", "heated contained vessel seal", "strong"),
        ],
        tarot_cards=["The Magician", "Strength", "Temperance", "The Chariot", "Justice", "The Hermit", "The Star", "The Moon", "The Emperor", "The Lovers", "Wheel of Fortune", "The Hierophant", "Death", "Judgment", "The Sun", "The High Priestess", "The Fool", "The Tower", "The World", "The Empress", "The Devil", "The Star", "The World"],
        movements=["press the volatile fluid into structure", "start inside doubled essence", "run the opening heat chain", "introduce fire-fluid without losing saturation", "root and valve the fluid", "compress outlet control", "salt the essence lightly", "extract the doubled essence", "braid the middle fluids", "bundle outlet and union", "transport extract into essence-fluid", "complete without ending", "wash the essence corridor twice", "thicken the layered fluids", "miniaturize the whole page", "preserve the rare vessel-fluid token", "restart late under fixed fluid law", "spike to triple essence", "allow completion into vessel", "stabilize the post-spike double essence", "broaden the final corridor", "culminate in quadruple essence", "seal in the heated vessel"],
        direct="`f17v` is Quire C's first great long distillation page. It turns the open vessel preparation of `f17r` into an extended essence-fluid corridor that slowly intensifies, then spikes late into `eees` and `qokeee`, and finally seals the captured product in `okeom`.",
        math="Across the formal lenses, `f17v` behaves like a long-horizon transport-and-concentration system with delayed nonlinear spikes. Most lines preserve local containment and fluid transport, while the late block introduces higher-order essence concentration before projection into a vessel attractor.",
        mythic="Across the mythic lenses, `f17v` is the pilgrimage page. The spirit does not leap to the vessel; it journeys through many small rooms until it is finally worthy of being housed.",
        compression="Sustain the essence-fluid corridor, preserve its many small corrections, spike late into `eees` and `qokeee`, and seal the final capture in `okeom`.",
        typed_state_machine=r"""
\[\mathcal R_{f17v} = \{r_{\mathrm{saturation}}, r_{\mathrm{middlecorridor}}, r_{\mathrm{latespike}}, r_{\mathrm{vesselseal}}\}\]
\[\delta(e_{\mathrm{eees}}): r_{\mathrm{middlecorridor}} \to r_{\mathrm{latespike}}\]
\[\delta(e_{\mathrm{qokeee}}): r_{\mathrm{latespike}} \to r_{\mathrm{vesselseal}}\]
""",
        invariants=r"""
\[N_{\mathrm{lines}}(f17v)=23, \qquad N_{\mathrm{eol/eey/eeor\ family}}(f17v)\ge 14, \qquad N_{\mathrm{chol}}(f17v)\ge 9\]
\[N_{\mathrm{fchol}}(f17v)=1, \qquad N_{\mathrm{eees}}(f17v)=1, \qquad N_{\mathrm{qokeee}}(f17v)=1, \qquad N_{\mathrm{okeom}}(f17v)=1\]
""",
        theorem=r"""
\[\rho_* = (\Psi_{P3} \circ \Psi_{P2} \circ \Psi_{P1})(\rho_0)\]

The formal theorem of `f17v` is:

1. Quire C's long distillation mode is built from repeated local containments, not from one dramatic leap
2. essence-fluid saturation is the governing background law of the page
3. the decisive concentration events are delayed until the late corridor, where `eees` and `qokeee` appear in sequence
4. vessel seal becomes admissible only after the concentrated essence has been re-rooted, fluidized, and rebound
""",
        crystal_contribution=[
            "extended essence-fluid distillation station",
            "longest-page saturation corridor",
            "late triple-to-quadruple essence line",
            "rare timed vessel-fluid route",
            "heated contained vessel seal",
        ],
        pointer_title="Extended Essence-Fluid Distillation",
        pointer_position="the verso opener of Quire C and long-corridor answer to the open vessel staging on `f17r`",
        pointer_page_type="single-herb long-form distillation page with 23 lines and late concentration spikes",
        pointer_conclusion="23-line corridor, early heat chain, `fchol`, late `eees`, `qokeee`, and final `okeom`",
        pointer_judgment="`f17v` is the first really long distillation atlas in the manuscript. It proves that the page can stay fluid for a long time, intensify only late, and still end in a contained vessel seal.",
    ),
]


def main() -> None:
    for folio in FOLIOS:
        (FOLIOS_DIR / f"{folio['folio_id']}_FINAL_DRAFT.md").write_text(render_folio(folio), encoding="utf-8")
        (FOLIOS_DIR / f"{folio['folio_id']}.md").write_text(render_pointer(folio), encoding="utf-8")


if __name__ == "__main__":
    main()
