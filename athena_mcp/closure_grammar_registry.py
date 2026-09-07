"""CLOSURE GRAMMAR — tradition registry (data, not code).

One entry per tradition / system, holding only what was attested in the
sources named in ``sources`` (the uploaded corpus, primary texts checked on
2026-09-07, or the pulses Ω28–Ω44).  Every line carries a glyph:

    🟢  extracted from a primary/secondary source or proved arithmetically
    🟡  attested but recalled / reading-dependent / contested
    🟠  interpretation (ours or the corpus's), not a fact about the source

``standing`` uses the vocabulary of ``athena_mcp.mythic_strata_runtime``:
PRIMARY_EVIDENCE, SECONDARY_SCHOLARSHIP, LIVING_TRADITION_SOURCE,
TRADITION_INTERNAL, MODERN_RECONSTRUCTION.

Crossing ``seat`` values (see docs/closure_grammar/02_SEATS.md):

    extra      an (n+1)th element outside the count: witness, uninvited,
               unnumbered, set aside  (17th ikin, the Fool 0, Da'at, Levi)
    centre     n around one central element that is not one of the n
               (4 provinces + Mide, Lo Shu 5, tengen, the poto mitan)
    withdrawn  the last of a nominal count is hidden / withheld / falls
               (12th Imam, 30th aeon Sophia, 18th charm, 50th gate)
    return     the (n+1)th step is the first again
               (7th day 復, the octave, 8th hour, 13th year, jubilee)
    residue    a declared leftover that does not close
               (5 epagomenal days, 1/64, the comma, the wayeb)
    extension  a marked block of k > 1 extra members outside the count
               (Rāhu and Ketu over the seven; the five forfeda; the five
               finals) — kept separate because it is not the unit step

For every seat except ``residue`` and ``extension`` the registry demands
cross == n + 1; for those two it demands cross > n.  ``marked`` records whether the
source itself marks the element as special (hidden, uncounted, unlucky,
holy, forbidden, witness).  An unmarked adjacency is only [N] and is not
entered as a crossing at all.

Number ``role`` values for the census in scripts/closure_grammar_report.py:
closure, order, passage, record, chaos, residue.
"""
from __future__ import annotations

REGISTRY_VERSION = "CLOSURE_GRAMMAR_REGISTRY_V1"
LAW = "close at n, cross at n+1, return"

SEATS = {
    "extra": "an (n+1)th element outside the closed count (witness / uninvited / unnumbered / set aside)",
    "centre": "n elements around one central element that is not one of the n",
    "withdrawn": "the last of a nominal count is hidden, withheld, or falls",
    "return": "the (n+1)th step is the first again",
    "residue": "a declared leftover quantity that does not close",
    "extension": "a marked block of k > 1 extra members outside the closed count (the shadow planets, the forfeda, the finals); evidence for a marked extra, not for the unit step",
}

GRADES = {"🟢": "extracted / proved", "🟡": "recalled / reading-dependent / contested", "🟠": "interpretation"}


def X(n, cross, seat, what, grade="🟢", marked=True, src=""):
    return {"n": n, "cross": cross, "seat": seat, "what": what, "grade": grade, "marked": marked, "src": src}


def C(n, what, grade="🟢"):
    return {"n": n, "what": what, "grade": grade}


def N(n, role, what, grade="🟢"):
    return {"n": n, "role": role, "what": what, "grade": grade}


def R(what, grade="🟢", quantity=None):
    d = {"what": what, "grade": grade}
    if quantity is not None:
        d["quantity"] = quantity
    return d


TRADITIONS = []


def T(**kw):
    kw.setdefault("closures", [])
    kw.setdefault("crossings", [])
    kw.setdefault("residues", [])
    kw.setdefault("devices", {"record": [], "hull": []})
    kw.setdefault("ladder", [])
    kw.setdefault("oracle", None)
    kw.setdefault("calendar", None)
    kw.setdefault("arithmetic", {"present": False, "what": ""})
    kw.setdefault("numbers", [])
    kw.setdefault("negatives", [])
    kw.setdefault("notes", "")
    TRADITIONS.append(kw)
    return kw


# ============================================================================
# A. ANCIENT NEAR EAST
# ============================================================================

T(
    id="sumer_babylon", name="Sumer / Babylon", family="Ancient Near East", region="Mesopotamia",
    standing="PRIMARY_EVIDENCE",
    sources=["ETCSL Sumerian King List (ms. WB), reigns re-fetched 2026-09-07", "Enūma Eliš (Ω34 census)",
             "god-number logograms: Anu 60, Enlil 50, Ea 40, Sin 30, Šamaš 20, Nergal 14 (Wikipedia infoboxes, 2026-09-07)",
             "Ω31–Ω34 pulses; corpus: ŠAR-60 Registry, SUMERIAN HOLOGRAM CARTRIDGE Ω5"],
    closures=[C(6, "closure ceiling: largest entry of any non-dihedral closing triple"), C(60, "carrier = lcm(1..6)"),
              C(360, "ideal year = lcm(1..10)/7"), C(3600, "šar = 60², 'totality'"), C(12, "months of the schematic year"),
              C(36, "stars of the three paths (Enūma Eliš V)"), C(7, "Anunnaki judges; gates of the netherworld")],
    crossings=[
        X(6, 7, "extra", "six registers close; seven gates of the Descent — the netherworld is the region the base cannot write", "🟠",
          src="Inanna's Descent; regular-number arithmetic"),
        X(6, 7, "return", "storm six days and seven nights, abates on the seventh (Gilgameš XI)", "🟢"),
        X(60, 61, "extra", "An = 60 = the unit; Nergal 14 = 2·7 is the pantheon's only irregular number, seated on death", "🟢", marked=True,
          src="Nergal infobox: number 14; 14th and 28th days sacred to him"),
        X(12, 13, "residue", "twelve months close; the intercalary thirteenth month (7 in 19 years by the 5th c. BC)", "🟢"),
    ],
    residues=[R("intercalation: 7 months in 19 years", "🟢", "7/19"), R("Kingu's blood → humanity (Enūma Eliš VI): the residue embodied", "🟠")],
    devices={"record": ["clay tablet", "cylinder seal (K=0 cover S¹×I→ℝ×I, mirror-cut)"], "hull": ["Utnapištim's cubic ark 120 cubits, 6 decks / 7 levels, 8 šar-gal"]},
    ladder=[{"count": 60, "what": "šar-gal 60³ → šar 60² → geš 60¹ → unit; King List descends one power per tier (log₆₀ 2.51 → 1.60 → 0.97)"}],
    oracle=None,
    calendar={"charts": [[12, 30], [6, 60], [2, 180], [1, 360]], "year": 360, "residue": "intercalary month", "intercalation": "7 in 19"},
    arithmetic={"present": True, "what": "sexagesimal place value; regular (2·3·5-smooth) reciprocal tables; first irregular 7"},
    numbers=[N(60, "order", "An"), N(50, "order", "Enlil / Marduk's fifty names"), N(40, "order", "Ea"), N(30, "order", "Sin"),
             N(20, "order", "Šamaš"), N(15, "order", "Ištar"), N(10, "order", "Adad (also 6)"), N(14, "passage", "Nergal, netherworld"),
             N(7, "passage", "gates of the Descent; Anunnaki judges"), N(126, "passage", "Gilgameš's reign 2·3²·7, the king who fails to cross death"),
             N(840, "passage", "Kish I reigns 14·60, first 7 in the list; first HCN divisible by 7"), N(420, "passage", "En-tarah-ana 7·60"),
             N(36, "order", "stars of the three paths"), N(12, "order", "months"), N(600, "order", "Anunnaki above and below, 300+300"),
             N(11, "chaos", "Tiamat's monsters"), N(8, "order", "Marduk's four eyes and four ears"),
             N(241200, "order", "antediluvian total = 67 šar"), N(432000, "order", "Berossus: 10 kings, 120 šar")],
    negatives=["Adad attested as both 6 and 10; the fraction 1/5 (12 sixtieths) has no god"],
    notes="Nine scripts' anchor. Verified today: all 47 reigns of the antediluvian, Kish I, Uruk I and Ur I tiers match the ETCSL text.",
)

T(
    id="egypt", name="Egypt", family="Ancient Near East", region="Nile valley",
    standing="PRIMARY_EVIDENCE",
    sources=["Egyptian calendar; Assessors of Maat; Osiris myth (Plutarch); Ennead/Ogdoad; Eye of Horus (Ritter 2002 dispute) — Wikipedia 2026-09-07",
             "corpus: EGYPT_KHEPER_GANITAM.docx (AI-drafted computational ontology; primary loci cited by spell number)", "Ω35 pulse"],
    closures=[C(360, "ideal year 12×30"), C(36, "decans"), C(8, "Ogdoad of Hermopolis"), C(9, "Ennead of Heliopolis = Atum + 8"),
              C(42, "assessors / negative confessions / nomes"), C(12, "hours of the night, gates"), C(6, "parts of the Eye (disputed fraction reading)")],
    crossings=[
        X(360, 365, "residue", "5 epagomenal days, birthdays of Osiris, Horus, Set, Isis, Nephthys; 'dangerous'", "🟢"),
        X(8, 9, "extra", "Ogdoad 8 → Ennead 9: Atum added above the eight; corpus reads Atum as the U(1) singlet 'that commutes with all other generators'", "🟢",
          src="Ennead page: Atum + 8 descendants; corpus Kheper Ganitam §3"),
        X(12, 13, "extra", "corpus: 'the Hidden 13th … Casimir operator that commutes with all 12 hourly Hamiltonians' (the sun disk over the 12 hours)", "🟠",
          src="Kheper Ganitam ch.4"),
        X(42, 43, "extra", "Thoth over the 42 judges: 'he does not cast a vote himself; he compiles the outputs of the 42 nodes'", "🟠", src="Kheper Ganitam B.8"),
        X(63, 64, "residue", "Eye of Horus 63/64, the missing 1/64 restored by Thoth (fraction reading disputed by Ritter 2002)", "🟡"),
        X(13, 14, "residue", "13 pieces of Osiris recovered; the 14th lost to the fish and replaced by a made substitute (Plutarch)", "🟢"),
    ],
    residues=[R("5 epagomenal days", "🟢", "365-360"), R("1/64 of the Eye", "🟡", "1/64"), R("the 14th piece", "🟢"),
              R("wandering year: 365 vs 365.25, Sothic cycle ≈ 1460", "🟢", "0.25/yr")],
    devices={"record": ["papyrus scroll (quotient: rolls the plane)", "tomb walls as boundary (corpus: AdS/CFT reading)"], "hull": ["chest of Osiris sealed and floated", "sarcophagus", "naos sealed with clay"]},
    ladder=[{"count": 10, "what": "decimal orders (iconic hieroglyphic powers of ten)"}, {"count": 12, "what": "hours of the Duat; 6th hour = midnight singularity"}],
    oracle=None,
    calendar={"charts": [[10, 36], [3, 120], [5, 72], [12, 30]], "year": 360, "residue": "5 epagomenal", "intercalation": "none (wandering year)"},
    arithmetic={"present": True, "what": "unit fractions: 1 = 1/2+1/3+1/6 is the unique three-term distinct partition; greedy remainder after (2,3,7) is 1/42"},
    numbers=[N(42, "passage", "assessors of the dead = 2·3·7"), N(14, "passage", "pieces of Osiris = waning half-month (Plutarch)"),
             N(70, "passage", "days of embalming = decan invisibility"), N(7, "passage", "Hathors of fate; gates of the house of Osiris"),
             N(21, "passage", "portals BD 144–147"), N(72, "chaos", "Set's conspirators = 360/5"),
             N(36, "order", "decans"), N(360, "order", "ideal year"), N(9, "order", "Ennead"), N(8, "order", "Ogdoad"), N(12, "order", "hours"),
             N(365, "residue", "civil year = 5·73, irregular"), N(1461, "residue", "Sothic cycle = 3·487, irregular"), N(30, "order", "Sed festival years")],
    negatives=["Eye-of-Horus fraction reading is contested (Ritter 2002); kept 🟡"],
    notes="Independent test of the grammar with base 10 and unit fractions. Corpus document locates the +1 'on top' (Atum, hidden 13th, Thoth), unlike Dao Su which seats it at the centre.",
)

T(
    id="zoroastrian", name="Zoroastrian / Avestan", family="Iranian", region="Iran",
    standing="PRIMARY_EVIDENCE",
    sources=["Amesha Spenta and Zoroastrian calendar pages, Wikipedia 2026-09-07", "corpus catalog: 'HBAS-Ω analysis' (12,000-year cycle)"],
    closures=[C(6, "Amesha Spentas proper"), C(7, "with Spenta Mainyu / Ahura Mazda as the seventh"), C(30, "named days of the month"), C(12, "months"),
              C(12000, "world-year = 4 × 3000", "🟡")],
    crossings=[
        X(6, 7, "extra", "six Amesha Spentas; 'the group is extended to include Ahura Mazda, represented by (or together with) Spenta Mainyu' as the seventh", "🟢"),
        X(360, 365, "residue", "12 × 30 named days + the five Gatha days (Hamaspathmaidyem)", "🟢"),
        X(3, 4, "return", "three nights after death, judgment at the Chinvat bridge at the dawn that follows (Vendidad 19)", "🟡"),
    ],
    residues=[R("five Gatha days", "🟢", "5")],
    devices={"record": [], "hull": ["fire temple as coherence-maintaining enclosure (corpus reading)"]},
    ladder=[{"count": 4, "what": "four ages of 3000 years"}],
    calendar={"charts": [[12, 30]], "year": 360, "residue": "5 Gatha days", "intercalation": "one month every 120 years (Sasanian, 🟡)"},
    arithmetic={"present": False, "what": ""},
    numbers=[N(7, "order", "Amesha Spentas with Ahura Mazda"), N(6, "order", "Amesha Spentas proper"), N(30, "order", "day-names"),
             N(5, "residue", "Gatha days"), N(3, "passage", "nights before Chinvat"), N(12000, "order", "world-year")],
    notes="Same 360 + 5 as Egypt with a different pantheon on the residue days: the five days are the Gathas, not births.",
)

T(
    id="canaan_ugarit", name="Ugarit / Canaan", family="Ancient Near East", region="Levant",
    standing="SECONDARY_SCHOLARSHIP",
    sources=["Baal Cycle (KTU 1.1–1.6), recalled"],
    closures=[C(70, "sons of Athirat (KTU 1.4 VI 46)", "🟡"), C(7, "years of Baal's absence / Mot's cycle", "🟡")],
    crossings=[X(6, 7, "return", "Baal's palace: fire burns six days, on the seventh the house stands (KTU 1.4 VI 24–33)", "🟡"),
               X(0, 1, "extra", "the window in Baal's closed house — the one opening Kothar insists on and Baal at first refuses (KTU 1.4 V–VII)", "🟠")],
    devices={"record": ["clay tablet"], "hull": ["Baal's house of cedar and brick with its single window"]},
    numbers=[N(70, "order", "sons of Athirat"), N(7, "passage", "years; days of the fire"), N(6, "order", "days of building")],
    notes="Thin entry, kept 🟡: the six-days/seventh-day building formula is the same formula as Gilgameš XI and Genesis 1.",
)

# ============================================================================
# B. MEDITERRANEAN — GREEK, ROMAN, HELLENISTIC
# ============================================================================

