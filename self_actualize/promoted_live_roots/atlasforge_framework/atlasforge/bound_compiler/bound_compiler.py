"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        BOUND OBJECT COMPILER MODULE                          ║
║                                                                              ║
║  Canonical Bound Objects (BO) and Calibration System                         ║
║                                                                              ║
║  Core Schema:                                                                ║
║    BO = (Q, U, δ, ε, n, A)                                                  ║
║                                                                              ║
║  Where:                                                                      ║
║    Q = Quantity being bounded                                               ║
║    U = Upper bound value                                                     ║
║    δ = Probability parameter (1 - confidence)                               ║
║    ε = Approximation tolerance                                               ║
║    n = Sample size / iteration count                                         ║
║    A = Assumptions (tail class, moments, etc.)                              ║
║                                                                              ║
║  Inequality Families:                                                        ║
║    - Chebyshev (variance-based)                                             ║
║    - Hoeffding (bounded support)                                            ║
║    - Chernoff (subgaussian)                                                 ║
║    - Bernstein (subexponential)                                             ║
║    - Berry-Esseen (CLT approximation)                                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Any, Callable
from enum import Enum
import numpy as np
from numpy.typing import NDArray


# ═══════════════════════════════════════════════════════════════════════════════
# TAIL CLASSES AND ASSUMPTIONS
# ═══════════════════════════════════════════════════════════════════════════════

class TailClass(Enum):
    """Classification of distribution tail behavior."""
    BOUNDED = "bounded"           # [a, b] support
    SUBGAUSSIAN = "subgaussian"   # ψ₂ norm finite
    SUBEXPONENTIAL = "subexp"     # ψ₁ norm finite
    POLYNOMIAL = "polynomial"      # Finite moments up to some p
    HEAVY = "heavy"               # Only finite low moments


@dataclass
class Assumptions:
    """
    Assumptions A for a bound object.
    
    Specifies what properties of the distribution are known/assumed.
    """
    tail_class: TailClass
    
    # Moment assumptions
    variance_known: bool = False
    variance: Optional[float] = None
    higher_moments: Dict[int, float] = field(default_factory=dict)
    
    # Support assumptions
    bounded: bool = False
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None
    
    # Subgaussian/subexponential parameters
    psi_2_norm: Optional[float] = None  # Subgaussian
    psi_1_norm: Optional[float] = None  # Subexponential
    
    # Independence
    iid: bool = True
    
    def is_satisfied_by(self, other: 'Assumptions') -> bool:
        """Check if other assumptions imply these."""
        # Bounded implies subgaussian
        if self.tail_class == TailClass.SUBGAUSSIAN:
            if other.tail_class == TailClass.BOUNDED:
                return True
        # Subgaussian implies subexponential
        if self.tail_class == TailClass.SUBEXPONENTIAL:
            if other.tail_class in [TailClass.BOUNDED, TailClass.SUBGAUSSIAN]:
                return True
        return other.tail_class == self.tail_class


# ═══════════════════════════════════════════════════════════════════════════════
# BOUND OBJECT (BO)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class BoundObject:
    """
    Canonical Bound Object.
    
    BO = (Q, U, δ, ε, n, A)
    
    Represents: P(Q ≤ U) ≥ 1 - δ under assumptions A
    """
    quantity: str           # Q: what is being bounded
    upper_bound: float      # U: the bound value
    delta: float           # δ: failure probability
    epsilon: float = 0.0   # ε: approximation error
    n: int = 1             # n: sample size
    assumptions: Assumptions = field(default_factory=lambda: Assumptions(TailClass.BOUNDED))
    
    # Metadata
    name: str = ""
    derivation: str = ""
    
    @property
    def confidence(self) -> float:
        """1 - δ confidence level."""
        return 1.0 - self.delta
    
    def is_tighter_than(self, other: 'BoundObject') -> bool:
        """
        Check if this bound dominates (is tighter than) another.
        
        B₁ ≺ B₂ iff U₁ ≤ U₂ at same δ with weaker assumptions.
        """
        if self.delta != other.delta:
            return False
        if not other.assumptions.is_satisfied_by(self.assumptions):
            return False
        return self.upper_bound <= other.upper_bound
    
    def scale(self, factor: float) -> 'BoundObject':
        """Scale the bound by a factor."""
        return BoundObject(
            self.quantity,
            self.upper_bound * factor,
            self.delta,
            self.epsilon * factor,
            self.n,
            self.assumptions,
            self.name,
            self.derivation
        )


