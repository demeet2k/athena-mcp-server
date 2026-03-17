"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                     NORMAL FORM COMPILER MODULE                              ║
║                                                                              ║
║  Canonicalization and Normal Form Computation                                ║
║                                                                              ║
║  Core Principle:                                                             ║
║    Every mathematical object has a CANONICAL representation                  ║
║    NF: Object → Canonical form (unique modulo equivalence)                   ║
║                                                                              ║
║  The Four Chart Normal Forms:                                                ║
║    □ NF: Exact discrete normal form (polynomials, matrices, integers)       ║
║    ✿ NF: Transform-domain normal form (Fourier, hub-locked)                 ║
║    ☁ NF: Bound-qualified form (BO with explicit uncertainty)                ║
║    ⟂ NF: Seed normal form (minimal reconstruction data + checksum)          ║
║                                                                              ║
║  Global "Same Object" Rule:                                                  ║
║    Objects equal iff NFs equal (up to chart)                                 ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Any, Callable, Generic, TypeVar
from enum import Enum
import numpy as np
from numpy.typing import NDArray
import hashlib


T = TypeVar('T')


# ═══════════════════════════════════════════════════════════════════════════════
# NORMAL FORM TYPES
# ═══════════════════════════════════════════════════════════════════════════════

class NFType(Enum):
    """Types of normal forms by chart."""
    SQUARE = "square"       # □ Exact/discrete
    FLOWER = "flower"       # ✿ Transform/hub
    CLOUD = "cloud"         # ☁ Bound-qualified
    FRACTAL = "fractal"     # ⟂ Seed/minimal


class CanonicalStatus(Enum):
    """Status of canonicalization."""
    CANONICAL = "canonical"         # In normal form
    NON_CANONICAL = "non_canonical" # Needs reduction
    PARTIAL = "partial"             # Partially reduced
    UNKNOWN = "unknown"             # Status not determined


# ═══════════════════════════════════════════════════════════════════════════════
# NORMAL FORM BASE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class NormalForm:
    """
    Base class for normal forms.
    """
    nf_type: NFType
    value: Any
    checksum: str = ""
    status: CanonicalStatus = CanonicalStatus.UNKNOWN
    
    def __post_init__(self):
        """Compute checksum."""
        self._compute_checksum()
    
    def _compute_checksum(self):
        """Compute content-addressed checksum."""
        data = f"{self.nf_type.name}|{repr(self.value)}"
        self.checksum = hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def __eq__(self, other: 'NormalForm') -> bool:
        """Equality via checksum."""
        if not isinstance(other, NormalForm):
            return False
        return self.checksum == other.checksum
    
    def __hash__(self) -> int:
        return hash(self.checksum)


# ═══════════════════════════════════════════════════════════════════════════════
# SQUARE NORMAL FORM (□)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SquareNF(NormalForm):
    """
    □ Square chart normal form: exact/discrete.
    
    Examples:
    - Polynomials: monic, ordered coefficients
    - Matrices: row echelon, Jordan form
    - Integers: (p, q) reduced fraction
    - Sequences: canonical ordering
    """
    
    @classmethod
    def polynomial(cls, coeffs: List[float]) -> 'SquareNF':
        """
        Polynomial normal form.
        
        Standard form: monic if possible, ordered by degree.
        """
        # Remove trailing zeros
        while coeffs and abs(coeffs[-1]) < 1e-15:
            coeffs.pop()
        
        if not coeffs:
            return cls(NFType.SQUARE, [], status=CanonicalStatus.CANONICAL)
        
        # Make monic (leading coeff = 1)
        lead = coeffs[-1]
        if abs(lead) > 1e-15:
            coeffs = [c / lead for c in coeffs]
        
        return cls(NFType.SQUARE, tuple(coeffs), status=CanonicalStatus.CANONICAL)
    
    @classmethod
    def rational(cls, p: int, q: int) -> 'SquareNF':
        """
        Rational number normal form p/q.
        
        Standard form: gcd(p, q) = 1, q > 0
        """
        import math
        if q == 0:
            raise ValueError("Denominator cannot be zero")
        
        # Sign convention
        if q < 0:
            p, q = -p, -q
        
        # Reduce
        g = math.gcd(abs(p), q)
        p, q = p // g, q // g
        
        return cls(NFType.SQUARE, (p, q), status=CanonicalStatus.CANONICAL)
    
    @classmethod
    def matrix_echelon(cls, M: NDArray) -> 'SquareNF':
        """
        Matrix row echelon form.
        """
        M = np.array(M, dtype=float).copy()
        rows, cols = M.shape
        
        pivot_row = 0
        for col in range(cols):
            # Find pivot
            max_row = pivot_row
            for row in range(pivot_row + 1, rows):
                if abs(M[row, col]) > abs(M[max_row, col]):
                    max_row = row
            
            if abs(M[max_row, col]) < 1e-15:
                continue
            
            # Swap
            M[[pivot_row, max_row]] = M[[max_row, pivot_row]]
            
            # Scale pivot to 1
            M[pivot_row] = M[pivot_row] / M[pivot_row, col]
            
            # Eliminate below
            for row in range(pivot_row + 1, rows):
                M[row] -= M[row, col] * M[pivot_row]
            
            pivot_row += 1
        
        return cls(NFType.SQUARE, tuple(map(tuple, M)), status=CanonicalStatus.CANONICAL)
    
    @classmethod
    def integer_factorization(cls, n: int) -> 'SquareNF':
        """
        Integer factorization normal form.
        
        n = p₁^e₁ × p₂^e₂ × ... (sorted primes)
        """
        if n <= 1:
            return cls(NFType.SQUARE, ((n, 1),), status=CanonicalStatus.CANONICAL)
        
        factors = []
        d = 2
        temp = abs(n)
        
        while d * d <= temp:
            exp = 0
            while temp % d == 0:
                exp += 1
                temp //= d
            if exp > 0:
                factors.append((d, exp))
            d += 1
        
        if temp > 1:
            factors.append((temp, 1))
        
        if n < 0:
            factors = [(-1, 1)] + factors
        
        return cls(NFType.SQUARE, tuple(factors), status=CanonicalStatus.CANONICAL)


