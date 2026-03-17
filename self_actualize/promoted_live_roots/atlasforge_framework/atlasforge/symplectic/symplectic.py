"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      SYMPLECTIC GEOMETRY MODULE                              ║
║                                                                              ║
║  Hamiltonian Mechanics, Phase Space, and Poisson Structures                  ║
║                                                                              ║
║  Core Principle:                                                             ║
║    The quad-polar framework has natural symplectic structure. The           ║
║    gateway scalars form canonical coordinates, and pole weights             ║
║    evolve via Hamiltonian flow.                                             ║
║                                                                              ║
║  Key Structures:                                                             ║
║    - Symplectic form ω = Σ dp_i ∧ dq_i                                      ║
║    - Poisson bracket {f, g} = Σ (∂f/∂q_i ∂g/∂p_i - ∂f/∂p_i ∂g/∂q_i)        ║
║    - Hamiltonian flow: dq/dt = ∂H/∂p, dp/dt = -∂H/∂q                        ║
║    - Canonical transformations preserve ω                                   ║
║                                                                              ║
║  Connection to Framework:                                                    ║
║    - (T, R) ↔ canonical pair (q, p)                                         ║
║    - Pole weights ↔ action-angle variables                                  ║
║    - Gateway hops ↔ symplectomorphisms                                      ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Callable
import numpy as np
from numpy.typing import NDArray


# ═══════════════════════════════════════════════════════════════════════════════
# SYMPLECTIC FORM
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SymplecticForm:
    """
    Symplectic 2-form on a 2n-dimensional manifold.
    
    Standard form: ω = Σ_{i=1}^n dp_i ∧ dq_i
    Matrix representation: J = [[0, I], [-I, 0]]
    """
    dimension: int  # Full dimension (must be even)
    
    def __post_init__(self):
        if self.dimension % 2 != 0:
            raise ValueError("Symplectic dimension must be even")
        self.n = self.dimension // 2
    
    @property
    def matrix(self) -> NDArray[np.float64]:
        """
        Standard symplectic matrix J.
        
        J = [[0, I_n], [-I_n, 0]]
        """
        n = self.n
        J = np.zeros((self.dimension, self.dimension))
        J[:n, n:] = np.eye(n)
        J[n:, :n] = -np.eye(n)
        return J
    
    def evaluate(self, v: NDArray, w: NDArray) -> float:
        """
        Evaluate ω(v, w) = v^T J w.
        """
        return float(v @ self.matrix @ w)
    
    def is_lagrangian(self, subspace: NDArray) -> bool:
        """
        Check if subspace is Lagrangian (ω|_L = 0 and dim L = n).
        
        subspace: matrix whose columns span L
        """
        if subspace.shape[1] != self.n:
            return False
        
        # Check ω(v_i, v_j) = 0 for all basis vectors
        for i in range(self.n):
            for j in range(i, self.n):
                if abs(self.evaluate(subspace[:, i], subspace[:, j])) > 1e-10:
                    return False
        return True
    
    def compatible_complex_structure(self) -> NDArray[np.float64]:
        """
        Standard compatible complex structure J² = -I.
        
        J is already a complex structure: J² = -I
        """
        return self.matrix


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE SPACE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class PhaseSpace:
    """
    Classical phase space with coordinates (q, p).
    """
    n_dof: int  # Number of degrees of freedom
    
    def __post_init__(self):
        self.omega = SymplecticForm(2 * self.n_dof)
    
    @property
    def dimension(self) -> int:
        return 2 * self.n_dof
    
    def coordinates(self, state: NDArray) -> Tuple[NDArray, NDArray]:
        """Split state into (q, p)."""
        return state[:self.n_dof], state[self.n_dof:]
    
    def from_coordinates(self, q: NDArray, p: NDArray) -> NDArray:
        """Combine (q, p) into state vector."""
        return np.concatenate([q, p])
    
    def poisson_bracket(self, df: NDArray, dg: NDArray) -> float:
        """
        Poisson bracket from gradients.
        
        {f, g} = ω(X_f, X_g) = df^T J dg
        """
        return self.omega.evaluate(df, dg)
    
    def hamiltonian_vector_field(self, dH: NDArray) -> NDArray:
        """
        Hamiltonian vector field X_H from gradient of H.
        
        X_H = J · ∇H
        """
        return self.omega.matrix @ dH


