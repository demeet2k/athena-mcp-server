"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    QUANTUM INFORMATION MODULE                                ║
║                                                                              ║
║  Density Matrices, Quantum Channels, and Entanglement Measures              ║
║                                                                              ║
║  Core Principle:                                                             ║
║    Quantum information theory provides the mathematical framework            ║
║    for the Σ-pole (stochastic/probabilistic). Density matrices              ║
║    generalize pure states, and quantum channels encode evolution.           ║
║                                                                              ║
║  Key Structures:                                                             ║
║    - Density matrix: ρ ≥ 0, Tr(ρ) = 1                                       ║
║    - Von Neumann entropy: S(ρ) = -Tr(ρ log ρ)                               ║
║    - Quantum channels: CPTP maps                                            ║
║    - Entanglement: Schmidt decomposition, negativity                        ║
║                                                                              ║
║  Connection to Framework:                                                    ║
║    - Σ-pole ↔ density matrix formulation                                    ║
║    - Entropy bounds ↔ information capacity                                  ║
║    - Entanglement ↔ non-factorizable correlations                           ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Callable
import numpy as np
from numpy.typing import NDArray


# ═══════════════════════════════════════════════════════════════════════════════
# DENSITY MATRIX
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class DensityMatrix:
    """
    Quantum density matrix ρ.
    
    Properties:
        - Hermitian: ρ = ρ†
        - Positive semidefinite: ρ ≥ 0
        - Trace 1: Tr(ρ) = 1
    """
    matrix: NDArray[np.complex128]
    
    def __post_init__(self):
        # Ensure Hermitian
        self.matrix = (self.matrix + self.matrix.conj().T) / 2
        
        # Ensure trace 1
        tr = np.trace(self.matrix)
        if abs(tr) > 1e-15:
            self.matrix = self.matrix / tr
    
    @property
    def dim(self) -> int:
        """Hilbert space dimension."""
        return self.matrix.shape[0]
    
    def trace(self) -> float:
        """Trace of density matrix."""
        return float(np.real(np.trace(self.matrix)))
    
    def purity(self) -> float:
        """
        Purity γ = Tr(ρ²).
        
        1/d ≤ γ ≤ 1, with γ = 1 iff pure state.
        """
        return float(np.real(np.trace(self.matrix @ self.matrix)))
    
    def is_pure(self, tolerance: float = 1e-10) -> bool:
        """Check if state is pure (rank 1)."""
        return abs(self.purity() - 1) < tolerance
    
    def eigenvalues(self) -> NDArray[np.float64]:
        """Eigenvalues of density matrix (probabilities)."""
        eigs = np.linalg.eigvalsh(self.matrix)
        # Ensure non-negative
        eigs = np.maximum(eigs, 0)
        return eigs
    
    def von_neumann_entropy(self) -> float:
        """
        Von Neumann entropy: S(ρ) = -Tr(ρ log ρ).
        
        0 ≤ S ≤ log(d), with S = 0 for pure states.
        """
        eigs = self.eigenvalues()
        eigs = eigs[eigs > 1e-15]  # Remove zeros
        return float(-np.sum(eigs * np.log(eigs)))
    
    def linear_entropy(self) -> float:
        """
        Linear entropy: S_L = 1 - Tr(ρ²).
        
        Approximates von Neumann entropy for small mixedness.
        """
        return 1 - self.purity()
    
    def fidelity(self, other: 'DensityMatrix') -> float:
        """
        Fidelity: F(ρ, σ) = [Tr(√(√ρ σ √ρ))]².
        
        For pure states: F(|ψ⟩, |φ⟩) = |⟨ψ|φ⟩|².
        """
        sqrt_rho = self._matrix_sqrt(self.matrix)
        inner = sqrt_rho @ other.matrix @ sqrt_rho
        sqrt_inner = self._matrix_sqrt(inner)
        return float(np.real(np.trace(sqrt_inner)) ** 2)
    
    def _matrix_sqrt(self, M: NDArray) -> NDArray:
        """Matrix square root via eigendecomposition."""
        eigs, vecs = np.linalg.eigh(M)
        eigs = np.maximum(eigs, 0)
        return vecs @ np.diag(np.sqrt(eigs)) @ vecs.conj().T
    
    def partial_trace(self, dims: Tuple[int, int], 
                     keep: int) -> 'DensityMatrix':
        """
        Partial trace over subsystem.
        
        dims: (dim_A, dim_B) of composite system
        keep: 0 for A, 1 for B
        """
        d_A, d_B = dims
        
        if d_A * d_B != self.dim:
            raise ValueError(f"Dimensions {dims} don't match matrix dim {self.dim}")
        
        rho = self.matrix.reshape(d_A, d_B, d_A, d_B)
        
        if keep == 0:
            # Trace out B: result is d_A × d_A
            result = np.einsum('ijik->jk', rho)
        else:
            # Trace out A: result is d_B × d_B
            result = np.einsum('ijkj->ik', rho)
        
        return DensityMatrix(result)
    
    @classmethod
    def pure(cls, state: NDArray) -> 'DensityMatrix':
        """Create pure state |ψ⟩⟨ψ|."""
        state = state / np.linalg.norm(state)
        return cls(np.outer(state, state.conj()))
    
    @classmethod
    def maximally_mixed(cls, d: int) -> 'DensityMatrix':
        """Maximally mixed state I/d."""
        return cls(np.eye(d) / d)
    
    @classmethod
    def thermal(cls, H: NDArray, beta: float) -> 'DensityMatrix':
        """
        Thermal state: ρ = exp(-βH) / Z.
        """
        exp_H = np.exp(-beta * np.linalg.eigvalsh(H))
        Z = np.sum(exp_H)
        
        eigs, vecs = np.linalg.eigh(H)
        rho = vecs @ np.diag(np.exp(-beta * eigs) / Z) @ vecs.conj().T
        return cls(rho)


