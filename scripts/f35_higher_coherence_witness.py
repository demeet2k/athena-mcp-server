from __future__ import annotations

import copy
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "spec" / "F35_HIGHER_COHERENCE_WITNESS_V1.json"
F37_SOURCE_PATH = ROOT / "spec" / "F37_LIBRARY_SOURCE_POPULATION_V1.json"
OUTPUT = Path("f35_higher_coherence_witness_v1.json")


def head() -> str:
    return subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()


@dataclass(frozen=True)
class Morphism:
    name: str
    src: str
    dst: str
    a: int
    b: int

    def apply(self, x: int) -> int:
        return self.a * x + self.b


@dataclass(frozen=True)
class PathSemantic:
    src: str
    dst: str
    a: int
    b: int

    def apply(self, x: int) -> int:
        return self.a * x + self.b

    def packet(self) -> dict:
        return {"src": self.src, "dst": self.dst, "affine": [self.a, self.b]}


def compose_affine(after: tuple[int, int], before: tuple[int, int]) -> tuple[int, int]:
    """Return after ∘ before for affine maps (a,b): x -> ax+b."""
    a2, b2 = after
    a1, b1 = before
    return a2 * a1, a2 * b1 + b2


def path_semantic(path: Iterable[str], morphisms: dict[str, Morphism]) -> PathSemantic:
    names = list(path)
    if not names:
        raise ValueError("empty path needs an explicit object identity and is not admitted here")
    first = morphisms[names[0]]
    src = first.src
    current = first.src
    affine = (1, 0)
    for name in names:
        m = morphisms[name]
        if m.src != current:
            raise ValueError(f"noncomposable path at {name}: expected source {current}, got {m.src}")
        affine = compose_affine((m.a, m.b), affine)
        current = m.dst
    return PathSemantic(src, current, affine[0], affine[1])


def two_cell_valid(source: list[str], target: list[str], morphisms: dict[str, Morphism]) -> tuple[bool, dict]:
    try:
        left = path_semantic(source, morphisms)
        right = path_semantic(target, morphisms)
    except (KeyError, ValueError) as exc:
        return False, {"reason": "TYPE_ERROR", "detail": str(exc)}
    same_boundary = left.src == right.src and left.dst == right.dst
    same_semantics = (left.a, left.b) == (right.a, right.b)
    return same_boundary and same_semantics, {
        "source": left.packet(),
        "target": right.packet(),
        "same_boundary": same_boundary,
        "same_semantics": same_semantics,
    }


def apply_rewrite(path: list[str], source: list[str], target: list[str]) -> list[str]:
    width = len(source)
    matches = [i for i in range(len(path) - width + 1) if path[i:i + width] == source]
    if len(matches) != 1:
        raise ValueError(f"rewrite source {source} must occur exactly once in path {path}; matches={matches}")
    i = matches[0]
    return path[:i] + target + path[i + width:]


def reduce_route(start: list[str], cells: list[str], cell_defs: dict[str, dict]) -> tuple[list[str], list[dict]]:
    path = list(start)
    trace = []
    for cell_name in cells:
        cell = cell_defs[cell_name]
        before = list(path)
        path = apply_rewrite(path, list(cell["source"]), list(cell["target"]))
        trace.append({"cell": cell_name, "before": before, "after": list(path)})
    return path, trace


