from __future__ import annotations

from collections import defaultdict
import hashlib
from typing import Any

from self_actualize.runtime.hemisphere_brain_support import (
    FLEET_MIRROR_ROOT,
    HEMISPHERE_ROOT,
    PT2_METRO_INTERLOCKS_PATH,
    REGISTRY_ROOT,
    SELF_ACTUALIZE_ROOT,
    load_json,
    utc_now,
)


DENSE_65_PRIMARY_CAP = 8
DENSE_65_PRIOR_SEED_POSITION = "1/65"
DENSE_65_RING_ORDER = ["A", "C", "B", "D"]
DENSE_65_CELL_FAMILIES = ("R", "Q", "T")
DENSE_65_SIGMA_PATH = ["AppA", "AppI", "AppM"]
DENSE_65_AUTHORITY_REFS = {
    "sigma_ingress": "AppA",
    "truth_lattice": "AppI",
    "replay_kernel": "AppM",
    "rotation_authority": "AppF",
    "antispin_authority": "AppG",
}
DENSE_65_FLOWER_LENS = "F"
DENSE_65_FLOWER_LENS_LABEL = "Flower"
DENSE_65_TICK_2B = "Tick_2B"
DENSE_65_VERSION_PINS_2B = "V_2B"
DENSE_65_ENV_PIN_2B = "E_2B"
DENSE_65_REPLAY_STEPS = ["ResolveZ", "ExpandAE", "RouteV2", "SlotCheck"]
DENSE_65_REPLAY_CHECKS = ["Sigma", "Hub<=6", "ZMatch"]
DENSE_65_AETHER_SLOTS = ["Core", "Ticket", "Residual", "Test"]
DENSE_65_PHASE_BINS = {
    "Phi0": "R+",
    "Phi1": "R-",
    "Phi2": "Q4",
    "Phi3": "T3",
}
DENSE_65_ROUTE_KEYS = {
    "rtL": "AppA>AppI>AppM>AppF>AppN>Ch21<0110>",
    "rtZ": "AppA>AppI>AppM>AppF>AppG>Ch21<0110>",
}
DENSE_65_Z_KEYS = {
    "ZA": "Z(Fire)",
    "ZB": "Z(Water)",
    "ZC": "Z(Air)",
    "ZD": "Z(Earth)",
}
DENSE_65_BUNDLE_LOCK = {
    "01": {"pole_set": ["A"], "z_binding": "ZA", "check_key": "loc(A)"},
    "02": {"pole_set": ["B"], "z_binding": "ZB", "check_key": "loc(B)"},
    "03": {"pole_set": ["A", "B"], "z_binding": "ZA+ZB", "check_key": "Z*"},
    "10": {"pole_set": ["C"], "z_binding": "ZC", "check_key": "loc(C)"},
    "11": {"pole_set": ["A", "C"], "z_binding": "ZA+ZC", "check_key": "loc(A>C)"},
    "12": {"pole_set": ["B", "C"], "z_binding": "ZB+ZC", "check_key": "loc(C>B)"},
    "13": {"pole_set": ["A", "B", "C"], "z_binding": "ZA+ZB+ZC", "check_key": "loc(A>C>B)"},
    "20": {"pole_set": ["D"], "z_binding": "ZD", "check_key": "loc(D)"},
    "21": {"pole_set": ["A", "D"], "z_binding": "ZA+ZD", "check_key": "loc(D>A)"},
    "22": {"pole_set": ["B", "D"], "z_binding": "ZB+ZD", "check_key": "loc(B>D)"},
    "23": {"pole_set": ["A", "B", "D"], "z_binding": "ZA+ZB+ZD", "check_key": "loc(B>D>A)"},
    "30": {"pole_set": ["C", "D"], "z_binding": "ZC+ZD", "check_key": "Z*"},
    "31": {"pole_set": ["A", "C", "D"], "z_binding": "ZA+ZC+ZD", "check_key": "loc(D>A>C)"},
    "32": {"pole_set": ["B", "C", "D"], "z_binding": "ZB+ZC+ZD", "check_key": "loc(C>B>D)"},
    "33": {"pole_set": ["A", "B", "C", "D"], "z_binding": "ZA+ZB+ZC+ZD", "check_key": "Z*"},
}

DENSE_65_SHELL_REGISTRY_PATH = SELF_ACTUALIZE_ROOT / "myth_math_dense_65_shell_registry.json"
DENSE_65_RQT_WITNESS_REGISTRY_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_dense_65_rqt_witness_registry.json"
)
DENSE_65_RQT_OVERFLOW_REGISTRY_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_dense_65_rqt_overflow_registry.json"
)
DENSE_65_MANIFEST_PATH = SELF_ACTUALIZE_ROOT / "myth_math_dense_65_manifest.json"

DENSE_65_SHELL_REGISTRY_MIRROR = REGISTRY_ROOT / DENSE_65_SHELL_REGISTRY_PATH.name
DENSE_65_RQT_WITNESS_REGISTRY_MIRROR = REGISTRY_ROOT / DENSE_65_RQT_WITNESS_REGISTRY_PATH.name
DENSE_65_RQT_OVERFLOW_REGISTRY_MIRROR = REGISTRY_ROOT / DENSE_65_RQT_OVERFLOW_REGISTRY_PATH.name
DENSE_65_MANIFEST_MIRROR = REGISTRY_ROOT / DENSE_65_MANIFEST_PATH.name

DENSE_65_HEMISPHERE_DOCS = {
    "dense_65_shell_index": HEMISPHERE_ROOT / "91_dense_65_shell_index.md",
    "dense_65_r_atlas": HEMISPHERE_ROOT / "92_dense_65_r_witness_atlas.md",
    "dense_65_q_atlas": HEMISPHERE_ROOT / "93_dense_65_q_orbit_atlas.md",
    "dense_65_t_atlas": HEMISPHERE_ROOT / "94_dense_65_t_antispin_atlas.md",
    "dense_65_coverage": HEMISPHERE_ROOT / "95_dense_65_coverage_and_overflow_receipt.md",
}

DENSE_65_HEADER_ROW = {
    "shell_position": DENSE_65_PRIOR_SEED_POSITION,
    "cell_id": "H00",
    "cell_family": "H",
    "label": "prior seed/header shell",
    "record_kind": "H",
    "record_index": 1,
    "record_id": "H00",
    "dense_kernel_ref": "DenseKernel65::H00",
    "sigma_path": list(DENSE_65_SIGMA_PATH),
    "authority_refs": dict(DENSE_65_AUTHORITY_REFS),
    "truth": "OK",
}


def _row(
    shell_position: str,
    cell_id: str,
    family: str,
    **fields: Any,
) -> dict[str, Any]:
    return {
        "shell_position": shell_position,
        "cell_id": cell_id,
        "cell_family": family,
        **fields,
    }


DENSE_65_P_ROWS = [
    _row("2/65", "P0", "P", pole="A", label="Fire", theta="0deg", rot_plus="C", inverse="B", rot_minus="D", z="Z(Fire)", ae="AE[F]"),
    _row("3/65", "P2", "P", pole="B", label="Water", theta="180deg", rot_plus="D", inverse="A", rot_minus="C", z="Z(Water)", ae="AE[W]"),
    _row("4/65", "P1", "P", pole="C", label="Air", theta="90deg", rot_plus="B", inverse="D", rot_minus="A", z="Z(Air)", ae="AE[A]"),
    _row("5/65", "P3", "P", pole="D", label="Earth", theta="270deg", rot_plus="A", inverse="C", rot_minus="B", z="Z(Earth)", ae="AE[E]"),
]


DENSE_65_S_ROWS = [
    _row("6/65", "S01", "S", mu="01", pole_set=["A"], card=1),
    _row("7/65", "S02", "S", mu="02", pole_set=["B"], card=1),
    _row("8/65", "S03", "S", mu="03", pole_set=["A", "B"], card=2),
    _row("9/65", "S10", "S", mu="10", pole_set=["C"], card=1),
    _row("10/65", "S11", "S", mu="11", pole_set=["A", "C"], card=2),
    _row("11/65", "S12", "S", mu="12", pole_set=["B", "C"], card=2),
    _row("12/65", "S13", "S", mu="13", pole_set=["A", "B", "C"], card=3),
    _row("13/65", "S20", "S", mu="20", pole_set=["D"], card=1),
    _row("14/65", "S21", "S", mu="21", pole_set=["A", "D"], card=2),
    _row("15/65", "S22", "S", mu="22", pole_set=["B", "D"], card=2),
    _row("16/65", "S23", "S", mu="23", pole_set=["A", "B", "D"], card=3),
    _row("17/65", "S30", "S", mu="30", pole_set=["C", "D"], card=2),
    _row("18/65", "S31", "S", mu="31", pole_set=["A", "C", "D"], card=3),
    _row("19/65", "S32", "S", mu="32", pole_set=["B", "C", "D"], card=3),
    _row("20/65", "S33", "S", mu="33", pole_set=["A", "B", "C", "D"], card=4),
]


