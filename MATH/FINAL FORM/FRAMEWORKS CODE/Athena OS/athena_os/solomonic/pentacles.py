"""
ATHENA OS - KEY OF SOLOMON COMPUTATIONAL FRAMEWORK
===================================================
Part III: The Pentacles (Kernel Operators)

PENTACLES AS PRECOMPILED SUBROUTINES:
    Each pentacle P_k is a structured object encoding:
    - G_k: Geometry (circles, stars, grids)
    - N_k: Names/symbols inscribed
    - V_k: Verse/semantic tag (effect direction)
    - Π_k: Planetary signature (spectral band)

KERNEL OPERATORS:
    K_k: C → C
    Each pentacle implements a kernel operator that transforms
    the configuration space, subject to:
    - Time compatibility: χ_Π(t) = 1
    - Consecration flag: consecrated(P_k) = true

THE 44-PENTACLE BASIS:
    The pentacles form a finite basis in an "effect vector space"
    7 planets × ~6 pentacles each = 44 total
    They are precompiled binaries: dense encodings of names,
    geometry, and scriptural phrases.

SOURCES:
    Key of Solomon (Clavicula Salomonis)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Set
from enum import Enum, auto
import numpy as np

# Import from temporal
from .temporal import Planet


# =============================================================================
# PENTACLE EFFECT TYPES
# =============================================================================

class EffectType(Enum):
    """Types of effects pentacles can produce."""
    
    PROTECTION = ("defense", "shield against harm")
    BINDING = ("constraint", "compel obedience")
    KNOWLEDGE = ("revelation", "obtain hidden information")
    FAVOR = ("attraction", "win love/friendship")
    WEALTH = ("prosperity", "material abundance")
    INVISIBILITY = ("concealment", "avoid detection")
    HEALING = ("restoration", "cure illness")
    AUTHORITY = ("dominion", "command spirits")
    DESTRUCTION = ("banishing", "defeat enemies")
    TRANSFORMATION = ("change", "alter circumstances")
    
    def __init__(self, category: str, description: str):
        self.category = category
        self.description = description


class GeometricForm(Enum):
    """Geometric forms used in pentacles."""
    
    CIRCLE = "concentric rings"
    HEXAGRAM = "six-pointed star (Star of David)"
    PENTAGRAM = "five-pointed star"
    SQUARE = "four-fold symmetry"
    CROSS = "four directions"
    WHEEL = "radial spokes"
    TRIANGLE = "threefold form"
    SIGIL = "abstract glyph"
    
    
# =============================================================================
# DIVINE NAMES ON PENTACLES
# =============================================================================

# Names commonly inscribed on pentacles
PENTACLE_NAMES = {
    "YHVH": ("יהוה", 26, "Tetragrammaton"),
    "ADONAI": ("אדני", 65, "Lord"),
    "EHEIEH": ("אהיה", 21, "I Am"),
    "AGLA": ("אגלא", 35, "Thou art mighty forever"),
    "EL": ("אל", 31, "God"),
    "ELOHIM": ("אלהים", 86, "Gods/Powers"),
    "SHADDAI": ("שדי", 314, "Almighty"),
    "TZABAOTH": ("צבאות", 499, "Hosts/Armies"),
    "ELION": ("עליון", 166, "Most High"),
    "IAH": ("יה", 15, "Jah"),
    "ELOAH": ("אלוה", 42, "God singular"),
    "ARARITA": ("אראריתא", 813, "Unity formula"),
}


# =============================================================================
# PENTACLE SPECIFICATION
# =============================================================================

@dataclass
class PentacleSpec:
    """
    Specification for a single pentacle.
    
    P_k = (G_k, N_k, V_k, Π_k)
    """
    
    # Identity
    planet: Planet
    number: int  # 1-7 within planet
    
    # Geometry
    form: GeometricForm
    rings: int = 2  # Number of concentric circles
    
    # Names inscribed
    names: List[str] = field(default_factory=list)
    
    # Verse/scriptural reference
    verse: str = ""
    psalm_reference: Optional[str] = None
    
    # Effect
    effect: EffectType = EffectType.PROTECTION
    effect_description: str = ""
    
    # State
    consecrated: bool = False
    
    @property
    def id(self) -> str:
        """Unique pentacle ID."""
        return f"{self.planet.name}_{self.number}"
    
    @property
    def full_name(self) -> str:
        """Full descriptive name."""
        ordinal = ["First", "Second", "Third", "Fourth", 
                   "Fifth", "Sixth", "Seventh"][self.number - 1]
        return f"{ordinal} Pentacle of {self.planet.name.title()}"
    
    def gematria_sum(self) -> int:
        """Sum of gematria values of inscribed names."""
        total = 0
        for name in self.names:
            if name in PENTACLE_NAMES:
                total += PENTACLE_NAMES[name][1]
        return total
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.full_name,
            "planet": self.planet.name,
            "form": self.form.name,
            "names": self.names,
            "verse": self.verse,
            "psalm": self.psalm_reference,
            "effect": self.effect.name,
            "description": self.effect_description,
            "consecrated": self.consecrated,
            "gematria": self.gematria_sum(),
        }


# =============================================================================
# THE 44 PENTACLES
# =============================================================================

def create_saturn_pentacles() -> List[PentacleSpec]:
    """Create the 7 Pentacles of Saturn."""
    return [
        PentacleSpec(
            planet=Planet.SATURN,
            number=1,
            form=GeometricForm.SQUARE,
            names=["YHVH", "ELOHIM"],
            verse="He hath put all things under his feet",
            psalm_reference="Psalm 72:8",
            effect=EffectType.BINDING,
            effect_description="To compel others to submit unto thee"
        ),
        PentacleSpec(
            planet=Planet.SATURN,
            number=2,
            form=GeometricForm.WHEEL,
            names=["YHVH", "ADONAI", "IAH", "EHEIEH"],
            verse="His enemies shall lick the dust",
            psalm_reference="Psalm 72:9",
            effect=EffectType.DESTRUCTION,
            effect_description="Against adversaries, to repress pride of spirits"
        ),
        PentacleSpec(
            planet=Planet.SATURN,
            number=3,
            form=GeometricForm.HEXAGRAM,
            names=["ADONAI"],
            verse="Defend me from mine enemies",
            effect=EffectType.PROTECTION,
            effect_description="Defense against plots and enemies"
        ),
        PentacleSpec(
            planet=Planet.SATURN,
            number=4,
            form=GeometricForm.SQUARE,
            names=["YHVH", "TZABAOTH"],
            effect=EffectType.KNOWLEDGE,
            effect_description="To know answers to questions and secrets"
        ),
        PentacleSpec(
            planet=Planet.SATURN,
            number=5,
            form=GeometricForm.CIRCLE,
            names=["ARARITA"],
            effect=EffectType.PROTECTION,
            effect_description="Protect the home and guard places"
        ),
        PentacleSpec(
            planet=Planet.SATURN,
            number=6,
            form=GeometricForm.CROSS,
            names=["ELOHIM"],
            effect=EffectType.BINDING,
            effect_description="To make others listen and obey"
        ),
        PentacleSpec(
            planet=Planet.SATURN,
            number=7,
            form=GeometricForm.SIGIL,
            names=["YHVH", "SHADDAI"],
            effect=EffectType.DESTRUCTION,
            effect_description="To cause earthquakes or bring ruin to enemies"
        ),
    ]


def create_jupiter_pentacles() -> List[PentacleSpec]:
    """Create the 7 Pentacles of Jupiter."""
    return [
        PentacleSpec(
            planet=Planet.JUPITER,
            number=1,
            form=GeometricForm.HEXAGRAM,
            names=["EL", "ADONAI"],
            effect=EffectType.KNOWLEDGE,
            effect_description="To invoke Spirits of Jupiter, treasure finding"
        ),
        PentacleSpec(
            planet=Planet.JUPITER,
            number=2,
            form=GeometricForm.SQUARE,
            names=["YHVH", "ELOHIM"],
            verse="Wealth and riches shall be in his house",
            psalm_reference="Psalm 112:3",
            effect=EffectType.WEALTH,
            effect_description="To acquire glory, honors, and riches"
        ),
        PentacleSpec(
            planet=Planet.JUPITER,
            number=3,
            form=GeometricForm.HEXAGRAM,
            names=["AGLA", "IAH"],
            effect=EffectType.PROTECTION,
            effect_description="Defense against spirits and dangers"
        ),
        PentacleSpec(
            planet=Planet.JUPITER,
            number=4,
            form=GeometricForm.SQUARE,
            names=["ADONAI", "EL"],
            effect=EffectType.WEALTH,
            effect_description="To acquire wealth and honor"
        ),
        PentacleSpec(
            planet=Planet.JUPITER,
            number=5,
            form=GeometricForm.SIGIL,
            names=["YHVH"],
            effect=EffectType.KNOWLEDGE,
            effect_description="True visions, especially in dreams"
        ),
        PentacleSpec(
            planet=Planet.JUPITER,
            number=6,
            form=GeometricForm.HEXAGRAM,
            names=["ELOHIM", "TZABAOTH"],
            effect=EffectType.PROTECTION,
            effect_description="Protection against earthly dangers"
        ),
        PentacleSpec(
            planet=Planet.JUPITER,
            number=7,
            form=GeometricForm.WHEEL,
            names=["EL", "ELION"],
            effect=EffectType.AUTHORITY,
            effect_description="Power to command and dominate"
        ),
    ]


def create_mars_pentacles() -> List[PentacleSpec]:
    """Create the 7 Pentacles of Mars."""
    return [
        PentacleSpec(
            planet=Planet.MARS,
            number=1,
            form=GeometricForm.HEXAGRAM,
            names=["ELOHIM", "TZABAOTH"],
            effect=EffectType.AUTHORITY,
            effect_description="To invoke Martial Spirits"
        ),
        PentacleSpec(
            planet=Planet.MARS,
            number=2,
            form=GeometricForm.SIGIL,
            names=["YHVH"],
            effect=EffectType.HEALING,
            effect_description="Against diseases and for healing"
        ),
        PentacleSpec(
            planet=Planet.MARS,
            number=3,
            form=GeometricForm.HEXAGRAM,
            names=["ELOHIM"],
            effect=EffectType.DESTRUCTION,
            effect_description="Exciting war and discord"
        ),
        PentacleSpec(
            planet=Planet.MARS,
            number=4,
            form=GeometricForm.PENTAGRAM,
            names=["AGLA", "ADONAI"],
            effect=EffectType.PROTECTION,
            effect_description="Victory in battle and disputes"
        ),
        PentacleSpec(
            planet=Planet.MARS,
            number=5,
            form=GeometricForm.SIGIL,
            names=["ELOHIM"],
            effect=EffectType.DESTRUCTION,
            effect_description="To cause demons to obey instantly"
        ),
        PentacleSpec(
            planet=Planet.MARS,
            number=6,
            form=GeometricForm.HEXAGRAM,
            names=["ADONAI"],
            effect=EffectType.PROTECTION,
            effect_description="Defense in battle, against weapons"
        ),
        PentacleSpec(
            planet=Planet.MARS,
            number=7,
            form=GeometricForm.WHEEL,
            names=["YHVH", "SHADDAI"],
            effect=EffectType.DESTRUCTION,
            effect_description="To cause discord and ruin enemies"
        ),
    ]


def create_sun_pentacles() -> List[PentacleSpec]:
    """Create the 7 Pentacles of the Sun."""
    return [
        PentacleSpec(
            planet=Planet.SUN,
            number=1,
            form=GeometricForm.HEXAGRAM,
            names=["SHADDAI", "EL"],
            effect=EffectType.AUTHORITY,
            effect_description="To invoke Spirits who will transport you"
        ),
        PentacleSpec(
            planet=Planet.SUN,
            number=2,
            form=GeometricForm.CIRCLE,
            names=["YHVH", "ELOHIM"],
            effect=EffectType.KNOWLEDGE,
            effect_description="To suppress pride of Solar Spirits"
        ),
        PentacleSpec(
            planet=Planet.SUN,
            number=3,
            form=GeometricForm.HEXAGRAM,
            names=["EHEIEH", "EL"],
            effect=EffectType.WEALTH,
            effect_description="To acquire kingdom and empire"
        ),
        PentacleSpec(
            planet=Planet.SUN,
            number=4,
            form=GeometricForm.SIGIL,
            names=["ELOHIM"],
            effect=EffectType.INVISIBILITY,
            effect_description="To render oneself invisible"
        ),
        PentacleSpec(
            planet=Planet.SUN,
            number=5,
            form=GeometricForm.PENTAGRAM,
            names=["ADONAI"],
            effect=EffectType.TRANSFORMATION,
            effect_description="To invoke those who give transportation"
        ),
        PentacleSpec(
            planet=Planet.SUN,
            number=6,
            form=GeometricForm.WHEEL,
            names=["YHVH", "ADONAI"],
            effect=EffectType.TRANSFORMATION,
            effect_description="For excellent operations of invisibility"
        ),
        PentacleSpec(
            planet=Planet.SUN,
            number=7,
            form=GeometricForm.CIRCLE,
            names=["EL", "SHADDAI"],
            effect=EffectType.PROTECTION,
            effect_description="To free from prison and chains"
        ),
    ]


def create_venus_pentacles() -> List[PentacleSpec]:
    """Create the 5 Pentacles of Venus."""
    return [
        PentacleSpec(
            planet=Planet.VENUS,
            number=1,
            form=GeometricForm.HEXAGRAM,
            names=["YHVH", "ADONAI"],
            effect=EffectType.FAVOR,
            effect_description="To obtain love and affection"
        ),
        PentacleSpec(
            planet=Planet.VENUS,
            number=2,
            form=GeometricForm.SIGIL,
            names=["ELOHIM"],
            effect=EffectType.FAVOR,
            effect_description="For obtaining grace and honor"
        ),
        PentacleSpec(
            planet=Planet.VENUS,
            number=3,
            form=GeometricForm.PENTAGRAM,
            names=["YHVH", "EL"],
            effect=EffectType.FAVOR,
            effect_description="To attract love and friendship"
        ),
        PentacleSpec(
            planet=Planet.VENUS,
            number=4,
            form=GeometricForm.CIRCLE,
            names=["ADONAI", "SHADDAI"],
            effect=EffectType.BINDING,
            effect_description="To compel spirits to bring desired person"
        ),
        PentacleSpec(
            planet=Planet.VENUS,
            number=5,
            form=GeometricForm.SIGIL,
            names=["ELOHIM", "TZABAOTH"],
            effect=EffectType.TRANSFORMATION,
            effect_description="To excite to passion any person"
        ),
    ]


def create_mercury_pentacles() -> List[PentacleSpec]:
    """Create the 5 Pentacles of Mercury."""
    return [
        PentacleSpec(
            planet=Planet.MERCURY,
            number=1,
            form=GeometricForm.HEXAGRAM,
            names=["EL", "ADONAI"],
            effect=EffectType.AUTHORITY,
            effect_description="To invoke Spirits under Mercury"
        ),
        PentacleSpec(
            planet=Planet.MERCURY,
            number=2,
            form=GeometricForm.SQUARE,
            names=["ELOHIM", "TZABAOTH"],
            effect=EffectType.BINDING,
            effect_description="Against unruly Spirits"
        ),
        PentacleSpec(
            planet=Planet.MERCURY,
            number=3,
            form=GeometricForm.SIGIL,
            names=["YHVH"],
            effect=EffectType.KNOWLEDGE,
            effect_description="To invoke Spirits who reveal secrets"
        ),
        PentacleSpec(
            planet=Planet.MERCURY,
            number=4,
            form=GeometricForm.WHEEL,
            names=["ADONAI", "EL"],
            effect=EffectType.KNOWLEDGE,
            effect_description="To acquire understanding of all sciences"
        ),
        PentacleSpec(
            planet=Planet.MERCURY,
            number=5,
            form=GeometricForm.HEXAGRAM,
            names=["ELION", "YHVH"],
            effect=EffectType.TRANSFORMATION,
            effect_description="To open doors and locks"
        ),
    ]


def create_moon_pentacles() -> List[PentacleSpec]:
    """Create the 6 Pentacles of the Moon."""
    return [
        PentacleSpec(
            planet=Planet.MOON,
            number=1,
            form=GeometricForm.CIRCLE,
            names=["YHVH", "ELOHIM"],
            effect=EffectType.TRANSFORMATION,
            effect_description="To open doors and portals"
        ),
        PentacleSpec(
            planet=Planet.MOON,
            number=2,
            form=GeometricForm.SIGIL,
            names=["EL", "SHADDAI"],
            effect=EffectType.PROTECTION,
            effect_description="Against perils by water"
        ),
        PentacleSpec(
            planet=Planet.MOON,
            number=3,
            form=GeometricForm.HEXAGRAM,
            names=["ADONAI", "TZABAOTH"],
            effect=EffectType.PROTECTION,
            effect_description="Defense against nocturnal dangers"
        ),
        PentacleSpec(
            planet=Planet.MOON,
            number=4,
            form=GeometricForm.WHEEL,
            names=["EHEIEH", "IAH"],
            effect=EffectType.PROTECTION,
            effect_description="Defense from evil and terror"
        ),
        PentacleSpec(
            planet=Planet.MOON,
            number=5,
            form=GeometricForm.CIRCLE,
            names=["ELOHIM", "EL"],
            effect=EffectType.KNOWLEDGE,
            effect_description="Answers in dreams and visions"
        ),
        PentacleSpec(
            planet=Planet.MOON,
            number=6,
            form=GeometricForm.TRIANGLE,
            names=["YHVH", "ADONAI"],
            effect=EffectType.DESTRUCTION,
            effect_description="To cause rain and tempests"
        ),
    ]


# Create the complete pentacle library
def create_all_pentacles() -> List[PentacleSpec]:
    """Create all 44 pentacles."""
    return (
        create_saturn_pentacles() +
        create_jupiter_pentacles() +
        create_mars_pentacles() +
        create_sun_pentacles() +
        create_venus_pentacles() +
        create_mercury_pentacles() +
        create_moon_pentacles()
    )


# Global pentacle library
PENTACLE_LIBRARY = create_all_pentacles()


# =============================================================================
# PENTACLE KERNEL
# =============================================================================

@dataclass
class PentacleKernel:
    """
    A pentacle as a kernel operator.
    
    K_k: Config → Config
    """
    
    spec: PentacleSpec
    
    # Activation state
    active: bool = False
    power_level: float = 0.0  # 0-1
    
    def activate(self, time_compatible: bool = True) -> bool:
        """
        Activate the kernel.
        
        Requires consecration and time compatibility.
        """
        if not self.spec.consecrated:
            return False
        if not time_compatible:
            self.power_level = 0.25  # Reduced power
        else:
            self.power_level = 1.0
        self.active = True
        return True
    
    def deactivate(self):
        """Deactivate the kernel."""
        self.active = False
        self.power_level = 0.0
    
    def apply(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply the kernel to a configuration.
        
        Returns modified configuration.
        """
        if not self.active:
            return config
        
        # Copy config
        new_config = config.copy()
        
        # Apply effect based on type
        effect_key = f"effect_{self.spec.effect.name.lower()}"
        current = new_config.get(effect_key, 0.0)
        new_config[effect_key] = current + self.power_level
        
        # Record application
        apps = new_config.get("pentacle_applications", [])
        apps.append(self.spec.id)
        new_config["pentacle_applications"] = apps
        
        return new_config


