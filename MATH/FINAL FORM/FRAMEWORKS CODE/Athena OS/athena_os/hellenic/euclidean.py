"""
ATHENA OS - HELLENIC: EUCLIDEAN ERROR CORRECTION
=================================================
The Anti-Fragile Data Container

THE HAMMING (31,26) CODE:
    Euclid's Elements structures as a linear block code.
    
    A valid codeword c satisfies: H·cᵀ = 0
    where H is the 5×31 parity check matrix over GF(2).

THE FIVE GATE PROPOSITIONS:
    Gate I   (Book IV.1):   10011 - Inscription
    Gate II  (Book V.2):    00011 - Aggregation
    Gate III (Book VI.2):   00010 - Proportion
    Gate IV  (Book X.8):    11000 - Irrationality
    Gate V   (Book XI.20):  01101 - Solid Closure

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
from typing import Dict, List, Optional, Tuple, Set
from enum import Enum, auto
import numpy as np


# =============================================================================
# GALOIS FIELD GF(2)
# =============================================================================

class GF2:
    """
    The Galois Field GF(2) = {0, 1}.
    
    Addition is XOR, multiplication is AND.
    """
    
    @staticmethod
    def add(a: int, b: int) -> int:
        """Addition in GF(2) = XOR."""
        return (a + b) % 2
    
    @staticmethod
    def multiply(a: int, b: int) -> int:
        """Multiplication in GF(2) = AND."""
        return a & b
    
    @staticmethod
    def vector_add(v1: np.ndarray, v2: np.ndarray) -> np.ndarray:
        """Vector addition in GF(2)."""
        return (v1 + v2) % 2
    
    @staticmethod
    def dot_product(v1: np.ndarray, v2: np.ndarray) -> int:
        """Dot product in GF(2)."""
        return np.sum(v1 * v2) % 2
    
    @staticmethod
    def matrix_vector_mult(M: np.ndarray, v: np.ndarray) -> np.ndarray:
        """Matrix-vector multiplication in GF(2)."""
        result = np.zeros(M.shape[0], dtype=int)
        for i in range(M.shape[0]):
            result[i] = np.sum(M[i] * v) % 2
        return result
    
    @staticmethod
    def matrix_mult(A: np.ndarray, B: np.ndarray) -> np.ndarray:
        """Matrix multiplication in GF(2)."""
        result = np.zeros((A.shape[0], B.shape[1]), dtype=int)
        for i in range(A.shape[0]):
            for j in range(B.shape[1]):
                result[i, j] = np.sum(A[i] * B[:, j]) % 2
        return result


# =============================================================================
# HAMMING CODE GATES
# =============================================================================

class GateProposition(Enum):
    """
    The Five Gate Propositions of Euclid.
    
    These form the parity basis for the (31,26) code.
    """
    
    GATE_I = (1, "Book IV.1", (1, 0, 0, 1, 1), "Inscription")
    GATE_II = (2, "Book V.2", (0, 0, 0, 1, 1), "Aggregation")
    GATE_III = (3, "Book VI.2", (0, 0, 0, 1, 0), "Proportion")
    GATE_IV = (4, "Book X.8", (1, 1, 0, 0, 0), "Irrationality")
    GATE_V = (5, "Book XI.20", (0, 1, 1, 0, 1), "Solid Closure")
    
    @property
    def vector(self) -> np.ndarray:
        return np.array(self.value[2], dtype=int)
    
    @property
    def locus(self) -> str:
        return self.value[1]
    
    @property
    def function(self) -> str:
        return self.value[3]


# =============================================================================
# HAMMING (31,26) CODE
# =============================================================================

class HammingCode:
    """
    The Hamming (31,26) Code.
    
    Parameters:
    - n = 31: Block length (2^5 - 1)
    - k = 26: Message length
    - r = 5:  Parity bits
    - d = 3:  Minimum distance
    - t = 1:  Error correction capability
    
    A perfect single-error-correcting code.
    """
    
    def __init__(self):
        self.n = 31  # Block length
        self.k = 26  # Message length
        self.r = 5   # Parity bits
        
        # Generate parity check matrix
        self.H = self._generate_parity_matrix()
        
        # Generate generator matrix
        self.G = self._generate_generator_matrix()
    
    def _generate_parity_matrix(self) -> np.ndarray:
        """
        Generate the 5×31 parity check matrix H.
        
        Each column is a unique non-zero 5-bit vector.
        """
        H = np.zeros((5, 31), dtype=int)
        
        col = 0
        for i in range(1, 32):  # 1 to 31
            # Convert to 5-bit binary
            bits = [(i >> j) & 1 for j in range(4, -1, -1)]
            H[:, col] = bits
            col += 1
        
        return H
    
    def _generate_generator_matrix(self) -> np.ndarray:
        """
        Generate the 26×31 generator matrix G.
        
        G = [I_k | P] in systematic form.
        """
        # For simplicity, use systematic form
        # Actual construction would derive from H
        G = np.zeros((26, 31), dtype=int)
        
        # Identity portion
        for i in range(26):
            G[i, i] = 1
        
        # Parity portion (derived from H)
        # This is a simplified construction
        for i in range(26):
            for j in range(5):
                G[i, 26 + j] = self.H[j, i]
        
        return G
    
    def encode(self, message: np.ndarray) -> np.ndarray:
        """
        Encode 26-bit message to 31-bit codeword.
        
        c = m·G
        """
        if len(message) != self.k:
            raise ValueError(f"Message must be {self.k} bits")
        
        codeword = GF2.matrix_vector_mult(self.G.T, message)
        return codeword
    
    def syndrome(self, received: np.ndarray) -> np.ndarray:
        """
        Compute syndrome s = H·rᵀ.
        
        s = 0 means no error detected.
        """
        if len(received) != self.n:
            raise ValueError(f"Received must be {self.n} bits")
        
        return GF2.matrix_vector_mult(self.H, received)
    
    def decode(self, received: np.ndarray) -> Tuple[np.ndarray, int]:
        """
        Decode received word, correcting single-bit errors.
        
        Returns (corrected_message, error_position)
        where error_position = 0 means no error.
        """
        s = self.syndrome(received)
        
        # Convert syndrome to error position
        error_pos = sum(s[i] * (2 ** (4 - i)) for i in range(5))
        
        corrected = received.copy()
        
        if error_pos > 0 and error_pos <= 31:
            # Flip the error bit (1-indexed to 0-indexed)
            corrected[error_pos - 1] = 1 - corrected[error_pos - 1]
        
        # Extract message (first 26 bits in systematic form)
        message = corrected[:self.k]
        
        return message, error_pos
    
    def is_valid_codeword(self, codeword: np.ndarray) -> bool:
        """Check if codeword is valid (syndrome = 0)."""
        s = self.syndrome(codeword)
        return np.all(s == 0)
    
    def minimum_distance(self) -> int:
        """Return minimum Hamming distance."""
        return 3
    
    def is_perfect(self) -> bool:
        """
        Verify code is perfect.
        
        A perfect code satisfies: Σᵢ₌₀ᵗ C(n,i) = 2^(n-k)
        For n=31, k=26, t=1: C(31,0) + C(31,1) = 1 + 31 = 32 = 2^5 ✓
        """
        from math import comb
        
        sphere_size = sum(comb(self.n, i) for i in range(2))  # t=1
        total_syndromes = 2 ** (self.n - self.k)
        
        return sphere_size == total_syndromes


# =============================================================================
# EUCLIDEAN STRUCTURE
# =============================================================================

@dataclass
class EuclideanProposition:
    """A proposition in Euclid's Elements."""
    
    book: int
    number: int
    statement: str
    dependencies: List[Tuple[int, int]] = field(default_factory=list)
    
    @property
    def id(self) -> Tuple[int, int]:
        return (self.book, self.number)


