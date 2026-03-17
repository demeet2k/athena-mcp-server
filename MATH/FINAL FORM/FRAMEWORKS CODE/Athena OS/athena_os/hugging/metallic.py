"""
ATHENA OS - Quantum Hugging Framework
=====================================
Metallic Spectrum: Metallic Means and Ratios

From The_Quantum_Hugging_Framework.docx §2.3:

METALLIC MEANS:
    Family of ratios (δₙ)_{n≥0} solving quadratic recurrences:
    
    δ₁ = φ⁻¹ ≈ 0.618 (Golden)
    δ₂ = √2 - 1 ≈ 0.414 (Silver)
    δ₃ = (√13 - 3)/2 ≈ 0.303 (Bronze)
    
    For large n: δₙ ≈ n + 1/n

FRACTIONAL EXPONENTS:
    δₙᵏ with k ∈ ℚ yields rich ratio spectrum
    for geometric encoders with tunable convergence

METALLIC PHASES:
    Each metallic mean defines a phase with distinct
    spectral signatures and convergence properties
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum, auto
import math


# =============================================================================
# METALLIC CONSTANTS
# =============================================================================

# Golden ratio and inverse
PHI = (1 + math.sqrt(5)) / 2      # φ ≈ 1.618
PHI_INV = PHI - 1                  # φ⁻¹ ≈ 0.618

# Silver ratio
SILVER = 1 + math.sqrt(2)          # δ_Ag ≈ 2.414
SILVER_INV = math.sqrt(2) - 1      # ≈ 0.414

# Bronze ratio
BRONZE = (3 + math.sqrt(13)) / 2   # ≈ 3.303
BRONZE_INV = (math.sqrt(13) - 3) / 2  # ≈ 0.303


# =============================================================================
# METALLIC MEAN
# =============================================================================

class MetallicType(Enum):
    """Types of metallic means."""
    
    GOLDEN = 1       # n = 1
    SILVER = 2       # n = 2
    BRONZE = 3       # n = 3
    COPPER = 4       # n = 4
    NICKEL = 5       # n = 5
    CUSTOM = 0       # Custom n


@dataclass
class MetallicMean:
    """
    Metallic mean of index n.
    
    Solves x² - nx - 1 = 0
    δₙ = (n + √(n² + 4)) / 2
    """
    
    n: int = 1
    
    @property
    def value(self) -> float:
        """Compute metallic mean δₙ."""
        return (self.n + math.sqrt(self.n**2 + 4)) / 2
    
    @property
    def inverse(self) -> float:
        """Compute inverse δₙ⁻¹."""
        return 1.0 / self.value
    
    @property
    def conjugate(self) -> float:
        """Compute conjugate (n - √(n² + 4)) / 2."""
        return (self.n - math.sqrt(self.n**2 + 4)) / 2
    
    def power(self, k: float) -> float:
        """Compute δₙᵏ."""
        return self.value ** k
    
    def inverse_power(self, k: float) -> float:
        """Compute δₙ⁻ᵏ."""
        return self.inverse ** k
    
    def ratio(self) -> float:
        """Ratio for geometric encoder (inverse)."""
        return self.inverse
    
    def continued_fraction_period(self) -> List[int]:
        """Get periodic continued fraction."""
        # Metallic means have period [n; n, n, n, ...]
        return [self.n]
    
    @property
    def metallic_type(self) -> MetallicType:
        """Get metallic type."""
        if self.n == 1:
            return MetallicType.GOLDEN
        elif self.n == 2:
            return MetallicType.SILVER
        elif self.n == 3:
            return MetallicType.BRONZE
        elif self.n == 4:
            return MetallicType.COPPER
        elif self.n == 5:
            return MetallicType.NICKEL
        else:
            return MetallicType.CUSTOM
    
    def __repr__(self) -> str:
        return f"δ_{self.n} = {self.value:.6f}"
    
    # Factory methods
    @classmethod
    def golden(cls) -> 'MetallicMean':
        """Golden mean (n=1)."""
        return cls(n=1)
    
    @classmethod
    def silver(cls) -> 'MetallicMean':
        """Silver mean (n=2)."""
        return cls(n=2)
    
    @classmethod
    def bronze(cls) -> 'MetallicMean':
        """Bronze mean (n=3)."""
        return cls(n=3)


# =============================================================================
# METALLIC SPECTRUM
# =============================================================================

@dataclass
class MetallicSpectrum:
    """
    Spectrum of metallic means (δₙ)_{n≥0}.
    
    Provides a family of ratios for geometric encoders.
    """
    
    max_n: int = 10
    means: Dict[int, MetallicMean] = field(default_factory=dict)
    
    def __post_init__(self):
        for n in range(1, self.max_n + 1):
            self.means[n] = MetallicMean(n=n)
    
    def get(self, n: int) -> MetallicMean:
        """Get metallic mean of index n."""
        if n not in self.means:
            self.means[n] = MetallicMean(n=n)
        return self.means[n]
    
    def ratio_spectrum(self) -> List[float]:
        """Get spectrum of ratios (inverses)."""
        return [self.means[n].ratio() for n in sorted(self.means.keys())]
    
    def convergence_rates(self) -> Dict[int, float]:
        """Get convergence rates for geometric encoders."""
        return {
            n: -math.log(self.means[n].ratio())
            for n in self.means
        }
    
    def select_for_capacity(self, target_capacity: float, 
                           epsilon: float) -> MetallicMean:
        """Select metallic mean for target capacity."""
        best = None
        best_diff = float('inf')
        
        for n, mean in self.means.items():
            # Capacity ≈ log₂(2ε/δ) where δ is based on ratio
            ratio = mean.ratio()
            capacity = math.log2(2 * epsilon / (epsilon * ratio))
            
            diff = abs(capacity - target_capacity)
            if diff < best_diff:
                best = mean
                best_diff = diff
        
        return best or MetallicMean.golden()
    
    def asymptotic_formula(self, n: int) -> float:
        """Asymptotic approximation for large n: δₙ ≈ n + 1/n."""
        return n + 1.0 / n
    
    def asymptotic_error(self, n: int) -> float:
        """Error of asymptotic formula."""
        exact = self.get(n).value
        approx = self.asymptotic_formula(n)
        return abs(exact - approx) / exact


# =============================================================================
# FRACTIONAL METALLIC POWERS
# =============================================================================

@dataclass
class FractionalPower:
    """
    Fractional power δₙᵏ of metallic mean.
    """
    
    mean: MetallicMean
    exponent: float
    
    @property
    def value(self) -> float:
        """Compute δₙᵏ."""
        return self.mean.power(self.exponent)
    
    @property
    def ratio(self) -> float:
        """As ratio for encoders."""
        return self.value if self.value < 1 else 1.0 / self.value
    
    def convergence_order(self) -> float:
        """Order of convergence for geometric series."""
        r = self.ratio
        if r >= 1:
            return 0.0
        return -1.0 / math.log(r)


@dataclass
class RatioSpectrum:
    """
    Rich spectrum of ratios from fractional metallic powers.
    """
    
    spectrum: MetallicSpectrum = field(default_factory=MetallicSpectrum)
    exponents: List[float] = field(default_factory=lambda: [0.5, 2/3, 1.0, 1.5, 2.0])
    
    def generate_ratios(self) -> List[Tuple[int, float, float]]:
        """Generate all (n, k, δₙᵏ) tuples."""
        ratios = []
        for n in self.spectrum.means:
            mean = self.spectrum.get(n)
            for k in self.exponents:
                fp = FractionalPower(mean, k)
                ratios.append((n, k, fp.ratio))
        return ratios
    
    def sorted_by_ratio(self) -> List[Tuple[int, float, float]]:
        """Get ratios sorted by value."""
        return sorted(self.generate_ratios(), key=lambda x: x[2])
    
    def find_closest(self, target: float) -> Tuple[int, float, float]:
        """Find (n, k) giving closest ratio to target."""
        best = None
        best_diff = float('inf')
        
        for n, k, r in self.generate_ratios():
            diff = abs(r - target)
            if diff < best_diff:
                best = (n, k, r)
                best_diff = diff
        
        return best


# =============================================================================
# METALLIC PHASE
# =============================================================================

@dataclass
class MetallicPhase:
    """
    A metallic phase with distinct properties.
    """
    
    mean: MetallicMean
    
    @property
    def name(self) -> str:
        """Phase name."""
        names = {
            1: "Golden",
            2: "Silver", 
            3: "Bronze",
            4: "Copper",
            5: "Nickel"
        }
        return names.get(self.mean.n, f"Metal-{self.mean.n}")
    
    @property
    def convergence_rate(self) -> float:
        """Rate of geometric convergence."""
        return -math.log(self.mean.ratio())
    
    @property
    def spectral_signature(self) -> List[float]:
        """Characteristic spectral values."""
        m = self.mean
        return [
            m.value,
            m.inverse,
            m.value ** 2,
            m.conjugate
        ]
    
    def series_sum(self, a: float, n_terms: int) -> float:
        """Sum of geometric series a·Σδ⁻ᵏ for k=0 to n."""
        r = self.mean.ratio()
        if abs(r) >= 1:
            return a * n_terms
        return a * (1 - r**(n_terms+1)) / (1 - r)
    
    def packets_needed(self, S: float, epsilon: float) -> int:
        """Estimate packets needed to encode S."""
        r = self.mean.ratio()
        if r >= 1:
            return max(1, int(math.ceil(abs(S) / epsilon)))
        
        # Geometric series: need Σr^k ≥ |S|/(ε(1-r))
        threshold = abs(S) / (epsilon * (1 - r))
        if threshold <= 1:
            return 1
        
        return int(math.ceil(math.log(threshold) / math.log(1/r)))


# =============================================================================
# VALIDATION
# =============================================================================

def validate_metallic() -> bool:
    """Validate metallic spectrum module."""
    
    # Test MetallicMean
    golden = MetallicMean.golden()
    assert abs(golden.value - PHI) < 1e-10
    assert abs(golden.inverse - PHI_INV) < 1e-10
    
    silver = MetallicMean.silver()
    assert abs(silver.value - SILVER) < 1e-10
    
    # Test powers
    assert abs(golden.power(2) - PHI**2) < 1e-10
    assert abs(golden.power(0.5) - math.sqrt(PHI)) < 1e-10
    
    # Test MetallicSpectrum
    spectrum = MetallicSpectrum(max_n=5)
    assert len(spectrum.means) == 5
    
    ratios = spectrum.ratio_spectrum()
    assert len(ratios) == 5
    assert ratios[0] > ratios[1] > ratios[2]  # Decreasing
    
    # Test asymptotic
    for n in [10, 50, 100]:
        error = spectrum.asymptotic_error(n)
        assert error < 0.01 if n >= 50 else True
    
    # Test FractionalPower
    fp = FractionalPower(golden, 0.5)
    assert abs(fp.value - math.sqrt(PHI)) < 1e-10
    
    # Test RatioSpectrum
    rs = RatioSpectrum()
    ratios = rs.generate_ratios()
    assert len(ratios) > 0
    
    closest = rs.find_closest(0.5)
    assert closest is not None
    
    # Test MetallicPhase
    phase = MetallicPhase(golden)
    assert phase.name == "Golden"
    assert phase.convergence_rate > 0
    
    return True


if __name__ == "__main__":
    print("Validating Quantum Hugging Metallic Module...")
    assert validate_metallic()
    print("✓ Metallic module validated")
    
    # Demo
    print("\n=== Metallic Spectrum Demo ===")
    
    print("\nMetallic Means:")
    for n in range(1, 6):
        mean = MetallicMean(n=n)
        print(f"  n={n}: δ = {mean.value:.6f}, δ⁻¹ = {mean.inverse:.6f}")
    
    # Phases
    print("\nMetallic Phases:")
    for n in range(1, 4):
        phase = MetallicPhase(MetallicMean(n=n))
        print(f"  {phase.name}:")
        print(f"    Convergence rate: {phase.convergence_rate:.4f}")
        print(f"    Packets for S=10, ε=0.5: {phase.packets_needed(10, 0.5)}")
    
    # Asymptotic accuracy
    print("\nAsymptotic Formula δₙ ≈ n + 1/n:")
    spectrum = MetallicSpectrum(max_n=100)
    for n in [5, 10, 50, 100]:
        error = spectrum.asymptotic_error(n)
        print(f"  n={n}: relative error = {error:.6f}")
    
    # Ratio spectrum
    print("\nFractional Power Ratios (sorted):")
    rs = RatioSpectrum(exponents=[0.5, 1.0, 2.0])
    for n, k, r in rs.sorted_by_ratio()[:8]:
        print(f"  δ_{n}^{k:.1f} = {r:.4f}")
