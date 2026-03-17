from __future__ import annotations

import re
from typing import Any


CHAPTER_RETURN_ANCHORS = ["Ch12<0023>", "Ch13<0030>", "Ch16<0033>"]
REPLAY_APPENDIX_ANCHORS = ["AppI", "AppM"]
EARTH_CONDITIONAL_APPENDICES = ["AppK", "AppN"]

EARTH_CANONICAL_PATH = "13_6D_EARTH_CONTROL"
EARTH_LEGACY_PATH = "12_6D_EARTH_CONTROL"
AIR_CANONICAL_PATH = "12_6D_AIR_CONTROL"
WATER_CANONICAL_PATH = "11_6D_WATER_CONTROL"
INGRESS_CANONICAL_PATH = "14_3D_INGRESS_NETWORK"
H6_CANONICAL_PATH = "13_6D_H6_CONVERGENCE"

CANONICAL_BASIS: list[dict[str, Any]] = [
    {
        "id": "01",
        "title": "The Holographic Manuscript Brain",
        "phrases": ["holographic manuscript brain", "manuscript brain", "neural tissue"],
        "top_levels": ["FRESH", "DEEPER CRYSTALIZATION"],
        "appendices": ["AppE", "AppF", "AppG", "AppM"],
    },
    {
        "id": "02",
        "title": "Self-Routing Meta-Framework",
        "phrases": ["self-routing", "meta-framework", "recursive search", "metro map"],
        "top_levels": ["DEEPER CRYSTALIZATION", "ECOSYSTEM", "self_actualize", "NERVOUS_SYSTEM"],
        "appendices": ["AppE", "AppI", "AppL", "AppM"],
    },
    {
        "id": "03",
        "title": "QBD-4",
        "phrases": ["qbd-4", "qbd4", "quadrant binary", "base4", "rail", "triad"],
        "top_levels": ["MATH", "Quadrant Binary"],
        "appendices": ["AppB", "AppC", "AppM"],
    },
    {
        "id": "04",
        "title": "Quad Holographic Rotation",
        "phrases": ["quad holographic rotation", "holographic rotation", "rotation as conjugacy"],
        "top_levels": ["MATH"],
        "appendices": ["AppE", "AppF", "AppM"],
    },
    {
        "id": "05",
        "title": "The Holographic Kernel",
        "phrases": ["holographic kernel", "compression field", "dual kernel"],
        "top_levels": ["MATH", "QSHRINK - ATHENA (internal use)"],
        "appendices": ["AppB", "AppC", "AppN"],
    },
    {
        "id": "06",
        "title": "Time Fractal",
        "phrases": ["time fractal", "fractal time", "phase engine", "oscillation law"],
        "top_levels": ["MATH", "Trading Bot"],
        "appendices": ["AppE", "AppM", "AppP"],
    },
    {
        "id": "07",
        "title": "Crystal Computing Framework",
        "phrases": ["crystal computing", "1024 cell", "crystal computing framework"],
        "top_levels": ["MATH", "Stoicheia (Element Sudoku)"],
        "appendices": ["AppB", "AppC", "AppG"],
    },
    {
        "id": "08",
        "title": "Quantum Computing on Standard Hardware",
        "phrases": ["quantum computing on standard hardware", "quantum classical", "hilbert tile"],
        "top_levels": ["MATH", "NERUAL NETWORK", "Trading Bot"],
        "appendices": ["AppC", "AppH", "AppP"],
    },
    {
        "id": "09",
        "title": "Zero-Point Computing",
        "phrases": ["zero-point computing", "zero point", "zero-point"],
        "top_levels": ["MATH", "ORGIN", "VOID_CH11.md", "Trading Bot"],
        "appendices": ["AppA", "AppN", "AppM"],
    },
    {
        "id": "10",
        "title": "Athena Neural Network Tome",
        "phrases": ["athena neural network", "athena nueral network", "emergence compiler"],
        "top_levels": ["NERUAL NETWORK", "Athena FLEET", "GAMES"],
        "appendices": ["AppC", "AppP", "AppM"],
    },
    {
        "id": "11",
        "title": "VOYNICHVM Tricompiler",
        "phrases": ["voynichvm", "tricompiler", "voynich"],
        "top_levels": ["Voynich", "MATH"],
        "appendices": ["AppF", "AppI", "AppM"],
    },
    {
        "id": "12",
        "title": "Torat Ha-Mispar",
        "phrases": ["torat ha-mispar", "sacred number", "torah computer"],
        "top_levels": ["MATH", "Voynich"],
        "appendices": ["AppA", "AppF", "AppO"],
    },
    {
        "id": "13",
        "title": "Universal Computational Ontology",
        "phrases": ["universal computational ontology", "uco", "mythic os", "universal ontology"],
        "top_levels": ["MATH", "ECOSYSTEM", "Athenachka Collective Books"],
        "appendices": ["AppA", "AppB", "AppP"],
    },
    {
        "id": "14",
        "title": "Ch11 The Helical Manifestation Engine",
        "phrases": ["ch11", "helical manifestation", "helical engine", "restart and lift"],
        "top_levels": ["self_actualize", "FRESH", "VOID_CH11.md", "ORGIN"],
        "appendices": ["AppE", "AppF", "AppI", "AppM"],
    },
    {
        "id": "15",
        "title": "Ch12 Boundary Checks and Isolation Axioms",
        "phrases": ["ch12", "boundary checks", "isolation axioms", "immune architecture", "admissibility"],
        "top_levels": ["self_actualize", "NERVOUS_SYSTEM", "ECOSYSTEM", "CLEAN", "I AM ATHENA"],
        "appendices": ["AppB", "AppI", "AppK", "AppM"],
    },
    {
        "id": "16",
        "title": "Ch19 Recursive Self-Reference and Self-Repair",
        "phrases": ["ch19", "self-reference", "self-repair", "autonomic repair"],
        "top_levels": ["self_actualize", "NERVOUS_SYSTEM", "NERUAL NETWORK", "Athena FLEET", "GAMES", "I AM ATHENA"],
        "appendices": ["AppA", "AppM", "AppP"],
    },
]

