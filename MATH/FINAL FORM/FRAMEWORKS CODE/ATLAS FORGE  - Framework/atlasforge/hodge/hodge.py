"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                          HODGE THEORY MODULE                                 ║
║                                                                              ║
║  Pure and Mixed Hodge Structures, Period Maps, Variations                    ║
║                                                                              ║
║  Core Principle:                                                             ║
║    Hodge theory relates topology and complex geometry:                       ║
║    H^n(X, ℂ) = ⊕_{p+q=n} H^{p,q}(X)                                        ║
║    with H^{p,q} = H^{q,p} (conjugation symmetry)                            ║
║                                                                              ║
║  Connection to Framework:                                                    ║
║    - C-pole ↔ Hodge decomposition (continuous structure)                    ║
║    - Ψ-pole ↔ Weight filtration (hierarchical)                              ║
║    - Gateway ↔ Period domain (hyperbolic geometry)                          ║
║    - D-pole ↔ Lattice structure (discrete)                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Any, Callable
from enum import Enum
import numpy as np
from numpy.typing import NDArray


# ═══════════════════════════════════════════════════════════════════════════════
# PURE HODGE STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class HodgeNumbers:
    """
    Hodge numbers h^{p,q} of a complex manifold.
    """
    numbers: Dict[Tuple[int, int], int]  # (p, q) → h^{p,q}
    
    def __getitem__(self, pq: Tuple[int, int]) -> int:
        return self.numbers.get(pq, 0)
    
    def dimension(self, n: int) -> int:
        """Dimension of H^n = Σ_{p+q=n} h^{p,q}."""
        return sum(h for (p, q), h in self.numbers.items() if p + q == n)
    
    @property
    def euler_characteristic(self) -> int:
        """χ = Σ (-1)^{p+q} h^{p,q}."""
        return sum((-1)**(p+q) * h for (p, q), h in self.numbers.items())
    
    def hodge_symmetry_check(self) -> bool:
        """Verify h^{p,q} = h^{q,p}."""
        for (p, q), h in self.numbers.items():
            if self.numbers.get((q, p), 0) != h:
                return False
        return True
    
    @classmethod
    def curve(cls, g: int) -> 'HodgeNumbers':
        """Hodge numbers of curve of genus g."""
        return cls({(0, 0): 1, (1, 0): g, (0, 1): g, (1, 1): 1})
    
    @classmethod
    def surface(cls, h_dict: Dict[Tuple[int, int], int]) -> 'HodgeNumbers':
        """Hodge numbers of a surface."""
        return cls(h_dict)
    
    @classmethod
    def projective_space(cls, n: int) -> 'HodgeNumbers':
        """Hodge numbers of P^n: h^{p,p} = 1 for 0 ≤ p ≤ n."""
        return cls({(p, p): 1 for p in range(n + 1)})


@dataclass
class PureHodgeStructure:
    """
    Pure Hodge structure of weight n.
    
    A ℤ-lattice H_ℤ with H_ℂ = H_ℤ ⊗ ℂ = ⊕_{p+q=n} H^{p,q}
    satisfying H^{p,q} = conjugate(H^{q,p}).
    """
    weight: int
    lattice_rank: int
    hodge_filtration: List[int]  # dim F^p for p = 0, 1, ..., n
    
    def dimension(self) -> int:
        return self.lattice_rank
    
    def hodge_numbers(self) -> Dict[Tuple[int, int], int]:
        """Compute h^{p,q} from filtration."""
        n = self.weight
        result = {}
        for p in range(n + 1):
            q = n - p
            # h^{p,q} = dim F^p / F^{p+1}
            fp = self.hodge_filtration[p] if p < len(self.hodge_filtration) else 0
            fp1 = self.hodge_filtration[p + 1] if p + 1 < len(self.hodge_filtration) else 0
            result[(p, q)] = fp - fp1
        return result
    
    def polarization_signature(self) -> Tuple[int, int]:
        """
        Signature of polarization form Q on H_ℝ.
        """
        # For weight n, Q has signature determined by Hodge numbers
        h = self.hodge_numbers()
        pos = sum(h.get((p, self.weight - p), 0) for p in range(0, self.weight + 1, 2))
        neg = sum(h.get((p, self.weight - p), 0) for p in range(1, self.weight + 1, 2))
        return (pos, neg)
    
    @classmethod
    def h1_curve(cls, g: int) -> 'PureHodgeStructure':
        """H^1 of curve of genus g."""
        return cls(weight=1, lattice_rank=2*g, hodge_filtration=[2*g, g, 0])
    
    @classmethod
    def tate(cls, n: int) -> 'PureHodgeStructure':
        """Tate Hodge structure ℤ(n)."""
        return cls(weight=-2*n, lattice_rank=1, hodge_filtration=[1, 0])


