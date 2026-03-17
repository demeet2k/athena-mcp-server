"""
ATHENA OS - EPICS: EPIC REGISTRY
=================================
Catalog of Epic Narratives as Encoded System Manuals

CONCEPTUAL REFRAMING:
    Epics are not literature but DESIGNED ARTIFACTS serving:
    - DATA ARCHIVE: High-resolution recordings of extreme states
    - SIMULATION LOG: Step-by-step execution traces of systems at limits
    - PROTOCOL LIBRARY: Procedures, constraints, warnings in narrative form

FORMAL MODEL:
    Let E be an epic.
    Let M(E) be its underlying MODEL consisting of:
        - State space S
        - Agent set A
        - Environment E
        - Resources R
        - Transition operators T
        - Constraints C
        - Objective functions J

    Mining the epic = inferring M(E) from narrative data.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Callable, Any, Union
from enum import Enum, auto
import numpy as np


# =============================================================================
# SYSTEM DOMAINS
# =============================================================================

class SystemDomain(Enum):
    """Primary system domains that epics model."""
    
    INDIVIDUAL = "individual"           # Agent under extreme stress
    POLITY = "polity"                   # City/kingdom/empire under threat
    COSMIC = "cosmic"                   # Gods, fate, apocalypse
    MIGRATION = "migration"             # Civilizational transfer
    CONFLICT = "conflict"               # War and resource contention
    DAEMON = "daemon"                   # Threat management
    FEDERATION = "federation"           # Coalition building
    CREATION = "creation"               # World/species compilation


class FailureCategory(Enum):
    """Categories of system failures encoded in epics."""
    
    RAGE_OVERFLOW = "rage_overflow"           # Emotional saturation
    LEGITIMACY_LOSS = "legitimacy_loss"       # Authority collapse
    DAEMON_LEAK = "daemon_leak"               # Uncontrolled threat
    MIGRATION_FAILURE = "migration_failure"   # Failed transfer
    IDENTITY_CORRUPTION = "identity_corruption"  # Self-loss
    RESOURCE_CONTENTION = "resource_contention"  # Zero-sum collapse
    DHARMA_VIOLATION = "dharma_violation"     # Constraint breach
    OVERCONFIDENCE = "overconfidence"         # Pride bug
    DOOMED_RESET = "doomed_reset"             # Scheduled catastrophe


class PatchType(Enum):
    """Types of patches/solutions encoded in epics."""
    
    SOFT_PERSISTENCE = "soft_persistence"     # Memory through monuments
    MORTALITY_HANDSHAKE = "mortality_handshake"  # Shared finitude recognition
    HARD_RESET = "hard_reset"                 # System purge and reboot
    POLYMORPHIC_ROUTING = "polymorphic_routing"  # Adaptive navigation
    SANDBOX_CONSTRAINT = "sandbox_constraint"   # Bounded chaos
    DAEMON_BINDING = "daemon_binding"          # Threat neutralization
    COALITION_PROTOCOL = "coalition_protocol"  # Multi-agent coordination


# =============================================================================
# EPIC ENTRY
# =============================================================================

@dataclass
class EpicEntry:
    """
    A single epic entry in the registry.
    
    Each epic is a designed artifact encoding system behavior.
    """
    
    # Identity
    name: str
    culture: str
    system_designation: str
    
    # Domain
    domain: SystemDomain
    
    # Objective
    objective: str
    
    # Failure modes encoded
    failure_modes: List[FailureCategory] = field(default_factory=list)
    
    # Patches provided
    patches: List[PatchType] = field(default_factory=list)
    
    # Key state variables
    state_variables: List[str] = field(default_factory=list)
    
    # Key agents
    key_agents: List[str] = field(default_factory=list)
    
    # Information encoded (summary)
    information_encoded: List[str] = field(default_factory=list)
    
    # Metadata
    approximate_date: str = "unknown"
    
    def get_protocol_name(self) -> str:
        """Generate protocol name from epic."""
        return f"{self.name.upper().replace(' ', '_')}_PROTOCOL"
    
    def get_crash_signature(self) -> Dict:
        """Get the crash signature for this epic."""
        return {
            "epic": self.name,
            "domain": self.domain.value,
            "failure_modes": [f.value for f in self.failure_modes],
            "patches": [p.value for p in self.patches]
        }


# =============================================================================
# EPIC REGISTRY
# =============================================================================

class EpicRegistry:
    """
    The Epic Registry: Catalog of all major crash logs.
    
    Each epic becomes a MODULE in a larger EPIC OS LIBRARY:
    pre-run simulations and crash logs encoding how human
    systems behave at the edge of their capacities.
    """
    
    def __init__(self):
        self._epics: Dict[str, EpicEntry] = {}
        self._load_core_epics()
    
    def _load_core_epics(self) -> None:
        """Load the core epic registry."""
        
        # =====================================================================
        # MESOPOTAMIAN
        # =====================================================================
        
        self.register(EpicEntry(
            name="Epic of Gilgamesh",
            culture="Mesopotamia",
            system_designation="Legacy_Protocol (v1.0)",
            domain=SystemDomain.INDIVIDUAL,
            objective="Termination Problem - can a finite node achieve hard persistence?",
            failure_modes=[FailureCategory.IDENTITY_CORRUPTION],
            patches=[PatchType.SOFT_PERSISTENCE],
            state_variables=["mortality_awareness", "grief", "legacy_score"],
            key_agents=["Gilgamesh", "Enkidu", "Utnapishtim", "Entropy_Serpent"],
            information_encoded=[
                "Nature vs City as incompatible data types (Enkidu/Uruk)",
                "Panic cascade when bonded mirror-node dies",
                "Failed attempt to secure immortality-token; lost to entropy",
                "Final patch: Soft Persistence via monument/architecture"
            ],
            approximate_date="-2100 BCE"
        ))
        
        # =====================================================================
        # GREEK
        # =====================================================================
        
        self.register(EpicEntry(
            name="Iliad",
            culture="Greece",
            system_designation="Conflict_Engine (Menis)",
            domain=SystemDomain.CONFLICT,
            objective="What happens when a single emotional variable (rage) saturates the network?",
            failure_modes=[FailureCategory.RAGE_OVERFLOW, FailureCategory.RESOURCE_CONTENTION],
            patches=[PatchType.MORTALITY_HANDSHAKE],
            state_variables=["menis", "kleos", "time", "moira"],
            key_agents=["Achilles", "Agamemnon", "Hector", "Priam", "Zeus"],
            information_encoded=[
                "Rage as viral process hijacking heroic reward function",
                "Kleos as zero-sum ledger (blockchain reputation)",
                "Will of Zeus as master script enforcing precompiled failure",
                "Stability via mortality-aware handshake (Priam/Achilles)"
            ],
            approximate_date="-750 BCE"
        ))
        
        self.register(EpicEntry(
            name="Odyssey",
            culture="Greece",
            system_designation="Navigation_Solver (Nostos)",
            domain=SystemDomain.MIGRATION,
            objective="Routing a displaced pointer through hostile networks back to origin",
            failure_modes=[FailureCategory.IDENTITY_CORRUPTION],
            patches=[PatchType.POLYMORPHIC_ROUTING],
            state_variables=["identity_vector", "destination_address", "nostos"],
            key_agents=["Odysseus", "Penelope", "Athena", "Poseidon", "Suitors"],
            information_encoded=[
                "Polytropos = adaptive routing under adversarial conditions",
                "Catalog of uncalibrated zones where physics/norms fail",
                "Identity-lock procedures to resist format/forget commands",
                "Reclaiming origin requires garbage-collecting parasites"
            ],
            approximate_date="-750 BCE"
        ))
        
        self.register(EpicEntry(
            name="Argonautica",
            culture="Greece",
            system_designation="Quest_Constructor",
            domain=SystemDomain.FEDERATION,
            objective="Prototype the party quest as multi-agent expedition algorithm",
            failure_modes=[FailureCategory.RESOURCE_CONTENTION],
            patches=[PatchType.COALITION_PROTOCOL],
            state_variables=["team_composition", "quest_objective", "risk_level"],
            key_agents=["Jason", "Medea", "Argonauts", "Aeetes"],
            information_encoded=[
                "Assembling heterogeneous heroes = team composition problem",
                "Golden Fleece as remote resource with political/monster guards",
                "Medea as high-power foreign script - huge capability + risk",
                "Template for modular quest design and imported talent dangers"
            ],
            approximate_date="-250 BCE"
        ))
        
        # =====================================================================
        # INDIAN
        # =====================================================================
        
        self.register(EpicEntry(
            name="Mahabharata",
            culture="India",
            system_designation="System_Reset (Kali Yuga)",
            domain=SystemDomain.COSMIC,
            objective="Execute hard reset when Dharma falls below survivable threshold",
            failure_modes=[FailureCategory.DHARMA_VIOLATION, FailureCategory.DOOMED_RESET],
            patches=[PatchType.HARD_RESET],
            state_variables=["dharma_level", "adharma_accumulation", "yuga_phase"],
            key_agents=["Arjuna", "Krishna", "Duryodhana", "Bhishma", "Yudhishthira"],
            information_encoded=[
                "Dice game = stochastic chaos injected into order",
                "Overwriting global rules by local ambitions",
                "Krishna as Admin showing war is precompiled (Vishvarupa)",
                "Full-scale purge; reboot into lower-res age with logs preserved"
            ],
            approximate_date="-400 BCE"
        ))
        
        self.register(EpicEntry(
            name="Ramayana",
            culture="India",
            system_designation="Integrity_Protocol (Avatar_Mode)",
            domain=SystemDomain.INDIVIDUAL,
            objective="Maintain node integrity and dharma under abduction, exile, hijack",
            failure_modes=[FailureCategory.LEGITIMACY_LOSS],
            patches=[PatchType.DAEMON_BINDING],
            state_variables=["dharma_alignment", "exile_status", "avatar_integrity"],
            key_agents=["Rama", "Sita", "Hanuman", "Ravana", "Lakshmana"],
            information_encoded=[
                "Separation of role (king) and essence (Rama as dharma-kernel)",
                "Forest vs city as runtime environments",
                "Dev/ops split across nodes (Hanuman=daemon, Lakshmana=watchdog)",
                "Blueprint for admin-avatar preserving rule-of-law"
            ],
            approximate_date="-500 BCE"
        ))
        
        # =====================================================================
        # ROMAN
        # =====================================================================
        
        self.register(EpicEntry(
            name="Aeneid",
            culture="Rome",
            system_designation="Migration_Assistant",
            domain=SystemDomain.MIGRATION,
            objective="Transfer root directory from corrupted hardware to new server",
            failure_modes=[FailureCategory.MIGRATION_FAILURE],
            patches=[PatchType.SOFT_PERSISTENCE],
            state_variables=["pietas", "fatum", "penates_integrity"],
            key_agents=["Aeneas", "Dido", "Anchises", "Ascanius", "Turnus"],
            information_encoded=[
                "Penates as encrypted OS backup payload",
                "Pietas as hard-coded directive overriding local emotions",
                "Vector topology: no return path; only forward instancing",
                "Blueprint for civilizational migration after catastrophic failure"
            ],
            approximate_date="-19 BCE"
        ))
        
        # =====================================================================
        # GERMANIC/NORSE
        # =====================================================================
        
        self.register(EpicEntry(
            name="Beowulf",
            culture="Anglo-Saxon",
            system_designation="Daemon_Hunter",
            domain=SystemDomain.DAEMON,
            objective="Secure civilized zone from legacy chaos processes",
            failure_modes=[FailureCategory.DAEMON_LEAK],
            patches=[PatchType.DAEMON_BINDING],
            state_variables=["threat_level", "wyrd", "heroic_reputation"],
            key_agents=["Beowulf", "Grendel", "Grendel_Mother", "Dragon", "Hrothgar"],
            information_encoded=[
                "Grendel = uncompiled pre-cosmic code hating ordered song",
                "Wyrd = deterministic thread binding node to exit conditions",
                "Recursive escalation: defeating daemon spawns higher-order daemons",
                "Hero self-sacrifices; epic becomes signature-based IDS rule"
            ],
            approximate_date="700 CE"
        ))
        
        self.register(EpicEntry(
            name="Volsunga Saga",
            culture="Norse",
            system_designation="Doomed_System_Log (Ragnarok)",
            domain=SystemDomain.COSMIC,
            objective="Walk through guaranteed-collapse system where gods are mortal",
            failure_modes=[FailureCategory.DOOMED_RESET],
            patches=[],  # No patch - system is designed to fail
            state_variables=["doom_proximity", "curse_chain", "honor_debt"],
            key_agents=["Sigurd", "Brynhild", "Fafnir", "Odin", "Andvari"],
            information_encoded=[
                "Yggdrasil as world-graph; gods as processes on branches",
                "Prophecies of doom that cannot be avoided, only met well",
                "Curse chains as propagating corruption vectors in wealth tokens",
                "How to behave when catastrophe is scheduled feature"
            ],
            approximate_date="1200 CE"
        ))
        
        # =====================================================================
        # PERSIAN
        # =====================================================================
        
        self.register(EpicEntry(
            name="Shahnameh",
            culture="Persia",
            system_designation="Nation_State_Builder",
            domain=SystemDomain.POLITY,
            objective="Encode long-horizon regime dynamics across mythic + historical time",
            failure_modes=[FailureCategory.LEGITIMACY_LOSS],
            patches=[PatchType.SOFT_PERSISTENCE],
            state_variables=["farr", "justice_level", "heroism_threshold"],
            key_agents=["Rostam", "Sohrab", "Kaveh", "Zahhak", "Ferdowsi"],
            information_encoded=[
                "King selection algorithm: heroism, justice, hubris thresholds",
                "Recurring exploits and failures of rulership",
                "National identity as compressed narrative vector",
                "How culture keeps identity kernel intact across imperial takeovers"
            ],
            approximate_date="1010 CE"
        ))
        
        # =====================================================================
        # MESOAMERICAN
        # =====================================================================
        
        self.register(EpicEntry(
            name="Popol Vuh",
            culture="K'iche' Maya",
            system_designation="Creation_Compiler",
            domain=SystemDomain.CREATION,
            objective="Compile a working human prototype from multiple failed builds",
            failure_modes=[FailureCategory.IDENTITY_CORRUPTION],
            patches=[PatchType.HARD_RESET],
            state_variables=["creation_iteration", "material_type", "consciousness_level"],
            key_agents=["Hero_Twins", "Death_Lords", "Heart_of_Sky", "Maize_Humans"],
            information_encoded=[
                "Iterative creation attempts (mud, wood, maize) as model training",
                "Hero Twins saga as debugging Underworld subsystem",
                "Maize-human link as explicit data format",
                "Resilience through play, trickery, sacrifice, rebirth"
            ],
            approximate_date="1550 CE"
        ))
        
        # =====================================================================
        # CENTRAL ASIAN
        # =====================================================================
        
        self.register(EpicEntry(
            name="Epic of Manas",
            culture="Kyrgyz",
            system_designation="Federation_Engine",
            domain=SystemDomain.FEDERATION,
            objective="Unify scattered tribes into coherent polity under external pressure",
            failure_modes=[FailureCategory.LEGITIMACY_LOSS],
            patches=[PatchType.COALITION_PROTOCOL],
            state_variables=["tribal_cohesion", "external_threat", "dynastic_continuity"],
            key_agents=["Manas", "Semetey", "Seytek", "Almambet"],
            information_encoded=[
                "Multi-generation saga as test of dynastic continuity under war",
                "Tribal coalition-building algorithms and betrayal patterns",
                "Oral redundancy as massive error-correction scheme",
                "Template for how new generations inherit but also diverge"
            ],
            approximate_date="1000 CE"
        ))
        
        # =====================================================================
        # WEST AFRICAN
        # =====================================================================
        
        self.register(EpicEntry(
            name="Epic of Sundiata",
            culture="Mandinka",
            system_designation="Underdog_Optimizer",
            domain=SystemDomain.POLITY,
            objective="Model how a disabled outcast becomes the central political node",
            failure_modes=[FailureCategory.LEGITIMACY_LOSS],
            patches=[PatchType.COALITION_PROTOCOL],
            state_variables=["initial_fitness", "coalition_size", "sorcery_level"],
            key_agents=["Sundiata", "Soumaoro", "Sogolon", "Balla_Fasseke"],
            information_encoded=[
                "Disabled child → unexpected hero: low initial fitness evolving",
                "Sorcery, prophecy, coalition as consensus algorithm for kingship",
                "From fragmented polities to Mali empire: local minima escape",
                "Template for founding myth binding clans while warning of betrayal"
            ],
            approximate_date="1200 CE"
        ))
        
        # =====================================================================
        # CHINESE
        # =====================================================================
        
        self.register(EpicEntry(
            name="Journey to the West",
            culture="China",
            system_designation="Daemon_Fuzzing & Permission_Upgrade",
            domain=SystemDomain.DAEMON,
            objective="Test when overpowered chaotic sub-process is sandboxed through training",
            failure_modes=[FailureCategory.DAEMON_LEAK],
            patches=[PatchType.SANDBOX_CONSTRAINT],
            state_variables=["chaos_level", "constraint_strength", "virtue_progress"],
            key_agents=["Sun_Wukong", "Tripitaka", "Buddha", "Pigsy", "Sandy"],
            information_encoded=[
                "Sun Wukong as misaligned kernel exploit: invulnerable, fast",
                "Buddha's five-finger mountain = hard sandbox constraint",
                "Pilgrimage as curriculum of encounters = fuzz-testing defenses",
                "Procedure for turning chaotic exploit into loyal guardian daemon"
            ],
            approximate_date="1592 CE"
        ))
        
        self.register(EpicEntry(
            name="Romance of Three Kingdoms",
            culture="China",
            system_designation="Warlord_Network_Sim",
            domain=SystemDomain.POLITY,
            objective="Explore long-term dynamics of fragmented sovereignty and betrayal",
            failure_modes=[FailureCategory.LEGITIMACY_LOSS, FailureCategory.RESOURCE_CONTENTION],
            patches=[PatchType.COALITION_PROTOCOL],
            state_variables=["guanxi_network", "territorial_control", "loyalty_edges"],
            key_agents=["Liu_Bei", "Cao_Cao", "Sun_Quan", "Zhuge_Liang", "Guan_Yu"],
            information_encoded=[
                "Dozens of warlord nodes with variable loyalty edges",
                "Guanxi as high-dimensional state > territorial maps",
                "Multiple optimal strategies depending on time horizon",
                "Library of political exploits and counter-exploits"
            ],
            approximate_date="1400 CE"
        ))
        
        # =====================================================================
        # JAPANESE
        # =====================================================================
        
        self.register(EpicEntry(
            name="Tale of the Heike",
            culture="Japan",
            system_designation="Impermanence_Logger",
            domain=SystemDomain.POLITY,
            objective="Encode the lifecycle of power under the law of impermanence (mujo)",
            failure_modes=[FailureCategory.LEGITIMACY_LOSS],
            patches=[],  # Impermanence is the lesson
            state_variables=["power_level", "attachment", "mujo_awareness"],
            key_agents=["Taira_Kiyomori", "Minamoto_Yoshitsune", "Retired_Emperor"],
            information_encoded=[
                "Rise and fall of Taira clan as complete power-cycle trace",
                "Emphasis on sound as acoustic encoding of Buddhist law",
                "Military and aristocratic elites degrade under attachment",
                "No dominance is permanent; only stable asset is how you carry loss"
            ],
            approximate_date="1371 CE"
        ))
        
        # =====================================================================
        # CELTIC/ARTHURIAN
        # =====================================================================
        
        self.register(EpicEntry(
            name="Arthurian Cycle",
            culture="Celtic/European",
            system_designation="Round_Table_Protocol",
            domain=SystemDomain.FEDERATION,
            objective="Create governance where peers of high power share without destroying each other",
            failure_modes=[FailureCategory.LEGITIMACY_LOSS, FailureCategory.RESOURCE_CONTENTION],
            patches=[PatchType.COALITION_PROTOCOL],
            state_variables=["table_symmetry", "grail_proximity", "loyalty_triangles"],
            key_agents=["Arthur", "Lancelot", "Guinevere", "Galahad", "Mordred"],
            information_encoded=[
                "Round table = symmetry: no privileged visual center",
                "Grail quest as universal attractor: not everyone is ready",
                "Love triangles show how personal bonds break structural symmetry",
                "Design guidelines for elite orders + inevitable fault-lines"
            ],
            approximate_date="1200 CE"
        ))
        
        # =====================================================================
        # FRENCH
        # =====================================================================
        
        self.register(EpicEntry(
            name="Chanson de Roland",
            culture="French",
            system_designation="Overconfidence_Test",
            domain=SystemDomain.CONFLICT,
            objective="Log failure mode where honor > information",
            failure_modes=[FailureCategory.OVERCONFIDENCE],
            patches=[],  # Warning only
            state_variables=["honor_priority", "information_flow", "alert_threshold"],
            key_agents=["Roland", "Oliver", "Charlemagne", "Ganelon"],
            information_encoded=[
                "Roland refuses to blow horn until too late = pride bug",
                "Ambush at Roncevaux shows single-point warning failure",
                "Make it permissible and honorable to raise alarms early"
            ],
            approximate_date="1100 CE"
        ))
    
    def register(self, epic: EpicEntry) -> None:
        """Register an epic in the registry."""
        self._epics[epic.name] = epic
    
    def get(self, name: str) -> Optional[EpicEntry]:
        """Get an epic by name."""
        return self._epics.get(name)
    
    def get_by_domain(self, domain: SystemDomain) -> List[EpicEntry]:
        """Get all epics for a given domain."""
        return [e for e in self._epics.values() if e.domain == domain]
    
    def get_by_failure_mode(self, mode: FailureCategory) -> List[EpicEntry]:
        """Get all epics encoding a specific failure mode."""
        return [e for e in self._epics.values() if mode in e.failure_modes]
    
    def get_by_patch(self, patch: PatchType) -> List[EpicEntry]:
        """Get all epics providing a specific patch type."""
        return [e for e in self._epics.values() if patch in e.patches]
    
    def get_all_crash_signatures(self) -> List[Dict]:
        """Get all crash signatures from the registry."""
        return [e.get_crash_signature() for e in self._epics.values()]
    
    def get_protocol_library(self) -> Dict[str, EpicEntry]:
        """Get the full protocol library."""
        return {e.get_protocol_name(): e for e in self._epics.values()}
    
    def __len__(self) -> int:
        return len(self._epics)
    
    def __iter__(self):
        return iter(self._epics.values())


# =============================================================================
# GLOBAL REGISTRY
# =============================================================================

EPIC_REGISTRY = EpicRegistry()


# =============================================================================
# VALIDATION
# =============================================================================

def validate_epic_registry() -> bool:
    """Validate epic registry module."""
    
    # Test EpicEntry
    entry = EpicEntry(
        name="Test Epic",
        culture="Test",
        system_designation="Test_Protocol",
        domain=SystemDomain.INDIVIDUAL,
        objective="Test objective",
        failure_modes=[FailureCategory.RAGE_OVERFLOW],
        patches=[PatchType.SOFT_PERSISTENCE]
    )
    
    assert entry.get_protocol_name() == "TEST_EPIC_PROTOCOL"
    
    sig = entry.get_crash_signature()
    assert "epic" in sig
    assert "failure_modes" in sig
    
    # Test EpicRegistry
    registry = EPIC_REGISTRY
    
    assert len(registry) > 10
    
    gilgamesh = registry.get("Epic of Gilgamesh")
    assert gilgamesh is not None
    assert gilgamesh.culture == "Mesopotamia"
    
    iliad = registry.get("Iliad")
    assert iliad is not None
    assert FailureCategory.RAGE_OVERFLOW in iliad.failure_modes
    
    # Test filtering
    conflict_epics = registry.get_by_domain(SystemDomain.CONFLICT)
    assert len(conflict_epics) >= 1
    
    rage_epics = registry.get_by_failure_mode(FailureCategory.RAGE_OVERFLOW)
    assert len(rage_epics) >= 1
    
    # Test protocol library
    protocols = registry.get_protocol_library()
    assert "ILIAD_PROTOCOL" in protocols
    assert "ODYSSEY_PROTOCOL" in protocols
    
    # Test crash signatures
    signatures = registry.get_all_crash_signatures()
    assert len(signatures) == len(registry)
    
    return True


if __name__ == "__main__":
    print("Validating Epic Registry Module...")
    assert validate_epic_registry()
    print("✓ Epic Registry Module validated")
    
    print(f"\nTotal epics registered: {len(EPIC_REGISTRY)}")
    for epic in EPIC_REGISTRY:
        print(f"  - {epic.name} ({epic.culture}): {epic.system_designation}")
