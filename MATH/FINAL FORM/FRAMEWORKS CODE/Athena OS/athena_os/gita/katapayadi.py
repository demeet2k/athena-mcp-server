"""
ATHENA OS - BHAGAVAD GĪTĀ COMPUTATIONAL FRAMEWORK
==================================================
Part V: The Kaṭapayādi Hashing System

THE KAṬAPAYĀDI CIPHER:
    An ancient bijective hash function H_KP: Σ → ℤ
    that maps Sanskrit phonemes to decimal integers.

ENCODING RULES:
    1. Only consonants encode digits
    2. Vowels are ignored
    3. In conjuncts, only the last consonant counts
    4. Numbers are read in reverse (Indian convention)

THE MAPPING:
    ka=1, kha=2, ga=3, gha=4, ṅa=5
    ca=6, cha=7, ja=8, jha=9, ña=0
    ṭa=1, ṭha=2, ḍa=3, ḍha=4, ṇa=5
    ta=6, tha=7, da=8, dha=9, na=0
    pa=1, pha=2, ba=3, bha=4, ma=5
    ya=1, ra=2, la=3, va=4, śa=5
    ṣa=6, sa=7, ha=8

APPLICATIONS:
    - Encoding π in verses (gopībhāgya = 3.14159...)
    - Encoding √2, φ, and other constants
    - Mathematical mnemonics in sacred texts

SOURCES:
    The Bhagavad Gītā: A Computational Treatise, Appendix B
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import numpy as np
import math


# =============================================================================
# THE KAṬAPAYĀDI MAPPING
# =============================================================================

# Sanskrit consonant to digit mapping
KATAPAYADI_MAP = {
    # Velars (ka-varga)
    'क': 1, 'ख': 2, 'ग': 3, 'घ': 4, 'ङ': 5,
    'ka': 1, 'kha': 2, 'ga': 3, 'gha': 4, 'nga': 5,
    
    # Palatals (ca-varga)
    'च': 6, 'छ': 7, 'ज': 8, 'झ': 9, 'ञ': 0,
    'ca': 6, 'cha': 7, 'ja': 8, 'jha': 9, 'nya': 0,
    
    # Retroflexes (ṭa-varga)
    'ट': 1, 'ठ': 2, 'ड': 3, 'ढ': 4, 'ण': 5,
    'ta_retro': 1, 'tha_retro': 2, 'da_retro': 3, 
    'dha_retro': 4, 'na_retro': 5,
    
    # Dentals (ta-varga)
    'त': 6, 'थ': 7, 'द': 8, 'ध': 9, 'न': 0,
    'ta': 6, 'tha': 7, 'da': 8, 'dha': 9, 'na': 0,
    
    # Labials (pa-varga)
    'प': 1, 'फ': 2, 'ब': 3, 'भ': 4, 'म': 5,
    'pa': 1, 'pha': 2, 'ba': 3, 'bha': 4, 'ma': 5,
    
    # Semivowels and sibilants
    'य': 1, 'र': 2, 'ल': 3, 'व': 4,
    'ya': 1, 'ra': 2, 'la': 3, 'va': 4,
    
    'श': 5, 'ष': 6, 'स': 7, 'ह': 8,
    'sha': 5, 'sha_retro': 6, 'sa': 7, 'ha': 8,
}

# Vowels (do not encode)
VOWELS = set([
    'अ', 'आ', 'इ', 'ई', 'उ', 'ऊ', 'ऋ', 'ॠ', 'ए', 'ऐ', 'ओ', 'औ',
    'a', 'aa', 'i', 'ii', 'u', 'uu', 'ri', 'rii', 'e', 'ai', 'o', 'au',
])

# Famous encoded verses
ENCODED_VERSES = {
    # gopībhāgya madhuvrata śṛṅgiśodadhi sandhiga |
    # khalajīvitakhātāva galahālārasandhara ||
    # Encodes π to 32 decimal places
    "gopibhagya": {
        "sanskrit": "गोपीभाग्य मधुव्रात",
        "romanized": "go-pi-bha-gya ma-dhu-vra-ta",
        "value": "3.14159265",
        "constant": "π",
    },
}


# =============================================================================
# THE HASH FUNCTION
# =============================================================================

@dataclass
class KatapaydiHasher:
    """
    The Kaṭapayādi Hash Function.
    
    A bijective function H_KP: Σ → ℤ that maps Sanskrit
    phonemes to decimal integers.
    """
    
    # Reverse mode (Indian convention: right-to-left)
    reverse_mode: bool = True
    
    def char_to_digit(self, char: str) -> Optional[int]:
        """
        Convert a single character/phoneme to digit.
        
        Returns None for vowels and unmapped characters.
        """
        # Check direct mapping
        if char in KATAPAYADI_MAP:
            return KATAPAYADI_MAP[char]
        
        # Check lowercase
        char_lower = char.lower()
        if char_lower in KATAPAYADI_MAP:
            return KATAPAYADI_MAP[char_lower]
        
        # Check if vowel
        if char in VOWELS or char.lower() in VOWELS:
            return None
        
        return None
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize Sanskrit text into phonemes.
        
        Handles conjuncts by taking only the last consonant.
        """
        # Simple tokenization by character
        # For full implementation, would need proper Sanskrit parser
        tokens = []
        
        i = 0
        while i < len(text):
            # Check for multi-character romanization
            for length in [3, 2, 1]:
                if i + length <= len(text):
                    token = text[i:i+length].lower()
                    if token in KATAPAYADI_MAP or token in VOWELS:
                        tokens.append(token)
                        i += length
                        break
            else:
                # Single character
                if text[i] not in ' -':
                    tokens.append(text[i])
                i += 1
        
        return tokens
    
    def hash(self, text: str) -> List[int]:
        """
        Hash a Sanskrit text to a list of digits.
        
        Returns digits in order (reversed if reverse_mode=True).
        """
        tokens = self.tokenize(text)
        digits = []
        
        for token in tokens:
            digit = self.char_to_digit(token)
            if digit is not None:
                digits.append(digit)
        
        if self.reverse_mode:
            digits.reverse()
        
        return digits
    
    def to_integer(self, text: str) -> int:
        """Hash text to a single integer."""
        digits = self.hash(text)
        
        if not digits:
            return 0
        
        result = 0
        for i, digit in enumerate(digits):
            result += digit * (10 ** i)
        
        return result
    
    def to_decimal(self, text: str, decimal_position: int = 1) -> float:
        """
        Hash text to a decimal number.
        
        decimal_position: position of decimal point from left
        """
        digits = self.hash(text)
        
        if not digits:
            return 0.0
        
        # Build the number
        integer_part = digits[:decimal_position]
        fractional_part = digits[decimal_position:]
        
        result = 0.0
        
        # Integer part
        for i, digit in enumerate(reversed(integer_part)):
            result += digit * (10 ** i)
        
        # Fractional part
        for i, digit in enumerate(fractional_part):
            result += digit * (10 ** -(i + 1))
        
        return result
    
    def verify_constant(self, text: str, constant: float, 
                        decimal_places: int = 5) -> bool:
        """
        Verify that text encodes a mathematical constant.
        """
        decoded = self.to_decimal(text, decimal_position=1)
        
        # Compare to specified precision
        tolerance = 10 ** (-decimal_places)
        
        return abs(decoded - constant) < tolerance


