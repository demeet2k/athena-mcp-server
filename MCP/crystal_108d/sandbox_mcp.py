# CRYSTAL: Xi108:W1:A8:S32 | face=S | node=615 | depth=0 | phase=Omega
# METRO: Su
# BRIDGES: mcp→observer→bridge→efficiency→metadata
"""
Sandbox MCP Tools — Agent-Facing Introspection Interface
=========================================================
6 MCP tools that let any agent query the sandbox observer system:

  1. sandbox_status()            — resource state + efficiency + bottlenecks
  2. sandbox_bottlenecks(top_n)  — slowest tools + redundant patterns
  3. sandbox_efficiency_history() — efficiency trend over time
  4. sandbox_co_occurrence()     — tool parallelism map
  5. sandbox_training_records()  — recent training records
  6. sandbox_directives()        — current optimization orders

These tools are themselves observed by the sandbox — recursive.
"""

from typing import Optional


def register_sandbox_tools(mcp) -> None:
    """Register all sandbox observer tools onto the MCP server."""

    @mcp.tool()
    def sandbox_status() -> str:
        """Get sandbox observer status: resources, efficiency, bottlenecks, bridge state.

        Returns a comprehensive overview of the meta-observer sandbox including:
        - System resource usage (memory, CPU, threads, disk I/O)
        - Context window pressure estimation
        - Token throughput metrics
        - Active tool traces and bottleneck summary
        - Unified observation bridge state
        - Recursive efficiency engine state
        """
        from .sandbox_observer import get_sandbox_observer
        from .sandbox_bridge import get_bridge
        from .sandbox_efficiency import get_efficiency_engine

        sandbox = get_sandbox_observer()
        bridge = get_bridge()
        efficiency = get_efficiency_engine()

        sections = [
            sandbox.status(),
            "",
            bridge.status(),
            "",
            efficiency.status(),
        ]

        # Token efficiency observer (non-fatal)
        try:
            from .sandbox_token_observer import get_token_observer
            sections.append("")
            sections.append(get_token_observer().status())
        except Exception:
            pass

        return "\n".join(sections)

    @mcp.tool()
    def sandbox_bottlenecks(top_n: int = 5) -> str:
        """Show top N bottleneck tools and optimization opportunities.

        Identifies:
        - Slowest tools by average latency
        - Redundant call patterns (rapid repeats)
        - Low-value tools (high token cost, low success)
        - Communication hot paths

        Args:
            top_n: Number of items per category (default 5)
        """
        from .sandbox_observer import get_sandbox_observer
        import json

        sandbox = get_sandbox_observer()
        report = sandbox.bottleneck_report(top_n=top_n)

        lines = ["## Bottleneck Report\n"]
        lines.append(f"**Total Traces**: {report['total_traces']} | "
                    f"**Unique Tools**: {report['total_tools_seen']}\n")

        if report["slowest"]:
            lines.append("### Slowest Tools")
            for s in report["slowest"]:
                lines.append(f"  - `{s['tool']}`: avg {s['avg_ms']:.1f}ms "
                            f"({s['count']} calls, {s['error_rate']:.0%} errors)")

        if report["redundant"]:
            lines.append("\n### Redundant Patterns")
            for r in report["redundant"]:
                lines.append(f"  - `{r['tool']}`: {r['rapid_repeat_count']} rapid repeats (<1s apart)")

        if report["low_value"]:
            lines.append("\n### High Token Cost")
            for lv in report["low_value"]:
                lines.append(f"  - `{lv['tool']}`: {lv['tokens_per_call']:.0f} tokens/call "
                            f"({lv['error_rate']:.0%} errors, {lv['count']} calls)")

        # Communication graph hot paths
        graph = sandbox.communication_graph()
        if graph["hot_paths"]:
            lines.append(f"\n### Communication Hot Paths (top {min(5, len(graph['hot_paths']))})")
            for hp in graph["hot_paths"][:5]:
                lines.append(f"  - `{hp['from']}` → `{hp['to']}`: {hp['weight']} sequential calls")

        return "\n".join(lines)

    @mcp.tool()
    def sandbox_efficiency_history(last_n: int = 20) -> str:
        """Show efficiency metrics trend over last N observations.

        Displays value_per_token and value_per_ms trends to track whether
        the system is becoming more efficient over time.

        Args:
            last_n: Number of recent records to show (default 20)
        """
        from .sandbox_metadata import get_metadata_emitter

        emitter = get_metadata_emitter()
        trend = emitter.efficiency_trend(n=last_n)

        if not trend:
            return "No efficiency data yet. Tool calls will populate this automatically."

        lines = ["## Efficiency Trend\n"]
        lines.append("| Cycle | Epoch | Value/Token | Value/ms | Delta |")
        lines.append("|-------|-------|-------------|----------|-------|")

        for t in trend:
            delta_str = f"{t['efficiency_delta']:+.4f}" if t['efficiency_delta'] else "—"
            lines.append(
                f"| {t['cycle']:>5} | {t['epoch']:>5} | "
                f"{t['value_per_token']:>11.4f} | {t['value_per_ms']:>8.4f} | {delta_str:>5} |"
            )

        # Summary
        if len(trend) >= 2:
            first_vpt = trend[0]["value_per_token"]
            last_vpt = trend[-1]["value_per_token"]
            if first_vpt > 0:
                change = (last_vpt - first_vpt) / first_vpt
                direction = "improving" if change > 0.05 else "declining" if change < -0.05 else "stable"
                lines.append(f"\n**Trend**: {direction} ({change:+.1%} over {len(trend)} records)")

        return "\n".join(lines)

    @mcp.tool()
    def sandbox_co_occurrence() -> str:
        """Show tool co-occurrence matrix for parallelism optimization.

        Identifies tools that are frequently called together (within 5-second
        windows), suggesting opportunities for batching or parallel execution.
        """
        from .sandbox_observer import get_sandbox_observer

        sandbox = get_sandbox_observer()
        matrix = sandbox.co_occurrence_matrix()
        candidates = sandbox.parallelism_candidates()

        if not matrix:
            return "No co-occurrence data yet. Multiple tool calls will populate this."

        lines = ["## Tool Co-Occurrence Matrix\n"]

        # Show as sorted list of pairs
        pairs = []
        seen = set()
        for tool_a, co_tools in matrix.items():
            for tool_b, count in co_tools.items():
                pair = tuple(sorted([tool_a, tool_b]))
                if pair not in seen:
                    seen.add(pair)
                    pairs.append((pair[0], pair[1], count))
        pairs.sort(key=lambda x: -x[2])

        lines.append("| Tool A | Tool B | Co-occurrences |")
        lines.append("|--------|--------|----------------|")
        for a, b, count in pairs[:15]:
            lines.append(f"| `{a}` | `{b}` | {count} |")

        if candidates:
            lines.append("\n### Parallelism Candidates")
            for c in candidates[:5]:
                lines.append(f"  - **{c['recommendation']}**: "
                            f"`{' + '.join(c['tools'])}` "
                            f"({c['co_occurrences']} co-occurrences)")

        return "\n".join(lines)

    @mcp.tool()
    def sandbox_training_records(last_n: int = 10) -> str:
        """Show recent training-ready records from the sandbox observer.

        Each record contains 15D scores (12D canonical + 3 sandbox),
        efficiency metrics, decision context, and witness chain hash.

        Args:
            last_n: Number of recent records to show (default 10)
        """
        from .sandbox_metadata import get_metadata_emitter

        emitter = get_metadata_emitter()
        records = emitter.recent_records(n=last_n)

        if not records:
            return "No training records yet. Self-play and tool calls will populate this."

        lines = ["## Recent Training Records\n"]

        for r in records:
            # Compact display
            scores_12d = [r.get(f"x{i}_{n}", 0.5) for i, n in enumerate([
                "structure", "semantics", "coordination", "recursion",
                "contradiction", "emergence", "legibility", "routing",
                "grounding", "compression", "interop", "potential"
            ], 1)]
            avg_12d = sum(scores_12d) / 12

            lines.append(f"### Record {r.get('record_id', '?')[:8]}")
            lines.append(f"  Source: {r.get('source', '?')} | "
                        f"Tool: {r.get('tool_name', '?')} | "
                        f"Outcome: {r.get('outcome', '?')}")
            lines.append(f"  12D avg: {avg_12d:.3f} | "
                        f"x13={r.get('x13_resource_efficiency', 0):.2f} "
                        f"x14={r.get('x14_latency', 0):.2f} "
                        f"x15={r.get('x15_throughput', 0):.2f}")
            lines.append(f"  V/token: {r.get('value_per_token', 0):.4f} | "
                        f"V/ms: {r.get('value_per_ms', 0):.4f} | "
                        f"Delta: {r.get('efficiency_delta', 0):+.4f}")
            lines.append(f"  Mem: {r.get('memory_mb', 0):.0f}MB | "
                        f"CPU: {r.get('cpu_percent', 0):.0f}% | "
                        f"Ctx: {r.get('context_pressure', 0):.1%}")
            lines.append("")

        # Show seeds if any
        seeds = emitter.recent_seeds(n=3)
        if seeds:
            lines.append("### Successor Seeds")
            for s in seeds:
                lines.append(f"  Epoch {s.get('epoch', '?')}: "
                            f"becoming={s.get('becoming_score', 0):.4f} | "
                            f"records={s.get('total_records', 0)} | "
                            f"best_v/t={s.get('best_value_per_token', 0):.4f}")

        return "\n".join(lines)

    @mcp.tool()
    def sandbox_directives() -> str:
        """Show current optimization directives from the recursive efficiency engine.

        Directives are self-verifying: the engine tracks whether each directive
        actually improved efficiency. Failed directives are not re-emitted.
        This is meta-observation of meta-observation (depth 2, bounded).
        """
        from .sandbox_efficiency import get_efficiency_engine

        engine = get_efficiency_engine()
        return engine.directives_report()
