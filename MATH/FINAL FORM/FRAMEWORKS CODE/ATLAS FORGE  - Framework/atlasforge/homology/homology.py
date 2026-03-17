"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      HOMOLOGICAL ALGEBRA MODULE                              ║
║                                                                              ║
║  Chain Complexes, Homology, and Exact Sequences                              ║
║                                                                              ║
║  Core Principle:                                                             ║
║    Homological algebra measures "failure of exactness" and provides         ║
║    algebraic invariants. The hybrid equations form chain complexes,         ║
║    and homology groups detect structural obstructions.                      ║
║                                                                              ║
║  Key Structures:                                                             ║
║    - Chain complex: ... → C_{n+1} → C_n → C_{n-1} → ... with d² = 0        ║
║    - Homology: H_n = ker(d_n)/im(d_{n+1})                                   ║
║    - Exact sequence: im(f) = ker(g)                                         ║
║    - Derived functors: Ext, Tor                                             ║
║                                                                              ║
║  Connection to Framework:                                                    ║
║    - Hybrid state spaces form graded modules                                ║
║    - Pole transitions define boundary maps                                  ║
║    - Homology detects "trapped" states                                      ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Callable
import numpy as np
from numpy.typing import NDArray


# ═══════════════════════════════════════════════════════════════════════════════
# CHAIN COMPLEX
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ChainComplex:
    """
    Chain complex of vector spaces with boundary maps.
    
    ... → C_2 →^{d_2} C_1 →^{d_1} C_0 → 0
    
    Condition: d_{n} ∘ d_{n+1} = 0
    """
    dimensions: List[int]  # dim(C_0), dim(C_1), ...
    differentials: List[NDArray[np.float64]]  # d_1, d_2, ...
    
    def __post_init__(self):
        # Verify d² = 0
        for i in range(len(self.differentials) - 1):
            d_i = self.differentials[i]
            d_ip1 = self.differentials[i + 1]
            
            product = d_i @ d_ip1
            if np.max(np.abs(product)) > 1e-10:
                raise ValueError(f"d_{i} ∘ d_{i+1} ≠ 0")
    
    @property
    def length(self) -> int:
        """Number of chain groups."""
        return len(self.dimensions)
    
    def boundary(self, n: int) -> NDArray[np.float64]:
        """Get boundary map d_n: C_n → C_{n-1}."""
        if n <= 0 or n > len(self.differentials):
            # Zero map
            return np.zeros((self.dimensions[max(0, n-1)], 
                           self.dimensions[min(n, len(self.dimensions)-1)]))
        return self.differentials[n - 1]
    
    def kernel(self, n: int) -> Tuple[int, NDArray]:
        """
        Kernel of d_n.
        
        Returns (dimension, basis matrix).
        """
        d_n = self.boundary(n)
        
        # Use SVD to find null space
        U, S, Vh = np.linalg.svd(d_n)
        
        # Null space is rows of Vh corresponding to zero singular values
        tol = 1e-10
        null_mask = np.concatenate([S, np.zeros(Vh.shape[0] - len(S))]) < tol
        null_space = Vh[null_mask].T
        
        return null_space.shape[1], null_space
    
    def image(self, n: int) -> Tuple[int, NDArray]:
        """
        Image of d_{n+1}.
        
        Returns (dimension, basis matrix).
        """
        d_np1 = self.boundary(n + 1)
        
        # Use SVD to find column space
        U, S, Vh = np.linalg.svd(d_np1)
        
        tol = 1e-10
        rank = np.sum(S > tol)
        col_space = U[:, :rank]
        
        return rank, col_space
    
    def homology_dimension(self, n: int) -> int:
        """
        Dimension of H_n = ker(d_n) / im(d_{n+1}).
        
        dim(H_n) = dim(ker(d_n)) - dim(im(d_{n+1}))
        """
        ker_dim, _ = self.kernel(n)
        im_dim, _ = self.image(n)
        return ker_dim - im_dim
    
    def betti_numbers(self) -> List[int]:
        """
        Betti numbers β_n = dim(H_n).
        """
        return [self.homology_dimension(n) for n in range(self.length)]
    
    def euler_characteristic(self) -> int:
        """
        Euler characteristic χ = Σ(-1)^n β_n = Σ(-1)^n dim(C_n).
        """
        return sum((-1)**n * self.dimensions[n] for n in range(self.length))
    
    @classmethod
    def from_simplicial(cls, boundary_matrices: List[NDArray]
                       ) -> 'ChainComplex':
        """
        Create chain complex from simplicial boundary matrices.
        """
        dims = [boundary_matrices[0].shape[0]]
        for d in boundary_matrices:
            dims.append(d.shape[1])
        
        return cls(dims, boundary_matrices)


