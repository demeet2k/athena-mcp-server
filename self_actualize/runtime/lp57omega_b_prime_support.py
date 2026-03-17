from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from self_actualize.runtime.hemisphere_brain_support import (
    FLEET_MIRROR_ROOT,
    HEMISPHERE_ROOT,
    REGISTRY_ROOT,
    SELF_ACTUALIZE_ROOT,
    load_docs_gate_status,
    load_json,
    utc_now,
    write_json,
    write_text,
)


B_PRIME_REGISTRY_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_lp57omega_b_prime_witness_registry.json"
)
B_PRIME_REGISTRY_MIRROR = REGISTRY_ROOT / B_PRIME_REGISTRY_PATH.name
B_PRIME_DOC_PATH = (
    HEMISPHERE_ROOT / "91_lp57omega_b_prime_witnessed_inversion_shell.md"
)
B_PRIME_DOC_MIRROR = FLEET_MIRROR_ROOT / B_PRIME_DOC_PATH.name
B_PRIME_MANIFEST_REPORT_PATH = (
    SELF_ACTUALIZE_ROOT / "lp57omega_b_prime_witness_verification.json"
)

LP57OMEGA_MANIFEST_PATH = SELF_ACTUALIZE_ROOT / "myth_math_lp57omega_manifest.json"
LP57OMEGA_MANIFEST_MIRROR = REGISTRY_ROOT / LP57OMEGA_MANIFEST_PATH.name
LP57OMEGA_MANIFEST_FLEET_MIRROR = FLEET_MIRROR_ROOT / LP57OMEGA_MANIFEST_PATH.name
LP57OMEGA_INDEX_PATH = HEMISPHERE_ROOT / "85_lp57omega_protocol_index.md"
LP57OMEGA_INDEX_MIRROR = FLEET_MIRROR_ROOT / LP57OMEGA_INDEX_PATH.name
LP57OMEGA_DEEP_CONTROL_PATH = (
    SELF_ACTUALIZE_ROOT
    / "mycelium_brain"
    / "dynamic_neural_network"
    / "14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK"
    / "00_CONTROL"
    / "13_LP57OMEGA_PROTOCOL.md"
)
LP57OMEGA_DEEP_CONTROL_MIRROR = FLEET_MIRROR_ROOT / LP57OMEGA_DEEP_CONTROL_PATH.name

SIGMA_ROUTE = "AppA -> AppI -> AppM"
AETHER_LENS = "F"
PHI_0 = "Φ0"
PHI_1 = "Φ1"
PHI_2 = "Φ2"
PHI_3 = "Φ3"

SUMMARY_WITNESS_FIELDS = [
    "parent_route",
    "transfer_mode",
    "tunnel_class",
    "aether_state",
    "entry_condition",
    "exit_condition",
]
WITNESS_SEED_FIELDS = [
    "id",
    "type",
    "location",
    "hash",
    "scope",
    "timestamp",
    "collector",
    "version_pins",
]
REPLAY_SEED_FIELDS = [
    "id",
    "inputs",
    "steps",
    "expected_outputs",
    "checks",
    "env_pin",
    "hash",
]
EXPECTED_OUTPUT_FIELDS = [
    "location_match",
    "slot_match",
    "z_match",
    "checkpoint_match",
    "route_match",
    "sigma_satisfied",
    "hub_budget_satisfied",
]
POINTER_SCOPE = ["OPS", "DEFINE", "SYSTEM"]
REPLAY_STEPS = ["ResolveZ", "ExpandAE", "RouteV2", "SlotCheck"]
REPLAY_CHECKS = ["Sigma", "Hub<=6", "ZMatch"]

ROUTE_PINS = {
    "rtL": {
        "alias": "rtL",
        "id": "Sigma-F-N-21",
        "resolved": "AppA>AppI>AppM>AppF>AppN>Ch21⟨0110⟩",
    },
    "rtZ": {
        "alias": "rtZ",
        "id": "Sigma-F-G-21",
        "resolved": "AppA>AppI>AppM>AppF>AppG>Ch21⟨0110⟩",
    },
}
ROUTE_ALIASES = {alias: payload["resolved"] for alias, payload in ROUTE_PINS.items()}
Z_ALIASES = {
    "ZA": "Z(Fire)",
    "ZB": "Z(Water)",
    "ZC": "Z(Air)",
    "ZD": "Z(Earth)",
}
PHASE_DEFS = {
    "R_PLUS": {"bin": PHI_0, "alias": "R+"},
    "R_MINUS": {"bin": PHI_1, "alias": "R-"},
    "Q4": {"bin": PHI_2, "alias": "Q4"},
    "T3": {"bin": PHI_3, "alias": "T3"},
}
SHARED_PINS = {
    "timestamp": "Tick_2B",
    "version_pins": "V_2B",
    "env_pin": "E_2B",
}

POLE_ROWS = [
    {"address": "2/65", "record_id": "P0", "pole": "A", "element": "Fire", "theta": "0°", "rot_plus": "C", "inv": "B", "rot_minus": "D", "z": "Z(Fire)", "ae": "AE[F]"},
    {"address": "3/65", "record_id": "P2", "pole": "B", "element": "Water", "theta": "180°", "rot_plus": "D", "inv": "A", "rot_minus": "C", "z": "Z(Water)", "ae": "AE[W]"},
    {"address": "4/65", "record_id": "P1", "pole": "C", "element": "Air", "theta": "90°", "rot_plus": "B", "inv": "D", "rot_minus": "A", "z": "Z(Air)", "ae": "AE[A]"},
    {"address": "5/65", "record_id": "P3", "pole": "D", "element": "Earth", "theta": "270°", "rot_plus": "A", "inv": "C", "rot_minus": "B", "z": "Z(Earth)", "ae": "AE[E]"},
]

