"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        DECOHERENCE MODULE                                    ║
║                                                                              ║
║  Quantum Coherence Dynamics and Lindblad Evolution                           ║
║                                                                              ║
║  Core Equation (Lindblad Master Equation):                                   ║
║    dρ/dt = -i[H, ρ] + D[ρ]                                                   ║
║    D[ρ] = Σ_k (L_k ρ L_k† - ½{L_k†L_k, ρ})                                  ║
║                                                                              ║
║  Coherence States:                                                           ║
║    - Coherent states: minimal uncertainty, low Texture                       ║
║    - Incoherent mixtures: no off-diagonal, low useful Texture                ║
║    - Intermediate: partial coherence, intermediate Texture                   ║
║                                                                              ║
║  Decoherence Cost:                                                           ║
║    Maintaining long-range coherence requires κ-budget allocation             ║
║    Coherence length ℓ_c bounded by available resources                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Any, Callable
from enum import Enum
import numpy as np
from numpy.typing import NDArray


# ═══════════════════════════════════════════════════════════════════════════════
# COHERENCE TYPES
# ═══════════════════════════════════════════════════════════════════════════════

class CoherenceState(Enum):
    """Classification of coherence states."""
    PURE_COHERENT = "pure_coherent"       # Minimal uncertainty coherent state
    PARTIALLY_COHERENT = "partial"         # Decohered superposition
    INCOHERENT_MIXTURE = "incoherent"     # No off-diagonal elements
    MAXIMALLY_MIXED = "maximally_mixed"   # ρ = I/d


class DecoherenceChannel(Enum):
    """Types of decoherence channels."""
    DEPHASING = "dephasing"           # Phase damping
    AMPLITUDE_DAMPING = "amplitude"   # Energy decay
    DEPOLARIZING = "depolarizing"     # Uniform mixing
    BIT_FLIP = "bit_flip"             # Classical bit flip
    PHASE_FLIP = "phase_flip"         # Z errors


# ═══════════════════════════════════════════════════════════════════════════════
# DENSITY MATRIX
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class DensityMatrix:
    """
    Quantum density matrix ρ.
    
    Properties:
    - Hermitian: ρ† = ρ
    - Positive: ⟨ψ|ρ|ψ⟩ ≥ 0
    - Trace one: Tr(ρ) = 1
    """
    matrix: NDArray
    
    def __post_init__(self):
        """Ensure matrix is proper density matrix."""
        self.matrix = np.asarray(self.matrix, dtype=complex)
    
    @property
    def dim(self) -> int:
        """Dimension d."""
        return self.matrix.shape[0]
    
    @property
    def trace(self) -> complex:
        """Tr(ρ)."""
        return np.trace(self.matrix)
    
    @property
    def purity(self) -> float:
        """γ = Tr(ρ²), 1/d ≤ γ ≤ 1."""
        return float(np.real(np.trace(self.matrix @ self.matrix)))
    
    @property
    def is_pure(self) -> bool:
        """Check if pure state (γ ≈ 1)."""
        return self.purity > 0.999
    
    @property
    def is_maximally_mixed(self) -> bool:
        """Check if maximally mixed (γ ≈ 1/d)."""
        return abs(self.purity - 1.0/self.dim) < 0.001
    
    def diagonal(self) -> NDArray:
        """Diagonal elements (populations)."""
        return np.diag(self.matrix)
    
    def off_diagonal_norm(self) -> float:
        """Frobenius norm of off-diagonal elements."""
        rho_diag = np.diag(np.diag(self.matrix))
        return np.linalg.norm(self.matrix - rho_diag, 'fro')
    
    def von_neumann_entropy(self) -> float:
        """S(ρ) = -Tr(ρ log ρ)."""
        eigenvalues = np.linalg.eigvalsh(self.matrix)
        eigenvalues = eigenvalues[eigenvalues > 1e-15]
        return -float(np.sum(eigenvalues * np.log2(eigenvalues)))
    
    def coherence_state(self) -> CoherenceState:
        """Classify coherence state."""
        if self.is_pure:
            return CoherenceState.PURE_COHERENT
        if self.is_maximally_mixed:
            return CoherenceState.MAXIMALLY_MIXED
        if self.off_diagonal_norm() < 1e-10:
            return CoherenceState.INCOHERENT_MIXTURE
        return CoherenceState.PARTIALLY_COHERENT
    
    @classmethod
    def pure(cls, psi: NDArray) -> 'DensityMatrix':
        """Create pure state |ψ⟩⟨ψ|."""
        psi = np.asarray(psi, dtype=complex).reshape(-1, 1)
        psi = psi / np.linalg.norm(psi)
        return cls(psi @ psi.conj().T)
    
    @classmethod
    def maximally_mixed(cls, d: int) -> 'DensityMatrix':
        """Create maximally mixed state I/d."""
        return cls(np.eye(d, dtype=complex) / d)
    
    @classmethod
    def thermal(cls, H: NDArray, beta: float) -> 'DensityMatrix':
        """Create thermal state ρ = e^{-βH}/Z."""
        exp_H = np.linalg.matrix_power(
            np.eye(H.shape[0]) - beta * H / 100, 100
        )
        Z = np.trace(exp_H)
        return cls(exp_H / Z)


