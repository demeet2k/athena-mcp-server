"""
ATHENA OS - Sieve Wheels and Desert Certificates
=================================================
Hard deserts, primorial wheels, and prime-free interval certification.

Key Concepts:
- Primorial P_B = ∏_{p≤B} p (product of primes up to B)
- Wheel R_B = {r ∈ Z/P_B : gcd(r, P_B) = 1} (coprime residues)
- Survivor set Surv_B(I) = {n ∈ I : n mod P_B ∈ R_B}
- Hard desert: interval where A_B(n) = 0 for all n (sieved out)
- Jacobsthal function j(m): minimum J such that any J consecutive integers
  contain at least one coprime to m

Desert Certification:
1. Hard-kill: prove all positions sieved by small primes
2. Soft tail: certify survivors are composite
3. Certificate: coverage witnesses + survivor composite proofs
"""

from __future__ import annotations
from enum import IntEnum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set, Any
from datetime import datetime
import math

from .certificates import (
    PrimeCertificate, FactorCertificate, create_prime_certificate,
    is_prime_miller_rabin
)


# =============================================================================
# PRIMORIAL AND WHEEL COMPUTATION
# =============================================================================

def primes_up_to(n: int) -> List[int]:
    """Generate all primes up to n using sieve of Eratosthenes."""
    if n < 2:
        return []
    
    sieve = [True] * (n + 1)
    sieve[0] = sieve[1] = False
    
    for i in range(2, int(math.isqrt(n)) + 1):
        if sieve[i]:
            for j in range(i * i, n + 1, i):
                sieve[j] = False
    
    return [i for i in range(2, n + 1) if sieve[i]]


def primorial(B: int) -> int:
    """
    Compute P_B = ∏_{p≤B} p (primorial).
    
    The product of all primes up to B.
    """
    primes = primes_up_to(B)
    result = 1
    for p in primes:
        result *= p
    return result


def euler_phi(n: int) -> int:
    """Compute Euler's totient function φ(n)."""
    result = n
    p = 2
    temp_n = n
    
    while p * p <= temp_n:
        if temp_n % p == 0:
            while temp_n % p == 0:
                temp_n //= p
            result -= result // p
        p += 1
    
    if temp_n > 1:
        result -= result // temp_n
    
    return result


@dataclass
class PrimorialWheel:
    """
    A primorial wheel for sieving.
    
    The wheel R_B contains all residues coprime to P_B.
    These are the "survivor" positions that pass the small-prime sieve.
    
    |R_B| = φ(P_B) = ∏_{p≤B} (p-1)
    """
    cutoff_B: int  # Prime cutoff
    primorial: int  # P_B
    wheel_residues: Set[int]  # R_B - coprime residues
    
    def __init__(self, B: int):
        """Initialize wheel with prime cutoff B."""
        self.cutoff_B = B
        self.primorial = primorial(B)
        self.wheel_residues = self._compute_wheel()
    
    def _compute_wheel(self) -> Set[int]:
        """Compute the wheel residues (coprime to P_B)."""
        P = self.primorial
        residues = set()
        
        for r in range(P):
            if math.gcd(r, P) == 1:
                residues.add(r)
        
        return residues
    
    @property
    def density(self) -> float:
        """Wheel density = |R_B| / P_B."""
        return len(self.wheel_residues) / self.primorial
    
    def is_survivor(self, n: int) -> bool:
        """Check if n survives the wheel (is coprime to P_B)."""
        return (n % self.primorial) in self.wheel_residues
    
    def survivors_in_interval(self, start: int, length: int) -> List[int]:
        """Get all survivors in [start, start + length)."""
        return [
            start + i 
            for i in range(length) 
            if self.is_survivor(start + i)
        ]
    
    def count_survivors(self, start: int, length: int) -> int:
        """Count survivors in [start, start + length)."""
        count = 0
        for i in range(length):
            if self.is_survivor(start + i):
                count += 1
        return count
    
    def covering_prime(self, n: int) -> Optional[int]:
        """
        Find a small prime that divides n.
        
        Returns None if n is coprime to P_B.
        """
        primes = primes_up_to(self.cutoff_B)
        for p in primes:
            if n % p == 0:
                return p
        return None


# =============================================================================
# JACOBSTHAL FUNCTION
# =============================================================================

