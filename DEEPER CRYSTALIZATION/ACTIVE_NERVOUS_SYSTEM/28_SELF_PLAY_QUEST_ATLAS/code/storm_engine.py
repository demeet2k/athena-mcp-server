#!/usr/bin/env python3
"""
StormEngine.v1 — PhiStorm Spawn, Priority, and Duration

Manages storm lifecycle from pheromone trigger through
pool allocation and difficulty boosting.
"""

from typing import List, Optional

from .constants import (
    STORM_SEED, STORM_TRIGGER, SHADOW_CUTOFF,
    STORM_BASE_DURATION, STORM_POOL_BASE, STORM_POOL_SCALE,
    STORM_COALITION_BONUS, PHI_INV, PHI_INV3,
)
from .types import (
    PhiStorm, PheromoneField, StormState, Vec4, Epoch, Ptr,
)
from .pheromone_engine import check_storm_trigger, compute_pulse


# ═══════════════════════════════════════════════════════════════
# STORM SPAWN
# ═══════════════════════════════════════════════════════════════

def try_spawn_storm(
    field: PheromoneField,
    current_epoch: Epoch,
    storm_id: str = "",
) -> Optional[PhiStorm]:
    """
    Attempt to spawn a PhiStorm from the pheromone field.
    Returns None if trigger conditions not met.
    """
    if not check_storm_trigger(field):
        return None

    pulse = compute_pulse(field)
    pool = compute_storm_pool(pulse)
    duration = compute_storm_duration(pulse)
    difficulty = compute_difficulty_boost(field)

    return PhiStorm(
        storm_id=storm_id or f"storm_{current_epoch}",
        anchor_addr=field.anchor_addr,
        coord12=field.coord12,
        source_field_id=field.field_id,
        trigger_epoch=current_epoch,
        end_epoch=current_epoch + duration,
        threshold_pos=STORM_TRIGGER,
        threshold_shadow=SHADOW_CUTOFF,
        event_pool=pool,
        difficulty_boost=difficulty,
        active=True,
    )


# ═══════════════════════════════════════════════════════════════
# POOL / DURATION / DIFFICULTY
# ═══════════════════════════════════════════════════════════════

def compute_storm_pool(pulse: float) -> float:
    """
    event_pool = STORM_POOL_BASE + STORM_POOL_SCALE * (pulse / STORM_TRIGGER)
    Clamped to [STORM_POOL_BASE, STORM_POOL_BASE + STORM_POOL_SCALE].
    """
    ratio = max(0.0, min(1.0, pulse / STORM_TRIGGER))
    return STORM_POOL_BASE + STORM_POOL_SCALE * ratio


def compute_storm_duration(pulse: float) -> int:
    """
    Duration scales with pulse intensity.
    Base = 5 epochs, +1 per 21 pulse above threshold.
    """
    extra = max(0, int((pulse - STORM_TRIGGER) / STORM_SEED))
    return STORM_BASE_DURATION + extra


def compute_difficulty_boost(field: PheromoneField) -> float:
    """
    Difficulty boost = φ⁻³ * (positive_norm / STORM_TRIGGER).
    Caps at φ⁻¹.
    """
    pos = field.positive.norm1() if field.positive else 0.0
    raw = PHI_INV3 * (pos / STORM_TRIGGER) if STORM_TRIGGER > 0 else 0.0
    return min(raw, PHI_INV)


# ═══════════════════════════════════════════════════════════════
# STORM LIFECYCLE
# ═══════════════════════════════════════════════════════════════

def advance_storm(storm: PhiStorm, current_epoch: Epoch) -> PhiStorm:
    """Advance storm state based on current epoch."""
    if not storm.active:
        return storm

    if current_epoch >= storm.end_epoch:
        storm.active = False

    return storm


def coalition_bonus(party_size: int) -> float:
    """
    Coalition bonus multiplier for storm quests.
    bonus = 1.0 + STORM_COALITION_BONUS * (party_size - 1)
    """
    if party_size <= 1:
        return 1.0
    return 1.0 + STORM_COALITION_BONUS * (party_size - 1)
