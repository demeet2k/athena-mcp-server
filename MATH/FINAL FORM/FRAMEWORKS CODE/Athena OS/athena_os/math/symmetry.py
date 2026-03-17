"""
ATHENA OS - Symmetry Geometry
=============================
Poles, Shadows, Crosses and Dihedral Actions in Lens Space.

The symmetry engine imports phase geometry through lenses:
- 90° rotation: R(x) = T⁻¹(T(x) + π/2)
- Negation: N(x) = T⁻¹(T(x) + π)
- Mirror: S(x) = T⁻¹(-T(x))
- Diagonal: D(x) = T⁻¹(π/2 - T(x))

These operators satisfy dihedral relations (D₄):
- Spin/counter-spin
- Mirrors and anti-symmetries
- Cross-symmetries between pole families

Lattice Atlas:
- Axis lattices: sin t = 0 (πℤ), cos t = 0 (π/2 + πℤ)
- Diagonal lattices: sin t = cos t (π/4 + πℤ), sin t = -cos t (-π/4 + πℤ)
- Pullback T⁻¹(L) generates constant families in x-space

Unification Bridge:
x^i = e^{i ln x} = cos(ln x) + i sin(ln x)
Multiplication → Addition → Rotation
"""

from __future__ import annotations
from enum import IntEnum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable, Set
import numpy as np

from .lenses import Lens, LogLens, TrigPhaseLens, PHI


# =============================================================================
# DIHEDRAL GROUP D₄ - THE SYMMETRY ENGINE
# =============================================================================

class DihedralElement(IntEnum):
    """
    Elements of D₄ (dihedral group of order 8).
    
    Actions on (sin, cos) space:
    - IDENTITY: (sin, cos) → (sin, cos)
    - ROT90: (sin, cos) → (cos, -sin)
    - ROT180: (sin, cos) → (-sin, -cos)
    - ROT270: (sin, cos) → (-cos, sin)
    - MIRROR_H: (sin, cos) → (sin, -cos)
    - MIRROR_V: (sin, cos) → (-sin, cos)
    - MIRROR_D1: (sin, cos) → (cos, sin)
    - MIRROR_D2: (sin, cos) → (-cos, -sin)
    """
    IDENTITY = 0
    ROT90 = 1      # Quarter turn (spin)
    ROT180 = 2     # Half turn (negation)
    ROT270 = 3     # Three-quarter turn (counter-spin)
    MIRROR_H = 4   # Horizontal mirror
    MIRROR_V = 5   # Vertical mirror
    MIRROR_D1 = 6  # Diagonal mirror (+ slope)
    MIRROR_D2 = 7  # Anti-diagonal mirror (- slope)


@dataclass
class D4Action:
    """
    D₄ group action with multiplication table.
    
    Multiplication table stored for composition.
    """
    
    # Phase shifts for rotations
    ROTATION_PHASES: Dict[DihedralElement, float] = field(default_factory=lambda: {
        DihedralElement.IDENTITY: 0,
        DihedralElement.ROT90: np.pi / 2,
        DihedralElement.ROT180: np.pi,
        DihedralElement.ROT270: 3 * np.pi / 2,
    })
    
    @staticmethod
    def is_rotation(elem: DihedralElement) -> bool:
        """Check if element is a rotation."""
        return elem.value < 4
    
    @staticmethod
    def is_reflection(elem: DihedralElement) -> bool:
        """Check if element is a reflection."""
        return elem.value >= 4
    
    @staticmethod
    def compose(a: DihedralElement, b: DihedralElement) -> DihedralElement:
        """Compose two D₄ elements: a ∘ b."""
        # Cayley table for D₄
        table = [
            [0, 1, 2, 3, 4, 5, 6, 7],  # IDENTITY
            [1, 2, 3, 0, 7, 6, 4, 5],  # ROT90
            [2, 3, 0, 1, 5, 4, 7, 6],  # ROT180
            [3, 0, 1, 2, 6, 7, 5, 4],  # ROT270
            [4, 6, 5, 7, 0, 2, 1, 3],  # MIRROR_H
            [5, 7, 4, 6, 2, 0, 3, 1],  # MIRROR_V
            [6, 5, 7, 4, 3, 1, 0, 2],  # MIRROR_D1
            [7, 4, 6, 5, 1, 3, 2, 0],  # MIRROR_D2
        ]
        return DihedralElement(table[a.value][b.value])
    
    @staticmethod
    def inverse(elem: DihedralElement) -> DihedralElement:
        """Get inverse element."""
        # Rotations: inverse is -rotation (mod 4)
        # Reflections: self-inverse
        inverses = [0, 3, 2, 1, 4, 5, 6, 7]
        return DihedralElement(inverses[elem.value])
    
    @staticmethod
    def apply_to_angle(elem: DihedralElement, theta: float) -> float:
        """
        Apply D₄ element to an angle θ.
        
        Rotations: θ → θ + phase
        Reflections: θ → ±(π/2 - θ) or ±θ depending on axis
        """
        if elem == DihedralElement.IDENTITY:
            return theta
        elif elem == DihedralElement.ROT90:
            return theta + np.pi / 2
        elif elem == DihedralElement.ROT180:
            return theta + np.pi
        elif elem == DihedralElement.ROT270:
            return theta + 3 * np.pi / 2
        elif elem == DihedralElement.MIRROR_H:
            return -theta
        elif elem == DihedralElement.MIRROR_V:
            return np.pi - theta
        elif elem == DihedralElement.MIRROR_D1:
            return np.pi / 2 - theta
        elif elem == DihedralElement.MIRROR_D2:
            return -np.pi / 2 - theta
        return theta