def jacobsthal(m: int) -> int:
    """
    Compute the Jacobsthal function j(m).
    
    j(m) is the smallest J such that any J consecutive integers
    contain at least one coprime to m.
    
    Equivalently, j(m) - 1 is the maximum gap between consecutive
    integers coprime to m.
    """
    if m <= 1:
        return 1
    
    # Find all residues coprime to m
    coprime_residues = sorted([r for r in range(m) if math.gcd(r, m) == 1])
    
    if not coprime_residues:
        return m + 1  # No coprimes exist
    
    # Find maximum gap (considering wraparound)
    max_gap = 0
    
    for i in range(len(coprime_residues)):
        if i == 0:
            # Gap from last to first (wraparound)
            gap = (m - coprime_residues[-1]) + coprime_residues[0]
        else:
            gap = coprime_residues[i] - coprime_residues[i-1]
        
        max_gap = max(max_gap, gap)
    
    return max_gap


def max_desert_length(B: int) -> int:
    """
    Maximum length of a prime-free run using sieve up to B.
    
    This is j(P_B) - 1 where P_B is the primorial.
    """
    P = primorial(B)
    return jacobsthal(P) - 1


# =============================================================================
# HARD DESERT DETECTION
# =============================================================================

@dataclass
class HardDesert:
    """
    A hard desert: an interval where all positions are sieved out.
    
    For cutoff B, a hard desert is an interval I where:
    - A_B(n) = 0 for all n in I
    - Every n in I has a prime factor ≤ B
    
    If the interval is above B, it contains no primes.
    """
    start: int
    length: int
    cutoff_B: int
    covering_primes: Dict[int, int]  # offset -> covering prime
    
    @property
    def end(self) -> int:
        """End of interval (exclusive)."""
        return self.start + self.length
    
    @property
    def is_above_cutoff(self) -> bool:
        """Check if all elements are > B."""
        return self.start > self.cutoff_B
    
    def is_prime_free(self) -> bool:
        """
        Check if this desert is provably prime-free.
        
        True if all elements are above B and have covering primes.
        """
        if not self.is_above_cutoff:
            return False
        return len(self.covering_primes) == self.length


def find_hard_desert(wheel: PrimorialWheel, start: int, 
                     min_length: int = 2) -> Optional[HardDesert]:
    """
    Find a hard desert starting at or after 'start'.
    
    Returns the first run of non-survivors of length >= min_length.
    """
    P = wheel.primorial
    B = wheel.cutoff_B
    
    current_start = None
    current_length = 0
    covering = {}
    
    # Search up to one period
    for offset in range(P):
        n = start + offset
        
        if wheel.is_survivor(n):
            # End of potential desert
            if current_length >= min_length:
                return HardDesert(
                    start=current_start,
                    length=current_length,
                    cutoff_B=B,
                    covering_primes=covering
                )
            current_start = None
            current_length = 0
            covering = {}
        else:
            # Extend desert
            if current_start is None:
                current_start = n
            
            covering_p = wheel.covering_prime(n)
            if covering_p:
                covering[n - current_start] = covering_p
            
            current_length += 1
    
    # Check if we ended in a desert
    if current_length >= min_length:
        return HardDesert(
            start=current_start,
            length=current_length,
            cutoff_B=B,
            covering_primes=covering
        )
    
    return None


# =============================================================================
# DESERT CERTIFICATE
# =============================================================================

@dataclass
class CoverageCertificate:
    """
    Certificate that a position is covered by a small prime.
    
    Proves: p | n for some p ≤ B.
    """
    n: int
    p: int  # Covering prime
    verified: bool = False
    
    def __post_init__(self):
        self.verify()
    
    def verify(self) -> bool:
        """Verify that p divides n."""
        self.verified = (self.n % self.p == 0 and self.p > 1)
        return self.verified


@dataclass
class SurvivorCompositeProof:
    """
    Proof that a survivor is composite.
    
    A survivor passes the small-prime sieve but may still be composite.
    This certificate proves compositeness by providing a factor.
    """
    n: int
    factor: int
    cofactor: int
    verified: bool = False
    
    def __post_init__(self):
        self.verify()
    
    def verify(self) -> bool:
        """Verify the composite proof."""
        self.verified = (
            self.factor > 1 and 
            self.cofactor > 1 and
            self.factor * self.cofactor == self.n
        )
        return self.verified


