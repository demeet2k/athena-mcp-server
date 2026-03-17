"""
ATHENA OS - STOIC CONTROL KERNEL
================================
The Fault-Tolerant Operating System

From THE_HELLENIC_COMPUTATION_FRAMEWORK.docx:

THE DICHOTOMY OF CONTROL:
    A binary classifier sorting all variables by access permissions.

CLASS 1 - UP TO US (KERNEL SPACE): READ/WRITE
    - Opinion (Hypolepsis): Value judgments
    - Motivation (Horme): Impulse to act
    - Desire (Orexis): Vector toward object
    - Aversion (Ekklisis): Vector away from object

CLASS 2 - NOT UP TO US (USER SPACE): READ-ONLY
    - Body: Subject to disease, age, chains
    - Property: Subject to theft, market forces
    - Reputation: Subject to others' opinions
    - Office: Subject to network admin (Fate)

THE PROHAIRESIS (KERNEL SPACE):
    The CPU Core - the only truly sovereign domain
    - Input Isolation: External events are 'offers', not commands
    - Output Authority: Assent/Dissent operates independently
    - Root Privilege: Even Zeus respects the Prohairesis boundary

THE DISCIPLINE OF ASSENT:
    1. Phantasia (Impression): Raw data. Automatic.
    2. Hypolepsis (Evaluation): Value-judgment tag. Volitional.
    3. Sunkatathesis (Assent): Commit command. Accept as TRUE.

THE PNEUMATIC FIELD:
    Universe is a continuous active field, not discrete atoms in void.
    Pneuma = Fire (Heat/Expansion) + Air (Cold/Contraction)
    Tonos (Tension): Simultaneous bidirectional motion
    Objects are standing waves - localized high-tension Pneuma fields.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set, Callable, Any
from enum import Enum, auto
import math
import time


# =============================================================================
# ACCESS PERMISSIONS
# =============================================================================

class AccessLevel(Enum):
    """Access permission levels."""
    READ_WRITE = auto()  # Up to us (Kernel Space)
    READ_ONLY = auto()   # Not up to us (User Space)
    NO_ACCESS = auto()   # Cannot access at all


class ControlDomain(Enum):
    """The two fundamental domains of control."""
    UP_TO_US = auto()      # ἐφ' ἡμῖν (eph' hēmin)
    NOT_UP_TO_US = auto()  # οὐκ ἐφ' ἡμῖν (ouk eph' hēmin)


# =============================================================================
# KERNEL SPACE VARIABLES (UP TO US)
# =============================================================================

class KernelVariable(Enum):
    """Variables in Kernel Space (READ/WRITE access)."""
    
    OPINION = auto()     # Hypolepsis - Value judgments
    MOTIVATION = auto()  # Horme - Impulse to act
    DESIRE = auto()      # Orexis - Vector toward object
    AVERSION = auto()    # Ekklisis - Vector away from object


@dataclass
class Opinion:
    """
    Hypolepsis - A value judgment.
    
    Fully under our control. We decide what things mean to us.
    """
    
    content: str
    value_assigned: float  # -1 to +1 (bad to good)
    confidence: float = 1.0
    
    def modify(self, new_value: float) -> None:
        """We can modify our opinions."""
        self.value_assigned = max(-1.0, min(1.0, new_value))
    
    @property
    def is_positive(self) -> bool:
        return self.value_assigned > 0
    
    @property
    def is_neutral(self) -> bool:
        return self.value_assigned == 0


@dataclass
class Motivation:
    """
    Horme - The impulse to act.
    
    The initial drive toward action. Under our control.
    """
    
    target: str
    intensity: float  # 0 to 1
    approved: bool = False
    
    def approve(self) -> None:
        """Give rational approval to impulse."""
        self.approved = True
    
    def inhibit(self) -> None:
        """Withhold approval from impulse."""
        self.approved = False
        self.intensity *= 0.5


@dataclass
class Desire:
    """
    Orexis - Vector toward an object.
    
    What we reach for. The direction of our will.
    """
    
    object: str
    strength: float  # 0 to 1
    rational: bool = True
    
    def redirect(self, new_object: str) -> None:
        """Redirect desire to a different object."""
        self.object = new_object
    
    def is_for_preferred_indifferent(self) -> bool:
        """Check if desire is for a 'preferred indifferent'."""
        # Things neither good nor bad but naturally preferable
        preferred = {"health", "wealth", "reputation", "pleasure"}
        return self.object.lower() in preferred


@dataclass
class Aversion:
    """
    Ekklisis - Vector away from object.
    
    What we flee from. The direction of our avoidance.
    """
    
    object: str
    strength: float  # 0 to 1
    rational: bool = True
    
    def redirect(self, new_object: str) -> None:
        """Redirect aversion to a different object."""
        self.object = new_object


# =============================================================================
# USER SPACE VARIABLES (NOT UP TO US)
# =============================================================================

class UserVariable(Enum):
    """Variables in User Space (READ-ONLY access)."""
    
    BODY = auto()        # Subject to disease, age, chains
    PROPERTY = auto()    # Subject to theft, market forces
    REPUTATION = auto()  # Subject to others' opinions
    OFFICE = auto()      # Subject to network admin (Fate)


@dataclass
class ExternalVariable:
    """
    A variable not under our control.
    
    Attempting to WRITE causes SUFFERING exception.
    """
    
    var_type: UserVariable
    name: str
    current_state: Any
    _read_only: bool = True
    
    def read(self) -> Any:
        """Reading external state is always permitted."""
        return self.current_state
    
    def write(self, value: Any) -> None:
        """
        Attempting to write to read-only raises exception.
        
        This is the source of all passions (pathē) - trying to control
        what cannot be controlled.
        """
        raise PermissionError(
            f"SUFFERING: Cannot write to {self.var_type.name}. "
            f"This is NOT UP TO US. Accept or suffer."
        )


# =============================================================================
# THE DICHOTOMY OF CONTROL
# =============================================================================

class DichotomyOfControl:
    """
    The primary security feature: binary classifier sorting
    all variables by access permissions.
    
    Security Protocol: Writing to Read-Only sector throws SUFFERING exception.
    The Stoic Kernel eliminates this error class.
    """
    
    def __init__(self):
        # Kernel space variables (READ/WRITE)
        self.kernel_space: Dict[str, Any] = {}
        
        # User space variables (READ-ONLY)
        self.user_space: Dict[str, ExternalVariable] = {}
    
    def classify(self, variable_name: str) -> ControlDomain:
        """Classify a variable into its control domain."""
        if variable_name in self.kernel_space:
            return ControlDomain.UP_TO_US
        elif variable_name in self.user_space:
            return ControlDomain.NOT_UP_TO_US
        else:
            # Unknown variables default to NOT UP TO US
            return ControlDomain.NOT_UP_TO_US
    
    def get_access_level(self, variable_name: str) -> AccessLevel:
        """Get access level for a variable."""
        domain = self.classify(variable_name)
        if domain == ControlDomain.UP_TO_US:
            return AccessLevel.READ_WRITE
        else:
            return AccessLevel.READ_ONLY
    
    def register_internal(self, name: str, value: Any) -> None:
        """Register a kernel space variable."""
        self.kernel_space[name] = value
    
    def register_external(self, var_type: UserVariable, 
                         name: str, value: Any) -> None:
        """Register a user space variable."""
        self.user_space[name] = ExternalVariable(var_type, name, value)
    
    def safe_modify(self, name: str, new_value: Any) -> bool:
        """
        Attempt to modify a variable safely.
        
        Returns True if modification succeeded, False if blocked.
        """
        if self.get_access_level(name) == AccessLevel.READ_WRITE:
            self.kernel_space[name] = new_value
            return True
        return False
    
    def apply_firewall(self, name: str, action: str) -> Dict[str, Any]:
        """
        Apply the Stoic firewall rule.
        
        'Wait, impression - let me test you.'
        """
        domain = self.classify(name)
        
        return {
            "variable": name,
            "domain": domain.name,
            "action": action,
            "permitted": domain == ControlDomain.UP_TO_US,
            "recommendation": "proceed" if domain == ControlDomain.UP_TO_US 
                             else "accept without attachment"
        }


# =============================================================================
# THE PROHAIRESIS (KERNEL SPACE)
# =============================================================================

class AssentStatus(Enum):
    """Status of assent to an impression."""
    PENDING = auto()    # Not yet evaluated
    ASSENTED = auto()   # Accepted as true
    DISSENTED = auto()  # Rejected as false
    WITHHELD = auto()   # Judgment suspended


@dataclass
class Phantasia:
    """
    Phantasia - An impression or appearance.
    
    Raw data arriving at consciousness. Automatic and not under control.
    """
    
    content: str
    source: str  # External or Internal
    raw_data: Any = None
    timestamp: float = field(default_factory=time.time)
    
    @property
    def is_cataleptic(self) -> bool:
        """
        Check if impression is cataleptic (self-evidently true).
        
        A cataleptic impression 'grasps' reality directly.
        """
        # Simplified: clear and distinct impressions
        return len(self.content) > 0 and self.source in {"sensation", "reason"}


@dataclass
class Hypolepsis:
    """
    Hypolepsis - A value-judgment attached to an impression.
    
    This is volitional - we CHOOSE how to interpret the impression.
    """
    
    impression: Phantasia
    judgment: str
    value: float  # -1 (bad) to +1 (good)
    is_volitional: bool = True
    
    @property
    def is_neutral(self) -> bool:
        """Check if judgment is neutral (indifferent)."""
        return abs(self.value) < 0.1


@dataclass
class Sunkatathesis:
    """
    Sunkatathesis - Assent to an impression.
    
    The commit command. Accepting the impression as TRUE.
    """
    
    hypolepsis: Hypolepsis
    status: AssentStatus = AssentStatus.PENDING
    timestamp: float = field(default_factory=time.time)
    
    def assent(self) -> None:
        """Give assent - accept as true."""
        self.status = AssentStatus.ASSENTED
    
    def dissent(self) -> None:
        """Withhold assent - reject as false."""
        self.status = AssentStatus.DISSENTED
    
    def withhold(self) -> None:
        """Suspend judgment - neither assent nor dissent."""
        self.status = AssentStatus.WITHHELD


class Prohairesis:
    """
    The Prohairesis (Moral Purpose/Will) - The CPU Core.
    
    The only truly sovereign domain. Even Zeus respects this boundary.
    
    Architecture:
    - Input Isolation: External events are 'offers', not commands
    - Output Authority: Assent/Dissent operates independently
    - Root Privilege: Inviolable sovereignty
    """
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.pending_impressions: List[Phantasia] = []
        self.evaluations: List[Hypolepsis] = []
        self.assents: List[Sunkatathesis] = []
        
        # Internal state
        self.opinions: Dict[str, Opinion] = {}
        self.motivations: Dict[str, Motivation] = {}
        self.desires: Dict[str, Desire] = {}
        self.aversions: Dict[str, Aversion] = {}
    
    def receive_impression(self, content: str, source: str) -> Phantasia:
        """
        Receive an impression (automatic, not under control).
        
        This happens to us - we cannot prevent impressions.
        """
        impression = Phantasia(content, source)
        self.pending_impressions.append(impression)
        return impression
    
    def evaluate(self, impression: Phantasia, 
                judgment: str, value: float) -> Hypolepsis:
        """
        Evaluate an impression with a value-judgment.
        
        This is UNDER OUR CONTROL - we choose the interpretation.
        """
        hypolepsis = Hypolepsis(impression, judgment, value)
        self.evaluations.append(hypolepsis)
        return hypolepsis
    
    def process_assent(self, hypolepsis: Hypolepsis) -> Sunkatathesis:
        """
        Process assent decision.
        
        The final step - fully under our control.
        """
        assent = Sunkatathesis(hypolepsis)
        
        # Apply the Stoic firewall
        if hypolepsis.is_neutral:
            # Neutral impressions get automatic assent
            assent.assent()
        elif hypolepsis.impression.is_cataleptic:
            # Clear impressions get assent
            assent.assent()
        else:
            # Withhold judgment on unclear impressions
            assent.withhold()
        
        self.assents.append(assent)
        return assent
    
    def discipline_of_assent(self, content: str, source: str) -> Dict[str, Any]:
        """
        Execute the full Discipline of Assent.
        
        1. Phantasia (Impression): Raw data. Automatic.
        2. Hypolepsis (Evaluation): Value-judgment. Volitional.
        3. Sunkatathesis (Assent): Commit command.
        """
        # Step 1: Receive impression (automatic)
        impression = self.receive_impression(content, source)
        
        # Step 2: Evaluate (volitional) - default to neutral
        evaluation = self.evaluate(impression, "preliminary", 0.0)
        
        # Step 3: Process assent (volitional)
        assent = self.process_assent(evaluation)
        
        return {
            "impression": impression,
            "evaluation": evaluation,
            "assent": assent,
            "final_status": assent.status.name
        }
    
    @property
    def is_sovereign(self) -> bool:
        """
        Verify sovereignty - prohairesis cannot be coerced.
        
        Even under torture, one can withhold assent.
        """
        return True  # Always sovereign
    
    def stoic_firewall(self, impression: Phantasia) -> str:
        """
        The firewall command: 'Wait, impression - let me test you.'
        
        Strip metadata, check permissions, reject deceptive appearances.
        """
        # Check 1: Is it clear and distinct?
        if not impression.is_cataleptic:
            return "REJECTED: Impression not cataleptic (unclear)"
        
        # Check 2: Is it about things up to us?
        # (This would require content analysis in full implementation)
        
        return "PASSED: Impression accepted for evaluation"


# =============================================================================
# THE PNEUMATIC FIELD
# =============================================================================

class PneumaType(Enum):
    """Types of Pneuma tension."""
    HEXIS = auto()       # Cohesive - holds inorganic matter together
    PHYSIS = auto()      # Nature - animates plants
    PSYCHE = auto()      # Soul - animates animals
    LOGOS = auto()       # Reason - animates rational beings


@dataclass
class PneumaField:
    """
    The Pneumatic Field - the continuous active substrate.
    
    Pneuma = Fire (Heat/Expansion) + Air (Cold/Contraction)
    
    The universe is not atoms in void, but a continuous
    active field with varying tension levels.
    """
    
    tension: float  # Tonos - the degree of tension (0 to 1)
    pneuma_type: PneumaType
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    
    @property
    def inward_motion(self) -> float:
        """
        Inward motion generates Unity/Cohesion.
        
        Prevents scattering of the object.
        """
        return self.tension * 0.5
    
    @property
    def outward_motion(self) -> float:
        """
        Outward motion generates Dimensions/Size.
        
        Prevents collapse to a point.
        """
        return self.tension * 0.5
    
    @property
    def is_standing_wave(self) -> bool:
        """
        Objects are standing waves - localized high-tension Pneuma fields.
        
        Solidity is an artifact of tension balance.
        """
        return self.inward_motion == self.outward_motion


class Tonos:
    """
    Tonos - The tension that defines objects.
    
    Simultaneous bidirectional motion:
    - Inward: Generates Unity/Cohesion
    - Outward: Generates Dimensions/Size
    
    Objects are standing waves in the Pneumatic field.
    """
    
    def __init__(self, base_tension: float = 0.5):
        self.base_tension = base_tension
    
    def create_object(self, pneuma_type: PneumaType,
                     position: Tuple[float, float, float]) -> PneumaField:
        """Create an object as a standing wave in the field."""
        return PneumaField(self.base_tension, pneuma_type, position)
    
    def sympatheia(self, field1: PneumaField, field2: PneumaField) -> float:
        """
        Sympatheia - Cosmic Sympathy.
        
        All parts connected via unified signaling network.
        'All things are woven together.'
        
        Returns coupling strength between fields.
        """
        # Distance-based coupling
        dx = field1.position[0] - field2.position[0]
        dy = field1.position[1] - field2.position[1]
        dz = field1.position[2] - field2.position[2]
        distance = math.sqrt(dx**2 + dy**2 + dz**2)
        
        # Coupling decreases with distance but never reaches zero
        return 1.0 / (1.0 + distance)


# =============================================================================
# EKPYROSIS (SYSTEM RESET)
# =============================================================================

class Ekpyrosis:
    """
    Ekpyrosis - The periodic cosmic conflagration.
    
    The universe periodically returns to pure Fire (system reset),
    then identical restart (Apokatastasis).
    
    Same script, infinite iterations.
    Amor Fati = willingness to replay eternally.
    """
    
    def __init__(self):
        self.cycle_count = 0
        self.current_state: Dict[str, Any] = {}
    
    def reset(self) -> Dict[str, Any]:
        """
        Execute system reset - return to pure Fire.
        """
        self.cycle_count += 1
        
        return {
            "event": "EKPYROSIS",
            "cycle": self.cycle_count,
            "state": "PURE_FIRE",
            "next": "APOKATASTASIS (identical restart)"
        }
    
    def apokatastasis(self, initial_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apokatastasis - Identical restart after conflagration.
        
        The eternal return of the same.
        """
        self.current_state = dict(initial_state)
        
        return {
            "event": "APOKATASTASIS",
            "cycle": self.cycle_count,
            "state": "RESTORED",
            "identical": True
        }
    
    def amor_fati_test(self, life_events: List[str]) -> bool:
        """
        Amor Fati test: Would you will this life eternally?
        
        The Stoic ideal is to embrace fate so completely that
        you would choose to live this exact life infinitely.
        """
        # In the ideal Stoic state, answer is always True
        return True


