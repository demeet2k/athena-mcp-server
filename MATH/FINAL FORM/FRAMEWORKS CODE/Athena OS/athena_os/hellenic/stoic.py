"""
ATHENA OS - HELLENIC: STOIC CONTROL KERNEL
==========================================
The Fault-Tolerant Operating System

THE DICHOTOMY OF CONTROL:
    X = (x_int, x_ext)
    
    x_int (Internal): Judgments, Intentions, Desires, Aversions
                      → Read/Write access
    
    x_ext (External): Body, Wealth, Reputation, Environment
                      → Read-Only access

THE HEGEMONIKON:
    The "Ruling Principle" - Central Processing Unit that:
    1. Receives impressions (φαντασίαι)
    2. Forms judgments (κρίσεις)
    3. Generates impulses (ὁρμαί)
    4. Gives or withholds assent (συγκατάθεσις)

THE PROHAIRESIS:
    The faculty of choice operating ONLY on internal variables.
    The "kernel space" that cannot be accessed by external forces.
    
    u = {u | u acts strictly on x_int}

THE VALUE FUNCTIONAL:
    J(π) = E[-Σ d(P_int(X_t), v*)]
    
    Where v* is the Ideal State (The Sage).
    Minimize distance from virtue, not maximize pleasure.

ERROR HANDLING:
    Passion = Error signal when control applied to x_ext
    Ataraxia = Zero error signal (imperturbability)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set, Callable, Any
from enum import Enum, auto
import numpy as np


# =============================================================================
# STATE SPACE DECOMPOSITION
# =============================================================================

class AccessLevel(Enum):
    """Access control levels."""
    
    READ_WRITE = "rw"   # Full control (internal)
    READ_ONLY = "ro"    # Observable only (external)


class VariableType(Enum):
    """Types of state variables."""
    
    # Internal (ἐφ' ἡμῖν - up to us)
    JUDGMENT = ("judgment", AccessLevel.READ_WRITE, "κρίσις")
    INTENTION = ("intention", AccessLevel.READ_WRITE, "ὁρμή")
    DESIRE = ("desire", AccessLevel.READ_WRITE, "ὄρεξις")
    AVERSION = ("aversion", AccessLevel.READ_WRITE, "ἔκκλισις")
    
    # External (οὐκ ἐφ' ἡμῖν - not up to us)
    BODY = ("body", AccessLevel.READ_ONLY, "σῶμα")
    PROPERTY = ("property", AccessLevel.READ_ONLY, "κτῆσις")
    REPUTATION = ("reputation", AccessLevel.READ_ONLY, "δόξα")
    OFFICE = ("office", AccessLevel.READ_ONLY, "ἀρχή")
    
    @property
    def access(self) -> AccessLevel:
        return self.value[1]
    
    @property
    def greek(self) -> str:
        return self.value[2]
    
    @property
    def is_internal(self) -> bool:
        return self.access == AccessLevel.READ_WRITE


@dataclass
class StateVariable:
    """A variable in the agent's state space."""
    
    var_type: VariableType
    value: Any = None
    
    @property
    def is_controllable(self) -> bool:
        return self.var_type.is_internal
    
    def can_write(self) -> bool:
        return self.var_type.access == AccessLevel.READ_WRITE


