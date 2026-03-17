"""
ATHENA OS - KEY OF SOLOMON COMPUTATIONAL FRAMEWORK
===================================================
Part V: The Operator State (Controller Interface)

OPERATOR STATE DECOMPOSITION:
    S_op = S_body × S_mind × S_intent
    
    The operator state determines authority level and whether
    high-authority operations are semantically valid.

PURIFICATION PROJECTOR:
    P_pure: S_op → S_op^pure
    
    Achieved via:
    - Confession/repentance (verbal sequences)
    - Fasting/abstinence (physical constraints)
    - Prayer/meditation (intent alignment)

AUTHORITY MODEL:
    If S_op ∉ S_op^pure, high-level operations are either:
    - Forbidden by type system, or
    - Flagged as high-risk

SOURCES:
    Key of Solomon (Clavicula Salomonis)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Set
from enum import Enum, auto
import numpy as np
from datetime import datetime, timedelta


# =============================================================================
# PURITY STATES
# =============================================================================

class PurityLevel(Enum):
    """Levels of operator purity."""
    
    PROFANE = (0, "No purification performed")
    MINIMAL = (1, "Basic washing and prayer")
    MODERATE = (2, "Fasting and confession")
    SUBSTANTIAL = (3, "Extended preparation, abstinence")
    COMPLETE = (4, "Full ritual preparation")
    EXALTED = (5, "Maximum purity state")
    
    def __init__(self, level: int, description: str):
        self.level = level
        self._description = description
    
    def __ge__(self, other):
        if isinstance(other, PurityLevel):
            return self.level >= other.level
        return NotImplemented
    
    def __le__(self, other):
        if isinstance(other, PurityLevel):
            return self.level <= other.level
        return NotImplemented


class AbstractionStatus(Enum):
    """Status of abstinence requirements."""
    
    NONE = ("no abstinence", 0)
    FOOD_PARTIAL = ("partial fast", 1)
    FOOD_COMPLETE = ("complete fast", 2)
    SEXUAL = ("celibate", 1)
    COMBINED = ("full abstinence", 3)
    
    def __init__(self, description: str, severity: int):
        self._description = description
        self.severity = severity


class IntentAlignment(Enum):
    """Alignment of operator's intent."""
    
    SCATTERED = (0, "Unfocused, multiple desires")
    WAVERING = (1, "Partially focused but unstable")
    FOCUSED = (2, "Clear primary intent")
    SINGULAR = (3, "Single-pointed concentration")
    CRYSTALLINE = (4, "Perfect alignment with purpose")
    
    def __init__(self, level: int, description: str):
        self.level = level
        self._description = description


# =============================================================================
# BODY STATE
# =============================================================================

@dataclass
class BodyState:
    """
    Physical/ritual state of the operator's body.
    
    S_body ⊆ Π X_j
    """
    
    # Hygiene
    ritually_washed: bool = False
    last_wash: Optional[datetime] = None
    
    # Abstinence
    fasting_hours: float = 0.0
    sexual_abstinence_hours: float = 0.0
    
    # Physical condition
    fatigue_level: float = 0.0  # 0-1
    illness_level: float = 0.0  # 0-1
    
    # Vestments
    ritual_garments_worn: bool = False
    lamen_worn: bool = False
    
    def update_fasting(self, hours: float):
        """Update fasting duration."""
        self.fasting_hours = hours
    
    def perform_ritual_wash(self):
        """Perform ritual washing."""
        self.ritually_washed = True
        self.last_wash = datetime.now()
    
    def don_vestments(self, lamen: bool = False):
        """Put on ritual garments."""
        self.ritual_garments_worn = True
        self.lamen_worn = lamen
    
    def body_score(self) -> float:
        """Calculate body state score (0-1)."""
        score = 0.0
        
        if self.ritually_washed:
            score += 0.2
        
        # Fasting bonus (max at 24 hours)
        score += min(self.fasting_hours / 24, 0.2)
        
        # Abstinence bonus (max at 72 hours)
        score += min(self.sexual_abstinence_hours / 72, 0.2)
        
        # Vestments
        if self.ritual_garments_worn:
            score += 0.2
        if self.lamen_worn:
            score += 0.1
        
        # Penalties
        score -= self.fatigue_level * 0.1
        score -= self.illness_level * 0.2
        
        return max(0.0, min(1.0, score))


# =============================================================================
# MIND STATE
# =============================================================================

