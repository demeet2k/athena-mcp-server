"""
ATHENA OS - IFÁ KERNEL: HYPERCUBE MODULE
========================================
The Q₈ Boolean Hypercube - 256 Odù State Space

ỌPẸ́-256: THE IFÁ COMPUTATIONAL ONTOLOGY

THE STATE SPACE:
    Q₈ = {0, 1}⁸ = Boolean hypercube with 256 vertices
    
    Each vertex is an Odù - a fundamental state of reality
    
    |Ψ(t)⟩ = Σₖ cₖ(t)|Odù_k⟩, k ∈ {1, 2, ..., 256}

STRUCTURE:
    - 256 vertices (Odù states)
    - 1024 edges (single bit-flip transitions)
    - 16 × 16 tensor decomposition (Principal × Secondary)
    - Bipartite: 128 even-parity + 128 odd-parity

THE 16 PRINCIPAL MEJI:
    The foundational archetypes from which all 256 derive:
    Ogbè, Ọ̀yẹ̀kú, Ìwòrì, Odí, Ìrosùn, Ọ̀wọ́nrín, Ọ̀bàrà, Ọ̀kànràn,
    Ògúndá, Ọ̀sá, Ìká, Òtúrúpọ̀n, Òtúrá, Ìrẹ̀tẹ̀, Ọ̀sẹ́, Òfún

BINARY REPRESENTATION:
    Each Odù is an 8-bit binary number
    Right leg (bits 0-3) = Least significant nibble
    Left leg (bits 4-7) = Most significant nibble
    
    Odù_index = (Left_leg << 4) | Right_leg

SOURCES:
    - Traditional Ifá corpus
    - HBAS-Ω Protocol documentation
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Iterator
from enum import Enum, IntEnum
import numpy as np


# =============================================================================
# THE 16 PRINCIPAL MEJI
# =============================================================================

class PrincipalOdu(IntEnum):
    """
    The 16 Principal Meji - foundational archetypes.
    
    Traditional Ifá hierarchy ordering.
    Each has a unique 4-bit pattern.
    """
    
    OGBE = 0       # ||||  (1111) - Pure Light/Expansion
    OYEKU = 1      # ::::  (0000) - Pure Darkness/Contraction
    IWORI = 2      # ::||  (0110) - Inversion/Transformation
    ODI = 3        # ||::  (1001) - Closure/Protection
    IROSUN = 4     # :|:|  (0101) - Vision/Revelation
    OWONRIN = 5    # |:|:  (1010) - Chaos/Creativity
    OBARA = 6      # |:::  (1000) - Wealth/Abundance
    OKANRAN = 7    # :::|  (0111) - Conflict/Force
    OGUNDA = 8     # |||:  (1110) - Clearing/Iron
    OSA = 9        # :::|  (0001) - Loss/Sacrifice
    IKA = 10       # ::|:  (0100) - Binding/Oath
    OTURUPON = 11  # |:||  (1011) - Disease/Healing
    OTURA = 12     # ::||  (0010) - Mystery/Divination
    IRETE = 13     # ||:|  (1101) - Pressing/Urgency
    OSE = 14       # |:::  (1000) - Fortune/Eros
    OFUN = 15      # :||:  (0010) - Death/Rebirth


# Traditional binary patterns for each Principal Meji
MEJI_PATTERNS: Dict[PrincipalOdu, int] = {
    PrincipalOdu.OGBE: 0b1111,      # All open
    PrincipalOdu.OYEKU: 0b0000,     # All closed
    PrincipalOdu.IWORI: 0b0110,     
    PrincipalOdu.ODI: 0b1001,
    PrincipalOdu.IROSUN: 0b0101,
    PrincipalOdu.OWONRIN: 0b1010,
    PrincipalOdu.OBARA: 0b1000,
    PrincipalOdu.OKANRAN: 0b0111,
    PrincipalOdu.OGUNDA: 0b1110,
    PrincipalOdu.OSA: 0b0001,
    PrincipalOdu.IKA: 0b0100,
    PrincipalOdu.OTURUPON: 0b1011,
    PrincipalOdu.OTURA: 0b0010,
    PrincipalOdu.IRETE: 0b1101,
    PrincipalOdu.OSE: 0b1100,
    PrincipalOdu.OFUN: 0b0011,
}

# Reverse lookup
PATTERN_TO_MEJI: Dict[int, PrincipalOdu] = {v: k for k, v in MEJI_PATTERNS.items()}


# =============================================================================
# ODÙ STATE
# =============================================================================

@dataclass
class Odu:
    """
    A single Odù - vertex in the Q₈ hypercube.
    
    Properties:
    - index: 0-255 (8-bit address)
    - binary: 8-bit representation
    - right_leg: Lower nibble (bits 0-3)
    - left_leg: Upper nibble (bits 4-7)
    - parity: Even or odd Hamming weight
    """
    
    index: int
    
    # Metadata
    name: str = ""
    ese: List[str] = field(default_factory=list)  # Verses
    taboos: List[str] = field(default_factory=list)
    prescriptions: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if not 0 <= self.index < 256:
            raise ValueError(f"Odù index must be 0-255, got {self.index}")
        
        if not self.name:
            self.name = self._generate_name()
    
    @property
    def binary(self) -> str:
        """8-bit binary representation."""
        return format(self.index, '08b')
    
    @property
    def right_leg(self) -> int:
        """Lower nibble (bits 0-3)."""
        return self.index & 0x0F
    
    @property
    def left_leg(self) -> int:
        """Upper nibble (bits 4-7)."""
        return (self.index >> 4) & 0x0F
    
    @property
    def hamming_weight(self) -> int:
        """Number of 1-bits."""
        return bin(self.index).count('1')
    
    @property
    def parity(self) -> str:
        """Even or odd parity."""
        return "even" if self.hamming_weight % 2 == 0 else "odd"
    
    @property
    def is_meji(self) -> bool:
        """Check if this is a Meji (doubled pattern)."""
        return self.right_leg == self.left_leg
    
    def _generate_name(self) -> str:
        """Generate traditional name from pattern."""
        right = PATTERN_TO_MEJI.get(self.right_leg, PrincipalOdu.OGBE)
        left = PATTERN_TO_MEJI.get(self.left_leg, PrincipalOdu.OGBE)
        
        right_name = right.name.capitalize()
        left_name = left.name.capitalize()
        
        if self.is_meji:
            return f"{right_name} Meji"
        else:
            return f"{right_name}-{left_name}"
    
    def to_vector(self) -> np.ndarray:
        """Convert to 8-dimensional binary vector."""
        return np.array([int(b) for b in self.binary], dtype=np.float64)
    
    def to_state_vector(self) -> np.ndarray:
        """Convert to 256-dimensional basis state vector."""
        vec = np.zeros(256)
        vec[self.index] = 1.0
        return vec
    
    def hamming_distance(self, other: Odu) -> int:
        """Calculate Hamming distance to another Odù."""
        return bin(self.index ^ other.index).count('1')
    
    def neighbors(self) -> List[int]:
        """Get indices of adjacent vertices (single bit-flip)."""
        return [self.index ^ (1 << i) for i in range(8)]
    
    def visual_pattern(self) -> str:
        """Traditional visual representation."""
        lines = []
        for i in range(4):
            right_bit = (self.right_leg >> (3 - i)) & 1
            left_bit = (self.left_leg >> (3 - i)) & 1
            
            right_sym = "|" if right_bit else ":"
            left_sym = "|" if left_bit else ":"
            
            lines.append(f"  {left_sym}   {right_sym}")
        
        return "\n".join(lines)


# =============================================================================
# Q₈ HYPERCUBE
# =============================================================================

class Q8Hypercube:
    """
    The Q₈ Boolean Hypercube - complete 256-state address space.
    
    Graph properties:
    - |V| = 256 vertices
    - |E| = 1024 edges (8 × 256 / 2)
    - Diameter = 8 (max Hamming distance)
    - Regular: degree 8 at every vertex
    - Bipartite: even/odd parity classes
    """
    
    def __init__(self):
        # Create all 256 Odù
        self.vertices: List[Odu] = [Odu(i) for i in range(256)]
        
        # Adjacency structure (edges are implicit from bit-flips)
        self._adjacency: Optional[np.ndarray] = None
        
        # Initialize Meji (the 16 principal doubled patterns)
        self.meji: List[Odu] = [
            self.get_odu(MEJI_PATTERNS[p] * 17)  # Pattern duplicated: XXXX XXXX
            for p in PrincipalOdu
        ]
        
        # Parity classes
        self.even_parity: List[Odu] = [o for o in self.vertices if o.parity == "even"]
        self.odd_parity: List[Odu] = [o for o in self.vertices if o.parity == "odd"]
    
    def get_odu(self, index: int) -> Odu:
        """Get Odù by index."""
        return self.vertices[index]
    
    def get_odu_by_pattern(self, right_leg: int, left_leg: int) -> Odu:
        """Get Odù by leg patterns."""
        index = (left_leg << 4) | right_leg
        return self.vertices[index]
    
    def get_meji(self, principal: PrincipalOdu) -> Odu:
        """Get a principal Meji."""
        pattern = MEJI_PATTERNS[principal]
        index = pattern * 17  # XXXX duplicated to XXXX XXXX
        return self.vertices[index]
    
    @property
    def adjacency_matrix(self) -> np.ndarray:
        """Get the 256×256 adjacency matrix."""
        if self._adjacency is None:
            self._adjacency = np.zeros((256, 256), dtype=np.int8)
            for i in range(256):
                for neighbor in self.vertices[i].neighbors():
                    self._adjacency[i, neighbor] = 1
        return self._adjacency
    
    def get_neighbors(self, index: int) -> List[Odu]:
        """Get neighboring Odù (Hamming distance 1)."""
        return [self.vertices[n] for n in self.vertices[index].neighbors()]
    
    def path_between(self, start: int, end: int) -> List[int]:
        """
        Find shortest path between two Odù.
        
        In a hypercube, the shortest path follows the differing bits.
        """
        diff = start ^ end
        path = [start]
        current = start
        
        for i in range(8):
            if diff & (1 << i):
                current ^= (1 << i)
                path.append(current)
        
        return path
    
    def sphere(self, center: int, radius: int) -> List[Odu]:
        """Get all Odù within Hamming distance radius of center."""
        return [
            self.vertices[i] 
            for i in range(256) 
            if self.vertices[center].hamming_distance(self.vertices[i]) <= radius
        ]
    
    def antipode(self, index: int) -> Odu:
        """Get the antipodal Odù (all bits flipped)."""
        return self.vertices[index ^ 0xFF]
    
    def complement(self, index: int) -> Odu:
        """Alias for antipode."""
        return self.antipode(index)
    
    def statistics(self) -> Dict[str, Any]:
        """Get hypercube statistics."""
        return {
            "vertices": 256,
            "edges": 1024,
            "diameter": 8,
            "degree": 8,
            "meji_count": 16,
            "even_parity_count": len(self.even_parity),
            "odd_parity_count": len(self.odd_parity)
        }


# =============================================================================
# STATE SUPERPOSITION
# =============================================================================

@dataclass
class OduSuperposition:
    """
    A superposition of Odù states.
    
    |Ψ⟩ = Σₖ cₖ|Odù_k⟩
    
    where Σ|cₖ|² = 1 (normalization)
    """
    
    amplitudes: np.ndarray  # 256-dimensional complex vector
    
    def __post_init__(self):
        if len(self.amplitudes) != 256:
            raise ValueError("Superposition must have 256 amplitudes")
        
        # Normalize
        norm = np.sqrt(np.sum(np.abs(self.amplitudes) ** 2))
        if norm > 0:
            self.amplitudes = self.amplitudes / norm
    
    @classmethod
    def from_odu(cls, odu: Odu) -> OduSuperposition:
        """Create pure state from single Odù."""
        amps = np.zeros(256, dtype=np.complex128)
        amps[odu.index] = 1.0
        return cls(amps)
    
    @classmethod
    def uniform(cls) -> OduSuperposition:
        """Create uniform superposition over all Odù."""
        amps = np.ones(256, dtype=np.complex128) / 16  # 1/√256 = 1/16
        return cls(amps)
    
    def probability(self, index: int) -> float:
        """Get probability of measuring Odù at index."""
        return float(np.abs(self.amplitudes[index]) ** 2)
    
    def probabilities(self) -> np.ndarray:
        """Get all probabilities."""
        return np.abs(self.amplitudes) ** 2
    
    def measure(self) -> int:
        """
        Collapse superposition (measurement).
        
        Returns index of measured Odù.
        """
        probs = self.probabilities()
        return int(np.random.choice(256, p=probs))
    
    def entropy(self) -> float:
        """Calculate von Neumann entropy."""
        probs = self.probabilities()
        probs = probs[probs > 0]  # Avoid log(0)
        return float(-np.sum(probs * np.log2(probs)))
    
    def dominant_odu(self) -> int:
        """Get index of highest-probability Odù."""
        return int(np.argmax(self.probabilities()))
    
    def top_k(self, k: int = 5) -> List[Tuple[int, float]]:
        """Get top k highest-probability Odù."""
        probs = self.probabilities()
        indices = np.argsort(probs)[::-1][:k]
        return [(int(i), float(probs[i])) for i in indices]


# =============================================================================
# IWA (CHARACTER TENSOR)
# =============================================================================

@dataclass
class IwaTensor:
    """
    The Ìwà (Character) Tensor.
    
    Accumulates non-commutative action history.
    
    Û_Ìwà(t) = Πᵢ Ûᵢ (product of action operators)
    
    The final state: |ψ(t)⟩ = Û_Ìwà(t)|Orí⟩
    """
    
    # Action history (list of operator indices)
    action_history: List[int] = field(default_factory=list)
    
    # Accumulated transformation matrix
    transformation: np.ndarray = field(
        default_factory=lambda: np.eye(256, dtype=np.complex128)
    )
    
    # Coherence measure
    coherence: float = 1.0
    
    def apply_action(self, operator: np.ndarray, action_id: int = 0) -> None:
        """
        Apply an action (operator) to the character tensor.
        
        Non-commutative: order matters!
        """
        self.action_history.append(action_id)
        self.transformation = operator @ self.transformation
        
        # Update coherence (trace of transformation)
        self.coherence = float(np.abs(np.trace(self.transformation)) / 256)
    
    def get_current_state(self, initial_ori: np.ndarray) -> np.ndarray:
        """
        Get current state from initial Orí (destiny).
        
        |ψ(t)⟩ = Û_Ìwà(t)|Orí⟩
        """
        return self.transformation @ initial_ori
    
    def action_count(self) -> int:
        """Count total actions taken."""
        return len(self.action_history)


# =============================================================================
# VALIDATION
# =============================================================================

def validate_hypercube() -> bool:
    """Validate hypercube module."""
    
    # Test Odù creation
    odu = Odu(0)
    assert odu.index == 0
    assert odu.binary == "00000000"
    assert odu.hamming_weight == 0
    assert odu.parity == "even"
    
    odu_255 = Odu(255)
    assert odu_255.index == 255
    assert odu_255.hamming_weight == 8
    assert odu_255.parity == "even"
    
    # Test legs
    odu_test = Odu(0xAB)  # 10101011
    assert odu_test.right_leg == 0x0B
    assert odu_test.left_leg == 0x0A
    
    # Test hypercube
    q8 = Q8Hypercube()
    assert len(q8.vertices) == 256
    assert len(q8.meji) == 16
    assert len(q8.even_parity) == 128
    assert len(q8.odd_parity) == 128
    
    # Test neighbors
    neighbors = q8.get_neighbors(0)
    assert len(neighbors) == 8
    assert all(odu.hamming_weight == 1 for odu in neighbors)
    
    # Test path
    path = q8.path_between(0, 255)
    assert path[0] == 0
    assert path[-1] == 255
    assert len(path) == 9  # 8 flips + start
    
    # Test antipode
    antipode = q8.antipode(0)
    assert antipode.index == 255
    
    # Test superposition
    sup = OduSuperposition.uniform()
    assert abs(sup.entropy() - 8.0) < 0.01  # log2(256) = 8
    
    measured = sup.measure()
    assert 0 <= measured < 256
    
    pure = OduSuperposition.from_odu(Odu(42))
    assert pure.probability(42) == 1.0
    assert pure.dominant_odu() == 42
    
    # Test Ìwà tensor
    iwa = IwaTensor()
    assert iwa.coherence == 1.0
    assert iwa.action_count() == 0
    
    return True


if __name__ == "__main__":
    print("Validating Hypercube Module...")
    assert validate_hypercube()
    print("✓ Hypercube Module validated")
    
    # Demo
    print("\n--- Q₈ Hypercube Demo ---")
    q8 = Q8Hypercube()
    
    stats = q8.statistics()
    print(f"\nHypercube Statistics:")
    for key, val in stats.items():
        print(f"  {key}: {val}")
    
    print("\n16 Principal Meji:")
    for meji in q8.meji[:8]:
        print(f"  {meji.name}: {meji.binary}")
    
    # Show one Odù pattern
    odu = q8.get_meji(PrincipalOdu.OGBE)
    print(f"\n{odu.name} Pattern:")
    print(odu.visual_pattern())