DENSE_65_R_ROWS = [
    _row("21/65", "R01", "R", src_set=["A"], rot_plus_set=["C"], rot_minus_set=["D"]),
    _row("22/65", "R02", "R", src_set=["B"], rot_plus_set=["D"], rot_minus_set=["C"]),
    _row("23/65", "R03", "R", src_set=["A", "B"], rot_plus_set=["C", "D"], rot_minus_set=["C", "D"]),
    _row("24/65", "R10", "R", src_set=["C"], rot_plus_set=["B"], rot_minus_set=["A"]),
    _row("25/65", "R11", "R", src_set=["A", "C"], rot_plus_set=["B", "C"], rot_minus_set=["A", "D"]),
    _row("26/65", "R12", "R", src_set=["B", "C"], rot_plus_set=["B", "D"], rot_minus_set=["A", "C"]),
    _row("27/65", "R13", "R", src_set=["A", "B", "C"], rot_plus_set=["B", "C", "D"], rot_minus_set=["A", "C", "D"]),
    _row("28/65", "R20", "R", src_set=["D"], rot_plus_set=["A"], rot_minus_set=["B"]),
    _row("29/65", "R21", "R", src_set=["A", "D"], rot_plus_set=["A", "C"], rot_minus_set=["B", "D"]),
    _row("30/65", "R22", "R", src_set=["B", "D"], rot_plus_set=["A", "D"], rot_minus_set=["B", "C"]),
    _row("31/65", "R23", "R", src_set=["A", "B", "D"], rot_plus_set=["A", "C", "D"], rot_minus_set=["B", "C", "D"]),
    _row("32/65", "R30", "R", src_set=["C", "D"], rot_plus_set=["A", "B"], rot_minus_set=["A", "B"]),
    _row("33/65", "R31", "R", src_set=["A", "C", "D"], rot_plus_set=["A", "B", "C"], rot_minus_set=["A", "B", "D"]),
    _row("34/65", "R32", "R", src_set=["B", "C", "D"], rot_plus_set=["A", "B", "D"], rot_minus_set=["A", "B", "C"]),
    _row("35/65", "R33", "R", src_set=["A", "B", "C", "D"], rot_plus_set=["A", "B", "C", "D"], rot_minus_set=["A", "B", "C", "D"]),
]


DENSE_65_Q_ROWS = [
    _row("36/65", "Q01", "Q", base4_orbit=[["A"], ["C"], ["B"], ["D"]]),
    _row("37/65", "Q02", "Q", base4_orbit=[["B"], ["D"], ["A"], ["C"]]),
    _row("38/65", "Q03", "Q", base4_orbit=[["A", "B"], ["C", "D"], ["A", "B"], ["C", "D"]]),
    _row("39/65", "Q10", "Q", base4_orbit=[["C"], ["B"], ["D"], ["A"]]),
    _row("40/65", "Q11", "Q", base4_orbit=[["A", "C"], ["B", "C"], ["B", "D"], ["A", "D"]]),
    _row("41/65", "Q12", "Q", base4_orbit=[["B", "C"], ["B", "D"], ["A", "D"], ["A", "C"]]),
    _row("42/65", "Q13", "Q", base4_orbit=[["A", "B", "C"], ["B", "C", "D"], ["A", "B", "D"], ["A", "C", "D"]]),
    _row("43/65", "Q20", "Q", base4_orbit=[["D"], ["A"], ["C"], ["B"]]),
    _row("44/65", "Q21", "Q", base4_orbit=[["A", "D"], ["A", "C"], ["B", "C"], ["B", "D"]]),
    _row("45/65", "Q22", "Q", base4_orbit=[["B", "D"], ["A", "D"], ["A", "C"], ["B", "C"]]),
    _row("46/65", "Q23", "Q", base4_orbit=[["A", "B", "D"], ["A", "C", "D"], ["A", "B", "C"], ["B", "C", "D"]]),
    _row("47/65", "Q30", "Q", base4_orbit=[["C", "D"], ["A", "B"], ["C", "D"], ["A", "B"]]),
    _row("48/65", "Q31", "Q", base4_orbit=[["A", "C", "D"], ["A", "B", "C"], ["B", "C", "D"], ["A", "B", "D"]]),
    _row("49/65", "Q32", "Q", base4_orbit=[["B", "C", "D"], ["A", "B", "D"], ["A", "C", "D"], ["A", "B", "C"]]),
    _row("50/65", "Q33", "Q", base4_orbit=[["A", "B", "C", "D"], ["A", "B", "C", "D"], ["A", "B", "C", "D"], ["A", "B", "C", "D"]]),
]


DENSE_65_T_ROWS = [
    _row("51/65", "T01", "T", hide_pole="C", triad_set=["A", "B", "D"], anti_plus_orbit=[["A"], ["B"], ["D"]], anti_minus_orbit=[["A"], ["D"], ["B"]]),
    _row("52/65", "T02", "T", hide_pole="A", triad_set=["C", "B", "D"], anti_plus_orbit=[["B"], ["D"], ["C"]], anti_minus_orbit=[["B"], ["C"], ["D"]]),
    _row("53/65", "T03", "T", hide_pole="C", triad_set=["A", "B", "D"], anti_plus_orbit=[["A", "B"], ["B", "D"], ["A", "D"]], anti_minus_orbit=[["A", "B"], ["A", "D"], ["B", "D"]]),
    _row("54/65", "T10", "T", hide_pole="A", triad_set=["C", "B", "D"], anti_plus_orbit=[["C"], ["B"], ["D"]], anti_minus_orbit=[["C"], ["D"], ["B"]]),
    _row("55/65", "T11", "T", hide_pole="B", triad_set=["A", "C", "D"], anti_plus_orbit=[["A", "C"], ["C", "D"], ["A", "D"]], anti_minus_orbit=[["A", "C"], ["A", "D"], ["C", "D"]]),
    _row("56/65", "T12", "T", hide_pole="A", triad_set=["C", "B", "D"], anti_plus_orbit=[["B", "C"], ["B", "D"], ["C", "D"]], anti_minus_orbit=[["B", "C"], ["C", "D"], ["B", "D"]]),
    _row("57/65", "T13", "T", hide_pole="D", triad_set=["A", "C", "B"], anti_plus_orbit=[["A", "B", "C"], ["A", "B", "C"], ["A", "B", "C"]], anti_minus_orbit=[["A", "B", "C"], ["A", "B", "C"], ["A", "B", "C"]]),
    _row("58/65", "T20", "T", hide_pole="A", triad_set=["C", "B", "D"], anti_plus_orbit=[["D"], ["C"], ["B"]], anti_minus_orbit=[["D"], ["B"], ["C"]]),
    _row("59/65", "T21", "T", hide_pole="C", triad_set=["A", "B", "D"], anti_plus_orbit=[["A", "D"], ["A", "B"], ["B", "D"]], anti_minus_orbit=[["A", "D"], ["B", "D"], ["A", "B"]]),
    _row("60/65", "T22", "T", hide_pole="A", triad_set=["C", "B", "D"], anti_plus_orbit=[["B", "D"], ["C", "D"], ["B", "C"]], anti_minus_orbit=[["B", "D"], ["B", "C"], ["C", "D"]]),
    _row("61/65", "T23", "T", hide_pole="C", triad_set=["A", "B", "D"], anti_plus_orbit=[["A", "B", "D"], ["A", "B", "D"], ["A", "B", "D"]], anti_minus_orbit=[["A", "B", "D"], ["A", "B", "D"], ["A", "B", "D"]]),
    _row("62/65", "T30", "T", hide_pole="A", triad_set=["C", "B", "D"], anti_plus_orbit=[["C", "D"], ["B", "C"], ["B", "D"]], anti_minus_orbit=[["C", "D"], ["B", "D"], ["B", "C"]]),
    _row("63/65", "T31", "T", hide_pole="B", triad_set=["A", "C", "D"], anti_plus_orbit=[["A", "C", "D"], ["A", "C", "D"], ["A", "C", "D"]], anti_minus_orbit=[["A", "C", "D"], ["A", "C", "D"], ["A", "C", "D"]]),
    _row("64/65", "T32", "T", hide_pole="A", triad_set=["C", "B", "D"], anti_plus_orbit=[["B", "C", "D"], ["B", "C", "D"], ["B", "C", "D"]], anti_minus_orbit=[["B", "C", "D"], ["B", "C", "D"], ["B", "C", "D"]]),
    _row("65/65", "T33", "T", hide_pole="A", triad_set=["C", "B", "D"], anti_plus_orbit=[["A", "B", "C", "D"], ["A", "B", "C", "D"], ["A", "B", "C", "D"]], anti_minus_orbit=[["A", "B", "C", "D"], ["A", "B", "C", "D"], ["A", "B", "C", "D"]]),
]


DENSE_65_BASE_ROWS = [
    *DENSE_65_P_ROWS,
    *DENSE_65_S_ROWS,
    *DENSE_65_R_ROWS,
    *DENSE_65_Q_ROWS,
    *DENSE_65_T_ROWS,
]

DENSE_65_GROUP_COUNTS = {"H": 1, "P": 4, "S": 15, "R": 15, "Q": 15, "T": 15}

POLE_FACE_MAP = {
    "fire": "A",
    "air": "C",
    "water": "B",
    "earth": "D",
}

PROOF_RANK = {"OK": 4, "NEAR": 3, "AMBIG": 2, "UNKNOWN": 1, "FAIL": 0, "": 0, None: 0}

SET_TO_SUFFIX = {
    tuple([pole for pole in DENSE_65_RING_ORDER if pole in row["pole_set"]]): row["mu"]
    for row in DENSE_65_S_ROWS
}