SYMMETRY_ROWS = [
    {"address": "6/65", "record_id": "S01", "mu": "01", "set": ["A"], "card": 1},
    {"address": "7/65", "record_id": "S02", "mu": "02", "set": ["B"], "card": 1},
    {"address": "8/65", "record_id": "S03", "mu": "03", "set": ["A", "B"], "card": 2},
    {"address": "9/65", "record_id": "S10", "mu": "10", "set": ["C"], "card": 1},
    {"address": "10/65", "record_id": "S11", "mu": "11", "set": ["A", "C"], "card": 2},
    {"address": "11/65", "record_id": "S12", "mu": "12", "set": ["B", "C"], "card": 2},
    {"address": "12/65", "record_id": "S13", "mu": "13", "set": ["A", "B", "C"], "card": 3},
    {"address": "13/65", "record_id": "S20", "mu": "20", "set": ["D"], "card": 1},
    {"address": "14/65", "record_id": "S21", "mu": "21", "set": ["A", "D"], "card": 2},
    {"address": "15/65", "record_id": "S22", "mu": "22", "set": ["B", "D"], "card": 2},
    {"address": "16/65", "record_id": "S23", "mu": "23", "set": ["A", "B", "D"], "card": 3},
    {"address": "17/65", "record_id": "S30", "mu": "30", "set": ["C", "D"], "card": 2},
    {"address": "18/65", "record_id": "S31", "mu": "31", "set": ["A", "C", "D"], "card": 3},
    {"address": "19/65", "record_id": "S32", "mu": "32", "set": ["B", "C", "D"], "card": 3},
    {"address": "20/65", "record_id": "S33", "mu": "33", "set": ["A", "B", "C", "D"], "card": 4},
]

ROTATION_ROWS = [
    {"address": "21/65", "record_id": "R01", "rot_plus": ["C"], "rot_minus": ["D"]},
    {"address": "22/65", "record_id": "R02", "rot_plus": ["D"], "rot_minus": ["C"]},
    {"address": "23/65", "record_id": "R03", "rot_plus": ["C", "D"], "rot_minus": ["C", "D"]},
    {"address": "24/65", "record_id": "R10", "rot_plus": ["B"], "rot_minus": ["A"]},
    {"address": "25/65", "record_id": "R11", "rot_plus": ["B", "C"], "rot_minus": ["A", "D"]},
    {"address": "26/65", "record_id": "R12", "rot_plus": ["B", "D"], "rot_minus": ["A", "C"]},
    {"address": "27/65", "record_id": "R13", "rot_plus": ["B", "C", "D"], "rot_minus": ["A", "C", "D"]},
    {"address": "28/65", "record_id": "R20", "rot_plus": ["A"], "rot_minus": ["B"]},
    {"address": "29/65", "record_id": "R21", "rot_plus": ["A", "C"], "rot_minus": ["B", "D"]},
    {"address": "30/65", "record_id": "R22", "rot_plus": ["A", "D"], "rot_minus": ["B", "C"]},
    {"address": "31/65", "record_id": "R23", "rot_plus": ["A", "C", "D"], "rot_minus": ["B", "C", "D"]},
    {"address": "32/65", "record_id": "R30", "rot_plus": ["A", "B"], "rot_minus": ["A", "B"]},
    {"address": "33/65", "record_id": "R31", "rot_plus": ["A", "B", "C"], "rot_minus": ["A", "B", "D"]},
    {"address": "34/65", "record_id": "R32", "rot_plus": ["A", "B", "D"], "rot_minus": ["A", "B", "C"]},
    {"address": "35/65", "record_id": "R33", "rot_plus": ["A", "B", "C", "D"], "rot_minus": ["A", "B", "C", "D"]},
]

SPIN_ROWS = [
    {"address": "36/65", "record_id": "Q01", "orbit": [["A"], ["C"], ["B"], ["D"]]},
    {"address": "37/65", "record_id": "Q02", "orbit": [["B"], ["D"], ["A"], ["C"]]},
    {"address": "38/65", "record_id": "Q03", "orbit": [["A", "B"], ["C", "D"], ["A", "B"], ["C", "D"]]},
    {"address": "39/65", "record_id": "Q10", "orbit": [["C"], ["B"], ["D"], ["A"]]},
    {"address": "40/65", "record_id": "Q11", "orbit": [["A", "C"], ["B", "C"], ["B", "D"], ["A", "D"]]},
    {"address": "41/65", "record_id": "Q12", "orbit": [["B", "C"], ["B", "D"], ["A", "D"], ["A", "C"]]},
    {"address": "42/65", "record_id": "Q13", "orbit": [["A", "B", "C"], ["B", "C", "D"], ["A", "B", "D"], ["A", "C", "D"]]},
    {"address": "43/65", "record_id": "Q20", "orbit": [["D"], ["A"], ["C"], ["B"]]},
    {"address": "44/65", "record_id": "Q21", "orbit": [["A", "D"], ["A", "C"], ["B", "C"], ["B", "D"]]},
    {"address": "45/65", "record_id": "Q22", "orbit": [["B", "D"], ["A", "D"], ["A", "C"], ["B", "C"]]},
    {"address": "46/65", "record_id": "Q23", "orbit": [["A", "B", "D"], ["A", "C", "D"], ["A", "B", "C"], ["B", "C", "D"]]},
    {"address": "47/65", "record_id": "Q30", "orbit": [["C", "D"], ["A", "B"], ["C", "D"], ["A", "B"]]},
    {"address": "48/65", "record_id": "Q31", "orbit": [["A", "C", "D"], ["A", "B", "C"], ["B", "C", "D"], ["A", "B", "D"]]},
    {"address": "49/65", "record_id": "Q32", "orbit": [["B", "C", "D"], ["A", "B", "D"], ["A", "C", "D"], ["A", "B", "C"]]},
    {"address": "50/65", "record_id": "Q33", "orbit": [["A", "B", "C", "D"], ["A", "B", "C", "D"], ["A", "B", "C", "D"], ["A", "B", "C", "D"]]},
]

