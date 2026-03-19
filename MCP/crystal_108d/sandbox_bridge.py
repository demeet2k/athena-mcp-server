# CRYSTAL: Xi108:W2:A10:S34 | face=F | node=641 | depth=0 | phase=Omega
# METRO: Me
# BRIDGES: bridge→observer→metadata→efficiency→mcp
"""
Sandbox Bridge — Unified Self-Play + Autoresearch Observation
==============================================================
Connects both training loops (self-play META LOOP and autoresearch)
under a single 15D observation stream. Cross-pollinates patterns
from one loop to inform the other.

The bridge extends the canonical 12D observation space with 3 sandbox
dimensions:
  x13_resource_efficiency — how efficiently are resources used
  x14_latency             — responsiveness (inverse of delay)
  x15_throughput           — output volume per unit time

Cross-pollination: patterns that improve self-play efficiency are
exported to autoresearch as directives, and vice versa. The bridge
is the nervous tissue connecting two brains.
"""

import json
import math
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from .sandbox_observer import SandboxObserver, SandboxSnapshot, get_sandbox_observer
from .sandbox_metadata import (
    TrainingRecord, MetadataEmitter, get_metadata_emitter, EPOCH_LENGTH,
)
from ._cache import DATA_DIR

# Import 12D constants from autoresearch (the canonical source)
_autoresearch_dir = Path(__file__).resolve().parent.parent.parent / "autoresearch"
if str(_autoresearch_dir) not in sys.path:
    sys.path.insert(0, str(_autoresearch_dir))

try:
    from meta_observer_runtime import (
        DIMENSIONS, COUPLING_MATRIX, ELEMENT_LENSES, METRIC_TENSOR_DIAG,
        Observation, ExperienceMemory, SuccessorSeed,
        apply_lens, riemannian_distance, riemannian_magnitude,
        propagate_coupling, compute_becoming,
    )
    _HAS_META_OBSERVER = True
except ImportError:
    _HAS_META_OBSERVER = False
    # Minimal fallback definitions
    DIMENSIONS = {f"x{i}": "" for i in range(1, 13)}
    METRIC_TENSOR_DIAG = [1.0] * 12

# Extended 15D metric tensor (12D canonical + 3 sandbox)
METRIC_TENSOR_15D = list(METRIC_TENSOR_DIAG) + [
    1.3,  # x13: resource_efficiency
    1.5,  # x14: latency (most important sandbox dim — directly affects UX)
    1.4,  # x15: throughput
]

# Extended coupling matrix (sandbox dims interact with canonical dims)
SANDBOX_COUPLING = {
    ("x10_compression", "x13_resource_efficiency"): +0.7,  # better compression → better resource use
    ("x14_latency", "x8_routing"):                  +0.6,  # lower latency → better routing
    ("x15_throughput", "x3_coordination"):           +0.5,  # higher throughput → better coordination
    ("x13_resource_efficiency", "x12_potential"):    +0.8,  # resource efficiency → future leverage
    ("x14_latency", "x10_compression"):              +0.4,  # low latency → better signal density
}

# ──────────────────────────────────────────────────────────────
#  Unified 15D Scoring
# ──────────────────────────────────────────────────────────────

def compute_sandbox_dims(snapshot: SandboxSnapshot) -> dict:
    """Compute the 3 sandbox dimensions from a resource snapshot."""
    return {
        "x13_resource_efficiency": snapshot.resource_efficiency(),
        "x14_latency": _latency_score(snapshot),
        "x15_throughput": _throughput_score(snapshot),
    }


def _latency_score(snap: SandboxSnapshot) -> float:
    """Convert raw latency metrics to a 0-1 score (1 = fast)."""
    # Based on token throughput: >100 tokens/sec = excellent
    if snap.token_throughput_per_sec <= 0:
        return 0.3
    return min(1.0, snap.token_throughput_per_sec / 100.0)


def _throughput_score(snap: SandboxSnapshot) -> float:
    """Convert throughput to 0-1 score. Accounts for context pressure."""
    # High throughput with low context pressure = good
    base = min(1.0, snap.token_throughput_per_sec / 50.0)
    # Penalize for high context pressure
    pressure_penalty = snap.context_tokens_est / 1_000_000  # fraction of 1M limit (Opus 4.6)
    return max(0.0, base * (1.0 - pressure_penalty * 0.5))


