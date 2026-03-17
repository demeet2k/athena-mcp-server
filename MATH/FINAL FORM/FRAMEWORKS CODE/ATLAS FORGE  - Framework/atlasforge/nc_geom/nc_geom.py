"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    NONCOMMUTATIVE GEOMETRY MODULE                            ║
║                                                                              ║
║  Spectral Triples, Cyclic Cohomology, and Connes' Program                   ║
║                                                                              ║
║  Core Principle:                                                             ║
║    Replace commutative algebra C(X) with noncommutative A:                  ║
║    Geometry encoded in spectral triple (A, H, D)                            ║
║                                                                              ║
║  Connection to Framework:                                                    ║
║    - C-pole ↔ Dirac operator D (differential structure)                     ║
║    - Ψ-pole ↔ Spectral dimension (hierarchical scales)                      ║
║    - Σ-pole ↔ Quantum statistics (noncommutativity)                         ║
║    - D-pole ↔ K-theory classes (discrete invariants)                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Any, Callable
from enum import Enum
import numpy as np
from numpy.typing import NDArray


# ═══════════════════════════════════════════════════════════════════════════════
# NONCOMMUTATIVE ALGEBRAS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class NoncommutativeAlgebra:
    """
    Noncommutative *-algebra A.
    
    Replaces C(X) in classical geometry.
    Key examples: M_n(ℂ), C*-algebras, quantum groups.
    """
    name: str
    is_unital: bool = True
    is_star_algebra: bool = True  # Has involution *
    
    def commutator(self, a: str, b: str) -> str:
        """[a, b] = ab - ba."""
        return f"[{a}, {b}]"
    
    def anticommutator(self, a: str, b: str) -> str:
        """{a, b} = ab + ba."""
        return f"{{{a}, {b}}}"
    
    @classmethod
    def matrix_algebra(cls, n: int) -> 'NoncommutativeAlgebra':
        """M_n(ℂ) - n×n matrices."""
        return cls(f"M_{n}(ℂ)", is_unital=True, is_star_algebra=True)
    
    @classmethod
    def weyl_algebra(cls, n: int = 1) -> 'NoncommutativeAlgebra':
        """Weyl algebra A_n: [q_i, p_j] = iℏδ_{ij}."""
        return cls(f"A_{n}", is_unital=True, is_star_algebra=False)
    
    @classmethod
    def noncommutative_torus(cls, theta: float) -> 'NoncommutativeAlgebra':
        """NC torus A_θ: UV = e^{2πiθ} VU."""
        return cls(f"A_θ (θ={theta:.4f})", is_unital=True, is_star_algebra=True)


@dataclass
class CStarAlgebra(NoncommutativeAlgebra):
    """
    C*-algebra: Banach *-algebra with ||a*a|| = ||a||².
    
    Gelfand-Naimark: Commutative C*-algebras ≅ C_0(X) for locally compact X.
    """
    is_commutative: bool = False
    
    def gelfand_spectrum(self) -> str:
        """Spectrum Â = space of characters (commutative case)."""
        if self.is_commutative:
            return f"Spec({self.name}) = X (locally compact Hausdorff)"
        return f"Spec({self.name}) = noncommutative (no classical space)"
    
    @classmethod
    def compact_operators(cls, H: str = "H") -> 'CStarAlgebra':
        """K(H) - compact operators on Hilbert space."""
        return cls(f"K({H})", is_commutative=False)
    
    @classmethod
    def bounded_operators(cls, H: str = "H") -> 'CStarAlgebra':
        """B(H) - bounded operators on Hilbert space."""
        return cls(f"B({H})", is_commutative=False)


# ═══════════════════════════════════════════════════════════════════════════════
# SPECTRAL TRIPLES
# ═══════════════════════════════════════════════════════════════════════════════

class SpectralTripleType(Enum):
    """Types of spectral triples."""
    COMMUTATIVE = "Commutative (classical manifold)"
    FINITE = "Finite (discrete geometry)"
    PRODUCT = "Product geometry"
    QUANTUM = "Quantum group"
    ALMOST_COMMUTATIVE = "Almost commutative (Standard Model)"