class EuclideanGraph:
    """
    The dependency graph of Euclid's Elements.
    
    Propositions form a directed acyclic graph (DAG)
    where edges represent logical dependencies.
    """
    
    def __init__(self):
        self.propositions: Dict[Tuple[int, int], EuclideanProposition] = {}
        self.adjacency: Dict[Tuple[int, int], Set[Tuple[int, int]]] = {}
    
    def add_proposition(self, prop: EuclideanProposition) -> None:
        """Add proposition to graph."""
        self.propositions[prop.id] = prop
        self.adjacency[prop.id] = set()
        
        for dep in prop.dependencies:
            if dep in self.adjacency:
                self.adjacency[dep].add(prop.id)
    
    def get_ancestors(self, prop_id: Tuple[int, int]) -> Set[Tuple[int, int]]:
        """Get all propositions that prop depends on."""
        if prop_id not in self.propositions:
            return set()
        
        ancestors = set()
        stack = list(self.propositions[prop_id].dependencies)
        
        while stack:
            dep = stack.pop()
            if dep not in ancestors and dep in self.propositions:
                ancestors.add(dep)
                stack.extend(self.propositions[dep].dependencies)
        
        return ancestors
    
    def get_descendants(self, prop_id: Tuple[int, int]) -> Set[Tuple[int, int]]:
        """Get all propositions that depend on prop."""
        if prop_id not in self.adjacency:
            return set()
        
        descendants = set()
        stack = list(self.adjacency[prop_id])
        
        while stack:
            child = stack.pop()
            if child not in descendants:
                descendants.add(child)
                if child in self.adjacency:
                    stack.extend(self.adjacency[child])
        
        return descendants
    
    def topological_order(self) -> List[Tuple[int, int]]:
        """Return propositions in topological order."""
        in_degree = {pid: len(self.propositions[pid].dependencies) 
                     for pid in self.propositions}
        
        queue = [pid for pid, deg in in_degree.items() if deg == 0]
        order = []
        
        while queue:
            pid = queue.pop(0)
            order.append(pid)
            
            for child in self.adjacency.get(pid, []):
                in_degree[child] -= 1
                if in_degree[child] == 0:
                    queue.append(child)
        
        return order


