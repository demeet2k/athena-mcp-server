"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        ATLAS FORGE - Pole Archetypes                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

The four elemental archetypes (Fire, Air, Water, Earth) that form the
metaphysical backbone of the framework. Each archetype represents a
fundamental mode of causation and transformation.

The 90° Rotation Rule:
- Adjacent poles can tunnel: Fire ↔ Air ↔ Water ↔ Earth ↔ Fire  
- Opposites don't touch directly: Fire/Water and Air/Earth are conjugate pairs
- When stuck, rotate into adjacent archetype—never push harder in same pole
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import (
    Any, Callable, Dict, Generic, List, Optional, 
    Set, Tuple, Type, TypeVar, Union
)
from enum import Enum
import math

from atlasforge.core.enums import Pole, Element
from atlasforge.core.base import AtlasObject, register_type


T = TypeVar('T')


class Archetype(ABC):
    """
    Abstract base class for elemental archetypes.
    
    Each archetype defines:
    - Core function (what it does)
    - Pattern signature (how it manifests)
    - Failure mode / shadow (how it breaks)
    - Rotation rules (how to escape)
    """
    
    @property
    @abstractmethod
    def element(self) -> Element:
        """The elemental type of this archetype."""
        pass
    
    @property
    @abstractmethod
    def pole(self) -> Pole:
        """The corresponding operator pole."""
        pass
    
    @property
    @abstractmethod
    def core_function(self) -> str:
        """The core function of this archetype."""
        pass
    
    @property
    @abstractmethod
    def pattern_signature(self) -> str:
        """The pattern signature (how it manifests in systems)."""
        pass
    
    @property
    @abstractmethod
    def shadow(self) -> str:
        """The failure mode (shadow) of this archetype."""
        pass
    
    @property
    def opposite(self) -> Type['Archetype']:
        """The conjugate/opposite archetype (cannot tunnel directly)."""
        opposites = {
            Element.FIRE: Earth,
            Element.EARTH: Fire,
            Element.AIR: Water,
            Element.WATER: Air,
        }
        return opposites[self.element]
    
    @property
    def adjacent(self) -> Tuple[Type['Archetype'], Type['Archetype']]:
        """The two adjacent archetypes (can tunnel via 90° rotation)."""
        adjacencies = {
            Element.FIRE: (Air, Earth),
            Element.AIR: (Fire, Water),
            Element.WATER: (Air, Earth),
            Element.EARTH: (Water, Fire),
        }
        return adjacencies[self.element]
    
    def can_tunnel_to(self, other: 'Archetype') -> bool:
        """Check if direct tunneling (90° rotation) is allowed."""
        return type(other) in self.adjacent
    
    @abstractmethod
    def apply(self, state: Any) -> Any:
        """Apply this archetype's transformation to a state."""
        pass
    
    @abstractmethod
    def detect_shadow(self, state: Any) -> bool:
        """Detect if the state exhibits the shadow (failure mode)."""
        pass
    
    def escape_shadow(self) -> Tuple[Type['Archetype'], str]:
        """
        Return the recommended escape when stuck in shadow.
        
        Returns:
            Tuple of (adjacent archetype to rotate into, guidance message)
        """
        adj1, adj2 = self.adjacent
        return adj1, f"Rotate 90° into {adj1.__name__} archetype"


@dataclass
class Fire(Archetype):
    """
    FIRE Archetype: Initiation / Impulse / Ignition
    
    Core function: The "start the move" archetype
    Pattern signature: Generates energy, pushes phase forward, creates gradient
    System terms: Drive, will, activation, "do the first rep"
    Failure mode: Reckless forcing, premature collapse, overheat
    
    In operator terms: D (Dissipative) - contractive, smoothing, entropy-decreasing
    """
    
    intensity: float = field(default=1.0)
    momentum: float = field(default=0.0)
    
    @property
    def element(self) -> Element:
        return Element.FIRE
    
    @property
    def pole(self) -> Pole:
        return Pole.D
    
    @property
    def core_function(self) -> str:
        return "Initiation / impulse / ignition — the 'start the move' archetype"
    
    @property
    def pattern_signature(self) -> str:
        return "Generates energy, pushes phase forward, creates gradient (difference) that forces motion"
    
    @property
    def shadow(self) -> str:
        return "Reckless forcing, premature collapse, overheat"
    
    def apply(self, state: Any) -> Any:
        """
        Apply Fire transformation: inject energy gradient.
        
        For numeric states, this adds momentum/impulse.
        """
        if isinstance(state, (int, float)):
            return state + self.intensity * (1 + self.momentum)
        elif hasattr(state, '__add__'):
            return state + self.intensity
        else:
            raise TypeError(f"Cannot apply Fire to {type(state)}")
    
    def detect_shadow(self, state: Any) -> bool:
        """
        Detect overheat/forcing.
        
        Shadow manifests when:
        - Energy is too high (overheat)
        - Changes are too rapid (forcing)
        - System is destabilizing
        """
        if isinstance(state, (int, float)):
            # Overheat: value exceeds reasonable bounds
            return abs(state) > 1e6 or math.isnan(state) or math.isinf(state)
        return False
    
    def ignite(self, initial: float = 0.0) -> float:
        """Create initial impulse."""
        return self.apply(initial)
    
    def pulse(self, state: float, frequency: float = 1.0) -> float:
        """Apply pulsed energy injection."""
        return state + self.intensity * math.sin(frequency * state)