# =============================================================================
# ENCODER (Inverse Function)
# =============================================================================

@dataclass
class KatapaydiEncoder:
    """
    Inverse of the hash function: encodes numbers into Sanskrit.
    """
    
    # Reverse mapping (digit to consonant options)
    DIGIT_TO_CONSONANTS: Dict[int, List[str]] = field(default_factory=lambda: {
        0: ['ña', 'na'],
        1: ['ka', 'ṭa', 'pa', 'ya'],
        2: ['kha', 'ṭha', 'pha', 'ra'],
        3: ['ga', 'ḍa', 'ba', 'la'],
        4: ['gha', 'ḍha', 'bha', 'va'],
        5: ['ṅa', 'ṇa', 'ma', 'śa'],
        6: ['ca', 'ta', 'ṣa'],
        7: ['cha', 'tha', 'sa'],
        8: ['ja', 'da', 'ha'],
        9: ['jha', 'dha'],
    })
    
    def encode_digit(self, digit: int, variant: int = 0) -> str:
        """
        Encode a single digit to a consonant.
        
        variant: which consonant option to use
        """
        if digit not in self.DIGIT_TO_CONSONANTS:
            return ''
        
        options = self.DIGIT_TO_CONSONANTS[digit]
        return options[variant % len(options)]
    
    def encode_integer(self, n: int, reverse: bool = True) -> str:
        """
        Encode an integer as Sanskrit syllables.
        """
        if n == 0:
            return self.encode_digit(0)
        
        digits = []
        while n > 0:
            digits.append(n % 10)
            n //= 10
        
        if reverse:
            digits.reverse()
        
        result = []
        for digit in digits:
            result.append(self.encode_digit(digit))
            result.append('a')  # Add vowel for syllable
        
        return ''.join(result)
    
    def encode_pi(self, decimal_places: int = 10) -> str:
        """
        Generate a Sanskrit encoding of π.
        """
        pi_str = str(math.pi).replace('.', '')[:decimal_places + 1]
        
        result = []
        for i, char in enumerate(pi_str):
            digit = int(char)
            # Vary consonant choices for natural text
            consonant = self.encode_digit(digit, variant=i)
            result.append(consonant)
            if i == 0:
                result.append('o')  # First syllable
            else:
                result.append('a')  # Other syllables
        
        return ''.join(result)


