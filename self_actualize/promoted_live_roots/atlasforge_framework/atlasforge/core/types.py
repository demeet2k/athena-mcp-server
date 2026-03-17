"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           ATLAS FORGE - Core Types                            ║
╚══════════════════════════════════════════════════════════════════════════════╝

Fundamental types for domains, intervals, and numerical policies.
These form the mathematical substrate on which all constructions are built.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import (
    Any, Callable, Dict, Generic, Iterator, List, Optional, 
    Set, Tuple, TypeVar, Union, Sequence
)
from enum import Enum
import math
import struct
import hashlib
from decimal import Decimal, ROUND_DOWN, ROUND_UP, ROUND_HALF_EVEN


# Type variables
T = TypeVar('T')
S = TypeVar('S')
Numeric = Union[int, float, Decimal]


class RoundingMode(Enum):
    """IEEE-754 rounding modes for deterministic floating-point semantics."""
    ROUND_DOWN = "round_down"           # Toward zero
    ROUND_UP = "round_up"               # Away from zero
    ROUND_FLOOR = "round_floor"         # Toward -∞
    ROUND_CEILING = "round_ceiling"     # Toward +∞
    ROUND_HALF_EVEN = "round_half_even" # Banker's rounding (default)
    ROUND_HALF_UP = "round_half_up"     # Standard rounding


@dataclass(frozen=True)
class FloatPolicy:
    """
    Policy for deterministic floating-point encoding and arithmetic.
    
    This ensures that semantically identical computations produce
    identical content hashes across platforms.
    
    Attributes:
        precision: Number of significant digits to preserve
        rounding: Rounding mode for operations
        encoding: Encoding format for serialization ('hex', 'decimal', 'binary')
        nan_handling: How to handle NaN ('error', 'propagate', 'replace')
        inf_handling: How to handle infinities ('error', 'propagate', 'clamp')
    """
    precision: int = 15
    rounding: RoundingMode = RoundingMode.ROUND_HALF_EVEN
    encoding: str = "hex"
    nan_handling: str = "error"
    inf_handling: str = "error"
    
    def encode(self, value: float) -> str:
        """Encode a float to canonical string representation."""
        if math.isnan(value):
            if self.nan_handling == "error":
                raise ValueError("NaN encountered with nan_handling='error'")
            return "NaN"
        
        if math.isinf(value):
            if self.inf_handling == "error":
                raise ValueError("Infinity encountered with inf_handling='error'")
            return "+Inf" if value > 0 else "-Inf"
        
        if self.encoding == "hex":
            return value.hex()
        elif self.encoding == "decimal":
            return f"{value:.{self.precision}e}"
        elif self.encoding == "binary":
            return struct.pack('!d', value).hex()
        else:
            raise ValueError(f"Unknown encoding: {self.encoding}")
    
    def decode(self, encoded: str) -> float:
        """Decode a canonical string to float."""
        if encoded == "NaN":
            return float('nan')
        if encoded == "+Inf":
            return float('inf')
        if encoded == "-Inf":
            return float('-inf')
        
        if self.encoding == "hex":
            return float.fromhex(encoded)
        elif self.encoding == "decimal":
            return float(encoded)
        elif self.encoding == "binary":
            return struct.unpack('!d', bytes.fromhex(encoded))[0]
        else:
            raise ValueError(f"Unknown encoding: {self.encoding}")
    
    def normalize(self, value: float) -> float:
        """Normalize a float according to this policy."""
        if math.isnan(value) or math.isinf(value):
            return value
        # Round-trip through encoding to normalize
        return self.decode(self.encode(value))


# Default float policy for the framework
DEFAULT_FLOAT_POLICY = FloatPolicy()


@dataclass(frozen=True)
class Bound:
    """
    A single bound (endpoint) of an interval.
    
    Attributes:
        value: The numerical value of the bound
        inclusive: Whether the bound is included in the interval
    """
    value: float
    inclusive: bool = True
    
    def __lt__(self, other: Bound) -> bool:
        if self.value != other.value:
            return self.value < other.value
        # If values equal, inclusive comes before exclusive for lower bounds
        return self.inclusive and not other.inclusive
    
    def __le__(self, other: Bound) -> bool:
        return self < other or self == other
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Bound):
            return NotImplemented
        return self.value == other.value and self.inclusive == other.inclusive
    
    def __hash__(self) -> int:
        return hash((self.value, self.inclusive))
    
    def __repr__(self) -> str:
        bracket = "[" if self.inclusive else "("
        return f"{bracket}{self.value}"


