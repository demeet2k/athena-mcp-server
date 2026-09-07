"""MYTHOS OS modules — family NEAR_EAST (R01).

Template module: ``babylon``.  Every other module in every family file follows
this exact shape.  Grades: 🟢 attested in a named source in ``sources`` (add
``src`` on the slot or item where a locus is known); 🟡 secondary / disputed;
🟠 our reading or corpus-only; ⊥ explicit absence (``absent=True``, no content).
"""
from __future__ import annotations

MODULES = [
    {
        "id": "babylon",
        "name": "Babylonian (Enūma Eliš, Atra-ḫasīs, the Marduk cult)",
        "family": "NEAR_EAST",
        "standing": "PRIMARY_EVIDENCE",
        "sources": [
            "Enūma Eliš (Lambert, Babylonian Creation Myths, 2013)",
            "Atra-ḫasīs (Lambert & Millard 1969)",
            "MUL.APIN (Hunger & Pingree 1989)",
            "Ištar's Descent (Foster, Before the Muses)",
            "Akītu ritual text (Thureau-Dangin, Rituels accadiens; Linssen 2004)",
            "Bārûtu extispicy series (Koch 2005)",
        ],
        "corpus_refs": [],
        "closure_grammar_id": "babylon",
        "services": {
            "BOOT": {
                "grade": "🟢", "mode": "CREATED", "src": "Enūma Eliš I–VI",
                "stages": [
                    {"stage": "VOID", "event": "Apsû and Tiāmat mingle their waters; nothing is named", "src": "Ee I 1–8"},
                    {"stage": "SEPARATION", "event": "the generations of gods are born (Laḫmu, Laḫamu, Anšar, Kišar, Anu, Ea)", "src": "Ee I 9–20"},
                    {"stage": "FAULT", "event": "the gods' noise; Apsû plots to destroy them; Ea kills Apsû", "src": "Ee I 21–78"},
                    {"stage": "ORDERING", "event": "Marduk splits Tiāmat, fixes the stations of the stars, the year, the moon's phases", "src": "Ee IV 135 – V 46"},
                    {"stage": "POPULATION", "event": "humankind made from Kingu's blood to bear the gods' toil", "src": "Ee VI 1–38"},
                    {"stage": "MAINTENANCE", "event": "Babylon and Esagila built; the gods rest; the fifty names recited", "src": "Ee VI 45 – VII"},
                    {"stage": "REBOOT", "event": "the flood sent because of humankind's noise; Atra-ḫasīs survives in the sealed boat", "src": "Atra-ḫasīs III"},
                ],
                "notes": "FAULT precedes POPULATION: the first failure is divine, and humans are made to repair it.",
            },
            "MEMMAP": {
                "grade": "🟢", "addressing": "VERTICAL", "axis": "Etemenanki / Esagila as the bond of heaven and earth", "src": "Ee IV–V; KAR 307",
                "realms": [
                    {"name": "upper heaven (Anu)", "level": 3, "kind": "HEAVEN"},
                    {"name": "middle heaven (Igigi)", "level": 2, "kind": "HEAVEN"},
                    {"name": "lower heaven (stars)", "level": 1, "kind": "HEAVEN"},
                    {"name": "earth (Babylon at the centre)", "level": 0, "kind": "MIDDLE"},
                    {"name": "Apsû (Ea's sweet-water deep)", "level": -1, "kind": "UNDER"},
                    {"name": "Irkalla / Kur (seven gates)", "level": -2, "kind": "UNDER"},
                ],
            },
            "PROC": {
                "grade": "🟢", "scheduler": "MONARCHIC", "src": "Ee IV 1–34 (kingship conferred); the fifty names",
                "agents": [
                    {"name": "Anu", "roles": ["SOVEREIGN", "CREATOR"], "domain": ["sky", "kingship-source"], "ring": 0, "parent": None},
                    {"name": "Enlil", "roles": ["SOVEREIGN"], "domain": ["command", "Tablet of Destinies"], "ring": 0, "parent": "Anu"},
                    {"name": "Ea", "roles": ["CREATOR", "HEALER", "SCRIBE"], "domain": ["wisdom", "sweet water", "incantation"], "ring": 0, "parent": "Anu"},
                    {"name": "Marduk", "roles": ["SOVEREIGN", "WARRIOR", "CREATOR"], "domain": ["kingship", "storm", "order"], "ring": 0, "parent": "Ea"},
                    {"name": "Nabû", "roles": ["SCRIBE"], "domain": ["writing", "destinies"], "ring": 1, "parent": "Marduk"},
                    {"name": "Šamaš", "roles": ["JUDGE", "WITNESS"], "domain": ["sun", "justice", "extispicy"], "ring": 1, "parent": "Anu"},
                    {"name": "Sîn", "roles": ["SCHEDULER"], "domain": ["moon", "month"], "ring": 1, "parent": "Enlil"},
                    {"name": "Ištar", "roles": ["WARRIOR", "MOTHER"], "domain": ["love", "war", "Venus"], "ring": 1, "parent": "Anu"},
                    {"name": "Ereškigal", "roles": ["SOVEREIGN", "JUDGE"], "domain": ["underworld"], "ring": 1, "parent": None},
                    {"name": "Namtar", "roles": ["MESSENGER", "PSYCHOPOMP"], "domain": ["fate", "plague"], "ring": 2, "parent": "Ereškigal"},
                    {"name": "Tiāmat", "roles": ["ADVERSARY", "MOTHER"], "domain": ["salt water", "chaos"], "ring": 3, "parent": None},
                    {"name": "Kingu", "roles": ["ADVERSARY"], "domain": ["Tablet of Destinies (usurped)"], "ring": 3, "parent": "Tiāmat"},
                ],
            },
            "CLOCK": {
                "grade": "🟢", "src": "MUL.APIN II ii; the 19-year cycle attested from the 5th c. BCE",
                "periods": [
                    {"name": "day", "length": 1, "unit": "day"},
                    {"name": "month (lunar)", "length": 29.53, "unit": "day"},
                    {"name": "year (12 lunar months)", "length": 354.37, "unit": "day", "role": "year"},
                    {"name": "ideal year", "length": 360, "unit": "day"},
                ],
                "intercalation": {"policy": "LUNISOLAR_MONTH", "rule": "seven intercalary months in nineteen years (Metonic, standardised c. 500 BCE); earlier by royal decree",
                                  "months_per_cycle": 7, "cycle_years": 19},
                "epochs": ["šuš (60)", "nēr (600)", "šār (3600)"],
                "festivals": [{"name": "Akītu (New Year)", "when": "Nisannu 1–11", "day": 1}, {"name": "Akītu of Tašrītu", "when": "month VII", "day": 178}],
            },
            "RITE": {
                "grade": "🟢", "src": "Akītu ritual (Linssen 2004); namburbi (Maul 1994)",
                "protocols": [
                    {"name": "Akītu day 4–5: recitation of Enūma Eliš and the king's humiliation", "required_ring": 0, "mode": "MAINTAINING",
                     "steps": ["PURIFY", "BOUND", "RECITE", "INVOKE", "OFFER", "PETITION", "WITNESS", "RECEIVE", "CLOSE"],
                     "cost": "the king's regalia removed; the king slapped and made to weep", "effect": "kingship renewed; destinies fixed for the year"},
                    {"name": "namburbi (release from a portended evil)", "required_ring": 1, "mode": "TRANSFORMING",
                     "steps": ["PURIFY", "BOUND", "INVOKE", "OFFER", "PETITION", "TRANSFORM", "RELEASE", "CLOSE"],
                     "cost": "substitute figure, offerings to Šamaš and Ea", "effect": "the evil is transferred to a substitute and sent downstream"},
                ],
            },
            "ORACLE": {
                "grade": "🟢", "src": "Bārûtu; Šumma ālu; Enūma Anu Enlil",
                "devices": [
                    {"name": "extispicy (liver of a sacrificed sheep)", "entropy": "BODY", "space": 2, "encoding": "BINARY",
                     "decoder": "bārûtu omen compendia: each zone favourable/unfavourable, tallied", "alphabet": ["favourable", "unfavourable"], "set_aside": None},
                    {"name": "celestial omens", "entropy": "SKY", "space": 70, "encoding": "N_ARY", "decoder": "Enūma Anu Enlil (c. 70 tablets)", "set_aside": None},
                ],
            },
            "FAULT": {
                "grade": "🟢", "src": "Atra-ḫasīs; Šurpu; namburbi",
                "faults": [
                    {"name": "the noise of humankind", "class": "COSMIC", "handler": ["plague", "drought", "famine", "flood"], "outcome": "REBOOT"},
                    {"name": "māmītu (broken oath / unknown transgression)", "class": "OATH_BREACH", "handler": ["Šurpu incantation series", "burning of onion, dates, wool"], "outcome": "RECOVERED"},
                    {"name": "portended evil (lumnu)", "class": "POLLUTION", "handler": "namburbi", "outcome": "RECOVERED"},
                    {"name": "usurping the Tablet of Destinies", "class": "HUBRIS", "handler": "defeat by Marduk", "outcome": "UNRECOVERABLE"},
                ],
            },
            "LEDGER": {
                "grade": "🟢", "model": "NONE", "src": "Ištar's Descent; Gilgameš XII",
                "soul": ["eṭemmu (ghost)", "zaqīqu (dream-spirit)"],
                "judgment": "no moral judgment; all the dead go to Irkalla; comfort depends on offerings by the living",
                "destinations": ["Irkalla (the house of dust)"],
            },
            "RING": {
                "grade": "🟢", "src": "Akītu ritual roles; āšipūtu",
                "rings": [
                    {"level": 0, "name": "king (šarru)"},
                    {"level": 1, "name": "šešgallu / āšipu / bārû (temple and exorcist priests)"},
                    {"level": 2, "name": "kalû, ērib bīti (lesser temple staff)"},
                    {"level": 3, "name": "laity"},
                ],
            },
            "CODEC": {
                "grade": "🟢", "src": "Ee VII; Atra-ḫasīs III",
                "record": {"medium": "TABLET", "script": "cuneiform", "base": 60},
                "hull": "Atra-ḫasīs' sealed boat (bitumen-caulked, roofed)",
                "compilers": ["the fifty names of Marduk (a name-table)", "namburbi templates", "kalû lament liturgies"],
            },
            "CONST": {
                "grade": "🟢",
                "constants": [
                    {"n": 60, "role": "closure", "what": "Anu's number; the base"},
                    {"n": 50, "role": "order", "what": "the fifty names of Marduk"},
                    {"n": 7, "role": "passage", "what": "the seven gates of Irkalla; seven evil spirits"},
                    {"n": 12, "role": "order", "what": "months; Marduk fixes twelve"},
                    {"n": 3, "role": "order", "what": "three heavens"},
                    {"n": 3600, "role": "record", "what": "šār"},
                ],
            },
            "LAW": {
                "grade": "🟢", "src": "Ee IV 19–26 (the word that creates and destroys); Codex Hammurapi prologue",
                "invariants": ["the Tablet of Destinies fixes fates for the year", "naming binds; the fifty names are the constitution",
                               "kingship descends from heaven and is renewed annually"],
                "acl": [{"ring": 0, "permitted": ["hold the Tablet of Destinies", "renew the year"]}, {"ring": 1, "permitted": ["read omens", "perform namburbi"]}],
                "canon": {"closed": False, "note": "scribal tradition, layered and copied over a millennium"},
            },
        },
    },
]
