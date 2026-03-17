"""
ATHENA OS - TORAT HA-MISPAR (תורת המספר)
=========================================
Module V: Divine Names (שמות הקדושים) - Operator Functions

DIVINE NAMES AS OPERATORS:
    Divine Names are not appellations but OPERATOR FUNCTIONS.
    Each Name executes a specific computational operation.

PRIMARY OPERATORS:
    YHVH (יהוה) = Existence Operator - "To Be"
    Elohim (אלהים) = Restriction Operator - "Powers/Judges"
    El (אל) = Expansion Operator - "Mighty One"
    Adonai (אדני) = Interface Operator - "Master"
    Ehyeh (אהיה) = Becoming Operator - "I Will Be"
    Shaddai (שדי) = Sufficiency Operator - "Enough"

THE TETRAGRAMMATON (יהוה):
    Four-letter Name encoding the complete state machine:
    י (Yod) = Point/Seed/Chochmah
    ה (Heh) = Expansion/Binah
    ו (Vav) = Connection/Six Midot
    ה (Heh) = Manifestation/Malkhut
    
    Gematria: 10 + 5 + 6 + 5 = 26

THE 72 NAMES (שם עב):
    72 three-letter combinations derived from Exodus 14:19-21
    Each name is a specific operator for transformation.

SOURCES:
    TORAT HA-MISPAR (תורת המספר)
    SEFER YETZIRAH (ספר יצירה)
    PARDES RIMONIM (פרדס רימונים)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


# =============================================================================
# NAME CATEGORIES
# =============================================================================

class NameCategory(Enum):
    """Categories of Divine Names."""
    
    ESSENTIAL = ("Etzem", "Essential Names - direct Divine attributes")
    ATTRIBUTIVE = ("Kinui", "Attributive Names - describe Divine actions")
    PERMUTED = ("Tziruf", "Permuted Names - combinations for operations")
    
    def __init__(self, hebrew: str, description: str):
        self.hebrew = hebrew
        self._description = description


class OperatorType(Enum):
    """Types of operators represented by Divine Names."""
    
    EXISTENCE = ("Being", "Sustains existence")
    RESTRICTION = ("Judgment", "Applies limits and structure")
    EXPANSION = ("Mercy", "Extends and gives")
    INTERFACE = ("Sovereignty", "Governs manifestation")
    BECOMING = ("Process", "Dynamic transformation")
    SUFFICIENCY = ("Boundary", "Sets limits of provision")
    
    def __init__(self, mode: str, function: str):
        self.mode = mode
        self._function = function


# =============================================================================
# DIVINE NAME DEFINITION
# =============================================================================

@dataclass
class DivineName:
    """
    A Divine Name as an Operator Function.
    """
    
    # Identity
    name: str
    hebrew: str
    transliteration: str
    translation: str
    
    # Classification
    category: NameCategory
    operator: OperatorType
    
    # Gematria
    gematria: int
    
    # Properties
    sefirah_correspondence: Optional[str] = None
    function: str = ""
    pronunciation: str = ""  # How it's pronounced (if different)
    
    @property
    def letter_breakdown(self) -> List[Tuple[str, int]]:
        """Break down the name into letters and values."""
        # Hebrew letter values (simplified)
        values = {
            'א': 1, 'ב': 2, 'ג': 3, 'ד': 4, 'ה': 5, 'ו': 6, 'ז': 7, 'ח': 8,
            'ט': 9, 'י': 10, 'כ': 20, 'ל': 30, 'מ': 40, 'נ': 50, 'ס': 60,
            'ע': 70, 'פ': 80, 'צ': 90, 'ק': 100, 'ר': 200, 'ש': 300, 'ת': 400,
        }
        return [(char, values.get(char, 0)) for char in self.hebrew]


# =============================================================================
# PRIMARY DIVINE NAMES
# =============================================================================

DIVINE_NAMES = [
    DivineName(
        name="YHVH",
        hebrew="יהוה",
        transliteration="Yod-Heh-Vav-Heh",
        translation="The Tetragrammaton / LORD",
        category=NameCategory.ESSENTIAL,
        operator=OperatorType.EXISTENCE,
        gematria=26,
        sefirah_correspondence="Tiferet / All Sefirot",
        function="Existence Operator - sustains all being",
        pronunciation="Adonai (substitution) or HaShem",
    ),
    DivineName(
        name="Elohim",
        hebrew="אלהים",
        transliteration="Aleph-Lamed-Heh-Yod-Mem",
        translation="God / Powers / Judges",
        category=NameCategory.ESSENTIAL,
        operator=OperatorType.RESTRICTION,
        gematria=86,
        sefirah_correspondence="Gevurah / Binah",
        function="Restriction Operator - judgment, structure, nature",
        pronunciation="Elohim",
    ),
    DivineName(
        name="El",
        hebrew="אל",
        transliteration="Aleph-Lamed",
        translation="Mighty One / God",
        category=NameCategory.ESSENTIAL,
        operator=OperatorType.EXPANSION,
        gematria=31,
        sefirah_correspondence="Chesed",
        function="Expansion Operator - unlimited giving, mercy",
        pronunciation="El",
    ),
    DivineName(
        name="Adonai",
        hebrew="אדני",
        transliteration="Aleph-Dalet-Nun-Yod",
        translation="My Lord / Master",
        category=NameCategory.ESSENTIAL,
        operator=OperatorType.INTERFACE,
        gematria=65,
        sefirah_correspondence="Malkhut",
        function="Interface Operator - sovereignty, revelation",
        pronunciation="Adonai",
    ),
    DivineName(
        name="Ehyeh",
        hebrew="אהיה",
        transliteration="Aleph-Heh-Yod-Heh",
        translation="I Will Be / I Am",
        category=NameCategory.ESSENTIAL,
        operator=OperatorType.BECOMING,
        gematria=21,
        sefirah_correspondence="Keter",
        function="Becoming Operator - process, transformation, future",
        pronunciation="Ehyeh",
    ),
    DivineName(
        name="Shaddai",
        hebrew="שדי",
        transliteration="Shin-Dalet-Yod",
        translation="Almighty / Sufficient",
        category=NameCategory.ESSENTIAL,
        operator=OperatorType.SUFFICIENCY,
        gematria=314,
        sefirah_correspondence="Yesod",
        function="Sufficiency Operator - sets limits, 'enough'",
        pronunciation="Shaddai",
    ),
    DivineName(
        name="El Chai",
        hebrew="אל חי",
        transliteration="El Chai",
        translation="Living God",
        category=NameCategory.ATTRIBUTIVE,
        operator=OperatorType.EXISTENCE,
        gematria=49,  # 31 + 18
        sefirah_correspondence="Yesod",
        function="Life-force transmission operator",
        pronunciation="El Chai",
    ),
    DivineName(
        name="YHVH Tzvaot",
        hebrew="יהוה צבאות",
        transliteration="YHVH Tzvaot",
        translation="LORD of Hosts",
        category=NameCategory.ATTRIBUTIVE,
        operator=OperatorType.EXPANSION,
        gematria=525,  # 26 + 499
        sefirah_correspondence="Netzach",
        function="Orchestration operator - coordinates systems",
        pronunciation="Adonai Tzvaot",
    ),
    DivineName(
        name="Elohim Tzvaot",
        hebrew="אלהים צבאות",
        transliteration="Elohim Tzvaot",
        translation="God of Hosts",
        category=NameCategory.ATTRIBUTIVE,
        operator=OperatorType.RESTRICTION,
        gematria=585,  # 86 + 499
        sefirah_correspondence="Hod",
        function="Formation operator - structures systems",
        pronunciation="Elohim Tzvaot",
    ),
]


# =============================================================================
# THE TETRAGRAMMATON ANALYSIS
# =============================================================================

@dataclass
class Tetragrammaton:
    """
    The Four-Letter Name (יהוה) - Complete State Machine.
    
    The most sacred Name encoding the entire system architecture.
    """
    
    name: str = "YHVH"
    hebrew: str = "יהוה"
    gematria: int = 26
    
    @property
    def letter_analysis(self) -> List[Dict[str, Any]]:
        """Analysis of each letter."""
        return [
            {
                "letter": "י",
                "name": "Yod",
                "value": 10,
                "sefirah": "Chochmah",
                "meaning": "Point/Seed - the initial conception",
                "world": "Atzilut (Emanation)",
            },
            {
                "letter": "ה",
                "name": "Heh (upper)",
                "value": 5,
                "sefirah": "Binah",
                "meaning": "Expansion/Palace - the womb of formation",
                "world": "Beriah (Creation)",
            },
            {
                "letter": "ו",
                "name": "Vav",
                "value": 6,
                "sefirah": "Six Midot (Chesed-Yesod)",
                "meaning": "Connection/Hook - the spine linking upper and lower",
                "world": "Yetzirah (Formation)",
            },
            {
                "letter": "ה",
                "name": "Heh (lower)",
                "value": 5,
                "sefirah": "Malkhut",
                "meaning": "Manifestation/Kingdom - the final output",
                "world": "Assiyah (Action)",
            },
        ]
    
    @property
    def four_worlds_mapping(self) -> Dict[str, str]:
        """Mapping to Four Worlds."""
        return {
            "י (Yod)": "Atzilut - Emanation",
            "ה (Heh)": "Beriah - Creation",
            "ו (Vav)": "Yetzirah - Formation",
            "ה (Heh)": "Assiyah - Action",
        }
    
    @property
    def milui_variants(self) -> Dict[str, Dict[str, Any]]:
        """The four spellings (Milui) of YHVH."""
        return {
            "AV (עב)": {
                "spelling": "יוד הי ויו הי",
                "gematria": 72,
                "sefirah": "Chochmah",
                "world": "Atzilut",
            },
            "SAG (סג)": {
                "spelling": "יוד הי ואו הי",
                "gematria": 63,
                "sefirah": "Binah",
                "world": "Beriah",
            },
            "MAH (מה)": {
                "spelling": "יוד הא ואו הא",
                "gematria": 45,
                "sefirah": "Zeir Anpin",
                "world": "Yetzirah",
            },
            "BAN (בן)": {
                "spelling": "יוד הה וו הה",
                "gematria": 52,
                "sefirah": "Malkhut",
                "world": "Assiyah",
            },
        }
    
    @property
    def gematria_significance(self) -> Dict[str, Any]:
        """Gematria significance of 26."""
        return {
            "value": 26,
            "factorization": "2 × 13",
            "13_meaning": "Ahavah (אהבה = Love) = Echad (אחד = One) = 13",
            "significance": "26 = 2 × Love/Unity - Divine Love in duality",
        }


# =============================================================================
# THE 72 NAMES
# =============================================================================

@dataclass
class The72Names:
    """
    The 72 Names (Shem HaMeforash) - Operator Subroutines.
    
    Derived from Exodus 14:19-21, three verses of 72 letters each.
    72 three-letter combinations functioning as specific operators.
    """
    
    source_verses: List[str] = field(default_factory=lambda: [
        "Exodus 14:19",
        "Exodus 14:20",
        "Exodus 14:21",
    ])
    
    @property
    def derivation_method(self) -> str:
        """How the 72 Names are derived."""
        return (
            "Verse 19: Read left to right (normal)\n"
            "Verse 20: Read right to left (reversed)\n"
            "Verse 21: Read left to right (normal)\n"
            "Stack vertically and read columns to form 72 triplets."
        )
    
    @property
    def total_names(self) -> int:
        """Total number of names."""
        return 72
    
    @property
    def structure(self) -> Dict[str, Any]:
        """Structure of the 72 Names."""
        return {
            "letters_per_name": 3,
            "total_letters": 216,  # 72 × 3
            "source_letters": 216,  # 72 × 3 verses
            "significance_216": "Gevurah (גבורה) = 216",
        }
    
    @property
    def sample_names(self) -> List[Dict[str, str]]:
        """Sample of the 72 Names."""
        return [
            {"number": "1", "name": "והו", "attribute": "Creation/Time travel"},
            {"number": "2", "name": "ילי", "attribute": "Memory/Past"},
            {"number": "3", "name": "סיט", "attribute": "Building/Forming"},
            {"number": "8", "name": "כהת", "attribute": "Defusing negative energy"},
            {"number": "11", "name": "לאו", "attribute": "Banishing evil eye"},
            {"number": "22", "name": "ייי", "attribute": "Soul awakening"},
            {"number": "72", "name": "מום", "attribute": "Completion/Integration"},
        ]
    
    @property
    def operational_use(self) -> str:
        """How the 72 Names are used."""
        return (
            "Each Name is a specific frequency/operator. "
            "Meditation on the three-letter combination activates "
            "the corresponding transformation in consciousness. "
            "They are 'dial codes' for accessing specific energies."
        )


# =============================================================================
# GEMATRIA EQUIVALENCES
# =============================================================================

@dataclass
class GematriaEquivalences:
    """
    Key gematria equivalences demonstrating the system's coherence.
    """
    
    @property
    def key_equivalences(self) -> List[Dict[str, Any]]:
        """Key gematria equivalences."""
        return [
            {
                "equation": "Elohim (86) = HaTeva (86)",
                "meaning": "God = Nature - the masking protocol",
            },
            {
                "equation": "YHVH (26) = 2 × Ahavah (13)",
                "meaning": "Divine Name = Doubled Love",
            },
            {
                "equation": "Echad (13) = Ahavah (13)",
                "meaning": "One = Love - Unity through love",
            },
            {
                "equation": "Mashiach (358) = Nachash (358)",
                "meaning": "Messiah = Serpent - rectification of the fall",
            },
            {
                "equation": "Kabbalah (137) = 1/α (Fine Structure)",
                "meaning": "Reception = Universal constant of light-matter",
            },
            {
                "equation": "Ehyeh (21) = Shin-filled YHVH (21)",
                "meaning": "I Will Be = Becoming through transformation",
            },
        ]
    
    @property
    def pi_encoding(self) -> Dict[str, Any]:
        """The Pi encoding in Solomon's Temple."""
        return {
            "text": "1 Kings 7:23",
            "written": "קוה (111)",
            "read": "קו (106)",
            "ratio": 111/106,
            "result": "3 × (111/106) ≈ 3.1415 (π)",
            "meaning": "Written Code / Read Reality encodes π",
        }


