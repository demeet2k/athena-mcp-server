"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                       TEXTURE FUNCTIONAL MODULE                              ║
║                                                                              ║
║  Complexity Measurement, Texture, and κ-Conservation                         ║
║                                                                              ║
║  Core Principle:                                                             ║
║    Each sector has a Texture functional T_α measuring pattern and structure  ║
║    Total complexity κ_tot = κ_+ + κ_- + κ_i + κ_ī is CONSERVED              ║
║                                                                              ║
║  Texture Components:                                                         ║
║    - Algorithmic complexity K(description)                                   ║
║    - Entropy S (phase-space or von Neumann)                                  ║
║    - Coherence measures (off-diagonal structure)                             ║
║    - Pattern density (multi-scale structure)                                 ║
║                                                                              ║
║  Conservation Law:                                                           ║
║    κ_tot(τ) = Σ_α T_α(|ψ_α⟩) = constant                                     ║
║    Complexity is redistributed, not created or destroyed                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Any, Callable
from enum import Enum
import numpy as np
from numpy.typing import NDArray


# ═══════════════════════════════════════════════════════════════════════════════
# TEXTURE TYPES
# ═══════════════════════════════════════════════════════════════════════════════

class TextureType(Enum):
    """Types of Texture measures."""
    ALGORITHMIC = "algorithmic"   # Kolmogorov complexity K
    ENTROPIC = "entropic"         # Entropy S
    COHERENCE = "coherence"       # Off-diagonal structure
    PATTERN = "pattern"           # Multi-scale structure
    COMPOSITE = "composite"       # Weighted combination


class SectorType(Enum):
    """Sector types for Texture."""
    PRIMAL = "primal"       # T_+
    INVERTED = "inverted"   # T_-
    IMAGINARY = "imaginary" # T_i
    CONJUGATE = "conjugate" # T_ī


# ═══════════════════════════════════════════════════════════════════════════════
# ALGORITHMIC COMPLEXITY
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class AlgorithmicComplexity:
    """
    Kolmogorov-like algorithmic complexity measure.
    
    K(x) = length of shortest program that outputs x
    
    Approximated via compression ratio.
    """
    
    def estimate(self, data: bytes) -> float:
        """
        Estimate algorithmic complexity via compression.
        
        K(x) ≈ |compressed(x)|
        """
        import zlib
        if len(data) == 0:
            return 0.0
        compressed = zlib.compress(data, level=9)
        return len(compressed)
    
    def normalized(self, data: bytes) -> float:
        """
        Normalized complexity ratio.
        
        K_norm = |compressed(x)| / |x|
        """
        if len(data) == 0:
            return 0.0
        return self.estimate(data) / len(data)
    
    def from_array(self, arr: NDArray) -> float:
        """Estimate complexity of numpy array."""
        return self.estimate(arr.tobytes())
    
    def from_string(self, s: str) -> float:
        """Estimate complexity of string."""
        return self.estimate(s.encode('utf-8'))


# ═══════════════════════════════════════════════════════════════════════════════
# ENTROPY MEASURES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class EntropyMeasure:
    """
    Entropy measures for Texture quantification.
    """
    
    def shannon(self, probs: NDArray) -> float:
        """
        Shannon entropy H = -Σ p_i log p_i
        """
        probs = np.asarray(probs, dtype=float)
        probs = probs[probs > 1e-15]  # Filter zeros
        return -np.sum(probs * np.log2(probs))
    
    def von_neumann(self, rho: NDArray) -> float:
        """
        Von Neumann entropy S = -Tr(ρ log ρ)
        
        For density matrix ρ.
        """
        eigenvalues = np.linalg.eigvalsh(rho)
        eigenvalues = eigenvalues[eigenvalues > 1e-15]
        return -np.sum(eigenvalues * np.log2(eigenvalues))
    
    def renyi(self, probs: NDArray, alpha: float = 2.0) -> float:
        """
        Rényi entropy H_α = (1/(1-α)) log Σ p_i^α
        """
        if np.abs(alpha - 1.0) < 1e-10:
            return self.shannon(probs)
        probs = np.asarray(probs, dtype=float)
        probs = probs[probs > 1e-15]
        return np.log2(np.sum(probs ** alpha)) / (1 - alpha)
    
    def phase_space(self, wigner: NDArray, dx: float = 1.0) -> float:
        """
        Phase-space entropy from Wigner function.
        
        S_ph = -∫ W(x,p) log |W(x,p)| dx dp
        """
        # Approximate via discrete sum
        w = np.abs(wigner)
        w = w[w > 1e-15]
        return -np.sum(w * np.log(w)) * dx * dx


