"""Compatibility-preserving registration seam for Ω + MMLG.2 + MMLG.3.

Python resolves a package before a same-named module. This package loads the
frozen legacy ``whole_crystal_autofill.py`` body from its exact sibling path,
re-exports every public symbol unchanged, and extends only the registration
function so the governed Meta Harness runtimes are mounted in the unified MCP
host.

The legacy implementation, constants, data path, closure digests, and tests
remain authoritative. The shims add no truth, evidence, authority, deployment,
or production effect.
"""

from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
from typing import Any


_PARENT_PACKAGE = __name__.rsplit(".", 1)[0]
_LEGACY_NAME = f"{_PARENT_PACKAGE}._whole_crystal_autofill_legacy"
_LEGACY_PATH = Path(__file__).resolve().parent.parent / "whole_crystal_autofill.py"

_spec = spec_from_file_location(_LEGACY_NAME, _LEGACY_PATH)
if _spec is None or _spec.loader is None:  # pragma: no cover - import machinery guard
    raise ImportError(f"cannot load legacy whole-crystal module at {_LEGACY_PATH}")
_legacy = module_from_spec(_spec)
sys.modules[_LEGACY_NAME] = _legacy
_spec.loader.exec_module(_legacy)

for _name in dir(_legacy):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_legacy, _name)

_register_legacy_whole_crystal_autofill = _legacy.register_whole_crystal_autofill

from ..meta_ml_game_v2 import register_meta_ml_game_v2
from ..meta_ml_game_v3 import register_meta_ml_game_v3


def register_whole_crystal_autofill(mcp: Any) -> None:
    """Register unchanged Ω, then governed MMLG.2 and MMLG.3 surfaces."""
    _register_legacy_whole_crystal_autofill(mcp)
    register_meta_ml_game_v2(mcp)
    register_meta_ml_game_v3(mcp)


MMLG2_MOUNT = {
    "schema": "athena.meta-ml-game-mcp-mount/v2",
    "legacy_module": str(_LEGACY_PATH),
    "control_head": "be1dec2d825e7a32cd7a373f08e62cf8a091f65f",
    "tools_added": 12,
    "resources_added": 3,
    "external_promotion_authority": False,
    "production_effect": "NONE",
}

MMLG3_MOUNT = {
    "schema": "athena.meta-ml-game-guild-hall-mcp-mount/v3",
    "runtime_parent_head": "77f8a7b456b48d173360c684d0dc2d79e7949009",
    "quest_projection": "12 domains x 12 goals = 144 quests",
    "source_adapters": 4,
    "canary_roles": 3,
    "tools_added": 11,
    "resources_added": 4,
    "guild_hall_source_board_written": False,
    "external_promotion_authority": False,
    "production_effect": "NONE",
}
