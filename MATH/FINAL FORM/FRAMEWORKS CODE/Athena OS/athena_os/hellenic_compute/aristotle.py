"""
ATHENA OS - HELLENIC COMPUTATION FRAMEWORK
==========================================
Part V: The Logic Kernel (Aristotle)

THE TEN CATEGORIES (Type System):
    Aristotle's categories as a complete type system:
    1. Substance (οὐσία) - "what it is"
    2. Quantity (ποσόν) - "how much"
    3. Quality (ποιόν) - "of what kind"
    4. Relation (πρός τι) - "relative to what"
    5. Place (ποῦ) - "where"
    6. Time (πότε) - "when"
    7. Position (κεῖσθαι) - "in what posture"
    8. State (ἔχειν) - "having what"
    9. Action (ποιεῖν) - "doing what"
    10. Passion (πάσχειν) - "undergoing what"

THE SYLLOGISM (Compilation Algorithm):
    The syllogistic forms as proof procedures:
    - Barbara: All M are P, All S are M ⊢ All S are P
    - Celarent: No M are P, All S are M ⊢ No S are P
    - And 14 more valid forms across 4 figures

THE FOUR CAUSES (Causal Vector):
    Complete explanation requires four causes:
    - Material: "out of what?"
    - Formal: "what is it?"
    - Efficient: "by what agent?"
    - Final: "for what purpose?"

THE KNOWLEDGE GRAPH:
    Aristotle's science as a connected graph of demonstrations.

SOURCES:
    - THE_HELLENIC_COMPUTATION_FRAMEWORK.docx Part V
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Set, Any, Union
from enum import Enum, auto
from abc import ABC, abstractmethod
import numpy as np

from .foundation import StateVector, Klein4Op, Element


# =============================================================================
# THE TEN CATEGORIES
# =============================================================================

class Category(Enum):
    """
    Aristotle's ten categories - the fundamental types.
    
    Every predicate falls under exactly one category.
    """
    
    SUBSTANCE = ("substance", "τί ἐστι", "what it is", True)
    QUANTITY = ("quantity", "ποσόν", "how much", False)
    QUALITY = ("quality", "ποιόν", "of what kind", False)
    RELATION = ("relation", "πρός τι", "relative to what", False)
    PLACE = ("place", "ποῦ", "where", False)
    TIME = ("time", "πότε", "when", False)
    POSITION = ("position", "κεῖσθαι", "in what posture", False)
    STATE = ("state", "ἔχειν", "having what", False)
    ACTION = ("action", "ποιεῖν", "doing what", False)
    PASSION = ("passion", "πάσχειν", "undergoing what", False)
    
    def __init__(self, name: str, greek: str, question: str, 
                 is_primary: bool):
        self._name = name
        self.greek = greek
        self.question = question
        self.is_primary = is_primary
    
    @classmethod
    def primary(cls) -> Category:
        """Return the primary category (Substance)."""
        return cls.SUBSTANCE
    
    @classmethod
    def accidents(cls) -> List[Category]:
        """Return all accident categories."""
        return [c for c in cls if not c.is_primary]
    
    def is_inherent(self) -> bool:
        """Check if category is inherent in substance."""
        return self in [Category.QUALITY, Category.QUANTITY]
    
    def is_relational(self) -> bool:
        """Check if category is relational."""
        return self in [Category.RELATION, Category.PLACE, Category.TIME]


@dataclass
class Predicate:
    """
    A predicate classified under a category.
    """
    
    name: str
    category: Category
    definition: str = ""
    
    def can_be_said_of(self, subject: Substance) -> bool:
        """Check if predicate can be said of subject."""
        return True  # Simplified - would check compatibility
    
    def __repr__(self) -> str:
        return f"{self.name} ({self.category.value[0]})"


@dataclass
class Substance:
    """
    A primary substance (individual) or secondary substance (species/genus).
    """
    
    name: str
    is_primary: bool = True  # Individual vs species
    genus: Optional[Substance] = None
    species: List[Substance] = field(default_factory=list)
    predicates: Dict[Category, List[Predicate]] = field(default_factory=dict)
    
    def add_predicate(self, predicate: Predicate) -> None:
        """Add a predicate to this substance."""
        cat = predicate.category
        if cat not in self.predicates:
            self.predicates[cat] = []
        self.predicates[cat].append(predicate)
    
    def get_predicates(self, category: Category) -> List[Predicate]:
        """Get all predicates of a category."""
        return self.predicates.get(category, [])
    
    def inherits_from(self, other: Substance) -> bool:
        """Check if this substance inherits from another."""
        if self.genus == other:
            return True
        if self.genus:
            return self.genus.inherits_from(other)
        return False


# =============================================================================
# THE SYLLOGISM
# =============================================================================

class Quantifier(Enum):
    """Syllogistic quantifiers."""
    
    ALL = "all"      # Universal affirmative (A)
    NONE = "no"      # Universal negative (E)
    SOME = "some"    # Particular affirmative (I)
    SOME_NOT = "some...not"  # Particular negative (O)
    
    @property
    def code(self) -> str:
        """Get traditional letter code."""
        codes = {
            Quantifier.ALL: "A",
            Quantifier.NONE: "E",
            Quantifier.SOME: "I",
            Quantifier.SOME_NOT: "O",
        }
        return codes[self]
    
    def is_universal(self) -> bool:
        return self in [Quantifier.ALL, Quantifier.NONE]
    
    def is_affirmative(self) -> bool:
        return self in [Quantifier.ALL, Quantifier.SOME]


@dataclass
class Proposition:
    """
    A categorical proposition: Quantifier + Subject + Predicate
    """
    
    quantifier: Quantifier
    subject: str
    predicate: str
    
    def __repr__(self) -> str:
        if self.quantifier == Quantifier.ALL:
            return f"All {self.subject} are {self.predicate}"
        elif self.quantifier == Quantifier.NONE:
            return f"No {self.subject} are {self.predicate}"
        elif self.quantifier == Quantifier.SOME:
            return f"Some {self.subject} are {self.predicate}"
        else:
            return f"Some {self.subject} are not {self.predicate}"
    
    @property
    def mood(self) -> str:
        """Get proposition type (A, E, I, O)."""
        return self.quantifier.code
    
    def contradict(self) -> Proposition:
        """Get contradictory proposition."""
        contradictions = {
            Quantifier.ALL: Quantifier.SOME_NOT,
            Quantifier.NONE: Quantifier.SOME,
            Quantifier.SOME: Quantifier.NONE,
            Quantifier.SOME_NOT: Quantifier.ALL,
        }
        return Proposition(
            contradictions[self.quantifier],
            self.subject,
            self.predicate
        )
    
    def converse(self) -> Optional[Proposition]:
        """Get converse (swap subject and predicate)."""
        # Only E and I convert simply
        if self.quantifier == Quantifier.NONE:
            return Proposition(Quantifier.NONE, self.predicate, self.subject)
        elif self.quantifier == Quantifier.SOME:
            return Proposition(Quantifier.SOME, self.predicate, self.subject)
        elif self.quantifier == Quantifier.ALL:
            # A converts to I (not A)
            return Proposition(Quantifier.SOME, self.predicate, self.subject)
        return None


@dataclass
class Syllogism:
    """
    A syllogism: two premises and a conclusion.
    
    Three terms: Major (P), Minor (S), Middle (M)
    """
    
    major_premise: Proposition  # Contains major term (P) and middle term (M)
    minor_premise: Proposition  # Contains minor term (S) and middle term (M)
    conclusion: Proposition     # Contains major term (P) and minor term (S)
    
    @property
    def mood(self) -> str:
        """Get syllogism mood (e.g., 'AAA' for Barbara)."""
        return (self.major_premise.mood + 
                self.minor_premise.mood + 
                self.conclusion.mood)
    
    @property
    def figure(self) -> int:
        """
        Determine figure (1-4) based on middle term position.
        
        Figure 1: M-P, S-M (middle is subject of major, predicate of minor)
        Figure 2: P-M, S-M (middle is predicate of both)
        Figure 3: M-P, M-S (middle is subject of both)
        Figure 4: P-M, M-S (middle is predicate of major, subject of minor)
        """
        # Simplified: would analyze term positions
        return 1
    
    def is_valid(self) -> bool:
        """Check if syllogism is valid."""
        # Check against valid forms
        valid_forms = VALID_SYLLOGISMS.get(self.figure, [])
        return self.mood in valid_forms


# Valid syllogistic forms by figure
VALID_SYLLOGISMS = {
    1: ["AAA", "EAE", "AII", "EIO"],  # Barbara, Celarent, Darii, Ferio
    2: ["EAE", "AEE", "EIO", "AOO"],  # Cesare, Camestres, Festino, Baroco
    3: ["IAI", "AII", "OAO", "EIO"],  # Disamis, Datisi, Bocardo, Ferison
    4: ["AEE", "IAI", "EIO"],          # Camenes, Dimaris, Fresison
}

# Named syllogisms
SYLLOGISM_NAMES = {
    ("AAA", 1): "Barbara",
    ("EAE", 1): "Celarent",
    ("AII", 1): "Darii",
    ("EIO", 1): "Ferio",
    ("EAE", 2): "Cesare",
    ("AEE", 2): "Camestres",
    ("EIO", 2): "Festino",
    ("AOO", 2): "Baroco",
}


class SyllogisticEngine:
    """
    Engine for syllogistic reasoning.
    """
    
    def __init__(self):
        self.propositions: List[Proposition] = []
    
    def add_proposition(self, prop: Proposition) -> None:
        """Add a proposition to the knowledge base."""
        self.propositions.append(prop)
    
    def construct_syllogism(self, major: Proposition,
                           minor: Proposition,
                           conclusion: Proposition) -> Syllogism:
        """Construct a syllogism from propositions."""
        return Syllogism(major, minor, conclusion)
    
    def validate(self, syllogism: Syllogism) -> Tuple[bool, str]:
        """
        Validate a syllogism and return reason.
        """
        mood = syllogism.mood
        figure = syllogism.figure
        
        if syllogism.is_valid():
            name = SYLLOGISM_NAMES.get((mood, figure), "Valid")
            return (True, f"Valid: {name}")
        
        # Check specific fallacies
        return (False, "Invalid syllogism")
    
    def infer(self, major: Proposition, 
             minor: Proposition) -> Optional[Proposition]:
        """
        Attempt to infer a valid conclusion from premises.
        """
        # Extract terms
        # This is simplified - full implementation would parse terms
        
        # Try Barbara (AAA-1) pattern
        if (major.quantifier == Quantifier.ALL and 
            minor.quantifier == Quantifier.ALL):
            return Proposition(
                Quantifier.ALL,
                minor.subject,
                major.predicate
            )
        
        return None


# =============================================================================
# THE FOUR CAUSES
# =============================================================================

class CauseType(Enum):
    """Aristotle's four causes."""
    
    MATERIAL = ("material", "out of what?", "ὕλη")
    FORMAL = ("formal", "what is it?", "εἶδος")
    EFFICIENT = ("efficient", "by what agent?", "ἀρχὴ τῆς κινήσεως")
    FINAL = ("final", "for what purpose?", "τέλος")
    
    def __init__(self, name: str, question: str, greek: str):
        self._name = name
        self.question = question
        self.greek = greek
    
    def to_state(self) -> StateVector:
        """Map to 2-bit state space."""
        mapping = {
            CauseType.MATERIAL: StateVector(0, 0),
            CauseType.FORMAL: StateVector(0, 1),
            CauseType.EFFICIENT: StateVector(1, 0),
            CauseType.FINAL: StateVector(1, 1),
        }
        return mapping[self]


