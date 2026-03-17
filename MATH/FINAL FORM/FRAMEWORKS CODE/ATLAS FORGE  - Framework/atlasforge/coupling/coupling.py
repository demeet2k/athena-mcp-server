"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                       HYBRID COUPLING MODULE                                 ║
║                                                                              ║
║  Discrete + Continuous Phase Coupling, Spectral Invariants, Detectors        ║
║                                                                              ║
║  Core Principle:                                                             ║
║    Hybridization couples discrete structure A with continuous phase φ(θ):    ║
║      H(θ) = A + λ φ(θ)φ(θ)*                                                 ║
║                                                                              ║
║    This is the canonical "Square as matrix, Flower as vector" coupling.      ║
║                                                                              ║
║  Invariants:                                                                 ║
║    - Trace moments: M_n(θ) = Tr(H(θ)^n)                                     ║
║    - Determinant: Δ(θ) = det(H(θ))                                          ║
║    - Spectral gaps: gap_j(θ) = λ_{j+1}(θ) - λ_j(θ)                          ║
║    - Heat traces: ℋ_β(θ) = Tr(e^{-βH(θ)})                                   ║
║                                                                              ║
║  Detectors:                                                                  ║
║    - Eigenvalue spike criterion via resolvent                                ║
║    - Interlacing law for rank-one updates                                    ║
║    - Constraint validation without brute force                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Callable, Any, Union
from enum import Enum, auto
import numpy as np
from numpy.typing import NDArray
import warnings


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE VECTOR - THE CONTINUOUS CHANNEL
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class PhaseVector:
    """
    Phase vector φ(θ) mapping continuous parameter to unit-modulus complex vector.
    
    φ(θ)_x = exp(i·Ω_x(θ))
    
    where Ω_x: Θ → ℝ is the phase function for each component x.
    
    Properties:
        - ||φ(θ)|| = 1 (unit normalization)
        - Each component has unit modulus: |φ_x| = 1
    """
    phases: NDArray[np.float64]  # Ω_x(θ) for each x
    
    def __post_init__(self):
        self.phases = np.asarray(self.phases, dtype=np.float64)
    
    @property
    def dimension(self) -> int:
        """Dimension N of the phase vector."""
        return len(self.phases)
    
    @property
    def vector(self) -> NDArray[np.complex128]:
        """φ(θ) = exp(i·Ω)."""
        return np.exp(1j * self.phases)
    
    @property
    def normalized_vector(self) -> NDArray[np.complex128]:
        """Normalized to ||φ|| = 1."""
        v = self.vector
        return v / np.linalg.norm(v)
    
    @property
    def norm(self) -> float:
        """||φ||."""
        return np.linalg.norm(self.vector)
    
    @classmethod
    def from_frequencies(cls, frequencies: NDArray[np.float64], 
                        theta: float) -> 'PhaseVector':
        """
        Create from frequency array: Ω_x(θ) = ω_x · θ.
        """
        phases = frequencies * theta
        return cls(phases=phases)
    
    @classmethod
    def uniform(cls, n: int, phase: float = 0.0) -> 'PhaseVector':
        """Uniform phase vector: all components have same phase."""
        return cls(phases=np.full(n, phase))
    
    @classmethod
    def random(cls, n: int, seed: Optional[int] = None) -> 'PhaseVector':
        """Random phase vector."""
        rng = np.random.default_rng(seed)
        phases = rng.uniform(0, 2 * np.pi, n)
        return cls(phases=phases)
    
    def outer_product(self) -> NDArray[np.complex128]:
        """φφ* (rank-one matrix)."""
        v = self.normalized_vector
        return np.outer(v, np.conj(v))
    
    def inner_product(self, other: 'PhaseVector') -> complex:
        """<φ, ψ> = φ*·ψ."""
        return np.vdot(self.vector, other.vector)
    
    def rotate(self, delta_phase: float) -> 'PhaseVector':
        """Global phase rotation."""
        return PhaseVector(phases=self.phases + delta_phase)


