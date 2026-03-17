"""
ATHENA OS - NORSE: WYRD MODULE
===============================
Non-Markovian Dynamics and the History Integral

THE WYRD EQUATION:
    dS/dt = L[S(t)] + ∫_{t0}^{t} K(t, τ) · S(τ) dτ
    
    Where:
    - L[S(t)]: Local dynamics (current actions)
    - K(t, τ): Memory Kernel (Web of Urd)
    - The integral: Accumulated historical weight

REJECTION OF MARKOV PROPERTY:
    Standard: P(X_{t+1} | X_t, ..., X_0) = P(X_{t+1} | X_t)
    Norse: S_{t+1} = f(S_t, ∫_{0}^{t} H(τ) dτ)
    
    The future depends on the ENTIRE HISTORY, not just current state.

THE NORN OPERATORS:
    Urd (Past): Fixes lower bound, makes history READ-ONLY
    Verdandi (Present): Delta function δ(t-τ), immediate insertion
    Skuld (Necessity): Projection operator for required trajectory

THE WEB OF URD:
    Visual representation of the History Tensor.
    Stores accumulated vectors of past actions.
    Once woven, threads CANNOT be unwoven.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Callable, Any, Union
from enum import Enum, auto
import numpy as np
from collections import deque


# =============================================================================
# HISTORY EVENT
# =============================================================================

@dataclass
class HistoryEvent:
    """
    A single event in the history record.
    
    Once created, becomes immutable (cannot be unwoven).
    """
    
    timestamp: float
    action: str
    magnitude: float
    source: str
    
    # Decay parameters
    decay_rate: float = 0.01
    
    # Links to other events
    causes: List[int] = field(default_factory=list)
    effects: List[int] = field(default_factory=list)
    
    # Immutable flag
    _locked: bool = False
    
    def lock(self) -> None:
        """Lock the event (make immutable)."""
        self._locked = True
    
    def get_weight(self, current_time: float) -> float:
        """
        Get current weight of this event.
        
        Weight decays over time but never reaches zero.
        """
        age = current_time - self.timestamp
        decay = np.exp(-self.decay_rate * age)
        return self.magnitude * decay * 0.5 + self.magnitude * 0.5
    
    @property
    def is_locked(self) -> bool:
        return self._locked


# =============================================================================
# MEMORY KERNEL (WEB OF URD)
# =============================================================================

class WebOfUrd:
    """
    The Memory Kernel K(t, τ).
    
    Encodes the weight/relevance of past events on current moment.
    This is the "Web" woven by the Norns.
    """
    
    def __init__(self, max_events: int = 10000):
        self.max_events = max_events
        
        # Event storage
        self._events: List[HistoryEvent] = []
        self._event_index: Dict[str, List[int]] = {}
        
        # Current time
        self._current_time = 0.0
        
        # Total accumulated weight
        self._total_weight = 0.0
    
    def weave_thread(self, action: str, magnitude: float, 
                    source: str, causes: List[int] = None) -> int:
        """
        Weave a new thread into the web.
        
        Returns the event index.
        """
        event = HistoryEvent(
            timestamp=self._current_time,
            action=action,
            magnitude=magnitude,
            source=source,
            causes=causes or []
        )
        
        idx = len(self._events)
        self._events.append(event)
        
        # Index by action type
        if action not in self._event_index:
            self._event_index[action] = []
        self._event_index[action].append(idx)
        
        # Update causal links
        for cause_idx in event.causes:
            if 0 <= cause_idx < len(self._events):
                self._events[cause_idx].effects.append(idx)
        
        self._total_weight += magnitude
        
        return idx
    
    def lock_past(self, cutoff_time: float) -> int:
        """
        Lock all events before cutoff time (Urd's function).
        
        Returns number of events locked.
        """
        locked_count = 0
        for event in self._events:
            if event.timestamp < cutoff_time and not event.is_locked:
                event.lock()
                locked_count += 1
        
        return locked_count
    
    def compute_kernel(self, query_time: float, 
                      action_filter: Optional[str] = None) -> float:
        """
        Compute the kernel integral at query_time.
        
        This is ∫_{t0}^{t} K(t, τ) dτ
        """
        total = 0.0
        
        for event in self._events:
            if event.timestamp > query_time:
                continue
            
            if action_filter and event.action != action_filter:
                continue
            
            total += event.get_weight(query_time)
        
        return total
    
    def get_thread_tension(self, action: str) -> float:
        """
        Get the accumulated tension for a type of action.
        
        Higher tension = stronger influence on future.
        """
        if action not in self._event_index:
            return 0.0
        
        total = 0.0
        for idx in self._event_index[action]:
            total += self._events[idx].get_weight(self._current_time)
        
        return total
    
    def advance_time(self, dt: float) -> None:
        """Advance web time."""
        self._current_time += dt
    
    def get_causal_chain(self, event_idx: int, 
                        depth: int = 10) -> List[int]:
        """
        Trace causal chain backwards from an event.
        
        Returns list of event indices.
        """
        if event_idx < 0 or event_idx >= len(self._events):
            return []
        
        chain = [event_idx]
        current = event_idx
        
        for _ in range(depth):
            event = self._events[current]
            if not event.causes:
                break
            
            # Follow first cause
            current = event.causes[0]
            chain.append(current)
        
        return list(reversed(chain))
    
    @property
    def n_events(self) -> int:
        return len(self._events)
    
    @property
    def total_weight(self) -> float:
        return self._total_weight
    
    @property
    def current_time(self) -> float:
        return self._current_time


# =============================================================================
# NORN OPERATORS
# =============================================================================

class NornOperator(Enum):
    """The three Norn operators."""
    
    URD = "urd"           # Past - locks history
    VERDANDI = "verdandi" # Present - immediate insertion
    SKULD = "skuld"       # Necessity - projection


@dataclass
class Norn:
    """
    A Norn operator acting on the Web of Urd.
    
    Norns are not entities but operators that update the Memory Kernel.
    """
    
    name: str
    operator_type: NornOperator
    
    def apply(self, web: WebOfUrd, 
             state: 'WyrdState', 
             **kwargs) -> Any:
        """Apply this Norn's operation."""
        if self.operator_type == NornOperator.URD:
            return self._apply_urd(web, state, **kwargs)
        elif self.operator_type == NornOperator.VERDANDI:
            return self._apply_verdandi(web, state, **kwargs)
        elif self.operator_type == NornOperator.SKULD:
            return self._apply_skuld(web, state, **kwargs)
    
    def _apply_urd(self, web: WebOfUrd, 
                   state: 'WyrdState', **kwargs) -> int:
        """
        Urd: Fix the past, make it read-only.
        
        Sets lower bound of integral, solidifies history.
        """
        cutoff = kwargs.get('cutoff', web.current_time - 1.0)
        return web.lock_past(cutoff)
    
    def _apply_verdandi(self, web: WebOfUrd,
                        state: 'WyrdState', **kwargs) -> int:
        """
        Verdandi: Insert new event into present moment.
        
        Acts as delta function δ(t-τ).
        """
        action = kwargs.get('action', 'unknown')
        magnitude = kwargs.get('magnitude', 1.0)
        source = kwargs.get('source', 'unknown')
        causes = kwargs.get('causes', [])
        
        return web.weave_thread(action, magnitude, source, causes)
    
    def _apply_skuld(self, web: WebOfUrd,
                     state: 'WyrdState', **kwargs) -> np.ndarray:
        """
        Skuld: Project required future trajectory.
        
        Calculates necessary S(t+Δt) based on history.
        """
        horizon = kwargs.get('horizon', 10.0)
        
        # Compute projection based on accumulated weight
        history_weight = web.compute_kernel(web.current_time)
        
        # Future state is constrained by past
        # As history grows, future becomes more determined
        determinism = 1.0 - np.exp(-history_weight / 100)
        
        # Project trajectory
        projected = state.vector * (1 + determinism * 0.1)
        
        return projected


# Create the three Norns
URD = Norn("Urd", NornOperator.URD)
VERDANDI = Norn("Verdandi", NornOperator.VERDANDI)
SKULD = Norn("Skuld", NornOperator.SKULD)


# =============================================================================
# WYRD STATE
# =============================================================================

@dataclass
class WyrdState:
    """
    The state vector S(t) governed by Wyrd.
    
    Evolution follows the non-Markovian Wyrd equation.
    """
    
    dimension: int
    
    # State vector
    vector: np.ndarray = field(init=False)
    
    # Local dynamics coefficient
    local_rate: float = 0.1
    
    # History integral coefficient
    history_rate: float = 0.05
    
    def __post_init__(self):
        self.vector = np.zeros(self.dimension)
    
    def set_initial(self, initial: np.ndarray) -> None:
        """Set initial state."""
        if len(initial) == self.dimension:
            self.vector = initial.copy()
    
    def local_dynamics(self) -> np.ndarray:
        """
        Compute local dynamics L[S(t)].
        
        This is the Markovian part (current choices).
        """
        # Simple decay + noise
        decay = -self.local_rate * self.vector
        noise = np.random.randn(self.dimension) * 0.01
        return decay + noise
    
    def history_contribution(self, history_integral: float) -> np.ndarray:
        """
        Compute history contribution to evolution.
        
        This is the non-Markovian part.
        """
        # History pulls toward accumulated pattern
        direction = np.sign(self.vector + 0.001)
        return self.history_rate * history_integral * direction
    
    def evolve(self, dt: float, history_integral: float) -> None:
        """
        Evolve state according to Wyrd equation.
        
        dS/dt = L[S(t)] + ∫K(t,τ)·S(τ)dτ
        """
        dS = self.local_dynamics() + self.history_contribution(history_integral)
        self.vector += dS * dt
    
    @property
    def magnitude(self) -> float:
        return float(np.linalg.norm(self.vector))


# =============================================================================
# WYRD SYSTEM
# =============================================================================

class WyrdSystem:
    """
    The Complete Wyrd Dynamics System.
    
    Manages non-Markovian state evolution with history integral.
    """
    
    def __init__(self, state_dimension: int = 16):
        # Core components
        self.web = WebOfUrd()
        self.state = WyrdState(dimension=state_dimension)
        
        # Norns
        self.urd = URD
        self.verdandi = VERDANDI
        self.skuld = SKULD
        
        # Simulation state
        self._time = 0.0
    
    def record_action(self, action: str, magnitude: float,
                     source: str, causes: List[int] = None) -> int:
        """
        Record an action in the web.
        
        Uses Verdandi operator.
        """
        return self.verdandi.apply(
            self.web, self.state,
            action=action,
            magnitude=magnitude,
            source=source,
            causes=causes
        )
    
    def lock_history(self, age: float = 1.0) -> int:
        """
        Lock old history.
        
        Uses Urd operator.
        """
        cutoff = self._time - age
        return self.urd.apply(self.web, self.state, cutoff=cutoff)
    
    def project_future(self, horizon: float = 10.0) -> np.ndarray:
        """
        Project future state.
        
        Uses Skuld operator.
        """
        return self.skuld.apply(
            self.web, self.state,
            horizon=horizon
        )
    
    def compute_wyrd_path(self, action_vector: np.ndarray,
                         history_tensor: Optional[np.ndarray] = None) -> Dict:
        """
        The calculate_wyrd_path() system call.
        
        Computes the tension on the Web generated by action
        relative to historical context.
        """
        # Compute history integral
        history_integral = self.web.compute_kernel(self._time)
        
        # Compute tension (conflict with history)
        if history_tensor is not None:
            tension = np.linalg.norm(action_vector - history_tensor.mean(axis=0))
        else:
            tension = np.linalg.norm(action_vector) * history_integral
        
        # Probability distribution weighted by history
        # Higher history = more constrained future
        freedom = np.exp(-history_integral / 100)
        determinism = 1 - freedom
        
        return {
            "history_weight": history_integral,
            "tension": tension,
            "freedom": freedom,
            "determinism": determinism,
            "projected_state": self.project_future()
        }
    
    def tick(self, dt: float = 1.0) -> Dict:
        """
        Advance the system by dt.
        
        Returns evolution statistics.
        """
        # Compute history integral
        history_integral = self.web.compute_kernel(self._time)
        
        # Evolve state
        old_magnitude = self.state.magnitude
        self.state.evolve(dt, history_integral)
        new_magnitude = self.state.magnitude
        
        # Advance web time
        self.web.advance_time(dt)
        self._time += dt
        
        # Lock old history (Urd's continual work)
        self.lock_history(age=10.0)
        
        return {
            "time": self._time,
            "history_weight": history_integral,
            "state_change": new_magnitude - old_magnitude,
            "n_events": self.web.n_events
        }
    
    def get_fatalism_index(self) -> float:
        """
        Compute the fatalism index.
        
        As time increases, history dominates choice.
        Higher index = more determined future.
        """
        history_weight = self.web.compute_kernel(self._time)
        local_weight = self.state.magnitude
        
        if local_weight + history_weight == 0:
            return 0.0
        
        return history_weight / (local_weight + history_weight)
    
    @property
    def time(self) -> float:
        return self._time


# =============================================================================
# VALIDATION
# =============================================================================

def validate_wyrd() -> bool:
    """Validate Norse wyrd module."""
    
    # Test HistoryEvent
    event = HistoryEvent(
        timestamp=0.0,
        action="test",
        magnitude=1.0,
        source="validator"
    )
    
    assert not event.is_locked
    event.lock()
    assert event.is_locked
    
    weight_0 = event.get_weight(0.0)
    weight_10 = event.get_weight(10.0)
    assert weight_10 < weight_0  # Decays over time
    assert weight_10 > 0  # Never reaches zero
    
    # Test WebOfUrd
    web = WebOfUrd()
    
    idx1 = web.weave_thread("action1", 1.0, "source1")
    assert idx1 == 0
    assert web.n_events == 1
    
    web.advance_time(1.0)
    idx2 = web.weave_thread("action2", 2.0, "source2", causes=[idx1])
    
    assert web.n_events == 2
    assert idx1 in web._events[idx2].causes
    assert idx2 in web._events[idx1].effects
    
    # Test kernel computation
    kernel = web.compute_kernel(web.current_time)
    assert kernel > 0
    
    # Test thread tension
    tension = web.get_thread_tension("action1")
    assert tension > 0
    
    # Test causal chain
    chain = web.get_causal_chain(idx2)
    assert idx1 in chain
    assert idx2 in chain
    
    # Test lock past
    locked = web.lock_past(0.5)
    assert locked == 1  # Only first event
    
    # Test Norn operators
    web2 = WebOfUrd()
    state = WyrdState(dimension=8)
    
    # Verdandi - insert
    idx = VERDANDI.apply(web2, state, action="test", magnitude=1.0, source="norn")
    assert web2.n_events == 1
    
    # Urd - lock
    web2.advance_time(1.0)
    VERDANDI.apply(web2, state, action="test2", magnitude=1.0, source="norn")
    locked = URD.apply(web2, state, cutoff=0.5)
    assert locked == 1
    
    # Skuld - project
    projected = SKULD.apply(web2, state, horizon=10.0)
    assert len(projected) == 8
    
    # Test WyrdState
    state2 = WyrdState(dimension=4)
    state2.set_initial(np.array([1.0, 0.0, -1.0, 0.5]))
    
    local = state2.local_dynamics()
    assert len(local) == 4
    
    hist = state2.history_contribution(10.0)
    assert len(hist) == 4
    
    old_vec = state2.vector.copy()
    state2.evolve(1.0, 10.0)
    assert not np.allclose(state2.vector, old_vec)
    
    # Test WyrdSystem
    system = WyrdSystem(state_dimension=8)
    
    idx = system.record_action("test_action", 1.5, "test_source")
    assert system.web.n_events == 1
    
    # Run simulation
    for i in range(10):
        system.record_action(f"action_{i}", float(i % 3), "sim")
        stats = system.tick(1.0)
    
    assert system.time == 10.0
    
    # Test wyrd path
    action_vec = np.random.randn(8)
    path_result = system.compute_wyrd_path(action_vec)
    
    assert "history_weight" in path_result
    assert "tension" in path_result
    assert "freedom" in path_result
    assert "determinism" in path_result
    assert path_result["freedom"] + path_result["determinism"] <= 1.01
    
    # Test fatalism index
    fatalism = system.get_fatalism_index()
    assert 0 <= fatalism <= 1
    
    return True


if __name__ == "__main__":
    print("Validating Norse Wyrd Module...")
    assert validate_wyrd()
    print("✓ Norse Wyrd Module validated")