@dataclass
class Air(Archetype):
    """
    AIR Archetype: Structure through Relation / Mapping / Routing
    
    Core function: The "connect the nodes" archetype
    Pattern signature: Builds links, creates models, moves information sideways
    System terms: Language, abstraction, strategy, navigation ("metro map" vibe)
    Failure mode: Over-analysis, detachment, endless branching without landing
    
    In operator terms: Ω (Oscillatory) - phase-preserving, conservative, transport
    """
    
    connectivity: float = field(default=1.0)
    abstraction_level: int = field(default=0)
    
    @property
    def element(self) -> Element:
        return Element.AIR
    
    @property
    def pole(self) -> Pole:
        return Pole.OMEGA
    
    @property
    def core_function(self) -> str:
        return "Structure through relation / mapping / routing — the 'connect the nodes' archetype"
    
    @property
    def pattern_signature(self) -> str:
        return "Builds links, creates models, moves information sideways (comparisons, analogies, coordination)"
    
    @property
    def shadow(self) -> str:
        return "Over-analysis, detachment, endless branching without landing"
    
    def apply(self, state: Any) -> Any:
        """
        Apply Air transformation: phase rotation / structure mapping.
        
        For numeric states, this applies oscillatory/rotational transform.
        """
        if isinstance(state, (int, float)):
            # Phase rotation (conservative transform)
            phase = self.connectivity * math.pi / 4  # 45° base rotation
            return state * math.cos(phase) + self.abstraction_level * math.sin(phase)
        elif isinstance(state, complex):
            # Complex rotation
            phase = self.connectivity * math.pi / 4
            return state * complex(math.cos(phase), math.sin(phase))
        else:
            raise TypeError(f"Cannot apply Air to {type(state)}")
    
    def detect_shadow(self, state: Any) -> bool:
        """
        Detect over-analysis/detachment.
        
        Shadow manifests when:
        - Too many branches (abstraction_level too high)
        - No grounding (detachment from concrete)
        - Circular references (endless analysis)
        """
        return self.abstraction_level > 10  # Arbitrary threshold
    
    def route(self, from_node: Any, to_node: Any) -> Tuple[Any, Any]:
        """Create a connection/route between nodes."""
        return (from_node, to_node)
    
    def abstract(self, concrete: Any) -> Tuple[Any, int]:
        """Lift to higher abstraction level."""
        return (concrete, self.abstraction_level + 1)
    
    def navigate(self, current: float, target: float) -> float:
        """Navigate toward target via phase adjustment."""
        diff = target - current
        step = diff * self.connectivity * 0.1
        return current + step