# ═══════════════════════════════════════════════════════════════════════════════
# HYBRID OPERATOR - DISCRETE + CONTINUOUS COUPLING
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class HybridOperator:
    """
    Rank-one hybrid coupling operator.
    
    H(θ) = A + λ·φ(θ)φ(θ)*
    
    where:
        A: N×N discrete operator (Hermitian for spectral analysis)
        λ: coupling strength
        φ(θ): phase vector
    
    Properties:
        - If A is Hermitian and λ ∈ ℝ, then H is Hermitian
        - Rank-one update: eigenvalues of H interlace those of A
        - Determinant lemma: det(H) = det(A)·(1 + λ·φ*A⁻¹φ)
    """
    discrete_operator: NDArray[np.complex128]  # A
    phase_vector: PhaseVector                   # φ(θ)
    coupling_strength: float = 1.0              # λ
    
    def __post_init__(self):
        self.discrete_operator = np.asarray(self.discrete_operator, dtype=np.complex128)
        n = self.discrete_operator.shape[0]
        if self.phase_vector.dimension != n:
            raise ValueError(f"Dimension mismatch: A is {n}×{n}, φ has dimension {self.phase_vector.dimension}")
    
    @property
    def dimension(self) -> int:
        """Matrix dimension N."""
        return self.discrete_operator.shape[0]
    
    @property
    def matrix(self) -> NDArray[np.complex128]:
        """H = A + λ·φφ*."""
        A = self.discrete_operator
        phi_outer = self.phase_vector.outer_product()
        return A + self.coupling_strength * phi_outer
    
    @property
    def is_hermitian(self) -> bool:
        """Check if H is Hermitian."""
        H = self.matrix
        return np.allclose(H, H.conj().T)
    
    def eigenvalues(self) -> NDArray[np.float64]:
        """
        Eigenvalues of H (real if Hermitian).
        Sorted in ascending order.
        """
        if self.is_hermitian:
            return np.linalg.eigvalsh(self.matrix)
        else:
            eigs = np.linalg.eigvals(self.matrix)
            return np.sort(np.real(eigs))
    
    def eigenpairs(self) -> Tuple[NDArray, NDArray]:
        """(eigenvalues, eigenvectors)."""
        if self.is_hermitian:
            return np.linalg.eigh(self.matrix)
        else:
            return np.linalg.eig(self.matrix)
    
    def spectral_gap(self, j: int) -> float:
        """
        j-th spectral gap: gap_j = λ_{j+1} - λ_j.
        """
        eigs = self.eigenvalues()
        if j < 0 or j >= len(eigs) - 1:
            raise ValueError(f"Invalid gap index {j}")
        return eigs[j + 1] - eigs[j]
    
    def minimum_gap(self) -> Tuple[int, float]:
        """Find minimum spectral gap and its index."""
        eigs = self.eigenvalues()
        gaps = np.diff(eigs)
        j = np.argmin(gaps)
        return (j, gaps[j])
    
    @classmethod
    def from_adjacency(cls, adjacency: NDArray, 
                      phases: NDArray[np.float64],
                      coupling: float = 1.0) -> 'HybridOperator':
        """
        Create from graph adjacency matrix and phase array.
        """
        return cls(
            discrete_operator=adjacency.astype(np.complex128),
            phase_vector=PhaseVector(phases=phases),
            coupling_strength=coupling
        )
    
    @classmethod
    def laplacian_coupling(cls, laplacian: NDArray,
                          phases: NDArray[np.float64],
                          coupling: float = 1.0) -> 'HybridOperator':
        """Create from graph Laplacian."""
        return cls(
            discrete_operator=laplacian.astype(np.complex128),
            phase_vector=PhaseVector(phases=phases),
            coupling_strength=coupling
        )


# ═══════════════════════════════════════════════════════════════════════════════
# TRACE MOMENTS - SPECTRAL FINGERPRINT
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class TraceMoments:
    """
    Trace moments M_n(θ) = Tr(H(θ)^n) as spectral invariants.
    
    If H is diagonalizable with eigenvalues {λ_j}:
        M_n = Σ_j λ_j^n
    
    Properties:
        - Invariant under similarity transformations
        - Newton's identities relate to elementary symmetric functions
        - Generate spectral fingerprint for comparison
    """
    hybrid: HybridOperator
    max_order: int = 10
    _cache: Dict[int, complex] = field(default_factory=dict, repr=False)
    
    def moment(self, n: int) -> complex:
        """M_n = Tr(H^n)."""
        if n in self._cache:
            return self._cache[n]
        
        H = self.hybrid.matrix
        H_power = np.linalg.matrix_power(H, n)
        result = np.trace(H_power)
        
        self._cache[n] = result
        return result
    
    def moments_up_to(self, k: int) -> List[complex]:
        """[M_1, M_2, ..., M_k]."""
        return [self.moment(n) for n in range(1, k + 1)]
    
    def fingerprint(self, precision: int = 6) -> Tuple[complex, ...]:
        """
        Spectral fingerprint: tuple of first few moments.
        Rounded for comparison.
        """
        moments = self.moments_up_to(self.max_order)
        rounded = [complex(round(m.real, precision), round(m.imag, precision)) 
                   for m in moments]
        return tuple(rounded)
    
    def matches(self, other: 'TraceMoments', tol: float = 1e-6) -> bool:
        """Check if two fingerprints match within tolerance."""
        for n in range(1, min(self.max_order, other.max_order) + 1):
            if abs(self.moment(n) - other.moment(n)) > tol:
                return False
        return True
    
    @staticmethod
    def from_eigenvalues(eigenvalues: NDArray, n: int) -> complex:
        """Compute M_n directly from eigenvalues."""
        return np.sum(eigenvalues ** n)


