"""
ATHENA OS - TORAT HA-MISPAR (תורת המספר)
=========================================
Module III: Otiyot (אותיות) - The 22-Letter Instruction Set

THE OTIYOT DEFINED:
    The 22 letters of the Hebrew alphabet function as a complete
    instruction set for the cosmic operating system.
    
    22 = 3 Mothers + 7 Doubles + 12 Simples

THE THREE MOTHERS (אמ״ש):
    Aleph (א) = Air = Balancing Scalar = 1
    Mem (מ) = Water = Flow Vector = 40
    Shin (ש) = Fire = Transformative Operator = 300
    
    These are the PRIMITIVES - elemental continua

THE SEVEN DOUBLES (בגדכפר״ת):
    Binary switches with Hard/Soft states (Dagesh operator)
    Map to: 7 days, 7 planets, 7 orifices, 7 directions
    
    These are the BINARY SWITCHES - discrete state operators

THE TWELVE SIMPLES:
    Coordinate primitives mapping to Zodiac/Calendar
    Establish the Spatial-Temporal Grid (C₁₂ cyclic group)
    
    These are the COORDINATES - grid establishment

LETTER COMPONENTS:
    - Sound: Frequency/Waveform
    - Shape: Circuit Diagram / Vector Topology
    - Number: Gematria Value / Frequency Modulator

SOURCES:
    TORAT HA-MISPAR (תורת המספר)
    SEFER YETZIRAH (ספר יצירה)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


# =============================================================================
# LETTER CATEGORIES
# =============================================================================

class LetterCategory(Enum):
    """Categories of Hebrew letters."""
    
    MOTHER = ("Imot", "3 Elemental Primitives")
    DOUBLE = ("Kefulot", "7 Binary Switches")
    SIMPLE = ("Peshutot", "12 Coordinate Primitives")
    
    def __init__(self, hebrew_name: str, description: str):
        self.hebrew_name = hebrew_name
        self._description = description


class ArticulationPoint(Enum):
    """Points of articulation for Hebrew letters."""
    
    GUTTURAL = ("Throat", "א, ה, ח, ע", "Root Directory - Keter interface")
    LABIAL = ("Lips", "ב, ו, מ, פ", "External Interface - Malkhut interface")
    PALATAL = ("Palate", "ג, י, כ, ק", "Liquid State - transition")
    DENTAL = ("Teeth", "ז, ס, ש, ר, צ", "Cutting/Hardening function")
    LINGUAL = ("Tongue", "ד, ט, ל, נ, ת", "Shaping/Balance function")
    
    def __init__(self, location: str, letters: str, function: str):
        self.location = location
        self.letters = letters
        self._function = function


class Element(Enum):
    """Elemental correspondences."""
    
    FIRE = ("אש", "Transformation/Energy")
    WATER = ("מים", "Flow/Fluidity")
    AIR = ("אויר", "Balance/Mediation")
    EARTH = ("עפר", "Manifestation/Solidity")
    
    def __init__(self, hebrew: str, function: str):
        self.hebrew = hebrew
        self._function = function


# =============================================================================
# HEBREW LETTER DEFINITION
# =============================================================================

@dataclass
class HebrewLetter:
    """
    A Hebrew letter with all its properties.
    """
    
    # Identity
    letter: str
    name: str
    name_hebrew: str
    
    # Classification
    category: LetterCategory
    position: int  # 1-22
    
    # Numerical values
    standard_value: int  # Standard gematria
    ordinal_value: int   # Position in alphabet (1-22)
    
    # Phonetic properties
    articulation: ArticulationPoint
    sound: str
    
    # Mystical properties
    meaning: str
    element: Optional[Element] = None
    
    # Double letter properties (only for Doubles)
    has_dagesh: bool = False
    hard_sound: Optional[str] = None
    soft_sound: Optional[str] = None
    polarity_pair: Optional[Tuple[str, str]] = None
    
    # Spatial/Temporal (for Doubles and Simples)
    direction: Optional[str] = None
    planet: Optional[str] = None
    zodiac: Optional[str] = None
    month: Optional[str] = None
    
    @property
    def full_spelling_value(self) -> int:
        """Milui - full spelling value (simplified)."""
        # For complete implementation, would spell out the letter name
        return self.standard_value
    
    @property
    def atbash_pair(self) -> int:
        """Atbash cipher pair position."""
        return 23 - self.position  # Aleph↔Tav, Bet↔Shin, etc.


# =============================================================================
# THE COMPLETE ALPHABET
# =============================================================================

# The Three Mothers (אמ״ש)
MOTHERS = [
    HebrewLetter(
        letter="א", name="Aleph", name_hebrew="אלף",
        category=LetterCategory.MOTHER, position=1,
        standard_value=1, ordinal_value=1,
        articulation=ArticulationPoint.GUTTURAL,
        sound="Silent glottal", element=Element.AIR,
        meaning="Ox/Leadership - Balancing Scalar",
    ),
    HebrewLetter(
        letter="מ", name="Mem", name_hebrew="מם",
        category=LetterCategory.MOTHER, position=13,
        standard_value=40, ordinal_value=13,
        articulation=ArticulationPoint.LABIAL,
        sound="m", element=Element.WATER,
        meaning="Water - Flow Vector",
    ),
    HebrewLetter(
        letter="ש", name="Shin", name_hebrew="שין",
        category=LetterCategory.MOTHER, position=21,
        standard_value=300, ordinal_value=21,
        articulation=ArticulationPoint.DENTAL,
        sound="sh/s", element=Element.FIRE,
        meaning="Tooth/Fire - Transformative Operator",
    ),
]

# The Seven Doubles (בגדכפר״ת)
DOUBLES = [
    HebrewLetter(
        letter="ב", name="Bet", name_hebrew="בית",
        category=LetterCategory.DOUBLE, position=2,
        standard_value=2, ordinal_value=2,
        articulation=ArticulationPoint.LABIAL,
        sound="b/v", has_dagesh=True,
        hard_sound="b", soft_sound="v",
        meaning="House/Container",
        polarity_pair=("Life", "Death"),
        direction="Up", planet="Saturn",
    ),
    HebrewLetter(
        letter="ג", name="Gimel", name_hebrew="גימל",
        category=LetterCategory.DOUBLE, position=3,
        standard_value=3, ordinal_value=3,
        articulation=ArticulationPoint.PALATAL,
        sound="g/gh", has_dagesh=True,
        hard_sound="g", soft_sound="gh",
        meaning="Camel/Movement",
        polarity_pair=("Peace", "War"),
        direction="Down", planet="Jupiter",
    ),
    HebrewLetter(
        letter="ד", name="Dalet", name_hebrew="דלת",
        category=LetterCategory.DOUBLE, position=4,
        standard_value=4, ordinal_value=4,
        articulation=ArticulationPoint.LINGUAL,
        sound="d/dh", has_dagesh=True,
        hard_sound="d", soft_sound="dh",
        meaning="Door/Pathway",
        polarity_pair=("Wisdom", "Folly"),
        direction="East", planet="Mars",
    ),
    HebrewLetter(
        letter="כ", name="Kaf", name_hebrew="כף",
        category=LetterCategory.DOUBLE, position=11,
        standard_value=20, ordinal_value=11,
        articulation=ArticulationPoint.PALATAL,
        sound="k/kh", has_dagesh=True,
        hard_sound="k", soft_sound="kh",
        meaning="Palm/Crown",
        polarity_pair=("Wealth", "Poverty"),
        direction="West", planet="Sun",
    ),
    HebrewLetter(
        letter="פ", name="Peh", name_hebrew="פא",
        category=LetterCategory.DOUBLE, position=17,
        standard_value=80, ordinal_value=17,
        articulation=ArticulationPoint.LABIAL,
        sound="p/f", has_dagesh=True,
        hard_sound="p", soft_sound="f",
        meaning="Mouth/Speech",
        polarity_pair=("Dominion", "Slavery"),
        direction="North", planet="Venus",
    ),
    HebrewLetter(
        letter="ר", name="Resh", name_hebrew="ריש",
        category=LetterCategory.DOUBLE, position=20,
        standard_value=200, ordinal_value=20,
        articulation=ArticulationPoint.DENTAL,
        sound="r", has_dagesh=True,
        hard_sound="r (rolled)", soft_sound="r (soft)",
        meaning="Head/Beginning",
        polarity_pair=("Grace", "Ugliness"),
        direction="South", planet="Mercury",
    ),
    HebrewLetter(
        letter="ת", name="Tav", name_hebrew="תו",
        category=LetterCategory.DOUBLE, position=22,
        standard_value=400, ordinal_value=22,
        articulation=ArticulationPoint.LINGUAL,
        sound="t/th", has_dagesh=True,
        hard_sound="t", soft_sound="th",
        meaning="Mark/Seal/Completion",
        polarity_pair=("Life", "Death"),
        direction="Center", planet="Moon",
    ),
]

# The Twelve Simples
SIMPLES = [
    HebrewLetter(
        letter="ה", name="Heh", name_hebrew="הא",
        category=LetterCategory.SIMPLE, position=5,
        standard_value=5, ordinal_value=5,
        articulation=ArticulationPoint.GUTTURAL,
        sound="h", meaning="Window/Revelation",
        zodiac="Aries", month="Nisan",
    ),
    HebrewLetter(
        letter="ו", name="Vav", name_hebrew="וו",
        category=LetterCategory.SIMPLE, position=6,
        standard_value=6, ordinal_value=6,
        articulation=ArticulationPoint.LABIAL,
        sound="v/w", meaning="Hook/Connection",
        zodiac="Taurus", month="Iyar",
    ),
    HebrewLetter(
        letter="ז", name="Zayin", name_hebrew="זין",
        category=LetterCategory.SIMPLE, position=7,
        standard_value=7, ordinal_value=7,
        articulation=ArticulationPoint.DENTAL,
        sound="z", meaning="Sword/Weapon",
        zodiac="Gemini", month="Sivan",
    ),
    HebrewLetter(
        letter="ח", name="Chet", name_hebrew="חית",
        category=LetterCategory.SIMPLE, position=8,
        standard_value=8, ordinal_value=8,
        articulation=ArticulationPoint.GUTTURAL,
        sound="ch (guttural)", meaning="Fence/Life",
        zodiac="Cancer", month="Tammuz",
    ),
    HebrewLetter(
        letter="ט", name="Tet", name_hebrew="טית",
        category=LetterCategory.SIMPLE, position=9,
        standard_value=9, ordinal_value=9,
        articulation=ArticulationPoint.LINGUAL,
        sound="t (emphatic)", meaning="Serpent/Good",
        zodiac="Leo", month="Av",
    ),
    HebrewLetter(
        letter="י", name="Yod", name_hebrew="יוד",
        category=LetterCategory.SIMPLE, position=10,
        standard_value=10, ordinal_value=10,
        articulation=ArticulationPoint.PALATAL,
        sound="y", meaning="Hand/Point",
        zodiac="Virgo", month="Elul",
    ),
    HebrewLetter(
        letter="ל", name="Lamed", name_hebrew="למד",
        category=LetterCategory.SIMPLE, position=12,
        standard_value=30, ordinal_value=12,
        articulation=ArticulationPoint.LINGUAL,
        sound="l", meaning="Goad/Teaching",
        zodiac="Libra", month="Tishrei",
    ),
    HebrewLetter(
        letter="נ", name="Nun", name_hebrew="נון",
        category=LetterCategory.SIMPLE, position=14,
        standard_value=50, ordinal_value=14,
        articulation=ArticulationPoint.LINGUAL,
        sound="n", meaning="Fish/Continuation",
        zodiac="Scorpio", month="Cheshvan",
    ),
    HebrewLetter(
        letter="ס", name="Samekh", name_hebrew="סמך",
        category=LetterCategory.SIMPLE, position=15,
        standard_value=60, ordinal_value=15,
        articulation=ArticulationPoint.DENTAL,
        sound="s", meaning="Support/Structure",
        zodiac="Sagittarius", month="Kislev",
    ),
    HebrewLetter(
        letter="ע", name="Ayin", name_hebrew="עין",
        category=LetterCategory.SIMPLE, position=16,
        standard_value=70, ordinal_value=16,
        articulation=ArticulationPoint.GUTTURAL,
        sound="Silent/guttural", meaning="Eye/Perception",
        zodiac="Capricorn", month="Tevet",
    ),
    HebrewLetter(
        letter="צ", name="Tzadi", name_hebrew="צדי",
        category=LetterCategory.SIMPLE, position=18,
        standard_value=90, ordinal_value=18,
        articulation=ArticulationPoint.DENTAL,
        sound="ts", meaning="Fishhook/Righteous",
        zodiac="Aquarius", month="Shevat",
    ),
    HebrewLetter(
        letter="ק", name="Qof", name_hebrew="קוף",
        category=LetterCategory.SIMPLE, position=19,
        standard_value=100, ordinal_value=19,
        articulation=ArticulationPoint.PALATAL,
        sound="k (deep)", meaning="Back of head/Holy",
        zodiac="Pisces", month="Adar",
    ),
]

# Complete alphabet (sorted by position)
ALPHABET = sorted(MOTHERS + DOUBLES + SIMPLES, key=lambda x: x.position)


# =============================================================================
# THREE MOTHERS ANALYSIS
# =============================================================================

@dataclass
class ThreeMothersSystem:
    """
    The Three Mothers (אמ״ש) - Elemental Primitives.
    
    These constitute the Primary Algorithm of creation.
    They function in a dialectic feedback loop:
    
    Thesis (Mem/Water) → Antithesis (Shin/Fire) → Synthesis (Aleph/Air)
    """
    
    @property
    def mothers(self) -> List[HebrewLetter]:
        """The three mother letters."""
        return MOTHERS
    
    @property
    def aleph_analysis(self) -> Dict[str, Any]:
        """Analysis of Aleph - the Balancing Scalar."""
        return {
            "letter": "א",
            "value": 1,
            "element": "Air (אויר)",
            "function": "Balancing Scalar - zero-point field",
            "anatomy": "Chest/Respiratory System",
            "role": "Carrier Wave for YHVH frequency",
            "graphic_composition": {
                "upper_yod": 10,
                "lower_yod": 10,
                "diagonal_vav": 6,
                "total": 26,
                "significance": "= YHVH gematria",
            },
        }
    
    @property
    def mem_analysis(self) -> Dict[str, Any]:
        """Analysis of Mem - the Flow Vector."""
        return {
            "letter": "מ",
            "value": 40,
            "element": "Water (מים)",
            "function": "Flow Vector - data fluidity",
            "anatomy": "Belly/Digestion",
            "dual_forms": {
                "open_mem": "מ - flowing potential, RAM",
                "closed_mem": "ם - contained manifestation, ROM",
            },
            "role": "Universal Solvent / Coolant System",
        }
    
    @property
    def shin_analysis(self) -> Dict[str, Any]:
        """Analysis of Shin - the Transformative Operator."""
        return {
            "letter": "ש",
            "value": 300,
            "element": "Fire (אש)",
            "function": "Transformative Operator - CPU",
            "anatomy": "Head/Neural processing",
            "graphic": "Three vectors (flames) from single base",
            "correspondence": "Three-Column Architecture of Tree of Life",
            "role": "State change driver - Alchemy",
        }
    
    @property
    def dialectic(self) -> Dict[str, str]:
        """The dialectic interaction."""
        return {
            "thesis": "Mem (Water) - presents dataset",
            "antithesis": "Shin (Fire) - applies transformation",
            "synthesis": "Aleph (Air) - equilibrates tension",
            "output": "Stable manifested reality",
        }
    
    @property
    def numeric_progression(self) -> Dict[str, Any]:
        """The numeric scaling law."""
        return {
            "sequence": "1 → 40 → 300",
            "insight": "Non-linear scaling - energy required increases exponentially",
            "constant": "Aleph (1) remains axis around which Fire/Water rotate",
        }


# =============================================================================
# SEVEN DOUBLES ANALYSIS
# =============================================================================

@dataclass
class SevenDoublesSystem:
    """
    The Seven Doubles (בגדכפר״ת) - Binary Switches.
    
    Unlike Mothers (elemental continua), Doubles introduce Discrete State.
    Each has two pronunciations determined by Dagesh (point).
    """
    
    @property
    def doubles(self) -> List[HebrewLetter]:
        """The seven double letters."""
        return DOUBLES
    
    @property
    def dagesh_operator(self) -> Dict[str, str]:
        """The Dagesh operator function."""
        return {
            "hard_state": "With Dagesh (State₁) - structure, hardness",
            "soft_state": "Without Dagesh (State₀) - flow, aspiration",
            "quantum": "Until Dagesh applied, letters in superposition",
        }
    
    @property
    def polarity_gates(self) -> Dict[str, Tuple[str, str]]:
        """The binary logic gates governed by each Double."""
        return {
            "ב (Bet)": ("Life", "Death"),
            "ג (Gimel)": ("Peace", "War"),
            "ד (Dalet)": ("Wisdom", "Folly"),
            "כ (Kaf)": ("Wealth", "Poverty"),
            "פ (Peh)": ("Dominion", "Slavery"),
            "ר (Resh)": ("Grace", "Ugliness"),
            "ת (Tav)": ("Life", "Death"),
        }
    
    @property
    def spatial_mapping(self) -> Dict[str, str]:
        """Mapping to spatial directions."""
        return {
            "ב": "Up",
            "ג": "Down", 
            "ד": "East",
            "כ": "West",
            "פ": "North",
            "ר": "South",
            "ת": "Center",
        }
    
    @property
    def planetary_drivers(self) -> Dict[str, str]:
        """Planetary correspondences."""
        return {
            "ב (Saturn)": "Structure/Time limit",
            "ג (Jupiter)": "Expansion/Growth",
            "ד (Mars)": "Energy/Conflict",
            "כ (Sun)": "Illumination/Central processing",
            "פ (Venus)": "Attraction/Binding",
            "ר (Mercury)": "Communication/Data transfer",
            "ת (Moon)": "Reflection/Memory",
        }


# =============================================================================
# TWELVE SIMPLES ANALYSIS
# =============================================================================

@dataclass
class TwelveSimplesSystem:
    """
    The Twelve Simples - Coordinate Primitives.
    
    Establish the Spatial-Temporal Grid (C₁₂ cyclic group).
    Map to Zodiac sectors and Hebrew months.
    """
    
    @property
    def simples(self) -> List[HebrewLetter]:
        """The twelve simple letters."""
        return SIMPLES
    
    @property
    def zodiac_mapping(self) -> Dict[str, str]:
        """Zodiac correspondences."""
        mapping = {}
        for letter in SIMPLES:
            if letter.zodiac:
                mapping[letter.letter] = letter.zodiac
        return mapping
    
    @property
    def month_mapping(self) -> Dict[str, str]:
        """Hebrew month correspondences."""
        mapping = {}
        for letter in SIMPLES:
            if letter.month:
                mapping[letter.letter] = letter.month
        return mapping
    
    @property
    def cyclic_group(self) -> Dict[str, Any]:
        """The C₁₂ cyclic group structure."""
        return {
            "group": "C₁₂",
            "elements": 12,
            "arc_degrees": 30,
            "function": "Hardware Clock of the cosmos",
            "filtering": "Each Zodiac sign acts as Static Mask/Filter",
        }
    
    @property
    def cube_geometry(self) -> str:
        """Geometric correspondence to cube."""
        return (
            "The 12 Simples correspond to the 12 Edges of a Cube. "
            "If Mothers are Axes (x,y,z) and Doubles are Faces, "
            "Simples are Structural Beams connecting vertices."
        )


# =============================================================================
# OTIYOT SYSTEM
# =============================================================================

@dataclass
class OtiyotSystem:
    """
    The complete 22-Letter Instruction Set.
    """
    
    mothers: ThreeMothersSystem = field(default_factory=ThreeMothersSystem)
    doubles: SevenDoublesSystem = field(default_factory=SevenDoublesSystem)
    simples: TwelveSimplesSystem = field(default_factory=TwelveSimplesSystem)
    
    @property
    def alphabet(self) -> List[HebrewLetter]:
        """The complete alphabet."""
        return ALPHABET
    
    def get_letter(self, char: str) -> Optional[HebrewLetter]:
        """Get letter by character."""
        for letter in ALPHABET:
            if letter.letter == char:
                return letter
        return None
    
    def get_by_value(self, value: int) -> Optional[HebrewLetter]:
        """Get letter by gematria value."""
        for letter in ALPHABET:
            if letter.standard_value == value:
                return letter
        return None
    
    def calculate_gematria(self, word: str) -> int:
        """Calculate standard gematria of a word."""
        total = 0
        for char in word:
            letter = self.get_letter(char)
            if letter:
                total += letter.standard_value
        return total
    
    def atbash_cipher(self, word: str) -> str:
        """Apply Atbash cipher transformation."""
        result = []
        for char in word:
            letter = self.get_letter(char)
            if letter:
                pair_pos = letter.atbash_pair
                pair_letter = next((l for l in ALPHABET if l.position == pair_pos), None)
                if pair_letter:
                    result.append(pair_letter.letter)
                else:
                    result.append(char)
            else:
                result.append(char)
        return ''.join(result)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get system summary."""
        return {
            "total_letters": 22,
            "mothers": {
                "count": 3,
                "letters": "אמ״ש",
                "function": "Elemental Primitives",
            },
            "doubles": {
                "count": 7,
                "letters": "בגדכפר״ת",
                "function": "Binary Switches",
            },
            "simples": {
                "count": 12,
                "letters": "הוזחטילנסעצק",
                "function": "Coordinate Primitives",
            },
            "formula": "22 = 3 + 7 + 12",
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_otiyot() -> bool:
    """Validate the Otiyot module."""
    
    # Test alphabet completeness
    assert len(ALPHABET) == 22
    assert len(MOTHERS) == 3
    assert len(DOUBLES) == 7
    assert len(SIMPLES) == 12
    
    # Test letter properties
    aleph = ALPHABET[0]
    assert aleph.letter == "א"
    assert aleph.standard_value == 1
    assert aleph.category == LetterCategory.MOTHER
    
    tav = ALPHABET[21]
    assert tav.letter == "ת"
    assert tav.standard_value == 400
    
    # Test ThreeMothersSystem
    mothers_sys = ThreeMothersSystem()
    aleph_data = mothers_sys.aleph_analysis
    assert aleph_data["graphic_composition"]["total"] == 26
    
    # Test SevenDoublesSystem
    doubles_sys = SevenDoublesSystem()
    gates = doubles_sys.polarity_gates
    assert "ב (Bet)" in gates
    
    # Test TwelveSimplesSystem
    simples_sys = TwelveSimplesSystem()
    zodiac = simples_sys.zodiac_mapping
    assert len(zodiac) == 12
    
    # Test OtiyotSystem
    system = OtiyotSystem()
    
    assert system.get_letter("א").standard_value == 1
    assert system.get_by_value(400).letter == "ת"
    
    # Test gematria
    assert system.calculate_gematria("אב") == 3  # 1 + 2
    
    summary = system.get_summary()
    assert summary["total_letters"] == 22
    assert summary["formula"] == "22 = 3 + 7 + 12"
    
    return True


if __name__ == "__main__":
    print("Validating Otiyot Module...")
    assert validate_otiyot()
    print("✓ Otiyot module validated")
    
    # Demo
    print("\n--- Otiyot System Demo ---")
    
    system = OtiyotSystem()
    
    print("\nThe 22-Letter Instruction Set:")
    print(f"  Formula: {system.get_summary()['formula']}")
    
    print("\nThree Mothers (אמ״ש):")
    for m in system.mothers.mothers:
        print(f"  {m.letter} ({m.name}) = {m.standard_value} [{m.element.name if m.element else 'N/A'}]")
    
    print("\nSeven Doubles (בגדכפר״ת):")
    for d in system.doubles.doubles:
        print(f"  {d.letter} ({d.name}) = {d.standard_value} [{d.polarity_pair}]")
    
    print("\nTwelve Simples (Zodiac):")
    zodiac = system.simples.zodiac_mapping
    for letter, sign in list(zodiac.items())[:6]:
        print(f"  {letter} → {sign}")
    
    print("\nAleph Composition:")
    aleph_data = system.mothers.aleph_analysis["graphic_composition"]
    print(f"  Upper Yod: {aleph_data['upper_yod']}")
    print(f"  Lower Yod: {aleph_data['lower_yod']}")
    print(f"  Diagonal Vav: {aleph_data['diagonal_vav']}")
    print(f"  Total: {aleph_data['total']} = YHVH")
