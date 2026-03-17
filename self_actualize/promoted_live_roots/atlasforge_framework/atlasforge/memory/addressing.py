"""Crystal address normalization utilities.

AtlasForge uses a 4×4×4×4 = 256 cell "crystal" taxonomy (Pole × Lens × Layer × Depth).
Entries in the memory bank can optionally carry a crystal address in two forms:

- ``extra["crystal_address"]``: a human-readable string
- ``extra["crystal_index"]``: an integer 0..255

This module provides a shared, best-effort normalizer so that both structured
knowledge records and plain notes can consistently attach addresses.
"""

from __future__ import annotations

from typing import Any, Optional, Tuple
import re


def _try_int(s: str) -> Optional[int]:
    try:
        return int(s)
    except Exception:
        return None


def _normalize_token(s: str) -> str:
    return re.sub(r"\s+", "", (s or "").strip()).lower()


def _parse_layer_token(tok: str):
    # Late import to avoid cycles.
    import atlasforge as af  # type: ignore

    t = _normalize_token(tok)
    if t in ("0", "l0", "objects", "obj", "o", "object"):
        return af.Layer.OBJECTS
    if t in ("1", "l1", "operators", "operator", "ops", "op"):
        return af.Layer.OPERATORS
    if t in ("2", "l2", "invariants", "invariant", "inv", "i"):
        return af.Layer.INVARIANTS
    if t in ("3", "l3", "artifacts", "artifact", "art", "a"):
        return af.Layer.ARTIFACTS

    # Try enum name
    for layer in list(af.Layer):
        if _normalize_token(layer.name) == t:
            return layer
    return None


def _parse_depth_token(tok: str):
    import atlasforge as af  # type: ignore

    t = _normalize_token(tok)
    if t in ("0", "d0", "surface", "s"):
        return af.Depth.SURFACE
    if t in ("1", "d1", "detail", "d"):
        return af.Depth.DETAIL
    if t in ("2", "d2", "deep"):
        return af.Depth.DEEP
    if t in ("3", "d3", "foundation", "f"):
        return af.Depth.FOUNDATION

    for depth in list(af.Depth):
        if _normalize_token(depth.name) == t:
            return depth
    return None


def _parse_pole_token(tok: str):
    import atlasforge as af  # type: ignore

    t = (tok or "").strip()
    t_norm = _normalize_token(tok)
    # Accept the glyphs directly.
    for pole in list(af.Pole):
        if t == pole.value:
            return pole
    # Names / aliases.
    if t_norm in ("d", "discrete", "earth", "alpha", "α"):
        return af.Pole.DISCRETE
    if t_norm in ("ω", "o", "continuous", "water", "d", "𝔇".lower()):
        # note: "d" ambiguity; discrete already handled; keep as continuous only if explicit
        if t == "Ω" or t_norm in ("ω", "o", "continuous", "water"):
            return af.Pole.CONTINUOUS
    if t_norm in ("σ", "s", "stochastic", "fire", "theta", "θ"):
        return af.Pole.STOCHASTIC
    if t_norm in ("ψ", "p", "hierarchical", "recursive", "air", "lambda", "λ"):
        return af.Pole.HIERARCHICAL

    for pole in list(af.Pole):
        if _normalize_token(pole.name) == t_norm:
            return pole
    return None


def _parse_lens_token(tok: str):
    import atlasforge as af  # type: ignore

    t = (tok or "").strip()
    t_norm = _normalize_token(tok)
    for lens in list(af.Lens):
        if t == lens.value:
            return lens
    if t_norm in ("square", "structural", "structure", "□"):
        return af.Lens.SQUARE
    if t_norm in ("flower", "cyclic", "cycle", "✿"):
        return af.Lens.FLOWER
    if t_norm in ("cloud", "probabilistic", "probability", "☁"):
        return af.Lens.CLOUD
    if t_norm in ("fractal", "recursive", "recursion", "❋"):
        return af.Lens.FRACTAL

    for lens in list(af.Lens):
        if _normalize_token(lens.name) == t_norm:
            return lens
    return None


def parse_crystal_address_string(address: str) -> Optional[int]:
    """Try to parse a crystal address string into an index 0..255.

    Accepted examples:
    - ``"D·□·OBJECTS·0"``
    - ``"Ω·✿·OPERATORS·2"``
    - ``"D·□·L0·d0"``
    - ``"12"``  (treated as index)
    """
    s = (address or "").strip()
    if not s:
        return None

    # Direct integer string
    n = _try_int(s)
    if n is not None:
        if 0 <= n <= 255:
            return n
        return None

    # Split on common separators; prefer the canonical middle dot.
    if "·" in s:
        parts = [p.strip() for p in s.split("·")]
    elif "|" in s:
        parts = [p.strip() for p in s.split("|")]
    elif "/" in s:
        parts = [p.strip() for p in s.split("/")]
    elif "." in s:
        parts = [p.strip() for p in s.split(".")]
    else:
        # As a last resort, split on whitespace.
        parts = [p.strip() for p in re.split(r"\s+", s) if p.strip()]

    if len(parts) != 4:
        return None

    pole_t, lens_t, layer_t, depth_t = parts

    pole = _parse_pole_token(pole_t)
    lens = _parse_lens_token(lens_t)
    layer = _parse_layer_token(layer_t)
    depth = _parse_depth_token(depth_t)

    if pole is None or lens is None or layer is None or depth is None:
        return None

    import atlasforge as af  # type: ignore

    try:
        idx = af.CrystalAddress(pole=pole, lens=lens, layer=layer, depth=depth).to_index()
        if 0 <= idx <= 255:
            return int(idx)
    except Exception:
        return None
    return None


def normalize_address(address: Any) -> Tuple[Optional[str], Optional[int]]:
    """Normalize a crystal address into (string, linear_index).

    Accepts:
    - ``None``
    - ``int`` (0..255)
    - ``str`` (attempted parse into index; always preserved as string)
    - any object with ``to_index()`` and/or ``__str__``
    """
    if address is None:
        return None, None

    # Integer index
    if isinstance(address, int):
        idx = int(address)
        try:
            import atlasforge as af  # local import to avoid cycles

            return str(af.CrystalAddress.from_index(idx)), idx
        except Exception:
            return None, idx

    # String address
    if isinstance(address, str):
        s = address.strip()
        idx = parse_crystal_address_string(s)
        return (s or None), idx

    # CrystalAddress-like objects
    try:
        idx = None
        if hasattr(address, "to_index"):
            idx = int(address.to_index())  # type: ignore[attr-defined]
        s = str(address)
        if idx is None and isinstance(s, str) and s.strip():
            idx = parse_crystal_address_string(s.strip())
        return (s.strip() or None), idx
    except Exception:
        return None, None