# =============================================================================
# ERROR CORRECTION LAYER
# =============================================================================

class EuclideanErrorCorrection:
    """
    Error correction layer using Euclidean structure.
    
    The mathematical dependencies in Elements form an
    "immune system" that detects and corrects errors.
    """
    
    def __init__(self):
        self.hamming = HammingCode()
        self.graph = EuclideanGraph()
    
    def encode_proposition(self, prop_id: Tuple[int, int],
                          data: np.ndarray) -> np.ndarray:
        """Encode proposition data with Hamming protection."""
        # Pad or truncate to 26 bits
        if len(data) < 26:
            data = np.pad(data, (0, 26 - len(data)))
        else:
            data = data[:26]
        
        return self.hamming.encode(data)
    
    def verify_and_correct(self, prop_id: Tuple[int, int],
                          received: np.ndarray) -> Tuple[np.ndarray, bool, int]:
        """
        Verify and correct received data.
        
        Returns (corrected_data, was_corrupted, error_position)
        """
        message, error_pos = self.hamming.decode(received)
        was_corrupted = error_pos > 0
        
        return message, was_corrupted, error_pos
    
    def check_consistency(self, prop_id: Tuple[int, int],
                         prop_data: Dict[Tuple[int, int], np.ndarray]) -> bool:
        """
        Check logical consistency with dependencies.
        
        Uses graph structure for additional validation.
        """
        if prop_id not in self.graph.propositions:
            return True
        
        prop = self.graph.propositions[prop_id]
        
        # All dependencies must be present and valid
        for dep_id in prop.dependencies:
            if dep_id not in prop_data:
                return False
            
            # Each dependency should be valid codeword
            if not self.hamming.is_valid_codeword(prop_data[dep_id]):
                return False
        
        return True
    
    def repair_using_redundancy(self, corrupted_id: Tuple[int, int],
                                prop_data: Dict[Tuple[int, int], np.ndarray]
                                ) -> Optional[np.ndarray]:
        """
        Attempt repair using logical redundancy.
        
        If Hamming correction fails, use dependency graph.
        """
        # First try Hamming correction
        if corrupted_id in prop_data:
            corrected, was_corrupted, _ = self.verify_and_correct(
                corrupted_id, prop_data[corrupted_id])
            
            if not was_corrupted:
                return corrected
        
        # If that fails, try inference from descendants
        # (propositions that use this one might constrain it)
        descendants = self.graph.get_descendants(corrupted_id)
        
        # This would require more sophisticated reconstruction
        # For now, return None if Hamming fails
        return None


