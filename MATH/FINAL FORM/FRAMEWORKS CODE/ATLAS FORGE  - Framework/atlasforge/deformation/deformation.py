"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                       DEFORMATION THEORY MODULE                              ║
║                                                                              ║
║  Infinitesimal and Formal Deformations                                       ║
║                                                                              ║
║  Core Principle:                                                             ║
║    Deformation theory studies how objects vary in families.                  ║
║    Infinitesimal deformations: X₀ → X_ε over Spec(k[ε]/ε²)                  ║
║    Formal deformations: X₀ → X over Spf(k[[t]])                             ║
║                                                                              ║
║  Connection to Framework:                                                    ║
║    - C-pole ↔ Tangent space (first-order deformations)                      ║
║    - Ψ-pole ↔ Higher-order obstructions (hierarchical)                      ║
║    - D-pole ↔ Discrete moduli (counting deformations)                       ║
║    - Gateway ↔ Kuranishi map (deformation vs obstruction)                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Any, Generic, TypeVar
from enum import Enum, auto
import numpy as np


T = TypeVar('T')


# ═══════════════════════════════════════════════════════════════════════════════
# ARTINIAN RINGS AND INFINITESIMALS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ArtinianRing:
    """
    Artinian local ring (A, 𝔪, k).
    
    Key examples:
    - k[ε]/(ε²) - dual numbers (first-order)
    - k[ε]/(ε^{n+1}) - n-th order
    - k[[t]]/(t^n) - truncated power series
    """
    base_field: str
    maximal_ideal: str
    nilpotent_order: int
    
    @property
    def symbol(self) -> str:
        return f"{self.base_field}[ε]/(ε^{self.nilpotent_order})"
    
    def residue_field(self) -> str:
        """k = A/𝔪."""
        return self.base_field
    
    def cotangent_space(self) -> str:
        """𝔪/𝔪² - cotangent space at closed point."""
        return f"{self.maximal_ideal}/{self.maximal_ideal}²"
    
    @classmethod
    def dual_numbers(cls, k: str = "k") -> 'ArtinianRing':
        """k[ε]/(ε²) - dual numbers."""
        return cls(k, "(ε)", 2)
    
    @classmethod
    def order_n(cls, n: int, k: str = "k") -> 'ArtinianRing':
        """k[ε]/(ε^{n+1}) - n-th order."""
        return cls(k, "(ε)", n + 1)


@dataclass
class FormalScheme:
    """
    Formal scheme - completion of a scheme.
    
    Spf(R) = colim Spec(R/I^n) for I-adic topology.
    """
    ring: str
    ideal: str
    
    @property
    def symbol(self) -> str:
        return f"Spf({self.ring})"
    
    @classmethod
    def formal_disk(cls, k: str = "k") -> 'FormalScheme':
        """Spf(k[[t]]) - formal disk."""
        return cls(f"{k}[[t]]", "(t)")
    
    @classmethod
    def formal_polydisk(cls, n: int, k: str = "k") -> 'FormalScheme':
        """Spf(k[[t₁,...,tₙ]]) - formal n-disk."""
        vars = ", ".join([f"t_{i}" for i in range(1, n+1)])
        return cls(f"{k}[[{vars}]]", f"({vars})")


# ═══════════════════════════════════════════════════════════════════════════════
# DEFORMATION FUNCTORS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class DeformationFunctor:
    """
    Deformation functor D: Art_k → Sets.
    
    D(A) = {deformations of X₀ over Spec(A)} / iso
    
    Schlessinger's criteria for pro-representability.
    """
    name: str
    object_type: str  # What we're deforming
    base_object: str  # X₀
    
    def of_ring(self, A: ArtinianRing) -> str:
        """D(A) - deformations over A."""
        return f"{self.name}({A.symbol})"
    
    def tangent_space(self) -> str:
        """T_D = D(k[ε]/ε²) - tangent space."""
        return f"T_{{{self.name}}} = {self.name}(k[ε]/ε²)"
    
    def obstruction_space(self) -> str:
        """Obstruction space (where obstructions live)."""
        return f"Obs_{{{self.name}}}"
    
    def is_pro_representable(self) -> bool:
        """Check Schlessinger's criteria (H1-H4)."""
        return True  # Generic
    
    def hull(self) -> str:
        """Pro-representing hull R if exists."""
        return f"R_{{{self.name}}}"


