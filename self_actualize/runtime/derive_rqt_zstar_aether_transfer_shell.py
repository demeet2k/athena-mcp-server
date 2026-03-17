from __future__ import annotations

import json
from pathlib import Path


WORKSPACE = Path(r"C:\Users\dmitr\Documents\Athena Agent")
SECTION_PATH = WORKSPACE / "self_actualize" / "manuscript_sections" / "026_rqt_zstar_aether_transfer_shell.md"
REGISTRY_PATH = WORKSPACE / "self_actualize" / "mycelium_brain" / "registry" / "rqt_zstar_aether_transfer_registry.json"
VERIFY_PATH = WORKSPACE / "self_actualize" / "mycelium_brain" / "registry" / "rqt_zstar_aether_transfer_verification.json"

POLE_GAUGE = {"A": "Fire", "C": "Air", "B": "Water", "D": "Earth"}
RING_ORDER = ["A", "C", "B", "D"]
SIGMA = ["AppA", "AppI", "AppM"]
ROTATION_ROUTE = ["AppA", "AppF", "AppC", "AppI", "AppM"]
ANTISPIN_ROUTE = ["AppA", "AppG", "AppC", "AppI", "AppM"]
TRUTH_CLASS = "NEAR"
DOCS_GATE = "BLOCKED"

LOCAL_WITNESSES = [
    "MYCELIUM_TOME_PART1.md::D.010 Sigma",
    "MYCELIUM_TOME_PART1.md::A.008 deterministic router",
    "MEGALITHIC TOME GENERATOR - Latent Tunneling - Skeleton.4d.md::Z_i<->Z* header",
    "user-shell::dense 2/65 -> 65/65 coordinate shell",
]

S_DATA = {
    "01": ["A"],
    "02": ["B"],
    "03": ["A", "B"],
    "10": ["C"],
    "11": ["A", "C"],
    "12": ["B", "C"],
    "13": ["A", "B", "C"],
    "20": ["D"],
    "21": ["A", "D"],
    "22": ["B", "D"],
    "23": ["A", "B", "D"],
    "30": ["C", "D"],
    "31": ["A", "C", "D"],
    "32": ["B", "C", "D"],
    "33": ["A", "B", "C", "D"],
}

R_DATA = {
    "01": {"src": ["A"]},
    "02": {"src": ["B"]},
    "03": {"src": ["A", "B"]},
    "10": {"src": ["C"]},
    "11": {"src": ["A", "C"]},
    "12": {"src": ["B", "C"]},
    "13": {"src": ["A", "B", "C"]},
    "20": {"src": ["D"]},
    "21": {"src": ["A", "D"]},
    "22": {"src": ["B", "D"]},
    "23": {"src": ["A", "B", "D"]},
    "30": {"src": ["C", "D"]},
    "31": {"src": ["A", "C", "D"]},
    "32": {"src": ["B", "C", "D"]},
    "33": {"src": ["A", "B", "C", "D"]},
}

Q_DATA = {
    "01": {"src": ["A"], "orbit": [["A"], ["C"], ["B"], ["D"]]},
    "02": {"src": ["B"], "orbit": [["B"], ["D"], ["A"], ["C"]]},
    "03": {"src": ["A", "B"], "orbit": [["A", "B"], ["C", "D"], ["A", "B"], ["C", "D"]]},
    "10": {"src": ["C"], "orbit": [["C"], ["B"], ["D"], ["A"]]},
    "11": {"src": ["A", "C"], "orbit": [["A", "C"], ["B", "C"], ["B", "D"], ["A", "D"]]},
    "12": {"src": ["B", "C"], "orbit": [["B", "C"], ["B", "D"], ["A", "D"], ["A", "C"]]},
    "13": {"src": ["A", "B", "C"], "orbit": [["A", "B", "C"], ["B", "C", "D"], ["A", "B", "D"], ["A", "C", "D"]]},
    "20": {"src": ["D"], "orbit": [["D"], ["A"], ["C"], ["B"]]},
    "21": {"src": ["A", "D"], "orbit": [["A", "D"], ["A", "C"], ["B", "C"], ["B", "D"]]},
    "22": {"src": ["B", "D"], "orbit": [["B", "D"], ["A", "D"], ["A", "C"], ["B", "C"]]},
    "23": {"src": ["A", "B", "D"], "orbit": [["A", "B", "D"], ["A", "C", "D"], ["A", "B", "C"], ["B", "C", "D"]]},
    "30": {"src": ["C", "D"], "orbit": [["C", "D"], ["A", "B"], ["C", "D"], ["A", "B"]]},
    "31": {"src": ["A", "C", "D"], "orbit": [["A", "C", "D"], ["A", "B", "C"], ["B", "C", "D"], ["A", "B", "D"]]},
    "32": {"src": ["B", "C", "D"], "orbit": [["B", "C", "D"], ["A", "B", "D"], ["A", "C", "D"], ["A", "B", "C"]]},
    "33": {"src": ["A", "B", "C", "D"], "orbit": [["A", "B", "C", "D"]] * 4},
}

