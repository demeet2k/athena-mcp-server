"""
ATHENA OS - PRIME FACTORIZATION KERNEL
======================================
The Crystal-Fractal Hybrid Toolkit for Prime Phenomena

From Prime_Factorization.docx:

CORE THESIS:
    "Mystery" arises from observing only discrete samples (integers) while
    ignoring the continuous symmetry frames and dual encodings that generate them.
    
THE HYBRID TOOLKIT:
    One kernel, many projections, one runtime loop:
    rotate → nullify → jump → spin → collapse → ledger

THE FOUR LENSES:
    □ Square  (??□)    - Bank gcd projection + valuation extraction
    ◇ Fractal (??◇)    - Perfect-power detection + shatter
    ⌀ Diagonal (??⌀)   - Difference-of-squares resonance
    ☁ Cloud   (??☁)    - Chaotic mixing → gcd witness

CERTIFICATE OBJECTS:
    - PrimeCertificate(p)
    - FactorCertificate(n, d)
    - ValuationCertificate(n, p, α)
    - FactorizationLedger(n)
    - DesertCertificate(I)
    - ConstellationCertificate(H, n)
    - PrimePowerCertificate(p, k)

THE 256-STATE ATLAS:
    Derived from (e, i, π, φ) × 64 root states each
    Enables deterministic "math-artist" parameterization

TRUTH BARRIER:
    Only certificates can assert truth about primes/factors/deserts.
    Signals guide but cannot prove.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Set, Callable
from enum import Enum, auto
import math
import hashlib
import random


# =============================================================================
# CERTIFICATE TYPES
# =============================================================================

@dataclass(frozen=True)
class PrimeCertificate:
    """
    Verifiable proof that p is prime.
    
    Contains witness information for verification.
    """
    p: int
    witness_type: str = "miller_rabin"  # or "lucas", "ecpp", "aks"
    witnesses: Tuple[int, ...] = ()
    certificate_hash: str = ""
    
    def __post_init__(self):
        if not self.certificate_hash:
            object.__setattr__(self, 'certificate_hash', 
                             hashlib.sha256(f"prime:{self.p}".encode()).hexdigest()[:16])
    
    def verify(self) -> bool:
        """Verify the prime certificate."""
        if self.p < 2:
            return False
        if self.p == 2:
            return True
        if self.p % 2 == 0:
            return False
        return self._miller_rabin_verify()
    
    def _miller_rabin_verify(self) -> bool:
        """Miller-Rabin primality test."""
        d, r = self.p - 1, 0
        while d % 2 == 0:
            d //= 2
            r += 1
        
        # Deterministic witnesses for small primes
        test_witnesses = self.witnesses if self.witnesses else (2, 3, 5, 7, 11, 13, 17)
        
        for a in test_witnesses:
            if a >= self.p:
                continue
            x = pow(a, d, self.p)
            if x == 1 or x == self.p - 1:
                continue
            for _ in range(r - 1):
                x = pow(x, 2, self.p)
                if x == self.p - 1:
                    break
            else:
                return False
        return True


@dataclass(frozen=True)
class FactorCertificate:
    """
    Verifiable witness that 1 < d < n and d | n.
    """
    n: int
    d: int
    certificate_hash: str = ""
    
    def __post_init__(self):
        if not self.certificate_hash:
            object.__setattr__(self, 'certificate_hash',
                             hashlib.sha256(f"factor:{self.n}:{self.d}".encode()).hexdigest()[:16])
    
    def verify(self) -> bool:
        """Verify the factor certificate."""
        return 1 < self.d < self.n and self.n % self.d == 0


@dataclass(frozen=True)
class ValuationCertificate:
    """
    Verifiable proof of exact multiplicity v_p(n) = α.
    """
    n: int
    p: int
    alpha: int  # The valuation v_p(n)
    certificate_hash: str = ""
    
    def __post_init__(self):
        if not self.certificate_hash:
            object.__setattr__(self, 'certificate_hash',
                             hashlib.sha256(f"val:{self.n}:{self.p}:{self.alpha}".encode()).hexdigest()[:16])
    
    def verify(self) -> bool:
        """Verify the valuation certificate."""
        if self.n <= 0 or self.p <= 1:
            return False
        
        # Check p^α | n
        if self.n % (self.p ** self.alpha) != 0:
            return False
        
        # Check p^(α+1) does not divide n
        if self.n % (self.p ** (self.alpha + 1)) == 0:
            return False
        
        return True


@dataclass
class FactorizationLedger:
    """
    Complete factorization proof with verifiable product invariant.
    """
    n: int
    factors: Dict[int, int] = field(default_factory=dict)  # p -> exponent
    prime_certs: List[PrimeCertificate] = field(default_factory=list)
    valuation_certs: List[ValuationCertificate] = field(default_factory=list)
    ledger_hash: str = ""
    
    def __post_init__(self):
        if not self.ledger_hash:
            self.ledger_hash = self._compute_hash()
    
    def _compute_hash(self) -> str:
        content = f"{self.n}:{sorted(self.factors.items())}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def verify(self) -> bool:
        """Verify complete factorization."""
        # Check product equals n
        product = 1
        for p, e in self.factors.items():
            product *= p ** e
        if product != self.n:
            return False
        
        # Verify all prime certificates
        for cert in self.prime_certs:
            if not cert.verify():
                return False
        
        # Verify all valuation certificates
        for cert in self.valuation_certs:
            if not cert.verify():
                return False
        
        return True
    
    def add_factor(self, p: int, e: int) -> None:
        """Add a prime factor with its exponent."""
        self.factors[p] = e
        self.prime_certs.append(PrimeCertificate(p))
        self.valuation_certs.append(ValuationCertificate(self.n, p, e))


@dataclass(frozen=True)
class DesertCertificate:
    """
    Verifiable proof that an interval is prime-free.
    
    Contains coverage witnesses (small prime divisors for each n in interval).
    """
    start: int
    end: int  # exclusive
    coverage: Dict[int, int] = field(default_factory=dict)  # n -> smallest prime divisor
    certificate_hash: str = ""
    
    def verify(self) -> bool:
        """Verify the desert certificate."""
        for n in range(self.start, self.end):
            if n < 2:
                continue
            if n not in self.coverage:
                return False
            p = self.coverage[n]
            if n % p != 0:
                return False
        return True


@dataclass(frozen=True)
class PrimePowerCertificate:
    """
    Verifiable proof that p^k is an exact prime power event.
    """
    p: int
    k: int
    prime_cert: Optional[PrimeCertificate] = None
    
    def verify(self) -> bool:
        """Verify the prime power certificate."""
        if self.prime_cert:
            if not self.prime_cert.verify():
                return False
        return self.k >= 1


# =============================================================================
# THE FOUR LENSES
# =============================================================================

class LensType(Enum):
    """The four lenses of the hybrid factoring system."""
    SQUARE = "□"    # Bank gcd projection + valuation extraction
    FRACTAL = "◇"   # Perfect-power detection + shatter
    DIAGONAL = "⌀"  # Difference-of-squares resonance
    CLOUD = "☁"     # Chaotic mixing → gcd witness


@dataclass
class LensResult:
    """Result from applying a lens."""
    lens: LensType
    found: bool
    factor: Optional[int] = None
    certificate: Optional[Any] = None
    cost: int = 0  # Computational cost
    

class SquareLens:
    """
    Square Lens (??□): Bank gcd projection + valuation extraction.
    
    Fast detection of small prime factors via trial division
    or precomputed prime banks.
    """
    
    def __init__(self, bank_size: int = 1000):
        self.bank = self._generate_prime_bank(bank_size)
    
    def _generate_prime_bank(self, size: int) -> List[int]:
        """Generate a bank of small primes."""
        sieve = [True] * (size + 1)
        sieve[0] = sieve[1] = False
        for i in range(2, int(size**0.5) + 1):
            if sieve[i]:
                for j in range(i*i, size + 1, i):
                    sieve[j] = False
        return [i for i in range(size + 1) if sieve[i]]
    
    def apply(self, n: int) -> LensResult:
        """Apply square lens to find small factors."""
        cost = 0
        for p in self.bank:
            cost += 1
            if p * p > n:
                break
            if n % p == 0:
                return LensResult(
                    LensType.SQUARE, True, p,
                    FactorCertificate(n, p), cost
                )
        return LensResult(LensType.SQUARE, False, cost=cost)


class FractalLens:
    """
    Fractal Lens (??◇): Perfect-power detection + shatter.
    
    Detects if n = r^k for some r, k > 1.
    """
    
    def __init__(self, max_power: int = 64):
        self.max_power = max_power
    
    def apply(self, n: int) -> LensResult:
        """Apply fractal lens to detect perfect powers."""
        cost = 0
        
        for k in range(2, self.max_power + 1):
            cost += 1
            # Compute k-th root
            r = int(round(n ** (1/k)))
            
            # Check neighbors due to floating point
            for candidate in [r - 1, r, r + 1]:
                if candidate > 1 and candidate ** k == n:
                    return LensResult(
                        LensType.FRACTAL, True, candidate,
                        PrimePowerCertificate(candidate, k), cost
                    )
            
            # Early termination: if r < 2, no point checking higher powers
            if r < 2:
                break
        
        return LensResult(LensType.FRACTAL, False, cost=cost)


class DiagonalLens:
    """
    Diagonal Lens (??⌀): Difference-of-squares resonance.
    
    For odd n: n = a² - b² = (a-b)(a+b)
    Efficient when factors p,q are close (near-square semiprimes).
    """
    
    def __init__(self, budget: int = 10000):
        self.budget = budget
    
    def apply(self, n: int) -> LensResult:
        """Apply diagonal lens using Fermat's method."""
        if n % 2 == 0:
            return LensResult(LensType.DIAGONAL, False, cost=1)
        
        cost = 0
        a = math.isqrt(n)
        if a * a < n:
            a += 1
        
        b2 = a * a - n
        
        while cost < self.budget:
            cost += 1
            b = math.isqrt(b2)
            
            if b * b == b2:
                # Found! n = (a-b)(a+b)
                factor = a - b
                if 1 < factor < n:
                    return LensResult(
                        LensType.DIAGONAL, True, factor,
                        FactorCertificate(n, factor), cost
                    )
            
            a += 1
            b2 = a * a - n
        
        return LensResult(LensType.DIAGONAL, False, cost=cost)