@dataclass
class Interval:
    """
    A closed, open, or half-open interval on the real line.
    
    This is the fundamental domain type for v1 of AtlasForge.
    Supports interval arithmetic with explicit rounding control.
    
    Attributes:
        lower: Lower bound
        upper: Upper bound
        float_policy: Policy for numerical operations
    
    Examples:
        >>> Interval(0, 1)              # [0, 1] closed
        >>> Interval(0, 1, lower_inclusive=False)  # (0, 1]
        >>> Interval.open(0, 1)         # (0, 1)
        >>> Interval.positive_reals()   # (0, +∞)
    """
    lower: float
    upper: float
    lower_inclusive: bool = True
    upper_inclusive: bool = True
    float_policy: FloatPolicy = field(default_factory=lambda: DEFAULT_FLOAT_POLICY)
    
    def __post_init__(self):
        if self.lower > self.upper:
            raise ValueError(f"Invalid interval: lower ({self.lower}) > upper ({self.upper})")
        if self.lower == self.upper and not (self.lower_inclusive and self.upper_inclusive):
            raise ValueError("Degenerate interval must be closed")
    
    @classmethod
    def closed(cls, lower: float, upper: float) -> Interval:
        """Create a closed interval [lower, upper]."""
        return cls(lower, upper, True, True)
    
    @classmethod
    def open(cls, lower: float, upper: float) -> Interval:
        """Create an open interval (lower, upper)."""
        return cls(lower, upper, False, False)
    
    @classmethod
    def left_open(cls, lower: float, upper: float) -> Interval:
        """Create a left-open interval (lower, upper]."""
        return cls(lower, upper, False, True)
    
    @classmethod
    def right_open(cls, lower: float, upper: float) -> Interval:
        """Create a right-open interval [lower, upper)."""
        return cls(lower, upper, True, False)
    
    @classmethod
    def point(cls, value: float) -> Interval:
        """Create a degenerate (point) interval [value, value]."""
        return cls(value, value, True, True)
    
    @classmethod
    def positive_reals(cls) -> Interval:
        """Create the interval (0, +∞)."""
        return cls(0, float('inf'), False, False)
    
    @classmethod
    def negative_reals(cls) -> Interval:
        """Create the interval (-∞, 0)."""
        return cls(float('-inf'), 0, False, False)
    
    @classmethod
    def all_reals(cls) -> Interval:
        """Create the interval (-∞, +∞)."""
        return cls(float('-inf'), float('inf'), False, False)
    
    @classmethod
    def unit(cls) -> Interval:
        """Create the unit interval [0, 1]."""
        return cls(0, 1, True, True)
    
    @property
    def is_bounded(self) -> bool:
        """Check if the interval is bounded (finite endpoints)."""
        return math.isfinite(self.lower) and math.isfinite(self.upper)
    
    @property
    def is_degenerate(self) -> bool:
        """Check if the interval is a single point."""
        return self.lower == self.upper
    
    @property
    def width(self) -> float:
        """Width of the interval."""
        return self.upper - self.lower
    
    @property
    def midpoint(self) -> float:
        """Midpoint of the interval."""
        if not self.is_bounded:
            raise ValueError("Cannot compute midpoint of unbounded interval")
        return (self.lower + self.upper) / 2
    
    @property
    def radius(self) -> float:
        """Radius (half-width) of the interval."""
        return self.width / 2
    
    @property
    def lo(self) -> float:
        """Alias for lower bound."""
        return self.lower
    
    @property
    def hi(self) -> float:
        """Alias for upper bound."""
        return self.upper
    
    def contains(self, x: float) -> bool:
        """Check if x is in this interval."""
        if x < self.lower or x > self.upper:
            return False
        if x == self.lower and not self.lower_inclusive:
            return False
        if x == self.upper and not self.upper_inclusive:
            return False
        return True
    
    def __contains__(self, x: float) -> bool:
        return self.contains(x)
    
    def contains_interval(self, other: Interval) -> bool:
        """Check if this interval contains another interval."""
        # Check lower bound
        if other.lower < self.lower:
            return False
        if other.lower == self.lower:
            if other.lower_inclusive and not self.lower_inclusive:
                return False
        # Check upper bound
        if other.upper > self.upper:
            return False
        if other.upper == self.upper:
            if other.upper_inclusive and not self.upper_inclusive:
                return False
        return True
    
    def intersects(self, other: Interval) -> bool:
        """Check if this interval intersects another."""
        if self.upper < other.lower or other.upper < self.lower:
            return False
        if self.upper == other.lower:
            return self.upper_inclusive and other.lower_inclusive
        if other.upper == self.lower:
            return other.upper_inclusive and self.lower_inclusive
        return True
    
    def intersection(self, other: Interval) -> Optional[Interval]:
        """Compute the intersection of two intervals."""
        if not self.intersects(other):
            return None
        
        # Determine lower bound
        if self.lower > other.lower:
            new_lower, new_lower_incl = self.lower, self.lower_inclusive
        elif self.lower < other.lower:
            new_lower, new_lower_incl = other.lower, other.lower_inclusive
        else:
            new_lower = self.lower
            new_lower_incl = self.lower_inclusive and other.lower_inclusive
        
        # Determine upper bound
        if self.upper < other.upper:
            new_upper, new_upper_incl = self.upper, self.upper_inclusive
        elif self.upper > other.upper:
            new_upper, new_upper_incl = other.upper, other.upper_inclusive
        else:
            new_upper = self.upper
            new_upper_incl = self.upper_inclusive and other.upper_inclusive
        
        return Interval(new_lower, new_upper, new_lower_incl, new_upper_incl)
    
    def union(self, other: Interval) -> Union[Interval, 'UnionDomain']:
        """Compute the union of two intervals."""
        if self.intersects(other) or self._touches(other):
            # Can merge into single interval
            if self.lower < other.lower:
                new_lower, new_lower_incl = self.lower, self.lower_inclusive
            elif self.lower > other.lower:
                new_lower, new_lower_incl = other.lower, other.lower_inclusive
            else:
                new_lower = self.lower
                new_lower_incl = self.lower_inclusive or other.lower_inclusive
            
            if self.upper > other.upper:
                new_upper, new_upper_incl = self.upper, self.upper_inclusive
            elif self.upper < other.upper:
                new_upper, new_upper_incl = other.upper, other.upper_inclusive
            else:
                new_upper = self.upper
                new_upper_incl = self.upper_inclusive or other.upper_inclusive
            
            return Interval(new_lower, new_upper, new_lower_incl, new_upper_incl)
        else:
            # Disjoint, return union domain
            return UnionDomain([self, other])
    
    def _touches(self, other: Interval) -> bool:
        """Check if intervals touch at a single point."""
        if self.upper == other.lower:
            return self.upper_inclusive or other.lower_inclusive
        if other.upper == self.lower:
            return other.upper_inclusive or self.lower_inclusive
        return False
    
    def split(self, x: Optional[float] = None) -> Tuple[Interval, Interval]:
        """Split the interval at point x (default: midpoint)."""
        if x is None:
            x = self.midpoint
        if x not in self:
            raise ValueError(f"Split point {x} not in interval")
        
        left = Interval(self.lower, x, self.lower_inclusive, True)
        right = Interval(x, self.upper, True, self.upper_inclusive)
        return left, right
    
    def subdivide(self, n: int) -> List[Interval]:
        """Subdivide the interval into n equal parts."""
        if n < 1:
            raise ValueError("n must be >= 1")
        if not self.is_bounded:
            raise ValueError("Cannot subdivide unbounded interval")
        
        step = self.width / n
        intervals = []
        for i in range(n):
            lo = self.lower + i * step
            hi = self.lower + (i + 1) * step
            lo_incl = self.lower_inclusive if i == 0 else True
            hi_incl = self.upper_inclusive if i == n - 1 else False
            intervals.append(Interval(lo, hi, lo_incl, hi_incl))
        return intervals
    
    # Interval arithmetic operations
    
    def __add__(self, other: Union[Interval, float]) -> Interval:
        """Interval addition: [a,b] + [c,d] = [a+c, b+d]."""
        if isinstance(other, (int, float)):
            return Interval(
                self.lower + other, self.upper + other,
                self.lower_inclusive, self.upper_inclusive
            )
        return Interval(
            self.lower + other.lower, self.upper + other.upper,
            self.lower_inclusive and other.lower_inclusive,
            self.upper_inclusive and other.upper_inclusive
        )
    
    def __radd__(self, other: float) -> Interval:
        return self + other
    
    def __neg__(self) -> Interval:
        """Negation: -[a,b] = [-b, -a]."""
        return Interval(
            -self.upper, -self.lower,
            self.upper_inclusive, self.lower_inclusive
        )
    
    def __sub__(self, other: Union[Interval, float]) -> Interval:
        """Interval subtraction."""
        if isinstance(other, (int, float)):
            return self + (-other)
        return self + (-other)
    
    def __rsub__(self, other: float) -> Interval:
        return (-self) + other
    
    def __mul__(self, other: Union[Interval, float]) -> Interval:
        """Interval multiplication."""
        if isinstance(other, (int, float)):
            if other >= 0:
                return Interval(
                    self.lower * other, self.upper * other,
                    self.lower_inclusive, self.upper_inclusive
                )
            else:
                return Interval(
                    self.upper * other, self.lower * other,
                    self.upper_inclusive, self.lower_inclusive
                )
        
        products = [
            self.lower * other.lower,
            self.lower * other.upper,
            self.upper * other.lower,
            self.upper * other.upper
        ]
        return Interval(min(products), max(products))
    
    def __rmul__(self, other: float) -> Interval:
        return self * other
    
    def __truediv__(self, other: Union[Interval, float]) -> Interval:
        """Interval division."""
        if isinstance(other, (int, float)):
            if other == 0:
                raise ZeroDivisionError("Division by zero")
            return self * (1.0 / other)
        
        if 0 in other:
            raise ZeroDivisionError("Division by interval containing zero")
        
        reciprocal = Interval(1.0 / other.upper, 1.0 / other.lower)
        return self * reciprocal
    
    def __pow__(self, n: int) -> Interval:
        """Interval power (integer exponent)."""
        if n == 0:
            return Interval.point(1.0)
        if n == 1:
            return self
        if n < 0:
            return (Interval.point(1.0) / self) ** (-n)
        
        if n % 2 == 1:
            # Odd power preserves sign
            return Interval(self.lower ** n, self.upper ** n)
        else:
            # Even power
            if self.lower >= 0:
                return Interval(self.lower ** n, self.upper ** n)
            elif self.upper <= 0:
                return Interval(self.upper ** n, self.lower ** n)
            else:
                return Interval(0, max(self.lower ** n, self.upper ** n))
    
    def sqrt(self) -> Interval:
        """Interval square root."""
        if self.lower < 0:
            raise ValueError("Square root of interval with negative values")
        return Interval(math.sqrt(max(0, self.lower)), math.sqrt(self.upper))
    
    def exp(self) -> Interval:
        """Interval exponential."""
        return Interval(math.exp(self.lower), math.exp(self.upper))
    
    def log(self) -> Interval:
        """Interval natural logarithm."""
        if self.lower <= 0:
            raise ValueError("Logarithm of interval containing non-positive values")
        return Interval(math.log(self.lower), math.log(self.upper))
    
    def sin(self) -> Interval:
        """Interval sine (conservative bounds)."""
        # This is a simplified version; full implementation needs range reduction
        if self.width >= 2 * math.pi:
            return Interval(-1, 1)
        
        # Evaluate at endpoints and critical points in range
        values = [math.sin(self.lower), math.sin(self.upper)]
        
        # Check for critical points (multiples of π/2)
        k_start = math.ceil((self.lower - math.pi/2) / math.pi)
        k_end = math.floor((self.upper - math.pi/2) / math.pi)
        
        for k in range(int(k_start), int(k_end) + 1):
            critical = math.pi/2 + k * math.pi
            if self.lower <= critical <= self.upper:
                values.append(math.sin(critical))
        
        return Interval(min(values), max(values))
    
    def cos(self) -> Interval:
        """Interval cosine (conservative bounds)."""
        # cos(x) = sin(x + π/2)
        shifted = Interval(self.lower + math.pi/2, self.upper + math.pi/2)
        return shifted.sin()
    
    def canonical_repr(self) -> str:
        """Canonical string representation for hashing."""
        policy = self.float_policy
        lb = "[" if self.lower_inclusive else "("
        ub = "]" if self.upper_inclusive else ")"
        return f"Interval{lb}{policy.encode(self.lower)},{policy.encode(self.upper)}{ub}"
    
    def __repr__(self) -> str:
        lb = "[" if self.lower_inclusive else "("
        ub = "]" if self.upper_inclusive else ")"
        return f"Interval{lb}{self.lower}, {self.upper}{ub}"
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Interval):
            return NotImplemented
        return (
            self.lower == other.lower and
            self.upper == other.upper and
            self.lower_inclusive == other.lower_inclusive and
            self.upper_inclusive == other.upper_inclusive
        )
    
    def __hash__(self) -> int:
        return hash((self.lower, self.upper, self.lower_inclusive, self.upper_inclusive))


