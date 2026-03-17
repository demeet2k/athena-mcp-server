"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    CYCLOTOMIC MANIFOLD MODULE (QCM)                          ║
║                                                                              ║
║  Quadrature-Cyclotomic Manifold: ΘΛ-Plane                                    ║
║                                                                              ║
║  Two Realms:                                                                 ║
║    Θ (Fire/Flower) = Continuous phase space (amplitudes, rotations)          ║
║    Λ (Air/Square)  = Discrete phase lattice (modular, cyclotomic)            ║
║                                                                              ║
║  Core Laws:                                                                  ║
║    Θ-Calculus: ψ = r·e^{iθ}, rotation, interference, orthogonality          ║
║    Λ-Calculus: k ∈ ℤ_N, ω_N = e^{2πi/N}, congruence, gcd, cyclic            ║
║                                                                              ║
║  Bridges:                                                                    ║
║    Meas (Θ→α): Born map |ψ|²                                                ║
║    Lift (Λ→Θ): Embed discrete into continuous phase                         ║
║    Quantize (Θ→Λ): Sample continuous phase to lattice                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Any, Callable, Union
from enum import Enum
import numpy as np
from numpy.typing import NDArray
import cmath


# ═══════════════════════════════════════════════════════════════════════════════
# QCM CODEX STRUCTURE
# ═══════════════════════════════════════════════════════════════════════════════

class QCMSection(Enum):
    """QCM Codex sections."""
    PRIMITIVES = "QCM-0"      # Primitives & Z-points
    TYPES = "QCM-1"           # Types & coordinate systems
    THETA_CALC = "QCM-2"      # Θ-calculus (phase, rotation)
    LAMBDA_CALC = "QCM-3"     # Λ-calculus (modular, congruence)
    BRIDGES = "QCM-4"         # Amp/Meas, Lift/Quant
    FOURIER = "QCM-5"         # DFT/IDFT, Parseval
    MEANS = "QCM-6"           # GM/RMS as centers
    TUNNELS = "QCM-7"         # Contradiction resolution
    INVARIANTS = "QCM-8"      # Certificates
    SCHEMA = "QCM-9"          # Implementation API


class ZeroType(Enum):
    """The three zeros (do not mix them)."""
    SCALAR = "alpha_0"      # α-0: 0 ∈ ℝ
    AMPLITUDE = "theta_0"   # Θ-0: 0 ∈ ℂ (no signal)
    BALANCED = "z_bit"      # Z-bit: |+⟩ = (|0⟩+|1⟩)/√2 (state center)


# ═══════════════════════════════════════════════════════════════════════════════
# Θ-REALM (CONTINUOUS PHASE SPACE)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ThetaScalar:
    """
    Θ-Scalar: single amplitude ψ ∈ ℂ.
    
    Polar form: ψ = r·e^{iθ} where r ≥ 0, θ ∈ ℝ
    """
    value: complex
    
    @property
    def r(self) -> float:
        """Magnitude (energy/power potential)."""
        return abs(self.value)
    
    @property
    def theta(self) -> float:
        """Phase angle (relationship/direction)."""
        return cmath.phase(self.value)
    
    @property
    def polar(self) -> Tuple[float, float]:
        """Polar form (r, θ)."""
        return (self.r, self.theta)
    
    def rotate(self, phi: float) -> 'ThetaScalar':
        """Rotation operator: ψ ↦ e^{iφ}ψ."""
        return ThetaScalar(self.value * np.exp(1j * phi))
    
    def rotate_90(self) -> 'ThetaScalar':
        """90° rotation: ψ ↦ iψ."""
        return ThetaScalar(1j * self.value)
    
    def root_half(self) -> 'ThetaScalar':
        """
        The "1/2 IN" operator: principal square root.
        
        √(r·e^{iθ}) = √r · e^{iθ/2}
        
        This is why √(-1) = i: -1 = e^{iπ} → √(-1) = e^{iπ/2} = i
        """
        return ThetaScalar(cmath.sqrt(self.value))
    
    def measure(self) -> float:
        """
        Born measurement: Meas(ψ) = |ψ|².
        
        Returns scalar "Earth-readout" (probability/energy/power).
        Phase is not visible after measurement.
        """
        return abs(self.value) ** 2
    
    @classmethod
    def from_polar(cls, r: float, theta: float) -> 'ThetaScalar':
        """Create from polar form."""
        return cls(r * np.exp(1j * theta))


