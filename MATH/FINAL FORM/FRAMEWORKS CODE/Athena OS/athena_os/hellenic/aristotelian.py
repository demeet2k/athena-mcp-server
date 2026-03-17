"""
ATHENA OS - HELLENIC: ARISTOTELIAN LOGIC KERNEL
================================================
The Processing Unit and Type System

THE TEN CATEGORIES:
    1. Substance (οὐσία):    Object Identifier / Primary Key
    2. Quantity (ποσόν):     Metric Tensor / Int|Float
    3. Quality (ποιόν):      Attribute Set / Enum|Boolean
    4. Relation (πρός τι):   Pointer / Reference
    5. Place (ποῦ):          Vector3 (x,y,z)
    6. Time (ποτέ):          Timestamp (t)
    7. Position (κεῖσθαι):   Quaternion / Transform
    8. State (ἔχειν):        Wrapper / Equipment
    9. Action (ποιεῖν):      Method (Output)
    10. Passion (πάσχειν):   Event Listener (Input)

THE SYLLOGISM:
    S(P₁, P₂) → C
    
    Major Premise: M → P  [Universal Rule]
    Minor Premise: S → M  [Specific Instance]
    Conclusion:    S → P  [Computed Relationship]

THE FOUR CAUSES:
    Material (ὕλη):     What it's made of
    Formal (εἶδος):     What it is (essence)
    Efficient (κίνησις): What made it
    Final (τέλος):      What it's for
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Set, Type, Union
from enum import Enum, auto
from abc import ABC, abstractmethod
import numpy as np


# =============================================================================
# THE TEN CATEGORIES
# =============================================================================

class Category(Enum):
    """The Ten Aristotelian Categories."""
    
    SUBSTANCE = (1, "οὐσία", "Object/Instance", "Primary Key")
    QUANTITY = (2, "ποσόν", "Int/Float/Array", "Metric")
    QUALITY = (3, "ποιόν", "Enum/Boolean/State", "Attribute")
    RELATION = (4, "πρός τι", "Pointer/Reference", "Link")
    PLACE = (5, "ποῦ", "Vector3", "Location")
    TIME = (6, "ποτέ", "Timestamp", "Moment")
    POSITION = (7, "κεῖσθαι", "Quaternion/Transform", "Orientation")
    STATE = (8, "ἔχειν", "Wrapper/Equipment", "Having")
    ACTION = (9, "ποιεῖν", "Method/Output", "Doing")
    PASSION = (10, "πάσχειν", "EventListener/Input", "Receiving")
    
    @property
    def number(self) -> int:
        return self.value[0]
    
    @property
    def greek(self) -> str:
        return self.value[1]
    
    @property
    def data_type(self) -> str:
        return self.value[2]
    
    @property
    def role(self) -> str:
        return self.value[3]


@dataclass
class CategoryValue:
    """A value belonging to a specific category."""
    
    category: Category
    value: Any
    
    def is_substance(self) -> bool:
        return self.category == Category.SUBSTANCE
    
    def is_accident(self) -> bool:
        """Non-substance categories are accidents."""
        return self.category != Category.SUBSTANCE


@dataclass
class Substance:
    """
    Primary Substance (πρώτη οὐσία).
    
    The fundamental subject to which all other categories attach.
    "This man", "This horse" - concrete individuals.
    """
    
    id: str                              # Unique identifier
    species: str                         # Secondary substance (kind)
    genus: str = ""                      # Higher genus
    
    # Accidents (Categories 2-10)
    quantity: Optional[Any] = None       # How much/many
    quality: List[str] = field(default_factory=list)  # Properties
    relations: Dict[str, 'Substance'] = field(default_factory=dict)
    place: Optional[np.ndarray] = None   # Where
    time: Optional[float] = None         # When
    position: Optional[np.ndarray] = None  # Posture
    state: Dict[str, Any] = field(default_factory=dict)  # Having
    actions: List[str] = field(default_factory=list)  # What it does
    passions: List[str] = field(default_factory=list)  # What happens to it
    
    def add_quality(self, quality: str) -> None:
        """Add a quality (accident) to substance."""
        if quality not in self.quality:
            self.quality.append(quality)
    
    def add_relation(self, relation_type: str, other: 'Substance') -> None:
        """Add a relation to another substance."""
        self.relations[relation_type] = other
    
    def get_category_value(self, category: Category) -> Any:
        """Get value for given category."""
        mapping = {
            Category.SUBSTANCE: self,
            Category.QUANTITY: self.quantity,
            Category.QUALITY: self.quality,
            Category.RELATION: self.relations,
            Category.PLACE: self.place,
            Category.TIME: self.time,
            Category.POSITION: self.position,
            Category.STATE: self.state,
            Category.ACTION: self.actions,
            Category.PASSION: self.passions,
        }
        return mapping.get(category)


class CategoryChecker:
    """
    Type safety checker for categories.
    
    Prevents category errors - applying operators to
    incompatible categories (e.g., "How heavy is red?").
    """
    
    # Valid operations per category
    VALID_OPERATIONS = {
        Category.QUANTITY: {"add", "subtract", "multiply", "divide", "compare"},
        Category.QUALITY: {"has", "is", "equals"},
        Category.RELATION: {"relates_to", "inverse"},
        Category.PLACE: {"distance", "contains", "intersects"},
        Category.TIME: {"before", "after", "simultaneous"},
        Category.POSITION: {"rotate", "transform"},
        Category.STATE: {"has", "equipped"},
        Category.ACTION: {"performs", "can_do"},
        Category.PASSION: {"receives", "affected_by"},
    }
    
    @classmethod
    def check_operation(cls, value: CategoryValue, operation: str) -> bool:
        """Check if operation is valid for category."""
        if value.category == Category.SUBSTANCE:
            return True  # Substance can participate in all
        
        valid = cls.VALID_OPERATIONS.get(value.category, set())
        return operation in valid
    
    @classmethod
    def check_compatibility(cls, v1: CategoryValue, v2: CategoryValue,
                           operation: str) -> bool:
        """Check if two values are compatible for operation."""
        # Same category generally compatible
        if v1.category == v2.category:
            return cls.check_operation(v1, operation)
        
        # Substance compatible with anything
        if v1.is_substance() or v2.is_substance():
            return True
        
        return False


# =============================================================================
# THE SYLLOGISM
# =============================================================================

class SyllogisticFigure(Enum):
    """The four syllogistic figures."""
    
    FIRST = 1   # M-P, S-M ⊢ S-P
    SECOND = 2  # P-M, S-M ⊢ S-P
    THIRD = 3   # M-P, M-S ⊢ S-P
    FOURTH = 4  # P-M, M-S ⊢ S-P


class PropositionType(Enum):
    """Types of categorical propositions."""
    
    UNIVERSAL_AFFIRMATIVE = ("A", "All S are P", True, True)
    UNIVERSAL_NEGATIVE = ("E", "No S are P", True, False)
    PARTICULAR_AFFIRMATIVE = ("I", "Some S are P", False, True)
    PARTICULAR_NEGATIVE = ("O", "Some S are not P", False, False)
    
    @property
    def code(self) -> str:
        return self.value[0]
    
    @property
    def template(self) -> str:
        return self.value[1]
    
    @property
    def is_universal(self) -> bool:
        return self.value[2]
    
    @property
    def is_affirmative(self) -> bool:
        return self.value[3]


@dataclass
class Proposition:
    """
    A categorical proposition.
    
    Form: Quantifier + Subject + Copula + Predicate
    """
    
    subject: str
    predicate: str
    prop_type: PropositionType
    
    def __repr__(self) -> str:
        template = self.prop_type.template
        return template.replace("S", self.subject).replace("P", self.predicate)
    
    @property
    def is_universal(self) -> bool:
        return self.prop_type.is_universal
    
    @property
    def is_affirmative(self) -> bool:
        return self.prop_type.is_affirmative


@dataclass
class Syllogism:
    """
    A categorical syllogism.
    
    S(P₁, P₂) → C
    
    Major Premise: M → P
    Minor Premise: S → M
    Conclusion:    S → P
    """
    
    major_premise: Proposition
    minor_premise: Proposition
    
    def __post_init__(self):
        # Find middle term
        self.middle_term = self._find_middle_term()
        self.figure = self._determine_figure()
    
    def _find_middle_term(self) -> Optional[str]:
        """Find the middle term (appears in premises, not conclusion)."""
        major_terms = {self.major_premise.subject, self.major_premise.predicate}
        minor_terms = {self.minor_premise.subject, self.minor_premise.predicate}
        
        middle = major_terms & minor_terms
        return next(iter(middle)) if middle else None
    
    def _determine_figure(self) -> SyllogisticFigure:
        """Determine the syllogistic figure."""
        if self.middle_term is None:
            return SyllogisticFigure.FIRST
        
        m_is_subject_major = self.major_premise.subject == self.middle_term
        m_is_subject_minor = self.minor_premise.subject == self.middle_term
        
        if m_is_subject_major and not m_is_subject_minor:
            return SyllogisticFigure.FIRST
        elif not m_is_subject_major and not m_is_subject_minor:
            return SyllogisticFigure.SECOND
        elif m_is_subject_major and m_is_subject_minor:
            return SyllogisticFigure.THIRD
        else:
            return SyllogisticFigure.FOURTH
    
    def derive_conclusion(self) -> Optional[Proposition]:
        """
        Derive conclusion using syllogistic rules.
        
        The middle term links subject to predicate.
        """
        if self.middle_term is None:
            return None
        
        # Get major and minor terms
        major_terms = {self.major_premise.subject, self.major_premise.predicate}
        minor_terms = {self.minor_premise.subject, self.minor_premise.predicate}
        
        major_term = (major_terms - {self.middle_term}).pop() if major_terms - {self.middle_term} else None
        minor_term = (minor_terms - {self.middle_term}).pop() if minor_terms - {self.middle_term} else None
        
        if major_term is None or minor_term is None:
            return None
        
        # Determine conclusion type based on premises
        # Simplified rules
        if self.major_premise.is_affirmative and self.minor_premise.is_affirmative:
            if self.major_premise.is_universal and self.minor_premise.is_universal:
                prop_type = PropositionType.UNIVERSAL_AFFIRMATIVE
            else:
                prop_type = PropositionType.PARTICULAR_AFFIRMATIVE
        elif not self.major_premise.is_affirmative or not self.minor_premise.is_affirmative:
            if self.major_premise.is_universal and self.minor_premise.is_universal:
                prop_type = PropositionType.UNIVERSAL_NEGATIVE
            else:
                prop_type = PropositionType.PARTICULAR_NEGATIVE
        else:
            prop_type = PropositionType.PARTICULAR_AFFIRMATIVE
        
        return Proposition(minor_term, major_term, prop_type)
    
    def is_valid(self) -> bool:
        """Check if syllogism follows valid rules."""
        # Rule 1: Middle term must be distributed at least once
        # Rule 2: No term distributed in conclusion that wasn't in premises
        # Rule 3: Two negative premises yield no conclusion
        # Rule 4: Negative premise requires negative conclusion
        # Rule 5: Two universal premises with particular conclusion
        
        # Simplified check
        if self.middle_term is None:
            return False
        
        # Both premises negative = invalid
        if not self.major_premise.is_affirmative and not self.minor_premise.is_affirmative:
            return False
        
        return True
    
    @property
    def mood(self) -> str:
        """Return mood (e.g., 'AAA', 'EIO')."""
        return (self.major_premise.prop_type.code + 
                self.minor_premise.prop_type.code +
                (self.derive_conclusion().prop_type.code 
                 if self.derive_conclusion() else "?"))


class SyllogisticEngine:
    """
    The syllogistic inference engine.
    
    Compiles knowledge base and performs deductions.
    """
    
    def __init__(self):
        self.knowledge_base: List[Proposition] = []
    
    def add_proposition(self, prop: Proposition) -> None:
        """Add proposition to knowledge base."""
        self.knowledge_base.append(prop)
    
    def find_syllogisms(self) -> List[Syllogism]:
        """Find all valid syllogisms from knowledge base."""
        syllogisms = []
        
        for i, p1 in enumerate(self.knowledge_base):
            for p2 in self.knowledge_base[i+1:]:
                syl = Syllogism(p1, p2)
                if syl.is_valid():
                    syllogisms.append(syl)
        
        return syllogisms
    
    def infer(self, query_subject: str, query_predicate: str) -> List[Proposition]:
        """Infer propositions relating subject to predicate."""
        results = []
        
        for syl in self.find_syllogisms():
            conclusion = syl.derive_conclusion()
            if conclusion:
                if (conclusion.subject == query_subject and 
                    conclusion.predicate == query_predicate):
                    results.append(conclusion)
        
        return results


# =============================================================================
# THE FOUR CAUSES
# =============================================================================

class CauseType(Enum):
    """The Four Aristotelian Causes."""
    
    MATERIAL = ("ὕλη", "What it's made of", "Internal", "Structural")
    FORMAL = ("εἶδος", "What it is (essence)", "Internal", "Telic")
    EFFICIENT = ("κίνησις", "What made it", "External", "Structural")
    FINAL = ("τέλος", "What it's for", "External", "Telic")
    
    @property
    def greek(self) -> str:
        return self.value[0]
    
    @property
    def description(self) -> str:
        return self.value[1]
    
    @property
    def axis1(self) -> str:
        """Internal/External axis."""
        return self.value[2]
    
    @property
    def axis2(self) -> str:
        """Structural/Telic axis."""
        return self.value[3]


@dataclass
class CausalVector:
    """
    The four-cause explanation of an entity.
    
    Complete explanation requires all four causes.
    """
    
    material: Any = None    # What it's made of
    formal: Any = None      # Its essence/form
    efficient: Any = None   # Its origin/maker
    final: Any = None       # Its purpose/goal
    
    def is_complete(self) -> bool:
        """Check if all four causes are specified."""
        return all([
            self.material is not None,
            self.formal is not None,
            self.efficient is not None,
            self.final is not None
        ])
    
    def get_cause(self, cause_type: CauseType) -> Any:
        """Get specific cause."""
        mapping = {
            CauseType.MATERIAL: self.material,
            CauseType.FORMAL: self.formal,
            CauseType.EFFICIENT: self.efficient,
            CauseType.FINAL: self.final,
        }
        return mapping.get(cause_type)
    
    def as_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "material": self.material,
            "formal": self.formal,
            "efficient": self.efficient,
            "final": self.final,
        }


class CausalAnalyzer:
    """
    Analyzer for causal explanations.
    
    Validates and completes causal accounts.
    """
    
    @staticmethod
    def analyze(entity: Any) -> CausalVector:
        """
        Attempt to extract causal vector from entity.
        
        Uses introspection where possible.
        """
        vector = CausalVector()
        
        # Material: Look for composition
        if hasattr(entity, '__dict__'):
            vector.material = list(entity.__dict__.keys())
        elif isinstance(entity, dict):
            vector.material = list(entity.keys())
        else:
            vector.material = type(entity).__name__
        
        # Formal: The type/class
        vector.formal = type(entity).__name__
        
        # Efficient: Constructor
        if hasattr(entity, '__init__'):
            vector.efficient = f"{type(entity).__name__}.__init__"
        else:
            vector.efficient = "Unknown"
        
        # Final: Purpose (if documented)
        if hasattr(entity, '__doc__') and entity.__doc__:
            vector.final = entity.__doc__.split('\n')[0]
        else:
            vector.final = "Not specified"
        
        return vector
    
    @staticmethod
    def validate_explanation(vector: CausalVector) -> Dict[CauseType, bool]:
        """Validate each cause in the vector."""
        return {
            CauseType.MATERIAL: vector.material is not None,
            CauseType.FORMAL: vector.formal is not None,
            CauseType.EFFICIENT: vector.efficient is not None,
            CauseType.FINAL: vector.final is not None,
        }
    
    @staticmethod
    def completeness_score(vector: CausalVector) -> float:
        """Score from 0-1 based on completeness."""
        count = sum([
            vector.material is not None,
            vector.formal is not None,
            vector.efficient is not None,
            vector.final is not None,
        ])
        return count / 4.0


# =============================================================================
# VALIDATION
# =============================================================================

def validate_aristotelian() -> bool:
    """Validate Aristotelian logic kernel module."""
    
    # Test Categories
    assert len(list(Category)) == 10
    assert Category.SUBSTANCE.number == 1
    assert Category.PASSION.number == 10
    
    # Test Substance
    socrates = Substance(
        id="socrates_1",
        species="Human",
        genus="Animal",
        quantity={"age": 70, "height": 1.7},
    )
    
    socrates.add_quality("Wise")
    socrates.add_quality("Snub-nosed")
    
    assert "Wise" in socrates.quality
    assert socrates.get_category_value(Category.SUBSTANCE) == socrates
    
    # Test CategoryChecker
    qty_value = CategoryValue(Category.QUANTITY, 10)
    assert CategoryChecker.check_operation(qty_value, "add")
    assert not CategoryChecker.check_operation(qty_value, "has")
    
    # Test Propositions
    p1 = Proposition("Humans", "Mortal", PropositionType.UNIVERSAL_AFFIRMATIVE)
    p2 = Proposition("Socrates", "Human", PropositionType.UNIVERSAL_AFFIRMATIVE)
    
    assert p1.is_universal
    assert p1.is_affirmative
    assert "All Humans are Mortal" in str(p1)
    
    # Test Syllogism
    syl = Syllogism(p1, p2)
    
    assert syl.middle_term == "Human"  # or "Humans"
    assert syl.is_valid()
    
    conclusion = syl.derive_conclusion()
    assert conclusion is not None
    
    # Test SyllogisticEngine
    engine = SyllogisticEngine()
    engine.add_proposition(p1)
    engine.add_proposition(p2)
    
    syllogisms = engine.find_syllogisms()
    assert len(syllogisms) > 0
    
    # Test CauseType
    assert len(list(CauseType)) == 4
    assert CauseType.MATERIAL.axis1 == "Internal"
    assert CauseType.FINAL.axis2 == "Telic"
    
    # Test CausalVector
    house_causes = CausalVector(
        material="Bricks, wood, concrete",
        formal="House (shelter structure)",
        efficient="Builder/Construction",
        final="To provide shelter",
    )
    
    assert house_causes.is_complete()
    assert house_causes.get_cause(CauseType.FINAL) == "To provide shelter"
    
    # Test CausalAnalyzer
    vector = CausalAnalyzer.analyze(socrates)
    
    assert vector.formal == "Substance"
    assert CausalAnalyzer.completeness_score(vector) == 1.0
    
    return True


if __name__ == "__main__":
    print("Validating Aristotelian Logic Kernel...")
    assert validate_aristotelian()
    print("✓ Aristotelian Logic Kernel validated")
    
    print("\n--- Ten Categories ---")
    for cat in Category:
        print(f"  {cat.number}. {cat.name}: {cat.greek} ({cat.data_type})")
    
    print("\n--- Syllogism Demo ---")
    p1 = Proposition("Mortal", "Living", PropositionType.UNIVERSAL_AFFIRMATIVE)
    p2 = Proposition("Human", "Mortal", PropositionType.UNIVERSAL_AFFIRMATIVE)
    
    syl = Syllogism(p1, p2)
    print(f"  Major: {p1}")
    print(f"  Minor: {p2}")
    print(f"  Middle term: {syl.middle_term}")
    print(f"  Figure: {syl.figure.name}")
    print(f"  Mood: {syl.mood}")
    print(f"  Conclusion: {syl.derive_conclusion()}")
    
    print("\n--- Four Causes ---")
    for cause in CauseType:
        print(f"  {cause.name}: {cause.greek} - {cause.description}")