@dataclass
class Water(Archetype):
    """
    WATER Archetype: Adaptation / Flow / Shaping
    
    Core function: The "let it move and find the path" archetype
    Pattern signature: Minimizes resistance, smooths discontinuities, converges by flow
    System terms: Optimization dynamics, gradients, learning, "become what the system needs"
    Failure mode: Drift, dissolving boundaries, avoiding commitment
    
    In operator terms: Σ (Stochastic) - Markovian expansion, mixing, noise injection
    """
    
    flow_rate: float = field(default=1.0)
    viscosity: float = field(default=0.1)
    temperature: float = field(default=1.0)
    
    @property
    def element(self) -> Element:
        return Element.WATER
    
    @property
    def pole(self) -> Pole:
        return Pole.SIGMA
    
    @property
    def core_function(self) -> str:
        return "Adaptation / flow / shaping — the 'let it move and find the path' archetype"
    
    @property
    def pattern_signature(self) -> str:
        return "Minimizes resistance, smooths discontinuities, converges by flow rather than force"
    
    @property
    def shadow(self) -> str:
        return "Drift, dissolving boundaries, avoiding commitment"
    
    def apply(self, state: Any) -> Any:
        """
        Apply Water transformation: stochastic smoothing/flow.
        
        For numeric states, this applies diffusive averaging.
        """
        if isinstance(state, (int, float)):
            # Diffusive smoothing toward equilibrium (0)
            decay = math.exp(-self.viscosity * self.flow_rate)
            noise = self.temperature * 0.01 * (hash(str(state)) % 100 - 50) / 50
            return state * decay + noise
        else:
            raise TypeError(f"Cannot apply Water to {type(state)}")
    
    def detect_shadow(self, state: Any) -> bool:
        """
        Detect drift/dissolution.
        
        Shadow manifests when:
        - State has diffused too much (lost structure)
        - Boundaries are unclear
        - No commitment to any path
        """
        if isinstance(state, (int, float)):
            # Drift: value is too close to zero (over-diffused)
            return abs(state) < 1e-10 and self.flow_rate > 0
        return False
    
    def flow(self, state: float, gradient: float) -> float:
        """Flow down gradient."""
        return state - self.flow_rate * gradient
    
    def diffuse(self, state: float) -> float:
        """Apply diffusive smoothing."""
        return self.apply(state)
    
    def mix(self, states: List[float]) -> float:
        """Mix multiple states (ensemble average)."""
        if not states:
            return 0.0
        return sum(states) / len(states)
    
    def sample(self, mean: float, std: float) -> float:
        """Sample from distribution (deterministic pseudo-random)."""
        # Deterministic "random" based on inputs
        seed = hash((mean, std, self.temperature))
        u = (seed % 10000) / 10000.0
        # Box-Muller approximation
        return mean + std * math.sqrt(-2 * math.log(max(u, 1e-10))) * math.cos(2 * math.pi * u)


