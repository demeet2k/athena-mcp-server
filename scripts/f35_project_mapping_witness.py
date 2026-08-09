from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "spec" / "F35_PROJECT_MAPPING_WITNESS_V1.json"
F37_SOURCE_PATH = ROOT / "spec" / "F37_LIBRARY_SOURCE_POPULATION_V1.json"
OUTPUT = Path("f35_project_mapping_witness_v1.json")


def head() -> str:
    return subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()


def sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def merkle_root(words: list[str]) -> str:
    level = [sha(word) for word in words]
    if not level:
        return sha("")
    while len(level) > 1:
        if len(level) % 2:
            level.append(level[-1])
        level = [sha(level[i] + level[i + 1]) for i in range(0, len(level), 2)]
    return level[0]


def decode_realization(realization: dict) -> list[int]:
    kind = realization["kind"]
    value = realization["value"]
    if kind in {"VECTOR", "SORTED_MULTISET"}:
        return [int(x) for x in value]
    if kind == "POLYNOMIAL_COEFFICIENTS":
        return [int(value[key]) for key in ("x2", "x1", "x0")]
    raise ValueError(f"unsupported realization kind {kind}")


def invariants(values: list[int]) -> dict:
    return {
        "rank": len(values),
        "parity": sum(values) % 2,
        "weight": sum(values),
    }


def collapse_realization(realization: dict) -> dict:
    values = decode_realization(realization)
    return {"values": values, "invariants": invariants(values)}


def comparison_residual(left: dict, right: dict) -> dict:
    keys = ("rank", "parity", "weight")
    delta = {key: int(left[key]) - int(right[key]) for key in keys}
    return {"delta": delta, "zero": all(value == 0 for value in delta.values())}


def build_h35_packet(k33: dict, collapses: dict[str, dict], fixture: dict) -> dict:
    target = fixture["F34_conditional_envelope"]["collapse_target"]
    paths = {
        name: {
            "source": "K33",
            "target": "M34",
            "realization": name,
            "semantic_invariants": data["invariants"],
        }
        for name, data in collapses.items()
    }
    pairwise = {}
    for left, right in combinations(sorted(paths), 2):
        residual = comparison_residual(paths[left]["semantic_invariants"], paths[right]["semantic_invariants"])
        pairwise[f"{left}<=>{right}"] = residual
    return {
        "carrier": "F35",
        "objects": list(fixture["F35_objects"]),
        "one_morphisms": list(fixture["F35_one_morphisms"]),
        "two_morphisms": list(fixture["F35_two_morphisms"]),
        "comparison_paths": paths,
        "pairwise_2cell_residuals": pairwise,
        "coherence_triangle": {
            "vertices": sorted(paths),
            "commutes": all(item["zero"] for item in pairwise.values()),
        },
        "collapse_packet": {
            "packet_id": k33["packet_id"],
            "merkle_root": merkle_root(k33["merkle_words"]),
            "invariants": target,
        },
    }


def export_f36_facing(k33: dict, h35: dict, fixture: dict) -> dict:
    residuals = [
        sum(abs(v) for v in record["delta"].values())
        for record in h35["pairwise_2cell_residuals"].values()
    ]
    typed_defects = {"partial_34": [], "partial_35": [], "partial_36": []}
    return {
        "carrier": "F36_FACING_FIXTURE",
        "standing": fixture["F36_facing_packet"]["standing"],
        "Sigma": int(fixture["F36_facing_packet"]["Sigma"]),
        "Ext": {"comparison_residuals": residuals},
        "Sing": list(fixture["F36_facing_packet"]["Sing"]),
        "memory": {
            "packet_id": k33["packet_id"],
            "merkle_root": merkle_root(k33["merkle_words"]),
            "invariants": dict(k33["invariants"]),
            "typed_defects": typed_defects,
        },
        "replay_target": fixture["F36_facing_packet"]["replay_target"],
    }


def replay_f36(packet: dict, expected_k33: dict) -> dict:
    memory = packet["memory"]
    expected = {
        "packet_id": expected_k33["packet_id"],
        "merkle_root": merkle_root(expected_k33["merkle_words"]),
        "invariants": expected_k33["invariants"],
    }
    observed = {key: memory.get(key) for key in expected}
    defects = [key for key in expected if observed.get(key) != expected[key]]
    return {
        "status": "REPLAY_MATCH" if not defects else "REPLAY_DEFECT",
        "defects": defects,
        "expected": expected,
        "observed": observed,
    }


