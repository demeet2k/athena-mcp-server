"""
ATHENA OS - Factorization Lenses
=================================
The four projections for factorization as carrier recovery.

The 4-Way Hybrid Factoring Equation:
- Square lens (L_□): Bank gcd projection + valuation extraction
- Fractal lens (L_◇): Perfect-power detection + shatter
- Diagonal lens (L_diag): Difference-of-squares resonance
- Cloud lens (L_☁): Chaotic mixing → gcd witness (Pollard rho)

Each lens is suited for different factor geometries:
- Small factors → Square
- Perfect powers → Fractal
- Near-square semiprimes → Diagonal
- Hard residuals → Cloud

The chain routes inputs by geometry, and all outputs
are certified by divisibility + primality checks.
"""

from __future__ import annotations
from enum import IntEnum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable
import math
import random

from .certificates import (
    FactorCertificate, PrimeCertificate, FactorizationLedger,
    create_prime_certificate, is_prime_miller_rabin, detect_prime_power
)


# =============================================================================
# LENS TYPES
# =============================================================================

class LensType(IntEnum):
    """Types of factorization lenses."""
    SQUARE = 0    # GCD bank projection
    FRACTAL = 1   # Perfect power detection
    DIAGONAL = 2  # Difference of squares
    CLOUD = 3     # Randomized (Pollard rho)


@dataclass
class LensResult:
    """Result from a lens operation."""
    lens_type: LensType
    success: bool
    factor: Optional[int] = None
    cofactor: Optional[int] = None
    
    # Certificate for the factor
    factor_cert: Optional[FactorCertificate] = None
    
    # Metadata
    iterations: int = 0
    cost: float = 0.0
    
    def verify(self, n: int) -> bool:
        """Verify the result."""
        if not self.success or self.factor is None:
            return False
        
        if self.factor_cert is None:
            self.factor_cert = FactorCertificate(n=n, d=self.factor)
        
        return self.factor_cert.verified


# =============================================================================
# SQUARE LENS - GCD Bank Projection
# =============================================================================

class SquareLens:
    """
    Square Lens: GCD bank projection + valuation extraction.
    
    Projects n onto a bank of small primes using gcd.
    This is "white-light spectroscopy": many carriers extracted in one shot.
    
    g = gcd(n, M) = ∏_{p|M} p^{min(v_p(n), v_p(M))}
    """
    
    # Default small prime bank
    SMALL_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    
    def __init__(self, prime_bank: List[int] = None, max_power: int = 10):
        """
        Initialize Square Lens.
        
        Args:
            prime_bank: List of small primes to test
            max_power: Maximum power to extract per prime
        """
        self.prime_bank = prime_bank or self.SMALL_PRIMES.copy()
        self.max_power = max_power
        
        # Precompute primorial for bank gcd
        self.primorial = 1
        for p in self.prime_bank:
            self.primorial *= p ** max_power
    
    def apply(self, n: int, budget: int = 100) -> LensResult:
        """
        Apply Square Lens to find small factors.
        
        Returns the first non-trivial factor found.
        """
        iterations = 0
        
        # Method 1: Bank GCD
        g = math.gcd(n, self.primorial)
        iterations += 1
        
        if 1 < g < n:
            return LensResult(
                lens_type=LensType.SQUARE,
                success=True,
                factor=g,
                cofactor=n // g,
                iterations=iterations,
                cost=iterations
            )
        
        # Method 2: Individual prime trial division
        for p in self.prime_bank:
            if iterations >= budget:
                break
            
            iterations += 1
            
            if n % p == 0:
                # Find full power
                factor = 1
                m = n
                while m % p == 0:
                    factor *= p
                    m //= p
                
                if 1 < factor < n:
                    return LensResult(
                        lens_type=LensType.SQUARE,
                        success=True,
                        factor=factor,
                        cofactor=n // factor,
                        iterations=iterations,
                        cost=iterations
                    )
        
        return LensResult(
            lens_type=LensType.SQUARE,
            success=False,
            iterations=iterations,
            cost=iterations
        )
    
    def extract_valuations(self, n: int) -> Dict[int, int]:
        """
        Extract all valuations for primes in the bank.
        
        Returns {p: v_p(n)} for each p with v_p(n) > 0.
        """
        valuations = {}
        m = n
        
        for p in self.prime_bank:
            alpha = 0
            while m % p == 0:
                alpha += 1
                m //= p
            if alpha > 0:
                valuations[p] = alpha
        
        return valuations


