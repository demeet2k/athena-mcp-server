"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        UNIFIED INTEGRATION MODULE                            ║
║                                                                              ║
║  Cross-Module Connectors and Quad-Polar Synthesis                            ║
║                                                                              ║
║  The Absolute Final Form:                                                    ║
║    This module synthesizes all components of AtlasForge into a unified       ║
║    whole. It provides the connective tissue between:                         ║
║                                                                              ║
║      D (Earth)  ← → Ω (Water)                                               ║
║          ↑   ⨯   ↓                                                          ║
║      Σ (Fire)  ← → Ψ (Air)                                                  ║
║                                                                              ║
║  Cross-Connections:                                                          ║
║    D ↔ Ω : Discrete structure ↔ Spectral representation                     ║
║    D ↔ Σ : Combinatorics ↔ Probability                                      ║
║    D ↔ Ψ : Local rules ↔ Recursive structure                                ║
║    Ω ↔ Σ : Coherence ↔ Entropy                                              ║
║    Ω ↔ Ψ : Harmonics ↔ Wavelets                                             ║
║    Σ ↔ Ψ : Diffusion ↔ Renormalization                                      ║
║                                                                              ║
║  The Shortcut Engine:                                                        ║
║    Shortcuts emerge from hybrid paths that traverse multiple poles           ║
║    more efficiently than any single-pole evolution.                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Callable, Any, Union
from enum import Enum, auto
import numpy as np
from numpy.typing import NDArray


# ═══════════════════════════════════════════════════════════════════════════════
# POLE TYPES AND WEIGHTS
# ═══════════════════════════════════════════════════════════════════════════════

class Pole(Enum):
    """The four fundamental poles."""
    D = "discrete"      # Earth - Discrete, Dissipative
    OMEGA = "oscillatory"  # Water - Oscillatory, Wave-like
    SIGMA = "stochastic"   # Fire - Stochastic, Probabilistic
    PSI = "recursive"      # Air - Recursive, Hierarchical


@dataclass
class PoleWeights:
    """
    Weights on the operator simplex Δ³.
    
    Represents a point (α_D, α_Ω, α_Σ, α_Ψ) where Σα = 1, α ≥ 0.
    """
    d: float = 0.25
    omega: float = 0.25
    sigma: float = 0.25
    psi: float = 0.25
    
    def __post_init__(self):
        self._normalize()
    
    def _normalize(self):
        """Normalize to sum to 1."""
        total = self.d + self.omega + self.sigma + self.psi
        if total > 0:
            self.d /= total
            self.omega /= total
            self.sigma /= total
            self.psi /= total
    
    @property
    def as_array(self) -> NDArray[np.float64]:
        return np.array([self.d, self.omega, self.sigma, self.psi])
    
    @classmethod
    def from_array(cls, arr: NDArray) -> 'PoleWeights':
        return cls(d=arr[0], omega=arr[1], sigma=arr[2], psi=arr[3])
    
    @classmethod
    def pure(cls, pole: Pole) -> 'PoleWeights':
        """Pure pole (vertex of simplex)."""
        if pole == Pole.D:
            return cls(d=1, omega=0, sigma=0, psi=0)
        elif pole == Pole.OMEGA:
            return cls(d=0, omega=1, sigma=0, psi=0)
        elif pole == Pole.SIGMA:
            return cls(d=0, omega=0, sigma=1, psi=0)
        elif pole == Pole.PSI:
            return cls(d=0, omega=0, sigma=0, psi=1)
    
    @classmethod
    def uniform(cls) -> 'PoleWeights':
        """Center of simplex."""
        return cls(d=0.25, omega=0.25, sigma=0.25, psi=0.25)
    
    def dominant_pole(self) -> Pole:
        """Return the pole with highest weight."""
        weights = [(self.d, Pole.D), (self.omega, Pole.OMEGA),
                   (self.sigma, Pole.SIGMA), (self.psi, Pole.PSI)]
        return max(weights, key=lambda x: x[0])[1]
    
    def entropy(self) -> float:
        """Shannon entropy of weights (max at uniform)."""
        arr = self.as_array
        mask = arr > 0
        return -np.sum(arr[mask] * np.log(arr[mask]))
    
    def lerp(self, other: 'PoleWeights', t: float) -> 'PoleWeights':
        """Linear interpolation between weight configurations."""
        return PoleWeights.from_array((1 - t) * self.as_array + t * other.as_array)