@dataclass
class Earth(Archetype):
    """
    EARTH Archetype: Constraint / Embodiment / Verification
    
    Core function: The "make it real" archetype
    Pattern signature: Enforces bounds, locks invariants, turns plans into stable artifacts
    System terms: Proof, tests, production constraints, compression integrity
    Failure mode: Rigidity, over-constraint, stagnation
    
    In operator terms: Ψ (Recursive) - scale transformation, coarse-graining, renormalization
    """
    
    rigidity: float = field(default=1.0)
    compression: float = field(default=0.5)
    recursion_depth: int = field(default=0)
    
    @property
    def element(self) -> Element:
        return Element.EARTH
    
    @property
    def pole(self) -> Pole:
        return Pole.PSI
    
    @property
    def core_function(self) -> str:
        return "Constraint / embodiment / verification — the 'make it real' archetype"
    
    @property
    def pattern_signature(self) -> str:
        return "Enforces bounds, locks invariants, turns a plan into a stable artifact"
    
    @property
    def shadow(self) -> str:
        return "Rigidity, over-constraint, stagnation"
    
    def apply(self, state: Any) -> Any:
        """
        Apply Earth transformation: constraint enforcement / compression.
        
        For numeric states, this applies bounds clamping and rounding.
        """
        if isinstance(state, (int, float)):
            # Constrain to bounds
            clamped = max(-1e10, min(1e10, state))
            # Quantize/compress
            if self.compression > 0:
                quantum = 10 ** (-int(self.compression * 10))
                clamped = round(clamped / quantum) * quantum
            return clamped
        else:
            raise TypeError(f"Cannot apply Earth to {type(state)}")
    
    def detect_shadow(self, state: Any) -> bool:
        """
        Detect rigidity/stagnation.
        
        Shadow manifests when:
        - State cannot change (over-constrained)
        - Recursion is too deep (infinite regress)
        - System is stuck in local minimum
        """
        return self.recursion_depth > 100 or self.rigidity > 10
    
    def constrain(self, state: float, lower: float, upper: float) -> float:
        """Enforce bounds constraint."""
        return max(lower, min(upper, state))
    
    def verify(self, state: float, predicate: Callable[[float], bool]) -> bool:
        """Verify that state satisfies predicate."""
        return predicate(state)
    
    def lock(self, state: float) -> float:
        """Lock state to nearest stable value."""
        return self.apply(state)
    
    def coarse_grain(self, states: List[float]) -> float:
        """Coarse-grain multiple states into single representative."""
        if not states:
            return 0.0
        # Use median for robustness
        sorted_states = sorted(states)
        n = len(sorted_states)
        if n % 2 == 0:
            return (sorted_states[n//2 - 1] + sorted_states[n//2]) / 2
        else:
            return sorted_states[n//2]
    
    def renormalize(self, state: float, scale: float) -> float:
        """Apply scale transformation (renormalization)."""
        return state * (scale ** self.compression)


# ═══════════════════════════════════════════════════════════════════════════════
# ROTATION ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class RotationEngine:
    """
    Engine for performing 90° rotations between archetypes.
    
    The rotation engine manages transitions between adjacent archetypes
    and provides escape routes when stuck in shadow states.
    """
    
    current: Archetype
    history: List[Archetype] = field(default_factory=list)
    
    def rotate_clockwise(self) -> Archetype:
        """
        Rotate 90° clockwise: Fire → Air → Water → Earth → Fire
        """
        self.history.append(self.current)
        
        rotation = {
            Element.FIRE: Air(),
            Element.AIR: Water(),
            Element.WATER: Earth(),
            Element.EARTH: Fire(),
        }
        
        self.current = rotation[self.current.element]
        return self.current
    
    def rotate_counterclockwise(self) -> Archetype:
        """
        Rotate 90° counter-clockwise: Fire → Earth → Water → Air → Fire
        """
        self.history.append(self.current)
        
        rotation = {
            Element.FIRE: Earth(),
            Element.EARTH: Water(),
            Element.WATER: Air(),
            Element.AIR: Fire(),
        }
        
        self.current = rotation[self.current.element]
        return self.current
    
    def tunnel_to(self, target: Type[Archetype]) -> Optional[Archetype]:
        """
        Attempt to tunnel to a specific archetype.
        
        Returns the new archetype if tunneling is allowed, None otherwise.
        """
        if target in self.current.adjacent:
            self.history.append(self.current)
            self.current = target()
            return self.current
        else:
            return None  # Cannot tunnel to opposite
    
    def escape_shadow(self) -> Tuple[Archetype, str]:
        """
        Escape from current shadow state by rotating to adjacent archetype.
        
        Returns the new archetype and guidance message.
        """
        adj_type, message = self.current.escape_shadow()
        new_arch = self.tunnel_to(adj_type)
        if new_arch:
            return new_arch, message
        else:
            # Try the other adjacent
            adj1, adj2 = self.current.adjacent
            other = adj2 if adj_type == adj1 else adj1
            new_arch = self.tunnel_to(other)
            return new_arch, f"Rotate 90° into {other.__name__} archetype"
    
    def spin_cycle(self, state: Any, steps: int = 4) -> Any:
        """
        Apply a full spin cycle (4 rotations) to state.
        
        This passes state through all four archetypes.
        """
        result = state
        for _ in range(steps):
            result = self.current.apply(result)
            self.rotate_clockwise()
        return result
    
    def reverse_spin_cycle(self, state: Any, steps: int = 4) -> Any:
        """
        Apply a reverse spin cycle (4 counter-rotations) to state.
        """
        result = state
        for _ in range(steps):
            result = self.current.apply(result)
            self.rotate_counterclockwise()
        return result


# ═══════════════════════════════════════════════════════════════════════════════
# ARCHETYPE REGISTRY
# ═══════════════════════════════════════════════════════════════════════════════

ARCHETYPE_MAP: Dict[Element, Type[Archetype]] = {
    Element.FIRE: Fire,
    Element.AIR: Air,
    Element.WATER: Water,
    Element.EARTH: Earth,
}

POLE_TO_ARCHETYPE: Dict[Pole, Type[Archetype]] = {
    Pole.D: Fire,
    Pole.OMEGA: Air,
    Pole.SIGMA: Water,
    Pole.PSI: Earth,
}


def get_archetype(element: Element) -> Archetype:
    """Get an archetype instance by element."""
    return ARCHETYPE_MAP[element]()


def get_archetype_for_pole(pole: Pole) -> Archetype:
    """Get an archetype instance by pole."""
    return POLE_TO_ARCHETYPE[pole]()