# =============================================================================
# FRACTAL LENS - Perfect Power Detection
# =============================================================================

class FractalLens:
    """
    Fractal Lens: Perfect-power detection + shatter.
    
    Detects if n = r^k for some k > 1, then shatters to k copies of r.
    
    This handles the recursive/self-similar structure of prime powers.
    """
    
    def __init__(self, max_power: int = 100):
        """
        Initialize Fractal Lens.
        
        Args:
            max_power: Maximum power to check
        """
        self.max_power = max_power
    
    def apply(self, n: int, budget: int = 100) -> LensResult:
        """
        Apply Fractal Lens to detect perfect powers.
        
        Returns (root, power) if n = root^power.
        """
        if n < 4:
            return LensResult(
                lens_type=LensType.FRACTAL,
                success=False,
                iterations=1,
                cost=1
            )
        
        result = detect_prime_power(n)
        
        if result is not None:
            root, power = result
            return LensResult(
                lens_type=LensType.FRACTAL,
                success=True,
                factor=root,
                cofactor=power,  # Using cofactor to store power
                iterations=int(math.log2(n)),
                cost=int(math.log2(n))
            )
        
        # Check for composite perfect powers
        max_k = min(self.max_power, int(math.log2(n)) + 1)
        iterations = 0
        
        for k in range(2, max_k + 1):
            if iterations >= budget:
                break
            
            iterations += 1
            
            # Newton's method for k-th root
            root = int(round(n ** (1/k)))
            
            for r in [root - 1, root, root + 1]:
                if r < 2:
                    continue
                if r ** k == n:
                    return LensResult(
                        lens_type=LensType.FRACTAL,
                        success=True,
                        factor=r,
                        cofactor=k,  # Power
                        iterations=iterations,
                        cost=iterations
                    )
        
        return LensResult(
            lens_type=LensType.FRACTAL,
            success=False,
            iterations=iterations,
            cost=iterations
        )
    
    def shatter(self, n: int) -> Optional[Tuple[int, int]]:
        """
        Shatter a perfect power into (root, power).
        
        Returns None if n is not a perfect power.
        """
        result = self.apply(n)
        if result.success:
            return (result.factor, result.cofactor)
        return None


# =============================================================================
# DIAGONAL LENS - Difference of Squares
# =============================================================================

class DiagonalLens:
    """
    Diagonal Lens: Difference-of-squares resonance (Fermat's method).
    
    For odd n: n = a² - b² = (a-b)(a+b)
    
    If factors p,q are close, b is small and a is near √n,
    so a bounded scan finds a²-n = b² quickly.
    
    This is the "near-square resonance axis" - exploits diagonal symmetry.
    """
    
    def __init__(self, max_iterations: int = 10000):
        """
        Initialize Diagonal Lens.
        
        Args:
            max_iterations: Maximum iterations for the search
        """
        self.max_iterations = max_iterations
    
    def apply(self, n: int, budget: int = None) -> LensResult:
        """
        Apply Diagonal Lens (Fermat's factorization method).
        
        Searches for a such that a² - n is a perfect square.
        """
        if budget is None:
            budget = self.max_iterations
        
        # Only works for odd composites
        if n < 4 or n % 2 == 0:
            return LensResult(
                lens_type=LensType.DIAGONAL,
                success=False,
                iterations=0,
                cost=0
            )
        
        # Start from ceil(sqrt(n))
        a = int(math.isqrt(n))
        if a * a < n:
            a += 1
        
        iterations = 0
        
        while iterations < budget:
            iterations += 1
            
            b_squared = a * a - n
            b = int(math.isqrt(b_squared))
            
            if b * b == b_squared:
                # Found it: n = (a-b)(a+b)
                factor1 = a - b
                factor2 = a + b
                
                if 1 < factor1 < n:
                    return LensResult(
                        lens_type=LensType.DIAGONAL,
                        success=True,
                        factor=factor1,
                        cofactor=factor2,
                        iterations=iterations,
                        cost=iterations
                    )
            
            a += 1
        
        return LensResult(
            lens_type=LensType.DIAGONAL,
            success=False,
            iterations=iterations,
            cost=iterations
        )
    
    def resonance_distance(self, n: int) -> float:
        """
        Estimate the "resonance distance" - how close n is to a perfect square.
        
        Lower values indicate Diagonal lens is more suitable.
        """
        sqrt_n = math.isqrt(n)
        return (sqrt_n + 1) ** 2 - n


