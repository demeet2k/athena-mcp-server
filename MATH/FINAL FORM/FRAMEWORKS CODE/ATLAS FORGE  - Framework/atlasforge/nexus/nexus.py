"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        NEXUS NAVIGATION MODULE                               ║
║                                                                              ║
║  Pell Nexus Points, Triangular-Square Numbers, Figurate Sequences            ║
║                                                                              ║
║  Core Discovery:                                                             ║
║    Pell equations generate "nexus points" where different number-theoretic   ║
║    structures intersect. These form navigation waypoints for gateway         ║
║    transport between representations.                                        ║
║                                                                              ║
║  Key Nexus Types:                                                            ║
║    - Triangular-Square: T_n = S_m (both triangular and square)              ║
║    - Pentagonal-Triangular: intersections in figurate lattice               ║
║    - Pronic-Square: n(n+1) connections                                      ║
║                                                                              ║
║  Navigation Principle:                                                       ║
║    Gateway hops through nexus points minimize transport cost                 ║
║    by exploiting algebraic coincidences.                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Iterator, Any
from enum import Enum, auto
import numpy as np
from numpy.typing import NDArray


# ═══════════════════════════════════════════════════════════════════════════════
# FIGURATE NUMBER TYPES
# ═══════════════════════════════════════════════════════════════════════════════

class FigurateType(Enum):
    """Types of figurate numbers."""
    TRIANGULAR = "triangular"      # T_n = n(n+1)/2
    SQUARE = "square"              # S_n = n²
    PENTAGONAL = "pentagonal"      # P_n = n(3n-1)/2
    HEXAGONAL = "hexagonal"        # H_n = n(2n-1)
    HEPTAGONAL = "heptagonal"      # He_n = n(5n-3)/2
    OCTAGONAL = "octagonal"        # O_n = n(3n-2)
    PRONIC = "pronic"              # Pr_n = n(n+1) (oblong)
    CENTERED_SQUARE = "centered_square"  # CS_n = n² + (n-1)²


@dataclass
class FigurateNumber:
    """
    A figurate number with its type and index.
    
    Figurate numbers are numbers that can be represented as
    regular geometric arrangements of points.
    """
    ftype: FigurateType
    index: int
    value: int = field(init=False)
    
    def __post_init__(self):
        self.value = self._compute_value()
    
    def _compute_value(self) -> int:
        """Compute the figurate number value."""
        n = self.index
        if self.ftype == FigurateType.TRIANGULAR:
            return n * (n + 1) // 2
        elif self.ftype == FigurateType.SQUARE:
            return n * n
        elif self.ftype == FigurateType.PENTAGONAL:
            return n * (3 * n - 1) // 2
        elif self.ftype == FigurateType.HEXAGONAL:
            return n * (2 * n - 1)
        elif self.ftype == FigurateType.HEPTAGONAL:
            return n * (5 * n - 3) // 2
        elif self.ftype == FigurateType.OCTAGONAL:
            return n * (3 * n - 2)
        elif self.ftype == FigurateType.PRONIC:
            return n * (n + 1)
        elif self.ftype == FigurateType.CENTERED_SQUARE:
            return n * n + (n - 1) * (n - 1) if n > 0 else 0
        else:
            raise ValueError(f"Unknown figurate type: {self.ftype}")
    
    @classmethod
    def triangular(cls, n: int) -> 'FigurateNumber':
        return cls(FigurateType.TRIANGULAR, n)
    
    @classmethod
    def square(cls, n: int) -> 'FigurateNumber':
        return cls(FigurateType.SQUARE, n)
    
    @classmethod
    def pentagonal(cls, n: int) -> 'FigurateNumber':
        return cls(FigurateType.PENTAGONAL, n)


# ═══════════════════════════════════════════════════════════════════════════════
# NEXUS POINT
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class NexusPoint:
    """
    A nexus point where two figurate sequences intersect.
    
    For example, triangular-square numbers are both T_n and S_m.
    """
    value: int
    type1: FigurateType
    index1: int
    type2: FigurateType
    index2: int
    
    @property
    def is_valid(self) -> bool:
        """Verify this is a valid nexus point."""
        f1 = FigurateNumber(self.type1, self.index1)
        f2 = FigurateNumber(self.type2, self.index2)
        return f1.value == f2.value == self.value
    
    def __repr__(self) -> str:
        return (f"NexusPoint({self.value}: "
                f"{self.type1.value}[{self.index1}] = "
                f"{self.type2.value}[{self.index2}])")


