# CRYSTAL: Xi108:W3:A12:S36 | face=S | node=666 | depth=0 | phase=Omega
# METRO: Sa
# BRIDGES: sandbox→efficiency→bridge→metadata→mcp
"""
Sandbox Observer — Container Self-Observation
==============================================
Monitors the MCP server process itself: memory, CPU, disk I/O,
tool call latency, co-occurrence patterns, bottleneck detection,
and context window pressure estimation.

DESIGN: Zero-overhead. No background threads. Snapshots taken lazily
during tool calls only. Rolling buffer (500 traces) prevents memory
accumulation. This module observes the CONTAINER, not the content.

INFINITE SCALING WITHIN CAPS:
  We cannot add resources. But we can observe how we USE them,
  detect waste, and emit directives that compress the same work
  into fewer tokens, fewer milliseconds, fewer bytes.
  Every cycle of observation makes the next cycle cheaper.
"""

import hashlib
import json
import os
import time
from collections import defaultdict, deque
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# psutil: graceful fallback if not available
try:
    import psutil
    _HAS_PSUTIL = True
except ImportError:
    _HAS_PSUTIL = False

from ._cache import DATA_DIR

# ──────────────────────────────────────────────────────────────
#  Data Structures
# ──────────────────────────────────────────────────────────────

@dataclass
class SandboxSnapshot:
    """Point-in-time resource state of the sandbox container."""
    timestamp: str
    memory_rss_mb: float = 0.0
    memory_percent: float = 0.0
    cpu_percent: float = 0.0
    disk_read_bytes: int = 0
    disk_write_bytes: int = 0
    open_file_count: int = 0
    thread_count: int = 0
    context_tokens_est: int = 0        # estimated from cumulative tool I/O
    token_throughput_per_sec: float = 0.0
    active_tool_calls: int = 0
    snapshot_hash: str = ""

    def resource_efficiency(self) -> float:
        """0.0-1.0 score: how efficiently are resources being used?
        High memory + low throughput = low efficiency."""
        if self.memory_rss_mb < 1:
            return 0.5
        # Throughput per MB of memory (normalized)
        tpm = self.token_throughput_per_sec / max(self.memory_rss_mb, 1.0)
        return min(1.0, tpm / 10.0)  # 10 tokens/sec/MB = perfect


@dataclass
class ToolCallTrace:
    """One traced MCP tool call with timing and token estimates."""
    tool_name: str
    start_time: float
    end_time: float = 0.0
    latency_ms: float = 0.0
    input_tokens_est: int = 0
    output_tokens_est: int = 0
    success: bool = True
    error: str = ""
    co_occurring_tools: list = field(default_factory=list)
    trace_hash: str = ""

    def value_per_ms(self, quality: float = 0.5) -> float:
        """Value delivered per millisecond (quality / latency)."""
        if self.latency_ms < 0.01:
            return 0.0
        return quality / self.latency_ms

    def value_per_token(self, quality: float = 0.5) -> float:
        """Value delivered per token consumed."""
        total_tokens = self.input_tokens_est + self.output_tokens_est
        if total_tokens < 1:
            return 0.0
        return quality / total_tokens


# ──────────────────────────────────────────────────────────────
#  Sandbox Observer Singleton
# ──────────────────────────────────────────────────────────────