@dataclass
class Cause:
    """A specific cause."""
    
    cause_type: CauseType
    description: str
    
    def __repr__(self) -> str:
        return f"{self.cause_type.value[0]}: {self.description}"


@dataclass
class CausalVector:
    """
    Complete causal explanation (all four causes).
    """
    
    material: Optional[Cause] = None
    formal: Optional[Cause] = None
    efficient: Optional[Cause] = None
    final: Optional[Cause] = None
    
    def is_complete(self) -> bool:
        """Check if all causes are specified."""
        return all([
            self.material is not None,
            self.formal is not None,
            self.efficient is not None,
            self.final is not None,
        ])
    
    def missing(self) -> List[CauseType]:
        """Get list of missing causes."""
        missing = []
        if self.material is None:
            missing.append(CauseType.MATERIAL)
        if self.formal is None:
            missing.append(CauseType.FORMAL)
        if self.efficient is None:
            missing.append(CauseType.EFFICIENT)
        if self.final is None:
            missing.append(CauseType.FINAL)
        return missing
    
    def set_cause(self, cause: Cause) -> None:
        """Set a cause by type."""
        if cause.cause_type == CauseType.MATERIAL:
            self.material = cause
        elif cause.cause_type == CauseType.FORMAL:
            self.formal = cause
        elif cause.cause_type == CauseType.EFFICIENT:
            self.efficient = cause
        elif cause.cause_type == CauseType.FINAL:
            self.final = cause
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary."""
        return {
            "material": self.material.description if self.material else None,
            "formal": self.formal.description if self.formal else None,
            "efficient": self.efficient.description if self.efficient else None,
            "final": self.final.description if self.final else None,
        }


# =============================================================================
# ACTUALITY AND POTENTIALITY
# =============================================================================

class ActualityState(Enum):
    """States along the potentiality-actuality spectrum."""
    
    PURE_POTENTIALITY = 0   # Prime matter
    POTENTIALITY = 1        # Capacity exists
    MOTION = 2              # Actualization in progress
    ACTUALITY = 3           # First actuality (hexis)
    ACTIVITY = 4            # Second actuality (energeia)
    PURE_ACTUALITY = 5      # God/Unmoved Mover


@dataclass
class PotentialActual:
    """
    Model of potentiality (δύναμις) and actuality (ἐνέργεια).
    """
    
    state: ActualityState
    capacity: float = 0.0   # Degree of potential (0-1)
    realization: float = 0.0  # Degree of actual (0-1)
    
    def actualize(self, amount: float) -> None:
        """Move from potential to actual."""
        transfer = min(amount, self.capacity)
        self.capacity -= transfer
        self.realization += transfer
        self._update_state()
    
    def _update_state(self) -> None:
        """Update state based on values."""
        ratio = self.realization / (self.capacity + self.realization + 0.001)
        if ratio < 0.2:
            self.state = ActualityState.POTENTIALITY
        elif ratio < 0.5:
            self.state = ActualityState.MOTION
        elif ratio < 0.8:
            self.state = ActualityState.ACTUALITY
        else:
            self.state = ActualityState.ACTIVITY


# =============================================================================
# KNOWLEDGE GRAPH
# =============================================================================

@dataclass
class Demonstration:
    """
    A scientific demonstration (ἀπόδειξις).
    
    Aristotelian science proceeds by demonstrations from first principles.
    """
    
    name: str
    premises: List[Proposition]
    conclusion: Proposition
    principles: List[str] = field(default_factory=list)
    
    def is_valid(self) -> bool:
        """Check if demonstration is logically valid."""
        if len(self.premises) < 2:
            return False
        # Would validate syllogistically
        return True


class KnowledgeGraph:
    """
    Graph of scientific knowledge.
    
    Nodes are propositions; edges are demonstrations.
    """
    
    def __init__(self):
        self.propositions: Dict[str, Proposition] = {}
        self.demonstrations: List[Demonstration] = []
        self.first_principles: Set[str] = set()
    
    def add_principle(self, name: str, prop: Proposition) -> None:
        """Add a first principle (axiom)."""
        self.propositions[name] = prop
        self.first_principles.add(name)
    
    def add_demonstration(self, demo: Demonstration) -> None:
        """Add a demonstration to the graph."""
        self.demonstrations.append(demo)
        self.propositions[demo.name] = demo.conclusion
    
    def derive(self, prop_name: str) -> Optional[List[Demonstration]]:
        """Find derivation chain for a proposition."""
        if prop_name in self.first_principles:
            return []  # First principles need no derivation
        
        for demo in self.demonstrations:
            if demo.name == prop_name:
                chain = [demo]
                # Recursively find premises
                for premise in demo.premises:
                    # Would trace back to principles
                    pass
                return chain
        
        return None


# =============================================================================
# VALIDATION
# =============================================================================

def validate_aristotle() -> bool:
    """Validate Aristotelian logic module."""
    
    # Test Categories
    assert Category.SUBSTANCE.is_primary
    assert len(Category.accidents()) == 9
    
    pred = Predicate("white", Category.QUALITY)
    assert pred.category == Category.QUALITY
    
    # Test Substance
    animal = Substance("Animal", is_primary=False)
    human = Substance("Human", is_primary=False, genus=animal)
    socrates = Substance("Socrates", is_primary=True, genus=human)
    
    assert socrates.inherits_from(human)
    assert socrates.inherits_from(animal)
    
    # Test Proposition
    prop = Proposition(Quantifier.ALL, "humans", "mortal")
    assert str(prop) == "All humans are mortal"
    assert prop.mood == "A"
    
    contra = prop.contradict()
    assert contra.quantifier == Quantifier.SOME_NOT
    
    # Test Syllogism
    major = Proposition(Quantifier.ALL, "animals", "mortal")
    minor = Proposition(Quantifier.ALL, "humans", "animals")
    conclusion = Proposition(Quantifier.ALL, "humans", "mortal")
    
    barbara = Syllogism(major, minor, conclusion)
    assert barbara.mood == "AAA"
    assert barbara.is_valid()
    
    # Test Four Causes
    material = Cause(CauseType.MATERIAL, "bronze")
    formal = Cause(CauseType.FORMAL, "shape of statue")
    efficient = Cause(CauseType.EFFICIENT, "sculptor")
    final = Cause(CauseType.FINAL, "to honor the god")
    
    cv = CausalVector()
    assert not cv.is_complete()
    assert len(cv.missing()) == 4
    
    cv.set_cause(material)
    cv.set_cause(formal)
    cv.set_cause(efficient)
    cv.set_cause(final)
    assert cv.is_complete()
    
    # Test CauseType to StateVector mapping
    assert CauseType.MATERIAL.to_state() == StateVector(0, 0)
    assert CauseType.FINAL.to_state() == StateVector(1, 1)
    
    # Test Potentiality/Actuality
    pa = PotentialActual(
        state=ActualityState.POTENTIALITY,
        capacity=1.0,
        realization=0.0
    )
    pa.actualize(0.5)
    assert pa.realization == 0.5
    
    return True


if __name__ == "__main__":
    print("Validating Aristotelian Logic Module...")
    assert validate_aristotle()
    print("✓ Aristotelian module validated")
    
    # Demo
    print("\n--- Aristotelian Logic Kernel Demo ---")
    
    print("\n1. The Ten Categories:")
    for cat in Category:
        mark = "*" if cat.is_primary else " "
        print(f"   {mark} {cat.value[0]}: {cat.question}")
    
    print("\n2. Classic Syllogism (Barbara):")
    major = Proposition(Quantifier.ALL, "animals", "mortal")
    minor = Proposition(Quantifier.ALL, "humans", "animals")
    conclusion = Proposition(Quantifier.ALL, "humans", "mortal")
    
    print(f"   Major: {major}")
    print(f"   Minor: {minor}")
    print(f"   ∴ Conclusion: {conclusion}")
    
    syl = Syllogism(major, minor, conclusion)
    print(f"\n   Mood: {syl.mood}")
    print(f"   Figure: {syl.figure}")
    print(f"   Valid: {syl.is_valid()}")
    
    print("\n3. The Four Causes (Statue Example):")
    cv = CausalVector(
        material=Cause(CauseType.MATERIAL, "bronze"),
        formal=Cause(CauseType.FORMAL, "shape of Apollo"),
        efficient=Cause(CauseType.EFFICIENT, "Phidias the sculptor"),
        final=Cause(CauseType.FINAL, "to honor Apollo")
    )
    
    for cause_type, desc in cv.to_dict().items():
        print(f"   {cause_type.capitalize()}: {desc}")
    
    print("\n4. Cause-to-Element Mapping:")
    for ct in CauseType:
        state = ct.to_state()
        elem = Element.from_state(state)
        print(f"   {ct.value[0]} → {state} → {elem.value}")
    
    print("\n5. Potentiality → Actuality:")
    pa = PotentialActual(ActualityState.POTENTIALITY, capacity=1.0)
    stages = ["Initial", "Growing", "Developed", "Complete"]
    for i, stage in enumerate(stages):
        print(f"   {stage}: potential={pa.capacity:.2f}, actual={pa.realization:.2f}, state={pa.state.name}")
        pa.actualize(0.3)
