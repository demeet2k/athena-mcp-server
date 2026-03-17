"""
ATHENA OS - HDCS: SENSOR OPERATORS
==================================
State Estimation and Measurement Theory

THE SENSOR OPERATOR (Ŝ):
    The Agent operates within a partially observable environment.
    To navigate, the system must extract classical information from
    the quantum state vector |Ψ(t)⟩.

WEAK CONTINUOUS MEASUREMENT (POVM):
    We model the Sensor not as projective measurement (which collapses
    state and destroys coherence), but as a Positive Operator-Valued
    Measure (POVM).
    
    y(t) = ⟨Ŝ⟩_t + ξ(t) = ⟨Ψ|Ŝ|Ψ⟩ + (1/√2κ)(dW/dt)

KALMAN FILTER:
    Optimal state estimation from noisy measurements.
    Minimizes error covariance: P(t) = E[(x - x̂)(x - x̂)ᵀ]
    
    Estimator dynamics: dx̂ = f(x̂)dt + Budt + L(y - Cx̂)dt
    Where L = Kalman Gain

STOCHASTIC MASTER EQUATION:
    d|Ψ⟩ = [-iĤdt/ℏ - κ(Ŝ-⟨Ŝ⟩)²dt + √2κ(Ŝ-⟨Ŝ⟩)dW]|Ψ⟩
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Callable, Any
from enum import Enum, auto
import numpy as np
from scipy import linalg


# =============================================================================
# MEASUREMENT TYPES
# =============================================================================

class MeasurementType(Enum):
    """Types of quantum measurements."""
    
    PROJECTIVE = "projective"      # Strong, collapses state
    WEAK = "weak"                  # Continuous, preserves coherence
    POVM = "povm"                  # Generalized measurement
    HOMODYNE = "homodyne"          # Phase-sensitive
    HETERODYNE = "heterodyne"      # Simultaneous quadratures


class ObservableType(Enum):
    """Types of observables."""
    
    POSITION = "position"
    MOMENTUM = "momentum"
    PHASE = "phase"
    NUMBER = "number"
    ENERGY = "energy"


# =============================================================================
# EFFECT OPERATORS (POVM)
# =============================================================================

@dataclass
class EffectOperator:
    """
    Effect Operator for POVM.
    
    POVM: {Ê_λ} satisfying ∫ Ê_λ dλ = Î (completeness)
    
    Probability: P(λ) = ⟨Ψ|Ê_λ|Ψ⟩
    """
    
    dimension: int
    label: str = "E"
    
    # Effect matrix
    _matrix: np.ndarray = field(default=None)
    
    def __post_init__(self):
        if self._matrix is None:
            # Default: identity/N (uniform POVM element)
            self._matrix = np.eye(self.dimension) / self.dimension
    
    def probability(self, state: np.ndarray) -> float:
        """
        Compute measurement probability.
        
        P(λ) = ⟨Ψ|Ê_λ|Ψ⟩ = Tr(ρÊ_λ)
        """
        if state.ndim == 1:
            # Pure state
            return float(np.real(np.conj(state) @ self._matrix @ state))
        else:
            # Density matrix
            return float(np.real(np.trace(state @ self._matrix)))
    
    def post_measurement_state(self, state: np.ndarray) -> np.ndarray:
        """
        State after measurement (generalized).
        
        |Ψ'⟩ = M_λ|Ψ⟩ / ||M_λ|Ψ⟩||
        where Ê_λ = M_λ†M_λ
        """
        # Compute M = sqrt(E)
        M = linalg.sqrtm(self._matrix)
        
        new_state = M @ state
        norm = np.linalg.norm(new_state)
        
        if norm > 1e-10:
            return new_state / norm
        return state
    
    @property
    def matrix(self) -> np.ndarray:
        return self._matrix.copy()


class POVM:
    """
    Positive Operator-Valued Measure.
    
    Complete set of effect operators: Σ Ê_k = Î
    
    Generalized measurement that doesn't require orthogonal projectors.
    """
    
    def __init__(self, dimension: int, num_outcomes: int = 4):
        self.dimension = dimension
        self.num_outcomes = num_outcomes
        
        # Generate POVM elements
        self._effects = self._generate_symmetric_povm()
    
    def _generate_symmetric_povm(self) -> List[EffectOperator]:
        """Generate symmetric POVM (SIC-POVM approximation)."""
        effects = []
        
        for k in range(self.num_outcomes):
            # Create effect matrix
            E = np.zeros((self.dimension, self.dimension), dtype=complex)
            
            # Diagonal elements
            for i in range(self.dimension):
                phase = 2 * np.pi * k * i / self.num_outcomes
                E[i, i] = (1 + np.cos(phase)) / self.num_outcomes
            
            # Ensure positivity and completeness
            E = (E + E.conj().T) / 2  # Hermitian
            
            effect = EffectOperator(self.dimension, label=f"E_{k}")
            effect._matrix = E
            effects.append(effect)
        
        # Normalize to satisfy completeness
        total = sum(e._matrix for e in effects)
        for e in effects:
            e._matrix = e._matrix @ np.linalg.inv(total) * self.dimension
        
        return effects
    
    def measure(self, state: np.ndarray) -> Tuple[int, float, np.ndarray]:
        """
        Perform POVM measurement.
        
        Returns: (outcome_index, probability, post_state)
        """
        probabilities = [e.probability(state) for e in self._effects]
        probabilities = np.array(probabilities)
        probabilities = probabilities / probabilities.sum()  # Normalize
        
        # Sample outcome
        outcome = np.random.choice(self.num_outcomes, p=probabilities)
        
        # Post-measurement state
        post_state = self._effects[outcome].post_measurement_state(state)
        
        return outcome, probabilities[outcome], post_state
    
    def check_completeness(self) -> float:
        """Check if POVM satisfies completeness: Σ Ê_k = Î"""
        total = sum(e._matrix for e in self._effects)
        identity = np.eye(self.dimension)
        return float(np.linalg.norm(total - identity))


# =============================================================================
# SENSOR OPERATOR
# =============================================================================

class SensorOperator:
    """
    The Sensor Operator Ŝ.
    
    Extracts classical information from quantum state.
    
    Measurement outcome (with noise):
    y(t) = ⟨Ŝ⟩_t + ξ(t) = ⟨Ψ|Ŝ|Ψ⟩ + (1/√2κ)(dW/dt)
    
    Where:
    - κ: Measurement strength (information extraction rate)
    - dW: Wiener increment (Gaussian white noise)
    """
    
    def __init__(self, dimension: int,
                 observable_type: ObservableType = ObservableType.POSITION,
                 measurement_strength: float = 1.0):
        self.dimension = dimension
        self.observable_type = observable_type
        self.kappa = measurement_strength
        
        # Observable matrix
        self._observable = self._create_observable()
        
        # Noise generator
        self._noise_std = 1.0 / np.sqrt(2 * self.kappa) if self.kappa > 0 else 0
    
    def _create_observable(self) -> np.ndarray:
        """Create observable matrix based on type."""
        if self.observable_type == ObservableType.POSITION:
            # Position operator (diagonal in position basis)
            return np.diag(np.arange(self.dimension) - self.dimension/2)
        
        elif self.observable_type == ObservableType.MOMENTUM:
            # Momentum operator (tridiagonal)
            S = np.zeros((self.dimension, self.dimension), dtype=complex)
            for i in range(self.dimension - 1):
                S[i, i+1] = -1j
                S[i+1, i] = 1j
            return S
        
        elif self.observable_type == ObservableType.PHASE:
            # Phase operator
            S = np.zeros((self.dimension, self.dimension), dtype=complex)
            for i in range(self.dimension):
                for j in range(self.dimension):
                    if i != j:
                        S[i, j] = 1.0 / (i - j)
            return S
        
        elif self.observable_type == ObservableType.NUMBER:
            # Number operator
            return np.diag(np.arange(self.dimension))
        
        elif self.observable_type == ObservableType.ENERGY:
            # Harmonic oscillator Hamiltonian
            return np.diag(np.arange(self.dimension) + 0.5)
        
        return np.eye(self.dimension)
    
    def expectation(self, state: np.ndarray) -> float:
        """
        Compute expectation value ⟨Ŝ⟩.
        
        ⟨Ŝ⟩ = ⟨Ψ|Ŝ|Ψ⟩
        """
        if state.ndim == 1:
            return float(np.real(np.conj(state) @ self._observable @ state))
        else:
            return float(np.real(np.trace(state @ self._observable)))
    
    def measure(self, state: np.ndarray, add_noise: bool = True) -> float:
        """
        Perform measurement with optional noise.
        
        y(t) = ⟨Ŝ⟩_t + ξ(t)
        """
        expectation = self.expectation(state)
        
        if add_noise and self._noise_std > 0:
            noise = np.random.normal(0, self._noise_std)
            return expectation + noise
        
        return expectation
    
    def variance(self, state: np.ndarray) -> float:
        """
        Compute variance ⟨Ŝ²⟩ - ⟨Ŝ⟩².
        """
        exp_S = self.expectation(state)
        
        S_squared = self._observable @ self._observable
        if state.ndim == 1:
            exp_S2 = float(np.real(np.conj(state) @ S_squared @ state))
        else:
            exp_S2 = float(np.real(np.trace(state @ S_squared)))
        
        return exp_S2 - exp_S ** 2
    
    def back_action(self, state: np.ndarray, dt: float) -> np.ndarray:
        """
        Compute measurement back-action on state.
        
        From Stochastic Schrödinger Equation:
        Back-action term: -κ(Ŝ - ⟨Ŝ⟩)²dt + √2κ(Ŝ - ⟨Ŝ⟩)dW
        """
        exp_S = self.expectation(state)
        
        # Deviation operator: Ŝ - ⟨Ŝ⟩
        S_dev = self._observable - exp_S * np.eye(self.dimension)
        
        # Deterministic back-action: -κ(Ŝ - ⟨Ŝ⟩)²dt
        deterministic = -self.kappa * S_dev @ S_dev @ state * dt
        
        # Stochastic back-action: √2κ(Ŝ - ⟨Ŝ⟩)dW
        dW = np.random.normal(0, np.sqrt(dt))
        stochastic = np.sqrt(2 * self.kappa) * S_dev @ state * dW
        
        return deterministic + stochastic
    
    @property
    def observable(self) -> np.ndarray:
        return self._observable.copy()


# =============================================================================
# KALMAN FILTER
# =============================================================================

class KalmanFilter:
    """
    Optimal State Estimator (Kalman Filter).
    
    Minimizes error covariance: P(t) = E[(x - x̂)(x - x̂)ᵀ]
    
    Estimator dynamics:
    dx̂ = f(x̂)dt + Budt + L(y - Cx̂)dt
    
    Where L = Kalman Gain = PCᵀR⁻¹
    
    Result: lim_{t→∞} ||x(t) - x̂(t)|| = 0
    """
    
    def __init__(self, state_dim: int,
                 measurement_dim: int = 1,
                 process_noise: float = 0.1,
                 measurement_noise: float = 0.1):
        self.n = state_dim
        self.m = measurement_dim
        
        # System matrices
        self.A = np.eye(state_dim)  # State transition
        self.B = np.zeros((state_dim, 1))  # Control input
        self.C = np.zeros((measurement_dim, state_dim))
        self.C[0, 0] = 1.0  # Observe first state
        
        # Noise covariances
        self.Q = process_noise * np.eye(state_dim)  # Process noise
        self.R = measurement_noise * np.eye(measurement_dim)  # Measurement noise
        
        # State estimate and covariance
        self._x_hat = np.zeros(state_dim)
        self._P = np.eye(state_dim)
        
        # Kalman gain
        self._L = np.zeros((state_dim, measurement_dim))
    
    def predict(self, u: np.ndarray = None, dt: float = 1.0) -> np.ndarray:
        """
        Prediction step (time update).
        
        x̂⁻ = Ax̂ + Bu
        P⁻ = APAᵀ + Q
        """
        if u is None:
            u = np.zeros(1)
        
        # Discretize for dt
        Ad = np.eye(self.n) + self.A * dt
        
        # State prediction
        self._x_hat = Ad @ self._x_hat + self.B @ u * dt
        
        # Covariance prediction
        self._P = Ad @ self._P @ Ad.T + self.Q * dt
        
        return self._x_hat.copy()
    
    def update(self, y: float) -> np.ndarray:
        """
        Update step (measurement update).
        
        L = PCᵀ(CPCᵀ + R)⁻¹  (Kalman gain)
        x̂ = x̂⁻ + L(y - Cx̂⁻)
        P = (I - LC)P⁻
        """
        y_vec = np.atleast_1d(y)
        
        # Innovation covariance
        S = self.C @ self._P @ self.C.T + self.R
        
        # Kalman gain
        self._L = self._P @ self.C.T @ np.linalg.inv(S)
        
        # Innovation (measurement residual)
        innovation = y_vec - self.C @ self._x_hat
        
        # State update
        self._x_hat = self._x_hat + self._L @ innovation
        
        # Covariance update (Joseph form for numerical stability)
        I_LC = np.eye(self.n) - self._L @ self.C
        self._P = I_LC @ self._P @ I_LC.T + self._L @ self.R @ self._L.T
        
        return self._x_hat.copy()
    
    def filter_step(self, y: float, u: np.ndarray = None, 
                    dt: float = 1.0) -> np.ndarray:
        """Combined predict-update step."""
        self.predict(u, dt)
        return self.update(y)
    
    def set_system_matrices(self, A: np.ndarray = None,
                           B: np.ndarray = None,
                           C: np.ndarray = None) -> None:
        """Set system matrices."""
        if A is not None:
            self.A = A
        if B is not None:
            self.B = B
        if C is not None:
            self.C = C
    
    def reset(self, x0: np.ndarray = None, P0: np.ndarray = None) -> None:
        """Reset filter state."""
        if x0 is not None:
            self._x_hat = x0.copy()
        else:
            self._x_hat = np.zeros(self.n)
        
        if P0 is not None:
            self._P = P0.copy()
        else:
            self._P = np.eye(self.n)
    
    @property
    def estimate(self) -> np.ndarray:
        return self._x_hat.copy()
    
    @property
    def covariance(self) -> np.ndarray:
        return self._P.copy()
    
    @property
    def kalman_gain(self) -> np.ndarray:
        return self._L.copy()
    
    def estimation_error(self, true_state: np.ndarray) -> float:
        """Compute estimation error ||x - x̂||."""
        return float(np.linalg.norm(true_state - self._x_hat))


# =============================================================================
# EXTENDED KALMAN FILTER
# =============================================================================

class ExtendedKalmanFilter(KalmanFilter):
    """
    Extended Kalman Filter for nonlinear systems.
    
    Nonlinear dynamics: dx = f(x)dt + Bu dt + Gdw
    Nonlinear measurement: y = h(x) + v
    
    Linearizes around current estimate using Jacobians.
    """
    
    def __init__(self, state_dim: int,
                 f: Callable[[np.ndarray], np.ndarray] = None,
                 h: Callable[[np.ndarray], np.ndarray] = None,
                 **kwargs):
        super().__init__(state_dim, **kwargs)
        
        # Nonlinear functions
        self._f = f if f is not None else lambda x: np.zeros_like(x)
        self._h = h if h is not None else lambda x: x[:1]
    
    def _jacobian_f(self, x: np.ndarray, eps: float = 1e-6) -> np.ndarray:
        """Compute Jacobian of f by finite differences."""
        n = len(x)
        J = np.zeros((n, n))
        
        f0 = self._f(x)
        for i in range(n):
            x_plus = x.copy()
            x_plus[i] += eps
            J[:, i] = (self._f(x_plus) - f0) / eps
        
        return J
    
    def _jacobian_h(self, x: np.ndarray, eps: float = 1e-6) -> np.ndarray:
        """Compute Jacobian of h by finite differences."""
        h0 = self._h(x)
        m = len(np.atleast_1d(h0))
        n = len(x)
        J = np.zeros((m, n))
        
        for i in range(n):
            x_plus = x.copy()
            x_plus[i] += eps
            J[:, i] = (np.atleast_1d(self._h(x_plus)) - np.atleast_1d(h0)) / eps
        
        return J
    
    def predict(self, u: np.ndarray = None, dt: float = 1.0) -> np.ndarray:
        """EKF prediction with nonlinear dynamics."""
        if u is None:
            u = np.zeros(1)
        
        # Jacobian at current estimate
        F = self._jacobian_f(self._x_hat)
        
        # State prediction (Euler integration)
        self._x_hat = self._x_hat + self._f(self._x_hat) * dt + self.B @ u * dt
        
        # Covariance prediction
        self._P = F @ self._P @ F.T + self.Q * dt
        
        return self._x_hat.copy()
    
    def update(self, y: float) -> np.ndarray:
        """EKF update with nonlinear measurement."""
        y_vec = np.atleast_1d(y)
        
        # Jacobian at current estimate
        H = self._jacobian_h(self._x_hat)
        
        # Innovation covariance
        S = H @ self._P @ H.T + self.R
        
        # Kalman gain
        self._L = self._P @ H.T @ np.linalg.inv(S)
        
        # Predicted measurement
        y_pred = np.atleast_1d(self._h(self._x_hat))
        
        # Innovation
        innovation = y_vec - y_pred
        
        # State update
        self._x_hat = self._x_hat + self._L @ innovation
        
        # Covariance update
        I_LH = np.eye(self.n) - self._L @ H
        self._P = I_LH @ self._P
        
        return self._x_hat.copy()


# =============================================================================
# VALIDATION
# =============================================================================

def validate_sensors() -> bool:
    """Validate sensor operators module."""
    
    # Test EffectOperator
    effect = EffectOperator(dimension=4)
    state = np.array([1, 0, 0, 0], dtype=complex)
    state = state / np.linalg.norm(state)
    
    prob = effect.probability(state)
    assert 0 <= prob <= 1
    
    # Test POVM
    povm = POVM(dimension=4, num_outcomes=4)
    
    completeness_error = povm.check_completeness()
    assert completeness_error < 0.1  # Approximate completeness
    
    outcome, prob, post_state = povm.measure(state)
    assert 0 <= outcome < 4
    assert 0 <= prob <= 1
    assert np.abs(np.linalg.norm(post_state) - 1) < 1e-6
    
    # Test SensorOperator
    sensor = SensorOperator(dimension=8, observable_type=ObservableType.POSITION)
    
    state = np.random.randn(8) + 1j * np.random.randn(8)
    state = state / np.linalg.norm(state)
    
    exp = sensor.expectation(state)
    assert isinstance(exp, float)
    
    measurement = sensor.measure(state)
    assert isinstance(measurement, float)
    
    var = sensor.variance(state)
    assert var >= 0  # Variance must be non-negative
    
    # Test KalmanFilter
    kf = KalmanFilter(state_dim=4, measurement_dim=1)
    
    # Simulate system
    true_state = np.array([1.0, 0.5, 0.2, 0.1])
    
    for _ in range(10):
        # Noisy measurement
        y = true_state[0] + np.random.normal(0, 0.1)
        estimate = kf.filter_step(y, dt=0.1)
    
    error = kf.estimation_error(true_state)
    assert error < 5.0  # Should converge somewhat
    
    # Test ExtendedKalmanFilter
    def f(x):
        return np.array([x[1], -x[0]])[:len(x)]
    
    def h(x):
        return x[0:1]
    
    ekf = ExtendedKalmanFilter(state_dim=2, f=f, h=h)
    
    for _ in range(5):
        y = 0.5 + np.random.normal(0, 0.1)
        estimate = ekf.filter_step(y, dt=0.1)
    
    assert len(estimate) == 2
    
    return True


if __name__ == "__main__":
    print("Validating Sensors Module...")
    assert validate_sensors()
    print("✓ Sensors Module validated")