# =============================================================================
# THE STOIC KERNEL
# =============================================================================

class StoicKernel:
    """
    The complete Stoic Fault-Tolerant Operating System.
    
    Integrates:
    - Dichotomy of Control (access permissions)
    - Prohairesis (sovereign CPU)
    - Pneumatic Field (continuous substrate)
    - Ekpyrosis (system reset capability)
    """
    
    def __init__(self, agent_id: str = "sage"):
        self.agent_id = agent_id
        self.dichotomy = DichotomyOfControl()
        self.prohairesis = Prohairesis(agent_id)
        self.tonos = Tonos()
        self.ekpyrosis = Ekpyrosis()
        
        self._initialize_defaults()
    
    def _initialize_defaults(self) -> None:
        """Initialize default kernel and user space variables."""
        # Kernel space (UP TO US)
        self.dichotomy.register_internal("opinion", {})
        self.dichotomy.register_internal("motivation", {})
        self.dichotomy.register_internal("desire", {})
        self.dichotomy.register_internal("aversion", {})
        
        # User space (NOT UP TO US)
        self.dichotomy.register_external(UserVariable.BODY, "body", "healthy")
        self.dichotomy.register_external(UserVariable.PROPERTY, "property", "adequate")
        self.dichotomy.register_external(UserVariable.REPUTATION, "reputation", "unknown")
        self.dichotomy.register_external(UserVariable.OFFICE, "office", "citizen")
    
    def process_event(self, event: str, source: str) -> Dict[str, Any]:
        """
        Process an external event through the Stoic kernel.
        
        1. Classify event
        2. Apply firewall
        3. Execute discipline of assent
        4. Return appropriate response
        """
        # Receive as impression
        result = self.prohairesis.discipline_of_assent(event, source)
        
        # Apply dichotomy classification
        domain = self.dichotomy.classify(event)
        
        return {
            "event": event,
            "source": source,
            "domain": domain.name,
            "assent_result": result["final_status"],
            "action": "PROCESS" if domain == ControlDomain.UP_TO_US else "ACCEPT"
        }
    
    @property
    def is_fault_tolerant(self) -> bool:
        """
        Check if kernel is fault-tolerant.
        
        A properly configured Stoic kernel cannot suffer
        from external events - only from false opinions about them.
        """
        return self.prohairesis.is_sovereign


