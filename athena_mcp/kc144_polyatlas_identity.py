from __future__ import annotations

"""Immutable KC144/KC27 identities and finite chart helpers."""

import hashlib
import json
from typing import Any, Iterable

POLYATLAS_VERSION = "KC144.POLYATLAS.1.0.0"
HOST_CARDINALITY = 144
ROSETTA_CARDINALITY = 729
KC27_CENTER = 14
ROSETTA_CENTER = 365

AUTHORITY_BOUNDARY = (
    "Coordinate equivalence, graph adjacency, exact arithmetic, source repetition, "
    "and local validation do not establish empirical truth, causal force, independent "
    "witness status, or promotion authority."
)

SOURCE_LINEAGE = (
    {
        "source_id": "GDRIVE.KC144.CMG.V19",
        "title": "ATHENA KC144 COMPLETE COORDINATE / MATHEMATICS / GRAPH SPECIFICATION 2",
        "locator": "gdrive:1KYmDH45AkQgh1U3igj-BjoH5UmWCFxNFOismYh1f3I4",
        "updated_at": "2026-08-08T07:37:04.018Z",
        "compiled_laws": ["UNKNOWN remains UNKNOWN", "typed 11/10/00/01 poles", "reachability is not proof"],
    },
    {
        "source_id": "GDRIVE.KC27.NESTED.RESOLUTION",
        "title": "KC144 / KC27 NESTED FRACTAL RESOLUTION CALCULUS",
        "locator": "gdrive:1DLn14aWr3RN9HWs8u2KSLgginYl8Xali6qPX8UcDvQE",
        "updated_at": "2026-08-08T07:38:35.780Z",
        "compiled_laws": ["KC27={0,1,2}^3", "14=111 is the mirror fixed point", "exact odd-3m transport"],
    },
    {
        "source_id": "GDRIVE.KC144.SPHERE",
        "title": "KC144 SPHERE COORDINATES",
        "locator": "gdrive:14dkdyS8eG1HWK8W658lfevWY3I-QdaK-NCf-TfyIzKo",
        "updated_at": "2026-08-08T07:44:04.011Z",
        "compiled_laws": ["144=12^2=27+117=6*3*8=4*36", "C01..C16 Rosetta", "project, do not duplicate"],
    },
)

DECOMPOSITIONS = (
    {"id": "D12_MATRIX", "law": "144=12*12", "shape": [12, 12]},
    {"id": "D27_117_SEMANTIC", "law": "144=27+117;117=13*9", "shape": [27, 117]},
    {"id": "D6_3_8_SPHERE", "law": "144=6*3*8", "shape": [6, 3, 8]},
    {"id": "D4_36_ELEMENT", "law": "144=4*36=4*(27+9)", "shape": [4, 36]},
)

ROSETTA_COORDINATES = tuple(
    {"id": f"C{index:02d}", "name": name}
    for index, name in enumerate(
        (
            "chapter ordinal", "chapter portal", "chapter ternary", "local shelf ordinal",
            "local shelf ternary", "six-trit holographic address", "GID729 flattened address",
            "balanced center", "Hamming graph", "radial shell", "mirror antipode",
            "KC144 host and Riemann sub-address", "KC54 conjugate", "KC108 four-element",
            "odd-times-three resolution operator", "tensor projective coordinate",
        ),
        1,
    )
)

FACE_FRAMES = (
    ("+X", (1, 0, 0), (0, 1, 0), (0, 0, 1)),
    ("-X", (-1, 0, 0), (0, -1, 0), (0, 0, 1)),
    ("+Y", (0, 1, 0), (-1, 0, 0), (0, 0, 1)),
    ("-Y", (0, -1, 0), (1, 0, 0), (0, 0, 1)),
    ("+Z", (0, 0, 1), (0, 1, 0), (-1, 0, 0)),
    ("-Z", (0, 0, -1), (0, 1, 0), (1, 0, 0)),
)

def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode()).hexdigest()