T(
    id="greek_philosophy", name="Greek philosophy (Pythagoras, Plato, Aristotle, Archimedes, Ptolemy)", family="Mediterranean", region="Greece",
    standing="PRIMARY_EVIDENCE",
    sources=["Timaeus 53c–55c; Laws 737e; Republic 546, 587e; Metaphysics A5 (Counter-Earth); Aether (De Caelo)",
             "corpus Philosophy.zip: PYTHAGOREAN / EUCLIDEAN / POLITEIA / PTOLEMAIC / PLATO UFT / METAPHYSICS / ARCHIMEDEAN / ATOMIST / ARISTOTELIAN engines",
             "5040 and Counter-Earth pages, Wikipedia 2026-09-07", "Ω40 pulse"],
    closures=[C(10, "tetractys 1+2+3+4; the ten Pythagorean opposites; ten bodies of Philolaus"), C(4, "elements"), C(5, "regular solids"),
              C(5040, "citizens of the Laws = 7!, divisible by 1..10 and 12"), C(729, "= 3⁶ days-and-nights of the king's happiness"),
              C(12960000, "nuptial number 60⁴ (Adam 1902)"), C(6, "half-equilateral triangles per face (Timaeus 54e: two rejected)"),
              C(10, "Aristotle's categories"), C(4, "Aristotle's causes — 'no fifth'"), C(55, "Aristotle's spheres"), C(31, "Euclid Optics propositions? corpus 2⁵−1", "🟠")],
    crossings=[
        X(9, 10, "extra", "Counter-Earth added 'to raise the number of heavenly bodies from nine to ten, which the Pythagoreans regarded as perfect' (Met. A5): a body invented to close the count", "🟢"),
        X(4, 5, "extra", "aether, the fifth element beyond the four, incapable of change, moving only in circles (De Caelo I.2–3)", "🟢"),
        X(10, 11, "return", "corpus Pythagorean engine: 'upon reaching 10 the system does not generate a Unit 11; it executes a return to the Root, 10 ⇒ 1'", "🟠"),
        X(7, 8, "residue", "twelve fifths overshoot seven octaves by the comma 3¹²/2¹⁹; the circle of fifths is a helix", "🟢"),
        X(8, 9, "extra", "seven planets + fixed stars = 8 spheres; the primum mobile as ninth (medieval Ptolemaic), the Unmoved Mover beyond all", "🟡"),
        X(6, 7, "extra", "corpus Politeia: anacyclosis closes on six constitutions; the Mixed Constitution is 'the seventh outside the 2×3 matrix'", "🟠"),
    ],
    residues=[R("leimma 256/243: the semitone that does not close (Timaeus 36b)", "🟢"), R("Pythagorean comma 531441/524288", "🟢"),
              R("incommensurable diagonal √2", "🟢"), R("Archimedes' cattle problem: 7 conditions close, the 8th/9th overflow (corpus)", "🟠")],
    devices={"record": ["wax tablet", "the sphere unrolled: Archimedes' surface = 2πr × 2r rectangle; stereographic projection (corpus Ptolemaic)"],
             "hull": ["the cosmos as sphere (Timaeus)", "Plato's cave", "Diogenes' pithos (corpus Cynic)"]},
    ladder=[{"count": 4, "what": "divided line"}, {"count": 4, "what": "tetractys point→line→plane→solid"}, {"count": 8, "what": "Archimedes' orders of 10⁸: 'the last of an order becomes the unit of the next' (corpus)"}],
    arithmetic={"present": True, "what": "ratios, means, tetractys, Timaeus triangle counts: 4·6=24, 8·6=48, 20·6=120 = |2T|,|2O|,|2I| (McKay)"},
    numbers=[N(24, "order", "tetrahedron elementary triangles = |2T|"), N(48, "order", "octahedron = |2O|"), N(120, "order", "icosahedron = |2I|"),
             N(5040, "order", "Laws"), N(729, "order", "Republic IX"), N(12960000, "order", "nuptial number 60⁴"), N(216, "order", "Plato's number 6³ = 3³+4³+5³"),
             N(10, "order", "decad"), N(7, "passage", "octaves overshot by twelve fifths"), N(12, "order", "fifths"), N(55, "order", "spheres"),
             N(4, "order", "elements, causes"), N(5, "order", "solids; fifth element")],
    notes="The tradition that argues the arithmetic out loud: divisibility as civic law, a residue named, a planet invented to close a count.",
)

T(
    id="greek_myth_cult", name="Greek myth and mystery cults (Olympians, Eris, Orphic, Eleusinian, Apollo)", family="Mediterranean", region="Greece",
    standing="PRIMARY_EVIDENCE",
    sources=["Twelve Olympians and Eris pages, Wikipedia 2026-09-07", "corpus Philosophy.zip: ORPHIC & HYMNIC DRIVER (87 hymns; Derveni 'DECODER'; gold leaves)",
             "Hesiod Works and Days 765–828 (recalled)"],
    closures=[C(12, "Olympians — 'the canonical number was twelve' though thirteen principal gods qualify"), C(9, "Muses"), C(3, "Fates, Graces, Hours"),
              C(50, "Nereids, Danaids"), C(12, "labours"), C(87, "Orphic hymns (corpus)"), C(7, "against Thebes; sages; wonders")],
    crossings=[
        X(12, 13, "extra", "thirteen principal Olympians for twelve seats: one always stands out (Hestia/Dionysus swap; the page marks the 'gave up her throne' story as modern)", "🟡"),
        X(12, 13, "extra", "Eris, the one goddess not invited to the wedding of Peleus and Thetis, throws the apple: the excluded one causes the breakdown", "🟢"),
        X(6, 7, "return", "Apollo hebdomagenes, born on the seventh; the seventh of the month holy (Hesiod WD 770)", "🟡"),
        X(1, 2, "extra", "Orphic gold leaves: refuse the first spring (Lethe), take the second (Mnemosyne) — the 'one more' spring on the right (corpus)", "🟠"),
    ],
    residues=[R("Hesiod's Days: some days of the month unlucky, the fifth in particular (WD 802)", "🟡")],
    devices={"record": ["Orphic gold lamellae buried with the initiate ('recovery disk', corpus)"], "hull": ["Orphic egg", "Eleusinian kykeon vessel", "the cista mystica"]},
    ladder=[{"count": 6, "what": "Orphic six generations of rulers (Phanes → Nyx → Ouranos → Kronos → Zeus → Dionysus)", "grade": "🟡"}],
    numbers=[N(12, "order", "Olympians"), N(13, "passage", "the excluded / the extra"), N(7, "passage", "Apollo's day"), N(9, "order", "Muses; Eleusinian nine days"),
             N(87, "record", "Orphic hymns"), N(6, "order", "Orphic generations")],
    notes="Eris and Oshun (Ifá) are the two cleanest 'uninvited one breaks the system' cases in the registry.",
)

T(
    id="hellenistic_schools", name="Hellenistic schools (Stoic, Pyrrhonian, Cynic, Hippocratic, Epistemic)", family="Mediterranean", region="Greece / Rome",
    standing="SECONDARY_SCHOLARSHIP",
    sources=["corpus Philosophy.zip: STOIC KERNEL, PYRRHONIAN NULL-STATE DRIVER, CYNIC BLOATWARE REMOVER, Hippocratic BIO_OS, EPISTEMIC VALIDATION ENGINE"],
    closures=[C(4, "humours / qualities / elements / seasons in one 4×7 matrix (corpus)"), C(10, "modes of Aenesidemus, reduced to the eighth"),
              C(3, "trilemma of Agrippa — 'no fourth option exists'"), C(2, "binary {⊤,⊥}"), C(6, "cognitive states ranked 1–6, nous unranked beyond")],
    crossings=[
        X(2, 3, "extra", "Pyrrhonian ε 'between ⊤ and ⊥': the third value beyond the closed binary (corpus)", "🟠"),
        X(6, 7, "return", "Hippocratic critical days: crisis at day 7 and 14, 'based on the number 7 or 4' (corpus; Epidemics I)", "🟡"),
        X(3, 4, "extra", "Cynic: three possessions (cloak, staff, wallet); the cup is the fourth, thrown away — the law run downward", "🟠"),
        X(0, 1, "return", "Stoic ekpyrosis: the Great Year ends and restarts identically ('you have read this sentence infinite times')", "🟢"),
    ],
    residues=[R("the reserve clause appended to every Stoic action; prohairesis as the one thing 'not even Zeus can conquer'", "🟠")],
    devices={"record": ["wax receiving the signet 'without the gold' (Theaetetus 191c)", "urine read in the glass matula (corpus)"], "hull": ["the inner citadel", "Diogenes' pithos"]},
    numbers=[N(7, "passage", "critical day"), N(14, "passage", "critical day"), N(10, "order", "modes"), N(3, "order", "trilemma"), N(4, "order", "humours")],
    notes="Modern computational rewrites; only the critical-day and ekpyrosis items are ancient doctrine.",
)

T(
    id="hellenistic_astrology", name="Hellenistic astrology", family="Mediterranean", region="Alexandria",
    standing="PRIMARY_EVIDENCE",
    sources=["corpus: HELLENISTIC_ASTROLOGY_COMPLETE.md", "dodekatemoria (Babylonian twelfth-parts), recalled; harmonic astrology (Addey) for the novile"],
    closures=[C(12, "signs × 30° = 360"), C(7, "planets in Chaldean order: 2 luminaries + 2 benefics + 2 malefics + Mercury"), C(12, "places / houses"),
              C(36, "decans"), C(144, "dodekatemoria: 12 twelfth-parts of 2°30' per sign", "🟡"), C(5, "Ptolemaic aspects 0/60/90/120/180")],
    crossings=[
        X(12, 13, "return", "profections: 'Age 12: back to the 1st (13th year); 12-year cycle' (corpus)", "🟢"),
        X(6, 7, "extra", "Mercury, the unpaired seventh, 'neutral, takes on the nature of companions' (corpus)", "🟢"),
        X(360, 361, "extra", "cazimi: within 17′ of the sun's centre, 'in the throne' — the one exception inside the combustion zone (corpus)", "🟠"),
    ],
    residues=[R("the septile 360/7 = 51°26′ is not a whole number of degrees: the one harmonic that does not close in the degree (harmonic astrology reads it as fate)", "🟡")],
    devices={"record": ["the chart / wheel"], "hull": ["the places (topoi); 'in the heart of the sun'"]},
    calendar={"charts": [[12, 30], [10, 36], [8, 45], [5, 72], [9, 40]], "year": 360, "residue": "", "intercalation": ""},
    arithmetic={"present": True, "what": "degree arithmetic; Lots; mod-12 profections; aspects as 360/n for n ∈ {1,2,3,4,6}; Kepler adds 5,8,10,12; the novile 360/9 = 40 is a 20th-century chart"},
    numbers=[N(360, "order", "degrees"), N(12, "order", "signs, houses"), N(7, "order", "planets"), N(36, "order", "decans"), N(144, "order", "dodekatemoria"),
             N(30, "order", "degrees per sign"), N(72, "order", "quintile"), N(40, "order", "novile (modern)"), N(13, "passage", "13th year = return"),
             N(8, "passage", "8th place: death"), N(12, "passage", "12th place: bad spirit")],
    notes="The 2.5° twelfth-part is the corpus's own KC144 step (360/144); the (9,40) chart is attested only as the modern novile.",
)

T(
    id="roman", name="Roman religio and calendar", family="Mediterranean", region="Rome",
    standing="PRIMARY_EVIDENCE",
    sources=["Ovid Fasti I–III, Macrobius Sat. I.12–13 (recalled)", "corpus catalog: 'Imperium Sine Fine' (Janus as Pauli-X)"],
    closures=[C(10, "months of the Romulan year = 304 days"), C(12, "months after Numa"), C(6, "Vestals"), C(12, "Salii; Arval brothers"), C(15, "flamines")],
    crossings=[
        X(304, 365, "residue", "the Romulan ten-month year of 304 days left the winter uncounted: about 61 days that were simply not in the calendar (Macrobius I.12)", "🟡"),
        X(12, 13, "residue", "Mercedonius, the intercalary month inserted after February 23", "🟢"),
        X(1, 2, "extra", "Janus, the god who is the gate: two faces, first invoked; the month that opens the year", "🟢"),
        X(0, 1, "withdrawn", "Terminus refused to move when the Capitoline temple was built — the boundary stone that stays inside the new hull (Livy I.55, Ovid Fasti II.667)", "🟢"),
    ],
    residues=[R("61 uncounted winter days", "🟡", "365-304")],
    devices={"record": ["fasti inscribed"], "hull": ["templum as cut-out enclosure", "Vesta's round temple"]},
    numbers=[N(304, "order", "Romulan year"), N(10, "order", "months"), N(12, "order", "months"), N(61, "residue", "uncounted winter"), N(2, "passage", "Janus' faces")],
    notes="The uncounted winter is the crudest residue in the registry: the closed count simply stops and the remainder is not written.",
)

T(
    id="pgm", name="Greek Magical Papyri (PGM)", family="Mediterranean", region="Roman Egypt",
    standing="PRIMARY_EVIDENCE",
    sources=["corpus: PGM_COMPLETE.md; Philosophy.zip PGM KERNEL", "Abraxas page (isopsephy 365), Wikipedia 2026-09-07"],
    closures=[C(7, "vowels = planets = heavens"), C(8, "Ogdoad of pre-creation powers"), C(36, "decans"), C(365, "Abrasax by isopsephy"), C(81, "papyri PGM I–LXXXI")],
    crossings=[
        X(7, 8, "extra", "'seven vowels = seven heavens' then the Ogdoad of pre-creation forces; PGM Kernel: Omega/Saturn 'the limit … the gate of time', the request passed beyond it (corpus)", "🟢"),
        X(0, 1, "return", "palindromes 'create closed magical circuits' (ABLANATHANALBA): closure as a string property (corpus)", "🟠"),
        X(7, 8, "return", "Mithras Liturgy: seven Virgins, seven Pole-Lords, then Helios; stage 8 'return: descend through the spheres' (corpus)", "🟢"),
    ],
    devices={"record": ["lead defixio folded and pierced", "gold/silver lamella"], "hull": ["lamp, bowl, ring", "the mummified cat 'made into an Osiris'"]},
    ladder=[{"count": 8, "what": "seven planetary heavens + Ogdoad"}],
    arithmetic={"present": True, "what": "isopsephy: ΑΒΡΑΣΑΞ = 1+2+100+1+200+1+60 = 365"},
    numbers=[N(365, "order", "Abrasax; Basilides' heavens"), N(7, "order", "vowels/planets"), N(8, "passage", "the eighth beyond the seven"), N(36, "order", "decans")],
)

T(
    id="hermeticism", name="Hermeticism (Corpus Hermeticum, Emerald Tablet, Kybalion)", family="Mediterranean", region="Alexandria",
    standing="PRIMARY_EVIDENCE",
    sources=["corpus: HERMETICISM_COMPLETE.md (CH I ascent; Kybalion 1908 flagged modern)", "Corpus Hermeticum I.24–26; NHC VI,6 Discourse on the Eighth and Ninth (recalled)"],
    closures=[C(7, "spheres / governors, each with a vice"), C(17, "tractates"), C(7, "Kybalion principles (modern)"), C(3, "parts of wisdom")],
    crossings=[
        X(7, 8, "extra", "'above the spheres: eighth sphere, fixed stars … enter with those above, become powers … enter into God' (corpus, CH I.26)", "🟢"),
        X(8, 9, "extra", "Discourse on the Eighth and Ninth: the ascent continues past the ogdoad to the ennead (NHC VI,6)", "🟡"),
        X(3, 4, "extra", "three parts of wisdom '(sometimes: magic/practical operation)' as an optional fourth (corpus)", "🟠"),
    ],
    residues=[R("seven vices left in the spheres on the way up: the residue returned to its shell", "🟠")],
    devices={"record": ["the Emerald Tablet — a text that is a tablet; closes 'what I have said of the operation of the Sun is complete'"], "hull": ["animated statues (Asclepius 24, 37)", "'the Wind carried it in its belly'"]},
    ladder=[{"count": 9, "what": "7 spheres → 8th (fixed stars) → 9th → God"}],
    numbers=[N(7, "order", "spheres"), N(8, "passage", "ogdoadic sphere"), N(9, "passage", "ennead"), N(17, "record", "tractates")],
)

T(
    id="neoplatonism", name="Neoplatonism and theurgy (Plotinus, Iamblichus, Proclus, Chaldean Oracles)", family="Mediterranean", region="Rome / Athens / Syria",
    standing="PRIMARY_EVIDENCE",
    sources=["corpus: NEOPLATONIC_THEURGY_COMPLETE.md; Philosophy.zip NEOPLATONIC HYPERVISOR (Elements of Theology 211 propositions)"],
    closures=[C(3, "hypostases One / Nous / Soul"), C(211, "propositions of Proclus' Elements"), C(7, "vowel string AEEIOUO"), C(12, "Olympians reinterpreted")],
    crossings=[
        X(3, 4, "extra", "the One 'is not the first element within the set of universal existents but the absolute precondition for the instantiation of the set itself' (corpus Hypervisor): the crossing above the countable", "🟠"),
        X(1, 2, "extra", "henads: 'without henads, One too remote … gateway to the One' — the inserted layer that makes the closed One reachable (corpus)", "🟢"),
        X(0, 1, "return", "procession and return (proodos / epistrophē): 'all things turn back to source'", "🟢"),
    ],
    residues=[R("Elements prop. 211: the descended soul 'does not ascend entire' — a residue on return (corpus)", "🟠"), R("matter as 'nearly non-being'", "🟢")],
    devices={"record": ["written names and characters inserted into the statue"], "hull": ["hollow statue 'for insertion of synthemata'; 'God descends into prepared vessel'", "the ochēma, spherical vehicle and 'black box' of the soul (corpus)"]},
    ladder=[{"count": 5, "what": "One → Nous → Psyche → Physis → Matter (corpus list)"}],
    numbers=[N(3, "order", "hypostases"), N(211, "record", "propositions"), N(7, "order", "vowels")],
)