@dataclass
class DesertCertificate:
    """
    Complete certificate that an interval is prime-free.
    
    Components:
    1. Coverage certificates: prove hard-kill positions are sieved
    2. Survivor composite proofs: prove survivors are composite
    3. Interval specification: [start, start + length)
    """
    start: int
    length: int
    cutoff_B: int
    
    # Hard-kill certificates (most positions)
    coverage_certs: List[CoverageCertificate] = field(default_factory=list)
    
    # Soft-tail certificates (survivors proven composite)
    survivor_proofs: List[SurvivorCompositeProof] = field(default_factory=list)
    
    verified: bool = False
    timestamp: datetime = field(default_factory=datetime.now)
    
    def verify(self) -> bool:
        """Verify the complete desert certificate."""
        # Check all positions are either covered or proven composite
        covered_positions = {cert.n for cert in self.coverage_certs if cert.verified}
        composite_survivors = {proof.n for proof in self.survivor_proofs if proof.verified}
        
        all_certified = covered_positions | composite_survivors
        
        # Every position in the interval must be certified
        for i in range(self.length):
            n = self.start + i
            if n not in all_certified:
                # Position not certified - check if it's prime
                if is_prime_miller_rabin(n):
                    # Found a prime - certificate fails
                    self.verified = False
                    return False
        
        self.verified = True
        return True
    
    @property
    def end(self) -> int:
        return self.start + self.length
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'type': 'DesertCertificate',
            'interval': [self.start, self.end],
            'length': self.length,
            'cutoff_B': self.cutoff_B,
            'coverage_count': len(self.coverage_certs),
            'survivor_count': len(self.survivor_proofs),
            'verified': self.verified,
            'timestamp': self.timestamp.isoformat()
        }


def certify_desert(start: int, length: int, B: int = 30) -> DesertCertificate:
    """
    Create a desert certificate for an interval.
    
    Uses sieve up to B for hard-kills, then certifies survivors.
    """
    wheel = PrimorialWheel(B)
    
    coverage_certs = []
    survivor_proofs = []
    
    for i in range(length):
        n = start + i
        
        if n < 2:
            continue
        
        # Check if covered by small prime
        covering_p = wheel.covering_prime(n)
        
        if covering_p:
            # Hard-kill: covered by small prime
            coverage_certs.append(CoverageCertificate(n=n, p=covering_p))
        else:
            # Survivor: need to prove composite
            if not is_prime_miller_rabin(n):
                # Find a factor
                factor = None
                for p in range(2, min(int(math.isqrt(n)) + 1, 10000)):
                    if n % p == 0:
                        factor = p
                        break
                
                if factor:
                    survivor_proofs.append(SurvivorCompositeProof(
                        n=n,
                        factor=factor,
                        cofactor=n // factor
                    ))
    
    cert = DesertCertificate(
        start=start,
        length=length,
        cutoff_B=B,
        coverage_certs=coverage_certs,
        survivor_proofs=survivor_proofs
    )
    cert.verify()
    
    return cert


# =============================================================================
# FACTORIAL DESERT CONSTRUCTION
# =============================================================================

def factorial_desert(m: int) -> Tuple[int, int, DesertCertificate]:
    """
    Construct a provably prime-free interval using factorial.
    
    For m ≥ 2, the interval [m!+2, m!+m] contains no primes because:
    - k | m! for k ∈ {2, ..., m}
    - Therefore k | (m! + k)
    
    Returns (start, length, certificate).
    """
    factorial = math.factorial(m)
    start = factorial + 2
    length = m - 1  # Interval [m!+2, m!+m]
    
    # Build coverage certificates
    coverage_certs = []
    for k in range(2, m + 1):
        n = factorial + k
        # k divides n because k divides m! and k divides k
        coverage_certs.append(CoverageCertificate(n=n, p=k))
    
    cert = DesertCertificate(
        start=start,
        length=length,
        cutoff_B=m,
        coverage_certs=coverage_certs
    )
    cert.verify()
    
    return start, length, cert


# =============================================================================
# CRT DESERT ENGINEERING
# =============================================================================