@dataclass
class SpectralTriple:
    """
    Spectral triple (A, H, D).
    
    - A: *-algebra represented on H
    - H: Hilbert space
    - D: Dirac operator (unbounded, self-adjoint)
    
    Axioms:
    1. [D, a] bounded for a ∈ A
    2. (D + i)^{-1} compact (regularity)
    3. Grading γ with γ² = 1, γD = -Dγ (even case)
    """
    algebra: NoncommutativeAlgebra
    hilbert_space_dim: Optional[int] = None  # None for infinite
    triple_type: SpectralTripleType = SpectralTripleType.COMMUTATIVE
    is_even: bool = True  # Has grading γ
    is_real: bool = True  # Has real structure J
    
    def dirac_operator(self) -> str:
        """The Dirac operator D."""
        return f"D: dom(D) ⊂ H → H"
    
    def commutator_condition(self, a: str) -> str:
        """[D, π(a)] must be bounded."""
        return f"||[D, π({a})]|| < ∞"
    
    def resolvent_compact(self) -> str:
        """Compactness of resolvent."""
        return "(D + i)^{-1} ∈ K(H)"
    
    @property
    def spectral_dimension(self) -> str:
        """
        Spectral dimension from Dixmier trace.
        d = inf{p : Tr(|D|^{-p}) < ∞}
        """
        return "d = spectral dimension"
    
    @classmethod
    def spin_manifold(cls, M: str, dim: int) -> 'SpectralTriple':
        """
        Canonical spectral triple of spin manifold.
        (C^∞(M), L²(S), D_M) where D_M is Dirac operator.
        """
        alg = NoncommutativeAlgebra(f"C^∞({M})")
        return cls(
            algebra=alg,
            triple_type=SpectralTripleType.COMMUTATIVE,
            is_even=(dim % 2 == 0)
        )
    
    @classmethod
    def finite(cls, n: int) -> 'SpectralTriple':
        """Finite spectral triple (M_n(ℂ), ℂ^n, D_F)."""
        return cls(
            algebra=NoncommutativeAlgebra.matrix_algebra(n),
            hilbert_space_dim=n,
            triple_type=SpectralTripleType.FINITE
        )
    
    @classmethod
    def standard_model(cls) -> 'SpectralTriple':
        """
        Almost-commutative geometry for Standard Model.
        (C^∞(M) ⊗ A_F, L²(S) ⊗ H_F, D_M ⊗ 1 + γ_5 ⊗ D_F)
        """
        alg = NoncommutativeAlgebra("C^∞(M) ⊗ A_F")
        return cls(
            algebra=alg,
            triple_type=SpectralTripleType.ALMOST_COMMUTATIVE,
            is_even=True,
            is_real=True
        )


@dataclass
class RealStructure:
    """
    Real structure J on spectral triple.
    
    Antilinear isometry J: H → H with:
    - J² = ε
    - JD = ε' DJ
    - Jγ = ε'' γJ (even case)
    
    where ε, ε', ε'' ∈ {±1} depend on KO-dimension mod 8.
    """
    epsilon: int  # ±1
    epsilon_prime: int  # ±1
    epsilon_double_prime: int  # ±1 (even case)
    ko_dimension: int  # 0-7
    
    def signs(self) -> Tuple[int, int, int]:
        """(ε, ε', ε'')."""
        return (self.epsilon, self.epsilon_prime, self.epsilon_double_prime)
    
    @classmethod
    def from_ko_dim(cls, n: int) -> 'RealStructure':
        """Real structure from KO-dimension mod 8."""
        # Standard table of signs
        signs_table = {
            0: (1, 1, 1),
            1: (1, -1, 0),
            2: (-1, 1, 1),
            3: (-1, 1, 0),
            4: (-1, 1, 1),
            5: (-1, -1, 0),
            6: (1, 1, 1),
            7: (1, 1, 0),
        }
        e, ep, epp = signs_table[n % 8]
        return cls(e, ep, epp, n % 8)


# ═══════════════════════════════════════════════════════════════════════════════
# CYCLIC COHOMOLOGY
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class HochschildComplex:
    """
    Hochschild complex C^n(A, A) = Hom(A^⊗n, A).
    
    Boundary: b(φ)(a_0,...,a_n) = Σ (-1)^i φ(...,a_i a_{i+1},...)
    """
    algebra: NoncommutativeAlgebra
    
    def cochain(self, n: int) -> str:
        """C^n(A, A)."""
        return f"C^{n}({self.algebra.name}, {self.algebra.name})"
    
    def boundary(self, n: int) -> str:
        """b: C^n → C^{n+1}."""
        return f"b: C^{n} → C^{{{n+1}}}"
    
    def hochschild_cohomology(self, n: int) -> str:
        """HH^n(A, A) = ker b / im b."""
        return f"HH^{n}({self.algebra.name})"


