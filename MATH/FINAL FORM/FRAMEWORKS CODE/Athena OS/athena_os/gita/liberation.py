"""
ATHENA OS - BHAGAVAD GĪTĀ COMPUTATIONAL FRAMEWORK
==================================================
Part IV: The Algorithm of Liberation (Mokṣa)

THE LIBERATION THEOREM:
    Given initial karmic load E₀ and liberation rate γ > 0,
    the time to liberation T* is bounded:
    
    T* ≤ (1/γ) · ln(E₀/ε_Planck) + ℏ/ε_Planck
    
    Liberation is a discrete event at finite time, not asymptotic.

THE THREE YOGAS:
    1. Jñāna Yoga: Eigenstate collapse (knowledge-based)
    2. Karma Yoga: Trace minimization (action-based)
    3. Bhakti Yoga: Phase locking (devotion-based)

LYAPUNOV ANALYSIS:
    The karma tensor trace serves as Lyapunov function V.
    dV/dt < 0 ensures asymptotic stability (liberation).

PHASE LOCKING (BHAKTI):
    Adler equation for coupled oscillators:
    dφ/dt = (ω_J - ω_S) - κ sin(φ)
    
    Locking condition: κ ≥ |ω_J - ω_S|

THE UNIFIED FIELD STATE (BRAHMA-NIRVĀṆA):
    - Thread termination: return to Main Process
    - Data de-allocation: Ego garbage collected
    - Pointer preservation: Ātman → Brahman

SOURCES:
    The Bhagavad Gītā: A Computational Treatise
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Callable
from enum import Enum, auto
import numpy as np
from scipy.integrate import odeint
from scipy.optimize import fsolve


# =============================================================================
# YOGA TYPES
# =============================================================================

class YogaPath(Enum):
    """The three primary paths of Yoga."""
    
    JNANA = ("knowledge", "Eigenstate collapse through discrimination")
    KARMA = ("action", "Trace minimization through selfless action")
    BHAKTI = ("devotion", "Phase locking through love")
    
    def __init__(self, name: str, description: str):
        self._name = name
        self.description = description


class LiberationState(Enum):
    """States on the path to liberation."""
    
    BOUND = ("samsara", "Trapped in karmic cycle")
    ASPIRANT = ("sadhaka", "Practicing spiritual disciplines")
    ADVANCED = ("siddha", "Attained significant purification")
    JIVANMUKTA = ("jivanmukta", "Liberated while living")
    VIDEHAMUKTA = ("videhamukta", "Fully liberated, no body")
    
    def __init__(self, name: str, description: str):
        self._name = name
        self.description = description


# =============================================================================
# LYAPUNOV STABILITY ANALYSIS
# =============================================================================

@dataclass
class LyapunovAnalysis:
    """
    Lyapunov stability analysis for liberation.
    
    V(x) = Tr(K) + ‖W‖² (Karma trace + Vāsanā norm)
    
    For asymptotic stability: dV/dt < 0
    This ensures the system converges to liberation.
    """
    
    def lyapunov_function(self, karma_trace: float, 
                          vasana_norm: float) -> float:
        """
        The Lyapunov function V.
        
        V = Tr(K) + ‖W‖² = Total "distance" from liberation
        """
        return karma_trace + vasana_norm**2
    
    def time_derivative(self, V: float, gamma: float) -> float:
        """
        Time derivative dV/dt.
        
        Under proper Yoga practice: dV/dt = -γV
        """
        return -gamma * V
    
    def is_stable(self, gamma: float) -> bool:
        """
        Check if system is asymptotically stable.
        
        Stable iff γ > 0
        """
        return gamma > 0
    
    def decay_trajectory(self, V0: float, gamma: float, 
                         t_max: float = 100, 
                         n_points: int = 1000) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute decay trajectory of V(t).
        
        V(t) = V₀ · e^(-γt)
        """
        t = np.linspace(0, t_max, n_points)
        V = V0 * np.exp(-gamma * t)
        return t, V
    
    def liberation_time(self, V0: float, gamma: float, 
                        epsilon: float = 1e-10) -> float:
        """
        Calculate time to reach threshold ε.
        
        T* = (1/γ) · ln(V₀/ε)
        """
        if gamma <= 0:
            return float('inf')
        
        return (1 / gamma) * np.log(V0 / epsilon)