T_DATA = {
    "01": {"src": ["A"], "hide": "C", "triad": ["A", "B", "D"], "anti_plus": [["A"], ["B"], ["D"]], "anti_minus": [["A"], ["D"], ["B"]]},
    "02": {"src": ["B"], "hide": "A", "triad": ["C", "B", "D"], "anti_plus": [["B"], ["D"], ["C"]], "anti_minus": [["B"], ["C"], ["D"]]},
    "03": {"src": ["A", "B"], "hide": "C", "triad": ["A", "B", "D"], "anti_plus": [["A", "B"], ["B", "D"], ["A", "D"]], "anti_minus": [["A", "B"], ["A", "D"], ["B", "D"]]},
    "10": {"src": ["C"], "hide": "A", "triad": ["C", "B", "D"], "anti_plus": [["C"], ["B"], ["D"]], "anti_minus": [["C"], ["D"], ["B"]]},
    "11": {"src": ["A", "C"], "hide": "B", "triad": ["A", "C", "D"], "anti_plus": [["A", "C"], ["C", "D"], ["A", "D"]], "anti_minus": [["A", "C"], ["A", "D"], ["C", "D"]]},
    "12": {"src": ["B", "C"], "hide": "A", "triad": ["C", "B", "D"], "anti_plus": [["B", "C"], ["B", "D"], ["C", "D"]], "anti_minus": [["B", "C"], ["C", "D"], ["B", "D"]]},
    "13": {"src": ["A", "B", "C"], "hide": "D", "triad": ["A", "C", "B"], "anti_plus": [["A", "B", "C"]] * 3, "anti_minus": [["A", "B", "C"]] * 3},
    "20": {"src": ["D"], "hide": "A", "triad": ["C", "B", "D"], "anti_plus": [["D"], ["C"], ["B"]], "anti_minus": [["D"], ["B"], ["C"]]},
    "21": {"src": ["A", "D"], "hide": "C", "triad": ["A", "B", "D"], "anti_plus": [["A", "D"], ["A", "B"], ["B", "D"]], "anti_minus": [["A", "D"], ["B", "D"], ["A", "B"]]},
    "22": {"src": ["B", "D"], "hide": "A", "triad": ["C", "B", "D"], "anti_plus": [["B", "D"], ["C", "D"], ["B", "C"]], "anti_minus": [["B", "D"], ["B", "C"], ["C", "D"]]},
    "23": {"src": ["A", "B", "D"], "hide": "C", "triad": ["A", "B", "D"], "anti_plus": [["A", "B", "D"]] * 3, "anti_minus": [["A", "B", "D"]] * 3},
    "30": {"src": ["C", "D"], "hide": "A", "triad": ["C", "B", "D"], "anti_plus": [["C", "D"], ["B", "C"], ["B", "D"]], "anti_minus": [["C", "D"], ["B", "D"], ["B", "C"]]},
    "31": {"src": ["A", "C", "D"], "hide": "B", "triad": ["A", "C", "D"], "anti_plus": [["A", "C", "D"]] * 3, "anti_minus": [["A", "C", "D"]] * 3},
    "32": {"src": ["B", "C", "D"], "hide": "A", "triad": ["C", "B", "D"], "anti_plus": [["B", "C", "D"]] * 3, "anti_minus": [["B", "C", "D"]] * 3},
    "33": {"src": ["A", "B", "C", "D"], "hide": "A", "triad": ["C", "B", "D"], "anti_plus": [["A", "B", "C", "D"]] * 3, "anti_minus": [["A", "B", "C", "D"]] * 3},
}

MU_ORDER = list(S_DATA.keys())


def ordered_for_ring(values: list[str]) -> list[str]:
    return [value for value in RING_ORDER if value in values]


def gate_addr(record_class: str, mu: str) -> str:
    class_digit = {"R": "1", "Q": "2", "T": "3"}[record_class]
    return f"Gate<{2}{class_digit}{mu}>"


def z_list(values: list[str]) -> list[str]:
    return [f"Z({POLE_GAUGE[pole]})" for pole in ordered_for_ring(values)]