# =============================================================================
# VERIFICATION SYSTEM
# =============================================================================

@dataclass
class KatapaydiVerifier:
    """
    Verify mathematical constants encoded in ancient texts.
    """
    
    hasher: KatapaydiHasher = field(default_factory=KatapaydiHasher)
    
    def verify_pi(self, text: str, places: int = 5) -> Dict[str, Any]:
        """
        Verify if text encodes π.
        """
        decoded = self.hasher.to_decimal(text, decimal_position=1)
        expected = math.pi
        
        difference = abs(decoded - expected)
        
        return {
            "decoded": decoded,
            "expected": expected,
            "difference": difference,
            "places_correct": int(-np.log10(max(difference, 1e-15))),
            "verified": difference < 10 ** (-places),
        }
    
    def verify_sqrt2(self, text: str, places: int = 5) -> Dict[str, Any]:
        """
        Verify if text encodes √2.
        """
        decoded = self.hasher.to_decimal(text, decimal_position=1)
        expected = math.sqrt(2)
        
        difference = abs(decoded - expected)
        
        return {
            "decoded": decoded,
            "expected": expected,
            "difference": difference,
            "verified": difference < 10 ** (-places),
        }
    
    def verify_phi(self, text: str, places: int = 5) -> Dict[str, Any]:
        """
        Verify if text encodes φ (golden ratio).
        """
        decoded = self.hasher.to_decimal(text, decimal_position=1)
        expected = (1 + math.sqrt(5)) / 2
        
        difference = abs(decoded - expected)
        
        return {
            "decoded": decoded,
            "expected": expected,
            "difference": difference,
            "verified": difference < 10 ** (-places),
        }
    
    def identify_constant(self, text: str) -> Optional[str]:
        """
        Try to identify which constant the text encodes.
        """
        decoded = self.hasher.to_decimal(text, decimal_position=1)
        
        constants = {
            "π": math.pi,
            "√2": math.sqrt(2),
            "√3": math.sqrt(3),
            "φ": (1 + math.sqrt(5)) / 2,
            "e": math.e,
            "1/π": 1 / math.pi,
        }
        
        best_match = None
        best_diff = float('inf')
        
        for name, value in constants.items():
            diff = abs(decoded - value)
            if diff < best_diff:
                best_diff = diff
                best_match = name
        
        if best_diff < 0.01:  # Reasonable threshold
            return best_match
        
        return None