# ═══════════════════════════════════════════════════════════════════════════════
# COHERENCE MEASURES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class CoherenceMeasure:
    """
    Quantum coherence measures.
    
    Quantifies off-diagonal structure in density matrix.
    """
    
    def l1_coherence(self, rho: NDArray) -> float:
        """
        l₁-norm of coherence.
        
        C_l1(ρ) = Σ_{i≠j} |ρ_{ij}|
        """
        n = rho.shape[0]
        total = 0.0
        for i in range(n):
            for j in range(n):
                if i != j:
                    total += np.abs(rho[i, j])
        return total
    
    def relative_entropy_coherence(self, rho: NDArray) -> float:
        """
        Relative entropy of coherence.
        
        C_RE(ρ) = S(ρ_diag) - S(ρ)
        """
        entropy = EntropyMeasure()
        
        # Diagonal state
        rho_diag = np.diag(np.diag(rho))
        
        s_diag = entropy.von_neumann(rho_diag)
        s_rho = entropy.von_neumann(rho)
        
        return max(0.0, s_diag - s_rho)
    
    def frob_coherence(self, rho: NDArray) -> float:
        """
        Frobenius norm coherence.
        
        C_F(ρ) = ||ρ - ρ_diag||_F
        """
        rho_diag = np.diag(np.diag(rho))
        return np.linalg.norm(rho - rho_diag, 'fro')
    
    def purity(self, rho: NDArray) -> float:
        """
        Purity Tr(ρ²).
        
        Pure state: γ = 1
        Maximally mixed: γ = 1/d
        """
        return np.real(np.trace(rho @ rho))