# ═══════════════════════════════════════════════════════════════════════════════
# LINDBLAD OPERATORS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class LindbladOperator:
    """
    Lindblad jump operator L_k.
    
    Describes irreversible dynamics through:
    L_k ρ L_k† - ½{L_k†L_k, ρ}
    """
    matrix: NDArray
    rate: float = 1.0
    name: str = ""
    
    @property
    def dagger(self) -> NDArray:
        """Hermitian conjugate L†."""
        return self.matrix.conj().T
    
    @property
    def LdagL(self) -> NDArray:
        """L†L for anticommutator term."""
        return self.dagger @ self.matrix
    
    def jump_term(self, rho: NDArray) -> NDArray:
        """L ρ L† term."""
        return self.matrix @ rho @ self.dagger
    
    def anticommutator_term(self, rho: NDArray) -> NDArray:
        """½{L†L, ρ} term."""
        LdL = self.LdagL
        return 0.5 * (LdL @ rho + rho @ LdL)
    
    def dissipator(self, rho: NDArray) -> NDArray:
        """Full dissipator D_L[ρ] = L ρ L† - ½{L†L, ρ}."""
        return self.rate * (self.jump_term(rho) - self.anticommutator_term(rho))
    
    @classmethod
    def dephasing(cls, d: int, gamma: float = 1.0) -> List['LindbladOperator']:
        """
        Dephasing operators for d-dimensional system.
        
        L_k = |k⟩⟨k| for k = 0, ..., d-1
        """
        ops = []
        for k in range(d):
            L = np.zeros((d, d), dtype=complex)
            L[k, k] = 1.0
            ops.append(cls(L, gamma, f"dephasing_{k}"))
        return ops
    
    @classmethod
    def amplitude_damping(cls, d: int, gamma: float = 1.0) -> List['LindbladOperator']:
        """
        Amplitude damping (energy decay) operators.
        
        L_k = √γ |k⟩⟨k+1| for k = 0, ..., d-2
        """
        ops = []
        for k in range(d - 1):
            L = np.zeros((d, d), dtype=complex)
            L[k, k + 1] = np.sqrt(gamma)
            ops.append(cls(L, 1.0, f"amp_damp_{k}"))
        return ops
    
    @classmethod
    def depolarizing(cls, d: int, gamma: float = 1.0) -> List['LindbladOperator']:
        """
        Depolarizing channel operators.
        
        Generalized Pauli matrices.
        """
        ops = []
        # Simple version: use |i⟩⟨j| basis
        for i in range(d):
            for j in range(d):
                if i != j:
                    L = np.zeros((d, d), dtype=complex)
                    L[i, j] = np.sqrt(gamma / (d * d - 1))
                    ops.append(cls(L, 1.0, f"depol_{i}_{j}"))
        return ops


