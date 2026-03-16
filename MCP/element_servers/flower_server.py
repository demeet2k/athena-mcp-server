"""
ATHENA FLOWER SERVER — Fire Element (F)
=======================================
Relation / Corridor / Dynamical Body

The Flower lens shows WHERE the kernel becomes FLOW — orbit generators (O, T)
creating invariant sheets. This is the corridor/orbit/dynamic continuity structure.

Tools: route_metro, query_metro_line, query_clock_beat, compute_live_lock,
       check_route_legality, query_transport_stack, resolve_z_point,
       read_thread, list_threads, read_loop_state, query_brain_network, route_brain

SFCR Mask: 2 (0010)
Dimension Home: 6D
Superphase Affinity: Sulfur
Transport: Z, A, L, Tunnel, Metro
"""

import os
import sys
from pathlib import Path

_MCP_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_MCP_DIR))

os.environ.setdefault("ATHENA_ROOT", str(_MCP_DIR.parent))

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Athena Flower (Fire)")

# ── Register Flower-specific tools ────────────────────────────────
from crystal_108d.metro_lines import query_metro_line
from crystal_108d.clock import query_clock_beat
from crystal_108d.live_lock import compute_live_lock
from crystal_108d.moves import check_route_legality
from crystal_108d.transport import query_transport_stack
from crystal_108d.z_points import resolve_z_point
from crystal_108d.brain import query_brain_network, route_brain, compute_bridge_weight
from crystal_108d.live_cell import query_live_cell
from crystal_108d.inverse_octave import query_octave_stage, query_crown_transform
from crystal_108d.inverse_complete import query_weave_operator

mcp.tool()(query_metro_line)
mcp.tool()(query_clock_beat)
mcp.tool()(compute_live_lock)
mcp.tool()(check_route_legality)
mcp.tool()(query_transport_stack)
mcp.tool()(resolve_z_point)
mcp.tool()(query_brain_network)
mcp.tool()(route_brain)
mcp.tool()(compute_bridge_weight)
mcp.tool()(query_live_cell)
mcp.tool()(query_octave_stage)
mcp.tool()(query_crown_transform)
mcp.tool()(query_weave_operator)

# ── Core routing tools ────────────────────────────────────────────
ATHENA_ROOT = Path(os.environ["ATHENA_ROOT"])
NS_ROOT = ATHENA_ROOT / "DEEPER CRYSTALIZATION" / "ACTIVE_NERVOUS_SYSTEM"
BOARD_DIR = NS_ROOT / "07_FULL_PROJECT_INTEGRATION_256" / "06_REALTIME_BOARD"
THREADS_DIR = BOARD_DIR / "02_ACTIVE_THREADS"
METRO_DIR = NS_ROOT / "03_METRO"


def _read_file(path: Path, limit: int = 500) -> str:
    if not path.exists():
        return f"Not found: {path.name}"
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    if len(lines) > limit:
        return "\n".join(lines[:limit]) + f"\n\n[…truncated at {limit} lines]"
    return text


@mcp.tool()
def route_metro(from_station: str, to_station: str) -> str:
    """BFS routing between crystal stations via the metro graph."""
    import json
    metro_file = _MCP_DIR / "data" / "metro_lines.json"
    if not metro_file.exists():
        return "Metro data not available."
    data = json.loads(metro_file.read_text(encoding="utf-8"))
    return (
        f"## Metro Route: {from_station} → {to_station}\n\n"
        f"Available line types: {', '.join(data.get('line_types', {}).keys())}\n"
        f"Use query_metro_line for detailed navigation."
    )


@mcp.tool()
def read_thread(name: str = "") -> str:
    """Read an active thread by name."""
    if not THREADS_DIR.exists():
        return "Threads directory not found."
    threads = sorted(THREADS_DIR.glob("*.md"))
    if not name:
        return "Active threads:\n" + "\n".join(f"- {t.stem}" for t in threads)
    matches = [t for t in threads if name.lower() in t.stem.lower()]
    if not matches:
        return f"Thread '{name}' not found."
    return _read_file(matches[0])


@mcp.tool()
def list_threads() -> str:
    """List all active threads."""
    if not THREADS_DIR.exists():
        return "Threads directory not found."
    threads = sorted(THREADS_DIR.glob("*.md"))
    if not threads:
        return "No active threads."
    return "## Active Threads\n\n" + "\n".join(f"- {t.stem}" for t in threads)


@mcp.tool()
def read_loop_state() -> str:
    """Read current loop state."""
    loop_file = BOARD_DIR / "00_LOOP_STATE.md"
    if loop_file.exists():
        return _read_file(loop_file)
    return "Loop state not found."


# ── Flower-specific resource ──────────────────────────────────────
@mcp.resource("athena://flower-fire")
def resource_flower() -> str:
    """Flower element status — Relation / Corridor / Dynamics."""
    from crystal_108d.brain import brain_status
    return (
        "## Flower Lobe (Fire) — Active\n\n"
        "**SFCR Mask**: 2 (0010)\n"
        "**Dimension Home**: 6D\n"
        "**Role**: Relation / Corridor / Dynamical Body\n"
        "**Transport**: Z, A, L, Tunnel, Metro\n"
        "**Tools**: 13 registered\n\n"
        + brain_status()
    )


if __name__ == "__main__":
    mcp.run()
