from __future__ import annotations

from render_f007_to_f008_parallel_batch import FOLIOS_DIR, render_folio, render_pointer
from render_f009_to_f010_parallel_batch import make_folio


TAROT_RING = [
    "The Magician",
    "The High Priestess",
    "The Empress",
    "The Emperor",
    "The Hierophant",
    "The Lovers",
    "The Chariot",
    "Strength",
    "The Hermit",
    "Wheel of Fortune",
    "Justice",
    "The Hanged Man",
    "Temperance",
    "The Devil",
    "The Tower",
    "The Star",
    "The Moon",
    "The Sun",
    "Judgment",
    "The World",
]


def tarot_for(count: int) -> list[str]:
    return [TAROT_RING[idx % len(TAROT_RING)] for idx in range(count)]


FOLIOS: list[dict[str, object]] = []


FOLIOS.extend(
    [
        make_folio(
            folio_id="F024R",
            quire="C",
            bifolio="bC1 = f17 + f24",
            manuscript_role="seven-essence cucumber-water combination formulary with convergent line architecture",
            purpose="`f24r` is the longest and most combinatorial outer-bifolio answer in Quire C so far. The page stacks seven triple-essence-class tokens and seven union-class events across nineteen body lines plus a title, then visibly shortens toward the end as if the process were being boiled down into a tighter admissible body. The cucumber identification matters less than the process profile: this is a high-load combination page where volatile, fluid, root, and salt are repeatedly brought together inside a cooling vehicle until the title names a salted vessel-active finish.",
            zero_claim="Carry a cucumber-water vehicle through seven essence-bearing turns and seven unions, keep the convergent corridor bound as the lines shorten, and finish as a salted vessel-active compound rather than a loose aggregation.",
            botanical="`Cucumis sativus` / cucumber remains the strongest local candidate because the page behaves like a cooling carrier or water-bearing vehicle for a seven-essence combination",
            risk="moderate",
            confidence="high on seven-essence combination logic and salted vessel-active closure, medium on species certainty",
            visual_grammar=[
                "`20 visible units including title` = unusually extended combinatory page for early Book I",
                "`7 triple-essence-class forms` = the page is built around repeated essence loading rather than one climax",
                "`7 union events` = conjunction is a governing law, not an afterthought",
                "`shortening final lines` = the route visibly contracts into a tighter admissible finish",
            ],
            full_eva="""
P1: por.or.y.chor.opchar.shecheol.daiin.or-
P2: qotaiin.eear.odaiin.okai*al.oky-
P3: ycthar.cthal.okol.qotar.ckhy-
P4: or.chckhal.cthar.eeor.chees.dy-
P5: qodar.cho.r.chey.cthy.cthe.keom-
P6: oeeeos.cthor.otal.qocthol.qoky-
P7: q*kar.chtar.s.cheor.cthol.qodol-
P8: eor.s.om.qoear.daiin.qokeol-
P9: odaiin.ckham.qoda**y.dol.dal-
P10: q*ar.cfhar.chor.s.am.chotaiin.dy-
P11: sar.cheoeees.okeom.cheor.qokain-
P12: qokchy.qotchy.tol.tod.ckhy-
P13: oees.ol.s.chein.chcth.sar-
P14: qor.cheey.qod.chor.cthal-
P15: ockhoees.oeees.ol.dal.s-
P16: sham.okeal.dal.dam.dal-
P17: sshey.otam.sham.cthoj.oky-
P18: ycheol.chol.daiin.chol.s-
P19: yol.kol.chol.shom.otacphy=
T20: sam.chorly=
""",
            core_vml=[
                "`eear`, `eeor`, `oeeeos`, `cheoeees`, `oees`, `ockhoees`, `oeees` = the seven essence-bearing signatures",
                "`ckham`, `am`, `sham`, `dam`, `otam`, and title `sam` = the union field appears seven times across the folio",
                "`cfhar` = fire applied at the root only after the combination corridor is already active",
                "`okeom` and `keom` = the page repeatedly cares about vessel-bearing finish, not only extraction",
                "`sam.chorly` = the title names a salted union inside an active volatile vessel corridor",
            ],
            groups=[
                {"label": "P1", "title": "Paragraph 1 - opening circulation and first essence threshold", "line_ids": ["P1", "P2", "P3", "P4", "P5"]},
                {"label": "P2", "title": "Paragraph 2 - expanded essence loading and first major unions", "line_ids": ["P6", "P7", "P8", "P9", "P10", "P11"]},
                {"label": "P3", "title": "Paragraph 3 - contraction toward structural and salt-bearing close", "line_ids": ["P12", "P13", "P14", "P15", "P16", "P17", "P18", "P19", "T20"]},
            ],
            lines=[
                ("P1", "por.or.y.chor.opchar.shecheol.daiin.or", "`por/or` press and outlet rotation; `opchar` heated-source opening; `shecheol` transition-volatile-fluid; `daiin` checkpoint.", "Open by circulating pressed source through outlet and heated volatile fluid, then immediately certify the route.", "circulating carrier opener", "strong"),
                ("P2", "qotaiin.eear.odaiin.okai*al.oky", "`qotaiin` transmuted completion; `eear` double-essence root; `odaiin`; damaged `okai*al`; `oky` contained active.", "The first clear essence surge is still bracketed by completion and containment rather than left free.", "first essence surge under containment", "mixed"),
                ("P3", "ycthar.cthal.okol.qotar.ckhy", "`ycthar` moist conduit-root; `cthal` conduit structure; `okol`; `qotar`; `ckhy` valve-active.", "Move the newly loaded essence through conduit and structure until valve control is explicit.", "conduit-structure with valve control", "strong"),
                ("P4", "or.chckhal.cthar.eeor.chees.dy", "`chckhal` volatile valve-structure; `cthar` conduit-root; `eeor` double-essence outlet; `chees` triple-essence volatile; `dy` fix.", "The page stacks outlet, structure, and essence again, but it lands in fixation rather than expansion.", "fixed essence-structure knot", "strong"),
                ("P5", "qodar.cho.r.chey.cthy.cthe.keom", "`qodar` transmuted root-fix; `chey` volatile essence active; `cthy/cthe` conduit bind and conduit essence; `keom` body-vessel.", "End the opening paragraph by shifting from loaded essence to vessel-bearing conduit law.", "vessel-bearing conduit seal", "strong"),
                ("P6", "oeeeos.cthor.otal.qocthol.qoky", "`oeeeos` triple-essence active fluid; `cthor`; `otal`; `qocthol`; `qoky` extracted contained active.", "The second paragraph begins with the page's strongest fluid-essence loading and immediately reinscribes it inside conduit and extraction control.", "major fluid-essence threshold", "strong"),
                ("P7", "q*kar.chtar.s.cheor.cthol.qodol", "damaged `q*kar`; `chtar` volatile root; `s`; `cheor` volatile-essence outlet; `cthol`; `qodol` transmuted fixed fluid.", "Even where the witness is damaged, the corridor still reads as root, essence outlet, conduit fluid, and fixed fluid.", "damaged but stable combinatory line", "mixed"),
                ("P8", "eor.s.om.qoear.daiin.qokeol", "`eor` essence outlet; `s`; standalone `om` vessel; `qoear` transmuted double-essence root; `daiin`; `qokeol` extracted contained essence-fluid.", "The page pulls the combination directly into vessel reference before reopening transmuted essence-fluid carriage.", "vessel midpoint with essence-fluid return", "strong"),
                ("P9", "odaiin.ckham.qoda**y.dol.dal", "`odaiin`; `ckham` valve-union; damaged `qoda**y`; `dol`; `dal`.", "The first major union in the folio is immediately pressed into double structural fixation.", "union driven into structure", "mixed"),
                ("P10", "q*ar.cfhar.chor.s.am.chotaiin.dy", "damaged `q*ar`; `cfhar` fire-root seal; `chor`; `s`; `am`; `chotaiin`; `dy`.", "Fire is admitted here as rooted seal, but only inside an already union-bearing and completed corridor.", "root-fire union threshold", "mixed"),
                ("P11", "sar.cheoeees.okeom.cheor.qokain", "`sar` salt-root; `cheoeees` triple-essence volatile body; `okeom` contained body-vessel; `cheor`; `qokain` extracted contained completion.", "This line states the core law plainly: salt, loaded essence body, and vessel completion belong together.", "salted vessel-essence theorem", "strong"),
                ("P12", "qokchy.qotchy.tol.tod.ckhy", "`qokchy/qotchy` extracted and transmuted active states; `tol/tod` driven fluid and fixed fluid; `ckhy` valve-active.", "As the page contracts, it compresses whole operations into short active-fluid and valve terms.", "compressed active-fluid control", "strong"),
                ("P13", "oees.ol.s.chein.chcth.sar", "`oees` essence-active; `ol`; `s`; `chein` volatile cycle complete; `chcth` volatile conduit; `sar` salt-root.", "The contraction phase keeps essence, fluid, conduit, and salt all present at once.", "essence-fluid-salt contraction", "strong"),
                ("P14", "qor.cheey.qod.chor.cthal", "`qor` transmuted outlet; `cheey` double-essence active; `qod`; `chor`; `cthal`.", "A short line still carries transmuted outlet, double essence, and final conduit structure.", "short structural essence pass", "strong"),
                ("P15", "ockhoees.oeees.ol.dal.s", "`ockhoees` contained valve triple-essence active; `oeees` triple-essence active; `ol`; `dal`; `s`.", "This is the tightest concentration line: doubled essence-load inside containment, then immediate structure and salt.", "tightest concentration knot", "strong"),
                ("P16", "sham.okeal.dal.dam.dal", "`sham` transition-union; `okeal` contained essence structure; `dal`; `dam`; `dal`.", "The page now alternates union and structure as if fusion itself must be repeatedly nailed down.", "union-structure hammer line", "strong"),
                ("P17", "sshey.otam.sham.cthoj.oky", "`sshey` intensified transition-essence active; `otam`; `sham`; `cthoj`; `oky`.", "Two unions appear in one short line, but the close still lands in contained activity.", "double-union active seal", "mixed"),
                ("P18", "ycheol.chol.daiin.chol.s", "`ycheol` moist volatile-fluid; `chol`; `daiin`; `chol`; `s`.", "The line contracts almost to pure fluid-volatile rhythm plus one checkpoint and salt.", "minimal fluid checkpoint line", "strong"),
                ("P19", "yol.kol.chol.shom.otacphy", "`yol/kol/chol` moist, contained, and ordinary fluid-volatiles; `shom` transition vessel; `otacphy` heated alembic-active.", "The last body line pulls the combination into vessel and alembic grammar before the title seals it.", "vessel-alembic pre-title close", "strong"),
                ("T20", "sam.chorly", "`sam` salted union; `chorly` volatile outlet active-fluid.", "Name the product as a salted union borne in active volatile fluid.", "salted vessel-active title", "strong"),
            ],
            tarot_cards=tarot_for(20),
            movements=[
                "open the cooling carrier route",
                "load first rooted essence",
                "bind through conduit and valve",
                "fix essence inside structure",
                "set the vessel-bearing conduit",
                "raise the fluid-essence threshold",
                "keep damaged witness inside law",
                "return essence to vessel",
                "drive first union into structure",
                "admit rooted fire inside union",
                "salt the vessel essence",
                "compress into active-fluid control",
                "contract toward salt and conduit",
                "shorten into structured essence",
                "tighten the concentration knot",
                "hammer union into structure",
                "seal double union in containment",
                "thin the route to fluid rhythm",
                "prepare the alembic finish",
                "name the salted union product",
            ],
            direct="`f24r` is a seven-essence combination formulary. Its deepest law is not abundance for its own sake, but lawful convergence: repeated essence loads and repeated unions are gradually tightened into a salted vessel-active close.",
            math="Across the formal lenses, `f24r` behaves like a many-input convergence manifold. Essence density and union count are both high, but the attractor is compressive: the route shortens, structure hardens, and the final state is a bounded salted vessel-fluid rather than unconstrained growth.",
            mythic="Across the mythic lenses, `f24r` is the great banquet reduced to one cup. Many guests enter; only one lawful tincture leaves.",
            compression="Load the cooling carrier with seven essence-bearing turns and seven unions, contract the route under structure and vessel law, and seal it as a salted volatile-fluid compound.",
            typed_state_machine=r"""
\[\mathcal R_{f24r} = \{r_{\mathrm{carrier}}, r_{\mathrm{essence\ load}}, r_{\mathrm{union}}, r_{\mathrm{contraction}}, r_{\mathrm{title}}\}\]
\[\delta(e_{\mathrm{oeeeos}}): r_{\mathrm{carrier}} \to r_{\mathrm{essence\ load}}\]
\[\delta(e_{\mathrm{ckham/am/sham/dam/otam/sam}}): r_{\mathrm{essence\ load}} \to r_{\mathrm{union}} \to r_{\mathrm{contraction}}\]
\[\delta(e_{\mathrm{T20}}): r_{\mathrm{contraction}} \to r_{\mathrm{title}}\]
""",
            invariants=r"""
\[N_{\mathrm{triple\text{-}essence\ class}}(f24r)=7, \qquad N_{\mathrm{union\ class}}(f24r)=7, \qquad N_{\mathrm{visible\ units}}(f24r)=20\]
\[N_{\mathrm{fire\ root\ seal}}(f24r)=1, \qquad N_{\mathrm{vessel\ forms}}(f24r)\ge 4, \qquad N_{\mathrm{contraction\ phase}}(f24r)=1\]
""",
            theorem=r"""
\[\rho_* = (\Psi_{P3} \circ \Psi_{P2} \circ \Psi_{P1})(\rho_0)\]

The formal theorem of `f24r` is:

1. the folio is governed by repeated essence loading and repeated union rather than by a single terminal spike
2. the route stays lawful because union is repeatedly pushed into structure and vessel grammar
3. `cfhar` appears only after the combinatory corridor is already active, so fire remains subordinate to the larger mixture law
4. the title `sam.chorly` proves that the attractor is a salted volatile-fluid product, not an endless aggregation
""",
            crystal_contribution=[
                "seven-essence combination station",
                "cooling-carrier convergence line",
                "root-fire union threshold",
                "union-structure contraction corridor",
                "salted vessel-active title close",
            ],
            pointer_title="Seven-Essence Cucumber-Water Combination Formulary",
            pointer_position="the recto of the `f17/f24` outer bifolio and late outer answer to Quire C's open-vessel start",
            pointer_page_type="long combination page with seven essence-class tokens, seven union events, and a title line",
            pointer_conclusion="`eear`, `eeor`, `oeeeos`, `cheoeees`, `oees`, `ockhoees`, `oeees`, plus `ckham`, `am`, `sham`, `dam`, `otam`, and title `sam.chorly`",
            pointer_judgment="`f24r` is Quire C's first true seven-load combination leaf. The page teaches convergence: repeated essence and repeated union are only admissible if they can be tightened into a salted vessel-active finish.",
        ),
        make_folio(
            folio_id="F024V",
            quire="C",
            bifolio="bC1 = f17 + f24",
            manuscript_role="deeply integrated fire-seal compound-processing page closing Quire C",
            purpose="`f24v` closes Quire C by pushing compound processing into deep integration instead of open expansion. The opener `chocfhey` embeds fire seal inside the volatile body immediately, later `foar` applies fire to the root again, `cheeodam` compresses compound plus union into one token, and the last line seals the page with vessel-completion variant `odaiim`. The page reads like the quire-closing proof that complex medicine can be internally fused rather than merely combined stepwise.",
            zero_claim="Embed fire seal deep inside the compound body, keep the route lawful through repeated contained transitions and late triple-essence loading, compress union into the medicine itself, and finish the quire in a completed vessel state.",
            botanical="`Pueraria lobata` / kudzu remains the local candidate, though the page's stronger identity is as a deep compound-integration procedure",
            risk="moderate",
            confidence="high on deep fire-seal integration and quire-closing vessel completion",
            visual_grammar=[
                "`final page of Quire C` = the folio behaves like a technical closer rather than a fresh opener",
                "`damage at P3 and P5` = the damaged witness must remain visible inside the compound logic",
                "``chocfhey` and `foar`` = fire appears both embedded in volatile body and later on the root",
                "`terminal `odaiim`` = completion is quire-closing vessel law, not an optional extra",
            ],
            full_eva="""
P1: tchodar.chocfhey.opod.shod.chcphy.opshody.oporaiin.ok.okam-
P2: yd**s.ckhor.shy.cho.dchor.otol.otaiir.otchos.okchom.okcho-
P3: ****.dchees.osear.ear.okam.chcth-
P4: yd.al.sh.okol.okaiin.odaiin.dlor-
P5: **r.oraiin.tchar.oro=
P6: tochol.shor.*ar.*r-
P7: ycheol.daid.dar.olom-
P8: kochky.chcthy.shol.sain-
P9: y.chol.chol.or.chor.om-
P10: okoeor.ctheod.choy.keol-
P11: ydaiin.cheor.qodom.okodaiin=
P12: ksho.foar.*to.sho.qok*.ok.okchal-
P13: oeeey.cheol.chol.odor.sho.do.ot.olodal-
P14: doar.cheeodam.sho.sho.dy-
P15: dchey.kchod.dchal.ochdy-
P16: otchol.odaiim=
""",
            core_vml=[
                "`chocfhey` = deeply embedded fire seal in the opening line",
                "`foar` = fire applied to the root in the late correction corridor",
                "`oeeey` = triple-essence active body appears only after the route is already heavily integrated",
                "`cheeodam` = compressed compound-union theorem token near the close",
                "`odaiim` = vessel-completion variant marking quire closure",
            ],
            groups=[
                {"label": "P1", "title": "Paragraph 1 - embedded fire-seal opener and damaged compound witness", "line_ids": ["P1", "P2", "P3", "P4", "P5"]},
                {"label": "P2", "title": "Paragraph 2 - restart, vessel carrying, and root-fire correction", "line_ids": ["P6", "P7", "P8", "P9", "P10", "P11", "P12"]},
                {"label": "P3", "title": "Paragraph 3 - late triple essence, compressed union, and vessel-completion close", "line_ids": ["P13", "P14", "P15", "P16"]},
            ],
            lines=[
                ("P1", "tchodar.chocfhey.opod.shod.chcphy.opshody.oporaiin.ok.okam", "`tchodar` driven volatile-root; `chocfhey` volatile-fire-seal essence active; `opod/shod` opened and transitioned fixatives; `chcphy` volatile alembic-active; `okam` contained union-vessel.", "Open by embedding the fire seal directly in the volatile body, but land the line inside alembic and vessel-union grammar.", "deep fire-seal opener", "strong"),
                ("P2", "yd**s.ckhor.shy.cho.dchor.otol.otaiir.otchos.okchom.okcho", "damaged moist opener; `ckhor` valve-outlet; `dchor` fixed outlet; `otol/otaiir/otchos` heated fluid and completed volatile cycles; `okchom/okcho` contained vessel-body volatile.", "The second line proves that the opening fire seal is not free burn; it immediately falls into outlet, fluid, and vessel control.", "outlet-vessel containment after fire", "mixed"),
                ("P3", "****.dchees.osear.ear.okam.chcth", "damaged initial cluster; `dchees` fixed triple-essence volatile; `osear/ear` heated and plain double-essence roots; `okam`; `chcth` volatile conduit.", "Even through heavy damage, the line still witnesses triple essence driven back into root and conduit under contained union.", "damaged triple-essence witness", "mixed"),
                ("P4", "yd.al.sh.okol.okaiin.odaiin.dlor", "`yd.al` moist fix-structure; `sh`; `okol`; `okaiin`; `odaiin`; `dlor` fixed fluid-outlet root.", "After the damaged threshold, the page hardens into containment and root-outlet fixation.", "hardening after damage", "strong"),
                ("P5", "**r.oraiin.tchar.oro", "damaged opener; `oraiin` heated-outlet completion; `tchar` driven volatile-root; `oro` outlet rotation.", "The fifth line is brief and damaged, but it still keeps the compound tethered to root and outlet cycling.", "brief damaged root-outlet bridge", "mixed"),
                ("P6", "tochol.shor.*ar.*r", "`tochol` driven volatile fluid; `shor`; damaged root tokens follow.", "Restart the second paragraph as a reduced but still volatile-fluid corridor.", "reduced restart line", "mixed"),
                ("P7", "ycheol.daid.dar.olom", "`ycheol` moist volatile-fluid; `daid` fixed energized completion; `dar`; `olom` fluid vessel.", "The route now becomes more vessel-bearing and less explosive.", "vessel-bearing recovery", "strong"),
                ("P8", "kochky.chcthy.shol.sain", "`kochky` body-contained active volatile; `chcthy` volatile conduit bind; `shol`; `sain` salt completion.", "Re-anchor the living compound in body and conduit, then certify it with salt completion.", "body-conduit salt checkpoint", "strong"),
                ("P9", "y.chol.chol.or.chor.om", "`y.chol.chol` moist doubled volatile fluid; `or/chor` outlet pair; `om` vessel.", "This line compresses the medicine into doubled fluid plus outlet and vessel, as if preparing for final internal integration.", "doubled-fluid vessel corridor", "strong"),
                ("P10", "okoeor.ctheod.choy.keol", "`okoeor` contained double-essence outlet; `ctheod` conduit-essence fix; `choy` volatile heated active; `keol` body-essence fluid.", "Essence, conduit, and body-fluid are now fully interleaved.", "interleaved essence-body line", "strong"),
                ("P11", "ydaiin.cheor.qodom.okodaiin", "`ydaiin` moist completion; `cheor`; `qodom` transmuted fixed vessel; `okodaiin` contained heated completion.", "The eleventh line explicitly proves vessel fixation before the final fire correction appears.", "vessel-proof line", "strong"),
                ("P12", "ksho.foar.*to.sho.qok*.ok.okchal", "`ksho` body-transition heat; `foar` fire-root; damaged middle cluster; `sho`; `qok*`; `ok`; `okchal` contained heated structure.", "Late fire returns only at the root, and even then the line ends in contained structure.", "late root-fire correction", "mixed"),
                ("P13", "oeeey.cheol.chol.odor.sho.do.ot.olodal", "`oeeey` triple-essence active body; `cheol/chol` volatile fluid pair; `odor` heated fixed outlet; `sho/do/ot`; `olodal` fluid-fixed structure.", "Triple essence arrives late and is immediately forced into fixed fluid-structure.", "late triple-essence integration", "strong"),
                ("P14", "doar.cheeodam.sho.sho.dy", "`doar` fixed heated root; `cheeodam` compressed volatile-double-essence-union; doubled `sho`; `dy`.", "This is the quire-closing theorem line: the compound and union are now compressed into the medicine itself.", "compressed union theorem", "strong"),
                ("P15", "dchey.kchod.dchal.ochdy", "`dchey` fixed volatile essence active; `kchod` body-volatile fix; `dchal` fixed structure; `ochdy` heated volatile-fix active.", "The penultimate line locks the integrated compound across body, structure, and active fixation.", "integrated penultimate lock", "strong"),
                ("P16", "otchol.odaiim", "`otchol` heated volatile fluid; `odaiim` completed vessel state.", "Close Quire C by declaring the volatile fluid admissible only as a completed vessel body.", "quire-closing vessel completion", "strong"),
            ],
            tarot_cards=tarot_for(16),
            movements=[
                "embed the fire seal",
                "fall into vessel control",
                "preserve the damaged essence witness",
                "harden the route",
                "bridge root and outlet",
                "restart in reduced form",
                "return to vessel bearing",
                "salt the body-conduit route",
                "double the fluid inside vessel",
                "interleave body and essence",
                "prove the vessel before correction",
                "apply late root-fire correction",
                "force triple essence into structure",
                "compress union into the medicine",
                "lock the compound body",
                "close in completed vessel state",
            ],
            direct="`f24v` is Quire C's deep integration closer. Instead of more open accumulation, it teaches how fire-sealed compound medicine is fused inward until union, structure, and vessel completion become one route.",
            math="Across the formal lenses, `f24v` behaves like a deep-integration operator chain. The fire term is internal from the start, damaged witnesses are absorbed without losing state coherence, and the attractor is a vessel-complete compound with compressed union near the close.",
            mythic="Across the mythic lenses, `f24v` is the inward wedding. What was mixture on the recto becomes marriage inside the body of the medicine.",
            compression="Embed fire in the volatile body, carry the compound through damaged but lawful containment, apply one late root-fire correction, compress union into the medicine itself, and close as a completed vessel state.",
            typed_state_machine=r"""
\[\mathcal R_{f24v} = \{r_{\mathrm{embed}}, r_{\mathrm{contain}}, r_{\mathrm{repair}}, r_{\mathrm{compress\ union}}, r_{\mathrm{vesselclose}}\}\]
\[\delta(e_{\mathrm{chocfhey}}): r_{\mathrm{embed}} \to r_{\mathrm{contain}}\]
\[\delta(e_{\mathrm{foar}}): r_{\mathrm{repair}} \to r_{\mathrm{compress\ union}}\]
\[\delta(e_{\mathrm{cheeodam}}): r_{\mathrm{compress\ union}} \to r_{\mathrm{vesselclose}}\]
""",
            invariants=r"""
\[N_{\mathrm{damage\ lines}}(f24v)=3, \qquad N_{\mathrm{fire\ terms}}(f24v)\ge 2, \qquad N_{\mathrm{vessel\ terms}}(f24v)\ge 5\]
\[N_{\mathrm{triple\text{-}essence\ class}}(f24v)=2, \qquad N_{\mathrm{compressed\ union}}(f24v)=1, \qquad N_{\mathrm{terminal\ odaiim}}(f24v)=1\]
""",
            theorem=r"""
\[\rho_* = (\Psi_{P3} \circ \Psi_{P2} \circ \Psi_{P1})(\rho_0)\]

The formal theorem of `f24v` is:

1. fire is embedded at the opening rather than introduced from outside later
2. damaged witness matter does not erase the route, because vessel and conduit grammar remain visible
3. late fire correction at the root is subordinate to deeper integration, not a reset of the page
4. `cheeodam` and `odaiim` prove that the quire closes by compressing union into a completed vessel body
""",
            crystal_contribution=[
                "deep fire-seal integration station",
                "damaged compound witness line",
                "late root-fire correction threshold",
                "compressed union theorem corridor",
                "quire-closing vessel-completion seal",
            ],
            pointer_title="Deep Fire-Seal Compound Integration",
            pointer_position="the verso of the `f17/f24` outer bifolio and closing page of Quire C",
            pointer_page_type="compound-processing quire closer with embedded fire seal, damaged witness retention, and terminal vessel completion",
            pointer_conclusion="`chocfhey`, `foar`, `oeeey`, `cheeodam`, and terminal `odaiim`",
            pointer_judgment="`f24v` closes Quire C by folding fire, union, and structure inward. The page is not merely mixed; it is fused into vessel-complete medicine.",
        ),
    ]
)


