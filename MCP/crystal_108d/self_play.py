"""
Self-Play Loop — Iterative Weight Refinement via Meta-Observer
================================================================
The neural network refines its own crystal-internal weights by:
  1. Querying itself (from corpus, zero-point, or cross-element sources)
  2. Running a forward pass with current weights
  3. Observing output quality in 12D via the meta-observer
  4. Computing weight gradients from 12D scores
  5. Committing improved weights or discarding (keep/discard protocol)

The 57-cycle super-structure covers all 12 archetypes across 3 wreaths,
with SFCR lens rotation every ~14 cycles. Configurable for longer runs
(57-570 cycles) with checkpoint/resume support.
"""

from __future__ import annotations

import json
import math
import random
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

from .crystal_weights import (
    FractalWeightStore,
    get_store,
    ELEMENT_TO_FACE,
    FACE_TO_ELEMENT,
    CHECKPOINT_DIR,
    PHI_INV,
)
from .neural_engine import (
    CrystalNeuralEngine,
    ForwardResult,
    ResonanceComputer,
    get_engine,
)
from .constants import (
    TOTAL_SHELLS,
    ARCHETYPE_NAMES,
    LENS_CODES,
)

# SFCR lens rotation order
LENS_ORDER = ["S", "F", "C", "R"]

# 12D dimension names (matching meta_observer_runtime.py)
DIM_NAMES = [
    "x1_structure", "x2_semantics", "x3_coordination", "x4_recursion",
    "x5_contradiction", "x6_emergence", "x7_legibility", "x8_routing",
    "x9_grounding", "x10_compression", "x11_interop", "x12_potential",
]

# Which 12D dimensions couple to which weight types
DIM_TO_WEIGHT_MAP = {
    "x1_structure": "gate",       # structure → gate matrix weights
    "x2_semantics": "pair",       # semantics → pair relevance
    "x3_coordination": "bridge",  # coordination → cross-element bridges
    "x4_recursion": "gate",       # recursion → gate transitions
    "x5_contradiction": "gate",   # contradiction → gate conflicts
    "x6_emergence": "bridge",     # emergence → cross-element connections
    "x7_legibility": "pair",      # legibility → pair clarity
    "x8_routing": "gate",         # routing → gate routing
    "x9_grounding": "pair",       # grounding → pair evidence
    "x10_compression": "seed",    # compression → seed fidelity
    "x11_interop": "bridge",      # interop → cross-element bridges
    "x12_potential": "seed",      # potential → seed growth
}

# Element lens emphasis (from meta_observer_runtime.py)
ELEMENT_LENS_WEIGHTS = {
    "S": {"x1_structure": 1.5, "x7_legibility": 1.3, "x8_routing": 1.2, "x10_compression": 1.1, "x11_interop": 1.2},
    "F": {"x5_contradiction": 1.5, "x3_coordination": 1.3, "x4_recursion": 1.2, "x9_grounding": 1.4},
    "C": {"x2_semantics": 1.3, "x3_coordination": 1.2, "x6_emergence": 1.5, "x11_interop": 1.1, "x12_potential": 1.3},
    "R": {"x2_semantics": 1.2, "x4_recursion": 1.4, "x6_emergence": 1.3, "x10_compression": 1.5, "x12_potential": 1.4},
}


@dataclass
class SelfPlayConfig:
    """Configuration for a self-play run."""
    total_cycles: int = 57
    cycles_per_checkpoint: int = 10
    base_lr: float = 0.01
    lr_schedule: str = "cosine"     # "cosine", "linear", "constant"
    lens_rotation_period: int = 14  # rotate S→F→C→R every N cycles
    min_resonance_threshold: float = 0.3
    max_time_minutes: int = 30
    query_source: str = "mixed"     # "corpus", "zero_point", "mixed"
    seed: int = 42


@dataclass
class CycleResult:
    """Result of a single self-play cycle."""
    cycle_id: int
    query: str
    lens: str
    resonance: float
    resonance_prev: float
    outcome: str          # "keep", "discard", "neutral"
    dim_scores: dict      # 12D observation scores
    weight_deltas: dict   # which weights changed and by how much
    elapsed_ms: float