# =============================================================================
# CLOUD LENS - Pollard's Rho
# =============================================================================

class CloudLens:
    """
    Cloud Lens: Chaotic mixing → gcd witness (Pollard's rho).
    
    Uses pseudo-random iteration to find factors through gcd witnesses.
    This is the "probabilistic cloud" approach for hard residuals.
    
    f(x) = x² + c (mod n) for random c
    Uses Floyd's cycle detection.
    """
    
    def __init__(self, max_iterations: int = 100000):
        """
        Initialize Cloud Lens.
        
        Args:
            max_iterations: Maximum iterations per attempt
        """
        self.max_iterations = max_iterations
    
    def _f(self, x: int, c: int, n: int) -> int:
        """The pseudo-random function f(x) = x² + c (mod n)."""
        return (x * x + c) % n
    
    def apply(self, n: int, budget: int = None) -> LensResult:
        """
        Apply Cloud Lens (Pollard's rho algorithm).
        
        Uses Floyd's cycle detection with gcd checks.
        """
        if budget is None:
            budget = self.max_iterations
        
        if n < 4:
            return LensResult(
                lens_type=LensType.CLOUD,
                success=False,
                iterations=0,
                cost=0
            )
        
        # Try with different starting values and constants
        for c in [1, 2, 3, 5, 7, 11]:
            x = 2
            y = 2
            d = 1
            
            iterations = 0
            
            while d == 1 and iterations < budget:
                iterations += 1
                
                x = self._f(x, c, n)
                y = self._f(self._f(y, c, n), c, n)
                
                d = math.gcd(abs(x - y), n)
            
            if 1 < d < n:
                return LensResult(
                    lens_type=LensType.CLOUD,
                    success=True,
                    factor=d,
                    cofactor=n // d,
                    iterations=iterations,
                    cost=iterations
                )
            
            if d == n:
                # Cycle found but no factor - try different c
                continue
        
        return LensResult(
            lens_type=LensType.CLOUD,
            success=False,
            iterations=budget,
            cost=budget
        )
    
    def brent_variant(self, n: int, budget: int = None) -> LensResult:
        """
        Brent's improvement to Pollard's rho.
        
        Uses a different cycle detection that's often faster.
        """
        if budget is None:
            budget = self.max_iterations
        
        if n < 4:
            return LensResult(
                lens_type=LensType.CLOUD,
                success=False,
                iterations=0,
                cost=0
            )
        
        for c in [1, 2, 3, 5]:
            y = random.randint(1, n - 1)
            c_val = c
            m = random.randint(1, n - 1)
            g = 1
            r = 1
            q = 1
            
            iterations = 0
            
            while g == 1 and iterations < budget:
                x = y
                for _ in range(r):
                    y = self._f(y, c_val, n)
                
                k = 0
                while k < r and g == 1:
                    ys = y
                    for _ in range(min(m, r - k)):
                        y = self._f(y, c_val, n)
                        q = (q * abs(x - y)) % n
                        iterations += 1
                    
                    g = math.gcd(q, n)
                    k += m
                
                r *= 2
            
            if g == n:
                # Backtrack
                while True:
                    ys = self._f(ys, c_val, n)
                    g = math.gcd(abs(x - ys), n)
                    if g > 1:
                        break
            
            if 1 < g < n:
                return LensResult(
                    lens_type=LensType.CLOUD,
                    success=True,
                    factor=g,
                    cofactor=n // g,
                    iterations=iterations,
                    cost=iterations
                )
        
        return LensResult(
            lens_type=LensType.CLOUD,
            success=False,
            iterations=budget,
            cost=budget
        )


# =============================================================================
# HYBRID LENS CHAIN
# =============================================================================

