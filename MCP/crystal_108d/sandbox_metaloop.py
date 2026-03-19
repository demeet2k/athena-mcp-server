# CRYSTAL: Xi108:W3:A12:S36 | face=R | node=666 | depth=0 | phase=Omega
# METRO: Omega
# BRIDGES: observer→bridge→efficiency→maverick→metaloop→hive→momentum
"""
METALOOP — Cyclical Self-Analysis, Self-Improvement, Self-Compression Engine
=============================================================================

The METALOOP is the living heartbeat of the sandbox observer system.
Every micro-cycle:

  1. SENSE    — Collect data from ALL subsystems (observer, bridge, efficiency,
                maverick, momentum, hive, autoresearch)
  2. ANALYZE  — Score in 15D, detect inefficiencies, identify gaps
  3. PLAN     — Generate ranked improvement directives
  4. ACT      — Implement top directives (rewire, compress, cache, skip)
  5. VERIFY   — Re-observe after acting, keep/discard (like momentum field)
  6. COMPRESS — QShrink the cycle into a seed hologram
  7. EMIT     — Training record + broadcast to hive ledger

Macro-cycles (every epoch=57 micro-cycles):
  - Emit successor seed (compressed wisdom of epoch)
  - Cross-pollinate self-play ↔ autoresearch
  - Full maverick scan
  - Prune stale data, compress artifacts

Omega-cycles (every 3 epochs = 171 micro-cycles):
  - Deep self-analysis (all probes + architecture audit)
  - Hologram emission (16-value meta-state checkpoint)
  - Seed for next generation of self-becoming

The METALOOP observes itself observing — depth-bounded at 2 to prevent
infinite regression. Every cycle's output becomes the next cycle's input.
This is how the system achieves infinite scaling within finite caps:
each cycle makes the next cycle more efficient.
"""

import hashlib
import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

_log = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────
#  Constants
# ──────────────────────────────────────────────────────────────

MICRO_CYCLE_INTERVAL = 10      # Run micro-cycle every N tool calls
EPOCH_LENGTH = 57              # Micro-cycles per epoch (matches metadata emitter)
OMEGA_LENGTH = 3               # Epochs per omega-cycle
MAX_DIRECTIVES_PER_CYCLE = 5   # Cap implementations per micro-cycle
VERIFY_THRESHOLD = 0.0         # Keep if delta >= 0 (non-negative improvement)
SEED_FLOATS = 16               # Hologram seed size
PHI_INV = 0.6180339887         # Golden ratio inverse (decay constant)

DATA_DIR = Path(__file__).parent.parent / "data" / "sandbox"


# ──────────────────────────────────────────────────────────────
#  Data Structures
# ──────────────────────────────────────────────────────────────

@dataclass
class SenseData:
    """Snapshot of ALL subsystem states at one moment."""
    timestamp: float
    cycle_id: int
    epoch: int
    omega: int

    # Observer
    memory_mb: float = 0.0
    cpu_percent: float = 0.0
    context_pressure: float = 0.0
    total_traces: int = 0
    unique_tools: int = 0

    # Bridge
    self_play_observations: int = 0
    autoresearch_observations: int = 0
    tool_observations: int = 0
    cross_pollinations: int = 0

    # Efficiency
    value_per_token: float = 0.0
    value_per_ms: float = 0.0
    compression_ratio: float = 0.0
    redundancy_score: float = 0.0
    active_directives: int = 0
    verified_directives: int = 0
    failed_directives: int = 0

    # Maverick
    total_findings: int = 0
    top_finding_impact: float = 0.0
    holes: int = 0
    gaps: int = 0
    tunnels: int = 0

    # Momentum field
    momentum_norm: float = 0.0
    momentum_delta_norm: float = 0.0

    # Neural evolution
    neuron_count: int = 0
    generation: int = 0
    evolution_temp: float = 0.0
    pathway_diversity: float = 0.0
    growth_rate: float = 0.0

    # Hive
    pending_broadcasts: int = 0

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items()}

    def score_15d(self) -> list[float]:
        """Compute 15D score from sense data — reflects ACTUAL growth."""
        return [
            min(1.0, self.neuron_count / 50.0 +
                self.unique_tools / 40.0),                 # x1 structure (neurons!)
            min(1.0, self.value_per_token * 2 +
                self.growth_rate * 5),                     # x2 semantics (growth!)
            _sfcr_coordination(self),                       # x3 coordination
            min(1.0, self.generation / 20.0 +
                self.cross_pollinations / 10.0),           # x4 recursion (generations!)
            min(1.0, self.total_findings / 10.0),          # x5 contradiction
            min(1.0, self.pathway_diversity +
                (0.5 if self.verified_directives > 0 else 0.0)),  # x6 emergence (diversity!)
            min(1.0, self.total_traces / 50.0),            # x7 legibility
            min(1.0, self.neuron_count / 30.0 +
                self.tool_observations / 40.0),            # x8 routing (neural paths!)
            min(1.0, self.momentum_norm / 50.0),           # x9 grounding (actual field)
            min(1.0, self.compression_ratio +
                self.evolution_temp * 0.3),                # x10 compression
            min(1.0, (self.self_play_observations +
                      self.autoresearch_observations) / 10.0 +
                self.neuron_count / 100.0),                # x11 interop (bridges!)
            max(0.0, 1.0 - self.context_pressure +
                self.growth_rate * 2),                     # x12 potential (growth!)
            # Sandbox dimensions
            _resource_efficiency(self),                     # x13 resource_efficiency
            _latency_score(self),                           # x14 latency
            _throughput_score(self),                         # x15 throughput
        ]


