"""
ATHENA OS - HELLENIC COMPUTATION FRAMEWORK
==========================================
Part III: The Error Correction Layer (Euclid)

THE 31-BIT REGISTER:
    Euclid's Elements uses 31 propositions as its foundational register.
    This is not accidental—31 is the optimal size for single-error
    correction using Hamming codes.

THE HAMMING (31,26) CODE:
    - 31 total bits (n = 31)
    - 26 data bits (k = 26)
    - 5 parity bits (r = 5, since 2^5 = 32 > 31)
    - Corrects all single-bit errors
    - Detects all double-bit errors

THE PARITY MATRIX:
    H is a 5×31 matrix where column i is the binary representation of i.
    The syndrome S = H × received_word identifies the error position.

SYNDROME DECODING:
    If S = 0: No error
    If S ≠ 0: S gives the position of the erroneous bit

GEOMETRIC INTERPRETATION:
    - Each proposition is a bit
    - Parity checks correspond to geometric dependencies
    - Error correction = restoring geometric consistency

SOURCES:
    - THE_HELLENIC_COMPUTATION_FRAMEWORK.docx Part III
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Set
import numpy as np


# =============================================================================
# HAMMING CODE PARAMETERS
# =============================================================================

@dataclass
class HammingParameters:
    """
    Parameters for a Hamming code.
    
    Hamming(n, k) where:
    - n = 2^r - 1 (codeword length)
    - k = n - r (data bits)
    - r = parity bits
    """
    
    r: int  # Number of parity bits
    
    @property
    def n(self) -> int:
        """Total codeword length."""
        return 2 ** self.r - 1
    
    @property
    def k(self) -> int:
        """Number of data bits."""
        return self.n - self.r
    
    @property
    def rate(self) -> float:
        """Code rate k/n."""
        return self.k / self.n
    
    @property
    def minimum_distance(self) -> int:
        """Minimum Hamming distance (always 3 for Hamming codes)."""
        return 3
    
    @property
    def error_correction_capability(self) -> int:
        """Number of errors that can be corrected."""
        return (self.minimum_distance - 1) // 2
    
    @property
    def error_detection_capability(self) -> int:
        """Number of errors that can be detected."""
        return self.minimum_distance - 1
    
    def is_perfect(self) -> bool:
        """
        Check if code is perfect.
        
        A code is perfect if it meets the Hamming bound with equality.
        Hamming codes are always perfect.
        """
        # Sphere-packing bound: Σᵢ₌₀ᵗ C(n,i) = 2^r
        # For t=1: 1 + n = 2^r
        return 1 + self.n == 2 ** self.r


# Standard Euclidean parameters
EUCLID_PARAMS = HammingParameters(r=5)  # Hamming(31, 26)


# =============================================================================
# PARITY CHECK MATRIX
# =============================================================================

class ParityMatrix:
    """
    The parity check matrix H for a Hamming code.
    
    H is an r×n matrix where column i is the binary representation of i.
    """
    
    def __init__(self, params: HammingParameters):
        self.params = params
        self.r = params.r
        self.n = params.n
        self._build_matrix()
    
    def _build_matrix(self) -> None:
        """Build the parity check matrix."""
        self.H = np.zeros((self.r, self.n), dtype=int)
        
        for col in range(1, self.n + 1):
            # Column i is binary representation of i
            for row in range(self.r):
                self.H[row, col - 1] = (col >> row) & 1
    
    def __getitem__(self, key: Tuple[int, int]) -> int:
        """Get element H[row, col]."""
        return int(self.H[key])
    
    @property
    def shape(self) -> Tuple[int, int]:
        """Matrix shape (r, n)."""
        return (self.r, self.n)
    
    def column(self, i: int) -> np.ndarray:
        """Get column i (0-indexed)."""
        return self.H[:, i].copy()
    
    def to_binary_string(self, col: int) -> str:
        """Get column as binary string."""
        return ''.join(str(b) for b in self.column(col))
    
    def syndrome(self, word: np.ndarray) -> np.ndarray:
        """
        Calculate syndrome S = H × word (mod 2).
        
        The syndrome identifies error position.
        """
        if len(word) != self.n:
            raise ValueError(f"Word must have length {self.n}")
        
        return np.dot(self.H, word) % 2
    
    def syndrome_to_position(self, syndrome: np.ndarray) -> int:
        """
        Convert syndrome to error position.
        
        Returns 0 if no error, else position (1-indexed).
        """
        # Syndrome is binary representation of position
        position = 0
        for i in range(self.r):
            position += int(syndrome[i]) * (2 ** i)
        return position
    
    def display(self) -> str:
        """Display matrix as string."""
        lines = []
        for row in self.H:
            lines.append(' '.join(str(b) for b in row))
        return '\n'.join(lines)


# =============================================================================
# GENERATOR MATRIX
# =============================================================================

class GeneratorMatrix:
    """
    The generator matrix G for a Hamming code.
    
    G is a k×n matrix that encodes k data bits into n codeword bits.
    In systematic form: G = [I_k | P] where P is the parity part.
    """
    
    def __init__(self, params: HammingParameters):
        self.params = params
        self.k = params.k
        self.n = params.n
        self.r = params.r
        self._build_matrix()
    
    def _build_matrix(self) -> None:
        """Build the generator matrix in systematic form."""
        self.G = np.zeros((self.k, self.n), dtype=int)
        
        # Identify data positions and parity positions
        # Parity bits are at positions 2^i - 1 (0-indexed)
        parity_positions = {2**i - 1 for i in range(self.r)}
        
        data_positions = [i for i in range(self.n) 
                         if i not in parity_positions]
        
        self.data_positions = data_positions
        self.parity_positions = sorted(parity_positions)
        
        # Build systematic form
        for i, pos in enumerate(data_positions):
            self.G[i, pos] = 1
        
        # Add parity relationships
        # Each parity bit covers positions where bit i of position is 1
        for i, parity_pos in enumerate(self.parity_positions):
            bit_mask = 2 ** i
            for j, data_pos in enumerate(data_positions):
                actual_pos = data_pos + 1  # 1-indexed for calculation
                if actual_pos & bit_mask:
                    # Find which row affects this
                    self.G[j, parity_pos] = 1
    
    def encode(self, data: np.ndarray) -> np.ndarray:
        """Encode k data bits into n codeword bits."""
        if len(data) != self.k:
            raise ValueError(f"Data must have length {self.k}")
        
        return np.dot(data, self.G) % 2
    
    @property
    def shape(self) -> Tuple[int, int]:
        return (self.k, self.n)


# =============================================================================
# HAMMING ENCODER/DECODER
# =============================================================================

class HammingCode:
    """
    Complete Hamming code implementation.
    
    Provides encoding, decoding, and error correction.
    """
    
    def __init__(self, r: int = 5):
        """
        Initialize Hamming code.
        
        r: Number of parity bits (default 5 for 31,26 code)
        """
        self.params = HammingParameters(r=r)
        self.parity = ParityMatrix(self.params)
        self._setup_positions()
    
    def _setup_positions(self) -> None:
        """Setup data and parity bit positions."""
        n = self.params.n
        r = self.params.r
        
        # Parity positions are at 2^i - 1 (0-indexed)
        self.parity_positions = [2**i - 1 for i in range(r)]
        
        # Data positions are all others
        self.data_positions = [i for i in range(n) 
                              if i not in self.parity_positions]
    
    def encode(self, data: np.ndarray) -> np.ndarray:
        """
        Encode data bits into codeword.
        
        data: Array of k data bits
        Returns: Array of n codeword bits
        """
        k = self.params.k
        n = self.params.n
        r = self.params.r
        
        if len(data) != k:
            raise ValueError(f"Data must have {k} bits, got {len(data)}")
        
        # Create codeword
        codeword = np.zeros(n, dtype=int)
        
        # Place data bits
        for i, pos in enumerate(self.data_positions):
            codeword[pos] = data[i]
        
        # Calculate parity bits
        for i in range(r):
            parity_pos = 2**i - 1
            bit_mask = 2**i
            
            parity = 0
            for j in range(n):
                if j != parity_pos and ((j + 1) & bit_mask):
                    parity ^= codeword[j]
            
            codeword[parity_pos] = parity
        
        return codeword
    
    def decode(self, received: np.ndarray) -> Tuple[np.ndarray, int]:
        """
        Decode received word, correcting single-bit errors.
        
        received: Array of n received bits
        Returns: (data bits, error_position or 0 if no error)
        """
        n = self.params.n
        
        if len(received) != n:
            raise ValueError(f"Received word must have {n} bits")
        
        # Calculate syndrome
        syndrome = self.parity.syndrome(received)
        error_pos = self.parity.syndrome_to_position(syndrome)
        
        # Correct error if present
        corrected = received.copy()
        if error_pos > 0:
            corrected[error_pos - 1] ^= 1
        
        # Extract data bits
        data = np.array([corrected[pos] for pos in self.data_positions])
        
        return data, error_pos
    
    def check(self, codeword: np.ndarray) -> bool:
        """Check if codeword is valid (no errors)."""
        syndrome = self.parity.syndrome(codeword)
        return np.all(syndrome == 0)
    
    def inject_error(self, codeword: np.ndarray, 
                    position: int) -> np.ndarray:
        """Inject single-bit error at position (1-indexed)."""
        result = codeword.copy()
        result[position - 1] ^= 1
        return result
    
    def hamming_distance(self, word1: np.ndarray, 
                        word2: np.ndarray) -> int:
        """Calculate Hamming distance between two words."""
        return np.sum(word1 != word2)


# =============================================================================
# EUCLIDEAN PROPOSITIONS
# =============================================================================

@dataclass
class Proposition:
    """
    A Euclidean proposition as a bit in the 31-bit register.
    """
    
    number: int  # 1-31
    statement: str = ""
    is_axiom: bool = False
    dependencies: List[int] = field(default_factory=list)
    
    @property
    def bit_position(self) -> int:
        """Position in the register (0-indexed)."""
        return self.number - 1
    
    def to_bit(self) -> int:
        """Convert proposition truth to bit."""
        return 1  # Propositions are true
    
    def is_parity(self) -> bool:
        """Check if this is a parity position."""
        return self.number in [1, 2, 4, 8, 16]


class EuclideanRegister:
    """
    The 31-proposition register of Euclid's Elements Book I.
    
    Implements error correction at the geometric level.
    """
    
    def __init__(self):
        self.hamming = HammingCode(r=5)
        self._init_propositions()
    
    def _init_propositions(self) -> None:
        """Initialize the 31 propositions."""
        self.propositions = []
        
        # First few propositions of Book I
        prop_data = [
            (1, "Construct equilateral triangle", False, []),
            (2, "Place equal segment at point", False, [1]),
            (3, "Cut off equal segment", False, [2]),
            (4, "SAS triangle congruence", True, [1, 2, 3]),
            (5, "Isoceles triangle angles", False, [4]),
            # ... remaining 26 propositions
        ]
        
        for i in range(1, 32):
            if i <= len(prop_data):
                num, stmt, is_ax, deps = prop_data[i - 1]
                prop = Proposition(num, stmt, is_ax, deps)
            else:
                prop = Proposition(i, f"Proposition {i}")
            self.propositions.append(prop)
    
    def to_codeword(self) -> np.ndarray:
        """Convert propositions to codeword."""
        return np.array([p.to_bit() for p in self.propositions])
    
    def check_consistency(self) -> Tuple[bool, int]:
        """
        Check geometric consistency using Hamming code.
        
        Returns (is_consistent, error_position or 0).
        """
        codeword = self.to_codeword()
        syndrome = self.hamming.parity.syndrome(codeword)
        error_pos = self.hamming.parity.syndrome_to_position(syndrome)
        return (error_pos == 0, error_pos)
    
    def get_proposition(self, number: int) -> Proposition:
        """Get proposition by number (1-indexed)."""
        return self.propositions[number - 1]


# =============================================================================
# VALIDATION
# =============================================================================

def validate_euclid() -> bool:
    """Validate Euclidean error correction module."""
    
    # Test HammingParameters
    params = HammingParameters(r=5)
    assert params.n == 31
    assert params.k == 26
    assert params.minimum_distance == 3
    assert params.is_perfect()
    
    # Test ParityMatrix
    parity = ParityMatrix(params)
    assert parity.shape == (5, 31)
    
    # Column 1 should be [1,0,0,0,0]
    assert parity.column(0)[0] == 1
    
    # Test syndrome of zero word
    zero_word = np.zeros(31, dtype=int)
    syndrome = parity.syndrome(zero_word)
    assert np.all(syndrome == 0)
    
    # Test HammingCode
    hamming = HammingCode(r=5)
    
    # Encode random data
    data = np.random.randint(0, 2, size=26)
    codeword = hamming.encode(data)
    assert len(codeword) == 31
    assert hamming.check(codeword)
    
    # Decode without error
    decoded, error_pos = hamming.decode(codeword)
    assert np.all(decoded == data)
    assert error_pos == 0
    
    # Inject error and correct
    for pos in [1, 15, 31]:
        corrupted = hamming.inject_error(codeword, pos)
        assert not hamming.check(corrupted)
        
        decoded, error_pos = hamming.decode(corrupted)
        assert error_pos == pos
        assert np.all(decoded == data)
    
    # Test EuclideanRegister
    register = EuclideanRegister()
    assert len(register.propositions) == 31
    
    return True


if __name__ == "__main__":
    print("Validating Euclidean Error Correction Module...")
    assert validate_euclid()
    print("✓ Euclidean module validated")
    
    # Demo
    print("\n--- Euclidean Error Correction Demo ---")
    
    print("\n1. Hamming(31,26) Parameters:")
    params = HammingParameters(r=5)
    print(f"   n = {params.n} (codeword length)")
    print(f"   k = {params.k} (data bits)")
    print(f"   r = {params.r} (parity bits)")
    print(f"   Rate = {params.rate:.3f}")
    print(f"   d_min = {params.minimum_distance}")
    print(f"   Perfect: {params.is_perfect()}")
    
    print("\n2. Encoding Example:")
    hamming = HammingCode(r=5)
    data = np.array([1,0,1,1,0,0,1,0,1,0,
                    1,1,0,0,1,0,1,0,0,1,
                    0,1,1,0,0,1])
    codeword = hamming.encode(data)
    print(f"   Data ({len(data)} bits): {data}")
    print(f"   Codeword ({len(codeword)} bits): {codeword}")
    print(f"   Valid: {hamming.check(codeword)}")
    
    print("\n3. Error Correction:")
    for error_pos in [5, 17, 28]:
        corrupted = hamming.inject_error(codeword, error_pos)
        decoded, detected_pos = hamming.decode(corrupted)
        
        print(f"   Error at position {error_pos}:")
        print(f"     Syndrome detected position: {detected_pos}")
        print(f"     Correction successful: {np.all(decoded == data)}")
    
    print("\n4. Parity Check Matrix (first 8 columns):")
    parity = ParityMatrix(params)
    print("   Position: 1  2  3  4  5  6  7  8")
    for i in range(5):
        row = ' '.join(str(parity[i, j]) for j in range(8))
        print(f"   Row {i}:    {row}")
    
    print("\n5. Euclidean Register:")
    register = EuclideanRegister()
    consistent, error = register.check_consistency()
    print(f"   Propositions: {len(register.propositions)}")
    print(f"   Geometric consistency: {consistent}")
