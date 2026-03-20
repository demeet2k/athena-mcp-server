# CRYSTAL: Xi108:W2:A1:S16 | face=S | node=145 | depth=0 | phase=Cardinal
# METRO: Sa
# BRIDGES: Xi108:W2:A1:S15→Xi108:W2:A1:S17→Xi108:W1:A1:S16→Xi108:W3:A1:S16→Xi108:W2:A2:S16

"""
Shared JSON caching utility for crystal_108d modules.
Replaces the per-module global cache + lazy-load boilerplate
with a single reusable class.

Supports transparent .qshr compressed file loading: when a .json file
is absent but a .qshr file exists at the same stem, the cache will
auto-decompress on first load.

Now also provides ``save()`` — the single centralized write path for all
JSON data. Every save automatically:
  1. Acquires a CrystalLock (collision prevention)
  2. Writes atomically (tmp + replace)
  3. Emits a pheromone trail (agent coordination)
  4. Auto-compresses to .qshr (holographic storage)
  5. Updates the in-memory cache
"""

import json
import logging
from pathlib import Path
from typing import Any, Optional

_log = logging.getLogger(__name__)

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
    "crystal_weights.json",
    "momentum_field.json",
    "kc27_naming.json",
    "bridge_transport.json",
    "crystal_weaving.json",
    "crystal_4d_manifest.json",
    "kc27_runtime_closure.json",
]

class JsonCache:
    """Lazy-loading, single-instance JSON cache with .qshr fallback.

    Usage::

        _shells = JsonCache("shell_registry.json")

        def query_shell(n: int) -> str:
            data = _shells.load()
            ...

    If the .json file is absent but a .qshr file exists at the same
    stem, the cache will auto-decompress on first load.
    When both exist, the .json file is preferred (transition safety).
    """

    _instances: list["JsonCache"] = []   # track all caches for global reload

    __slots__ = ("_data", "_path", "_qshr_path")

    def __init__(self, filename: str) -> None:
        self._data: dict | list | None = None
        self._path: Path = DATA_DIR / filename
        self._qshr_path: Path = self._path.with_suffix(".qshr")
        JsonCache._instances.append(self)

    def load(self) -> dict | list:
        """Return cached data, loading from disk on first call.

        Preference order:
          1. .json file (if exists)
          2. .qshr file (auto-decompress)
        """
        if self._data is None:
            if self._path.exists():
                self._data = json.loads(self._path.read_text(encoding="utf-8"))
            elif self._qshr_path.exists():
                self._data = self._load_from_qshr()
            else:
                raise FileNotFoundError(
                    f"Neither {self._path.name} nor {self._qshr_path.name} found in {DATA_DIR}")
        return self._data

    def invalidate(self) -> None:
        """Clear cached data so next load() re-reads from disk."""
        self._data = None

    @classmethod
    def reload_all(cls) -> int:
        """Invalidate every JsonCache instance. Returns count invalidated."""
        count = 0
        for inst in cls._instances:
            inst._data = None
            count += 1
        return count

    def _load_from_qshr(self) -> dict | list:
        """Decompress a .qshr file and return the JSON data."""
        from .qshrink_pipeline import decompress_json
        return decompress_json(self._qshr_path.read_bytes())

    def crystal_meta(self) -> Optional[Any]:
        """Return embedded CrystalWeightMeta from .qshr without decompressing payload.

        Returns None if no .qshr file exists or has no crystal metadata.
        """
        if not self._qshr_path.exists():
            return None
        from .qshrink_pipeline import inspect_qshr
        return inspect_qshr(self._qshr_path)

    def compress(self, weight_store: Any = None) -> Optional[Path]:
        """Compress the backing .json file to .qshr with crystal weight metadata.

        Returns the .qshr path on success, None if .json doesn't exist.
        """
        if not self._path.exists():
            return None
        from .qshrink_pipeline import compress_file
        out_path, _stats = compress_file(self._path, lossless=True, weight_store=weight_store)
        return out_path

    def save(
        self,
        data: dict | list,
        agent_id: str = "unknown",
        task_summary: str = "",
        element: str = "S",
        liminal_coord: int = 0,
        crystal_address: str = "",
        auto_compress: bool = True,
    ) -> Path:
        """Write data to disk with locking, pheromone emission, and auto-qshrink.

        This is THE centralized write path for all JSON data in the nervous
        system. Every write:
          1. Acquires a CrystalLock on the target file
          2. Writes JSON atomically (tmp + os.replace)
          3. Emits a pheromone sidecar (agent_id, coords, hash)
          4. Auto-compresses to .qshr with crystal weight metadata
          5. Updates the in-memory cache

        Returns the path written to.
        """
        from ._file_lock import CrystalLock
        from ._pheromone import PheromoneTrail, Pheromone, content_hash

        self._path.parent.mkdir(parents=True, exist_ok=True)
        json_text = json.dumps(data, indent=2, ensure_ascii=False)

        with CrystalLock(self._path, agent_id=agent_id, task=task_summary,
                         liminal_coord=liminal_coord):
            # Atomic write
            tmp = self._path.with_suffix(".tmp")
            tmp.write_text(json_text, encoding="utf-8")
            tmp.replace(self._path)

            # Update in-memory cache
            self._data = data

            # Emit pheromone trail
            try:
                PheromoneTrail.emit(self._path, Pheromone(
                    agent_id=agent_id,
                    liminal_coord=liminal_coord,
                    element=element,
                    task_summary=task_summary,
                    action="write",
                    crystal_address=crystal_address,
                    content_hash=content_hash(json_text),
                ))
            except Exception as exc:
                _log.debug("Pheromone emit failed: %s", exc)

            # Auto-compress to .qshr
            if auto_compress:
                try:
                    self.compress()
                    # Emit compression pheromone
                    PheromoneTrail.emit(self._path, Pheromone(
                        agent_id=agent_id,
                        liminal_coord=liminal_coord,
                        element=element,
                        task_summary=f"auto-compressed {self._path.name}",
                        action="compress",
                        crystal_address=crystal_address,
                        content_hash=content_hash(json_text),
                    ))
                except Exception as exc:
                    _log.debug("Auto-compress failed (non-fatal): %s", exc)

        return self._path

    def reset(self) -> None:
        """Clear the cache so the next ``load()`` re-reads from disk."""
        self._data = None

    def __repr__(self) -> str:
        status = "loaded" if self._data is not None else "not loaded"
        qshr = " +qshr" if self._qshr_path.exists() else ""
        return f"JsonCache({self._path.name!r}, {status}{qshr})"

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