# ═══════════════════════════════════════════════════════════════════════════════
# UNIFIED STATE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class UnifiedState:
    """
    State that exists across all four representations.
    
    Provides simultaneous access to:
        - SQUARE: Discrete/combinatorial view
        - FLOWER: Wave/modal view
        - CLOUD: Probabilistic view
        - FRACTAL: Hierarchical view
    """
    dimension: int
    kappa: float = 1.0  # Kernel parameter
    
    # Raw state vector
    _vector: NDArray[np.float64] = field(default=None, repr=False)
    
    # Cached representations
    _square: NDArray = field(default=None, repr=False)
    _flower: NDArray = field(default=None, repr=False)
    _cloud: NDArray = field(default=None, repr=False)
    _fractal: List[NDArray] = field(default=None, repr=False)
    
    def __post_init__(self):
        if self._vector is None:
            self._vector = np.zeros(self.dimension)
    
    @classmethod
    def from_vector(cls, v: NDArray, kappa: float = 1.0) -> 'UnifiedState':
        """Create state from raw vector."""
        state = cls(dimension=len(v), kappa=kappa)
        state._vector = np.asarray(v, dtype=np.float64)
        return state
    
    @classmethod
    def random(cls, dimension: int, kappa: float = 1.0, 
              rng: np.random.Generator = None) -> 'UnifiedState':
        """Create random state."""
        if rng is None:
            rng = np.random.default_rng()
        v = rng.standard_normal(dimension)
        return cls.from_vector(v, kappa)
    
    @property
    def vector(self) -> NDArray[np.float64]:
        return self._vector.copy()
    
    @property
    def square(self) -> NDArray:
        """SQUARE representation: discrete structure."""
        if self._square is None:
            # Reshape to 2D grid if possible
            n = int(np.sqrt(self.dimension))
            if n * n == self.dimension:
                self._square = self._vector.reshape(n, n)
            else:
                self._square = self._vector
        return self._square
    
    @property
    def flower(self) -> NDArray:
        """FLOWER representation: spectral/modal view."""
        if self._flower is None:
            # FFT gives modal decomposition
            self._flower = np.fft.fft(self._vector)
        return self._flower
    
    @property
    def cloud(self) -> NDArray:
        """CLOUD representation: probability distribution."""
        if self._cloud is None:
            # Square and normalize
            probs = np.abs(self._vector) ** 2
            total = np.sum(probs)
            self._cloud = probs / total if total > 0 else probs
        return self._cloud
    
    @property
    def fractal(self) -> List[NDArray]:
        """FRACTAL representation: multi-scale decomposition."""
        if self._fractal is None:
            # Simple dyadic decomposition
            self._fractal = []
            current = self._vector.copy()
            while len(current) >= 2:
                n = len(current)
                approx = (current[::2] + current[1::2]) / np.sqrt(2)
                detail = (current[::2] - current[1::2]) / np.sqrt(2)
                self._fractal.append(detail)
                current = approx
            self._fractal.append(current)
        return self._fractal
    
    def invalidate_cache(self):
        """Clear cached representations."""
        self._square = None
        self._flower = None
        self._cloud = None
        self._fractal = None
    
    @property
    def bandwidth(self) -> float:
        """Kernel bandwidth τ_κ = π/(2√κ)."""
        return np.pi / (2 * np.sqrt(self.kappa))
    
    def norm(self) -> float:
        """Euclidean norm."""
        return np.linalg.norm(self._vector)
    
    def entropy(self) -> float:
        """Shannon entropy of cloud representation."""
        p = self.cloud
        mask = p > 0
        return -np.sum(p[mask] * np.log(p[mask]))