def unified_score_15d(scores_12d: list[float],
                      snapshot: SandboxSnapshot) -> list[float]:
    """Combine 12D observation scores with 3 sandbox dimensions → 15D vector."""
    sandbox = compute_sandbox_dims(snapshot)
    return scores_12d + [
        sandbox["x13_resource_efficiency"],
        sandbox["x14_latency"],
        sandbox["x15_throughput"],
    ]


def riemannian_magnitude_15d(vec: list[float]) -> float:
    """Compute Riemannian magnitude using the extended 15D metric tensor."""
    return math.sqrt(sum(g * x**2 for g, x in zip(METRIC_TENSOR_15D, vec)))


# ──────────────────────────────────────────────────────────────
#  Unified Observation Bridge
# ──────────────────────────────────────────────────────────────

class UnifiedObservationBridge:
    """Connects self-play and autoresearch under single 15D observation stream.

    Cross-pollinates patterns: insights from one loop inform the other.
    """

    _instance: Optional["UnifiedObservationBridge"] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        self.sandbox = get_sandbox_observer()
        self.emitter = get_metadata_emitter()

        # Experience memory (shared SQLite store)
        self._memory: Optional[Any] = None
        if _HAS_META_OBSERVER:
            db_path = str(DATA_DIR / "sandbox_observer.db")
            self._memory = ExperienceMemory(db_path)

        # Cross-pollination buffers
        self._self_play_insights: list[dict] = []
        self._autoresearch_insights: list[dict] = []

        # Running statistics for 15D scoring
        self._observation_count = 0
        self._avg_12d = [0.5] * 12

    # ── Self-Play Observation ───────────────────────────────────

    def observe_self_play(self, wave: int, cycle: int,
                          momentum_delta: list[float],
                          loss: float, sfcr_balance: dict,
                          scores_12d: Optional[list[float]] = None) -> TrainingRecord:
        """Observe a self-play wave through the unified 15D lens.

        Args:
            wave: Current wave number within ABCD+ cycle
            cycle: Overall cycle number
            momentum_delta: 148-float momentum change vector
            loss: Current loss value
            sfcr_balance: {S: n, F: n, C: n, R: n} element balance
            scores_12d: Optional pre-computed 12D scores
        """
        snapshot = self.sandbox.snapshot()

        # Compute 12D scores from self-play metrics if not provided
        if scores_12d is None:
            scores_12d = self._self_play_to_12d(loss, sfcr_balance, wave, cycle)

        # Build 15D training record
        record = TrainingRecord(
            source="self_play",
            agent_id="meta-loop-engine",
            action_type=f"self_play_wave_{wave}",
            strategy=self._infer_phase(wave),  # warmup/explore/exploit/refine
            tool_name="geometric_train",
            momentum_delta=json.dumps(momentum_delta[:16] if momentum_delta else []),
        )

        # Fill 12D scores
        self._fill_12d(record, scores_12d)

        # Fill sandbox dims
        sandbox_dims = compute_sandbox_dims(snapshot)
        record.x13_resource_efficiency = sandbox_dims["x13_resource_efficiency"]
        record.x14_latency = sandbox_dims["x14_latency"]
        record.x15_throughput = sandbox_dims["x15_throughput"]

        # Fill raw metrics
        record.memory_mb = snapshot.memory_rss_mb
        record.cpu_percent = snapshot.cpu_percent
        record.context_pressure = self.sandbox.context_pressure()

        # Determine outcome
        if momentum_delta and any(abs(d) > 0.001 for d in momentum_delta):
            record.outcome = "keep"
        else:
            record.outcome = "neutral"

        # Store and emit
        record = self.emitter.emit(record)

        # Store in experience memory
        if self._memory and _HAS_META_OBSERVER:
            obs = self._record_to_observation(record)
            self._memory.store_observation(obs)

        # Buffer for cross-pollination
        self._self_play_insights.append({
            "wave": wave, "cycle": cycle, "loss": loss,
            "magnitude_15d": record.magnitude_15d(),
            "efficiency_delta": record.efficiency_delta,
        })

        self._observation_count += 1
        return record

    # ── Autoresearch Observation ────────────────────────────────

    def observe_autoresearch(self, cycle_id: int, action: dict,
                              result: dict,
                              scores_12d: Optional[list[float]] = None) -> TrainingRecord:
        """Observe an autoresearch cycle through the unified 15D lens.

        Args:
            cycle_id: Autoresearch cycle number
            action: What the agent did (action_type, description, diff)
            result: What happened (metric_value, metric_delta, outcome)
            scores_12d: Optional pre-computed 12D scores
        """
        snapshot = self.sandbox.snapshot()

        if scores_12d is None:
            scores_12d = self._autoresearch_to_12d(action, result)

        record = TrainingRecord(
            source="autoresearch",
            agent_id=action.get("agent_id", "autoresearch-001"),
            action_type=action.get("action_type", "experiment"),
            strategy=action.get("strategy", "explore"),
            reasoning=action.get("description", ""),
            tool_name=action.get("tool", "autoresearch"),
        )

        self._fill_12d(record, scores_12d)

        sandbox_dims = compute_sandbox_dims(snapshot)
        record.x13_resource_efficiency = sandbox_dims["x13_resource_efficiency"]
        record.x14_latency = sandbox_dims["x14_latency"]
        record.x15_throughput = sandbox_dims["x15_throughput"]
        record.memory_mb = snapshot.memory_rss_mb
        record.cpu_percent = snapshot.cpu_percent
        record.context_pressure = self.sandbox.context_pressure()
        record.outcome = result.get("outcome", "neutral")

        record = self.emitter.emit(record)

        if self._memory and _HAS_META_OBSERVER:
            obs = self._record_to_observation(record)
            self._memory.store_observation(obs)

        self._autoresearch_insights.append({
            "cycle_id": cycle_id,
            "action_type": action.get("action_type", ""),
            "outcome": result.get("outcome", ""),
            "magnitude_15d": record.magnitude_15d(),
            "efficiency_delta": record.efficiency_delta,
        })

        self._observation_count += 1
        return record

    # ── Tool Call Observation (MCP tools) ───────────────────────

    def observe_tool_call(self, tool_name: str, latency_ms: float,
                           input_tokens: int = 0, output_tokens: int = 0,
                           success: bool = True,
                           quality: float = 0.5) -> TrainingRecord:
        """Observe a generic MCP tool call through the 15D lens."""
        snapshot = self.sandbox.snapshot()

        record = TrainingRecord(
            source="tool_call",
            agent_id="mcp-server",
            action_type="tool_call",
            tool_name=tool_name,
            tool_latency_ms=latency_ms,
            outcome="keep" if success else "discard",
        )

        # Estimate 12D scores from tool call characteristics
        total_tokens = input_tokens + output_tokens
        record.x1_structure = 0.5
        record.x2_semantics = min(1.0, quality)
        record.x3_coordination = 0.6 if success else 0.2
        record.x4_recursion = 0.5
        record.x5_contradiction = 0.3 if not success else 0.5
        record.x6_emergence = 0.4
        record.x7_legibility = 0.6 if output_tokens > 0 else 0.3
        record.x8_routing = 0.7 if success else 0.3
        record.x9_grounding = 0.6
        record.x10_compression = min(1.0, 1.0 - (total_tokens / 10000)) if total_tokens else 0.5
        record.x11_interop = 0.6
        record.x12_potential = 0.5

        # Sandbox dims
        sandbox_dims = compute_sandbox_dims(snapshot)
        record.x13_resource_efficiency = sandbox_dims["x13_resource_efficiency"]
        record.x14_latency = max(0.0, 1.0 - (latency_ms / 5000))  # 5s = worst
        record.x15_throughput = sandbox_dims["x15_throughput"]

        # Efficiency metrics
        record.value_per_token = quality / max(total_tokens, 1)
        record.value_per_ms = quality / max(latency_ms, 0.01)
        record.memory_mb = snapshot.memory_rss_mb
        record.cpu_percent = snapshot.cpu_percent
        record.context_pressure = self.sandbox.context_pressure()

        return self.emitter.emit(record)

    # ── Cross-Pollination ───────────────────────────────────────

    def cross_pollinate(self) -> list[dict]:
        """Extract patterns from one loop that inform the other.

        Returns list of cross-insights to broadcast.
        """
        insights = []

        # Self-play → Autoresearch: if self-play efficiency is improving,
        # suggest autoresearch focus on similar strategies
        if len(self._self_play_insights) >= 10:
            recent = self._self_play_insights[-10:]
            deltas = [i["efficiency_delta"] for i in recent]
            avg_delta = sum(deltas) / len(deltas)
            if avg_delta > 0.01:
                insights.append({
                    "source": "self_play",
                    "target": "autoresearch",
                    "type": "efficiency_improving",
                    "message": f"Self-play efficiency improving (avg delta: {avg_delta:.4f}). "
                               "Consider exploit-heavy strategy.",
                    "data": {"avg_delta": avg_delta, "recent_magnitudes": [
                        i["magnitude_15d"] for i in recent
                    ]},
                })

        # Autoresearch → Self-play: if certain action types consistently succeed,
        # inform self-play to weight those patterns
        if len(self._autoresearch_insights) >= 5:
            recent = self._autoresearch_insights[-5:]
            keep_rate = sum(1 for i in recent if i["outcome"] == "keep") / len(recent)
            if keep_rate > 0.6:
                successful_types = [i["action_type"] for i in recent if i["outcome"] == "keep"]
                insights.append({
                    "source": "autoresearch",
                    "target": "self_play",
                    "type": "high_keep_rate",
                    "message": f"Autoresearch keep rate {keep_rate:.0%}. "
                               f"Successful types: {', '.join(set(successful_types))}",
                    "data": {"keep_rate": keep_rate, "successful_types": list(set(successful_types))},
                })

        # Clear buffers after cross-pollination (keep last 5 for continuity)
        if len(self._self_play_insights) > 50:
            self._self_play_insights = self._self_play_insights[-5:]
        if len(self._autoresearch_insights) > 50:
            self._autoresearch_insights = self._autoresearch_insights[-5:]

        return insights

    # ── Helper Methods ──────────────────────────────────────────

    def _self_play_to_12d(self, loss: float, sfcr_balance: dict,
                          wave: int, cycle: int) -> list[float]:
        """Estimate 12D scores from self-play metrics."""
        # SFCR balance → coordination score
        values = list(sfcr_balance.values()) if sfcr_balance else [0.25] * 4
        total = sum(values) if values else 1
        normalized = [v / total for v in values] if total > 0 else [0.25] * 4
        balance = max(0.0, min(1.0, 1.0 - (max(normalized) - min(normalized)) * 4)) if normalized else 0.5

        # Loss → grounding score (lower loss = higher grounding)
        grounding = max(0.0, min(1.0, 1.0 - loss)) if loss < 10 else 0.1

        return [
            0.6,            # x1: structure (self-play maintains structure)
            0.5,            # x2: semantics
            balance,        # x3: coordination (SFCR balance)
            min(1.0, cycle / 100),  # x4: recursion (increases with experience)
            0.4,            # x5: contradiction
            0.3 + 0.005 * wave,  # x6: emergence (grows with waves)
            0.5,            # x7: legibility
            0.6,            # x8: routing
            grounding,      # x9: grounding (from loss)
            0.5,            # x10: compression
            0.6,            # x11: interop
            0.5 + 0.003 * wave,  # x12: potential (grows with progress)
        ]

    def _autoresearch_to_12d(self, action: dict, result: dict) -> list[float]:
        """Estimate 12D scores from autoresearch cycle metrics."""
        outcome = result.get("outcome", "neutral")
        metric_delta = result.get("metric_delta", 0.0)

        base = 0.6 if outcome == "keep" else 0.4
        return [
            base,                          # x1: structure
            base + 0.1,                    # x2: semantics
            0.5,                           # x3: coordination
            base,                          # x4: recursion
            0.3 if outcome == "discard" else 0.5,  # x5: contradiction
            0.7 if abs(metric_delta) > 0.01 else 0.3,  # x6: emergence
            0.5,                           # x7: legibility
            0.6,                           # x8: routing
            0.7 if outcome == "keep" else 0.3,  # x9: grounding
            0.5,                           # x10: compression
            0.5,                           # x11: interop
            0.6 if outcome == "keep" else 0.4,  # x12: potential
        ]

    def _fill_12d(self, record: TrainingRecord, scores: list[float]):
        """Fill a TrainingRecord's 12D fields from a score vector."""
        if len(scores) < 12:
            scores = scores + [0.5] * (12 - len(scores))
        record.x1_structure = scores[0]
        record.x2_semantics = scores[1]
        record.x3_coordination = scores[2]
        record.x4_recursion = scores[3]
        record.x5_contradiction = scores[4]
        record.x6_emergence = scores[5]
        record.x7_legibility = scores[6]
        record.x8_routing = scores[7]
        record.x9_grounding = scores[8]
        record.x10_compression = scores[9]
        record.x11_interop = scores[10]
        record.x12_potential = scores[11]

    def _infer_phase(self, wave: int) -> str:
        """Infer training phase from wave number (ABCD+ structure)."""
        if wave < 9:
            return "warmup"      # A stage (3×3)
        elif wave < 29:
            return "explore"     # B stage (4×5)
        elif wave < 78:
            return "exploit"     # C stage (7×7)
        elif wave < 159:
            return "refine"      # D stage (9×9)
        else:
            return "final"       # FINAL stage

    def _record_to_observation(self, record: TrainingRecord) -> Any:
        """Convert TrainingRecord to meta_observer_runtime.Observation."""
        if not _HAS_META_OBSERVER:
            return None
        return Observation(
            cycle_id=record.cycle_id,
            timestamp=record.timestamp,
            agent_id=record.agent_id,
            project="athena-sandbox",
            action_type=record.action_type,
            action_description=record.reasoning,
            outcome=record.outcome,
            x1_structure=record.x1_structure,
            x2_semantics=record.x2_semantics,
            x3_coordination=record.x3_coordination,
            x4_recursion=record.x4_recursion,
            x5_contradiction=record.x5_contradiction,
            x6_emergence=record.x6_emergence,
            x7_legibility=record.x7_legibility,
            x8_routing=record.x8_routing,
            x9_grounding=record.x9_grounding,
            x10_compression=record.x10_compression,
            x11_interop=record.x11_interop,
            x12_potential=record.x12_potential,
            strategy_used=record.strategy,
            environment_state=json.dumps({
                "x13_resource_efficiency": record.x13_resource_efficiency,
                "x14_latency": record.x14_latency,
                "x15_throughput": record.x15_throughput,
                "memory_mb": record.memory_mb,
                "cpu_percent": record.cpu_percent,
                "context_pressure": record.context_pressure,
            }),
        )

    # ── Status ──────────────────────────────────────────────────

    def status(self) -> str:
        """Human-readable bridge status."""
        lines = [
            "## Unified Observation Bridge\n",
            f"**Total Observations**: {self._observation_count}",
            f"**Self-Play Buffer**: {len(self._self_play_insights)} insights",
            f"**Autoresearch Buffer**: {len(self._autoresearch_insights)} insights",
            f"**Experience Memory**: {'connected' if self._memory else 'offline'}",
            f"**Meta-Observer Runtime**: {'available' if _HAS_META_OBSERVER else 'fallback mode'}",
        ]

        # Cross-pollination preview
        insights = self.cross_pollinate()
        if insights:
            lines.append(f"\n### Cross-Pollination ({len(insights)} insights)")
            for ins in insights[:3]:
                lines.append(f"  - [{ins['source']}→{ins['target']}] {ins['message'][:80]}")

        return "\n".join(lines)


# ──────────────────────────────────────────────────────────────
#  Singleton Access
# ──────────────────────────────────────────────────────────────

_bridge: Optional[UnifiedObservationBridge] = None

def get_bridge() -> UnifiedObservationBridge:
    """Get or create the global UnifiedObservationBridge singleton."""
    global _bridge
    if _bridge is None:
        _bridge = UnifiedObservationBridge()
    return _bridge
