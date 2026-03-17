"""
ATHENA OS - KERNEL: COMPLEX ADAPTIVE SYSTEMS
=============================================
Dynamic Equilibrium and Adaptive Architecture

THE PARADIGM SHIFT:
    Legacy (Uranian): Static Equilibrium - Rigid, brittle, resists change
    Olympian (Zeusian): Dynamic Equilibrium - Fluid, adaptive, metabolizes change

STATIC vs DYNAMIC EQUILIBRIUM:
    Static: System returns to single fixed state after perturbation
    Dynamic: System maintains stability through continuous adaptation
    
    The shift is from "resist change" to "process change"

COMPLEX ADAPTIVE SYSTEMS (CAS):
    - Many interacting agents
    - Nonlinear dynamics
    - Emergence of macro-patterns
    - Self-organization
    - Adaptation to environment
    - Edge of chaos operation

ATTRACTOR DYNAMICS:
    Point Attractor: Single stable state (static)
    Limit Cycle: Periodic oscillation
    Strange Attractor: Chaotic but bounded (dynamic equilibrium)

FEEDBACK LOOPS:
    Negative Feedback: Stabilizing, error-correcting
    Positive Feedback: Amplifying, growth-driving
    
    Balance of both maintains edge of chaos

ADAPTATION MECHANISMS:
    1. Parameter Tuning - Adjust internal variables
    2. Structural Reconfiguration - Change topology
    3. Rule Modification - Update behavioral rules
    4. Boundary Adjustment - Modify system scope

SOURCES:
    - ATHENA-KERNEL_SELF-OPTIMIZATION.docx Chapter 7
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Set, Tuple
from enum import Enum
import numpy as np
import math
from abc import ABC, abstractmethod


# =============================================================================
# EQUILIBRIUM TYPES
# =============================================================================

class EquilibriumType(Enum):
    """Types of equilibrium states."""
    
    STATIC = "static"           # Fixed point, resists change
    DYNAMIC = "dynamic"         # Continuous adaptation
    CHAOTIC = "chaotic"         # Bounded chaos
    EDGE_OF_CHAOS = "edge"      # Optimal complexity


class AttractorType(Enum):
    """Types of dynamical attractors."""
    
    POINT = "point"             # Single fixed state
    LIMIT_CYCLE = "limit_cycle"  # Periodic orbit
    STRANGE = "strange"         # Chaotic attractor
    NONE = "none"               # No attractor (divergent)


# =============================================================================
# AGENT
# =============================================================================

@dataclass
class Agent:
    """
    An agent in the complex adaptive system.
    
    Agents interact, adapt, and contribute to emergent behavior.
    """
    
    id: str
    state: np.ndarray = field(default_factory=lambda: np.zeros(4))
    
    # Agent properties
    adaptability: float = 0.5    # Rate of adaptation
    connectivity: int = 0        # Number of connections
    fitness: float = 0.5         # Current fitness
    
    # Behavioral parameters
    parameters: Dict[str, float] = field(default_factory=dict)
    
    # Rules
    rules: List[Callable] = field(default_factory=list)
    
    @property
    def energy(self) -> float:
        """Agent energy (state magnitude)."""
        return float(np.linalg.norm(self.state))
    
    def update_state(self, delta: np.ndarray, 
                    learning_rate: float = 0.1) -> None:
        """Update agent state."""
        self.state = self.state + learning_rate * delta
    
    def adapt(self, environment: Dict[str, Any]) -> None:
        """Adapt to environment."""
        # Simple adaptation: adjust parameters toward environment
        for key, target in environment.items():
            if key in self.parameters:
                current = self.parameters[key]
                self.parameters[key] = (
                    current + self.adaptability * (target - current)
                )
    
    def interact(self, other: Agent) -> Tuple[np.ndarray, np.ndarray]:
        """
        Interact with another agent.
        
        Returns (self_influence, other_influence).
        """
        # Simple coupling: states influence each other
        diff = other.state - self.state
        coupling = 0.1
        
        self_influence = coupling * diff
        other_influence = -coupling * diff
        
        return (self_influence, other_influence)
    
    def evaluate_fitness(self, target: np.ndarray) -> float:
        """Evaluate fitness relative to target."""
        distance = np.linalg.norm(self.state - target)
        self.fitness = 1.0 / (1.0 + distance)
        return self.fitness


# =============================================================================
# FEEDBACK LOOP
# =============================================================================

@dataclass
class FeedbackLoop:
    """
    A feedback loop in the system.
    
    Negative: Stabilizing, error-correcting
    Positive: Amplifying, growth-driving
    """
    
    name: str
    loop_type: str  # "positive" or "negative"
    gain: float = 1.0
    delay: float = 0.0
    
    # Components in the loop
    components: List[str] = field(default_factory=list)
    
    # State
    current_value: float = 0.0
    history: List[float] = field(default_factory=list)
    
    @property
    def is_stabilizing(self) -> bool:
        """Check if loop is stabilizing (negative feedback)."""
        return self.loop_type == "negative"
    
    @property
    def is_amplifying(self) -> bool:
        """Check if loop is amplifying (positive feedback)."""
        return self.loop_type == "positive"
    
    def process(self, input_signal: float) -> float:
        """
        Process signal through feedback loop.
        """
        # Apply gain
        output = input_signal * self.gain
        
        # Apply feedback type
        if self.is_stabilizing:
            # Negative feedback reduces deviation
            output = -output
        
        # Update history
        self.history.append(output)
        if len(self.history) > 100:
            self.history = self.history[-50:]
        
        self.current_value = output
        return output
    
    def get_trend(self, window: int = 10) -> float:
        """Get recent trend in feedback values."""
        if len(self.history) < 2:
            return 0.0
        
        recent = self.history[-min(window, len(self.history)):]
        if len(recent) < 2:
            return 0.0
        
        return (recent[-1] - recent[0]) / len(recent)


# =============================================================================
# ATTRACTOR
# =============================================================================

class Attractor:
    """
    A dynamical attractor.
    """
    
    def __init__(self, attractor_type: AttractorType, 
                 center: np.ndarray = None,
                 strength: float = 1.0):
        """
        Initialize attractor.
        
        attractor_type: Type of attractor
        center: Attractor center (for point attractors)
        strength: Attraction strength
        """
        self.attractor_type = attractor_type
        self.center = center if center is not None else np.zeros(4)
        self.strength = strength
        
        # For limit cycles
        self.frequency = 0.1
        self.radius = 1.0
        
        # For strange attractors
        self.lyapunov_exponent = 0.1
    
    def attract(self, state: np.ndarray, dt: float = 0.1) -> np.ndarray:
        """
        Calculate attraction force on state.
        
        Returns force vector.
        """
        if self.attractor_type == AttractorType.POINT:
            # Simple attraction to center
            direction = self.center - state
            return self.strength * direction * dt
        
        elif self.attractor_type == AttractorType.LIMIT_CYCLE:
            # Attract to circular orbit
            # Get radial and tangential components
            r = np.linalg.norm(state[:2]) if len(state) >= 2 else 0
            if r == 0:
                return np.zeros_like(state)
            
            radial = state[:2] / r
            tangent = np.array([-radial[1], radial[0]])
            
            # Radial force toward desired radius
            radial_force = self.strength * (self.radius - r) * radial
            
            # Tangential force for rotation
            tangent_force = self.frequency * tangent
            
            force = np.zeros_like(state)
            force[:2] = radial_force + tangent_force
            return force * dt
        
        elif self.attractor_type == AttractorType.STRANGE:
            # Simplified strange attractor (Lorenz-like)
            # Chaotic but bounded motion
            if len(state) >= 3:
                # Lorenz-inspired dynamics
                sigma, rho, beta = 10, 28, 8/3
                x, y, z = state[0], state[1], state[2]
                
                dx = sigma * (y - x)
                dy = x * (rho - z) - y
                dz = x * y - beta * z
                
                force = np.zeros_like(state)
                force[0] = dx * 0.01
                force[1] = dy * 0.01
                force[2] = dz * 0.01
                return force * dt
            else:
                return np.zeros_like(state)
        
        return np.zeros_like(state)
    
    def classify_state(self, state: np.ndarray) -> str:
        """Classify state relative to attractor."""
        if self.attractor_type == AttractorType.POINT:
            dist = np.linalg.norm(state - self.center)
            if dist < 0.1:
                return "at_attractor"
            elif dist < 1.0:
                return "near_attractor"
            else:
                return "far_from_attractor"
        
        elif self.attractor_type == AttractorType.LIMIT_CYCLE:
            r = np.linalg.norm(state[:2]) if len(state) >= 2 else 0
            if abs(r - self.radius) < 0.1:
                return "on_cycle"
            else:
                return "off_cycle"
        
        return "in_basin"


# =============================================================================
# COMPLEX ADAPTIVE SYSTEM
# =============================================================================

class ComplexAdaptiveSystem:
    """
    A Complex Adaptive System (CAS).
    
    Features:
    - Multiple interacting agents
    - Nonlinear dynamics
    - Emergence and self-organization
    - Adaptation to environment
    """
    
    def __init__(self, n_agents: int = 10, state_dim: int = 4):
        """
        Initialize CAS.
        
        n_agents: Number of agents
        state_dim: Dimension of state space
        """
        self.state_dim = state_dim
        
        # Agents
        self.agents: Dict[str, Agent] = {}
        for i in range(n_agents):
            agent_id = f"agent_{i}"
            state = np.random.randn(state_dim) * 0.5
            self.agents[agent_id] = Agent(id=agent_id, state=state)
        
        # Network connections
        self.connections: Dict[str, Set[str]] = {
            aid: set() for aid in self.agents
        }
        self._create_random_network(0.3)
        
        # Feedback loops
        self.feedback_loops: List[FeedbackLoop] = []
        
        # Attractors
        self.attractors: List[Attractor] = []
        
        # Global state
        self.time = 0.0
        self.equilibrium_type = EquilibriumType.DYNAMIC
        
        # History
        self.global_state_history: List[np.ndarray] = []
        self.entropy_history: List[float] = []
    
    def _create_random_network(self, connection_prob: float) -> None:
        """Create random network between agents."""
        agent_ids = list(self.agents.keys())
        for i, aid1 in enumerate(agent_ids):
            for aid2 in agent_ids[i+1:]:
                if np.random.random() < connection_prob:
                    self.connections[aid1].add(aid2)
                    self.connections[aid2].add(aid1)
                    self.agents[aid1].connectivity += 1
                    self.agents[aid2].connectivity += 1
    
    def add_feedback_loop(self, name: str, loop_type: str,
                         gain: float = 1.0) -> FeedbackLoop:
        """Add a feedback loop."""
        loop = FeedbackLoop(name=name, loop_type=loop_type, gain=gain)
        self.feedback_loops.append(loop)
        return loop
    
    def add_attractor(self, attractor_type: AttractorType,
                     center: np.ndarray = None,
                     strength: float = 1.0) -> Attractor:
        """Add an attractor."""
        attractor = Attractor(attractor_type, center, strength)
        self.attractors.append(attractor)
        return attractor
    
    @property
    def global_state(self) -> np.ndarray:
        """Get mean state across all agents."""
        if not self.agents:
            return np.zeros(self.state_dim)
        
        states = np.array([a.state for a in self.agents.values()])
        return np.mean(states, axis=0)
    
    @property
    def variance(self) -> float:
        """Get variance of agent states (measure of disorder)."""
        if not self.agents:
            return 0.0
        
        states = np.array([a.state for a in self.agents.values()])
        return float(np.var(states))
    
    @property
    def entropy(self) -> float:
        """Estimate system entropy."""
        # Use variance as proxy for entropy
        return math.log(1 + self.variance)
    
    def step(self, dt: float = 0.1) -> Dict[str, Any]:
        """
        Execute one time step of the CAS.
        """
        self.time += dt
        
        # 1. Agent interactions
        for aid, connections in self.connections.items():
            agent = self.agents[aid]
            total_influence = np.zeros(self.state_dim)
            
            for neighbor_id in connections:
                neighbor = self.agents[neighbor_id]
                self_inf, _ = agent.interact(neighbor)
                total_influence += self_inf
            
            agent.update_state(total_influence, dt)
        
        # 2. Apply attractors
        for attractor in self.attractors:
            for agent in self.agents.values():
                force = attractor.attract(agent.state, dt)
                agent.update_state(force, 1.0)
        
        # 3. Process feedback
        error = np.linalg.norm(self.global_state)
        for loop in self.feedback_loops:
            correction = loop.process(error)
            
            # Apply correction to all agents
            for agent in self.agents.values():
                agent.update_state(
                    np.ones(self.state_dim) * correction * 0.01, dt
                )
        
        # 4. Record history
        self.global_state_history.append(self.global_state.copy())
        self.entropy_history.append(self.entropy)
        
        if len(self.global_state_history) > 1000:
            self.global_state_history = self.global_state_history[-500:]
            self.entropy_history = self.entropy_history[-500:]
        
        return {
            "time": self.time,
            "global_state": self.global_state.tolist(),
            "variance": self.variance,
            "entropy": self.entropy,
            "n_agents": len(self.agents)
        }
    
    def run(self, n_steps: int = 100, dt: float = 0.1) -> List[Dict[str, Any]]:
        """Run simulation for n steps."""
        results = []
        for _ in range(n_steps):
            result = self.step(dt)
            results.append(result)
        return results
    
    def adapt_to_environment(self, environment: Dict[str, Any]) -> None:
        """Have all agents adapt to environment."""
        for agent in self.agents.values():
            agent.adapt(environment)
    
    def classify_equilibrium(self) -> EquilibriumType:
        """
        Classify current equilibrium type based on dynamics.
        """
        if len(self.global_state_history) < 20:
            return EquilibriumType.DYNAMIC
        
        recent = np.array(self.global_state_history[-20:])
        
        # Check for fixed point
        variance = np.var(recent, axis=0).mean()
        if variance < 0.01:
            self.equilibrium_type = EquilibriumType.STATIC
            return EquilibriumType.STATIC
        
        # Check for chaos (high variance, bounded)
        total_var = np.var(recent.flatten())
        if total_var > 1.0:
            self.equilibrium_type = EquilibriumType.CHAOTIC
            return EquilibriumType.CHAOTIC
        
        # Check for edge of chaos (moderate variance)
        if 0.1 < variance < 0.5:
            self.equilibrium_type = EquilibriumType.EDGE_OF_CHAOS
            return EquilibriumType.EDGE_OF_CHAOS
        
        self.equilibrium_type = EquilibriumType.DYNAMIC
        return EquilibriumType.DYNAMIC
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get system statistics."""
        return {
            "n_agents": len(self.agents),
            "total_connections": sum(len(c) for c in self.connections.values()) // 2,
            "n_feedback_loops": len(self.feedback_loops),
            "n_attractors": len(self.attractors),
            "equilibrium_type": self.equilibrium_type.value,
            "global_state": self.global_state.tolist(),
            "variance": self.variance,
            "entropy": self.entropy,
            "time": self.time,
            "mean_fitness": np.mean([a.fitness for a in self.agents.values()]),
            "mean_connectivity": np.mean([a.connectivity for a in self.agents.values()])
        }