@dataclass
class SelfPlayReport:
    """Summary of a complete self-play run."""
    total_cycles: int
    kept: int
    discarded: int
    neutral: int
    initial_resonance: float
    final_resonance: float
    resonance_improvement: float
    best_resonance: float
    best_cycle: int
    lens_distribution: dict       # {"S": 14, "F": 14, ...}
    weight_updates: int
    elapsed_seconds: float
    cycle_history: list[dict]


# ── Query generation ─────────────────────────────────────────────────


def _generate_queries(store: FractalWeightStore, config: SelfPlayConfig) -> list[str]:
    """Generate queries for self-play from the corpus."""
    docs = store.doc_registry
    if not docs:
        return ["seed kernel", "crystal structure", "neural network", "consciousness"]

    rng = random.Random(config.seed)
    queries = []

    if config.query_source in ("corpus", "mixed"):
        # Token-based queries from document corpus
        for doc in docs:
            tokens = doc.get("tokens", [])
            if len(tokens) >= 3:
                # Sample 2-4 tokens as a query
                n = min(rng.randint(2, 4), len(tokens))
                sample = rng.sample(tokens, n)
                queries.append(" ".join(sample))

    if config.query_source in ("zero_point", "mixed"):
        # Zero-point queries (convergence zones)
        zero_queries = [
            "seed proof memory governance",
            "compression recursion void collapse",
            "emergence transformation crystal",
            "structure address admissibility law",
            "observation multiplicity fiber",
            "transport routing metro bridge",
            "archetype shell wreath phase",
            "golden resonance harmonic balance",
            "angel self-model consciousness",
            "manuscript generation protocol",
            "holographic projection seed equation",
            "conservation invariant symmetry",
        ]
        queries.extend(zero_queries)

    rng.shuffle(queries)
    return queries


# ── 12D observation scoring ──────────────────────────────────────────


def _score_12d(result: ForwardResult, lens: str) -> dict[str, float]:
    """Compute 12D observation scores from a forward pass result.

    This is the self-play's internal observer — it scores the quality
    of the engine's output without needing the full MetaObserver runtime.
    """
    scores = {}
    candidates = result.candidates

    if not candidates:
        return {dim: 0.2 for dim in DIM_NAMES}

    # x1_structure: are results structurally diverse? (gate coverage)
    gates_seen = set(c.gate for c in candidates)
    scores["x1_structure"] = min(len(gates_seen) / 8.0, 1.0)

    # x2_semantics: do results have high token overlap with query?
    avg_desire = sum(c.desire for c in candidates) / len(candidates)
    scores["x2_semantics"] = min(avg_desire * 1.5, 1.0)

    # x3_coordination: are SFCR paths in agreement?
    top = candidates[0]
    path_vals = list(top.path_contributions.values())
    if path_vals:
        path_std = _std(path_vals)
        scores["x3_coordination"] = max(0.0, 1.0 - path_std * 3)
    else:
        scores["x3_coordination"] = 0.5

    # x4_recursion: does the engine improve on previous results? (based on resonance)
    scores["x4_recursion"] = min(result.resonance * 1.5, 1.0)

    # x5_contradiction: any conflicting signals?
    elements_seen = set(c.element for c in candidates)
    # More elements = less contradiction (diverse but coherent)
    scores["x5_contradiction"] = min(len(elements_seen) / 3.0, 1.0)

    # x6_emergence: novel cross-element pairs?
    cross_pairs = len(result.cross_element_pairs_used)
    scores["x6_emergence"] = min(cross_pairs / 10.0, 1.0)

    # x7_legibility: are results well-formed? (have names, elements, gates)
    well_formed = sum(1 for c in candidates if c.doc_name and c.element and c.gate)
    scores["x7_legibility"] = well_formed / max(len(candidates), 1)

    # x8_routing: is the ranking smooth? (no huge gaps in action values)
    if len(candidates) > 1:
        actions = [c.action for c in candidates]
        action_range = max(actions) - min(actions)
        scores["x8_routing"] = max(0.0, 1.0 - action_range * 2)
    else:
        scores["x8_routing"] = 0.5

    # x9_grounding: resonance passes threshold?
    scores["x9_grounding"] = 1.0 if result.committed else 0.3

    # x10_compression: seed-based path (R) contributes meaningfully?
    if candidates:
        r_score = candidates[0].path_contributions.get("R", 0.0)
        scores["x10_compression"] = min(r_score * 2, 1.0)
    else:
        scores["x10_compression"] = 0.3

    # x11_interop: cross-element bridges actually used?
    scores["x11_interop"] = min(cross_pairs / 5.0, 1.0)

    # x12_potential: top result has high desire (future leverage)?
    if candidates:
        scores["x12_potential"] = min(candidates[0].desire * 2, 1.0)
    else:
        scores["x12_potential"] = 0.3

    # Apply lens weighting
    lens_weights = ELEMENT_LENS_WEIGHTS.get(lens, {})
    for dim, weight in lens_weights.items():
        if dim in scores:
            scores[dim] = min(scores[dim] * weight, 1.0)

    return scores