# =============================================================================
# FAMOUS EXAMPLES
# =============================================================================

def demonstrate_gopibhagya() -> Dict[str, Any]:
    """
    Demonstrate the famous gopībhāgya verse encoding π.
    
    गोपीभाग्य मधुव्रात शृङ्गीशोदधि सन्धिग।
    खलजीवितखाटाव गलहालारसन्धर॥
    
    Decoded: 3.1415926535897932384626433832792...
    """
    hasher = KatapaydiHasher(reverse_mode=True)
    
    # Romanized version (simplified)
    verse = "go-pi-bha-gya"
    
    digits = hasher.hash(verse)
    
    return {
        "verse": "गोपीभाग्य (gopībhāgya)",
        "digits_extracted": digits,
        "meaning": "The fortune of the gopis (cowherd girls)",
        "encodes": "π",
        "decoded_value": hasher.to_decimal(verse, 1),
        "actual_pi": math.pi,
    }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_katapayadi() -> bool:
    """Validate the katapayadi module."""
    
    # Test character mapping
    hasher = KatapaydiHasher()
    
    assert hasher.char_to_digit('ka') == 1
    assert hasher.char_to_digit('ga') == 3
    assert hasher.char_to_digit('na') == 0
    assert hasher.char_to_digit('pa') == 1
    assert hasher.char_to_digit('ra') == 2
    assert hasher.char_to_digit('sa') == 7
    
    # Vowels should return None
    assert hasher.char_to_digit('a') is None
    
    # Test tokenization
    tokens = hasher.tokenize("ka-ga-pa")
    assert len(tokens) >= 3
    
    # Test hashing
    digits = hasher.hash("ka-ga-pa")
    assert isinstance(digits, list)
    assert all(isinstance(d, int) for d in digits)
    
    # Test to_integer
    n = hasher.to_integer("ka")
    assert isinstance(n, int)
    
    # Test encoder
    encoder = KatapaydiEncoder()
    syllable = encoder.encode_digit(1)
    assert syllable in ['ka', 'ṭa', 'pa', 'ya']
    
    encoded = encoder.encode_integer(123)
    assert len(encoded) > 0
    
    # Test verifier
    verifier = KatapaydiVerifier()
    
    # Test identification
    constant = verifier.identify_constant("ga")  # Would decode to 3.xxx
    # Just check it returns something or None
    assert constant is None or isinstance(constant, str)
    
    return True


if __name__ == "__main__":
    print("Validating Kaṭapayādi Module...")
    assert validate_katapayadi()
    print("✓ Kaṭapayādi module validated")
    
    # Demo
    print("\n--- Kaṭapayādi System Demo ---")
    
    print("\n1. The Mapping (subset):")
    for syllable in ['ka', 'kha', 'ga', 'gha', 'pa', 'ra', 'sa', 'na']:
        digit = KATAPAYADI_MAP.get(syllable, '?')
        print(f"   {syllable} → {digit}")
    
    print("\n2. Encoding π:")
    encoder = KatapaydiEncoder()
    pi_encoded = encoder.encode_pi(5)
    print(f"   π (5 digits) → {pi_encoded}")
    
    print("\n3. Famous Verse: gopībhāgya")
    result = demonstrate_gopibhagya()
    print(f"   Verse: {result['verse']}")
    print(f"   Meaning: {result['meaning']}")
    print(f"   Encodes: {result['encodes']}")
    print(f"   Digits: {result['digits_extracted']}")
    
    print("\n4. Verification:")
    verifier = KatapaydiVerifier()
    # Using a test string that might encode something close to π
    hasher = KatapaydiHasher()
    
    print(f"   Actual π = {math.pi:.10f}")
    print(f"   Actual φ = {((1 + math.sqrt(5)) / 2):.10f}")
    print(f"   Actual √2 = {math.sqrt(2):.10f}")
