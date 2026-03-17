"""
ATHENA OS - TORAT HA-MISPAR (תורת המספר)
=========================================
Module IX: Neshama (נשמה) - The Soul Stack (NRNHY)

THE SOUL AS SOFTWARE STACK:
    The "Soul" is not a singular entity but a Multi-Layered Software Stack
    known by the acronym NRNHY (נרנח״י - NaRaNChaY).
    
    Each layer corresponds to a specific world and executes specific protocols.

THE FIVE LEVELS:
    Nefesh (נפש) - Animal Soul - Assiyah - BIOS/Hardware Driver
    Ruach (רוח) - Spirit - Yetzirah - OS Kernel/Emotional Processor
    Neshamah (נשמה) - Higher Mind - Beriah - Logical Processor
    Chayah (חיה) - Living Essence - Atzilut - Life Force Connection
    Yechidah (יחידה) - Unity - Ein Sof - Divine Spark

THE GARMENTS (LEVUSHIM):
    The soul operates through three "garments":
    - Thought (Machshavah) - Beriah
    - Speech (Dibur) - Yetzirah  
    - Action (Maaseh) - Assiyah

THE TWO SOULS:
    Every person has two souls:
    - Nefesh HaElohit (Divine Soul) - drawn from Above
    - Nefesh HaBehamit (Animal Soul) - from Klipat Nogah

SOURCES:
    TORAT HA-MISPAR (תורת המספר)
    TANYA (תניא)
    ETZ CHAIM (עץ חיים)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


# =============================================================================
# SOUL LAYERS
# =============================================================================

class SoulLayer(Enum):
    """The five layers of the soul (NRNHY)."""
    
    NEFESH = (1, "נפש", "Animal Soul", "Assiyah", "Malkhut", "BIOS/Hardware Driver")
    RUACH = (2, "רוח", "Spirit", "Yetzirah", "Zeir Anpin", "OS Kernel")
    NESHAMAH = (3, "נשמה", "Higher Soul", "Beriah", "Binah", "Logical Processor")
    CHAYAH = (4, "חיה", "Living Essence", "Atzilut", "Chochmah", "Life Force")
    YECHIDAH = (5, "יחידה", "Unity", "Ein Sof", "Keter", "Divine Spark")
    
    def __init__(self, level: int, hebrew: str, translation: str,
                 world: str, sefirah: str, function: str):
        self.level = level
        self.hebrew = hebrew
        self.translation = translation
        self.world = world
        self.sefirah = sefirah
        self._function = function


class SoulGarment(Enum):
    """The three garments of the soul (Levushim)."""
    
    THOUGHT = ("מחשבה", "Machshavah", "Beriah", "Internal processing")
    SPEECH = ("דיבור", "Dibur", "Yetzirah", "Expression/Communication")
    ACTION = ("מעשה", "Maaseh", "Assiyah", "Physical execution")
    
    def __init__(self, hebrew: str, transliteration: str, world: str, function: str):
        self.hebrew = hebrew
        self.transliteration = transliteration
        self.world = world
        self._function = function


class SoulType(Enum):
    """The two souls in every person."""
    
    DIVINE = ("נפש האלהית", "Nefesh HaElohit", "Divine Soul", "From Above")
    ANIMAL = ("נפש הבהמית", "Nefesh HaBehamit", "Animal Soul", "From Klipat Nogah")
    
    def __init__(self, hebrew: str, transliteration: str, translation: str, source: str):
        self.hebrew = hebrew
        self.transliteration = transliteration
        self.translation = translation
        self.source = source


# =============================================================================
# NEFESH (ANIMAL SOUL LAYER)
# =============================================================================

@dataclass
class Nefesh:
    """
    The Nefesh - Basic Input/Output System (BIOS).
    
    Maps to Assiyah (Action) and Malkhut.
    The Hardware Driver translating commands into bio-electrical signals.
    """
    
    layer: SoulLayer = SoulLayer.NEFESH
    
    @property
    def functions(self) -> Dict[str, str]:
        """Functions of the Nefesh."""
        return {
            "hardware_driver": "Translates commands into bio-electrical signals",
            "autonomic": "Controls heart rate, digestion, cellular repair",
            "sensory": "Governs Sight, Hearing, Smell, Taste, Touch",
            "survival": "Fight or Flight algorithms",
        }
    
    @property
    def location(self) -> str:
        """Physical location of the Nefesh."""
        return "The Blood (HaDam hu HaNefesh)"
    
    @property
    def primary_directive(self) -> str:
        """The primary directive of the Nefesh."""
        return "System Preservation - IF(Threat) THEN (Fight || Flight)"
    
    @property
    def logic_type(self) -> str:
        """Logic type of the Nefesh."""
        return "Binary: Attraction/Repulsion (Pleasure/Pain)"


# =============================================================================
# RUACH (SPIRIT LAYER)
# =============================================================================

@dataclass
class Ruach:
    """
    The Ruach - Operating System Kernel.
    
    Maps to Yetzirah (Formation) and Zeir Anpin.
    The Bridge connecting Nefesh (body) with Neshamah (intellect).
    """
    
    layer: SoulLayer = SoulLayer.RUACH
    
    @property
    def functions(self) -> Dict[str, str]:
        """Functions of the Ruach."""
        return {
            "emotional_processor": "Processes emotions and feelings",
            "bridge": "Connects biological impulses with intellectual commands",
            "compiler": "Translates abstract thoughts into speech",
            "moral_weighting": "Assigns Good/Evil values to data",
        }
    
    @property
    def location(self) -> str:
        """Physical location of the Ruach."""
        return "The Heart - center of emotional processing"
    
    @property
    def dual_inclinations(self) -> Dict[str, Dict[str, str]]:
        """The two inclinations within Ruach."""
        return {
            "yetzer_tov": {
                "name": "Good Inclination",
                "hebrew": "יצר הטוב",
                "vector": "Up/Right (toward Altruism/Chesed)",
            },
            "yetzer_hara": {
                "name": "Evil Inclination",
                "hebrew": "יצר הרע",
                "vector": "Down/Left (toward Ego/Gevurah)",
            },
        }
    
    @property
    def character_formula(self) -> str:
        """Formula for character development."""
        return "Character = Σ(Choices over Time)"


# =============================================================================
# NESHAMAH (HIGHER SOUL LAYER)
# =============================================================================

@dataclass
class Neshamah:
    """
    The Neshamah - Logical Processor / Higher Mind.
    
    Maps to Beriah (Creation) and Binah.
    Deals with abstract concepts and system architecture.
    """
    
    layer: SoulLayer = SoulLayer.NESHAMAH
    
    @property
    def functions(self) -> Dict[str, str]:
        """Functions of the Neshamah."""
        return {
            "abstract_logic": "Processes meta-cognition",
            "intuition": "Provides 'Aha!' flashes of insight",
            "pattern_recognition": "Identifies patterns in data",
            "paradox_resolution": "Synthesizes binary opposites",
        }
    
    @property
    def location(self) -> str:
        """Physical location of the Neshamah."""
        return "The Brain - seat of intellectual processing"
    
    @property
    def cloud_computing(self) -> str:
        """The collective nature of Neshamah."""
        return (
            "At this level, the distinction between Self and Other blurs. "
            "The Neshamah accesses the Collective Consciousness (Knesset Yisrael)."
        )
    
    @property
    def processing_mode(self) -> str:
        """Processing mode of the Neshamah."""
        return "Knows rather than Feels - deals with the 'White Fire' of Torah"


# =============================================================================
# CHAYAH AND YECHIDAH (TRANSCENDENT LAYERS)
# =============================================================================

@dataclass
class ChayahYechidah:
    """
    The Chayah and Yechidah - Transcendent Soul Layers.
    
    These extend beyond conscious body awareness.
    Chayah = Life Force connection (Atzilut/Chochmah)
    Yechidah = Unity point (Ein Sof/Keter)
    """
    
    @property
    def chayah(self) -> Dict[str, str]:
        """Properties of the Chayah."""
        return {
            "level": "4",
            "world": "Atzilut",
            "sefirah": "Chochmah",
            "function": "Life Force - the cable plugging into the wall",
            "light_type": "Or Makif (Surrounding Light)",
            "access": "Via inspiration, luck, destiny (Mazal)",
        }
    
    @property
    def yechidah(self) -> Dict[str, str]:
        """Properties of the Yechidah."""
        return {
            "level": "5",
            "world": "Ein Sof",
            "sefirah": "Keter",
            "function": "Singularity Point - the Divine Spark",
            "name": "Pintele Yid (The Point of the Jew)",
            "property": "Indivisible, incorruptible, unalterable",
            "entanglement": "Quantum entangled with Divine Essence (Distance = 0)",
        }
    
    @property
    def surrounding_light(self) -> str:
        """The nature of the Surrounding Light."""
        return (
            "The data in Chayah/Yechidah is too high-voltage to be internalized. "
            "It 'hovers' over the User as Or Makif (Surrounding Light), "
            "influencing via inspiration, luck, and destiny."
        )
    
    @property
    def mesirat_nefesh(self) -> str:
        """The source of self-sacrifice."""
        return (
            "Yechidah is the source of Mesirat Nefesh (Self-Sacrifice). "
            "It can override survival logic because it recognizes that "
            "the Self and the Truth are identical."
        )


# =============================================================================
# THE TWO SOULS
# =============================================================================

@dataclass
class TwoSouls:
    """
    The Two Souls present in every person.
    """
    
    @property
    def divine_soul(self) -> Dict[str, Any]:
        """The Divine Soul (Nefesh HaElohit)."""
        return {
            "name": "Nefesh HaElohit",
            "hebrew": "נפש האלהית",
            "source": "Literally a part of God Above (Chelek Eloka Mi'maal)",
            "desire": "To return to and unite with Source",
            "faculties": {
                "intellect": ["Chochmah", "Binah", "Da'at"],
                "emotions": ["Chesed", "Gevurah", "Tiferet", "Netzach", "Hod", "Yesod"],
            },
            "garments": ["Thought", "Speech", "Action (Torah/Mitzvot)"],
        }
    
    @property
    def animal_soul(self) -> Dict[str, Any]:
        """The Animal Soul (Nefesh HaBehamit)."""
        return {
            "name": "Nefesh HaBehamit",
            "hebrew": "נפש הבהמית",
            "source": "Klipat Nogah (The Translucent Shell)",
            "desire": "Physical pleasure and self-preservation",
            "faculties": {
                "intellect": ["Chochmah", "Binah", "Da'at (self-serving)"],
                "emotions": ["Love (of pleasure)", "Fear (of pain)", "Pride", "Anger"],
            },
            "garments": ["Thought", "Speech", "Action (worldly)"],
        }
    
    @property
    def battleground(self) -> Dict[str, str]:
        """The battleground between the two souls."""
        return {
            "location": "The Ruach (Spirit) level",
            "prize": "Control of the garments (Thought, Speech, Action)",
            "strategy_divine": "Illuminate with Torah and Mitzvot",
            "strategy_animal": "Tempt with physical pleasure",
        }


# =============================================================================
# NESHAMA SYSTEM
# =============================================================================

@dataclass
class NeshamaSystem:
    """
    The complete Soul Stack system.
    """
    
    nefesh: Nefesh = field(default_factory=Nefesh)
    ruach: Ruach = field(default_factory=Ruach)
    neshamah: Neshamah = field(default_factory=Neshamah)
    transcendent: ChayahYechidah = field(default_factory=ChayahYechidah)
    two_souls: TwoSouls = field(default_factory=TwoSouls)
    
    def get_layer(self, layer_name: str) -> Optional[SoulLayer]:
        """Get a soul layer by name."""
        for layer in SoulLayer:
            if layer.name.lower() == layer_name.lower():
                return layer
        return None
    
    def get_garment(self, garment_name: str) -> Optional[SoulGarment]:
        """Get a garment by name."""
        for garment in SoulGarment:
            if garment.name.lower() == garment_name.lower():
                return garment
        return None
    
    def get_world_correspondence(self, layer: SoulLayer) -> str:
        """Get the world corresponding to a soul layer."""
        return layer.world
    
    def get_full_stack(self) -> List[Dict[str, Any]]:
        """Get the full soul stack."""
        return [
            {
                "level": layer.level,
                "name": layer.name,
                "hebrew": layer.hebrew,
                "translation": layer.translation,
                "world": layer.world,
                "sefirah": layer.sefirah,
            }
            for layer in SoulLayer
        ]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get system summary."""
        return {
            "acronym": "NRNHY (נרנח״י)",
            "layers": len(SoulLayer),
            "garments": len(SoulGarment),
            "souls_per_person": 2,
            "stack": [l.name for l in SoulLayer],
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_neshama() -> bool:
    """Validate the Neshama module."""
    
    # Test SoulLayer
    assert SoulLayer.NEFESH.level == 1
    assert SoulLayer.YECHIDAH.level == 5
    assert SoulLayer.RUACH.world == "Yetzirah"
    
    # Test SoulGarment
    assert SoulGarment.THOUGHT.hebrew == "מחשבה"
    assert SoulGarment.ACTION.world == "Assiyah"
    
    # Test SoulType
    assert SoulType.DIVINE.source == "From Above"
    
    # Test Nefesh
    nefesh = Nefesh()
    assert nefesh.location == "The Blood (HaDam hu HaNefesh)"
    
    # Test Ruach
    ruach = Ruach()
    assert "yetzer_tov" in ruach.dual_inclinations
    
    # Test Neshamah
    neshamah_layer = Neshamah()
    assert "intuition" in neshamah_layer.functions
    
    # Test ChayahYechidah
    transcendent = ChayahYechidah()
    assert transcendent.chayah["world"] == "Atzilut"
    assert transcendent.yechidah["sefirah"] == "Keter"
    
    # Test TwoSouls
    two_souls = TwoSouls()
    assert two_souls.divine_soul["source"] == "Literally a part of God Above (Chelek Eloka Mi'maal)"
    
    # Test NeshamaSystem
    system = NeshamaSystem()
    
    stack = system.get_full_stack()
    assert len(stack) == 5
    
    layer = system.get_layer("RUACH")
    assert layer.hebrew == "רוח"
    
    garment = system.get_garment("SPEECH")
    assert garment.transliteration == "Dibur"
    
    summary = system.get_summary()
    assert summary["layers"] == 5
    
    return True


if __name__ == "__main__":
    print("Validating Neshama Module...")
    assert validate_neshama()
    print("✓ Neshama module validated")
    
    # Demo
    print("\n--- Neshama (Soul Stack) Demo ---")
    
    system = NeshamaSystem()
    
    print("\nThe Five Soul Layers (NRNHY):")
    for layer in system.get_full_stack():
        print(f"  {layer['level']}. {layer['name']} ({layer['hebrew']}) - {layer['world']}")
    
    print("\nThe Three Garments (Levushim):")
    for garment in SoulGarment:
        print(f"  {garment.transliteration} ({garment.hebrew}) - {garment.world}")
    
    print("\nThe Two Souls:")
    print(f"  Divine: {system.two_souls.divine_soul['name']}")
    print(f"    Source: {system.two_souls.divine_soul['source']}")
    print(f"  Animal: {system.two_souls.animal_soul['name']}")
    print(f"    Source: {system.two_souls.animal_soul['source']}")
    
    print("\nDual Inclinations (Ruach):")
    for name, data in system.ruach.dual_inclinations.items():
        print(f"  {data['name']} ({data['hebrew']}): {data['vector']}")