# ═══════════════════════════════════════════════════════════════════════════════
# DETERMINANT AND CHARACTERISTIC POLYNOMIAL
# ═══════════════════════════════════════════════════════════════════════════════

class DeterminantInvariants:
    """
    Determinant-based invariants for hybrid operator.
    
    Key formula (matrix determinant lemma):
        det(A + λφφ*) = det(A)·(1 + λ·φ*A⁻¹φ)
    
    when A is invertible.
    """
    
    def __init__(self, hybrid: HybridOperator):
        self.hybrid = hybrid
    
    def determinant(self) -> complex:
        """Δ(θ) = det(H(θ))."""
        return np.linalg.det(self.hybrid.matrix)
    
    def determinant_fast(self) -> Optional[complex]:
        """
        Fast determinant using matrix determinant lemma.
        Returns None if A is singular.
        """
        A = self.hybrid.discrete_operator
        phi = self.hybrid.phase_vector.normalized_vector
        lam = self.hybrid.coupling_strength
        
        try:
            det_A = np.linalg.det(A)
            if abs(det_A) < 1e-15:
                return None
            
            A_inv_phi = np.linalg.solve(A, phi)
            correction = 1 + lam * np.vdot(phi, A_inv_phi)
            
            return det_A * correction
        except np.linalg.LinAlgError:
            return None
    
    def characteristic_polynomial_at(self, z: complex) -> complex:
        """
        χ_H(z) = det(zI - H).
        
        Using rank-one formula:
        χ_H(z) = χ_A(z)·(1 - λ·φ*(zI-A)⁻¹φ)
        """
        H = self.hybrid.matrix
        n = H.shape[0]
        return np.linalg.det(z * np.eye(n) - H)
    
    def characteristic_polynomial_fast(self, z: complex) -> Optional[complex]:
        """
        Fast characteristic polynomial using rank-one formula.
        """
        A = self.hybrid.discrete_operator
        phi = self.hybrid.phase_vector.normalized_vector
        lam = self.hybrid.coupling_strength
        n = A.shape[0]
        
        try:
            zI_minus_A = z * np.eye(n) - A
            det_base = np.linalg.det(zI_minus_A)
            
            if abs(det_base) < 1e-15:
                return None
            
            resolvent_phi = np.linalg.solve(zI_minus_A, phi)
            correction = 1 - lam * np.vdot(phi, resolvent_phi)
            
            return det_base * correction
        except np.linalg.LinAlgError:
            return None


# ═══════════════════════════════════════════════════════════════════════════════
# HEAT KERNEL TRACES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class HeatKernelTrace:
    """
    Heat trace ℋ_β(θ) = Tr(e^{-βH(θ)}).
    
    Properties:
        - Smoothed spectral signature
        - ℋ_β = Σ_j e^{-β λ_j}
        - Stable under small perturbations
        - Compatible with semigroup analysis
    """
    hybrid: HybridOperator
    
    def trace(self, beta: float) -> float:
        """ℋ_β = Tr(e^{-βH})."""
        if beta < 0:
            raise ValueError(f"β must be non-negative, got {beta}")
        
        # Use eigenvalue decomposition for stability
        eigs = self.hybrid.eigenvalues()
        return np.sum(np.exp(-beta * eigs))
    
    def trace_derivative(self, beta: float) -> float:
        """d/dβ ℋ_β = -Tr(H·e^{-βH}) = -Σ_j λ_j e^{-β λ_j}."""
        eigs = self.hybrid.eigenvalues()
        return -np.sum(eigs * np.exp(-beta * eigs))
    
    def partition_function(self, beta: float) -> float:
        """Z(β) = ℋ_β (statistical mechanics interpretation)."""
        return self.trace(beta)
    
    def free_energy(self, beta: float) -> float:
        """F = -ln(Z)/β."""
        Z = self.partition_function(beta)
        if Z <= 0:
            return float('inf')
        return -np.log(Z) / beta if beta > 0 else 0
    
    def entropy_from_heat(self, beta: float) -> float:
        """S = β²·∂F/∂β = β·<E> + ln(Z)."""
        Z = self.partition_function(beta)
        if Z <= 0:
            return 0
        E_avg = -self.trace_derivative(beta) / Z
        return beta * E_avg + np.log(Z)