def shell_slot(record_class: str, index: int) -> str:
    base = {"R": 21, "Q": 36, "T": 51}[record_class]
    return f"{base + index}/65"


def transfer_signature(record_class: str, src: list[str]) -> dict[str, object]:
    primary_hub = "AppF" if record_class in {"R", "Q"} else "AppG"
    route = ROTATION_ROUTE if record_class in {"R", "Q"} else ANTISPIN_ROUTE
    source_z = z_list(src)
    return {
        "source_z": source_z[0] if len(source_z) == 1 else source_z,
        "tunnel": f"{' + '.join(source_z)} -> Z*" if len(source_z) > 1 else f"{source_z[0]} -> Z*",
        "aether_endpoint": "Aether",
        "transfer_mode": {"R": "rotation_bridge", "Q": "spin_orbit", "T": "antispin_lock"}[record_class],
        "primary_hub": primary_hub,
        "bridge_hub": "AppC",
        "sigma_shell": SIGMA,
        "opposite_pole_policy": "forbidden_direct_opposite_except_via_zstar",
        "landing_signature": " -> ".join(route),
    }


def route_witness(record_class: str, mu: str) -> dict[str, object]:
    is_t = record_class == "T"
    route = ANTISPIN_ROUTE if is_t else ROTATION_ROUTE
    prior_record = {"R": f"S{mu}", "Q": f"R{mu}", "T": f"S{mu}"}[record_class]
    supporting = ["AppA", "AppI", "AppM", "AppC", "AppG" if is_t else "AppF"]
    return {
        "prior_record": prior_record,
        "route_kind": "prior_compact_metro",
        "route": " -> ".join(route),
        "witness_basis": LOCAL_WITNESSES,
        "replay_basis": f"Same gauge, same ring order A->C->B->D, same mu={mu}, same route {'/'.join(route)} reproduces the same signature.",
        "supporting_appendices": supporting,
    }


def witness_ptr(record_class: str, mu: str) -> list[str]:
    shared = [
        "C:\\Users\\dmitr\\Documents\\Athena Agent\\MYCELIUM_TOME_PART1.md::D.010",
        "C:\\Users\\dmitr\\Documents\\Athena Agent\\MYCELIUM_TOME_PART1.md::A.008",
        "C:\\Users\\dmitr\\Documents\\Athena Agent\\FULL_PROJECT_TESSERACT_SYNTHESIS_2026-03-11.md::Master Agent <-> Aether",
        "in-thread::dense shell 2/65 -> 65/65",
    ]
    extra = "C:\\Users\\dmitr\\Documents\\Athena Agent\\MYCELIUM_TOME_PART1.md::AppG" if record_class == "T" else "C:\\Users\\dmitr\\Documents\\Athena Agent\\MYCELIUM_TOME_PART1.md::AppF"
    return shared + [extra, f"{'S' if record_class in {'R', 'T'} else 'R'}{mu}"]


def replay_ptr(record_class: str, mu: str) -> list[str]:
    route = "AppA -> AppG -> AppC -> AppI -> AppM" if record_class == "T" else "AppA -> AppF -> AppC -> AppI -> AppM"
    return [
        "C:\\Users\\dmitr\\Documents\\Athena Agent\\MYCELIUM_TOME_PART1.md::worked example",
        f"replay::{record_class}{mu}::{route}",
        f"replay::mu={mu}::ring=A->C->B->D",
    ]


def record_note(record_class: str) -> str:
    if record_class == "R":
        return "Metadata attachment over rotation/counter-rotation pair; no source-set rewrite."
    if record_class == "Q":
        return "Metadata attachment over base-4 orbit closure; orbit body preserved exactly."
    return "Metadata attachment over base-3 antispin lock; hidden-pole law preserved exactly."