@dataclass
class MindState:
    """
    Mental/psychological state of the operator.
    
    S_mind
    """
    
    # Prayer/meditation
    prayers_recited: List[str] = field(default_factory=list)
    meditation_minutes: float = 0.0
    
    # Confession
    confession_performed: bool = False
    sins_confessed: int = 0
    
    # Emotional state
    fear_level: float = 0.0  # 0-1
    doubt_level: float = 0.0  # 0-1
    
    # Knowledge
    divine_names_known: List[str] = field(default_factory=list)
    psalms_memorized: List[str] = field(default_factory=list)
    
    def recite_prayer(self, prayer: str):
        """Record a recited prayer."""
        self.prayers_recited.append(prayer)
    
    def perform_meditation(self, minutes: float):
        """Record meditation time."""
        self.meditation_minutes += minutes
    
    def perform_confession(self, sins: int = 0):
        """Perform confession."""
        self.confession_performed = True
        self.sins_confessed = sins
    
    def learn_name(self, name: str):
        """Learn a divine name."""
        if name not in self.divine_names_known:
            self.divine_names_known.append(name)
    
    def mind_score(self) -> float:
        """Calculate mind state score (0-1)."""
        score = 0.0
        
        # Prayer bonus (max at 7 prayers)
        score += min(len(self.prayers_recited) / 7, 0.2)
        
        # Meditation bonus (max at 60 minutes)
        score += min(self.meditation_minutes / 60, 0.2)
        
        # Confession bonus
        if self.confession_performed:
            score += 0.2
        
        # Knowledge bonus
        score += min(len(self.divine_names_known) / 10, 0.2)
        score += min(len(self.psalms_memorized) / 7, 0.1)
        
        # Penalties
        score -= self.fear_level * 0.15
        score -= self.doubt_level * 0.15
        
        return max(0.0, min(1.0, score))


# =============================================================================
# INTENT STATE
# =============================================================================

@dataclass
class IntentState:
    """
    State of the operator's intent/will.
    
    S_intent
    """
    
    # Primary goal
    primary_goal: str = ""
    goal_clarity: float = 0.5  # 0-1
    
    # Will strength
    will_strength: float = 0.5  # 0-1
    
    # Alignment
    alignment: IntentAlignment = IntentAlignment.WAVERING
    
    # Moral state
    righteous_purpose: bool = False
    
    def set_goal(self, goal: str, clarity: float = 0.5):
        """Set the primary goal."""
        self.primary_goal = goal
        self.goal_clarity = clarity
    
    def strengthen_will(self, amount: float = 0.1):
        """Strengthen the will."""
        self.will_strength = min(1.0, self.will_strength + amount)
    
    def align_intent(self, level: IntentAlignment):
        """Set intent alignment level."""
        self.alignment = level
    
    def declare_righteous(self):
        """Declare righteous purpose."""
        self.righteous_purpose = True
    
    def intent_score(self) -> float:
        """Calculate intent state score (0-1)."""
        score = 0.0
        
        # Goal clarity
        if self.primary_goal:
            score += self.goal_clarity * 0.3
        
        # Will strength
        score += self.will_strength * 0.3
        
        # Alignment bonus
        score += self.alignment.level * 0.05  # max 0.2
        
        # Righteous purpose bonus
        if self.righteous_purpose:
            score += 0.2
        
        return max(0.0, min(1.0, score))


# =============================================================================
# OPERATOR STATE
# =============================================================================

@dataclass
class OperatorState:
    """
    Complete operator state.
    
    S_op = S_body × S_mind × S_intent
    """
    
    body: BodyState = field(default_factory=BodyState)
    mind: MindState = field(default_factory=MindState)
    intent: IntentState = field(default_factory=IntentState)
    
    # Computed state
    purity_level: PurityLevel = PurityLevel.PROFANE
    authority_level: int = 0  # 0-10
    
    def update_purity(self):
        """Recalculate purity level based on component scores."""
        total_score = (self.body.body_score() + 
                       self.mind.mind_score() + 
                       self.intent.intent_score()) / 3
        
        if total_score >= 0.9:
            self.purity_level = PurityLevel.EXALTED
        elif total_score >= 0.75:
            self.purity_level = PurityLevel.COMPLETE
        elif total_score >= 0.6:
            self.purity_level = PurityLevel.SUBSTANTIAL
        elif total_score >= 0.4:
            self.purity_level = PurityLevel.MODERATE
        elif total_score >= 0.2:
            self.purity_level = PurityLevel.MINIMAL
        else:
            self.purity_level = PurityLevel.PROFANE
    
    def update_authority(self):
        """Calculate authority level based on purity and preparation."""
        # Base authority from purity
        base = self.purity_level.level * 2  # 0-10
        
        # Bonus from divine names known
        names_bonus = min(len(self.mind.divine_names_known) / 5, 2)
        
        # Penalty from negative states
        penalty = (self.mind.fear_level + self.mind.doubt_level) * 2
        
        self.authority_level = max(0, min(10, int(base + names_bonus - penalty)))
    
    def refresh(self):
        """Refresh all computed values."""
        self.update_purity()
        self.update_authority()
    
    def total_score(self) -> float:
        """Get total operator score."""
        return (self.body.body_score() + 
                self.mind.mind_score() + 
                self.intent.intent_score()) / 3
    
    def is_pure(self) -> bool:
        """Check if operator is in pure state."""
        return self.purity_level >= PurityLevel.SUBSTANTIAL
    
    def can_invoke(self, required_authority: int) -> bool:
        """Check if operator can perform invocation requiring given authority."""
        return self.authority_level >= required_authority
    
    def status(self) -> Dict[str, Any]:
        """Get current status."""
        self.refresh()
        return {
            "purity_level": self.purity_level.name,
            "authority_level": self.authority_level,
            "body_score": self.body.body_score(),
            "mind_score": self.mind.mind_score(),
            "intent_score": self.intent.intent_score(),
            "total_score": self.total_score(),
            "is_pure": self.is_pure(),
        }


