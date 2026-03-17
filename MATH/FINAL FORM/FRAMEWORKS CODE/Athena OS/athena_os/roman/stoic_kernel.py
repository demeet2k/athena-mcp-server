"""
ATHENA OS - ROMAN KERNEL: STOIC CONTROL MODULE
===============================================
Control-Theoretic Operating System from Stoic Philosophy

THE STOIC KERNEL:
    A control-theoretic operating system that partitions world dynamics
    into controllable vs uncontrollable variables and runs a virtue-
    optimizing policy on the controllable subset.

STATE SPACE DECOMPOSITION:
    X = (x_int, x_ext)
    
    x_int: Internal state (judgments, intentions, desires, aversions)
    x_ext: External state (body, possessions, reputation, environment)
    
    AXIOM: Only x_int is under direct control

VIRTUE AS COST FUNCTIONAL:
    J(π) = E[-Σ d(P_int(X_t), v*)]
    
    Minimize distance to ideal virtue state (the Sage)
    regardless of external fluctuations

EMOTION AS CONTROL ERROR:
    e(t) = f_value(x_ext) - f_proper(x_ext)
    
    Philosophical therapy updates valuation toward Stoic ideal

KEY ALGORITHMS:
    - Dichotomy of Control: Project goals into controllable subspace
    - Premeditatio Malorum: Monte Carlo stress-testing
    - Evening Review: Episodic reinforcement learning

SOURCES:
    - Epictetus: Enchiridion, Discourses
    - Marcus Aurelius: Meditations
    - Seneca: Letters, De Ira, De Brevitate Vitae
    - Musonius Rufus: Lectures
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Callable
from enum import Enum
import numpy as np


# =============================================================================
# STATE SPACE ENUMS
# =============================================================================

class StateType(Enum):
    """Types of state variables."""
    
    INTERNAL = "internal"     # Within our power (eph' hēmin)
    EXTERNAL = "external"     # Not within our power (ouk eph' hēmin)


class VirtueType(Enum):
    """The four cardinal virtues (Stoic tetrad)."""
    
    WISDOM = "wisdom"         # Sophia/Prudentia - knowing what is good/evil
    JUSTICE = "justice"       # Dikaiosyne/Iustitia - giving each their due
    COURAGE = "courage"       # Andreia/Fortitudo - enduring hardship
    TEMPERANCE = "temperance" # Sophrosyne/Temperantia - moderation


class EmotionType(Enum):
    """Types of passions (pathē) - cognitive errors."""
    
    # Future-oriented
    FEAR = "fear"             # Anticipation of evil
    DESIRE = "desire"         # Anticipation of good (false)
    
    # Present-oriented
    PAIN = "pain"             # Presence of perceived evil
    PLEASURE = "pleasure"     # Presence of perceived good (false)
    
    # Specific passions
    ANGER = "anger"           # Desire for revenge
    GRIEF = "grief"           # Pain at loss
    ENVY = "envy"             # Pain at others' good
    ANXIETY = "anxiety"       # Fear of uncertain future


class IndifferentType(Enum):
    """Preferred and dispreferred indifferents."""
    
    PREFERRED = "preferred"       # Health, wealth, reputation
    DISPREFERRED = "dispreferred" # Sickness, poverty, obscurity
    ABSOLUTE = "absolute"         # Truly neutral


# =============================================================================
# STATE VECTORS
# =============================================================================

@dataclass
class InternalState:
    """
    Internal state vector (x_int).
    
    Components within our power:
    - Judgments (assent to impressions)
    - Intentions (impulses to action)
    - Desires (reaching for things)
    - Aversions (withdrawal from things)
    """
    
    # Virtue alignment (0-1 for each)
    wisdom: float = 0.5
    justice: float = 0.5
    courage: float = 0.5
    temperance: float = 0.5
    
    # Control variables
    assent_quality: float = 0.5    # Quality of judgments
    intention_alignment: float = 0.5  # Alignment with virtue
    desire_control: float = 0.5    # Control over desires
    aversion_control: float = 0.5  # Control over aversions
    
    # Emotional state
    emotional_error: float = 0.0   # Distance from apatheia
    
    def to_vector(self) -> np.ndarray:
        """Convert to numpy array."""
        return np.array([
            self.wisdom, self.justice, self.courage, self.temperance,
            self.assent_quality, self.intention_alignment,
            self.desire_control, self.aversion_control,
            self.emotional_error
        ])
    
    @classmethod
    def from_vector(cls, vec: np.ndarray) -> InternalState:
        """Create from numpy array."""
        return cls(
            wisdom=float(vec[0]),
            justice=float(vec[1]),
            courage=float(vec[2]),
            temperance=float(vec[3]),
            assent_quality=float(vec[4]),
            intention_alignment=float(vec[5]),
            desire_control=float(vec[6]),
            aversion_control=float(vec[7]),
            emotional_error=float(vec[8])
        )
    
    def virtue_distance(self) -> float:
        """Distance from perfect virtue (the Sage)."""
        ideal = np.ones(4)  # Perfect virtue
        current = np.array([self.wisdom, self.justice, 
                           self.courage, self.temperance])
        return float(np.linalg.norm(ideal - current))
    
    def get_dominant_virtue(self) -> VirtueType:
        """Get the dominant virtue."""
        virtues = {
            VirtueType.WISDOM: self.wisdom,
            VirtueType.JUSTICE: self.justice,
            VirtueType.COURAGE: self.courage,
            VirtueType.TEMPERANCE: self.temperance
        }
        return max(virtues, key=virtues.get)


@dataclass
class ExternalState:
    """
    External state vector (x_ext).
    
    Components not within our power:
    - Body (health, appearance)
    - Possessions (wealth, property)
    - Reputation (fame, honor)
    - Relationships (family, friends)
    - Environment (political, natural)
    """
    
    # Physical
    health: float = 0.7
    wealth: float = 0.5
    
    # Social
    reputation: float = 0.5
    relationships: float = 0.6
    
    # Environmental
    political_stability: float = 0.5
    environmental_safety: float = 0.7
    
    def to_vector(self) -> np.ndarray:
        """Convert to numpy array."""
        return np.array([
            self.health, self.wealth, self.reputation,
            self.relationships, self.political_stability,
            self.environmental_safety
        ])
    
    def is_adverse(self) -> bool:
        """Check if external conditions are adverse."""
        return np.mean(self.to_vector()) < 0.4


@dataclass
class GlobalState:
    """Complete state X = (x_int, x_ext)."""
    
    internal: InternalState = field(default_factory=InternalState)
    external: ExternalState = field(default_factory=ExternalState)
    
    def project_internal(self) -> InternalState:
        """P_int: X → x_int"""
        return self.internal
    
    def project_external(self) -> ExternalState:
        """P_ext: X → x_ext"""
        return self.external


# =============================================================================
# STOIC VALUATION FUNCTIONS
# =============================================================================

class ValuationFunction:
    """
    Valuation function mapping external states to perceived value.
    
    f_proper: Correct Stoic valuation (only vice is evil)
    f_current: Agent's current (possibly mistaken) valuation
    """
    
    @staticmethod
    def proper_valuation(external: ExternalState) -> float:
        """
        Correct Stoic valuation.
        
        External things are indifferent - neither truly good nor evil.
        """
        return 0.0  # All externals are indifferent
    
    @staticmethod
    def false_valuation(external: ExternalState) -> float:
        """
        False valuation (non-Stoic).
        
        Treats externals as truly good or evil.
        """
        # Mistakenly values externals
        vec = external.to_vector()
        return float(np.mean(vec) - 0.5)  # Deviation from neutral
    
    @staticmethod
    def calculate_emotional_error(external: ExternalState,
                                   current_valuation: Callable) -> float:
        """
        Calculate emotional error.
        
        e(t) = f_current(x_ext) - f_proper(x_ext)
        """
        proper = ValuationFunction.proper_valuation(external)
        current = current_valuation(external)
        return abs(current - proper)


# =============================================================================
# DICHOTOMY OF CONTROL
# =============================================================================

@dataclass
class Goal:
    """A goal or desire."""
    
    name: str
    description: str
    state_type: StateType
    value: float = 1.0
    
    def is_controllable(self) -> bool:
        """Check if goal is within our control."""
        return self.state_type == StateType.INTERNAL


class DichotomyOfControl:
    """
    The Dichotomy of Control algorithm (Epictetus).
    
    Project all goals into the controllable subspace.
    """
    
    @staticmethod
    def classify_goal(goal: Goal) -> StateType:
        """Classify a goal as internal or external."""
        # Internal goals (within our power)
        internal_keywords = [
            "virtue", "judgment", "intention", "desire", "aversion",
            "opinion", "impulse", "response", "attitude", "character"
        ]
        
        desc_lower = goal.description.lower()
        
        for keyword in internal_keywords:
            if keyword in desc_lower:
                return StateType.INTERNAL
        
        return StateType.EXTERNAL
    
    @staticmethod
    def transform_goal(goal: Goal) -> Goal:
        """
        Transform external goal to internal equivalent.
        
        "I want to win" → "I want to play excellently"
        "I want wealth" → "I want to use whatever comes virtuously"
        """
        if goal.is_controllable():
            return goal
        
        # Transform to internal
        new_name = f"virtuous_response_to_{goal.name}"
        new_desc = f"To respond virtuously to whatever happens with {goal.name}"
        
        return Goal(
            name=new_name,
            description=new_desc,
            state_type=StateType.INTERNAL,
            value=goal.value
        )
    
    @staticmethod
    def apply_dichotomy(goals: List[Goal]) -> List[Goal]:
        """
        Apply dichotomy to a list of goals.
        
        Returns transformed goals in controllable subspace.
        """
        return [DichotomyOfControl.transform_goal(g) for g in goals]


# =============================================================================
# STOIC THERAPEUTIC ALGORITHMS
# =============================================================================

class PremeditatiaMalorum:
    """
    Premeditatio Malorum - Pre-meditation of evils.
    
    Monte Carlo stress-testing: enumerate possible adverse events
    and rehearse virtuous responses.
    """
    
    def __init__(self):
        self.adverse_events = self._generate_events()
        self.contingency_policies: Dict[str, str] = {}
    
    def _generate_events(self) -> List[Dict[str, Any]]:
        """Generate list of possible adverse events."""
        return [
            {"name": "loss_of_wealth", "description": "Financial ruin", "severity": 0.7},
            {"name": "loss_of_health", "description": "Serious illness", "severity": 0.8},
            {"name": "loss_of_reputation", "description": "Public disgrace", "severity": 0.6},
            {"name": "death_of_loved_one", "description": "Bereavement", "severity": 0.9},
            {"name": "exile", "description": "Banishment from home", "severity": 0.7},
            {"name": "physical_pain", "description": "Torture or injury", "severity": 0.8},
            {"name": "betrayal", "description": "Betrayal by friend", "severity": 0.6},
            {"name": "own_death", "description": "Impending death", "severity": 1.0},
        ]
    
    def rehearse_event(self, event_name: str) -> Dict[str, Any]:
        """
        Rehearse virtuous response to an event.
        
        Returns the rehearsal result.
        """
        event = next((e for e in self.adverse_events if e["name"] == event_name), None)
        
        if not event:
            return {"error": "Event not found"}
        
        # Generate Stoic response
        response = self._generate_stoic_response(event)
        
        # Store as contingency policy
        self.contingency_policies[event_name] = response["policy"]
        
        return {
            "event": event,
            "response": response,
            "rehearsal_complete": True
        }
    
    def _generate_stoic_response(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Stoic response to event."""
        return {
            "immediate": "This is not evil, only an indifferent",
            "reframe": f"The {event['name']} affects only externals, not my character",
            "action": "I will respond with virtue (wisdom, justice, courage, temperance)",
            "policy": f"When {event['description']}: maintain rational composure, act virtuously"
        }
    
    def run_full_exercise(self) -> Dict[str, Any]:
        """Run premeditatio for all events."""
        results = []
        for event in self.adverse_events:
            result = self.rehearse_event(event["name"])
            results.append(result)
        
        return {
            "events_rehearsed": len(results),
            "contingencies_prepared": len(self.contingency_policies),
            "readiness": "high"
        }


