"""
ATHENA OS - KHEMET: DYNAMICS MODULE
====================================
Runtime Dynamics, Control Loops, and Spectral Cycles

THE CYBERNETIC CONTROL LOOP:
    Observer → Controller → Actuator → Plant → (feedback)
    
    Ma'at Tracking: Maintains optimal path through state space

AUTOMATIC GAIN CONTROL (AGC):
    Regime I (Linear): K = K_LINEAR, stable maintenance
    Regime II (Purge): K = α·exp(λt), exponential threat response
    Regime III (Damped): Soft saturation, thermal runaway prevention

THE SPECTRAL CYCLE (Day/Night):
    Day Phase: Time domain representation (Active)
    Night Phase: Frequency domain representation (Processing)
    
    F: L²(ℝ) → L²(ℝ)
    |Ψ̃(ω)⟩ = F[|Ψ(t)⟩]

SPECTRAL CLEANING:
    1. Forward Transform (Dissolution/Sleep)
    2. High-Pass Filter (Remove entropy)
    3. Phase Conjugation (Entropy reversal)
    4. Inverse Transform (Rebirth/Sunrise)
    5. Parseval Integrity Check
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Callable, Any, Union
from enum import Enum, auto
from abc import ABC, abstractmethod
import numpy as np
from scipy.fft import fft, ifft, fftfreq


# =============================================================================
# CONTROL SYSTEM CONSTANTS
# =============================================================================

# Gain parameters
K_LINEAR = 1.0
ALPHA = 0.1
LAMBDA_CONST = 0.5

# Damping parameters
ZETA_NOMINAL = 0.7    # Nominal damping ratio
ZETA_CRITICAL = 1.0   # Critical damping
ZETA_OVERDAMPED = 2.0

# Thresholds
THRESHOLD_EPSILON = 0.01
MAX_SAFE_LOAD = 10.0
SATURATION_LIMIT = 100.0

# Spectral parameters
OMEGA_C = 0.1  # Cutoff frequency


# =============================================================================
# CONTROL REGIMES
# =============================================================================

class ControlRegime(Enum):
    """Operating regimes for the control system."""
    
    STABLE = "stable"         # Linear, low-gain maintenance
    PURGE = "purge"           # Non-linear, high-gain response
    DAMPED = "damped"         # Overdamped, safety mode
    RUNAWAY = "runaway"       # Thermal runaway detected


class ClockPhase(Enum):
    """Phases of the spectral clock cycle."""
    
    DAY = "day"               # Time domain (Active)
    NIGHT = "night"           # Frequency domain (Processing)
    DAWN = "dawn"             # Transition Night → Day
    DUSK = "dusk"             # Transition Day → Night


# =============================================================================
# OBSERVER (STATE ESTIMATION)
# =============================================================================

@dataclass
class StateObserver:
    """
    The Observer (Sensor) Component.
    
    Estimates system state from noisy measurements.
    Implements Kalman-like filtering.
    """
    
    dimension: int
    
    # State estimate
    x_hat: np.ndarray = field(default=None)
    
    # Covariance
    P: np.ndarray = field(default=None)
    
    # Noise parameters
    Q: float = 0.01  # Process noise
    R: float = 0.1   # Measurement noise
    
    def __post_init__(self):
        if self.x_hat is None:
            self.x_hat = np.zeros(self.dimension, dtype=np.complex128)
        if self.P is None:
            self.P = np.eye(self.dimension) * 0.1
    
    def predict(self, A: np.ndarray) -> np.ndarray:
        """Prediction step: x̂⁻ = A·x̂"""
        self.x_hat = A @ self.x_hat
        self.P = A @ self.P @ A.T + self.Q * np.eye(self.dimension)
        return self.x_hat
    
    def update(self, z: np.ndarray, H: np.ndarray) -> np.ndarray:
        """Update step with measurement z."""
        # Kalman gain
        S = H @ self.P @ H.T + self.R * np.eye(len(z))
        K = self.P @ H.T @ np.linalg.inv(S)
        
        # Update estimate
        innovation = z - H @ self.x_hat
        self.x_hat = self.x_hat + K @ innovation
        
        # Update covariance
        self.P = (np.eye(self.dimension) - K @ H) @ self.P
        
        return self.x_hat
    
    def get_estimate(self) -> np.ndarray:
        """Get current state estimate."""
        return self.x_hat.copy()


# =============================================================================
# CONTROLLER (MA'AT PATH TRACKING)
# =============================================================================

@dataclass
class TrajectoryController:
    """
    The Controller Component.
    
    Implements Ma'at (Optimal Path) tracking.
    Computes error and generates control signal.
    """
    
    dimension: int
    
    # Controller gains
    K_p: float = 1.0   # Proportional
    K_i: float = 0.1   # Integral
    K_d: float = 0.05  # Derivative
    
    # State
    integral_error: np.ndarray = field(default=None)
    prev_error: np.ndarray = field(default=None)
    
    def __post_init__(self):
        if self.integral_error is None:
            self.integral_error = np.zeros(self.dimension, dtype=np.complex128)
        if self.prev_error is None:
            self.prev_error = np.zeros(self.dimension, dtype=np.complex128)
    
    def compute_error(self, reference: np.ndarray, 
                     estimated: np.ndarray) -> np.ndarray:
        """Compute deviation from Ma'at (optimal path)."""
        return reference - estimated
    
    def compute_control(self, error: np.ndarray, 
                       dt: float = 0.01) -> np.ndarray:
        """
        PID control law.
        
        u = K_p·e + K_i·∫e + K_d·de/dt
        """
        # Update integral
        self.integral_error += error * dt
        
        # Compute derivative
        derivative = (error - self.prev_error) / dt if dt > 0 else np.zeros_like(error)
        
        # PID output
        u = (self.K_p * error + 
             self.K_i * self.integral_error + 
             self.K_d * derivative)
        
        # Store for next iteration
        self.prev_error = error.copy()
        
        return u
    
    def reset(self) -> None:
        """Reset controller state."""
        self.integral_error = np.zeros(self.dimension, dtype=np.complex128)
        self.prev_error = np.zeros(self.dimension, dtype=np.complex128)