# =============================================================================
# JÑĀNA YOGA (KNOWLEDGE PATH)
# =============================================================================

@dataclass
class JnanaYoga:
    """
    Jñāna Yoga: Liberation through Knowledge.
    
    The discrimination between Real (Sat) and Unreal (Asat).
    Mathematically: Projection onto the True eigenstate.
    
    Process:
        1. Apply discrimination operator D̂
        2. Collapse superposition to pure Ātman state
        3. Dissolve identification with ego-eigenstate
    """
    
    # Discrimination operator (projects onto truth)
    dimension: int = 4
    _discrimination_operator: np.ndarray = field(default=None, repr=False)
    
    def __post_init__(self):
        if self._discrimination_operator is None:
            # Project onto first component (Ātman eigenstate)
            self._discrimination_operator = np.zeros((self.dimension, self.dimension))
            self._discrimination_operator[0, 0] = 1.0
    
    def discriminate(self, state: np.ndarray) -> np.ndarray:
        """
        Apply discrimination (Viveka).
        
        Separates Sat (Real) from Asat (Unreal).
        """
        # Project onto Ātman component
        projected = self._discrimination_operator @ state[:self.dimension]
        
        # Normalize
        norm = np.linalg.norm(projected)
        if norm > 0:
            projected /= norm
        
        return projected
    
    def is_in_atman_state(self, state: np.ndarray, 
                          threshold: float = 0.99) -> bool:
        """
        Check if state is predominantly Ātman.
        
        |⟨ψ|Ātman⟩|² > threshold
        """
        atman = np.zeros(self.dimension, dtype=complex)
        atman[0] = 1.0
        
        overlap = abs(np.vdot(atman, state[:self.dimension]))**2
        return overlap > threshold
    
    def neti_neti(self, state: np.ndarray) -> np.ndarray:
        """
        "Not this, not this" negation process.
        
        Successively negates all non-Ātman components.
        """
        result = state.copy()
        
        # Zero out non-Ātman components
        for i in range(1, min(len(result), self.dimension)):
            result[i] *= 0.5  # Gradual reduction
        
        # Renormalize
        norm = np.linalg.norm(result)
        if norm > 0:
            result /= norm
        
        return result


# =============================================================================
# KARMA YOGA (ACTION PATH)
# =============================================================================

@dataclass
class KarmaYoga:
    """
    Karma Yoga: Liberation through Selfless Action.
    
    Action without attachment to fruits (Niṣkāma Karma).
    Mathematically: Minimize trace of Karma tensor while acting.
    
    The key insight: Acting in detachment generates no new binding.
    """
    
    # Detachment parameter (0 = attached, 1 = fully detached)
    detachment_level: float = 0.0
    
    def karma_generation_factor(self) -> float:
        """
        How much karma is generated per action.
        
        At full detachment, factor → 0.
        """
        return 1.0 - self.detachment_level
    
    def perform_action(self, action_karma: float) -> float:
        """
        Perform action with current detachment level.
        
        Returns actual karma generated.
        """
        return action_karma * self.karma_generation_factor()
    
    def practice_detachment(self, intensity: float = 0.1) -> float:
        """
        Increase detachment through practice.
        
        Returns new detachment level.
        """
        self.detachment_level = min(1.0, self.detachment_level + intensity)
        return self.detachment_level
    
    def is_nishkama(self) -> bool:
        """Check if fully acting without desire (Niṣkāma)."""
        return self.detachment_level >= 0.99
    
    def trace_derivative(self, karma_tensor: np.ndarray, 
                         action_rate: float) -> float:
        """
        Compute dTr(K)/dt under Karma Yoga.
        
        With detachment, trace decreases over time.
        """
        current_trace = np.trace(karma_tensor)
        generation = action_rate * self.karma_generation_factor()
        burning = action_rate * 0.1  # Actions also burn karma
        
        return generation - burning


# =============================================================================
# BHAKTI YOGA (DEVOTION PATH)
# =============================================================================