class EveningReview:
    """
    Evening Review - Daily self-examination.
    
    Episodic reinforcement learning: review day's actions,
    identify deviations from virtue, update policy.
    """
    
    def __init__(self):
        self.review_log: List[Dict[str, Any]] = []
    
    def review_day(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Review a day's events and actions.
        
        Seneca's three questions:
        1. What bad habit have I cured today?
        2. What fault have I resisted?
        3. In what way am I better?
        """
        analysis = {
            "events": [],
            "deviations": [],
            "improvements": [],
            "policy_updates": []
        }
        
        for event in events:
            event_analysis = self._analyze_event(event)
            analysis["events"].append(event_analysis)
            
            if event_analysis.get("deviation"):
                analysis["deviations"].append(event_analysis["deviation"])
            
            if event_analysis.get("improvement"):
                analysis["improvements"].append(event_analysis["improvement"])
        
        # Generate policy updates
        for deviation in analysis["deviations"]:
            update = f"In future similar situations, apply more {deviation['virtue_needed']}"
            analysis["policy_updates"].append(update)
        
        # Log review
        self.review_log.append({
            "events_count": len(events),
            "deviations_count": len(analysis["deviations"]),
            "improvements_count": len(analysis["improvements"])
        })
        
        return analysis
    
    def _analyze_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single event for virtue alignment."""
        result = {"event": event}
        
        # Check for emotional error
        if event.get("emotional_reaction"):
            reaction = event["emotional_reaction"]
            
            if reaction.get("intensity", 0) > 0.5:
                result["deviation"] = {
                    "type": "emotional_excess",
                    "description": f"Excessive {reaction.get('type', 'emotion')}",
                    "virtue_needed": "temperance"
                }
        
        # Check for improvement
        if event.get("virtuous_action"):
            result["improvement"] = {
                "action": event["virtuous_action"],
                "virtue_demonstrated": event.get("virtue", "general")
            }
        
        return result


# =============================================================================
# STOIC KERNEL
# =============================================================================

class StoicKernel:
    """
    The Stoic Control-Theoretic Kernel.
    
    Runs a virtue-optimizing policy on controllable state variables.
    """
    
    # The Sage - perfect virtue state
    SAGE_STATE = InternalState(
        wisdom=1.0, justice=1.0, courage=1.0, temperance=1.0,
        assent_quality=1.0, intention_alignment=1.0,
        desire_control=1.0, aversion_control=1.0,
        emotional_error=0.0
    )
    
    def __init__(self):
        self.state = GlobalState()
        self.valuation = ValuationFunction()
        self.dichotomy = DichotomyOfControl()
        self.premeditatio = PremeditatiaMalorum()
        self.evening_review = EveningReview()
        
        # Learning rate for valuation updates
        self.learning_rate = 0.1
        
        # Policy log
        self.policy_log: List[Dict[str, Any]] = []
    
    def calculate_cost(self) -> float:
        """
        Calculate cost J(π) = distance from sage.
        
        Lower is better.
        """
        return self.state.internal.virtue_distance()
    
    def update_valuation(self) -> Dict[str, Any]:
        """
        Update valuation function toward proper Stoic valuation.
        
        Gradient step: f_value ← f_value - η∇[f_value - f_proper]
        """
        # Calculate current error
        error = ValuationFunction.calculate_emotional_error(
            self.state.external,
            ValuationFunction.false_valuation
        )
        
        # Update internal state
        self.state.internal.emotional_error *= (1 - self.learning_rate)
        
        return {
            "previous_error": error,
            "new_error": self.state.internal.emotional_error,
            "learning_rate": self.learning_rate
        }
    
    def process_impression(self, impression: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an impression (phantasia).
        
        Apply Epictetus's method:
        1. Pause before assent
        2. Test: Is this within my control?
        3. If external, withhold assent to value judgment
        """
        # Classify
        is_external = impression.get("type") == "external"
        
        if is_external:
            # Withhold value assent
            return {
                "impression": impression,
                "assent": "withheld",
                "reason": "External, indifferent",
                "response": "I see this impression. It is not my concern."
            }
        else:
            # Internal - evaluate for virtue alignment
            return {
                "impression": impression,
                "assent": "evaluated",
                "alignment": "pending virtue check"
            }
    
    def apply_virtue_step(self, situation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply one step of virtue optimization.
        
        Updates internal state toward sage ideal.
        """
        # Current state
        current = self.state.internal.to_vector()
        ideal = self.SAGE_STATE.to_vector()
        
        # Gradient toward ideal
        gradient = ideal - current
        
        # Step
        new_vec = current + self.learning_rate * gradient
        
        # Clamp values
        new_vec = np.clip(new_vec, 0, 1)
        new_vec[8] = max(0, new_vec[8])  # emotional_error can't be negative
        
        # Update
        self.state.internal = InternalState.from_vector(new_vec)
        
        return {
            "situation": situation,
            "previous_cost": np.linalg.norm(ideal - current),
            "new_cost": np.linalg.norm(ideal - new_vec),
            "improvement": True
        }
    
    def run_daily_cycle(self, day_events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Run a complete daily cycle.
        
        Morning: Premeditatio
        Throughout: Process impressions
        Evening: Review
        """
        # Morning meditation
        morning = self.premeditatio.rehearse_event("own_death")
        
        # Process day's events
        processed = []
        for event in day_events:
            result = self.process_impression(event)
            processed.append(result)
            self.apply_virtue_step(event)
        
        # Evening review
        evening = self.evening_review.review_day(day_events)
        
        # Update valuation
        val_update = self.update_valuation()
        
        return {
            "morning": morning,
            "events_processed": len(processed),
            "evening_review": evening,
            "valuation_update": val_update,
            "final_cost": self.calculate_cost()
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get kernel status."""
        return {
            "internal_state": {
                "wisdom": self.state.internal.wisdom,
                "justice": self.state.internal.justice,
                "courage": self.state.internal.courage,
                "temperance": self.state.internal.temperance,
                "emotional_error": self.state.internal.emotional_error
            },
            "cost": self.calculate_cost(),
            "dominant_virtue": self.state.internal.get_dominant_virtue().value,
            "contingencies_prepared": len(self.premeditatio.contingency_policies)
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_stoic_kernel() -> bool:
    """Validate stoic kernel module."""
    
    # Test state vectors
    internal = InternalState()
    assert internal.virtue_distance() > 0
    
    vec = internal.to_vector()
    restored = InternalState.from_vector(vec)
    assert abs(restored.wisdom - internal.wisdom) < 0.001
    
    # Test global state
    state = GlobalState()
    assert state.project_internal() == state.internal
    
    # Test dichotomy of control
    goal_ext = Goal("wealth", "I want to be rich", StateType.EXTERNAL)
    assert not goal_ext.is_controllable()
    
    transformed = DichotomyOfControl.transform_goal(goal_ext)
    assert transformed.is_controllable()
    
    # Test premeditatio
    premed = PremeditatiaMalorum()
    result = premed.rehearse_event("loss_of_wealth")
    assert result["rehearsal_complete"]
    
    # Test evening review
    review = EveningReview()
    events = [{"action": "spoke harshly", "emotional_reaction": {"type": "anger", "intensity": 0.7}}]
    result = review.review_day(events)
    assert "deviations" in result
    
    # Test kernel
    kernel = StoicKernel()
    assert kernel.calculate_cost() > 0
    
    result = kernel.apply_virtue_step({"situation": "test"})
    assert result["improvement"]
    
    status = kernel.get_status()
    assert "cost" in status
    
    return True


if __name__ == "__main__":
    print("Validating Stoic Kernel Module...")
    assert validate_stoic_kernel()
    print("✓ Stoic Kernel Module validated")
    
    # Demo
    print("\n--- Stoic Kernel Demo ---")
    kernel = StoicKernel()
    
    print("\nInitial Status:")
    status = kernel.get_status()
    print(f"  Virtue Distance from Sage: {status['cost']:.3f}")
    print(f"  Dominant Virtue: {status['dominant_virtue']}")
    
    # Process some impressions
    impressions = [
        {"type": "external", "content": "Lost money in market"},
        {"type": "internal", "content": "I must respond calmly"},
        {"type": "external", "content": "Someone insulted me"}
    ]
    
    print("\nProcessing impressions:")
    for imp in impressions:
        result = kernel.process_impression(imp)
        print(f"  {imp['content']}: {result['assent']}")
    
    # Run virtue steps
    for _ in range(10):
        kernel.apply_virtue_step({})
    
    print("\nAfter 10 virtue steps:")
    status = kernel.get_status()
    print(f"  Virtue Distance: {status['cost']:.3f}")
    print(f"  Wisdom: {status['internal_state']['wisdom']:.3f}")