# =============================================================================
# SELF-OPTIMIZATION
# =============================================================================

class SelfOptimizer:
    """
    Self-optimization layer for the CAS.
    
    Continuously tunes parameters to maintain optimal performance.
    """
    
    def __init__(self, cas: ComplexAdaptiveSystem):
        self.cas = cas
        
        # Targets
        self.target_entropy = 0.5       # Edge of chaos
        self.target_fitness = 0.8
        
        # Learning rates
        self.entropy_lr = 0.1
        self.fitness_lr = 0.1
        
        # Optimization history
        self.optimization_history: List[Dict[str, float]] = []
    
    def optimize_step(self) -> Dict[str, Any]:
        """
        Execute one optimization step.
        
        Adjusts system parameters toward targets.
        """
        current_entropy = self.cas.entropy
        current_fitness = np.mean([a.fitness for a in self.cas.agents.values()])
        
        # Entropy optimization
        entropy_error = self.target_entropy - current_entropy
        
        if abs(entropy_error) > 0.1:
            # Too much entropy: increase coupling (more order)
            # Too little entropy: decrease coupling (more chaos)
            coupling_adjustment = entropy_error * self.entropy_lr
            
            for agent in self.cas.agents.values():
                agent.adaptability = max(0.1, min(0.9, 
                    agent.adaptability + coupling_adjustment))
        
        # Fitness optimization
        for attractor in self.cas.attractors:
            if attractor.attractor_type == AttractorType.POINT:
                # Adjust attractor strength based on fitness
                fitness_error = self.target_fitness - current_fitness
                attractor.strength = max(0.1, min(2.0,
                    attractor.strength + fitness_error * self.fitness_lr))
        
        result = {
            "entropy_error": entropy_error,
            "fitness": current_fitness,
            "equilibrium": self.cas.classify_equilibrium().value
        }
        
        self.optimization_history.append(result)
        
        return result
    
    def auto_optimize(self, n_steps: int = 100) -> None:
        """Run automatic optimization."""
        for _ in range(n_steps):
            self.cas.step(0.1)
            self.optimize_step()