# ═══════════════════════════════════════════════════════════════════════════════
# MIXED HODGE STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class MixedHodgeStructure:
    """
    Mixed Hodge structure.
    
    - Weight filtration W_• on H_ℚ (increasing)
    - Hodge filtration F^• on H_ℂ (decreasing)
    
    such that F^• induces pure Hodge structure on gr^W_k.
    """
    weight_filtration: Dict[int, int]  # k → dim W_k
    hodge_filtration: Dict[int, int]   # p → dim F^p
    total_dimension: int
    
    def graded_weight(self, k: int) -> int:
        """dim gr^W_k = dim W_k / W_{k-1}."""
        wk = self.weight_filtration.get(k, 0)
        wk1 = self.weight_filtration.get(k - 1, 0)
        return wk - wk1
    
    def weights_present(self) -> List[int]:
        """List of weights k where gr^W_k ≠ 0."""
        return [k for k in sorted(self.weight_filtration.keys()) 
                if self.graded_weight(k) > 0]
    
    def is_pure(self) -> bool:
        """Check if MHS is actually pure (single weight)."""
        weights = self.weights_present()
        return len(weights) == 1
    
    @classmethod
    def of_punctured_curve(cls, g: int, n: int) -> 'MixedHodgeStructure':
        """
        H^1 of curve of genus g with n punctures.
        Weights 1 and 2 appear.
        """
        # Weight 1: H^1 of compact curve
        # Weight 2: from punctures
        return cls(
            weight_filtration={1: 2*g, 2: 2*g + n - 1},
            hodge_filtration={0: 2*g + n - 1, 1: g + n - 1, 2: 0},
            total_dimension=2*g + n - 1
        )


# ═══════════════════════════════════════════════════════════════════════════════
# PERIOD DOMAINS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class PeriodDomain:
    """
    Period domain D classifying Hodge structures of given type.
    
    D = G(ℝ) / V where G is algebraic group, V is compact subgroup.
    
    For weight 1 curves: D = Siegel upper half space 𝔥_g.
    """
    hodge_numbers: Dict[Tuple[int, int], int]
    weight: int
    
    @property
    def dimension(self) -> int:
        """Complex dimension of period domain."""
        # For weight n, dim = Σ_{p<q} h^{p,q} h^{q,p}
        total = 0
        for (p, q), h in self.hodge_numbers.items():
            if p < q:
                h_conj = self.hodge_numbers.get((q, p), 0)
                total += h * h_conj
        return total
    
    def is_hermitian_symmetric(self) -> bool:
        """Check if D is a Hermitian symmetric domain."""
        # True for curves (Siegel), some surfaces (Type IV)
        return self.weight <= 2
    
    @classmethod
    def siegel(cls, g: int) -> 'PeriodDomain':
        """Siegel upper half space 𝔥_g for curves of genus g."""
        return cls(
            hodge_numbers={(1, 0): g, (0, 1): g},
            weight=1
        )


@dataclass
class PeriodMap:
    """
    Period map from moduli to period domain.
    
    Φ: M_g → 𝔥_g / Sp(2g, ℤ)
    
    (Griffiths) The period map is holomorphic and horizontal.
    """
    source_name: str  # Moduli space
    target_domain: PeriodDomain
    monodromy_group: str = "Sp(2g, ℤ)"
    
    def horizontality(self) -> str:
        """Griffiths transversality: dΦ(T) ⊂ T^{-1,1} D."""
        return f"dΦ: T_{{{self.source_name}}} → T^{{-1,1}} D"
    
    def torelli_theorem(self) -> str:
        """Torelli: period map is injective (for curves)."""
        return f"Φ: {self.source_name} ↪ D / Γ is injective"


# ═══════════════════════════════════════════════════════════════════════════════
# VARIATIONS OF HODGE STRUCTURE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class VariationOfHodgeStructure:
    """
    Variation of Hodge structure (VHS) over a base S.
    
    A local system H_ℤ with Hodge filtration F^• varying holomorphically.
    
    Griffiths transversality: ∇F^p ⊂ F^{p-1} ⊗ Ω^1_S.
    """
    base_name: str
    weight: int
    rank: int
    
    def connection(self) -> str:
        """Gauss-Manin connection ∇."""
        return f"∇: H → H ⊗ Ω^1_{{{self.base_name}}}"
    
    def griffiths_transversality(self) -> str:
        """Transversality condition."""
        return f"∇(F^p) ⊂ F^{{p-1}} ⊗ Ω^1"
    
    def monodromy_representation(self) -> str:
        """π_1(S) → GL(H_ℤ)."""
        return f"ρ: π_1({self.base_name}) → GL_{{{self.rank}}}(ℤ)"
    
    @classmethod
    def universal_curve(cls, g: int) -> 'VariationOfHodgeStructure':
        """VHS from universal curve over M_g."""
        return cls(base_name=f"M_{g}", weight=1, rank=2*g)


@dataclass
class HodgeBundle:
    """
    Hodge bundle F^p on a base with VHS.
    """
    filtration_level: int  # p
    vhs: VariationOfHodgeStructure
    
    @property
    def rank(self) -> int:
        """Rank of F^p."""
        # Would depend on Hodge numbers
        return self.vhs.rank // 2
    
    def chern_class(self) -> str:
        """First Chern class c_1(F^p)."""
        return f"c_1(F^{{{self.filtration_level}}})"


