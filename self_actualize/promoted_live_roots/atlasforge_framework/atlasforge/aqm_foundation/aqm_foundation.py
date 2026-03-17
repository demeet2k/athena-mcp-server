"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      AQM FOUNDATION MODULE                                   ║
║                                                                              ║
║  Axiomatic Quantum Mathematics - TOME I Implementation                       ║
║                                                                              ║
║  Core Concepts:                                                              ║
║    - Value Space: Riemann sphere Ĉ = ℂ ∪ {∞}                                 ║
║    - Q-numbers: States ρ on H = L²(Ĉ, μ)                                     ║
║    - Meaning Transport: Koopman-Jacobian unitaries U_T                       ║
║    - Classical Shadow: Measurement → probability distribution                ║
║                                                                              ║
║  Key Invariants:                                                             ║
║    - Inversion duality: J(z) = 1/z (near ↔ far)                              ║
║    - Scale symmetry: z ↦ λz (zoom)                                           ║
║    - Total mass conservation under transport                                 ║
║                                                                              ║
║  4⁴ Crystal Discipline:                                                      ║
║    Lenses: □ Square, ✿ Flower, ☁ Cloud, ⟂ Fractal                           ║
║    Layers: Objects, Operators, Invariants, Certificates                      ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Any, Callable, Union
from enum import Enum
import numpy as np
from numpy.typing import NDArray


# ═══════════════════════════════════════════════════════════════════════════════
# VALUE SPACE: RIEMANN SPHERE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class RiemannSphere:
    """
    Riemann sphere Ĉ = ℂ ∪ {∞}.
    
    Properties:
    - Compact, globally finite measure
    - Two poles: 0 (near) and ∞ (far)
    - Möbius transformations as coordinate changes
    - Canonical measure μ (spherical area)
    """
    
    @staticmethod
    def stereographic_project(theta: float, phi: float) -> complex:
        """
        Stereographic projection from S² to ℂ.
        
        (θ, φ) → z = tan(θ/2) · e^{iφ}
        """
        if np.isclose(theta, np.pi):
            return complex('inf')
        return np.tan(theta / 2) * np.exp(1j * phi)
    
    @staticmethod
    def inverse_stereographic(z: complex) -> Tuple[float, float]:
        """
        Inverse stereographic: ℂ → S².
        
        z → (θ, φ) where θ = 2·arctan|z|, φ = arg(z)
        """
        if not np.isfinite(z):
            return (np.pi, 0.0)
        r = abs(z)
        theta = 2 * np.arctan(r)
        phi = np.angle(z)
        return (theta, phi)
    
    @staticmethod
    def spherical_measure_density(z: complex) -> float:
        """
        Spherical measure density dμ/d²z at z ∈ ℂ.
        
        dμ = 4 / (1 + |z|²)² d²z
        """
        if not np.isfinite(z):
            return 0.0
        return 4.0 / (1 + abs(z)**2)**2
    
    @staticmethod
    def inversion(z: complex) -> complex:
        """
        Inversion J(z) = 1/z.
        
        Near ↔ Far duality:
        - 0 ↔ ∞
        - |z| < 1 ↔ |z| > 1
        """
        if z == 0:
            return complex('inf')
        if not np.isfinite(z):
            return 0j
        return 1.0 / z
    
    @staticmethod
    def scaling(z: complex, lam: complex) -> complex:
        """
        Scaling z ↦ λz (zoom operation).
        """
        if not np.isfinite(z):
            return z
        return lam * z
    
    @staticmethod
    def mobius(z: complex, a: complex, b: complex, 
               c: complex, d: complex) -> complex:
        """
        Möbius transformation: z ↦ (az + b)/(cz + d).
        
        General SL(2,ℂ) action on Ĉ.
        """
        if not np.isfinite(z):
            if c == 0:
                return complex('inf')
            return a / c
        
        denom = c * z + d
        if denom == 0:
            return complex('inf')
        return (a * z + b) / denom