def _std(values: list[float]) -> float:
    """Compute standard deviation."""
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    return math.sqrt(sum((v - mean) ** 2 for v in values) / (len(values) - 1))


# ── Weight refinement ────────────────────────────────────────────────


def _compute_weight_deltas(
    dim_scores: dict[str, float],
    result: ForwardResult,
    store: FractalWeightStore,
    lr: float,
    lens: str,
) -> dict:
    """Map 12D observation scores to weight adjustments.

    Returns dict of {weight_type: {coordinate: delta}}.
    """
    deltas = {"gate": {}, "seed": {}, "bridge": {}}

    for dim_name, score in dim_scores.items():
        # Gradient: how far from optimal (0.7 = "good enough" baseline)
        gradient = (score - 0.7) * lr
        weight_type = DIM_TO_WEIGHT_MAP.get(dim_name, "seed")

        # Apply lens weighting
        lens_w = ELEMENT_LENS_WEIGHTS.get(lens, {}).get(dim_name, 1.0)
        gradient *= lens_w

        if weight_type == "gate" and result.candidates:
            # Adjust gate weights for gates appearing in results
            for candidate in result.candidates[:3]:
                gate = candidate.gate
                key = f"{gate}:{result.query.home_gate}"
                current = deltas["gate"].get(key, 0.0)
                deltas["gate"][key] = current + gradient * candidate.resonance

        elif weight_type == "seed":
            # Adjust shell seeds for shells appearing in results
            for candidate in result.candidates[:3]:
                shell = candidate.shell
                key = f"S{shell}"
                current = deltas["seed"].get(key, 0.0)
                deltas["seed"][key] = current + gradient

        elif weight_type == "bridge":
            # Adjust cross-element bridge affinity
            for pair_str in result.cross_element_pairs_used[:5]:
                key = pair_str.split(":")[0] if ":" in pair_str else pair_str
                current = deltas["bridge"].get(key, 0.0)
                deltas["bridge"][key] = current + gradient * 0.5

    return deltas


def _apply_weight_deltas(store: FractalWeightStore, deltas: dict) -> int:
    """Apply weight deltas to the store. Returns number of weights updated."""
    updates = 0

    # Apply seed deltas
    for key, delta in deltas.get("seed", {}).items():
        shell = int(key[1:])  # "S5" → 5
        if shell in store.shell_seeds:
            seed = store.shell_seeds[shell]
            seed.mean += delta
            seed.mean = max(0.0, seed.mean)  # clamp non-negative
            updates += 1

    # Apply gate deltas
    for key, delta in deltas.get("gate", {}).items():
        parts = key.split(":")
        if len(parts) == 2:
            src_gate, dst_gate = parts
            if src_gate in store._gate_weights and dst_gate in store._gate_weights.get(src_gate, {}):
                cw = store._gate_weights[src_gate][dst_gate]
                cw.value += delta
                cw.value = max(0.0, cw.value)
                updates += 1

    return updates


# ── Learning rate schedules ──────────────────────────────────────────


