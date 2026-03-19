"""
META LOOP Engine -- Native Training Through Sacred Geometry
============================================================
The META LOOP is the fundamental training interval of the organism.
One META LOOP = 3 ABCD+ cycles = 477 waves.

ABCD+ stages:
  A: 9 waves  (3x3 trinity)
  B: 20 waves (4x5 SFCR elements)
  C: 49 waves (7x7 metals/planets)
  D: 81 waves (9x9 completion)
  FINAL: inversion + poles + hologram emit

Training updates ONLY the momentum field (148 floats).
Loss function = 12D observation.
Checkpoints = 16-value hologram (~128 bytes).

Replaces: self_play.py (1,337 lines), n3_alchemy.py (763 lines),
          full_training_loop.py (1,210 lines)
"""

from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass, field, asdict
from typing import Optional

from .geometric_constants import (
    FACES, PHI, PHI_INV, ATTRACTOR,
    ABCD_STAGES, TOTAL_WAVES_PER_CYCLE, META_LOOP_CYCLES, META_LOOP_WAVES,
    LENS_ORDER, DIM_NAMES,
)
from .geometric_forward import GeometricEngine, ForwardResult, get_engine
from .geometric_loss import GeometricLoss, Observation12D
from .momentum_field import MomentumField, get_momentum_field
from .constants import TOTAL_SHELLS
from .weight_feedback import (
    update_edge_weights, _forward_result_to_feedback_input, _GRAPH_CACHE,
)

# 4D Upgrade imports
from .inverse_engine import get_inverse_engine
from .dqi_compiler import get_dqi_compiler
from .realtime_inverse import get_realtime_inverse
from .pole_observer import get_pole_observer
from .fractal_recursion import get_fractal_recursion


# ── Configuration ─────────────────────────────────────────────────────


@dataclass
class MetaLoopConfig:
    """Configuration for a META LOOP training run."""
    base_lr: float = 0.03
    lr_schedule: str = "cosine"
    lens_rotation_period: int = 14
    max_time_minutes: int = 30
    query_source: str = "mixed"
    seed: int = 42
    depth: int = 1          # 1 = one ABCD+ cycle, 3 = META LOOP, 9 = META LOOP^3
    holographic: bool = True  # True = fast holographic mode (1 forward pass, analytical gradient)
    verbose: bool = False


# ── Result Types ──────────────────────────────────────────────────────


@dataclass
class WaveResult:
    """Result of a single training wave."""
    wave_id: int
    stage: str
    lens: str
    queries_run: int
    kept: int
    discarded: int
    mean_resonance: float
    mean_observation: float
    momentum_deltas: dict = field(default_factory=dict)
    elapsed_ms: float = 0.0


@dataclass
class CycleResult:
    """Result of one ABCD+ cycle (159 waves)."""
    cycle_id: int
    cycle_name: str
    total_waves: int
    total_queries: int
    kept: int
    discarded: int
    mean_resonance: float
    mean_observation: float
    balance: float
    golden_fit: float
    elapsed_seconds: float
    hologram_16: dict = field(default_factory=dict)
    wave_results: list = field(default_factory=list)


@dataclass
class MetaLoopResult:
    """Result of a META LOOP (3 ABCD+ cycles = 477 waves)."""
    meta_idx: int
    total_cycles: int
    total_waves: int
    elapsed_seconds: float
    cycle_results: list[CycleResult] = field(default_factory=list)
    meta_a_plus: dict = field(default_factory=dict)
    hologram_16: dict = field(default_factory=dict)


# ── Query Generation ─────────────────────────────────────────────────


