#!/usr/bin/env python3
"""
PheromoneEngine.v1 — 4+4 Channel Pheromone Field

Deposit law, φ⁻¹ golden-memory decay, storm triggering,
and magnetic quest routing.
"""

from typing import Dict, List, Optional, Tuple

from .constants import (
    PHI_INV, PHEROMONE_DECAY, PHEROMONE_KAPPA,
    STORM_TRIGGER, SHADOW_CUTOFF,
    MAGNET_PROFILE_WEIGHT, MAGNET_POSITIVE_WEIGHT,
    MAGNET_SHADOW_WEIGHT, MAGNET_UNFINISHED_WEIGHT,
    MAGNET_PULSE_WEIGHT,
)
from .types import (
    Vec4, PheromoneField, AgentProfile, Element4, Epoch,
)


# ═══════════════════════════════════════════════════════════════
# DEPOSIT
# ═══════════════════════════════════════════════════════════════

def deposit_positive(field: PheromoneField, delta: Vec4, kappa: float = PHEROMONE_KAPPA) -> PheromoneField:
    """
    Deposit positive pheromone into a field.
    Each channel: p_e += kappa * delta_e
    """
    if field.positive is None:
        field.positive = Vec4()
    field.positive = Vec4(
        fire=field.positive.fire + kappa * delta.fire,
        air=field.positive.air + kappa * delta.air,
        water=field.positive.water + kappa * delta.water,
        earth=field.positive.earth + kappa * delta.earth,
    )
    return field


def deposit_shadow(field: PheromoneField, delta: Vec4, kappa: float = PHEROMONE_KAPPA) -> PheromoneField:
    """
    Deposit shadow pheromone (failure/ambiguity traces).
    Each channel: s_e += kappa * delta_e
    """
    if field.shadow is None:
        field.shadow = Vec4()
    field.shadow = Vec4(
        fire=field.shadow.fire + kappa * delta.fire,
        air=field.shadow.air + kappa * delta.air,
        water=field.shadow.water + kappa * delta.water,
        earth=field.shadow.earth + kappa * delta.earth,
    )
    return field


# ═══════════════════════════════════════════════════════════════
# DECAY
# ═══════════════════════════════════════════════════════════════

def decay_field(field: PheromoneField, current_epoch: Epoch) -> PheromoneField:
    """
    Apply golden-memory decay: p_e *= φ⁻¹ per elapsed epoch.
    """
    elapsed = max(0, current_epoch - field.last_epoch)
    if elapsed == 0:
        return field

    decay_factor = PHEROMONE_DECAY ** elapsed

    if field.positive:
        field.positive = Vec4(
            fire=field.positive.fire * decay_factor,
            air=field.positive.air * decay_factor,
            water=field.positive.water * decay_factor,
            earth=field.positive.earth * decay_factor,
        )

    if field.shadow:
        field.shadow = Vec4(
            fire=field.shadow.fire * decay_factor,
            air=field.shadow.air * decay_factor,
            water=field.shadow.water * decay_factor,
            earth=field.shadow.earth * decay_factor,
        )

    field.last_epoch = current_epoch
    return field


# ═══════════════════════════════════════════════════════════════
# STORM DETECTION
# ═══════════════════════════════════════════════════════════════

def check_storm_trigger(field: PheromoneField) -> bool:
    """
    Storm triggers when positive norm1 ≥ STORM_TRIGGER (34)
    AND shadow norm1 ≤ SHADOW_CUTOFF (13).
    """
    pos_total = field.positive.norm1() if field.positive else 0.0
    shadow_total = field.shadow.norm1() if field.shadow else 0.0
    return pos_total >= STORM_TRIGGER and shadow_total <= SHADOW_CUTOFF


def compute_pulse(field: PheromoneField) -> float:
    """
    Pulse score = positive_norm - shadow_norm.
    Negative pulse = area needs repair attention.
    """
    pos = field.positive.norm1() if field.positive else 0.0
    shd = field.shadow.norm1() if field.shadow else 0.0
    return pos - shd


# ═══════════════════════════════════════════════════════════════
# MAGNETIC ROUTING
# ═══════════════════════════════════════════════════════════════

def magnetic_score(
    field: PheromoneField,
    agent: AgentProfile,
    unfinished_count: int = 0,
) -> float:
    """
    Compute magnetic attraction score for an agent to a pheromone field.

    score = w_profile * profile_alignment
          + w_positive * positive_alignment
          - w_shadow * shadow_alignment
          - w_unfinished * unfinished_count
          + w_pulse * pulse

    Higher score = stronger routing recommendation.
    """
    profile_alignment = 0.0
    if agent.element_bias and field.positive:
        profile_alignment = agent.element_bias.dot(field.positive.normalized())

    positive_alignment = field.positive.norm1() if field.positive else 0.0
    shadow_alignment = field.shadow.norm1() if field.shadow else 0.0
    pulse = compute_pulse(field)

    return (
        MAGNET_PROFILE_WEIGHT * profile_alignment
        + MAGNET_POSITIVE_WEIGHT * positive_alignment
        - MAGNET_SHADOW_WEIGHT * shadow_alignment
        - MAGNET_UNFINISHED_WEIGHT * unfinished_count
        + MAGNET_PULSE_WEIGHT * pulse
    )


def rank_fields(
    fields: List[PheromoneField],
    agent: AgentProfile,
    unfinished_counts: Optional[Dict[str, int]] = None,
) -> List[Tuple[float, PheromoneField]]:
    """
    Rank pheromone fields by magnetic score for an agent.
    Returns sorted list of (score, field), highest first.
    """
    if unfinished_counts is None:
        unfinished_counts = {}

    scored = []
    for f in fields:
        uc = unfinished_counts.get(f.field_id, 0)
        s = magnetic_score(f, agent, uc)
        scored.append((s, f))

    scored.sort(key=lambda x: x[0], reverse=True)
    return scored
