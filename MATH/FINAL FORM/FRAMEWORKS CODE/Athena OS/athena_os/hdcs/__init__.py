"""
ATHENA OS - HDCS: HYBRID DYNAMICAL CONTROL SYSTEM
==================================================
Complete Cybernetic Control Framework

CORE CONCEPT:
    The HDCS implements a complete feedback control loop for
    autonomous agents operating in partially observable environments.
    
    Components:
    - SENSORS: State estimation (POVM, Kalman filtering)
    - CONTROLLERS: Control laws (PID, LQR, LQG)
    - ACTUATORS: Hamiltonian modulation
    - STABILITY: Lyapunov analysis, AGC
    - SPECTRAL: Fourier domain processing

THE AUTOPOIETIC LOOP:

    ┌─────────────────────────────────────────────────┐
    │                                                 │
    │   ┌─────────┐    ┌────────────┐    ┌────────┐  │
    │   │ SENSOR  │───▶│ CONTROLLER │───▶│ACTUATOR│  │
    │   │  (Ŝ)    │    │    (Ĉ)     │    │  (Â)   │  │
    │   └────▲────┘    └────────────┘    └───┬────┘  │
    │        │                               │       │
    │        │         ┌────────┐           │       │
    │        └─────────│ SYSTEM │◀──────────┘       │
    │                  │  (Ĥ)   │                   │
    │                  └────────┘                   │
    │                                               │
    └───────────────────────────────────────────────┘

CONTROL LOOP ALGORITHM:
    def feedback_loop(agent, target_trajectory, t):
        # 1. SENSOR (Sia): State Estimation
        y_meas = measure_observable(agent.state, operator=S_HAT)
        y_est = kalman_filter.update(y_meas, t)
        
        # 2. CONTROLLER (Hu): Error Calculation
        r_ref = target_trajectory.get_point(t)
        error = r_ref - y_est
        u_control = PID.compute(error)
        
        # 3. ACTUATOR (Heka): Hamiltonian Modulation
        H_ctrl = u_control * GENERATOR_G
        agent.hamiltonian += H_ctrl
        
        return agent

MODULES:

1. SENSORS (sensors.py)
   - POVM (Positive Operator-Valued Measure)
   - SensorOperator with weak measurements
   - KalmanFilter for optimal state estimation
   - ExtendedKalmanFilter for nonlinear systems

2. CONTROLLERS (controllers.py)
   - ReferenceTrajectory for target paths
   - ErrorVector tracking
   - PIDController (Proportional-Integral-Derivative)
   - LQRController (Linear Quadratic Regulator)
   - LQGController (Linear Quadratic Gaussian)
   - TransferFunction for frequency domain analysis

3. ACTUATORS (actuators.py)
   - GeneratorOperator (Lie algebra elements)
   - ControlHamiltonian
   - ActuatorOperator for Hamiltonian modulation
   - ModulatedActuator with time-dependent drives
   - OptimalActuator with pulse optimization

4. STABILITY (stability.py)
   - GainFunction (linear/nonlinear regimes)
   - AutomaticGainControl (AGC)
   - LyapunovAnalysis for stability proofs
   - RiccatiSolver for optimal control
   - BifurcationAnalysis for parameter studies

5. SPECTRAL (spectral.py)
   - FourierOperator for domain transforms
   - SpectralFilter (LP, HP, BP, BS, notch)
   - SpectralCleaner for noise removal
   - SpectralCycle for day/night processing
"""

from __future__ import annotations

# =============================================================================
# SENSORS
# =============================================================================

from .sensors import (
    # Enums
    MeasurementType,
    ObservableType,
    
    # POVM
    EffectOperator,
    POVM,
    
    # Sensor Operator
    SensorOperator,
    
    # Kalman Filters
    KalmanFilter,
    ExtendedKalmanFilter,
    
    # Validation
    validate_sensors,
)

# =============================================================================
# CONTROLLERS
# =============================================================================

from .controllers import (
    # Enums
    ControllerType,
    StabilityStatus,
    
    # Reference
    ReferenceTrajectory,
    ErrorVector,
    
    # Controllers
    PIDController,
    LQRController,
    LQGController,
    
    # Transfer Function
    TransferFunction,
    
    # Validation
    validate_controllers,
)

# =============================================================================
# ACTUATORS
# =============================================================================

from .actuators import (
    # Enums
    ActuatorType,
    ModulationType,
    
    # Generators
    GeneratorOperator,
    ControlHamiltonian,
    
    # Actuators
    ActuatorOperator,
    ModulatedActuator,
    OptimalActuator,
    
    # Validation
    validate_actuators,
)

# =============================================================================
# STABILITY
# =============================================================================

from .stability import (
    # Enums
    GainRegime,
    StabilityType,
    
    # Gain Control
    GainFunction,
    AutomaticGainControl,
    
    # Stability Analysis
    LyapunovAnalysis,
    RiccatiSolver,
    BifurcationAnalysis,
    
    # Validation
    validate_agc_stability,
)