def bounded_int(name: str, value: Any, lower: int, upper: int) -> int:
    if isinstance(value, bool):
        raise TypeError(f"{name} must be an integer")
    try:
        result = int(value)
    except (TypeError, ValueError) as exc:
        raise TypeError(f"{name} must be an integer") from exc
    if result != value and not isinstance(value, str):
        raise TypeError(f"{name} must be an exact integer")
    if not lower <= result <= upper:
        raise ValueError(f"{name} must be in {lower}..{upper}")
    return result



def trits(index: int, width: int = 3) -> tuple[int, ...]:
    if not 0 <= index < 3**width:
        raise ValueError("ternary index outside chart")
    result = [0] * width
    for position in range(width - 1, -1, -1):
        result[position], index = index % 3, index // 3
    return tuple(result)


def from_trits(values: Iterable[int]) -> int:
    result = 0
    for value in values:
        if value not in (0, 1, 2):
            raise ValueError("ternary digits must belong to {0,1,2}")
        result = 3 * result + value
    return result


def kc27_address(chapter: int) -> dict[str, Any]:
    chapter = bounded_int("chapter", chapter, 1, 27)
    values = trits(chapter - 1)
    balanced = [value - 1 for value in values]
    neighbors = []
    for axis in range(3):
        for replacement in (0, 1, 2):
            if replacement != values[axis]:
                candidate = list(values); candidate[axis] = replacement
                neighbors.append(1 + from_trits(candidate))
    return {
        "chapter": chapter, "portal": chapter - 1, "ternary": "".join(map(str, values)),
        "trits": list(values), "balanced": balanced, "center_delta": chapter - 14,
        "mirror": 28 - chapter, "mirror_ternary": "".join(str(2 - value) for value in values),
        "shell": sum(value != 1 for value in values), "hamming_neighbors": sorted(neighbors),
        "charts": {"3x9": [values[0] + 1, 3 * values[1] + values[2] + 1],
                   "9x3": [3 * values[0] + values[1] + 1, values[2] + 1],
                   "direction": balanced},
        "fixed_point": chapter == 14,
    }


def kc27_from_ternary(value: str | Iterable[int]) -> int:
    values = tuple(map(int, value.strip())) if isinstance(value, str) else tuple(map(int, value))
    if len(values) != 3:
        raise ValueError("KC27 ternary address requires three trits")
    return 1 + from_trits(values)


def kc27_shell_census() -> dict[str, Any]:
    shells = {radius: [] for radius in range(4)}
    for chapter in range(1, 28):
        shells[kc27_address(chapter)["shell"]].append(chapter)
    return {"center": 14, "center_ternary": "111", "law": "1+6+12+8=27",
            "counts": {str(key): len(value) for key, value in shells.items()},
            "shells": {str(key): value for key, value in shells.items()}, "digest": digest(shells)}

def gid_decompositions(gid: int) -> dict[str, Any]:
    gid = bounded_int("gid", gid, 1, 144); zero = gid - 1
    row, column = divmod(zero, 12); face, local24 = divmod(zero, 24)
    phase, boundary = divmod(local24, 8); element, local36 = divmod(zero, 36)
    semantic = ({"kind": "KC27_ANCHOR", "anchor": gid, "ternary": kc27_address(gid)["ternary"]}
                if gid <= 27 else {"kind": "GRAPH117_RELATION", "relation": gid - 27,
                                   "row13": (gid - 28) // 9 + 1, "column9": (gid - 28) % 9 + 1})
    return {"gid": gid, "matrix_12x12": {"row": row + 1, "column": column + 1, "inverse": gid},
            "semantic_27_plus_117": semantic,
            "sphere_6x3x8": {"face_index": face, "face": FACE_FRAMES[face][0], "phase": phase,
                              "boundary": boundary, "inverse": 1 + 24 * face + 8 * phase + boundary},
            "element_4x36": {"element": element, "local": local36 + 1,
                              "role": "KC27_CORE" if local36 < 27 else "KC9_CLOSURE", "inverse": gid},
            "wheel": {"index": zero, "angle_degrees": 2.5 * zero}, "mirror_gid": 145 - gid}
