"""Import seam for the standalone KC144 MAX–RAG v1 cartridge."""

from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys


_PARENT_PACKAGE = __name__.rsplit(".", 1)[0]
_IMPLEMENTATION_NAME = f"{_PARENT_PACKAGE}._max_rag_game_v1_impl"
_IMPLEMENTATION_PATH = Path(__file__).resolve().parent.parent / "max_rag_game_v1.py"

_spec = spec_from_file_location(_IMPLEMENTATION_NAME, _IMPLEMENTATION_PATH)
if _spec is None or _spec.loader is None:  # pragma: no cover
    raise ImportError(f"cannot load MAX-RAG implementation at {_IMPLEMENTATION_PATH}")
_impl = module_from_spec(_spec)
sys.modules[_IMPLEMENTATION_NAME] = _impl
_spec.loader.exec_module(_impl)

for _name in dir(_impl):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_impl, _name)

MAX_RAG_IMPORT_SEAM = {
    "schema": "athena.max-rag-import-seam/v1",
    "implementation": str(_IMPLEMENTATION_PATH),
    "runtime_law_changed": False,
    "authority_effect": "NONE",
    "production_effect": "NONE",
}