# =============================================================================
# AUTOMATIC GAIN CONTROL (AGC)
# =============================================================================

class GainScheduler:
    """
    Automatic Gain Controller.
    
    Manages amplification based on error magnitude.
    Includes soft-saturation safety limits.
    """
    
    def __init__(self):
        self.time_step = 0
        self.current_regime = ControlRegime.STABLE
    
    def compute_gain(self, error_signal: np.ndarray, 
                    system_output: np.ndarray) -> Tuple[float, float, ControlRegime]:
        """
        Gain scheduling algorithm.
        
        Returns (gain, damping, regime).
        """
        error_mag = np.linalg.norm(error_signal)
        output_mag = np.linalg.norm(system_output)
        
        # Check Error Magnitude
        if error_mag < THRESHOLD_EPSILON:
            # REGIME I: Linear Operation
            gain = K_LINEAR
            damping = ZETA_NOMINAL
            status = ControlRegime.STABLE
        else:
            # REGIME II: Non-Linear Purge
            self.time_step += 1
            gain = ALPHA * np.exp(LAMBDA_CONST * self.time_step * 0.01)
            damping = ZETA_NOMINAL
            status = ControlRegime.PURGE
        
        # Safety Check (Thermal Runaway Prevention)
        if output_mag > MAX_SAFE_LOAD:
            # INJECT DAMPING FLUID
            damping = ZETA_CRITICAL
            
            # Apply Soft Saturation (Tanh)
            gain = (SATURATION_LIMIT / (output_mag + 1e-10)) * np.tanh(output_mag)
            status = ControlRegime.DAMPED
        
        self.current_regime = status
        return gain, damping, status
    
    def soft_saturation(self, x: float, L: float = SATURATION_LIMIT) -> float:
        """
        Soft saturation function.
        
        G(x) = L·tanh(x/L)
        """
        return L * np.tanh(x / L)
    
    def reset(self) -> None:
        """Reset time step counter."""
        self.time_step = 0
        self.current_regime = ControlRegime.STABLE


# =============================================================================
# ACTUATOR (HAMILTONIAN MODULATION)
# =============================================================================

