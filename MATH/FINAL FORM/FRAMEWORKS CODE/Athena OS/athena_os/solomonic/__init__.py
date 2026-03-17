"""
ATHENA OS - KEY OF SOLOMON COMPUTATIONAL FRAMEWORK
===================================================
Clavicula Salomonis: A Formal Security Model for Ceremonial Invocation

CORE THESIS:
    The Key of Solomon is a controlled-invocation runtime for
    semi-autonomous processes (spirits). It defines:
    - A session-level orchestration function (InvokeSession)
    - Alignment, sandboxing, kernel libraries, capability elevation
    - Tool/agent orchestration with security invariants

CONFIGURATION SPACE:
    C = S_operator × S_spirits × E_space × T
    
    - S_operator: Operator's internal state (purity, focus, intent)
    - S_spirits: Latent processes that can be excited/constrained
    - E_space: Physical layout (circle, triangle, pentacles, tools)
    - T: Discrete time (planetary day/hour, lunar phase)

THE SOLOMONIC OPERATION:
    F: C_valid → C
    Defined only on configs satisfying preconditions (timing, purity, geometry)
    Outside C_valid it's undefined or "unsafe"

MODULES:
    - temporal: Time as gating function (planetary hours, lunar phases)
    - geometry: Sacred space (circles, triangles, pentagrams)
    - pentacles: Kernel operators (44 precompiled subroutines)
    - spirits: Semi-autonomous processes (state machine)
    - operator: Controller interface (purification protocol)
    - spells: Typed programs (complete operations)

SECURITY MODEL:
    The Key of Solomon defines a complete security protocol stack:
    1. Identity/Authority: Purity determines privilege level
    2. Resource Access: Time and planetary correspondences
    3. Sandboxing: Geometry defines trusted/untrusted zones
    4. Safe Interaction: Typed programs with strict ordering
    5. Shutdown/Cleanup: Release + banishing + teardown

SOURCES:
    Key of Solomon (Clavicula Salomonis)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import numpy as np


# =============================================================================
# TEMPORAL MODULE
# =============================================================================

from .temporal import (
    # Types
    Planet,
    LunarPhase,
    
    # Classes
    TimeIndex,
    PlanetaryHour,
    PlanetaryDay,
    TimeWindow,
    TimePredicate,
    TemporalScheduler,
    
    # Data
    PLANETARY_DAYS,
    PLANETARY_HOUR_SEQUENCE,
    
    # Validation
    validate_temporal,
)


# =============================================================================
# GEOMETRY MODULE
# =============================================================================

from .geometry import (
    # Types
    Zone,
    GeometryType,
    DivineName,
    
    # Classes
    BoundaryLabel,
    MagicCircle,
    TriangleOfArt,
    Pentagram,
    GeometricKernel,
    AccessControlMatrix,
    RitualSpace,
    
    # Validation
    validate_geometry,
)


# =============================================================================
# PENTACLES MODULE
# =============================================================================

from .pentacles import (
    # Types
    EffectType,
    GeometricForm,
    
    # Classes
    PentacleSpec,
    PentacleKernel,
    PentacleLibrary,
    
    # Data
    PENTACLE_NAMES,
    PENTACLE_LIBRARY,
    
    # Validation
    validate_pentacles,
)


# =============================================================================
# SPIRITS MODULE
# =============================================================================

from .spirits import (
    # Types
    SpiritState,
    SpiritClass,
    FunctionDomain,
    
    # Classes
    SpiritSpec,
    Spirit,
    SpiritRegistry,
    
    # Data
    SAMPLE_SPIRITS,
    
    # Validation
    validate_spirits,
)


# =============================================================================
# OPERATOR MODULE
# =============================================================================

from .operator import (
    # Types
    PurityLevel,
    AbstractionStatus,
    IntentAlignment,
    
    # Classes
    BodyState,
    MindState,
    IntentState,
    OperatorState,
    PurificationProtocol,
    
    # Validation
    validate_operator,
)


# =============================================================================
# SPELLS MODULE
# =============================================================================

from .spells import (
    # Types
    SpellCategory,
    SpellResult,
    
    # Classes
    SpellSpec,
    SpellInstance,
    SpellBook,
    
    # Data
    SPELL_LIBRARY,
    
    # Validation
    validate_spells,
)


# =============================================================================
# UNIFIED FRAMEWORK
# =============================================================================

@dataclass
class SolomonicFramework:
    """
    The unified Key of Solomon Computational Framework.
    
    A controlled-invocation runtime for semi-autonomous processes.
    
    Integrates:
        - Temporal (time gating)
        - Geometry (sacred space)
        - Pentacles (kernel operators)
        - Spirits (processes)
        - Operator (controller)
        - Spells (typed programs)
    """
    
    # Components
    operator: OperatorState = field(default_factory=OperatorState)
    space: RitualSpace = field(default_factory=RitualSpace)
    pentacle_library: PentacleLibrary = field(default_factory=PentacleLibrary)
    spirit_registry: SpiritRegistry = field(default_factory=SpiritRegistry)
    spell_book: SpellBook = field(default_factory=SpellBook)
    scheduler: TemporalScheduler = field(default_factory=TemporalScheduler)
    
    # Session state
    session_active: bool = False
    current_time: Optional[TimeIndex] = None
    
    # -------------------------------------------------------------------------
    # SESSION MANAGEMENT
    # -------------------------------------------------------------------------
    
    def begin_session(self) -> Tuple[bool, str]:
        """
        Begin a ceremonial session.
        
        Sets up the ritual space and validates timing.
        """
        if self.session_active:
            return (False, "Session already active")
        
        # Get current time
        self.current_time = TimeIndex.now()
        
        # Set up space
        setup = self.space.setup()
        if not setup["circle_consecrated"]:
            return (False, "Failed to consecrate circle")
        
        self.session_active = True
        return (True, f"Session begun at {self.current_time.planetary_day.name} "
                      f"hour of {self.current_time.planetary_hour.name}")
    
    def end_session(self) -> Tuple[bool, str]:
        """
        End the ceremonial session.
        
        Dismisses all spirits and tears down space.
        """
        if not self.session_active:
            return (False, "No active session")
        
        # Dismiss all spirits
        self.spirit_registry.dismiss_all()
        
        # Teardown space
        self.space.teardown()
        
        self.session_active = False
        self.current_time = None
        
        return (True, "Session ended, all spirits released")
    
    # -------------------------------------------------------------------------
    # OPERATOR INTERFACE
    # -------------------------------------------------------------------------
    
    def purify_operator(self) -> Tuple[bool, List[str]]:
        """Execute full purification protocol."""
        protocol = PurificationProtocol()
        return protocol.execute_full(self.operator)
    
    def get_operator_status(self) -> Dict[str, Any]:
        """Get operator status."""
        return self.operator.status()
    
    def get_authority_level(self) -> int:
        """Get current operator authority level."""
        self.operator.refresh()
        return self.operator.authority_level
    
    # -------------------------------------------------------------------------
    # TEMPORAL INTERFACE
    # -------------------------------------------------------------------------
    
    def get_current_time(self) -> TimeIndex:
        """Get current planetary time."""
        if self.current_time:
            return self.current_time
        return TimeIndex.now()
    
    def get_planetary_hours(self, day_index: int = None, count: int = 24) -> List[Dict]:
        """Get planetary hours for a day."""
        if day_index is None:
            day_index = self.get_current_time().day
        return self.scheduler.list_planetary_hours(day_index, count)
    
    def find_next_window(self, planet: Planet, 
                         waxing: bool = None) -> Optional[TimeIndex]:
        """Find next valid time window for a planet."""
        if waxing is not None:
            window = TimeWindow.combined(planet, waxing)
        else:
            window = TimeWindow.planetary(planet)
        return self.scheduler.find_next_valid(window, self.get_current_time())
    
    # -------------------------------------------------------------------------
    # PENTACLE INTERFACE
    # -------------------------------------------------------------------------
    
    def get_pentacles_for_planet(self, planet: Planet) -> List[PentacleSpec]:
        """Get pentacles for a planet."""
        return self.pentacle_library.get_by_planet(planet)
    
    def get_pentacles_for_effect(self, effect: EffectType) -> List[PentacleSpec]:
        """Get pentacles by effect type."""
        return self.pentacle_library.get_by_effect(effect)
    
    def consecrate_pentacle(self, pentacle_id: str) -> bool:
        """Consecrate a pentacle."""
        return self.pentacle_library.consecrate(pentacle_id)
    
    # -------------------------------------------------------------------------
    # SPIRIT INTERFACE
    # -------------------------------------------------------------------------
    
    def get_spirits_for_domain(self, domain: FunctionDomain) -> List[SpiritSpec]:
        """Get spirits for a function domain."""
        return self.spirit_registry.get_by_domain(domain)
    
    def get_spirits_for_planet(self, planet: Planet) -> List[SpiritSpec]:
        """Get spirits for a planet."""
        return self.spirit_registry.get_by_planet(planet)
    
    def invoke_spirit(self, name: str) -> Optional[Spirit]:
        """Create and summon a spirit."""
        spirit = self.spirit_registry.create_spirit(name)
        if spirit:
            spirit.summon()
        return spirit
    
    def check_safety_invariant(self) -> bool:
        """Check if all spirits are in safe states."""
        return self.spirit_registry.check_safety_invariant()
    
    # -------------------------------------------------------------------------
    # SPELL INTERFACE
    # -------------------------------------------------------------------------
    
    def get_available_spells(self) -> List[SpellSpec]:
        """Get all available spells."""
        return self.spell_book.spells
    
    def get_spells_for_category(self, category: SpellCategory) -> List[SpellSpec]:
        """Get spells by category."""
        return self.spell_book.get_by_category(category)
    
    def get_spells_for_current_time(self) -> List[SpellSpec]:
        """Get spells valid for current planetary time."""
        current = self.get_current_time()
        return self.spell_book.get_for_planet(current.planetary_day)
    
    def cast_spell(self, spell_name: str) -> Tuple[SpellResult, List[str]]:
        """
        Cast a spell.
        
        Returns: (result, execution_log)
        """
        if not self.session_active:
            return (SpellResult.FAILURE, ["No active session"])
        
        current = self.get_current_time()
        return self.spell_book.cast(
            spell_name,
            self.operator,
            self.spirit_registry,
            current.planetary_day
        )
    
    # -------------------------------------------------------------------------
    # SUMMARY
    # -------------------------------------------------------------------------
    
    def get_summary(self) -> Dict[str, Any]:
        """Get complete framework summary."""
        self.operator.refresh()
        current = self.get_current_time()
        
        return {
            "session": {
                "active": self.session_active,
                "time": {
                    "day": current.planetary_day.name,
                    "hour": current.planetary_hour.name,
                    "lunar": current.lunar.name,
                },
            },
            "operator": {
                "purity": self.operator.purity_level.name,
                "authority": self.operator.authority_level,
                "is_pure": self.operator.is_pure(),
            },
            "space": self.space.get_status() if self.session_active else {"active": False},
            "pentacles": {
                "total": self.pentacle_library.total_count(),
                "by_planet": self.pentacle_library.count_by_planet(),
            },
            "spirits": {
                "available": len(self.spirit_registry.specs),
                "active": len(self.spirit_registry.active_spirits),
                "safety_ok": self.check_safety_invariant(),
            },
            "spells": {
                "total": len(self.spell_book.spells),
                "valid_now": len(self.get_spells_for_current_time()),
            },
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_solomonic() -> bool:
    """Validate the complete Solomonic module."""
    
    print("Validating Key of Solomon Framework...")
    
    # Run individual validations
    assert validate_temporal(), "Temporal validation failed"
    print("  ✓ Temporal module")
    
    assert validate_geometry(), "Geometry validation failed"
    print("  ✓ Geometry module")
    
    assert validate_pentacles(), "Pentacles validation failed"
    print("  ✓ Pentacles module")
    
    assert validate_spirits(), "Spirits validation failed"
    print("  ✓ Spirits module")
    
    assert validate_operator(), "Operator validation failed"
    print("  ✓ Operator module")
    
    assert validate_spells(), "Spells validation failed"
    print("  ✓ Spells module")
    
    # Test unified framework
    framework = SolomonicFramework()
    
    # Test session management
    success, msg = framework.begin_session()
    assert success
    assert framework.session_active
    
    # Test operator
    status = framework.get_operator_status()
    assert "purity_level" in status
    
    # Test purification
    success, messages = framework.purify_operator()
    assert success
    assert framework.operator.is_pure() or framework.operator.purity_level.level >= 2
    
    # Test pentacles
    saturn_pentacles = framework.get_pentacles_for_planet(Planet.SATURN)
    assert len(saturn_pentacles) == 7
    
    # Test spirits
    knowledge_spirits = framework.get_spirits_for_domain(FunctionDomain.KNOWLEDGE)
    assert len(knowledge_spirits) > 0
    
    # Test spells
    spells = framework.get_available_spells()
    assert len(spells) > 0
    
    # Test spell casting
    result, log = framework.cast_spell("For Love and Favor")
    assert result is not None
    
    # Test safety
    assert framework.check_safety_invariant()
    
    # Test summary
    summary = framework.get_summary()
    assert "session" in summary
    assert "operator" in summary
    assert "pentacles" in summary
    
    # End session
    success, msg = framework.end_session()
    assert success
    assert not framework.session_active
    
    print("  ✓ Unified framework")
    
    return True


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Temporal
    'Planet', 'LunarPhase', 'TimeIndex', 'PlanetaryHour', 'PlanetaryDay',
    'TimeWindow', 'TimePredicate', 'TemporalScheduler',
    
    # Geometry
    'Zone', 'GeometryType', 'DivineName', 'BoundaryLabel',
    'MagicCircle', 'TriangleOfArt', 'Pentagram', 'GeometricKernel',
    'AccessControlMatrix', 'RitualSpace',
    
    # Pentacles
    'EffectType', 'GeometricForm', 'PentacleSpec', 'PentacleKernel',
    'PentacleLibrary', 'PENTACLE_LIBRARY',
    
    # Spirits
    'SpiritState', 'SpiritClass', 'FunctionDomain',
    'SpiritSpec', 'Spirit', 'SpiritRegistry',
    
    # Operator
    'PurityLevel', 'AbstractionStatus', 'IntentAlignment',
    'BodyState', 'MindState', 'IntentState', 'OperatorState',
    'PurificationProtocol',
    
    # Spells
    'SpellCategory', 'SpellResult', 'SpellSpec', 'SpellInstance',
    'SpellBook', 'SPELL_LIBRARY',
    
    # Unified
    'SolomonicFramework',
    'validate_solomonic',
]


if __name__ == "__main__":
    assert validate_solomonic()
    print("\n✓ All validations passed")
    
    # Demo
    print("\n" + "=" * 60)
    print("KEY OF SOLOMON FRAMEWORK - DEMONSTRATION")
    print("=" * 60)
    
    framework = SolomonicFramework()
    
    print("\n1. Begin Session:")
    success, msg = framework.begin_session()
    print(f"   {msg}")
    
    print("\n2. Current Planetary Time:")
    current = framework.get_current_time()
    print(f"   Day: {current.planetary_day.name}")
    print(f"   Hour: {current.planetary_hour.name}")
    print(f"   Lunar: {current.lunar.name}")
    
    print("\n3. Purify Operator:")
    success, messages = framework.purify_operator()
    status = framework.get_operator_status()
    print(f"   Purity: {status['purity_level']}")
    print(f"   Authority: {status['authority_level']}")
    
    print("\n4. Available Pentacles by Planet:")
    for planet in [Planet.SATURN, Planet.JUPITER, Planet.SUN]:
        pentacles = framework.get_pentacles_for_planet(planet)
        print(f"   {planet.name}: {len(pentacles)} pentacles")
    
    print("\n5. Available Spirits:")
    for domain in [FunctionDomain.KNOWLEDGE, FunctionDomain.WEALTH]:
        spirits = framework.get_spirits_for_domain(domain)
        names = [s.name for s in spirits]
        print(f"   {domain.name}: {', '.join(names)}")
    
    print("\n6. Cast Spell:")
    result, log = framework.cast_spell("Invocation of Knowledge")
    print(f"   Result: {result.name}")
    print(f"   Log entries: {len(log)}")
    
    print("\n7. Safety Check:")
    print(f"   All spirits safe: {framework.check_safety_invariant()}")
    
    print("\n8. End Session:")
    success, msg = framework.end_session()
    print(f"   {msg}")
    
    print("\n" + "=" * 60)