# =============================================================================
# SYMMETRY OPERATORS ON LENS SPACE
# =============================================================================

class SymmetryOperator:
    """
    A symmetry operator transported through a lens.
    
    Base operators in t-space (angle space):
    - R (90° rotation): t → t + π/2
    - N (negation): t → t + π
    - S (mirror): t → -t
    - D (diagonal): t → π/2 - t
    
    Transported to x-space: Op(x) = T⁻¹(op(T(x)))
    """
    
    def __init__(self, lens: Lens, dihedral_elem: DihedralElement):
        self.lens = lens
        self.element = dihedral_elem
    
    def __call__(self, x: float) -> float:
        """Apply the transported symmetry operator."""
        t = self.lens.forward(x)
        t_new = D4Action.apply_to_angle(self.element, t)
        return self.lens.inverse(t_new)
    
    @property
    def name(self) -> str:
        return f"{self.element.name}_via_{self.lens.name}"
    
    def compose(self, other: 'SymmetryOperator') -> 'SymmetryOperator':
        """Compose with another symmetry operator (same lens)."""
        if self.lens != other.lens:
            raise ValueError("Cannot compose operators with different lenses")
        new_elem = D4Action.compose(self.element, other.element)
        return SymmetryOperator(self.lens, new_elem)
    
    def inverse(self) -> 'SymmetryOperator':
        """Get inverse operator."""
        return SymmetryOperator(self.lens, D4Action.inverse(self.element))


def create_rotation_operator(lens: Lens) -> SymmetryOperator:
    """
    Create 90° rotation: R(x) = T⁻¹(T(x) + π/2)
    """
    return SymmetryOperator(lens, DihedralElement.ROT90)


def create_negation_operator(lens: Lens) -> SymmetryOperator:
    """
    Create negation (180°): N(x) = T⁻¹(T(x) + π)
    """
    return SymmetryOperator(lens, DihedralElement.ROT180)


def create_mirror_operator(lens: Lens) -> SymmetryOperator:
    """
    Create mirror: S(x) = T⁻¹(-T(x))
    """
    return SymmetryOperator(lens, DihedralElement.MIRROR_H)


def create_diagonal_operator(lens: Lens) -> SymmetryOperator:
    """
    Create diagonal swap: D(x) = T⁻¹(π/2 - T(x))
    """
    return SymmetryOperator(lens, DihedralElement.MIRROR_D1)


# =============================================================================
# POLES AND SHADOWS
# =============================================================================

class PoleType(IntEnum):
    """Types of poles in the symmetry crystal."""
    PRIMARY = 0    # Original expression
    ROTATED = 1    # 90° rotated shadow
    NEGATED = 2    # 180° rotated (anti-pole)
    COUNTER = 3    # 270° rotated shadow


