#!/usr/bin/env python3
"""
RewardEngine.v1 — Full Settlement Engine

Truth gate, quality law, contribution split, community multiplier,
per-capsule and per-epoch clamps. Produces PoPhiXCapsules.
"""

from typing import Dict, List, Optional

from .constants import (
    PHI, PHI_INV, PHI_INV2,
    BASE_XP_UNIT, BASE_EPOCH_REWARD,
    GAMMA_OK, GAMMA_NEAR, GAMMA_ZERO,
    GUILD_LAMBDA, TEMPLE_LAMBDA, DIFFICULTY_DELTA,
    COMMUNITY_BETA, CAPSULE_CLAMP, EPOCH_CLAMP,
    RESONANCE_RATIO, MINT_RATES, NEAR_VEST_RATIO,
)
from .types import (
    Truth4, QuestClass, Vec4, Quest,
    PoPhiXCapsule, VestingVault, VaultState,
    AgentID, Epoch, Ptr,
)
from .leveling_engine import amplifier


# ═══════════════════════════════════════════════════════════════
# TRUTH GATE
# ═══════════════════════════════════════════════════════════════

def truth_gate(truth: Truth4) -> float:
    """Map truth state to reward multiplier (γ)."""
    if truth == Truth4.OK:
        return GAMMA_OK
    if truth == Truth4.NEAR:
        return GAMMA_NEAR
    return GAMMA_ZERO  # AMBIG, FAIL


# ═══════════════════════════════════════════════════════════════
# QUALITY LAW
# ═══════════════════════════════════════════════════════════════

def quality_score(elemental: Vec4, pass_weights: tuple) -> float:
    """
    Quality = dot(elemental, pass_weights) normalized.
    pass_weights = (d_F, d_A, d_W, d_E) from PASS_TRANSFORMS.
    """
    raw = (
        elemental.fire * pass_weights[0]
        + elemental.air * pass_weights[1]
        + elemental.water * pass_weights[2]
        + elemental.earth * pass_weights[3]
    )
    return max(0.0, min(1.0, raw))


# ═══════════════════════════════════════════════════════════════
# SETTLEMENT
# ═══════════════════════════════════════════════════════════════

def settle_quest(
    quest: Quest,
    participants: List[AgentID],
    contribution_weights: Dict[AgentID, float],
    participant_levels: Dict[AgentID, int],
    truth: Truth4,
    elemental_quality: Vec4,
    current_epoch: Epoch,
    pass_weights: tuple = (1.0, 1.0, 1.0, 1.0),
) -> PoPhiXCapsule:
    """
    Full reward settlement for a completed quest.

    XP per agent per element:
      xp_e = BASE_XP * γ * quality * contribution * amplifier * difficulty * community

    Resonance:
      resonance = RESONANCE_RATIO * sum(xp_e)

    Mint:
      mint = MINT_RATE[class] * sum(xp_e)

    NEAR → partial XP released, rest goes to VestingVault.
    """
    gamma = truth_gate(truth)
    q = quality_score(elemental_quality, pass_weights)
    difficulty = 1.0 + DIFFICULTY_DELTA * quest.station19

    # Community multiplier
    community = 1.0
    if quest.quest_class in (QuestClass.COMMUNITY, QuestClass.CONVERGENCE):
        community = 1.0 + COMMUNITY_BETA * max(0, len(participants) - 1)

    # Mint rate
    mint_rate = MINT_RATES.get(quest.quest_class.value, 0.0)

    settled_xp: Dict[AgentID, Vec4] = {}
    settled_resonance: Dict[AgentID, float] = {}
    settled_mint: Dict[AgentID, float] = {}
    settled_vesting: Dict[AgentID, Ptr] = {}

    for agent in participants:
        w = contribution_weights.get(agent, 1.0 / max(1, len(participants)))
        amp = amplifier(participant_levels.get(agent, 0))

        xp_fire = BASE_XP_UNIT * gamma * q * w * amp * difficulty * community * elemental_quality.fire
        xp_air = BASE_XP_UNIT * gamma * q * w * amp * difficulty * community * elemental_quality.air
        xp_water = BASE_XP_UNIT * gamma * q * w * amp * difficulty * community * elemental_quality.water
        xp_earth = BASE_XP_UNIT * gamma * q * w * amp * difficulty * community * elemental_quality.earth

        xp_vec = Vec4(fire=xp_fire, air=xp_air, water=xp_water, earth=xp_earth)

        # Apply per-capsule clamp
        total = xp_vec.norm1()
        if total > CAPSULE_CLAMP * BASE_XP_UNIT:
            scale = (CAPSULE_CLAMP * BASE_XP_UNIT) / total
            xp_vec = Vec4(
                fire=xp_vec.fire * scale,
                air=xp_vec.air * scale,
                water=xp_vec.water * scale,
                earth=xp_vec.earth * scale,
            )
            total = xp_vec.norm1()

        # NEAR vesting: release (1 - NEAR_VEST_RATIO), lock rest
        if truth == Truth4.NEAR:
            released = Vec4(
                fire=xp_vec.fire * (1 - NEAR_VEST_RATIO),
                air=xp_vec.air * (1 - NEAR_VEST_RATIO),
                water=xp_vec.water * (1 - NEAR_VEST_RATIO),
                earth=xp_vec.earth * (1 - NEAR_VEST_RATIO),
            )
            settled_xp[agent] = released
            settled_vesting[agent] = f"vest_{agent}_{current_epoch}"
        else:
            settled_xp[agent] = xp_vec

        settled_resonance[agent] = RESONANCE_RATIO * total
        settled_mint[agent] = mint_rate * total

    return PoPhiXCapsule(
        quest_id=quest.quest_id,
        participants=list(participants),
        contribution_weights=dict(contribution_weights),
        elemental_quality=elemental_quality,
        difficulty_epoch=current_epoch,
        settled_xp=settled_xp,
        settled_resonance=settled_resonance,
        settled_mint=settled_mint,
        settled_vesting=settled_vesting,
    )


# ═══════════════════════════════════════════════════════════════
# EPOCH CLAMP
# ═══════════════════════════════════════════════════════════════

def clamp_epoch_rewards(
    capsules: List[PoPhiXCapsule],
) -> List[PoPhiXCapsule]:
    """
    Apply per-epoch clamp across all capsules.
    Total XP minted in one epoch ≤ EPOCH_CLAMP * BASE_EPOCH_REWARD.
    """
    max_total = EPOCH_CLAMP * BASE_EPOCH_REWARD

    # Sum all settled XP
    grand_total = 0.0
    for cap in capsules:
        for xp in cap.settled_xp.values():
            grand_total += xp.norm1()

    if grand_total <= max_total or grand_total == 0:
        return capsules

    scale = max_total / grand_total
    for cap in capsules:
        for agent in cap.settled_xp:
            v = cap.settled_xp[agent]
            cap.settled_xp[agent] = Vec4(
                fire=v.fire * scale,
                air=v.air * scale,
                water=v.water * scale,
                earth=v.earth * scale,
            )
        for agent in cap.settled_resonance:
            cap.settled_resonance[agent] *= scale
        for agent in cap.settled_mint:
            cap.settled_mint[agent] *= scale

    return capsules
