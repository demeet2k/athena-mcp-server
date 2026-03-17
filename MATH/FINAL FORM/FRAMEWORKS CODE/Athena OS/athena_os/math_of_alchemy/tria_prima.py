"""
ATHENA OS - THE MATH OF ALCHEMY
================================
Module II: Tria Prima (השלושה הראשונים) - The Three Governing Operators

THE THREE PRINCIPLES:
    The alchemical dynamical system decomposes into three structural operators:
    
    dΨ/dt = F(Ψ) + M(Ψ) + S(Ψ)
    
    where:
    - F = Sulfur (??) - Gradient/Cardinal Operator
    - M = Mercury (☿) - Flux/Mutable Operator
    - S = Salt (??) - Integral/Fixed Operator

SULFUR (??):
    The principle of directed change, ignition, initiation.
    Corresponds to Cardinal modality (Aries, Cancer, Libra, Capricorn).
    Modeled as gradient operator: F(Ψ) = -α∇U(Ψ)
    
    Effects: Increases Heat, initiates motion, breaks symmetry

MERCURY (☿):
    The principle of circulation, mixing, volatility.
    Corresponds to Mutable modality (Gemini, Virgo, Sagittarius, Pisces).
    Modeled as flux operator: M(Ψ) = m_ij * Ψ (skew-symmetric mixing)
    
    Effects: Redistributes without net creation, oscillatory

SALT (??):
    The principle of stability, structure, memory.
    Corresponds to Fixed modality (Taurus, Leo, Scorpio, Aquarius).
    Modeled as integral operator: S(Ψ) = β∫G(Ψ)dτ
    
    Effects: Slows, damps, stabilizes, creates attractors

SOURCES:
    THE MATH OF ALCHEMY
    Paracelsian Tradition
"""

from __future__ import annotations
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Callable
from enum import Enum, auto

from .elements import ElementalState, ElementalSystem, Element


# =============================================================================
# TRIA PRIMA TYPES
# =============================================================================

class PrincipleType(Enum):
    """The Three Alchemical Principles."""
    
    SULFUR = ("??", "Sulfur", "Cardinal", "Gradient", "Initiation")
    MERCURY = ("☿", "Mercury", "Mutable", "Flux", "Circulation")
    SALT = ("??", "Salt", "Fixed", "Integral", "Fixation")
    
    def __init__(self, symbol: str, name: str, modality: str, 
                 operator_type: str, function: str):
        self.symbol = symbol
        self._name = name
        self.modality = modality
        self.operator_type = operator_type
        self._function = function


class Modality(Enum):
    """The Three Modalities."""
    
    CARDINAL = ("Cardinal", "Initiation", [0, 3, 6, 9])  # Aries, Cancer, Libra, Capricorn
    FIXED = ("Fixed", "Stabilization", [1, 4, 7, 10])     # Taurus, Leo, Scorpio, Aquarius
    MUTABLE = ("Mutable", "Circulation", [2, 5, 8, 11])   # Gemini, Virgo, Sagittarius, Pisces
    
    def __init__(self, name: str, function: str, zodiac_indices: List[int]):
        self._name = name
        self._function = function
        self.zodiac_indices = zodiac_indices


# =============================================================================
# SULFUR OPERATOR - GRADIENT/CARDINAL
# =============================================================================