# ═══════════════════════════════════════════════════════════════════════════════
# INEQUALITY COMPILERS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ChebyshevBound:
    """
    Chebyshev inequality: P(|X - μ| ≥ kσ) ≤ 1/k²
    
    Only requires finite variance.
    """
    variance: float
    
    def compile(self, k: float) -> BoundObject:
        """
        Compile Chebyshev bound.
        
        U = kσ with δ = 1/k²
        """
        sigma = np.sqrt(self.variance)
        delta = 1.0 / (k ** 2)
        return BoundObject(
            quantity="|X - μ|",
            upper_bound=k * sigma,
            delta=delta,
            assumptions=Assumptions(TailClass.POLYNOMIAL, variance_known=True, variance=self.variance),
            name="Chebyshev",
            derivation=f"P(|X - μ| ≥ {k}σ) ≤ 1/{k}² = {delta:.4f}"
        )
    
    def for_sum(self, n: int, target_delta: float) -> BoundObject:
        """
        Chebyshev for sum of n iid variables.
        
        P(|S̄ₙ - μ| ≥ t) ≤ σ²/(nt²)
        """
        # Solve: σ²/(nt²) = δ → t = σ/√(nδ)
        sigma = np.sqrt(self.variance)
        t = sigma / np.sqrt(n * target_delta)
        return BoundObject(
            quantity="|S̄ₙ - μ|",
            upper_bound=t,
            delta=target_delta,
            n=n,
            assumptions=Assumptions(TailClass.POLYNOMIAL, variance_known=True, variance=self.variance, iid=True),
            name="Chebyshev (sum)",
            derivation=f"P(|S̄ₙ - μ| ≥ {t:.4f}) ≤ σ²/(n·t²) = {target_delta:.4f}"
        )


@dataclass
class HoeffdingBound:
    """
    Hoeffding inequality for bounded random variables.
    
    If Xᵢ ∈ [aᵢ, bᵢ], then:
    P(Sₙ - E[Sₙ] ≥ t) ≤ exp(-2t² / Σ(bᵢ-aᵢ)²)
    """
    lower: float  # a
    upper: float  # b
    
    @property
    def range(self) -> float:
        """b - a"""
        return self.upper - self.lower
    
    def compile(self, n: int, target_delta: float) -> BoundObject:
        """
        Compile Hoeffding bound for n iid bounded variables.
        
        P(|S̄ₙ - μ| ≥ t) ≤ 2exp(-2nt²/(b-a)²)
        """
        # Solve: 2exp(-2nt²/r²) = δ → t = r√(ln(2/δ)/(2n))
        r = self.range
        t = r * np.sqrt(np.log(2.0 / target_delta) / (2 * n))
        return BoundObject(
            quantity="|S̄ₙ - μ|",
            upper_bound=t,
            delta=target_delta,
            n=n,
            assumptions=Assumptions(
                TailClass.BOUNDED,
                bounded=True,
                lower_bound=self.lower,
                upper_bound=self.upper,
                iid=True
            ),
            name="Hoeffding",
            derivation=f"P(|S̄ₙ - μ| ≥ {t:.4f}) ≤ 2exp(-2n·t²/(b-a)²) = {target_delta:.4f}"
        )


@dataclass
class ChernoffBound:
    """
    Chernoff/subgaussian bound.
    
    For σ-subgaussian X:
    P(X ≥ t) ≤ exp(-t²/(2σ²))
    """
    sigma_sg: float  # Subgaussian parameter
    
    def compile(self, n: int, target_delta: float) -> BoundObject:
        """
        Compile Chernoff bound for sum of n iid subgaussian.
        
        P(|S̄ₙ - μ| ≥ t) ≤ 2exp(-nt²/(2σ²))
        """
        # Solve: 2exp(-nt²/(2σ²)) = δ → t = σ√(2ln(2/δ)/n)
        t = self.sigma_sg * np.sqrt(2 * np.log(2.0 / target_delta) / n)
        return BoundObject(
            quantity="|S̄ₙ - μ|",
            upper_bound=t,
            delta=target_delta,
            n=n,
            assumptions=Assumptions(
                TailClass.SUBGAUSSIAN,
                psi_2_norm=self.sigma_sg,
                iid=True
            ),
            name="Chernoff/Subgaussian",
            derivation=f"P(|S̄ₙ - μ| ≥ {t:.4f}) ≤ 2exp(-n·t²/(2σ²_sg)) = {target_delta:.4f}"
        )