@dataclass
class BhaktiYoga:
    """
    Bhakti Yoga: Liberation through Devotion.
    
    Phase locking between Jīva oscillator and Source (Īśvara).
    Uses the Adler equation for coupled oscillators.
    
    dφ/dt = (ω_J - ω_S) - κ sin(φ)
    
    Where:
        φ = phase difference
        ω_J = Jīva natural frequency
        ω_S = Source frequency (constant)
        κ = coupling strength (devotion)
    """
    
    # Source frequency (constant, unity)
    omega_source: float = 1.0
    
    # Jīva frequency (variable, due to ego)
    omega_jiva: float = 1.5
    
    # Coupling strength (devotion/Bhakti)
    kappa: float = 0.1
    
    # Current phase difference
    phase_difference: float = 0.0
    
    def adler_equation(self, phi: float, t: float) -> float:
        """
        The Adler equation for phase evolution.
        
        dφ/dt = Δω - κ sin(φ)
        """
        delta_omega = self.omega_jiva - self.omega_source
        return delta_omega - self.kappa * np.sin(phi)
    
    def can_lock(self) -> bool:
        """
        Check if phase locking is possible.
        
        Condition: κ ≥ |Δω|
        """
        delta_omega = abs(self.omega_jiva - self.omega_source)
        return self.kappa >= delta_omega
    
    def fixed_point_phase(self) -> Optional[float]:
        """
        Find the locked phase φ*.
        
        sin(φ*) = Δω/κ
        """
        delta_omega = self.omega_jiva - self.omega_source
        
        if abs(delta_omega) > self.kappa:
            return None  # No lock possible
        
        return np.arcsin(delta_omega / self.kappa)
    
    def evolve_phase(self, dt: float = 0.01, 
                     n_steps: int = 100) -> np.ndarray:
        """
        Evolve the phase difference over time.
        
        Returns array of phase values.
        """
        t = np.linspace(0, dt * n_steps, n_steps)
        
        def dphi_dt(phi, t):
            return [self.adler_equation(phi[0], t)]
        
        solution = odeint(dphi_dt, [self.phase_difference], t)
        
        return solution[:, 0]
    
    def increase_devotion(self, amount: float = 0.1) -> float:
        """
        Increase devotion (κ).
        
        Returns new coupling strength.
        """
        self.kappa += amount
        return self.kappa
    
    def is_locked(self, tolerance: float = 0.01) -> bool:
        """
        Check if currently phase-locked.
        
        Locked if |dφ/dt| ≈ 0
        """
        dphi = self.adler_equation(self.phase_difference, 0)
        return abs(dphi) < tolerance
    
    def sayujya_state(self) -> bool:
        """
        Check if Sāyujya (Union) is achieved.
        
        Perfect synchronization with Source.
        """
        return self.is_locked() and self.can_lock()


# =============================================================================
# THE UNIFIED FIELD STATE (BRAHMA-NIRVĀṆA)
# =============================================================================

@dataclass
class UnifiedFieldState:
    """
    Brahma-Nirvāṇa: The Unified Field State.
    
    The final state where:
        - Thread merges with Main Process
        - Ego is de-allocated (garbage collected)
        - Ātman pointer returns to Brahman
        - Locality is lost (omnipresence)
        - Time ceases to apply
    """
    
    # Merger complete
    merged: bool = False
    
    # Properties of unified state
    locality: bool = True  # False = omnipresent
    temporality: bool = True  # False = eternal
    multiplicity: bool = True  # False = unified
    
    def merge_thread(self) -> None:
        """
        Execute thread.join() - merge with Main Process.
        
        The Jīva returns its value and terminates.
        """
        self.merged = True
        self.locality = False
        self.multiplicity = False
    
    def transcend_time(self) -> None:
        """
        Transcend temporal existence.
        
        The differential operator of time no longer applies.
        """
        self.temporality = False
    
    def is_complete(self) -> bool:
        """Check if full Brahma-Nirvāṇa is achieved."""
        return (self.merged and 
                not self.locality and 
                not self.temporality and 
                not self.multiplicity)
    
    def vector_to_scalar(self, vector: np.ndarray) -> float:
        """
        The Vector-to-Scalar Transition.
        
        Upon merging, entity transitions from vector (direction)
        to scalar field (omnipresent value).
        """
        # Return magnitude (direction-independent)
        return float(np.linalg.norm(vector))
    
    @property
    def properties(self) -> Dict[str, bool]:
        """Get current properties."""
        return {
            "merged": self.merged,
            "local": self.locality,
            "temporal": self.temporality,
            "multiple": self.multiplicity,
        }