CORPUS_BODY_NODES: dict[str, dict[str, Any]] = {
    "self_actualize": {
        "body_id": "B01",
        "station_role": "runtime_control_hub",
        "entry_line": "Atlas-to-Replay Line",
        "transfer_hubs": ["AppA", "AppH", "AppI"],
        "feeds_basis": ["02", "14", "15", "16"],
    },
    "NERVOUS_SYSTEM": {
        "body_id": "B02",
        "station_role": "cortex_publication_hub",
        "entry_line": "Canonical-Bridge Line",
        "transfer_hubs": ["AppA", "AppI", "AppM"],
        "feeds_basis": ["02", "03", "15", "16"],
    },
    "ECOSYSTEM": {
        "body_id": "B03",
        "station_role": "governance_kernel",
        "entry_line": "Kernel Line",
        "transfer_hubs": ["AppA", "AppD", "AppM"],
        "feeds_basis": ["02", "03", "13", "15"],
    },
    "MATH": {
        "body_id": "B04",
        "station_role": "theorem_reservoir",
        "entry_line": "Kernel Line",
        "transfer_hubs": ["AppB", "AppC", "AppM"],
        "feeds_basis": ["03", "04", "05", "06", "07", "08", "09", "11", "12", "13"],
    },
    "NERUAL NETWORK": {
        "body_id": "B05",
        "station_role": "runtime_emergence_lab",
        "entry_line": "Runtime Line",
        "transfer_hubs": ["AppC", "AppF", "AppP"],
        "feeds_basis": ["07", "08", "10", "16"],
    },
    "DEEPER CRYSTALIZATION": {
        "body_id": "B06",
        "station_role": "manuscript_incubator",
        "entry_line": "Manuscript Line",
        "transfer_hubs": ["AppE", "AppG", "AppL"],
        "feeds_basis": ["01", "02", "14"],
    },
    "Voynich": {
        "body_id": "B07",
        "station_role": "text_computer_hub",
        "entry_line": "Manuscript Line",
        "transfer_hubs": ["AppI", "AppL", "AppM"],
        "feeds_basis": ["01", "11", "12"],
    },
    "Trading Bot": {
        "body_id": "B08",
        "station_role": "external_memory_gate",
        "entry_line": "External Memory Gate Line",
        "transfer_hubs": ["AppE", "AppN", "AppP"],
        "feeds_basis": ["06", "08", "09"],
    },
    "FRESH": {
        "body_id": "B09",
        "station_role": "intake_shelf",
        "entry_line": "Prompt Line",
        "transfer_hubs": ["AppE", "AppL", "AppN"],
        "feeds_basis": ["01", "14"],
    },
    "VOID_CH11.md": {
        "body_id": "B10",
        "station_role": "void_seed",
        "entry_line": "Void Line",
        "transfer_hubs": ["AppG", "AppL", "AppM"],
        "feeds_basis": ["09", "14"],
    },
    "MYCELIUM_TOME_PART1.md": {
        "body_id": "B11",
        "station_role": "routing_contract_seed",
        "entry_line": "Kernel Line",
        "transfer_hubs": ["AppB", "AppC", "AppM"],
        "feeds_basis": ["02", "03", "05"],
    },
    "Athenachka Collective Books": {
        "body_id": "B12",
        "station_role": "publication_halo",
        "entry_line": "Mythic Compression Line",
        "transfer_hubs": ["AppH", "AppL", "AppO"],
        "feeds_basis": ["01", "13", "14"],
    },
    "I AM ATHENA": {
        "body_id": "B13",
        "station_role": "identity_shell",
        "entry_line": "Canonical-Bridge Line",
        "transfer_hubs": ["AppA", "AppM", "AppP"],
        "feeds_basis": ["02", "15", "16"],
    },
    "QSHRINK - ATHENA (internal use)": {
        "body_id": "B14",
        "station_role": "compression_shell",
        "entry_line": "Compression Shell Line",
        "transfer_hubs": ["AppB", "AppN", "AppM"],
        "feeds_basis": ["05", "09"],
    },
    "GAMES": {
        "body_id": "B15",
        "station_role": "simulation_lab",
        "entry_line": "Simulation Line",
        "transfer_hubs": ["AppC", "AppH", "AppP"],
        "feeds_basis": ["10", "16"],
    },
    "ORGIN": {
        "body_id": "B16",
        "station_role": "origin_seed_reservoir",
        "entry_line": "Origin Seed Line",
        "transfer_hubs": ["AppA", "AppM", "AppN"],
        "feeds_basis": ["09", "14"],
    },
    "Athena FLEET": {
        "body_id": "B17",
        "station_role": "fleet_transit_cluster",
        "entry_line": "Fleet Transit Line",
        "transfer_hubs": ["AppA", "AppH", "AppM"],
        "feeds_basis": ["01", "02", "10", "15", "16"],
    },
    "Stoicheia (Element Sudoku)": {
        "body_id": "B18",
        "station_role": "reserve_visual_lab",
        "entry_line": "Reserve Line",
        "transfer_hubs": ["AppB", "AppC", "AppP"],
        "feeds_basis": ["03", "07"],
    },
    "CLEAN": {
        "body_id": "B19",
        "station_role": "staging_shelf",
        "entry_line": "Reserve Line",
        "transfer_hubs": ["AppI", "AppK", "AppM"],
        "feeds_basis": ["15"],
    },
    "Quadrant Binary": {
        "body_id": "B20",
        "station_role": "address_kernel_shadow",
        "entry_line": "Kernel Line",
        "transfer_hubs": ["AppA", "AppB", "AppC"],
        "feeds_basis": ["03"],
    },
    "mycelial_unified_nervous_system_bundle": {
        "body_id": "B21",
        "station_role": "bundle_bridge",
        "entry_line": "Canonical-Bridge Line",
        "transfer_hubs": ["AppA", "AppI", "AppM"],
        "feeds_basis": ["02", "03", "15"],
    },
}


