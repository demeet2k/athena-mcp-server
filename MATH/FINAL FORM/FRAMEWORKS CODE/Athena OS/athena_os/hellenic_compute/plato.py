"""
ATHENA OS - HELLENIC COMPUTATION FRAMEWORK
==========================================
Part IV: The Type System (Plato)

THE FOUR-VARIABLE COMPILER (Timaeus):
    Plato's cosmology compiles the universe from four types:
    - Being (τὸ ὄν): Eternal, unchanging Forms
    - Becoming (τὸ γιγνόμενον): Temporal, changing instances
    - Space (χώρα): The Receptacle, coordinate system
    - Demiurge (δημιουργός): The compiler/constructor

THE RECEPTACLE (Chora):
    The coordinate system in which Forms are instantiated.
    Neither Being nor Becoming, but the medium for both.
    Functions as the type environment.

GEOMETRIC ATOMISM:
    The five Platonic solids as atomic types:
    - Tetrahedron → Fire (4 faces)
    - Octahedron → Air (8 faces)
    - Icosahedron → Water (20 faces)
    - Cube → Earth (6 faces)
    - Dodecahedron → Cosmos (12 faces)

THE OPTIMIZATION FUNCTION (The Good):
    The Good (τὸ ἀγαθόν) is the objective function.
    All Forms participate in the Good.
    The compiler optimizes toward the Good.

SOURCES:
    - THE_HELLENIC_COMPUTATION_FRAMEWORK.docx Part IV
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Set, Any, TypeVar, Generic
from enum import Enum
from abc import ABC, abstractmethod
import numpy as np
import math


# =============================================================================
# PLATONIC ONTOLOGY
# =============================================================================

class OntologicalLevel(Enum):
    """The levels of Platonic reality."""
    
    THE_GOOD = "good"           # τὸ ἀγαθόν - ultimate principle
    BEING = "being"             # τὸ ὄν - eternal Forms
    BECOMING = "becoming"       # τὸ γιγνόμενον - sensible world
    SPACE = "space"             # χώρα - receptacle
    NONBEING = "nonbeing"       # τὸ μὴ ὄν - privation
    
    @property
    def rank(self) -> int:
        """Ontological rank (higher = more real)."""
        return {
            OntologicalLevel.THE_GOOD: 4,
            OntologicalLevel.BEING: 3,
            OntologicalLevel.BECOMING: 2,
            OntologicalLevel.SPACE: 1,
            OntologicalLevel.NONBEING: 0,
        }[self]
    
    def __lt__(self, other: OntologicalLevel) -> bool:
        return self.rank < other.rank


# =============================================================================
# FORMS (EIDOS)
# =============================================================================

T = TypeVar('T')

@dataclass
class Form(Generic[T]):
    """
    A Platonic Form (εἶδος/ἰδέα).
    
    Forms are eternal, unchanging patterns that instances participate in.
    """
    
    name: str
    definition: str = ""
    
    # Form properties
    is_eternal: bool = True
    is_unchanging: bool = True
    is_intelligible: bool = True  # Known by reason, not senses
    
    # Hierarchical position
    genus: Optional[Form] = None  # Parent form
    species: List[Form] = field(default_factory=list)
    
    # Participation
    instances: List[Any] = field(default_factory=list)
    
    @property
    def level(self) -> OntologicalLevel:
        return OntologicalLevel.BEING
    
    def participates_in(self, other: Form) -> bool:
        """Check if this Form participates in another."""
        if self.genus == other:
            return True
        if self.genus:
            return self.genus.participates_in(other)
        return False
    
    def instantiate(self, instance: T) -> Instance[T]:
        """Create an instance of this Form."""
        inst = Instance(form=self, matter=instance)
        self.instances.append(inst)
        return inst


@dataclass
class Instance(Generic[T]):
    """
    An instance participating in a Form.
    
    Instances are in the realm of Becoming.
    """
    
    form: Form[T]
    matter: T
    
    # Instance properties
    is_temporal: bool = True
    is_changing: bool = True
    is_sensible: bool = True  # Known by senses
    
    @property
    def level(self) -> OntologicalLevel:
        return OntologicalLevel.BECOMING
    
    def degree_of_participation(self) -> float:
        """
        How well does this instance approximate its Form?
        
        Returns value in [0, 1].
        """
        # Simplified: instances always imperfectly participate
        return 0.7


# =============================================================================
# THE RECEPTACLE (CHORA)
# =============================================================================

@dataclass
class Receptacle:
    """
    The Receptacle (χώρα) - Plato's "space".
    
    The medium in which Forms are instantiated.
    Neither Being nor Becoming, but the condition for both.
    """
    
    dimensions: int = 3
    
    # State
    contents: Dict[Tuple[float, ...], Instance] = field(default_factory=dict)
    
    @property
    def level(self) -> OntologicalLevel:
        return OntologicalLevel.SPACE
    
    def place(self, instance: Instance, 
             coordinates: Tuple[float, ...]) -> None:
        """Place an instance in the Receptacle."""
        if len(coordinates) != self.dimensions:
            raise ValueError(f"Expected {self.dimensions} coordinates")
        self.contents[coordinates] = instance
    
    def remove(self, coordinates: Tuple[float, ...]) -> Optional[Instance]:
        """Remove instance at coordinates."""
        return self.contents.pop(coordinates, None)
    
    def query(self, coordinates: Tuple[float, ...], 
             radius: float = 0.0) -> List[Instance]:
        """Query instances near coordinates."""
        results = []
        for coords, instance in self.contents.items():
            dist = math.sqrt(sum((a - b) ** 2 
                                for a, b in zip(coordinates, coords)))
            if dist <= radius:
                results.append(instance)
        return results


# =============================================================================
# PLATONIC SOLIDS
# =============================================================================

class PlatonicSolid(Enum):
    """
    The five Platonic solids as atomic types.
    
    Each corresponds to an element in Platonic cosmology.
    """
    
    TETRAHEDRON = ("tetrahedron", 4, 4, 6, "Fire")
    OCTAHEDRON = ("octahedron", 8, 6, 12, "Air")
    ICOSAHEDRON = ("icosahedron", 20, 12, 30, "Water")
    CUBE = ("cube", 6, 8, 12, "Earth")
    DODECAHEDRON = ("dodecahedron", 12, 20, 30, "Cosmos")
    
    def __init__(self, name: str, faces: int, 
                vertices: int, edges: int, element: str):
        self._name = name
        self._faces = faces
        self._vertices = vertices
        self._edges = edges
        self._element = element
    
    @property
    def faces(self) -> int:
        return self._faces
    
    @property
    def vertices(self) -> int:
        return self._vertices
    
    @property
    def edges(self) -> int:
        return self._edges
    
    @property
    def element(self) -> str:
        return self._element
    
    def euler_characteristic(self) -> int:
        """V - E + F = 2 for convex polyhedra."""
        return self._vertices - self._edges + self._faces
    
    def face_type(self) -> str:
        """Type of face (triangle, square, pentagon)."""
        if self in [PlatonicSolid.TETRAHEDRON, 
                   PlatonicSolid.OCTAHEDRON,
                   PlatonicSolid.ICOSAHEDRON]:
            return "triangle"
        elif self == PlatonicSolid.CUBE:
            return "square"
        else:
            return "pentagon"
    
    @classmethod
    def from_element(cls, element: str) -> Optional[PlatonicSolid]:
        """Get solid corresponding to element."""
        for solid in cls:
            if solid._element.lower() == element.lower():
                return solid
        return None


# =============================================================================
# THE DEMIURGE (Compiler)
# =============================================================================

class Demiurge:
    """
    The Demiurge (δημιουργός) - the divine craftsman/compiler.
    
    Looks to the Forms and creates instances in the Receptacle.
    Functions as the type-checker and instantiator.
    """
    
    def __init__(self):
        self.forms: Dict[str, Form] = {}
        self.receptacle = Receptacle()
        self.good = TheGood()
    
    def define_form(self, name: str, definition: str = "",
                   genus: Optional[Form] = None) -> Form:
        """Define a new Form."""
        form = Form(name=name, definition=definition, genus=genus)
        self.forms[name] = form
        
        if genus:
            genus.species.append(form)
        
        return form
    
    def instantiate(self, form_name: str, 
                   matter: Any,
                   coordinates: Tuple[float, ...] = (0, 0, 0)) -> Instance:
        """
        Instantiate a Form in the Receptacle.
        
        This is the fundamental act of creation.
        """
        if form_name not in self.forms:
            raise ValueError(f"Unknown Form: {form_name}")
        
        form = self.forms[form_name]
        instance = form.instantiate(matter)
        self.receptacle.place(instance, coordinates)
        
        return instance
    
    def type_check(self, instance: Instance, form: Form) -> bool:
        """Check if instance is of type Form."""
        return instance.form == form or instance.form.participates_in(form)
    
    def optimize(self, instance: Instance) -> float:
        """
        Evaluate instance against the Good.
        
        Returns goodness score in [0, 1].
        """
        participation = instance.degree_of_participation()
        return self.good.evaluate(participation)


# =============================================================================
# THE GOOD (Optimization Function)
# =============================================================================

@dataclass
class TheGood:
    """
    The Form of the Good (τὸ ἀγαθόν).
    
    The ultimate principle that all Forms participate in.
    Functions as the objective function for optimization.
    """
    
    @property
    def level(self) -> OntologicalLevel:
        return OntologicalLevel.THE_GOOD
    
    def evaluate(self, participation: float) -> float:
        """
        Evaluate goodness of a participation degree.
        
        Higher participation in Form = closer to the Good.
        """
        return participation
    
    def compare(self, a: float, b: float) -> int:
        """Compare two goodness values."""
        if a > b:
            return 1
        elif a < b:
            return -1
        return 0
    
    def is_optimal(self, value: float, threshold: float = 0.99) -> bool:
        """Check if value is optimal (fully good)."""
        return value >= threshold


# =============================================================================
# THE DIVIDED LINE
# =============================================================================

class DividedLine:
    """
    Plato's Divided Line from the Republic.
    
    Maps types of objects to types of cognition.
    """
    
    SEGMENTS = [
        ("Images", "Imagination (εἰκασία)"),
        ("Physical Objects", "Belief (πίστις)"),
        ("Mathematical Objects", "Understanding (διάνοια)"),
        ("Forms", "Knowledge (νόησις)"),
    ]
    
    def __init__(self, total_length: float = 1.0, ratio: float = 0.618):
        """
        Initialize divided line.
        
        ratio: Proportion between sections (golden ratio by default)
        """
        self.total = total_length
        self.ratio = ratio
        self._divide()
    
    def _divide(self) -> None:
        """Divide line according to ratio."""
        # Upper:Lower = ratio
        lower = self.total / (1 + self.ratio)
        upper = self.total - lower
        
        # Each half divided by same ratio
        self.segments = [
            lower / (1 + self.ratio),       # Images
            lower - lower / (1 + self.ratio),  # Physical
            upper / (1 + self.ratio),       # Mathematical
            upper - upper / (1 + self.ratio),  # Forms
        ]
    
    def get_segment(self, index: int) -> Tuple[str, str, float]:
        """Get segment info by index (0-3)."""
        obj, cog = self.SEGMENTS[index]
        length = self.segments[index]
        return (obj, cog, length)
    
    def classify(self, obj: Any) -> int:
        """Classify object to segment."""
        if isinstance(obj, Form):
            return 3
        elif isinstance(obj, Instance):
            return 1
        elif isinstance(obj, (int, float, complex)):
            return 2
        else:
            return 0


# =============================================================================
# THE ALLEGORY OF THE CAVE
# =============================================================================

class Cave:
    """
    Plato's Allegory of the Cave.
    
    Models the transition from ignorance to knowledge.
    """
    
    class Stage(Enum):
        SHADOWS = 0        # Seeing shadows (lowest)
        OBJECTS = 1        # Seeing carried objects
        FIRE = 2           # Seeing the fire
        ASCENT = 3         # Climbing out
        OUTSIDE = 4        # Outside the cave
        SUN = 5            # Seeing the sun (highest)
    
    def __init__(self):
        self.current_stage = self.Stage.SHADOWS
    
    def perceive(self) -> str:
        """What the prisoner perceives at current stage."""
        perceptions = {
            self.Stage.SHADOWS: "Shadows of artifacts on wall",
            self.Stage.OBJECTS: "Artifacts being carried",
            self.Stage.FIRE: "The fire casting shadows",
            self.Stage.ASCENT: "The cave exit above",
            self.Stage.OUTSIDE: "Objects illuminated by sun",
            self.Stage.SUN: "The Sun itself (Form of Good)",
        }
        return perceptions[self.current_stage]
    
    def ascend(self) -> bool:
        """Attempt to ascend one stage."""
        if self.current_stage.value < self.Stage.SUN.value:
            self.current_stage = self.Stage(self.current_stage.value + 1)
            return True
        return False
    
    def descend(self) -> bool:
        """Descend back into cave (return to teach others)."""
        if self.current_stage.value > self.Stage.SHADOWS.value:
            self.current_stage = self.Stage(self.current_stage.value - 1)
            return True
        return False
    
    def enlightenment_ratio(self) -> float:
        """Ratio of current enlightenment."""
        return self.current_stage.value / self.Stage.SUN.value


# =============================================================================
# VALIDATION
# =============================================================================

def validate_plato() -> bool:
    """Validate Platonic type system module."""
    
    # Test OntologicalLevel
    assert OntologicalLevel.THE_GOOD.rank > OntologicalLevel.BEING.rank
    assert OntologicalLevel.BEING > OntologicalLevel.BECOMING
    
    # Test Form and Instance
    animal = Form(name="Animal", definition="Living being with sensation")
    dog = Form(name="Dog", definition="Four-legged animal", genus=animal)
    
    assert dog.participates_in(animal)
    
    fido = dog.instantiate("Fido the dog")
    assert fido.level == OntologicalLevel.BECOMING
    assert fido.form == dog
    
    # Test Receptacle
    receptacle = Receptacle(dimensions=3)
    receptacle.place(fido, (1.0, 2.0, 3.0))
    
    results = receptacle.query((1.0, 2.0, 3.0), radius=0.1)
    assert len(results) == 1
    
    # Test PlatonicSolid
    tetra = PlatonicSolid.TETRAHEDRON
    assert tetra.faces == 4
    assert tetra.element == "Fire"
    assert tetra.euler_characteristic() == 2
    
    cube = PlatonicSolid.from_element("Earth")
    assert cube == PlatonicSolid.CUBE
    
    # Test Demiurge
    demiurge = Demiurge()
    form_justice = demiurge.define_form("Justice", "Giving each its due")
    
    just_act = demiurge.instantiate("Justice", "Returning borrowed book")
    assert demiurge.type_check(just_act, form_justice)
    
    # Test TheGood
    good = TheGood()
    assert good.level == OntologicalLevel.THE_GOOD
    assert good.evaluate(0.9) == 0.9
    
    # Test DividedLine
    line = DividedLine()
    assert len(line.segments) == 4
    
    obj, cog, length = line.get_segment(3)
    assert obj == "Forms"
    
    # Test Cave
    cave = Cave()
    assert cave.current_stage == Cave.Stage.SHADOWS
    
    for _ in range(5):
        cave.ascend()
    assert cave.current_stage == Cave.Stage.SUN
    assert cave.enlightenment_ratio() == 1.0
    
    return True


if __name__ == "__main__":
    print("Validating Platonic Type System Module...")
    assert validate_plato()
    print("✓ Platonic module validated")
    
    # Demo
    print("\n--- Platonic Type System Demo ---")
    
    print("\n1. Ontological Hierarchy:")
    for level in sorted(OntologicalLevel, key=lambda x: -x.rank):
        print(f"   {level.rank}: {level.value}")
    
    print("\n2. Platonic Solids:")
    for solid in PlatonicSolid:
        print(f"   {solid._name}: {solid.faces} faces → {solid.element}")
        print(f"      V={solid.vertices}, E={solid.edges}, F={solid.faces}")
        print(f"      Euler: {solid.euler_characteristic()}")
    
    print("\n3. Form Hierarchy Example:")
    demiurge = Demiurge()
    
    being = demiurge.define_form("Being")
    living = demiurge.define_form("Living", genus=being)
    animal = demiurge.define_form("Animal", genus=living)
    human = demiurge.define_form("Human", "Rational animal", genus=animal)
    
    print(f"   Being")
    print(f"   └── Living")
    print(f"       └── Animal")
    print(f"           └── Human")
    
    socrates = demiurge.instantiate("Human", "Socrates", (0, 0, 0))
    print(f"\n   Instance: {socrates.matter}")
    print(f"   Participates in Human: {demiurge.type_check(socrates, human)}")
    print(f"   Participates in Animal: {socrates.form.participates_in(animal)}")
    
    print("\n4. Divided Line:")
    line = DividedLine()
    for i in range(4):
        obj, cog, length = line.get_segment(i)
        print(f"   {obj}: {cog} ({length:.3f})")
    
    print("\n5. Cave Allegory (Ascent):")
    cave = Cave()
    while cave.current_stage != Cave.Stage.SUN:
        print(f"   Stage {cave.current_stage.value}: {cave.perceive()}")
        cave.ascend()
    print(f"   Stage {cave.current_stage.value}: {cave.perceive()}")