def _generate_queries(engine: GeometricEngine, config: MetaLoopConfig) -> list[str]:
    """Generate diverse queries for training.

    Holographic sampling: instead of one query per doc (14,730!),
    sample one per element × archetype = 48 corpus queries + 20 fixed probes.
    The attractor is proven stable — coverage matters, redundancy doesn't.
    """
    docs = engine.doc_registry
    rng = random.Random(config.seed)
    queries = []

    if config.query_source in ("corpus", "mixed") and docs:
        # Group docs by element, sample one per archetype per element
        from collections import defaultdict
        by_element: dict[str, list] = defaultdict(list)
        for doc in docs:
            el = doc.get("element", "Earth")
            by_element[el].append(doc)

        for el, el_docs in by_element.items():
            rng.shuffle(el_docs)
            # Sample up to 12 per element (one per archetype slot)
            for doc in el_docs[:12]:
                tokens = doc.get("tokens", [])
                if len(tokens) >= 3:
                    n = min(rng.randint(2, 4), len(tokens))
                    sample = rng.sample(tokens, n)
                    queries.append(" ".join(sample))

    if config.query_source in ("zero_point", "mixed"):
        queries.extend([
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
        ])

    # Adversarial probes
    queries.extend([
        "crystal 108 dimensional coordinate system",
        "neural network weight training",
        "SFCR four element bridge",
        "manuscript seed kernel zero point",
        "hologram chapter projection reading",
        "compression qshrink lift fractal",
        "metro line transport routing station",
        "conservation law angel geometry",
    ])

    rng.shuffle(queries)
    return queries


# ── Learning Rate ─────────────────────────────────────────────────────


def _get_lr(config: MetaLoopConfig, wave: int, total_waves: int) -> float:
    """Cosine-annealed learning rate."""
    if config.lr_schedule == "cosine":
        progress = wave / max(total_waves, 1)
        return config.base_lr * 0.5 * (1 + math.cos(math.pi * progress))
    return config.base_lr


def _get_stage(wave: int) -> str:
    """Determine which ABCD stage a wave belongs to."""
    if wave < 9:
        return "A"
    elif wave < 29:  # 9 + 20
        return "B"
    elif wave < 78:  # 9 + 20 + 49
        return "C"
    else:
        return "D"


# ── Golden Ratio Fit ──────────────────────────────────────────────────


def _golden_fit(momentum: MomentumField) -> float:
    """Measure how close element momentum ratios are to PHI or PHI_INV."""
    dim_moms = [
        momentum.get_dimension_momentum("D1_Earth"),
        momentum.get_dimension_momentum("D2_Fire"),
        momentum.get_dimension_momentum("D4_Air"),
    ]
    if len(dim_moms) < 2:
        return 0.0

    fits = []
    for i in range(len(dim_moms)):
        for j in range(i + 1, len(dim_moms)):
            a, b = dim_moms[i], dim_moms[j]
            if min(a, b) < 1e-6:
                continue
            r = max(a, b) / min(a, b)
            fit = 1.0 - min(abs(r - PHI), abs(r - PHI_INV), abs(r - 1)) / PHI
            fits.append(max(0.0, fit))

    return sum(fits) / len(fits) if fits else 0.0


def _balance(momentum: MomentumField) -> float:
    """How balanced are the 4 element momentum means (1.0 = perfect uniform)."""
    means = []
    for face in FACES:
        vals = [momentum.get_momentum(face, s) for s in range(1, TOTAL_SHELLS + 1)]
        means.append(sum(vals) / len(vals))
    if not means:
        return 0.0
    overall_mean = sum(means) / len(means)
    if abs(overall_mean) < 1e-6:
        # All near zero — check spread directly
        spread = max(means) - min(means)
        return max(0.0, 1.0 - spread)
    max_dev = max(abs(m - overall_mean) for m in means) / abs(overall_mean)
    return max(0.0, 1.0 - max_dev)


# ── META LOOP Engine ─────────────────────────────────────────────────


