"""MYTHOS OS module registry.

Each ``*.py`` file in this package (other than this one) exports ``MODULES``: a
list of tradition modules conforming to ``athena_mcp.mythos_kernel.validate_module``.
This package concatenates them in sorted file order.  The module dicts are the
source of truth; ``spec/MYTHOS_OS_V1.json`` is an export.
"""
from __future__ import annotations

import os
from importlib import import_module
from typing import Any, Dict, List

_HERE = os.path.dirname(os.path.abspath(__file__))
FAMILY_FILES = sorted(
    f[:-3] for f in os.listdir(_HERE) if f.endswith(".py") and f != "__init__.py" and not f.startswith("_")
)

MODULES: List[Dict[str, Any]] = []
for _name in FAMILY_FILES:
    _mod = import_module(f"{__name__}.{_name}")
    MODULES.extend(getattr(_mod, "MODULES", []))

MODULE_INDEX: Dict[str, Dict[str, Any]] = {m["id"]: m for m in MODULES}


def get_module(module_id: str) -> Dict[str, Any]:
    return MODULE_INDEX[module_id]