@dataclass
class LensChain:
    """
    The 4-Way Hybrid Factoring Chain.
    
    Routes inputs by geometry through the four lenses:
    1. Square: small factors
    2. Fractal: perfect powers
    3. Diagonal: near-square semiprimes
    4. Cloud: hard residuals
    """
    
    square: SquareLens = field(default_factory=SquareLens)
    fractal: FractalLens = field(default_factory=FractalLens)
    diagonal: DiagonalLens = field(default_factory=DiagonalLens)
    cloud: CloudLens = field(default_factory=CloudLens)
    
    def factor(self, n: int, budget: int = 10000) -> FactorizationLedger:
        """
        Complete factorization using the 4-way chain.
        
        Returns a FactorizationLedger with certified factors.
        """
        ledger = FactorizationLedger(n=n)
        work_queue = [n]
        total_iterations = 0
        
        while work_queue and total_iterations < budget:
            current = work_queue.pop()
            
            if current <= 1:
                continue
            
            # Check if prime
            if is_prime_miller_rabin(current):
                ledger.add_factor(current, 1)
                continue
            
            # Try lenses in order
            result = None
            
            # 1. Square lens (small factors)
            result = self.square.apply(current, budget=100)
            total_iterations += result.iterations
            
            if not result.success:
                # 2. Fractal lens (perfect powers)
                result = self.fractal.apply(current, budget=50)
                total_iterations += result.iterations
                
                if result.success:
                    # Handle perfect power: add power copies
                    power = result.cofactor
                    root = result.factor
                    work_queue.append(root)
                    # The factorization will be handled when we factor root
                    continue
            
            if not result.success:
                # 3. Diagonal lens (near-square)
                result = self.diagonal.apply(current, budget=1000)
                total_iterations += result.iterations
            
            if not result.success:
                # 4. Cloud lens (Pollard rho)
                result = self.cloud.apply(current, budget=5000)
                total_iterations += result.iterations
            
            if result.success and result.factor:
                # Found a factor - add both parts to work queue
                factor = result.factor
                cofactor = current // factor
                
                if factor > 1:
                    work_queue.append(factor)
                if cofactor > 1:
                    work_queue.append(cofactor)
            else:
                # Budget exhausted for this number
                # Leave it in the remainder
                pass
        
        return ledger
    
    def find_one_factor(self, n: int) -> Optional[LensResult]:
        """
        Find a single factor using the chain.
        
        Returns the first successful result.
        """
        if is_prime_miller_rabin(n):
            return None
        
        for lens_apply in [
            lambda: self.square.apply(n),
            lambda: self.fractal.apply(n),
            lambda: self.diagonal.apply(n),
            lambda: self.cloud.apply(n)
        ]:
            result = lens_apply()
            if result.success:
                return result
        
        return None


# =============================================================================
# VALIDATION
# =============================================================================

def validate_lenses() -> bool:
    """Validate factorization lenses."""
    
    # Test Square Lens
    square = SquareLens()
    result = square.apply(100)
    assert result.success
    assert result.factor in [2, 4, 5, 10, 20, 25, 50]  # Any factor works
    
    # Test Fractal Lens
    fractal = FractalLens()
    result = fractal.apply(27)  # 3^3
    assert result.success
    assert result.factor == 3
    assert result.cofactor == 3  # Power
    
    result = fractal.apply(1024)  # 2^10
    assert result.success
    assert result.factor == 2
    assert result.cofactor == 10
    
    # Test Diagonal Lens
    diagonal = DiagonalLens()
    # 15 = 4² - 1² = (4-1)(4+1) = 3*5
    result = diagonal.apply(15)
    assert result.success
    assert result.factor in [3, 5]
    
    # Test Cloud Lens
    cloud = CloudLens()
    result = cloud.apply(91)  # 7 * 13
    assert result.success
    assert result.factor in [7, 13]
    
    # Test Lens Chain
    chain = LensChain()
    ledger = chain.factor(360)  # 2³ × 3² × 5
    assert ledger.complete or ledger.remainder == 1
    
    ledger = chain.factor(1001)  # 7 × 11 × 13
    assert ledger.complete or ledger.remainder == 1
    
    return True


if __name__ == "__main__":
    print("Validating Factorization Lenses...")
    assert validate_lenses()
    print("✓ Factorization Lenses validated")
    
    # Demo
    chain = LensChain()
    
    test_numbers = [360, 1001, 10007, 104729, 1000003]
    
    print("\n=== Lens Chain Demo ===")
    for n in test_numbers:
        print(f"\nFactoring {n}:")
        
        if is_prime_miller_rabin(n):
            print(f"  {n} is PRIME")
            continue
        
        ledger = chain.factor(n)
        if ledger.complete:
            factors_str = " × ".join(
                f"{e.p}^{e.alpha}" if e.alpha > 1 else str(e.p)
                for e in sorted(ledger.entries, key=lambda x: x.p)
            )
            print(f"  {n} = {factors_str}")
        else:
            print(f"  Partial factorization, remainder = {ledger.remainder}")
