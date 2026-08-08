from __future__ import annotations

import importlib.util
from pathlib import Path

_legacy_path=Path(__file__).resolve().parent.parent / "registry.py"
_spec=importlib.util.spec_from_file_location("athena_mcp.orchestration_hug._registry_impl",_legacy_path)
_impl=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_impl)

HUG_PARAMS=_impl.HUG_PARAMS
HUG_STATUS_ORDER=_impl.HUG_STATUS_ORDER

class HugRegistry(_impl.HugRegistry):
    def state(self,impl_id:str):
        out=super().state(impl_id)
        if out and isinstance(out.get("parameter_semantics"),dict):
            raw=out["parameter_semantics"]
            out["parameter_semantics"]={name:raw[name] for name in HUG_PARAMS if name in raw}
        return out

__all__=["HUG_PARAMS","HUG_STATUS_ORDER","HugRegistry"]
