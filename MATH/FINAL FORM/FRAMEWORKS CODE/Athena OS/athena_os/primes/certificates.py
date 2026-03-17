"""
ATHENA OS - Prime Certificates
==============================
Certificate types for verified arithmetic claims.

The system asserts truth only through certificate objects:
- PrimeCertificate: Verifiable proof that p is prime
- FactorCertificate: Verifiable witness that d divides n
- ValuationCertificate: Proof of exact prime power multiplicity
- FactorizationLedger: Complete factorization proof
- DesertCertificate: Proof that interval is prime-free
- ConstellationCertificate: Proof that pattern is all primes
- PrimePowerCertificate: Proof of exact prime power

All other computed objects (scores, signals, peaks, coherence) are
explicitly labeled as SIGNALS and never asserted as truth.

The Truth Barrier:
- Tier 1: Identities (exact equalities)
- Tier 2: Signals (bounded observables for routing)
- Tier 3: Certificates (verifiable proof objects - ONLY tier for truth)
"""

from __future__ import annotations
from enum import IntEnum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Set
from datetime import datetime
import hashlib
import math


# =============================================================================
# TIER CLASSIFICATION
# =============================================================================

class Tier(IntEnum):
    """Epistemic tier classification."""
    IDENTITY = 1    # Exact equalities/propositions
    SIGNAL = 2      # Bounded observables (never asserts truth)
    CERTIFICATE = 3 # Verifiable proof objects (only tier for truth)


class CertificateType(IntEnum):
    """Types of arithmetic certificates."""
    PRIME = 0
    FACTOR = 1
    VALUATION = 2
    FACTORIZATION = 3
    DESERT = 4
    CONSTELLATION = 5
    PRIME_POWER = 6


# =============================================================================
# PRIMALITY TESTING
# =============================================================================

def is_prime_naive(n: int) -> bool:
    """Naive primality test for small numbers."""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(math.isqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True


def miller_rabin_witness(n: int, a: int) -> bool:
    """
    Miller-Rabin witness test.
    
    Returns True if a is a witness for n being composite.
    Returns False if n passes the test for base a.
    """
    if n < 2:
        return True
    if n == 2:
        return False
    if n % 2 == 0:
        return True
    
    # Write n-1 = 2^s * d
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    
    # Compute a^d mod n
    x = pow(a, d, n)
    
    if x == 1 or x == n - 1:
        return False
    
    for _ in range(s - 1):
        x = pow(x, 2, n)
        if x == n - 1:
            return False
    
    return True


def is_prime_miller_rabin(n: int, witnesses: List[int] = None) -> bool:
    """
    Deterministic Miller-Rabin primality test.
    
    For n < 3,317,044,064,679,887,385,961,981, the witnesses
    [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37] are sufficient.
    """
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    
    # Sufficient witnesses for deterministic test
    if witnesses is None:
        if n < 2047:
            witnesses = [2]
        elif n < 1373653:
            witnesses = [2, 3]
        elif n < 9080191:
            witnesses = [31, 73]
        elif n < 25326001:
            witnesses = [2, 3, 5]
        elif n < 3215031751:
            witnesses = [2, 3, 5, 7]
        else:
            witnesses = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
    
    for a in witnesses:
        if a >= n:
            continue
        if miller_rabin_witness(n, a):
            return False
    
    return True


# =============================================================================
# PRIME CERTIFICATE
# =============================================================================

@dataclass
class PrimeCertificate:
    """
    Verifiable proof that p is prime.
    
    Contains the witnesses used and can be independently verified.
    """
    p: int
    witnesses: List[int]
    verified: bool = False
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        self.verify()
    
    def verify(self) -> bool:
        """Verify the primality certificate."""
        if self.p < 2:
            self.verified = False
            return False
        
        # Use Miller-Rabin with the stored witnesses
        self.verified = is_prime_miller_rabin(self.p, self.witnesses)
        return self.verified
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'type': 'PrimeCertificate',
            'p': self.p,
            'witnesses': self.witnesses,
            'verified': self.verified,
            'timestamp': self.timestamp.isoformat()
        }
    
    @property
    def hash(self) -> str:
        """Unique hash for the certificate."""
        data = f"PRIME:{self.p}:{self.witnesses}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]


def create_prime_certificate(p: int) -> Optional[PrimeCertificate]:
    """
    Create a prime certificate if p is prime.
    
    Returns None if p is not prime.
    """
    # Determine appropriate witnesses
    if p < 2047:
        witnesses = [2]
    elif p < 1373653:
        witnesses = [2, 3]
    elif p < 9080191:
        witnesses = [31, 73]
    else:
        witnesses = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
    
    cert = PrimeCertificate(p=p, witnesses=witnesses)
    return cert if cert.verified else None


# =============================================================================
# FACTOR CERTIFICATE
# =============================================================================

