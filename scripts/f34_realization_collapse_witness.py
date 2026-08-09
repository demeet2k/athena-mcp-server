from __future__ import annotations

import copy
import json
import math
import subprocess
from itertools import permutations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "spec" / "F34_MOTIVIC_ENVELOPE_WITNESS_V1.json"
F37_SOURCE_PATH = ROOT / "spec" / "F37_LIBRARY_SOURCE_POPULATION_V1.json"
OUTPUT = Path("f34_realization_collapse_witness_v1.json")


def head() -> str:
    return subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()


def invariants(values: list[int]) -> dict:
    return {
        "rank": len(values),
        "parity": sum(values) % 2,
        "weight": sum(values),
        "product": math.prod(values),
    }


def decode(realization: dict) -> list[int]:
    kind = realization["kind"]
    value = realization["value"]
    if kind == "VECTOR":
        return [int(x) for x in value]
    if kind == "POLYNOMIAL":
        return [int(value[key]) for key in ("x2", "x1", "x0")]
    if kind == "PRIME_MAP":
        out = []
        for prime in sorted((int(k) for k in value), key=int):
            out.extend([prime] * int(value[str(prime)]))
        return out
    raise ValueError(f"unsupported realization kind {kind}")


def encode(kind: str, values: list[int]) -> dict:
    if kind == "VECTOR":
        return {"kind": kind, "value": list(values)}
    if kind == "POLYNOMIAL":
        if len(values) != 3:
            raise ValueError("polynomial fixture expects exactly three coefficients")
        return {"kind": kind, "value": {"x2": values[0], "x1": values[1], "x0": values[2]}}
    if kind == "PRIME_MAP":
        counts = {}
        for value in values:
            if value < 2:
                raise ValueError("prime-map fixture admits integers >=2 only")
            counts[str(value)] = counts.get(str(value), 0) + 1
        return {"kind": kind, "value": counts}
    raise ValueError(f"unsupported realization kind {kind}")


def compare_map(source: dict, target_kind: str) -> dict:
    values = decode(source)
    encoded = encode(target_kind, values)
    return {
        "source_kind": source["kind"],
        "target_kind": target_kind,
        "encoded": encoded,
        "roundtrip_values": decode(encoded),
        "exact": decode(encoded) == values,
    }


def collapse(realization: dict, standing: str) -> dict:
    values = decode(realization)
    return {
        "carrier": "F34_GENERIC_ENVELOPE_FIXTURE",
        "standing": standing,
        "values": values,
        "invariants": invariants(values),
    }