R_LOOKUP = {row["cell_id"]: row for row in DENSE_65_R_ROWS}
Q_LOOKUP = {row["cell_id"]: row for row in DENSE_65_Q_ROWS}
T_LOOKUP = {row["cell_id"]: row for row in DENSE_65_T_ROWS}


def _shell_suffix(cell_id: str) -> str | None:
    return cell_id[1:] if len(cell_id) > 1 and cell_id[0] in {"S", "R", "Q", "T"} else None


def _format_pole_set(values: list[str]) -> str:
    return "{" + ",".join(values) + "}"


def _bundle_lock_for_row(row: dict[str, Any]) -> dict[str, Any] | None:
    suffix = _shell_suffix(row["cell_id"])
    if suffix is None:
        return None
    return DENSE_65_BUNDLE_LOCK.get(suffix)


def _phase_bin_for_row(row: dict[str, Any]) -> str:
    family = row["cell_family"]
    if family == "R":
        return "R+ / R-"
    if family == "Q":
        return "Q4"
    if family == "T":
        return "T3"
    return "H"


def _tunnel_required_for_row(row: dict[str, Any]) -> bool:
    lock = _bundle_lock_for_row(row)
    if lock is None:
        return False
    if lock["check_key"] == "Z*":
        return True
    pole_set = list(lock["pole_set"])
    opposites = {("A", "B"), ("C", "D")}
    return any(pair[0] in pole_set and pair[1] in pole_set for pair in opposites)


def _dense_transfer_signature_for_row(row: dict[str, Any]) -> dict[str, Any] | None:
    family = row["cell_family"]
    if family not in DENSE_65_CELL_FAMILIES:
        return None
    lock = _bundle_lock_for_row(row)
    tunnel_required = _tunnel_required_for_row(row)
    if family == "R":
        zstar_mode = "zstar_tunnel" if tunnel_required else "adjacent_bridge"
    elif family == "Q":
        zstar_mode = "order_4_orbit_with_zstar" if tunnel_required else "order_4_orbit"
    else:
        zstar_mode = "order_3_antispin_with_zstar" if tunnel_required else "order_3_antispin"
    return {
        "record_id": row["cell_id"],
        "zstar_mode": zstar_mode,
        "zstar_source": lock["z_binding"] if lock else "",
        "zstar_target": lock["z_binding"] if lock else "",
        "aether_binding": {
            "sigma_path": list(DENSE_65_SIGMA_PATH),
            "phase_bin": _phase_bin_for_row(row),
            "rotation_authority": DENSE_65_AUTHORITY_REFS["rotation_authority"],
            "antispin_authority": DENSE_65_AUTHORITY_REFS["antispin_authority"],
        },
        "opposite_pole_policy": "adjacent_bridge_or_zstar_tunnel_only",
        "tunnel_required": tunnel_required,
        "legality_class": "OK",
        "proof_ref": "Sigma=AppA->AppI->AppM ; AppF rotation ; AppG antispin",
    }


def _dense_metro_witness_for_row(row: dict[str, Any]) -> dict[str, Any] | None:
    family = row["cell_family"]
    if family not in DENSE_65_CELL_FAMILIES:
        return None
    route_class = (
        "order_4_rotation_orbit"
        if family == "Q"
        else "order_3_antispin_lock"
        if family == "T"
        else "adjacent_rotation_pair"
    )
    return {
        "record_id": row["cell_id"],
        "prior_route_class": route_class,
        "prior_route_path": list(DENSE_65_SIGMA_PATH),
        "appf_rotation_ref": DENSE_65_AUTHORITY_REFS["rotation_authority"],
        "appg_antispin_ref": DENSE_65_AUTHORITY_REFS["antispin_authority"],
        "appi_truth_ref": DENSE_65_AUTHORITY_REFS["truth_lattice"],
        "appm_replay_ref": DENSE_65_AUTHORITY_REFS["replay_kernel"],
        "witness_status": "OK",
    }


def _dense_kernel_binding(cell_row: dict[str, Any], pole_set: list[str]) -> dict[str, Any]:
    suffix = _shell_suffix(cell_row["cell_id"])
    return {
        "dense_kernel_ref": f"DenseKernel65::{cell_row['cell_id']}",
        "kernel_record_id": cell_row["cell_id"],
        "record_kind": cell_row["cell_family"],
        "shell_position": cell_row["shell_position"],
        "header_record_id": DENSE_65_HEADER_ROW["record_id"],
        "prior_seed_position": DENSE_65_PRIOR_SEED_POSITION,
        "symmetry_record_id": f"S{suffix}" if suffix else None,
        "rotation_record_id": f"R{suffix}" if suffix else None,
        "orbit_record_id": f"Q{suffix}" if suffix else None,
        "antispin_record_id": f"T{suffix}" if suffix else None,
        "pole_set": list(pole_set),
        "hide_pole": canonical_hide_pole(list(pole_set)) if pole_set else "A",
        "ring_order": list(DENSE_65_RING_ORDER),
        "sigma_path": list(DENSE_65_SIGMA_PATH),
        "authority_refs": dict(DENSE_65_AUTHORITY_REFS),
        "overlay_mode": "kernel_overlay",
    }


def _enriched_shell_row(row: dict[str, Any]) -> dict[str, Any]:
    enriched = dict(row)
    enriched["record_index"] = int(str(row["shell_position"]).split("/")[0])
    enriched["record_id"] = row["cell_id"]
    enriched["record_kind"] = row["cell_family"]
    enriched["dense_kernel_ref"] = f"DenseKernel65::{row['cell_id']}"
    enriched["sigma_path"] = list(DENSE_65_SIGMA_PATH)
    enriched["authority_refs"] = dict(DENSE_65_AUTHORITY_REFS)
    enriched["truth"] = "OK"
    suffix = _shell_suffix(row["cell_id"])
    if suffix is not None:
        enriched["mu_code"] = suffix
        lock = DENSE_65_BUNDLE_LOCK[suffix]
        enriched["pole_set"] = list(lock["pole_set"])
        enriched["card"] = len(lock["pole_set"])
    if row["cell_family"] == "P":
        enriched["pole_set"] = [row["pole"]]
        enriched["card"] = 1
    if row["cell_family"] == "R":
        enriched["rot_plus"] = list(row["rot_plus_set"])
        enriched["rot_minus"] = list(row["rot_minus_set"])
        enriched["dense_transfer_signature"] = _dense_transfer_signature_for_row(row)
        enriched["dense_metro_witness"] = _dense_metro_witness_for_row(row)
    elif row["cell_family"] == "Q":
        enriched["dense_transfer_signature"] = _dense_transfer_signature_for_row(row)
        enriched["dense_metro_witness"] = _dense_metro_witness_for_row(row)
    elif row["cell_family"] == "T":
        enriched["hide_pole"] = row["hide_pole"]
        enriched["triad"] = list(row["triad_set"])
        enriched["base3_antispin_plus"] = [list(step) for step in row["anti_plus_orbit"]]
        enriched["base3_antispin_minus"] = [list(step) for step in row["anti_minus_orbit"]]
        enriched["dense_transfer_signature"] = _dense_transfer_signature_for_row(row)
        enriched["dense_metro_witness"] = _dense_metro_witness_for_row(row)
    return enriched


DENSE_65_SHELL_ROWS = [DENSE_65_HEADER_ROW, *[_enriched_shell_row(row) for row in DENSE_65_BASE_ROWS]]


def _route_key_for_cell_id(cell_id: str) -> str:
    if cell_id.startswith("T"):
        return "rtZ"
    return "rtZ" if cell_id[1:] in {"03", "30", "33"} else "rtL"


DENSE_65_CANONICAL_SEED_TABLE = {
    cell_id: {
        "record_id": cell_id,
        "family": family,
        "mu": mu,
        "bundle": f"B{mu}",
        "pole_set": list(DENSE_65_BUNDLE_LOCK[mu]["pole_set"]),
        "z_binding": DENSE_65_BUNDLE_LOCK[mu]["z_binding"],
        "check_key": DENSE_65_BUNDLE_LOCK[mu]["check_key"],
        "route_key": _route_key_for_cell_id(cell_id),
        "hidden_pole": T_LOOKUP[cell_id]["hide_pole"] if family == "T" else None,
    }
    for family in DENSE_65_CELL_FAMILIES
    for mu in DENSE_65_BUNDLE_LOCK
    for cell_id in [f"{family}{mu}"]
}


def _ascii_sha256(payload: str) -> str:
    return hashlib.sha256(payload.encode("ascii")).hexdigest()


def _record_label(cell_id: str) -> str:
    if cell_id.startswith("R"):
        return "rotation-pair"
    if cell_id.startswith("Q"):
        return "spin-orbit"
    return "antispin-orbit"


def _family_orbit_mechanics_ref(family: str) -> str:
    if family == "R":
        return (
            "ACTIVE_NERVOUS_SYSTEM/03_METRO/00_core_metro_map.md :: "
            "Ch07<0012> lawful transports, shadow-axis rotation, and typed tunnel semantics"
        )
    if family == "Q":
        return (
            "ACTIVE_NERVOUS_SYSTEM/03_METRO/00_core_metro_map.md :: "
            "Ch08<0013> synchronization calculus and lawful circulation"
        )
    return (
        "ACTIVE_NERVOUS_SYSTEM/04_CHAPTERS/Ch11_0022_void_book_and_restart_token_tunneling.md :: "
        "Ch11<0022> void book, restart token tunneling, and lawful antispin packaging"
    )


