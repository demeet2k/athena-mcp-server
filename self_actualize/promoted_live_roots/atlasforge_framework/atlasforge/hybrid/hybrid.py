"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                       ATLAS FORGE - Hybrid System                             ║
╚══════════════════════════════════════════════════════════════════════════════╝

Hybrid Equations: Continuous Dynamics + Discrete Events

A hybrid system combines:
- Continuous flow (differential equations)
- Discrete jumps (mode switches, resets)
- Guard conditions (when to switch)
- Reset maps (what happens on switch)

Key Patterns:
- RelaxProject: Relax continuously, project discretely
- FlowPrune: Flow continuously, prune branches discretely
- PredictCorrect: Predict continuously, correct discretely
- SpectralCombinatorial: Spectral (Ω) + Combinatorial (Ψ)
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Generic, List, Optional, Tuple, TypeVar
from enum import Enum, auto
import math
import numpy as np
from numpy.typing import NDArray

from atlasforge.core.types import Interval
from atlasforge.core.enums import Pole, FlowType
from atlasforge.poles.generator import Generator, HybridGenerator
from atlasforge.poles.simplex import PoleCoefficients


T = TypeVar('T')


# ═══════════════════════════════════════════════════════════════════════════════
# HYBRID STATE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class HybridState(Generic[T]):
    """
    State of a hybrid system.
    
    Contains:
    - Continuous state x ∈ R^n
    - Discrete mode q ∈ Q (finite set)
    - Time t ∈ R
    """
    
    continuous: T  # Continuous state (can be scalar, vector, etc.)
    mode: int = 0  # Discrete mode index
    time: float = 0.0  # Current time
    
    # History tracking
    jump_count: int = 0
    last_jump_time: float = 0.0
    
    def copy(self) -> 'HybridState[T]':
        """Create a copy of this state."""
        if isinstance(self.continuous, np.ndarray):
            cont = self.continuous.copy()
        else:
            cont = self.continuous
        return HybridState(
            continuous=cont,
            mode=self.mode,
            time=self.time,
            jump_count=self.jump_count,
            last_jump_time=self.last_jump_time,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# FLOW (CONTINUOUS DYNAMICS)
# ═══════════════════════════════════════════════════════════════════════════════

class Flow(ABC, Generic[T]):
    """
    Abstract base class for continuous flows.
    
    A flow defines the continuous dynamics dx/dt = f(x, t, q)
    """
    
    @abstractmethod
    def vector_field(self, x: T, t: float, mode: int = 0) -> T:
        """
        Compute the vector field dx/dt at state x, time t, mode q.
        """
        pass
    
    def integrate(
        self, 
        x0: T, 
        t0: float, 
        t1: float, 
        mode: int = 0,
        dt: float = 0.01
    ) -> T:
        """
        Integrate the flow from t0 to t1.
        
        Default implementation uses RK4.
        """
        x = x0
        t = t0
        h = dt
        
        while t < t1:
            if t + h > t1:
                h = t1 - t
            
            k1 = self.vector_field(x, t, mode)
            k2 = self.vector_field(self._add(x, self._scale(h/2, k1)), t + h/2, mode)
            k3 = self.vector_field(self._add(x, self._scale(h/2, k2)), t + h/2, mode)
            k4 = self.vector_field(self._add(x, self._scale(h, k3)), t + h, mode)
            
            dx = self._scale(h/6, self._add(k1, self._add(self._scale(2, k2), 
                                             self._add(self._scale(2, k3), k4))))
            x = self._add(x, dx)
            t += h
        
        return x
    
    def _add(self, a: T, b: T) -> T:
        """Add two states (override for non-standard types)."""
        if isinstance(a, np.ndarray):
            return a + b
        return a + b
    
    def _scale(self, s: float, x: T) -> T:
        """Scale a state (override for non-standard types)."""
        if isinstance(x, np.ndarray):
            return s * x
        return s * x


@dataclass
class LinearFlow(Flow[float]):
    """Linear flow: dx/dt = a*x + b"""
    
    a: float = -1.0
    b: float = 0.0
    
    def vector_field(self, x: float, t: float, mode: int = 0) -> float:
        return self.a * x + self.b
    
    def integrate(self, x0: float, t0: float, t1: float, mode: int = 0, dt: float = 0.01) -> float:
        """Exact solution for linear ODE."""
        dt_total = t1 - t0
        if abs(self.a) < 1e-15:
            return x0 + self.b * dt_total
        return (x0 + self.b/self.a) * math.exp(self.a * dt_total) - self.b/self.a


@dataclass
class GradientFlow(Flow[NDArray[np.float64]]):
    """Gradient flow: dx/dt = -∇V(x)"""
    
    potential: Callable[[NDArray], float] = field(default=lambda x: 0.5 * np.sum(x**2))
    eps: float = 1e-6  # For numerical gradient
    
    def vector_field(self, x: NDArray, t: float, mode: int = 0) -> NDArray:
        """Compute -∇V(x) numerically."""
        grad = np.zeros_like(x)
        for i in range(len(x)):
            x_plus = x.copy()
            x_plus[i] += self.eps
            x_minus = x.copy()
            x_minus[i] -= self.eps
            grad[i] = (self.potential(x_plus) - self.potential(x_minus)) / (2 * self.eps)
        return -grad


@dataclass
class GeneratorFlow(Flow[NDArray[np.float64]]):
    """Flow generated by a Generator."""
    
    generator: Generator = field(default_factory=lambda: None)
    
    def vector_field(self, x: NDArray, t: float, mode: int = 0) -> NDArray:
        return self.generator(x)


# ═══════════════════════════════════════════════════════════════════════════════
# GUARD AND RESET
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Guard(Generic[T]):
    """
    Guard condition for mode transitions.
    
    A guard is a predicate G(x, t, q) that triggers when true.
    """
    
    predicate: Callable[[T, float, int], bool]
    source_mode: int = 0
    target_mode: int = 1
    name: str = "guard"
    
    def is_active(self, x: T, t: float, mode: int) -> bool:
        """Check if guard is active at current state."""
        if mode != self.source_mode:
            return False
        return self.predicate(x, t, mode)


@dataclass
class Reset(Generic[T]):
    """
    Reset map for mode transitions.
    
    A reset R(x, t) defines the new continuous state after a jump.
    """
    
    map_fn: Callable[[T, float], T]
    name: str = "reset"
    
    def apply(self, x: T, t: float) -> T:
        """Apply the reset map."""
        return self.map_fn(x, t)


@dataclass
class Transition(Generic[T]):
    """
    A complete transition = Guard + Reset.
    """
    
    guard: Guard[T]
    reset: Reset[T]
    priority: int = 0  # Higher priority transitions are checked first
    
    @property
    def source_mode(self) -> int:
        return self.guard.source_mode
    
    @property
    def target_mode(self) -> int:
        return self.guard.target_mode


# ═══════════════════════════════════════════════════════════════════════════════
# HYBRID SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class HybridSystem(Generic[T]):
    """
    A complete hybrid dynamical system.
    
    Components:
    - Flows: One per mode (or shared)
    - Transitions: Guard + Reset pairs
    - Modes: Discrete state space
    """
    
    flows: Dict[int, Flow[T]] = field(default_factory=dict)
    transitions: List[Transition[T]] = field(default_factory=list)
    num_modes: int = 1
    default_flow: Optional[Flow[T]] = None
    
    def get_flow(self, mode: int) -> Flow[T]:
        """Get the flow for a given mode."""
        if mode in self.flows:
            return self.flows[mode]
        if self.default_flow is not None:
            return self.default_flow
        raise ValueError(f"No flow defined for mode {mode}")
    
    def check_transitions(self, state: HybridState[T]) -> Optional[Transition[T]]:
        """
        Check if any transition is triggered.
        
        Returns the highest-priority active transition, or None.
        """
        active = []
        for trans in self.transitions:
            if trans.guard.is_active(state.continuous, state.time, state.mode):
                active.append(trans)
        
        if not active:
            return None
        
        # Return highest priority
        return max(active, key=lambda t: t.priority)
    
    def step(
        self, 
        state: HybridState[T], 
        dt: float,
        max_jumps: int = 10
    ) -> Tuple[HybridState[T], bool]:
        """
        Take one step of the hybrid system.
        
        Returns (new_state, jumped).
        """
        new_state = state.copy()
        jumped = False
        
        # Check for immediate transitions (Zeno protection)
        jumps_this_step = 0
        while jumps_this_step < max_jumps:
            trans = self.check_transitions(new_state)
            if trans is None:
                break
            
            # Apply transition
            new_state.continuous = trans.reset.apply(new_state.continuous, new_state.time)
            new_state.mode = trans.target_mode
            new_state.jump_count += 1
            new_state.last_jump_time = new_state.time
            jumped = True
            jumps_this_step += 1
        
        # Continuous evolution
        flow = self.get_flow(new_state.mode)
        new_state.continuous = flow.integrate(
            new_state.continuous,
            new_state.time,
            new_state.time + dt,
            new_state.mode
        )
        new_state.time += dt
        
        return new_state, jumped
    
    def simulate(
        self,
        initial: HybridState[T],
        duration: float,
        dt: float = 0.01
    ) -> List[HybridState[T]]:
        """
        Simulate the hybrid system.
        
        Returns trajectory as list of states.
        """
        trajectory = [initial.copy()]
        state = initial.copy()
        
        while state.time < initial.time + duration:
            state, _ = self.step(state, dt)
            trajectory.append(state.copy())
        
        return trajectory


# ═══════════════════════════════════════════════════════════════════════════════
# HYBRID PATTERNS
# ═══════════════════════════════════════════════════════════════════════════════

class RelaxProjectPattern:
    """
    Relax-Project Pattern: D-Ψ axis.
    
    Mode 0: Relax (continuous dissipation, D pole)
    Mode 1: Project (discrete constraint enforcement, Ψ pole)
    
    Used for optimization with constraints.
    """
    
    @staticmethod
    def create(
        relax_rate: float = 1.0,
        project_fn: Callable[[NDArray], NDArray] = lambda x: x,
        switch_threshold: float = 0.01
    ) -> HybridSystem[NDArray]:
        """Create a Relax-Project hybrid system."""
        
        # Relaxation flow (gradient descent)
        relax_flow = LinearFlow(a=-relax_rate)
        
        # Identity flow in projection mode (instantaneous)
        project_flow = LinearFlow(a=0)
        
        # Guard: switch to project when gradient is small
        guard_to_project = Guard(
            predicate=lambda x, t, m: abs(x) < switch_threshold if isinstance(x, (int, float)) else np.linalg.norm(x) < switch_threshold,
            source_mode=0,
            target_mode=1,
            name="to_project"
        )
        
        # Guard: switch back to relax after projection
        guard_to_relax = Guard(
            predicate=lambda x, t, m: True,  # Always switch back
            source_mode=1,
            target_mode=0,
            name="to_relax"
        )
        
        # Reset: apply projection
        reset_project = Reset(
            map_fn=lambda x, t: project_fn(x),
            name="project"
        )
        
        # Reset: identity for relax
        reset_relax = Reset(
            map_fn=lambda x, t: x,
            name="identity"
        )
        
        return HybridSystem(
            flows={0: relax_flow, 1: project_flow},
            transitions=[
                Transition(guard_to_project, reset_project, priority=1),
                Transition(guard_to_relax, reset_relax, priority=0),
            ],
            num_modes=2,
        )


class FlowPrunePattern:
    """
    Flow-Prune Pattern: Ω-Ψ axis.
    
    Mode 0: Flow (continuous oscillation/exploration, Ω pole)
    Mode 1: Prune (discrete elimination of branches, Ψ pole)
    
    Used for branch-and-bound type algorithms.
    """
    
    @staticmethod
    def create(
        flow_generator: Optional[Generator] = None,
        prune_fn: Callable[[NDArray], NDArray] = lambda x: x,
        prune_period: float = 1.0
    ) -> HybridSystem[NDArray]:
        """Create a Flow-Prune hybrid system."""
        
        # Create simple oscillatory flow if not provided
        if flow_generator is None:
            flow = LinearFlow(a=0, b=1)  # Constant velocity
        else:
            flow = GeneratorFlow(generator=flow_generator)
        
        # Guard: prune periodically
        guard_to_prune = Guard(
            predicate=lambda x, t, m: (t % prune_period) < 0.01,
            source_mode=0,
            target_mode=1,
            name="to_prune"
        )
        
        guard_to_flow = Guard(
            predicate=lambda x, t, m: True,
            source_mode=1,
            target_mode=0,
            name="to_flow"
        )
        
        reset_prune = Reset(map_fn=lambda x, t: prune_fn(x), name="prune")
        reset_identity = Reset(map_fn=lambda x, t: x, name="identity")
        
        return HybridSystem(
            flows={0: flow, 1: LinearFlow(a=0)},
            transitions=[
                Transition(guard_to_prune, reset_prune, priority=1),
                Transition(guard_to_flow, reset_identity, priority=0),
            ],
            num_modes=2,
        )


class PredictCorrectPattern:
    """
    Predict-Correct Pattern: D-Σ axis.
    
    Mode 0: Predict (continuous extrapolation, D pole)
    Mode 1: Correct (stochastic update, Σ pole)
    
    Used for filtering and estimation.
    """
    
    @staticmethod
    def create(
        predict_rate: float = 1.0,
        correct_fn: Callable[[NDArray, float], NDArray] = lambda x, t: x,
        measurement_period: float = 0.1
    ) -> HybridSystem[NDArray]:
        """Create a Predict-Correct hybrid system."""
        
        predict_flow = LinearFlow(a=predict_rate)
        correct_flow = LinearFlow(a=0)
        
        guard_to_correct = Guard(
            predicate=lambda x, t, m: (t % measurement_period) < 0.01,
            source_mode=0,
            target_mode=1,
            name="to_correct"
        )
        
        guard_to_predict = Guard(
            predicate=lambda x, t, m: True,
            source_mode=1,
            target_mode=0,
            name="to_predict"
        )
        
        reset_correct = Reset(map_fn=correct_fn, name="correct")
        reset_identity = Reset(map_fn=lambda x, t: x, name="identity")
        
        return HybridSystem(
            flows={0: predict_flow, 1: correct_flow},
            transitions=[
                Transition(guard_to_correct, reset_correct, priority=1),
                Transition(guard_to_predict, reset_identity, priority=0),
            ],
            num_modes=2,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# HYBRID EQUATION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class HybridEquation:
    """
    A hybrid equation to be solved.
    
    Combines:
    - Continuous dynamics (flow)
    - Discrete events (guards + resets)
    - Target condition (what we're solving for)
    """
    
    system: HybridSystem
    
    # Target condition
    target: Callable[[HybridState], float] = field(default=lambda s: s.continuous)
    target_value: float = 0.0
    
    # Solve parameters
    max_time: float = 100.0
    tolerance: float = 1e-10
    
    def residual(self, state: HybridState) -> float:
        """Compute residual from target."""
        return abs(self.target(state) - self.target_value)
    
    def is_satisfied(self, state: HybridState) -> bool:
        """Check if target is reached."""
        return self.residual(state) < self.tolerance
