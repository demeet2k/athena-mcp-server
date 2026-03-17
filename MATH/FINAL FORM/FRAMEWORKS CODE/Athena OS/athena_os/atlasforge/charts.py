"""
ATHENA OS - AtlasForge: CHARTS
==============================
Chart Rewriting and Coordinate Transport

CHART DEFINITION:
    A Chart is a map T: D → U from a structured domain D 
    (intervals, unions, graphs, manifolds) into a coordinate 
    space U ⊆ ℝ where construction may be simpler.

FUNDAMENTAL REWRITE OPERATOR:
    Transport by conjugation: for operator f acting in coordinates,
    the transported operator on original domain is:
    
        f_T = T⁻¹ ∘ f ∘ T
    
    whenever T is admissible on a certified corridor.

CORRIDOR CONDITIONS (must be certified):
    1. Legality - chart is well-defined on corridor
    2. Injectivity - strict monotonicity (v1)
    3. Inverse Admissibility - inverse exists and is stable

CHART TYPES:
    - Identity Chart (no transformation)
    - Linear Chart (affine scaling)
    - Logarithmic Chart (log transform)
    - Exponential Chart
    - Trigonometric Charts (sin, cos, tan)
    - Polynomial Charts
    - Möbius/Fractional Linear Charts
    - Custom Charts (user-defined)

CERTIFICATE REQUIREMENTS:
    ChartCorridor certificate must prove:
    - legality on corridor
    - injectivity/monotonicity  
    - inverse admissibility
    - optional conditioning bounds

SOURCES:
    - AtlasForge.docx Section A
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Tuple, Union
from enum import Enum
import numpy as np
from abc import ABC, abstractmethod
import hashlib


# =============================================================================
# ENUMS
# =============================================================================

class ChartType(Enum):
    """Types of charts available."""
    
    IDENTITY = "identity"
    LINEAR = "linear"
    LOGARITHMIC = "logarithmic"
    EXPONENTIAL = "exponential"
    TRIGONOMETRIC = "trigonometric"
    POLYNOMIAL = "polynomial"
    MOBIUS = "mobius"
    POWER = "power"
    CUSTOM = "custom"


class CorridorStatus(Enum):
    """Status of corridor certification."""
    
    UNCHECKED = "unchecked"
    CHECKING = "checking"
    CERTIFIED = "certified"
    FAILED = "failed"
    EXPIRED = "expired"


class MonotonicityType(Enum):
    """Type of monotonicity."""
    
    UNKNOWN = "unknown"
    STRICTLY_INCREASING = "strictly_increasing"
    STRICTLY_DECREASING = "strictly_decreasing"
    NON_DECREASING = "non_decreasing"
    NON_INCREASING = "non_increasing"
    NON_MONOTONIC = "non_monotonic"


# =============================================================================
# CORRIDOR
# =============================================================================

@dataclass
class Corridor:
    """
    A certified region where a chart is valid.
    
    Corridor conditions:
    1. Legality - chart is well-defined
    2. Injectivity - strict monotonicity
    3. Inverse admissibility - stable inverse exists
    """
    
    # Domain bounds
    lower: float
    upper: float
    
    # Certification status
    status: CorridorStatus = CorridorStatus.UNCHECKED
    
    # Properties
    is_legal: bool = False
    is_injective: bool = False
    is_inverse_admissible: bool = False
    
    # Monotonicity type
    monotonicity: MonotonicityType = MonotonicityType.UNKNOWN
    
    # Conditioning bounds (optional)
    condition_number: Optional[float] = None
    lipschitz_constant: Optional[float] = None
    
    # Evidence
    evidence: Dict[str, Any] = field(default_factory=dict)
    
    # Certification timestamp
    certified_at: Optional[float] = None
    
    @property
    def is_certified(self) -> bool:
        """Check if corridor is fully certified."""
        return (self.status == CorridorStatus.CERTIFIED and
                self.is_legal and
                self.is_injective and
                self.is_inverse_admissible)
    
    @property
    def width(self) -> float:
        """Get corridor width."""
        return self.upper - self.lower
    
    def contains(self, x: float) -> bool:
        """Check if point is in corridor."""
        return self.lower <= x <= self.upper
    
    def contains_interval(self, a: float, b: float) -> bool:
        """Check if interval [a, b] is contained in corridor."""
        return self.lower <= a and b <= self.upper
    
    def __hash__(self) -> int:
        return hash((self.lower, self.upper))


# =============================================================================
# ABSTRACT CHART
# =============================================================================

class Chart(ABC):
    """
    Abstract base class for charts.
    
    A Chart is a map T: D → U that transforms coordinates
    to simplify construction.
    """
    
    def __init__(self, chart_type: ChartType, name: str = ""):
        self.chart_type = chart_type
        self.name = name or chart_type.value
        self.corridors: List[Corridor] = []
        self._id: Optional[str] = None
    
    @abstractmethod
    def forward(self, x: float) -> float:
        """Apply chart transformation: T(x)."""
        pass
    
    @abstractmethod
    def inverse(self, u: float) -> float:
        """Apply inverse transformation: T⁻¹(u)."""
        pass
    
    @abstractmethod
    def derivative(self, x: float) -> float:
        """Compute derivative T'(x)."""
        pass
    
    @abstractmethod
    def inverse_derivative(self, u: float) -> float:
        """Compute derivative of inverse (T⁻¹)'(u)."""
        pass
    
    def forward_array(self, x: np.ndarray) -> np.ndarray:
        """Vectorized forward transformation."""
        return np.vectorize(self.forward)(x)
    
    def inverse_array(self, u: np.ndarray) -> np.ndarray:
        """Vectorized inverse transformation."""
        return np.vectorize(self.inverse)(u)
    
    def transport_operator(self, f: Callable[[float], float], 
                          x: float) -> float:
        """
        Transport operator f through chart.
        
        f_T = T⁻¹ ∘ f ∘ T
        """
        u = self.forward(x)
        f_u = f(u)
        return self.inverse(f_u)
    
    def certify_corridor(self, lower: float, upper: float,
                        n_samples: int = 100) -> Corridor:
        """
        Certify a corridor for this chart.
        
        Tests legality, injectivity, and inverse admissibility.
        """
        corridor = Corridor(lower=lower, upper=upper)
        corridor.status = CorridorStatus.CHECKING
        
        # Sample points
        x_samples = np.linspace(lower, upper, n_samples)
        
        # Test legality
        try:
            u_samples = self.forward_array(x_samples)
            corridor.is_legal = np.all(np.isfinite(u_samples))
        except:
            corridor.is_legal = False
            corridor.status = CorridorStatus.FAILED
            return corridor
        
        # Test injectivity via monotonicity
        if corridor.is_legal:
            derivatives = np.array([self.derivative(x) for x in x_samples])
            
            if np.all(derivatives > 0):
                corridor.is_injective = True
                corridor.monotonicity = MonotonicityType.STRICTLY_INCREASING
            elif np.all(derivatives < 0):
                corridor.is_injective = True
                corridor.monotonicity = MonotonicityType.STRICTLY_DECREASING
            elif np.all(derivatives >= 0):
                corridor.is_injective = False
                corridor.monotonicity = MonotonicityType.NON_DECREASING
            elif np.all(derivatives <= 0):
                corridor.is_injective = False
                corridor.monotonicity = MonotonicityType.NON_INCREASING
            else:
                corridor.is_injective = False
                corridor.monotonicity = MonotonicityType.NON_MONOTONIC
        
        # Test inverse admissibility
        if corridor.is_injective:
            try:
                # Check round-trip
                x_recovered = self.inverse_array(u_samples)
                error = np.max(np.abs(x_recovered - x_samples))
                corridor.is_inverse_admissible = error < 1e-10
                
                # Compute condition number
                inv_derivatives = np.array([self.inverse_derivative(u) 
                                           for u in u_samples])
                corridor.condition_number = np.max(np.abs(derivatives)) * \
                                           np.max(np.abs(inv_derivatives))
                
                # Lipschitz constant
                corridor.lipschitz_constant = np.max(np.abs(derivatives))
                
            except:
                corridor.is_inverse_admissible = False
        
        # Set final status
        if corridor.is_legal and corridor.is_injective and corridor.is_inverse_admissible:
            corridor.status = CorridorStatus.CERTIFIED
            import time
            corridor.certified_at = time.time()
        else:
            corridor.status = CorridorStatus.FAILED
        
        # Store evidence
        corridor.evidence = {
            "n_samples": n_samples,
            "derivative_range": (float(np.min(derivatives)), float(np.max(derivatives))),
            "forward_range": (float(np.min(u_samples)), float(np.max(u_samples)))
        }
        
        self.corridors.append(corridor)
        return corridor
    
    def get_certified_corridor(self, x: float) -> Optional[Corridor]:
        """Get a certified corridor containing x."""
        for corridor in self.corridors:
            if corridor.is_certified and corridor.contains(x):
                return corridor
        return None
    
    @property
    def chart_id(self) -> str:
        """Get content-addressed ID for this chart."""
        if self._id is None:
            content = f"{self.chart_type.value}:{self.name}:{self._get_params()}"
            self._id = hashlib.sha256(content.encode()).hexdigest()[:16]
        return self._id
    
    @abstractmethod
    def _get_params(self) -> str:
        """Get serialized parameters for hashing."""
        pass
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(type={self.chart_type.value}, name={self.name})"