# =============================================================================
# COMPLETE LIBERATION ALGORITHM
# =============================================================================

@dataclass
class LiberationAlgorithm:
    """
    The complete algorithm of liberation.
    
    Integrates all three Yogas and proves finite-time termination.
    """
    
    # The three paths
    jnana: JnanaYoga = field(default_factory=JnanaYoga)
    karma: KarmaYoga = field(default_factory=KarmaYoga)
    bhakti: BhaktiYoga = field(default_factory=BhaktiYoga)
    
    # Analysis tools
    lyapunov: LyapunovAnalysis = field(default_factory=LyapunovAnalysis)
    unified_state: UnifiedFieldState = field(default_factory=UnifiedFieldState)
    
    # Liberation parameters
    liberation_rate: float = 0.1  # γ
    planck_threshold: float = 1e-35  # ε_Planck
    
    def current_state(self, karma_trace: float, 
                      vasana_norm: float) -> LiberationState:
        """
        Determine current liberation state.
        """
        V = self.lyapunov.lyapunov_function(karma_trace, vasana_norm)
        
        if V < self.planck_threshold:
            return LiberationState.VIDEHAMUKTA
        elif V < 0.01:
            return LiberationState.JIVANMUKTA
        elif V < 0.5:
            return LiberationState.ADVANCED
        elif V < 2.0:
            return LiberationState.ASPIRANT
        else:
            return LiberationState.BOUND
    
    def estimate_liberation_time(self, V0: float) -> float:
        """
        Estimate time to liberation.
        
        T* ≤ (1/γ) · ln(V₀/ε_Planck)
        """
        return self.lyapunov.liberation_time(
            V0, self.liberation_rate, self.planck_threshold
        )
    
    def step(self, state: np.ndarray, karma_trace: float,
             vasana_norm: float, dt: float = 0.1) -> Dict[str, Any]:
        """
        Execute one step of the liberation algorithm.
        
        Applies all three Yogas in parallel.
        """
        results = {}
        
        # Jñāna: Discriminate
        discriminated = self.jnana.discriminate(state)
        results["jnana_atman_overlap"] = abs(discriminated[0])**2
        
        # Karma: Detached action
        self.karma.practice_detachment(dt * 0.1)
        results["karma_detachment"] = self.karma.detachment_level
        
        # Bhakti: Phase evolution
        self.bhakti.increase_devotion(dt * 0.05)
        phases = self.bhakti.evolve_phase(dt, 10)
        self.bhakti.phase_difference = phases[-1] % (2 * np.pi)
        results["bhakti_locked"] = self.bhakti.is_locked()
        
        # Lyapunov decay
        V_current = self.lyapunov.lyapunov_function(karma_trace, vasana_norm)
        V_next = V_current * np.exp(-self.liberation_rate * dt)
        results["lyapunov_V"] = V_next
        
        # New karma/vasana values
        new_karma = karma_trace * np.exp(-self.liberation_rate * dt)
        new_vasana = vasana_norm * np.exp(-self.liberation_rate * dt / 2)
        results["new_karma"] = new_karma
        results["new_vasana"] = new_vasana
        
        # Check liberation
        state_now = self.current_state(new_karma, new_vasana)
        results["state"] = state_now
        
        return results
    
    def run_to_liberation(self, initial_state: np.ndarray,
                          initial_karma: float,
                          initial_vasana: float,
                          max_steps: int = 10000) -> Dict[str, Any]:
        """
        Run algorithm until liberation or max steps.
        
        Returns history and final state.
        """
        state = initial_state.copy()
        karma = initial_karma
        vasana = initial_vasana
        
        history = {
            "karma": [karma],
            "vasana": [vasana],
            "lyapunov": [self.lyapunov.lyapunov_function(karma, vasana)],
            "states": [self.current_state(karma, vasana)],
        }
        
        for step in range(max_steps):
            results = self.step(state, karma, vasana)
            
            karma = results["new_karma"]
            vasana = results["new_vasana"]
            
            history["karma"].append(karma)
            history["vasana"].append(vasana)
            history["lyapunov"].append(results["lyapunov_V"])
            history["states"].append(results["state"])
            
            if results["state"] == LiberationState.VIDEHAMUKTA:
                self.unified_state.merge_thread()
                self.unified_state.transcend_time()
                history["liberated_at_step"] = step
                break
        
        history["final_state"] = results["state"]
        history["unified_complete"] = self.unified_state.is_complete()
        
        return history


