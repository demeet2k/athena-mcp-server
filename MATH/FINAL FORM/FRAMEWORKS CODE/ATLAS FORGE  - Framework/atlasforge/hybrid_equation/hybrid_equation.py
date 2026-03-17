"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    HYBRID EQUATION GENERATOR MODULE                          ║
║                                                                              ║
║  Quad-Polar Hybrid Equations: D + Ω + Σ + Ψ                                  ║
║                                                                              ║
║  Four Fundamental Operators:                                                 ║
║    D (Earth/Discrete)   : Combinatorial, graph Laplacians, constraints       ║
║    Ω (Water/Continuous) : Differential, geometric flow, PDEs                 ║
║    Σ (Fire/Stochastic)  : Random expansion, noise, MCMC                      ║
║    Ψ (Air/Recursive)    : Renormalization, multigrid, hierarchical           ║
║                                                                              ║
║  Hybrid Generators:                                                          ║
║    G = D + Ω           : Discrete-Continuous hybrid                          ║
║    G_vert = Σ + Ψ      : Expansion-Recursion vertical                        ║
║    G_full = D + Ω + Σ + Ψ : Full quad-polar                                 ║
║                                                                              ║
║  Shortcut Patterns:                                                          ║
║    relax-project, flow-prune, predict-correct, spectral-combinatorial        ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Any, Callable, Union
from enum import Enum
import numpy as np
from numpy.typing import NDArray


# ═══════════════════════════════════════════════════════════════════════════════
# OPERATOR POLES
# ═══════════════════════════════════════════════════════════════════════════════

class OperatorPole(Enum):
    """The four fundamental operator poles."""
    D = "discrete"      # Earth: combinatorial, graph, constraint
    OMEGA = "continuous" # Water: differential, geometric, PDE
    SIGMA = "stochastic" # Fire: random, noise, MCMC
    PSI = "recursive"    # Air: renormalization, multigrid, hierarchical


class HybridPattern(Enum):
    """Canonical hybrid shortcut patterns."""
    RELAX_PROJECT = "relax_project"       # Continuous relax → discrete project
    FLOW_PRUNE = "flow_prune"             # Continuous flow → discrete prune
    PREDICT_CORRECT = "predict_correct"   # Predict → correct cycle
    SPECTRAL_COMB = "spectral_comb"       # Spectral ↔ combinatorial bridge
    DIFFUSION_SAMPLE = "diffusion_sample" # Diffusion → sample
    MULTIGRID = "multigrid"               # Coarse-fine recursion
    HIERARCHICAL_MCMC = "hierarchical_mcmc" # Multi-level MCMC


# ═══════════════════════════════════════════════════════════════════════════════
# BASE OPERATORS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class DiscreteOperator:
    """
    D-Operator (Earth): Discrete/Combinatorial.
    
    Examples:
    - Graph Laplacian: (Lf)(i) = Σ_j w_{ij}(f(i) - f(j))
    - Transition matrix of Markov chain
    - Constraint projector
    - Finite difference stencil
    """
    matrix: NDArray
    name: str = "D"
    
    @property
    def dim(self) -> int:
        return self.matrix.shape[0]
    
    def apply(self, x: NDArray) -> NDArray:
        """Apply operator: Dx."""
        return self.matrix @ x
    
    @property
    def spectrum(self) -> NDArray:
        """Eigenvalues of D."""
        return np.linalg.eigvalsh(self.matrix)
    
    @classmethod
    def graph_laplacian(cls, adjacency: NDArray) -> 'DiscreteOperator':
        """Create graph Laplacian from adjacency matrix."""
        degree = np.diag(np.sum(adjacency, axis=1))
        L = degree - adjacency
        return cls(L, "graph_laplacian")
    
    @classmethod
    def transition_matrix(cls, P: NDArray) -> 'DiscreteOperator':
        """Create from Markov transition matrix."""
        return cls(P, "transition")


