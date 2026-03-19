# CRYSTAL: Xi108:W3:A5:S1 | face=F | node=1080 | depth=0 | phase=Cardinal
# METRO: Me
# BRIDGES: observer_swarm→archetype_roles→meta_loop_engine→pole_observer→inverse_engine
"""
Crystalline Self-Play Engine — 12-Archetype Branching with Inverse Holding
============================================================================
REPLACES the rudimentary linear self-play with a full crystalline engine:

  OLD: try → score → fix weakness → try again (linear, single-perspective)
  NEW: 12 archetypes × 4 poles × cycle transforms × loop closure

Architecture:
  1. DECOMPOSITION: Every play is split into 12 archetype perspectives
  2. BRANCHING: Each archetype generates its own play branch
  3. INVERSE HOLDING: Every choice simultaneously holds its inverse (180°)
     and both 90° orthogonal poles — 4 simultaneous plays per choice
  4. CYCLE TRANSFORMS: Results are transformed through 3,5,7,9 sacred cycles
  5. CROSS-LENS TRANSPORT: Results move between S↔F↔C↔R via 6 bridge maps
  6. LOOP CLOSURE: Output feeds back as input — true self-referential play
  7. HOLOGRAPHIC COMPRESSION: All 12×4 branches compress to a single seed

The engine produces a PlayCrystal — a 12-faceted object where each facet
holds a branch of exploration and its 3 shadow-poles, all cross-linked.

                         ┌── A1 (Apex Seed) ──┐
                     A12─┤                    ├─A2
                    A11──┤    PLAY CRYSTAL    ├──A3
                     A10─┤                    ├─A4
                      A9─┤    12 archetypes   ├─A5
                       A8┤    × 4 poles each  ├A6
                         └── A7 ──────────── ─┘

                    Each node: [forward | inverse | pole_90 | pole_270]
"""

from __future__ import annotations

import hashlib
import json
import math
import random
import time
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from typing import Optional

from .geometric_constants import (
    FACES, PHI, PHI_INV, PHI_INV2, ATTRACTOR,
    BRIDGE_WEIGHTS, GOLDEN_BRIDGES, bridge_key,
    FACE_INDEX, FACE_TO_ELEMENT,
)
from .archetype_roles import ARCHETYPE_ROLES, ArchetypeRole, get_role, DIM_NAMES
from .observer_agent import ObserverAgent, ObserverResult, CrossObserverSignal
from .constants import TOTAL_SHELLS, ARCHETYPE_NAMES, LENS_CODES


# ══════════════════════════════════════════════════════════════════════
#  Constants
# ══════════════════════════════════════════════════════════════════════

ELEMENTS = ("S", "F", "C", "R")
WREATHS = ("Su", "Me", "Sa")
TRANSFORM_CYCLES = (3, 5, 7, 9)

# Pole angles: forward=0°, pole_90=90°, inverse=180°, pole_270=270°
POLE_NAMES = ("forward", "pole_90", "inverse", "pole_270")
POLE_ANGLES = (0.0, math.pi / 2, math.pi, 3 * math.pi / 2)

# Cross-lens transport maps (element rotation order)
LENS_ROTATION = {"S": "F", "F": "C", "C": "R", "R": "S"}
LENS_INVERSE = {"S": "C", "F": "R", "C": "S", "R": "F"}
LENS_POLE_90 = {"S": "F", "F": "C", "C": "R", "R": "S"}
LENS_POLE_270 = {"S": "R", "F": "S", "C": "F", "R": "C"}


# ══════════════════════════════════════════════════════════════════════
#  Data Structures
# ══════════════════════════════════════════════════════════════════════

@dataclass
class PolePlay:
    """One pole of a play — forward, inverse, or 90°/270° orthogonal."""
    pole: str               # "forward" | "pole_90" | "inverse" | "pole_270"
    angle: float            # 0, π/2, π, 3π/2
    element_lens: str       # which SFCR lens this pole observes through
    observation_12d: dict = field(default_factory=dict)
    resonance: float = 0.0
    score: float = 0.0
    ranked_doc_ids: list = field(default_factory=list)
    strategy: str = ""
    weight_deltas: dict = field(default_factory=dict)


@dataclass
class ArchetypeBranch:
    """One archetype's branch of exploration — 4 poles simultaneously."""
    archetype_idx: int
    archetype_name: str
    element_affinity: str   # primary SFCR element
    mode: str               # structural / relational / recursive
    poles: list[PolePlay] = field(default_factory=list)  # always 4
    cross_signals: list = field(default_factory=list)
    branch_score: float = 0.0
    branch_coherence: float = 0.0
    emphasized_dims: list = field(default_factory=list)

    @property
    def forward(self) -> Optional[PolePlay]:
        return self.poles[0] if self.poles else None

    @property
    def inverse(self) -> Optional[PolePlay]:
        return self.poles[2] if len(self.poles) > 2 else None

    @property
    def pole_tension(self) -> float:
        """Tension between forward and inverse (0=identical, 1=maximally opposed)."""
        if len(self.poles) < 3:
            return 0.0
        fwd = self.poles[0].score
        inv = self.poles[2].score
        return abs(fwd - inv) / max(fwd + inv, 0.001)