def _family_prior_route_witness(family: str) -> str:
    if family == "R":
        return (
            "ACTIVE_NERVOUS_SYSTEM/03_METRO/00_core_metro_map.md :: "
            "Ch07<0012> lawful transports, shadow-axis rotation, and typed tunnel semantics :: "
            "route-class=adjacent-bridge / tunnel-ready rotation pair"
        )
    if family == "Q":
        return (
            "ACTIVE_NERVOUS_SYSTEM/03_METRO/00_core_metro_map.md :: "
            "Ch08<0013> synchronization calculus and lawful circulation :: "
            "route-class=order-4 spin orbit / full-ring circulation"
        )
    return (
        "ACTIVE_NERVOUS_SYSTEM/04_CHAPTERS/Ch11_0022_void_book_and_restart_token_tunneling.md :: "
        "Ch11<0022> void book, restart token tunneling, and lawful antispin packaging :: "
        "route-class=order-3 antispin orbit / restart-safe residual packaging"
    )


def _transfer_coordinate_stamp(cell_row: dict[str, Any]) -> dict[str, Any]:
    shell_position = cell_row["shell_position"]
    slot_number = shell_position.split("/")[0]
    return {
        "Xs": "ACTIVE_NERVOUS_SYSTEM.18_LP_57OMEGA_PROTOCOL",
        "Ys": f"{cell_row['cell_family']}-shell",
        "Zs": f"slot-{slot_number}-of-65",
        "Ts": shell_position,
        "Qs": cell_row["cell_id"],
        "Rs": _record_label(cell_row["cell_id"]),
        "Cs": "active",
        "Fs": "flower",
        "Ms": "lp57omega-dense-shell",
        "Ns": "sigma-appa-appi-appm",
        "Hs": f"record:{cell_row['cell_id']}",
        "Omega_s": "NEAR-derived:active",
    }


def _aether_transfer_signature(cell_id: str) -> str:
    bindings = _orientation_bindings_for_cell(cell_id)
    family = cell_id[0]
    if family == "R":
        return (
            f"{bindings[0]['ae_coord']['canonical_key']} / {bindings[1]['ae_coord']['canonical_key']} "
            "bind the flower-lens rotation pair."
        )
    if family == "Q":
        return f"{bindings[0]['ae_coord']['canonical_key']} binds the flower-lens spin orbit."
    return f"{bindings[0]['ae_coord']['canonical_key']} binds the flower-lens residual antispin shell."


def _z_transfer_signature_text(spec: dict[str, Any]) -> str:
    if spec["family"] == "R":
        return (
            f"z={spec['z_binding']} with ck={spec['check_key']} and rt={spec['route_key']} "
            "preserves the lawful adjacent bridge under the A -> C -> B -> D ring."
        )
    if spec["family"] == "Q":
        return (
            f"z={spec['z_binding']} with ck={spec['check_key']} and rt={spec['route_key']} "
            "closes the q4 orbit without opposite-pole shortcut."
        )
    return (
        f"z={spec['z_binding']} with ck={spec['check_key']} and rt={spec['route_key']} "
        f"carries the t3 residual with hidden pole={spec['hidden_pole']}."
    )


def _packaging_status(family: str) -> str:
    if family == "T":
        return "flower-residual t3 shell"
    return "flower-core operator shell"


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    header = "| " + " | ".join(headers) + " |"
    separator = "| " + " | ".join("---" for _ in headers) + " |"
    body = ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join([header, separator, *body])


def _canonicalize_pole_list(values: list[str]) -> list[str]:
    deduped = []
    for pole in DENSE_65_RING_ORDER:
        if pole in values and pole not in deduped:
            deduped.append(pole)
    return deduped


def canonical_hide_pole(pole_set: list[str]) -> str:
    for pole in DENSE_65_RING_ORDER:
        if pole not in pole_set:
            return pole
    return "A"


def _normalize_face_to_pole(face: Any) -> str | None:
    if not face:
        return None
    key = str(face).strip().lower()
    if key in {"void", "aether"}:
        return None
    return POLE_FACE_MAP.get(key)


def _appendix_stack(route: dict[str, Any], cell_family: str) -> list[str]:
    stack = ["AppA", "AppI", "AppM"]
    for appendix in route.get("appendix_support") or []:
        if appendix not in stack:
            stack.append(appendix)
    if cell_family == "Q" and "AppF" not in stack:
        stack.append("AppF")
    if cell_family == "T":
        for appendix in ("AppF", "AppG"):
            if appendix not in stack:
                stack.append(appendix)
    return stack


def _compact_route_witness(route: dict[str, Any], witness_side: str) -> dict[str, Any]:
    return {
        "witness_side": witness_side,
        "route_id": route.get("route_id"),
        "prior_route_class": "record_matched_route",
        "prior_route_path": list(DENSE_65_SIGMA_PATH),
        "grand_central_exchange": route.get("grand_central_exchange"),
        "origin_system": route.get("origin_system"),
        "target_system": route.get("target_system"),
        "station_path": list(route.get("station_path") or []),
        "interlock_ids": list(route.get("interlock_ids") or []),
        "return_path": list(route.get("return_path") or []),
        "metro_line_ids": list(route.get("metro_line_ids") or []),
        "root_station_address": route.get("root_station_address"),
        "rail3": route.get("rail3"),
        "dominant_lens_system": route.get("dominant_lens_system"),
        "appendix_support": list(route.get("appendix_support") or []),
        "appf_rotation_ref": DENSE_65_AUTHORITY_REFS["rotation_authority"],
        "appg_antispin_ref": DENSE_65_AUTHORITY_REFS["antispin_authority"],
        "appi_truth_ref": DENSE_65_AUTHORITY_REFS["truth_lattice"],
        "appm_replay_ref": DENSE_65_AUTHORITY_REFS["replay_kernel"],
        "truth_state": route.get("truth_state") or route.get("proof_state") or "UNKNOWN",
    }


def _z_transfer_signature(
    route: dict[str, Any],
    coordinate_row: dict[str, Any],
    cell_family: str,
    cell_id: str,
    pole_set: list[str],
) -> dict[str, Any]:
    aether_point = route.get("aether_point") or {}
    liminal = route.get("liminal_vector") or {}
    tunnel_plan = route.get("tunnel_plan") or {}
    from_z = (
        tunnel_plan.get("from_z")
        or route.get("local_addr")
        or route.get("addr4")
        or route.get("root_station_address")
        or "UNSPECIFIED"
    )
    to_z = (
        tunnel_plan.get("to_z")
        or route.get("global_addr")
        or route.get("addr4")
        or route.get("root_station_address")
        or "UNSPECIFIED"
    )
    opposite_pairs = {("A", "B"), ("C", "D")}
    tunnel_required = any(
        left in pole_set and right in pole_set for left, right in opposite_pairs
    )
    if cell_family == "R":
        zstar_mode = "zstar_tunnel" if tunnel_required else "adjacent_bridge"
    elif cell_family == "Q":
        zstar_mode = "order_4_orbit_with_zstar" if tunnel_required else "order_4_orbit"
    else:
        zstar_mode = "order_3_antispin_with_zstar" if tunnel_required else "order_3_antispin"
    return {
        "record_id": cell_id,
        "zstar_mode": zstar_mode,
        "zstar_source": from_z,
        "zstar_target": to_z,
        "aether_binding": {
            "sigma_path": list(DENSE_65_SIGMA_PATH),
            "rotation_authority": DENSE_65_AUTHORITY_REFS["rotation_authority"],
            "antispin_authority": DENSE_65_AUTHORITY_REFS["antispin_authority"],
            "truth_lattice": DENSE_65_AUTHORITY_REFS["truth_lattice"],
            "replay_kernel": DENSE_65_AUTHORITY_REFS["replay_kernel"],
        },
        "opposite_pole_policy": "adjacent_bridge_or_zstar_tunnel_only",
        "tunnel_required": tunnel_required,
        "legality_class": "OK",
        "proof_ref": f"DenseKernel65::{cell_id} :: AppA -> AppI -> AppM",
        "from_z": from_z,
        "via": "Z*",
        "to_z": to_z,
        "zpoint_id": route.get("zpoint_id"),
        "field_id": route.get("field_id"),
        "geodesic_mode": route.get("geodesic_mode"),
        "aether_density": aether_point.get("aether_density"),
        "zero_proximity": aether_point.get("zero_proximity"),
        "tunnel_cost": aether_point.get("tunnel_cost"),
        "rail_hardness": aether_point.get("rail_hardness"),
        "resonance_pressure": aether_point.get("resonance_pressure"),
        "repair_gain": aether_point.get("repair_gain"),
        "appendix_stack": _appendix_stack(route, cell_family),
        "sigma_path": list(DENSE_65_SIGMA_PATH),
        "rotation_authority": DENSE_65_AUTHORITY_REFS["rotation_authority"],
        "antispin_authority": DENSE_65_AUTHORITY_REFS["antispin_authority"],
        "omega_relation": {
            "lp57_omega": (coordinate_row.get("coordinate_tuple") or {}).get("OMEGAs"),
            "route_omega": liminal.get("omega"),
            "route_integration": liminal.get("integration"),
        },
    }


