"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    ATLAS FORGE - Representation Routing                       ║
╚══════════════════════════════════════════════════════════════════════════════╝

Four Canonical Representations (Models):

SQUARE (D/Earth):
    - Discrete, combinatorial, lattice-based
    - Vertices, edges, graphs
    - Configurations in finite sets
    - Optimal for: constraints, combinatorics

FLOWER (Ω/Water):
    - Continuous, wave-like, modal
    - Eigenfunctions, harmonics
    - Standing waves, nodal patterns
    - Optimal for: oscillatory, spectral

CLOUD (Σ/Fire):
    - Probabilistic, distributional
    - Probability densities, measures
    - Entropy, mixing
    - Optimal for: sampling, uncertainty

FRACTAL (Ψ/Air):
    - Hierarchical, self-similar
    - Multi-scale, recursive
    - Trees, wavelets
    - Optimal for: compression, abstraction

Representation Routing:
    Route state through the representation that makes the
    current operation simplest, then transform back.

    Square ↔ Flower ↔ Cloud ↔ Fractal
       ↕         ↕         ↕
       └─────────┴─────────┘

Key Principle:
    "Algorithmic advantage arises when state is routed through
    the pole that makes the next transformation simple."
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from enum import Enum
import math

import numpy as np
from numpy.typing import NDArray


class Representation(Enum):
    """The four canonical representations."""
    SQUARE = "square"     # Discrete (D/Earth)
    FLOWER = "flower"     # Wave-like (Ω/Water)
    CLOUD = "cloud"       # Probabilistic (Σ/Fire)
    FRACTAL = "fractal"   # Hierarchical (Ψ/Air)


@dataclass
class SquareState:
    """
    Square representation: discrete/combinatorial state.
    
    Lives on vertices/edges of a graph or lattice.
    """
    values: NDArray                     # Discrete or discretized values
    labels: Optional[List[Any]] = None  # Vertex/state labels
    adjacency: Optional[NDArray] = None # Graph structure
    
    @property
    def dimension(self) -> int:
        return len(self.values)
    
    @property
    def is_binary(self) -> bool:
        return set(np.unique(self.values)).issubset({0, 1, -1})
    
    def to_continuous(self) -> NDArray:
        """Lift to continuous representation."""
        return self.values.astype(float)
    
    @classmethod
    def from_binary(cls, bits: NDArray) -> 'SquareState':
        """Create from binary vector."""
        return cls(values=bits.astype(float))


@dataclass
class FlowerState:
    """
    Flower representation: wave-like/modal state.
    
    Decomposed into eigenfunctions/harmonics.
    """
    coefficients: NDArray              # Modal coefficients
    modes: Optional[NDArray] = None    # Mode shapes (columns)
    frequencies: Optional[NDArray] = None  # Modal frequencies
    
    @property
    def n_modes(self) -> int:
        return len(self.coefficients)
    
    def reconstruct(self) -> NDArray:
        """Reconstruct physical state from modes."""
        if self.modes is None:
            return self.coefficients
        return self.modes @ self.coefficients
    
    def truncate(self, n_modes: int) -> 'FlowerState':
        """Keep only first n modes."""
        return FlowerState(
            coefficients=self.coefficients[:n_modes],
            modes=self.modes[:, :n_modes] if self.modes is not None else None,
            frequencies=self.frequencies[:n_modes] if self.frequencies is not None else None,
        )
    
    @classmethod
    def from_physical(
        cls,
        x: NDArray,
        modes: NDArray,
    ) -> 'FlowerState':
        """Project physical state onto modes."""
        coefficients = np.linalg.lstsq(modes, x, rcond=None)[0]
        return cls(coefficients=coefficients, modes=modes)


