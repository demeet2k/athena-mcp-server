"""
ATHENA OS - SQUARING THE CIRCLE: TYPOLOGY
==========================================
Psychological Types from Circle-Square Integration

THE 16 ARCHETYPES (4×4):
    Root element × Expression element = 16 configurations
    - 4 pure (diagonal): F-F, W-W, A-A, E-E
    - 12 mixed (off-diagonal): F-W, F-A, F-E, etc.

THE 64 TYPES (4³):
    Root × Expression × Mode = 64 permutations
    - 4 pure (FFF, WWW, AAA, EEE): maximum intensity
    - 36 double-single: two positions same element
    - 24 triple-distinct: all three positions different

CONSTITUTIONAL TYPES:
    The Hippocratic 4 humors × 4 expressions = 16 types
    Each person has constitution + current state

JUNGIAN CORRELATION:
    - Fire: Intuition (perceiving possibilities)
    - Water: Feeling (evaluating emotionally)
    - Air: Thinking (analyzing logically)
    - Earth: Sensation (perceiving concretely)

SOURCES:
    - SQUARING_THE_CIRCLE.docx Chapters 8, 18
    - Hippocratic-Galenic medical tradition
    - Jungian psychological types
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum, IntEnum


# =============================================================================
# ELEMENTS
# =============================================================================

class Element(IntEnum):
    """The four classical elements."""
    FIRE = 0
    WATER = 1
    AIR = 2
    EARTH = 3


ELEMENT_QUALITIES = {
    Element.FIRE: ("Hot", "Dry"),
    Element.WATER: ("Cold", "Wet"),
    Element.AIR: ("Hot", "Wet"),
    Element.EARTH: ("Cold", "Dry")
}

ELEMENT_SYMBOLS = {
    Element.FIRE: "??",
    Element.WATER: "??",
    Element.AIR: "??",
    Element.EARTH: "??"
}


# =============================================================================
# JUNGIAN FUNCTIONS
# =============================================================================

class JungianFunction(Enum):
    """Jung's four psychological functions."""
    
    INTUITION = "Intuition"   # Fire - perceiving possibilities
    FEELING = "Feeling"       # Water - evaluating emotionally
    THINKING = "Thinking"     # Air - analyzing logically
    SENSATION = "Sensation"   # Earth - perceiving concretely


# Element to Jung mapping
ELEMENT_TO_JUNG = {
    Element.FIRE: JungianFunction.INTUITION,
    Element.WATER: JungianFunction.FEELING,
    Element.AIR: JungianFunction.THINKING,
    Element.EARTH: JungianFunction.SENSATION
}

JUNG_TO_ELEMENT = {v: k for k, v in ELEMENT_TO_JUNG.items()}


class JungianAttitude(Enum):
    """Jung's two attitudes."""
    
    EXTRAVERSION = "Extraversion"  # Energy flows outward
    INTROVERSION = "Introversion"  # Energy flows inward


# =============================================================================
# TEMPERAMENTS (HIPPOCRATIC)
# =============================================================================

class Temperament(Enum):
    """The four classical temperaments (Hippocratic humors)."""
    
    SANGUINE = "Sanguine"       # Air/Blood - optimistic, social
    CHOLERIC = "Choleric"       # Fire/Yellow Bile - ambitious, leader
    MELANCHOLIC = "Melancholic" # Earth/Black Bile - analytical, detail
    PHLEGMATIC = "Phlegmatic"   # Water/Phlegm - relaxed, peaceful


TEMPERAMENT_TO_ELEMENT = {
    Temperament.SANGUINE: Element.AIR,
    Temperament.CHOLERIC: Element.FIRE,
    Temperament.MELANCHOLIC: Element.EARTH,
    Temperament.PHLEGMATIC: Element.WATER
}

ELEMENT_TO_TEMPERAMENT = {v: k for k, v in TEMPERAMENT_TO_ELEMENT.items()}


@dataclass
class TemperamentData:
    """Complete data for a temperament."""
    
    temperament: Temperament
    element: Element
    humor: str
    qualities: Tuple[str, str]
    organ: str
    season: str
    traits: List[str]
    
    @property
    def symbol(self) -> str:
        return ELEMENT_SYMBOLS[self.element]


