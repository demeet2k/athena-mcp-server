from __future__ import annotations

import itertools
import json
import subprocess
from collections import Counter
from pathlib import Path

from athena_mcp.inner_constitution import seat

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "spec" / "KC15_INDEPENDENT_WITNESS_V1.json"
POPULATION_SPEC_PATH = ROOT / "spec" / "KC15_KC27_LIBRARY_SOURCE_POPULATION_V1.json"
OUTPUT = Path("kc15_independent_witness_v1.json")


def git_head() -> str:
    return subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()


def blob_sha(path: str) -> str:
    return subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", f"HEAD:{path}"], text=True).strip()


def independent_masks(poles: list[str]) -> list[dict]:
    rows = []
    for n in range(1, 1 << len(poles)):
        bits = [1 if n & (1 << i) else 0 for i in range(len(poles))]
        mask = "".join(str(bit) for bit in bits)
        support = [pole for pole, bit in zip(poles, bits) if bit]
        rows.append({"ordinal": n, "gid": 90 + n, "mask": mask, "support": support, "rank": len(support)})
    return rows


def main() -> int:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    population = json.loads(POPULATION_SPEC_PATH.read_text(encoding="utf-8"))
    poles = list(contract["poles"])
    rows = independent_masks(poles)
    active_masks = population["kc15"]["active_masks"]

    checks: dict[str, bool] = {}
    checks["exactly_15_masks"] = len(rows) == 15
    checks["all_masks_nonempty"] = all(row["rank"] >= 1 for row in rows)
    checks["all_masks_unique"] = len({row["mask"] for row in rows}) == 15
    checks["all_supports_unique"] = len({tuple(row["support"]) for row in rows}) == 15

    mismatches = []
    for row in rows:
        gid = row["gid"]
        descriptor = seat(gid)
        declared = active_masks[str(gid)]
        expected_coord = "{" + ",".join(row["support"]) + "}"
        if descriptor["code"] != row["mask"]:
            mismatches.append({"gid": gid, "field": "constitution_mask", "expected": row["mask"], "actual": descriptor["code"]})
        if descriptor["coordinate"] != expected_coord:
            mismatches.append({"gid": gid, "field": "constitution_support", "expected": expected_coord, "actual": descriptor["coordinate"]})
        if declared["mask"] != row["mask"]:
            mismatches.append({"gid": gid, "field": "population_mask", "expected": row["mask"], "actual": declared["mask"]})
        if list(declared["support"]) != row["support"]:
            mismatches.append({"gid": gid, "field": "population_support", "expected": row["support"], "actual": declared["support"]})
    checks["active_epoch_mapping_matches_independent_enumeration"] = not mismatches

    rank_counts = Counter(row["rank"] for row in rows)
    expected_rank = {int(k): int(v) for k, v in contract["required_rank_distribution"].items()}
    checks["rank_distribution_4_6_4_1"] = dict(rank_counts) == expected_rank

    support_to_gid = {frozenset(row["support"]): row["gid"] for row in rows}
    all_supports = set(support_to_gid)
    empty = frozenset()
    pair_failures = []
    empty_intersections = 0
    for left, right in itertools.product(rows, repeat=2):
        a = frozenset(left["support"])
        b = frozenset(right["support"])
        union = a | b
        inter = a & b
        if union not in all_supports:
            pair_failures.append({"left": left["gid"], "right": right["gid"], "operation": "union", "result": sorted(union)})
        if inter:
            if inter not in all_supports:
                pair_failures.append({"left": left["gid"], "right": right["gid"], "operation": "intersection", "result": sorted(inter)})
        else:
            empty_intersections += 1
    checks["union_closure"] = not any(row["operation"] == "union" for row in pair_failures)
    checks["nonempty_intersection_closure"] = not any(row["operation"] == "intersection" for row in pair_failures)
    checks["empty_subset_excluded"] = empty not in all_supports and empty_intersections > 0
    checks["full_mask_present"] = any(row["mask"] == "1111" and row["support"] == poles for row in rows)

    # Structural witness is deliberately non-authoritative outside the finite lattice claim.
    semantic_firewalls = {
        "support_is_truth": False,
        "support_is_evidence": False,
        "support_is_probability": False,
        "mask_is_semantic_identity": False,
        "structural_witness_grants_execution_authority": False,
        "structural_witness_grants_promotion_authority": False,
    }
    checks["all_authority_firewalls_false"] = not any(semantic_firewalls.values())

    ok = all(checks.values())
    head = git_head()
    receipt = {
        "artifact": contract["artifact"],
        "status": "KC15_INDEPENDENT_STRUCTURAL_WITNESS_PASS" if ok else "KC15_INDEPENDENT_STRUCTURAL_WITNESS_HOLD",
        "checkout_head": head,
        "source_refs": [
            f"GIT_BLOB:athena_mcp/inner_constitution.py:{blob_sha('athena_mcp/inner_constitution.py')}",
            f"GIT_BLOB:spec/KC15_KC27_LIBRARY_SOURCE_POPULATION_V1.json:{blob_sha('spec/KC15_KC27_LIBRARY_SOURCE_POPULATION_V1.json')}",
        ],
        "independence_group": contract["success_standing"]["independence_group"],
        "checks": checks,
        "rank_distribution_observed": {str(k): v for k, v in sorted(rank_counts.items())},
        "empty_intersection_cases": empty_intersections,
        "mismatches": mismatches,
        "pair_failures": pair_failures,
        "rows": rows,
        "semantic_firewalls": semantic_firewalls,
        "standing_after_witness": {
            "population": "CLOSED",
            "execution": "PARTIAL",
            "evidence": "HOLD",
            "independent_structural_witness": "PASS" if ok else "HOLD",
            "interpretation_review": "HOLD",
            "admission_authority": "HOLD",
            "truth_claim": "NOT_ESTABLISHED",
            "promotion_authority": False,
        },
        "next_obligations": [
            "KC15_INTERPRETATION_REVIEW",
            "KC15_IC10_ADMISSION_AUTHORITY",
        ] if ok else ["REPAIR_KC15_STRUCTURAL_WITNESS"],
        "evidence_ceiling": [
            "INDEPENDENT_STRUCTURAL_WITNESS != CLAIM_TRUTH",
            "INDEPENDENT_STRUCTURAL_WITNESS != INTERPRETATION_REVIEW",
            "INDEPENDENT_STRUCTURAL_WITNESS != ADMISSION_AUTHORITY",
            "KC15_EVIDENCE_REMAINS_HOLD_UNTIL_REMAINING_OBLIGATIONS_DISCHARGE",
        ],
    }
    OUTPUT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in receipt.items() if k != "rows"}, indent=2, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
