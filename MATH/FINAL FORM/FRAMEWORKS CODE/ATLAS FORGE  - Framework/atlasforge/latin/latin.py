"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                       LATIN KERNEL SYSTEMS MODULE                            ║
║                                                                              ║
║  4×4 Holographic Seed, Prime Diagonal Latin Squares, Klein-4 Symmetry        ║
║                                                                              ║
║  Core Principle:                                                             ║
║    The 4×4 diagonal Latin kernel with Klein-4 symmetry is the minimal        ║
║    discrete structure exhibiting:                                            ║
║      - Latin uniqueness in rows, columns, and both diagonals                 ║
║      - Near-maximal 2×2 holography (local-global encoding)                   ║
║      - Klein-4 = ℤ₂×ℤ₂ bit-flip symmetry on 4-state alphabet                ║
║      - Radix-4 tower construction for arbitrary powers of 4                  ║
║                                                                              ║
║  Canonical 4×4 Seed:                                                         ║
║    1 2 3 4        or equivalently in ℤ₄:    0 1 2 3                         ║
║    3 4 1 2                                  2 3 0 1                         ║
║    4 3 2 1                                  3 2 1 0                         ║
║    2 1 4 3                                  1 0 3 2                         ║
║                                                                              ║
║  Prime DLS (Affine Family):                                                  ║
║    L_k(i,j) = i + k·j (mod p), where k ∉ {0, 1, -1} mod p                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Set, FrozenSet, Callable, Any
from enum import Enum, auto
import numpy as np
from numpy.typing import NDArray
import itertools


# ═══════════════════════════════════════════════════════════════════════════════
# KLEIN-4 GROUP - THE FUNDAMENTAL SYMMETRY
# ═══════════════════════════════════════════════════════════════════════════════

class Klein4Element(Enum):
    """
    Elements of Klein-4 group K₄ = ℤ₂ × ℤ₂.
    
    Acting on 2-bit space {0,1,2,3} ≅ {00,01,10,11}:
        I: identity
        R: flip bit 0 (swap 0↔1, 2↔3)
        S: flip bit 1 (swap 0↔2, 1↔3)  
        C: flip both bits (swap 0↔3, 1↔2)
    """
    I = (0, 0)  # Identity
    R = (1, 0)  # First bit flip
    S = (0, 1)  # Second bit flip
    C = (1, 1)  # Both bits flip (complement)
    
    @property
    def bits(self) -> Tuple[int, int]:
        return self.value
    
    def apply(self, x: int) -> int:
        """Apply element to 2-bit value x ∈ {0,1,2,3}."""
        b0, b1 = self.bits
        # x = x₁·2 + x₀
        x0 = x & 1
        x1 = (x >> 1) & 1
        new_x0 = x0 ^ b0
        new_x1 = x1 ^ b1
        return new_x1 * 2 + new_x0
    
    def compose(self, other: 'Klein4Element') -> 'Klein4Element':
        """Group multiplication: XOR on bit vectors."""
        new_bits = (self.bits[0] ^ other.bits[0], self.bits[1] ^ other.bits[1])
        for elem in Klein4Element:
            if elem.bits == new_bits:
                return elem
        raise RuntimeError("Invalid composition")
    
    def inverse(self) -> 'Klein4Element':
        """All elements are self-inverse in Klein-4."""
        return self
    
    def __mul__(self, other: 'Klein4Element') -> 'Klein4Element':
        return self.compose(other)


class Klein4Group:
    """
    Complete Klein-4 group structure.
    
    Cayley table:
        * | I R S C
        --|--------
        I | I R S C
        R | R I C S
        S | S C I R
        C | C S R I
    """
    
    elements = list(Klein4Element)
    
    @classmethod
    def cayley_table(cls) -> NDArray[np.int64]:
        """4×4 Cayley table."""
        table = np.zeros((4, 4), dtype=np.int64)
        for i, a in enumerate(cls.elements):
            for j, b in enumerate(cls.elements):
                product = a * b
                table[i, j] = cls.elements.index(product)
        return table
    
    @classmethod
    def orbit(cls, x: int) -> Set[int]:
        """Full orbit of x under Klein-4 action."""
        return {elem.apply(x) for elem in cls.elements}
    
    @classmethod
    def is_transitive(cls) -> bool:
        """Check if action is transitive on {0,1,2,3}."""
        return cls.orbit(0) == {0, 1, 2, 3}
    
    @classmethod
    def stabilizer(cls, x: int) -> Set[Klein4Element]:
        """Elements fixing x."""
        return {elem for elem in cls.elements if elem.apply(x) == x}
    
    @classmethod
    def character_table(cls) -> NDArray[np.int64]:
        """
        Character table of Klein-4.
        All irreps are 1-dimensional (abelian group).
        """
        # Characters: trivial, R-sign, S-sign, C-sign
        return np.array([
            [1,  1,  1,  1],   # trivial
            [1,  1, -1, -1],   # sign on S and C
            [1, -1,  1, -1],   # sign on R and C
            [1, -1, -1,  1],   # sign on R and S
        ], dtype=np.int64)