ANTISPIN_ROWS = [
    {"address": "51/65", "record_id": "T01", "hide": "C", "triad": ["A", "B", "D"], "anti_plus": [["A"], ["B"], ["D"]], "anti_minus": [["A"], ["D"], ["B"]]},
    {"address": "52/65", "record_id": "T02", "hide": "A", "triad": ["C", "B", "D"], "anti_plus": [["B"], ["D"], ["C"]], "anti_minus": [["B"], ["C"], ["D"]]},
    {"address": "53/65", "record_id": "T03", "hide": "C", "triad": ["A", "B", "D"], "anti_plus": [["A", "B"], ["B", "D"], ["A", "D"]], "anti_minus": [["A", "B"], ["A", "D"], ["B", "D"]]},
    {"address": "54/65", "record_id": "T10", "hide": "A", "triad": ["C", "B", "D"], "anti_plus": [["C"], ["B"], ["D"]], "anti_minus": [["C"], ["D"], ["B"]]},
    {"address": "55/65", "record_id": "T11", "hide": "B", "triad": ["A", "C", "D"], "anti_plus": [["A", "C"], ["C", "D"], ["A", "D"]], "anti_minus": [["A", "C"], ["A", "D"], ["C", "D"]]},
    {"address": "56/65", "record_id": "T12", "hide": "A", "triad": ["C", "B", "D"], "anti_plus": [["B", "C"], ["B", "D"], ["C", "D"]], "anti_minus": [["B", "C"], ["C", "D"], ["B", "D"]]},
    {"address": "57/65", "record_id": "T13", "hide": "D", "triad": ["A", "C", "B"], "anti_plus": [["A", "B", "C"], ["A", "B", "C"], ["A", "B", "C"]], "anti_minus": [["A", "B", "C"], ["A", "B", "C"], ["A", "B", "C"]]},
    {"address": "58/65", "record_id": "T20", "hide": "A", "triad": ["C", "B", "D"], "anti_plus": [["D"], ["C"], ["B"]], "anti_minus": [["D"], ["B"], ["C"]]},
    {"address": "59/65", "record_id": "T21", "hide": "C", "triad": ["A", "B", "D"], "anti_plus": [["A", "D"], ["A", "B"], ["B", "D"]], "anti_minus": [["A", "D"], ["B", "D"], ["A", "B"]]},
    {"address": "60/65", "record_id": "T22", "hide": "A", "triad": ["C", "B", "D"], "anti_plus": [["B", "D"], ["C", "D"], ["B", "C"]], "anti_minus": [["B", "D"], ["B", "C"], ["C", "D"]]},
    {"address": "61/65", "record_id": "T23", "hide": "C", "triad": ["A", "B", "D"], "anti_plus": [["A", "B", "D"], ["A", "B", "D"], ["A", "B", "D"]], "anti_minus": [["A", "B", "D"], ["A", "B", "D"], ["A", "B", "D"]]},
    {"address": "62/65", "record_id": "T30", "hide": "A", "triad": ["C", "B", "D"], "anti_plus": [["C", "D"], ["B", "C"], ["B", "D"]], "anti_minus": [["C", "D"], ["B", "D"], ["B", "C"]]},
    {"address": "63/65", "record_id": "T31", "hide": "B", "triad": ["A", "C", "D"], "anti_plus": [["A", "C", "D"], ["A", "C", "D"], ["A", "C", "D"]], "anti_minus": [["A", "C", "D"], ["A", "C", "D"], ["A", "C", "D"]]},
    {"address": "64/65", "record_id": "T32", "hide": "A", "triad": ["C", "B", "D"], "anti_plus": [["B", "C", "D"], ["B", "C", "D"], ["B", "C", "D"]], "anti_minus": [["B", "C", "D"], ["B", "C", "D"], ["B", "C", "D"]]},
    {"address": "65/65", "record_id": "T33", "hide": "A", "triad": ["C", "B", "D"], "anti_plus": [["A", "B", "C", "D"], ["A", "B", "C", "D"], ["A", "B", "C", "D"]], "anti_minus": [["A", "B", "C", "D"], ["A", "B", "C", "D"], ["A", "B", "C", "D"]]},
]

ROW_PIN_MAP = {
    "01": {"z": "ZA", "ck": "loc(A)", "rt_alias": "rtL"},
    "02": {"z": "ZB", "ck": "loc(B)", "rt_alias": "rtL"},
    "03": {"z": "ZA+ZB", "ck": "Z*", "rt_alias": "rtZ"},
    "10": {"z": "ZC", "ck": "loc(C)", "rt_alias": "rtL"},
    "11": {"z": "ZA+ZC", "ck": "loc(A>C)", "rt_alias": "rtL"},
    "12": {"z": "ZB+ZC", "ck": "loc(C>B)", "rt_alias": "rtL"},
    "13": {"z": "ZA+ZB+ZC", "ck": "loc(A>C>B)", "rt_alias": "rtL"},
    "20": {"z": "ZD", "ck": "loc(D)", "rt_alias": "rtL"},
    "21": {"z": "ZA+ZD", "ck": "loc(D>A)", "rt_alias": "rtL"},
    "22": {"z": "ZB+ZD", "ck": "loc(B>D)", "rt_alias": "rtL"},
    "23": {"z": "ZA+ZB+ZD", "ck": "loc(B>D>A)", "rt_alias": "rtL"},
    "30": {"z": "ZC+ZD", "ck": "Z*", "rt_alias": "rtZ"},
    "31": {"z": "ZA+ZC+ZD", "ck": "loc(D>A>C)", "rt_alias": "rtL"},
    "32": {"z": "ZB+ZC+ZD", "ck": "loc(C>B>D)", "rt_alias": "rtL"},
    "33": {"z": "ZA+ZB+ZC+ZD", "ck": "Z*", "rt_alias": "rtZ"},
}


def _marker_block(marker: str, body: str) -> str:
    return "\n".join([f"<!-- {marker}:START -->", body.rstrip(), f"<!-- {marker}:END -->"])


def apply_marker_block(current: str, marker: str, body: str) -> str:
    start_marker = f"<!-- {marker}:START -->"
    end_marker = f"<!-- {marker}:END -->"
    block = _marker_block(marker, body)
    if start_marker in current and end_marker in current:
        start = current.index(start_marker)
        end = current.index(end_marker) + len(end_marker)
        return current[:start] + block + current[end:]
    current = current.rstrip()
    if current:
        return current + "\n\n" + block + "\n"
    return block + "\n"