class Domain(ABC):
    """
    Abstract base class for all domain types.
    
    A domain is a structured subset of R^n with explicit
    boundary/regularity declarations.
    """
    
    @abstractmethod
    def contains(self, x: Any) -> bool:
        """Check if x is in this domain."""
        pass
    
    @abstractmethod
    def is_bounded(self) -> bool:
        """Check if the domain is bounded."""
        pass
    
    @abstractmethod
    def canonical_repr(self) -> str:
        """Canonical string representation for hashing."""
        pass
    
    @abstractmethod
    def dimension(self) -> int:
        """Dimension of the domain."""
        pass


@dataclass
class UnionDomain(Domain):
    """
    A domain formed as the union of disjoint intervals.
    
    Attributes:
        intervals: List of disjoint intervals (automatically sorted and merged)
    """
    intervals: List[Interval] = field(default_factory=list)
    
    def __post_init__(self):
        # Sort and merge overlapping intervals
        self._normalize()
    
    def _normalize(self):
        """Sort and merge overlapping intervals."""
        if not self.intervals:
            return
        
        # Sort by lower bound
        sorted_intervals = sorted(self.intervals, key=lambda i: (i.lower, not i.lower_inclusive))
        
        merged = [sorted_intervals[0]]
        for current in sorted_intervals[1:]:
            last = merged[-1]
            if last.intersects(current) or last._touches(current):
                merged[-1] = last.union(current)
                if isinstance(merged[-1], UnionDomain):
                    # Should not happen after sorting, but handle gracefully
                    merged[-1] = merged[-1].intervals[0]
            else:
                merged.append(current)
        
        self.intervals = merged
    
    def contains(self, x: float) -> bool:
        """Check if x is in any of the component intervals."""
        return any(interval.contains(x) for interval in self.intervals)
    
    def __contains__(self, x: float) -> bool:
        return self.contains(x)
    
    def is_bounded(self) -> bool:
        """Check if all component intervals are bounded."""
        return all(interval.is_bounded for interval in self.intervals)
    
    def dimension(self) -> int:
        return 1
    
    def canonical_repr(self) -> str:
        parts = [i.canonical_repr() for i in self.intervals]
        return f"UnionDomain({','.join(parts)})"
    
    def __repr__(self) -> str:
        return f"UnionDomain({self.intervals})"
    
    def __len__(self) -> int:
        return len(self.intervals)
    
    def __iter__(self) -> Iterator[Interval]:
        return iter(self.intervals)


