"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         ATLAS FORGE - Canonical Lenses                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

Standard, pre-built lenses for common coordinate transformations.

Key Canonical Lenses:
- IdentityLens: The trivial transformation
- LogLens: Logarithmic (multiplication → addition)
- ExpLens: Exponential (addition → multiplication)
- TrigLens: Trigonometric (angle → coordinate)
- PhiLens: Phase unification (x → e^{i ln x})
- FourierLens: Fourier transform (position ↔ momentum)

The Phase Unification Chain:
    Multiplication in x → Addition in ln(x) → Rotation in e^{i ln x}
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Optional, Tuple
import math
import cmath
import numpy as np
from numpy.typing import NDArray

from atlasforge.core.types import Interval
from atlasforge.lenses.chart import Chart, Lens, CorridorCondition, ChartError


# ═══════════════════════════════════════════════════════════════════════════════
# IDENTITY LENS
# ═══════════════════════════════════════════════════════════════════════════════

class IdentityLens(Chart[float, float]):
    """
    The identity lens: T(x) = x
    
    This is the trivial transformation that leaves everything unchanged.
    It serves as the identity element for lens composition.
    """
    
    @property
    def name(self) -> str:
        return "Identity"
    
    @property
    def symbol(self) -> str:
        return "Id"
    
    @property
    def corridor(self) -> CorridorCondition:
        return CorridorCondition(Interval.all_reals(), "all")
    
    def forward(self, x: float) -> float:
        return x
    
    def inverse(self, y: float) -> float:
        return y
    
    def jacobian(self, x: float) -> float:
        return 1.0


# ═══════════════════════════════════════════════════════════════════════════════
# LOGARITHMIC LENS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class LogLens(Chart[float, float]):
    """
    The logarithmic lens: T(x) = log_base(x)
    
    Key Properties:
    - Domain: (0, ∞)
    - Range: (-∞, ∞)
    - Transforms multiplication to addition: log(xy) = log(x) + log(y)
    - Transforms powers to multiplication: log(x^n) = n·log(x)
    - Jacobian: T'(x) = 1/(x·ln(base))
    
    This lens is fundamental for:
    - Converting multiplicative problems to additive ones
    - Handling scale-invariant phenomena
    - Working with growth/decay processes
    """
    
    base: float = math.e
    
    def __post_init__(self):
        if self.base <= 0 or self.base == 1:
            raise ChartError("Logarithm base must be positive and ≠ 1")
    
    @property
    def name(self) -> str:
        return "Ln" if self.base == math.e else f"Log_{self.base:.1f}"
    
    @property
    def symbol(self) -> str:
        return "ln" if self.base == math.e else f"log_{self.base:.1f}"
    
    @property
    def corridor(self) -> CorridorCondition:
        return CorridorCondition(
            Interval.positive_reals(),
            "(0, ∞)",
            predicate=lambda x: x > 0
        )
    
    @property
    def ln_base(self) -> float:
        return math.log(self.base)
    
    def forward(self, x: float) -> float:
        if x <= 0:
            raise ChartError(f"LogLens requires positive input, got {x}")
        return math.log(x) / self.ln_base
    
    def inverse(self, y: float) -> float:
        return self.base ** y
    
    def jacobian(self, x: float) -> float:
        if x <= 0:
            raise ChartError(f"Jacobian requires positive input, got {x}")
        return 1.0 / (x * self.ln_base)
    
    # Transported operations leveraging log properties
    
    def mul_as_add(self, x: float, y: float) -> float:
        """Multiplication in original coords = Addition in log coords."""
        return self.inverse(self.forward(x) + self.forward(y))
    
    def pow_as_mul(self, x: float, n: float) -> float:
        """Power in original coords = Scalar multiplication in log coords."""
        return self.inverse(n * self.forward(x))
    
    def geometric_mean(self, values: list) -> float:
        """Geometric mean via arithmetic mean in log space."""
        if not values:
            raise ValueError("Cannot compute geometric mean of empty list")
        log_sum = sum(self.forward(v) for v in values)
        return self.inverse(log_sum / len(values))