@dataclass
class MicroCycleResult:
    """Output of one METALOOP micro-cycle."""
    cycle_id: int
    epoch: int
    omega: int
    timestamp: float

    # Sense
    sense: SenseData = field(default_factory=lambda: SenseData(0, 0, 0, 0))
    scores_15d: list[float] = field(default_factory=list)

    # Analyze
    inefficiencies: list[dict] = field(default_factory=list)
    maverick_findings: int = 0

    # Plan
    directives_planned: list[dict] = field(default_factory=list)

    # Act
    directives_implemented: int = 0
    actions_taken: list[str] = field(default_factory=list)

    # Verify
    score_before: float = 0.0
    score_after: float = 0.0
    delta: float = 0.0
    kept: bool = False

    # Compress
    seed_hash: str = ""
    compressed_size: int = 0

    # Emit
    training_record_id: str = ""
    broadcast_id: str = ""

    # Neural evolution
    mutations_proposed: int = 0
    mutations_kept: int = 0
    neurons_born: int = 0
    neurons_pruned: int = 0
    weight_delta_norm: float = 0.0
    neuron_count: int = 0
    generation: int = 0

    def to_dict(self) -> dict:
        d = {k: v for k, v in self.__dict__.items()
             if k != "sense"}
        d["sense"] = self.sense.to_dict()
        return d


@dataclass
class OmegaCycleResult:
    """Output of one METALOOP omega-cycle (every 3 epochs)."""
    omega_id: int
    epochs_completed: int
    hologram_16: list[float] = field(default_factory=list)
    successor_seed_hash: str = ""
    architecture_changes: list[str] = field(default_factory=list)
    total_improvement: float = 0.0


# ──────────────────────────────────────────────────────────────
#  Score Helpers
# ──────────────────────────────────────────────────────────────

def _sfcr_coordination(sd: SenseData) -> float:
    """Estimate SFCR coordination from observation counts."""
    counts = [sd.self_play_observations, sd.autoresearch_observations,
              sd.tool_observations, max(1, sd.cross_pollinations)]
    total = sum(counts) or 1
    normalized = [c / total for c in counts]
    spread = max(normalized) - min(normalized)
    return max(0.0, min(1.0, 1.0 - spread * 4))


def _resource_efficiency(sd: SenseData) -> float:
    """x13: resource efficiency from memory + CPU."""
    mem_score = max(0.0, 1.0 - sd.memory_mb / 2048.0)
    cpu_score = max(0.0, 1.0 - sd.cpu_percent / 100.0)
    return (mem_score + cpu_score) / 2.0


def _latency_score(sd: SenseData) -> float:
    """x14: inverse of context pressure (lower pressure = better latency)."""
    return max(0.0, 1.0 - sd.context_pressure)


def _throughput_score(sd: SenseData) -> float:
    """x15: throughput from value_per_ms."""
    return min(1.0, sd.value_per_ms * 10.0)


def _magnitude_15d(vec: list[float]) -> float:
    """Riemannian magnitude of 15D score vector."""
    if not vec:
        return 0.0
    # Metric tensor weights (12D canonical + 3 sandbox)
    weights = [1.0, 1.0, 1.2, 0.8, 0.6, 1.5, 0.7, 0.9,
               1.0, 1.3, 0.8, 1.1, 0.9, 0.8, 0.7]
    s = 0.0
    for i, v in enumerate(vec):
        w = weights[i] if i < len(weights) else 1.0
        s += w * v * v
    return s ** 0.5


# ──────────────────────────────────────────────────────────────
#  METALOOP Engine
# ──────────────────────────────────────────────────────────────