# =============================================================================
# VALIDATION
# =============================================================================

def validate_liberation() -> bool:
    """Validate the liberation module."""
    
    # Test LyapunovAnalysis
    lyap = LyapunovAnalysis()
    V = lyap.lyapunov_function(1.0, 0.5)
    assert V == 1.25  # 1.0 + 0.5²
    
    assert lyap.is_stable(0.1)
    assert not lyap.is_stable(-0.1)
    
    T = lyap.liberation_time(1.0, 0.1, 1e-10)
    assert T > 0
    assert T < 1000
    
    # Test JnanaYoga
    jnana = JnanaYoga(dimension=4)
    state = np.array([0.5, 0.5, 0.5, 0.5], dtype=complex)
    discriminated = jnana.discriminate(state)
    assert len(discriminated) == 4
    assert abs(discriminated[0]) > abs(discriminated[1])
    
    # Test KarmaYoga
    karma_yoga = KarmaYoga(detachment_level=0.0)
    assert karma_yoga.karma_generation_factor() == 1.0
    
    karma_yoga.practice_detachment(0.5)
    assert karma_yoga.detachment_level == 0.5
    assert karma_yoga.karma_generation_factor() == 0.5
    
    # Test BhaktiYoga
    bhakti = BhaktiYoga(omega_source=1.0, omega_jiva=1.1, kappa=0.2)
    assert bhakti.can_lock()  # 0.2 >= 0.1
    
    phi_star = bhakti.fixed_point_phase()
    assert phi_star is not None
    
    bhakti.increase_devotion(0.5)
    assert bhakti.kappa == 0.7
    
    # Test UnifiedFieldState
    unified = UnifiedFieldState()
    assert not unified.is_complete()
    
    unified.merge_thread()
    assert unified.merged
    assert not unified.locality
    
    unified.transcend_time()
    assert unified.is_complete()
    
    # Test LiberationAlgorithm
    alg = LiberationAlgorithm()
    state = alg.current_state(0.001, 0.001)
    assert state == LiberationState.JIVANMUKTA
    
    state = alg.current_state(5.0, 2.0)
    assert state == LiberationState.BOUND
    
    T = alg.estimate_liberation_time(1.0)
    assert T > 0
    
    return True


if __name__ == "__main__":
    print("Validating Liberation Module...")
    assert validate_liberation()
    print("✓ Liberation module validated")
    
    # Demo
    print("\n--- Liberation Algorithm Demo ---")
    
    print("\n1. Lyapunov Analysis:")
    lyap = LyapunovAnalysis()
    V0 = 5.0
    gamma = 0.1
    T = lyap.liberation_time(V0, gamma, 1e-10)
    print(f"   Initial V₀ = {V0}")
    print(f"   Liberation rate γ = {gamma}")
    print(f"   Time to liberation T* ≈ {T:.1f}")
    
    print("\n2. The Three Yogas:")
    for yoga in YogaPath:
        print(f"   {yoga.name}: {yoga.description}")
    
    print("\n3. Bhakti Phase Locking:")
    bhakti = BhaktiYoga(omega_source=1.0, omega_jiva=1.3, kappa=0.2)
    print(f"   ω_S = {bhakti.omega_source}, ω_J = {bhakti.omega_jiva}")
    print(f"   κ (devotion) = {bhakti.kappa}")
    print(f"   Can lock: {bhakti.can_lock()}")
    
    bhakti.increase_devotion(0.3)
    print(f"   After practice: κ = {bhakti.kappa}")
    print(f"   Can lock now: {bhakti.can_lock()}")
    
    print("\n4. Running Liberation Algorithm:")
    alg = LiberationAlgorithm(liberation_rate=0.5)
    initial_state = np.array([0.5, 0.5, 0.5, 0.5], dtype=complex)
    
    history = alg.run_to_liberation(
        initial_state, 
        initial_karma=2.0, 
        initial_vasana=1.0,
        max_steps=100
    )
    
    print(f"   Final state: {history['final_state'].name}")
    print(f"   Unified complete: {history['unified_complete']}")
    if 'liberated_at_step' in history:
        print(f"   Liberated at step: {history['liberated_at_step']}")