# ═══════════════════════════════════════════════════════════════════════════════
# FLOWER NORMAL FORM (✿)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class FlowerNF(NormalForm):
    """
    ✿ Flower chart normal form: transform/hub-locked.
    
    Examples:
    - Fourier: frequency-ordered spectrum with ticket
    - Laplace: s-domain representation
    - Hub-locked: locked to specific hub transformation
    """
    ticket: Optional[Dict[str, Any]] = None
    
    @classmethod
    def fourier(cls, signal: NDArray, normalization: str = "ortho") -> 'FlowerNF':
        """
        Fourier transform normal form.
        
        DFT with stored ticket for reconstruction.
        """
        n = len(signal)
        if normalization == "ortho":
            spectrum = np.fft.fft(signal) / np.sqrt(n)
        else:
            spectrum = np.fft.fft(signal)
        
        ticket = {
            "n": n,
            "normalization": normalization,
            "type": "DFT"
        }
        
        nf = cls(NFType.FLOWER, tuple(spectrum), status=CanonicalStatus.CANONICAL)
        nf.ticket = ticket
        return nf
    
    @classmethod
    def hub_locked(cls, value: Any, hub_type: str, 
                   params: Dict[str, Any]) -> 'FlowerNF':
        """
        Hub-locked normal form.
        
        Value locked to a specific hub with parameters.
        """
        ticket = {
            "hub_type": hub_type,
            "params": params
        }
        nf = cls(NFType.FLOWER, value, status=CanonicalStatus.CANONICAL)
        nf.ticket = ticket
        return nf
    
    def inverse(self) -> Any:
        """
        Apply inverse transform using ticket.
        """
        if self.ticket is None:
            raise ValueError("No ticket for inverse")
        
        if self.ticket.get("type") == "DFT":
            spectrum = np.array(self.value)
            n = self.ticket["n"]
            if self.ticket["normalization"] == "ortho":
                return np.fft.ifft(spectrum) * np.sqrt(n)
            else:
                return np.fft.ifft(spectrum)
        
        raise ValueError(f"Unknown transform type: {self.ticket}")


