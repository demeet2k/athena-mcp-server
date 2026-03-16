"""
ATHENA SQUARE SERVER — Earth Element (S)
========================================
Structure / Address / Admissibility Body

The Square lens fixes WHERE the object is, WHAT state it carries, and WHAT law
generated it.  This is the discrete admissibility ledger — the visible board grid.

Tools: navigate_crystal, navigate_108d, query_shell, query_superphase,
       query_archetype, read_chapter, read_appendix, query_overlay,
       query_sigma15, read_manifest, query_brain_network, route_brain

SFCR Mask: 1 (0001)
Dimension Home: 4D
Superphase Affinity: Salt
Transport: Z, A
"""

import os
import sys
from pathlib import Path

# Ensure MCP/ is on the path
_MCP_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_MCP_DIR))

os.environ.setdefault("ATHENA_ROOT", str(_MCP_DIR.parent))

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Athena Square (Earth)")

# ── Register Square-specific tools ────────────────────────────────
from crystal_108d.shells import query_shell, query_superphase, query_archetype
from crystal_108d.address import navigate_108d
from crystal_108d.overlays import query_overlay, query_sigma15
from crystal_108d.brain import query_brain_network, route_brain, compute_bridge_weight
from crystal_108d.hologram_reading import query_hologram
from crystal_108d.inverse_seed import query_4d_seed
from crystal_108d.angel_geometry import query_angel_conservation

mcp.tool()(query_shell)
mcp.tool()(query_superphase)
mcp.tool()(query_archetype)
mcp.tool()(navigate_108d)
mcp.tool()(query_overlay)
mcp.tool()(query_sigma15)
mcp.tool()(query_brain_network)
mcp.tool()(route_brain)
mcp.tool()(compute_bridge_weight)
mcp.tool()(query_hologram)
mcp.tool()(query_4d_seed)
mcp.tool()(query_angel_conservation)

# ── Import core tools from main server (read-only navigation) ─────
from crystal_108d import status_summary

ATHENA_ROOT = Path(os.environ["ATHENA_ROOT"])
NS_ROOT = ATHENA_ROOT / "DEEPER CRYSTALIZATION" / "ACTIVE_NERVOUS_SYSTEM"
CHAPTERS_DIR = NS_ROOT / "04_CHAPTERS"
APPENDICES_DIR = NS_ROOT / "05_APPENDICES"
RUNTIME_DIR = NS_ROOT / "06_RUNTIME"


def _read_file(path: Path, limit: int = 500) -> str:
    if not path.exists():
        return f"Not found: {path.name}"
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    if len(lines) > limit:
        return "\n".join(lines[:limit]) + f"\n\n[…truncated at {limit} lines]"
    return text


@mcp.tool()
def navigate_crystal(address: str) -> str:
    """Navigate the 4D crystal by address (e.g., Ch01<0000>.S1.a)."""
    import re
    m = re.match(r"(Ch\d{2}|App[A-P])<(\d{4})>\.([SFCR])(\d)\.([a-d])", address)
    if not m:
        return f"Invalid crystal address: {address}"
    tile, digits, face, level, atom = m.groups()
    if tile.startswith("Ch"):
        base = CHAPTERS_DIR
    else:
        base = APPENDICES_DIR
    matches = list(base.glob(f"*{tile}*"))
    if not matches:
        return f"Tile {tile} not found."
    return _read_file(matches[0])


@mcp.tool()
def read_chapter(code: str = "Ch01") -> str:
    """Read a chapter tile (Ch01–Ch21)."""
    matches = list(CHAPTERS_DIR.glob(f"*{code}*"))
    if not matches:
        return f"Chapter {code} not found."
    return _read_file(matches[0])


@mcp.tool()
def read_appendix(code: str = "AppA") -> str:
    """Read an appendix hub (AppA–AppP)."""
    matches = list(APPENDICES_DIR.glob(f"*{code}*"))
    if not matches:
        return f"Appendix {code} not found."
    return _read_file(matches[0])


@mcp.tool()
def read_manifest(name: str = "") -> str:
    """Read runtime manifests."""
    if not RUNTIME_DIR.exists():
        return "Runtime directory not found."
    manifests = sorted(RUNTIME_DIR.glob("*.md"))
    if not name:
        return "Available manifests:\n" + "\n".join(f"- {m.stem}" for m in manifests)
    matches = [m for m in manifests if name.lower() in m.stem.lower()]
    if not matches:
        return f"Manifest '{name}' not found."
    return _read_file(matches[0])


# ── Square-specific resource ──────────────────────────────────────
@mcp.resource("athena://square-earth")
def resource_square() -> str:
    """Square element status — Structure / Address / Admissibility."""
    from crystal_108d.brain import brain_status
    return (
        "## Square Lobe (Earth) — Active\n\n"
        "**SFCR Mask**: 1 (0001)\n"
        "**Dimension Home**: 4D\n"
        "**Role**: Structure / Address / Admissibility Body\n"
        "**Transport**: Z, A\n"
        "**Tools**: 12 registered\n\n"
        + brain_status()
    )


if __name__ == "__main__":
    mcp.run()
