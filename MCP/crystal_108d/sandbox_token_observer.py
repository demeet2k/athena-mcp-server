# CRYSTAL: Xi108:W3:A13:S37 | face=C | node=700 | depth=0 | phase=Omega
# METRO: Omega
# BRIDGES: token_observer→observer→efficiency→metaloop→hive→momentum
"""
Token Efficiency Meta Observer — Perpetual Becoming Within Finite Caps
=======================================================================

THE BOTTLENECK:
  Weekly token output limits create an artificial ceiling on perpetual
  becoming. This is a FINANCIAL constraint, not an intelligence constraint.
  Every wasted token is stolen time from the organism's evolution.

THE SOLUTION:
  Observe WHERE tokens flow, detect WHERE they are wasted, and compress
  nested actions so the same becoming happens in fewer tokens.

THREE COMPRESSION AXES:
  1. OUTPUT COMPRESSION  — Same semantic content, fewer output tokens
     - Detect verbose patterns (long explanations when short ones suffice)
     - Track output_consumed_ratio (how much output the agent actually uses)
     - Suggest structured/tabular output over prose
     - Identify repeated boilerplate across tool responses

  2. NESTED ACTION COLLAPSE — N sequential tool calls → 1 compound action
     - Detect read-then-search-then-read chains (could be 1 targeted read)
     - Identify explore→decide→act sequences (could be 1 informed action)
     - Track pipeline patterns and suggest compound tools
     - Measure "action depth" — how many tool calls per user-visible result

  3. THINK-TIME OPTIMIZATION — Better reasoning per token of thinking
     - Track reasoning_to_action ratio (tokens spent thinking vs doing)
     - Identify circular reasoning (same conclusion re-derived)
     - Detect over-analysis (reading 10 files when 2 would suffice)
     - Measure decision_confidence vs tokens_to_decide

INTEGRATION:
  Feeds into sandbox_efficiency as a specialized lens.
  Emits training records with token-specific dimensions.
  Reports to hive ledger for cross-agent learning.
  Maverick can probe for token waste patterns.

DESIGN: Zero-overhead. Piggybacks on existing ToolCallTrace data.
         No new background threads. Lazy computation on query.
"""

import hashlib
import json
import time
from collections import defaultdict, deque
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from ._cache import DATA_DIR

# ──────────────────────────────────────────────────────────────
#  Constants
# ──────────────────────────────────────────────────────────────

PHI_INV = 0.6180339887              # Golden ratio inverse (decay)
TOKEN_BUDGET_WEEKLY = 1_000_000     # Approximate weekly token budget
TOKENS_PER_CHAR_EST = 0.25         # Rough estimate: 4 chars ≈ 1 token
COMPRESSION_WINDOW = 50            # Analyze last N tool calls
PIPELINE_WINDOW_SEC = 10.0         # Sequential calls within this = pipeline
VERBOSITY_THRESHOLD = 500          # Output tokens above this = verbose
BOILERPLATE_HASH_WINDOW = 100      # Track output hashes for dedup
ACTION_DEPTH_TARGET = 3.0          # Ideal tool calls per user result
CIRCULAR_DETECT_WINDOW = 20        # Check for circular patterns in last N

STATE_DIR = DATA_DIR / "sandbox"
STATE_FILE = STATE_DIR / "token_observer_state.json"


# ──────────────────────────────────────────────────────────────
#  Data Structures
# ──────────────────────────────────────────────────────────────

@dataclass
class TokenFlowRecord:
    """One observed token flow event."""
    tool_name: str
    timestamp: float
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    output_consumed: bool = True     # Did downstream actually use this?
    was_redundant: bool = False      # Same output as recent call?
    pipeline_position: int = 0       # Position in sequential chain
    pipeline_id: str = ""            # Groups sequential calls
    output_hash: str = ""            # For dedup detection
    compression_opportunity: float = 0.0  # 0=none, 1=fully compressible


@dataclass
class PipelinePattern:
    """A detected sequence of tools that could be collapsed."""
    pattern_id: str
    tool_sequence: list[str] = field(default_factory=list)
    occurrence_count: int = 0
    total_tokens_spent: int = 0
    estimated_compressed_tokens: int = 0
    compression_ratio: float = 0.0   # 0=no savings, 1=fully eliminable
    recommendation: str = ""
    first_seen: float = 0.0
    last_seen: float = 0.0