T(
    id="mithraism", name="Mithraic mysteries", family="Mediterranean", region="Roman Empire",
    standing="SECONDARY_SCHOLARSHIP",
    sources=["Mithraism page (Jerome's seven grades), Wikipedia 2026-09-07", "Origen, Contra Celsum VI.22 (ladder of seven gates and the eighth), recalled"],
    closures=[C(7, "grades: Corax, Nymphus, Miles, Leo, Perses, Heliodromus, Pater, each under a planet")],
    crossings=[X(7, 8, "extra", "Celsus' Mithraic ladder: seven gates of seven metals, one per planet, and an eighth gate of the fixed stars", "🟡")],
    devices={"record": ["tauroctony relief"], "hull": ["the mithraeum as cave"]},
    ladder=[{"count": 7, "what": "grades = planets"}],
    numbers=[N(7, "order", "grades"), N(8, "passage", "eighth gate")],
)

# ============================================================================
# C. ABRAHAMIC
# ============================================================================

T(
    id="hebrew_bible", name="Hebrew Bible", family="Abrahamic", region="Israel",
    standing="PRIMARY_EVIDENCE",
    sources=["Genesis 1–2, 5; Numbers 1:47–49; 33; Leviticus 23, 25; 1 Kings 6; Daniel 9 (recalled); Tribe of Levi, Jubilee and Solomon's Temple pages, Wikipedia 2026-09-07", "Ω41 pulse"],
    closures=[C(6, "days of work"), C(12, "tribes"), C(49, "seven sabbaths of years"), C(7, "sabbatical"), C(613, "commandments = 365 + 248"),
              C(10, "commandments"), C(40, "years, days"), C(42, "stations of the Exodus (Num 33)")],
    crossings=[
        X(6, 7, "return", "six days of work, the seventh holy (Gen 2:2–3): the crossing grammar as commandment", "🟢"),
        X(12, 13, "extra", "'the Levites were not numbered among them' (Num 1:47): twelve counted tribes and one set apart; Joseph split into Ephraim and Manasseh keeps the twelve", "🟢"),
        X(49, 50, "return", "'seven sabbaths of years, forty-nine … the fiftieth year … each of you shall return to his own property' (Lev 25:8–10)", "🟢"),
        X(49, 50, "return", "the Omer: forty-nine days counted, Shavuot on the fiftieth", "🟢"),
        X(6, 7, "extra", "the cubit: common cubit 6 palms, Ezekiel's sacred cubit 'a cubit and a handbreadth' = 7 palms; the reed six cubits (Ezek 40:5)", "🟢"),
        X(6, 7, "withdrawn", "the seventh patriarch Enoch, 365 years, 'was not, for God took him' (Gen 5:24): the seventh crosses upward without dying", "🟢"),
    ],
    residues=[R("intercalation: 7 months in 19 years", "🟢", "7/19")],
    devices={"record": ["the two tablets"], "hull": ["the Ark of the Covenant carrying the tablets (2.5 × 1.5 × 1.5)", "Holy of Holies 20³ cube", "Noah's ark 300 × 50 × 30"]},
    calendar={"charts": [[12, 30]], "year": 354, "residue": "intercalary month Adar II", "intercalation": "7 in 19"},
    arithmetic={"present": False, "what": "no positional arithmetic in the text; the numbers are counts and measures"},
    numbers=[N(7, "passage", "seventh day; seventh patriarch"), N(49, "order", "sabbath of sabbaths"), N(50, "passage", "jubilee, Shavuot"), N(42, "passage", "stations = 2·3·7"),
             N(365, "passage", "Enoch's years"), N(777, "passage", "Lamech, father of the flood hero"), N(490, "passage", "Daniel's seventy weeks"),
             N(60, "order", "temple length (1 Kgs 6:2 — 60×20×30 = (6,2,3), the (2,3,6) triple in tens)"), N(20, "order", "temple width; Holy of Holies cube"),
             N(613, "order", "commandments"), N(12, "order", "tribes"), N(120, "order", "Genesis 6:3 lifespan cap = 2 geš"), N(600, "order", "Noah's age = 10 geš"),
             N(930, "residue", "Adam — patriarch ages irregular"), N(1656, "residue", "Adam to flood = 2³·3²·23")],
    negatives=["The antediluvian ages are all irregular; only the 7th (365) and 9th (777) positions are designed. The genealogy is not built on closure numbers."],
    notes="Grammar present in full, arithmetic layer absent: the cleanest evidence that the grammar is lunar-calendrical and precedes scribal arithmetic.",
)

T(
    id="kabbalah", name="Kabbalah (Sefer Yetzirah, Zohar, practical Kabbalah, Hermetic Qabalah)", family="Abrahamic", region="Provence / Spain / Safed",
    standing="PRIMARY_EVIDENCE",
    sources=["corpus: MERKAVAH_HEKHALOT_COMPLETE.md, PRACTICAL_KABBALAH_COMPLETE.md, HERMETIC_QABALAH_COMPLETE.md", "Da'at and Sefer Yetzirah pages, Wikipedia 2026-09-07",
             "Rosh Hashanah 21b / Nedarim 38a (fifty gates), recalled"],
    closures=[C(10, "sefirot — 'ten and not nine, ten and not eleven' (SY 1:4)"), C(22, "letters = 3 mothers + 7 doubles + 12 simples"), C(32, "paths = 10 + 22"),
              C(231, "gates = C(22,2)"), C(72, "names from three 72-letter verses = 216 letters"), C(42, "letter name = 7 lines of 6"), C(27, "letters with the five finals = 3³"),
              C(50, "gates of understanding"), C(36, "hidden righteous (Sanhedrin 97b)", "🟡")],
    crossings=[
        X(10, 11, "extra", "Da'at: 'not a sefirah', an 'empty slot'; Cordovero counts Keter and omits Da'at, Luria the reverse — the eleventh is never seated", "🟢"),
        X(49, 50, "withdrawn", "'fifty gates of understanding were created, and all were given to Moses except one' (RH 21b): the fiftieth withheld", "🟡"),
        X(3, 4, "withdrawn", "four entered Pardes: one died, one went mad, one cut the shoots, Akiva 'entered in peace and left in peace' (Hagigah 14b) — one returns", "🟢"),
        X(6, 7, "extra", "hekhalot: the sixth palace is the illusion test ('water, water'), the seventh is the throne 'from which one must return' (corpus)", "🟢"),
        X(0, 1, "withdrawn", "golem: erase the aleph of EMET and MET (death) remains — the silent first letter is the load-bearing extra (corpus)", "🟢"),
        X(10, 11, "extra", "Hermetic Qabalah / Golden Dawn grade notation n°=m□ sums to 11 for every grade except 0=0 (corpus, computed)", "🟠"),
    ],
    residues=[R("qliphoth, the shells; 777 'world of shells' (corpus)", "🟠"), R("the true pronunciation of the Name 'lost'", "🟡")],
    devices={"record": ["qameot on parchment/silver", "mezuzah scroll with Shaddai visible through the window", "planetary squares 3×3 … 9×9"],
             "hull": ["golem body of virgin earth with the name-parchment in the mouth", "tefillin boxes", "the Ark with the cherubim"]},
    ladder=[{"count": 10, "what": "sefirot"}, {"count": 4, "what": "worlds"}, {"count": 7, "what": "hekhalot"}, {"count": 7, "what": "planetary squares of order 3→9"}],
    arithmetic={"present": True, "what": "gematria in nine methods; magic squares (Saturn 3×3 = 15/45 … Moon 9×9 = 369/3321; Sun 6×6 = 111/666); 26 = 13 + 13; 358 = 358"},
    numbers=[N(10, "order", "sefirot"), N(11, "passage", "Da'at, the abyss"), N(22, "order", "letters"), N(27, "order", "with finals = 3³"), N(32, "order", "paths"),
             N(231, "order", "gates"), N(72, "order", "names"), N(216, "order", "letters of the 72 = 6³"), N(42, "order", "letter name = 7·6"), N(50, "passage", "gate withheld"),
             N(613, "order", "commandments"), N(666, "order", "Sun square total"), N(36, "order", "lamed-vav"), N(7, "passage", "palaces; doubles as 'gates'"),
             N(12, "order", "simples"), N(3, "order", "mothers")],
    notes="The corpus's cleanest statement of the closure guard in any tradition: 'ten and not nine, ten and not eleven'.",
)

T(
    id="christianity", name="Christianity (New Testament, liturgy, Dante)", family="Abrahamic", region="Mediterranean → Europe",
    standing="PRIMARY_EVIDENCE",
    sources=["Revelation 13:18, 21:16–17; John 21:11; Acts 1:26; Number of the beast, 153, Pentecost, New Jerusalem, Divine Comedy pages, Wikipedia 2026-09-07", "Ω41 pulse"],
    closures=[C(12, "apostles"), C(7, "seals, trumpets, bowls, churches, sacraments"), C(144000, "sealed = 12²·1000"), C(33, "cantos per cantica; years"),
              C(150, "psalms; Aves of the rosary"), C(40, "days of Lent; of the flood"), C(3, "days in the tomb")],
    crossings=[
        X(7, 8, "return", "the eighth day: resurrection on the day after the sabbath, 'the first day again'; octagonal baptisteries", "🟢"),
        X(12, 13, "extra", "Judas replaced by Matthias to restore twelve (Acts 1:26); thirteen at the table", "🟢"),
        X(49, 50, "return", "Pentecost: the fiftieth day after Passover / seven weeks and a day", "🟢"),
        X(99, 100, "extra", "Dante: 100 cantos = 1 introductory + 3 × 33; each realm 9 + 1 (nine circles + Lucifer, nine terraces + Eden, nine spheres + Empyrean)", "🟢"),
        X(6, 7, "residue", "666 = T(36) 'falls short of seven three times'; 888 = Jesus by isopsephy, the eighth (Sibylline Oracles I.324)", "🟡"),
        X(16, 17, "extra", "153 fish = T(17); Augustine reads 17 = 10 (law) + 7 (grace)", "🟢"),
    ],
    residues=[R("42 months = 1260 days = 2520/2, the passage reign (Rev 11–13)", "🟢", "1260")],
    devices={"record": ["the scroll with seven seals"], "hull": ["New Jerusalem: length, breadth and height equal, 12,000 stadia, wall 144 cubits", "the tomb; the ark of Noah"]},
    ladder=[{"count": 9, "what": "Dionysius' nine orders in three triads"}, {"count": 10, "what": "Dante: nine heavens + the Empyrean"}],
    arithmetic={"present": True, "what": "isopsephy (666 / 616 / 888); triangular numbers 666 = T(36), 153 = T(17)"},
    numbers=[N(666, "chaos", "beast = T(36)"), N(888, "order", "Jesus"), N(153, "order", "fish = T(17)"), N(144000, "order", "sealed"), N(1260, "passage", "days of the beast's reign = 42·30"),
             N(42, "passage", "months"), N(7, "order", "seals etc."), N(8, "passage", "eighth day"), N(12, "order", "apostles, gates"), N(24, "order", "elders"),
             N(100, "order", "cantos"), N(33, "order", "cantos per cantica"), N(9, "order", "circles, terraces, spheres"), N(50, "passage", "Pentecost"), N(40, "passage", "Lent")],
    notes="Revelation runs on 6 | 7 | 8 explicitly (666 short, 7 complete, 888 renewed) — the same three values the yarrow assigns to old yin, young yang, young yin.",
)

T(
    id="gnosticism", name="Gnosticism (Valentinian, Sethian, Basilides)", family="Abrahamic", region="Alexandria / Rome",
    standing="PRIMARY_EVIDENCE",
    sources=["corpus: GNOSTICISM_COMPLETE.md", "Aeon (Gnosticism) and Abraxas pages, Wikipedia 2026-09-07"],
    closures=[C(30, "aeons in 15 syzygies (Valentinus): ogdoad 8 + 22"), C(7, "archons (or 12) on the planetary spheres"), C(8, "ogdoad"), C(365, "heavens of Basilides = Abraxas"), C(5, "seals / sacraments"), C(114, "sayings of Thomas")],
    crossings=[
        X(29, 30, "withdrawn", "Sophia, 'lowest/last' of the thirty, emanates 'without her consort' → Yaldabaoth 'hidden in a cloud': the last of the closed count breaks the pair and produces the residue", "🟢"),
        X(7, 8, "extra", "seven archons, the ogdoad above them: the ascent passes the seven with passwords to the eighth", "🟢"),
        X(2, 3, "extra", "three kinds of humans; the hylics 'cannot be saved' — the excluded class (corpus)", "🟠"),
    ],
    residues=[R("Yaldabaoth 'an abortion … malformed'; 'part of her trapped in matter, she must be redeemed too'", "🟢")],
    devices={"record": ["the letter that awakens (Hymn of the Pearl)", "Nag Hammadi codices (fold)"], "hull": ["the pleroma 'fullness'", "the cloud hiding Yaldabaoth", "the body as prison", "the bridal chamber"]},
    ladder=[{"count": 30, "what": "aeons"}, {"count": 7, "what": "spheres with passwords"}],
    arithmetic={"present": True, "what": "isopsephy: Abraxas 365; Marcosian 888"},
    numbers=[N(30, "order", "aeons"), N(365, "order", "heavens"), N(7, "passage", "archons to pass"), N(8, "passage", "ogdoad"), N(114, "record", "sayings"), N(5, "order", "seals")],
    notes="Textbook 'the excluded one causes breakdown', with the residue (the demiurge) named as the cosmos itself.",
)

T(
    id="islam", name="Islam (Qur'an, ḥajj, Twelver and Sevener Shīʿa)", family="Abrahamic", region="Arabia →",
    standing="PRIMARY_EVIDENCE",
    sources=["Quran (114/30/60/7), Names of God (99 + the greatest name), Hajj (7/7/7), Kaaba (360 idols), Seven Sleepers (18:22), Muhammad al-Mahdi pages, Wikipedia 2026-09-07"],
    closures=[C(99, "names of God"), C(114, "suras = 2·3·19"), C(30, "juzʼ"), C(60, "ḥizb"), C(7, "manzil; heavens; tawaf; saʿy; pebbles per pillar"), C(5, "pillars; daily prayers"),
              C(12, "Imams (Twelver)"), C(28, "abjad letters = 4·7"), C(360, "idols around the Kaaba before the conquest (Bukhari 4287)"), C(19, "'over it are nineteen' (74:30)")],
    crossings=[
        X(99, 100, "extra", "'traditionally enumerated as 99, to which is added as the highest name (al-ism al-aʿẓam)' — the hundredth hidden", "🟢"),
        X(11, 12, "withdrawn", "the twelfth Imam in occultation since 941: the last of the closed count hidden; the Seveners hide the seventh", "🟢"),
        X(7, 8, "extra", "Qur'an 18:22: 'three, the fourth their dog; five, the sixth their dog; seven and the eighth their dog' — the n+1 is the guardian animal at every count", "🟢"),
        X(33, 34, "extra", "tasbīḥ of Fāṭima 33 + 33 + 34 = 100; the bead-string's marker bead (imām) not counted", "🟡"),
        X(360, 361, "withdrawn", "360 idols, 'one for each day', all broken at the conquest: the old closed count emptied", "🟢"),
    ],
    residues=[R("the lunar year of 354 days is left to wander against the sun (no intercalation after 9:36–37)", "🟢", "11 days/yr")],
    devices={"record": ["muṣḥaf; the Preserved Tablet (85:22)"], "hull": ["the Kaaba (cube) circled seven times", "the cave of the Sleepers"]},
    ladder=[{"count": 7, "what": "heavens of the Miʿrāj"}],
    calendar={"charts": [], "year": 354, "residue": "uncorrected drift", "intercalation": "forbidden"},
    arithmetic={"present": True, "what": "abjad numerals (28 letters, 1…1000); 786 = basmala; 66 = Allāh; 92 = Muḥammad"},
    numbers=[N(99, "order", "names"), N(100, "passage", "the hidden name"), N(114, "order", "suras"), N(19, "order", "74:30; suras = 6·19"), N(7, "order", "tawaf, saʿy, heavens"),
             N(49, "order", "7 pebbles × 7 throws (varies)"), N(360, "chaos", "idols"), N(12, "order", "Imams"), N(28, "order", "abjad letters"), N(354, "residue", "lunar year"),
             N(40, "passage", "age of prophethood"), N(786, "order", "basmala")],
    notes="99|100 is the registry's cleanest 'hidden (n+1)th' with the source itself using the word 'added'.",
)