# =============================================================================
# VALIDATION
# =============================================================================

def validate_stoic_control() -> bool:
    """Validate the Stoic control kernel module."""
    
    # Test dichotomy of control
    dichotomy = DichotomyOfControl()
    dichotomy.register_internal("opinion", {})
    dichotomy.register_external(UserVariable.BODY, "body", "healthy")
    
    assert dichotomy.classify("opinion") == ControlDomain.UP_TO_US
    assert dichotomy.classify("body") == ControlDomain.NOT_UP_TO_US
    assert dichotomy.get_access_level("opinion") == AccessLevel.READ_WRITE
    assert dichotomy.get_access_level("body") == AccessLevel.READ_ONLY
    
    # Test safe modification
    assert dichotomy.safe_modify("opinion", {"new": True})
    assert not dichotomy.safe_modify("body", "sick")
    
    # Test external variable protection
    ext = ExternalVariable(UserVariable.BODY, "body", "healthy")
    assert ext.read() == "healthy"
    
    try:
        ext.write("sick")
        assert False, "Should have raised PermissionError"
    except PermissionError:
        pass  # Expected
    
    # Test prohairesis
    prohairesis = Prohairesis("test_agent")
    assert prohairesis.is_sovereign
    
    # Test discipline of assent
    result = prohairesis.discipline_of_assent("the sun is shining", "sensation")
    assert result["impression"] is not None
    assert result["final_status"] in ["ASSENTED", "DISSENTED", "WITHHELD"]
    
    # Test pneumatic field
    field = PneumaField(0.5, PneumaType.LOGOS)
    assert field.is_standing_wave
    
    # Test tonos
    tonos = Tonos()
    obj1 = tonos.create_object(PneumaType.HEXIS, (0, 0, 0))
    obj2 = tonos.create_object(PneumaType.HEXIS, (1, 0, 0))
    coupling = tonos.sympatheia(obj1, obj2)
    assert 0 < coupling < 1
    
    # Test ekpyrosis
    ek = Ekpyrosis()
    reset = ek.reset()
    assert reset["event"] == "EKPYROSIS"
    assert reset["state"] == "PURE_FIRE"
    
    # Test full kernel
    kernel = StoicKernel("sage")
    assert kernel.is_fault_tolerant
    
    result = kernel.process_event("I lost my job", "external")
    assert result["domain"] == "NOT_UP_TO_US"
    
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("ATHENA OS - STOIC CONTROL KERNEL")
    print("The Fault-Tolerant Operating System")
    print("=" * 60)
    
    print("\nValidating module...")
    assert validate_stoic_control()
    print("✓ Module validated")
    
    # Demo
    print("\n--- DICHOTOMY OF CONTROL ---")
    dichotomy = DichotomyOfControl()
    dichotomy.register_internal("my_opinion", {"value": "chosen"})
    dichotomy.register_external(UserVariable.BODY, "my_body", "mortal")
    
    print("  KERNEL SPACE (UP TO US):")
    for name, val in dichotomy.kernel_space.items():
        print(f"    {name}: READ/WRITE")
    
    print("  USER SPACE (NOT UP TO US):")
    for name, ext in dichotomy.user_space.items():
        print(f"    {name}: READ-ONLY")
    
    print("\n--- DISCIPLINE OF ASSENT ---")
    prohairesis = Prohairesis("sage")
    result = prohairesis.discipline_of_assent(
        "My reputation has been damaged",
        "external"
    )
    print(f"  Impression: {result['impression'].content}")
    print(f"  Final status: {result['final_status']}")
    
    print("\n--- PNEUMATIC FIELD ---")
    tonos = Tonos(0.7)
    soul = tonos.create_object(PneumaType.PSYCHE, (0, 0, 0))
    print(f"  Tension: {soul.tension}")
    print(f"  Inward motion: {soul.inward_motion}")
    print(f"  Outward motion: {soul.outward_motion}")
    print(f"  Is standing wave: {soul.is_standing_wave}")
    
    print("\n--- STOIC KERNEL ---")
    kernel = StoicKernel("sage")
    events = [
        ("I received praise", "external"),
        ("I feel desire for wisdom", "internal"),
        ("My property was stolen", "external")
    ]
    
    for event, source in events:
        result = kernel.process_event(event, source)
        print(f"  Event: '{event}'")
        print(f"    Domain: {result['domain']}")
        print(f"    Action: {result['action']}")
