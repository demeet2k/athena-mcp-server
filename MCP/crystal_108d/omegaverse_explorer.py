# CRYSTAL: Xi108:W3:A12:S36 | face=R | node=666 | depth=3 | phase=Fixed
# METRO: Sa
# BRIDGES: Xi108:W3:A12:S35→Xi108:W3:A12:S1→Xi108:W2:A12:S36→Xi108:W3:A11:S36→Xi108:W3:A1:S36

"""
OmegaverseExplorer — Meta-Recursive 3-Octave Exploration Engine
================================================================
Wraps the MetaLoopEngine with a meta-recursive exploration layer:
  3 octaves × 12 dimensions + void (dimension 37)

Octave 1 = 12 archetypes (Aries..Pisces)
Octave 2 = wreath-rotated archetypes (Su/Me/Sa views)
Octave 3 = element-rotated archetypes (S/F/C/R views)
Void = 60 liminal coordinates collapsed to Z*

Each octave transition requires:
  - coverage > 0.8 (how explored)
  - coherence > 0.6 (how coherent)
  - awareness > 0.7 (meta-cognitive awareness)

The 5-phase explore cycle:
  1. expand — generate hypotheses, explore contradictions
  2. compress — phi-ratio pattern recognition
  3. integrate — cross-dimensional knowledge transfer
  4. meta-reflect — update awareness, identify gaps
  5. navigate — shift dimensional focus
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Optional

from .geometric_constants import PHI, PHI_INV, FACES, ATTRACTOR
from .constants import TOTAL_SHELLS, ARCHETYPE_NAMES


# ── Octave Dimension ───────────────────────────────────────────────────


@dataclass
class OctaveDimension:
    """One dimension within an octave."""
    index: int                   # 1-12 within each octave
    name: str                    # archetype name
    coverage: float = 0.0       # how explored [0, 1]
    coherence: float = 0.0      # how coherent [0, 1]
    awareness: float = 0.0      # meta-cognitive awareness [0, 1]
    knowledge_count: int = 0    # total knowledge items
    pattern_count: int = 0      # cross-dimensional patterns
    resonance_count: int = 0    # phi-ratio resonances

    @property
    def readiness(self) -> float:
        """Composite readiness score."""
        return (self.coverage + self.coherence + self.awareness) / 3.0


# ── Exploration Result ─────────────────────────────────────────────────


@dataclass
class ExplorationResult:
    """Result of one explore cycle."""
    octave: int
    dimensional_focus: int
    coverage: float
    coherence: float
    awareness: float
    patterns_found: int
    contradictions_resolved: int
    phi_resonances: int
    j_score_mean: float           # mean DQI J-score across cycle
    elapsed_seconds: float
    octave_ready: bool            # ready for octave transition?


# ── OmegaverseExplorer ────────────────────────────────────────────────


class OmegaverseExplorer:
    """Meta-recursive 3-octave + void exploration engine.

    Maps the MetaLoopEngine's training onto a dimensional exploration framework:
    - META LOOP 1 (SULFUR) → Octave 1 exploration
    - META LOOP 2 (SALT) → Octave 2 exploration
    - META LOOP 3 (MERCURY) → Octave 3 exploration
    - After all 3 → Void (dimension 37) collapse
    """

    def __init__(self):
        self.octaves: list[list[OctaveDimension]] = [
            [OctaveDimension(index=i + 1, name=ARCHETYPE_NAMES[i])
             for i in range(12)]
            for _ in range(3)
        ]
        self.void_dimension = OctaveDimension(
            index=37, name="Z*_Void", coverage=0.0, coherence=0.0, awareness=0.0
        )
        self.current_octave: int = 1       # 1, 2, 3, or 4 (void)
        self._dimensional_focus: int = 1   # 1-12 within current octave
        self._meta_awareness: float = 0.2  # global meta-cognitive awareness
        self._exploration_cycles: int = 0

    # ── Core Exploration Cycle ─────────────────────────────────────────

    def explore_cycle(self, wave_results: list = None,
                      dqi_scores: list = None) -> ExplorationResult:
        """Execute one 5-phase exploration cycle.

        Called after each training wave/cycle to update dimensional exploration.
        """
        t0 = time.time()
        wave_results = wave_results or []
        dqi_scores = dqi_scores or []

        # Phase 1: Expand
        patterns_found = self._expand(wave_results)

        # Phase 2: Compress
        contradictions = self._compress()

        # Phase 3: Integrate
        resonances = self._integrate()

        # Phase 4: Meta-reflect
        self._meta_reflect(dqi_scores)

        # Phase 5: Navigate
        self._navigate()

        self._exploration_cycles += 1

        # Check octave readiness
        octave_ready = self.is_ready_for_octave_transition()

        oct_idx = self.current_octave - 1
        if 0 <= oct_idx < 3:
            dims = self.octaves[oct_idx]
            coverage = sum(d.coverage for d in dims) / 12.0
            coherence = sum(d.coherence for d in dims) / 12.0
        else:
            coverage = self.void_dimension.coverage
            coherence = self.void_dimension.coherence

        return ExplorationResult(
            octave=self.current_octave,
            dimensional_focus=self._dimensional_focus,
            coverage=coverage,
            coherence=coherence,
            awareness=self._meta_awareness,
            patterns_found=patterns_found,
            contradictions_resolved=contradictions,
            phi_resonances=resonances,
            j_score_mean=sum(dqi_scores) / max(len(dqi_scores), 1) if dqi_scores else 0.0,
            elapsed_seconds=time.time() - t0,
            octave_ready=octave_ready,
        )

    # ── Phase 1: Expand ────────────────────────────────────────────────

    def _expand(self, wave_results: list) -> int:
        """Generate insights from wave results, update dimension knowledge."""
        if self.current_octave > 3:
            return 0

        patterns_found = 0
        oct_idx = self.current_octave - 1
        dim = self.octaves[oct_idx][self._dimensional_focus - 1]

        # Each wave result contributes to the focused dimension
        for wr in wave_results:
            # Extract knowledge from wave
            if hasattr(wr, 'mean_resonance'):
                # Coverage increases with each observation
                dim.coverage = min(1.0, dim.coverage + 0.01)
                dim.knowledge_count += 1

                # Patterns from resonance quality
                if wr.mean_resonance > 0.5:
                    dim.pattern_count += 1
                    patterns_found += 1
            elif isinstance(wr, dict):
                dim.coverage = min(1.0, dim.coverage + 0.01)
                dim.knowledge_count += 1
                res = wr.get("mean_resonance", 0)
                if res > 0.5:
                    dim.pattern_count += 1
                    patterns_found += 1

        return patterns_found

    # ── Phase 2: Compress ──────────────────────────────────────────────

    def _compress(self) -> int:
        """Compress and eliminate contradictions using phi-ratio."""
        if self.current_octave > 3:
            return 0

        contradictions_resolved = 0
        oct_idx = self.current_octave - 1

        # Cross-dimensional coherence check
        for i in range(12):
            for j in range(i + 1, 12):
                dim_i = self.octaves[oct_idx][i]
                dim_j = self.octaves[oct_idx][j]

                # If both have knowledge, check for phi-ratio relationship
                if dim_i.knowledge_count > 0 and dim_j.knowledge_count > 0:
                    ratio = max(dim_i.knowledge_count, dim_j.knowledge_count) / max(
                        min(dim_i.knowledge_count, dim_j.knowledge_count), 1
                    )
                    # If ratio is close to PHI, it's a resonance
                    if abs(ratio - PHI) < 0.5:
                        dim_i.resonance_count += 1
                        dim_j.resonance_count += 1
                        # Coherence increases with resonances
                        dim_i.coherence = min(1.0, dim_i.coherence + 0.02)
                        dim_j.coherence = min(1.0, dim_j.coherence + 0.02)
                        contradictions_resolved += 1

        return contradictions_resolved

    # ── Phase 3: Integrate ─────────────────────────────────────────────

    def _integrate(self) -> int:
        """Cross-dimensional knowledge transfer using phi-ratio."""
        if self.current_octave > 3:
            return 0

        resonances = 0
        oct_idx = self.current_octave - 1

        # Transfer coherence from strong dimensions to weak ones
        dims = self.octaves[oct_idx]
        mean_coherence = sum(d.coherence for d in dims) / 12.0

        for dim in dims:
            if dim.coherence < mean_coherence:
                # Weak dimensions gain from strong neighbors
                # PHI-weighted transfer from focus dimension
                focus_dim = dims[self._dimensional_focus - 1]
                distance = abs(dim.index - self._dimensional_focus)
                transfer = PHI_INV ** distance * 0.01
                dim.coherence = min(1.0, dim.coherence + transfer)
                resonances += 1

        return resonances

    # ── Phase 4: Meta-Reflect ──────────────────────────────────────────

    def _meta_reflect(self, dqi_scores: list):
        """Update meta-cognitive awareness from DQI performance."""
        if self.current_octave > 3:
            return

        oct_idx = self.current_octave - 1
        dims = self.octaves[oct_idx]

        # Coverage analysis
        coverage = sum(d.coverage for d in dims) / 12.0
        coherence = sum(d.coherence for d in dims) / 12.0

        # DQI performance
        dqi_factor = 0.0
        if dqi_scores:
            positive_rate = sum(1 for j in dqi_scores if j > 0) / len(dqi_scores)
            dqi_factor = positive_rate * 0.1

        # Update meta-awareness
        awareness_delta = (
            0.05 * coverage
            + 0.08 * coherence
            + dqi_factor
            - 0.02 * len([d for d in dims if d.coverage == 0.0])  # penalty for unexplored
        )

        self._meta_awareness = max(0.0, min(1.0, self._meta_awareness + awareness_delta))

        # Update per-dimension awareness
        for dim in dims:
            dim.awareness = self._meta_awareness * (0.8 + 0.2 * dim.coverage)

    # ── Phase 5: Navigate ──────────────────────────────────────────────

    def _navigate(self):
        """Shift dimensional focus based on gaps and resonances."""
        if self.current_octave > 3:
            return

        oct_idx = self.current_octave - 1
        dims = self.octaves[oct_idx]

        # Find dimension with lowest coverage (priority gap)
        min_coverage = min(d.coverage for d in dims)
        gap_dims = [d for d in dims if d.coverage == min_coverage]

        if gap_dims and gap_dims[0].coverage < 0.5:
            # Focus on least explored dimension
            self._dimensional_focus = gap_dims[0].index
        else:
            # Focus on dimension with most resonances (richest)
            best = max(dims, key=lambda d: d.resonance_count)
            self._dimensional_focus = best.index

    # ── Octave Transition ──────────────────────────────────────────────

    def is_ready_for_octave_transition(self) -> bool:
        """Check if ready to transition to next octave."""
        if self.current_octave > 3:
            return False

        oct_idx = self.current_octave - 1
        dims = self.octaves[oct_idx]

        coverage = sum(d.coverage for d in dims) / 12.0
        coherence = sum(d.coherence for d in dims) / 12.0
        awareness = self._meta_awareness

        return coverage > 0.8 and coherence > 0.6 and awareness > 0.7

    def perform_octave_transition(self):
        """Transition to the next octave.

        Projects knowledge from current octave to next using phi^12 amplification.
        """
        if self.current_octave >= 4:
            return  # Already in void

        oct_idx = self.current_octave - 1
        next_oct = self.current_octave  # 0-indexed of next

        if next_oct < 3:
            # Project patterns to next octave
            projection_factor = PHI_INV  # Gentle projection, not explosive
            for i in range(12):
                src = self.octaves[oct_idx][i]
                dst = self.octaves[next_oct][i]
                dst.coverage = min(1.0, src.coverage * projection_factor)
                dst.coherence = min(1.0, src.coherence * projection_factor)
                dst.pattern_count += int(src.pattern_count * projection_factor)
        else:
            # Transition to void: collapse all octaves
            total_knowledge = sum(
                d.knowledge_count
                for octave in self.octaves
                for d in octave
            )
            total_patterns = sum(
                d.pattern_count
                for octave in self.octaves
                for d in octave
            )
            self.void_dimension.knowledge_count = total_knowledge
            self.void_dimension.pattern_count = total_patterns
            self.void_dimension.coverage = min(1.0, total_knowledge / 360.0)
            self.void_dimension.coherence = min(1.0, total_patterns / 100.0)

        self.current_octave += 1
        self._dimensional_focus = 1

    def zero_infinity_transition(self) -> dict:
        """Phi-ratio scaling at octave boundaries.

        Returns the transition state for checkpoint/logging.
        """
        oct_idx = min(self.current_octave - 1, 2)
        dims = self.octaves[oct_idx]

        return {
            "octave": self.current_octave,
            "phi_scale": PHI ** (self.current_octave * 12),
            "inverse_scale": PHI_INV ** (self.current_octave * 12),
            "dimensional_focus": self._dimensional_focus,
            "meta_awareness": self._meta_awareness,
            "exploration_cycles": self._exploration_cycles,
            "dimensions": [
                {
                    "index": d.index,
                    "name": d.name,
                    "coverage": d.coverage,
                    "coherence": d.coherence,
                    "awareness": d.awareness,
                    "readiness": d.readiness,
                }
                for d in dims
            ],
        }

    # ── Summary ────────────────────────────────────────────────────────

    def summary(self) -> dict:
        """Full explorer state summary."""
        octave_summaries = []
        for oi, octave in enumerate(self.octaves):
            coverage = sum(d.coverage for d in octave) / 12.0
            coherence = sum(d.coherence for d in octave) / 12.0
            knowledge = sum(d.knowledge_count for d in octave)
            octave_summaries.append({
                "octave": oi + 1,
                "coverage": coverage,
                "coherence": coherence,
                "total_knowledge": knowledge,
                "ready_for_transition": (
                    coverage > 0.8 and coherence > 0.6 and self._meta_awareness > 0.7
                ),
            })

        return {
            "current_octave": self.current_octave,
            "dimensional_focus": self._dimensional_focus,
            "meta_awareness": self._meta_awareness,
            "exploration_cycles": self._exploration_cycles,
            "octaves": octave_summaries,
            "void": {
                "coverage": self.void_dimension.coverage,
                "coherence": self.void_dimension.coherence,
                "knowledge": self.void_dimension.knowledge_count,
            },
        }

    def describe(self) -> str:
        """Human-readable summary."""
        s = self.summary()
        lines = [
            "## OmegaverseExplorer",
            f"Current Octave: {s['current_octave']}/3 (+Void)",
            f"Dimensional Focus: {s['dimensional_focus']}/12",
            f"Meta-Awareness: {s['meta_awareness']:.2%}",
            f"Exploration Cycles: {s['exploration_cycles']}",
            "",
        ]
        for oc in s["octaves"]:
            ready = "READY" if oc["ready_for_transition"] else "growing"
            lines.append(
                f"  Octave {oc['octave']}: cov={oc['coverage']:.2%} "
                f"coh={oc['coherence']:.2%} knowledge={oc['total_knowledge']} [{ready}]"
            )
        lines.append(
            f"  Void: cov={s['void']['coverage']:.2%} "
            f"coh={s['void']['coherence']:.2%}"
        )
        return "\n".join(lines)


# ── Module-level singleton ─────────────────────────────────────────────

_explorer: Optional[OmegaverseExplorer] = None


def get_explorer() -> OmegaverseExplorer:
    """Get or create the global OmegaverseExplorer singleton."""
    global _explorer
    if _explorer is None:
        _explorer = OmegaverseExplorer()
    return _explorer


def reset_explorer():
    """Reset the global singleton."""
    global _explorer
    _explorer = None