# ═══════════════════════════════════════════════════════════════════════════════
# TRIANGULAR-SQUARE NEXUS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class TriangularSquareNexus:
    """
    Generator for triangular-square numbers.
    
    These are numbers that are both triangular T_n = n(n+1)/2
    and perfect squares S_m = m².
    
    The sequence: 0, 1, 36, 1225, 41616, 1413721, ...
    
    Generated by Pell equation: x² - 8y² = 1
    where x = 2n+1, y gives the triangular index.
    
    Recurrence: N_{k+1} = 34·N_k - N_{k-1} + 2
    """
    
    @staticmethod
    def pell_fundamental() -> Tuple[int, int]:
        """Fundamental solution to x² - 8y² = 1."""
        return (3, 1)  # 3² - 8·1² = 9 - 8 = 1
    
    def generate(self, count: int) -> List[NexusPoint]:
        """Generate first `count` triangular-square nexus points."""
        if count <= 0:
            return []
        
        nexus_points = []
        
        # Initial Pell solutions
        x, y = 1, 0  # Trivial solution gives N = 0
        u, v = self.pell_fundamental()
        
        for _ in range(count):
            # Triangular-square value from Pell coordinates
            # x² - 8y² = 1, where x = 2t+1 for triangular index t
            # N = y²·(y² + 1)/2 for the y-th triangular number
            
            if y == 0:
                N = 0
                t_idx, s_idx = 0, 0
            else:
                # The triangular index is (x-1)/2
                # The square root is y times something
                t_idx = (x - 1) // 2
                N = t_idx * (t_idx + 1) // 2
                s_idx = int(np.sqrt(N)) if N > 0 else 0
            
            nexus_points.append(NexusPoint(
                value=N,
                type1=FigurateType.TRIANGULAR,
                index1=t_idx,
                type2=FigurateType.SQUARE,
                index2=s_idx
            ))
            
            # Pell recursion: (x', y') = (u·x + 8·v·y, v·x + u·y)
            x_new = u * x + 8 * v * y
            y_new = v * x + u * y
            x, y = x_new, y_new
        
        return nexus_points
    
    def nth_triangular_square(self, n: int) -> int:
        """Get the n-th triangular-square number (0-indexed)."""
        if n == 0:
            return 0
        if n == 1:
            return 1
        
        # Use recurrence: N_{k+1} = 34·N_k - N_{k-1} + 2
        N_prev, N_curr = 0, 1
        for _ in range(n - 1):
            N_prev, N_curr = N_curr, 34 * N_curr - N_prev + 2
        
        return N_curr
    
    def is_triangular_square(self, N: int) -> bool:
        """Check if N is a triangular-square number."""
        if N < 0:
            return False
        if N == 0 or N == 1:
            return True
        
        # Check if triangular
        # N = t(t+1)/2 => t = (-1 + sqrt(1 + 8N))/2
        disc = 1 + 8 * N
        sqrt_disc = int(np.sqrt(disc))
        if sqrt_disc * sqrt_disc != disc:
            return False
        if (sqrt_disc - 1) % 2 != 0:
            return False
        
        # Check if square
        sqrt_N = int(np.sqrt(N))
        return sqrt_N * sqrt_N == N


# ═══════════════════════════════════════════════════════════════════════════════
# GENERAL PELL NEXUS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class PellNexus:
    """
    General Pell equation nexus for x² - D·y² = 1.
    
    Each discriminant D generates a different nexus sequence.
    """
    discriminant: int
    fundamental_x: int = field(init=False)
    fundamental_y: int = field(init=False)
    
    def __post_init__(self):
        self.fundamental_x, self.fundamental_y = self._find_fundamental()
    
    def _find_fundamental(self) -> Tuple[int, int]:
        """Find fundamental solution via continued fraction."""
        D = self.discriminant
        
        # Check if D is a perfect square
        sqrt_D = int(np.sqrt(D))
        if sqrt_D * sqrt_D == D:
            raise ValueError(f"D={D} is a perfect square, no solutions exist")
        
        # Continued fraction algorithm
        m, d, a = 0, 1, sqrt_D
        
        # Convergents
        p_prev, p_curr = 1, a
        q_prev, q_curr = 0, 1
        
        while True:
            m = d * a - m
            d = (D - m * m) // d
            a = (sqrt_D + m) // d
            
            p_prev, p_curr = p_curr, a * p_curr + p_prev
            q_prev, q_curr = q_curr, a * q_curr + q_prev
            
            # Check if solution found
            if p_curr * p_curr - D * q_curr * q_curr == 1:
                return (p_curr, q_curr)
            
            # Safety limit
            if q_curr > 10**15:
                raise ValueError(f"Could not find fundamental solution for D={D}")
    
    def nth_solution(self, n: int) -> Tuple[int, int]:
        """Get n-th solution (x_n, y_n) where n ≥ 1."""
        if n < 1:
            raise ValueError("n must be >= 1")
        
        x1, y1 = self.fundamental_x, self.fundamental_y
        
        if n == 1:
            return (x1, y1)
        
        # Use power formula: (x_n + y_n√D) = (x_1 + y_1√D)^n
        x, y = x1, y1
        for _ in range(n - 1):
            x_new = x * x1 + self.discriminant * y * y1
            y_new = x * y1 + y * x1
            x, y = x_new, y_new
        
        return (x, y)
    
    def solutions(self, count: int) -> List[Tuple[int, int]]:
        """Generate first `count` solutions."""
        return [self.nth_solution(n) for n in range(1, count + 1)]