# ═══════════════════════════════════════════════════════════════════════════════
# EXACT SEQUENCE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ExactSequence:
    """
    Exact sequence of linear maps.
    
    A sequence A →^f B →^g C is exact at B if im(f) = ker(g).
    """
    spaces: List[int]  # Dimensions
    maps: List[NDArray[np.float64]]
    
    def is_exact_at(self, position: int) -> bool:
        """Check exactness at given position."""
        if position <= 0 or position >= len(self.spaces) - 1:
            return True
        
        f = self.maps[position - 1]  # Map into position
        g = self.maps[position]      # Map out of position
        
        # Check im(f) = ker(g)
        # This means: (1) g ∘ f = 0, and (2) rank(f) = dim(B) - rank(g)
        
        # Condition 1: g ∘ f = 0
        if np.max(np.abs(g @ f)) > 1e-10:
            return False
        
        # Condition 2: rank(f) + rank(g) = dim(B)
        rank_f = np.linalg.matrix_rank(f)
        rank_g = np.linalg.matrix_rank(g)
        dim_B = self.spaces[position]
        
        return rank_f + rank_g == dim_B
    
    def is_exact(self) -> bool:
        """Check if entire sequence is exact."""
        return all(self.is_exact_at(i) for i in range(1, len(self.spaces) - 1))
    
    def exactness_defect(self, position: int) -> int:
        """
        Measure failure of exactness at position.
        
        Returns dim(ker(g)/im(f)) = dim(ker(g)) - dim(im(f))
        """
        if position <= 0 or position >= len(self.spaces) - 1:
            return 0
        
        f = self.maps[position - 1]
        g = self.maps[position]
        
        # dim(ker(g))
        _, S_g, _ = np.linalg.svd(g)
        ker_g_dim = self.spaces[position] - np.sum(S_g > 1e-10)
        
        # dim(im(f))
        im_f_dim = np.linalg.matrix_rank(f)
        
        return int(ker_g_dim - im_f_dim)


@dataclass
class ShortExactSequence:
    """
    Short exact sequence: 0 → A →^f B →^g C → 0
    
    Exactness means:
    - f is injective (ker(f) = 0)
    - g is surjective (im(g) = C)
    - im(f) = ker(g)
    """
    dim_A: int
    dim_B: int
    dim_C: int
    f: NDArray[np.float64]  # A → B
    g: NDArray[np.float64]  # B → C
    
    def is_exact(self) -> bool:
        """Verify short exact sequence conditions."""
        # f injective: rank(f) = dim(A)
        if np.linalg.matrix_rank(self.f) != self.dim_A:
            return False
        
        # g surjective: rank(g) = dim(C)
        if np.linalg.matrix_rank(self.g) != self.dim_C:
            return False
        
        # g ∘ f = 0
        if np.max(np.abs(self.g @ self.f)) > 1e-10:
            return False
        
        # Dimension count: dim(A) + dim(C) = dim(B)
        return self.dim_A + self.dim_C == self.dim_B
    
    def splits(self) -> bool:
        """
        Check if sequence splits (B ≅ A ⊕ C).
        
        Always true for vector spaces.
        """
        return True  # Over a field, all SES split
    
    def section(self) -> Optional[NDArray]:
        """
        Find section s: C → B with g ∘ s = id_C.
        """
        # Pseudoinverse gives a section
        return np.linalg.pinv(self.g)
    
    def retraction(self) -> Optional[NDArray]:
        """
        Find retraction r: B → A with r ∘ f = id_A.
        """
        return np.linalg.pinv(self.f)


