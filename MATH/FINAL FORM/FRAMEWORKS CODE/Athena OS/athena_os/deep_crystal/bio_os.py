"""
ATHENA OS - BIO-OS CONTROL LOOPS
================================
Agent Dynamics and Feedback Control

From DEEP_CRYSTAL_SYNTHESIS.docx Chapter 3:

SEED: Local Control Loops (Bio-OS)

3.1.1 Stoicism as Feedback Control (u vs d)
    - Separate controllables (u) from disturbances (d)
    - Virtue → control policy mapping
    - Robustness margins and actuator limits

3.1.2 PID Controller in Emotional Regulation
    - Emotion regulation as PID
    - Rumination → integral windup
    - Tune gains via practice

3.1.3 Witness as Kalman Filter (state estimation)
    - Observing mind estimates hidden state
    - Mindfulness → filtering mapping
    - Minimum-variance estimation

3.1.4 Suffering as Error Signal
    - Suffering = control error E(t) = setpoint - actual
    - Craving → setpoint shift
    - Error-energy relation
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Callable, Any
from enum import Enum, auto
from abc import ABC, abstractmethod
import numpy as np


# =============================================================================
# STOIC CONTROL FRAMEWORK
# =============================================================================

class ControlType(Enum):
    """Classification of inputs."""
    
    CONTROLLABLE = "u"      # Things we can control (actions)
    DISTURBANCE = "d"       # Things we cannot control (externals)
    UNCERTAIN = "?"         # Requires classification


@dataclass
class StoicPartition:
    """
    Stoic partition of inputs into controllable (u) and disturbances (d).
    
    Key insight: Separate what we can control from what we cannot.
    """
    
    controllables: List[str] = field(default_factory=list)
    disturbances: List[str] = field(default_factory=list)
    uncertain: List[str] = field(default_factory=list)
    
    def classify(self, input_name: str, 
                control_test: Callable[[str], bool]) -> ControlType:
        """
        Classify an input as controllable or disturbance.
        
        control_test: Returns True if input is controllable.
        """
        if control_test(input_name):
            self.controllables.append(input_name)
            return ControlType.CONTROLLABLE
        else:
            self.disturbances.append(input_name)
            return ControlType.DISTURBANCE
    
    def robustness_margin(self) -> float:
        """
        Compute robustness margin.
        
        Higher ratio of controllables to disturbances = more robust.
        """
        total = len(self.controllables) + len(self.disturbances)
        if total == 0:
            return 1.0
        return len(self.controllables) / total


class VirtuePolicy:
    """
    Virtue → Control Policy mapping.
    
    Each virtue defines a policy for handling disturbances.
    """
    
    def __init__(self):
        self._policies: Dict[str, Callable[[np.ndarray, np.ndarray], np.ndarray]] = {}
        self._add_cardinal_virtues()
    
    def _add_cardinal_virtues(self):
        """Add Stoic cardinal virtue policies."""
        
        # Wisdom: Optimal estimation and decision
        def wisdom_policy(state: np.ndarray, disturbance: np.ndarray) -> np.ndarray:
            return -0.5 * state  # Move toward equilibrium
        self._policies["wisdom"] = wisdom_policy
        
        # Courage: Bold action despite uncertainty
        def courage_policy(state: np.ndarray, disturbance: np.ndarray) -> np.ndarray:
            return -1.0 * state  # Stronger correction
        self._policies["courage"] = courage_policy
        
        # Temperance: Moderated response
        def temperance_policy(state: np.ndarray, disturbance: np.ndarray) -> np.ndarray:
            return -0.3 * state  # Gentle correction
        self._policies["temperance"] = temperance_policy
        
        # Justice: Balanced consideration
        def justice_policy(state: np.ndarray, disturbance: np.ndarray) -> np.ndarray:
            return -0.5 * (state + 0.1 * disturbance)  # Account for externals
        self._policies["justice"] = justice_policy
    
    def apply(self, virtue: str, state: np.ndarray, 
              disturbance: np.ndarray) -> np.ndarray:
        """Apply virtue policy to compute control action."""
        if virtue in self._policies:
            return self._policies[virtue](state, disturbance)
        return np.zeros_like(state)
    
    def add_policy(self, virtue: str, 
                   policy: Callable[[np.ndarray, np.ndarray], np.ndarray]) -> None:
        """Add custom virtue policy."""
        self._policies[virtue] = policy


@dataclass
class StoicController:
    """
    Stoic feedback controller.
    
    Separates controllables from disturbances and applies virtue policies.
    """
    
    partition: StoicPartition
    policy: VirtuePolicy
    
    # Actuator limits
    u_min: float = -10.0
    u_max: float = 10.0
    
    # Robustness margin target
    margin_target: float = 0.5
    
    def control(self, state: np.ndarray, disturbance: np.ndarray,
                virtue: str = "wisdom") -> np.ndarray:
        """
        Compute control action.
        
        u = policy(state, d) clamped to actuator limits
        """
        u = self.policy.apply(virtue, state, disturbance)
        
        # Clamp to actuator limits
        u = np.clip(u, self.u_min, self.u_max)
        
        return u
    
    def is_robust(self) -> bool:
        """Check if robustness margin meets target."""
        return self.partition.robustness_margin() >= self.margin_target


# =============================================================================
# PID EMOTIONAL REGULATION
# =============================================================================

@dataclass
class PIDGains:
    """PID controller gains."""
    
    Kp: float = 1.0   # Proportional gain
    Ki: float = 0.1   # Integral gain
    Kd: float = 0.05  # Derivative gain
    
    # Anti-windup limits
    integral_min: float = -10.0
    integral_max: float = 10.0


class EmotionalPIDController:
    """
    PID Controller for Emotional Regulation.
    
    Emotion = actual state
    Setpoint = desired emotional state
    Error = setpoint - actual
    
    Rumination = integral windup (accumulating past errors)
    Overreaction = high proportional gain
    Anticipatory anxiety = excessive derivative term
    """
    
    def __init__(self, gains: PIDGains = None):
        self.gains = gains or PIDGains()
        
        # State
        self._integral = 0.0
        self._last_error = 0.0
        self._last_time = 0.0
    
    def reset(self) -> None:
        """Reset controller state."""
        self._integral = 0.0
        self._last_error = 0.0
        self._last_time = 0.0
    
    def compute(self, setpoint: float, actual: float, 
                dt: float = 1.0) -> Tuple[float, Dict[str, float]]:
        """
        Compute PID control output.
        
        Returns (control_output, components)
        """
        error = setpoint - actual
        
        # Proportional term
        P = self.gains.Kp * error
        
        # Integral term (with anti-windup)
        self._integral += error * dt
        self._integral = np.clip(
            self._integral, 
            self.gains.integral_min, 
            self.gains.integral_max
        )
        I = self.gains.Ki * self._integral
        
        # Derivative term
        if dt > 0:
            derivative = (error - self._last_error) / dt
        else:
            derivative = 0.0
        D = self.gains.Kd * derivative
        
        # Update state
        self._last_error = error
        
        output = P + I + D
        
        components = {
            "error": error,
            "P": P,
            "I": I,
            "D": D,
            "integral_state": self._integral,
            "output": output
        }
        
        return output, components
    
    def has_integral_windup(self, threshold: float = 5.0) -> bool:
        """
        Check for integral windup (rumination).
        
        High integral state indicates accumulated past errors.
        """
        return abs(self._integral) > threshold
    
    def tune_gains(self, settling_time: float, overshoot: float) -> None:
        """
        Tune gains based on desired settling time and overshoot.
        
        Simplified Ziegler-Nichols-like tuning.
        """
        # Faster settling → higher gains
        speed_factor = 1.0 / max(settling_time, 0.1)
        
        # Lower overshoot → lower proportional gain
        overshoot_factor = 1.0 - overshoot
        
        self.gains.Kp = 1.0 * speed_factor * overshoot_factor
        self.gains.Ki = 0.1 * speed_factor
        self.gains.Kd = 0.05 * speed_factor


@dataclass
class EmotionalState:
    """Emotional state vector."""
    
    valence: float = 0.0      # Positive/negative (-1 to 1)
    arousal: float = 0.0       # Calm/excited (-1 to 1)
    dominance: float = 0.0     # Submissive/dominant (-1 to 1)
    
    def to_array(self) -> np.ndarray:
        return np.array([self.valence, self.arousal, self.dominance])
    
    @classmethod
    def from_array(cls, arr: np.ndarray) -> 'EmotionalState':
        return cls(valence=arr[0], arousal=arr[1], dominance=arr[2])
    
    def magnitude(self) -> float:
        """Emotional intensity."""
        return np.linalg.norm(self.to_array())


class EmotionalRegulator:
    """
    Complete emotional regulation system with PID control.
    """
    
    def __init__(self):
        self._controllers = {
            "valence": EmotionalPIDController(),
            "arousal": EmotionalPIDController(),
            "dominance": EmotionalPIDController()
        }
        self._setpoints = EmotionalState(0.0, 0.0, 0.0)  # Neutral
        self._history: List[EmotionalState] = []
    
    def set_target(self, target: EmotionalState) -> None:
        """Set target emotional state."""
        self._setpoints = target
    
    def regulate(self, current: EmotionalState, 
                 dt: float = 1.0) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Regulate emotion toward setpoint.
        
        Returns (regulation_signal, diagnostics)
        """
        self._history.append(current)
        
        outputs = []
        diagnostics = {}
        
        # Regulate each dimension
        for dim in ["valence", "arousal", "dominance"]:
            actual = getattr(current, dim)
            setpoint = getattr(self._setpoints, dim)
            
            output, components = self._controllers[dim].compute(setpoint, actual, dt)
            outputs.append(output)
            diagnostics[dim] = components
        
        # Check for issues
        diagnostics["rumination"] = any(
            c.has_integral_windup() for c in self._controllers.values()
        )
        diagnostics["variance"] = np.var([s.magnitude() for s in self._history[-10:]])
        
        return np.array(outputs), diagnostics
    
    def settling_time(self, threshold: float = 0.1) -> float:
        """Estimate settling time from history."""
        if len(self._history) < 2:
            return float('inf')
        
        # Find when we last exceeded threshold from setpoint
        for i in range(len(self._history) - 1, -1, -1):
            error = np.linalg.norm(
                self._history[i].to_array() - self._setpoints.to_array()
            )
            if error > threshold:
                return len(self._history) - i
        
        return 0.0


