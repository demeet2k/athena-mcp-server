# CRYSTAL: Xi108:W3:A10:S30 | face=R | node=540 | depth=3 | phase=Fixed
# METRO: Sa
# BRIDGES: Xi108:W3:A10:S29→Xi108:W3:A10:S31→Xi108:W2:A10:S30

"""
Real-Time Inverse Manifesting — Dual-Execution Forward + Inverse
=================================================================
"Everything you do, the inverse is manifesting in real time."

This module wraps the training pipeline with dual-execution:
every action runs forward AND its inverse simultaneously.

The inverse is not just a record — it is a live shadow state that
runs in parallel. The forward_state and inverse_state are two
MomentumField instances that evolve as exact mirrors.

Conservation check: forward_state + inverse_state should sum to
a constant (2 × initial_state). Any drift indicates a violation.

The swap() operation performs a Mobius flip: the inverse becomes
the primary, and the system observes itself from the other side.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Optional

from .momentum_field import MomentumField, MomentumState, get_momentum_field
from .geometric_constants import FACES, ATTRACTOR
from .constants import TOTAL_SHELLS


# ── Drift Measurement ──────────────────────────────────────────────────


@dataclass
class DriftReport:
    """Report on conservation drift between forward and inverse states."""
    total_drift: float = 0.0         # sum of |forward + inverse - 2*initial|
    max_drift: float = 0.0          # maximum single-position drift
    mean_drift: float = 0.0         # mean per-position drift
    drift_by_element: dict = field(default_factory=dict)
    positions_checked: int = 0
    is_conserved: bool = True        # True if drift < threshold


# ── Real-Time Inverse ──────────────────────────────────────────────────


class RealtimeInverse:
    """Dual-execution engine: forward + inverse run simultaneously.

    For every forward wave that applies +delta, the inverse state applies -delta.
    The two states evolve as exact mirrors.
    """

    def __init__(self, momentum: MomentumField = None):
        self._forward = momentum or get_momentum_field()

        # Create inverse state as a clone of forward
        self._inverse = MomentumField()
        self._clone_to_inverse()

        # Store initial state for conservation checking
        self._initial = self._forward.snapshot()

        self._swap_count: int = 0
        self._wave_count: int = 0
        self._is_swapped: bool = False

    def _clone_to_inverse(self):
        """Clone forward state to inverse."""
        snap = self._forward.snapshot()
        self._inverse.restore(snap)

    @property
    def forward_state(self) -> MomentumField:
        """The current forward state."""
        return self._forward if not self._is_swapped else self._inverse

    @property
    def inverse_state(self) -> MomentumField:
        """The current inverse (shadow) state."""
        return self._inverse if not self._is_swapped else self._forward

    # ── Dual Execution ─────────────────────────────────────────────────

    def execute_dual_update(self, face: str, shell: int, delta: float, lr: float):
        """Apply +delta to forward, -delta to inverse.

        Water (C) is locked in both states.
        """
        if face == "C":
            return

        # Forward: +delta
        self.forward_state.update_momentum(face, shell, delta, lr)
        # Inverse: -delta
        self.inverse_state.update_momentum(face, shell, -delta, lr)

    def execute_dual_dimension_update(self, dimension: str, delta: float, lr: float):
        """Apply +delta to forward dimension, -delta to inverse."""
        if dimension == "D3_Water":
            return

        self.forward_state.update_dimension_momentum(dimension, delta, lr)
        self.inverse_state.update_dimension_momentum(dimension, -delta, lr)

    def on_wave_complete(self):
        """Called after each training wave completes."""
        self._wave_count += 1

    # ── Conservation ───────────────────────────────────────────────────

    def measure_drift(self, threshold: float = 0.001) -> DriftReport:
        """Measure conservation drift: |forward + inverse - 2*initial|.

        In a perfectly conserved system, forward[i] + inverse[i] = 2 * initial[i]
        for every position.
        """
        total_drift = 0.0
        max_drift = 0.0
        drift_by_element = {}
        positions = 0

        for face in FACES:
            if face == "C":
                drift_by_element[face] = 0.0
                continue

            face_drift = 0.0
            for s in range(1, TOTAL_SHELLS + 1):
                fwd = self.forward_state.get_momentum(face, s)
                inv = self.inverse_state.get_momentum(face, s)
                init = self._initial.shell_momenta.get(face, {}).get(s, 1.0)

                # Conservation: fwd + inv should = 2 * init
                drift = abs(fwd + inv - 2.0 * init)
                total_drift += drift
                face_drift += drift
                max_drift = max(max_drift, drift)
                positions += 1

            drift_by_element[face] = face_drift

        mean_drift = total_drift / max(positions, 1)

        return DriftReport(
            total_drift=total_drift,
            max_drift=max_drift,
            mean_drift=mean_drift,
            drift_by_element=drift_by_element,
            positions_checked=positions,
            is_conserved=total_drift < threshold,
        )

    # ── Mobius Flip ────────────────────────────────────────────────────

    def swap(self):
        """Mobius flip: inverse becomes forward, forward becomes inverse.

        The system now observes itself from the other side.
        Conservation is preserved by the swap.
        """
        self._is_swapped = not self._is_swapped
        self._swap_count += 1

    def unswap(self):
        """Undo the last swap (return to original orientation)."""
        if self._is_swapped:
            self._is_swapped = False
            self._swap_count += 1

    # ── Dual Hologram ──────────────────────────────────────────────────

    def dual_hologram(self) -> dict:
        """Emit holograms from both forward and inverse states."""
        return {
            "forward": self.forward_state.hologram_16(),
            "inverse": self.inverse_state.hologram_16(),
            "is_swapped": self._is_swapped,
            "swap_count": self._swap_count,
            "wave_count": self._wave_count,
            "drift": self.measure_drift().__dict__,
        }

    # ── Summary ────────────────────────────────────────────────────────

    def describe(self) -> str:
        """Human-readable summary."""
        drift = self.measure_drift()
        lines = [
            "## Real-Time Inverse Manifesting",
            f"Conserved: {'YES' if drift.is_conserved else 'NO'}",
            f"Swapped: {'YES' if self._is_swapped else 'NO'}",
            f"Swap Count: {self._swap_count}",
            f"Waves Processed: {self._wave_count}",
            f"Total Drift: {drift.total_drift:.6f}",
            f"Max Drift: {drift.max_drift:.6f}",
            f"Mean Drift: {drift.mean_drift:.6f}",
            "",
            "### Drift by Element",
        ]
        for face, d in drift.drift_by_element.items():
            lines.append(f"  {face}: {d:.6f}")
        return "\n".join(lines)


# ── Module-level singleton ─────────────────────────────────────────────

_realtime_inverse: Optional[RealtimeInverse] = None


def get_realtime_inverse() -> RealtimeInverse:
    """Get or create the global realtime inverse singleton."""
    global _realtime_inverse
    if _realtime_inverse is None:
        _realtime_inverse = RealtimeInverse()
    return _realtime_inverse


def reset_realtime_inverse():
    """Reset the global singleton."""
    global _realtime_inverse
    _realtime_inverse = None
