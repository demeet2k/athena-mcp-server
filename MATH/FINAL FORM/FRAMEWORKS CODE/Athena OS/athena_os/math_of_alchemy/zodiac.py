"""
ATHENA OS - THE MATH OF ALCHEMY
================================
Module IV: Zodiac (מזלות) - The Twelve Archetypal Generators

THE TWELVE ZODIACAL SIGNS:
    The Zodiac forms a C_12 cyclic symmetry group acting on elemental space.
    Each sign is a generator X_i in a Lie algebra.

    Fire Triplicity (Cardinal/Fixed/Mutable):
        ♈ Aries (Cardinal Fire) - Calcination
        ♌ Leo (Fixed Fire) - Digestion
        ♐ Sagittarius (Mutable Fire) - Incineration

    Earth Triplicity:
        ♑ Capricorn (Cardinal Earth) - Fermentation
        ♉ Taurus (Fixed Earth) - Congelation
        ♍ Virgo (Mutable Earth) - Distillation

    Air Triplicity:
        ♎ Libra (Cardinal Air) - Sublimation
        ♒ Aquarius (Fixed Air) - Multiplication
        ♊ Gemini (Mutable Air) - Fixation

    Water Triplicity:
        ♋ Cancer (Cardinal Water) - Dissolution
        ♏ Scorpio (Fixed Water) - Separation
        ♓ Pisces (Mutable Water) - Projection

THE 12 ALCHEMICAL OPERATIONS:
    Each zodiac sign governs one of the 12 classical operations
    of the Great Work (Magnum Opus).

SOURCES:
    THE MATH OF ALCHEMY
    Classical Astrological Tradition
    Alchemical Corpus
"""

from __future__ import annotations
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto

from .elements import ElementalState, Element


# =============================================================================
# ZODIAC TYPES
# =============================================================================

class ZodiacSign(Enum):
    """The Twelve Zodiacal Signs."""
    
    ARIES = (0, "♈", "Aries", Element.FIRE, "Cardinal", "Calcination")
    TAURUS = (1, "♉", "Taurus", Element.EARTH, "Fixed", "Congelation")
    GEMINI = (2, "♊", "Gemini", Element.AIR, "Mutable", "Fixation")
    CANCER = (3, "♋", "Cancer", Element.WATER, "Cardinal", "Dissolution")
    LEO = (4, "♌", "Leo", Element.FIRE, "Fixed", "Digestion")
    VIRGO = (5, "♍", "Virgo", Element.EARTH, "Mutable", "Distillation")
    LIBRA = (6, "♎", "Libra", Element.AIR, "Cardinal", "Sublimation")
    SCORPIO = (7, "♏", "Scorpio", Element.WATER, "Fixed", "Separation")
    SAGITTARIUS = (8, "♐", "Sagittarius", Element.FIRE, "Mutable", "Incineration")
    CAPRICORN = (9, "♑", "Capricorn", Element.EARTH, "Cardinal", "Fermentation")
    AQUARIUS = (10, "♒", "Aquarius", Element.AIR, "Fixed", "Multiplication")
    PISCES = (11, "♓", "Pisces", Element.WATER, "Mutable", "Projection")
    
    def __init__(self, index: int, symbol: str, name: str,
                 element: Element, modality: str, operation: str):
        self.index = index
        self.symbol = symbol
        self._name = name
        self.element = element
        self.modality = modality
        self.operation = operation
    
    @property
    def opposite(self) -> 'ZodiacSign':
        """Get the opposite sign (180° across the zodiac)."""
        opposite_idx = (self.index + 6) % 12
        return list(ZodiacSign)[opposite_idx]
    
    @property
    def is_cardinal(self) -> bool:
        return self.modality == "Cardinal"
    
    @property
    def is_fixed(self) -> bool:
        return self.modality == "Fixed"
    
    @property
    def is_mutable(self) -> bool:
        return self.modality == "Mutable"


class AlchemicalOperation(Enum):
    """The Twelve Alchemical Operations of the Great Work."""
    
    CALCINATION = (0, "Calcination", "Burning", ZodiacSign.ARIES, "Heating to ash")
    CONGELATION = (1, "Congelation", "Freezing", ZodiacSign.TAURUS, "Solidifying")
    FIXATION = (2, "Fixation", "Stabilizing", ZodiacSign.GEMINI, "Making volatile fixed")
    DISSOLUTION = (3, "Dissolution", "Dissolving", ZodiacSign.CANCER, "Breaking down")
    DIGESTION = (4, "Digestion", "Cooking", ZodiacSign.LEO, "Gentle sustained heat")
    DISTILLATION = (5, "Distillation", "Purifying", ZodiacSign.VIRGO, "Separating pure")
    SUBLIMATION = (6, "Sublimation", "Refining", ZodiacSign.LIBRA, "Solid to gas")
    SEPARATION = (7, "Separation", "Dividing", ZodiacSign.SCORPIO, "Splitting components")
    INCINERATION = (8, "Incineration", "Burning away", ZodiacSign.SAGITTARIUS, "Complete burning")
    FERMENTATION = (9, "Fermentation", "Transforming", ZodiacSign.CAPRICORN, "Decay/rebirth")
    MULTIPLICATION = (10, "Multiplication", "Increasing", ZodiacSign.AQUARIUS, "Augmenting power")
    PROJECTION = (11, "Projection", "Transmuting", ZodiacSign.PISCES, "Final transformation")
    
    def __init__(self, index: int, name: str, action: str,
                 zodiac: ZodiacSign, description: str):
        self.index = index
        self._name = name
        self.action = action
        self.zodiac = zodiac
        self._description = description