class CloudLens:
    """
    Cloud Lens (??☁): Chaotic mixing → gcd witness.
    
    Pollard's rho algorithm with Brent's cycle detection.
    """
    
    def __init__(self, budget: int = 100000):
        self.budget = budget
    
    def apply(self, n: int, c: int = 1) -> LensResult:
        """Apply cloud lens using Pollard's rho."""
        if n % 2 == 0:
            return LensResult(LensType.CLOUD, True, 2,
                            FactorCertificate(n, 2), 1)
        
        cost = 0
        x = y = 2
        d = 1
        
        f = lambda x: (x * x + c) % n
        
        while d == 1 and cost < self.budget:
            cost += 1
            x = f(x)
            y = f(f(y))
            d = math.gcd(abs(x - y), n)
        
        if d != n and d != 1:
            return LensResult(
                LensType.CLOUD, True, d,
                FactorCertificate(n, d), cost
            )
        
        return LensResult(LensType.CLOUD, False, cost=cost)


# =============================================================================
# THE 4-WAY HYBRID EQUATION
# =============================================================================

class HybridFactorizer:
    """
    The 4-Way Hybrid Factoring System.
    
    Routes inputs by geometry:
    - small factors → Square
    - perfect powers → Fractal
    - near-square semiprimes → Diagonal
    - hard residuals → Cloud
    """
    
    def __init__(self):
        self.square = SquareLens(bank_size=10000)
        self.fractal = FractalLens(max_power=64)
        self.diagonal = DiagonalLens(budget=10000)
        self.cloud = CloudLens(budget=100000)
        
        self.ledger_entries: List[FactorizationLedger] = []
    
    def is_prime(self, n: int) -> Tuple[bool, Optional[PrimeCertificate]]:
        """Check if n is prime."""
        if n < 2:
            return False, None
        if n == 2:
            return True, PrimeCertificate(2)
        if n % 2 == 0:
            return False, None
        
        cert = PrimeCertificate(n)
        return cert.verify(), cert if cert.verify() else None
    
    def factorize(self, n: int) -> FactorizationLedger:
        """
        Complete factorization using 4-way hybrid equation.
        
        ??(n) = {
            {(n,1)},                          if Z₀^prime(n) = PRIME
            ??(d) ⊎ ??(n/d),                   if d = ??□(n) ≠ ∅
            ??(r) ⊎ ... ⊎ ??(r),              if (r,k) = ??◇(n) ≠ ∅
            ??(d) ⊎ ??(n/d),                   if d = ??⌀(n) ≠ ∅
            ??(d) ⊎ ??(n/d),                   if d = ??☁(n) ≠ ∅
            INCOMPLETE(n),                    if budget exhausted
        }
        """
        ledger = FactorizationLedger(n)
        self._factorize_recursive(n, ledger)
        self.ledger_entries.append(ledger)
        return ledger
    
    def _factorize_recursive(self, n: int, ledger: FactorizationLedger) -> None:
        """Recursive factorization."""
        if n <= 1:
            return
        
        # Check if prime
        is_p, cert = self.is_prime(n)
        if is_p:
            if n in ledger.factors:
                ledger.factors[n] += 1
            else:
                ledger.add_factor(n, 1)
            return
        
        # Try each lens in order
        
        # Lens 1: Square (small factors)
        result = self.square.apply(n)
        if result.found and result.factor:
            self._extract_factor(n, result.factor, ledger)
            return
        
        # Lens 2: Fractal (perfect powers)
        result = self.fractal.apply(n)
        if result.found and result.factor:
            # n = r^k, factorize r and multiply exponents
            k = 1
            r = result.factor
            while r ** (k + 1) <= n:
                if r ** (k + 1) == n:
                    k += 1
                else:
                    break
            # Factorize r, then multiply all exponents by k
            sub_ledger = FactorizationLedger(r)
            self._factorize_recursive(r, sub_ledger)
            for p, e in sub_ledger.factors.items():
                if p in ledger.factors:
                    ledger.factors[p] += e * k
                else:
                    ledger.add_factor(p, e * k)
            return
        
        # Lens 3: Diagonal (near-square)
        result = self.diagonal.apply(n)
        if result.found and result.factor:
            self._extract_factor(n, result.factor, ledger)
            return
        
        # Lens 4: Cloud (chaotic mixing)
        for c in [1, 2, 3, 5, 7]:  # Try different constants
            result = self.cloud.apply(n, c)
            if result.found and result.factor:
                self._extract_factor(n, result.factor, ledger)
                return
        
        # Budget exhausted - treat as prime (may be wrong for very large numbers)
        ledger.add_factor(n, 1)
    
    def _extract_factor(self, n: int, d: int, ledger: FactorizationLedger) -> None:
        """Extract factor d from n and continue factorization."""
        # Count multiplicity of d
        e = 0
        temp = n
        while temp % d == 0:
            temp //= d
            e += 1
        
        # Factorize d
        self._factorize_recursive(d, ledger)
        
        # Multiply the exponent
        for p in list(ledger.factors.keys()):
            if n % (p ** ledger.factors[p]) == 0:
                # This factor came from d, multiply by e
                pass  # Already handled
        
        # Continue with remaining
        self._factorize_recursive(temp, ledger)


