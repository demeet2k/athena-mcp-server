"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        FLOWER MODES MODULE                                   ║
║                                                                              ║
║  Wave-Side of the Universal Harmonic Framework                               ║
║                                                                              ║
║  Rose Curves: r = a·cos(kθ)                                                  ║
║    - k odd: k petals                                                         ║
║    - k even: 2k petals                                                       ║
║                                                                              ║
║  Symmetry Groups:                                                            ║
║    - Dihedral D_k (rotations + reflections)                                  ║
║    - Internal duality algebra Δ_k ≅ (ℤ₂)^{m_k}                               ║
║                                                                              ║
║  Interference Law:                                                           ║
║    |ψ₁ + ψ₂|² = a² + b² + 2ab·cos(Δθ)                                        ║
║                                                                              ║
║  Coding Connection:                                                          ║
║    Order 4 → 7-bit duality → (7,4) Hamming code                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Any, Callable
from enum import Enum
import numpy as np
from numpy.typing import NDArray


# ═══════════════════════════════════════════════════════════════════════════════
# ROSE CURVE DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class RoseCurve:
    """
    Rose curve (rhodonea curve): r = a·cos(kθ) or r = a·sin(kθ).
    
    Petal count:
    - k odd: exactly k petals
    - k even: exactly 2k petals
    
    The curve is a canonical 1D flower with k-fold symmetry.
    """
    amplitude: float = 1.0  # Parameter a
    order: int = 4          # Parameter k (harmonic frequency)
    use_sine: bool = False  # Use sin(kθ) instead of cos(kθ)
    
    @property
    def petal_count(self) -> int:
        """Number of petals."""
        return self.order if self.order % 2 == 1 else 2 * self.order
    
    @property
    def angular_period(self) -> float:
        """Period in θ for complete curve."""
        return 2 * np.pi if self.order % 2 == 1 else np.pi
    
    def radius(self, theta: float) -> float:
        """Compute r(θ) = a·cos(kθ) or a·sin(kθ)."""
        if self.use_sine:
            return self.amplitude * np.sin(self.order * theta)
        return self.amplitude * np.cos(self.order * theta)
    
    def point(self, theta: float) -> Tuple[float, float]:
        """Cartesian point (x, y) at angle θ."""
        r = self.radius(theta)
        return (r * np.cos(theta), r * np.sin(theta))
    
    def sample(self, n_points: int = 1000) -> Tuple[NDArray, NDArray]:
        """Sample the curve as (x, y) arrays."""
        theta = np.linspace(0, self.angular_period, n_points)
        r = np.array([self.radius(t) for t in theta])
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        return x, y
    
    def petal_angles(self) -> NDArray:
        """Angles of petal centers (where r is maximal)."""
        if self.order % 2 == 1:
            # k petals at θ = 2πj/k
            return np.array([2 * np.pi * j / self.order for j in range(self.order)])
        else:
            # 2k petals at θ = πj/k
            return np.array([np.pi * j / self.order for j in range(2 * self.order)])
    
    def rotate(self, phi: float) -> 'RoseCurve':
        """
        Rotate curve by angle φ.
        
        r = a·cos(k(θ - φ/k)) = a·cos(kθ - φ)
        Equivalent to phase shift in the argument.
        """
        # For rotation, we'd need to track phase; simplified here
        return RoseCurve(self.amplitude, self.order, self.use_sine)
    
    @classmethod
    def from_order(cls, k: int, a: float = 1.0) -> 'RoseCurve':
        """Create rose curve of order k."""
        return cls(amplitude=a, order=k)


# ═══════════════════════════════════════════════════════════════════════════════
# SPECIAL FLOWER ORDERS
# ═══════════════════════════════════════════════════════════════════════════════

