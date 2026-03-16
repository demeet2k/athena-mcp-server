"""
ATHENA FRACTAL SERVER — Air Element (R)
=======================================
Seed / Replay / Compression Body

The Fractal lens provides the minimal seed with collapse/expand discipline.
Expand(σ) → Sq(Ω), Collapse(Sq) → σ.  Closure: Expand ∘ Collapse ~ id.
This is the TRANSPORTABLE COMPRESSION body — seeds that replicate the whole.

Tools: query_stage_code, query_angel, read_hologram_chapter, query_containment,
       dimensional_lift, resolve_dimensional_body, query_organ, query_mobius_lens,
       query_sfcr_station, athena_status, list_families, query_brain_network, route_brain

SFCR Mask: 8 (1000)
Dimension Home: 10D
Superphase Affinity: Salt
Transport: Z, A, L, Tunnel, Metro, Mycelium, Bus, Plane, ETV
"""

import os
import sys
from pathlib import Path

_MCP_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_MCP_DIR))

os.environ.setdefault("ATHENA_ROOT", str(_MCP_DIR.parent))

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Athena Fractal (Air)")

# ── Register Fractal-specific tools ───────────────────────────────
from crystal_108d.stage_codes import query_stage_code
from crystal_108d.angel import query_angel
from crystal_108d.shells import read_hologram_chapter
from crystal_108d.dimensions import resolve_dimensional_body, dimensional_lift, query_containment
from crystal_108d.organs import query_organ
from crystal_108d.mobius_lenses import query_mobius_lens, query_sfcr_station
from crystal_108d.brain import query_brain_network, route_brain, compute_bridge_weight, brain_status
from crystal_108d.emergence import query_emergence
from crystal_108d.inverse_seed import query_3d_crystal
from crystal_108d.inverse_complete import query_projection_stack
from crystal_108d.hologram_reading import query_hologram

mcp.tool()(query_stage_code)
mcp.tool()(query_angel)
mcp.tool()(read_hologram_chapter)
mcp.tool()(resolve_dimensional_body)
mcp.tool()(dimensional_lift)
mcp.tool()(query_containment)
mcp.tool()(query_organ)
mcp.tool()(query_mobius_lens)
mcp.tool()(query_sfcr_station)
mcp.tool()(query_brain_network)
mcp.tool()(route_brain)
mcp.tool()(compute_bridge_weight)
mcp.tool()(query_emergence)
mcp.tool()(query_3d_crystal)
mcp.tool()(query_projection_stack)
mcp.tool()(query_hologram)

# ── Core fractal/compression tools ────────────────────────────────
ATHENA_ROOT = Path(os.environ["ATHENA_ROOT"])
NS_ROOT = ATHENA_ROOT / "DEEPER CRYSTALIZATION" / "ACTIVE_NERVOUS_SYSTEM"
BOARD_DIR = NS_ROOT / "07_FULL_PROJECT_INTEGRATION_256" / "06_REALTIME_BOARD"


def _read_file(path: Path, limit: int = 500) -> str:
    if not path.exists():
        return f"Not found: {path.name}"
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    if len(lines) > limit:
        return "\n".join(lines[:limit]) + f"\n\n[…truncated at {limit} lines]"
    return text


@mcp.tool()
def athena_status() -> str:
    """Full system status including 108D summary and brain network."""
    from crystal_108d import status_summary
    return status_summary() + "\n" + brain_status()


@mcp.tool()
def list_families() -> str:
    """List active project families."""
    families_dir = BOARD_DIR / "03_FAMILIES"
    if not families_dir.exists():
        return "Families directory not found."
    families = sorted(families_dir.glob("*.md"))
    if not families:
        return "No active families."
    return "## Active Families\n\n" + "\n".join(f"- {f.stem}" for f in families)


# ── Fractal-specific resource ─────────────────────────────────────
@mcp.resource("athena://fractal-air")
def resource_fractal() -> str:
    """Fractal element status — Seed / Replay / Compression."""
    return (
        "## Fractal Lobe (Air) — Active\n\n"
        "**SFCR Mask**: 8 (1000)\n"
        "**Dimension Home**: 10D\n"
        "**Role**: Seed / Replay / Compression Body\n"
        "**Transport**: Z, A, L, Tunnel, Metro, Mycelium, Bus, Plane, ETV\n"
        "**Tools**: 14 registered\n\n"
        + brain_status()
    )


if __name__ == "__main__":
    mcp.run()