@dataclass
class FactorCertificate:
    """
    Verifiable witness that d divides n.
    
    The witness is the quotient q such that n = d * q.
    """
    n: int
    d: int
    q: int = 0  # Quotient: n = d * q
    verified: bool = False
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        self.verify()
    
    def verify(self) -> bool:
        """Verify the factor certificate."""
        if self.d < 1 or self.d > self.n:
            self.verified = False
            return False
        
        if self.n % self.d == 0:
            self.q = self.n // self.d
            self.verified = True
        else:
            self.verified = False
        
        return self.verified
    
    @property
    def is_nontrivial(self) -> bool:
        """Check if this is a non-trivial factor (1 < d < n)."""
        return self.verified and 1 < self.d < self.n
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'type': 'FactorCertificate',
            'n': self.n,
            'd': self.d,
            'q': self.q,
            'verified': self.verified,
            'nontrivial': self.is_nontrivial,
            'timestamp': self.timestamp.isoformat()
        }


# =============================================================================
# VALUATION CERTIFICATE  
# =============================================================================

@dataclass
class ValuationCertificate:
    """
    Verifiable proof of exact prime power multiplicity.
    
    Proves that v_p(n) = alpha, meaning p^alpha divides n
    but p^(alpha+1) does not.
    """
    n: int
    p: int
    alpha: int  # The valuation v_p(n)
    prime_cert: Optional[PrimeCertificate] = None
    verified: bool = False
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        self.verify()
    
    def verify(self) -> bool:
        """Verify the valuation certificate."""
        # First verify p is prime
        if self.prime_cert is None:
            self.prime_cert = create_prime_certificate(self.p)
        
        if self.prime_cert is None or not self.prime_cert.verified:
            self.verified = False
            return False
        
        # Compute actual valuation
        actual_alpha = 0
        m = self.n
        while m > 0 and m % self.p == 0:
            actual_alpha += 1
            m //= self.p
        
        self.verified = (actual_alpha == self.alpha)
        return self.verified
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'type': 'ValuationCertificate',
            'n': self.n,
            'p': self.p,
            'alpha': self.alpha,
            'verified': self.verified,
            'prime_cert': self.prime_cert.to_dict() if self.prime_cert else None,
            'timestamp': self.timestamp.isoformat()
        }


def compute_valuation(n: int, p: int) -> int:
    """Compute v_p(n) = max{k : p^k | n}."""
    if n == 0:
        return float('inf')
    alpha = 0
    while n % p == 0:
        alpha += 1
        n //= p
    return alpha


# =============================================================================
# PRIME POWER CERTIFICATE
# =============================================================================

@dataclass
class PrimePowerCertificate:
    """
    Verifiable proof that n = p^k for some prime p.
    """
    n: int
    p: int
    k: int
    prime_cert: Optional[PrimeCertificate] = None
    verified: bool = False
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        self.verify()
    
    def verify(self) -> bool:
        """Verify the prime power certificate."""
        # Verify p is prime
        if self.prime_cert is None:
            self.prime_cert = create_prime_certificate(self.p)
        
        if self.prime_cert is None or not self.prime_cert.verified:
            self.verified = False
            return False
        
        # Verify n = p^k
        self.verified = (self.p ** self.k == self.n)
        return self.verified
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'type': 'PrimePowerCertificate',
            'n': self.n,
            'p': self.p,
            'k': self.k,
            'verified': self.verified,
            'prime_cert': self.prime_cert.to_dict() if self.prime_cert else None,
            'timestamp': self.timestamp.isoformat()
        }


def detect_prime_power(n: int) -> Optional[Tuple[int, int]]:
    """
    Detect if n is a prime power.
    
    Returns (p, k) if n = p^k for prime p, else None.
    """
    if n < 2:
        return None
    
    # Check if n is itself prime
    if is_prime_miller_rabin(n):
        return (n, 1)
    
    # Check for k-th roots for k = 2, 3, ...
    max_k = int(math.log2(n)) + 1
    
    for k in range(2, max_k + 1):
        # Compute floor(n^(1/k))
        root = int(round(n ** (1/k)))
        
        # Check root and neighbors
        for r in [root - 1, root, root + 1]:
            if r < 2:
                continue
            if r ** k == n:
                if is_prime_miller_rabin(r):
                    return (r, k)
    
    return None


# =============================================================================
# FACTORIZATION ENTRY
# =============================================================================

@dataclass
class FactorizationEntry:
    """
    A single entry in a factorization: (p, alpha) meaning p^alpha.
    """
    p: int
    alpha: int
    prime_cert: Optional[PrimeCertificate] = None
    valuation_cert: Optional[ValuationCertificate] = None
    
    @property
    def value(self) -> int:
        """The value p^alpha."""
        return self.p ** self.alpha
    
    def verify(self, n: int) -> bool:
        """Verify this entry against n."""
        # Verify prime
        if self.prime_cert is None:
            self.prime_cert = create_prime_certificate(self.p)
        if not self.prime_cert or not self.prime_cert.verified:
            return False
        
        # Verify valuation
        if self.valuation_cert is None:
            self.valuation_cert = ValuationCertificate(n, self.p, self.alpha)
        
        return self.valuation_cert.verified
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'p': self.p,
            'alpha': self.alpha,
            'value': self.value,
            'prime_verified': self.prime_cert.verified if self.prime_cert else False,
            'valuation_verified': self.valuation_cert.verified if self.valuation_cert else False
        }


