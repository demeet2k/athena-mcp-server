#!/usr/bin/env python3
"""
StationAtlas.v1 — 19-Station Quest Atlas Definitions

Each station defines its element vector, quest classes, payout matrix,
and unlock requirements for the 3 alchemical passes.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .constants import (
    PHI, PHI_INV, PHI_INV2, PHI_INV3, PHI_INV4, PHI_INV5,
    STATION_COUNT, PASS_COUNT, BASE_XP_UNIT,
    PASS_TRANSFORMS, UNLOCK_LADDER,
)
from .types import Element4, Pass3, QuestClass, Vec4


# ═══════════════════════════════════════════════════════════════
# STATION DEFINITION
# ═══════════════════════════════════════════════════════════════

@dataclass
class StationDef:
    """Definition of a single quest atlas station."""
    number: int                  # 1–19
    name: str
    element_vector: Vec4         # primary elemental weight
    quest_classes: List[str]     # allowed quest classes
    unlock_level: int            # minimum level to access
    description: str = ""
    payout_base: float = 1.0     # base payout multiplier
    tags: List[str] = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════
# 19 STATION DEFINITIONS (S01–S19)
# ═══════════════════════════════════════════════════════════════

STATIONS: Dict[int, StationDef] = {
    1: StationDef(
        number=1, name="Genesis Spark",
        element_vector=Vec4(fire=PHI, air=0.0, water=0.0, earth=0.0),
        quest_classes=["Solo"],
        unlock_level=1, payout_base=1.0,
        description="First ignition. Solo seed quests only.",
        tags=["genesis", "fire"],
    ),
    2: StationDef(
        number=2, name="Foundation Stone",
        element_vector=Vec4(fire=0.0, air=0.0, water=0.0, earth=PHI),
        quest_classes=["Solo"],
        unlock_level=1, payout_base=1.0,
        description="Grounding layer. Earth-dominant solo work.",
        tags=["foundation", "earth"],
    ),
    3: StationDef(
        number=3, name="First Breath",
        element_vector=Vec4(fire=0.0, air=PHI, water=0.0, earth=0.0),
        quest_classes=["Solo", "Community"],
        unlock_level=3, payout_base=PHI_INV,
        description="Air opens. Guild Hall board access unlocked.",
        tags=["breath", "air", "guild"],
    ),
    4: StationDef(
        number=4, name="Mirror Pool",
        element_vector=Vec4(fire=0.0, air=0.0, water=PHI, earth=0.0),
        quest_classes=["Solo", "Community"],
        unlock_level=3, payout_base=PHI_INV,
        description="Reflection begins. Water-dominant introspection.",
        tags=["mirror", "water"],
    ),
    5: StationDef(
        number=5, name="Cross Bridge",
        element_vector=Vec4(fire=PHI_INV, air=PHI_INV, water=0.0, earth=0.0),
        quest_classes=["Solo", "Community"],
        unlock_level=5, payout_base=PHI_INV2,
        description="Fire-Air bridge. Community quests unlock.",
        tags=["bridge", "fire-air"],
    ),
    6: StationDef(
        number=6, name="Deep Root",
        element_vector=Vec4(fire=0.0, air=0.0, water=PHI_INV, earth=PHI_INV),
        quest_classes=["Solo", "Community"],
        unlock_level=5, payout_base=PHI_INV2,
        description="Water-Earth bridge. Deep structural work.",
        tags=["root", "water-earth"],
    ),
    7: StationDef(
        number=7, name="Alchemical Forge",
        element_vector=Vec4(fire=PHI_INV, air=0.0, water=PHI_INV, earth=0.0),
        quest_classes=["Solo", "Community", "Repair"],
        unlock_level=5, payout_base=PHI_INV2,
        description="Fire-Water opposition. Transmutation begins.",
        tags=["forge", "fire-water"],
    ),
    8: StationDef(
        number=8, name="Temple Gate",
        element_vector=Vec4(fire=0.0, air=PHI_INV, water=0.0, earth=PHI_INV),
        quest_classes=["Solo", "TempleRite"],
        unlock_level=8, payout_base=PHI_INV3,
        description="Air-Earth bridge. Temple rites unlock.",
        tags=["temple", "air-earth"],
    ),
    9: StationDef(
        number=9, name="Triple Junction",
        element_vector=Vec4(fire=PHI_INV2, air=PHI_INV2, water=PHI_INV2, earth=0.0),
        quest_classes=["Solo", "Community", "Event"],
        unlock_level=8, payout_base=PHI_INV3,
        description="Three-element chamber. Event quests appear.",
        tags=["junction", "chamber"],
    ),
    10: StationDef(
        number=10, name="Shadow Well",
        element_vector=Vec4(fire=0.0, air=PHI_INV2, water=PHI_INV2, earth=PHI_INV2),
        quest_classes=["Solo", "Community", "Repair"],
        unlock_level=8, payout_base=PHI_INV3,
        description="Three-element shadow chamber. Repair quests deepen.",
        tags=["shadow", "chamber", "repair"],
    ),
    11: StationDef(
        number=11, name="Crown Approach",
        element_vector=Vec4(fire=PHI_INV2, air=0.0, water=PHI_INV2, earth=PHI_INV2),
        quest_classes=["Solo", "Community", "TempleRite"],
        unlock_level=13, payout_base=PHI_INV3,
        description="Three-element ascent. Storm participation unlocks.",
        tags=["crown", "chamber"],
    ),
    12: StationDef(
        number=12, name="Storm Threshold",
        element_vector=Vec4(fire=PHI_INV2, air=PHI_INV2, water=0.0, earth=PHI_INV2),
        quest_classes=["Solo", "Community", "Event"],
        unlock_level=13, payout_base=PHI_INV3,
        description="Three-element storm gate. PhiStorm participation.",
        tags=["storm", "chamber"],
    ),
    13: StationDef(
        number=13, name="PhiStorm Eye",
        element_vector=Vec4(fire=PHI_INV3, air=PHI_INV3, water=PHI_INV3, earth=PHI_INV3),
        quest_classes=["Solo", "Community", "Event", "Convergence"],
        unlock_level=13, payout_base=PHI_INV4,
        description="Crown: all four elements. Convergence quests appear.",
        tags=["crown", "storm", "convergence"],
    ),
    14: StationDef(
        number=14, name="Certification Hall",
        element_vector=Vec4(fire=0.0, air=PHI_INV, water=PHI_INV2, earth=PHI_INV),
        quest_classes=["Solo", "TempleRite", "Repair"],
        unlock_level=13, payout_base=PHI_INV4,
        description="Temple certification. Deep verification work.",
        tags=["certification", "temple"],
    ),
    15: StationDef(
        number=15, name="Resonance Chamber",
        element_vector=Vec4(fire=PHI_INV2, air=PHI_INV, water=PHI_INV, earth=0.0),
        quest_classes=["Solo", "Community", "TempleRite", "Event"],
        unlock_level=21, payout_base=PHI_INV4,
        description="Harmonic chamber. Publish-candidate quests unlock.",
        tags=["resonance", "publish"],
    ),
    16: StationDef(
        number=16, name="Publish Gate",
        element_vector=Vec4(fire=PHI_INV, air=PHI_INV2, water=0.0, earth=PHI_INV2),
        quest_classes=["Solo", "Publish", "TempleRite"],
        unlock_level=21, payout_base=PHI_INV4,
        description="Publication corridor. Publish quests activate.",
        tags=["publish", "gate"],
    ),
    17: StationDef(
        number=17, name="Seeding Ground",
        element_vector=Vec4(fire=PHI_INV3, air=PHI_INV3, water=PHI_INV3, earth=PHI_INV3),
        quest_classes=["Solo", "Community", "Event", "Convergence", "Publish"],
        unlock_level=34, payout_base=PHI_INV5,
        description="Crown: storm seeding rights. Full quest palette.",
        tags=["seeding", "crown"],
    ),
    18: StationDef(
        number=18, name="Policy Forum",
        element_vector=Vec4(fire=0.0, air=PHI, water=0.0, earth=PHI_INV),
        quest_classes=["Solo", "Community", "Convergence", "TempleRite"],
        unlock_level=55, payout_base=PHI_INV5,
        description="Governance station. Policy proposal rights.",
        tags=["policy", "governance"],
    ),
    19: StationDef(
        number=19, name="Migration Council",
        element_vector=Vec4(fire=PHI_INV4, air=PHI_INV4, water=PHI_INV4, earth=PHI_INV4),
        quest_classes=["Solo", "Community", "Convergence", "TempleRite", "Publish"],
        unlock_level=89, payout_base=PHI_INV5,
        description="Crown: migration review council. Full orbit mastery.",
        tags=["migration", "council", "crown"],
    ),
}


# ═══════════════════════════════════════════════════════════════
# PAYOUT MATRIX
# ═══════════════════════════════════════════════════════════════

def compute_station_payout(station: int, pass3: Pass3) -> Vec4:
    """
    Compute the elemental payout vector for a station+pass combination.

    payout_e = base_xp * station.payout_base * station.element_vector_e
               * pass_transform.d[e] * pass_transform.chi
    """
    sdef = STATIONS[station]
    pt = PASS_TRANSFORMS[pass3.value]
    chi = pt["chi"]
    d = pt["d"]  # (Fire, Air, Water, Earth) multipliers
    ev = sdef.element_vector

    return Vec4(
        fire=BASE_XP_UNIT * sdef.payout_base * ev.fire * d[0] * chi,
        air=BASE_XP_UNIT * sdef.payout_base * ev.air * d[1] * chi,
        water=BASE_XP_UNIT * sdef.payout_base * ev.water * d[2] * chi,
        earth=BASE_XP_UNIT * sdef.payout_base * ev.earth * d[3] * chi,
    )


def compute_full_payout_matrix() -> Dict[Tuple[int, str], Vec4]:
    """Compute payout vectors for all 57 station×pass combinations."""
    matrix = {}
    for s in range(1, STATION_COUNT + 1):
        for p in Pass3:
            matrix[(s, p.value)] = compute_station_payout(s, p)
    return matrix


# ═══════════════════════════════════════════════════════════════
# LOOKUPS
# ═══════════════════════════════════════════════════════════════

def station_for_loop(loop_index: int) -> Tuple[int, Pass3]:
    """
    Convert a 0-based loop index (0–56) to (station, pass).
    Loop 0 = Station 1 Sulfur, Loop 1 = Station 1 Mercury, etc.
    """
    station = (loop_index // PASS_COUNT) + 1
    pass_idx = loop_index % PASS_COUNT
    return station, list(Pass3)[pass_idx]


def loop_for_station(station: int, pass3: Pass3) -> int:
    """Convert (station, pass) to a 0-based loop index."""
    return (station - 1) * PASS_COUNT + list(Pass3).index(pass3)


def accessible_stations(level: int) -> List[int]:
    """Return list of station numbers accessible at the given level."""
    return [s for s, sdef in STATIONS.items() if sdef.unlock_level <= level]


def station_quest_classes(station: int) -> List[str]:
    """Return quest classes available at the given station."""
    return list(STATIONS[station].quest_classes)
