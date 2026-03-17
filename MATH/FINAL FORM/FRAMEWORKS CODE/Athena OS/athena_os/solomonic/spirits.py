"""
ATHENA OS - KEY OF SOLOMON COMPUTATIONAL FRAMEWORK
===================================================
Part IV: The Spirit Model (Semi-Autonomous Processes)

SPIRIT AS TYPED PROCESS:
    Each spirit is modeled as a typed process with:
    - f_i: Function class (domain of action)
    - ρ_i: Typical location (manifestation context)
    - μ_i: Mitigation operator (countermeasures)

STATE SPACE:
    S_sp = Π S_i where each S_i ∈ {inactive, latent, present, bound, hostile, tasked, released}

OPERATORS:
    - σ_i: Selection operator (target specific spirit)
    - B_i: Binding operator (constrain to bound subspace)
    - τ_i: Tasking operator (modify environment)
    - R_i: Release operator (license to depart)

THE CONJURATION PROTOCOL:
    1. inactive/latent → present
    2. present → bound
    3. bound + task → tasked
    4. tasked → released (via R_i)

SOURCES:
    Key of Solomon (Clavicula Salomonis)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Set, Callable
from enum import Enum, auto
import numpy as np

# Import from temporal
from .temporal import Planet


# =============================================================================
# SPIRIT STATES
# =============================================================================

class SpiritState(Enum):
    """States a spirit can occupy."""
    
    INACTIVE = ("dormant", 0, "Not engaged in any interaction")
    LATENT = ("potential", 1, "Capable of being called but not active")
    SUMMONED = ("called", 2, "Invocation initiated, awaiting manifestation")
    PRESENT = ("manifest", 3, "Actively present in the ritual space")
    BOUND = ("constrained", 4, "Under operator's authority")
    HOSTILE = ("resistant", 5, "Present but resisting constraints")
    TASKED = ("working", 6, "Executing assigned task")
    RELEASED = ("departed", 7, "Properly dismissed")
    BANISHED = ("expelled", 8, "Forcibly removed")
    
    def __init__(self, description: str, level: int, explanation: str):
        self.description = description
        self.level = level
        self.explanation = explanation
    
    @property
    def is_active(self) -> bool:
        """Check if spirit is in an active state."""
        return self in [SpiritState.PRESENT, SpiritState.BOUND, 
                       SpiritState.HOSTILE, SpiritState.TASKED]
    
    @property
    def is_safe(self) -> bool:
        """Check if state is safe for operator."""
        return self in [SpiritState.INACTIVE, SpiritState.LATENT,
                       SpiritState.BOUND, SpiritState.TASKED, 
                       SpiritState.RELEASED]


class SpiritClass(Enum):
    """Classes of spirits by hierarchy."""
    
    CELESTIAL = ("highest", 9, "Angels, Archangels")
    PLANETARY = ("middle", 7, "Planetary Intelligences")
    ELEMENTAL = ("lower", 5, "Elemental beings")
    CHTHONIC = ("infernal", 3, "Underworld entities")
    AERIAL = ("middle-low", 4, "Spirits of the air")
    
    def __init__(self, rank: str, authority_level: int, description: str):
        self.rank = rank
        self.authority_level = authority_level
        self._description = description


class FunctionDomain(Enum):
    """Domains of spirit function/expertise."""
    
    KNOWLEDGE = ("revelation", "Hidden information, sciences")
    WEALTH = ("prosperity", "Material abundance, treasure")
    LOVE = ("attraction", "Relationships, affection")
    PROTECTION = ("defense", "Guarding, warding")
    DESTRUCTION = ("harm", "Enemies, obstacles")
    HEALING = ("restoration", "Illness, injury")
    TRANSFORMATION = ("change", "Alteration of circumstances")
    TRANSPORTATION = ("movement", "Travel, teleportation")
    BINDING = ("constraint", "Compelling obedience")
    DIVINATION = ("foresight", "Future events, prophecy")
    
    def __init__(self, category: str, description: str):
        self.category = category
        self._description = description


# =============================================================================
# SPIRIT SPECIFICATION
# =============================================================================

@dataclass
class SpiritSpec:
    """
    Specification for a spirit entity.
    
    Parameters:
    - f_i: function class (domain)
    - ρ_i: typical location
    - μ_i: mitigation measures
    """
    
    # Identity
    name: str
    rank: SpiritClass
    
    # Function class (f_i)
    domains: List[FunctionDomain] = field(default_factory=list)
    
    # Planetary correspondence
    planet: Optional[Planet] = None
    
    # Authority required to command
    authority_required: int = 5  # 1-10 scale
    
    # Mitigation (μ_i)
    mitigations: List[str] = field(default_factory=list)
    
    # Names that compel obedience
    binding_names: List[str] = field(default_factory=list)
    
    @property
    def id(self) -> str:
        """Unique spirit ID."""
        return self.name.upper().replace(" ", "_")
    
    def requires_authority(self, operator_authority: int) -> bool:
        """Check if operator has sufficient authority."""
        return operator_authority >= self.authority_required


# =============================================================================
# SPIRIT STATE MACHINE
# =============================================================================

@dataclass 
class Spirit:
    """
    A spirit instance with state.
    
    Implements the spirit state machine with transition operators.
    """
    
    spec: SpiritSpec
    state: SpiritState = SpiritState.INACTIVE
    
    # Task state
    current_task: Optional[str] = None
    task_progress: float = 0.0
    
    # Binding state
    binding_strength: float = 0.0
    binding_names_invoked: List[str] = field(default_factory=list)
    
    # Hostility tracking
    hostility_level: float = 0.0
    escalation_count: int = 0
    
    @property
    def id(self) -> str:
        return self.spec.id
    
    @property
    def name(self) -> str:
        return self.spec.name
    
    # -------------------------------------------------------------------------
    # STATE TRANSITIONS
    # -------------------------------------------------------------------------
    
    def summon(self) -> Tuple[bool, str]:
        """
        σ_call: Initiate summoning.
        
        INACTIVE/LATENT → SUMMONED
        """
        if self.state not in [SpiritState.INACTIVE, SpiritState.LATENT]:
            return (False, f"Cannot summon from state {self.state.name}")
        
        self.state = SpiritState.SUMMONED
        return (True, f"{self.name} summoned")
    
    def manifest(self, success_prob: float = 0.8) -> Tuple[bool, str]:
        """
        Transition from SUMMONED to PRESENT or HOSTILE.
        
        Success probability affected by timing, authority, etc.
        """
        if self.state != SpiritState.SUMMONED:
            return (False, f"Cannot manifest from state {self.state.name}")
        
        if np.random.random() < success_prob:
            self.state = SpiritState.PRESENT
            return (True, f"{self.name} manifested successfully")
        else:
            # Spirit resists - enters hostile state
            self.state = SpiritState.HOSTILE
            self.hostility_level = 0.5
            return (False, f"{self.name} manifested but is hostile")
    
    def bind(self, authority_level: int, 
             names_invoked: List[str] = None) -> Tuple[bool, str]:
        """
        B_i: Binding operator.
        
        PRESENT/HOSTILE → BOUND
        """
        if self.state not in [SpiritState.PRESENT, SpiritState.HOSTILE]:
            return (False, f"Cannot bind from state {self.state.name}")
        
        if not self.spec.requires_authority(authority_level):
            return (False, "Insufficient authority to bind")
        
        # Calculate binding strength
        names_invoked = names_invoked or []
        self.binding_names_invoked = names_invoked
        
        # Base strength from authority
        base_strength = authority_level / 10.0
        
        # Bonus from using correct binding names
        name_bonus = 0.0
        for name in names_invoked:
            if name in self.spec.binding_names:
                name_bonus += 0.1
        
        self.binding_strength = min(1.0, base_strength + name_bonus)
        
        # Check if binding succeeds
        if self.binding_strength >= 0.5 - (self.hostility_level * 0.2):
            self.state = SpiritState.BOUND
            self.hostility_level = 0.0
            return (True, f"{self.name} bound with strength {self.binding_strength:.2f}")
        else:
            # Binding fails, spirit remains hostile
            self.hostility_level += 0.1
            return (False, f"Binding failed, hostility increased to {self.hostility_level:.2f}")
    
    def escalate(self) -> Tuple[bool, str]:
        """
        Apply escalation (stronger conjurations, curses).
        
        Increases pressure on hostile spirits.
        """
        if self.state != SpiritState.HOSTILE:
            return (False, "Escalation only applies to hostile spirits")
        
        self.escalation_count += 1
        
        # Each escalation reduces hostility but risks banishment
        self.hostility_level = max(0, self.hostility_level - 0.15)
        
        if self.escalation_count >= 3 and self.hostility_level > 0.3:
            # Spirit may need to be banished
            return (False, "Maximum escalation reached, consider banishment")
        
        if self.hostility_level <= 0.2:
            # Spirit submits
            self.state = SpiritState.PRESENT
            return (True, f"{self.name} submits after {self.escalation_count} escalations")
        
        return (True, f"Escalation applied, hostility now {self.hostility_level:.2f}")
    
    def assign_task(self, task: str) -> Tuple[bool, str]:
        """
        τ_i: Tasking operator.
        
        BOUND → TASKED
        """
        if self.state != SpiritState.BOUND:
            return (False, f"Cannot task from state {self.state.name}")
        
        if self.binding_strength < 0.3:
            return (False, "Binding too weak for tasking")
        
        self.current_task = task
        self.task_progress = 0.0
        self.state = SpiritState.TASKED
        
        return (True, f"{self.name} tasked: {task}")
    
    def work_task(self, progress: float = 0.25) -> Tuple[bool, str]:
        """
        Advance task progress.
        """
        if self.state != SpiritState.TASKED:
            return (False, "Spirit is not currently tasked")
        
        self.task_progress = min(1.0, self.task_progress + progress)
        
        if self.task_progress >= 1.0:
            return (True, f"Task '{self.current_task}' completed")
        
        return (True, f"Task progress: {self.task_progress*100:.0f}%")
    
    def release(self) -> Tuple[bool, str]:
        """
        R_i: Release operator (License to Depart).
        
        BOUND/TASKED → RELEASED
        """
        if self.state not in [SpiritState.BOUND, SpiritState.TASKED]:
            return (False, f"Cannot release from state {self.state.name}")
        
        if self.state == SpiritState.TASKED and self.task_progress < 1.0:
            return (False, "Task not yet complete")
        
        self.state = SpiritState.RELEASED
        self.current_task = None
        self.binding_strength = 0.0
        self.binding_names_invoked = []
        
        return (True, f"{self.name} released with license to depart")
    
    def banish(self) -> Tuple[bool, str]:
        """
        Forcible banishment.
        
        Any active state → BANISHED
        """
        if not self.state.is_active and self.state != SpiritState.SUMMONED:
            return (False, f"Cannot banish from state {self.state.name}")
        
        self.state = SpiritState.BANISHED
        self.current_task = None
        self.binding_strength = 0.0
        self.hostility_level = 0.0
        
        return (True, f"{self.name} forcibly banished")
    
    def reset(self):
        """Reset to inactive state."""
        self.state = SpiritState.INACTIVE
        self.current_task = None
        self.task_progress = 0.0
        self.binding_strength = 0.0
        self.binding_names_invoked = []
        self.hostility_level = 0.0
        self.escalation_count = 0
    
    # -------------------------------------------------------------------------
    # STATUS
    # -------------------------------------------------------------------------
    
    def status(self) -> Dict[str, Any]:
        """Get current status."""
        return {
            "name": self.name,
            "state": self.state.name,
            "is_active": self.state.is_active,
            "is_safe": self.state.is_safe,
            "binding_strength": self.binding_strength,
            "hostility_level": self.hostility_level,
            "current_task": self.current_task,
            "task_progress": self.task_progress,
            "escalation_count": self.escalation_count,
        }


# =============================================================================
# SPIRIT REGISTRY
# =============================================================================

# Sample spirits from the Solomonic tradition
SAMPLE_SPIRITS = [
    SpiritSpec(
        name="Michael",
        rank=SpiritClass.CELESTIAL,
        domains=[FunctionDomain.PROTECTION, FunctionDomain.KNOWLEDGE],
        planet=Planet.SUN,
        authority_required=9,
        binding_names=["YHVH", "ADONAI"],
    ),
    SpiritSpec(
        name="Gabriel",
        rank=SpiritClass.CELESTIAL,
        domains=[FunctionDomain.KNOWLEDGE, FunctionDomain.DIVINATION],
        planet=Planet.MOON,
        authority_required=9,
        binding_names=["SHADDAI", "EL"],
    ),
    SpiritSpec(
        name="Raphael",
        rank=SpiritClass.CELESTIAL,
        domains=[FunctionDomain.HEALING, FunctionDomain.PROTECTION],
        planet=Planet.MERCURY,
        authority_required=9,
        binding_names=["ELOHIM", "YHVH"],
    ),
    SpiritSpec(
        name="Uriel",
        rank=SpiritClass.CELESTIAL,
        domains=[FunctionDomain.KNOWLEDGE, FunctionDomain.TRANSFORMATION],
        planet=Planet.VENUS,
        authority_required=9,
        binding_names=["ADONAI", "TZABAOTH"],
    ),
    SpiritSpec(
        name="Sachiel",
        rank=SpiritClass.PLANETARY,
        domains=[FunctionDomain.WEALTH, FunctionDomain.KNOWLEDGE],
        planet=Planet.JUPITER,
        authority_required=7,
        binding_names=["EL", "ADONAI"],
    ),
    SpiritSpec(
        name="Anael",
        rank=SpiritClass.PLANETARY,
        domains=[FunctionDomain.LOVE, FunctionDomain.TRANSFORMATION],
        planet=Planet.VENUS,
        authority_required=6,
        binding_names=["YHVH", "ELOHIM"],
    ),
    SpiritSpec(
        name="Samael",
        rank=SpiritClass.PLANETARY,
        domains=[FunctionDomain.DESTRUCTION, FunctionDomain.BINDING],
        planet=Planet.MARS,
        authority_required=8,
        binding_names=["AGLA", "SHADDAI"],
        mitigations=["Iron amulet", "Mars pentacle"],
    ),
    SpiritSpec(
        name="Cassiel",
        rank=SpiritClass.PLANETARY,
        domains=[FunctionDomain.BINDING, FunctionDomain.KNOWLEDGE],
        planet=Planet.SATURN,
        authority_required=8,
        binding_names=["YHVH", "TZABAOTH"],
    ),
    SpiritSpec(
        name="Tiriel",
        rank=SpiritClass.PLANETARY,
        domains=[FunctionDomain.KNOWLEDGE, FunctionDomain.DIVINATION],
        planet=Planet.MERCURY,
        authority_required=6,
        binding_names=["EL", "ELOHIM"],
    ),
    SpiritSpec(
        name="Sorath",
        rank=SpiritClass.PLANETARY,
        domains=[FunctionDomain.WEALTH, FunctionDomain.TRANSFORMATION],
        planet=Planet.SUN,
        authority_required=7,
        binding_names=["SHADDAI", "ADONAI"],
    ),
]


@dataclass
class SpiritRegistry:
    """
    Registry of available spirits.
    """
    
    specs: List[SpiritSpec] = field(default_factory=lambda: SAMPLE_SPIRITS.copy())
    active_spirits: Dict[str, Spirit] = field(default_factory=dict)
    
    def get_spec(self, name: str) -> Optional[SpiritSpec]:
        """Get spirit spec by name."""
        for spec in self.specs:
            if spec.name.lower() == name.lower():
                return spec
        return None
    
    def get_by_planet(self, planet: Planet) -> List[SpiritSpec]:
        """Get spirits by planetary correspondence."""
        return [s for s in self.specs if s.planet == planet]
    
    def get_by_domain(self, domain: FunctionDomain) -> List[SpiritSpec]:
        """Get spirits by function domain."""
        return [s for s in self.specs if domain in s.domains]
    
    def create_spirit(self, name: str) -> Optional[Spirit]:
        """Create a spirit instance from spec."""
        spec = self.get_spec(name)
        if not spec:
            return None
        
        spirit = Spirit(spec=spec)
        self.active_spirits[spirit.id] = spirit
        return spirit
    
    def get_active(self, spirit_id: str) -> Optional[Spirit]:
        """Get active spirit by ID."""
        return self.active_spirits.get(spirit_id)
    
    def dismiss_all(self):
        """Dismiss all active spirits."""
        for spirit in self.active_spirits.values():
            if spirit.state.is_active:
                spirit.banish()
        self.active_spirits.clear()
    
    def check_safety_invariant(self) -> bool:
        """
        Check global safety invariant.
        
        All spirits should be in safe states.
        """
        for spirit in self.active_spirits.values():
            if not spirit.state.is_safe:
                return False
        return True


# =============================================================================
# VALIDATION
# =============================================================================

def validate_spirits() -> bool:
    """Validate the spirits module."""
    
    # Test SpiritSpec
    spec = SpiritSpec(
        name="Test Spirit",
        rank=SpiritClass.PLANETARY,
        domains=[FunctionDomain.KNOWLEDGE],
        planet=Planet.MERCURY,
        authority_required=5,
        binding_names=["YHVH"],
    )
    assert spec.id == "TEST_SPIRIT"
    assert spec.requires_authority(5)
    assert not spec.requires_authority(4)
    
    # Test Spirit state machine
    spirit = Spirit(spec=spec)
    assert spirit.state == SpiritState.INACTIVE
    
    # Summon
    success, _ = spirit.summon()
    assert success
    assert spirit.state == SpiritState.SUMMONED
    
    # Manifest
    spirit.manifest(success_prob=1.0)  # Force success
    assert spirit.state == SpiritState.PRESENT
    
    # Bind
    success, _ = spirit.bind(authority_level=7, names_invoked=["YHVH"])
    assert success
    assert spirit.state == SpiritState.BOUND
    assert spirit.binding_strength > 0.5
    
    # Task
    success, _ = spirit.assign_task("Find hidden knowledge")
    assert success
    assert spirit.state == SpiritState.TASKED
    
    # Work
    for _ in range(4):
        spirit.work_task(0.25)
    assert spirit.task_progress >= 1.0
    
    # Release
    success, _ = spirit.release()
    assert success
    assert spirit.state == SpiritState.RELEASED
    
    # Test SpiritRegistry
    registry = SpiritRegistry()
    assert len(registry.specs) > 0
    
    michael = registry.get_spec("Michael")
    assert michael is not None
    assert michael.rank == SpiritClass.CELESTIAL
    
    jupiter_spirits = registry.get_by_planet(Planet.JUPITER)
    assert len(jupiter_spirits) > 0
    
    spirit = registry.create_spirit("Sachiel")
    assert spirit is not None
    assert spirit.id in registry.active_spirits
    
    assert registry.check_safety_invariant()
    
    return True


if __name__ == "__main__":
    print("Validating Spirits Module...")
    assert validate_spirits()
    print("✓ Spirits module validated")
    
    # Demo
    print("\n--- Spirit System Demo ---")
    
    registry = SpiritRegistry()
    
    print("\nAvailable spirits:")
    for spec in registry.specs[:5]:
        domains = ", ".join(d.name for d in spec.domains)
        print(f"  {spec.name} ({spec.rank.name}): {domains}")
    
    print("\nConjuration sequence:")
    spirit = registry.create_spirit("Sachiel")
    if spirit:
        print(f"  Created: {spirit.name}")
        
        success, msg = spirit.summon()
        print(f"  Summon: {msg}")
        
        success, msg = spirit.manifest(1.0)
        print(f"  Manifest: {msg}")
        
        success, msg = spirit.bind(8, ["EL", "ADONAI"])
        print(f"  Bind: {msg}")
        
        success, msg = spirit.assign_task("Reveal hidden treasure")
        print(f"  Task: {msg}")
        
        for i in range(4):
            success, msg = spirit.work_task(0.25)
            print(f"  Work: {msg}")
        
        success, msg = spirit.release()
        print(f"  Release: {msg}")
        
        print(f"\nFinal state: {spirit.state.name}")
        print(f"Safety invariant: {registry.check_safety_invariant()}")
