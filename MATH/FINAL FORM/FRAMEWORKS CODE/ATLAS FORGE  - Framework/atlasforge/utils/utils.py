"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         ATLAS FORGE - Utilities                               ║
╚══════════════════════════════════════════════════════════════════════════════╝

Hash utilities, interval helpers, numerical differentiation, and common helpers.
"""

from __future__ import annotations
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import hashlib
import json
import math
from functools import wraps
from dataclasses import asdict, is_dataclass

from atlasforge.core.types import Interval


# ═══════════════════════════════════════════════════════════════════════════════
# HASH UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

def sha256_hash(data: Union[str, bytes]) -> str:
    """Compute SHA-256 hash of data."""
    if isinstance(data, str):
        data = data.encode('utf-8')
    return hashlib.sha256(data).hexdigest()


def content_hash(obj: Any) -> str:
    """Compute content hash of an object."""
    if hasattr(obj, 'content_hash'):
        return obj.content_hash()
    if hasattr(obj, 'canonical_repr'):
        return sha256_hash(obj.canonical_repr())
    if isinstance(obj, (str, bytes)):
        return sha256_hash(obj)
    if isinstance(obj, (int, float)):
        return sha256_hash(f"{obj:.15e}" if isinstance(obj, float) else str(obj))
    if isinstance(obj, (list, tuple)):
        return sha256_hash('|'.join(content_hash(x) for x in obj))
    if isinstance(obj, dict):
        sorted_items = sorted(obj.items(), key=lambda x: str(x[0]))
        return sha256_hash('|'.join(f"{k}:{content_hash(v)}" for k, v in sorted_items))
    if is_dataclass(obj):
        return sha256_hash(json.dumps(asdict(obj), sort_keys=True, default=str))
    return sha256_hash(str(obj))


def short_hash(obj: Any, length: int = 8) -> str:
    return content_hash(obj)[:length]


def combine_hashes(*hashes: str) -> str:
    return sha256_hash('|'.join(hashes))


# ═══════════════════════════════════════════════════════════════════════════════
# INTERVAL HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def interval_eval(f: Callable[[float], float], I: Interval, samples: int = 100) -> Interval:
    """Approximate range of f over I by sampling."""
    if not I.is_bounded:
        raise ValueError("Interval must be bounded")
    values = []
    for i in range(samples + 1):
        t = i / samples
        x = I.lo + t * I.width
        try:
            y = f(x)
            if math.isfinite(y):
                values.append(y)
        except Exception:
            pass
    return Interval.closed(min(values), max(values)) if values else Interval.empty()


def interval_sign_change(f: Callable[[float], float], I: Interval) -> bool:
    """Check if f has a sign change over I."""
    try:
        return f(I.lo) * f(I.hi) < 0
    except Exception:
        return False


def bisect_interval(I: Interval) -> Tuple[Interval, Interval]:
    """Bisect an interval."""
    mid = I.midpoint
    return Interval.closed(I.lo, mid), Interval.closed(mid, I.hi)


def subdivide_interval(I: Interval, n: int) -> List[Interval]:
    """Subdivide interval into n parts."""
    step = I.width / n
    return [Interval.closed(I.lo + i*step, I.lo + (i+1)*step) for i in range(n)]


# ═══════════════════════════════════════════════════════════════════════════════
# NUMERICAL DIFFERENTIATION
# ═══════════════════════════════════════════════════════════════════════════════

def derivative(f: Callable[[float], float], x: float, h: float = 1e-8) -> float:
    """Central difference derivative."""
    return (f(x + h) - f(x - h)) / (2 * h)


def second_derivative(f: Callable[[float], float], x: float, h: float = 1e-5) -> float:
    """Second derivative."""
    return (f(x + h) - 2 * f(x) + f(x - h)) / (h * h)


def gradient(f: Callable[[List[float]], float], x: List[float], h: float = 1e-8) -> List[float]:
    """Numerical gradient."""
    grad = []
    for i in range(len(x)):
        x_plus, x_minus = x.copy(), x.copy()
        x_plus[i] += h
        x_minus[i] -= h
        grad.append((f(x_plus) - f(x_minus)) / (2 * h))
    return grad


def jacobian(f: Callable[[List[float]], List[float]], x: List[float], h: float = 1e-8) -> List[List[float]]:
    """Numerical Jacobian matrix."""
    fx = f(x)
    J = [[0.0] * len(x) for _ in range(len(fx))]
    for j in range(len(x)):
        x_plus, x_minus = x.copy(), x.copy()
        x_plus[j] += h
        x_minus[j] -= h
        f_plus, f_minus = f(x_plus), f(x_minus)
        for i in range(len(fx)):
            J[i][j] = (f_plus[i] - f_minus[i]) / (2 * h)
    return J


# ═══════════════════════════════════════════════════════════════════════════════
# MATHEMATICAL HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def sign(x: float) -> int:
    return 1 if x > 0 else (-1 if x < 0 else 0)


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def lerp(a: float, b: float, t: float) -> float:
    return a + t * (b - a)


def relative_error(computed: float, exact: float) -> float:
    return abs(computed - exact) / abs(exact) if exact != 0 else abs(computed)


def nearly_equal(a: float, b: float, rel_tol: float = 1e-9, abs_tol: float = 1e-12) -> bool:
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


def quadratic_roots(a: float, b: float, c: float) -> List[float]:
    """Solve ax² + bx + c = 0."""
    if abs(a) < 1e-15:
        return [-c / b] if abs(b) >= 1e-15 else []
    disc = b * b - 4 * a * c
    if disc < 0:
        return []
    elif disc == 0:
        return [-b / (2 * a)]
    sqrt_d = math.sqrt(disc)
    return [(-b - sqrt_d) / (2 * a), (-b + sqrt_d) / (2 * a)]


def golden_ratio() -> float:
    return (1 + math.sqrt(5)) / 2


def fibonacci(n: int) -> int:
    if n <= 1:
        return max(0, n)
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def factorial(n: int) -> int:
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


def binomial(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    k = min(k, n - k)
    result = 1
    for i in range(k):
        result = result * (n - i) // (i + 1)
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# SERIALIZATION
# ═══════════════════════════════════════════════════════════════════════════════

def to_json(obj: Any, indent: int = 2) -> str:
    def default_serializer(o):
        if hasattr(o, 'to_dict'):
            return o.to_dict()
        if is_dataclass(o):
            return asdict(o)
        return str(o)
    return json.dumps(obj, indent=indent, default=default_serializer, sort_keys=True)


def from_json(s: str) -> Any:
    return json.loads(s)


# ═══════════════════════════════════════════════════════════════════════════════
# DECORATORS
# ═══════════════════════════════════════════════════════════════════════════════

def memoize(f: Callable) -> Callable:
    cache = {}
    @wraps(f)
    def wrapper(*args):
        if args not in cache:
            cache[args] = f(*args)
        return cache[args]
    wrapper.cache = cache
    wrapper.clear_cache = cache.clear
    return wrapper


# ═══════════════════════════════════════════════════════════════════════════════
# VALIDATION
# ═══════════════════════════════════════════════════════════════════════════════

def assert_finite(x: float, name: str = "value"):
    if not math.isfinite(x):
        raise ValueError(f"{name} must be finite, got {x}")


def assert_positive(x: float, name: str = "value"):
    if x <= 0:
        raise ValueError(f"{name} must be positive, got {x}")


def assert_in_range(x: float, lo: float, hi: float, name: str = "value"):
    if not (lo <= x <= hi):
        raise ValueError(f"{name} must be in [{lo}, {hi}], got {x}")