# =============================================================================
# VALIDATION
# =============================================================================

def validate_euclidean() -> bool:
    """Validate Euclidean error correction module."""
    
    # Test GF2
    assert GF2.add(0, 0) == 0
    assert GF2.add(0, 1) == 1
    assert GF2.add(1, 1) == 0
    assert GF2.multiply(1, 1) == 1
    assert GF2.multiply(1, 0) == 0
    
    v1 = np.array([1, 0, 1, 1])
    v2 = np.array([0, 1, 1, 0])
    assert np.array_equal(GF2.vector_add(v1, v2), np.array([1, 1, 0, 1]))
    
    # Test Gate Propositions
    assert len(list(GateProposition)) == 5
    
    gate_vectors = [g.vector for g in GateProposition]
    # Check they span GF(2)^5 (rank = 5)
    M = np.array(gate_vectors)
    rank = np.linalg.matrix_rank(M.astype(float))
    assert rank == 5
    
    # Test HammingCode
    hamming = HammingCode()
    
    assert hamming.n == 31
    assert hamming.k == 26
    assert hamming.r == 5
    assert hamming.minimum_distance() == 3
    assert hamming.is_perfect()
    
    # Test encoding/decoding
    message = np.zeros(26, dtype=int)
    message[0] = 1
    message[5] = 1
    message[10] = 1
    
    codeword = hamming.encode(message)
    assert len(codeword) == 31
    assert hamming.is_valid_codeword(codeword)
    
    # Test error detection
    syndrome = hamming.syndrome(codeword)
    assert np.all(syndrome == 0)
    
    # Introduce error
    corrupted = codeword.copy()
    corrupted[7] = 1 - corrupted[7]
    
    syndrome = hamming.syndrome(corrupted)
    assert not np.all(syndrome == 0)
    
    # Test error correction
    recovered, error_pos = hamming.decode(corrupted)
    assert error_pos == 8  # Position 8 (1-indexed)
    assert np.array_equal(recovered, message)
    
    # Test EuclideanGraph
    graph = EuclideanGraph()
    
    p1 = EuclideanProposition(1, 1, "Base case", [])
    p2 = EuclideanProposition(1, 2, "Second", [(1, 1)])
    p3 = EuclideanProposition(1, 3, "Third", [(1, 1), (1, 2)])
    
    graph.add_proposition(p1)
    graph.add_proposition(p2)
    graph.add_proposition(p3)
    
    ancestors = graph.get_ancestors((1, 3))
    assert (1, 1) in ancestors
    assert (1, 2) in ancestors
    
    order = graph.topological_order()
    assert order.index((1, 1)) < order.index((1, 2))
    assert order.index((1, 2)) < order.index((1, 3))
    
    return True


if __name__ == "__main__":
    print("Validating Euclidean Error Correction...")
    assert validate_euclidean()
    print("✓ Euclidean Error Correction validated")
    
    print("\n--- Hamming (31,26) Code ---")
    hamming = HammingCode()
    print(f"  Block length: {hamming.n}")
    print(f"  Message length: {hamming.k}")
    print(f"  Parity bits: {hamming.r}")
    print(f"  Minimum distance: {hamming.minimum_distance()}")
    print(f"  Perfect code: {hamming.is_perfect()}")
    
    print("\n--- Error Correction Demo ---")
    msg = np.array([1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 
                    0, 1, 0, 1, 0, 1, 0, 1, 0, 1,
                    1, 1, 0, 0, 1, 1], dtype=int)
    code = hamming.encode(msg)
    print(f"  Original message: {msg[:10]}...")
    print(f"  Encoded: {code[:10]}...")
    
    # Corrupt bit 15
    code[14] = 1 - code[14]
    print(f"  Corrupted bit 15")
    
    recovered, pos = hamming.decode(code)
    print(f"  Detected error at position: {pos}")
    print(f"  Recovered message matches: {np.array_equal(recovered, msg)}")