class StateSpace:
    """
    The complete state space X = (x_int, x_ext).
    
    Partitioned into internal (controllable) and
    external (uncontrollable) subspaces.
    """
    
    def __init__(self):
        self.variables: Dict[str, StateVariable] = {}
        
        # Initialize with standard Stoic variables
        self._initialize_default()
    
    def _initialize_default(self) -> None:
        """Initialize with standard internal/external variables."""
        # Internal variables
        self.variables["judgment"] = StateVariable(VariableType.JUDGMENT, {})
        self.variables["intention"] = StateVariable(VariableType.INTENTION, [])
        self.variables["desire"] = StateVariable(VariableType.DESIRE, set())
        self.variables["aversion"] = StateVariable(VariableType.AVERSION, set())
        
        # External variables
        self.variables["body"] = StateVariable(VariableType.BODY, {"health": 1.0})
        self.variables["property"] = StateVariable(VariableType.PROPERTY, 0.0)
        self.variables["reputation"] = StateVariable(VariableType.REPUTATION, 0.5)
        self.variables["office"] = StateVariable(VariableType.OFFICE, None)
    
    def get_internal(self) -> Dict[str, StateVariable]:
        """Get internal (controllable) variables."""
        return {k: v for k, v in self.variables.items() if v.is_controllable}
    
    def get_external(self) -> Dict[str, StateVariable]:
        """Get external (uncontrollable) variables."""
        return {k: v for k, v in self.variables.items() if not v.is_controllable}
    
    def project_internal(self) -> Dict[str, Any]:
        """Project state onto internal subspace."""
        return {k: v.value for k, v in self.get_internal().items()}
    
    def project_external(self) -> Dict[str, Any]:
        """Project state onto external subspace."""
        return {k: v.value for k, v in self.get_external().items()}
    
    def write(self, var_name: str, value: Any) -> bool:
        """
        Attempt to write to variable.
        
        Returns True if write succeeded, False if permission denied.
        """
        if var_name not in self.variables:
            return False
        
        var = self.variables[var_name]
        
        if not var.can_write():
            return False  # Permission denied
        
        var.value = value
        return True
    
    def read(self, var_name: str) -> Optional[Any]:
        """Read variable value (always allowed)."""
        if var_name in self.variables:
            return self.variables[var_name].value
        return None


# =============================================================================
# THE HEGEMONIKON
# =============================================================================

class ImpressionType(Enum):
    """Types of impressions (φαντασίαι)."""
    
    SENSORY = "sensory"         # From senses
    COGNITIVE = "cognitive"     # From thought
    IMPULSE = "impulse"         # Action-prompting


@dataclass
class Impression:
    """
    An impression (φαντασία).
    
    Raw input to the hegemonikon before judgment.
    """
    
    content: Any
    impression_type: ImpressionType
    source: str = "unknown"
    timestamp: float = 0.0
    
    # Proposed judgment (can be modified before assent)
    proposed_judgment: Optional[str] = None


class Hegemonikon:
    """
    The Hegemonikon (ἡγεμονικόν) - Ruling Principle.
    
    The central executive that:
    1. Receives impressions
    2. Forms judgments
    3. Generates impulses
    4. Grants or withholds assent
    """
    
    def __init__(self, state: StateSpace):
        self.state = state
        
        # Processing queues
        self._impression_queue: List[Impression] = []
        self._judgment_log: List[Tuple[Impression, bool, str]] = []
        
        # Assent threshold
        self.assent_threshold = 0.7
    
    def receive_impression(self, impression: Impression) -> None:
        """Receive impression for processing."""
        self._impression_queue.append(impression)
    
    def process_impression(self, impression: Impression) -> Tuple[bool, str]:
        """
        Process impression through judgment.
        
        Returns (assent_given, judgment)
        """
        # Default: suspend judgment
        judgment = "Suspended"
        assent = False
        
        # Check if impression proposes judgment about internal or external
        if impression.proposed_judgment:
            # Analyze the judgment
            involves_external = self._involves_external(impression.proposed_judgment)
            
            if involves_external:
                # Flag as potential passion
                judgment = f"Rejected: Involves externals - {impression.proposed_judgment}"
                assent = False
            else:
                # Evaluate truth of judgment
                confidence = self._evaluate_confidence(impression)
                
                if confidence >= self.assent_threshold:
                    judgment = impression.proposed_judgment
                    assent = True
                else:
                    judgment = f"Suspended (confidence={confidence:.2f})"
                    assent = False
        
        self._judgment_log.append((impression, assent, judgment))
        return assent, judgment
    
    def _involves_external(self, judgment: str) -> bool:
        """Check if judgment involves external variables."""
        external_terms = {"body", "property", "wealth", "reputation", 
                         "fame", "office", "health", "death"}
        
        judgment_lower = judgment.lower()
        return any(term in judgment_lower for term in external_terms)
    
    def _evaluate_confidence(self, impression: Impression) -> float:
        """Evaluate confidence in impression."""
        # Simplified: sensory impressions less reliable than cognitive
        base_confidence = {
            ImpressionType.SENSORY: 0.6,
            ImpressionType.COGNITIVE: 0.8,
            ImpressionType.IMPULSE: 0.5,
        }
        return base_confidence.get(impression.impression_type, 0.5)
    
    def generate_impulse(self, judgment: str) -> Optional[str]:
        """
        Generate impulse from judgment.
        
        Only generates impulse for assented judgments about internals.
        """
        if not judgment or "Rejected" in judgment or "Suspended" in judgment:
            return None
        
        # Create action directive
        return f"IMPULSE: Act according to - {judgment}"
    
    def process_all(self) -> List[Tuple[Impression, bool, str]]:
        """Process all queued impressions."""
        results = []
        
        while self._impression_queue:
            impression = self._impression_queue.pop(0)
            assent, judgment = self.process_impression(impression)
            results.append((impression, assent, judgment))
        
        return results