class FlowerOrder(Enum):
    """Special flower orders with distinct properties."""
    BIFOLIUM = 2      # 2 petals (figure-eight shape)
    TRIFOLIUM = 3     # 3 petals (trefoil)
    QUADRIFOLIUM = 4  # 4 petals (four-leaf clover)
    PENTAFOLIUM = 5   # 5 petals (prime, no internal duality)
    HEXAFOLIUM = 6    # 6 petals (composite anomaly: 2×3)
    OCTOFOLIUM = 8    # 8 petals
    DECAFOLIUM = 10   # 10 petals
    DODECAFOLIUM = 12 # 12 petals


@dataclass
class FlowerProperties:
    """Properties of a flower of given order."""
    order: int
    petal_count: int
    duality_dimension: int  # m_k for Δ_k ≅ (ℤ₂)^{m_k}
    rotational_symmetry: int  # Order of cyclic group
    has_reflection: bool
    special_notes: str
    
    @classmethod
    def for_order(cls, k: int) -> 'FlowerProperties':
        """Get properties for order k flower."""
        petals = k if k % 2 == 1 else 2 * k
        
        # Duality dimensions (from the FLOWERS document)
        duality_dims = {
            2: 3,   # 3-bit duality
            3: 0,   # No internal duality (cyclic only)
            4: 7,   # 7-bit duality → Hamming (7,4)
            5: 0,   # Prime, no internal duality
            6: 3,   # Composite: 2×3 interaction
        }
        m_k = duality_dims.get(k, 0)
        
        notes = {
            2: "Figure-eight, 3-bit duality",
            3: "Trefoil, pure cyclic symmetry",
            4: "Quadrifolium, 7-bit duality ↔ Hamming(7,4)",
            5: "Prime order, no internal duality",
            6: "Composite anomaly: 2×3 factorization",
        }
        
        return cls(
            order=k,
            petal_count=petals,
            duality_dimension=m_k,
            rotational_symmetry=k,
            has_reflection=True,
            special_notes=notes.get(k, f"Order-{k} flower")
        )


# ═══════════════════════════════════════════════════════════════════════════════
# SYMMETRY GROUPS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class DihedralGroup:
    """
    Dihedral group D_k: symmetries of regular k-gon.
    
    Elements:
    - k rotations: r^j for j = 0, 1, ..., k-1
    - k reflections: s, sr, sr², ..., sr^{k-1}
    
    Order: |D_k| = 2k
    """
    order: int  # k
    
    @property
    def size(self) -> int:
        """Group order |D_k| = 2k."""
        return 2 * self.order
    
    def rotation_angle(self, j: int) -> float:
        """Angle for j-th rotation: 2πj/k."""
        return 2 * np.pi * (j % self.order) / self.order
    
    def rotation_matrix(self, j: int) -> NDArray:
        """Rotation matrix R_j."""
        theta = self.rotation_angle(j)
        c, s = np.cos(theta), np.sin(theta)
        return np.array([[c, -s], [s, c]])
    
    def reflection_matrix(self, j: int = 0) -> NDArray:
        """Reflection matrix (across axis at angle πj/k)."""
        theta = np.pi * j / self.order
        c, s = np.cos(2 * theta), np.sin(2 * theta)
        return np.array([[c, s], [s, -c]])
    
    def apply_rotation(self, point: Tuple[float, float], j: int) -> Tuple[float, float]:
        """Apply j-th rotation to point."""
        R = self.rotation_matrix(j)
        p = np.array(point)
        result = R @ p
        return (result[0], result[1])
    
    def orbit(self, point: Tuple[float, float]) -> List[Tuple[float, float]]:
        """Full orbit of point under D_k."""
        orbit_points = []
        for j in range(self.order):
            # Rotations
            orbit_points.append(self.apply_rotation(point, j))
            # Reflections
            p = np.array(point)
            S = self.reflection_matrix(j)
            reflected = S @ p
            orbit_points.append((reflected[0], reflected[1]))
        return orbit_points