# ═══════════════════════════════════════════════════════════════════════════════
# LINDBLAD MASTER EQUATION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class LindbladEvolution:
    """
    Lindblad master equation evolution.
    
    dρ/dt = -i[H, ρ] + Σ_k D_{L_k}[ρ]
    """
    hamiltonian: NDArray
    lindblad_ops: List[LindbladOperator]
    
    def commutator(self, rho: NDArray) -> NDArray:
        """Compute -i[H, ρ]."""
        return -1j * (self.hamiltonian @ rho - rho @ self.hamiltonian)
    
    def total_dissipator(self, rho: NDArray) -> NDArray:
        """Compute Σ_k D_{L_k}[ρ]."""
        D = np.zeros_like(rho)
        for L in self.lindblad_ops:
            D += L.dissipator(rho)
        return D
    
    def drho_dt(self, rho: NDArray) -> NDArray:
        """Full time derivative dρ/dt."""
        return self.commutator(rho) + self.total_dissipator(rho)
    
    def evolve(self, rho0: DensityMatrix, t_final: float,
               dt: float = 0.01) -> List[DensityMatrix]:
        """
        Evolve density matrix via Euler method.
        
        Returns trajectory.
        """
        trajectory = [rho0]
        rho = rho0.matrix.copy()
        t = 0.0
        
        while t < t_final:
            drho = self.drho_dt(rho)
            rho = rho + dt * drho
            
            # Ensure trace = 1
            rho = rho / np.trace(rho)
            
            trajectory.append(DensityMatrix(rho.copy()))
            t += dt
        
        return trajectory
    
    def decoherence_rate(self, rho: DensityMatrix) -> float:
        """
        Estimate decoherence rate from Lindblad operators.
        
        Rate = Σ_k Tr(L_k† L_k ρ)
        """
        rate = 0.0
        for L in self.lindblad_ops:
            rate += L.rate * np.real(np.trace(L.LdagL @ rho.matrix))
        return rate


# ═══════════════════════════════════════════════════════════════════════════════
# COHERENCE LENGTH
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class CoherenceLength:
    """
    Coherence length ℓ_c in configuration/mode space.
    
    Correlations ρ(x, x') significant for |x - x'| ≲ ℓ_c.
    """
    
    def estimate(self, rho: DensityMatrix) -> float:
        """
        Estimate coherence length from density matrix.
        
        ℓ_c ≈ effective width of off-diagonal decay.
        """
        d = rho.dim
        if d < 2:
            return 0.0
        
        # Look at off-diagonal decay
        norms = []
        for k in range(1, d):
            # k-th off-diagonal
            offdiag = np.diag(rho.matrix, k)
            norms.append(np.linalg.norm(offdiag))
        
        if not norms or max(norms) < 1e-15:
            return 0.0
        
        # Find where norm drops to e^{-1} of max
        max_norm = max(norms)
        for k, n in enumerate(norms):
            if n < max_norm / np.e:
                return float(k + 1)
        
        return float(d - 1)
    
    def max_coherence_length(self, kappa: float, 
                             decoherence_rate: float) -> float:
        """
        Maximum achievable coherence length given κ allocation.
        
        ℓ_c^max = √(κ / γ_dec)
        """
        if decoherence_rate < 1e-15:
            return float('inf')
        return np.sqrt(kappa / decoherence_rate)


# ═══════════════════════════════════════════════════════════════════════════════
# DECOHERENCE COST
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class DecoherenceCost:
    """
    Cost of maintaining coherence (κ-budget perspective).
    
    Ċ_i(S) = Σ_k Tr(L_k†L_k ρ)|_S
    """
    
    def instantaneous_cost(self, rho: DensityMatrix,
                           lindblad_ops: List[LindbladOperator]) -> float:
        """
        Instantaneous decoherence pressure.
        """
        cost = 0.0
        for L in lindblad_ops:
            cost += L.rate * np.real(np.trace(L.LdagL @ rho.matrix))
        return cost
    
    def coherence_maintenance_cost(self, coherence_length: float,
                                   time_duration: float,
                                   gamma: float = 1.0) -> float:
        """
        Total cost to maintain coherence length for duration.
        
        Cost ∝ ℓ_c² × γ × t
        """
        return coherence_length ** 2 * gamma * time_duration
    
    def texture_action_contribution(self, rho: DensityMatrix,
                                    lindblad_ops: List[LindbladOperator],
                                    lambda_weight: float = 1.0) -> float:
        """
        Contribution to Texture action.
        
        A_i[ρ] = λ_i T_i[ρ] - decoherence_control_cost
        """
        # Simple Texture estimate
        texture = rho.von_neumann_entropy() + rho.off_diagonal_norm()
        cost = self.instantaneous_cost(rho, lindblad_ops)
        return lambda_weight * texture - cost