# ═══════════════════════════════════════════════════════════════════════════════
# PATTERN DENSITY
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class PatternDensity:
    """
    Multi-scale pattern density measure.
    
    Quantifies structured complexity at multiple scales.
    """
    
    def wavelet_entropy(self, signal: NDArray, levels: int = 4) -> float:
        """
        Wavelet entropy across scales.
        
        Measures energy distribution across wavelet levels.
        """
        # Simple Haar wavelet decomposition
        energies = []
        current = signal.copy()
        
        for _ in range(levels):
            if len(current) < 2:
                break
            n = len(current) // 2
            # Approximation and detail
            approx = (current[::2] + current[1::2]) / np.sqrt(2)
            detail = (current[::2] - current[1::2]) / np.sqrt(2)
            
            e_detail = np.sum(detail ** 2)
            energies.append(e_detail)
            current = approx
        
        # Add remaining approximation energy
        energies.append(np.sum(current ** 2))
        
        # Normalize to probabilities
        total_e = sum(energies)
        if total_e < 1e-15:
            return 0.0
        probs = np.array(energies) / total_e
        
        return EntropyMeasure().shannon(probs)
    
    def fractal_dimension(self, signal: NDArray) -> float:
        """
        Estimate fractal dimension via box-counting.
        """
        # Higuchi fractal dimension approximation
        n = len(signal)
        if n < 10:
            return 1.0
        
        k_max = min(10, n // 4)
        lk = []
        
        for k in range(1, k_max + 1):
            lengths = []
            for m in range(1, k + 1):
                idx = np.arange(m - 1, n, k)
                if len(idx) < 2:
                    continue
                subsig = signal[idx]
                L = np.sum(np.abs(np.diff(subsig))) * (n - 1) / (k * len(idx) * k)
                lengths.append(L)
            if lengths:
                lk.append(np.mean(lengths))
            else:
                lk.append(1e-10)
        
        # Linear regression in log-log
        ks = np.arange(1, len(lk) + 1)
        log_k = np.log(ks)
        log_l = np.log(np.array(lk) + 1e-15)
        
        if len(log_k) < 2:
            return 1.0
        
        slope = np.polyfit(log_k, log_l, 1)[0]
        return -slope


# ═══════════════════════════════════════════════════════════════════════════════
# SECTOR TEXTURE FUNCTIONAL
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SectorTexture:
    """
    Texture functional T_α for a single sector.
    
    T_α(|ψ_α⟩) = weighted combination of:
    - Algorithmic complexity
    - Entropy
    - Coherence
    - Pattern density
    """
    sector: SectorType
    weights: Dict[TextureType, float] = field(default_factory=lambda: {
        TextureType.ALGORITHMIC: 0.3,
        TextureType.ENTROPIC: 0.3,
        TextureType.COHERENCE: 0.2,
        TextureType.PATTERN: 0.2
    })
    
    def compute(self, 
                psi: NDArray,
                rho: Optional[NDArray] = None) -> float:
        """
        Compute Texture functional for sector state.
        """
        texture = 0.0
        
        # Algorithmic complexity
        if TextureType.ALGORITHMIC in self.weights:
            kc = AlgorithmicComplexity()
            k = kc.from_array(psi)
            texture += self.weights[TextureType.ALGORITHMIC] * k
        
        # Entropic
        if TextureType.ENTROPIC in self.weights:
            probs = np.abs(psi) ** 2
            probs = probs / (np.sum(probs) + 1e-15)
            s = EntropyMeasure().shannon(probs)
            texture += self.weights[TextureType.ENTROPIC] * s
        
        # Coherence (if density matrix provided)
        if TextureType.COHERENCE in self.weights and rho is not None:
            c = CoherenceMeasure().l1_coherence(rho)
            texture += self.weights[TextureType.COHERENCE] * c
        
        # Pattern density
        if TextureType.PATTERN in self.weights:
            real_part = np.real(psi).flatten()
            if len(real_part) >= 4:
                p = PatternDensity().wavelet_entropy(real_part)
                texture += self.weights[TextureType.PATTERN] * p
        
        return texture
    
    @classmethod
    def primal_texture(cls) -> 'SectorTexture':
        """Texture functional for Primal sector (matter)."""
        return cls(SectorType.PRIMAL, {
            TextureType.ALGORITHMIC: 0.4,
            TextureType.ENTROPIC: 0.2,
            TextureType.COHERENCE: 0.1,
            TextureType.PATTERN: 0.3
        })
    
    @classmethod
    def imaginary_texture(cls) -> 'SectorTexture':
        """Texture functional for Imaginary sector (wave)."""
        return cls(SectorType.IMAGINARY, {
            TextureType.ALGORITHMIC: 0.2,
            TextureType.ENTROPIC: 0.3,
            TextureType.COHERENCE: 0.4,
            TextureType.PATTERN: 0.1
        })


# ═══════════════════════════════════════════════════════════════════════════════
# COMPLEXITY BUDGET
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ComplexityBudget:
    """
    Global complexity budget κ.
    
    κ_tot = κ_+ + κ_- + κ_i + κ_ī = constant
    
    Complexity is redistributed, not created or destroyed.
    """
    kappa_primal: float = 0.25
    kappa_inverted: float = 0.25
    kappa_imaginary: float = 0.25
    kappa_conjugate: float = 0.25
    
    @property
    def total(self) -> float:
        """Total complexity κ_tot."""
        return (self.kappa_primal + self.kappa_inverted + 
                self.kappa_imaginary + self.kappa_conjugate)
    
    def normalize(self) -> 'ComplexityBudget':
        """Normalize to sum to 1."""
        t = self.total
        if t < 1e-15:
            return ComplexityBudget()
        return ComplexityBudget(
            self.kappa_primal / t,
            self.kappa_inverted / t,
            self.kappa_imaginary / t,
            self.kappa_conjugate / t
        )
    
    def transfer(self, from_sector: SectorType, to_sector: SectorType,
                 amount: float) -> 'ComplexityBudget':
        """
        Transfer complexity between sectors (conserving total).
        """
        kappas = {
            SectorType.PRIMAL: self.kappa_primal,
            SectorType.INVERTED: self.kappa_inverted,
            SectorType.IMAGINARY: self.kappa_imaginary,
            SectorType.CONJUGATE: self.kappa_conjugate
        }
        
        # Clamp transfer to available
        actual = min(amount, kappas[from_sector])
        
        kappas[from_sector] -= actual
        kappas[to_sector] += actual
        
        return ComplexityBudget(
            kappas[SectorType.PRIMAL],
            kappas[SectorType.INVERTED],
            kappas[SectorType.IMAGINARY],
            kappas[SectorType.CONJUGATE]
        )
    
    def as_dict(self) -> Dict[SectorType, float]:
        """Return as dictionary."""
        return {
            SectorType.PRIMAL: self.kappa_primal,
            SectorType.INVERTED: self.kappa_inverted,
            SectorType.IMAGINARY: self.kappa_imaginary,
            SectorType.CONJUGATE: self.kappa_conjugate
        }


# ═══════════════════════════════════════════════════════════════════════════════
# TEXTURE CONSERVATION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class TextureConservation:
    """
    Enforces texture/complexity conservation law.
    
    dκ_tot/dτ = 0
    """
    initial_total: float = 1.0
    tolerance: float = 1e-6
    
    def check_conservation(self, budget: ComplexityBudget) -> bool:
        """Check if conservation is satisfied."""
        return abs(budget.total - self.initial_total) < self.tolerance
    
    def enforce(self, budget: ComplexityBudget) -> ComplexityBudget:
        """Enforce conservation by rescaling."""
        if self.check_conservation(budget):
            return budget
        
        t = budget.total
        if t < 1e-15:
            return ComplexityBudget(
                self.initial_total / 4,
                self.initial_total / 4,
                self.initial_total / 4,
                self.initial_total / 4
            )
        
        scale = self.initial_total / t
        return ComplexityBudget(
            budget.kappa_primal * scale,
            budget.kappa_inverted * scale,
            budget.kappa_imaginary * scale,
            budget.kappa_conjugate * scale
        )


# ═══════════════════════════════════════════════════════════════════════════════
# TEXTURE BOUND
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class TextureBound:
    """
    Bound on achievable Texture in a sector.
    
    T_α[ρ_α] ≤ T_α^max(κ_α)
    
    Maximum Texture is monotone in allocated complexity.
    """
    sector: SectorType
    
    def max_texture(self, kappa: float) -> float:
        """
        Maximum achievable Texture given κ allocation.
        
        T_max = f(κ) where f is monotone increasing.
        """
        # Simple monotone bound
        return np.log2(1 + kappa * 10)
    
    def coherence_cost(self, coherence_length: float,
                       kappa: float) -> float:
        """
        Cost of maintaining coherence length.
        
        Returns fraction of κ required.
        """
        # Cost grows with coherence length
        return 0.1 * coherence_length ** 2 / (kappa + 0.01)


# ═══════════════════════════════════════════════════════════════════════════════
# POLE BRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class TexturePoleBridge:
    """
    Bridge between Texture functionals and four-pole framework.
    """
    
    @staticmethod
    def cloud_chart() -> str:
        """Texture lives primarily in ☁ chart."""
        return "Texture ↔ ☁ chart: uncertainty, calibration, bounds"
    
    @staticmethod
    def sigma_pole() -> str:
        """Σ-pole manages complexity budget."""
        return "Σ-pole ↔ Stochastic complexity redistribution"
    
    @staticmethod
    def integration() -> str:
        return """
        TEXTURE FUNCTIONALS ↔ FRAMEWORK
        
        Complexity Conservation: κ_tot = Σ κ_α = constant
        
        Sector Textures:
          T_+ (Primal):    Algorithmic + Pattern (matter structure)
          T_- (Inverted):  Entropic (void smoothness)
          T_i (Imaginary): Coherence + Entropy (wave interference)
          T_ī (Conjugate): Algorithmic (memory compression)
        
        Texture Bound: T_α ≤ T_α^max(κ_α)
        
        Links to ☁ chart and Σ-pole for stochastic management.
        """


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def algorithmic_complexity() -> AlgorithmicComplexity:
    """Create algorithmic complexity estimator."""
    return AlgorithmicComplexity()


def entropy_measure() -> EntropyMeasure:
    """Create entropy measure."""
    return EntropyMeasure()


def coherence_measure() -> CoherenceMeasure:
    """Create coherence measure."""
    return CoherenceMeasure()


def pattern_density() -> PatternDensity:
    """Create pattern density measure."""
    return PatternDensity()


def sector_texture(sector: SectorType) -> SectorTexture:
    """Create sector texture functional."""
    return SectorTexture(sector)


def complexity_budget(k_p: float = 0.25, k_inv: float = 0.25,
                      k_im: float = 0.25, k_conj: float = 0.25) -> ComplexityBudget:
    """Create complexity budget."""
    return ComplexityBudget(k_p, k_inv, k_im, k_conj)


def texture_conservation(total: float = 1.0) -> TextureConservation:
    """Create texture conservation enforcer."""
    return TextureConservation(total)


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Enums
    'TextureType',
    'SectorType',
    
    # Complexity Measures
    'AlgorithmicComplexity',
    'EntropyMeasure',
    'CoherenceMeasure',
    'PatternDensity',
    
    # Texture
    'SectorTexture',
    
    # Budget
    'ComplexityBudget',
    'TextureConservation',
    'TextureBound',
    
    # Bridge
    'TexturePoleBridge',
    
    # Functions
    'algorithmic_complexity',
    'entropy_measure',
    'coherence_measure',
    'pattern_density',
    'sector_texture',
    'complexity_budget',
    'texture_conservation',
]