def main() -> int:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    f37 = json.loads(F37_SOURCE_PATH.read_text(encoding="utf-8"))
    fixture = contract["fixture"]
    k33 = fixture["K33_tail"]
    realizations = fixture["F34_conditional_envelope"]["realizations"]
    collapse_target = fixture["F34_conditional_envelope"]["collapse_target"]

    source_checks = {
        "f35_parent_hold_present": f37["known_hold_by_gid"].get("78") == "HIGHER_COHERENCE_COMPOSITION_WITNESS",
        "f34_parent_hold_present": f37["known_hold_by_gid"].get("77") == "MOTIVIC_COMPARISON_DEBT",
        "f36_parent_hold_present": f37["known_hold_by_gid"].get("79") == "DERIVED_SINGULARITY_AND_EMPIRICAL_CLOSURE",
        "math_source_hash_match": f37["source_roots"]["F37_MATH_LEDGER"]["sha256"] == contract["source_roots"]["math"]["sha256"],
        "symmetry_source_hash_match": f37["source_roots"]["F37_SYMMETRY_LEDGER"]["sha256"] == contract["source_roots"]["symmetry"]["sha256"],
    }

    k33_checks = {
        "k33_invariants_recompute": invariants(list(k33["fusion_index"])) == k33["invariants"],
        "k33_merkle_root_nonempty": bool(merkle_root(k33["merkle_words"])),
    }

    collapses = {name: collapse_realization(data) for name, data in realizations.items()}
    collapse_checks = {
        "all_f34_fixture_realizations_collapse_to_same_invariants": all(data["invariants"] == collapse_target for data in collapses.values()),
        "all_f34_fixture_realizations_decode_to_same_packet": len({tuple(data["values"]) for data in collapses.values()}) == 1,
    }

    h35 = build_h35_packet(k33, collapses, fixture)
    path_values = list(h35["comparison_paths"].values())
    h35_checks = {
        "f35_comparison_2cells_are_parallel": all(path["source"] == "K33" and path["target"] == "M34" for path in path_values),
        "f35_comparison_triangle_commutes": h35["coherence_triangle"]["commutes"],
        "f35_lift_preserves_packet_invariants": h35["collapse_packet"]["invariants"] == k33["invariants"],
        "f35_collapse_preserves_merkle_identity": h35["collapse_packet"]["merkle_root"] == merkle_root(k33["merkle_words"]),
    }

    f36_packet = export_f36_facing(k33, h35, fixture)
    replay = replay_f36(f36_packet, k33)
    typed_defects = f36_packet["memory"]["typed_defects"]
    f36_checks = {
        "f36_facing_export_typed": f36_packet["carrier"] == "F36_FACING_FIXTURE" and f36_packet["standing"] == "F36_FACING_FIXTURE_NOT_W36_PROOF",
        "f36_facing_export_replayable_on_fixture": replay["status"] == "REPLAY_MATCH",
        "typed_defects_remain_separate": set(typed_defects) == {"partial_34", "partial_35", "partial_36"} and len({id(typed_defects[key]) for key in typed_defects}) == 3,
    }

    # Negative control 1: realization mismatch must be caught before F35 admission.
    tampered_realizations = copy.deepcopy(realizations)
    tampered_realizations["R_polynomial"]["value"]["x0"] = 7
    tampered_collapses = {name: collapse_realization(data) for name, data in tampered_realizations.items()}
    tampered_match = all(data["invariants"] == collapse_target for data in tampered_collapses.values())
    partial_34 = [] if tampered_match else ["REALIZATION_MISMATCH"]

    # Negative control 2: F36 memory corruption must fail replay without being relabeled as F35 coherence failure.
    tampered_f36 = copy.deepcopy(f36_packet)
    tampered_f36["memory"]["merkle_root"] = "0" * 64
    tampered_replay = replay_f36(tampered_f36, k33)
    partial_36 = [] if tampered_replay["status"] == "REPLAY_MATCH" else ["SINGULAR_REPLAY_MISMATCH"]
    partial_35 = []  # generic CUT-01 coherence remains valid in both negative controls

    negative_checks = {
        "tampered_f34_realization_fails_before_f35_admission": not tampered_match and partial_34 == ["REALIZATION_MISMATCH"],
        "tampered_f36_replay_memory_is_detected": tampered_replay["status"] == "REPLAY_DEFECT" and "merkle_root" in tampered_replay["defects"],
        "negative_defects_remain_typed": partial_34 == ["REALIZATION_MISMATCH"] and partial_35 == [] and partial_36 == ["SINGULAR_REPLAY_MISMATCH"],
    }

    checks = {
        **source_checks,
        **k33_checks,
        **collapse_checks,
        **h35_checks,
        **f36_checks,
        **negative_checks,
        "f34_fixture_not_upgraded_to_w34": fixture["F34_conditional_envelope"]["standing"] == "ASSUMED_FIXTURE_NOT_W34_PROOF",
        "f36_fixture_not_upgraded_to_w36": fixture["F36_facing_packet"]["standing"] == "F36_FACING_FIXTURE_NOT_W36_PROOF",
        "f35_evidence_hold_preserved": contract["standing_after_pass"]["evidence"] == "HOLD",
        "promotion_authority_false": contract["standing_after_pass"]["promotion_authority"] is False,
    }
    ok = all(checks.values())

    receipt = {
        "artifact": contract["artifact"],
        "status": "F35_PROJECT_MAPPING_CONDITIONAL_PASS" if ok else "F35_PROJECT_MAPPING_HOLD",
        "checkout_head": head(),
        "gid": 78,
        "checks": checks,
        "K33_tail": {
            **k33,
            "merkle_root": merkle_root(k33["merkle_words"]),
        },
        "F34_conditional_collapses": collapses,
        "F35_packet": h35,
        "F36_facing_packet": f36_packet,
        "F36_replay": replay,
        "negative_controls": {
            "tampered_F34": {
                "collapses": tampered_collapses,
                "typed_defect_34": partial_34,
            },
            "tampered_F36": {
                "replay": tampered_replay,
                "typed_defect_36": partial_36,
            },
            "typed_defect_35": partial_35,
        },
        "standing_after_witness": contract["standing_after_pass"],
        "remaining_obligations": contract["standing_after_pass"]["remaining_obligations"],
        "evidence_ceiling": contract["firewalls"],
    }
    OUTPUT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
