"""
config.py -- Global configuration for the Athena Process Language Compiler.

Centralises filesystem paths, default settings, and the backend registry
so that every module resolves configuration from a single source.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Root paths
# ---------------------------------------------------------------------------

#: Root of the rosetta_machine tree (two levels up from this file).
ROSETTA_ROOT: Path = Path(__file__).resolve().parent.parent

#: Root of the compiler package itself.
COMPILER_ROOT: Path = Path(__file__).resolve().parent

#: Default GAWM output directory.
GAWM_ROOT: Path = ROSETTA_ROOT / "GLOBAL_ATHENA"

# ---------------------------------------------------------------------------
# GAWM sub-directories
# ---------------------------------------------------------------------------

GAWM_REGISTRY: Path = GAWM_ROOT / "00_REGISTRY"
GAWM_TUNNELS: Path = GAWM_ROOT / "01_TUNNELS"
GAWM_PACKS: Path = GAWM_ROOT / "02_PACKS"
GAWM_RUNTIME: Path = GAWM_ROOT / "04_RUNTIME"

GAWM_DIRS: list[Path] = [
    GAWM_REGISTRY,
    GAWM_TUNNELS,
    GAWM_PACKS,
    GAWM_RUNTIME,
]

# ---------------------------------------------------------------------------
# Backend registry
# ---------------------------------------------------------------------------

#: Known rendering backends and their module paths.
BACKEND_REGISTRY: dict[str, str] = {
    "latex": "athena_process_compiler.renderers.latex",
    "sympy": "athena_process_compiler.renderers.sympy",
    "codegen": "athena_process_compiler.renderers.codegen",
    "prose": "athena_process_compiler.renderers.prose",
    "mermaid": "athena_process_compiler.renderers.mermaid",
}

# ---------------------------------------------------------------------------
# Default settings
# ---------------------------------------------------------------------------

#: Default hash algorithm used for content-addressed fingerprints.
HASH_ALGORITHM: str = "sha256"

#: Minimum cross-backend consistency score to qualify as OK.
CONSISTENCY_THRESHOLD: float = 0.95

#: Minimum cross-backend consistency score to qualify as NEAR.
NEAR_THRESHOLD: float = 0.70

#: Default replay mode for new OperatorIR nodes.
DEFAULT_REPLAY_MODE: str = "live"

#: Maximum number of replay steps before forced termination.
MAX_REPLAY_DEPTH: int = 256

#: AtlasPack default compression (currently none; reserved for future).
ATLASPACK_COMPRESS: bool = False

#: JSON serialisation defaults.
JSON_INDENT: int = 2
JSON_ENSURE_ASCII: bool = False


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def ensure_gawm_dirs() -> None:
    """Create all GAWM sub-directories if they do not already exist."""
    for d in GAWM_DIRS:
        d.mkdir(parents=True, exist_ok=True)


def get_backend_module(name: str) -> str:
    """Return the dotted module path for a registered backend.

    Raises:
        KeyError: If *name* is not in the backend registry.
    """
    if name not in BACKEND_REGISTRY:
        raise KeyError(
            f"Unknown backend {name!r}. "
            f"Registered backends: {sorted(BACKEND_REGISTRY)}"
        )
    return BACKEND_REGISTRY[name]


def register_backend(name: str, module_path: str) -> None:
    """Add or overwrite a backend entry in the registry.

    Args:
        name:        Short identifier (e.g. "latex").
        module_path: Fully-qualified Python module path.
    """
    BACKEND_REGISTRY[name] = module_path