def main() -> int:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    f37_source = json.loads(F37_SOURCE_PATH.read_text(encoding="utf-8"))
    fixture = contract["formal_fixture"]

    morphisms = {
        name: Morphism(name, data["src"], data["dst"], int(data["affine"][0]), int(data["affine"][1]))
        for name, data in fixture["one_morphisms"].items()
    }
    cell_defs = {name: dict(data) for name, data in fixture["two_morphisms"].items()}

    source_checks = {
        "f35_is_honesty_ledger_in_parent": "F35" in f37_source["source_status_partition"]["HONESTY_LEDGER_HOLD"],
        "gid078_hold_exact": f37_source["known_hold_by_gid"].get("78") == "HIGHER_COHERENCE_COMPOSITION_WITNESS",
        "math_source_hash_match": f37_source["source_roots"]["F37_MATH_LEDGER"]["sha256"] == contract["source_roots"]["math"]["sha256"],
        "symmetry_source_hash_match": f37_source["source_roots"]["F37_SYMMETRY_LEDGER"]["sha256"] == contract["source_roots"]["symmetry"]["sha256"],
    }

    object_checks = {
        "all_objects_exist": set(fixture["objects"]) == {m.src for m in morphisms.values()} | {m.dst for m in morphisms.values()},
        "all_one_morphisms_typecheck": True,
    }
    type_errors = []
    for name in morphisms:
        try:
            path_semantic([name], morphisms)
        except ValueError as exc:
            object_checks["all_one_morphisms_typecheck"] = False
            type_errors.append({"morphism": name, "error": str(exc)})

    two_cell_checks = {}
    two_cell_details = {}
    for name, cell in cell_defs.items():
        valid, detail = two_cell_valid(list(cell["source"]), list(cell["target"]), morphisms)
        two_cell_checks[name] = valid
        two_cell_details[name] = detail

    # Identity and associativity are checked at the exact affine-map level.
    identity = (1, 0)
    identity_checks = {}
    for name, m in morphisms.items():
        affine = (m.a, m.b)
        identity_checks[name] = (
            compose_affine(affine, identity) == affine
            and compose_affine(identity, affine) == affine
        )

    f = (morphisms["f"].a, morphisms["f"].b)
    g = (morphisms["g"].a, morphisms["g"].b)
    h = (morphisms["h"].a, morphisms["h"].b)
    assoc_left = compose_affine(h, compose_affine(g, f))
    assoc_right = compose_affine(compose_affine(h, g), f)

    diamond = fixture["coherence_diamond"]
    start = list(diamond["start"])
    left_path, left_trace = reduce_route(start, list(diamond["route_left"]), cell_defs)
    right_path, right_trace = reduce_route(start, list(diamond["route_right"]), cell_defs)
    target = list(diamond["canonical_target"])
    start_semantic = path_semantic(start, morphisms)
    left_semantic = path_semantic(left_path, morphisms)
    right_semantic = path_semantic(right_path, morphisms)
    target_semantic = path_semantic(target, morphisms)

    collapse_packets = {
        "start": start_semantic.packet(),
        "left": left_semantic.packet(),
        "right": right_semantic.packet(),
        "target": target_semantic.packet(),
    }
    coherence_checks = {
        "identity_laws": all(identity_checks.values()),
        "one_morphism_associativity": assoc_left == assoc_right,
        "left_route_reduces_to_target": left_path == target,
        "right_route_reduces_to_target": right_path == target,
        "coherence_diamond_commutes": left_semantic == right_semantic == target_semantic == start_semantic,
        "collapse_packet_equal": len({json.dumps(packet, sort_keys=True) for packet in collapse_packets.values()}) == 1,
    }

    # Explicit negative controls.
    nonparallel_valid, nonparallel_detail = two_cell_valid(["f"], ["u"], morphisms)
    mutated = copy.deepcopy(morphisms)
    w = mutated["w"]
    mutated["w"] = Morphism("w", w.src, w.dst, w.a, 0)  # break canonical higher transport
    gamma_bad, gamma_bad_detail = two_cell_valid(cell_defs["gamma"]["source"], cell_defs["gamma"]["target"], mutated)
    delta_bad, delta_bad_detail = two_cell_valid(cell_defs["delta"]["source"], cell_defs["delta"]["target"], mutated)
    broken_left_semantic = path_semantic(left_path, mutated)
    broken_right_semantic = path_semantic(right_path, mutated)
    broken_transport_detected = (
        not gamma_bad
        and not delta_bad
        and (broken_left_semantic != start_semantic or broken_right_semantic != start_semantic)
    )

    negative_checks = {
        "nonadmissible_two_morphism_rejected": not nonparallel_valid,
        "broken_higher_transport_detected": broken_transport_detected,
    }

    checks = {
        **source_checks,
        **object_checks,
        "all_two_morphisms_parallel_and_semantically_equal": all(two_cell_checks.values()),
        **coherence_checks,
        **negative_checks,
        "evidence_hold_preserved": contract["standing_after_pass"]["evidence"] == "HOLD",
        "promotion_authority_false": contract["standing_after_pass"]["promotion_authority"] is False,
    }
    ok = all(checks.values())

    receipt = {
        "artifact": contract["artifact"],
        "status": "F35_GENERIC_HIGHER_COHERENCE_WITNESS_PASS" if ok else "F35_GENERIC_HIGHER_COHERENCE_WITNESS_HOLD",
        "checkout_head": head(),
        "gid": 78,
        "carrier": "F35",
        "checks": checks,
        "type_errors": type_errors,
        "two_cell_details": two_cell_details,
        "identity_checks": identity_checks,
        "associativity": {"left": list(assoc_left), "right": list(assoc_right)},
        "coherence": {
            "start": start,
            "left_trace": left_trace,
            "right_trace": right_trace,
            "canonical_target": target,
            "collapse_packets": collapse_packets,
        },
        "negative_controls": {
            "nonparallel_two_cell": nonparallel_detail,
            "broken_gamma": gamma_bad_detail,
            "broken_delta": delta_bad_detail,
        },
        "standing_after_witness": contract["standing_after_pass"],
        "next_obligation": contract["standing_after_pass"]["remaining_obligation"],
        "evidence_ceiling": contract["firewalls"],
    }
    OUTPUT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
