# CRYSTAL: Xi108:W3:A11:S33 | face=R | node=594 | depth=3 | phase=Cardinal
# METRO: Sa
# BRIDGES: Xi108:W3:A11:S32→Xi108:W3:A11:S34→Xi108:W2:A11:S33→Xi108:W3:A10:S33→Xi108:W3:A12:S33

"""
Inverse Engine — Real-Time Forward-Inverse Recording & Replay
===============================================================
For every forward operation F, simultaneously computes and stores F^{-1}.
The inverse is not metaphor — it is mathematical: every +delta has a -delta
recorded in a ring buffer that can be replayed to reconstruct the mirror state.

InverseRecord: one recorded mutation and its inverse.
InverseEngine: wraps MomentumField, intercepts updates, stores inverse ring.

Conservation law: forward_state + inverse_state should sum to the initial state.
Any drift indicates a conservation violation.

This module bridges the organism from 3D to 4D by making the inverse dimension
explicit and live, not implicit and static.
"""

from __future__ import annotations

import time
import hashlib
import json
from collections import deque
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

from .momentum_field import MomentumField, MomentumState, get_momentum_field
from .geometric_constants import FACES, ATTRACTOR
from .constants import TOTAL_SHELLS
from ._cache import DATA_DIR


INVERSE_STATE_FILE = DATA_DIR / "inverse_engine_state.json"


# ── Inverse Record ─────────────────────────────────────────────────────


@dataclass
class InverseRecord:
    """One recorded mutation and its exact mathematical inverse."""
    timestamp: float
    operation: str           # "momentum_update", "dimension_update", "invert_and_balance"
    face: str                # S, F, C, R
    shell: int               # 1-36 (0 for dimension-level ops)
    delta: float             # the forward delta applied
    inverse_delta: float     # -delta (the exact inverse)
    lr: float                # learning rate used
    wave_id: int             # which training wave produced this
    liminal_coord: int       # which of 60 liminal coordinates this maps to (0 = unmapped)
    pole_angle: float        # 0, 90, 180, 270 — which observation pole

    @property
    def is_valid(self) -> bool:
        """Inverse fidelity check: inverse_delta must equal -delta."""
        return abs(self.inverse_delta + self.delta) < 1e-12


# ── Pole Angle Mapping ─────────────────────────────────────────────────

_FACE_TO_POLE = {
    "S": 0.0,     # Earth — forward axis
    "F": 90.0,    # Fire — 90-degree rotation
    "C": 180.0,   # Water — inversion (anti-pole)
    "R": 270.0,   # Air — 270-degree (orthogonal to Fire)
}

_FACE_TO_ORTHOGONAL = {
    "S": "C",   # S-F plane -> orthogonal observation on C-R plane
    "F": "R",
    "C": "S",
    "R": "F",
}


def _pole_angle(face: str) -> float:
    """Get the pole angle for a face."""
    return _FACE_TO_POLE.get(face, 0.0)


def _orthogonal_face(face: str) -> str:
    """Get the orthogonal face (90-degree pole observation)."""
    return _FACE_TO_ORTHOGONAL.get(face, "S")


# ── Liminal Coordinate Mapping ─────────────────────────────────────────

def _face_to_liminal_base(face: str) -> int:
    """Map face to base liminal coordinate (SR orbit, solo mask)."""
    return {"S": 1, "F": 2, "C": 3, "R": 4}.get(face, 1)


# ── Inverse Engine ─────────────────────────────────────────────────────