# ═══════════════════════════════════════════════════════════════════════════════
# EXPONENTIAL LENS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ExpLens(Chart[float, float]):
    """
    The exponential lens: T(x) = base^x
    
    This is the inverse of the LogLens.
    
    Key Properties:
    - Domain: (-∞, ∞)
    - Range: (0, ∞)
    - Transforms addition to multiplication: exp(x+y) = exp(x)·exp(y)
    - Jacobian: T'(x) = base^x · ln(base)
    """
    
    base: float = math.e
    
    def __post_init__(self):
        if self.base <= 0:
            raise ChartError("Exponential base must be positive")
    
    @property
    def name(self) -> str:
        return "Exp" if self.base == math.e else f"Exp_{self.base:.1f}"
    
    @property
    def symbol(self) -> str:
        return "exp" if self.base == math.e else f"{self.base:.1f}^x"
    
    @property
    def corridor(self) -> CorridorCondition:
        return CorridorCondition(Interval.all_reals(), "ℝ")
    
    @property
    def ln_base(self) -> float:
        return math.log(self.base)
    
    def forward(self, x: float) -> float:
        return self.base ** x
    
    def inverse(self, y: float) -> float:
        if y <= 0:
            raise ChartError(f"ExpLens inverse requires positive input, got {y}")
        return math.log(y) / self.ln_base
    
    def jacobian(self, x: float) -> float:
        return (self.base ** x) * self.ln_base
    
    # Transported operations
    
    def add_as_mul(self, x: float, y: float) -> float:
        """Addition in original coords = Multiplication in exp coords."""
        return self.inverse(self.forward(x) * self.forward(y))


# ═══════════════════════════════════════════════════════════════════════════════
# TRIGONOMETRIC LENSES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class TrigLens(Chart[float, float]):
    """
    Trigonometric lens: maps angles to coordinates.
    
    Supported functions:
    - "tan": tan / atan on (-π/2, π/2)
    - "sin": sin / asin on [-π/2, π/2]
    - "cos": cos / acos on [0, π]
    """
    
    func: str = "tan"
    
    def __post_init__(self):
        if self.func not in ("tan", "sin", "cos"):
            raise ChartError(f"Unknown trigonometric function: {self.func}")
    
    @property
    def name(self) -> str:
        return self.func.capitalize()
    
    @property
    def symbol(self) -> str:
        return self.func
    
    @property
    def corridor(self) -> CorridorCondition:
        if self.func == "tan":
            return CorridorCondition(
                Interval.open(-math.pi/2, math.pi/2),
                "(-π/2, π/2)"
            )
        elif self.func == "sin":
            return CorridorCondition(
                Interval.closed(-math.pi/2, math.pi/2),
                "[-π/2, π/2]"
            )
        else:  # cos
            return CorridorCondition(
                Interval.closed(0, math.pi),
                "[0, π]"
            )
    
    def forward(self, x: float) -> float:
        if self.func == "tan":
            return math.tan(x)
        elif self.func == "sin":
            return math.sin(x)
        else:
            return math.cos(x)
    
    def inverse(self, y: float) -> float:
        if self.func == "tan":
            return math.atan(y)
        elif self.func == "sin":
            return math.asin(max(-1, min(1, y)))
        else:
            return math.acos(max(-1, min(1, y)))
    
    def jacobian(self, x: float) -> float:
        if self.func == "tan":
            c = math.cos(x)
            return 1.0 / (c * c) if c != 0 else float('inf')
        elif self.func == "sin":
            return math.cos(x)
        else:
            return -math.sin(x)


# ═══════════════════════════════════════════════════════════════════════════════
# PHI LENS (PHASE UNIFICATION)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class PhiLens(Chart[float, complex]):
    """
    The Phase Unification Lens: T(x) = e^{i·ln(x)}
    
    This implements the remarkable transformation chain:
        x → ln(x) → e^{i·ln(x)} = cos(ln x) + i·sin(ln x)
    
    Key Properties:
    - Domain: (0, ∞)
    - Range: Unit circle in ℂ
    - x^i = e^{i·ln(x)} (imaginary power!)
    - Multiplicative circle: x → (cos(ln x), sin(ln x))
    
    This lens reveals:
    - Multiplication becomes rotation: xy → rotation by ln(x) + ln(y)
    - Powers become phase shifts: x^n → rotation by n·ln(x)
    - The unit circle is the "multiplicative modulus 2π" structure
    """
    
    @property
    def name(self) -> str:
        return "Phi"
    
    @property
    def symbol(self) -> str:
        return "Φ"
    
    @property
    def corridor(self) -> CorridorCondition:
        return CorridorCondition(
            Interval.positive_reals(),
            "(0, ∞)",
            predicate=lambda x: x > 0
        )
    
    def forward(self, x: float) -> complex:
        if x <= 0:
            raise ChartError(f"PhiLens requires positive input, got {x}")
        ln_x = math.log(x)
        return complex(math.cos(ln_x), math.sin(ln_x))
    
    def inverse(self, z: complex) -> float:
        """
        Inverse: Given z on unit circle, find x such that e^{i·ln(x)} = z.
        
        z = e^{iθ} implies ln(x) = θ (mod 2π), so x = e^θ.
        We use the principal branch.
        """
        theta = cmath.phase(z)
        return math.exp(theta)
    
    def jacobian(self, x: float) -> float:
        """
        The Jacobian |dT/dx| = |i·e^{i·ln(x)}/x| = 1/x.
        """
        return 1.0 / x
    
    # Special methods for phase operations
    
    def phase(self, x: float) -> float:
        """Get the phase angle ln(x) mod 2π."""
        return math.log(x) % (2 * math.pi)
    
    def imaginary_power(self, x: float) -> complex:
        """Compute x^i directly."""
        return self.forward(x)
    
    def on_circle(self, x: float) -> Tuple[float, float]:
        """Return (cos(ln x), sin(ln x)) - point on unit circle."""
        z = self.forward(x)
        return (z.real, z.imag)
    
    def multiplicative_distance(self, x: float, y: float) -> float:
        """
        Distance on multiplicative circle between x and y.
        
        This is |ln(x) - ln(y)| mod π (arc length on unit circle).
        """
        diff = abs(math.log(x) - math.log(y))
        return min(diff % (2 * math.pi), 2 * math.pi - diff % (2 * math.pi))