# =============================================================================
# ZODIACAL MATRICES
# =============================================================================

class ZodiacMatrices:
    """
    The 4×4 matrices encoding each zodiac sign's action on elemental space.
    
    D_i: V_elem → V_elem
    """
    
    @staticmethod
    def _element_template(element: Element) -> np.ndarray:
        """Base template for an element's triplicity."""
        if element == Element.FIRE:
            return np.array([
                [+1.0, +0.3, -0.3, -0.2],  # Fire amplified
                [0.0, 0.0, 0.0, 0.0],
                [-0.2, 0.0, 0.0, 0.0],     # Water reduced
                [-0.1, 0.0, 0.0, 0.0],     # Earth reduced
            ])
        elif element == Element.EARTH:
            return np.array([
                [-0.2, 0.0, 0.0, 0.0],     # Fire reduced
                [0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, -0.1],
                [-0.1, 0.0, -0.1, +1.0],   # Earth amplified
            ])
        elif element == Element.AIR:
            return np.array([
                [0.0, +0.3, 0.0, 0.0],
                [+0.3, +1.0, +0.3, 0.0],   # Air amplified
                [0.0, +0.2, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0],
            ])
        else:  # Water
            return np.array([
                [0.0, 0.0, -0.2, 0.0],
                [0.0, 0.0, +0.2, 0.0],
                [-0.2, +0.2, +1.0, 0.0],   # Water amplified
                [0.0, 0.0, 0.0, 0.0],
            ])
    
    @staticmethod
    def _modal_modifier(modality: str) -> np.ndarray:
        """Modal modification matrix."""
        eta = 0.3  # Cardinal intensity
        kappa = 0.2  # Fixed damping
        lam = 0.15  # Mutable mixing
        
        if modality == "Cardinal":
            return eta * np.eye(4)
        elif modality == "Fixed":
            return -kappa * np.eye(4)
        else:  # Mutable
            return np.array([
                [0, +lam, 0, -lam],
                [-lam, 0, +lam, 0],
                [0, -lam, 0, +lam],
                [+lam, 0, -lam, 0]
            ])
    
    @classmethod
    def get_matrix(cls, sign: ZodiacSign) -> np.ndarray:
        """Get the full zodiacal matrix for a sign."""
        elem_base = cls._element_template(sign.element)
        modal_mod = cls._modal_modifier(sign.modality)
        return elem_base + modal_mod
    
    @classmethod
    def all_matrices(cls) -> Dict[ZodiacSign, np.ndarray]:
        """Get all 12 zodiacal matrices."""
        return {sign: cls.get_matrix(sign) for sign in ZodiacSign}


# =============================================================================
# ZODIACAL OPERATOR
# =============================================================================