def _get_lr(config: SelfPlayConfig, cycle: int) -> float:
    """Compute learning rate for the current cycle."""
    progress = cycle / max(config.total_cycles, 1)

    if config.lr_schedule == "cosine":
        return config.base_lr * 0.5 * (1 + math.cos(math.pi * progress))
    elif config.lr_schedule == "linear":
        return config.base_lr * (1 - progress)
    else:  # constant
        return config.base_lr


# ── Self-Play Loop ───────────────────────────────────────────────────


class SelfPlayLoop:
    """Iterative weight refinement via self-observation."""

    def __init__(self, config: SelfPlayConfig = None):
        self.config = config or SelfPlayConfig()
        self.store = get_store()
        self.engine = CrystalNeuralEngine(self.store)

        self._cycle_history: list[CycleResult] = []
        self._best_resonance = 0.0
        self._best_cycle = 0
        self._initial_resonance = 0.0
        self._weight_snapshots: dict[int, dict] = {}  # cycle → snapshot for rollback

    def run(self, cycles: int = None, queries: list[str] = None) -> SelfPlayReport:
        """Run the self-play loop for N cycles."""
        if cycles is not None:
            self.config.total_cycles = cycles

        if queries is None:
            queries = _generate_queries(self.store, self.config)

        t_start = time.time()
        max_time = self.config.max_time_minutes * 60

        kept = 0
        discarded = 0
        neutral = 0
        total_updates = 0
        lens_counts = {l: 0 for l in LENS_ORDER}

        # Initial resonance baseline
        if queries:
            baseline = self.engine.forward(queries[0])
            self._initial_resonance = baseline.resonance
            self._best_resonance = baseline.resonance

        for cycle in range(self.config.total_cycles):
            elapsed = time.time() - t_start
            if elapsed > max_time:
                break

            # Select query (cycle through available queries)
            query = queries[cycle % len(queries)] if queries else "seed kernel"

            # Determine active lens
            lens_idx = (cycle // self.config.lens_rotation_period) % 4
            lens = LENS_ORDER[lens_idx]
            lens_counts[lens] += 1

            # Learning rate
            lr = _get_lr(self.config, cycle)

            # Snapshot current seed state for rollback
            snapshot = {s: seed.mean for s, seed in self.store.shell_seeds.items()}

            # Forward pass
            result = self.engine.forward(query)
            resonance = result.resonance

            # 12D observation
            dim_scores = _score_12d(result, lens)

            # Compute weight deltas
            deltas = _compute_weight_deltas(dim_scores, result, self.store, lr, lens)

            # Apply deltas
            updates = _apply_weight_deltas(self.store, deltas)

            # Re-evaluate with updated weights
            result_after = self.engine.forward(query)
            resonance_after = result_after.resonance

            # Keep/discard decision
            if resonance_after > resonance + 0.001:
                outcome = "keep"
                kept += 1
                total_updates += updates
                if resonance_after > self._best_resonance:
                    self._best_resonance = resonance_after
                    self._best_cycle = cycle
            elif resonance_after < resonance - 0.01:
                outcome = "discard"
                discarded += 1
                # Rollback
                for s, mean in snapshot.items():
                    if s in self.store.shell_seeds:
                        self.store.shell_seeds[s].mean = mean
            else:
                outcome = "neutral"
                neutral += 1
                total_updates += updates  # keep neutral changes

            cycle_result = CycleResult(
                cycle_id=cycle,
                query=query[:80],
                lens=lens,
                resonance=resonance_after,
                resonance_prev=resonance,
                outcome=outcome,
                dim_scores=dim_scores,
                weight_deltas={k: len(v) for k, v in deltas.items()},
                elapsed_ms=(time.time() - t_start) * 1000 - elapsed * 1000,
            )
            self._cycle_history.append(cycle_result)

            # Checkpoint
            if (cycle + 1) % self.config.cycles_per_checkpoint == 0:
                self._checkpoint(cycle)

        # Final save
        self.store.compress_to_seed()
        self.store.compress_to_micro_seed()
        self.store.compress_to_nano_seed()
        self.store.save()

        total_elapsed = time.time() - t_start
        final_resonance = self._best_resonance

        return SelfPlayReport(
            total_cycles=len(self._cycle_history),
            kept=kept,
            discarded=discarded,
            neutral=neutral,
            initial_resonance=self._initial_resonance,
            final_resonance=final_resonance,
            resonance_improvement=final_resonance - self._initial_resonance,
            best_resonance=self._best_resonance,
            best_cycle=self._best_cycle,
            lens_distribution=lens_counts,
            weight_updates=total_updates,
            elapsed_seconds=total_elapsed,
            cycle_history=[
                {
                    "cycle": cr.cycle_id,
                    "lens": cr.lens,
                    "resonance": round(cr.resonance, 4),
                    "outcome": cr.outcome,
                }
                for cr in self._cycle_history
            ],
        )

    def _checkpoint(self, cycle: int) -> None:
        """Save checkpoint for resume."""
        CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
        cp_path = CHECKPOINT_DIR / f"checkpoint_{cycle:04d}.json"
        self.store.save(cp_path)

    def resume(self, checkpoint_path: Path) -> bool:
        """Resume from a checkpoint."""
        return self.store.load(checkpoint_path)


# ── MCP tool entry point ─────────────────────────────────────────────


def run_self_play(
    cycles: int = 57,
    query_source: str = "mixed",
    max_time_minutes: int = 5,
) -> str:
    """Run a self-play loop to refine the crystal neural network weights.

    The network queries itself, observes output quality in 12D,
    and iteratively adjusts weights. Each cycle:
      query → forward pass → 12D observation → weight refinement → keep/discard

    Args:
        cycles: Number of self-play cycles (57 = one super-cycle)
        query_source: Where to get queries - "corpus", "zero_point", or "mixed"
        max_time_minutes: Maximum wall-clock time for the run
    """
    config = SelfPlayConfig(
        total_cycles=max(1, min(cycles, 570)),
        query_source=query_source,
        max_time_minutes=max(1, min(max_time_minutes, 120)),
    )

    loop = SelfPlayLoop(config)
    report = loop.run()

    return _format_report(report)


def _format_report(report: SelfPlayReport) -> str:
    lines = [
        "## Self-Play Report\n",
        f"**Total Cycles**: {report.total_cycles}",
        f"**Kept**: {report.kept} | **Discarded**: {report.discarded} | **Neutral**: {report.neutral}",
        f"**Initial Resonance**: {report.initial_resonance:.4f}",
        f"**Final Resonance**: {report.final_resonance:.4f}",
        f"**Improvement**: {report.resonance_improvement:+.4f}",
        f"**Best Resonance**: {report.best_resonance:.4f} (cycle {report.best_cycle})",
        f"**Weight Updates**: {report.weight_updates}",
        f"**Elapsed**: {report.elapsed_seconds:.1f}s\n",
    ]

    # Lens distribution
    lines.append("### SFCR Lens Distribution\n")
    for lens, count in report.lens_distribution.items():
        name = LENS_CODES.get(lens, lens)
        bar = "█" * count + "░" * (max(0, 15 - count))
        lines.append(f"  {lens} ({name:7s}): {bar} {count}")

    # Cycle history (last 20)
    if report.cycle_history:
        lines.append("\n### Cycle History (last 20)\n")
        lines.append("| Cycle | Lens | Resonance | Outcome |")
        lines.append("|-------|------|-----------|---------|")
        for ch in report.cycle_history[-20:]:
            icon = {"keep": "✓", "discard": "✗", "neutral": "~"}.get(ch["outcome"], "?")
            lines.append(
                f"| {ch['cycle']:3d} | {ch['lens']} | {ch['resonance']:.4f} | {icon} {ch['outcome']} |"
            )

    # Resonance trajectory
    if len(report.cycle_history) > 5:
        lines.append("\n### Resonance Trajectory\n")
        resonances = [ch["resonance"] for ch in report.cycle_history]
        n = len(resonances)

        # Sample 10 points
        indices = [int(i * (n - 1) / 9) for i in range(10)]
        for idx in indices:
            r = resonances[idx]
            bar_len = int(r * 40)
            bar = "█" * bar_len + "░" * (40 - bar_len)
            lines.append(f"  c{report.cycle_history[idx]['cycle']:3d}: {bar} {r:.4f}")

    return "\n".join(lines)