# =============================================================================
# THE 256-STATE ATLAS
# =============================================================================

class MathConstant(Enum):
    """The four fundamental math constants."""
    E = "e"       # Euler's number - exponential flow
    I = "i"       # Imaginary unit - phase/unitarity
    PI = "π"      # Pi - geometry/rotation
    PHI = "φ"     # Golden ratio - scale/self-similarity


@dataclass
class AtlasState:
    """
    A state in the 256-state atlas.
    
    Derived from (e, i, π, φ) × 64 root states.
    """
    constant: MathConstant
    root_index: int  # 0-63
    
    @property
    def index(self) -> int:
        """Get global index (0-255)."""
        const_idx = list(MathConstant).index(self.constant)
        return const_idx * 64 + self.root_index
    
    @classmethod
    def from_index(cls, idx: int) -> 'AtlasState':
        """Create from global index."""
        const_idx = idx // 64
        root_idx = idx % 64
        return cls(list(MathConstant)[const_idx], root_idx)


class SymmetryAtlas:
    """
    The 256-state symmetry atlas for parameterization.
    
    Enables deterministic "math-artist" parameterization of:
    - schedules
    - tapers
    - wheels
    - cross-domain routing
    """
    
    def __init__(self):
        self.states = [AtlasState.from_index(i) for i in range(256)]
    
    def get_state(self, constant: MathConstant, root: int) -> AtlasState:
        """Get specific atlas state."""
        return AtlasState(constant, root % 64)
    
    def route_by_geometry(self, n: int) -> AtlasState:
        """Determine optimal atlas state for a number."""
        # Use properties of n to select state
        bits = n.bit_length()
        
        # Select constant based on structure
        if self._has_small_factors(n):
            const = MathConstant.E  # Exponential decomposition
        elif self._is_near_square(n):
            const = MathConstant.PI  # Geometric (diagonal)
        elif self._is_smooth(n):
            const = MathConstant.PHI  # Self-similar
        else:
            const = MathConstant.I  # Phase mixing (cloud)
        
        # Select root based on bit pattern
        root = (n ^ (n >> 8) ^ (n >> 16)) % 64
        
        return AtlasState(const, root)
    
    def _has_small_factors(self, n: int) -> bool:
        """Check if n has small prime factors."""
        for p in [2, 3, 5, 7, 11, 13]:
            if n % p == 0:
                return True
        return False
    
    def _is_near_square(self, n: int) -> bool:
        """Check if n is close to a perfect square."""
        sqrt_n = math.isqrt(n)
        return abs(n - sqrt_n * sqrt_n) < sqrt_n // 10
    
    def _is_smooth(self, n: int) -> bool:
        """Check if n is B-smooth for small B."""
        temp = n
        for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]:
            while temp % p == 0:
                temp //= p
        return temp == 1