# =============================================================================
# CONCRETE CHARTS
# =============================================================================

class IdentityChart(Chart):
    """Identity chart - no transformation."""
    
    def __init__(self):
        super().__init__(ChartType.IDENTITY, "identity")
    
    def forward(self, x: float) -> float:
        return x
    
    def inverse(self, u: float) -> float:
        return u
    
    def derivative(self, x: float) -> float:
        return 1.0
    
    def inverse_derivative(self, u: float) -> float:
        return 1.0
    
    def _get_params(self) -> str:
        return ""


class LinearChart(Chart):
    """
    Linear (affine) chart: T(x) = ax + b
    """
    
    def __init__(self, scale: float = 1.0, offset: float = 0.0):
        super().__init__(ChartType.LINEAR, f"linear({scale},{offset})")
        
        if scale == 0:
            raise ValueError("Scale cannot be zero for linear chart")
        
        self.scale = scale
        self.offset = offset
    
    def forward(self, x: float) -> float:
        return self.scale * x + self.offset
    
    def inverse(self, u: float) -> float:
        return (u - self.offset) / self.scale
    
    def derivative(self, x: float) -> float:
        return self.scale
    
    def inverse_derivative(self, u: float) -> float:
        return 1.0 / self.scale
    
    def _get_params(self) -> str:
        return f"{self.scale}:{self.offset}"