# ═══════════════════════════════════════════════════════════════════════════════
# CROSS-POLE CONNECTORS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class CrossPoleConnector:
    """
    Connectors between pairs of poles.
    
    Each connection provides bidirectional transformation
    between two polar representations.
    """
    
    def d_to_omega(self, discrete_state: NDArray) -> NDArray[np.complex128]:
        """
        D → Ω: Discrete to Oscillatory via DFT.
        
        This is the spectral bridge: combinatorial structure
        becomes frequency content.
        """
        return np.fft.fft(discrete_state)
    
    def omega_to_d(self, spectral_state: NDArray) -> NDArray[np.float64]:
        """
        Ω → D: Oscillatory to Discrete via inverse DFT.
        """
        return np.real(np.fft.ifft(spectral_state))
    
    def d_to_sigma(self, discrete_state: NDArray) -> NDArray[np.float64]:
        """
        D → Σ: Discrete to Stochastic via normalization.
        
        Converts counts/weights to probability distribution.
        """
        state = np.abs(discrete_state)
        total = np.sum(state)
        return state / total if total > 0 else state
    
    def sigma_to_d(self, prob_state: NDArray, scale: float = 1.0) -> NDArray[np.float64]:
        """
        Σ → D: Stochastic to Discrete via sampling.
        
        Converts probabilities back to weighted structure.
        """
        return prob_state * scale
    
    def d_to_psi(self, discrete_state: NDArray, levels: int = None) -> List[NDArray]:
        """
        D → Ψ: Discrete to Recursive via wavelet decomposition.
        """
        if levels is None:
            levels = max(1, int(np.log2(len(discrete_state))))
        
        result = []
        current = discrete_state.copy()
        
        for _ in range(levels):
            if len(current) < 2:
                break
            n = len(current)
            approx = (current[::2] + current[1::2]) / np.sqrt(2)
            detail = (current[::2] - current[1::2]) / np.sqrt(2)
            result.append(detail)
            current = approx
        
        result.append(current)
        return result
    
    def psi_to_d(self, hierarchical_state: List[NDArray]) -> NDArray[np.float64]:
        """
        Ψ → D: Recursive to Discrete via wavelet reconstruction.
        """
        current = hierarchical_state[-1]
        
        for detail in reversed(hierarchical_state[:-1]):
            n = len(detail)
            reconstructed = np.zeros(2 * n)
            reconstructed[::2] = (current + detail) / np.sqrt(2)
            reconstructed[1::2] = (current - detail) / np.sqrt(2)
            current = reconstructed
        
        return current
    
    def omega_to_sigma(self, spectral_state: NDArray) -> NDArray[np.float64]:
        """
        Ω → Σ: Oscillatory to Stochastic via power spectrum.
        
        Converts phase information to energy distribution.
        """
        power = np.abs(spectral_state) ** 2
        total = np.sum(power)
        return power / total if total > 0 else power
    
    def sigma_to_omega(self, prob_state: NDArray, 
                      phase: NDArray = None) -> NDArray[np.complex128]:
        """
        Σ → Ω: Stochastic to Oscillatory by adding phase.
        
        Reconstructs complex amplitudes from magnitude distribution.
        """
        magnitude = np.sqrt(prob_state * len(prob_state))
        
        if phase is None:
            phase = np.zeros_like(prob_state)
        
        return magnitude * np.exp(1j * phase)
    
    def omega_to_psi(self, spectral_state: NDArray, 
                    levels: int = 4) -> Dict[int, NDArray]:
        """
        Ω → Ψ: Oscillatory to Recursive via frequency bands.
        
        Groups frequencies into octave bands (wavelet-like).
        """
        n = len(spectral_state)
        bands = {}
        
        for level in range(levels):
            low = n // (2 ** (level + 1))
            high = n // (2 ** level)
            
            if low == high:
                continue
            
            band = np.zeros_like(spectral_state)
            band[low:high] = spectral_state[low:high]
            band[n-high:n-low] = spectral_state[n-high:n-low]
            
            bands[level] = band
        
        return bands
    
    def sigma_to_psi(self, prob_state: NDArray, 
                    levels: int = None) -> List[NDArray[np.float64]]:
        """
        Σ → Ψ: Stochastic to Recursive via entropy at scales.
        
        Decomposes distribution into scale-local entropies.
        """
        if levels is None:
            levels = max(1, int(np.log2(len(prob_state))))
        
        result = []
        current = prob_state.copy()
        
        for _ in range(levels):
            if len(current) < 2:
                break
            
            # Coarse-grain
            coarse = (current[::2] + current[1::2])
            coarse = coarse / np.sum(coarse) if np.sum(coarse) > 0 else coarse
            
            # Conditional entropy of fine given coarse
            detail = np.zeros(len(coarse))
            for i in range(len(coarse)):
                if coarse[i] > 0:
                    p1 = current[2*i] / (current[2*i] + current[2*i+1] + 1e-15)
                    if 0 < p1 < 1:
                        detail[i] = -(p1 * np.log(p1) + (1-p1) * np.log(1-p1))
            
            result.append(detail)
            current = coarse
        
        result.append(current)
        return result


