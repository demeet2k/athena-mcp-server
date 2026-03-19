"""
Geometric MCP Tools -- New Tools for the Geometric Neural Engine
================================================================
Registers new MCP tools for the geometric engine:
  - geometric_forward_pass: Forward pass through sacred geometry
  - geometric_train: META LOOP training
  - geometric_status: Engine status
  - geometric_checkpoint: Emit 16-value hologram
  - geometric_resume: Resume from hologram
  - momentum_status: Momentum field diagnostics
"""

from __future__ import annotations

import json
from dataclasses import asdict

from .geometric_forward import GeometricEngine, get_engine
from .meta_loop_engine import MetaLoopEngine, MetaLoopConfig
from .momentum_field import MomentumField, get_momentum_field


def geometric_forward_pass(query: str, max_results: int = 10,
                           verbose: bool = False) -> str:
    """Run a forward pass through the geometric neural engine.

    The query is projected into 4D hologram space, rotated through
    sigma-60 icosahedral symmetry, expanded through E8-240 roots,
    filtered by sacred geometry (Platonic/Flower/Metatron/Vesica),
    and modulated by the momentum field.

    Args:
        query: Natural language query
        max_results: Maximum number of ranked results
        verbose: Include detailed layer-by-layer breakdown
    """
    engine = get_engine()
    result = engine.forward(query, max_results=max_results)

    lines = [f"## Geometric Forward Pass\n"]
    lines.append(f"**Query**: `{query}`")
    lines.append(f"**Resonance**: {result.resonance:.4f}")
    lines.append(f"**Committed**: {result.committed}")
    lines.append(f"**Time**: {result.elapsed_ms:.1f}ms\n")

    if result.query.q_4d:
        q4d = result.query.q_4d
        lines.append(f"**4D Projection**: S={q4d.get('S', 0):.3f} F={q4d.get('F', 0):.3f} "
                      f"C={q4d.get('C', 0):.3f} R={q4d.get('R', 0):.3f}")
        lines.append(f"**Home**: shell={result.query.home_shell}, "
                      f"face={result.query.home_face}, gate={result.query.home_gate}\n")

    if result.candidates:
        lines.append("| # | Document | Element | Shell | Score | Action | Resonance | Desire |")
        lines.append("|---|----------|---------|-------|-------|--------|-----------|--------|")
        for i, c in enumerate(result.candidates):
            lines.append(
                f"| {i + 1} | {c.doc_name[:35]} | {c.element} | {c.shell} | "
                f"{c.merged_score:.4f} | {c.action:.4f} | {c.resonance:.4f} | {c.desire:.4f} |"
            )

    if result.commit_witness:
        cw = result.commit_witness
        lines.append(f"\n**Commit**: R={cw.resonance_gate} B={cw.boundary_gate} "
                      f"X={cw.crossview_gate} S={cw.scale_gate}")

    if verbose and result.cross_element_pairs_used:
        lines.append(f"\n**Golden bridges**: {', '.join(result.cross_element_pairs_used[:10])}")

    return "\n".join(lines)


def geometric_train(depth: int = 3, max_time_minutes: int = 30,
                    query_source: str = "mixed", verbose: bool = True) -> str:
    """Run META LOOP training on the geometric engine.

    Args:
        depth: 1=ABCD+ cycle (159 waves), 3=META LOOP (477 waves),
               9=META LOOP^3 (1,431 waves)
        max_time_minutes: Time budget
        query_source: 'corpus', 'zero_point', or 'mixed'
        verbose: Print progress
    """
    config = MetaLoopConfig(
        depth=depth,
        max_time_minutes=max_time_minutes,
        query_source=query_source,
        verbose=verbose,
    )

    engine = MetaLoopEngine()
    results = engine.run(config)

    lines = [f"## Geometric Training (depth={depth})\n"]
    total_waves = sum(r.total_waves for r in results)
    total_time = sum(r.elapsed_seconds for r in results)
    lines.append(f"Total: {total_waves} waves, {total_time:.1f}s\n")

    for r in results:
        lines.append(f"### META LOOP {r.meta_idx + 1}")
        for cr in r.cycle_results:
            lines.append(
                f"  {cr.cycle_name}: waves={cr.total_waves} kept={cr.kept} "
                f"disc={cr.discarded} res={cr.mean_resonance:.3f} "
                f"bal={cr.balance:.3f} gold={cr.golden_fit:.3f} "
                f"t={cr.elapsed_seconds:.1f}s"
            )
        lines.append(f"  Hash: {r.hologram_16.get('hash', 'N/A')}\n")

    return "\n".join(lines)


