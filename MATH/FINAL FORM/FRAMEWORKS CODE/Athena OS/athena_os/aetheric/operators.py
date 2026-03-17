"""
ATHENA OS - AETHERIC OPERATORS
==============================
Sector Operators and Meta-Hybrid Construction

From Aetheric_Meta-Hybrid_Calculus.docx:

SECTOR OPERATORS:
    D - Discrete operator (graph Laplacians, generators)
    Ω - Continuous operator (differential, pseudo-differential)
    Σ - Stochastic operator (Markov, Fokker-Planck)
    R - Recursive operator (RG flows, scale transitions)

META-HYBRID OPERATOR:
    ℋ_c = Σ_E (α^(c,A) O_E^A + α^(c,Ā) O_E^Ā + α^(c,in) O_E^in + α^(c,out) O_E^out)
    
    Where O_E combines D, Ω, Σ, R projected onto element and aether sectors.

FIELD EQUATION:
    ℋ_c Ψ_c = 0
    
    Compatibility condition among discrete, continuous, stochastic,
    and recursive dynamics.

DIMENSIONAL LIFTS:
    256 → 1024 super-crystal by including Aether poles as explicit factors.
    Higher-dimensional meta-constants arise as eigenvalues of ℋ_full.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Callable, Any
import numpy as np
from abc import ABC, abstractmethod
import math
import cmath

from .core import (
    FundamentalConstant, Shape, Element, AetherPole,
    OperationCoord, OperationCrystal, AethericCoupling,
    HybridState, TextureFunctional
)


# =============================================================================
# BASE SECTOR OPERATOR
# =============================================================================

class SectorOperator(ABC):
    """
    Abstract base for sector operators.
    
    Each sector operator (D, Ω, Σ, R) acts on a specific shape.
    """
    
    def __init__(self, shape: Shape, dimension: int = 8):
        self.shape = shape
        self.dimension = dimension
        self._matrix: Optional[np.ndarray] = None
    
    @property
    @abstractmethod
    def symbol(self) -> str:
        """Get operator symbol."""
        pass
    
    @abstractmethod
    def build_matrix(self) -> np.ndarray:
        """Build the operator matrix representation."""
        pass
    
    @property
    def matrix(self) -> np.ndarray:
        """Get or build the matrix."""
        if self._matrix is None:
            self._matrix = self.build_matrix()
        return self._matrix
    
    def apply(self, state: np.ndarray) -> np.ndarray:
        """Apply operator to state vector."""
        return self.matrix @ state
    
    def eigenvalues(self) -> np.ndarray:
        """Compute eigenvalues."""
        return np.linalg.eigvals(self.matrix)
    
    def spectral_gap(self) -> float:
        """Compute spectral gap (smallest nonzero eigenvalue)."""
        eigs = np.abs(self.eigenvalues())
        eigs = eigs[eigs > 1e-10]  # Remove zeros
        return np.min(eigs) if len(eigs) > 0 else 0.0


# =============================================================================
# DISCRETE OPERATOR (D) - SQUARE
# =============================================================================

class DiscreteOperator(SectorOperator):
    """
    Discrete operator D for Square shape.
    
    Examples: graph Laplacians, adjacency operators, 
    combinatorial generators.
    """
    
    def __init__(self, dimension: int = 8, 
                 boundary: str = "periodic",
                 coupling: float = 1.0):
        super().__init__(Shape.SQUARE, dimension)
        self.boundary = boundary
        self.coupling = coupling
    
    @property
    def symbol(self) -> str:
        return "D"
    
    def build_matrix(self) -> np.ndarray:
        """
        Build discrete Laplacian matrix.
        
        L = (1/h²) * tridiag(1, -2, 1) with boundary conditions.
        """
        N = self.dimension
        h = 1.0 / N
        
        # Build tridiagonal Laplacian
        L = np.zeros((N, N), dtype=complex)
        
        for i in range(N):
            L[i, i] = -2.0 * self.coupling / (h * h)
            if i > 0:
                L[i, i-1] = 1.0 * self.coupling / (h * h)
            if i < N - 1:
                L[i, i+1] = 1.0 * self.coupling / (h * h)
        
        # Periodic boundary
        if self.boundary == "periodic":
            L[0, N-1] = 1.0 * self.coupling / (h * h)
            L[N-1, 0] = 1.0 * self.coupling / (h * h)
        
        return L
    
    def adjacency_matrix(self) -> np.ndarray:
        """Build adjacency matrix (for graph perspective)."""
        N = self.dimension
        A = np.zeros((N, N), dtype=complex)
        
        for i in range(N):
            if i > 0:
                A[i, i-1] = 1.0
            if i < N - 1:
                A[i, i+1] = 1.0
        
        if self.boundary == "periodic":
            A[0, N-1] = 1.0
            A[N-1, 0] = 1.0
        
        return A


# =============================================================================
# CONTINUOUS OPERATOR (Ω) - FLOWER
# =============================================================================

class ContinuousOperator(SectorOperator):
    """
    Continuous operator Ω for Flower shape.
    
    Examples: differential operators, Laplacians on manifolds,
    pseudo-differential operators.
    """
    
    def __init__(self, dimension: int = 16,
                 order: int = 2,
                 coefficient: float = 1.0):
        super().__init__(Shape.FLOWER, dimension)
        self.order = order
        self.coefficient = coefficient
    
    @property
    def symbol(self) -> str:
        return "Ω"
    
    def build_matrix(self) -> np.ndarray:
        """
        Build Fourier-basis representation of differential operator.
        
        For -d²/dx² on [0,1] with periodic BC:
        Eigenvalues are (2πk)² for k = 0, 1, ..., M-1
        """
        M = self.dimension
        
        # Diagonal matrix of eigenvalues
        Omega = np.zeros((M, M), dtype=complex)
        
        for k in range(M):
            # Eigenvalue of -d²/dx² in Fourier basis
            eigenval = (2 * np.pi * k) ** self.order
            Omega[k, k] = self.coefficient * eigenval
        
        return Omega
    
    def heat_kernel(self, t: float) -> np.ndarray:
        """
        Compute heat kernel exp(-tΩ).
        """
        return np.diag(np.exp(-t * np.diag(self.matrix)))
    
    def resolvent(self, z: complex) -> np.ndarray:
        """
        Compute resolvent (zI - Ω)^(-1).
        """
        return np.linalg.inv(z * np.eye(self.dimension) - self.matrix)


# =============================================================================
# STOCHASTIC OPERATOR (Σ) - CLOUD
# =============================================================================

class StochasticOperator(SectorOperator):
    """
    Stochastic operator Σ for Cloud shape.
    
    Examples: Markov generators, Fokker-Planck operators,
    diffusion generators.
    """
    
    def __init__(self, dimension: int = 8,
                 transition_rate: float = 1.0,
                 diffusion: float = 0.5):
        super().__init__(Shape.CLOUD, dimension)
        self.transition_rate = transition_rate
        self.diffusion = diffusion
    
    @property
    def symbol(self) -> str:
        return "Σ"
    
    def build_matrix(self) -> np.ndarray:
        """
        Build Markov generator matrix Q.
        
        Q has: off-diagonal ≥ 0, diagonal ≤ 0, row sums = 0.
        """
        N = self.dimension
        Q = np.zeros((N, N), dtype=complex)
        
        # Build nearest-neighbor Markov generator
        for i in range(N):
            # Transition rates to neighbors
            if i > 0:
                Q[i, i-1] = self.transition_rate * (1 + self.diffusion)
            if i < N - 1:
                Q[i, i+1] = self.transition_rate * (1 - self.diffusion)
            
            # Diagonal: negative sum of off-diagonal
            Q[i, i] = -np.sum(Q[i, :]) + Q[i, i]
        
        return Q
    
    def stationary_distribution(self) -> np.ndarray:
        """
        Compute stationary distribution π where πQ = 0.
        """
        # Find left eigenvector with eigenvalue 0
        evals, evecs = np.linalg.eig(self.matrix.T)
        idx = np.argmin(np.abs(evals))
        pi = np.abs(evecs[:, idx])
        return pi / np.sum(pi)
    
    def mixing_time(self, epsilon: float = 0.25) -> float:
        """
        Estimate mixing time from spectral gap.
        
        t_mix ≈ (1/gap) * log(1/ε)
        """
        gap = self.spectral_gap()
        if gap > 0:
            return (1.0 / gap) * np.log(1.0 / epsilon)
        return float('inf')


# =============================================================================
# RECURSIVE OPERATOR (R) - FRACTAL
# =============================================================================

class RecursiveOperator(SectorOperator):
    """
    Recursive operator R for Fractal shape.
    
    Examples: RG flow operators, scale transition maps,
    coarse-graining operators.
    """
    
    def __init__(self, dimension: int = 4,
                 scaling_factor: float = 0.5,
                 coupling: float = 1.0):
        super().__init__(Shape.FRACTAL, dimension)
        self.scaling_factor = scaling_factor  # < 1 for contraction
        self.coupling = coupling
    
    @property
    def symbol(self) -> str:
        return "R"
    
    def build_matrix(self) -> np.ndarray:
        """
        Build RG flow matrix.
        
        Lower-triangular with scale coupling:
        R[ℓ, ℓ'] = coupling * scaling^(ℓ-ℓ') for ℓ > ℓ'
        """
        L = self.dimension
        R = np.zeros((L, L), dtype=complex)
        
        for ell in range(L):
            # Diagonal: self-coupling
            R[ell, ell] = -self.coupling
            
            # Lower diagonal: scale flow
            for ell_prime in range(ell):
                R[ell, ell_prime] = self.coupling * (self.scaling_factor ** (ell - ell_prime))
        
        return R
    
    def fixed_point(self) -> Optional[np.ndarray]:
        """
        Compute fixed point of RG flow: Rψ* = 0.
        """
        # Null space of R
        U, S, Vh = np.linalg.svd(self.matrix)
        null_mask = S < 1e-10
        if np.any(null_mask):
            null_idx = np.argmax(null_mask)
            return Vh[null_idx, :]
        return None
    
    def critical_exponent(self) -> float:
        """
        Extract critical exponent from leading eigenvalue.
        """
        eigs = self.eigenvalues()
        nonzero_eigs = eigs[np.abs(eigs) > 1e-10]
        if len(nonzero_eigs) > 0:
            return -np.log(np.min(np.abs(nonzero_eigs))) / np.log(self.scaling_factor)
        return 0.0


# =============================================================================
# AETHERIC SECTOR DECOMPOSITION
# =============================================================================

class AethericSectorOperator:
    """
    Sector operator decomposed into Aether poles.
    
    O_E = O_E^A + O_E^Ā + O_E^in + O_E^out
    """
    
    def __init__(self, base_operator: SectorOperator, element: Element):
        self.base = base_operator
        self.element = element
        
        # Compute Aether pole components
        self._components: Dict[AetherPole, np.ndarray] = {}
        self._decompose()
    
    def _decompose(self):
        """
        Decompose operator into Aether pole components.
        
        A (primal): (O + O†)/2 (self-adjoint part)
        Ā (adjoint): (O - O†)/2i (skew-adjoint part)
        in (inner): [O, O†]/2 (commutator structure)
        out (outer): {O, O†}/2 - ||O||² I (shell structure)
        """
        O = self.base.matrix
        O_dag = O.conj().T
        
        # Primal: Hermitian part
        self._components[AetherPole.PRIMAL] = (O + O_dag) / 2
        
        # Adjoint: Skew-Hermitian part
        self._components[AetherPole.ADJOINT] = (O - O_dag) / (2j)
        
        # Inner: Commutator structure
        commutator = O @ O_dag - O_dag @ O
        self._components[AetherPole.INNER] = commutator / 2
        
        # Outer: Anticommutator minus trace
        anticommutator = O @ O_dag + O_dag @ O
        trace_term = np.trace(anticommutator) / O.shape[0] * np.eye(O.shape[0])
        self._components[AetherPole.OUTER] = anticommutator / 2 - trace_term
    
    def get_component(self, pole: AetherPole) -> np.ndarray:
        """Get component for a specific pole."""
        return self._components[pole]
    
    def weighted_sum(self, coupling: AethericCoupling) -> np.ndarray:
        """
        Compute weighted sum of components.
        
        Σ_p α^(c,p) O_E^p
        """
        result = np.zeros_like(self.base.matrix)
        
        for pole in AetherPole:
            alpha = coupling.get(self.element, pole)
            result += alpha * self._components[pole]
        
        return result


# =============================================================================
# META-HYBRID OPERATOR (ℋ_c)
# =============================================================================

class MetaHybridOperator:
    """
    The Meta-Hybrid Operator ℋ_c for a fundamental constant.
    
    ℋ_c = Σ_E (α^(c,A) O_E^A + α^(c,Ā) O_E^Ā + α^(c,in) O_E^in + α^(c,out) O_E^out)
    
    Where O_E combines D, Ω, Σ, R projected onto elements.
    """
    
    def __init__(self, constant: FundamentalConstant,
                 N_discrete: int = 8,
                 M_continuous: int = 16,
                 L_scale: int = 4):
        self.constant = constant
        self.N_discrete = N_discrete
        self.M_continuous = M_continuous
        self.L_scale = L_scale
        
        # Total dimension
        self.dimension = N_discrete * M_continuous * L_scale
        
        # Get coupling
        self.coupling = self._get_canonical_coupling()
        
        # Build sector operators
        self.D = DiscreteOperator(N_discrete)
        self.Omega = ContinuousOperator(M_continuous)
        self.Sigma = StochasticOperator(N_discrete)
        self.R = RecursiveOperator(L_scale)
        
        # Build Aetheric decompositions
        self._aetheric_ops: Dict[Element, AethericSectorOperator] = {}
        self._build_aetheric_operators()
        
        # Cache full operator
        self._matrix: Optional[np.ndarray] = None
    
    def _get_canonical_coupling(self) -> AethericCoupling:
        """Get canonical coupling for this constant."""
        return {
            FundamentalConstant.PI: AethericCoupling.pi_coupling(),
            FundamentalConstant.E: AethericCoupling.e_coupling(),
            FundamentalConstant.I: AethericCoupling.i_coupling(),
            FundamentalConstant.PHI: AethericCoupling.phi_coupling()
        }[self.constant]
    
    def _build_aetheric_operators(self):
        """Build Aetheric decomposition for each element."""
        # Earth ↔ Square (discrete/structural)
        self._aetheric_ops[Element.EARTH] = AethericSectorOperator(self.D, Element.EARTH)
        
        # Water ↔ Flower (continuous/flow)
        self._aetheric_ops[Element.WATER] = AethericSectorOperator(self.Omega, Element.WATER)
        
        # Fire ↔ Cloud (stochastic/transformation)
        self._aetheric_ops[Element.FIRE] = AethericSectorOperator(self.Sigma, Element.FIRE)
        
        # Air ↔ Fractal (recursive/spectral)
        self._aetheric_ops[Element.AIR] = AethericSectorOperator(self.R, Element.AIR)
    
    @property
    def matrix(self) -> np.ndarray:
        """
        Build the full meta-hybrid operator matrix.
        
        Uses Kronecker products to combine sectors.
        """
        if self._matrix is not None:
            return self._matrix
        
        N, M, L = self.N_discrete, self.M_continuous, self.L_scale
        dim = N * M * L
        
        # Initialize
        H = np.zeros((dim, dim), dtype=complex)
        
        # Build using Kronecker structure
        I_N = np.eye(N, dtype=complex)
        I_M = np.eye(M, dtype=complex)
        I_L = np.eye(L, dtype=complex)
        
        # Earth (D) contribution: D ⊗ I_M ⊗ I_L
        for pole in AetherPole:
            alpha = self.coupling.get(Element.EARTH, pole)
            D_comp = self._aetheric_ops[Element.EARTH].get_component(pole)
            H += alpha * np.kron(np.kron(D_comp, I_M), I_L)
        
        # Water (Ω) contribution: I_N ⊗ Ω ⊗ I_L
        for pole in AetherPole:
            alpha = self.coupling.get(Element.WATER, pole)
            Omega_comp = self._aetheric_ops[Element.WATER].get_component(pole)
            H += alpha * np.kron(np.kron(I_N, Omega_comp), I_L)
        
        # Fire (Σ) contribution: Σ ⊗ I_M ⊗ I_L (shares discrete space)
        for pole in AetherPole:
            alpha = self.coupling.get(Element.FIRE, pole)
            Sigma_comp = self._aetheric_ops[Element.FIRE].get_component(pole)
            H += alpha * np.kron(np.kron(Sigma_comp, I_M), I_L)
        
        # Air (R) contribution: I_N ⊗ I_M ⊗ R
        for pole in AetherPole:
            alpha = self.coupling.get(Element.AIR, pole)
            R_comp = self._aetheric_ops[Element.AIR].get_component(pole)
            H += alpha * np.kron(np.kron(I_N, I_M), R_comp)
        
        self._matrix = H
        return H
    
    def apply(self, state: HybridState) -> np.ndarray:
        """Apply ℋ_c to a hybrid state."""
        return self.matrix @ state.amplitudes
    
    def eigenvalues(self) -> np.ndarray:
        """Compute eigenvalues of ℋ_c."""
        return np.linalg.eigvals(self.matrix)
    
    def ground_state(self) -> Tuple[complex, np.ndarray]:
        """
        Compute ground state (lowest eigenvalue).
        
        Returns (eigenvalue, eigenvector).
        """
        evals, evecs = np.linalg.eig(self.matrix)
        idx = np.argmin(np.abs(evals))
        return evals[idx], evecs[:, idx]
    
    def spectral_invariant(self) -> complex:
        """
        Extract spectral invariant associated with constant.
        
        This is related to how the constant emerges from the spectrum.
        """
        evals = self.eigenvalues()
        
        # Characteristic spectral measure depends on constant
        if self.constant == FundamentalConstant.PI:
            # π appears in spectral gaps of Laplacians
            return np.mean(np.abs(evals[np.abs(evals) > 0.1]))
        
        elif self.constant == FundamentalConstant.E:
            # e appears in exponential decay
            return np.exp(-np.mean(np.abs(evals)))
        
        elif self.constant == FundamentalConstant.I:
            # i relates to phase structure
            phases = np.angle(evals)
            return np.mean(np.exp(1j * phases))
        
        else:  # PHI
            # φ appears in eigenvalue ratios
            sorted_evals = np.sort(np.abs(evals))
            ratios = sorted_evals[1:] / (sorted_evals[:-1] + 1e-10)
            return np.mean(ratios)


# =============================================================================
# FULL COUPLED SYSTEM (ℍ_full)
# =============================================================================

class FullHybridSystem:
    """
    The fully coupled meta-hybrid system ℍ_full.
    
    Couples all four constant operators:
    ℍ_full acts on Ψ⃗ = (Ψ_π, Ψ_e, Ψ_i, Ψ_φ)ᵀ
    
    Meta-constants at dimension N+1 arise as eigenvalues of ℍ_full.
    """
    
    def __init__(self, N_discrete: int = 4, M_continuous: int = 8, L_scale: int = 2):
        self.N_discrete = N_discrete
        self.M_continuous = M_continuous
        self.L_scale = L_scale
        
        # Single-constant dimension
        self.sector_dim = N_discrete * M_continuous * L_scale
        
        # Full dimension (4× for four constants)
        self.dimension = 4 * self.sector_dim
        
        # Build individual operators
        self.H_pi = MetaHybridOperator(FundamentalConstant.PI, N_discrete, M_continuous, L_scale)
        self.H_e = MetaHybridOperator(FundamentalConstant.E, N_discrete, M_continuous, L_scale)
        self.H_i = MetaHybridOperator(FundamentalConstant.I, N_discrete, M_continuous, L_scale)
        self.H_phi = MetaHybridOperator(FundamentalConstant.PHI, N_discrete, M_continuous, L_scale)
        
        # Cross-coupling coefficients
        self.kappa = self._initialize_cross_coupling()
        
        # Cache
        self._matrix: Optional[np.ndarray] = None
    
    def _initialize_cross_coupling(self) -> Dict[Tuple[FundamentalConstant, FundamentalConstant], complex]:
        """Initialize cross-coupling between constants."""
        kappa = {}
        
        # Canonical cross-couplings (symmetric)
        kappa[(FundamentalConstant.PI, FundamentalConstant.E)] = 0.1
        kappa[(FundamentalConstant.PI, FundamentalConstant.I)] = 0.2j
        kappa[(FundamentalConstant.PI, FundamentalConstant.PHI)] = 0.05
        kappa[(FundamentalConstant.E, FundamentalConstant.I)] = 0.15
        kappa[(FundamentalConstant.E, FundamentalConstant.PHI)] = 0.1
        kappa[(FundamentalConstant.I, FundamentalConstant.PHI)] = 0.1j
        
        # Symmetrize
        for (c1, c2), v in list(kappa.items()):
            kappa[(c2, c1)] = v.conjugate()
        
        # Diagonal (self-coupling = 0 additional)
        for c in FundamentalConstant:
            kappa[(c, c)] = 0.0
        
        return kappa
    
    @property
    def matrix(self) -> np.ndarray:
        """
        Build the full coupled system matrix.
        
        ℍ_full = diag(ℋ_π, ℋ_e, ℋ_i, ℋ_φ) + K
        
        Where K encodes cross-couplings.
        """
        if self._matrix is not None:
            return self._matrix
        
        dim = self.dimension
        sdim = self.sector_dim
        
        H_full = np.zeros((dim, dim), dtype=complex)
        
        # Diagonal blocks
        H_full[0:sdim, 0:sdim] = self.H_pi.matrix
        H_full[sdim:2*sdim, sdim:2*sdim] = self.H_e.matrix
        H_full[2*sdim:3*sdim, 2*sdim:3*sdim] = self.H_i.matrix
        H_full[3*sdim:4*sdim, 3*sdim:4*sdim] = self.H_phi.matrix
        
        # Cross-coupling blocks
        constants = list(FundamentalConstant)
        for i, c1 in enumerate(constants):
            for j, c2 in enumerate(constants):
                if i != j:
                    k_val = self.kappa.get((c1, c2), 0.0)
                    # Simple coupling: scalar times identity
                    block = k_val * np.eye(sdim, dtype=complex)
                    H_full[i*sdim:(i+1)*sdim, j*sdim:(j+1)*sdim] = block
        
        self._matrix = H_full
        return H_full
    
    def eigenvalues(self) -> np.ndarray:
        """Compute eigenvalues (meta-constants at N+1)."""
        return np.linalg.eigvals(self.matrix)
    
    def meta_constants(self, n_top: int = 4) -> List[complex]:
        """
        Extract leading meta-constants.
        
        These are stable eigenvalue clusters that represent
        higher-dimensional analogues of (π, e, i, φ).
        """
        evals = self.eigenvalues()
        
        # Sort by magnitude
        sorted_evals = evals[np.argsort(np.abs(evals))]
        
        # Return smallest non-zero eigenvalues (most stable)
        nonzero = sorted_evals[np.abs(sorted_evals) > 1e-10]
        
        return list(nonzero[:n_top])
    
    def constant_mixing_matrix(self) -> np.ndarray:
        """
        Compute how constants mix under the full dynamics.
        
        Returns 4×4 effective mixing matrix.
        """
        sdim = self.sector_dim
        mixing = np.zeros((4, 4), dtype=complex)
        
        for i in range(4):
            for j in range(4):
                # Average coupling between sectors
                block = self.matrix[i*sdim:(i+1)*sdim, j*sdim:(j+1)*sdim]
                mixing[i, j] = np.mean(np.abs(block))
        
        return mixing


# =============================================================================
# DIMENSIONAL LIFT (256 → 1024)
# =============================================================================

class DimensionalLift:
    """
    Dimensional lift from 256 to 1024 operation super-crystal.
    
    At dimension N+1, Aether poles become explicit tensor factors.
    """
    
    def __init__(self, crystal: OperationCrystal):
        self.base_crystal = crystal
        self._super_crystal: Optional[np.ndarray] = None
    
    def lift(self) -> np.ndarray:
        """
        Perform dimensional lift: 256 → 1024.
        
        1024 = 256 × 4 (base crystal × Aether pole index)
        """
        if self._super_crystal is not None:
            return self._super_crystal
        
        # 1024-dimensional index space
        super_crystal = np.zeros((1024, 1024), dtype=complex)
        
        # Each 256 cell spawns 4 cells (one per Aether pole as explicit factor)
        for base_idx in range(256):
            base_cell = self.base_crystal[base_idx]
            
            for aether_idx, pole in enumerate(AetherPole):
                # Super-index = base_idx * 4 + aether_idx
                super_idx = base_idx * 4 + aether_idx
                
                # Coupling inherits from base with pole-dependent phase
                phase = {
                    AetherPole.PRIMAL: 1.0,
                    AetherPole.ADJOINT: -1.0,
                    AetherPole.INNER: 1j,
                    AetherPole.OUTER: -1j
                }[pole]
                
                super_crystal[super_idx, super_idx] = base_cell.coupling * phase
        
        self._super_crystal = super_crystal
        return super_crystal
    
    def project_down(self, super_state: np.ndarray) -> np.ndarray:
        """
        Project from 1024 back to 256 by averaging over Aether poles.
        """
        base_state = np.zeros(256, dtype=complex)
        
        for base_idx in range(256):
            # Average over 4 Aether copies
            for aether_idx in range(4):
                super_idx = base_idx * 4 + aether_idx
                base_state[base_idx] += super_state[super_idx]
            base_state[base_idx] /= 4
        
        return base_state


# =============================================================================
# VALIDATION
# =============================================================================

def validate_operators() -> bool:
    """Validate aetheric operators module."""
    
    # Test discrete operator
    D = DiscreteOperator(dimension=8)
    assert D.matrix.shape == (8, 8)
    assert np.allclose(D.matrix, D.matrix.T.conj())  # Hermitian
    
    # Test continuous operator
    Omega = ContinuousOperator(dimension=16)
    assert Omega.matrix.shape == (16, 16)
    eigs = Omega.eigenvalues()
    assert np.all(np.real(eigs) >= 0)  # Non-negative
    
    # Test stochastic operator
    Sigma = StochasticOperator(dimension=8)
    assert Sigma.matrix.shape == (8, 8)
    row_sums = np.sum(Sigma.matrix, axis=1)
    assert np.allclose(row_sums, 0, atol=1e-10)  # Row sums = 0
    
    # Test recursive operator
    R = RecursiveOperator(dimension=4)
    assert R.matrix.shape == (4, 4)
    
    # Test Aetheric sector decomposition
    aetheric_D = AethericSectorOperator(D, Element.EARTH)
    primal = aetheric_D.get_component(AetherPole.PRIMAL)
    adjoint = aetheric_D.get_component(AetherPole.ADJOINT)
    
    # Primal should be Hermitian
    assert np.allclose(primal, primal.T.conj())
    
    # Test meta-hybrid operator
    H_pi = MetaHybridOperator(FundamentalConstant.PI, N_discrete=4, M_continuous=4, L_scale=2)
    assert H_pi.dimension == 4 * 4 * 2
    
    evals = H_pi.eigenvalues()
    assert len(evals) == H_pi.dimension
    
    # Test full hybrid system
    H_full = FullHybridSystem(N_discrete=2, M_continuous=4, L_scale=2)
    assert H_full.dimension == 4 * (2 * 4 * 2)
    
    meta_consts = H_full.meta_constants(n_top=4)
    assert len(meta_consts) <= 4
    
    # Test dimensional lift
    crystal = OperationCrystal()
    lift = DimensionalLift(crystal)
    super_crystal = lift.lift()
    assert super_crystal.shape == (1024, 1024)
    
    # Test projection
    super_state = np.random.rand(1024) + 1j * np.random.rand(1024)
    base_state = lift.project_down(super_state)
    assert len(base_state) == 256
    
    return True


if __name__ == "__main__":
    print("Validating Aetheric operators...")
    assert validate_operators()
    print("✓ Aetheric operators validated")
