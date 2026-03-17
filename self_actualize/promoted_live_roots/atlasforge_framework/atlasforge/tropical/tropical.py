"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      TROPICAL GEOMETRY MODULE                                ║
║                                                                              ║
║  Min-Plus Algebra, Tropical Curves, and Valuations                           ║
║                                                                              ║
║  Core Principle:                                                             ║
║    Tropical geometry replaces (+, ×) with (min, +).                         ║
║    This dequantization transforms algebra to combinatorics,                 ║
║    connecting to the D-pole (discrete/constraint-based).                    ║
║                                                                              ║
║  Key Structures:                                                             ║
║    - Tropical semiring: (ℝ ∪ {∞}, min, +)                                   ║
║    - Tropical polynomial: f = min_α (c_α + α·x)                             ║
║    - Tropical curve: corner locus of tropical polynomial                    ║
║    - Valuation: v(x) maps to tropical world                                 ║
║                                                                              ║
║  Connection to Framework:                                                    ║
║    - D-pole constraints ↔ tropical inequalities                             ║
║    - Optimization ↔ shortest paths (tropical matrix mult)                   ║
║    - Discrete structure ↔ tropical variety combinatorics                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Set
import numpy as np
from numpy.typing import NDArray


# ═══════════════════════════════════════════════════════════════════════════════
# TROPICAL NUMBER
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class TropicalNumber:
    """
    Element of tropical semiring (ℝ ∪ {∞}, ⊕, ⊙).
    
    x ⊕ y = min(x, y)  (tropical addition)
    x ⊙ y = x + y      (tropical multiplication)
    
    Identity for ⊕: ∞
    Identity for ⊙: 0
    """
    value: float
    
    @classmethod
    def infinity(cls) -> 'TropicalNumber':
        """Additive identity ∞."""
        return cls(float('inf'))
    
    @classmethod
    def zero(cls) -> 'TropicalNumber':
        """Multiplicative identity 0."""
        return cls(0.0)
    
    def __add__(self, other: 'TropicalNumber') -> 'TropicalNumber':
        """Tropical addition: x ⊕ y = min(x, y)."""
        return TropicalNumber(min(self.value, other.value))
    
    def __mul__(self, other: 'TropicalNumber') -> 'TropicalNumber':
        """Tropical multiplication: x ⊙ y = x + y."""
        return TropicalNumber(self.value + other.value)
    
    def __pow__(self, n: int) -> 'TropicalNumber':
        """Tropical power: x^n = n * x."""
        return TropicalNumber(n * self.value)
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TropicalNumber):
            return False
        return self.value == other.value
    
    def __lt__(self, other: 'TropicalNumber') -> bool:
        return self.value < other.value
    
    def __repr__(self) -> str:
        if self.value == float('inf'):
            return "∞"
        return f"{self.value:.4g}"
    
    def is_infinity(self) -> bool:
        return self.value == float('inf')


# ═══════════════════════════════════════════════════════════════════════════════
# TROPICAL MATRIX
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class TropicalMatrix:
    """
    Matrix over tropical semiring.
    
    Matrix multiplication finds shortest paths.
    """
    data: NDArray[np.float64]
    
    @property
    def shape(self) -> Tuple[int, int]:
        return self.data.shape
    
    def __getitem__(self, idx: Tuple[int, int]) -> TropicalNumber:
        return TropicalNumber(self.data[idx])
    
    def __matmul__(self, other: 'TropicalMatrix') -> 'TropicalMatrix':
        """
        Tropical matrix multiplication.
        
        (A ⊙ B)_{ij} = ⊕_k (A_{ik} ⊙ B_{kj}) = min_k (A_{ik} + B_{kj})
        """
        m, n = self.shape
        n2, p = other.shape
        
        if n != n2:
            raise ValueError(f"Shape mismatch: {self.shape} vs {other.shape}")
        
        result = np.full((m, p), float('inf'))
        
        for i in range(m):
            for j in range(p):
                for k in range(n):
                    result[i, j] = min(result[i, j], 
                                       self.data[i, k] + other.data[k, j])
        
        return TropicalMatrix(result)
    
    def __add__(self, other: 'TropicalMatrix') -> 'TropicalMatrix':
        """Tropical matrix addition: entrywise min."""
        return TropicalMatrix(np.minimum(self.data, other.data))
    
    def power(self, n: int) -> 'TropicalMatrix':
        """Matrix power A^n (for shortest paths of length n)."""
        if n == 0:
            return TropicalMatrix.identity(self.shape[0])
        
        result = self
        for _ in range(n - 1):
            result = result @ self
        
        return result
    
    def kleene_star(self, max_iter: int = 100) -> 'TropicalMatrix':
        """
        Kleene star A* = I ⊕ A ⊕ A² ⊕ ... (all paths).
        
        Converges if no negative cycles.
        """
        n = self.shape[0]
        result = TropicalMatrix.identity(n)
        power = self
        
        for _ in range(max_iter):
            old_result = result.data.copy()
            result = result + power
            power = power @ self
            
            if np.allclose(old_result, result.data):
                break
        
        return result
    
    def shortest_path(self, i: int, j: int) -> float:
        """Shortest path distance from i to j."""
        star = self.kleene_star()
        return star.data[i, j]
    
    @classmethod
    def identity(cls, n: int) -> 'TropicalMatrix':
        """Tropical identity: 0 on diagonal, ∞ elsewhere."""
        data = np.full((n, n), float('inf'))
        np.fill_diagonal(data, 0)
        return cls(data)
    
    @classmethod
    def from_graph(cls, adj: NDArray, default: float = float('inf')
                  ) -> 'TropicalMatrix':
        """Create tropical matrix from weighted adjacency."""
        data = np.where(adj > 0, adj, default)
        np.fill_diagonal(data, 0)
        return cls(data)


