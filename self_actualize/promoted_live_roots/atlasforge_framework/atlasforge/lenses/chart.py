"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         ATLAS FORGE - Charts & Lenses                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

The Lens/Chart transformation system for coordinate transport.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Generic, List, Optional, Tuple, TypeVar, Union
import math

from atlasforge.core.types import Interval, AnyDomain
from atlasforge.core.enums import CertificateLevel

T = TypeVar('T')
S = TypeVar('S')
Numeric = Union[int, float, complex]


class ChartError(Exception):
    """Exception raised for chart-related errors."""
    pass


class CorridorViolation(ChartError):
    """Exception raised when a corridor condition is violated."""
    pass


@dataclass(frozen=True)
class CorridorCondition:
    """A corridor condition specifies where a chart is valid."""
    domain: AnyDomain
    name: str = "corridor"
    predicate: Optional[Callable[[Numeric], bool]] = None
    jacobian_bound: Optional[Tuple[float, float]] = None
    
    def contains(self, x: Numeric) -> bool:
        if isinstance(x, complex):
            if isinstance(self.domain, Interval):
                return self.domain.contains(x.real)
        elif isinstance(self.domain, Interval):
            if not self.domain.contains(float(x)):
                return False
        if self.predicate is not None:
            return self.predicate(x)
        return True
    
    def __contains__(self, x: Numeric) -> bool:
        return self.contains(x)
    
    def assert_in(self, x: Numeric, context: str = ""):
        if not self.contains(x):
            msg = f"Value {x} not in corridor {self.name}"
            if context:
                msg = f"{context}: {msg}"
            raise CorridorViolation(msg)