@dataclass
class DualityAlgebra:
    """
    Internal duality algebra Δ_k ≅ (ℤ₂)^{m_k}.
    
    For order-4 flower: Δ_4 ≅ (ℤ₂)^7 ≅ F_2^7
    This connects to the (7,4) Hamming code.
    """
    order: int  # Flower order k
    dimension: int  # m_k
    
    @property
    def size(self) -> int:
        """Number of duality states: 2^{m_k}."""
        return 2 ** self.dimension
    
    def state_vector(self, index: int) -> NDArray:
        """Convert index to binary state vector."""
        bits = [(index >> i) & 1 for i in range(self.dimension)]
        return np.array(bits, dtype=int)
    
    def flip(self, state: NDArray, axis: int) -> NDArray:
        """Flip the specified axis (XOR with basis vector)."""
        result = state.copy()
        result[axis] = 1 - result[axis]
        return result
    
    def xor(self, state1: NDArray, state2: NDArray) -> NDArray:
        """XOR two states (group operation in (ℤ₂)^m)."""
        return (state1 + state2) % 2
    
    @classmethod
    def for_order(cls, k: int) -> 'DualityAlgebra':
        """Create duality algebra for order-k flower."""
        dims = {2: 3, 3: 0, 4: 7, 5: 0, 6: 3}
        m = dims.get(k, 0)
        return cls(k, m)


# ═══════════════════════════════════════════════════════════════════════════════
# HAMMING CODE CONNECTION (ORDER 4)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class HammingFlowerCode:
    """
    The 7-bit flower and the (7,4) Hamming code.
    
    For quadrifolium (order 4):
    - Δ_4 ≅ (ℤ₂)^7 ≅ F_2^7
    - Parity-check matrix H defines admissible duality states
    - Single-bit errors are detectable and correctable
    
    Fano plane incidence ↔ parity-check relations.
    """
    
    @staticmethod
    def parity_check_matrix() -> NDArray:
        """
        (7,4) Hamming code parity-check matrix H.
        
        H·x^T = 0 ⟺ x ∈ Hamming code
        """
        return np.array([
            [1, 0, 0, 1, 0, 1, 1],
            [0, 1, 0, 1, 1, 0, 1],
            [0, 0, 1, 0, 1, 1, 1]
        ], dtype=int)
    
    @staticmethod
    def generator_matrix() -> NDArray:
        """
        (7,4) Hamming code generator matrix G.
        
        Codewords: c = m·G for message m ∈ F_2^4
        """
        return np.array([
            [1, 0, 0, 0, 1, 1, 0],
            [0, 1, 0, 0, 1, 0, 1],
            [0, 0, 1, 0, 0, 1, 1],
            [0, 0, 0, 1, 1, 1, 1]
        ], dtype=int)
    
    def encode(self, message: NDArray) -> NDArray:
        """Encode 4-bit message to 7-bit codeword."""
        G = self.generator_matrix()
        return (message @ G) % 2
    
    def syndrome(self, received: NDArray) -> NDArray:
        """Compute syndrome s = H·r^T."""
        H = self.parity_check_matrix()
        return (H @ received) % 2
    
    def is_codeword(self, word: NDArray) -> bool:
        """Check if word is a valid codeword."""
        s = self.syndrome(word)
        return np.all(s == 0)
    
    def decode(self, received: NDArray) -> Tuple[NDArray, int]:
        """
        Decode received word, correcting single-bit errors.
        
        Returns (corrected, error_position).
        error_position = -1 if no error, else position 0-6.
        """
        s = self.syndrome(received)
        
        if np.all(s == 0):
            return received.copy(), -1
        
        # Syndrome gives binary representation of error position + 1
        error_pos = s[0] + 2*s[1] + 4*s[2] - 1
        
        corrected = received.copy()
        if 0 <= error_pos < 7:
            corrected[error_pos] = 1 - corrected[error_pos]
        
        return corrected, error_pos
    
    def duality_to_code(self, duality_state: NDArray) -> bool:
        """Check if duality state is an admissible codeword."""
        return self.is_codeword(duality_state)


