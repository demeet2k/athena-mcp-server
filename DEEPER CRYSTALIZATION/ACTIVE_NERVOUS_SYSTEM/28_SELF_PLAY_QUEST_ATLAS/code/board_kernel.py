#!/usr/bin/env python3
"""
BoardKernel.v1 — Deterministic Board Engine

Scores candidates, assigns to Guild or Temple queues,
and emits orbit-wide board snapshots.
"""

from typing import Dict, List, Tuple

from .constants import (
    STATION_COUNT, PASS_COUNT, ORBIT_SIZE,
    GUILD_LAMBDA, TEMPLE_LAMBDA, DIFFICULTY_DELTA,
    COMMUNITY_BETA, PHI, PHI_INV, PHI_INV2,
)
from .types import (
    Truth4, QuestClass, BoardKind, QueueName, Pass3,
    Candidate, RouteTicket, BoardEntry, Vec4,
    GuildHallBoard, TempleRegistry,
)
from .route_compiler import compile_route
from .station_atlas import STATIONS, station_for_loop


# ═══════════════════════════════════════════════════════════════
# CANDIDATE NORMALIZATION
# ═══════════════════════════════════════════════════════════════

def normalize_candidate(c: Candidate) -> Candidate:
    """Clamp station/pass/orbit to valid ranges."""
    c.station19 = max(1, min(STATION_COUNT, c.station19))
    if c.orbit_index < 0:
        c.orbit_index = 0
    if c.elemental_signature is None:
        sdef = STATIONS.get(c.station19)
        if sdef:
            c.elemental_signature = sdef.element_vector
    return c


# ═══════════════════════════════════════════════════════════════
# SCORING HELPERS (BoardKernelPolicy.json)
# ═══════════════════════════════════════════════════════════════

def pass_decay(p: Pass3) -> float:
    """φ^(-(pass-1)): Sulfur=1.0, Mercury=φ⁻¹, Salt=φ⁻²."""
    return {Pass3.SULFUR: 1.0, Pass3.MERCURY: PHI_INV, Pass3.SALT: PHI_INV2}[p]


def element_coherence(v: Vec4) -> float:
    """
    Element coherence bonus = 1.0 + φ⁻¹ * (1 - normalised variance).
    Maximal (1+φ⁻¹) when all four channels equal; minimal (1.0) when single-element.
    """
    vals = v.as_tuple()
    n = v.norm1()
    if n == 0:
        return 1.0
    normed = tuple(x / n for x in vals)
    mean = 0.25  # normed sums to 1.0, mean = 1/4
    var = sum((x - mean) ** 2 for x in normed) / 4.0
    max_var = 3.0 * mean ** 2  # variance when single-element (0.75, 0.25³ ×3)
    normalised_var = var / max_var if max_var > 0 else 0.0
    return 1.0 + PHI_INV * (1.0 - normalised_var)


# ═══════════════════════════════════════════════════════════════
# SCORING
# ═══════════════════════════════════════════════════════════════

def guild_score(c: Candidate, route: RouteTicket) -> float:
    """
    Guild Hall score per BoardKernelPolicy:
    base × gamma(truth) × difficulty × φ^(-(pass-1)) × coherence × pressure.
    """
    base = 1.0
    truth_w = _truth_weight(route.truth)
    diff = 1.0 + DIFFICULTY_DELTA * c.station19
    pd = pass_decay(c.pass3)
    pressure = sum(c.pressure.values()) if c.pressure else 1.0

    # Element coherence bonus
    coherence = element_coherence(c.elemental_signature) if c.elemental_signature else 1.0

    # Community multiplier
    community_mult = 1.0
    if c.quest_class in ("Community", "Event", "Convergence", "Storm", "Crown"):
        community_mult = 1.0 + COMMUNITY_BETA

    # Guild amplifier
    guild_amp = 1.0 + GUILD_LAMBDA * len(c.target_set)

    return base * truth_w * diff * pd * coherence * pressure * community_mult * guild_amp


