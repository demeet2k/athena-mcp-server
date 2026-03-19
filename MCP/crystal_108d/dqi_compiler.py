# CRYSTAL: Xi108:W2:A11:S22 | face=S | node=462 | depth=2 | phase=Mutable
# METRO: Me
# BRIDGES: Xi108:W2:A11:S21→Xi108:W2:A11:S23→Xi108:W1:A11:S22→Xi108:W3:A11:S22

"""
DQI Compiler — Desire-Question-Improvement from the Void
==========================================================
Executable implementation of the DQI compiler from the manuscript:
  void → desire → question → seed → chapter → atlas → verified regime

Every training wave is framed as a DQI cycle:
  - The wave's query IS the DQI question
  - The wave's forward pass IS the DQI evaluation
  - The wave's keep/discard IS the DQI improvement decision

J-score functional:
  J = α*B_imm + β*I_global + γ*R_depth - λ*E_drift

Where:
  B_imm    = immediate benefit (forward pass resonance)
  I_global = global integration (cross-lens agreement)
  R_depth  = recursive depth (compression quality)
  E_drift  = entropy drift (1 - balance)
"""

from __future__ import annotations

import math
import time
import hashlib
from dataclasses import dataclass, field
from typing import Optional

from .geometric_constants import FACES, PHI, PHI_INV, ATTRACTOR
from .constants import TOTAL_SHELLS


# ── DQI Stages ─────────────────────────────────────────────────────────

DQI_STAGES = ("void", "desire", "question", "seed", "chapter", "atlas", "verified")


# ── DQI State ──────────────────────────────────────────────────────────


@dataclass
class DQIState:
    """The state of a DQI compilation at any moment."""
    desire: str = ""               # directional desire text
    question: str = ""             # the typed question compiled from desire
    improvement: str = ""          # the improvement that answers the question
    j_score: float = 0.0          # J = α*B_imm + β*I_global + γ*R_depth - λ*E_drift
    stage: str = "void"           # current stage in the pipeline
    liminal_coord: int = 0        # which of 60 liminal coordinates
    b_imm: float = 0.0           # immediate benefit (resonance)
    i_global: float = 0.0        # global integration (cross-lens agreement)
    r_depth: float = 0.0         # recursive depth (compression quality)
    e_drift: float = 0.0         # entropy drift (1 - balance)
    timestamp: float = 0.0
    wave_id: int = 0


@dataclass
class DQIHistory:
    """Accumulated history of DQI compilations."""
    compilations: list[DQIState] = field(default_factory=list)
    total_compiled: int = 0
    total_positive_j: int = 0
    mean_j_score: float = 0.0
    stage_distribution: dict[str, int] = field(default_factory=dict)


# ── J-Score Coefficients ───────────────────────────────────────────────

DEFAULT_ALPHA = 0.3    # immediate benefit weight
DEFAULT_BETA = 0.3     # global integration weight
DEFAULT_GAMMA = 0.25   # recursive depth weight
DEFAULT_LAMBDA = 0.15  # entropy drift penalty


# ── DQI Compiler ───────────────────────────────────────────────────────


