"""
ATHENA OS - Aristotelian Type System
====================================
The 10 Categories of Being as a computational type system.

Categories:
1. SUBSTANCE (ousia) - What it IS (primary being)
2. QUANTITY (poson) - How MUCH/MANY
3. QUALITY (poion) - What KIND
4. RELATION (pros ti) - Toward WHAT
5. PLACE (pou) - WHERE
6. TIME (pote) - WHEN
7. POSITION (keisthai) - DISPOSITION/posture
8. HAVING (echein) - POSSESSION/state
9. ACTION (poiein) - DOING
10. PASSION (paschein) - BEING-DONE-TO (undergoing)

Plus the Four Causes:
- Material: What it's made of
- Formal: What makes it that kind of thing
- Efficient: What brought it about
- Final: What it's for (purpose/telos)
"""

from __future__ import annotations
from enum import IntEnum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Set, TypeVar, Generic
from abc import ABC, abstractmethod
from datetime import datetime


# =============================================================================
# THE TEN CATEGORIES
# =============================================================================

class Category(IntEnum):
    """
    The 10 Aristotelian Categories of predication.
    
    These are the fundamental ways we can say something ABOUT something.
    They form a complete type system for describing any entity.
    """
    SUBSTANCE = 0    # What it IS (the subject)
    QUANTITY = 1     # How much/many (size, number, extent)
    QUALITY = 2      # What kind (properties, characteristics)
    RELATION = 3     # Toward what (connections, comparisons)
    PLACE = 4        # Where (spatial location)
    TIME = 5         # When (temporal location)
    POSITION = 6     # Disposition (arrangement, posture)
    HAVING = 7       # State of possession/condition
    ACTION = 8       # What it does (active causation)
    PASSION = 9      # What is done to it (passive reception)
    
    @property
    def greek(self) -> str:
        """Original Greek term."""
        return {
            Category.SUBSTANCE: "οὐσία (ousia)",
            Category.QUANTITY: "ποσόν (poson)",
            Category.QUALITY: "ποιόν (poion)",
            Category.RELATION: "πρός τι (pros ti)",
            Category.PLACE: "ποῦ (pou)",
            Category.TIME: "ποτέ (pote)",
            Category.POSITION: "κεῖσθαι (keisthai)",
            Category.HAVING: "ἔχειν (echein)",
            Category.ACTION: "ποιεῖν (poiein)",
            Category.PASSION: "πάσχειν (paschein)"
        }[self]
    
    @property
    def question(self) -> str:
        """The question this category answers."""
        return {
            Category.SUBSTANCE: "What is it?",
            Category.QUANTITY: "How much/many?",
            Category.QUALITY: "What kind?",
            Category.RELATION: "Related to what?",
            Category.PLACE: "Where?",
            Category.TIME: "When?",
            Category.POSITION: "In what arrangement?",
            Category.HAVING: "What does it have/possess?",
            Category.ACTION: "What is it doing?",
            Category.PASSION: "What is being done to it?"
        }[self]
    
    @property
    def examples(self) -> List[str]:
        """Example predicates in this category."""
        return {
            Category.SUBSTANCE: ["human", "horse", "tree", "process", "system"],
            Category.QUANTITY: ["five", "large", "triple", "half", "32-bit"],
            Category.QUALITY: ["white", "musical", "valid", "stable", "coherent"],
            Category.RELATION: ["greater than", "parent of", "similar to", "depends on"],
            Category.PLACE: ["in the register", "at address 0x00", "in memory"],
            Category.TIME: ["yesterday", "at cycle 100", "during execution"],
            Category.POSITION: ["lying", "standing", "suspended", "queued"],
            Category.HAVING: ["armed", "holding lock", "owning resource"],
            Category.ACTION: ["cutting", "computing", "transforming", "emitting"],
            Category.PASSION: ["being cut", "being computed", "being transformed"]
        }[self]
    
    @property
    def is_primary(self) -> bool:
        """SUBSTANCE is primary; all others are secondary."""
        return self == Category.SUBSTANCE


