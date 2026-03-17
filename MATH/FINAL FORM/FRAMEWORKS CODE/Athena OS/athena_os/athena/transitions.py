"""
ATHENA OS - STATE TRANSITIONS MODULE
====================================
The Actuality-Potentiality Calculus and Change Types

From ATHENA_OPERATING_SYSTEM_.docx Chapter 8:

ACTUALITY-POTENTIALITY SPECTRUM:
    0 = Pure potentiality (no actualized properties)
    1 = Pure actuality (fully actualized, no unrealized potential)

CHANGE TYPES:
    GENERATION: Non-being → Being (Essential)
    DESTRUCTION: Being → Non-being (Essential)
    ALTERATION: Quality₁ → Quality₂ (Accidental)
    GROWTH: Quantity₁ → Quantity₂+ (Accidental)
    DIMINUTION: Quantity₁ → Quantity₂- (Accidental)
    LOCOMOTION: Place₁ → Place₂ (Accidental)

CHANGE INVARIANTS:
    - Substrate persistence (something underlies change)
    - Terminus specification (from-state and to-state defined)
    - Continuity (no instantaneous jumps without connection)

NATURAL vs VIOLENT MOTION:
    Natural: Toward entity's natural state
    Violent: Away from entity's natural state
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Set, Callable, Union
from enum import Enum, auto
from abc import ABC, abstractmethod
import time


# =============================================================================
# ACTUALITY-POTENTIALITY
# =============================================================================

class ActualityState(Enum):
    """States on the actuality-potentiality spectrum."""
    PURE_POTENTIALITY = 0   # δύναμις (dynamis) - pure capacity
    FIRST_POTENTIALITY = 1  # Has capacity, not exercised
    FIRST_ACTUALITY = 2     # ἐνέργεια (energeia) - has form
    SECOND_ACTUALITY = 3    # Actively exercising capacity
    PURE_ACTUALITY = 4      # ἐντελέχεια (entelechia) - fully realized


@dataclass
class Capacity:
    """A capacity (dynamis) that can be actualized."""
    
    name: str
    category: str  # What kind of capacity
    actualized: bool = False
    actualization_conditions: List[str] = field(default_factory=list)
    
    def actualize(self) -> None:
        """Actualize this capacity."""
        self.actualized = True
    
    def de_actualize(self) -> None:
        """Return to potential state."""
        self.actualized = False


@dataclass
class EntityState:
    """Complete state of an entity on actuality-potentiality spectrum."""
    
    entity_id: str
    actuality_level: float  # 0.0 to 1.0
    
    # Form structure
    essential_form: Any  # What makes it what it is
    accidental_forms: Dict[str, Any] = field(default_factory=dict)
    
    # Matter (substrate)
    matter: Any = None
    
    # Capacities
    capacities: Dict[str, Capacity] = field(default_factory=dict)
    
    # Temporal
    timestamp: float = field(default_factory=time.time)
    
    @property
    def actuality_state(self) -> ActualityState:
        """Get discrete actuality state."""
        if self.actuality_level == 0.0:
            return ActualityState.PURE_POTENTIALITY
        elif self.actuality_level < 0.25:
            return ActualityState.FIRST_POTENTIALITY
        elif self.actuality_level < 0.5:
            return ActualityState.FIRST_ACTUALITY
        elif self.actuality_level < 1.0:
            return ActualityState.SECOND_ACTUALITY
        else:
            return ActualityState.PURE_ACTUALITY
    
    @property
    def actualized_capacities(self) -> List[Capacity]:
        """Get list of actualized capacities."""
        return [c for c in self.capacities.values() if c.actualized]
    
    @property
    def potential_capacities(self) -> List[Capacity]:
        """Get list of potential (non-actualized) capacities."""
        return [c for c in self.capacities.values() if not c.actualized]
    
    def add_capacity(self, capacity: Capacity) -> None:
        """Add a capacity to the entity."""
        self.capacities[capacity.name] = capacity
    
    def actualize_capacity(self, name: str) -> bool:
        """Actualize a capacity by name."""
        if name in self.capacities:
            self.capacities[name].actualize()
            self._recalculate_actuality()
            return True
        return False
    
    def _recalculate_actuality(self) -> None:
        """Recalculate actuality level based on capacities."""
        if not self.capacities:
            return
        actualized_count = len(self.actualized_capacities)
        total_count = len(self.capacities)
        self.actuality_level = actualized_count / total_count


# =============================================================================
# CHANGE TYPES
# =============================================================================

class ChangeCategory(Enum):
    """Categories of change (kinesis/metabole)."""
    ESSENTIAL = auto()    # Changes to substance itself
    ACCIDENTAL = auto()   # Changes to accidents


class ChangeType(Enum):
    """Types of change in Aristotelian physics."""
    # Essential changes
    GENERATION = auto()   # Non-being → Being (γένεσις)
    DESTRUCTION = auto()  # Being → Non-being (φθορά)
    
    # Accidental changes
    ALTERATION = auto()   # Quality change (ἀλλοίωσις)
    GROWTH = auto()       # Quantity increase (αὔξησις)
    DIMINUTION = auto()   # Quantity decrease (φθίσις)
    LOCOMOTION = auto()   # Place change (φορά)


@dataclass(frozen=True)
class ChangeSpec:
    """Specification of a change type."""
    
    change_type: ChangeType
    name: str
    greek_name: str
    category: ChangeCategory
    from_category: Optional[str]  # Category of from-state
    to_category: Optional[str]    # Category of to-state
    description: str


CHANGE_GENERATION = ChangeSpec(
    ChangeType.GENERATION, "Generation", "γένεσις",
    ChangeCategory.ESSENTIAL, "Non-being", "Being",
    "Coming into existence"
)

CHANGE_DESTRUCTION = ChangeSpec(
    ChangeType.DESTRUCTION, "Destruction", "φθορά",
    ChangeCategory.ESSENTIAL, "Being", "Non-being",
    "Passing out of existence"
)

CHANGE_ALTERATION = ChangeSpec(
    ChangeType.ALTERATION, "Alteration", "ἀλλοίωσις",
    ChangeCategory.ACCIDENTAL, "Quality", "Quality",
    "Change in quality"
)

CHANGE_GROWTH = ChangeSpec(
    ChangeType.GROWTH, "Growth", "αὔξησις",
    ChangeCategory.ACCIDENTAL, "Quantity", "Quantity+",
    "Increase in quantity"
)

CHANGE_DIMINUTION = ChangeSpec(
    ChangeType.DIMINUTION, "Diminution", "φθίσις",
    ChangeCategory.ACCIDENTAL, "Quantity-", "Quantity",
    "Decrease in quantity"
)

CHANGE_LOCOMOTION = ChangeSpec(
    ChangeType.LOCOMOTION, "Locomotion", "φορά",
    ChangeCategory.ACCIDENTAL, "Place", "Place",
    "Change in location"
)

ALL_CHANGES: Dict[ChangeType, ChangeSpec] = {
    ChangeType.GENERATION: CHANGE_GENERATION,
    ChangeType.DESTRUCTION: CHANGE_DESTRUCTION,
    ChangeType.ALTERATION: CHANGE_ALTERATION,
    ChangeType.GROWTH: CHANGE_GROWTH,
    ChangeType.DIMINUTION: CHANGE_DIMINUTION,
    ChangeType.LOCOMOTION: CHANGE_LOCOMOTION,
}


# =============================================================================
# CHANGE EVENTS
# =============================================================================

@dataclass
class ChangeEvent:
    """A change event in the system."""
    
    event_id: str
    entity_id: str
    change_type: ChangeType
    
    # Termini
    from_state: Any
    to_state: Any
    
    # Context
    efficient_cause: Optional[str] = None
    final_cause: Optional[str] = None
    
    # Timing
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    
    # Status
    completed: bool = False
    
    @property
    def duration(self) -> Optional[float]:
        if self.end_time is not None:
            return self.end_time - self.start_time
        return None
    
    @property
    def change_spec(self) -> ChangeSpec:
        return ALL_CHANGES[self.change_type]
    
    def complete(self) -> None:
        """Mark change as complete."""
        self.end_time = time.time()
        self.completed = True


# =============================================================================
# MOTION TYPES
# =============================================================================

class MotionType(Enum):
    """Types of motion relative to natural state."""
    NATURAL = auto()   # Toward natural state (κατὰ φύσιν)
    VIOLENT = auto()   # Away from natural state (βίᾳ)


@dataclass
class Motion:
    """A motion (kinesis) - change in progress."""
    
    entity_id: str
    change_event: ChangeEvent
    motion_type: MotionType
    
    # Progress
    progress: float = 0.0  # 0.0 to 1.0
    
    # Cause
    mover: Optional[str] = None  # What causes the motion
    
    def advance(self, delta: float) -> None:
        """Advance motion progress."""
        self.progress = min(1.0, self.progress + delta)
    
    @property
    def is_complete(self) -> bool:
        return self.progress >= 1.0


# =============================================================================
# CHANGE INVARIANTS
# =============================================================================

class ChangeInvariant(Enum):
    """Invariants that must hold during change."""
    SUBSTRATE_PERSISTENCE = auto()  # Something underlies change
    TERMINUS_SPECIFICATION = auto() # From and to states defined
    CONTINUITY = auto()             # No instantaneous jumps


@dataclass
class InvariantCheck:
    """Check of a change invariant."""
    
    invariant: ChangeInvariant
    satisfied: bool
    message: str


def check_invariants(event: ChangeEvent, 
                    entity_state: Optional[EntityState] = None) -> List[InvariantCheck]:
    """Check all change invariants for an event."""
    checks = []
    
    # Substrate persistence
    has_substrate = entity_state is not None and entity_state.matter is not None
    # For generation, no prior substrate needed
    if event.change_type == ChangeType.GENERATION:
        has_substrate = True
    checks.append(InvariantCheck(
        ChangeInvariant.SUBSTRATE_PERSISTENCE,
        has_substrate,
        "Substrate persists through change" if has_substrate else "No substrate found"
    ))
    
    # Terminus specification
    termini_defined = event.from_state is not None and event.to_state is not None
    checks.append(InvariantCheck(
        ChangeInvariant.TERMINUS_SPECIFICATION,
        termini_defined,
        "Termini specified" if termini_defined else "Termini not fully specified"
    ))
    
    # Continuity (basic check - from and to should be "connected")
    continuous = True  # Assume continuous unless proven otherwise
    checks.append(InvariantCheck(
        ChangeInvariant.CONTINUITY,
        continuous,
        "Change is continuous" if continuous else "Discontinuity detected"
    ))
    
    return checks


# =============================================================================
# STATE TRANSITION ENGINE
# =============================================================================

class TransitionResult(Enum):
    """Result of a state transition."""
    SUCCESS = auto()
    INVARIANT_VIOLATION = auto()
    IMPOSSIBLE = auto()
    BLOCKED = auto()


@dataclass
class TransitionOutcome:
    """Outcome of a state transition attempt."""
    
    result: TransitionResult
    new_state: Optional[EntityState]
    change_event: Optional[ChangeEvent]
    invariant_checks: List[InvariantCheck]
    message: str


class StateTransitionEngine:
    """Engine for managing state transitions."""
    
    def __init__(self):
        self.entities: Dict[str, EntityState] = {}
        self.change_history: List[ChangeEvent] = []
        self.active_motions: Dict[str, Motion] = {}
    
    def register_entity(self, entity_id: str, 
                       essential_form: Any,
                       matter: Any = None) -> EntityState:
        """Register a new entity."""
        state = EntityState(
            entity_id=entity_id,
            actuality_level=0.5,  # Default middle actuality
            essential_form=essential_form,
            matter=matter
        )
        self.entities[entity_id] = state
        return state
    
    def get_state(self, entity_id: str) -> Optional[EntityState]:
        """Get current state of entity."""
        return self.entities.get(entity_id)
    
    def transition(self, 
                  entity_id: str,
                  change_type: ChangeType,
                  to_state: Any,
                  efficient_cause: Optional[str] = None,
                  final_cause: Optional[str] = None) -> TransitionOutcome:
        """
        Attempt a state transition.
        
        Args:
            entity_id: Entity to transition
            change_type: Type of change
            to_state: Target state
            efficient_cause: What causes the change
            final_cause: Purpose of the change
        """
        entity_state = self.entities.get(entity_id)
        
        # For generation, entity may not exist yet
        if change_type == ChangeType.GENERATION:
            if entity_state is not None:
                return TransitionOutcome(
                    TransitionResult.IMPOSSIBLE,
                    None, None, [],
                    "Entity already exists - cannot generate"
                )
            # Create the entity
            from_state = None
            entity_state = EntityState(
                entity_id=entity_id,
                actuality_level=0.0,
                essential_form=to_state
            )
        elif entity_state is None:
            return TransitionOutcome(
                TransitionResult.IMPOSSIBLE,
                None, None, [],
                f"Entity {entity_id} not found"
            )
        else:
            from_state = self._extract_relevant_state(entity_state, change_type)
        
        # Create change event
        event = ChangeEvent(
            event_id=f"change_{len(self.change_history)}",
            entity_id=entity_id,
            change_type=change_type,
            from_state=from_state,
            to_state=to_state,
            efficient_cause=efficient_cause,
            final_cause=final_cause
        )
        
        # Check invariants
        invariants = check_invariants(event, entity_state)
        violations = [i for i in invariants if not i.satisfied]
        
        if violations:
            return TransitionOutcome(
                TransitionResult.INVARIANT_VIOLATION,
                None, event, invariants,
                f"Invariant violations: {[v.message for v in violations]}"
            )
        
        # Apply transition
        new_state = self._apply_change(entity_state, change_type, to_state)
        event.complete()
        
        # Update records
        self.entities[entity_id] = new_state
        self.change_history.append(event)
        
        return TransitionOutcome(
            TransitionResult.SUCCESS,
            new_state, event, invariants,
            f"Transition complete: {change_type.name}"
        )
    
    def _extract_relevant_state(self, 
                               entity_state: EntityState,
                               change_type: ChangeType) -> Any:
        """Extract the relevant from-state based on change type."""
        spec = ALL_CHANGES[change_type]
        
        if change_type == ChangeType.ALTERATION:
            return entity_state.accidental_forms.get("quality")
        elif change_type in (ChangeType.GROWTH, ChangeType.DIMINUTION):
            return entity_state.accidental_forms.get("quantity")
        elif change_type == ChangeType.LOCOMOTION:
            return entity_state.accidental_forms.get("place")
        elif change_type == ChangeType.DESTRUCTION:
            return entity_state.essential_form
        else:
            return entity_state
    
    def _apply_change(self,
                     entity_state: EntityState,
                     change_type: ChangeType,
                     to_state: Any) -> EntityState:
        """Apply the change to entity state."""
        # Create new state (immutable pattern)
        new_state = EntityState(
            entity_id=entity_state.entity_id,
            actuality_level=entity_state.actuality_level,
            essential_form=entity_state.essential_form,
            accidental_forms=dict(entity_state.accidental_forms),
            matter=entity_state.matter,
            capacities=dict(entity_state.capacities)
        )
        
        if change_type == ChangeType.ALTERATION:
            new_state.accidental_forms["quality"] = to_state
        elif change_type in (ChangeType.GROWTH, ChangeType.DIMINUTION):
            new_state.accidental_forms["quantity"] = to_state
        elif change_type == ChangeType.LOCOMOTION:
            new_state.accidental_forms["place"] = to_state
        elif change_type == ChangeType.GENERATION:
            new_state.essential_form = to_state
            new_state.actuality_level = 0.5
        elif change_type == ChangeType.DESTRUCTION:
            new_state.essential_form = None
            new_state.actuality_level = 0.0
        
        return new_state
    
    def start_motion(self,
                    entity_id: str,
                    change_type: ChangeType,
                    to_state: Any,
                    motion_type: MotionType = MotionType.NATURAL,
                    mover: Optional[str] = None) -> Optional[Motion]:
        """Start a continuous motion (change in progress)."""
        entity_state = self.entities.get(entity_id)
        if entity_state is None:
            return None
        
        from_state = self._extract_relevant_state(entity_state, change_type)
        
        event = ChangeEvent(
            event_id=f"motion_{len(self.change_history)}",
            entity_id=entity_id,
            change_type=change_type,
            from_state=from_state,
            to_state=to_state
        )
        
        motion = Motion(
            entity_id=entity_id,
            change_event=event,
            motion_type=motion_type,
            mover=mover
        )
        
        self.active_motions[entity_id] = motion
        return motion
    
    def advance_motion(self, entity_id: str, delta: float) -> Optional[TransitionOutcome]:
        """Advance an active motion."""
        motion = self.active_motions.get(entity_id)
        if motion is None:
            return None
        
        motion.advance(delta)
        
        if motion.is_complete:
            # Complete the transition
            del self.active_motions[entity_id]
            return self.transition(
                entity_id,
                motion.change_event.change_type,
                motion.change_event.to_state,
                motion.change_event.efficient_cause,
                motion.change_event.final_cause
            )
        
        return None


# =============================================================================
# VALIDATION
# =============================================================================

def validate_transitions() -> bool:
    """Validate the transitions module."""
    
    # Test actuality states
    state = EntityState(
        entity_id="test",
        actuality_level=0.5,
        essential_form="triangle"
    )
    assert state.actuality_state == ActualityState.FIRST_ACTUALITY
    
    # Test capacity
    cap = Capacity("see", "perception")
    assert not cap.actualized
    cap.actualize()
    assert cap.actualized
    
    # Test change types
    assert len(ALL_CHANGES) == 6
    assert CHANGE_GENERATION.category == ChangeCategory.ESSENTIAL
    assert CHANGE_ALTERATION.category == ChangeCategory.ACCIDENTAL
    
    # Test change event
    event = ChangeEvent(
        event_id="e1",
        entity_id="entity1",
        change_type=ChangeType.ALTERATION,
        from_state="white",
        to_state="black"
    )
    invariants = check_invariants(event, state)
    assert len(invariants) == 3
    
    # Test transition engine
    engine = StateTransitionEngine()
    
    # Register entity
    entity = engine.register_entity("socrates", "human", "flesh and bone")
    assert entity.entity_id == "socrates"
    
    # Perform alteration
    outcome = engine.transition(
        "socrates",
        ChangeType.ALTERATION,
        "wise",
        efficient_cause="philosophy",
        final_cause="knowledge"
    )
    assert outcome.result == TransitionResult.SUCCESS
    
    # Check new state
    new_state = engine.get_state("socrates")
    assert new_state.accidental_forms.get("quality") == "wise"
    
    # Test locomotion
    outcome = engine.transition(
        "socrates",
        ChangeType.LOCOMOTION,
        "agora",
        efficient_cause="walking",
        final_cause="discourse"
    )
    assert outcome.result == TransitionResult.SUCCESS
    
    # Test generation
    outcome = engine.transition(
        "new_entity",
        ChangeType.GENERATION,
        "circle"
    )
    assert outcome.result == TransitionResult.SUCCESS
    
    # Test motion
    motion = engine.start_motion(
        "socrates",
        ChangeType.LOCOMOTION,
        "academy",
        MotionType.NATURAL
    )
    assert motion is not None
    assert motion.progress == 0.0
    
    motion.advance(0.5)
    assert motion.progress == 0.5
    
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("ATHENA OS - STATE TRANSITIONS MODULE")
    print("=" * 60)
    
    print("\nValidating transitions...")
    assert validate_transitions()
    print("✓ Transitions validated")
    
    # Demo
    print("\n--- ACTUALITY STATES ---")
    for state in ActualityState:
        print(f"  {state.value}: {state.name}")
    
    print("\n--- CHANGE TYPES ---")
    for change_type, spec in ALL_CHANGES.items():
        print(f"  {spec.name} ({spec.greek_name})")
        print(f"      {spec.from_category} → {spec.to_category}")
        print(f"      Category: {spec.category.name}")
    
    print("\n--- DEMO: State Transitions ---")
    engine = StateTransitionEngine()
    
    # Create Socrates
    engine.register_entity("socrates", "rational animal", "flesh and bone")
    print("  Created: Socrates (rational animal)")
    
    # Make him wise
    outcome = engine.transition("socrates", ChangeType.ALTERATION, "wise")
    print(f"  Alteration: → wise [{outcome.result.name}]")
    
    # Move to agora
    outcome = engine.transition("socrates", ChangeType.LOCOMOTION, "agora")
    print(f"  Locomotion: → agora [{outcome.result.name}]")
    
    state = engine.get_state("socrates")
    print(f"  Final state: {state.accidental_forms}")