# ═══════════════════════════════════════════════════════════════════════════════
# SIMPLICIAL HOMOLOGY
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SimplicialComplex:
    """
    Simplicial complex for computing homology.
    """
    vertices: List[int]
    simplices: Dict[int, List[Tuple]]  # dimension → list of simplices
    
    @classmethod
    def from_faces(cls, faces: List[Tuple]) -> 'SimplicialComplex':
        """
        Create simplicial complex from maximal faces.
        
        Automatically includes all sub-faces.
        """
        vertices = set()
        simplices = {}
        
        for face in faces:
            # Add all subsets
            n = len(face)
            for k in range(n + 1):
                if k not in simplices:
                    simplices[k] = []
                
                from itertools import combinations
                for subset in combinations(face, k):
                    if subset not in simplices[k]:
                        simplices[k].append(subset)
                        vertices.update(subset)
        
        return cls(sorted(vertices), simplices)
    
    def boundary_matrix(self, n: int) -> NDArray[np.float64]:
        """
        Boundary matrix ∂_n: C_n → C_{n-1}.
        
        ∂_n([v_0, ..., v_n]) = Σ(-1)^i [v_0, ..., v̂_i, ..., v_n]
        """
        if n <= 0 or n not in self.simplices:
            return np.zeros((1, 1))
        
        n_simplices = self.simplices.get(n, [])
        nm1_simplices = self.simplices.get(n - 1, [])
        
        if not n_simplices or not nm1_simplices:
            return np.zeros((len(nm1_simplices) or 1, len(n_simplices) or 1))
        
        matrix = np.zeros((len(nm1_simplices), len(n_simplices)))
        
        for j, simplex in enumerate(n_simplices):
            for i in range(len(simplex)):
                # Remove i-th vertex
                face = simplex[:i] + simplex[i+1:]
                
                if face in nm1_simplices:
                    k = nm1_simplices.index(face)
                    matrix[k, j] = (-1) ** i
        
        return matrix
    
    def chain_complex(self) -> ChainComplex:
        """Convert to chain complex."""
        max_dim = max(self.simplices.keys())
        
        dims = []
        differentials = []
        
        for n in range(max_dim + 1):
            dims.append(len(self.simplices.get(n, [])))
        
        for n in range(1, max_dim + 1):
            differentials.append(self.boundary_matrix(n))
        
        return ChainComplex(dims, differentials)
    
    def homology(self) -> List[int]:
        """Compute all homology groups (Betti numbers)."""
        return self.chain_complex().betti_numbers()


# ═══════════════════════════════════════════════════════════════════════════════
# DERIVED FUNCTORS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ExtFunctor:
    """
    Ext functor: Ext^n(A, B) measures extensions of A by B.
    
    For vector spaces (R-modules with R a field):
    - Ext^0(A, B) = Hom(A, B)
    - Ext^n(A, B) = 0 for n > 0
    """
    
    @staticmethod
    def ext_dimension(n: int, dim_A: int, dim_B: int) -> int:
        """
        Dimension of Ext^n(A, B) for vector spaces.
        """
        if n == 0:
            return dim_A * dim_B  # dim(Hom(A, B))
        return 0  # Higher Ext vanish for vector spaces
    
    @staticmethod
    def hom_space_basis(dim_A: int, dim_B: int) -> List[NDArray]:
        """
        Basis for Hom(A, B) ≅ M_{B×A}(k).
        """
        basis = []
        for i in range(dim_B):
            for j in range(dim_A):
                E = np.zeros((dim_B, dim_A))
                E[i, j] = 1.0
                basis.append(E)
        return basis