@dataclass
class Pole:
    """
    A pole in the symmetry crystal.
    
    Poles are chosen primitive operators/expressions.
    Shadows are conjugates in rotated coordinates.
    """
    expression: Callable[[float], float]
    lens: Lens
    pole_type: PoleType = PoleType.PRIMARY
    name: str = "pole"
    
    def evaluate(self, x: float) -> float:
        """Evaluate the pole expression at x."""
        return self.expression(x)
    
    def shadow(self, rotation: DihedralElement) -> 'Pole':
        """
        Generate a shadow pole via rotation.
        
        Shadow = T⁻¹ ∘ original ∘ T, then rotated.
        """
        op = SymmetryOperator(self.lens, rotation)
        
        def shadow_expr(x: float) -> float:
            # Apply rotation in t-space
            x_rot = op.inverse()(x)
            return self.expression(x_rot)
        
        # Determine shadow type
        if rotation == DihedralElement.ROT90:
            new_type = PoleType.ROTATED
        elif rotation == DihedralElement.ROT180:
            new_type = PoleType.NEGATED
        elif rotation == DihedralElement.ROT270:
            new_type = PoleType.COUNTER
        else:
            new_type = self.pole_type
        
        return Pole(
            expression=shadow_expr,
            lens=self.lens,
            pole_type=new_type,
            name=f"{self.name}_{rotation.name}"
        )
    
    def cross_symmetry(self, other: 'Pole') -> List[float]:
        """
        Find cross-symmetry points where this pole equals another.
        
        Z(F, G) = {x: F(x) = G(x)} = Z(F - G)
        """
        # Numerical search for intersection
        results = []
        a, b = self.lens.domain
        if not np.isfinite(a):
            a = 0.01
        if not np.isfinite(b):
            b = 100
        
        xs = np.linspace(a, b, 1000)
        for i in range(len(xs) - 1):
            try:
                f1 = self.evaluate(xs[i]) - other.evaluate(xs[i])
                f2 = self.evaluate(xs[i+1]) - other.evaluate(xs[i+1])
                
                if f1 * f2 < 0:  # Sign change
                    # Bisection
                    lo, hi = xs[i], xs[i+1]
                    for _ in range(50):
                        mid = (lo + hi) / 2
                        fm = self.evaluate(mid) - other.evaluate(mid)
                        if abs(fm) < 1e-12:
                            break
                        if fm * f1 < 0:
                            hi = mid
                        else:
                            lo = mid
                    results.append((lo + hi) / 2)
            except (ValueError, OverflowError):
                pass
        
        return results


# =============================================================================
# LATTICE ATLAS - ZERO SETS AND PREIMAGES
# =============================================================================

class LatticeType(IntEnum):
    """Types of canonical lattices in t-space."""
    SIN_ZEROS = 0      # sin t = 0: t ∈ πℤ
    COS_ZEROS = 1      # cos t = 0: t ∈ π/2 + πℤ
    DIAGONAL_POS = 2   # sin t = cos t: t ∈ π/4 + πℤ
    DIAGONAL_NEG = 3   # sin t = -cos t: t ∈ -π/4 + πℤ


@dataclass
class Lattice:
    """
    A lattice in t-space with pullback to x-space.
    
    Lattice L in t-space: {base + k·period : k ∈ ℤ}
    Pullback T⁻¹(L): infinite family of constants in x-space
    """
    base: float
    period: float
    lattice_type: LatticeType
    name: str = "lattice"
    
    def points(self, n_terms: int = 10) -> List[float]:
        """Generate lattice points in t-space."""
        return [self.base + k * self.period for k in range(-n_terms, n_terms + 1)]
    
    def pullback(self, lens: Lens, n_terms: int = 10) -> List[float]:
        """
        Pull back lattice through lens: T⁻¹(L)
        
        This generates a family of constants in x-space.
        """
        results = []
        for t in self.points(n_terms):
            try:
                x = lens.inverse(t)
                if lens.in_domain(x):
                    results.append(x)
            except (ValueError, OverflowError):
                pass
        return sorted(results)
    
    def contains(self, t: float, tolerance: float = 1e-10) -> bool:
        """Check if t is in this lattice."""
        # t = base + k·period → k = (t - base) / period
        if abs(self.period) < 1e-15:
            return abs(t - self.base) < tolerance
        
        k = (t - self.base) / self.period
        return abs(k - round(k)) < tolerance


# Standard lattices
SIN_ZERO_LATTICE = Lattice(
    base=0, period=np.pi, lattice_type=LatticeType.SIN_ZEROS,
    name="sin_zeros"
)

COS_ZERO_LATTICE = Lattice(
    base=np.pi/2, period=np.pi, lattice_type=LatticeType.COS_ZEROS,
    name="cos_zeros"
)

DIAGONAL_POS_LATTICE = Lattice(
    base=np.pi/4, period=np.pi, lattice_type=LatticeType.DIAGONAL_POS,
    name="diagonal_pos"  # sin t = cos t
)

