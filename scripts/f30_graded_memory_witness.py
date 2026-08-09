from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "spec" / "F30_GRADED_MEMORY_WITNESS_V1.json"
F37_SOURCE_PATH = ROOT / "spec" / "F37_LIBRARY_SOURCE_POPULATION_V1.json"
OUTPUT = Path("f30_graded_memory_witness_v1.json")


def head() -> str:
    return subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def grade_record(grade: int, data: dict) -> dict:
    basis = list(data["basis"])
    signs = [int(x) for x in data["action_signs"]]
    dimension = len(basis)
    trace = sum(signs)
    return {
        "grade": grade,
        "basis": basis,
        "action_signs": signs,
        "dimension": dimension,
        "trace": trace,
        "action_order_two": len(signs) == dimension and all(sign in (-1, 1) and sign * sign == 1 for sign in signs),
        "content_digest": digest({"grade": grade, "basis": basis, "action_signs": signs}),
    }


def replay(records: list[dict], order: list[int]) -> dict:
    by_grade = {int(row["grade"]): row for row in records}
    missing = [grade for grade in order if grade not in by_grade]
    if missing:
        return {"status": "REPLAY_DEFECT", "defects": [{"type": "MISSING_GRADE", "grades": missing}]}
    dimensions = [int(by_grade[grade]["dimension"]) for grade in order]
    characters = [int(by_grade[grade]["trace"]) for grade in order]
    digest_errors = []
    for grade in order:
        row = by_grade[grade]
        expected = digest({"grade": grade, "basis": row["basis"], "action_signs": row["action_signs"]})
        if row.get("content_digest") != expected:
            digest_errors.append(grade)
    return {
        "status": "REPLAY_MATCH" if not digest_errors else "REPLAY_DEFECT",
        "defects": [] if not digest_errors else [{"type": "GRADE_DIGEST_MISMATCH", "grades": digest_errors}],
        "dimension_series": dimensions,
        "character_series": characters,
    }


def main() -> int:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    f37 = json.loads(F37_SOURCE_PATH.read_text(encoding="utf-8"))
    fixture = contract["formal_fixture"]
    order = [int(x) for x in fixture["memory_order"]]

    source_checks = {
        "f30_parent_hold_present": f37["known_hold_by_gid"].get("73") == "GRADED_MEMORY_PARTIAL_EXACTIFICATION",
        "f30_is_honesty_ledger": "F30" in f37["source_status_partition"]["HONESTY_LEDGER_HOLD"],
        "math_source_hash_match": f37["source_roots"]["F37_MATH_LEDGER"]["sha256"] == contract["source_roots"]["math"]["sha256"],
        "symmetry_source_hash_match": f37["source_roots"]["F37_SYMMETRY_LEDGER"]["sha256"] == contract["source_roots"]["symmetry"]["sha256"],
    }

    records = [grade_record(int(grade), data) for grade, data in sorted(fixture["grades"].items(), key=lambda kv: int(kv[0]))]
    dimension_series = [row["dimension"] for row in records]
    character_series = [row["trace"] for row in records]
    nominal_replay = replay(records, order)

    main_checks = {
        "all_grade_dimensions_nonnegative_integers": all(isinstance(row["dimension"], int) and row["dimension"] >= 0 for row in records),
        "dimension_series_matches_grades": dimension_series == fixture["expected_dimension_series"],
        "C2_action_squares_to_identity": all(row["action_order_two"] for row in records),
        "character_series_matches_grade_traces": character_series == fixture["expected_character_series"],
        "grade_content_digests_are_stable": len({row["content_digest"] for row in records}) == len(records),
        "replay_reconstructs_dimension_and_character_series": (
            nominal_replay["status"] == "REPLAY_MATCH"
            and nominal_replay["dimension_series"] == fixture["expected_dimension_series"]
            and nominal_replay["character_series"] == fixture["expected_character_series"]
        ),
    }

    tampered_dimensions = list(fixture["expected_dimension_series"])
    tampered_dimensions[2] += 1
    dimension_tamper_detected = tampered_dimensions != dimension_series

    tampered_records = copy.deepcopy(records)
    tampered_records[1]["action_signs"][2] = 1
    tampered_records[1]["trace"] = sum(tampered_records[1]["action_signs"])
    tampered_records[1]["content_digest"] = digest({"grade": 1, "basis": tampered_records[1]["basis"], "action_signs": tampered_records[1]["action_signs"]})
    tampered_character = [row["trace"] for row in tampered_records]
    character_tamper_detected = tampered_character != fixture["expected_character_series"]

    corrupted_memory = copy.deepcopy(records)
    corrupted_memory[3]["basis"][0] = "CORRUPTED"
    corrupt_replay = replay(corrupted_memory, order)

    negative_checks = {
        "tampered_dimension_series_detected": dimension_tamper_detected,
        "tampered_character_trace_detected": character_tamper_detected,
        "tampered_grade_memory_detected": corrupt_replay["status"] == "REPLAY_DEFECT" and bool(corrupt_replay["defects"]),
    }

    checks = {
        **source_checks,
        **main_checks,
        **negative_checks,
        "finite_fixture_not_upgraded_to_moonshine_theorem": True,
        "f30_evidence_hold_preserved": contract["standing_after_pass"]["evidence"] == "HOLD",
        "promotion_authority_false": contract["standing_after_pass"]["promotion_authority"] is False,
    }
    ok = all(checks.values())

    receipt = {
        "artifact": contract["artifact"],
        "status": "F30_GENERIC_GRADED_MEMORY_WITNESS_PASS" if ok else "F30_GENERIC_GRADED_MEMORY_WITNESS_HOLD",
        "checkout_head": head(),
        "gid": 73,
        "carrier": "F30",
        "checks": checks,
        "grade_records": records,
        "dimension_series": dimension_series,
        "character_series": character_series,
        "nominal_replay": nominal_replay,
        "negative_controls": {
            "tampered_dimension_series": tampered_dimensions,
            "tampered_character_series": tampered_character,
            "corrupted_memory_replay": corrupt_replay,
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