@dataclass
class ThetaVector:
    """
    Θ-Vector: state vector ψ ∈ ℂ^d.
    
    Inner product: ⟨u,v⟩ = Σ_j ū_j v_j
    Norm: |u| = √⟨u,u⟩
    """
    components: NDArray  # Complex array
    
    @property
    def dim(self) -> int:
        return len(self.components)
    
    def inner(self, other: 'ThetaVector') -> complex:
        """Inner product ⟨self, other⟩."""
        return np.vdot(self.components, other.components)
    
    @property
    def norm(self) -> float:
        """Norm |ψ|."""
        return np.sqrt(np.real(self.inner(self)))
    
    def is_orthogonal(self, other: 'ThetaVector', tol: float = 1e-10) -> bool:
        """Check orthogonality: u ⊥ v ⟺ ⟨u,v⟩ = 0."""
        return abs(self.inner(other)) < tol
    
    def normalize(self) -> 'ThetaVector':
        """Normalize to unit vector."""
        n = self.norm
        if n < 1e-15:
            return self
        return ThetaVector(self.components / n)
    
    def measure_in_basis(self, basis: List['ThetaVector']) -> NDArray:
        """
        Measure in orthonormal basis.
        
        Returns probability distribution over basis states.
        """
        probs = []
        for b in basis:
            prob = abs(self.inner(b)) ** 2
            probs.append(prob)
        return np.array(probs)


# ═══════════════════════════════════════════════════════════════════════════════
# Θ-CALCULUS: INTERFERENCE LAW
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ThetaInterference:
    """
    The master Θ-addition law: Interference.
    
    For ψ₁ = a·e^{iθ₁}, ψ₂ = b·e^{iθ₂}:
    |ψ₁ + ψ₂|² = a² + b² + 2ab·cos(Δθ), where Δθ = θ₂ - θ₁
    """
    
    @staticmethod
    def interference_norm_squared(psi1: ThetaScalar, psi2: ThetaScalar) -> float:
        """Compute |ψ₁ + ψ₂|²."""
        a, theta1 = psi1.polar
        b, theta2 = psi2.polar
        delta_theta = theta2 - theta1
        return a**2 + b**2 + 2*a*b*np.cos(delta_theta)
    
    @staticmethod
    def quadrature_sum(a: float, b: float) -> float:
        """
        Orthogonal/quadrature addition (Δθ = π/2).
        
        a ⊞ b = √(a² + b²)
        
        This is the Pythagorean sum / RMS-style addition.
        """
        return np.sqrt(a**2 + b**2)
    
    @staticmethod
    def aligned_sum(a: float, b: float) -> float:
        """Aligned phases (Δθ = 0): |ψ₁ + ψ₂|² = (a+b)²."""
        return (a + b)**2
    
    @staticmethod
    def anti_aligned_sum(a: float, b: float) -> float:
        """Anti-aligned phases (Δθ = π): |ψ₁ + ψ₂|² = (a-b)²."""
        return (a - b)**2
    
    @staticmethod
    def general_sum(a: float, b: float, delta_theta: float) -> float:
        """General interference at arbitrary phase difference."""
        return a**2 + b**2 + 2*a*b*np.cos(delta_theta)