def _order4_projection_summary(route: dict[str, Any]) -> dict[str, Any]:
    return {
        "addr4": route.get("addr4"),
        "face6": route.get("face6"),
        "arc7": route.get("arc7"),
        "rail3": route.get("rail3"),
        "dominant_lens_system": route.get("dominant_lens_system"),
    }


def _rail_antispin_lock(
    route: dict[str, Any],
    interlock_lookup: dict[str, dict[str, Any]],
    appendix_stack: list[str],
) -> dict[str, Any]:
    interlock_truths = []
    for interlock_id in route.get("interlock_ids") or []:
        interlock = interlock_lookup.get(interlock_id) or {}
        interlock_truths.append(
            {
                "interlock_id": interlock_id,
                "dispatch_score": interlock.get("dispatch_score"),
                "proof_state": interlock.get("proof_state"),
            }
        )
    return {
        "lock_mode": "order_3_antispin",
        "rail3": route.get("rail3"),
        "station_path": list(route.get("station_path") or []),
        "interlock_ids": list(route.get("interlock_ids") or []),
        "interlock_truths": interlock_truths,
        "orbit_appendices": appendix_stack,
        "truth_state": route.get("truth_state") or route.get("proof_state") or "UNKNOWN",
    }


def _derive_record_pole_set(
    record: dict[str, Any],
    pt2_face_lookup: dict[str, list[str]],
) -> list[str]:
    poles: list[str] = []
    for side in ("MATH", "MYTH"):
        route = (record.get("hemisphere_routes") or {}).get(side) or {}
        pole = _normalize_face_to_pole(route.get("face6"))
        if pole:
            poles.append(pole)
    for face in pt2_face_lookup.get(record.get("record_id") or "", []):
        pole = _normalize_face_to_pole(face)
        if pole:
            poles.append(pole)
    return _canonicalize_pole_list(poles)