@dataclass
class ZodiacOperator:
    """
    A single zodiacal operator (generator).
    
    X_i ∈ Lie algebra acting on V_elem
    """
    
    sign: ZodiacSign
    intensity: float = 1.0
    
    @property
    def matrix(self) -> np.ndarray:
        """Get the zodiacal matrix."""
        return self.intensity * ZodiacMatrices.get_matrix(self.sign)
    
    @property
    def operation(self) -> AlchemicalOperation:
        """Get the associated alchemical operation."""
        for op in AlchemicalOperation:
            if op.zodiac == self.sign:
                return op
        return None
    
    def apply(self, state: ElementalState, dt: float = 0.1) -> ElementalState:
        """
        Apply the zodiacal operator.
        
        dΨ/dt = D_i · Ψ
        """
        psi = state.vector.real
        dpsi = self.matrix @ psi
        new_psi = psi + dpsi * dt
        return ElementalState.from_vector(new_psi.astype(complex))
    
    def eigenanalysis(self) -> Dict[str, Any]:
        """Analyze eigenstructure of the zodiacal matrix."""
        eigenvalues, eigenvectors = np.linalg.eig(self.matrix)
        return {
            "eigenvalues": eigenvalues,
            "eigenvectors": eigenvectors,
            "spectral_radius": np.max(np.abs(eigenvalues)),
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Get operator summary."""
        return {
            "sign": self.sign._name,
            "symbol": self.sign.symbol,
            "element": self.sign.element._name,
            "modality": self.sign.modality,
            "operation": self.operation._name if self.operation else None,
            "intensity": self.intensity,
        }


# =============================================================================
# ZODIACAL SYSTEM (LIE ALGEBRA)
# =============================================================================

@dataclass
class ZodiacSystem:
    """
    The full zodiacal Lie algebra acting on elemental space.
    
    Contains 12 generators with commutation relations.
    """
    
    operators: Dict[ZodiacSign, ZodiacOperator] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize all zodiacal operators if not provided."""
        if not self.operators:
            for sign in ZodiacSign:
                self.operators[sign] = ZodiacOperator(sign=sign)
    
    def commutator(self, sign1: ZodiacSign, sign2: ZodiacSign) -> np.ndarray:
        """
        Compute the Lie bracket [X_i, X_j] = X_i X_j - X_j X_i
        """
        X1 = self.operators[sign1].matrix
        X2 = self.operators[sign2].matrix
        return X1 @ X2 - X2 @ X1
    
    def apply_sign(self, state: ElementalState, sign: ZodiacSign,
                   dt: float = 0.1) -> ElementalState:
        """Apply a single zodiacal operator."""
        return self.operators[sign].apply(state, dt)
    
    def apply_sequence(self, state: ElementalState,
                       sequence: List[ZodiacSign],
                       dt: float = 0.1) -> ElementalState:
        """Apply a sequence of zodiacal operators."""
        current = state
        for sign in sequence:
            current = self.apply_sign(current, sign, dt)
        return current
    
    def yearly_evolution(self, initial_state: ElementalState,
                         steps_per_sign: int = 30) -> List[Tuple[ZodiacSign, ElementalState]]:
        """
        Simulate the yearly solar transit through all 12 signs.
        """
        trajectory = []
        current = initial_state
        
        for sign in ZodiacSign:
            for _ in range(steps_per_sign):
                current = self.apply_sign(current, sign, dt=0.1)
            trajectory.append((sign, current))
        
        return trajectory
    
    def get_triplicity(self, element: Element) -> List[ZodiacSign]:
        """Get the three signs of an elemental triplicity."""
        return [sign for sign in ZodiacSign if sign.element == element]
    
    def get_quadruplicity(self, modality: str) -> List[ZodiacSign]:
        """Get the four signs of a modal quadruplicity."""
        return [sign for sign in ZodiacSign if sign.modality == modality]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get system summary."""
        return {
            "signs": len(self.operators),
            "triplicities": {
                "fire": [s._name for s in self.get_triplicity(Element.FIRE)],
                "earth": [s._name for s in self.get_triplicity(Element.EARTH)],
                "air": [s._name for s in self.get_triplicity(Element.AIR)],
                "water": [s._name for s in self.get_triplicity(Element.WATER)],
            },
            "modalities": {
                "cardinal": [s._name for s in self.get_quadruplicity("Cardinal")],
                "fixed": [s._name for s in self.get_quadruplicity("Fixed")],
                "mutable": [s._name for s in self.get_quadruplicity("Mutable")],
            },
        }


# =============================================================================
# THE GREAT WORK (MAGNUM OPUS)
# =============================================================================

@dataclass
class MagnumOpus:
    """
    The Great Work - the composite of all 12 alchemical operations.
    
    O_Magnum = O_12 ∘ O_11 ∘ ... ∘ O_1
    
    The goal is to find the Philosopher's Stone - a fixed point
    of this composite operator.
    """
    
    zodiac_system: ZodiacSystem = field(default_factory=ZodiacSystem)
    
    @property
    def operation_sequence(self) -> List[AlchemicalOperation]:
        """The canonical sequence of the 12 operations."""
        return list(AlchemicalOperation)
    
    @property
    def zodiac_sequence(self) -> List[ZodiacSign]:
        """The zodiacal sequence of the Work."""
        return list(ZodiacSign)
    
    def execute_full_work(self, initial_state: ElementalState,
                          cycles: int = 1,
                          dt: float = 0.1) -> ElementalState:
        """
        Execute the complete Magnum Opus.
        
        Applies all 12 operations in sequence.
        """
        current = initial_state
        
        for _ in range(cycles):
            current = self.zodiac_system.apply_sequence(
                current, self.zodiac_sequence, dt
            )
        
        return current
    
    def find_stone(self, initial_state: ElementalState,
                   max_cycles: int = 100,
                   tolerance: float = 1e-6,
                   dt: float = 0.1) -> Tuple[ElementalState, bool, int]:
        """
        Search for the Philosopher's Stone (fixed point).
        
        Returns (final_state, converged, cycles_taken).
        """
        current = initial_state
        
        for cycle in range(max_cycles):
            next_state = self.execute_full_work(current, cycles=1, dt=dt)
            
            # Check for eigenstate condition
            diff = np.linalg.norm(next_state.vector - current.vector)
            if diff < tolerance:
                return next_state, True, cycle + 1
            
            current = next_state
        
        return current, False, max_cycles
    
    def stage_analysis(self, state: ElementalState) -> List[Dict[str, Any]]:
        """
        Analyze the state after each operation of the Work.
        """
        analysis = []
        current = state
        
        for op in AlchemicalOperation:
            sign = op.zodiac
            current = self.zodiac_system.apply_sign(current, sign, dt=0.1)
            
            analysis.append({
                "operation": op._name,
                "zodiac": sign._name,
                "element": sign.element._name,
                "state": {
                    "fire": float(current.fire.real),
                    "air": float(current.air.real),
                    "water": float(current.water.real),
                    "earth": float(current.earth.real),
                },
                "magnitude": current.magnitude,
            })
        
        return analysis
    
    def get_summary(self) -> Dict[str, Any]:
        """Get Magnum Opus summary."""
        return {
            "operations": [op._name for op in self.operation_sequence],
            "formula": "O_Magnum = O_12 ∘ ... ∘ O_1",
            "goal": "Find fixed point (Philosopher's Stone)",
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_zodiac() -> bool:
    """Validate the Zodiac module."""
    
    # Test ZodiacSign
    assert ZodiacSign.ARIES.element == Element.FIRE
    assert ZodiacSign.ARIES.modality == "Cardinal"
    assert ZodiacSign.ARIES.opposite == ZodiacSign.LIBRA
    
    # Test all signs
    assert len(list(ZodiacSign)) == 12
    
    # Test AlchemicalOperation
    assert AlchemicalOperation.CALCINATION.zodiac == ZodiacSign.ARIES
    assert len(list(AlchemicalOperation)) == 12
    
    # Test ZodiacMatrices
    aries_matrix = ZodiacMatrices.get_matrix(ZodiacSign.ARIES)
    assert aries_matrix.shape == (4, 4)
    
    all_matrices = ZodiacMatrices.all_matrices()
    assert len(all_matrices) == 12
    
    # Test ZodiacOperator
    aries_op = ZodiacOperator(sign=ZodiacSign.ARIES)
    assert aries_op.operation == AlchemicalOperation.CALCINATION
    
    state = ElementalState(fire=0.3, air=0.3, water=0.2, earth=0.2)
    new_state = aries_op.apply(state, dt=0.1)
    assert new_state.fire.real != state.fire.real
    
    # Test ZodiacSystem
    system = ZodiacSystem()
    assert len(system.operators) == 12
    
    # Test commutator
    comm = system.commutator(ZodiacSign.ARIES, ZodiacSign.LIBRA)
    assert comm.shape == (4, 4)
    
    # Test triplicities
    fire_signs = system.get_triplicity(Element.FIRE)
    assert len(fire_signs) == 3
    assert ZodiacSign.ARIES in fire_signs
    
    # Test MagnumOpus
    opus = MagnumOpus()
    assert len(opus.operation_sequence) == 12
    
    # Test execute_full_work
    final = opus.execute_full_work(state, cycles=1, dt=0.1)
    assert final.magnitude > 0
    
    return True


if __name__ == "__main__":
    print("Validating Zodiac Module...")
    assert validate_zodiac()
    print("✓ Zodiac module validated")
    
    # Demo
    print("\n--- Zodiac Demo ---")
    
    print("\nThe Twelve Signs and Operations:")
    for sign in ZodiacSign:
        print(f"  {sign.symbol} {sign._name:12} | {sign.element._name:5} | "
              f"{sign.modality:8} | {sign.operation}")
    
    print("\nTriplicities:")
    system = ZodiacSystem()
    for elem in Element:
        signs = system.get_triplicity(elem)
        names = [s._name for s in signs]
        print(f"  {elem._name}: {names}")
    
    # Execute Magnum Opus
    print("\n--- Magnum Opus Execution ---")
    opus = MagnumOpus()
    
    initial = ElementalState(fire=0.1, air=0.1, water=0.1, earth=0.7)
    print(f"\nInitial (Lead-like): Fire={initial.fire.real:.3f}, Earth={initial.earth.real:.3f}")
    
    final, converged, cycles = opus.find_stone(initial, max_cycles=50, dt=0.1)
    print(f"\nFinal State: Fire={final.fire.real:.3f}, Air={final.air.real:.3f}, "
          f"Water={final.water.real:.3f}, Earth={final.earth.real:.3f}")
    print(f"Converged: {converged} in {cycles} cycles")