T(
    id="sufism", name="Sufism", family="Abrahamic", region="Islamic world",
    standing="PRIMARY_EVIDENCE",
    sources=["corpus: SUFI_MYSTICISM_COMPLETE.md"],
    closures=[C(7, "maqāmāt; aḥwāl"), C(3, "sharīʿa / ṭarīqa / ḥaqīqa"), C(99, "names"), C(33, "tasbīḥ count × 3"), C(40, "days of the chilla; the abdāl"), C(1001, "days of the Mevlevi chille = 7·11·13", "🟡")],
    crossings=[
        X(99, 100, "extra", "'the 100th hidden name: synthesis of all' (corpus)", "🟢"),
        X(3, 4, "return", "three fanāʾ then baqāʾ, 'after fana, return, but transformed'; maʿrifa as the fourth beyond the triad (corpus)", "🟢"),
        X(40, 41, "centre", "forty abdāl and the one quṭb, the pole at the centre of the hierarchy of saints", "🟡"),
    ],
    devices={"record": ["talisman with magic square and verse, 'seal and preserve'", "the wird"], "hull": ["the heart 'swept clean, presence installed'", "the black cloak removed in the semāʿ"]},
    ladder=[{"count": 7, "what": "stations"}, {"count": 7, "what": "planetary squares 3→9 with sums 15, 34, 65, 111, 175, 260, 369"}],
    arithmetic={"present": True, "what": "abjad; Budūḥ 3×3 = 15; planetary squares"},
    numbers=[N(99, "order", "names"), N(100, "passage", "hidden name"), N(7, "order", "stations"), N(40, "passage", "chilla, abdāl"), N(1001, "passage", "chille days"), N(15, "order", "Budūḥ sum")],
)

T(
    id="bahai", name="Baháʼí calendar", family="Abrahamic", region="Iran →",
    standing="PRIMARY_EVIDENCE",
    sources=["Baháʼí calendar page, Wikipedia 2026-09-07"],
    closures=[C(361, "19 months × 19 days"), C(19, "váḥid = 19 years"), C(361, "kull-i-shayʼ = 19² years")],
    crossings=[X(361, 365, "residue", "Ayyám-i-Há: 4 or 5 intercalary days between the 18th and 19th months", "🟢")],
    residues=[R("4–5 intercalary days", "🟢", "365-361")],
    calendar={"charts": [[19, 19]], "year": 361, "residue": "4/5 Ayyám-i-Há", "intercalation": "annual"},
    numbers=[N(361, "order", "19²"), N(19, "order", "váḥid"), N(4, "residue", "Ayyám-i-Há"), N(5, "residue", "leap Ayyám-i-Há")],
    notes="A modern designed calendar that lands on 361 = 360 + 1 with the residue placed just before the last month — the same shape as the Go board's 361.",
)

T(
    id="enoch_jubilees", name="Enochic / Jubilees 364-day calendar", family="Abrahamic", region="Judea (Qumran)",
    standing="PRIMARY_EVIDENCE",
    sources=["1 Enoch 72–82; Jubilees 6 (recalled); Enoch calendar page, Wikipedia 2026-09-07"],
    closures=[C(364, "days = 52 weeks = 4 × 91 = 12 × 30 + 4"), C(91, "days per season = 7·13"), C(52, "weeks")],
    crossings=[X(360, 364, "residue", "12 months of 30 + four added days, 'the four leaders of the stars' at the quarters; 1 Enoch 82:4–6 says people err by not counting them", "🟢"),
               X(364, 365, "residue", "the 364-day year deliberately ignores the 365th day to keep the sabbath fixed; the residue is refused, not absorbed", "🟢")],
    residues=[R("4 quarter-days added; ~1.25 days/yr left to drift", "🟢", "4")],
    calendar={"charts": [[4, 91], [12, 30]], "year": 364, "residue": "4 quarter days", "intercalation": "none"},
    numbers=[N(364, "order", "year = 2²·7·13"), N(91, "order", "season = 7·13"), N(4, "residue", "added days"), N(52, "order", "weeks")],
    notes="Ifá's 364 (Ω43 🟡) and Dee's 91 governors (Enochian, below) share this arithmetic: 364 = 4 · 91 = 4 · 7 · 13.",
)

# ============================================================================
# D. INDIA
# ============================================================================

T(
    id="vedic", name="Vedic and Purāṇic India", family="India", region="India",
    standing="PRIMARY_EVIDENCE",
    sources=["RV 1.164.11, 48 (recalled); Kali Yuga, Berossus, Nakshatra, Thirty-three gods, Bhagavad Gita pages, Wikipedia 2026-09-07", "corpus: San_tana_Ga_ita docx (jyotiṣa formalisation)", "Ω39 pulse"],
    closures=[C(360, "pegs of the wheel, RV 1.164.48"), C(720, "sons in pairs = days and nights, RV 1.164.11"), C(33, "devas = 8 Vasus + 11 Rudras + 12 Ādityas + 2"),
              C(27, "nakṣatras = 3³"), C(108, "= 27 × 4 pādas = 12 × 9 navāṃśas"), C(4, "yugas 4:3:2:1"), C(432000, "Kali = 2·60³"), C(4320000, "mahāyuga"),
              C(18, "chapters of the Gītā, parvas, days of the war"), C(6, "seasons of 60 days"), C(7, "ṛṣis; lokas")],
    crossings=[
        X(27, 28, "extra", "Abhijit, the 28th nakṣatra, 'intercalary', 'left out without a portion' when the 27 were made equal, kept for muhūrta", "🟢"),
        X(7, 9, "extension", "navagraha: the seven visible bodies + the two shadow planets Rāhu and Ketu (nodes) — two invisible members complete the count; corpus: 'topological defects where the logic breaks down'", "🟢", marked=True),
        X(12, 13, "centre", "corpus jyotiṣa: '12 outer generators (the rāśis), 1 central charge (the lagna / observer)' — the observer as the +1 at the centre", "🟠"),
        X(10, 11, "centre", "eleven Rudras = 'the 10 directions of space plus the centre (or the self)' (corpus)", "🟠"),
        X(6, 7, "return", "the seventh loka satya, the passage upward; the seventh antediluvian king / Enoch parallel in Ω34", "🟠"),
    ],
    residues=[R("adhika māsa, the intercalary month (7 in 19)", "🟢", "7/19"), R("corpus: karma as 'the residue of non-commuting operations', bhasma the ash", "🟠")],
    devices={"record": ["palm-leaf; the chart (kuṇḍalī)", "corpus: 'the Akashic record as vacuum phase'"], "hull": ["hiraṇyagarbha, the golden egg", "Manu's ship", "the Agnicayana altar of 10,800 bricks (Śatapatha), 'Prajāpati is the year'"]},
    ladder=[{"count": 4, "what": "yugas 1,728,000 : 1,296,000 : 864,000 : 432,000 = 8:6:4:2 šar-gal"}, {"count": 7, "what": "lokas"}, {"count": 14, "what": "manvantaras per kalpa"}],
    oracle=None,
    calendar={"charts": [[6, 60], [12, 30]], "year": 360, "residue": "adhika māsa", "intercalation": "7 in 19"},
    arithmetic={"present": True, "what": "decimal place value; 432,000 = 12 × 36 × 1000 syllables (Śatapatha Br. X.4.2); yuga arithmetic"},
    numbers=[N(360, "order", "pegs"), N(720, "order", "days+nights"), N(33, "order", "devas"), N(27, "order", "nakṣatras = 3³"), N(28, "passage", "with Abhijit"), N(108, "order", "pādas"),
             N(432000, "order", "Kali yuga = 2·60³"), N(1728000, "order", "Kṛta = 120³ = ark volume"), N(1296000, "order", "Tretā = 360 šar"), N(864000, "order", "Dvāpara"),
             N(10800, "order", "altar bricks = 30·360"), N(7, "passage", "ṛṣis; seventh loka"), N(14, "passage", "Manus per kalpa"), N(9, "order", "grahas"), N(18, "order", "Gītā chapters"),
             N(120, "order", "Vimśottarī cycle = 5·24"), N(21600, "order", "arc-minutes; breaths"), N(3339, "order", "gods of RV 3.9.9 = 3²·7·53")],
    negatives=["The 33 gods carry 11 in the order column; 11 is not part of the invariant core."],
)

T(
    id="samkhya_yoga", name="Sāṃkhya and Yoga", family="India", region="India",
    standing="PRIMARY_EVIDENCE",
    sources=["Samkhya page, Wikipedia 2026-09-07 (25 tattvas; puruṣa 'the witness-consciousness')", "Yogasūtra II.29 (recalled)", "corpus: HINDU_TANTRA (36 tattvas)"],
    closures=[C(24, "tattvas of prakṛti"), C(25, "with puruṣa"), C(8, "limbs of yoga"), C(36, "tattvas of Kashmir Śaivism = 6²"), C(3, "guṇas")],
    crossings=[X(24, 25, "extra", "'the twenty-fifth tattva, the puruṣa': the witness (sākṣī) that does not act, set apart from the twenty-four that do", "🟢"),
               X(3, 4, "extra", "turīya, 'the fourth', beyond waking, dream and sleep (Māṇḍūkya Up. 7); corpus: 'root access / kernel mode'", "🟢")],
    devices={"record": [], "hull": ["the body as field (kṣetra)"]},
    ladder=[{"count": 8, "what": "aṣṭāṅga"}, {"count": 36, "what": "tattvas Śiva → pṛthivī"}],
    numbers=[N(24, "order", "tattvas"), N(25, "passage", "puruṣa the witness"), N(4, "passage", "turīya"), N(36, "order", "tattvas"), N(8, "order", "limbs")],
    notes="The witness seat stated as doctrine: the (n+1)th is exactly the one that observes and does not act.",
)

T(
    id="tantra", name="Hindu Tantra (Śrī Vidyā, Kuṇḍalinī, mantra)", family="India", region="India",
    standing="TRADITION_INTERNAL",
    sources=["corpus: HINDU_TANTRA_COMPLETE.md", "Japa mala and Chakra pages, Wikipedia 2026-09-07 (guru bead not crossed; sahasrāra 'not regarded as a chakra')"],
    closures=[C(108, "mālā beads"), C(6, "cakras of the Ṣaṭcakranirūpaṇa, petals 4+6+10+12+16+2 = 50"), C(50, "mātṛkā letters"), C(1000, "petals of the crown = 20 × 50"),
              C(43, "triangles of the Śrī Yantra from 9 interlaced"), C(9, "āvaraṇas"), C(72000, "nāḍīs"), C(16, "kalās of the moon", "🟡"), C(64, "yoginīs, tantras, kalās")],
    crossings=[
        X(108, 109, "extra", "the meru / guru bead: 'not used for counting; counting begins and ends beside it; rather than crossing it the mālā is turned' — the uncounted 109th that may not be crossed, and forces the return", "🟢"),
        X(6, 7, "extra", "six cakras and the sahasrāra 'not technically a cakra … the lotus that never closes' (corpus); the six lower petal-counts sum to the fifty letters", "🟢"),
        X(15, 16, "withdrawn", "the sixteenth kalā of the moon, amṛtā, the one that never wanes (Tantric/Purāṇic; recalled)", "🟡"),
        X(4, 5, "extra", "visarga (16th vowel) 'expansion, Śiva' after bindu (15th) (corpus)", "🟠"),
    ],
    residues=[R("amṛta 'drips from bindu, caught or burned' — lost unless caught (corpus)", "🟠"), R("3½ coils of kuṇḍalinī: the half coil", "🟢")],
    devices={"record": ["yantra on bhūrja bark / copper (flat, bhūprastara)", "nyāsa on the body"], "hull": ["meru (raised yantra)", "bhūpura square with four gates", "'body is temple'", "kumbhaka + bandhas = 'complete sealing'"]},
    ladder=[{"count": 7, "what": "cakras"}, {"count": 36, "what": "tattvas"}, {"count": 5, "what": "puraścaraṇa 600,000 → 60 by ÷10"}],
    oracle=None,
    arithmetic={"present": True, "what": "108 = 27·4 = 12·9; 50 × 20 = 1000; ratio breathing 1:4:2"},
    numbers=[N(108, "order", "beads"), N(109, "passage", "meru bead"), N(50, "order", "letters = petals"), N(7, "passage", "the crown beyond six"), N(43, "order", "Śrī Yantra triangles"),
             N(72000, "order", "nāḍīs"), N(16, "order", "kalās"), N(64, "order", "yoginīs"), N(1000, "order", "crown petals")],
    notes="The meru bead is the physical statement of the whole law: closed count, uncounted summit, no crossing, mandatory turn.",
)

T(
    id="buddhism", name="Buddhism (Theravāda, Mahāyāna)", family="India", region="India →",
    standing="PRIMARY_EVIDENCE",
    sources=["Twelve Nidānas, Bhūmi, Bardo pages, Wikipedia 2026-09-07 (49 days: Mahāvibhāṣā, Abhidharmakośa 'seven times seven')"],
    closures=[C(4, "truths"), C(8, "fold path"), C(12, "nidānas"), C(10, "bhūmis"), C(37, "factors of awakening = 4+4+4+5+5+7+8"), C(108, "defilements"), C(84000, "dharma doors = 2⁵·3·5³·7"), C(49, "days of the intermediate state = 7²"), C(31, "planes"), C(6, "realms")],
    crossings=[X(10, 11, "extra", "the eleventh bhūmi (Samantaprabha) and beyond in Vajrayāna/Dzogchen: the ten close, tantra adds the 'universal light'", "🟢"),
               X(12, 13, "return", "the twelfth link (aging-and-death) feeds the first (ignorance): the chain drawn as a wheel", "🟢", marked=True),
               X(48, 49, "return", "'seven times seven days at most' — the rebirth after the 49th", "🟢")],
    devices={"record": ["palm-leaf sūtra; the wheel of life painted"], "hull": ["stūpa", "the wheel"]},
    ladder=[{"count": 10, "what": "bhūmis"}, {"count": 31, "what": "planes"}],
    numbers=[N(12, "order", "nidānas"), N(49, "passage", "bardo days = 7²"), N(84000, "order", "dharma doors (carries 7)"), N(37, "order", "bodhipakṣa"), N(108, "order", "defilements"), N(10, "order", "bhūmis"), N(11, "passage", "bhūmi beyond ten")],
)

T(
    id="tibetan_vajrayana", name="Tibetan Vajrayāna (Kālacakra, Bardo Thödol)", family="India", region="Tibet",
    standing="TRADITION_INTERNAL",
    sources=["corpus: TIBETAN_VAJRAYANA_COMPLETE.md", "Bardo page (49 days), Wikipedia 2026-09-07; 42 peaceful + 58 wrathful = 100 deities (recalled 🟡)"],
    closures=[C(3, "kāyas"), C(4, "empowerments"), C(6, "bardos"), C(5, "Buddha families = 4 directions + centre"), C(49, "days = 7·7"), C(100, "peaceful and wrathful deities = 42 + 58", "🟡"),
              C(360, "Kālacakra: 12 × 30 breath-units; 21,600 breaths a day = 60 × 360", "🟡"), C(84, "mahāsiddhas = 12·7"), C(21, "Tārās = 3·7"), C(9, "yānas (Nyingma)")],
    crossings=[X(3, 4, "extra", "'the fourth empowerment (caturthābhiṣeka)', result svabhāvikakāya 'beyond the three kāyas', seat 'beyond chakras' (corpus)", "🟢"),
               X(3, 4, "return", "dissolution: white, red, black, then 'clear light (the actual moment of death)' — three then the fourth (corpus)", "🟢"),
               X(4, 5, "centre", "five Buddha families: four directions around Vairocana at the centre of the maṇḍala", "🟢"),
               X(48, 49, "return", "49 days = 7 × 7 then rebirth", "🟢")],
    residues=[R("rainbow body leaves 'only hair and nails' (corpus)", "🟢"), R("the indestructible drop 'never destroyed until enlightenment' — the unit that does not dissolve (corpus)", "🟢")],
    devices={"record": ["maṇḍala drawn; terma hidden texts; seed syllables"], "hull": ["celestial palace with four gates", "protection wheel", "the vase", "the heart holding the indestructible drop"]},
    ladder=[{"count": 4, "what": "tantra classes"}, {"count": 9, "what": "yānas"}, {"count": 6, "what": "bardos as a cycle"}],
    numbers=[N(49, "passage", "bardo = 7²"), N(42, "passage", "peaceful deities = 2·3·7"), N(58, "passage", "wrathful"), N(100, "order", "deities"), N(84, "order", "mahāsiddhas"), N(21, "order", "Tārās"),
             N(360, "order", "Kālacakra wheel"), N(21600, "order", "breaths"), N(4, "passage", "the fourth empowerment"), N(5, "order", "families"), N(14, "passage", "days of the bardo of dharmatā (corpus)")],
)