def _build_witness_row(
    *,
    record: dict[str, Any],
    coordinate_row: dict[str, Any],
    pole_set: list[str],
    cell_family: str,
    cell_row: dict[str, Any],
    interlock_lookup: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    routes = record.get("hemisphere_routes") or {}
    primary_hemi = record.get("primary_hemisphere") or "MATH"
    secondary_hemi = "MYTH" if primary_hemi == "MATH" else "MATH"
    primary_route = routes.get(primary_hemi) or {}
    secondary_route = routes.get(secondary_hemi) or {}
    appendix_stack = _appendix_stack(primary_route, cell_family)
    row = {
        "cell_id": cell_row["cell_id"],
        "cell_family": cell_family,
        "shell_position": cell_row["shell_position"],
        "record_index": int(str(cell_row["shell_position"]).split("/")[0]),
        "record_kind": cell_family,
        "mu_code": _shell_suffix(cell_row["cell_id"]),
        "record_id": record.get("record_id"),
        "relative_path": record.get("relative_path"),
        "pole_set": pole_set,
        "hide_pole": canonical_hide_pole(pole_set) if cell_family == "T" else None,
        "primary_hemisphere": primary_hemi,
        "primary_route_id": primary_route.get("route_id"),
        "secondary_route_id": secondary_route.get("route_id"),
        "basis_anchor_ids": list(record.get("basis_anchor_ids") or []),
        "lp57_lookup_address": coordinate_row.get("lookup_address"),
        "dense_kernel_ref": _dense_kernel_binding(cell_row, pole_set),
        "sigma_path": list(DENSE_65_SIGMA_PATH),
        "authority_refs": dict(DENSE_65_AUTHORITY_REFS),
        "docs_gate_status": record.get("docs_gate_status"),
        "canonical_seed_refs": _canonical_seed_refs(cell_row["cell_id"]),
        "z_star_aether_transfer_signature": _z_transfer_signature(
            primary_route,
            coordinate_row,
            cell_family,
            cell_row["cell_id"],
            pole_set,
        ),
        "prior_metro_route_witness": _compact_route_witness(primary_route, primary_hemi),
        "counter_route_witness": _compact_route_witness(secondary_route, secondary_hemi),
        "truth_state": primary_route.get("truth_state") or primary_route.get("proof_state") or "UNKNOWN",
        "proof_state": primary_route.get("proof_state") or "UNKNOWN",
        "record_confidence": record.get("confidence"),
        "record_salience": record.get("salience"),
    }
    row["dense_transfer_signature"] = row["z_star_aether_transfer_signature"]
    row["dense_metro_witness"] = row["prior_metro_route_witness"]
    if cell_family == "R":
        row["rot_plus_set"] = list(cell_row["rot_plus_set"])
        row["rot_minus_set"] = list(cell_row["rot_minus_set"])
    elif cell_family == "Q":
        row["base4_orbit"] = [list(step) for step in cell_row["base4_orbit"]]
        row["order4_projection_summary"] = _order4_projection_summary(primary_route)
    elif cell_family == "T":
        row["triad_set"] = list(cell_row["triad_set"])
        row["triad"] = list(cell_row["triad_set"])
        row["anti_plus_orbit"] = [list(step) for step in cell_row["anti_plus_orbit"]]
        row["anti_minus_orbit"] = [list(step) for step in cell_row["anti_minus_orbit"]]
        row["base3_antispin_plus"] = [list(step) for step in cell_row["anti_plus_orbit"]]
        row["base3_antispin_minus"] = [list(step) for step in cell_row["anti_minus_orbit"]]
        row["rail_antispin_lock"] = _rail_antispin_lock(
            primary_route,
            interlock_lookup,
            appendix_stack,
        )
    return row


def _shell_registry(docs_gate_status: str) -> dict[str, Any]:
    return {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "overlay_mode": "kernel_overlay",
        "prior_seed_position": DENSE_65_PRIOR_SEED_POSITION,
        "header_record_id": DENSE_65_HEADER_ROW["record_id"],
        "ring_gauge": {
            "A": "Fire",
            "C": "Air",
            "B": "Water",
            "D": "Earth",
        },
        "ring_order": list(DENSE_65_RING_ORDER),
        "sigma_path": list(DENSE_65_SIGMA_PATH),
        "authority_refs": dict(DENSE_65_AUTHORITY_REFS),
        "hidden_pole_rule": "first missing pole in A -> C -> B -> D, default A",
        "opposite_pole_policy": "adjacent_bridge_or_zstar_tunnel_only",
        "row_count": len(DENSE_65_SHELL_ROWS),
        "group_counts": dict(DENSE_65_GROUP_COUNTS),
        "rows": _shell_rows_with_explicit_ae(),
    }


def _index_markdown(shell_registry: dict[str, Any], manifest: dict[str, Any]) -> str:
    rows = [
        [family, str(shell_registry["group_counts"][family])]
        for family in ("H", "P", "S", "R", "Q", "T")
    ]
    shell_rows = []
    for row in shell_registry["rows"]:
        family = row["cell_family"]
        if family == "H":
            payload = "prior seed/header shell"
        elif family == "P":
            payload = (
                f"{row['pole']}={row['label']} | θ={row['theta']} | rot+={row['rot_plus']} | "
                f"inv={row['inverse']} | rot-={row['rot_minus']} | z={row['z']} | ae={row['ae']}"
            )
        elif family == "S":
            payload = f"μ={row['mu']} | set={_format_pole_set(row['pole_set'])} | card={row['card']}"
        elif family == "R":
            payload = (
                f"src={_format_pole_set(row['src_set'])} | "
                f"rot+={_format_pole_set(row['rot_plus_set'])} | "
                f"rot-={_format_pole_set(row['rot_minus_set'])}"
            )
        elif family == "Q":
            orbit = " -> ".join(_format_pole_set(step) for step in row["base4_orbit"])
            payload = f"base4 orbit={orbit}"
        else:
            anti_plus = " -> ".join(_format_pole_set(step) for step in row["anti_plus_orbit"])
            anti_minus = " -> ".join(_format_pole_set(step) for step in row["anti_minus_orbit"])
            payload = (
                f"hide={row['hide_pole']} | triad={_format_pole_set(row['triad_set'])} | "
                f"anti+={anti_plus} | anti-={anti_minus}"
            )
        shell_rows.append([row["shell_position"], row["cell_id"], family, payload])
    return "\n".join(
        [
            "# Dense 65 Shell Index",
            "",
            f"- `prior_seed_position`: `{shell_registry['prior_seed_position']}`",
            f"- `header_record_id`: `{shell_registry['header_record_id']}`",
            f"- `docs_gate_status`: `{manifest['docs_gate_status']}`",
            f"- sealed shell rows: `{shell_registry['row_count']}`",
            f"- sigma path: `{' -> '.join(shell_registry['sigma_path'])}`",
            f"- rotation authority: `{shell_registry['authority_refs']['rotation_authority']}`",
            f"- antispin authority: `{shell_registry['authority_refs']['antispin_authority']}`",
            f"- hidden pole rule: `{shell_registry['hidden_pole_rule']}`",
            f"- primary witness cap per cell: `{manifest['primary_cap_per_cell']}`",
            f"- matched records: `{manifest['coverage']['matched_records']}`",
            f"- abstained records: `{manifest['coverage']['abstained_records']}`",
            "",
            markdown_table(["Family", "Row Count"], rows),
            "",
            "## Sealed Shell",
            "",
            markdown_table(["Address", "Record", "Family", "Payload"], shell_rows),
            "",
            "## Outputs",
            "",
            f"- shell registry: `{DENSE_65_SHELL_REGISTRY_PATH.name}`",
            f"- primary witness registry: `{DENSE_65_RQT_WITNESS_REGISTRY_PATH.name}`",
            f"- overflow registry: `{DENSE_65_RQT_OVERFLOW_REGISTRY_PATH.name}`",
            f"- manifest: `{DENSE_65_MANIFEST_PATH.name}`",
        ]
    )


def _cell_markdown(
    *,
    title: str,
    family: str,
    registry: dict[str, Any],
    lookup: dict[str, dict[str, Any]],
) -> str:
    cell_rows = []
    for summary in registry["cell_summaries"]:
        if summary["cell_family"] != family:
            continue
        cell_id = summary["cell_id"]
        overlay = lookup[cell_id]
        witness_rows = summary["primary_rows"]
        if family == "R":
            detail = f"rot+={overlay['rot_plus_set']} | rot-={overlay['rot_minus_set']}"
        elif family == "Q":
            detail = f"orbit={overlay['base4_orbit']}"
        else:
            detail = (
                f"hide={overlay['hide_pole']} | triad={overlay['triad_set']} | "
                f"anti+={overlay['anti_plus_orbit']} | anti-={overlay['anti_minus_orbit']}"
            )
        cell_rows.extend(
            [
                f"## {cell_id}",
                "",
                f"- shell position: `{overlay['shell_position']}`",
                f"- definition: `{detail}`",
                f"- primary witness count: `{summary['primary_count']}`",
                f"- overflow count: `{summary['overflow_count']}`",
                "",
            ]
        )
        if witness_rows:
            table_rows = [
                [
                    row["record_id"],
                    row["relative_path"],
                    ",".join(row["pole_set"]),
                    row["primary_hemisphere"],
                    row["prior_metro_route_witness"]["target_system"] or "-",
                    row["z_star_aether_transfer_signature"]["zpoint_id"] or "-",
                ]
                for row in witness_rows
            ]
            cell_rows.append(
                markdown_table(
                    ["Record", "Path", "Poles", "Primary", "Target System", "Z-Point"],
                    table_rows,
                )
            )
        else:
            cell_rows.append("_No lawful primary witnesses yet._")
        cell_rows.append("")
    return "\n".join([f"# {title}", "", *cell_rows]).rstrip() + "\n"


def _coverage_markdown(
    *,
    manifest: dict[str, Any],
    witness_registry: dict[str, Any],
    overflow_registry: dict[str, Any],
) -> str:
    rows = []
    for summary in witness_registry["cell_summaries"]:
        rows.append(
            [
                summary["cell_id"],
                summary["cell_family"],
                str(summary["primary_count"]),
                str(summary["overflow_count"]),
                "yes" if summary["zero_witness"] else "no",
            ]
        )
    zero_cells = ", ".join(manifest["coverage"]["zero_witness_cells"]) or "none"
    return "\n".join(
        [
            "# Dense 65 Coverage And Overflow Receipt",
            "",
            f"- `docs_gate_status`: `{manifest['docs_gate_status']}`",
            f"- matched records: `{manifest['coverage']['matched_records']}`",
            f"- abstained records: `{manifest['coverage']['abstained_records']}`",
            f"- primary witness rows: `{witness_registry['row_count']}`",
            f"- overflow witness rows: `{overflow_registry['overflow_count']}`",
            f"- zero-witness cells: `{zero_cells}`",
            "",
            markdown_table(
                ["Cell", "Family", "Primary", "Overflow", "Zero Witness"],
                rows,
            ),
        ]
    )


def build_dense_65_payloads(
    *,
    full_corpus_authority_registry: dict[str, Any],
    lp57omega_coordinate_registry: dict[str, Any],
    docs_gate_status: str,
) -> dict[str, Any]:
    shell_registry = _shell_registry(docs_gate_status)
    coordinate_lookup = {
        row["record_id"]: row for row in lp57omega_coordinate_registry.get("rows", [])
    }
    pt2_holo = load_json(SELF_ACTUALIZE_ROOT / "phase4_pt2_holo_coordinate_registry.json")
    pt2_aether = load_json(SELF_ACTUALIZE_ROOT / "phase4_pt2_aether_point_registry.json")
    pt2_interlocks = load_json(PT2_METRO_INTERLOCKS_PATH)
    pt2_face_lookup: dict[str, list[str]] = defaultdict(list)
    for row in pt2_holo.get("coordinates", []):
        record_id = row.get("record_id")
        if record_id and row.get("face6"):
            pt2_face_lookup[record_id].append(row["face6"])
    interlock_lookup = {
        row.get("interlock_id"): row
        for row in pt2_interlocks.get("interlocks", [])
        if row.get("interlock_id")
    }

    cell_candidates: dict[str, list[dict[str, Any]]] = {
        row["cell_id"]: [] for row in [*DENSE_65_R_ROWS, *DENSE_65_Q_ROWS, *DENSE_65_T_ROWS]
    }
    abstention_rows: list[dict[str, Any]] = []

    for record in full_corpus_authority_registry.get("records", []):
        pole_set = _derive_record_pole_set(record, pt2_face_lookup)
        if not pole_set:
            abstention_rows.append(
                {
                    "record_id": record.get("record_id"),
                    "relative_path": record.get("relative_path"),
                    "overflow_reason": "no_elemental_pole_evidence",
                    "docs_gate_status": docs_gate_status,
                }
            )
            continue
        suffix = SET_TO_SUFFIX.get(tuple(pole_set))
        coordinate_row = coordinate_lookup.get(record.get("record_id") or "")
        if not suffix or coordinate_row is None:
            abstention_rows.append(
                {
                    "record_id": record.get("record_id"),
                    "relative_path": record.get("relative_path"),
                    "pole_set": pole_set,
                    "overflow_reason": "missing_cell_mapping_or_coordinate",
                    "docs_gate_status": docs_gate_status,
                }
            )
            continue
        for cell_family, lookup in (("R", R_LOOKUP), ("Q", Q_LOOKUP), ("T", T_LOOKUP)):
            cell_id = f"{cell_family}{suffix}"
            witness = _build_witness_row(
                record=record,
                coordinate_row=coordinate_row,
                pole_set=pole_set,
                cell_family=cell_family,
                cell_row=lookup[cell_id],
                interlock_lookup=interlock_lookup,
            )
            cell_candidates[cell_id].append(witness)

    witness_rows: list[dict[str, Any]] = []
    overflow_rows: list[dict[str, Any]] = []
    cell_summaries: list[dict[str, Any]] = []
    zero_witness_cells: list[str] = []

    for cell_id, candidates in sorted(cell_candidates.items()):
        ordered = sorted(
            candidates,
            key=lambda row: (
                -PROOF_RANK.get(row.get("truth_state"), 0),
                -PROOF_RANK.get(row.get("proof_state"), 0),
                -(row.get("record_confidence") or 0.0),
                -(row.get("record_salience") or 0.0),
                row.get("relative_path") or "",
            ),
        )
        primaries = ordered[:DENSE_65_PRIMARY_CAP]
        extras = ordered[DENSE_65_PRIMARY_CAP:]
        witness_rows.extend(primaries)
        for overflow_rank, row in enumerate(extras, start=1):
            overflow_rows.append(
                {
                    **row,
                    "overflow_rank": overflow_rank,
                    "overflow_reason": "capacity",
                }
            )
        if not primaries:
            zero_witness_cells.append(cell_id)
        cell_summaries.append(
            {
                "cell_id": cell_id,
                "cell_family": cell_id[0],
                "primary_count": len(primaries),
                "overflow_count": len(extras),
                "zero_witness": not primaries,
                "primary_rows": primaries,
            }
        )

    witness_registry = {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "overlay_mode": "kernel_overlay",
        "header_record_id": DENSE_65_HEADER_ROW["record_id"],
        "sigma_path": list(DENSE_65_SIGMA_PATH),
        "authority_refs": dict(DENSE_65_AUTHORITY_REFS),
        "primary_cap_per_cell": DENSE_65_PRIMARY_CAP,
        "row_count": len(witness_rows),
        "cell_summaries": cell_summaries,
        "rows": witness_rows,
    }
    overflow_registry = {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "overflow_count": len(overflow_rows),
        "abstention_count": len(abstention_rows),
        "overflow_rows": overflow_rows,
        "abstention_rows": abstention_rows,
    }
    coverage = {
        "matched_records": len({row["record_id"] for row in witness_rows}),
        "abstained_records": len(abstention_rows),
        "zero_witness_cells": zero_witness_cells,
        "per_cell_primary_counts": {
            row["cell_id"]: row["primary_count"] for row in cell_summaries
        },
        "per_cell_overflow_counts": {
            row["cell_id"]: row["overflow_count"] for row in cell_summaries
        },
        "pt2_holo_coordinate_count": len(pt2_holo.get("coordinates", [])),
        "pt2_aether_point_count": len(pt2_aether.get("aether_points", [])),
        "pt2_interlock_count": len(pt2_interlocks.get("interlocks", [])),
    }
    manifest = {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "overlay_mode": "kernel_overlay",
        "header_record_id": DENSE_65_HEADER_ROW["record_id"],
        "sigma_path": list(DENSE_65_SIGMA_PATH),
        "authority_refs": dict(DENSE_65_AUTHORITY_REFS),
        "primary_cap_per_cell": DENSE_65_PRIMARY_CAP,
        "counts": {
            "shell_rows": shell_registry["row_count"],
            "primary_witness_rows": witness_registry["row_count"],
            "overflow_rows": overflow_registry["overflow_count"],
            "abstention_rows": overflow_registry["abstention_count"],
        },
        "coverage": coverage,
        "output_paths": {
            "shell_registry": str(DENSE_65_SHELL_REGISTRY_PATH),
            "witness_registry": str(DENSE_65_RQT_WITNESS_REGISTRY_PATH),
            "overflow_registry": str(DENSE_65_RQT_OVERFLOW_REGISTRY_PATH),
            "manifest": str(DENSE_65_MANIFEST_PATH),
        },
    }
    markdown_pages = {
        "dense_65_shell_index": _index_markdown(shell_registry, manifest),
        "dense_65_r_atlas": _cell_markdown(
            title="Dense 65 R Witness Atlas",
            family="R",
            registry=witness_registry,
            lookup=R_LOOKUP,
        ),
        "dense_65_q_atlas": _cell_markdown(
            title="Dense 65 Q Orbit Atlas",
            family="Q",
            registry=witness_registry,
            lookup=Q_LOOKUP,
        ),
        "dense_65_t_atlas": _cell_markdown(
            title="Dense 65 T Antispin Atlas",
            family="T",
            registry=witness_registry,
            lookup=T_LOOKUP,
        ),
        "dense_65_coverage": _coverage_markdown(
            manifest=manifest,
            witness_registry=witness_registry,
            overflow_registry=overflow_registry,
        ),
    }
    return {
        "shell_registry": shell_registry,
        "witness_registry": witness_registry,
        "overflow_registry": overflow_registry,
        "manifest": manifest,
        "markdown_pages": markdown_pages,
    }


def _ae_coord(*, phase_id: str, bundle: str, slot: str, hidden_pole: str | None = None) -> dict[str, Any]:
    phase_label = DENSE_65_PHASE_BINS.get(phase_id, phase_id)
    canonical_key = f"AE=({DENSE_65_FLOWER_LENS},{phase_label},{bundle};{slot})"
    if hidden_pole:
        canonical_key = f"AE=({DENSE_65_FLOWER_LENS},{phase_label},{bundle}:h={hidden_pole};{slot})"
    payload: dict[str, Any] = {
        "Lens": DENSE_65_FLOWER_LENS,
        "Phase": phase_label,
        "Bundle": bundle,
        "Slot": slot,
        "lens": DENSE_65_FLOWER_LENS,
        "phase": phase_label,
        "phase_id": phase_id,
        "phase_label": phase_label,
        "bundle": bundle,
        "slot": slot,
        "canonical_key": canonical_key,
    }
    if hidden_pole:
        payload["hidden_pole"] = hidden_pole
        payload["HiddenPole"] = hidden_pole
    return payload


def _binding_witness_seed(
    seed_id: str,
    ae_coord: dict[str, Any],
    z_binding: str,
    check_key: str,
    route_key: str,
) -> dict[str, Any]:
    seed_payload = "|".join([seed_id, ae_coord["canonical_key"], z_binding, check_key, route_key])
    return {
        "seed_id": seed_id,
        "type": "INTERNAL_SLICE",
        "location": ae_coord,
        "hash": _ascii_sha256(seed_payload),
        "scope": ["OPS", "DEFINE", "SYSTEM"],
        "timestamp": DENSE_65_TICK_2B,
        "collector": "SYSTEM",
        "version_pins": DENSE_65_VERSION_PINS_2B,
    }


def _binding_replay_seed(
    seed_id: str,
    ae_coord: dict[str, Any],
    z_binding: str,
    check_key: str,
    route_key: str,
) -> dict[str, Any]:
    seed_payload = "|".join([seed_id, ae_coord["canonical_key"], DENSE_65_ENV_PIN_2B])
    return {
        "seed_id": seed_id,
        "inputs": {
            "ae_coord": ae_coord,
            "z_binding": z_binding,
            "check_key": check_key,
            "route_key": route_key,
        },
        "steps": list(DENSE_65_REPLAY_STEPS),
        "expected_outputs": {
            "ae_coord": ae_coord,
            "z_binding": z_binding,
            "check_key": check_key,
            "route_key": route_key,
            "slot": ae_coord["slot"],
        },
        "checks": list(DENSE_65_REPLAY_CHECKS),
        "env_pin": DENSE_65_ENV_PIN_2B,
        "hash": _ascii_sha256(seed_payload),
    }


def _orientation_bindings_for_cell(cell_id: str) -> list[dict[str, Any]]:
    spec = DENSE_65_CANONICAL_SEED_TABLE[cell_id]
    bundle = spec["bundle"]
    if spec["family"] == "R":
        orientation_specs = [("plus", "Phi0", "Core", None), ("minus", "Phi1", "Core", None)]
    elif spec["family"] == "Q":
        orientation_specs = [("spin", "Phi2", "Core", None)]
    else:
        orientation_specs = [("antispin", "Phi3", "Residual", spec["hidden_pole"])]

    bindings: list[dict[str, Any]] = []
    for orientation_name, phase_id, slot, hidden_pole in orientation_specs:
        ae_coord = _ae_coord(
            phase_id=phase_id,
            bundle=bundle,
            slot=slot,
            hidden_pole=hidden_pole,
        )
        pointer_id = (
            f"{cell_id}:+" if orientation_name == "plus"
            else f"{cell_id}:-" if orientation_name == "minus"
            else f"{cell_id}:{orientation_name}"
        )
        witness_seed_id = (
            f"WS[{cell_id},+]" if orientation_name == "plus"
            else f"WS[{cell_id},-]" if orientation_name == "minus"
            else f"WS[{cell_id}]"
        )
        replay_seed_id = (
            f"RS[{cell_id},+]" if orientation_name == "plus"
            else f"RS[{cell_id},-]" if orientation_name == "minus"
            else f"RS[{cell_id}]"
        )
        witness_ptr = _binding_witness_seed(
            witness_seed_id,
            ae_coord,
            spec["z_binding"],
            spec["check_key"],
            spec["route_key"],
        )
        replay_ptr = _binding_replay_seed(
            replay_seed_id,
            ae_coord,
            spec["z_binding"],
            spec["check_key"],
            spec["route_key"],
        )
        bindings.append(
            {
                "pointer_id": pointer_id,
                "binding_id": pointer_id,
                "binding_key": orientation_name,
                "AE": {
                    "lens": ae_coord["lens"],
                    "phase": ae_coord["phase"],
                    "bundle": ae_coord["bundle"],
                    "slot": ae_coord["slot"],
                    **({"hidden_pole": ae_coord["hidden_pole"]} if "hidden_pole" in ae_coord else {}),
                },
                "Location": ae_coord["canonical_key"],
                "phase_id": ae_coord["phase_id"],
                "phase_label": ae_coord["phase_label"],
                "orientation": orientation_name,
                "hidden_pole": hidden_pole,
                "slot": slot,
                "WitnessPtr": witness_ptr,
                "ReplayPtr": replay_ptr,
                "z": spec["z_binding"],
                "checkpoint": spec["check_key"],
                "route_id": spec["route_key"],
                "route_path": DENSE_65_ROUTE_KEYS[spec["route_key"]],
                "orientation_id": pointer_id,
                "orientation_name": orientation_name,
                "ae_coord": ae_coord,
                "ae_token": ae_coord["canonical_key"],
                "z_binding": spec["z_binding"],
                "z_expanded": "+".join(DENSE_65_Z_KEYS[token] for token in spec["z_binding"].split("+")),
                "check_key": spec["check_key"],
                "route_key": spec["route_key"],
                "witness_seed_id": witness_seed_id,
                "replay_seed_id": replay_seed_id,
                "WitnessPtr": witness_ptr,
                "ReplayPtr": replay_ptr,
                "witness_seed": witness_ptr,
                "replay_seed": replay_ptr,
            }
        )
    return bindings


def _canonical_seed_refs(cell_id: str) -> list[dict[str, str]]:
    return [
        {
            "orientation_id": binding["binding_id"],
            "witness_seed_id": binding["witness_seed_id"],
            "replay_seed_id": binding["replay_seed_id"],
            "canonical_key": binding["ae_coord"]["canonical_key"],
        }
        for binding in _orientation_bindings_for_cell(cell_id)
    ]


def _shell_rows_with_explicit_ae() -> list[dict[str, Any]]:
    rows = [{**DENSE_65_HEADER_ROW}]
    rows.extend(_enriched_shell_row(row) for row in DENSE_65_P_ROWS)
    rows.extend(_enriched_shell_row(row) for row in DENSE_65_S_ROWS)
    for group in (DENSE_65_R_ROWS, DENSE_65_Q_ROWS, DENSE_65_T_ROWS):
        for row in group:
            spec = DENSE_65_CANONICAL_SEED_TABLE[row["cell_id"]]
            rows.append(
                {
                    **_enriched_shell_row(row),
                    "mu": spec["mu"],
                    "ae_bindings": [
                        {
                            "orientation_id": binding["orientation_id"],
                            "ae_coord": binding["ae_coord"],
                        }
                        for binding in _orientation_bindings_for_cell(row["cell_id"])
                    ],
                    "explicit_aether_coordinates": [
                        {
                            "pointer_id": binding["pointer_id"],
                            "orientation": binding["orientation"],
                            "phase_id": binding["phase_id"],
                            "phase_label": binding["phase_label"],
                            "ae_coord": binding["ae_coord"],
                            "ae_token": binding["ae_token"],
                        }
                        for binding in _orientation_bindings_for_cell(row["cell_id"])
                    ],
                }
            )
    return rows


def _compressed_orientation_bindings(bindings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "pointer_id": binding["pointer_id"],
            "binding_id": binding["binding_id"],
            "binding_key": binding["binding_key"],
            "AE": binding["AE"],
            "Location": binding["Location"],
            "orientation": binding["orientation"],
            "phase_id": binding["phase_id"],
            "phase_label": binding["phase_label"],
            "slot": binding["slot"],
            "ae_token": binding["ae_token"],
            "hidden_pole": binding["hidden_pole"],
            "z": binding["z"],
            "checkpoint": binding["checkpoint"],
            "route_id": binding["route_id"],
            "route_path": binding["route_path"],
            "orientation_id": binding["orientation_id"],
            "orientation_name": binding["orientation_name"],
            "ae_coord": binding["ae_coord"],
            "z_binding": binding["z_binding"],
            "z_expanded": binding["z_expanded"],
            "check_key": binding["check_key"],
            "route_key": binding["route_key"],
            "witness_seed_id": binding["witness_seed_id"],
            "replay_seed_id": binding["replay_seed_id"],
            "WitnessPtr": binding["WitnessPtr"],
            "ReplayPtr": binding["ReplayPtr"],
            "witness_seed": binding["witness_seed"],
            "replay_seed": binding["replay_seed"],
        }
        for binding in bindings
    ]