@dataclass
class SulfurOperator:
    """
    The Sulfur Operator - Gradient dynamics.
    
    F(Ψ) = -α∇U(Ψ)
    
    Sulfur creates directed flow toward/away from potential minima/maxima.
    It is the initiator of motion in the alchemical system.
    """
    
    alpha: float = 1.0  # Sulfur intensity
    
    def quadratic_potential(self, psi: np.ndarray, A: np.ndarray = None) -> float:
        """
        Quadratic potential: U(Ψ) = ½Ψᵀ A Ψ
        
        Default A biases toward Fire (element 0).
        """
        if A is None:
            # Default: bias toward Fire
            A = np.diag([-1, 0, 1, 1])  # Fire is minimum
        return 0.5 * psi @ A @ psi
    
    def gradient_quadratic(self, psi: np.ndarray, A: np.ndarray = None) -> np.ndarray:
        """
        Gradient of quadratic potential: ∇U = AΨ
        """
        if A is None:
            A = np.diag([-1, 0, 1, 1])
        return A @ psi
    
    def apply(self, state: ElementalState, 
              potential_matrix: np.ndarray = None,
              dt: float = 0.1) -> ElementalState:
        """
        Apply Sulfur operator: dΨ/dt = -α∇U(Ψ)
        """
        psi = state.vector.real
        grad = self.gradient_quadratic(psi, potential_matrix)
        new_psi = psi - self.alpha * dt * grad
        return ElementalState.from_vector(new_psi.astype(complex))
    
    @property
    def cardinal_zodiac(self) -> List[str]:
        """Cardinal signs associated with Sulfur."""
        return ["Aries", "Cancer", "Libra", "Capricorn"]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get operator summary."""
        return {
            "principle": "Sulfur",
            "symbol": "??",
            "operator_type": "Gradient",
            "modality": "Cardinal",
            "alpha": self.alpha,
            "function": "Directed change, initiation, heating",
            "zodiac": self.cardinal_zodiac,
        }


# =============================================================================
# MERCURY OPERATOR - FLUX/MUTABLE
# =============================================================================

@dataclass
class MercuryOperator:
    """
    The Mercury Operator - Flux/Mixing dynamics.
    
    M(Ψ) = m_ij Ψ  (skew-symmetric mixing matrix)
    
    Mercury redistributes intensities without net creation.
    It is oscillatory and circulatory.
    """
    
    # Default mixing matrix (skew-symmetric for pure circulation)
    mixing_matrix: np.ndarray = field(default_factory=lambda: np.array([
        [0, 0.5, 0, -0.5],
        [-0.5, 0, 0.5, 0],
        [0, -0.5, 0, 0.5],
        [0.5, 0, -0.5, 0]
    ]))
    
    def apply(self, state: ElementalState, dt: float = 0.1) -> ElementalState:
        """
        Apply Mercury operator: dΨ/dt = MΨ
        
        For skew-symmetric M, this produces rotation/circulation.
        """
        psi = state.vector.real
        dpsi = self.mixing_matrix @ psi
        new_psi = psi + dt * dpsi
        return ElementalState.from_vector(new_psi.astype(complex))
    
    def is_conservative(self) -> bool:
        """Check if mixing matrix is skew-symmetric (conservative)."""
        return np.allclose(self.mixing_matrix, -self.mixing_matrix.T)
    
    def eigenspectrum(self) -> np.ndarray:
        """Get eigenvalues of the mixing matrix."""
        return np.linalg.eigvals(self.mixing_matrix)
    
    @property
    def mutable_zodiac(self) -> List[str]:
        """Mutable signs associated with Mercury."""
        return ["Gemini", "Virgo", "Sagittarius", "Pisces"]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get operator summary."""
        return {
            "principle": "Mercury",
            "symbol": "☿",
            "operator_type": "Flux",
            "modality": "Mutable",
            "conservative": self.is_conservative(),
            "function": "Circulation, mixing, volatility",
            "zodiac": self.mutable_zodiac,
        }


# =============================================================================
# SALT OPERATOR - INTEGRAL/FIXED
# =============================================================================

