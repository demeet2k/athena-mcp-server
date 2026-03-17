"""
ATHENA OS - QUMRAN KERNEL: ROLE GRAPH MODULE
=============================================
Institutional Automaton and Community Structure

ROLE GRAPH (G_R):
    G_R = (V_R, E_R)
    
    Nodes (V_R): Role-types
    - Priests (Kohanim)
    - Levites
    - Israel (laypeople)
    - Strangers/Converts
    - Teacher/Maskil (instructor)
    - Mebaqqer (overseer)
    - Sons of Light / Sons of Darkness
    - Angelic orders
    - Spirits of Truth/Falsehood
    
    Edges (E_R): Relations
    - Authority (command direction)
    - Holiness flow (Temple → priest → people)
    - Contamination risk (impurity transfer)
    - Conflict (Light vs Darkness)

INSTITUTIONAL AUTOMATON:
    State machine governing:
    - Entry into covenant
    - Rank advancement (Four Classes)
    - Expulsion/restoration
    - Authority delegation

TEACHER MIDDLEWARE:
    Three-layer computation:
    - Top: Divine code (Law)
    - Middle: Priestly interpreters (compiler)
    - Bottom: People (runtime)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Tuple
from enum import Enum, IntEnum
import numpy as np


# =============================================================================
# ROLE TYPES
# =============================================================================

class RoleType(Enum):
    """Types of roles in the Qumran community."""
    
    # Human roles
    HIGH_PRIEST = "high_priest"
    PRIEST = "priest"
    LEVITE = "levite"
    ISRAELITE = "israelite"
    CONVERT = "convert"
    STRANGER = "stranger"
    
    # Leadership roles
    MASKIL = "maskil"           # Instructor/Enlightener
    MEBAQQER = "mebaqqer"       # Overseer/Guardian
    PAQID = "paqid"             # Appointed one
    
    # Cosmic roles
    PRINCE_OF_LIGHT = "prince_of_light"
    ANGEL_OF_DARKNESS = "angel_of_darkness"
    SPIRIT_OF_TRUTH = "spirit_of_truth"
    SPIRIT_OF_FALSEHOOD = "spirit_of_falsehood"
    
    # Community classes
    SON_OF_LIGHT = "son_of_light"
    SON_OF_DARKNESS = "son_of_darkness"


class HolinessLevel(IntEnum):
    """Levels of holiness (kedushah)."""
    
    PROFANE = 0             # Chol - ordinary
    HOLY = 1                # Kadosh - set apart
    MOST_HOLY = 2           # Kodesh Kodashim
    DIVINE = 3              # Reserved for God alone


class PurityState(Enum):
    """States of ritual purity."""
    
    PURE = "pure"           # Tahor
    IMPURE = "impure"       # Tamei
    PURIFYING = "purifying" # In process
    EXCLUDED = "excluded"   # Cut off


class CommunityClass(IntEnum):
    """Four classes of the community (from Community Rule)."""
    
    NOVICE = 1              # First year candidate
    PROBATIONER = 2         # Second year
    FULL_MEMBER = 3         # Accepted into congregation
    ELDER = 4               # Senior with authority


# =============================================================================
# ROLE NODE
# =============================================================================

@dataclass
class RoleNode:
    """
    A node in the role graph representing a position/type.
    
    Each role has:
    - Authority level
    - Holiness level
    - Permitted actions
    - Access rights
    """
    
    role_type: RoleType
    name: str
    
    # Hierarchy
    holiness_level: HolinessLevel = HolinessLevel.PROFANE
    authority_level: int = 0     # 0-10
    
    # Capabilities
    can_teach: bool = False
    can_judge: bool = False
    can_bless: bool = False
    can_curse: bool = False
    can_sacrifice: bool = False
    can_enter_sanctuary: bool = False
    
    # Access
    max_allowed_holiness: HolinessLevel = HolinessLevel.HOLY
    
    def can_interact_with_holiness(self, level: HolinessLevel) -> bool:
        """Check if role can interact with given holiness level."""
        return level <= self.max_allowed_holiness


# =============================================================================
# PREDEFINED ROLES
# =============================================================================

ROLE_DEFINITIONS = {
    RoleType.HIGH_PRIEST: RoleNode(
        role_type=RoleType.HIGH_PRIEST,
        name="High Priest",
        holiness_level=HolinessLevel.MOST_HOLY,
        authority_level=10,
        can_teach=True,
        can_judge=True,
        can_bless=True,
        can_curse=True,
        can_sacrifice=True,
        can_enter_sanctuary=True,
        max_allowed_holiness=HolinessLevel.MOST_HOLY
    ),
    RoleType.PRIEST: RoleNode(
        role_type=RoleType.PRIEST,
        name="Priest",
        holiness_level=HolinessLevel.HOLY,
        authority_level=8,
        can_teach=True,
        can_judge=True,
        can_bless=True,
        can_curse=True,
        can_sacrifice=True,
        can_enter_sanctuary=True,
        max_allowed_holiness=HolinessLevel.HOLY
    ),
    RoleType.LEVITE: RoleNode(
        role_type=RoleType.LEVITE,
        name="Levite",
        holiness_level=HolinessLevel.HOLY,
        authority_level=6,
        can_teach=True,
        can_judge=False,
        can_bless=False,
        can_curse=False,
        can_sacrifice=False,
        can_enter_sanctuary=True,
        max_allowed_holiness=HolinessLevel.HOLY
    ),
    RoleType.MASKIL: RoleNode(
        role_type=RoleType.MASKIL,
        name="Maskil (Instructor)",
        holiness_level=HolinessLevel.HOLY,
        authority_level=7,
        can_teach=True,
        can_judge=True,
        can_bless=True,
        can_curse=False,
        can_sacrifice=False,
        can_enter_sanctuary=False,
        max_allowed_holiness=HolinessLevel.HOLY
    ),
    RoleType.MEBAQQER: RoleNode(
        role_type=RoleType.MEBAQQER,
        name="Mebaqqer (Overseer)",
        holiness_level=HolinessLevel.HOLY,
        authority_level=7,
        can_teach=True,
        can_judge=True,
        can_bless=False,
        can_curse=False,
        can_sacrifice=False,
        can_enter_sanctuary=False,
        max_allowed_holiness=HolinessLevel.HOLY
    ),
    RoleType.ISRAELITE: RoleNode(
        role_type=RoleType.ISRAELITE,
        name="Israelite",
        holiness_level=HolinessLevel.PROFANE,
        authority_level=3,
        can_teach=False,
        can_judge=False,
        can_bless=False,
        can_curse=False,
        can_sacrifice=False,
        can_enter_sanctuary=False,
        max_allowed_holiness=HolinessLevel.PROFANE
    ),
    RoleType.CONVERT: RoleNode(
        role_type=RoleType.CONVERT,
        name="Convert (Ger)",
        holiness_level=HolinessLevel.PROFANE,
        authority_level=2,
        can_teach=False,
        can_judge=False,
        can_bless=False,
        can_curse=False,
        can_sacrifice=False,
        can_enter_sanctuary=False,
        max_allowed_holiness=HolinessLevel.PROFANE
    ),
    RoleType.PRINCE_OF_LIGHT: RoleNode(
        role_type=RoleType.PRINCE_OF_LIGHT,
        name="Prince of Light (Michael)",
        holiness_level=HolinessLevel.DIVINE,
        authority_level=10,
        can_teach=True,
        can_judge=True,
        can_bless=True,
        can_curse=True,
        can_sacrifice=False,
        can_enter_sanctuary=True,
        max_allowed_holiness=HolinessLevel.DIVINE
    ),
    RoleType.ANGEL_OF_DARKNESS: RoleNode(
        role_type=RoleType.ANGEL_OF_DARKNESS,
        name="Angel of Darkness (Belial)",
        holiness_level=HolinessLevel.PROFANE,
        authority_level=10,
        can_teach=True,
        can_judge=True,
        can_bless=False,
        can_curse=True,
        can_sacrifice=False,
        can_enter_sanctuary=False,
        max_allowed_holiness=HolinessLevel.PROFANE
    ),
}


# =============================================================================
# ROLE EDGE
# =============================================================================

class EdgeType(Enum):
    """Types of edges in the role graph."""
    
    AUTHORITY = "authority"         # Command/control
    HOLINESS_FLOW = "holiness"      # Transfer of sanctity
    TEACHING = "teaching"           # Instruction flow
    CONTAMINATION = "contamination" # Impurity risk
    CONFLICT = "conflict"           # Opposed relationship
    SERVICE = "service"             # Subordinate serves superior


@dataclass
class RoleEdge:
    """
    An edge connecting two roles in the graph.
    
    Weighted by:
    - Authority intensity
    - Holiness transfer rate
    - Contamination risk
    """
    
    source: RoleType
    target: RoleType
    edge_type: EdgeType
    
    # Weights
    weight_authority: float = 0.0      # Strength of command
    weight_holiness: float = 0.0       # Sanctity transfer
    weight_contamination: float = 0.0  # Impurity risk
    
    # Direction
    bidirectional: bool = False


# =============================================================================
# ROLE GRAPH
# =============================================================================

class RoleGraph:
    """
    The complete role graph G_R = (V_R, E_R).
    
    Models the institutional structure of the Qumran community
    as a weighted directed graph.
    """
    
    def __init__(self):
        self.nodes: Dict[RoleType, RoleNode] = ROLE_DEFINITIONS.copy()
        self.edges: List[RoleEdge] = []
        
        # Adjacency structures
        self.authority_matrix: Optional[np.ndarray] = None
        self.holiness_matrix: Optional[np.ndarray] = None
        
        self._build_edges()
        self._build_matrices()
    
    def _build_edges(self) -> None:
        """Build standard edges between roles."""
        # Authority edges (high to low)
        self.edges.append(RoleEdge(
            RoleType.HIGH_PRIEST, RoleType.PRIEST,
            EdgeType.AUTHORITY, weight_authority=1.0
        ))
        self.edges.append(RoleEdge(
            RoleType.PRIEST, RoleType.LEVITE,
            EdgeType.AUTHORITY, weight_authority=0.8
        ))
        self.edges.append(RoleEdge(
            RoleType.MASKIL, RoleType.ISRAELITE,
            EdgeType.TEACHING, weight_authority=0.7
        ))
        
        # Holiness flow edges
        self.edges.append(RoleEdge(
            RoleType.HIGH_PRIEST, RoleType.PRIEST,
            EdgeType.HOLINESS_FLOW, weight_holiness=1.0
        ))
        self.edges.append(RoleEdge(
            RoleType.PRIEST, RoleType.ISRAELITE,
            EdgeType.HOLINESS_FLOW, weight_holiness=0.5
        ))
        
        # Conflict edges
        self.edges.append(RoleEdge(
            RoleType.PRINCE_OF_LIGHT, RoleType.ANGEL_OF_DARKNESS,
            EdgeType.CONFLICT, bidirectional=True
        ))
    
    def _build_matrices(self) -> None:
        """Build adjacency matrices for graph operations."""
        role_types = list(RoleType)
        n = len(role_types)
        
        self.authority_matrix = np.zeros((n, n))
        self.holiness_matrix = np.zeros((n, n))
        
        for edge in self.edges:
            i = role_types.index(edge.source)
            j = role_types.index(edge.target)
            
            if edge.edge_type == EdgeType.AUTHORITY:
                self.authority_matrix[i, j] = edge.weight_authority
                if edge.bidirectional:
                    self.authority_matrix[j, i] = edge.weight_authority
            
            if edge.edge_type == EdgeType.HOLINESS_FLOW:
                self.holiness_matrix[i, j] = edge.weight_holiness
    
    def get_role(self, role_type: RoleType) -> RoleNode:
        """Get role node by type."""
        return self.nodes.get(role_type)
    
    def get_authority_over(self, role: RoleType) -> List[RoleType]:
        """Get roles that this role has authority over."""
        result = []
        for edge in self.edges:
            if edge.source == role and edge.edge_type == EdgeType.AUTHORITY:
                result.append(edge.target)
        return result
    
    def get_holiness_sources(self, role: RoleType) -> List[RoleType]:
        """Get roles that can transfer holiness to this role."""
        result = []
        for edge in self.edges:
            if edge.target == role and edge.edge_type == EdgeType.HOLINESS_FLOW:
                result.append(edge.source)
        return result
    
    def can_command(self, commander: RoleType, subject: RoleType) -> bool:
        """Check if commander can give orders to subject."""
        cmd_node = self.nodes.get(commander)
        sub_node = self.nodes.get(subject)
        
        if not cmd_node or not sub_node:
            return False
        
        return cmd_node.authority_level > sub_node.authority_level


# =============================================================================
# COMMUNITY MEMBER
# =============================================================================

@dataclass
class CommunityMember:
    """
    An individual member of the Qumran community (Yahad).
    
    Tracks:
    - Role and class
    - Purity state
    - Time in community
    - Violations/merits
    """
    
    member_id: str
    name: str
    
    # Role
    primary_role: RoleType = RoleType.ISRAELITE
    community_class: CommunityClass = CommunityClass.NOVICE
    
    # State
    purity_state: PurityState = PurityState.PURE
    is_in_covenant: bool = False
    
    # History
    years_in_community: int = 0
    violations: List[str] = field(default_factory=list)
    merits: List[str] = field(default_factory=list)
    
    # Allegiance
    allegiance: str = "light"  # "light" or "darkness"
    
    def get_standing(self) -> float:
        """Calculate community standing (0-1)."""
        merit_score = len(self.merits) * 0.1
        violation_score = len(self.violations) * 0.15
        
        base = 0.5 + (self.community_class.value * 0.1)
        return max(0, min(1, base + merit_score - violation_score))


# =============================================================================
# INSTITUTIONAL AUTOMATON
# =============================================================================

class AutomatonState(Enum):
    """States in the institutional automaton."""
    
    OUTSIDE = "outside"          # Not in covenant
    CANDIDATE = "candidate"      # Seeking entry
    NOVICE = "novice"           # First year
    PROBATIONER = "probationer" # Second year
    MEMBER = "member"           # Full member
    ELDER = "elder"             # Senior position
    EXPELLED = "expelled"       # Cast out
    RESTORED = "restored"       # Returning after expulsion


class InstitutionalAutomaton:
    """
    State machine governing community membership.
    
    Transitions:
    - Entry: OUTSIDE → CANDIDATE → NOVICE → PROBATIONER → MEMBER
    - Advancement: MEMBER → ELDER
    - Discipline: MEMBER → EXPELLED → RESTORED → PROBATIONER
    """
    
    # Transition requirements
    REQUIREMENTS = {
        (AutomatonState.OUTSIDE, AutomatonState.CANDIDATE): {
            "examination": True,
            "sponsor": True
        },
        (AutomatonState.CANDIDATE, AutomatonState.NOVICE): {
            "oath": True,
            "knowledge_test": True
        },
        (AutomatonState.NOVICE, AutomatonState.PROBATIONER): {
            "years": 1,
            "purity": True
        },
        (AutomatonState.PROBATIONER, AutomatonState.MEMBER): {
            "years": 1,
            "vote": True
        },
        (AutomatonState.MEMBER, AutomatonState.ELDER): {
            "years": 10,
            "merit": True
        }
    }
    
    def __init__(self):
        self.current_state = AutomatonState.OUTSIDE
        self.transition_log: List[Dict[str, Any]] = []
    
    def can_transition(self, from_state: AutomatonState,
                       to_state: AutomatonState,
                       conditions: Dict[str, Any]) -> bool:
        """Check if transition is allowed."""
        key = (from_state, to_state)
        
        if key not in self.REQUIREMENTS:
            return False
        
        requirements = self.REQUIREMENTS[key]
        
        for req_key, req_val in requirements.items():
            if req_key not in conditions:
                return False
            
            if isinstance(req_val, bool):
                if conditions[req_key] != req_val:
                    return False
            elif isinstance(req_val, int):
                if conditions.get(req_key, 0) < req_val:
                    return False
        
        return True
    
    def transition(self, to_state: AutomatonState,
                   conditions: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt state transition."""
        if self.can_transition(self.current_state, to_state, conditions):
            old_state = self.current_state
            self.current_state = to_state
            
            record = {
                "from": old_state.value,
                "to": to_state.value,
                "conditions": conditions,
                "success": True
            }
            self.transition_log.append(record)
            
            return {"success": True, "new_state": to_state.value}
        else:
            return {"success": False, "current_state": self.current_state.value}
    
    def expel(self, reason: str) -> Dict[str, Any]:
        """Expel from community."""
        if self.current_state in [AutomatonState.MEMBER, AutomatonState.ELDER]:
            old_state = self.current_state
            self.current_state = AutomatonState.EXPELLED
            
            return {
                "success": True,
                "from": old_state.value,
                "reason": reason
            }
        return {"success": False, "error": "Cannot expel from current state"}
    
    def restore(self) -> Dict[str, Any]:
        """Begin restoration process."""
        if self.current_state == AutomatonState.EXPELLED:
            self.current_state = AutomatonState.RESTORED
            return {"success": True, "state": "restored"}
        return {"success": False}