def format_set(values: list[str]) -> str:
    return "{" + ",".join(values) + "}"


def format_orbit(states: list[list[str]]) -> str:
    return " -> ".join(format_set(state) for state in states)


def symmetry_by_suffix() -> dict[str, dict[str, Any]]:
    return {row["record_id"][1:]: row for row in SYMMETRY_ROWS}


def rotation_by_suffix() -> dict[str, dict[str, Any]]:
    return {row["record_id"][1:]: row for row in ROTATION_ROWS}


def spin_by_suffix() -> dict[str, dict[str, Any]]:
    return {row["record_id"][1:]: row for row in SPIN_ROWS}


def bundle_id_for(suffix: str) -> str:
    return f"B{suffix}"


def route_pin(alias: str) -> dict[str, str]:
    return dict(ROUTE_PINS[alias])


def render_aether(bundle_id: str, phase_bin: str, slot: str, hidden_pole: str | None = None) -> str:
    bundle_token = bundle_id if hidden_pole is None else f"{bundle_id}:h={hidden_pole}"
    return f"AE=({AETHER_LENS},{phase_bin},{bundle_token};{slot})"


def build_aether_coordinate(
    phase_key: str,
    bundle_id: str,
    slot: str,
    hidden_pole: str | None = None,
) -> dict[str, Any]:
    phase = PHASE_DEFS[phase_key]
    bundle_token = bundle_id if hidden_pole is None else f"{bundle_id}:h={hidden_pole}"
    coordinate = {
        "lens": AETHER_LENS,
        "phase_bin": phase["bin"],
        "phase_alias": phase["alias"],
        "bundle_id": bundle_id,
        "bundle_token": bundle_token,
        "slot": slot,
        "render": render_aether(bundle_id, phase["bin"], slot, hidden_pole),
    }
    if hidden_pole is not None:
        coordinate["hidden_pole"] = hidden_pole
    return coordinate


def build_expected_outputs(
    coordinate: dict[str, Any],
    z_alias: str,
    checkpoint_alias: str,
    route_alias: str,
) -> dict[str, str]:
    return {
        "location_match": coordinate["render"],
        "slot_match": coordinate["slot"],
        "z_match": z_alias,
        "checkpoint_match": checkpoint_alias,
        "route_match": route_alias,
        "sigma_satisfied": SIGMA_ROUTE,
        "hub_budget_satisfied": "Hub<=6",
    }


def build_witness_seed(
    seed_id: str,
    coordinate: dict[str, Any],
    z_alias: str,
    checkpoint_alias: str,
    route_alias: str,
) -> dict[str, Any]:
    return {
        "id": seed_id,
        "type": "INTERNAL_SLICE",
        "location": coordinate["render"],
        "hash": f"H({seed_id}|{coordinate['render']}|{z_alias}|{checkpoint_alias}|{route_alias})",
        "scope": list(POINTER_SCOPE),
        "timestamp": SHARED_PINS["timestamp"],
        "collector": "SYSTEM",
        "version_pins": SHARED_PINS["version_pins"],
    }


def build_replay_seed(
    seed_id: str,
    coordinate: dict[str, Any],
    z_alias: str,
    checkpoint_alias: str,
    route_alias: str,
) -> dict[str, Any]:
    return {
        "id": seed_id,
        "inputs": {"AE": coordinate["render"], "z": z_alias, "ck": checkpoint_alias, "rt": route_alias},
        "steps": list(REPLAY_STEPS),
        "expected_outputs": build_expected_outputs(coordinate, z_alias, checkpoint_alias, route_alias),
        "checks": list(REPLAY_CHECKS),
        "env_pin": SHARED_PINS["env_pin"],
        "hash": f"H({seed_id}|{coordinate['render']}|{SHARED_PINS['env_pin']})",
    }


def build_rotation_rows() -> list[dict[str, Any]]:
    symmetry_lookup = symmetry_by_suffix()
    rows: list[dict[str, Any]] = []
    for row in ROTATION_ROWS:
        suffix = row["record_id"][1:]
        parent = symmetry_lookup[suffix]
        pins = ROW_PIN_MAP[suffix]
        route = route_pin(pins["rt_alias"])
        bundle_id = bundle_id_for(suffix)
        coordinate_plus = build_aether_coordinate("R_PLUS", bundle_id, "Core")
        coordinate_minus = build_aether_coordinate("R_MINUS", bundle_id, "Core")
        rows.append(
            {
                **row,
                "family": "R",
                "set": list(parent["set"]),
                "bundle_id": bundle_id,
                "parent_route": parent["record_id"],
                "transfer_mode": "rotation-pair",
                "tunnel_class": "adjacent-bridge",
                "aether_state": (
                    f"AE+={coordinate_plus['render']} | AE-={coordinate_minus['render']}"
                ),
                "entry_condition": f"{parent['record_id']}::set={format_set(parent['set'])}",
                "exit_condition": (
                    f"rot+={format_set(row['rot_plus'])}; rot-={format_set(row['rot_minus'])}"
                ),
                "z": pins["z"],
                "ck": pins["ck"],
                "rt_alias": pins["rt_alias"],
                "rt": route["resolved"],
                "route_pin": route,
                "aether_coordinate_plus": coordinate_plus,
                "aether_coordinate_minus": coordinate_minus,
                "witness_seed_plus": build_witness_seed(
                    f"WS[{row['record_id']},+]",
                    coordinate_plus,
                    pins["z"],
                    pins["ck"],
                    pins["rt_alias"],
                ),
                "replay_seed_plus": build_replay_seed(
                    f"RS[{row['record_id']},+]",
                    coordinate_plus,
                    pins["z"],
                    pins["ck"],
                    pins["rt_alias"],
                ),
                "witness_seed_minus": build_witness_seed(
                    f"WS[{row['record_id']},-]",
                    coordinate_minus,
                    pins["z"],
                    pins["ck"],
                    pins["rt_alias"],
                ),
                "replay_seed_minus": build_replay_seed(
                    f"RS[{row['record_id']},-]",
                    coordinate_minus,
                    pins["z"],
                    pins["ck"],
                    pins["rt_alias"],
                ),
            }
        )
    return rows