# ═══════════════════════════════════════════════════════════════════════════════
# HAMILTONIAN SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class HamiltonianSystem:
    """
    Hamiltonian dynamical system.
    
    dq/dt = ∂H/∂p
    dp/dt = -∂H/∂q
    """
    H: Callable[[NDArray], float]  # Hamiltonian function
    n_dof: int
    
    def __post_init__(self):
        self.phase_space = PhaseSpace(self.n_dof)
    
    def gradient(self, state: NDArray, epsilon: float = 1e-7) -> NDArray:
        """Numerical gradient of H."""
        grad = np.zeros(2 * self.n_dof)
        for i in range(2 * self.n_dof):
            e_i = np.zeros(2 * self.n_dof)
            e_i[i] = epsilon
            grad[i] = (self.H(state + e_i) - self.H(state - e_i)) / (2 * epsilon)
        return grad
    
    def equations_of_motion(self, state: NDArray) -> NDArray:
        """
        Hamilton's equations: dz/dt = J · ∇H
        """
        dH = self.gradient(state)
        return self.phase_space.omega.matrix @ dH
    
    def integrate_symplectic(self, z0: NDArray, t_span: Tuple[float, float],
                            n_steps: int = 1000) -> Tuple[NDArray, NDArray]:
        """
        Symplectic integration using Störmer-Verlet.
        """
        t0, t1 = t_span
        dt = (t1 - t0) / n_steps
        n = self.n_dof
        
        times = np.linspace(t0, t1, n_steps + 1)
        trajectory = np.zeros((n_steps + 1, 2 * n))
        trajectory[0] = z0
        
        q, p = z0[:n].copy(), z0[n:].copy()
        
        for i in range(n_steps):
            # Half step in p
            state = self.phase_space.from_coordinates(q, p)
            dH = self.gradient(state)
            p = p - 0.5 * dt * dH[:n]  # -∂H/∂q
            
            # Full step in q
            state = self.phase_space.from_coordinates(q, p)
            dH = self.gradient(state)
            q = q + dt * dH[n:]  # ∂H/∂p
            
            # Half step in p
            state = self.phase_space.from_coordinates(q, p)
            dH = self.gradient(state)
            p = p - 0.5 * dt * dH[:n]
            
            trajectory[i + 1] = self.phase_space.from_coordinates(q, p)
        
        return times, trajectory
    
    def energy_error(self, trajectory: NDArray) -> NDArray:
        """Compute energy error along trajectory."""
        H0 = self.H(trajectory[0])
        return np.array([self.H(z) - H0 for z in trajectory])


@dataclass
class HarmonicOscillator:
    """
    Simple harmonic oscillator: H = (p² + ω²q²)/2
    """
    omega_freq: float = 1.0
    
    def __post_init__(self):
        self.n_dof = 1
        self.phase_space = PhaseSpace(self.n_dof)
    
    def H(self, z: NDArray) -> float:
        """Hamiltonian."""
        return 0.5 * (z[1]**2 + self.omega_freq**2 * z[0]**2)
    
    def gradient(self, state: NDArray, epsilon: float = 1e-7) -> NDArray:
        """Gradient of H."""
        return np.array([self.omega_freq**2 * state[0], state[1]])
    
    def integrate_symplectic(self, z0: NDArray, t_span: Tuple[float, float],
                            n_steps: int = 1000) -> Tuple[NDArray, NDArray]:
        """Symplectic integration using Störmer-Verlet."""
        t0, t1 = t_span
        dt = (t1 - t0) / n_steps
        
        times = np.linspace(t0, t1, n_steps + 1)
        trajectory = np.zeros((n_steps + 1, 2))
        trajectory[0] = z0
        
        q, p = z0[0], z0[1]
        w = self.omega_freq
        
        for i in range(n_steps):
            # Störmer-Verlet
            p = p - 0.5 * dt * w**2 * q
            q = q + dt * p
            p = p - 0.5 * dt * w**2 * q
            
            trajectory[i + 1] = np.array([q, p])
        
        return times, trajectory
    
    def exact_solution(self, z0: NDArray, t: float) -> NDArray:
        """Analytical solution."""
        q0, p0 = z0[0], z0[1]
        w = self.omega_freq
        
        q = q0 * np.cos(w * t) + (p0 / w) * np.sin(w * t)
        p = -q0 * w * np.sin(w * t) + p0 * np.cos(w * t)
        
        return np.array([q, p])