class Chart(ABC, Generic[T, S]):
    """Abstract base class for charts (coordinate transformations)."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @property
    @abstractmethod
    def symbol(self) -> str:
        pass
    
    @property
    @abstractmethod
    def corridor(self) -> CorridorCondition:
        pass
    
    @property
    def domain(self) -> AnyDomain:
        return self.corridor.domain
    
    @abstractmethod
    def forward(self, x: T) -> S:
        pass
    
    @abstractmethod
    def inverse(self, y: S) -> T:
        pass
    
    def __call__(self, x: T) -> S:
        return self.forward(x)
    
    def jacobian(self, x: T) -> float:
        eps = 1e-8
        return (self.forward(float(x) + eps) - self.forward(float(x) - eps)) / (2 * eps)
    
    def inverse_jacobian(self, y: S) -> float:
        x = self.inverse(y)
        j = self.jacobian(x)
        if abs(j) < 1e-15:
            raise ChartError(f"Singular Jacobian at {x}")
        return 1.0 / j
    
    def transported_add(self, x: T, y: T) -> T:
        return self.inverse(self.forward(x) + self.forward(y))
    
    def transported_mul(self, x: T, y: T) -> T:
        return self.inverse(self.forward(x) * self.forward(y))
    
    def pullback(self, f: Callable[[S], S]) -> Callable[[T], T]:
        def pulled_back(x: T) -> T:
            return self.inverse(f(self.forward(x)))
        return pulled_back
    
    def pushforward(self, g: Callable[[T], T]) -> Callable[[S], S]:
        def pushed_forward(y: S) -> S:
            x = self.inverse(y)
            return self.forward(g(x))
        return pushed_forward


@dataclass
class ComposedChart(Chart[T, Any]):
    """Composition of two charts."""
    inner: Chart
    outer: Chart
    
    @property
    def name(self) -> str:
        return f"{self.outer.name} ∘ {self.inner.name}"
    
    @property
    def symbol(self) -> str:
        return f"{self.outer.symbol} ∘ {self.inner.symbol}"
    
    @property
    def corridor(self) -> CorridorCondition:
        return self.inner.corridor
    
    def forward(self, x: T) -> Any:
        return self.outer.forward(self.inner.forward(x))
    
    def inverse(self, z: Any) -> T:
        return self.inner.inverse(self.outer.inverse(z))


class Lens(Chart[T, S]):
    """A Lens is a named, reusable chart with metadata."""
    
    def __init__(self, name: str, symbol: str, corridor: CorridorCondition,
                 forward_fn: Callable[[T], S], inverse_fn: Callable[[S], T],
                 jacobian_fn: Optional[Callable[[T], float]] = None, **metadata):
        self._name = name
        self._symbol = symbol
        self._corridor = corridor
        self._forward_fn = forward_fn
        self._inverse_fn = inverse_fn
        self._jacobian_fn = jacobian_fn
        self._metadata = metadata
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def symbol(self) -> str:
        return self._symbol
    
    @property
    def corridor(self) -> CorridorCondition:
        return self._corridor
    
    def forward(self, x: T) -> S:
        return self._forward_fn(x)
    
    def inverse(self, y: S) -> T:
        return self._inverse_fn(y)
    
    def jacobian(self, x: T) -> float:
        if self._jacobian_fn:
            return self._jacobian_fn(x)
        return super().jacobian(x)


@dataclass
class ChartCertificate:
    """Certificate attesting to properties of a chart."""
    chart_name: str
    domain: AnyDomain
    is_bijective: Optional[bool] = None
    smoothness_order: Optional[int] = None
    jacobian_lower_bound: Optional[float] = None
    jacobian_upper_bound: Optional[float] = None
    corridor_valid: Optional[bool] = None
    level: CertificateLevel = CertificateLevel.L0_CLAIM


class ChartFactory:
    """Factory for creating common charts."""
    
    @staticmethod
    def identity(domain: AnyDomain = Interval.all_reals()) -> Lens:
        return Lens("Identity", "Id", CorridorCondition(domain, "all"),
                    lambda x: x, lambda x: x, lambda x: 1.0)
    
    @staticmethod
    def linear(a: float, b: float = 0) -> Lens:
        if a == 0:
            raise ChartError("Linear coefficient 'a' cannot be zero")
        return Lens(f"Linear({a},{b})", f"{a}x+{b}",
                    CorridorCondition(Interval.all_reals(), "linear"),
                    lambda x: a * x + b, lambda y: (y - b) / a, lambda x: a)
    
    @staticmethod
    def logarithmic(base: float = math.e) -> Lens:
        log_base = math.log(base)
        return Lens("Ln" if base == math.e else f"Log({base})", "ln",
                    CorridorCondition(Interval.positive_reals(), "positive", lambda x: x > 0),
                    lambda x: math.log(x) / log_base, lambda y: base ** y,
                    lambda x: 1 / (x * log_base))
    
    @staticmethod
    def exponential(base: float = math.e) -> Lens:
        log_base = math.log(base)
        return Lens("Exp" if base == math.e else f"Exp({base})", "exp",
                    CorridorCondition(Interval.all_reals(), "all"),
                    lambda x: base ** x, lambda y: math.log(y) / log_base,
                    lambda x: log_base * (base ** x))
    
    @staticmethod
    def trigonometric(func: str = "tan") -> Lens:
        if func == "tan":
            return Lens("Tan", "tan",
                        CorridorCondition(Interval.open(-math.pi/2, math.pi/2), "(-π/2,π/2)"),
                        math.tan, math.atan, lambda x: 1 / (math.cos(x) ** 2))
        elif func == "sin":
            return Lens("Sin", "sin",
                        CorridorCondition(Interval.closed(-math.pi/2, math.pi/2), "[-π/2,π/2]"),
                        math.sin, math.asin, math.cos)
        raise ChartError(f"Unknown trig function: {func}")
    
    @staticmethod
    def logit() -> Lens:
        return Lens("Logit", "logit",
                    CorridorCondition(Interval.open(0, 1), "(0,1)", lambda x: 0 < x < 1),
                    lambda x: math.log(x / (1 - x)),
                    lambda y: 1 / (1 + math.exp(-y)),
                    lambda x: 1 / (x * (1 - x)))