T(
    id="jain", name="Jainism", family="India", region="India",
    standing="PRIMARY_EVIDENCE",
    sources=["Jain cosmology page, Wikipedia 2026-09-07"],
    closures=[C(24, "tīrthaṅkaras"), C(63, "śalākāpuruṣas = 24 + 12 + 9 + 9 + 9"), C(6, "aras per half-cycle"), C(14, "guṇasthānas"), C(14, "rajlok height"), C(6, "dravyas")],
    crossings=[X(14, 15, "extra", "fourteen guṇasthānas are stages in the body; the siddha beyond them is not a stage", "🟠"),
               X(6, 7, "return", "six aras descend, then six ascend: the wheel turns at the sixth", "🟢")],
    ladder=[{"count": 14, "what": "guṇasthānas"}, {"count": 12, "what": "aras of the full wheel"}],
    numbers=[N(24, "order", "tīrthaṅkaras"), N(63, "order", "illustrious beings"), N(14, "order", "stages, rajlok"), N(6, "order", "aras")],
)

T(
    id="sikh", name="Sikhism", family="India", region="Punjab",
    standing="PRIMARY_EVIDENCE",
    sources=["Guru Granth Sahib as eternal Guru (1708), recalled"],
    closures=[C(10, "human Gurus"), C(5, "Ks; the Pañj Piāre"), C(1430, "aṅgs of the Guru Granth Sahib")],
    crossings=[X(10, 11, "extra", "ten human Gurus close the line; Guru Gobind Singh installs the scripture as the eleventh and eternal Guru (1708)", "🟢"),
               X(4, 5, "extra", "the Pañj Piāre: five beloved ones, the fifth completing the Khalsa's founding (1699)", "🟠")],
    devices={"record": ["the Granth itself, the book as Guru"], "hull": ["the Harmandir with four doors"]},
    numbers=[N(10, "order", "Gurus"), N(11, "passage", "the book as Guru"), N(5, "order", "Ks"), N(1430, "record", "pages")],
    notes="A tradition that seats the (n+1)th deliberately: the record (the book) becomes the crossing element.",
)

# ============================================================================
# E. EAST ASIA
# ============================================================================

T(
    id="i_ching", name="I Ching (Zhouyi and the Ten Wings)", family="East Asia", region="China",
    standing="PRIMARY_EVIDENCE",
    sources=["I Ching divination page, Wikipedia 2026-09-07 (50 stalks, one set aside; 1/16, 5/16, 7/16, 3/16)", "Hexagram 24 Judgment 反復其道，七日來復 (recalled); 用九/用六", "corpus: DAO_SU docx (Q₆, King Wen pairs, nuclear hexagrams, Fuxi carry 31→32)", "Ω38 pulse"],
    closures=[C(64, "hexagrams = 2⁶"), C(8, "trigrams"), C(6, "lines"), C(50, "stalks of the great expansion"), C(49, "used = 7²"), C(18, "changes per hexagram = 3·6"),
              C(36, "shapes under reversal = 6²"), C(28, "reversal pairs + 4 complement pairs = 32 in King Wen"), C(8, "palindromic hexagrams")],
    crossings=[
        X(6, 7, "return", "'on the seventh day comes the return' (Fu, hex 24); Wilhelm's gloss: seven is six exhausted plus one", "🟢"),
        X(49, 50, "extra", "'fifty yarrow stalks are used, though one stalk is set aside at the beginning' — the witness stalk", "🟢"),
        X(6, 7, "extra", "only Qian and Kun carry a seventh line-statement, 用九 'use the nines' and 用六 'use the sixes' — the seventh text is the two poles' overflow", "🟢"),
        X(63, 64, "return", "corpus Dao Su: hex 64 'the configuration that necessitates a reboot of the beginning'; Fuxi carry 011111 → 100000 as 'system shock'", "🟠"),
        X(8, 9, "centre", "corpus Dao Su: the 3-cube's centre (½,½,½) 'equidistant from all 8 trigrams … the Taiji core, around which the 8 states rotate'", "🟠"),
    ],
    residues=[R("yarrow remainders removed at each change; χ = 1/64 (corpus) as the quantum of change", "🟠"), R("corpus: 64 − 21 = 43 spare codon states (DNA isomorphism, marked 'convergent, not causal')", "🟠")],
    devices={"record": ["bamboo strips bound and rolled (卷); the oracle-bone plastron cracked to be read"], "hull": ["the gourd of Fuxi and Nüwa", "the tortoise shell"]},
    oracle={"states": 64, "encoding": "6 bits, bottom = LSB", "set_aside": "1 of 50", "symmetry": "complement (錯) and reversal (綜) generate V₄; 36 reversal classes, 20 V₄ orbits; nuclear hexagram discards lines 1 and 6",
            "line_values": {"6": "1/16", "7": "5/16", "8": "7/16", "9": "3/16"}},
    calendar=None,
    arithmetic={"present": True, "what": "binary (Shao Yong / Fuxi order); yarrow arithmetic with remainders 5/9, 4/8; Hamming weights 1,6,15,20,15,6,1"},
    numbers=[N(64, "order", "hexagrams"), N(50, "order", "great expansion"), N(49, "order", "used = 7²"), N(7, "passage", "seventh day return; young yang 5/16"), N(6, "passage", "old yin, moving"),
             N(9, "passage", "old yang, moving"), N(8, "order", "young yin 7/16; trigrams"), N(18, "order", "changes"), N(36, "order", "shapes"), N(24, "passage", "hexagram Fu (Return)")],
    notes="The law is stated as doctrine here; the oracle's own number system is 6|7|8|9 with 7² stalks in hand and one set aside.",
)

T(
    id="taoism_china", name="Taoist religion, Chinese calendar and cosmography", family="East Asia", region="China",
    standing="PRIMARY_EVIDENCE",
    sources=["corpus: TAOIST_MAGIC_COMPLETE.md; DAO_SU docx (Lo Shu, He Tu, Flying Star, Luo Pan 24 mountains)", "Sexagenary cycle, Twenty-Eight Mansions, Solar term, Lo Shu, Water Margin, Tao Te Ching, Japanese calendar pages, Wikipedia 2026-09-07",
             "Qijing Shisanpian on the Go board (recalled 🟡); Taoist nine-star Dipper 輔弼 (recalled 🟡)"],
    closures=[C(60, "sexagenary = lcm(10,12), half the stem–branch torus"), C(24, "solar terms of 15°"), C(72, "pentads of 5 days"), C(8, "principal terms 45° apart"), C(28, "mansions = 4 × 7"),
              C(5, "phases"), C(9, "palaces of the Lo Shu, magic sum 15, centre 5"), C(81, "chapters of the Tao Te Ching = 9² (Han standardisation)"), C(108, "= 36 heavenly + 72 earthly stars"),
              C(361, "points of the Go board = 19²"), C(10000, "the ten-thousand things = totality at the fourth place"), C(3, "dantian")],
    crossings=[
        X(4, 5, "centre", "four directional phases around Earth at the centre; the Lo Shu's 5 at the centre; corpus Dao Su: 'the pivot, the CPU around which the peripheral 1–9 rotate'", "🟢"),
        X(360, 361, "centre", "Go board: 361 points = 360 + the centre (tiānyuán); the Qijing reads 360 as the days of heaven, four quarters of 90 for the seasons, the outer 72 for the pentads", "🟡"),
        X(7, 9, "extension", "the Northern Dipper as nine stars: seven visible and two hidden (輔 and 弼) — the Taoist completion of 7 to 9 with invisible members, as in the navagraha", "🟡", marked=True),
        X(3, 4, "extra", "three dantian and the niwan at the crown, 'exit point for spirit'; three neidan stages and a fourth 'refine emptiness and merge with Dao' (corpus)", "🟢"),
        X(5, 6, "residue", "the Six Classics became Five when the Classic of Music was lost — a canonical count with its residue marked by absence", "🟡"),
        X(12, 13, "residue", "7 intercalary months in 19 years (章)", "🟢"),
    ],
    residues=[R("7 in 19", "🟢", "7/19"), R("Jing Fang: 53 fifths nearly close; he extended to 60 lü, finding after 53 'incredibly close' values (Mercator's comma 177147/176776)", "🟢"),
              R("corpus talisman: one broken stroke voids the whole (fu written 'in one continuous action')", "🟢")],
    devices={"record": ["fu talisman on yellow paper: header / body / seal", "bamboo roll 卷", "oracle bone", "the bagua mirror (stored negative)"], "hull": ["gourd", "altar 'seal the space'", "the body as furnace (lower dantian)"]},
    ladder=[{"count": 4, "what": "1 → 10 → 100 → 1000 → 萬 (totality at the fourth place)"}, {"count": 3, "what": "Pure Ones / heavens"}, {"count": 9, "what": "Flying Star periods of 20 = 180-year cycle (corpus)"}],
    oracle=None,
    calendar={"charts": [[24, 15], [72, 5], [8, 45], [12, 30]], "year": 360, "residue": "7 intercalary in 19", "intercalation": "7 in 19"},
    arithmetic={"present": True, "what": "decimal rod numerals; Lo Shu; lcm(10,12) = 60 reached independently of Babylon; 19² = 361; 4·19 − 4 = 72"},
    numbers=[N(60, "order", "cycle"), N(24, "order", "terms"), N(72, "order", "pentads; earthly stars"), N(36, "order", "heavenly stars"), N(108, "order", "stars"), N(28, "order", "mansions = 4·7"),
             N(15, "order", "Lo Shu sum"), N(5, "order", "centre"), N(9, "order", "palaces; supreme yang; Dipper with the hidden two"), N(81, "record", "chapters = 9²"), N(361, "order", "Go points"),
             N(7, "order", "visible Dipper stars"), N(19, "order", "章 cycle"), N(53, "residue", "fifths of Jing Fang's near-closure")],
    notes="China supplies an independent 60, the 4+centre seat, and the 360+1 board with its own commentary.",
)

T(
    id="shinto_japan", name="Shintō and Japanese calendar", family="East Asia", region="Japan",
    standing="PRIMARY_EVIDENCE",
    sources=["Imperial Regalia (mirror at Ise; Amaterasu's cave), Yaoyorozu no Kami, Japanese calendar pages, Wikipedia 2026-09-07"],
    closures=[C(3, "regalia: mirror, sword, jewel"), C(8, "'eight million' kami = innumerable; eight islands; eight-headed Orochi"), C(24, "sekki"), C(72, "kō"), C(88, "Shikoku temples", "🟡"), C(33, "Kannon pilgrimage", "🟡")],
    crossings=[X(0, 1, "return", "Amaterasu withdrawn into the cave is drawn out by her own reflection in the mirror: the withdrawn one returns through the stored image", "🟢"),
               X(4, 5, "centre", "the mirror kept boxed and unseen at Ise: the record hidden inside the hull, viewed by no one", "🟠")],
    devices={"record": ["the mirror Yata no Kagami — 'the image stored'"], "hull": ["the cave", "the boxes in which the regalia are never shown"]},
    calendar={"charts": [[24, 15], [72, 5]], "year": 360, "residue": "", "intercalation": "Chinese"},
    numbers=[N(8, "order", "'many'"), N(3, "order", "regalia"), N(24, "order", "sekki"), N(72, "order", "kō")],
)

T(
    id="shamanism_siberian_core", name="Siberian shamanism and 'core shamanism'", family="Steppe / Circumpolar", region="Siberia; modern (Harner)",
    standing="MODERN_RECONSTRUCTION",
    sources=["corpus: CORE_SHAMANISM_COMPLETE.md (Eliade's list; 'extra bone = sign of shaman')", "Buryat/Yakut nine- or seven-notched pole (Eliade), recalled"],
    closures=[C(3, "worlds joined by the axis"), C(8, "Eliade's core elements"), C(9, "notches of the Buryat shaman's tree; heavens", "🟡"), C(7, "heavens (Yakut variant)", "🟡")],
    crossings=[X(0, 1, "extra", "'bones counted / extra bone = sign of shaman' (corpus): the initiate is the body with one bone more", "🟡"),
               X(3, 4, "centre", "three worlds and the world tree / pole as the fourth thing, the axis at the centre", "🟠")],
    residues=[R("extraction leaves a hole: 'must fill where intrusion was, otherwise new intrusion possible' (corpus)", "🟡")],
    devices={"record": ["the drum skin painted with the cosmos"], "hull": ["the drum", "the tent with the smoke hole as exit"]},
    ladder=[{"count": 9, "what": "notches / heavens", "grade": "🟡"}],
    numbers=[N(3, "order", "worlds"), N(9, "passage", "notches"), N(7, "passage", "heavens")],
)

# ============================================================================
# F. NORTHERN AND WESTERN EUROPE
# ============================================================================

T(
    id="norse", name="Norse / Germanic", family="Northern Europe", region="Scandinavia",
    standing="PRIMARY_EVIDENCE",
    sources=["corpus: NORSE_RUNIC_COMPLETE.md (18 songs, '18. secret spell (never told)'; 9 nights; 24 = 3·8)", "Elder Futhark, Hávamál, Draupnir, Nine Worlds, Long hundred, Loki pages, Wikipedia 2026-09-07", "Ω42 pulse"],
    closures=[C(24, "runes = 3 ættir × 8"), C(16, "Younger Futhark"), C(9, "worlds; nights on the tree"), C(8, "Sleipnir's legs; rings per ninth night"), C(18, "charms of the Ljóðatal"),
              C(120, "the long hundred"), C(540, "doors of Valhalla"), C(800, "warriors per door")],
    crossings=[
        X(8, 9, "return", "Draupnir: 'every ninth night eight gold rings of equal weight' — the closure delivered at the crossing", "🟢"),
        X(17, 18, "withdrawn", "seventeen charms told; the eighteenth 'I never will tell to maiden or man's wife' (Hávamál 163)", "🟢"),
        X(8, 9, "extra", "eight worlds and Hel the ninth; nine nights on the windy tree then 'I fell back from there' (Hávamál 138–139)", "🟢"),
        X(12, 13, "extra", "Loki arrives uninvited at Ægir's feast (Lokasenna) — the excluded guest; the '13th guest' count is not in the sources", "🟡"),
    ],
    residues=[R("Younger Futhark 24 → 16: 'less phonetically precise' (corpus)", "🟢"), R("Valhalla 540 × 800 = 432,000 only under the decimal reading; under the long hundred 640 × 960 = 614,400", "🟡")],
    devices={"record": ["runestone", "bracteate"], "hull": ["ship burial (Oseberg, Gokstad)", "Naglfar", "the mead vessel Óðrerir"]},
    ladder=[{"count": 9, "what": "worlds on Yggdrasil"}, {"count": 3, "what": "ættir"}],
    oracle={"states": 24, "encoding": "runes drawn; symmetric runes have no reversal (corpus lists 9 while saying 8)", "set_aside": "", "symmetry": "reversal"},
    arithmetic={"present": True, "what": "the long hundred 120 = SHCN between 60 and 360"},
    numbers=[N(24, "order", "runes"), N(16, "order", "Younger"), N(9, "passage", "nights, worlds"), N(8, "order", "ætt; rings"), N(18, "passage", "the untold charm"), N(120, "order", "long hundred"),
             N(540, "order", "doors = 9·60"), N(800, "order", "warriors"), N(432000, "order", "einherjar (decimal reading)"), N(13, "passage", "the uninvited (🟡)")],
    notes="Closes at 8, crosses at 9: the ternary crossing number, with the law delivered in one object (Draupnir).",
)

