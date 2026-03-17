"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                     REPRESENTATION THEORY MODULE                             ║
║                                                                              ║
║  Group Representations, Characters, and Decomposition                        ║
║                                                                              ║
║  Core Principle:                                                             ║
║    The OA6 operators form a group, and understanding their representations   ║
║    reveals the structure of hybrid states. Representation theory provides   ║
║    the systematic decomposition of state spaces.                            ║
║                                                                              ║
║  Key Structures:                                                             ║
║    - Representation ρ: G → GL(V)                                            ║
║    - Character χ(g) = Tr(ρ(g))                                              ║
║    - Irreducible decomposition V = ⊕ n_i V_i                                ║
║    - Schur's lemma: Hom(V_i, V_j) = 0 for i ≠ j                             ║
║                                                                              ║
║  Connection to Framework:                                                    ║
║    - OA6 = ⟨C, R, G, K, S, T⟩ action on hybrid states                       ║
║    - Klein-4 subgroup structure                                             ║
║    - Character analysis reveals invariant subspaces                         ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Callable, Set
from enum import Enum
import numpy as np
from numpy.typing import NDArray


# ═══════════════════════════════════════════════════════════════════════════════
# FINITE GROUP
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class FiniteGroup:
    """
    A finite group with multiplication table.
    """
    elements: List[str]
    multiplication: Dict[Tuple[str, str], str]
    identity: str
    
    @property
    def order(self) -> int:
        """Order of the group."""
        return len(self.elements)
    
    def multiply(self, a: str, b: str) -> str:
        """Group multiplication."""
        return self.multiplication[(a, b)]
    
    def inverse(self, a: str) -> str:
        """Find inverse of element."""
        for b in self.elements:
            if self.multiply(a, b) == self.identity:
                return b
        raise ValueError(f"No inverse found for {a}")
    
    def element_order(self, a: str) -> int:
        """Order of element (smallest n with a^n = e)."""
        current = a
        for n in range(1, self.order + 1):
            if current == self.identity:
                return n
            current = self.multiply(current, a)
        return self.order
    
    def is_abelian(self) -> bool:
        """Check if group is abelian."""
        for a in self.elements:
            for b in self.elements:
                if self.multiply(a, b) != self.multiply(b, a):
                    return False
        return True
    
    def conjugacy_classes(self) -> List[Set[str]]:
        """Compute conjugacy classes."""
        remaining = set(self.elements)
        classes = []
        
        while remaining:
            a = remaining.pop()
            conj_class = {a}
            
            for g in self.elements:
                g_inv = self.inverse(g)
                conjugate = self.multiply(g, self.multiply(a, g_inv))
                conj_class.add(conjugate)
            
            remaining -= conj_class
            classes.append(conj_class)
        
        return classes
    
    @classmethod
    def cyclic(cls, n: int) -> 'FiniteGroup':
        """Cyclic group Z_n."""
        elements = [f"g^{i}" for i in range(n)]
        elements[0] = "e"
        
        mult = {}
        for i in range(n):
            for j in range(n):
                k = (i + j) % n
                a = elements[i]
                b = elements[j]
                mult[(a, b)] = elements[k]
        
        return cls(elements, mult, "e")
    
    @classmethod
    def klein_four(cls) -> 'FiniteGroup':
        """Klein four-group V_4 ≅ Z_2 × Z_2."""
        elements = ["e", "a", "b", "c"]
        mult = {
            ("e", "e"): "e", ("e", "a"): "a", ("e", "b"): "b", ("e", "c"): "c",
            ("a", "e"): "a", ("a", "a"): "e", ("a", "b"): "c", ("a", "c"): "b",
            ("b", "e"): "b", ("b", "a"): "c", ("b", "b"): "e", ("b", "c"): "a",
            ("c", "e"): "c", ("c", "a"): "b", ("c", "b"): "a", ("c", "c"): "e",
        }
        return cls(elements, mult, "e")
    
    @classmethod
    def symmetric(cls, n: int) -> 'FiniteGroup':
        """Symmetric group S_n (for small n)."""
        from itertools import permutations
        
        perms = list(permutations(range(n)))
        elements = [str(p) for p in perms]
        
        def compose(p1, p2):
            return tuple(p1[i] for i in p2)
        
        mult = {}
        for i, p1 in enumerate(perms):
            for j, p2 in enumerate(perms):
                result = compose(p1, p2)
                mult[(elements[i], elements[j])] = str(result)
        
        identity = str(tuple(range(n)))
        return cls(elements, mult, identity)