# ═══════════════════════════════════════════════════════════════════════════════
# HYBRID PATH
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class HybridPathStep:
    """Single step in a hybrid path."""
    from_pole: Pole
    to_pole: Pole
    transformation: str  # Description
    cost: float = 1.0


@dataclass
class HybridPath:
    """
    A path through the pole space.
    
    Hybrid algorithms correspond to paths that traverse
    multiple poles, potentially achieving "shortcuts".
    """
    steps: List[HybridPathStep] = field(default_factory=list)
    
    @property
    def total_cost(self) -> float:
        return sum(step.cost for step in self.steps)
    
    @property
    def pole_sequence(self) -> List[Pole]:
        """Sequence of poles visited."""
        if not self.steps:
            return []
        sequence = [self.steps[0].from_pole]
        for step in self.steps:
            sequence.append(step.to_pole)
        return sequence
    
    def add_step(self, from_pole: Pole, to_pole: Pole, 
                transformation: str, cost: float = 1.0):
        """Add a step to the path."""
        self.steps.append(HybridPathStep(from_pole, to_pole, transformation, cost))
    
    def is_shortcut(self, single_pole_cost: float) -> bool:
        """Check if this path is a shortcut vs single-pole evolution."""
        return self.total_cost < single_pole_cost


# ═══════════════════════════════════════════════════════════════════════════════
# SHORTCUT DETECTOR
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ShortcutDetector:
    """
    Detect and analyze shortcuts in hybrid algorithms.
    
    A shortcut exists when a hybrid path achieves a target
    in fewer steps than any pure single-pole evolution.
    """
    connector: CrossPoleConnector = field(default_factory=CrossPoleConnector)
    
    def estimate_single_pole_cost(self, initial: UnifiedState, 
                                  target: UnifiedState, 
                                  pole: Pole) -> float:
        """Estimate cost of reaching target using only one pole."""
        if pole == Pole.D:
            # Discrete: count operations needed
            diff = np.abs(initial.vector - target.vector)
            return np.sum(diff > 0.1)  # Number of positions to change
        
        elif pole == Pole.OMEGA:
            # Oscillatory: spectral distance
            spec_diff = np.abs(initial.flower - target.flower)
            return np.sum(spec_diff) / len(initial.flower)
        
        elif pole == Pole.SIGMA:
            # Stochastic: KL divergence
            p = initial.cloud + 1e-10
            q = target.cloud + 1e-10
            return np.sum(p * np.log(p / q))
        
        elif pole == Pole.PSI:
            # Recursive: multi-scale difference
            h1 = initial.fractal
            h2 = target.fractal
            cost = 0
            for c1, c2 in zip(h1, h2):
                cost += np.sum(np.abs(c1 - c2))
            return cost
        
        return float('inf')
    
    def find_shortcut_path(self, initial: UnifiedState, 
                          target: UnifiedState,
                          max_steps: int = 5) -> Optional[HybridPath]:
        """
        Find a hybrid path that beats all single-pole paths.
        """
        # Compute single-pole costs
        single_costs = {
            pole: self.estimate_single_pole_cost(initial, target, pole)
            for pole in Pole
        }
        best_single = min(single_costs.values())
        
        # Try simple 2-step hybrid paths
        for p1 in Pole:
            for p2 in Pole:
                if p1 == p2:
                    continue
                
                # Estimate hybrid cost
                hybrid_cost = self._estimate_hybrid_cost(initial, target, [p1, p2])
                
                if hybrid_cost < best_single:
                    path = HybridPath()
                    path.add_step(p1, p2, f"{p1.value}→{p2.value}", hybrid_cost)
                    return path
        
        return None
    
    def _estimate_hybrid_cost(self, initial: UnifiedState, 
                             target: UnifiedState,
                             pole_sequence: List[Pole]) -> float:
        """Estimate cost of a multi-pole path."""
        # Simplified: sum of transition costs
        cost = 0
        for i in range(len(pole_sequence) - 1):
            # Cross-pole transition cost
            cost += 1.0  # Base cost for any transition
        
        # Add final distance
        if pole_sequence:
            cost += self.estimate_single_pole_cost(initial, target, pole_sequence[-1]) / 2
        
        return cost