# =============================================================================
# THE PROHAIRESIS
# =============================================================================

class Prohairesis:
    """
    The Prohairesis (προαίρεσις) - Faculty of Choice.
    
    The kernel-space faculty that:
    - Operates ONLY on internal variables
    - Cannot be coerced by external forces
    - Is the true locus of freedom
    
    "Some things are up to us, and some things are not up to us."
    """
    
    def __init__(self, state: StateSpace, hegemonikon: Hegemonikon):
        self.state = state
        self.hegemonikon = hegemonikon
        
        # The sphere of choice
        self._choices: List[Dict] = []
    
    def can_act_on(self, var_name: str) -> bool:
        """Check if prohairesis can act on variable."""
        if var_name not in self.state.variables:
            return False
        return self.state.variables[var_name].is_controllable
    
    def choose(self, action: str, target: str, value: Any) -> bool:
        """
        Make a choice (act of will).
        
        Only succeeds if target is internal variable.
        """
        if not self.can_act_on(target):
            # Log attempt to control external
            self._choices.append({
                "action": action,
                "target": target,
                "value": value,
                "success": False,
                "reason": "Target is external (not up to us)"
            })
            return False
        
        # Execute choice
        success = self.state.write(target, value)
        
        self._choices.append({
            "action": action,
            "target": target,
            "value": value,
            "success": success,
            "reason": "OK" if success else "Write failed"
        })
        
        return success
    
    def set_judgment(self, topic: str, value: Any) -> bool:
        """Set a judgment about something."""
        judgments = self.state.read("judgment") or {}
        judgments[topic] = value
        return self.choose("set_judgment", "judgment", judgments)
    
    def add_desire(self, target: str) -> bool:
        """Add something to desires (with Stoic warning)."""
        # Stoic principle: desire only virtue
        if target not in ["virtue", "wisdom", "justice", "courage", "temperance"]:
            # Still allow but note it
            pass
        
        desires = self.state.read("desire") or set()
        desires.add(target)
        return self.choose("add_desire", "desire", desires)
    
    def add_aversion(self, target: str) -> bool:
        """Add something to aversions (with Stoic warning)."""
        # Stoic principle: avert only vice
        if target not in ["vice", "injustice", "cowardice", "intemperance"]:
            pass
        
        aversions = self.state.read("aversion") or set()
        aversions.add(target)
        return self.choose("add_aversion", "aversion", aversions)
    
    def get_choice_history(self) -> List[Dict]:
        """Return history of choices."""
        return self._choices.copy()


# =============================================================================
# PASSION AND VIRTUE
# =============================================================================

class PassionType(Enum):
    """The four primary passions (πάθη)."""
    
    # Present goods (false)
    PLEASURE = ("ἡδονή", "irrational elation at seeming good")
    
    # Future goods (false)
    DESIRE = ("ἐπιθυμία", "irrational reaching for seeming good")
    
    # Present evils (false)
    DISTRESS = ("λύπη", "irrational contraction at seeming evil")
    
    # Future evils (false)
    FEAR = ("φόβος", "irrational avoidance of seeming evil")
    
    @property
    def greek(self) -> str:
        return self.value[0]
    
    @property
    def description(self) -> str:
        return self.value[1]


class VirtueType(Enum):
    """The four cardinal virtues (ἀρεταί)."""
    
    WISDOM = ("σοφία", "knowledge of good and evil")
    JUSTICE = ("δικαιοσύνη", "giving each their due")
    COURAGE = ("ἀνδρεία", "endurance of hardship for the good")
    TEMPERANCE = ("σωφροσύνη", "moderation in desires")
    
    @property
    def greek(self) -> str:
        return self.value[0]
    
    @property
    def description(self) -> str:
        return self.value[1]


