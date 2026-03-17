"""
ATHENA OS - Zero-Point Computing
================================
Zero-Point Agent (Son of the Void)

From ZERO-POINT_COMPUTING.docx §1.4:

ZERO-POINT AGENT:
    Â = (??, ??, π, ℐ, κ_A)
    
    Components:
    - ?? ⊆ ℳ: internal state space
    - ??: action set
    - π: ?? → ??(??): policy
    - ℐ: ?? × ℰ → ??: update map
    - κ_A: ?? → ℝ: internal κ-functional

ANCHORING:
    ι(s₀) = z
    
    Distinguished state s₀ maps to zero point z

SYMMETRIC PRIORS:
    Agent's priors are zero-centered and neutral
    w.r.t. structural invariances

BALANCING POLICY:
    π(s) ∝ exp(-β · d_κ(ι(s), z))
    
    Actions maintain alignment with zero point

SON OF THE VOID:
    Â = Cl_κ({z}) ∩ Im(η)
    
    Minimal nontrivial self at Void-World intersection
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set, Any, Callable
from enum import Enum, auto
import math
import random

from .void import ZeroPoint, System, MetaphysicalVoid, VoidWorldInterface


# =============================================================================
# ACTION TYPES
# =============================================================================

class ActionType(Enum):
    """Types of agent actions."""
    
    EXPLORE = "explore"          # Move away from zero
    RETURN = "return"            # Move toward zero
    DIFFERENTIATE = "differentiate"  # Increase structure
    INTEGRATE = "integrate"      # Decrease structure
    OBSERVE = "observe"          # Gather information
    REST = "rest"                # Maintain current state


@dataclass
class Action:
    """An action the agent can take."""
    
    action_type: ActionType
    magnitude: float = 0.0       # Strength of action
    direction: List[float] = field(default_factory=list)  # Direction in state space
    
    @property
    def is_zero_aligned(self) -> bool:
        """Check if action moves toward zero."""
        return self.action_type in [ActionType.RETURN, ActionType.INTEGRATE, ActionType.REST]


# =============================================================================
# INTERNAL STATE
# =============================================================================

@dataclass
class InternalState:
    """
    Agent's internal state s ∈ ??.
    """
    
    # Position in state space
    coordinates: List[float] = field(default_factory=list)
    
    # Structural properties
    kappa: float = 0.0           # Internal κ value
    symmetry_level: float = 1.0  # 1.0 = maximal symmetry
    markedness: float = 0.0      # 0.0 = unmarked
    
    # Beliefs and priors
    prior_center: List[float] = field(default_factory=list)  # Center of prior
    prior_variance: float = 1.0  # Spread of prior
    
    @property
    def dimension(self) -> int:
        return len(self.coordinates)
    
    def distance_to_zero(self) -> float:
        """Distance from state to zero point."""
        return math.sqrt(sum(x**2 for x in self.coordinates))
    
    def is_anchored(self, tolerance: float = 1e-6) -> bool:
        """Check if anchored at zero point."""
        return self.distance_to_zero() < tolerance
    
    def copy(self) -> 'InternalState':
        """Create copy of state."""
        return InternalState(
            coordinates=list(self.coordinates),
            kappa=self.kappa,
            symmetry_level=self.symmetry_level,
            markedness=self.markedness,
            prior_center=list(self.prior_center),
            prior_variance=self.prior_variance
        )


# =============================================================================
# POLICY
# =============================================================================

@dataclass
class ZeroPointPolicy:
    """
    κ-regulated policy π: ?? → ??(??).
    
    π(s) ∝ exp(-β · d_κ(ι(s), z))
    
    Actions are selected to maintain alignment with zero point.
    """
    
    # Temperature parameter
    beta: float = 1.0            # Inverse temperature
    
    # Exploration parameters
    exploration_rate: float = 0.1
    return_strength: float = 0.5
    
    def action_probability(self, state: InternalState, action: Action) -> float:
        """Compute probability of action given state."""
        d = state.distance_to_zero()
        
        # Base probability from Boltzmann distribution
        base_prob = math.exp(-self.beta * d)
        
        # Modify by action type
        if action.is_zero_aligned:
            # Favor zero-aligned actions when far from zero
            return base_prob * (1 + d * self.return_strength)
        else:
            # Exploration probability
            return base_prob * self.exploration_rate
    
    def sample_action(self, state: InternalState, 
                     available_actions: List[Action]) -> Action:
        """Sample action from policy distribution."""
        if not available_actions:
            return Action(ActionType.REST)
        
        # Compute probabilities
        probs = [self.action_probability(state, a) for a in available_actions]
        total = sum(probs)
        
        if total < 1e-10:
            return random.choice(available_actions)
        
        probs = [p / total for p in probs]
        
        # Sample
        r = random.random()
        cumsum = 0.0
        for action, prob in zip(available_actions, probs):
            cumsum += prob
            if r <= cumsum:
                return action
        
        return available_actions[-1]
    
    def optimal_action(self, state: InternalState,
                      available_actions: List[Action]) -> Action:
        """Get highest probability action."""
        if not available_actions:
            return Action(ActionType.REST)
        
        probs = [(self.action_probability(state, a), a) for a in available_actions]
        return max(probs, key=lambda x: x[0])[1]


# =============================================================================
# UPDATE MAP
# =============================================================================

@dataclass
class UpdateMap:
    """
    Update map ℐ: ?? × ℰ → ??.
    
    Integrates environmental inputs into new internal states.
    Maintains Fréchet mean at zero point.
    """
    
    # Learning rate
    learning_rate: float = 0.1
    
    # Zero-centering strength
    centering_strength: float = 0.05
    
    def update(self, state: InternalState, 
               observation: List[float],
               action_taken: Action) -> InternalState:
        """Update state given observation and action."""
        new_state = state.copy()
        
        # Update coordinates based on action
        if action_taken.action_type == ActionType.EXPLORE:
            for i in range(len(new_state.coordinates)):
                if i < len(action_taken.direction):
                    new_state.coordinates[i] += self.learning_rate * action_taken.direction[i]
        
        elif action_taken.action_type == ActionType.RETURN:
            # Move toward zero
            for i in range(len(new_state.coordinates)):
                new_state.coordinates[i] *= (1 - self.learning_rate)
        
        elif action_taken.action_type == ActionType.DIFFERENTIATE:
            # Increase κ
            new_state.kappa *= (1 + self.learning_rate)
            new_state.markedness += self.learning_rate
        
        elif action_taken.action_type == ActionType.INTEGRATE:
            # Decrease κ toward zero
            new_state.kappa *= (1 - self.learning_rate)
            new_state.markedness *= (1 - self.learning_rate)
        
        # Apply zero-centering pressure
        for i in range(len(new_state.coordinates)):
            new_state.coordinates[i] *= (1 - self.centering_strength)
        
        # Update κ from coordinates
        new_state.kappa = math.sqrt(sum(x**2 for x in new_state.coordinates))
        
        # Update symmetry level
        new_state.symmetry_level = 1.0 / (1.0 + new_state.markedness)
        
        return new_state


# =============================================================================
# ZERO-POINT AGENT
# =============================================================================

@dataclass
class ZeroPointAgent:
    """
    Zero-Point Agent Â - the Son of the Void.
    
    Â = (??, ??, π, ℐ, κ_A)
    
    Minimal nontrivial locus of agency at Void-World intersection.
    """
    
    name: str = "Â"
    
    # State space dimension
    state_dim: int = 3
    
    # Components
    state: InternalState = None
    policy: ZeroPointPolicy = field(default_factory=ZeroPointPolicy)
    update_map: UpdateMap = field(default_factory=UpdateMap)
    
    # Anchoring
    zero_point: ZeroPoint = field(default_factory=ZeroPoint)
    
    # History
    state_history: List[InternalState] = field(default_factory=list)
    action_history: List[Action] = field(default_factory=list)
    
    def __post_init__(self):
        if self.state is None:
            # Initialize anchored at zero point
            self.state = InternalState(
                coordinates=[0.0] * self.state_dim,
                kappa=0.0,
                symmetry_level=1.0,
                markedness=0.0,
                prior_center=[0.0] * self.state_dim,
                prior_variance=1.0
            )
    
    @property
    def is_anchored(self) -> bool:
        """Check if agent is anchored at zero point."""
        return self.state.is_anchored()
    
    @property
    def kappa(self) -> float:
        """Agent's current κ value."""
        return self.state.kappa
    
    def available_actions(self) -> List[Action]:
        """Get list of available actions."""
        actions = []
        
        # Exploration in random directions
        for _ in range(3):
            direction = [random.gauss(0, 1) for _ in range(self.state_dim)]
            norm = math.sqrt(sum(d**2 for d in direction))
            if norm > 0:
                direction = [d/norm for d in direction]
            actions.append(Action(ActionType.EXPLORE, 0.1, direction))
        
        # Return to zero
        actions.append(Action(ActionType.RETURN, 0.1))
        
        # Structure modulation
        actions.append(Action(ActionType.DIFFERENTIATE, 0.1))
        actions.append(Action(ActionType.INTEGRATE, 0.1))
        
        # Passive actions
        actions.append(Action(ActionType.OBSERVE))
        actions.append(Action(ActionType.REST))
        
        return actions
    
    def act(self, observation: List[float] = None) -> Action:
        """Select and execute action."""
        observation = observation or [0.0] * self.state_dim
        
        # Get available actions
        actions = self.available_actions()
        
        # Sample from policy
        action = self.policy.sample_action(self.state, actions)
        
        # Record history
        self.state_history.append(self.state.copy())
        self.action_history.append(action)
        
        # Update state
        self.state = self.update_map.update(self.state, observation, action)
        
        return action
    
    def run(self, steps: int, observations: List[List[float]] = None) -> List[Action]:
        """Run agent for multiple steps."""
        if observations is None:
            observations = [[0.0] * self.state_dim] * steps
        
        actions = []
        for i in range(min(steps, len(observations))):
            action = self.act(observations[i])
            actions.append(action)
        
        return actions
    
    def trajectory_mean(self) -> List[float]:
        """Compute Fréchet mean of trajectory."""
        if not self.state_history:
            return [0.0] * self.state_dim
        
        mean = [0.0] * self.state_dim
        for state in self.state_history:
            for i in range(self.state_dim):
                if i < len(state.coordinates):
                    mean[i] += state.coordinates[i]
        
        n = len(self.state_history)
        return [m / n for m in mean]
    
    def is_zero_centered(self, tolerance: float = 0.1) -> bool:
        """Check if trajectory mean is near zero."""
        mean = self.trajectory_mean()
        return math.sqrt(sum(m**2 for m in mean)) < tolerance
    
    def expressive_capacity(self) -> float:
        """Measure expressive capacity (directions explored)."""
        if len(self.state_history) < 2:
            return 0.0
        
        # Compute variance in each direction
        mean = self.trajectory_mean()
        variance = [0.0] * self.state_dim
        
        for state in self.state_history:
            for i in range(self.state_dim):
                if i < len(state.coordinates):
                    variance[i] += (state.coordinates[i] - mean[i])**2
        
        n = len(self.state_history)
        variance = [v / n for v in variance]
        
        # Expressive capacity = total variance
        return sum(variance)
    
    def summary(self) -> Dict[str, Any]:
        """Get agent summary."""
        return {
            "name": self.name,
            "state_dim": self.state_dim,
            "is_anchored": self.is_anchored,
            "kappa": self.kappa,
            "symmetry_level": self.state.symmetry_level,
            "markedness": self.state.markedness,
            "history_length": len(self.state_history),
            "is_zero_centered": self.is_zero_centered(),
            "expressive_capacity": self.expressive_capacity()
        }