class LogarithmicChart(Chart):
    """
    Logarithmic chart: T(x) = log_base(x)
    """
    
    def __init__(self, base: float = np.e):
        super().__init__(ChartType.LOGARITHMIC, f"log({base})")
        
        if base <= 0 or base == 1:
            raise ValueError("Base must be positive and not equal to 1")
        
        self.base = base
        self.log_base = np.log(base)
    
    def forward(self, x: float) -> float:
        if x <= 0:
            return float('-inf')
        return np.log(x) / self.log_base
    
    def inverse(self, u: float) -> float:
        return self.base ** u
    
    def derivative(self, x: float) -> float:
        if x <= 0:
            return float('inf')
        return 1.0 / (x * self.log_base)
    
    def inverse_derivative(self, u: float) -> float:
        return self.base ** u * self.log_base
    
    def _get_params(self) -> str:
        return f"{self.base}"


class ExponentialChart(Chart):
    """
    Exponential chart: T(x) = base^x
    """
    
    def __init__(self, base: float = np.e):
        super().__init__(ChartType.EXPONENTIAL, f"exp({base})")
        
        if base <= 0 or base == 1:
            raise ValueError("Base must be positive and not equal to 1")
        
        self.base = base
        self.log_base = np.log(base)
    
    def forward(self, x: float) -> float:
        return self.base ** x
    
    def inverse(self, u: float) -> float:
        if u <= 0:
            return float('-inf')
        return np.log(u) / self.log_base
    
    def derivative(self, x: float) -> float:
        return self.base ** x * self.log_base
    
    def inverse_derivative(self, u: float) -> float:
        if u <= 0:
            return float('inf')
        return 1.0 / (u * self.log_base)
    
    def _get_params(self) -> str:
        return f"{self.base}"


class PowerChart(Chart):
    """
    Power chart: T(x) = x^n
    """
    
    def __init__(self, power: float = 2.0):
        super().__init__(ChartType.POWER, f"power({power})")
        
        if power == 0:
            raise ValueError("Power cannot be zero")
        
        self.power = power
    
    def forward(self, x: float) -> float:
        if x < 0 and self.power != int(self.power):
            return float('nan')
        return x ** self.power
    
    def inverse(self, u: float) -> float:
        if u < 0 and 1/self.power != int(1/self.power):
            return float('nan')
        return u ** (1.0 / self.power)
    
    def derivative(self, x: float) -> float:
        return self.power * x ** (self.power - 1)
    
    def inverse_derivative(self, u: float) -> float:
        inv_power = 1.0 / self.power
        return inv_power * u ** (inv_power - 1)
    
    def _get_params(self) -> str:
        return f"{self.power}"


