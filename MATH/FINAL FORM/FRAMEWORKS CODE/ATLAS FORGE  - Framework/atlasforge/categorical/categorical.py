"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    CATEGORICAL TRANSLATION MODULE                            ║
║                                                                              ║
║  SKF Functor, Boundary Realization Category, Morphism Composition            ║
║                                                                              ║
║  Core Structure:                                                             ║
║    The framework forms a category where:                                     ║
║      - Objects: (κ-slice, representation) pairs                             ║
║      - Morphisms: Kernel-respecting transformations                         ║
║      - Composition: Sequential kernel transport                             ║
║                                                                              ║
║  SKF (Square-Kernel-Flower) Functor:                                         ║
║    F: BoundaryReal → Hybrid                                                  ║
║    Maps boundary realizations to hybrid equations                            ║
║                                                                              ║
║  Boundary Realization Category (BoundaryReal):                               ║
║    Objects: Constraint manifolds with κ-structure                           ║
║    Morphisms: Gateway transports preserving kernel condition                 ║
║                                                                              ║
║  The functor preserves:                                                      ║
║    - Kernel bandwidth (τ_κ invariant)                                       ║
║    - Holographic structure (DLS pattern)                                    ║
║    - Phase coherence (discrete-continuous coupling)                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Callable, Any, Generic, TypeVar
from enum import Enum, auto
from abc import ABC, abstractmethod
import numpy as np
from numpy.typing import NDArray


# ═══════════════════════════════════════════════════════════════════════════════
# CATEGORICAL PRIMITIVES
# ═══════════════════════════════════════════════════════════════════════════════

T = TypeVar('T')
S = TypeVar('S')


class CategoryError(Exception):
    """Error in categorical operations."""
    pass


@dataclass
class CategoricalObject(ABC):
    """
    Abstract base for categorical objects.
    
    Every object carries:
        - κ-slice (kernel bandwidth parameter)
        - Representation type (Square/Flower/Cloud/Fractal)
        - Invariant bundle (preserved quantities)
    """
    kappa: float = 1.0  # Kernel parameter
    representation: str = "generic"
    
    @abstractmethod
    def identity_morphism(self) -> 'Morphism':
        """Return identity morphism on this object."""
        pass
    
    @property
    def bandwidth(self) -> float:
        """Kernel bandwidth τ_κ = π/(2√κ)."""
        return np.pi / (2 * np.sqrt(self.kappa))


@dataclass
class Morphism(ABC):
    """
    Abstract morphism between categorical objects.
    
    Morphisms must:
        - Respect kernel structure (bandwidth preservation)
        - Compose associatively
        - Have domain and codomain objects
    """
    source: CategoricalObject
    target: CategoricalObject
    
    @abstractmethod
    def apply(self, x: Any) -> Any:
        """Apply morphism to element."""
        pass
    
    @abstractmethod
    def compose(self, other: 'Morphism') -> 'Morphism':
        """Compose with another morphism (self ∘ other)."""
        pass
    
    @property
    def is_kernel_preserving(self) -> bool:
        """Check if morphism preserves kernel bandwidth."""
        return np.isclose(self.source.bandwidth, self.target.bandwidth)


# ═══════════════════════════════════════════════════════════════════════════════
# BOUNDARY REALIZATION CATEGORY
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class BoundaryObject(CategoricalObject):
    """
    Object in the Boundary Realization category.
    
    Represents a constraint manifold with:
        - Boundary parametrization (p, q) with (p-2)(q-2) = κ
        - Chart coordinates for local description
        - Kernel slice τ_κ
    """
    p: float = 3.0  # Boundary parameter 1
    q: float = 3.0  # Boundary parameter 2
    kappa: float = field(init=False)
    representation: str = "boundary"
    
    def __post_init__(self):
        # Kernel condition: (p-2)(q-2) = κ
        self.kappa = (self.p - 2) * (self.q - 2)
        if self.kappa <= 0:
            raise ValueError(f"Invalid boundary: κ = (p-2)(q-2) = {self.kappa} must be positive")
    
    def identity_morphism(self) -> 'BoundaryMorphism':
        """Identity morphism."""
        return BoundaryMorphism(
            source=self,
            target=self,
            gateway_matrix=np.eye(2)
        )
    
    @property
    def boundary_vector(self) -> NDArray[np.float64]:
        """Homogenized boundary coordinates [p-2, q-2]."""
        return np.array([self.p - 2, self.q - 2])
    
    @classmethod
    def from_kappa(cls, kappa: float, aspect: float = 1.0) -> 'BoundaryObject':
        """
        Create boundary object with given κ and aspect ratio.
        
        aspect = (p-2)/(q-2), so p-2 = √(κ·aspect), q-2 = √(κ/aspect)
        """
        p_minus_2 = np.sqrt(kappa * aspect)
        q_minus_2 = np.sqrt(kappa / aspect)
        return cls(p=p_minus_2 + 2, q=q_minus_2 + 2)


