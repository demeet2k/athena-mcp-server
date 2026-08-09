from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "spec" / "F36_DERIVED_REPLAY_WITNESS_V1.json"
F37_SOURCE_PATH = ROOT / "spec" / "F37_LIBRARY_SOURCE_POPULATION_V1.json"
OUTPUT = Path("f36_derived_replay_witness_v1.json")


def head() -> str:
    return subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha(value: object) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def matmul(a: list[list[int]], b: list[list[int]]) -> list[list[int]]:
    if not a or not b or len(a[0]) != len(b):
        raise ValueError("matrix dimension mismatch")
    return [[sum(a[i][k] * b[k][j] for k in range(len(b))) for j in range(len(b[0]))] for i in range(len(a))]


def matrix_rank(matrix: list[list[int]]) -> int:
    a = [[Fraction(x) for x in row] for row in matrix]
    rows = len(a)
    cols = len(a[0]) if rows else 0
    rank = 0
    col = 0
    while rank < rows and col < cols:
        pivot = next((r for r in range(rank, rows) if a[r][col] != 0), None)
        if pivot is None:
            col += 1
            continue
        a[rank], a[pivot] = a[pivot], a[rank]
        pv = a[rank][col]
        a[rank] = [x / pv for x in a[rank]]
        for r in range(rows):
            if r == rank or a[r][col] == 0:
                continue
            factor = a[r][col]
            a[r] = [x - factor * y for x, y in zip(a[r], a[rank])]
        rank += 1
        col += 1
    return rank


def derived_packet(fixture: dict) -> dict:
    cc = fixture["chain_complex"]
    d2 = cc["d2"]
    d1 = cc["d1"]
    composition = matmul(d1, d2)
    zero = all(value == 0 for row in composition for value in row)
    r2 = matrix_rank(d2)
    r1 = matrix_rank(d1)
    homology = {
        "H2": int(cc["C2_dim"]) - r2,
        "H1": int(cc["C1_dim"]) - r2 - r1,
        "H0": int(cc["C0_dim"]) - r1,
    }
    singularities = []
    if not zero:
        singularities.append({"type": "CHAIN_CONDITION_DEFECT", "composition": composition})
    if any(value < 0 for value in homology.values()):
        singularities.append({"type": "NEGATIVE_HOMOLOGY_DIMENSION", "homology": homology})
    memory = {
        "packet_id": fixture["packet_id"],
        "state": list(fixture["state"]),
        "lineage": list(fixture["lineage"]),
        "chain_digest": sha(cc),
        "derived": {"rank_d2": r2, "rank_d1": r1, "homology_dimensions": homology},
    }
    return {
        "carrier": "F36_FORMAL_REPLAY_FIXTURE",
        "D": {"chain_complex": cc, "derived": memory["derived"]},
        "Sigma": 0 if zero else 1,
        "Ext": {
            "standing": "FORMAL_EXT_LIKE_RESIDUAL_NOT_EXT_FUNCTOR",
            "residuals": [sum(abs(x) for row in composition for x in row)],
        },
        "Sing": singularities,
        "memory": memory,
    }


def replay(packet: dict, fixture: dict) -> dict:
    expected = {
        "packet_id": fixture["packet_id"],
        "state": fixture["state"],
        "lineage": fixture["lineage"],
        "chain_digest": sha(fixture["chain_complex"]),
    }
    observed = {key: packet["memory"].get(key) for key in expected}
    defects = [key for key in expected if observed.get(key) != expected[key]]
    return {"status": "REPLAY_MATCH" if not defects else "REPLAY_DEFECT", "defects": defects, "expected": expected, "observed": observed}