# =============================================================================
# SPECTRAL
# =============================================================================

from .spectral import (
    # Enums
    DomainState,
    FilterType,
    
    # Fourier
    FourierOperator,
    
    # Filters
    SpectralFilter,
    SpectralCleaner,
    
    # Cycle
    SpectralCycle,
    
    # Validation
    validate_spectral,
)


# =============================================================================
# VALIDATION
# =============================================================================

def validate_hdcs() -> bool:
    """Validate complete HDCS module."""
    assert validate_sensors()
    assert validate_controllers()
    assert validate_actuators()
    assert validate_agc_stability()
    assert validate_spectral()
    return True


# =============================================================================
# INTEGRATED CONTROL SYSTEM
# =============================================================================

import numpy as np
from typing import Dict, Optional, Callable


class HDCSController:
    """
    Complete Hybrid Dynamical Control System.
    
    Integrates sensors, controllers, actuators, and stability
    analysis into a unified feedback control framework.
    
    The Autopoietic Loop:
    1. Sense (POVM/Kalman) → Estimate state
    2. Control (PID/LQR) → Compute action
    3. Actuate (Hamiltonian) → Apply control
    4. Stabilize (AGC/Lyapunov) → Ensure bounded response
    """
    
    def __init__(self, state_dim: int = 4,
                 measurement_dim: int = 1,
                 control_dim: int = 1):
        self.n = state_dim
        self.m = measurement_dim
        self.p = control_dim
        
        # Default system matrices
        self.A = np.eye(state_dim)
        self.B = np.zeros((state_dim, control_dim))
        self.B[0, 0] = 1.0
        self.C = np.zeros((measurement_dim, state_dim))
        self.C[0, 0] = 1.0
        
        # Components
        self.sensor = SensorOperator(state_dim)
        self.kalman = KalmanFilter(state_dim, measurement_dim)
        self.pid = PIDController(state_dim, Kp=1.0, Ki=0.1, Kd=0.01)
        self.lqr = None  # Created when system matrices set
        self.actuator = ActuatorOperator(state_dim)
        self.agc = AutomaticGainControl()
        
        # Spectral processing
        self.spectral = SpectralCycle()
        
        # Reference trajectory
        self.reference = ReferenceTrajectory(state_dim)
        
        # State
        self._state = np.zeros(state_dim, dtype=complex)
        self._control = np.zeros(control_dim)
        self._time = 0.0
    
    def set_system_matrices(self, A: np.ndarray = None,
                           B: np.ndarray = None,
                           C: np.ndarray = None) -> None:
        """Set system dynamics matrices."""
        if A is not None:
            self.A = np.atleast_2d(A)
        if B is not None:
            self.B = np.atleast_2d(B)
        if C is not None:
            self.C = np.atleast_2d(C)
        
        # Update components
        self.kalman.set_system_matrices(self.A, self.B, self.C)
        
        # Create LQR controller
        try:
            self.lqr = LQRController(self.A, self.B)
        except Exception:
            pass
    
    def set_initial_state(self, state: np.ndarray) -> None:
        """Set initial state."""
        self._state = np.atleast_1d(state).astype(complex)
    
    def set_reference(self, setpoint: np.ndarray,
                     trajectory_type: str = "constant") -> None:
        """Set reference trajectory."""
        self.reference = ReferenceTrajectory(self.n, trajectory_type)
        self.reference.set_setpoint(setpoint)
    
    def step(self, dt: float = 0.1, 
             external_measurement: float = None) -> Dict:
        """
        Execute one control loop iteration.
        
        Returns dict with state, control, error, and status.
        """
        # 1. SENSE - Get measurement
        if external_measurement is not None:
            measurement = external_measurement
        else:
            measurement = self.sensor.measure(self._state)
        
        # 2. ESTIMATE - Kalman filter
        state_estimate = self.kalman.filter_step(measurement, dt=dt)
        
        # 3. REFERENCE - Get target
        reference = self.reference.evaluate(self._time)
        
        # 4. CONTROL - Compute control signal
        control_pid = self.pid.compute(reference, state_estimate[:self.n], dt)
        
        # Optional LQR
        control_lqr = np.zeros(self.p)
        if self.lqr is not None:
            control_lqr = self.lqr.compute(state_estimate[:self.n])
        
        # Blend controls (favor LQR if available)
        alpha = 0.7 if self.lqr is not None else 0.0
        control = alpha * control_lqr[:self.p] + (1 - alpha) * control_pid[:self.p]
        
        # 5. AGC - Automatic gain control
        error_norm = self.pid.error.norm
        agc_result = self.agc.compute(error_norm, np.linalg.norm(control))
        
        # Scale control by AGC
        control = control * (agc_result["gain"] / (self.agc.gain_func.K_linear + 1e-10))
        
        # 6. ACTUATE - Apply control
        self._state = self.actuator.apply_control(
            self._state, control, self._time, dt)
        
        # 7. SPECTRAL - Process cycle
        spectral_result = self.spectral.advance(dt)
        
        # Update time
        self._time += dt
        self._control = control
        
        return {
            "time": self._time,
            "state": np.real(self._state).tolist(),
            "state_estimate": state_estimate.tolist(),
            "control": control.tolist(),
            "error": self.pid.error.current.tolist(),
            "error_norm": error_norm,
            "agc": agc_result,
            "spectral": spectral_result
        }
    
    def run(self, duration: float, dt: float = 0.1) -> List[Dict]:
        """Run control loop for specified duration."""
        results = []
        
        while self._time < duration:
            result = self.step(dt)
            results.append(result)
        
        return results
    
    def analyze_stability(self) -> Dict:
        """Perform stability analysis."""
        # Lyapunov analysis
        lyap = LyapunovAnalysis(self.A)
        
        # Closed-loop analysis if LQR available
        if self.lqr is not None:
            A_cl = self.lqr.closed_loop_matrix()
            lyap_cl = LyapunovAnalysis(A_cl)
        else:
            lyap_cl = lyap
        
        return {
            "open_loop_stable": lyap.is_stable(),
            "open_loop_type": lyap.stability_type().value,
            "closed_loop_stable": lyap_cl.is_stable(),
            "closed_loop_type": lyap_cl.stability_type().value,
            "decay_rate": lyap_cl.decay_rate()
        }
    
    def reset(self) -> None:
        """Reset controller state."""
        self._state = np.zeros(self.n, dtype=complex)
        self._control = np.zeros(self.p)
        self._time = 0.0
        self.pid.reset()
        self.kalman.reset()
        self.agc.reset()
    
    def get_status(self) -> Dict:
        """Get system status."""
        return {
            "time": self._time,
            "state_dim": self.n,
            "control_dim": self.p,
            "state": np.real(self._state).tolist(),
            "control": self._control.tolist(),
            "error_norm": self.pid.error.norm,
            "agc_regime": self.agc._current_regime.value,
            "spectral_domain": self.spectral.domain.value
        }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Sensors
    "MeasurementType", "ObservableType",
    "EffectOperator", "POVM",
    "SensorOperator",
    "KalmanFilter", "ExtendedKalmanFilter",
    
    # Controllers
    "ControllerType", "StabilityStatus",
    "ReferenceTrajectory", "ErrorVector",
    "PIDController", "LQRController", "LQGController",
    "TransferFunction",
    
    # Actuators
    "ActuatorType", "ModulationType",
    "GeneratorOperator", "ControlHamiltonian",
    "ActuatorOperator", "ModulatedActuator", "OptimalActuator",
    
    # Stability
    "GainRegime", "StabilityType",
    "GainFunction", "AutomaticGainControl",
    "LyapunovAnalysis", "RiccatiSolver", "BifurcationAnalysis",
    
    # Spectral
    "DomainState", "FilterType",
    "FourierOperator", "SpectralFilter",
    "SpectralCleaner", "SpectralCycle",
    
    # Integrated System
    "HDCSController",
    
    # Validation
    "validate_hdcs",
]

