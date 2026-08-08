from __future__ import annotations

"""Six-face gnomonic, spherical-volume, and Riemann projections."""

import math
from typing import Any
from .kc144_polyatlas_core import FACE_FRAMES, HOST_CARDINALITY, POLYATLAS_VERSION, bounded_int, digest, gid_decompositions


def _primitive(u: float, v: float) -> float:
    return math.atan2(u * v, math.sqrt(1 + u * u + v * v))


def _solid_angle(u0: float, u1: float, v0: float, v1: float) -> float:
    return _primitive(u1, v1) - _primitive(u0, v1) - _primitive(u1, v0) + _primitive(u0, v0)


def sphere_cell(gid: int, *, radius: float = 1.0) -> dict[str, Any]:
    gid = bounded_int("gid", gid, 1, HOST_CARDINALITY)
    radius = float(radius)
    if not math.isfinite(radius) or radius <= 0:
        raise ValueError("radius must be finite and positive")
    seat = gid_decompositions(gid)["sphere_6x3x8"]
    face, phase, boundary = seat["face_index"], seat["phase"], seat["boundary"]
    face_name, normal, e1, e2 = FACE_FRAMES[face]
    u0, u1 = -1 + 2 * boundary / 8, -1 + 2 * (boundary + 1) / 8
    v0, v1 = -1 + 2 * phase / 3, -1 + 2 * (phase + 1) / 3
    u, v = (u0 + u1) / 2, (v0 + v1) / 2
    q = tuple(normal[index] + u * e1[index] + v * e2[index] for index in range(3))
    norm = math.sqrt(sum(value * value for value in q))
    x, y, z = (radius * value / norm for value in q)
    omega = _solid_angle(u0, u1, v0, v1)
    denominator = radius - z
    riemann = ({"chart": "NORTH_INFINITY", "infinite": True, "real": None, "imag": None}
               if abs(denominator) <= 1e-15 else
               {"chart": "NORTH_STEREOGRAPHIC", "infinite": False,
                "real": x / denominator, "imag": y / denominator,
                "modulus": math.hypot(x / denominator, y / denominator)})
    return {"version": POLYATLAS_VERSION, "gid": gid, "face_index": face, "face": face_name,
            "phase": phase, "boundary": boundary,
            "face_frame": {"normal": list(normal), "e1": list(e1), "e2": list(e2)},
            "gnomonic_bounds": {"u0": u0, "u1": u1, "v0": v0, "v1": v1},
            "gnomonic_centroid": {"u": u, "v": v},
            "cartesian": {"x": x, "y": y, "z": z, "radius": radius},
            "spherical": {"theta_radians": math.atan2(y, x), "phi_radians": math.acos(max(-1, min(1, z / radius)))},
            "riemann": riemann, "solid_angle": omega, "surface_area": radius * radius * omega,
            "radial_wedge_volume": radius**3 * omega / 3,
            "portal_fibre": {"face": face_name, "phase": phase, "normal": list(normal),
                             "state": "RESERVED_KC162_PORTAL_NOT_ACTIVE_KC144_SEAT"}}


def sphere_atlas(*, offset: int = 0, limit: int = 144, radius: float = 1.0) -> dict[str, Any]:
    offset = bounded_int("offset", offset, 0, 143); limit = bounded_int("limit", limit, 1, 144)
    end = min(144, offset + limit)
    items = [sphere_cell(gid, radius=radius) for gid in range(offset + 1, end + 1)]
    return {"version": POLYATLAS_VERSION, "offset": offset, "returned": len(items),
            "next_offset": end if end < 144 else None, "radius": float(radius),
            "items": items, "digest": digest(items)}


def sphere_summary(*, radius: float = 1.0) -> dict[str, Any]:
    cells = [sphere_cell(gid, radius=radius) for gid in range(1, 145)]
    radius = float(radius)
    observed = {"solid_angle": math.fsum(item["solid_angle"] for item in cells),
                "surface_area": math.fsum(item["surface_area"] for item in cells),
                "wedge_volume": math.fsum(item["radial_wedge_volume"] for item in cells)}
    expected = {"solid_angle": 4 * math.pi, "surface_area": 4 * math.pi * radius**2,
                "wedge_volume": 4 * math.pi * radius**3 / 3}
    payload = {"version": POLYATLAS_VERSION, "cell_count": 144, "portal_count": 18,
               "factorization": "KC162=6*3*9 -> KC144=6*3*8 + 18 portals", "radius": radius,
               "observed": observed, "expected": expected,
               "errors": {key: abs(observed[key] - expected[key]) for key in expected},
               "landmarks": ["+1", "-1", "+i", "-i", "infinity", "0"]}
    payload["digest"] = digest(payload)
    return payload