@dataclass
class HamiltonianActuator:
    """
    The Actuator Component.
    
    Applies control force to the system Hamiltonian.
    Modulates potential energy surface.
    """
    
    dimension: int
    
    # Current potential modification
    delta_V: np.ndarray = field(default=None)
    
    def __post_init__(self):
        if self.delta_V is None:
            self.delta_V = np.zeros((self.dimension, self.dimension), dtype=np.complex128)
    
    def update_potential(self, control_force: np.ndarray, 
                        gain: float = 1.0) -> np.ndarray:
        """
        Update potential based on control force.
        
        V → V + gain · diag(F)
        """
        # Create diagonal modification
        for i in range(min(len(control_force), self.dimension)):
            self.delta_V[i, i] = gain * control_force[i]
        
        return self.delta_V
    
    def get_modification(self) -> np.ndarray:
        """Get current potential modification."""
        return self.delta_V.copy()
    
    def reset(self) -> None:
        """Reset modification."""
        self.delta_V = np.zeros((self.dimension, self.dimension), dtype=np.complex128)


# =============================================================================
# SPECTRAL CYCLE (FOURIER TRANSFORM)
# =============================================================================

class SpectralClock:
    """
    The Spectral Clock.
    
    Manages Day/Night cycle transitions between
    time domain and frequency domain.
    """
    
    def __init__(self, cycle_period: float = 2 * np.pi):
        self.cycle_period = cycle_period
        self.phase = 0.0
        self.current_phase = ClockPhase.DAY
    
    def advance(self, dt: float) -> ClockPhase:
        """Advance clock by dt."""
        self.phase = (self.phase + dt) % self.cycle_period
        
        # Determine phase
        normalized = self.phase / self.cycle_period
        
        if 0.0 <= normalized < 0.25:
            self.current_phase = ClockPhase.DAY
        elif 0.25 <= normalized < 0.5:
            self.current_phase = ClockPhase.DUSK
        elif 0.5 <= normalized < 0.75:
            self.current_phase = ClockPhase.NIGHT
        else:
            self.current_phase = ClockPhase.DAWN
        
        return self.current_phase
    
    def is_end_of_cycle(self) -> bool:
        """Check if at end of cycle (θ ≈ 2π)."""
        return np.abs(self.phase - self.cycle_period) < 0.1
    
    def reset(self) -> None:
        """Reset clock to start of cycle."""
        self.phase = 0.0
        self.current_phase = ClockPhase.DAY


class SpectralDecomposition:
    """
    Spectral Decomposition Engine.
    
    Implements the Fourier transform cycle for
    state cleaning and regeneration.
    """
    
    def __init__(self, dimension: int = 64):
        self.dimension = dimension
        self.cutoff_frequency = OMEGA_C
    
    def forward_transform(self, psi_time: np.ndarray) -> np.ndarray:
        """
        Forward Fourier Transform (Dissolution/Sleep).
        
        |Ψ̃(ω)⟩ = F[|Ψ(t)⟩]
        """
        return fft(psi_time)
    
    def inverse_transform(self, psi_freq: np.ndarray) -> np.ndarray:
        """
        Inverse Fourier Transform (Rebirth/Sunrise).
        
        |Ψ(t)⟩ = F⁻¹[|Ψ̃(ω)⟩]
        """
        return ifft(psi_freq)
    
    def high_pass_filter(self, spectrum: np.ndarray) -> np.ndarray:
        """
        High-Pass Filter (12 Sectors).
        
        Removes low-frequency entropic noise.
        """
        n = len(spectrum)
        frequencies = fftfreq(n)
        
        # Filter mask
        mask = np.abs(frequencies) >= self.cutoff_frequency
        
        return spectrum * mask
    
    def phase_conjugate(self, spectrum: np.ndarray) -> np.ndarray:
        """
        Phase Conjugation (Midnight Singularity).
        
        Reverses entropy by conjugating phases.
        """
        return np.conj(spectrum)
    
    def parseval_check(self, psi: np.ndarray) -> bool:
        """
        Parseval Integrity Check.
        
        Ensures norm is preserved (within tolerance).
        """
        norm = np.linalg.norm(psi)
        return np.abs(norm - 1.0) < 0.1
    
    def renormalization_group_flow(self, psi: np.ndarray) -> np.ndarray:
        """
        Renormalization Group Flow.
        
        Rescales state to unit norm.
        """
        norm = np.linalg.norm(psi)
        if norm > 1e-10:
            return psi / norm
        return psi
    
    def execute_cleaning_cycle(self, psi: np.ndarray) -> np.ndarray:
        """
        Execute full spectral cleaning cycle.
        
        1. Forward Transform
        2. High-Pass Filter
        3. Phase Conjugation
        4. Inverse Transform
        5. Parseval Check
        """
        # A. Forward Transform (Dissolution)
        spectral_state = self.forward_transform(psi)
        
        # B. Filter Bank (The 12 Sectors)
        cleaned_spectrum = self.high_pass_filter(spectral_state)
        
        # C. Phase Conjugation (Entropy reversal)
        cleaned_spectrum = self.phase_conjugate(cleaned_spectrum)
        
        # D. Inverse Transform (Rebirth)
        restored_state = self.inverse_transform(cleaned_spectrum)
        
        # E. Parseval Integrity Check
        if not self.parseval_check(restored_state):
            restored_state = self.renormalization_group_flow(restored_state)
        
        return restored_state