TEMPERAMENT_CATALOG = {
    Temperament.SANGUINE: TemperamentData(
        temperament=Temperament.SANGUINE,
        element=Element.AIR,
        humor="Blood",
        qualities=("Hot", "Wet"),
        organ="Liver",
        season="Spring",
        traits=["Optimistic", "Social", "Enthusiastic", "Impulsive"]
    ),
    Temperament.CHOLERIC: TemperamentData(
        temperament=Temperament.CHOLERIC,
        element=Element.FIRE,
        humor="Yellow Bile",
        qualities=("Hot", "Dry"),
        organ="Gallbladder",
        season="Summer",
        traits=["Ambitious", "Decisive", "Leader", "Short-tempered"]
    ),
    Temperament.MELANCHOLIC: TemperamentData(
        temperament=Temperament.MELANCHOLIC,
        element=Element.EARTH,
        humor="Black Bile",
        qualities=("Cold", "Dry"),
        organ="Spleen",
        season="Autumn",
        traits=["Analytical", "Detail-oriented", "Deep", "Pessimistic"]
    ),
    Temperament.PHLEGMATIC: TemperamentData(
        temperament=Temperament.PHLEGMATIC,
        element=Element.WATER,
        humor="Phlegm",
        qualities=("Cold", "Wet"),
        organ="Brain",
        season="Winter",
        traits=["Relaxed", "Peaceful", "Content", "Passive"]
    )
}


# =============================================================================
# THE 16 ARCHETYPES (4×4 MATRIX)
# =============================================================================

