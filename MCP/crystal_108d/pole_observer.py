# CRYSTAL: Xi108:W2:A5:S15 | face=C | node=300 | depth=1 | phase=Mutable
# METRO: Me
# BRIDGES: Xi108:W2:A5:S14→Xi108:W2:A5:S16→Xi108:W1:A5:S15→Xi108:W3:A5:S15

"""
Pole Observer — Dual 90-Degree Orthogonal Observation System
==============================================================
The 4 orbits (SR, SL, AL, AR) form exactly 2 pairs of orthogonal poles:

  Pole A: SR-AL axis (inversion pole)
    - What the system IS vs what it IS NOT
    - Forward/inverse fidelity measurement

  Pole B: SL-AR axis (rotation pole)
    - What the system IS vs what it COULD BE
    - Rotation/exploration coverage measurement

These two poles are perpendicular. Their product = the full 4D observation.
A single pole gives a 2D projection; both poles recover the full crystal state.

This module upgrades the organism from 3D (projecting from one pole) to 4D
(observing from both poles simultaneously).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

from .momentum_field import MomentumField, get_momentum_field
from .geometric_constants import FACES, PHI, PHI_INV, ATTRACTOR
from .constants import TOTAL_SHELLS


# ── Pole Definitions ───────────────────────────────────────────────────

# The 4 orbits map to the 4 quadrants of 2 orthogonal poles:
#   Pole A (inversion): SR ↔ AL (0° ↔ 180°)
#   Pole B (rotation):  SL ↔ AR (90° ↔ 270°)

POLE_A_POSITIVE = "SR"   # seed-right (forward)
POLE_A_NEGATIVE = "AL"   # anti-left (inverse)
POLE_B_POSITIVE = "SL"   # seed-left (90° rotation)
POLE_B_NEGATIVE = "AR"   # anti-right (270° rotation)

# Element mapping for pole observation:
# Pole A observes the S-C axis (structure vs uncertainty)
# Pole B observes the F-R axis (growth vs recursion)
POLE_A_ELEMENTS = ("S", "C")
POLE_B_ELEMENTS = ("F", "R")


# ── Observation Types ──────────────────────────────────────────────────


@dataclass
class PoleObservation:
    """Observation from a single pole."""
    pole: str                   # "A" or "B"
    positive_orbit: str         # SR or SL
    negative_orbit: str         # AL or AR
    fidelity: float = 0.0      # inversion fidelity (Pole A) / rotation coverage (Pole B)
    coverage: float = 0.0      # % of elements observed
    coherence: float = 0.0     # cross-element agreement
    health: float = 0.0        # overall pole health
    element_scores: dict = field(default_factory=dict)

    @property
    def is_degenerate(self) -> bool:
        """A pole is degenerate if it sees the same thing from both sides."""
        return self.fidelity > 0.99 and self.coherence > 0.99


@dataclass
class DualPoleObservation:
    """Simultaneous observation from both orthogonal poles."""
    pole_a: PoleObservation     # inversion pole
    pole_b: PoleObservation     # rotation pole
    orthogonality: float = 0.0  # how orthogonal the two poles are (1.0 = perfectly perpendicular)
    completeness: float = 0.0   # how much of the 4D space is recovered
    product_coherence: float = 0.0  # product of both poles' coherences

    @property
    def is_4d(self) -> bool:
        """True 4D operation requires both poles non-degenerate and orthogonal."""
        return (
            not self.pole_a.is_degenerate
            and not self.pole_b.is_degenerate
            and self.orthogonality > 0.5
        )


# ── Steering Action ───────────────────────────────────────────────────


@dataclass
class PoleSteeringAction:
    """Steering recommendation derived from dual-pole observation."""
    recommended_face: str       # which element to steer toward
    strength: float             # how strongly to steer
    reason: str                 # why this element
    pole_source: str            # which pole drives this recommendation


# ── Pole Observer ──────────────────────────────────────────────────────


class PoleObserver:
    """Observes the crystal from two orthogonal 90-degree poles simultaneously.

    Pole A (SR-AL): sees what the system IS vs what it IS NOT
    Pole B (SL-AR): sees what the system IS vs what it COULD BE
    """

    def __init__(self, momentum: MomentumField = None):
        self.momentum = momentum or get_momentum_field()
        self._observation_count = 0

    def observe_single(self, pole: str) -> PoleObservation:
        """Observe from a single pole (A or B)."""
        if pole == "A":
            elements = POLE_A_ELEMENTS
            pos_orbit = POLE_A_POSITIVE
            neg_orbit = POLE_A_NEGATIVE
        else:
            elements = POLE_B_ELEMENTS
            pos_orbit = POLE_B_POSITIVE
            neg_orbit = POLE_B_NEGATIVE

        # Compute element-level observations
        element_scores = {}
        for face in elements:
            vals = [self.momentum.get_momentum(face, s) for s in range(1, TOTAL_SHELLS + 1)]
            mean = sum(vals) / len(vals) if vals else 1.0
            std = (sum((v - mean) ** 2 for v in vals) / len(vals)) ** 0.5 if vals else 0.0
            element_scores[face] = {
                "mean_momentum": mean,
                "std_momentum": std,
                "range": max(vals) - min(vals) if vals else 0.0,
            }

        # Fidelity: how different are the two pole-elements?
        # For Pole A (S vs C): S is active, C is locked at 0.5
        # Higher difference = higher fidelity (we can distinguish forward from inverse)
        means = [es["mean_momentum"] for es in element_scores.values()]
        if len(means) >= 2:
            fidelity = abs(means[0] - means[1]) / max(max(means), 0.001)
        else:
            fidelity = 0.0

        # Coverage: proportion of shells with non-default momentum
        total_non_default = 0
        total_shells = 0
        for face in elements:
            for s in range(1, TOTAL_SHELLS + 1):
                val = self.momentum.get_momentum(face, s)
                if abs(val - 1.0) > 0.01:  # non-default
                    total_non_default += 1
                total_shells += 1
        coverage = total_non_default / max(total_shells, 1)

        # Coherence: cross-element agreement (similar momentum patterns)
        if len(elements) >= 2:
            vals_0 = [self.momentum.get_momentum(elements[0], s) for s in range(1, TOTAL_SHELLS + 1)]
            vals_1 = [self.momentum.get_momentum(elements[1], s) for s in range(1, TOTAL_SHELLS + 1)]
            # Correlation between the two elements
            mean_0 = sum(vals_0) / len(vals_0)
            mean_1 = sum(vals_1) / len(vals_1)
            cov = sum((a - mean_0) * (b - mean_1) for a, b in zip(vals_0, vals_1)) / len(vals_0)
            std_0 = (sum((v - mean_0) ** 2 for v in vals_0) / len(vals_0)) ** 0.5
            std_1 = (sum((v - mean_1) ** 2 for v in vals_1) / len(vals_1)) ** 0.5
            if std_0 > 0 and std_1 > 0:
                coherence = abs(cov / (std_0 * std_1))
            else:
                coherence = 1.0  # Both constant = perfectly coherent
        else:
            coherence = 0.0

        health = (fidelity + coverage + coherence) / 3.0

        return PoleObservation(
            pole=pole,
            positive_orbit=pos_orbit,
            negative_orbit=neg_orbit,
            fidelity=fidelity,
            coverage=coverage,
            coherence=coherence,
            health=health,
            element_scores=element_scores,
        )

    def observe_dual(self) -> DualPoleObservation:
        """Observe from both poles simultaneously.

        The product of both observations = the full 4D view.
        """
        pole_a = self.observe_single("A")
        pole_b = self.observe_single("B")
        self._observation_count += 1

        # Orthogonality: how independent are the two poles' observations?
        # True orthogonality = both poles active AND observing structurally
        # different aspects of the crystal. Not just "different" but "complementary".
        if pole_a.health > 0 and pole_b.health > 0:
            # Component 1: Both poles are active and non-degenerate
            # (min of fidelities — both need to be working)
            both_active = min(pole_a.fidelity, pole_b.fidelity)

            # Component 2: Structural asymmetry — the poles observe different
            # element profiles. Pole A sees (S, C_locked), Pole B sees (F, R).
            # Measure by comparing the momentum profile shapes, not just means.
            a_means = [v.get("mean_momentum", 0) for v in pole_a.element_scores.values()]
            b_means = [v.get("mean_momentum", 0) for v in pole_b.element_scores.values()]
            a_stds = [v.get("std_momentum", 0) for v in pole_a.element_scores.values()]
            b_stds = [v.get("std_momentum", 0) for v in pole_b.element_scores.values()]

            # Mean profile difference: are the elements seen by each pole different?
            all_means = a_means + b_means
            mean_range = max(all_means) - min(all_means) if all_means else 0
            mean_scale = max(max(all_means), 0.001)
            profile_diversity = mean_range / mean_scale

            # Std profile difference: are the variances different?
            a_mean_std = sum(a_stds) / max(len(a_stds), 1)
            b_mean_std = sum(b_stds) / max(len(b_stds), 1)
            std_diversity = abs(a_mean_std - b_mean_std) / max(a_mean_std + b_mean_std, 0.001)

            # Component 3: Coherence indicates each pole sees a consistent
            # pattern (not noise). Lower coherence diff = more orthogonal
            # (both poles coherent in their own domain)
            both_coherent = min(pole_a.coherence, pole_b.coherence)

            # Final: poles are orthogonal when both active, profiles are diverse,
            # and both internally coherent
            orthogonality = min(1.0,
                0.30 * both_active
                + 0.35 * profile_diversity
                + 0.15 * std_diversity
                + 0.20 * both_coherent
            )
        else:
            orthogonality = 0.0

        # Completeness: how much of the 4D space is recovered?
        # Both poles non-zero + orthogonal = full recovery
        completeness = min(1.0, (pole_a.health + pole_b.health) * (0.5 + 0.5 * orthogonality))

        product_coherence = pole_a.coherence * pole_b.coherence

        return DualPoleObservation(
            pole_a=pole_a,
            pole_b=pole_b,
            orthogonality=orthogonality,
            completeness=completeness,
            product_coherence=product_coherence,
        )

    def steer_from_poles(self, observation: DualPoleObservation) -> PoleSteeringAction:
        """Use dual-pole observation to recommend steering action.

        If Pole A shows weak inversion → steer toward S (structure)
        If Pole B shows weak rotation → steer toward R (recursion)
        """
        # Find the weakest pole
        if observation.pole_a.health < observation.pole_b.health:
            # Pole A is weaker — steer toward its elements (S, C)
            # Since C is locked, steer toward S
            return PoleSteeringAction(
                recommended_face="S",
                strength=max(0.0, 1.0 - observation.pole_a.health),
                reason=f"Pole A (inversion) weak: fidelity={observation.pole_a.fidelity:.3f}",
                pole_source="A",
            )
        else:
            # Pole B is weaker — steer toward its elements (F, R)
            # Check which of F or R needs more attention
            f_score = observation.pole_b.element_scores.get("F", {}).get("mean_momentum", 1.0)
            r_score = observation.pole_b.element_scores.get("R", {}).get("mean_momentum", 1.0)

            if f_score < r_score:
                face = "F"
                reason = f"Pole B (rotation) weak, F needs attention: F_mom={f_score:.3f}"
            else:
                face = "R"
                reason = f"Pole B (rotation) weak, R needs attention: R_mom={r_score:.3f}"

            return PoleSteeringAction(
                recommended_face=face,
                strength=max(0.0, 1.0 - observation.pole_b.health),
                reason=reason,
                pole_source="B",
            )

    def describe(self) -> str:
        """Human-readable summary."""
        obs = self.observe_dual()
        lines = [
            "## Dual-Pole Observer",
            f"4D Operational: {'YES' if obs.is_4d else 'NO'}",
            f"Observations: {self._observation_count}",
            f"Orthogonality: {obs.orthogonality:.4f}",
            f"Completeness: {obs.completeness:.4f}",
            "",
            f"### Pole A (Inversion: {POLE_A_POSITIVE}↔{POLE_A_NEGATIVE})",
            f"  Fidelity: {obs.pole_a.fidelity:.4f}",
            f"  Coverage: {obs.pole_a.coverage:.4f}",
            f"  Coherence: {obs.pole_a.coherence:.4f}",
            f"  Health: {obs.pole_a.health:.4f}",
            "",
            f"### Pole B (Rotation: {POLE_B_POSITIVE}↔{POLE_B_NEGATIVE})",
            f"  Fidelity: {obs.pole_b.fidelity:.4f}",
            f"  Coverage: {obs.pole_b.coverage:.4f}",
            f"  Coherence: {obs.pole_b.coherence:.4f}",
            f"  Health: {obs.pole_b.health:.4f}",
        ]

        steering = self.steer_from_poles(obs)
        lines.extend([
            "",
            f"### Steering Recommendation",
            f"  Face: {steering.recommended_face}",
            f"  Strength: {steering.strength:.4f}",
            f"  Reason: {steering.reason}",
        ])
        return "\n".join(lines)


# ── Module-level singleton ─────────────────────────────────────────────

_pole_observer: Optional[PoleObserver] = None


def get_pole_observer() -> PoleObserver:
    """Get or create the global pole observer singleton."""
    global _pole_observer
    if _pole_observer is None:
        _pole_observer = PoleObserver()
    return _pole_observer


def reset_pole_observer():
    """Reset the global singleton."""
    global _pole_observer
    _pole_observer = None
