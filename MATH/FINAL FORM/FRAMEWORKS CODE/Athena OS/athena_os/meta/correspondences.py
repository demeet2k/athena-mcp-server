"""
ATHENA OS — CROSS-TRADITION MAPPINGS
=====================================

The Rosetta Stone of Sacred Computation.

This module maps corresponding concepts across all 12 traditions
in ATHENA OS, enabling seamless translation and integration.

"The boundary encodes the bulk" — every tradition encodes
the same underlying truth through different symbolic systems.

TRADITIONS MAPPED:
    1. Greek/Hellenic (Aristotle, Plato, Pythagoras, Stoics)
    2. Hebrew/Jewish (Kabbalah, Gematria, Torah)
    3. Christian (Biblical typology, prophecy)
    4. Islamic (Quranic structure, geometry)
    5. Hindu (Vedanta, Tantra, Yoga)
    6. Buddhist (Vajrayana, Zen)
    7. Norse (Runes, Yggdrasil)
    8. Celtic (Ogham, Triadic)
    9. Egyptian (Maat, Duat)
    10. Yoruba (Ifa, Orisha)
    11. Zoroastrian (Amesha Spentas)
    12. Hermetic/Alchemical (Tria Prima, Operations)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Set
from enum import Enum, auto

# Import unified types
from ..unified_types import Element, B4, TypedTruth, Cause, Category, Lens


# =============================================================================
# TRADITION ENUM
# =============================================================================

class Tradition(Enum):
    """The 12 source traditions."""
    GREEK = "greek"
    HEBREW = "hebrew"
    CHRISTIAN = "christian"
    ISLAMIC = "islamic"
    HINDU = "hindu"
    BUDDHIST = "buddhist"
    NORSE = "norse"
    CELTIC = "celtic"
    EGYPTIAN = "egyptian"
    YORUBA = "yoruba"
    ZOROASTRIAN = "zoroastrian"
    HERMETIC = "hermetic"


# =============================================================================
# FOUR-FOLD CORRESPONDENCES
# =============================================================================

@dataclass
class FourFoldCorrespondence:
    """
    Four-fold correspondence across traditions.
    
    Every tradition has a four-fold structure that maps to:
    - The four elements (Fire, Air, Water, Earth)
    - The Klein-4 group (I, R, S, C)
    - The B4 truth values (⊥, 0, 1, ⊤)
    """
    
    element: Element
    b4: B4
    greek: str           # Element name
    hebrew: str          # Hebrew letter/sefirah
    christian: str       # Gospel/evangelist
    islamic: str         # Direction/pillar
    hindu: str           # Guna/tattva
    buddhist: str        # Element/aggregate
    norse: str           # Realm/direction
    celtic: str          # Festival/direction
    egyptian: str        # Son of Horus
    yoruba: str          # Orisha
    zoroastrian: str     # Amesha Spenta
    hermetic: str        # Tria Prima aspect


# The Four-Fold Master Table
FOUR_FOLD_TABLE: Dict[Element, FourFoldCorrespondence] = {
    Element.FIRE: FourFoldCorrespondence(
        element=Element.FIRE,
        b4=B4.ONE,
        greek="Πῦρ (Pyr)",
        hebrew="ש (Shin) / Netzach",
        christian="Mark / Lion",
        islamic="East / Hajj",
        hindu="Rajas / Tejas",
        buddhist="Fire / Samskara",
        norse="Muspelheim / South",
        celtic="Beltane / South",
        egyptian="Duamutef",
        yoruba="Shango",
        zoroastrian="Asha Vahishta",
        hermetic="Sulfur"
    ),
    Element.AIR: FourFoldCorrespondence(
        element=Element.AIR,
        b4=B4.TOP,
        greek="Ἀήρ (Aer)",
        hebrew="א (Aleph) / Yesod",
        christian="Matthew / Angel",
        islamic="South / Zakat",
        hindu="Sattva / Vayu",
        buddhist="Air / Vijnana",
        norse="Vanaheim / East",
        celtic="Imbolc / East",
        egyptian="Qebehsenuef",
        yoruba="Oya",
        zoroastrian="Spenta Armaiti",
        hermetic="Mercury"
    ),
    Element.WATER: FourFoldCorrespondence(
        element=Element.WATER,
        b4=B4.ZERO,
        greek="Ὕδωρ (Hydor)",
        hebrew="מ (Mem) / Chesed",
        christian="John / Eagle",
        islamic="West / Sawm",
        hindu="Tamas / Apas",
        buddhist="Water / Vedana",
        norse="Niflheim / West",
        celtic="Samhain / West",
        egyptian="Imsety",
        yoruba="Yemoja",
        zoroastrian="Haurvatat",
        hermetic="Salt"
    ),
    Element.EARTH: FourFoldCorrespondence(
        element=Element.EARTH,
        b4=B4.BOT,
        greek="Γῆ (Ge)",
        hebrew="ת (Tav) / Malkuth",
        christian="Luke / Ox",
        islamic="North / Salat",
        hindu="Prakriti / Prithvi",
        buddhist="Earth / Rupa",
        norse="Midgard / North",
        celtic="Lughnasadh / North",
        egyptian="Hapi",
        yoruba="Ogun",
        zoroastrian="Ameretat",
        hermetic="Body (Corpus)"
    ),
}


# =============================================================================
# NUMERICAL CORRESPONDENCES
# =============================================================================

@dataclass
class NumericalCorrespondence:
    """Sacred numbers across traditions."""
    
    value: int
    significance: str
    greek: str
    hebrew: str
    christian: str
    islamic: str
    hindu: str
    buddhist: str
    hermetic: str


SACRED_NUMBERS: Dict[int, NumericalCorrespondence] = {
    1: NumericalCorrespondence(
        value=1,
        significance="Unity, Source",
        greek="Monad (τὸ ἕν)",
        hebrew="Aleph (א) / Keter",
        christian="One God",
        islamic="Tawhid",
        hindu="Brahman",
        buddhist="Dharmakaya",
        hermetic="The All"
    ),
    3: NumericalCorrespondence(
        value=3,
        significance="Trinity, Process",
        greek="Triad (τριάς)",
        hebrew="Three Pillars",
        christian="Trinity",
        islamic="Three Aspects of Tawhid",
        hindu="Trimurti",
        buddhist="Three Jewels",
        hermetic="Tria Prima"
    ),
    4: NumericalCorrespondence(
        value=4,
        significance="Manifestation, Elements",
        greek="Tetrad / Elements",
        hebrew="YHVH / Four Worlds",
        christian="Four Gospels",
        islamic="Four Caliphs",
        hindu="Four Vedas",
        buddhist="Four Noble Truths",
        hermetic="Four Elements"
    ),
    7: NumericalCorrespondence(
        value=7,
        significance="Completion, Planets",
        greek="Seven Planets",
        hebrew="Seven Days / n₁=7",
        christian="Seven Churches",
        islamic="Seven Heavens",
        hindu="Seven Chakras",
        buddhist="Seven Factors",
        hermetic="Seven Metals"
    ),
    10: NumericalCorrespondence(
        value=10,
        significance="Completeness",
        greek="Decad / Tetractys",
        hebrew="Ten Sefirot",
        christian="Ten Commandments",
        islamic="Ten Companions",
        hindu="Ten Avatars",
        buddhist="Ten Perfections",
        hermetic="Ten Grades"
    ),
    12: NumericalCorrespondence(
        value=12,
        significance="Cosmic Order",
        greek="Twelve Olympians",
        hebrew="Twelve Tribes",
        christian="Twelve Apostles",
        islamic="Twelve Imams",
        hindu="Twelve Adityas",
        buddhist="Twelve Nidanas",
        hermetic="Twelve Signs"
    ),
    19: NumericalCorrespondence(
        value=19,
        significance="Prime of Primes",
        greek="19-year Metonic",
        hebrew="n₂=19 / Checksum",
        christian="19 in Revelation",
        islamic="Basmala (19 letters)",
        hindu="19 Upanishads",
        buddhist="19 Realms",
        hermetic="Great Year divisor"
    ),
    22: NumericalCorrespondence(
        value=22,
        significance="Structure, Paths",
        greek="22 in Tetractys",
        hebrew="22 Letters",
        christian="22 Revelation chapters",
        islamic="22 in Quran",
        hindu="22 Shruti",
        buddhist="22 Faculties",
        hermetic="22 Major Arcana"
    ),
}


# =============================================================================
# PROCESS CORRESPONDENCES
# =============================================================================

@dataclass
class ProcessCorrespondence:
    """Transformation processes across traditions."""
    
    stage: int
    name: str
    greek: str          # Aristotelian
    hebrew: str         # Kabbalistic
    hindu: str          # Yogic
    hermetic: str       # Alchemical
    buddhist: str       # Vajrayana


TRANSFORMATION_STAGES: List[ProcessCorrespondence] = [
    ProcessCorrespondence(
        stage=1,
        name="Dissolution",
        greek="Hyle (ὕλη)",
        hebrew="Tzimtzum",
        hindu="Pratyahara",
        hermetic="Nigredo",
        buddhist="Bardo of Dying"
    ),
    ProcessCorrespondence(
        stage=2,
        name="Purification",
        greek="Katharsis",
        hebrew="Tikkun",
        hindu="Tapas",
        hermetic="Albedo",
        buddhist="Bardo of Dharmata"
    ),
    ProcessCorrespondence(
        stage=3,
        name="Illumination",
        greek="Theoria",
        hebrew="Or Ein Sof",
        hindu="Samadhi",
        hermetic="Citrinitas",
        buddhist="Clear Light"
    ),
    ProcessCorrespondence(
        stage=4,
        name="Perfection",
        greek="Henosis",
        hebrew="Devekut",
        hindu="Moksha",
        hermetic="Rubedo",
        buddhist="Bardo of Becoming"
    ),
]


# =============================================================================
# LENS CORRESPONDENCES
# =============================================================================

@dataclass
class LensCorrespondence:
    """The four lenses across traditions."""
    
    lens: Lens
    greek: str
    hebrew: str
    hindu: str
    buddhist: str
    hermetic: str


LENS_TABLE: Dict[Lens, LensCorrespondence] = {
    Lens.SQUARE: LensCorrespondence(
        lens=Lens.SQUARE,
        greek="Arithmos (Number)",
        hebrew="Mispar (Number)",
        hindu="Sankhya (Enumeration)",
        buddhist="Abhidharma",
        hermetic="Geometry"
    ),
    Lens.FLOWER: LensCorrespondence(
        lens=Lens.FLOWER,
        greek="Logos (Reason)",
        hebrew="Sekhel (Intellect)",
        hindu="Buddhi (Intelligence)",
        buddhist="Prajna",
        hermetic="Analysis"
    ),
    Lens.CLOUD: LensCorrespondence(
        lens=Lens.CLOUD,
        greek="Tyche (Fortune)",
        hebrew="Mazal (Fate)",
        hindu="Karma (Action)",
        buddhist="Samsara",
        hermetic="Probability"
    ),
    Lens.FRACTAL: LensCorrespondence(
        lens=Lens.FRACTAL,
        greek="Physis (Nature)",
        hebrew="Olam (World)",
        hindu="Maya (Illusion)",
        buddhist="Sunyata",
        hermetic="Recursion"
    ),
}


# =============================================================================
# CAUSE CORRESPONDENCES
# =============================================================================

@dataclass
class CauseCorrespondence:
    """The four causes across traditions."""
    
    cause: Cause
    greek: str
    hebrew: str
    hindu: str
    buddhist: str
    hermetic: str


CAUSE_TABLE: Dict[Cause, CauseCorrespondence] = {
    Cause.MATERIAL: CauseCorrespondence(
        cause=Cause.MATERIAL,
        greek="Hyle (ὕλη)",
        hebrew="Assiah (Action)",
        hindu="Prakriti (Matter)",
        buddhist="Rupa (Form)",
        hermetic="Salt"
    ),
    Cause.FORMAL: CauseCorrespondence(
        cause=Cause.FORMAL,
        greek="Eidos (εἶδος)",
        hebrew="Yetzirah (Formation)",
        hindu="Svabhava (Nature)",
        buddhist="Dharma (Law)",
        hermetic="Sulfur"
    ),
    Cause.EFFICIENT: CauseCorrespondence(
        cause=Cause.EFFICIENT,
        greek="Kinesis (κίνησις)",
        hebrew="Briah (Creation)",
        hindu="Shakti (Power)",
        buddhist="Karma (Action)",
        hermetic="Mercury"
    ),
    Cause.FINAL: CauseCorrespondence(
        cause=Cause.FINAL,
        greek="Telos (τέλος)",
        hebrew="Atziluth (Emanation)",
        hindu="Moksha (Liberation)",
        buddhist="Nirvana",
        hermetic="Philosopher's Stone"
    ),
}


# =============================================================================
# TREE CORRESPONDENCES
# =============================================================================

@dataclass
class TreeCorrespondence:
    """The World Tree across traditions."""
    
    tradition: Tradition
    name: str
    levels: int
    realms: List[str]
    root: str
    crown: str


WORLD_TREES: Dict[Tradition, TreeCorrespondence] = {
    Tradition.HEBREW: TreeCorrespondence(
        tradition=Tradition.HEBREW,
        name="Etz Chaim (Tree of Life)",
        levels=10,
        realms=["Keter", "Chokmah", "Binah", "Chesed", "Geburah", 
                "Tiferet", "Netzach", "Hod", "Yesod", "Malkuth"],
        root="Malkuth (Kingdom)",
        crown="Keter (Crown)"
    ),
    Tradition.NORSE: TreeCorrespondence(
        tradition=Tradition.NORSE,
        name="Yggdrasil",
        levels=9,
        realms=["Asgard", "Vanaheim", "Alfheim", "Midgard", "Jotunheim",
                "Svartalfheim", "Niflheim", "Muspelheim", "Helheim"],
        root="Hel/Nidhogg",
        crown="Asgard"
    ),
    Tradition.HINDU: TreeCorrespondence(
        tradition=Tradition.HINDU,
        name="Ashvattha (Cosmic Tree)",
        levels=7,
        realms=["Muladhara", "Svadhisthana", "Manipura", "Anahata",
                "Vishuddha", "Ajna", "Sahasrara"],
        root="Muladhara",
        crown="Sahasrara"
    ),
    Tradition.HERMETIC: TreeCorrespondence(
        tradition=Tradition.HERMETIC,
        name="Arbor Philosophica",
        levels=7,
        realms=["Saturn/Lead", "Jupiter/Tin", "Mars/Iron", "Sun/Gold",
                "Venus/Copper", "Mercury/Quicksilver", "Moon/Silver"],
        root="Saturn (Nigredo)",
        crown="Gold (Rubedo)"
    ),
}


# =============================================================================
# TRANSLATION FUNCTIONS
# =============================================================================

def translate_element(element: Element, from_tradition: Tradition, 
                      to_tradition: Tradition) -> str:
    """Translate element concept between traditions."""
    corr = FOUR_FOLD_TABLE.get(element)
    if not corr:
        return element.name
    
    tradition_map = {
        Tradition.GREEK: corr.greek,
        Tradition.HEBREW: corr.hebrew,
        Tradition.CHRISTIAN: corr.christian,
        Tradition.ISLAMIC: corr.islamic,
        Tradition.HINDU: corr.hindu,
        Tradition.BUDDHIST: corr.buddhist,
        Tradition.NORSE: corr.norse,
        Tradition.CELTIC: corr.celtic,
        Tradition.EGYPTIAN: corr.egyptian,
        Tradition.YORUBA: corr.yoruba,
        Tradition.ZOROASTRIAN: corr.zoroastrian,
        Tradition.HERMETIC: corr.hermetic,
    }
    return tradition_map.get(to_tradition, element.name)


def translate_number(value: int, to_tradition: Tradition) -> Optional[str]:
    """Get significance of number in tradition."""
    corr = SACRED_NUMBERS.get(value)
    if not corr:
        return None
    
    tradition_map = {
        Tradition.GREEK: corr.greek,
        Tradition.HEBREW: corr.hebrew,
        Tradition.CHRISTIAN: corr.christian,
        Tradition.ISLAMIC: corr.islamic,
        Tradition.HINDU: corr.hindu,
        Tradition.BUDDHIST: corr.buddhist,
        Tradition.HERMETIC: corr.hermetic,
    }
    return tradition_map.get(to_tradition)


def get_transformation_stage(stage: int, tradition: Tradition) -> Optional[str]:
    """Get transformation stage name in tradition."""
    if stage < 1 or stage > len(TRANSFORMATION_STAGES):
        return None
    
    corr = TRANSFORMATION_STAGES[stage - 1]
    tradition_map = {
        Tradition.GREEK: corr.greek,
        Tradition.HEBREW: corr.hebrew,
        Tradition.HINDU: corr.hindu,
        Tradition.BUDDHIST: corr.buddhist,
        Tradition.HERMETIC: corr.hermetic,
    }
    return tradition_map.get(tradition, corr.name)


# =============================================================================
# MASTER CORRESPONDENCE TABLE
# =============================================================================

def print_four_fold_table() -> str:
    """Generate printable four-fold correspondence table."""
    lines = []
    lines.append("╔════════════════════════════════════════════════════════════════════════════════════╗")
    lines.append("║                    FOUR-FOLD MASTER CORRESPONDENCE TABLE                          ║")
    lines.append("╠════════════════════════════════════════════════════════════════════════════════════╣")
    
    for element in [Element.FIRE, Element.AIR, Element.WATER, Element.EARTH]:
        corr = FOUR_FOLD_TABLE[element]
        lines.append(f"║ {element.name:6} ({corr.b4.glyph})                                                              ║")
        lines.append(f"║   Greek: {corr.greek:20} Hebrew: {corr.hebrew:20}              ║")
        lines.append(f"║   Hindu: {corr.hindu:20} Buddhist: {corr.buddhist:18}              ║")
        lines.append(f"║   Norse: {corr.norse:20} Celtic: {corr.celtic:20}              ║")
        lines.append(f"║   Hermetic: {corr.hermetic:17} Egyptian: {corr.egyptian:18}              ║")
        lines.append("║────────────────────────────────────────────────────────────────────────────────────║")
    
    lines.append("╚════════════════════════════════════════════════════════════════════════════════════╝")
    return "\n".join(lines)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    'Tradition',
    
    # Correspondences
    'FourFoldCorrespondence', 'FOUR_FOLD_TABLE',
    'NumericalCorrespondence', 'SACRED_NUMBERS',
    'ProcessCorrespondence', 'TRANSFORMATION_STAGES',
    'LensCorrespondence', 'LENS_TABLE',
    'CauseCorrespondence', 'CAUSE_TABLE',
    'TreeCorrespondence', 'WORLD_TREES',
    
    # Functions
    'translate_element', 'translate_number', 'get_transformation_stage',
    'print_four_fold_table',
]


# =============================================================================
# VERIFICATION
# =============================================================================

if __name__ == "__main__":
    print("=== ATHENA OS CROSS-TRADITION MAPPINGS ===\n")
    
    # Print the four-fold table
    print(print_four_fold_table())
    
    # Test translations
    print("\n=== ELEMENT TRANSLATIONS ===")
    for element in [Element.FIRE, Element.WATER]:
        print(f"\n{element.name}:")
        for tradition in [Tradition.GREEK, Tradition.HEBREW, Tradition.HINDU, Tradition.HERMETIC]:
            translated = translate_element(element, Tradition.GREEK, tradition)
            print(f"  {tradition.value}: {translated}")
    
    # Test number translations
    print("\n=== SACRED NUMBER 22 ===")
    for tradition in [Tradition.GREEK, Tradition.HEBREW, Tradition.BUDDHIST, Tradition.HERMETIC]:
        sig = translate_number(22, tradition)
        print(f"  {tradition.value}: {sig}")
    
    # Test transformation stages
    print("\n=== TRANSFORMATION STAGES ===")
    for stage in range(1, 5):
        print(f"\nStage {stage}:")
        for tradition in [Tradition.GREEK, Tradition.HEBREW, Tradition.HERMETIC]:
            name = get_transformation_stage(stage, tradition)
            print(f"  {tradition.value}: {name}")
    
    print("\n=== CROSS-TRADITION MAPPINGS VERIFIED ===")