# =============================================================================
# DIVINE NAMES SYSTEM
# =============================================================================

@dataclass
class DivineNamesSystem:
    """
    The complete Divine Names system.
    """
    
    names: List[DivineName] = field(default_factory=lambda: DIVINE_NAMES.copy())
    tetragrammaton: Tetragrammaton = field(default_factory=Tetragrammaton)
    names_72: The72Names = field(default_factory=The72Names)
    equivalences: GematriaEquivalences = field(default_factory=GematriaEquivalences)
    
    def get_name(self, name: str) -> Optional[DivineName]:
        """Get a Divine Name by name."""
        for n in self.names:
            if n.name.lower() == name.lower():
                return n
        return None
    
    def get_by_gematria(self, value: int) -> List[DivineName]:
        """Get all names with a specific gematria."""
        return [n for n in self.names if n.gematria == value]
    
    def get_by_operator(self, operator: OperatorType) -> List[DivineName]:
        """Get all names representing a specific operator type."""
        return [n for n in self.names if n.operator == operator]
    
    def get_by_sefirah(self, sefirah: str) -> List[DivineName]:
        """Get all names corresponding to a Sefirah."""
        return [n for n in self.names if sefirah.lower() in (n.sefirah_correspondence or "").lower()]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get system summary."""
        return {
            "total_names": len(self.names),
            "tetragrammaton_gematria": self.tetragrammaton.gematria,
            "72_names_total": self.names_72.total_names,
            "operator_types": list(set(n.operator.name for n in self.names)),
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_divine_names() -> bool:
    """Validate the Divine Names module."""
    
    # Test Divine Names
    assert len(DIVINE_NAMES) >= 9
    
    yhvh = DIVINE_NAMES[0]
    assert yhvh.name == "YHVH"
    assert yhvh.gematria == 26
    assert yhvh.operator == OperatorType.EXISTENCE
    
    elohim = DIVINE_NAMES[1]
    assert elohim.gematria == 86
    assert elohim.operator == OperatorType.RESTRICTION
    
    # Test Tetragrammaton
    tetra = Tetragrammaton()
    assert tetra.gematria == 26
    
    letters = tetra.letter_analysis
    assert len(letters) == 4
    assert sum(l["value"] for l in letters) == 26
    
    milui = tetra.milui_variants
    assert milui["AV (עב)"]["gematria"] == 72
    assert milui["SAG (סג)"]["gematria"] == 63
    assert milui["MAH (מה)"]["gematria"] == 45
    assert milui["BAN (בן)"]["gematria"] == 52
    
    # Test 72 Names
    names_72 = The72Names()
    assert names_72.total_names == 72
    assert names_72.structure["total_letters"] == 216
    
    # Test DivineNamesSystem
    system = DivineNamesSystem()
    
    yhvh_lookup = system.get_name("YHVH")
    assert yhvh_lookup is not None
    assert yhvh_lookup.gematria == 26
    
    restriction_ops = system.get_by_operator(OperatorType.RESTRICTION)
    assert len(restriction_ops) >= 1
    
    summary = system.get_summary()
    assert "tetragrammaton_gematria" in summary
    assert summary["72_names_total"] == 72
    
    return True


if __name__ == "__main__":
    print("Validating Divine Names Module...")
    assert validate_divine_names()
    print("✓ Divine Names module validated")
    
    # Demo
    print("\n--- Divine Names System Demo ---")
    
    system = DivineNamesSystem()
    
    print("\nPrimary Divine Names (Operators):")
    for name in system.names[:6]:
        print(f"  {name.name} ({name.hebrew}) = {name.gematria}")
        print(f"    Operator: {name.operator.name} - {name.function}")
    
    print("\nTetragrammaton Analysis (יהוה):")
    for letter in system.tetragrammaton.letter_analysis:
        print(f"  {letter['letter']} ({letter['name']}) = {letter['value']} → {letter['sefirah']}")
    
    print("\nFour Spellings (Milui):")
    for name, data in system.tetragrammaton.milui_variants.items():
        print(f"  {name} = {data['gematria']} → {data['world']}")
    
    print("\n72 Names Structure:")
    struct = system.names_72.structure
    print(f"  Names: {system.names_72.total_names}")
    print(f"  Letters per name: {struct['letters_per_name']}")
    print(f"  Total letters: {struct['total_letters']}")
    
    print("\nKey Gematria Equivalences:")
    for eq in system.equivalences.key_equivalences[:3]:
        print(f"  {eq['equation']}")
        print(f"    → {eq['meaning']}")