def _full_pointer_records(transfer_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "record_id": record["record_id"],
            "record_type": record["record_type"],
            "shell_slot": record["shell_slot"],
            "shell_slot_label": record["shell_slot_label"],
            "mu": record["mu"],
            "bundle": record["bundle"],
            "source_set": record["source_set"],
            "z_binding": record["z_binding"],
            "z_alias": record["z_binding"],
            "z_expanded": record["z_expanded"],
            "check_key": record["check_key"],
            "ck": record["check_key"],
            "route_key": record["route_key"],
            "rt": record["route_key"],
            "route_path": record["route_path"],
            "rt_path": record["route_path"],
            "hidden_pole": record["hidden_pole"],
            "packaging_status": record["packaging_status"],
            "coordinate_stamp": record["coordinate_stamp"],
            "pointers": record["full_pointer_bindings"],
        }
        for record in transfer_records
    ]


def build_dense_65_canonical_payloads(docs_gate_status: str) -> dict[str, Any]:
    shell_registry = {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "prior_seed_position": DENSE_65_PRIOR_SEED_POSITION,
        "row_count": len(DENSE_65_SHELL_ROWS),
        "group_counts": DENSE_65_GROUP_COUNTS,
        "rows": _shell_rows_with_explicit_ae(),
    }
    transfer_records = []
    for cell_row in [*DENSE_65_R_ROWS, *DENSE_65_Q_ROWS, *DENSE_65_T_ROWS]:
        spec = DENSE_65_CANONICAL_SEED_TABLE[cell_row["cell_id"]]
        full_pointer_bindings = _orientation_bindings_for_cell(cell_row["cell_id"])
        transfer_records.append(
            {
                "record_id": cell_row["cell_id"],
                "shell_slot": int(cell_row["shell_position"].split("/")[0]),
                "shell_slot_label": cell_row["shell_position"],
                "record_type": spec["family"],
                "mu": spec["mu"],
                "bundle": spec["bundle"],
                "source_set": list(spec["pole_set"]),
                "z_binding": spec["z_binding"],
                "z_expanded": "+".join(DENSE_65_Z_KEYS[token] for token in spec["z_binding"].split("+")),
                "check_key": spec["check_key"],
                "route_key": spec["route_key"],
                "z": spec["z_binding"],
                "checkpoint": spec["check_key"],
                "route_id": spec["route_key"],
                "route_path": DENSE_65_ROUTE_KEYS[spec["route_key"]],
                "hidden_pole": spec["hidden_pole"],
                "sigma_path": ["AppA", "AppI", "AppM"],
                "orbit_mechanics_ref": _family_orbit_mechanics_ref(spec["family"]),
                "z_transfer_signature": _z_transfer_signature_text(spec),
                "aether_transfer_signature": _aether_transfer_signature(cell_row["cell_id"]),
                "prior_metro_route_witness": _family_prior_route_witness(spec["family"]),
                "truth_status": "NEAR-derived",
                "packaging_status": _packaging_status(spec["family"]),
                "coordinate_stamp": _transfer_coordinate_stamp(cell_row),
                "phase_bindings": _compressed_orientation_bindings(full_pointer_bindings),
                "full_pointer_bindings": full_pointer_bindings,
            }
        )
        transfer_records[-1]["phase_binding_count"] = len(transfer_records[-1]["phase_bindings"])
        transfer_records[-1]["orientation_bindings"] = transfer_records[-1]["phase_bindings"]
    transfer_registry = {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "protocol_id": "LP-57OMEGA",
        "truth_status": "NEAR-derived",
        "sigma_path": ["AppA", "AppI", "AppM"],
        "base3_antispin_lock": "deterministic packaging choice layered on top of corpus law",
        "flower_lens": DENSE_65_FLOWER_LENS,
        "phase_bins": dict(DENSE_65_PHASE_BINS),
        "route_constants": dict(DENSE_65_ROUTE_KEYS),
        "z_constants": dict(DENSE_65_Z_KEYS),
        "tick_constant": DENSE_65_TICK_2B,
        "version_pin_constant": DENSE_65_VERSION_PINS_2B,
        "env_pin_constant": DENSE_65_ENV_PIN_2B,
        "enriched_transfer_record_count": len(transfer_records),
        "orientation_binding_count": sum(len(record["orientation_bindings"]) for record in transfer_records),
        "phase_binding_count": sum(len(record["phase_bindings"]) for record in transfer_records),
        "concrete_pointer_count": sum(len(record["full_pointer_bindings"]) for record in transfer_records),
        "records": transfer_records,
    }
    pointer_records = _full_pointer_records(transfer_records)
    pointer_registry = {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "protocol_id": "LP-57OMEGA",
        "truth_status": "NEAR-derived",
        "record_count": len(pointer_records),
        "concrete_pointer_count": sum(len(record["pointers"]) for record in pointer_records),
        "aether_lattice_abi": {
            "lens": DENSE_65_FLOWER_LENS,
            "lens_label": DENSE_65_FLOWER_LENS_LABEL,
            "phase_bins": dict(DENSE_65_PHASE_BINS),
            "slots": list(DENSE_65_AETHER_SLOTS),
            "slot_policy": {"R": "Core", "Q": "Core", "T": "Residual"},
            "bundles": [f"B{mu}" for mu in DENSE_65_BUNDLE_LOCK],
        },
        "sigma_path": list(DENSE_65_SIGMA_PATH),
        "rotation_carriers": [
            DENSE_65_AUTHORITY_REFS["rotation_authority"],
            DENSE_65_AUTHORITY_REFS["antispin_authority"],
        ],
        "route_constants": dict(DENSE_65_ROUTE_KEYS),
        "z_constants": dict(DENSE_65_Z_KEYS),
        "witness_lock": {
            "type": "INTERNAL_SLICE",
            "scope": ["OPS", "DEFINE", "SYSTEM"],
            "timestamp": DENSE_65_TICK_2B,
            "collector": "SYSTEM",
            "version_pins": DENSE_65_VERSION_PINS_2B,
        },
        "replay_lock": {
            "steps": list(DENSE_65_REPLAY_STEPS),
            "checks": list(DENSE_65_REPLAY_CHECKS),
            "env_pin": DENSE_65_ENV_PIN_2B,
        },
        "records": pointer_records,
    }
    pointer_schema = {
        "protocol_id": "LP-57OMEGA",
        "title": "LP-57Omega AETHER Witness/Replay Pointer Schema",
        "record_count": 45,
        "concrete_pointer_count": 60,
        "pointer_record_required": [
            "record_id",
            "record_type",
            "bundle",
            "source_set",
            "z_alias",
            "z_expanded",
            "ck",
            "rt",
            "rt_path",
            "pointers",
        ],
        "pointer_binding_required": [
            "orientation_id",
            "ae_coord",
            "z_binding",
            "check_key",
            "route_key",
            "witness_seed",
            "replay_seed",
        ],
        "witness_seed_required": [
            "seed_id",
            "type",
            "location",
            "hash",
            "scope",
            "timestamp",
            "collector",
            "version_pins",
        ],
        "replay_seed_required": [
            "seed_id",
            "inputs",
            "steps",
            "expected_outputs",
            "checks",
            "env_pin",
            "hash",
        ],
    }
    return {
        "shell_registry": shell_registry,
        "transfer_registry": transfer_registry,
        "pointer_registry": pointer_registry,
        "pointer_schema": pointer_schema,
    }
