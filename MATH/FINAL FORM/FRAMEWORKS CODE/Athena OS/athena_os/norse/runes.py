"""
ATHENA OS - NORSE: RUNES MODULE
================================
The Elder Futhark Operator Algebra (ℜ₂₄)

THE FUTHARK BASIS:
    24 unitary operators {R̂₁, R̂₂, ..., R̂₂₄} forming a non-abelian group.
    
    Runes are not merely an alphabet - they are discrete transformation
    matrices acting on the local manifold.

OPERATOR TYPES:
    - Fehu (F̂): Accumulation - increases scalar potential
    - Hagalaz (Ĥ): Disruption - introduces stochastic noise
    - Isa (Î): Stasis - halts time evolution (dS/dt → 0)
    - Ansuz (Â): Communication - opens channels between nodes

RUNECASTING:
    A query to the Wyrd Kernel. Measurement operation M̂ that
    collapses superposition of future probabilities.
    
    Cast() → {R̂ᵢ, R̂ⱼ, R̂ₖ} maximizing ⟨ψ_final|R̂ₖR̂ⱼR̂ᵢ|ψ_initial⟩

THE THREE AETTIR:
    1. Freya's Aett (1-8): Material/Wealth operations
    2. Heimdall's Aett (9-16): Elemental/Natural operations  
    3. Tyr's Aett (17-24): Spiritual/Victory operations
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Callable, Any, Union
from enum import Enum, auto
import numpy as np


# =============================================================================
# AETTIR (RUNE FAMILIES)
# =============================================================================

class Aett(Enum):
    """The three Aettir (families) of runes."""
    
    FREYA = "freya"       # Material/Wealth (1-8)
    HEIMDALL = "heimdall" # Elemental/Natural (9-16)
    TYR = "tyr"           # Spiritual/Victory (17-24)


class RuneElement(Enum):
    """Elemental associations of runes."""
    
    FIRE = "fire"
    ICE = "ice"
    EARTH = "earth"
    AIR = "air"
    WATER = "water"
    VOID = "void"


# =============================================================================
# RUNE
# =============================================================================

@dataclass
class Rune:
    """
    A single rune from the Elder Futhark.
    
    Each rune is a discrete transformation operator.
    """
    
    index: int              # 1-24
    glyph: str              # Unicode rune character
    name: str               # Traditional name
    phoneme: str            # Sound value
    meaning: str            # Primary meaning
    aett: Aett              # Which Aett it belongs to
    element: RuneElement    # Elemental association
    
    # Operator properties
    operator_type: str = ""
    effect_magnitude: float = 1.0
    
    # Position in Aett (1-8)
    aett_position: int = 0
    
    def __post_init__(self):
        self.aett_position = ((self.index - 1) % 8) + 1
    
    def as_vector(self, dimension: int = 24) -> np.ndarray:
        """Get rune as one-hot vector."""
        vec = np.zeros(dimension)
        vec[self.index - 1] = 1.0
        return vec
    
    def as_matrix(self, dimension: int = 8) -> np.ndarray:
        """
        Get rune as transformation matrix.
        
        Based on index and effect magnitude.
        """
        # Create rotation-like transformation
        angle = (self.index / 24) * 2 * np.pi
        
        matrix = np.eye(dimension)
        
        # Apply rotation in first two dimensions
        c, s = np.cos(angle), np.sin(angle)
        matrix[0, 0] = c
        matrix[0, 1] = -s
        matrix[1, 0] = s
        matrix[1, 1] = c
        
        # Scale by magnitude
        matrix *= self.effect_magnitude
        
        return matrix


# =============================================================================
# ELDER FUTHARK
# =============================================================================

def create_elder_futhark() -> Dict[int, Rune]:
    """
    Create the complete Elder Futhark (24 runes).
    
    These form the operator algebra ℜ₂₄.
    """
    runes = {}
    
    # FREYA'S AETT (1-8) - Material/Wealth
    runes[1] = Rune(1, "ᚠ", "Fehu", "f", "Wealth/Cattle", Aett.FREYA, RuneElement.FIRE,
                   operator_type="accumulation", effect_magnitude=1.2)
    runes[2] = Rune(2, "ᚢ", "Uruz", "u", "Aurochs/Strength", Aett.FREYA, RuneElement.EARTH,
                   operator_type="force", effect_magnitude=1.3)
    runes[3] = Rune(3, "ᚦ", "Thurisaz", "th", "Thorn/Giant", Aett.FREYA, RuneElement.FIRE,
                   operator_type="destruction", effect_magnitude=1.5)
    runes[4] = Rune(4, "ᚨ", "Ansuz", "a", "God/Signal", Aett.FREYA, RuneElement.AIR,
                   operator_type="communication", effect_magnitude=1.1)
    runes[5] = Rune(5, "ᚱ", "Raidho", "r", "Journey/Ride", Aett.FREYA, RuneElement.AIR,
                   operator_type="transport", effect_magnitude=1.0)
    runes[6] = Rune(6, "ᚲ", "Kenaz", "k", "Torch/Knowledge", Aett.FREYA, RuneElement.FIRE,
                   operator_type="illumination", effect_magnitude=1.2)
    runes[7] = Rune(7, "ᚷ", "Gebo", "g", "Gift/Exchange", Aett.FREYA, RuneElement.AIR,
                   operator_type="binding", effect_magnitude=1.0)
    runes[8] = Rune(8, "ᚹ", "Wunjo", "w", "Joy/Harmony", Aett.FREYA, RuneElement.EARTH,
                   operator_type="integration", effect_magnitude=0.9)
    
    # HEIMDALL'S AETT (9-16) - Elemental/Natural
    runes[9] = Rune(9, "ᚺ", "Hagalaz", "h", "Hail/Disruption", Aett.HEIMDALL, RuneElement.ICE,
                   operator_type="disruption", effect_magnitude=1.4)
    runes[10] = Rune(10, "ᚾ", "Nauthiz", "n", "Need/Necessity", Aett.HEIMDALL, RuneElement.FIRE,
                    operator_type="constraint", effect_magnitude=1.1)
    runes[11] = Rune(11, "ᛁ", "Isa", "i", "Ice/Stasis", Aett.HEIMDALL, RuneElement.ICE,
                    operator_type="freezing", effect_magnitude=1.3)
    runes[12] = Rune(12, "ᛃ", "Jera", "j", "Year/Harvest", Aett.HEIMDALL, RuneElement.EARTH,
                    operator_type="cycle", effect_magnitude=1.0)
    runes[13] = Rune(13, "ᛇ", "Eihwaz", "ei", "Yew/Axis", Aett.HEIMDALL, RuneElement.EARTH,
                    operator_type="connection", effect_magnitude=1.2)
    runes[14] = Rune(14, "ᛈ", "Perthro", "p", "Dice/Chance", Aett.HEIMDALL, RuneElement.WATER,
                    operator_type="probability", effect_magnitude=1.0)
    runes[15] = Rune(15, "ᛉ", "Algiz", "z", "Elk/Protection", Aett.HEIMDALL, RuneElement.AIR,
                    operator_type="shielding", effect_magnitude=1.3)
    runes[16] = Rune(16, "ᛊ", "Sowilo", "s", "Sun/Victory", Aett.HEIMDALL, RuneElement.FIRE,
                    operator_type="power", effect_magnitude=1.5)
    
    # TYR'S AETT (17-24) - Spiritual/Victory
    runes[17] = Rune(17, "ᛏ", "Tiwaz", "t", "Tyr/Justice", Aett.TYR, RuneElement.AIR,
                    operator_type="judgment", effect_magnitude=1.2)
    runes[18] = Rune(18, "ᛒ", "Berkano", "b", "Birch/Birth", Aett.TYR, RuneElement.EARTH,
                    operator_type="generation", effect_magnitude=1.1)
    runes[19] = Rune(19, "ᛖ", "Ehwaz", "e", "Horse/Movement", Aett.TYR, RuneElement.EARTH,
                    operator_type="velocity", effect_magnitude=1.2)
    runes[20] = Rune(20, "ᛗ", "Mannaz", "m", "Man/Human", Aett.TYR, RuneElement.AIR,
                    operator_type="self", effect_magnitude=1.0)
    runes[21] = Rune(21, "ᛚ", "Laguz", "l", "Water/Flow", Aett.TYR, RuneElement.WATER,
                    operator_type="flow", effect_magnitude=1.1)
    runes[22] = Rune(22, "ᛜ", "Ingwaz", "ng", "Ing/Seed", Aett.TYR, RuneElement.EARTH,
                    operator_type="potential", effect_magnitude=1.0)
    runes[23] = Rune(23, "ᛞ", "Dagaz", "d", "Day/Awakening", Aett.TYR, RuneElement.FIRE,
                    operator_type="transformation", effect_magnitude=1.4)
    runes[24] = Rune(24, "ᛟ", "Othala", "o", "Heritage/Home", Aett.TYR, RuneElement.EARTH,
                    operator_type="inheritance", effect_magnitude=1.0)
    
    return runes


# =============================================================================
# RUNE OPERATORS
# =============================================================================

class RuneOperator:
    """
    A rune as a quantum-like operator.
    
    Operates on state vectors in the manner described by the rune.
    """
    
    def __init__(self, rune: Rune, dimension: int = 8):
        self.rune = rune
        self.dimension = dimension
        self._matrix = self._build_matrix()
    
    def _build_matrix(self) -> np.ndarray:
        """Build the operator matrix based on rune type."""
        
        matrix = np.eye(self.dimension)
        
        op_type = self.rune.operator_type
        mag = self.rune.effect_magnitude
        
        if op_type == "accumulation":
            # Fehu: Add to all components
            matrix *= mag
            
        elif op_type == "force":
            # Uruz: Amplify magnitude
            matrix *= mag * 1.1
            
        elif op_type == "destruction":
            # Thurisaz: Introduce chaos
            noise = np.random.randn(self.dimension, self.dimension) * 0.1
            matrix = matrix * mag + noise
            
        elif op_type == "communication":
            # Ansuz: Open channels (off-diagonal)
            for i in range(self.dimension - 1):
                matrix[i, i+1] = 0.5 * mag
                matrix[i+1, i] = 0.5 * mag
                
        elif op_type == "disruption":
            # Hagalaz: Random perturbation
            noise = np.random.randn(self.dimension, self.dimension) * mag * 0.2
            matrix += noise
            
        elif op_type == "freezing":
            # Isa: Project toward zero evolution
            matrix *= (1.0 / mag)
            
        elif op_type == "probability":
            # Perthro: Stochastic matrix
            matrix = np.random.rand(self.dimension, self.dimension)
            matrix /= matrix.sum(axis=1, keepdims=True)
            
        elif op_type == "shielding":
            # Algiz: Increase norm preservation
            matrix = np.eye(self.dimension) * mag
            
        elif op_type == "power":
            # Sowilo: Maximum amplification
            matrix *= mag * 1.2
            
        elif op_type == "transformation":
            # Dagaz: Rotation
            angle = np.pi / 4
            c, s = np.cos(angle), np.sin(angle)
            matrix[0:2, 0:2] = np.array([[c, -s], [s, c]])
        
        return matrix
    
    def apply(self, state: np.ndarray) -> np.ndarray:
        """Apply operator to state vector."""
        if len(state) != self.dimension:
            raise ValueError(f"State dimension mismatch: {len(state)} vs {self.dimension}")
        return self._matrix @ state
    
    def compose(self, other: 'RuneOperator') -> 'RuneOperator':
        """Compose with another rune operator (matrix multiplication)."""
        # Create combined operator
        combined = RuneOperator(self.rune, self.dimension)
        combined._matrix = self._matrix @ other._matrix
        return combined
    
    @property
    def matrix(self) -> np.ndarray:
        return self._matrix.copy()


# =============================================================================
# RUNECASTING
# =============================================================================

class RuneCast:
    """
    A runecasting operation.
    
    Queries the Wyrd Kernel to determine optimal
    operator sequence for desired outcome.
    """
    
    def __init__(self, futhark: Dict[int, Rune], n_runes: int = 3):
        self.futhark = futhark
        self.n_runes = n_runes
        self._cast_result: List[Rune] = []
    
    def cast(self, seed: Optional[int] = None) -> List[Rune]:
        """
        Cast runes randomly.
        
        Returns list of drawn runes.
        """
        if seed is not None:
            np.random.seed(seed)
        
        indices = np.random.choice(
            list(self.futhark.keys()),
            size=self.n_runes,
            replace=False
        )
        
        self._cast_result = [self.futhark[i] for i in indices]
        return self._cast_result
    
    def cast_for_outcome(self, initial_state: np.ndarray,
                        target_state: np.ndarray,
                        dimension: int = 8) -> Tuple[List[Rune], float]:
        """
        Cast to find runes maximizing alignment with target.
        
        Returns (runes, alignment_score).
        """
        best_runes = []
        best_score = -float('inf')
        
        # Sample many combinations
        for _ in range(100):
            runes = self.cast()
            
            # Build combined operator
            state = initial_state.copy()
            for rune in runes:
                op = RuneOperator(rune, dimension)
                state = op.apply(state)
            
            # Compute alignment with target
            score = np.dot(state, target_state) / (
                np.linalg.norm(state) * np.linalg.norm(target_state) + 1e-10
            )
            
            if score > best_score:
                best_score = score
                best_runes = runes.copy()
        
        self._cast_result = best_runes
        return best_runes, best_score
    
    def interpret(self) -> Dict[str, Any]:
        """
        Interpret the current cast.
        
        Returns analysis of the cast.
        """
        if not self._cast_result:
            return {"error": "No cast performed"}
        
        interpretation = {
            "runes": [r.name for r in self._cast_result],
            "glyphs": "".join(r.glyph for r in self._cast_result),
            "meanings": [r.meaning for r in self._cast_result],
            "elements": [r.element.value for r in self._cast_result],
            "aettir": [r.aett.value for r in self._cast_result],
            "total_magnitude": sum(r.effect_magnitude for r in self._cast_result),
            "dominant_element": self._get_dominant_element(),
            "position_reading": self._positional_reading()
        }
        
        return interpretation
    
    def _get_dominant_element(self) -> str:
        """Get most common element in cast."""
        if not self._cast_result:
            return "none"
        
        elements = [r.element for r in self._cast_result]
        element_counts = {}
        for e in elements:
            element_counts[e] = element_counts.get(e, 0) + 1
        
        return max(element_counts, key=element_counts.get).value
    
    def _positional_reading(self) -> Dict[str, str]:
        """
        Generate positional reading.
        
        Position 1: Past
        Position 2: Present  
        Position 3: Future
        """
        if len(self._cast_result) < 3:
            return {}
        
        return {
            "past": self._cast_result[0].meaning,
            "present": self._cast_result[1].meaning,
            "future": self._cast_result[2].meaning
        }
    
    @property
    def result(self) -> List[Rune]:
        return self._cast_result.copy()


# =============================================================================
# RUNE ALGEBRA
# =============================================================================

class FutharkAlgebra:
    """
    The complete Elder Futhark operator algebra ℜ₂₄.
    
    Non-abelian group of 24 transformation operators.
    """
    
    def __init__(self, dimension: int = 8):
        self.dimension = dimension
        self.futhark = create_elder_futhark()
        self._operators: Dict[int, RuneOperator] = {}
        
        # Build operators
        for idx, rune in self.futhark.items():
            self._operators[idx] = RuneOperator(rune, dimension)
    
    def get_rune(self, index: int) -> Optional[Rune]:
        """Get rune by index (1-24)."""
        return self.futhark.get(index)
    
    def get_rune_by_name(self, name: str) -> Optional[Rune]:
        """Get rune by name."""
        for rune in self.futhark.values():
            if rune.name.lower() == name.lower():
                return rune
        return None
    
    def get_operator(self, index: int) -> Optional[RuneOperator]:
        """Get operator by rune index."""
        return self._operators.get(index)
    
    def compose_sequence(self, indices: List[int]) -> RuneOperator:
        """
        Compose a sequence of rune operators.
        
        Non-commutative: order matters!
        """
        if not indices:
            raise ValueError("Empty sequence")
        
        result = self._operators[indices[0]]
        
        for idx in indices[1:]:
            result = result.compose(self._operators[idx])
        
        return result
    
    def apply_sequence(self, state: np.ndarray, 
                      indices: List[int]) -> np.ndarray:
        """Apply sequence of runes to state."""
        for idx in indices:
            op = self._operators[idx]
            state = op.apply(state)
        return state
    
    def commutator(self, idx1: int, idx2: int) -> np.ndarray:
        """
        Compute commutator [R1, R2] = R1·R2 - R2·R1.
        
        Non-zero commutator indicates non-commutativity.
        """
        R1 = self._operators[idx1].matrix
        R2 = self._operators[idx2].matrix
        
        return R1 @ R2 - R2 @ R1
    
    def is_commutative(self, idx1: int, idx2: int, 
                      tolerance: float = 1e-10) -> bool:
        """Check if two runes commute."""
        comm = self.commutator(idx1, idx2)
        return np.allclose(comm, 0, atol=tolerance)
    
    def get_aett(self, aett: Aett) -> List[Rune]:
        """Get all runes in an Aett."""
        return [r for r in self.futhark.values() if r.aett == aett]
    
    def cast_runes(self, n: int = 3, seed: Optional[int] = None) -> RuneCast:
        """Perform a runecast."""
        cast = RuneCast(self.futhark, n)
        cast.cast(seed)
        return cast
    
    @property
    def n_runes(self) -> int:
        return len(self.futhark)


# =============================================================================
# VALIDATION
# =============================================================================

def validate_runes() -> bool:
    """Validate Norse runes module."""
    
    # Test Rune creation
    futhark = create_elder_futhark()
    assert len(futhark) == 24
    
    fehu = futhark[1]
    assert fehu.name == "Fehu"
    assert fehu.glyph == "ᚠ"
    assert fehu.aett == Aett.FREYA
    assert fehu.aett_position == 1
    
    hagalaz = futhark[9]
    assert hagalaz.aett == Aett.HEIMDALL
    assert hagalaz.operator_type == "disruption"
    
    tiwaz = futhark[17]
    assert tiwaz.aett == Aett.TYR
    
    # Test rune vector
    vec = fehu.as_vector()
    assert len(vec) == 24
    assert vec[0] == 1.0
    assert sum(vec) == 1.0
    
    # Test rune matrix
    mat = fehu.as_matrix()
    assert mat.shape == (8, 8)
    
    # Test RuneOperator
    op = RuneOperator(fehu, dimension=8)
    
    state = np.ones(8)
    new_state = op.apply(state)
    assert len(new_state) == 8
    
    # Test composition
    op2 = RuneOperator(hagalaz, dimension=8)
    composed = op.compose(op2)
    
    # Non-commutativity (composition order matters)
    composed2 = op2.compose(op)
    assert not np.allclose(composed.matrix, composed2.matrix)
    
    # Test RuneCast
    cast = RuneCast(futhark, n_runes=3)
    runes = cast.cast(seed=42)
    
    assert len(runes) == 3
    assert all(isinstance(r, Rune) for r in runes)
    
    interp = cast.interpret()
    assert len(interp["runes"]) == 3
    assert "past" in interp["position_reading"]
    
    # Test cast for outcome
    initial = np.random.randn(8)
    target = np.random.randn(8)
    
    best_runes, score = cast.cast_for_outcome(initial, target)
    assert len(best_runes) == 3
    assert -1 <= score <= 1
    
    # Test FutharkAlgebra
    algebra = FutharkAlgebra(dimension=8)
    
    assert algebra.n_runes == 24
    
    rune = algebra.get_rune(1)
    assert rune.name == "Fehu"
    
    rune2 = algebra.get_rune_by_name("Hagalaz")
    assert rune2.index == 9
    
    # Test sequence composition
    seq_op = algebra.compose_sequence([1, 9, 17])
    assert seq_op.matrix.shape == (8, 8)
    
    # Test sequence application
    state = np.ones(8)
    final = algebra.apply_sequence(state, [1, 9, 17])
    assert len(final) == 8
    
    # Test commutator
    comm = algebra.commutator(1, 9)
    # Most runes should not commute
    assert comm.shape == (8, 8)
    
    # Test Aett extraction
    freya_aett = algebra.get_aett(Aett.FREYA)
    assert len(freya_aett) == 8
    
    # Test runecast
    cast = algebra.cast_runes(n=3, seed=123)
    assert len(cast.result) == 3
    
    return True


if __name__ == "__main__":
    print("Validating Norse Runes Module...")
    assert validate_runes()
    print("✓ Norse Runes Module validated")