# ═══════════════════════════════════════════════════════════════════════════════
# TROPICAL POLYNOMIAL
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class TropicalPolynomial:
    """
    Tropical polynomial in one variable.
    
    f(x) = ⊕_i (c_i ⊙ x^i) = min_i (c_i + i·x)
    
    coefficients: list where coefficients[i] = c_i (or ∞ if missing)
    """
    coefficients: List[float]
    
    def __call__(self, x: float) -> float:
        """Evaluate tropical polynomial at x."""
        values = [c + i * x for i, c in enumerate(self.coefficients)
                 if c != float('inf')]
        return min(values) if values else float('inf')
    
    def __add__(self, other: 'TropicalPolynomial') -> 'TropicalPolynomial':
        """Tropical polynomial addition: entrywise min."""
        n = max(len(self.coefficients), len(other.coefficients))
        
        result = []
        for i in range(n):
            c1 = self.coefficients[i] if i < len(self.coefficients) else float('inf')
            c2 = other.coefficients[i] if i < len(other.coefficients) else float('inf')
            result.append(min(c1, c2))
        
        return TropicalPolynomial(result)
    
    def __mul__(self, other: 'TropicalPolynomial') -> 'TropicalPolynomial':
        """Tropical polynomial multiplication: min-convolution."""
        n1 = len(self.coefficients)
        n2 = len(other.coefficients)
        
        result = [float('inf')] * (n1 + n2 - 1)
        
        for i, c1 in enumerate(self.coefficients):
            for j, c2 in enumerate(other.coefficients):
                if c1 != float('inf') and c2 != float('inf'):
                    result[i + j] = min(result[i + j], c1 + c2)
        
        return TropicalPolynomial(result)
    
    def corner_locus(self) -> List[float]:
        """
        Find corner points (tropical roots).
        
        Corners occur where multiple terms achieve the minimum.
        """
        corners = []
        n = len(self.coefficients)
        
        # Corner at intersection of lines c_i + ix and c_j + jx
        for i in range(n):
            for j in range(i + 1, n):
                c_i = self.coefficients[i]
                c_j = self.coefficients[j]
                
                if c_i == float('inf') or c_j == float('inf'):
                    continue
                
                # c_i + ix = c_j + jx => x = (c_i - c_j)/(j - i)
                x = (c_i - c_j) / (j - i)
                
                # Check this is actually a corner (minimum)
                val = self(x)
                expected = c_i + i * x
                
                if np.isclose(val, expected, atol=1e-10):
                    corners.append(x)
        
        return sorted(set(corners))
    
    @classmethod
    def from_roots(cls, roots: List[float]) -> 'TropicalPolynomial':
        """
        Create tropical polynomial from roots.
        
        (x ⊕ r_1) ⊙ (x ⊕ r_2) ⊙ ... = min(x, r_1) + min(x, r_2) + ...
        """
        result = cls([0])  # Tropical 1
        for r in roots:
            factor = cls([r, 0])  # x ⊕ r = min(x, r)
            result = result * factor
        return result