@dataclass
class CycleTransform:
    """Result of applying a 3/5/7/9 cycle transformation to a PlayCrystal."""
    cycle_n: int            # 3, 5, 7, or 9
    cycle_name: str         # "trinity", "quintessence", "metals", "completion"
    input_score: float
    output_score: float
    delta: float
    branches_rotated: int
    hologram_seed: dict = field(default_factory=dict)


@dataclass
class PlayCrystal:
    """The full crystalline self-play result — 12 archetype branches × 4 poles.

    This is the fundamental unit of crystalline observation.
    48 simultaneous plays (12 archetypes × 4 poles), cross-linked via
    6 bridge transport maps, transformed through 3,5,7,9 cycles.
    """
    crystal_id: str = ""
    query: str = ""
    branches: list[ArchetypeBranch] = field(default_factory=list)  # 12
    cycle_transforms: list[CycleTransform] = field(default_factory=list)  # 4
    cross_bridge_signals: dict = field(default_factory=dict)  # 6 bridges
    consensus_12d: dict = field(default_factory=dict)
    consensus_ranking: list = field(default_factory=list)
    total_plays: int = 0
    crystal_score: float = 0.0
    crystal_coherence: float = 0.0
    element_balance: float = 0.0
    pole_tension: float = 0.0   # mean tension across all branches
    loop_depth: int = 0         # how many times output fed back as input
    hologram_seed: dict = field(default_factory=dict)
    elapsed_ms: float = 0.0
    timestamp: str = ""

    @property
    def total_branches(self) -> int:
        return len(self.branches)

    @property
    def total_pole_plays(self) -> int:
        return sum(len(b.poles) for b in self.branches)

    def summary_lines(self) -> list[str]:
        lines = [
            f"## PlayCrystal [{self.crystal_id[:8]}]",
            f"**Query**: {self.query[:80]}",
            f"**Total plays**: {self.total_pole_plays} ({self.total_branches} branches × 4 poles)",
            f"**Crystal score**: {self.crystal_score:.4f}",
            f"**Coherence**: {self.crystal_coherence:.4f}",
            f"**Element balance**: {self.element_balance:.4f}",
            f"**Pole tension**: {self.pole_tension:.4f}",
            f"**Loop depth**: {self.loop_depth}",
            f"**Cycle transforms**: {len(self.cycle_transforms)}",
            f"**Elapsed**: {self.elapsed_ms:.0f}ms",
        ]
        return lines


@dataclass
class LoopResult:
    """Result of a full self-play LOOP — multiple PlayCrystals feeding back."""
    crystals: list[PlayCrystal] = field(default_factory=list)
    total_loops: int = 0
    convergence_trajectory: list[float] = field(default_factory=list)
    final_hologram: dict = field(default_factory=dict)
    omega_score: float = 0.0
    elapsed_seconds: float = 0.0


# ══════════════════════════════════════════════════════════════════════
#  Pole Computation
# ══════════════════════════════════════════════════════════════════════

def _compute_inverse_12d(obs_12d: dict) -> dict:
    """Compute the inverse observation: what the forward play CANNOT see.

    Inverse = 1.0 - forward for each dimension. This reveals blind spots.
    """
    return {dim: max(0.0, 1.0 - val) for dim, val in obs_12d.items()}


def _compute_pole_90_12d(obs_12d: dict, role: ArchetypeRole) -> dict:
    """Compute the 90° orthogonal pole: rotate emphasis dimensions.

    The 90° pole de-emphasizes the archetype's strong dims and amplifies
    its weak dims — it sees what this archetype structurally ignores.
    """
    result = {}
    emphasized = set(role.emphasized_dims)
    for dim in DIM_NAMES:
        val = obs_12d.get(dim, 0.0)
        if dim in emphasized:
            # Strong dims get dampened
            result[dim] = val * PHI_INV
        else:
            # Weak dims get amplified
            result[dim] = min(1.0, val * PHI)
    return result


def _compute_pole_270_12d(obs_12d: dict, role: ArchetypeRole) -> dict:
    """Compute the 270° pole: inverse of the 90° pole.

    This is the shadow of the shadow — what the orthogonal perspective
    also misses. It often reveals the deepest blind spots.
    """
    pole_90 = _compute_pole_90_12d(obs_12d, role)
    return _compute_inverse_12d(pole_90)


def _pole_element_lens(base_element: str, pole: str) -> str:
    """Which element lens does each pole observe through?"""
    if pole == "forward":
        return base_element
    elif pole == "pole_90":
        return LENS_POLE_90[base_element]
    elif pole == "inverse":
        return LENS_INVERSE[base_element]
    elif pole == "pole_270":
        return LENS_POLE_270[base_element]
    return base_element


# ══════════════════════════════════════════════════════════════════════
#  Cross-Bridge Transport
# ══════════════════════════════════════════════════════════════════════