# =============================================================================
# FACTORIZATION LEDGER
# =============================================================================

@dataclass
class FactorizationLedger:
    """
    Complete factorization proof with the product invariant.
    
    Maintains: n₀ = (∏ p^α) · R
    
    A run is correct iff it ends with R=1 and every p is prime-certified.
    """
    n: int
    entries: List[FactorizationEntry] = field(default_factory=list)
    remainder: int = 0
    verified: bool = False
    complete: bool = False
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        self.remainder = self.n
        self._compute_product()
    
    def _compute_product(self) -> int:
        """Compute current factored product."""
        product = 1
        for entry in self.entries:
            product *= entry.value
        return product
    
    def add_factor(self, p: int, alpha: int) -> bool:
        """Add a prime power factor."""
        entry = FactorizationEntry(p=p, alpha=alpha)
        
        # Verify against current remainder
        if not entry.verify(self.remainder):
            return False
        
        self.entries.append(entry)
        
        # Update remainder
        self.remainder //= entry.value
        
        # Check completeness
        if self.remainder == 1:
            self.complete = True
            self.verified = all(e.prime_cert and e.prime_cert.verified 
                              for e in self.entries)
        
        return True
    
    def verify_invariant(self) -> bool:
        """
        Verify the product invariant: n = (∏ p^α) · R
        """
        product = self._compute_product()
        return product * self.remainder == self.n
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'type': 'FactorizationLedger',
            'n': self.n,
            'entries': [e.to_dict() for e in self.entries],
            'remainder': self.remainder,
            'verified': self.verified,
            'complete': self.complete,
            'product_check': self.verify_invariant(),
            'timestamp': self.timestamp.isoformat()
        }
    
    @property
    def factors(self) -> Dict[int, int]:
        """Get factors as {p: alpha} dictionary."""
        return {e.p: e.alpha for e in self.entries}
    
    @property
    def hash(self) -> str:
        """Unique hash for the certificate."""
        factors_str = ",".join(f"{e.p}^{e.alpha}" for e in sorted(self.entries, key=lambda x: x.p))
        data = f"FACTORIZATION:{self.n}:{factors_str}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]


# =============================================================================
# VALIDATION
# =============================================================================

def validate_certificates() -> bool:
    """Validate certificate system."""
    
    # Test prime certificate
    cert2 = create_prime_certificate(2)
    assert cert2 is not None
    assert cert2.verified
    
    cert13 = create_prime_certificate(13)
    assert cert13 is not None
    assert cert13.verified
    
    cert_composite = create_prime_certificate(15)
    assert cert_composite is None
    
    # Test factor certificate
    factor_cert = FactorCertificate(n=100, d=5)
    assert factor_cert.verified
    assert factor_cert.q == 20
    assert factor_cert.is_nontrivial
    
    # Test valuation certificate
    val_cert = ValuationCertificate(n=100, p=2, alpha=2)
    assert val_cert.verified  # 100 = 4 * 25 = 2^2 * 5^2
    
    val_cert2 = ValuationCertificate(n=100, p=5, alpha=2)
    assert val_cert2.verified
    
    # Test prime power detection
    pp = detect_prime_power(27)
    assert pp == (3, 3)
    
    pp2 = detect_prime_power(17)
    assert pp2 == (17, 1)
    
    pp3 = detect_prime_power(12)
    assert pp3 is None
    
    # Test factorization ledger
    ledger = FactorizationLedger(n=100)
    assert ledger.add_factor(2, 2)
    assert ledger.remainder == 25
    assert ledger.add_factor(5, 2)
    assert ledger.remainder == 1
    assert ledger.complete
    assert ledger.verified
    assert ledger.verify_invariant()
    
    return True


if __name__ == "__main__":
    print("Validating Certificate System...")
    assert validate_certificates()
    print("✓ Certificate System validated")
    
    # Demo
    print("\n=== Prime Certificate Demo ===")
    p = 104729  # 10000th prime
    cert = create_prime_certificate(p)
    if cert:
        print(f"Prime {p}: verified={cert.verified}")
        print(f"Witnesses used: {cert.witnesses}")
    
    print("\n=== Factorization Ledger Demo ===")
    n = 360
    ledger = FactorizationLedger(n=n)
    # 360 = 2^3 * 3^2 * 5
    ledger.add_factor(2, 3)
    ledger.add_factor(3, 2)
    ledger.add_factor(5, 1)
    
    print(f"Factorization of {n}:")
    for e in ledger.entries:
        print(f"  {e.p}^{e.alpha} = {e.value}")
    print(f"Complete: {ledger.complete}")
    print(f"Verified: {ledger.verified}")
    print(f"Invariant: {ledger.verify_invariant()}")
