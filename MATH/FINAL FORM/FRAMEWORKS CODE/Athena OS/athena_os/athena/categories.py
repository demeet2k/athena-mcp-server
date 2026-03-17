"""
ATHENA OS - CATEGORIES MODULE
=============================
The Ten Aristotelian Categories and Four Causes

From ATHENA_OPERATING_SYSTEM_.docx Chapter 7:

THE TEN CATEGORIES:
    0. ENTITY (Substance) - Primary category, can be subject
    1. QUANTITY - How much/many
    2. QUALITY - What kind
    3. RELATION - How related
    4. PLACE - Where
    5. TIME - When
    6. POSTURE - Position/arrangement
    7. HAVING - Possession/condition
    8. ACTION - What it does
    9. PASSION - What is done to it

PREDICATION RULES:
    - Only ENTITY (0) can serve as logical subject
    - Predicates must be from categories 1-9
    - Categories 1-9 are "accidents" (depend on substance)

FOUR CAUSES (Aitiai):
    1. Material Cause - What it's made of
    2. Formal Cause - Its defining structure
    3. Efficient Cause - What brought it about
    4. Final Cause - Its purpose/end (telos)

CAUSAL COMPLETENESS:
    A complete explanation requires all four causes.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Set, Callable, Union
from enum import Enum, auto
from abc import ABC, abstractmethod


# =============================================================================
# THE TEN CATEGORIES
# =============================================================================

class CategoryType(Enum):
    """The ten Aristotelian categories."""
    ENTITY = 0      # Substance - primary category
    QUANTITY = 1    # How much/many
    QUALITY = 2     # What kind
    RELATION = 3    # How related
    PLACE = 4       # Where
    TIME = 5        # When
    POSTURE = 6     # Position/arrangement
    HAVING = 7      # Possession/condition
    ACTION = 8      # What it does
    PASSION = 9     # What is done to it


@dataclass(frozen=True)
class Category:
    """Definition of an Aristotelian category."""
    
    category_type: CategoryType
    name: str
    greek_name: str
    question: str
    description: str
    examples: Tuple[str, ...]
    is_substance: bool = False
    
    @property
    def index(self) -> int:
        return self.category_type.value
    
    @property
    def is_accident(self) -> bool:
        return not self.is_substance


# Define all ten categories
CATEGORY_ENTITY = Category(
    CategoryType.ENTITY,
    "Entity", "οὐσία (ousia)",
    "What is it?",
    "Primary being; that which exists in itself and can receive predicates",
    ("man", "horse", "tree", "stone"),
    is_substance=True
)

CATEGORY_QUANTITY = Category(
    CategoryType.QUANTITY,
    "Quantity", "ποσόν (poson)",
    "How much? How many?",
    "Extension in space or number",
    ("two cubits", "three", "large", "small")
)

CATEGORY_QUALITY = Category(
    CategoryType.QUALITY,
    "Quality", "ποιόν (poion)",
    "What kind?",
    "Characteristic property or state",
    ("white", "grammatical", "hot", "virtuous")
)

CATEGORY_RELATION = Category(
    CategoryType.RELATION,
    "Relation", "πρός τι (pros ti)",
    "Related to what?",
    "Reference to another entity",
    ("double", "half", "greater", "master of")
)

CATEGORY_PLACE = Category(
    CategoryType.PLACE,
    "Place", "ποῦ (pou)",
    "Where?",
    "Location in space",
    ("in the Lyceum", "in the marketplace", "here", "there")
)

CATEGORY_TIME = Category(
    CategoryType.TIME,
    "Time", "ποτέ (pote)",
    "When?",
    "Location in time",
    ("yesterday", "last year", "now", "then")
)

CATEGORY_POSTURE = Category(
    CategoryType.POSTURE,
    "Posture", "κεῖσθαι (keisthai)",
    "In what position?",
    "Arrangement of parts",
    ("lying", "sitting", "standing", "reclining")
)

CATEGORY_HAVING = Category(
    CategoryType.HAVING,
    "Having", "ἔχειν (echein)",
    "Having what?",
    "Possession or condition",
    ("armed", "shod", "clothed", "equipped")
)

CATEGORY_ACTION = Category(
    CategoryType.ACTION,
    "Action", "ποιεῖν (poiein)",
    "What does it do?",
    "Activity performed by entity",
    ("cutting", "burning", "teaching", "walking")
)

CATEGORY_PASSION = Category(
    CategoryType.PASSION,
    "Passion", "πάσχειν (paschein)",
    "What is done to it?",
    "Being affected by another",
    ("being cut", "being burned", "being taught", "being moved")
)

# All categories in a dict
ALL_CATEGORIES: Dict[int, Category] = {
    0: CATEGORY_ENTITY,
    1: CATEGORY_QUANTITY,
    2: CATEGORY_QUALITY,
    3: CATEGORY_RELATION,
    4: CATEGORY_PLACE,
    5: CATEGORY_TIME,
    6: CATEGORY_POSTURE,
    7: CATEGORY_HAVING,
    8: CATEGORY_ACTION,
    9: CATEGORY_PASSION,
}

# Substance category (primary)
SUBSTANCE_CATEGORY = CATEGORY_ENTITY

# Accident categories (1-9)
ACCIDENT_CATEGORIES: List[Category] = [
    ALL_CATEGORIES[i] for i in range(1, 10)
]


# =============================================================================
# PREDICATION
# =============================================================================

class PredicationError(Exception):
    """Error in categorical predication."""
    pass


@dataclass
class Term:
    """A term that can be subject or predicate."""
    
    name: str
    category: CategoryType
    properties: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def category_info(self) -> Category:
        return ALL_CATEGORIES[self.category.value]
    
    def can_be_subject(self) -> bool:
        """Only ENTITY can be subject."""
        return self.category == CategoryType.ENTITY
    
    def can_be_predicate(self) -> bool:
        """Categories 1-9 can be predicates."""
        return self.category != CategoryType.ENTITY


@dataclass
class Predication:
    """A predication of property to subject."""
    
    subject: Term
    predicate: Term
    is_affirmative: bool = True
    is_universal: bool = True
    
    def __post_init__(self):
        self.validate()
    
    def validate(self) -> None:
        """Validate predication follows categorical rules."""
        if not self.subject.can_be_subject():
            raise PredicationError(
                f"Non-entity '{self.subject.name}' cannot be subject. "
                f"Only ENTITY can serve as logical subject."
            )
        
        if not self.predicate.can_be_predicate():
            raise PredicationError(
                f"Entity '{self.predicate.name}' cannot be predicate. "
                f"Predicates must be from categories 1-9."
            )
    
    @property
    def statement(self) -> str:
        """Generate natural language statement."""
        quant = "All" if self.is_universal else "Some"
        copula = "are" if self.is_affirmative else "are not"
        return f"{quant} {self.subject.name} {copula} {self.predicate.name}"


def validate_subject(term: Term) -> bool:
    """Validate term can be subject."""
    if term.category != CategoryType.ENTITY:
        raise PredicationError(f"Non-entity subject: {term.name}")
    return True


def validate_predicate(term: Term) -> bool:
    """Validate term can be predicate."""
    if term.category == CategoryType.ENTITY:
        raise PredicationError(f"Entity as predicate: {term.name}")
    if term.category.value not in range(1, 10):
        raise PredicationError(f"Invalid predicate category: {term.category}")
    return True


# =============================================================================
# CATEGORY PROFILES
# =============================================================================

@dataclass
class CategoryProfile:
    """Profile of an entity across all categories."""
    
    entity: Term
    accidents: Dict[CategoryType, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.entity.category != CategoryType.ENTITY:
            raise PredicationError("Profile requires an entity")
    
    def set_accident(self, category: CategoryType, value: Any) -> None:
        """Set an accidental property."""
        if category == CategoryType.ENTITY:
            raise PredicationError("Cannot set ENTITY as accident")
        self.accidents[category] = value
    
    def get_accident(self, category: CategoryType) -> Optional[Any]:
        """Get value of an accident."""
        return self.accidents.get(category)
    
    def has_accident(self, category: CategoryType) -> bool:
        """Check if accident is defined."""
        return category in self.accidents
    
    def all_accidents(self) -> Dict[CategoryType, Any]:
        """Get all defined accidents."""
        return dict(self.accidents)
    
    def completeness(self) -> float:
        """Fraction of accident categories defined."""
        return len(self.accidents) / 9.0


def extract_category_profile(entity: Term, 
                             accident_values: Dict[CategoryType, Any]) -> CategoryProfile:
    """Extract a category profile for an entity."""
    profile = CategoryProfile(entity)
    for cat, value in accident_values.items():
        if value is not None and cat != CategoryType.ENTITY:
            profile.set_accident(cat, value)
    return profile


# =============================================================================
# THE FOUR CAUSES
# =============================================================================

class CauseType(Enum):
    """The four Aristotelian causes (aitiai)."""
    MATERIAL = auto()   # What it's made of
    FORMAL = auto()     # Its defining structure
    EFFICIENT = auto()  # What brought it about
    FINAL = auto()      # Its purpose/end (telos)


@dataclass(frozen=True)
class CauseDefinition:
    """Definition of a cause type."""
    
    cause_type: CauseType
    name: str
    greek_name: str
    question: str
    description: str
    examples: Tuple[str, ...]


CAUSE_MATERIAL = CauseDefinition(
    CauseType.MATERIAL,
    "Material Cause", "ὕλη (hyle)",
    "What is it made of?",
    "The matter or substrate from which something is made",
    ("bronze for a statue", "wood for a table", "letters for a syllable")
)

CAUSE_FORMAL = CauseDefinition(
    CauseType.FORMAL,
    "Formal Cause", "εἶδος (eidos) / μορφή (morphe)",
    "What is its form?",
    "The pattern, essence, or definition that makes it what it is",
    ("the shape of a statue", "the blueprint of a house", "the soul of a living thing")
)

CAUSE_EFFICIENT = CauseDefinition(
    CauseType.EFFICIENT,
    "Efficient Cause", "κινοῦν (kinoun)",
    "What made it?",
    "The agent or process that brought it into being",
    ("the sculptor who made the statue", "the father who begot the child", "the carpenter")
)

CAUSE_FINAL = CauseDefinition(
    CauseType.FINAL,
    "Final Cause", "τέλος (telos)",
    "What is it for?",
    "The purpose, goal, or end for which something exists",
    ("health as the goal of walking", "shelter as the purpose of a house", "happiness as the end of life")
)

ALL_CAUSES: Dict[CauseType, CauseDefinition] = {
    CauseType.MATERIAL: CAUSE_MATERIAL,
    CauseType.FORMAL: CAUSE_FORMAL,
    CauseType.EFFICIENT: CAUSE_EFFICIENT,
    CauseType.FINAL: CAUSE_FINAL,
}


# =============================================================================
# CAUSAL ANALYSIS
# =============================================================================

@dataclass
class CausalAnalysis:
    """Complete causal analysis of an entity."""
    
    entity: Term
    material: Optional[Any] = None
    formal: Optional[Any] = None
    efficient: Optional[Any] = None
    final: Optional[Any] = None
    
    def __post_init__(self):
        if self.entity.category != CategoryType.ENTITY:
            raise PredicationError("Causal analysis requires an entity")
    
    def set_cause(self, cause_type: CauseType, value: Any) -> None:
        """Set a cause."""
        if cause_type == CauseType.MATERIAL:
            self.material = value
        elif cause_type == CauseType.FORMAL:
            self.formal = value
        elif cause_type == CauseType.EFFICIENT:
            self.efficient = value
        elif cause_type == CauseType.FINAL:
            self.final = value
    
    def get_cause(self, cause_type: CauseType) -> Optional[Any]:
        """Get a cause."""
        if cause_type == CauseType.MATERIAL:
            return self.material
        elif cause_type == CauseType.FORMAL:
            return self.formal
        elif cause_type == CauseType.EFFICIENT:
            return self.efficient
        elif cause_type == CauseType.FINAL:
            return self.final
        return None
    
    def missing_causes(self) -> List[CauseType]:
        """Get list of undefined causes."""
        missing = []
        for cause_type in CauseType:
            if self.get_cause(cause_type) is None:
                missing.append(cause_type)
        return missing
    
    def is_complete(self) -> bool:
        """Check if all four causes are defined."""
        return len(self.missing_causes()) == 0
    
    def completeness_status(self) -> str:
        """Get completeness status."""
        missing = self.missing_causes()
        if not missing:
            return "COMPLETE"
        return f"INCOMPLETE (missing: {', '.join(c.name for c in missing)})"


def causal_completeness(entity: Term, 
                       causes: Dict[CauseType, Any]) -> CausalAnalysis:
    """Create causal analysis and check completeness."""
    analysis = CausalAnalysis(entity)
    for cause_type, value in causes.items():
        if value is not None:
            analysis.set_cause(cause_type, value)
    return analysis


# =============================================================================
# CAUSAL CHAIN TRAVERSAL
# =============================================================================

class CausalChainResult(Enum):
    """Result of causal chain traversal."""
    TERMINATED_NONE = auto()    # No further cause found
    TERMINATED_SELF = auto()    # Self-causing (Prime Mover)
    TERMINATED_DEPTH = auto()   # Max depth reached
    ERROR_CYCLE = auto()        # Cycle detected


@dataclass
class CausalChain:
    """A chain of causes."""
    
    chain: List[Term]
    cause_type: CauseType
    termination: CausalChainResult
    
    @property
    def length(self) -> int:
        return len(self.chain)
    
    @property
    def is_well_founded(self) -> bool:
        """Chain is well-founded if no cycle and has terminus."""
        return self.termination in (
            CausalChainResult.TERMINATED_NONE,
            CausalChainResult.TERMINATED_SELF
        )


def traverse_causal_chain(
    entity: Term,
    cause_type: CauseType,
    get_cause: Callable[[Term, CauseType], Optional[Term]],
    max_depth: int = 100
) -> CausalChain:
    """
    Traverse a causal chain from entity.
    
    Args:
        entity: Starting entity
        cause_type: Type of cause to follow
        get_cause: Function to get cause of an entity
        max_depth: Maximum traversal depth
    
    Returns:
        CausalChain with traversal results
    """
    chain = [entity]
    current = entity
    depth = 0
    
    while depth < max_depth:
        cause = get_cause(current, cause_type)
        
        if cause is None:
            return CausalChain(chain, cause_type, CausalChainResult.TERMINATED_NONE)
        
        if cause == current:
            return CausalChain(chain, cause_type, CausalChainResult.TERMINATED_SELF)
        
        if cause in chain:
            chain.append(cause)
            return CausalChain(chain, cause_type, CausalChainResult.ERROR_CYCLE)
        
        chain.append(cause)
        current = cause
        depth += 1
    
    return CausalChain(chain, cause_type, CausalChainResult.TERMINATED_DEPTH)


# =============================================================================
# HYLOMORPHISM
# =============================================================================

@dataclass
class HylomorphicEntity:
    """
    Entity as form-matter composite (hylomorphism).
    
    Every physical entity is a unity of:
    - Matter (hyle): The substrate that receives form
    - Form (morphe): The essence that makes it what it is
    """
    
    name: str
    matter: Any
    form: Any
    
    @property
    def is_composite(self) -> bool:
        """Physical entities are form-matter composites."""
        return self.matter is not None and self.form is not None
    
    @property
    def is_pure_form(self) -> bool:
        """Only divine entities are pure form without matter."""
        return self.matter is None and self.form is not None
    
    @property
    def is_prime_matter(self) -> bool:
        """Prime matter has no form (purely potential)."""
        return self.matter is not None and self.form is None


# =============================================================================
# ACTUALITY AND POTENTIALITY
# =============================================================================

class ActualityLevel(Enum):
    """Levels of actuality (energeia) vs potentiality (dynamis)."""
    PURE_POTENTIALITY = 0   # No actualized properties
    FIRST_ACTUALITY = 1     # Has form, capacity not exercised
    SECOND_ACTUALITY = 2    # Capacity actively exercised
    PURE_ACTUALITY = 3      # No unrealized potential


@dataclass
class ActualityState:
    """The actuality-potentiality state of an entity."""
    
    entity: Term
    level: ActualityLevel
    actualized_capacities: Set[str] = field(default_factory=set)
    potential_capacities: Set[str] = field(default_factory=set)
    
    @property
    def actuality_ratio(self) -> float:
        """Ratio of actualized to total capacities."""
        total = len(self.actualized_capacities) + len(self.potential_capacities)
        if total == 0:
            return 0.0
        return len(self.actualized_capacities) / total
    
    def actualize(self, capacity: str) -> None:
        """Move capacity from potential to actual."""
        if capacity in self.potential_capacities:
            self.potential_capacities.remove(capacity)
            self.actualized_capacities.add(capacity)
    
    def de_actualize(self, capacity: str) -> None:
        """Move capacity from actual to potential."""
        if capacity in self.actualized_capacities:
            self.actualized_capacities.remove(capacity)
            self.potential_capacities.add(capacity)


# =============================================================================
# CATEGORY SYSTEM
# =============================================================================

class CategorySystem:
    """Complete category system for the ATHENA OS."""
    
    def __init__(self):
        self.categories = ALL_CATEGORIES
        self.causes = ALL_CAUSES
        self.entities: Dict[str, Term] = {}
        self.profiles: Dict[str, CategoryProfile] = {}
        self.causal_analyses: Dict[str, CausalAnalysis] = {}
    
    def register_entity(self, name: str, **properties) -> Term:
        """Register a new entity."""
        entity = Term(name, CategoryType.ENTITY, properties)
        self.entities[name] = entity
        return entity
    
    def create_profile(self, entity_name: str, 
                      accidents: Dict[CategoryType, Any]) -> CategoryProfile:
        """Create category profile for entity."""
        entity = self.entities.get(entity_name)
        if not entity:
            raise PredicationError(f"Unknown entity: {entity_name}")
        profile = extract_category_profile(entity, accidents)
        self.profiles[entity_name] = profile
        return profile
    
    def create_causal_analysis(self, entity_name: str,
                              causes: Dict[CauseType, Any]) -> CausalAnalysis:
        """Create causal analysis for entity."""
        entity = self.entities.get(entity_name)
        if not entity:
            raise PredicationError(f"Unknown entity: {entity_name}")
        analysis = causal_completeness(entity, causes)
        self.causal_analyses[entity_name] = analysis
        return analysis
    
    def get_category_info(self, category_type: CategoryType) -> Category:
        """Get category definition."""
        return self.categories[category_type.value]
    
    def get_cause_info(self, cause_type: CauseType) -> CauseDefinition:
        """Get cause definition."""
        return self.causes[cause_type]


# =============================================================================
# VALIDATION
# =============================================================================

def validate_categories() -> bool:
    """Validate the categories module."""
    
    # Test categories
    assert len(ALL_CATEGORIES) == 10
    assert SUBSTANCE_CATEGORY.is_substance
    assert len(ACCIDENT_CATEGORIES) == 9
    assert all(c.is_accident for c in ACCIDENT_CATEGORIES)
    
    # Test predication rules
    man = Term("man", CategoryType.ENTITY)
    white = Term("white", CategoryType.QUALITY)
    
    assert man.can_be_subject()
    assert not man.can_be_predicate()
    assert not white.can_be_subject()
    assert white.can_be_predicate()
    
    # Test valid predication
    pred = Predication(man, white, is_affirmative=True, is_universal=True)
    assert pred.statement == "All man are white"
    
    # Test invalid predication (entity as predicate)
    horse = Term("horse", CategoryType.ENTITY)
    try:
        Predication(man, horse)
        assert False, "Should have raised PredicationError"
    except PredicationError:
        pass
    
    # Test category profile
    profile = CategoryProfile(man)
    profile.set_accident(CategoryType.QUALITY, "rational")
    profile.set_accident(CategoryType.QUANTITY, "one")
    assert profile.completeness() == 2/9
    
    # Test causes
    assert len(ALL_CAUSES) == 4
    
    # Test causal analysis
    analysis = CausalAnalysis(man)
    analysis.set_cause(CauseType.MATERIAL, "flesh and bone")
    analysis.set_cause(CauseType.FORMAL, "rational animal")
    analysis.set_cause(CauseType.EFFICIENT, "parents")
    assert not analysis.is_complete()
    analysis.set_cause(CauseType.FINAL, "eudaimonia")
    assert analysis.is_complete()
    
    # Test category system
    system = CategorySystem()
    socrates = system.register_entity("Socrates")
    profile = system.create_profile("Socrates", {
        CategoryType.QUALITY: "wise",
        CategoryType.PLACE: "Athens",
        CategoryType.TIME: "469-399 BCE"
    })
    assert profile.completeness() == 3/9
    
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("ATHENA OS - CATEGORIES MODULE")
    print("=" * 60)
    
    print("\nValidating categories...")
    assert validate_categories()
    print("✓ Categories validated")
    
    # Demo
    print("\n--- THE TEN CATEGORIES ---")
    for idx, cat in ALL_CATEGORIES.items():
        marker = "★" if cat.is_substance else " "
        print(f"  {marker} {idx}. {cat.name} ({cat.greek_name})")
        print(f"       {cat.question} - {cat.description}")
    
    print("\n--- THE FOUR CAUSES ---")
    for cause_type, cause in ALL_CAUSES.items():
        print(f"  • {cause.name} ({cause.greek_name})")
        print(f"    {cause.question}")
        print(f"    {cause.description}")
    
    print("\n--- EXAMPLE: Statue ---")
    statue = Term("statue", CategoryType.ENTITY)
    analysis = CausalAnalysis(statue)
    analysis.set_cause(CauseType.MATERIAL, "bronze")
    analysis.set_cause(CauseType.FORMAL, "shape of human figure")
    analysis.set_cause(CauseType.EFFICIENT, "sculptor")
    analysis.set_cause(CauseType.FINAL, "honor the depicted person")
    print(f"  Material: {analysis.material}")
    print(f"  Formal: {analysis.formal}")
    print(f"  Efficient: {analysis.efficient}")
    print(f"  Final: {analysis.final}")
    print(f"  Status: {analysis.completeness_status()}")