T(
    id="celtic_druid", name="Celtic (Ogham, Coligny, provinces) and modern Druidry", family="Northern Europe", region="Ireland / Gaul / Britain",
    standing="PRIMARY_EVIDENCE",
    sources=["Ogham, Coligny calendar, Provinces of Ireland pages, Wikipedia 2026-09-07", "corpus: DRUIDRY_COMPLETE.md (modern, self-flagged 'ancient fragmentary / modern revived')", "Diodorus II.47 (Hyperborean Apollo, 19 years), recalled"],
    closures=[C(20, "Ogham letters in four aicmí of five"), C(25, "with the five forfeda"), C(62, "Coligny months in five years = 60 + 2 intercalary"), C(4, "provinces"), C(5, "'fifths' with Mide"), C(3, "triads; rays of Awen"), C(8, "festivals of modern Druidry / Wicca")],
    crossings=[
        X(4, 5, "centre", "cúige means 'a fifth': four provinces and Mide, 'the middle', the fifth at the centre", "🟢"),
        X(20, 25, "extension", "four aicmí of five letters; a fifth aicme of five forfeda 'added later' — the extra group", "🟢"),
        X(60, 62, "residue", "Coligny: twelve months × five years = 60, plus two intercalary months (year 1 and year 3)", "🟢"),
        X(7, 8, "return", "Samhain is at once the last festival ('summer's end') and the new year (corpus, modern)", "🟠"),
        X(18, 19, "return", "Apollo returns to the Hyperborean island every nineteen years (Diodorus II.47): the Metonic return", "🟡"),
    ],
    residues=[R("'three drops of Awen escaped' from the year-long brew: the residue makes the bard (corpus)", "🟡")],
    devices={"record": ["Ogham on stone edge", "staves cast on cloth"], "hull": ["cauldron", "nemeton"]},
    calendar={"charts": [[12, 30]], "year": 354, "residue": "2 months in 5 years", "intercalation": "2 in 5"},
    numbers=[N(20, "order", "Ogham"), N(25, "order", "with forfeda"), N(62, "order", "Coligny months"), N(5, "order", "fifths"), N(19, "passage", "Hyperborean return"), N(3, "order", "triads")],
)

T(
    id="arthurian", name="Arthurian / Grail", family="Northern Europe", region="Britain / France",
    standing="PRIMARY_EVIDENCE",
    sources=["Siege Perilous page, Wikipedia 2026-09-07 (Malory 1485; Perceval de Didot; Lia Fáil parallel)"],
    closures=[C(12, "knights of the Round Table (count varies by text)", "🟡")],
    crossings=[X(12, 13, "extra", "the Siege Perilous: the one seat kept empty, fatal to any but the Grail knight; Galahad takes it on Whitsunday (Pentecost — the fiftieth day)", "🟢")],
    devices={"record": ["the letters of gold on the seat"], "hull": ["the Grail", "the Round Table"]},
    numbers=[N(13, "passage", "the empty seat"), N(12, "order", "knights")],
    notes="An empty seat that kills the wrong occupant is the tradition's own version of the corpus rule 'KC144+ does not create GID145'.",
)

T(
    id="finnish", name="Finnish (Kalevala)", family="Northern Europe", region="Finland / Karelia",
    standing="SECONDARY_SCHOLARSHIP",
    sources=["Kalevala page, Wikipedia 2026-09-07"],
    closures=[C(50, "runos"), C(9, "diseases, sons of Loviatar")],
    crossings=[X(8, 9, "extra", "nine sons of Loviatar: eight named diseases and a ninth, unnamed, sent away (runo 45)", "🟡")],
    devices={"record": [], "hull": ["the Sampo, the closed mill of plenty, broken and its fragments the residue"]},
    numbers=[N(50, "record", "runos"), N(9, "passage", "diseases")],
)

T(
    id="wicca", name="Wicca and modern witchcraft", family="Northern Europe", region="Britain (1950s →)",
    standing="MODERN_RECONSTRUCTION",
    sources=["corpus: WICCA_COMPLETE.md", "Coven page (Murray 1921, thirteen), Wikipedia 2026-09-07"],
    closures=[C(8, "sabbats"), C(13, "esbats 'typically'"), C(3, "degrees; threefold law"), C(5, "moon phases with the dark"), C(13, "coven (Murray's claim)")],
    crossings=[X(12, 13, "extra", "thirteen esbats against twelve months: the thirteenth full moon (corpus)", "🟢"),
               X(12, 13, "extra", "coven of thirteen = twelve and a leader (Murray 1921; modern)", "🟡"),
               X(8, 9, "return", "Samhain is the eighth sabbat and the 'Witch's New Year' (corpus)", "🟢", marked=True),
               X(365, 366, "return", "'a year and a day' between degrees (corpus)", "🟢")],
    devices={"record": ["Book of Shadows", "pentacle disk"], "hull": ["the circle 'open but unbroken', with a door cut and resealed", "cauldron", "chalice"]},
    calendar={"charts": [[8, 45]], "year": 365, "residue": "13th esbat", "intercalation": ""},
    numbers=[N(8, "order", "sabbats"), N(13, "passage", "esbats; coven"), N(3, "order", "degrees")],
)

# ============================================================================
# G. AFRICA AND THE DIASPORA
# ============================================================================

T(
    id="ifa_yoruba", name="Ifá / Yoruba", family="Africa", region="Yorubaland",
    standing="LIVING_TRADITION_SOURCE",
    sources=["corpus: IFA_DIVINATION_COMPLETE.md (no 17th ikin, no Ọ̀ṣẹ́tùúrá, no 401 in the file)", "Ifá, Oshun, Yoruba calendar pages, Wikipedia 2026-09-07", "Ω43 pulse (seniority order = V₄ orbits)"],
    closures=[C(16, "principal odù = 2⁴"), C(256, "odù = 16²"), C(4, "days of the week"), C(91, "weeks"), C(364, "days = 91 × 4"), C(400, "= 20², 'complete' in base 20; ẹ́rìndínlógún 'four less than twenty' = 16"), C(8, "seed halves of the ọ̀pẹ̀lẹ̀")],
    crossings=[
        X(16, 17, "extra", "Ọ̀ṣun 'the only female among the irúnmọlẹ̀ sent to create the world'; the male spirits' attempt 'without female involvement caused the world to fail' until she was included — the seventeenth admitted", "🟢"),
        X(16, 17, "extra", "the seventeenth ikin (adélé / olórí ikin) kept apart from the sixteen and not cast; Ọ̀ṣẹ́tùúrá as the seventeenth odù that carries sacrifice", "🟡"),
        X(400, 401, "extra", "irinwó irúnmọlẹ̀ + 1 = 401 orisha", "🟡"),
        X(0, 1, "extra", "Èṣù 'must be honored first … without Èṣù nothing moves', carved at the head of the tray (corpus)", "🟢"),
    ],
    residues=[R("grabs leaving 0 or ≥3 nuts are invalid and repeated (corpus): the outcomes outside the code", "🟢")],
    devices={"record": ["ọpọ́n Ifá tray with iyerosun powder — the odù marked and wiped"], "hull": ["the calabash of ikin", "the sopera / vessel (diaspora)"]},
    oracle={"states": 256, "encoding": "1 nut left → II (0), 2 nuts → I (1); eight grabs; right column senior", "set_aside": "17th ikin (🟡)",
            "symmetry": "traditional seniority pairs: 4 complement pairs + 4 reversal pairs = the six V₄-orbits (four of size 2, two of size 4)"},
    calendar={"charts": [[4, 91]], "year": 364, "residue": "", "intercalation": ""},
    arithmetic={"present": False, "what": "binary structure without positional arithmetic"},
    numbers=[N(16, "order", "odù"), N(256, "order", "odù"), N(17, "passage", "Ọ̀ṣun; the witness nut"), N(400, "order", "complete"), N(401, "passage", "orisha"), N(364, "order", "year = 4·7·13"), N(91, "order", "weeks = 7·13"), N(4, "order", "week")],
    notes="The 16|17 pair confirmed the generalised law (Ω43); Ọ̀ṣun's exclusion is the same myth as Eris's.",
)

T(
    id="santeria_lucumi", name="Santería / Lucumí", family="Africa diaspora", region="Cuba",
    standing="LIVING_TRADITION_SOURCE",
    sources=["corpus: SANTERIA_LUCUMI_COMPLETE.md (odún 1–12 read by the santero, 13–16 referred; '16 + 2 additional shells'; Babalú-Ayé 17; obí 4 → 5 letras)", "Babalú-Ayé page: Metanlá (13 cowries), Wikipedia 2026-09-07"],
    closures=[C(16, "cowries of the dilogún"), C(12, "odún the santero reads"), C(4, "obí pieces"), C(5, "obí letras"), C(7, "days of kariocha; the Seven African Powers"), C(21, "paths of Elegguá")],
    crossings=[
        X(12, 13, "extra", "'13 – Metanlá: sudden death (babalawo refers)'; odún 13–16 pass to the higher oracle — the oracle stops at twelve and the thirteenth is the passage", "🟢"),
        X(16, 17, "extra", "Babalú-Ayé, the outcast of disease, numbered 17 after Orula's and Obatalá's 16 (corpus)", "🟢"),
        X(16, 18, "extension", "'16 + 2 additional shells' set aside from the cast (corpus)", "🟢"),
        X(4, 5, "extra", "obí: four pieces give five patterns; Alafia (all white) 'too perfect — cast again'", "🟢"),
        X(0, 1, "extra", "Elegguá 'first honored', kept 'behind the door'", "🟢"),
    ],
    devices={"record": ["the correspondence table; the filed 'mouths' of the cowries"], "hull": ["soperas holding the otanes — 'the orisha lives in the vessel'", "the igbodú"]},
    oracle={"states": 16, "encoding": "count of open mouths 1–16", "set_aside": "2 extra shells; the obí piece with the natural mouth", "symmetry": "obí: Alafia↔Oyekun, Itagua↔Okana complements; Eyeife self-complementary and 'definitive'"},
    numbers=[N(16, "order", "cowries"), N(13, "passage", "Metanlá: sudden death, referred out"), N(17, "passage", "Babalú-Ayé"), N(9, "passage", "Oyá of the cemetery"), N(21, "passage", "Elegguá at the crossroads = 3·7"),
             N(7, "order", "Yemayá; powers"), N(8, "order", "Obatalá"), N(5, "order", "Ochún"), N(6, "order", "Changó"), N(3, "order", "Elegguá")],
    notes="Three nested crossings from one living oracle: 12|13 in the reading, 16|17 in the orisha numbers, 16+2 in the shells. Numbers are attested practice, readings are ours.",
)

T(
    id="vodou_haiti", name="Haitian Vodou", family="Africa diaspora", region="Haiti",
    standing="LIVING_TRADITION_SOURCE",
    sources=["corpus: HAITIAN_VODOU_COMPLETE.md"],
    closures=[C(5, "nanchon named"), C(3, "served in order: Rada, Petwo, Gede"), C(21, "peppers in Baron's rum; nations (🟡)"), C(7, "ceremony phases; days")],
    crossings=[X(0, 1, "extra", "Legba 'always saluted first, opens the gate', thanked at the close; the song promises the return: 'when I return I will salute the Lwa' (corpus)", "🟢"),
               X(2, 3, "extra", "Gede 'between Rada and Petwo, served last' — the death set as the passage between the two (corpus)", "🟢"),
               X(4, 5, "centre", "the poto mitan, the centre post 'connecting heaven, earth and Ginen', around which the vèvè are drawn (corpus)", "🟢")],
    residues=[R("the vèvè is danced upon and destroyed; the pot tèt keeps hair and nails as the soul's seat (corpus)", "🟢")],
    devices={"record": ["vèvè in cornmeal — a flat record that is consumed"], "hull": ["pot tèt", "govi", "asson containing the pwen", "the djevo"]},
    numbers=[N(21, "passage", "peppers; nations"), N(7, "order", "phases"), N(3, "order", "nanchon served"), N(1, "passage", "the gate")],
)

T(
    id="hoodoo_folk_magic", name="Hoodoo, Pow-Wow, Curanderismo (folk magic)", family="Africa diaspora / Europe / Americas", region="USA / Mexico",
    standing="LIVING_TRADITION_SOURCE",
    sources=["corpus: HOODOO_ROOTWORK_COMPLETE.md, POWWOW_BRAUCHEREI_COMPLETE.md, CURANDERISMO_COMPLETE.md", "Sator Square page (Pompeii, pre-AD 62), Wikipedia 2026-09-07"],
    closures=[C(9, "nights at the crossroads; nails/pins/needles"), C(25, "letters of the SATOR square"), C(7, "day candles; egg-reading signs + the eighth 'clear'"), C(3, "wells; crosses; the Trinity of the charm")],
    crossings=[X(2, 3, "extra", "'never an even number of items' in the mojo: 3, 5, 7 or 9 — the odd count as closed set plus one (corpus)", "🟠"),
               X(3, 4, "extra", "'whoever is stronger than these three may do unto me what they will': the closed three naming its own breaching fourth (corpus Pow-Wow)", "🟢"),
               X(7, 8, "extra", "egg reading: seven signs and the eighth state 'clear: patient is clean' (corpus)", "🟢"),
               X(0, 1, "extra", "the crossroads: the Black Man met there, 'return home before dawn', 'walk away without looking back' (corpus)", "🟢")],
    devices={"record": ["SATOR square, palindromic in four directions with N at the centre — the mirror stored", "name-paper", "Himmelsbrief"], "hull": ["the egg absorbing the negative, broken into water and read", "honey jar", "mojo bag", "witch bottle"]},
    numbers=[N(9, "passage", "crossroads nights"), N(7, "order", "candles"), N(25, "record", "SATOR"), N(91, "passage", "Psalm 91 = 7·13"), N(23, "order", "Psalm 23")],
)

T(
    id="kongo_akan_dogon", name="Kongo, Akan, Dogon", family="Africa", region="Central and West Africa",
    standing="SECONDARY_SCHOLARSHIP",
    sources=["Kongo cosmogram, Akan calendar, Dogon (Griaule / van Beek) pages, Wikipedia 2026-09-07"],
    closures=[C(4, "moments of the sun in the dikenga"), C(42, "days of the Akan adaduanan = lcm(6,7)"), C(378, "days = 9 adaduanan"), C(8, "Dogon ancestors (Griaule, contested)", "🟡")],
    crossings=[X(4, 5, "centre", "the dikenga: four moments around the crossing point, 'the intersection holds particular significance'", "🟢"),
               X(365, 378, "residue", "nine cycles of 42 = 378 exceed the solar year by ~13 days, so the festivals walk through the year", "🟢")],
    residues=[R("378 − 365.25 ≈ 12.75 days", "🟢", "13")],
    devices={"record": ["dikenga drawn on the ground; Adinkra stamped"], "hull": []},
    calendar={"charts": [[6, 7]], "year": 378, "residue": "13 days", "intercalation": "none"},
    numbers=[N(42, "order", "adaduanan = 2·3·7"), N(378, "order", "year = 2·3³·7"), N(6, "order", "week"), N(7, "order", "week"), N(8, "order", "Dogon ancestors")],
    negatives=["Griaule's Dogon material is disputed (van Beek): kept 🟡 and not used for any count."],
)

# ============================================================================
# H. THE AMERICAS
# ============================================================================

T(
    id="maya", name="Maya", family="Americas", region="Mesoamerica",
    standing="PRIMARY_EVIDENCE",
    sources=["Maya calendar page, Wikipedia 2026-09-07; Popol Vuh (recalled)", "Ω36 pulse"],
    closures=[C(360, "tun = 18 × 20"), C(260, "tzolk'in = 13 × 20"), C(18980, "calendar round = 52 years"), C(9, "lords of the night"), C(13, "levels of heaven (🟡)"), C(819, "count = 7·9·13"), C(20, "day names"), C(144000, "bak'tun")],
    crossings=[X(360, 365, "residue", "haab' = 18 × 20 + 5 wayeb', 'unlucky'", "🟢"),
               X(4, 5, "centre", "four directions and the centre (the ceiba), four colours and the fifth", "🟢"),
               X(8, 9, "extra", "nine lords of the night; Xibalba's nine levels (🟡)", "🟡"),
               X(6, 7, "extra", "Popol Vuh: One Death and Seven Death, lords of Xibalba; six houses of trial (Dark, Cold, Jaguar, Bat, Razor, Fire — count varies)", "🟡")],
    residues=[R("5 wayeb'", "🟢", "5")],
    devices={"record": ["screenfold codex (fold)", "stela"], "hull": ["the canoe of the Paddler gods", "the turtle carapace split for the Maize god's rebirth"]},
    ladder=[{"count": 5, "what": "k'in 1 → winal 20 → tun 360 → k'atun 7200 → bak'tun 144,000"}],
    calendar={"charts": [[18, 20]], "year": 360, "residue": "5 wayeb'", "intercalation": "none"},
    arithmetic={"present": True, "what": "vigesimal place value with 18 at the second place; zero; no fractions"},
    numbers=[N(360, "order", "tun"), N(260, "order", "tzolk'in"), N(18980, "order", "calendar round"), N(819, "passage", "count = 7·9·13"), N(9, "passage", "lords of the night"),
             N(13, "order", "numbers of the tzolk'in"), N(7, "passage", "Seven Death"), N(5, "residue", "wayeb'"), N(20, "order", "days"), N(144000, "order", "bak'tun")],
    negatives=["13 is a lucky/complete number here (13 × 20), not a passage: the crossing numbers are 5, 7 and 9."],
)