@dataclass
class InfinitesimalDeformation:
    """
    First-order (infinitesimal) deformation.
    
    X_ε → Spec(k[ε]/ε²) lifting X₀ → Spec(k).
    """
    base_object: str
    base: ArtinianRing = field(default_factory=ArtinianRing.dual_numbers)
    
    def fiber(self) -> str:
        """Central fiber X₀."""
        return self.base_object
    
    def is_trivial(self) -> bool:
        """Check if deformation is trivial (product)."""
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# TANGENT AND OBSTRUCTION THEORY
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class TangentObstructionTheory:
    """
    Tangent-obstruction complex for deformations.
    
    For X smooth:
    - T¹ = H¹(X, T_X) = first-order deformations
    - T² = H²(X, T_X) = obstructions
    
    For X with singularities: cotangent complex T^•.
    """
    object_name: str
    tangent_sheaf: str = "T_X"
    
    def T1(self) -> str:
        """T¹ = space of first-order deformations."""
        return f"H¹({self.object_name}, {self.tangent_sheaf})"
    
    def T2(self) -> str:
        """T² = obstruction space."""
        return f"H²({self.object_name}, {self.tangent_sheaf})"
    
    def T0(self) -> str:
        """T⁰ = infinitesimal automorphisms."""
        return f"H⁰({self.object_name}, {self.tangent_sheaf})"
    
    def is_unobstructed(self) -> bool:
        """Check if T² = 0 (deformations always extend)."""
        return False  # Generic
    
    def euler_characteristic(self) -> str:
        """χ(T_X) = dim T⁰ - dim T¹ + dim T² - ..."""
        return f"χ({self.object_name}, {self.tangent_sheaf})"


@dataclass
class CotangentComplex:
    """
    Cotangent complex 𝕃_{X/S}.
    
    For X → S morphism:
    - 𝕃_{X/S} is a complex of O_X-modules
    - H⁰(𝕃) = Ω¹_{X/S} (Kähler differentials)
    - H^{-1}(𝕃) detects singularities
    
    Deformation theory: Ext^i(𝕃, F) controls deformations.
    """
    source: str
    target: str
    
    @property
    def symbol(self) -> str:
        return f"𝕃_{{{self.source}/{self.target}}}"
    
    def H0(self) -> str:
        """H⁰(𝕃) = Ω¹ (differentials)."""
        return f"Ω¹_{{{self.source}/{self.target}}}"
    
    def Hminus1(self) -> str:
        """H^{-1}(𝕃) detects non-lci singularities."""
        return f"H^{{-1}}({self.symbol})"
    
    def deformation_ext(self, i: int, F: str) -> str:
        """Ext^i(𝕃, F) controls deformations."""
        return f"Ext^{i}({self.symbol}, {F})"
    
    def is_perfect(self) -> bool:
        """Check if 𝕃 is perfect (bounded amplitude)."""
        return True  # For lci morphisms


# ═══════════════════════════════════════════════════════════════════════════════
# MODULI THEORY
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ModuliProblem:
    """
    A moduli problem: functor F: Sch^op → Sets.
    
    F(S) = {families of objects over S} / iso
    
    Question: Is F representable by a scheme/stack?
    """
    name: str
    objects: str
    
    def at_scheme(self, S: str) -> str:
        """F(S) - families over S."""
        return f"{self.name}({S})"
    
    def point_count(self) -> str:
        """F(Spec k) - objects over a point."""
        return f"{self.name}(Spec k)"
    
    def tangent_at(self, x: str) -> str:
        """Tangent space to moduli at x."""
        return f"T_{{{x}}} {self.name}"
    
    def is_representable(self) -> bool:
        """Check if representable by scheme."""
        return False  # Usually need stack


@dataclass
class ModuliSpace:
    """
    Moduli space (or stack) M.
    
    Represents/parametrizes a moduli problem.
    """
    name: str
    dimension: int
    is_fine: bool = False  # Fine moduli = represents functor
    is_coarse: bool = True  # Coarse moduli = universal homeomorphism
    
    def universal_family(self) -> str:
        """Universal family over M (for fine moduli)."""
        if self.is_fine:
            return f"𝒳 → {self.name}"
        return "No universal family (coarse moduli)"
    
    def tangent_space(self, x: str) -> str:
        """Tangent space at point."""
        return f"T_{{{x}}} {self.name}"
    
    def obstruction_space(self, x: str) -> str:
        """Obstruction space at point."""
        return f"Obs_{{{x}}} {self.name}"


@dataclass
class ModuliStack:
    """
    Moduli stack - allows automorphisms.
    
    Example: ℳ_g (moduli of curves) is a DM stack.
    """
    name: str
    dimension: int
    stack_type: str = "DM"  # Deligne-Mumford or Artin
    
    def inertia_stack(self) -> str:
        """Inertia I_M = M ×_{M×M} M."""
        return f"I_{{{self.name}}}"
    
    def coarse_moduli(self) -> str:
        """Coarse moduli space."""
        return f"|{self.name}|"
    
    def at_point(self, x: str) -> str:
        """Local structure at point (gerbe)."""
        return f"{self.name} near {x} ≃ [pt/Aut({x})]"


# ═══════════════════════════════════════════════════════════════════════════════
# KURANISHI MAP
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class KuranishiMap:
    """
    Kuranishi map κ: T¹ → T².
    
    Controls deformations:
    - ker(κ) = actual deformations
    - κ = 0 means unobstructed
    
    Local model: deformation space ≃ κ⁻¹(0) / Aut.
    """
    tangent_space: str
    obstruction_space: str
    
    def domain(self) -> str:
        return self.tangent_space
    
    def codomain(self) -> str:
        return self.obstruction_space
    
    def kernel(self) -> str:
        """ker(κ) = versal deformation space."""
        return f"ker(κ: {self.tangent_space} → {self.obstruction_space})"
    
    def local_moduli(self) -> str:
        """Local model of moduli space."""
        return f"κ⁻¹(0) / Aut"


