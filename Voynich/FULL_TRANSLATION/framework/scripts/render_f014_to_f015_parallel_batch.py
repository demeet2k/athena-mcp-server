from __future__ import annotations

from render_f007_to_f008_parallel_batch import FOLIOS_DIR, render_folio, render_pointer
from render_f009_to_f010_parallel_batch import make_folio


FOLIOS: list[dict[str, object]] = [
    make_folio(
        folio_id="F014R",
        quire="B",
        bifolio="bB3 = f11 + f14",
        manuscript_role="systematic double-extraction root page with extended salt cycling",
        purpose="`f14r` is Quire B's explicit doubling page. The leaf verifies readiness in five tokens, then starts stacking repeated forms: `iiinykeey`, `soiiin`, `olol`, `dy.dy`, and final `kchy.kchy`. The page reads like a root extraction that refuses to trust a single pass, pushing dense matter through repeated fluid, fixation, and body-volatile handling until the extract can be sealed as a fully reworked body.",
        zero_claim="Verify readiness first, cycle the root through extended triple-i and salt refinement, repeat the major fluid and fixation moves, and close only after the body-volatile route itself has been doubled.",
        botanical="`Scorzonera hispanica` / black salsify remains moderate but plausible; root-process fit is stronger than taxonomic certainty",
        risk="moderate",
        confidence="high on systematic doubling and root extraction",
        visual_grammar=[
            "`two-plus leaf clusters` = ordinary Herbal A profile carrying a root-intensive technical page",
            "`taproot logic` = local corpus aligns the folio more with dense root matter than with delicate leaf work",
            "`bB3 pairing with f11` = safe precision on one bifolio face answered by deliberate doubled extraction on the other",
            "`13-line page` = one of the longer Quire B leaves, consistent with staged repetition",
        ],
        full_eva="""
P1: pchodaiin.chopol.shoiin.daiin.dain-
P2: iiinykeey.soiiin.chok.qokchy.da.okol-
P3: ydaiin.ol.chy.kchor.daiin.olol-
P4: ochkchor.kol.shy.daiin.dorody-
P5: qokchol.dar.dalo.qotolo-
P6: ychol.oir.okor.choor.ockhy-
P7: otcho.dain.chckhy=
P8: soshy.*chol.shor.cheor.ykaiin.s-
P9: sody.chody.otchody.qotchy.koiin.sy.sho.ty.dy-
P10: qotchor.chod.shoty.chody.dol.dy.dy.okchedy-
P11: dchokchy.schol.dy.shey.dar.qoty.ykeeyky-
P12: oeee*.chey.keor.chey.tchyky.chodalg-
P13: sodaiin.chy.kchy.kchy.ykeody=
""",
        core_vml=[
            "`daiin.dain` at the opening = readiness verification before true processing starts",
            "`iiinykeey` + `soiiin` = prolonged triple-cycle essence plus salt refinement",
            "`olol` = doubled fluid step",
            "`dy.dy` = doubled fixation in the late corridor",
            "`kchy.kchy` = doubled body-volatile handling in the terminal line",
            "`oeee*` = damaged triple-essence spike retained rather than normalized away",
        ],
        groups=[
            {"label": "P1", "title": "Paragraph 1 - readiness and first extraction cycles", "line_ids": ["P1", "P2", "P3", "P4", "P5", "P6", "P7"]},
            {"label": "P2", "title": "Paragraph 2 - salt refinement and doubling cascade", "line_ids": ["P8", "P9", "P10", "P11", "P12", "P13"]},
        ],
        lines=[
            ("P1", "pchodaiin.chopol.shoiin.daiin.dain", "`pchodaiin` pressed volatile heat-fix complete; `daiin.dain` double completion.", "Open by proving readiness and completion before the main extraction even begins.", "readiness verification opener", "strong"),
            ("P2", "iiinykeey.soiiin.chok.qokchy.da.okol", "`iiinykeey` prolonged triple-cycle double-essence route; `soiiin` salt triple-cycle; `qokchy` extract contain volatile active.", "Run the root through extended cycling and triple-pass salt refinement while keeping the extracted volatile contained.", "extended salt-cycle extraction", "strong"),
            ("P3", "ydaiin.ol.chy.kchor.daiin.olol", "`ydaiin` moist fix complete; `kchor` body-volatile outlet; `olol` doubled fluid.", "Moisten and complete the route, then explicitly repeat the fluid operation to keep the dense body workable.", "doubled fluid move", "strong"),
            ("P4", "ochkchor.kol.shy.daiin.dorody", "`ochkchor` heated volatile-contained outlet chain; `daiin`; `dorody` fix-outlet-heat-fix active.", "Carry the dense extract through outlet containment and re-fix the heated route after checkpointing it.", "heated outlet refixation", "strong"),
            ("P5", "qokchol.dar.dalo.qotolo", "`qokchol` extract contained volatile fluid; `dar` root fix; `dalo` fixed structure heat; `qotolo` double-heated fluid transmutation.", "Extract the volatile fluid from the root and move it into structured double-heated transmutation.", "root-to-structured-fluid turn", "strong"),
            ("P6", "ychol.oir.okor.choor.ockhy", "`ychol` moist volatile fluid; `oir` heat rotation; `okor/choor` doubled outlet heat; `ockhy` heated volatile containment.", "Rotate the moist fluid through repeated outlet-heating until the volatile can be contained again.", "rotational outlet heating", "mixed"),
            ("P7", "otcho.dain.chckhy", "`otcho` timed volatile heat; `dain` fix-complete; `chckhy` valve-active.", "Seal the first phase as a timed heated volatile that can survive valve governance.", "phase-one valve seal", "strong"),
            ("P8", "soshy.*chol.shor.cheor.ykaiin.s", "`soshy` salt-heat transition active; damaged `*chol`; `cheor` volatile essence outlet; `ykaiin` moist contain complete.", "Reopen under salt transition, keep the damaged volatile-fluid visible, and lead the route toward a moist contained essence outlet.", "salted restart with damage retained", "mixed"),
            ("P9", "sody.chody.otchody.qotchy.koiin.sy.sho.ty.dy", "`sody/chody/otchody` layered salt and volatile heat-fix; `qotchy` transmuted driven volatile; terminal `dy`.", "Stack salt-fix and volatile-fix operators until the route becomes a driven transmuted volatile fixed in motion.", "layered salt-fix corridor", "strong"),
            ("P10", "qotchor.chod.shoty.chody.dol.dy.dy.okchedy", "`qotchor` transmuted driven outlet; `dy.dy` doubled fixation; `okchedy` heated contained volatile essence fix active.", "Drive the outlet through emphatic doubled fixation and lock the essence into heated containment.", "doubled fixation climax", "strong"),
            ("P11", "dchokchy.schol.dy.shey.dar.qoty.ykeeyky", "`dchokchy` fixed contained volatile body; `schol` salt volatile fluid; `dar` root fix; `ykeeyky` moist double-essence contained active.", "Rebind the extract to root and salt-fluid while preserving a moist doubled-essence body.", "root-salt rebind", "strong"),
            ("P12", "oeee*.chey.keor.chey.tchyky.chodalg", "damaged `oeee*` triple essence; `chey` volatile essence active; `keor` contained essence outlet; `chodalg` volatile heat-fix structure.", "Spike the route into damaged-but-visible triple essence and force that concentration into structured fixation.", "damaged triple-essence spike", "mixed"),
            ("P13", "sodaiin.chy.kchy.kchy.ykeody", "`sodaiin` salt heat fix complete; `kchy.kchy` doubled body-volatile; `ykeody` moist contained essence heat-fix active.", "Close only after the body-volatile route itself has been processed twice and turned into a moist fixed essence.", "double body-volatile terminal", "strong"),
        ],
        tarot_cards=["Justice", "Wheel of Fortune", "Temperance", "Strength", "The Emperor", "The Chariot", "The Hermit", "The Star", "The Magician", "Judgment", "The Priestess", "The Moon", "The World"],
        movements=["verify readiness", "cycle the salt three times", "repeat the fluid pass", "refix the heated outlet", "draw from the root", "rotate the moist route", "seal the first phase", "restart with salt", "layer the fixes", "double-fix the outlet", "rebind root and salt", "spike triple essence", "close on doubled body"],
        direct="`f14r` is a systematic double-extraction page for dense root matter. The manuscript keeps announcing that one pass is not enough: the fluid is doubled, fixation is doubled, and the body-volatile track is doubled before the page is allowed to close.",
        math="Across the formal lenses, `f14r` behaves like an iterative refinement scheme for a stubborn root substrate. The page increases extraction reliability by repeating operators on the same state rather than by changing regime, so the dominant structure is repeated application with intermittent checkpoints and late concentration spikes.",
        mythic="Across the mythic lenses, `f14r` is the page that refuses haste. The root must be asked twice, then twice again, before it yields a trustworthy answer.",
        compression="Verify first, cycle long, repeat the fluid, repeat the fixation, repeat the body-volatile route, and only then seal the root extract.",
        typed_state_machine=r"""
\[\mathcal R_{f14r} = \{r_{\mathrm{ready}}, r_{\mathrm{cycle}}, r_{\mathrm{doublefix}}, r_{\mathrm{doublebody}}\}\]
\[\delta(e_{\mathrm{iiinykeey}}): r_{\mathrm{ready}} \to r_{\mathrm{cycle}}\]
\[\delta(e_{\mathrm{kchy.kchy}}): r_{\mathrm{doublefix}} \to r_{\mathrm{doublebody}}\]
""",
        invariants=r"""
\[N_{\mathrm{double}}(f14r)\ge 4, \qquad N_{\mathrm{daiin/dain}}(f14r)\ge 6, \qquad N_{\mathrm{salt}}(f14r)\ge 4\]
\[N_{\mathrm{iiinykeey}}(f14r)=1, \qquad N_{\mathrm{soiiin}}(f14r)=1, \qquad N_{\mathrm{oeee*}}(f14r)=1\]
""",
        theorem=r"""
\[\rho_* = (\Psi_{P2} \circ \Psi_{P1})(\rho_0)\]

The formal theorem of `f14r` is:

1. readiness is explicitly certified before the heavy route begins
2. extended cycling and salt refinement are the main engines of the first phase
3. the second phase turns repetition into method through doubled fluid, fixation, and body-volatile operators
4. the page closes only after the dense root substrate has been worked twice over at every major layer
""",
        crystal_contribution=[
            "systematic double-extraction station",
            "extended triple-cycle salt line",
            "doubled fluid and fixation corridor",
            "damaged triple-essence spike",
            "double body-volatile terminal",
        ],
        pointer_title="Systematic Double-Extraction",
        pointer_position="the recto of the third Quire B bifolio and partner to the fixation-saturated `f11v` leaf",
        pointer_page_type="single-root extraction page with extended cycling and overt doubling pattern",
        pointer_conclusion="`iiinykeey`, `soiiin`, `olol`, `dy.dy`, and `kchy.kchy`",
        pointer_judgment="`f14r` teaches that dense root matter must be worked more than once. The page is a controlled doctrine of repetition rather than a single-pass extraction.",
    ),
    make_folio(
        folio_id="F014V",
        quire="B",
        bifolio="bB3 = f11 + f14",
        manuscript_role="maximum-fixation moist wound-medicine page with triple consecutive closure pressure",
        purpose="`f14v` is the most fixation-obsessed page yet translated. The leaf floods itself with `-dy`, culminates in `dy.dy.dy`, saturates the route with moist-active and `-shy` transitions, and waits until the penultimate line to allow `dam`. The whole page behaves like a wet medicinal preparation that must stay active, unstable, and constantly corrected until the final valve-governed seal.",
        zero_claim="Keep the wound medicine moist and in motion, fix it over and over without letting it settle, unite it with its carrier only near the end, and close the live preparation under a final valve seal.",
        botanical="`Stachys monnieri` / wood betony is plausible in the local corpus, but the operational profile is stronger than the plant ID",
        risk="safe",
        confidence="high on wet fixation saturation and late carrier union",
        visual_grammar=[
            "`standard Herbal A drawing` = visual calm masking an unusually intense fixation page",
            "`paired with f11r` = aromatic precision on recto answered by moist wound-medicine stabilization on verso",
            "`9-line compression` = high operator density with very little descriptive slack",
            "`late union and valve close` = the text, not the image, carries the decisive structure",
        ],
        full_eva="""
P1: pdychoiin.yfodain.oty.chy.dy.ypchor.daiin.kol.ydain-
P2: okchor.d.chy.tshy.oty.chy.cthy.otchy.ty.chol.daiin-
P3: ychy.dy.daiin.chcthy.ykyaiin.dytchy.ykchy.kydy-
P4: ytychy.ksho.ykshy.shokshor.yty.darody.dy.otyds-
P5: okshy.daiin.okchor.chky.qotchy.daiin.cthor.oty-
P6: qoty.choky.cthy.chokchy.dy.dy.dy.chckhy.dchyd.n-
P7: oykshy.choky.dy.dy.odyd.otchy.o.kchy.dshy.dardy-
P8: chokshor.daiin.okshydy.daiin.dol.dair.dam-
P9: dykchy.ctholdg.dchckhy=
""",
        core_vml=[
            "`-dy` x14 = absolute maximum fixation count in the local corpus so far",
            "`dy.dy.dy` = unprecedented triple consecutive fixation",
            "`y-` and `-shy` saturation = moist, active, constantly transitioning preparation",
            "`odyd` = heat-fix-active-fix inversion of the earlier `dod` sandwich logic",
            "`dam` in the penultimate line = carrier union is delayed until the preparation is almost done",
            "`dchckhy` = fix-volatile-valve-active terminal",
        ],
        groups=[
            {"label": "P1", "title": "Paragraph 1 - moist active fixation corridor", "line_ids": ["P1", "P2", "P3", "P4", "P5"]},
            {"label": "P2", "title": "Paragraph 2 - triple fixation, late union, and valve seal", "line_ids": ["P6", "P7", "P8", "P9"]},
        ],
        lines=[
            ("P1", "pdychoiin.yfodain.oty.chy.dy.ypchor.daiin.kol.ydain", "`pdychoiin` pressed fixed volatile heat-cycle; `yfodain` moist fire heat-fix complete; `daiin`; `ydain` moist fix complete.", "Start with wet heat already under fixation and prove that the living preparation can survive both press and moisture at once.", "wet-heat fixation opener", "strong"),
            ("P2", "okchor.d.chy.tshy.oty.chy.cthy.otchy.ty.chol.daiin", "`okchor` heated contained volatile outlet; `tshy` driven transition active; `cthy` conduit bind; `daiin` checkpoint.", "Keep the moist volatile in active transition while forcing it through conduit governance and repeated verification.", "transition-bound moist route", "strong"),
            ("P3", "ychy.dy.daiin.chcthy.ykyaiin.dytchy.ykchy.kydy", "`ychy` moist volatile active; `dy`; `chcthy` volatile conduit bind; `ykyaiin` moist contained moist cycle complete; `kydy` contained moist fix active.", "Preserve moisture, containment, and fixation together so the active volatile never drops into a dead state.", "moist contained fixation weave", "strong"),
            ("P4", "ytychy.ksho.ykshy.shokshor.yty.darody.dy.otyds", "`ytychy` double-moist volatile active; `ykshy` moist contain transition active; `shokshor` transition heat contain transition outlet; `darody` root heat-fix active.", "Intensify the wet transition chain and return the preparation to doubly fixed root governance.", "double-moist transition intensifier", "strong"),
            ("P5", "okshy.daiin.okchor.chky.qotchy.daiin.cthor.oty", "`okshy` heated contained transition active; twin `daiin`; `qotchy` transmuted driven volatile; `cthor` conduit outlet.", "Checkpoint the transition twice before allowing the active volatile to move toward the outlet.", "double-checkpoint threshold", "strong"),
            ("P6", "qoty.choky.cthy.chokchy.dy.dy.dy.chckhy.dchyd.n", "`qoty` heated transmutation; `chokchy` volatile heat contain volatile active; `dy.dy.dy`; `chckhy` valve active; `dchyd` fix-volatile-active-fix.", "Drive the live medicine into the manuscript's first triple consecutive fixation and immediately lock it behind a valve check.", "triple-fixation climax", "strong"),
            ("P7", "oykshy.choky.dy.dy.odyd.otchy.o.kchy.dshy.dardy", "`oykshy` heated moist contained transition active; `dy.dy`; `odyd` heat-fix-active-fix; `dshy` fixed transition active; `dardy` root doubly fixed active.", "Continue fixing the wet preparation by inverting the heat sandwich and then re-rooting the active volatile body.", "inverted heat-sandwich continuation", "strong"),
            ("P8", "chokshor.daiin.okshydy.daiin.dol.dair.dam", "`chokshor` volatile heat contain transition outlet; `okshydy` heated contained transition fixed active; `dair` timed fixation; `dam` union.", "Only after timed fixation does the page finally allow the medicine to join its carrier.", "late carrier union", "strong"),
            ("P9", "dykchy.ctholdg.dchckhy", "`dykchy` fixed active body-volatile; `ctholdg` conduit heat-fluid fix; `dchckhy` fixed volatile valve active.", "Close by keeping the active volatile body under a final fixed valve rather than granting it a free exit.", "valve-governed medicinal close", "strong"),
        ],
        tarot_cards=["Strength", "Temperance", "Justice", "The Chariot", "The Hermit", "Judgment", "Death", "The Lovers", "The World"],
        movements=["wet-heat the medicine", "bind the moist transition", "weave moisture and fixation", "intensify the wet route", "checkpoint the threshold twice", "triple-fix behind the valve", "invert the heat sandwich", "unite with the carrier late", "seal the active product"],
        direct="`f14v` is a wet wound-medicine stabilization page. The route stays moist and active almost all the way through, and the manuscript answers that instability with relentless fixation rather than with simplification.",
        math="Across the formal lenses, `f14v` is a high-frequency stabilization problem with a nonzero activity floor. The state is never allowed to relax, so the control law must repeatedly project it back into admissible fixed subspaces, culminating in the triple-projection event `dy.dy.dy` and a valve-bound terminal state.",
        mythic="Across the mythic lenses, `f14v` is the healer's page of relentless care. The medicine survives because someone keeps tending it before it can collapse.",
        compression="Keep it wet, keep it moving, fix it again and again, allow union only near the end, and seal the active medicine under a valve.",
        typed_state_machine=r"""
\[\mathcal R_{f14v} = \{r_{\mathrm{wetactive}}, r_{\mathrm{transition}}, r_{\mathrm{triplefix}}, r_{\mathrm{valveseal}}\}\]
\[\delta(e_{\mathrm{dy.dy.dy}}): r_{\mathrm{transition}} \to r_{\mathrm{triplefix}}\]
\[\delta(e_{\mathrm{dchckhy}}): r_{\mathrm{triplefix}} \to r_{\mathrm{valveseal}}\]
""",
        invariants=r"""
\[N_{\mathrm{dy}}(f14v)=14, \qquad N_{y}(f14v)\ge 10, \qquad N_{\mathrm{shy}}(f14v)\ge 6\]
\[N_{\mathrm{dy.dy.dy}}(f14v)=1, \qquad N_{\mathrm{dam}}(f14v)=1, \qquad N_{\mathrm{dchckhy}}(f14v)=1\]
""",
        theorem=r"""
\[\rho_* = (\Psi_{P2} \circ \Psi_{P1})(\rho_0)\]

The formal theorem of `f14v` is:

1. the page keeps a moist active preparation in continuous transition rather than quiescent storage
2. fixation is applied at higher density here than on any earlier folio in the corpus
3. the carrier union is intentionally delayed until the route has survived maximum stabilization pressure
4. the true close is not passive completion but a fixed volatile product under valve law
""",
        crystal_contribution=[
            "maximum-fixation moist-medicine station",
            "triple-consecutive fixation line",
            "wet transition corridor",
            "late carrier-union threshold",
            "valve-sealed medicinal close",
        ],
        pointer_title="Maximum-Fixation Moist Medicine",
        pointer_position="the verso of the third Quire B bifolio and wet-medicine counterpart to the dry root repetitions on `f14r`",
        pointer_page_type="single-herb high-fixation medicinal page with triple-fixation climax and late union",
        pointer_conclusion="`-dy` x14, `dy.dy.dy`, `odyd`, late `dam`, and `dchckhy`",
        pointer_judgment="`f14v` keeps a live wet medicine from falling apart by force of fixation alone. The page culminates in a triple lock and then seals the still-active product under valve control.",
    ),
    make_folio(
        folio_id="F015R",
        quire="B",
        bifolio="bB2 = f10 + f15",
        manuscript_role="salt-intensive latex crystallization page with vessel-sealed storage close",
        purpose="`f15r` is Quire B's salt page. The leaf runs a long 14-line route, keeps `cth-` binding active, and concentrates the manuscript's strongest salt cluster on a latex-bearing plant. The page does not merely precipitate salt once: it names `sol`, `sal`, `saiin`, `saiiin`, and `sky`, then closes near `dom`, a fix-heat-vessel terminal that turns the refined salt body into stored medicine.",
        zero_claim="Extract the milky latex through bound conduit work, refine its salt fraction through repeated cycles until both fluid and structured salts appear, embody the active salt, and finally seal the product in its vessel.",
        botanical="`Sonchus oleraceus` is a moderate local-corpus fit; latex and salt-residue chemistry align well with the page",
        risk="moderate",
        confidence="high on salt-intensive latex refinement",
        visual_grammar=[
            "`standard Herbal A` = ordinary outward form masking an unusually long technical page",
            "`two leaf shapes` = local corpus associates the drawing with latex-bearing milky sap vegetation",
            "`14 lines` = one of the longest pages in the second half of Quire B, matching multi-stage refinement",
            "`bB2 pairing with f10` = earlier retort discipline on the bifolio answered later by salt discipline",
        ],
        full_eva="""
P1: tshor.shey.tchaly.shy.chtols.shey.daiin-
P2: otchor.qokchor.oly.okor.shy.koly-
P3: qokaiin.qotchytydy.daiin.chol.cthy-
P4: scheaiin.chodaiin.chl.sol.ckhaiin.sal-
P5: qotchy.r.shor.cthy.daiin.cthy.dy-
P6: ochy.kokaiin.chdy.saiin.okear-
P7: daiin.shkaiin.cthy.sho.keocthy-
P8: chocthy.tol.kaiin.s.dain.ctholy-
P9: octhain.qokaiin.chos.odaiin.cthl.s.y-
P10: ychain.ch**y.okesy.saiiin.dol.chds-
P11A: qotor.shor.tcheor.chy.cthaiin.shan-
P12: ykshol.dor.sheey.*y.dain.sky.shor.shoty-
P13: otcho.kchy.chol.daiin.*ar.ytol.dor.dom-
P14: qotchor.chaiin.chy.kol.daky=
""",
        core_vml=[
            "`scheaiin`, `sol`, `sal`, `saiin`, `saiiin`, `sky` = the densest salt family in Quire B",
            "`sol + sal` on one line = fluid-salt and structured-salt produced from the same phase",
            "`sky` = embodied active salt rather than inert precipitate",
            "`dom` = fix-heat-vessel terminal before final closure",
            "`cth-` remains elevated = salt work still depends on binding discipline, not only precipitation",
            "`14-line length` = salt refinement stretched across a long controlled corridor",
        ],
        groups=[
            {"label": "P1", "title": "Paragraph 1 - latex intake and first salt products", "line_ids": ["P1", "P2", "P3", "P4", "P5", "P6", "P7"]},
            {"label": "P2", "title": "Paragraph 2 - salt intensification, embodiment, and vessel seal", "line_ids": ["P8", "P9", "P10", "P11A", "P12", "P13", "P14"]},
        ],
        lines=[
            ("P1", "tshor.shey.tchaly.shy.chtols.shey.daiin", "`tshor` driven transition outlet; `tchaly` driven volatile structure active; `chtols` volatile driven heat-fluid dissolve; `daiin` checkpoint.", "Open by driving the latex-bearing volatile into structured transition and immediately verifying the route.", "latex-route opener", "strong"),
            ("P2", "otchor.qokchor.oly.okor.shy.koly", "`otchor` timed volatile outlet; `qokchor` extract contained outlet; `okor` heated contained outlet; `koly` body-fluid active.", "Draw off the timed latex route and keep its body-fluid fraction active under containment.", "timed contained outlet", "strong"),
            ("P3", "qokaiin.qotchytydy.daiin.chol.cthy", "`qokaiin` extract-contain complete; `qotchytydy` transmuted driven volatile active fixed active; `cthy` conduit bind.", "Complete the first extract and bind it into conduit discipline before the true salt work begins.", "pre-salt bind", "strong"),
            ("P4", "scheaiin.chodaiin.chl.sol.ckhaiin.sal", "`scheaiin` salt-volatile-essence cycle complete; `chodaiin` volatile heat-fix complete; `sol` fluid salt; `sal` structured salt.", "Produce both the fluid and solid salt fractions from one completed volatile-essence cycle.", "dual salt products line", "strong"),
            ("P5", "qotchy.r.shor.cthy.daiin.cthy.dy", "`qotchy` transmuted driven volatile; `r` root/outlet; twin `cthy`; `dy` fixed.", "Turn the salt-bearing volatile back through the conduit and certify it as fixed.", "salt-bound conduit return", "strong"),
            ("P6", "ochy.kokaiin.chdy.saiin.okear", "`ochy` heated volatile active; `kokaiin` body-heat-contain complete; `saiin` salt cycle complete; `okear` heated contained essence root.", "Complete one explicit salt cycle and ground the active salt-essence back at the root.", "first explicit salt cycle", "strong"),
            ("P7", "daiin.shkaiin.cthy.sho.keocthy", "`daiin` checkpoint; `shkaiin` transition contain complete; `keocthy` contained essence heat conduit bind.", "Checkpoint the route again and keep the essence contained inside the heated conduit.", "essence containment checkpoint", "strong"),
            ("P8", "chocthy.tol.kaiin.s.dain.ctholy", "`chocthy` volatile heat conduit bind; `tol` driven heat fluid; `kaiin` body complete; `dain`; `ctholy` conduit heat-fluid active.", "Restart the second phase by binding the volatile fluid to the conduit and proving the body is ready for further refinement.", "second-phase conduit restart", "strong"),
            ("P9", "octhain.qokaiin.chos.odaiin.cthl.s.y", "`octhain` heated conduit cycle complete; `qokaiin` extract contain complete; `chos` volatile heat dissolve; `odaiin` heat-fix complete; `cthl` conduit lock.", "Complete another extraction cycle and lock the salt-bearing volatile after dissolve and heat-fix steps.", "locked extraction refinement", "strong"),
            ("P10", "ychain.ch**y.okesy.saiiin.dol.chds", "`ychain` moist volatile cycle; damaged `ch**y`; `okesy` heated contained essence dissolve active; `saiiin` triple-cycle salt; `dol` fixed fluid.", "Push the salt fraction through its most intense refinement cycle and preserve the damaged volatile token while fixing the fluid body.", "triple-cycle salt intensification", "mixed"),
            ("P11A", "qotor.shor.tcheor.chy.cthaiin.shan", "`qotor` transmute heat-driven outlet; `tcheor` driven volatile essence outlet; `cthaiin` conduit cycle complete.", "Use one retort-class turn to redrive the salt-bearing essence through a completed conduit cycle.", "retort correction inside salt work", "strong"),
            ("P12", "ykshol.dor.sheey.*y.dain.sky.shor.shoty", "`ykshol` moist contained transition fluid; `dor` fix outlet; `sheey` transition double-essence active; damaged `*y`; `sky` active embodied salt.", "Embodied salt appears here as an active body, not as dead residue, and the route stays in transition after the checkpoint.", "embodied active salt line", "strong"),
            ("P13", "otcho.kchy.chol.daiin.*ar.ytol.dor.dom", "`otcho` timed volatile heat; `kchy` body-volatile active; `daiin`; damaged `*ar`; `ytol` moist driven fluid; `dor`; `dom` fix-heat-vessel.", "Checkpoint the body-volatile fraction one last time and seal the refined medicine inside its vessel.", "vessel-seal penultimate close", "strong"),
            ("P14", "qotchor.chaiin.chy.kol.daky", "`qotchor` transmuted driven volatile outlet; `chaiin` volatile cycle complete; `kol` body-fluid; `daky` fixed earth-contained active.", "Finish by certifying the salt-refined volatile as an embodied active body-fluid preparation.", "active salt terminal", "strong"),
        ],
        tarot_cards=["The Magician", "Justice", "Temperance", "The Hierophant", "Strength", "The Emperor", "The Hermit", "The Chariot", "Wheel of Fortune", "The Star", "Judgment", "The Sun", "The World", "The Empress"],
        movements=["draw the latex route", "hold the body-fluid active", "bind before salt work", "split fluid and solid salts", "return through conduit", "complete the first salt cycle", "checkpoint the essence", "restart the conduit", "lock the refinement", "triple-cycle the salt", "retort-correct the essence", "embody the salt", "seal in vessel", "close as active body"],
        direct="`f15r` is a latex-to-salt page. The manuscript keeps converting a milky active body into multiple salt forms, then refuses to treat the result as inert by embodying it in `sky` and storing it under `dom`.",
        math="Across the formal lenses, `f15r` is a long salt-refinement cascade with branching product states. The system repeatedly alternates extraction, binding, and crystallization until the salt appears both as fluid and structured form, then reintegrates that salt as active embodied matter.",
        mythic="Across the mythic lenses, `f15r` is the milk-into-crystal page. What begins as living sap is taught to survive as mineral body without ceasing to act.",
        compression="Extract the latex, crystallize its salt repeatedly, produce both fluid and structured salt, embody the active fraction, and seal it in the vessel.",
        typed_state_machine=r"""
\[\mathcal R_{f15r} = \{r_{\mathrm{latex}}, r_{\mathrm{saltsplit}}, r_{\mathrm{triplecycle}}, r_{\mathrm{vesselseal}}\}\]
\[\delta(e_{\mathrm{sol/sal}}): r_{\mathrm{latex}} \to r_{\mathrm{saltsplit}}\]
\[\delta(e_{\mathrm{dom}}): r_{\mathrm{triplecycle}} \to r_{\mathrm{vesselseal}}\]
""",
        invariants=r"""
\[N_{\mathrm{salt}}(f15r)\ge 7, \qquad N_{\mathrm{cth}}(f15r)\ge 7, \qquad N_{\mathrm{qotor}}(f15r)=1\]
\[N_{\mathrm{saiiin}}(f15r)=1, \qquad N_{\mathrm{sky}}(f15r)=1, \qquad N_{\mathrm{dom}}(f15r)=1\]
""",
        theorem=r"""
\[\rho_* = (\Psi_{P2} \circ \Psi_{P1})(\rho_0)\]

The formal theorem of `f15r` is:

1. the page converts a latex route into an explicitly salt-dominant route
2. one line can produce more than one salt state from the same operation
3. the late page insists that active salt must be embodied, not merely precipitated
4. the stable close requires vessel logic as much as extraction logic
""",
        crystal_contribution=[
            "salt-intensive latex station",
            "dual salt-product line",
            "triple-cycle salt intensifier",
            "embodied active salt route",
            "vessel-sealed terminal",
        ],
        pointer_title="Salt-Intensive Latex Crystallization",
        pointer_position="the recto of the second Quire B bifolio opposite the earlier short retort corridor",
        pointer_page_type="long single-herb salt refinement page with latex chemistry and vessel close",
        pointer_conclusion="`sol + sal`, `saiiin`, `sky`, and `dom`",
        pointer_judgment="`f15r` turns milky plant matter into active salt body. The page is not just about precipitation; it is about converting residue into stored medicine.",
    ),
    make_folio(
        folio_id="F015V",
        quire="B",
        bifolio="bB2 = f10 + f15",
        manuscript_role="repetitive volatile-source heating page for controlled toxic processing",
        purpose="`f15v` is Quire B's repetition page. Instead of escalating to long compounds, it hammers the same class again and again: `chor`, `otchor`, `ytchor`, `chol.chol`. Short lines, doubled and tripled outlet forms, and a late `eoy` concentration marker make the page feel like cautious toxic processing by exhaustive repetition rather than by one decisive transformation.",
        zero_claim="Drive the toxic volatile through repeated source-heating and outlet cycles, wash it again when needed, activate the surviving essence only after enough repetition, and close on the same `chor` class that governed the page from the start.",
        botanical="`Paris quadrifolia` is plausible in the local corpus; toxic handling profile aligns with the page",
        risk="moderate",
        confidence="high on repetitive volatile-source heating, moderate on exact plant ID",
        visual_grammar=[
            "`pinwheel structure` = local corpus ties the image to a radial toxic herb with balanced outward form",
            "`short repeated lines` = the page's shape already performs the repetition it prescribes",
            "`bB2 pairing with f10r` = earlier repeated retort on the bifolio answered here by repeated volatile-source heating",
            "`12-line moderate page` = enough length to feel methodical without becoming chemically expansive",
        ],
        full_eva="""
P1: poror.orshy.choiin.dtchan.opchordy-
P2: *chor.or.oro.r.aiin.cthy.*ain.dar-
P3: cthor.daiin.qokor.okeor.okaiin-
P4: doiin.choky.shol.qoky.qotchod-
P5: otchor.chor.chor.ytchor.cthy.s-
P6: qotchey.choty.kaiin.otchy.r.aiin-
P7: eoy.choiin.sho.*.chy.s.chy.tor.olr-
P8: ytchor.chor.ol.oiin.oty.shol.daiin-
P9: otchol.octhol.chol.chol.chody.kan-
P10: sor.chor.cthoiin.cthy.qokaiin-
P11: soloiin.cheor.chol.daiin.cthy-
P12: daiin.cthor.chol.chor=
""",
        core_vml=[
            "`chor`-class x9 = highest volatile-source heating concentration in the translated corpus",
            "`chor.chor.ytchor` = triple pass through the same outlet logic",
            "`chol.chol` = doubled volatile-fluid wash",
            "`eoy` = brief essence-activation marker after long repetition",
            "`short lines` = repetition as method rather than as rhetorical flourish",
            "`final chor` = page ends on the same operator family that governs it",
        ],
        groups=[
            {"label": "P1", "title": "Paragraph 1 - repeated outlet-heating corridor", "line_ids": ["P1", "P2", "P3", "P4", "P5", "P6"]},
            {"label": "P2", "title": "Paragraph 2 - essence activation, doubled washing, and terminal chor", "line_ids": ["P7", "P8", "P9", "P10", "P11", "P12"]},
        ],
        lines=[
            ("P1", "poror.orshy.choiin.dtchan.opchordy", "`poror` press-heat-outlet-heat-outlet; `orshy` outlet transition active; `choiin` volatile heat cycle; `opchordy` pressed volatile outlet fixed active.", "Open by heating the outlet twice and setting the repetitive volatile route under fixed active pressure.", "double-outlet heated opener", "strong"),
            ("P2", "*chor.or.oro.r.aiin.cthy.*ain.dar", "damaged `*chor`; `or.oro` outlet and double-heat outlet; `cthy`; damaged `*ain`; `dar` root fix.", "Keep the damaged outlet evidence visible while re-running the same heat-at-source logic and returning it to the root.", "damaged repeated outlet turn", "mixed"),
            ("P3", "cthor.daiin.qokor.okeor.okaiin", "`cthor` conduit outlet; `daiin`; `qokor` extract contained heated outlet; `okeor` heated contained essence outlet.", "Checkpoint the route and then keep heating the source through contained outlet and essence outlet forms.", "contained outlet checkpoint", "strong"),
            ("P4", "doiin.choky.shol.qoky.qotchod", "`doiin` fix-heat cycle; `choky` volatile heat contain active; `shol` transition fluid; `qotchod` transmuted driven volatile heat-fix.", "Repeat the same volatile control cycle until heat, containment, and fixation feel like one operator family.", "repeated fix-heat cycle", "strong"),
            ("P5", "otchor.chor.chor.ytchor.cthy.s", "`otchor` timed volatile outlet; `chor.chor.ytchor` triple outlet pass; `cthy`; `s` dissolve.", "Run the page's decisive repetition line by driving the outlet through the same source-heating class three times in sequence.", "triple outlet pass", "strong"),
            ("P6", "qotchey.choty.kaiin.otchy.r.aiin", "`qotchey` transmuted driven volatile essence active; `choty` volatile heat driven active; `kaiin` body complete; `otchy`; `aiin` complete.", "Keep the volatile active and driven, but only inside a cycle that can still complete and return.", "active cycle completion", "strong"),
            ("P7", "eoy.choiin.sho.*.chy.s.chy.tor.olr", "`eoy` essence-heat-active; `choiin` volatile heat cycle; damaged `*`; `tor` driven heat outlet; `olr` fluid outlet.", "Only after all the repetition does the page briefly activate the surviving essence and move it toward outlet fluid.", "essence activation after exhaustion", "mixed"),
            ("P8", "ytchor.chor.ol.oiin.oty.shol.daiin", "`ytchor` moist driven outlet; `chor` outlet; `ol` fluid; `oiin` heat cycle; `daiin` checkpoint.", "Repeat the outlet one more time, but now moisten it and checkpoint the fluid form that remains.", "moistened outlet checkpoint", "strong"),
            ("P9", "otchol.octhol.chol.chol.chody.kan", "`otchol` timed volatile fluid; `octhol` heated conduit fluid; `chol.chol` doubled volatile fluid; `chody` volatile heat-fix active.", "Wash the surviving fluid twice before fixing the volatile body again.", "doubled fluid wash", "strong"),
            ("P10", "sor.chor.cthoiin.cthy.qokaiin", "`sor` salt outlet; `chor` outlet; `cthoiin` conduit heat cycle; `qokaiin` extract contain complete.", "Introduce a salt outlet without changing the page's core law: source-heating still dominates the route.", "salted outlet continuation", "strong"),
            ("P11", "soloiin.cheor.chol.daiin.cthy", "`soloiin` salt-fluid heat cycle; `cheor` volatile essence outlet; `daiin`; `cthy` conduit bind.", "Cycle the salt-fluid and essence outlet together under one more checkpoint and conduit bind.", "salt-fluid essence checkpoint", "strong"),
            ("P12", "daiin.cthor.chol.chor", "`daiin` final checkpoint; `cthor` conduit outlet; `chol` volatile fluid; `chor` volatile outlet.", "End on the same volatile-source outlet family that ruled the page from the first line.", "terminal chor close", "strong"),
        ],
        tarot_cards=["The Devil", "Strength", "Justice", "Temperance", "Wheel of Fortune", "The Hermit", "Death", "The Moon", "The Star", "The Emperor", "The Hierophant", "The World"],
        movements=["heat the outlet twice", "repeat despite damage", "checkpoint the contained outlet", "cycle heat and fix again", "triple-pass the source", "complete the active cycle", "activate the surviving essence", "moisten the outlet", "wash the fluid twice", "salt the route lightly", "checkpoint the salt-fluid essence", "end on chor"],
        direct="`f15v` is a cautious toxic-processing page. The manuscript does not solve the problem by inventing a new operation; it solves it by repeating the same volatile-source handling until the dangerous fraction is exhausted and only a controllable essence remains.",
        math="Across the formal lenses, `f15v` is a recurrence-dominated detoxification corridor. The main operator family is repeatedly reapplied with limited state-space expansion, so the page behaves like iterative attenuation followed by a small late essence activation and a final return to the governing outlet basis.",
        mythic="Across the mythic lenses, `f15v` is the page of careful repetition against poison. The victory is not brilliance but the willingness to do the same right thing enough times.",
        compression="Repeat the source-heating cycle until the toxic volatile is spent, wash what remains, briefly activate the essence, and close on the same disciplined outlet law.",
        typed_state_machine=r"""
\[\mathcal R_{f15v} = \{r_{\mathrm{repeat}}, r_{\mathrm{triplepass}}, r_{\mathrm{essence}}, r_{\mathrm{terminalchor}}\}\]
\[\delta(e_{\mathrm{chor}}): r_{\mathrm{repeat}} \to r_{\mathrm{repeat}}\]
\[\delta(e_{\mathrm{eoy}}): r_{\mathrm{triplepass}} \to r_{\mathrm{essence}} \to r_{\mathrm{terminalchor}}\]
""",
        invariants=r"""
\[N_{\mathrm{chor}}(f15v)\ge 9, \qquad N_{\mathrm{cth}}(f15v)\ge 5, \qquad N_{\mathrm{shortlines}}(f15v)\ge 6\]
\[N_{\mathrm{eoy}}(f15v)=1, \qquad N_{\mathrm{chol.chol}}(f15v)=1, \qquad N_{\mathrm{daiin}}(f15v)\ge 4\]
""",
        theorem=r"""
\[\rho_* = (\Psi_{P2} \circ \Psi_{P1})(\rho_0)\]

The formal theorem of `f15v` is:

1. one outlet-heating family dominates the page more than any alternative operator class
2. the page treats repetition itself as the safety mechanism for toxic matter
3. essence activation arrives late and briefly, only after sustained attenuation
4. the correct close returns to the governing `chor` family instead of escaping it
""",
        crystal_contribution=[
            "repetitive volatile-source heating station",
            "triple-pass outlet line",
            "late essence-activation marker",
            "doubled fluid wash route",
            "terminal chor closure",
        ],
        pointer_title="Repetitive Volatile-Source Heating",
        pointer_position="the verso of the second Quire B bifolio and counterpart to the earlier repeated-retort discipline page",
        pointer_page_type="single-toxic-herb repetition page built from short lines and repeated outlet operators",
        pointer_conclusion="`chor` x9, `chor.chor.ytchor`, `eoy`, `chol.chol`, and final `chor`",
        pointer_judgment="`f15v` handles toxic matter by doing the same careful heating-and-outlet move over and over. The page's repetition is its medicine.",
    ),
]


def main() -> None:
    for folio in FOLIOS:
        (FOLIOS_DIR / f"{folio['folio_id']}_FINAL_DRAFT.md").write_text(render_folio(folio), encoding="utf-8")
        (FOLIOS_DIR / f"{folio['folio_id']}.md").write_text(render_pointer(folio), encoding="utf-8")


if __name__ == "__main__":
    main()
