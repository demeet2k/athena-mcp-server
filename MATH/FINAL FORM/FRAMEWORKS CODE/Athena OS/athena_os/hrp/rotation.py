"""
ATHENA OS - HOLOGRAPHIC ROTATION PROTOCOL
==========================================
Rotation: Functors Between Elemental Frames

From Holographic_Rotation_Protocol.docx:

ROTATION OPERATORS R_{α→β}:
    Transport system between elemental views.

    R_{W→E}: Water → Earth
        Discretization, coding, algorithmic realization
        Continuous → Discrete
        
    R_{E→F}: Earth → Fire
        Randomization, ensemble lifting
        Deterministic → Stochastic
        
    R_{F→A}: Fire → Air
        Spectral/information-theoretic lifting
        Stochastic → Informational
        
    R_{A→W}: Air → Water
        Reconstruction of continuum fields
        Symbolic → Continuous

APPROXIMATE INVERSES:
    R_{β→α} ∘ R_{α→β}(X) ≃ X
    
    Round-trip property up to acceptable distortion.

COHERENCE ACROSS CHAINS:
    Rotations compose with bounded accumulated distortion.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Callable, Type
from enum import Enum
from abc import ABC, abstractmethod
import numpy as np

from .frames import (
    Element, Frame, StateSpace, Dynamics, Measure,
    WaterFrame, EarthFrame, FireFrame, AirFrame,
    StateSpaceType, DynamicsType, MeasureType
)
from .texture import TextureTriple, TextureAnalyzer


# =============================================================================
# ROTATION BASE CLASS
# =============================================================================

@dataclass
class RotationOperator(ABC):
    """
    Abstract base class for rotation operators.
    
    R_{α→β}: C_α → C_β
    
    Maps objects from source element to target element.
    """
    
    source: Element
    target: Element
    
    # Distortion tracking
    distortion_bound: float = 0.1
    distortion_metric: str = "l2"
    
    @property
    def name(self) -> str:
        """Rotation name."""
        return f"R_{{{self.source.value[0].upper()}→{self.target.value[0].upper()}}}"
    
    @abstractmethod
    def rotate(self, frame: Frame) -> Frame:
        """Apply rotation to frame."""
        pass
    
    @abstractmethod
    def estimate_distortion(self, original: Frame, rotated: Frame) -> float:
        """Estimate distortion introduced by rotation."""
        pass
    
    def __call__(self, frame: Frame) -> Frame:
        """Apply rotation operator."""
        if frame.element != self.source:
            raise ValueError(f"Expected {self.source} frame, got {frame.element}")
        return self.rotate(frame)


# =============================================================================
# WATER → EARTH (Discretization)
# =============================================================================

@dataclass
class WaterToEarth(RotationOperator):
    """
    R_{W→E}: Discretization functor.
    
    Transforms continuous fields/flows into discrete structures:
    - Grid discretization of PDEs
    - Graph approximation of manifolds
    - Finite automata from continuous dynamics
    """
    
    source: Element = field(default=Element.WATER)
    target: Element = field(default=Element.EARTH)
    
    # Discretization parameters
    grid_resolution: int = 10
    time_step: float = 0.1
    
    def rotate(self, frame: WaterFrame) -> EarthFrame:
        """Discretize Water frame to Earth frame."""
        
        # Discretize state space
        n_points = self.grid_resolution ** frame.field_dimension
        
        discrete_space = StateSpace(
            space_type=StateSpaceType.LATTICE,
            dimension=n_points,
            is_continuous=False
        )
        
        # Discretize dynamics (create transition map)
        def discrete_map(state_idx: int) -> int:
            """Map discrete state index to next state index."""
            # Convert index to continuous state
            coords = self._idx_to_coords(state_idx, frame.field_dimension)
            state = np.array(coords) / self.grid_resolution
            
            # Apply flow
            if frame.flow_function is not None:
                next_state = state + self.time_step * frame.flow_function(state)
            else:
                next_state = state
            
            # Convert back to index
            return self._coords_to_idx(
                tuple(np.clip(
                    (next_state * self.grid_resolution).astype(int),
                    0, self.grid_resolution - 1
                )),
                frame.field_dimension
            )
        
        discrete_dynamics = Dynamics(
            dynamics_type=DynamicsType.MAP,
            generator=discrete_map,
            is_deterministic=True,
            time_type="discrete"
        )
        
        # Discretize measure
        discrete_measure = Measure(
            measure_type=MeasureType.COUNTING,
            is_probability=True
        )
        
        return EarthFrame(
            state_space=discrete_space,
            dynamics=discrete_dynamics,
            measure=discrete_measure,
            graph_vertices=n_points,
            transition_map=discrete_map,
            data={"source": frame, "rotation": self.name}
        )
    
    def _idx_to_coords(self, idx: int, dim: int) -> Tuple[int, ...]:
        """Convert linear index to grid coordinates."""
        coords = []
        for _ in range(dim):
            coords.append(idx % self.grid_resolution)
            idx //= self.grid_resolution
        return tuple(coords)
    
    def _coords_to_idx(self, coords: Tuple[int, ...], dim: int) -> int:
        """Convert grid coordinates to linear index."""
        idx = 0
        multiplier = 1
        for i in range(dim):
            idx += coords[i] * multiplier
            multiplier *= self.grid_resolution
        return idx
    
    def estimate_distortion(self, original: WaterFrame, 
                           rotated: EarthFrame) -> float:
        """Estimate discretization error."""
        # Distortion proportional to grid spacing
        return 1.0 / self.grid_resolution


# =============================================================================
# EARTH → FIRE (Randomization)
# =============================================================================

@dataclass
class EarthToFire(RotationOperator):
    """
    R_{E→F}: Randomization functor.
    
    Transforms discrete deterministic dynamics into stochastic:
    - Add noise to transitions
    - Ensemble lifting
    - Probabilistic interpretation
    """
    
    source: Element = field(default=Element.EARTH)
    target: Element = field(default=Element.FIRE)
    
    # Randomization parameters
    temperature: float = 1.0
    noise_level: float = 0.1
    
    def rotate(self, frame: EarthFrame) -> FireFrame:
        """Randomize Earth frame to Fire frame."""
        
        n_states = frame.graph_vertices
        
        # Create stochastic transition matrix
        P = self._create_transition_matrix(frame)
        
        stochastic_space = StateSpace(
            space_type=StateSpaceType.PROBABILITY,
            dimension=n_states,
            is_continuous=False
        )
        
        stochastic_dynamics = Dynamics(
            dynamics_type=DynamicsType.MARKOV,
            generator=P,
            is_deterministic=False,
            time_type="discrete"
        )
        
        gibbs_measure = Measure(
            measure_type=MeasureType.GIBBS,
            is_probability=True,
            temperature=self.temperature
        )
        
        return FireFrame(
            state_space=stochastic_space,
            dynamics=stochastic_dynamics,
            measure=gibbs_measure,
            state_count=n_states,
            temperature=self.temperature,
            transition_matrix=P,
            data={"source": frame, "rotation": self.name}
        )
    
    def _create_transition_matrix(self, frame: EarthFrame) -> np.ndarray:
        """Create stochastic transition matrix from deterministic map."""
        n = frame.graph_vertices
        P = np.zeros((n, n))
        
        for i in range(n):
            # Deterministic target
            if frame.transition_map is not None:
                j = frame.transition_map(i) % n
            else:
                j = i
            
            # Add probability mass to deterministic target
            P[i, j] = 1.0 - self.noise_level
            
            # Distribute remaining mass uniformly (noise)
            noise_mass = self.noise_level / n
            P[i, :] += noise_mass
        
        # Normalize rows
        P = P / P.sum(axis=1, keepdims=True)
        
        return P
    
    def estimate_distortion(self, original: EarthFrame,
                           rotated: FireFrame) -> float:
        """Estimate randomization distortion."""
        return self.noise_level


# =============================================================================
# FIRE → AIR (Information Lifting)
# =============================================================================

@dataclass
class FireToAir(RotationOperator):
    """
    R_{F→A}: Information-theoretic lifting functor.
    
    Transforms stochastic dynamics into informational:
    - Spectral decomposition
    - Entropy/coding representation
    - Symbolic dynamics extraction
    """
    
    source: Element = field(default=Element.FIRE)
    target: Element = field(default=Element.AIR)
    
    # Information parameters
    code_length: int = 8
    
    def rotate(self, frame: FireFrame) -> AirFrame:
        """Lift Fire frame to Air frame."""
        
        n_states = frame.state_count
        
        # Create symbolic alphabet
        alphabet = [str(i) for i in range(n_states)]
        
        # Create grammar rules from transition probabilities
        grammar = self._create_grammar(frame)
        
        symbolic_space = StateSpace(
            space_type=StateSpaceType.SYMBOLIC,
            dimension=n_states,
            is_continuous=False
        )
        
        symbolic_dynamics = Dynamics(
            dynamics_type=DynamicsType.GRAMMAR,
            generator=grammar,
            is_deterministic=False,
            time_type="discrete"
        )
        
        uniform_measure = Measure(
            measure_type=MeasureType.UNIFORM,
            is_probability=True
        )
        
        return AirFrame(
            state_space=symbolic_space,
            dynamics=symbolic_dynamics,
            measure=uniform_measure,
            alphabet=alphabet,
            grammar_rules=grammar,
            encoder=lambda x: str(x),
            decoder=lambda s: int(s) if s.isdigit() else 0,
            data={"source": frame, "rotation": self.name}
        )
    
    def _create_grammar(self, frame: FireFrame) -> Dict[str, List[str]]:
        """Create probabilistic grammar from transition matrix."""
        grammar = {}
        P = frame.transition_matrix
        
        if P is None:
            return grammar
        
        n = len(P)
        for i in range(n):
            # Non-deterministic: multiple possible productions
            successors = []
            for j in range(n):
                if P[i, j] > 0.01:  # Threshold
                    successors.append(str(j))
            grammar[str(i)] = successors if successors else [str(i)]
        
        return grammar
    
    def estimate_distortion(self, original: FireFrame,
                           rotated: AirFrame) -> float:
        """Estimate information compression distortion."""
        # Distortion from discretizing probabilities
        return 0.05


# =============================================================================
# AIR → WATER (Reconstruction)
# =============================================================================

@dataclass
class AirToWater(RotationOperator):
    """
    R_{A→W}: Reconstruction functor.
    
    Transforms informational/symbolic back to continuous:
    - Interpolation from symbolic data
    - Field reconstruction
    - Effective PDE derivation
    """
    
    source: Element = field(default=Element.AIR)
    target: Element = field(default=Element.WATER)
    
    # Reconstruction parameters
    smoothing: float = 0.1
    field_dim: int = 3
    
    def rotate(self, frame: AirFrame) -> WaterFrame:
        """Reconstruct Water frame from Air frame."""
        
        continuous_space = StateSpace(
            space_type=StateSpaceType.MANIFOLD,
            dimension=self.field_dim,
            is_continuous=True
        )
        
        # Create flow from symbolic dynamics
        flow_func = self._create_flow(frame)
        
        continuous_dynamics = Dynamics(
            dynamics_type=DynamicsType.FLOW,
            generator=flow_func,
            is_deterministic=True,
            time_type="continuous"
        )
        
        lebesgue_measure = Measure(
            measure_type=MeasureType.LEBESGUE,
            is_probability=False
        )
        
        return WaterFrame(
            state_space=continuous_space,
            dynamics=continuous_dynamics,
            measure=lebesgue_measure,
            field_dimension=self.field_dim,
            flow_function=flow_func,
            data={"source": frame, "rotation": self.name}
        )
    
    def _create_flow(self, frame: AirFrame) -> Callable:
        """Create continuous flow from symbolic dynamics."""
        def flow(state: np.ndarray) -> np.ndarray:
            # Simple reconstruction: gradient descent toward attractor
            # Based on symbolic structure
            
            # Map state to symbol
            idx = int(np.sum(state) * 10) % len(frame.alphabet)
            symbol = frame.alphabet[idx]
            
            # Get next symbols
            if symbol in frame.grammar_rules:
                next_symbols = frame.grammar_rules[symbol]
                # Average of next state indices
                avg_next = np.mean([
                    int(s) if s.isdigit() else 0 
                    for s in next_symbols
                ])
            else:
                avg_next = idx
            
            # Create flow vector pointing toward next state
            target = np.ones(len(state)) * avg_next / 10
            return self.smoothing * (target - state)
        
        return flow
    
    def estimate_distortion(self, original: AirFrame,
                           rotated: WaterFrame) -> float:
        """Estimate reconstruction distortion."""
        return self.smoothing


# =============================================================================
# ROTATION CHAIN
# =============================================================================

@dataclass
class RotationChain:
    """
    Composed rotation operators.
    
    Allows chaining: R_{α→β} ∘ R_{γ→α} etc.
    Tracks cumulative distortion.
    """
    
    rotations: List[RotationOperator] = field(default_factory=list)
    total_distortion: float = 0.0
    
    def add(self, rotation: RotationOperator) -> 'RotationChain':
        """Add rotation to chain."""
        self.rotations.append(rotation)
        return self
    
    def apply(self, frame: Frame) -> Tuple[Frame, float]:
        """Apply rotation chain to frame."""
        current = frame
        distortion = 0.0
        
        for rotation in self.rotations:
            next_frame = rotation(current)
            distortion += rotation.estimate_distortion(current, next_frame)
            current = next_frame
        
        self.total_distortion = distortion
        return current, distortion
    
    @property
    def source(self) -> Element:
        """Source element of chain."""
        if self.rotations:
            return self.rotations[0].source
        return Element.WATER
    
    @property
    def target(self) -> Element:
        """Target element of chain."""
        if self.rotations:
            return self.rotations[-1].target
        return Element.WATER


# =============================================================================
# FULL ROTATION CYCLE
# =============================================================================

@dataclass
class RotationCycle:
    """
    Complete rotation through all four elements.
    
    W → E → F → A → W
    
    Analyzes texture at each stage and computes invariants.
    """
    
    # Default rotation operators
    w_to_e: WaterToEarth = field(default_factory=WaterToEarth)
    e_to_f: EarthToFire = field(default_factory=EarthToFire)
    f_to_a: FireToAir = field(default_factory=FireToAir)
    a_to_w: AirToWater = field(default_factory=AirToWater)
    
    # Results
    frames: Dict[Element, Frame] = field(default_factory=dict)
    textures: Dict[Element, TextureTriple] = field(default_factory=dict)
    distortions: Dict[str, float] = field(default_factory=dict)
    
    def rotate(self, initial_frame: WaterFrame) -> Dict[Element, Frame]:
        """
        Perform full rotation cycle.
        
        Returns frames at each element.
        """
        self.frames[Element.WATER] = initial_frame
        
        # W → E
        earth = self.w_to_e(initial_frame)
        self.frames[Element.EARTH] = earth
        self.distortions["W→E"] = self.w_to_e.estimate_distortion(
            initial_frame, earth
        )
        
        # E → F
        fire = self.e_to_f(earth)
        self.frames[Element.FIRE] = fire
        self.distortions["E→F"] = self.e_to_f.estimate_distortion(
            earth, fire
        )
        
        # F → A
        air = self.f_to_a(fire)
        self.frames[Element.AIR] = air
        self.distortions["F→A"] = self.f_to_a.estimate_distortion(
            fire, air
        )
        
        # A → W
        water_final = self.a_to_w(air)
        self.frames[Element.WATER] = water_final
        self.distortions["A→W"] = self.a_to_w.estimate_distortion(
            air, water_final
        )
        
        return self.frames
    
    @property
    def total_distortion(self) -> float:
        """Total accumulated distortion."""
        return sum(self.distortions.values())


# =============================================================================
# ROTATION FACTORY
# =============================================================================

def get_rotation(source: Element, target: Element) -> RotationOperator:
    """Get rotation operator between elements."""
    rotations = {
        (Element.WATER, Element.EARTH): WaterToEarth,
        (Element.EARTH, Element.FIRE): EarthToFire,
        (Element.FIRE, Element.AIR): FireToAir,
        (Element.AIR, Element.WATER): AirToWater,
    }
    
    key = (source, target)
    if key in rotations:
        return rotations[key]()
    
    # For non-adjacent rotations, compose
    cycle = [Element.WATER, Element.EARTH, Element.FIRE, Element.AIR]
    source_idx = cycle.index(source)
    target_idx = cycle.index(target)
    
    if target_idx > source_idx:
        steps = target_idx - source_idx
    else:
        steps = 4 - source_idx + target_idx
    
    chain = RotationChain()
    current = source
    for _ in range(steps):
        next_elem = current.next()
        chain.add(get_rotation(current, next_elem))
        current = next_elem
    
    # Return composed rotation (simplified - just use first)
    return chain.rotations[0] if chain.rotations else WaterToEarth()


# =============================================================================
# VALIDATION
# =============================================================================

def validate_rotation() -> bool:
    """Validate rotation module."""
    
    # Create a simple Water frame
    water = WaterFrame(
        state_space=StateSpace(StateSpaceType.MANIFOLD, dimension=2),
        dynamics=Dynamics(DynamicsType.FLOW),
        measure=Measure(MeasureType.LEBESGUE),
        field_dimension=2,
        flow_function=lambda x: -0.1 * x
    )
    
    # Test W → E
    w_to_e = WaterToEarth(grid_resolution=5)
    earth = w_to_e(water)
    assert earth.element == Element.EARTH
    assert earth.graph_vertices == 25  # 5^2
    
    distortion_we = w_to_e.estimate_distortion(water, earth)
    assert distortion_we > 0
    
    # Test E → F
    e_to_f = EarthToFire(noise_level=0.05)
    fire = e_to_f(earth)
    assert fire.element == Element.FIRE
    assert fire.transition_matrix is not None
    
    # Verify stochastic matrix
    P = fire.transition_matrix
    assert np.allclose(P.sum(axis=1), 1.0)
    
    # Test F → A
    f_to_a = FireToAir()
    air = f_to_a(fire)
    assert air.element == Element.AIR
    assert len(air.alphabet) == fire.state_count
    
    # Test A → W
    a_to_w = AirToWater(field_dim=2)
    water_final = a_to_w(air)
    assert water_final.element == Element.WATER
    assert water_final.flow_function is not None
    
    # Test full cycle
    cycle = RotationCycle()
    frames = cycle.rotate(water)
    
    assert len(frames) == 4
    assert Element.WATER in frames
    assert Element.EARTH in frames
    assert Element.FIRE in frames
    assert Element.AIR in frames
    
    total = cycle.total_distortion
    assert total > 0
    
    # Test rotation chain
    chain = RotationChain()
    chain.add(WaterToEarth())
    chain.add(EarthToFire())
    
    result, dist = chain.apply(water)
    assert result.element == Element.FIRE
    assert dist > 0
    
    return True


if __name__ == "__main__":
    print("Validating Rotation...")
    assert validate_rotation()
    print("✓ Rotation module validated")