def make_records() -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for index, mu in enumerate(MU_ORDER):
        src_r = R_DATA[mu]["src"]
        records.append(
            {
                "record_id": f"R{mu}",
                "record_class": "R",
                "shell_slot": shell_slot("R", index),
                "gate_addr": gate_addr("R", mu),
                "mu": mu,
                "source_set": src_r,
                "cardinality": len(src_r),
                "pole_gauge": POLE_GAUGE,
                "ring_order": RING_ORDER,
                "primary_hub": "AppF",
                "sigma_shell": SIGMA,
                "route_bridge_hub": "AppC",
                "hide": None,
                "triad": None,
                "z_transfer_signature": transfer_signature("R", src_r),
                "prior_metro_route_witness": route_witness("R", mu),
                "witness_ptr": witness_ptr("R", mu),
                "replay_ptr": replay_ptr("R", mu),
                "truth_class": TRUTH_CLASS,
                "notes": record_note("R"),
            }
        )
        src_q = Q_DATA[mu]["src"]
        records.append(
            {
                "record_id": f"Q{mu}",
                "record_class": "Q",
                "shell_slot": shell_slot("Q", index),
                "gate_addr": gate_addr("Q", mu),
                "mu": mu,
                "source_set": src_q,
                "cardinality": len(src_q),
                "pole_gauge": POLE_GAUGE,
                "ring_order": RING_ORDER,
                "primary_hub": "AppF",
                "sigma_shell": SIGMA,
                "route_bridge_hub": "AppC",
                "hide": None,
                "triad": None,
                "z_transfer_signature": transfer_signature("Q", src_q),
                "prior_metro_route_witness": route_witness("Q", mu),
                "witness_ptr": witness_ptr("Q", mu),
                "replay_ptr": replay_ptr("Q", mu),
                "truth_class": TRUTH_CLASS,
                "notes": f"{record_note('Q')} orbit={Q_DATA[mu]['orbit']}",
            }
        )
        src_t = T_DATA[mu]["src"]
        records.append(
            {
                "record_id": f"T{mu}",
                "record_class": "T",
                "shell_slot": shell_slot("T", index),
                "gate_addr": gate_addr("T", mu),
                "mu": mu,
                "source_set": src_t,
                "cardinality": len(src_t),
                "pole_gauge": POLE_GAUGE,
                "ring_order": RING_ORDER,
                "primary_hub": "AppG",
                "sigma_shell": SIGMA,
                "route_bridge_hub": "AppC",
                "hide": T_DATA[mu]["hide"],
                "triad": T_DATA[mu]["triad"],
                "z_transfer_signature": transfer_signature("T", src_t),
                "prior_metro_route_witness": route_witness("T", mu),
                "witness_ptr": witness_ptr("T", mu),
                "replay_ptr": replay_ptr("T", mu),
                "truth_class": TRUTH_CLASS,
                "notes": f"{record_note('T')} anti_plus={T_DATA[mu]['anti_plus']} anti_minus={T_DATA[mu]['anti_minus']}",
            }
        )
    return records


def row_text(record: dict[str, object]) -> str:
    hide = record["hide"] if record["hide"] is not None else "-"
    transfer = record["z_transfer_signature"]
    route = record["prior_metro_route_witness"]
    return (
        f"| `{record['record_id']}` | `{record['gate_addr']}` | `{record['mu']}` | "
        f"`{','.join(record['source_set'])}` | `{hide}` | `{record['primary_hub']}` | "
        f"`{transfer['tunnel']} -> {transfer['aether_endpoint']} via {transfer['landing_signature']}` | "
        f"`{route['prior_record']} :: {route['route']}` | `{record['truth_class']}` |"
    )