# =============================================================================
# VALIDATION
# =============================================================================

def validate_cas() -> bool:
    """Validate Complex Adaptive Systems module."""
    
    # Test Agent
    agent = Agent(id="test", state=np.array([1.0, 0.0, 0.0, 0.0]))
    assert agent.energy > 0
    
    agent.update_state(np.array([0.1, 0.1, 0.0, 0.0]))
    
    agent2 = Agent(id="test2", state=np.array([0.0, 1.0, 0.0, 0.0]))
    inf1, inf2 = agent.interact(agent2)
    assert inf1.shape == agent.state.shape
    
    # Test FeedbackLoop
    neg_loop = FeedbackLoop(name="stabilizer", loop_type="negative", gain=0.5)
    output = neg_loop.process(1.0)
    assert output < 0  # Negative feedback
    
    pos_loop = FeedbackLoop(name="amplifier", loop_type="positive", gain=2.0)
    output = pos_loop.process(1.0)
    assert output > 0  # Positive feedback
    
    # Test Attractor
    point_attr = Attractor(AttractorType.POINT, np.zeros(4), strength=1.0)
    state = np.array([1.0, 1.0, 0.0, 0.0])
    force = point_attr.attract(state)
    assert np.linalg.norm(force) > 0  # Should attract
    
    cycle_attr = Attractor(AttractorType.LIMIT_CYCLE)
    force = cycle_attr.attract(state)
    assert force is not None
    
    # Test ComplexAdaptiveSystem
    cas = ComplexAdaptiveSystem(n_agents=5, state_dim=4)
    assert len(cas.agents) == 5
    
    # Add components
    cas.add_feedback_loop("stabilizer", "negative", 0.5)
    cas.add_attractor(AttractorType.POINT, np.zeros(4), 0.5)
    
    # Run simulation
    results = cas.run(10, dt=0.1)
    assert len(results) == 10
    
    # Check equilibrium classification
    eq_type = cas.classify_equilibrium()
    assert eq_type in EquilibriumType
    
    stats = cas.get_statistics()
    assert "n_agents" in stats
    assert "entropy" in stats
    
    # Test SelfOptimizer
    optimizer = SelfOptimizer(cas)
    result = optimizer.optimize_step()
    assert "entropy_error" in result
    
    return True


