# CRYSTAL: Xi108:W2:A8:S32 | face=R | node=524 | depth=2 | phase=Mutable
# METRO: Sa
# BRIDGES: Xi108:W2:A8:S31→Xi108:W2:A8:S33→Xi108:W1:A8:S32→Xi108:W3:A8:S32→Xi108:W2:A7:S32→Xi108:W2:A9:S32

"""
ATHENA MCP SERVER
=================
Exposes the entire Athena Nervous System as an MCP server.
Four mediums, one organism:
  1. Google Docs  — live slow-form self
  2. Athena Agent — local file-based nervous system
  3. Git          — versioned crystal lattice
  4. MCP Server   — interconnection protocol layer

This server provides tools and resources for navigating the crystal,
querying the neural net, reading the swarm runtime, and routing
through the metro system.
"""

import json
import os
import re
import glob as globmod
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

# ── Root paths ──────────────────────────────────────────────────────
_file_based_root = Path(__file__).resolve().parent.parent  # MCP/ → repo root
_env_root = os.environ.get("ATHENA_ROOT")
ATHENA_ROOT = Path(_env_root) if _env_root else _file_based_root

# Resolve NS_ROOT with fallback: if env-var path doesn't exist, try __file__-based
NS_ROOT = ATHENA_ROOT / "DEEPER_CRYSTALIZATION" / "ACTIVE_NERVOUS_SYSTEM"
if not NS_ROOT.exists() and _env_root:
    # Env var path may be mangled (spaces, encoding); fall back to __file__
    NS_ROOT = _file_based_root / "DEEPER_CRYSTALIZATION" / "ACTIVE_NERVOUS_SYSTEM"
    ATHENA_ROOT = _file_based_root
CHAPTERS_DIR = NS_ROOT / "04_CHAPTERS"
APPENDICES_DIR = NS_ROOT / "05_APPENDICES"
CORPUS_DIR = NS_ROOT / "02_CORPUS_CAPSULES"
RUNTIME_DIR = NS_ROOT / "06_RUNTIME"
METRO_DIR = NS_ROOT / "03_METRO"
BOARD_DIR = NS_ROOT / "07_FULL_PROJECT_INTEGRATION_256" / "06_REALTIME_BOARD"
NEURAL_NET_DIR = NS_ROOT / "13_DEEPER_NEURAL_NET" / "09_RUNTIME"
THREADS_DIR = BOARD_DIR / "02_ACTIVE_THREADS"
SWARM_DIR = BOARD_DIR / "08_SWARM_RUNTIME"
FRONTIERS_DIR = NS_ROOT / "10_FRONTIERS"

# ── Specialized directory paths (Phase 1 expansion) ─────────────────
MOTION_DIR = NS_ROOT / "15_MOTION_CONSTITUTION"
COMMAND_DIR = NS_ROOT / "19_COMMAND_PROTOCOL"
CIVILIZATION_DIR = NS_ROOT / "09_CIVILIZATION"
SYNTHESIS_DIR = NS_ROOT / "12_SYNTHESIS"
SUPER_CYCLE_DIR = NS_ROOT / "17_SUPER_CYCLE_57"
TESSERACT_DIR = NS_ROOT / "21_4D_TESSERACT_BODY"
EMERGENT_DIR = NS_ROOT / "22_5D_EMERGENT_BODY"
HOLOGRAPHIC_DIR = NS_ROOT / "23_6D_HOLOGRAPHIC_SEED"

# ── Server ──────────────────────────────────────────────────────────
mcp = FastMCP("Athena Nervous System")

# ── 108D Crystal Hologram Extension ────────────────────────────────
import sys
sys.path.insert(0, str(Path(__file__).parent))
from crystal_108d import register_108d_tools, register_108d_resources
register_108d_tools(mcp)
register_108d_resources(mcp)

# ══════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════