# ═══════════════════════════════════════════════════════════════════════════════
# TROPICAL CURVE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class TropicalCurve:
    """
    Tropical curve in ℝ².
    
    Corner locus of tropical polynomial in two variables.
    """
    # Terms: dict mapping (i, j) exponent to coefficient c
    terms: Dict[Tuple[int, int], float]
    
    def evaluate(self, x: float, y: float) -> float:
        """Evaluate tropical polynomial at (x, y)."""
        values = [c + i * x + j * y 
                 for (i, j), c in self.terms.items()
                 if c != float('inf')]
        return min(values) if values else float('inf')
    
    def is_on_curve(self, x: float, y: float, tolerance: float = 1e-10) -> bool:
        """
        Check if (x, y) is on the tropical curve.
        
        On curve iff minimum achieved by ≥ 2 terms.
        """
        values = [(c + i * x + j * y, (i, j)) 
                 for (i, j), c in self.terms.items()
                 if c != float('inf')]
        
        if len(values) < 2:
            return False
        
        values.sort()
        return values[1][0] - values[0][0] < tolerance
    
    def vertices(self, x_range: Tuple[float, float] = (-10, 10),
                y_range: Tuple[float, float] = (-10, 10),
                resolution: int = 100) -> List[Tuple[float, float]]:
        """Find approximate vertices of tropical curve."""
        vertices = []
        
        xs = np.linspace(x_range[0], x_range[1], resolution)
        ys = np.linspace(y_range[0], y_range[1], resolution)
        
        for x in xs:
            for y in ys:
                if self.is_on_curve(x, y):
                    vertices.append((x, y))
        
        return vertices
    
    @classmethod
    def line(cls) -> 'TropicalCurve':
        """Tropical line: min(0, x, y) = 0."""
        return cls({(0, 0): 0, (1, 0): 0, (0, 1): 0})
    
    @classmethod
    def conic(cls) -> 'TropicalCurve':
        """Tropical conic: min(0, x, y, 2x, x+y, 2y)."""
        return cls({
            (0, 0): 0, (1, 0): 0, (0, 1): 0,
            (2, 0): 0, (1, 1): 0, (0, 2): 0
        })


# ═══════════════════════════════════════════════════════════════════════════════
# VALUATION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Valuation:
    """
    Valuation v: K* → ℝ.
    
    v(xy) = v(x) + v(y)
    v(x + y) ≥ min(v(x), v(y))
    """
    
    @staticmethod
    def p_adic(n: int, p: int) -> float:
        """
        p-adic valuation: v_p(n) = largest k with p^k | n.
        """
        if n == 0:
            return float('inf')
        
        n = abs(n)
        k = 0
        while n % p == 0:
            n //= p
            k += 1
        
        return float(k)
    
    @staticmethod
    def degree_valuation(poly: List[float]) -> float:
        """Degree valuation: v(f) = -deg(f)."""
        for i, c in enumerate(reversed(poly)):
            if c != 0:
                return float(-(len(poly) - 1 - i))
        return float('inf')
    
    @staticmethod
    def tropicalize(values: List[float], base: float = np.e) -> List[float]:
        """
        Tropicalize by taking log.
        
        Maps (ℝ₊, ×, +) to (ℝ, +, min).
        """
        return [-np.log(v) / np.log(base) if v > 0 else float('inf') 
                for v in values]


# ═══════════════════════════════════════════════════════════════════════════════
# D-POLE TROPICAL BRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class DPoleTropicalBridge:
    """
    Bridge between D-pole (discrete) and tropical geometry.
    """
    
    @staticmethod
    def constraint_to_tropical(constraints: List[Tuple[List[float], float]]
                              ) -> TropicalMatrix:
        """
        Convert linear constraints Ax ≤ b to tropical form.
        
        Each constraint becomes a row in tropical matrix.
        """
        if not constraints:
            return TropicalMatrix(np.array([[float('inf')]]))
        
        n_vars = len(constraints[0][0])
        n_constraints = len(constraints)
        
        data = np.zeros((n_constraints, n_vars))
        for i, (coeffs, bound) in enumerate(constraints):
            for j, c in enumerate(coeffs):
                data[i, j] = c
        
        return TropicalMatrix(data)
    
    @staticmethod
    def shortest_path_from_adj(adj: NDArray) -> TropicalMatrix:
        """All-pairs shortest paths via tropical matrix."""
        trop = TropicalMatrix.from_graph(adj)
        return trop.kleene_star()


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def tropical(x: float) -> TropicalNumber:
    """Create tropical number."""
    return TropicalNumber(x)


def tropical_matrix(data: NDArray) -> TropicalMatrix:
    """Create tropical matrix."""
    return TropicalMatrix(data)


def tropical_poly(*coeffs: float) -> TropicalPolynomial:
    """Create tropical polynomial."""
    return TropicalPolynomial(list(coeffs))


def all_pairs_shortest_paths(adj: NDArray) -> NDArray:
    """Compute all-pairs shortest paths."""
    trop = TropicalMatrix.from_graph(adj)
    star = trop.kleene_star()
    return star.data


def p_adic_valuation(n: int, p: int) -> float:
    """p-adic valuation of n."""
    return Valuation.p_adic(n, p)


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Core
    'TropicalNumber',
    'TropicalMatrix',
    'TropicalPolynomial',
    'TropicalCurve',
    
    # Valuation
    'Valuation',
    
    # Bridge
    'DPoleTropicalBridge',
    
    # Functions
    'tropical',
    'tropical_matrix',
    'tropical_poly',
    'all_pairs_shortest_paths',
    'p_adic_valuation',
]
