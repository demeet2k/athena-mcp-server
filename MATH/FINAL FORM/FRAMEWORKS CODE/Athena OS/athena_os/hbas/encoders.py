"""
ATHENA OS - HBAS-Ω: ENCODERS MODULE
====================================
Encoding Systems Detected Across Ancient Civilizations

ENCODER TYPES:

1. BINARY / HYPERCUBE ENCODERS:
   - Ifá (256 = 2⁸), I Ching (64 = 2⁶), Kabbalah (2^n trees)
   - Bit-space and operator alphabets

2. GRAPH / WORLD-TREE ENCODERS:
   - Yggdrasil, Kabbalistic Tree, Inca Ceques
   - State-space topology

3. SPECTRAL / HARMONIC ENCODERS:
   - Pythagorean intervals, Vedic chant, Tibetan mantras
   - Eigenmodes and resonance

4. METROLOGICAL ENCODERS:
   - Sumerian sexagesimal, Harappan binary/decimal
   - Number systems and measurement

5. TRANSITION / REPAIR ENCODERS:
   - Egyptian Duat, Tibetan Bardo, Zoroastrian 12k-year
   - Error detection, state transitions, reset protocols

Each encoder is a MODULE of the same universal machine,
rotated into different cultural coordinates.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Callable, Any, Union
from enum import Enum, auto
from abc import ABC, abstractmethod
import numpy as np


# =============================================================================
# ENCODER TYPES
# =============================================================================

class EncoderType(Enum):
    """Types of encoding systems."""
    
    BINARY = "binary"           # Hypercube encoders (2^n states)
    GRAPH = "graph"             # World-tree / topology encoders
    SPECTRAL = "spectral"       # Harmonic / eigenmode encoders
    METROLOGICAL = "metrology"  # Number system / measurement
    TRANSITION = "transition"   # State change / error correction


# =============================================================================
# BINARY / HYPERCUBE ENCODERS
# =============================================================================

@dataclass
class BinaryEncoder:
    """
    Binary Hypercube Encoder.
    
    Encodes states as vertices of Q_n (n-dimensional Boolean hypercube).
    Examples: Ifá (Q_8 = 256), I Ching (Q_6 = 64)
    """
    
    name: str
    dimension: int  # n in 2^n
    
    # Derived
    n_states: int = field(init=False)
    
    # Generator set (principal states)
    generators: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        self.n_states = 2 ** self.dimension
    
    def state_to_binary(self, state_index: int) -> np.ndarray:
        """Convert state index to binary vector."""
        binary = np.zeros(self.dimension, dtype=np.int8)
        for i in range(self.dimension):
            binary[i] = (state_index >> i) & 1
        return binary
    
    def binary_to_state(self, binary: np.ndarray) -> int:
        """Convert binary vector to state index."""
        state = 0
        for i, bit in enumerate(binary):
            state += int(bit) << i
        return state
    
    def hamming_distance(self, state1: int, state2: int) -> int:
        """Compute Hamming distance between two states."""
        xor = state1 ^ state2
        return bin(xor).count('1')
    
    def neighbors(self, state: int) -> List[int]:
        """Get all states at Hamming distance 1."""
        result = []
        for i in range(self.dimension):
            neighbor = state ^ (1 << i)
            result.append(neighbor)
        return result
    
    def tensor_decompose(self, state: int, split: int) -> Tuple[int, int]:
        """
        Decompose state as tensor product of two sub-states.
        
        For Ifá: 256 = 16 × 16 (split at 4 bits)
        """
        mask = (1 << split) - 1
        left = state & mask
        right = state >> split
        return left, right
    
    def generate_adjacency_matrix(self) -> np.ndarray:
        """Generate hypercube adjacency matrix."""
        adj = np.zeros((self.n_states, self.n_states), dtype=np.int8)
        
        for state in range(self.n_states):
            for neighbor in self.neighbors(state):
                adj[state, neighbor] = 1
        
        return adj


class IfaEncoder(BinaryEncoder):
    """
    Ọpẹ́-256: The Ifá 8-bit Binary Encoder.
    
    256 Odù as vertices of Q_8 hypercube.
    16 Principal Odù (Méjì) as generators.
    """
    
    def __init__(self):
        super().__init__(
            name="Ifá/Ọpẹ́-256",
            dimension=8
        )
        self.generators = [
            "Ogbe", "Oyeku", "Iwori", "Odi",
            "Irosun", "Owonrin", "Obara", "Okanran",
            "Ogunda", "Osa", "Ika", "Oturupon",
            "Otura", "Irete", "Ose", "Ofun"
        ]
    
    def odu_from_casting(self, marks: List[int]) -> int:
        """
        Convert casting marks to Odù index.
        
        marks: List of 8 values, each 1 (single line) or 0 (double line)
        """
        if len(marks) != 8:
            raise ValueError("Ifá requires exactly 8 marks")
        
        return self.binary_to_state(np.array(marks))
    
    def get_principal_odu(self, index: int) -> str:
        """Get name of principal Odù by index (0-15)."""
        if 0 <= index < 16:
            return self.generators[index]
        raise ValueError(f"Principal index must be 0-15, got {index}")
    
    def decompose_to_principals(self, odu: int) -> Tuple[str, str]:
        """Decompose composite Odù into two principals."""
        left, right = self.tensor_decompose(odu, 4)
        return self.get_principal_odu(right), self.get_principal_odu(left)


class IChingEncoder(BinaryEncoder):
    """
    I Ching 6-bit Binary Encoder.
    
    64 Hexagrams as vertices of Q_6 hypercube.
    8 Trigrams as generators.
    """
    
    def __init__(self):
        super().__init__(
            name="I Ching/易經",
            dimension=6
        )
        self.generators = [
            "☰ Qián (Heaven)", "☱ Duì (Lake)",
            "☲ Lí (Fire)", "☳ Zhèn (Thunder)",
            "☴ Xùn (Wind)", "☵ Kǎn (Water)",
            "☶ Gèn (Mountain)", "☷ Kūn (Earth)"
        ]
        
        # Trigram mapping (3-bit)
        self.trigrams = {
            0b111: "☰", 0b011: "☱", 0b101: "☲", 0b001: "☳",
            0b110: "☴", 0b010: "☵", 0b100: "☶", 0b000: "☷"
        }
    
    def decompose_to_trigrams(self, hexagram: int) -> Tuple[str, str]:
        """Decompose hexagram into upper and lower trigrams."""
        lower = hexagram & 0b111
        upper = (hexagram >> 3) & 0b111
        return self.trigrams.get(lower, "?"), self.trigrams.get(upper, "?")


# =============================================================================
# GRAPH / WORLD-TREE ENCODERS
# =============================================================================

@dataclass
class GraphEncoder:
    """
    Graph / World-Tree Encoder.
    
    Encodes state space as graph with nodes and edges.
    Examples: Yggdrasil (9 nodes), Sefirotic Tree (10 nodes)
    """
    
    name: str
    n_nodes: int
    n_edges: int
    
    # Node and edge labels
    nodes: List[str] = field(default_factory=list)
    edges: List[Tuple[int, int, str]] = field(default_factory=list)
    
    # Adjacency
    _adjacency: Optional[np.ndarray] = None
    
    def build_adjacency(self) -> np.ndarray:
        """Build adjacency matrix from edges."""
        adj = np.zeros((self.n_nodes, self.n_nodes), dtype=np.int8)
        
        for src, dst, _ in self.edges:
            adj[src, dst] = 1
            adj[dst, src] = 1  # Undirected
        
        self._adjacency = adj
        return adj
    
    def shortest_path(self, start: int, end: int) -> List[int]:
        """Find shortest path using BFS."""
        if self._adjacency is None:
            self.build_adjacency()
        
        from collections import deque
        
        visited = {start}
        queue = deque([(start, [start])])
        
        while queue:
            node, path = queue.popleft()
            
            if node == end:
                return path
            
            for neighbor in range(self.n_nodes):
                if self._adjacency[node, neighbor] and neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return []  # No path
    
    def get_neighbors(self, node: int) -> List[int]:
        """Get all neighbors of a node."""
        if self._adjacency is None:
            self.build_adjacency()
        
        return [i for i in range(self.n_nodes) if self._adjacency[node, i]]


class YggdrasilEncoder(GraphEncoder):
    """
    Yggdrasil: Norse 9-World Graph Encoder.
    
    9 nodes (worlds) connected by the World Tree.
    24 runes as transformation operators on edges.
    """
    
    def __init__(self):
        super().__init__(
            name="Yggdrasil",
            n_nodes=9,
            n_edges=0  # Set after edges defined
        )
        
        self.nodes = [
            "Asgard",      # 0 - Realm of Æsir
            "Vanaheim",    # 1 - Realm of Vanir
            "Alfheim",     # 2 - Realm of Light Elves
            "Midgard",     # 3 - Realm of Humans
            "Jotunheim",   # 4 - Realm of Giants
            "Svartalfheim",# 5 - Realm of Dark Elves
            "Niflheim",    # 6 - Realm of Ice
            "Muspelheim",  # 7 - Realm of Fire
            "Helheim"      # 8 - Realm of the Dead
        ]
        
        # Define connections (World Tree paths)
        self.edges = [
            (0, 3, "Bifrost"),      # Asgard - Midgard
            (3, 4, "Mountain"),     # Midgard - Jotunheim
            (3, 6, "Root"),         # Midgard - Niflheim
            (3, 7, "Root"),         # Midgard - Muspelheim
            (6, 8, "Gjöll"),        # Niflheim - Helheim
            (0, 1, "Path"),         # Asgard - Vanaheim
            (0, 2, "Path"),         # Asgard - Alfheim
            (3, 5, "Root"),         # Midgard - Svartalfheim
            (6, 7, "Ginnungagap"),  # Niflheim - Muspelheim (primordial)
        ]
        
        self.n_edges = len(self.edges)
        
        # Elder Futhark runes as operators
        self.runes = [
            "ᚠ Fehu", "ᚢ Uruz", "ᚦ Thurisaz", "ᚨ Ansuz",
            "ᚱ Raidho", "ᚲ Kenaz", "ᚷ Gebo", "ᚹ Wunjo",
            "ᚺ Hagalaz", "ᚾ Nauthiz", "ᛁ Isa", "ᛃ Jera",
            "ᛇ Eihwaz", "ᛈ Perthro", "ᛉ Algiz", "ᛊ Sowilo",
            "ᛏ Tiwaz", "ᛒ Berkano", "ᛖ Ehwaz", "ᛗ Mannaz",
            "ᛚ Laguz", "ᛜ Ingwaz", "ᛞ Dagaz", "ᛟ Othala"
        ]
        
        self.build_adjacency()


class SefirotEncoder(GraphEncoder):
    """
    Sefirotic Tree: Kabbalistic 10-Node Graph Encoder.
    
    10 Sefirot as nodes, 22 Hebrew letters as edges.
    """
    
    def __init__(self):
        super().__init__(
            name="Etz Chaim (Tree of Life)",
            n_nodes=10,
            n_edges=22
        )
        
        self.nodes = [
            "Keter (Crown)",        # 0
            "Chokmah (Wisdom)",     # 1
            "Binah (Understanding)",# 2
            "Chesed (Mercy)",       # 3
            "Gevurah (Severity)",   # 4
            "Tiferet (Beauty)",     # 5
            "Netzach (Victory)",    # 6
            "Hod (Glory)",          # 7
            "Yesod (Foundation)",   # 8
            "Malkuth (Kingdom)"     # 9
        ]
        
        # 22 paths (Hebrew letters as edge labels)
        self.edges = [
            (0, 1, "א Aleph"), (0, 2, "ב Bet"), (0, 5, "ג Gimel"),
            (1, 2, "ד Dalet"), (1, 3, "ה He"), (1, 5, "ו Vav"),
            (2, 4, "ז Zayin"), (2, 5, "ח Chet"),
            (3, 4, "ט Tet"), (3, 5, "י Yod"), (3, 6, "כ Kaf"),
            (4, 5, "ל Lamed"), (4, 7, "מ Mem"),
            (5, 6, "נ Nun"), (5, 7, "ס Samekh"), (5, 8, "ע Ayin"),
            (6, 7, "פ Pe"), (6, 8, "צ Tsadi"),
            (7, 8, "ק Qof"),
            (8, 9, "ר Resh"),
            (0, 3, "ש Shin"),  # Additional major paths
            (0, 4, "ת Tav")
        ]
        
        # Four Worlds (dimensional cascade)
        self.worlds = {
            "Atziluth": [0],           # Emanation
            "Briah": [1, 2],           # Creation
            "Yetzirah": [3, 4, 5, 6, 7, 8],  # Formation
            "Assiah": [9]              # Action
        }
        
        self.build_adjacency()
    
    def gematria(self, word: str) -> int:
        """Compute gematria value of Hebrew word."""
        values = {
            'א': 1, 'ב': 2, 'ג': 3, 'ד': 4, 'ה': 5,
            'ו': 6, 'ז': 7, 'ח': 8, 'ט': 9, 'י': 10,
            'כ': 20, 'ל': 30, 'מ': 40, 'נ': 50, 'ס': 60,
            'ע': 70, 'פ': 80, 'צ': 90, 'ק': 100, 'ר': 200,
            'ש': 300, 'ת': 400
        }
        return sum(values.get(c, 0) for c in word)


# =============================================================================
# SPECTRAL / HARMONIC ENCODERS
# =============================================================================

@dataclass
class SpectralEncoder:
    """
    Spectral / Harmonic Encoder.
    
    Encodes reality as sum of harmonics (eigenmodes).
    Examples: Pythagorean intervals, Harmony of Spheres
    """
    
    name: str
    fundamental_frequency: float = 1.0
    
    # Harmonic ratios
    ratios: Dict[str, Tuple[int, int]] = field(default_factory=dict)
    
    def frequency_from_ratio(self, ratio: Tuple[int, int]) -> float:
        """Get frequency from integer ratio."""
        return self.fundamental_frequency * ratio[0] / ratio[1]
    
    def cents(self, ratio: Tuple[int, int]) -> float:
        """Convert ratio to cents (1200 cents = octave)."""
        return 1200 * np.log2(ratio[0] / ratio[1])
    
    def consonance_score(self, ratio: Tuple[int, int]) -> float:
        """
        Estimate consonance from ratio simplicity.
        
        Lower product of numerator × denominator = more consonant.
        """
        product = ratio[0] * ratio[1]
        return 1.0 / np.log(product + 1)


class PythagoreanEncoder(SpectralEncoder):
    """
    Pythagorean Spectral Encoder.
    
    Based on Tetraktys and harmonic ratios.
    """
    
    def __init__(self):
        super().__init__(
            name="Pythagorean Harmonics",
            fundamental_frequency=256.0  # C4 approximation
        )
        
        # Perfect intervals
        self.ratios = {
            "unison": (1, 1),
            "octave": (2, 1),
            "fifth": (3, 2),
            "fourth": (4, 3),
            "major_third": (5, 4),
            "minor_third": (6, 5),
            "major_second": (9, 8),
            "minor_second": (16, 15)
        }
        
        # Tetraktys: 1 + 2 + 3 + 4 = 10
        self.tetraktys = [1, 2, 3, 4]
        self.tetraktys_sum = 10
    
    def harmony_of_spheres(self) -> Dict[str, float]:
        """
        Generate planetary frequencies (Harmony of Spheres).
        
        Based on orbital period ratios.
        """
        # Simplified orbital ratios (Earth = 1)
        orbital_ratios = {
            "Mercury": 0.24,
            "Venus": 0.62,
            "Earth": 1.0,
            "Mars": 1.88,
            "Jupiter": 11.86,
            "Saturn": 29.46
        }
        
        return {
            planet: self.fundamental_frequency / ratio
            for planet, ratio in orbital_ratios.items()
        }
    
    def generate_scale(self, n_steps: int = 7) -> List[float]:
        """Generate Pythagorean scale by stacking fifths."""
        frequencies = [self.fundamental_frequency]
        current = self.fundamental_frequency
        
        for _ in range(n_steps - 1):
            # Go up a fifth
            current = current * 3 / 2
            # Reduce to within octave
            while current >= self.fundamental_frequency * 2:
                current /= 2
            frequencies.append(current)
        
        return sorted(frequencies)


# =============================================================================
# METROLOGICAL ENCODERS
# =============================================================================

@dataclass
class MetrologicalEncoder:
    """
    Metrological Encoder.
    
    Encodes number systems and measurement standards.
    Examples: Sumerian sexagesimal, Maya vigesimal
    """
    
    name: str
    base: int
    
    # Digit symbols
    digits: List[str] = field(default_factory=list)
    
    def to_base(self, n: int) -> List[int]:
        """Convert integer to base representation."""
        if n == 0:
            return [0]
        
        result = []
        while n > 0:
            result.append(n % self.base)
            n //= self.base
        
        return result[::-1]
    
    def from_base(self, digits: List[int]) -> int:
        """Convert base representation to integer."""
        result = 0
        for digit in digits:
            result = result * self.base + digit
        return result
    
    def format_number(self, n: int) -> str:
        """Format number in this base."""
        base_digits = self.to_base(n)
        if self.digits:
            return ' '.join(self.digits[d] if d < len(self.digits) else str(d) 
                          for d in base_digits)
        return ' '.join(str(d) for d in base_digits)


class SumerianEncoder(MetrologicalEncoder):
    """
    Sumerian Sexagesimal (Base-60) Encoder.
    
    Used for time, angles, and astronomical calculations.
    """
    
    def __init__(self):
        super().__init__(
            name="ŠAR-60 (Sumerian Sexagesimal)",
            base=60
        )
        
        # Key Sumerian number terms
        self.terms = {
            1: "diš",
            10: "u",
            60: "geš",
            600: "geš'u",
            3600: "šar",
            36000: "šar'u",
            216000: "šar-gal"
        }
        
        # Precessional constants
        self.sar = 3600
        self.ner = 600
        self.great_year = 25920  # Years for precession


class MayaEncoder(MetrologicalEncoder):
    """
    Maya Vigesimal (Base-20) Encoder.
    
    With modified base for Long Count (18 × 20 = 360).
    """
    
    def __init__(self):
        super().__init__(
            name="Maya Vigesimal",
            base=20
        )
        
        # Bar-and-dot representation
        self.digits = ["??", "??", "??", "??", "??",  # 0-4
                      "??", "??", "??", "??", "??",  # 5-9
                      "??", "??", "??", "??", "??",  # 10-14
                      "??", "??", "??", "??", "??"]  # 15-19
        
        # Calendar cycles
        self.tzolkin = 260  # 13 × 20
        self.haab = 365     # 18 × 20 + 5
        self.calendar_round = 52 * 365  # LCM(260, 365) = 18980 days
        self.long_count_cycle = 5125 * 365  # ~5125 years
    
    def long_count_to_days(self, baktun: int, katun: int, 
                          tun: int, uinal: int, kin: int) -> int:
        """Convert Long Count date to day number."""
        return (baktun * 144000 + 
                katun * 7200 + 
                tun * 360 + 
                uinal * 20 + 
                kin)


# =============================================================================
# TRANSITION / REPAIR ENCODERS
# =============================================================================

@dataclass
class TransitionEncoder:
    """
    Transition / Repair Encoder.
    
    Encodes state transitions and error correction protocols.
    Examples: Egyptian Duat, Tibetan Bardo
    """
    
    name: str
    n_stages: int
    
    # Stages with conditions
    stages: List[Dict[str, Any]] = field(default_factory=list)
    
    # Transition matrix
    _transition_matrix: Optional[np.ndarray] = None
    
    def build_transition_matrix(self) -> np.ndarray:
        """Build Markov transition matrix."""
        n = self.n_stages + 1  # +1 for absorbing states
        matrix = np.zeros((n, n))
        
        for i, stage in enumerate(self.stages):
            success_prob = stage.get("success_prob", 0.5)
            
            if i < self.n_stages - 1:
                matrix[i, i + 1] = success_prob  # Progress
                matrix[i, 0] = 1 - success_prob  # Reset/fail
            else:
                matrix[i, i] = success_prob      # Absorbing (success)
                matrix[i, 0] = 1 - success_prob  # Reset
        
        # Normalize rows
        for i in range(n):
            row_sum = np.sum(matrix[i])
            if row_sum > 0:
                matrix[i] /= row_sum
        
        self._transition_matrix = matrix
        return matrix
    
    def simulate_passage(self, n_steps: int = 100) -> List[int]:
        """Simulate passage through stages."""
        if self._transition_matrix is None:
            self.build_transition_matrix()
        
        state = 0
        history = [state]
        
        for _ in range(n_steps):
            probs = self._transition_matrix[state]
            state = np.random.choice(len(probs), p=probs)
            history.append(state)
            
            if state == self.n_stages - 1:  # Reached end
                break
        
        return history


class BardoEncoder(TransitionEncoder):
    """
    Tibetan Bardo Transition Encoder.
    
    49-day intermediate state with 7 × 7 structure.
    """
    
    def __init__(self):
        super().__init__(
            name="Bardo Thödol",
            n_stages=49
        )
        
        # 7 weeks of 7 days
        self.weeks = 7
        self.days_per_week = 7
        
        # Build stages
        self.stages = []
        
        # Peaceful deities (days 1-7)
        for day in range(7):
            self.stages.append({
                "name": f"Peaceful Deity Day {day + 1}",
                "week": 1,
                "deity_type": "peaceful",
                "success_prob": 0.9 - day * 0.05  # Decreasing
            })
        
        # Wrathful deities (days 8-14)
        for day in range(7):
            self.stages.append({
                "name": f"Wrathful Deity Day {day + 8}",
                "week": 2,
                "deity_type": "wrathful",
                "success_prob": 0.7 - day * 0.05
            })
        
        # Remaining weeks (rebirth attractions)
        for week in range(3, 8):
            for day in range(7):
                self.stages.append({
                    "name": f"Week {week} Day {day + 1}",
                    "week": week,
                    "deity_type": "none",
                    "success_prob": 0.5
                })
        
        # Absorbing states
        self.liberation_state = "Liberation"
        self.rebirth_realms = [
            "Deva", "Asura", "Human", 
            "Animal", "Preta", "Naraka"
        ]


class DuatEncoder(TransitionEncoder):
    """
    Egyptian Duat (Underworld) Transition Encoder.
    
    12 Hours of the Night with gates and guardians.
    """
    
    def __init__(self):
        super().__init__(
            name="Duat Navigation",
            n_stages=12
        )
        
        # 12 Hours of the Night
        self.stages = []
        
        for hour in range(12):
            self.stages.append({
                "name": f"Hour {hour + 1}",
                "gate": f"Gate {hour + 1}",
                "guardian": f"Guardian of Hour {hour + 1}",
                "spell_required": f"Spell {hour + 1}",
                "success_prob": 0.8 if hour < 6 else 0.6
            })
        
        # Key locations
        self.locations = {
            5: "Lake of Fire",
            6: "Judgment Hall (Weighing of Heart)",
            11: "Field of Reeds"
        }
        
        # 42 Negative Confessions
        self.n_confessions = 42


# =============================================================================
# ENCODER FACTORY
# =============================================================================

class EncoderFactory:
    """Factory for creating encoders by type and culture."""
    
    @staticmethod
    def create_binary(culture: str) -> BinaryEncoder:
        """Create binary encoder for culture."""
        encoders = {
            "ifa": IfaEncoder(),
            "iching": IChingEncoder(),
        }
        return encoders.get(culture.lower(), BinaryEncoder("Generic", 8))
    
    @staticmethod
    def create_graph(culture: str) -> GraphEncoder:
        """Create graph encoder for culture."""
        encoders = {
            "norse": YggdrasilEncoder(),
            "kabbalah": SefirotEncoder(),
        }
        return encoders.get(culture.lower(), GraphEncoder("Generic", 10, 15))
    
    @staticmethod
    def create_spectral(culture: str) -> SpectralEncoder:
        """Create spectral encoder for culture."""
        encoders = {
            "pythagorean": PythagoreanEncoder(),
        }
        return encoders.get(culture.lower(), SpectralEncoder("Generic"))
    
    @staticmethod
    def create_metrological(culture: str) -> MetrologicalEncoder:
        """Create metrological encoder for culture."""
        encoders = {
            "sumerian": SumerianEncoder(),
            "maya": MayaEncoder(),
        }
        return encoders.get(culture.lower(), MetrologicalEncoder("Generic", 10))
    
    @staticmethod
    def create_transition(culture: str) -> TransitionEncoder:
        """Create transition encoder for culture."""
        encoders = {
            "tibetan": BardoEncoder(),
            "egyptian": DuatEncoder(),
        }
        return encoders.get(culture.lower(), TransitionEncoder("Generic", 12))


# =============================================================================
# VALIDATION
# =============================================================================

def validate_encoders() -> bool:
    """Validate HBAS encoders module."""
    
    # Test Binary Encoders
    ifa = IfaEncoder()
    assert ifa.n_states == 256
    
    binary = ifa.state_to_binary(42)
    back = ifa.binary_to_state(binary)
    assert back == 42
    
    dist = ifa.hamming_distance(0, 255)
    assert dist == 8  # All bits differ
    
    neighbors = ifa.neighbors(0)
    assert len(neighbors) == 8
    
    left, right = ifa.decompose_to_principals(128)
    principals = ifa.get_principal_odu(0), ifa.get_principal_odu(8)
    
    iching = IChingEncoder()
    assert iching.n_states == 64
    lower, upper = iching.decompose_to_trigrams(0)
    
    # Test Graph Encoders
    yggdrasil = YggdrasilEncoder()
    assert yggdrasil.n_nodes == 9
    assert len(yggdrasil.runes) == 24
    
    path = yggdrasil.shortest_path(0, 8)  # Asgard to Helheim
    assert len(path) > 0
    
    sefirot = SefirotEncoder()
    assert sefirot.n_nodes == 10
    
    gematria = sefirot.gematria("אב")  # Aleph + Bet = 1 + 2 = 3
    assert gematria == 3
    
    # Test Spectral Encoders
    pythag = PythagoreanEncoder()
    
    fifth = pythag.frequency_from_ratio((3, 2))
    assert fifth == pythag.fundamental_frequency * 1.5
    
    consonance = pythag.consonance_score((2, 1))
    assert consonance > pythag.consonance_score((16, 15))
    
    scale = pythag.generate_scale(7)
    assert len(scale) == 7
    
    # Test Metrological Encoders
    sumerian = SumerianEncoder()
    assert sumerian.base == 60
    
    base_rep = sumerian.to_base(3661)  # 1 hour, 1 minute, 1 second
    assert sumerian.from_base(base_rep) == 3661
    
    maya = MayaEncoder()
    assert maya.base == 20
    
    days = maya.long_count_to_days(13, 0, 0, 0, 0)
    assert days == 13 * 144000
    
    # Test Transition Encoders
    bardo = BardoEncoder()
    assert bardo.n_stages == 49
    assert bardo.weeks == 7
    
    matrix = bardo.build_transition_matrix()
    assert matrix.shape[0] == 50  # 49 + 1
    
    duat = DuatEncoder()
    assert duat.n_stages == 12
    assert duat.n_confessions == 42
    
    # Test Factory
    ifa2 = EncoderFactory.create_binary("ifa")
    assert isinstance(ifa2, IfaEncoder)
    
    ygg2 = EncoderFactory.create_graph("norse")
    assert isinstance(ygg2, YggdrasilEncoder)
    
    return True


if __name__ == "__main__":
    print("Validating HBAS Encoders Module...")
    assert validate_encoders()
    print("✓ HBAS Encoders Module validated")