@dataclass
class ContinuousOperator:
    """
    Ω-Operator (Water): Continuous/Geometric.
    
    Examples:
    - Laplacian Δ on manifold
    - Gradient flow ∇f
    - Hamiltonian vector field
    - Heat/Wave/Schrödinger operator
    """
    apply_fn: Callable[[NDArray], NDArray]
    name: str = "Omega"
    generator_type: str = "elliptic"  # elliptic, parabolic, hyperbolic
    
    def apply(self, x: NDArray) -> NDArray:
        """Apply operator: Ωx."""
        return self.apply_fn(x)
    
    @classmethod
    def laplacian_1d(cls, n: int, h: float = 1.0) -> 'ContinuousOperator':
        """1D Laplacian via finite differences."""
        def apply_laplacian(x):
            result = np.zeros_like(x)
            for i in range(1, len(x) - 1):
                result[i] = (x[i-1] - 2*x[i] + x[i+1]) / (h * h)
            return result
        return cls(apply_laplacian, "laplacian_1d", "elliptic")
    
    @classmethod
    def gradient(cls, f: Callable[[NDArray], float], h: float = 1e-6) -> 'ContinuousOperator':
        """Gradient operator for scalar function."""
        def apply_grad(x):
            grad = np.zeros_like(x)
            for i in range(len(x)):
                x_plus = x.copy()
                x_plus[i] += h
                x_minus = x.copy()
                x_minus[i] -= h
                grad[i] = (f(x_plus) - f(x_minus)) / (2 * h)
            return grad
        return cls(apply_grad, "gradient", "parabolic")


@dataclass
class StochasticOperator:
    """
    Σ-Operator (Fire): Stochastic/Expansion.
    
    Examples:
    - Noise injection √(2D) dW
    - MCMC proposal kernel
    - Random perturbation
    - Fokker-Planck generator
    """
    noise_scale: float = 1.0
    name: str = "Sigma"
    
    def apply(self, x: NDArray, rng: np.random.Generator = None) -> NDArray:
        """Apply stochastic operator: Σx + noise."""
        if rng is None:
            rng = np.random.default_rng()
        noise = self.noise_scale * rng.standard_normal(x.shape)
        return x + noise
    
    def sample_proposal(self, x: NDArray, rng: np.random.Generator = None) -> NDArray:
        """Sample from proposal distribution centered at x."""
        return self.apply(x, rng)
    
    @classmethod
    def gaussian_noise(cls, scale: float = 1.0) -> 'StochasticOperator':
        """Gaussian noise operator."""
        return cls(scale, "gaussian_noise")
    
    @classmethod
    def metropolis_proposal(cls, step_size: float) -> 'StochasticOperator':
        """Metropolis random walk proposal."""
        return cls(step_size, "metropolis")


@dataclass
class RecursiveOperator:
    """
    Ψ-Operator (Air): Recursive/Hierarchical.
    
    Examples:
    - Multigrid V-cycle
    - Renormalization group flow
    - Wavelet transform
    - Hierarchical decomposition
    """
    coarsen: Callable[[NDArray], NDArray]
    refine: Callable[[NDArray], NDArray]
    name: str = "Psi"
    
    def restrict(self, x: NDArray) -> NDArray:
        """Coarsen: fine → coarse."""
        return self.coarsen(x)
    
    def prolongate(self, x: NDArray) -> NDArray:
        """Refine: coarse → fine."""
        return self.refine(x)
    
    def v_cycle(self, x: NDArray, levels: int = 2) -> NDArray:
        """Apply V-cycle at multiple levels."""
        if levels <= 0:
            return x
        
        # Restrict to coarse
        x_coarse = self.restrict(x)
        
        # Recurse
        x_coarse = self.v_cycle(x_coarse, levels - 1)
        
        # Prolongate back
        return self.prolongate(x_coarse)
    
    @classmethod
    def simple_restriction(cls) -> 'RecursiveOperator':
        """Simple averaging restriction and linear interpolation."""
        def coarsen(x):
            n = len(x)
            return (x[::2] + x[1::2]) / 2 if n > 1 else x
        
        def refine(x):
            result = np.zeros(2 * len(x))
            result[::2] = x
            result[1::2] = x
            return result
        
        return cls(coarsen, refine, "simple_mg")