@dataclass
class CloudState:
    """
    Cloud representation: probabilistic state.
    
    Distribution over configurations.
    """
    probabilities: NDArray              # Probability vector
    support: Optional[NDArray] = None   # Corresponding states
    temperature: float = 1.0            # Effective temperature
    
    @property
    def n_states(self) -> int:
        return len(self.probabilities)
    
    @property
    def entropy(self) -> float:
        """Shannon entropy of distribution."""
        p = self.probabilities[self.probabilities > 1e-15]
        return -np.sum(p * np.log(p))
    
    def sample(self, n: int = 1, seed: Optional[int] = None) -> NDArray:
        """Sample from distribution."""
        rng = np.random.default_rng(seed)
        indices = rng.choice(self.n_states, size=n, p=self.probabilities)
        if self.support is not None:
            return self.support[indices]
        return indices
    
    def sharpen(self, beta: float) -> 'CloudState':
        """Sharpen distribution by raising to power beta."""
        new_p = self.probabilities ** beta
        new_p /= np.sum(new_p)
        return CloudState(
            probabilities=new_p,
            support=self.support,
            temperature=self.temperature / beta,
        )
    
    def soften(self, alpha: float) -> 'CloudState':
        """Soften distribution toward uniform."""
        n = self.n_states
        uniform = np.ones(n) / n
        new_p = (1 - alpha) * self.probabilities + alpha * uniform
        return CloudState(
            probabilities=new_p,
            support=self.support,
            temperature=self.temperature * (1 + alpha),
        )
    
    @classmethod
    def from_energies(
        cls,
        energies: NDArray,
        temperature: float = 1.0,
    ) -> 'CloudState':
        """Create Gibbs distribution from energies."""
        beta = 1.0 / temperature
        log_p = -beta * energies
        log_p -= np.max(log_p)  # Numerical stability
        p = np.exp(log_p)
        p /= np.sum(p)
        return cls(probabilities=p, temperature=temperature)