def main() -> int:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    f37 = json.loads(F37_SOURCE_PATH.read_text(encoding="utf-8"))
    fixture = contract["formal_fixture"]
    seed = fixture["seed_packet"]
    realizations = fixture["realizations"]
    canonical_envelope = fixture["canonical_envelope"]

    source_checks = {
        "f34_parent_hold_present": f37["known_hold_by_gid"].get("77") == "MOTIVIC_COMPARISON_DEBT",
        "f34_is_honesty_ledger": "F34" in f37["source_status_partition"]["HONESTY_LEDGER_HOLD"],
        "math_source_hash_match": f37["source_roots"]["F37_MATH_LEDGER"]["sha256"] == contract["source_roots"]["math"]["sha256"],
        "symmetry_source_hash_match": f37["source_roots"]["F37_SYMMETRY_LEDGER"]["sha256"] == contract["source_roots"]["symmetry"]["sha256"],
    }

    decoded = {name: decode(realization) for name, realization in realizations.items()}
    decoded_packets = {tuple(values) for values in decoded.values()}
    realization_checks = {
        "seed_invariants_recompute": invariants(list(seed["values"])) == seed["invariants"],
        "all_realizations_decode_to_same_seed": len(decoded_packets) == 1 and next(iter(decoded_packets)) == tuple(seed["values"]),
    }

    comparisons = {}
    exact_comparisons = True
    names = sorted(realizations)
    for source_name in names:
        for target_name in names:
            if source_name == target_name:
                continue
            result = compare_map(realizations[source_name], realizations[target_name]["kind"])
            comparisons[f"{source_name}->{target_name}"] = result
            exact_comparisons = exact_comparisons and result["exact"] and result["roundtrip_values"] == seed["values"]

    # The triangle commutes if every route through any intermediate realization
    # has the same canonical decoded packet as the direct comparison.
    triangle_results = []
    triangle_commutes = True
    for a, b, c in permutations(names, 3):
        direct = decode(compare_map(realizations[a], realizations[c]["kind"])["encoded"])
        via_b_enc = compare_map(realizations[a], realizations[b]["kind"])["encoded"]
        via_b = decode(compare_map(via_b_enc, realizations[c]["kind"])["encoded"])
        equal = direct == via_b == seed["values"]
        triangle_results.append({"route": [a, b, c], "direct": direct, "via": via_b, "equal": equal})
        triangle_commutes = triangle_commutes and equal

    collapses = {
        name: collapse(realization, canonical_envelope["standing"])
        for name, realization in realizations.items()
    }
    collapse_invariants = {json.dumps(packet["invariants"], sort_keys=True) for packet in collapses.values()}
    collapse_values = {tuple(packet["values"]) for packet in collapses.values()}
    collapse_checks = {
        "all_comparison_maps_exact_and_bidirectional": exact_comparisons,
        "comparison_triangle_commutes": triangle_commutes,
        "collapse_returns_same_canonical_envelope_from_each_realization": (
            len(collapse_invariants) == 1
            and next(iter(collapse_invariants)) == json.dumps(canonical_envelope["invariants"], sort_keys=True)
        ),
        "roundtrip_realization_collapse_reconstructs_seed": len(collapse_values) == 1 and next(iter(collapse_values)) == tuple(seed["values"]),
    }

    # Negative control A: realization mismatch.
    tampered_realization = copy.deepcopy(realizations["R_polynomial"])
    tampered_realization["value"]["x0"] = 7
    tampered_values = decode(tampered_realization)
    tampered_detected = tampered_values != seed["values"] and invariants(tampered_values) != seed["invariants"]

    # Negative control B: corrupt one comparison map by reversing the translated seed.
    bad_comparison = encode(realizations["R_vector"]["kind"], list(reversed(seed["values"])))
    bad_comparison_detected = decode(bad_comparison) != seed["values"]

    # Negative control C: a collapse that omits an invariant is not the canonical envelope.
    lossy_collapse = copy.deepcopy(collapses["R_vector"])
    lossy_collapse["invariants"].pop("product")
    lossy_detected = lossy_collapse["invariants"] != canonical_envelope["invariants"]

    negative_checks = {
        "tampered_realization_is_detected": tampered_detected,
        "tampered_comparison_map_is_detected": bad_comparison_detected,
        "lossy_collapse_is_detected": lossy_detected,
    }

    checks = {
        **source_checks,
        **realization_checks,
        **collapse_checks,
        **negative_checks,
        "fixture_not_upgraded_to_motivic_theorem": canonical_envelope["standing"] == "FORMAL_REALIZATION_FIXTURE_NOT_MOTIVIC_THEOREM",
        "f34_evidence_hold_preserved": contract["standing_after_pass"]["evidence"] == "HOLD",
        "promotion_authority_false": contract["standing_after_pass"]["promotion_authority"] is False,
    }
    ok = all(checks.values())

    receipt = {
        "artifact": contract["artifact"],
        "status": "F34_GENERIC_REALIZATION_COLLAPSE_WITNESS_PASS" if ok else "F34_GENERIC_REALIZATION_COLLAPSE_WITNESS_HOLD",
        "checkout_head": head(),
        "gid": 77,
        "carrier": "F34",
        "checks": checks,
        "decoded_realizations": decoded,
        "comparison_maps": comparisons,
        "comparison_triangles": triangle_results,
        "collapse_packets": collapses,
        "negative_controls": {
            "tampered_realization": {"values": tampered_values, "detected": tampered_detected},
            "tampered_comparison": {"encoded": bad_comparison, "detected": bad_comparison_detected},
            "lossy_collapse": {"packet": lossy_collapse, "detected": lossy_detected},
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
