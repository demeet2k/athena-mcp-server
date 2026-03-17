"""
ATHENA OS - HDCS: AUTOMATIC GAIN CONTROL & STABILITY
=====================================================
Non-Linear Gain Control and Lyapunov Analysis

AUTOMATIC GAIN CONTROL (AGC):
    Modulates output response amplitude based on error signal magnitude.
    
    y(t) = G(e) × x(t)
    
    Where G(e) is the Gain Function.

OPERATING REGIMES:

REGIME I - LINEAR STABILITY (|e| < ε_crit):
    G(e) ≈ K_lin (constant gain)
    Negative feedback ensures asymptotic stability
    Re(s_i) < 0 ⟹ lim_{t→∞} e(t) = 0

REGIME II - NON-LINEAR SATURATION (|e| > ε_crit):
    Hopf Bifurcation occurs
    G(e) ∝ e^{λt} (exponential growth)
    Landau-Stuart: ẏ = αy - βy³

SOFT SATURATION (SAFETY PROTOCOL):
    Damping injection when output approaches limits
    y_clamped = L × tanh(G(e)x(t) / T_damp)

LYAPUNOV STABILITY:
    V(x) = xᵀSx (Energy of Disorder)
    For stability: V̇ < 0
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Callable, Any
from enum import Enum, auto
import numpy as np
from scipy import linalg


# =============================================================================
# GAIN REGIMES
# =============================================================================

class GainRegime(Enum):
    """Operating regimes of gain controller."""
    
    LINEAR = "linear"         # Normal operation, negative feedback
    PURGE = "purge"           # Non-linear, exponential amplification
    DAMPED = "damped"         # Soft saturation, safety mode
    SATURATED = "saturated"   # Hard limit reached


class StabilityType(Enum):
    """Types of stability."""
    
    ASYMPTOTICALLY_STABLE = "asymptotic"
    EXPONENTIALLY_STABLE = "exponential"
    MARGINALLY_STABLE = "marginal"
    UNSTABLE = "unstable"
    LYAPUNOV_STABLE = "lyapunov"


# =============================================================================
# GAIN FUNCTION
# =============================================================================

@dataclass
class GainFunction:
    """
    Non-Linear Gain Function G(e).
    
    G(e) = K_lin           if |e| < ε
    G(e) = α × e^{λe}      if |e| ≥ ε
    
    With soft saturation applied above threshold.
    """
    
    # Linear regime
    K_linear: float = 1.0
    
    # Nonlinear regime
    alpha: float = 1.0
    lambda_coeff: float = 0.1
    
    # Threshold
    epsilon_crit: float = 1.0
    
    # Saturation
    saturation_limit: float = 10.0
    temperature: float = 1.0  # Damping "temperature"
    
    def evaluate(self, error: float) -> Tuple[float, GainRegime]:
        """
        Evaluate gain function.
        
        Returns (gain, regime)
        """
        error_mag = np.abs(error)
        
        if error_mag < self.epsilon_crit:
            # Regime I: Linear
            return self.K_linear, GainRegime.LINEAR
        
        else:
            # Regime II: Non-linear
            raw_gain = self.alpha * np.exp(self.lambda_coeff * error_mag)
            
            # Check saturation
            if raw_gain > self.saturation_limit:
                # Apply soft saturation
                gain = self.saturation_limit * np.tanh(
                    raw_gain / (self.saturation_limit * self.temperature))
                return gain, GainRegime.SATURATED
            
            return raw_gain, GainRegime.PURGE
    
    def apply(self, error: float, input_signal: float) -> Tuple[float, GainRegime]:
        """
        Apply gain to input signal.
        
        y = G(e) × x
        """
        gain, regime = self.evaluate(error)
        output = gain * input_signal
        
        # Apply output limiting
        if np.abs(output) > self.saturation_limit:
            output = self.saturation_limit * np.sign(output)
            regime = GainRegime.SATURATED
        
        return output, regime


# =============================================================================
# AUTOMATIC GAIN CONTROL
# =============================================================================

class AutomaticGainControl:
    """
    Automatic Gain Control (AGC) System.
    
    Modulates system output based on error magnitude
    to maintain stability while allowing high-energy response.
    
    Features:
    - Bi-stable operation (linear/nonlinear)
    - Soft saturation with damping injection
    - Thermal runaway prevention
    """
    
    def __init__(self, K_linear: float = 1.0,
                 epsilon_crit: float = 1.0,
                 saturation_limit: float = 10.0):
        
        self.gain_func = GainFunction(
            K_linear=K_linear,
            epsilon_crit=epsilon_crit,
            saturation_limit=saturation_limit
        )
        
        # State tracking
        self._current_regime = GainRegime.LINEAR
        self._current_gain = K_linear
        
        # Damping parameters
        self._zeta_nominal = 0.7
        self._zeta_critical = 2.0
        
        # Energy tracking
        self._system_energy = 0.0
        self._max_safe_energy = 100.0
        
        # History
        self._gain_history: List[float] = []
        self._regime_history: List[GainRegime] = []
    
    def compute(self, error: float, input_signal: float) -> Dict:
        """
        Execute AGC computation.
        
        Returns dict with output, gain, regime, and damping.
        """
        error_mag = np.abs(error)
        
        # Compute gain
        gain, regime = self.gain_func.evaluate(error)
        
        # Check energy level
        output = gain * input_signal
        self._system_energy += output ** 2 * 0.01  # Integrate
        
        # Determine damping
        if self._system_energy > self._max_safe_energy:
            # Safety: inject critical damping
            damping = self._zeta_critical
            regime = GainRegime.DAMPED
            
            # Apply soft saturation
            output = self.gain_func.saturation_limit * np.tanh(
                output / self.gain_func.temperature)
            
            # Decay energy
            self._system_energy *= 0.9
        
        elif regime == GainRegime.PURGE:
            # Some damping in purge mode
            damping = self._zeta_nominal * 1.5
        
        else:
            damping = self._zeta_nominal
        
        # Update state
        self._current_regime = regime
        self._current_gain = gain
        
        # Record history
        self._gain_history.append(gain)
        self._regime_history.append(regime)
        
        return {
            "output": output,
            "gain": gain,
            "regime": regime.value,
            "damping": damping,
            "energy": self._system_energy
        }
    
    def reset(self) -> None:
        """Reset AGC state."""
        self._current_regime = GainRegime.LINEAR
        self._current_gain = self.gain_func.K_linear
        self._system_energy = 0.0
        self._gain_history.clear()
        self._regime_history.clear()
    
    def set_parameters(self, K_linear: float = None,
                       epsilon_crit: float = None,
                       saturation_limit: float = None) -> None:
        """Update AGC parameters."""
        if K_linear is not None:
            self.gain_func.K_linear = K_linear
        if epsilon_crit is not None:
            self.gain_func.epsilon_crit = epsilon_crit
        if saturation_limit is not None:
            self.gain_func.saturation_limit = saturation_limit
    
    def get_status(self) -> Dict:
        """Get AGC status."""
        return {
            "regime": self._current_regime.value,
            "gain": self._current_gain,
            "energy": self._system_energy,
            "history_length": len(self._gain_history)
        }


# =============================================================================
# LYAPUNOV ANALYSIS
# =============================================================================

class LyapunovAnalysis:
    """
    Lyapunov Stability Analysis.
    
    Uses Lyapunov's Direct Method:
    
    V(x) = xᵀSx (Lyapunov candidate function)
    
    For stability, require V̇ < 0:
    V̇(x) = xᵀ(AᵀS + SA)x < 0
    
    This holds if Q = -(AᵀS + SA) > 0 (positive definite)
    """
    
    def __init__(self, A: np.ndarray, Q: np.ndarray = None):
        """
        Initialize Lyapunov analysis.
        
        Args:
            A: System matrix (ẋ = Ax)
            Q: Penalty matrix for V̇ (default: identity)
        """
        self.A = np.atleast_2d(A)
        self.n = self.A.shape[0]
        
        self.Q = Q if Q is not None else np.eye(self.n)
        
        # Solve Lyapunov equation for S
        self._S = self._solve_lyapunov()
    
    def _solve_lyapunov(self) -> np.ndarray:
        """
        Solve continuous Lyapunov equation.
        
        AᵀS + SA = -Q
        """
        try:
            S = linalg.solve_continuous_lyapunov(self.A.T, -self.Q)
            return S
        except Exception:
            # Fallback if unstable
            return np.eye(self.n)
    
    def lyapunov_function(self, x: np.ndarray) -> float:
        """
        Evaluate Lyapunov function.
        
        V(x) = xᵀSx
        """
        x = np.atleast_1d(x)
        return float(x @ self._S @ x)
    
    def lyapunov_derivative(self, x: np.ndarray) -> float:
        """
        Evaluate Lyapunov derivative.
        
        V̇(x) = xᵀ(AᵀS + SA)x = -xᵀQx
        """
        x = np.atleast_1d(x)
        return float(-x @ self.Q @ x)
    
    def is_stable(self) -> bool:
        """
        Check if system is Lyapunov stable.
        
        Stable if S > 0 and V̇ < 0 for all x ≠ 0
        """
        # Check S is positive definite
        eigvals_S = np.linalg.eigvalsh(self._S)
        S_positive = np.all(eigvals_S > 0)
        
        # V̇ = -xᵀQx < 0 if Q > 0
        eigvals_Q = np.linalg.eigvalsh(self.Q)
        Q_positive = np.all(eigvals_Q > 0)
        
        return S_positive and Q_positive
    
    def stability_type(self) -> StabilityType:
        """Determine stability type."""
        eigenvalues = np.linalg.eigvals(self.A)
        max_real = np.max(np.real(eigenvalues))
        
        if max_real < -1e-10:
            if self.is_stable():
                return StabilityType.ASYMPTOTICALLY_STABLE
            return StabilityType.EXPONENTIALLY_STABLE
        
        elif max_real > 1e-10:
            return StabilityType.UNSTABLE
        
        else:
            return StabilityType.MARGINALLY_STABLE
    
    def decay_rate(self) -> float:
        """
        Compute exponential decay rate.
        
        ||x(t)|| ≤ ||x(0)|| × e^{-αt}
        
        α = min(eigenvalues of Q) / (2 × max(eigenvalues of S))
        """
        eigvals_Q = np.linalg.eigvalsh(self.Q)
        eigvals_S = np.linalg.eigvalsh(self._S)
        
        if np.max(eigvals_S) <= 0:
            return 0.0
        
        return float(np.min(eigvals_Q) / (2 * np.max(eigvals_S)))
    
    def region_of_attraction(self, c: float = 1.0) -> Dict:
        """
        Estimate region of attraction.
        
        Ω_c = {x : V(x) ≤ c}
        """
        # For quadratic V, region is ellipsoid
        # Semi-axes proportional to sqrt(c/eigenvalues(S))
        
        eigvals, eigvecs = np.linalg.eigh(self._S)
        
        semi_axes = np.sqrt(c / eigvals)
        
        return {
            "level_set": c,
            "semi_axes": semi_axes.tolist(),
            "principal_directions": eigvecs.tolist(),
            "volume": np.pi**(self.n/2) * np.prod(semi_axes) / np.math.gamma(self.n/2 + 1)
        }
    
    @property
    def S_matrix(self) -> np.ndarray:
        return self._S.copy()


# =============================================================================
# RICCATI SOLVER
# =============================================================================

class RiccatiSolver:
    """
    Algebraic Riccati Equation Solver.
    
    Continuous ARE: AᵀS + SA - SBR⁻¹BᵀS + Q = 0
    
    Used for LQR optimal control.
    """
    
    def __init__(self, A: np.ndarray, B: np.ndarray,
                 Q: np.ndarray = None, R: np.ndarray = None):
        self.A = np.atleast_2d(A)
        self.B = np.atleast_2d(B)
        
        self.n = self.A.shape[0]
        self.m = self.B.shape[1]
        
        self.Q = Q if Q is not None else np.eye(self.n)
        self.R = R if R is not None else np.eye(self.m)
        
        self._S = None
        self._solved = False
    
    def solve(self) -> np.ndarray:
        """
        Solve continuous-time ARE.
        
        Returns S matrix.
        """
        try:
            self._S = linalg.solve_continuous_are(
                self.A, self.B, self.Q, self.R)
            self._solved = True
        except Exception:
            # Fallback
            self._S = np.eye(self.n)
            self._solved = False
        
        return self._S.copy()
    
    def optimal_gain(self) -> np.ndarray:
        """
        Compute optimal feedback gain.
        
        K = R⁻¹BᵀS
        """
        if not self._solved:
            self.solve()
        
        return np.linalg.inv(self.R) @ self.B.T @ self._S
    
    def closed_loop_matrix(self) -> np.ndarray:
        """
        Compute closed-loop system matrix.
        
        A_cl = A - BK
        """
        K = self.optimal_gain()
        return self.A - self.B @ K
    
    def closed_loop_poles(self) -> np.ndarray:
        """Get closed-loop eigenvalues."""
        A_cl = self.closed_loop_matrix()
        return np.linalg.eigvals(A_cl)
    
    def verify_solution(self, tol: float = 1e-6) -> bool:
        """
        Verify ARE solution.
        
        Check AᵀS + SA - SBR⁻¹BᵀS + Q ≈ 0
        """
        if self._S is None:
            return False
        
        R_inv = np.linalg.inv(self.R)
        residual = (self.A.T @ self._S + self._S @ self.A - 
                   self._S @ self.B @ R_inv @ self.B.T @ self._S + self.Q)
        
        return float(np.linalg.norm(residual)) < tol
    
    @property
    def solution(self) -> np.ndarray:
        if self._S is None:
            self.solve()
        return self._S.copy()


# =============================================================================
# BIFURCATION ANALYSIS
# =============================================================================

class BifurcationAnalysis:
    """
    Bifurcation Analysis.
    
    Detects when system parameters cross stability boundaries.
    
    Hopf Bifurcation: Eigenvalues cross imaginary axis
    Leads to transition from stable to oscillatory behavior.
    """
    
    def __init__(self, A_func: Callable[[float], np.ndarray]):
        """
        Initialize bifurcation analysis.
        
        Args:
            A_func: Function mapping parameter μ to system matrix A(μ)
        """
        self.A_func = A_func
    
    def eigenvalues_at(self, mu: float) -> np.ndarray:
        """Get eigenvalues at parameter value μ."""
        A = self.A_func(mu)
        return np.linalg.eigvals(A)
    
    def find_hopf_bifurcation(self, mu_range: Tuple[float, float],
                              resolution: int = 100) -> Optional[float]:
        """
        Find Hopf bifurcation point.
        
        Searches for parameter value where max(Re(λ)) crosses zero.
        """
        mu_values = np.linspace(mu_range[0], mu_range[1], resolution)
        
        max_real_prev = None
        
        for mu in mu_values:
            eigvals = self.eigenvalues_at(mu)
            max_real = np.max(np.real(eigvals))
            
            if max_real_prev is not None:
                # Check for sign change
                if max_real_prev < 0 and max_real > 0:
                    # Bifurcation between these values
                    return float((mu + mu_values[np.where(mu_values == mu)[0][0] - 1]) / 2)
            
            max_real_prev = max_real
        
        return None
    
    def stability_boundary(self, mu_range: Tuple[float, float],
                          resolution: int = 100) -> List[Dict]:
        """
        Map stability boundary.
        
        Returns list of (parameter, eigenvalue, stable) tuples.
        """
        mu_values = np.linspace(mu_range[0], mu_range[1], resolution)
        results = []
        
        for mu in mu_values:
            eigvals = self.eigenvalues_at(mu)
            max_real = np.max(np.real(eigvals))
            
            results.append({
                "parameter": float(mu),
                "max_real_eigenvalue": float(max_real),
                "stable": max_real < 0
            })
        
        return results


# =============================================================================
# VALIDATION
# =============================================================================

def validate_agc_stability() -> bool:
    """Validate AGC and stability module."""
    
    # Test GainFunction
    gain_func = GainFunction(K_linear=1.0, epsilon_crit=1.0)
    
    gain, regime = gain_func.evaluate(0.5)
    assert regime == GainRegime.LINEAR
    assert gain == 1.0
    
    gain, regime = gain_func.evaluate(2.0)
    assert regime == GainRegime.PURGE
    assert gain > 1.0
    
    # Test AutomaticGainControl
    agc = AutomaticGainControl(K_linear=1.0, epsilon_crit=1.0)
    
    result = agc.compute(error=0.5, input_signal=1.0)
    assert result["regime"] == "linear"
    
    result = agc.compute(error=5.0, input_signal=1.0)
    assert result["regime"] in ["purge", "saturated", "damped"]
    
    # Test LyapunovAnalysis
    # Stable system: ẋ = -x
    A_stable = np.array([[-1.0]])
    lyap = LyapunovAnalysis(A_stable)
    
    assert lyap.is_stable()
    assert lyap.stability_type() == StabilityType.ASYMPTOTICALLY_STABLE
    
    V = lyap.lyapunov_function(np.array([1.0]))
    assert V > 0
    
    V_dot = lyap.lyapunov_derivative(np.array([1.0]))
    assert V_dot < 0  # Decreasing
    
    decay = lyap.decay_rate()
    assert decay > 0
    
    # Unstable system: ẋ = x
    A_unstable = np.array([[1.0]])
    lyap_unstable = LyapunovAnalysis(A_unstable)
    
    assert lyap_unstable.stability_type() == StabilityType.UNSTABLE
    
    # Test RiccatiSolver
    A = np.array([[0, 1], [-2, -3]])
    B = np.array([[0], [1]])
    
    riccati = RiccatiSolver(A, B)
    S = riccati.solve()
    
    assert S.shape == (2, 2)
    
    K = riccati.optimal_gain()
    assert K.shape == (1, 2)
    
    poles = riccati.closed_loop_poles()
    assert np.all(np.real(poles) < 0)  # Stable closed-loop
    
    # Test BifurcationAnalysis
    def A_param(mu):
        return np.array([[mu, 1], [-1, mu]])
    
    bifurc = BifurcationAnalysis(A_param)
    
    eigvals = bifurc.eigenvalues_at(mu=-1.0)
    assert len(eigvals) == 2
    
    # Find Hopf bifurcation (should be near μ = 0)
    hopf_point = bifurc.find_hopf_bifurcation((-2.0, 2.0))
    if hopf_point is not None:
        assert abs(hopf_point) < 0.5
    
    return True


if __name__ == "__main__":
    print("Validating AGC & Stability Module...")
    assert validate_agc_stability()
    print("✓ AGC & Stability Module validated")