# ═══════════════════════════════════════════════════════════════════════════════
# FOURIER LENS
# ═══════════════════════════════════════════════════════════════════════════════

class FourierLens(Chart[NDArray[np.float64], NDArray[np.complex128]]):
    """
    The Fourier Transform Lens: T(f) = F[f]
    
    This is a 90° rotation in phase space:
    - Position ↔ Momentum (wave number)
    - Local ↔ Global structure
    - Convolution ↔ Multiplication
    
    For quantum mechanics:
    - ψ(x) = ⟨x|ψ⟩ (position representation - "particle")
    - φ(p) = ⟨p|ψ⟩ (momentum representation - "wave")
    - φ(p) = (1/√2πℏ) ∫ e^{-ipx/ℏ} ψ(x) dx
    
    Uncertainty invariant: Δx · Δp ≥ ℏ/2
    """
    
    @property
    def name(self) -> str:
        return "Fourier"
    
    @property
    def symbol(self) -> str:
        return "ℱ"
    
    @property
    def corridor(self) -> CorridorCondition:
        return CorridorCondition(Interval.all_reals(), "L²(ℝ)")
    
    def forward(self, x: NDArray[np.float64]) -> NDArray[np.complex128]:
        """Compute FFT of input array."""
        return np.fft.fft(x)
    
    def inverse(self, k: NDArray[np.complex128]) -> NDArray[np.float64]:
        """Compute inverse FFT."""
        return np.fft.ifft(k).real
    
    def jacobian(self, x: NDArray[np.float64]) -> float:
        """The Fourier transform is unitary, so |J| = 1."""
        return 1.0
    
    # Special Fourier operations
    
    def convolution_to_product(
        self, 
        f: NDArray[np.float64], 
        g: NDArray[np.float64]
    ) -> NDArray[np.float64]:
        """
        Compute f * g (convolution) via product in Fourier domain.
        
        F[f * g] = F[f] · F[g]
        """
        F_f = self.forward(f)
        F_g = self.forward(g)
        return self.inverse(F_f * F_g)
    
    def derivative(
        self, 
        f: NDArray[np.float64], 
        dx: float = 1.0
    ) -> NDArray[np.float64]:
        """
        Compute df/dx via multiplication by ik in Fourier domain.
        
        F[df/dx] = ik · F[f]
        """
        n = len(f)
        k = np.fft.fftfreq(n, dx) * 2 * np.pi
        F_f = self.forward(f)
        F_df = 1j * k * F_f
        return self.inverse(F_df)
    
    def power_spectrum(self, f: NDArray[np.float64]) -> NDArray[np.float64]:
        """Compute power spectrum |F[f]|²."""
        F_f = self.forward(f)
        return np.abs(F_f) ** 2
    
    def parseval_energy(self, f: NDArray[np.float64]) -> float:
        """
        Compute energy via Parseval's theorem.
        
        ∫|f(x)|² dx = (1/2π) ∫|F[f](k)|² dk
        """
        return np.sum(np.abs(f) ** 2)