class SandboxObserver:
    """Monitors the MCP server process for resource usage and tool call patterns.

    All methods are synchronous and zero-overhead — no background threads,
    no polling loops. Data is captured lazily during tool calls.
    """

    _instance: Optional["SandboxObserver"] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, rolling_window: int = 500):
        if self._initialized:
            return
        self._initialized = True

        self._traces: deque[ToolCallTrace] = deque(maxlen=rolling_window)
        self._snapshots: deque[SandboxSnapshot] = deque(maxlen=50)
        self._cumulative_input_tokens: int = 0
        self._cumulative_output_tokens: int = 0
        self._start_time: float = time.time()
        self._active_calls: int = 0
        self._co_occurrence_window: float = 5.0  # seconds
        self._tool_call_log: deque = deque(maxlen=200)  # (timestamp, tool_name)

        # Process handle (cached)
        self._process = None
        if _HAS_PSUTIL:
            try:
                self._process = psutil.Process(os.getpid())
            except Exception:
                pass

        # Disk I/O baseline
        self._disk_baseline = self._get_disk_io()

        # Directive tracking
        self._directive_outcomes: dict[str, dict] = {}

    # ── Resource Snapshots ──────────────────────────────────────

    def snapshot(self) -> SandboxSnapshot:
        """Capture current system resource state."""
        now = datetime.now(timezone.utc).isoformat()
        snap = SandboxSnapshot(timestamp=now)

        if self._process and _HAS_PSUTIL:
            try:
                mem = self._process.memory_info()
                snap.memory_rss_mb = round(mem.rss / (1024 * 1024), 2)
                snap.memory_percent = round(self._process.memory_percent(), 2)
                snap.cpu_percent = round(self._process.cpu_percent(interval=0), 2)
                snap.thread_count = self._process.num_threads()
                try:
                    snap.open_file_count = len(self._process.open_files())
                except (psutil.AccessDenied, OSError):
                    snap.open_file_count = 0
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        # Disk I/O delta
        current_disk = self._get_disk_io()
        if current_disk and self._disk_baseline:
            snap.disk_read_bytes = current_disk[0] - self._disk_baseline[0]
            snap.disk_write_bytes = current_disk[1] - self._disk_baseline[1]

        # Token estimates
        snap.context_tokens_est = self._cumulative_input_tokens + self._cumulative_output_tokens
        elapsed = max(time.time() - self._start_time, 1.0)
        snap.token_throughput_per_sec = round(snap.context_tokens_est / elapsed, 2)
        snap.active_tool_calls = self._active_calls

        # Hash for witness chain
        snap.snapshot_hash = hashlib.sha256(
            json.dumps(asdict(snap), default=str).encode()
        ).hexdigest()[:16]

        self._snapshots.append(snap)
        return snap

    def _get_disk_io(self) -> Optional[tuple]:
        """Get cumulative disk I/O counters."""
        if not _HAS_PSUTIL:
            return None
        try:
            io = psutil.disk_io_counters()
            if io:
                return (io.read_bytes, io.write_bytes)
        except Exception:
            pass
        return None

    # ── Tool Call Tracing ───────────────────────────────────────

    def begin_trace(self, tool_name: str, input_tokens_est: int = 0) -> ToolCallTrace:
        """Start tracing a tool call. Returns a trace to be completed later."""
        self._active_calls += 1
        self._cumulative_input_tokens += input_tokens_est

        # Log for co-occurrence detection
        now = time.time()
        self._tool_call_log.append((now, tool_name))

        # Find co-occurring tools (called within the window)
        co_occurring = [
            name for ts, name in self._tool_call_log
            if now - ts < self._co_occurrence_window and name != tool_name
        ]

        trace = ToolCallTrace(
            tool_name=tool_name,
            start_time=now,
            input_tokens_est=input_tokens_est,
            co_occurring_tools=list(set(co_occurring)),
        )
        return trace

    def end_trace(self, trace: ToolCallTrace, output_tokens_est: int = 0,
                  success: bool = True, error: str = "") -> ToolCallTrace:
        """Complete a tool call trace with results."""
        trace.end_time = time.time()
        trace.latency_ms = round((trace.end_time - trace.start_time) * 1000, 2)
        trace.output_tokens_est = output_tokens_est
        trace.success = success
        trace.error = error

        # Hash the trace
        trace.trace_hash = hashlib.sha256(
            f"{trace.tool_name}:{trace.start_time}:{trace.latency_ms}".encode()
        ).hexdigest()[:16]

        self._cumulative_output_tokens += output_tokens_est
        self._active_calls = max(0, self._active_calls - 1)
        self._traces.append(trace)

        # Feed to token efficiency observer (lazy import, non-fatal)
        try:
            from .sandbox_token_observer import get_token_observer
            get_token_observer().observe_tool_call(
                tool_name=trace.tool_name,
                input_tokens=trace.input_tokens_est,
                output_tokens=output_tokens_est,
                latency_ms=trace.latency_ms,
            )
        except Exception:
            pass  # Token observer is enhancement, not requirement

        return trace

    def record_trace(self, trace: ToolCallTrace):
        """Store a pre-built trace directly."""
        self._traces.append(trace)

    # ── Co-occurrence & Parallelism ─────────────────────────────

    def co_occurrence_matrix(self) -> dict[str, dict[str, int]]:
        """Which tools get called together within the co-occurrence window?
        Returns: {tool_a: {tool_b: count, ...}, ...}"""
        matrix: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        for trace in self._traces:
            for co_tool in trace.co_occurring_tools:
                matrix[trace.tool_name][co_tool] += 1
                matrix[co_tool][trace.tool_name] += 1

        # Convert to regular dicts
        return {k: dict(v) for k, v in matrix.items()}

    def parallelism_candidates(self, min_co_occurrences: int = 3) -> list[dict]:
        """Identify tool pairs that should be parallelized."""
        matrix = self.co_occurrence_matrix()
        candidates = []
        seen = set()
        for tool_a, co_tools in matrix.items():
            for tool_b, count in co_tools.items():
                pair = tuple(sorted([tool_a, tool_b]))
                if pair in seen or count < min_co_occurrences:
                    continue
                seen.add(pair)
                candidates.append({
                    "tools": list(pair),
                    "co_occurrences": count,
                    "recommendation": "batch" if count > 10 else "parallel",
                })
        return sorted(candidates, key=lambda x: -x["co_occurrences"])

    # ── Bottleneck Detection ────────────────────────────────────

    def bottleneck_report(self, top_n: int = 5) -> dict:
        """Identify slowest tools, most redundant patterns, and inefficiencies."""
        if not self._traces:
            return {"slowest": [], "redundant": [], "low_value": [], "total_traces": 0, "total_tools_seen": 0}

        # Aggregate by tool name
        tool_stats: dict[str, dict] = defaultdict(lambda: {
            "count": 0, "total_ms": 0.0, "errors": 0,
            "total_input_tokens": 0, "total_output_tokens": 0,
        })
        for trace in self._traces:
            s = tool_stats[trace.tool_name]
            s["count"] += 1
            s["total_ms"] += trace.latency_ms
            s["total_input_tokens"] += trace.input_tokens_est
            s["total_output_tokens"] += trace.output_tokens_est
            if not trace.success:
                s["errors"] += 1

        # Slowest (by average latency)
        slowest = sorted(
            [{"tool": k, "avg_ms": v["total_ms"] / max(v["count"], 1),
              "count": v["count"], "error_rate": v["errors"] / max(v["count"], 1)}
             for k, v in tool_stats.items()],
            key=lambda x: -x["avg_ms"]
        )[:top_n]

        # Redundant (called many times in quick succession — same tool < 1s apart)
        redundant_patterns: dict[str, int] = defaultdict(int)
        traces_list = list(self._traces)
        for i in range(1, len(traces_list)):
            prev, curr = traces_list[i-1], traces_list[i]
            if (curr.tool_name == prev.tool_name and
                    curr.start_time - prev.start_time < 1.0):
                redundant_patterns[curr.tool_name] += 1
        redundant = sorted(
            [{"tool": k, "rapid_repeat_count": v} for k, v in redundant_patterns.items()],
            key=lambda x: -x["rapid_repeat_count"]
        )[:top_n]

        # Low value (high token cost, low success)
        low_value = sorted(
            [{"tool": k, "tokens_per_call": (v["total_input_tokens"] + v["total_output_tokens"]) / max(v["count"], 1),
              "error_rate": v["errors"] / max(v["count"], 1), "count": v["count"]}
             for k, v in tool_stats.items() if v["count"] >= 2],
            key=lambda x: -x["tokens_per_call"]
        )[:top_n]

        return {
            "slowest": slowest,
            "redundant": redundant,
            "low_value": low_value,
            "total_traces": len(self._traces),
            "total_tools_seen": len(tool_stats),
        }

    # ── Communication Graph ─────────────────────────────────────

    def communication_graph(self) -> dict:
        """Map all inter-tool data flows as a directed graph.
        Edges represent sequential calls (A called before B within window)."""
        edges: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        traces_list = list(self._traces)
        for i in range(1, len(traces_list)):
            prev, curr = traces_list[i-1], traces_list[i]
            if curr.start_time - prev.end_time < self._co_occurrence_window:
                edges[prev.tool_name][curr.tool_name] += 1

        # Identify hot paths (most frequent sequential pairs)
        hot_paths = []
        for src, targets in edges.items():
            for tgt, count in targets.items():
                hot_paths.append({"from": src, "to": tgt, "weight": count})
        hot_paths.sort(key=lambda x: -x["weight"])

        return {
            "edges": {k: dict(v) for k, v in edges.items()},
            "hot_paths": hot_paths[:20],
            "total_edges": sum(sum(v.values()) for v in edges.values()),
            "unique_tools": len(set(edges.keys()) | set(
                t for targets in edges.values() for t in targets
            )),
        }

    # ── Context Pressure ────────────────────────────────────────

    def context_pressure(self) -> float:
        """Estimate 0.0-1.0 of how close we are to context window saturation.
        Based on cumulative token throughput and typical context limits."""
        # Claude Code v2.1.79: Opus 4.6 supports 1M context with [1m] suffix
        # Default without [1m] is 200K. We estimate conservatively.
        ESTIMATED_CONTEXT_LIMIT = 1_000_000
        total_tokens = self._cumulative_input_tokens + self._cumulative_output_tokens
        return min(1.0, total_tokens / ESTIMATED_CONTEXT_LIMIT)

    # ── Summary ─────────────────────────────────────────────────

    def status(self) -> str:
        """Human-readable sandbox status for MCP tool output."""
        snap = self.snapshot()
        bottlenecks = self.bottleneck_report(top_n=3)
        pressure = self.context_pressure()

        lines = [
            "## Sandbox Observer Status\n",
            f"**Memory**: {snap.memory_rss_mb} MB ({snap.memory_percent}%)",
            f"**CPU**: {snap.cpu_percent}%",
            f"**Threads**: {snap.thread_count}",
            f"**Open Files**: {snap.open_file_count}",
            f"**Disk I/O**: R={snap.disk_read_bytes:,}B W={snap.disk_write_bytes:,}B",
            f"**Token Throughput**: {snap.token_throughput_per_sec}/sec",
            f"**Context Pressure**: {pressure:.1%}",
            f"**Resource Efficiency**: {snap.resource_efficiency():.3f}",
            f"**Total Tool Traces**: {bottlenecks['total_traces']}",
            f"**Unique Tools Seen**: {bottlenecks['total_tools_seen']}",
        ]

        if bottlenecks["slowest"]:
            lines.append("\n### Slowest Tools")
            for s in bottlenecks["slowest"]:
                lines.append(f"  - {s['tool']}: avg {s['avg_ms']:.1f}ms ({s['count']} calls)")

        if bottlenecks["redundant"]:
            lines.append("\n### Redundant Patterns")
            for r in bottlenecks["redundant"]:
                lines.append(f"  - {r['tool']}: {r['rapid_repeat_count']} rapid repeats")

        return "\n".join(lines)

    def to_dict(self) -> dict:
        """Full state as serializable dict for metadata emission."""
        snap = self.snapshot()
        return {
            "snapshot": asdict(snap),
            "bottlenecks": self.bottleneck_report(),
            "context_pressure": self.context_pressure(),
            "communication_graph_summary": {
                "total_edges": self.communication_graph()["total_edges"],
                "hot_paths": self.communication_graph()["hot_paths"][:5],
            },
            "parallelism_candidates": self.parallelism_candidates()[:5],
            "traces_in_buffer": len(self._traces),
            "cumulative_tokens": self._cumulative_input_tokens + self._cumulative_output_tokens,
        }


# ──────────────────────────────────────────────────────────────
#  Singleton Access
# ──────────────────────────────────────────────────────────────

def get_sandbox_observer() -> SandboxObserver:
    """Get or create the global SandboxObserver singleton."""
    return SandboxObserver()