# ═══════════════════════════════════════════════════════════════════════════════
# INTERFERENCE AND STANDING WAVES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class FlowerInterference:
    """
    Interference patterns for flower modes.
    
    Two flowers f_k1, f_k2 interfere according to:
    |f_k1 + f_k2|² = |f_k1|² + |f_k2|² + 2·Re(f_k1·f̄_k2)
    """
    
    @staticmethod
    def interference_pattern(k1: int, k2: int, 
                            theta: NDArray) -> NDArray:
        """
        Compute interference pattern of two rose modes.
        
        f_k(θ) = cos(kθ)
        """
        f1 = np.cos(k1 * theta)
        f2 = np.cos(k2 * theta)
        return (f1 + f2) ** 2
    
    @staticmethod
    def beat_frequency(k1: int, k2: int) -> int:
        """Beat frequency from interference."""
        return abs(k1 - k2)
    
    @staticmethod
    def sum_frequency(k1: int, k2: int) -> int:
        """Sum frequency from product."""
        return k1 + k2
    
    @staticmethod
    def standing_wave(k: int, theta: NDArray, 
                      amplitude: float = 1.0) -> NDArray:
        """
        Standing wave pattern for order k.
        
        ψ(θ) = A·cos(kθ)
        Energy density: |ψ|²
        """
        return amplitude * np.cos(k * theta)


# ═══════════════════════════════════════════════════════════════════════════════
# HELMHOLTZ MODES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class HelmholtzMode:
    """
    Separable solution of Helmholtz equation: ∇²ψ + ω²ψ = 0.
    
    In polar coordinates:
    ψ(r,θ) = R(r)·Θ(θ)
    
    Angular part: Θ(θ) = cos(kθ) or sin(kθ)
    Radial part: R(r) = J_k(ωr) (Bessel function)
    """
    angular_order: int  # k
    frequency: float    # ω
    
    def angular_part(self, theta: float, use_sine: bool = False) -> float:
        """Angular factor Θ(θ)."""
        if use_sine:
            return np.sin(self.angular_order * theta)
        return np.cos(self.angular_order * theta)
    
    def radial_part(self, r: float) -> float:
        """Radial factor R(r) = J_k(ωr)."""
        from scipy.special import jv
        return jv(self.angular_order, self.frequency * r)
    
    def evaluate(self, r: float, theta: float) -> float:
        """Full mode ψ(r,θ) = R(r)·Θ(θ)."""
        return self.radial_part(r) * self.angular_part(theta)
    
    def nodal_lines_angular(self) -> NDArray:
        """Angular positions of nodal lines (where Θ = 0)."""
        k = self.angular_order
        # cos(kθ) = 0 at θ = (2j+1)π/(2k)
        return np.array([(2*j + 1) * np.pi / (2 * k) 
                         for j in range(2 * k)])


# ═══════════════════════════════════════════════════════════════════════════════
# FLOWER MODE SPACE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class FlowerModeSpace:
    """
    Space of flower modes on the circle S¹.
    
    Basis: {cos(kθ), sin(kθ)} for k = 0, 1, 2, ...
    
    A general flower is a linear combination:
    f(θ) = a_0 + Σ_k [a_k·cos(kθ) + b_k·sin(kθ)]
    """
    max_order: int = 12
    
    def basis_function(self, k: int, theta: float, 
                       use_sine: bool = False) -> float:
        """Basis function cos(kθ) or sin(kθ)."""
        if use_sine:
            return np.sin(k * theta)
        return np.cos(k * theta)
    
    def expand(self, coeffs_cos: List[float], 
               coeffs_sin: List[float],
               theta: float) -> float:
        """
        Evaluate flower mode with given Fourier coefficients.
        
        f(θ) = Σ_k [a_k·cos(kθ) + b_k·sin(kθ)]
        """
        result = 0.0
        for k, (a, b) in enumerate(zip(coeffs_cos, coeffs_sin)):
            result += a * np.cos(k * theta) + b * np.sin(k * theta)
        return result
    
    def project(self, f: Callable[[float], float], 
                n_samples: int = 1000) -> Tuple[List[float], List[float]]:
        """
        Project function f onto flower mode basis.
        
        Returns (a_k, b_k) Fourier coefficients.
        """
        theta = np.linspace(0, 2*np.pi, n_samples, endpoint=False)
        f_values = np.array([f(t) for t in theta])
        
        coeffs_cos = []
        coeffs_sin = []
        
        for k in range(self.max_order + 1):
            cos_k = np.cos(k * theta)
            sin_k = np.sin(k * theta)
            
            a_k = 2 * np.mean(f_values * cos_k)
            b_k = 2 * np.mean(f_values * sin_k)
            
            if k == 0:
                a_k /= 2
            
            coeffs_cos.append(a_k)
            coeffs_sin.append(b_k)
        
        return coeffs_cos, coeffs_sin