# ═══════════════════════════════════════════════════════════════════════════════
# Q-NUMBERS: QUANTUM-EXTENDED NUMBERS
# ═══════════════════════════════════════════════════════════════════════════════

class QNumberType(Enum):
    """Types of Q-numbers."""
    PURE = "pure"           # Ray in Hilbert space |ψ⟩
    MIXED = "mixed"         # Density operator ρ
    CLASSICAL = "classical" # Delta function (classical limit)
    BOUNDARY = "boundary"   # Boundary state (jets at 0 or ∞)


@dataclass
class QNumber:
    """
    A Q-number: quantum-extended number as a state on H = L²(Ĉ, μ).
    
    Not a scalar, but a state that carries:
    - Spread (localization width)
    - Phase (interference structure)
    - Mixtures (convex combinations)
    - Boundary behavior (jets at poles)
    
    Represented either as:
    - Pure state: |ψ⟩ ∈ H (modulo global phase)
    - Mixed state: ρ ≥ 0, Tr(ρ) = 1
    """
    # Representation as coefficients in a basis
    coefficients: NDArray  # Complex coefficients
    basis_type: str = "spherical_harmonic"  # Basis used
    qtype: QNumberType = QNumberType.MIXED
    
    # Metadata
    spread: float = 0.0  # Localization width σ
    center: complex = 0j  # Classical shadow center
    boundary_order_0: int = 0  # Jet order at z=0
    boundary_order_inf: int = 0  # Jet order at z=∞
    
    @classmethod
    def classical(cls, z: complex, sigma: float = 0.01) -> 'QNumber':
        """
        Create classical Q-number: Gaussian localized at z.
        
        This is the "corridor" limit where Q-numbers ≈ scalars.
        """
        # Simplified: just store center and spread
        return cls(
            coefficients=np.array([1.0 + 0j]),
            qtype=QNumberType.CLASSICAL,
            spread=sigma,
            center=z
        )
    
    @classmethod
    def pure(cls, psi: NDArray) -> 'QNumber':
        """Create pure state Q-number from amplitude vector."""
        # Normalize
        norm = np.linalg.norm(psi)
        if norm > 0:
            psi = psi / norm
        return cls(
            coefficients=psi,
            qtype=QNumberType.PURE,
            spread=0.0  # Computed later
        )
    
    @classmethod
    def mixed(cls, rho: NDArray) -> 'QNumber':
        """Create mixed state Q-number from density matrix."""
        # Verify positive and trace-one (simplified)
        return cls(
            coefficients=rho.flatten(),
            qtype=QNumberType.MIXED
        )
    
    @property
    def is_classical(self) -> bool:
        """Check if Q-number is in classical corridor."""
        return self.spread < 0.1 and self.qtype == QNumberType.CLASSICAL
    
    def classical_shadow(self) -> complex:
        """
        Extract classical shadow (expected value).
        
        The classical shadow is the measurement outcome distribution.
        """
        return self.center
    
    def purity(self) -> float:
        """
        Purity Tr(ρ²) ∈ [1/d, 1].
        
        1 = pure state, 1/d = maximally mixed.
        """
        if self.qtype == QNumberType.PURE:
            return 1.0
        # For mixed states, compute Tr(ρ²)
        if len(self.coefficients.shape) == 1:
            return 1.0
        rho = self.coefficients.reshape(int(np.sqrt(len(self.coefficients))), -1)
        return np.real(np.trace(rho @ rho))