@dataclass
class CyclicCohomology:
    """
    Cyclic cohomology HC^n(A).
    
    Cyclic cochains: φ(a_1,...,a_n,a_0) = (-1)^n φ(a_0,...,a_n)
    
    Long exact sequence: ... → HH^n → HC^n → HC^{n-2} → HH^{n+1} → ...
    """
    algebra: NoncommutativeAlgebra
    
    def HC(self, n: int) -> str:
        """HC^n(A)."""
        return f"HC^{n}({self.algebra.name})"
    
    def periodicity(self) -> str:
        """Connes periodicity: S: HC^n → HC^{n+2}."""
        return f"S: HC^n → HC^{{n+2}}"
    
    def periodic_cyclic(self) -> str:
        """HP^*(A) = lim HC^{*+2k}."""
        return f"HP^*({self.algebra.name})"
    
    def connes_chern(self) -> str:
        """Chern character ch: K_*(A) → HP^*(A)."""
        return f"ch: K_*({self.algebra.name}) → HP^*({self.algebra.name})"


@dataclass
class ConnesIndex:
    """
    Connes' index theorem for spectral triples.
    
    Ind(D_A) = ⟨[D], [e]⟩ = pairing of K-theory and K-homology
    """
    spectral_triple: SpectralTriple
    
    def index_pairing(self, e: str) -> str:
        """⟨[D], [e]⟩ for projection e."""
        return f"⟨[D], [{e}]⟩ = Ind(P e P : eH → eH)"
    
    def local_index_formula(self) -> str:
        """Connes-Moscovici local index formula."""
        return "Ind(D_A) = φ(ch(e)) where φ = local cyclic cocycle"
    
    def residue_formula(self) -> str:
        """Residue at spectral dimension."""
        return "Res_{s=0} Tr(a |D|^{-s}) = Wres(a)"


# ═══════════════════════════════════════════════════════════════════════════════
# MOYAL PRODUCT AND DEFORMATION QUANTIZATION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class MoyalProduct:
    """
    Moyal star product on ℝ^{2n}.
    
    (f ⋆ g)(x) = exp(iℏ/2 θ^{ij} ∂_i ⊗ ∂_j) f(x) g(y)|_{y=x}
    
    Deformation of pointwise product to noncommutative.
    """
    theta: NDArray[np.float64]  # Antisymmetric matrix θ^{ij}
    hbar: float = 1.0
    
    @property
    def dimension(self) -> int:
        return self.theta.shape[0]
    
    def star_commutator(self, x_i: int, x_j: int) -> str:
        """[x_i, x_j]_⋆ = iℏθ^{ij}."""
        return f"[x_{x_i}, x_{x_j}]_⋆ = i·{self.hbar}·θ^{{{x_i}{x_j}}}"
    
    def weyl_quantization(self) -> str:
        """Weyl quantization map."""
        return "W: (C^∞(ℝ^{2n}), ⋆) → B(L²(ℝ^n))"
    
    @classmethod
    def canonical(cls, n: int, hbar: float = 1.0) -> 'MoyalProduct':
        """Canonical Moyal product: [q_i, p_j] = iℏδ_{ij}."""
        theta = np.zeros((2*n, 2*n))
        for i in range(n):
            theta[i, n+i] = 1.0
            theta[n+i, i] = -1.0
        return cls(theta, hbar)


# ═══════════════════════════════════════════════════════════════════════════════
# QUANTUM GROUPS AND HOPF ALGEBRAS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class HopfAlgebra:
    """
    Hopf algebra (H, μ, η, Δ, ε, S).
    
    - Algebra: (H, μ, η)
    - Coalgebra: (H, Δ, ε)
    - Antipode: S: H → H
    """
    name: str
    
    def coproduct(self) -> str:
        """Δ: H → H ⊗ H."""
        return f"Δ: {self.name} → {self.name} ⊗ {self.name}"
    
    def counit(self) -> str:
        """ε: H → k."""
        return f"ε: {self.name} → k"
    
    def antipode(self) -> str:
        """S: H → H with μ(S ⊗ id)Δ = ηε."""
        return f"S: {self.name} → {self.name}"
    
    @classmethod
    def group_algebra(cls, G: str) -> 'HopfAlgebra':
        """k[G] with Δ(g) = g ⊗ g."""
        return cls(f"k[{G}]")
    
    @classmethod
    def universal_enveloping(cls, g: str) -> 'HopfAlgebra':
        """U(g) with Δ(X) = X ⊗ 1 + 1 ⊗ X."""
        return cls(f"U({g})")


