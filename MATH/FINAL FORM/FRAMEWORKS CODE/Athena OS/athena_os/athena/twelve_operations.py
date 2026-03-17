"""
ATHENA OS - THE 12 ALCHEMICAL OPERATIONS
========================================
The Great Work as a Structured Algorithm

From THE_MATH_OF_ALCHEMY.docx:

THE MAGNUM OPUS:
    O_Magnum = O_12 ∘ O_11 ∘ ... ∘ O_1
    
    The Stone satisfies: O_Magnum(Ψ*) = λΨ*, λ ≥ 1
    The Stone is an eigenvector of the full algorithm.

THE 12 OPERATIONS (Zodiacal Correspondence):
    1. Calcination (Aries)      - Fire expansion, entropy increase
    2. Congelation (Taurus)     - Thermal reduction, densification
    3. Fixation (Gemini)        - Binding volatiles to structure
    4. Dissolution (Cancer)     - Immersion in Water matrix
    5. Digestion (Leo)          - Slow sustained heating
    6. Distillation (Virgo)     - Signal/noise separation
    7. Sublimation (Libra)      - Earth → Air elevation
    8. Separation (Scorpio)     - Sharp filtration, decomposition
    9. Ceration (Sagittarius)   - Softening rigid Earth
    10. Fermentation (Capricorn) - Self-replicating pattern
    11. Multiplication (Aquarius) - Power amplification
    12. Projection (Pisces)      - Impose perfected frequency

THREE PHASES:
    Nigredo (1-4): Calcination → Congelation → Fixation → Dissolution
    Albedo (5-8): Digestion → Distillation → Sublimation → Separation
    Rubedo (9-12): Ceration → Fermentation → Multiplication → Projection
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Callable, Any
from enum import Enum, auto
import math
import numpy as np
from .alchemical_state import ElementalState, Element, QualityMapping


# =============================================================================
# ALCHEMICAL OPERATIONS ENUM
# =============================================================================

class AlchemicalOperation(Enum):
    """The 12 Alchemical Operations with zodiacal correspondence."""
    CALCINATION = 1      # Aries
    CONGELATION = 2      # Taurus
    FIXATION = 3         # Gemini
    DISSOLUTION = 4      # Cancer
    DIGESTION = 5        # Leo
    DISTILLATION = 6     # Virgo
    SUBLIMATION = 7      # Libra
    SEPARATION = 8       # Scorpio
    CERATION = 9         # Sagittarius
    FERMENTATION = 10    # Capricorn
    MULTIPLICATION = 11  # Aquarius
    PROJECTION = 12      # Pisces
    
    @property
    def zodiac(self) -> str:
        """Get corresponding zodiacal sign."""
        signs = {
            1: "Aries", 2: "Taurus", 3: "Gemini", 4: "Cancer",
            5: "Leo", 6: "Virgo", 7: "Libra", 8: "Scorpio",
            9: "Sagittarius", 10: "Capricorn", 11: "Aquarius", 12: "Pisces"
        }
        return signs[self.value]
    
    @property
    def phase(self) -> str:
        """Get alchemical phase (Nigredo/Albedo/Rubedo)."""
        if self.value <= 4:
            return "Nigredo"
        elif self.value <= 8:
            return "Albedo"
        else:
            return "Rubedo"
    
    @property
    def element(self) -> Element:
        """Get associated element."""
        mapping = {
            1: Element.FIRE, 2: Element.EARTH, 3: Element.AIR, 4: Element.WATER,
            5: Element.FIRE, 6: Element.EARTH, 7: Element.AIR, 8: Element.WATER,
            9: Element.FIRE, 10: Element.EARTH, 11: Element.AIR, 12: Element.WATER
        }
        return mapping[self.value]


# =============================================================================
# OPERATOR BASE CLASS
# =============================================================================

class AlchemicalOperator:
    """Base class for alchemical operation operators."""
    
    def __init__(self, operation: AlchemicalOperation,
                 intensity: float = 1.0):
        self.operation = operation
        self.intensity = intensity
    
    def get_matrix(self) -> np.ndarray:
        """Get the operator matrix A_k."""
        raise NotImplementedError
    
    def apply(self, state: ElementalState) -> ElementalState:
        """Apply operator to state: O_k(Ψ)."""
        raise NotImplementedError
    
    def __str__(self) -> str:
        return f"{self.operation.name} ({self.operation.zodiac})"


# =============================================================================
# THE 12 OPERATIONS
# =============================================================================

class Calcination(AlchemicalOperator):
    """
    CALCINATION (Aries) - High-temperature entropy expansion.
    
    O_1(Ψ) = exp(A_1)Ψ
    
    Effect: 
    - Fire increases exponentially
    - Water, Earth decay exponentially
    - Heat increases, Moisture decreases
    """
    
    def __init__(self, kappa_f: float = 0.5, 
                 kappa_w: float = 0.3, kappa_e: float = 0.2):
        super().__init__(AlchemicalOperation.CALCINATION)
        self.kappa_f = kappa_f
        self.kappa_w = kappa_w
        self.kappa_e = kappa_e
    
    def get_matrix(self) -> np.ndarray:
        return np.diag([+self.kappa_f, 0, -self.kappa_w, -self.kappa_e])
    
    def apply(self, state: ElementalState) -> ElementalState:
        A = self.get_matrix()
        psi = np.real(state.to_array())
        result = np.linalg.matrix_power(
            np.eye(4) + 0.1 * A, 10
        ) @ psi  # Approximate exp(A)
        return ElementalState.from_array(result)


class Congelation(AlchemicalOperator):
    """
    CONGELATION (Taurus) - Thermal reduction and densification.
    
    Effect:
    - Earth increases (coagulation)
    - Fire, Water decrease
    - Heat lowers, slight moisture reduction
    """
    
    def __init__(self, mu_f: float = 0.3, 
                 mu_w: float = 0.2, mu_e: float = 0.5):
        super().__init__(AlchemicalOperation.CONGELATION)
        self.mu_f = mu_f
        self.mu_w = mu_w
        self.mu_e = mu_e
    
    def get_matrix(self) -> np.ndarray:
        return np.diag([-self.mu_f, 0, -self.mu_w, +self.mu_e])
    
    def apply(self, state: ElementalState) -> ElementalState:
        A = self.get_matrix()
        psi = np.real(state.to_array())
        result = np.linalg.matrix_power(
            np.eye(4) + 0.1 * A, 10
        ) @ psi
        return ElementalState.from_array(result)


class Fixation(AlchemicalOperator):
    """
    FIXATION (Gemini) - Binding volatile factors to structure.
    
    Effect:
    - Fire ↔ Air exchange/binding
    - Skew-symmetric interaction
    """
    
    def __init__(self, eta: float = 0.4):
        super().__init__(AlchemicalOperation.FIXATION)
        self.eta = eta
    
    def get_matrix(self) -> np.ndarray:
        return np.array([
            [0, -self.eta, 0, 0],
            [self.eta, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ])
    
    def apply(self, state: ElementalState) -> ElementalState:
        B = self.get_matrix()
        psi = np.real(state.to_array())
        result = psi + B @ psi
        return ElementalState.from_array(result)


class Dissolution(AlchemicalOperator):
    """
    DISSOLUTION (Cancer) - Elemental immersion in Water matrix.
    
    Effect:
    - Redistribution toward Water
    - Moisture increases, Heat decreases
    """
    
    def __init__(self, delta_f: float = 0.2, delta_w: float = 0.3):
        super().__init__(AlchemicalOperation.DISSOLUTION)
        self.delta_f = delta_f
        self.delta_w = delta_w
    
    def get_matrix(self) -> np.ndarray:
        return np.array([
            [-self.delta_f, 0, 0, 0],
            [0, 0, 0, 0],
            [self.delta_w, self.delta_w, self.delta_w, self.delta_w],
            [0, 0, 0, 0]
        ])
    
    def apply(self, state: ElementalState) -> ElementalState:
        A = self.get_matrix()
        psi = np.real(state.to_array())
        result = np.linalg.matrix_power(
            np.eye(4) + 0.1 * A, 10
        ) @ psi
        return ElementalState.from_array(result)


class Digestion(AlchemicalOperator):
    """
    DIGESTION (Leo) - Slow sustained heating for internal recombination.
    
    Effect:
    - Uniform warming with low-amplitude mixing
    - Internal reorganization
    """
    
    def __init__(self, omega: float = 0.1, epsilon: float = 0.05):
        super().__init__(AlchemicalOperation.DIGESTION)
        self.omega = omega
        self.epsilon = epsilon
    
    def get_matrix(self) -> np.ndarray:
        # Identity (uniform warming) + small mixing
        I = self.omega * np.eye(4)
        K = self.epsilon * np.array([
            [0, 1, 0, 0],
            [1, 0, 1, 0],
            [0, 1, 0, 1],
            [0, 0, 1, 0]
        ])
        return I + K
    
    def apply(self, state: ElementalState, t: float = 1.0) -> ElementalState:
        D = self.get_matrix()
        psi = np.real(state.to_array())
        # exp(tD)Ψ approximated
        result = np.linalg.matrix_power(
            np.eye(4) + 0.1 * t * D, 10
        ) @ psi
        return ElementalState.from_array(result)


class Distillation(AlchemicalOperator):
    """
    DISTILLATION (Virgo) - Separation of signal from noise.
    
    Effect:
    - Repeated heating-cooling cycles
    - Purification filter: lim_{n→∞} (RC)^n
    """
    
    def __init__(self, purity_factor: float = 0.8):
        super().__init__(AlchemicalOperation.DISTILLATION)
        self.purity = purity_factor
    
    def get_condensation_matrix(self) -> np.ndarray:
        """Project onto low-entropy (Earth-dominant)."""
        return np.diag([0.5, 0.7, 0.9, 1.0])
    
    def get_rarefaction_matrix(self) -> np.ndarray:
        """Expand volatile factors."""
        return np.diag([1.2, 1.1, 0.9, 0.8])
    
    def apply(self, state: ElementalState, iterations: int = 5) -> ElementalState:
        C = self.get_condensation_matrix()
        R = self.get_rarefaction_matrix()
        RC = R @ C
        
        psi = np.real(state.to_array())
        for _ in range(iterations):
            psi = RC @ psi
            # Normalize to prevent blow-up
            norm = np.linalg.norm(psi)
            if norm > 0:
                psi = psi / norm * state.norm
        
        return ElementalState.from_array(psi)


class Sublimation(AlchemicalOperator):
    """
    SUBLIMATION (Libra) - Elevation of Earth → Air.
    
    Effect:
    - Earth rises into Air (bypasses liquid)
    - Equilibrium shift
    """
    
    def __init__(self, sigma: float = 0.3):
        super().__init__(AlchemicalOperation.SUBLIMATION)
        self.sigma = sigma
    
    def get_matrix(self) -> np.ndarray:
        s = self.sigma
        return np.array([
            [0, s, 0, +s],
            [s, 0, 0, +s],
            [0, 0, 0, 0],
            [-s, -s, 0, 0]
        ])
    
    def apply(self, state: ElementalState) -> ElementalState:
        A = self.get_matrix()
        psi = np.real(state.to_array())
        result = np.linalg.matrix_power(
            np.eye(4) + 0.1 * A, 10
        ) @ psi
        return ElementalState.from_array(result)


class Separation(AlchemicalOperator):
    """
    SEPARATION (Scorpio) - Sharp filtration and extraction.
    
    Effect:
    - Diagonal projection eliminating impurities
    - Decomposition of composite states
    """
    
    def __init__(self, p_f: float = 0.9, p_a: float = 0.8,
                 p_w: float = 0.7, p_e: float = 0.6):
        super().__init__(AlchemicalOperation.SEPARATION)
        self.projections = [p_f, p_a, p_w, p_e]
    
    def get_matrix(self) -> np.ndarray:
        return np.diag(self.projections)
    
    def apply(self, state: ElementalState) -> ElementalState:
        P = self.get_matrix()
        psi = np.real(state.to_array())
        result = P @ psi
        return ElementalState.from_array(result)


class Ceration(AlchemicalOperator):
    """
    CERATION (Sagittarius) - Softening rigid Earth via Fire/Air.
    
    Effect:
    - Moves rigidity → plasticity
    - Fire/Air entrainment into Earth
    """
    
    def __init__(self, chi: float = 0.25):
        super().__init__(AlchemicalOperation.CERATION)
        self.chi = chi
    
    def get_matrix(self) -> np.ndarray:
        c = self.chi
        return np.array([
            [0, c, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [+c, +c, 0, 0]
        ])
    
    def apply(self, state: ElementalState) -> ElementalState:
        A = self.get_matrix()
        psi = np.real(state.to_array())
        result = np.linalg.matrix_power(
            np.eye(4) + 0.1 * A, 10
        ) @ psi
        return ElementalState.from_array(result)


class Fermentation(AlchemicalOperator):
    """
    FERMENTATION (Capricorn) - Introduction of self-replicating pattern.
    
    Effect:
    - Nonlinear growth: O_10(Ψ) = Ψ + ρF(Ψ)
    - Exponential emergence of "new life"
    """
    
    def __init__(self, rho: float = 0.2, k: float = 1.5):
        super().__init__(AlchemicalOperation.FERMENTATION)
        self.rho = rho
        self.k = k  # Growth exponent
    
    def growth_functional(self, state: ElementalState) -> np.ndarray:
        """F(Ψ) with F(λΨ) = λ^k F(Ψ)."""
        psi = np.abs(state.to_array())
        # Nonlinear growth favoring balanced states
        norm = np.linalg.norm(psi)
        if norm < 1e-10:
            return np.zeros(4)
        return (norm ** (self.k - 1)) * psi
    
    def apply(self, state: ElementalState) -> ElementalState:
        psi = np.real(state.to_array())
        f = self.growth_functional(state)
        result = psi + self.rho * f
        return ElementalState.from_array(result)


class Multiplication(AlchemicalOperator):
    """
    MULTIPLICATION (Aquarius) - Amplification of Stone's power.
    
    Effect:
    - Scaling field: O_11(Ψ) = μΨ, μ > 1
    - Self-strengthening transformation
    """
    
    def __init__(self, mu: float = 1.5, xi: float = 0.1):
        super().__init__(AlchemicalOperation.MULTIPLICATION)
        self.mu_base = mu
        self.xi = xi
    
    def compute_multiplier(self, state: ElementalState) -> float:
        """μ = exp(ξ||Ψ||) for self-strengthening."""
        return math.exp(self.xi * state.norm) * self.mu_base
    
    def apply(self, state: ElementalState) -> ElementalState:
        mu = self.compute_multiplier(state)
        psi = state.to_array()
        result = mu * psi
        return ElementalState.from_array(result)


class Projection(AlchemicalOperator):
    """
    PROJECTION (Pisces) - Impose perfected frequency onto base matter.
    
    Effect:
    - Phase synchronization: P_Pis(Φ) = (Φ/||Φ||)||Ψ*||
    - Forces input to adopt Stone eigenstate
    """
    
    def __init__(self, stone_state: ElementalState = None):
        super().__init__(AlchemicalOperation.PROJECTION)
        if stone_state is None:
            # Default "perfected" Stone state (balanced)
            self.stone = ElementalState(0.5, 0.5, 0.5, 0.5)
        else:
            self.stone = stone_state
    
    def apply(self, state: ElementalState) -> ElementalState:
        """Force state to adopt Stone's pattern."""
        norm = state.norm
        if norm < 1e-10:
            return ElementalState.from_array(self.stone.to_array())
        
        # Project onto Stone direction with input's magnitude
        stone_normalized = self.stone.normalize()
        result = stone_normalized.to_array() * norm
        return ElementalState.from_array(result)