# ═══════════════════════════════════════════════════════════════════════════════
# QUANTUM CHANNEL
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class QuantumChannel:
    """
    Quantum channel (CPTP map).
    
    Represented via Kraus operators: Φ(ρ) = Σ_k K_k ρ K_k†
    with Σ_k K_k† K_k = I.
    """
    kraus_operators: List[NDArray[np.complex128]]
    
    @property
    def input_dim(self) -> int:
        return self.kraus_operators[0].shape[1]
    
    @property
    def output_dim(self) -> int:
        return self.kraus_operators[0].shape[0]
    
    def apply(self, rho: DensityMatrix) -> DensityMatrix:
        """Apply channel to density matrix."""
        result = np.zeros((self.output_dim, self.output_dim), 
                         dtype=np.complex128)
        
        for K in self.kraus_operators:
            result += K @ rho.matrix @ K.conj().T
        
        return DensityMatrix(result)
    
    def is_trace_preserving(self, tolerance: float = 1e-10) -> bool:
        """Check Σ K†K = I."""
        total = sum(K.conj().T @ K for K in self.kraus_operators)
        return np.allclose(total, np.eye(self.input_dim), atol=tolerance)
    
    def choi_matrix(self) -> NDArray[np.complex128]:
        """
        Choi matrix representation.
        
        J(Φ) = (I ⊗ Φ)(|Ω⟩⟨Ω|) where |Ω⟩ = Σ |ii⟩/√d.
        """
        d = self.input_dim
        
        # Maximally entangled state
        omega = np.zeros((d * d, 1), dtype=np.complex128)
        for i in range(d):
            omega[i * d + i] = 1 / np.sqrt(d)
        
        omega_proj = omega @ omega.conj().T
        omega_proj = omega_proj.reshape(d, d, d, d)
        
        # Apply channel to second subsystem
        choi = np.zeros((d * self.output_dim, d * self.output_dim), 
                       dtype=np.complex128)
        
        for i in range(d):
            for j in range(d):
                # |i⟩⟨j| on first system
                # Φ(|i⟩⟨j|) on second system
                input_matrix = np.zeros((d, d), dtype=np.complex128)
                input_matrix[i, j] = 1
                
                output = np.zeros((self.output_dim, self.output_dim), 
                                 dtype=np.complex128)
                for K in self.kraus_operators:
                    output += K @ input_matrix @ K.conj().T
                
                # Tensor product contribution
                for a in range(d):
                    for b in range(d):
                        for c in range(self.output_dim):
                            for e in range(self.output_dim):
                                if a == i and b == j:
                                    choi[a * self.output_dim + c, 
                                        b * self.output_dim + e] += output[c, e] / d
        
        return choi
    
    @classmethod
    def identity(cls, d: int) -> 'QuantumChannel':
        """Identity channel."""
        return cls([np.eye(d, dtype=np.complex128)])
    
    @classmethod
    def depolarizing(cls, d: int, p: float) -> 'QuantumChannel':
        """
        Depolarizing channel: Φ(ρ) = (1-p)ρ + p·I/d.
        """
        # Kraus: √(1-p) I and √(p/d²) E_{ij} for all i,j
        kraus = [np.sqrt(1 - p + p/d**2) * np.eye(d, dtype=np.complex128)]
        
        for i in range(d):
            for j in range(d):
                if i != j or (i == 0 and j == 0):
                    continue
                E = np.zeros((d, d), dtype=np.complex128)
                E[i, j] = np.sqrt(p / d**2)
                kraus.append(E)
        
        return cls(kraus)
    
    @classmethod
    def amplitude_damping(cls, gamma: float) -> 'QuantumChannel':
        """
        Amplitude damping channel (qubit decay).
        
        K_0 = |0⟩⟨0| + √(1-γ)|1⟩⟨1|
        K_1 = √γ |0⟩⟨1|
        """
        K0 = np.array([[1, 0], [0, np.sqrt(1 - gamma)]], dtype=np.complex128)
        K1 = np.array([[0, np.sqrt(gamma)], [0, 0]], dtype=np.complex128)
        return cls([K0, K1])
    
    @classmethod
    def phase_damping(cls, gamma: float) -> 'QuantumChannel':
        """
        Phase damping channel (dephasing).
        """
        K0 = np.array([[1, 0], [0, np.sqrt(1 - gamma)]], dtype=np.complex128)
        K1 = np.array([[0, 0], [0, np.sqrt(gamma)]], dtype=np.complex128)
        return cls([K0, K1])