# ═══════════════════════════════════════════════════════════════════════════════
# NEXUS NAVIGATOR
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class NexusNavigator:
    """
    Navigation system using nexus points as waypoints.
    
    The navigator finds efficient paths through the space
    of figurate numbers by hopping between nexus points.
    """
    triangular_square: TriangularSquareNexus = field(default_factory=TriangularSquareNexus)
    
    def nearest_triangular_square(self, N: int) -> NexusPoint:
        """Find nearest triangular-square number to N."""
        # Generate enough nexus points
        nexus_list = self.triangular_square.generate(20)
        
        best = None
        best_dist = float('inf')
        
        for nexus in nexus_list:
            dist = abs(nexus.value - N)
            if dist < best_dist:
                best_dist = dist
                best = nexus
            if nexus.value > N:
                break
        
        return best
    
    def path_through_nexus(self, start: int, end: int, 
                          max_hops: int = 5) -> List[NexusPoint]:
        """
        Find path from start to end using nexus points.
        
        Returns list of nexus waypoints.
        """
        path = []
        current = start
        
        for _ in range(max_hops):
            if current >= end:
                break
            
            # Find next useful nexus point
            nexus = self.nearest_triangular_square(current)
            
            if nexus.value > current and nexus.value <= end:
                path.append(nexus)
                current = nexus.value
            else:
                # No helpful nexus, jump directly
                break
        
        return path
    
    def gateway_matrix_for_hop(self, nexus: NexusPoint) -> NDArray[np.float64]:
        """
        Compute gateway matrix for hopping to a nexus point.
        
        Uses the Pell structure to determine the transport matrix.
        """
        # For triangular-square nexus, use (3,1) fundamental
        u, v = 3, 1
        D = 8  # Discriminant for triangular-square
        
        # Gateway matrix in SL(2,Z)
        return np.array([
            [u, D * v],
            [v, u]
        ], dtype=np.float64)


# ═══════════════════════════════════════════════════════════════════════════════
# FIGURATE LATTICE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class FigurateLattice:
    """
    Lattice of figurate numbers with multiple types.
    
    Provides unified view of triangular, square, pentagonal, etc.
    numbers and their intersections.
    """
    max_value: int = 10000
    
    def __post_init__(self):
        self._build_lattice()
    
    def _build_lattice(self):
        """Build sets of figurate numbers up to max_value."""
        self.triangular = set()
        self.square = set()
        self.pentagonal = set()
        self.hexagonal = set()
        
        n = 1
        while True:
            t = n * (n + 1) // 2
            if t > self.max_value:
                break
            self.triangular.add(t)
            n += 1
        
        n = 1
        while n * n <= self.max_value:
            self.square.add(n * n)
            n += 1
        
        n = 1
        while True:
            p = n * (3 * n - 1) // 2
            if p > self.max_value:
                break
            self.pentagonal.add(p)
            n += 1
        
        n = 1
        while True:
            h = n * (2 * n - 1)
            if h > self.max_value:
                break
            self.hexagonal.add(h)
            n += 1
    
    def intersections(self, type1: FigurateType, type2: FigurateType) -> List[int]:
        """Find intersection of two figurate types."""
        sets = {
            FigurateType.TRIANGULAR: self.triangular,
            FigurateType.SQUARE: self.square,
            FigurateType.PENTAGONAL: self.pentagonal,
            FigurateType.HEXAGONAL: self.hexagonal
        }
        
        s1 = sets.get(type1, set())
        s2 = sets.get(type2, set())
        
        return sorted(s1 & s2)
    
    def all_nexus_points(self) -> Dict[str, List[int]]:
        """Find all nexus points between different figurate types."""
        return {
            'triangular_square': self.intersections(
                FigurateType.TRIANGULAR, FigurateType.SQUARE),
            'triangular_pentagonal': self.intersections(
                FigurateType.TRIANGULAR, FigurateType.PENTAGONAL),
            'square_pentagonal': self.intersections(
                FigurateType.SQUARE, FigurateType.PENTAGONAL),
            'triangular_hexagonal': self.intersections(
                FigurateType.TRIANGULAR, FigurateType.HEXAGONAL),
        }
    
    def is_multi_figurate(self, N: int) -> Dict[FigurateType, bool]:
        """Check which figurate types N belongs to."""
        return {
            FigurateType.TRIANGULAR: N in self.triangular,
            FigurateType.SQUARE: N in self.square,
            FigurateType.PENTAGONAL: N in self.pentagonal,
            FigurateType.HEXAGONAL: N in self.hexagonal
        }