class MobiusChart(Chart):
    """
    Möbius (fractional linear) chart: T(x) = (ax + b) / (cx + d)
    
    Requires ad - bc ≠ 0 for invertibility.
    """
    
    def __init__(self, a: float = 1.0, b: float = 0.0, 
                 c: float = 0.0, d: float = 1.0):
        super().__init__(ChartType.MOBIUS, f"mobius({a},{b},{c},{d})")
        
        # Check invertibility
        det = a * d - b * c
        if abs(det) < 1e-15:
            raise ValueError("Möbius chart requires ad - bc ≠ 0")
        
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.det = det
    
    def forward(self, x: float) -> float:
        denom = self.c * x + self.d
        if abs(denom) < 1e-15:
            return float('inf') if (self.a * x + self.b) > 0 else float('-inf')
        return (self.a * x + self.b) / denom
    
    def inverse(self, u: float) -> float:
        # Inverse: (d*u - b) / (-c*u + a)
        denom = -self.c * u + self.a
        if abs(denom) < 1e-15:
            return float('inf')
        return (self.d * u - self.b) / denom
    
    def derivative(self, x: float) -> float:
        denom = self.c * x + self.d
        if abs(denom) < 1e-15:
            return float('inf')
        return self.det / (denom ** 2)
    
    def inverse_derivative(self, u: float) -> float:
        denom = -self.c * u + self.a
        if abs(denom) < 1e-15:
            return float('inf')
        return self.det / (denom ** 2)
    
    def _get_params(self) -> str:
        return f"{self.a}:{self.b}:{self.c}:{self.d}"


class TrigonometricChart(Chart):
    """
    Trigonometric charts (sin, cos, tan, etc.)
    """
    
    def __init__(self, func: str = "sin"):
        super().__init__(ChartType.TRIGONOMETRIC, f"trig({func})")
        
        self.func = func.lower()
        
        if self.func not in ["sin", "cos", "tan", "sinh", "cosh", "tanh"]:
            raise ValueError(f"Unknown trig function: {func}")
    
    def forward(self, x: float) -> float:
        if self.func == "sin":
            return np.sin(x)
        elif self.func == "cos":
            return np.cos(x)
        elif self.func == "tan":
            return np.tan(x)
        elif self.func == "sinh":
            return np.sinh(x)
        elif self.func == "cosh":
            return np.cosh(x)
        elif self.func == "tanh":
            return np.tanh(x)
    
    def inverse(self, u: float) -> float:
        if self.func == "sin":
            return np.arcsin(np.clip(u, -1, 1))
        elif self.func == "cos":
            return np.arccos(np.clip(u, -1, 1))
        elif self.func == "tan":
            return np.arctan(u)
        elif self.func == "sinh":
            return np.arcsinh(u)
        elif self.func == "cosh":
            return np.arccosh(max(u, 1))
        elif self.func == "tanh":
            return np.arctanh(np.clip(u, -0.9999, 0.9999))
    
    def derivative(self, x: float) -> float:
        if self.func == "sin":
            return np.cos(x)
        elif self.func == "cos":
            return -np.sin(x)
        elif self.func == "tan":
            return 1 / np.cos(x)**2
        elif self.func == "sinh":
            return np.cosh(x)
        elif self.func == "cosh":
            return np.sinh(x)
        elif self.func == "tanh":
            return 1 / np.cosh(x)**2
    
    def inverse_derivative(self, u: float) -> float:
        if self.func == "sin":
            return 1 / np.sqrt(1 - u**2) if abs(u) < 1 else float('inf')
        elif self.func == "cos":
            return -1 / np.sqrt(1 - u**2) if abs(u) < 1 else float('inf')
        elif self.func == "tan":
            return 1 / (1 + u**2)
        elif self.func == "sinh":
            return 1 / np.sqrt(u**2 + 1)
        elif self.func == "cosh":
            return 1 / np.sqrt(u**2 - 1) if u > 1 else float('inf')
        elif self.func == "tanh":
            return 1 / (1 - u**2) if abs(u) < 1 else float('inf')
    
    def _get_params(self) -> str:
        return f"{self.func}"


