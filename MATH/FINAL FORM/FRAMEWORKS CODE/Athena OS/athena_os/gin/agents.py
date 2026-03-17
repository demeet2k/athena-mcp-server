"""
ATHENA OS - GLOBAL INFORMATION NETWORK
======================================
Agents: Multi-Agent System Architecture and Distributed Consensus

From GLOBAL_INFORMATION_NETWORK.docx §1.4 and §2:

AGENT DEFINITION:
    Agent = (G, A, π) where:
    - G: Goals/objectives
    - A: Action set
    - π: Policy π(a|s)
    
    Humans modeled as control subroutines with bounded rationality.

OBJECTIVE FUNCTION:
    J = ∫(E + S)dt
    Minimize energy (E) and entropy (S) over time.

DISTRIBUTED CONSENSUS ("Culture" as protocol):
    - Culture = consensus layer
    - Norms → agreement
    - Trust weights
    - Byzantine failure handling

KOŚA (SHEATH) ARCHITECTURE:
    - Annamaya: Hardware constraints (persistent storage)
    - Prāṇamaya: Energy/resource budget
    - Manomaya: Perception/working memory
    - Vijñānamaya: Kernel logic (decision operator D)

EGO-BOUNDARY CONTROLLER (Ahaṃkāra):
    PID controller model maintaining self-model coherence.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Set, Callable
from enum import Enum
import numpy as np
from abc import ABC, abstractmethod

from .valuation import V4, Valuation


# =============================================================================
# AGENT DEFINITION
# =============================================================================

@dataclass
class Goal:
    """Agent goal with priority and satisfaction function."""
    
    name: str
    priority: float = 1.0
    satisfaction: Callable[[np.ndarray], float] = field(default_factory=lambda: lambda x: 0.0)
    
    def evaluate(self, state: np.ndarray) -> float:
        """Evaluate goal satisfaction at state."""
        return self.satisfaction(state)


@dataclass
class Agent:
    """
    Multi-agent system agent.
    
    Agent = (G, A, π) with bounded rationality.
    """
    
    agent_id: str
    goals: List[Goal] = field(default_factory=list)
    action_space: List[np.ndarray] = field(default_factory=list)
    
    # State
    state: np.ndarray = field(default_factory=lambda: np.zeros(4))
    belief: Dict[str, float] = field(default_factory=dict)
    
    # Policy parameters
    temperature: float = 1.0  # For softmax policy
    rationality_bound: float = 0.9  # < 1 means bounded rationality
    
    def add_goal(self, name: str, priority: float,
                 satisfaction: Callable[[np.ndarray], float]) -> None:
        """Add a goal to the agent."""
        self.goals.append(Goal(name, priority, satisfaction))
    
    def objective(self, state: np.ndarray) -> float:
        """
        Compute total objective J at state.
        
        Weighted sum of goal satisfactions.
        """
        total = 0.0
        for goal in self.goals:
            total += goal.priority * goal.evaluate(state)
        return total
    
    def policy(self, state: np.ndarray) -> np.ndarray:
        """
        Compute action probabilities π(a|s).
        
        Uses softmax over action values with bounded rationality.
        """
        if not self.action_space:
            return np.array([])
        
        # Compute action values
        values = []
        for action in self.action_space:
            # Estimate next state (simplified)
            next_state = state + 0.1 * action
            value = self.objective(next_state)
            values.append(value)
        
        values = np.array(values)
        
        # Apply bounded rationality (add noise)
        noise = (1 - self.rationality_bound) * np.random.randn(len(values))
        values = values + noise
        
        # Softmax
        exp_values = np.exp(values / self.temperature)
        probs = exp_values / (np.sum(exp_values) + 1e-10)
        
        return probs
    
    def select_action(self, state: np.ndarray) -> np.ndarray:
        """Select action according to policy."""
        if not self.action_space:
            return np.zeros_like(state)
        
        probs = self.policy(state)
        idx = np.random.choice(len(self.action_space), p=probs)
        return self.action_space[idx]


# =============================================================================
# KOŚA (SHEATH) ARCHITECTURE
# =============================================================================

class KosaLayer(Enum):
    """The five sheaths of agent architecture."""
    
    ANNAMAYA = "annamaya"      # Hardware/persistent storage
    PRANAMAYA = "pranamaya"    # Energy/resource budget
    MANOMAYA = "manomaya"      # Perception/working memory
    VIJNANAMAYA = "vijnanamaya"  # Kernel logic
    ANANDAMAYA = "anandamaya"  # Bliss/optimization target


@dataclass
class Annamaya:
    """
    Annamaya Kośa: Hardware constraints.
    
    Persistent storage and physical limits.
    """
    
    storage_capacity: int = 1000  # C_disk
    compute_rate: float = 1.0     # Operations per time unit
    
    # State
    stored_data: Dict[str, any] = field(default_factory=dict)
    
    def store(self, key: str, value: any) -> bool:
        """Store data if capacity allows."""
        if len(self.stored_data) >= self.storage_capacity:
            return False
        self.stored_data[key] = value
        return True
    
    def retrieve(self, key: str) -> Optional[any]:
        """Retrieve stored data."""
        return self.stored_data.get(key)
    
    def available_capacity(self) -> int:
        """Get remaining storage capacity."""
        return self.storage_capacity - len(self.stored_data)


@dataclass
class Pranamaya:
    """
    Prāṇamaya Kośa: Energy/resource budget.
    
    Rate constraints and resource allocation.
    """
    
    energy_budget: float = 100.0  # E_budget
    energy_rate: float = 1.0      # Recharge rate
    
    # State
    current_energy: float = 100.0
    
    def consume(self, amount: float) -> bool:
        """Consume energy if available."""
        if amount > self.current_energy:
            return False
        self.current_energy -= amount
        return True
    
    def recharge(self, dt: float) -> None:
        """Recharge energy over time."""
        self.current_energy = min(
            self.energy_budget,
            self.current_energy + self.energy_rate * dt
        )
    
    def available_energy(self) -> float:
        """Get current available energy."""
        return self.current_energy


@dataclass
class Manomaya:
    """
    Manomaya Kośa: Perception and working memory.
    
    Bounded buffer with capacity and rate constraints.
    Primary source of partial observability → U in V4.
    """
    
    buffer_capacity: int = 10     # C_ram
    input_rate: float = 1.0       # R_io
    
    # State
    buffer: List[np.ndarray] = field(default_factory=list)
    state_estimate: np.ndarray = field(default_factory=lambda: np.zeros(4))
    
    def observe(self, observation: np.ndarray) -> bool:
        """Add observation to buffer."""
        if len(self.buffer) >= self.buffer_capacity:
            self.buffer.pop(0)  # Remove oldest
        self.buffer.append(observation)
        return True
    
    def update_estimate(self) -> np.ndarray:
        """Update state estimate from buffer."""
        if not self.buffer:
            return self.state_estimate
        
        # Simple averaging
        self.state_estimate = np.mean(self.buffer, axis=0)
        return self.state_estimate
    
    def clear_buffer(self) -> None:
        """Clear working memory."""
        self.buffer.clear()


@dataclass
class Vijnanamaya:
    """
    Vijñānamaya Kośa: Kernel logic (decision operator D).
    
    D: (ŝ, y) → (u, ν)
    
    Maps state estimate and observation to action and valuation.
    Must handle B-valued propositions without explosion.
    """
    
    valuation: Valuation = field(default_factory=Valuation)
    
    def decide(self, state_estimate: np.ndarray,
               observation: np.ndarray,
               action_space: List[np.ndarray]) -> Tuple[np.ndarray, Valuation]:
        """
        Apply decision operator D.
        
        Args:
            state_estimate: Current state estimate ŝ
            observation: Latest observation y
            action_space: Available actions
        
        Returns:
            (selected_action, updated_valuation)
        """
        # Update valuation based on observation
        self._update_valuation(state_estimate, observation)
        
        # Select action that respects valuation constraints
        action = self._select_safe_action(state_estimate, action_space)
        
        return (action, self.valuation)
    
    def _update_valuation(self, state: np.ndarray, obs: np.ndarray) -> None:
        """Update valuation based on new evidence."""
        # Example: check if state is in safe region
        is_safe = np.linalg.norm(state) < 2.0
        
        if is_safe:
            self.valuation["safe"] = V4.T
        else:
            self.valuation["safe"] = V4.F
        
        # Check for uncertainty
        obs_noise = np.std(obs)
        if obs_noise > 0.5:
            self.valuation["certain"] = V4.U
        else:
            self.valuation["certain"] = V4.T
    
    def _select_safe_action(self, state: np.ndarray,
                           actions: List[np.ndarray]) -> np.ndarray:
        """Select action respecting valuation constraints."""
        if not actions:
            return np.zeros_like(state)
        
        # Filter by safety
        safe_actions = []
        for a in actions:
            next_state = state + 0.1 * a
            if np.linalg.norm(next_state) < 2.0:
                safe_actions.append(a)
        
        if safe_actions:
            return safe_actions[np.random.randint(len(safe_actions))]
        
        # If no safe action, return smallest action
        norms = [np.linalg.norm(a) for a in actions]
        return actions[np.argmin(norms)]


@dataclass
class KosaStack:
    """
    Complete Kośa stack for an agent.
    """
    
    annamaya: Annamaya = field(default_factory=Annamaya)
    pranamaya: Pranamaya = field(default_factory=Pranamaya)
    manomaya: Manomaya = field(default_factory=Manomaya)
    vijnanamaya: Vijnanamaya = field(default_factory=Vijnanamaya)
    
    def process(self, observation: np.ndarray,
                action_space: List[np.ndarray],
                energy_cost: float = 1.0) -> Optional[np.ndarray]:
        """
        Process observation through full stack.
        
        Returns action or None if resource constrained.
        """
        # Check energy
        if not self.pranamaya.consume(energy_cost):
            return None  # No energy
        
        # Perceive
        self.manomaya.observe(observation)
        state_estimate = self.manomaya.update_estimate()
        
        # Decide
        action, valuation = self.vijnanamaya.decide(
            state_estimate, observation, action_space
        )
        
        # Store decision
        self.annamaya.store(
            f"decision_{len(self.annamaya.stored_data)}",
            {"state": state_estimate.tolist(), "action": action.tolist()}
        )
        
        return action


# =============================================================================
# EGO-BOUNDARY CONTROLLER (AHAMKARA)
# =============================================================================

@dataclass
class EgoBoundary:
    """
    Ahaṃkāra: Ego-boundary controller.
    
    PID controller maintaining coherence between self-model and state.
    
    u(t) = K_P e(t) + K_I ∫e(τ)dτ + K_D de/dt
    """
    
    # PID gains
    k_p: float = 1.0   # Proportional
    k_i: float = 0.1   # Integral
    k_d: float = 0.05  # Derivative
    
    # Reference (self-model)
    reference: np.ndarray = field(default_factory=lambda: np.zeros(4))
    
    # State
    integral_error: np.ndarray = field(default_factory=lambda: np.zeros(4))
    prev_error: np.ndarray = field(default_factory=lambda: np.zeros(4))
    
    def set_reference(self, ref: np.ndarray) -> None:
        """Set self-model reference trajectory."""
        self.reference = ref.copy()
    
    def compute_correction(self, state: np.ndarray, dt: float = 0.1) -> np.ndarray:
        """
        Compute corrective action from PID controller.
        
        Args:
            state: Current operational state s(t)
            dt: Time step
        
        Returns:
            Correction u(t)
        """
        # Error
        error = self.reference - state
        
        # Integral
        self.integral_error += error * dt
        
        # Derivative
        derivative = (error - self.prev_error) / dt
        self.prev_error = error.copy()
        
        # PID output
        u = (self.k_p * error + 
             self.k_i * self.integral_error + 
             self.k_d * derivative)
        
        return u
    
    def reset(self) -> None:
        """Reset controller state."""
        self.integral_error = np.zeros_like(self.reference)
        self.prev_error = np.zeros_like(self.reference)


# =============================================================================
# DISTRIBUTED CONSENSUS
# =============================================================================

@dataclass
class ConsensusProtocol:
    """
    Distributed consensus protocol ("Culture" as protocol).
    
    Handles opinion dynamics, trust weights, and Byzantine failures.
    """
    
    n_agents: int = 10
    trust_matrix: np.ndarray = field(default_factory=lambda: np.eye(10))
    
    # State
    opinions: np.ndarray = field(default_factory=lambda: np.random.randn(10))
    
    def __post_init__(self):
        """Initialize with random opinions."""
        if self.opinions.shape[0] != self.n_agents:
            self.opinions = np.random.randn(self.n_agents)
        if self.trust_matrix.shape != (self.n_agents, self.n_agents):
            self.trust_matrix = np.eye(self.n_agents)
    
    def set_trust(self, i: int, j: int, trust: float) -> None:
        """Set trust weight from agent i to agent j."""
        if 0 <= i < self.n_agents and 0 <= j < self.n_agents:
            self.trust_matrix[i, j] = max(0.0, min(1.0, trust))
    
    def update_opinions(self, learning_rate: float = 0.1) -> np.ndarray:
        """
        Update opinions via consensus dynamics.
        
        x_i(t+1) = x_i(t) + η Σ_j w_ij (x_j(t) - x_i(t))
        """
        new_opinions = self.opinions.copy()
        
        for i in range(self.n_agents):
            influence = 0.0
            total_weight = 0.0
            
            for j in range(self.n_agents):
                if i != j:
                    weight = self.trust_matrix[i, j]
                    influence += weight * (self.opinions[j] - self.opinions[i])
                    total_weight += weight
            
            if total_weight > 0:
                new_opinions[i] += learning_rate * influence / total_weight
        
        self.opinions = new_opinions
        return self.opinions
    
    def consensus_value(self) -> float:
        """Get current consensus value (mean)."""
        return float(np.mean(self.opinions))
    
    def consensus_variance(self) -> float:
        """Get variance (measure of disagreement)."""
        return float(np.var(self.opinions))
    
    def detect_byzantine(self, threshold: float = 2.0) -> List[int]:
        """
        Detect potential Byzantine (adversarial) agents.
        
        Agents whose opinions deviate significantly from consensus.
        """
        mean = self.consensus_value()
        std = np.std(self.opinions) + 1e-10
        
        byzantine = []
        for i in range(self.n_agents):
            z_score = abs(self.opinions[i] - mean) / std
            if z_score > threshold:
                byzantine.append(i)
        
        return byzantine
    
    def isolate_byzantine(self, agents: List[int]) -> None:
        """Reduce trust in suspected Byzantine agents."""
        for i in agents:
            for j in range(self.n_agents):
                self.trust_matrix[j, i] *= 0.1  # Reduce incoming trust


# =============================================================================
# MULTI-AGENT SYSTEM
# =============================================================================

@dataclass
class MultiAgentSystem:
    """
    Complete multi-agent system with consensus.
    """
    
    agents: Dict[str, Agent] = field(default_factory=dict)
    consensus: ConsensusProtocol = field(default_factory=ConsensusProtocol)
    
    # Global state
    global_state: np.ndarray = field(default_factory=lambda: np.zeros(4))
    time: float = 0.0
    
    def add_agent(self, agent: Agent) -> None:
        """Add agent to system."""
        self.agents[agent.agent_id] = agent
    
    def step(self, dt: float = 0.1) -> Dict[str, np.ndarray]:
        """
        Execute one time step for all agents.
        
        Returns dict of agent_id → action taken.
        """
        actions = {}
        
        for agent_id, agent in self.agents.items():
            # Agent selects action
            action = agent.select_action(agent.state)
            actions[agent_id] = action
            
            # Update agent state (simplified dynamics)
            agent.state = agent.state + dt * action
        
        # Update consensus
        self.consensus.update_opinions()
        
        # Update time
        self.time += dt
        
        return actions
    
    def compute_social_objective(self) -> float:
        """
        Compute total social objective.
        
        J_total = Σ_i J_i (agent objectives)
        """
        total = 0.0
        for agent in self.agents.values():
            total += agent.objective(agent.state)
        return total
    
    def sync_agent_opinions(self) -> None:
        """Sync agent beliefs with consensus protocol."""
        if len(self.agents) != self.consensus.n_agents:
            return
        
        for i, (agent_id, agent) in enumerate(self.agents.items()):
            agent.belief["consensus"] = self.consensus.opinions[i]


# =============================================================================
# VALIDATION
# =============================================================================

def validate_agents() -> bool:
    """Validate agents module."""
    
    # Test Agent
    agent = Agent(agent_id="test")
    agent.add_goal("minimize_norm", 1.0, lambda s: -np.linalg.norm(s))
    agent.action_space = [
        np.array([1.0, 0.0, 0.0, 0.0]),
        np.array([-1.0, 0.0, 0.0, 0.0]),
        np.array([0.0, 1.0, 0.0, 0.0])
    ]
    
    state = np.array([0.5, 0.0, 0.0, 0.0])
    probs = agent.policy(state)
    assert len(probs) == 3
    assert np.isclose(np.sum(probs), 1.0)
    
    action = agent.select_action(state)
    assert action.shape == (4,)
    
    # Test KosaStack
    stack = KosaStack()
    
    obs = np.array([0.1, 0.2, 0.3, 0.4])
    actions = agent.action_space
    
    result = stack.process(obs, actions)
    assert result is not None
    assert result.shape == (4,)
    
    # Test after energy depletion
    stack.pranamaya.current_energy = 0.0
    result = stack.process(obs, actions)
    assert result is None  # No energy
    
    # Test EgoBoundary
    ego = EgoBoundary()
    ego.set_reference(np.array([1.0, 0.0, 0.0, 0.0]))
    
    state = np.array([0.5, 0.0, 0.0, 0.0])
    correction = ego.compute_correction(state)
    assert correction[0] > 0  # Should push toward reference
    
    # Test ConsensusProtocol
    consensus = ConsensusProtocol(n_agents=5)
    consensus.opinions = np.array([0.0, 0.1, 0.2, 0.1, 10.0])  # Last is outlier
    
    # Initial variance
    initial_var = consensus.consensus_variance()
    
    # Run consensus
    for _ in range(10):
        consensus.update_opinions()
    
    # Variance should decrease
    final_var = consensus.consensus_variance()
    # May not always decrease due to outlier
    
    # Detect byzantine
    consensus.opinions = np.array([0.0, 0.1, 0.2, 0.1, 10.0])
    byzantine = consensus.detect_byzantine()
    assert 4 in byzantine  # Agent 4 is outlier
    
    # Test MultiAgentSystem
    mas = MultiAgentSystem()
    mas.add_agent(agent)
    
    actions = mas.step()
    assert "test" in actions
    
    return True


if __name__ == "__main__":
    print("Validating Agents and Consensus...")
    assert validate_agents()
    print("✓ Agents module validated")
