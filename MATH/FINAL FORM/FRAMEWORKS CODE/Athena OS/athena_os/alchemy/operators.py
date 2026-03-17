"""
ATHENA OS - ALCHEMY MODULE: OPERATORS
=====================================
The Tria Prima and Operator Algebra

THE TRIA PRIMA (Three Principles):
    Sulfur (??) - The Combustible Principle (Soul)
        Increases Fire/Air, modifies Quintessence
        Root of all transformation
    
    Mercury (ℳ) - The Fluid Principle (Spirit)
        Redistributes elements at fixed total
        The mediating bridge
    
    Salt (??a) - The Fixed Principle (Body)
        Opposite to Sulfur, stabilizing
        The crystalline anchor

THE PLANETARY OPERATORS:
    ☉ Sun     - Exaltation, vitality, gold
    ☽ Moon    - Reflection, flux, silver
    ☿ Mercury - Volatility, communication
    ♀ Venus   - Harmony, attraction, copper
    ♂ Mars    - Force, separation, iron
    ♃ Jupiter - Expansion, governance, tin
    ♄ Saturn  - Contraction, limit, lead

THE ZODIACAL GENERATORS (12-fold):
    12 transformations forming a closed algebra
    Each sign = specific elemental operation

OPERATOR ALGEBRA:
    [X_i, X_j] = f^k_ij X_k (structure constants)
    Lie bracket relations define transformation grammar

SPECIAL OPERATORS:
    Green Lion (??) - Universal dissolution
    Dragon (??) - Entropy, chaos
    Phoenix (??) - Regeneration
    Quintessence (??) - Fifth element synthesis

SOURCES:
    - THE_MATH_OF_ALCHEMY.docx
    - Paracelsian tria prima
    - Hermetic planetary correspondences
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import numpy as np

from .elements import ElementalState, Element, ElementalSimplex


# =============================================================================
# OPERATOR TYPES
# =============================================================================

class OperatorType(Enum):
    """Types of alchemical operators."""
    
    TRIA_PRIMA = "tria_prima"
    PLANETARY = "planetary"
    ZODIACAL = "zodiacal"
    SPECIAL = "special"
    DISSOLUTION = "dissolution"
    COAGULATION = "coagulation"


class Planet(Enum):
    """The seven classical planets."""
    
    SUN = "sun"
    MOON = "moon"
    MERCURY = "mercury"
    VENUS = "venus"
    MARS = "mars"
    JUPITER = "jupiter"
    SATURN = "saturn"


class ZodiacSign(Enum):
    """The twelve zodiac signs."""
    
    ARIES = "aries"
    TAURUS = "taurus"
    GEMINI = "gemini"
    CANCER = "cancer"
    LEO = "leo"
    VIRGO = "virgo"
    LIBRA = "libra"
    SCORPIO = "scorpio"
    SAGITTARIUS = "sagittarius"
    CAPRICORN = "capricorn"
    AQUARIUS = "aquarius"
    PISCES = "pisces"


# =============================================================================
# BASE OPERATOR
# =============================================================================

@dataclass
class AlchemicalOperator:
    """
    Base class for alchemical operators.
    
    An operator transforms one elemental state to another:
    Ψ' = O(Ψ)
    """
    
    name: str
    symbol: str
    operator_type: OperatorType
    
    # Strength/intensity parameter
    intensity: float = 1.0
    
    # Transformation matrix (4x4 for elemental state)
    matrix: Optional[np.ndarray] = None
    
    def apply(self, state: ElementalState) -> ElementalState:
        """Apply the operator to a state."""
        if self.matrix is not None:
            v = self.matrix @ state.vector * self.intensity
            # Project back to simplex
            v = ElementalSimplex.project_to_simplex(v)
            return ElementalState.from_vector(v)
        return state
    
    def compose(self, other: AlchemicalOperator) -> AlchemicalOperator:
        """Compose two operators: (self ∘ other)."""
        if self.matrix is not None and other.matrix is not None:
            new_matrix = self.matrix @ other.matrix
            return AlchemicalOperator(
                name=f"{self.name}∘{other.name}",
                symbol=f"({self.symbol}∘{other.symbol})",
                operator_type=OperatorType.SPECIAL,
                matrix=new_matrix
            )
        return self
    
    def __call__(self, state: ElementalState) -> ElementalState:
        return self.apply(state)


# =============================================================================
# TRIA PRIMA
# =============================================================================

class Sulfur(AlchemicalOperator):
    """
    Sulfur (??) - The Combustible Principle.
    
    Increases Fire/Air (hot elements), modifies quintessence.
    The soul of transformation, root of combustion.
    """
    
    def __init__(self, intensity: float = 0.1):
        # Matrix that shifts toward hot elements
        matrix = np.array([
            [1.2, 0.1, 0.0, 0.1],   # Fire increases
            [0.1, 1.1, 0.1, 0.0],   # Air increases slightly
            [0.0, 0.1, 0.8, 0.0],   # Water decreases
            [0.1, 0.0, 0.0, 0.8],   # Earth decreases
        ])
        
        super().__init__(
            name="Sulfur",
            symbol="??",
            operator_type=OperatorType.TRIA_PRIMA,
            intensity=intensity,
            matrix=matrix
        )
    
    def apply(self, state: ElementalState) -> ElementalState:
        """Apply sulfurous transformation."""
        v = state.vector.copy()
        
        # Transfer from cold to hot
        delta = self.intensity * 0.5
        
        # Water → Air (wet stays, gains hot)
        transfer_w = min(delta, v[2])
        v[2] -= transfer_w
        v[1] += transfer_w
        
        # Earth → Fire (dry stays, gains hot)
        transfer_e = min(delta, v[3])
        v[3] -= transfer_e
        v[0] += transfer_e
        
        v = ElementalSimplex.project_to_simplex(v)
        return ElementalState.from_vector(v)


class Mercury(AlchemicalOperator):
    """
    Mercury (ℳ) - The Fluid Principle.
    
    Redistributes elements while preserving total.
    The mediating bridge, spirit of volatility.
    """
    
    def __init__(self, intensity: float = 0.1):
        # Mercury is a mixing/averaging operator
        # Moves toward uniform distribution
        uniform = np.ones((4, 4)) / 4
        identity = np.eye(4)
        matrix = identity + intensity * (uniform - identity)
        
        super().__init__(
            name="Mercury",
            symbol="☿",
            operator_type=OperatorType.TRIA_PRIMA,
            intensity=intensity,
            matrix=matrix
        )
    
    def apply(self, state: ElementalState) -> ElementalState:
        """Apply mercurial mixing."""
        centroid = np.array([0.25, 0.25, 0.25, 0.25])
        v = (1 - self.intensity) * state.vector + self.intensity * centroid
        return ElementalState.from_vector(v)


class Salt(AlchemicalOperator):
    """
    Salt (??a) - The Fixed Principle.
    
    Opposite to Sulfur - shifts toward cold/dry.
    The crystalline body, anchor of stability.
    """
    
    def __init__(self, intensity: float = 0.1):
        matrix = np.array([
            [0.8, 0.0, 0.1, 0.1],   # Fire decreases
            [0.0, 0.8, 0.1, 0.1],   # Air decreases
            [0.1, 0.1, 1.1, 0.0],   # Water increases
            [0.1, 0.1, 0.0, 1.2],   # Earth increases
        ])
        
        super().__init__(
            name="Salt",
            symbol="??",
            operator_type=OperatorType.TRIA_PRIMA,
            intensity=intensity,
            matrix=matrix
        )
    
    def apply(self, state: ElementalState) -> ElementalState:
        """Apply salt crystallization."""
        v = state.vector.copy()
        
        delta = self.intensity * 0.5
        
        # Fire → Earth
        transfer_f = min(delta, v[0])
        v[0] -= transfer_f
        v[3] += transfer_f
        
        # Air → Water
        transfer_a = min(delta, v[1])
        v[1] -= transfer_a
        v[2] += transfer_a
        
        v = ElementalSimplex.project_to_simplex(v)
        return ElementalState.from_vector(v)


# =============================================================================
# PLANETARY OPERATORS
# =============================================================================

@dataclass
class PlanetaryOperator(AlchemicalOperator):
    """
    Planetary operator - each planet modifies specific qualities.
    """
    
    planet: Planet = Planet.SUN
    
    def __post_init__(self):
        self.operator_type = OperatorType.PLANETARY
        self._setup_matrix()
    
    def _setup_matrix(self):
        """Setup transformation matrix based on planet."""
        # Identity base
        m = np.eye(4)
        
        if self.planet == Planet.SUN:
            # Sol exalts, increases vitality (Fire/Air)
            m[0, 0] = 1.2
            m[1, 1] = 1.1
            self.symbol = "☉"
            
        elif self.planet == Planet.MOON:
            # Luna reflects, increases moisture
            m[1, 1] = 1.1
            m[2, 2] = 1.2
            self.symbol = "☽"
            
        elif self.planet == Planet.MERCURY:
            # Mercury volatilizes, mixing
            m = np.ones((4, 4)) * 0.1 + np.eye(4) * 0.6
            self.symbol = "☿"
            
        elif self.planet == Planet.VENUS:
            # Venus harmonizes toward balance
            m = np.ones((4, 4)) * 0.15 + np.eye(4) * 0.4
            self.symbol = "♀"
            
        elif self.planet == Planet.MARS:
            # Mars heats and dries (Fire/Earth)
            m[0, 0] = 1.3
            m[3, 3] = 1.1
            self.symbol = "♂"
            
        elif self.planet == Planet.JUPITER:
            # Jupiter expands (Air dominant)
            m[1, 1] = 1.3
            self.symbol = "♃"
            
        elif self.planet == Planet.SATURN:
            # Saturn contracts, cools (Earth dominant)
            m[3, 3] = 1.3
            m[2, 2] = 1.1
            self.symbol = "♄"
        
        self.matrix = m


def create_planetary_operators() -> Dict[Planet, PlanetaryOperator]:
    """Create all planetary operators."""
    return {
        planet: PlanetaryOperator(
            name=planet.value.capitalize(),
            symbol="",
            operator_type=OperatorType.PLANETARY,
            planet=planet
        )
        for planet in Planet
    }


# =============================================================================
# ZODIACAL OPERATORS
# =============================================================================

@dataclass
class ZodiacalOperator(AlchemicalOperator):
    """
    Zodiacal operator - 12-fold transformation cycle.
    """
    
    sign: ZodiacSign = ZodiacSign.ARIES
    ruling_element: Element = Element.FIRE
    
    def __post_init__(self):
        self.operator_type = OperatorType.ZODIACAL
        self._setup_from_sign()
    
    def _setup_from_sign(self):
        """Setup based on zodiac sign."""
        # Zodiac element assignments
        fire_signs = [ZodiacSign.ARIES, ZodiacSign.LEO, ZodiacSign.SAGITTARIUS]
        earth_signs = [ZodiacSign.TAURUS, ZodiacSign.VIRGO, ZodiacSign.CAPRICORN]
        air_signs = [ZodiacSign.GEMINI, ZodiacSign.LIBRA, ZodiacSign.AQUARIUS]
        water_signs = [ZodiacSign.CANCER, ZodiacSign.SCORPIO, ZodiacSign.PISCES]
        
        if self.sign in fire_signs:
            self.ruling_element = Element.FIRE
            self.symbol = "♈♌♐"[fire_signs.index(self.sign)]
        elif self.sign in earth_signs:
            self.ruling_element = Element.EARTH
            self.symbol = "♉♍♑"[earth_signs.index(self.sign)]
        elif self.sign in air_signs:
            self.ruling_element = Element.AIR
            self.symbol = "♊♎♒"[air_signs.index(self.sign)]
        else:
            self.ruling_element = Element.WATER
            self.symbol = "♋♏♓"[water_signs.index(self.sign)]
        
        # Create matrix emphasizing ruling element
        self.matrix = np.eye(4)
        elem_idx = [Element.FIRE, Element.AIR, Element.WATER, Element.EARTH].index(self.ruling_element)
        self.matrix[elem_idx, elem_idx] = 1.2
    
    def apply(self, state: ElementalState) -> ElementalState:
        """Apply zodiacal influence."""
        v = self.matrix @ state.vector * self.intensity
        v = ElementalSimplex.project_to_simplex(v)
        return ElementalState.from_vector(v)


# =============================================================================
# SPECIAL OPERATORS
# =============================================================================

class GreenLion(AlchemicalOperator):
    """
    The Green Lion (Leo Viridis) - Universal dissolution.
    
    Drives all states toward uniform distribution.
    "The green lion devours all."
    """
    
    def __init__(self, intensity: float = 0.2):
        super().__init__(
            name="Green Lion",
            symbol="??",
            operator_type=OperatorType.DISSOLUTION,
            intensity=intensity
        )
    
    def apply(self, state: ElementalState) -> ElementalState:
        """Dissolve toward maximum entropy."""
        uniform = np.array([0.25, 0.25, 0.25, 0.25])
        v = (1 - self.intensity) * state.vector + self.intensity * uniform
        return ElementalState.from_vector(v)


class Dragon(AlchemicalOperator):
    """
    The Dragon - Entropy and chaos operator.
    
    Adds noise, increases disorder.
    """
    
    def __init__(self, intensity: float = 0.1):
        super().__init__(
            name="Dragon",
            symbol="??",
            operator_type=OperatorType.SPECIAL,
            intensity=intensity
        )
    
    def apply(self, state: ElementalState) -> ElementalState:
        """Add chaotic perturbation."""
        noise = np.random.randn(4) * self.intensity
        v = state.vector + noise
        v = ElementalSimplex.project_to_simplex(v)
        return ElementalState.from_vector(v)


class Phoenix(AlchemicalOperator):
    """
    The Phoenix - Regeneration from death.
    
    Extracts the seed from ash and regrows.
    """
    
    def __init__(self, intensity: float = 0.5, target: Element = Element.FIRE):
        super().__init__(
            name="Phoenix",
            symbol="??",
            operator_type=OperatorType.SPECIAL,
            intensity=intensity
        )
        self.target = target
    
    def apply(self, state: ElementalState) -> ElementalState:
        """Regenerate toward target element."""
        target_vec = ElementalState.pure(self.target).vector
        v = (1 - self.intensity) * state.vector + self.intensity * target_vec
        return ElementalState.from_vector(v)


class Quintessence(AlchemicalOperator):
    """
    Quintessence (??) - The Fifth Element synthesis.
    
    Emerges when all four elements are balanced AND correlated.
    """
    
    def __init__(self, intensity: float = 0.1):
        super().__init__(
            name="Quintessence",
            symbol="⊕",
            operator_type=OperatorType.SPECIAL,
            intensity=intensity
        )
    
    def compute_quintessence(self, state: ElementalState) -> float:
        """
        Compute quintessence level Q(Ψ).
        
        Q = det(Correlation_matrix)
        """
        v = state.vector
        # At balance, all equal → Q potential is maximized
        deviation = v - 0.25
        balance_score = 1.0 - np.sum(deviation**2) * 4
        
        # Also need correlation structure
        # Use product of deviations as correlation measure
        correlation = np.prod(1 - np.abs(deviation) * 4)
        
        return max(0, balance_score * correlation)
    
    def apply(self, state: ElementalState) -> ElementalState:
        """
        Apply quintessence synthesis.
        
        Moves toward perfect balance with correlation.
        """
        # Move toward balance
        balanced = np.array([0.25, 0.25, 0.25, 0.25])
        q = self.compute_quintessence(state)
        
        # Higher quintessence = stronger pull toward balance
        effective_intensity = self.intensity * (1 + q)
        v = (1 - effective_intensity) * state.vector + effective_intensity * balanced
        
        return ElementalState.from_vector(v)


# =============================================================================
# OPERATOR ALGEBRA
# =============================================================================

class OperatorAlgebra:
    """
    The complete operator algebra for alchemical transformations.
    
    Provides composition, commutation, and iteration.
    """
    
    def __init__(self):
        # Initialize standard operators
        self.sulfur = Sulfur()
        self.mercury = Mercury()
        self.salt = Salt()
        
        self.planetary = create_planetary_operators()
        
        self.green_lion = GreenLion()
        self.dragon = Dragon()
        self.phoenix = Phoenix()
        self.quintessence = Quintessence()
    
    def get_tria_prima(self) -> List[AlchemicalOperator]:
        """Get the three principles."""
        return [self.sulfur, self.mercury, self.salt]
    
    def commutator(self, op1: AlchemicalOperator, op2: AlchemicalOperator,
                   test_state: ElementalState = None) -> float:
        """
        Compute commutator [op1, op2] as distance metric.
        
        ||op1(op2(Ψ)) - op2(op1(Ψ))||
        """
        if test_state is None:
            test_state = ElementalSimplex.random_point()
        
        result_12 = op1(op2(test_state))
        result_21 = op2(op1(test_state))
        
        return float(np.linalg.norm(result_12.vector - result_21.vector))
    
    def iterate(self, operator: AlchemicalOperator, state: ElementalState,
                n: int) -> List[ElementalState]:
        """Iterate an operator n times, returning trajectory."""
        trajectory = [state]
        current = state
        
        for _ in range(n):
            current = operator(current)
            trajectory.append(current)
        
        return trajectory
    
    def compose_sequence(self, operators: List[AlchemicalOperator],
                        state: ElementalState) -> ElementalState:
        """Apply a sequence of operators."""
        result = state
        for op in operators:
            result = op(result)
        return result
    
    def find_fixed_point(self, operator: AlchemicalOperator,
                        initial: ElementalState = None,
                        max_iter: int = 1000,
                        tolerance: float = 1e-6) -> Optional[ElementalState]:
        """Find fixed point of an operator."""
        if initial is None:
            initial = ElementalSimplex.random_point()
        
        current = initial
        for _ in range(max_iter):
            next_state = operator(current)
            if np.linalg.norm(next_state.vector - current.vector) < tolerance:
                return next_state
            current = next_state
        
        return current  # Return last state even if not converged


# =============================================================================
# VALIDATION
# =============================================================================

def validate_operators() -> bool:
    """Validate operators module."""
    
    # Test Tria Prima
    state = ElementalState.balanced()
    
    sulfur = Sulfur(intensity=0.2)
    result = sulfur(state)
    assert result.heat > state.heat, "Sulfur should increase heat"
    
    salt = Salt(intensity=0.2)
    result = salt(state)
    assert result.heat < state.heat, "Salt should decrease heat"
    
    mercury = Mercury(intensity=0.5)
    pure_fire = ElementalState.pure(Element.FIRE)
    result = mercury(pure_fire)
    assert result.distance_from_balance() < pure_fire.distance_from_balance()
    
    # Test planetary operators
    ops = create_planetary_operators()
    assert len(ops) == 7
    
    mars = ops[Planet.MARS]
    result = mars.apply(state)
    assert ElementalSimplex.is_valid(result)
    
    # Test special operators
    lion = GreenLion(intensity=0.5)
    result = lion(pure_fire)
    assert result.distance_from_balance() < pure_fire.distance_from_balance()
    
    dragon = Dragon(intensity=0.1)
    result = dragon(state)
    assert ElementalSimplex.is_valid(result)
    
    phoenix = Phoenix(intensity=0.5, target=Element.FIRE)
    result = phoenix(state)
    assert result.fire > state.fire
    
    quint = Quintessence()
    q_val = quint.compute_quintessence(state)
    assert q_val >= 0
    
    # Test algebra
    algebra = OperatorAlgebra()
    tria = algebra.get_tria_prima()
    assert len(tria) == 3
    
    # Test iteration
    trajectory = algebra.iterate(sulfur, state, 10)
    assert len(trajectory) == 11
    
    # Test composition
    result = algebra.compose_sequence([sulfur, mercury, salt], state)
    assert ElementalSimplex.is_valid(result)
    
    return True


if __name__ == "__main__":
    print("Validating Operators Module...")
    assert validate_operators()
    print("✓ Operators Module validated")
    
    # Demo
    print("\n--- Operator Algebra Demo ---")
    
    algebra = OperatorAlgebra()
    state = ElementalState.balanced()
    
    print(f"\nInitial state: {state}")
    print(f"  Heat: {state.heat:.3f}, Moisture: {state.moisture:.3f}")
    
    print("\nApplying Tria Prima:")
    for op in algebra.get_tria_prima():
        result = op(state)
        print(f"  {op.symbol} {op.name}: Heat={result.heat:.3f}, "
              f"Moist={result.moisture:.3f}")
    
    print("\nPlanetary influences on pure Fire:")
    pure_fire = ElementalState.pure(Element.FIRE)
    for planet, op in algebra.planetary.items():
        result = op.apply(pure_fire)
        print(f"  {op.symbol} {planet.value}: {result}")
    
    print("\nQuintessence levels:")
    for elem in Element:
        pure = ElementalState.pure(elem)
        q = algebra.quintessence.compute_quintessence(pure)
        print(f"  Pure {elem.value}: Q={q:.4f}")
    
    balanced = ElementalState.balanced()
    q = algebra.quintessence.compute_quintessence(balanced)
    print(f"  Balanced: Q={q:.4f}")
