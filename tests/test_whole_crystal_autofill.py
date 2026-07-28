from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

from MCP.crystal_108d.whole_crystal_autofill import (
    CONTROL_W32_HEAD,
    CONTROL_W32_TREE,
    DATA_PATH,
    FORCED_FIELDS,
    FrozenWholeCrystalAutofill,
    PLANE,
    PRODUCTION_COUNT_FIELDS,
    RUNTIME_W32_HEAD,
    RUNTIME_W32_TREE,
    SCHEMA,
    SUCCESSOR,
    WITHHELD_FIELDS,
    WholeCrystalAutofillError,
)


def _compiler() -> FrozenWholeCrystalAutofill:
    return FrozenWholeCrystalAutofill.load()


def test_frozen_snapshot_contract_and_identity():
    compiler = _compiler()
    assert compiler.snapshot["schema"] == SCHEMA
    assert compiler.snapshot["plane"] == PLANE
    assert compiler.snapshot["contract_digest"].startswith("sha256:")


def test_exact_runtime_and_control_w32_custody():
    predecessor = _compiler().snapshot["predecessor"]
    assert predecessor["runtime_head"] == RUNTIME_W32_HEAD
    assert predecessor["runtime_tree"] == RUNTIME_W32_TREE
    assert predecessor["control_head"] == CONTROL_W32_HEAD
    assert predecessor["control_tree"] == CONTROL_W32_TREE


def test_four_manifestations_remain_distinct():
    compiler = _compiler()
    assert list(compiler.manifestations) == [
        "INTERNAL_CONTINUITY",
        "GOOGLE_DRIVE",
        "GITHUB_RUNTIME",
        "GITHUB_CONTROL",
    ]
    assert len(
        {
            item["source_id"]
            for item in compiler.snapshot["manifestations"]
        }
    ) == 4


def test_every_manifestation_covers_all_eight_propositions():
    compiler = _compiler()
    expected = set(compiler.propositions)
    assert len(expected) == 8
    for manifestation in compiler.manifestations.values():
        assert set(manifestation["proposition_states"]) == expected


def test_convergence_lattice_closes_seven_structural_laws_only():
    lattice = _compiler().convergence_lattice()
    assert lattice["row_count"] == 8
    assert lattice["forced_structural_propositions"] == 7
    assert lattice["semantic_empirical_authority_autofills"] == 0
    authority = next(
        row
        for row in lattice["rows"]
        if row["proposition_id"] == "P06_AUTHORITY_BARRIER"
    )
    assert authority["structurally_forced"] is False
    assert authority["autofill_policy"] == "FORBIDDEN"


def test_live_w32_state_converges_across_both_git_bodies():
    row = next(
        item
        for item in _compiler().convergence_lattice()["rows"]
        if item["proposition_id"] == "P05_W32_VERIFIER_STATE"
    )
    assert row["surface_states"]["GITHUB_RUNTIME"] == "EXACT"
    assert row["surface_states"]["GITHUB_CONTROL"] == "EXACT"
    assert row["standing"] == "EXACT_CROSS_SURFACE"


def test_defect_tensor_has_declared_four_by_eight_by_five_by_two_shape():
    tensor = _compiler().defect_tensor()
    assert tensor["shape"] == [4, 8, 5, 2]
    assert tensor["cell_count"] == 320
    assert tensor["zero_defect_cells"] + tensor["nonzero_defect_cells"] == 320


def test_defect_tensor_filter_is_exact():
    tensor = _compiler().defect_tensor(
        surface="GITHUB_RUNTIME",
        proposition_id="P05_W32_VERIFIER_STATE",
    )
    assert tensor["shape"] == [1, 1, 5, 2]
    assert tensor["cell_count"] == 10
    assert {
        cell["surface"] for cell in tensor["cells"]
    } == {"GITHUB_RUNTIME"}


def test_authority_lens_never_has_zero_defect():
    tensor = _compiler().defect_tensor()
    authority_cells = [
        cell for cell in tensor["cells"] if cell["lens"] == "AUTHORITY"
    ]
    assert len(authority_cells) == 64
    assert all(cell["defect"] > 0 for cell in authority_cells)
    assert all(
        "AUTHORITY_NOT_AUTOFILLABLE" in cell["reasons"]
        for cell in authority_cells
    )


def test_physical_grid_is_a_bijection():
    compiler = _compiler()
    cells = [compiler.station(gid) for gid in range(1, 145)]
    assert len({cell["gid"] for cell in cells}) == 144
    assert len({cell["grid"] for cell in cells}) == 144
    assert cells[0]["grid"] == "R01C01"
    assert cells[-1]["grid"] == "R12C12"


def test_angle_and_octave_formulas_are_exact():
    compiler = _compiler()
    assert compiler.station(1)["theta_degrees"] == 0
    assert compiler.station(144)["theta_degrees"] == 357.5
    assert compiler.station(144, octave=4)["scale"] == 16


def test_grid_neighbors_do_not_wrap():
    compiler = _compiler()
    assert compiler.station(1)["neighbors"] == ["GID002", "GID013"]
    assert compiler.station(144)["neighbors"] == ["GID132", "GID143"]
    assert len(compiler.station(66)["neighbors"]) == 4


def test_generated_cell_marks_every_withheld_nonstructural_field():
    cell = _compiler().station(50)
    assert cell["fill_class"] == "GENERATED_STRUCTURAL"
    assert set(cell["withheld"]) == set(WITHHELD_FIELDS)
    assert cell["withheld"]["semantic_role"] == "AMBIG"
    assert cell["withheld"]["promotion_state"] == "FORBIDDEN"
    assert cell["authority_state"] == "HOLD"


