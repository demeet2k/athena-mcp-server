"""
ATHENA OS - HDCS: CONTROLLER OPERATORS
======================================
Control Laws and Optimization

THE CONTROLLER (Ĉ):
    Processes error signal to generate control input u(t).
    
    PID Control Law:
    u(t) = K_p·e(t) + K_i·∫e(τ)dτ + K_d·de/dt

REFERENCE TRAJECTORY:
    The "Optimal Path" (L_opt) is defined as the geodesic trajectory
    on the Ma'at-Manifold (ideal configuration space).
    
    Error Vector: e(t) = r_ref(t) - ŷ(t)

LQR CONTROLLER:
    Minimizes infinite horizon cost:
    J = E[∫₀^∞ (xᵀQx + uᵀRu) dt]
    
    Optimal control: u*(t) = -Kx̂(t)
    Where K = R⁻¹BᵀS (S solves Algebraic Riccati Equation)

STABILITY CONDITION:
    All roots s of characteristic equation must satisfy Re(s) < 0
    for global asymptotic stability.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Callable, Any
from enum import Enum, auto
import numpy as np
from scipy import linalg


# =============================================================================
# CONTROLLER TYPES
# =============================================================================

class ControllerType(Enum):
    """Types of controllers."""
    
    P = "proportional"
    PI = "proportional_integral"
    PD = "proportional_derivative"
    PID = "pid"
    LQR = "lqr"
    LQG = "lqg"
    MPC = "model_predictive"


class StabilityStatus(Enum):
    """System stability status."""
    
    STABLE = "stable"               # All poles in LHP
    MARGINALLY_STABLE = "marginal"  # Poles on imaginary axis
    UNSTABLE = "unstable"           # Poles in RHP
    BIFURCATION = "bifurcation"     # At stability boundary


# =============================================================================
# REFERENCE TRAJECTORY
# =============================================================================

class ReferenceTrajectory:
    """
    Reference Trajectory r_ref(t).
    
    The "Optimal Path" on the configuration manifold.
    Defines the target state the system should track.
    """
    
    def __init__(self, dimension: int = 1,
                 trajectory_type: str = "constant"):
        self.dimension = dimension
        self.trajectory_type = trajectory_type
        
        # Trajectory parameters
        self._setpoint = np.zeros(dimension)
        self._amplitude = np.ones(dimension)
        self._frequency = np.ones(dimension)
        self._phase = np.zeros(dimension)
    
    def evaluate(self, t: float) -> np.ndarray:
        """
        Evaluate reference at time t.
        
        r_ref(t) = setpoint + amplitude * signal(ωt + φ)
        """
        if self.trajectory_type == "constant":
            return self._setpoint.copy()
        
        elif self.trajectory_type == "sinusoidal":
            return self._setpoint + self._amplitude * np.sin(
                self._frequency * t + self._phase)
        
        elif self.trajectory_type == "step":
            return self._setpoint * (1 if t >= 0 else 0)
        
        elif self.trajectory_type == "ramp":
            return self._setpoint * t
        
        elif self.trajectory_type == "exponential":
            return self._setpoint * (1 - np.exp(-t))
        
        return self._setpoint.copy()
    
    def derivative(self, t: float) -> np.ndarray:
        """Compute reference derivative dr/dt."""
        if self.trajectory_type == "constant":
            return np.zeros(self.dimension)
        
        elif self.trajectory_type == "sinusoidal":
            return self._amplitude * self._frequency * np.cos(
                self._frequency * t + self._phase)
        
        elif self.trajectory_type == "ramp":
            return self._setpoint.copy()
        
        elif self.trajectory_type == "exponential":
            return self._setpoint * np.exp(-t)
        
        return np.zeros(self.dimension)
    
    def set_setpoint(self, setpoint: np.ndarray) -> None:
        """Set reference setpoint."""
        self._setpoint = np.atleast_1d(setpoint).astype(float)
        self.dimension = len(self._setpoint)
    
    def set_parameters(self, amplitude: np.ndarray = None,
                      frequency: np.ndarray = None,
                      phase: np.ndarray = None) -> None:
        """Set trajectory parameters."""
        if amplitude is not None:
            self._amplitude = np.atleast_1d(amplitude)
        if frequency is not None:
            self._frequency = np.atleast_1d(frequency)
        if phase is not None:
            self._phase = np.atleast_1d(phase)


# =============================================================================
# ERROR VECTOR
# =============================================================================

@dataclass
class ErrorVector:
    """
    Error Vector e(t) = r_ref(t) - ŷ(t).
    
    Represents the divergence of estimated state from reference.
    A non-zero norm ||e|| > 0 indicates system drift (Isfet-Flux).
    """
    
    dimension: int = 1
    
    # Error components
    _current: np.ndarray = field(default=None)
    _integral: np.ndarray = field(default=None)
    _derivative: np.ndarray = field(default=None)
    _previous: np.ndarray = field(default=None)
    
    def __post_init__(self):
        self._current = np.zeros(self.dimension)
        self._integral = np.zeros(self.dimension)
        self._derivative = np.zeros(self.dimension)
        self._previous = np.zeros(self.dimension)
    
    def update(self, reference: np.ndarray, measurement: np.ndarray,
               dt: float = 1.0) -> np.ndarray:
        """
        Update error vector.
        
        e(t) = r_ref(t) - ŷ(t)
        """
        reference = np.atleast_1d(reference)
        measurement = np.atleast_1d(measurement)
        
        # Store previous
        self._previous = self._current.copy()
        
        # Current error
        self._current = reference - measurement
        
        # Integral (trapezoidal rule)
        self._integral += 0.5 * (self._current + self._previous) * dt
        
        # Derivative
        if dt > 0:
            self._derivative = (self._current - self._previous) / dt
        
        return self._current.copy()
    
    def reset(self) -> None:
        """Reset error accumulator."""
        self._current = np.zeros(self.dimension)
        self._integral = np.zeros(self.dimension)
        self._derivative = np.zeros(self.dimension)
        self._previous = np.zeros(self.dimension)
    
    @property
    def current(self) -> np.ndarray:
        return self._current.copy()
    
    @property
    def integral(self) -> np.ndarray:
        return self._integral.copy()
    
    @property
    def derivative(self) -> np.ndarray:
        return self._derivative.copy()
    
    @property
    def norm(self) -> float:
        return float(np.linalg.norm(self._current))


# =============================================================================
# PID CONTROLLER
# =============================================================================

class PIDController:
    """
    Proportional-Integral-Derivative Controller.
    
    Control Law:
    u(t) = K_p·e(t) + K_i·∫e(τ)dτ + K_d·de/dt
    
    Gain Tuning:
    - K_p (Proportional): Restoring Force (Spring Constant)
    - K_i (Integral): Drift Correction (Bias Removal)
    - K_d (Derivative): Damping (Viscosity)
    """
    
    def __init__(self, dimension: int = 1,
                 Kp: float = 1.0,
                 Ki: float = 0.1,
                 Kd: float = 0.01):
        self.dimension = dimension
        
        # Gain matrices (allow different gains per dimension)
        self.Kp = Kp * np.eye(dimension) if np.isscalar(Kp) else np.diag(Kp)
        self.Ki = Ki * np.eye(dimension) if np.isscalar(Ki) else np.diag(Ki)
        self.Kd = Kd * np.eye(dimension) if np.isscalar(Kd) else np.diag(Kd)
        
        # Error tracking
        self.error = ErrorVector(dimension)
        
        # Anti-windup limits
        self._integral_limit = 100.0
        
        # Output limits
        self._output_min = -float('inf')
        self._output_max = float('inf')
    
    def compute(self, reference: np.ndarray, measurement: np.ndarray,
                dt: float = 1.0) -> np.ndarray:
        """
        Compute control output.
        
        u = K_p·e + K_i·∫e dt + K_d·de/dt
        """
        # Update error
        self.error.update(reference, measurement, dt)
        
        # Anti-windup: limit integral
        integral = np.clip(self.error.integral, 
                          -self._integral_limit, 
                          self._integral_limit)
        
        # PID terms
        P_term = self.Kp @ self.error.current
        I_term = self.Ki @ integral
        D_term = self.Kd @ self.error.derivative
        
        # Total control output
        u = P_term + I_term + D_term
        
        # Output limiting
        u = np.clip(u, self._output_min, self._output_max)
        
        return u
    
    def set_gains(self, Kp: float = None, Ki: float = None, 
                  Kd: float = None) -> None:
        """Set controller gains."""
        if Kp is not None:
            self.Kp = Kp * np.eye(self.dimension)
        if Ki is not None:
            self.Ki = Ki * np.eye(self.dimension)
        if Kd is not None:
            self.Kd = Kd * np.eye(self.dimension)
    
    def set_limits(self, integral_limit: float = None,
                   output_min: float = None,
                   output_max: float = None) -> None:
        """Set controller limits."""
        if integral_limit is not None:
            self._integral_limit = integral_limit
        if output_min is not None:
            self._output_min = output_min
        if output_max is not None:
            self._output_max = output_max
    
    def reset(self) -> None:
        """Reset controller state."""
        self.error.reset()
    
    def get_status(self) -> Dict:
        """Get controller status."""
        return {
            "type": ControllerType.PID.value,
            "Kp": np.diag(self.Kp).tolist(),
            "Ki": np.diag(self.Ki).tolist(),
            "Kd": np.diag(self.Kd).tolist(),
            "error_norm": self.error.norm,
            "integral_norm": float(np.linalg.norm(self.error.integral))
        }


# =============================================================================
# LQR CONTROLLER
# =============================================================================

class LQRController:
    """
    Linear Quadratic Regulator.
    
    Minimizes cost functional:
    J = E[∫₀^∞ (xᵀQx + uᵀRu) dt]
    
    Where:
    - xᵀQx: Penalty for deviation from Order
    - uᵀRu: Penalty for excessive intervention
    
    Optimal control law: u*(t) = -Kx̂(t)
    Where K = R⁻¹BᵀS (S solves Algebraic Riccati Equation)
    """
    
    def __init__(self, A: np.ndarray, B: np.ndarray,
                 Q: np.ndarray = None, R: np.ndarray = None):
        """
        Initialize LQR controller.
        
        Args:
            A: State matrix (n x n)
            B: Input matrix (n x m)
            Q: State cost matrix (n x n)
            R: Input cost matrix (m x m)
        """
        self.A = np.atleast_2d(A)
        self.B = np.atleast_2d(B)
        
        self.n = self.A.shape[0]  # State dimension
        self.m = self.B.shape[1]  # Input dimension
        
        # Cost matrices
        self.Q = Q if Q is not None else np.eye(self.n)
        self.R = R if R is not None else np.eye(self.m)
        
        # Solution matrices
        self._S = None  # Riccati solution
        self._K = None  # Optimal gain
        
        # Solve
        self._solve_riccati()
    
    def _solve_riccati(self) -> None:
        """
        Solve Algebraic Riccati Equation (ARE).
        
        AᵀS + SA - SBR⁻¹BᵀS + Q = 0
        """
        try:
            self._S = linalg.solve_continuous_are(self.A, self.B, self.Q, self.R)
            self._K = np.linalg.inv(self.R) @ self.B.T @ self._S
        except Exception:
            # Fallback: simple pole placement
            self._S = np.eye(self.n)
            self._K = np.ones((self.m, self.n)) * 0.1
    
    def compute(self, state: np.ndarray) -> np.ndarray:
        """
        Compute optimal control.
        
        u*(t) = -Kx̂(t)
        """
        state = np.atleast_1d(state)
        return -self._K @ state
    
    def cost(self, state: np.ndarray, control: np.ndarray) -> float:
        """
        Compute instantaneous cost.
        
        L(x, u) = xᵀQx + uᵀRu
        """
        state = np.atleast_1d(state)
        control = np.atleast_1d(control)
        
        state_cost = float(state @ self.Q @ state)
        control_cost = float(control @ self.R @ control)
        
        return state_cost + control_cost
    
    def closed_loop_poles(self) -> np.ndarray:
        """
        Get closed-loop system poles.
        
        Eigenvalues of (A - BK)
        """
        A_cl = self.A - self.B @ self._K
        return np.linalg.eigvals(A_cl)
    
    def is_stable(self) -> bool:
        """Check if closed-loop system is stable."""
        poles = self.closed_loop_poles()
        return bool(np.all(np.real(poles) < 0))
    
    def stability_margin(self) -> float:
        """
        Compute stability margin.
        
        max(Re(λ)) for closed-loop poles
        """
        poles = self.closed_loop_poles()
        return float(-np.max(np.real(poles)))
    
    @property
    def gain(self) -> np.ndarray:
        return self._K.copy()
    
    @property
    def riccati_solution(self) -> np.ndarray:
        return self._S.copy()


# =============================================================================
# LQG CONTROLLER
# =============================================================================

class LQGController:
    """
    Linear Quadratic Gaussian Controller.
    
    Combines LQR optimal control with Kalman filtering.
    
    Separation Principle:
    - Estimator (Kalman) and Regulator (LQR) can be designed independently
    - Combined system maintains optimality
    
    Control law: u*(t) = -Kx̂(t)
    Where x̂ comes from Kalman filter
    """
    
    def __init__(self, A: np.ndarray, B: np.ndarray, C: np.ndarray,
                 Q_state: np.ndarray = None, R_control: np.ndarray = None,
                 Q_process: float = 0.1, R_measure: float = 0.1):
        """
        Initialize LQG controller.
        
        Args:
            A, B, C: System matrices
            Q_state: State cost (LQR)
            R_control: Control cost (LQR)
            Q_process: Process noise covariance (Kalman)
            R_measure: Measurement noise covariance (Kalman)
        """
        self.A = np.atleast_2d(A)
        self.B = np.atleast_2d(B)
        self.C = np.atleast_2d(C)
        
        self.n = self.A.shape[0]
        self.m = self.B.shape[1]
        
        # LQR component
        self.lqr = LQRController(A, B, Q_state, R_control)
        
        # Kalman filter component
        from .sensors import KalmanFilter
        self.kalman = KalmanFilter(
            state_dim=self.n,
            measurement_dim=self.C.shape[0],
            process_noise=Q_process,
            measurement_noise=R_measure
        )
        self.kalman.set_system_matrices(A, B, C)
    
    def compute(self, measurement: float, dt: float = 1.0) -> np.ndarray:
        """
        Compute LQG control.
        
        1. Update state estimate via Kalman filter
        2. Compute optimal control via LQR
        """
        # Get state estimate
        x_hat = self.kalman.filter_step(measurement, dt=dt)
        
        # Compute optimal control
        u = self.lqr.compute(x_hat)
        
        return u
    
    def reset(self) -> None:
        """Reset controller state."""
        self.kalman.reset()
    
    @property
    def state_estimate(self) -> np.ndarray:
        return self.kalman.estimate
    
    @property
    def control_gain(self) -> np.ndarray:
        return self.lqr.gain


# =============================================================================
# TRANSFER FUNCTION
# =============================================================================

class TransferFunction:
    """
    Transfer Function G(s) = Y(s)/U(s).
    
    Represents input-output relationship in Laplace domain.
    
    G(s) = (b_m s^m + ... + b_1 s + b_0) / (a_n s^n + ... + a_1 s + a_0)
    """
    
    def __init__(self, numerator: np.ndarray, denominator: np.ndarray):
        """
        Initialize transfer function.
        
        G(s) = num(s) / den(s)
        """
        self.num = np.atleast_1d(numerator)
        self.den = np.atleast_1d(denominator)
        
        # Normalize
        if self.den[0] != 0:
            self.num = self.num / self.den[0]
            self.den = self.den / self.den[0]
    
    def evaluate(self, s: complex) -> complex:
        """Evaluate G(s) at complex frequency s."""
        num_val = np.polyval(self.num, s)
        den_val = np.polyval(self.den, s)
        
        if np.abs(den_val) < 1e-15:
            return complex('inf')
        
        return num_val / den_val
    
    def frequency_response(self, omega: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute frequency response G(jω).
        
        Returns: (magnitude, phase)
        """
        s = 1j * omega
        response = np.array([self.evaluate(si) for si in s])
        
        magnitude = np.abs(response)
        phase = np.angle(response)
        
        return magnitude, phase
    
    def poles(self) -> np.ndarray:
        """Get system poles (roots of denominator)."""
        return np.roots(self.den)
    
    def zeros(self) -> np.ndarray:
        """Get system zeros (roots of numerator)."""
        return np.roots(self.num)
    
    def is_stable(self) -> bool:
        """Check BIBO stability (all poles in LHP)."""
        poles = self.poles()
        return bool(np.all(np.real(poles) < 0))
    
    def dc_gain(self) -> float:
        """Compute DC gain G(0)."""
        return float(np.real(self.evaluate(0)))
    
    def bandwidth(self, threshold: float = 0.707) -> float:
        """
        Compute -3dB bandwidth.
        
        Frequency where |G(jω)| = threshold × |G(0)|
        """
        dc = np.abs(self.evaluate(0))
        target = threshold * dc
        
        # Binary search for bandwidth
        omega_low, omega_high = 0.01, 100.0
        
        for _ in range(50):
            omega_mid = (omega_low + omega_high) / 2
            mag = np.abs(self.evaluate(1j * omega_mid))
            
            if mag > target:
                omega_low = omega_mid
            else:
                omega_high = omega_mid
        
        return (omega_low + omega_high) / 2
    
    def stability_status(self) -> StabilityStatus:
        """Determine stability status."""
        poles = self.poles()
        
        max_real = np.max(np.real(poles))
        
        if max_real < -1e-10:
            return StabilityStatus.STABLE
        elif max_real > 1e-10:
            return StabilityStatus.UNSTABLE
        else:
            return StabilityStatus.MARGINALLY_STABLE