@dataclass
class PassionSignal:
    """
    Error signal indicating misapplied control.
    
    Passion = attempt to control externals
    """
    
    passion_type: PassionType
    target: str                    # What triggered it
    magnitude: float = 1.0         # Intensity
    timestamp: float = 0.0
    
    @property
    def is_error(self) -> bool:
        """All passions are errors in Stoic theory."""
        return True


class PassionDetector:
    """
    Detects passion (error) signals.
    
    Monitors for attempts to control externals.
    """
    
    def __init__(self, state: StateSpace):
        self.state = state
        self._signals: List[PassionSignal] = []
    
    def check_desire(self, target: str) -> Optional[PassionSignal]:
        """Check if desire is properly directed."""
        external = self.state.get_external()
        
        if target in external or target in ["wealth", "fame", "health", "life"]:
            signal = PassionSignal(
                passion_type=PassionType.DESIRE,
                target=target,
                magnitude=1.0
            )
            self._signals.append(signal)
            return signal
        
        return None
    
    def check_aversion(self, target: str) -> Optional[PassionSignal]:
        """Check if aversion is properly directed."""
        if target in ["death", "pain", "poverty", "obscurity"]:
            signal = PassionSignal(
                passion_type=PassionType.FEAR,
                target=target,
                magnitude=1.0
            )
            self._signals.append(signal)
            return signal
        
        return None
    
    def ataraxia_score(self) -> float:
        """
        Compute ataraxia (imperturbability) score.
        
        1.0 = perfect tranquility
        0.0 = maximum disturbance
        """
        if not self._signals:
            return 1.0
        
        # Recent signals weighted more
        recent_count = len([s for s in self._signals[-10:]])
        return max(0.0, 1.0 - recent_count / 10.0)
    
    def clear_signals(self) -> None:
        """Clear passion signals (after processing)."""
        self._signals.clear()


# =============================================================================
# STOIC CONTROLLER
# =============================================================================