def test_every_fill_carries_generator_neighbors_and_rejection_tests():
    cell = _compiler().station(90)
    assert cell["generator"]["contract_digest"].startswith("sha256:")
    assert cell["neighbors"]
    assert cell["invariants"]
    assert cell["losses"]
    assert cell["rejection_tests"]
    assert cell["alternatives"] == []


def test_fixed_point_closes_all_144_structural_envelopes_in_one_wave():
    closure = _compiler().compile_fixed_point()
    assert closure["fixed_point_reached"] is True
    assert closure["station_cells"] == 144
    assert closure["iterations"][-1]["frontier"] == 0
    assert closure["forced_structural_fields"] == 144 * len(FORCED_FIELDS)
    assert closure["withheld_nonstructural_fields"] == 144 * len(
        WITHHELD_FIELDS
    )


def test_fixed_point_is_deterministic_and_octave_parent_qualified():
    compiler = _compiler()
    base_a = compiler.compile_fixed_point()
    base_b = compiler.compile_fixed_point()
    lifted = compiler.compile_fixed_point(octave=1)
    assert base_a["closure_digest"] == base_b["closure_digest"]
    assert base_a["cell_root"] != lifted["cell_root"]
    assert base_a["station_cells"] == lifted["station_cells"] == 144


def test_fixed_point_cannot_change_production_or_truth():
    closure = _compiler().compile_fixed_point()
    assert set(closure["production_counts"]) == set(PRODUCTION_COUNT_FIELDS)
    assert all(value == 0 for value in closure["production_counts"].values())
    assert closure["truth_credit_assigned"] == 0
    assert closure["authority_effect"] == "NONE"
    assert closure["production_effect"] == "NONE"


def test_every_genuine_barrier_remains_non_autofillable():
    result = _compiler().barriers()
    assert result["autofillable_barriers"] == 0
    assert len(result["barriers"]) == 6
    assert all(item["autofillable"] is False for item in result["barriers"])
    assert result["successor"] == SUCCESSOR


def test_status_preserves_blocked_w33_and_negative_effects():
    status = _compiler().status()
    assert status["successor"] == SUCCESSOR
    assert "HOLD_W33_EXTERNAL_AUTHORITY_RETURN" in status["status"]
    assert status["authority_generated"] is False
    assert status["registry_opened"] is False
    assert status["production_effect_claimed"] is False


def test_explanation_names_the_exact_fixed_point_separation():
    result = _compiler().explain()
    assert result["equation"] == "F[n+1]=F[n]∪READY_STRUCTURAL(F[n])"
    assert result["forced_fields"] == list(FORCED_FIELDS)
    assert result["withheld_fields"] == list(WITHHELD_FIELDS)
    assert result["direction"][0] == "SEED"
    assert result["direction"][-1] == "GID144_M12_REENTRY"


@pytest.mark.parametrize("gid", [0, 145, True, "1"])
def test_invalid_gid_fails_closed(gid):
    with pytest.raises(ValueError):
        _compiler().station(gid)  # type: ignore[arg-type]


@pytest.mark.parametrize("octave", [-1, True, 1.5])
def test_invalid_octave_fails_closed(octave):
    with pytest.raises(ValueError):
        _compiler().station(1, octave=octave)  # type: ignore[arg-type]


def test_unknown_tensor_coordinates_fail_closed():
    compiler = _compiler()
    with pytest.raises(ValueError):
        compiler.defect_tensor(surface="NOT_A_SURFACE")
    with pytest.raises(ValueError):
        compiler.defect_tensor(proposition_id="NOT_A_PROPOSITION")


def test_contract_tamper_is_rejected():
    snapshot = json.loads(DATA_PATH.read_text())
    tampered = deepcopy(snapshot)
    tampered["production_counts"]["promotions"] = 1
    with pytest.raises(ValueError):
        FrozenWholeCrystalAutofill(tampered)


def test_source_state_tamper_is_rejected_even_if_rehashed():
    snapshot = json.loads(DATA_PATH.read_text())
    tampered = deepcopy(snapshot)
    tampered["manifestations"][0]["retrieval_state"] = "PROMOTED"
    tampered["contract_digest"] = "sha256:invalid"
    with pytest.raises(ValueError):
        FrozenWholeCrystalAutofill(tampered, allow_test_contract=True)


def test_content_addressed_receipt_matches_compiled_closure():
    root = Path(__file__).resolve().parents[1]
    receipt = json.loads(
        (
            root
            / ".athena"
            / "receipts"
            / "whole-crystal-convergence-autofill.json"
        ).read_text()
    )
    addressed = deepcopy(receipt)
    receipt_id = addressed.pop("receipt_id")
    computed = hashlib.sha256(
        json.dumps(
            addressed,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
    ).hexdigest()
    assert receipt_id == f"whole-crystal-convergence-autofill:sha256:{computed}"
    closure = _compiler().compile_fixed_point()
    assert (
        receipt["mathematical_closure"]["closure_digest"]
        == closure["closure_digest"]
    )
    assert receipt["mathematical_closure"]["cell_root"] == closure["cell_root"]
    assert all(value == 0 for value in receipt["production_counts"].values())


def test_cli_replays_frozen_status():
    root = Path(__file__).resolve().parents[1]
    completed = subprocess.run(
        [sys.executable, "scripts/whole_crystal_autofill.py", "--status"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    result = json.loads(completed.stdout)
    assert result["fixed_point"]["station_cells"] == 144
    assert result["successor"] == SUCCESSOR
