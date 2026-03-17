"""
ATHENA OS - SQUARING THE CIRCLE: METAPHYSICS
=============================================
Philosophical Foundations of Circle-Square Integration

BEING AND BEINGS:
    Being (to on): Circle - continuous, one, eternal
    Beings (ta onta): Square - discrete, many, temporal

FORM AND MATTER:
    Form (eidos): Circle - universal, eternal, active
    Matter (hyle): Square - particular, temporal, passive
    Substance (ousia): Form + Matter = Squared Circle

THE FOUR CAUSES:
    Material: What it's made of (substrate)
    Formal: What it is (pattern)
    Efficient: What brought it about (agent)
    Final: What it's for (purpose)

THE UNMOVED MOVER:
    Pure actuality (energeia)
    Thought thinking itself (noesis noeseos)
    Final cause of all motion

NEOPLATONIC EMANATION:
    The One (to hen): Absolute unity
    Emanation (proodos): Unity → Plurality
    Return (epistrophe): Plurality → Unity

SOURCES:
    - SQUARING_THE_CIRCLE.docx Chapters 16-17
    - Aristotle, Metaphysics, Physics
    - Plato, Republic, Parmenides
    - Plotinus, Enneads
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum


# =============================================================================
# ONTOLOGICAL CATEGORIES
# =============================================================================

class OntologicalCategory(Enum):
    """Fundamental categories of being."""
    
    BEING = "Being"          # To on - Being itself
    BEINGS = "Beings"        # Ta onta - particular beings
    ONE = "One"              # To hen - absolute unity
    MANY = "Many"            # Ta polla - plurality
    FORM = "Form"            # Eidos - universal pattern
    MATTER = "Matter"        # Hyle - material substrate
    SUBSTANCE = "Substance"  # Ousia - unified being
    ACCIDENT = "Accident"    # Symbebekos - changeable property


@dataclass
class CircleSquareMapping:
    """
    Mapping of ontological concepts to circle/square.
    """
    
    concept: str
    circle_aspect: str
    square_aspect: str
    integration: str
    
    def __repr__(self) -> str:
        return f"CircleSquareMapping({self.concept})"


ONTOLOGICAL_MAPPINGS = [
    CircleSquareMapping(
        concept="Being/Beings",
        circle_aspect="Being (continuous, one, eternal)",
        square_aspect="Beings (discrete, many, temporal)",
        integration="Substance unifies form and matter"
    ),
    CircleSquareMapping(
        concept="Form/Matter",
        circle_aspect="Form (universal, eternal, active)",
        square_aspect="Matter (particular, temporal, passive)",
        integration="Hylomorphic compound"
    ),
    CircleSquareMapping(
        concept="Process/Structure",
        circle_aspect="Process (becoming, change, flow)",
        square_aspect="Structure (being, stability, form)",
        integration="Dynamic equilibrium"
    ),
    CircleSquareMapping(
        concept="Time/Space",
        circle_aspect="Time (sequential, cyclic, continuous)",
        square_aspect="Space (simultaneous, structural, discrete)",
        integration="Spacetime continuum"
    ),
    CircleSquareMapping(
        concept="Universal/Particular",
        circle_aspect="Universal (one in many)",
        square_aspect="Particular (individual instance)",
        integration="Participation/Instantiation"
    )
]


# =============================================================================
# ARISTOTELIAN CAUSES
# =============================================================================

class CauseType(Enum):
    """Aristotle's Four Causes."""
    
    MATERIAL = "Material"    # What it's made of
    FORMAL = "Formal"        # What it is (essence)
    EFFICIENT = "Efficient"  # What brought it about
    FINAL = "Final"          # What it's for (purpose)


@dataclass
class FourCauses:
    """
    The four causes of a being.
    
    Complete explanation requires all four.
    """
    
    material: str   # The matter/substrate
    formal: str     # The form/essence
    efficient: str  # The agent/source
    final: str      # The purpose/telos
    
    @property
    def circle_aspect(self) -> str:
        """Formal and final causes (circle-like)."""
        return f"Form: {self.formal}; Telos: {self.final}"
    
    @property
    def square_aspect(self) -> str:
        """Material and efficient causes (square-like)."""
        return f"Matter: {self.material}; Agent: {self.efficient}"
    
    def describe(self) -> str:
        return f"""Four Causes:
  Material: {self.material}
  Formal: {self.formal}
  Efficient: {self.efficient}
  Final: {self.final}"""