@dataclass
class KeplerProblem(HamiltonianSystem):
    """
    Kepler/gravitational two-body problem.
    
    H = |p|²/2 - 1/|q|
    """
    
    def __post_init__(self):
        self.n_dof = 2
        self.H = self._kepler_hamiltonian
        super().__post_init__()
    
    def _kepler_hamiltonian(self, z: NDArray) -> float:
        q, p = z[:2], z[2:]
        r = np.linalg.norm(q)
        if r < 1e-10:
            return float('inf')
        return 0.5 * np.dot(p, p) - 1.0 / r


# ═══════════════════════════════════════════════════════════════════════════════
# CANONICAL TRANSFORMATIONS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class CanonicalTransformation:
    """
    Canonical (symplectic) transformation.
    
    Preserves the symplectic form: T*ω = ω
    Equivalently: T^T J T = J
    """
    matrix: NDArray[np.float64]
    
    def __post_init__(self):
        n = self.matrix.shape[0]
        if n % 2 != 0:
            raise ValueError("Matrix must be even-dimensional")
        self.n = n // 2
        
        # Verify symplecticity
        J = SymplecticForm(n).matrix
        residual = self.matrix.T @ J @ self.matrix - J
        if np.max(np.abs(residual)) > 1e-10:
            raise ValueError("Matrix is not symplectic")
    
    def apply(self, z: NDArray) -> NDArray:
        """Apply transformation to phase space point."""
        return self.matrix @ z
    
    def compose(self, other: 'CanonicalTransformation') -> 'CanonicalTransformation':
        """Compose two canonical transformations."""
        return CanonicalTransformation(self.matrix @ other.matrix)
    
    def inverse(self) -> 'CanonicalTransformation':
        """Inverse transformation."""
        return CanonicalTransformation(np.linalg.inv(self.matrix))
    
    @classmethod
    def rotation(cls, n_dof: int, angle: float, plane: Tuple[int, int] = (0, 0)
                ) -> 'CanonicalTransformation':
        """
        Rotation in (q_i, p_i) plane.
        """
        dim = 2 * n_dof
        M = np.eye(dim)
        
        i, j = plane
        c, s = np.cos(angle), np.sin(angle)
        
        M[i, i] = c
        M[i, i + n_dof] = s
        M[i + n_dof, i] = -s
        M[i + n_dof, i + n_dof] = c
        
        return cls(M)
    
    @classmethod
    def scaling(cls, n_dof: int, factor: float) -> 'CanonicalTransformation':
        """
        Canonical scaling: q → λq, p → p/λ
        """
        dim = 2 * n_dof
        M = np.eye(dim)
        M[:n_dof, :n_dof] *= factor
        M[n_dof:, n_dof:] /= factor
        return cls(M)