FOLIOS.extend(
    [
        make_folio(
            folio_id="F027R",
            quire="D",
            bifolio="bD3 = f27 + f30",
            manuscript_role="two-stage union procedure with source-level fire in Currier B",
            purpose="`f27r` is comparatively short, but it places one fire-at-source token `chforaiin` at the opening, then divides its work across two explicit union events: `dam` in the first paragraph and `cham` in the second. The page feels like a two-stage marriage procedure: source-level ignition, first conjunction, second conjunction, and title-line naming. Currier B here is no longer mostly about standardization; it is using its shorter tokens to articulate exact stages of union.",
            zero_claim="Apply fire at the source, move the matter through one first-stage union and one second-stage union, and close the process as a named body-volatile product rather than as unresolved source matter.",
            botanical="`Spinacia oleracea` / spinach remains the local candidate, though the page's clearer identity is as a two-stage union procedure",
            risk="moderate",
            confidence="high on source-level fire and doubled-union staging, medium on species fit",
            visual_grammar=[
                "`short Currier B leaf` = the page relies on stage precision rather than line abundance",
                "`chforaiin` in P1` = fire is applied at the volatile source immediately",
                "`dam` and `cham` = one union marker in each paragraph",
                "`title `otchodeey`` = the finished product is named in standard B-language style",
            ],
            full_eva="""
P1: ksor.shey.shoteo.chforaiin.shy-shod.chary-
P2: dy.chain.shol.dain.dar.shokyd-dchol.cthey.ds-
P3: chok.shy.keol.chol.chy.shol.chy-daiin.chey.dam-
P4: qokey.chor.char.chy.dchy.keey-chos.cthody-
P5: dor.chees.ctho.shy.cphary-daiin.dair-
P6: chy.tchols.chor.chol.chaiin-shy.kchal.dy=
P7: kchoy.chey.kcheol.pcho.schey.ly-chals.cham-
P8: ytchy.chy.tchol.dy.tchey.dain-chol.dal-
P9: dchey.keeod.shotchey.chol.oty-chytolcth-
P10: qotchey.shes.sy.chy.tchey.dy-
P12a: dain.cheokeey.chey.cthey.otal=
T13: otchodeey=
""",
            core_vml=[
                "`chforaiin` = fire at volatile source in the opener",
                "`dam` and `cham` = two distinct union checkpoints, one per paragraph",
                "`keeod` = double-essence body extraction in the late corridor",
                "`short B tokens` = precision staging through concise morphology",
                "`otchodeey` = standard named product close after the two-stage union process",
            ],
            groups=[
                {"label": "P1", "title": "Paragraph 1 - source fire and first union", "line_ids": ["P1", "P2", "P3", "P4", "P5", "P6"]},
                {"label": "P2", "title": "Paragraph 2 - second union and named product close", "line_ids": ["P7", "P8", "P9", "P10", "P12a", "T13"]},
            ],
            lines=[
                ("P1", "ksor.shey.shoteo.chforaiin.shy-shod.chary", "`ksor` contained salt-outlet; `shey`; `shoteo`; `chforaiin` fire-at-source completion; `shy-shod`; `chary` volatile-root active.", "Open by igniting the source directly, but keep the route rooted and transition-bound.", "source-fire opener", "strong"),
                ("P2", "dy.chain.shol.dain.dar.shokyd-dchol.cthey.ds", "`dy`; `chain`; `shol`; `dain`; `dar`; `shokyd-dchol`; `cthey`; `ds`.", "The second line moves immediately from source fire into completion, root fixation, and conduit essence.", "rooted completion after source fire", "mixed"),
                ("P3", "chok.shy.keol.chol.chy.shol.chy-daiin.chey.dam", "`chok`; `shy`; `keol`; `chol/chy/shol/chy`; `daiin`; `chey`; `dam`.", "The first union appears only after the volatile body has already been carried through fluid and completion.", "first union line", "strong"),
                ("P4", "qokey.chor.char.chy.dchy.keey-chos.cthody", "`qokey`; `chor/char`; `chy`; `dchy`; `keey-chos`; `cthody`.", "After the first union, the page reworks the body through outlet, root, and conduit-fix grammar.", "post-union reworking", "strong"),
                ("P5", "dor.chees.ctho.shy.cphary-daiin.dair", "`dor`; `chees`; `ctho`; `shy`; `cphary`; `daiin`; `dair`.", "Triple essence is allowed in the first paragraph, but only under conduit and timed fixation.", "timed triple-essence seal", "strong"),
                ("P6", "chy.tchols.chor.chol.chaiin-shy.kchal.dy", "`chy`; `tchols`; `chor/chol`; `chaiin-shy`; `kchal`; `dy`.", "Seal the first paragraph by returning body and outlet to structure-fix law.", "first-stage structural seal", "strong"),
                ("P7", "kchoy.chey.kcheol.pcho.schey.ly-chals.cham", "`kchoy` body-volatile active; `chey`; `kcheol`; `pcho`; `schey`; `ly-chals`; `cham`.", "The second paragraph opens the second union stage directly in the body-volatile register.", "second union opener", "strong"),
                ("P8", "ytchy.chy.tchol.dy.tchey.dain-chol.dal", "`ytchy/chy`; `tchol`; `dy`; `tchey`; `dain-chol`; `dal`.", "After the second union, the route is immediately fixed back into fluid and structure.", "post-second-union fixation", "strong"),
                ("P9", "dchey.keeod.shotchey.chol.oty-chytolcth", "`dchey`; `keeod` double-essence body extraction; `shotchey`; `chol`; `oty-chytolcth` heated active conduit-fluid cluster.", "This line gives the page's late reward: a double-essence body form after the second union is already secured.", "late double-essence reward", "strong"),
                ("P10", "qotchey.shes.sy.chy.tchey.dy", "`qotchey`; `shes`; `sy`; `chy`; `tchey`; `dy`.", "Compress the late corridor into active transition essence and one final fixation.", "compressed late corridor", "strong"),
                ("P12a", "dain.cheokeey.chey.cthey.otal", "`dain`; `cheokeey` contained double-essence active; `chey`; `cthey`; `otal`.", "The penultimate line turns the medicine into a contained double-essence conduit-fluid close.", "contained double-essence close", "strong"),
                ("T13", "otchodeey", "`otchodeey` heated volatile-fix double-essence active named product.", "Name the result as a standard B-language product after the two unions are complete.", "named product title", "strong"),
            ],
            tarot_cards=tarot_for(12),
            movements=[
                "ignite the source",
                "root the fire under completion",
                "enter the first union",
                "rework the joined body",
                "seal timed triple essence",
                "fix the first stage structurally",
                "open the second union",
                "fix the second stage",
                "release late double essence",
                "compress the final corridor",
                "contain the double essence",
                "name the product",
            ],
            direct="`f27r` is a two-stage union leaf. Fire is applied at the source, the route marries once in the first paragraph and once in the second, and only then does the page name the product.",
            math="Across the formal lenses, `f27r` behaves like a staged conjunction map. One source-fire perturbation initiates the route, and two separate union events partition the page into clear procedural phases before the attractor collapses into named product form.",
            mythic="Across the mythic lenses, `f27r` is the two-vow marriage page. The first vow joins the matter; the second vow makes it durable enough to be named.",
            compression="Ignite the source, secure a first union, rework the joined body, secure a second union, and close as a named double-essence volatile product.",
            typed_state_machine=r"""
\[\mathcal R_{f27r} = \{r_{\mathrm{sourcefire}}, r_{\mathrm{first\ union}}, r_{\mathrm{second\ union}}, r_{\mathrm{product}}\}\]
\[\delta(e_{\mathrm{chforaiin}}): r_{\mathrm{sourcefire}} \to r_{\mathrm{first\ union}}\]
\[\delta(e_{\mathrm{dam}}): r_{\mathrm{first\ union}} \to r_{\mathrm{second\ union}}\]
\[\delta(e_{\mathrm{cham}}): r_{\mathrm{second\ union}} \to r_{\mathrm{product}}\]
""",
            invariants=r"""
\[N_{\mathrm{union}}(f27r)=2, \qquad N_{\mathrm{fire\ at\ source}}(f27r)=1, \qquad N_{\mathrm{title}}(f27r)=1\]
\[N_{\mathrm{double\text{-}essence\ body\ forms}}(f27r)\ge 2, \qquad N_{\mathrm{paragraphs}}(f27r)=2, \qquad N_{\mathrm{visible\ units}}(f27r)=12\]
""",
            theorem=r"""
\[\rho_* = (\Psi_{P2} \circ \Psi_{P1})(\rho_0)\]

The formal theorem of `f27r` is:

1. fire is applied at the source only once, at the opening
2. the first paragraph culminates in `dam`, while the second culminates in `cham`, making the folio explicitly two-stage
3. late double-essence body extraction is allowed only after the second conjunction is secured
4. the title proves that the route ends as named product, not open source material
""",
            crystal_contribution=[
                "two-stage union station",
                "source-fire threshold line",
                "first-union corridor",
                "second-union body route",
                "named product close",
            ],
            pointer_title="Two-Stage Union with Source Fire",
            pointer_position="the recto of bifolio `f27/f30` and middle Currier B union-procedure page",
            pointer_page_type="short B-language page with one source-fire opener, two union markers, and a title line",
            pointer_conclusion="`chforaiin`, `dam`, `cham`, `keeod`, and title `otchodeey`",
            pointer_judgment="`f27r` is one of the clearest staged conjunction leaves in Book I. It teaches that not all unions are the same; some must occur in sequence.",
            currier_language="B",
            currier_hand="2",
        ),
        make_folio(
            folio_id="F027V",
            quire="D",
            bifolio="bD3 = f27 + f30",
            manuscript_role="continuous double-fire volatile-processing page with triple-root extraction and zero completion markers",
            purpose="`f27v` is the negative image of the orderly capstone pages around it. The folio opens with doubled fire-volatile forms `ochof.chof`, later preserves the unique `kchrrr` triple-root token, contains a full missing line at `P5`, and yet never uses ordinary completion markers. This is only the second page after `f17r` to suspend completion grammar so completely. The page reads like a continuously active volatile corridor that must be held live rather than repeatedly certified.",
            zero_claim="Sustain a double-fire volatile route without ordinary completion markers, preserve the damaged witness line instead of normalizing it away, pass through triple-root extraction, and finish as a still-active but lawfully bounded volatile process.",
            botanical="`Dianthus superbus` / pink remains the local candidate, though the operational signature is stronger: continuous double-fire volatile processing without completion grammar",
            risk="moderate",
            confidence="high on zero-completion law, doubled fire opener, and triple-root extraction; mixed on damaged middle recovery",
            visual_grammar=[
                "`ochof.chof` opener = doubled fire-volatile statement at the first line",
                "`missing P5` = the lacuna is a structural part of the witness",
                "`kchrrr` = unique triple-root extraction token",
                "`zero completion markers` = only the second such page in the current corpus after `f17r`",
            ],
            full_eva="""
P1: ochof.chof.cho.sho.sholy.shol.ytchail.opchory.kchor.chor-
P2: dchy.chkar.otchy.shy.shy.dchy.dshy.kchy.cheo.daijy.dchy-
P3: kchey.kchy.dchokchy.dsho.dchar.cho.dchy.etcheody.shl.d-
P4: okcho.chy.kchod.chl.chol.kod-o.oksho.do.chees.g-
P5: {missing line}-
P6: dsho.kchrrr.okeedy-dchrchy.shotchdy-
P7: sho.shoykcho.shdy-dchd.chschsy.otchdy-
P8: okshes.okcho.kshy=
""",
            core_vml=[
                "`ochof.chof` = doubled fire-volatile opener",
                "`zero completion markers` = the page stays live rather than repeatedly certified",
                "`kchrrr` = unique triple-root extraction signature in the damaged-late corridor",
                "`shy.shy` = doubled transition in P2",
                "`missing P5` = the lacuna must remain visible and untranslated as certainty",
            ],
            groups=[
                {"label": "P1", "title": "Paragraph 1 - doubled fire opener and live volatile corridor", "line_ids": ["P1", "P2", "P3", "P4"]},
                {"label": "P2", "title": "Paragraph 2 - lacuna preservation, triple-root extraction, and live close", "line_ids": ["P5", "P6", "P7", "P8"]},
            ],
            lines=[
                ("P1", "ochof.chof.cho.sho.sholy.shol.ytchail.opchory.kchor.chor", "`ochof/chof` doubled heated volatile-fire forms; `cho/sho/sholy/shol` volatile transition fluid stack; `ytchail`; `opchory`; `kchor/chor` body-outlet pair.", "Open with continuous fire already inside the volatile stream and keep the route live rather than completed.", "doubled fire-volatile opener", "strong"),
                ("P2", "dchy.chkar.otchy.shy.shy.dchy.dshy.kchy.cheo.daijy.dchy", "`dchy`; `chkar`; `otchy`; doubled `shy`; second `dchy`; `dshy`; `kchy`; `cheo`; `daijy`; terminal `dchy`.", "The doubled transition in the middle of the line shows the page prefers live oscillation to closure.", "doubled-transition live line", "strong"),
                ("P3", "kchey.kchy.dchokchy.dsho.dchar.cho.dchy.etcheody.shl.d", "`kchey/kchy` body and active volatile; `dchokchy`; `dsho`; `dchar`; `cho`; `dchy`; `etcheody`; `shl`; `d`.", "The corridor stays body-volatile and structurally active without ever invoking ordinary completion.", "body-volatile without completion", "mixed"),
                ("P4", "okcho.chy.kchod.chl.chol.kod-o.oksho.do.chees.g", "`okcho/chy`; `kchod`; `chl/chol`; `kod-o`; `oksho`; `do`; `chees`; terminal `g`.", "Even the triple-essence touch here remains embedded in a live volatile process, not a closed proof line.", "live triple-essence touch", "mixed"),
                ("P5", "{missing line}", "The fifth line is physically absent in the witness and must remain marked as such.", "Preserve the lacuna as evidence rather than inventing a completion-bearing bridge.", "lacuna preserved", "strong"),
                ("P6", "dsho.kchrrr.okeedy-dchrchy.shotchdy", "`dsho`; `kchrrr` triple-root body-volatile extraction; `okeedy-dchrchy`; `shotchdy`.", "After the lacuna, the page returns with its strongest root token, as if the missing matter fed directly into deeper extraction.", "triple-root extraction return", "strong"),
                ("P7", "sho.shoykcho.shdy-dchd.chschsy.otchdy", "`sho`; `shoykcho`; `shdy-dchd`; `chschsy`; `otchdy`.", "The penultimate line keeps transition, body-volatile action, and active fixation moving without closure language.", "live penultimate corridor", "mixed"),
                ("P8", "okshes.okcho.kshy", "`okshes` contained transition-essence active; `okcho`; `kshy` body-transition active.", "Close as a still-active bounded route, not as a fully completed product.", "active bounded close", "strong"),
            ],
            tarot_cards=tarot_for(8),
            movements=[
                "open with doubled fire",
                "keep the transition live",
                "hold body and volatile together",
                "touch triple essence without closure",
                "preserve the missing witness",
                "return through triple-root extraction",
                "continue the live corridor",
                "close while still active",
            ],
            direct="`f27v` is a live-process page. It refuses ordinary completion grammar, preserves a missing line, and still teaches how double-fire volatile work can remain bounded through body, root, and active structure.",
            math="Across the formal lenses, `f27v` behaves like an open-system control corridor. Completion projectors are suppressed, so stability is achieved through bounded activity, root recurrence, and live containment rather than through repeated terminal checkpoints.",
            mythic="Across the mythic lenses, `f27v` is the vigil page. The fire must be watched, not declared finished.",
            compression="Sustain the doubled-fire volatile route without normal completion markers, preserve the lacuna, return through triple-root extraction, and close as active but bounded process.",
            typed_state_machine=r"""
\[\mathcal R_{f27v} = \{r_{\mathrm{doublefire}}, r_{\mathrm{live\ corridor}}, r_{\mathrm{lacuna}}, r_{\mathrm{triple\ root}}, r_{\mathrm{active\ close}}\}\]
\[\delta(e_{\mathrm{ochof.chof}}): r_{\mathrm{doublefire}} \to r_{\mathrm{live\ corridor}}\]
\[\delta(e_{\mathrm{missing\ P5}}): r_{\mathrm{live\ corridor}} \to r_{\mathrm{lacuna}} \to r_{\mathrm{triple\ root}}\]
\[\delta(e_{\mathrm{kchrrr}}): r_{\mathrm{triple\ root}} \to r_{\mathrm{active\ close}}\]
""",
            invariants=r"""
\[N_{\mathrm{completion\ markers}}(f27v)=0, \qquad N_{\mathrm{fire\ opener}}(f27v)=2, \qquad N_{\mathrm{missing\ lines}}(f27v)=1\]
\[N_{\mathrm{triple\ root\ signatures}}(f27v)=1, \qquad N_{\mathrm{doubled\ transition}}(f27v)=1, \qquad N_{\mathrm{visible\ units}}(f27v)=8\]
""",
            theorem=r"""
\[\rho_* = (\Psi_{P2} \circ \Psi_{P1})(\rho_0)\]

The formal theorem of `f27v` is:

1. the page's defining law is the suspension of ordinary completion grammar
2. stability is maintained by bounded live activity, not by repeated certified closure
3. the lacuna is part of the operational witness and must remain visible in any honest translation
4. `kchrrr` marks the decisive recovery operator: triple-root extraction after the missing middle
""",
            crystal_contribution=[
                "double-fire live-process station",
                "zero-completion volatile corridor",
                "lacuna-preservation threshold",
                "triple-root extraction return",
                "active bounded close",
            ],
            pointer_title="Double-Fire Live Volatile Processing",
            pointer_position="the verso of bifolio `f27/f30` and zero-completion counterpart to the staged unions of `f27r`",
            pointer_page_type="short B-language live-process page with one missing line, unique `kchrrr`, and no ordinary completion markers",
            pointer_conclusion="`ochof.chof`, `shy.shy`, missing `P5`, `kchrrr`, and active terminal `okshes.okcho.kshy`",
            pointer_judgment="`f27v` is one of Book I's clearest live-process leaves. It does not certify repeatedly; it keeps the fire-bearing route active and bounded until the end.",
            currier_language="B",
            currier_hand="2",
        ),
    ]
)