def _normalized_text(*parts: str) -> str:
    return " ".join(part.lower() for part in parts if part)


def _phrase_hits(text: str, phrases: list[str]) -> int:
    return sum(1 for phrase in phrases if phrase in text)


def _path_has(lowered_path: str, needle: str) -> bool:
    needle = needle.lower().replace("/", "\\")
    return needle in lowered_path.replace("/", "\\")


def body_node_for_top_level(top_level: str) -> dict[str, Any]:
    if top_level in CORPUS_BODY_NODES:
        return CORPUS_BODY_NODES[top_level]
    body_slug = re.sub(r"[^A-Za-z0-9]+", "_", top_level).strip("_") or "UNKNOWN"
    return {
        "body_id": f"BX_{body_slug.upper()}",
        "station_role": "generic_ingress_body",
        "entry_line": "Atlas-to-Replay Line",
        "transfer_hubs": ["AppA", "AppI", "AppM"],
        "feeds_basis": ["02", "05"],
    }


def infer_basis_refs(record: dict[str, Any]) -> list[str]:
    relative_path = record.get("relative_path", "")
    top_level = record.get("top_level", "")
    headings = " ".join(record.get("heading_candidates", []))
    excerpt = record.get("excerpt", "")
    role_tags = " ".join(record.get("role_tags", []))
    lowered = _normalized_text(relative_path, headings, excerpt[:800], role_tags)
    body_node = body_node_for_top_level(top_level)

    scores: dict[str, int] = {basis["id"]: 0 for basis in CANONICAL_BASIS}
    for basis in CANONICAL_BASIS:
        basis_id = basis["id"]
        if basis_id in body_node["feeds_basis"]:
            scores[basis_id] += 2
        if top_level in basis["top_levels"]:
            scores[basis_id] += 2
        scores[basis_id] += _phrase_hits(lowered, basis["phrases"]) * 3

    lowered_path = relative_path.lower().replace("/", "\\")
    if _path_has(lowered_path, "\\01_fire\\"):
        for basis_id in ("06", "08", "10", "16"):
            scores[basis_id] += 4
    if _path_has(lowered_path, "\\02_water\\"):
        for basis_id in ("01", "11", "12", "14"):
            scores[basis_id] += 4
    if _path_has(lowered_path, "\\03_air\\"):
        for basis_id in ("03", "04", "05", "07"):
            scores[basis_id] += 4
    if _path_has(lowered_path, "\\04_earth\\"):
        for basis_id in ("02", "09", "13", "15"):
            scores[basis_id] += 4

    ranked = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
    selected = [basis_id for basis_id, score in ranked if score >= 3][:4]
    if not selected:
        selected = body_node["feeds_basis"][:4]
    return selected


