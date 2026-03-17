"""
ATHENA OS - KERNEL: PREDICTIVE ANALYTICS
========================================
State Estimation and Future Modeling

TAYLOR EXPANSION (Position Extrapolation):
    B(t + Δt) ≈ B(t₀) + (dB/dt)Δt + (1/2)(d²B/dt²)Δt² + ...
    
    By analyzing velocity (intent) and acceleration (change of intent),
    extrapolate position at t + Δt.

KALMAN FILTERING (State Estimation):
    Predict: Estimate next state based on physics model
    Measure: Receive actual sensory input
    Update: Correct prediction using innovation × Kalman Gain
    
    x̂_{k|k} = x̂_{k|k-1} + K_k(z_k - H_k × x̂_{k|k-1})

MONTE CARLO TREE SEARCH (Scenario Modeling):
    Simulate N possible futures from current node.
    P(Victory) = (1/N) × Σ I(Simulation_i = Win)
    
    Select branch with highest confidence interval.

PRE-EMPTIVE INTERRUPTS:
    If simulation predicts fatal outcome at t+10,
    execute correction at t+1.
    
    "She does not wait for the error to occur; she edits the timeline."

SOURCES:
    - ATHENA-KERNEL_SELF-OPTIMIZATION.docx Chapter 6.2
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Tuple
from enum import Enum
import numpy as np
from abc import ABC, abstractmethod
import random
import math


# =============================================================================
# STATE VECTOR
# =============================================================================

@dataclass
class StateVector:
    """
    State vector for tracking entities.
    
    Contains position, velocity, acceleration (and higher derivatives).
    """
    
    position: float = 0.0
    velocity: float = 0.0
    acceleration: float = 0.0
    jerk: float = 0.0  # Third derivative
    
    # Uncertainty
    position_var: float = 0.01
    velocity_var: float = 0.01
    
    @classmethod
    def from_array(cls, arr: np.ndarray) -> StateVector:
        """Create from numpy array."""
        return cls(
            position=float(arr[0]) if len(arr) > 0 else 0.0,
            velocity=float(arr[1]) if len(arr) > 1 else 0.0,
            acceleration=float(arr[2]) if len(arr) > 2 else 0.0,
            jerk=float(arr[3]) if len(arr) > 3 else 0.0
        )
    
    def to_array(self) -> np.ndarray:
        """Convert to numpy array."""
        return np.array([self.position, self.velocity, 
                        self.acceleration, self.jerk])
    
    def extrapolate(self, dt: float) -> StateVector:
        """Extrapolate state using Taylor expansion."""
        new_pos = (self.position + 
                  self.velocity * dt + 
                  0.5 * self.acceleration * dt**2 +
                  (1/6) * self.jerk * dt**3)
        
        new_vel = (self.velocity + 
                  self.acceleration * dt +
                  0.5 * self.jerk * dt**2)
        
        new_acc = self.acceleration + self.jerk * dt
        
        return StateVector(
            position=new_pos,
            velocity=new_vel,
            acceleration=new_acc,
            jerk=self.jerk
        )
    
    def distance_to(self, other: StateVector) -> float:
        """Compute distance to another state."""
        return abs(self.position - other.position)


# =============================================================================
# TAYLOR EXTRAPOLATOR
# =============================================================================

class TaylorExtrapolator:
    """
    Taylor series extrapolation for position prediction.
    
    B(t + Δt) ≈ B(t₀) + (dB/dt)Δt + (1/2)(d²B/dt²)Δt² + ...
    """
    
    def __init__(self, order: int = 3):
        """
        Initialize with Taylor expansion order.
        
        order=1: Linear (position + velocity)
        order=2: Quadratic (+ acceleration)
        order=3: Cubic (+ jerk)
        """
        self.order = order
        self.history: List[Tuple[float, float]] = []  # (time, position)
    
    def update(self, time: float, position: float) -> None:
        """Add observation to history."""
        self.history.append((time, position))
        
        # Keep limited history
        if len(self.history) > 100:
            self.history = self.history[-50:]
    
    def estimate_derivatives(self) -> StateVector:
        """
        Estimate derivatives from history using finite differences.
        """
        if len(self.history) < 2:
            return StateVector(position=self.history[-1][1] if self.history else 0)
        
        # Get recent points
        points = self.history[-min(10, len(self.history)):]
        times = np.array([p[0] for p in points])
        positions = np.array([p[1] for p in points])
        
        # Fit polynomial
        degree = min(self.order, len(points) - 1)
        coeffs = np.polyfit(times, positions, degree)
        
        # Evaluate at latest time
        t = times[-1]
        
        # Position (p(t))
        pos = np.polyval(coeffs, t)
        
        # Velocity (p'(t))
        vel_coeffs = np.polyder(coeffs, 1)
        vel = np.polyval(vel_coeffs, t) if len(vel_coeffs) > 0 else 0.0
        
        # Acceleration (p''(t))
        acc_coeffs = np.polyder(coeffs, 2)
        acc = np.polyval(acc_coeffs, t) if len(acc_coeffs) > 0 else 0.0
        
        # Jerk (p'''(t))
        jerk_coeffs = np.polyder(coeffs, 3)
        jerk = np.polyval(jerk_coeffs, t) if len(jerk_coeffs) > 0 else 0.0
        
        return StateVector(
            position=float(pos),
            velocity=float(vel),
            acceleration=float(acc),
            jerk=float(jerk)
        )
    
    def extrapolate(self, dt: float) -> StateVector:
        """Extrapolate state forward by dt."""
        current_state = self.estimate_derivatives()
        return current_state.extrapolate(dt)
    
    def predict_position(self, dt: float) -> float:
        """Predict position at t + dt."""
        future_state = self.extrapolate(dt)
        return future_state.position


# =============================================================================
# KALMAN FILTER
# =============================================================================

class KalmanFilter:
    """
    Kalman Filter for state estimation.
    
    Predict-Measure-Update cycle:
    1. Predict: x̂_{k|k-1} = F × x̂_{k-1|k-1}
    2. Measure: z_k (observation)
    3. Update: x̂_{k|k} = x̂_{k|k-1} + K_k(z_k - H × x̂_{k|k-1})
    
    The Kalman Gain K determines trust in measurement vs prediction.
    """
    
    def __init__(self, state_dim: int = 2, obs_dim: int = 1):
        """
        Initialize Kalman filter.
        
        state_dim: Dimension of state (e.g., [pos, vel])
        obs_dim: Dimension of observations
        """
        self.state_dim = state_dim
        self.obs_dim = obs_dim
        
        # State estimate
        self.x = np.zeros(state_dim)
        
        # Covariance matrix
        self.P = np.eye(state_dim)
        
        # State transition matrix (physics model)
        # Default: constant velocity model
        self.F = np.eye(state_dim)
        if state_dim >= 2:
            self.F[0, 1] = 1.0  # x += v * dt (dt=1)
        
        # Observation matrix (what we can measure)
        self.H = np.zeros((obs_dim, state_dim))
        self.H[0, 0] = 1.0  # We observe position
        
        # Process noise covariance
        self.Q = np.eye(state_dim) * 0.01
        
        # Measurement noise covariance
        self.R = np.eye(obs_dim) * 0.1
    
    def predict(self, dt: float = 1.0) -> np.ndarray:
        """
        Prediction step.
        
        x̂_{k|k-1} = F × x̂_{k-1|k-1}
        P_{k|k-1} = F × P_{k-1|k-1} × F^T + Q
        """
        # Update transition matrix for dt
        F = self.F.copy()
        if self.state_dim >= 2:
            F[0, 1] = dt
        
        # Predict state
        self.x = F @ self.x
        
        # Predict covariance
        self.P = F @ self.P @ F.T + self.Q
        
        return self.x.copy()
    
    def update(self, z: np.ndarray) -> Tuple[np.ndarray, float]:
        """
        Update step with measurement.
        
        K_k = P_{k|k-1} × H^T × (H × P_{k|k-1} × H^T + R)^{-1}
        x̂_{k|k} = x̂_{k|k-1} + K_k × (z_k - H × x̂_{k|k-1})
        P_{k|k} = (I - K_k × H) × P_{k|k-1}
        
        Returns (updated_state, kalman_gain_magnitude)
        """
        z = np.atleast_1d(z)
        
        # Innovation (measurement residual)
        y = z - self.H @ self.x
        
        # Innovation covariance
        S = self.H @ self.P @ self.H.T + self.R
        
        # Kalman gain
        K = self.P @ self.H.T @ np.linalg.inv(S)
        
        # Update state
        self.x = self.x + K @ y
        
        # Update covariance
        I = np.eye(self.state_dim)
        self.P = (I - K @ self.H) @ self.P
        
        # Return gain magnitude (how much we trust measurement)
        gain_magnitude = float(np.linalg.norm(K))
        
        return self.x.copy(), gain_magnitude
    
    def filter(self, measurement: float, dt: float = 1.0) -> Dict[str, Any]:
        """
        Complete predict-update cycle.
        """
        # Predict
        predicted = self.predict(dt)
        
        # Update
        z = np.array([measurement])
        updated, gain = self.update(z)
        
        return {
            "predicted_state": predicted,
            "updated_state": updated,
            "position": updated[0],
            "velocity": updated[1] if self.state_dim >= 2 else 0.0,
            "kalman_gain": gain,
            "innovation": measurement - predicted[0]
        }
    
    def get_state(self) -> StateVector:
        """Get current state estimate as StateVector."""
        return StateVector(
            position=self.x[0],
            velocity=self.x[1] if len(self.x) > 1 else 0.0,
            position_var=self.P[0, 0],
            velocity_var=self.P[1, 1] if len(self.x) > 1 else 0.0
        )
    
    def is_feint_detected(self, measurement: float, threshold: float = 3.0) -> bool:
        """
        Detect if measurement is likely a feint (deceptive signal).
        
        Uses Mahalanobis distance to check if measurement is outlier.
        """
        # Predicted measurement
        z_pred = self.H @ self.x
        
        # Innovation
        innovation = measurement - z_pred[0]
        
        # Innovation covariance
        S = float(self.H @ self.P @ self.H.T + self.R)
        
        # Mahalanobis distance
        d = abs(innovation) / math.sqrt(S)
        
        return d > threshold


# =============================================================================
# MONTE CARLO TREE SEARCH
# =============================================================================

class MCTSNode:
    """Node in Monte Carlo Tree Search."""
    
    def __init__(self, state: Any, parent: Optional[MCTSNode] = None,
                 action: Optional[str] = None):
        self.state = state
        self.parent = parent
        self.action = action
        
        # Statistics
        self.visits = 0
        self.wins = 0
        self.children: Dict[str, MCTSNode] = {}
    
    @property
    def win_rate(self) -> float:
        if self.visits == 0:
            return 0.0
        return self.wins / self.visits
    
    @property
    def ucb1(self) -> float:
        """Upper Confidence Bound for Trees (UCB1)."""
        if self.visits == 0:
            return float('inf')
        
        if self.parent is None or self.parent.visits == 0:
            return self.win_rate
        
        exploration = math.sqrt(2 * math.log(self.parent.visits) / self.visits)
        return self.win_rate + exploration
    
    def is_leaf(self) -> bool:
        return len(self.children) == 0
    
    def is_fully_expanded(self, actions: List[str]) -> bool:
        return len(self.children) == len(actions)


class MonteCarloTreeSearch:
    """
    Monte Carlo Tree Search for scenario modeling.
    
    Simulates N possible futures to find optimal action.
    """
    
    def __init__(self, 
                 get_actions: Callable[[Any], List[str]],
                 simulate_action: Callable[[Any, str], Any],
                 is_terminal: Callable[[Any], bool],
                 evaluate: Callable[[Any], float]):
        """
        Initialize MCTS.
        
        get_actions: Returns available actions from a state
        simulate_action: Returns new state after action
        is_terminal: Checks if state is terminal
        evaluate: Evaluates terminal state (1=win, 0=loss)
        """
        self.get_actions = get_actions
        self.simulate_action = simulate_action
        self.is_terminal = is_terminal
        self.evaluate = evaluate
    
    def search(self, initial_state: Any, 
               n_simulations: int = 1000) -> Dict[str, Any]:
        """
        Run MCTS from initial state.
        
        Returns best action and statistics.
        """
        root = MCTSNode(initial_state)
        
        for _ in range(n_simulations):
            # Selection
            node = self._select(root)
            
            # Expansion
            if not self.is_terminal(node.state):
                node = self._expand(node)
            
            # Simulation (rollout)
            result = self._simulate(node.state)
            
            # Backpropagation
            self._backpropagate(node, result)
        
        # Select best action
        best_child = max(root.children.values(), 
                        key=lambda n: n.visits) if root.children else None
        
        return {
            "best_action": best_child.action if best_child else None,
            "win_probability": best_child.win_rate if best_child else 0.0,
            "visits": root.visits,
            "children": {
                action: {
                    "visits": child.visits,
                    "win_rate": child.win_rate
                }
                for action, child in root.children.items()
            }
        }
    
    def _select(self, node: MCTSNode) -> MCTSNode:
        """Select best leaf node using UCB1."""
        while not node.is_leaf():
            # Select child with highest UCB1
            node = max(node.children.values(), key=lambda n: n.ucb1)
        return node
    
    def _expand(self, node: MCTSNode) -> MCTSNode:
        """Expand node by adding a child."""
        actions = self.get_actions(node.state)
        
        # Find untried actions
        untried = [a for a in actions if a not in node.children]
        
        if not untried:
            return node
        
        # Choose random untried action
        action = random.choice(untried)
        new_state = self.simulate_action(node.state, action)
        
        # Create child node
        child = MCTSNode(new_state, parent=node, action=action)
        node.children[action] = child
        
        return child
    
    def _simulate(self, state: Any, max_depth: int = 100) -> float:
        """Simulate random playout from state."""
        current = state
        depth = 0
        
        while not self.is_terminal(current) and depth < max_depth:
            actions = self.get_actions(current)
            if not actions:
                break
            action = random.choice(actions)
            current = self.simulate_action(current, action)
            depth += 1
        
        return self.evaluate(current)
    
    def _backpropagate(self, node: MCTSNode, result: float) -> None:
        """Backpropagate result up the tree."""
        while node is not None:
            node.visits += 1
            node.wins += result
            node = node.parent


# =============================================================================
# PRE-EMPTIVE INTERRUPT
# =============================================================================

@dataclass
class PredictedOutcome:
    """A predicted future outcome."""
    
    time_offset: float
    state: Any
    probability: float
    is_fatal: bool = False
    severity: float = 0.0  # 0 = benign, 1 = catastrophic
    
    @property
    def expected_cost(self) -> float:
        return self.probability * self.severity


class PreemptiveInterruptSystem:
    """
    System for detecting and preventing fatal outcomes.
    
    If simulation predicts fatal outcome at t+N, execute correction at t+1.
    """
    
    def __init__(self, 
                 predict_fn: Callable[[Any, float], PredictedOutcome],
                 correct_fn: Callable[[Any, PredictedOutcome], Any]):
        """
        Initialize interrupt system.
        
        predict_fn: Predicts outcome at time offset from state
        correct_fn: Returns corrected state given prediction
        """
        self.predict_fn = predict_fn
        self.correct_fn = correct_fn
        
        # Thresholds
        self.fatal_threshold = 0.8  # Severity above this is fatal
        self.action_threshold = 0.5  # Expected cost above this triggers action
        
        # Statistics
        self.predictions_made = 0
        self.interrupts_triggered = 0
    
    def scan_future(self, state: Any, 
                   horizons: List[float] = [1, 5, 10]) -> List[PredictedOutcome]:
        """Scan multiple future time horizons."""
        outcomes = []
        for t in horizons:
            outcome = self.predict_fn(state, t)
            outcome.time_offset = t
            outcomes.append(outcome)
            self.predictions_made += 1
        return outcomes
    
    def evaluate_threats(self, 
                        outcomes: List[PredictedOutcome]) -> Optional[PredictedOutcome]:
        """Identify most critical threat requiring action."""
        threats = [
            o for o in outcomes 
            if o.expected_cost > self.action_threshold or o.is_fatal
        ]
        
        if not threats:
            return None
        
        # Return most imminent critical threat
        return min(threats, key=lambda o: o.time_offset)
    
    def execute_interrupt(self, state: Any, 
                         threat: PredictedOutcome) -> Tuple[Any, Dict[str, Any]]:
        """
        Execute pre-emptive interrupt.
        
        Returns (corrected_state, action_report)
        """
        corrected = self.correct_fn(state, threat)
        self.interrupts_triggered += 1
        
        return corrected, {
            "threat_time": threat.time_offset,
            "threat_severity": threat.severity,
            "threat_probability": threat.probability,
            "was_fatal": threat.is_fatal,
            "interrupt_executed": True
        }
    
    def monitor(self, state: Any) -> Tuple[Any, Optional[Dict[str, Any]]]:
        """
        Monitor state and intervene if necessary.
        
        Returns (possibly_corrected_state, action_report_or_none)
        """
        # Scan future
        outcomes = self.scan_future(state)
        
        # Evaluate threats
        threat = self.evaluate_threats(outcomes)
        
        if threat:
            return self.execute_interrupt(state, threat)
        
        return state, None


# =============================================================================
# VALIDATION
# =============================================================================

def validate_predictive() -> bool:
    """Validate predictive analytics module."""
    
    # Test StateVector
    sv = StateVector(position=10.0, velocity=2.0, acceleration=0.1)
    future = sv.extrapolate(5.0)
    assert future.position > sv.position  # Should have moved forward
    
    # Test TaylorExtrapolator
    taylor = TaylorExtrapolator(order=2)
    for t in range(10):
        taylor.update(float(t), float(t * t))  # Quadratic motion
    
    # Predict future position
    pred = taylor.predict_position(1.0)
    assert pred > 0  # Should predict positive position
    
    # Test Kalman Filter
    kf = KalmanFilter(state_dim=2, obs_dim=1)
    
    # Feed noisy measurements of linear motion
    true_pos = 0.0
    for _ in range(10):
        true_pos += 1.0
        noisy = true_pos + np.random.normal(0, 0.1)
        result = kf.filter(noisy, dt=1.0)
        assert "position" in result
    
    # Test feint detection
    kf2 = KalmanFilter()
    for i in range(20):
        kf2.filter(float(i), 1.0)
    
    # Large deviation should be detected as potential feint
    is_feint = kf2.is_feint_detected(100.0)  # Way off
    assert is_feint
    
    # Test MCTS (simple game)
    def get_actions(state):
        if state >= 10:
            return []
        return ["add1", "add2"]
    
    def simulate(state, action):
        if action == "add1":
            return state + 1
        return state + 2
    
    def is_terminal(state):
        return state >= 10
    
    def evaluate(state):
        return 1.0 if state == 10 else 0.0
    
    mcts = MonteCarloTreeSearch(get_actions, simulate, is_terminal, evaluate)
    result = mcts.search(0, n_simulations=100)
    assert result["best_action"] is not None
    
    return True


if __name__ == "__main__":
    print("Validating Predictive Analytics Module...")
    assert validate_predictive()
    print("✓ Predictive Analytics Module validated")
    
    # Demo
    print("\n--- Predictive Analytics Demo ---")
    
    # Taylor Extrapolation
    print("\n1. Taylor Extrapolation:")
    taylor = TaylorExtrapolator()
    
    # Simulate accelerating object
    for t in range(20):
        pos = 0.5 * t * t  # x = 0.5 * t²
        taylor.update(float(t), pos)
    
    state = taylor.estimate_derivatives()
    print(f"   Position: {state.position:.2f}")
    print(f"   Velocity: {state.velocity:.2f}")
    print(f"   Acceleration: {state.acceleration:.2f}")
    
    future = taylor.extrapolate(5.0)
    print(f"   Predicted position at t+5: {future.position:.2f}")
    
    # Kalman Filter
    print("\n2. Kalman Filter:")
    kf = KalmanFilter()
    
    print("   Tracking noisy linear motion...")
    true_positions = []
    estimated_positions = []
    
    for i in range(20):
        true_pos = float(i)
        noisy = true_pos + np.random.normal(0, 0.5)
        result = kf.filter(noisy, dt=1.0)
        
        true_positions.append(true_pos)
        estimated_positions.append(result["position"])
    
    print(f"   Final true position: {true_positions[-1]:.2f}")
    print(f"   Final estimate: {estimated_positions[-1]:.2f}")
    print(f"   Final Kalman gain: {result['kalman_gain']:.3f}")
    
    # MCTS
    print("\n3. Monte Carlo Tree Search:")
    
    def get_actions(state):
        if state >= 10: return []
        return ["conservative", "aggressive"]
    
    def simulate(state, action):
        if action == "conservative":
            return state + random.randint(1, 2)
        return state + random.randint(1, 4)
    
    def is_terminal(state):
        return state >= 10
    
    def evaluate(state):
        if state == 10: return 1.0
        if state > 10: return 0.5
        return 0.0
    
    mcts = MonteCarloTreeSearch(get_actions, simulate, is_terminal, evaluate)
    result = mcts.search(0, n_simulations=500)
    
    print(f"   Best action: {result['best_action']}")
    print(f"   Win probability: {result['win_probability']:.2%}")
    print(f"   Action statistics:")
    for action, stats in result["children"].items():
        print(f"     {action}: {stats['visits']} visits, "
              f"{stats['win_rate']:.2%} win rate")