# ═══════════════════════════════════════════════════════════════════════════════
# POLE BRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class FlowerPoleBridge:
    """
    Bridge between Flower Modes and four-pole framework.
    """
    
    @staticmethod
    def integration() -> str:
        return """
        FLOWER MODES ↔ FRAMEWORK
        
        Flowers = Wave-side (Yin/Circular) encoding
        
        Chart Mapping:
          Rose curves → ✿ Flower chart (continuous phase)
          Petal structure → k-fold symmetry
          Duality algebra → □ Square chart (discrete)
          
        Pole Correspondence:
          Θ (Fire) = Wave/phase/rotation
          Λ (Air) = Lattice/discrete sampling
          
        Special Orders:
          k=2: Bifolium (3-bit duality)
          k=3: Trifolium (pure cyclic)
          k=4: Quadrifolium (7-bit → Hamming)
          k=5: Pentafolium (prime, no duality)
          k=6: Hexafolium (2×3 anomaly)
        
        Key Equation:
          r(θ) = a·cos(kθ)
          
        Coding Connection:
          Δ_4 ≅ (ℤ₂)^7 ↔ (7,4) Hamming code
          Duality flips ↔ error patterns
          Fano plane ↔ parity checks
        """


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def rose_curve(order: int, amplitude: float = 1.0) -> RoseCurve:
    """Create rose curve of given order."""
    return RoseCurve(amplitude=amplitude, order=order)


def flower_properties(order: int) -> FlowerProperties:
    """Get properties for flower of given order."""
    return FlowerProperties.for_order(order)


def dihedral_group(order: int) -> DihedralGroup:
    """Create dihedral group D_k."""
    return DihedralGroup(order)


def duality_algebra(order: int) -> DualityAlgebra:
    """Create duality algebra for flower order."""
    return DualityAlgebra.for_order(order)


def hamming_flower() -> HammingFlowerCode:
    """Create Hamming (7,4) flower code."""
    return HammingFlowerCode()


def flower_interference() -> FlowerInterference:
    """Create flower interference calculator."""
    return FlowerInterference()


def helmholtz_mode(k: int, omega: float = 1.0) -> HelmholtzMode:
    """Create Helmholtz mode."""
    return HelmholtzMode(k, omega)


def flower_mode_space(max_order: int = 12) -> FlowerModeSpace:
    """Create flower mode space."""
    return FlowerModeSpace(max_order)


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Rose Curves
    'RoseCurve',
    'FlowerOrder',
    'FlowerProperties',
    
    # Symmetry
    'DihedralGroup',
    'DualityAlgebra',
    
    # Hamming Code
    'HammingFlowerCode',
    
    # Interference
    'FlowerInterference',
    
    # Helmholtz
    'HelmholtzMode',
    
    # Mode Space
    'FlowerModeSpace',
    
    # Bridge
    'FlowerPoleBridge',
    
    # Functions
    'rose_curve',
    'flower_properties',
    'dihedral_group',
    'duality_algebra',
    'hamming_flower',
    'flower_interference',
    'helmholtz_mode',
    'flower_mode_space',
]