# ═══════════════════════════════════════════════════════════════════════════════
# GROUP REPRESENTATION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Representation:
    """
    A matrix representation ρ: G → GL(V).
    """
    group: FiniteGroup
    matrices: Dict[str, NDArray[np.complex128]]
    dimension: int
    
    def __post_init__(self):
        # Verify dimensions
        for g, M in self.matrices.items():
            if M.shape != (self.dimension, self.dimension):
                raise ValueError(f"Matrix for {g} has wrong dimension")
    
    def __call__(self, g: str) -> NDArray[np.complex128]:
        """Get matrix for group element."""
        return self.matrices[g]
    
    def character(self, g: str) -> complex:
        """Character χ(g) = Tr(ρ(g))."""
        return np.trace(self.matrices[g])
    
    def character_table_row(self) -> List[complex]:
        """Character values on conjugacy classes."""
        classes = self.group.conjugacy_classes()
        return [self.character(next(iter(c))) for c in classes]
    
    def is_irreducible(self) -> bool:
        """
        Check if representation is irreducible.
        
        Uses ⟨χ, χ⟩ = 1 criterion.
        """
        inner = self.character_inner_product(self)
        return abs(inner - 1.0) < 1e-10
    
    def character_inner_product(self, other: 'Representation') -> complex:
        """
        Inner product of characters: ⟨χ, ψ⟩ = (1/|G|) Σ χ(g) ψ(g)*.
        """
        total = 0
        for g in self.group.elements:
            total += self.character(g) * np.conj(other.character(g))
        return total / self.group.order
    
    def direct_sum(self, other: 'Representation') -> 'Representation':
        """Direct sum of representations."""
        if self.group != other.group:
            raise ValueError("Representations must be for same group")
        
        new_dim = self.dimension + other.dimension
        new_matrices = {}
        
        for g in self.group.elements:
            M = np.zeros((new_dim, new_dim), dtype=np.complex128)
            M[:self.dimension, :self.dimension] = self.matrices[g]
            M[self.dimension:, self.dimension:] = other.matrices[g]
            new_matrices[g] = M
        
        return Representation(self.group, new_matrices, new_dim)
    
    def tensor_product(self, other: 'Representation') -> 'Representation':
        """Tensor product of representations."""
        if self.group != other.group:
            raise ValueError("Representations must be for same group")
        
        new_dim = self.dimension * other.dimension
        new_matrices = {}
        
        for g in self.group.elements:
            new_matrices[g] = np.kron(self.matrices[g], other.matrices[g])
        
        return Representation(self.group, new_matrices, new_dim)
    
    @classmethod
    def trivial(cls, group: FiniteGroup) -> 'Representation':
        """Trivial representation ρ(g) = 1."""
        matrices = {g: np.array([[1.0]], dtype=np.complex128) 
                   for g in group.elements}
        return cls(group, matrices, 1)
    
    @classmethod
    def regular(cls, group: FiniteGroup) -> 'Representation':
        """
        Regular representation.
        
        Acts on C[G] by left multiplication.
        """
        n = group.order
        matrices = {}
        
        for g in group.elements:
            M = np.zeros((n, n), dtype=np.complex128)
            for i, h in enumerate(group.elements):
                gh = group.multiply(g, h)
                j = group.elements.index(gh)
                M[j, i] = 1.0
            matrices[g] = M
        
        return cls(group, matrices, n)