# ═══════════════════════════════════════════════════════════════════════════════
# UNIFIED SOLVER
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class UnifiedSolver:
    """
    The complete unified solver using all four poles.
    
    Automatically selects the best pole or hybrid combination
    based on problem characteristics.
    """
    connector: CrossPoleConnector = field(default_factory=CrossPoleConnector)
    shortcut_detector: ShortcutDetector = field(default_factory=ShortcutDetector)
    
    def diagnose(self, state: UnifiedState) -> Dict[str, Any]:
        """Analyze state to determine optimal approach."""
        return {
            'dimension': state.dimension,
            'kappa': state.kappa,
            'bandwidth': state.bandwidth,
            'entropy': state.entropy(),
            'norm': state.norm(),
            'spectral_energy': np.sum(np.abs(state.flower) ** 2),
            'dominant_frequencies': np.argsort(np.abs(state.flower))[-5:][::-1].tolist(),
            'scale_distribution': [np.sum(c**2) for c in state.fractal]
        }
    
    def suggest_pole(self, state: UnifiedState, 
                    task: str = 'general') -> PoleWeights:
        """Suggest pole weights for given state and task."""
        diagnosis = self.diagnose(state)
        
        if task == 'smooth':
            # Prefer spectral for smooth functions
            return PoleWeights(d=0.1, omega=0.6, sigma=0.1, psi=0.2)
        
        elif task == 'sparse':
            # Prefer discrete for sparse data
            return PoleWeights(d=0.6, omega=0.1, sigma=0.1, psi=0.2)
        
        elif task == 'noisy':
            # Prefer stochastic for noisy data
            return PoleWeights(d=0.1, omega=0.2, sigma=0.5, psi=0.2)
        
        elif task == 'hierarchical':
            # Prefer recursive for multi-scale data
            return PoleWeights(d=0.1, omega=0.2, sigma=0.1, psi=0.6)
        
        else:
            # Default: balanced
            return PoleWeights.uniform()
    
    def apply_operator(self, state: UnifiedState, 
                      weights: PoleWeights,
                      operator_type: str = 'evolution') -> UnifiedState:
        """
        Apply hybrid operator with given pole weights.
        """
        result = np.zeros_like(state.vector)
        
        # D contribution: local averaging
        if weights.d > 0:
            d_result = np.convolve(state.vector, [0.25, 0.5, 0.25], mode='same')
            result += weights.d * d_result
        
        # Ω contribution: frequency damping
        if weights.omega > 0:
            spec = self.connector.d_to_omega(state.vector)
            # Damp high frequencies
            freqs = np.fft.fftfreq(len(spec))
            damping = np.exp(-np.abs(freqs) * state.kappa)
            spec *= damping
            omega_result = self.connector.omega_to_d(spec)
            result += weights.omega * omega_result
        
        # Σ contribution: entropy regularization
        if weights.sigma > 0:
            probs = self.connector.d_to_sigma(state.vector)
            # Move toward maximum entropy
            uniform = np.ones_like(probs) / len(probs)
            sigma_result = probs + 0.1 * (uniform - probs)
            result += weights.sigma * sigma_result * state.norm()
        
        # Ψ contribution: multi-scale smoothing
        if weights.psi > 0:
            decomp = self.connector.d_to_psi(state.vector)
            # Smooth at each scale
            for i, detail in enumerate(decomp[:-1]):
                decomp[i] = detail * np.exp(-i * 0.1)  # Scale-dependent damping
            psi_result = self.connector.psi_to_d(decomp)
            result += weights.psi * psi_result
        
        return UnifiedState.from_vector(result, state.kappa)
    
    def solve(self, initial: UnifiedState, 
             objective: Callable[[UnifiedState], float],
             max_iterations: int = 100,
             tolerance: float = 1e-6) -> Dict[str, Any]:
        """
        Solve optimization problem using adaptive pole selection.
        """
        current = initial
        history = []
        
        for iteration in range(max_iterations):
            current_value = objective(current)
            history.append(current_value)
            
            if iteration > 0 and abs(history[-1] - history[-2]) < tolerance:
                break
            
            # Adapt pole weights based on progress
            if iteration < max_iterations // 4:
                weights = PoleWeights(d=0.4, omega=0.3, sigma=0.2, psi=0.1)
            elif iteration < max_iterations // 2:
                weights = PoleWeights(d=0.2, omega=0.4, sigma=0.2, psi=0.2)
            else:
                weights = PoleWeights(d=0.1, omega=0.3, sigma=0.3, psi=0.3)
            
            current = self.apply_operator(current, weights)
        
        return {
            'solution': current,
            'objective_value': objective(current),
            'iterations': iteration + 1,
            'history': history,
            'converged': iteration + 1 < max_iterations
        }


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def create_unified_state(dimension: int, kappa: float = 1.0) -> UnifiedState:
    """Create new unified state."""
    return UnifiedState(dimension=dimension, kappa=kappa)