# Example causes
COSMOS_CAUSES = FourCauses(
    material="Four elements (sublunary) + Aether (celestial)",
    formal="Spherical arrangement with Earth at center",
    efficient="The Unmoved Mover imparting circular motion",
    final="Eternal circular motion imitating divine contemplation"
)

HUMAN_CAUSES = FourCauses(
    material="Four elements in humoral balance",
    formal="Rational soul (psyche)",
    efficient="Parents and nutrition",
    final="Contemplation and happiness (eudaimonia)"
)

STATE_CAUSES = FourCauses(
    material="Citizens and territory",
    formal="Constitution (politeia)",
    efficient="Lawgivers and founders",
    final="The good life for citizens"
)


# =============================================================================
# HYLOMORPHISM
# =============================================================================

@dataclass
class Hylomorphism:
    """
    The form-matter compound (hylomorphic analysis).
    
    Every substance is a unity of form and matter.
    """
    
    name: str
    form: str       # What it is (circle-like)
    matter: str     # What it's made of (square-like)
    
    @property
    def is_squared_circle(self) -> bool:
        """Substance is the 'squared circle' of form and matter."""
        return True  # By definition
    
    def describe(self) -> str:
        return f"{self.name}: Form ({self.form}) + Matter ({self.matter})"


HYLOMORPHIC_EXAMPLES = [
    Hylomorphism("Bronze statue", "Shape of the figure", "Bronze"),
    Hylomorphism("Human being", "Rational soul", "Body (organized matter)"),
    Hylomorphism("House", "Structure providing shelter", "Bricks and wood"),
    Hylomorphism("Word", "Meaning/concept", "Sound/letters"),
    Hylomorphism("Cosmos", "Spherical order", "Elements and aether")
]


# =============================================================================
# THE UNMOVED MOVER
# =============================================================================

@dataclass
class UnmovedMover:
    """
    Aristotle's Prime Mover / Unmoved Mover.
    
    The first cause of all motion, itself unmoved.
    """
    
    @staticmethod
    def nature() -> str:
        return "Pure actuality (energeia) - no potentiality"
    
    @staticmethod
    def essence() -> str:
        return "Thought thinking itself (noesis noeseos)"
    
    @staticmethod
    def causation() -> str:
        return "Final cause - moves by being desired, not by pushing"
    
    @staticmethod
    def properties() -> Dict[str, str]:
        return {
            "nature": "Pure actuality (no potentiality)",
            "essence": "Thought thinking itself",
            "eternity": "Eternal, without beginning or end",
            "unity": "One, simple, indivisible",
            "immateriality": "No matter, pure form",
            "immobility": "Unmoved, yet causes all motion",
            "perfection": "Complete, lacking nothing",
            "bliss": "Perfect contemplation (theoria)"
        }
    
    @staticmethod
    def relation_to_cosmos() -> str:
        return """
The Unmoved Mover and the Cosmos:
1. The Mover is the final cause of celestial motion
2. The outermost sphere (Primum Mobile) is moved by desire for the Mover
3. Each lower sphere is moved by the sphere above
4. Celestial motion is eternal and circular
5. The Mover transcends yet grounds both circle (celestial) and square (sublunary)
"""


# =============================================================================
# NEOPLATONIC SYSTEM
# =============================================================================

class NeoplatonicLevel(Enum):
    """The levels of Neoplatonic reality."""
    
    ONE = "The One"      # To hen - absolute unity, beyond being
    NOUS = "Intellect"   # Divine mind, contains the Forms
    SOUL = "Soul"        # Psyche - mediates between nous and matter
    NATURE = "Nature"    # Physis - soul's projection into matter
    MATTER = "Matter"    # Hyle - the lowest level, pure potentiality


NEOPLATONIC_DATA = {
    NeoplatonicLevel.ONE: {
        "greek": "To Hen",
        "description": "Absolute unity, beyond being and thought",
        "properties": ["Simple", "Ineffable", "Source of all"],
        "relation_to_integration": "The center from which circle and square emanate"
    },
    NeoplatonicLevel.NOUS: {
        "greek": "Nous",
        "description": "Divine Intellect containing eternal Forms",
        "properties": ["Thinking", "Being", "Unity-in-plurality"],
        "relation_to_integration": "Circle system - eternal, unified Forms"
    },
    NeoplatonicLevel.SOUL: {
        "greek": "Psyche",
        "description": "World Soul and individual souls",
        "properties": ["Life", "Motion", "Mediation"],
        "relation_to_integration": "Mediator between circle (nous) and square (matter)"
    },
    NeoplatonicLevel.NATURE: {
        "greek": "Physis",
        "description": "Soul's creative projection",
        "properties": ["Generation", "Growth", "Natural order"],
        "relation_to_integration": "Square system emerging - structural forms"
    },
    NeoplatonicLevel.MATTER: {
        "greek": "Hyle",
        "description": "Pure potentiality, near non-being",
        "properties": ["Receptive", "Formless", "Darkness"],
        "relation_to_integration": "Square system complete - discrete particulars"
    }
}