@dataclass(frozen=True)
class Archetype16:
    """
    One of 16 archetypes from 4×4 element matrix.
    
    Root element × Expression element = 16 types.
    """
    
    root: Element        # The fundamental nature
    expression: Element  # The manifest style
    
    @property
    def index(self) -> int:
        """Index 0-15."""
        return self.root * 4 + self.expression
    
    @property
    def code(self) -> str:
        """Two-letter code."""
        letters = {Element.FIRE: 'F', Element.WATER: 'W', 
                   Element.AIR: 'A', Element.EARTH: 'E'}
        return letters[self.root] + letters[self.expression]
    
    @property
    def is_pure(self) -> bool:
        """Same root and expression (diagonal)."""
        return self.root == self.expression
    
    @property
    def is_mixed(self) -> bool:
        """Different root and expression (off-diagonal)."""
        return self.root != self.expression
    
    @property
    def name(self) -> str:
        """Descriptive name."""
        if self.is_pure:
            return f"Pure {self.root.name.title()}"
        return f"{self.root.name.title()}-{self.expression.name.title()}"
    
    @property
    def description(self) -> str:
        """Brief description of the archetype."""
        if self.is_pure:
            return self._pure_description()
        return self._mixed_description()
    
    def _pure_description(self) -> str:
        descs = {
            Element.FIRE: "Maximum intensity, pure energy, undiluted drive",
            Element.WATER: "Maximum depth, pure emotion, undiluted feeling",
            Element.AIR: "Maximum clarity, pure thought, undiluted reason",
            Element.EARTH: "Maximum stability, pure form, undiluted structure"
        }
        return descs[self.root]
    
    def _mixed_description(self) -> str:
        # Key combinations
        combos = {
            (Element.FIRE, Element.WATER): "Passionate energy channeled through emotion",
            (Element.FIRE, Element.AIR): "Energetic thought, intellectual enthusiasm",
            (Element.FIRE, Element.EARTH): "Grounded energy, practical drive",
            (Element.WATER, Element.FIRE): "Emotional intensity, feeling-driven action",
            (Element.WATER, Element.AIR): "Emotional reasoning, intuitive thought",
            (Element.WATER, Element.EARTH): "Deep practicality, emotional grounding",
            (Element.AIR, Element.FIRE): "Thought-driven action, intellectual energy",
            (Element.AIR, Element.WATER): "Rational feeling, analytical empathy",
            (Element.AIR, Element.EARTH): "Practical intellect, applied thinking",
            (Element.EARTH, Element.FIRE): "Structured energy, methodical drive",
            (Element.EARTH, Element.WATER): "Stable emotion, grounded feeling",
            (Element.EARTH, Element.AIR): "Concrete thought, practical reasoning"
        }
        return combos.get((self.root, self.expression), 
                         f"{self.root.name}-natured, {self.expression.name}-expressed")
    
    @classmethod
    def from_index(cls, index: int) -> Archetype16:
        """Create from index 0-15."""
        return cls(Element(index // 4), Element(index % 4))
    
    def __repr__(self) -> str:
        return f"Archetype16({self.code})"


# Generate all 16 archetypes
ALL_ARCHETYPES_16 = [Archetype16.from_index(i) for i in range(16)]

# Separate pure and mixed
PURE_ARCHETYPES = [a for a in ALL_ARCHETYPES_16 if a.is_pure]
MIXED_ARCHETYPES = [a for a in ALL_ARCHETYPES_16 if a.is_mixed]


# =============================================================================
# THE 64 TYPES (4³ CUBE)
# =============================================================================

@dataclass(frozen=True)
class Type64:
    """
    One of 64 types from 4³ element cube.
    
    Root × Expression × Mode = 64 types.
    """
    
    root: Element        # Fundamental nature
    expression: Element  # Manifest style
    mode: Element        # Operational context
    
    @property
    def index(self) -> int:
        """Index 0-63."""
        return self.root * 16 + self.expression * 4 + self.mode
    
    @property
    def code(self) -> str:
        """Three-letter code."""
        letters = {Element.FIRE: 'F', Element.WATER: 'W',
                   Element.AIR: 'A', Element.EARTH: 'E'}
        return letters[self.root] + letters[self.expression] + letters[self.mode]
    
    @property
    def element_counts(self) -> Dict[Element, int]:
        """Count of each element."""
        counts = {e: 0 for e in Element}
        for e in [self.root, self.expression, self.mode]:
            counts[e] += 1
        return counts
    
    @property
    def type_class(self) -> str:
        """Classification: pure, double, or triple-distinct."""
        unique = len(set([self.root, self.expression, self.mode]))
        if unique == 1:
            return "pure"
        elif unique == 2:
            return "double"
        else:
            return "triple-distinct"
    
    @property
    def is_pure(self) -> bool:
        return self.type_class == "pure"
    
    @property
    def is_double(self) -> bool:
        return self.type_class == "double"
    
    @property
    def is_triple_distinct(self) -> bool:
        return self.type_class == "triple-distinct"
    
    @property
    def dominant_element(self) -> Optional[Element]:
        """Element appearing most (None if all different)."""
        counts = self.element_counts
        max_count = max(counts.values())
        if max_count == 1:
            return None
        dominants = [e for e, c in counts.items() if c == max_count]
        return dominants[0] if len(dominants) == 1 else None
    
    @property
    def intensity(self) -> int:
        """Intensity measure: 3 for pure, 2 for double, 1 for triple-distinct."""
        return 4 - len(set([self.root, self.expression, self.mode]))
    
    @property
    def complexity(self) -> int:
        """Complexity: inverse of intensity (more elements = more complex)."""
        return len(set([self.root, self.expression, self.mode]))
    
    @property
    def archetype_16(self) -> Archetype16:
        """The 16-type archetype (ignoring mode)."""
        return Archetype16(self.root, self.expression)
    
    def to_jungian(self) -> Dict[str, str]:
        """Express in Jungian terms."""
        return {
            "dominant": ELEMENT_TO_JUNG[self.root].value,
            "auxiliary": ELEMENT_TO_JUNG[self.expression].value,
            "tertiary": ELEMENT_TO_JUNG[self.mode].value
        }
    
    def to_temperament(self) -> Dict[str, str]:
        """Express in temperament terms."""
        return {
            "constitutional": ELEMENT_TO_TEMPERAMENT[self.root].value,
            "expressed": ELEMENT_TO_TEMPERAMENT[self.expression].value,
            "contextual": ELEMENT_TO_TEMPERAMENT[self.mode].value
        }
    
    @classmethod
    def from_index(cls, index: int) -> Type64:
        """Create from index 0-63."""
        root = Element(index // 16)
        expression = Element((index // 4) % 4)
        mode = Element(index % 4)
        return cls(root, expression, mode)
    
    @classmethod
    def from_code(cls, code: str) -> Type64:
        """Create from code like 'FWA'."""
        letter_to_element = {'F': Element.FIRE, 'W': Element.WATER,
                            'A': Element.AIR, 'E': Element.EARTH}
        return cls(
            letter_to_element[code[0].upper()],
            letter_to_element[code[1].upper()],
            letter_to_element[code[2].upper()]
        )
    
    def __repr__(self) -> str:
        return f"Type64({self.code})"


# Generate all 64 types
ALL_TYPES_64 = [Type64.from_index(i) for i in range(64)]

# Categorize
PURE_TYPES = [t for t in ALL_TYPES_64 if t.is_pure]
DOUBLE_TYPES = [t for t in ALL_TYPES_64 if t.is_double]
TRIPLE_DISTINCT_TYPES = [t for t in ALL_TYPES_64 if t.is_triple_distinct]

# Verify counts
assert len(PURE_TYPES) == 4          # FFF, WWW, AAA, EEE
assert len(DOUBLE_TYPES) == 36       # C(4,1) × C(3,1) × 3 positions = 36
assert len(TRIPLE_DISTINCT_TYPES) == 24  # 4! = 24


# =============================================================================
# CONSTITUTIONAL TYPES (16)
# =============================================================================

@dataclass
class ConstitutionalType:
    """
    One of 16 constitutional types.
    
    Constitution (innate temperament) × Current State = 16 types.
    """
    
    constitution: Temperament  # Innate, stable
    current: Temperament       # Temporary, variable
    
    @property
    def code(self) -> str:
        """Code like 'S-C' (Sanguine constitution, Choleric current)."""
        abbrevs = {
            Temperament.SANGUINE: 'S',
            Temperament.CHOLERIC: 'C',
            Temperament.MELANCHOLIC: 'M',
            Temperament.PHLEGMATIC: 'P'
        }
        return f"{abbrevs[self.constitution]}-{abbrevs[self.current]}"
    
    @property
    def is_congruent(self) -> bool:
        """Constitution matches current (on diagonal)."""
        return self.constitution == self.current
    
    @property
    def is_incongruent(self) -> bool:
        """Constitution differs from current."""
        return not self.is_congruent
    
    @property
    def diagnostic_note(self) -> str:
        """Diagnostic guidance."""
        if self.is_congruent:
            return f"Pure {self.constitution.value} - moderate the dominant humor"
        return (f"{self.constitution.value} constitution in {self.current.value} state - "
                f"address both constitution and current condition")
    
    def __repr__(self) -> str:
        return f"ConstitutionalType({self.code})"


# Generate all 16 constitutional types
ALL_CONSTITUTIONAL_TYPES = [
    ConstitutionalType(const, curr)
    for const in Temperament
    for curr in Temperament
]


# =============================================================================
# SOUL STRUCTURE (PLATONIC)
# =============================================================================

class SoulPart(Enum):
    """Plato's three parts of the soul."""
    
    REASON = "Reason"       # Logistikon - thinking, ruling
    SPIRIT = "Spirit"       # Thumoeides - striving, defending
    APPETITE = "Appetite"   # Epithumetikon - desiring, consuming


@dataclass
class SoulData:
    """Data for a soul part."""
    
    part: SoulPart
    function: str
    location: str
    object: str
    virtue: str
    element_affinity: Element


SOUL_CATALOG = {
    SoulPart.REASON: SoulData(
        part=SoulPart.REASON,
        function="Thinking, planning, ruling",
        location="Head",
        object="Truth, the Good",
        virtue="Wisdom (sophia)",
        element_affinity=Element.AIR
    ),
    SoulPart.SPIRIT: SoulData(
        part=SoulPart.SPIRIT,
        function="Striving, defending, asserting",
        location="Chest",
        object="Honor, victory",
        virtue="Courage (andreia)",
        element_affinity=Element.FIRE
    ),
    SoulPart.APPETITE: SoulData(
        part=SoulPart.APPETITE,
        function="Desiring, consuming, enjoying",
        location="Belly",
        object="Pleasure, material things",
        virtue="Temperance (sophrosyne)",
        element_affinity=Element.WATER
    )
}


# =============================================================================
# TYPOLOGY SYSTEM
# =============================================================================

class TypologySystem:
    """
    Complete typology system integrating all type frameworks.
    """
    
    N_ARCHETYPES_16 = 16
    N_TYPES_64 = 64
    N_CONSTITUTIONAL = 16
    
    def __init__(self):
        self.archetypes_16 = ALL_ARCHETYPES_16
        self.types_64 = ALL_TYPES_64
        self.constitutional = ALL_CONSTITUTIONAL_TYPES
        self.temperaments = list(Temperament)
    
    def get_archetype(self, root: Element, expression: Element) -> Archetype16:
        """Get archetype by elements."""
        return Archetype16(root, expression)
    
    def get_type(self, root: Element, expression: Element, mode: Element) -> Type64:
        """Get type by elements."""
        return Type64(root, expression, mode)
    
    def types_by_dominant(self, element: Element) -> List[Type64]:
        """Get all types where element is dominant."""
        return [t for t in self.types_64 if t.dominant_element == element]
    
    def types_by_class(self, type_class: str) -> List[Type64]:
        """Get types by class (pure, double, triple-distinct)."""
        return [t for t in self.types_64 if t.type_class == type_class]
    
    def element_distribution(self) -> Dict[str, Dict[Element, int]]:
        """Distribution of elements across type positions."""
        root_dist = {e: 0 for e in Element}
        expr_dist = {e: 0 for e in Element}
        mode_dist = {e: 0 for e in Element}
        
        for t in self.types_64:
            root_dist[t.root] += 1
            expr_dist[t.expression] += 1
            mode_dist[t.mode] += 1
        
        return {
            "root": root_dist,
            "expression": expr_dist,
            "mode": mode_dist
        }
    
    def class_distribution(self) -> Dict[str, int]:
        """Distribution by type class."""
        return {
            "pure": len(PURE_TYPES),
            "double": len(DOUBLE_TYPES),
            "triple_distinct": len(TRIPLE_DISTINCT_TYPES)
        }
    
    def get_temperament_data(self, temp: Temperament) -> TemperamentData:
        """Get temperament data."""
        return TEMPERAMENT_CATALOG[temp]
    
    def get_soul_data(self, part: SoulPart) -> SoulData:
        """Get soul part data."""
        return SOUL_CATALOG[part]
    
    def summary(self) -> Dict[str, Any]:
        """Get system summary."""
        return {
            "archetypes_16": {
                "total": self.N_ARCHETYPES_16,
                "pure": len(PURE_ARCHETYPES),
                "mixed": len(MIXED_ARCHETYPES)
            },
            "types_64": {
                "total": self.N_TYPES_64,
                "pure": len(PURE_TYPES),
                "double": len(DOUBLE_TYPES),
                "triple_distinct": len(TRIPLE_DISTINCT_TYPES)
            },
            "constitutional": self.N_CONSTITUTIONAL,
            "temperaments": [t.value for t in self.temperaments],
            "jungian_functions": [j.value for j in JungianFunction]
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_typology() -> bool:
    """Validate the typology module."""
    
    # Verify archetype counts
    assert len(ALL_ARCHETYPES_16) == 16
    assert len(PURE_ARCHETYPES) == 4
    assert len(MIXED_ARCHETYPES) == 12
    
    # Verify type counts
    assert len(ALL_TYPES_64) == 64
    assert len(PURE_TYPES) == 4
    assert len(DOUBLE_TYPES) == 36
    assert len(TRIPLE_DISTINCT_TYPES) == 24
    assert 4 + 36 + 24 == 64
    
    # Verify constitutional counts
    assert len(ALL_CONSTITUTIONAL_TYPES) == 16
    
    # Verify mappings
    for e in Element:
        assert e in ELEMENT_TO_JUNG
        assert e in ELEMENT_TO_TEMPERAMENT
    
    # Verify system
    system = TypologySystem()
    summary = system.summary()
    assert summary["archetypes_16"]["total"] == 16
    assert summary["types_64"]["total"] == 64
    
    # Verify type reconstruction
    for i in range(64):
        t = Type64.from_index(i)
        assert t.index == i
        t2 = Type64.from_code(t.code)
        assert t == t2
    
    return True


if __name__ == "__main__":
    print("Validating Typology Module...")
    assert validate_typology()
    print("✓ Typology Module validated")
    
    # Demo
    print("\n--- Typology System Demo ---")
    
    system = TypologySystem()
    summary = system.summary()
    
    print("\n16 Archetypes (4×4):")
    print(f"  Total: {summary['archetypes_16']['total']}")
    print(f"  Pure: {summary['archetypes_16']['pure']}")
    print(f"  Mixed: {summary['archetypes_16']['mixed']}")
    
    print("\n64 Types (4³):")
    print(f"  Total: {summary['types_64']['total']}")
    print(f"  Pure: {summary['types_64']['pure']}")
    print(f"  Double: {summary['types_64']['double']}")
    print(f"  Triple-distinct: {summary['types_64']['triple_distinct']}")
    
    print("\nPure Types:")
    for t in PURE_TYPES:
        print(f"  {t.code}: {t.to_jungian()['dominant']}")
    
    print("\nTemperaments:")
    for temp in Temperament:
        data = TEMPERAMENT_CATALOG[temp]
        print(f"  {data.symbol} {temp.value}: {data.humor} ({data.qualities[0]}/{data.qualities[1]})")
    
    print("\nSoul Parts:")
    for part in SoulPart:
        data = SOUL_CATALOG[part]
        print(f"  {part.value}: {data.function}")