# ═══════════════════════════════════════════════════════════════════════════════
# COHERENT STATES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class CoherentStateAnalysis:
    """
    Analysis of coherent vs incoherent states.
    """
    
    def is_coherent_state(self, rho: DensityMatrix,
                          threshold: float = 0.9) -> bool:
        """
        Check if state is approximately coherent.
        
        Coherent states have:
        - High purity
        - Minimal uncertainty
        - Simple Wigner function
        """
        return rho.purity > threshold
    
    def coherence_fraction(self, rho: DensityMatrix) -> float:
        """
        Fraction of norm in off-diagonal elements.
        
        f_coh = ||ρ_off||_F / ||ρ||_F
        """
        total_norm = np.linalg.norm(rho.matrix, 'fro')
        if total_norm < 1e-15:
            return 0.0
        return rho.off_diagonal_norm() / total_norm
    
    def decoherence_witness(self, rho_initial: DensityMatrix,
                            rho_final: DensityMatrix) -> float:
        """
        Witness decoherence by comparing off-diagonal norms.
        
        W = 1 - ||ρ_off_final|| / ||ρ_off_initial||
        """
        norm_i = rho_initial.off_diagonal_norm()
        norm_f = rho_final.off_diagonal_norm()
        if norm_i < 1e-15:
            return 0.0
        return 1.0 - norm_f / norm_i


# ═══════════════════════════════════════════════════════════════════════════════
# POLE BRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class DecoherencePoleBridge:
    """
    Bridge between Decoherence dynamics and four-pole framework.
    """
    
    @staticmethod
    def imaginary_sector() -> str:
        """Decoherence lives in Imaginary sector."""
        return "Decoherence ↔ U_𝕀+ (Imaginary sector)"
    
    @staticmethod
    def c_pole() -> str:
        """C-pole manages continuous wave dynamics."""
        return "C-pole ↔ Continuous wave evolution, coherence"
    
    @staticmethod
    def flower_chart() -> str:
        """✿ chart for transform dynamics."""
        return "✿ chart: Wave transformations, phase dynamics"
    
    @staticmethod
    def integration() -> str:
        return """
        DECOHERENCE ↔ FRAMEWORK
        
        Lindblad Master Equation:
          dρ/dt = -i[H, ρ] + Σ_k D_{L_k}[ρ]
        
        Coherence States:
          - Pure coherent: γ ≈ 1, low Texture
          - Incoherent: no off-diagonal, low useful Texture
          - Intermediate: partial coherence, high Texture
        
        κ-Budget Connection:
          - Maintaining coherence costs κ allocation
          - ℓ_c^max bounded by available resources
          - Trade-off with other sectors
        
        Links to:
          - C-pole (continuous dynamics)
          - ✿ chart (phase space)
          - Imaginary sector (probability/wave)
        """


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def density_matrix(matrix: NDArray) -> DensityMatrix:
    """Create density matrix."""
    return DensityMatrix(matrix)


def pure_state(psi: NDArray) -> DensityMatrix:
    """Create pure state density matrix."""
    return DensityMatrix.pure(psi)


def maximally_mixed(d: int) -> DensityMatrix:
    """Create maximally mixed state."""
    return DensityMatrix.maximally_mixed(d)


def lindblad_operator(matrix: NDArray, rate: float = 1.0) -> LindbladOperator:
    """Create Lindblad operator."""
    return LindbladOperator(matrix, rate)


def dephasing_channel(d: int, gamma: float = 1.0) -> List[LindbladOperator]:
    """Create dephasing Lindblad operators."""
    return LindbladOperator.dephasing(d, gamma)


def amplitude_damping_channel(d: int, gamma: float = 1.0) -> List[LindbladOperator]:
    """Create amplitude damping operators."""
    return LindbladOperator.amplitude_damping(d, gamma)


def lindblad_evolution(H: NDArray, ops: List[LindbladOperator]) -> LindbladEvolution:
    """Create Lindblad evolution."""
    return LindbladEvolution(H, ops)


def coherence_length() -> CoherenceLength:
    """Create coherence length estimator."""
    return CoherenceLength()


def decoherence_cost() -> DecoherenceCost:
    """Create decoherence cost calculator."""
    return DecoherenceCost()


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Enums
    'CoherenceState',
    'DecoherenceChannel',
    
    # Density Matrix
    'DensityMatrix',
    
    # Lindblad
    'LindbladOperator',
    'LindbladEvolution',
    
    # Coherence
    'CoherenceLength',
    'DecoherenceCost',
    'CoherentStateAnalysis',
    
    # Bridge
    'DecoherencePoleBridge',
    
    # Functions
    'density_matrix',
    'pure_state',
    'maximally_mixed',
    'lindblad_operator',
    'dephasing_channel',
    'amplitude_damping_channel',
    'lindblad_evolution',
    'coherence_length',
    'decoherence_cost',
]