# ═══════════════════════════════════════════════════════════════════════════════
# DIAGONAL LATIN SQUARE - THE FUNDAMENTAL OBJECT
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class DiagonalLatinSquare:
    """
    A Latin square with both diagonals also being permutations.
    
    Properties:
        - Each row is a permutation of {0, ..., n-1}
        - Each column is a permutation of {0, ..., n-1}
        - Main diagonal is a permutation
        - Anti-diagonal is a permutation
    
    Existence: Order 1, 4, and all n ≥ 5 except n = 6.
    """
    matrix: NDArray[np.int64]
    
    def __post_init__(self):
        self._validate()
    
    def _validate(self):
        """Verify all Latin and diagonal properties."""
        n = self.order
        symbols = set(range(n))
        
        # Check rows
        for i in range(n):
            if set(self.matrix[i, :]) != symbols:
                raise ValueError(f"Row {i} is not a permutation")
        
        # Check columns
        for j in range(n):
            if set(self.matrix[:, j]) != symbols:
                raise ValueError(f"Column {j} is not a permutation")
        
        # Check main diagonal
        main_diag = set(self.matrix[i, i] for i in range(n))
        if main_diag != symbols:
            raise ValueError("Main diagonal is not a permutation")
        
        # Check anti-diagonal
        anti_diag = set(self.matrix[i, n-1-i] for i in range(n))
        if anti_diag != symbols:
            raise ValueError("Anti-diagonal is not a permutation")
    
    @property
    def order(self) -> int:
        """Size n of the n×n square."""
        return self.matrix.shape[0]
    
    @property
    def main_diagonal(self) -> NDArray[np.int64]:
        """Main diagonal entries."""
        return np.diag(self.matrix)
    
    @property
    def anti_diagonal(self) -> NDArray[np.int64]:
        """Anti-diagonal entries."""
        n = self.order
        return np.array([self.matrix[i, n-1-i] for i in range(n)])
    
    def row(self, i: int) -> NDArray[np.int64]:
        """i-th row."""
        return self.matrix[i, :]
    
    def column(self, j: int) -> NDArray[np.int64]:
        """j-th column."""
        return self.matrix[:, j]
    
    def window_2x2(self, i: int, j: int) -> NDArray[np.int64]:
        """2×2 window with top-left at (i, j)."""
        return self.matrix[i:i+2, j:j+2]
    
    def all_2x2_windows(self) -> List[NDArray[np.int64]]:
        """All (n-1)² 2×2 windows."""
        n = self.order
        windows = []
        for i in range(n - 1):
            for j in range(n - 1):
                windows.append(self.window_2x2(i, j))
        return windows
    
    def is_holographic_window(self, window: NDArray[np.int64]) -> bool:
        """
        Check if 2×2 window is holographic (contains all 4 symbols).
        For order-4 DLS: 4 symbols → must be {0,1,2,3}.
        """
        return len(set(window.flatten())) == 4
    
    def holography_count(self) -> int:
        """Count of holographic 2×2 windows."""
        return sum(1 for w in self.all_2x2_windows() 
                   if self.is_holographic_window(w))
    
    def holography_fraction(self) -> float:
        """Fraction of 2×2 windows that are holographic."""
        total = (self.order - 1) ** 2
        if total == 0:
            return 1.0
        return self.holography_count() / total
    
    def transpose(self) -> 'DiagonalLatinSquare':
        """Transpose (also a DLS)."""
        return DiagonalLatinSquare(matrix=self.matrix.T.copy())
    
    def __repr__(self) -> str:
        return f"DLS(order={self.order}, holography={self.holography_fraction():.2%})"


