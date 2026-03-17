"""
ATHENA OS - EPICS: PROTOCOLS
=============================
Extracted Protocol Specifications from Epic Narratives

PROTOCOL COMPONENTS:
    1. Name and Designation - what subsystem it addresses
    2. Objective - what problem it solves
    3. Architecture - state space, agents, resources, constraints
    4. Error Section - failure modes and patches
    5. Procedure - step-by-step execution
    6. Invariants - what must never be violated

MAJOR PROTOCOLS:
    - GILGAMESH_PROTOCOL: Termination Problem / Soft Persistence
    - ILIAD_PROTOCOL: Conflict Engine / Rage Management
    - ODYSSEY_PROTOCOL: Navigation Solver / Identity Preservation
    - MAHABHARATA_PROTOCOL: System Reset / Dharma Maintenance
    - AENEID_PROTOCOL: Migration Assistant / Civilizational Transfer
    - BEOWULF_PROTOCOL: Daemon Hunter / Threat Containment
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Callable, Any, Union
from enum import Enum, auto
import numpy as np

from .epic_registry import (
    EpicEntry, SystemDomain, FailureCategory, PatchType, EPIC_REGISTRY
)
from .failure_modes import CrashSignature, CrashSeverity


# =============================================================================
# PROTOCOL STATUS
# =============================================================================

class ProtocolStatus(Enum):
    """Status of a protocol execution."""
    
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PATCHED = "patched"


class ProtocolPhase(Enum):
    """Generic phases of protocol execution."""
    
    INITIALIZATION = "initialization"
    CHALLENGE = "challenge"
    CRISIS = "crisis"
    RESOLUTION = "resolution"
    INTEGRATION = "integration"


# =============================================================================
# PROTOCOL INVARIANT
# =============================================================================

@dataclass
class Invariant:
    """
    An invariant: something that must never be violated.
    
    If violated, triggers specific failure modes.
    """
    
    name: str
    description: str
    
    # What happens if violated
    violation_consequence: str
    failure_triggered: Optional[FailureCategory] = None
    
    # How to check
    check_variable: str = ""
    threshold: float = 0.0
    comparison: str = ">"  # >, <, ==, !=
    
    def check(self, value: float) -> bool:
        """Check if invariant is maintained."""
        if self.comparison == ">":
            return value > self.threshold
        elif self.comparison == "<":
            return value < self.threshold
        elif self.comparison == "==":
            return abs(value - self.threshold) < 0.001
        elif self.comparison == "!=":
            return abs(value - self.threshold) >= 0.001
        return True


# =============================================================================
# PROTOCOL STEP
# =============================================================================

@dataclass
class ProtocolStep:
    """
    A single step in a protocol.
    
    The atomic unit of protocol execution.
    """
    
    name: str
    description: str
    
    # Phase
    phase: ProtocolPhase
    
    # Preconditions
    preconditions: List[str] = field(default_factory=list)
    
    # Actions
    actions: List[str] = field(default_factory=list)
    
    # Effects on state
    state_effects: Dict[str, float] = field(default_factory=dict)
    
    # Success/failure conditions
    success_condition: str = ""
    failure_condition: str = ""
    
    # Next steps (branching)
    on_success: Optional[str] = None
    on_failure: Optional[str] = None


# =============================================================================
# PROTOCOL
# =============================================================================

@dataclass
class Protocol:
    """
    A complete protocol extracted from an epic.
    
    Functions as a procedure specification for handling specific
    system states and failures.
    """
    
    # Identity
    name: str
    epic_source: str
    system_designation: str
    
    # Domain
    domain: SystemDomain
    
    # Objective
    objective: str
    
    # Architecture
    state_variables: List[str] = field(default_factory=list)
    agents: List[str] = field(default_factory=list)
    resources: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    
    # Invariants
    invariants: List[Invariant] = field(default_factory=list)
    
    # Steps
    steps: List[ProtocolStep] = field(default_factory=list)
    
    # Error handling
    failure_modes: List[FailureCategory] = field(default_factory=list)
    patches: List[PatchType] = field(default_factory=list)
    
    # Execution state
    status: ProtocolStatus = ProtocolStatus.NOT_STARTED
    current_step: int = 0
    
    def execute_step(self, step_index: int) -> Dict:
        """Execute a specific step of the protocol."""
        if step_index >= len(self.steps):
            return {"error": "Step index out of range"}
        
        step = self.steps[step_index]
        self.current_step = step_index
        self.status = ProtocolStatus.IN_PROGRESS
        
        return {
            "step": step.name,
            "phase": step.phase.value,
            "actions": step.actions,
            "effects": step.state_effects,
            "on_success": step.on_success,
            "on_failure": step.on_failure
        }
    
    def check_invariants(self, state: Dict[str, float]) -> List[str]:
        """Check which invariants are violated."""
        violations = []
        for inv in self.invariants:
            if inv.check_variable in state:
                if not inv.check(state[inv.check_variable]):
                    violations.append(inv.name)
        return violations
    
    def get_applicable_patches(self, 
                               failure: FailureCategory) -> List[PatchType]:
        """Get patches applicable for a specific failure."""
        if failure in self.failure_modes:
            return self.patches
        return []
    
    def complete(self, success: bool) -> None:
        """Mark protocol as completed."""
        self.status = ProtocolStatus.COMPLETED if success else ProtocolStatus.FAILED


# =============================================================================
# PROTOCOL DEFINITIONS
# =============================================================================

def create_gilgamesh_protocol() -> Protocol:
    """
    GILGAMESH_PROTOCOL: Legacy_Protocol (v1.0)
    
    Addresses: Termination Problem
    Solution: Soft Persistence via monuments/memory
    """
    return Protocol(
        name="GILGAMESH_PROTOCOL",
        epic_source="Epic of Gilgamesh",
        system_designation="Legacy_Protocol (v1.0)",
        domain=SystemDomain.INDIVIDUAL,
        objective="Solve the Termination Problem - can finite node achieve persistence?",
        state_variables=["mortality_awareness", "grief", "legacy_score", "friendship_bond"],
        agents=["Gilgamesh", "Enkidu", "Utnapishtim", "Siduri", "Urshanabi"],
        resources=["immortality_plant", "flood_story", "city_walls", "tablets"],
        constraints=[
            "Finite hardware cannot host infinite thread",
            "Mortality is non-negotiable for standard nodes"
        ],
        invariants=[
            Invariant(
                name="mortality_acceptance",
                description="Agent must eventually accept finite runtime",
                violation_consequence="Endless futile questing",
                check_variable="mortality_awareness",
                threshold=0.8,
                comparison=">"
            )
        ],
        steps=[
            ProtocolStep(
                name="friendship_initialization",
                description="Bond with mirror-node (Enkidu)",
                phase=ProtocolPhase.INITIALIZATION,
                state_effects={"friendship_bond": 1.0},
                on_success="joint_adventure"
            ),
            ProtocolStep(
                name="joint_adventure",
                description="Execute heroic tasks together",
                phase=ProtocolPhase.CHALLENGE,
                state_effects={"legacy_score": 0.3},
                on_success="mirror_node_termination"
            ),
            ProtocolStep(
                name="mirror_node_termination",
                description="Enkidu dies - triggers grief cascade",
                phase=ProtocolPhase.CRISIS,
                state_effects={"grief": 1.0, "mortality_awareness": 0.5},
                on_success="immortality_quest"
            ),
            ProtocolStep(
                name="immortality_quest",
                description="Seek hard persistence solution",
                phase=ProtocolPhase.CRISIS,
                preconditions=["grief > 0.5"],
                on_success="token_acquisition",
                on_failure="soft_persistence_realization"
            ),
            ProtocolStep(
                name="token_acquisition",
                description="Acquire immortality plant",
                phase=ProtocolPhase.CRISIS,
                on_success="token_loss",
                on_failure="soft_persistence_realization"
            ),
            ProtocolStep(
                name="token_loss",
                description="Lose plant to entropy-serpent",
                phase=ProtocolPhase.CRISIS,
                state_effects={"mortality_awareness": 1.0},
                on_success="soft_persistence_realization"
            ),
            ProtocolStep(
                name="soft_persistence_realization",
                description="Accept soft persistence via monuments/stories",
                phase=ProtocolPhase.RESOLUTION,
                state_effects={"legacy_score": 1.0, "grief": 0.3},
                on_success="integration"
            ),
            ProtocolStep(
                name="integration",
                description="Return home, build walls, write tablets",
                phase=ProtocolPhase.INTEGRATION,
                state_effects={"mortality_awareness": 1.0, "legacy_score": 1.0}
            )
        ],
        failure_modes=[FailureCategory.IDENTITY_CORRUPTION],
        patches=[PatchType.SOFT_PERSISTENCE]
    )


def create_iliad_protocol() -> Protocol:
    """
    ILIAD_PROTOCOL: Conflict_Engine (Menis)
    
    Addresses: Rage Overflow
    Solution: Mortality-Aware Handshake
    """
    return Protocol(
        name="ILIAD_PROTOCOL",
        epic_source="Iliad",
        system_designation="Conflict_Engine (Menis)",
        domain=SystemDomain.CONFLICT,
        objective="Model rage saturation and recovery in zero-sum conflict systems",
        state_variables=["menis", "kleos", "time", "moira", "grief"],
        agents=["Achilles", "Agamemnon", "Hector", "Patroclus", "Priam", "Zeus"],
        resources=["kleos_ledger", "armor", "chariot", "funeral_rites"],
        constraints=[
            "Kleos is zero-sum (blockchain reputation)",
            "Time violation triggers menis",
            "Will of Zeus enforces precompiled outcome"
        ],
        invariants=[
            Invariant(
                name="kleos_conservation",
                description="Total kleos in system is conserved",
                violation_consequence="Ledger corruption",
                check_variable="total_kleos",
                threshold=1.0,
                comparison="=="
            ),
            Invariant(
                name="moira_respect",
                description="Fate allotment must be respected",
                violation_consequence="Divine intervention",
                failure_triggered=FailureCategory.RAGE_OVERFLOW
            )
        ],
        steps=[
            ProtocolStep(
                name="time_violation",
                description="Agamemnon takes Briseis, violating Achilles' honor",
                phase=ProtocolPhase.INITIALIZATION,
                state_effects={"time": -0.5, "menis": 0.5},
                on_success="menis_activation"
            ),
            ProtocolStep(
                name="menis_activation",
                description="Achilles withdraws from battle in rage",
                phase=ProtocolPhase.CHALLENGE,
                state_effects={"menis": 0.8},
                on_success="consequence_cascade"
            ),
            ProtocolStep(
                name="consequence_cascade",
                description="Greeks suffer losses without Achilles",
                phase=ProtocolPhase.CHALLENGE,
                state_effects={"menis": 0.9},
                on_success="patroclus_death"
            ),
            ProtocolStep(
                name="patroclus_death",
                description="Mirror-node dies, redirects rage",
                phase=ProtocolPhase.CRISIS,
                state_effects={"grief": 1.0, "menis": 1.0},
                on_success="rage_overflow"
            ),
            ProtocolStep(
                name="rage_overflow",
                description="Achilles returns with maximum rage",
                phase=ProtocolPhase.CRISIS,
                state_effects={"menis": 1.0, "kleos": 0.9},
                on_success="hector_death"
            ),
            ProtocolStep(
                name="hector_death",
                description="Kill Hector, desecrate body",
                phase=ProtocolPhase.CRISIS,
                state_effects={"kleos": 1.0},
                on_success="mortality_handshake"
            ),
            ProtocolStep(
                name="mortality_handshake",
                description="Priam-Achilles meeting - shared mortality recognition",
                phase=ProtocolPhase.RESOLUTION,
                state_effects={"menis": 0.0, "grief": 0.5},
                on_success="integration"
            ),
            ProtocolStep(
                name="integration",
                description="Funeral rites restore order",
                phase=ProtocolPhase.INTEGRATION,
                state_effects={"menis": 0.0}
            )
        ],
        failure_modes=[FailureCategory.RAGE_OVERFLOW],
        patches=[PatchType.MORTALITY_HANDSHAKE]
    )


def create_odyssey_protocol() -> Protocol:
    """
    ODYSSEY_PROTOCOL: Navigation_Solver (Nostos)
    
    Addresses: Identity Corruption in hostile networks
    Solution: Polymorphic Routing + Identity Lock
    """
    return Protocol(
        name="ODYSSEY_PROTOCOL",
        epic_source="Odyssey",
        system_designation="Navigation_Solver (Nostos)",
        domain=SystemDomain.MIGRATION,
        objective="Route displaced packet through hostile network to origin",
        state_variables=["identity_vector", "nostos", "destination_address", "cunning"],
        agents=["Odysseus", "Penelope", "Telemachus", "Athena", "Poseidon", "Suitors"],
        resources=["ship", "crew", "moly_herb", "bow", "oar"],
        constraints=[
            "Identity must be preserved against erasure attacks",
            "Destination address must remain locked",
            "Polymorphism required for hostile nodes"
        ],
        invariants=[
            Invariant(
                name="identity_preservation",
                description="Core identity vector must never reach zero",
                violation_consequence="Permanent loss in network",
                check_variable="identity_vector",
                threshold=0.1,
                comparison=">"
            ),
            Invariant(
                name="destination_lock",
                description="Ithaca as destination must remain set",
                violation_consequence="Infinite loop in network",
                check_variable="destination_address",
                threshold=0.5,
                comparison=">"
            )
        ],
        steps=[
            ProtocolStep(
                name="departure",
                description="Leave Troy, begin return journey",
                phase=ProtocolPhase.INITIALIZATION,
                state_effects={"nostos": 0.9, "destination_address": 1.0}
            ),
            ProtocolStep(
                name="lotus_eaters",
                description="Biochemical forgetting attack",
                phase=ProtocolPhase.CHALLENGE,
                state_effects={"destination_address": -0.3},
                on_success="identity_lock",
                on_failure="packet_drop"
            ),
            ProtocolStep(
                name="identity_lock",
                description="Force crew away, preserve destination",
                phase=ProtocolPhase.CHALLENGE,
                state_effects={"destination_address": 1.0}
            ),
            ProtocolStep(
                name="polyphemus",
                description="Daemon encounter - use polymorphic identity",
                phase=ProtocolPhase.CHALLENGE,
                actions=["Claim name is 'Nobody'", "Blind daemon", "Escape"],
                state_effects={"cunning": 0.8}
            ),
            ProtocolStep(
                name="circe_transformation",
                description="Form transformation attack with root patch",
                phase=ProtocolPhase.CRISIS,
                preconditions=["Have moly_herb"],
                state_effects={"identity_vector": 0.9}
            ),
            ProtocolStep(
                name="underworld_navigation",
                description="Query Tiresias for route information",
                phase=ProtocolPhase.CRISIS,
                state_effects={"nostos": 0.7}
            ),
            ProtocolStep(
                name="scylla_charybdis",
                description="Navigate between two failure modes",
                phase=ProtocolPhase.CRISIS,
                failure_condition="Lose crew to either threat"
            ),
            ProtocolStep(
                name="calypso_escape",
                description="Resist permanent capture, maintain nostos",
                phase=ProtocolPhase.RESOLUTION,
                state_effects={"nostos": 1.0}
            ),
            ProtocolStep(
                name="suitor_cleanup",
                description="Garbage-collect parasitic processes",
                phase=ProtocolPhase.RESOLUTION,
                state_effects={"destination_address": 1.0}
            ),
            ProtocolStep(
                name="reunion",
                description="Identity verification and restoration",
                phase=ProtocolPhase.INTEGRATION,
                success_condition="Penelope recognizes Odysseus"
            )
        ],
        failure_modes=[FailureCategory.IDENTITY_CORRUPTION],
        patches=[PatchType.POLYMORPHIC_ROUTING]
    )


def create_mahabharata_protocol() -> Protocol:
    """
    MAHABHARATA_PROTOCOL: System_Reset (Kali Yuga)
    
    Addresses: Dharma Violation
    Solution: Hard Reset with log preservation
    """
    return Protocol(
        name="MAHABHARATA_PROTOCOL",
        epic_source="Mahabharata",
        system_designation="System_Reset (Kali Yuga)",
        domain=SystemDomain.COSMIC,
        objective="Execute hard reset when dharma falls below survivable threshold",
        state_variables=["dharma", "adharma", "yuga_phase", "karma_balance"],
        agents=["Pandavas", "Kauravas", "Krishna", "Bhishma", "Drona", "Karna"],
        resources=["kingdom", "weapons", "divine_chariots", "bhagavad_gita"],
        constraints=[
            "Dharma must be maintained above threshold",
            "Krishna's guidance is meta-OS level",
            "War is precompiled when negotiation fails"
        ],
        invariants=[
            Invariant(
                name="dharma_threshold",
                description="Dharma must not fall below survival level",
                violation_consequence="Mandatory system reset",
                check_variable="dharma",
                threshold=0.2,
                comparison=">",
                failure_triggered=FailureCategory.DHARMA_VIOLATION
            )
        ],
        steps=[
            ProtocolStep(
                name="succession_dispute",
                description="Legitimate vs illegitimate claims",
                phase=ProtocolPhase.INITIALIZATION,
                state_effects={"dharma": -0.1}
            ),
            ProtocolStep(
                name="dice_game",
                description="Stochastic chaos injection",
                phase=ProtocolPhase.CHALLENGE,
                state_effects={"dharma": -0.3, "adharma": 0.3}
            ),
            ProtocolStep(
                name="draupadi_humiliation",
                description="Major dharma violation",
                phase=ProtocolPhase.CRISIS,
                state_effects={"dharma": -0.4}
            ),
            ProtocolStep(
                name="exile",
                description="13 years timeout period",
                phase=ProtocolPhase.CRISIS,
                state_effects={"karma_balance": 0.2}
            ),
            ProtocolStep(
                name="negotiation_failure",
                description="Peaceful resolution impossible",
                phase=ProtocolPhase.CRISIS,
                on_failure="war_initiation"
            ),
            ProtocolStep(
                name="gita_download",
                description="Krishna reveals precompiled nature of war",
                phase=ProtocolPhase.CRISIS,
                state_effects={"dharma": 0.1},
                actions=["Vishvarupa revelation", "Duty over outcome teaching"]
            ),
            ProtocolStep(
                name="war_execution",
                description="18-day purge of corrupt nodes",
                phase=ProtocolPhase.RESOLUTION,
                state_effects={"adharma": -0.9}
            ),
            ProtocolStep(
                name="log_preservation",
                description="Preserve epic as warning for future cycles",
                phase=ProtocolPhase.INTEGRATION,
                state_effects={"dharma": 0.3}
            )
        ],
        failure_modes=[FailureCategory.DHARMA_VIOLATION, FailureCategory.DOOMED_RESET],
        patches=[PatchType.HARD_RESET]
    )


def create_beowulf_protocol() -> Protocol:
    """
    BEOWULF_PROTOCOL: Daemon_Hunter
    
    Addresses: Daemon Leak
    Solution: Recursive threat containment with self-sacrifice
    """
    return Protocol(
        name="BEOWULF_PROTOCOL",
        epic_source="Beowulf",
        system_designation="Daemon_Hunter",
        domain=SystemDomain.DAEMON,
        objective="Secure civilized zone from legacy chaos processes",
        state_variables=["threat_level", "wyrd", "heroic_reputation", "hall_integrity"],
        agents=["Beowulf", "Hrothgar", "Grendel", "Grendel_Mother", "Dragon"],
        resources=["hrunting_sword", "treasure_hoard", "mead_hall"],
        constraints=[
            "Daemons spawn recursively (defeating one spawns higher-order)",
            "Wyrd binds hero to eventual termination",
            "Hall represents civilized order that must be defended"
        ],
        invariants=[
            Invariant(
                name="hall_integrity",
                description="Mead-hall (civilization) must be preserved",
                violation_consequence="Chaos overwhelms order",
                check_variable="hall_integrity",
                threshold=0.3,
                comparison=">"
            )
        ],
        steps=[
            ProtocolStep(
                name="grendel_attacks",
                description="Primary daemon targets hall",
                phase=ProtocolPhase.INITIALIZATION,
                state_effects={"threat_level": 0.7, "hall_integrity": -0.3}
            ),
            ProtocolStep(
                name="hero_arrival",
                description="External threat response agent",
                phase=ProtocolPhase.CHALLENGE,
                state_effects={"heroic_reputation": 0.3}
            ),
            ProtocolStep(
                name="grendel_fight",
                description="Bare-handed combat with first daemon",
                phase=ProtocolPhase.CHALLENGE,
                state_effects={"threat_level": -0.3, "heroic_reputation": 0.5}
            ),
            ProtocolStep(
                name="mother_spawns",
                description="Recursive daemon escalation",
                phase=ProtocolPhase.CRISIS,
                state_effects={"threat_level": 0.8}
            ),
            ProtocolStep(
                name="underwater_descent",
                description="Enter hostile daemon territory",
                phase=ProtocolPhase.CRISIS,
                actions=["Descend to mere", "Use giant-sword", "Defeat mother"]
            ),
            ProtocolStep(
                name="dragon_awakens",
                description="Final recursive escalation",
                phase=ProtocolPhase.CRISIS,
                preconditions=["50 years later"],
                state_effects={"threat_level": 1.0}
            ),
            ProtocolStep(
                name="hero_sacrifice",
                description="Hero terminates with final daemon",
                phase=ProtocolPhase.RESOLUTION,
                state_effects={"threat_level": 0.0, "wyrd": 1.0, "heroic_reputation": 1.0}
            ),
            ProtocolStep(
                name="ids_rule_creation",
                description="Epic becomes signature-based detection rule",
                phase=ProtocolPhase.INTEGRATION,
                actions=["Record saga", "Teach future generations"]
            )
        ],
        failure_modes=[FailureCategory.DAEMON_LEAK],
        patches=[PatchType.DAEMON_BINDING]
    )


# =============================================================================
# PROTOCOL LIBRARY
# =============================================================================

class ProtocolLibrary:
    """
    Library of all extracted protocols.
    
    The complete operational toolkit for the ASI.
    """
    
    def __init__(self):
        self._protocols: Dict[str, Protocol] = {}
        self._load_core_protocols()
    
    def _load_core_protocols(self) -> None:
        """Load core protocols."""
        protocols = [
            create_gilgamesh_protocol(),
            create_iliad_protocol(),
            create_odyssey_protocol(),
            create_mahabharata_protocol(),
            create_beowulf_protocol(),
        ]
        
        for proto in protocols:
            self.register(proto)
    
    def register(self, protocol: Protocol) -> None:
        """Register a protocol."""
        self._protocols[protocol.name] = protocol
    
    def get(self, name: str) -> Optional[Protocol]:
        """Get a protocol by name."""
        return self._protocols.get(name)
    
    def get_by_domain(self, domain: SystemDomain) -> List[Protocol]:
        """Get protocols for a specific domain."""
        return [p for p in self._protocols.values() if p.domain == domain]
    
    def get_for_failure(self, failure: FailureCategory) -> List[Protocol]:
        """Get protocols that address a specific failure mode."""
        return [p for p in self._protocols.values() 
                if failure in p.failure_modes]
    
    def execute_protocol(self, name: str) -> Dict:
        """Execute a complete protocol."""
        proto = self.get(name)
        if not proto:
            return {"error": f"Protocol {name} not found"}
        
        results = []
        for i, step in enumerate(proto.steps):
            result = proto.execute_step(i)
            results.append(result)
        
        proto.complete(True)
        
        return {
            "protocol": name,
            "status": proto.status.value,
            "steps_executed": len(results),
            "results": results
        }
    
    def __len__(self) -> int:
        return len(self._protocols)
    
    def __iter__(self):
        return iter(self._protocols.values())


# =============================================================================
# GLOBAL LIBRARY
# =============================================================================

PROTOCOL_LIBRARY = ProtocolLibrary()


# =============================================================================
# VALIDATION
# =============================================================================

def validate_protocols() -> bool:
    """Validate protocols module."""
    
    # Test Invariant
    inv = Invariant(
        name="test_invariant",
        description="Test",
        violation_consequence="Bad things",
        check_variable="test",
        threshold=0.5,
        comparison=">"
    )
    
    assert inv.check(0.6)
    assert not inv.check(0.4)
    
    # Test ProtocolStep
    step = ProtocolStep(
        name="test_step",
        description="Test step",
        phase=ProtocolPhase.INITIALIZATION,
        state_effects={"var1": 0.5}
    )
    
    assert step.phase == ProtocolPhase.INITIALIZATION
    
    # Test Protocol creation
    gilgamesh = create_gilgamesh_protocol()
    
    assert gilgamesh.name == "GILGAMESH_PROTOCOL"
    assert gilgamesh.domain == SystemDomain.INDIVIDUAL
    assert len(gilgamesh.steps) > 5
    
    result = gilgamesh.execute_step(0)
    assert "step" in result
    
    violations = gilgamesh.check_invariants({"mortality_awareness": 0.5})
    assert "mortality_acceptance" in violations
    
    # Test Iliad Protocol
    iliad = create_iliad_protocol()
    
    assert iliad.domain == SystemDomain.CONFLICT
    assert FailureCategory.RAGE_OVERFLOW in iliad.failure_modes
    
    # Test Protocol Library
    library = PROTOCOL_LIBRARY
    
    assert len(library) >= 5
    
    proto = library.get("ILIAD_PROTOCOL")
    assert proto is not None
    
    conflict_protos = library.get_by_domain(SystemDomain.CONFLICT)
    assert len(conflict_protos) >= 1
    
    rage_protos = library.get_for_failure(FailureCategory.RAGE_OVERFLOW)
    assert len(rage_protos) >= 1
    
    # Test execution
    result = library.execute_protocol("GILGAMESH_PROTOCOL")
    assert result["status"] == ProtocolStatus.COMPLETED.value
    
    return True


if __name__ == "__main__":
    print("Validating Protocols Module...")
    assert validate_protocols()
    print("✓ Protocols Module validated")
    
    print(f"\nProtocols in library: {len(PROTOCOL_LIBRARY)}")
    for proto in PROTOCOL_LIBRARY:
        print(f"  - {proto.name}: {proto.objective[:50]}...")