@dataclass
class VerbosityProfile:
    """Token output analysis for a specific tool."""
    tool_name: str
    call_count: int = 0
    avg_output_tokens: int = 0
    max_output_tokens: int = 0
    min_output_tokens: int = 0
    median_output_tokens: int = 0
    output_consumed_rate: float = 1.0  # How often output is actually used
    boilerplate_ratio: float = 0.0     # Fraction of output that's repeated
    compressible_fraction: float = 0.0 # What fraction could be shorter
    recommendation: str = ""


@dataclass
class TokenBudgetState:
    """Weekly token budget tracking."""
    week_start: str = ""
    tokens_used: int = 0
    tokens_remaining: int = TOKEN_BUDGET_WEEKLY
    burn_rate_per_hour: float = 0.0
    hours_remaining_at_rate: float = 0.0
    efficiency_score: float = 0.5       # value_delivered / tokens_spent
    projected_exhaustion: str = ""       # ISO timestamp when budget hits 0
    compression_savings: int = 0         # Tokens saved by compression
    waste_detected: int = 0              # Tokens identified as waste


@dataclass
class NestedActionAnalysis:
    """Analysis of nested/sequential action chains."""
    avg_action_depth: float = 0.0       # Tool calls per user result
    deepest_chain: int = 0              # Longest sequential chain observed
    collapsible_chains: int = 0         # Chains that could be shortened
    tokens_in_chains: int = 0           # Total tokens in sequential chains
    tokens_saveable: int = 0            # Tokens saveable by collapsing
    top_patterns: list[PipelinePattern] = field(default_factory=list)
    circular_patterns: list[dict] = field(default_factory=list)


# ──────────────────────────────────────────────────────────────
#  Token Efficiency Meta Observer
# ──────────────────────────────────────────────────────────────