FOLIOS.extend(
    [
        make_folio(
            folio_id="F026R",
            quire="D",
            bifolio="bD2 = f26 + f31",
            manuscript_role="first Currier B standardized retort-processing page with production-language saturation",
            purpose="`f26r` introduces Currier B not as a gentle continuation but as a different operating language. The folio is saturated with `-edy` forms, repeats `qokedy` five times, uses the new fire token `fchy`, and standardizes what Currier A often rendered more idiosyncratically. This is the manuscript's first page that truly feels like production language: less singular drama, more repeatable retort procedure.",
            zero_claim="Translate earlier volatile-retort competencies into standardized production language, keep the route repeatable through `-edy` saturation and repeated `qokedy`, and close the first Currier B page as a stabilized retort corridor rather than a singular experiment.",
            botanical="`Prunella vulgaris` / self-heal remains the local candidate, though the page's stronger signature is linguistic and procedural: Book I shifts into production-language retort work",
            risk="safe",
            confidence="high on Currier B transition, standardized retort grammar, and production-language character",
            visual_grammar=[
                "`first Currier B page` = linguistic transition is the primary event on the leaf",
                "`about 18 `-edy` suffixes` = production-language fixation and repeatability dominate",
                "`qokedy` x5` = one standardized retort form becomes the page's anchor",
                "`eedy.eedy` and `qiiinkedy` = B-language intensity still exists, but inside regularized morphology",
            ],
            full_eva="""
P1: psheoky.odaiir.qoy-ofshod.chypchey.ypchedyain-chofo-chepchdy-
P2: dchey.saiin.ajeeody.ykecthey.chedy.ytedy.dy-checthedy.ls-
P3: oaiin.shcthy.cthedy.oloy.ykshdy.olchedy.dyl-ysheey.saiin.s-
P4: qokedy.cheos.ytedy.qokedy.ytedy.chekedy.daiin.odam.saldy-
P5: saiin.shedy.eedy.eedy.schy.daiin.cthedy-qokeedy.qokedy.cthey-
P6: rchedy.qokedy=
P7: peeo.qokedy.dar.sheo.ypchseds.s-aiin-shapchedy.fchy.dal.chedy.sar-
P8: daiin.shedy.qokeedy.qoteedar.s-okol.ytedy.qokeedy.qiiinkedy-
P9: tcheoshy.dshdy.okedy.chckhy.s-dy-dy-ykeechy.okeedy.cheky-
P10: shese.aiin.sheos.cheody.otal-
""",
            core_vml=[
                "`qokedy` x5 = standardized retort-processing anchor",
                "`-edy` saturation = Currier B shifts the folio into procedural regularity",
                "`fchy` = B-language fire token arrives inside production grammar, not as isolated drama",
                "`eedy.eedy` = doubled essence-energy fixation inside the regularized corridor",
                "`qiiinkedy` = quadruple-i retort variant proves B can still scale intensity",
            ],
            groups=[
                {"label": "P1", "title": "Paragraph 1 - B-language retort entry and regularization field", "line_ids": ["P1", "P2", "P3"]},
                {"label": "P2", "title": "Paragraph 2 - qokedy standardization and first union", "line_ids": ["P4", "P5", "P6"]},
                {"label": "P3", "title": "Paragraph 3 - fire token inside production language and quadruple retort close", "line_ids": ["P7", "P8", "P9", "P10"]},
            ],
            lines=[
                ("P1", "psheoky.odaiir.qoy-ofshod.chypchey.ypchedyain-chofo-chepchdy", "`psheoky` pressed transition-contained active; `odaiir`; `qoy-ofshod` transmuted moist fire-transition fix; `chypchey`; extended `ypchedyain`; `chofo`; `chepchdy`.", "Open Currier B with a morphology that already sounds standardized: repeated `-edy` endings turn the route into a process language.", "Currier B production-language opener", "mixed"),
                ("P2", "dchey.saiin.ajeeody.ykecthey.chedy.ytedy.dy-checthedy.ls", "`dchey`; `saiin`; `ajeeody` fixed double-essence active; `ykecthey`; `chedy`; `ytedy`; `dy-checthedy`; `ls`.", "The second line proves that Currier B can still carry essence intensity, but it encodes it inside highly regular suffixal grammar.", "regularized essence line", "mixed"),
                ("P3", "oaiin.shcthy.cthedy.oloy.ykshdy.olchedy.dyl-ysheey.saiin.s", "`oaiin`; `shcthy/cthedy`; `oloy`; `ykshdy`; `olchedy`; `dyl-ysheey`; `saiin`; `s`.", "Containment, conduit, fluid, and salt now move inside a standardized morphology rather than singular highlight tokens.", "standardized fluid-conduit salt route", "strong"),
                ("P4", "qokedy.cheos.ytedy.qokedy.ytedy.chekedy.daiin.odam.saldy", "`qokedy` twice; `cheos`; `ytedy` twice; `chekedy`; `daiin`; `odam`; `saldy`.", "This is the first full B-language theorem line: the standardized retort token repeats until union and salt fixation become routine.", "qokedy theorem line", "strong"),
                ("P5", "saiin.shedy.eedy.eedy.schy.daiin.cthedy-qokeedy.qokedy.cthey", "`saiin`; `shedy`; doubled `eedy`; `schy`; `daiin`; `cthedy`; `qokeedy`; `qokedy`; `cthey`.", "The page can still spike into doubled essence, but even that spike is rendered as repeatable procedure.", "doubled essence under procedure", "strong"),
                ("P6", "rchedy.qokedy", "`rchedy` rooted fixed volatile-active; `qokedy`.", "Reduce the whole paragraph to root-active fixation plus the standard retort operator.", "minimal standardization seal", "strong"),
                ("P7", "peeo.qokedy.dar.sheo.ypchseds.s-aiin-shapchedy.fchy.dal.chedy.sar", "`peeo` pressed double essence; `qokedy`; `dar`; `sheo`; `ypchseds`; `shapchedy`; `fchy`; `dal`; `chedy`; `sar`.", "The new fire token appears here, but it is immediately absorbed into standard retort, structure, and salt grammar.", "B-language fire inside procedure", "mixed"),
                ("P8", "daiin.shedy.qokeedy.qoteedar.s-okol.ytedy.qokeedy.qiiinkedy", "`daiin`; `shedy`; `qokeedy`; `qoteedar`; `s-okol`; `ytedy`; second `qokeedy`; `qiiinkedy`.", "Scale the standard route upward without abandoning its repeatable suffix logic.", "quadruple-retort scaling line", "strong"),
                ("P9", "tcheoshy.dshdy.okedy.chckhy.s-dy-dy-ykeechy.okeedy.cheky", "`tcheoshy`; `dshdy`; `okedy`; `chckhy`; `s-dy-dy`; `ykeechy`; `okeedy`; `cheky`.", "The ninth line shows Currier B at full speed: even valve-active control is folded into repeated `-edy` production cadence.", "fast production cadence line", "strong"),
                ("P10", "shese.aiin.sheos.cheody.otal", "`shese`; `aiin`; `sheos`; `cheody`; `otal`.", "Close the page as a compact transition-essence fluid route, not a singular dramatic endpoint.", "compact production close", "strong"),
            ],
            tarot_cards=tarot_for(10),
            movements=[
                "enter the production language",
                "regularize the essence corridor",
                "standardize fluid and salt",
                "repeat qokedy into union",
                "stabilize doubled essence",
                "reduce to minimal retort law",
                "absorb fire into procedure",
                "scale the standard route",
                "accelerate the production cadence",
                "close as compact retort flow",
            ],
            direct="`f26r` is the first true production-language page in Book I. Currier B enters by making retort work regular, suffix-heavy, and repeatable without losing access to high-energy states.",
            math="Across the formal lenses, `f26r` behaves like a standardization map. Repeated operators collapse variance, `qokedy` acts as a recurring kernel, and even exceptional tokens like `fchy` and `qiiinkedy` are normalized inside the broader procedure.",
            mythic="Across the mythic lenses, `f26r` is the factory floor opening. The art does not vanish; it becomes reproducible.",
            compression="Translate volatile-retort work into production language, repeat `qokedy` until the route is standard, absorb fire into the regular cadence, and close as stabilized procedure.",
            typed_state_machine=r"""
\[\mathcal R_{f26r} = \{r_{\mathrm{entry}}, r_{\mathrm{standardize}}, r_{\mathrm{union}}, r_{\mathrm{scale}}, r_{\mathrm{close}}\}\]
\[\delta(e_{\mathrm{qokedy}}): r_{\mathrm{entry}} \to r_{\mathrm{standardize}}\]
\[\delta(e_{\mathrm{odam}}): r_{\mathrm{standardize}} \to r_{\mathrm{union}}\]
\[\delta(e_{\mathrm{qiiinkedy}}): r_{\mathrm{union}} \to r_{\mathrm{scale}} \to r_{\mathrm{close}}\]
""",
            invariants=r"""
\[N_{\mathrm{-edy}}(f26r)\approx 18, \qquad N_{\mathrm{qokedy}}(f26r)=5, \qquad N_{\mathrm{fire\ token}}(f26r)=1\]
\[N_{\mathrm{doubled\ eedy}}(f26r)=1, \qquad N_{\mathrm{union}}(f26r)=1, \qquad N_{\mathrm{quadruple\ variant}}(f26r)=1\]
""",
            theorem=r"""
\[\rho_* = (\Psi_{P3} \circ \Psi_{P2} \circ \Psi_{P1})(\rho_0)\]

The formal theorem of `f26r` is:

1. Currier B begins by standardizing the route, not by reducing its sophistication
2. `qokedy` is the new production kernel that organizes repeated retort work
3. even fire and high-order retort variants are encoded as regular procedural inflections
4. the page's true novelty is linguistic-operational: Book I has entered reproducible production mode
""",
            crystal_contribution=[
                "Currier B production-language station",
                "qokedy standardization line",
                "B-language fire-inside-procedure threshold",
                "quadruple-retort scaling corridor",
                "compact production close",
            ],
            pointer_title="Production-Language Retort Standardization",
            pointer_position="the recto of bifolio `f26/f31` and first Currier B page in the manuscript",
            pointer_page_type="ten-line procedural leaf saturated with `-edy` forms and repeated `qokedy`",
            pointer_conclusion="`qokedy` x5, about 18 `-edy` suffixes, doubled `eedy`, `fchy`, and `qiiinkedy`",
            pointer_judgment="`f26r` is where Book I changes dialect. Currier B enters as production language: regular, retort-centered, and ready for scale.",
            currier_language="B",
            currier_hand="2",
        ),
        make_folio(
            folio_id="F026V",
            quire="D",
            bifolio="bD2 = f26 + f31",
            manuscript_role="pure Currier B triple-essence production page with maximum `-edy` saturation",
            purpose="`f26v` doubles down on what `f26r` introduces. The page is even more saturated with `-edy`, repeats `daiiin` twice, preserves both `ofchdy` and `ofchy` B-language fire forms, and runs a long production corridor where containment, transition, and completion are all rendered through one dominant suffix family. If `f26r` is the entry into Currier B, `f26v` is the proof that the new language can carry triple-essence medicine at full speed.",
            zero_claim="Run the pure production-language corridor with maximum `-edy` saturation, keep triple-essence and fire folded into the standardized morphology, and finish the page as a lawful completed route rather than a singular flare.",
            botanical="uncertain Herbal B form; the operational identity is clearer than the species candidate",
            risk="safe",
            confidence="high on pure Currier B production-language triple-essence processing",
            visual_grammar=[
                "`about 22 `-edy` forms` = the page is the clearest production-language saturation leaf yet",
                "`daiiin` at P1 and P7` = extended completion appears twice as global checkpoints",
                "`ofchdy` and `ofchy` = B-language fire remains embedded inside the procedural cadence",
                "`qotedy.qotedy` = doubled retort operator is normalized, not dramatized",
            ],
            full_eva="""
P1: pchedar.qodary.daiiin.pcheety.sair.shedy.ypchedy.ypchdy.qopy.shdy-
P2: saraiir.chekedy.qokedy.otedy.sary.etedy.qokedy.or.ashealys.chedy-
P3: pchdar.opar.dar.cheeol.ofchdy.otedy.ckhdy.odar.chedy.ytedy.okchdy.g-
P4: yckheody.qokedy.deey.saldy.okedor.or.cheos.oraiin.okeo.chekaiin-
P5: dchol.cheody.qoteedy.qokody.qotedy.qotedy.opchedy.ofchy.chs.ar-
P6: toeedy.keody.shedy.dar.chedy.shees.or.cheeky.dar.chey.cheky.yteedy-
P7: pchedy.dar.cheoetchy.sair.chees.odaiiin.chkeeey.ykey.sheey-
P8: tchedy.okeeos.cheeos.ysaiin.okcheey.keody.saiin.cheeos.qokes.ory-
P9: ysheey.okeshe.shody.peshy.tody.dy=
""",
            core_vml=[
                "`-edy` saturation reaches about 22` = Currier B fully commits to production morphology",
                "`daiiin` appears twice = extended completion now acts as a large-scale checkpoint rather than a singular flourish",
                "`ofchdy` and `ofchy` = B-language fire tokens survive inside the suffix-heavy procedural field",
                "`qotedy.qotedy` = doubled retort operator is normalized mid-page",
                "`chkeeey` = triple-essence body-volatile form inside the production corridor",
            ],
            groups=[
                {"label": "P1", "title": "Paragraph 1 - maximum `-edy` entry and repeated qokedy field", "line_ids": ["P1", "P2", "P3"]},
                {"label": "P2", "title": "Paragraph 2 - doubled retort normalization and embedded fire", "line_ids": ["P4", "P5", "P6"]},
                {"label": "P3", "title": "Paragraph 3 - triple-essence body forms and lawful page close", "line_ids": ["P7", "P8", "P9"]},
            ],
            lines=[
                ("P1", "pchedar.qodary.daiiin.pcheety.sair.shedy.ypchedy.ypchdy.qopy.shdy", "`pchedar` pressed fixed root; `qodary`; `daiiin`; `pcheety`; `sair`; `shedy`; `ypchedy/ypchdy`; `qopy`; `shdy`.", "Open the page at full production speed: extended completion arrives immediately inside a dense `-edy` corridor.", "maximum-saturation opener", "strong"),
                ("P2", "saraiir.chekedy.qokedy.otedy.sary.etedy.qokedy.or.ashealys.chedy", "`saraiir` double-root salt completion; `chekedy`; `qokedy`; `otedy`; `sary`; `etedy`; second `qokedy`; `or`; `ashealys`; `chedy`.", "The route is now so standardized that repeated qokedy sits naturally beside root-salt completion and outlet motion.", "repeated qokedy production line", "mixed"),
                ("P3", "pchdar.opar.dar.cheeol.ofchdy.otedy.ckhdy.odar.chedy.ytedy.okchdy.g", "`pchdar/opar/dar` pressed and opened root corridor; `cheeol` volatile-double-essence fluid; `ofchdy` fire-fix active; `otedy`; `ckhdy`; `odar`; `chedy`; `ytedy`; `okchdy`; terminal `g`.", "The page can still stage essence and fire, but all of it is absorbed into the production cadence.", "embedded fire in production cadence", "strong"),
                ("P4", "yckheody.qokedy.deey.saldy.okedor.or.cheos.oraiin.okeo.chekaiin", "`yckheody` moist valve-heat-fix active; `qokedy`; `deey`; `saldy`; `okedor`; `or`; `cheos`; `oraiin`; `okeo`; `chekaiin`.", "The route binds valve work, salt fixation, and contained essence without leaving the standardized grammar.", "salt-valve standard line", "strong"),
                ("P5", "dchol.cheody.qoteedy.qokody.qotedy.qotedy.opchedy.ofchy.chs.ar", "`dchol`; `cheody`; `qoteedy`; `qokody`; doubled `qotedy`; `opchedy`; `ofchy`; `chs`; `ar`.", "This is the page's normalization theorem: doubled retort and fire-active terms appear without breaking the procedural texture.", "normalized doubled-retort theorem", "strong"),
                ("P6", "toeedy.keody.shedy.dar.chedy.shees.or.cheeky.dar.chey.cheky.yteedy", "`toeedy/keody/shedy` repeated production variants; `dar`; `chedy`; `shees`; `or`; `cheeky`; second `dar`; `chey`; `cheky`; `yteedy`.", "The sixth line proves that B can carry high essence and active body forms while still sounding standardized.", "high-essence production braid", "strong"),
                ("P7", "pchedy.dar.cheoetchy.sair.chees.odaiiin.chkeeey.ykey.sheey", "`pchedy`; `dar`; `cheoetchy`; `sair`; `chees`; `odaiiin`; `chkeeey`; `ykey`; `sheey`.", "Triple essence and extended completion return together, but they are still folded into the B-language procedural weave.", "triple-essence return under completion", "strong"),
                ("P8", "tchedy.okeeos.cheeos.ysaiin.okcheey.keody.saiin.cheeos.qokes.ory", "`tchedy`; `okeeos/cheeos` contained essence bodies; `ysaiin`; `okcheey`; `keody`; second `saiin`; `cheeos`; `qokes`; `ory`.", "The penultimate line turns the route toward repeated essence bodies and salt completion without abandoning flow.", "essence-body salt penultimate line", "strong"),
                ("P9", "ysheey.okeshe.shody.peshy.tody.dy", "`ysheey` moist transition-essence active; `okeshe`; `shody`; `peshy`; `tody`; `dy`.", "Close as a concise active transition route ending in fixation, not as a dramatic terminal spike.", "lawful production close", "strong"),
            ],
            tarot_cards=tarot_for(9),
            movements=[
                "enter maximum suffix saturation",
                "repeat the production kernel",
                "hide fire inside procedure",
                "bind salt and valve work",
                "normalize doubled retort",
                "braid high essence into the cadence",
                "return triple essence under completion",
                "thicken the essence-body route",
                "close as lawful production flow",
            ],
            direct="`f26v` is pure Currier B. The page proves that standardized production language can carry fire, triple essence, and doubled retort without ceasing to sound procedural.",
            math="Across the formal lenses, `f26v` behaves like a maximal regularization field. Morphological repetition reduces variance, and exceptional loads like fire or triple essence are treated as admissible perturbations of the same production kernel rather than as separate regimes.",
            mythic="Across the mythic lenses, `f26v` is the engine room at full speed. The miracle is not that it burns; the miracle is that it stays rhythmic.",
            compression="Run the route in pure production language, fold fire and triple essence into the `-edy` cadence, normalize doubled retort, and close as lawful standardized flow.",
            typed_state_machine=r"""
\[\mathcal R_{f26v} = \{r_{\mathrm{saturate}}, r_{\mathrm{normalize}}, r_{\mathrm{essence\ body}}, r_{\mathrm{close}}\}\]
\[\delta(e_{\mathrm{daiiin}}): r_{\mathrm{saturate}} \to r_{\mathrm{normalize}}\]
\[\delta(e_{\mathrm{qotedy.qotedy}}): r_{\mathrm{normalize}} \to r_{\mathrm{essence\ body}}\]
\[\delta(e_{\mathrm{dy}}): r_{\mathrm{essence\ body}} \to r_{\mathrm{close}}\]
""",
            invariants=r"""
\[N_{\mathrm{-edy}}(f26v)\approx 22, \qquad N_{\mathrm{daiiin}}(f26v)=2, \qquad N_{\mathrm{fire\ tokens}}(f26v)=2\]
\[N_{\mathrm{qotedy}}(f26v)\ge 2, \qquad N_{\mathrm{triple\text{-}essence\ body\ forms}}(f26v)\ge 2, \qquad N_{\mathrm{terminal\ fixation}}(f26v)=1\]
""",
            theorem=r"""
\[\rho_* = (\Psi_{P3} \circ \Psi_{P2} \circ \Psi_{P1})(\rho_0)\]

The formal theorem of `f26v` is:

1. Currier B can bear high-intensity medicine without abandoning its standardized morphology
2. repeated suffixal regularity is itself a safety and reproducibility technology
3. doubled retort and embedded fire are normalized inside the production kernel rather than treated as separate dramas
4. the page closes as lawful flow because standardization now holds the route together
""",
            crystal_contribution=[
                "maximum Currier B saturation station",
                "pure production-language cadence line",
                "embedded fire normalization threshold",
                "doubled-retort standard corridor",
                "lawful production close",
            ],
            pointer_title="Pure Currier B Triple-Essence Production",
            pointer_position="the verso of bifolio `f26/f31` and immediate deepening of the first Currier B leaf",
            pointer_page_type="nine-line production-language page with about 22 `-edy` forms, doubled retort, and embedded fire",
            pointer_conclusion="double `daiiin`, `ofchdy`, `ofchy`, `qotedy.qotedy`, and `chkeeey` inside extreme `-edy` saturation",
            pointer_judgment="`f26v` proves that Currier B is not just simpler morphology. It is a full production language capable of carrying triple-essence medicine at industrial cadence.",
            currier_language="B",
            currier_hand="2",
        ),
    ]
)