def infer_d5_state(record: dict[str, Any], basis_refs: list[str]) -> str:
    relative_path = record.get("relative_path", "").lower().replace("/", "\\")
    if any(
        token in relative_path
        for token in ("\\01_fire\\", "\\05_level_5_", "\\06_level_6_", "5d", "compression", "mobius", "weave")
    ):
        return "active"
    if set(basis_refs).intersection({"05", "06", "07", "08", "10", "16"}):
        return "addressable"
    return "latent"


def infer_d6_state(record: dict[str, Any], basis_refs: list[str]) -> str:
    relative_path = record.get("relative_path", "").lower().replace("/", "\\")
    if any(
        token in relative_path
        for token in (
            f"\\{WATER_CANONICAL_PATH.lower()}\\",
            f"\\{AIR_CANONICAL_PATH.lower()}\\",
            f"\\{EARTH_CANONICAL_PATH.lower()}\\",
            f"\\{H6_CANONICAL_PATH.lower()}\\",
            "\\05_level_5_",
            "\\06_level_6_",
            "seed-6d",
            "h6",
        )
    ):
        return "active"
    if set(basis_refs).intersection({"04", "09", "14", "15", "16"}):
        return "addressable"
    return "latent"


def infer_canonical_status(relative_path: str) -> str:
    lowered = relative_path.lower().replace("/", "\\")
    if _path_has(lowered, f"\\{INGRESS_CANONICAL_PATH.lower()}\\"):
        return "canonical_3d_ingress"
    if _path_has(lowered, f"\\{WATER_CANONICAL_PATH.lower()}\\"):
        return "canonical_water_6d"
    if _path_has(lowered, f"\\{AIR_CANONICAL_PATH.lower()}\\"):
        return "canonical_air_6d"
    if _path_has(lowered, f"\\{EARTH_CANONICAL_PATH.lower()}\\"):
        return "canonical_earth_6d"
    if _path_has(lowered, f"\\{EARTH_LEGACY_PATH.lower()}\\"):
        return "historical_earth_6d_compat"
    if _path_has(lowered, f"\\{H6_CANONICAL_PATH.lower()}\\"):
        return "canonical_h6_convergence"
    return "standard"