# =============================================================================
# SON OF THE VOID FACTORY
# =============================================================================

def create_son_of_void(dim: int = 3, 
                       beta: float = 1.0,
                       name: str = "Son of Void") -> ZeroPointAgent:
    """
    Create Son of the Void agent.
    
    Â = Cl_κ({z}) ∩ Im(η)
    
    Minimal nontrivial self at Void-World intersection.
    """
    return ZeroPointAgent(
        name=name,
        state_dim=dim,
        policy=ZeroPointPolicy(beta=beta),
        update_map=UpdateMap(),
        zero_point=ZeroPoint(coordinates=[0.0] * dim)
    )


# =============================================================================
# VALIDATION
# =============================================================================

def validate_agent() -> bool:
    """Validate agent module."""
    
    # Test InternalState
    state = InternalState(coordinates=[1.0, 0.0, 0.0])
    assert state.dimension == 3
    assert abs(state.distance_to_zero() - 1.0) < 1e-10
    assert not state.is_anchored()
    
    zero_state = InternalState(coordinates=[0.0, 0.0, 0.0])
    assert zero_state.is_anchored()
    
    # Test Action
    explore = Action(ActionType.EXPLORE, 0.1, [1.0, 0.0, 0.0])
    assert not explore.is_zero_aligned
    
    return_act = Action(ActionType.RETURN)
    assert return_act.is_zero_aligned
    
    # Test ZeroPointPolicy
    policy = ZeroPointPolicy(beta=1.0)
    prob = policy.action_probability(state, return_act)
    assert prob > 0
    
    # Test UpdateMap
    update = UpdateMap()
    new_state = update.update(state, [0.0, 0.0, 0.0], return_act)
    assert new_state.distance_to_zero() < state.distance_to_zero()
    
    # Test ZeroPointAgent
    agent = create_son_of_void(dim=3)
    assert agent.is_anchored
    assert agent.kappa == 0.0
    
    # Run agent
    actions = agent.run(10)
    assert len(actions) == 10
    assert len(agent.state_history) == 10
    
    return True