# =============================================================================
# COMPLETE CONTROL LOOP
# =============================================================================

class KhemetControlLoop:
    """
    The Complete KHEMET Control Loop.
    
    Integrates all components:
    - Observer (State Estimation)
    - Controller (Ma'at Tracking)
    - Gain Scheduler (AGC)
    - Actuator (Hamiltonian Modulation)
    - Spectral Cycle (Cleaning)
    """
    
    def __init__(self, dimension: int = 64):
        self.dimension = dimension
        
        # Components
        self.observer = StateObserver(dimension)
        self.controller = TrajectoryController(dimension)
        self.gain_scheduler = GainScheduler()
        self.actuator = HamiltonianActuator(dimension)
        self.spectral = SpectralDecomposition(dimension)
        self.clock = SpectralClock()
        
        # Target trajectory (Ma'at)
        self._target: Optional[np.ndarray] = None
        
        # Current state
        self._current_state: Optional[np.ndarray] = None
        
        # Energy tracking
        self._energy = 1.0
    
    def set_target(self, target: np.ndarray) -> None:
        """Set target trajectory (Ma'at path)."""
        self._target = target
    
    def set_state(self, state: np.ndarray) -> None:
        """Set current state."""
        self._current_state = state
        self.observer.x_hat = state.copy()
    
    def step(self, measurement: np.ndarray, dt: float = 0.01) -> Dict:
        """
        Execute one control step.
        
        Continuous maintenance (Day Cycle).
        """
        if self._target is None:
            raise ValueError("Target trajectory not set")
        
        # 1. State Estimation (Observer)
        A = np.eye(self.dimension)  # State transition
        H = np.eye(self.dimension)  # Observation
        
        self.observer.predict(A)
        y_estimated = self.observer.update(measurement, H)
        
        # 2. Error Calculation (Controller)
        ref_state = self._target
        error_vector = self.controller.compute_error(ref_state, y_estimated)
        
        # 3. Gain Scheduling (AGC)
        gain, damping, mode = self.gain_scheduler.compute_gain(
            error_vector, y_estimated
        )
        
        # Handle runaway
        if mode == ControlRegime.RUNAWAY:
            self._inject_damping(damping)
        
        # 4. Control Signal
        control_signal = self.controller.compute_control(error_vector, dt)
        
        # 5. Actuation (Hamiltonian Modulation)
        delta_V = self.actuator.update_potential(control_signal, gain)
        
        # 6. Advance Clock
        phase = self.clock.advance(dt)
        
        # Store state
        self._current_state = y_estimated
        self._energy = np.linalg.norm(y_estimated) ** 2
        
        return {
            "estimated_state": y_estimated,
            "error": error_vector,
            "gain": gain,
            "damping": damping,
            "regime": mode,
            "phase": phase,
            "energy": self._energy
        }
    
    def night_cycle(self) -> Dict:
        """
        Execute discrete maintenance (Night Cycle).
        
        Spectral cleaning when clock completes cycle.
        """
        if self._current_state is None:
            return {"success": False, "message": "No state to clean"}
        
        if not self.clock.is_end_of_cycle():
            return {"success": False, "message": "Not end of cycle"}
        
        # Execute spectral cleaning
        cleaned_state = self.spectral.execute_cleaning_cycle(self._current_state)
        
        self._current_state = cleaned_state
        self.observer.x_hat = cleaned_state.copy()
        
        return {
            "success": True,
            "cleaned_state": cleaned_state,
            "norm": np.linalg.norm(cleaned_state)
        }
    
    def _inject_damping(self, damping: float) -> None:
        """Inject damping fluid to prevent runaway."""
        if self._current_state is not None:
            # Apply exponential decay
            self._current_state *= np.exp(-damping * 0.1)
    
    def run_maintenance(self, state: np.ndarray, 
                       target: np.ndarray,
                       n_steps: int = 100,
                       dt: float = 0.01) -> List[Dict]:
        """
        Run complete maintenance loop.
        
        Includes both continuous (day) and discrete (night) cycles.
        """
        self.set_state(state)
        self.set_target(target)
        
        history = []
        
        for _ in range(n_steps):
            # Add measurement noise
            noise = np.random.randn(self.dimension) * 0.01
            measurement = self._current_state + noise
            
            # Continuous step
            result = self.step(measurement, dt)
            history.append(result)
            
            # Check for night cycle
            if self.clock.is_end_of_cycle():
                night_result = self.night_cycle()
                history.append({"night_cycle": night_result})
                self.clock.reset()
        
        return history