# ═══════════════════════════════════════════════════════════════════════════════
# ENTANGLEMENT MEASURES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class EntanglementMeasures:
    """
    Various entanglement measures for bipartite states.
    """
    rho: DensityMatrix
    dims: Tuple[int, int]  # (dim_A, dim_B)
    
    def reduced_A(self) -> DensityMatrix:
        """Reduced density matrix of subsystem A."""
        return self.rho.partial_trace(self.dims, keep=0)
    
    def reduced_B(self) -> DensityMatrix:
        """Reduced density matrix of subsystem B."""
        return self.rho.partial_trace(self.dims, keep=1)
    
    def entanglement_entropy(self) -> float:
        """
        Entanglement entropy: S(ρ_A) = S(ρ_B) for pure states.
        """
        rho_A = self.reduced_A()
        return rho_A.von_neumann_entropy()
    
    def mutual_information(self) -> float:
        """
        Quantum mutual information: I(A:B) = S(A) + S(B) - S(AB).
        """
        S_A = self.reduced_A().von_neumann_entropy()
        S_B = self.reduced_B().von_neumann_entropy()
        S_AB = self.rho.von_neumann_entropy()
        return S_A + S_B - S_AB
    
    def negativity(self) -> float:
        """
        Negativity: N(ρ) = (||ρ^{T_A}||_1 - 1)/2.
        
        Non-zero for entangled states (PPT criterion).
        """
        d_A, d_B = self.dims
        
        # Partial transpose on A
        rho_reshaped = self.rho.matrix.reshape(d_A, d_B, d_A, d_B)
        rho_pt = np.einsum('ijkl->kjil', rho_reshaped)
        rho_pt = rho_pt.reshape(d_A * d_B, d_A * d_B)
        
        # Trace norm = sum of singular values
        singular_values = np.linalg.svd(rho_pt, compute_uv=False)
        trace_norm = np.sum(singular_values)
        
        return (trace_norm - 1) / 2
    
    def log_negativity(self) -> float:
        """
        Logarithmic negativity: E_N = log_2(||ρ^{T_A}||_1).
        """
        d_A, d_B = self.dims
        
        rho_reshaped = self.rho.matrix.reshape(d_A, d_B, d_A, d_B)
        rho_pt = np.einsum('ijkl->kjil', rho_reshaped)
        rho_pt = rho_pt.reshape(d_A * d_B, d_A * d_B)
        
        singular_values = np.linalg.svd(rho_pt, compute_uv=False)
        trace_norm = np.sum(singular_values)
        
        return np.log2(trace_norm) if trace_norm > 0 else 0
    
    def concurrence(self) -> float:
        """
        Concurrence for 2-qubit states.
        
        C(ρ) = max(0, λ_1 - λ_2 - λ_3 - λ_4)
        where λ_i are eigenvalues of √(√ρ ρ̃ √ρ).
        """
        if self.dims != (2, 2):
            raise ValueError("Concurrence only defined for 2x2 systems")
        
        # Spin-flip: ρ̃ = (σ_y ⊗ σ_y) ρ* (σ_y ⊗ σ_y)
        sigma_y = np.array([[0, -1j], [1j, 0]], dtype=np.complex128)
        Y = np.kron(sigma_y, sigma_y)
        
        rho_tilde = Y @ self.rho.matrix.conj() @ Y
        
        sqrt_rho = self.rho._matrix_sqrt(self.rho.matrix)
        R = sqrt_rho @ rho_tilde @ sqrt_rho
        
        eigenvalues = np.sqrt(np.maximum(np.linalg.eigvalsh(R), 0))
        eigenvalues = np.sort(eigenvalues)[::-1]
        
        return max(0, eigenvalues[0] - np.sum(eigenvalues[1:]))