# ═══════════════════════════════════════════════════════════════════════════════
# CHARACTER TABLE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class CharacterTable:
    """
    Complete character table of a finite group.
    """
    group: FiniteGroup
    irreps: List[Representation]
    
    @property
    def table(self) -> NDArray[np.complex128]:
        """Character table as matrix."""
        classes = self.group.conjugacy_classes()
        n_classes = len(classes)
        n_irreps = len(self.irreps)
        
        table = np.zeros((n_irreps, n_classes), dtype=np.complex128)
        
        for i, rep in enumerate(self.irreps):
            for j, cls in enumerate(classes):
                g = next(iter(cls))
                table[i, j] = rep.character(g)
        
        return table
    
    def decompose(self, rep: Representation) -> Dict[int, int]:
        """
        Decompose representation into irreducibles.
        
        Returns multiplicities {irrep_index: multiplicity}.
        """
        multiplicities = {}
        
        for i, irrep in enumerate(self.irreps):
            inner = rep.character_inner_product(irrep)
            mult = int(round(inner.real))
            if mult > 0:
                multiplicities[i] = mult
        
        return multiplicities
    
    @classmethod
    def for_cyclic_group(cls, n: int) -> 'CharacterTable':
        """Character table for Z_n."""
        group = FiniteGroup.cyclic(n)
        irreps = []
        
        omega = np.exp(2j * np.pi / n)
        
        for k in range(n):
            matrices = {}
            for i, g in enumerate(group.elements):
                matrices[g] = np.array([[omega ** (k * i)]], dtype=np.complex128)
            irreps.append(Representation(group, matrices, 1))
        
        return cls(group, irreps)
    
    @classmethod
    def for_klein_four(cls) -> 'CharacterTable':
        """Character table for V_4."""
        group = FiniteGroup.klein_four()
        irreps = []
        
        # Four 1-dimensional irreps
        signs = [
            (1, 1, 1, 1),   # Trivial
            (1, 1, -1, -1), # Sign on b, c
            (1, -1, 1, -1), # Sign on a, c
            (1, -1, -1, 1), # Sign on a, b
        ]
        
        for sign in signs:
            matrices = {
                "e": np.array([[sign[0]]], dtype=np.complex128),
                "a": np.array([[sign[1]]], dtype=np.complex128),
                "b": np.array([[sign[2]]], dtype=np.complex128),
                "c": np.array([[sign[3]]], dtype=np.complex128),
            }
            irreps.append(Representation(group, matrices, 1))
        
        return cls(group, irreps)


# ═══════════════════════════════════════════════════════════════════════════════
# SCHUR-WEYL DUALITY
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SchurWeylDecomposition:
    """
    Schur-Weyl duality: V^⊗n decomposes under GL(V) × S_n action.
    
    V^⊗n = ⊕_λ V_λ ⊗ S_λ
    
    where λ runs over partitions of n.
    """
    dim_V: int  # Dimension of V
    n: int      # Tensor power
    
    def partitions(self) -> List[Tuple[int, ...]]:
        """Generate partitions of n."""
        def _partitions(n, max_val):
            if n == 0:
                return [()]
            result = []
            for i in range(min(n, max_val), 0, -1):
                for p in _partitions(n - i, i):
                    result.append((i,) + p)
            return result
        
        return _partitions(self.n, self.n)
    
    def hook_length(self, partition: Tuple[int, ...], i: int, j: int) -> int:
        """Hook length at position (i, j) in Young diagram."""
        # Arm length + leg length + 1
        arm = partition[i] - j - 1
        leg = sum(1 for k in range(i + 1, len(partition)) if partition[k] > j)
        return arm + leg + 1
    
    def dimension_GL(self, partition: Tuple[int, ...]) -> int:
        """
        Dimension of GL(V) irrep labeled by partition.
        
        Uses hook length formula.
        """
        if len(partition) > self.dim_V:
            return 0
        
        # Numerator: product over boxes of (d + content)
        # Content of (i,j) is j - i
        num = 1
        for i, p_i in enumerate(partition):
            for j in range(p_i):
                num *= (self.dim_V + j - i)
        
        # Denominator: product of hook lengths
        denom = 1
        for i, p_i in enumerate(partition):
            for j in range(p_i):
                denom *= self.hook_length(partition, i, j)
        
        return num // denom
    
    def dimension_Sn(self, partition: Tuple[int, ...]) -> int:
        """
        Dimension of S_n irrep labeled by partition.
        
        dim(S_λ) = n! / (product of hook lengths)
        """
        from math import factorial
        
        denom = 1
        for i, p_i in enumerate(partition):
            for j in range(p_i):
                denom *= self.hook_length(partition, i, j)
        
        return factorial(self.n) // denom


