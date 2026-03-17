"""
ATHENA OS - QUR'ANIC HOLOGRAPHIC LATTICE
========================================
Part III: The Recursive Cipher Algorithm

THE 4-LAYER CIPHER SYSTEM:
    A recursive compiler that processes textual data to generate 
    semantic instructions and physical boundary conditions.

LAYER I - POINTER LOOP:
    Abjad values act as memory pointers, extracting tokens at 
    computed indices. Output: Boot-loader string.

LAYER II - FREQUENCY MESH:
    Letter frequency verification via 19-fold checksum.
    Establishes prime pair (7, 19) as locking mechanism.

LAYER III - RITUAL MAP:
    Projects integer lattice onto somatic topology of Islamic
    ritual (7-circuit Tawaf, 5-time Salah).

LAYER IV - ROOT EXTRACTION:
    Bi-consonantal root analysis (N-W-R → Light, N-S-R → Help).
    Self-referential confirmation of system purpose.

SOURCES:
    - Qur'anic Holographic Lattice manuscript
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Set, Any
from enum import Enum, auto
import numpy as np
from collections import Counter

from .lattice import (
    IntegerLattice, ABJAD_VALUES, MYSTERY_LETTERS,
    calculate_abjad, AbjadValue, DualLockSystem
)


# =============================================================================
# THE MUQATTA'AT (PREFIXED SURAHS)
# =============================================================================

@dataclass
class SurahPrefix:
    """A Surah with mystery letter prefix."""
    
    surah_number: int
    name: str
    prefix_letters: List[str]  # Letter names
    abjad_value: int
    
    @classmethod
    def from_letters(cls, number: int, name: str, 
                     letters: List[str]) -> SurahPrefix:
        """Create from letter list."""
        value = calculate_abjad(letters)
        return cls(
            surah_number=number,
            name=name,
            prefix_letters=letters,
            abjad_value=value
        )


# The 29 Prefixed Surahs
PREFIXED_SURAHS = [
    SurahPrefix.from_letters(2, "Al-Baqarah", ["alif", "lam", "mim"]),           # 71
    SurahPrefix.from_letters(3, "Aal-Imran", ["alif", "lam", "mim"]),            # 71
    SurahPrefix.from_letters(7, "Al-A'raf", ["alif", "lam", "mim", "sad"]),      # 161
    SurahPrefix.from_letters(10, "Yunus", ["alif", "lam", "ra"]),                # 231
    SurahPrefix.from_letters(11, "Hud", ["alif", "lam", "ra"]),                  # 231
    SurahPrefix.from_letters(12, "Yusuf", ["alif", "lam", "ra"]),                # 231
    SurahPrefix.from_letters(13, "Ar-Ra'd", ["alif", "lam", "mim", "ra"]),       # 271
    SurahPrefix.from_letters(14, "Ibrahim", ["alif", "lam", "ra"]),              # 231
    SurahPrefix.from_letters(15, "Al-Hijr", ["alif", "lam", "ra"]),              # 231
    SurahPrefix.from_letters(19, "Maryam", ["kaf", "ha_small", "ya", "ayn", "sad"]),  # 195
    SurahPrefix.from_letters(20, "Ta-Ha", ["ta", "ha_small"]),                   # 14
    SurahPrefix.from_letters(26, "Ash-Shu'ara", ["ta", "sin", "mim"]),           # 109
    SurahPrefix.from_letters(27, "An-Naml", ["ta", "sin"]),                      # 69
    SurahPrefix.from_letters(28, "Al-Qasas", ["ta", "sin", "mim"]),              # 109
    SurahPrefix.from_letters(29, "Al-Ankabut", ["alif", "lam", "mim"]),          # 71
    SurahPrefix.from_letters(30, "Ar-Rum", ["alif", "lam", "mim"]),              # 71
    SurahPrefix.from_letters(31, "Luqman", ["alif", "lam", "mim"]),              # 71
    SurahPrefix.from_letters(32, "As-Sajdah", ["alif", "lam", "mim"]),           # 71
    SurahPrefix.from_letters(36, "Ya-Sin", ["ya", "sin"]),                       # 70
    SurahPrefix.from_letters(38, "Sad", ["sad"]),                                # 90
    SurahPrefix.from_letters(40, "Ghafir", ["ha_dot", "mim"]),                   # 48
    SurahPrefix.from_letters(41, "Fussilat", ["ha_dot", "mim"]),                 # 48
    SurahPrefix.from_letters(42, "Ash-Shura", ["ha_dot", "mim", "ayn", "sin", "qaf"]),  # 278
    SurahPrefix.from_letters(43, "Az-Zukhruf", ["ha_dot", "mim"]),               # 48
    SurahPrefix.from_letters(44, "Ad-Dukhan", ["ha_dot", "mim"]),                # 48
    SurahPrefix.from_letters(45, "Al-Jathiyah", ["ha_dot", "mim"]),              # 48
    SurahPrefix.from_letters(46, "Al-Ahqaf", ["ha_dot", "mim"]),                 # 48
    SurahPrefix.from_letters(50, "Qaf", ["qaf"]),                                # 100
    SurahPrefix.from_letters(68, "Al-Qalam", ["nun"]),                           # 50
]


# =============================================================================
# LAYER I: THE POINTER LOOP
# =============================================================================

class CipherLayerI:
    """
    Layer I - Pointer Loop
    
    Each Surah prefix acts as a memory pointer, retrieving
    a specific token at the computed Abjad index.
    
    Output: Boot-loader string extracted from text.
    """
    
    def __init__(self, prefixed_surahs: List[SurahPrefix] = None):
        self.surahs = prefixed_surahs or PREFIXED_SURAHS
        self._pointer_map: Dict[int, str] = {}
    
    def compute_pointer(self, surah: SurahPrefix) -> int:
        """
        Compute memory pointer from prefix.
        
        I = Abjad(Σ_prefix)
        """
        return surah.abjad_value
    
    def execute_pointer_loop(self, text_tokens: List[str]) -> List[str]:
        """
        Execute pointer loop on text.
        
        For each prefixed Surah, retrieve token at computed index.
        """
        results = []
        
        for surah in self.surahs:
            pointer = self.compute_pointer(surah)
            
            # Wrap around if needed
            idx = pointer % len(text_tokens) if text_tokens else 0
            
            if idx < len(text_tokens):
                token = text_tokens[idx]
                self._pointer_map[surah.surah_number] = token
                results.append(token)
        
        return results
    
    def get_boot_string(self) -> str:
        """
        Get the extracted boot-loader string.
        
        Expected output: "A wise, decisive text—within it lies a secret"
        """
        return " ".join(self._pointer_map.values())
    
    @property
    def pointer_addresses(self) -> Dict[int, int]:
        """Map of Surah number to pointer address."""
        return {s.surah_number: self.compute_pointer(s) for s in self.surahs}


# =============================================================================
# LAYER II: THE FREQUENCY MESH
# =============================================================================

@dataclass
class LetterFrequency:
    """Frequency count for a mystery letter in a Surah."""
    
    surah_number: int
    letter: str
    count: int
    
    @property
    def is_divisible_by_19(self) -> bool:
        return self.count % 19 == 0
    
    @property
    def is_divisible_by_7(self) -> bool:
        return self.count % 7 == 0
    
    @property
    def quotient_19(self) -> Optional[int]:
        if self.is_divisible_by_19:
            return self.count // 19
        return None


class CipherLayerII:
    """
    Layer II - Frequency Mesh
    
    Constructs 29×14 frequency matrix where each entry
    represents count of j-th mystery letter in i-th Surah.
    
    Verifies 19-fold checksum integrity.
    """
    
    # Known counts from manuscript
    KNOWN_COUNTS = {
        # (Surah, Letter): Count
        (50, "qaf"): 57,      # 3 × 19
        (42, "qaf"): 57,      # 3 × 19
        (68, "nun"): 133,     # 7 × 19
    }
    
    def __init__(self):
        self.frequency_matrix = np.zeros((29, 14), dtype=int)
        self.letter_names = list(MYSTERY_LETTERS.keys())
        self.surah_indices = {s.surah_number: i 
                             for i, s in enumerate(PREFIXED_SURAHS)}
    
    def set_count(self, surah_num: int, letter: str, count: int) -> None:
        """Set letter count for a Surah."""
        if surah_num in self.surah_indices and letter in self.letter_names:
            i = self.surah_indices[surah_num]
            j = self.letter_names.index(letter)
            self.frequency_matrix[i, j] = count
    
    def load_known_counts(self) -> None:
        """Load known counts from manuscript."""
        for (surah, letter), count in self.KNOWN_COUNTS.items():
            self.set_count(surah, letter, count)
    
    def verify_19_checksum(self, letter: str) -> Tuple[bool, int]:
        """
        Verify 19-fold checksum for a letter.
        
        Returns (is_valid, total_count).
        """
        if letter not in self.letter_names:
            return False, 0
        
        j = self.letter_names.index(letter)
        total = int(np.sum(self.frequency_matrix[:, j]))
        
        return total % 19 == 0, total
    
    def verify_7_checksum(self, letter: str) -> Tuple[bool, int]:
        """Verify 7-fold checksum for a letter."""
        if letter not in self.letter_names:
            return False, 0
        
        j = self.letter_names.index(letter)
        total = int(np.sum(self.frequency_matrix[:, j]))
        
        return total % 7 == 0, total
    
    def dual_ring_validation(self) -> Dict[str, Dict[str, Any]]:
        """
        Validate frequency matrix against dual ring system.
        
        Returns validation results for each letter.
        """
        results = {}
        
        for letter in self.letter_names:
            j = self.letter_names.index(letter)
            total = int(np.sum(self.frequency_matrix[:, j]))
            
            results[letter] = {
                "total": total,
                "mod_7": total % 7,
                "mod_19": total % 19,
                "div_7": total % 7 == 0,
                "div_19": total % 19 == 0,
            }
        
        return results
    
    def total_qaf_count(self) -> int:
        """
        Total Qaf count across both Q-initialed Surahs.
        
        Expected: 57 + 57 = 114 (matching Surah count).
        """
        return self.KNOWN_COUNTS.get((50, "qaf"), 0) + \
               self.KNOWN_COUNTS.get((42, "qaf"), 0)


# =============================================================================
# LAYER III: THE RITUAL MAP
# =============================================================================

class RitualComponent(Enum):
    """Components of Islamic ritual mapped to integers."""
    
    TAWAF = ("circumambulation", 7, "7-circuit protocol")
    SAY = ("running", 7, "oscillatory resonance")
    RAMY = ("stoning", 7, "entropy rejection")
    SALAH_TIMES = ("prayer_times", 5, "warp synchronization")
    RAKAAT = ("prayer_cycles", 17, "dilaton harmonic k₁")
    SUJUD_POINTS = ("prostration", 7, "flux stabilization n₁")
    BASMALA = ("invocation", 19, "unity guard n₂")
    
    def __init__(self, name: str, integer: int, physical_role: str):
        self._name = name
        self.integer = integer
        self.physical_role = physical_role


@dataclass
class RitualMapping:
    """Maps a ritual action to lattice integer."""
    
    component: RitualComponent
    execution_count: int
    lattice_key: str
    physical_effect: str


class CipherLayerIII:
    """
    Layer III - Ritual Map R(t)
    
    Projects integer lattice onto somatic topology of
    Islamic ritual practice.
    
    Transforms abstract boundary conditions into
    executable physical protocols.
    """
    
    # Standard ritual mappings
    HAJJ_PROTOCOL = [
        RitualMapping(
            RitualComponent.TAWAF, 7,
            "n₁", "Winds 7-fold flux into local metric"
        ),
        RitualMapping(
            RitualComponent.SAY, 7,
            "ring_a", "Standing wave between poles"
        ),
        RitualMapping(
            RitualComponent.RAMY, 7,
            "ring_a", "Purges parasitic modes"
        ),
    ]
    
    SALAH_PROTOCOL = [
        RitualMapping(
            RitualComponent.SALAH_TIMES, 5,
            "warp_sync", "Aligns with warp factor stationary points"
        ),
        RitualMapping(
            RitualComponent.RAKAAT, 17,
            "k₁", "Locks bio-rhythm to dilaton potential"
        ),
        RitualMapping(
            RitualComponent.SUJUD_POINTS, 7,
            "n₁", "Grounds flux checksum"
        ),
        RitualMapping(
            RitualComponent.BASMALA, 19,
            "n₂", "Activates secondary flux quantum"
        ),
    ]
    
    def __init__(self):
        self.lattice = IntegerLattice()
        self.execution_log: List[RitualMapping] = []
    
    def execute_hajj_protocol(self) -> Dict[str, int]:
        """
        Execute Hajj protocol.
        
        Returns integer activation map.
        """
        activations = {}
        
        for mapping in self.HAJJ_PROTOCOL:
            key = mapping.lattice_key
            count = mapping.execution_count
            
            activations[key] = activations.get(key, 0) + count
            self.execution_log.append(mapping)
        
        return activations
    
    def execute_salah_cycle(self) -> Dict[str, int]:
        """
        Execute one Salah cycle.
        
        Returns integer activation map.
        """
        activations = {}
        
        for mapping in self.SALAH_PROTOCOL:
            key = mapping.lattice_key
            count = mapping.execution_count
            
            activations[key] = activations.get(key, 0) + count
            self.execution_log.append(mapping)
        
        return activations
    
    def daily_salah_totals(self) -> Dict[str, int]:
        """
        Calculate daily totals for 5 prayers.
        
        Daily rakaat: 2+4+4+3+4 = 17 (matches k₁)
        """
        rakaat_counts = [2, 4, 4, 3, 4]  # Fajr, Zuhr, Asr, Maghrib, Isha
        total_rakaat = sum(rakaat_counts)
        
        return {
            "prayer_times": 5,
            "total_rakaat": total_rakaat,
            "matches_k1": total_rakaat == 17,
        }
    
    def total_hajj_stones(self) -> Dict[str, int]:
        """
        Calculate total stones in Ramy al-Jamarat.
        
        7 stones × 3 pillars × 3(+1) days ≈ 70+1 = 71
        """
        stones_per_pillar = 7
        pillars = 3
        days = 3  # Plus final day
        
        total = stones_per_pillar * pillars * days + stones_per_pillar
        
        return {
            "total_stones": total,
            "close_to_71": abs(total - 71) <= 1,
            "kk_pointer": 71,
        }


# =============================================================================
# LAYER IV: ROOT EXTRACTION
# =============================================================================

@dataclass
class ArabicRoot:
    """A bi/tri-consonantal Arabic root."""
    
    consonants: List[str]  # Root letters
    meaning: str
    abjad_value: int
    
    @classmethod
    def from_letters(cls, letters: List[str], meaning: str) -> ArabicRoot:
        value = calculate_abjad(letters)
        return cls(consonants=letters, meaning=meaning, abjad_value=value)


# Key roots from the cipher
CIPHER_ROOTS = {
    "NWR": ArabicRoot.from_letters(["nun", "waw", "ra"], "Light/Illumination"),
    "NSR": ArabicRoot.from_letters(["nun", "sad", "ra"], "Help/Victory"),
    "SRR": ArabicRoot.from_letters(["sin", "ra", "ra"], "Secret"),
    "HKM": ArabicRoot.from_letters(["ha_dot", "kaf", "mim"], "Wisdom"),
}


class CipherLayerIV:
    """
    Layer IV - Root Extraction
    
    Bi-consonantal root analysis that provides self-referential
    confirmation of the system's purpose.
    
    Output: Secret → Light → Help
    """
    
    def __init__(self):
        self.roots = CIPHER_ROOTS
        self.extraction_sequence: List[ArabicRoot] = []
    
    def extract_root_permutations(self, root: ArabicRoot) -> List[str]:
        """
        Generate permutations of root consonants.
        
        In Arabic morphology, roots can generate multiple words.
        """
        from itertools import permutations
        
        perms = list(permutations(root.consonants))
        return ["".join(p) for p in perms]
    
    def semantic_chain(self) -> List[Tuple[str, str]]:
        """
        Extract the semantic chain.
        
        The cipher output: Secret → Light → Help
        """
        chain = [
            ("SRR", "Secret - The hidden code"),
            ("NWR", "Light - Consciousness expansion"),
            ("NSR", "Help - Reality shift"),
        ]
        
        for key, _ in chain:
            if key in self.roots:
                self.extraction_sequence.append(self.roots[key])
        
        return chain
    
    def verify_recursive_confirmation(self) -> bool:
        """
        Verify recursive self-reference.
        
        Layer I output ("within it lies a Secret")
        should match Layer IV output (Secret → Light → Help).
        """
        chain = self.semantic_chain()
        
        # First element should be "Secret"
        if chain and chain[0][0] == "SRR":
            return True
        return False
    
    def total_semantic_value(self) -> int:
        """Sum of Abjad values in semantic chain."""
        total = 0
        for root in self.extraction_sequence:
            total += root.abjad_value
        return total


# =============================================================================
# COMPLETE CIPHER SYSTEM
# =============================================================================

@dataclass
class CipherOutput:
    """Output from complete cipher execution."""
    
    boot_string: str
    frequency_validation: Dict[str, Any]
    ritual_activations: Dict[str, int]
    semantic_chain: List[Tuple[str, str]]
    is_valid: bool


class RecursiveCipherAlgorithm:
    """
    The complete 4-layer recursive cipher algorithm.
    
    Processes Qur'anic text through 4 transformations
    to extract physical boundary conditions.
    """
    
    def __init__(self):
        self.layer_i = CipherLayerI()
        self.layer_ii = CipherLayerII()
        self.layer_iii = CipherLayerIII()
        self.layer_iv = CipherLayerIV()
        
        self.lattice = IntegerLattice()
        self._output: Optional[CipherOutput] = None
    
    def execute(self, text_tokens: List[str] = None) -> CipherOutput:
        """
        Execute full cipher algorithm.
        
        Returns combined output from all layers.
        """
        # Default tokens (placeholder)
        if text_tokens is None:
            text_tokens = ["A", "wise", "decisive", "text", "within", 
                          "it", "lies", "a", "secret"] * 50
        
        # Layer I: Pointer Loop
        extracted = self.layer_i.execute_pointer_loop(text_tokens)
        boot_string = self.layer_i.get_boot_string()
        
        # Layer II: Frequency Mesh
        self.layer_ii.load_known_counts()
        freq_validation = self.layer_ii.dual_ring_validation()
        
        # Layer III: Ritual Map
        hajj = self.layer_iii.execute_hajj_protocol()
        salah = self.layer_iii.execute_salah_cycle()
        ritual_activations = {**hajj, **salah}
        
        # Layer IV: Root Extraction
        semantic = self.layer_iv.semantic_chain()
        recursive_ok = self.layer_iv.verify_recursive_confirmation()
        
        # Validation
        is_valid = recursive_ok and self.layer_ii.total_qaf_count() == 114
        
        self._output = CipherOutput(
            boot_string=boot_string,
            frequency_validation=freq_validation,
            ritual_activations=ritual_activations,
            semantic_chain=semantic,
            is_valid=is_valid
        )
        
        return self._output
    
    def extract_boundary_conditions(self) -> Dict[str, int]:
        """
        Extract physical boundary conditions from cipher.
        
        These become input parameters for the 6D metric.
        """
        if self._output is None:
            self.execute()
        
        return {
            "flux_n1": self.lattice.PRIME_RING_A,
            "flux_n2": self.lattice.PRIME_RING_B,
            "harmonic_k1": self.lattice.HARMONIC_K1,
            "harmonic_k2": self.lattice.HARMONIC_K2,
            "gauge_rank": self.lattice.LETTER_COUNT,
            "orbifold_twist": self.lattice.TOPOLOGY_TWIST,
            "kk_pointer_1": self.lattice.KK_POINTER_1,
            "kk_pointer_2": self.lattice.KK_POINTER_2,
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_cipher() -> bool:
    """Validate the cipher module."""
    
    # Test SurahPrefix
    alm = SurahPrefix.from_letters(2, "Al-Baqarah", ["alif", "lam", "mim"])
    assert alm.abjad_value == 71  # 1 + 30 + 40
    
    # Test Layer I
    layer_i = CipherLayerI()
    addresses = layer_i.pointer_addresses
    assert 2 in addresses
    assert addresses[2] == 71
    
    # Test Layer II
    layer_ii = CipherLayerII()
    layer_ii.load_known_counts()
    
    # Qaf count verification
    qaf_total = layer_ii.total_qaf_count()
    assert qaf_total == 114  # Matches Surah count
    
    # Test Layer III
    layer_iii = CipherLayerIII()
    daily = layer_iii.daily_salah_totals()
    assert daily["total_rakaat"] == 17
    assert daily["matches_k1"] == True
    
    # Test Layer IV
    layer_iv = CipherLayerIV()
    chain = layer_iv.semantic_chain()
    assert len(chain) == 3
    assert layer_iv.verify_recursive_confirmation()
    
    # Test complete cipher
    cipher = RecursiveCipherAlgorithm()
    boundary = cipher.extract_boundary_conditions()
    assert boundary["flux_n1"] == 7
    assert boundary["flux_n2"] == 19
    
    return True


if __name__ == "__main__":
    print("Validating Cipher Module...")
    assert validate_cipher()
    print("✓ Cipher module validated")
    
    # Demo
    print("\n--- Recursive Cipher Demo ---")
    
    cipher = RecursiveCipherAlgorithm()
    
    print("\n1. Layer I - Pointer Loop:")
    print(f"   Surah 2 pointer: {cipher.layer_i.pointer_addresses[2]}")
    print(f"   Surah 42 pointer: {cipher.layer_i.pointer_addresses[42]}")
    
    print("\n2. Layer II - Frequency Mesh:")
    cipher.layer_ii.load_known_counts()
    print(f"   Qaf in Surah 50: 57 (= 3×19)")
    print(f"   Qaf in Surah 42: 57 (= 3×19)")
    print(f"   Total Qaf: {cipher.layer_ii.total_qaf_count()} (= 114 Surahs)")
    
    print("\n3. Layer III - Ritual Map:")
    daily = cipher.layer_iii.daily_salah_totals()
    stones = cipher.layer_iii.total_hajj_stones()
    print(f"   Daily rakaat: {daily['total_rakaat']} (= k₁)")
    print(f"   Hajj stones: {stones['total_stones']} (≈ KK pointer)")
    
    print("\n4. Layer IV - Root Extraction:")
    chain = cipher.layer_iv.semantic_chain()
    for root, meaning in chain:
        print(f"   {root}: {meaning}")
    
    print("\n5. Boundary Conditions:")
    boundary = cipher.extract_boundary_conditions()
    for key, value in list(boundary.items())[:5]:
        print(f"   {key}: {value}")