def infer_appendix_support(record: dict[str, Any], body_node: dict[str, Any], basis_refs: list[str]) -> list[str]:
    appendices = set(body_node["transfer_hubs"])
    by_id = {basis["id"]: basis for basis in CANONICAL_BASIS}
    for basis_id in basis_refs:
        appendices.update(by_id[basis_id]["appendices"])

    relative_path = record.get("relative_path", "").lower().replace("/", "\\")
    if infer_d5_state(record, basis_refs) in {"active", "addressable"}:
        appendices.update({"AppE", "AppF", "AppI", "AppM"})
    if infer_d6_state(record, basis_refs) in {"active", "addressable"}:
        appendices.update({"AppA", "AppB", "AppI", "AppM"})
    if any(token in relative_path for token in ("\\05_level_5_", "\\06_level_6_", "\\07_level_7_", "q ingress", "appq")):
        appendices.add("AppQ")
    if any(token in relative_path for token in ("quarantine", "conflict", "boundary", "earth", "qo")):
        appendices.add("AppK")
    if any(token in relative_path for token in ("seed-6d", "seed-7d", "h6", "h7", "4d+", "container_formats", "persisted")):
        appendices.add("AppN")
    if any(token in relative_path for token in ("deploy", "stable return", "appo", "appp", "publication")):
        appendices.add("AppP")
    return sorted(appendices)


def infer_return_targets(record: dict[str, Any], appendix_support: list[str]) -> list[str]:
    relative_path = record.get("relative_path", "").lower().replace("/", "\\")
    targets = list(CHAPTER_RETURN_ANCHORS)
    targets.extend(REPLAY_APPENDIX_ANCHORS)
    if "AppK" in appendix_support or any(token in relative_path for token in ("conflict", "quarantine", "qo", "reverse_overlay")):
        targets.append("AppK")
    if "AppN" in appendix_support or any(token in relative_path for token in ("seed-6d", "seed-7d", "h6", "h7", "4d+")):
        targets.append("AppN")
    if "AppQ" in appendix_support and any(token in relative_path for token in ("q ingress", "appq", "\\05_level_5_")):
        targets.append("AppQ")
    deduped: list[str] = []
    for target in targets:
        if target not in deduped:
            deduped.append(target)
    return deduped


def infer_metro_levels(record: dict[str, Any], d5_state: str, d6_state: str) -> list[int]:
    levels = {1, 2, 3, 4}
    if d5_state in {"active", "addressable"}:
        levels.add(5)
    if d6_state in {"active", "addressable"}:
        levels.add(6)
    relative_path = record.get("relative_path", "").lower().replace("/", "\\")
    if any(token in relative_path for token in ("\\07_7d_cross_agent_seed", "\\07_level_7_", "seed-7d", "h7")):
        levels.add(7)
    return sorted(levels)


def infer_dimensional_bindings(record: dict[str, Any], body_node: dict[str, Any], basis_refs: list[str]) -> dict[str, Any]:
    relative_path = record.get("relative_path", "")
    folder_scope = relative_path.rsplit("\\", 1)[0] if "\\" in relative_path else record.get("top_level", "")
    d5_state = infer_d5_state(record, basis_refs)
    d6_state = infer_d6_state(record, basis_refs)
    return {
        "d3_ingress": {
            "stage": "3D_INGRESS",
            "body_id": body_node["body_id"],
            "folder_scope": folder_scope,
            "station_role": body_node["station_role"],
            "entry_line": body_node["entry_line"],
            "transfer_hubs": body_node["transfer_hubs"],
            "feeds_basis": basis_refs,
            "nearest_metro_level": 1,
            "replay_ref": "14_3D_INGRESS_NETWORK/04_reentry_into_4d_native.md",
        },
        "d4_native": {
            "stage": "4D_NATIVE",
            "compiled_basis_refs": basis_refs,
            "matrix_surface": "05_MATRIX_16X16/00_INDEX.md",
            "metro_surface": "07_METRO_STACK/02_level_3_deeper_neural_map.md",
            "active": True,
        },
        "d5_overlay": {
            "stage": "5D_COMPRESSION",
            "owner": "Fire",
            "state": d5_state,
            "control_refs": [
                "00_CONTROL/06_FIRE_5D_6D_EXTENSION.md",
                "07_METRO_STACK/05_level_5_mobius_bridge_map.md",
            ],
        },
        "d6_overlay": {
            "stage": "6D_WEAVE",
            "owners": ["Water", "Air", "Earth"],
            "state": d6_state,
            "control_refs": [
                "11_6D_WATER_CONTROL/00_INDEX.md",
                "12_6D_AIR_CONTROL/00_INDEX.md",
                "13_6D_EARTH_CONTROL/00_INDEX.md",
                "13_6D_H6_CONVERGENCE/00_INDEX.md",
            ],
        },
    }