def temple_score(c: Candidate, route: RouteTicket) -> float:
    """
    Temple score per BoardKernelPolicy:
    base × gamma(truth) × depth × φ^(-(pass-1)) × coherence.
    """
    base = 1.0
    truth_w = _truth_weight(route.truth)
    depth = 1.0 + 0.1 * len(c.witness_ptrs) + 0.1 * len(c.replay_ptrs)
    pd = pass_decay(c.pass3)

    # Element coherence bonus
    coherence = element_coherence(c.elemental_signature) if c.elemental_signature else 1.0

    # Temple amplifier
    temple_amp = 1.0 + TEMPLE_LAMBDA * len(c.evidence_ptrs)

    return base * truth_w * depth * pd * coherence * temple_amp


def _truth_weight(truth: Truth4) -> float:
    """Map truth state to scoring weight."""
    return {
        Truth4.OK: 1.0,
        Truth4.NEAR: PHI_INV2,
        Truth4.AMBIG: PHI_INV,
        Truth4.FAIL: 0.0,
    }[truth]


# ═══════════════════════════════════════════════════════════════
# QUEUE ASSIGNMENT
# ═══════════════════════════════════════════════════════════════

def assign_guild_queue(c: Candidate, route: RouteTicket) -> QueueName:
    """Assign a candidate to a Guild Hall queue."""
    if route.truth == Truth4.FAIL:
        return QueueName.OVERFLOW

    if c.quest_class == "Repair":
        return QueueName.REPAIR

    if hasattr(route, 'mode') and route.mode == "publish":
        return QueueName.FEATURED

    if c.quest_class in ("Event", "Convergence"):
        return QueueName.STORM

    if c.quest_class == "Community":
        return QueueName.RECRUIT

    return QueueName.LADDER


def assign_temple_queue(c: Candidate, route: RouteTicket) -> QueueName:
    """Assign a candidate to a Temple queue."""
    if route.truth == Truth4.FAIL:
        return QueueName.OVERFLOW

    if route.truth == Truth4.AMBIG:
        return QueueName.AMBIGUITIES

    if route.truth == Truth4.NEAR:
        return QueueName.NEAR_CLOSURE

    if c.quest_class == "TempleRite":
        return QueueName.CERTIFICATION

    if c.quest_class == "Publish":
        return QueueName.SOVEREIGN

    return QueueName.COMPRESSION


# ═══════════════════════════════════════════════════════════════
# BOARD BUILDERS
# ═══════════════════════════════════════════════════════════════

def build_board_entry(c: Candidate, kind: BoardKind) -> BoardEntry:
    """Compile route, score, and assign queue for a single candidate."""
    c = normalize_candidate(c)
    route = compile_route(c)

    if kind == BoardKind.GUILD:
        score = guild_score(c, route)
        queue = assign_guild_queue(c, route)
    else:
        score = temple_score(c, route)
        queue = assign_temple_queue(c, route)

    return BoardEntry(
        candidate=c,
        route=route,
        board_kind=kind,
        score=score,
        queue=queue,
    )


def build_guild_board(candidates: List[Candidate]) -> List[BoardEntry]:
    """Build sorted Guild Hall board from candidates."""
    entries = [build_board_entry(c, BoardKind.GUILD) for c in candidates]
    entries.sort(key=lambda e: e.score, reverse=True)
    return entries


def build_temple_board(candidates: List[Candidate]) -> List[BoardEntry]:
    """Build sorted Temple board from candidates."""
    entries = [build_board_entry(c, BoardKind.TEMPLE) for c in candidates]
    entries.sort(key=lambda e: e.score, reverse=True)
    return entries


# ═══════════════════════════════════════════════════════════════
# ORBIT-WIDE DRIVER
# ═══════════════════════════════════════════════════════════════

def emit_orbit_boards(
    candidates: List[Candidate],
) -> Dict[str, List[BoardEntry]]:
    """
    Emit full orbit boards — one Guild and one Temple board.
    Deterministic: same input → same output.
    """
    guild_candidates = []
    temple_candidates = []

    for c in candidates:
        sdef = STATIONS.get(c.station19)
        if not sdef:
            continue

        classes = sdef.quest_classes
        if c.quest_class in ("TempleRite",):
            temple_candidates.append(c)
        elif c.quest_class in classes:
            guild_candidates.append(c)
        else:
            guild_candidates.append(c)

    return {
        "guild": build_guild_board(guild_candidates),
        "temple": build_temple_board(temple_candidates),
    }