# =============================================================================
# THE GREAT WORK
# =============================================================================

class MagnumOpus:
    """
    The Great Work - Complete alchemical transformation algorithm.
    
    O_Magnum = O_12 ∘ O_11 ∘ ... ∘ O_1
    
    The Philosopher's Stone is an eigenvector:
    O_Magnum(Ψ*) = λΨ*, λ ≥ 1
    """
    
    def __init__(self):
        self.operations: List[AlchemicalOperator] = [
            Calcination(),
            Congelation(),
            Fixation(),
            Dissolution(),
            Digestion(),
            Distillation(),
            Sublimation(),
            Separation(),
            Ceration(),
            Fermentation(),
            Multiplication(),
            Projection()
        ]
    
    def apply_single(self, state: ElementalState, 
                    operation: AlchemicalOperation) -> ElementalState:
        """Apply a single operation."""
        op = self.operations[operation.value - 1]
        return op.apply(state)
    
    def apply_sequence(self, state: ElementalState,
                      operations: List[AlchemicalOperation]) -> ElementalState:
        """Apply a sequence of operations."""
        current = state
        for op in operations:
            current = self.apply_single(current, op)
        return current
    
    def apply_full(self, state: ElementalState) -> ElementalState:
        """
        Apply the complete Magnum Opus.
        
        O_Magnum = O_12 ∘ O_11 ∘ ... ∘ O_1
        """
        current = state
        for op in self.operations:
            current = op.apply(current)
        return current
    
    def apply_phase(self, state: ElementalState, 
                   phase: str) -> ElementalState:
        """Apply operations for a specific phase."""
        phase_ops = {
            "Nigredo": [AlchemicalOperation.CALCINATION, 
                       AlchemicalOperation.CONGELATION,
                       AlchemicalOperation.FIXATION,
                       AlchemicalOperation.DISSOLUTION],
            "Albedo": [AlchemicalOperation.DIGESTION,
                      AlchemicalOperation.DISTILLATION,
                      AlchemicalOperation.SUBLIMATION,
                      AlchemicalOperation.SEPARATION],
            "Rubedo": [AlchemicalOperation.CERATION,
                      AlchemicalOperation.FERMENTATION,
                      AlchemicalOperation.MULTIPLICATION,
                      AlchemicalOperation.PROJECTION]
        }
        return self.apply_sequence(state, phase_ops.get(phase, []))
    
    def find_stone(self, max_iterations: int = 100,
                  tol: float = 1e-4) -> Optional[ElementalState]:
        """
        Find the Philosopher's Stone - eigenvector of O_Magnum.
        
        Searches for Ψ* such that O_Magnum(Ψ*) = λΨ*
        """
        # Start with balanced state
        current = ElementalState(0.5, 0.5, 0.5, 0.5)
        
        for i in range(max_iterations):
            # Apply full opus
            result = self.apply_full(current)
            
            # Check if eigenvector (parallel to current)
            current_norm = current.normalize()
            result_norm = result.normalize()
            
            diff = np.linalg.norm(
                current_norm.to_array() - result_norm.to_array()
            )
            
            if diff < tol:
                # Found eigenstate
                return result
            
            # Update (power iteration style)
            current = result.normalize()
        
        return current
    
    def compute_eigenvalue(self, stone: ElementalState) -> float:
        """Compute eigenvalue λ for the Stone."""
        result = self.apply_full(stone)
        if stone.norm < 1e-10:
            return 0.0
        return result.norm / stone.norm


