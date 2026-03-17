"""
ATHENA OS - TORAT HA-MISPAR (תורת המספר)
=========================================
Module VI: Olamot (עולמות) - The Four Worlds

THE FOUR WORLDS:
    Atzilut (אצילות) - Emanation - Near to Source
    Beriah (בריאה) - Creation - Something from Nothing
    Yetzirah (יצירה) - Formation - Shaping existing matter
    Assiyah (עשיה) - Action - Physical manifestation

THE CHAIN OF DESCENT:
    Data flows from Ein Sof through four levels of "stepping down"
    until it manifests as physical reality.
    
    Each world has its own complete Tree of Life.
    Each world contains 10 Sefirot = 40 Sefirot total.

THE SOUL LEVELS:
    Yechidah (יחידה) - Unity - Atzilut
    Chayah (חיה) - Living Essence - Atzilut
    Neshamah (נשמה) - Breath/Soul - Beriah
    Ruach (רוח) - Spirit - Yetzirah
    Nefesh (נפש) - Animal Soul - Assiyah

OLAM ETYMOLOGY:
    עולם (Olam) derives from העלם (Helem) - Concealment
    Each world is a layer of concealment from the Source.

SOURCES:
    TORAT HA-MISPAR (תורת המספר)
    ETZ CHAIM (עץ חיים)
    TANYA (תניא)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


# =============================================================================
# SOUL LEVELS
# =============================================================================

class SoulLevel(Enum):
    """The five levels of the soul."""
    
    YECHIDAH = ("יחידה", "Unity", "Keter", "Atzilut", "Complete union with Divine")
    CHAYAH = ("חיה", "Living Essence", "Chochmah", "Atzilut", "Life force interface")
    NESHAMAH = ("נשמה", "Breath/Soul", "Binah", "Beriah", "Intellectual soul")
    RUACH = ("רוח", "Spirit", "Midot", "Yetzirah", "Emotional soul")
    NEFESH = ("נפש", "Animal Soul", "Malkhut", "Assiyah", "Vital/Animal nature")
    
    def __init__(self, hebrew: str, translation: str, sefirah: str, world: str, function: str):
        self.hebrew = hebrew
        self.translation = translation
        self.sefirah = sefirah
        self.world = world
        self._function = function


# =============================================================================
# WORLD DEFINITION
# =============================================================================

@dataclass
class World:
    """
    A World (Olam) - Level of Divine Concealment.
    """
    
    # Identity
    name: str
    hebrew: str
    translation: str
    
    # Position
    number: int  # 1-4 (1 = closest to Source)
    
    # Properties
    element: str
    tetragrammaton_letter: str
    primary_sefirah: str
    creation_mode: str
    
    # Soul correspondence
    soul_levels: List[str]
    
    # Reality type
    reality_type: str
    
    # Description
    description: str
    
    @property
    def concealment_level(self) -> int:
        """Level of concealment (higher = more concealment)."""
        return 5 - self.number  # 4, 3, 2, 1


# =============================================================================
# THE FOUR WORLDS
# =============================================================================

WORLDS = [
    World(
        name="Atzilut",
        hebrew="אצילות",
        translation="Emanation / Nearness",
        number=1,
        element="Fire",
        tetragrammaton_letter="י (Yod)",
        primary_sefirah="Chochmah",
        creation_mode="Emanation - direct extension of Divine",
        soul_levels=["Yechidah", "Chayah"],
        reality_type="Pure Divinity - no independent existence",
        description=(
            "The world of Emanation where the light of Ein Sof still "
            "shines in its purity. The Sefirot here are still unified "
            "with their Source. No creation yet, only emanation."
        ),
    ),
    World(
        name="Beriah",
        hebrew="בריאה",
        translation="Creation / Ex Nihilo",
        number=2,
        element="Air/Wind",
        tetragrammaton_letter="ה (Heh upper)",
        primary_sefirah="Binah",
        creation_mode="Yesh M'Ayin - Something from Nothing",
        soul_levels=["Neshamah"],
        reality_type="First sense of 'something' separate from Source",
        description=(
            "The world of Creation where 'something' first emerges from "
            "'nothing'. The Throne of Glory (Kisei HaKavod) is here. "
            "Souls are created as distinct entities."
        ),
    ),
    World(
        name="Yetzirah",
        hebrew="יצירה",
        translation="Formation / Shaping",
        number=3,
        element="Water",
        tetragrammaton_letter="ו (Vav)",
        primary_sefirah="Zeir Anpin (6 Midot)",
        creation_mode="Yesh M'Yesh - Something from Something",
        soul_levels=["Ruach"],
        reality_type="Angels and emotional archetypes",
        description=(
            "The world of Formation where existing substance is shaped "
            "into distinct forms. The realm of angels (Malachim) who are "
            "autonomous subroutines executing specific functions."
        ),
    ),
    World(
        name="Assiyah",
        hebrew="עשיה",
        translation="Action / Making",
        number=4,
        element="Earth",
        tetragrammaton_letter="ה (Heh lower)",
        primary_sefirah="Malkhut",
        creation_mode="Physical action and manifestation",
        soul_levels=["Nefesh"],
        reality_type="Physical universe and material reality",
        description=(
            "The world of Action - the physical universe we inhabit. "
            "The endpoint of the chain of descent where infinite light "
            "is maximally concealed within finite material forms."
        ),
    ),
]


# =============================================================================
# INTER-WORLD DYNAMICS
# =============================================================================

@dataclass
class InterWorldDynamics:
    """
    Dynamics between the Four Worlds.
    """
    
    @property
    def chain_of_descent(self) -> List[Dict[str, str]]:
        """The chain of descent from world to world."""
        return [
            {
                "from": "Ein Sof",
                "to": "Atzilut",
                "mechanism": "Tzimtzum and Kav",
                "attenuation": "First filtering",
            },
            {
                "from": "Atzilut",
                "to": "Beriah",
                "mechanism": "Masach (Screen)",
                "attenuation": "From Divine to Created",
            },
            {
                "from": "Beriah",
                "to": "Yetzirah",
                "mechanism": "Masach (Screen)",
                "attenuation": "From Intellectual to Emotional",
            },
            {
                "from": "Yetzirah",
                "to": "Assiyah",
                "mechanism": "Masach (Screen)",
                "attenuation": "From Form to Matter",
            },
        ]
    
    @property
    def malkhut_keter_link(self) -> str:
        """How worlds connect via Malkhut-Keter."""
        return (
            "The Malkhut of a higher world becomes the Keter of the lower world. "
            "Thus: Malkhut of Atzilut = Keter of Beriah, "
            "Malkhut of Beriah = Keter of Yetzirah, "
            "Malkhut of Yetzirah = Keter of Assiyah."
        )
    
    @property
    def total_sefirot(self) -> int:
        """Total Sefirot across all worlds."""
        return 4 * 10  # 40 Sefirot
    
    @property
    def reality_density(self) -> Dict[str, str]:
        """Reality density by world."""
        return {
            "Atzilut": "Pure Light - no vessel distinction",
            "Beriah": "Light > Vessel - primarily spiritual",
            "Yetzirah": "Light = Vessel - balanced",
            "Assiyah": "Vessel > Light - primarily material",
        }


# =============================================================================
# CORRESPONDENCES
# =============================================================================

@dataclass
class WorldCorrespondences:
    """
    Correspondences for each world.
    """
    
    @property
    def biblical_creatures(self) -> Dict[str, str]:
        """Ezekiel's Chariot creatures by world."""
        return {
            "Atzilut": "Man (אדם) - Human face",
            "Beriah": "Lion (אריה) - Right face",
            "Yetzirah": "Ox (שור) - Left face",
            "Assiyah": "Eagle (נשר) - Back face",
        }
    
    @property
    def angels_by_world(self) -> Dict[str, List[str]]:
        """Angelic orders by world."""
        return {
            "Atzilut": ["Seraphim (burning ones)"],
            "Beriah": ["Chayot HaKodesh (holy creatures)", "Ophanim (wheels)"],
            "Yetzirah": ["General angels (Malachim)"],
            "Assiyah": ["Physical nature angels"],
        }
    
    @property
    def consciousness_states(self) -> Dict[str, str]:
        """Consciousness states by world."""
        return {
            "Atzilut": "Unity consciousness - no self/other",
            "Beriah": "Pure intellect - understanding without ego",
            "Yetzirah": "Emotional awareness - love, fear, etc.",
            "Assiyah": "Physical sensation - body awareness",
        }
    
    @property
    def garments_of_soul(self) -> Dict[str, str]:
        """Soul garments by world."""
        return {
            "Atzilut": "Beyond garments - naked essence",
            "Beriah": "Thought (Machshavah)",
            "Yetzirah": "Speech (Dibur)",
            "Assiyah": "Action (Maaseh)",
        }