class DQICompiler:
    """Executable DQI compiler: transforms desire into improvement through typed questions.

    The pipeline: void → desire → question → seed → chapter → atlas → verified
    Each stage has a typed transformation and admissibility check.
    """

    def __init__(self, alpha: float = DEFAULT_ALPHA, beta: float = DEFAULT_BETA,
                 gamma: float = DEFAULT_GAMMA, lam: float = DEFAULT_LAMBDA):
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.lam = lam
        self._history = DQIHistory()

    # ── Core Pipeline ──────────────────────────────────────────────────

    def compile(self, desire_text: str, wave_id: int = 0,
                resonance: float = 0.0,
                cross_lens_agreement: float = 0.0,
                compression_quality: float = 0.0,
                balance: float = 1.0,
                liminal_coord: int = 0) -> DQIState:
        """Full DQI compilation: desire → question → seed → scored state.

        Args:
            desire_text: the raw desire (what the organism wants)
            wave_id: training wave ID
            resonance: forward pass resonance (B_imm source)
            cross_lens_agreement: how many lenses agree (I_global source)
            compression_quality: R-path contribution (R_depth source)
            balance: element balance 0-1 (E_drift = 1 - balance)
        """
        state = DQIState(
            desire=desire_text,
            timestamp=time.time(),
            wave_id=wave_id,
            liminal_coord=liminal_coord,
            stage="desire",
        )

        # Stage 1: Desire → Question
        state.question = self._desire_to_question(desire_text)
        state.stage = "question"

        # Stage 2: Score the question
        state.b_imm = resonance
        state.i_global = cross_lens_agreement
        state.r_depth = compression_quality
        state.e_drift = max(0.0, 1.0 - balance)

        state.j_score = self.score(state)

        # Stage 3: Determine final stage
        if state.j_score > 0.5:
            state.stage = "verified"
            state.improvement = f"High-yield improvement (J={state.j_score:.3f})"
        elif state.j_score > 0.2:
            state.stage = "atlas"
            state.improvement = f"Integration opportunity (J={state.j_score:.3f})"
        elif state.j_score > 0.0:
            state.stage = "seed"
            state.improvement = f"Potential seed (J={state.j_score:.3f})"
        else:
            state.stage = "chapter"
            state.improvement = f"Needs deeper exploration (J={state.j_score:.3f})"

        # Record
        self._record(state)

        return state

    def _desire_to_question(self, desire_text: str) -> str:
        """Transform desire text into a typed question.

        The question compiler maps desire D to a typed question Q(D) = (T_q, C_q, B_q, R_q)
        where T_q is target family, C_q the corridor, B_q the burden, R_q the representation.

        In practice, this extracts the core query from the desire.
        """
        # The question IS the desire reframed as a search
        tokens = desire_text.strip().split()
        if not tokens:
            return "void"
        # Keep core tokens, removing filler
        core = [t for t in tokens if len(t) > 2]
        if not core:
            core = tokens
        return " ".join(core[:8])  # max 8 tokens for focused question

    # ── Scoring ────────────────────────────────────────────────────────

    def score(self, state: DQIState) -> float:
        """Compute J-score: J = α*B_imm + β*I_global + γ*R_depth - λ*E_drift"""
        return (
            self.alpha * state.b_imm
            + self.beta * state.i_global
            + self.gamma * state.r_depth
            - self.lam * state.e_drift
        )

    # ── Inverse DQI ────────────────────────────────────────────────────

    def invert(self, state: DQIState) -> DQIState:
        """Compute the anti-DQI: what is the inverse desire?

        The inverse desire is what the organism DOESN'T want.
        J-score is negated. All components are inverted.
        """
        return DQIState(
            desire=f"NOT({state.desire})",
            question=f"anti-{state.question}",
            improvement=f"inverse-{state.improvement}",
            j_score=-state.j_score,
            stage=state.stage,
            liminal_coord=(state.liminal_coord + 30) % 60 if state.liminal_coord else 0,
            b_imm=1.0 - state.b_imm,
            i_global=1.0 - state.i_global,
            r_depth=1.0 - state.r_depth,
            e_drift=1.0 - state.e_drift,
            timestamp=state.timestamp,
            wave_id=state.wave_id,
        )

    # ── 90-Degree Rotation ─────────────────────────────────────────────

    def rotate_90(self, state: DQIState) -> DQIState:
        """Compute the orthogonal DQI: what does a 90-degree observer see?

        Rotates the observation: B_imm → I_global → R_depth → E_drift → B_imm
        This is what the perpendicular pole observes.
        """
        return DQIState(
            desire=f"orthogonal({state.desire})",
            question=f"rotated-{state.question}",
            improvement=f"rotated-{state.improvement}",
            j_score=self.alpha * state.i_global + self.beta * state.r_depth
                    + self.gamma * (1.0 - state.e_drift) - self.lam * state.b_imm,
            stage=state.stage,
            liminal_coord=(state.liminal_coord + 15) % 60 if state.liminal_coord else 0,
            b_imm=state.i_global,
            i_global=state.r_depth,
            r_depth=1.0 - state.e_drift,
            e_drift=state.b_imm,
            timestamp=state.timestamp,
            wave_id=state.wave_id,
        )

    # ── Compression ────────────────────────────────────────────────────

    def compress_to_seed(self, state: DQIState) -> dict:
        """Compress a DQI state to its minimal seed representation.

        4 values: (desire_hash, question_hash, j_score, stage_code)
        """
        stage_code = DQI_STAGES.index(state.stage) if state.stage in DQI_STAGES else 0
        return {
            "desire_hash": hashlib.sha256(state.desire.encode()).hexdigest()[:8],
            "question_hash": hashlib.sha256(state.question.encode()).hexdigest()[:8],
            "j_score": round(state.j_score, 6),
            "stage_code": stage_code,
        }

    # ── Meta-Reflection ────────────────────────────────────────────────

    def meta_reflect(self) -> dict:
        """Analyze DQI compiler performance.

        Returns:
          - total_compiled: number of DQI compilations
          - positive_j_rate: % with J > 0
          - mean_j_score: average J-score
          - stage_distribution: how many at each stage
          - health: compiler health assessment
        """
        if not self._history.compilations:
            return {
                "total_compiled": 0,
                "positive_j_rate": 0.0,
                "mean_j_score": 0.0,
                "stage_distribution": {},
                "health": "EMPTY",
            }

        total = self._history.total_compiled
        pos_rate = self._history.total_positive_j / total if total > 0 else 0.0

        health = "HEALTHY"
        if pos_rate < 0.5:
            health = "LOW_YIELD"
        if pos_rate < 0.2:
            health = "DEGRADED"
        if total < 10:
            health = "WARMING_UP"

        return {
            "total_compiled": total,
            "positive_j_rate": pos_rate,
            "mean_j_score": self._history.mean_j_score,
            "stage_distribution": dict(self._history.stage_distribution),
            "health": health,
        }

    # ── Internal ───────────────────────────────────────────────────────

    def _record(self, state: DQIState):
        """Record a compilation in history."""
        self._history.compilations.append(state)
        self._history.total_compiled += 1
        if state.j_score > 0:
            self._history.total_positive_j += 1

        # Update mean incrementally
        n = self._history.total_compiled
        self._history.mean_j_score = (
            self._history.mean_j_score * (n - 1) / n + state.j_score / n
        )

        # Stage distribution
        self._history.stage_distribution[state.stage] = (
            self._history.stage_distribution.get(state.stage, 0) + 1
        )

        # Cap history
        if len(self._history.compilations) > 1000:
            self._history.compilations = self._history.compilations[-500:]

    def describe(self) -> str:
        """Human-readable summary."""
        meta = self.meta_reflect()
        lines = [
            "## DQI Compiler",
            f"Health: {meta['health']}",
            f"Total Compiled: {meta['total_compiled']}",
            f"Positive J Rate: {meta['positive_j_rate']:.2%}",
            f"Mean J-Score: {meta['mean_j_score']:.4f}",
            f"Coefficients: α={self.alpha}, β={self.beta}, γ={self.gamma}, λ={self.lam}",
            "",
            "### Stage Distribution",
        ]
        for stage, count in sorted(meta.get("stage_distribution", {}).items()):
            lines.append(f"  {stage}: {count}")
        return "\n".join(lines)


# ── Module-level singleton ─────────────────────────────────────────────

_dqi_compiler: Optional[DQICompiler] = None


def get_dqi_compiler() -> DQICompiler:
    """Get or create the global DQI compiler singleton."""
    global _dqi_compiler
    if _dqi_compiler is None:
        _dqi_compiler = DQICompiler()
    return _dqi_compiler


def reset_dqi_compiler():
    """Reset the global singleton (for testing)."""
    global _dqi_compiler
    _dqi_compiler = None