# =============================================================================
# KALMAN FILTER (WITNESS/OBSERVER)
# =============================================================================

@dataclass
class KalmanParameters:
    """Parameters for Kalman filter."""
    
    # State transition matrix
    A: np.ndarray = field(default_factory=lambda: np.eye(2))
    
    # Observation matrix
    H: np.ndarray = field(default_factory=lambda: np.eye(2))
    
    # Process noise covariance
    Q: np.ndarray = field(default_factory=lambda: 0.1 * np.eye(2))
    
    # Observation noise covariance
    R: np.ndarray = field(default_factory=lambda: 0.5 * np.eye(2))


class WitnessFilter:
    """
    Kalman Filter as "Witness" (mindful observation).
    
    The observing mind estimates hidden internal state from
    noisy observations (interoception, thoughts, emotions).
    
    Key mapping:
    - Hidden state: True internal condition
    - Observations: Sensory signals, thoughts, feelings
    - Prediction: Mental model of self
    - Update: Integration of new information
    - Estimation error: Gap between model and reality
    """
    
    def __init__(self, dim: int = 2, params: KalmanParameters = None):
        self.dim = dim
        self.params = params or KalmanParameters(
            A=np.eye(dim),
            H=np.eye(dim),
            Q=0.1 * np.eye(dim),
            R=0.5 * np.eye(dim)
        )
        
        # State estimate
        self._x = np.zeros(dim)
        
        # Estimate covariance
        self._P = np.eye(dim)
        
        # History for diagnostics
        self._observation_history: List[np.ndarray] = []
        self._estimate_history: List[np.ndarray] = []
        self._error_history: List[float] = []
    
    def predict(self) -> np.ndarray:
        """
        Prediction step.
        
        x_pred = A * x
        P_pred = A * P * A^T + Q
        """
        A, Q = self.params.A, self.params.Q
        
        self._x = A @ self._x
        self._P = A @ self._P @ A.T + Q
        
        return self._x.copy()
    
    def update(self, observation: np.ndarray) -> np.ndarray:
        """
        Update step with new observation.
        
        K = P * H^T * (H * P * H^T + R)^{-1}
        x = x + K * (z - H * x)
        P = (I - K * H) * P
        """
        H, R = self.params.H, self.params.R
        
        # Innovation (measurement residual)
        y = observation - H @ self._x
        
        # Innovation covariance
        S = H @ self._P @ H.T + R
        
        # Kalman gain
        K = self._P @ H.T @ np.linalg.inv(S)
        
        # Update state estimate
        self._x = self._x + K @ y
        
        # Update covariance
        I = np.eye(self.dim)
        self._P = (I - K @ H) @ self._P
        
        # Record history
        self._observation_history.append(observation.copy())
        self._estimate_history.append(self._x.copy())
        self._error_history.append(np.linalg.norm(y))
        
        return self._x.copy()
    
    def step(self, observation: np.ndarray) -> np.ndarray:
        """Complete predict-update cycle."""
        self.predict()
        return self.update(observation)
    
    @property
    def state_estimate(self) -> np.ndarray:
        """Current state estimate."""
        return self._x.copy()
    
    @property
    def estimation_uncertainty(self) -> float:
        """Estimation uncertainty (trace of covariance)."""
        return np.trace(self._P)
    
    def calibration_error(self, n_recent: int = 10) -> float:
        """
        Measure calibration error.
        
        Good observer: prediction errors match expected uncertainty.
        """
        if len(self._error_history) < n_recent:
            return float('inf')
        
        recent_errors = self._error_history[-n_recent:]
        expected_error = np.sqrt(np.trace(self.params.R))
        
        return abs(np.mean(recent_errors) - expected_error)
    
    def is_dissociated(self, threshold: float = 2.0) -> bool:
        """
        Check for dissociation.
        
        High uncertainty + high errors = disconnected from observations.
        """
        if len(self._error_history) < 5:
            return False
        
        recent_error = np.mean(self._error_history[-5:])
        return recent_error > threshold * self.estimation_uncertainty