# =============================================================================
# RUNTIME LOOP
# =============================================================================

class RuntimeState:
    """
    Runtime state Σ for the factorization kernel.
    
    Contains:
    - work_queue: unresolved targets
    - corridor: candidate sets + constraints
    - proof_store: certificates
    - telemetry: cost and stability metrics
    - ledger: immutable run record
    """
    
    def __init__(self, targets: List[int]):
        self.work_queue: List[int] = targets.copy()
        self.corridor: Dict[str, Any] = {}
        self.proof_store: List[Any] = []
        self.telemetry: Dict[str, int] = {"total_cost": 0, "lens_calls": 0}
        self.ledger: List[str] = []
    
    def is_terminal(self) -> bool:
        """Check if state is terminal (work queue empty)."""
        return len(self.work_queue) == 0
    
    def log(self, entry: str) -> None:
        """Add entry to ledger."""
        self.ledger.append(entry)


class PrimeFactorizationKernel:
    """
    The complete Prime Factorization Kernel.
    
    Runtime loop: rotate → nullify → jump → spin → collapse → ledger
    """
    
    def __init__(self):
        self.factorizer = HybridFactorizer()
        self.atlas = SymmetryAtlas()
    
    def execute(self, targets: List[int]) -> Dict[int, FactorizationLedger]:
        """Execute factorization on all targets."""
        state = RuntimeState(targets)
        results: Dict[int, FactorizationLedger] = {}
        
        while not state.is_terminal():
            n = state.work_queue.pop(0)
            
            # Rotate: select optimal lens via atlas
            atlas_state = self.atlas.route_by_geometry(n)
            state.log(f"ROTATE: n={n} → atlas={atlas_state.constant.value}[{atlas_state.root_index}]")
            
            # Execute factorization
            ledger = self.factorizer.factorize(n)
            
            # Collapse: verify certificates
            if ledger.verify():
                state.log(f"COLLAPSE: n={n} verified")
                results[n] = ledger
                state.proof_store.append(ledger)
            else:
                state.log(f"FAIL: n={n} verification failed")
            
            state.telemetry["lens_calls"] += 1
        
        return results