# =============================================================================
# THE FOUR CAUSES
# =============================================================================

class Cause(IntEnum):
    """
    The Four Causes (aitia) - ways of explaining WHY something is.
    
    Complete explanation of any phenomenon requires all four.
    """
    MATERIAL = 0    # What it's made of
    FORMAL = 1      # What makes it that kind of thing (form/structure)
    EFFICIENT = 2   # What brought it about (agent/process)
    FINAL = 3       # What it's for (telos/purpose)
    
    @property
    def question(self) -> str:
        """The question this cause answers."""
        return {
            Cause.MATERIAL: "What is it made of?",
            Cause.FORMAL: "What is its form/structure?",
            Cause.EFFICIENT: "What produced it?",
            Cause.FINAL: "What is it for?"
        }[self]
    
    @property
    def example(self) -> str:
        """Example explanation using this cause."""
        # Example: a bronze statue
        return {
            Cause.MATERIAL: "Bronze (the stuff)",
            Cause.FORMAL: "The shape of a human (the form)",
            Cause.EFFICIENT: "The sculptor's art (the maker)",
            Cause.FINAL: "Honor the god (the purpose)"
        }[self]


# =============================================================================
# ACTUALITY AND POTENTIALITY
# =============================================================================

class ActualityMode(IntEnum):
    """
    The modes of being: Actuality (energeia) and Potentiality (dynamis).
    
    - POTENTIAL: What something CAN be
    - ACTUAL: What something IS
    - COMPLETE (entelechia): Fully realized actuality
    """
    POTENTIAL = 0    # Dynamis - capacity, possibility
    ACTUAL = 1       # Energeia - activity, being-at-work
    COMPLETE = 2     # Entelechia - complete actuality, fulfillment


@dataclass
class ActualityState:
    """
    Tracks the actuality/potentiality of an entity.
    
    An entity can have multiple potentials, some of which
    may be actualized to varying degrees.
    """
    potentials: Dict[str, float] = field(default_factory=dict)  # name -> degree (0-1)
    actualized: Set[str] = field(default_factory=set)
    complete: Set[str] = field(default_factory=set)
    
    def add_potential(self, name: str, degree: float = 0.0) -> None:
        """Add a potential capacity."""
        self.potentials[name] = max(0.0, min(1.0, degree))
    
    def actualize(self, name: str, degree: float = 1.0) -> bool:
        """
        Actualize a potential.
        Returns True if successful.
        """
        if name not in self.potentials:
            return False
        
        self.potentials[name] = max(0.0, min(1.0, degree))
        if degree > 0:
            self.actualized.add(name)
        if degree >= 1.0:
            self.complete.add(name)
        return True
    
    def deactualize(self, name: str) -> None:
        """Return an actuality to potential."""
        if name in self.actualized:
            self.actualized.remove(name)
        if name in self.complete:
            self.complete.remove(name)
        self.potentials[name] = 0.0
    
    def is_potential(self, name: str) -> bool:
        """Check if something is merely potential."""
        return name in self.potentials and name not in self.actualized
    
    def is_actual(self, name: str) -> bool:
        """Check if something is actual."""
        return name in self.actualized
    
    def is_complete(self, name: str) -> bool:
        """Check if something is fully actual (entelechia)."""
        return name in self.complete
    
    def actualization_ratio(self) -> float:
        """Return ratio of actualized to total potentials."""
        if not self.potentials:
            return 0.0
        return len(self.actualized) / len(self.potentials)


# =============================================================================
# CATEGORICAL PREDICATE
# =============================================================================