# ═══════════════════════════════════════════════════════════════════════════════
# DELIGNE COHOMOLOGY
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class DeligneCohomology:
    """
    Deligne cohomology H^n_D(X, ℤ(p)).
    
    Fits in exact sequence:
    0 → J^p(X) → H^n_D(X, ℤ(p)) → H^n(X, ℤ) ∩ F^p → 0
    
    where J^p is the intermediate Jacobian.
    """
    variety_name: str
    
    def H_D(self, n: int, p: int) -> str:
        """Deligne cohomology group."""
        return f"H^{n}_D({self.variety_name}, ℤ({p}))"
    
    def chern_class_map(self, p: int) -> str:
        """Chern class in Deligne cohomology."""
        return f"c_{{p}}: K_0({self.variety_name}) → H^{{2p}}_D({self.variety_name}, ℤ({p}))"
    
    def intermediate_jacobian(self, n: int) -> str:
        """J^n(X) = F^n H^{2n-1} \\\\ H^{2n-1}_ℂ / H^{2n-1}_ℤ."""
        return f"J^{{{n}}}({self.variety_name})"
    
    def abel_jacobi_map(self) -> str:
        """Abel-Jacobi map from cycles to intermediate Jacobian."""
        return f"AJ: Z^p({self.variety_name})_hom → J^p({self.variety_name})"


# ═══════════════════════════════════════════════════════════════════════════════
# POLE BRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class HodgePoleBridge:
    """
    Bridge between Hodge theory and pole structure.
    """
    
    @staticmethod
    def c_pole_as_hodge_decomposition() -> str:
        """
        C-pole corresponds to Hodge decomposition.
        Continuous splitting H = ⊕ H^{p,q}.
        """
        return "C ↔ Hodge: H^n = ⊕_{p+q=n} H^{p,q} continuous structure"
    
    @staticmethod
    def psi_pole_as_weight_filtration() -> str:
        """
        Ψ-pole corresponds to weight filtration.
        Hierarchical W_k ⊂ W_{k+1}.
        """
        return "Ψ ↔ Weight: W_0 ⊂ W_1 ⊂ ... hierarchical filtration"
    
    @staticmethod
    def gateway_as_period_domain() -> str:
        """
        Gateway corresponds to period domain.
        Hyperbolic geometry of Siegel space.
        """
        return "Gateway ↔ Period: 𝔥_g = Sp(2g,ℝ)/U(g) hyperbolic"
    
    @staticmethod
    def d_pole_as_lattice() -> str:
        """
        D-pole corresponds to integral lattice.
        Discrete structure H_ℤ ⊂ H.
        """
        return "D ↔ Lattice: H_ℤ discrete subgroup"
    
    @staticmethod
    def vhs_unifies_poles() -> str:
        """
        Variation of Hodge Structure unifies all poles.
        """
        return """VHS Unity:
  • C-pole: Hodge filtration F^• varies holomorphically
  • Ψ-pole: Weight filtration W_• is constant
  • D-pole: Local system H_ℤ (discrete)
  • Gateway: Period map Φ: S → D"""


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def hodge_numbers(h_dict: Dict[Tuple[int, int], int]) -> HodgeNumbers:
    """Create Hodge numbers from dictionary."""
    return HodgeNumbers(h_dict)


def pure_hodge(weight: int, rank: int, filtration: List[int]) -> PureHodgeStructure:
    """Create pure Hodge structure."""
    return PureHodgeStructure(weight, rank, filtration)


def mixed_hodge(weight_filt: Dict[int, int], hodge_filt: Dict[int, int],
                dim: int) -> MixedHodgeStructure:
    """Create mixed Hodge structure."""
    return MixedHodgeStructure(weight_filt, hodge_filt, dim)


def period_domain(h_numbers: Dict[Tuple[int, int], int], 
                  weight: int) -> PeriodDomain:
    """Create period domain."""
    return PeriodDomain(h_numbers, weight)


def vhs(base: str, weight: int, rank: int) -> VariationOfHodgeStructure:
    """Create variation of Hodge structure."""
    return VariationOfHodgeStructure(base, weight, rank)


def deligne_cohomology(variety: str) -> DeligneCohomology:
    """Create Deligne cohomology object."""
    return DeligneCohomology(variety)


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Pure Hodge
    'HodgeNumbers',
    'PureHodgeStructure',
    
    # Mixed Hodge
    'MixedHodgeStructure',
    
    # Period domains
    'PeriodDomain',
    'PeriodMap',
    
    # Variations
    'VariationOfHodgeStructure',
    'HodgeBundle',
    
    # Deligne
    'DeligneCohomology',
    
    # Bridge
    'HodgePoleBridge',
    
    # Functions
    'hodge_numbers',
    'pure_hodge',
    'mixed_hodge',
    'period_domain',
    'vhs',
    'deligne_cohomology',
]