# ═══════════════════════════════════════════════════════════════════════════════
# PAULI OPERATORS
# ═══════════════════════════════════════════════════════════════════════════════

class PauliOperators:
    """Standard Pauli operators for qubits."""
    
    I = np.array([[1, 0], [0, 1]], dtype=np.complex128)
    X = np.array([[0, 1], [1, 0]], dtype=np.complex128)
    Y = np.array([[0, -1j], [1j, 0]], dtype=np.complex128)
    Z = np.array([[1, 0], [0, -1]], dtype=np.complex128)
    
    @classmethod
    def basis(cls) -> List[NDArray[np.complex128]]:
        """Pauli basis {I, X, Y, Z}."""
        return [cls.I, cls.X, cls.Y, cls.Z]
    
    @classmethod
    def decompose(cls, M: NDArray) -> List[complex]:
        """Decompose 2x2 matrix in Pauli basis."""
        coeffs = []
        for P in cls.basis():
            coeffs.append(np.trace(P @ M) / 2)
        return coeffs


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def density_matrix(matrix: NDArray) -> DensityMatrix:
    """Create density matrix."""
    return DensityMatrix(matrix)


def pure_state(state: NDArray) -> DensityMatrix:
    """Create pure state density matrix."""
    return DensityMatrix.pure(state)


def von_neumann_entropy(rho: DensityMatrix) -> float:
    """Compute von Neumann entropy."""
    return rho.von_neumann_entropy()


def fidelity(rho: DensityMatrix, sigma: DensityMatrix) -> float:
    """Compute fidelity between states."""
    return rho.fidelity(sigma)


def negativity(rho: DensityMatrix, dims: Tuple[int, int]) -> float:
    """Compute negativity."""
    return EntanglementMeasures(rho, dims).negativity()


def depolarizing_channel(d: int, p: float) -> QuantumChannel:
    """Create depolarizing channel."""
    return QuantumChannel.depolarizing(d, p)


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Core
    'DensityMatrix',
    
    # Channels
    'QuantumChannel',
    
    # Entanglement
    'EntanglementMeasures',
    
    # Pauli
    'PauliOperators',
    
    # Functions
    'density_matrix',
    'pure_state',
    'von_neumann_entropy',
    'fidelity',
    'negativity',
    'depolarizing_channel',
]