T(
    id="aztec", name="Aztec / Mexica", family="Americas", region="Mesoamerica",
    standing="PRIMARY_EVIDENCE",
    sources=["Aztec calendar, Five Suns, Coyolxauhqui, Tonalpohualli pages, Wikipedia 2026-09-07"],
    closures=[C(360, "18 × 20 named days"), C(5, "nemontemi"), C(260, "tonalpohualli"), C(52, "year bundle = 4 × 13"), C(4, "previous suns"), C(400, "Centzon Huitznahua, 'four hundred' = innumerable"), C(13, "heavens (🟡)"), C(9, "underworld levels (🟡)")],
    crossings=[X(4, 5, "return", "four suns destroyed, the fifth (Nahui Ollin) is the present, 'destined to end in earthquake'", "🟢"),
               X(360, 365, "residue", "five nameless days, 'thought to be unlucky'", "🟢"),
               X(400, 401, "extra", "the four hundred Huitznahua and their sister Coyolxauhqui: 400 + 1 lead the attack; Huitzilopochtli scatters the 400 and dismembers the one", "🟢"),
               X(4, 5, "centre", "four directions and the centre (Tlalxicco, the navel)", "🟢")],
    residues=[R("nemontemi", "🟢", "5")],
    devices={"record": ["screenfold codex", "the Sun Stone"], "hull": ["the year-bundle bound and buried at the New Fire"]},
    calendar={"charts": [[18, 20]], "year": 360, "residue": "5 nemontemi", "intercalation": "none"},
    arithmetic={"present": True, "what": "vigesimal; 52 = 4·13"},
    numbers=[N(5, "residue", "nemontemi; the fifth sun"), N(400, "order", "the many"), N(401, "passage", "the one sister"), N(52, "order", "year bundle"), N(13, "order", "numbers"), N(9, "passage", "Mictlan levels"), N(4, "order", "suns past")],
    notes="Base-20 culture with 400 + 1, like the Yoruba 401: the two vigesimal traditions put the crossing at the same place.",
)

T(
    id="inca_andean", name="Inca / Andean", family="Americas", region="Andes",
    standing="SECONDARY_SCHOLARSHIP",
    sources=["Tawantinsuyu and Ceque system pages (Zuidema), Wikipedia 2026-09-07"],
    closures=[C(4, "suyus 'whose corners met at the capital'"), C(41, "ceques (41–42)"), C(328, "huacas 'each may represent one day'")],
    crossings=[X(4, 5, "centre", "Tawantinsuyu 'the four parts together' meeting at Cusco, the navel", "🟢"),
               X(328, 365, "residue", "Zuidema: 328 = 12 sidereal months; the 37 missing days = the invisibility of the Pleiades", "🟡")],
    residues=[R("37 days", "🟡", "37")],
    devices={"record": ["quipu (base 10, knotted)"], "hull": ["the Qorikancha"]},
    calendar={"charts": [], "year": 328, "residue": "37", "intercalation": ""},
    numbers=[N(4, "order", "suyus"), N(328, "order", "huacas"), N(37, "residue", "Pleiades invisible"), N(41, "order", "ceques")],
)

T(
    id="north_american", name="North American (Plains medicine wheel)", family="Americas", region="Great Plains",
    standing="SECONDARY_SCHOLARSHIP",
    sources=["Medicine wheel page (Bighorn: 28 spokes; symbol invented 1972), Wikipedia 2026-09-07"],
    closures=[C(4, "directions"), C(28, "spokes of the Bighorn wheel = 4 × 7")],
    crossings=[X(4, 5, "centre", "four directions around the central cairn", "🟢")],
    devices={"record": ["the wheel laid in stone"], "hull": ["the sweat lodge"]},
    numbers=[N(28, "order", "spokes = 4·7"), N(4, "order", "directions")],
    negatives=["The modern 'medicine wheel' symbol (1972) is a reconstruction; only the stone wheels are primary."],
)

# ============================================================================
# I. OCEANIA
# ============================================================================

T(
    id="polynesian_hawaiian", name="Polynesian / Hawaiian (Kumulipo, star compass)", family="Oceania", region="Hawaiʻi / Micronesia",
    standing="PRIMARY_EVIDENCE",
    sources=["Kumulipo page, Wikipedia 2026-09-07 (16 wā: 7 pō, 9 ao)", "Mau Piailug / Nainoa Thompson star compass of 32 houses (recalled)"],
    closures=[C(16, "wā of the Kumulipo = 2⁴"), C(7, "wā of pō (night)"), C(9, "wā of ao (light)"), C(32, "houses of the star compass = 2⁵", "🟡")],
    crossings=[X(7, 8, "return", "'the first seven wā fall under pō, the age of spirit; the remaining nine are ao, signalled by the arrival of light and the gods' — night closes at seven, light begins at the eighth", "🟢")],
    devices={"record": ["the chant itself (2,102 lines)"], "hull": ["the canoe"]},
    numbers=[N(16, "order", "wā"), N(7, "passage", "night eras"), N(9, "order", "light eras"), N(32, "order", "star houses")],
    notes="A creation chant with the 7|8 night-to-day crossing built into its table of contents, with no contact with the Near East.",
)

T(
    id="australian", name="Australian Aboriginal", family="Oceania", region="Australia",
    standing="SECONDARY_SCHOLARSHIP",
    sources=["general: six-season calendars (Yolŋu, D'harawal), songlines as record — recalled"],
    closures=[C(6, "seasons (Yolŋu, D'harawal)", "🟡")],
    crossings=[],
    devices={"record": ["songlines: the land as the record, the song as the map"], "hull": []},
    numbers=[N(6, "order", "seasons")],
    negatives=["No marked crossing entered: the sources available here do not support one. Left open rather than filled."],
)

# ============================================================================
# J. WESTERN ESOTERIC (RENAISSANCE → MODERN)
# ============================================================================

T(
    id="alchemy", name="Western alchemy", family="Western esoteric", region="Alexandria → Europe",
    standing="PRIMARY_EVIDENCE",
    sources=["corpus: WESTERN_ALCHEMY_COMPLETE.md (Ripley's twelve gates; egg 'must not be opened'; citrinitas 'often merged')"],
    closures=[C(4, "elements"), C(3, "principles"), C(7, "metals = planets = days"), C(12, "operations / gates (Ripley)"), C(4, "colour stages")],
    crossings=[X(4, 5, "extra", "quintessence, 'the fifth element: what remains when four elements are balanced' (corpus)", "🟢"),
               X(3, 4, "withdrawn", "citrinitas, the third of four stages, 'often merged with rubedo' — the stage that vanishes into its neighbour (corpus)", "🟢"),
               X(0, 1, "return", "ouroboros 'one is all'; the pelican 'self-circulating'; 'it ascends from earth to heaven and descends again' (Emerald Tablet)", "🟢")],
    residues=[R("salt = 'what remains, the ash' (corpus)", "🟢")],
    devices={"record": ["the Emerald Tablet — a tablet that ends 'what I have said … is complete'", "Mutus Liber"], "hull": ["the philosophical egg 'hermetically sealed, must not be opened'", "athanor 'the immortal, the womb of the Stone'", "pelican"]},
    ladder=[{"count": 7, "what": "metals lead → gold"}, {"count": 4, "what": "nigredo → albedo → citrinitas → rubedo"}],
    numbers=[N(4, "order", "elements"), N(5, "passage", "quintessence"), N(7, "order", "metals"), N(12, "order", "gates"), N(3, "order", "principles")],
    notes="The sealed egg is the ark law as laboratory practice: the work happens only inside a closed hull.",
)

T(
    id="solomonic_goetia", name="Solomonic magic and the Goetia", family="Western esoteric", region="Europe, 13th–17th c.",
    standing="PRIMARY_EVIDENCE",
    sources=["corpus: SOLOMONIC_MAGIC_COMPLETE.md, GOETIC_GRIMOIRE_COMPLETE.md"],
    closures=[C(72, "spirits of the Ars Goetia; Asmoday's 72 legions"), C(7, "planets; ranks; pentacles per planet (mostly)"), C(24, "planetary hours"), C(36, "decan-demons of the Testament"), C(5, "books of the Lemegeton"), C(4, "kings of the quarters"), C(196, "Olympic provinces 49+42+35+28+21+14+7 = 4·49")],
    crossings=[X(7, 8, "return", "'hours: 1st and 8th' for every planet — the eighth hour is the first again (corpus)", "🟢"),
               X(72, 80, "extension", "ranks sum to exactly 72 through the earls; the eight knights are listed over (corpus, computed)", "🟠"),
               X(0, 1, "extra", "the triangle of art placed outside the circle: the summoned one has its own smaller hull; the operator 'never leaves' the circle", "🟢"),
               X(4, 5, "extra", "Ars Notoria as the fifth book, 'originally separate, older, no spirits' (corpus)", "🟠")],
    devices={"record": ["seals 'the key to communication'", "pentacles on virgin parchment, wrapped in silk"], "hull": ["the brass vessel with the seal on the lid and the sigils inside", "circle of 9 feet", "the triangle"]},
    ladder=[{"count": 7, "what": "ranks kings → knights"}, {"count": 7, "what": "Olympic provinces descending by 7"}],
    numbers=[N(72, "order", "spirits = 360/5 = 8·9"), N(7, "order", "planets"), N(8, "passage", "the eighth hour"), N(24, "order", "hours"), N(196, "order", "provinces = 4·7²"), N(9, "order", "circle feet; ninth legion")],
)

T(
    id="enochian_dee", name="Enochian magic (Dee and Kelley)", family="Western esoteric", region="England, 1582–1589",
    standing="PRIMARY_EVIDENCE",
    sources=["corpus: ENOCHIAN_MAGIC_COMPLETE.md ('18 explicit Calls + 1 implicit'; 624 + 20 = 644; 4 small + 1 large Sigilla; 91 governors; ZAX the 10th of 30)", "Liber Loagaeth page (94 grids of 49×49), Wikipedia 2026-09-07"],
    closures=[C(21, "letters = 3·7"), C(49, "tables of Loagaeth, each 49 × 49 = 7⁴ cells"), C(30, "aethyrs"), C(91, "governors / parts of the earth = 7·13"), C(4, "watchtowers of 12 × 13 = 156"), C(624, "letters of the four watchtowers"), C(20, "letters of the Tablet of Union"), C(18, "calls"), C(7, "ensigns; heptarchic kings")],
    crossings=[X(18, 19, "extra", "'the nineteen calls: 18 explicit + 1 implicit' (corpus)", "🟢"),
               X(4, 5, "centre", "four watchtowers bound by the Tablet of Union, 'the fifth element', 624 + 20 = 644 letters; one large Sigillum for the centre and four small for the legs (corpus)", "🟢"),
               X(90, 91, "extra", "30 aethyrs × 3 governors = 90; the tradition counts 91 — one over (corpus, computed)", "🟠"),
               X(9, 10, "withdrawn", "the tenth aethyr ZAX is the Abyss 'that must be crossed', with nine supernal aethyrs above it: the crossing sits inside the count (corpus)", "🟢")],
    residues=[R("cacodemons = 'servient names reversed', the inverted set stored in the same tablet (corpus)", "🟢")],
    devices={"record": ["Holy Table with 84-letter border", "the 49 × 49 tables", "wax Sigillum engraved on both sides"], "hull": ["shewstone", "the temple aligned to the quarters"]},
    ladder=[{"count": 30, "what": "aethyrs 30 → 1, abyss at 10"}],
    arithmetic={"present": True, "what": "letter values; 12·13 = 156; 4·156 = 624; 49 = 7²; 91 = 7·13 = 364/4 (the Jubilees quarter)"},
    numbers=[N(49, "order", "tables = 7²"), N(2401, "order", "cells per table = 7⁴"), N(91, "order", "governors = 7·13"), N(156, "order", "squares per watchtower = 12·13"), N(644, "order", "letters"), N(30, "order", "aethyrs"),
             N(10, "passage", "ZAX, the Abyss"), N(19, "passage", "the implicit call"), N(21, "record", "letters = 3·7")],
    notes="A designed system saturated with 7 (21, 49, 91, 2401) that also states the n+1 in its own words three times.",
)

T(
    id="rosicrucian", name="Rosicrucianism", family="Western esoteric", region="Germany, 1614–1616",
    standing="PRIMARY_EVIDENCE",
    sources=["corpus: ROSICRUCIANISM_COMPLETE.md (seven-sided vault; 120 years; six days then 'Day Seven: return … incomplete (text ends suddenly)')", "Fama Fraternitatis page, Wikipedia 2026-09-07"],
    closures=[C(7, "sides of the vault; days of the Chymical Wedding; floors of the Tower"), C(120, "years before the vault is opened (1484 → 1604)"), C(8, "brothers (4 then 8)"), C(3, "manifestos")],
    crossings=[X(6, 7, "return", "six days complete the Work; Day Seven is 'return', CRC 'to be doorkeeper', and the text 'ends suddenly' — the crossing is both gate and unclosed (corpus)", "🟢"),
               X(3, 4, "extra", "CRC and three monks make four, doubled to eight (corpus)", "🟠")],
    devices={"record": ["Book M", "the vault's 'books, mirrors, symbols … a compendium of the universe'"], "hull": ["the heptagonal vault with the body of CRC inside"]},
    numbers=[N(7, "order", "sides, days"), N(120, "order", "years = SHCN"), N(8, "order", "brothers"), N(106, "order", "CRC's lifespan (2·53, irregular)")],
)

T(
    id="freemasonry", name="Freemasonry", family="Western esoteric", region="Britain →",
    standing="TRADITION_INTERNAL",
    sources=["Scottish Rite page (4°–32° conferred, 33° honorary), Wikipedia 2026-09-07", "winding stair 3+5+7 = 15; the 47th proposition — recalled"],
    closures=[C(3, "craft degrees"), C(33, "Scottish Rite degrees"), C(15, "steps of the winding stair = 3 + 5 + 7", "🟡"), C(7, "liberal arts"), C(5, "points of fellowship")],
    crossings=[X(32, 33, "extra", "degrees 4–32 are worked; 'an additional honorary 33rd degree' conferred, not worked", "🟢"),
               X(0, 1, "residue", "the Lost Word: the closed rite is built around a missing unit, replaced by a substitute", "🟡")],
    devices={"record": ["tracing board"], "hull": ["the lodge as Solomon's temple"]},
    numbers=[N(33, "passage", "the honorary degree"), N(32, "order", "worked degrees"), N(15, "order", "stair steps"), N(47, "order", "the 47th proposition of Euclid I")],
)