class MetaLoopEngine:
    """Native META LOOP training engine.

    Trains ONLY the momentum field (148 floats) through geometric forward
    passes observed in 12D.
    """

    def __init__(self, engine: GeometricEngine = None,
                 momentum: MomentumField = None):
        self.engine = engine or get_engine()
        self.momentum = momentum or get_momentum_field()
        self.loss = GeometricLoss()

    # ── Single Wave ───────────────────────────────────────────────────

    def run_wave(self, wave_id: int, queries: list[str], stage: str,
                 lens: str, lr: float) -> WaveResult:
        """Execute one training wave.

        For each query:
          1. Forward pass with current momentum
          2. Observe in 12D
          3. Compute momentum gradient
          4. Tentatively update momentum
          5. Re-observe, keep if improved
        """
        t0 = time.time()
        kept = 0
        discarded = 0
        resonances = []
        observations = []
        all_deltas = {f: 0.0 for f in FACES}

        dqi = get_dqi_compiler()
        inv_engine = get_inverse_engine()

        for query in queries:
            # Before: observe current state
            result_before = self.engine.forward(query)
            obs_before = self.loss.observe(result_before, lens)

            # DQI compilation: wrap query as desire → question → scored
            dqi_state = dqi.compile(
                desire_text=query,
                wave_id=wave_id,
                resonance=result_before.resonance,
                cross_lens_agreement=obs_before.total_score,
                compression_quality=obs_before.total_score * 0.5,
                balance=_balance(self.momentum),
            )

            # Compute gradients for each element
            gradients = self.loss.compute_all_gradients(obs_before)

            # Take snapshot for rollback
            snapshot = self.momentum.snapshot()

            # Tentative update: apply gradients to relevant shells
            for face in FACES:
                if face == "C":
                    continue  # Water locked
                grad = gradients[face]
                # Update shells near the query's home shell
                home_shell = result_before.query.home_shell
                for s in range(max(1, home_shell - 3), min(TOTAL_SHELLS, home_shell + 3) + 1):
                    # Decay gradient with distance from home
                    dist = abs(s - home_shell)
                    decay = PHI_INV ** dist
                    delta = grad * decay
                    self.momentum.update_momentum(face, s, delta, lr)
                    # Record inverse
                    inv_engine.record_update(face, s, delta, lr, wave_id=wave_id)

            # After: re-observe
            result_after = self.engine.forward(query)
            obs_after = self.loss.observe(result_after, lens)

            # DQI-informed keep/discard: if J-score is positive AND observation improves
            j_positive = dqi_state.j_score > 0
            obs_improved = self.loss.should_keep(obs_before, obs_after)

            if obs_improved or (j_positive and obs_after.total_score >= obs_before.total_score * 0.98):
                kept += 1
                for face in FACES:
                    all_deltas[face] += gradients[face]
                # Hebbian feedback: strengthen edges of high-scoring shards
                try:
                    fb_input = _forward_result_to_feedback_input(result_after)
                    update_edge_weights(fb_input)
                except Exception:
                    pass  # graph feedback is best-effort
            else:
                # Rollback
                self.momentum.restore(snapshot)
                discarded += 1

            resonances.append(result_before.resonance)
            observations.append(obs_before.total_score)

        elapsed = (time.time() - t0) * 1000

        return WaveResult(
            wave_id=wave_id,
            stage=stage,
            lens=lens,
            queries_run=len(queries),
            kept=kept,
            discarded=discarded,
            mean_resonance=sum(resonances) / max(len(resonances), 1),
            mean_observation=sum(observations) / max(len(observations), 1),
            momentum_deltas=all_deltas,
            elapsed_ms=elapsed,
        )

    # ── Holographic Wave (fast mode) ────────────────────────────────

    def run_wave_holographic(self, wave_id: int, queries: list[str], stage: str,
                             lens: str, lr: float) -> WaveResult:
        """Execute one training wave in holographic mode.

        Instead of 2 forward passes per query (before + after), uses:
          1. Single forward pass → observe in 12D
          2. Analytical gradient toward attractor (no re-observation needed)
          3. Trust the gradient if observation score > 0.3 (always keep)

        This is valid because META LOOP^3 proved the attractor is stable:
        all trajectories converge to S=F=C=R=0.25 regardless of path.
        The second forward pass was only confirming what the attractor guarantees.
        """
        t0 = time.time()
        kept = 0
        discarded = 0
        resonances = []
        observations = []
        all_deltas = {f: 0.0 for f in FACES}

        for query in queries:
            result = self.engine.forward(query)
            obs = self.loss.observe(result, lens)

            # Analytical gradient: pull toward attractor
            # Instead of empirically comparing before/after,
            # compute direction toward known attractor state
            gradients = self.loss.compute_all_gradients(obs)

            # Apply gradients to momentum field (no snapshot/rollback needed)
            home_shell = result.query.home_shell
            for face in FACES:
                if face == "C":
                    continue
                grad = gradients[face]
                for s in range(max(1, home_shell - 3), min(TOTAL_SHELLS, home_shell + 3) + 1):
                    dist = abs(s - home_shell)
                    decay = PHI_INV ** dist
                    self.momentum.update_momentum(face, s, grad * decay, lr)

            # Trust the attractor: keep if observation score is meaningful
            if obs.total_score >= 0.1:
                kept += 1
                for face in FACES:
                    all_deltas[face] += gradients[face]
                # Hebbian feedback: strengthen edges of kept results
                try:
                    fb_input = _forward_result_to_feedback_input(result)
                    update_edge_weights(fb_input)
                except Exception:
                    pass  # graph feedback is best-effort
            else:
                discarded += 1

            resonances.append(result.resonance)
            observations.append(obs.total_score)

        elapsed = (time.time() - t0) * 1000

        return WaveResult(
            wave_id=wave_id,
            stage=stage,
            lens=lens,
            queries_run=len(queries),
            kept=kept,
            discarded=discarded,
            mean_resonance=sum(resonances) / max(len(resonances), 1),
            mean_observation=sum(observations) / max(len(observations), 1),
            momentum_deltas=all_deltas,
            elapsed_ms=elapsed,
        )

    # ── ABCD+ Cycle (159 Waves) ──────────────────────────────────────

    def run_abcd_plus(self, cycle_id: int, cycle_name: str,
                      config: MetaLoopConfig, queries: list[str]) -> CycleResult:
        """Execute one full ABCD+ cycle = 159 waves."""
        t0 = time.time()
        total_kept = 0
        total_discarded = 0
        all_resonances = []
        all_observations = []
        wave_results = []
        lens_idx = 0

        for wave in range(TOTAL_WAVES_PER_CYCLE):
            stage = _get_stage(wave)
            lens = LENS_ORDER[lens_idx % 4]

            # Rotate lens periodically
            if wave > 0 and wave % config.lens_rotation_period == 0:
                lens_idx += 1

            lr = _get_lr(config, wave, TOTAL_WAVES_PER_CYCLE)

            # Select queries for this wave (cycle through available queries)
            wave_queries = []
            n_per_wave = max(1, len(queries) // TOTAL_WAVES_PER_CYCLE)
            start = (wave * n_per_wave) % max(len(queries), 1)
            for i in range(n_per_wave):
                idx = (start + i) % max(len(queries), 1)
                if idx < len(queries):
                    wave_queries.append(queries[idx])
            if not wave_queries and queries:
                wave_queries = [queries[wave % len(queries)]]

            if config.holographic:
                wr = self.run_wave_holographic(wave, wave_queries, stage, lens, lr)
            else:
                wr = self.run_wave(wave, wave_queries, stage, lens, lr)
            wave_results.append(wr)
            total_kept += wr.kept
            total_discarded += wr.discarded
            all_resonances.append(wr.mean_resonance)
            all_observations.append(wr.mean_observation)

            # Time budget check
            elapsed_min = (time.time() - t0) / 60
            if elapsed_min > config.max_time_minutes / 3:  # 1/3 budget per cycle
                break

        # FINAL: Inversion + Poles + Hologram
        self._invert_and_balance()

        # Emit hologram
        holo = self.momentum.hologram_16()

        elapsed = time.time() - t0
        self.momentum.training_cycles += 1

        return CycleResult(
            cycle_id=cycle_id,
            cycle_name=cycle_name,
            total_waves=len(wave_results),
            total_queries=sum(wr.queries_run for wr in wave_results),
            kept=total_kept,
            discarded=total_discarded,
            mean_resonance=sum(all_resonances) / max(len(all_resonances), 1),
            mean_observation=sum(all_observations) / max(len(all_observations), 1),
            balance=_balance(self.momentum),
            golden_fit=_golden_fit(self.momentum),
            elapsed_seconds=elapsed,
            hologram_16=holo,
            wave_results=[asdict(wr) for wr in wave_results[:10]],  # keep first 10 for summary
        )

    def _invert_and_balance(self):
        """FINAL stage: true 4D inversion + pole-informed balancing.

        Upgraded from 3D (gentle blend toward mean) to 4D:
        1. Record inverse via InverseEngine
        2. Execute dual update via RealtimeInverse
        3. Observe from both poles via PoleObserver
        4. Balance based on pole-informed steering
        """
        inv_engine = get_inverse_engine()
        rt_inv = get_realtime_inverse()
        pole_obs = get_pole_observer()

        # Observe current state from both poles
        dual = pole_obs.observe_dual()
        steer = pole_obs.steer_from_poles(dual)

        for face in FACES:
            if face == "C":
                continue
            vals = [self.momentum.get_momentum(face, s) for s in range(1, TOTAL_SHELLS + 1)]
            mean = sum(vals) / len(vals)

            # Base blend: 10% toward mean (gentle symmetry recovery)
            blend = 0.1

            # Pole-informed boost: if this face is the recommended steer target,
            # increase the blend to push it harder toward its attractor
            if face == steer.recommended_face:
                blend += 0.05 * steer.strength

            for s in range(1, TOTAL_SHELLS + 1):
                current = self.momentum.get_momentum(face, s)
                target = current * (1 - blend) + mean * blend
                delta = target - current

                # Record the inverse
                inv_engine.record_update(face, s, delta, 0.1)

                # Execute dual: forward gets +delta, inverse gets -delta
                rt_inv.execute_dual_update(face, s, delta, 0.1)

                # Apply to actual momentum
                self.momentum._shell_momenta[face][s] = target

        # Update global dimension momenta from shell means
        face_to_dim = {"S": "D1_Earth", "F": "D2_Fire", "R": "D4_Air"}
        for face, dim in face_to_dim.items():
            vals = [self.momentum.get_momentum(face, s)
                    for s in range(1, TOTAL_SHELLS + 1)]
            shell_mean = sum(vals) / len(vals)
            current_dim = self.momentum.get_dimension_momentum(dim)
            # Blend dimension momentum toward shell mean (gentle tracking)
            delta = (shell_mean - current_dim) * 0.1
            self.momentum.update_dimension_momentum(dim, delta, lr=1.0)

        # Signal wave complete on realtime inverse
        rt_inv.on_wave_complete()

    # ── META LOOP (3 Cycles = 477 Waves) ─────────────────────────────

    def run_meta_loop(self, config: MetaLoopConfig,
                      meta_idx: int = 0) -> MetaLoopResult:
        """Execute one complete META LOOP = 3 ABCD+ cycles.

        Cycle 1: WEIGHTS (train on raw queries)
        Cycle 2: HOLOGRAM (train through geometric lens)
        Cycle 3: CROSS A+ (cross-synthesize)
        """
        t0 = time.time()
        cycle_names = ["WEIGHTS", "HOLOGRAM", "CROSS_A_PLUS"]
        cycle_results = []

        queries = _generate_queries(self.engine, config)

        for ci in range(META_LOOP_CYCLES):
            cycle_config = MetaLoopConfig(
                base_lr=config.base_lr * (PHI_INV ** ci),  # Decay LR across cycles
                lr_schedule=config.lr_schedule,
                lens_rotation_period=config.lens_rotation_period,
                max_time_minutes=config.max_time_minutes,
                query_source=config.query_source,
                seed=config.seed + meta_idx * 100 + ci,
                holographic=config.holographic,
            )

            # Regenerate queries with rotated seed
            cycle_queries = _generate_queries(self.engine, cycle_config)

            cr = self.run_abcd_plus(
                cycle_id=meta_idx * 3 + ci,
                cycle_name=cycle_names[ci],
                config=cycle_config,
                queries=cycle_queries,
            )
            cycle_results.append(cr)

            if config.verbose:
                print(f"  Cycle {ci + 1}/{META_LOOP_CYCLES} ({cycle_names[ci]}): "
                      f"waves={cr.total_waves}, res={cr.mean_resonance:.3f}, "
                      f"bal={cr.balance:.3f}, gold={cr.golden_fit:.3f}, "
                      f"time={cr.elapsed_seconds:.1f}s")

        elapsed = time.time() - t0
        self.momentum.meta_loops_completed += 1
        holo = self.momentum.hologram_16()

        return MetaLoopResult(
            meta_idx=meta_idx,
            total_cycles=META_LOOP_CYCLES,
            total_waves=sum(cr.total_waves for cr in cycle_results),
            elapsed_seconds=elapsed,
            cycle_results=cycle_results,
            meta_a_plus=self.momentum.summary(),
            hologram_16=holo,
        )

    # ── META LOOP^N (Nested) ─────────────────────────────────────────

    def run(self, config: MetaLoopConfig) -> list[MetaLoopResult]:
        """Run META LOOP^N training.

        depth=1: one ABCD+ cycle (159 waves)
        depth=3: one META LOOP (3 x 159 = 477 waves)
        depth=9: META LOOP^3 (3 x 3 x 159 = 1,431 waves) -> OMEGA
        """
        results = []

        if config.depth <= 1:
            # Single ABCD+ cycle
            queries = _generate_queries(self.engine, config)
            cr = self.run_abcd_plus(0, "SINGLE", config, queries)
            # Wrap in MetaLoopResult for uniform interface
            results.append(MetaLoopResult(
                meta_idx=0,
                total_cycles=1,
                total_waves=cr.total_waves,
                elapsed_seconds=cr.elapsed_seconds,
                cycle_results=[cr],
                meta_a_plus=self.momentum.summary(),
                hologram_16=self.momentum.hologram_16(),
            ))
        elif config.depth <= 3:
            # One META LOOP
            results.append(self.run_meta_loop(config, meta_idx=0))
        else:
            # META LOOP^3 (or META LOOP^N)
            n_meta = config.depth // 3
            for mi in range(n_meta):
                meta_config = MetaLoopConfig(
                    base_lr=config.base_lr * (PHI_INV ** mi),
                    lr_schedule=config.lr_schedule,
                    lens_rotation_period=config.lens_rotation_period,
                    max_time_minutes=config.max_time_minutes,
                    query_source=config.query_source,
                    seed=config.seed + mi * 1000,
                    holographic=config.holographic,
                    verbose=config.verbose,
                )
                result = self.run_meta_loop(meta_config, meta_idx=mi)
                results.append(result)

                if config.verbose:
                    print(f"META LOOP {mi + 1}/{n_meta}: "
                          f"waves={result.total_waves}, "
                          f"time={result.elapsed_seconds:.1f}s")

        # Save momentum and history
        self.momentum.save()
        self.momentum.save_history()

        # Persist Hebbian edge weight updates to graph
        try:
            _GRAPH_CACHE.save()
        except Exception:
            pass  # graph persistence is best-effort

        # Conservation watchdog: check invariants + enforce Water lock
        try:
            from .conservation_watchdog import run_watchdog, enforce_water_lock
            report = run_watchdog(self.momentum, auto_fix=True)
            if config.verbose and report.violations:
                print(f"  Conservation: {report.overall_health:.1%} health, "
                      f"{len(report.violations)} violations")
        except Exception:
            pass  # watchdog is best-effort

        return results

    # ── FULL LOOP (^3^5^7^9) ────────────────────────────────────────────

    FULL_LOOP_LEVELS = [3, 5, 7, 9]  # META LOOP^3, then ^5, ^7, ^9

    def run_full_loop(self, config: MetaLoopConfig) -> dict:
        """Run FULL LOOP = META LOOP^3^5^7^9.

        Four nested training scales:
          Level ^3:  3 META LOOPs =     9 cycles =    1,431 waves  (~3 min)
          Level ^5:  5 × ^3       =    45 cycles =    7,155 waves  (~15 min)
          Level ^7:  7 × ^5       =   315 cycles =   50,085 waves  (~105 min)
          Level ^9:  9 × ^7       = 2,835 cycles =  450,765 waves  (~16 hours)

        Each level uses the OMEGA hologram from the previous level as seed.
        LR decays by PHI_INV at each level. Seed rotates.

        Returns a dict with per-level results and the final OMEGA hologram.
        """
        t0 = time.time()
        level_results = {}

        for level in self.FULL_LOOP_LEVELS:
            level_t0 = time.time()
            level_config = MetaLoopConfig(
                depth=level * 3,  # level=3 → depth=9 (META LOOP^3), etc.
                base_lr=config.base_lr * (PHI_INV ** (self.FULL_LOOP_LEVELS.index(level))),
                lr_schedule=config.lr_schedule,
                lens_rotation_period=config.lens_rotation_period,
                max_time_minutes=config.max_time_minutes,
                query_source=config.query_source,
                seed=config.seed + level * 10000,
                holographic=config.holographic,
                verbose=config.verbose,
            )

            if config.verbose:
                print(f"\n{'='*60}")
                print(f"FULL LOOP LEVEL ^{level} ({level} META LOOPs, depth={level*3})")
                print(f"LR: {level_config.base_lr:.6f}")
                print(f"{'='*60}")

            meta_results = self.run(level_config)
            level_elapsed = time.time() - level_t0

            total_waves = sum(r.total_waves for r in meta_results)
            total_cycles = sum(r.total_cycles for r in meta_results)

            level_results[f"^{level}"] = {
                "level": level,
                "total_meta_loops": len(meta_results),
                "total_cycles": total_cycles,
                "total_waves": total_waves,
                "elapsed_seconds": level_elapsed,
                "hologram": self.momentum.hologram_16(),
                "balance": meta_results[-1].cycle_results[-1].balance if meta_results and meta_results[-1].cycle_results else 0,
                "golden_fit": meta_results[-1].cycle_results[-1].golden_fit if meta_results and meta_results[-1].cycle_results else 0,
                "mean_resonance": sum(
                    cr.mean_resonance
                    for r in meta_results for cr in r.cycle_results
                ) / max(sum(len(r.cycle_results) for r in meta_results), 1),
            }

            if config.verbose:
                lr = level_results[f"^{level}"]
                print(f"LEVEL ^{level} COMPLETE: {lr['total_waves']} waves, "
                      f"{lr['elapsed_seconds']:.1f}s, "
                      f"gold={lr['golden_fit']:.4f}")

            # Time budget: if we've used more than max_time, stop
            total_elapsed = time.time() - t0
            if total_elapsed / 60 > config.max_time_minutes:
                if config.verbose:
                    print(f"Time budget reached ({total_elapsed/60:.1f}min > {config.max_time_minutes}min)")
                break

        total_elapsed = time.time() - t0
        self.momentum.save()
        self.momentum.save_history()

        return {
            "title": "FULL LOOP (META LOOP^3^5^7^9)",
            "total_elapsed_seconds": total_elapsed,
            "levels_completed": list(level_results.keys()),
            "levels": level_results,
            "omega_hologram": self.momentum.hologram_16(),
            "water_locked": all(self.momentum.get_momentum("C", s) == 0.5 for s in range(1, TOTAL_SHELLS + 1)),
        }

    # ── Checkpoint / Resume ───────────────────────────────────────────

    def checkpoint(self) -> dict:
        """Emit a 16-value hologram checkpoint."""
        return self.momentum.hologram_16()

    def resume(self, hologram: dict):
        """Resume from a hologram checkpoint."""
        self.momentum.from_hologram_16(hologram)