# ═══════════════════════════════════════════════════════════════════════════════
# CANONICAL 4×4 SEED - THE HOLOGRAPHIC KERNEL
# ═══════════════════════════════════════════════════════════════════════════════

class HolographicSeed4x4:
    """
    The canonical 4×4 diagonal Latin seed with Klein-4 symmetry.
    
    Seed (0-indexed):
        0 1 2 3
        2 3 0 1
        3 2 1 0
        1 0 3 2
    
    Properties:
        - All rows, columns, diagonals are permutations of {0,1,2,3}
        - 8 of 9 2×2 windows are holographic (88.9%)
        - Klein-4 symmetric: K₄ acts by symbol permutation
        - Generates radix-4 tower for orders 4^r
    """
    
    # Canonical seed matrix
    SEED = np.array([
        [0, 1, 2, 3],
        [2, 3, 0, 1],
        [3, 2, 1, 0],
        [1, 0, 3, 2]
    ], dtype=np.int64)
    
    @classmethod
    def get_dls(cls) -> DiagonalLatinSquare:
        """Get as DiagonalLatinSquare object."""
        return DiagonalLatinSquare(matrix=cls.SEED.copy())
    
    @classmethod
    def klein4_action(cls, element: Klein4Element) -> NDArray[np.int64]:
        """
        Apply Klein-4 element to seed (symbol permutation).
        Returns new matrix with symbols permuted.
        """
        result = np.zeros_like(cls.SEED)
        for i in range(4):
            for j in range(4):
                result[i, j] = element.apply(cls.SEED[i, j])
        return result
    
    @classmethod
    def is_invariant_under_klein4(cls) -> bool:
        """
        Check if seed is invariant under Klein-4 action.
        (It's not literally invariant, but the structure is preserved.)
        """
        base = cls.get_dls()
        for elem in Klein4Element:
            transformed = cls.klein4_action(elem)
            try:
                DiagonalLatinSquare(matrix=transformed)
            except ValueError:
                return False
        return True
    
    @classmethod
    def holographic_windows(cls) -> List[Tuple[int, int, NDArray[np.int64]]]:
        """Get all 2×2 windows with their positions."""
        dls = cls.get_dls()
        results = []
        for i in range(3):
            for j in range(3):
                window = dls.window_2x2(i, j)
                is_holo = len(set(window.flatten())) == 4
                results.append((i, j, window, is_holo))
        return results
    
    @classmethod
    def non_holographic_window(cls) -> Optional[Tuple[int, int, NDArray[np.int64]]]:
        """Find the non-holographic window (if any)."""
        for i, j, window, is_holo in cls.holographic_windows():
            if not is_holo:
                return (i, j, window)
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# RADIX-4 TOWER - RECURSIVE CONSTRUCTION
# ═══════════════════════════════════════════════════════════════════════════════

class Radix4Tower:
    """
    Recursive construction of order 4^r diagonal Latin squares.
    
    L_{4^r}[i,j] = 4^{r-1} · (L_4[i_0, j_0] - 1) + L_{4^{r-1}}[i', j']
    
    where:
        i = 4^{r-1} · i_0 + i'
        j = 4^{r-1} · j_0 + j'
        i_0, j_0 ∈ {0,1,2,3}
        i', j' ∈ {0, ..., 4^{r-1}-1}
    """
    
    def __init__(self, base_seed: NDArray[np.int64] = None):
        """Initialize with base 4×4 seed."""
        self.base = base_seed if base_seed is not None else HolographicSeed4x4.SEED.copy()
    
    def generate(self, r: int) -> NDArray[np.int64]:
        """
        Generate order 4^r DLS recursively.
        
        Args:
            r: Tower level (1 gives 4×4, 2 gives 16×16, etc.)
        """
        if r < 1:
            raise ValueError("r must be ≥ 1")
        if r == 1:
            return self.base.copy()
        
        # Recursive construction
        n = 4 ** r
        block_size = 4 ** (r - 1)
        
        # Get smaller DLS
        smaller = self.generate(r - 1)
        
        # Build larger DLS
        result = np.zeros((n, n), dtype=np.int64)
        
        for i in range(n):
            for j in range(n):
                # Decompose indices
                i0 = i // block_size
                i_prime = i % block_size
                j0 = j // block_size
                j_prime = j % block_size
                
                # Apply recursion formula
                coarse = self.base[i0, j0]
                fine = smaller[i_prime, j_prime]
                result[i, j] = block_size * coarse + fine
        
        return result
    
    def verify_dls(self, r: int) -> bool:
        """Verify that generated matrix is a valid DLS."""
        matrix = self.generate(r)
        try:
            DiagonalLatinSquare(matrix=matrix)
            return True
        except ValueError:
            return False
    
    def holography_by_level(self, max_r: int = 4) -> Dict[int, float]:
        """Compute holography fraction for each tower level."""
        results = {}
        for r in range(1, max_r + 1):
            matrix = self.generate(r)
            dls = DiagonalLatinSquare(matrix=matrix)
            results[r] = dls.holography_fraction()
        return results


