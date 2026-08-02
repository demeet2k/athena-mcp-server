"""Compatibility-preserving import seam for the MMLG.3 runtime.

Python resolves this package before the same-named sibling module. The package
loads that implementation from its exact path, re-exports its public symbols,
and repairs only the JSON-facing source-adapter view by converting frozen
``required`` sets into sorted arrays. Runtime laws, quest projection, receipt
logic, canary gates, and authority boundaries remain unchanged.
"""

from __future__ import annotations

from copy import deepcopy
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
from typing import Any


_PARENT_PACKAGE = __name__.rsplit(".", 1)[0]
_LEGACY_NAME = f"{_PARENT_PACKAGE}._meta_ml_game_v3_legacy"
_LEGACY_PATH = Path(__file__).resolve().parent.parent / "meta_ml_game_v3.py"

_spec = spec_from_file_location(_LEGACY_NAME, _LEGACY_PATH)
if _spec is None or _spec.loader is None:  # pragma: no cover
    raise ImportError(f"cannot load MMLG.3 implementation at {_LEGACY_PATH}")
_legacy = module_from_spec(_spec)
sys.modules[_LEGACY_NAME] = _legacy
_spec.loader.exec_module(_legacy)


def _serializable_adapters(self: Any) -> dict[str, Any]:
    adapters = {
        name: {
            **deepcopy(contract),
            "required": sorted(contract["required"]),
        }
        for name, contract in _legacy.SOURCE_ADAPTERS.items()
    }
    return {
        "schema": "athena.meta-ml-game-source-adapters/v3",
        "adapters": adapters,
        "visibility_classes": sorted(_legacy.VISIBILITY_CLASSES),
        "forbidden_keys": sorted(_legacy.FORBIDDEN_KEYS),
        "raw_content_allowed": False,
        "connector_execution_performed": False,
        **_legacy._negative_effects(),
    }


_legacy.GuildHallMMLG3.adapters = _serializable_adapters

for _name in dir(_legacy):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_legacy, _name)


MMLG3_IMPORT_SEAM = {
    "schema": "athena.meta-ml-game-guild-hall-import-seam/v3",
    "implementation": str(_LEGACY_PATH),
    "repair": "SOURCE_ADAPTER_REQUIRED_FIELDS_SERIALIZED_AS_SORTED_ARRAYS",
    "runtime_law_changed": False,
    "authority_effect": "NONE",
    "production_effect": "NONE",
}