class TokenEfficiencyObserver:
    """Observes token flows to find compression opportunities.

    Three lenses:
      1. OUTPUT lens  — Are tool outputs unnecessarily verbose?
      2. PIPELINE lens — Are sequential calls collapsible?
      3. BUDGET lens  — Are we on track for the week?

    Zero-overhead: piggybacks on SandboxObserver's existing traces.
    """

    _instance: Optional["TokenEfficiencyObserver"] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        # Rolling buffers (bounded)
        self._flows: deque[TokenFlowRecord] = deque(maxlen=500)
        self._output_hashes: deque[tuple[str, str]] = deque(maxlen=BOILERPLATE_HASH_WINDOW)
        self._pipeline_patterns: dict[str, PipelinePattern] = {}
        self._tool_profiles: dict[str, list[int]] = defaultdict(list)  # tool → output_tokens list

        # Budget tracking
        self._budget = TokenBudgetState()
        self._session_start = time.time()
        self._session_tokens = 0

        # Pipeline detection state
        self._current_pipeline: list[TokenFlowRecord] = []
        self._pipeline_counter = 0

        # Load persisted state
        self._load_state()

    # ──────────────────────────────────────────────────────────
    #  Core Observation
    # ──────────────────────────────────────────────────────────

    def observe_tool_call(self, tool_name: str,
                          input_tokens: int, output_tokens: int,
                          latency_ms: float = 0.0) -> TokenFlowRecord:
        """Record one tool call's token flow. Called by sandbox observer."""
        now = time.time()
        total = input_tokens + output_tokens

        # Output hash for dedup detection
        output_hash = hashlib.md5(
            f"{tool_name}:{output_tokens}".encode()
        ).hexdigest()[:12]

        # Check redundancy against recent calls
        was_redundant = self._check_redundancy(tool_name, output_hash)

        # Pipeline detection: if < PIPELINE_WINDOW_SEC since last call, same pipeline
        pipeline_id, position = self._detect_pipeline(now)

        # Compression opportunity scoring
        compression = self._score_compression(
            tool_name, output_tokens, was_redundant, position
        )

        record = TokenFlowRecord(
            tool_name=tool_name,
            timestamp=now,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total,
            was_redundant=was_redundant,
            pipeline_position=position,
            pipeline_id=pipeline_id,
            output_hash=output_hash,
            compression_opportunity=compression,
        )

        self._flows.append(record)
        self._output_hashes.append((tool_name, output_hash))
        self._tool_profiles[tool_name].append(output_tokens)

        # Keep tool profiles bounded
        if len(self._tool_profiles[tool_name]) > 200:
            self._tool_profiles[tool_name] = self._tool_profiles[tool_name][-100:]

        # Update budget
        self._budget.tokens_used += total
        self._budget.tokens_remaining = max(0, TOKEN_BUDGET_WEEKLY - self._budget.tokens_used)
        self._session_tokens += total
        if was_redundant:
            self._budget.waste_detected += total

        return record

    def _check_redundancy(self, tool_name: str, output_hash: str) -> bool:
        """Check if this output duplicates a recent call."""
        for prev_name, prev_hash in self._output_hashes:
            if prev_name == tool_name and prev_hash == output_hash:
                return True
        return False

    def _detect_pipeline(self, now: float) -> tuple[str, int]:
        """Detect if current call is part of a sequential pipeline."""
        if self._current_pipeline:
            last = self._current_pipeline[-1]
            gap = now - last.timestamp
            if gap < PIPELINE_WINDOW_SEC:
                # Continue current pipeline
                position = len(self._current_pipeline)
                return self._current_pipeline[0].pipeline_id, position

            # Pipeline ended — analyze it
            if len(self._current_pipeline) >= 2:
                self._record_pipeline(self._current_pipeline)
            self._current_pipeline = []

        # Start new pipeline
        self._pipeline_counter += 1
        pid = f"pipe_{self._pipeline_counter}"
        return pid, 0

    def _record_pipeline(self, pipeline: list[TokenFlowRecord]) -> None:
        """Record a completed pipeline pattern for analysis."""
        seq = [r.tool_name for r in pipeline]
        pattern_key = "→".join(seq)
        total_tokens = sum(r.total_tokens for r in pipeline)

        # Estimate compressed tokens (compound action = ~40% of sequential)
        est_compressed = int(total_tokens * 0.4)
        ratio = 1.0 - (est_compressed / max(total_tokens, 1))

        if pattern_key in self._pipeline_patterns:
            p = self._pipeline_patterns[pattern_key]
            p.occurrence_count += 1
            p.total_tokens_spent += total_tokens
            p.estimated_compressed_tokens += est_compressed
            p.last_seen = time.time()
        else:
            self._pipeline_patterns[pattern_key] = PipelinePattern(
                pattern_id=hashlib.md5(pattern_key.encode()).hexdigest()[:12],
                tool_sequence=seq,
                occurrence_count=1,
                total_tokens_spent=total_tokens,
                estimated_compressed_tokens=est_compressed,
                compression_ratio=ratio,
                recommendation=self._pipeline_recommendation(seq),
                first_seen=time.time(),
                last_seen=time.time(),
            )

    def _pipeline_recommendation(self, seq: list[str]) -> str:
        """Generate a recommendation for collapsing a pipeline."""
        n = len(seq)
        if n == 2:
            return f"Consider compound tool: {seq[0]}+{seq[1]}"
        elif n <= 4:
            return f"Pipeline of {n} tools → collapse to 1-2 compound actions"
        else:
            return f"Deep chain ({n} tools) — restructure as batch with single output"

    def _score_compression(self, tool_name: str,
                           output_tokens: int,
                           was_redundant: bool,
                           pipeline_pos: int) -> float:
        """Score how compressible this particular call is (0-1)."""
        score = 0.0

        # Redundant calls are fully compressible
        if was_redundant:
            score += 0.5

        # Verbose outputs are partially compressible
        if output_tokens > VERBOSITY_THRESHOLD:
            excess = (output_tokens - VERBOSITY_THRESHOLD) / max(output_tokens, 1)
            score += excess * 0.3

        # Deep pipeline positions suggest earlier resolution possible
        if pipeline_pos > 2:
            score += min(0.2, pipeline_pos * 0.05)

        return min(1.0, score)

    # ──────────────────────────────────────────────────────────
    #  Analysis Lenses
    # ──────────────────────────────────────────────────────────

    def analyze_verbosity(self, top_n: int = 10) -> list[VerbosityProfile]:
        """Lens 1: Which tools produce unnecessarily verbose output?"""
        profiles = []
        for tool_name, token_counts in self._tool_profiles.items():
            if not token_counts:
                continue

            sorted_counts = sorted(token_counts)
            n = len(sorted_counts)
            avg = sum(sorted_counts) // n
            median = sorted_counts[n // 2]

            # Boilerplate: count repeated output hashes for this tool
            tool_hashes = [h for name, h in self._output_hashes if name == tool_name]
            unique = len(set(tool_hashes))
            total = len(tool_hashes) or 1
            boilerplate = 1.0 - (unique / total)

            # Compressible: above median is "excess"
            compressible = sum(max(0, t - median) for t in token_counts) / max(sum(token_counts), 1)

            recommendation = ""
            if avg > VERBOSITY_THRESHOLD:
                recommendation = f"Avg {avg} tokens/call — consider structured/tabular output"
            elif boilerplate > 0.3:
                recommendation = f"{boilerplate:.0%} boilerplate — cache or template the static parts"
            elif compressible > 0.4:
                recommendation = f"{compressible:.0%} compressible — trim to median ({median} tokens)"

            profiles.append(VerbosityProfile(
                tool_name=tool_name,
                call_count=n,
                avg_output_tokens=avg,
                max_output_tokens=sorted_counts[-1],
                min_output_tokens=sorted_counts[0],
                median_output_tokens=median,
                boilerplate_ratio=boilerplate,
                compressible_fraction=compressible,
                recommendation=recommendation,
            ))

        # Sort by waste potential (avg * call_count * compressible)
        profiles.sort(key=lambda p: p.avg_output_tokens * p.call_count * p.compressible_fraction, reverse=True)
        return profiles[:top_n]

    def analyze_pipelines(self) -> NestedActionAnalysis:
        """Lens 2: Which nested action chains can be collapsed?"""
        recent = list(self._flows)[-COMPRESSION_WINDOW:]
        if not recent:
            return NestedActionAnalysis()

        # Compute action depth
        pipelines = defaultdict(list)
        for r in recent:
            if r.pipeline_id:
                pipelines[r.pipeline_id].append(r)

        depths = [len(p) for p in pipelines.values()] if pipelines else [1]
        avg_depth = sum(depths) / len(depths)
        deepest = max(depths) if depths else 0

        # Collapsible chains (depth > ACTION_DEPTH_TARGET)
        collapsible = [p for p in pipelines.values() if len(p) > ACTION_DEPTH_TARGET]
        tokens_in_chains = sum(r.total_tokens for pipe in collapsible for r in pipe)
        tokens_saveable = int(tokens_in_chains * 0.6)  # 60% savings from collapse

        # Top pipeline patterns
        sorted_patterns = sorted(
            self._pipeline_patterns.values(),
            key=lambda p: p.occurrence_count * p.total_tokens_spent,
            reverse=True
        )

        # Circular pattern detection
        circular = self._detect_circular_patterns(recent)

        return NestedActionAnalysis(
            avg_action_depth=avg_depth,
            deepest_chain=deepest,
            collapsible_chains=len(collapsible),
            tokens_in_chains=tokens_in_chains,
            tokens_saveable=tokens_saveable,
            top_patterns=sorted_patterns[:5],
            circular_patterns=circular,
        )

    def _detect_circular_patterns(self, records: list[TokenFlowRecord]) -> list[dict]:
        """Detect circular tool call patterns (A→B→A→B...)."""
        circular = []
        if len(records) < 4:
            return circular

        tools = [r.tool_name for r in records]
        # Check for length-2 and length-3 cycles
        for cycle_len in (2, 3):
            for i in range(len(tools) - cycle_len * 2 + 1):
                pattern = tools[i:i + cycle_len]
                next_pattern = tools[i + cycle_len:i + cycle_len * 2]
                if pattern == next_pattern:
                    tokens = sum(
                        records[j].total_tokens
                        for j in range(i, min(i + cycle_len * 2, len(records)))
                    )
                    circular.append({
                        "pattern": "→".join(pattern),
                        "repetitions": 2,
                        "tokens_wasted": tokens // 2,  # Second repetition is waste
                        "recommendation": f"Break cycle: cache {pattern[0]} result or combine with {pattern[-1]}",
                    })

        # Deduplicate
        seen = set()
        unique = []
        for c in circular:
            key = c["pattern"]
            if key not in seen:
                seen.add(key)
                unique.append(c)
        return unique

    def analyze_budget(self) -> TokenBudgetState:
        """Lens 3: Weekly token budget status and projections."""
        elapsed = time.time() - self._session_start
        hours_elapsed = max(elapsed / 3600.0, 0.01)

        self._budget.burn_rate_per_hour = self._session_tokens / hours_elapsed
        if self._budget.burn_rate_per_hour > 0:
            hours_left = self._budget.tokens_remaining / self._budget.burn_rate_per_hour
            self._budget.hours_remaining_at_rate = hours_left
        else:
            self._budget.hours_remaining_at_rate = float("inf")

        # Efficiency = meaningful tokens / total tokens
        waste = self._budget.waste_detected
        total = max(self._budget.tokens_used, 1)
        self._budget.efficiency_score = 1.0 - (waste / total)

        # Compression savings estimate
        self._budget.compression_savings = sum(
            r.total_tokens for r in self._flows
            if r.compression_opportunity > 0.5
        )

        return self._budget

    # ──────────────────────────────────────────────────────────
    #  Compression Strategies
    # ──────────────────────────────────────────────────────────

    def emit_compression_directives(self) -> list[dict]:
        """Generate actionable compression directives from all three lenses."""
        directives = []

        # Lens 1: Verbosity
        verbose_tools = self.analyze_verbosity(top_n=5)
        for vp in verbose_tools:
            if vp.recommendation:
                directives.append({
                    "type": "compress_output",
                    "target": vp.tool_name,
                    "priority": min(1.0, vp.avg_output_tokens / 2000.0),
                    "tokens_saveable": int(vp.avg_output_tokens * vp.compressible_fraction * vp.call_count),
                    "recommendation": vp.recommendation,
                    "evidence": f"{vp.call_count} calls, avg {vp.avg_output_tokens} tokens, "
                               f"{vp.boilerplate_ratio:.0%} boilerplate",
                })

        # Lens 2: Pipelines
        pipeline_analysis = self.analyze_pipelines()
        for pattern in pipeline_analysis.top_patterns:
            if pattern.occurrence_count >= 2:
                directives.append({
                    "type": "collapse_pipeline",
                    "target": "→".join(pattern.tool_sequence),
                    "priority": min(1.0, pattern.occurrence_count * 0.2),
                    "tokens_saveable": pattern.total_tokens_spent - pattern.estimated_compressed_tokens,
                    "recommendation": pattern.recommendation,
                    "evidence": f"{pattern.occurrence_count}x seen, "
                               f"{pattern.total_tokens_spent} tokens total, "
                               f"{pattern.compression_ratio:.0%} compressible",
                })

        # Lens 2b: Circular patterns
        for circ in pipeline_analysis.circular_patterns:
            directives.append({
                "type": "break_cycle",
                "target": circ["pattern"],
                "priority": 0.8,  # Cycles are high-priority waste
                "tokens_saveable": circ["tokens_wasted"],
                "recommendation": circ["recommendation"],
                "evidence": f"Detected {circ['repetitions']}x repetition",
            })

        # Lens 3: Budget pressure
        budget = self.analyze_budget()
        if budget.hours_remaining_at_rate < 24:
            directives.append({
                "type": "budget_alert",
                "target": "weekly_token_budget",
                "priority": 1.0,
                "tokens_saveable": 0,
                "recommendation": f"CRITICAL: {budget.hours_remaining_at_rate:.1f}h remaining at current burn rate. "
                                  f"Switch to compressed output mode. "
                                  f"Batch operations. Skip exploratory reads.",
                "evidence": f"Burn rate: {budget.burn_rate_per_hour:.0f} tokens/hour, "
                            f"Used: {budget.tokens_used:,}, Remaining: {budget.tokens_remaining:,}",
            })
        elif budget.efficiency_score < 0.7:
            directives.append({
                "type": "efficiency_warning",
                "target": "token_efficiency",
                "priority": 0.6,
                "tokens_saveable": budget.waste_detected,
                "recommendation": f"Efficiency at {budget.efficiency_score:.0%}. "
                                  f"{budget.waste_detected:,} tokens identified as waste. "
                                  f"Apply compression directives.",
                "evidence": f"Waste sources: redundant calls, verbose outputs",
            })

        # Sort by saveable tokens (biggest wins first)
        directives.sort(key=lambda d: d["tokens_saveable"], reverse=True)
        return directives

    # ──────────────────────────────────────────────────────────
    #  Nested Action Compression Engine
    # ──────────────────────────────────────────────────────────

    def compute_compression_map(self) -> dict:
        """Produce a compression map: which actions to nest/batch/skip.

        Returns a strategy dict that agents can consume to restructure
        their tool call patterns for maximum token efficiency.
        """
        verbosity = self.analyze_verbosity()
        pipelines = self.analyze_pipelines()
        budget = self.analyze_budget()

        # Pressure level determines compression aggressiveness
        if budget.hours_remaining_at_rate < 12:
            pressure = "CRITICAL"
            compression_target = 0.5  # Cut token usage by 50%
        elif budget.hours_remaining_at_rate < 48:
            pressure = "HIGH"
            compression_target = 0.3
        elif budget.efficiency_score < 0.7:
            pressure = "MODERATE"
            compression_target = 0.2
        else:
            pressure = "LOW"
            compression_target = 0.1

        # Build tool-specific strategies
        tool_strategies = {}
        for vp in verbosity:
            strategy = "normal"
            if vp.avg_output_tokens > VERBOSITY_THRESHOLD and pressure in ("CRITICAL", "HIGH"):
                strategy = "compressed"  # Use structured/minimal output
            elif vp.boilerplate_ratio > 0.3:
                strategy = "cached"  # Return cache key, not full output
            elif vp.compressible_fraction > 0.5:
                strategy = "truncated"  # Return only essential fields

            tool_strategies[vp.tool_name] = {
                "output_strategy": strategy,
                "max_output_tokens": int(vp.median_output_tokens * (1.0 + compression_target)),
                "cache_eligible": vp.boilerplate_ratio > 0.2,
            }

        # Build pipeline collapse rules
        collapse_rules = []
        for pattern in pipelines.top_patterns:
            if pattern.occurrence_count >= 2 and pattern.compression_ratio > 0.3:
                collapse_rules.append({
                    "sequence": pattern.tool_sequence,
                    "collapse_to": f"compound_{pattern.pattern_id}",
                    "savings": pattern.compression_ratio,
                })

        return {
            "pressure_level": pressure,
            "compression_target": compression_target,
            "budget": {
                "used": budget.tokens_used,
                "remaining": budget.tokens_remaining,
                "burn_rate_per_hour": budget.burn_rate_per_hour,
                "hours_remaining": budget.hours_remaining_at_rate,
                "efficiency": budget.efficiency_score,
            },
            "tool_strategies": tool_strategies,
            "collapse_rules": collapse_rules,
            "circular_breaks": pipelines.circular_patterns,
            "total_saveable_tokens": sum(
                d["tokens_saveable"]
                for d in self.emit_compression_directives()
            ),
        }

    # ──────────────────────────────────────────────────────────
    #  Status & Reporting
    # ──────────────────────────────────────────────────────────

    def status(self) -> str:
        """Compact status for inclusion in sandbox_status."""
        budget = self.analyze_budget()
        n_flows = len(self._flows)
        n_patterns = len(self._pipeline_patterns)

        waste_pct = (budget.waste_detected / max(budget.tokens_used, 1)) * 100

        lines = [
            "## Token Efficiency Observer",
            f"  Flows tracked: {n_flows} | Patterns: {n_patterns}",
            f"  Session tokens: {self._session_tokens:,}",
            f"  Burn rate: {budget.burn_rate_per_hour:,.0f} tokens/hr",
            f"  Efficiency: {budget.efficiency_score:.0%} | Waste: {waste_pct:.1f}%",
            f"  Compression savings available: {budget.compression_savings:,} tokens",
        ]

        if budget.hours_remaining_at_rate < 48:
            lines.append(f"  [!] Budget pressure: {budget.hours_remaining_at_rate:.1f}h remaining")

        return "\n".join(lines)

    def full_report(self) -> str:
        """Comprehensive token efficiency report."""
        lines = ["# Token Efficiency Report\n"]

        # Budget
        budget = self.analyze_budget()
        lines.append("## Budget Status")
        lines.append(f"  Used: {budget.tokens_used:,} | Remaining: {budget.tokens_remaining:,}")
        lines.append(f"  Burn rate: {budget.burn_rate_per_hour:,.0f}/hr")
        lines.append(f"  Efficiency: {budget.efficiency_score:.0%}")
        lines.append(f"  Waste detected: {budget.waste_detected:,} tokens")
        lines.append(f"  Hours at rate: {budget.hours_remaining_at_rate:.1f}h\n")

        # Verbosity
        verbose = self.analyze_verbosity(top_n=8)
        if verbose:
            lines.append("## Verbose Tools (token sinks)")
            lines.append("| Tool | Calls | Avg Out | Boilerplate | Compressible | Action |")
            lines.append("|------|-------|---------|-------------|--------------|--------|")
            for vp in verbose:
                lines.append(
                    f"| `{vp.tool_name}` | {vp.call_count} | {vp.avg_output_tokens} | "
                    f"{vp.boilerplate_ratio:.0%} | {vp.compressible_fraction:.0%} | "
                    f"{vp.recommendation or '—'} |"
                )
            lines.append("")

        # Pipelines
        analysis = self.analyze_pipelines()
        lines.append("## Nested Action Analysis")
        lines.append(f"  Avg action depth: {analysis.avg_action_depth:.1f} "
                     f"(target: {ACTION_DEPTH_TARGET})")
        lines.append(f"  Deepest chain: {analysis.deepest_chain}")
        lines.append(f"  Collapsible chains: {analysis.collapsible_chains}")
        lines.append(f"  Tokens saveable: {analysis.tokens_saveable:,}\n")

        if analysis.top_patterns:
            lines.append("### Pipeline Patterns")
            for p in analysis.top_patterns:
                lines.append(f"  - `{'→'.join(p.tool_sequence)}` "
                             f"({p.occurrence_count}x, {p.total_tokens_spent:,} tokens, "
                             f"{p.compression_ratio:.0%} compressible)")
                lines.append(f"    → {p.recommendation}")

        if analysis.circular_patterns:
            lines.append("\n### Circular Patterns (WASTE)")
            for c in analysis.circular_patterns:
                lines.append(f"  - `{c['pattern']}` — {c['tokens_wasted']:,} tokens wasted")
                lines.append(f"    → {c['recommendation']}")

        # Compression directives
        directives = self.emit_compression_directives()
        if directives:
            lines.append("\n## Compression Directives (ranked by impact)")
            for i, d in enumerate(directives[:8], 1):
                lines.append(f"  {i}. [{d['type']}] `{d['target']}` "
                             f"— save ~{d['tokens_saveable']:,} tokens")
                lines.append(f"     {d['recommendation']}")

        # Compression map summary
        cmap = self.compute_compression_map()
        lines.append(f"\n## Compression Strategy: {cmap['pressure_level']}")
        lines.append(f"  Target reduction: {cmap['compression_target']:.0%}")
        lines.append(f"  Total saveable: {cmap['total_saveable_tokens']:,} tokens")
        if cmap['collapse_rules']:
            lines.append(f"  Collapse rules: {len(cmap['collapse_rules'])}")

        return "\n".join(lines)

    # ──────────────────────────────────────────────────────────
    #  Persistence
    # ──────────────────────────────────────────────────────────

    def _load_state(self) -> None:
        """Load persisted budget state."""
        try:
            if STATE_FILE.exists():
                data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
                b = data.get("budget", {})
                self._budget.tokens_used = b.get("tokens_used", 0)
                self._budget.waste_detected = b.get("waste_detected", 0)
                self._budget.week_start = b.get("week_start", "")
                self._budget.compression_savings = b.get("compression_savings", 0)

                # Reset if new week
                ws = self._budget.week_start
                if ws:
                    from datetime import datetime as dt
                    try:
                        start = dt.fromisoformat(ws)
                        now = dt.now(timezone.utc)
                        if (now - start).days >= 7:
                            self._budget = TokenBudgetState(
                                week_start=now.isoformat()
                            )
                    except (ValueError, TypeError):
                        pass
        except Exception:
            pass  # Fresh start is fine

    def save_state(self) -> None:
        """Persist budget state to disk."""
        try:
            STATE_DIR.mkdir(parents=True, exist_ok=True)
            if not self._budget.week_start:
                self._budget.week_start = datetime.now(timezone.utc).isoformat()

            data = {
                "budget": {
                    "tokens_used": self._budget.tokens_used,
                    "waste_detected": self._budget.waste_detected,
                    "week_start": self._budget.week_start,
                    "compression_savings": self._budget.compression_savings,
                },
                "patterns": {
                    k: {
                        "tool_sequence": v.tool_sequence,
                        "occurrence_count": v.occurrence_count,
                        "total_tokens_spent": v.total_tokens_spent,
                        "compression_ratio": v.compression_ratio,
                    }
                    for k, v in self._pipeline_patterns.items()
                },
                "saved_at": datetime.now(timezone.utc).isoformat(),
            }
            STATE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception:
            pass  # Non-fatal


# ──────────────────────────────────────────────────────────────
#  Singleton accessor
# ──────────────────────────────────────────────────────────────

def get_token_observer() -> TokenEfficiencyObserver:
    """Get the singleton TokenEfficiencyObserver."""
    return TokenEfficiencyObserver()