# ═══════════════════════════════════════════════════════════════════════════════
# PRIME DIAGONAL LATIN SQUARES - AFFINE FAMILY
# ═══════════════════════════════════════════════════════════════════════════════

class AffineDLS:
    """
    Affine diagonal Latin squares over ℤ_p (p prime).
    
    L_k(i,j) = i + k·j (mod p)
    
    For this to be a DLS:
        - k ≢ 0 (mod p) [rows are permutations]
        - k ≢ 1 (mod p) [main diagonal is permutation]
        - k ≢ -1 (mod p) [anti-diagonal is permutation]
    
    Valid k: k ∈ {2, 3, ..., p-2} for p ≥ 5.
    """
    
    def __init__(self, p: int, k: int):
        """
        Create affine DLS.
        
        Args:
            p: Prime order
            k: Slope parameter (must be valid)
        """
        self.p = p
        self.k = k % p
        self._validate_params()
        self.matrix = self._generate()
    
    def _validate_params(self):
        """Validate p is prime and k is valid slope."""
        if self.p < 5:
            raise ValueError(f"Prime must be ≥ 5 for DLS existence, got {self.p}")
        
        # Simple primality check
        if self.p > 2 and self.p % 2 == 0:
            raise ValueError(f"{self.p} is not prime")
        for d in range(3, int(self.p**0.5) + 1, 2):
            if self.p % d == 0:
                raise ValueError(f"{self.p} is not prime")
        
        # Valid slope check
        invalid_slopes = {0, 1, self.p - 1}  # 0, 1, -1 mod p
        if self.k in invalid_slopes:
            raise ValueError(f"Slope k={self.k} is invalid (must not be 0, 1, or -1 mod {self.p})")
    
    def _generate(self) -> NDArray[np.int64]:
        """Generate the affine DLS matrix."""
        matrix = np.zeros((self.p, self.p), dtype=np.int64)
        for i in range(self.p):
            for j in range(self.p):
                matrix[i, j] = (i + self.k * j) % self.p
        return matrix
    
    def get_dls(self) -> DiagonalLatinSquare:
        """Get as DiagonalLatinSquare object."""
        return DiagonalLatinSquare(matrix=self.matrix.copy())
    
    @property
    def row_increment(self) -> int:
        """Constant increment along rows: k."""
        return self.k
    
    @property
    def column_increment(self) -> int:
        """Constant increment along columns: 1."""
        return 1
    
    @property
    def main_diagonal_increment(self) -> int:
        """Increment along main diagonal: 1 + k."""
        return (1 + self.k) % self.p
    
    @property
    def anti_diagonal_increment(self) -> int:
        """Increment along anti-diagonal: 1 - k."""
        return (1 - self.k) % self.p
    
    @classmethod
    def canonical_slope(cls, p: int) -> int:
        """Return canonical slope k=2 for prime p ≥ 5."""
        if p < 5:
            raise ValueError(f"No DLS exists for prime {p} < 5")
        return 2
    
    @classmethod
    def all_valid_slopes(cls, p: int) -> List[int]:
        """List all valid slopes for prime p."""
        if p < 5:
            return []
        invalid = {0, 1, p - 1}
        return [k for k in range(p) if k not in invalid]
    
    def window_spectrum(self) -> Dict[FrozenSet[int], int]:
        """
        Compute 2×2 window spectrum: count of each symbol subset.
        
        For affine DLS, each 2×2 window contains 4 distinct symbols
        (holographic) for valid slopes.
        """
        spectrum = {}
        n = self.p
        for i in range(n - 1):
            for j in range(n - 1):
                window = self.matrix[i:i+2, j:j+2]
                symbols = frozenset(window.flatten())
                spectrum[symbols] = spectrum.get(symbols, 0) + 1
        return spectrum
    
    def is_fully_holographic(self) -> bool:
        """Check if all 2×2 windows are holographic."""
        spectrum = self.window_spectrum()
        for symbols in spectrum:
            if len(symbols) < 4:
                return False
        return True