@dataclass
class Predicate:
    """
    A categorical predicate - something said OF a subject.
    """
    category: Category
    value: Any
    degree: float = 1.0  # For qualities that admit of degree
    negated: bool = False
    
    def __str__(self) -> str:
        neg = "NOT " if self.negated else ""
        return f"{self.category.name}: {neg}{self.value}"
    
    def negate(self) -> 'Predicate':
        """Return the negation of this predicate."""
        return Predicate(
            category=self.category,
            value=self.value,
            degree=self.degree,
            negated=not self.negated
        )
    
    def satisfies(self, other: 'Predicate') -> bool:
        """Check if this predicate satisfies another."""
        if self.category != other.category:
            return False
        if self.negated != other.negated:
            return False
        return self.value == other.value


# =============================================================================
# ENTITY (Substance Instance)
# =============================================================================

T = TypeVar('T')

@dataclass
class Entity:
    """
    An entity in the Aristotelian type system.
    
    Primary substance: the individual thing (this human, this horse)
    Secondary substance: the kind/species (human, horse)
    
    All other categories are predicated OF substances.
    """
    # Identity
    id: str
    species: str  # Secondary substance (the kind)
    genus: Optional[str] = None  # Higher genus
    
    # The 10 categories as slots
    substance: str = ""  # What it IS (primary being)
    quantity: Any = None  # How much/many
    quality: List[str] = field(default_factory=list)  # What kind
    relations: Dict[str, Any] = field(default_factory=dict)  # Relations to others
    place: Optional[str] = None  # Where
    time: Optional[datetime] = None  # When
    position: Optional[str] = None  # Disposition
    having: List[str] = field(default_factory=list)  # What it possesses
    action: Optional[str] = None  # What it's doing
    passion: Optional[str] = None  # What's done to it
    
    # The 4 causes
    material_cause: Optional[str] = None
    formal_cause: Optional[str] = None
    efficient_cause: Optional[str] = None
    final_cause: Optional[str] = None
    
    # Actuality state
    actuality: ActualityState = field(default_factory=ActualityState)
    
    def __post_init__(self):
        """Initialize substance from species."""
        if not self.substance:
            self.substance = self.species
    
    def predicate(self, pred: Predicate) -> bool:
        """
        Apply a predicate to this entity.
        Returns True if successful.
        """
        if pred.negated:
            return self._remove_predicate(pred.category, pred.value)
        return self._add_predicate(pred.category, pred.value)
    
    def _add_predicate(self, category: Category, value: Any) -> bool:
        """Add a predicate."""
        if category == Category.SUBSTANCE:
            self.substance = value
        elif category == Category.QUANTITY:
            self.quantity = value
        elif category == Category.QUALITY:
            if value not in self.quality:
                self.quality.append(value)
        elif category == Category.RELATION:
            if isinstance(value, tuple) and len(value) == 2:
                self.relations[value[0]] = value[1]
        elif category == Category.PLACE:
            self.place = value
        elif category == Category.TIME:
            self.time = value
        elif category == Category.POSITION:
            self.position = value
        elif category == Category.HAVING:
            if value not in self.having:
                self.having.append(value)
        elif category == Category.ACTION:
            self.action = value
        elif category == Category.PASSION:
            self.passion = value
        return True
    
    def _remove_predicate(self, category: Category, value: Any) -> bool:
        """Remove a predicate."""
        if category == Category.QUALITY:
            if value in self.quality:
                self.quality.remove(value)
        elif category == Category.HAVING:
            if value in self.having:
                self.having.remove(value)
        elif category == Category.RELATION:
            if isinstance(value, tuple) and value[0] in self.relations:
                del self.relations[value[0]]
        return True
    
    def get_category(self, category: Category) -> Any:
        """Get the value for a category."""
        return {
            Category.SUBSTANCE: self.substance,
            Category.QUANTITY: self.quantity,
            Category.QUALITY: self.quality,
            Category.RELATION: self.relations,
            Category.PLACE: self.place,
            Category.TIME: self.time,
            Category.POSITION: self.position,
            Category.HAVING: self.having,
            Category.ACTION: self.action,
            Category.PASSION: self.passion
        }[category]
    
    def get_causes(self) -> Dict[Cause, Optional[str]]:
        """Return all four causes."""
        return {
            Cause.MATERIAL: self.material_cause,
            Cause.FORMAL: self.formal_cause,
            Cause.EFFICIENT: self.efficient_cause,
            Cause.FINAL: self.final_cause
        }
    
    def has_quality(self, quality: str) -> bool:
        """Check if entity has a specific quality."""
        return quality in self.quality
    
    def has_relation(self, relation: str) -> bool:
        """Check if entity has a specific relation."""
        return relation in self.relations
    
    def describe(self) -> str:
        """Generate a natural language description."""
        lines = [f"Entity: {self.id} ({self.species})"]
        lines.append(f"  Substance: {self.substance}")
        if self.quantity:
            lines.append(f"  Quantity: {self.quantity}")
        if self.quality:
            lines.append(f"  Qualities: {', '.join(self.quality)}")
        if self.relations:
            lines.append(f"  Relations: {self.relations}")
        if self.place:
            lines.append(f"  Place: {self.place}")
        if self.time:
            lines.append(f"  Time: {self.time}")
        if self.position:
            lines.append(f"  Position: {self.position}")
        if self.having:
            lines.append(f"  Having: {', '.join(self.having)}")
        if self.action:
            lines.append(f"  Action: {self.action}")
        if self.passion:
            lines.append(f"  Passion: {self.passion}")
        return '\n'.join(lines)