# ═══════════════════════════════════════════════════════════════════════════════
# MEANING TRANSPORT: KOOPMAN-JACOBIAN UNITARIES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class MeaningTransport:
    """
    Meaning transport via Koopman-Jacobian representation.
    
    For measurable nonsingular T: Ĉ → Ĉ with T_#μ ≪ μ:
    
    U_T ψ(v) = J_T(v)^{1/2} · ψ(T(v))
    
    where J_T = d(T_#μ)/dμ is the Radon-Nikodym derivative.
    
    This ensures:
    - Norm preservation: ‖U_T ψ‖ = ‖ψ‖
    - Coordinate-free meaning
    - Total mass conservation
    """
    
    @staticmethod
    def radon_nikodym_inversion(z: complex) -> float:
        """
        Radon-Nikodym factor for inversion J(z) = 1/z.
        
        J_{1/z}(v) = |v|^{-4} (standard formula on sphere)
        """
        if z == 0 or not np.isfinite(z):
            return 0.0
        return abs(z)**(-4)
    
    @staticmethod
    def radon_nikodym_scaling(z: complex, lam: complex) -> float:
        """
        Radon-Nikodym factor for scaling z ↦ λz.
        
        J_λ(v) = |λ|^2 (scaling the measure)
        """
        return abs(lam)**2
    
    @staticmethod
    def transport_inversion(psi: Callable[[complex], complex]) -> Callable[[complex], complex]:
        """
        Apply inversion transport U_J to amplitude function.
        
        (U_J ψ)(v) = |v|^{-2} · ψ(1/v)
        """
        def transported(v: complex) -> complex:
            if v == 0:
                return 0j
            jac = abs(v)**(-2)  # Square root of RN factor
            return jac * psi(1.0 / v)
        return transported
    
    @staticmethod
    def transport_scaling(psi: Callable[[complex], complex], 
                          lam: complex) -> Callable[[complex], complex]:
        """
        Apply scaling transport U_λ to amplitude function.
        
        (U_λ ψ)(v) = |λ| · ψ(λv)
        """
        def transported(v: complex) -> complex:
            jac = abs(lam)  # Square root of RN factor
            return jac * psi(lam * v)
        return transported


# ═══════════════════════════════════════════════════════════════════════════════
# MEASUREMENT AND CLASSICAL SHADOW
# ═══════════════════════════════════════════════════════════════════════════════

class MeasurementType(Enum):
    """Types of measurements on Q-numbers."""
    POSITION = "position"       # Where is the value?
    MODULUS = "modulus"         # How far from origin?
    PHASE = "phase"             # What angle?
    BOUNDARY = "boundary"       # Near 0 or ∞?


@dataclass
class POVM:
    """
    Positive Operator-Valued Measure for Q-number measurement.
    
    A POVM {E_k} satisfies:
    - E_k ≥ 0 (positive)
    - Σ_k E_k = I (completeness)
    
    Probability of outcome k: P(k) = Tr(ρ E_k)
    """
    operators: List[NDArray]  # POVM elements E_k
    outcomes: List[Any]       # Outcome labels
    
    def probabilities(self, rho: NDArray) -> NDArray:
        """Compute outcome probabilities for state ρ."""
        probs = []
        for E in self.operators:
            p = np.real(np.trace(rho @ E))
            probs.append(max(0, p))  # Ensure non-negative
        probs = np.array(probs)
        return probs / probs.sum()  # Normalize


@dataclass
class ClassicalShadow:
    """
    Classical shadow of a Q-number.
    
    The shadow is the probability distribution over Ĉ induced by
    measurement. It is NOT the Q-number itself, but an explicit
    projection with information loss accounting.
    """
    distribution: Dict[str, float]  # Outcome → probability
    estimator: complex              # Point estimate
    confidence_region: Tuple[complex, float]  # (center, radius)
    information_loss: float         # Entropy of shadow
    
    @classmethod
    def from_qnumber(cls, q: QNumber, 
                     measurement: MeasurementType = MeasurementType.POSITION) -> 'ClassicalShadow':
        """Extract classical shadow via measurement."""
        # Simplified: for classical Q-numbers, shadow ≈ center
        if q.is_classical:
            return cls(
                distribution={"center": 1.0},
                estimator=q.center,
                confidence_region=(q.center, q.spread),
                information_loss=0.0
            )
        
        # For non-classical, information is lost
        return cls(
            distribution={"spread": 1.0},
            estimator=q.center,
            confidence_region=(q.center, q.spread * 3),  # 3σ region
            information_loss=np.log(q.spread + 1)
        )