# ═══════════════════════════════════════════════════════════════════════════════
# SPECIAL LENSES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class LogitLens(Chart[float, float]):
    """
    The Logit Lens: T(p) = log(p / (1-p))
    
    Maps probability (0,1) to log-odds (-∞, ∞).
    Inverse is the sigmoid: σ(x) = 1 / (1 + e^{-x})
    """
    
    @property
    def name(self) -> str:
        return "Logit"
    
    @property
    def symbol(self) -> str:
        return "logit"
    
    @property
    def corridor(self) -> CorridorCondition:
        return CorridorCondition(
            Interval.open(0, 1),
            "(0, 1)",
            predicate=lambda x: 0 < x < 1
        )
    
    def forward(self, p: float) -> float:
        if not (0 < p < 1):
            raise ChartError(f"LogitLens requires p ∈ (0,1), got {p}")
        return math.log(p / (1 - p))
    
    def inverse(self, x: float) -> float:
        """Sigmoid function."""
        return 1 / (1 + math.exp(-x))
    
    def jacobian(self, p: float) -> float:
        return 1 / (p * (1 - p))


@dataclass
class ProbityLens(Chart[float, float]):
    """
    The Probit Lens: T(p) = Φ⁻¹(p)
    
    Maps probability to standard normal quantile.
    Uses the inverse of the standard normal CDF.
    """
    
    @property
    def name(self) -> str:
        return "Probit"
    
    @property
    def symbol(self) -> str:
        return "Φ⁻¹"
    
    @property
    def corridor(self) -> CorridorCondition:
        return CorridorCondition(
            Interval.open(0, 1),
            "(0, 1)",
            predicate=lambda x: 0 < x < 1
        )
    
    def forward(self, p: float) -> float:
        """Inverse standard normal CDF (probit function)."""
        from scipy import stats
        if not (0 < p < 1):
            raise ChartError(f"ProbitLens requires p ∈ (0,1), got {p}")
        return stats.norm.ppf(p)
    
    def inverse(self, x: float) -> float:
        """Standard normal CDF."""
        from scipy import stats
        return stats.norm.cdf(x)
    
    def jacobian(self, p: float) -> float:
        from scipy import stats
        z = stats.norm.ppf(p)
        return 1 / stats.norm.pdf(z)


@dataclass
class BoxCoxLens(Chart[float, float]):
    """
    The Box-Cox Lens: T(x) = (x^λ - 1) / λ  for λ ≠ 0
                           = ln(x)           for λ = 0
    
    A family of power transforms that includes log as a limit.
    Used for variance stabilization and normalization.
    """
    
    lam: float = 0.0  # λ parameter
    
    @property
    def name(self) -> str:
        return f"BoxCox(λ={self.lam})"
    
    @property
    def symbol(self) -> str:
        return f"BC_{self.lam}"
    
    @property
    def corridor(self) -> CorridorCondition:
        return CorridorCondition(
            Interval.positive_reals(),
            "(0, ∞)",
            predicate=lambda x: x > 0
        )
    
    def forward(self, x: float) -> float:
        if x <= 0:
            raise ChartError(f"BoxCoxLens requires positive input, got {x}")
        if abs(self.lam) < 1e-10:
            return math.log(x)
        return (x ** self.lam - 1) / self.lam
    
    def inverse(self, y: float) -> float:
        if abs(self.lam) < 1e-10:
            return math.exp(y)
        val = self.lam * y + 1
        if val <= 0:
            raise ChartError(f"BoxCox inverse undefined for y={y} with λ={self.lam}")
        return val ** (1 / self.lam)
    
    def jacobian(self, x: float) -> float:
        if abs(self.lam) < 1e-10:
            return 1 / x
        return x ** (self.lam - 1)


# ═══════════════════════════════════════════════════════════════════════════════
# LENS CATALOG
# ═══════════════════════════════════════════════════════════════════════════════

class LensCatalog:
    """Catalog of all canonical lenses."""
    
    @staticmethod
    def identity() -> IdentityLens:
        return IdentityLens()
    
    @staticmethod
    def log(base: float = math.e) -> LogLens:
        return LogLens(base)
    
    @staticmethod
    def exp(base: float = math.e) -> ExpLens:
        return ExpLens(base)
    
    @staticmethod
    def trig(func: str = "tan") -> TrigLens:
        return TrigLens(func)
    
    @staticmethod
    def phi() -> PhiLens:
        return PhiLens()
    
    @staticmethod
    def fourier() -> FourierLens:
        return FourierLens()
    
    @staticmethod
    def logit() -> LogitLens:
        return LogitLens()
    
    @staticmethod
    def boxcox(lam: float = 0.0) -> BoxCoxLens:
        return BoxCoxLens(lam)
    
    @classmethod
    def list_all(cls) -> list:
        return [
            "identity", "log", "exp", "trig", "phi", 
            "fourier", "logit", "boxcox"
        ]