def pole_weights(d: float = 0.25, omega: float = 0.25, 
                sigma: float = 0.25, psi: float = 0.25) -> PoleWeights:
    """Create pole weights."""
    return PoleWeights(d=d, omega=omega, sigma=sigma, psi=psi)


def diagnose_state(state: UnifiedState) -> Dict[str, Any]:
    """Diagnose unified state."""
    return UnifiedSolver().diagnose(state)


def find_shortcut(initial: UnifiedState, target: UnifiedState) -> Optional[HybridPath]:
    """Find shortcut path between states."""
    return ShortcutDetector().find_shortcut_path(initial, target)


def hybrid_evolution(state: UnifiedState, weights: PoleWeights, 
                    steps: int = 10) -> UnifiedState:
    """Evolve state using hybrid operator."""
    solver = UnifiedSolver()
    current = state
    for _ in range(steps):
        current = solver.apply_operator(current, weights)
    return current


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Enums
    'Pole',
    
    # Core classes
    'PoleWeights',
    'UnifiedState',
    
    # Connectors
    'CrossPoleConnector',
    
    # Paths
    'HybridPathStep',
    'HybridPath',
    
    # Detection
    'ShortcutDetector',
    
    # Solver
    'UnifiedSolver',
    
    # Functions
    'create_unified_state',
    'pole_weights',
    'diagnose_state',
    'find_shortcut',
    'hybrid_evolution',
]