T(
    id="golden_dawn_qabalah", name="Golden Dawn (Hermetic Qabalah as grade system)", family="Western esoteric", region="England, 1888",
    standing="PRIMARY_EVIDENCE",
    sources=["corpus: GOLDEN_DAWN_COMPLETE.md, HERMETIC_QABALAH_COMPLETE.md"],
    closures=[C(10, "sefirot = grades 1°=10□ … 10°=1□"), C(22, "paths 11–32; trumps 0–XXI"), C(4, "elements; worlds; weapons"), C(6, "points of the hexagram"), C(7, "sides of the Vault; officers")],
    crossings=[X(10, 11, "extra", "Da'ath 'not a sefirah, invisible, where the Tree was broken, must be crossed'; yet counted as the second of five Middle Pillar centres (corpus)", "🟢"),
               X(0, 1, "extra", "Neophyte 0°=0□ 'outside the Tree'; the Portal grade unnumbered 'Spirit reconciling the four' between 4°=7□ and 5°=6□ (corpus)", "🟢"),
               X(21, 22, "extra", "the Fool numbered '0/XXII' — the trump that is both before the first and after the last (corpus)", "🟢"),
               X(6, 7, "centre", "hexagram of six planets with 'the Sun at the centre' (corpus)", "🟢"),
               X(4, 5, "extra", "the Lotus Wand as the fifth implement; Spirit as the fifth element (corpus)", "🟢")],
    residues=[R("Kether's image 'seen in profile — only one side visible' (corpus)", "🟠")],
    devices={"record": ["Cipher Manuscripts (Trithemius cipher)", "the Earth Pentacle: hexagram on one side, pentagram on the other"], "hull": ["Vault of the Adepti: seven walls, ceiling zodiac, floor elements, the pastos with the body of CRC within"]},
    ladder=[{"count": 11, "what": "grades 0=0 … 10=1; n + m = 11 for all but 0=0"}],
    arithmetic={"present": True, "what": "gematria; grade notation n°=m□ with n+m = 11"},
    numbers=[N(11, "passage", "Da'ath; grade sum"), N(10, "order", "sefirot"), N(22, "order", "paths"), N(0, "passage", "the Fool; Neophyte"), N(7, "order", "Vault sides"), N(13, "passage", "path of Gimel 'crosses the Abyss'")],
    notes="Densest single file in the corpus for the law: five distinct crossings, each in the tradition's own words.",
)

T(
    id="thelema", name="Thelema", family="Western esoteric", region="1904 →",
    standing="PRIMARY_EVIDENCE",
    sources=["corpus: THELEMA_COMPLETE.md"],
    closures=[C(10, "numbered A∴A∴ grades"), C(3, "chapters of Liber AL; aeons"), C(11, "'the number of magick' = 10 + 1"), C(93, "Thelema = Agape"), C(418, "Abrahadabra"), C(666, "Therion"), C(333, "Choronzon")],
    crossings=[X(10, 11, "extra", "Daath 'non-sephira'; an unnumbered grade at every threshold: Student | 0°, Dominus Liminis | 5°=6□, Babe of the Abyss | 8°=3□ (corpus)", "🟢"),
               X(10, 11, "extra", "the Black Brothers 'build a false sephira in Daath, become trapped … eventually destroyed': occupying the excluded slot is the named failure (corpus)", "🟢"),
               X(10, 11, "extra", "O.T.O.: XI° beyond the X° national head, 'extremely restricted' (corpus)", "🟢")],
    devices={"record": ["Liber AL, 'change not so much as the style of a letter'"], "hull": ["'the babe in the egg' (Harpocrates)", "the circumference (Nuit) and the point (Hadit)"]},
    arithmetic={"present": True, "what": "gematria: 31 = AL = LA; 93; 418; 666; 777; 888"},
    numbers=[N(11, "passage", "magick; Daath"), N(93, "order", "current"), N(418, "order", "the word of the aeon"), N(666, "order", "Therion"), N(333, "chaos", "Choronzon"), N(31, "order", "AL")],
)

T(
    id="theosophy_anthroposophy", name="Theosophy and Anthroposophy", family="Western esoteric", region="1875 → / 1912 →",
    standing="MODERN_RECONSTRUCTION",
    sources=["corpus: THEOSOPHY_COMPLETE.md ('FOUR INITIATIONS' heading followed by a 5th), ANTHROPOSOPHY_COMPLETE.md (3×3 hierarchies, humans the developing fourth)"],
    closures=[C(7, "planes, globes, rounds, root races, sub-races, principles"), C(9, "orders of spiritual beings = 3 × 3"), C(6, "subsidiary exercises"), C(4, "initiations (heading)")],
    crossings=[X(4, 5, "extra", "heading 'FOUR INITIATIONS', then '5th Initiation (Resurrection) … Master' (corpus)", "🟢"),
               X(9, 10, "extra", "nine orders in three triads; 'humans: fourth hierarchy (developing)' (corpus)", "🟢"),
               X(5, 6, "return", "five exercises and a sixth that is 'harmony of all five' (corpus)", "🟢"),
               X(3, 4, "centre", "Earth as globe D, fourth of seven, 'midpoint of evolution, matter densest' — the turning slot of a 3-1-3 ladder (corpus)", "🟠")],
    residues=[R("Luciferic beings 'remained behind on Old Moon' — the lagging residue (corpus)", "🟠")],
    devices={"record": ["Rückschau: the day reviewed backwards (the stored negative)"], "hull": ["cow horn buried over winter (BD 500)", "the causal body 'destroyed at the fourth initiation'"]},
    ladder=[{"count": 7, "what": "7 × 7 × 7 × 7 nested globes, rounds, races, sub-races"}],
    numbers=[N(7, "order", "everything"), N(9, "order", "hierarchies"), N(5, "passage", "the fifth initiation"), N(4, "order", "globe D")],
)

T(
    id="chaos_magic", name="Chaos magic", family="Western esoteric", region="1976 →",
    standing="MODERN_RECONSTRUCTION",
    sources=["corpus: CHAOS_MAGIC_COMPLETE.md (octarine 'the meta-colour that contains all others', a Pratchett reference)"],
    closures=[C(7, "planetary colours"), C(8, "with octarine"), C(5, "IOT degrees 4° → 0°"), C(25, "Liber KKK operations = 5 × 5"), C(8, "arrows of the chaosphere")],
    crossings=[X(7, 8, "extra", "octarine, the eighth colour 'visible only to magicians', containing the seven (corpus)", "🟢"),
               X(4, 5, "extra", "degrees count down 4° → 1°, and 0° Ipsissimus is 'beyond organization, theoretical only' (corpus)", "🟢"),
               X(8, 9, "centre", "the chaosphere: eight arrows and 'the centre is Chaos itself' (corpus)", "🟢"),
               X(0, 1, "extra", "the robofish: one near-certain sigil added to the shoal 'pulls the others along' (corpus)", "🟠")],
    residues=[R("sigil practice: the plaintext is destroyed and forgotten, only the glyph kept — the record stored as its own negative (corpus)", "🟢")],
    devices={"record": ["sigil", "kamea"], "hull": ["envelope 'seal and file away'", "circle + triangle"]},
    numbers=[N(8, "passage", "octarine"), N(7, "order", "colours"), N(25, "order", "operations"), N(0, "passage", "Ipsissimus")],
)

T(
    id="spiritualism", name="Spiritualism / mediumship", family="Western esoteric", region="1848 →",
    standing="MODERN_RECONSTRUCTION",
    sources=["corpus: SPIRITUALISM_MEDIUMSHIP_COMPLETE.md ('doorway to reformation never closed'; 'no final endpoint')"],
    closures=[C(7, "principles (SNU)"), C(7, "spheres 'common model'"), C(4, "clairs")],
    crossings=[],
    devices={"record": ["slate writing", "the rapping code (one knock = yes)"], "hull": ["the development circle 'always close properly'", "the darkened séance room"]},
    numbers=[N(7, "order", "principles, spheres")],
    negatives=["Declared falsifier-adjacent: the doctrine refuses closure ('never closed', 'no final endpoint'). The law does not apply where no closed count is asserted; the only closure operator is the instruction to close the circle."],
)

# ============================================================================
# K. INSTRUMENTS: ORACLE DEVICES, GAMES, COUNTING STRINGS, MUSIC
# ============================================================================

T(
    id="tarot_geomancy_cards", name="Tarot, geomancy and playing cards", family="Instruments", region="Italy / Arabia / France",
    standing="PRIMARY_EVIDENCE",
    sources=["Tarot page (21 numbered trumps + the unnumbered Fool; 56 = 4 × 14), Standard 52-card deck page, Wikipedia 2026-09-07", "geomantic shield chart: judge parity theorem verified exhaustively in athena_mcp.closure_grammar"],
    closures=[C(78, "cards = T(12) = 22 + 56"), C(21, "numbered trumps"), C(56, "minors = 4 × 14"), C(16, "geomantic figures = 2⁴"), C(15, "figures of the shield chart: 4 mothers, 4 daughters, 4 nieces, 2 witnesses, 1 judge"),
              C(52, "cards = 4 × 13"), C(364, "= 52 × 7")],
    crossings=[X(21, 22, "extra", "the Fool 'unnumbered, sometimes 0 or XXII' — the card outside the count that the Golden Dawn seats at both ends", "🟢"),
               X(15, 16, "extra", "the shield chart closes with the Judge as the fifteenth figure; the Reconciler (Judge ⊕ first Mother) is the optional sixteenth", "🟢"),
               X(52, 53, "extra", "the joker outside the 52; 52 weeks × 7 = 364 and the year's odd day", "🟡")],
    devices={"record": ["the card face", "sand or wax for the geomantic points"], "hull": ["the deck box; the 'shield'"]},
    oracle={"states": 16, "encoding": "4 bits, odd = one point", "set_aside": "the Reconciler", "symmetry": "daughters are the transpose of the mothers; nieces XOR adjacent pairs"},
    arithmetic={"present": True, "what": "78 = 1+2+…+12; XOR generation of the shield; parity of the Judge"},
    numbers=[N(78, "order", "cards = T(12)"), N(22, "order", "trumps with the Fool"), N(0, "passage", "the Fool"), N(16, "order", "geomantic figures"), N(8, "order", "possible judges"), N(52, "order", "cards"), N(364, "order", "weeks × days"), N(13, "order", "ranks")],
    notes="Geomancy states the witness law in its own vocabulary: two Witnesses and a Judge. Parity theorem (verified over all 65,536 charts): the Judge always has an even number of single points, so only 8 of the 16 figures can close a chart.",
)

T(
    id="games_boards", name="Board games and dice (Go, chess, mahjong, dominoes, dice)", family="Instruments", region="China / India / Europe",
    standing="PRIMARY_EVIDENCE",
    sources=["Go page (361 points), Mahjong tiles page (136 + 8 = 144), Wikipedia 2026-09-07; Qijing Shisanpian ch. 1 on the board's 360 + 1 (recalled 🟡); die opposite faces summing to 7 (standard since antiquity, some ancient dice excepted)"],
    closures=[C(361, "Go points = 19² = 360 + 1"), C(72, "perimeter points of the Go board = 4·19 − 4 = the 72 pentads (Qijing)"), C(64, "chess squares = 8²"), C(32, "chess pieces"), C(144, "mahjong tiles = 136 + 8 flowers"),
              C(28, "dominoes (double-six) = T(7)"), C(6, "faces of a die")],
    crossings=[X(360, 361, "centre", "the Go board's centre point (tiānyuán) over 360: the Qijing reads 360 as the days, the four quarters of 90 as seasons, the 72 outer points as pentads", "🟡"),
               X(136, 144, "extension", "mahjong: 136 tiles and 8 bonus tiles (flowers/seasons) outside the play", "🟢"),
               X(6, 7, "return", "a die's opposite faces sum to 7: the closed cube's involution has constant n + 1, exactly the corpus's mirror constants M₁₄₄ = 145 − g, J₂₇ = 28 − n", "🟢")],
    devices={"record": ["the board as grid"], "hull": ["the die: the smallest closed hull whose mirror sums to n+1", "the dice cup"]},
    arithmetic={"present": True, "what": "19² = 361; 4·19 − 4 = 72; 360/4 = 90; T(7) = 28; opposite faces 1+6 = 2+5 = 3+4 = 7"},
    numbers=[N(361, "order", "Go"), N(72, "order", "Go perimeter"), N(64, "order", "chess"), N(144, "order", "mahjong"), N(28, "order", "dominoes = T(7)"), N(7, "order", "die face sum")],
    notes="The die is the corpus's mirror law made of wood: n faces, involution summing to n + 1, no seat for the sum.",
)

T(
    id="counting_strings", name="Counting strings (mālā, tasbīḥ, rosary, prayer rope)", family="Instruments", region="India / Islam / Christendom",
    standing="PRIMARY_EVIDENCE",
    sources=["Japa mala page (guru bead 'not used for counting', the mālā turned rather than crossed), Wikipedia 2026-09-07", "misbaḥa 33/99 + imām bead; rosary 5 × 10 + 3 + 1; prayer rope 33/50/100/300 — recalled"],
    closures=[C(108, "mālā beads"), C(99, "misbaḥa beads (or 33 × 3)"), C(150, "Aves of the full Dominican rosary = 150 psalms"), C(33, "knots of the small prayer rope; the tasbīḥ")],
    crossings=[X(108, 109, "extra", "the guru / meru bead, uncounted and not crossed: the counting reverses direction at it", "🟢"),
               X(99, 100, "extra", "the imām bead beyond the 99, uncounted — and the hundredth name hidden", "🟡"),
               X(50, 51, "extra", "the rosary's decades close at 50 Aves per chaplet; the pendant beads and crucifix hang outside the loop", "🟡")],
    devices={"record": [], "hull": ["the loop itself: a closed count worn on the body"]},
    numbers=[N(108, "order", "beads"), N(109, "passage", "meru"), N(99, "order", "misbaḥa"), N(100, "passage", "imām bead"), N(150, "order", "Aves")],
    notes="The physical oracle law: every counting string is a closed count plus one bead that is not counted and marks the turn.",
)

T(
    id="music", name="Music theory (Pythagorean, Chinese lü, Indian śruti)", family="Instruments", region="cross-cultural",
    standing="PRIMARY_EVIDENCE",
    sources=["Pythagorean comma, Jing Fang, Octave, Shruti pages, Wikipedia 2026-09-07", "Qian Lezhi's 360 lü (recalled 🟡)", "Ω29 pulse"],
    closures=[C(7, "diatonic notes"), C(12, "semitones / fifths of the near-closure"), C(53, "fifths of Jing Fang's closer near-closure"), C(60, "lü of Jing Fang"), C(22, "śrutis"), C(5, "pentatonic; 5-limit primes 2,3,5"), C(360, "lü of Qian Lezhi", "🟡")],
    crossings=[X(7, 8, "return", "the octave: the eighth note is the first again", "🟢"),
               X(12, 13, "residue", "twelve fifths miss seven octaves by the Pythagorean comma 3¹²/2¹⁹ = 531441/524288; the circle is a helix", "🟢"),
               X(53, 54, "residue", "53 fifths miss 31 octaves by Mercator's comma; Jing Fang's 60 lü carry the sequence past the near-closure", "🟢")],
    residues=[R("Pythagorean comma ≈ 23.5 cents", "🟢"), R("Mercator's comma 177147/176776", "🟢"), R("leimma 256/243", "🟢")],
    arithmetic={"present": True, "what": "record fifth-closures at k = 1, 2, 5, 12, 41, 53 (computed); 5-limit = the regular numbers"},
    numbers=[N(7, "order", "notes"), N(8, "passage", "octave"), N(12, "order", "semitones"), N(53, "order", "fifths"), N(60, "order", "lü"), N(22, "order", "śrutis"), N(360, "order", "lü (Qian Lezhi)")],
    notes="Music is where 'close at n, cross at n+1, and a residue remains' is audible: the octave is the return, the comma is the residue, and the regular numbers are the consonances.",
)

T(
    id="hermetic_science_of_letters", name="Alphabetic numerals (Hebrew 27, Greek 27, Arabic 28)", family="Instruments", region="Mediterranean",
    standing="PRIMARY_EVIDENCE",
    sources=["Greek numerals page (24 + digamma, koppa, sampi), Wikipedia 2026-09-07; Hebrew finals; abjad"],
    closures=[C(27, "symbols needed for 1–9, 10–90, 100–900 = 3 × 9"), C(24, "Greek letters"), C(22, "Hebrew letters"), C(28, "Arabic letters = 4 × 7")],
    crossings=[X(24, 27, "extension", "the Greek numeral alphabet needs 27: three dead letters (digamma 6, koppa 90, sampi 900) are kept for numbers only", "🟢"),
               X(22, 27, "extension", "Hebrew: 22 letters and five final forms make 27 = 3³ for the same three decades", "🟢")],
    arithmetic={"present": True, "what": "(base − 1) × places = 27 for decimal three-place alphabetic numerals (computed)"},
    numbers=[N(27, "order", "numeral symbols = 3³"), N(24, "order", "Greek"), N(22, "order", "Hebrew"), N(28, "order", "Arabic = 4·7")],
    notes="Structural consequence, not design: any decimal alphabetic numeral system closes at 27 and both isopsephy alphabets reach it by adding letters outside the ordinary count.",
)
