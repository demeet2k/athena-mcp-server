"""
ATHENA OS - TORAT HA-MISPAR (תורת המספר)
=========================================
Module VII: Shevirah (שבירה) - The Breaking of the Vessels

SHEVIRAT HAKELIM DEFINED:
    The catastrophic system failure in the initial creation.
    The vessels (Kelim) could not contain the light intensity
    and shattered, scattering holy sparks (Nitzotzot) into chaos.

THE WORLD OF TOHU:
    Olam HaTohu - World of Chaos
    Characterized by high-intensity lights in weak vessels.
    Vessels were isolated (not interconnected) - single-threaded.
    
    The system crashed due to:
    1. Voltage overload (lights too intense)
    2. Buffer isolation (no inter-node communication)
    3. Ego-logic (each vessel only for itself)

THE KLIPOT (SHELLS):
    After the breaking, the fallen vessel fragments became Klipot.
    They encapsulate the holy sparks, creating the realm of evil.
    
    Four Klipot:
    - Klipat Nogah (translucent shell - neutral)
    - Three completely impure shells

THE HOLY SPARKS (NITZOTZOT):
    288 sparks fell into the Klipot.
    They sustain the shells parasitically.
    Extraction = Tikkun (Rectification)

SOURCES:
    TORAT HA-MISPAR (תורת המספר)
    ETZ CHAIM (עץ חיים)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


# =============================================================================
# WORLD STATES
# =============================================================================

class WorldState(Enum):
    """States of the cosmic system."""
    
    TOHU = ("תהו", "Chaos", "Pre-crash high-intensity isolated vessels")
    TIKKUN = ("תיקון", "Rectification", "Post-repair interconnected system")
    BOHU = ("בהו", "Void", "Empty - post-shatter pre-repair")
    
    def __init__(self, hebrew: str, translation: str, description: str):
        self.hebrew = hebrew
        self.translation = translation
        self._description = description


class KlipahType(Enum):
    """Types of Klipot (Shells)."""
    
    NOGAH = ("נוגה", "Translucent", "Neutral - can be elevated")
    RUACH_SEARAH = ("רוח סערה", "Stormy Wind", "Completely impure")
    ANAN_GADOL = ("ענן גדול", "Great Cloud", "Completely impure")
    EISH_MITLAKACHAT = ("אש מתלקחת", "Flaming Fire", "Completely impure")
    
    def __init__(self, hebrew: str, translation: str, nature: str):
        self.hebrew = hebrew
        self.translation = translation
        self.nature = nature


# =============================================================================
# THE OLAM HATOHU (WORLD OF CHAOS)
# =============================================================================

@dataclass
class OlamHaTohu:
    """
    The World of Chaos (Tohu) - Pre-Shattering State.
    
    Characterized by:
    - High-intensity lights (Or Rav)
    - Weak/thin vessels (Kelim Dakim)
    - No inter-vessel communication (isolation)
    """
    
    name: str = "Olam HaTohu"
    hebrew: str = "עולם התהו"
    state: WorldState = WorldState.TOHU
    
    @property
    def characteristics(self) -> Dict[str, Any]:
        """Characteristics of the Tohu world."""
        return {
            "lights": {
                "intensity": "Maximum (Or Rav)",
                "type": "Penetrating, unfiltered",
                "problem": "Too powerful for vessels to contain",
            },
            "vessels": {
                "strength": "Weak/Thin (Kelim Dakim)",
                "topology": "Isolated - no interconnection",
                "problem": "Single-point-of-failure architecture",
            },
            "logic": {
                "type": "Ego-based (Each for itself)",
                "mode": "Single-threaded processing",
                "problem": "No load balancing or redundancy",
            },
        }
    
    @property
    def failure_analysis(self) -> Dict[str, str]:
        """Why the system failed."""
        return {
            "voltage_overload": "Light intensity exceeded vessel capacity",
            "buffer_isolation": "No inter-node communication to distribute load",
            "ego_architecture": "Will to Receive for Self Only",
            "no_resistance": "Vessels had no Masach (Screen) to reflect light",
        }
    
    @property
    def sefirot_state(self) -> Dict[str, str]:
        """State of Sefirot in Tohu."""
        return {
            "configuration": "Linear/Serial - one below the other",
            "interaction": "None - completely isolated",
            "vulnerability": "Each vessel alone against the light",
        }


# =============================================================================
# THE BREAKING EVENT
# =============================================================================

@dataclass
class SheviratHaKelim:
    """
    The Breaking of the Vessels - Critical System Failure.
    
    The catastrophic event where the vessels of Tohu shattered,
    scattering sparks into the lower realms.
    """
    
    name: str = "Shevirat HaKelim"
    hebrew: str = "שבירת הכלים"
    translation: str = "Breaking of the Vessels"
    
    @property
    def event_description(self) -> str:
        """Description of the shattering event."""
        return (
            "The eight lower Sefirot of Tohu (from Da'at to Malkhut) "
            "shattered under the intensity of the light. The upper "
            "Sefirot (Keter, Chochmah, Binah) were damaged but not broken. "
            "The fragments fell into the lower worlds, becoming Klipot."
        )
    
    @property
    def affected_sefirot(self) -> Dict[str, str]:
        """Which Sefirot were affected."""
        return {
            "unbroken": ["Keter", "Chochmah", "Binah"],
            "damaged": ["Da'at"],
            "shattered": ["Chesed", "Gevurah", "Tiferet", "Netzach", "Hod", "Yesod", "Malkhut"],
        }
    
    @property
    def mechanics(self) -> Dict[str, Any]:
        """Mechanics of the breaking."""
        return {
            "sequence": [
                "1. Light descends from Ein Sof through Kav",
                "2. Light fills first vessel (Da'at) - vessel cracks",
                "3. Light overflows to second vessel - more cracking",
                "4. Chain reaction as vessels cannot handle intensity",
                "5. Lower vessels completely shatter",
                "6. Fragments fall carrying sparks into chaos",
            ],
            "sparks_count": 288,
            "sparks_formula": "288 = 32 × 9 (paths × lower Sefirot)",
            "kings_of_edom": 8,  # The 8 kings who died (Gen 36)
        }
    
    @property
    def purposes(self) -> List[str]:
        """The hidden purposes of the breaking."""
        return [
            "Create Free Will - without evil, no choice exists",
            "Enable Tikkun - repair generates greater light",
            "Establish physical world - dense matter requires separation",
            "Create reward/punishment system - consequences require duality",
            "Allow for merit - effort in extracting sparks creates value",
        ]


# =============================================================================
# THE KLIPOT (SHELLS)
# =============================================================================

@dataclass
class Klipah:
    """
    A Klipah (Shell) - Fragment of Broken Vessel.
    
    The Klipot are the outer shells that conceal the holy sparks.
    They constitute the realm of impurity and evil.
    """
    
    type: KlipahType
    
    @property
    def nature(self) -> str:
        """Nature of this Klipah."""
        return self.type.nature
    
    @property
    def elevatable(self) -> bool:
        """Can this Klipah be elevated?"""
        return self.type == KlipahType.NOGAH


@dataclass
class KlipotSystem:
    """
    The System of Klipot (Shells).
    """
    
    @property
    def four_klipot(self) -> List[Dict[str, Any]]:
        """The four Klipot from Ezekiel's vision."""
        return [
            {
                "name": "Klipat Nogah",
                "hebrew": "קליפת נוגה",
                "translation": "Translucent Shell",
                "nature": "Neutral - mixture of good and evil",
                "elevatable": True,
                "correspondence": "Permitted pleasures, neutral activities",
            },
            {
                "name": "Ruach Se'arah",
                "hebrew": "רוח סערה",
                "translation": "Stormy Wind",
                "nature": "Completely impure",
                "elevatable": False,
                "correspondence": "Anger, violence, destruction",
            },
            {
                "name": "Anan Gadol",
                "hebrew": "ענן גדול",
                "translation": "Great Cloud",
                "nature": "Completely impure",
                "elevatable": False,
                "correspondence": "Confusion, depression, darkness",
            },
            {
                "name": "Eish Mitlakachat",
                "hebrew": "אש מתלקחת",
                "translation": "Flaming Fire",
                "nature": "Completely impure",
                "elevatable": False,
                "correspondence": "Desire, passion for forbidden",
            },
        ]
    
    @property
    def function(self) -> Dict[str, str]:
        """Function of the Klipot in the system."""
        return {
            "concealment": "Hide the holy sparks within",
            "sustenance": "Parasitically derive energy from sparks",
            "testing": "Provide obstacles for soul refinement",
            "free_will": "Enable choice between good and evil",
        }
    
    @property
    def parasitic_nature(self) -> str:
        """How Klipot derive their existence."""
        return (
            "The Klipot have no independent connection to the Life Source (Kav). "
            "They survive ONLY by siphoning energy from the holy sparks they contain. "
            "When the spark is extracted, the Klipah collapses into null space."
        )