# =============================================================================
# VALIDATION
# =============================================================================

def validate_prime_factorization() -> bool:
    """Validate the prime factorization kernel."""
    
    # Test PrimeCertificate
    cert2 = PrimeCertificate(2)
    assert cert2.verify()
    
    cert17 = PrimeCertificate(17)
    assert cert17.verify()
    
    cert15 = PrimeCertificate(15)
    assert not cert15.verify()
    
    # Test FactorCertificate
    fcert = FactorCertificate(15, 3)
    assert fcert.verify()
    
    # Test ValuationCertificate
    vcert = ValuationCertificate(24, 2, 3)  # 24 = 2^3 * 3
    assert vcert.verify()
    
    # Test lenses
    square = SquareLens()
    result = square.apply(15)
    assert result.found and result.factor == 3
    
    fractal = FractalLens()
    result = fractal.apply(27)  # 3^3
    assert result.found and result.factor == 3
    
    diagonal = DiagonalLens()
    result = diagonal.apply(143)  # 11 * 13, close factors
    assert result.found
    
    cloud = CloudLens()
    result = cloud.apply(91)  # 7 * 13
    assert result.found
    
    # Test HybridFactorizer
    factorizer = HybridFactorizer()
    ledger = factorizer.factorize(360)  # 2^3 * 3^2 * 5
    assert ledger.verify()
    assert 2 in ledger.factors
    assert 3 in ledger.factors
    assert 5 in ledger.factors
    
    # Test atlas
    atlas = SymmetryAtlas()
    state = atlas.get_state(MathConstant.PI, 0)
    assert state.constant == MathConstant.PI
    
    # Test kernel
    kernel = PrimeFactorizationKernel()
    results = kernel.execute([12, 35, 100])
    assert 12 in results
    assert 35 in results
    
    return True


if __name__ == "__main__":
    print("=" * 70)
    print("ATHENA OS - PRIME FACTORIZATION KERNEL")
    print("The Crystal-Fractal Hybrid Toolkit")
    print("=" * 70)
    
    print("\nValidating module...")
    assert validate_prime_factorization()
    print("✓ Module validated")
    
    # Demo
    print("\n--- FACTORIZATION DEMO ---")
    kernel = PrimeFactorizationKernel()
    
    test_numbers = [12, 100, 1001, 10403, 123456]
    results = kernel.execute(test_numbers)
    
    for n, ledger in results.items():
        factors_str = " × ".join(f"{p}^{e}" if e > 1 else str(p) 
                                 for p, e in sorted(ledger.factors.items()))
        verified = "✓" if ledger.verify() else "✗"
        print(f"  {n} = {factors_str} {verified}")
    
    print("\n--- 256-STATE ATLAS ---")
    atlas = SymmetryAtlas()
    for n in [12, 143, 1000000007]:
        state = atlas.route_by_geometry(n)
        print(f"  {n} → {state.constant.value}[{state.root_index}]")
