from __future__ import annotations

from render_f007_to_f008_parallel_batch import FOLIOS_DIR, render_folio, render_pointer
from render_f009_to_f010_parallel_batch import make_folio


FOLIOS: list[dict[str, object]] = [
    make_folio(
        folio_id="F011R",
        quire="B",
        bifolio="bB3 = f11 + f14",
        manuscript_role="fire-sealed aromatic distillation page with maximum precision fixation",
        purpose="`f11r` is Quire B's first precision-aromatic page. The leaf begins with `tshol`, ignites with `fy`, compresses the central apparatus move into `shcfhydaiin`, then keeps checkpointing the route until `dod` locks a heat step between two fixations. The page is safe in material profile but severe in control demands, which makes it the cleanest local proof that high fixation density in Book I measures precision and volatile preservation rather than danger alone.",
        zero_claim="Start from energized salt-fluid, pass the aromatic body through an integrated fire-sealed alembic route, heat-sandwich the volatile under `dod`, and finish the second phase as a fixed conduit-bound distillate.",
        botanical="`Rosmarinus officinalis` (strong local-corpus fit; Hungary Water class reading)",
        risk="safe",
        confidence="high on sealed aromatic distillation and precision fixation",
        visual_grammar=[
            "`stem-root line` = source and product linked by one direct route rather than a branching plant grammar",
            "`single narrow-leaf herbal` = aromatic herb fit is plausible, but the process profile is stronger than the image alone",
            "`two-paragraph page` = first sealed extraction block, then second fixation-and-locking block",
            "`paired in bB3` = safe precision page before the later doubling pages across the same bifolio",
        ],
        full_eva="""
P1: tshol.schoal.fy.shcfhydaiin.cphy.shey.k.chody.shoyty-
P2: socthody.qodor.y.kshy.daiin.ytchy.ytchoky.kchol.daiin-
P3: qoty.chol.cthy.dor.ykychy.choty.dain.chaiin.daiin.dod-
P4: dchol.chy.kchy.dy.daiin=
P5: tchol.shor.shor.dky.**y.daiin.cthy.dy.chodl.daiin-
P6: odl.d.s.y.otol.chaiin.ykchor.dair.chody.cthy.s.daiin-
P7: qotchy.okchol.cthy.dy=
""",
        core_vml=[
            "`tshol` = energized salt-heated-fluid opener",
            "`shcfhydaiin` = most complex embedded fire-seal compound in the local corpus",
            "`d-` at 22.2% = fixation overload in a safe page, proving precision rather than poison",
            "`dod` = fix-heat-fix sandwich around the volatile step",
            "`shor.shor` = doubled transition outlet in the second paragraph",
            "`dair` = timed rotational fixation rather than a loose terminal exit",
        ],
        groups=[
            {"label": "P1", "title": "Paragraph 1 - integrated fire-sealed distillation", "line_ids": ["P1", "P2", "P3", "P4"]},
            {"label": "P2", "title": "Paragraph 2 - doubled transition and timed fixation", "line_ids": ["P5", "P6", "P7"]},
        ],
        lines=[
            ("P1", "tshol.schoal.fy.shcfhydaiin.cphy.shey.k.chody.shoyty", "`tshol` energized salt-heated fluid; `fy` fire-active; `shcfhydaiin` embedded fire-seal moist-fix complete; `cphy` alembic-active.", "Open by igniting a salt-fluid start and pushing the aromatic body straight into an integrated fire-sealed alembic route.", "integrated fire-sealed alembic opener", "strong"),
            ("P2", "socthody.qodor.y.kshy.daiin.ytchy.ytchoky.kchol.daiin", "`socthody` salt through heated conduit to fix; `qodor` transmute-fix outlet; two `daiin` checkpoints.", "Carry the salted volatile through conduit fixation and verify the containment twice before advancing.", "salted conduit proof with twin checkpoints", "strong"),
            ("P3", "qoty.chol.cthy.dor.ykychy.choty.dain.chaiin.daiin.dod", "`qoty` heated transmutation; `ykychy` double-moist volatile containment; `dod` fix-heat-fix.", "Transmute the volatile fluid under conduit bind, keep it double-moistened, and clamp the heating step between two fixations.", "heat-sandwich precision lock", "strong"),
            ("P4", "dchol.chy.kchy.dy.daiin", "`dchol` fixed volatile fluid; `kchy` body-volatile active; `dy` fixed; `daiin` checkpoint.", "Seal the first block by certifying that the volatile body has become a fixed fluid state.", "phase-one seal", "strong"),
            ("P5", "tchol.shor.shor.dky.**y.daiin.cthy.dy.chodl.daiin", "`shor.shor` doubled transition outlet; `dky` fixed containment; damaged `**y`; `chodl` volatile heat-fix lock.", "Restart the route with two outlet transitions, preserve the damaged active token, and lock the volatile back into fixed conduit control.", "double-transition restart", "mixed"),
            ("P6", "odl.d.s.y.otol.chaiin.ykchor.dair.chody.cthy.s.daiin", "`odl` heat-fix lock; `otol` timed heated fluid; `ykchor` moist contained outlet; `dair` timed fixation.", "Move the distillate through timed heated fluid and one measured fixation cycle before dissolving it back into conduit governance.", "timed fixation cycle", "strong"),
            ("P7", "qotchy.okchol.cthy.dy", "`qotchy` driven transmuted volatile; `okchol` heated contained volatile fluid; `cthy` conduit bind; `dy` fixed.", "Close by proving that the transmuted aromatic volatile can remain fixed inside heated conduit-bound fluid.", "fixed conduit-bound aromatic close", "strong"),
        ],
        tarot_cards=["Temperance", "Justice", "Strength", "The Hermit", "The Chariot", "Wheel of Fortune", "The Sun"],
        movements=["ignite the salt route", "verify the conduit twice", "heat-sandwich the volatile", "seal the first phase", "double the outlet transition", "time the fixation", "finish as fixed distillate"],
        direct="`f11r` reads as a rosemary-class aromatic distillation page where fire sealing is integrated into the process itself rather than added as a boundary condition. The safe herb still demands maximum fixation because the product is volatile, not because the matter is poisonous.",
        math="Across the formal lenses, `f11r` is a precision-preservation corridor. The operator family concentrates on keeping the volatile inside a sealed and repeatedly verified route, with `dod` behaving like a local sandwich operator that stabilizes the heating pulse between two fixation states.",
        mythic="Across the mythic lenses, `f11r` is the perfumer's discipline lesson. Nothing spectacular happens except that every beautiful thing is prevented from escaping.",
        compression="Ignite the aromatic salt-fluid, integrate the fire seal into the alembic path, clamp heat inside `dod`, and finish as a fixed conduit-bound distillate.",
        typed_state_machine=r"""
\[\mathcal R_{f11r} = \{r_{\mathrm{saltfire}}, r_{\mathrm{sealedistill}}, r_{\mathrm{sandwichfix}}, r_{\mathrm{timedclose}}\}\]
\[\delta(e_{\mathrm{shcfhydaiin}}): r_{\mathrm{saltfire}} \to r_{\mathrm{sealedistill}} \to r_{\mathrm{sandwichfix}} \to r_{\mathrm{timedclose}}\]
\[\delta(e_{\mathrm{dod}}): r_{\mathrm{sealedistill}} \to r_{\mathrm{sandwichfix}}\]
""",
        invariants=r"""
\[N_{d}(f11r)=12, \qquad N_{\mathrm{daiin/dain}}(f11r)=8, \qquad N_{\mathrm{fireseal}}(f11r)=1\]
\[N_{\mathrm{dod}}(f11r)=1, \qquad N_{\mathrm{shor.shor}}(f11r)=1, \qquad N_{\mathrm{dy}}(f11r)\ge 3\]
""",
        theorem=r"""
\[\rho_* = (\Psi_{P2} \circ \Psi_{P1})(\rho_0)\]

The formal theorem of `f11r` is:

1. the page opens with salt-fluid and ignition rather than with passive herb description
2. `shcfhydaiin` proves that the fire seal is embedded inside a flowing aromatic route
3. `dod` forces the heat step to occur between two fixation boundaries
4. the second paragraph turns sealed extraction into timed, conduit-bound completion
""",
        crystal_contribution=[
            "precision aromatic distillation station",
            "embedded fire-seal compound line",
            "heat-sandwich fixation operator",
            "doubled transition outlet route",
            "timed aromatic close",
        ],
        pointer_title="Precision Aromatic Distillation",
        pointer_position="the recto of the third Quire B bifolio and first safe precision-distillation page of the quire",
        pointer_page_type="single-herb aromatic distillation page with two-phase structure and heavy fixation",
        pointer_conclusion="`shcfhydaiin`, `dod`, `shor.shor`, and `dair`",
        pointer_judgment="`f11r` distills a safe aromatic herb under maximum precision: integrate the fire seal, protect the heat pulse, and verify the volatile until it can be fixed without loss.",
    ),
    make_folio(
        folio_id="F011V",
        quire="B",
        bifolio="bB3 = f11 + f14",
        manuscript_role="maximum-fixation dye and medicine extraction page with early union and minimal heat",
        purpose="`f11v` is the fixation-saturated answer to `f11r`. Instead of centered fire discipline, the leaf locks nearly every line with `-dy`, introduces union almost immediately through `dam`, double-dissolves the active body in `chololar`, and culminates in the unique `ddy` terminal. The result is a safe page whose difficulty lies in stabilizing a stubborn compound rather than in surviving a poison.",
        zero_claim="Fix nearly every step of the turmeric route, join the extract to a carrier early, dissolve the active body twice at the root, and only close once the page can sustain doubled fixation intensity.",
        botanical="`Curcuma longa` (good local-corpus fit; cold oil / dye extraction reading)",
        risk="safe",
        confidence="high on fixation saturation, early union, and double-dissolution",
        visual_grammar=[
            "`top-of-stem concentration` = process weight moves from root material directly into terminal product handling",
            "`circular root elements` = rhizome or sliced-body cue consistent with turmeric-class processing",
            "`short six-line leaf` = compressed but relentless verification pattern",
            "`paired in bB3` = safe aromatic precision on recto answered by safe fixation saturation on verso",
        ],
        full_eva="""
P1: poldchody.shcphy.shordy.qoty.shol.cphar.dan.y-
P2: shol.dy.chckhy.shcthy.daiin.dam.ykchy.dain.dchy-
P3: otchor.dy.kchy.tchy.dar.qokchd.oky.chol.dy.dy-
P4: qokchor.chololar.chyky.dchy.qoky.ctho.tchey.tu-
P5: loydy.qoteey.qot.chor.dy.ddy.cthor.shyarg-
P6: ycheor.ksho.dor.cthoy.s.chold=
""",
        core_vml=[
            "`-dy` x10 in 6 lines = highest fixation density per line in the current corpus",
            "`dam` in line 2 = early union with a carrier or co-substance",
            "`chololar` = double-fluid root dissolution",
            "`ddy` = unique double-d fixation terminal",
            "`tu` = extremely rare direct-address or abbreviated operator marker",
            "`o=1` in the local cross-reference = minimal direct heat despite heavy fixation",
        ],
        groups=[
            {"label": "P1", "title": "Paragraph 1 - early union and fixation saturation", "line_ids": ["P1", "P2", "P3"]},
            {"label": "P2", "title": "Paragraph 2 - double dissolution and doubled fixation close", "line_ids": ["P4", "P5", "P6"]},
        ],
        lines=[
            ("P1", "poldchody.shcphy.shordy.qoty.shol.cphar.dan.y", "`poldchody` press-fluid-fix volatile heat-fix active; `shcphy` transition alembic active; `cphar` alembic-root; `dan` fix-cycle.", "Compress the opening operation into one fixed pressed-fluid route and anchor it immediately in alembic handling.", "compressed fixed opener", "strong"),
            ("P2", "shol.dy.chckhy.shcthy.daiin.dam.ykchy.dain.dchy", "`shol.dy` transition fluid fixed; `chckhy` volatile valve check; `dam` union; `ykchy` moist contained volatile.", "Verify the volatile under valve control and join it to a carrier early rather than waiting for a late conjunction.", "early union under valve check", "strong"),
            ("P3", "otchor.dy.kchy.tchy.dar.qokchd.oky.chol.dy.dy", "`otchor` timed volatile outlet; `dar` root fix; `qokchd` extracted contained volatile fixed; terminal `dy.dy`.", "Time the outlet, return the extract to root fixation, and land the line in an emphatic double-fixed state.", "double-fixed root return", "strong"),
            ("P4", "qokchor.chololar.chyky.dchy.qoky.ctho.tchey.tu", "`qokchor` extract contained outlet; `chololar` double-fluid root; `ctho` conduit heat; rare `tu` terminal.", "Extract the outlet, dissolve the active body twice into fluid, and mark the operator with the page's rare direct-address or abbreviation token.", "double-dissolution operator cue", "strong"),
            ("P5", "loydy.qoteey.qot.chor.dy.ddy.cthor.shyarg", "`loydy` locked heated active fixation; `qoteey` double-essence transmutation; `ddy` double-d fixation.", "Escalate from fixed active lock into double-essence transmutation and certify the result with the manuscript's unique doubled-fix terminal.", "double-essence doubled-fix climax", "strong"),
            ("P6", "ycheor.ksho.dor.cthoy.s.chold", "`ycheor` moist volatile essence outlet; `ksho` contained transition heat; `dor` fix outlet; `chold` volatile heat-fluid fix.", "Release the moist essence only after it can leave as a fixed heated fluid body under contained transition control.", "moist essence fixed close", "strong"),
        ],
        tarot_cards=["Justice", "Temperance", "Strength", "The Priestess", "The Empress", "The Sun"],
        movements=["compress the first operation", "join the carrier early", "double-fix the outlet", "dissolve twice at the root", "escalate to doubled fixation", "release only as fixed essence"],
        direct="`f11v` is a turmeric-class fixation page. The route is safe, minimally heated, and obsessed with preserving an unstable active compound by union, repeated containment, and redundant fixation.",
        math="Across the formal lenses, `f11v` behaves like a cold-biased stabilization system. The state evolution is dominated by fixed-point reinforcement rather than by energy injection, while `dam`, `chololar`, and `ddy` mark the carrier join, double dissolution, and doubled terminal lock.",
        mythic="Across the mythic lenses, `f11v` is the patient apothecary's yellow page: nothing is trusted until it has been fixed again, and then fixed one more time.",
        compression="Fix everything, join the carrier early, dissolve the root-body twice, and end only on `ddy`-grade certainty.",
        typed_state_machine=r"""
\[\mathcal R_{f11v} = \{r_{\mathrm{compressed}}, r_{\mathrm{union}}, r_{\mathrm{doublefluid}}, r_{\mathrm{doublefix}}\}\]
\[\delta(e_{\mathrm{dam}}): r_{\mathrm{compressed}} \to r_{\mathrm{union}}\]
\[\delta(e_{\mathrm{ddy}}): r_{\mathrm{doublefluid}} \to r_{\mathrm{doublefix}}\]
""",
        invariants=r"""
\[N_{\mathrm{dy}}(f11v)=10, \qquad N_{d}(f11v)=10, \qquad N_{\mathrm{dam}}(f11v)=1\]
\[N_{\mathrm{ddy}}(f11v)=1, \qquad N_{\mathrm{chololar}}(f11v)=1, \qquad N_{\mathrm{tu}}(f11v)=1\]
""",
        theorem=r"""
\[\rho_* = (\Psi_{P2} \circ \Psi_{P1})(\rho_0)\]

The formal theorem of `f11v` is:

1. fixation, not heat, is the dominant operator family of the page
2. `dam` proves that carrier union belongs near the start of this route
3. `chololar` marks a double-fluid dissolution stage before terminal locking
4. `ddy` certifies the strongest safe fixation terminal yet seen in Quire B
""",
        crystal_contribution=[
            "maximum-fixation safe extraction station",
            "early carrier-union line",
            "double-fluid root dissolution route",
            "double-d fixation terminal",
            "minimal-heat stabilization page",
        ],
        pointer_title="Maximum-Fixation Extraction",
        pointer_position="the verso of the third Quire B bifolio and safe counterpart to the rosemary precision page",
        pointer_page_type="single-herb fixation-saturated extraction page with early union and doubled fixation close",
        pointer_conclusion="`-dy` saturation, `dam`, `chololar`, `ddy`, and rare `tu`",
        pointer_judgment="`f11v` teaches how to preserve a difficult active body: fix almost every move, join the carrier early, double-dissolve the root, and only then allow the product to close.",
    ),
    make_folio(
        folio_id="F013R",
        quire="B",
        bifolio="bB4 = f13 + [f12 missing]",
        manuscript_role="non-separative dual-source extraction page with mid-process fire sealing",
        purpose="`f13r` is one of Quire B's clearest structural pages. The leaf opens on `torshor`, closes on `okorory`, saturates the middle with `-kchy` compounds, spikes to `oeees`, and applies `cfhol` in the middle instead of at a boundary. The page reads less like a simple plant handling page than like a decision to keep body and volatile together while working two source references through a heated route.",
        zero_claim="Process a dual-source body without separating volatile from material, intensify it through `oeees`, apply the fire seal in the middle of the route, and close on a triple-heated doubled-source terminal.",
        botanical="`Musa acuminata` remains weak and debated; process profile is much stronger than species fit",
        risk="moderate",
        confidence="high on non-separative dual-source extraction, low on exact plant ID",
        visual_grammar=[
            "`stem-root line` = direct routing motif persists even though the species fit is weak",
            "`bifolio with missing partner` = local uncertainty about the larger instructional pair remains visible",
            "`textual frame bracket` = `torshor` and `okorory` matter more than image taxon here",
            "`mid-page fire seal` = the layout behaves like an internal technical intervention, not a ceremonial boundary",
        ],
        full_eva="""
P1: torshor.opchy.shol.dy.qopchy.shol.opchor.dypchy.dchg-
P2: dchol.chol.dol.shkchy.ydal.shy.ykchy.qot*y.daiin.s.y-
P3: s.y.dchor.shaiin.oeees.ykor.chor.ytshy.ykchy.kchy.dar-
P4: qodchy.ytchy.otchor=
P5: shorodo.shy.tshy.kchol.dpchy.qopchy.otchol.cfhol.dy-
P6: tchor.dor.daiin.qotchol.okchy.okchor.oiin.chckhy.d-
P7: dchy.qoky.chol.dy.qo**y.d.oldy.okchor.doaiin-
P8: shochy.qokchy.torchy.k**.s.okchey.daiin-
P9: oldy.shey.chol.doiin.ykoly.okchal.daldy-
P10: sotchy.kchy.okorory=
""",
        core_vml=[
            "`torshor` <-> `okorory` = opening and closing double-source frame bracket",
            "`-kchy` x6 = body and volatile kept jointly active instead of fully separated",
            "`oeees` = triple-essence concentration spike",
            "`cfhol` = fire seal appears mid-page, not at a quire boundary",
            "`okorory` = unique triple-heated doubled-source close",
            "`-dy` x8 = heavy fixation despite non-separative handling",
        ],
        groups=[
            {"label": "P1", "title": "Paragraph 1 - dual-source non-separative opener", "line_ids": ["P1", "P2", "P3", "P4"]},
            {"label": "P2", "title": "Paragraph 2 - internal fire seal and framed close", "line_ids": ["P5", "P6", "P7", "P8", "P9", "P10"]},
        ],
        lines=[
            ("P1", "torshor.opchy.shol.dy.qopchy.shol.opchor.dypchy.dchg", "`torshor` doubled-source opener; `opchy/qopchy/opchor` pressing volatile route; `dy` fixed.", "Open by naming two source references at once and keeping the pressed volatile in a fixed but still active route.", "double-source press opener", "strong"),
            ("P2", "dchol.chol.dol.shkchy.ydal.shy.ykchy.qot*y.daiin.s.y", "`dchol/chol/dol` fluid fixation chain; `shkchy` transition-contained volatile; `ykchy` first moist contained volatile; damaged `qot*y`.", "Continue without separating body from volatile, preserve the damaged transmutation token, and checkpoint the jointly active route.", "first non-separative containment block", "mixed"),
            ("P3", "s.y.dchor.shaiin.oeees.ykor.chor.ytshy.ykchy.kchy.dar", "`oeees` triple essence; `ykor/chor` outlet pair; `ykchy.kchy` body-volatile cluster; `dar` root fix.", "Raise the joint body-volatile route into triple essence and return it to root fixation without ever fully splitting the two bodies apart.", "triple-essence non-separative spike", "strong"),
            ("P4", "qodchy.ytchy.otchor", "`qodchy` transmute fixed volatile; `ytchy` moist driven volatile; `otchor` timed outlet.", "Seal the first block as a transmuted volatile outlet that is still timed and actively driven.", "phase-one timed seal", "strong"),
            ("P5", "shorodo.shy.tshy.kchol.dpchy.qopchy.otchol.cfhol.dy", "`shorodo` transition outlet heat-fix heat; `kchol` body volatile fluid; `cfhol` fire-sealed fluid.", "Reopen the process with transition heat, keep the body inside volatile fluid, and apply the fire seal in the middle of the route.", "mid-process fire-seal intervention", "strong"),
            ("P6", "tchor.dor.daiin.qotchol.okchy.okchor.oiin.chckhy.d", "`tchor` driven volatile outlet; `daiin` checkpoint; `qotchol` transmuted volatile fluid; `okchy/okchor` heated contained volatile pair; `chckhy` valve check.", "Drive the non-separative fluid through outlet, containment, and valve governance before allowing the route to proceed.", "valve-governed non-separative corridor", "strong"),
            ("P7", "dchy.qoky.chol.dy.qo**y.d.oldy.okchor.doaiin", "`dchy` fixed volatile active; `qoky` extract contain active; damaged `qo**y`; `oldy` fluid-fix active; `doaiin` fix-heat cycle complete.", "Extract from the still-joint body, preserve the damaged transmutation token, and certify the route as a completed heat-fix cycle.", "damaged extraction proof", "mixed"),
            ("P8", "shochy.qokchy.torchy.k**.s.okchey.daiin", "`shochy` transition heat volatile; `qokchy` extract contain volatile active; damaged `k**`; `okchey` heated contained volatile essence.", "Heat the volatile body again, contain its essence, and checkpoint the damaged body token instead of erasing it.", "essence checkpoint with damage retained", "mixed"),
            ("P9", "oldy.shey.chol.doiin.ykoly.okchal.daldy", "`oldy` fluid-fix active; `shey` transition essence; `doiin` fix-heat cycle; `ykoly` moist contained fluid; `okchal/daldy` structural fixation.", "Convert the non-separative extract into a structurally fixed fluid body before the final close.", "structural rebind before close", "strong"),
            ("P10", "sotchy.kchy.okorory", "`sotchy` salt-heated driven volatile; `kchy` body-volatile active; `okorory` triple-heated doubled-source terminal.", "Close by naming the body-volatile pair one last time and collapsing the whole route into a doubled-source heated terminal.", "double-source terminal close", "strong"),
        ],
        tarot_cards=["The Lovers", "Strength", "The Devil", "Temperance", "The Tower", "Justice", "The Moon", "The Hermit", "The Emperor", "The World"],
        movements=["name both sources", "keep body and volatile together", "raise to triple essence", "seal the timed outlet", "apply internal fire seal", "govern by valve", "carry damaged proof forward", "checkpoint the contained essence", "rebind into structure", "close on doubled source"],
        direct="`f13r` is a non-separative dual-source extraction leaf. The page keeps body and volatile active together, compresses them through a triple-essence spike, and uses the fire seal as an internal technical tool rather than a structural border.",
        math="Across the formal lenses, `f13r` is a constrained joint-state evolution problem. The system resists factorization into separate body and volatile channels, and the page instead works by preserving a coupled state until `cfhol` and the final `okorory` terminal force the joint attractor into a heated doubled-source close.",
        mythic="Across the mythic lenses, `f13r` is the refusal-to-divorce page. The matter and its spirit stay married through the whole ordeal, and the furnace intervenes only to keep the marriage from dissolving.",
        compression="Keep body and volatile together, spike the coupled state with `oeees`, apply `cfhol` midstream, and close on `okorory`.",
        typed_state_machine=r"""
\[\mathcal R_{f13r} = \{r_{\mathrm{dualopen}}, r_{\mathrm{jointstate}}, r_{\mathrm{firesealed}}, r_{\mathrm{doublesource}}\}\]
\[\delta(e_{\mathrm{oeees}}): r_{\mathrm{jointstate}} \to r_{\mathrm{jointstate}}\]
\[\delta(e_{\mathrm{cfhol}}): r_{\mathrm{jointstate}} \to r_{\mathrm{firesealed}} \to r_{\mathrm{doublesource}}\]
""",
        invariants=r"""
\[N_{\mathrm{kchy}}(f13r)\ge 6, \qquad N_{\mathrm{cfhol}}(f13r)=1, \qquad N_{\mathrm{oeees}}(f13r)=1\]
\[N_{\mathrm{okorory}}(f13r)=1, \qquad N_{\mathrm{daiin}}(f13r)=3, \qquad N_{\mathrm{dy}}(f13r)\ge 5\]
""",
        theorem=r"""
\[\rho_* = (\Psi_{P2} \circ \Psi_{P1})(\rho_0)\]

The formal theorem of `f13r` is:

1. the page is framed by doubled-source language at both opening and close
2. `-kchy` density prevents a clean separation of body from volatile through most of the route
3. `cfhol` confirms that fire sealing is an internal operational intervention
4. the final terminal is not neutral completion but a heated doubled-source attractor
""",
        crystal_contribution=[
            "non-separative dual-source station",
            "body-volatile coupled-state line",
            "mid-process fire-seal intervention",
            "triple-essence joint-state spike",
            "double-source terminal close",
        ],
        pointer_title="Non-Separative Dual-Source Extraction",
        pointer_position="the recto of the fourth Quire B bifolio whose partner folio is missing",
        pointer_page_type="single-herb but weakly identified coupled-state extraction page with internal fire seal",
        pointer_conclusion="`torshor`, `-kchy` x6, `oeees`, mid-page `cfhol`, and `okorory`",
        pointer_judgment="`f13r` teaches a dual-source route that refuses full separation: hold body and volatile together, seal midstream, and close only when the doubled source can survive peak heat.",
    ),
    make_folio(
        folio_id="F013V",
        quire="B",
        bifolio="bB4 = f13 + [f12 missing]",
        manuscript_role="retort extraction page that turns into structural building and salve-like fixation",
        purpose="`f13v` is the clearest two-phase page of this Quire B batch. The first five lines are a retort extraction corridor ending on `qoky.daiin=`, and the second half opens with `foldaiin` before building a structural matrix through repeated `-al/-tal` terminals, `kokydaiin`, and `tchtod`. The page looks like a liquid capture that is then forced into durable form.",
        zero_claim="Extract the aromatic volatile through retort logic, reopen the route with fire-fluid completion, trap and pump the body into a repeatedly structured matrix, and close only when the page can seal as `dal`.",
        botanical="`Lonicera periclymenum` (moderate local-corpus fit; aromatic flower-water or salve reading)",
        risk="moderate",
        confidence="high on two-phase extraction/build structure, moderate on species",
        visual_grammar=[
            "`all structures at top of stem` = concentrated terminal processing with minimal intermediate stages",
            "`two-plus leaf clusters` = shared top-heavy visual grammar with other concentrated-processing leaves",
            "`twining/climbing habit` = honeysuckle-like reading remains plausible but not decisive",
            "`textual section seal at P5` = the page itself divides cleanly into extraction then building",
        ],
        full_eva="""
P1: koais.chtoiin.otchy.kchod.otol.otchy.octhos-
P2: oko.qokol.chodal.otchol.cphol.choty-
P3: qokchy.qokod.chy.otchy.cthody-
P4: o.l.s.chey.okos.oain.okshy.qo*-
P5: qoky.daiin=
P6: foldaiin.olcphy.chol.dy.oty.shor.qotyd.dairod-
P7: dain.okal.chy.qokchory.dchy.kokydaiin.shon-
P8: otchy.daiin.y.dain.ykol.okchy.okald.d.ytaiin-
P9: tchtod.otal.cthor.ytal.y.cho.tal.sho.qocthy-
P10: y.ol.chy.kchey.kchor.dal=
""",
        core_vml=[
            "`qoky.daiin=` = hard section seal ending the extraction phase",
            "`foldaiin` = fire-fluid-fix-complete pivot into phase 2",
            "`kokydaiin` = double containment around active heating",
            "`-al/-tal` cluster = structural terminals dominate the building phase",
            "`tchtod` = energy-pumped volatile under heat-fixation",
            "`dal` = structural fixation terminal closing the page",
        ],
        groups=[
            {"label": "P1", "title": "Paragraph 1 - retort extraction corridor", "line_ids": ["P1", "P2", "P3", "P4", "P5"]},
            {"label": "P2", "title": "Paragraph 2 - structural building and matrix lock", "line_ids": ["P6", "P7", "P8", "P9", "P10"]},
        ],
        lines=[
            ("P1", "koais.chtoiin.otchy.kchod.otol.otchy.octhos", "`koais` contain-heat-earth-cycle dissolve opener; `chtoiin` volatile driven heat cycle; `kchod` body-volatile heat-fix.", "Begin the extraction by containing, heating, and dissolving the volatile body through a driven heat cycle.", "extraction opener", "strong"),
            ("P2", "oko.qokol.chodal.otchol.cphol.choty", "`oko` heated containment; `qokol` extract contained fluid; `chodal` volatile heat-fix structure; `cphol` alembic fluid.", "Extract a contained fluid through alembic handling and start hinting at structure before the first phase is over.", "contained alembic extraction", "strong"),
            ("P3", "qokchy.qokod.chy.otchy.cthody", "`qokchy` extract contain volatile active; `qokod` extract contain heat-fix; `cthody` conduit heat-fix active.", "Drive the volatile through a retort-and-conduit corridor where extraction and fixation are already coupled.", "retort conduit corridor", "strong"),
            ("P4", "o.l.s.chey.okos.oain.okshy.qo*", "`o.l.s` heat fluid dissolve; `chey` volatile essence active; `okos` heated contained dissolve; damaged `qo*` transmutation.", "Reduce the route to heat, fluid, and dissolve, then preserve the damaged transmutation token instead of smoothing it away.", "damaged dissolve line", "mixed"),
            ("P5", "qoky.daiin", "`qoky` extract contain active; `daiin` checkpoint and seal.", "Seal the first phase as a completed contained extraction.", "phase-one extraction seal", "strong"),
            ("P6", "foldaiin.olcphy.chol.dy.oty.shor.qotyd.dairod", "`foldaiin` fire-fluid-fix-complete; `olcphy` fluid alembic active; `qotyd` transmute heat active fix; `dairod` rotational heat-root fixation.", "Open the second phase with fire-applied fluid completion and turn the extract toward structured rotational fixation.", "fire-to-structure pivot", "strong"),
            ("P7", "dain.okal.chy.qokchory.dchy.kokydaiin.shon", "`okal` heat-contained structure; `qokchory` extracted contained volatile heat outlet active; `kokydaiin` double containment complete.", "Build the first explicit structure and trap the active volatile inside a double-contained heated matrix.", "double-contained structure build", "strong"),
            ("P8", "otchy.daiin.y.dain.ykol.okchy.okald.d.ytaiin", "`otchy` timed volatile active; `ykol` moist contained fluid; `okald` heated contained structure fix; `ytaiin` moist-driven completion.", "Checkpoint the volatile again, moisten the contained fluid, and thicken the structure into a fixed moist completion.", "moist structural thickening", "strong"),
            ("P9", "tchtod.otal.cthor.ytal.y.cho.tal.sho.qocthy", "`tchtod` double-energy volatile heat-fix; `otal/ytal/tal` structural terminals; `qocthy` transmute conduit bind active.", "Energy-pump the volatile into the matrix and land three structure markers in one line so the product acquires durable form.", "energy-pumped structural cascade", "strong"),
            ("P10", "y.ol.chy.kchey.kchor.dal", "`y.ol.chy` active fluid volatile; `kchey` body-volatile essence; `kchor` body-volatile outlet; `dal` fixed structure.", "Close by making the active volatile body exit only as a structurally fixed product.", "structural terminal close", "strong"),
        ],
        tarot_cards=["The Magician", "Temperance", "The Chariot", "The Moon", "Justice", "Strength", "The Emperor", "The Star", "The Tower", "The World"],
        movements=["open the retort extract", "draw off contained fluid", "bind extraction to conduit", "preserve damaged dissolve", "seal phase one", "ignite the building phase", "double-contain the matrix", "thicken the moist structure", "pump energy into form", "close on structure"],
        direct="`f13v` is a retort-to-structure page. The first phase extracts an aromatic volatile; the second builds that capture into a stable structured body, like a salve, wax, syrup, or thickened medicinal matrix.",
        math="Across the formal lenses, `f13v` is a phase-transition system with a clear regime switch at `qoky.daiin=` and `foldaiin`. The first block emphasizes extraction transport, while the second block increases structural basis vectors until the terminal state is governed by `dal` rather than by free outlet.",
        mythic="Across the mythic lenses, `f13v` is the builder's answer to fragrance: first catch the breath of the flower, then teach it how to live in a body.",
        compression="Extract under retort, pivot with `foldaiin`, trap the volatile in `kokydaiin`, pile up structure markers, and close on `dal`.",
        typed_state_machine=r"""
\[\mathcal R_{f13v} = \{r_{\mathrm{extract}}, r_{\mathrm{sealbreak}}, r_{\mathrm{structure}}, r_{\mathrm{matrixclose}}\}\]
\[\delta(e_{\mathrm{qoky.daiin}}): r_{\mathrm{extract}} \to r_{\mathrm{sealbreak}}\]
\[\delta(e_{\mathrm{foldaiin}}): r_{\mathrm{sealbreak}} \to r_{\mathrm{structure}} \to r_{\mathrm{matrixclose}}\]
""",
        invariants=r"""
\[N_{\mathrm{qo}}(f13v)=7, \qquad N_{\mathrm{ot}}(f13v)=6, \qquad N_{\mathrm{daiin/dain}}(f13v)\ge 4\]
\[N_{\mathrm{foldaiin}}(f13v)=1, \qquad N_{\mathrm{kokydaiin}}(f13v)=1, \qquad N_{\mathrm{al/tal}}(f13v)\ge 5\]
""",
        theorem=r"""
\[\rho_* = (\Psi_{P2} \circ \Psi_{P1})(\rho_0)\]

The formal theorem of `f13v` is:

1. the page is explicitly biphasic: extraction first, structural building second
2. `foldaiin` is the fire-mediated regime switch into the building phase
3. `kokydaiin` and the `-al/-tal` cluster prove that containment is being converted into form
4. the correct close is `dal`, meaning the product is valuable only once structure has been achieved
""",
        crystal_contribution=[
            "retort-to-structure transition station",
            "phase-seal pivot line",
            "double-containment matrix route",
            "energy-pumped structural cascade",
            "dal structural terminal",
        ],
        pointer_title="Retort Extraction into Structure",
        pointer_position="the verso of the fourth Quire B bifolio whose facing partner folio is lost",
        pointer_page_type="single-herb two-phase extraction-and-building page with strong structural terminal density",
        pointer_conclusion="`qoky.daiin=`, `foldaiin`, `kokydaiin`, `tchtod`, and final `dal`",
        pointer_judgment="`f13v` catches an aromatic extract and then forces it into durable form. The second half is not an afterthought - it is the point of the page.",
    ),
]


def main() -> None:
    for folio in FOLIOS:
        (FOLIOS_DIR / f"{folio['folio_id']}_FINAL_DRAFT.md").write_text(render_folio(folio), encoding="utf-8")
        (FOLIOS_DIR / f"{folio['folio_id']}.md").write_text(render_pointer(folio), encoding="utf-8")


if __name__ == "__main__":
    main()
