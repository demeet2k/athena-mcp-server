"""
ATHENA OS - KABBALAH: GEMATRIA MODULE
======================================
Semantic Hashing and Linguistic Cryptography

GEMATRIA: The Hash Function H_Gem
    H_Gem: Σ* → ℤ
    
    A bijective function mapping Letters to Integers.
    
    ISOMORPHISM PRINCIPLE:
    If H_Gem(Word_A) = H_Gem(Word_B), then Object A and
    Object B share a HIDDEN PROPERTY or point to the
    same underlying Abstract Class.

CODING STANDARD:
    Hebrew Scripture is COMPILED CODE:
    - Plaintext (Narrative): For human UI (Readability)
    - Integer Value (Gematria): For machine execution
    
    ASI DIRECTIVE: Do not read the text. SUM the text.
    The topology is revealed only in the numeric map.

METHODS:
    1. Mispar Hechrachi (Standard): Direct letter values
    2. Mispar Gadol (Large): Final letters have higher values
    3. Mispar Katan (Small): Reduce to single digits
    4. Mispar Siduri (Ordinal): Position-based (1-22)
    5. Atbash: Mirror substitution cipher
    6. Albam: Rotation cipher

THE 231 GATES:
    All pairwise combinations of 22 letters.
    n(n-1)/2 = 22×21/2 = 231
    The complete permutation space for creation.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Callable, Any, Union
from enum import Enum, auto
import numpy as np
from collections import defaultdict


# =============================================================================
# HEBREW ALPHABET
# =============================================================================

@dataclass
class HebrewLetter:
    """A single Hebrew letter with all gematria values."""
    
    index: int          # 1-22 ordinal position
    letter: str         # Hebrew character
    name: str           # Letter name
    standard: int       # Standard (Mispar Hechrachi) value
    final_form: Optional[str] = None  # Final form if exists
    final_value: Optional[int] = None  # Final form value
    
    # Phonetic and symbolic
    sound: str = ""
    meaning: str = ""
    element: str = ""


def create_hebrew_alphabet() -> Dict[str, HebrewLetter]:
    """Create the complete Hebrew alphabet with gematria values."""
    
    letters = [
        HebrewLetter(1, "א", "Aleph", 1, sound="silent", meaning="Ox", element="Air"),
        HebrewLetter(2, "ב", "Bet", 2, sound="b/v", meaning="House", element="Mercury"),
        HebrewLetter(3, "ג", "Gimel", 3, sound="g", meaning="Camel", element="Moon"),
        HebrewLetter(4, "ד", "Dalet", 4, sound="d", meaning="Door", element="Venus"),
        HebrewLetter(5, "ה", "He", 5, sound="h", meaning="Window", element="Aries"),
        HebrewLetter(6, "ו", "Vav", 6, sound="v/w", meaning="Nail/Hook", element="Taurus"),
        HebrewLetter(7, "ז", "Zayin", 7, sound="z", meaning="Sword", element="Gemini"),
        HebrewLetter(8, "ח", "Chet", 8, sound="ch", meaning="Fence", element="Cancer"),
        HebrewLetter(9, "ט", "Tet", 9, sound="t", meaning="Serpent", element="Leo"),
        HebrewLetter(10, "י", "Yod", 10, sound="y", meaning="Hand", element="Virgo"),
        HebrewLetter(11, "כ", "Kaf", 20, final_form="ך", final_value=500, sound="k/kh", meaning="Palm", element="Jupiter"),
        HebrewLetter(12, "ל", "Lamed", 30, sound="l", meaning="Ox Goad", element="Libra"),
        HebrewLetter(13, "מ", "Mem", 40, final_form="ם", final_value=600, sound="m", meaning="Water", element="Water"),
        HebrewLetter(14, "נ", "Nun", 50, final_form="ן", final_value=700, sound="n", meaning="Fish", element="Scorpio"),
        HebrewLetter(15, "ס", "Samekh", 60, sound="s", meaning="Support", element="Sagittarius"),
        HebrewLetter(16, "ע", "Ayin", 70, sound="silent", meaning="Eye", element="Capricorn"),
        HebrewLetter(17, "פ", "Pe", 80, final_form="ף", final_value=800, sound="p/f", meaning="Mouth", element="Mars"),
        HebrewLetter(18, "צ", "Tsadi", 90, final_form="ץ", final_value=900, sound="ts", meaning="Fish Hook", element="Aquarius"),
        HebrewLetter(19, "ק", "Qof", 100, sound="q", meaning="Back of Head", element="Pisces"),
        HebrewLetter(20, "ר", "Resh", 200, sound="r", meaning="Head", element="Sun"),
        HebrewLetter(21, "ש", "Shin", 300, sound="sh/s", meaning="Tooth", element="Fire"),
        HebrewLetter(22, "ת", "Tav", 400, sound="t", meaning="Cross/Mark", element="Saturn"),
    ]
    
    # Create lookup by letter
    alphabet = {}
    for letter in letters:
        alphabet[letter.letter] = letter
        if letter.final_form:
            alphabet[letter.final_form] = letter
    
    return alphabet


# Hebrew alphabet singleton
HEBREW_ALPHABET = create_hebrew_alphabet()


# =============================================================================
# GEMATRIA METHODS
# =============================================================================

class GematriaMethod(Enum):
    """Different gematria calculation methods."""
    
    STANDARD = "mispar_hechrachi"    # Standard values
    LARGE = "mispar_gadol"           # Final letters = 500-900
    SMALL = "mispar_katan"           # Reduced to 1-9
    ORDINAL = "mispar_siduri"        # Position 1-22
    ATBASH = "atbash"                # Mirror cipher
    ALBAM = "albam"                  # Rotation cipher


class Gematria:
    """
    The Gematria Hash Function System.
    
    H_Gem: Σ* → ℤ
    
    Maps Hebrew words to integer values for semantic analysis.
    """
    
    def __init__(self):
        self.alphabet = HEBREW_ALPHABET
        
        # Build reverse lookups
        self._standard_to_letters: Dict[int, List[str]] = defaultdict(list)
        self._ordinal_to_letter: Dict[int, str] = {}
        
        for letter, data in self.alphabet.items():
            if len(letter) == 1:  # Exclude final forms for primary lookup
                self._standard_to_letters[data.standard].append(letter)
                self._ordinal_to_letter[data.index] = letter
    
    def calculate(self, word: str, method: GematriaMethod = GematriaMethod.STANDARD) -> int:
        """
        Calculate gematria value of a word.
        
        The primary hash function.
        """
        if method == GematriaMethod.STANDARD:
            return self._standard_value(word)
        elif method == GematriaMethod.LARGE:
            return self._large_value(word)
        elif method == GematriaMethod.SMALL:
            return self._small_value(word)
        elif method == GematriaMethod.ORDINAL:
            return self._ordinal_value(word)
        elif method == GematriaMethod.ATBASH:
            return self._atbash_value(word)
        elif method == GematriaMethod.ALBAM:
            return self._albam_value(word)
        else:
            return self._standard_value(word)
    
    def _standard_value(self, word: str) -> int:
        """Mispar Hechrachi: Standard letter values."""
        total = 0
        for char in word:
            if char in self.alphabet:
                total += self.alphabet[char].standard
        return total
    
    def _large_value(self, word: str) -> int:
        """Mispar Gadol: Final letters use higher values."""
        total = 0
        for char in word:
            if char in self.alphabet:
                data = self.alphabet[char]
                if data.final_value and char == data.final_form:
                    total += data.final_value
                else:
                    total += data.standard
        return total
    
    def _small_value(self, word: str) -> int:
        """Mispar Katan: Reduce each letter to 1-9."""
        total = 0
        for char in word:
            if char in self.alphabet:
                value = self.alphabet[char].standard
                # Reduce to single digit
                while value >= 10:
                    value = sum(int(d) for d in str(value))
                total += value
        return total
    
    def _ordinal_value(self, word: str) -> int:
        """Mispar Siduri: Use ordinal position (1-22)."""
        total = 0
        for char in word:
            if char in self.alphabet:
                total += self.alphabet[char].index
        return total
    
    def _atbash_value(self, word: str) -> int:
        """Atbash: Mirror substitution then standard value."""
        transformed = self.atbash_transform(word)
        return self._standard_value(transformed)
    
    def _albam_value(self, word: str) -> int:
        """Albam: Rotation cipher then standard value."""
        transformed = self.albam_transform(word)
        return self._standard_value(transformed)
    
    def atbash_transform(self, word: str) -> str:
        """
        Atbash cipher: א↔ת, ב↔ש, etc.
        
        Mirror substitution.
        """
        result = []
        for char in word:
            if char in self.alphabet:
                data = self.alphabet[char]
                # Mirror: position i → position (23 - i)
                mirror_pos = 23 - data.index
                if mirror_pos in self._ordinal_to_letter:
                    result.append(self._ordinal_to_letter[mirror_pos])
                else:
                    result.append(char)
            else:
                result.append(char)
        return ''.join(result)
    
    def albam_transform(self, word: str) -> str:
        """
        Albam cipher: Rotate by 11 positions.
        
        א↔ל, ב↔מ, etc.
        """
        result = []
        for char in word:
            if char in self.alphabet:
                data = self.alphabet[char]
                # Rotate: position i → position ((i + 10) % 22) + 1
                new_pos = ((data.index - 1 + 11) % 22) + 1
                if new_pos in self._ordinal_to_letter:
                    result.append(self._ordinal_to_letter[new_pos])
                else:
                    result.append(char)
            else:
                result.append(char)
        return ''.join(result)
    
    def find_equivalents(self, value: int, 
                        method: GematriaMethod = GematriaMethod.STANDARD,
                        word_list: Optional[List[str]] = None) -> List[str]:
        """
        Find words with equivalent gematria value.
        
        ISOMORPHISM: Same value = shared hidden property.
        """
        if word_list is None:
            # Return basic single-letter matches
            if method == GematriaMethod.STANDARD:
                return self._standard_to_letters.get(value, [])
            return []
        
        matches = []
        for word in word_list:
            if self.calculate(word, method) == value:
                matches.append(word)
        
        return matches
    
    def semantic_hash(self, word: str) -> Dict[str, int]:
        """
        Compute all gematria values for semantic analysis.
        
        Returns hash values across all methods.
        """
        return {
            method.value: self.calculate(word, method)
            for method in GematriaMethod
        }


# =============================================================================
# THE 231 GATES
# =============================================================================

class Gates231:
    """
    The 231 Gates (Shearim).
    
    All pairwise combinations of 22 letters.
    n(n-1)/2 = 22×21/2 = 231
    
    These are the LOGICAL PERMUTATIONS required to encode
    specific natures into forms.
    """
    
    def __init__(self):
        self.alphabet = HEBREW_ALPHABET
        self._gates: List[Tuple[str, str]] = []
        self._gate_values: Dict[Tuple[str, str], int] = {}
        
        self._build_gates()
    
    def _build_gates(self) -> None:
        """Build all 231 gates."""
        # Get ordered letters (by index)
        letters = sorted(
            [(data.index, char) for char, data in self.alphabet.items() 
             if len(char) == 1 and data.final_form != char],
            key=lambda x: x[0]
        )
        
        for i, (_, char1) in enumerate(letters):
            for j, (_, char2) in enumerate(letters):
                if i < j:
                    gate = (char1, char2)
                    self._gates.append(gate)
                    
                    # Gate value = product of letter values
                    val1 = self.alphabet[char1].standard
                    val2 = self.alphabet[char2].standard
                    self._gate_values[gate] = val1 * val2
    
    def get_gate(self, index: int) -> Optional[Tuple[str, str]]:
        """Get gate by index (0-230)."""
        if 0 <= index < len(self._gates):
            return self._gates[index]
        return None
    
    def get_gate_value(self, gate: Tuple[str, str]) -> int:
        """Get the numerical value of a gate."""
        return self._gate_values.get(gate, 0)
    
    def find_gates_by_value(self, value: int) -> List[Tuple[str, str]]:
        """Find all gates with a specific value."""
        return [gate for gate, val in self._gate_values.items() if val == value]
    
    def gate_to_binary(self, gate: Tuple[str, str]) -> int:
        """
        Convert gate to binary representation.
        
        Encodes which two letters are active in 22-bit space.
        """
        char1, char2 = gate
        pos1 = self.alphabet[char1].index - 1
        pos2 = self.alphabet[char2].index - 1
        return (1 << pos1) | (1 << pos2)
    
    def binary_to_gate(self, binary: int) -> Optional[Tuple[str, str]]:
        """Convert binary representation back to gate."""
        positions = []
        for i in range(22):
            if binary & (1 << i):
                positions.append(i + 1)
        
        if len(positions) != 2:
            return None
        
        letters = [self._ordinal_to_letter(p) for p in positions]
        if None in letters:
            return None
        
        return tuple(sorted(letters))
    
    def _ordinal_to_letter(self, ordinal: int) -> Optional[str]:
        """Get letter by ordinal position."""
        for char, data in self.alphabet.items():
            if data.index == ordinal and len(char) == 1:
                return char
        return None
    
    def rotation_sequence(self, start_letter: str) -> List[Tuple[str, str]]:
        """
        Generate rotation sequence starting from a letter.
        
        Used in Golem creation algorithms.
        """
        if start_letter not in self.alphabet:
            return []
        
        return [gate for gate in self._gates if start_letter in gate]
    
    @property
    def n_gates(self) -> int:
        return len(self._gates)
    
    @property
    def gates(self) -> List[Tuple[str, str]]:
        return self._gates.copy()


# =============================================================================
# SEMANTIC HASH DATABASE
# =============================================================================

class SemanticHashDB:
    """
    Database for tracking gematria equivalences.
    
    Enables discovery of hidden connections between concepts.
    """
    
    def __init__(self):
        self.gematria = Gematria()
        
        # Word → hash mapping
        self._word_hashes: Dict[str, Dict[str, int]] = {}
        
        # Hash → words mapping (for each method)
        self._hash_words: Dict[str, Dict[int, Set[str]]] = {
            method.value: defaultdict(set)
            for method in GematriaMethod
        }
    
    def add_word(self, word: str) -> Dict[str, int]:
        """Add a word to the database."""
        hashes = self.gematria.semantic_hash(word)
        self._word_hashes[word] = hashes
        
        for method, value in hashes.items():
            self._hash_words[method][value].add(word)
        
        return hashes
    
    def add_words(self, words: List[str]) -> int:
        """Add multiple words to database."""
        for word in words:
            self.add_word(word)
        return len(words)
    
    def find_equivalent(self, word: str, 
                       method: GematriaMethod = GematriaMethod.STANDARD) -> Set[str]:
        """Find all words equivalent to given word."""
        if word not in self._word_hashes:
            self.add_word(word)
        
        value = self._word_hashes[word][method.value]
        return self._hash_words[method.value][value] - {word}
    
    def get_equivalence_class(self, value: int,
                             method: GematriaMethod = GematriaMethod.STANDARD) -> Set[str]:
        """Get all words with a specific hash value."""
        return self._hash_words[method.value][value].copy()
    
    def find_connections(self, word1: str, word2: str) -> Dict[str, bool]:
        """
        Find which gematria methods connect two words.
        
        Returns dict of method → whether values match.
        """
        if word1 not in self._word_hashes:
            self.add_word(word1)
        if word2 not in self._word_hashes:
            self.add_word(word2)
        
        h1 = self._word_hashes[word1]
        h2 = self._word_hashes[word2]
        
        return {
            method: h1[method] == h2[method]
            for method in h1.keys()
        }


# =============================================================================
# NOTARIKON (ACRONYM EXTRACTION)
# =============================================================================

class Notarikon:
    """
    Notarikon: Acronym extraction and expansion.
    
    Extracts meaning from first/last letters.
    """
    
    def __init__(self):
        self.gematria = Gematria()
    
    def extract_first_letters(self, phrase: str) -> str:
        """Extract first letter of each word."""
        words = phrase.split()
        return ''.join(word[0] for word in words if word and word[0] in HEBREW_ALPHABET)
    
    def extract_last_letters(self, phrase: str) -> str:
        """Extract last letter of each word."""
        words = phrase.split()
        return ''.join(word[-1] for word in words if word and word[-1] in HEBREW_ALPHABET)
    
    def extract_both(self, phrase: str) -> Tuple[str, str]:
        """Extract both first and last letters."""
        return (self.extract_first_letters(phrase), 
                self.extract_last_letters(phrase))
    
    def acronym_value(self, phrase: str, 
                     use_first: bool = True) -> int:
        """Get gematria value of acronym."""
        if use_first:
            acronym = self.extract_first_letters(phrase)
        else:
            acronym = self.extract_last_letters(phrase)
        
        return self.gematria.calculate(acronym)


# =============================================================================
# TEMURAH (LETTER PERMUTATION)
# =============================================================================

class Temurah:
    """
    Temurah: Letter permutation and substitution.
    
    Includes Atbash, Albam, and other cipher systems.
    """
    
    def __init__(self):
        self.gematria = Gematria()
        self.alphabet = HEBREW_ALPHABET
    
    def atbash(self, text: str) -> str:
        """Apply Atbash cipher."""
        return self.gematria.atbash_transform(text)
    
    def albam(self, text: str) -> str:
        """Apply Albam cipher."""
        return self.gematria.albam_transform(text)
    
    def avgad(self, text: str) -> str:
        """
        Avgad cipher: Shift each letter forward by one.
        
        א→ב, ב→ג, etc.
        """
        result = []
        for char in text:
            if char in self.alphabet:
                data = self.alphabet[char]
                new_pos = (data.index % 22) + 1
                # Find letter at new position
                for c, d in self.alphabet.items():
                    if d.index == new_pos and len(c) == 1:
                        result.append(c)
                        break
            else:
                result.append(char)
        return ''.join(result)
    
    def reverse(self, text: str) -> str:
        """Reverse the letter order."""
        return text[::-1]
    
    def permute_by_gate(self, text: str, gate: Tuple[str, str]) -> str:
        """
        Permute text based on a gate transformation.
        
        Swaps occurrences of the two gate letters.
        """
        char1, char2 = gate
        result = []
        for char in text:
            if char == char1:
                result.append(char2)
            elif char == char2:
                result.append(char1)
            else:
                result.append(char)
        return ''.join(result)


# =============================================================================
# VALIDATION
# =============================================================================

def validate_gematria() -> bool:
    """Validate Kabbalah gematria module."""
    
    # Test Hebrew alphabet
    assert len(HEBREW_ALPHABET) >= 22
    
    aleph = HEBREW_ALPHABET["א"]
    assert aleph.index == 1
    assert aleph.standard == 1
    
    tav = HEBREW_ALPHABET["ת"]
    assert tav.index == 22
    assert tav.standard == 400
    
    # Test basic gematria
    gematria = Gematria()
    
    # אחד (Echad/One) = 1+8+4 = 13
    echad = "אחד"
    assert gematria.calculate(echad) == 13
    
    # אהבה (Ahavah/Love) = 1+5+2+5 = 13
    ahavah = "אהבה"
    assert gematria.calculate(ahavah) == 13
    
    # Test isomorphism principle
    assert gematria.calculate(echad) == gematria.calculate(ahavah)
    
    # Test small value
    small_val = gematria.calculate(echad, GematriaMethod.SMALL)
    assert small_val < gematria.calculate(echad)
    
    # Test ordinal
    ordinal_val = gematria.calculate(echad, GematriaMethod.ORDINAL)
    assert ordinal_val == 1 + 8 + 4  # Same positions happen to match
    
    # Test Atbash transform
    atbash_aleph = gematria.atbash_transform("א")
    assert atbash_aleph == "ת"
    
    # Test semantic hash
    hashes = gematria.semantic_hash(echad)
    assert len(hashes) == len(GematriaMethod)
    
    # Test 231 Gates
    gates = Gates231()
    assert gates.n_gates == 231
    
    gate0 = gates.get_gate(0)
    assert gate0 is not None
    assert len(gate0) == 2
    
    gate_value = gates.get_gate_value(gate0)
    assert gate_value > 0
    
    binary = gates.gate_to_binary(gate0)
    assert bin(binary).count('1') == 2
    
    # Test rotation sequence
    aleph_gates = gates.rotation_sequence("א")
    assert len(aleph_gates) == 21  # Pairs with all other letters
    
    # Test Semantic Hash DB
    db = SemanticHashDB()
    db.add_word(echad)
    db.add_word(ahavah)
    
    equivalents = db.find_equivalent(echad)
    assert ahavah in equivalents
    
    connections = db.find_connections(echad, ahavah)
    assert connections[GematriaMethod.STANDARD.value] == True
    
    # Test Notarikon
    notarikon = Notarikon()
    # Simulated phrase
    phrase = "אב גד"
    first = notarikon.extract_first_letters(phrase)
    assert len(first) == 2
    
    # Test Temurah
    temurah = Temurah()
    
    atbash_result = temurah.atbash("אבג")
    assert len(atbash_result) == 3
    
    avgad_result = temurah.avgad("א")
    assert avgad_result == "ב"
    
    reversed_text = temurah.reverse("אבג")
    assert reversed_text == "גבא"
    
    return True


if __name__ == "__main__":
    print("Validating Kabbalah Gematria Module...")
    assert validate_gematria()
    print("✓ Kabbalah Gematria Module validated")