@dataclass
class PointSet(Domain):
    """
    A domain consisting of a finite set of discrete points.
    
    Attributes:
        points: The set of points
    """
    points: Set[float] = field(default_factory=set)
    
    def contains(self, x: float) -> bool:
        return x in self.points
    
    def __contains__(self, x: float) -> bool:
        return self.contains(x)
    
    def is_bounded(self) -> bool:
        if not self.points:
            return True
        return all(math.isfinite(p) for p in self.points)
    
    def dimension(self) -> int:
        return 0  # Discrete points have dimension 0
    
    def canonical_repr(self) -> str:
        policy = DEFAULT_FLOAT_POLICY
        sorted_points = sorted(self.points)
        encoded = [policy.encode(p) for p in sorted_points]
        return f"PointSet({{{','.join(encoded)}}})"
    
    def __repr__(self) -> str:
        return f"PointSet({self.points})"
    
    def __len__(self) -> int:
        return len(self.points)
    
    def __iter__(self) -> Iterator[float]:
        return iter(self.points)


@dataclass
class RectangularDomain(Domain):
    """
    A rectangular domain in R^n (product of intervals).
    
    Attributes:
        intervals: List of intervals, one per dimension
    """
    intervals: List[Interval] = field(default_factory=list)
    
    def contains(self, x: Sequence[float]) -> bool:
        if len(x) != len(self.intervals):
            return False
        return all(interval.contains(xi) for interval, xi in zip(self.intervals, x))
    
    def __contains__(self, x: Sequence[float]) -> bool:
        return self.contains(x)
    
    def is_bounded(self) -> bool:
        return all(interval.is_bounded for interval in self.intervals)
    
    def dimension(self) -> int:
        return len(self.intervals)
    
    def canonical_repr(self) -> str:
        parts = [i.canonical_repr() for i in self.intervals]
        return f"RectangularDomain({','.join(parts)})"
    
    def __repr__(self) -> str:
        return f"RectangularDomain({self.intervals})"
    
    def project(self, dim: int) -> Interval:
        """Project onto a single dimension."""
        return self.intervals[dim]
    
    def slice_at(self, dim: int, value: float) -> 'RectangularDomain':
        """Fix one dimension at a value, returning lower-dimensional domain."""
        new_intervals = [i for j, i in enumerate(self.intervals) if j != dim]
        return RectangularDomain(new_intervals)