# =============================================================================
# VALIDATION
# =============================================================================

def validate_twelve_operations() -> bool:
    """Validate the 12 operations module."""
    
    # Test individual operations
    state = ElementalState(fire=0.5, air=0.3, water=0.1, earth=0.1)
    
    calc = Calcination()
    result = calc.apply(state)
    assert isinstance(result, ElementalState)
    
    cong = Congelation()
    result = cong.apply(state)
    assert isinstance(result, ElementalState)
    
    # Test all 12 operations have correct zodiac
    for op in AlchemicalOperation:
        assert op.zodiac in [
            "Aries", "Taurus", "Gemini", "Cancer",
            "Leo", "Virgo", "Libra", "Scorpio",
            "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]
    
    # Test phases
    assert AlchemicalOperation.CALCINATION.phase == "Nigredo"
    assert AlchemicalOperation.DIGESTION.phase == "Albedo"
    assert AlchemicalOperation.PROJECTION.phase == "Rubedo"
    
    # Test Magnum Opus
    opus = MagnumOpus()
    
    # Apply single
    result = opus.apply_single(state, AlchemicalOperation.CALCINATION)
    assert isinstance(result, ElementalState)
    
    # Apply full
    result = opus.apply_full(state)
    assert isinstance(result, ElementalState)
    
    # Apply phase
    nigredo_result = opus.apply_phase(state, "Nigredo")
    assert isinstance(nigredo_result, ElementalState)
    
    # Find Stone
    stone = opus.find_stone(max_iterations=50)
    assert stone is not None
    
    # Check eigenvalue
    eigenvalue = opus.compute_eigenvalue(stone)
    assert eigenvalue > 0
    
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("ATHENA OS - THE 12 ALCHEMICAL OPERATIONS")
    print("The Great Work as a Structured Algorithm")
    print("=" * 60)
    
    print("\nValidating module...")
    assert validate_twelve_operations()
    print("✓ Module validated")
    
    # Demo
    print("\n--- THE 12 OPERATIONS ---")
    for op in AlchemicalOperation:
        print(f"  {op.value:2d}. {op.name:15s} ({op.zodiac:12s}) - {op.phase}")
    
    print("\n--- MAGNUM OPUS DEMONSTRATION ---")
    
    # Initial "prima materia"
    prima_materia = ElementalState(fire=0.2, air=0.1, water=0.3, earth=0.4)
    print(f"\nPrima Materia:")
    print(f"  Fire={prima_materia.fire:.2f}, Air={prima_materia.air:.2f}, " +
          f"Water={prima_materia.water:.2f}, Earth={prima_materia.earth:.2f}")
    
    opus = MagnumOpus()
    
    # Process through phases
    print("\n--- PHASE PROGRESSION ---")
    current = prima_materia
    
    for phase in ["Nigredo", "Albedo", "Rubedo"]:
        current = opus.apply_phase(current, phase)
        print(f"\nAfter {phase}:")
        print(f"  Fire={abs(current.fire):.3f}, Air={abs(current.air):.3f}, " +
              f"Water={abs(current.water):.3f}, Earth={abs(current.earth):.3f}")
    
    # Find the Stone
    print("\n--- FINDING THE PHILOSOPHER'S STONE ---")
    stone = opus.find_stone(max_iterations=100)
    eigenvalue = opus.compute_eigenvalue(stone)
    
    print(f"\nPhilosopher's Stone found:")
    print(f"  Fire={abs(stone.fire):.3f}, Air={abs(stone.air):.3f}, " +
          f"Water={abs(stone.water):.3f}, Earth={abs(stone.earth):.3f}")
    print(f"  Eigenvalue λ = {eigenvalue:.3f}")
    print(f"  (λ ≥ 1 indicates stable/amplifying Stone)")