# ═══════════════════════════════════════════════════════════════════════════════
# SPECIFIC DEFORMATION THEORIES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class CurveDeformations:
    """
    Deformations of algebraic curves.
    
    For smooth curve C of genus g:
    - dim T¹ = 3g - 3 for g ≥ 2
    - T² = 0 (unobstructed)
    - Moduli: ℳ_g has dim 3g - 3
    """
    genus: int
    
    def dimension_moduli(self) -> int:
        """dim ℳ_g = 3g - 3."""
        if self.genus <= 1:
            return 0 if self.genus == 0 else 1
        return 3 * self.genus - 3
    
    def is_unobstructed(self) -> bool:
        """Curves are unobstructed."""
        return True
    
    def T1_dimension(self) -> int:
        """H¹(C, T_C)."""
        return self.dimension_moduli()
    
    def automorphism_dimension(self) -> int:
        """H⁰(C, T_C) for generic curve."""
        if self.genus == 0:
            return 3  # PGL(2)
        elif self.genus == 1:
            return 1  # Translations
        return 0


@dataclass
class SurfaceDeformations:
    """
    Deformations of algebraic surfaces.
    
    May have obstructions! H²(S, T_S) ≠ 0 in general.
    """
    name: str
    kodaira_dimension: int  # κ(S)
    
    def T1(self) -> str:
        """H¹(S, T_S) - first-order deformations."""
        return f"H¹({self.name}, T_{{{self.name}}})"
    
    def T2(self) -> str:
        """H²(S, T_S) - obstructions."""
        return f"H²({self.name}, T_{{{self.name}}})"
    
    def is_rigid(self) -> bool:
        """Check if surface is rigid (no deformations)."""
        return False  # Check T¹ = 0


# ═══════════════════════════════════════════════════════════════════════════════
# POLE BRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class DeformationPoleBridge:
    """
    Bridge between deformation theory and pole structure.
    """
    
    @staticmethod
    def c_pole_as_tangent() -> str:
        """
        C-pole (continuous) corresponds to tangent directions.
        First-order deformations = infinitesimal continuous variation.
        """
        return "C-pole ↔ Tangent: T¹ = first-order continuous variation"
    
    @staticmethod
    def psi_pole_as_higher_order() -> str:
        """
        Ψ-pole (hierarchical) corresponds to higher-order obstructions.
        Tower of Artinian rings = hierarchical deformation.
        """
        return "Ψ-pole ↔ Higher order: k[ε]/ε^n → k[ε]/ε^{n+1}"
    
    @staticmethod
    def d_pole_as_discrete_moduli() -> str:
        """
        D-pole (discrete) corresponds to discrete moduli.
        Counting deformations, discrete invariants.
        """
        return "D-pole ↔ Discrete moduli: dim, invariants, counts"
    
    @staticmethod
    def gateway_as_kuranishi() -> str:
        """
        Gateway corresponds to Kuranishi map κ: T¹ → T².
        Balance between deformation and obstruction.
        """
        return "Gateway ↔ Kuranishi: κ: T¹ → T² (def ↔ obs)"


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def dual_numbers(k: str = "k") -> ArtinianRing:
    """Create dual numbers k[ε]/ε²."""
    return ArtinianRing.dual_numbers(k)


def deformation_functor(name: str, obj_type: str, base: str) -> DeformationFunctor:
    """Create a deformation functor."""
    return DeformationFunctor(name, obj_type, base)


def tangent_obstruction(X: str) -> TangentObstructionTheory:
    """Create tangent-obstruction theory for X."""
    return TangentObstructionTheory(X)


def cotangent_complex(X: str, S: str = "Spec(k)") -> CotangentComplex:
    """Create cotangent complex 𝕃_{X/S}."""
    return CotangentComplex(X, S)


def moduli_curves(g: int) -> CurveDeformations:
    """Deformation theory for curves of genus g."""
    return CurveDeformations(g)


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Artinian
    'ArtinianRing',
    'FormalScheme',
    
    # Deformation functors
    'DeformationFunctor',
    'InfinitesimalDeformation',
    
    # Tangent-obstruction
    'TangentObstructionTheory',
    'CotangentComplex',
    
    # Moduli
    'ModuliProblem',
    'ModuliSpace',
    'ModuliStack',
    
    # Kuranishi
    'KuranishiMap',
    
    # Specific theories
    'CurveDeformations',
    'SurfaceDeformations',
    
    # Bridge
    'DeformationPoleBridge',
    
    # Functions
    'dual_numbers',
    'deformation_functor',
    'tangent_obstruction',
    'cotangent_complex',
    'moduli_curves',
]