@dataclass
class TorFunctor:
    """
    Tor functor: Tor_n(A, B) measures failure of flatness.
    
    For vector spaces:
    - Tor_0(A, B) = A ⊗ B
    - Tor_n(A, B) = 0 for n > 0
    """
    
    @staticmethod
    def tor_dimension(n: int, dim_A: int, dim_B: int) -> int:
        """
        Dimension of Tor_n(A, B) for vector spaces.
        """
        if n == 0:
            return dim_A * dim_B  # dim(A ⊗ B)
        return 0


# ═══════════════════════════════════════════════════════════════════════════════
# HYBRID STATE HOMOLOGY
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class HybridStateComplex:
    """
    Chain complex structure on hybrid states.
    
    C_n = states with n active poles
    ∂: C_n → C_{n-1} "forgets" one pole
    """
    
    @staticmethod
    def pole_complex() -> ChainComplex:
        """
        Chain complex for quad-polar structure.
        
        C_4 = {D ∧ Ω ∧ Σ ∧ Ψ}         dim = 1
        C_3 = {3-pole states}          dim = 4
        C_2 = {2-pole states}          dim = 6
        C_1 = {single pole states}     dim = 4
        C_0 = {vacuum}                 dim = 1
        """
        # Dimensions from binomial coefficients
        dims = [1, 4, 6, 4, 1]
        
        # Boundary maps (simplicial)
        # ∂_1: C_1 → C_0 (all to vacuum)
        d1 = np.ones((1, 4))
        
        # ∂_2: C_2 → C_1 (each 2-face has 2 edges)
        d2 = np.array([
            [1, 1, 1, 0, 0, 0],
            [1, 0, 0, 1, 1, 0],
            [0, 1, 0, 1, 0, 1],
            [0, 0, 1, 0, 1, 1]
        ], dtype=np.float64)
        
        # ∂_3: C_3 → C_2
        d3 = np.array([
            [1, 1, 0, 0],
            [1, 0, 1, 0],
            [0, 1, 1, 0],
            [1, 0, 0, 1],
            [0, 1, 0, 1],
            [0, 0, 1, 1]
        ], dtype=np.float64)
        
        # ∂_4: C_4 → C_3
        d4 = np.ones((4, 1))
        
        return ChainComplex(dims, [d1, d2, d3, d4])
    
    @staticmethod
    def homology_interpretation() -> Dict[int, str]:
        """Physical interpretation of homology groups."""
        return {
            0: "Connected components of state space",
            1: "Cycles without spanning 2-cells",
            2: "2D voids in state space",
            3: "3D cavities (tetrahedral holes)"
        }


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def chain_complex(dims: List[int], 
                 differentials: List[NDArray]) -> ChainComplex:
    """Create chain complex."""
    return ChainComplex(dims, differentials)


def simplicial_complex(*faces) -> SimplicialComplex:
    """Create simplicial complex from maximal faces."""
    return SimplicialComplex.from_faces(list(faces))


def betti_numbers(complex: ChainComplex) -> List[int]:
    """Compute Betti numbers."""
    return complex.betti_numbers()


def euler_characteristic(complex: ChainComplex) -> int:
    """Compute Euler characteristic."""
    return complex.euler_characteristic()


def is_exact(sequence: ExactSequence) -> bool:
    """Check if sequence is exact."""
    return sequence.is_exact()


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Chain complexes
    'ChainComplex',
    
    # Exact sequences
    'ExactSequence',
    'ShortExactSequence',
    
    # Simplicial
    'SimplicialComplex',
    
    # Derived functors
    'ExtFunctor',
    'TorFunctor',
    
    # Hybrid states
    'HybridStateComplex',
    
    # Functions
    'chain_complex',
    'simplicial_complex',
    'betti_numbers',
    'euler_characteristic',
    'is_exact',
]
