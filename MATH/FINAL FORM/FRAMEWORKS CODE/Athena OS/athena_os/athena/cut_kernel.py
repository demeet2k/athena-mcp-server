"""
ATHENA OS - CUT KERNEL
======================
Computational Universe Toolkit - The Universe Compiler

From CUT_-_TOME__Computational_Universe_Toolkit_.docx:

CUT CENTRAL CLAIM:
    Stable structure across domains is produced by a single algorithmic pattern:
    (PackSpec, Data) → (CUTLedger, TypedOutcome)

HYBRID STATE:
    X(t) = (κ(t), ℓ(t), b(t), Θ(t))
    - κ: conserved content (density/measure/graph mass)
    - ℓ ∈ {0,...,L}: regime ladder index
    - b ∈ {0,1}⁸: 8-bit mode register
    - Θ: auxiliary coordinates (domain-specific)

UNIVERSAL QUADRATIC KERNEL:
    K(p,q; κ_sc) = (p-2)(q-2) - κ_sc = 0
    
κ-LADDER (Universal Discrete Ruler):
    log₂ X = log₂ X₀ + σ·Δn/6 + Σₖ Δₖ log₂ Hₖ + ∫β(τ)d ln τ
    - Δn ∈ ℤ: rung count (base stride 1/6)
    - σ ∈ {+1,-1}: dial orientation
    - Hₖ: exact prime scalars
    - Δₖ: prime exponents
    - β: bounded drift

DISCRETE EVENT PRIMES:
    Primes encode discrete DOF/topology changes:
    - DOF removal/lock
    - Coherent coupling
    - Boundary creation
    - Regime migration

β-FLOW:
    Continuous, bounded evolution within a rung:
    - ≤1% relative drift per segment (default)
    - No prime change within segments

CORRIDOR ADMISSIBILITY:
    Typed truth: OK / NEAR / AMBIG / FAIL
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable
from enum import Enum, auto
import numpy as np
import math
import hashlib
from .crystal_structure import TypedTruth, OutcomeBundle


# =============================================================================
# MODE REGISTER
# =============================================================================

@dataclass
class ModeRegister:
    """
    8-bit mode register b(t) ∈ {0,1}⁸.
    
    Selects semantic DOF families (global semantics, cross-pack invariant).
    """
    bits: int = 0  # 8-bit value (0-255)
    
    def __post_init__(self):
        self.bits = self.bits & 0xFF  # Ensure 8-bit
    
    def get_bit(self, index: int) -> bool:
        """Get bit at index (0-7)."""
        if not 0 <= index < 8:
            raise ValueError("Bit index must be 0-7")
        return bool((self.bits >> index) & 1)
    
    def set_bit(self, index: int, value: bool) -> 'ModeRegister':
        """Set bit at index."""
        if not 0 <= index < 8:
            raise ValueError("Bit index must be 0-7")
        if value:
            new_bits = self.bits | (1 << index)
        else:
            new_bits = self.bits & ~(1 << index)
        return ModeRegister(new_bits)
    
    def to_binary(self) -> str:
        """Get binary representation."""
        return format(self.bits, '08b')
    
    @classmethod
    def from_binary(cls, binary: str) -> 'ModeRegister':
        """Create from binary string."""
        return cls(int(binary, 2))


# =============================================================================
# KAPPA CONTENT
# =============================================================================

@dataclass
class KappaContent:
    """
    Conserved content κ(t) on a carrier Ω.
    
    Properties:
    - Density/measure/graph mass
    - Positivity invariant
    - Accounting invariant
    """
    value: float = 1.0
    carrier_id: str = "Ω"
    is_normalized: bool = True
    
    def __post_init__(self):
        if self.value < 0:
            raise ValueError("κ content must be non-negative")
    
    @property
    def kappa_scalar(self) -> float:
        """
        κ_sc: scalar binding extracted from κ.
        
        Used in kernel equation: K(p,q; κ_sc) = (p-2)(q-2) - κ_sc = 0
        """
        return self.value
    
    def scale(self, factor: float) -> 'KappaContent':
        """Scale κ by factor."""
        return KappaContent(self.value * factor, self.carrier_id, False)


# =============================================================================
# HYBRID STATE
# =============================================================================

@dataclass
class HybridState:
    """
    CUT Hybrid State: X(t) = (κ(t), ℓ(t), b(t), Θ(t))
    
    The complete state of a CUT system at time t.
    """
    kappa: KappaContent
    regime_index: int  # ℓ(t) ∈ {0,...,L}
    mode: ModeRegister
    theta: Dict[str, float] = field(default_factory=dict)  # Auxiliary coords
    time: float = 0.0
    
    def __post_init__(self):
        if self.regime_index < 0:
            raise ValueError("Regime index must be non-negative")
    
    @property
    def kappa_scalar(self) -> float:
        """Get κ_sc for kernel equation."""
        return self.kappa.kappa_scalar
    
    def with_regime(self, new_regime: int) -> 'HybridState':
        """Create new state with different regime."""
        return HybridState(
            self.kappa, new_regime, self.mode,
            self.theta.copy(), self.time
        )
    
    def with_theta(self, key: str, value: float) -> 'HybridState':
        """Create new state with updated theta."""
        new_theta = self.theta.copy()
        new_theta[key] = value
        return HybridState(
            self.kappa, self.regime_index, self.mode,
            new_theta, self.time
        )


# =============================================================================
# UNIVERSAL QUADRATIC KERNEL
# =============================================================================

class UniversalKernel:
    """
    Universal Quadratic Kernel (Normal Form).
    
    K(p,q; κ_sc) = (p-2)(q-2) - κ_sc = 0
    
    This is the canonical topology surface for CUT.
    """
    
    @staticmethod
    def evaluate(p: float, q: float, kappa_sc: float) -> float:
        """Evaluate kernel: K(p,q; κ_sc) = (p-2)(q-2) - κ_sc."""
        return (p - 2) * (q - 2) - kappa_sc
    
    @staticmethod
    def on_kernel(p: float, q: float, kappa_sc: float, tol: float = 1e-10) -> bool:
        """Check if (p,q) lies on the kernel surface."""
        return abs(UniversalKernel.evaluate(p, q, kappa_sc)) < tol
    
    @staticmethod
    def solve_p(q: float, kappa_sc: float) -> Optional[float]:
        """Solve for p given q and κ_sc."""
        if q == 2:
            return None  # Undefined
        return kappa_sc / (q - 2) + 2
    
    @staticmethod
    def solve_q(p: float, kappa_sc: float) -> Optional[float]:
        """Solve for q given p and κ_sc."""
        if p == 2:
            return None  # Undefined
        return kappa_sc / (p - 2) + 2
    
    @staticmethod
    def kappa_from_faces(p: float, q: float) -> float:
        """Compute κ_sc from face values (p,q)."""
        return (p - 2) * (q - 2)


# =============================================================================
# κ-LADDER (UNIVERSAL DISCRETE RULER)
# =============================================================================

@dataclass
class KappaLadder:
    """
    κ-Ladder: Universal Discrete Ruler in log space.
    
    log₂ X = log₂ X₀ + σ·Δn/6 + Σₖ Δₖ log₂ Hₖ + ∫β(τ)d ln τ
    
    Properties:
    - Base stride: 1/6 in log₂ space
    - Rung count Δn ∈ ℤ
    - Dial orientation σ ∈ {+1, -1}
    """
    
    x0: float = 1.0          # Reference value
    sigma: int = 1           # Dial orientation (+1 or -1)
    delta_n: int = 0         # Rung count
    prime_exponents: Dict[str, int] = field(default_factory=dict)  # Δₖ
    beta_integral: float = 0.0  # ∫β(τ)d ln τ
    
    BASE_STRIDE: float = 1.0 / 6.0  # 1/6 in log₂ space
    
    # Exact prime scalars (Pow2/Rat/ConstID encodings)
    PRIMES: Dict[str, float] = field(default_factory=lambda: {
        "H2": 2.0,               # 2^1
        "H3": 3.0,               # 3
        "H5": 5.0,               # 5
        "H_edge": 2**(1/50),     # Edge microquantum
        "H_phi": (1 + 5**0.5)/2, # Golden ratio
    })
    
    def __post_init__(self):
        if self.sigma not in {-1, +1}:
            raise ValueError("σ must be +1 or -1")
    
    @property
    def log2_value(self) -> float:
        """Compute log₂ X from ladder parameters."""
        result = np.log2(self.x0)
        result += self.sigma * self.delta_n * self.BASE_STRIDE
        
        for prime_id, delta_k in self.prime_exponents.items():
            if prime_id in self.PRIMES:
                result += delta_k * np.log2(self.PRIMES[prime_id])
        
        result += self.beta_integral
        return result
    
    @property
    def value(self) -> float:
        """Compute X from ladder parameters."""
        return 2 ** self.log2_value
    
    def step_rung(self, steps: int = 1) -> 'KappaLadder':
        """Move by steps on the ladder (Δn += steps)."""
        return KappaLadder(
            self.x0, self.sigma, self.delta_n + steps,
            self.prime_exponents.copy(), self.beta_integral
        )
    
    def apply_prime(self, prime_id: str, exponent: int = 1) -> 'KappaLadder':
        """Apply a prime with given exponent."""
        new_exponents = self.prime_exponents.copy()
        new_exponents[prime_id] = new_exponents.get(prime_id, 0) + exponent
        return KappaLadder(
            self.x0, self.sigma, self.delta_n,
            new_exponents, self.beta_integral
        )
    
    def add_drift(self, beta: float) -> 'KappaLadder':
        """Add continuous drift (β-flow contribution)."""
        return KappaLadder(
            self.x0, self.sigma, self.delta_n,
            self.prime_exponents.copy(), self.beta_integral + beta
        )
    
    def discretize(self, value: float) -> Tuple[int, float]:
        """
        Find nearest lattice point for a given value.
        
        Returns (Δn, residual).
        """
        log2_target = np.log2(value) - np.log2(self.x0)
        # Subtract prime contributions
        for prime_id, delta_k in self.prime_exponents.items():
            if prime_id in self.PRIMES:
                log2_target -= delta_k * np.log2(self.PRIMES[prime_id])
        log2_target -= self.beta_integral
        
        # Find nearest rung
        delta_n = round(log2_target / (self.sigma * self.BASE_STRIDE))
        residual = log2_target - delta_n * self.sigma * self.BASE_STRIDE
        
        return (delta_n, residual)


# =============================================================================
# DISCRETE EVENT PRIMES
# =============================================================================

class PrimeKind(Enum):
    """Kind of discrete event prime."""
    LATTICE = auto()   # Lattice prime (Δₖ ∈ ℤ)
    EVENT = auto()     # Toggle-once event
    CORRIDOR = auto()  # Corridor constraint


class PrimeRepeatability(Enum):
    """Repeatability of a prime."""
    ONCE = auto()      # Toggle once only
    REPEATABLE = auto()  # Can repeat (microcounter)


@dataclass
class DiscreteEventPrime:
    """
    A Discrete Event Prime (DOF-change token).
    
    Primes encode discrete topology/DOF changes:
    - DOF removal/lock (constraint tying)
    - Coherent coupling (channel merge)
    - Boundary creation (accessible region truncation)
    - Micro-front events (repeatable micro-splits)
    - Regime migration (event boundary transitions)
    """
    
    prime_id: str
    kind: PrimeKind
    repeatability: PrimeRepeatability
    scope: str = "pack"  # pack/dial/zone/run
    exact_value: float = 1.0  # Pow2/Rat/ConstID encoding
    bounds: Tuple[int, int] = (-1, 1)  # For toggle-once primes
    detector: Optional[Callable[[HybridState], bool]] = None
    description: str = ""
    
    @property
    def log2_value(self) -> float:
        return np.log2(self.exact_value)
    
    def is_active(self, state: HybridState) -> bool:
        """Check if prime is activated for this state."""
        if self.detector:
            return self.detector(state)
        return False
    
    def apply(self, ladder: KappaLadder, exponent: int = 1) -> KappaLadder:
        """Apply prime to ladder."""
        if self.repeatability == PrimeRepeatability.ONCE:
            if exponent not in range(self.bounds[0], self.bounds[1] + 1):
                raise ValueError(f"Exponent {exponent} out of bounds for toggle-once prime")
        return ladder.apply_prime(self.prime_id, exponent)


# =============================================================================
# β-FLOW
# =============================================================================

@dataclass
class BetaFlow:
    """
    β-Flow: Bounded continuous evolution within a rung.
    
    Properties:
    - Continuous, bounded
    - Does not alter discrete invariants
    - Default: ≤1% relative drift per segment
    """
    
    max_drift: float = 0.01  # 1% default
    current_integral: float = 0.0
    segment_start: float = 0.0
    
    def integrate(self, beta_func: Callable[[float], float],
                  t_start: float, t_end: float,
                  num_steps: int = 100) -> float:
        """
        Integrate β(τ) d ln τ from t_start to t_end.
        """
        dt = (t_end - t_start) / num_steps
        integral = 0.0
        t = t_start
        for _ in range(num_steps):
            if t > 0:
                integral += beta_func(t) * dt / t
            t += dt
        return integral
    
    def apply(self, ladder: KappaLadder, beta: float) -> Tuple[KappaLadder, bool]:
        """
        Apply drift to ladder.
        
        Returns (new_ladder, within_bounds).
        """
        new_integral = self.current_integral + beta
        within_bounds = abs(new_integral) <= self.max_drift
        
        new_ladder = ladder.add_drift(beta)
        return (new_ladder, within_bounds)
    
    def reset(self) -> 'BetaFlow':
        """Reset flow at segment boundary."""
        return BetaFlow(self.max_drift, 0.0, 0.0)


# =============================================================================
# CORRIDOR
# =============================================================================

@dataclass
class Corridor:
    """
    Corridor Admissibility Gate.
    
    Determines what is allowed; truth is typed OK/NEAR/AMBIG/FAIL.
    """
    
    name: str
    predicates: List[Callable[[HybridState], bool]] = field(default_factory=list)
    margin_threshold: float = 0.1  # Margin for NEAR
    
    def evaluate(self, state: HybridState) -> Tuple[TypedTruth, float]:
        """
        Evaluate corridor for state.
        
        Returns (truth, margin).
        """
        if not self.predicates:
            return (TypedTruth.OK, 1.0)
        
        passing = sum(1 for p in self.predicates if p(state))
        total = len(self.predicates)
        margin = passing / total
        
        if margin == 1.0:
            return (TypedTruth.OK, margin)
        elif margin >= 1.0 - self.margin_threshold:
            return (TypedTruth.NEAR, margin)
        elif margin >= 0.5:
            return (TypedTruth.AMBIG, margin)
        else:
            return (TypedTruth.FAIL, margin)


# =============================================================================
# CUT LEDGER
# =============================================================================

@dataclass
class CUTLedger:
    """
    CUT Ledger: The minimal publishable unit.
    
    Contains deterministic record of:
    - Dial inputs + provenance
    - Anchor selections + gauge discipline
    - Inferred integer lattice coordinates (Δ-counts)
    - Prime activations + evidence
    - β integrals + smear bounds
    - Corridor outcomes + margins
    - Declared primary metric
    - Replay plan + hash pins
    """
    
    ledger_id: str
    dial_inputs: Dict[str, Any] = field(default_factory=dict)
    anchor_selection: Optional[str] = None
    delta_counts: Dict[str, int] = field(default_factory=dict)
    prime_activations: List[str] = field(default_factory=list)
    beta_integral: float = 0.0
    corridor_outcome: TypedTruth = TypedTruth.OK
    margin: float = 1.0
    primary_metric: Optional[str] = None
    replay_hash: str = ""
    
    def __post_init__(self):
        if not self.replay_hash:
            self.replay_hash = self._compute_hash()
    
    def _compute_hash(self) -> str:
        """Compute deterministic hash for replay."""
        content = str(sorted(self.dial_inputs.items()))
        content += str(sorted(self.delta_counts.items()))
        content += str(self.prime_activations)
        content += str(self.beta_integral)
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    @property
    def is_valid(self) -> bool:
        """Check if ledger represents valid claim."""
        return self.corridor_outcome.is_success and self.primary_metric is not None


# =============================================================================
# PACK SPEC
# =============================================================================

@dataclass
class PackSpec:
    """
    PackSpec: Domain Compiler Contract.
    
    Every domain is defined by its PackSpec:
    (DialSpec, AnchorSpec, LatticeSpec, PrimeSpec, FlowSpec, 
     CorridorSpec, LedgerSpec, MetricSpec)
    """
    
    name: str
    dial_spec: Dict[str, type] = field(default_factory=dict)
    anchor_spec: Optional[str] = None
    lattice_spec: Optional[KappaLadder] = None
    prime_spec: List[DiscreteEventPrime] = field(default_factory=list)
    flow_spec: Optional[BetaFlow] = None
    corridor_spec: List[Corridor] = field(default_factory=list)
    metric_spec: List[str] = field(default_factory=list)
    
    def compile(self, data: Dict[str, Any]) -> Tuple[CUTLedger, TypedTruth]:
        """
        Compile data through pack.
        
        (PackSpec, Data) → (CUTLedger, TypedOutcome)
        """
        # Create initial state
        kappa = KappaContent(1.0)
        mode = ModeRegister(0)
        state = HybridState(kappa, 0, mode)
        
        # Evaluate corridors
        for corridor in self.corridor_spec:
            truth, margin = corridor.evaluate(state)
            if truth == TypedTruth.FAIL:
                return (CUTLedger(
                    f"ledger_{self.name}",
                    data, None, {}, [], 0.0,
                    truth, margin, None
                ), truth)
        
        # Build ledger
        ledger = CUTLedger(
            ledger_id=f"ledger_{self.name}",
            dial_inputs=data,
            anchor_selection=self.anchor_spec,
            corridor_outcome=TypedTruth.OK,
            margin=1.0,
            primary_metric=self.metric_spec[0] if self.metric_spec else None
        )
        
        return (ledger, TypedTruth.OK)


# =============================================================================
# VALIDATION
# =============================================================================

def validate_cut_kernel() -> bool:
    """Validate the CUT kernel module."""
    
    # Test ModeRegister
    mode = ModeRegister(0b10101010)
    assert mode.get_bit(1) == True
    assert mode.get_bit(0) == False
    assert mode.to_binary() == "10101010"
    
    # Test KappaContent
    kappa = KappaContent(4.0)
    assert kappa.kappa_scalar == 4.0
    
    # Test HybridState
    state = HybridState(kappa, 0, mode)
    assert state.kappa_scalar == 4.0
    
    # Test UniversalKernel
    # K(4,4; 4) = (4-2)(4-2) - 4 = 4 - 4 = 0
    assert UniversalKernel.on_kernel(4, 4, 4)
    assert not UniversalKernel.on_kernel(3, 3, 4)
    assert UniversalKernel.kappa_from_faces(4, 4) == 4
    
    # Test KappaLadder
    ladder = KappaLadder(x0=1.0, sigma=1, delta_n=0)
    assert abs(ladder.value - 1.0) < 1e-10
    
    ladder2 = ladder.step_rung(6)
    # After 6 rungs: 2^(6/6) = 2
    assert abs(ladder2.value - 2.0) < 1e-10
    
    # Test DiscreteEventPrime
    prime = DiscreteEventPrime(
        "H2", PrimeKind.LATTICE, PrimeRepeatability.REPEATABLE,
        exact_value=2.0
    )
    ladder3 = prime.apply(ladder, 1)
    assert abs(ladder3.value - 2.0) < 1e-10
    
    # Test BetaFlow
    flow = BetaFlow(max_drift=0.01)
    new_ladder, ok = flow.apply(ladder, 0.005)
    assert ok  # Within bounds
    
    # Test Corridor
    corridor = Corridor("test", [lambda s: True])
    truth, margin = corridor.evaluate(state)
    assert truth == TypedTruth.OK
    
    # Test PackSpec
    pack = PackSpec("test_pack", metric_spec=["accuracy"])
    ledger, outcome = pack.compile({"x": 42})
    assert outcome == TypedTruth.OK
    assert ledger.is_valid
    
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("ATHENA OS - CUT KERNEL")
    print("Computational Universe Toolkit")
    print("=" * 60)
    
    print("\nValidating module...")
    assert validate_cut_kernel()
    print("✓ Module validated")
    
    # Demo
    print("\n--- κ-LADDER DEMO ---")
    ladder = KappaLadder(x0=1.0, sigma=1, delta_n=0)
    print(f"Base: X = {ladder.value:.4f}")
    
    for i in range(1, 7):
        ladder = ladder.step_rung(1)
        print(f"Rung {i}: X = {ladder.value:.4f}")
    
    print("\n--- KERNEL SURFACE ---")
    for kappa in [1, 4, 9]:
        p = UniversalKernel.solve_p(4, kappa)
        print(f"κ_sc = {kappa}: (p={p:.2f}, q=4) on kernel")