__version__ = "1.0.0"
__module_name__ = "hdcs"


if __name__ == "__main__":
    print("=" * 70)
    print("ATHENA OS - HYBRID DYNAMICAL CONTROL SYSTEM")
    print("Cybernetic Feedback Control Framework")
    print("=" * 70)
    print(f"Version: {__version__}")
    
    print("\nValidating...")
    if validate_hdcs():
        print("✓ All components validated")
    
    # Demo
    print("\n--- HDCS Controller Demo ---")
    
    controller = HDCSController(state_dim=2, measurement_dim=1, control_dim=1)
    
    # Set system: damped oscillator
    A = np.array([[0, 1], [-1, -0.5]])
    B = np.array([[0], [1]])
    C = np.array([[1, 0]])
    
    controller.set_system_matrices(A, B, C)
    controller.set_initial_state(np.array([1.0, 0.0]))
    controller.set_reference(np.array([0.0, 0.0]))
    
    print("\n1. Running control loop...")
    results = controller.run(duration=5.0, dt=0.1)
    
    print(f"   Steps executed: {len(results)}")
    print(f"   Final error: {results[-1]['error_norm']:.4f}")
    
    print("\n2. Stability analysis...")
    stability = controller.analyze_stability()
    print(f"   Open-loop stable: {stability['open_loop_stable']}")
    print(f"   Closed-loop stable: {stability['closed_loop_stable']}")
    print(f"   Decay rate: {stability['decay_rate']:.4f}")
    
    print("\n3. Final status...")
    status = controller.get_status()
    print(f"   Time: {status['time']:.2f}")
    print(f"   AGC regime: {status['agc_regime']}")
    print(f"   Spectral domain: {status['spectral_domain']}")
    
    print("\n" + "=" * 70)
    print("HDCS: The Autopoietic Control Loop")
    print("=" * 70)