@dataclass
class FractalState:
    """
    Fractal representation: hierarchical/multi-scale state.
    
    Organized in scale hierarchy.
    """
    levels: Dict[int, NDArray] = field(default_factory=dict)  # Scale → data
    root: Optional[NDArray] = None                             # Coarsest level
    
    @property
    def n_levels(self) -> int:
        return len(self.levels)
    
    @property
    def finest_level(self) -> int:
        return min(self.levels.keys()) if self.levels else 0
    
    @property
    def coarsest_level(self) -> int:
        return max(self.levels.keys()) if self.levels else 0
    
    def get_level(self, level: int) -> Optional[NDArray]:
        return self.levels.get(level)
    
    def set_level(self, level: int, data: NDArray):
        self.levels[level] = data
    
    @classmethod
    def from_signal(
        cls,
        x: NDArray,
        n_levels: int = 3,
    ) -> 'FractalState':
        """Create hierarchical representation via averaging."""
        state = cls()
        state.set_level(0, x.copy())
        
        current = x.copy()
        for level in range(1, n_levels + 1):
            # Coarsen by averaging pairs
            n = len(current)
            if n < 2:
                break
            coarse = np.zeros(n // 2)
            for i in range(n // 2):
                coarse[i] = (current[2*i] + current[2*i + 1]) / 2
            state.set_level(level, coarse)
            current = coarse
        
        state.root = current
        return state


class RepresentationTransform(ABC):
    """Abstract base for representation transforms."""
    
    @property
    @abstractmethod
    def source(self) -> Representation:
        pass
    
    @property
    @abstractmethod
    def target(self) -> Representation:
        pass
    
    @abstractmethod
    def forward(self, state: Any) -> Any:
        """Transform from source to target."""
        pass
    
    @abstractmethod
    def backward(self, state: Any) -> Any:
        """Transform from target to source."""
        pass


class SquareToFlower(RepresentationTransform):
    """
    Transform Square → Flower via spectral decomposition.
    
    Discrete → Modal: eigendecomposition of graph Laplacian.
    """
    
    def __init__(self, laplacian: Optional[NDArray] = None):
        self._L = laplacian
        self._eigenvectors = None
        self._eigenvalues = None
        
        if laplacian is not None:
            self._decompose()
    
    def _decompose(self):
        self._eigenvalues, self._eigenvectors = np.linalg.eigh(self._L)
    
    @property
    def source(self) -> Representation:
        return Representation.SQUARE
    
    @property
    def target(self) -> Representation:
        return Representation.FLOWER
    
    def forward(self, state: SquareState) -> FlowerState:
        """Project onto eigenmodes."""
        if self._eigenvectors is None:
            # Use DFT as default
            n = state.dimension
            modes = np.fft.fft(np.eye(n), axis=0)
            coeffs = np.fft.fft(state.values) / n
            return FlowerState(coefficients=np.abs(coeffs), modes=modes)
        
        coeffs = self._eigenvectors.T @ state.values
        return FlowerState(
            coefficients=coeffs,
            modes=self._eigenvectors,
            frequencies=self._eigenvalues,
        )
    
    def backward(self, state: FlowerState) -> SquareState:
        """Reconstruct from modes."""
        if state.modes is not None:
            values = state.modes @ state.coefficients
        else:
            values = np.fft.ifft(state.coefficients).real
        return SquareState(values=values.real)


class FlowerToCloud(RepresentationTransform):
    """
    Transform Flower → Cloud via Gibbs distribution.
    
    Modal energies → Probability distribution.
    """
    
    def __init__(self, temperature: float = 1.0):
        self.temperature = temperature
    
    @property
    def source(self) -> Representation:
        return Representation.FLOWER
    
    @property
    def target(self) -> Representation:
        return Representation.CLOUD
    
    def forward(self, state: FlowerState) -> CloudState:
        """Convert modal coefficients to probabilities."""
        # Energy proportional to squared amplitude
        energies = np.abs(state.coefficients) ** 2
        return CloudState.from_energies(energies, self.temperature)
    
    def backward(self, state: CloudState) -> FlowerState:
        """Sample or average to get modal coefficients."""
        # Use probabilities as weights
        coeffs = np.sqrt(state.probabilities) * np.exp(1j * 0)  # Phase = 0
        return FlowerState(coefficients=np.abs(coeffs))


class CloudToFractal(RepresentationTransform):
    """
    Transform Cloud → Fractal via hierarchical clustering.
    
    Distribution → Multi-scale representation.
    """
    
    def __init__(self, n_levels: int = 3):
        self.n_levels = n_levels
    
    @property
    def source(self) -> Representation:
        return Representation.CLOUD
    
    @property
    def target(self) -> Representation:
        return Representation.FRACTAL
    
    def forward(self, state: CloudState) -> FractalState:
        """Hierarchical coarsening of distribution."""
        return FractalState.from_signal(state.probabilities, self.n_levels)
    
    def backward(self, state: FractalState) -> CloudState:
        """Reconstruct distribution from hierarchy."""
        if 0 in state.levels:
            p = state.levels[0]
            p = np.maximum(p, 0)
            p /= np.sum(p)
            return CloudState(probabilities=p)
        return CloudState(probabilities=np.array([1.0]))


class FractalToSquare(RepresentationTransform):
    """
    Transform Fractal → Square via refinement.
    
    Multi-scale → Discrete (coarse-to-fine reconstruction).
    """
    
    @property
    def source(self) -> Representation:
        return Representation.FRACTAL
    
    @property
    def target(self) -> Representation:
        return Representation.SQUARE
    
    def forward(self, state: FractalState) -> SquareState:
        """Reconstruct fine scale from hierarchy."""
        if 0 in state.levels:
            return SquareState(values=state.levels[0])
        
        # Refine from coarsest
        current = state.root if state.root is not None else np.array([0.0])
        
        for level in range(state.coarsest_level - 1, -1, -1):
            if level in state.levels:
                # Use stored value
                current = state.levels[level]
            else:
                # Interpolate
                n = len(current)
                fine = np.zeros(2 * n)
                for i in range(n):
                    fine[2*i] = current[i]
                    fine[2*i + 1] = current[i]
                current = fine
        
        return SquareState(values=current)
    
    def backward(self, state: SquareState) -> FractalState:
        """Create hierarchy from fine scale."""
        return FractalState.from_signal(state.values)


@dataclass
class RepresentationRouter:
    """
    Routes computation through optimal representation.
    
    Core principle: move to the representation where
    the operation is simplest, then transform back.
    """
    
    current_rep: Representation = Representation.SQUARE
    transforms: Dict[Tuple[Representation, Representation], RepresentationTransform] = field(default_factory=dict)
    
    def __post_init__(self):
        # Initialize default transforms
        self._init_default_transforms()
    
    def _init_default_transforms(self):
        """Set up default transforms between representations."""
        self.transforms[(Representation.SQUARE, Representation.FLOWER)] = SquareToFlower()
        self.transforms[(Representation.FLOWER, Representation.CLOUD)] = FlowerToCloud()
        self.transforms[(Representation.CLOUD, Representation.FRACTAL)] = CloudToFractal()
        self.transforms[(Representation.FRACTAL, Representation.SQUARE)] = FractalToSquare()
    
    def transform(
        self,
        state: Any,
        source: Representation,
        target: Representation,
    ) -> Any:
        """Transform state between representations."""
        if source == target:
            return state
        
        key = (source, target)
        if key in self.transforms:
            return self.transforms[key].forward(state)
        
        # Try reverse
        reverse_key = (target, source)
        if reverse_key in self.transforms:
            return self.transforms[reverse_key].backward(state)
        
        # Find path
        path = self._find_path(source, target)
        if path is None:
            raise ValueError(f"No path from {source} to {target}")
        
        current = state
        for i in range(len(path) - 1):
            current = self.transform(current, path[i], path[i+1])
        
        return current
    
    def _find_path(
        self,
        source: Representation,
        target: Representation,
    ) -> Optional[List[Representation]]:
        """Find transformation path (BFS)."""
        from collections import deque
        
        queue = deque([(source, [source])])
        visited = {source}
        
        while queue:
            current, path = queue.popleft()
            
            if current == target:
                return path
            
            # Find neighbors
            for (s, t), _ in self.transforms.items():
                if s == current and t not in visited:
                    visited.add(t)
                    queue.append((t, path + [t]))
                if t == current and s not in visited:
                    visited.add(s)
                    queue.append((s, path + [s]))
        
        return None
    
    def route_operation(
        self,
        state: Any,
        operation: Callable,
        optimal_rep: Representation,
        current_rep: Representation,
        return_rep: Optional[Representation] = None,
    ) -> Any:
        """
        Route state through optimal representation for operation.
        
        Args:
            state: Current state
            operation: Operation to perform
            optimal_rep: Best representation for operation
            current_rep: Current representation
            return_rep: Representation to return to (default: current_rep)
        
        Returns:
            State after operation in return representation
        """
        if return_rep is None:
            return_rep = current_rep
        
        # Transform to optimal
        optimal_state = self.transform(state, current_rep, optimal_rep)
        
        # Apply operation
        result = operation(optimal_state)
        
        # Transform back
        return self.transform(result, optimal_rep, return_rep)


# Convenience functions
def route_through_flower(
    square_state: SquareState,
    operation: Callable[[FlowerState], FlowerState],
    laplacian: Optional[NDArray] = None,
) -> SquareState:
    """Route Square state through Flower for spectral operation."""
    s2f = SquareToFlower(laplacian)
    flower = s2f.forward(square_state)
    flower_result = operation(flower)
    return s2f.backward(flower_result)


def route_through_cloud(
    flower_state: FlowerState,
    operation: Callable[[CloudState], CloudState],
    temperature: float = 1.0,
) -> FlowerState:
    """Route Flower state through Cloud for probabilistic operation."""
    f2c = FlowerToCloud(temperature)
    cloud = f2c.forward(flower_state)
    cloud_result = operation(cloud)
    return f2c.backward(cloud_result)


def optimal_representation_for_task(task: str) -> Representation:
    """Determine optimal representation for a given task."""
    task_lower = task.lower()
    
    if any(x in task_lower for x in ['constraint', 'discrete', 'graph', 'combinatorial']):
        return Representation.SQUARE
    elif any(x in task_lower for x in ['spectral', 'wave', 'fourier', 'oscillat', 'modal']):
        return Representation.FLOWER
    elif any(x in task_lower for x in ['probability', 'sample', 'random', 'stochastic', 'entropy']):
        return Representation.CLOUD
    elif any(x in task_lower for x in ['hierarchy', 'multi-scale', 'recursive', 'wavelet', 'compress']):
        return Representation.FRACTAL
    else:
        return Representation.SQUARE  # Default