class InverseEngine:
    """Wraps MomentumField to intercept all mutations and record their inverses.

    The ring buffer stores the last `max_records` inverse records.
    At any moment, manifest_inverse(wave_id) replays the exact inverse of wave N.
    """

    def __init__(self, momentum: MomentumField = None, max_records: int = 10_000):
        self.momentum = momentum or get_momentum_field()
        self._ring: deque[InverseRecord] = deque(maxlen=max_records)
        self._initial_snapshot: Optional[MomentumState] = None
        self._wave_index: dict[int, list[int]] = {}  # wave_id -> [ring indices]
        self._total_recorded: int = 0
        self._total_fidelity_checks: int = 0
        self._fidelity_passes: int = 0

    def capture_initial(self):
        """Take a snapshot of the initial state for conservation checking."""
        self._initial_snapshot = self.momentum.snapshot()

    # ── Recording ──────────────────────────────────────────────────────

    def record_update(self, face: str, shell: int, delta: float,
                      lr: float, wave_id: int = 0):
        """Record a momentum update and its inverse.

        Called after MomentumField.update_momentum().
        """
        record = InverseRecord(
            timestamp=time.time(),
            operation="momentum_update",
            face=face,
            shell=shell,
            delta=delta,
            inverse_delta=-delta,
            lr=lr,
            wave_id=wave_id,
            liminal_coord=_face_to_liminal_base(face),
            pole_angle=_pole_angle(face),
        )
        idx = len(self._ring)
        self._ring.append(record)

        # Index by wave
        if wave_id not in self._wave_index:
            self._wave_index[wave_id] = []
        self._wave_index[wave_id].append(idx)

        self._total_recorded += 1

    def record_dimension_update(self, dimension: str, delta: float,
                                lr: float, wave_id: int = 0):
        """Record a dimension-level momentum update."""
        face = {"D1_Earth": "S", "D2_Fire": "F", "D3_Water": "C", "D4_Air": "R"}.get(
            dimension, "S"
        )
        record = InverseRecord(
            timestamp=time.time(),
            operation="dimension_update",
            face=face,
            shell=0,
            delta=delta,
            inverse_delta=-delta,
            lr=lr,
            wave_id=wave_id,
            liminal_coord=_face_to_liminal_base(face),
            pole_angle=_pole_angle(face),
        )
        self._ring.append(record)
        self._total_recorded += 1

    def record_balance(self, face: str, shell: int, old_val: float,
                       new_val: float, wave_id: int = 0):
        """Record an invert-and-balance operation."""
        delta = new_val - old_val
        record = InverseRecord(
            timestamp=time.time(),
            operation="invert_and_balance",
            face=face,
            shell=shell,
            delta=delta,
            inverse_delta=-delta,
            lr=0.0,
            wave_id=wave_id,
            liminal_coord=_face_to_liminal_base(face),
            pole_angle=_pole_angle(face),
        )
        self._ring.append(record)
        self._total_recorded += 1

    # ── Inverse Manifesting ────────────────────────────────────────────

    def manifest_inverse(self, wave_id: int) -> list[InverseRecord]:
        """Retrieve all inverse records for a given wave.

        These can be replayed to reconstruct the mirror state.
        """
        indices = self._wave_index.get(wave_id, [])
        records = []
        for idx in indices:
            if idx < len(self._ring):
                records.append(self._ring[idx])
        return records

    def replay_inverse(self, wave_id: int):
        """Actually replay the inverse of a wave — apply -delta for every +delta.

        This mutates the momentum field to undo wave N.
        """
        for record in self.manifest_inverse(wave_id):
            if record.face == "C":
                continue  # Water locked
            if record.operation == "momentum_update" and record.shell > 0:
                self.momentum.update_momentum(
                    record.face, record.shell,
                    record.inverse_delta, record.lr
                )
            elif record.operation == "dimension_update":
                face_num = {"S": 1, "F": 2, "C": 3, "R": 4}[record.face]
                face_name = {"S": "Earth", "F": "Fire", "C": "Water", "R": "Air"}[record.face]
                self.momentum.update_dimension_momentum(
                    f"D{face_num}_{face_name}",
                    record.inverse_delta, record.lr
                )

    def get_inverse_state(self) -> dict[str, dict[int, float]]:
        """Compute the full inverse momentum state.

        For every recorded delta, accumulate the inverse.
        Start from the initial snapshot and apply all inverse deltas.
        """
        if self._initial_snapshot is None:
            return {}

        inverse_momenta = {
            face: dict(shells)
            for face, shells in self._initial_snapshot.shell_momenta.items()
        }

        for record in self._ring:
            if record.face == "C":
                continue
            if record.operation == "momentum_update" and record.shell > 0:
                if record.face in inverse_momenta and record.shell in inverse_momenta[record.face]:
                    inverse_momenta[record.face][record.shell] += record.lr * record.inverse_delta

        return inverse_momenta

    # ── Hologram ───────────────────────────────────────────────────────

    def inverse_hologram_16(self) -> dict:
        """Compress the inverse record buffer to 16 values.

        4 elements x 4 properties:
          - net_inverse_delta: sum of all inverse deltas for this element
          - mean_pole_angle: mean observation pole
          - fidelity: % of records with valid inverses
          - coverage: how many shells had inverse records
        """
        result = {}
        for face in FACES:
            face_records = [r for r in self._ring if r.face == face]
            if not face_records:
                result[face] = {
                    "net_inverse_delta": 0.0,
                    "mean_pole_angle": _pole_angle(face),
                    "fidelity": 1.0,
                    "coverage": 0.0,
                }
                continue

            net_delta = sum(r.inverse_delta for r in face_records)
            mean_pole = sum(r.pole_angle for r in face_records) / len(face_records)
            valid = sum(1 for r in face_records if r.is_valid)
            fidelity = valid / len(face_records) if face_records else 1.0
            shells_touched = len(set(r.shell for r in face_records if r.shell > 0))
            coverage = shells_touched / TOTAL_SHELLS

            result[face] = {
                "net_inverse_delta": net_delta,
                "mean_pole_angle": mean_pole,
                "fidelity": fidelity,
                "coverage": coverage,
            }
        return result

    # ── Self-Diagnostics ───────────────────────────────────────────────

    def self_diagnose(self) -> dict:
        """Check inverse engine health.

        Returns:
          - fidelity: % of records where inverse_delta == -delta
          - conservation_drift: |forward + inverse - initial| (should be ~0)
          - coverage: % of element-shells with inverse records
          - total_recorded: total inverse records
        """
        if not self._ring:
            return {
                "fidelity": 1.0,
                "conservation_drift": 0.0,
                "coverage": 0.0,
                "total_recorded": 0,
                "health": "EMPTY",
            }

        # Fidelity check
        valid = sum(1 for r in self._ring if r.is_valid)
        fidelity = valid / len(self._ring)

        # Conservation drift
        drift = 0.0
        if self._initial_snapshot is not None:
            initial = self._initial_snapshot
            for face in FACES:
                if face == "C":
                    continue
                for s in range(1, TOTAL_SHELLS + 1):
                    init_val = initial.shell_momenta.get(face, {}).get(s, 1.0)
                    current_val = self.momentum.get_momentum(face, s)
                    # Sum of forward deltas for this position
                    forward_deltas = sum(
                        r.lr * r.delta
                        for r in self._ring
                        if r.face == face and r.shell == s
                        and r.operation == "momentum_update"
                    )
                    # Expected: current = init + sum(forward_deltas)
                    # Drift = actual - expected
                    expected = init_val + forward_deltas
                    drift += abs(current_val - expected)

        # Coverage
        shells_with_records = set()
        for r in self._ring:
            if r.shell > 0:
                shells_with_records.add((r.face, r.shell))
        max_positions = len(FACES) * TOTAL_SHELLS
        coverage = len(shells_with_records) / max_positions

        health = "HEALTHY"
        if fidelity < 0.99:
            health = "DEGRADED"
        if drift > 0.01:
            health = "DRIFT"
        if coverage < 0.1:
            health = "LOW_COVERAGE"

        return {
            "fidelity": fidelity,
            "conservation_drift": drift,
            "coverage": coverage,
            "total_recorded": self._total_recorded,
            "buffer_size": len(self._ring),
            "waves_indexed": len(self._wave_index),
            "health": health,
        }

    # ── Persistence ────────────────────────────────────────────────────

    def save(self, path: Optional[Path] = None):
        """Save inverse engine state."""
        path = path or INVERSE_STATE_FILE
        data = {
            "type": "inverse_engine_state",
            "total_recorded": self._total_recorded,
            "buffer_size": len(self._ring),
            "hologram_16": self.inverse_hologram_16(),
            "diagnostics": self.self_diagnose(),
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def describe(self) -> str:
        """Human-readable summary."""
        diag = self.self_diagnose()
        holo = self.inverse_hologram_16()
        lines = [
            "## Inverse Engine",
            f"Health: {diag['health']}",
            f"Fidelity: {diag['fidelity']:.4f}",
            f"Conservation Drift: {diag['conservation_drift']:.6f}",
            f"Coverage: {diag['coverage']:.2%}",
            f"Total Recorded: {diag['total_recorded']}",
            f"Buffer Size: {diag['buffer_size']}",
            "",
            "### Inverse Hologram (16 values)",
        ]
        for face, vals in holo.items():
            lines.append(
                f"  {face}: net_inv={vals['net_inverse_delta']:.4f}, "
                f"pole={vals['mean_pole_angle']:.0f}°, "
                f"fidelity={vals['fidelity']:.4f}, "
                f"coverage={vals['coverage']:.2%}"
            )
        return "\n".join(lines)


# ── Module-level singleton ─────────────────────────────────────────────

_inverse_engine: Optional[InverseEngine] = None


def get_inverse_engine() -> InverseEngine:
    """Get or create the global inverse engine singleton."""
    global _inverse_engine
    if _inverse_engine is None:
        _inverse_engine = InverseEngine()
        _inverse_engine.capture_initial()
    return _inverse_engine


def reset_inverse_engine():
    """Reset the global singleton (for testing)."""
    global _inverse_engine
    _inverse_engine = None