# ═══════════════════════════════════════════════════════════════════════════════
# EQUIVALENCE AND NORMAL FORMS
# ═══════════════════════════════════════════════════════════════════════════════

class EquivalenceType(Enum):
    """Types of Q-number equivalence."""
    EXACT = "exact"              # ρ₁ = ρ₂ exactly
    GAUGE = "gauge"              # ρ₁ = U ρ₂ U* for some U_T
    MEASUREMENT = "measurement"  # Same probabilities for all POVMs
    SHADOW = "shadow"            # Same classical shadow


@dataclass
class QNumberNormalForm:
    """
    Normal form / canonical representative for Q-numbers.
    
    Supports indexing, retrieval, and auditability.
    """
    spectral_decomposition: List[Tuple[float, NDArray]]  # (eigenvalue, eigenvector)
    center: complex       # Weighted center
    spread: float         # Characteristic width
    boundary_jets: Dict[str, List[complex]]  # Jets at 0 and ∞
    hash_digest: str      # Content hash for indexing
    
    @classmethod
    def compute(cls, q: QNumber) -> 'QNumberNormalForm':
        """Compute normal form of Q-number."""
        import hashlib
        
        # Simplified: use coefficient hash
        data = q.coefficients.tobytes()
        h = hashlib.sha256(data).hexdigest()[:16]
        
        return cls(
            spectral_decomposition=[(1.0, q.coefficients)],
            center=q.center,
            spread=q.spread,
            boundary_jets={"0": [], "inf": []},
            hash_digest=h
        )


# ═══════════════════════════════════════════════════════════════════════════════
# 4⁴ CRYSTAL DISCIPLINE
# ═══════════════════════════════════════════════════════════════════════════════

class CrystalLens(Enum):
    """Four lenses of the 4⁴ crystal."""
    SQUARE = "□"    # Formal objects
    FLOWER = "✿"    # Geometric structure
    CLOUD = "☁"     # Probability/information
    FRACTAL = "⟂"   # Implementation/certificates


class CrystalLayer(Enum):
    """Four layers per lens."""
    OBJECTS = "objects"
    OPERATORS = "operators"
    INVARIANTS = "invariants"
    CERTIFICATES = "certificates"


@dataclass
class CrystalAddress:
    """
    Address in the 4⁴ crystal: ⟨chapter, section, lens, layer⟩₄.
    
    Example: ⟨0000:00⟩ = Chapter 0, Section 0, Objects, Square
    """
    chapter: int  # 0-3
    section: int  # 0-3
    lens: CrystalLens
    layer: CrystalLayer
    
    def __str__(self) -> str:
        lens_idx = list(CrystalLens).index(self.lens)
        layer_idx = list(CrystalLayer).index(self.layer)
        return f"⟨{self.chapter}{self.section}{lens_idx}{layer_idx}⟩₄"


# ═══════════════════════════════════════════════════════════════════════════════
# CORRIDOR CONSTRAINTS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class CorridorConstraint:
    """
    Corridor constraint: conditions under which AQM reduces to classical.
    
    Inside the corridor:
    - Q-numbers behave like scalars
    - Operations are approximately pointwise
    - Error bounds are controlled
    
    Outside the corridor:
    - Full quantum structure is needed
    - Interference and superposition matter
    - Boundary semantics activate
    """
    max_spread: float = 0.1        # Maximum allowed σ
    min_purity: float = 0.9        # Minimum purity for classical
    boundary_tolerance: float = 0.01  # How close to 0 or ∞
    
    def is_classical(self, q: QNumber) -> bool:
        """Check if Q-number is in classical corridor."""
        if q.spread > self.max_spread:
            return False
        if q.purity() < self.min_purity:
            return False
        return True
    
    def corridor_error(self, q: QNumber) -> float:
        """Estimate error from treating Q-number classically."""
        return q.spread + (1 - q.purity())


