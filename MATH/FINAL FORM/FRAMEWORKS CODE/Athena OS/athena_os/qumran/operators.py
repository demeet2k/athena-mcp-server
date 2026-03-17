"""
ATHENA OS - QUMRAN KERNEL: OPERATORS MODULE
============================================
Ritual Operator Calculus

RITUAL OPERATOR CALCULUS (O):
    A suite of operators acting on individual and communal
    state vectors, scheduled according to the calendar.
    
OPERATOR TYPES:
    
    P (Purification):
        - Padyab (daily washing)
        - Nahn (full immersion)
        - Barashnum (major purification)
        Transforms: impure → pure
        
    B (Blessing):
        - Priestly blessing
        - Covenant blessing
        - Community blessing
        Amplifies: holiness, protection
        
    C (Curse):
        - Covenant curse
        - Exclusion curse
        Attenuates: standing, access
        
    E (Exorcism):
        - Binding spirits
        - Casting out demons
        Removes: demonic influence
        
    L (Liturgy):
        - Songs of Sabbath Sacrifice
        - Angelic communion
        - Praise sequences
        Elevates: spiritual state

STATE VECTORS:
    Individual state: (purity, holiness, standing, allegiance)
    Community state: (cohesion, sanctity, protection, blessing)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import numpy as np


# =============================================================================
# OPERATOR TYPES
# =============================================================================

class OperatorType(Enum):
    """Types of ritual operators."""
    
    PURIFICATION = "purification"    # P - cleansing
    BLESSING = "blessing"            # B - amplification
    CURSE = "curse"                  # C - attenuation
    EXORCISM = "exorcism"           # E - removal
    LITURGY = "liturgy"             # L - elevation
    SACRIFICE = "sacrifice"         # S - offering
    OATH = "oath"                   # O - binding


class PurificationType(Enum):
    """Types of purification rituals."""
    
    PADYAB = "padyab"           # Daily washing
    NAHN = "nahn"               # Full immersion
    BARASHNUM = "barashnum"     # Nine-day major purification
    SPRINKLING = "sprinkling"   # Water sprinkling
    ASH_WATER = "ash_water"     # Red heifer ashes


class ImpurityLevel(Enum):
    """Levels of ritual impurity."""
    
    PURE = "pure"               # Tahor
    LIGHT = "light"             # Minor impurity
    MODERATE = "moderate"       # Day-long impurity
    SEVERE = "severe"           # Week-long impurity
    CORPSE = "corpse"          # Corpse contamination (7 days)


# =============================================================================
# STATE VECTOR
# =============================================================================

@dataclass
class IndividualState:
    """
    State vector for an individual.
    
    Components:
    - purity: Ritual purity (0-1)
    - holiness: Sanctity level (0-1)
    - standing: Community standing (0-1)
    - allegiance: Light-darkness balance (-1 to 1)
    """
    
    purity: float = 1.0
    holiness: float = 0.5
    standing: float = 0.5
    allegiance: float = 0.5      # 1 = pure light, -1 = pure darkness
    
    def to_vector(self) -> np.ndarray:
        """Convert to numpy array."""
        return np.array([self.purity, self.holiness, self.standing, self.allegiance])
    
    @classmethod
    def from_vector(cls, vec: np.ndarray) -> IndividualState:
        """Create from numpy array."""
        return cls(
            purity=float(vec[0]),
            holiness=float(vec[1]),
            standing=float(vec[2]),
            allegiance=float(vec[3])
        )
    
    def is_valid(self) -> bool:
        """Check if state is valid (all values in range)."""
        return (0 <= self.purity <= 1 and
                0 <= self.holiness <= 1 and
                0 <= self.standing <= 1 and
                -1 <= self.allegiance <= 1)


@dataclass
class CommunityState:
    """
    State vector for the community (Yahad).
    
    Components:
    - cohesion: Unity of community (0-1)
    - sanctity: Collective holiness (0-1)
    - protection: Divine protection (0-1)
    - blessing: Accumulated blessing (0-1)
    """
    
    cohesion: float = 0.8
    sanctity: float = 0.7
    protection: float = 0.8
    blessing: float = 0.6
    
    def to_vector(self) -> np.ndarray:
        """Convert to numpy array."""
        return np.array([self.cohesion, self.sanctity, self.protection, self.blessing])


# =============================================================================
# BASE OPERATOR
# =============================================================================

@dataclass
class RitualOperator:
    """
    A ritual operator acting on state vectors.
    
    Operators are represented as linear transformations
    (matrices) that modify state.
    """
    
    name: str
    operator_type: OperatorType
    
    # Transformation matrix (4x4 for individual state)
    matrix: np.ndarray = field(default_factory=lambda: np.eye(4))
    
    # Requirements
    requires_purity: bool = False
    requires_priest: bool = False
    requires_sabbath: bool = False
    requires_temple: bool = False
    
    # Effects
    duration_days: int = 1
    
    def apply(self, state: IndividualState) -> IndividualState:
        """Apply operator to individual state."""
        vec = state.to_vector()
        new_vec = self.matrix @ vec
        
        # Clamp values
        new_vec[0:3] = np.clip(new_vec[0:3], 0, 1)
        new_vec[3] = np.clip(new_vec[3], -1, 1)
        
        return IndividualState.from_vector(new_vec)
    
    def can_apply(self, state: IndividualState,
                  has_priest: bool = False,
                  is_sabbath: bool = False) -> bool:
        """Check if operator can be applied."""
        if self.requires_purity and state.purity < 0.5:
            return False
        if self.requires_priest and not has_priest:
            return False
        if self.requires_sabbath and not is_sabbath:
            return False
        return True


# =============================================================================
# PURIFICATION OPERATORS
# =============================================================================

def create_purification_operator(level: PurificationType) -> RitualOperator:
    """Create a purification operator."""
    
    if level == PurificationType.PADYAB:
        # Daily washing - small purity boost
        matrix = np.eye(4)
        matrix[0, 0] = 1.1  # Purity increase
        return RitualOperator(
            name="Padyab (Daily Washing)",
            operator_type=OperatorType.PURIFICATION,
            matrix=matrix,
            duration_days=1
        )
    
    elif level == PurificationType.NAHN:
        # Full immersion - medium purity boost
        matrix = np.eye(4)
        matrix[0, 0] = 1.3  # Significant purity increase
        matrix[1, 1] = 1.1  # Small holiness boost
        return RitualOperator(
            name="Nahn (Full Immersion)",
            operator_type=OperatorType.PURIFICATION,
            matrix=matrix,
            duration_days=1
        )
    
    elif level == PurificationType.BARASHNUM:
        # Major purification - full restoration
        matrix = np.eye(4)
        matrix[0, 0] = 2.0  # Full purity restoration
        matrix[1, 1] = 1.2  # Holiness boost
        return RitualOperator(
            name="Barashnum (Major Purification)",
            operator_type=OperatorType.PURIFICATION,
            matrix=matrix,
            requires_priest=True,
            duration_days=9
        )
    
    else:
        # Default
        return RitualOperator(
            name="Basic Purification",
            operator_type=OperatorType.PURIFICATION,
            matrix=np.eye(4)
        )


# =============================================================================
# BLESSING OPERATORS
# =============================================================================

def create_blessing_operator(blessing_type: str) -> RitualOperator:
    """Create a blessing operator."""
    
    if blessing_type == "priestly":
        # Priestly blessing (Numbers 6:24-26)
        matrix = np.eye(4)
        matrix[1, 1] = 1.2  # Holiness boost
        matrix[2, 2] = 1.1  # Standing boost
        matrix[3, 3] = 1.05 # Allegiance toward light
        return RitualOperator(
            name="Birkat Kohanim (Priestly Blessing)",
            operator_type=OperatorType.BLESSING,
            matrix=matrix,
            requires_priest=True,
            duration_days=1
        )
    
    elif blessing_type == "covenant":
        # Covenant blessing - major amplification
        matrix = np.eye(4)
        matrix[0, 0] = 1.1
        matrix[1, 1] = 1.3
        matrix[2, 2] = 1.2
        matrix[3, 3] = 1.1
        return RitualOperator(
            name="Covenant Blessing",
            operator_type=OperatorType.BLESSING,
            matrix=matrix,
            requires_purity=True,
            duration_days=1
        )
    
    elif blessing_type == "sabbath":
        # Sabbath blessing
        matrix = np.eye(4)
        matrix[1, 1] = 1.15
        matrix[3, 3] = 1.05
        return RitualOperator(
            name="Sabbath Blessing",
            operator_type=OperatorType.BLESSING,
            matrix=matrix,
            requires_sabbath=True,
            duration_days=1
        )
    
    else:
        return RitualOperator(
            name="General Blessing",
            operator_type=OperatorType.BLESSING,
            matrix=np.eye(4)
        )


# =============================================================================
# CURSE OPERATORS
# =============================================================================

def create_curse_operator(curse_type: str) -> RitualOperator:
    """Create a curse operator (attenuation)."""
    
    if curse_type == "covenant":
        # Covenant curse - severe attenuation
        matrix = np.eye(4)
        matrix[1, 1] = 0.5   # Major holiness reduction
        matrix[2, 2] = 0.3   # Standing collapse
        matrix[3, 3] = 0.7   # Allegiance damage
        return RitualOperator(
            name="Covenant Curse",
            operator_type=OperatorType.CURSE,
            matrix=matrix,
            requires_priest=True,
            duration_days=1
        )
    
    elif curse_type == "exclusion":
        # Exclusion from community
        matrix = np.eye(4)
        matrix[2, 2] = 0.0   # Standing eliminated
        return RitualOperator(
            name="Exclusion Curse",
            operator_type=OperatorType.CURSE,
            matrix=matrix,
            requires_priest=True,
            duration_days=1
        )
    
    else:
        return RitualOperator(
            name="General Curse",
            operator_type=OperatorType.CURSE,
            matrix=np.eye(4) * 0.9
        )


# =============================================================================
# EXORCISM OPERATORS
# =============================================================================

def create_exorcism_operator() -> RitualOperator:
    """Create an exorcism operator."""
    
    # Exorcism removes darkness influence
    matrix = np.eye(4)
    matrix[0, 0] = 1.1   # Purity restoration
    matrix[3, 3] = 0.0   # Reset allegiance (then add light)
    matrix[3, :] = [0, 0, 0, 0]  # Zero out allegiance row
    matrix[3, 3] = 0.5   # Set to positive (light)
    
    return RitualOperator(
        name="Exorcism (Spirit Removal)",
        operator_type=OperatorType.EXORCISM,
        matrix=matrix,
        requires_priest=True,
        requires_purity=True,
        duration_days=1
    )


# =============================================================================
# LITURGY OPERATORS
# =============================================================================

def create_liturgy_operator(liturgy_type: str) -> RitualOperator:
    """Create a liturgy operator."""
    
    if liturgy_type == "sabbath_sacrifice":
        # Songs of Sabbath Sacrifice
        matrix = np.eye(4)
        matrix[1, 1] = 1.25  # Major holiness elevation
        matrix[3, 3] = 1.1   # Light strengthening
        return RitualOperator(
            name="Songs of Sabbath Sacrifice",
            operator_type=OperatorType.LITURGY,
            matrix=matrix,
            requires_sabbath=True,
            duration_days=1
        )
    
    elif liturgy_type == "angelic":
        # Angelic communion liturgy
        matrix = np.eye(4)
        matrix[1, 1] = 1.3   # Strong holiness boost
        matrix[0, 0] = 1.1   # Purity enhancement
        return RitualOperator(
            name="Angelic Communion Liturgy",
            operator_type=OperatorType.LITURGY,
            matrix=matrix,
            requires_purity=True,
            duration_days=1
        )
    
    else:
        return RitualOperator(
            name="Daily Liturgy",
            operator_type=OperatorType.LITURGY,
            matrix=np.eye(4)
        )


# =============================================================================
# OPERATOR CALCULUS
# =============================================================================

class OperatorCalculus:
    """
    Complete ritual operator calculus system.
    
    Manages operator application, scheduling, and composition.
    """
    
    def __init__(self):
        # Standard operators
        self.operators: Dict[str, RitualOperator] = {}
        self._register_standard_operators()
        
        # Application log
        self.application_log: List[Dict[str, Any]] = []
    
    def _register_standard_operators(self) -> None:
        """Register standard ritual operators."""
        # Purification
        self.operators["padyab"] = create_purification_operator(PurificationType.PADYAB)
        self.operators["nahn"] = create_purification_operator(PurificationType.NAHN)
        self.operators["barashnum"] = create_purification_operator(PurificationType.BARASHNUM)
        
        # Blessing
        self.operators["priestly_blessing"] = create_blessing_operator("priestly")
        self.operators["covenant_blessing"] = create_blessing_operator("covenant")
        self.operators["sabbath_blessing"] = create_blessing_operator("sabbath")
        
        # Curse
        self.operators["covenant_curse"] = create_curse_operator("covenant")
        self.operators["exclusion_curse"] = create_curse_operator("exclusion")
        
        # Exorcism
        self.operators["exorcism"] = create_exorcism_operator()
        
        # Liturgy
        self.operators["sabbath_songs"] = create_liturgy_operator("sabbath_sacrifice")
        self.operators["angelic_liturgy"] = create_liturgy_operator("angelic")
    
    def apply_operator(self, operator_name: str,
                       state: IndividualState,
                       context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Apply a named operator to a state.
        
        Returns new state and application result.
        """
        if operator_name not in self.operators:
            return {"error": f"Unknown operator: {operator_name}"}
        
        operator = self.operators[operator_name]
        context = context or {}
        
        # Check requirements
        if not operator.can_apply(
            state,
            has_priest=context.get("has_priest", False),
            is_sabbath=context.get("is_sabbath", False)
        ):
            return {"error": "Requirements not met", "operator": operator_name}
        
        # Apply
        old_state = state.to_vector()
        new_state = operator.apply(state)
        
        result = {
            "operator": operator_name,
            "type": operator.operator_type.value,
            "old_state": old_state.tolist(),
            "new_state": new_state.to_vector().tolist(),
            "success": True
        }
        
        self.application_log.append(result)
        
        return result
    
    def compose_operators(self, operator_names: List[str]) -> np.ndarray:
        """
        Compose multiple operators into single transformation.
        
        Returns the product matrix.
        """
        result = np.eye(4)
        
        for name in operator_names:
            if name in self.operators:
                result = self.operators[name].matrix @ result
        
        return result
    
    def get_operator(self, name: str) -> Optional[RitualOperator]:
        """Get an operator by name."""
        return self.operators.get(name)
    
    def list_operators(self, operator_type: OperatorType = None) -> List[str]:
        """List available operators."""
        if operator_type is None:
            return list(self.operators.keys())
        else:
            return [
                name for name, op in self.operators.items()
                if op.operator_type == operator_type
            ]