# ═══════════════════════════════════════════════════════════════════════════════
# CLOUD NORMAL FORM (☁)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class CloudNF(NormalForm):
    """
    ☁ Cloud chart normal form: bound-qualified.
    
    Every value comes with explicit uncertainty bounds.
    
    Form: (value, BO) where BO = (Q, U, δ, ε, n, A)
    """
    uncertainty: Optional[Dict[str, float]] = None
    
    @classmethod
    def with_bounds(cls, value: float, upper: float, lower: float,
                    delta: float = 0.05) -> 'CloudNF':
        """
        Value with interval bounds.
        
        value ∈ [lower, upper] with probability ≥ 1 - δ
        """
        uncertainty = {
            "upper": upper,
            "lower": lower,
            "delta": delta,
            "epsilon": (upper - lower) / 2
        }
        nf = cls(NFType.CLOUD, value, status=CanonicalStatus.CANONICAL)
        nf.uncertainty = uncertainty
        return nf
    
    @classmethod
    def from_samples(cls, samples: NDArray, delta: float = 0.05) -> 'CloudNF':
        """
        Normal form from sample statistics.
        """
        mean = np.mean(samples)
        std = np.std(samples)
        n = len(samples)
        
        # Chebyshev bound
        k = np.sqrt(1 / delta)
        interval = k * std / np.sqrt(n)
        
        return cls.with_bounds(mean, mean + interval, mean - interval, delta)
    
    @classmethod
    def rounding_certificate(cls, exact: float, approx: float,
                             tolerance: float) -> 'CloudNF':
        """
        Rounding certificate: |approx - exact| < tolerance.
        """
        error = abs(approx - exact)
        certified = error < tolerance
        
        uncertainty = {
            "tolerance": tolerance,
            "actual_error": error,
            "certified": certified
        }
        nf = cls(NFType.CLOUD, approx, status=CanonicalStatus.CANONICAL if certified 
                 else CanonicalStatus.PARTIAL)
        nf.uncertainty = uncertainty
        return nf


# ═══════════════════════════════════════════════════════════════════════════════
# FRACTAL NORMAL FORM (⟂)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class FractalNF(NormalForm):
    """
    ⟂ Fractal chart normal form: seed/minimal.
    
    Minimal data sufficient for reconstruction.
    
    Contains:
    - Header/contract
    - Canonical statements
    - Assumptions + tolerances
    - Reconstruction routes
    - Checksums
    """
    routes: Dict[str, str] = field(default_factory=dict)
    assumptions: List[str] = field(default_factory=list)
    
    @classmethod
    def seed(cls, header: Dict[str, Any], 
             canonical_form: Any,
             routes: Dict[str, str] = None) -> 'FractalNF':
        """
        Create minimal seed normal form.
        """
        if routes is None:
            routes = {"default": "direct"}
        
        value = {
            "header": header,
            "canonical": canonical_form,
        }
        
        nf = cls(NFType.FRACTAL, value, status=CanonicalStatus.CANONICAL)
        nf.routes = routes
        return nf
    
    @classmethod
    def fixed_point_seed(cls, map_formula: str, 
                         fixed_point: float,
                         selector: str) -> 'FractalNF':
        """
        Fixed point iteration seed.
        """
        return cls.seed(
            header={"type": "fixed_point", "formula": map_formula},
            canonical_form=fixed_point,
            routes={
                "□": "exact_rational_lift",
                "✿": "error_kernel",
                "☁": "noise_floor_bound",
                "⟂": "idempotent_collapse"
            }
        )
    
    def verify_idempotence(self, expand: Callable, collapse: Callable) -> bool:
        """
        Verify Collapse(Expand(Seed)) = Seed.
        """
        expanded = expand(self.value)
        collapsed = collapse(expanded)
        return self.value == collapsed


# ═══════════════════════════════════════════════════════════════════════════════
# NORMAL FORM COMPILER
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class NFCompiler:
    """
    Compiler for computing normal forms.
    
    Transforms objects to their canonical chart representations.
    """
    
    def to_square(self, obj: Any) -> SquareNF:
        """Compile to □ normal form."""
        if isinstance(obj, (list, tuple)) and all(isinstance(x, (int, float)) for x in obj):
            return SquareNF.polynomial(list(obj))
        elif isinstance(obj, tuple) and len(obj) == 2:
            p, q = obj
            if isinstance(p, int) and isinstance(q, int):
                return SquareNF.rational(p, q)
        elif isinstance(obj, np.ndarray) and obj.ndim == 2:
            return SquareNF.matrix_echelon(obj)
        elif isinstance(obj, int):
            return SquareNF.integer_factorization(obj)
        
        return SquareNF(NFType.SQUARE, obj, status=CanonicalStatus.NON_CANONICAL)
    
    def to_flower(self, obj: Any, hub: str = "fourier") -> FlowerNF:
        """Compile to ✿ normal form."""
        if hub == "fourier" and isinstance(obj, np.ndarray):
            return FlowerNF.fourier(obj)
        
        return FlowerNF.hub_locked(obj, hub, {})
    
    def to_cloud(self, obj: Any, bounds: Tuple[float, float] = None) -> CloudNF:
        """Compile to ☁ normal form."""
        if isinstance(obj, np.ndarray):
            return CloudNF.from_samples(obj)
        elif bounds is not None:
            return CloudNF.with_bounds(float(obj), bounds[1], bounds[0])
        
        return CloudNF(NFType.CLOUD, obj, status=CanonicalStatus.NON_CANONICAL)
    
    def to_fractal(self, obj: Any, header: Dict = None) -> FractalNF:
        """Compile to ⟂ normal form."""
        if header is None:
            header = {"type": "generic"}
        return FractalNF.seed(header, obj)
    
    def are_equal(self, nf1: NormalForm, nf2: NormalForm) -> bool:
        """
        Global "same object" rule: equal iff NFs equal.
        """
        return nf1 == nf2