# =============================================================================
# CHART COMPOSITION
# =============================================================================

class ComposedChart(Chart):
    """
    Composition of two charts: T = T2 ∘ T1
    
    T(x) = T2(T1(x))
    T⁻¹(u) = T1⁻¹(T2⁻¹(u))
    """
    
    def __init__(self, inner: Chart, outer: Chart):
        super().__init__(ChartType.CUSTOM, f"({outer.name}∘{inner.name})")
        
        self.inner = inner
        self.outer = outer
    
    def forward(self, x: float) -> float:
        return self.outer.forward(self.inner.forward(x))
    
    def inverse(self, u: float) -> float:
        return self.inner.inverse(self.outer.inverse(u))
    
    def derivative(self, x: float) -> float:
        # Chain rule: (T2 ∘ T1)'(x) = T2'(T1(x)) * T1'(x)
        inner_val = self.inner.forward(x)
        return self.outer.derivative(inner_val) * self.inner.derivative(x)
    
    def inverse_derivative(self, u: float) -> float:
        outer_inv = self.outer.inverse(u)
        return self.inner.inverse_derivative(outer_inv) * \
               self.outer.inverse_derivative(u)
    
    def _get_params(self) -> str:
        return f"{self.inner.chart_id}:{self.outer.chart_id}"


# =============================================================================
# CHART FACTORY
# =============================================================================

class ChartFactory:
    """Factory for creating charts."""
    
    @staticmethod
    def create(chart_type: ChartType, **kwargs) -> Chart:
        """Create a chart of the specified type."""
        
        if chart_type == ChartType.IDENTITY:
            return IdentityChart()
        elif chart_type == ChartType.LINEAR:
            return LinearChart(
                scale=kwargs.get("scale", 1.0),
                offset=kwargs.get("offset", 0.0)
            )
        elif chart_type == ChartType.LOGARITHMIC:
            return LogarithmicChart(base=kwargs.get("base", np.e))
        elif chart_type == ChartType.EXPONENTIAL:
            return ExponentialChart(base=kwargs.get("base", np.e))
        elif chart_type == ChartType.POWER:
            return PowerChart(power=kwargs.get("power", 2.0))
        elif chart_type == ChartType.MOBIUS:
            return MobiusChart(
                a=kwargs.get("a", 1.0),
                b=kwargs.get("b", 0.0),
                c=kwargs.get("c", 0.0),
                d=kwargs.get("d", 1.0)
            )
        elif chart_type == ChartType.TRIGONOMETRIC:
            return TrigonometricChart(func=kwargs.get("func", "sin"))
        else:
            raise ValueError(f"Unknown chart type: {chart_type}")
    
    @staticmethod
    def compose(inner: Chart, outer: Chart) -> ComposedChart:
        """Create a composed chart."""
        return ComposedChart(inner, outer)
    
    @staticmethod
    def normalize(lower: float, upper: float) -> LinearChart:
        """Create a chart that normalizes [lower, upper] to [0, 1]."""
        scale = 1.0 / (upper - lower)
        offset = -lower * scale
        return LinearChart(scale=scale, offset=offset)
    
    @staticmethod
    def standardize(mean: float, std: float) -> LinearChart:
        """Create a chart that standardizes to mean=0, std=1."""
        return LinearChart(scale=1.0/std, offset=-mean/std)


# =============================================================================
# CHART CERTIFICATE
# =============================================================================