@dataclass
class QuantumGroup:
    """
    Quantum group U_q(g).
    
    Deformation of U(g) with parameter q.
    """
    lie_algebra: str
    q: complex = np.exp(1j * np.pi / 3)  # Generic q
    
    def quantum_parameter(self) -> str:
        return f"q = {self.q}"
    
    def quantum_commutator(self) -> str:
        """[E, F] = (K - K^{-1})/(q - q^{-1})."""
        return "[E, F] = [K; 0]_q = (K - K^{-1})/(q - q^{-1})"
    
    def r_matrix(self) -> str:
        """Universal R-matrix for quasitriangular structure."""
        return f"R ∈ U_q({self.lie_algebra}) ⊗ U_q({self.lie_algebra})"
    
    def yang_baxter(self) -> str:
        """Quantum Yang-Baxter equation."""
        return "R₁₂ R₁₃ R₂₃ = R₂₃ R₁₃ R₁₂"
    
    @classmethod
    def sl2(cls, q: complex = None) -> 'QuantumGroup':
        """U_q(sl_2)."""
        return cls("sl_2", q or np.exp(1j * np.pi / 3))


# ═══════════════════════════════════════════════════════════════════════════════
# POLE BRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class NCGeomPoleBridge:
    """
    Bridge between noncommutative geometry and pole structure.
    """
    
    @staticmethod
    def c_pole_as_dirac() -> str:
        """
        C-pole corresponds to Dirac operator.
        Differential structure from spectral data.
        """
        return "C ↔ Dirac: D encodes differential geometry"
    
    @staticmethod
    def psi_pole_as_spectral_dimension() -> str:
        """
        Ψ-pole corresponds to spectral dimension.
        Hierarchical scale structure.
        """
        return "Ψ ↔ Spectral dim: d from Tr(|D|^{-s})"
    
    @staticmethod
    def sigma_pole_as_nc() -> str:
        """
        Σ-pole corresponds to noncommutativity.
        Quantum uncertainty in geometry.
        """
        return "Σ ↔ NC: [x_i, x_j] ≠ 0 quantum geometry"
    
    @staticmethod
    def d_pole_as_k_theory() -> str:
        """
        D-pole corresponds to K-theory classes.
        Discrete topological invariants.
        """
        return "D ↔ K-theory: K_*(A) discrete invariants"
    
    @staticmethod
    def gateway_as_index() -> str:
        """
        Gateway corresponds to index pairing.
        Bridge K-theory and K-homology.
        """
        return "Gateway ↔ Index: ⟨[D], [e]⟩ = Ind(D_e)"


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def nc_algebra(name: str) -> NoncommutativeAlgebra:
    """Create noncommutative algebra."""
    return NoncommutativeAlgebra(name)


def spectral_triple(alg: NoncommutativeAlgebra, 
                    triple_type: SpectralTripleType = SpectralTripleType.COMMUTATIVE
                   ) -> SpectralTriple:
    """Create spectral triple."""
    return SpectralTriple(alg, triple_type=triple_type)


def cyclic_cohomology(alg: NoncommutativeAlgebra) -> CyclicCohomology:
    """Create cyclic cohomology."""
    return CyclicCohomology(alg)


def moyal_product(n: int, hbar: float = 1.0) -> MoyalProduct:
    """Create canonical Moyal product."""
    return MoyalProduct.canonical(n, hbar)


def quantum_group(g: str, q: complex = None) -> QuantumGroup:
    """Create quantum group."""
    return QuantumGroup(g, q or np.exp(1j * np.pi / 3))


def hopf_algebra(name: str) -> HopfAlgebra:
    """Create Hopf algebra."""
    return HopfAlgebra(name)


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Algebras
    'NoncommutativeAlgebra',
    'CStarAlgebra',
    
    # Spectral triples
    'SpectralTripleType',
    'SpectralTriple',
    'RealStructure',
    
    # Cyclic cohomology
    'HochschildComplex',
    'CyclicCohomology',
    'ConnesIndex',
    
    # Deformation
    'MoyalProduct',
    
    # Quantum groups
    'HopfAlgebra',
    'QuantumGroup',
    
    # Bridge
    'NCGeomPoleBridge',
    
    # Functions
    'nc_algebra',
    'spectral_triple',
    'cyclic_cohomology',
    'moyal_product',
    'quantum_group',
    'hopf_algebra',
]