# =============================================================================
# THE HOLY SPARKS (NITZOTZOT)
# =============================================================================

@dataclass
class HolySparks:
    """
    The Holy Sparks (Nitzotzot) - Trapped Divine Light.
    
    288 sparks fell during the Breaking, distributed throughout
    the four worlds and awaiting extraction.
    """
    
    total_count: int = 288
    
    @property
    def distribution(self) -> Dict[str, Any]:
        """Distribution of sparks."""
        return {
            "formula": "288 = 32 × 9",
            "32_paths": "32 Paths of Wisdom (10 Sefirot + 22 Letters)",
            "9_sefirot": "9 Lower Sefirot (Da'at to Malkhut)",
            "distribution": "Spread throughout all worlds and beings",
        }
    
    @property
    def state_in_klipot(self) -> Dict[str, str]:
        """State of sparks within the Klipot."""
        return {
            "condition": "Imprisoned/Concealed",
            "awareness": "The spark 'cries out' for redemption",
            "energy_drain": "Being parasitically drained by shell",
            "longing": "Desire to reunite with Source",
        }
    
    @property
    def extraction_methods(self) -> List[str]:
        """Methods for extracting sparks."""
        return [
            "Performing Mitzvot (Commandments) with proper intention",
            "Torah study - elevates sparks in intellect",
            "Prayer - elevates sparks through speech",
            "Eating with blessing and sanctity",
            "Using physical objects for holy purposes",
            "Teshuvah (Return) - releases sparks from past transgressions",
        ]