@dataclass
class ChartCorridorCertificate:
    """
    Certificate proving chart validity on a corridor.
    
    Required for Prove-level verification.
    """
    
    chart_id: str
    corridor: Corridor
    
    # Certificate components
    legality_proof: Dict[str, Any] = field(default_factory=dict)
    injectivity_proof: Dict[str, Any] = field(default_factory=dict)
    inverse_proof: Dict[str, Any] = field(default_factory=dict)
    
    # Level (L0=claim, L1=empirical, L2=certified, L3=formal)
    level: int = 0
    
    # Validator signature
    validator_id: Optional[str] = None
    validated_at: Optional[float] = None
    
    @property
    def is_valid(self) -> bool:
        """Check if certificate is valid."""
        return (self.corridor.is_certified and 
                self.level >= 1)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "chart_id": self.chart_id,
            "corridor": {
                "lower": self.corridor.lower,
                "upper": self.corridor.upper,
                "status": self.corridor.status.value,
                "monotonicity": self.corridor.monotonicity.value
            },
            "level": self.level,
            "validator_id": self.validator_id
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_charts() -> bool:
    """Validate charts module."""
    
    # Test Identity
    id_chart = IdentityChart()
    assert id_chart.forward(5.0) == 5.0
    assert id_chart.inverse(5.0) == 5.0
    
    # Test Linear
    lin_chart = LinearChart(scale=2.0, offset=1.0)
    assert lin_chart.forward(3.0) == 7.0
    assert abs(lin_chart.inverse(7.0) - 3.0) < 1e-10
    
    # Test Log/Exp
    log_chart = LogarithmicChart()
    exp_chart = ExponentialChart()
    assert abs(log_chart.forward(np.e) - 1.0) < 1e-10
    assert abs(exp_chart.forward(1.0) - np.e) < 1e-10
    
    # Test round-trip
    for x in [0.5, 1.0, 2.0, 5.0]:
        assert abs(log_chart.inverse(log_chart.forward(x)) - x) < 1e-10
        assert abs(exp_chart.inverse(exp_chart.forward(x)) - x) < 1e-10
    
    # Test Power
    pow_chart = PowerChart(power=2.0)
    assert pow_chart.forward(3.0) == 9.0
    assert abs(pow_chart.inverse(9.0) - 3.0) < 1e-10
    
    # Test Möbius
    mob_chart = MobiusChart(a=1.0, b=0.0, c=0.0, d=1.0)  # Identity
    assert mob_chart.forward(5.0) == 5.0
    
    # Test Trig
    sin_chart = TrigonometricChart("sin")
    assert abs(sin_chart.forward(np.pi/2) - 1.0) < 1e-10
    
    # Test Corridor Certification
    lin_chart2 = LinearChart(scale=2.0, offset=0.0)
    corridor = lin_chart2.certify_corridor(0.0, 10.0)
    assert corridor.is_certified
    assert corridor.monotonicity == MonotonicityType.STRICTLY_INCREASING
    
    # Test Composition
    composed = ChartFactory.compose(
        LinearChart(scale=2.0),
        LogarithmicChart()
    )
    x = 1.0
    assert abs(composed.inverse(composed.forward(x)) - x) < 1e-10
    
    # Test Factory
    chart = ChartFactory.create(ChartType.LINEAR, scale=3.0, offset=1.0)
    assert chart.forward(2.0) == 7.0
    
    # Test Normalize
    norm_chart = ChartFactory.normalize(10.0, 20.0)
    assert abs(norm_chart.forward(10.0) - 0.0) < 1e-10
    assert abs(norm_chart.forward(20.0) - 1.0) < 1e-10
    
    return True


if __name__ == "__main__":
    print("Validating Charts Module...")
    assert validate_charts()
    print("✓ Charts Module validated")
    
    # Demo
    print("\n--- Chart Rewriting Demo ---")
    
    # Create charts
    charts = [
        IdentityChart(),
        LinearChart(scale=2.0, offset=1.0),
        LogarithmicChart(),
        ExponentialChart(),
        PowerChart(power=2.0),
        TrigonometricChart("sin")
    ]
    
    x = 2.0
    print(f"\nTransformations of x = {x}:")
    for chart in charts:
        u = chart.forward(x)
        x_back = chart.inverse(u)
        print(f"  {chart.name}: T({x}) = {u:.4f}, T⁻¹({u:.4f}) = {x_back:.4f}")
    
    # Certify corridors
    print("\nCorridor Certification:")
    lin = LinearChart(scale=3.0, offset=-2.0)
    corridor = lin.certify_corridor(-10.0, 10.0)
    print(f"  Linear chart on [-10, 10]:")
    print(f"    Certified: {corridor.is_certified}")
    print(f"    Monotonicity: {corridor.monotonicity.value}")
    print(f"    Condition Number: {corridor.condition_number:.4f}")
    
    # Transport example
    print("\nOperator Transport:")
    f = lambda u: u**2 + 1  # Operator in coordinates
    log_chart = LogarithmicChart()
    
    x = 2.0
    direct = f(x)
    transported = log_chart.transport_operator(f, x)
    print(f"  f(x) = x² + 1")
    print(f"  Direct f({x}) = {direct}")
    print(f"  Transported through log chart: {transported:.4f}")