# ═══════════════════════════════════════════════════════════════════════════════
# HYBRID GENERATORS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class HybridGenerator:
    """
    Hybrid generator combining multiple operator poles.
    
    G = α_D·D + α_Ω·Ω + α_Σ·Σ + α_Ψ·Ψ
    
    Lives in the operator simplex where weights sum to 1.
    """
    D: Optional[DiscreteOperator] = None
    Omega: Optional[ContinuousOperator] = None
    Sigma: Optional[StochasticOperator] = None
    Psi: Optional[RecursiveOperator] = None
    
    weights: Dict[OperatorPole, float] = field(default_factory=lambda: {
        OperatorPole.D: 0.25,
        OperatorPole.OMEGA: 0.25,
        OperatorPole.SIGMA: 0.25,
        OperatorPole.PSI: 0.25
    })
    
    @property
    def active_poles(self) -> List[OperatorPole]:
        """List of active poles (weight > 0)."""
        return [p for p, w in self.weights.items() if w > 0]
    
    @property
    def is_discrete_continuous(self) -> bool:
        """Check if D+Ω hybrid."""
        return (self.weights[OperatorPole.D] > 0 and 
                self.weights[OperatorPole.OMEGA] > 0)
    
    @property
    def is_expansion_recursion(self) -> bool:
        """Check if Σ+Ψ hybrid."""
        return (self.weights[OperatorPole.SIGMA] > 0 and 
                self.weights[OperatorPole.PSI] > 0)
    
    def apply(self, x: NDArray, rng: np.random.Generator = None) -> NDArray:
        """Apply hybrid generator."""
        result = np.zeros_like(x, dtype=float)
        
        if self.D is not None and self.weights[OperatorPole.D] > 0:
            result += self.weights[OperatorPole.D] * self.D.apply(x)
        
        if self.Omega is not None and self.weights[OperatorPole.OMEGA] > 0:
            result += self.weights[OperatorPole.OMEGA] * self.Omega.apply(x)
        
        if self.Sigma is not None and self.weights[OperatorPole.SIGMA] > 0:
            result = self.Sigma.apply(result, rng)
        
        if self.Psi is not None and self.weights[OperatorPole.PSI] > 0:
            result = self.Psi.v_cycle(result, levels=1)
        
        return result
    
    @classmethod
    def discrete_continuous(cls, D: DiscreteOperator, 
                            Omega: ContinuousOperator,
                            alpha: float = 0.5) -> 'HybridGenerator':
        """Create D+Ω hybrid."""
        return cls(
            D=D, Omega=Omega,
            weights={
                OperatorPole.D: alpha,
                OperatorPole.OMEGA: 1 - alpha,
                OperatorPole.SIGMA: 0,
                OperatorPole.PSI: 0
            }
        )
    
    @classmethod
    def expansion_recursion(cls, Sigma: StochasticOperator,
                            Psi: RecursiveOperator,
                            beta: float = 0.5) -> 'HybridGenerator':
        """Create Σ+Ψ vertical hybrid."""
        return cls(
            Sigma=Sigma, Psi=Psi,
            weights={
                OperatorPole.D: 0,
                OperatorPole.OMEGA: 0,
                OperatorPole.SIGMA: beta,
                OperatorPole.PSI: 1 - beta
            }
        )


# ═══════════════════════════════════════════════════════════════════════════════
# HYBRID SHORTCUT PATTERNS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class RelaxProjectPattern:
    """
    Relax-Project pattern: continuous relaxation → discrete projection.
    
    1. Solve continuous relaxation (e.g., LP relaxation)
    2. Project to discrete feasible set (e.g., rounding)
    """
    relaxation: ContinuousOperator
    projection: DiscreteOperator
    
    def solve(self, x0: NDArray, n_relax: int = 10, dt: float = 0.1) -> NDArray:
        """Run relax-project cycle."""
        x = x0.copy()
        
        # Relaxation phase
        for _ in range(n_relax):
            dx = self.relaxation.apply(x)
            x = x + dt * dx
        
        # Projection phase
        x = self.projection.apply(x)
        
        return x