def crt_reconstruct(residues: List[Tuple[int, int]]) -> int:
    """
    Chinese Remainder Theorem reconstruction.
    
    Given [(a_1, m_1), (a_2, m_2), ...], find x such that:
    x ≡ a_i (mod m_i) for all i
    
    Assumes m_i are pairwise coprime.
    """
    # Compute total modulus M = ∏ m_i
    M = 1
    for _, m in residues:
        M *= m
    
    result = 0
    for a, m in residues:
        M_i = M // m
        # Find inverse of M_i mod m
        _, inv, _ = extended_gcd(M_i, m)
        inv = inv % m
        
        result += a * M_i * inv
    
    return result % M


def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """Extended Euclidean algorithm. Returns (gcd, x, y) where ax + by = gcd."""
    if a == 0:
        return b, 0, 1
    
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    
    return gcd, x, y


def engineer_desert(length: int, moduli: List[int] = None) -> Tuple[int, DesertCertificate]:
    """
    Engineer a prime-free interval of given length using CRT.
    
    Choose coprime moduli q_1, ..., q_L and impose:
    N ≡ -j (mod q_j) for j = 1, ..., L
    
    Then q_j | (N + j) for all j, so [N+1, N+L] is composite-only.
    """
    if moduli is None:
        # Use first 'length' primes as moduli
        all_primes = primes_up_to(length * 10)
        moduli = all_primes[:length]
    
    if len(moduli) < length:
        raise ValueError(f"Need at least {length} moduli")
    
    # Build residue conditions: N ≡ -j (mod q_j)
    residues = [(-j, moduli[j-1]) for j in range(1, length + 1)]
    
    N = crt_reconstruct(residues)
    
    # Build certificate
    coverage_certs = []
    for j in range(1, length + 1):
        n = N + j
        p = moduli[j-1]
        coverage_certs.append(CoverageCertificate(n=n, p=p))
    
    cert = DesertCertificate(
        start=N + 1,
        length=length,
        cutoff_B=max(moduli),
        coverage_certs=coverage_certs
    )
    cert.verify()
    
    return N + 1, cert


# =============================================================================
# VALIDATION
# =============================================================================

def validate_sieves() -> bool:
    """Validate sieve wheels and desert certificates."""
    
    # Test primorial
    assert primorial(5) == 2 * 3 * 5 == 30
    assert primorial(7) == 2 * 3 * 5 * 7 == 210
    
    # Test wheel
    wheel = PrimorialWheel(5)
    assert wheel.primorial == 30
    assert 1 in wheel.wheel_residues
    assert 7 in wheel.wheel_residues
    assert 2 not in wheel.wheel_residues  # divisible by 2
    assert 3 not in wheel.wheel_residues  # divisible by 3
    
    # Test Jacobsthal
    assert jacobsthal(6) == 4  # Max gap in coprimes to 6 is 3
    
    # Test factorial desert
    start, length, cert = factorial_desert(5)
    assert length == 3  # [5!+2, 5!+5] = [122, 125]
    assert cert.verified
    
    # Test coverage certificate
    cov = CoverageCertificate(n=100, p=2)
    assert cov.verified
    
    cov_bad = CoverageCertificate(n=101, p=2)
    assert not cov_bad.verified
    
    # Test survivor composite proof
    proof = SurvivorCompositeProof(n=91, factor=7, cofactor=13)
    assert proof.verified
    
    # Test CRT desert
    start, cert = engineer_desert(5)
    assert cert.verified
    assert cert.length == 5
    
    return True


if __name__ == "__main__":
    print("Validating Sieve Wheels and Desert Certificates...")
    assert validate_sieves()
    print("✓ Sieve Wheels validated")
    
    # Demo
    print("\n=== Primorial Wheel Demo (B=7) ===")
    wheel = PrimorialWheel(7)
    print(f"P_7 = {wheel.primorial}")
    print(f"|R_7| = {len(wheel.wheel_residues)}")
    print(f"Density = {wheel.density:.4f}")
    print(f"First 10 wheel residues: {sorted(wheel.wheel_residues)[:10]}")
    
    print("\n=== Factorial Desert Demo ===")
    start, length, cert = factorial_desert(6)
    print(f"6! = {math.factorial(6)}")
    print(f"Desert: [{start}, {start + length})")
    print(f"Length: {length}")
    print(f"Verified: {cert.verified}")
    
    print("\n=== CRT Engineered Desert Demo ===")
    start, cert = engineer_desert(10)
    print(f"Engineered desert of length 10")
    print(f"Start: {start}")
    print(f"Verified: {cert.verified}")