def build_markdown(records: list[dict[str, object]]) -> str:
    grouped = {"R": [], "Q": [], "T": []}
    for record in records:
        grouped[record["record_class"]].append(record)

    parts = [
        "# 2/65-65/65 RQT Z-Star Aether Nesting Layer",
        "",
        "## Fixed Law Header",
        "",
        f"- Docs gate: `{DOCS_GATE}`",
        "- Ring gauge: `A=Fire, C=Air, B=Water, D=Earth`",
        "- Ring order: `A -> C -> B -> D -> A`",
        "- Opposite-pole law: `forbidden_direct_opposite_except_via_zstar`",
        "- Sigma: `{AppA, AppI, AppM}`",
        "- Rotation carrier: `AppF`",
        "- Rail and antispin carrier: `AppG`",
        "- Bridge hub: `AppC`",
        "- Hide default: `first missing pole in ring order A->C->B->D`, default `A` when none is missing",
        "",
        "## Address Law",
        "",
        "- Dense-shell family prefix: `2`",
        "- Class digits: `R=1`, `Q=2`, `T=3`",
        "- Record gate form: `Gate<2 c mu>`",
        "- Examples: `R01 -> Gate<2101>`, `Q13 -> Gate<2213>`, `T33 -> Gate<2333>`",
        "- Visible `21/65` through `65/65` shell slots remain presentation indices only.",
        "",
        "## R Table",
        "",
        "| id | gate | mu | src | hide | hub | z* / aether signature | prior metro witness | truth |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    parts.extend(row_text(record) for record in grouped["R"])
    parts.extend(
        [
            "",
            "## Q Table",
            "",
            "| id | gate | mu | src | hide | hub | z* / aether signature | prior metro witness | truth |",
            "|---|---|---|---|---|---|---|---|---|",
        ]
    )
    parts.extend(row_text(record) for record in grouped["Q"])
    parts.extend(
        [
            "",
            "## T Table",
            "",
            "| id | gate | mu | src | hide | hub | z* / aether signature | prior metro witness | truth |",
            "|---|---|---|---|---|---|---|---|---|",
        ]
    )
    parts.extend(row_text(record) for record in grouped["T"])
    parts.extend(
        [
            "",
            "## Compact Witness And Replay Notes",
            "",
            "- Every record inherits `Sigma = {AppA, AppI, AppM}` and adds the lawful carrier hub plus `AppC` as bridge hub.",
            "- `R(mu)` witnesses back to `S(mu)`; `Q(mu)` witnesses back to `R(mu)`; `T(mu)` witnesses back to `S(mu)`.",
            "- `R/Q` land through `AppA -> AppF -> AppC -> AppI -> AppM`.",
            "- `T` lands through `AppA -> AppG -> AppC -> AppI -> AppM`.",
            "- This shell is metadata attachment only. It does not rewrite the sealed `P` or `S` records and does not alter the user-fixed `R/Q/T` math.",
            "",
            "SUPPLEMENT - RQT Z-Star Aether Transfer Shell",
        ]
    )
    return "\n".join(parts) + "\n"


def verify(records: list[dict[str, object]]) -> dict[str, object]:
    gate_addrs = [record["gate_addr"] for record in records]
    counts = {
        "R": sum(record["record_class"] == "R" for record in records),
        "Q": sum(record["record_class"] == "Q" for record in records),
        "T": sum(record["record_class"] == "T" for record in records),
    }
    unique_gate_prefixes = {
        "R": all(record["gate_addr"].startswith("Gate<21") for record in records if record["record_class"] == "R"),
        "Q": all(record["gate_addr"].startswith("Gate<22") for record in records if record["record_class"] == "Q"),
        "T": all(record["gate_addr"].startswith("Gate<23") for record in records if record["record_class"] == "T"),
    }
    sigma_ok = all(record["sigma_shell"] == SIGMA for record in records)
    hub_ok = all(
        (
            record["primary_hub"] == "AppF"
            if record["record_class"] in {"R", "Q"}
            else record["primary_hub"] == "AppG"
        )
        and record["route_bridge_hub"] == "AppC"
        for record in records
    )
    t_hide_defaults_ok = next(record for record in records if record["record_id"] == "T33")["hide"] == "A"
    prior_links_ok = all(
        record["prior_metro_route_witness"]["prior_record"] == (
            f"S{record['mu']}" if record["record_class"] in {"R", "T"} else f"R{record['mu']}"
        )
        for record in records
    )
    witness_nonempty = all(record["witness_ptr"] and record["replay_ptr"] for record in records)
    transfer_ok = all(
        record["z_transfer_signature"]["aether_endpoint"] == "Aether"
        and record["z_transfer_signature"]["opposite_pole_policy"] == "forbidden_direct_opposite_except_via_zstar"
        for record in records
    )
    return {
        "truth_class": TRUTH_CLASS,
        "docs_gate": DOCS_GATE,
        "record_count": len(records),
        "counts_by_class": counts,
        "unique_gate_count": len(set(gate_addrs)),
        "unique_gate_prefixes_ok": unique_gate_prefixes,
        "sigma_ok": sigma_ok,
        "hub_ok": hub_ok,
        "transfer_ok": transfer_ok,
        "prior_links_ok": prior_links_ok,
        "witness_nonempty": witness_nonempty,
        "t33_hide_default_ok": t_hide_defaults_ok,
        "all_checks_pass": (
            len(records) == 45
            and counts == {"R": 15, "Q": 15, "T": 15}
            and len(set(gate_addrs)) == 45
            and all(unique_gate_prefixes.values())
            and sigma_ok
            and hub_ok
            and transfer_ok
            and prior_links_ok
            and witness_nonempty
            and t_hide_defaults_ok
        ),
    }


def main() -> int:
    records = make_records()
    SECTION_PATH.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    SECTION_PATH.write_text(build_markdown(records), encoding="utf-8")
    REGISTRY_PATH.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    VERIFY_PATH.write_text(json.dumps(verify(records), indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {SECTION_PATH}")
    print(f"Wrote {REGISTRY_PATH}")
    print(f"Wrote {VERIFY_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