@dataclass 
class BernsteinBound:
    """
    Bernstein inequality for subexponential variables.
    
    Combines variance term and tail term.
    """
    variance: float
    b: float  # Subexponential parameter
    
    def compile(self, n: int, target_delta: float) -> BoundObject:
        """
        Compile Bernstein bound.
        
        P(|S̄ₙ - μ| ≥ t) ≤ 2exp(-n·min(t²/(2σ²), t/(2b)))
        """
        # Two regimes: t small → Gaussian, t large → exponential
        # Solve for crossover: t²/(2σ²) = t/(2b) → t* = σ²/b
        
        # Use simpler bound: t = √(2σ²ln(2/δ)/n) + 2b·ln(2/δ)/n
        log_term = np.log(2.0 / target_delta)
        t = np.sqrt(2 * self.variance * log_term / n) + 2 * self.b * log_term / n
        
        return BoundObject(
            quantity="|S̄ₙ - μ|",
            upper_bound=t,
            delta=target_delta,
            n=n,
            assumptions=Assumptions(
                TailClass.SUBEXPONENTIAL,
                variance_known=True,
                variance=self.variance,
                psi_1_norm=self.b,
                iid=True
            ),
            name="Bernstein",
            derivation=f"P(|S̄ₙ - μ| ≥ {t:.4f}) ≤ {target_delta:.4f}"
        )


