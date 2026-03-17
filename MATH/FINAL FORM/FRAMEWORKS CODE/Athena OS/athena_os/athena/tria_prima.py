"""
ATHENA OS - TRIA PRIMA OPERATORS
================================
The Three Governing Operators of Alchemical Dynamics

From THE_MATH_OF_ALCHEMY.docx:

THE TRIA PRIMA DECOMPOSITION:
    dΨ/dt = F(Ψ) + M(Ψ) + S(Ψ)
    
    F = Sulfur (drive/gradient component)
    M = Mercury (flux/mixing component)  
    S = Salt (integration/memory component)

SULFUR (CARDINAL/GRADIENT):
    F(Ψ) = -α∇U(Ψ)
    - Gradient operator on potential U
    - Initiates motion, breaks symmetry
    - Corresponds to Cardinal signs (Aries, Cancer, Libra, Capricorn)
    - Heating operator

MERCURY (MUTABLE/FLUX):
    M(Ψ) = curl-like redistribution
    - Skew-symmetric mixing operator
    - Preserves total but redistributes
    - Corresponds to Mutable signs (Gemini, Virgo, Sagittarius, Pisces)
    - Circulating operator

SALT (FIXED/INTEGRAL):
    S(Ψ)(t) = Ψ(t) + β∫G(Ψ(τ))dτ
    - Integral/memory operator
    - Stabilizes and accumulates structure
    - Corresponds to Fixed signs (Taurus, Leo, Scorpio, Aquarius)
    - Damping/fixation operator

LIE ALGEBRA DECOMPOSITION:
    A = S_F ⊕ S_M ⊕ S_S
    - Sulfur: symmetric operators
    - Mercury: skew-symmetric operators
    - Salt: diagonal/integrative operators
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Callable, Any
from enum import Enum, auto
import math
import numpy as np
from .alchemical_state import ElementalState, QualityState, Element, QualityMapping


# =============================================================================
# TRIA PRIMA TYPES
# =============================================================================

class TriaPrima(Enum):
    """The three governing principles."""
    SULFUR = auto()   # Drive/gradient
    MERCURY = auto()  # Flux/mixing
    SALT = auto()     # Memory/fixation


class Modality(Enum):
    """Zodiacal modalities corresponding to Tria Prima."""
    CARDINAL = auto()  # Sulfur - initiating
    MUTABLE = auto()   # Mercury - adapting
    FIXED = auto()     # Salt - stabilizing


# =============================================================================
# POTENTIAL FUNCTIONS
# =============================================================================

class PotentialFunction:
    """
    Base class for Sulfur potential functions U(Ψ).
    
    F(Ψ) = -α∇U(Ψ)
    """
    
    def evaluate(self, state: ElementalState) -> float:
        """Evaluate potential at state."""
        raise NotImplementedError
    
    def gradient(self, state: ElementalState) -> np.ndarray:
        """Compute gradient ∇U(Ψ)."""
        raise NotImplementedError


class QuadraticPotential(PotentialFunction):
    """
    Quadratic potential: U(Ψ) = (1/2)Ψ^T A Ψ
    
    Gradient: ∇U = AΨ
    """
    
    def __init__(self, A: np.ndarray = None):
        if A is None:
            # Default: Fire-attracting potential
            self.A = np.diag([-1.0, 0.5, 1.0, 1.0])
        else:
            self.A = A
    
    def evaluate(self, state: ElementalState) -> float:
        psi = np.real(state.to_array())
        return 0.5 * psi @ self.A @ psi
    
    def gradient(self, state: ElementalState) -> np.ndarray:
        psi = np.real(state.to_array())
        return self.A @ psi


class EntropyPotential(PotentialFunction):
    """
    Entropy potential: U(Ψ) = Σ p_i ln(p_i)
    
    Drives toward uniform distribution (maximum entropy).
    """
    
    def evaluate(self, state: ElementalState) -> float:
        dist = state.get_distribution()
        u = 0.0
        for p in dist.values():
            if p > 1e-10:
                u += p * math.log(p)
        return u
    
    def gradient(self, state: ElementalState) -> np.ndarray:
        eps = 1e-10
        psi = np.abs(state.to_array())
        total = np.sum(psi)
        if total < eps:
            return np.zeros(4)
        
        p = psi / total
        grad = np.zeros(4)
        for i in range(4):
            if p[i] > eps:
                grad[i] = (1 + math.log(p[i])) / total
        return grad


class ElementSpecificPotential(PotentialFunction):
    """
    Element-specific potential: U(Ψ) = Σ u_i |c_i|²
    
    Different weights for each element.
    """
    
    def __init__(self, u_fire: float = -1.0, u_air: float = 0.0,
                 u_water: float = 1.0, u_earth: float = 0.5):
        self.u = np.array([u_fire, u_air, u_water, u_earth])
    
    def evaluate(self, state: ElementalState) -> float:
        psi = np.abs(state.to_array())
        return np.sum(self.u * psi**2)
    
    def gradient(self, state: ElementalState) -> np.ndarray:
        psi = np.abs(state.to_array())
        return 2 * self.u * psi


# =============================================================================
# SULFUR OPERATOR
# =============================================================================

class SulfurOperator:
    """
    Sulfur (☉) - The Cardinal/Gradient Operator.
    
    F(Ψ) = -α∇U(Ψ)
    
    Properties:
    - Gradient dynamics on potential landscape
    - Initiates motion, breaks symmetry
    - Increases Heat, drives toward Fire/Air
    - Corresponds to Cardinal signs
    """
    
    def __init__(self, alpha: float = 1.0, 
                 potential: PotentialFunction = None):
        self.alpha = alpha
        self.potential = potential or QuadraticPotential()
    
    def apply(self, state: ElementalState) -> np.ndarray:
        """
        Apply Sulfur operator: F(Ψ) = -α∇U(Ψ)
        
        Returns dΨ/dt contribution.
        """
        grad = self.potential.gradient(state)
        return -self.alpha * grad
    
    def update_state(self, state: ElementalState, dt: float) -> ElementalState:
        """Update state with Sulfur dynamics."""
        dpsi = self.apply(state)
        new_arr = state.to_array() + dt * dpsi
        return ElementalState.from_array(new_arr)
    
    def heat_change(self, state: ElementalState) -> float:
        """
        Compute heat change from Sulfur action.
        
        Sulfur typically increases Heat.
        """
        dpsi = self.apply(state)
        dh, dm = QualityMapping.project_dynamics(dpsi)
        return dh
    
    @property
    def cardinal_signs(self) -> List[str]:
        """Zodiacal signs governed by Sulfur."""
        return ["Aries", "Cancer", "Libra", "Capricorn"]


# =============================================================================
# MERCURY OPERATOR
# =============================================================================

class MercuryOperator:
    """
    Mercury (☿) - The Mutable/Flux Operator.
    
    M(Ψ) = BΨ where B is skew-symmetric
    
    Properties:
    - Redistributes without net creation
    - Rotational/mixing flow
    - Preserves total but changes proportions
    - Corresponds to Mutable signs
    """
    
    def __init__(self, gamma: float = 1.0, 
                 mixing_matrix: np.ndarray = None):
        self.gamma = gamma
        
        if mixing_matrix is None:
            # Default skew-symmetric mixing
            # Fire ↔ Air, Water ↔ Earth exchange
            self.B = np.array([
                [0, -1, 0, 0],
                [1, 0, 0, 0],
                [0, 0, 0, -1],
                [0, 0, 1, 0]
            ], dtype=float)
        else:
            self.B = mixing_matrix
    
    @property
    def is_skew_symmetric(self) -> bool:
        """Verify B is skew-symmetric (B^T = -B)."""
        return np.allclose(self.B.T, -self.B)
    
    def apply(self, state: ElementalState) -> np.ndarray:
        """
        Apply Mercury operator: M(Ψ) = γBΨ
        
        Returns dΨ/dt contribution.
        """
        psi = np.real(state.to_array())
        return self.gamma * self.B @ psi
    
    def update_state(self, state: ElementalState, dt: float) -> ElementalState:
        """Update state with Mercury dynamics (rotation)."""
        dpsi = self.apply(state)
        new_arr = state.to_array() + dt * dpsi
        return ElementalState.from_array(new_arr)
    
    def conserved_quantity(self, state: ElementalState) -> float:
        """
        Mercury preserves total elemental magnitude.
        
        d/dt ||Ψ||² = 2⟨Ψ, BΨ⟩ = 0 (since B is skew-symmetric)
        """
        return state.norm**2
    
    @property
    def mutable_signs(self) -> List[str]:
        """Zodiacal signs governed by Mercury."""
        return ["Gemini", "Virgo", "Sagittarius", "Pisces"]


# =============================================================================
# SALT OPERATOR
# =============================================================================

class SaltOperator:
    """
    Salt (⊕) - The Fixed/Integral Operator.
    
    S(Ψ)(t) = Ψ(t) + β∫G(Ψ(τ))dτ
    
    Properties:
    - Memory/integral term
    - Stabilizes and fixes structure
    - Low-pass filter / damping
    - Corresponds to Fixed signs
    """
    
    def __init__(self, beta: float = 0.5,
                 decay_rate: float = 0.1):
        self.beta = beta
        self.decay_rate = decay_rate
        self.history: List[np.ndarray] = []
        self.accumulated: np.ndarray = np.zeros(4)
    
    def reset(self) -> None:
        """Reset accumulated history."""
        self.history = []
        self.accumulated = np.zeros(4)
    
    def structure_functional(self, state: ElementalState) -> np.ndarray:
        """
        Structure contribution G(Ψ).
        
        Default: projects toward Earth-dominant stability.
        """
        psi = np.real(state.to_array())
        # Favor Earth (index 3), damp Fire (index 0)
        G = np.diag([-0.5, 0.0, 0.0, 1.0])
        return G @ psi
    
    def accumulate(self, state: ElementalState, dt: float) -> None:
        """Add to accumulated memory."""
        g = self.structure_functional(state)
        self.history.append(g)
        self.accumulated += g * dt
        # Apply decay
        self.accumulated *= (1 - self.decay_rate * dt)
    
    def apply(self, state: ElementalState) -> np.ndarray:
        """
        Apply Salt operator.
        
        Returns the integral contribution β∫G(Ψ)dτ
        """
        return self.beta * self.accumulated
    
    def update_state(self, state: ElementalState, dt: float) -> ElementalState:
        """Update state with Salt dynamics (fixation)."""
        self.accumulate(state, dt)
        contribution = self.apply(state)
        new_arr = state.to_array() + contribution
        return ElementalState.from_array(new_arr)
    
    @property
    def fixed_signs(self) -> List[str]:
        """Zodiacal signs governed by Salt."""
        return ["Taurus", "Leo", "Scorpio", "Aquarius"]


# =============================================================================
# TRIA PRIMA SYSTEM
# =============================================================================

class TriaPrimaSystem:
    """
    Complete Tria Prima dynamical system.
    
    dΨ/dt = F(Ψ) + M(Ψ) + S(Ψ)
           Sulfur + Mercury + Salt
    """
    
    def __init__(self,
                 sulfur: SulfurOperator = None,
                 mercury: MercuryOperator = None,
                 salt: SaltOperator = None):
        self.sulfur = sulfur or SulfurOperator()
        self.mercury = mercury or MercuryOperator()
        self.salt = salt or SaltOperator()
    
    def compute_derivative(self, state: ElementalState) -> np.ndarray:
        """
        Compute full derivative dΨ/dt.
        
        dΨ/dt = F(Ψ) + M(Ψ) + S(Ψ)
        """
        f = self.sulfur.apply(state)
        m = self.mercury.apply(state)
        s = self.salt.apply(state)
        return f + m + s
    
    def step(self, state: ElementalState, dt: float) -> ElementalState:
        """
        Execute one time step (Euler method).
        """
        dpsi = self.compute_derivative(state)
        new_arr = state.to_array() + dt * dpsi
        
        # Update Salt memory
        self.salt.accumulate(state, dt)
        
        return ElementalState.from_array(new_arr)
    
    def evolve(self, initial: ElementalState, 
               duration: float, dt: float = 0.01) -> List[ElementalState]:
        """
        Evolve state over time.
        
        Returns trajectory.
        """
        trajectory = [initial]
        current = initial
        
        t = 0
        while t < duration:
            current = self.step(current, dt)
            trajectory.append(current)
            t += dt
        
        return trajectory
    
    def find_fixed_point(self, initial: ElementalState,
                        max_iter: int = 1000,
                        tol: float = 1e-6) -> Optional[ElementalState]:
        """
        Find fixed point where dΨ/dt ≈ 0.
        """
        current = initial
        dt = 0.01
        
        for i in range(max_iter):
            dpsi = self.compute_derivative(current)
            if np.linalg.norm(dpsi) < tol:
                return current
            
            new_arr = current.to_array() + dt * dpsi
            current = ElementalState.from_array(new_arr)
            self.salt.accumulate(current, dt)
        
        return current  # Return best found
    
    def decompose_dynamics(self, state: ElementalState
                          ) -> Dict[TriaPrima, np.ndarray]:
        """Decompose dynamics into Tria Prima components."""
        return {
            TriaPrima.SULFUR: self.sulfur.apply(state),
            TriaPrima.MERCURY: self.mercury.apply(state),
            TriaPrima.SALT: self.salt.apply(state)
        }
    
    def quality_dynamics(self, state: ElementalState) -> Tuple[float, float]:
        """
        Compute quality space dynamics (dH/dt, dM/dt).
        """
        dpsi = self.compute_derivative(state)
        return QualityMapping.project_dynamics(dpsi)


# =============================================================================
# VALIDATION
# =============================================================================

def validate_tria_prima() -> bool:
    """Validate the Tria Prima operators module."""
    
    # Test potentials
    state = ElementalState(fire=0.5, air=0.3, water=0.2, earth=0.0)
    
    quad_pot = QuadraticPotential()
    u = quad_pot.evaluate(state)
    grad = quad_pot.gradient(state)
    assert isinstance(u, float)
    assert grad.shape == (4,)
    
    ent_pot = EntropyPotential()
    u_ent = ent_pot.evaluate(state)
    assert u_ent < 0  # Entropy is negative
    
    # Test Sulfur
    sulfur = SulfurOperator(alpha=0.5)
    f = sulfur.apply(state)
    assert f.shape == (4,)
    
    # Test Mercury
    mercury = MercuryOperator(gamma=0.3)
    assert mercury.is_skew_symmetric
    m = mercury.apply(state)
    assert m.shape == (4,)
    
    # Mercury conserves norm (approximately, since we're in continuous time)
    initial_norm = state.norm
    
    # Test Salt
    salt = SaltOperator(beta=0.2)
    salt.accumulate(state, 0.1)
    s = salt.apply(state)
    assert s.shape == (4,)
    
    # Test full system
    system = TriaPrimaSystem()
    dpsi = system.compute_derivative(state)
    assert dpsi.shape == (4,)
    
    # Test evolution
    trajectory = system.evolve(state, duration=1.0, dt=0.1)
    assert len(trajectory) > 10
    
    # Test decomposition
    decomp = system.decompose_dynamics(state)
    assert TriaPrima.SULFUR in decomp
    assert TriaPrima.MERCURY in decomp
    assert TriaPrima.SALT in decomp
    
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("ATHENA OS - TRIA PRIMA OPERATORS")
    print("Sulfur, Mercury, Salt Dynamics")
    print("=" * 60)
    
    print("\nValidating module...")
    assert validate_tria_prima()
    print("✓ Module validated")
    
    # Demo
    print("\n--- TRIA PRIMA DYNAMICS DEMO ---")
    
    # Create initial state (mostly Fire, some Air)
    initial = ElementalState(fire=0.8, air=0.2, water=0.0, earth=0.0)
    print(f"Initial: Fire={initial.fire:.2f}, Air={initial.air:.2f}, " +
          f"Water={initial.water:.2f}, Earth={initial.earth:.2f}")
    
    # Create system
    system = TriaPrimaSystem(
        sulfur=SulfurOperator(alpha=0.3),
        mercury=MercuryOperator(gamma=0.5),
        salt=SaltOperator(beta=0.2)
    )
    
    # Decompose dynamics
    decomp = system.decompose_dynamics(initial)
    print("\nDynamics decomposition at initial state:")
    for prima, contrib in decomp.items():
        print(f"  {prima.name}: [{', '.join(f'{v:.3f}' for v in contrib)}]")
    
    # Evolve
    print("\nEvolving for 2.0 time units...")
    trajectory = system.evolve(initial, duration=2.0, dt=0.1)
    
    final = trajectory[-1]
    print(f"Final: Fire={abs(final.fire):.2f}, Air={abs(final.air):.2f}, " +
          f"Water={abs(final.water):.2f}, Earth={abs(final.earth):.2f}")
    
    # Quality dynamics
    dh, dm = system.quality_dynamics(initial)
    print(f"\nQuality dynamics: dH/dt = {dh:.3f}, dM/dt = {dm:.3f}")