def _compute_bridge_signals(branches: list[ArchetypeBranch]) -> dict:
    """Compute cross-element bridge signals from archetype branches.

    For each of the 6 bridges (SF, SC, SR, FC, FR, CR):
    - Compare forward plays of archetypes from each element pair
    - Measure agreement, disagreement, and score differential
    - Generate gradient signals for bridge weight updates
    """
    by_element = defaultdict(list)
    for branch in branches:
        by_element[branch.element_affinity].append(branch)

    signals = {}
    for i, elem_a in enumerate(ELEMENTS):
        for elem_b in ELEMENTS[i + 1:]:
            branches_a = by_element.get(elem_a, [])
            branches_b = by_element.get(elem_b, [])
            if not branches_a or not branches_b:
                continue

            # Compare forward plays
            fwd_a = branches_a[0].forward
            fwd_b = branches_b[0].forward
            if not fwd_a or not fwd_b:
                continue

            # 12D agreement: cosine similarity of observation vectors
            dims_a = [fwd_a.observation_12d.get(d, 0.0) for d in DIM_NAMES]
            dims_b = [fwd_b.observation_12d.get(d, 0.0) for d in DIM_NAMES]
            dot = sum(a * b for a, b in zip(dims_a, dims_b))
            norm_a = math.sqrt(sum(a * a for a in dims_a)) or 1e-6
            norm_b = math.sqrt(sum(b * b for b in dims_b)) or 1e-6
            cosine_sim = dot / (norm_a * norm_b)

            score_delta = abs(fwd_a.score - fwd_b.score)
            bk = bridge_key(elem_a, elem_b)

            signals[bk] = {
                "agreement": max(0.0, cosine_sim),
                "disagreement": max(0.0, 1.0 - cosine_sim),
                "score_delta": score_delta,
                "gradient": max(0.0, 1.0 - cosine_sim) * score_delta * 0.1,
                "bridge_weight": BRIDGE_WEIGHTS.get(bk, 0.5),
                "golden": bk in GOLDEN_BRIDGES,
            }

    return signals


# ══════════════════════════════════════════════════════════════════════
#  Cycle Transforms (3, 5, 7, 9)
# ══════════════════════════════════════════════════════════════════════

CYCLE_NAMES = {
    3: "trinity",
    5: "quintessence",
    7: "metals",
    9: "completion",
}