# ═══════════════════════════════════════════════════════════════════════════════
# EIGENVALUE SPIKE DETECTOR
# ═══════════════════════════════════════════════════════════════════════════════

class EigenvalueSpikeDetector:
    """
    Detector for eigenvalue spikes under rank-one coupling.
    
    Key insight: Eigenvalue z is in spectrum of H = A + λφφ* iff
        1 - λ·g_θ(z) = 0
    where
        g_θ(z) = φ*(zI - A)⁻¹φ
    
    This reduces eigenvalue detection to scalar root-finding.
    """
    
    def __init__(self, hybrid: HybridOperator):
        self.hybrid = hybrid
        self.A = hybrid.discrete_operator
        self.phi = hybrid.phase_vector.normalized_vector
        self.lam = hybrid.coupling_strength
        self.n = hybrid.dimension
    
    def resolvent_functional(self, z: complex) -> complex:
        """
        g_θ(z) = φ*(zI - A)⁻¹φ.
        """
        try:
            zI_minus_A = z * np.eye(self.n) - self.A
            resolvent_phi = np.linalg.solve(zI_minus_A, self.phi)
            return np.vdot(self.phi, resolvent_phi)
        except np.linalg.LinAlgError:
            return complex('inf')
    
    def spike_equation(self, z: complex) -> complex:
        """
        f(z) = 1 - λ·g_θ(z).
        Roots are eigenvalues of H.
        """
        return 1 - self.lam * self.resolvent_functional(z)
    
    def has_spike_in_gap(self, lower: float, upper: float, 
                        n_samples: int = 100) -> bool:
        """
        Check if there's an eigenvalue spike in interval (lower, upper).
        Uses sign change detection for real intervals.
        """
        # Sample along real line
        z_values = np.linspace(lower + 1e-10, upper - 1e-10, n_samples)
        
        prev_sign = None
        for z in z_values:
            f_z = self.spike_equation(z)
            if not np.isfinite(f_z):
                continue
            
            curr_sign = np.sign(np.real(f_z))
            if prev_sign is not None and curr_sign != prev_sign:
                return True
            prev_sign = curr_sign
        
        return False
    
    def locate_spikes(self, search_range: Tuple[float, float],
                     n_initial: int = 50) -> List[float]:
        """
        Locate eigenvalue spikes in search range.
        """
        from scipy.optimize import brentq
        
        lower, upper = search_range
        z_values = np.linspace(lower, upper, n_initial)
        
        # Find sign changes
        spikes = []
        prev_z, prev_f = None, None
        
        for z in z_values:
            f_z = self.spike_equation(z)
            if not np.isfinite(f_z):
                prev_z, prev_f = None, None
                continue
            
            f_real = np.real(f_z)
            if prev_f is not None:
                if prev_f * f_real < 0:
                    # Sign change - locate root
                    try:
                        root = brentq(
                            lambda x: np.real(self.spike_equation(x)),
                            prev_z, z
                        )
                        spikes.append(root)
                    except:
                        pass
            
            prev_z, prev_f = z, f_real
        
        return spikes
    
    def interlacing_check(self) -> bool:
        """
        Verify interlacing law: eigenvalues of H interlace those of A.
        For rank-one update, this should always hold.
        """
        eigs_A = np.linalg.eigvalsh(self.A) if np.allclose(self.A, self.A.conj().T) else np.sort(np.real(np.linalg.eigvals(self.A)))
        eigs_H = self.hybrid.eigenvalues()
        
        # Check interlacing: between each pair of H-eigenvalues, 
        # there should be at most one A-eigenvalue
        for i in range(len(eigs_H) - 1):
            count = np.sum((eigs_A > eigs_H[i]) & (eigs_A < eigs_H[i + 1]))
            if count > 1:
                return False
        
        return True


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE COHERENCE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class PhaseCoherence:
    """
    Phase coherence between discrete and continuous transformations.
    
    Coherence condition: discrete operation a and continuous transformation b
    induce the same phase action:
        Δ_a(x) = Γ_b(θ)  (mod 2π)
    
    Under coherence, translation between dialects is certified.
    """
    discrete_phases: NDArray[np.float64]   # Δ_a(x)
    continuous_phases: NDArray[np.float64]  # Γ_b(θ)
    tolerance: float = 1e-6
    
    def phase_difference(self) -> NDArray[np.float64]:
        """Δ_a - Γ_b (mod 2π)."""
        diff = self.discrete_phases - self.continuous_phases
        return np.mod(diff + np.pi, 2 * np.pi) - np.pi
    
    def is_coherent(self) -> bool:
        """Check if phases are coherent within tolerance."""
        diff = self.phase_difference()
        return np.all(np.abs(diff) < self.tolerance)
    
    def coherence_defect(self) -> float:
        """Maximum phase difference (coherence violation)."""
        return np.max(np.abs(self.phase_difference()))
    
    def coherence_certificate(self) -> Dict[str, Any]:
        """Generate coherence certificate."""
        return {
            'is_coherent': self.is_coherent(),
            'max_defect': self.coherence_defect(),
            'tolerance': self.tolerance,
            'phase_differences': self.phase_difference().tolist()
        }