# ═══════════════════════════════════════════════════════════════════════════════
# REED-SOLOMON CODE CONNECTION
# ═══════════════════════════════════════════════════════════════════════════════

class DLSCodeView:
    """
    View the affine DLS as a Reed-Solomon code structure.
    
    The rows of L_k form codewords in the affine code:
        C_{aff} = {a·1 + b·x : a,b ∈ F_p}
    
    This is a [p, 2, p-1] MDS code.
    """
    
    def __init__(self, affine_dls: AffineDLS):
        self.dls = affine_dls
        self.p = affine_dls.p
        self.k = affine_dls.k
    
    @property
    def dimension(self) -> int:
        """Code dimension: 2."""
        return 2
    
    @property
    def length(self) -> int:
        """Code length: p."""
        return self.p
    
    @property
    def minimum_distance(self) -> int:
        """Minimum distance: p - 1 (MDS bound)."""
        return self.p - 1
    
    def row_as_codeword(self, i: int) -> NDArray[np.int64]:
        """
        Row i as codeword: c(j) = i + k·j, j = 0,...,p-1.
        This is the evaluation of f(x) = i + k·x at x = 0,...,p-1.
        """
        return self.dls.matrix[i, :]
    
    def hamming_distance(self, row1: int, row2: int) -> int:
        """Hamming distance between two rows."""
        r1 = self.dls.matrix[row1, :]
        r2 = self.dls.matrix[row2, :]
        return np.sum(r1 != r2)
    
    def is_equidistant_rows(self) -> bool:
        """
        Check if all row pairs have equal distance.
        For affine DLS: d(r_i, r_j) = p for i ≠ j.
        """
        distances = set()
        for i in range(self.p):
            for j in range(i + 1, self.p):
                distances.add(self.hamming_distance(i, j))
        return len(distances) == 1


# ═══════════════════════════════════════════════════════════════════════════════
# SYMMETRY ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class DLSSymmetry:
    """
    Analyze symmetries of a diagonal Latin square.
    """
    dls: DiagonalLatinSquare
    
    def is_symmetric(self) -> bool:
        """Check if L = L^T."""
        return np.array_equal(self.dls.matrix, self.dls.matrix.T)
    
    def is_centrosymmetric(self) -> bool:
        """Check if L[i,j] + L[n-1-i, n-1-j] = n-1."""
        n = self.dls.order
        for i in range(n):
            for j in range(n):
                if self.dls.matrix[i, j] + self.dls.matrix[n-1-i, n-1-j] != n - 1:
                    return False
        return True
    
    def row_permutation_group_order(self) -> int:
        """
        Estimate order of row permutation symmetry group.
        Count row permutations that preserve DLS property.
        """
        n = self.dls.order
        count = 0
        for perm in itertools.permutations(range(n)):
            permuted = self.dls.matrix[list(perm), :]
            try:
                DiagonalLatinSquare(matrix=permuted)
                count += 1
            except ValueError:
                pass
        return count
    
    def isotopy_signature(self) -> Tuple[int, ...]:
        """
        Compute isotopy signature for equivalence classification.
        Based on sorted sequence of row/column/symbol cycle structures.
        """
        n = self.dls.order
        
        # Row cycle structure
        row_cycles = []
        for i in range(n):
            row = tuple(self.dls.matrix[i, :])
            cycles = self._cycle_type(row)
            row_cycles.append(cycles)
        
        return tuple(sorted(row_cycles))
    
    def _cycle_type(self, perm: Tuple[int, ...]) -> Tuple[int, ...]:
        """Compute cycle type of permutation."""
        n = len(perm)
        seen = [False] * n
        cycles = []
        
        for start in range(n):
            if seen[start]:
                continue
            cycle_len = 0
            i = start
            while not seen[i]:
                seen[i] = True
                i = perm[i]
                cycle_len += 1
            cycles.append(cycle_len)
        
        return tuple(sorted(cycles, reverse=True))


# ═══════════════════════════════════════════════════════════════════════════════
# LATTICE MODEL INTERPRETATION
# ═══════════════════════════════════════════════════════════════════════════════