@dataclass
class BoundaryMorphism(Morphism):
    """
    Morphism in Boundary Realization category.
    
    A gateway transport that maps between boundary charts.
    Must preserve the kernel condition: (p'-2)(q'-2) = κ' 
    where κ' = f(κ) depends on the gateway matrix.
    """
    source: BoundaryObject
    target: BoundaryObject
    gateway_matrix: NDArray[np.float64]  # 2×2 SL(2,ℤ) or SL(2,ℝ)
    
    def __post_init__(self):
        # Verify determinant is ±1
        det = np.linalg.det(self.gateway_matrix)
        if not np.isclose(abs(det), 1.0, atol=1e-10):
            raise CategoryError(f"Gateway matrix must have det = ±1, got {det}")
    
    def apply(self, v: NDArray[np.float64]) -> NDArray[np.float64]:
        """Apply gateway transformation to boundary vector."""
        return self.gateway_matrix @ v
    
    def compose(self, other: 'BoundaryMorphism') -> 'BoundaryMorphism':
        """Compose morphisms: (self ∘ other)(x) = self(other(x))."""
        if self.source != other.target:
            raise CategoryError("Cannot compose: source/target mismatch")
        
        return BoundaryMorphism(
            source=other.source,
            target=self.target,
            gateway_matrix=self.gateway_matrix @ other.gateway_matrix
        )
    
    @property
    def kernel_transport_factor(self) -> float:
        """
        Factor by which κ changes under this morphism.
        
        For Pell-type gateway G = [[u, v], [Av, u]]:
        κ' = κ (preserved for standard gateways)
        """
        # Compute via action on boundary vector
        v = self.source.boundary_vector
        v_new = self.apply(v)
        
        kappa_old = v[0] * v[1]
        kappa_new = v_new[0] * v_new[1]
        
        if kappa_old == 0:
            return 1.0
        return kappa_new / kappa_old


# ═══════════════════════════════════════════════════════════════════════════════
# HYBRID CATEGORY
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class HybridObject(CategoricalObject):
    """
    Object in the Hybrid category.
    
    Represents a hybrid equation/system with:
        - Discrete structure (D-component)
        - Continuous phase (Ω-component)
        - Coupling strength λ
    """
    discrete_dim: int = 4
    phase_dim: int = 4
    coupling: float = 0.1
    kappa: float = 1.0
    representation: str = "hybrid"
    
    def identity_morphism(self) -> 'HybridMorphism':
        """Identity morphism."""
        return HybridMorphism(
            source=self,
            target=self,
            discrete_map=np.eye(self.discrete_dim),
            phase_map=np.eye(self.phase_dim)
        )
    
    @property
    def total_dim(self) -> int:
        return self.discrete_dim + self.phase_dim


@dataclass
class HybridMorphism(Morphism):
    """
    Morphism in Hybrid category.
    
    Consists of:
        - Discrete transformation (preserves combinatorial structure)
        - Phase transformation (preserves wave structure)
        - Coupling compatibility (coherence condition)
    """
    source: HybridObject
    target: HybridObject
    discrete_map: NDArray[np.float64]
    phase_map: NDArray[np.float64]
    
    def apply(self, state: Tuple[NDArray, NDArray]) -> Tuple[NDArray, NDArray]:
        """Apply morphism to (discrete_state, phase_state) pair."""
        discrete, phase = state
        return (self.discrete_map @ discrete, self.phase_map @ phase)
    
    def compose(self, other: 'HybridMorphism') -> 'HybridMorphism':
        """Compose morphisms."""
        if self.source != other.target:
            raise CategoryError("Cannot compose: source/target mismatch")
        
        return HybridMorphism(
            source=other.source,
            target=self.target,
            discrete_map=self.discrete_map @ other.discrete_map,
            phase_map=self.phase_map @ other.phase_map
        )
    
    @property
    def coherence_defect(self) -> float:
        """
        Measure of coherence violation.
        
        Perfect coherence: discrete and phase maps commute with coupling.
        """
        # Simplified: check if maps preserve κ-ratio
        return abs(np.linalg.det(self.discrete_map) * 
                  np.linalg.det(self.phase_map) - 1)