# ═══════════════════════════════════════════════════════════════════════════════
# HYBRID INVARIANT BUNDLE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class HybridInvariantBundle:
    """
    Complete bundle of hybrid invariants for a coupling.
    
    Collects:
        - Trace moments
        - Determinant
        - Spectral gaps
        - Heat traces
    """
    hybrid: HybridOperator
    
    def trace_moments(self, max_order: int = 5) -> TraceMoments:
        """Get trace moments object."""
        return TraceMoments(hybrid=self.hybrid, max_order=max_order)
    
    def determinant_invariants(self) -> DeterminantInvariants:
        """Get determinant invariants."""
        return DeterminantInvariants(self.hybrid)
    
    def heat_trace(self) -> HeatKernelTrace:
        """Get heat kernel trace."""
        return HeatKernelTrace(self.hybrid)
    
    def spike_detector(self) -> EigenvalueSpikeDetector:
        """Get eigenvalue spike detector."""
        return EigenvalueSpikeDetector(self.hybrid)
    
    def full_diagnostic(self) -> Dict[str, Any]:
        """Complete diagnostic report."""
        eigs = self.hybrid.eigenvalues()
        
        return {
            'dimension': self.hybrid.dimension,
            'coupling_strength': self.hybrid.coupling_strength,
            'is_hermitian': self.hybrid.is_hermitian,
            'eigenvalues': eigs.tolist(),
            'trace_M1': float(np.real(self.trace_moments().moment(1))),
            'trace_M2': float(np.real(self.trace_moments().moment(2))),
            'determinant': complex(self.determinant_invariants().determinant()),
            'min_gap': self.hybrid.minimum_gap(),
            'heat_trace_beta1': self.heat_trace().trace(1.0),
            'interlacing_valid': self.spike_detector().interlacing_check()
        }


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def create_hybrid_coupling(A: NDArray, phases: NDArray, 
                          coupling: float = 1.0) -> HybridOperator:
    """Create hybrid operator from discrete matrix and phases."""
    return HybridOperator(
        discrete_operator=A,
        phase_vector=PhaseVector(phases=phases),
        coupling_strength=coupling
    )


def analyze_hybrid(hybrid: HybridOperator) -> Dict[str, Any]:
    """Complete analysis of hybrid operator."""
    bundle = HybridInvariantBundle(hybrid)
    return bundle.full_diagnostic()


def check_coherence(discrete_phases: NDArray, 
                   continuous_phases: NDArray,
                   tol: float = 1e-6) -> bool:
    """Quick coherence check."""
    return PhaseCoherence(discrete_phases, continuous_phases, tol).is_coherent()


def trace_fingerprint(hybrid: HybridOperator, order: int = 5) -> Tuple:
    """Get trace moment fingerprint."""
    return TraceMoments(hybrid, max_order=order).fingerprint()


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Core classes
    'PhaseVector',
    'HybridOperator',
    
    # Invariants
    'TraceMoments',
    'DeterminantInvariants',
    'HeatKernelTrace',
    
    # Detection
    'EigenvalueSpikeDetector',
    'PhaseCoherence',
    
    # Bundle
    'HybridInvariantBundle',
    
    # Functions
    'create_hybrid_coupling',
    'analyze_hybrid',
    'check_coherence',
    'trace_fingerprint',
]