DIAGONAL_NEG_LATTICE = Lattice(
    base=-np.pi/4, period=np.pi, lattice_type=LatticeType.DIAGONAL_NEG,
    name="diagonal_neg"  # sin t = -cos t
)


class LatticeAtlas:
    """
    Complete atlas of canonical lattices with pullback operations.
    
    The lattice atlas holographically encodes infinite families
    of constants through pullback: T⁻¹(L).
    """
    
    def __init__(self):
        self.lattices: Dict[str, Lattice] = {
            "sin_zeros": SIN_ZERO_LATTICE,
            "cos_zeros": COS_ZERO_LATTICE,
            "diagonal_pos": DIAGONAL_POS_LATTICE,
            "diagonal_neg": DIAGONAL_NEG_LATTICE,
        }
    
    def add_lattice(self, name: str, base: float, period: float) -> Lattice:
        """Add a custom lattice."""
        lattice = Lattice(
            base=base, period=period,
            lattice_type=LatticeType.SIN_ZEROS,  # Generic
            name=name
        )
        self.lattices[name] = lattice
        return lattice
    
    def pullback_all(self, lens: Lens, n_terms: int = 5) -> Dict[str, List[float]]:
        """Pull back all lattices through a lens."""
        return {
            name: lattice.pullback(lens, n_terms)
            for name, lattice in self.lattices.items()
        }
    
    def axis_preimages(self, lens: Lens, n_terms: int = 10) -> Dict[str, List[float]]:
        """Get axis preimages (sin=0, cos=0)."""
        return {
            "sin_zeros": SIN_ZERO_LATTICE.pullback(lens, n_terms),
            "cos_zeros": COS_ZERO_LATTICE.pullback(lens, n_terms),
        }
    
    def diagonal_preimages(self, lens: Lens, n_terms: int = 10) -> Dict[str, List[float]]:
        """Get diagonal preimages (sin=cos, sin=-cos)."""
        return {
            "diagonal_pos": DIAGONAL_POS_LATTICE.pullback(lens, n_terms),
            "diagonal_neg": DIAGONAL_NEG_LATTICE.pullback(lens, n_terms),
        }


# =============================================================================
# UNIFICATION BRIDGE: SCALE ↔ TRANSLATION ↔ ROTATION
# =============================================================================

class PhaseBridge:
    """
    The unification bridge: x^i = e^{i ln x} = cos(ln x) + i sin(ln x)
    
    This exhibits the chain:
    - Multiplication in x → Addition in ln x → Rotation in e^{i ln x}
    
    Power/radical maps become scaling in log space:
    x → x^p  ↔  ln x → p·ln x
    
    Square/sqrt and sin/cos are two faces of one geometric mechanism:
    scaling and phase rotation in appropriate coordinates.
    """
    
    @staticmethod
    def phase_from_real(x: float) -> complex:
        """
        Compute x^i = e^{i ln x}
        
        This is the bridge from real scaling to phase rotation.
        """
        if x <= 0:
            raise ValueError("Phase bridge requires x > 0")
        return np.exp(1j * np.log(x))
    
    @staticmethod
    def phase_components(x: float) -> Tuple[float, float]:
        """
        Return (cos(ln x), sin(ln x))
        
        These are the real and imaginary parts of x^i.
        """
        if x <= 0:
            raise ValueError("Phase bridge requires x > 0")
        ln_x = np.log(x)
        return np.cos(ln_x), np.sin(ln_x)
    
    @staticmethod
    def power_as_rotation(x: float, p: float) -> Tuple[float, float]:
        """
        View x^p as rotation + scaling in log-phase space.
        
        x^p = e^{p ln x}
        
        For complex: (x^p)^i = x^{ip} = e^{ip ln x}
        Phase angle: p·ln(x)
        """
        ln_x = np.log(x)
        return p * ln_x, np.exp(p * ln_x)  # (phase angle, magnitude)
    
    @staticmethod
    def multiplication_to_rotation(a: float, b: float) -> Tuple[float, float]:
        """
        Show how multiplication becomes rotation:
        (a·b)^i = a^i · b^i
        
        Returns (phase_product, phase_a + phase_b)
        """
        phase_a = np.log(a)
        phase_b = np.log(b)
        return phase_a + phase_b, np.log(a * b)  # Should be equal


# =============================================================================
# PHI-INDEXED SYMMETRIES
# =============================================================================

