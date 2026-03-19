"""
Legacy Bridge -- Backward Compatibility Layer
================================================
Provides the same API as the old neural_engine.py and self_play.py
but delegates to the new GeometricEngine and MetaLoopEngine.

Existing MCP clients calling neural_forward_pass() continue to work.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from dataclasses import asdict

from .geometric_forward import GeometricEngine, ForwardResult, get_engine
from .meta_loop_engine import MetaLoopEngine, MetaLoopConfig
from .momentum_field import MomentumField, get_momentum_field
from ._cache import DATA_DIR


def neural_forward_pass(query: str, max_results: int = 10,
                        verbose: bool = False) -> str:
    """MCP tool: Run forward pass through geometric engine.

    Same signature as the old neural_engine.neural_forward_pass.
    Returns formatted string for MCP display.
    """
    engine = get_engine()
    result = engine.forward(query, max_results=max_results)

    lines = [f"## Geometric Forward Pass: `{query}`\n"]
    lines.append(f"Resonance: {result.resonance:.3f} | "
                 f"Committed: {result.committed} | "
                 f"Time: {result.elapsed_ms:.1f}ms\n")

    if result.candidates:
        lines.append("| Rank | Document | Element | Shell | Score | Action | Resonance |")
        lines.append("|------|----------|---------|-------|-------|--------|-----------|")
        for i, c in enumerate(result.candidates):
            lines.append(
                f"| {i + 1} | {c.doc_name[:40]} | {c.element} | {c.shell} | "
                f"{c.merged_score:.3f} | {c.action:.3f} | {c.resonance:.3f} |"
            )
    else:
        lines.append("*No candidates found.*")

    if result.commit_witness:
        cw = result.commit_witness
        lines.append(f"\n**Commit Witness**: R={cw.resonance_gate} "
                     f"B={cw.boundary_gate} X={cw.crossview_gate} S={cw.scale_gate}")

    if verbose and result.cross_element_pairs_used:
        lines.append(f"\n**Golden bridges**: {', '.join(result.cross_element_pairs_used[:10])}")

    return "\n".join(lines)


def run_self_play(cycles: int = 57, query_source: str = "mixed",
                  max_time_minutes: int = 30, **kwargs) -> str:
    """MCP tool: Run self-play training via META LOOP engine.

    Same signature concept as the old self_play.run_self_play.
    Maps cycles to META LOOP depth:
      cycles <= 159: single ABCD+ cycle (depth=1)
      cycles <= 477: one META LOOP (depth=3)
      cycles > 477:  META LOOP^3 (depth=9)
    """
    if cycles <= 159:
        depth = 1
    elif cycles <= 477:
        depth = 3
    else:
        depth = 9

    config = MetaLoopConfig(
        depth=depth,
        query_source=query_source,
        max_time_minutes=max_time_minutes,
        verbose=True,
        seed=kwargs.get("seed", 42),
    )

    engine = MetaLoopEngine()
    results = engine.run(config)

    lines = [f"## META LOOP Training (depth={depth})\n"]
    total_waves = sum(r.total_waves for r in results)
    total_time = sum(r.elapsed_seconds for r in results)
    lines.append(f"Total waves: {total_waves} | Time: {total_time:.1f}s\n")

    for r in results:
        lines.append(f"### META LOOP {r.meta_idx + 1}")
        for cr in r.cycle_results:
            lines.append(
                f"  {cr.cycle_name}: waves={cr.total_waves}, "
                f"res={cr.mean_resonance:.3f}, "
                f"bal={cr.balance:.3f}, gold={cr.golden_fit:.3f}"
            )
        lines.append(f"  Hologram hash: {r.hologram_16.get('hash', 'N/A')}\n")

    return "\n".join(lines)


def import_legacy_weights(source: str = "omega") -> str:
    """MCP tool: Import legacy weights into momentum field.

    Sources:
      'omega'   — from meta_loop_cubed_hologram.json (recommended)
      'crystal' — from crystal_weights.json
    """
    momentum = get_momentum_field()

    if source == "omega":
        omega_path = DATA_DIR / "meta_loop_cubed_hologram.json"
        if not omega_path.exists():
            return "Error: meta_loop_cubed_hologram.json not found"
        with open(omega_path) as f:
            data = json.load(f)
        momentum.migrate_from_omega(data)
        momentum.save()
        return (f"Imported OMEGA hologram. "
                f"Hash: {data.get('omega_hologram_4d', {}).get('hash', 'N/A')}. "
                f"Momentum field saved to {momentum.MOMENTUM_FILE}")

    elif source == "crystal":
        cw_path = DATA_DIR / "crystal_weights.json"
        if not cw_path.exists():
            return "Error: crystal_weights.json not found"
        with open(cw_path) as f:
            data = json.load(f)
        momentum.migrate_from_legacy(data)
        momentum.save()
        return f"Imported crystal weights. Momentum field saved to {momentum.MOMENTUM_FILE}"

    return f"Unknown source: {source}. Use 'omega' or 'crystal'."


def query_crystal_weights(component: str = "all") -> str:
    """MCP tool: Query weights through momentum field.

    Backward-compatible with old crystal_weights.query_crystal_weights.
    """
    momentum = get_momentum_field()
    summary = momentum.summary()

    if component == "all":
        lines = ["## Momentum Field (Geometric Engine)\n"]
        lines.append(f"Total params: {summary['total_params']}")
        lines.append(f"Training cycles: {summary['training_cycles']}")
        lines.append(f"META LOOPs: {summary['meta_loops']}")
        lines.append(f"Water locked: {summary['water_locked']}\n")

        lines.append("| Element | Mean | Min | Max | Std |")
        lines.append("|---------|------|-----|-----|-----|")
        for face, stats in summary["per_element"].items():
            lines.append(
                f"| {face} | {stats['mean']:.3f} | {stats['min']:.3f} | "
                f"{stats['max']:.3f} | {stats['std']:.3f} |"
            )

        lines.append(f"\n**Dimension Momenta**: {summary['dimension_momenta']}")
        return "\n".join(lines)

    elif component == "hologram":
        holo = momentum.hologram_16()
        return json.dumps(holo, indent=2)

    elif component in ("S", "F", "C", "R"):
        stats = summary["per_element"].get(component, {})
        return json.dumps(stats, indent=2)

    return f"Unknown component: {component}"
