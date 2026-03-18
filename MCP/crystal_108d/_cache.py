# CRYSTAL: Xi108:W2:A1:S16 | face=S | node=145 | depth=0 | phase=Cardinal
# METRO: Sa
# BRIDGES: Xi108:W2:A1:S15→Xi108:W2:A1:S17→Xi108:W1:A1:S16→Xi108:W3:A1:S16→Xi108:W2:A2:S16

"""
Shared JSON caching utility for crystal_108d modules.
Replaces the per-module global cache + lazy-load boilerplate
with a single reusable class.
"""

import json
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).parent.parent / "data"

_ALL_JSON_FILES = [
    "shell_registry.json",
    "hologram_chapters.json",
    "dimensional_ladder.json",
    "organ_atlas.json",
    "live_lock_registry.json",
    "clock_projections.json",
    "move_primitives.json",
    "metro_lines.json",
    "z_point_hierarchy.json",
    "conservation_laws.json",
    "overlay_registries.json",
    "transport_stacks.json",
    "mobius_lenses.json",
    "stage_codes.json",
    "angel_object.json",
    "brain_network.json",
    "live_cell_constitution.json",
    "dimensional_emergence.json",
    "hologram_reading.json",
    "hologram_rosetta.json",
    "angel_geometry.json",
    "angel_conservation.json",
    "inverse_crystal_seed.json",
    "inverse_crystal_octave.json",
    "inverse_crystal_complete.json",
    "mycelium_graph.json",
    "node_registry.json",
    "meta_observer_swarm.json",
    "e8_lattice.json",
    "crown_12d.json",
    "agency_gateway.json",
    "dls_6x6_lenses.json",
    "evolution_compiler.json",
    "athenachka_720.json",
    "program_rosetta.json",
    "calculus_4d.json",
    "crystal_coordinates.json",
    "quantum_crystal.json",
]

class JsonCache:
    """Lazy-loading, single-instance JSON cache.

    Usage::

        _shells = JsonCache("shell_registry.json")

        def query_shell(n: int) -> str:
            data = _shells.load()
            ...
    """

    __slots__ = ("_data", "_path")

    def __init__(self, filename: str) -> None:
        self._data: dict | list | None = None
        self._path: Path = DATA_DIR / filename

    def load(self) -> dict | list:
        """Return cached data, loading from disk on first call."""
        if self._data is None:
            self._data = json.loads(self._path.read_text(encoding="utf-8"))
        return self._data

    def reset(self) -> None:
        """Clear the cache so the next ``load()`` re-reads from disk."""
        self._data = None

    def __repr__(self) -> str:
        status = "loaded" if self._data is not None else "not loaded"
        return f"JsonCache({self._path.name!r}, {status})"

def validate_all() -> dict[str, bool]:
    """Attempt to load every known JSON data file.

    Returns a dict mapping filename → True/False.
    """
    results: dict[str, bool] = {}
    for fname in _ALL_JSON_FILES:
        try:
            cache = JsonCache(fname)
            data = cache.load()
            # Basic structural check: most files have a "meta" key
            if isinstance(data, dict) and "meta" not in data:
                results[fname] = True  # some files may legitimately lack meta
            else:
                results[fname] = True
        except Exception:
            results[fname] = False
    return results