@dataclass
class FlowPrunePattern:
    """
    Flow-Prune pattern: continuous flow → discrete pruning.
    
    1. Run gradient/diffusion flow
    2. Prune based on discrete criterion
    """
    flow: ContinuousOperator
    prune_threshold: float = 0.1
    
    def solve(self, x0: NDArray, n_flow: int = 10, dt: float = 0.1) -> NDArray:
        """Run flow-prune cycle."""
        x = x0.copy()
        
        # Flow phase
        for _ in range(n_flow):
            dx = self.flow.apply(x)
            x = x + dt * dx
        
        # Prune phase
        x[np.abs(x) < self.prune_threshold] = 0
        
        return x


@dataclass
class PredictCorrectPattern:
    """
    Predict-Correct pattern: predictor step → corrector step.
    
    Used in numerical integration (e.g., Adams-Bashforth/Moulton).
    """
    predictor: Callable[[NDArray], NDArray]
    corrector: Callable[[NDArray, NDArray], NDArray]
    
    def step(self, x: NDArray) -> NDArray:
        """Single predict-correct step."""
        x_pred = self.predictor(x)
        x_corr = self.corrector(x, x_pred)
        return x_corr


@dataclass
class SpectralCombinatorialBridge:
    """
    Spectral-Combinatorial bridge pattern.
    
    Uses spectral methods to inform combinatorial decisions.
    """
    graph_laplacian: DiscreteOperator
    
    def spectral_partition(self, k: int = 2) -> NDArray:
        """Partition using spectral clustering."""
        L = self.graph_laplacian.matrix
        eigenvalues, eigenvectors = np.linalg.eigh(L)
        
        # Use Fiedler vector for bipartition
        fiedler = eigenvectors[:, 1]
        
        if k == 2:
            return (fiedler >= 0).astype(int)
        else:
            # k-means on first k eigenvectors
            from scipy.cluster.vq import kmeans2
            V = eigenvectors[:, 1:k+1]
            _, labels = kmeans2(V, k, minit='++')
            return labels


# ═══════════════════════════════════════════════════════════════════════════════
# OPERATOR SIMPLEX
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class OperatorSimplex:
    """
    The 4-dimensional operator simplex.
    
    Points in the simplex represent weighted combinations of D, Ω, Σ, Ψ.
    
    Vertices: pure poles
    Edges: 2-operator hybrids (6 edges)
    Faces: 3-operator hybrids (4 faces)
    Interior: full 4-operator hybrid
    """
    
    @staticmethod
    def vertex(pole: OperatorPole) -> Dict[OperatorPole, float]:
        """Pure pole (vertex of simplex)."""
        weights = {p: 0.0 for p in OperatorPole}
        weights[pole] = 1.0
        return weights
    
    @staticmethod
    def edge(pole1: OperatorPole, pole2: OperatorPole, 
             t: float = 0.5) -> Dict[OperatorPole, float]:
        """2-operator hybrid (edge of simplex)."""
        weights = {p: 0.0 for p in OperatorPole}
        weights[pole1] = t
        weights[pole2] = 1 - t
        return weights
    
    @staticmethod
    def face(poles: List[OperatorPole], 
             coords: List[float] = None) -> Dict[OperatorPole, float]:
        """3-operator hybrid (face of simplex)."""
        if coords is None:
            coords = [1/3] * 3
        assert len(poles) == 3 and len(coords) == 3
        
        weights = {p: 0.0 for p in OperatorPole}
        for pole, c in zip(poles, coords):
            weights[pole] = c
        return weights
    
    @staticmethod
    def interior(coords: List[float] = None) -> Dict[OperatorPole, float]:
        """Full 4-operator hybrid (interior of simplex)."""
        if coords is None:
            coords = [0.25] * 4
        assert len(coords) == 4
        
        poles = list(OperatorPole)
        return {pole: c for pole, c in zip(poles, coords)}
    
    @staticmethod
    def barycentric_to_weights(bary: Tuple[float, float, float, float]) -> Dict[OperatorPole, float]:
        """Convert barycentric coordinates to pole weights."""
        poles = list(OperatorPole)
        return {pole: b for pole, b in zip(poles, bary)}