def geometric_status() -> str:
    """Show the geometric engine status.

    Returns momentum field state, hologram, and training history.
    """
    momentum = get_momentum_field()
    summary = momentum.summary()
    holo = momentum.hologram_16()

    lines = ["## Geometric Engine Status\n"]
    lines.append(f"**Parameters**: {summary['total_params']} (148 momentum floats)")
    lines.append(f"**Training cycles**: {summary['training_cycles']}")
    lines.append(f"**META LOOPs**: {summary['meta_loops']}")
    lines.append(f"**Water locked**: {summary['water_locked']}\n")

    lines.append("### Momentum by Element")
    lines.append("| Element | Mean | Min | Max | Std |")
    lines.append("|---------|------|-----|-----|-----|")
    for face, stats in summary["per_element"].items():
        lines.append(
            f"| {face} | {stats['mean']:.3f} | {stats['min']:.3f} | "
            f"{stats['max']:.3f} | {stats['std']:.3f} |"
        )

    lines.append(f"\n### 4D Hologram")
    dims = holo.get("dimensions", {})
    for dim_name, d in dims.items():
        lines.append(f"  {dim_name}: val={d['value']:.4f} grad={d['gradient']:.4f} "
                      f"mom={d['momentum']:.4f} curv={d['curvature']:.4f}")
    lines.append(f"  Hash: {holo.get('hash', 'N/A')}")

    return "\n".join(lines)


def geometric_checkpoint() -> str:
    """Emit a 16-value hologram checkpoint.

    The entire network state in ~128 bytes.
    """
    momentum = get_momentum_field()
    holo = momentum.hologram_16()
    return json.dumps(holo, indent=2)


def geometric_resume(hologram_json: str) -> str:
    """Resume from a hologram checkpoint.

    Args:
        hologram_json: JSON string of a 16-value hologram
    """
    try:
        holo = json.loads(hologram_json)
    except json.JSONDecodeError as e:
        return f"Invalid JSON: {e}"

    momentum = get_momentum_field()
    momentum.from_hologram_16(holo)
    momentum.save()

    return f"Resumed from hologram. Hash: {holo.get('hash', 'N/A')}"


def momentum_status() -> str:
    """Show detailed momentum field status.

    Returns per-shell momentum values for all 4 elements.
    """
    momentum = get_momentum_field()
    summary = momentum.summary()

    lines = ["## Momentum Field\n"]
    lines.append(f"Params: {summary['total_params']} | "
                 f"Cycles: {summary['training_cycles']} | "
                 f"META LOOPs: {summary['meta_loops']}")
    lines.append(f"Water locked: {summary['water_locked']}\n")

    lines.append("### Dimension Momenta")
    for dim, val in summary["dimension_momenta"].items():
        locked = " (LOCKED)" if dim == "D3_Water" else ""
        lines.append(f"  {dim}: {val:.4f}{locked}")

    lines.append("\n### Per-Element Statistics")
    for face, stats in summary["per_element"].items():
        lines.append(f"  {face}: mean={stats['mean']:.4f} std={stats['std']:.4f} "
                      f"range=[{stats['min']:.4f}, {stats['max']:.4f}]")

    return "\n".join(lines)