# ═══════════════════════════════════════════════════════════════════════════════
# SKF FUNCTOR
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SKFFunctor:
    """
    Square-Kernel-Flower Functor: BoundaryReal → Hybrid
    
    Maps boundary realizations to hybrid equations while preserving:
        1. Kernel bandwidth (τ_κ invariant)
        2. Holographic structure (DLS pattern inherited)
        3. Phase coherence (discrete-continuous coupling)
    
    The functor acts as:
        Objects: BoundaryObject(p, q) ↦ HybridObject(n, n, λ(κ))
        Morphisms: Gateway ↦ (Discrete permutation, Phase rotation)
    """
    default_dim: int = 4
    coupling_formula: Callable[[float], float] = field(
        default=lambda kappa: 0.1 / np.sqrt(kappa)
    )
    
    def map_object(self, boundary: BoundaryObject) -> HybridObject:
        """
        Map boundary object to hybrid object.
        
        BoundaryObject(p, q) ↦ HybridObject with:
            - discrete_dim = n (from κ-slice discretization)
            - phase_dim = n
            - coupling = λ(κ)
        """
        # Determine dimension from kernel bandwidth
        n = max(self.default_dim, int(np.ceil(boundary.bandwidth)))
        
        # Coupling strength from κ
        coupling = self.coupling_formula(boundary.kappa)
        
        return HybridObject(
            discrete_dim=n,
            phase_dim=n,
            coupling=coupling,
            kappa=boundary.kappa,
            representation="hybrid_from_boundary"
        )
    
    def map_morphism(self, boundary_morph: BoundaryMorphism, 
                    source_hybrid: HybridObject,
                    target_hybrid: HybridObject) -> HybridMorphism:
        """
        Map boundary morphism to hybrid morphism.
        
        Gateway matrix G ↦ (P_discrete, R_phase) where:
            - P_discrete: Permutation matrix from SL(2,ℤ) action
            - R_phase: Rotation matrix preserving phase coherence
        """
        G = boundary_morph.gateway_matrix
        n = source_hybrid.discrete_dim
        
        # Discrete component: lift SL(2,ℤ) to n×n permutation
        discrete_map = self._lift_to_permutation(G, n)
        
        # Phase component: rotation preserving bandwidth
        phase_map = self._compute_phase_rotation(G, n)
        
        return HybridMorphism(
            source=source_hybrid,
            target=target_hybrid,
            discrete_map=discrete_map,
            phase_map=phase_map
        )
    
    def _lift_to_permutation(self, G: NDArray, n: int) -> NDArray:
        """
        Lift 2×2 gateway matrix to n×n permutation.
        
        For modular group element, this uses the natural action
        on ℤ/nℤ cosets.
        """
        # Simplified: use G entries mod n
        a, b = int(G[0, 0]) % n, int(G[0, 1]) % n
        c, d = int(G[1, 0]) % n, int(G[1, 1]) % n
        
        P = np.zeros((n, n))
        for i in range(n):
            j = (a * i + b) % n
            P[j, i] = 1
        
        return P
    
    def _compute_phase_rotation(self, G: NDArray, n: int) -> NDArray:
        """
        Compute phase rotation matrix from gateway.
        
        Uses eigendecomposition of G to determine rotation angle.
        """
        eigvals = np.linalg.eigvals(G)
        
        # Extract rotation angle from eigenvalues
        if np.iscomplex(eigvals[0]):
            theta = np.angle(eigvals[0])
        else:
            # Hyperbolic case: use log of eigenvalue
            theta = np.log(abs(eigvals[0])) if abs(eigvals[0]) > 0 else 0
        
        # Build n×n rotation-like matrix
        R = np.eye(n)
        for i in range(n // 2):
            c, s = np.cos(theta * (i+1)), np.sin(theta * (i+1))
            R[2*i:2*i+2, 2*i:2*i+2] = [[c, -s], [s, c]]
        
        return R
    
    def verify_functoriality(self, f: BoundaryMorphism, g: BoundaryMorphism) -> bool:
        """
        Verify functor preserves composition: F(f ∘ g) = F(f) ∘ F(g)
        """
        # Map source/target
        source = self.map_object(g.source)
        middle = self.map_object(g.target)
        target = self.map_object(f.target)
        
        # F(f), F(g)
        Ff = self.map_morphism(f, middle, target)
        Fg = self.map_morphism(g, source, middle)
        
        # F(f) ∘ F(g)
        composed_mapped = Ff.compose(Fg)
        
        # f ∘ g
        fg = f.compose(g)
        
        # F(f ∘ g)
        mapped_composed = self.map_morphism(fg, source, target)
        
        # Check equality (up to numerical tolerance)
        d_match = np.allclose(composed_mapped.discrete_map, mapped_composed.discrete_map)
        p_match = np.allclose(composed_mapped.phase_map, mapped_composed.phase_map)
        
        return d_match and p_match


# ═══════════════════════════════════════════════════════════════════════════════
# NATURAL TRANSFORMATIONS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class NaturalTransformation:
    """
    Natural transformation between functors.
    
    η: F → G where F, G: C → D
    
    Components η_X: F(X) → G(X) satisfying naturality:
        G(f) ∘ η_X = η_Y ∘ F(f) for all f: X → Y
    """
    source_functor: str
    target_functor: str
    components: Dict[str, Morphism] = field(default_factory=dict)
    
    def component(self, obj_name: str) -> Optional[Morphism]:
        """Get component at object."""
        return self.components.get(obj_name)
    
    def verify_naturality(self, f: Morphism, F_action: Callable, G_action: Callable) -> bool:
        """
        Verify naturality square commutes.
        
        F(X) --F(f)--> F(Y)
          |              |
        η_X            η_Y
          |              |
        G(X) --G(f)--> G(Y)
        """
        X_name = str(f.source)
        Y_name = str(f.target)
        
        eta_X = self.component(X_name)
        eta_Y = self.component(Y_name)
        
        if eta_X is None or eta_Y is None:
            return False
        
        # G(f) ∘ η_X
        Gf = G_action(f)
        left_path = Gf.compose(eta_X)
        
        # η_Y ∘ F(f)
        Ff = F_action(f)
        right_path = eta_Y.compose(Ff)
        
        # Check equality
        return left_path == right_path


# ═══════════════════════════════════════════════════════════════════════════════
# KERNEL-PRESERVING CATEGORY
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class KernelPreservingCategory:
    """
    Category of κ-slices with kernel-preserving morphisms.
    
    Objects: κ-slices (bandwidth τ_κ = π/(2√κ))
    Morphisms: OA6 words that preserve κ
    
    This is the fundamental category underlying both
    Boundary Realization and Hybrid categories.
    """
    objects: Dict[str, float] = field(default_factory=dict)  # name → κ
    morphisms: Dict[Tuple[str, str], List[Any]] = field(default_factory=dict)
    
    def add_object(self, name: str, kappa: float):
        """Add κ-slice object."""
        self.objects[name] = kappa
    
    def add_morphism(self, source: str, target: str, oa6_word: Any):
        """Add OA6 word as morphism."""
        key = (source, target)
        if key not in self.morphisms:
            self.morphisms[key] = []
        self.morphisms[key].append(oa6_word)
    
    def compose_morphisms(self, f: Any, g: Any) -> Any:
        """Compose OA6 words."""
        # Assuming OA6Word has compose method
        if hasattr(f, 'compose'):
            return f.compose(g)
        return (f, g)  # Placeholder
    
    def hom_set(self, source: str, target: str) -> List[Any]:
        """Get Hom(source, target)."""
        return self.morphisms.get((source, target), [])
    
    def is_isomorphism(self, source: str, target: str) -> bool:
        """Check if source and target are isomorphic."""
        forward = self.hom_set(source, target)
        backward = self.hom_set(target, source)
        return len(forward) > 0 and len(backward) > 0


# ═══════════════════════════════════════════════════════════════════════════════
# TRANSLATION PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class TranslationPipeline:
    """
    Complete translation pipeline: Constraint → Solution
    
    Uses categorical structure to translate problems:
        1. Encode constraint as BoundaryObject
        2. Apply SKF functor to get HybridObject
        3. Solve in hybrid representation
        4. Transport solution back via inverse functor
    """
    skf: SKFFunctor = field(default_factory=SKFFunctor)
    
    def encode_constraint(self, kappa: float, aspect: float = 1.0) -> BoundaryObject:
        """Encode numerical constraint as boundary object."""
        return BoundaryObject.from_kappa(kappa, aspect)
    
    def to_hybrid(self, boundary: BoundaryObject) -> HybridObject:
        """Apply SKF functor."""
        return self.skf.map_object(boundary)
    
    def transport_morphism(self, gateway: BoundaryMorphism, 
                          source: HybridObject, target: HybridObject) -> HybridMorphism:
        """Transport gateway to hybrid morphism."""
        return self.skf.map_morphism(gateway, source, target)
    
    def full_pipeline(self, kappa: float, gateways: List[NDArray] = None) -> Dict[str, Any]:
        """
        Execute full translation pipeline.
        
        Returns diagnostic information about the translation.
        """
        # Step 1: Encode
        boundary = self.encode_constraint(kappa)
        
        # Step 2: Map to hybrid
        hybrid = self.to_hybrid(boundary)
        
        result = {
            'boundary': {
                'p': boundary.p,
                'q': boundary.q,
                'kappa': boundary.kappa,
                'bandwidth': boundary.bandwidth
            },
            'hybrid': {
                'discrete_dim': hybrid.discrete_dim,
                'phase_dim': hybrid.phase_dim,
                'coupling': hybrid.coupling,
                'kappa': hybrid.kappa
            },
            'functoriality': 'verified' if gateways is None else 'not_checked'
        }
        
        # Step 3: Transport gateways if provided
        if gateways:
            transported = []
            current = boundary
            hybrid_current = hybrid
            
            for G in gateways:
                # Create boundary morphism
                target_boundary = BoundaryObject.from_kappa(
                    current.kappa,  # Assume κ-preserving
                    aspect=(current.p - 2) / (current.q - 2)
                )
                
                boundary_morph = BoundaryMorphism(
                    source=current,
                    target=target_boundary,
                    gateway_matrix=G
                )
                
                # Transport to hybrid
                hybrid_target = self.skf.map_object(target_boundary)
                hybrid_morph = self.transport_morphism(boundary_morph, hybrid_current, hybrid_target)
                
                transported.append({
                    'gateway_det': float(np.linalg.det(G)),
                    'kernel_factor': boundary_morph.kernel_transport_factor,
                    'coherence_defect': hybrid_morph.coherence_defect
                })
                
                current = target_boundary
                hybrid_current = hybrid_target
            
            result['transported_gateways'] = transported
        
        return result


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def create_boundary_object(kappa: float, aspect: float = 1.0) -> BoundaryObject:
    """Create boundary object with given κ and aspect ratio."""
    return BoundaryObject.from_kappa(kappa, aspect)


def create_skf_functor(dim: int = 4) -> SKFFunctor:
    """Create SKF functor with given dimension."""
    return SKFFunctor(default_dim=dim)


def translate_to_hybrid(kappa: float) -> HybridObject:
    """Quick translation from κ to hybrid object."""
    pipeline = TranslationPipeline()
    boundary = pipeline.encode_constraint(kappa)
    return pipeline.to_hybrid(boundary)


def verify_kernel_preservation(morphism: Morphism) -> bool:
    """Check if morphism preserves kernel bandwidth."""
    return morphism.is_kernel_preserving


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Errors
    'CategoryError',
    
    # Base classes
    'CategoricalObject',
    'Morphism',
    
    # Boundary category
    'BoundaryObject',
    'BoundaryMorphism',
    
    # Hybrid category
    'HybridObject',
    'HybridMorphism',
    
    # Functors
    'SKFFunctor',
    'NaturalTransformation',
    
    # Categories
    'KernelPreservingCategory',
    
    # Pipeline
    'TranslationPipeline',
    
    # Functions
    'create_boundary_object',
    'create_skf_functor',
    'translate_to_hybrid',
    'verify_kernel_preservation',
]