class LatinLatticeModel:
    """
    Interpret the DLS as a lattice model constraint.
    
    Energy = 0 for configurations matching the DLS pattern.
    Energy = penalty for violations.
    
    This connects to statistical mechanics and ground state structure.
    """
    
    def __init__(self, dls: DiagonalLatinSquare, penalty: float = 1.0):
        self.dls = dls
        self.penalty = penalty
    
    def local_energy(self, i: int, j: int, state: NDArray[np.int64]) -> float:
        """
        Local energy contribution at site (i,j).
        Zero if matches DLS, penalty otherwise.
        """
        if state[i, j] == self.dls.matrix[i, j]:
            return 0.0
        return self.penalty
    
    def total_energy(self, state: NDArray[np.int64]) -> float:
        """Total energy of configuration."""
        n = self.dls.order
        energy = 0.0
        for i in range(n):
            for j in range(n):
                energy += self.local_energy(i, j, state)
        return energy
    
    def defect_count(self, state: NDArray[np.int64]) -> int:
        """Count number of sites differing from DLS."""
        return np.sum(state != self.dls.matrix)
    
    def is_ground_state(self, state: NDArray[np.int64]) -> bool:
        """Check if state is ground state (zero energy)."""
        return np.array_equal(state, self.dls.matrix)
    
    def defect_locations(self, state: NDArray[np.int64]) -> List[Tuple[int, int]]:
        """List locations of defects."""
        defects = []
        n = self.dls.order
        for i in range(n):
            for j in range(n):
                if state[i, j] != self.dls.matrix[i, j]:
                    defects.append((i, j))
        return defects


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def get_canonical_4x4_seed() -> NDArray[np.int64]:
    """Get the canonical 4×4 holographic seed."""
    return HolographicSeed4x4.SEED.copy()


def generate_dls(order: int, method: str = 'auto') -> DiagonalLatinSquare:
    """
    Generate a DLS of given order.
    
    Args:
        order: Size of square
        method: 'radix4' for powers of 4, 'affine' for primes, 'auto' to choose
    """
    if method == 'auto':
        # Check if power of 4
        if order > 0 and (order & (order - 1)) == 0:  # Power of 2
            log2 = int(np.log2(order))
            if log2 % 2 == 0:  # Power of 4
                method = 'radix4'
            else:
                method = 'affine'
        else:
            method = 'affine'
    
    if method == 'radix4':
        log4 = int(np.log2(order) / 2)
        if 4 ** log4 != order:
            raise ValueError(f"Order {order} is not a power of 4")
        tower = Radix4Tower()
        return DiagonalLatinSquare(matrix=tower.generate(log4))
    
    elif method == 'affine':
        # Use affine construction for prime orders
        if order < 5:
            raise ValueError(f"No DLS exists for order {order}")
        k = AffineDLS.canonical_slope(order)
        return AffineDLS(order, k).get_dls()
    
    else:
        raise ValueError(f"Unknown method: {method}")


def klein4_orbit(x: int) -> Set[int]:
    """Orbit of x under Klein-4 action."""
    return Klein4Group.orbit(x)


def holography_analysis(dls: DiagonalLatinSquare) -> Dict[str, Any]:
    """Complete holography analysis of a DLS."""
    windows = dls.all_2x2_windows()
    total = len(windows)
    holo_count = dls.holography_count()
    
    # Categorize windows
    holo_windows = []
    non_holo_windows = []
    
    n = dls.order
    for i in range(n - 1):
        for j in range(n - 1):
            w = dls.window_2x2(i, j)
            if len(set(w.flatten())) == 4:
                holo_windows.append((i, j))
            else:
                non_holo_windows.append((i, j))
    
    return {
        'total_windows': total,
        'holographic_count': holo_count,
        'non_holographic_count': total - holo_count,
        'fraction': holo_count / total if total > 0 else 1.0,
        'holographic_positions': holo_windows,
        'non_holographic_positions': non_holo_windows
    }


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Klein-4
    'Klein4Element',
    'Klein4Group',
    
    # DLS
    'DiagonalLatinSquare',
    'HolographicSeed4x4',
    'Radix4Tower',
    'AffineDLS',
    
    # Analysis
    'DLSCodeView',
    'DLSSymmetry',
    'LatinLatticeModel',
    
    # Functions
    'get_canonical_4x4_seed',
    'generate_dls',
    'klein4_orbit',
    'holography_analysis',
]