# =============================================================================
# PENTACLE LIBRARY MANAGER
# =============================================================================

@dataclass
class PentacleLibrary:
    """
    Manager for the pentacle library.
    
    Provides access to the 44 pentacles as precompiled kernels.
    """
    
    pentacles: List[PentacleSpec] = field(default_factory=lambda: PENTACLE_LIBRARY.copy())
    kernels: Dict[str, PentacleKernel] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize kernels for all pentacles."""
        for spec in self.pentacles:
            self.kernels[spec.id] = PentacleKernel(spec=spec)
    
    def get_pentacle(self, planet: Planet, number: int) -> Optional[PentacleSpec]:
        """Get a pentacle by planet and number."""
        for p in self.pentacles:
            if p.planet == planet and p.number == number:
                return p
        return None
    
    def get_kernel(self, pentacle_id: str) -> Optional[PentacleKernel]:
        """Get a kernel by pentacle ID."""
        return self.kernels.get(pentacle_id)
    
    def get_by_planet(self, planet: Planet) -> List[PentacleSpec]:
        """Get all pentacles for a planet."""
        return [p for p in self.pentacles if p.planet == planet]
    
    def get_by_effect(self, effect: EffectType) -> List[PentacleSpec]:
        """Get all pentacles with a given effect type."""
        return [p for p in self.pentacles if p.effect == effect]
    
    def consecrate(self, pentacle_id: str) -> bool:
        """Consecrate a pentacle."""
        for p in self.pentacles:
            if p.id == pentacle_id:
                p.consecrated = True
                return True
        return False
    
    def consecrate_all(self):
        """Consecrate all pentacles (for testing)."""
        for p in self.pentacles:
            p.consecrated = True
    
    def total_count(self) -> int:
        """Total number of pentacles."""
        return len(self.pentacles)
    
    def count_by_planet(self) -> Dict[str, int]:
        """Count pentacles by planet."""
        counts = {}
        for planet in Planet:
            counts[planet.name] = len(self.get_by_planet(planet))
        return counts
    
    def count_by_effect(self) -> Dict[str, int]:
        """Count pentacles by effect type."""
        counts = {}
        for effect in EffectType:
            counts[effect.name] = len(self.get_by_effect(effect))
        return counts


# =============================================================================
# VALIDATION
# =============================================================================

def validate_pentacles() -> bool:
    """Validate the pentacles module."""
    
    # Test PentacleSpec
    spec = PentacleSpec(
        planet=Planet.SATURN,
        number=1,
        form=GeometricForm.SQUARE,
        names=["YHVH", "ELOHIM"],
        effect=EffectType.BINDING,
    )
    assert spec.id == "SATURN_1"
    assert spec.full_name == "First Pentacle of Saturn"
    assert spec.gematria_sum() == 26 + 86  # YHVH + ELOHIM
    
    # Test PentacleKernel
    kernel = PentacleKernel(spec=spec)
    assert not kernel.active
    
    # Cannot activate without consecration
    assert not kernel.activate()
    
    # Consecrate and activate
    spec.consecrated = True
    assert kernel.activate()
    assert kernel.active
    assert kernel.power_level == 1.0
    
    # Test apply
    config = {"test": True}
    new_config = kernel.apply(config)
    assert "effect_binding" in new_config
    
    kernel.deactivate()
    assert not kernel.active
    
    # Test PentacleLibrary
    library = PentacleLibrary()
    assert library.total_count() == 44
    
    # Check planet counts
    counts = library.count_by_planet()
    assert counts["SATURN"] == 7
    assert counts["JUPITER"] == 7
    assert counts["VENUS"] == 5
    assert counts["MERCURY"] == 5
    assert counts["MOON"] == 6
    
    # Test retrieval
    saturn_1 = library.get_pentacle(Planet.SATURN, 1)
    assert saturn_1 is not None
    assert saturn_1.effect == EffectType.BINDING
    
    protection = library.get_by_effect(EffectType.PROTECTION)
    assert len(protection) > 0
    
    # Test consecration
    assert library.consecrate("JUPITER_2")
    jupiter_2 = library.get_pentacle(Planet.JUPITER, 2)
    assert jupiter_2.consecrated
    
    return True


if __name__ == "__main__":
    print("Validating Pentacles Module...")
    assert validate_pentacles()
    print("✓ Pentacles module validated")
    
    # Demo
    print("\n--- Pentacle Library Demo ---")
    
    library = PentacleLibrary()
    
    print(f"\nTotal pentacles: {library.total_count()}")
    
    print("\nBy planet:")
    for planet, count in library.count_by_planet().items():
        print(f"  {planet}: {count}")
    
    print("\nBy effect:")
    for effect, count in library.count_by_effect().items():
        print(f"  {effect}: {count}")
    
    print("\nSample pentacles:")
    for planet in [Planet.SATURN, Planet.JUPITER, Planet.SUN]:
        p = library.get_pentacle(planet, 1)
        if p:
            print(f"  {p.full_name}")
            print(f"    Effect: {p.effect.name} - {p.effect_description}")
            print(f"    Names: {', '.join(p.names)}")