# =============================================================================
# SYLLOGISTIC INFERENCE
# =============================================================================

@dataclass
class Syllogism:
    """
    Aristotelian syllogistic inference.
    
    Form: 
    Major premise: All M are P
    Minor premise: All S are M
    Conclusion: All S are P
    """
    major_premise: Tuple[str, str, str]  # (quantifier, subject, predicate)
    minor_premise: Tuple[str, str, str]
    middle_term: str
    
    QUANTIFIERS = {'ALL', 'NO', 'SOME', 'SOME_NOT'}
    
    def derive_conclusion(self) -> Optional[Tuple[str, str, str]]:
        """
        Attempt to derive a valid conclusion.
        Returns (quantifier, subject, predicate) or None if invalid.
        """
        maj_q, maj_s, maj_p = self.major_premise
        min_q, min_s, min_p = self.minor_premise
        
        # Barbara (AAA-1): All M are P, All S are M → All S are P
        if maj_q == 'ALL' and min_q == 'ALL':
            if maj_s == self.middle_term and min_p == self.middle_term:
                return ('ALL', min_s, maj_p)
        
        # Celarent (EAE-1): No M is P, All S are M → No S is P
        if maj_q == 'NO' and min_q == 'ALL':
            if maj_s == self.middle_term and min_p == self.middle_term:
                return ('NO', min_s, maj_p)
        
        # Darii (AII-1): All M are P, Some S is M → Some S is P
        if maj_q == 'ALL' and min_q == 'SOME':
            if maj_s == self.middle_term and min_p == self.middle_term:
                return ('SOME', min_s, maj_p)
        
        # Ferio (EIO-1): No M is P, Some S is M → Some S is not P
        if maj_q == 'NO' and min_q == 'SOME':
            if maj_s == self.middle_term and min_p == self.middle_term:
                return ('SOME_NOT', min_s, maj_p)
        
        return None
    
    def is_valid(self) -> bool:
        """Check if the syllogism can derive a valid conclusion."""
        return self.derive_conclusion() is not None


# =============================================================================
# TYPE REGISTRY (Species and Genera)
# =============================================================================

