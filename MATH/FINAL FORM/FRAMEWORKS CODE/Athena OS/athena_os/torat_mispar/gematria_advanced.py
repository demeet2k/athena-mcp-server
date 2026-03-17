"""
ATHENA OS - TORAT HA-MISPAR (תורת המספר)
=========================================
Module X: Gematria Advanced (גימטריא) - The Numerical Cipher

GEMATRIA DEFINED:
    The alphanumeric code-system where letters have numerical values.
    Symbol = Number = Frequency = Meaning

STANDARD VALUES:
    Units (1-9): א-ט
    Tens (10-90): י-צ
    Hundreds (100-400): ק-ת
    Finals (500-900): ך, ם, ן, ף, ץ

METHODS:
    1. Mispar Hechrachi (Standard) - Standard values
    2. Mispar Siduri (Ordinal) - Position 1-22
    3. Mispar Katan (Small) - Digital root
    4. Mispar Gadol (Large) - Finals as 500-900
    5. Milui (Full spelling) - Spell out letters
    6. Atbash - Substitution cipher
    7. Albam - Half-alphabet substitution
    8. Kidmi (Cumulative) - Sum of all preceding

KEY CONSTANTS:
    YHVH = 26 (10+5+6+5)
    Elohim = 86 = HaTeva (Nature)
    Echad = Ahavah = 13 (One = Love)
    Kabbalah = 137 (Fine Structure Constant)

SOURCES:
    TORAT HA-MISPAR (תורת המספר)
    SEFER YETZIRAH (ספר יצירה)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


# =============================================================================
# GEMATRIA METHOD TYPES
# =============================================================================

class GematriaMethod(Enum):
    """Types of Gematria calculation methods."""
    
    STANDARD = ("Mispar Hechrachi", "Standard decimal values")
    ORDINAL = ("Mispar Siduri", "Position in alphabet 1-22")
    SMALL = ("Mispar Katan", "Digital root (mod 9)")
    LARGE = ("Mispar Gadol", "Finals as 500-900")
    FULL_SPELLING = ("Milui", "Spell out letter names")
    ATBASH = ("אתבש", "First↔Last substitution")
    ALBAM = ("אלבם", "Half-alphabet substitution")
    CUMULATIVE = ("Mispar Kidmi", "Sum of all preceding")
    
    def __init__(self, hebrew_name: str, description: str):
        self.hebrew_name = hebrew_name
        self._description = description


# =============================================================================
# LETTER VALUES
# =============================================================================

# Standard values
STANDARD_VALUES: Dict[str, int] = {
    'א': 1, 'ב': 2, 'ג': 3, 'ד': 4, 'ה': 5, 'ו': 6, 'ז': 7, 'ח': 8, 'ט': 9,
    'י': 10, 'כ': 20, 'ל': 30, 'מ': 40, 'נ': 50, 'ס': 60, 'ע': 70, 'פ': 80, 'צ': 90,
    'ק': 100, 'ר': 200, 'ש': 300, 'ת': 400,
    # Final forms (Sofit)
    'ך': 20, 'ם': 40, 'ן': 50, 'ף': 80, 'ץ': 90,
}

# Large values (finals as 500-900)
LARGE_VALUES: Dict[str, int] = {
    **STANDARD_VALUES,
    'ך': 500, 'ם': 600, 'ן': 700, 'ף': 800, 'ץ': 900,
}

# Ordinal values (position 1-22)
ORDINAL_VALUES: Dict[str, int] = {
    'א': 1, 'ב': 2, 'ג': 3, 'ד': 4, 'ה': 5, 'ו': 6, 'ז': 7, 'ח': 8, 'ט': 9,
    'י': 10, 'כ': 11, 'ל': 12, 'מ': 13, 'נ': 14, 'ס': 15, 'ע': 16, 'פ': 17, 'צ': 18,
    'ק': 19, 'ר': 20, 'ש': 21, 'ת': 22,
    'ך': 11, 'ם': 13, 'ן': 14, 'ף': 17, 'ץ': 18,
}

# Atbash pairs (first↔last)
ATBASH_PAIRS: Dict[str, str] = {
    'א': 'ת', 'ב': 'ש', 'ג': 'ר', 'ד': 'ק', 'ה': 'צ', 'ו': 'פ', 'ז': 'ע',
    'ח': 'ס', 'ט': 'נ', 'י': 'מ', 'כ': 'ל',
    'ת': 'א', 'ש': 'ב', 'ר': 'ג', 'ק': 'ד', 'צ': 'ה', 'פ': 'ו', 'ע': 'ז',
    'ס': 'ח', 'נ': 'ט', 'מ': 'י', 'ל': 'כ',
}

# Full spelling of letters (for Milui)
LETTER_SPELLINGS: Dict[str, str] = {
    'א': 'אלף', 'ב': 'בית', 'ג': 'גימל', 'ד': 'דלת', 'ה': 'הא',
    'ו': 'וו', 'ז': 'זין', 'ח': 'חית', 'ט': 'טית', 'י': 'יוד',
    'כ': 'כף', 'ל': 'למד', 'מ': 'מם', 'נ': 'נון', 'ס': 'סמך',
    'ע': 'עין', 'פ': 'פא', 'צ': 'צדי', 'ק': 'קוף', 'ר': 'ריש',
    'ש': 'שין', 'ת': 'תו',
}


# =============================================================================
# GEMATRIA CALCULATOR
# =============================================================================

@dataclass
class GematriaCalculator:
    """
    Advanced Gematria Calculator supporting multiple methods.
    """
    
    def calculate_standard(self, word: str) -> int:
        """Calculate standard gematria."""
        return sum(STANDARD_VALUES.get(c, 0) for c in word)
    
    def calculate_ordinal(self, word: str) -> int:
        """Calculate ordinal gematria (position 1-22)."""
        return sum(ORDINAL_VALUES.get(c, 0) for c in word)
    
    def calculate_small(self, word: str) -> int:
        """Calculate small gematria (digital root)."""
        total = self.calculate_standard(word)
        # Reduce to single digit (except 0)
        while total > 9:
            total = sum(int(d) for d in str(total))
        return total
    
    def calculate_large(self, word: str) -> int:
        """Calculate large gematria (finals as 500-900)."""
        return sum(LARGE_VALUES.get(c, 0) for c in word)
    
    def calculate_milui(self, word: str) -> int:
        """Calculate full spelling (Milui) gematria."""
        total = 0
        for c in word:
            spelled = LETTER_SPELLINGS.get(c, c)
            total += self.calculate_standard(spelled)
        return total
    
    def calculate_cumulative(self, word: str) -> int:
        """Calculate cumulative (Kidmi) gematria."""
        total = 0
        for c in word:
            ordinal = ORDINAL_VALUES.get(c, 0)
            # Sum of all letters up to and including this position
            cumulative = sum(STANDARD_VALUES.get(chr(1488 + i), 0) for i in range(ordinal))
            total += cumulative
        return total
    
    def apply_atbash(self, word: str) -> str:
        """Apply Atbash cipher."""
        return ''.join(ATBASH_PAIRS.get(c, c) for c in word)
    
    def calculate(self, word: str, method: GematriaMethod) -> Any:
        """Calculate gematria using specified method."""
        methods = {
            GematriaMethod.STANDARD: self.calculate_standard,
            GematriaMethod.ORDINAL: self.calculate_ordinal,
            GematriaMethod.SMALL: self.calculate_small,
            GematriaMethod.LARGE: self.calculate_large,
            GematriaMethod.FULL_SPELLING: self.calculate_milui,
            GematriaMethod.CUMULATIVE: self.calculate_cumulative,
            GematriaMethod.ATBASH: self.apply_atbash,
        }
        
        func = methods.get(method)
        if func:
            return func(word)
        return None
    
    def find_equivalences(self, value: int, words: List[str]) -> List[Tuple[str, int]]:
        """Find words with equivalent gematria."""
        return [(w, self.calculate_standard(w)) for w in words 
                if self.calculate_standard(w) == value]


# =============================================================================
# KEY GEMATRIA CONSTANTS
# =============================================================================

@dataclass
class GematriaConstants:
    """
    Key gematria constants and equivalences.
    """
    
    @property
    def primary_names(self) -> Dict[str, Dict[str, Any]]:
        """Primary Divine Name values."""
        return {
            "YHVH": {
                "hebrew": "יהוה",
                "value": 26,
                "breakdown": "10 + 5 + 6 + 5",
                "significance": "The Tetragrammaton - Existence Operator",
            },
            "Elohim": {
                "hebrew": "אלהים",
                "value": 86,
                "breakdown": "1 + 30 + 5 + 10 + 40",
                "significance": "God/Powers - Restriction Operator",
            },
            "Adonai": {
                "hebrew": "אדני",
                "value": 65,
                "breakdown": "1 + 4 + 50 + 10",
                "significance": "My Lord - Interface Operator",
            },
            "Ehyeh": {
                "hebrew": "אהיה",
                "value": 21,
                "breakdown": "1 + 5 + 10 + 5",
                "significance": "I Will Be - Becoming Operator",
            },
            "El": {
                "hebrew": "אל",
                "value": 31,
                "breakdown": "1 + 30",
                "significance": "Mighty One - Expansion Operator",
            },
            "Shaddai": {
                "hebrew": "שדי",
                "value": 314,
                "breakdown": "300 + 4 + 10",
                "significance": "Almighty - π encoding",
            },
        }
    
    @property
    def key_equivalences(self) -> List[Dict[str, Any]]:
        """Key gematria equivalences."""
        return [
            {
                "value": 13,
                "words": ["אחד (Echad/One)", "אהבה (Ahavah/Love)"],
                "significance": "Unity and Love are identical",
            },
            {
                "value": 86,
                "words": ["אלהים (Elohim/God)", "הטבע (HaTeva/Nature)"],
                "significance": "God manifests as Nature - the Masking Protocol",
            },
            {
                "value": 358,
                "words": ["משיח (Mashiach/Messiah)", "נחש (Nachash/Serpent)"],
                "significance": "Messiah rectifies the Fall",
            },
            {
                "value": 137,
                "words": ["קבלה (Kabbalah/Reception)"],
                "significance": "Fine Structure Constant (1/α)",
            },
            {
                "value": 26,
                "words": ["יהוה (YHVH)"],
                "significance": "2 × 13 = Double Love/Unity",
            },
        ]
    
    @property
    def milui_yhvh(self) -> Dict[str, Dict[str, Any]]:
        """The four spellings of YHVH (Milui variants)."""
        return {
            "AV": {
                "hebrew": "עב",
                "value": 72,
                "spelling": "יוד הי ויו הי",
                "world": "Atzilut",
                "sefirah": "Chochmah",
            },
            "SAG": {
                "hebrew": "סג",
                "value": 63,
                "spelling": "יוד הי ואו הי",
                "world": "Beriah",
                "sefirah": "Binah",
            },
            "MAH": {
                "hebrew": "מה",
                "value": 45,
                "spelling": "יוד הא ואו הא",
                "world": "Yetzirah",
                "sefirah": "Zeir Anpin",
            },
            "BAN": {
                "hebrew": "בן",
                "value": 52,
                "spelling": "יוד הה וו הה",
                "world": "Assiyah",
                "sefirah": "Malkhut",
            },
        }
    
    @property
    def mathematical_constants(self) -> Dict[str, Dict[str, Any]]:
        """Mathematical constants encoded in gematria."""
        return {
            "pi": {
                "encoding": "Solomon's Sea (1 Kings 7:23)",
                "written": "קוה (111)",
                "read": "קו (106)",
                "calculation": "30 × (111/106) ≈ 3.1415",
                "significance": "π encoded in Ktiv/Kri",
            },
            "fine_structure": {
                "word": "קבלה (Kabbalah)",
                "value": 137,
                "physics": "1/α ≈ 137.036",
                "significance": "Light-matter interaction constant",
            },
        }


# =============================================================================
# GEMATRIA SYSTEM
# =============================================================================

@dataclass
class GematriaSystem:
    """
    The complete Gematria system.
    """
    
    calculator: GematriaCalculator = field(default_factory=GematriaCalculator)
    constants: GematriaConstants = field(default_factory=GematriaConstants)
    
    def analyze_word(self, word: str) -> Dict[str, Any]:
        """Complete gematria analysis of a word."""
        return {
            "word": word,
            "standard": self.calculator.calculate_standard(word),
            "ordinal": self.calculator.calculate_ordinal(word),
            "small": self.calculator.calculate_small(word),
            "large": self.calculator.calculate_large(word),
            "milui": self.calculator.calculate_milui(word),
            "atbash": self.calculator.apply_atbash(word),
            "atbash_value": self.calculator.calculate_standard(
                self.calculator.apply_atbash(word)
            ),
        }
    
    def find_connections(self, word: str) -> List[Dict[str, Any]]:
        """Find gematria connections for a word."""
        value = self.calculator.calculate_standard(word)
        connections = []
        
        # Check key equivalences
        for eq in self.constants.key_equivalences:
            if eq["value"] == value:
                connections.append({
                    "type": "equivalence",
                    "value": value,
                    "related_words": eq["words"],
                    "significance": eq["significance"],
                })
        
        # Check Divine Names
        for name, data in self.constants.primary_names.items():
            if data["value"] == value:
                connections.append({
                    "type": "divine_name",
                    "name": name,
                    "hebrew": data["hebrew"],
                    "significance": data["significance"],
                })
        
        return connections
    
    def get_summary(self) -> Dict[str, Any]:
        """Get system summary."""
        return {
            "methods": len(GematriaMethod),
            "letters": len(STANDARD_VALUES),
            "key_constants": len(self.constants.primary_names),
            "equivalences": len(self.constants.key_equivalences),
            "milui_variants": len(self.constants.milui_yhvh),
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_gematria_advanced() -> bool:
    """Validate the Gematria Advanced module."""
    
    # Test GematriaMethod
    assert GematriaMethod.STANDARD.hebrew_name == "Mispar Hechrachi"
    
    # Test standard values
    assert STANDARD_VALUES['א'] == 1
    assert STANDARD_VALUES['ת'] == 400
    assert STANDARD_VALUES['י'] == 10
    
    # Test calculator
    calc = GematriaCalculator()
    
    # Test YHVH = 26
    assert calc.calculate_standard("יהוה") == 26
    
    # Test Elohim = 86
    assert calc.calculate_standard("אלהים") == 86
    
    # Test Echad = 13
    assert calc.calculate_standard("אחד") == 13
    
    # Test ordinal
    assert calc.calculate_ordinal("אבג") == 6  # 1+2+3
    
    # Test small (digital root)
    assert calc.calculate_small("יהוה") == 8  # 26 -> 2+6 = 8
    
    # Test Atbash
    assert calc.apply_atbash("א") == "ת"
    assert calc.apply_atbash("ת") == "א"
    
    # Test constants
    constants = GematriaConstants()
    
    assert constants.primary_names["YHVH"]["value"] == 26
    assert constants.milui_yhvh["AV"]["value"] == 72
    assert constants.milui_yhvh["SAG"]["value"] == 63
    assert constants.milui_yhvh["MAH"]["value"] == 45
    assert constants.milui_yhvh["BAN"]["value"] == 52
    
    # Test GematriaSystem
    system = GematriaSystem()
    
    analysis = system.analyze_word("יהוה")
    assert analysis["standard"] == 26
    
    summary = system.get_summary()
    assert summary["methods"] == len(GematriaMethod)
    
    return True


if __name__ == "__main__":
    print("Validating Gematria Advanced Module...")
    assert validate_gematria_advanced()
    print("✓ Gematria Advanced module validated")
    
    # Demo
    print("\n--- Gematria Advanced Demo ---")
    
    system = GematriaSystem()
    
    print("\nDivine Name Values:")
    for name, data in system.constants.primary_names.items():
        print(f"  {name} ({data['hebrew']}) = {data['value']}")
    
    print("\nKey Equivalences:")
    for eq in system.constants.key_equivalences[:3]:
        print(f"  {eq['value']}: {eq['words']}")
        print(f"    → {eq['significance']}")
    
    print("\nMilui (Full Spelling) of YHVH:")
    for name, data in system.constants.milui_yhvh.items():
        print(f"  {name} ({data['hebrew']}) = {data['value']} → {data['world']}")
    
    print("\nWord Analysis (יהוה):")
    analysis = system.analyze_word("יהוה")
    for method, value in analysis.items():
        if method != "word":
            print(f"  {method}: {value}")
    
    print("\nAtbash Cipher:")
    test_word = "משה"
    atbash = system.calculator.apply_atbash(test_word)
    print(f"  {test_word} → {atbash}")