@dataclass
class Emanation:
    """
    The process of emanation (proodos) from the One.
    """
    
    source: NeoplatonicLevel
    product: NeoplatonicLevel
    process: str
    
    @staticmethod
    def chain() -> List[Emanation]:
        """The complete chain of emanation."""
        return [
            Emanation(NeoplatonicLevel.ONE, NeoplatonicLevel.NOUS, 
                     "Overflow of unity produces thought"),
            Emanation(NeoplatonicLevel.NOUS, NeoplatonicLevel.SOUL,
                     "Thinking produces life/motion"),
            Emanation(NeoplatonicLevel.SOUL, NeoplatonicLevel.NATURE,
                     "Life projects into nature"),
            Emanation(NeoplatonicLevel.NATURE, NeoplatonicLevel.MATTER,
                     "Nature reaches toward pure potentiality")
        ]


@dataclass
class Return:
    """
    The process of return (epistrophe) to the One.
    """
    
    @staticmethod
    def description() -> str:
        return """
Epistrophe - The Return to the One:

1. Philosophy: The mind turns from matter to Forms to Unity
2. Purification: The soul sheds bodily attachments
3. Contemplation: The intellect focuses on eternal truths
4. Henosis: Union with the One (mystical experience)

The return is the 'unsquaring' of the circle:
- From multiplicity (square) back to unity (circle)
- From matter back to form
- From beings back to Being
- From the many back to the One
"""


# =============================================================================
# PARMENIDEAN SPHERE
# =============================================================================

@dataclass
class ParmenideanBeing:
    """
    Parmenides' conception of Being as a sphere.
    """
    
    @staticmethod
    def properties() -> Dict[str, str]:
        return {
            "unity": "Being is one, not many",
            "continuity": "Being admits no gaps or non-being within",
            "eternity": "Being neither comes to be nor passes away",
            "immobility": "Being does not move or change",
            "perfection": "Being is complete, lacking nothing",
            "sphericality": "Like a well-rounded sphere, equal from center"
        }
    
    @staticmethod
    def circle_interpretation() -> str:
        return """
Parmenidean Being is the ultimate Circle:
- Continuous (no gaps)
- One (not divided)
- Eternal (no beginning/end)
- Perfect (spherical, complete)

The 'way of truth' reveals Being as circular;
The 'way of seeming' reveals beings as square.
"""


# =============================================================================
# PLATONIC CAVE
# =============================================================================

@dataclass
class CaveAllegory:
    """
    Plato's Allegory of the Cave as circle-square integration.
    """
    
    @staticmethod
    def cave_structure() -> Dict[str, str]:
        """The cave represents the square system."""
        return {
            "shadows": "64 permutations (discrete configurations)",
            "fire": "Efficient cause producing shadows",
            "prisoners": "Consciousness trapped in structural thinking",
            "wall": "Boundary of square system",
            "chains": "Limitation to 'what' without 'when'"
        }
    
    @staticmethod
    def outside_structure() -> Dict[str, str]:
        """Outside represents the circle system."""
        return {
            "sun": "Center of the circle (source of truth)",
            "natural_things": "36 faces illuminated by sun",
            "sky": "Circular dome (continuous cycle)",
            "freed_prisoner": "Consciousness knowing 'when' and 'what'"
        }
    
    @staticmethod
    def integration() -> str:
        return """
The Philosopher's Journey as Integration:

1. Cave = Square (64 permutations, structural)
2. Outside = Circle (36 faces, temporal)
3. Ascending = Learning the circle system
4. Descending = Bringing circular knowledge into square form
5. Teaching prisoners = Translating temporal into structural

The complete philosopher knows both cave (square) and sun (circle).
The unified field (36 + 64 = 100) is the philosopher's map.
"""


# =============================================================================
# METAPHYSICAL SYSTEM
# =============================================================================