class TypeRegistry:
    """
    Registry of species and genera (secondary substances).
    
    Implements the "tree of Porphyry" - the classification hierarchy.
    """
    
    def __init__(self):
        self.types: Dict[str, Dict] = {}  # name -> {genus, differentia, qualities}
        self.hierarchy: Dict[str, Set[str]] = {}  # genus -> set of species
    
    def register_type(self, name: str, 
                      genus: Optional[str] = None,
                      differentia: Optional[str] = None,
                      essential_qualities: List[str] = None) -> None:
        """Register a new type (species)."""
        self.types[name] = {
            'genus': genus,
            'differentia': differentia,
            'essential_qualities': essential_qualities or []
        }
        
        if genus:
            if genus not in self.hierarchy:
                self.hierarchy[genus] = set()
            self.hierarchy[genus].add(name)
    
    def get_genus(self, species: str) -> Optional[str]:
        """Get the genus of a species."""
        if species in self.types:
            return self.types[species].get('genus')
        return None
    
    def get_species(self, genus: str) -> Set[str]:
        """Get all species under a genus."""
        return self.hierarchy.get(genus, set())
    
    def is_a(self, species: str, genus: str) -> bool:
        """Check if species IS-A genus (transitive)."""
        if species == genus:
            return True
        
        current_genus = self.get_genus(species)
        while current_genus:
            if current_genus == genus:
                return True
            current_genus = self.get_genus(current_genus)
        
        return False
    
    def get_essential_qualities(self, species: str) -> List[str]:
        """Get essential qualities of a species."""
        if species in self.types:
            return self.types[species].get('essential_qualities', [])
        return []
    
    def create_entity(self, species: str, entity_id: str) -> Entity:
        """Create an entity of a given species."""
        if species not in self.types:
            raise ValueError(f"Unknown species: {species}")
        
        type_info = self.types[species]
        entity = Entity(
            id=entity_id,
            species=species,
            genus=type_info.get('genus'),
            quality=list(type_info.get('essential_qualities', []))
        )
        return entity


# =============================================================================
# VALIDATION
# =============================================================================

def validate_aristotelian_system() -> bool:
    """Validate the Aristotelian type system."""
    # 10 categories
    assert len(Category) == 10
    
    # SUBSTANCE is primary
    assert Category.SUBSTANCE.is_primary
    for c in Category:
        if c != Category.SUBSTANCE:
            assert not c.is_primary
    
    # 4 causes
    assert len(Cause) == 4
    
    # 3 actuality modes
    assert len(ActualityMode) == 3
    
    # Syllogism Barbara works
    syl = Syllogism(
        major_premise=('ALL', 'mortal', 'living'),
        minor_premise=('ALL', 'human', 'mortal'),
        middle_term='mortal'
    )
    conclusion = syl.derive_conclusion()
    assert conclusion is not None
    assert conclusion[0] == 'ALL'
    
    return True


if __name__ == "__main__":
    print("Validating Aristotelian type system...")
    assert validate_aristotelian_system()
    print("✓ 10 Categories + 4 Causes validated")
    
    # Demo
    print("\n=== The 10 Categories ===")
    for c in Category:
        print(f"{c.value}. {c.name} {c.greek}")
        print(f"   Question: {c.question}")
    
    print("\n=== The 4 Causes ===")
    for cause in Cause:
        print(f"{cause.name}: {cause.question}")
        print(f"   Example: {cause.example}")
    
    print("\n=== Entity Demo ===")
    registry = TypeRegistry()
    registry.register_type('substance', None, None, [])
    registry.register_type('living', 'substance', 'has life', ['animate'])
    registry.register_type('animal', 'living', 'has sensation', ['sentient'])
    registry.register_type('human', 'animal', 'has reason', ['rational'])
    
    socrates = registry.create_entity('human', 'socrates')
    socrates.predicate(Predicate(Category.QUALITY, 'wise'))
    socrates.predicate(Predicate(Category.PLACE, 'Athens'))
    socrates.predicate(Predicate(Category.ACTION, 'philosophizing'))
    socrates.material_cause = 'flesh and bone'
    socrates.formal_cause = 'rational soul'
    socrates.efficient_cause = 'parents'
    socrates.final_cause = 'eudaimonia'
    
    print(socrates.describe())
    
    print("\n=== Type Hierarchy ===")
    print(f"human IS-A animal: {registry.is_a('human', 'animal')}")
    print(f"human IS-A living: {registry.is_a('human', 'living')}")
    print(f"human IS-A substance: {registry.is_a('human', 'substance')}")
