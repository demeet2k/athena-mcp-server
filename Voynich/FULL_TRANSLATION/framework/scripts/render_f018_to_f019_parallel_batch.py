from __future__ import annotations

from render_f007_to_f008_parallel_batch import FOLIOS_DIR, render_folio, render_pointer
from render_f009_to_f010_parallel_batch import make_folio


FOLIOS: list[dict[str, object]] = [
    make_folio(
        folio_id="F018R",
        quire="C",
        bifolio="bC2 = f18 + f23",
        manuscript_role="structural scaffolding page with triple root-anchoring and explicit product label",
        purpose="`f18r` is the first true structural page after Quire C's open vessel opener. The folio divides cleanly into extractive first paragraph, structural second paragraph, and title-line naming. It carries six `-al` structure terminals, two vessel references, elevated valve control, and the unique `dar.dar.dal` chain where the root is fixed twice before the structure is locked. The page reads like a flower-head or alpine-root extract that must be turned into a stable scaffolded body before it can be named.",
        zero_claim="Extract the aster-class material into vessel and valve governance, then pin the root twice and lock the structure repeatedly until a moist volatile-essence body can be named as finished product.",
        botanical="`Aster alpinus` remains one of the stronger Sherwood-style IDs in Quire C, though the operational profile matters more than the species certainty",
        risk="moderate",
        confidence="high on structural scaffolding and triple root-anchoring",
        visual_grammar=[
            "`two leaf shapes` = A-exclusive drawing feature that fits the local corpus note for `f18r`",
            "`paired with f23v on bC2` = a mid-quire structural page on an inner-not-center bifolio",
            "`three-phase architecture` = extractive paragraph, structural paragraph, then title label",
            "`standalone om and later chom` = vessel reference appears both independently and as a suffix-bearing storage form",
        ],
        full_eva="""
P1: pdrairdy.darod*.yoar.ykchol.dor.om.chckhy.o*or.dyl-
P2: otshol.qokchol.chykchy.okchal.daiin.dy.chol.dain-
P3: qokchor.chor.chckhy.or.chey.qokchol.dy.ytcharg-
P4: chor.cthor.okeor.ykchol.okain=
P5: tchor.shor.cthaiin.cthol.chlol.chom-
P6: ychykchor.dair.ytol.chcthy.dar.dar.dal-
P7: oshor.shaiin.cthy.sholdy.doldy.dolaiin-
P8: qokchor.ckhol.olody.okal.dy.dary-
P9: chol.chcthal.okshal.chykald-
P10: sotchaiin.chokchy.chckhol.chor.g-
P11: ychair.cthol.daiin.qokchy.cthy-
P12: or.shaiin.cthor.cthal.okal.dar=
T14: ychekchy.kchaiin=
""",
        core_vml=[
            "`dar.dar.dal` = unique triple anchoring sequence: root, root, then structure",
            "`-al` terminals x6 = structural building dominates the page",
            "`om` in P1 = a rare standalone vessel reference rather than only a suffixal close",
            "`chckhy / ckhol / ckh-` = elevated valve-control grammar inside a structural build",
            "`T14` = product label after the structural paragraph rather than before it",
            "`g` terminals on P3 and P10 = rare preserved terminal marker",
        ],
        groups=[
            {"label": "P1", "title": "Paragraph 1 - extraction into vessel and outlet control", "line_ids": ["P1", "P2", "P3", "P4"]},
            {"label": "P2", "title": "Paragraph 2 - structural build and root anchoring", "line_ids": ["P5", "P6", "P7", "P8", "P9", "P10", "P11", "P12"]},
            {"label": "T", "title": "Title line - named structural product", "line_ids": ["T14"]},
        ],
        lines=[
            ("P1", "pdrairdy.darod*.yoar.ykchol.dor.om.chckhy.o*or.dyl", "`pdrairdy` pressed fix-root rotation fix active; damaged `darod*`; `yoar` moist heat-root; `ykchol` moist contained volatile fluid; standalone `om` vessel; `chckhy` valve-active volatile body.", "Open by pressing and re-fixing the root route while directly referencing the receiving vessel and placing the outlet under valve law.", "press-root extraction into standalone vessel", "mixed"),
            ("P2", "otshol.qokchol.chykchy.okchal.daiin.dy.chol.dain", "`otshol` timed transition fluid; `qokchol` extracted contained volatile fluid; `okchal` heated contained volatile structure; `daiin` and `dain` bracket fixation.", "The first paragraph already begins building structure: extract the fluid, contain it, and certify the structural volatile body with doubled completion logic.", "extractive structure checkpoint", "strong"),
            ("P3", "qokchor.chor.chckhy.or.chey.qokchol.dy.ytcharg", "`qokchor` extracted contained volatile outlet; `chckhy` valve-active; `chey` volatile essence active; `qokchol` extracted contained fluid; terminal `ytcharg` moist-driven volatile-root with rare `g` marker.", "Route the extracted volatile through valve and outlet control, then send it back toward rooted moist drive rather than leaving it as free essence.", "valved outlet returning to rooted drive", "strong"),
            ("P4", "chor.cthor.okeor.ykchol.okain", "`chor/cthor` volatile outlet and conduit outlet; `okeor` heated contained essence outlet; `ykchol` moist contained volatile fluid; `okain` heated contained completion.", "Seal the first paragraph as a contained outlet corridor whose product is already complete enough to survive transfer into the second phase.", "contained section seal", "strong"),
            ("P5", "tchor.shor.cthaiin.cthol.chlol.chom", "`tchor` driven volatile outlet; `shor` transition outlet; `cthaiin` conduit cycle complete; `cthol` conduit fluid; `chlol` volatile lock-fluid; `chom` volatile heat vessel.", "Start the structural paragraph by moving from outlet logic into locked conduit fluid and depositing the volatile into a vessel body.", "conduit-fluid into vessel", "strong"),
            ("P6", "ychykchor.dair.ytol.chcthy.dar.dar.dal", "`ychykchor` moist active contained volatile outlet; `dair` timed fixation; `ytol` moist driven fluid; `chcthy` volatile conduit bind; `dar.dar.dal` triple root-root-structure anchoring.", "This is the folio's theorem line: the root is fixed twice and only then is the structure locked, turning an unstable extract into anchored form.", "triple root-anchoring theorem", "strong"),
            ("P7", "oshor.shaiin.cthy.sholdy.doldy.dolaiin", "`oshor` heated transition outlet; `shaiin` transition complete; `cthy` conduit bind; `sholdy` transition-fluid-fix active; `doldy` fix-fluid-fix active; `dolaiin` fix-fluid cycle complete.", "After anchoring, the page repeatedly fixes the fluid body until the transition itself can be trusted as structural medium.", "fluid-fix stabilization corridor", "strong"),
            ("P8", "qokchor.ckhol.olody.okal.dy.dary", "`qokchor` extracted contained outlet; `ckhol` valve-fluid; `olody` fluid heat-fix active; `okal` heated contained structure; `dy`; `dary` fixed root active.", "Re-extract under valve-fluid control and push the product deeper into heated contained structure while keeping the root active.", "valve-fluid structural reinforcement", "strong"),
            ("P9", "chol.chcthal.okshal.chykald", "`chol` volatile fluid; `chcthal` volatile conduit structure; `okshal` heated contained transition structure; `chykald` volatile active contained structure-fix.", "This short line is almost pure scaffolding: every token pushes the volatile toward structured containment.", "pure structure cluster", "strong"),
            ("P10", "sotchaiin.chokchy.chckhol.chor.g", "`sotchaiin` salt-heat-driven volatile cycle complete; `chokchy` volatile heat-contained active; `chckhol` volatile valve-fluid; `chor`; terminal `g`.", "Add one salt-driven completion and keep the volatile under valve-fluid discipline even in the brief terminal-marked line.", "salted valve-fluid proof", "mixed"),
            ("P11", "ychair.cthol.daiin.qokchy.cthy", "`ychair` moist volatile earth-rotation; `cthol` conduit fluid; `daiin`; `qokchy` extracted contained active; `cthy` conduit bind.", "Checkpoint the nearly finished scaffold and confirm that the extract can still remain contained inside conduit fluid.", "late checkpoint in conduit fluid", "strong"),
            ("P12", "or.shaiin.cthor.cthal.okal.dar", "`or` outlet; `shaiin` transition complete; `cthor` conduit outlet; `cthal` conduit structure; `okal` heated contained structure; `dar` fixed root.", "Close the structural paragraph by landing outlet, conduit, structure, and root in one final anchored sequence.", "rooted structural close", "strong"),
            ("T14", "ychekchy.kchaiin", "`ychekchy` moist volatile essence contained body-active; `kchaiin` body-volatile cycle complete.", "Name the product as a moistened volatile-essence body that has achieved completion through containment and structure.", "product-label close", "strong"),
        ],
        tarot_cards=["The Magician", "Justice", "The Chariot", "Temperance", "The Emperor", "Strength", "The Hermit", "Wheel of Fortune", "The Hierophant", "The Moon", "Judgment", "The World", "The Empress"],
        movements=["press the root into vessel law", "extract with structural intent", "valve the outlet", "seal the first phase", "shift to conduit-fluid building", "anchor root twice then lock structure", "stabilize the fluid body", "reinforce under valve-fluid control", "cluster the scaffolding", "salt the proof line", "checkpoint the scaffold", "close on root and structure", "name the finished body"],
        direct="`f18r` is Quire C's first clear structural-build page. The folio extracts first, then spends most of its length turning the volatile product into anchored scaffolded form, climaxing in `dar.dar.dal` and ending with a named body-product title.",
        math="Across the formal lenses, `f18r` behaves like a stabilization-through-scaffolding system. The first phase extracts and contains; the second phase increases structural basis terms until the route is anchored at the root and locked as form rather than left as flowing essence.",
        mythic="Across the mythic lenses, `f18r` is the page that builds bones. What Quire C opened as vessel possibility is here taught how to stand up.",
        compression="Extract into vessel control, anchor the root twice, lock the structure repeatedly, and name the resulting moist volatile-essence body.",
        typed_state_machine=r"""
\[\mathcal R_{f18r} = \{r_{\mathrm{extract}}, r_{\mathrm{valvevessel}}, r_{\mathrm{anchor}}, r_{\mathrm{structure}}, r_{\mathrm{label}}\}\]
\[\delta(e_{\mathrm{dar.dar.dal}}): r_{\mathrm{valvevessel}} \to r_{\mathrm{anchor}} \to r_{\mathrm{structure}}\]
\[\delta(e_{\mathrm{T14}}): r_{\mathrm{structure}} \to r_{\mathrm{label}}\]
""",
        invariants=r"""
\[N_{\mathrm{-al}}(f18r)=6, \qquad N_{\mathrm{ckh}}(f18r)\ge 3, \qquad N_{\mathrm{om/chom}}(f18r)\ge 2\]
\[N_{\mathrm{dar.dar.dal}}(f18r)=1, \qquad N_{\mathrm{title}}(f18r)=1, \qquad N_{\mathrm{g\ terminal}}(f18r)=2\]
""",
        theorem=r"""
\[\rho_* = (\Psi_{T} \circ \Psi_{P2} \circ \Psi_{P1})(\rho_0)\]

The formal theorem of `f18r` is:

1. the first paragraph extracts and contains the material under vessel and valve law
2. the second paragraph converts that extract into scaffolded structure rather than further volatile escalation
3. `dar.dar.dal` is the decisive anchoring operator: root, root, then structure
4. the title certifies the result as a completed volatile-essence body rather than a free liquid fraction
""",
        crystal_contribution=[
            "structural scaffolding station",
            "triple root-anchoring line",
            "standalone vessel-reference threshold",
            "structural -al saturation corridor",
            "named body-product close",
        ],
        pointer_title="Structural Scaffolding with Triple Root-Anchoring",
        pointer_position="the recto of the second Quire C bifolio and structural counterpart to later co-distillation on `f18v`",
        pointer_page_type="single-herb extract-then-solidify page with a separate title label",
        pointer_conclusion="six `-al` structures, rare standalone `om`, `dar.dar.dal`, elevated valve control, and title `ychekchy.kchaiin`",
        pointer_judgment="`f18r` teaches that Quire C does not only fill vessels. It also knows how to build a volatile extract into anchored form and then name the product explicitly.",
    ),
    make_folio(
        folio_id="F018V",
        quire="C",
        bifolio="bC2 = f18 + f23",
        manuscript_role="continuous co-distillation page with double triple-essence concentration and damaged close",
        purpose="`f18v` takes the structural preparation of `f18r` and drives it into Quire C's first sustained retort storm. The folio is saturated with `qo-` forms, runs two different triple-essence lines (`qoeees` and `qokeees`), unites material inside the retort vessel through `qokam`, and preserves physical damage in the final line rather than pretending the close is fully recoverable. The page reads as continuous co-distillation rather than batchwise processing.",
        zero_claim="Continue already locked material through uninterrupted retort cycling, pass it through triple essence twice, combine ingredients inside the retort vessel, and close the surviving product in a vessel even though the terminal line is partially lost.",
        botanical="`Telfairia pedata` is a weak Sherwood carryover; a generic cucurbit-class cooling or oily plant remains a safer practical inference than the species label",
        risk="moderate",
        confidence="high on continuous retort cycling and double triple-essence, mixed on the damaged close",
        visual_grammar=[
            "`continuation opener told` = the page begins as though the material is already in play rather than freshly started",
            "`paired with f18r` = structural preparation on recto answered by retort concentration on verso",
            "`10-line density with 12 qo-` = continuous retort law dominates the folio more than illustration does",
            "`damaged P10` = closure must be preserved as a lacunose witness, not normalized into certainty",
        ],
        full_eva="""
P1: told.shor.ytshy.otchdal.dchal.dchy.ytchm-
P2: qoeees.or.oaiin.shy*.okshy.qokchy.qokchy.s.g-
P3: or*shy.qoky.qoky.chkchy.qokshy.qokam-
P4: qotchy.qokay.qokchy.ykcho.ydl.dan-
P5: ychoees.ykchy.qol.kchy.qotchol.dair.om-
P6: qotor.chor.otchy.qokeees.chy.s.ar.ykar-
P7: ychol.dor.chod.qokol.daiin.qotol.dar.dy-
P8: tolol.sh.cphoy.daror.ddy.ytor.ykam-
P9: okchor.qotchy.qokchy.ytol.doky.dy-
P10: !!!!!!!yko!!!!!!!!!!.dysh!!!!!!!.dair.ykol.dom=
""",
        core_vml=[
            "`qo-` x12 in 10 lines = continuous retort cycling, not discrete batch work",
            "`qoeees` plus `qokeees` = double-pass triple-essence concentration",
            "`qokam` = union inside the retort vessel, i.e. co-distillation",
            "`told` opener = continuation law; the material is already locked before this page starts",
            "`ddy` = doubled fixation inside the retort storm",
            "`P10` damage must remain visible; only `...dair.ykol.dom` clearly survives the close",
        ],
        groups=[
            {"label": "P1", "title": "Paragraph 1 - continuous retort opening and first triple-essence pass", "line_ids": ["P1", "P2", "P3", "P4", "P5"]},
            {"label": "P2", "title": "Paragraph 2 - second triple-essence pass, doubled fixation, and damaged vessel close", "line_ids": ["P6", "P7", "P8", "P9", "P10"]},
        ],
        lines=[
            ("P1", "told.shor.ytshy.otchdal.dchal.dchy.ytchm", "`told` driven heat-fluid-fix continuation opener; `shor/ytshy` transition outlet and moist driven transition; `otchdal/dchal` timed volatile structure and fixed volatile structure; `ytchm` moist driven volatile vessel.", "Open as a continuation procedure: the material is already locked, already heated, and immediately pushed toward vessel-borne structural processing.", "continuation opener into vesselized structure", "strong"),
            ("P2", "qoeees.or.oaiin.shy*.okshy.qokchy.qokchy.s.g", "`qoeees` retort triple essence dissolve; `oaiin` heat-cycle complete; damaged `shy*`; doubled `qokchy`; `s`; terminal `g`.", "The first great concentration line reaches triple essence and immediately follows it with doubled retort extraction rather than repose.", "first triple-essence pass with doubled extraction", "strong"),
            ("P3", "or*shy.qoky.qoky.chkchy.qokshy.qokam", "damaged `or*shy`; doubled `qoky`; `chkchy` volatile body-active; `qokshy` extracted contained transition; `qokam` extracted contained union vessel.", "The folio then performs co-distillation proper: extraction and union happen inside the retort vessel rather than before or after it.", "co-distillation union inside vessel", "strong"),
            ("P4", "qotchy.qokay.qokchy.ykcho.ydl.dan", "`qotchy` transmuted driven volatile; `qokay` extracted contained earth-active; `qokchy` extracted contained body-active; `ykcho` moist contained volatile heat; `ydl` moist fixed lock; `dan` fix-cycle.", "Stabilize the co-distilled route by locking its moist volatile body before the second half intensifies again.", "retort stabilization before reintensification", "strong"),
            ("P5", "ychoees.ykchy.qol.kchy.qotchol.dair.om", "`ychoees` moist volatile double-essence dissolve; `ykchy` moist contained body-active; `qol` transmuted fluid; `kchy` body-volatile active; `qotchol` transmuted driven volatile fluid; `dair`; standalone `om` vessel.", "Deposit the double-essence moist route back into vessel logic so the page can survive its next concentration leap.", "double-essence vessel deposit", "strong"),
            ("P6", "qotor.chor.otchy.qokeees.chy.s.ar.ykar", "`qotor` transmute heated outlet; `chor`; `otchy`; `qokeees` extracted contained triple essence dissolve; `ar` root; `ykar` moist contained root.", "The second triple-essence pass arrives here, but unlike P2 it is explicitly contained and rerooted inside the retort corridor.", "second contained triple-essence pass", "strong"),
            ("P7", "ychol.dor.chod.qokol.daiin.qotol.dar.dy", "`ychol` moist volatile fluid; `dor` fixed outlet; `chod` volatile heat-fix; `qokol` extracted contained fluid; `daiin`; `qotol` transmuted heat-fluid; `dar`; `dy`.", "After the second concentration spike, the page checks itself and returns to fixed fluid and root discipline.", "post-spike checkpoint and rerooting", "strong"),
            ("P8", "tolol.sh.cphoy.daror.ddy.ytor.ykam", "`tolol` double heated fluid; `sh` transition; `cphoy` alembic heat-active; `daror` fixed root outlet; `ddy` double fix active; `ytor` moist driven outlet; `ykam` moist contained union vessel.", "This is the retort storm's consolidation line: double fluid, alembic, double fixation, and union in vessel all appear at once.", "double-fix vessel consolidation", "strong"),
            ("P9", "okchor.qotchy.qokchy.ytol.doky.dy", "`okchor` heated contained volatile outlet; `qotchy` and `qokchy` transmuted and extracted volatile; `ytol` moist driven fluid; `doky` fixed heat-contained active; `dy`.", "Keep the volatile product contained and moist while one last fixed active closure is established before the damaged line.", "contained moist preterminal fix", "strong"),
            ("P10", "!!!!!!!yko!!!!!!!!!!.dysh!!!!!!!.dair.ykol.dom", "damaged opening zone with surviving `yko`; surviving `dysh`; `dair`; `ykol`; `dom` fix-heat vessel.", "The exact closure is partly lost, but what survives still shows a familiar pattern: fixation, moist contained fluid, and vessel sealing.", "damaged vessel-seal close", "mixed"),
        ],
        tarot_cards=["The Chariot", "Strength", "The Lovers", "Justice", "Temperance", "Judgment", "The Hermit", "The Tower", "The Emperor", "The World"],
        movements=["continue the locked route", "run the first triple-essence pass", "unite inside the retort", "stabilize the co-distillate", "deposit the double essence in vessel", "run the second triple-essence pass", "checkpoint and reroot", "double-fix the vessel union", "hold the moist contained product", "seal what survives of the close"],
        direct="`f18v` is Quire C's first continuous co-distillation page. It keeps the retort running, processes triple essence twice, unites material inside the vessel, and still closes under vessel fixation even though the final line is physically damaged.",
        math="Across the formal lenses, `f18v` behaves like a continuously driven concentration loop with embedded union. The route does not reset between operations; instead it compounds, concentrates, and recontains in one uninterrupted retort field.",
        mythic="Across the mythic lenses, `f18v` is the storm chamber. The matter is not merely refined; it is kept inside the turning furnace until it agrees to become one thing.",
        compression="Continue the locked material through uninterrupted retort cycling, pass triple essence twice, unite it inside the vessel, and seal the surviving close under `dom`.",
        typed_state_machine=r"""
\[\mathcal R_{f18v} = \{r_{\mathrm{continuation}}, r_{\mathrm{triple1}}, r_{\mathrm{codistill}}, r_{\mathrm{triple2}}, r_{\mathrm{damagedclose}}\}\]
\[\delta(e_{\mathrm{qoeees}}): r_{\mathrm{continuation}} \to r_{\mathrm{triple1}}\]
\[\delta(e_{\mathrm{qokam}}): r_{\mathrm{triple1}} \to r_{\mathrm{codistill}}\]
\[\delta(e_{\mathrm{qokeees}}): r_{\mathrm{codistill}} \to r_{\mathrm{triple2}} \to r_{\mathrm{damagedclose}}\]
""",
        invariants=r"""
\[N_{\mathrm{qo}}(f18v)=12, \qquad N_{\mathrm{qoeees}}(f18v)=1, \qquad N_{\mathrm{qokeees}}(f18v)=1\]
\[N_{\mathrm{qokam}}(f18v)=1, \qquad N_{\mathrm{ykam}}(f18v)=1, \qquad N_{\mathrm{ddy}}(f18v)=1, \qquad N_{\mathrm{damage}}(f18v)=1\]
""",
        theorem=r"""
\[\rho_* = (\Psi_{P2} \circ \Psi_{P1})(\rho_0)\]

The formal theorem of `f18v` is:

1. the folio assumes pre-locked material and therefore behaves as a continuation rather than a fresh intake
2. triple essence is processed twice, with the second pass explicitly contained
3. `qokam` proves that union occurs inside the retort vessel itself
4. the closing state is genuinely lacunose, but the surviving witness still certifies vessel fixation under `dom`
""",
        crystal_contribution=[
            "continuous co-distillation station",
            "double triple-essence concentration line",
            "retort-internal union-vessel gate",
            "double-fix consolidation corridor",
            "damaged vessel-seal close",
        ],
        pointer_title="Continuous Co-Distillation with Double Triple-Essence",
        pointer_position="the verso of the second Quire C bifolio and retort answer to the scaffolding page on `f18r`",
        pointer_page_type="single-herb continuation page with extreme qo-density and a damaged terminal line",
        pointer_conclusion="`qoeees`, `qokeees`, `qokam`, `ddy`, and damaged `...dair.ykol.dom`",
        pointer_judgment="`f18v` keeps the retort running continuously and concentrates the essence twice over. Even the damaged close still shows that the product ends sealed in a vessel.",
    ),
    make_folio(
        folio_id="F019R",
        quire="C",
        bifolio="bC3 = f19 + f22",
        manuscript_role="hyper-verified sedative tincture page with deep-root retort and completion-fluid close",
        purpose="`f19r` is the most checkpoint-saturated page in Quire C so far. The folio compresses 11 completion markers into 13 lines, contracts to short mid-page verification bursts, reaches a deep-source retort in `qokorar`, and culminates in `daiinol`, where completion fuses with the fluid suffix. The page reads like a valerian-class sedative tincture that cannot be trusted unless every phase is checked and rechecked.",
        zero_claim="Drive the sedative root through repeated retort and fixation passes, verify almost every line, complete the decisive transition itself, and finish with a product that is complete as fluid rather than as a hardened body.",
        botanical="`Polemonium caeruleum` / Greek valerian remains a plausible sedative-root fit in the local corpus, with stronger process fit than visual certainty",
        risk="moderate",
        confidence="high on hyper-verification and fluid completion",
        visual_grammar=[
            "`two-plus leaf clusters` = local corpus aligns the drawing with a sedative-root candidate but the textual pattern is more decisive",
            "`paired with f22v on bC3` = inner-quire tincture discipline before the next answer leaf",
            "`13 short-to-medium lines` = repeated checkpointing rather than long free-flowing corridor logic",
            "`no title line` = the product is certified through repeated completions rather than by external label",
        ],
        full_eva="""
P1: pchor.qodchy.qotshy.dy.tchy.qotchy.qoky.daiin.dchydy-
P2: dshy.chor.y.tchy.chol.dytchy.chordy.daiin.dy.ty.*.ch*-
P3: oscheos.shy.tdaiin.chol.dor.yky-
P4: qokorar.daiin.chckhy.shy.kchor-
P5: otchy.tchy.qoky.daiin.r-
P6: yshor.shy.daiin.otytchy.daiin-
P7: q*t.cho.ty.cthar.dor.chan.dar-
P8: or.chor.daky.dal.chor.dor.l.shy-
P9: qotchor.dy.dor.y.tchykchy.shdaiin-
P10: daiin.cthor.chol.ykchor.chordy-
P11: qotchy.qolody.choldy.cthod-
P12: ykchor.chor.daiin.daiinol-
P13: or.octhor.y.tchor=
""",
        core_vml=[
            "`daiin/dain/tdaiin/shdaiin` x11 = highest completion density in Quire C",
            "`qokorar` = deep-source retort that reaches down to the root",
            "`shdaiin` = completion through transition rather than after transition",
            "`daiinol` = completion fused with fluid; the product finishes as liquid",
            "`P5` and `P6` short lines = rapid-fire verification bursts",
            "`dchydy` = double fixation around volatile activity at the opener",
        ],
        groups=[
            {"label": "P1", "title": "Paragraph 1 - opening verification corridor", "line_ids": ["P1", "P2", "P3", "P4"]},
            {"label": "P2", "title": "Paragraph 2 - short-line verification bursts and transition-completion", "line_ids": ["P5", "P6", "P7", "P8", "P9"]},
            {"label": "P3", "title": "Paragraph 3 - final fluid completion and seal", "line_ids": ["P10", "P11", "P12", "P13"]},
        ],
        lines=[
            ("P1", "pchor.qodchy.qotshy.dy.tchy.qotchy.qoky.daiin.dchydy", "`pchor` press-volatile-outlet; `qodchy` transmute-fix-active; `qotshy` transmute-heat-transition; `daiin`; `dchydy` double fixation around volatile activity.", "Open by mixing press, transmutation, and fixation immediately, then certify the result with the first checkpoint and doubled volatile fixation.", "opening checkpoint with doubled fixation", "strong"),
            ("P2", "dshy.chor.y.tchy.chol.dytchy.chordy.daiin.dy.ty.*.ch*", "`dshy` fixed transition active; `chor/chol` outlet and fluid; `dytchy` fixed driven volatile active; `chordy` fixed outlet; `daiin`; damaged tail preserved.", "Continue the same discipline: outlet and fluid are both kept active, but every move is constrained by fixation and another checkpoint.", "damaged yet still checked volatile corridor", "mixed"),
            ("P3", "oscheos.shy.tdaiin.chol.dor.yky", "`oscheos` heated salt volatile-essence dissolve; `shy`; `tdaiin` energized completion; `chol`; `dor`; `yky` moist contained active.", "The third line shows that even an energized completion still returns to contained moist fluid rather than breaking the page's safety law.", "energized completion under containment", "strong"),
            ("P4", "qokorar.daiin.chckhy.shy.kchor", "`qokorar` deep-source retort; `daiin`; `chckhy` valve-active body-volatile; `shy`; `kchor` body-volatile outlet.", "Reach down to the source root through the retort, then immediately checkpoint and valve the recovered volatile body.", "deep-root retort with valve control", "strong"),
            ("P5", "otchy.tchy.qoky.daiin.r", "`otchy` timed volatile active; `tchy` driven volatile active; `qoky` extracted contained active; `daiin`; terminal `r`.", "The first short line acts like a rapid bench check: drive, extract, confirm, and move on.", "short-line rapid verification", "strong"),
            ("P6", "yshor.shy.daiin.otytchy.daiin", "`yshor` moist transition outlet; `shy`; `daiin`; `otytchy` timed active driven volatile; second `daiin`.", "The second short line doubles the checkpoint, creating the page's most explicit hold-and-confirm rhythm before the process continues.", "double-check midpoint hold", "strong"),
            ("P7", "q*t.cho.ty.cthar.dor.chan.dar", "damaged `q*t`; `cho`; `ty`; `cthar` conduit-earth-root; `dor`; `chan`; `dar`.", "Even where damage intrudes, the route still resolves back to conduit, outlet, cycle, and root fixation.", "damaged root-cycle bridge", "mixed"),
            ("P8", "or.chor.daky.dal.chor.dor.l.shy", "`or/chor` outlet pair; `daky` fixed earth-contained active; `dal` fixed structure; `dor`; `l`; `shy`.", "After the short checks, the page briefly stabilizes into structure and lock before the decisive transition-completion line.", "locked structural interlude", "strong"),
            ("P9", "qotchor.dy.dor.y.tchykchy.shdaiin", "`qotchor` transmuted driven outlet; `dy`; `dor`; `tchykchy` driven volatile contained body-active; `shdaiin` transition-completion.", "This is the unique completion-through-transition event: the changing of state is itself the completion criterion.", "transition itself as completion", "strong"),
            ("P10", "daiin.cthor.chol.ykchor.chordy", "`daiin`; `cthor`; `chol`; `ykchor`; `chordy`.", "Checkpoint again and hold the nearly finished tincture as contained fluid and fixed outlet rather than hurrying to a vessel terminal.", "late fluid checkpoint", "strong"),
            ("P11", "qotchy.qolody.choldy.cthod", "`qotchy` transmuted driven volatile active; `qolody` transmuted fluid heat-fix active; `choldy` volatile fluid fix active; `cthod` conduit heat-fix.", "Drive the fluid through one last fixed conduit corridor so the liquid completion will be lawful rather than accidental.", "final conduit heat-fix corridor", "strong"),
            ("P12", "ykchor.chor.daiin.daiinol", "`ykchor` moist contained volatile outlet; `chor`; `daiin`; `daiinol` completion-fluid.", "The page's whole discipline resolves here: the product is complete as fluid, which is why all the earlier checks mattered.", "completion fused with fluid", "strong"),
            ("P13", "or.octhor.y.tchor", "`or`; `octhor` heated conduit outlet; `y`; `tchor` driven volatile outlet.", "Seal the tincture as an active outlet state rather than a dried or immobilized terminal body.", "active terminal outlet seal", "strong"),
        ],
        tarot_cards=["Justice", "Temperance", "Strength", "The Hermit", "The Priestess", "Judgment", "The Moon", "The Emperor", "Death", "The Star", "The Hierophant", "The World", "The Chariot"],
        movements=["verify the opener", "recheck the active outlet", "energize the checkpoint", "retort down to the root", "run a short bench check", "double-check at midstream", "bridge the damaged root line", "lock the structure briefly", "complete through transition", "checkpoint the fluid again", "heat-fix the conduit", "finish as fluid", "seal the active tincture"],
        direct="`f19r` is a sedative tincture page built on verification density. The manuscript treats the valerian-class product as something that must be checked almost every line, reach down to the root through retort, and only finally declare itself complete when it is complete as fluid.",
        math="Across the formal lenses, `f19r` behaves like a heavily sampled control process. The state is repeatedly projected back into admissible subspaces, with brief line contractions functioning like fast sampling intervals and `daiinol` serving as the liquid-state terminal attractor.",
        mythic="Across the mythic lenses, `f19r` is the healer who keeps checking the patient's breath. It is a page of care through repetition, not bravado through force.",
        compression="Verify almost every step, retort down to the root, let transition itself become completion, and finish with a liquid sedative product in `daiinol`.",
        typed_state_machine=r"""
\[\mathcal R_{f19r} = \{r_{\mathrm{verify}}, r_{\mathrm{deepretort}}, r_{\mathrm{shortcheck}}, r_{\mathrm{transitioncomplete}}, r_{\mathrm{fluidclose}}\}\]
\[\delta(e_{\mathrm{qokorar}}): r_{\mathrm{verify}} \to r_{\mathrm{deepretort}}\]
\[\delta(e_{\mathrm{shdaiin}}): r_{\mathrm{shortcheck}} \to r_{\mathrm{transitioncomplete}}\]
\[\delta(e_{\mathrm{daiinol}}): r_{\mathrm{transitioncomplete}} \to r_{\mathrm{fluidclose}}\]
""",
        invariants=r"""
\[N_{\mathrm{completion}}(f19r)=11, \qquad N_{\mathrm{qo}}(f19r)=7, \qquad N_{\mathrm{dy}}(f19r)=7\]
\[N_{\mathrm{qokorar}}(f19r)=1, \qquad N_{\mathrm{shdaiin}}(f19r)=1, \qquad N_{\mathrm{daiinol}}(f19r)=1\]
""",
        theorem=r"""
\[\rho_* = (\Psi_{P3} \circ \Psi_{P2} \circ \Psi_{P1})(\rho_0)\]

The formal theorem of `f19r` is:

1. sedative preparation is encoded as a hyper-verified process rather than a free-flowing extraction
2. the retort is explicitly required to reach the source root via `qokorar`
3. `shdaiin` proves that transition itself can serve as the completion event
4. the true terminal state is `daiinol`, where the medicine is complete precisely as fluid
""",
        crystal_contribution=[
            "hyper-verification station",
            "deep-source retort line",
            "short-line checkpoint burst",
            "transition-completion gate",
            "completion-fluid tincture close",
        ],
        pointer_title="Hyper-Verified Sedative Tincture",
        pointer_position="the recto of the third Quire C bifolio and verifier-heavy partner to the lacunose page on `f19v`",
        pointer_page_type="single-herb tincture page with the highest checkpoint density in Quire C",
        pointer_conclusion="11 completions, `qokorar`, `shdaiin`, contracted P5-P6, and `daiinol`",
        pointer_judgment="`f19r` teaches that sedative medicine must be made under constant verification. The product only becomes trustworthy when completion fuses with fluid state itself.",
    ),
    make_folio(
        folio_id="F019V",
        quire="C",
        bifolio="bC3 = f19 + f22",
        manuscript_role="double-verified alpine extraction page with preserved lacuna and wet y-prefix terminal",
        purpose="`f19v` is a lacunose but still highly legible process page. The folio preserves a missing line at P6, doubles completion on P4, doubles source fixation in `ddor`, seals two different vessel forms (`darom`, `dom`, `otam`), and ends with a six-token y-prefix chain that leaves the product wet and active. Its title line is a true mega-compound, `otcholcheaiin.cthol`, where the product name compresses its process into miniature form.",
        zero_claim="Keep the alpine extraction honest by preserving the missing witness line, verify the route twice where needed, reinforce the source itself with double fixation, and end not with dryness but with a wet active completed product named by its own process.",
        botanical="`Draba nivalis` / nailwort is a weak local-corpus ID; the process profile is more reliable than the plant assignment",
        risk="moderate",
        confidence="high on the verification and wet-terminal structure, mixed on the lost segment",
        visual_grammar=[
            "`two-plus leaf clusters` = modest herbal form paired with a surprisingly self-describing title line",
            "`paired with f22r on bC3` = lacunose page on one face, still active partner to come on the other",
            "`missing P6` = one of the few honest textual voids in the herbal section and must stay visible",
            "`wet y-prefix close` = the page ends by insisting on hydrated activity rather than a dried terminal body",
        ],
        full_eva="""
P1: pochaiin.cthor.chpcheor.opchey.py.kchy-
P2: qokchy.kchol.sor.qokchor.ykchy.darom-
P3: otchy.chol.daiin.qotol.ytol.daiiin-
P4: ytch.chcthy.qotol.daiin.daiin-
P5: qotchy.qotchy.daiin.doty.qot-
P6: {missing line}-
P6a: ychor.chaiin.cthor=
P7: toy.tchey.qo.dchol.qokchs.dom-
P8: ychor.oky.chor.ytol.chol.oky.ddor-
P9: daiin.chor.daiin.qokoq.y.okchan-
P10: qotol.dor.okchor.daiin.cthor.otam-
P11: otch.okchodshy.daiin.or.otaiin.dair-
P12: yees.ykchol.oty.ytor.ytar.ytchor.ytaiin=
T13: otcholcheaiin.cthol=
""",
        core_vml=[
            "`P6` lacuna = the missing line is part of the witness and must remain visible",
            "`daiin.daiin` on P4 = explicit hold-and-confirm double verification",
            "`ddor` = double fixation anchored at the source/outlet side of the route",
            "`darom`, `dom`, and `otam` = multiple vessel-sealing forms across one page",
            "`P12` y-prefix chain = six consecutive moist/active operators at the close",
            "`T13` mega-compound = the title encodes the process of the product instead of merely naming it",
        ],
        groups=[
            {"label": "P1", "title": "Paragraph 1 - initial extraction and doubled verification", "line_ids": ["P1", "P2", "P3", "P4", "P5"]},
            {"label": "P2", "title": "Paragraph 2 - lacuna, vessel seals, and late checkpoint corridor", "line_ids": ["P6", "P6a", "P7", "P8", "P9", "P10", "P11", "P12"]},
            {"label": "T", "title": "Title line - self-describing mega-compound product name", "line_ids": ["T13"]},
        ],
        lines=[
            ("P1", "pochaiin.cthor.chpcheor.opchey.py.kchy", "`pochaiin` pressed heated volatile cycle complete; `cthor` conduit outlet; `chpcheor` volatile-press volatile-essence outlet; `opchey` heated press volatile essence active; `py`; `kchy` body-volatile active.", "Open by completing a pressed volatile intake and immediately shaping it toward essence outlet and embodied volatile activity.", "pressed volatile-essence opener", "strong"),
            ("P2", "qokchy.kchol.sor.qokchor.ykchy.darom", "`qokchy` extracted contained body-active; `kchol` body-volatile fluid; `sor` salt outlet; `qokchor` extracted contained outlet; `ykchy` moist contained body-active; `darom` fixed root vessel.", "The second line grounds the page by sealing the root in vessel form while keeping the extract bodily and moist.", "root sealed in vessel", "strong"),
            ("P3", "otchy.chol.daiin.qotol.ytol.daiiin", "`otchy` timed volatile active; `chol` fluid; `daiin`; `qotol` transmuted heat-fluid; `ytol` moist driven fluid; `daiiin` triple-cycle completion.", "Move from ordinary checkpointing into extended verification so the wet fluid route can remain admissible.", "triple-cycle verified fluid line", "strong"),
            ("P4", "ytch.chcthy.qotol.daiin.daiin", "`ytch` moist driven volatile; `chcthy` volatile conduit bind; `qotol` transmuted heat-fluid; doubled `daiin`.", "This is the folio's hold-and-confirm line: the process pauses for an explicit double verification before continuing.", "doubled completion hold", "strong"),
            ("P5", "qotchy.qotchy.daiin.doty.qot", "doubled `qotchy`; `daiin`; `doty`; `qot`.", "Repeat the driven transmutation itself and checkpoint it again before the textual gap interrupts the witness.", "doubled retort before lacuna", "strong"),
            ("P6", "{missing line}", "text lacuna preserved exactly as witness loss.", "One procedural step is irrecoverably lost here; the translation must preserve the gap rather than invent a bridge.", "witness lacuna", "strong"),
            ("P6a", "ychor.chaiin.cthor", "`ychor` moist volatile outlet; `chaiin` volatile cycle complete; `cthor` conduit outlet.", "The surviving half-line after the lacuna still shows a sealed moist outlet state, implying a section boundary rather than total collapse.", "post-lacuna section seal", "mixed"),
            ("P7", "toy.tchey.qo.dchol.qokchs.dom", "`toy` driven heat active; `tchey` driven volatile essence active; `qo`; `dchol` fixed volatile fluid; `qokchs` extracted contained volatile dissolve; `dom` fixed heat vessel.", "Re-enter after the gap with driven heat and essence work that quickly resolves into a vessel seal.", "post-gap vessel seal", "strong"),
            ("P8", "ychor.oky.chor.ytol.chol.oky.ddor", "`ychor` moist volatile outlet; `oky` heated contained active; `chor`; `ytol`; `chol`; second `oky`; `ddor` double-fixed source/outlet.", "This is the page's reinforcement line: the source side of the route is fixed twice so the fragile material can survive later wet handling.", "double-fixed source reinforcement", "strong"),
            ("P9", "daiin.chor.daiin.qokoq.y.okchan", "`daiin`; `chor`; second `daiin`; `qokoq` extract-contain heat-transmute; `y`; `okchan` heated contained volatile cycle.", "Another double checkpoint follows the reinforced source, proving that the page trusts verification more than speed.", "double checkpoint after reinforcement", "strong"),
            ("P10", "qotol.dor.okchor.daiin.cthor.otam", "`qotol` transmuted heat-fluid; `dor`; `okchor`; `daiin`; `cthor`; `otam` timed heat union vessel.", "The late corridor combines fluid transmutation with one more checkpoint and a timed union in vessel.", "timed union in vessel", "strong"),
            ("P11", "otch.okchodshy.daiin.or.otaiin.dair", "`otch` timed volatile; `okchodshy` heated contained volatile heat-fix transition active; `daiin`; `or`; `otaiin`; `dair`.", "Keep the route timed and contained through one more checkpoint so the wet ending can arrive without losing fixation.", "timed contained preterminal check", "strong"),
            ("P12", "yees.ykchol.oty.ytor.ytar.ytchor.ytaiin", "`yees` moist double-essence dissolve; `ykchol` moist contained volatile fluid; `oty`; `ytor`; `ytar`; `ytchor`; `ytaiin` moist driven completion.", "The final operational line refuses drying entirely: it ends as a fully wet active process chain, not as a desiccated close.", "wet y-prefix terminal chain", "strong"),
            ("T13", "otcholcheaiin.cthol", "`otcholcheaiin` timed volatile fluid volatile essence complete; `cthol` conduit fluid.", "The title names the product by replaying its whole process in compressed form, as though the recipe has become its own label.", "mega-compound title as recipe", "strong"),
        ],
        tarot_cards=["The Magician", "Justice", "Temperance", "The Priestess", "Strength", "The Hanged Man", "Judgment", "The Emperor", "The Hermit", "The Lovers", "The Star", "The Moon", "The World", "The Hierophant"],
        movements=["complete the pressed intake", "seal the root in vessel", "extend verification", "hold and confirm", "double the transmutation", "preserve the gap", "seal the surviving outlet", "seal again after the gap", "reinforce the source twice", "double-check again", "time the union in vessel", "checkpoint before the wet close", "end in moist active completion", "compress the recipe into the title"],
        direct="`f19v` is a double-verified alpine extraction page that stays honest about loss. It preserves its missing line, reasserts vessel law and source reinforcement afterward, and ends in a wet active product whose title encodes its process.",
        math="Across the formal lenses, `f19v` behaves like a partially observed control process. One state transition is missing from the witness, but the remaining lines still show a stable pattern of verification, source reinforcement, and moist terminal completion.",
        mythic="Across the mythic lenses, `f19v` is the page that keeps working despite a tear in memory. The craft survives because the remaining steps still know what they are for.",
        compression="Preserve the lacuna, verify twice when needed, reinforce the source with `ddor`, keep sealing the route in vessels, and finish wet in the y-prefix chain named by the mega-compound title.",
        typed_state_machine=r"""
\[\mathcal R_{f19v} = \{r_{\mathrm{verify}}, r_{\mathrm{lacuna}}, r_{\mathrm{recovery}}, r_{\mathrm{wetclose}}, r_{\mathrm{title}}\}\]
\[\delta(e_{\mathrm{P6\ lacuna}}): r_{\mathrm{verify}} \to r_{\mathrm{lacuna}}\]
\[\delta(e_{\mathrm{ddor}}): r_{\mathrm{lacuna}} \to r_{\mathrm{recovery}}\]
\[\delta(e_{\mathrm{ytaiin}}): r_{\mathrm{recovery}} \to r_{\mathrm{wetclose}} \to r_{\mathrm{title}}\]
""",
        invariants=r"""
\[N_{\mathrm{daiin.daiin}}(f19v)=1, \qquad N_{\mathrm{daiiin}}(f19v)=1, \qquad N_{\mathrm{ddor}}(f19v)=1\]
\[N_{\mathrm{lacuna}}(f19v)=1, \qquad N_{\mathrm{dom}}(f19v)=1, \qquad N_{\mathrm{otam}}(f19v)=1, \qquad N_{\mathrm{y\text{-}prefix\ chain}}(f19v)=6\]
""",
        theorem=r"""
\[\rho_* = (\Psi_{T} \circ \Psi_{P2} \circ \Psi_{P1})(\rho_0)\]

The formal theorem of `f19v` is:

1. the page must preserve a genuine internal lacuna rather than erase it
2. doubled verification and doubled source fixation compensate for the fragility of the route
3. the operational close remains wet and active instead of resolving into a dry terminal state
4. the title line functions as a self-describing compressed recipe, not a bare label
""",
        crystal_contribution=[
            "lacuna-preserving alpine station",
            "doubled completion hold line",
            "double-fixed source reinforcement route",
            "wet y-prefix terminal corridor",
            "mega-compound title close",
        ],
        pointer_title="Double-Verified Alpine Extraction with Lacuna",
        pointer_position="the verso of the third Quire C bifolio and lacunose counterpart to the hyper-verified tincture on `f19r`",
        pointer_page_type="single-herb extraction page with one missing line, one mega-compound title, and a wet active terminal",
        pointer_conclusion="missing `P6`, `daiin.daiin`, `ddor`, `otam`, the six-token y-prefix chain, and title `otcholcheaiin.cthol`",
        pointer_judgment="`f19v` proves that the manuscript can survive a textual wound without pretending it is whole. The missing line remains missing, but the rest of the page still shows a wet, reinforced, vessel-governed extraction path.",
    ),
]


def main() -> None:
    for folio in FOLIOS:
        (FOLIOS_DIR / f"{folio['folio_id']}_FINAL_DRAFT.md").write_text(render_folio(folio), encoding="utf-8")
        (FOLIOS_DIR / f"{folio['folio_id']}.md").write_text(render_pointer(folio), encoding="utf-8")


if __name__ == "__main__":
    main()
