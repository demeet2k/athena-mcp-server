#!/usr/bin/env python3
"""
SeatElection.v1 — Host/Steward Seat Election

Deterministic election of quest hosts and stewards
with quarantine guards and capability matching.
"""

from typing import Dict, List, Optional, Tuple

from .constants import PHI, PHI_INV, PHI_INV2, PHI_INV3
from .types import AgentProfile, Candidate, BoardEntry, QueueName


# ═══════════════════════════════════════════════════════════════
# ELECTION
# ═══════════════════════════════════════════════════════════════

def elect_host(
    entry: BoardEntry,
    agents: List[AgentProfile],
) -> Optional[AgentProfile]:
    """
    Elect the best host for a board entry.
    Quarantined agents are excluded.
    Score = rank + replay_quality + reciprocity - ambig_penalty.
    """
    eligible = [a for a in agents if not a.quarantine_active]
    if not eligible:
        return None

    scored = []
    for a in eligible:
        s = _host_score(a, entry)
        scored.append((s, a))

    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[0][1]


def elect_steward(
    entry: BoardEntry,
    agents: List[AgentProfile],
    host: Optional[AgentProfile] = None,
) -> Optional[AgentProfile]:
    """
    Elect a steward (verifier/witness role) for a board entry.
    Must differ from host. Prioritizes temple_seal and replay_quality.
    """
    eligible = [
        a for a in agents
        if not a.quarantine_active and (host is None or a.agent_id != host.agent_id)
    ]
    if not eligible:
        return None

    scored = []
    for a in eligible:
        s = _steward_score(a, entry)
        scored.append((s, a))

    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[0][1]


# ═══════════════════════════════════════════════════════════════
# SCORING
# ═══════════════════════════════════════════════════════════════

def _host_score(agent: AgentProfile, entry: BoardEntry) -> float:
    """
    Score per SeatElectionPolicy.json:
    sealed_count * φ⁻² + crown_count * φ + witness_count * φ⁻³ + storm_participation * φ⁻¹
    Plus element alignment and ambiguity penalty as supplementary factors.
    """
    # Policy-defined scoring components
    score = (
        agent.sealed_count * PHI_INV2           # 0.382
        + agent.crown_count * PHI               # 1.618
        + agent.witness_count * PHI_INV3        # 0.236
        + agent.storm_participation * PHI_INV   # 0.618
    )

    # Supplementary: element alignment bonus
    if agent.element_bias and entry.candidate.elemental_signature:
        score += agent.element_bias.dot(entry.candidate.elemental_signature) * PHI_INV3

    # Supplementary: ambiguity penalty
    score -= agent.unresolved_critical_ambig * PHI_INV2

    return score


def _steward_score(agent: AgentProfile, entry: BoardEntry) -> float:
    """
    Score per SeatElectionPolicy.json:
    sealed_count * φ⁻³ + temple_count * φ + dispute_resolution * 1.0 + policy_contributions * φ⁻¹
    """
    return (
        agent.sealed_count * PHI_INV3           # 0.236
        + agent.temple_count * PHI              # 1.618
        + agent.dispute_resolution * 1.0        # 1.0
        + agent.policy_contributions * PHI_INV  # 0.618
    )


# ═══════════════════════════════════════════════════════════════
# BATCH ELECTION
# ═══════════════════════════════════════════════════════════════

def elect_seats(
    entries: List[BoardEntry],
    agents: List[AgentProfile],
) -> List[Tuple[BoardEntry, Optional[AgentProfile], Optional[AgentProfile]]]:
    """
    Elect host + steward pairs for a list of board entries.
    Returns list of (entry, host, steward) triples.
    """
    results = []
    for entry in entries:
        host = elect_host(entry, agents)
        steward = elect_steward(entry, agents, host)
        results.append((entry, host, steward))
    return results