# =============================================================================
# SHEVIRAH SYSTEM
# =============================================================================

@dataclass
class ShevirahSystem:
    """
    The complete Shevirah (Breaking) system.
    """
    
    tohu: OlamHaTohu = field(default_factory=OlamHaTohu)
    breaking: SheviratHaKelim = field(default_factory=SheviratHaKelim)
    klipot: KlipotSystem = field(default_factory=KlipotSystem)
    sparks: HolySparks = field(default_factory=HolySparks)
    
    def analyze_failure(self) -> Dict[str, Any]:
        """Analyze the system failure."""
        return {
            "world_state": self.tohu.state.name,
            "failure_causes": self.tohu.failure_analysis,
            "affected_sefirot": self.breaking.affected_sefirot,
            "result": {
                "sparks_scattered": self.sparks.total_count,
                "klipot_formed": len(self.klipot.four_klipot),
            },
        }
    
    def get_extraction_status(self, sparks_extracted: int) -> Dict[str, Any]:
        """Get status of spark extraction."""
        remaining = self.sparks.total_count - sparks_extracted
        percentage = (sparks_extracted / self.sparks.total_count) * 100
        return {
            "total": self.sparks.total_count,
            "extracted": sparks_extracted,
            "remaining": remaining,
            "percentage_complete": f"{percentage:.2f}%",
            "tikkun_status": "Complete" if remaining == 0 else "In Progress",
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Get system summary."""
        return {
            "tohu": {
                "name": self.tohu.name,
                "state": self.tohu.state.name,
            },
            "breaking": {
                "name": self.breaking.name,
                "sparks": self.breaking.mechanics["sparks_count"],
            },
            "klipot": {
                "count": len(self.klipot.four_klipot),
                "elevatable": 1,  # Only Nogah
            },
            "sparks": {
                "total": self.sparks.total_count,
                "formula": self.sparks.distribution["formula"],
            },
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_shevirah() -> bool:
    """Validate the Shevirah module."""
    
    # Test WorldState
    assert WorldState.TOHU.hebrew == "תהו"
    assert WorldState.TIKKUN.translation == "Rectification"
    
    # Test KlipahType
    assert KlipahType.NOGAH.nature == "Neutral - can be elevated"
    
    # Test OlamHaTohu
    tohu = OlamHaTohu()
    assert tohu.state == WorldState.TOHU
    chars = tohu.characteristics
    assert "lights" in chars
    assert "vessels" in chars
    
    # Test SheviratHaKelim
    breaking = SheviratHaKelim()
    assert breaking.mechanics["sparks_count"] == 288
    assert len(breaking.affected_sefirot["shattered"]) == 7
    
    # Test KlipotSystem
    klipot = KlipotSystem()
    assert len(klipot.four_klipot) == 4
    assert klipot.four_klipot[0]["elevatable"] == True
    
    # Test HolySparks
    sparks = HolySparks()
    assert sparks.total_count == 288
    
    # Test ShevirahSystem
    system = ShevirahSystem()
    
    analysis = system.analyze_failure()
    assert "failure_causes" in analysis
    
    status = system.get_extraction_status(144)
    assert status["remaining"] == 144
    assert status["tikkun_status"] == "In Progress"
    
    complete = system.get_extraction_status(288)
    assert complete["tikkun_status"] == "Complete"
    
    summary = system.get_summary()
    assert summary["sparks"]["total"] == 288
    
    return True


if __name__ == "__main__":
    print("Validating Shevirah Module...")
    assert validate_shevirah()
    print("✓ Shevirah module validated")
    
    # Demo
    print("\n--- Shevirah (Breaking of Vessels) Demo ---")
    
    system = ShevirahSystem()
    
    print(f"\nOlam HaTohu ({system.tohu.hebrew}):")
    print(f"  State: {system.tohu.state.name}")
    for cause, desc in system.tohu.failure_analysis.items():
        print(f"  - {cause}: {desc}")
    
    print(f"\nShevirat HaKelim ({system.breaking.hebrew}):")
    print(f"  Sparks scattered: {system.breaking.mechanics['sparks_count']}")
    print(f"  Formula: {system.breaking.mechanics['sparks_formula']}")
    
    print("\nThe Four Klipot:")
    for k in system.klipot.four_klipot:
        elevate = "✓" if k["elevatable"] else "✗"
        print(f"  {k['name']} ({k['hebrew']}) - Elevatable: {elevate}")
    
    print("\nExtraction Status (144 extracted):")
    status = system.get_extraction_status(144)
    print(f"  Progress: {status['percentage_complete']}")
    print(f"  Status: {status['tikkun_status']}")