FOLIOS.extend(
    [
        make_folio(
            folio_id="F025R",
            quire="D",
            bifolio="bD1 = f25 + f32",
            manuscript_role="maximally compressed quadruple-extraction active-salt page and penultimate Currier A folio",
            purpose="`f25r` is shockingly short for what it carries. In six body lines plus a title it packs the last Currier A fire seal, the unique `cheesees` quadruple-extraction token, multiple completion variants, and a title naming an active salt product. The page behaves like a compression exam: can the operator recognize a full high-order extraction route when almost every instruction is packed into condensed compounds.",
            zero_claim="Compress a quadruple extraction into minimal space, carry the route through multiple completion variants without reopening the corridor, and finish as a living active-salt product.",
            botanical="`Thymus capitatus` / wild thyme remains the local candidate, but the page is better read as a capstone of compressed active-salt procedure",
            risk="moderate",
            confidence="high on compressed quadruple extraction and active-salt title close",
            visual_grammar=[
                "`6 body lines plus title` = shortest page in the current four-quire span",
                "`cheesees` = unique quadruple-extraction signature",
                "`dense completion clustering` = completion variants appear at unusually high density for such a short leaf",
                "`title `otosy`` = the product is named as active or living salt",
            ],
            full_eva="""
P1: fcholdy.soshy.daiin.*in.shody.daiin.ocholdy.cpholdy.sy-
P2: otor.chor.chsky.chotchy.shain.qod.shachy.kchy.chkain-
P3: qotchy.qotshy.cheesees.sheear.s.chain.daiin.chain.dan-
P4: dchckhy.shocthy.ytchey.cthor.s.chan.chaiin.qotchain-
P5: qotcheaiin.dchain.cthain.daiin.daiin.cthain.qotaiin-
P6: okal.chotaiin=
T7: dair.otaiir.otosy=
""",
            core_vml=[
                "`fcholdy` = the last Currier A fire-seal opener",
                "`cheesees` = unique quadruple-extraction token and the page's clear climax",
                "`chain / dchain / cthain / qotchain` = completion variants are used as an entire family",
                "`daiin.daiin` = doubled verification appears even on this maximally compressed leaf",
                "`otosy` = active or living salt named directly in the title",
            ],
            groups=[
                {"label": "P1", "title": "Paragraph 1 - compressed fire-seal opener and quadruple extraction", "line_ids": ["P1", "P2", "P3"]},
                {"label": "P2", "title": "Paragraph 2 - completion-family compression and active-salt close", "line_ids": ["P4", "P5", "P6", "T7"]},
            ],
            lines=[
                ("P1", "fcholdy.soshy.daiin.*in.shody.daiin.ocholdy.cpholdy.sy", "`fcholdy` fire-volatile-fluid-fix active; `soshy` salt-transition active; two `daiin` checkpoints; damaged `*in`; `ocholdy/cpholdy` heated and alembic fluid-fix variants.", "Open with fire seal, salt, and repeated completion already compressed into one narrow corridor.", "compressed fire-seal opener", "mixed"),
                ("P2", "otor.chor.chsky.chotchy.shain.qod.shachy.kchy.chkain", "`otor/chor` timed heated outlet; `chsky` volatile-salt-body active; `chotchy` volatile heated active; `shain`; `qod`; `shachy`; `kchy`; `chkain`.", "The second line converts the opener into a short body-salt active corridor under completion.", "body-salt active compression", "strong"),
                ("P3", "qotchy.qotshy.cheesees.sheear.s.chain.daiin.chain.dan", "`qotchy/qotshy` transmuted active and transition-active states; `cheesees` quadruple extraction; `sheear` transition double-essence root; `chain`; `daiin`; second `chain`; `dan`.", "This is the folio's theorem line: maximal extraction is packed into one sentence and immediately stabilized by completion-family grammar.", "quadruple-extraction theorem", "strong"),
                ("P4", "dchckhy.shocthy.ytchey.cthor.s.chan.chaiin.qotchain", "`dchckhy` fixed valve-active volatile; `shocthy` transition volatile conduit bind; `ytchey`; `cthor`; `s`; `chan/chaiin/qotchain` three completion variants.", "The page answers maximal extraction with maximal finish-language density.", "completion-family cascade", "strong"),
                ("P5", "qotcheaiin.dchain.cthain.daiin.daiin.cthain.qotaiin", "`qotcheaiin` transmuted volatile completion; `dchain/cthain` fixed and conduit completion variants; doubled `daiin`; `qotaiin`.", "The fifth line doubles ordinary verification inside an already completion-saturated grammar.", "double-check inside completion field", "strong"),
                ("P6", "okal.chotaiin", "`okal` heated contained structure; `chotaiin` volatile heated completion.", "Reduce the route to one last structure-plus-completion miniature.", "minimal structural seal", "strong"),
                ("T7", "dair.otaiir.otosy", "`dair` timed fixation; `otaiir` heated completion-outlet; `otosy` active salt.", "Name the finished product as timed active salt rather than generic extract.", "active-salt title", "strong"),
            ],
            tarot_cards=tarot_for(7),
            movements=[
                "ignite and salt the corridor",
                "compress the body-active route",
                "pack quadruple extraction into one line",
                "cascade through completion variants",
                "double-check the compressed field",
                "shrink to structural seal",
                "name the active-salt product",
            ],
            direct="`f25r` is the penultimate Currier A compression leaf. It proves that a high-order extraction can be taught in miniature if the operator already knows how to unpack dense completion families.",
            math="Across the formal lenses, `f25r` behaves like a high-information compression map. Operator density is high, line count is low, and the route reaches a legitimate active-salt attractor without relaxing its control grammar.",
            mythic="Across the mythic lenses, `f25r` is the master whisper. A whole workshop is folded into one breath and a title.",
            compression="Compress a fire-sealed quadruple extraction into six lines, stabilize it through dense completion families, and seal the product as active salt.",
            typed_state_machine=r"""
\[\mathcal R_{f25r} = \{r_{\mathrm{ignite}}, r_{\mathrm{quadextract}}, r_{\mathrm{completion\ family}}, r_{\mathrm{saltclose}}\}\]
\[\delta(e_{\mathrm{fcholdy}}): r_{\mathrm{ignite}} \to r_{\mathrm{quadextract}}\]
\[\delta(e_{\mathrm{cheesees}}): r_{\mathrm{quadextract}} \to r_{\mathrm{completion\ family}}\]
\[\delta(e_{\mathrm{otosy}}): r_{\mathrm{completion\ family}} \to r_{\mathrm{saltclose}}\]
""",
            invariants=r"""
\[N_{\mathrm{visible\ units}}(f25r)=7, \qquad N_{\mathrm{cheesees}}(f25r)=1, \qquad N_{\mathrm{completion\ variants}}(f25r)\ge 8\]
\[N_{\mathrm{fire\ seal}}(f25r)=1, \qquad N_{\mathrm{daiin}}(f25r)=4, \qquad N_{\mathrm{title}}(f25r)=1\]
""",
            theorem=r"""
\[\rho_* = (\Psi_{P2} \circ \Psi_{P1})(\rho_0)\]

The formal theorem of `f25r` is:

1. the page is intentionally compressed rather than incomplete
2. `cheesees` marks the highest extraction burden on the leaf, but completion-family grammar immediately absorbs it
3. the final Currier A fire seal appears here as compressed mastery rather than as spectacle
4. the title proves that the end state is an active salt body, not an unresolved intermediate
""",
            crystal_contribution=[
                "compressed quadruple-extraction station",
                "last Currier A fire-seal threshold",
                "completion-family compression line",
                "double-check miniature corridor",
                "active-salt title close",
            ],
            pointer_title="Compressed Quadruple-Extraction Active Salt",
            pointer_position="the recto of bifolio `f25/f32` and penultimate Currier A page in the manuscript",
            pointer_page_type="ultra-short capstone leaf with one title line, unique `cheesees`, and dense completion-family grammar",
            pointer_conclusion="`fcholdy`, `cheesees`, `chain/dchain/cthain/qotchain`, and title `otosy`",
            pointer_judgment="`f25r` is a capstone miniature. The page compresses a full quadruple-extraction route into almost no space and still lands on an explicitly named active-salt product.",
        ),
        make_folio(
            folio_id="F025V",
            quire="D",
            bifolio="bD1 = f25 + f32",
            manuscript_role="Currier A capstone page for maximum-verified fire-sealed transitional procedure",
            purpose="`f25v` is the last surviving Currier A page and it behaves like a final examination in that language. Completion density is the highest in the current manuscript run, `qofchor` and `shcfhor` preserve A-language fire usage at the capstone, `daiity` and `deeaiir` push completion into unusual high-energy variants, and the page closes without giving up transitional volatility. It reads like a declaration that Currier A's discipline is control through repeated lawful closure, not merely early simplicity.",
            zero_claim="Cap the Currier A corridor by saturating a fire-sealed transitional route with completion markers, keep the active volatile under repeated verification, and close the language phase without abandoning intensity.",
            botanical="`Isatis tinctoria` / woad remains the local candidate, though the operational profile points more strongly to a capstone transitional procedure",
            risk="moderate",
            confidence="high on Currier A capstone status, completion saturation, and fire-sealed transition law",
            visual_grammar=[
                "`last Currier A page` = the folio functions as a language capstone",
                "`highest completion density in the current run` = closure grammar dominates every line",
                "`physical damage at P1 and P7` = the witness remains imperfect but legible",
                "`A-language fire tokens persist to the end` = Currier A does not exit quietly; it exits under controlled flame",
            ],
            full_eva="""
P1: ***aiin.qoky.shy.daiin.qopchey.otchey.qofchor.sos-
P2: dchor.cthor.chor.daiin.s.okeeaiin.daiin.ckhey.daiin-
P3: orcho.kchor.chol.daiin.shcfhor.daiin.dshey.daiity-
P4: qokaiin.qokcho.shol.daiin.ckhear.ckhol.daiin.chkear-
P5: dar.chokeey.dshor.dshey.qochol.dol.cho.daiin.daiin-
P6: qokcho.r.ochy.qotchy.qotoral.cho.*.chain.deeaiir.s-
P7: o*.chkey.daii.ol.daiin.shckh.orchaiin=
""",
            core_vml=[
                "`qofchor` = retort-fire-volatile-source in the damaged opener line",
                "`shcfhor` = final clear Currier A fire-seal token",
                "`daiity` = energized completion variant",
                "`deeaiir` = double-essence fix-root completion late in the page",
                "`completion density ~1.57 per line` = closure grammar is the true capstone signal",
            ],
            groups=[
                {"label": "P1", "title": "Paragraph 1 - damaged fire-retort opener and completion saturation", "line_ids": ["P1", "P2", "P3"]},
                {"label": "P2", "title": "Paragraph 2 - valve-structured continuation and capstone close", "line_ids": ["P4", "P5", "P6", "P7"]},
            ],
            lines=[
                ("P1", "***aiin.qoky.shy.daiin.qopchey.otchey.qofchor.sos", "damaged completion opener; `qoky/shy`; `daiin`; `qopchey/otchey` retort-active volatile variants; `qofchor` retort-fire-source; `sos` salt-transition.", "Even in damage, the page starts as a fire-sealed retort route already under completion and salt law.", "damaged fire-retort opener", "mixed"),
                ("P2", "dchor.cthor.chor.daiin.s.okeeaiin.daiin.ckhey.daiin", "`dchor/cthor/chor` fixed, conduit, and ordinary outlets; three `daiin`; `okeeaiin` contained double-essence completion; `ckhey` valve-essence active.", "The second line shows why this is a capstone: outlet control and completion repeat until they become the page's atmosphere.", "outlet control under triple verification", "strong"),
                ("P3", "orcho.kchor.chol.daiin.shcfhor.daiin.dshey.daiity", "`orcho/kchor/chol` outlet, body, and fluid-volatiles; `shcfhor` transition fire-seal source; `dshey`; `daiity` energized completion.", "The final A-language fire token appears mid-page, but it is immediately reabsorbed into completion and fixed volatile essence.", "capstone fire token line", "strong"),
                ("P4", "qokaiin.qokcho.shol.daiin.ckhear.ckhol.daiin.chkear", "`qokaiin/qokcho` extracted containment and extracted body-volatile; `shol`; `daiin`; `ckhear/ckhol/chkear` valve-root, valve-fluid, and valve-root variants; second `daiin`.", "The page answers fire with valve geometry and more completion, not with retreat.", "valve geometry under repeated proof", "strong"),
                ("P5", "dar.chokeey.dshor.dshey.qochol.dol.cho.daiin.daiin", "`dar`; `chokeey` volatile double-essence active; `dshor/dshey`; `qochol`; `dol`; `cho`; doubled `daiin`.", "Double essence is permitted, but only with doubled verification and fixed transition-outlet support.", "double-essence double-check line", "strong"),
                ("P6", "qokcho.r.ochy.qotchy.qotoral.cho.*.chain.deeaiir.s", "`qokcho`; `ochy`; `qotchy`; `qotoral` retort-heated-root-structure; damaged volatile token; `chain`; `deeaiir`; `s`.", "Late in the page, the route reaches retort-root-structure and the unusual `deeaiir` completion without ever loosening its control grammar.", "late retort-root capstone", "mixed"),
                ("P7", "o*.chkey.daii.ol.daiin.shckh.orchaiin", "damaged opener; `chkey` volatile-essence active; `daii`; `ol`; `daiin`; `shckh` transition valve-heat; `orchaiin` outlet completion.", "Close Currier A with damaged but still lawful volatile activity, one last valve-heat token, and outlet completion.", "damaged but lawful language close", "mixed"),
            ],
            tarot_cards=tarot_for(7),
            movements=[
                "open under damaged fire-retort law",
                "triple-verify the outlet",
                "place the final A-language fire token",
                "answer with valve geometry",
                "double-check the double essence",
                "drive to retort-root structure",
                "close Currier A in lawful damage",
            ],
            direct="`f25v` is the Currier A capstone. It exits the language not by simplifying, but by saturating a volatile fire route with completion and valve control until the operator can hold intensity without losing closure.",
            math="Across the formal lenses, `f25v` behaves like a high-density verification field. Fire terms remain present, but the dominant invariant is completion count, which repeatedly projects the route back into admissible outlet and valve subspaces.",
            mythic="Across the mythic lenses, `f25v` is the last lesson in the first tongue: keep the flame, but make it answer to law.",
            compression="Saturate the last Currier A fire-sealed transition page with completion, keep volatile activity under valve and outlet control, and close the language phase without giving up intensity.",
            typed_state_machine=r"""
\[\mathcal R_{f25v} = \{r_{\mathrm{fire\ route}}, r_{\mathrm{verification\ field}}, r_{\mathrm{valve\ control}}, r_{\mathrm{language\ close}}\}\]
\[\delta(e_{\mathrm{qofchor}}): r_{\mathrm{fire\ route}} \to r_{\mathrm{verification\ field}}\]
\[\delta(e_{\mathrm{shcfhor}}): r_{\mathrm{verification\ field}} \to r_{\mathrm{valve\ control}}\]
\[\delta(e_{\mathrm{orchaiin}}): r_{\mathrm{valve\ control}} \to r_{\mathrm{language\ close}}\]
""",
            invariants=r"""
\[N_{\mathrm{completion}}(f25v)\ge 11, \qquad N_{\mathrm{visible\ body\ lines}}(f25v)=7, \qquad N_{\mathrm{fire\ tokens}}(f25v)\ge 2\]
\[N_{\mathrm{damage\ lines}}(f25v)=2, \qquad N_{\mathrm{doubled\ verification}}(f25v)\ge 2, \qquad N_{\mathrm{rare\ capstone\ variants}}(f25v)=2\]
""",
            theorem=r"""
\[\rho_* = (\Psi_{P2} \circ \Psi_{P1})(\rho_0)\]

The formal theorem of `f25v` is:

1. Currier A ends in heightened density, not reduced complexity
2. fire remains present through `qofchor` and `shcfhor`, but repeated completion governs the page more strongly than flame does
3. valve and outlet control absorb the dangerous middle back into lawful structure
4. the damaged close still certifies a valid language-phase ending because the completion and valve grammar survive intact
""",
            crystal_contribution=[
                "Currier A capstone station",
                "fire-retort completion field",
                "final A-language fire threshold",
                "valve-geometry verification corridor",
                "damaged but lawful language close",
            ],
            pointer_title="Currier A Capstone Fire-Sealed Transition",
            pointer_position="the verso of bifolio `f25/f32` and final Currier A folio in the manuscript",
            pointer_page_type="short capstone page with heavy completion density, damaged opening and close, and preserved A-language fire tokens",
            pointer_conclusion="`qofchor`, `shcfhor`, `daiity`, `deeaiir`, and the manuscript's highest completion density so far",
            pointer_judgment="`f25v` is the last Currier A page, and it behaves like a graduation test: keep fire, volatility, and damage in play, but never surrender the rule of closure.",
        ),
    ]
)


def main() -> None:
    for folio in FOLIOS:
        (FOLIOS_DIR / f"{folio['folio_id']}_FINAL_DRAFT.md").write_text(render_folio(folio), encoding="utf-8")
        (FOLIOS_DIR / f"{folio['folio_id']}.md").write_text(render_pointer(folio), encoding="utf-8")


if __name__ == "__main__":
    main()