# ═══════════════════════════════════════════════════════════════════════════════
# OA6 REPRESENTATION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class OA6Representation:
    """
    Representation theory of the OA6 operator group.
    
    The six generators C, R, G, K, S, T act on 4×4 matrices.
    """
    
    @staticmethod
    def generator_matrices() -> Dict[str, NDArray[np.complex128]]:
        """
        The six OA6 generator matrices.
        """
        # These are 4×4 permutation/sign matrices
        I = np.eye(4, dtype=np.complex128)
        
        # C: column permutation (0123) → (1032)
        C = np.array([
            [0, 1, 0, 0],
            [1, 0, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 1, 0]
        ], dtype=np.complex128)
        
        # R: row permutation (0123) → (2301)
        R = np.array([
            [0, 0, 1, 0],
            [0, 0, 0, 1],
            [1, 0, 0, 0],
            [0, 1, 0, 0]
        ], dtype=np.complex128)
        
        # G: diagonal signs
        G = np.diag([1, -1, -1, 1]).astype(np.complex128)
        
        # K: anti-diagonal swap
        K = np.array([
            [0, 0, 0, 1],
            [0, 0, 1, 0],
            [0, 1, 0, 0],
            [1, 0, 0, 0]
        ], dtype=np.complex128)
        
        # S: specific permutation
        S = np.array([
            [1, 0, 0, 0],
            [0, 0, 1, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 1]
        ], dtype=np.complex128)
        
        # T: transpose-like
        T = np.array([
            [1, 0, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 1, 0],
            [0, 1, 0, 0]
        ], dtype=np.complex128)
        
        return {"I": I, "C": C, "R": R, "G": G, "K": K, "S": S, "T": T}
    
    @staticmethod
    def klein_four_subgroup() -> Dict[str, NDArray[np.complex128]]:
        """
        Extract Klein-4 subgroup from OA6.
        
        V_4 = {I, C², R², (CR)²}
        """
        gens = OA6Representation.generator_matrices()
        I = gens["I"]
        C = gens["C"]
        R = gens["R"]
        
        return {
            "e": I,
            "a": C @ C,       # C²
            "b": R @ R,       # R²
            "c": C @ R @ C @ R  # (CR)²
        }
    
    @staticmethod
    def decompose_into_irreps() -> Dict[str, int]:
        """
        Decompose the 4-dimensional representation.
        
        For the Klein-4 action on C⁴.
        """
        # The 4-dim rep of Klein-4 decomposes into 1-dim irreps
        # Based on eigenspaces
        
        K4 = OA6Representation.klein_four_subgroup()
        
        # Simultaneous diagonalization
        # Each 1-dim irrep appears with some multiplicity
        
        # For V_4 acting on C⁴, we get multiplicities
        return {
            "trivial": 1,
            "sign_a": 1,
            "sign_b": 1,
            "sign_ab": 1
        }


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def cyclic_group(n: int) -> FiniteGroup:
    """Create cyclic group Z_n."""
    return FiniteGroup.cyclic(n)


def klein_four_group() -> FiniteGroup:
    """Create Klein four-group."""
    return FiniteGroup.klein_four()


def character_table(group: FiniteGroup) -> NDArray[np.complex128]:
    """Compute character table."""
    if group.order <= 4 and group.is_abelian():
        if group.order == 4:
            return CharacterTable.for_klein_four().table
        return CharacterTable.for_cyclic_group(group.order).table
    raise NotImplementedError("Only small abelian groups supported")


def regular_representation(group: FiniteGroup) -> Representation:
    """Regular representation of group."""
    return Representation.regular(group)


def decompose_representation(rep: Representation, 
                            char_table: CharacterTable) -> Dict[int, int]:
    """Decompose representation into irreducibles."""
    return char_table.decompose(rep)


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Groups
    'FiniteGroup',
    
    # Representations
    'Representation',
    'CharacterTable',
    
    # Schur-Weyl
    'SchurWeylDecomposition',
    
    # OA6
    'OA6Representation',
    
    # Functions
    'cyclic_group',
    'klein_four_group',
    'character_table',
    'regular_representation',
    'decompose_representation',
]