class PhiSymmetry:
    """
    φ-indexed symmetry operations.
    
    In φ-log space, φ-scaling becomes integer translation:
    x → φx  ↔  s → s + 1 (where s = log_φ x)
    
    In trig-phase space (T = π/2 · log_φ x):
    x → φx  ↔  T → T + π/2 (quarter turn)
    
    This makes φ a native step size in the symmetry crystal.
    """
    
    def __init__(self, lens: TrigPhaseLens = None):
        self.lens = lens or TrigPhaseLens()
    
    def phi_translate(self, x: float, n: int = 1) -> float:
        """
        φ-translation: x → φⁿ·x
        
        In lens space: T(x) → T(x) + n·π/2
        """
        return (PHI ** n) * x
    
    def quarter_turn_family(self, x: float) -> List[float]:
        """
        Generate the 4-element orbit under quarter turns:
        {x, φx, φ²x, φ³x}
        """
        return [self.phi_translate(x, n) for n in range(4)]
    
    def phi_lattice_constants(self, k: int, n_terms: int = 5) -> List[float]:
        """
        Generate constants at T⁻¹(k·π/4 + n·π/2).
        
        k=0: axis (sin=0)
        k=1: diagonal (sin=cos)
        k=2: axis (cos=0)
        k=3: diagonal (sin=-cos)
        """
        lattice = Lattice(
            base=k * np.pi / 4,
            period=np.pi / 2,
            lattice_type=LatticeType(k % 4),
            name=f"phi_k{k}"
        )
        return lattice.pullback(self.lens, n_terms)


# =============================================================================
# VALIDATION
# =============================================================================

def validate_symmetry_geometry() -> bool:
    """Validate symmetry geometry."""
    # D₄ group operations
    assert D4Action.compose(DihedralElement.ROT90, DihedralElement.ROT90) == DihedralElement.ROT180
    assert D4Action.compose(DihedralElement.ROT180, DihedralElement.ROT180) == DihedralElement.IDENTITY
    assert D4Action.inverse(DihedralElement.ROT90) == DihedralElement.ROT270
    
    # Symmetry operators
    phi_lens = TrigPhaseLens()
    rot90 = create_rotation_operator(phi_lens)
    rot180 = create_negation_operator(phi_lens)
    
    # Test that rotation by π gives same as φ² scaling
    x = 2.0
    # T(φ²x) = T(x) + π
    x_rotated = rot180(x)
    x_phi2 = PHI * PHI * x
    assert abs(phi_lens.forward(x_rotated) - phi_lens.forward(x) - np.pi) < 1e-8
    
    # Lattice pullback
    atlas = LatticeAtlas()
    sin_zeros = SIN_ZERO_LATTICE.pullback(phi_lens, 5)
    assert len(sin_zeros) > 0
    
    # Check that pullback points satisfy sin(T(x)) ≈ 0
    for x in sin_zeros:
        t = phi_lens.forward(x)
        assert abs(np.sin(t)) < 1e-8
    
    # Phase bridge
    x = 2.5
    phase = PhaseBridge.phase_from_real(x)
    cos_ln, sin_ln = PhaseBridge.phase_components(x)
    assert abs(phase.real - cos_ln) < 1e-10
    assert abs(phase.imag - sin_ln) < 1e-10
    
    # φ symmetry
    phi_sym = PhiSymmetry()
    x = 1.5
    orbit = phi_sym.quarter_turn_family(x)
    assert len(orbit) == 4
    assert abs(orbit[1] - PHI * x) < 1e-10
    
    return True


if __name__ == "__main__":
    print("Validating Symmetry Geometry...")
    assert validate_symmetry_geometry()
    print("✓ Symmetry Geometry validated")
    
    # Demo
    print("\n=== D₄ Group Demo ===")
    print(f"ROT90 ∘ ROT90 = {D4Action.compose(DihedralElement.ROT90, DihedralElement.ROT90).name}")
    print(f"ROT90⁻¹ = {D4Action.inverse(DihedralElement.ROT90).name}")
    
    print("\n=== Lattice Pullback Demo ===")
    phi_lens = TrigPhaseLens()
    atlas = LatticeAtlas()
    
    preimages = atlas.pullback_all(phi_lens, 3)
    for name, values in preimages.items():
        print(f"  {name}: {[f'{v:.4f}' for v in values[:5]]}")
    
    print("\n=== Phase Bridge Demo ===")
    x = np.e  # e
    phase = PhaseBridge.phase_from_real(x)
    print(f"e^i = cos(1) + i·sin(1) = {phase.real:.4f} + {phase.imag:.4f}i")