# =============================================================================
# SUFFERING AS ERROR SIGNAL
# =============================================================================

@dataclass
class Setpoint:
    """
    Desired state setpoint.
    
    Suffering arises when actual state differs from setpoint.
    """
    
    name: str
    value: float
    
    # Setpoint dynamics
    adaptive: bool = False
    adaptation_rate: float = 0.01
    
    def adapt(self, actual: float) -> None:
        """Adapt setpoint toward actual (hedonic adaptation)."""
        if self.adaptive:
            self.value += self.adaptation_rate * (actual - self.value)


class SufferingModel:
    """
    Suffering as Error Signal.
    
    E(t) = setpoint - actual
    
    Key insights:
    - Suffering = control error
    - Craving = upward setpoint shift
    - Aversion = error from negative states
    - Attachment = rigid setpoints
    """
    
    def __init__(self):
        self._setpoints: Dict[str, Setpoint] = {}
        self._error_history: List[float] = []
    
    def add_setpoint(self, name: str, value: float, 
                     adaptive: bool = False) -> None:
        """Add a setpoint."""
        self._setpoints[name] = Setpoint(name, value, adaptive)
    
    def compute_error(self, name: str, actual: float) -> float:
        """
        Compute error for a setpoint.
        
        E = setpoint - actual
        """
        if name not in self._setpoints:
            return 0.0
        
        sp = self._setpoints[name]
        error = sp.value - actual
        
        # Adapt setpoint if enabled
        sp.adapt(actual)
        
        return error
    
    def total_suffering(self, actuals: Dict[str, float]) -> float:
        """
        Compute total suffering from all setpoints.
        
        S = Σ |E_i|² (quadratic error)
        """
        total = 0.0
        for name, actual in actuals.items():
            error = self.compute_error(name, actual)
            total += error ** 2
        
        self._error_history.append(total)
        return total
    
    def chronic_suffering(self, n_recent: int = 10) -> float:
        """Measure chronic suffering (persistent error)."""
        if len(self._error_history) < n_recent:
            return 0.0
        return np.mean(self._error_history[-n_recent:])
    
    def reduce_attachment(self, name: str, rate: float = 0.1) -> None:
        """
        Reduce attachment by increasing setpoint adaptivity.
        
        More adaptive setpoints = less chronic suffering.
        """
        if name in self._setpoints:
            self._setpoints[name].adaptive = True
            self._setpoints[name].adaptation_rate = rate
    
    def shift_setpoint(self, name: str, delta: float) -> None:
        """
        Shift setpoint (craving/aversion).
        
        Craving: delta > 0 (want more)
        Aversion: delta < 0 (want less)
        """
        if name in self._setpoints:
            self._setpoints[name].value += delta
    
    def multi_objective_conflict(self) -> float:
        """
        Measure conflict between multiple setpoints.
        
        Conflict arises when satisfying one setpoint worsens another.
        """
        if len(self._setpoints) < 2:
            return 0.0
        
        # Simplified: variance in setpoint values
        values = [sp.value for sp in self._setpoints.values()]
        return np.var(values)