def build_spin_rows() -> list[dict[str, Any]]:
    rotation_lookup = rotation_by_suffix()
    symmetry_lookup = symmetry_by_suffix()
    rows: list[dict[str, Any]] = []
    for row in SPIN_ROWS:
        suffix = row["record_id"][1:]
        parent = rotation_lookup[suffix]
        symmetry = symmetry_lookup[suffix]
        pins = ROW_PIN_MAP[suffix]
        route = route_pin(pins["rt_alias"])
        bundle_id = bundle_id_for(suffix)
        coordinate = build_aether_coordinate("Q4", bundle_id, "Core")
        rows.append(
            {
                **row,
                "family": "Q",
                "set": list(symmetry["set"]),
                "bundle_id": bundle_id,
                "parent_route": parent["record_id"],
                "transfer_mode": "base4-spin",
                "tunnel_class": "adjacent-bridge",
                "aether_state": coordinate["render"],
                "entry_condition": (
                    f"{parent['record_id']}::rot+={format_set(parent['rot_plus'])}; "
                    f"rot-={format_set(parent['rot_minus'])}"
                ),
                "exit_condition": f"orbit={format_orbit(row['orbit'])}",
                "z": pins["z"],
                "ck": pins["ck"],
                "rt_alias": pins["rt_alias"],
                "rt": route["resolved"],
                "route_pin": route,
                "aether_coordinate": coordinate,
                "witness_seed": build_witness_seed(
                    f"WS[{row['record_id']}]",
                    coordinate,
                    pins["z"],
                    pins["ck"],
                    pins["rt_alias"],
                ),
                "replay_seed": build_replay_seed(
                    f"RS[{row['record_id']}]",
                    coordinate,
                    pins["z"],
                    pins["ck"],
                    pins["rt_alias"],
                ),
            }
        )
    return rows


def build_antispin_rows() -> list[dict[str, Any]]:
    spin_lookup = spin_by_suffix()
    symmetry_lookup = symmetry_by_suffix()
    rows: list[dict[str, Any]] = []
    for row in ANTISPIN_ROWS:
        suffix = row["record_id"][1:]
        parent = spin_lookup[suffix]
        symmetry = symmetry_lookup[suffix]
        pins = ROW_PIN_MAP[suffix]
        route = route_pin("rtZ")
        bundle_id = bundle_id_for(suffix)
        coordinate = build_aether_coordinate("T3", bundle_id, "Residual", row["hide"])
        rows.append(
            {
                **row,
                "family": "T",
                "set": list(symmetry["set"]),
                "bundle_id": bundle_id,
                "parent_route": parent["record_id"],
                "transfer_mode": "base3-antispin",
                "tunnel_class": "z-star",
                "aether_state": coordinate["render"],
                "entry_condition": (
                    f"{parent['record_id']}::orbit={format_orbit(parent['orbit'])}; "
                    f"hide={row['hide']}; triad={format_set(row['triad'])}"
                ),
                "exit_condition": (
                    f"anti+={format_orbit(row['anti_plus'])}; "
                    f"anti-={format_orbit(row['anti_minus'])}; hide={row['hide']}"
                ),
                "z": pins["z"],
                "ck": pins["ck"],
                "rt_alias": "rtZ",
                "rt": route["resolved"],
                "route_pin": route,
                "aether_coordinate": coordinate,
                "witness_seed": build_witness_seed(
                    f"WS[{row['record_id']}]",
                    coordinate,
                    pins["z"],
                    pins["ck"],
                    "rtZ",
                ),
                "replay_seed": build_replay_seed(
                    f"RS[{row['record_id']}]",
                    coordinate,
                    pins["z"],
                    pins["ck"],
                    "rtZ",
                ),
            }
        )
    return rows


def build_b_prime_registry() -> dict[str, Any]:
    docs_gate_payload = load_docs_gate_status()
    docs_gate_status = (
        str(docs_gate_payload.get("status", "UNKNOWN"))
        if isinstance(docs_gate_payload, dict)
        else str(docs_gate_payload)
    )

    rotation_rows = build_rotation_rows()
    spin_rows = build_spin_rows()
    antispin_rows = build_antispin_rows()
    dense_shell_rows = (
        len(POLE_ROWS)
        + len(SYMMETRY_ROWS)
        + len(rotation_rows)
        + len(spin_rows)
        + len(antispin_rows)
    )
    payload_count = (len(rotation_rows) * 2) + len(spin_rows) + len(antispin_rows)

    return {
        "generated_at": utc_now(),
        "protocol_id": "LP-57OMEGA",
        "shell_id": "B-PRIME-WITNESSED-INVERSION-SHELL",
        "docs_gate_status": docs_gate_status,
        "docs_gate_mode": "LOCAL_ONLY",
        "authority_root": str(B_PRIME_DOC_PATH),
        "dense_shell": {
            "header_shell": "1/65",
            "active_span": "2/65 -> 65/65",
            "sealed": True,
            "inversion_law": "Complement",
            "parent_law": "Chain Parent",
            "witness_scope": "Immediate lawful parent only",
            "sigma_shell": SIGMA_ROUTE,
            "orbit_mechanics": "AppF/AppG",
            "ring_gauge": "A=Fire, C=Air, B=Water, D=Earth",
            "lawful_cycle": "Fire -> Air -> Water -> Earth -> Fire",
        },
        "aether_abi": {
            "render": "AE=(L,Phi,B;sigma)",
            "lattice": "Lens x Phase x Bundle",
            "lens": AETHER_LENS,
            "phase_bins": {PHI_0: "R+", PHI_1: "R-", PHI_2: "Q4", PHI_3: "T3"},
            "slot_domain": ["Core", "Ticket", "Residual", "Test"],
            "slot_policy": {
                "Core": "cert-closed omega-safe only",
                "Residual": "deferred antispin layer",
                "Ticket": "reserved",
                "Test": "reserved",
            },
            "bundle_ids": [bundle_id_for(row["record_id"][1:]) for row in SYMMETRY_ROWS],
        },
        "seed_lock": {
            "witness_formula": (
                "WS[id]:=(Type=INTERNAL_SLICE, Location=AE, Hash=H(id|AE|z|ck|rt), "
                "Scope=(OPS,DEFINE,SYSTEM), Timestamp=Tick_2B, Collector=SYSTEM, VersionPins=V_2B)"
            ),
            "replay_formula": (
                "RS[id]:=(Inputs=(AE,z,ck,rt), Steps=[ResolveZ,ExpandAE,RouteV2,SlotCheck], "
                "ExpectedOutputs, Checks=[Sigma,Hub<=6,ZMatch], EnvPin=E_2B, Hash=H(id|AE|E_2B))"
            ),
            "route_aliases": dict(ROUTE_ALIASES),
            "route_pins": dict(ROUTE_PINS),
            "z_aliases": dict(Z_ALIASES),
            "shared_pins": dict(SHARED_PINS),
        },
        "pointer_contract": {
            "witness_seed_fields": list(WITNESS_SEED_FIELDS),
            "replay_seed_fields": list(REPLAY_SEED_FIELDS),
            "expected_output_fields": list(EXPECTED_OUTPUT_FIELDS),
            "scope": list(POINTER_SCOPE),
            "steps": list(REPLAY_STEPS),
            "checks": list(REPLAY_CHECKS),
            "witness_hook": "WitnessPtr",
            "replay_hook": "ReplayPtr",
            "seed_materialization": "symbolic",
        },
        "counts": {
            "pole_rows": len(POLE_ROWS),
            "symmetry_rows": len(SYMMETRY_ROWS),
            "rotation_rows": len(rotation_rows),
            "spin_rows": len(spin_rows),
            "antispin_rows": len(antispin_rows),
            "witnessed_rows": len(rotation_rows) + len(spin_rows) + len(antispin_rows),
            "dense_shell_rows": dense_shell_rows,
        },
        "payload_counts": {
            "pointer_expanded_rows": len(rotation_rows) + len(spin_rows) + len(antispin_rows),
            "witness_seed_payloads": payload_count,
            "replay_seed_payloads": payload_count,
        },
        "pole_rows": POLE_ROWS,
        "symmetry_rows": SYMMETRY_ROWS,
        "rotation_rows": rotation_rows,
        "spin_rows": spin_rows,
        "antispin_rows": antispin_rows,
    }


