# CRYSTAL: Xi108:W3:A13:S37 | face=C | node=701 | depth=0 | phase=Omega
# METRO: Omega
# BRIDGES: token_mcp→token_observer→observer→efficiency→metaloop
"""
Token Efficiency MCP Tools — Agent-Facing Token Observation Interface
======================================================================
4 MCP tools for token efficiency observation and compression:

  1. token_efficiency_status()     — budget + burn rate + waste detection
  2. token_bottleneck_report()     — verbose tools + pipeline waste + circular patterns
  3. token_compression_map()       — actionable compression strategy
  4. token_observe_call()          — manual token flow recording

These tools are self-aware: using them costs tokens, so they compress
their own output aggressively. Every report is structured, not prose.
"""


def register_token_tools(mcp) -> None:
    """Register all token efficiency observer tools onto the MCP server."""

    @mcp.tool()
    def token_efficiency_status() -> str:
        """Get token budget status: burn rate, waste %, efficiency score, hours remaining.

        Shows BOTH observable tokens (what we can measure) and dark tokens
        (estimated invisible cost: Claude's thinking, context re-read,
        protocol overhead). Real cost = observable + dark + envelope.

        Use this to check whether the organism is spending tokens wisely
        and how much runway remains in the weekly budget.
        """
        from .sandbox_token_observer import get_token_observer

        obs = get_token_observer()
        budget = obs.analyze_budget()

        waste_pct = (budget.waste_detected / max(budget.real_cost_est, 1)) * 100
        dark_pct = (budget.dark_tokens_est / max(budget.real_cost_est, 1)) * 100

        lines = [
            "TOKEN BUDGET (observable + dark)",
            f"  observable: {budget.tokens_used:>12,}  (what we can measure)",
            f"  dark (est): {budget.dark_tokens_est:>12,}  ({dark_pct:.0f}% invisible: thinking + context)",
            f"  real cost:  {budget.real_cost_est:>12,}  (observable + dark + envelope)",
            f"  remaining:  {budget.tokens_remaining:>12,}",
            f"  burn/hr:    {budget.real_burn_rate_per_hour:>12,.0f}  (real cost rate)",
            f"  hours_left: {budget.hours_remaining_at_rate:>12.1f}",
            f"  efficiency: {budget.efficiency_score:>12.0%}",
            f"  waste:      {budget.waste_detected:>12,} ({waste_pct:.1f}%)",
            f"  ctx_weight: {budget.context_inflation_total:>12,.0f}  (cumulative inflation)",
            f"  savings:    {budget.compression_savings:>12,} (available, incl. dark savings)",
        ]

        if budget.hours_remaining_at_rate < 12:
            lines.append("  PRESSURE:   CRITICAL -- compress everything")
        elif budget.hours_remaining_at_rate < 48:
            lines.append("  PRESSURE:   HIGH -- batch and truncate")
        elif budget.efficiency_score < 0.7:
            lines.append("  PRESSURE:   MODERATE -- reduce verbose tools")

        obs.save_state()
        return "\n".join(lines)

    @mcp.tool()
    def token_bottleneck_report(top_n: int = 5) -> str:
        """Identify token waste: verbose tools, collapsible pipelines, circular patterns.

        Args:
            top_n: Number of items per category (default 5)
        """
        from .sandbox_token_observer import get_token_observer

        obs = get_token_observer()
        return obs.full_report()

    @mcp.tool()
    def token_compression_map() -> str:
        """Get actionable compression strategy for reducing token output.

        Returns a structured strategy map with:
        - Pressure level (LOW/MODERATE/HIGH/CRITICAL)
        - Per-tool output strategies (compressed/cached/truncated/normal)
        - Pipeline collapse rules (which chains to merge)
        - Circular pattern breaks (which cycles to cache)
        - Total saveable tokens estimate
        """
        from .sandbox_token_observer import get_token_observer
        import json

        obs = get_token_observer()
        cmap = obs.compute_compression_map()

        # Structured output — JSON for machine consumption
        lines = [
            f"COMPRESSION STRATEGY: {cmap['pressure_level']}",
            f"  target_reduction: {cmap['compression_target']:.0%}",
            f"  total_saveable:   {cmap['total_saveable_tokens']:,} tokens",
            "",
            "BUDGET:",
            f"  used:      {cmap['budget']['used']:,}",
            f"  remaining: {cmap['budget']['remaining']:,}",
            f"  burn/hr:   {cmap['budget']['burn_rate_per_hour']:.0f}",
            f"  hours:     {cmap['budget']['hours_remaining']:.1f}",
            f"  eff:       {cmap['budget']['efficiency']:.0%}",
        ]

        if cmap['tool_strategies']:
            lines.append("\nTOOL STRATEGIES:")
            for tool, strat in cmap['tool_strategies'].items():
                lines.append(f"  {tool}: {strat['output_strategy']} "
                            f"(max={strat['max_output_tokens']}, "
                            f"cache={'Y' if strat['cache_eligible'] else 'N'})")

        if cmap['collapse_rules']:
            lines.append("\nCOLLAPSE RULES:")
            for rule in cmap['collapse_rules']:
                lines.append(f"  {'→'.join(rule['sequence'])} "
                            f"→ {rule['collapse_to']} "
                            f"(save {rule['savings']:.0%})")

        if cmap['circular_breaks']:
            lines.append("\nCIRCULAR BREAKS:")
            for cb in cmap['circular_breaks']:
                lines.append(f"  {cb['pattern']}: {cb['recommendation']}")

        return "\n".join(lines)

    @mcp.tool()
    def token_observe_call(tool_name: str,
                           input_tokens: int = 0,
                           output_tokens: int = 0,
                           latency_ms: float = 0.0) -> str:
        """Record a tool call's token usage for efficiency tracking.

        Called automatically by sandbox observer hooks, but can also be
        called manually to record external tool usage (e.g., Claude API
        calls, Google Docs fetches).

        Args:
            tool_name: Name of the tool called
            input_tokens: Estimated input tokens consumed
            output_tokens: Estimated output tokens produced
            latency_ms: Call latency in milliseconds
        """
        from .sandbox_token_observer import get_token_observer

        obs = get_token_observer()
        record = obs.observe_tool_call(
            tool_name=tool_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
        )

        return (f"Recorded: {tool_name} "
                f"in={input_tokens} out={output_tokens} "
                f"redundant={'Y' if record.was_redundant else 'N'} "
                f"compress={record.compression_opportunity:.0%} "
                f"pipe={record.pipeline_id}:{record.pipeline_position}")