@dataclass
class Lattice(Domain):
    """
    A discrete lattice domain: { base + k*step : k ∈ Z, base + k*step ∈ bounds }.
    
    Used for generator constraints like T(x_k) = θ + kΔ.
    
    Attributes:
        base: The base point (θ)
        step: The step size (Δ)
        bounds: Optional bounding interval
    """
    base: float
    step: float
    bounds: Optional[Interval] = None
    
    def contains(self, x: float) -> bool:
        if self.bounds and x not in self.bounds:
            return False
        
        # Check if x = base + k*step for some integer k
        if self.step == 0:
            return x == self.base
        
        k = (x - self.base) / self.step
        return abs(k - round(k)) < 1e-10
    
    def is_bounded(self) -> bool:
        return self.bounds is not None and self.bounds.is_bounded
    
    def dimension(self) -> int:
        return 0  # Discrete
    
    def canonical_repr(self) -> str:
        policy = DEFAULT_FLOAT_POLICY
        base_enc = policy.encode(self.base)
        step_enc = policy.encode(self.step)
        bounds_repr = self.bounds.canonical_repr() if self.bounds else "None"
        return f"Lattice({base_enc},{step_enc},{bounds_repr})"
    
    def __repr__(self) -> str:
        return f"Lattice(base={self.base}, step={self.step}, bounds={self.bounds})"
    
    def enumerate(self, max_count: int = 1000) -> List[float]:
        """Enumerate lattice points within bounds."""
        if self.bounds is None:
            raise ValueError("Cannot enumerate unbounded lattice")
        
        points = []
        k = 0
        while len(points) < max_count:
            x_pos = self.base + k * self.step
            x_neg = self.base - k * self.step if k > 0 else None
            
            added = False
            if x_pos in self.bounds:
                points.append(x_pos)
                added = True
            if x_neg is not None and x_neg in self.bounds:
                points.append(x_neg)
                added = True
            
            if not added and k > 0:
                break
            k += 1
        
        return sorted(set(points))


# Type alias for any domain
AnyDomain = Union[Interval, UnionDomain, PointSet, RectangularDomain, Lattice]