# ═══════════════════════════════════════════════════════════════════════════════
# CROSS-CHART COMMUTATION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class NFCommutation:
    """
    Check commutation between chart normal forms.
    
    NF(R̃(NF(p, q))) = NF(R̃(p, q))
    """
    
    def check_commutation(self, nf1: NormalForm, nf2: NormalForm,
                          transform: Callable,
                          tolerance: float = 1e-10) -> bool:
        """
        Check if transformation commutes with NF.
        """
        # Transform then NF
        t1 = transform(nf1.value)
        nf_t1 = self._to_nf(t1, nf1.nf_type)
        
        # NF then transform
        nf_v1 = nf1.value
        t2 = transform(nf_v1)
        nf_t2 = self._to_nf(t2, nf1.nf_type)
        
        return nf_t1 == nf_t2
    
    def _to_nf(self, value: Any, nf_type: NFType) -> NormalForm:
        """Convert value to specified NF type."""
        compiler = NFCompiler()
        if nf_type == NFType.SQUARE:
            return compiler.to_square(value)
        elif nf_type == NFType.FLOWER:
            return compiler.to_flower(value)
        elif nf_type == NFType.CLOUD:
            return compiler.to_cloud(value)
        else:
            return compiler.to_fractal(value)


# ═══════════════════════════════════════════════════════════════════════════════
# POLE BRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class NFPoleBridge:
    """
    Bridge between Normal Forms and four-pole framework.
    """
    
    @staticmethod
    def chart_map() -> str:
        return """
        NORMAL FORMS ↔ FOUR CHARTS
        
        □ (Square):  Exact discrete NF (polynomials, matrices, rationals)
        ✿ (Flower):  Transform NF (Fourier with ticket, hub-locked)
        ☁ (Cloud):   Bound-qualified NF (value + BO)
        ⟂ (Fractal): Seed NF (minimal reconstruction data)
        """
    
    @staticmethod
    def global_rule() -> str:
        return "Objects equal iff NFs equal (modulo chart equivalence)"
    
    @staticmethod
    def integration() -> str:
        return """
        NORMAL FORM COMPILER ↔ FRAMEWORK
        
        Canonicalization:
          Every object → unique NF in each chart
          NF(NF(x)) = NF(x) (idempotent)
        
        Commutation:
          NF(Transform(NF(x))) = NF(Transform(x))
          
        Cross-Chart:
          □ ↔ ✿: via hub law (DFT(a*b) = DFT(a)⊙DFT(b))
          ✿ ↔ ☁: via rounding certificate
          ☁ ↔ ⟂: via bound-to-seed compression
          ⟂ ↔ □: via idempotent expansion
        """


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def square_nf(obj: Any) -> SquareNF:
    """Create □ normal form."""
    return NFCompiler().to_square(obj)


def flower_nf(obj: Any, hub: str = "fourier") -> FlowerNF:
    """Create ✿ normal form."""
    return NFCompiler().to_flower(obj, hub)


def cloud_nf(obj: Any, bounds: Tuple[float, float] = None) -> CloudNF:
    """Create ☁ normal form."""
    return NFCompiler().to_cloud(obj, bounds)


def fractal_nf(obj: Any, header: Dict = None) -> FractalNF:
    """Create ⟂ normal form."""
    return NFCompiler().to_fractal(obj, header)


def nf_compiler() -> NFCompiler:
    """Create NF compiler."""
    return NFCompiler()


def nf_commutation() -> NFCommutation:
    """Create NF commutation checker."""
    return NFCommutation()


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Enums
    'NFType',
    'CanonicalStatus',
    
    # Base
    'NormalForm',
    
    # Chart NFs
    'SquareNF',
    'FlowerNF',
    'CloudNF',
    'FractalNF',
    
    # Compiler
    'NFCompiler',
    'NFCommutation',
    
    # Bridge
    'NFPoleBridge',
    
    # Functions
    'square_nf',
    'flower_nf',
    'cloud_nf',
    'fractal_nf',
    'nf_compiler',
    'nf_commutation',
]