class MetaphysicalSystem:
    """
    Complete metaphysical framework.
    """
    
    def __init__(self):
        self.mappings = ONTOLOGICAL_MAPPINGS
        self.hylomorphic_examples = HYLOMORPHIC_EXAMPLES
        self.unmoved_mover = UnmovedMover()
        self.cave = CaveAllegory()
    
    def get_mapping(self, concept: str) -> Optional[CircleSquareMapping]:
        """Get mapping by concept name."""
        for m in self.mappings:
            if m.concept == concept:
                return m
        return None
    
    def four_causes(self, subject: str = "cosmos") -> FourCauses:
        """Get four causes for a subject."""
        causes = {
            "cosmos": COSMOS_CAUSES,
            "human": HUMAN_CAUSES,
            "state": STATE_CAUSES
        }
        return causes.get(subject, COSMOS_CAUSES)
    
    def neoplatonic_level(self, level: NeoplatonicLevel) -> Dict[str, Any]:
        """Get data for a Neoplatonic level."""
        return NEOPLATONIC_DATA[level]
    
    def emanation_chain(self) -> List[Emanation]:
        """Get the chain of emanation."""
        return Emanation.chain()
    
    def being_properties(self) -> Dict[str, str]:
        """Get Parmenidean Being properties."""
        return ParmenideanBeing.properties()
    
    def mover_properties(self) -> Dict[str, str]:
        """Get Unmoved Mover properties."""
        return UnmovedMover.properties()
    
    def circle_square_relation(self) -> str:
        """Describe how circle and square relate metaphysically."""
        return """
Circle-Square Metaphysical Relation:

CIRCLE represents:
- Being (continuous, unified, eternal)
- Form (universal, active, determining)
- Process (becoming, change, cycle)
- Time (sequential, cyclic flow)

SQUARE represents:
- Beings (discrete, multiple, temporal)
- Matter (particular, passive, determined)
- Structure (being, stability, state)
- Space (simultaneous, structural grid)

INTEGRATION (100 = 36 + 64):
- Substance = Form + Matter
- Complete description = When + What
- Philosophy = Cave + Sun
- Cosmos = Celestial + Sublunary

The squared circle is the fundamental metaphysical pattern:
Neither pure circle nor pure square, but their synthesis.
"""
    
    def summary(self) -> Dict[str, Any]:
        """Get system summary."""
        return {
            "ontological_mappings": len(self.mappings),
            "hylomorphic_examples": len(self.hylomorphic_examples),
            "neoplatonic_levels": len(NeoplatonicLevel),
            "aristotelian_causes": 4,
            "key_concepts": [
                "Being/Beings",
                "Form/Matter",
                "Four Causes",
                "Unmoved Mover",
                "Emanation/Return"
            ]
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_metaphysics() -> bool:
    """Validate the metaphysics module."""
    
    # Verify mappings
    assert len(ONTOLOGICAL_MAPPINGS) >= 5
    
    # Verify causes
    for cause_type in CauseType:
        assert cause_type.value in ["Material", "Formal", "Efficient", "Final"]
    
    # Verify hylomorphic examples
    assert len(HYLOMORPHIC_EXAMPLES) >= 5
    
    # Verify Neoplatonic levels
    assert len(NeoplatonicLevel) == 5
    assert len(NEOPLATONIC_DATA) == 5
    
    # Verify emanation chain
    chain = Emanation.chain()
    assert len(chain) == 4
    
    # Verify system
    system = MetaphysicalSystem()
    summary = system.summary()
    assert summary["aristotelian_causes"] == 4
    assert summary["neoplatonic_levels"] == 5
    
    # Verify Unmoved Mover
    props = UnmovedMover.properties()
    assert "nature" in props
    assert "essence" in props
    
    return True


if __name__ == "__main__":
    print("Validating Metaphysics Module...")
    assert validate_metaphysics()
    print("✓ Metaphysics Module validated")
    
    # Demo
    print("\n--- Metaphysics Demo ---")
    
    system = MetaphysicalSystem()
    
    print("\nOntological Mappings (Circle ↔ Square):")
    for m in system.mappings[:3]:
        print(f"  {m.concept}:")
        print(f"    Circle: {m.circle_aspect}")
        print(f"    Square: {m.square_aspect}")
    
    print("\nFour Causes of the Cosmos:")
    causes = system.four_causes("cosmos")
    print(causes.describe())
    
    print("\nUnmoved Mover Properties:")
    props = system.mover_properties()
    for key in ["nature", "essence", "causation"]:
        if key in props:
            print(f"  {key.title()}: {props[key]}")
    
    print("\nNeoplatonic Levels:")
    for level in NeoplatonicLevel:
        data = NEOPLATONIC_DATA[level]
        print(f"  {level.value} ({data['greek']})")
    
    print("\nHylomorphism Examples:")
    for h in HYLOMORPHIC_EXAMPLES[:3]:
        print(f"  {h.describe()}")
