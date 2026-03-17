"""
ATHENA OS - HOLOGRAPHIC ROTATION PROTOCOL
==========================================
Frames: The Four Elemental Lenses

From Holographic_Rotation_Protocol.docx:

FOUR ELEMENTAL FRAMES:

    WATER (W): Continuous fields and flows
        - PDEs, manifolds, vector fields
        - Differential operators, flows
        - Continuous state spaces
        
    EARTH (E): Discrete structures
        - Integers, graphs, algorithms, circuits
        - Finite automata, recurrences
        - Symbolic combinatorics
        
    FIRE (F): Probabilistic and spectral
        - Stochastic processes, Markov chains
        - Energy landscapes, Gibbs measures
        - Thermal/noisy dynamics
        
    AIR (A): Informational and fractal
        - Compression, codes, fractals
        - Symbolic dynamics, grammars
        - Logical systems, factor graphs

Each frame provides:
    - State space representation
    - Dynamics/operator representation
    - Measure representation (invariant/reference)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Callable, Union
from enum import Enum
from abc import ABC, abstractmethod
import numpy as np


# =============================================================================
# ELEMENT ENUMERATION
# =============================================================================

class Element(Enum):
    """The four elemental frames."""
    
    WATER = "water"   # Continuous, geometric
    EARTH = "earth"   # Discrete, combinatorial
    FIRE = "fire"     # Stochastic, thermal
    AIR = "air"       # Informational, symbolic
    
    @property
    def symbol(self) -> str:
        """Get symbolic representation."""
        symbols = {
            Element.WATER: "??",
            Element.EARTH: "??",
            Element.FIRE: "??",
            Element.AIR: "??"
        }
        return symbols[self]
    
    @property
    def description(self) -> str:
        """Get element description."""
        descriptions = {
            Element.WATER: "Continuous fields and flows",
            Element.EARTH: "Discrete structures and algorithms",
            Element.FIRE: "Probabilistic and spectral",
            Element.AIR: "Informational and fractal"
        }
        return descriptions[self]
    
    def next(self) -> 'Element':
        """Get next element in rotation cycle."""
        cycle = [Element.WATER, Element.EARTH, Element.FIRE, Element.AIR]
        idx = cycle.index(self)
        return cycle[(idx + 1) % 4]
    
    def prev(self) -> 'Element':
        """Get previous element in rotation cycle."""
        cycle = [Element.WATER, Element.EARTH, Element.FIRE, Element.AIR]
        idx = cycle.index(self)
        return cycle[(idx - 1) % 4]


# =============================================================================
# STATE SPACE REPRESENTATIONS
# =============================================================================

class StateSpaceType(Enum):
    """Types of state space."""
    
    MANIFOLD = "manifold"       # Continuous manifold
    FUNCTION_SPACE = "function" # Space of functions
    DISCRETE_SET = "discrete"   # Finite/countable set
    GRAPH = "graph"             # Graph structure
    LATTICE = "lattice"         # Integer lattice
    PROBABILITY = "probability" # Probability space
    SYMBOLIC = "symbolic"       # Symbolic alphabet


@dataclass
class StateSpace:
    """Abstract state space descriptor."""
    
    space_type: StateSpaceType
    dimension: Optional[int] = None
    topology: str = "euclidean"
    is_continuous: bool = True
    is_bounded: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        return f"{self.space_type.value}(dim={self.dimension})"


# =============================================================================
# DYNAMICS REPRESENTATIONS
# =============================================================================

class DynamicsType(Enum):
    """Types of dynamics/operators."""
    
    FLOW = "flow"               # Continuous-time flow Φ_t
    MAP = "map"                 # Discrete-time map T
    PDE = "pde"                 # Partial differential equation
    ODE = "ode"                 # Ordinary differential equation
    MARKOV = "markov"           # Markov transition operator
    AUTOMATON = "automaton"     # Finite automaton
    GRAMMAR = "grammar"         # Formal grammar
    CIRCUIT = "circuit"         # Boolean/arithmetic circuit


@dataclass
class Dynamics:
    """Abstract dynamics descriptor."""
    
    dynamics_type: DynamicsType
    generator: Optional[Any] = None  # L, T, or rule
    is_deterministic: bool = True
    is_reversible: bool = False
    time_type: str = "discrete"  # "discrete" or "continuous"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        det = "det" if self.is_deterministic else "stoch"
        return f"{self.dynamics_type.value}({det})"


# =============================================================================
# MEASURE REPRESENTATIONS
# =============================================================================

class MeasureType(Enum):
    """Types of measures."""
    
    LEBESGUE = "lebesgue"       # Lebesgue measure
    COUNTING = "counting"       # Counting measure
    INVARIANT = "invariant"     # Invariant measure
    GIBBS = "gibbs"             # Gibbs/Boltzmann measure
    UNIFORM = "uniform"         # Uniform measure
    SPECTRAL = "spectral"       # Spectral measure


@dataclass
class Measure:
    """Abstract measure descriptor."""
    
    measure_type: MeasureType
    is_probability: bool = True
    is_ergodic: bool = False
    temperature: Optional[float] = None  # For Gibbs measures
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        return f"{self.measure_type.value}"


# =============================================================================
# FRAME BASE CLASS
# =============================================================================

@dataclass
class Frame(ABC):
    """
    Abstract base class for elemental frames.
    
    A Frame is a complete representation of an object in one element:
    - state_space: How states are represented
    - dynamics: How the system evolves
    - measure: Reference or invariant measure
    """
    
    element: Element
    state_space: StateSpace
    dynamics: Dynamics
    measure: Measure
    
    # Frame-specific data
    data: Dict[str, Any] = field(default_factory=dict)
    
    @abstractmethod
    def evaluate(self, state: Any) -> Any:
        """Evaluate dynamics at a state."""
        pass
    
    @abstractmethod
    def sample(self, n: int = 1) -> List[Any]:
        """Sample from measure."""
        pass
    
    def __str__(self) -> str:
        return f"{self.element.symbol} {self.element.value.upper()} Frame"


# =============================================================================
# WATER FRAME
# =============================================================================

@dataclass
class WaterFrame(Frame):
    """
    Water Frame: Continuous fields and flows.
    
    Represents objects through:
    - Manifolds and continuous state spaces
    - PDEs, ODEs, and continuous flows
    - Lebesgue or smooth measures
    """
    
    element: Element = field(default=Element.WATER)
    
    # Water-specific
    field_dimension: int = 3
    flow_function: Optional[Callable] = None
    pde_operator: Optional[Callable] = None
    
    def __post_init__(self):
        if self.state_space is None:
            self.state_space = StateSpace(
                space_type=StateSpaceType.MANIFOLD,
                dimension=self.field_dimension,
                is_continuous=True
            )
        if self.dynamics is None:
            self.dynamics = Dynamics(
                dynamics_type=DynamicsType.FLOW,
                time_type="continuous"
            )
        if self.measure is None:
            self.measure = Measure(measure_type=MeasureType.LEBESGUE)
    
    def evaluate(self, state: np.ndarray) -> np.ndarray:
        """Evaluate flow at state."""
        if self.flow_function is not None:
            return self.flow_function(state)
        return state  # Identity
    
    def sample(self, n: int = 1) -> List[np.ndarray]:
        """Sample from continuous measure."""
        dim = self.field_dimension
        return [np.random.randn(dim) for _ in range(n)]
    
    def integrate_flow(self, initial: np.ndarray, 
                       t_span: Tuple[float, float],
                       dt: float = 0.01) -> np.ndarray:
        """Integrate flow from initial condition."""
        if self.flow_function is None:
            return initial
        
        t0, t1 = t_span
        t = t0
        state = initial.copy()
        trajectory = [state.copy()]
        
        while t < t1:
            # Euler step
            dstate = self.flow_function(state)
            state = state + dt * dstate
            t += dt
            trajectory.append(state.copy())
        
        return np.array(trajectory)


# =============================================================================
# EARTH FRAME
# =============================================================================

@dataclass
class EarthFrame(Frame):
    """
    Earth Frame: Discrete structures and algorithms.
    
    Represents objects through:
    - Integers, graphs, lattices
    - Discrete maps, automata
    - Counting measures
    """
    
    element: Element = field(default=Element.EARTH)
    
    # Earth-specific
    alphabet_size: int = 2
    graph_vertices: int = 10
    transition_map: Optional[Callable] = None
    
    def __post_init__(self):
        if self.state_space is None:
            self.state_space = StateSpace(
                space_type=StateSpaceType.DISCRETE_SET,
                dimension=self.graph_vertices,
                is_continuous=False
            )
        if self.dynamics is None:
            self.dynamics = Dynamics(
                dynamics_type=DynamicsType.MAP,
                time_type="discrete"
            )
        if self.measure is None:
            self.measure = Measure(measure_type=MeasureType.COUNTING)
    
    def evaluate(self, state: int) -> int:
        """Apply discrete map."""
        if self.transition_map is not None:
            return self.transition_map(state)
        return state
    
    def sample(self, n: int = 1) -> List[int]:
        """Sample discrete states."""
        return list(np.random.randint(0, self.graph_vertices, n))
    
    def iterate(self, initial: int, steps: int) -> List[int]:
        """Iterate discrete map."""
        trajectory = [initial]
        state = initial
        
        for _ in range(steps):
            state = self.evaluate(state)
            trajectory.append(state)
        
        return trajectory
    
    def build_transition_matrix(self) -> np.ndarray:
        """Build transition matrix from map."""
        n = self.graph_vertices
        T = np.zeros((n, n))
        
        for i in range(n):
            j = self.evaluate(i)
            if 0 <= j < n:
                T[i, j] = 1.0
        
        return T


# =============================================================================
# FIRE FRAME
# =============================================================================

@dataclass
class FireFrame(Frame):
    """
    Fire Frame: Probabilistic and spectral.
    
    Represents objects through:
    - Stochastic processes, Markov chains
    - Energy landscapes, Gibbs measures
    - Spectral decompositions
    """
    
    element: Element = field(default=Element.FIRE)
    
    # Fire-specific
    state_count: int = 10
    temperature: float = 1.0
    transition_matrix: Optional[np.ndarray] = None
    energy_function: Optional[Callable] = None
    
    def __post_init__(self):
        if self.state_space is None:
            self.state_space = StateSpace(
                space_type=StateSpaceType.PROBABILITY,
                dimension=self.state_count,
                is_continuous=False
            )
        if self.dynamics is None:
            self.dynamics = Dynamics(
                dynamics_type=DynamicsType.MARKOV,
                is_deterministic=False,
                time_type="discrete"
            )
        if self.measure is None:
            self.measure = Measure(
                measure_type=MeasureType.GIBBS,
                temperature=self.temperature
            )
        
        # Initialize transition matrix if not provided
        if self.transition_matrix is None:
            self.transition_matrix = self._default_transition_matrix()
    
    def _default_transition_matrix(self) -> np.ndarray:
        """Create default stochastic transition matrix."""
        n = self.state_count
        P = np.random.rand(n, n)
        P = P / P.sum(axis=1, keepdims=True)  # Row stochastic
        return P
    
    def evaluate(self, state: int) -> int:
        """Sample next state from transition probabilities."""
        if self.transition_matrix is None:
            return state
        probs = self.transition_matrix[state]
        return int(np.random.choice(len(probs), p=probs))
    
    def sample(self, n: int = 1) -> List[int]:
        """Sample from stationary distribution."""
        if self.transition_matrix is None:
            return list(np.random.randint(0, self.state_count, n))
        
        # Find stationary distribution (approximate)
        P = self.transition_matrix
        pi = np.ones(len(P)) / len(P)
        for _ in range(100):
            pi = pi @ P
        
        return list(np.random.choice(len(pi), n, p=pi))
    
    def spectral_gap(self) -> float:
        """Compute spectral gap of transition matrix."""
        if self.transition_matrix is None:
            return 0.0
        
        eigenvalues = np.linalg.eigvals(self.transition_matrix)
        eigenvalues = np.sort(np.abs(eigenvalues))[::-1]
        
        if len(eigenvalues) < 2:
            return 0.0
        
        return float(1.0 - eigenvalues[1])
    
    def mixing_time(self, epsilon: float = 0.01) -> int:
        """Estimate mixing time."""
        gap = self.spectral_gap()
        if gap < 1e-10:
            return 10000  # Very slow mixing
        return int(np.ceil(np.log(1/epsilon) / gap))


# =============================================================================
# AIR FRAME
# =============================================================================

@dataclass
class AirFrame(Frame):
    """
    Air Frame: Informational and fractal.
    
    Represents objects through:
    - Symbolic dynamics, codes, grammars
    - Compression, information measures
    - Fractal structures
    """
    
    element: Element = field(default=Element.AIR)
    
    # Air-specific
    alphabet: List[str] = field(default_factory=lambda: ['0', '1'])
    grammar_rules: Dict[str, List[str]] = field(default_factory=dict)
    encoder: Optional[Callable] = None
    decoder: Optional[Callable] = None
    
    def __post_init__(self):
        if self.state_space is None:
            self.state_space = StateSpace(
                space_type=StateSpaceType.SYMBOLIC,
                dimension=len(self.alphabet),
                is_continuous=False
            )
        if self.dynamics is None:
            self.dynamics = Dynamics(
                dynamics_type=DynamicsType.GRAMMAR,
                time_type="discrete"
            )
        if self.measure is None:
            self.measure = Measure(measure_type=MeasureType.UNIFORM)
    
    def evaluate(self, state: str) -> str:
        """Apply grammar rule."""
        if state in self.grammar_rules:
            rules = self.grammar_rules[state]
            if rules:
                return np.random.choice(rules)
        return state
    
    def sample(self, n: int = 1) -> List[str]:
        """Sample symbolic strings."""
        length = 10  # Default string length
        return [
            ''.join(np.random.choice(self.alphabet, length))
            for _ in range(n)
        ]
    
    def encode(self, data: Any) -> str:
        """Encode data to symbolic form."""
        if self.encoder is not None:
            return self.encoder(data)
        return str(data)
    
    def decode(self, code: str) -> Any:
        """Decode symbolic form to data."""
        if self.decoder is not None:
            return self.decoder(code)
        return code
    
    def entropy_rate(self, sequence: str) -> float:
        """Estimate entropy rate of sequence."""
        if len(sequence) < 2:
            return 0.0
        
        # Count symbol frequencies
        freq = {}
        for s in sequence:
            freq[s] = freq.get(s, 0) + 1
        
        # Compute entropy
        n = len(sequence)
        h = 0.0
        for count in freq.values():
            p = count / n
            if p > 0:
                h -= p * np.log(p)
        
        return h
    
    def compression_ratio(self, data: str) -> float:
        """Estimate compression ratio (simplified)."""
        original_length = len(data)
        
        # Count unique symbols
        unique = len(set(data))
        if unique == 0:
            return 1.0
        
        # Theoretical minimum bits
        min_bits = np.ceil(np.log2(unique + 1))
        actual_bits = 8  # Assuming ASCII
        
        return min_bits / actual_bits


# =============================================================================
# FRAME FACTORY
# =============================================================================

def create_frame(element: Element, **kwargs) -> Frame:
    """Factory function to create frames."""
    frame_classes = {
        Element.WATER: WaterFrame,
        Element.EARTH: EarthFrame,
        Element.FIRE: FireFrame,
        Element.AIR: AirFrame,
    }
    
    cls = frame_classes[element]
    
    # Create minimal state_space, dynamics, measure if not provided
    default_state = StateSpace(StateSpaceType.DISCRETE_SET)
    default_dyn = Dynamics(DynamicsType.MAP)
    default_meas = Measure(MeasureType.UNIFORM)
    
    return cls(
        state_space=kwargs.get('state_space', default_state),
        dynamics=kwargs.get('dynamics', default_dyn),
        measure=kwargs.get('measure', default_meas),
        **{k: v for k, v in kwargs.items() 
           if k not in ['state_space', 'dynamics', 'measure']}
    )


# =============================================================================
# VALIDATION
# =============================================================================

def validate_frames() -> bool:
    """Validate frames module."""
    
    # Test Element
    assert Element.WATER.next() == Element.EARTH
    assert Element.AIR.next() == Element.WATER
    assert Element.WATER.prev() == Element.AIR
    
    # Test WaterFrame
    water = WaterFrame(
        state_space=StateSpace(StateSpaceType.MANIFOLD, dimension=3),
        dynamics=Dynamics(DynamicsType.FLOW),
        measure=Measure(MeasureType.LEBESGUE),
        flow_function=lambda x: -0.1 * x  # Decay flow
    )
    
    samples = water.sample(5)
    assert len(samples) == 5
    
    initial = np.array([1.0, 0.0, 0.0])
    trajectory = water.integrate_flow(initial, (0, 1), dt=0.1)
    assert len(trajectory) > 1
    
    # Test EarthFrame
    earth = EarthFrame(
        state_space=StateSpace(StateSpaceType.DISCRETE_SET),
        dynamics=Dynamics(DynamicsType.MAP),
        measure=Measure(MeasureType.COUNTING),
        graph_vertices=10,
        transition_map=lambda x: (x + 1) % 10
    )
    
    trajectory = earth.iterate(0, 10)
    assert len(trajectory) == 11
    assert trajectory[10] == 0  # Should cycle back
    
    T = earth.build_transition_matrix()
    assert T.shape == (10, 10)
    
    # Test FireFrame
    fire = FireFrame(
        state_space=StateSpace(StateSpaceType.PROBABILITY),
        dynamics=Dynamics(DynamicsType.MARKOV),
        measure=Measure(MeasureType.GIBBS),
        state_count=5
    )
    
    gap = fire.spectral_gap()
    assert 0 <= gap <= 1
    
    # Test AirFrame
    air = AirFrame(
        state_space=StateSpace(StateSpaceType.SYMBOLIC),
        dynamics=Dynamics(DynamicsType.GRAMMAR),
        measure=Measure(MeasureType.UNIFORM),
        alphabet=['a', 'b', 'c']
    )
    
    samples = air.sample(3)
    assert len(samples) == 3
    
    h = air.entropy_rate("aabbccaabbcc")
    assert h > 0
    
    # Test factory
    frame = create_frame(Element.FIRE, state_count=8)
    assert frame.element == Element.FIRE
    
    return True


if __name__ == "__main__":
    print("Validating Frames...")
    assert validate_frames()
    print("✓ Frames module validated")