# =============================================================================
# INTEGRATED BIO-OS CONTROLLER
# =============================================================================

class BioOSController:
    """
    Complete Bio-OS control system integrating all components.
    
    - Stoic partition of u/d
    - PID emotional regulation
    - Kalman witness filtering
    - Suffering error model
    """
    
    def __init__(self, state_dim: int = 3):
        self.state_dim = state_dim
        
        # Components
        self.stoic = StoicController(
            partition=StoicPartition(),
            policy=VirtuePolicy()
        )
        self.regulator = EmotionalRegulator()
        self.witness = WitnessFilter(dim=state_dim)
        self.suffering = SufferingModel()
        
        # State
        self._current_state = np.zeros(state_dim)
        self._control_history: List[np.ndarray] = []
    
    def initialize_setpoints(self, names: List[str], 
                            values: List[float]) -> None:
        """Initialize suffering model setpoints."""
        for name, value in zip(names, values):
            self.suffering.add_setpoint(name, value)
    
    def step(self, observation: np.ndarray, 
             disturbance: np.ndarray) -> Dict[str, Any]:
        """
        Execute one step of Bio-OS control.
        
        1. Witness observes and estimates state
        2. Stoic partitions inputs
        3. PID computes regulation
        4. Suffering model evaluates error
        """
        # 1. Witness estimates hidden state
        estimated_state = self.witness.step(observation)
        
        # 2. Stoic control
        control = self.stoic.control(estimated_state, disturbance, "wisdom")
        
        # 3. Emotional regulation (using first 3 dims)
        if len(observation) >= 3:
            emotional = EmotionalState.from_array(observation[:3])
            reg_signal, reg_diag = self.regulator.regulate(emotional)
        else:
            reg_signal = np.zeros(3)
            reg_diag = {}
        
        # 4. Suffering evaluation
        actuals = {f"dim_{i}": observation[i] for i in range(len(observation))}
        total_suffering = self.suffering.total_suffering(actuals)
        
        # Update state
        self._current_state = estimated_state
        self._control_history.append(control)
        
        return {
            "estimated_state": estimated_state,
            "control": control,
            "regulation": reg_signal,
            "suffering": total_suffering,
            "witness_uncertainty": self.witness.estimation_uncertainty,
            "rumination": self.regulator._controllers["valence"].has_integral_windup(),
            "dissociated": self.witness.is_dissociated(),
            "robustness": self.stoic.partition.robustness_margin()
        }
    
    def diagnose(self) -> Dict[str, Any]:
        """Generate diagnostic report."""
        return {
            "chronic_suffering": self.suffering.chronic_suffering(),
            "calibration_error": self.witness.calibration_error(),
            "multi_objective_conflict": self.suffering.multi_objective_conflict(),
            "settling_time": self.regulator.settling_time(),
            "is_robust": self.stoic.is_robust()
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_bio_os() -> bool:
    """Validate Bio-OS control loops module."""
    
    # Test Stoic partition
    partition = StoicPartition()
    
    def can_control(x: str) -> bool:
        return x.startswith("my_")
    
    assert partition.classify("my_action", can_control) == ControlType.CONTROLLABLE
    assert partition.classify("external_event", can_control) == ControlType.DISTURBANCE
    assert partition.robustness_margin() == 0.5
    
    # Test virtue policy
    policy = VirtuePolicy()
    state = np.array([1.0, 2.0])
    dist = np.array([0.5, 0.5])
    
    action = policy.apply("wisdom", state, dist)
    assert len(action) == 2
    
    # Test Stoic controller
    controller = StoicController(partition, policy)
    u = controller.control(state, dist, "courage")
    assert np.all(u >= controller.u_min)
    assert np.all(u <= controller.u_max)
    
    # Test PID
    pid = EmotionalPIDController()
    output, components = pid.compute(setpoint=0.0, actual=1.0, dt=1.0)
    assert "P" in components
    assert "I" in components
    assert "D" in components
    
    # Test integral windup
    for _ in range(100):
        pid.compute(setpoint=10.0, actual=0.0, dt=1.0)
    assert pid.has_integral_windup()
    
    # Test emotional regulator
    regulator = EmotionalRegulator()
    current = EmotionalState(valence=0.5, arousal=0.3, dominance=0.1)
    signal, diag = regulator.regulate(current)
    assert len(signal) == 3
    
    # Test Kalman witness
    witness = WitnessFilter(dim=2)
    obs = np.array([1.0, 2.0])
    estimate = witness.step(obs)
    assert len(estimate) == 2
    assert witness.estimation_uncertainty > 0
    
    # Test suffering model
    suffering = SufferingModel()
    suffering.add_setpoint("pleasure", 1.0)
    suffering.add_setpoint("status", 0.5)
    
    error = suffering.compute_error("pleasure", 0.5)
    assert error == 0.5  # 1.0 - 0.5
    
    total = suffering.total_suffering({"pleasure": 0.5, "status": 0.3})
    assert total > 0
    
    # Test integrated controller
    bio_os = BioOSController(state_dim=3)
    bio_os.initialize_setpoints(["dim_0", "dim_1", "dim_2"], [0.0, 0.0, 0.0])
    
    result = bio_os.step(
        observation=np.array([0.1, 0.2, 0.3]),
        disturbance=np.array([0.05, 0.05, 0.05])
    )
    
    assert "estimated_state" in result
    assert "control" in result
    assert "suffering" in result
    
    diag = bio_os.diagnose()
    assert "chronic_suffering" in diag
    
    return True


if __name__ == "__main__":
    print("Validating Bio-OS Control Loops...")
    assert validate_bio_os()
    print("✓ Bio-OS Control Loops validated")