@dataclass
class SaltOperator:
    """
    The Salt Operator - Integral/Fixation dynamics.
    
    S(Ψ)(t) = Ψ(t) + β∫G(Ψ(τ))dτ
    
    Salt accumulates structure over time, creating memory and stability.
    It is the source of fixation in classical alchemy.
    """
    
    beta: float = 0.1  # Inertia/fixation parameter
    accumulated: np.ndarray = field(default_factory=lambda: np.zeros(4))
    
    def structural_functional(self, psi: np.ndarray) -> np.ndarray:
        """
        Default structural functional: G(Ψ) = P_EW(Ψ)
        
        Projects onto Earth-Water subspace (stabilizing elements).
        """
        # Projection matrix onto Earth-Water
        P_EW = np.diag([0, 0, 1, 1])  # Only keep Water and Earth
        return P_EW @ psi
    
    def apply(self, state: ElementalState, dt: float = 0.1) -> ElementalState:
        """
        Apply Salt operator with accumulation.
        
        Updates: accumulated += β * G(Ψ) * dt
        Returns: Ψ + accumulated
        """
        psi = state.vector.real
        g_psi = self.structural_functional(psi)
        self.accumulated += self.beta * g_psi * dt
        
        new_psi = psi + self.accumulated
        return ElementalState.from_vector(new_psi.astype(complex))
    
    def apply_instantaneous(self, state: ElementalState, 
                            dt: float = 0.1) -> ElementalState:
        """
        Apply instantaneous Salt (no accumulation tracking).
        
        dΨ/dt = β * G(Ψ)
        """
        psi = state.vector.real
        g_psi = self.structural_functional(psi)
        new_psi = psi + self.beta * g_psi * dt
        return ElementalState.from_vector(new_psi.astype(complex))
    
    def reset_accumulation(self):
        """Reset the accumulated integral."""
        self.accumulated = np.zeros(4)
    
    @property
    def fixed_zodiac(self) -> List[str]:
        """Fixed signs associated with Salt."""
        return ["Taurus", "Leo", "Scorpio", "Aquarius"]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get operator summary."""
        return {
            "principle": "Salt",
            "symbol": "??",
            "operator_type": "Integral",
            "modality": "Fixed",
            "beta": self.beta,
            "accumulated": self.accumulated.tolist(),
            "function": "Stabilization, memory, fixation",
            "zodiac": self.fixed_zodiac,
        }


# =============================================================================
# COMBINED TRIA PRIMA SYSTEM
# =============================================================================

@dataclass
class TriaPrimaSystem:
    """
    The combined Tria Prima dynamical system.
    
    dΨ/dt = F(Ψ) + M(Ψ) + S(Ψ)
    
    where F = Sulfur, M = Mercury, S = Salt
    """
    
    sulfur: SulfurOperator = field(default_factory=SulfurOperator)
    mercury: MercuryOperator = field(default_factory=MercuryOperator)
    salt: SaltOperator = field(default_factory=SaltOperator)
    
    def step(self, state: ElementalState, dt: float = 0.1,
             sulfur_active: bool = True,
             mercury_active: bool = True,
             salt_active: bool = True) -> ElementalState:
        """
        Execute one time step of the combined dynamics.
        
        Sequentially applies active operators.
        """
        current = state
        
        if sulfur_active:
            current = self.sulfur.apply(current, dt=dt)
        
        if mercury_active:
            current = self.mercury.apply(current, dt=dt)
        
        if salt_active:
            current = self.salt.apply_instantaneous(current, dt=dt)
        
        return current
    
    def evolve(self, initial_state: ElementalState, 
               n_steps: int = 100,
               dt: float = 0.1,
               sulfur_active: bool = True,
               mercury_active: bool = True,
               salt_active: bool = True) -> List[ElementalState]:
        """
        Evolve the system over multiple time steps.
        
        Returns trajectory of states.
        """
        trajectory = [initial_state]
        current = initial_state
        
        for _ in range(n_steps):
            current = self.step(current, dt, sulfur_active, mercury_active, salt_active)
            trajectory.append(current)
        
        return trajectory
    
    def find_equilibrium(self, initial_state: ElementalState,
                         max_steps: int = 1000,
                         tolerance: float = 1e-6,
                         dt: float = 0.1) -> Tuple[ElementalState, bool]:
        """
        Find equilibrium state (fixed point).
        
        Returns (final_state, converged).
        """
        current = initial_state
        
        for _ in range(max_steps):
            next_state = self.step(current, dt)
            
            # Check convergence
            diff = np.linalg.norm(next_state.vector - current.vector)
            if diff < tolerance:
                return next_state, True
            
            current = next_state
        
        return current, False
    
    def analyze_dynamics(self, state: ElementalState) -> Dict[str, Any]:
        """
        Analyze the dynamics at a given state.
        """
        psi = state.vector.real
        
        # Sulfur contribution
        sulfur_grad = self.sulfur.gradient_quadratic(psi)
        sulfur_flow = -self.sulfur.alpha * sulfur_grad
        
        # Mercury contribution
        mercury_flow = self.mercury.mixing_matrix @ psi
        
        # Salt contribution
        salt_flow = self.salt.beta * self.salt.structural_functional(psi)
        
        # Total
        total_flow = sulfur_flow + mercury_flow + salt_flow
        
        return {
            "state": psi.tolist(),
            "sulfur_flow": sulfur_flow.tolist(),
            "mercury_flow": mercury_flow.tolist(),
            "salt_flow": salt_flow.tolist(),
            "total_flow": total_flow.tolist(),
            "flow_magnitude": float(np.linalg.norm(total_flow)),
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Get system summary."""
        return {
            "sulfur": self.sulfur.get_summary(),
            "mercury": self.mercury.get_summary(),
            "salt": self.salt.get_summary(),
            "equation": "dΨ/dt = F(Ψ) + M(Ψ) + S(Ψ)",
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_tria_prima() -> bool:
    """Validate the Tria Prima module."""
    
    # Test PrincipleType
    assert PrincipleType.SULFUR.modality == "Cardinal"
    assert PrincipleType.MERCURY.operator_type == "Flux"
    assert PrincipleType.SALT.symbol == "??"
    
    # Test Modality
    assert 0 in Modality.CARDINAL.zodiac_indices  # Aries
    assert 1 in Modality.FIXED.zodiac_indices     # Taurus
    assert 2 in Modality.MUTABLE.zodiac_indices   # Gemini
    
    # Test SulfurOperator
    sulfur = SulfurOperator(alpha=0.5)
    state = ElementalState(fire=1, air=0.5, water=0.3, earth=0.2)
    new_state = sulfur.apply(state, dt=0.1)
    assert new_state.fire != state.fire  # State changed
    
    # Test MercuryOperator
    mercury = MercuryOperator()
    assert mercury.is_conservative()  # Default is skew-symmetric
    mixed = mercury.apply(state, dt=0.1)
    assert mixed.fire != state.fire
    
    # Test SaltOperator
    salt = SaltOperator(beta=0.2)
    salted = salt.apply_instantaneous(state, dt=0.1)
    # Salt should increase Earth/Water
    assert salted.water.real >= state.water.real or salted.earth.real >= state.earth.real
    
    # Test TriaPrimaSystem
    system = TriaPrimaSystem()
    
    # Test step
    stepped = system.step(state, dt=0.1)
    assert stepped.magnitude > 0
    
    # Test evolve
    trajectory = system.evolve(state, n_steps=10, dt=0.1)
    assert len(trajectory) == 11  # Initial + 10 steps
    
    # Test analysis
    analysis = system.analyze_dynamics(state)
    assert "total_flow" in analysis
    
    # Test summary
    summary = system.get_summary()
    assert "sulfur" in summary
    assert "mercury" in summary
    assert "salt" in summary
    
    return True


if __name__ == "__main__":
    print("Validating Tria Prima Module...")
    assert validate_tria_prima()
    print("✓ Tria Prima module validated")
    
    # Demo
    print("\n--- Tria Prima Demo ---")
    
    print("\nThe Three Principles:")
    for p in PrincipleType:
        print(f"  {p.symbol} {p._name}: {p.modality} / {p.operator_type}")
    
    # Create system
    system = TriaPrimaSystem(
        sulfur=SulfurOperator(alpha=0.3),
        mercury=MercuryOperator(),
        salt=SaltOperator(beta=0.1)
    )
    
    # Initial state: mostly Fire
    initial = ElementalState(fire=0.8, air=0.1, water=0.05, earth=0.05)
    
    print(f"\nInitial State:")
    print(f"  Fire={initial.fire.real:.3f}, Air={initial.air.real:.3f}, "
          f"Water={initial.water.real:.3f}, Earth={initial.earth.real:.3f}")
    
    # Evolve
    trajectory = system.evolve(initial, n_steps=50, dt=0.1)
    final = trajectory[-1]
    
    print(f"\nFinal State (after 50 steps):")
    print(f"  Fire={final.fire.real:.3f}, Air={final.air.real:.3f}, "
          f"Water={final.water.real:.3f}, Earth={final.earth.real:.3f}")
    
    # Analyze at final state
    analysis = system.analyze_dynamics(final)
    print(f"\nFlow Analysis:")
    print(f"  Total flow magnitude: {analysis['flow_magnitude']:.6f}")