def main() -> int:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    f37 = json.loads(F37_SOURCE_PATH.read_text(encoding="utf-8"))
    fixture = contract["formal_fixture"]
    expected = fixture["expected"]

    source_checks = {
        "f36_parent_hold_present": f37["known_hold_by_gid"].get("79") == "DERIVED_SINGULARITY_AND_EMPIRICAL_CLOSURE",
        "f36_is_honesty_ledger": "F36" in f37["source_status_partition"]["HONESTY_LEDGER_HOLD"],
        "math_source_hash_match": f37["source_roots"]["F37_MATH_LEDGER"]["sha256"] == contract["source_roots"]["math"]["sha256"],
        "symmetry_source_hash_match": f37["source_roots"]["F37_SYMMETRY_LEDGER"]["sha256"] == contract["source_roots"]["symmetry"]["sha256"],
    }

    packet = derived_packet(fixture)
    observed = packet["D"]["derived"]
    composition = matmul(fixture["chain_complex"]["d1"], fixture["chain_complex"]["d2"])
    main_checks = {
        "chain_condition_verified": all(x == 0 for row in composition for x in row) == expected["chain_condition_zero"],
        "rank_d2_verified": observed["rank_d2"] == expected["rank_d2"],
        "rank_d1_verified": observed["rank_d1"] == expected["rank_d1"],
        "homology_dimensions_verified": observed["homology_dimensions"] == expected["homology_dimensions"],
        "typed_residue_packet_emitted": set(packet) == {"carrier", "D", "Sigma", "Ext", "Sing", "memory"},
        "no_singularity_in_nominal_fixture": packet["Sing"] == [] and packet["Sigma"] == 0,
        "formal_ext_like_residuals_zero": packet["Ext"]["residuals"] == [0],
        "formal_ext_label_preserved": packet["Ext"]["standing"] == "FORMAL_EXT_LIKE_RESIDUAL_NOT_EXT_FUNCTOR",
    }
    replay_nominal = replay(packet, fixture)
    main_checks["replay_memory_reconstructs_original_packet"] = replay_nominal["status"] == "REPLAY_MATCH"

    # Negative control 1: violate d1∘d2=0.
    broken_fixture = copy.deepcopy(fixture)
    broken_fixture["chain_complex"]["d1"] = [[1, 0]]
    broken_packet = derived_packet(broken_fixture)
    broken_chain_detected = (
        broken_packet["Sigma"] == 1
        and any(item.get("type") == "CHAIN_CONDITION_DEFECT" for item in broken_packet["Sing"])
    )

    # Negative control 2: corrupt replay memory without altering the formal derived packet.
    corrupt_packet = copy.deepcopy(packet)
    corrupt_packet["memory"]["state"] = [2, 3, 7]
    corrupt_replay = replay(corrupt_packet, fixture)

    negative_checks = {
        "broken_chain_condition_detected_as_singularity": broken_chain_detected,
        "replay_memory_corruption_detected": corrupt_replay["status"] == "REPLAY_DEFECT" and "state" in corrupt_replay["defects"],
    }

    checks = {
        **source_checks,
        **main_checks,
        **negative_checks,
        "formal_ext_like_residuals_do_not_claim_Ext_theorem": packet["Ext"]["standing"] == "FORMAL_EXT_LIKE_RESIDUAL_NOT_EXT_FUNCTOR",
        "empirical_closure_remains_hold": "EXTERNAL_EMPIRICAL_CLOSURE_WITNESS" in contract["standing_after_pass"]["remaining_obligations"],
        "f36_evidence_hold_preserved": contract["standing_after_pass"]["evidence"] == "HOLD",
        "promotion_authority_false": contract["standing_after_pass"]["promotion_authority"] is False,
    }
    ok = all(checks.values())

    receipt = {
        "artifact": contract["artifact"],
        "status": "F36_GENERIC_DERIVED_REPLAY_WITNESS_PASS" if ok else "F36_GENERIC_DERIVED_REPLAY_WITNESS_HOLD",
        "checkout_head": head(),
        "gid": 79,
        "carrier": "F36",
        "checks": checks,
        "nominal_packet": packet,
        "nominal_replay": replay_nominal,
        "negative_controls": {
            "broken_chain": broken_packet,
            "corrupt_replay": corrupt_replay,
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