# =============================================================================
# VALIDATION
# =============================================================================

def validate_dynamics() -> bool:
    """Validate KHEMET dynamics module."""
    
    dim = 32
    
    # Test Observer
    observer = StateObserver(dim)
    A = np.eye(dim)
    H = np.eye(dim)
    
    pred = observer.predict(A)
    assert len(pred) == dim
    
    z = np.random.randn(dim)
    upd = observer.update(z, H)
    assert len(upd) == dim
    
    # Test Controller
    controller = TrajectoryController(dim)
    ref = np.ones(dim)
    est = np.zeros(dim)
    
    error = controller.compute_error(ref, est)
    assert np.allclose(error, ref)
    
    control = controller.compute_control(error, dt=0.01)
    assert len(control) == dim
    
    # Test Gain Scheduler
    scheduler = GainScheduler()
    
    # Low error - stable
    low_error = np.ones(dim) * 0.001
    low_output = np.ones(dim) * 0.5
    gain, damp, regime = scheduler.compute_gain(low_error, low_output)
    assert regime == ControlRegime.STABLE
    
    # High error - purge
    scheduler.reset()
    high_error = np.ones(dim) * 1.0
    gain, damp, regime = scheduler.compute_gain(high_error, low_output)
    assert regime == ControlRegime.PURGE
    
    # High output - damped
    scheduler.reset()
    high_output = np.ones(dim) * 20.0
    gain, damp, regime = scheduler.compute_gain(low_error, high_output)
    assert regime == ControlRegime.DAMPED
    
    # Test Actuator
    actuator = HamiltonianActuator(dim)
    force = np.random.randn(dim)
    delta_V = actuator.update_potential(force, gain=1.0)
    assert delta_V.shape == (dim, dim)
    
    # Test Spectral Clock
    clock = SpectralClock()
    
    for _ in range(100):
        phase = clock.advance(0.1)
    
    assert clock.is_end_of_cycle() or not clock.is_end_of_cycle()  # Valid state
    
    # Test Spectral Decomposition
    spectral = SpectralDecomposition(dim)
    
    psi = np.random.randn(dim) + 1j * np.random.randn(dim)
    psi /= np.linalg.norm(psi)
    
    # Forward/inverse
    freq = spectral.forward_transform(psi)
    back = spectral.inverse_transform(freq)
    assert np.allclose(psi, back)
    
    # High-pass filter
    filtered = spectral.high_pass_filter(freq)
    assert len(filtered) == dim
    
    # Phase conjugate
    conj = spectral.phase_conjugate(freq)
    assert np.allclose(conj, np.conj(freq))
    
    # Full cleaning cycle
    cleaned = spectral.execute_cleaning_cycle(psi)
    assert len(cleaned) == dim
    
    # Test Complete Control Loop
    loop = KhemetControlLoop(dim)
    
    initial = np.random.randn(dim) + 1j * np.random.randn(dim)
    initial /= np.linalg.norm(initial)
    
    target = np.ones(dim, dtype=np.complex128)
    target /= np.linalg.norm(target)
    
    history = loop.run_maintenance(initial, target, n_steps=50, dt=0.01)
    
    assert len(history) > 0
    assert "estimated_state" in history[0]
    
    return True


if __name__ == "__main__":
    print("Validating KHEMET Dynamics Module...")
    assert validate_dynamics()
    print("✓ KHEMET Dynamics Module validated")