# =============================================================================
# VALIDATION
# =============================================================================

def validate_controllers() -> bool:
    """Validate controllers module."""
    
    # Test ReferenceTrajectory
    ref = ReferenceTrajectory(dimension=2, trajectory_type="sinusoidal")
    ref.set_setpoint(np.array([1.0, 2.0]))
    ref.set_parameters(amplitude=np.array([0.5, 0.5]), frequency=np.array([1.0, 2.0]))
    
    r = ref.evaluate(0.0)
    assert len(r) == 2
    
    dr = ref.derivative(0.0)
    assert len(dr) == 2
    
    # Test ErrorVector
    error = ErrorVector(dimension=2)
    e = error.update(np.array([1.0, 1.0]), np.array([0.8, 0.9]), dt=0.1)
    
    assert len(e) == 2
    assert error.norm > 0
    
    # Test PIDController
    pid = PIDController(dimension=1, Kp=1.0, Ki=0.1, Kd=0.01)
    
    u = pid.compute(reference=np.array([1.0]), measurement=np.array([0.8]), dt=0.1)
    assert len(u) == 1
    assert u[0] != 0  # Should produce non-zero control
    
    # Test LQRController
    A = np.array([[0, 1], [-2, -3]])
    B = np.array([[0], [1]])
    
    lqr = LQRController(A, B)
    
    assert lqr.is_stable()
    assert lqr.stability_margin() > 0
    
    u = lqr.compute(np.array([1.0, 0.5]))
    assert len(u) == 1
    
    # Test TransferFunction
    # Second order system: G(s) = 1/(s^2 + 2s + 1)
    tf = TransferFunction([1], [1, 2, 1])
    
    assert tf.is_stable()
    assert tf.dc_gain() == 1.0
    
    poles = tf.poles()
    assert len(poles) == 2
    assert np.all(np.real(poles) < 0)
    
    bw = tf.bandwidth()
    assert bw > 0
    
    return True


if __name__ == "__main__":
    print("Validating Controllers Module...")
    assert validate_controllers()
    print("✓ Controllers Module validated")