# ═══════════════════════════════════════════════════════════════════════════════
# ACTION-ANGLE VARIABLES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ActionAngleVariables:
    """
    Action-angle variables for integrable systems.
    
    For integrable system with n degrees of freedom:
    - Actions I_i are constants of motion
    - Angles θ_i evolve linearly: θ_i(t) = ω_i t + θ_i(0)
    """
    actions: NDArray[np.float64]  # I_1, ..., I_n
    angles: NDArray[np.float64]   # θ_1, ..., θ_n
    frequencies: NDArray[np.float64]  # ω_1, ..., ω_n
    
    def evolve(self, t: float) -> 'ActionAngleVariables':
        """Evolve angles by time t."""
        new_angles = (self.angles + self.frequencies * t) % (2 * np.pi)
        return ActionAngleVariables(self.actions.copy(), new_angles, 
                                   self.frequencies.copy())
    
    @classmethod
    def from_harmonic_oscillator(cls, q: float, p: float, omega: float
                                ) -> 'ActionAngleVariables':
        """
        Action-angle for harmonic oscillator.
        
        I = (p² + ω²q²)/(2ω) = E/ω
        θ = arctan(ωq/p)
        """
        I = (p**2 + omega**2 * q**2) / (2 * omega)
        theta = np.arctan2(omega * q, p)
        
        return cls(
            np.array([I]),
            np.array([theta]),
            np.array([omega])
        )
    
    def to_cartesian(self, omega: float = 1.0) -> Tuple[float, float]:
        """
        Convert back to (q, p) for 1D harmonic oscillator.
        """
        I = self.actions[0]
        theta = self.angles[0]
        
        q = np.sqrt(2 * I / omega) * np.sin(theta)
        p = np.sqrt(2 * I * omega) * np.cos(theta)
        
        return q, p


# ═══════════════════════════════════════════════════════════════════════════════
# GATEWAY SYMPLECTIC STRUCTURE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class GatewaySymplecticBridge:
    """
    Symplectic structure of the gateway algebra.
    
    The gateway parameters (T, R) form a canonical pair
    with the constraint T² + R² < 1 (Poincaré disk).
    """
    
    @staticmethod
    def gateway_to_phase_space(T: float, R: float) -> NDArray:
        """
        Map gateway (T, R) to phase space (q, p).
        
        Using identification q = T, p = R.
        """
        return np.array([T, R])
    
    @staticmethod
    def phase_space_to_gateway(q: float, p: float) -> Tuple[float, float]:
        """Map (q, p) back to gateway (T, R)."""
        return q, p
    
    @staticmethod
    def gateway_poisson_bracket(dF_dT: float, dF_dR: float,
                                dG_dT: float, dG_dR: float) -> float:
        """
        Poisson bracket for functions F, G of (T, R).
        
        {F, G} = ∂F/∂T · ∂G/∂R - ∂F/∂R · ∂G/∂T
        """
        return dF_dT * dG_dR - dF_dR * dG_dT
    
    @staticmethod
    def rapidity_action(T: float) -> float:
        """
        Action variable corresponding to gateway T.
        
        I = (1/2) log((1+T)/(1-T)) = artanh(T)
        """
        if abs(T) >= 1:
            return float('inf') if T > 0 else float('-inf')
        return np.arctanh(T)


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def symplectic_form(dimension: int) -> NDArray:
    """Standard symplectic matrix."""
    return SymplecticForm(dimension).matrix


def poisson_bracket(phase_space: PhaseSpace, df: NDArray, dg: NDArray) -> float:
    """Compute Poisson bracket."""
    return phase_space.poisson_bracket(df, dg)


def harmonic_oscillator(omega: float = 1.0) -> HarmonicOscillator:
    """Create harmonic oscillator system."""
    return HarmonicOscillator(omega_freq=omega)


def kepler_problem() -> KeplerProblem:
    """Create Kepler problem."""
    return KeplerProblem()


def canonical_rotation(n_dof: int, angle: float) -> CanonicalTransformation:
    """Canonical rotation transformation."""
    return CanonicalTransformation.rotation(n_dof, angle)


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Symplectic structure
    'SymplecticForm',
    'PhaseSpace',
    
    # Hamiltonian systems
    'HamiltonianSystem',
    'HarmonicOscillator',
    'KeplerProblem',
    
    # Transformations
    'CanonicalTransformation',
    
    # Action-angle
    'ActionAngleVariables',
    
    # Bridge
    'GatewaySymplecticBridge',
    
    # Functions
    'symplectic_form',
    'poisson_bracket',
    'harmonic_oscillator',
    'kepler_problem',
    'canonical_rotation',
]
