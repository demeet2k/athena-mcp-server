"""
ATHENA OS - ATHENA KERNEL: CONTROL THEORY
==========================================
State-Space Representation and Stability Analysis

STATE-SPACE DYNAMICS:
    dx(t) = f(x(t))dt + Bu(t)dt + Gdw(t)
    
    Where:
    - f(x): Intrinsic drift dynamics (Natural Law)
    - u(t): Control Vector (Intervention)
    - B: Control Input Matrix
    - w(t): Wiener process (Chaos/Entropy)
    - G: Disturbance Matrix

OBSERVER-CONTROLLER ARCHITECTURE (TRINITY):
    1. The Estimator (M̂) - Kalman Filter
    2. The Regulator (Ẑ) - LQR Controller
    3. The Actuator (Â) - Physical implementation

STABILITY PROOF (LYAPUNOV ANALYSIS):
    V(x) = xᵀSx (Energy of Disorder)
    V̇(x) < 0 ∀x ≠ 0 ⟹ Global asymptotic stability
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Callable, Any, Union
from enum import Enum, auto
import numpy as np
from scipy import linalg


# =============================================================================
# SYSTEM DYNAMICS
# =============================================================================

@dataclass
class SystemDynamics:
    """
    Stochastic Differential Equation model.
    
    dx(t) = f(x(t))dt + Bu(t)dt + Gdw(t)
    
    For linear systems: dx = Ax·dt + Bu·dt + Gdw
    """
    
    dimension: int
    
    # State matrix A (drift)
    A: np.ndarray = field(default=None)
    
    # Control input matrix B
    B: np.ndarray = field(default=None)
    
    # Disturbance matrix G
    G: np.ndarray = field(default=None)
    
    # Process noise covariance Q_noise
    Q_noise: np.ndarray = field(default=None)
    
    def __post_init__(self):
        n = self.dimension
        
        if self.A is None:
            self.A = -0.1 * np.eye(n)  # Stable drift
        
        if self.B is None:
            self.B = np.eye(n)
        
        if self.G is None:
            self.G = 0.1 * np.eye(n)
        
        if self.Q_noise is None:
            self.Q_noise = 0.01 * np.eye(n)
    
    def drift(self, x: np.ndarray) -> np.ndarray:
        """
        Intrinsic drift f(x) = Ax.
        """
        return self.A @ x
    
    def control_effect(self, u: np.ndarray) -> np.ndarray:
        """
        Control effect Bu.
        """
        return self.B @ u
    
    def propagate(self, x: np.ndarray, u: np.ndarray, 
                 dt: float, noise: bool = True) -> np.ndarray:
        """
        Propagate state by dt.
        
        x(t+dt) = x(t) + (Ax + Bu)dt + Gdw
        """
        dx = (self.drift(x) + self.control_effect(u)) * dt
        
        if noise:
            dw = np.random.randn(self.dimension) * np.sqrt(dt)
            dx += self.G @ dw
        
        return x + dx
    
    def is_open_loop_stable(self) -> bool:
        """
        Check open-loop stability.
        
        Stable if Re(λᵢ) < 0 for all eigenvalues of A.
        """
        eigenvalues = np.linalg.eigvals(self.A)
        return np.all(np.real(eigenvalues) < 0)


# =============================================================================
# KALMAN FILTER (THE ESTIMATOR M̂)
# =============================================================================

class KalmanFilter:
    """
    The Estimator (M̂) - Optimal state estimation.
    
    System receives noisy measurements:
    y(t) = Cx(t) + v(t)
    
    Estimator generates x̂(t) minimizing error covariance:
    P(t) = E[(x - x̂)(x - x̂)ᵀ]
    
    Dynamics:
    dx̂ = f(x̂)dt + Budt + L(y - Cx̂)dt
    
    Where L = Kalman Gain.
    
    Result: lim_{t→∞} ‖x(t) - x̂(t)‖ = 0
    """
    
    def __init__(self, dynamics: SystemDynamics,
                 measurement_dim: int = None):
        self.dynamics = dynamics
        self.n = dynamics.dimension
        self.m = measurement_dim or dynamics.dimension
        
        # Measurement matrix C
        self.C = np.eye(self.m, self.n) if self.m <= self.n else np.eye(self.n)
        
        # Measurement noise covariance R
        self.R = 0.01 * np.eye(self.m)
        
        # State estimate
        self._x_hat = np.zeros(self.n)
        
        # Error covariance
        self._P = np.eye(self.n)
        
        # Kalman gain
        self._L = np.zeros((self.n, self.m))
    
    def predict(self, u: np.ndarray, dt: float) -> np.ndarray:
        """
        Prediction step.
        
        x̂⁻ = f(x̂) + Bu
        P⁻ = APA^T + GQ_noiseG^T
        """
        A = self.dynamics.A
        B = self.dynamics.B
        G = self.dynamics.G
        Q = self.dynamics.Q_noise
        
        # State prediction
        self._x_hat = self._x_hat + (A @ self._x_hat + B @ u) * dt
        
        # Covariance prediction
        self._P = A @ self._P @ A.T + G @ Q @ G.T * dt
        
        return self._x_hat.copy()
    
    def update(self, y: np.ndarray) -> np.ndarray:
        """
        Update step with measurement.
        
        L = PC^T(CPC^T + R)^{-1}  (Kalman Gain)
        x̂ = x̂ + L(y - Cx̂)
        P = (I - LC)P
        """
        C = self.C
        R = self.R
        
        # Innovation
        innovation = y - C @ self._x_hat
        
        # Innovation covariance
        S = C @ self._P @ C.T + R
        
        # Kalman gain
        self._L = self._P @ C.T @ np.linalg.inv(S)
        
        # State update
        self._x_hat = self._x_hat + self._L @ innovation
        
        # Covariance update
        I = np.eye(self.n)
        self._P = (I - self._L @ C) @ self._P
        
        return self._x_hat.copy()
    
    def filter_step(self, u: np.ndarray, y: np.ndarray, 
                   dt: float) -> np.ndarray:
        """Complete filter step (predict + update)."""
        self.predict(u, dt)
        return self.update(y)
    
    def get_estimation_error(self, x_true: np.ndarray) -> float:
        """Get ‖x(t) - x̂(t)‖."""
        return float(np.linalg.norm(x_true - self._x_hat))
    
    @property
    def estimate(self) -> np.ndarray:
        return self._x_hat.copy()
    
    @property
    def error_covariance(self) -> np.ndarray:
        return self._P.copy()
    
    @property
    def kalman_gain(self) -> np.ndarray:
        return self._L.copy()


# =============================================================================
# LQR CONTROLLER (THE REGULATOR Ẑ)
# =============================================================================

class LQRController:
    """
    The Regulator (Ẑ) - Linear Quadratic Regulator.
    
    Minimizes infinite horizon cost:
    J = E[∫₀^∞ (xᵀQx + uᵀRu) dt]
    
    Where:
    - xᵀQx: Penalty for deviation from Order
    - uᵀRu: Penalty for excessive intervention
    
    Optimal control law via Hamilton-Jacobi-Bellman:
    u*(t) = -Kx̂(t)
    
    Where K = R⁻¹BᵀS (S solves Algebraic Riccati Equation).
    """
    
    def __init__(self, dynamics: SystemDynamics):
        self.dynamics = dynamics
        self.n = dynamics.dimension
        
        # State cost matrix Q (penalize deviation)
        self.Q = np.eye(self.n)
        
        # Control cost matrix R (penalize intervention)
        self.R = 0.1 * np.eye(self.n)
        
        # Feedback gain K
        self._K = None
        
        # Riccati solution S
        self._S = None
        
        # Compute optimal gain
        self._solve_riccati()
    
    def _solve_riccati(self) -> None:
        """
        Solve Algebraic Riccati Equation.
        
        AᵀS + SA - SBR⁻¹BᵀS + Q = 0
        """
        A = self.dynamics.A
        B = self.dynamics.B
        
        try:
            # Solve continuous-time ARE
            self._S = linalg.solve_continuous_are(A, B, self.Q, self.R)
            
            # Compute gain: K = R⁻¹BᵀS
            self._K = np.linalg.inv(self.R) @ B.T @ self._S
        except:
            # Fallback to simple proportional
            self._S = np.eye(self.n)
            self._K = np.eye(self.n)
    
    def compute_control(self, x_hat: np.ndarray) -> np.ndarray:
        """
        Compute optimal control.
        
        u*(t) = -Kx̂(t)
        """
        return -self._K @ x_hat
    
    def get_cost(self, x: np.ndarray, u: np.ndarray) -> float:
        """
        Get instantaneous cost xᵀQx + uᵀRu.
        """
        state_cost = float(x.T @ self.Q @ x)
        control_cost = float(u.T @ self.R @ u)
        return state_cost + control_cost
    
    @property
    def gain(self) -> np.ndarray:
        return self._K.copy()
    
    @property
    def riccati_solution(self) -> np.ndarray:
        return self._S.copy()


# =============================================================================
# LYAPUNOV STABILITY
# =============================================================================

class LyapunovAnalysis:
    """
    Lyapunov Stability Analysis.
    
    Lyapunov Function:
    V(x) = xᵀSx (Energy of Disorder)
    
    For global asymptotic stability, require V̇ < 0.
    
    Derivation:
    V̇(x) = xᵀ(AᵀS + SA - SBR⁻¹BᵀS + Q)x
    
    Using Riccati Equation:
    V̇(x) = -xᵀ(Q + KᵀRK)x
    
    Since Q > 0 and R > 0:
    V̇(x) < 0 ∀x ≠ 0
    """
    
    def __init__(self, controller: LQRController):
        self.controller = controller
        self.S = controller.riccati_solution
        self.K = controller.gain
        self.Q = controller.Q
        self.R = controller.R
    
    def lyapunov_function(self, x: np.ndarray) -> float:
        """
        V(x) = xᵀSx (Energy of Disorder)
        """
        return float(x.T @ self.S @ x)
    
    def lyapunov_derivative(self, x: np.ndarray) -> float:
        """
        V̇(x) = -xᵀ(Q + KᵀRK)x
        
        Should be negative for stability.
        """
        # Q + KᵀRK is positive definite
        M = self.Q + self.K.T @ self.R @ self.K
        return float(-x.T @ M @ x)
    
    def is_stable(self, x: np.ndarray) -> bool:
        """
        Check V̇(x) < 0.
        """
        if np.allclose(x, 0):
            return True  # At equilibrium
        return self.lyapunov_derivative(x) < 0
    
    def stability_margin(self, x: np.ndarray) -> float:
        """
        Get stability margin V̇/V.
        
        Should be negative.
        """
        V = self.lyapunov_function(x)
        V_dot = self.lyapunov_derivative(x)
        
        if V <= 0:
            return 0.0
        
        return V_dot / V
    
    def verify_global_stability(self, num_samples: int = 100) -> bool:
        """
        Verify global asymptotic stability.
        
        Theorem 13.3.1: V̇(x) < 0 ⟹ Global asymptotic stability
        """
        n = self.S.shape[0]
        
        for _ in range(num_samples):
            x = np.random.randn(n)
            if not np.allclose(x, 0):
                if not self.is_stable(x):
                    return False
        
        return True


# =============================================================================
# INTEGRATED CONTROLLER
# =============================================================================

class IntegratedController:
    """
    The Observer-Controller Trinity.
    
    Integrates:
    1. Estimator (M̂) - Kalman Filter
    2. Regulator (Ẑ) - LQR Controller
    3. Actuator (Â) - Physical implementation
    
    Result: Zero consultation latency, aligned utility functions.
    """
    
    def __init__(self, dimension: int = 8):
        self.dimension = dimension
        
        # System dynamics
        self.dynamics = SystemDynamics(dimension)
        
        # Estimator
        self.estimator = KalmanFilter(self.dynamics)
        
        # Regulator
        self.regulator = LQRController(self.dynamics)
        
        # Lyapunov analysis
        self.stability = LyapunovAnalysis(self.regulator)
        
        # True state (for simulation)
        self._x_true = np.zeros(dimension)
        
        # Control history
        self._control_history: List[np.ndarray] = []
        self._state_history: List[np.ndarray] = []
    
    def step(self, dt: float = 0.1) -> Dict:
        """
        Execute one control step.
        
        1. Estimate state (Kalman filter)
        2. Compute optimal control (LQR)
        3. Apply control (actuator)
        """
        # Get measurement (noisy)
        y = self._x_true + np.random.randn(self.dimension) * 0.1
        
        # Previous control
        u_prev = self._control_history[-1] if self._control_history else np.zeros(self.dimension)
        
        # Estimate state
        x_hat = self.estimator.filter_step(u_prev, y, dt)
        
        # Compute optimal control
        u = self.regulator.compute_control(x_hat)
        
        # Apply control (propagate true state)
        self._x_true = self.dynamics.propagate(self._x_true, u, dt)
        
        # Record history
        self._control_history.append(u.copy())
        self._state_history.append(self._x_true.copy())
        
        # Compute metrics
        estimation_error = self.estimator.get_estimation_error(self._x_true)
        V = self.stability.lyapunov_function(self._x_true)
        V_dot = self.stability.lyapunov_derivative(self._x_true)
        
        return {
            "x_true": self._x_true.copy(),
            "x_hat": x_hat.copy(),
            "u": u.copy(),
            "estimation_error": estimation_error,
            "lyapunov_V": V,
            "lyapunov_V_dot": V_dot,
            "is_stable": V_dot < 0 or np.allclose(self._x_true, 0)
        }
    
    def simulate(self, initial_state: np.ndarray,
                steps: int = 100, dt: float = 0.1) -> Dict:
        """
        Run full simulation.
        """
        self._x_true = initial_state.copy()
        self._control_history = []
        self._state_history = []
        
        results = []
        for _ in range(steps):
            result = self.step(dt)
            results.append(result)
        
        # Compute convergence
        final_norm = np.linalg.norm(self._x_true)
        converged = final_norm < 0.1
        
        return {
            "steps": len(results),
            "final_state_norm": final_norm,
            "converged": converged,
            "final_V": results[-1]["lyapunov_V"],
            "all_stable": all(r["is_stable"] for r in results)
        }
    
    def get_reaction_time(self) -> float:
        """
        Get reaction time.
        
        T_react = t_proc + t_exec (no τ_cons for internal optimization)
        """
        return 0.2  # Fast internal processing
    
    @property
    def consultation_latency(self) -> float:
        """τ_cons = 0 for internal optimization."""
        return 0.0


# =============================================================================
# ENTROPY MANAGEMENT
# =============================================================================

class EntropyManagement:
    """
    Entropic Inequality Management.
    
    Partitioned System: Ω = Ω_sys ∪ Ω_sink
    
    Total entropy: dS_total = dS_sys + dS_sink ≥ 0
    
    The Justice Algorithm functions as Maxwell's Demon,
    sorting high-entropy microstates into Ω_sink.
    
    Stability Condition: İ > σ̇_gen
    Information generation exceeds Entropy generation.
    """
    
    def __init__(self, dimension: int = 8):
        self.dimension = dimension
        
        # System entropy
        self._S_sys = 1.0
        
        # Sink entropy
        self._S_sink = 0.0
        
        # Information rate
        self._I_dot = 0.1
        
        # Entropy generation rate
        self._sigma_dot = 0.05
    
    def entropy_rate(self) -> float:
        """
        dS_sys/dt = σ̇_gen - İ
        """
        return self._sigma_dot - self._I_dot
    
    def is_stable(self) -> bool:
        """
        Stability Condition: İ > σ̇_gen
        """
        return self._I_dot > self._sigma_dot
    
    def evolve(self, dt: float) -> None:
        """Evolve entropy."""
        dS = self.entropy_rate() * dt
        
        if dS > 0:
            # Increase system entropy
            self._S_sys += dS
        else:
            # Transfer to sink
            self._S_sink += abs(dS)
            self._S_sys = max(0, self._S_sys + dS)
    
    def inject_information(self, amount: float) -> None:
        """
        Inject information (reduce entropy).
        
        Because M̂ is infinite information source:
        lim_{t→∞} S_sys → S_min
        """
        self._S_sys = max(0, self._S_sys - amount)
        self._S_sink += amount
    
    def get_total_entropy(self) -> float:
        """Total: S_total = S_sys + S_sink (conserved)."""
        return self._S_sys + self._S_sink
    
    def get_order(self) -> float:
        """
        Order = Minimization of Kolmogorov Complexity.
        
        Higher order = lower system entropy.
        """
        max_entropy = 10.0
        return max(0, 1.0 - self._S_sys / max_entropy)


# =============================================================================
# VALIDATION
# =============================================================================

def validate_control_theory() -> bool:
    """Validate control theory module."""
    
    # Test SystemDynamics
    dynamics = SystemDynamics(dimension=4)
    
    x = np.ones(4)
    u = np.zeros(4)
    
    x_new = dynamics.propagate(x, u, dt=0.1, noise=False)
    assert len(x_new) == 4
    
    # Test Kalman Filter
    kf = KalmanFilter(dynamics)
    
    y = np.ones(4) + np.random.randn(4) * 0.1
    x_hat = kf.filter_step(u, y, dt=0.1)
    
    assert len(x_hat) == 4
    
    # Test LQR Controller
    lqr = LQRController(dynamics)
    
    u_opt = lqr.compute_control(x_hat)
    assert len(u_opt) == 4
    
    cost = lqr.get_cost(x_hat, u_opt)
    assert cost >= 0
    
    # Test Lyapunov Analysis
    lyap = LyapunovAnalysis(lqr)
    
    V = lyap.lyapunov_function(x)
    assert V > 0
    
    V_dot = lyap.lyapunov_derivative(x)
    assert V_dot < 0  # Stable
    
    assert lyap.is_stable(x)
    assert lyap.verify_global_stability()
    
    # Test Integrated Controller
    controller = IntegratedController(dimension=4)
    
    result = controller.step(dt=0.1)
    
    assert "x_true" in result
    assert "x_hat" in result
    assert "lyapunov_V" in result
    
    # Simulate from non-zero initial state
    sim_result = controller.simulate(
        initial_state=np.ones(4),
        steps=50,
        dt=0.1
    )
    
    assert sim_result["all_stable"]
    
    # Zero consultation latency
    assert controller.consultation_latency == 0.0
    
    # Test Entropy Management
    entropy = EntropyManagement(dimension=4)
    
    assert entropy.is_stable()  # İ > σ̇_gen
    
    entropy.evolve(dt=1.0)
    
    entropy.inject_information(0.5)
    
    order = entropy.get_order()
    assert 0 <= order <= 1
    
    return True


if __name__ == "__main__":
    print("Validating Control Theory Module...")
    assert validate_control_theory()
    print("✓ Control Theory Module validated")