# =============================================================================
# VALIDATION
# =============================================================================

def validate_operators() -> bool:
    """Validate operators module."""
    
    # Test state vectors
    state = IndividualState(purity=0.8, holiness=0.5, standing=0.6, allegiance=0.3)
    assert state.is_valid()
    
    vec = state.to_vector()
    assert len(vec) == 4
    
    restored = IndividualState.from_vector(vec)
    assert abs(restored.purity - state.purity) < 0.001
    
    # Test purification operator
    purify = create_purification_operator(PurificationType.NAHN)
    new_state = purify.apply(state)
    assert new_state.purity >= state.purity
    
    # Test blessing operator
    bless = create_blessing_operator("priestly")
    assert bless.requires_priest
    
    # Test curse operator
    curse = create_curse_operator("exclusion")
    cursed_state = curse.apply(state)
    assert cursed_state.standing < state.standing
    
    # Test operator calculus
    calculus = OperatorCalculus()
    assert len(calculus.operators) >= 10
    
    result = calculus.apply_operator("padyab", state)
    assert result["success"]
    
    # Test composition
    composed = calculus.compose_operators(["padyab", "nahn"])
    assert composed.shape == (4, 4)
    
    return True


if __name__ == "__main__":
    print("Validating Operators Module...")
    assert validate_operators()
    print("✓ Operators Module validated")
    
    # Demo
    print("\n--- Operator Calculus Demo ---")
    calculus = OperatorCalculus()
    
    print("Available operators:")
    for name in list(calculus.operators.keys())[:6]:
        op = calculus.operators[name]
        print(f"  {name}: {op.operator_type.value}")
    
    print("\n--- State Transformation Demo ---")
    state = IndividualState(purity=0.5, holiness=0.3, standing=0.5, allegiance=0.2)
    print(f"Initial: purity={state.purity}, holiness={state.holiness}")
    
    # Apply purification
    result = calculus.apply_operator("nahn", state)
    new_vec = result["new_state"]
    print(f"After Nahn: purity={new_vec[0]:.2f}, holiness={new_vec[1]:.2f}")
    
    # Apply blessing
    new_state = IndividualState.from_vector(np.array(new_vec))
    result = calculus.apply_operator("sabbath_blessing", new_state, {"is_sabbath": True})
    if result.get("success"):
        new_vec = result["new_state"]
        print(f"After Sabbath Blessing: holiness={new_vec[1]:.2f}")