# =============================================================================
# PURIFICATION PROTOCOL
# =============================================================================

@dataclass
class PurificationProtocol:
    """
    Protocol for purifying the operator state.
    
    P_pure: S_op → S_op^pure
    """
    
    # Required steps
    steps_required: List[str] = field(default_factory=list)
    steps_completed: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.steps_required:
            self.steps_required = [
                "ritual_wash",
                "don_vestments",
                "begin_fast",
                "confession",
                "preliminary_prayers",
                "meditation",
                "set_intent",
            ]
    
    def execute_step(self, step: str, operator: OperatorState) -> Tuple[bool, str]:
        """Execute a purification step."""
        if step not in self.steps_required:
            return (False, f"Unknown step: {step}")
        
        if step == "ritual_wash":
            operator.body.perform_ritual_wash()
            msg = "Ritual washing performed"
            
        elif step == "don_vestments":
            operator.body.don_vestments(lamen=True)
            msg = "Ritual vestments donned"
            
        elif step == "begin_fast":
            operator.body.update_fasting(12)  # Assume 12-hour fast
            msg = "Fast begun (12 hours)"
            
        elif step == "confession":
            operator.mind.perform_confession(sins=7)  # Traditional number
            msg = "Confession performed"
            
        elif step == "preliminary_prayers":
            for prayer in ["Pater Noster", "Ave Maria", "Credo"]:
                operator.mind.recite_prayer(prayer)
            msg = "Preliminary prayers recited"
            
        elif step == "meditation":
            operator.mind.perform_meditation(30)
            msg = "Meditation performed (30 minutes)"
            
        elif step == "set_intent":
            operator.intent.set_goal("Invoke spirits safely", clarity=0.8)
            operator.intent.align_intent(IntentAlignment.SINGULAR)
            operator.intent.declare_righteous()
            msg = "Intent set and aligned"
            
        else:
            return (False, f"Step not implemented: {step}")
        
        self.steps_completed.append(step)
        operator.refresh()
        return (True, msg)
    
    def execute_full(self, operator: OperatorState) -> Tuple[bool, List[str]]:
        """Execute full purification protocol."""
        messages = []
        
        for step in self.steps_required:
            success, msg = self.execute_step(step, operator)
            messages.append(f"{step}: {msg}")
            if not success:
                return (False, messages)
        
        return (True, messages)
    
    def completion_percentage(self) -> float:
        """Get protocol completion percentage."""
        if not self.steps_required:
            return 1.0
        return len(self.steps_completed) / len(self.steps_required)
    
    def is_complete(self) -> bool:
        """Check if protocol is complete."""
        return set(self.steps_required) <= set(self.steps_completed)


# =============================================================================
# VALIDATION
# =============================================================================

def validate_operator() -> bool:
    """Validate the operator module."""
    
    # Test BodyState
    body = BodyState()
    assert body.body_score() == 0.0
    
    body.perform_ritual_wash()
    assert body.ritually_washed
    assert body.body_score() > 0
    
    body.don_vestments(lamen=True)
    assert body.ritual_garments_worn
    
    # Test MindState
    mind = MindState()
    assert mind.mind_score() == 0.0
    
    mind.perform_confession()
    assert mind.confession_performed
    
    mind.learn_name("YHVH")
    assert "YHVH" in mind.divine_names_known
    
    # Test IntentState
    intent = IntentState()
    intent.set_goal("Test goal", 0.9)
    intent.align_intent(IntentAlignment.SINGULAR)
    intent.declare_righteous()
    assert intent.intent_score() > 0.5
    
    # Test OperatorState
    operator = OperatorState()
    assert operator.purity_level == PurityLevel.PROFANE
    
    # Apply purification
    protocol = PurificationProtocol()
    success, messages = protocol.execute_full(operator)
    assert success
    assert protocol.is_complete()
    
    # Check improved state
    operator.refresh()
    assert operator.purity_level >= PurityLevel.MODERATE
    assert operator.authority_level > 0
    assert operator.is_pure() or operator.purity_level >= PurityLevel.MODERATE
    
    return True


if __name__ == "__main__":
    print("Validating Operator Module...")
    assert validate_operator()
    print("✓ Operator module validated")
    
    # Demo
    print("\n--- Operator Purification Demo ---")
    
    operator = OperatorState()
    print(f"\nInitial state:")
    status = operator.status()
    print(f"  Purity: {status['purity_level']}")
    print(f"  Authority: {status['authority_level']}")
    print(f"  Total score: {status['total_score']:.2f}")
    
    print("\nExecuting purification protocol:")
    protocol = PurificationProtocol()
    for step in protocol.steps_required:
        success, msg = protocol.execute_step(step, operator)
        print(f"  {msg}")
    
    print(f"\nFinal state:")
    status = operator.status()
    print(f"  Purity: {status['purity_level']}")
    print(f"  Authority: {status['authority_level']}")
    print(f"  Total score: {status['total_score']:.2f}")
    print(f"  Is pure: {status['is_pure']}")