if __name__ == "__main__":
    print("Validating Complex Adaptive Systems Module...")
    assert validate_cas()
    print("✓ Complex Adaptive Systems Module validated")
    
    # Demo
    print("\n--- Complex Adaptive Systems Demo ---")
    
    cas = ComplexAdaptiveSystem(n_agents=20, state_dim=4)
    
    print("\nInitial State:")
    stats = cas.get_statistics()
    print(f"  Agents: {stats['n_agents']}")
    print(f"  Connections: {stats['total_connections']}")
    print(f"  Initial entropy: {stats['entropy']:.4f}")
    
    # Add feedback and attractors
    print("\nAdding System Components:")
    cas.add_feedback_loop("negative_fb", "negative", 0.3)
    cas.add_feedback_loop("positive_fb", "positive", 0.1)
    cas.add_attractor(AttractorType.POINT, np.array([0.5, 0.5, 0.0, 0.0]), 0.2)
    print("  Added 2 feedback loops")
    print("  Added 1 point attractor")
    
    # Run simulation
    print("\nRunning Simulation (100 steps)...")
    results = cas.run(100, dt=0.1)
    
    print(f"\nFinal State:")
    stats = cas.get_statistics()
    print(f"  Equilibrium type: {stats['equilibrium_type']}")
    print(f"  Final entropy: {stats['entropy']:.4f}")
    print(f"  Variance: {stats['variance']:.4f}")
    print(f"  Mean fitness: {stats['mean_fitness']:.4f}")
    
    # Self-optimization
    print("\nRunning Self-Optimization...")
    optimizer = SelfOptimizer(cas)
    optimizer.auto_optimize(50)
    
    print(f"\nAfter Optimization:")
    stats = cas.get_statistics()
    print(f"  Equilibrium type: {stats['equilibrium_type']}")
    print(f"  Final entropy: {stats['entropy']:.4f}")
    print(f"  Target entropy: {optimizer.target_entropy}")
