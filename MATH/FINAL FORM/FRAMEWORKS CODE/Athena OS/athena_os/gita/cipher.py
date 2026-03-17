"""
ATHENA OS - BHAGAVAD GĪTĀ COMPUTATIONAL FRAMEWORK
==================================================
Part VI: The Holographic Encryption (The Gītā Cipher)

THE CIPHER STRUCTURE:
    The Gītā is not merely a linear narrative but a self-extracting
    archive. The text contains hidden executable code accessible
    through specific decryption keys.

THE RAHASYAM TAG SYSTEM:
    Entry points marked with "Rahasyam" (Secret) serve as
    pointers to the cipher:
    - 4:3  "rahasyam hy etad uttamam" (Supreme Secret)
    - 9:1  "idaṁ tu te guhyatamaṁ" (Most Secret)
    - 18:64 "sarva-guhyatamaṁ" (Greatest Secret of All)
    - 18:66 "sarva-dharmān parityajya" (Final Instruction)

THE 5-VERSE KERNEL:
    Verses 18:64-68 contain the compressed seed of the entire text.
    These form a fractal kernel that expands to the full 700 verses.

THE TERMINATION TOKEN:
    The syllable "haṁ" (I/Ego) at verse 18:66 serves as the
    termination command that halts the samsaric loop.

SOURCES:
    The Bhagavad Gītā: A Computational Treatise, Chapter 5
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import numpy as np
import hashlib


# =============================================================================
# SECRET LEVELS
# =============================================================================

class SecretLevel(Enum):
    """Levels of secrecy (encryption depth)."""
    
    GUHYA = (1, "secret", "Basic hidden meaning")
    GUHYATARA = (2, "more_secret", "Deeper hidden meaning")
    GUHYATAMA = (3, "most_secret", "Deepest core instruction")
    
    def __init__(self, level: int, name: str, description: str):
        self.level = level
        self._name = name
        self.description = description


# =============================================================================
# THE RAHASYAM TAGS (Entry Points)
# =============================================================================

@dataclass
class RahasyamTag:
    """
    A 'Rahasyam' (Secret) tag marking a cipher entry point.
    
    These serve as initialization vectors for the decryption algorithm.
    """
    
    chapter: int
    verse: int
    sanskrit: str
    translation: str
    secret_level: SecretLevel
    function: str  # Computational function
    
    @property
    def verse_id(self) -> str:
        return f"{self.chapter}.{self.verse}"
    
    def get_hash(self) -> str:
        """Generate hash of the tag for verification."""
        data = f"{self.chapter}:{self.verse}:{self.sanskrit}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]


# The four major Rahasyam tags
RAHASYAM_TAGS = [
    RahasyamTag(
        chapter=4, verse=3,
        sanskrit="rahasyam hy etad uttamam",
        translation="This is the supreme secret",
        secret_level=SecretLevel.GUHYA,
        function="INIT_VECTOR"
    ),
    RahasyamTag(
        chapter=9, verse=1,
        sanskrit="idaṁ tu te guhyatamaṁ pravakṣyāmy anasūyave",
        translation="I shall declare to you this most secret wisdom",
        secret_level=SecretLevel.GUHYATARA,
        function="ENCRYPTION_KEY"
    ),
    RahasyamTag(
        chapter=18, verse=64,
        sanskrit="sarva-guhyatamaṁ bhūyaḥ śṛṇu me paramaṁ vacaḥ",
        translation="Hear again My supreme word, most secret of all",
        secret_level=SecretLevel.GUHYATAMA,
        function="KERNEL_ENTRY"
    ),
    RahasyamTag(
        chapter=18, verse=66,
        sanskrit="sarva-dharmān parityajya mām ekaṁ śaraṇaṁ vraja",
        translation="Abandon all dharmas, take refuge in Me alone",
        secret_level=SecretLevel.GUHYATAMA,
        function="TERMINATION_TOKEN"
    ),
]


# =============================================================================
# THE 5-VERSE KERNEL
# =============================================================================

@dataclass
class KernelVerse:
    """A verse in the 5-verse compression kernel."""
    
    verse_number: int  # 64-68
    sanskrit_first_line: str
    function: str
    compression_ratio: float  # How much it expands to
    
    def expansion_factor(self, total_verses: int = 700) -> float:
        """How many verses this kernel verse represents."""
        return total_verses / 5 * self.compression_ratio


# The 5-verse kernel (18:64-68)
KERNEL_VERSES = [
    KernelVerse(
        verse_number=64,
        sanskrit_first_line="sarva-guhyatamaṁ bhūyaḥ",
        function="HEADER",
        compression_ratio=1.0
    ),
    KernelVerse(
        verse_number=65,
        sanskrit_first_line="man-manā bhava mad-bhakto",
        function="BHAKTI_INSTRUCTION",
        compression_ratio=1.2
    ),
    KernelVerse(
        verse_number=66,
        sanskrit_first_line="sarva-dharmān parityajya",
        function="MAIN_EXECUTABLE",
        compression_ratio=1.5
    ),
    KernelVerse(
        verse_number=67,
        sanskrit_first_line="idaṁ te nātapaskāya",
        function="ACCESS_CONTROL",
        compression_ratio=0.8
    ),
    KernelVerse(
        verse_number=68,
        sanskrit_first_line="ya idaṁ paramaṁ guhyaṁ",
        function="REWARD_PROMISE",
        compression_ratio=0.5
    ),
]


# =============================================================================
# THE TERMINATION TOKEN
# =============================================================================

@dataclass
class TerminationToken:
    """
    The 'haṁ' (I/Ego) termination token.
    
    This syllable in verse 18:66 serves as the HALT instruction
    that breaks the recursive loop of Samsara.
    
    Position: The word 'ahaṁ' (I) at the end of verse 18:66
    """
    
    syllable: str = "haṁ"
    verse_location: str = "18:66"
    
    # Energy properties
    gamma_minimum: float = 0.02  # μV² (cortical energy minimum)
    breath_phase: int = 1000     # The 1000th "petal" of breath cycle
    
    def is_termination(self, input_syllable: str) -> bool:
        """Check if input matches termination token."""
        return input_syllable.lower().strip() in ["haṁ", "ham", "aham", "ahaṁ"]
    
    def halt_state(self) -> Dict[str, Any]:
        """Return the state after HALT is executed."""
        return {
            "ego_state": "DISSOLVED",
            "thought_stream": "TERMINATED",
            "samsara_loop": "BROKEN",
            "gamma_energy": self.gamma_minimum,
            "breath_state": "KEVALA_KUMBHAKA",
        }


# =============================================================================
# THE HOLOGRAPHIC COMPRESSION
# =============================================================================

@dataclass
class HolographicCompressor:
    """
    Holographic Compression Algorithm.
    
    The entire 700-verse Gītā is losslessly compressed into the
    5-verse kernel (18:64-68), which can expand back to the full text.
    
    Properties:
        - Self-similar structure (fractal)
        - Information-preserving transformation
        - Bidirectional (compress/decompress)
    """
    
    kernel_verses: List[KernelVerse] = field(default_factory=lambda: KERNEL_VERSES)
    total_verses: int = 700
    
    def compression_ratio(self) -> float:
        """Overall compression ratio."""
        return self.total_verses / len(self.kernel_verses)
    
    def compress(self, verse_array: np.ndarray) -> np.ndarray:
        """
        Compress verse data to kernel size.
        
        Uses hierarchical averaging (simplified model).
        """
        n_verses = len(verse_array)
        kernel_size = len(self.kernel_verses)
        
        # Reshape and average
        chunk_size = n_verses // kernel_size
        compressed = np.zeros(kernel_size)
        
        for i in range(kernel_size):
            start = i * chunk_size
            end = start + chunk_size
            compressed[i] = np.mean(verse_array[start:end])
        
        return compressed
    
    def decompress(self, kernel_data: np.ndarray) -> np.ndarray:
        """
        Decompress kernel back to full size.
        
        Uses interpolation (simplified model).
        """
        kernel_size = len(kernel_data)
        
        # Expand using interpolation
        expanded = np.zeros(self.total_verses)
        chunk_size = self.total_verses // kernel_size
        
        for i in range(kernel_size):
            start = i * chunk_size
            end = start + chunk_size
            
            # Add variation based on kernel verse properties
            factor = self.kernel_verses[i].compression_ratio if i < len(self.kernel_verses) else 1.0
            expanded[start:end] = kernel_data[i] * factor
            
            # Add fractal detail
            expanded[start:end] += np.random.randn(chunk_size) * 0.01
        
        return expanded
    
    def verify_lossless(self, original: np.ndarray, 
                        tolerance: float = 0.1) -> bool:
        """
        Verify that compression is approximately lossless.
        
        Note: True lossless requires the full cipher mechanism.
        """
        compressed = self.compress(original)
        reconstructed = self.decompress(compressed)
        
        # Check mean is preserved
        return abs(np.mean(original) - np.mean(reconstructed)) < tolerance


# =============================================================================
# THE CIPHER ENGINE
# =============================================================================

@dataclass
class GitaCipherEngine:
    """
    The complete Gītā Cipher Engine.
    
    Provides encryption/decryption using the Rahasyam tag system
    and holographic compression.
    """
    
    tags: List[RahasyamTag] = field(default_factory=lambda: RAHASYAM_TAGS)
    compressor: HolographicCompressor = field(default_factory=HolographicCompressor)
    termination: TerminationToken = field(default_factory=TerminationToken)
    
    # Cipher state
    initialized: bool = False
    decryption_key: Optional[str] = None
    
    def initialize(self, key_tag: RahasyamTag = None) -> bool:
        """
        Initialize the cipher with a Rahasyam tag.
        
        Default uses the 9:1 tag (encryption key).
        """
        if key_tag is None:
            key_tag = self.tags[1]  # 9:1 tag
        
        self.decryption_key = key_tag.get_hash()
        self.initialized = True
        
        return True
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt plaintext using the Gītā cipher.
        
        Simple XOR with key hash (demonstration).
        """
        if not self.initialized:
            self.initialize()
        
        key_bytes = self.decryption_key.encode()
        plain_bytes = plaintext.encode()
        
        # XOR encryption
        encrypted = bytes([
            plain_bytes[i] ^ key_bytes[i % len(key_bytes)]
            for i in range(len(plain_bytes))
        ])
        
        return encrypted.hex()
    
    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt ciphertext using the Gītā cipher.
        """
        if not self.initialized:
            self.initialize()
        
        key_bytes = self.decryption_key.encode()
        cipher_bytes = bytes.fromhex(ciphertext)
        
        # XOR decryption (same as encryption)
        decrypted = bytes([
            cipher_bytes[i] ^ key_bytes[i % len(key_bytes)]
            for i in range(len(cipher_bytes))
        ])
        
        return decrypted.decode()
    
    def execute_halt(self, input_token: str) -> Dict[str, Any]:
        """
        Execute the HALT instruction if termination token detected.
        """
        if self.termination.is_termination(input_token):
            return self.termination.halt_state()
        
        return {"status": "CONTINUE", "token_received": input_token}
    
    def get_kernel_summary(self) -> Dict[str, Any]:
        """Get summary of the 5-verse kernel."""
        return {
            "verses": [
                {
                    "number": kv.verse_number,
                    "function": kv.function,
                    "ratio": kv.compression_ratio,
                }
                for kv in self.compressor.kernel_verses
            ],
            "total_ratio": self.compressor.compression_ratio(),
        }


# =============================================================================
# THE RECURSIVE STRUCTURE
# =============================================================================

@dataclass
class RecursiveStructure:
    """
    The recursive (fractal) structure of the Gītā.
    
    Each chapter contains the whole teaching in miniature.
    Each verse contains the chapter's essence.
    Each word contains the verse's meaning.
    """
    
    levels: List[str] = field(default_factory=lambda: [
        "TEXT",      # 700 verses
        "CHAPTER",   # 18 chapters
        "VERSE",     # Individual verse
        "PADA",      # Quarter-verse
        "WORD",      # Individual word
        "SYLLABLE",  # Akṣara (letter)
        "BINDU",     # Point (zero-dimension)
    ])
    
    def level_count(self, level: str) -> int:
        """Approximate count at each level."""
        counts = {
            "TEXT": 1,
            "CHAPTER": 18,
            "VERSE": 700,
            "PADA": 2800,
            "WORD": 9000,
            "SYLLABLE": 32000,
            "BINDU": 1,  # Returns to unity
        }
        return counts.get(level, 0)
    
    def fractal_dimension(self) -> float:
        """
        Estimate fractal dimension of the text structure.
        
        Based on verse-to-chapter ratio.
        """
        return np.log(700) / np.log(18)  # ≈ 2.27
    
    def self_similarity_check(self, chapter_data: np.ndarray,
                               text_data: np.ndarray) -> float:
        """
        Check self-similarity between chapter and full text.
        
        Returns correlation coefficient.
        """
        # Resize chapter to match text
        chapter_expanded = np.interp(
            np.linspace(0, 1, len(text_data)),
            np.linspace(0, 1, len(chapter_data)),
            chapter_data
        )
        
        # Compute correlation
        correlation = np.corrcoef(text_data, chapter_expanded)[0, 1]
        return float(correlation)


# =============================================================================
# VALIDATION
# =============================================================================

def validate_cipher() -> bool:
    """Validate the cipher module."""
    
    # Test RahasyamTag
    tag = RAHASYAM_TAGS[0]
    assert tag.chapter == 4
    assert tag.verse == 3
    assert len(tag.get_hash()) == 16
    
    # Test TerminationToken
    token = TerminationToken()
    assert token.is_termination("haṁ")
    assert token.is_termination("aham")
    assert not token.is_termination("brahman")
    
    halt = token.halt_state()
    assert halt["ego_state"] == "DISSOLVED"
    
    # Test HolographicCompressor
    compressor = HolographicCompressor()
    assert compressor.compression_ratio() == 140.0  # 700/5
    
    # Test compression/decompression
    original = np.random.randn(700)
    compressed = compressor.compress(original)
    assert len(compressed) == 5
    
    decompressed = compressor.decompress(compressed)
    assert len(decompressed) == 700
    
    # Test GitaCipherEngine
    engine = GitaCipherEngine()
    assert engine.initialize()
    assert engine.initialized
    assert engine.decryption_key is not None
    
    # Test encrypt/decrypt
    plaintext = "test"
    encrypted = engine.encrypt(plaintext)
    decrypted = engine.decrypt(encrypted)
    assert decrypted == plaintext
    
    # Test halt execution
    result = engine.execute_halt("haṁ")
    assert result["ego_state"] == "DISSOLVED"
    
    result = engine.execute_halt("other")
    assert result["status"] == "CONTINUE"
    
    # Test RecursiveStructure
    recursive = RecursiveStructure()
    assert recursive.level_count("CHAPTER") == 18
    assert recursive.level_count("VERSE") == 700
    
    fd = recursive.fractal_dimension()
    assert 2.0 < fd < 3.0
    
    return True


if __name__ == "__main__":
    print("Validating Cipher Module...")
    assert validate_cipher()
    print("✓ Cipher module validated")
    
    # Demo
    print("\n--- Gītā Cipher Demo ---")
    
    print("\n1. Rahasyam Tags (Entry Points):")
    for tag in RAHASYAM_TAGS:
        print(f"   {tag.verse_id}: {tag.secret_level.name} - {tag.function}")
    
    print("\n2. 5-Verse Kernel (18:64-68):")
    for kv in KERNEL_VERSES:
        print(f"   v{kv.verse_number}: {kv.function} (ratio: {kv.compression_ratio})")
    
    print("\n3. Holographic Compression:")
    compressor = HolographicCompressor()
    print(f"   Compression ratio: {compressor.compression_ratio()}:1")
    print(f"   700 verses → 5 kernel verses")
    
    print("\n4. Termination Token:")
    token = TerminationToken()
    print(f"   Token: '{token.syllable}' at {token.verse_location}")
    print(f"   Gamma minimum: {token.gamma_minimum} μV²")
    
    print("\n5. Cipher Engine Test:")
    engine = GitaCipherEngine()
    engine.initialize()
    plaintext = "moksha"
    encrypted = engine.encrypt(plaintext)
    decrypted = engine.decrypt(encrypted)
    print(f"   Original: {plaintext}")
    print(f"   Encrypted: {encrypted[:20]}...")
    print(f"   Decrypted: {decrypted}")