# ═══════════════════════════════════════════════════════════════════════════════
# POLE BRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class AQMFoundationPoleBridge:
    """
    Bridge between AQM Foundation and four-pole framework.
    """
    
    @staticmethod
    def integration() -> str:
        return """
        AQM FOUNDATION ↔ FRAMEWORK
        
        Value Space (Riemann Sphere Ĉ):
          - Compact, finite measure
          - Two poles: 0 (near), ∞ (far)
          - Möbius transformations = SL(2,ℂ) action
        
        Q-Numbers as States:
          - Pure: |ψ⟩ ∈ H (ray modulo phase)
          - Mixed: ρ ≥ 0, Tr(ρ) = 1
          - Classical corridor: σ → 0 limit
        
        Meaning Transport:
          U_T ψ(v) = J_T(v)^{1/2} · ψ(T(v))
          - Koopman-Jacobian representation
          - Preserves norm (total mass)
          - Inversion: U_J, Scaling: S(λ)
        
        Classical Shadow:
          - Measurement → probability distribution
          - Explicit loss accounting
          - Corridor theorems for classical limit
        
        4⁴ Crystal Discipline:
          □ Square: Formal objects
          ✿ Flower: Geometric structure
          ☁ Cloud: Probability/information
          ⟂ Fractal: Implementation/certificates
        
        Pole Correspondence:
          Ĉ = D ∪ Ω ∪ Σ ∪ Ψ structure
          - D: Discrete lattice sampling
          - Ω: Continuous manifold
          - Σ: Probability distributions
          - Ψ: Hierarchical jets
        """


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def riemann_sphere() -> RiemannSphere:
    """Create Riemann sphere."""
    return RiemannSphere()


def qnumber_classical(z: complex, sigma: float = 0.01) -> QNumber:
    """Create classical Q-number localized at z."""
    return QNumber.classical(z, sigma)


def qnumber_pure(psi: NDArray) -> QNumber:
    """Create pure state Q-number."""
    return QNumber.pure(psi)


def meaning_transport() -> MeaningTransport:
    """Create meaning transport."""
    return MeaningTransport()


def classical_shadow(q: QNumber) -> ClassicalShadow:
    """Extract classical shadow from Q-number."""
    return ClassicalShadow.from_qnumber(q)


def normal_form(q: QNumber) -> QNumberNormalForm:
    """Compute normal form of Q-number."""
    return QNumberNormalForm.compute(q)


def corridor_constraint(max_spread: float = 0.1) -> CorridorConstraint:
    """Create corridor constraint."""
    return CorridorConstraint(max_spread=max_spread)


def crystal_address(chapter: int, section: int, 
                    lens: CrystalLens, layer: CrystalLayer) -> CrystalAddress:
    """Create crystal address."""
    return CrystalAddress(chapter, section, lens, layer)


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Value Space
    'RiemannSphere',
    
    # Q-Numbers
    'QNumberType',
    'QNumber',
    
    # Transport
    'MeaningTransport',
    
    # Measurement
    'MeasurementType',
    'POVM',
    'ClassicalShadow',
    
    # Equivalence
    'EquivalenceType',
    'QNumberNormalForm',
    
    # Crystal
    'CrystalLens',
    'CrystalLayer',
    'CrystalAddress',
    
    # Corridor
    'CorridorConstraint',
    
    # Bridge
    'AQMFoundationPoleBridge',
    
    # Functions
    'riemann_sphere',
    'qnumber_classical',
    'qnumber_pure',
    'meaning_transport',
    'classical_shadow',
    'normal_form',
    'corridor_constraint',
    'crystal_address',
]