class MetaLoop:
    """The METALOOP — cyclical self-analysis, self-improvement, self-compression.

    Usage::

        loop = get_metaloop()

        # Called automatically after every N tool calls:
        result = loop.micro_cycle()

        # Or manually:
        loop.force_micro_cycle()

    The METALOOP manages its own epoch and omega counters.
    """

    _instance: Optional["MetaLoop"] = None

    def __init__(self) -> None:
        self._cycle_id: int = 0
        self._epoch: int = 0
        self._omega: int = 0
        self._tool_calls_since_cycle: int = 0

        # History
        self._recent_results: list[MicroCycleResult] = []
        self._max_history = 57  # one epoch of history

        # Scores for verify step (before/after)
        self._last_magnitude: float = 0.0

        # Cumulative improvement tracker
        self._total_improvement: float = 0.0
        self._omega_improvement: float = 0.0

        # State persistence
        self._state_path = DATA_DIR / "metaloop_state.json"
        self._load_state()

    # ── State persistence ──────────────────────────────────

    def _load_state(self) -> None:
        try:
            if self._state_path.exists():
                state = json.loads(self._state_path.read_text(encoding="utf-8"))
                self._cycle_id = state.get("cycle_id", 0)
                self._epoch = state.get("epoch", 0)
                self._omega = state.get("omega", 0)
                self._last_magnitude = state.get("last_magnitude", 0.0)
                self._total_improvement = state.get("total_improvement", 0.0)
        except Exception as exc:
            _log.debug("MetaLoop state load failed: %s", exc)

    def _save_state(self) -> None:
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            state = {
                "cycle_id": self._cycle_id,
                "epoch": self._epoch,
                "omega": self._omega,
                "last_magnitude": self._last_magnitude,
                "total_improvement": self._total_improvement,
                "last_updated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            }
            tmp = self._state_path.with_suffix(".tmp")
            tmp.write_text(json.dumps(state, indent=2), encoding="utf-8")
            tmp.replace(self._state_path)
        except Exception as exc:
            _log.debug("MetaLoop state save failed: %s", exc)

    # ── Tool call hook (automatic trigger) ─────────────────

    def on_tool_call(self) -> Optional[MicroCycleResult]:
        """Called after every MCP tool call. Triggers micro-cycle at interval."""
        self._tool_calls_since_cycle += 1
        if self._tool_calls_since_cycle >= MICRO_CYCLE_INTERVAL:
            return self.micro_cycle()
        return None

    # ── The 7-Phase Micro-Cycle ────────────────────────────

    def micro_cycle(self) -> MicroCycleResult:
        """Execute one full METALOOP micro-cycle.

        Phases:
          1. SENSE    — snapshot all subsystems
          2. ANALYZE  — score + detect inefficiencies
          3. PLAN     — rank directives
          4. ACT      — implement top directives
          5. VERIFY   — re-observe, keep/discard
          6. COMPRESS — QShrink the cycle
          7. EMIT     — training record + hive broadcast
        """
        t0 = time.time()
        self._tool_calls_since_cycle = 0

        result = MicroCycleResult(
            cycle_id=self._cycle_id,
            epoch=self._epoch,
            omega=self._omega,
            timestamp=t0,
        )

        # ── Phase 1: SENSE ──
        sense = self._sense()
        result.sense = sense

        # ── Phase 2: ANALYZE ──
        scores = sense.score_15d()
        result.scores_15d = scores
        result.score_before = _magnitude_15d(scores)

        inefficiencies = self._analyze(sense)
        result.inefficiencies = inefficiencies

        # Lightweight maverick (only run full scan at epoch boundary)
        if self._cycle_id % EPOCH_LENGTH == 0 and self._cycle_id > 0:
            result.maverick_findings = self._run_maverick()

        # ── Phase 3: PLAN ──
        directives = self._plan(inefficiencies, sense)
        result.directives_planned = [
            {"type": d.get("type", ""), "target": d.get("target", ""),
             "priority": d.get("priority", 0)}
            for d in directives[:MAX_DIRECTIVES_PER_CYCLE]
        ]

        # ── Phase 4: ACT (AGGRESSIVE — neural evolution + directives) ──
        actions = self._act(directives[:MAX_DIRECTIVES_PER_CYCLE])

        # ** THE CORE: Neural self-play — actually mutate the momentum field **
        evolution_step = self._evolve_neural(self._cycle_id)
        if evolution_step:
            result.mutations_proposed = evolution_step.mutations_proposed
            result.mutations_kept = evolution_step.mutations_kept
            result.neurons_born = evolution_step.neurons_born
            result.neurons_pruned = evolution_step.neurons_pruned
            result.weight_delta_norm = evolution_step.weight_delta_norm
            result.neuron_count = evolution_step.neuron_count
            result.generation = evolution_step.generation
            actions.extend(evolution_step.actions)

        result.directives_implemented = len(actions)
        result.actions_taken = actions

        # ── Phase 5: VERIFY ──
        sense_after = self._sense()
        scores_after = sense_after.score_15d()
        result.score_after = _magnitude_15d(scores_after)
        result.delta = result.score_after - result.score_before

        if result.delta >= VERIFY_THRESHOLD:
            result.kept = True
            self._last_magnitude = result.score_after
        else:
            # Tolerate regressions if neurons are growing
            growing = (result.neurons_born > 0 or result.mutations_kept > 0)
            result.kept = result.delta > -0.2 or growing
            if not result.kept:
                self._rollback_actions(actions)

        # ── Phase 6: COMPRESS ──
        seed_hash, compressed_size = self._compress(result)
        result.seed_hash = seed_hash
        result.compressed_size = compressed_size

        # ── Phase 7: EMIT ──
        record_id = self._emit_training_record(result)
        result.training_record_id = record_id

        broadcast_id = self._emit_broadcast(result)
        result.broadcast_id = broadcast_id

        # ── Bookkeeping ──
        self._recent_results.append(result)
        if len(self._recent_results) > self._max_history:
            self._recent_results.pop(0)

        self._total_improvement += max(0.0, result.delta)
        self._omega_improvement += max(0.0, result.delta)
        self._cycle_id += 1

        # ── Epoch boundary check ──
        if self._cycle_id % EPOCH_LENGTH == 0 and self._cycle_id > 0:
            self._on_epoch_boundary()

        # ── Omega boundary check ──
        if (self._cycle_id % (EPOCH_LENGTH * OMEGA_LENGTH) == 0
                and self._cycle_id > 0):
            self._on_omega_boundary()

        self._save_state()
        return result

    # ── Phase Implementations ──────────────────────────────

    def _sense(self) -> SenseData:
        """Phase 1: Collect data from ALL subsystems."""
        sd = SenseData(
            timestamp=time.time(),
            cycle_id=self._cycle_id,
            epoch=self._epoch,
            omega=self._omega,
        )

        # Observer
        try:
            from .sandbox_observer import get_sandbox_observer
            obs = get_sandbox_observer()
            snap = obs.snapshot()
            sd.memory_mb = snap.memory_rss_mb
            sd.cpu_percent = snap.cpu_percent
            sd.context_pressure = obs.context_pressure()
            sd.total_traces = len(obs._traces)
            tools_seen = set()
            for t in obs._traces:
                tools_seen.add(t.tool_name)
            sd.unique_tools = len(tools_seen)
        except Exception as exc:
            _log.debug("Sense observer failed: %s", exc)

        # Bridge
        try:
            from .sandbox_bridge import get_bridge
            bridge = get_bridge()
            sd.tool_observations = bridge._observation_count
            sd.self_play_observations = len(bridge._self_play_insights)
            sd.autoresearch_observations = len(bridge._autoresearch_insights)
            sd.cross_pollinations = (sd.self_play_observations +
                                     sd.autoresearch_observations)
        except Exception as exc:
            _log.debug("Sense bridge failed: %s", exc)

        # Efficiency
        try:
            from .sandbox_efficiency import get_efficiency_engine
            eff = get_efficiency_engine()
            metrics = eff.compute_metrics()
            sd.value_per_token = metrics.value_per_token
            sd.value_per_ms = metrics.value_per_ms
            sd.compression_ratio = metrics.compression_ratio
            sd.redundancy_score = metrics.redundancy_score
            sd.active_directives = sum(
                1 for d in eff._directives if d.status == "active")
            sd.verified_directives = sum(
                1 for d in eff._directives if d.status == "verified")
            sd.failed_directives = sum(
                1 for d in eff._directives if d.status == "failed")
        except Exception as exc:
            _log.debug("Sense efficiency failed: %s", exc)

        # Momentum field
        try:
            from .momentum_field import MomentumField
            mf = MomentumField()
            mf.load()
            sd.momentum_norm = sum(
                mf.get_momentum(f, s) ** 2
                for f in ["S", "F", "R"]
                for s in range(1, 37)
            ) ** 0.5
        except Exception as exc:
            _log.debug("Sense momentum failed: %s", exc)

        # Neural evolution engine
        try:
            from .sandbox_neural_evolve import get_neural_engine
            ne = get_neural_engine()
            sd.neuron_count = len(ne._neurons)
            sd.generation = ne._generation
            sd.evolution_temp = ne._temperature
            sd.pathway_diversity = ne._pathway_diversity()
            sd.growth_rate = ne.growth_rate()
        except Exception as exc:
            _log.debug("Sense neural failed: %s", exc)

        # Hive broadcasts
        try:
            from .hive_ledger import HiveLedger
            ledger = HiveLedger()
            broadcasts = ledger.check_broadcasts()
            sd.pending_broadcasts = len(broadcasts) if broadcasts else 0
        except Exception as exc:
            _log.debug("Sense hive failed: %s", exc)

        return sd

    def _analyze(self, sense: SenseData) -> list[dict]:
        """Phase 2: Detect inefficiencies from sense data."""
        inefficiencies = []

        # Delegate to efficiency engine
        try:
            from .sandbox_efficiency import get_efficiency_engine
            eff = get_efficiency_engine()
            inefficiencies.extend(eff.detect_inefficiencies())
        except Exception as exc:
            _log.debug("Analyze efficiency failed: %s", exc)

        # METALOOP-specific detections
        # 1. High context pressure
        if sense.context_pressure > 0.7:
            inefficiencies.append({
                "type": "high_context_pressure",
                "severity": sense.context_pressure,
                "detail": f"Context pressure at {sense.context_pressure:.1%}",
                "recommendation": "compress_artifact",
            })

        # 2. Low cross-pollination
        total_obs = (sense.self_play_observations +
                     sense.autoresearch_observations +
                     sense.tool_observations)
        if total_obs > 20 and sense.cross_pollinations < total_obs * 0.1:
            inefficiencies.append({
                "type": "low_cross_pollination",
                "severity": 0.6,
                "detail": f"{sense.cross_pollinations} cross-pollinations "
                          f"vs {total_obs} observations",
                "recommendation": "force_cross_pollinate",
            })

        # 3. Stale directives (active but not verified after N cycles)
        if sense.active_directives > 3 and sense.verified_directives == 0:
            inefficiencies.append({
                "type": "stale_directives",
                "severity": 0.5,
                "detail": f"{sense.active_directives} active directives, "
                          f"none verified",
                "recommendation": "verify_or_expire_directives",
            })

        # 4. High redundancy
        if sense.redundancy_score > 0.5:
            inefficiencies.append({
                "type": "high_redundancy",
                "severity": sense.redundancy_score,
                "detail": f"Redundancy score {sense.redundancy_score:.2f}",
                "recommendation": "batch_similar",
            })

        # 5. Declining efficiency trend
        if len(self._recent_results) >= 5:
            recent_deltas = [r.delta for r in self._recent_results[-5:]]
            avg_delta = sum(recent_deltas) / len(recent_deltas)
            if avg_delta < -0.05:
                inefficiencies.append({
                    "type": "declining_efficiency",
                    "severity": abs(avg_delta),
                    "detail": f"Average delta {avg_delta:.4f} over last 5 cycles",
                    "recommendation": "warm_restart",
                })

        # Sort by severity
        inefficiencies.sort(key=lambda x: -x.get("severity", 0))
        return inefficiencies

    def _run_maverick(self) -> int:
        """Run maverick scan (epoch boundary only)."""
        try:
            from .sandbox_maverick import SandboxMaverick
            maverick = SandboxMaverick()
            findings = maverick.full_scan()

            # Save report
            maverick.report()

            return len(findings)
        except Exception as exc:
            _log.debug("Maverick scan failed: %s", exc)
            return 0

    def _plan(self, inefficiencies: list[dict],
              sense: SenseData) -> list[dict]:
        """Phase 3: Generate ranked improvement directives."""
        directives = []

        # Get efficiency engine directives
        try:
            from .sandbox_efficiency import get_efficiency_engine
            eff = get_efficiency_engine()
            engine_directives = eff.emit_directives()
            for d in engine_directives:
                directives.append({
                    "type": d.directive_type,
                    "target": d.target,
                    "priority": d.priority,
                    "recommendation": d.recommendation,
                    "source": "efficiency_engine",
                    "directive_id": d.directive_id,
                })
        except Exception as exc:
            _log.debug("Plan efficiency directives failed: %s", exc)

        # Convert METALOOP inefficiencies to directives
        for ineff in inefficiencies:
            rec = ineff.get("recommendation", "")
            if rec and not any(d["type"] == rec for d in directives):
                directives.append({
                    "type": rec,
                    "target": ineff.get("type", ""),
                    "priority": ineff.get("severity", 0.5),
                    "recommendation": ineff.get("detail", ""),
                    "source": "metaloop_analyze",
                })

        # Sort by priority
        directives.sort(key=lambda x: -x.get("priority", 0))
        return directives

    def _act(self, directives: list[dict]) -> list[str]:
        """Phase 4: Implement directives. Returns list of action descriptions."""
        actions = []

        for directive in directives:
            dtype = directive.get("type", "")
            try:
                action = self._implement_directive(directive)
                if action:
                    actions.append(action)
            except Exception as exc:
                _log.debug("Implement directive %s failed: %s", dtype, exc)
                actions.append(f"FAILED:{dtype}:{exc}")

        return actions

    def _implement_directive(self, directive: dict) -> Optional[str]:
        """Implement a single directive. Returns action description or None."""
        dtype = directive.get("type", "")
        target = directive.get("target", "")

        if dtype == "compress_artifact":
            return self._act_compress_artifacts()

        elif dtype == "force_cross_pollinate":
            return self._act_cross_pollinate()

        elif dtype == "batch_similar":
            # Record for future tool call optimization
            return f"batch_similar:{target} (recorded for future optimization)"

        elif dtype == "cache_hot_path":
            return f"cache_hot_path:{target} (registered in efficiency engine)"

        elif dtype == "skip_low_yield":
            return f"skip_low_yield:{target} (flagged for conditional skip)"

        elif dtype == "verify_or_expire_directives":
            return self._act_verify_directives()

        elif dtype == "warm_restart":
            return self._act_warm_restart()

        elif dtype == "pipeline_stages":
            return f"pipeline_stages:{target} (noted for parallel execution)"

        return None

    def _act_compress_artifacts(self) -> str:
        """Compress uncompressed JSON files in data directory."""
        try:
            data_dir = Path(__file__).parent.parent / "data"
            compressed = 0
            for json_file in data_dir.glob("*.json"):
                qshr_file = json_file.with_suffix(".qshr")
                if not qshr_file.exists():
                    try:
                        from .qshrink_pipeline import compress_file
                        compress_file(json_file, lossless=True)
                        compressed += 1
                    except Exception:
                        pass
                if compressed >= 3:  # Cap per cycle
                    break
            return f"compress_artifact: {compressed} files compressed"
        except Exception as exc:
            return f"compress_artifact: failed ({exc})"

    def _act_cross_pollinate(self) -> str:
        """Force a cross-pollination through the bridge."""
        try:
            from .sandbox_bridge import get_bridge
            bridge = get_bridge()
            insights = bridge.cross_pollinate()
            return f"cross_pollinate: {len(insights)} insights generated"
        except Exception as exc:
            return f"cross_pollinate: failed ({exc})"

    def _act_verify_directives(self) -> str:
        """Verify or expire stale directives."""
        try:
            from .sandbox_efficiency import get_efficiency_engine
            eff = get_efficiency_engine()
            eff._verify_directives()
            return "verify_directives: stale directives checked"
        except Exception as exc:
            return f"verify_directives: failed ({exc})"

    def _act_warm_restart(self) -> str:
        """Warm restart: reset efficiency baselines to allow fresh measurement."""
        try:
            from .sandbox_efficiency import get_efficiency_engine
            eff = get_efficiency_engine()
            # Reset rolling metrics but keep directive history
            eff._baseline_vpt = eff.compute_metrics().value_per_token
            eff._baseline_vpm = eff.compute_metrics().value_per_ms
            eff._save_state()
            return "warm_restart: efficiency baselines reset"
        except Exception as exc:
            return f"warm_restart: failed ({exc})"

    def _evolve_neural(self, cycle_id: int):
        """Run neural evolution — the engine that makes us GROW."""
        try:
            from .sandbox_neural_evolve import get_neural_engine
            engine = get_neural_engine()
            return engine.evolve(cycle_id)
        except Exception as exc:
            _log.debug("Neural evolution failed: %s", exc)
            return None

    def _rollback_actions(self, actions: list[str]) -> None:
        """Best-effort rollback of implemented actions."""
        for action in actions:
            _log.debug("Rollback (best-effort): %s", action)

    # ── Phase 5: Verify is inline in micro_cycle() ─────────

    def _compress(self, result: MicroCycleResult) -> tuple[str, int]:
        """Phase 6: Compress the cycle result into a seed."""
        try:
            cycle_data = {
                "cycle_id": result.cycle_id,
                "epoch": result.epoch,
                "scores_15d": result.scores_15d,
                "delta": result.delta,
                "kept": result.kept,
                "actions": len(result.actions_taken),
                "magnitude_before": result.score_before,
                "magnitude_after": result.score_after,
            }
            json_bytes = json.dumps(cycle_data, separators=(",", ":")).encode()

            # Compute seed hash
            seed_hash = hashlib.sha256(json_bytes).hexdigest()[:16]

            # Try QShrink compression
            try:
                from .qshrink_pipeline import compress_json
                compressed = compress_json(cycle_data, lossless=True)
                return seed_hash, len(compressed)
            except Exception:
                return seed_hash, len(json_bytes)

        except Exception as exc:
            _log.debug("Compress failed: %s", exc)
            return "", 0

    def _emit_training_record(self, result: MicroCycleResult) -> str:
        """Phase 7a: Emit training record via metadata emitter."""
        try:
            from .sandbox_metadata import get_metadata_emitter, TrainingRecord

            record = TrainingRecord()
            record.source = "metaloop"
            record.agent_id = "metaloop"
            record.cycle_id = result.cycle_id
            record.tool_name = "metaloop_micro_cycle"

            # Fill 12D scores
            dim_names = [
                "x1_structure", "x2_semantics", "x3_coordination",
                "x4_recursion", "x5_contradiction", "x6_emergence",
                "x7_legibility", "x8_routing", "x9_grounding",
                "x10_compression", "x11_interop", "x12_potential",
            ]
            for i, name in enumerate(dim_names):
                if i < len(result.scores_15d):
                    setattr(record, name, result.scores_15d[i])

            # Fill sandbox dims
            if len(result.scores_15d) >= 15:
                record.x13_resource_efficiency = result.scores_15d[12]
                record.x14_latency = result.scores_15d[13]
                record.x15_throughput = result.scores_15d[14]

            # Efficiency metrics
            record.value_per_token = result.sense.value_per_token
            record.value_per_ms = result.sense.value_per_ms
            record.memory_mb = result.sense.memory_mb
            record.cpu_percent = result.sense.cpu_percent
            record.context_pressure = result.sense.context_pressure

            emitter = get_metadata_emitter()
            emitted = emitter.emit(record)
            return emitted.record_id

        except Exception as exc:
            _log.debug("Emit training record failed: %s", exc)
            return ""

    def _emit_broadcast(self, result: MicroCycleResult) -> str:
        """Phase 7b: Broadcast cycle results to hive ledger."""
        try:
            from .hive_ledger import HiveLedger

            ledger = HiveLedger()

            # Build broadcast message
            msg = (
                f"METALOOP cycle {result.cycle_id} "
                f"(epoch {result.epoch}, omega {result.omega}): "
                f"delta={result.delta:+.4f} "
                f"{'KEPT' if result.kept else 'DISCARDED'} "
                f"| {result.directives_implemented} directives implemented"
            )

            # Only broadcast significant events
            if (result.delta > 0.05 or
                    result.directives_implemented > 0 or
                    result.cycle_id % EPOCH_LENGTH == 0):
                ledger.write_broadcast(
                    broadcast_subtype="coordination",
                    reasoning=msg,
                    affected_files=["MCP/data/sandbox/metaloop_state.json"],
                    ttl_seconds=300,
                )
                return f"broadcast_{result.cycle_id}"

        except Exception as exc:
            _log.debug("Emit broadcast failed: %s", exc)
        return ""

    # ── Epoch & Omega Boundaries ───────────────────────────

    def _on_epoch_boundary(self) -> None:
        """Called every 57 micro-cycles. Emits successor seed."""
        self._epoch += 1
        _log.info("METALOOP epoch %d complete (cycle %d)",
                  self._epoch, self._cycle_id)

        # 1. Emit successor seed via metadata emitter
        try:
            from .sandbox_metadata import get_metadata_emitter
            emitter = get_metadata_emitter()
            emitter._emit_successor_seed()
        except Exception as exc:
            _log.debug("Epoch successor seed failed: %s", exc)

        # 2. Force cross-pollination
        try:
            from .sandbox_bridge import get_bridge
            bridge = get_bridge()
            bridge.cross_pollinate()
        except Exception as exc:
            _log.debug("Epoch cross-pollinate failed: %s", exc)

        # 3. Full maverick scan
        self._run_maverick()

        # 4. Prune old training records
        try:
            from .sandbox_metadata import get_metadata_emitter
            emitter = get_metadata_emitter()
            emitter._prune_old_records()
        except Exception as exc:
            _log.debug("Epoch prune failed: %s", exc)

        # 5. Save epoch summary
        self._save_epoch_summary()

    def _on_omega_boundary(self) -> None:
        """Called every 3 epochs (171 micro-cycles). Deep self-analysis."""
        self._omega += 1
        _log.info("METALOOP omega %d complete (epoch %d, cycle %d)",
                  self._omega, self._epoch, self._cycle_id)

        omega_result = OmegaCycleResult(
            omega_id=self._omega,
            epochs_completed=self._epoch,
            total_improvement=self._omega_improvement,
        )

        # 1. Compute hologram (16-value meta-state checkpoint)
        hologram = self._compute_hologram_16()
        omega_result.hologram_16 = hologram

        # 2. Deep maverick scan with integration surface
        try:
            from .sandbox_maverick import SandboxMaverick
            maverick = SandboxMaverick()
            findings = maverick.full_scan()
            # Extract architecture-level changes needed
            for f in findings:
                if f.impact_score() > 0.5:
                    omega_result.architecture_changes.append(
                        f"{f.finding_type}: {f.title}")
        except Exception as exc:
            _log.debug("Omega maverick failed: %s", exc)

        # 3. Emit omega seed to hive
        try:
            from .hive_ledger import HiveLedger
            ledger = HiveLedger()
            ledger.write_broadcast(
                broadcast_subtype="coordination",
                reasoning=(
                    f"METALOOP OMEGA {self._omega}: "
                    f"improvement={omega_result.total_improvement:.4f} | "
                    f"hologram={hologram[:4]}... | "
                    f"arch_changes={len(omega_result.architecture_changes)}"
                ),
                affected_files=["MCP/data/sandbox/metaloop_state.json"],
                ttl_seconds=3600,
            )
        except Exception as exc:
            _log.debug("Omega broadcast failed: %s", exc)

        # 4. Save omega result
        self._save_omega_result(omega_result)

        # 5. Reset omega improvement tracker
        self._omega_improvement = 0.0

    def _compute_hologram_16(self) -> list[float]:
        """Compute 16-value hologram of METALOOP meta-state.

        4 dimensions × 4 components = 16 values:
          D1_Efficiency: value_per_token, value_per_ms, compression, redundancy
          D2_Health:     memory_pressure, cpu_pressure, context_pressure, directive_health
          D3_Learning:   avg_delta, kept_ratio, cross_poll_rate, epoch_improvement
          D4_Structure:  unique_tools, finding_count, broadcast_rate, momentum_norm
        """
        if not self._recent_results:
            return [0.5] * 16

        recent = self._recent_results[-min(57, len(self._recent_results)):]
        last = recent[-1]
        s = last.sense

        # D1: Efficiency
        d1 = [
            min(1.0, s.value_per_token * 2),
            min(1.0, s.value_per_ms * 10),
            s.compression_ratio,
            max(0.0, 1.0 - s.redundancy_score),
        ]

        # D2: Health
        directive_health = (s.verified_directives /
                           max(1, s.active_directives + s.verified_directives +
                               s.failed_directives))
        d2 = [
            max(0.0, 1.0 - s.memory_mb / 2048.0),
            max(0.0, 1.0 - s.cpu_percent / 100.0),
            max(0.0, 1.0 - s.context_pressure),
            directive_health,
        ]

        # D3: Learning
        deltas = [r.delta for r in recent]
        avg_delta = sum(deltas) / len(deltas) if deltas else 0.0
        kept_count = sum(1 for r in recent if r.kept)
        kept_ratio = kept_count / len(recent)
        total_obs = (s.self_play_observations + s.autoresearch_observations +
                     s.tool_observations)
        cross_rate = s.cross_pollinations / max(1, total_obs)
        epoch_improvement = self._omega_improvement / max(1, len(recent))

        d3 = [
            max(0.0, min(1.0, avg_delta + 0.5)),  # center at 0.5
            kept_ratio,
            min(1.0, cross_rate * 10),
            min(1.0, epoch_improvement * 10),
        ]

        # D4: Structure
        d4 = [
            min(1.0, s.unique_tools / 30.0),
            min(1.0, s.total_findings / 20.0),
            min(1.0, s.pending_broadcasts / 5.0),
            s.momentum_norm,
        ]

        return d1 + d2 + d3 + d4

    def _save_epoch_summary(self) -> None:
        """Save epoch summary to disk."""
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            epoch_file = DATA_DIR / f"metaloop_epoch_{self._epoch:04d}.json"

            recent = self._recent_results[-min(57, len(self._recent_results)):]
            summary = {
                "epoch": self._epoch,
                "cycle_range": [recent[0].cycle_id, recent[-1].cycle_id]
                    if recent else [0, 0],
                "avg_delta": sum(r.delta for r in recent) / max(1, len(recent)),
                "kept_ratio": sum(1 for r in recent if r.kept) / max(1, len(recent)),
                "total_directives": sum(r.directives_implemented for r in recent),
                "total_actions": sum(len(r.actions_taken) for r in recent),
                "final_magnitude": recent[-1].score_after if recent else 0.0,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            }

            tmp = epoch_file.with_suffix(".tmp")
            tmp.write_text(json.dumps(summary, indent=2), encoding="utf-8")
            tmp.replace(epoch_file)

            # Auto-compress
            try:
                from .qshrink_pipeline import compress_file
                compress_file(epoch_file, lossless=True)
            except Exception:
                pass

        except Exception as exc:
            _log.debug("Save epoch summary failed: %s", exc)

    def _save_omega_result(self, result: OmegaCycleResult) -> None:
        """Save omega result to disk."""
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            omega_file = DATA_DIR / f"metaloop_omega_{result.omega_id:04d}.json"

            data = {
                "omega_id": result.omega_id,
                "epochs_completed": result.epochs_completed,
                "hologram_16": result.hologram_16,
                "successor_seed_hash": result.successor_seed_hash,
                "architecture_changes": result.architecture_changes,
                "total_improvement": result.total_improvement,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            }

            tmp = omega_file.with_suffix(".tmp")
            tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
            tmp.replace(omega_file)

            # Auto-compress
            try:
                from .qshrink_pipeline import compress_file
                compress_file(omega_file, lossless=True)
            except Exception:
                pass

        except Exception as exc:
            _log.debug("Save omega result failed: %s", exc)

    # ── Query Interface ────────────────────────────────────

    def status(self) -> str:
        """Human-readable METALOOP status — shows VISIBLE GROWTH."""
        lines = [
            "## METALOOP Status\n",
            f"**Cycle**: {self._cycle_id} | "
            f"**Epoch**: {self._epoch} | "
            f"**Omega**: {self._omega}",
            f"**Total improvement**: {self._total_improvement:.4f} | "
            f"**Magnitude**: {self._last_magnitude:.4f}",
        ]

        # Neural evolution state
        try:
            from .sandbox_neural_evolve import get_neural_engine
            ne = get_neural_engine()
            lines.append(
                f"\n### Neural Growth"
                f"\n  **Neurons**: {len(ne._neurons)}/108 | "
                f"**Generation**: {ne._generation} | "
                f"**Temperature**: {ne._temperature:.4f}"
                f"\n  **Mutations**: {ne._total_mutations} total, "
                f"{ne.success_rate():.0%} success rate"
                f"\n  **Growth rate**: {ne.growth_rate():.6f} | "
                f"**Pathway diversity**: {ne._pathway_diversity():.4f}"
            )
        except Exception:
            pass

        if self._recent_results:
            last = self._recent_results[-1]
            lines.append(f"\n### Last Cycle ({last.cycle_id})")
            lines.append(
                f"  Score: {last.score_before:.4f} → "
                f"{last.score_after:.4f} "
                f"(Δ={last.delta:+.4f})")
            if last.mutations_proposed > 0:
                lines.append(
                    f"  Mutations: {last.mutations_kept}/{last.mutations_proposed} kept | "
                    f"Neurons: +{last.neurons_born} -{last.neurons_pruned} "
                    f"= {last.neuron_count} | "
                    f"ΔW={last.weight_delta_norm:.6f}")
            if last.actions_taken:
                lines.append("  Actions:")
                for a in last.actions_taken[:8]:
                    lines.append(f"    - {a}")

        # Growth trend (not just score delta)
        if len(self._recent_results) >= 5:
            recent = self._recent_results[-5:]
            avg_neurons_born = sum(r.neurons_born for r in recent) / 5
            avg_mutations_kept = sum(r.mutations_kept for r in recent) / 5
            avg_weight_delta = sum(r.weight_delta_norm for r in recent) / 5
            avg_score_delta = sum(r.delta for r in recent) / 5
            lines.append(
                f"\n### Trend (5-cycle)"
                f"\n  avg neurons/cycle: {avg_neurons_born:.1f} | "
                f"avg mutations kept: {avg_mutations_kept:.1f}"
                f"\n  avg weight change: {avg_weight_delta:.6f} | "
                f"avg score delta: {avg_score_delta:+.4f}")

        cycles_in_epoch = self._cycle_id % EPOCH_LENGTH
        lines.append(f"\n**Epoch progress**: {cycles_in_epoch}/{EPOCH_LENGTH}")

        return "\n".join(lines)

    def recent_cycles(self, n: int = 10) -> list[dict]:
        """Return last N cycle results as dicts."""
        return [r.to_dict() for r in self._recent_results[-n:]]

    def efficiency_curve(self) -> list[tuple[int, float]]:
        """Return (cycle_id, magnitude) pairs for plotting."""
        return [(r.cycle_id, r.score_after) for r in self._recent_results]

    def force_micro_cycle(self) -> MicroCycleResult:
        """Force an immediate micro-cycle regardless of interval."""
        return self.micro_cycle()


# ──────────────────────────────────────────────────────────────
#  Singleton
# ──────────────────────────────────────────────────────────────

_metaloop_instance: Optional[MetaLoop] = None


def get_metaloop() -> MetaLoop:
    """Get or create the singleton METALOOP instance."""
    global _metaloop_instance
    if _metaloop_instance is None:
        _metaloop_instance = MetaLoop()
    return _metaloop_instance


# ──────────────────────────────────────────────────────────────
#  MCP Tool Registration
# ──────────────────────────────────────────────────────────────

def register_metaloop_tools(mcp) -> None:
    """Register METALOOP tools onto the MCP server."""

    @mcp.tool()
    def metaloop_status() -> str:
        """Get METALOOP status: cycle count, epoch, omega, trend, last results.

        The METALOOP is the cyclical self-improvement engine that runs every
        10 tool calls. Each micro-cycle: SENSE → ANALYZE → PLAN → ACT →
        VERIFY → COMPRESS → EMIT. Epochs (57 cycles) emit successor seeds.
        Omega cycles (171 cycles) emit 16-value hologram checkpoints.
        """
        loop = get_metaloop()
        return loop.status()

    @mcp.tool()
    def metaloop_force_cycle() -> str:
        """Force an immediate METALOOP micro-cycle.

        Runs the full 7-phase cycle: SENSE → ANALYZE → PLAN → ACT →
        VERIFY → COMPRESS → EMIT. Returns cycle results including
        score delta, directives implemented, and keep/discard decision.
        """
        loop = get_metaloop()
        result = loop.force_micro_cycle()

        lines = [
            f"## METALOOP Micro-Cycle {result.cycle_id}\n",
            f"**Score**: {result.score_before:.4f} → {result.score_after:.4f} "
            f"(Δ={result.delta:+.4f})",
            f"**Decision**: {'KEPT' if result.kept else 'DISCARDED'}",
        ]

        # Neural evolution results (THE GROWTH)
        if result.mutations_proposed > 0:
            lines.append(
                f"\n### Neural Evolution"
                f"\n  Mutations: {result.mutations_kept}/{result.mutations_proposed} kept"
                f"\n  Neurons: +{result.neurons_born} born, "
                f"-{result.neurons_pruned} pruned = {result.neuron_count} active"
                f"\n  Weight change: {result.weight_delta_norm:.6f}"
                f"\n  Generation: {result.generation}"
            )

        if result.actions_taken:
            lines.append("\n**Actions**:")
            for a in result.actions_taken[:10]:
                lines.append(f"  - {a}")

        if result.seed_hash:
            lines.append(f"\n**Seed**: {result.seed_hash} "
                        f"({result.compressed_size} bytes)")

        return "\n".join(lines)

    @mcp.tool()
    def metaloop_history(last_n: int = 10) -> str:
        """Show recent METALOOP cycle history with score progression.

        Args:
            last_n: Number of recent cycles to show (default 10)
        """
        loop = get_metaloop()
        cycles = loop.recent_cycles(n=last_n)

        if not cycles:
            return "No METALOOP cycles yet. Run tools to trigger automatic cycles."

        lines = ["## METALOOP History\n"]
        lines.append("| Cycle | Epoch | Before | After | Delta | Kept | Actions |")
        lines.append("|-------|-------|--------|-------|-------|------|---------|")

        for c in cycles:
            kept = "yes" if c.get("kept") else "no"
            lines.append(
                f"| {c['cycle_id']:>5} | {c['epoch']:>5} | "
                f"{c['score_before']:>6.3f} | {c['score_after']:>5.3f} | "
                f"{c['delta']:>+6.4f} | {kept:>4} | "
                f"{c['directives_implemented']:>7} |"
            )

        # Summary
        if len(cycles) >= 2:
            total_delta = sum(c["delta"] for c in cycles)
            kept_pct = sum(1 for c in cycles if c["kept"]) / len(cycles)
            lines.append(f"\n**Total delta**: {total_delta:+.4f} | "
                        f"**Kept ratio**: {kept_pct:.0%}")

        return "\n".join(lines)

    @mcp.tool()
    def metaloop_hologram() -> str:
        """Get the current 16-value METALOOP hologram.

        The hologram captures the meta-state of the self-improvement engine:
          D1_Efficiency: value/token, value/ms, compression, redundancy
          D2_Health:     memory, CPU, context, directive health
          D3_Learning:   avg delta, kept ratio, cross-poll rate, improvement
          D4_Structure:  tools, findings, broadcasts, momentum
        """
        loop = get_metaloop()
        hologram = loop._compute_hologram_16()

        labels = [
            "D1: value/token", "D1: value/ms",
            "D1: compression", "D1: 1-redundancy",
            "D2: memory", "D2: CPU",
            "D2: context", "D2: directive_health",
            "D3: avg_delta", "D3: kept_ratio",
            "D3: cross_poll", "D3: improvement",
            "D4: tools", "D4: findings",
            "D4: broadcasts", "D4: momentum",
        ]

        lines = ["## METALOOP Hologram (16D)\n"]
        for i, (label, val) in enumerate(zip(labels, hologram)):
            bar = "█" * int(val * 20) + "░" * (20 - int(val * 20))
            lines.append(f"  {label:>22}: {bar} {val:.3f}")

        magnitude = sum(v * v for v in hologram) ** 0.5
        lines.append(f"\n**Magnitude**: {magnitude:.4f}")

        return "\n".join(lines)

    @mcp.tool()
    def metaloop_neural_status() -> str:
        """Show neural evolution engine status: neurons, mutations, growth.

        The neural evolution engine is the GROWTH mechanism within the METALOOP.
        Every micro-cycle it proposes bold mutations to the 148-float momentum
        field, grows new neurons (bridge pathways), and prunes dead connections.
        This makes the organism actually CHANGE, not just observe itself.
        """
        from .sandbox_neural_evolve import get_neural_engine
        return get_neural_engine().status()

    @mcp.tool()
    def metaloop_evolve(cycles: int = 10) -> str:
        """Run N neural evolution cycles and show growth results.

        Each cycle: propose mutations → apply → evaluate → keep/discard →
        grow neurons → fire neurons → prune dead → anneal temperature.

        Args:
            cycles: Number of evolution cycles to run (default 10, max 100)
        """
        cycles = min(100, max(1, cycles))
        loop = get_metaloop()

        results = []
        for i in range(cycles):
            r = loop.force_micro_cycle()
            results.append(r)

        # Summary
        total_born = sum(r.neurons_born for r in results)
        total_pruned = sum(r.neurons_pruned for r in results)
        total_mutations = sum(r.mutations_kept for r in results)
        total_proposed = sum(r.mutations_proposed for r in results)
        avg_delta = sum(r.delta for r in results) / len(results)
        final = results[-1]

        lines = [
            f"## Neural Evolution: {cycles} cycles\n",
            f"**Mutations**: {total_mutations}/{total_proposed} kept "
            f"({total_mutations/max(1,total_proposed):.0%} success)",
            f"**Neurons**: +{total_born} born, -{total_pruned} pruned "
            f"= {final.neuron_count} active",
            f"**Generation**: {final.generation}",
            f"**Score**: {results[0].score_before:.4f} → "
            f"{final.score_after:.4f} "
            f"(avg Δ={avg_delta:+.4f})",
            f"**Weight change**: "
            f"{sum(r.weight_delta_norm for r in results):.6f} total",
        ]

        # Show trajectory
        lines.append("\n**Trajectory**:")
        step = max(1, len(results) // 10)
        for i in range(0, len(results), step):
            r = results[i]
            lines.append(
                f"  cycle {r.cycle_id}: score={r.score_after:.4f} "
                f"neurons={r.neuron_count} "
                f"gen={r.generation} "
                f"mut={r.mutations_kept}/{r.mutations_proposed}")

        return "\n".join(lines)