def _table(headers: list[str], rows: list[list[str]]) -> str:
    header = "| " + " | ".join(headers) + " |"
    separator = "| " + " | ".join("---" for _ in headers) + " |"
    body = ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join([header, separator, *body])


def _json_block(payload: Any) -> str:
    return "```json\n" + json.dumps(payload, indent=2, ensure_ascii=False) + "\n```"


def _payload_suffix(seed: dict[str, Any]) -> str:
    return seed["hash"]


def render_b_prime_markdown(registry: dict[str, Any]) -> str:
    pole_rows = [
        [
            row["address"],
            row["record_id"],
            row["pole"],
            row["element"],
            row["theta"],
            row["rot_plus"],
            row["inv"],
            row["rot_minus"],
            row["z"],
            row["ae"],
        ]
        for row in registry["pole_rows"]
    ]
    symmetry_rows = [
        [row["address"], row["record_id"], row["mu"], format_set(row["set"]), str(row["card"])]
        for row in registry["symmetry_rows"]
    ]
    rotation_rows = [
        [
            row["address"],
            row["record_id"],
            format_set(row["set"]),
            row["aether_coordinate_plus"]["render"],
            row["aether_coordinate_minus"]["render"],
            _payload_suffix(row["witness_seed_plus"]),
            _payload_suffix(row["replay_seed_plus"]),
            _payload_suffix(row["witness_seed_minus"]),
            _payload_suffix(row["replay_seed_minus"]),
            row["z"],
            row["ck"],
            row["rt_alias"],
        ]
        for row in registry["rotation_rows"]
    ]
    spin_rows = [
        [
            row["address"],
            row["record_id"],
            format_set(row["set"]),
            row["aether_coordinate"]["render"],
            _payload_suffix(row["witness_seed"]),
            _payload_suffix(row["replay_seed"]),
            row["z"],
            row["ck"],
            row["rt_alias"],
        ]
        for row in registry["spin_rows"]
    ]
    antispin_rows = [
        [
            row["address"],
            row["record_id"],
            format_set(row["set"]),
            row["hide"],
            row["aether_coordinate"]["render"],
            _payload_suffix(row["witness_seed"]),
            _payload_suffix(row["replay_seed"]),
            row["z"],
            row["ck"],
            row["rt_alias"],
        ]
        for row in registry["antispin_rows"]
    ]

    return f"""# B' Witnessed Inversion Shell

Docs gate: `{registry['docs_gate_status']}`
Protocol: `LP-57Omega`
Shell law: `A -> B -> B'`

## Lock

- `A` = holographic seed
- `B` = dense inversion shell `2/65 -> 65/65`
- `B'` = witnessed inversion shell with explicit Flower-lens AETHER coordinates
- `1/65` remains the prior seed/header shell
- ring gauge remains `A=Fire, C=Air, B=Water, D=Earth`
- lawful cycle remains `Fire -> Air -> Water -> Earth -> Fire`
- opposite-pole shortcuts remain forbidden except by adjacent bridging or `Z*`
- metro shell remains `Sigma = AppA -> AppI -> AppM`
- orbit and rail mechanics remain on `AppF / AppG`
- only `Rxx`, `Qxx`, and `Txx` receive the appended coordinate and seed payload layer

## Seed Lock

```text
{registry['seed_lock']['witness_formula']}
{registry['seed_lock']['replay_formula']}

rtL = Sigma-F-N-21 = {registry['seed_lock']['route_aliases']['rtL']}
rtZ = Sigma-F-G-21 = {registry['seed_lock']['route_aliases']['rtZ']}
ZA = {registry['seed_lock']['z_aliases']['ZA']}
ZB = {registry['seed_lock']['z_aliases']['ZB']}
ZC = {registry['seed_lock']['z_aliases']['ZC']}
ZD = {registry['seed_lock']['z_aliases']['ZD']}
```

## Summary Tuple

{_table(["Field", "Rule"], [
    ["parent_route", "Immediate lawful parent only"],
    ["transfer_mode", "R=rotation-pair, Q=base4-spin, T=base3-antispin"],
    ["tunnel_class", "adjacent-bridge for R/Q, z-star for T"],
    ["aether_state", "Explicit AETHER coordinate render for the active witnessed cell(s)"],
    ["entry_condition", "Parent active state exactly as inherited"],
    ["exit_condition", "Child realized state after lawful transfer completes"],
])}

## Payload Law

{_table(["Payload", "Fields"], [
    ["WitnessSeed", ", ".join(WITNESS_SEED_FIELDS)],
    ["ReplaySeed", ", ".join(REPLAY_SEED_FIELDS)],
    ["ExpectedOutputs", ", ".join(EXPECTED_OUTPUT_FIELDS)],
])}

## Pole Basis

{_table(["Index", "Record", "Pole", "Element", "Theta", "rot+", "inv", "rot-", "z", "ae"], pole_rows)}

## Raw Symmetry Snapshot

{_table(["Index", "Record", "mu", "set", "card"], symmetry_rows)}

## R-Family :: Rotation / Counter-Rotation x15

{_table(["Index", "Record", "set", "AE+", "AE-", "WS+", "RS+", "WS-", "RS-", "z", "ck", "rt"], rotation_rows)}

## Q-Family :: Spin (Base 4) x15

{_table(["Index", "Record", "set", "AE", "WS", "RS", "z", "ck", "rt"], spin_rows)}

## T-Family :: Antispin (Base 3) x15

{_table(["Index", "Record", "set", "hide", "AE", "WS", "RS", "z", "ck", "rt"], antispin_rows)}

## Pointer Appendix :: Rotation

{_json_block(registry["rotation_rows"])}

## Pointer Appendix :: Spin

{_json_block(registry["spin_rows"])}

## Pointer Appendix :: Antispin

{_json_block(registry["antispin_rows"])}
"""