class StoicController:
    """
    Complete Stoic control system.
    
    Integrates state space, hegemonikon, prohairesis,
    and passion detection into a unified controller.
    """
    
    def __init__(self):
        self.state = StateSpace()
        self.hegemonikon = Hegemonikon(self.state)
        self.prohairesis = Prohairesis(self.state, self.hegemonikon)
        self.passion_detector = PassionDetector(self.state)
        
        # Value functional target
        self._virtue_target = {v.name: 1.0 for v in VirtueType}
    
    def receive_impression(self, content: Any, 
                          imp_type: ImpressionType = ImpressionType.SENSORY,
                          proposed_judgment: str = None) -> Tuple[bool, str]:
        """Receive and process an impression."""
        impression = Impression(
            content=content,
            impression_type=imp_type,
            proposed_judgment=proposed_judgment
        )
        
        self.hegemonikon.receive_impression(impression)
        results = self.hegemonikon.process_all()
        
        if results:
            return results[0][1], results[0][2]
        return False, "No processing"
    
    def act(self, action: str, target: str, value: Any) -> Dict:
        """
        Attempt an action.
        
        Returns result including any passion signals.
        """
        result = {
            "action": action,
            "target": target,
            "success": False,
            "passion": None,
            "message": ""
        }
        
        # Check for passion (desire for external)
        if action == "desire":
            passion = self.passion_detector.check_desire(target)
            if passion:
                result["passion"] = passion
                result["message"] = f"Passion detected: desiring external '{target}'"
        
        elif action == "avoid":
            passion = self.passion_detector.check_aversion(target)
            if passion:
                result["passion"] = passion
                result["message"] = f"Passion detected: fearing external '{target}'"
        
        # Attempt action via prohairesis
        if self.prohairesis.can_act_on(target):
            result["success"] = self.prohairesis.choose(action, target, value)
            if result["success"]:
                result["message"] = f"Successfully executed: {action} on {target}"
        else:
            result["message"] = f"Cannot act on external: {target}"
        
        return result
    
    def virtue_distance(self) -> float:
        """
        Compute distance from virtue (sage state).
        
        J(π) = d(current, v*)
        """
        # Simplified: based on ataraxia and proper desires
        ataraxia = self.passion_detector.ataraxia_score()
        
        desires = self.state.read("desire") or set()
        proper_desires = {"virtue", "wisdom", "justice", "courage", "temperance"}
        desire_quality = len(desires & proper_desires) / max(len(desires), 1)
        
        return 1.0 - (0.5 * ataraxia + 0.5 * desire_quality)
    
    def status(self) -> Dict:
        """Get controller status."""
        return {
            "internal": self.state.project_internal(),
            "external": self.state.project_external(),
            "ataraxia": self.passion_detector.ataraxia_score(),
            "virtue_distance": self.virtue_distance(),
            "choices": len(self.prohairesis.get_choice_history()),
            "judgments": len(self.hegemonikon._judgment_log)
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_stoic() -> bool:
    """Validate Stoic control kernel module."""
    
    # Test AccessLevel
    assert AccessLevel.READ_WRITE.value == "rw"
    assert AccessLevel.READ_ONLY.value == "ro"
    
    # Test VariableType
    assert VariableType.JUDGMENT.is_internal
    assert not VariableType.BODY.is_internal
    
    # Test StateSpace
    state = StateSpace()
    
    internal = state.get_internal()
    external = state.get_external()
    
    assert "judgment" in internal
    assert "body" in external
    
    assert state.write("judgment", {"test": True})
    assert not state.write("body", {"health": 0.0})  # Should fail
    
    # Test Impression
    impression = Impression(
        content="This is good",
        impression_type=ImpressionType.COGNITIVE,
        proposed_judgment="External wealth is good"
    )
    
    assert impression.impression_type == ImpressionType.COGNITIVE
    
    # Test Hegemonikon
    hegemonikon = Hegemonikon(state)
    hegemonikon.receive_impression(impression)
    
    results = hegemonikon.process_all()
    assert len(results) == 1
    assent, judgment = results[0][1], results[0][2]
    
    # Should reject because involves external
    assert not assent
    assert "Rejected" in judgment
    
    # Test Prohairesis
    prohairesis = Prohairesis(state, hegemonikon)
    
    assert prohairesis.can_act_on("judgment")
    assert not prohairesis.can_act_on("body")
    
    assert prohairesis.set_judgment("virtue", "good")
    assert not prohairesis.choose("change", "body", {"health": 0.0})
    
    # Test PassionDetector
    detector = PassionDetector(state)
    
    signal = detector.check_desire("wealth")
    assert signal is not None
    assert signal.passion_type == PassionType.DESIRE
    
    # Ataraxia decreases with passions
    assert detector.ataraxia_score() < 1.0
    
    detector.clear_signals()
    assert detector.ataraxia_score() == 1.0
    
    # Test StoicController
    controller = StoicController()
    
    # Proper action
    result = controller.act("add", "desire", "wisdom")
    
    # Improper action (triggers passion)
    result = controller.act("desire", "wealth", None)
    assert result["passion"] is not None
    
    status = controller.status()
    assert "ataraxia" in status
    assert "virtue_distance" in status
    
    return True


if __name__ == "__main__":
    print("Validating Stoic Control Kernel...")
    assert validate_stoic()
    print("✓ Stoic Control Kernel validated")
    
    print("\n--- Dichotomy of Control ---")
    print("Internal (ἐφ' ἡμῖν):")
    for v in VariableType:
        if v.is_internal:
            print(f"  {v.name}: {v.greek}")
    
    print("\nExternal (οὐκ ἐφ' ἡμῖν):")
    for v in VariableType:
        if not v.is_internal:
            print(f"  {v.name}: {v.greek}")
    
    print("\n--- Controller Demo ---")
    controller = StoicController()
    
    # Try to desire wisdom (proper)
    result = controller.act("add_desire", "desire", {"wisdom"})
    print(f"Desire wisdom: success={result['success']}")
    
    # Try to desire wealth (improper)
    result = controller.act("desire", "wealth", None)
    print(f"Desire wealth: passion={result['passion'] is not None}")
    
    status = controller.status()
    print(f"\nAtaraxia score: {status['ataraxia']:.2f}")