def infer_metro_bindings(record: dict[str, Any], body_node: dict[str, Any], basis_refs: list[str], appendix_support: list[str]) -> dict[str, Any]:
    d5_state = infer_d5_state(record, basis_refs)
    d6_state = infer_d6_state(record, basis_refs)
    active_levels = infer_metro_levels(record, d5_state, d6_state)
    metro_refs = [
        "14_3D_INGRESS_NETWORK/03_local_metro_entry_routes.md",
        "07_METRO_STACK/00_level_1_core_metro_map.md",
        "07_METRO_STACK/01_level_2_deep_emergence_metro_map.md",
        "07_METRO_STACK/02_level_3_deeper_neural_map.md",
        "07_METRO_STACK/03_level_4_transcendence_metro_map.md",
    ]
    if 5 in active_levels:
        metro_refs.append("07_METRO_STACK/05_level_5_mobius_bridge_map.md")
    if 6 in active_levels:
        metro_refs.append("07_METRO_STACK/06_level_6_hologram_weave_map.md")
    if 7 in active_levels:
        metro_refs.append("07_METRO_STACK/07_level_7_next_synthesis_seed_map.md")
    return {
        "ingress_line": body_node["entry_line"],
        "transfer_hubs": body_node["transfer_hubs"],
        "active_metro_levels": active_levels,
        "metro_refs": metro_refs,
        "appendix_refs": appendix_support,
        "return_targets": infer_return_targets(record, appendix_support),
        "line_role": body_node["station_role"],
    }


def infer_control_bindings(record: dict[str, Any], basis_refs: list[str], docs_gate_status: str) -> dict[str, Any]:
    relative_path = record.get("relative_path", "")
    canonical_status = infer_canonical_status(relative_path)
    drift_status = "historical-compat-only" if canonical_status == "historical_earth_6d_compat" else "current"
    return {
        "basis_refs": basis_refs,
        "truth_state": "NEAR",
        "docs_gate": docs_gate_status,
        "canonical_status": canonical_status,
        "drift_status": drift_status,
        "earth_package_root": EARTH_CANONICAL_PATH,
    }


def apply_dimensional_backplane(record: dict[str, Any], docs_gate_status: str = "BLOCKED") -> dict[str, Any]:
    enriched = dict(record)
    body_node = body_node_for_top_level(record.get("top_level", ""))
    basis_refs = infer_basis_refs(record)
    appendix_support = infer_appendix_support(record, body_node, basis_refs)
    enriched["dimensional_bindings"] = infer_dimensional_bindings(record, body_node, basis_refs)
    enriched["metro_bindings"] = infer_metro_bindings(record, body_node, basis_refs, appendix_support)
    enriched["control_bindings"] = infer_control_bindings(record, basis_refs, docs_gate_status)
    return enriched


def summarize_backplane(records: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    by_d3_line: dict[str, int] = {}
    by_d5_state: dict[str, int] = {}
    by_d6_state: dict[str, int] = {}
    by_canonical_status: dict[str, int] = {}
    for record in records:
        d3 = record.get("dimensional_bindings", {}).get("d3_ingress", {})
        d5 = record.get("dimensional_bindings", {}).get("d5_overlay", {})
        d6 = record.get("dimensional_bindings", {}).get("d6_overlay", {})
        control = record.get("control_bindings", {})
        d3_line = d3.get("entry_line", "UNKNOWN")
        d5_state = d5.get("state", "UNKNOWN")
        d6_state = d6.get("state", "UNKNOWN")
        canonical_status = control.get("canonical_status", "UNKNOWN")
        by_d3_line[d3_line] = by_d3_line.get(d3_line, 0) + 1
        by_d5_state[d5_state] = by_d5_state.get(d5_state, 0) + 1
        by_d6_state[d6_state] = by_d6_state.get(d6_state, 0) + 1
        by_canonical_status[canonical_status] = by_canonical_status.get(canonical_status, 0) + 1
    return {
        "by_d3_line": dict(sorted(by_d3_line.items(), key=lambda item: (-item[1], item[0]))),
        "by_d5_state": dict(sorted(by_d5_state.items(), key=lambda item: (-item[1], item[0]))),
        "by_d6_state": dict(sorted(by_d6_state.items(), key=lambda item: (-item[1], item[0]))),
        "by_canonical_status": dict(sorted(by_canonical_status.items(), key=lambda item: (-item[1], item[0]))),
    }