def _verify_seed_fields(seed: dict[str, Any], expected_fields: list[str]) -> bool:
    return set(seed.keys()) == set(expected_fields)


def _verify_expected_outputs(
    payload: dict[str, Any],
    coordinate: dict[str, Any],
    z_alias: str,
    ck_alias: str,
    rt_alias: str,
) -> bool:
    return payload == {
        "location_match": coordinate["render"],
        "slot_match": coordinate["slot"],
        "z_match": z_alias,
        "checkpoint_match": ck_alias,
        "route_match": rt_alias,
        "sigma_satisfied": SIGMA_ROUTE,
        "hub_budget_satisfied": "Hub<=6",
    }


def _verify_witness_seed(
    seed: dict[str, Any],
    coordinate: dict[str, Any],
    z_alias: str,
    ck_alias: str,
    rt_alias: str,
) -> bool:
    return (
        _verify_seed_fields(seed, WITNESS_SEED_FIELDS)
        and seed["type"] == "INTERNAL_SLICE"
        and seed["location"] == coordinate["render"]
        and seed["hash"] == f"H({seed['id']}|{coordinate['render']}|{z_alias}|{ck_alias}|{rt_alias})"
        and seed["scope"] == POINTER_SCOPE
        and seed["timestamp"] == SHARED_PINS["timestamp"]
        and seed["collector"] == "SYSTEM"
        and seed["version_pins"] == SHARED_PINS["version_pins"]
    )


def _verify_replay_seed(
    seed: dict[str, Any],
    coordinate: dict[str, Any],
    z_alias: str,
    ck_alias: str,
    rt_alias: str,
) -> bool:
    return (
        _verify_seed_fields(seed, REPLAY_SEED_FIELDS)
        and seed["inputs"] == {"AE": coordinate["render"], "z": z_alias, "ck": ck_alias, "rt": rt_alias}
        and seed["steps"] == REPLAY_STEPS
        and _verify_expected_outputs(seed["expected_outputs"], coordinate, z_alias, ck_alias, rt_alias)
        and seed["checks"] == REPLAY_CHECKS
        and seed["env_pin"] == SHARED_PINS["env_pin"]
        and seed["hash"] == f"H({seed['id']}|{coordinate['render']}|{SHARED_PINS['env_pin']})"
    )