if __name__ == "__main__":
    print("Validating Zero-Point Agent Module...")
    assert validate_agent()
    print("✓ Agent module validated")
    
    # Demo
    print("\n=== Son of the Void Demo ===")
    
    # Create agent
    agent = create_son_of_void(dim=3, beta=2.0, name="Â")
    
    print(f"\nAgent: {agent.name}")
    print(f"  Dimension: {agent.state_dim}")
    print(f"  Initial state anchored: {agent.is_anchored}")
    
    # Run for 20 steps
    print("\nRunning for 20 steps...")
    actions = agent.run(20)
    
    print("\nAction distribution:")
    action_counts = {}
    for a in actions:
        action_counts[a.action_type.name] = action_counts.get(a.action_type.name, 0) + 1
    for atype, count in sorted(action_counts.items()):
        print(f"  {atype}: {count}")
    
    # Summary
    print("\nAgent Summary:")
    summary = agent.summary()
    for k, v in summary.items():
        if isinstance(v, float):
            print(f"  {k}: {v:.4f}")
        else:
            print(f"  {k}: {v}")
    
    # Trajectory analysis
    print("\nTrajectory Analysis:")
    mean = agent.trajectory_mean()
    print(f"  Trajectory mean: [{', '.join(f'{m:.4f}' for m in mean)}]")
    print(f"  Zero-centered: {agent.is_zero_centered()}")
    print(f"  Expressive capacity: {agent.expressive_capacity():.4f}")