# ═══════════════════════════════════════════════════════════════════════════════
# HYBRID EVOLUTION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class HybridEvolution:
    """
    Time evolution under hybrid generator.
    
    ∂_t u = G·u  or  u_{n+1} = Φ(u_n)
    """
    generator: HybridGenerator
    
    def evolve(self, u0: NDArray, t_final: float, 
               dt: float = 0.01) -> List[NDArray]:
        """Forward Euler evolution."""
        trajectory = [u0.copy()]
        u = u0.copy()
        t = 0.0
        
        while t < t_final:
            du = self.generator.apply(u)
            u = u + dt * du
            trajectory.append(u.copy())
            t += dt
        
        return trajectory
    
    def iterate(self, u0: NDArray, n_steps: int) -> List[NDArray]:
        """Discrete iteration."""
        trajectory = [u0.copy()]
        u = u0.copy()
        
        for _ in range(n_steps):
            u = self.generator.apply(u)
            trajectory.append(u.copy())
        
        return trajectory


# ═══════════════════════════════════════════════════════════════════════════════
# POLE BRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class HybridEquationPoleBridge:
    """
    Bridge between Hybrid Equations and four-pole framework.
    """
    
    @staticmethod
    def pole_map() -> str:
        return """
        HYBRID OPERATORS ↔ FOUR POLES
        
        D (Discrete):
          - Earth pole
          - □ Square chart
          - Graph Laplacians, constraints, combinatorial
          
        Ω (Continuous):
          - Water/C pole  
          - ✿ Flower chart
          - Differential, geometric flow, PDEs
          
        Σ (Stochastic):
          - Fire/Σ pole
          - ☁ Cloud chart
          - Random expansion, noise, MCMC
          
        Ψ (Recursive):
          - Air/Ψ pole
          - ⟂ Fractal chart
          - Renormalization, multigrid, hierarchical
        """
    
    @staticmethod
    def integration() -> str:
        return """
        HYBRID EQUATION GENERATOR ↔ FRAMEWORK
        
        Hybrid Generator: G = α_D·D + α_Ω·Ω + α_Σ·Σ + α_Ψ·Ψ
        
        Two Axes:
          Horizontal: D ↔ Ω (discrete-continuous)
          Vertical: Σ ↔ Ψ (expansion-recursion)
        
        Operator Simplex:
          Vertices: pure poles (4)
          Edges: 2-hybrids (6)
          Faces: 3-hybrids (4)
          Interior: full quad-polar
        
        Shortcut Patterns:
          relax-project, flow-prune, predict-correct,
          spectral-combinatorial, diffusion-sample, multigrid
        """


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def discrete_operator(matrix: NDArray) -> DiscreteOperator:
    """Create discrete operator."""
    return DiscreteOperator(matrix)


def graph_laplacian(adjacency: NDArray) -> DiscreteOperator:
    """Create graph Laplacian."""
    return DiscreteOperator.graph_laplacian(adjacency)


def stochastic_operator(noise_scale: float = 1.0) -> StochasticOperator:
    """Create stochastic operator."""
    return StochasticOperator(noise_scale)


def recursive_operator() -> RecursiveOperator:
    """Create recursive operator."""
    return RecursiveOperator.simple_restriction()


def hybrid_generator(D: DiscreteOperator = None,
                     Omega: ContinuousOperator = None,
                     Sigma: StochasticOperator = None,
                     Psi: RecursiveOperator = None) -> HybridGenerator:
    """Create hybrid generator."""
    return HybridGenerator(D, Omega, Sigma, Psi)


def operator_simplex() -> OperatorSimplex:
    """Create operator simplex."""
    return OperatorSimplex()


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Enums
    'OperatorPole',
    'HybridPattern',
    
    # Base Operators
    'DiscreteOperator',
    'ContinuousOperator',
    'StochasticOperator',
    'RecursiveOperator',
    
    # Hybrid
    'HybridGenerator',
    'HybridEvolution',
    
    # Patterns
    'RelaxProjectPattern',
    'FlowPrunePattern',
    'PredictCorrectPattern',
    'SpectralCombinatorialBridge',
    
    # Simplex
    'OperatorSimplex',
    
    # Bridge
    'HybridEquationPoleBridge',
    
    # Functions
    'discrete_operator',
    'graph_laplacian',
    'stochastic_operator',
    'recursive_operator',
    'hybrid_generator',
    'operator_simplex',
]