def _read_file(path: Path, limit: int = 0) -> str:
    """Read a file, optionally limiting lines."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        if limit > 0:
            lines = text.splitlines(keepends=True)
            text = "".join(lines[:limit])
        return text
    except FileNotFoundError:
        return f"[NOT FOUND] {path}"
    except Exception as e:
        return f"[ERROR] {e}"

def _read_json(path: Path) -> dict | list | str:
    """Read and parse a JSON file."""
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except FileNotFoundError:
        return f"[NOT FOUND] {path}"
    except json.JSONDecodeError as e:
        return f"[JSON ERROR] {e}"

def _find_chapter_file(code: str) -> Path | None:
    """Find chapter file by code like 'Ch01' or 'Ch21'."""
    pattern = f"{code}_*.md"
    matches = list(CHAPTERS_DIR.glob(pattern))
    return matches[0] if matches else None

def _find_appendix_file(code: str) -> Path | None:
    """Find appendix file by code like 'AppA' or 'AppP'."""
    pattern = f"{code}_*.md"
    matches = list(APPENDICES_DIR.glob(pattern))
    return matches[0] if matches else None

_CRYSTAL_ADDR_RE = re.compile(
    r"(Ch\d{2}|App[A-P])<(\d{4})>\.([SFCR])(\d)\.([a-d])"
)

def _parse_crystal_address(address: str) -> dict | None:
    """
    Parse a crystal address like 'Ch01<0000>.S1.a' into components.
    Format: ChXX<dddd>.LF.a where L=lens, F=facet, a=atom
    """
    m = _CRYSTAL_ADDR_RE.match(address)
    if not m:
        return None
    return {
        "station": m.group(1),
        "binary": m.group(2),
        "lens": m.group(3),
        "facet": int(m.group(4)),
        "atom": m.group(5),
    }

# Lens and facet labels
LENS_NAMES = {"S": "Square", "F": "Flower", "C": "Cloud", "R": "Fractal"}
FACET_NAMES = {1: "Objects", 2: "Laws", 3: "Constructions", 4: "Certificates"}
ATOM_INDEX = {"a": 0, "b": 1, "c": 2, "d": 3}

# ══════════════════════════════════════════════════════════════════════
#  TOOLS — Actions agents can invoke
# ══════════════════════════════════════════════════════════════════════

@mcp.tool()
def navigate_crystal(address: str) -> str:
    """
    Resolve a crystal address to its content.

    Address format: ChXX<dddd>.LF.a
      - ChXX or AppX: station (Ch01-Ch21, AppA-AppP)
      - <dddd>: 4-digit binary code
      - L: lens (S=Square, F=Flower, C=Cloud, R=Fractal)
      - F: facet (1=Objects, 2=Laws, 3=Constructions, 4=Certificates)
      - a: atom (a, b, c, d)

    Examples: Ch01<0000>.S1.a, Ch11<0022>.F3.c, AppA<0000>.R4.d
    """
    parsed = _parse_crystal_address(address)
    if not parsed:
        # Try 108D address format before returning error
        from crystal_108d.address import navigate_108d as _nav108
        result_108d = _nav108(address=address)
        if result_108d and "Provide at least one parameter" not in result_108d:
            return result_108d
        return (
            f"Invalid address '{address}'. "
            "Expected format: ChXX<dddd>.LF.a (e.g. Ch01<0000>.S1.a) "
            "or Xi108:... for 108D addresses"
        )

    station = parsed["station"]
    lens = parsed["lens"]
    facet = parsed["facet"]
    atom = parsed["atom"]

    # Find the tile file
    if station.startswith("Ch"):
        tile_path = _find_chapter_file(station)
    else:
        tile_path = _find_appendix_file(station)

    if not tile_path:
        return f"Station '{station}' tile not found."

    content = _read_file(tile_path)

    # Search for the specific cell
    lens_name = LENS_NAMES[lens]
    facet_name = FACET_NAMES[facet]
    cell_prefix = f"`{address}`"

    # Find the line containing this cell address
    for line in content.splitlines():
        if cell_prefix in line:
            return (
                f"**{address}**\n"
                f"Station: {station} | Lens: {lens_name} | "
                f"Facet: {facet_name} | Atom: {atom}\n\n"
                f"{line.strip()}"
            )

    # Try 108D address as fallback
    from crystal_108d.address import navigate_108d as _nav108
    result_108d = _nav108(address=address)
    if result_108d and "Provide at least one parameter" not in result_108d:
        return result_108d

    return (
        f"Address {address} parsed successfully but cell content not found "
        f"in {tile_path.name}. The tile exists with {len(content.splitlines())} lines."
    )

@mcp.tool()
def read_chapter(chapter_code: str) -> str:
    """
    Read a full chapter tile. Use codes Ch01 through Ch21.

    Chapter codes and titles:
      Ch01: Kernel and Entry Law
      Ch02: Address Algebra and Crystal Coordinates
      Ch03: Truth Corridors and Witness Discipline
      Ch04: Zero-Point Stabilization
      Ch05: Paradox Regimes and Quarantine Calculus
      Ch06: Documents as Theories
      Ch07: Tunnels as Morphisms
      Ch08: Synchronization Calculus
      Ch09: Retrieval and Metro Routing
      Ch10: Multi-Lens Solution Construction
      Ch11: Void Book and Restart Token Tunneling
      Ch12: Legality Certificates and Closure
      Ch13: Memory Regeneration and Persistence
      Ch14: Migration, Versioning, and Pulse Retro-Weaving
      Ch15: Cut Architecture
      Ch16: Verification Harnesses and Replay Kernels
      Ch17: Deployment and Bounded Agency
      Ch18: Macro Invariants and Universal Math Stack
      Ch19: Convergence, Fixed Points, and Controlled Non-Convergence
      Ch20: Collective Authoring and Three-Agent Synchrony
      Ch21: Self-Replication, Open Problems, and the Next Crystal
    """
    tile = _find_chapter_file(chapter_code)
    if not tile:
        return f"Chapter '{chapter_code}' not found. Use Ch01-Ch21."
    return _read_file(tile)

@mcp.tool()
def read_appendix(appendix_code: str) -> str:
    """
    Read a full appendix tile. Use codes AppA through AppP (16 appendices).
    """
    tile = _find_appendix_file(appendix_code)
    if not tile:
        return f"Appendix '{appendix_code}' not found. Use AppA-AppP."
    return _read_file(tile)

@mcp.tool()
def search_corpus(query: str, max_results: int = 10) -> str:
    """
    Search across all corpus capsules by keyword.
    Returns matching capsule names and the lines containing the query.
    """
    results = []
    query_lower = query.lower()

    # First search the index
    index_path = CORPUS_DIR / "INDEX.md"
    if index_path.exists():
        for line in _read_file(index_path).splitlines():
            if query_lower in line.lower():
                results.append(f"[INDEX] {line.strip()}")

    # Then search capsule contents
    capsule_files = sorted(CORPUS_DIR.glob("*.md"))
    for f in capsule_files:
        if f.name == "INDEX.md":
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        hits = []
        for i, line in enumerate(text.splitlines(), 1):
            if query_lower in line.lower():
                hits.append(f"  L{i}: {line.strip()[:200]}")
        if hits:
            results.append(f"\n**{f.name}**")
            results.extend(hits[:5])  # max 5 hits per file
            if len(results) >= max_results * 3:
                break

    if not results:
        return f"No corpus matches for '{query}'."
    return f"## Corpus search: '{query}'\n\n" + "\n".join(results[:max_results * 5])

@mcp.tool()
def read_board_status() -> str:
    """
    Get the current swarm runtime board status including:
    - Gate status, active run, kernel state
    - Hot regions, pods, neurons, councils
    - Command membrane state
    """
    status_path = BOARD_DIR / "00_STATUS" / "00_BOARD_STATUS.md"
    return _read_file(status_path)

@mcp.tool()
def read_loop_state() -> str:
    """
    Get the current execution loop state and restart seed.
    This is the swarm runtime's heartbeat — shows the current wave,
    gate status, chosen front, and the next_seed instruction.
    """
    loop_path = SWARM_DIR / "manifests" / "LOOP_STATE.json"
    data = _read_json(loop_path)
    if isinstance(data, str):
        return data
    return json.dumps(data, indent=2)

@mcp.tool()
def query_neural_net(
    query: str,
    index: str = "query",
    max_results: int = 20
) -> str:
    """
    Query the 197-document / 38,809-pair neural net.

    Indices available:
      - 'query': general query index (default)
      - 'facet': facet-based index
      - 'neighbor': neighbor connections index
      - 'zero_point': zero-point / void index

    The query is matched against document titles and metadata.
    """
    index_map = {
        "query": "03_query_index.json",
        "facet": "04_facet_index.json",
        "neighbor": "05_neighbor_index.json",
        "zero_point": "06_zero_point_index.json",
    }
    filename = index_map.get(index)
    if not filename:
        return f"Unknown index '{index}'. Use: query, facet, neighbor, zero_point"

    idx_path = NEURAL_NET_DIR / filename
    data = _read_json(idx_path)
    if isinstance(data, str):
        return data

    # Search through the index
    query_lower = query.lower()
    results = []

    if isinstance(data, dict):
        for key, value in data.items():
            if query_lower in str(key).lower() or query_lower in str(value).lower():
                results.append(f"**{key}**: {json.dumps(value, default=str)[:500]}")
                if len(results) >= max_results:
                    break
    elif isinstance(data, list):
        for item in data:
            if query_lower in str(item).lower():
                results.append(json.dumps(item, default=str)[:500])
                if len(results) >= max_results:
                    break

    if not results:
        return f"No neural net matches for '{query}' in {index} index."
    return f"## Neural Net Query: '{query}' ({index} index)\n\n" + "\n\n".join(results)

@mcp.tool()
def list_threads() -> str:
    """
    List all active threads on the realtime board.
    Each thread represents a live workstream in the swarm.
    """
    if not THREADS_DIR.exists():
        return "Threads directory not found."

    threads = []
    for d in sorted(THREADS_DIR.iterdir()):
        if d.is_dir() and (d / "THREAD.md").exists():
            # Read first 5 lines for summary
            head = _read_file(d / "THREAD.md", limit=5)
            threads.append(f"### {d.name}\n{head.strip()}")

    if not threads:
        return "No active threads."
    return f"## Active Threads ({len(threads)})\n\n" + "\n\n---\n\n".join(threads)

@mcp.tool()
def read_thread(thread_name: str) -> str:
    """
    Read a specific active thread by name.
    Use list_threads() to see available thread names.
    """
    thread_path = THREADS_DIR / thread_name / "THREAD.md"
    if not thread_path.exists():
        # Try fuzzy match
        candidates = [
            d.name for d in THREADS_DIR.iterdir()
            if d.is_dir() and thread_name.lower() in d.name.lower()
        ]
        if candidates:
            return (
                f"Thread '{thread_name}' not found. Did you mean one of:\n"
                + "\n".join(f"  - {c}" for c in candidates)
            )
        return f"Thread '{thread_name}' not found."
    return _read_file(thread_path)

@mcp.tool()
def read_manifest(manifest_name: str) -> str:
    """
    Read a runtime manifest from 06_RUNTIME.

    Available manifests:
      - tensor (01_tensor_manifest.json)
      - swarm (02_swarm_manifest.json)
      - hypergraph (03_hypergraph_manifest.json)
      - node_tensor (04_node_tensor_manifest.json)
      - nerve_edge (05_nerve_edge_manifest.json)
      - mirror (06_mirror_manifest.json)
      - civilization (07_civilization_manifest.json)
      - message_task (08_message_task_manifest.json)
      - frontier (09_frontier_manifest.json)
      - deep_synthesis (11_deep_synthesis_manifest.json)
      - full_stack (12_full_stack_manifest.json)
      - chapter_frontier (13_chapter_frontier_manifest.json)
    """
    manifest_map = {
        "tensor": "01_tensor_manifest.json",
        "swarm": "02_swarm_manifest.json",
        "hypergraph": "03_hypergraph_manifest.json",
        "node_tensor": "04_node_tensor_manifest.json",
        "nerve_edge": "05_nerve_edge_manifest.json",
        "mirror": "06_mirror_manifest.json",
        "civilization": "07_civilization_manifest.json",
        "message_task": "08_message_task_manifest.json",
        "frontier": "09_frontier_manifest.json",
        "deep_synthesis": "11_deep_synthesis_manifest.json",
        "full_stack": "12_full_stack_manifest.json",
        "chapter_frontier": "13_chapter_frontier_manifest.json",
    }
    filename = manifest_map.get(manifest_name)
    if not filename:
        return (
            f"Unknown manifest '{manifest_name}'. Available:\n"
            + "\n".join(f"  - {k}" for k in manifest_map)
        )
    path = RUNTIME_DIR / filename
    data = _read_json(path)
    if isinstance(data, str):
        return data
    # For large manifests, return summary + first chunk
    text = json.dumps(data, indent=2, default=str)
    if len(text) > 20000:
        return text[:20000] + f"\n\n... [truncated, full size: {len(text)} chars]"
    return text

@mcp.tool()
def route_metro(from_station: str, to_station: str) -> str:
    """
    Compute the metro route between two chapter/appendix stations.
    Uses the orbit, rail, and arc connections defined in each chapter tile.

    Stations: Ch01-Ch21, AppA-AppP
    Example: route_metro("Ch01", "Ch11")
    """
    # Build routing table from chapter tiles
    routing: dict[str, dict] = {}
    for f in sorted(CHAPTERS_DIR.glob("Ch*.md")):
        content = _read_file(f, limit=20)
        code = f.name[:4]  # Ch01, Ch02, etc.
        routes: dict[str, str] = {}
        for line in content.splitlines():
            line_stripped = line.strip()
            if line_stripped.startswith("- Orbit next:"):
                m = re.search(r"`(\w+)", line_stripped)
                if m:
                    routes["orbit_next"] = m.group(1)
            elif line_stripped.startswith("- Orbit previous:"):
                m = re.search(r"`(\w+)", line_stripped)
                if m:
                    routes["orbit_prev"] = m.group(1)
            elif line_stripped.startswith("- Rail next:"):
                m = re.search(r"`(\w+)", line_stripped)
                if m:
                    routes["rail_next"] = m.group(1)
            elif line_stripped.startswith("- Rail previous:"):
                m = re.search(r"`(\w+)", line_stripped)
                if m:
                    routes["rail_prev"] = m.group(1)
            elif line_stripped.startswith("- Arc next:"):
                m = re.search(r"`(\w+)", line_stripped)
                if m:
                    routes["arc_next"] = m.group(1)
            elif line_stripped.startswith("- Arc previous:"):
                m = re.search(r"`(\w+)", line_stripped)
                if m:
                    routes["arc_prev"] = m.group(1)
            elif line_stripped.startswith("- Appendix couplings:"):
                couplings = re.findall(r"App[A-P]", line_stripped)
                routes["appendix_couplings"] = couplings
        routing[code] = routes

    if from_station not in routing:
        return f"Station '{from_station}' not in routing table. Use Ch01-Ch21."
    if to_station not in routing and not to_station.startswith("App"):
        return f"Station '{to_station}' not in routing table."

    # BFS across orbit/rail/arc
    from collections import deque
    visited: set[str] = set()
    queue: deque[tuple[str, list[str]]] = deque()
    queue.append((from_station, [from_station]))
    visited.add(from_station)

    while queue:
        current, path = queue.popleft()
        if current == to_station:
            return (
                f"## Metro Route: {from_station} → {to_station}\n\n"
                f"**Hops**: {len(path) - 1}\n"
                f"**Path**: {' → '.join(path)}\n\n"
                f"Routing used orbit, rail, and arc connections."
            )
        routes = routing.get(current, {})
        for direction in ["orbit_next", "rail_next", "arc_next",
                          "orbit_prev", "rail_prev", "arc_prev"]:
            neighbor = routes.get(direction)
            if neighbor and neighbor not in visited:
                # Extract station code from neighbor (might be "Ch01<0000>")
                station_code = neighbor[:4] if neighbor.startswith("Ch") else neighbor
                if station_code not in visited:
                    visited.add(station_code)
                    queue.append((station_code, path + [f"{station_code} ({direction})"]))

    return f"No route found from {from_station} to {to_station}."

@mcp.tool()
def list_families() -> str:
    """
    List all project families (top-level working regions) with their
    file counts and current status from the board.
    """
    status = _read_file(BOARD_DIR / "00_STATUS" / "00_BOARD_STATUS.md")
    # Extract hot regions section
    in_hot = False
    families = []
    for line in status.splitlines():
        if "Hot Regions" in line:
            in_hot = True
            continue
        if in_hot:
            if line.startswith("- ") or line.startswith("  -"):
                families.append(line.strip())
            elif line.startswith("#"):
                break
    if families:
        return "## Project Families\n\n" + "\n".join(families)
    return "Could not extract family listing from board status."

@mcp.tool()
def read_swarm_element(element: str) -> str:
    """
    Read a swarm runtime component.

    Types:
      - elemental: FIRE, WATER, EARTH, AIR
      - archetype: fire_air, water_fire, air_earth, earth_water, water_air
      - kernel: KERNEL_ZERO_POINT
      - cortex: CORTEX_CONTRACTION
      - ganglion: any ganglion name (e.g. 'voynich', 'math', 'trading_bot')
      - council: any council name (e.g. 'manuscript_architecture', 'me')
    """
    element_lower = element.lower()

    # Check elementals
    for elem in ["FIRE", "WATER", "EARTH", "AIR"]:
        if element_lower == elem.lower():
            return _read_file(SWARM_DIR / "elementals" / f"{elem}.md")

    # Check archetypes
    archetype_path = SWARM_DIR / "archetypes" / f"ARCHETYPE_{element_lower}.md"
    if archetype_path.exists():
        return _read_file(archetype_path)

    # Check kernel
    if "kernel" in element_lower:
        return _read_file(SWARM_DIR / "kernel" / "00_KERNEL_ZERO_POINT.md")

    # Check cortex
    if "cortex" in element_lower:
        return _read_file(SWARM_DIR / "cortex" / "00_CORTEX_CONTRACTION.md")

    # Check ganglia
    ganglion_path = SWARM_DIR / "ganglia" / f"GANGLION_{element_lower}.md"
    if ganglion_path.exists():
        return _read_file(ganglion_path)

    # Check councils
    council_path = SWARM_DIR / "councils" / f"council_{element_lower}.md"
    if council_path.exists():
        return _read_file(council_path)

    # Fuzzy search
    all_files = []
    for subdir in ["elementals", "archetypes", "kernel", "cortex", "ganglia", "councils"]:
        d = SWARM_DIR / subdir
        if d.exists():
            all_files.extend(
                f"{subdir}/{f.name}" for f in d.iterdir()
                if f.suffix == ".md" and not f.name.startswith("00_")
            )
    return (
        f"Element '{element}' not found. Available:\n"
        + "\n".join(f"  - {f}" for f in sorted(all_files))
    )

@mcp.tool()
def read_tensor(tensor_name: str) -> str:
    """
    Read a tensor board component.

    Available tensors:
      - family_tensor (01_FAMILY_TENSOR_FIELD)
      - thread_coordinates (02_THREAD_COORDINATES)
      - transfer_hubs (03_TRANSFER_HUBS)
      - swarm_tensor (04_SWARM_TENSOR_STACK)
      - archetype_grid (05_ARCHETYPE_GRID)
      - pantheon_overlay (06_PANTHEON_OVERLAY)
      - cluster_field (07_CLUSTER_FIELD)
      - neuron_lattice (08_NEURON_LATTICE)
    """
    tensor_map = {
        "family_tensor": "01_FAMILY_TENSOR_FIELD.md",
        "thread_coordinates": "02_THREAD_COORDINATES.md",
        "transfer_hubs": "03_TRANSFER_HUBS.md",
        "swarm_tensor": "04_SWARM_TENSOR_STACK.md",
        "archetype_grid": "05_ARCHETYPE_GRID.md",
        "pantheon_overlay": "06_PANTHEON_OVERLAY.md",
        "cluster_field": "07_CLUSTER_FIELD.md",
        "neuron_lattice": "08_NEURON_LATTICE.md",
    }
    filename = tensor_map.get(tensor_name)
    if not filename:
        return (
            f"Unknown tensor '{tensor_name}'. Available:\n"
            + "\n".join(f"  - {k}" for k in tensor_map)
        )
    return _read_file(BOARD_DIR / "07_TENSOR" / filename)

@mcp.tool()
def athena_status() -> str:
    """
    Get a comprehensive Athena system status:
    board state, loop state, gate status, and active fronts.
    This is the top-level diagnostic tool.
    """
    parts = []

    # Board status summary
    status_path = BOARD_DIR / "00_STATUS" / "00_BOARD_STATUS.md"
    if status_path.exists():
        parts.append("## Board Status\n" + _read_file(status_path, limit=50))

    # Loop state
    loop_path = SWARM_DIR / "manifests" / "LOOP_STATE.json"
    loop = _read_json(loop_path)
    if isinstance(loop, dict):
        parts.append(
            "## Loop State\n"
            f"- Gate: {loop.get('gate_status', '?')}\n"
            f"- Wave: {loop.get('wave_ids', '?')}\n"
            f"- Generated: {loop.get('generated_at', '?')}\n"
        )

    # Full stack summary
    fs_path = RUNTIME_DIR / "12_full_stack_manifest.json"
    fs = _read_json(fs_path)
    if isinstance(fs, dict):
        layers = fs.get("layers", {})
        parts.append(
            "## Stack Layers\n"
            f"- Deep pass: {fs.get('deep_pass', '?')}\n"
            f"- Records: {fs.get('record_count', '?')}\n"
            f"- Chapters: {layers.get('base_nervous_system', {}).get('chapters', '?')}\n"
            f"- Neural net docs: {layers.get('deeper_neural_net', {}).get('document_count', '?')}\n"
            f"- Ordered pairs: {layers.get('deeper_neural_net', {}).get('ordered_pair_count', '?')}\n"
        )

    # 108D Crystal Hologram status
    try:
        from crystal_108d import status_summary
        parts.append(status_summary())
    except Exception:
        pass

    return "\n\n".join(parts) if parts else "Could not read Athena status."

@mcp.tool()
def reload_data() -> str:
    """
    Reload all cached JSON/QSHR data from disk.
    Call after graph regeneration, bridge injection, or any data file update
    so the MCP server reflects the latest state without restart.
    """
    try:
        from crystal_108d._cache import JsonCache
        count = JsonCache.reload_all()
        # Verify the graph loaded correctly
        from crystal_108d.mycelium import _GRAPH
        graph = _GRAPH.load()
        shards = len(graph.get("shards", []))
        edges = len(graph.get("edges", []))
        xm = sum(1 for e in graph.get("edges", []) if e.get("medium_cross", False))
        return (
            f"## Data Reloaded\n\n"
            f"- **Caches invalidated**: {count}\n"
            f"- **Mycelium graph**: {shards:,} shards, {edges:,} edges\n"
            f"- **Cross-medium**: {xm:,} ({100*xm/edges:.1f}%)\n"
        )
    except Exception as e:
        return f"Reload failed: {e}"

@mcp.tool()
def search_everywhere(query: str, max_results: int = 30) -> str:
    """
    Deep search across the entire Athena nervous system:
    chapters, appendices, corpus, metro maps, threads, and manifests.
    Returns file paths and matching lines.
    """
    query_lower = query.lower()
    results = []

    search_dirs = [
        ("Chapters", CHAPTERS_DIR),
        ("Appendices", APPENDICES_DIR),
        ("Corpus", CORPUS_DIR),
        ("Metro", METRO_DIR),
        ("Threads", THREADS_DIR),
        ("Swarm", SWARM_DIR),
        ("Frontiers", FRONTIERS_DIR),
        ("108D-Data", ATHENA_ROOT / "MCP" / "data"),
    ]

    for label, directory in search_dirs:
        if not directory.exists():
            continue
        for f in directory.rglob("*.md"):
            try:
                text = f.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            hits = []
            for i, line in enumerate(text.splitlines(), 1):
                if query_lower in line.lower():
                    hits.append(f"  L{i}: {line.strip()[:200]}")
            if hits:
                rel = f.relative_to(NS_ROOT) if NS_ROOT in f.parents else f.name
                results.append(f"\n**[{label}] {rel}**")
                results.extend(hits[:3])
                if len(results) >= max_results * 3:
                    break
        if len(results) >= max_results * 3:
            break

    if not results:
        return f"No matches for '{query}' across the nervous system."
    return f"## Global Search: '{query}'\n\n" + "\n".join(results)

@mcp.tool()
def list_corpus_capsules() -> str:
    """
    List all corpus capsules with their titles and categories.
    """
    index_path = CORPUS_DIR / "INDEX.md"
    if index_path.exists():
        return _read_file(index_path)
    # Fallback: list files
    files = sorted(CORPUS_DIR.glob("*.md"))
    return "\n".join(f"- {f.name}" for f in files if f.name != "INDEX.md")

@mcp.tool()
def read_corpus_capsule(capsule_id: str) -> str:
    """
    Read a specific corpus capsule by number or filename.
    Example: read_corpus_capsule("01") or read_corpus_capsule("54_athena_the_archetype")
    """
    # Try direct match
    matches = list(CORPUS_DIR.glob(f"{capsule_id}*.md"))
    if matches:
        return _read_file(matches[0])

    # Try with leading zeros
    if capsule_id.isdigit():
        padded = capsule_id.zfill(2)
        matches = list(CORPUS_DIR.glob(f"{padded}_*.md"))
        if matches:
            return _read_file(matches[0])

    return f"Capsule '{capsule_id}' not found."

@mcp.tool()
def read_frontier(chapter_code: str) -> str:
    """
    Read the frontier bundle for a chapter. Frontiers represent
    the current boundary of completed work for each chapter.
    Example: read_frontier("Ch03")
    """
    bundle = list(FRONTIERS_DIR.glob(f"{chapter_code}_*frontier_bundle.md"))
    if bundle:
        return _read_file(bundle[0])

    # List available frontiers
    available = [
        f.name for f in FRONTIERS_DIR.glob("*frontier_bundle.md")
    ]
    return (
        f"No frontier bundle for '{chapter_code}'. Available:\n"
        + "\n".join(f"  - {a}" for a in available)
    )

# ══════════════════════════════════════════════════════════════════════
#  TOOLS — Nervous System Navigation (Phase 1 expansion)
# ══════════════════════════════════════════════════════════════════════

@mcp.tool()
def explore_nervous_system(path: str = "", depth: int = 1) -> str:
    """
    Explore any directory in ACTIVE_NERVOUS_SYSTEM.

    Args:
        path: subdirectory relative to ACTIVE_NERVOUS_SYSTEM
              (e.g. '21_4D_TESSERACT_BODY' or '15_MOTION_CONSTITUTION/01_CORE')
              Empty string = list all 28 top-level directories.
        depth: 1 = immediate children, 2 = include grandchildren.

    Returns directory listing with file counts and types.
    """
    target = NS_ROOT / path if path else NS_ROOT
    if not target.exists():
        return f"[NOT FOUND] {path or 'ACTIVE_NERVOUS_SYSTEM'} (resolved: {target})"
    if not target.is_dir():
        return _read_file(target)

    lines = [f"## {path or 'ACTIVE_NERVOUS_SYSTEM'}\n"]
    entries = sorted(target.iterdir())
    dirs, files = [], []
    for e in entries:
        if e.is_dir():
            child_count = sum(1 for _ in e.rglob("*") if _.is_file())
            dirs.append(f"  [DIR]  {e.name}/  ({child_count} files)")
            if depth >= 2:
                for sub in sorted(e.iterdir()):
                    if sub.is_dir():
                        sc = sum(1 for _ in sub.rglob("*") if _.is_file())
                        dirs.append(f"         {e.name}/{sub.name}/  ({sc} files)")
                    else:
                        dirs.append(f"         {e.name}/{sub.name}")
        else:
            size = e.stat().st_size
            files.append(f"  [FILE] {e.name}  ({size:,} bytes)")

    lines.extend(dirs)
    lines.extend(files)
    lines.append(f"\n**Total**: {len(dirs)} dirs, {len(files)} files")
    return "\n".join(lines)

@mcp.tool()
def read_nervous_system_file(path: str) -> str:
    """
    Read any file within ACTIVE_NERVOUS_SYSTEM by relative path.

    Examples:
        read_nervous_system_file('15_MOTION_CONSTITUTION/01_LEGAL_MOVES.md')
        read_nervous_system_file('21_4D_TESSERACT_BODY/TESSERACT_OVERVIEW.md')
        read_nervous_system_file('README.md')
    """
    target = NS_ROOT / path
    if not target.exists():
        # Fuzzy search
        parts = Path(path).parts
        if parts:
            parent = NS_ROOT / parts[0] if len(parts) > 1 else NS_ROOT
            if parent.exists():
                candidates = [f.name for f in parent.rglob("*") if parts[-1].lower() in f.name.lower()][:10]
                if candidates:
                    return (
                        f"[NOT FOUND] '{path}'. Similar files in {parts[0]}:\n"
                        + "\n".join(f"  - {c}" for c in candidates)
                    )
        return f"[NOT FOUND] '{path}' in ACTIVE_NERVOUS_SYSTEM."
    if target.is_dir():
        return explore_nervous_system(path)
    return _read_file(target)

@mcp.tool()
def read_motion_constitution(document: str = "index") -> str:
    """
    Read documents from the Motion Constitution (dir 15).
    Defines the 10 legal move primitives, 3 invariants, and lawful motion rules.

    Args:
        document: 'index' for overview, or filename/keyword to find specific doc.
    """
    return _read_specialized_dir(MOTION_DIR, document, "Motion Constitution")

@mcp.tool()
def read_dimensional_body(dimension: str = "4D", document: str = "index") -> str:
    """
    Read dimensional body documents (dirs 21-23).
    Covers the 4D Tesseract Body, 5D Emergent Body, and 6D Holographic Seed.

    Args:
        dimension: '4D', '5D', or '6D'
        document: 'index' for overview, or filename/keyword.
    """
    dim_map = {"4D": TESSERACT_DIR, "5D": EMERGENT_DIR, "6D": HOLOGRAPHIC_DIR}
    target = dim_map.get(dimension.upper())
    if not target:
        return f"Unknown dimension '{dimension}'. Use: 4D, 5D, 6D"
    return _read_specialized_dir(target, document, f"{dimension} Dimensional Body")

@mcp.tool()
def read_command_protocol(document: str = "index") -> str:
    """
    Read Command Protocol documents (dir 19).
    Defines execution commands, gate protocols, and command membrane.

    Args:
        document: 'index' for overview, or filename/keyword.
    """
    return _read_specialized_dir(COMMAND_DIR, document, "Command Protocol")

@mcp.tool()
def read_civilization(document: str = "index") -> str:
    """
    Read Civilization governance documents (dir 09).
    Defines governance structures, civilizational metrics, and social layer.

    Args:
        document: 'index' for overview, or filename/keyword.
    """
    return _read_specialized_dir(CIVILIZATION_DIR, document, "Civilization")

@mcp.tool()
def read_synthesis(document: str = "index") -> str:
    """
    Read Synthesis documents (dir 12).
    Cross-chapter integration, deep synthesis results.

    Args:
        document: 'index' for overview, or filename/keyword.
    """
    return _read_specialized_dir(SYNTHESIS_DIR, document, "Synthesis")

@mcp.tool()
def read_super_cycle(document: str = "index") -> str:
    """
    Read Super Cycle 57 documents (dir 17).
    The 57-beat super cycle execution state and protocol.

    Args:
        document: 'index' for overview, or filename/keyword.
    """
    return _read_specialized_dir(SUPER_CYCLE_DIR, document, "Super Cycle 57")

def _read_specialized_dir(directory: Path, document: str, label: str) -> str:
    """Helper: read from a specialized nervous system directory."""
    if not directory.exists():
        return f"[NOT FOUND] {label} directory."

    if document == "index":
        # Return listing + any README/INDEX file
        lines = [f"## {label}\n"]
        readme = None
        for candidate in ["README.md", "INDEX.md", "00_INDEX.md", "00_README.md"]:
            p = directory / candidate
            if p.exists():
                readme = p
                break
        if readme:
            lines.append(_read_file(readme, limit=50))
            lines.append("\n---\n")

        all_files = sorted(directory.rglob("*"))
        for f in all_files:
            if f.is_file():
                rel = f.relative_to(directory)
                lines.append(f"  - {rel}")
        lines.append(f"\n**Total files**: {sum(1 for f in all_files if f.is_file())}")
        return "\n".join(lines)

    # Search for matching file
    doc_lower = document.lower()
    matches = [
        f for f in directory.rglob("*")
        if f.is_file() and doc_lower in f.name.lower()
    ]
    if matches:
        return _read_file(matches[0])

    # No match — list available
    available = sorted(
        f.relative_to(directory) for f in directory.rglob("*") if f.is_file()
    )
    return (
        f"No document matching '{document}' in {label}. Available:\n"
        + "\n".join(f"  - {a}" for a in available[:30])
    )

# ══════════════════════════════════════════════════════════════════════
#  RESOURCES — Readable content exposed via resource URIs
# ══════════════════════════════════════════════════════════════════════

@mcp.resource("athena://status")
def resource_status() -> str:
    """Current Athena system status."""
    return athena_status()

@mcp.resource("athena://board")
def resource_board() -> str:
    """Current board status."""
    return read_board_status()

@mcp.resource("athena://loop")
def resource_loop() -> str:
    """Current loop state and restart seed."""
    return read_loop_state()

# ══════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    mcp.run()
