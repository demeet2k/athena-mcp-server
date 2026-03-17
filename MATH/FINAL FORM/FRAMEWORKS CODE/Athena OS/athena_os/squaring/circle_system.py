"""
ATHENA OS - SQUARING THE CIRCLE: CIRCLE SYSTEM
===============================================
The Circular System - Temporal/Cyclic Dimension

THE CIRCLE'S HIERARCHY:
    Level 1: 3 Modes (Cardinal, Fixed, Mutable)
    Level 2: 4 Elements (Fire, Water, Air, Earth)  
    Level 3: 12 Archetypes (3 × 4 = element-mode pairs)
    Level 4: 36 Faces (12 × 3 = decanates)
    Level 5: 360 Degrees (36 × 10 = complete circle)

CIRCULAR PROPERTIES:
    - Temporal sequence
    - Cyclic return
    - Continuous variation
    - Phase transitions
    - Rotational symmetry

THE THREE MODES:
    Cardinal: Initiating, beginning, impulse
    Fixed: Stabilizing, maintaining, persistence
    Mutable: Transitioning, changing, adaptation

THE TWELVE ARCHETYPES (Zodiac):
    Fire-Cardinal: Aries       Water-Cardinal: Cancer
    Fire-Fixed: Leo            Water-Fixed: Scorpio
    Fire-Mutable: Sagittarius  Water-Mutable: Pisces
    Air-Cardinal: Libra        Earth-Cardinal: Capricorn
    Air-Fixed: Aquarius        Earth-Fixed: Taurus
    Air-Mutable: Gemini        Earth-Mutable: Virgo

SOURCES:
    - SQUARING_THE_CIRCLE.docx
    - Hellenic astrological tradition
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Iterator
from enum import Enum, IntEnum
import numpy as np
import math


# =============================================================================
# ENUMS - CIRCULAR SYSTEM
# =============================================================================

class Mode(IntEnum):
    """The three modes of circular expression."""
    
    CARDINAL = 0   # Initiating, beginning
    FIXED = 1      # Stabilizing, maintaining
    MUTABLE = 2    # Transitioning, adapting


class Element(IntEnum):
    """The four classical elements."""
    
    FIRE = 0    # Hot + Dry
    WATER = 1   # Cold + Wet
    AIR = 2     # Hot + Wet
    EARTH = 3   # Cold + Dry


class Archetype(IntEnum):
    """The twelve zodiacal archetypes (3 modes × 4 elements)."""
    
    # Fire Signs
    ARIES = 0        # Fire-Cardinal
    LEO = 4          # Fire-Fixed
    SAGITTARIUS = 8  # Fire-Mutable
    
    # Water Signs
    CANCER = 3       # Water-Cardinal
    SCORPIO = 7      # Water-Fixed
    PISCES = 11      # Water-Mutable
    
    # Air Signs
    LIBRA = 6        # Air-Cardinal
    AQUARIUS = 10    # Air-Fixed
    GEMINI = 2       # Air-Mutable
    
    # Earth Signs
    CAPRICORN = 9    # Earth-Cardinal
    TAURUS = 1       # Earth-Fixed
    VIRGO = 5        # Earth-Mutable


# Archetype ordering by degree (0° Aries start)
ARCHETYPE_ORDER = [
    Archetype.ARIES,       # 0° - 30°
    Archetype.TAURUS,      # 30° - 60°
    Archetype.GEMINI,      # 60° - 90°
    Archetype.CANCER,      # 90° - 120°
    Archetype.LEO,         # 120° - 150°
    Archetype.VIRGO,       # 150° - 180°
    Archetype.LIBRA,       # 180° - 210°
    Archetype.SCORPIO,     # 210° - 240°
    Archetype.SAGITTARIUS, # 240° - 270°
    Archetype.CAPRICORN,   # 270° - 300°
    Archetype.AQUARIUS,    # 300° - 330°
    Archetype.PISCES       # 330° - 360°
]


# =============================================================================
# ARCHETYPE PROPERTIES
# =============================================================================

@dataclass
class ArchetypeProperties:
    """Properties of a zodiacal archetype."""
    
    archetype: Archetype
    name: str
    symbol: str
    element: Element
    mode: Mode
    
    # Degree range
    start_degree: int
    end_degree: int
    
    # Ruling planet (traditional)
    ruler: str
    
    # Polarity
    polarity: str  # "positive" (masculine) or "negative" (feminine)
    
    @property
    def center_degree(self) -> float:
        """Get center degree of this archetype."""
        return (self.start_degree + self.end_degree) / 2
    
    @property
    def is_cardinal(self) -> bool:
        return self.mode == Mode.CARDINAL
    
    @property
    def is_fixed(self) -> bool:
        return self.mode == Mode.FIXED
    
    @property
    def is_mutable(self) -> bool:
        return self.mode == Mode.MUTABLE
    
    def contains_degree(self, degree: float) -> bool:
        """Check if degree falls within this archetype."""
        deg = degree % 360
        return self.start_degree <= deg < self.end_degree


# Archetype definitions
ARCHETYPE_DATA: Dict[Archetype, ArchetypeProperties] = {
    Archetype.ARIES: ArchetypeProperties(
        Archetype.ARIES, "Aries", "♈", Element.FIRE, Mode.CARDINAL,
        0, 30, "Mars", "positive"
    ),
    Archetype.TAURUS: ArchetypeProperties(
        Archetype.TAURUS, "Taurus", "♉", Element.EARTH, Mode.FIXED,
        30, 60, "Venus", "negative"
    ),
    Archetype.GEMINI: ArchetypeProperties(
        Archetype.GEMINI, "Gemini", "♊", Element.AIR, Mode.MUTABLE,
        60, 90, "Mercury", "positive"
    ),
    Archetype.CANCER: ArchetypeProperties(
        Archetype.CANCER, "Cancer", "♋", Element.WATER, Mode.CARDINAL,
        90, 120, "Moon", "negative"
    ),
    Archetype.LEO: ArchetypeProperties(
        Archetype.LEO, "Leo", "♌", Element.FIRE, Mode.FIXED,
        120, 150, "Sun", "positive"
    ),
    Archetype.VIRGO: ArchetypeProperties(
        Archetype.VIRGO, "Virgo", "♍", Element.EARTH, Mode.MUTABLE,
        150, 180, "Mercury", "negative"
    ),
    Archetype.LIBRA: ArchetypeProperties(
        Archetype.LIBRA, "Libra", "♎", Element.AIR, Mode.CARDINAL,
        180, 210, "Venus", "positive"
    ),
    Archetype.SCORPIO: ArchetypeProperties(
        Archetype.SCORPIO, "Scorpio", "♏", Element.WATER, Mode.FIXED,
        210, 240, "Mars", "negative"
    ),
    Archetype.SAGITTARIUS: ArchetypeProperties(
        Archetype.SAGITTARIUS, "Sagittarius", "♐", Element.FIRE, Mode.MUTABLE,
        240, 270, "Jupiter", "positive"
    ),
    Archetype.CAPRICORN: ArchetypeProperties(
        Archetype.CAPRICORN, "Capricorn", "♑", Element.EARTH, Mode.CARDINAL,
        270, 300, "Saturn", "negative"
    ),
    Archetype.AQUARIUS: ArchetypeProperties(
        Archetype.AQUARIUS, "Aquarius", "♒", Element.AIR, Mode.FIXED,
        300, 330, "Saturn", "positive"
    ),
    Archetype.PISCES: ArchetypeProperties(
        Archetype.PISCES, "Pisces", "♓", Element.WATER, Mode.MUTABLE,
        330, 360, "Jupiter", "negative"
    ),
}


# =============================================================================
# FACE (DECANATE)
# =============================================================================

@dataclass
class Face:
    """
    A Face (Decanate) - 10° subdivision of the zodiac.
    
    36 faces total = 12 archetypes × 3 faces each
    """
    
    index: int  # 0-35
    archetype: Archetype
    decanate: int  # 1, 2, or 3 within archetype
    
    # Degree range
    start_degree: int
    end_degree: int
    
    # Ruler (varies by decanate system)
    ruler: str = ""
    
    @property
    def center_degree(self) -> float:
        return (self.start_degree + self.end_degree) / 2
    
    @property
    def element(self) -> Element:
        return ARCHETYPE_DATA[self.archetype].element
    
    @property
    def mode(self) -> Mode:
        return ARCHETYPE_DATA[self.archetype].mode
    
    def contains_degree(self, degree: float) -> bool:
        deg = degree % 360
        return self.start_degree <= deg < self.end_degree
    
    def __hash__(self) -> int:
        return hash(self.index)


def generate_faces() -> List[Face]:
    """Generate all 36 faces of the zodiac."""
    faces = []
    
    for i, archetype in enumerate(ARCHETYPE_ORDER):
        arch_data = ARCHETYPE_DATA[archetype]
        base_degree = i * 30
        
        for dec in range(3):
            face = Face(
                index=i * 3 + dec,
                archetype=archetype,
                decanate=dec + 1,
                start_degree=base_degree + dec * 10,
                end_degree=base_degree + (dec + 1) * 10
            )
            faces.append(face)
    
    return faces


FACES = generate_faces()


# =============================================================================
# CIRCULAR POSITION
# =============================================================================

@dataclass
class CircularPosition:
    """
    A position on the circle (0-360 degrees).
    
    Captures the complete circular hierarchy:
    - Degree (360)
    - Face (36)
    - Archetype (12)
    - Element (4)
    - Mode (3)
    """
    
    degree: float
    
    def __post_init__(self):
        # Normalize to [0, 360)
        self.degree = self.degree % 360
    
    @property
    def face_index(self) -> int:
        """Get face index (0-35)."""
        return int(self.degree // 10)
    
    @property
    def face(self) -> Face:
        """Get the face containing this position."""
        return FACES[self.face_index]
    
    @property
    def archetype_index(self) -> int:
        """Get archetype index (0-11)."""
        return int(self.degree // 30)
    
    @property
    def archetype(self) -> Archetype:
        """Get the archetype containing this position."""
        return ARCHETYPE_ORDER[self.archetype_index]
    
    @property
    def archetype_props(self) -> ArchetypeProperties:
        """Get archetype properties."""
        return ARCHETYPE_DATA[self.archetype]
    
    @property
    def element(self) -> Element:
        """Get element at this position."""
        return self.archetype_props.element
    
    @property
    def mode(self) -> Mode:
        """Get mode at this position."""
        return self.archetype_props.mode
    
    @property
    def degree_within_sign(self) -> float:
        """Get degree within current sign (0-30)."""
        return self.degree % 30
    
    @property
    def radians(self) -> float:
        """Get position in radians."""
        return math.radians(self.degree)
    
    @property
    def cartesian(self) -> Tuple[float, float]:
        """Get (x, y) on unit circle."""
        rad = self.radians
        return (math.cos(rad), math.sin(rad))
    
    def distance_to(self, other: CircularPosition) -> float:
        """Get angular distance to another position."""
        diff = abs(self.degree - other.degree)
        return min(diff, 360 - diff)
    
    def aspect_to(self, other: CircularPosition) -> Optional[str]:
        """
        Get major aspect to another position.
        
        Returns aspect name or None.
        """
        dist = self.distance_to(other)
        orb = 8  # Degree orb
        
        if abs(dist - 0) <= orb:
            return "conjunction"
        elif abs(dist - 60) <= orb:
            return "sextile"
        elif abs(dist - 90) <= orb:
            return "square"
        elif abs(dist - 120) <= orb:
            return "trine"
        elif abs(dist - 180) <= orb:
            return "opposition"
        
        return None
    
    def advance(self, degrees: float) -> CircularPosition:
        """Return new position advanced by degrees."""
        return CircularPosition(self.degree + degrees)
    
    def __repr__(self) -> str:
        arch = self.archetype_props
        return f"{self.degree:.2f}° ({arch.name} {arch.symbol})"


# =============================================================================
# CIRCLE SYSTEM
# =============================================================================

class CircleSystem:
    """
    The complete circular system.
    
    Hierarchy:
        3 Modes → 4 Elements → 12 Archetypes → 36 Faces → 360 Degrees
    """
    
    # Constants
    N_MODES = 3
    N_ELEMENTS = 4
    N_ARCHETYPES = 12
    N_FACES = 36
    N_DEGREES = 360
    
    def __init__(self):
        self.faces = FACES
        self.archetypes = ARCHETYPE_DATA
    
    def get_position(self, degree: float) -> CircularPosition:
        """Get circular position for degree."""
        return CircularPosition(degree)
    
    def get_face(self, index: int) -> Face:
        """Get face by index (0-35)."""
        return self.faces[index % 36]
    
    def get_archetype(self, archetype: Archetype) -> ArchetypeProperties:
        """Get archetype properties."""
        return self.archetypes[archetype]
    
    def get_archetype_by_index(self, index: int) -> ArchetypeProperties:
        """Get archetype by index (0-11)."""
        return self.archetypes[ARCHETYPE_ORDER[index % 12]]
    
    def get_signs_by_element(self, element: Element) -> List[Archetype]:
        """Get all signs of an element (triplicity)."""
        return [a for a, p in self.archetypes.items() if p.element == element]
    
    def get_signs_by_mode(self, mode: Mode) -> List[Archetype]:
        """Get all signs of a mode (quadruplicity)."""
        return [a for a, p in self.archetypes.items() if p.mode == mode]
    
    def iterate_degrees(self, step: float = 1.0) -> Iterator[CircularPosition]:
        """Iterate through all degrees."""
        degree = 0.0
        while degree < 360:
            yield CircularPosition(degree)
            degree += step
    
    def iterate_faces(self) -> Iterator[Face]:
        """Iterate through all 36 faces."""
        return iter(self.faces)
    
    def iterate_archetypes(self) -> Iterator[ArchetypeProperties]:
        """Iterate through all 12 archetypes in order."""
        for arch in ARCHETYPE_ORDER:
            yield self.archetypes[arch]
    
    def phase_of_cycle(self, degree: float) -> Tuple[int, str]:
        """
        Get phase of cycle (0-11) and description.
        
        Based on lunar-like 12-phase model.
        """
        phase = int(degree // 30)
        descriptions = [
            "New/Beginning",
            "Crescent/Emerging",
            "First Quarter/Crisis",
            "Gibbous/Refining",
            "Full/Culmination",
            "Disseminating/Sharing",
            "Last Quarter/Reorienting",
            "Balsamic/Releasing",
            "Void/Transition",
            "Seed/Potential",
            "Germination/Stirring",
            "Sprouting/Manifesting"
        ]
        return (phase, descriptions[phase % 12])
    
    def element_balance(self, positions: List[CircularPosition]) -> Dict[Element, int]:
        """Count elements in a list of positions."""
        balance = {e: 0 for e in Element}
        for pos in positions:
            balance[pos.element] += 1
        return balance
    
    def mode_balance(self, positions: List[CircularPosition]) -> Dict[Mode, int]:
        """Count modes in a list of positions."""
        balance = {m: 0 for m in Mode}
        for pos in positions:
            balance[pos.mode] += 1
        return balance
    
    def get_level_count(self, level: int) -> int:
        """Get count at each level of the hierarchy."""
        counts = {
            1: self.N_MODES,      # 3
            2: self.N_ELEMENTS,   # 4
            3: self.N_ARCHETYPES, # 12 = 3 × 4
            4: self.N_FACES,      # 36 = 12 × 3
            5: self.N_DEGREES     # 360 = 36 × 10
        }
        return counts.get(level, 0)
    
    def summary(self) -> Dict[str, Any]:
        """Get summary of circle system."""
        return {
            "levels": 5,
            "modes": self.N_MODES,
            "elements": self.N_ELEMENTS,
            "archetypes": self.N_ARCHETYPES,
            "faces": self.N_FACES,
            "degrees": self.N_DEGREES,
            "product_check": f"3 × 4 = {3*4}, 12 × 3 = {12*3}, 36 × 10 = {36*10}"
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_circle_system() -> bool:
    """Validate circle system module."""
    
    # Test constants
    assert len(Mode) == 3
    assert len(Element) == 4
    assert len(ARCHETYPE_ORDER) == 12
    assert len(FACES) == 36
    
    # Test archetype properties
    for arch in Archetype:
        props = ARCHETYPE_DATA[arch]
        assert props.archetype == arch
        assert 0 <= props.start_degree < 360
        assert props.end_degree - props.start_degree == 30
    
    # Test faces
    for i, face in enumerate(FACES):
        assert face.index == i
        assert 0 <= face.start_degree < 360
        assert face.end_degree - face.start_degree == 10
    
    # Test circular position
    pos = CircularPosition(45.0)
    assert pos.archetype == Archetype.TAURUS
    assert pos.face_index == 4
    assert pos.element == Element.EARTH
    assert pos.mode == Mode.FIXED
    
    # Test wrap-around
    pos2 = CircularPosition(370.0)
    assert pos2.degree == 10.0
    
    # Test circle system
    circle = CircleSystem()
    assert circle.N_ARCHETYPES == 12
    assert circle.N_FACES == 36
    
    fire_signs = circle.get_signs_by_element(Element.FIRE)
    assert len(fire_signs) == 3
    
    cardinal_signs = circle.get_signs_by_mode(Mode.CARDINAL)
    assert len(cardinal_signs) == 4
    
    # Test aspect detection
    pos_a = CircularPosition(0)
    pos_b = CircularPosition(120)
    assert pos_a.aspect_to(pos_b) == "trine"
    
    pos_c = CircularPosition(90)
    assert pos_a.aspect_to(pos_c) == "square"
    
    return True


if __name__ == "__main__":
    print("Validating Circle System...")
    assert validate_circle_system()
    print("✓ Circle System validated")
    
    # Demo
    print("\n--- Circle System Demo ---")
    
    circle = CircleSystem()
    print(f"\nHierarchy:")
    for level in range(1, 6):
        print(f"  Level {level}: {circle.get_level_count(level)}")
    
    print("\nThe 12 Archetypes:")
    for props in circle.iterate_archetypes():
        print(f"  {props.symbol} {props.name}: {props.element.name}/{props.mode.name}")
    
    print("\nSample Position (15° Taurus):")
    pos = circle.get_position(45.0)
    print(f"  {pos}")
    print(f"  Element: {pos.element.name}")
    print(f"  Mode: {pos.mode.name}")
    print(f"  Face: {pos.face.index + 1}/36")
    
    print("\nFaces of Aries:")
    for i in range(3):
        face = circle.get_face(i)
        print(f"  Decanate {face.decanate}: {face.start_degree}° - {face.end_degree}°")
