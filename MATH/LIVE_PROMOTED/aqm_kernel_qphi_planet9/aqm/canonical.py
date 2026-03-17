from __future__ import annotations

import json
from dataclasses import is_dataclass, asdict
from typing import Any

class CanonicalizationError(ValueError):
    pass

def _normalize(obj: Any) -> Any:
    # Convert dataclasses to dicts
    if is_dataclass(obj):
        obj = asdict(obj)

    # Primitive JSON types are fine
    if obj is None or isinstance(obj, (bool, int, str)):
        return obj

    # Floats are allowed but discouraged for cross-platform determinism.
    # We encode them as a tagged string to avoid JSON float formatting drift.
    if isinstance(obj, float):
        # Use repr which is round-trip in Python 3, but still platform-ish.
        # Better: store decimals as strings upstream.
        return {"__float__": repr(obj)}

    if isinstance(obj, bytes):
        # deterministic base16
        return {"__bytes__": obj.hex()}

    if isinstance(obj, (list, tuple)):
        return [_normalize(x) for x in obj]

    if isinstance(obj, set):
        return {"__set__": sorted([_normalize(x) for x in obj], key=lambda x: json.dumps(x, ensure_ascii=False, sort_keys=True))}

    if isinstance(obj, dict):
        # Keys must be strings for canonical JSON.
        norm = {}
        for k, v in obj.items():
            if not isinstance(k, str):
                raise CanonicalizationError(f"Non-string key in dict: {k!r}")
            norm[k] = _normalize(v)
        return norm

    raise CanonicalizationError(f"Unsupported type for canonicalization: {type(obj).__name__}")

def canonical_json_bytes(obj: Any) -> bytes:
    norm = _normalize(obj)
    # Canonical JSON: UTF-8, no whitespace, sorted keys.
    s = json.dumps(norm, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return s.encode("utf-8")

def canonical_json_str(obj: Any) -> str:
    return canonical_json_bytes(obj).decode("utf-8")