@dataclass
class BerryEsseenBound:
    """
    Berry-Esseen CLT approximation bound.
    
    |P(Sₙ/√n ≤ x) - Φ(x)| ≤ C·ρ/(σ³√n)
    
    where ρ = E[|X-μ|³] is the third absolute moment.
    """
    variance: float
    third_moment: float
    C: float = 0.4748  # Best known constant
    
    @property
    def drift(self) -> float:
        """Berry-Esseen drift bound."""
        sigma = np.sqrt(self.variance)
        return self.C * self.third_moment / (sigma ** 3)
    
    def compile(self, n: int, target_alpha: float) -> BoundObject:
        """
        Compile CLT-based bound with Berry-Esseen correction.
        
        Returns bound with explicit approximation error.
        """
        from scipy import stats
        
        sigma = np.sqrt(self.variance)
        z = stats.norm.ppf(1 - target_alpha / 2)
        
        # CLT gives: P(|S̄ₙ - μ| ≥ z·σ/√n) ≈ α
        # Berry-Esseen adds drift
        drift = self.drift / np.sqrt(n)
        
        t = z * sigma / np.sqrt(n)
        
        return BoundObject(
            quantity="|S̄ₙ - μ|",
            upper_bound=t,
            delta=target_alpha,
            epsilon=drift,
            n=n,
            assumptions=Assumptions(
                TailClass.POLYNOMIAL,
                variance_known=True,
                variance=self.variance,
                higher_moments={3: self.third_moment},
                iid=True
            ),
            name="CLT + Berry-Esseen",
            derivation=f"CLT: z_{1-α/2}·σ/√n = {t:.4f}, BE drift = {drift:.6f}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# TOP-K BOUND SELECTION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class TopKBounds:
    """
    Maintain top-k bounds until assumptions are certified.
    
    Follows the principle: "singleton output forbidden if assumptions not certified."
    """
    bounds: List[BoundObject] = field(default_factory=list)
    k: int = 3
    certified: Dict[str, bool] = field(default_factory=dict)
    
    def add_bound(self, bo: BoundObject):
        """Add a bound to the collection."""
        self.bounds.append(bo)
        self.certified[bo.name] = False
    
    def certify(self, name: str):
        """Mark a bound's assumptions as certified."""
        self.certified[name] = True
    
    @property
    def certified_bounds(self) -> List[BoundObject]:
        """Return only certified bounds."""
        return [b for b in self.bounds if self.certified.get(b.name, False)]
    
    @property
    def tightest_certified(self) -> Optional[BoundObject]:
        """Return tightest certified bound, or None if no certifications."""
        certified = self.certified_bounds
        if not certified:
            return None
        return min(certified, key=lambda b: b.upper_bound)
    
    def select(self) -> Tuple[Optional[BoundObject], bool]:
        """
        Select output bound.
        
        Returns (bound, is_singleton).
        If no certified bounds, returns (None, False).
        """
        tightest = self.tightest_certified
        if tightest is not None:
            return tightest, True
        # Return top-k as candidates
        return None, False
    
    def dominance_analysis(self) -> List[Tuple[str, str, str]]:
        """
        Analyze dominance relations between bounds.
        
        Returns list of (B1, relation, B2).
        """
        results = []
        for i, b1 in enumerate(self.bounds):
            for b2 in self.bounds[i+1:]:
                if b1.is_tighter_than(b2):
                    results.append((b1.name, "≺", b2.name))
                elif b2.is_tighter_than(b1):
                    results.append((b2.name, "≺", b1.name))
                else:
                    results.append((b1.name, "≁", b2.name))
        return results


# ═══════════════════════════════════════════════════════════════════════════════
# BOUND COMPILER
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class BoundCompiler:
    """
    Compile bounds from different inequality families.
    
    Automatically selects applicable bounds based on known assumptions.
    """
    
    def compile_mean_estimation(self, 
                                 n: int,
                                 target_delta: float,
                                 known: Assumptions) -> TopKBounds:
        """
        Compile all applicable bounds for mean estimation.
        
        Returns top-k bounds until assumptions certified.
        """
        topk = TopKBounds(k=5)
        
        # Chebyshev (only needs variance)
        if known.variance_known and known.variance is not None:
            cheb = ChebyshevBound(known.variance)
            topk.add_bound(cheb.for_sum(n, target_delta))
        
        # Hoeffding (needs bounded support)
        if known.bounded and known.lower_bound is not None and known.upper_bound is not None:
            hoeff = HoeffdingBound(known.lower_bound, known.upper_bound)
            topk.add_bound(hoeff.compile(n, target_delta))
        
        # Chernoff (needs subgaussian)
        if known.psi_2_norm is not None:
            chern = ChernoffBound(known.psi_2_norm)
            topk.add_bound(chern.compile(n, target_delta))
        elif known.bounded and known.lower_bound is not None and known.upper_bound is not None:
            # Bounded implies subgaussian with σ_sg = (b-a)/2
            sigma_sg = (known.upper_bound - known.lower_bound) / 2
            chern = ChernoffBound(sigma_sg)
            topk.add_bound(chern.compile(n, target_delta))
        
        # Bernstein (needs variance + subexponential parameter)
        if known.variance_known and known.psi_1_norm is not None:
            bern = BernsteinBound(known.variance, known.psi_1_norm)
            topk.add_bound(bern.compile(n, target_delta))
        
        # Berry-Esseen (needs third moment)
        if known.variance_known and 3 in known.higher_moments:
            be = BerryEsseenBound(known.variance, known.higher_moments[3])
            topk.add_bound(be.compile(n, target_delta))
        
        return topk
    
    def compare_bounds(self, bounds: List[BoundObject]) -> str:
        """Generate comparison report."""
        if not bounds:
            return "No bounds to compare."
        
        lines = ["Bound Comparison:"]
        lines.append("=" * 60)
        
        for bo in sorted(bounds, key=lambda b: b.upper_bound):
            lines.append(f"  {bo.name}:")
            lines.append(f"    U = {bo.upper_bound:.6f}")
            lines.append(f"    δ = {bo.delta:.6f}")
            lines.append(f"    Assumes: {bo.assumptions.tail_class.value}")
        
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# DOMINANCE PROOFS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class DominanceProof:
    """
    Prove dominance relation between bounds.
    """
    bound1: BoundObject
    bound2: BoundObject
    
    def prove(self) -> Tuple[str, str]:
        """
        Attempt to prove B1 ≺ B2 or B2 ≺ B1.
        
        Returns (relation, proof).
        """
        if self.bound1.delta != self.bound2.delta:
            return "incomparable", "Different δ values"
        
        # Check assumption compatibility
        a1_implies_a2 = self.bound2.assumptions.is_satisfied_by(self.bound1.assumptions)
        a2_implies_a1 = self.bound1.assumptions.is_satisfied_by(self.bound2.assumptions)
        
        if not a1_implies_a2 and not a2_implies_a1:
            return "incomparable", "Incompatible assumptions"
        
        u1, u2 = self.bound1.upper_bound, self.bound2.upper_bound
        
        if a1_implies_a2 and u1 <= u2:
            proof = f"{self.bound1.name} ≺ {self.bound2.name}: U₁={u1:.4f} ≤ U₂={u2:.4f} with weaker assumptions"
            return "≺", proof
        elif a2_implies_a1 and u2 <= u1:
            proof = f"{self.bound2.name} ≺ {self.bound1.name}: U₂={u2:.4f} ≤ U₁={u1:.4f} with weaker assumptions"
            return "≻", proof
        else:
            return "incomparable", "No clear dominance"


# ═══════════════════════════════════════════════════════════════════════════════
# POLE BRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class BoundObjectPoleBridge:
    """
    Bridge between Bound Objects and four-pole framework.
    """
    
    @staticmethod
    def cloud_chart() -> str:
        """BO lives primarily in ☁ (Cloud) chart."""
        return "BO = (Q, U, δ, ε, n, A) ↔ ☁ chart: uncertainty/calibration"
    
    @staticmethod
    def sigma_pole() -> str:
        """Connection to Σ-pole."""
        return "Σ-pole ↔ Stochastic bounds, probabilistic certificates"
    
    @staticmethod
    def d_pole() -> str:
        """Connection to D-pole."""
        return "D-pole ↔ Discrete assumptions, certified conditions"
    
    @staticmethod
    def integration() -> str:
        return """
        BOUND OBJECTS ↔ FRAMEWORK
        
        ☁ Cloud Chart: BO as first-class uncertainty objects
        Σ-pole: Stochastic/probabilistic bounds
        D-pole: Certified assumptions, discrete conditions
        
        Top-k until stable: "singleton output forbidden if assumptions not certified"
        
        Dominance: B₁ ≺ B₂ iff U₁ ≤ U₂ under weaker assumptions
        """


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def bound_object(quantity: str, upper: float, delta: float, **kwargs) -> BoundObject:
    """Create bound object."""
    return BoundObject(quantity, upper, delta, **kwargs)


def chebyshev_bound(variance: float) -> ChebyshevBound:
    """Create Chebyshev bound compiler."""
    return ChebyshevBound(variance)


def hoeffding_bound(lower: float, upper: float) -> HoeffdingBound:
    """Create Hoeffding bound compiler."""
    return HoeffdingBound(lower, upper)


def chernoff_bound(sigma_sg: float) -> ChernoffBound:
    """Create Chernoff/subgaussian bound compiler."""
    return ChernoffBound(sigma_sg)


def bernstein_bound(variance: float, b: float) -> BernsteinBound:
    """Create Bernstein bound compiler."""
    return BernsteinBound(variance, b)


def bound_compiler() -> BoundCompiler:
    """Create bound compiler."""
    return BoundCompiler()


def topk_bounds(k: int = 3) -> TopKBounds:
    """Create top-k bounds container."""
    return TopKBounds(k=k)


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Enums
    'TailClass',
    
    # Assumptions
    'Assumptions',
    
    # Bound Object
    'BoundObject',
    
    # Compilers
    'ChebyshevBound',
    'HoeffdingBound',
    'ChernoffBound',
    'BernsteinBound',
    'BerryEsseenBound',
    
    # Selection
    'TopKBounds',
    'BoundCompiler',
    
    # Proofs
    'DominanceProof',
    
    # Bridge
    'BoundObjectPoleBridge',
    
    # Functions
    'bound_object',
    'chebyshev_bound',
    'hoeffding_bound',
    'chernoff_bound',
    'bernstein_bound',
    'bound_compiler',
    'topk_bounds',
]