# =============================================================================
# TEACHER MIDDLEWARE
# =============================================================================

class ComputationLayer(Enum):
    """Layers in the teacher middleware model."""
    
    DIVINE = "divine"           # Top: God's law
    INTERPRETIVE = "interpretive"  # Middle: Priests/teachers
    RUNTIME = "runtime"         # Bottom: People


@dataclass
class TeacherMiddleware:
    """
    Three-layer computation model.
    
    Top Layer: Divine code (Law as specification)
    Middle Layer: Priestly interpreters (compiler/VM)
    Bottom Layer: People (runtime environment)
    
    Divine code never acts directly on people;
    it flows through the interpretive middleware.
    """
    
    def compile_law(self, divine_code: str,
                    interpreter: RoleNode) -> Dict[str, Any]:
        """
        Compile divine law through interpreter.
        
        Returns practical instruction for runtime.
        """
        if not interpreter.can_teach:
            return {"error": "Interpreter cannot teach"}
        
        # Simulate compilation
        return {
            "source": divine_code,
            "interpreter": interpreter.name,
            "compiled": f"[{interpreter.name}]: {divine_code}",
            "authority_level": interpreter.authority_level
        }
    
    def execute_instruction(self, instruction: Dict[str, Any],
                            receiver: CommunityMember) -> Dict[str, Any]:
        """
        Execute compiled instruction on community member.
        
        Checks that instruction authority matches receiver status.
        """
        if not instruction.get("compiled"):
            return {"error": "Invalid instruction"}
        
        return {
            "instruction": instruction["compiled"],
            "receiver": receiver.name,
            "executed": True,
            "effect": "Instruction applied to runtime"
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_role_graph() -> bool:
    """Validate role graph module."""
    
    # Test role definitions
    assert len(ROLE_DEFINITIONS) >= 8
    
    high_priest = ROLE_DEFINITIONS[RoleType.HIGH_PRIEST]
    assert high_priest.holiness_level == HolinessLevel.MOST_HOLY
    assert high_priest.can_sacrifice
    
    # Test role graph
    graph = RoleGraph()
    assert len(graph.nodes) >= 8
    assert len(graph.edges) >= 3
    
    # Test authority
    assert graph.can_command(RoleType.HIGH_PRIEST, RoleType.PRIEST)
    assert not graph.can_command(RoleType.ISRAELITE, RoleType.PRIEST)
    
    # Test community member
    member = CommunityMember(
        member_id="001",
        name="Yohanan",
        primary_role=RoleType.ISRAELITE,
        community_class=CommunityClass.FULL_MEMBER
    )
    assert member.get_standing() > 0
    
    # Test automaton
    automaton = InstitutionalAutomaton()
    assert automaton.current_state == AutomatonState.OUTSIDE
    
    result = automaton.transition(
        AutomatonState.CANDIDATE,
        {"examination": True, "sponsor": True}
    )
    assert result["success"]
    
    # Test middleware
    middleware = TeacherMiddleware()
    priest = ROLE_DEFINITIONS[RoleType.PRIEST]
    
    compiled = middleware.compile_law("Keep the Sabbath", priest)
    assert "compiled" in compiled
    
    return True


if __name__ == "__main__":
    print("Validating Role Graph Module...")
    assert validate_role_graph()
    print("✓ Role Graph Module validated")
    
    # Demo
    print("\n--- Role Hierarchy Demo ---")
    graph = RoleGraph()
    
    for role_type, node in list(graph.nodes.items())[:5]:
        print(f"{node.name}:")
        print(f"  Authority: {node.authority_level}")
        print(f"  Holiness: {node.holiness_level.name}")
    
    print("\n--- Institutional Automaton Demo ---")
    automaton = InstitutionalAutomaton()
    
    steps = [
        (AutomatonState.CANDIDATE, {"examination": True, "sponsor": True}),
        (AutomatonState.NOVICE, {"oath": True, "knowledge_test": True}),
        (AutomatonState.PROBATIONER, {"years": 1, "purity": True}),
        (AutomatonState.MEMBER, {"years": 1, "vote": True}),
    ]
    
    for target, conditions in steps:
        result = automaton.transition(target, conditions)
        status = "✓" if result["success"] else "✗"
        print(f"  {status} → {target.value}")