# ═══════════════════════════════════════════════════════════════════════════════
# NEXUS-BASED SCALING
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class NexusScaling:
    """
    Use nexus points to define natural scaling transformations.
    
    The ratios between consecutive nexus points define
    "canonical" scaling factors for the gateway algebra.
    """
    nexus_gen: TriangularSquareNexus = field(default_factory=TriangularSquareNexus)
    
    def scaling_ratios(self, count: int = 10) -> List[float]:
        """
        Compute ratios between consecutive triangular-square numbers.
        
        These converge to (3 + 2√2)² = 17 + 12√2 ≈ 33.97
        """
        nexus_list = self.nexus_gen.generate(count + 1)
        values = [n.value for n in nexus_list if n.value > 0]
        
        ratios = []
        for i in range(1, len(values)):
            ratios.append(values[i] / values[i-1])
        
        return ratios
    
    @staticmethod
    def asymptotic_ratio() -> float:
        """
        Asymptotic ratio between consecutive triangular-square numbers.
        
        Limit = (3 + 2√2)² = 17 + 12√2
        """
        sqrt2 = np.sqrt(2)
        return (3 + 2 * sqrt2) ** 2
    
    def canonical_scales(self, base_kappa: float, n_levels: int = 5) -> List[float]:
        """
        Generate canonical κ-scales using nexus ratios.
        """
        ratio = self.asymptotic_ratio()
        return [base_kappa * (ratio ** k) for k in range(n_levels)]


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def triangular(n: int) -> int:
    """n-th triangular number."""
    return n * (n + 1) // 2


def is_triangular(N: int) -> bool:
    """Check if N is triangular."""
    if N < 0:
        return False
    # N = n(n+1)/2 => n² + n - 2N = 0 => n = (-1 + √(1+8N))/2
    disc = 1 + 8 * N
    sqrt_disc = int(np.sqrt(disc))
    if sqrt_disc * sqrt_disc != disc:
        return False
    return (sqrt_disc - 1) % 2 == 0


def is_square(N: int) -> bool:
    """Check if N is a perfect square."""
    if N < 0:
        return False
    sqrt_N = int(np.sqrt(N))
    return sqrt_N * sqrt_N == N


def is_triangular_square(N: int) -> bool:
    """Check if N is both triangular and square."""
    return is_triangular(N) and is_square(N)


def triangular_square_sequence(count: int) -> List[int]:
    """Generate first `count` triangular-square numbers."""
    ts = TriangularSquareNexus()
    return [ts.nth_triangular_square(n) for n in range(count)]


def solve_pell(D: int, count: int = 5) -> List[Tuple[int, int]]:
    """Solve Pell equation x² - Dy² = 1."""
    pell = PellNexus(D)
    return pell.solutions(count)


def figurate_intersections(max_value: int = 10000) -> Dict[str, List[int]]:
    """Find all figurate number intersections up to max_value."""
    lattice = FigurateLattice(max_value)
    return lattice.all_nexus_points()


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Enums
    'FigurateType',
    
    # Classes
    'FigurateNumber',
    'NexusPoint',
    'TriangularSquareNexus',
    'PellNexus',
    'NexusNavigator',
    'FigurateLattice',
    'NexusScaling',
    
    # Functions
    'triangular',
    'is_triangular',
    'is_square',
    'is_triangular_square',
    'triangular_square_sequence',
    'solve_pell',
    'figurate_intersections',
]
