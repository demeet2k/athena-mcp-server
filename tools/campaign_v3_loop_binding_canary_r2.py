from __future__ import annotations

import importlib.util
from pathlib import Path

_BASE_PATH = Path(__file__).with_name("campaign_v3_loop_binding_canary.py")
_SPEC = importlib.util.spec_from_file_location("campaign_v3_loop_binding_canary_base", _BASE_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError("unable to load base loop-binding canary")
_base = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_base)


def _assert_remote(result: dict, label: str) -> None:
    publish = result.get("remote_publish") or {}
    if publish.get("shared_frontier_verified") is not True:
        raise AssertionError(f"{label}: shared remote publication not verified")
    if "durable_return" in result and result.get("durable_return") is not True:
        raise AssertionError(f"{label}: durable_return is not true")


_base.assert_remote = _assert_remote
_base.main()
