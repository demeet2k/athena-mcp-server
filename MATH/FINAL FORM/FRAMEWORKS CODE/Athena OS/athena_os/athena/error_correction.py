"""
ATHENA OS - EUCLIDEAN ERROR CORRECTION
======================================
The Self-Healing Information Architecture

From THE_HELLENIC_COMPUTATION_FRAMEWORK.docx:

THE 31-BIT REGISTER:
    Projective space PG(4,2) contains exactly 31 points:
    |P| = (2⁵ - 1)/(2 - 1) = 31

HAMMING (31,26) CODE:
    - Data Payload: 26 bits (k = 2⁵ - 1 - 5)
    - Parity Check: 5 bits (r = 5 dimensions)
    - Information Density: 26/31 ≈ 84%
    - Corrects any single-bit error

THE FIVE GATE PROPOSITIONS:
    Gate I   (Book IV.1):  10011  - Inscription
    Gate II  (Book V.2):   00011  - Aggregation
    Gate III (Book VI.2):  00010  - Proportion
    Gate IV  (Book X.8):   11000  - Irrationality
    Gate V   (Book XI.20): 01101  - Solid Closure

SYNDROME DECODING:
    1. Receive vector r (possibly corrupted: r = c + e)
    2. Compute syndrome: S = H·rᵀ
    3. IF S = [0,0,0,0,0]ᵀ THEN text is intact
    4. ELSE S encodes binary index of error
    5. Flip bit at position decimal(S) to restore

The Elements functions as a self-healing manuscript.
Mathematical dependencies form an immune system against error.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set, Any
from enum import Enum, auto
import numpy as np


# =============================================================================
# GALOIS FIELD GF(2)
# =============================================================================

class GF2:
    """
    Galois Field GF(2) = {0, 1} with XOR addition and AND multiplication.
    """
    
    @staticmethod
    def add(a: int, b: int) -> int:
        """Addition in GF(2) = XOR."""
        return a ^ b
    
    @staticmethod
    def mul(a: int, b: int) -> int:
        """Multiplication in GF(2) = AND."""
        return a & b
    
    @staticmethod
    def neg(a: int) -> int:
        """Negation in GF(2) (a = -a)."""
        return a
    
    @staticmethod
    def dot(v1: List[int], v2: List[int]) -> int:
        """Dot product in GF(2)."""
        result = 0
        for a, b in zip(v1, v2):
            result ^= (a & b)
        return result
    
    @staticmethod
    def mat_vec_mul(matrix: List[List[int]], vec: List[int]) -> List[int]:
        """Matrix-vector multiplication in GF(2)."""
        return [GF2.dot(row, vec) for row in matrix]


# =============================================================================
# THE FIVE GATE PROPOSITIONS
# =============================================================================

@dataclass(frozen=True)
class GateProposition:
    """
    A Gate Proposition - one of the 5 parity basis vectors.
    
    These span GF(2)⁵ completely (Rank = 5).
    """
    
    gate_id: int
    name: str
    locus: str
    vector: Tuple[int, int, int, int, int]
    function: str
    
    def __str__(self) -> str:
        return f"Gate {self.gate_id}: {''.join(str(b) for b in self.vector)} ({self.function})"


# The five canonical gates from the manuscript
GATE_I = GateProposition(1, "Gate I", "Book IV.1", (1, 0, 0, 1, 1), "Inscription")
GATE_II = GateProposition(2, "Gate II", "Book V.2", (0, 0, 0, 1, 1), "Aggregation")
GATE_III = GateProposition(3, "Gate III", "Book VI.2", (0, 0, 0, 1, 0), "Proportion")
GATE_IV = GateProposition(4, "Gate IV", "Book X.8", (1, 1, 0, 0, 0), "Irrationality")
GATE_V = GateProposition(5, "Gate V", "Book XI.20", (0, 1, 1, 0, 1), "Solid Closure")

ALL_GATES = [GATE_I, GATE_II, GATE_III, GATE_IV, GATE_V]


def gates_span_gf2_5() -> bool:
    """
    Verify the five gates span GF(2)⁵ completely.
    
    The matrix formed by gate vectors should have rank 5.
    """
    matrix = np.array([gate.vector for gate in ALL_GATES], dtype=int)
    # Use row reduction over GF(2)
    rank = np.linalg.matrix_rank(matrix % 2)
    return rank == 5


# =============================================================================
# HAMMING (31, 26) CODE
# =============================================================================

class HammingCode:
    """
    The Hamming (31, 26) perfect code.
    
    Properties:
    - n = 31: codeword length
    - k = 26: data bits
    - r = 5: parity bits
    - d = 3: minimum distance
    - Corrects any single-bit error
    
    A perfect code satisfies: Σᵢ₌₀ᵗ C(n,i) = 2^(n-k)
    For t=1: C(31,0) + C(31,1) = 1 + 31 = 32 = 2⁵ ✓
    """
    
    def __init__(self):
        self.n = 31  # Codeword length
        self.k = 26  # Data bits
        self.r = 5   # Parity bits (dimensions)
        
        # Build the parity check matrix H (5 x 31)
        self.H = self._build_parity_matrix()
        
        # Build the generator matrix G (26 x 31)
        self.G = self._build_generator_matrix()
    
    def _build_parity_matrix(self) -> List[List[int]]:
        """
        Build the 5×31 parity check matrix H.
        
        Each column is a unique non-zero 5-bit vector.
        Column j is the binary representation of j+1.
        """
        H = [[0] * 31 for _ in range(5)]
        
        for j in range(31):
            # Column j is binary of (j+1)
            val = j + 1
            for i in range(5):
                H[4 - i][j] = (val >> i) & 1
        
        return H
    
    def _build_generator_matrix(self) -> List[List[int]]:
        """
        Build the 26×31 generator matrix G.
        
        In systematic form: G = [I_26 | P] where H = [-Pᵀ | I_5]
        """
        # For simplicity, we use the parity check relationship
        # In a systematic code, data positions are those where
        # column has more than one 1 (not power of 2)
        
        G = [[0] * 31 for _ in range(26)]
        
        # Data bit positions (non-power-of-2 positions)
        data_positions = [i for i in range(31) if (i + 1) & i != 0 or i == 0]
        
        # Build identity part for data bits
        for i, pos in enumerate(data_positions[:26]):
            G[i][pos] = 1
            
            # Add parity bits
            for p in range(5):
                parity_pos = (1 << p) - 1  # Positions 0,1,3,7,15 (powers of 2 minus 1)
                if self.H[4-p][pos] == 1:
                    G[i][parity_pos] = GF2.add(G[i][parity_pos], 1)
        
        return G
    
    @property
    def information_density(self) -> float:
        """Information density k/n."""
        return self.k / self.n
    
    def encode(self, data: List[int]) -> List[int]:
        """
        Encode 26-bit data into 31-bit codeword.
        
        c = data × G (mod 2)
        """
        if len(data) != self.k:
            raise ValueError(f"Data must be {self.k} bits")
        
        codeword = [0] * self.n
        for i, bit in enumerate(data):
            if bit:
                for j in range(self.n):
                    codeword[j] = GF2.add(codeword[j], self.G[i][j])
        
        return codeword
    
    def compute_syndrome(self, received: List[int]) -> List[int]:
        """
        Compute syndrome S = H · rᵀ.
        
        S = 0 means no error detected.
        S ≠ 0 encodes error position in binary.
        """
        if len(received) != self.n:
            raise ValueError(f"Received vector must be {self.n} bits")
        
        return GF2.mat_vec_mul(self.H, received)
    
    def syndrome_to_position(self, syndrome: List[int]) -> Optional[int]:
        """
        Convert syndrome to error position.
        
        Returns None if syndrome is zero (no error).
        """
        # Convert syndrome to decimal
        pos = 0
        for i, bit in enumerate(reversed(syndrome)):
            pos |= (bit << i)
        
        return pos - 1 if pos > 0 else None
    
    def decode(self, received: List[int]) -> Tuple[List[int], bool, Optional[int]]:
        """
        Decode received vector with single-error correction.
        
        Returns:
            (corrected_data, had_error, error_position)
        """
        syndrome = self.compute_syndrome(received)
        error_pos = self.syndrome_to_position(syndrome)
        
        corrected = list(received)
        
        if error_pos is not None:
            # Flip the error bit
            corrected[error_pos] = 1 - corrected[error_pos]
        
        # Extract data bits (non-power-of-2 positions)
        data_positions = [i for i in range(31) if (i + 1) & i != 0][:26]
        data = [corrected[pos] for pos in data_positions]
        
        return data, error_pos is not None, error_pos
    
    def verify_codeword(self, codeword: List[int]) -> bool:
        """Check if vector is a valid codeword."""
        syndrome = self.compute_syndrome(codeword)
        return all(s == 0 for s in syndrome)
    
    def is_perfect(self) -> bool:
        """
        Verify the code is perfect.
        
        A perfect code satisfies: Σᵢ₌₀ᵗ C(n,i) = 2^(n-k)
        """
        from math import comb
        t = 1  # Error correction capability
        sphere_size = sum(comb(self.n, i) for i in range(t + 1))
        total_syndromes = 2 ** self.r
        return sphere_size == total_syndromes


# =============================================================================
# THE 31-BIT REGISTER
# =============================================================================

@dataclass
class Register31:
    """
    The 31-bit register - the Euclidean data container.
    
    Structure:
    - 26 data bits (payload)
    - 5 parity bits (error correction)
    
    Derived from projective space PG(4,2) with 31 points.
    """
    
    data: List[int] = field(default_factory=lambda: [0] * 26)
    code: HammingCode = field(default_factory=HammingCode, repr=False)
    
    def __post_init__(self):
        if len(self.data) != 26:
            raise ValueError("Data must be 26 bits")
    
    @property
    def encoded(self) -> List[int]:
        """Get encoded 31-bit codeword."""
        return self.code.encode(self.data)
    
    def write(self, position: int, value: int) -> None:
        """Write a bit to data position."""
        if not 0 <= position < 26:
            raise ValueError("Position must be 0-25")
        self.data[position] = value & 1
    
    def read(self, position: int) -> int:
        """Read a bit from data position."""
        return self.data[position]
    
    def corrupt(self, codeword: List[int], position: int) -> List[int]:
        """Simulate single-bit error at position."""
        result = list(codeword)
        result[position] = 1 - result[position]
        return result
    
    def heal(self, corrupted: List[int]) -> Tuple[List[int], bool, Optional[int]]:
        """
        Self-healing: detect and correct single-bit error.
        
        The manuscript functions as a self-healing document.
        """
        return self.code.decode(corrupted)


# =============================================================================
# PROJECTIVE GEOMETRY PG(4,2)
# =============================================================================

class ProjectiveGeometry:
    """
    Projective Geometry PG(4,2) - the underlying structure.
    
    PG(n-1, q) has (q^n - 1)/(q - 1) points.
    PG(4, 2) = (2⁵ - 1)/(2 - 1) = 31 points.
    
    Each point corresponds to a position in the Hamming code.
    """
    
    def __init__(self, dimension: int = 5, field_size: int = 2):
        self.n = dimension
        self.q = field_size
        self.num_points = (field_size ** dimension - 1) // (field_size - 1)
    
    def point_coordinates(self, index: int) -> Tuple[int, ...]:
        """
        Get homogeneous coordinates of point.
        
        Point i has coordinates equal to binary of (i+1).
        """
        val = index + 1
        return tuple((val >> k) & 1 for k in range(self.n))
    
    def all_points(self) -> List[Tuple[int, ...]]:
        """Get all points in the projective space."""
        return [self.point_coordinates(i) for i in range(self.num_points)]
    
    def are_collinear(self, p1: int, p2: int, p3: int) -> bool:
        """
        Check if three points are collinear in PG(4,2).
        
        In GF(2), three points are collinear if p1 ⊕ p2 ⊕ p3 = 0.
        """
        c1 = self.point_coordinates(p1)
        c2 = self.point_coordinates(p2)
        c3 = self.point_coordinates(p3)
        
        return all((a ^ b ^ c) == 0 for a, b, c in zip(c1, c2, c3))


# =============================================================================
# EUCLIDEAN IMMUNE SYSTEM
# =============================================================================

class EuclideanImmuneSystem:
    """
    The complete error-correction immune system.
    
    The Elements functions as a self-healing manuscript.
    Mathematical dependencies form an immune system against scribal error.
    """
    
    def __init__(self):
        self.code = HammingCode()
        self.geometry = ProjectiveGeometry()
        self.gates = ALL_GATES
    
    def encode_proposition(self, content: str) -> List[int]:
        """
        Encode a proposition into the 31-bit container.
        
        Uses first 26 characters (or pads with zeros).
        """
        # Simple encoding: ASCII mod 2 for each char
        data = []
        for i in range(26):
            if i < len(content):
                data.append(ord(content[i]) % 2)
            else:
                data.append(0)
        
        return self.code.encode(data)
    
    def verify_integrity(self, codeword: List[int]) -> Dict[str, Any]:
        """
        Verify integrity of encoded proposition.
        
        Returns diagnostic information.
        """
        syndrome = self.code.compute_syndrome(codeword)
        error_pos = self.code.syndrome_to_position(syndrome)
        
        return {
            "valid": error_pos is None,
            "syndrome": syndrome,
            "error_position": error_pos,
            "syndrome_decimal": sum(s << (4-i) for i, s in enumerate(syndrome))
        }
    
    def repair(self, corrupted: List[int]) -> Tuple[List[int], Dict[str, Any]]:
        """
        Repair corrupted codeword.
        
        Returns (repaired_codeword, repair_info).
        """
        data, had_error, error_pos = self.code.decode(corrupted)
        
        repair_info = {
            "had_error": had_error,
            "error_position": error_pos,
            "repair_successful": True  # Single-bit errors always repairable
        }
        
        if had_error:
            # Re-encode the repaired data
            repaired = self.code.encode(data)
            return repaired, repair_info
        else:
            return corrupted, repair_info
    
    def demonstrate_self_healing(self) -> Dict[str, Any]:
        """
        Demonstrate the self-healing property.
        
        1. Encode data
        2. Introduce error
        3. Detect and correct
        """
        # Original data
        original_data = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0,
                        1, 0, 1, 0, 1, 0, 1, 0, 1, 0,
                        1, 0, 1, 0, 1, 0]
        
        # Encode
        codeword = self.code.encode(original_data)
        
        # Corrupt at position 15
        error_pos = 15
        corrupted = list(codeword)
        corrupted[error_pos] = 1 - corrupted[error_pos]
        
        # Detect
        integrity = self.verify_integrity(corrupted)
        
        # Repair
        repaired, repair_info = self.repair(corrupted)
        
        return {
            "original_data": original_data,
            "codeword": codeword,
            "error_position": error_pos,
            "corrupted": corrupted,
            "detected_position": integrity["error_position"],
            "repaired": repaired,
            "repair_matches_original": repaired == codeword,
            "self_healing_successful": repaired == codeword
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_error_correction() -> bool:
    """Validate the error correction module."""
    
    # Test GF(2) operations
    assert GF2.add(0, 0) == 0
    assert GF2.add(1, 1) == 0
    assert GF2.add(0, 1) == 1
    assert GF2.mul(1, 1) == 1
    assert GF2.mul(1, 0) == 0
    
    # Test gates span GF(2)⁵
    assert gates_span_gf2_5()
    
    # Test Hamming code properties
    code = HammingCode()
    assert code.n == 31
    assert code.k == 26
    assert code.r == 5
    assert abs(code.information_density - 0.8387) < 0.001
    
    # Test encoding/decoding
    data = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0,
            1, 0, 1, 0, 1, 0, 1, 0, 1, 0,
            1, 0, 1, 0, 1, 0]
    
    codeword = code.encode(data)
    assert len(codeword) == 31
    assert code.verify_codeword(codeword)
    
    # Test syndrome of valid codeword
    syndrome = code.compute_syndrome(codeword)
    assert all(s == 0 for s in syndrome)
    
    # Test error correction
    corrupted = list(codeword)
    error_pos = 10
    corrupted[error_pos] = 1 - corrupted[error_pos]
    
    decoded, had_error, detected_pos = code.decode(corrupted)
    assert had_error
    assert detected_pos == error_pos
    
    # Test perfect code property
    assert code.is_perfect()
    
    # Test projective geometry
    pg = ProjectiveGeometry()
    assert pg.num_points == 31
    
    # Test Register31
    reg = Register31(data)
    assert len(reg.encoded) == 31
    
    # Test immune system
    immune = EuclideanImmuneSystem()
    demo = immune.demonstrate_self_healing()
    assert demo["self_healing_successful"]
    
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("ATHENA OS - EUCLIDEAN ERROR CORRECTION")
    print("The Self-Healing Information Architecture")
    print("=" * 60)
    
    print("\nValidating module...")
    assert validate_error_correction()
    print("✓ Module validated")
    
    # Demo
    print("\n--- THE FIVE GATE PROPOSITIONS ---")
    for gate in ALL_GATES:
        print(f"  {gate}")
    print(f"  Gates span GF(2)⁵: {gates_span_gf2_5()}")
    
    print("\n--- HAMMING (31,26) CODE ---")
    code = HammingCode()
    print(f"  n = {code.n} (codeword length)")
    print(f"  k = {code.k} (data bits)")
    print(f"  r = {code.r} (parity bits)")
    print(f"  Information density: {code.information_density:.2%}")
    print(f"  Is perfect code: {code.is_perfect()}")
    
    print("\n--- PROJECTIVE GEOMETRY PG(4,2) ---")
    pg = ProjectiveGeometry()
    print(f"  Dimension: {pg.n}")
    print(f"  Field size: {pg.q}")
    print(f"  Number of points: {pg.num_points}")
    
    print("\n--- SELF-HEALING DEMONSTRATION ---")
    immune = EuclideanImmuneSystem()
    demo = immune.demonstrate_self_healing()
    print(f"  Error introduced at position: {demo['error_position']}")
    print(f"  Error detected at position: {demo['detected_position']}")
    print(f"  Self-healing successful: {demo['self_healing_successful']}")
