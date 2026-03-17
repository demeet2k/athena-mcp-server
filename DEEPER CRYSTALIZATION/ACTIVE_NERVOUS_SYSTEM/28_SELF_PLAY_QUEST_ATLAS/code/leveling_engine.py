#!/usr/bin/env python3
"""
LevelingEngine.v1 — Infinite-Cap Levels and Orbit Decomposition

Level = 57k + ℓ where k = orbit number, ℓ = position in orbit (0–56).
Amplifier law scales rewards with phi-weighted level progression.
"""

import math
from typing import Tuple

from .constants import (
    ORBIT_SIZE, STATION_COUNT, PASS_COUNT, PHI, PHI_INV,
    BASE_XP_UNIT, UNLOCK_LADDER,
)


# ═══════════════════════════════════════════════════════════════
# ORBIT DECOMPOSITION
# ═══════════════════════════════════════════════════════════════

def decompose_level(level: int) -> Tuple[int, int]:
    """
    Decompose level into (orbit_number, position_in_orbit).
    level = 57 * orbit + position
    Requires level >= 0.
    """
    if level < 0:
        raise ValueError(f"level must be >= 0, got {level}")
    orbit = level // ORBIT_SIZE
    position = level % ORBIT_SIZE
    return orbit, position


def compose_level(orbit: int, position: int) -> int:
    """Compose level from orbit number and position."""
    return orbit * ORBIT_SIZE + position


def level_to_station_pass(level: int) -> Tuple[int, int, int]:
    """
    Convert level to (orbit, station, pass_index).
    station: 1–19, pass_index: 0–2.
    """
    orbit, pos = decompose_level(level)
    station = (pos // PASS_COUNT) + 1
    pass_idx = pos % PASS_COUNT
    return orbit, station, pass_idx


# ═══════════════════════════════════════════════════════════════
# XP THRESHOLDS
# ═══════════════════════════════════════════════════════════════

def xp_for_level(level: int) -> float:
    """
    XP required to reach the given level.
    Uses phi-scaled Fibonacci-like growth:
    xp(n) = BASE_XP_UNIT * φ^(n/19)

    This ensures each orbit requires roughly φ× the XP of the previous.
    """
    return BASE_XP_UNIT * (PHI ** (level / STATION_COUNT))


def cumulative_xp(level: int) -> float:
    """
    Total XP required from level 0 to the target level.
    Sum of xp_for_level(0) through xp_for_level(level-1).
    """
    total = 0.0
    for i in range(level):
        total += xp_for_level(i)
    return total


def level_from_xp(total_xp: float) -> int:
    """
    Determine the level achieved from cumulative XP.
    Returns the highest level whose cumulative threshold is met.
    """
    level = 0
    accumulated = 0.0
    while True:
        threshold = xp_for_level(level)
        if accumulated + threshold > total_xp:
            break
        accumulated += threshold
        level += 1
    return level


# ═══════════════════════════════════════════════════════════════
# AMPLIFIER LAW
# ═══════════════════════════════════════════════════════════════

def amplifier(level: int) -> float:
    """
    Level-based reward amplifier.
    amp = 1 + φ⁻¹ * log_φ(1 + level)

    Grows sub-linearly: experienced agents earn more,
    but never exponentially more.
    """
    if level <= 0:
        return 1.0
    log_phi = math.log(1 + level) / math.log(PHI)
    return 1.0 + PHI_INV * log_phi


# ═══════════════════════════════════════════════════════════════
# UNLOCK CHECKS
# ═══════════════════════════════════════════════════════════════

def unlocked_rights(level: int) -> list:
    """Return list of (threshold, right_name) pairs unlocked at the given level."""
    return [
        (thresh, name)
        for thresh, name in sorted(UNLOCK_LADDER.items())
        if level >= thresh
    ]


def highest_unlock(level: int) -> str:
    """Return the name of the highest right unlocked."""
    rights = unlocked_rights(level)
    if not rights:
        return "none"
    return rights[-1][1]
