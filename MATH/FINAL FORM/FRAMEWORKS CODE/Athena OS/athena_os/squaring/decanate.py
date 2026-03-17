"""
ATHENA OS - SQUARING THE CIRCLE: DECANATE SYSTEM
=================================================
The 36 Faces of the Zodiacal Circle

THE 36 DECANATES:
    12 Signs × 3 Faces = 36 Decanates
    
    Each sign spans 30° of the ecliptic.
    Each face spans 10° within the sign.
    
    36 × 10° = 360° (complete circle)

SIGNIFICANCE OF 36:
    36 = 6² (square of the first perfect number)
    36 = T₈ (8th triangular number: 1+2+3+4+5+6+7+8)
    36 = 1³ + 2³ + 3³ (sum of first three cubes)
    
    36 + 64 = 100 (Pythagorean completion)

THE THREE FACES:
    Face 1 (0°-10°): Pure expression of sign
    Face 2 (10°-20°): Development/elaboration
    Face 3 (20°-30°): Transition/completion
    
    Each face inherits the sign's element-mode
    but adds triadic modification.

CHALDEAN RULERSHIP:
    Traditional planetary sequence:
    ♄ Saturn → ♃ Jupiter → ♂ Mars → ☉ Sun → ♀ Venus → ☿ Mercury → ☽ Moon
    
    Starting from Leo Face 1, cycling through all 36 faces.

EGYPTIAN DECANS:
    The 36 decanates derive from Egyptian astronomy.
    Each decan was a star group rising heliacally
    for a 10-day period during the year.
    
    The decan system predates and underlies the zodiac.

SOURCES:
    - SQUARING_THE_CIRCLE.docx Chapter 4
    - Hellenistic astrological tradition
    - Egyptian decan system
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Iterator
from enum import Enum, IntEnum
import math


# =============================================================================
# ENUMS
# =============================================================================

class Element(IntEnum):
    """The four classical elements."""
    FIRE = 0
    EARTH = 1
    AIR = 2
    WATER = 3


class Mode(IntEnum):
    """The three zodiacal modes."""
    CARDINAL = 0
    FIXED = 1
    MUTABLE = 2


class Planet(IntEnum):
    """The seven classical planets (Chaldean order)."""
    SATURN = 0
    JUPITER = 1
    MARS = 2
    SUN = 3
    VENUS = 4
    MERCURY = 5
    MOON = 6


# Planet symbols
PLANET_SYMBOLS: Dict[Planet, str] = {
    Planet.SATURN: "♄",
    Planet.JUPITER: "♃",
    Planet.MARS: "♂",
    Planet.SUN: "☉",
    Planet.VENUS: "♀",
    Planet.MERCURY: "☿",
    Planet.MOON: "☽"
}


class Sign(IntEnum):
    """The twelve zodiacal signs (in order from Aries)."""
    ARIES = 0
    TAURUS = 1
    GEMINI = 2
    CANCER = 3
    LEO = 4
    VIRGO = 5
    LIBRA = 6
    SCORPIO = 7
    SAGITTARIUS = 8
    CAPRICORN = 9
    AQUARIUS = 10
    PISCES = 11


# Sign symbols
SIGN_SYMBOLS: Dict[Sign, str] = {
    Sign.ARIES: "♈",
    Sign.TAURUS: "♉",
    Sign.GEMINI: "♊",
    Sign.CANCER: "♋",
    Sign.LEO: "♌",
    Sign.VIRGO: "♍",
    Sign.LIBRA: "♎",
    Sign.SCORPIO: "♏",
    Sign.SAGITTARIUS: "♐",
    Sign.CAPRICORN: "♑",
    Sign.AQUARIUS: "♒",
    Sign.PISCES: "♓"
}


# =============================================================================
# SIGN DATA
# =============================================================================

@dataclass(frozen=True)
class SignData:
    """Data for a zodiacal sign."""
    
    sign: Sign
    name: str
    symbol: str
    element: Element
    mode: Mode
    start_degree: int
    ruling_planet: Planet
    exaltation: Optional[Planet] = None
    detriment: Optional[Planet] = None
    fall: Optional[Planet] = None
    
    @property
    def end_degree(self) -> int:
        return self.start_degree + 30
    
    @property
    def triplicity(self) -> List[Sign]:
        """Get signs of same element."""
        elem = self.element
        return [s for s in Sign if SIGN_CATALOG[s].element == elem]
    
    @property
    def quadruplicity(self) -> List[Sign]:
        """Get signs of same mode."""
        mod = self.mode
        return [s for s in Sign if SIGN_CATALOG[s].mode == mod]


# Complete sign catalog
SIGN_CATALOG: Dict[Sign, SignData] = {
    Sign.ARIES: SignData(
        Sign.ARIES, "Aries", "♈", Element.FIRE, Mode.CARDINAL,
        0, Planet.MARS, Planet.SUN, Planet.VENUS, Planet.SATURN
    ),
    Sign.TAURUS: SignData(
        Sign.TAURUS, "Taurus", "♉", Element.EARTH, Mode.FIXED,
        30, Planet.VENUS, Planet.MOON, Planet.MARS, None
    ),
    Sign.GEMINI: SignData(
        Sign.GEMINI, "Gemini", "♊", Element.AIR, Mode.MUTABLE,
        60, Planet.MERCURY, None, Planet.JUPITER, None
    ),
    Sign.CANCER: SignData(
        Sign.CANCER, "Cancer", "♋", Element.WATER, Mode.CARDINAL,
        90, Planet.MOON, Planet.JUPITER, Planet.SATURN, Planet.MARS
    ),
    Sign.LEO: SignData(
        Sign.LEO, "Leo", "♌", Element.FIRE, Mode.FIXED,
        120, Planet.SUN, None, Planet.SATURN, None
    ),
    Sign.VIRGO: SignData(
        Sign.VIRGO, "Virgo", "♍", Element.EARTH, Mode.MUTABLE,
        150, Planet.MERCURY, Planet.MERCURY, Planet.JUPITER, Planet.VENUS
    ),
    Sign.LIBRA: SignData(
        Sign.LIBRA, "Libra", "♎", Element.AIR, Mode.CARDINAL,
        180, Planet.VENUS, Planet.SATURN, Planet.MARS, Planet.SUN
    ),
    Sign.SCORPIO: SignData(
        Sign.SCORPIO, "Scorpio", "♏", Element.WATER, Mode.FIXED,
        210, Planet.MARS, None, Planet.VENUS, Planet.MOON
    ),
    Sign.SAGITTARIUS: SignData(
        Sign.SAGITTARIUS, "Sagittarius", "♐", Element.FIRE, Mode.MUTABLE,
        240, Planet.JUPITER, None, Planet.MERCURY, None
    ),
    Sign.CAPRICORN: SignData(
        Sign.CAPRICORN, "Capricorn", "♑", Element.EARTH, Mode.CARDINAL,
        270, Planet.SATURN, Planet.MARS, Planet.MOON, Planet.JUPITER
    ),
    Sign.AQUARIUS: SignData(
        Sign.AQUARIUS, "Aquarius", "♒", Element.AIR, Mode.FIXED,
        300, Planet.SATURN, None, Planet.SUN, None
    ),
    Sign.PISCES: SignData(
        Sign.PISCES, "Pisces", "♓", Element.WATER, Mode.MUTABLE,
        330, Planet.JUPITER, Planet.VENUS, Planet.MERCURY, Planet.MERCURY
    )
}


# =============================================================================
# DECANATE (FACE)
# =============================================================================

@dataclass
class Decanate:
    """
    A decanate (face) - 10° subdivision of the zodiac.
    
    36 decanates total (12 signs × 3 faces each).
    """
    
    index: int          # 0-35
    sign: Sign          # Parent sign
    face_number: int    # 1, 2, or 3 within sign
    start_degree: int   # 0-359
    
    # Chaldean ruler (traditional)
    chaldean_ruler: Planet = None
    
    # Triplicity ruler (by element)
    triplicity_sign: Sign = None
    
    @property
    def end_degree(self) -> int:
        return self.start_degree + 10
    
    @property
    def center_degree(self) -> float:
        return self.start_degree + 5.0
    
    @property
    def sign_data(self) -> SignData:
        return SIGN_CATALOG[self.sign]
    
    @property
    def element(self) -> Element:
        return self.sign_data.element
    
    @property
    def mode(self) -> Mode:
        return self.sign_data.mode
    
    @property
    def symbol(self) -> str:
        return f"{SIGN_SYMBOLS[self.sign]}{self.face_number}"
    
    @property
    def chaldean_symbol(self) -> str:
        if self.chaldean_ruler:
            return PLANET_SYMBOLS[self.chaldean_ruler]
        return "?"
    
    @property
    def degree_range(self) -> str:
        return f"{self.start_degree}°-{self.end_degree}°"
    
    @property
    def triplicity_influence(self) -> str:
        """Get the triplicity influence description."""
        if self.triplicity_sign:
            trip_data = SIGN_CATALOG[self.triplicity_sign]
            return f"{trip_data.name} ({trip_data.mode.name})"
        return "Pure"
    
    def contains_degree(self, degree: float) -> bool:
        deg = degree % 360
        return self.start_degree <= deg < self.end_degree
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "sign": self.sign.name,
            "face": self.face_number,
            "degrees": self.degree_range,
            "element": self.element.name,
            "mode": self.mode.name,
            "chaldean_ruler": self.chaldean_ruler.name if self.chaldean_ruler else None,
            "triplicity_sign": self.triplicity_sign.name if self.triplicity_sign else None
        }
    
    def __repr__(self) -> str:
        return f"Decanate({self.sign.name} Face {self.face_number})"
    
    def __hash__(self) -> int:
        return hash(self.index)


# =============================================================================
# CHALDEAN SEQUENCE
# =============================================================================

def chaldean_planet_sequence(n: int) -> List[Planet]:
    """
    Generate Chaldean planetary sequence.
    
    Order: Saturn → Jupiter → Mars → Sun → Venus → Mercury → Moon → repeat
    """
    sequence = []
    for i in range(n):
        sequence.append(Planet(i % 7))
    return sequence


def assign_chaldean_rulers() -> List[Planet]:
    """
    Assign Chaldean rulers to 36 decanates.
    
    Traditionally starts with Mars at Aries Face 1.
    (Leo Face 1 = Sun, hence Aries Face 1 = Mars)
    """
    # Leo Face 1 = Sun (index 3 in sequence)
    # Aries Face 1 is 4 signs × 3 faces = 12 faces earlier
    # So Aries Face 1 starts at offset in sequence
    
    # Calculate: Leo is sign 4 (0-indexed), Face 1
    # Leo Face 1 = decanate index 4*3 + 0 = 12
    # At index 12, ruler should be Sun
    # Sun is Planet index 3
    # So starting offset = (12 - 3) % 7 = 9 % 7 = 2
    
    # Actually, traditionally Aries Face 1 = Mars
    # Mars is Planet index 2
    # So sequence starts at Mars
    
    rulers = []
    for i in range(36):
        # Starting from Mars (index 2), go backwards in Chaldean order
        planet_idx = (2 + i) % 7
        rulers.append(Planet(planet_idx))
    return rulers


# =============================================================================
# TRIPLICITY RULERSHIP
# =============================================================================

def get_triplicity_signs(element: Element) -> List[Sign]:
    """Get the three signs of an element in mode order (Cardinal, Fixed, Mutable)."""
    signs = []
    for sign in Sign:
        if SIGN_CATALOG[sign].element == element:
            signs.append(sign)
    # Sort by mode
    return sorted(signs, key=lambda s: SIGN_CATALOG[s].mode.value)


def assign_triplicity_rulers() -> List[Optional[Sign]]:
    """
    Assign triplicity rulers to each decanate.
    
    Each face receives influence from another sign of its element:
    - Face 1: Pure (same sign)
    - Face 2: Next sign of same element (Fixed for Cardinal, Mutable for Fixed, Cardinal for Mutable)
    - Face 3: Remaining sign of same element
    """
    rulers = []
    for sign in Sign:
        sign_data = SIGN_CATALOG[sign]
        element = sign_data.element
        mode = sign_data.mode
        
        # Get triplicity in mode order
        triplicity = get_triplicity_signs(element)
        
        # Find this sign's position in triplicity
        sign_pos = None
        for i, s in enumerate(triplicity):
            if s == sign:
                sign_pos = i
                break
        
        # Assign rulers for three faces
        # Face 1: Self (pure)
        rulers.append(None)  # No modifier - pure sign
        
        # Face 2: Next in triplicity cycle
        next_pos = (sign_pos + 1) % 3
        rulers.append(triplicity[next_pos])
        
        # Face 3: Remaining sign
        remaining_pos = (sign_pos + 2) % 3
        rulers.append(triplicity[remaining_pos])
    
    return rulers


# =============================================================================
# DECANATE GENERATION
# =============================================================================

def generate_decanates() -> List[Decanate]:
    """Generate all 36 decanates with rulers."""
    
    chaldean_rulers = assign_chaldean_rulers()
    triplicity_rulers = assign_triplicity_rulers()
    
    decanates = []
    
    for i in range(36):
        sign_idx = i // 3
        face_num = (i % 3) + 1
        sign = Sign(sign_idx)
        sign_data = SIGN_CATALOG[sign]
        start_deg = sign_data.start_degree + (face_num - 1) * 10
        
        dec = Decanate(
            index=i,
            sign=sign,
            face_number=face_num,
            start_degree=start_deg,
            chaldean_ruler=chaldean_rulers[i],
            triplicity_sign=triplicity_rulers[i]
        )
        decanates.append(dec)
    
    return decanates


# Global decanate list
DECANATES = generate_decanates()


# =============================================================================
# NUMBER 36 PROPERTIES
# =============================================================================

class ThirtySixProperties:
    """
    Mathematical properties of the number 36.
    """
    
    N = 36
    
    @classmethod
    def is_square(cls) -> bool:
        """36 = 6²."""
        return int(math.sqrt(cls.N)) ** 2 == cls.N
    
    @classmethod
    def square_root(cls) -> int:
        """√36 = 6."""
        return 6
    
    @classmethod
    def is_triangular(cls) -> bool:
        """36 = T₈ = 1+2+3+4+5+6+7+8."""
        return cls.triangular_index() is not None
    
    @classmethod
    def triangular_index(cls) -> int:
        """36 = T₈."""
        # T_n = n(n+1)/2, solve for n
        # n² + n - 72 = 0
        # n = (-1 + √(1 + 288)) / 2 = (-1 + 17) / 2 = 8
        return 8
    
    @classmethod
    def sum_of_cubes(cls) -> List[int]:
        """36 = 1³ + 2³ + 3³."""
        return [1, 2, 3]
    
    @classmethod
    def verify_sum_of_cubes(cls) -> bool:
        """Verify 1³ + 2³ + 3³ = 36."""
        return sum(n**3 for n in cls.sum_of_cubes()) == cls.N
    
    @classmethod
    def divisors(cls) -> List[int]:
        """Get all divisors of 36."""
        return [1, 2, 3, 4, 6, 9, 12, 18, 36]
    
    @classmethod
    def prime_factorization(cls) -> Dict[int, int]:
        """36 = 2² × 3²."""
        return {2: 2, 3: 2}
    
    @classmethod
    def pythagorean_role(cls) -> str:
        """36 in the Pythagorean identity 36 + 64 = 100."""
        return "36 = 6² (Circle contribution to 6² + 8² = 10²)"
    
    @classmethod
    def all_representations(cls) -> Dict[str, str]:
        """All representations of 36."""
        return {
            "square": "6²",
            "triangular": "T₈",
            "sum_of_cubes": "1³ + 2³ + 3³",
            "prime": "2² × 3²",
            "zodiac": "12 signs × 3 faces",
            "pythagorean": "Circle in 36 + 64 = 100"
        }


# =============================================================================
# DECANATE SYSTEM
# =============================================================================

class DecanateSystem:
    """
    Complete system of 36 decanates.
    """
    
    N_DECANATES = 36
    N_SIGNS = 12
    N_FACES = 3
    DEGREES_PER_FACE = 10
    
    def __init__(self):
        self.decanates = DECANATES
        self.sign_catalog = SIGN_CATALOG
    
    def get_decanate(self, index: int) -> Decanate:
        """Get decanate by index (0-35)."""
        return self.decanates[index % 36]
    
    def get_by_sign_face(self, sign: Sign, face: int) -> Decanate:
        """Get decanate by sign and face number (1-3)."""
        index = sign.value * 3 + (face - 1)
        return self.decanates[index]
    
    def get_by_degree(self, degree: float) -> Decanate:
        """Get decanate containing a degree."""
        deg = degree % 360
        index = int(deg // 10)
        return self.decanates[index]
    
    def iterate_decanates(self) -> Iterator[Decanate]:
        """Iterate all 36 decanates."""
        return iter(self.decanates)
    
    def decanates_by_element(self, element: Element) -> List[Decanate]:
        """Get all decanates of an element."""
        return [d for d in self.decanates if d.element == element]
    
    def decanates_by_mode(self, mode: Mode) -> List[Decanate]:
        """Get all decanates of a mode."""
        return [d for d in self.decanates if d.mode == mode]
    
    def decanates_by_ruler(self, planet: Planet) -> List[Decanate]:
        """Get all decanates ruled by a planet (Chaldean)."""
        return [d for d in self.decanates if d.chaldean_ruler == planet]
    
    def ruler_distribution(self) -> Dict[Planet, int]:
        """Get distribution of planetary rulers."""
        dist = {p: 0 for p in Planet}
        for d in self.decanates:
            if d.chaldean_ruler:
                dist[d.chaldean_ruler] += 1
        return dist
    
    def sign_decanates(self, sign: Sign) -> List[Decanate]:
        """Get all three decanates of a sign."""
        start = sign.value * 3
        return self.decanates[start:start+3]
    
    def summary(self) -> Dict[str, Any]:
        """Get system summary."""
        ruler_dist = self.ruler_distribution()
        return {
            "total_decanates": self.N_DECANATES,
            "signs": self.N_SIGNS,
            "faces_per_sign": self.N_FACES,
            "degrees_per_face": self.DEGREES_PER_FACE,
            "structure": f"{self.N_SIGNS} × {self.N_FACES} = {self.N_DECANATES}",
            "ruler_distribution": {p.name: c for p, c in ruler_dist.items()},
            "number_36_properties": ThirtySixProperties.all_representations()
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_decanate_system() -> bool:
    """Validate the decanate module."""
    
    # Count verification
    assert len(DECANATES) == 36
    assert len(Sign) == 12
    assert len(Planet) == 7
    
    # Index uniqueness
    indices = [d.index for d in DECANATES]
    assert len(set(indices)) == 36
    
    # Degree coverage
    covered = set()
    for d in DECANATES:
        for deg in range(d.start_degree, d.end_degree):
            covered.add(deg)
    assert covered == set(range(360))
    
    # Each sign has exactly 3 faces
    for sign in Sign:
        sign_decs = [d for d in DECANATES if d.sign == sign]
        assert len(sign_decs) == 3
        assert {d.face_number for d in sign_decs} == {1, 2, 3}
    
    # Chaldean rulers: each planet rules 5 or 6 faces
    system = DecanateSystem()
    ruler_dist = system.ruler_distribution()
    for planet, count in ruler_dist.items():
        assert 5 <= count <= 6, f"Planet {planet.name} has {count} decanates"
    
    # 36 properties
    assert ThirtySixProperties.is_square()
    assert ThirtySixProperties.square_root() == 6
    assert ThirtySixProperties.is_triangular()
    assert ThirtySixProperties.triangular_index() == 8
    assert ThirtySixProperties.verify_sum_of_cubes()
    
    # Pythagorean
    assert 36 + 64 == 100
    assert 6**2 + 8**2 == 10**2
    
    return True


if __name__ == "__main__":
    print("Validating Decanate System...")
    assert validate_decanate_system()
    print("✓ Decanate System validated")
    
    # Demo
    print("\n--- Decanate System Demo ---")
    
    system = DecanateSystem()
    summary = system.summary()
    
    print(f"\nStructure: {summary['structure']}")
    
    print("\nNumber 36 Properties:")
    for rep, val in summary['number_36_properties'].items():
        print(f"  {rep}: {val}")
    
    print("\nPlanetary Ruler Distribution:")
    for planet, count in summary['ruler_distribution'].items():
        print(f"  {PLANET_SYMBOLS[Planet[planet]]} {planet}: {count} decanates")
    
    print("\nAries Decanates:")
    for dec in system.sign_decanates(Sign.ARIES):
        print(f"  Face {dec.face_number}: {dec.degree_range} - {dec.chaldean_symbol} {dec.chaldean_ruler.name if dec.chaldean_ruler else 'None'}")
    
    print("\nSample Decanate Lookup (165°):")
    dec = system.get_by_degree(165)
    print(f"  {dec}")
    print(f"  Sign: {dec.sign.name}")
    print(f"  Element: {dec.element.name}")
    print(f"  Mode: {dec.mode.name}")
    print(f"  Ruler: {dec.chaldean_ruler.name if dec.chaldean_ruler else 'None'}")
