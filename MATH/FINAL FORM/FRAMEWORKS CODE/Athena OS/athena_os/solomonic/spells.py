"""
ATHENA OS - KEY OF SOLOMON COMPUTATIONAL FRAMEWORK
===================================================
Part VI: The Spells (Typed Programs/Operations)

SPELL AS TYPED FUNCTION:
    Spell: (Goal, SpiritScope, PentacleSet, ToolSet, Time, OperatorState, SpaceLayout)
           → NewConfig | Exception(Misfire/NoShow)

PRECONDITIONS:
    Each spell has strict preconditions that must be satisfied:
    - Required Tools
    - Required Pentacles
    - Required Time (planetary day/hour)
    - Required OperatorState (purity threshold)
    - Required SpaceLayout (circle, triangle, labels)

ALGORITHM STRUCTURE:
    1. Normalize operator state (purification)
    2. Instantiate geometry (circle, tools, pentacles)
    3. Invoke global authority (divine names, psalms)
    4. Call the spirit (pattern matching on S_spirits)
    5. Constraint/escalation (if no response)
    6. Tasking (apply τ_i)
    7. License to depart (R_i)

SOURCES:
    Key of Solomon (Clavicula Salomonis)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Set, Callable
from enum import Enum, auto
import numpy as np

# Import from other modules
from .temporal import Planet, PlanetaryHour, PlanetaryDay, TimePredicate
from .pentacles import PentacleSpec, PentacleLibrary, EffectType
from .spirits import Spirit, SpiritRegistry, SpiritState, FunctionDomain
from .operator import OperatorState, PurityLevel, PurificationProtocol


# =============================================================================
# SPELL TYPES
# =============================================================================

class SpellCategory(Enum):
    """Categories of spells/experiments."""
    
    INVOCATION = ("calling", "Summon and bind spirits")
    DIVINATION = ("knowing", "Obtain hidden knowledge")
    PROTECTION = ("warding", "Defense and shielding")
    BINDING = ("constraint", "Compel obedience")
    TRANSFORMATION = ("change", "Alter circumstances")
    DESTRUCTION = ("banishing", "Remove enemies/obstacles")
    FAVOR = ("attraction", "Win love/friendship")
    WEALTH = ("prosperity", "Material abundance")
    INVISIBILITY = ("concealment", "Avoid detection")
    HEALING = ("restoration", "Cure illness")
    
    def __init__(self, short_name: str, description: str):
        self.short_name = short_name
        self._description = description


class SpellResult(Enum):
    """Possible spell outcomes."""
    
    SUCCESS = ("complete", "Spell completed successfully")
    PARTIAL = ("partial", "Partial effect achieved")
    FAILURE = ("failed", "Spell failed to produce effect")
    MISFIRE = ("misfire", "Spell produced unintended effect")
    BACKFIRE = ("backfire", "Spell harmed the operator")
    CANCELLED = ("cancelled", "Spell was cancelled")
    
    def __init__(self, code: str, description: str):
        self.code = code
        self._description = description
    
    @property
    def is_positive(self) -> bool:
        return self in [SpellResult.SUCCESS, SpellResult.PARTIAL]


# =============================================================================
# SPELL SPECIFICATION
# =============================================================================

@dataclass
class SpellSpec:
    """
    Specification for a spell/experiment.
    
    Defines the type signature and preconditions.
    """
    
    # Identity
    name: str
    category: SpellCategory
    
    # Goal
    goal_description: str
    
    # Requirements
    required_purity: PurityLevel = PurityLevel.MODERATE
    required_authority: int = 5
    
    # Planetary requirements
    valid_planets: List[Planet] = field(default_factory=list)
    
    # Pentacles required
    required_pentacles: List[str] = field(default_factory=list)
    
    # Tools required
    required_tools: List[str] = field(default_factory=list)
    
    # Spirit scope (which spirits can fulfill this)
    spirit_domains: List[FunctionDomain] = field(default_factory=list)
    
    # Geometry required
    requires_circle: bool = True
    requires_triangle: bool = False
    
    @property
    def id(self) -> str:
        """Unique spell ID."""
        return self.name.upper().replace(" ", "_")


# =============================================================================
# SPELL INSTANCE
# =============================================================================

@dataclass
class SpellInstance:
    """
    A running instance of a spell.
    
    Tracks state through the execution pipeline.
    """
    
    spec: SpellSpec
    
    # Execution state
    phase: str = "INITIALIZED"
    result: Optional[SpellResult] = None
    
    # Bound resources
    operator: Optional[OperatorState] = None
    spirits: List[Spirit] = field(default_factory=list)
    pentacles: List[PentacleSpec] = field(default_factory=list)
    
    # Configuration
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Execution log
    log: List[str] = field(default_factory=list)
    
    def _log(self, message: str):
        """Add message to execution log."""
        self.log.append(f"[{self.phase}] {message}")
    
    # -------------------------------------------------------------------------
    # EXECUTION PHASES
    # -------------------------------------------------------------------------
    
    def check_preconditions(self, operator: OperatorState,
                           current_planet: Planet) -> Tuple[bool, List[str]]:
        """
        Check all preconditions before execution.
        """
        errors = []
        
        # Check purity
        if operator.purity_level.level < self.spec.required_purity.level:
            errors.append(f"Insufficient purity: need {self.spec.required_purity.name}")
        
        # Check authority
        if operator.authority_level < self.spec.required_authority:
            errors.append(f"Insufficient authority: need {self.spec.required_authority}")
        
        # Check planetary timing
        if self.spec.valid_planets and current_planet not in self.spec.valid_planets:
            valid = ", ".join(p.name for p in self.spec.valid_planets)
            errors.append(f"Wrong planetary timing: valid planets are {valid}")
        
        return (len(errors) == 0, errors)
    
    def phase_1_normalize(self, operator: OperatorState) -> bool:
        """
        Phase 1: Normalize operator state.
        
        P_pure: S_op → S_op^pure
        """
        self.phase = "NORMALIZE"
        self._log("Beginning operator normalization")
        
        self.operator = operator
        operator.refresh()
        
        if operator.is_pure():
            self._log(f"Operator already pure: {operator.purity_level.name}")
            return True
        
        # Apply purification
        protocol = PurificationProtocol()
        success, messages = protocol.execute_full(operator)
        
        for msg in messages:
            self._log(msg)
        
        operator.refresh()
        self._log(f"Final purity: {operator.purity_level.name}")
        
        return operator.purity_level.level >= self.spec.required_purity.level
    
    def phase_2_geometry(self) -> bool:
        """
        Phase 2: Instantiate geometry.
        
        Set up circle, triangle, tools, pentacles.
        """
        self.phase = "GEOMETRY"
        self._log("Setting up ritual geometry")
        
        if self.spec.requires_circle:
            self.config["circle_active"] = True
            self._log("Magic circle inscribed")
        
        if self.spec.requires_triangle:
            self.config["triangle_active"] = True
            self._log("Triangle of Art prepared")
        
        # Record pentacles
        for pentacle_id in self.spec.required_pentacles:
            self._log(f"Pentacle activated: {pentacle_id}")
        
        # Record tools
        for tool in self.spec.required_tools:
            self._log(f"Tool prepared: {tool}")
        
        self.config["geometry_complete"] = True
        return True
    
    def phase_3_authority(self) -> bool:
        """
        Phase 3: Invoke global authority.
        
        Recite divine names and psalms.
        """
        self.phase = "AUTHORITY"
        self._log("Invoking divine authority")
        
        # Invoke divine names
        divine_names = ["YHVH", "ADONAI", "EHEIEH", "AGLA"]
        for name in divine_names:
            self._log(f"Name invoked: {name}")
        
        # Recite psalms
        psalms = ["Psalm 51", "Psalm 91", "Psalm 72"]
        for psalm in psalms:
            self._log(f"Recited: {psalm}")
        
        self.config["authority_invoked"] = True
        return True
    
    def phase_4_call(self, registry: SpiritRegistry) -> bool:
        """
        Phase 4: Call the spirit(s).
        
        σ_call: Pattern match on S_spirits
        """
        self.phase = "CALL"
        self._log("Calling spirits")
        
        # Find appropriate spirits for this spell
        candidates = []
        for domain in self.spec.spirit_domains:
            candidates.extend(registry.get_by_domain(domain))
        
        if not candidates:
            self._log("No appropriate spirits found")
            return False
        
        # Create and summon first available
        spirit_spec = candidates[0]
        spirit = registry.create_spirit(spirit_spec.name)
        
        if not spirit:
            self._log(f"Failed to create spirit: {spirit_spec.name}")
            return False
        
        self._log(f"Spirit selected: {spirit.name}")
        
        # Summon
        success, msg = spirit.summon()
        self._log(msg)
        
        if not success:
            return False
        
        # Manifest
        success, msg = spirit.manifest(success_prob=0.8)
        self._log(msg)
        
        self.spirits.append(spirit)
        return spirit.state in [SpiritState.PRESENT, SpiritState.HOSTILE]
    
    def phase_5_bind(self) -> bool:
        """
        Phase 5: Bind/escalate.
        
        B_i: Binding operator with escalation loop.
        """
        self.phase = "BIND"
        
        if not self.spirits:
            self._log("No spirits to bind")
            return False
        
        for spirit in self.spirits:
            self._log(f"Binding {spirit.name}")
            
            # Attempt binding
            authority = self.operator.authority_level if self.operator else 5
            success, msg = spirit.bind(authority, ["YHVH", "ADONAI", "AGLA"])
            self._log(msg)
            
            # Escalation loop if hostile
            escalation = 0
            while spirit.state == SpiritState.HOSTILE and escalation < 3:
                self._log(f"Spirit hostile, escalating ({escalation + 1}/3)")
                success, msg = spirit.escalate()
                self._log(msg)
                
                if spirit.state != SpiritState.HOSTILE:
                    # Re-attempt binding
                    success, msg = spirit.bind(authority, ["YHVH", "SHADDAI"])
                    self._log(msg)
                
                escalation += 1
            
            if spirit.state != SpiritState.BOUND:
                self._log(f"Failed to bind {spirit.name}")
                return False
        
        return True
    
    def phase_6_task(self) -> bool:
        """
        Phase 6: Assign task.
        
        τ_i: Tasking operator.
        """
        self.phase = "TASK"
        
        for spirit in self.spirits:
            self._log(f"Tasking {spirit.name}")
            
            success, msg = spirit.assign_task(self.spec.goal_description)
            self._log(msg)
            
            if not success:
                return False
            
            # Work on task
            while spirit.task_progress < 1.0:
                success, msg = spirit.work_task(0.25)
                self._log(msg)
        
        return True
    
    def phase_7_release(self) -> bool:
        """
        Phase 7: License to depart.
        
        R_i: Release operator.
        """
        self.phase = "RELEASE"
        
        for spirit in self.spirits:
            self._log(f"Releasing {spirit.name}")
            
            success, msg = spirit.release()
            self._log(msg)
            
            if not success:
                # Force banishment if release fails
                self._log(f"Release failed, banishing")
                success, msg = spirit.banish()
                self._log(msg)
        
        # Teardown geometry
        self._log("Tearing down ritual geometry")
        self.config["circle_active"] = False
        self.config["triangle_active"] = False
        
        # Closing prayers
        self._log("Closing thanksgiving prayers recited")
        
        return True
    
    # -------------------------------------------------------------------------
    # MAIN EXECUTION
    # -------------------------------------------------------------------------
    
    def execute(self, operator: OperatorState,
                registry: SpiritRegistry,
                current_planet: Planet) -> SpellResult:
        """
        Execute the complete spell.
        
        Returns: SpellResult
        """
        self.phase = "CHECKING"
        self._log(f"Beginning spell: {self.spec.name}")
        
        # Check preconditions
        valid, errors = self.check_preconditions(operator, current_planet)
        if not valid:
            for error in errors:
                self._log(f"Precondition failed: {error}")
            self.result = SpellResult.FAILURE
            return self.result
        
        try:
            # Phase 1: Normalize
            if not self.phase_1_normalize(operator):
                self._log("Normalization failed")
                self.result = SpellResult.FAILURE
                return self.result
            
            # Phase 2: Geometry
            if not self.phase_2_geometry():
                self._log("Geometry setup failed")
                self.result = SpellResult.FAILURE
                return self.result
            
            # Phase 3: Authority
            if not self.phase_3_authority():
                self._log("Authority invocation failed")
                self.result = SpellResult.FAILURE
                return self.result
            
            # Phase 4: Call
            if not self.phase_4_call(registry):
                self._log("Spirit calling failed")
                self.result = SpellResult.FAILURE
                return self.result
            
            # Phase 5: Bind
            if not self.phase_5_bind():
                self._log("Binding failed")
                self.result = SpellResult.FAILURE
                return self.result
            
            # Phase 6: Task
            if not self.phase_6_task():
                self._log("Tasking failed")
                self.result = SpellResult.PARTIAL
                self.phase_7_release()
                return self.result
            
            # Phase 7: Release
            if not self.phase_7_release():
                self._log("Release incomplete")
                self.result = SpellResult.PARTIAL
                return self.result
            
            # Success!
            self.phase = "COMPLETE"
            self._log("Spell completed successfully")
            self.result = SpellResult.SUCCESS
            return self.result
            
        except Exception as e:
            self._log(f"Exception: {str(e)}")
            self.result = SpellResult.MISFIRE
            # Attempt emergency cleanup
            self.phase_7_release()
            return self.result


# =============================================================================
# SPELL LIBRARY
# =============================================================================

# Predefined spells from the Key of Solomon
SPELL_LIBRARY = [
    SpellSpec(
        name="Invocation of Knowledge",
        category=SpellCategory.DIVINATION,
        goal_description="Obtain hidden knowledge and secrets",
        required_purity=PurityLevel.SUBSTANTIAL,
        required_authority=6,
        valid_planets=[Planet.MERCURY, Planet.MOON],
        required_pentacles=["MERCURY_3", "MERCURY_4"],
        required_tools=["wand", "incense"],
        spirit_domains=[FunctionDomain.KNOWLEDGE, FunctionDomain.DIVINATION],
    ),
    SpellSpec(
        name="Experiment of Invisibility",
        category=SpellCategory.INVISIBILITY,
        goal_description="Render oneself invisible to enemies",
        required_purity=PurityLevel.COMPLETE,
        required_authority=7,
        valid_planets=[Planet.SUN, Planet.MOON],
        required_pentacles=["SUN_4", "SUN_6"],
        required_tools=["ring", "lamp"],
        spirit_domains=[FunctionDomain.TRANSFORMATION],
    ),
    SpellSpec(
        name="For Love and Favor",
        category=SpellCategory.FAVOR,
        goal_description="Win the love and friendship of a person",
        required_purity=PurityLevel.MODERATE,
        required_authority=5,
        valid_planets=[Planet.VENUS],
        required_pentacles=["VENUS_1", "VENUS_3"],
        required_tools=["parchment", "dove_feather"],
        spirit_domains=[FunctionDomain.LOVE],
    ),
    SpellSpec(
        name="Against Adversaries",
        category=SpellCategory.PROTECTION,
        goal_description="Protection against enemies and plots",
        required_purity=PurityLevel.SUBSTANTIAL,
        required_authority=6,
        valid_planets=[Planet.SATURN, Planet.MARS],
        required_pentacles=["SATURN_2", "SATURN_3", "MARS_4"],
        required_tools=["sword", "shield"],
        spirit_domains=[FunctionDomain.PROTECTION, FunctionDomain.BINDING],
    ),
    SpellSpec(
        name="For Riches and Treasure",
        category=SpellCategory.WEALTH,
        goal_description="Acquire wealth, riches, and honor",
        required_purity=PurityLevel.SUBSTANTIAL,
        required_authority=6,
        valid_planets=[Planet.JUPITER, Planet.SUN],
        required_pentacles=["JUPITER_2", "JUPITER_4"],
        required_tools=["gold_coin", "incense"],
        spirit_domains=[FunctionDomain.WEALTH],
    ),
    SpellSpec(
        name="For Opening Locks",
        category=SpellCategory.TRANSFORMATION,
        goal_description="Open any lock or barrier",
        required_purity=PurityLevel.MODERATE,
        required_authority=5,
        valid_planets=[Planet.MERCURY, Planet.MOON],
        required_pentacles=["MERCURY_5", "MOON_1"],
        required_tools=["key", "wand"],
        spirit_domains=[FunctionDomain.TRANSFORMATION],
    ),
    SpellSpec(
        name="Spirit Binding",
        category=SpellCategory.BINDING,
        goal_description="Bind a spirit to obedience",
        required_purity=PurityLevel.COMPLETE,
        required_authority=8,
        valid_planets=[Planet.SATURN],
        required_pentacles=["SATURN_1", "SATURN_6"],
        required_tools=["chain", "sword", "circle"],
        spirit_domains=[FunctionDomain.BINDING],
        requires_triangle=True,
    ),
    SpellSpec(
        name="For Healing",
        category=SpellCategory.HEALING,
        goal_description="Cure illness and restore health",
        required_purity=PurityLevel.SUBSTANTIAL,
        required_authority=6,
        valid_planets=[Planet.SUN, Planet.JUPITER],
        required_pentacles=["MARS_2", "JUPITER_6"],
        required_tools=["oil", "herbs"],
        spirit_domains=[FunctionDomain.HEALING],
    ),
]


@dataclass
class SpellBook:
    """
    Collection of spells with execution capabilities.
    """
    
    spells: List[SpellSpec] = field(default_factory=lambda: SPELL_LIBRARY.copy())
    
    def get_spell(self, name: str) -> Optional[SpellSpec]:
        """Get spell by name."""
        for spell in self.spells:
            if spell.name.lower() == name.lower():
                return spell
        return None
    
    def get_by_category(self, category: SpellCategory) -> List[SpellSpec]:
        """Get spells by category."""
        return [s for s in self.spells if s.category == category]
    
    def get_for_planet(self, planet: Planet) -> List[SpellSpec]:
        """Get spells valid for a planet."""
        return [s for s in self.spells 
                if not s.valid_planets or planet in s.valid_planets]
    
    def cast(self, spell_name: str,
             operator: OperatorState,
             registry: SpiritRegistry,
             current_planet: Planet) -> Tuple[SpellResult, List[str]]:
        """
        Cast a spell by name.
        
        Returns: (result, execution_log)
        """
        spec = self.get_spell(spell_name)
        if not spec:
            return (SpellResult.FAILURE, [f"Unknown spell: {spell_name}"])
        
        instance = SpellInstance(spec=spec)
        result = instance.execute(operator, registry, current_planet)
        
        return (result, instance.log)


# =============================================================================
# VALIDATION
# =============================================================================

def validate_spells() -> bool:
    """Validate the spells module."""
    
    # Test SpellSpec
    spec = SpellSpec(
        name="Test Spell",
        category=SpellCategory.DIVINATION,
        goal_description="Test goal",
        required_purity=PurityLevel.MINIMAL,
        required_authority=3,
        valid_planets=[Planet.MERCURY],
        spirit_domains=[FunctionDomain.KNOWLEDGE],
    )
    assert spec.id == "TEST_SPELL"
    
    # Test SpellInstance
    instance = SpellInstance(spec=spec)
    
    # Test precondition checking
    operator = OperatorState()
    operator.purity_level = PurityLevel.MODERATE
    operator.authority_level = 5
    
    valid, errors = instance.check_preconditions(operator, Planet.MERCURY)
    assert valid
    
    # Test with wrong planet
    valid, errors = instance.check_preconditions(operator, Planet.SATURN)
    assert not valid
    
    # Test SpellBook
    book = SpellBook()
    assert len(book.spells) > 0
    
    knowledge_spell = book.get_spell("Invocation of Knowledge")
    assert knowledge_spell is not None
    
    div_spells = book.get_by_category(SpellCategory.DIVINATION)
    assert len(div_spells) > 0
    
    # Test full execution
    registry = SpiritRegistry()
    operator = OperatorState()
    
    result, log = book.cast("For Love and Favor", operator, registry, Planet.VENUS)
    assert result is not None
    assert len(log) > 0
    
    return True


if __name__ == "__main__":
    print("Validating Spells Module...")
    assert validate_spells()
    print("✓ Spells module validated")
    
    # Demo
    print("\n--- Spell Casting Demo ---")
    
    book = SpellBook()
    registry = SpiritRegistry()
    operator = OperatorState()
    
    print("\nAvailable spells:")
    for spell in book.spells[:5]:
        planets = ", ".join(p.name for p in spell.valid_planets) if spell.valid_planets else "Any"
        print(f"  {spell.name} ({spell.category.name})")
        print(f"    Planets: {planets}")
        print(f"    Required authority: {spell.required_authority}")
    
    print("\nCasting 'Invocation of Knowledge'...")
    result, log = book.cast("Invocation of Knowledge", operator, registry, Planet.MERCURY)
    
    print(f"\nResult: {result.name}")
    print("\nExecution log:")
    for entry in log[-10:]:
        print(f"  {entry}")