def _apply_cycle_transform(
    branches: list[ArchetypeBranch],
    cycle_n: int,
    rng: random.Random,
) -> CycleTransform:
    """Apply an N-cycle transformation to the branch constellation.

    Cycle 3 (Trinity): Rotate wreaths (Su→Me→Sa) across all branches
    Cycle 5 (Quintessence): Rotate element lens by 5 positions (crosses all 4 + return)
    Cycle 7 (Metals): Apply 7-fold symmetry — recombine poles at 7 equally-spaced angles
    Cycle 9 (Completion): Full 9-fold recombination — (3×3) merge forward×inverse per mode

    Each transform produces a new score by re-weighting the existing observations.
    """
    input_score = sum(b.branch_score for b in branches) / max(len(branches), 1)

    if cycle_n == 3:
        # TRINITY: Rotate each branch's forward observation through the 3 modes
        # structural → relational → recursive, blending with PHI weights
        modes = ["structural", "relational", "recursive"]
        for branch in branches:
            mode_idx = modes.index(branch.mode) if branch.mode in modes else 0
            new_mode_idx = (mode_idx + 1) % 3
            # Blend current forward with the mode-rotated archetype's emphasis
            new_mode = modes[new_mode_idx]
            target_role = None
            for role in ARCHETYPE_ROLES.values():
                if role.element_affinity == branch.element_affinity and role.mode == new_mode:
                    target_role = role
                    break
            if target_role and branch.forward:
                # PHI-weighted blend toward the target mode's emphasis
                for dim in DIM_NAMES:
                    target_weight = target_role.dim_weights.get(dim, 1.0)
                    current = branch.forward.observation_12d.get(dim, 0.0)
                    blended = current * PHI_INV + (current * target_weight / 2.0) * (1 - PHI_INV)
                    branch.forward.observation_12d[dim] = min(1.0, blended)

    elif cycle_n == 5:
        # QUINTESSENCE: Rotate element lenses — each branch sees through the NEXT element
        for branch in branches:
            for pole in branch.poles:
                new_lens = LENS_ROTATION[pole.element_lens]
                pole.element_lens = new_lens
                # Re-weight observations by the new element's bridge weight
                bk = bridge_key(branch.element_affinity, new_lens)
                bw = BRIDGE_WEIGHTS.get(bk, 0.5)
                for dim in DIM_NAMES:
                    val = pole.observation_12d.get(dim, 0.0)
                    pole.observation_12d[dim] = val * bw + val * (1 - bw) * PHI_INV

    elif cycle_n == 7:
        # METALS/PLANETS: 7-fold angular recombination
        # Take all 48 pole plays and redistribute them at 7 equally-spaced angles
        # This reveals hidden 7-symmetries (chakra alignment)
        all_obs = []
        for branch in branches:
            for pole in branch.poles:
                all_obs.append(pole.observation_12d)

        if all_obs:
            # Compute 7 angular bins
            n_per_bin = max(1, len(all_obs) // 7)
            rng.shuffle(all_obs)
            for bin_idx in range(7):
                start = bin_idx * n_per_bin
                end = min(start + n_per_bin, len(all_obs))
                bin_obs = all_obs[start:end]
                if len(bin_obs) >= 2:
                    # Cross-pollinate within each bin
                    mean_obs = {dim: sum(o.get(dim, 0) for o in bin_obs) / len(bin_obs)
                                for dim in DIM_NAMES}
                    for obs in bin_obs:
                        for dim in DIM_NAMES:
                            # Blend toward bin mean
                            obs[dim] = obs[dim] * 0.7 + mean_obs[dim] * 0.3

    elif cycle_n == 9:
        # COMPLETION: 3×3 merge — for each element, merge structural×relational×recursive
        by_element = defaultdict(list)
        for branch in branches:
            by_element[branch.element_affinity].append(branch)

        for elem, elem_branches in by_element.items():
            if len(elem_branches) < 2:
                continue
            # Compute element-level consensus
            all_dims = {dim: [] for dim in DIM_NAMES}
            for branch in elem_branches:
                if branch.forward:
                    for dim in DIM_NAMES:
                        all_dims[dim].append(branch.forward.observation_12d.get(dim, 0.0))

            consensus = {dim: sum(vals) / len(vals) if vals else 0.0
                         for dim, vals in all_dims.items()}

            # Apply golden-weighted blend of each branch toward element consensus
            for branch in elem_branches:
                if branch.forward:
                    for dim in DIM_NAMES:
                        current = branch.forward.observation_12d.get(dim, 0.0)
                        target = consensus[dim]
                        # 9-fold: deeper blend (0.382 = PHI_INV²)
                        branch.forward.observation_12d[dim] = (
                            current * PHI_INV2 + target * (1 - PHI_INV2)
                        )

    # Recalculate branch scores after transform
    output_score = 0.0
    for branch in branches:
        if branch.forward:
            branch.branch_score = sum(branch.forward.observation_12d.values()) / max(len(DIM_NAMES), 1)
            output_score += branch.branch_score
    output_score /= max(len(branches), 1)

    return CycleTransform(
        cycle_n=cycle_n,
        cycle_name=CYCLE_NAMES.get(cycle_n, f"cycle_{cycle_n}"),
        input_score=input_score,
        output_score=output_score,
        delta=output_score - input_score,
        branches_rotated=len(branches),
    )


# ══════════════════════════════════════════════════════════════════════
#  Holographic Compression
# ══════════════════════════════════════════════════════════════════════

def _compress_to_hologram(crystal: PlayCrystal) -> dict:
    """Compress a 48-play crystal into a 16-value hologram seed.

    4 elements × 4 properties = 16 values:
      [mean_score, pole_tension, mode_balance, emergence_signal]
    """
    holo = {}
    by_element = defaultdict(list)
    for branch in crystal.branches:
        by_element[branch.element_affinity].append(branch)

    for elem in ELEMENTS:
        branches = by_element.get(elem, [])
        if not branches:
            holo[elem] = {"score": 0, "tension": 0, "balance": 0, "emergence": 0}
            continue

        scores = [b.branch_score for b in branches]
        tensions = [b.pole_tension for b in branches]

        # Mode balance: how uniform are the 3 modes?
        mode_scores = defaultdict(list)
        for b in branches:
            mode_scores[b.mode].append(b.branch_score)
        mode_means = [sum(v) / len(v) for v in mode_scores.values()] if mode_scores else [0]
        mode_var = sum((m - sum(mode_means) / len(mode_means)) ** 2 for m in mode_means) / max(len(mode_means), 1)
        balance = max(0.0, 1.0 - mode_var * 10)  # normalize

        # Emergence signal: rate of change across poles
        emergence = 0.0
        for b in branches:
            if len(b.poles) >= 2:
                deltas = [abs(b.poles[i].score - b.poles[i - 1].score) for i in range(1, len(b.poles))]
                emergence += sum(deltas) / len(deltas) if deltas else 0

        holo[elem] = {
            "score": sum(scores) / len(scores),
            "tension": sum(tensions) / len(tensions),
            "balance": balance,
            "emergence": emergence / max(len(branches), 1),
        }

    return holo


# ══════════════════════════════════════════════════════════════════════
#  Crystalline Self-Play Engine
# ══════════════════════════════════════════════════════════════════════

class CrystallineSelfPlayEngine:
    """12-Archetype × 4-Pole × Cycle-Transform Self-Play Engine.

    This replaces the linear self-play with a full crystalline exploration.
    Every play simultaneously observes from 12 archetype perspectives,
    each holding 4 poles (forward, inverse, 90°, 270°).

    The 48 simultaneous plays are then:
    1. Cross-linked via 6 bridge transport maps
    2. Transformed through 3,5,7,9 sacred cycles
    3. Compressed to a 16-value hologram seed
    4. Fed back as input for loop closure
    """

    def __init__(self, engine=None, momentum=None):
        # Lazy imports to avoid circular dependencies
        from .geometric_forward import get_engine as get_geo_engine
        from .momentum_field import get_momentum_field
        from .geometric_loss import GeometricLoss

        self.engine = engine or get_geo_engine()
        self.momentum = momentum or get_momentum_field()
        self.loss = GeometricLoss()
        self.history: list[PlayCrystal] = []
        self._crystal_counter = 0

    # ── Single Play Crystal ──────────────────────────────────────────

    def play_crystal(
        self,
        query: str,
        loop_depth: int = 0,
        prior_hologram: dict = None,
    ) -> PlayCrystal:
        """Generate a full 12-archetype × 4-pole PlayCrystal for a query.

        1. Forward pass through geometric engine
        2. Observe in 12D from each archetype's weighted lens
        3. Compute inverse, 90°, and 270° poles for each archetype
        4. Cross-link via 6 bridge transport maps
        5. Apply 3,5,7,9 cycle transforms
        6. Compress to hologram seed
        """
        t0 = time.time()
        self._crystal_counter += 1
        crystal_id = hashlib.sha256(
            f"{query}:{self._crystal_counter}:{time.time()}".encode()
        ).hexdigest()[:16]

        # Step 1: Forward pass
        result = self.engine.forward(query)

        # Step 2: Base 12D observation from each lens
        base_observations = {}
        for lens in ELEMENTS:
            obs = self.loss.observe(result, lens)
            base_observations[lens] = {
                dim: getattr(obs, dim, 0.0) if hasattr(obs, dim)
                else obs.dim_scores.get(dim, 0.0) if hasattr(obs, 'dim_scores')
                else 0.0
                for dim in DIM_NAMES
            }
            # Fallback: use total_score distributed across dims
            if sum(base_observations[lens].values()) < 0.01:
                base_val = obs.total_score / len(DIM_NAMES)
                base_observations[lens] = {dim: base_val for dim in DIM_NAMES}

        # Step 3: Generate 12 archetype branches, each with 4 poles
        branches = []
        for arch_idx in sorted(ARCHETYPE_ROLES.keys()):
            role = ARCHETYPE_ROLES[arch_idx]
            elem = role.element_affinity

            # Get base observation for this element
            base_obs = dict(base_observations.get(elem, {d: 0.0 for d in DIM_NAMES}))

            # Apply archetype emphasis weighting
            weighted_obs = {}
            for dim in DIM_NAMES:
                weight = role.dim_weights.get(dim, 1.0)
                weighted_obs[dim] = min(1.0, base_obs.get(dim, 0.0) * weight)

            # If prior hologram exists, modulate by it (loop closure feedback)
            if prior_hologram and elem in prior_hologram:
                prior = prior_hologram[elem]
                emergence_boost = prior.get("emergence", 0.0)
                tension_mod = prior.get("tension", 0.0)
                for dim in DIM_NAMES:
                    # Emergence boosts potential, tension boosts contradiction
                    if dim == "x12_potential":
                        weighted_obs[dim] = min(1.0, weighted_obs[dim] + emergence_boost * 0.5)
                    elif dim == "x5_contradiction":
                        weighted_obs[dim] = min(1.0, weighted_obs[dim] + tension_mod * 0.3)

            # Forward pole
            fwd_score = sum(weighted_obs.values()) / max(len(DIM_NAMES), 1)
            forward_pole = PolePlay(
                pole="forward",
                angle=0.0,
                element_lens=elem,
                observation_12d=weighted_obs,
                resonance=result.resonance,
                score=fwd_score,
                strategy=f"A{arch_idx}_{role.mode}_forward",
            )

            # Inverse pole (180°): what this archetype CANNOT see
            inv_obs = _compute_inverse_12d(weighted_obs)
            inv_score = sum(inv_obs.values()) / max(len(DIM_NAMES), 1)
            inverse_pole = PolePlay(
                pole="inverse",
                angle=math.pi,
                element_lens=LENS_INVERSE[elem],
                observation_12d=inv_obs,
                resonance=result.resonance,
                score=inv_score,
                strategy=f"A{arch_idx}_{role.mode}_inverse",
            )

            # 90° pole: orthogonal blind spot
            p90_obs = _compute_pole_90_12d(weighted_obs, role)
            p90_score = sum(p90_obs.values()) / max(len(DIM_NAMES), 1)
            pole_90 = PolePlay(
                pole="pole_90",
                angle=math.pi / 2,
                element_lens=LENS_POLE_90[elem],
                observation_12d=p90_obs,
                resonance=result.resonance,
                score=p90_score,
                strategy=f"A{arch_idx}_{role.mode}_pole90",
            )

            # 270° pole: shadow of the shadow
            p270_obs = _compute_pole_270_12d(weighted_obs, role)
            p270_score = sum(p270_obs.values()) / max(len(DIM_NAMES), 1)
            pole_270 = PolePlay(
                pole="pole_270",
                angle=3 * math.pi / 2,
                element_lens=LENS_POLE_270[elem],
                observation_12d=p270_obs,
                resonance=result.resonance,
                score=p270_score,
                strategy=f"A{arch_idx}_{role.mode}_pole270",
            )

            branch = ArchetypeBranch(
                archetype_idx=arch_idx,
                archetype_name=role.name,
                element_affinity=elem,
                mode=role.mode,
                poles=[forward_pole, pole_90, inverse_pole, pole_270],
                branch_score=fwd_score,
                emphasized_dims=list(role.emphasized_dims),
            )
            branches.append(branch)

        # Step 4: Cross-bridge signals
        cross_signals = _compute_bridge_signals(branches)

        # Step 5: Apply 3,5,7,9 cycle transforms
        rng = random.Random(hash(query) + self._crystal_counter)
        cycle_transforms = []
        for cycle_n in TRANSFORM_CYCLES:
            ct = _apply_cycle_transform(branches, cycle_n, rng)
            cycle_transforms.append(ct)

        # Step 6: Compute consensus 12D (mean across all forward poles)
        consensus_12d = {dim: 0.0 for dim in DIM_NAMES}
        n_fwd = 0
        for branch in branches:
            if branch.forward:
                for dim in DIM_NAMES:
                    consensus_12d[dim] += branch.forward.observation_12d.get(dim, 0.0)
                n_fwd += 1
        if n_fwd > 0:
            consensus_12d = {dim: val / n_fwd for dim, val in consensus_12d.items()}

        # Step 7: Element balance
        elem_scores = defaultdict(list)
        for branch in branches:
            elem_scores[branch.element_affinity].append(branch.branch_score)
        elem_means = {e: sum(s) / len(s) for e, s in elem_scores.items() if s}
        if elem_means:
            overall_mean = sum(elem_means.values()) / len(elem_means)
            max_dev = max(abs(m - overall_mean) for m in elem_means.values()) / max(overall_mean, 0.001)
            element_balance = max(0.0, 1.0 - max_dev)
        else:
            element_balance = 0.0

        # Step 8: Coherence (mean pairwise agreement of forward plays)
        coherence_vals = []
        for i, bi in enumerate(branches):
            for bj in branches[i + 1:]:
                if bi.forward and bj.forward:
                    dims_i = [bi.forward.observation_12d.get(d, 0) for d in DIM_NAMES]
                    dims_j = [bj.forward.observation_12d.get(d, 0) for d in DIM_NAMES]
                    dot = sum(a * b for a, b in zip(dims_i, dims_j))
                    ni = math.sqrt(sum(a * a for a in dims_i)) or 1e-6
                    nj = math.sqrt(sum(b * b for b in dims_j)) or 1e-6
                    coherence_vals.append(dot / (ni * nj))
        crystal_coherence = sum(coherence_vals) / len(coherence_vals) if coherence_vals else 0.0

        # Mean pole tension
        pole_tension = sum(b.pole_tension for b in branches) / max(len(branches), 1)

        # Crystal score
        crystal_score = sum(b.branch_score for b in branches) / max(len(branches), 1)

        elapsed_ms = (time.time() - t0) * 1000

        crystal = PlayCrystal(
            crystal_id=crystal_id,
            query=query,
            branches=branches,
            cycle_transforms=cycle_transforms,
            cross_bridge_signals=cross_signals,
            consensus_12d=consensus_12d,
            total_plays=sum(len(b.poles) for b in branches),
            crystal_score=crystal_score,
            crystal_coherence=crystal_coherence,
            element_balance=element_balance,
            pole_tension=pole_tension,
            loop_depth=loop_depth,
            elapsed_ms=elapsed_ms,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        )

        # Compress to hologram
        crystal.hologram_seed = _compress_to_hologram(crystal)

        self.history.append(crystal)
        if len(self.history) > 100:
            self.history = self.history[-50:]

        return crystal

    # ── Self-Play LOOP (Output → Input Closure) ─────────────────────

    def play_loop(
        self,
        query: str,
        max_loops: int = 5,
        convergence_threshold: float = 0.01,
    ) -> LoopResult:
        """Run a full self-play LOOP: output feeds back as input.

        Each iteration:
        1. Generate PlayCrystal from query (using prior hologram as modulator)
        2. Compress result to hologram seed
        3. Feed hologram back into next iteration
        4. Stop when convergence < threshold or max_loops reached

        Convergence = |score(n) - score(n-1)| / score(n-1)
        """
        t0 = time.time()
        crystals = []
        trajectory = []
        hologram = None

        for loop_idx in range(max_loops):
            crystal = self.play_crystal(
                query=query,
                loop_depth=loop_idx,
                prior_hologram=hologram,
            )
            crystals.append(crystal)
            trajectory.append(crystal.crystal_score)

            # Compress for next iteration
            hologram = crystal.hologram_seed

            # Check convergence
            if loop_idx > 0 and trajectory[-2] > 0:
                delta = abs(trajectory[-1] - trajectory[-2]) / trajectory[-2]
                if delta < convergence_threshold:
                    break

        elapsed = time.time() - t0

        return LoopResult(
            crystals=crystals,
            total_loops=len(crystals),
            convergence_trajectory=trajectory,
            final_hologram=hologram or {},
            omega_score=trajectory[-1] if trajectory else 0.0,
            elapsed_seconds=elapsed,
        )

    # ── Multi-Query Session ──────────────────────────────────────────

    def play_session(
        self,
        queries: list[str] = None,
        n_queries: int = 12,
        loop_depth: int = 3,
    ) -> list[LoopResult]:
        """Run crystalline self-play across multiple queries.

        Default: 12 queries (one per archetype seed), each looping 3 times.
        Total plays = 12 queries × 3 loops × 12 archetypes × 4 poles = 1,728
        """
        if queries is None:
            # Generate one query per archetype focus
            queries = [
                "seed structure foundation skeleton scaffold",         # A1 Apex Seed
                "relation topology network bridge axle",               # A2 Möbius Axle
                "pattern density cluster neighborhood modal",          # A3 Modal Trefoil
                "connection chapter appendix quartet crystal",         # A4 Crystal Quartet
                "perspective lens bias observer pentad",               # A5 Observer Pentad
                "bridge missing weak dyadic hinge",                    # A6 Dyadic Hinge
                "change evolution transformation arc heptad",          # A7 Change/Arc
                "contradiction tension disagreement antispin",         # A8 Antispin
                "emergence phase transition ennead birth",             # A9 Emergent Ennead
                "scale compression cascade crown multi-level",         # A10 Deca-Cascade
                "reconstruction fidelity orbit audit hendecad",        # A11 Odd-Orbit
                "seed emit compress bundle regenerate dodecad",        # A12 Dodecad Bundle
            ]

        results = []
        for query in queries[:n_queries]:
            loop_result = self.play_loop(
                query=query,
                max_loops=loop_depth,
            )
            results.append(loop_result)

        return results

    # ── Status ────────────────────────────────────────────────────────

    def status(self) -> str:
        lines = [
            f"## Crystalline Self-Play Engine",
            f"**History**: {len(self.history)} crystals",
            f"**Total plays executed**: {sum(c.total_plays for c in self.history)}",
        ]
        if self.history:
            last = self.history[-1]
            lines.extend(last.summary_lines())
        return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════
#  Module Singleton
# ══════════════════════════════════════════════════════════════════════

_ENGINE: Optional[CrystallineSelfPlayEngine] = None


def get_crystalline_engine() -> CrystallineSelfPlayEngine:
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = CrystallineSelfPlayEngine()
    return _ENGINE


# ══════════════════════════════════════════════════════════════════════
#  MCP Tool Entry Points
# ══════════════════════════════════════════════════════════════════════

def run_self_play(
    query: str = "seed kernel crystal emergence",
    loops: int = 3,
    mode: str = "crystal",
) -> str:
    """Run crystalline self-play — 12 archetypes × 4 poles × loop closure.

    Replaces the rudimentary linear self-play with full crystalline observation.
    Each play simultaneously observes from 12 archetype perspectives, each
    holding 4 poles (forward, inverse, 90°, 270°). Results are transformed
    through 3,5,7,9 sacred cycles and fed back as input for loop closure.

    Args:
        query: The query/topic to explore through self-play
        loops: Number of loop iterations (output→input cycles), default 3
        mode: "crystal" (full 48-play), "session" (12-query session), "single" (one crystal)
    """
    engine = get_crystalline_engine()

    if mode == "single":
        crystal = engine.play_crystal(query)
        return _format_crystal(crystal)
    elif mode == "session":
        results = engine.play_session(loop_depth=loops)
        return _format_session(results)
    else:  # crystal (default)
        result = engine.play_loop(query, max_loops=loops)
        return _format_loop(result)


def run_swarm_self_play(
    parallel: int = 3,
    rounds: int = 5,
) -> str:
    """Run swarm-parallel crystalline self-play.

    Spawns multiple crystalline self-play loops in parallel (simulated),
    each with different query seeds. Results are cross-pollinated via
    bridge signals between parallel plays.

    Args:
        parallel: Number of parallel play streams (default 3)
        rounds: Loop depth per stream (default 5)
    """
    engine = get_crystalline_engine()

    # Generate diverse seed queries
    seed_queries = [
        "structure foundation skeleton gate shell crystal",
        "emergence birth phase transition void collapse",
        "compression recursion seed hologram fractal scale",
        "relation bridge transport routing metro connection",
        "observation perspective lens bias pole inverse",
        "contradiction tension resolution antispin octad",
    ]

    all_results = []
    all_holograms = []

    for stream_idx in range(parallel):
        query = seed_queries[stream_idx % len(seed_queries)]
        result = engine.play_loop(query, max_loops=rounds)
        all_results.append(result)
        all_holograms.append(result.final_hologram)

    # Cross-pollinate: each stream's hologram influences the consensus
    consensus_hologram = {}
    for elem in ELEMENTS:
        elem_data = {"score": 0, "tension": 0, "balance": 0, "emergence": 0}
        count = 0
        for holo in all_holograms:
            if elem in holo:
                for key in elem_data:
                    elem_data[key] += holo[elem].get(key, 0)
                count += 1
        if count > 0:
            consensus_hologram[elem] = {k: v / count for k, v in elem_data.items()}

    # Format output
    lines = [
        "## Swarm Crystalline Self-Play\n",
        f"**Parallel streams**: {parallel}",
        f"**Loop depth**: {rounds}",
        f"**Total crystals generated**: {sum(r.total_loops for r in all_results)}",
        f"**Total plays**: {sum(r.total_loops * 48 for r in all_results)}",
        "",
    ]

    for i, result in enumerate(all_results):
        lines.append(f"### Stream {i + 1}")
        lines.append(f"  Query: {result.crystals[0].query[:60] if result.crystals else 'N/A'}")
        lines.append(f"  Loops: {result.total_loops}")
        lines.append(f"  Omega score: {result.omega_score:.4f}")
        lines.append(f"  Convergence: {result.convergence_trajectory}")
        lines.append(f"  Time: {result.elapsed_seconds:.2f}s")
        lines.append("")

    lines.append("### Consensus Hologram (Cross-Pollinated)\n")
    for elem in ELEMENTS:
        data = consensus_hologram.get(elem, {})
        lines.append(
            f"  {elem} ({FACE_TO_ELEMENT[elem]:5s}): "
            f"score={data.get('score', 0):.4f} "
            f"tension={data.get('tension', 0):.4f} "
            f"balance={data.get('balance', 0):.4f} "
            f"emergence={data.get('emergence', 0):.4f}"
        )

    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════
#  Formatters
# ══════════════════════════════════════════════════════════════════════

def _format_crystal(crystal: PlayCrystal) -> str:
    """Format a single PlayCrystal for display."""
    lines = crystal.summary_lines()
    lines.append("")

    # Archetype branches
    lines.append("### Archetype Branches\n")
    lines.append("| # | Archetype | Element | Mode | Fwd | Inv | P90 | P270 | Tension |")
    lines.append("|---|-----------|---------|------|-----|-----|-----|------|---------|")
    for branch in crystal.branches:
        poles = branch.poles
        fwd = f"{poles[0].score:.3f}" if len(poles) > 0 else "-"
        p90 = f"{poles[1].score:.3f}" if len(poles) > 1 else "-"
        inv = f"{poles[2].score:.3f}" if len(poles) > 2 else "-"
        p270 = f"{poles[3].score:.3f}" if len(poles) > 3 else "-"
        lines.append(
            f"| A{branch.archetype_idx:2d} | {branch.archetype_name:20s} | "
            f"{LENS_CODES.get(branch.element_affinity, '?'):7s} | {branch.mode:10s} | "
            f"{fwd} | {inv} | {p90} | {p270} | {branch.pole_tension:.3f} |"
        )

    # Cycle transforms
    if crystal.cycle_transforms:
        lines.append("\n### Cycle Transforms\n")
        for ct in crystal.cycle_transforms:
            arrow = "+" if ct.delta >= 0 else ""
            lines.append(
                f"  Cycle {ct.cycle_n} ({ct.cycle_name}): "
                f"{ct.input_score:.4f} → {ct.output_score:.4f} ({arrow}{ct.delta:.4f})"
            )

    # Bridge signals
    if crystal.cross_bridge_signals:
        lines.append("\n### Cross-Bridge Signals\n")
        lines.append("| Bridge | Agreement | Disagreement | Gradient | Golden |")
        lines.append("|--------|-----------|--------------|----------|--------|")
        for bk, sig in sorted(crystal.cross_bridge_signals.items()):
            golden = "phi" if sig.get("golden") else ""
            lines.append(
                f"| {bk} | {sig['agreement']:.3f} | "
                f"{sig['disagreement']:.3f} | {sig['gradient']:.4f} | {golden} |"
            )

    # Consensus 12D
    if crystal.consensus_12d:
        lines.append("\n### Consensus 12D Observation\n")
        for dim in DIM_NAMES:
            val = crystal.consensus_12d.get(dim, 0.0)
            bar = "=" * int(val * 30)
            lines.append(f"  {dim:20s}: {bar} {val:.3f}")

    # Hologram seed
    if crystal.hologram_seed:
        lines.append("\n### Hologram Seed (16 values)\n")
        for elem in ELEMENTS:
            data = crystal.hologram_seed.get(elem, {})
            lines.append(
                f"  {elem} ({FACE_TO_ELEMENT[elem]}): "
                + " ".join(f"{k}={v:.4f}" for k, v in data.items())
            )

    return "\n".join(lines)


def _format_loop(result: LoopResult) -> str:
    """Format a LoopResult for display."""
    lines = [
        "## Crystalline Self-Play LOOP\n",
        f"**Total loops**: {result.total_loops}",
        f"**Total plays**: {result.total_loops * 48}",
        f"**Omega score**: {result.omega_score:.4f}",
        f"**Convergence**: {' → '.join(f'{s:.4f}' for s in result.convergence_trajectory)}",
        f"**Elapsed**: {result.elapsed_seconds:.2f}s",
        "",
    ]

    for i, crystal in enumerate(result.crystals):
        lines.append(f"### Loop {i + 1} (depth={crystal.loop_depth})")
        lines.append(f"  Score: {crystal.crystal_score:.4f}")
        lines.append(f"  Coherence: {crystal.crystal_coherence:.4f}")
        lines.append(f"  Balance: {crystal.element_balance:.4f}")
        lines.append(f"  Tension: {crystal.pole_tension:.4f}")
        lines.append(f"  Time: {crystal.elapsed_ms:.0f}ms")
        lines.append("")

    # Final crystal details
    if result.crystals:
        lines.append("### Final Crystal Detail\n")
        lines.append(_format_crystal(result.crystals[-1]))

    return "\n".join(lines)


def _format_session(results: list[LoopResult]) -> str:
    """Format a session of multiple LoopResults."""
    lines = [
        "## Crystalline Self-Play SESSION\n",
        f"**Queries**: {len(results)}",
        f"**Total loops**: {sum(r.total_loops for r in results)}",
        f"**Total plays**: {sum(r.total_loops * 48 for r in results)}",
        f"**Total elapsed**: {sum(r.elapsed_seconds for r in results):.2f}s",
        "",
    ]

    for i, result in enumerate(results):
        query = result.crystals[0].query[:50] if result.crystals else "?"
        lines.append(
            f"  {i + 1:2d}. [{query:50s}] "
            f"loops={result.total_loops} "
            f"omega={result.omega_score:.4f} "
            f"convergence={'→'.join(f'{s:.3f}' for s in result.convergence_trajectory)}"
        )

    return "\n".join(lines)