# ═══════════════════════════════════════════════════════════════════════════════
# Λ-REALM (DISCRETE PHASE LATTICE)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class LambdaLattice:
    """
    Λ-Realm: Finite gear with N positions.
    
    Objects:
    - Λ-index: k ∈ ℤ_N (clock positions)
    - Cyclotomic phases: μ_N = {e^{2πik/N} : k ∈ ℤ_N}
    - Λ-pattern: function x: ℤ_N → ℂ
    """
    N: int
    
    @property
    def omega(self) -> complex:
        """Primitive Nth root of unity: ω_N = e^{2πi/N}."""
        return np.exp(2j * np.pi / self.N)
    
    def cyclotomic_phase(self, k: int) -> complex:
        """Get cyclotomic phase ω_N^k."""
        return self.omega ** (k % self.N)
    
    @property
    def all_phases(self) -> NDArray:
        """All N cyclotomic phases."""
        return np.array([self.cyclotomic_phase(k) for k in range(self.N)])
    
    def wrap(self, k: int) -> int:
        """Wrap to ℤ_N: k mod N."""
        return k % self.N
    
    def add_mod(self, a: int, b: int) -> int:
        """Addition in ℤ_N."""
        return (a + b) % self.N
    
    def mult_mod(self, a: int, b: int) -> int:
        """Multiplication in ℤ_N."""
        return (a * b) % self.N
    
    def is_unit(self, a: int) -> bool:
        """Check if a is a unit in ℤ_N (gcd(a, N) = 1)."""
        from math import gcd
        return gcd(a % self.N, self.N) == 1
    
    def inverse(self, a: int) -> Optional[int]:
        """Modular inverse if exists."""
        if not self.is_unit(a):
            return None
        # Extended Euclidean algorithm
        def extended_gcd(a, b):
            if a == 0:
                return b, 0, 1
            gcd, x1, y1 = extended_gcd(b % a, a)
            return gcd, y1 - (b // a) * x1, x1
        
        _, x, _ = extended_gcd(a % self.N, self.N)
        return x % self.N


@dataclass
class LambdaPattern:
    """
    Λ-pattern: function x: ℤ_N → ℂ.
    
    Equivalent to a length-N vector.
    """
    values: NDArray  # Complex array of length N
    
    @property
    def N(self) -> int:
        return len(self.values)
    
    def __getitem__(self, k: int) -> complex:
        return self.values[k % self.N]
    
    def shift(self, s: int) -> 'LambdaPattern':
        """Cyclic shift: x[k] ↦ x[k-s]."""
        return LambdaPattern(np.roll(self.values, s))
    
    def pointwise_mult(self, other: 'LambdaPattern') -> 'LambdaPattern':
        """Pointwise multiplication."""
        return LambdaPattern(self.values * other.values)


# ═══════════════════════════════════════════════════════════════════════════════
# BRIDGES: Θ ↔ Λ ↔ α
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class QCMBridge:
    """
    Bridges between realms.
    
    Meas (Θ→α): Born map |ψ|²
    Lift (Λ→Θ): Embed discrete into continuous
    Quantize (Θ→Λ): Sample continuous to lattice
    """
    N: int = 4  # Default lattice size
    
    def born_measure(self, psi: ThetaScalar) -> float:
        """Meas: Θ → α via Born rule."""
        return psi.measure()
    
    def lift(self, k: int) -> ThetaScalar:
        """Lift: Λ → Θ by embedding as cyclotomic phase."""
        omega_k = np.exp(2j * np.pi * k / self.N)
        return ThetaScalar(omega_k)
    
    def quantize(self, psi: ThetaScalar) -> int:
        """
        Quantize: Θ → Λ by sampling phase to nearest lattice point.
        
        Maps continuous phase θ to k = round(N·θ/(2π)) mod N.
        """
        theta = psi.theta
        if theta < 0:
            theta += 2 * np.pi
        k = int(round(self.N * theta / (2 * np.pi))) % self.N
        return k
    
    def amplitude_lift(self, pattern: LambdaPattern) -> ThetaVector:
        """Lift Λ-pattern to Θ-vector with cyclotomic phases."""
        lattice = LambdaLattice(pattern.N)
        phases = lattice.all_phases
        return ThetaVector(pattern.values * phases)


# ═══════════════════════════════════════════════════════════════════════════════
# FOURIER GEARBOX
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class FourierGearbox:
    """
    DFT/IDFT on Λ-lattice.
    
    DFT: x[k] → X[m] = Σ_k x[k] ω_N^{-km}
    IDFT: X[m] → x[k] = (1/N) Σ_m X[m] ω_N^{km}
    
    Key Laws:
    - Orthogonality: Σ_k ω_N^{k(m-n)} = N·δ_{mn}
    - Parseval: Σ_k |x[k]|² = (1/N) Σ_m |X[m]|²
    - Convolution: DFT(x * y) = DFT(x) ⊙ DFT(y)
    """
    N: int
    
    def dft(self, x: LambdaPattern) -> LambdaPattern:
        """Discrete Fourier Transform."""
        return LambdaPattern(np.fft.fft(x.values))
    
    def idft(self, X: LambdaPattern) -> LambdaPattern:
        """Inverse DFT."""
        return LambdaPattern(np.fft.ifft(X.values))
    
    def verify_orthogonality(self) -> bool:
        """Verify Σ_k ω_N^{k·m} = N·δ_{m,0}."""
        omega = np.exp(2j * np.pi / self.N)
        for m in range(self.N):
            sum_val = sum(omega ** (k * m) for k in range(self.N))
            expected = self.N if m == 0 else 0
            if abs(sum_val - expected) > 1e-10:
                return False
        return True
    
    def verify_parseval(self, x: LambdaPattern) -> Tuple[float, float]:
        """Verify Parseval: Σ|x|² = (1/N)Σ|X|²."""
        X = self.dft(x)
        time_energy = np.sum(np.abs(x.values) ** 2)
        freq_energy = np.sum(np.abs(X.values) ** 2) / self.N
        return time_energy, freq_energy
    
    def cyclic_convolution(self, x: LambdaPattern, y: LambdaPattern) -> LambdaPattern:
        """Convolution via DFT: x * y = IDFT(DFT(x) ⊙ DFT(y))."""
        X = self.dft(x)
        Y = self.dft(y)
        return self.idft(X.pointwise_mult(Y))


# ═══════════════════════════════════════════════════════════════════════════════
# GEOMETRIC MEAN AS CENTER
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ThetaMeans:
    """
    Means as "centers" in Θ-realm.
    
    Θ-multiplication: (r₁e^{iθ₁})(r₂e^{iθ₂}) = (r₁r₂)e^{i(θ₁+θ₂)}
    
    Root∘Multiply is the midpoint operator:
    √(ψ₁·ψ₂) = √(r₁r₂) · e^{i(θ₁+θ₂)/2}
    
    - magnitude: geometric mean √(r₁r₂)
    - phase: arithmetic mean (θ₁+θ₂)/2
    """
    
    @staticmethod
    def geometric_mean(psi1: ThetaScalar, psi2: ThetaScalar) -> ThetaScalar:
        """
        Geometric mean in Θ: √(ψ₁·ψ₂).
        
        This is the true "midpoint operator" in polar manifold.
        """
        product = psi1.value * psi2.value
        return ThetaScalar(cmath.sqrt(product))
    
    @staticmethod
    def rms_norm(values: List[ThetaScalar]) -> float:
        """RMS (root mean square) of magnitudes."""
        squared = [v.measure() for v in values]
        return np.sqrt(np.mean(squared))
    
    @staticmethod
    def phase_mean(psi1: ThetaScalar, psi2: ThetaScalar) -> float:
        """Arithmetic mean of phases."""
        return (psi1.theta + psi2.theta) / 2


# ═══════════════════════════════════════════════════════════════════════════════
# Z0 RECORD FORMAT
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Z0Record:
    """
    Mandatory Z0 record format for any glyph-composite.
    
    Z0 = (status, ρ, w, seed, hash, sig)
    """
    status: str                    # Computation status
    rho: float                     # Residual/drift measure
    witness_keys: List[str]        # Minimal witness set
    seed: Any                      # Repair/tunnel seed
    checksum: str                  # Content hash
    signature: str                 # Orbit/stabilizer signature
    
    @classmethod
    def create(cls, status: str, rho: float, 
               witnesses: List[str], seed: Any) -> 'Z0Record':
        """Create Z0 record with computed checksum."""
        import hashlib
        data = f"{status}|{rho}|{witnesses}|{seed}"
        checksum = hashlib.sha256(data.encode()).hexdigest()[:16]
        return cls(status, rho, witnesses, seed, checksum, "")


# ═══════════════════════════════════════════════════════════════════════════════
# POLE BRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class QCMPoleBridge:
    """
    Bridge between QCM and four-pole framework.
    """
    
    @staticmethod
    def realm_chart_map() -> Dict[str, str]:
        return {
            "Θ (Theta)": "✿ Flower chart (continuous phase)",
            "Λ (Lambda)": "□ Square chart (discrete lattice)",
            "α (Alpha)": "☁ Cloud chart (measurement/probability)",
            "Ψ (Psi)": "⟂ Fractal chart (recursive/hierarchical)"
        }
    
    @staticmethod
    def integration() -> str:
        return """
        QCM ↔ FOUR-POLE FRAMEWORK
        
        Θ-Realm (Continuous Phase):
          - Lives in ✿ Flower chart
          - C-pole continuous transformations
          - Objects: ψ ∈ ℂ, polar form r·e^{iθ}
          - Operators: Rotation, √, interference
        
        Λ-Realm (Discrete Lattice):
          - Lives in □ Square chart  
          - D-pole discrete constraints
          - Objects: k ∈ ℤ_N, ω_N = e^{2πi/N}
          - Operators: mod, gcd, DFT
        
        Bridges:
          Meas (Θ→α): Born rule |ψ|² → ☁ chart
          Lift (Λ→Θ): Cyclotomic embedding
          Quant (Θ→Λ): Phase sampling
        
        The "1/2 IN" Key:
          √(-1) = i because -1 = e^{iπ} → √(-1) = e^{iπ/2} = i
          Half-angle + root-radius: the decoding operator
        """


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def theta_scalar(value: complex) -> ThetaScalar:
    """Create Θ-scalar."""
    return ThetaScalar(value)


def theta_vector(components: NDArray) -> ThetaVector:
    """Create Θ-vector."""
    return ThetaVector(np.asarray(components, dtype=complex))


def lambda_lattice(N: int) -> LambdaLattice:
    """Create Λ-lattice."""
    return LambdaLattice(N)


def lambda_pattern(values: NDArray) -> LambdaPattern:
    """Create Λ-pattern."""
    return LambdaPattern(np.asarray(values, dtype=complex))


def qcm_bridge(N: int = 4) -> QCMBridge:
    """Create QCM bridge."""
    return QCMBridge(N)


def fourier_gearbox(N: int) -> FourierGearbox:
    """Create Fourier gearbox."""
    return FourierGearbox(N)


def quadrature_sum(a: float, b: float) -> float:
    """Quadrature sum a ⊞ b = √(a² + b²)."""
    return ThetaInterference.quadrature_sum(a, b)


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Enums
    'QCMSection',
    'ZeroType',
    
    # Θ-Realm
    'ThetaScalar',
    'ThetaVector',
    'ThetaInterference',
    'ThetaMeans',
    
    # Λ-Realm
    'LambdaLattice',
    'LambdaPattern',
    
    # Bridges
    'QCMBridge',
    'FourierGearbox',
    
    # Records
    'Z0Record',
    
    # Bridge
    'QCMPoleBridge',
    
    # Functions
    'theta_scalar',
    'theta_vector',
    'lambda_lattice',
    'lambda_pattern',
    'qcm_bridge',
    'fourier_gearbox',
    'quadrature_sum',
]
