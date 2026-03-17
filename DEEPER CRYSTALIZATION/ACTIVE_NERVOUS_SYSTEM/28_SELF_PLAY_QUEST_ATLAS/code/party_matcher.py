#!/usr/bin/env python3
"""
PartyMatcher.v1 — Party Matching for Community Quests

Complementarity scoring, rights fit, and recruit fallback.
"""

from typing import Dict, List, Optional, Tuple

from .constants import PHI_INV, PHI_INV2
from .types import AgentProfile, CommunityQuest, Vec4


# ═══════════════════════════════════════════════════════════════
# COMPLEMENTARITY
# ═══════════════════════════════════════════════════════════════

def complementarity(a: AgentProfile, b: AgentProfile) -> float:
    """
    Measure how complementary two agents are.
    High when element biases cover different elements.
    """
    if not a.element_bias or not b.element_bias:
        return 0.0

    av = a.element_bias.normalized()
    bv = b.element_bias.normalized()

    # Coverage = norm1 of sum (higher when covering different elements)
    combined = Vec4(
        fire=max(av.fire, bv.fire),
        air=max(av.air, bv.air),
        water=max(av.water, bv.water),
        earth=max(av.earth, bv.earth),
    )
    coverage = combined.norm1()

    # Overlap penalty (lower when different)
    overlap = av.dot(bv)

    return coverage - overlap * PHI_INV


def diversity_score(party: List[AgentProfile]) -> float:
    """Average pairwise complementarity of a party."""
    if len(party) < 2:
        return 0.0
    total = 0.0
    count = 0
    for i in range(len(party)):
        for j in range(i + 1, len(party)):
            total += complementarity(party[i], party[j])
            count += 1
    return total / count if count > 0 else 0.0


# ═══════════════════════════════════════════════════════════════
# RIGHTS FIT
# ═══════════════════════════════════════════════════════════════

def rights_fit(agent: AgentProfile, quest: CommunityQuest) -> bool:
    """Check if an agent meets quest rights requirements."""
    if agent.quarantine_active:
        return False
    if agent.guild_rank < quest.level_requirement:
        return False
    return True


# ═══════════════════════════════════════════════════════════════
# PARTY ASSEMBLY
# ═══════════════════════════════════════════════════════════════

def assemble_party(
    quest: CommunityQuest,
    candidates: List[AgentProfile],
    prefer_diversity: bool = True,
) -> List[AgentProfile]:
    """
    Assemble the best party for a community quest.
    Greedy: start with highest-scored agent, add most complementary.
    Falls back to recruit pool if not enough eligible.
    """
    eligible = [a for a in candidates if rights_fit(a, quest)]
    if len(eligible) < quest.min_party:
        return []  # insufficient — needs recruit fallback

    # Sort by guild_rank + replay_quality as baseline
    eligible.sort(
        key=lambda a: a.guild_rank + a.replay_quality,
        reverse=True,
    )

    party = [eligible[0]]
    remaining = eligible[1:]

    while len(party) < quest.max_party and remaining:
        if prefer_diversity:
            # Pick most complementary to current party
            best_idx = 0
            best_comp = -1.0
            for i, agent in enumerate(remaining):
                comp = sum(complementarity(agent, p) for p in party) / len(party)
                if comp > best_comp:
                    best_comp = comp
                    best_idx = i
            party.append(remaining.pop(best_idx))
        else:
            party.append(remaining.pop(0))

    return party


def check_quorum(party: List[AgentProfile], quest: CommunityQuest) -> bool:
    """Check if the party meets quorum."""
    return len(party) >= quest.quorum