# =============================================================================
# OLAMOT SYSTEM
# =============================================================================

@dataclass
class OlamotSystem:
    """
    The complete Four Worlds system.
    """
    
    worlds: List[World] = field(default_factory=lambda: WORLDS.copy())
    dynamics: InterWorldDynamics = field(default_factory=InterWorldDynamics)
    correspondences: WorldCorrespondences = field(default_factory=WorldCorrespondences)
    
    def get_world(self, name: str) -> Optional[World]:
        """Get a world by name."""
        for w in self.worlds:
            if w.name.lower() == name.lower():
                return w
        return None
    
    def get_by_number(self, number: int) -> Optional[World]:
        """Get a world by number."""
        for w in self.worlds:
            if w.number == number:
                return w
        return None
    
    def get_soul_level(self, level_name: str) -> Optional[SoulLevel]:
        """Get a soul level by name."""
        for level in SoulLevel:
            if level.name.lower() == level_name.lower():
                return level
        return None
    
    def get_world_for_soul(self, soul_level: str) -> Optional[World]:
        """Get the world corresponding to a soul level."""
        for w in self.worlds:
            if soul_level in w.soul_levels:
                return w
        return None
    
    def trace_descent(self, start_world: str = "Atzilut") -> List[str]:
        """Trace the chain of descent from a world."""
        start_idx = next((w.number for w in self.worlds if w.name == start_world), 1)
        return [w.name for w in self.worlds if w.number >= start_idx]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get system summary."""
        return {
            "total_worlds": len(self.worlds),
            "total_sefirot": self.dynamics.total_sefirot,
            "worlds": [w.name for w in self.worlds],
            "soul_levels": [s.name for s in SoulLevel],
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_olamot() -> bool:
    """Validate the Olamot module."""
    
    # Test World count
    assert len(WORLDS) == 4
    
    # Test World properties
    atzilut = WORLDS[0]
    assert atzilut.name == "Atzilut"
    assert atzilut.number == 1
    assert atzilut.element == "Fire"
    
    assiyah = WORLDS[3]
    assert assiyah.name == "Assiyah"
    assert assiyah.number == 4
    assert assiyah.element == "Earth"
    
    # Test SoulLevel
    assert SoulLevel.YECHIDAH.hebrew == "יחידה"
    assert SoulLevel.NEFESH.world == "Assiyah"
    
    # Test InterWorldDynamics
    dynamics = InterWorldDynamics()
    assert dynamics.total_sefirot == 40
    
    chain = dynamics.chain_of_descent
    assert len(chain) == 4
    
    # Test OlamotSystem
    system = OlamotSystem()
    
    beriah = system.get_world("Beriah")
    assert beriah is not None
    assert beriah.number == 2
    
    world_by_num = system.get_by_number(3)
    assert world_by_num.name == "Yetzirah"
    
    neshamah_world = system.get_world_for_soul("Neshamah")
    assert neshamah_world.name == "Beriah"
    
    descent = system.trace_descent("Beriah")
    assert descent == ["Beriah", "Yetzirah", "Assiyah"]
    
    summary = system.get_summary()
    assert summary["total_worlds"] == 4
    assert summary["total_sefirot"] == 40
    
    return True


if __name__ == "__main__":
    print("Validating Olamot Module...")
    assert validate_olamot()
    print("✓ Olamot module validated")
    
    # Demo
    print("\n--- Olamot (Four Worlds) System Demo ---")
    
    system = OlamotSystem()
    
    print("\nThe Four Worlds:")
    for w in system.worlds:
        print(f"  {w.number}. {w.name} ({w.hebrew}) - {w.translation}")
        print(f"     Element: {w.element} | Letter: {w.tetragrammaton_letter}")
        print(f"     Soul: {w.soul_levels}")
    
    print("\nChain of Descent:")
    for link in system.dynamics.chain_of_descent:
        print(f"  {link['from']} → {link['to']}")
        print(f"    Mechanism: {link['mechanism']}")
    
    print(f"\nTotal Sefirot: {system.dynamics.total_sefirot} (4 worlds × 10)")
    
    print("\nSoul Levels:")
    for level in SoulLevel:
        print(f"  {level.name} ({level.hebrew}) - {level.world}")
    
    print("\nMalkhut-Keter Link:")
    print(f"  {system.dynamics.malkhut_keter_link[:100]}...")
    
    print("\nReality Density:")
    for world, density in system.dynamics.reality_density.items():
        print(f"  {world}: {density}")