def verify_b_prime_registry(registry: dict[str, Any], markdown: str | None = None) -> dict[str, Any]:
    checks: dict[str, bool] = {}
    notes: list[str] = []

    checks["docs_gate_blocked"] = registry.get("docs_gate_status") == "BLOCKED"
    counts = registry.get("counts", {})
    checks["count_vector"] = counts == {
        "pole_rows": 4,
        "symmetry_rows": 15,
        "rotation_rows": 15,
        "spin_rows": 15,
        "antispin_rows": 15,
        "witnessed_rows": 45,
        "dense_shell_rows": 64,
    }
    checks["payload_count_vector"] = registry.get("payload_counts") == {
        "pointer_expanded_rows": 45,
        "witness_seed_payloads": 60,
        "replay_seed_payloads": 60,
    }

    ps_clean = True
    for row in registry.get("pole_rows", []) + registry.get("symmetry_rows", []):
        if any(field in row for field in SUMMARY_WITNESS_FIELDS):
            ps_clean = False
            notes.append(f"{row['record_id']} illegally gained witness tuple fields")
        if any(field in row for field in ["aether_coordinate", "witness_seed", "replay_seed"]):
            ps_clean = False
            notes.append(f"{row['record_id']} illegally gained pointer payloads")
    checks["ps_rows_untouched"] = ps_clean

    rotation_ok = True
    for row in registry.get("rotation_rows", []):
        coordinate_plus = row["aether_coordinate_plus"]
        coordinate_minus = row["aether_coordinate_minus"]
        rotation_ok = rotation_ok and row["parent_route"] == f"S{row['record_id'][1:]}"
        rotation_ok = rotation_ok and row["transfer_mode"] == "rotation-pair"
        rotation_ok = rotation_ok and row["tunnel_class"] == "adjacent-bridge"
        rotation_ok = rotation_ok and coordinate_plus["lens"] == "F" and coordinate_minus["lens"] == "F"
        rotation_ok = rotation_ok and coordinate_plus["phase_bin"] == PHI_0 and coordinate_minus["phase_bin"] == PHI_1
        rotation_ok = rotation_ok and coordinate_plus["slot"] == "Core" and coordinate_minus["slot"] == "Core"
        rotation_ok = rotation_ok and "hidden_pole" not in coordinate_plus and "hidden_pole" not in coordinate_minus
        rotation_ok = rotation_ok and row["rt_alias"] in ROUTE_PINS and row["rt"] == ROUTE_PINS[row["rt_alias"]]["resolved"]
        rotation_ok = rotation_ok and _verify_witness_seed(row["witness_seed_plus"], coordinate_plus, row["z"], row["ck"], row["rt_alias"])
        rotation_ok = rotation_ok and _verify_replay_seed(row["replay_seed_plus"], coordinate_plus, row["z"], row["ck"], row["rt_alias"])
        rotation_ok = rotation_ok and _verify_witness_seed(row["witness_seed_minus"], coordinate_minus, row["z"], row["ck"], row["rt_alias"])
        rotation_ok = rotation_ok and _verify_replay_seed(row["replay_seed_minus"], coordinate_minus, row["z"], row["ck"], row["rt_alias"])
    checks["rotation_payload_contract"] = rotation_ok

    spin_ok = True
    for row in registry.get("spin_rows", []):
        coordinate = row["aether_coordinate"]
        spin_ok = spin_ok and row["parent_route"] == f"R{row['record_id'][1:]}"
        spin_ok = spin_ok and row["transfer_mode"] == "base4-spin"
        spin_ok = spin_ok and row["tunnel_class"] == "adjacent-bridge"
        spin_ok = spin_ok and coordinate["lens"] == "F" and coordinate["phase_bin"] == PHI_2
        spin_ok = spin_ok and coordinate["slot"] == "Core" and "hidden_pole" not in coordinate
        spin_ok = spin_ok and row["rt_alias"] in ROUTE_PINS and row["rt"] == ROUTE_PINS[row["rt_alias"]]["resolved"]
        spin_ok = spin_ok and _verify_witness_seed(row["witness_seed"], coordinate, row["z"], row["ck"], row["rt_alias"])
        spin_ok = spin_ok and _verify_replay_seed(row["replay_seed"], coordinate, row["z"], row["ck"], row["rt_alias"])
    checks["spin_payload_contract"] = spin_ok

    antispin_ok = True
    for row in registry.get("antispin_rows", []):
        coordinate = row["aether_coordinate"]
        antispin_ok = antispin_ok and row["parent_route"] == f"Q{row['record_id'][1:]}"
        antispin_ok = antispin_ok and row["transfer_mode"] == "base3-antispin"
        antispin_ok = antispin_ok and row["tunnel_class"] == "z-star"
        antispin_ok = antispin_ok and coordinate["lens"] == "F" and coordinate["phase_bin"] == PHI_3
        antispin_ok = antispin_ok and coordinate["slot"] == "Residual"
        antispin_ok = antispin_ok and coordinate.get("hidden_pole") == row["hide"]
        antispin_ok = antispin_ok and coordinate["bundle_token"].endswith(f":h={row['hide']}")
        antispin_ok = antispin_ok and row["rt_alias"] == "rtZ" and row["rt"] == ROUTE_PINS["rtZ"]["resolved"]
        antispin_ok = antispin_ok and _verify_witness_seed(row["witness_seed"], coordinate, row["z"], row["ck"], row["rt_alias"])
        antispin_ok = antispin_ok and _verify_replay_seed(row["replay_seed"], coordinate, row["z"], row["ck"], row["rt_alias"])
    checks["antispin_payload_contract"] = antispin_ok

    checks["symbolic_hash_policy"] = all(
        str(seed["hash"]).startswith("H(")
        for row in registry.get("rotation_rows", [])
        for seed in [row["witness_seed_plus"], row["replay_seed_plus"], row["witness_seed_minus"], row["replay_seed_minus"]]
    ) and all(
        str(seed["hash"]).startswith("H(")
        for row in registry.get("spin_rows", []) + registry.get("antispin_rows", [])
        for seed in [row["witness_seed"], row["replay_seed"]]
    )

    checks["route_alias_contract"] = all(
        row["rt_alias"] in ROUTE_PINS and row["rt"] == ROUTE_PINS[row["rt_alias"]]["resolved"]
        for row in registry.get("rotation_rows", []) + registry.get("spin_rows", []) + registry.get("antispin_rows", [])
    )

    checks["flower_phase_assignments"] = all(
        row["aether_coordinate_plus"]["phase_bin"] == PHI_0 and row["aether_coordinate_minus"]["phase_bin"] == PHI_1
        for row in registry.get("rotation_rows", [])
    ) and all(
        row["aether_coordinate"]["phase_bin"] == PHI_2 for row in registry.get("spin_rows", [])
    ) and all(
        row["aether_coordinate"]["phase_bin"] == PHI_3 for row in registry.get("antispin_rows", [])
    )

    if markdown is None:
        checks["markdown_contract"] = True
    else:
        checks["markdown_contract"] = (
            "Pointer Appendix :: Rotation" in markdown
            and "Pointer Appendix :: Spin" in markdown
            and "Pointer Appendix :: Antispin" in markdown
            and "AE=(" in markdown
            and "Tick_2B" in markdown
            and "V_2B" in markdown
            and "E_2B" in markdown
            and "AppA>AppI>AppM>AppF>AppN>Ch21⟨0110⟩" in markdown
            and "AppA>AppI>AppM>AppF>AppG>Ch21⟨0110⟩" in markdown
        )

    truth = "OK" if all(checks.values()) else "FAIL"
    return {
        "generated_at": utc_now(),
        "truth": truth,
        "docs_gate_status": registry.get("docs_gate_status", "UNKNOWN"),
        "counts": counts,
        "payload_counts": registry.get("payload_counts", {}),
        "checks": checks,
        "notes": notes,
    }
