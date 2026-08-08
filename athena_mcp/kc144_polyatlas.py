from __future__ import annotations

"""Executable C01..C16 KC144/KC27 polyatlas and typed navigation layer."""

from collections import deque
from functools import lru_cache
from typing import Any, Iterable
from .kc144_polyatlas_core import (
    AUTHORITY_BOUNDARY, DECOMPOSITIONS, FACE_FRAMES, HOST_CARDINALITY, KC27_CENTER,
    POLYATLAS_VERSION, ROSETTA_CARDINALITY, ROSETTA_CENTER, ROSETTA_COORDINATES,
    SOURCE_LINEAGE, bounded_int, digest, gid_decompositions, kc27_address,
    kc27_from_ternary, kc27_shell_census, resolution_descriptor, resolution_family,
    resolution_transport, validate_resolution,
)
from .kc144_polyatlas_sphere import sphere_atlas, sphere_cell, sphere_summary

GRAPH_LAYERS = ("matrix", "wheel", "mirror", "sphere_face_grid", "sphere_proximity")


def rosetta_address(chapter: int, shelf: int, *, conjugate: int = 0, element: int = 0,
                    target_resolution: int = 21) -> dict[str, Any]:
    chapter = bounded_int("chapter", chapter, 1, 27); shelf = bounded_int("shelf", shelf, 1, 27)
    conjugate = bounded_int("conjugate", conjugate, 0, 1); element = bounded_int("element", element, 0, 3)
    target_resolution = validate_resolution("target_resolution", target_resolution)
    ca, sa = kc27_address(chapter), kc27_address(shelf)
    six = tuple(ca["trits"] + sa["trits"]); gid729 = 1 + 27 * (chapter - 1) + shelf - 1
    host_gid, fibre = 1 + (gid729 - 1) % 144, (gid729 - 1) // 144
    mirror_gid = 730 - gid729
    coordinates = {
        "C01": {"chapter": chapter}, "C02": {"chapter_portal": chapter - 1},
        "C03": {"chapter_ternary": ca["ternary"], "trits": ca["trits"]},
        "C04": {"shelf": shelf}, "C05": {"shelf_ternary": sa["ternary"], "trits": sa["trits"]},
        "C06": {"six_trit": "".join(map(str, six)), "trits": list(six)},
        "C07": {"gid729": gid729, "inverse": {"chapter": 1 + (gid729 - 1) // 27, "shelf": 1 + (gid729 - 1) % 27}},
        "C08": {"balanced": [value - 1 for value in six], "delta_from_gid365": gid729 - 365},
        "C09": {"graph": "H(6,3)", "hamming_radius_from_111111": sum(value != 1 for value in six), "local_degree": 12},
        "C10": {"chapter_shell": ca["shell"], "shelf_shell": sa["shell"],
                 "combined_shell": sum(value != 1 for value in six), "capacity_law": "[x^r](1+2x)^6"},
        "C11": {"mirror_chapter": 28 - chapter, "mirror_shelf": 28 - shelf,
                 "mirror_gid729": mirror_gid, "involution": 730 - mirror_gid == gid729},
        "C12": {"host_gid": host_gid, "fibre_index": fibre,
                 "serialization_projection": "GID729-1=144*fibre+(host_gid-1)",
                 "reconstructed_gid729": 1 + 144 * fibre + host_gid - 1,
                 "bijective_only_as_pair": True, "decompositions": gid_decompositions(host_gid),
                 "riemann": sphere_cell(host_gid)["riemann"]},
        "C13": {"kc54_gid": 1 + 2 * (shelf - 1) + conjugate, "shelf": shelf, "conjugate": conjugate},
        "C14": {"kc108_gid": 1 + 4 * (shelf - 1) + element, "shelf": shelf, "element": element},
        "C15": resolution_transport(27, target_resolution, chapter),
        "C16": {"basis": [chapter - 1, shelf - 1], "tensor_index": gid729,
                 "rank_one_symbol": f"e_{chapter - 1} tensor e_{shelf - 1}"},
    }
    payload = {"version": POLYATLAS_VERSION, "canonical_locus": {"chapter": chapter, "shelf": shelf},
               "coordinates": coordinates, "coordinate_order": [item["id"] for item in ROSETTA_COORDINATES],
               "roundtrip": {"chapter": kc27_from_ternary(ca["ternary"]) == chapter,
                             "shelf": kc27_from_ternary(sa["ternary"]) == shelf,
                             "gid729": coordinates["C12"]["reconstructed_gid729"] == gid729,
                             "mirror": 730 - mirror_gid == gid729},
               "projection_law": "PROJECT_DO_NOT_DUPLICATE", "authority_boundary": AUTHORITY_BOUNDARY}
    payload["digest"] = digest(payload); return payload


def rosetta_from_gid729(gid729: int, **kwargs: Any) -> dict[str, Any]:
    gid729 = bounded_int("gid729", gid729, 1, 729)
    return rosetta_address(1 + (gid729 - 1) // 27, 1 + (gid729 - 1) % 27, **kwargs)


def _matrix(gid: int) -> set[int]:
    row, column = divmod(gid - 1, 12); result = set()
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        if 0 <= row + dr < 12 and 0 <= column + dc < 12:
            result.add(1 + 12 * (row + dr) + column + dc)
    return result


def _face_grid(gid: int) -> set[int]:
    seat = gid_decompositions(gid)["sphere_6x3x8"]; face, phase, boundary = seat["face_index"], seat["phase"], seat["boundary"]
    result = set()
    for dp, db in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        if 0 <= phase + dp < 3 and 0 <= boundary + db < 8:
            result.add(1 + 24 * face + 8 * (phase + dp) + boundary + db)
    return result


@lru_cache(maxsize=1)
def _proximity_edges() -> frozenset[tuple[int, int]]:
    vectors = {gid: tuple(sphere_cell(gid)["cartesian"][axis] for axis in ("x", "y", "z")) for gid in range(1, 145)}
    edges = set()
    for gid, vector in vectors.items():
        nearest = sorted((other for other in vectors if other != gid),
                         key=lambda other: (-sum(vector[i] * vectors[other][i] for i in range(3)), other))[:4]
        edges.update(tuple(sorted((gid, other))) for other in nearest)
    return frozenset(edges)


def graph_neighbors(gid: int, layer: str) -> set[int]:
    gid = bounded_int("gid", gid, 1, 144)
    if layer == "matrix": return _matrix(gid)
    if layer == "wheel": return {1 + ((gid - 2) % 144), 1 + (gid % 144)}
    if layer == "mirror": return {145 - gid}
    if layer == "sphere_face_grid": return _face_grid(gid)
    if layer == "sphere_proximity":
        return {right if left == gid else left for left, right in _proximity_edges() if gid in (left, right)}
    raise KeyError(f"unknown graph layer: {layer}")


def polyatlas_route(src: int, dst: int, *, layers: Iterable[str] | None = None) -> dict[str, Any]:
    src = bounded_int("src", src, 1, 144); dst = bounded_int("dst", dst, 1, 144)
    selected = tuple(dict.fromkeys(layers or ("matrix",)))
    unknown = sorted(set(selected) - set(GRAPH_LAYERS))
    if not selected: raise ValueError("at least one graph layer is required")
    if unknown: raise KeyError(f"unknown graph layers: {unknown}")
    predecessor: dict[int, int | None] = {src: None}; queue = deque([src])
    while queue and dst not in predecessor:
        current = queue.popleft(); neighbors = set()
        for layer in selected: neighbors.update(graph_neighbors(current, layer))
        for neighbor in sorted(neighbors):
            if neighbor not in predecessor: predecessor[neighbor] = current; queue.append(neighbor)
    if dst not in predecessor:
        return {"version": POLYATLAS_VERSION, "src": src, "dst": dst, "layers": list(selected),
                "found": False, "path": [], "edges": [], "semantic_boundary": "selected-layer absence is not global impossibility"}
    path = [dst]
    while path[-1] != src: path.append(predecessor[path[-1]])
    path.reverse()
    edges = [{"src": left, "dst": right, "layers": [layer for layer in selected if right in graph_neighbors(left, layer)]}
             for left, right in zip(path, path[1:])]
    payload = {"version": POLYATLAS_VERSION, "src": src, "dst": dst, "layers": list(selected),
               "found": True, "path": path, "hop_count": len(path) - 1, "edges": edges,
               "routing_law": "deterministic BFS over selected typed layers",
               "semantic_boundary": "route existence is navigation, not proof or authority"}
    payload["digest"] = digest(payload); return payload


def sources() -> dict[str, Any]:
    items = [dict(item) for item in SOURCE_LINEAGE]
    return {"version": POLYATLAS_VERSION, "items": items, "count": len(items),
            "authority_boundary": AUTHORITY_BOUNDARY, "digest": digest(items)}


def manifest() -> dict[str, Any]:
    payload = {"version": POLYATLAS_VERSION, "host": "KC144", "host_cardinality": 144,
               "rosetta_cardinality": 729, "decompositions": [dict(item) for item in DECOMPOSITIONS],
               "coordinate_systems": [dict(item) for item in ROSETTA_COORDINATES], "coordinate_count": 16,
               "graph_layers": list(GRAPH_LAYERS), "kc27_shells": kc27_shell_census(),
               "resolution_family": {"law": "N=3m,m odd", "resolution_step": 6, "center_step": 3},
               "sphere": sphere_summary(), "sources": sources(), "projection_law": "PROJECT_DO_NOT_DUPLICATE",
               "authority_boundary": AUTHORITY_BOUNDARY, "promotion_ready": False}
    payload["digest"] = digest(payload); return payload


def status() -> dict[str, Any]:
    return {"version": POLYATLAS_VERSION, "state": "EXECUTABLE_SOURCE_BOUND_PROJECTION_LAYER",
            "host_cardinality": 144, "coordinate_count": 16, "decomposition_count": 4,
            "graph_layer_count": len(GRAPH_LAYERS), "source_count": len(SOURCE_LINEAGE),
            "sphere_cell_count": 144, "rosetta_locus_count": 729, "authority_boundary": AUTHORITY_BOUNDARY}


def validate(*, include_details: bool = True) -> dict[str, Any]:
    checks = []
    def check(name: str, observed: Any, expected: Any, detail: Any = None) -> None:
        item = {"name": name, "status": "PASS" if observed == expected else "FAIL", "observed": observed, "expected": expected}
        if include_details and detail is not None: item["detail"] = detail
        checks.append(item)
    gids = set(range(1, 145))
    check("matrix_12x12_bijection", {gid_decompositions(g)["matrix_12x12"]["inverse"] for g in gids} == gids, True)
    check("sphere_6x3x8_bijection", {gid_decompositions(g)["sphere_6x3x8"]["inverse"] for g in gids} == gids, True)
    check("element_4x36_bijection", {gid_decompositions(g)["element_4x36"]["inverse"] for g in gids} == gids, True)
    check("semantic_partition", sum(g <= 27 for g in gids), 27); check("relation_partition", sum(g > 27 for g in gids), 117)
    check("mirror_involution", all(145 - (145 - g) == g for g in gids), True)
    check("kc27_shell_census", kc27_shell_census()["counts"], {"0": 1, "1": 6, "2": 12, "3": 8})
    check("kc27_roundtrip", all(kc27_from_ternary(kc27_address(c)["ternary"]) == c for c in range(1, 28)), True)
    check("kc27_center_fixed", kc27_address(14)["mirror"], 14)
    loci = {1 + 27 * (c - 1) + s - 1 for c in range(1, 28) for s in range(1, 28)}
    check("rosetta_729_census", len(loci), 729)
    check("rosetta_host_fibre_roundtrip", all(1 + ((g - 1) // 144) * 144 + (1 + (g - 1) % 144) - 1 == g for g in loci), True)
    check("rosetta_center", rosetta_address(14, 14)["coordinates"]["C07"]["gid729"], 365)
    sphere = sphere_summary(); tolerance = 1e-12
    for key in ("solid_angle", "surface_area", "wedge_volume"):
        check(f"sphere_{key}", sphere["errors"][key] <= tolerance, True, sphere["errors"][key])
    transport_ok = all(all(resolution_transport(a, b, station)["invariants"].values())
                       for a, b in ((3, 27), (21, 27), (27, 33), (27, 39), (39, 21))
                       for station in (1, (a + 1) // 2, a))
    check("resolution_transport_invariants", transport_ok, True)
    route = polyatlas_route(1, 144, layers=("matrix", "mirror"))
    check("typed_route_reaches_return", route["found"], True); check("typed_route_endpoints", (route["path"][0], route["path"][-1]), (1, 144))
    result = {"version": POLYATLAS_VERSION, "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL",
              "check_count": len(checks), "pass_count": sum(item["status"] == "PASS" for item in checks),
              "fail_count": sum(item["status"] == "FAIL" for item in checks),
              "checks": checks if include_details else [{"name": item["name"], "status": item["status"]} for item in checks],
              "authority_boundary": AUTHORITY_BOUNDARY}
    result["digest"] = digest(result); return result

__all__ = ["GRAPH_LAYERS", "POLYATLAS_VERSION", "gid_decompositions", "kc27_address", "kc27_from_ternary",
           "kc27_shell_census", "manifest", "polyatlas_route", "resolution_descriptor", "resolution_family",
           "resolution_transport", "rosetta_address", "rosetta_from_gid729", "sources", "sphere_atlas",
           "sphere_cell", "sphere_summary", "status", "validate"]
