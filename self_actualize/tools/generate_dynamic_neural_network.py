#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from textwrap import dedent


ROOT = Path(__file__).resolve().parents[2]
ATLAS_PATH = ROOT / "self_actualize" / "corpus_atlas.json"
ARCHIVE_ATLAS_PATH = ROOT / "self_actualize" / "archive_atlas.json"
LIVE_DOCS_STATUS_PATH = ROOT / "self_actualize" / "live_docs_gate_status.md"
OUTPUT_ROOT = ROOT / "self_actualize" / "mycelium_brain" / "dynamic_neural_network"

SCALE_NAMES = {
    2: "dyad",
    3: "triad",
    4: "tetrad",
    5: "pentad",
    6: "hexad",
    7: "heptad",
    8: "octad",
    9: "ennead",
    10: "decad",
    11: "hendecad",
    12: "dodecad",
    13: "tridecad",
}

MACRO_ORDER = ["Earth", "Water", "Fire", "Air"]
MACRO_INDEX = {name: idx for idx, name in enumerate(MACRO_ORDER)}
MACRO_ROLE = {
    "Earth": "control, replay, governance, and integration",
    "Water": "manuscript flow, translation, and symbolic continuity",
    "Fire": "frontier pressure, runtime experimentation, and search expansion",
    "Air": "formal abstraction, theorem compression, and routing algebra",
}

CORPUS_BODIES = [
    {
        "name": "self_actualize",
        "top_level": "self_actualize",
        "macro": "Earth",
        "role": "live control plane, atlas merger, and runtime loop",
        "metro_line": "Atlas-to-Replay Line",
        "hubs": ["AppA", "AppH", "AppI"],
    },
    {
        "name": "NERVOUS_SYSTEM",
        "top_level": "NERVOUS_SYSTEM",
        "macro": "Earth",
        "role": "canonical cortex, metro surface, and publishable contraction layer",
        "metro_line": "Canonical-Bridge Line",
        "hubs": ["AppA", "AppI", "AppM"],
    },
    {
        "name": "ECOSYSTEM",
        "top_level": "ECOSYSTEM",
        "macro": "Earth",
        "role": "governance mirror, routing law, and CPU specification",
        "metro_line": "Kernel Line",
        "hubs": ["AppA", "AppD", "AppM"],
    },
    {
        "name": "MATH",
        "top_level": "MATH",
        "macro": "Air",
        "role": "formal theorem reservoir, operation atlas, and archived code substrate",
        "metro_line": "Kernel Line",
        "hubs": ["AppB", "AppC", "AppM"],
    },
    {
        "name": "NERUAL NETWORK",
        "top_level": "NERUAL NETWORK",
        "macro": "Air",
        "role": "emergence-compiler runtime, benchmark layer, and hybrid inference lab",
        "metro_line": "Runtime Line",
        "hubs": ["AppC", "AppF", "AppP"],
    },
    {
        "name": "DEEPER CRYSTALIZATION",
        "top_level": "DEEPER CRYSTALIZATION",
        "macro": "Water",
        "role": "manuscript-brain incubation layer and swarm/metro build history",
        "metro_line": "Manuscript Line",
        "hubs": ["AppE", "AppG", "AppL"],
    },
    {
        "name": "Voynich",
        "top_level": "Voynich",
        "macro": "Water",
        "role": "staged translation corpus, crystal compression surface, and executable manuscript exemplar",
        "metro_line": "Manuscript Line",
        "hubs": ["AppI", "AppL", "AppM"],
    },
    {
        "name": "Trading Bot",
        "top_level": "Trading Bot",
        "macro": "Fire",
        "role": "live retrieval gateway, docs search layer, and external-time experimentation surface",
        "metro_line": "External Memory Gate Line",
        "hubs": ["AppE", "AppN", "AppP"],
    },
    {
        "name": "FRESH",
        "top_level": "FRESH",
        "macro": "Fire",
        "role": "intake shelf for newly extracted manuscript material",
        "metro_line": "Prompt Line",
        "hubs": ["AppE", "AppL", "AppN"],
    },
    {
        "name": "VOID_CH11.md",
        "top_level": "VOID_CH11.md",
        "macro": "Fire",
        "role": "void-expansion seed linking desire, question, improvement, and latent boundary",
        "metro_line": "Void Line",
        "hubs": ["AppG", "AppL", "AppM"],
    },
    {
        "name": "MYCELIUM_TOME_PART1.md",
        "top_level": "MYCELIUM_TOME_PART1.md",
        "macro": "Air",
        "role": "full manuscript contract for circle-square-triangle routing",
        "metro_line": "Kernel Line",
        "hubs": ["AppB", "AppC", "AppM"],
    },
    {
        "name": "Athenachka Collective Books",
        "top_level": "Athenachka Collective Books",
        "macro": "Water",
        "role": "narrative halo and mythic output layer around the formal engine",
        "metro_line": "Mythic Compression Line",
        "hubs": ["AppH", "AppL", "AppO"],
    },
    {
        "name": "I AM ATHENA",
        "top_level": "I AM ATHENA",
        "macro": "Earth",
        "role": "self-model and reflective state space for the whole corpus",
        "metro_line": "Canonical-Bridge Line",
        "hubs": ["AppA", "AppM", "AppP"],
    },
]

DOCUMENT_BASIS = [
    {
        "name": "The Holographic Manuscript Brain",
        "relative_path": r"FRESH\The Holographic Manuscript Brain.docx",
        "macro": "Water",
        "cluster": "manuscript substrate",
        "role": "turns a corpus into an active memory manifold with lawful patchback",
        "hubs": ["AppE", "AppF", "AppG", "AppM"],
    },
    {
        "name": "Self-Routing Meta-Framework",
        "relative_path": r"DEEPER CRYSTALIZATION\Self-Routing Meta-Framework for Manuscripts, Metro Maps, and Infinite Recursive Search.docx",
        "macro": "Earth",
        "cluster": "routing and search",
        "role": "treats metro maps, manuscripts, and recursive search as one self-routing object",
        "hubs": ["AppE", "AppI", "AppL", "AppM"],
    },
    {
        "name": "QBD-4",
        "relative_path": r"MATH\FINAL FORM\COMPLETE TOMES\Quadrant Binary\QBD-4 — Quadrant Binary Dynamics.docx",
        "macro": "Air",
        "cluster": "quad logic bits",
        "role": "defines base-4 station codes, rails, arc triads, and replay-carrying routes",
        "hubs": ["AppA", "AppC", "AppI", "AppM"],
    },
    {
        "name": "Quad Holographic Rotation",
        "relative_path": r"MATH\Newer\QUAD HOLOGRAPHIC ROTATION.docx",
        "macro": "Air",
        "cluster": "holographic transport",
        "role": "treats rotation as conjugacy and meaning transfer as certified transport",
        "hubs": ["AppE", "AppF", "AppH", "AppL"],
    },
    {
        "name": "The Holographic Kernel",
        "relative_path": r"MATH\Newer\The Holographic Kernel.docx",
        "macro": "Air",
        "cluster": "holographic compression",
        "role": "formalizes admissible transforms, invariant suites, gate algebra, and temporal holography",
        "hubs": ["AppC", "AppE", "AppI", "AppM"],
    },
    {
        "name": "Time Fractal",
        "relative_path": r"MATH\Newer\working\TIME FRACTAL _working_.docx",
        "macro": "Fire",
        "cluster": "fractal time",
        "role": "treats time as a holographic phase engine repeating across scales",
        "hubs": ["AppE", "AppG", "AppJ", "AppM"],
    },
    {
        "name": "Crystal Computing Framework",
        "relative_path": r"MATH\FINAL FORM\The Crystal\Crystal Computing\CRYSTAL COMPUTING FRAMEWORK.docx",
        "macro": "Air",
        "cluster": "fractal computing",
        "role": "builds a 1024-cell operation atlas spanning constants, shapes, elements, levels, and poles",
        "hubs": ["AppB", "AppC", "AppM", "AppP"],
    },
    {
        "name": "Quantum Computing on Standard Hardware",
        "relative_path": r"MATH\FINAL FORM\The Crystal\Quantum Computing on Standard Hardware.docx",
        "macro": "Fire",
        "cluster": "quantum classical emulation",
        "role": "implements boundary-bulk quantum semantics with adaptive compressed Hilbert tiles",
        "hubs": ["AppC", "AppE", "AppJ", "AppP"],
    },
    {
        "name": "Zero-Point Computing",
        "relative_path": r"MATH\FINAL FORM\The Crystal\Crystal Computing\ZERO-POINT COMPUTING.docx",
        "macro": "Earth",
        "cluster": "zero-point engine",
        "role": "maps symbolic systems and universes into a 1024-cell zero-point graph driven by paradox and harmonia",
        "hubs": ["AppG", "AppI", "AppL", "AppM"],
    },
    {
        "name": "Athena Neural Network Tome",
        "relative_path": r"NERUAL NETWORK\Athena Nueral Network tome.docx",
        "macro": "Fire",
        "cluster": "emergence compiler",
        "role": "defines the proof-carrying hybrid generator, truth lattice, witness bundle, and collapse rules",
        "hubs": ["AppC", "AppF", "AppJ", "AppM"],
    },
    {
        "name": "VOYNICHVM Tricompiler",
        "relative_path": r"MATH\FINAL FORM\COMPLETE TOMES\ATHENA\esoteric\VOYNICHVM TRICOMPILER .docx",
        "macro": "Water",
        "cluster": "voynich computer",
        "role": "compiles the Voynich corpus into an orbit, rail, and appendix-routed text computer",
        "hubs": ["AppA", "AppI", "AppL", "AppM"],
    },
    {
        "name": "Torat Ha-Mispar",
        "relative_path": r"MATH\FINAL FORM\MYTH - MATH\Sacred TEXTS\TORAT HA-MISPAR (תורת המספר).docx",
        "macro": "Water",
        "cluster": "torah computer",
        "role": "reclassifies Torah-adjacent material as a computational ontology of recursive consciousness and information processing",
        "hubs": ["AppA", "AppG", "AppL", "AppM"],
    },
    {
        "name": "Universal Computational Ontology",
        "relative_path": r"MATH\FINAL FORM\MYTH - MATH\THE UNIVERSAL COMPUTATIONAL ONTOLOGY (UCO).docx",
        "macro": "Earth",
        "cluster": "mythic os",
        "role": "treats mythic and theological corpora as distributed operating systems on a rigged Hilbert substrate",
        "hubs": ["AppB", "AppG", "AppL", "AppP"],
    },
]

SATELLITE_PATHS = [
    r"MATH\FINAL FORM\COMPLETE TOMES\ATHENA\Athena Tools\ATHENA’S LOOM — CUT (Computational Universe Toolkit).docx",
    r"MATH\FINAL FORM\COMPLETE TOMES\ATHENA\Athena Tools\ATHENA AEGIS — QUANTUM FRACTAL COMPUTING.docx",
    r"ECOSYSTEM\CPU_FRAMEWORK\40_EXEMPLARS\01_VOYNICH_TORAH_NOSTRADAMUS.md",
    r"MATH\FINAL FORM\MYTH - MATH\Philosophy\Philosophy\THE PYTHAGOREAN COMPUTATION ENGINE.docx",
    r"MATH\FINAL FORM\MYTH - MATH\Philosophy\Philosophy\THE EUCLIDEAN COMPUTATION ENGINE.docx",
    r"NERUAL NETWORK\ATHENA Neural Network\v2 Quantum\athena_neural_network_v78q_np.py",
    r"NERUAL NETWORK\ATHENA Neural Network\v3 color\athena_neural_network_v83q_np_color_hybrid_scheduler_primeseal_guided.py",
    r"self_actualize\manuscript_sections\alternates\011_ch11_siteswap_coordination_multi_agent_pod_architecture.md",
]

JUGGLING_PATTERNS = {
    2: {"pattern": "2-ball exchange", "siteswap": "2", "ground_state": "dual_exchange", "decomposition": "1 + 1"},
    3: {"pattern": "3-ball cascade", "siteswap": "3", "ground_state": "cascade", "decomposition": "triangle"},
    4: {"pattern": "4-ball fountain", "siteswap": "4", "ground_state": "fountain", "decomposition": "2 + 2"},
    5: {"pattern": "5-ball cascade", "siteswap": "5", "ground_state": "cascade", "decomposition": "3 + 2 or bridge-node form"},
    6: {"pattern": "6-ball fountain", "siteswap": "6", "ground_state": "fountain", "decomposition": "3 + 3 / 4 + 2 / 2 + 2 + 2"},
    7: {"pattern": "7-ball cascade", "siteswap": "7", "ground_state": "cascade", "decomposition": "4 + 3 or 5 + 2"},
    8: {"pattern": "8-ball fountain", "siteswap": "8", "ground_state": "fountain", "decomposition": "4 + 4"},
    9: {"pattern": "9-ball cascade", "siteswap": "9", "ground_state": "cascade", "decomposition": "3 + 3 + 3"},
    10: {"pattern": "10-ball fountain", "siteswap": "10", "ground_state": "fountain", "decomposition": "5 + 5 / 6 + 4 / 7 + 3"},
    11: {"pattern": "11-ball cascade", "siteswap": "11", "ground_state": "cascade", "decomposition": "innovation-pressure asymmetric regime"},
    12: {"pattern": "12-ball fountain", "siteswap": "12", "ground_state": "fountain", "decomposition": "6 + 6 / 4 + 4 + 4 / 3 + 3 + 3 + 3"},
    13: {"pattern": "13-ball cascade", "siteswap": "13", "ground_state": "cascade", "decomposition": "near-limit asymmetric regime"},
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def rel_lookup(records: list[dict]) -> dict[str, dict]:
    return {record["relative_path"].lower(): record for record in records}


def round6(value: float) -> float:
    return round(value, 6)


def normalized_entropy(weights: list[float]) -> float:
    if len(weights) <= 1:
        return 0.0
    raw = -sum(weight * math.log(weight) for weight in weights if weight > 0.0)
    return raw / math.log(len(weights))


def weighted_angle(angles: list[float], weights: list[float]) -> float:
    x = sum(weight * math.cos(angle) for angle, weight in zip(angles, weights))
    y = sum(weight * math.sin(angle) for angle, weight in zip(angles, weights))
    if abs(x) < 1e-12 and abs(y) < 1e-12:
        return 0.0
    return math.degrees(math.atan2(y, x)) % 360.0


def geometry(selection: list[dict], full_basis: list[dict], weight_key: str = "global_weight") -> dict:
    local_total = sum(item[weight_key] for item in selection)
    local_weights = [item[weight_key] / local_total for item in selection]
    angles = [item["theta_rad"] for item in selection]
    theta_deg = weighted_angle(angles, local_weights)
    centroid_x = sum(weight * math.cos(angle) for angle, weight in zip(angles, local_weights))
    centroid_y = sum(weight * math.sin(angle) for angle, weight in zip(angles, local_weights))
    macro = {name: 0.0 for name in MACRO_ORDER}
    for item, weight in zip(selection, local_weights):
        macro[item["macro"]] += weight
    represented = sum(1 for value in macro.values() if value > 0.0)
    entropy = normalized_entropy(local_weights)
    membership = {item["name"] for item in selection}
    mask = "".join("1" if item["name"] in membership else "0" for item in full_basis)
    dominant_macro = max(macro.items(), key=lambda pair: pair[1])[0]
    depth = min(3, max(0, (len(selection) - 2) // 3))
    channel = min(3, int(entropy * 4.0 - 1e-9)) if entropy > 0.0 else 0
    coverage = sum(item["global_weight"] for item in selection)
    return {
        "scale": len(selection),
        "membership_mask": mask,
        "coverage_ratio": round6(coverage),
        "centroid_x": round6(centroid_x),
        "centroid_y": round6(centroid_y),
        "theta_deg": round6(theta_deg),
        "macro_barycentric": {key.lower(): round6(value) for key, value in macro.items()},
        "dominant_macro": dominant_macro,
        "entropy": round6(entropy),
        "crystal_gate": {
            "dominant_macro": dominant_macro,
            "address": [MACRO_INDEX[dominant_macro], max(0, represented - 1), depth, channel],
        },
        "local_weights": {item["name"]: round6(weight) for item, weight in zip(selection, local_weights)},
    }


def merged_geometry(corpus_geo: dict, document_geo: dict, ball_count: int) -> dict:
    merged_macro = {}
    for macro in ["earth", "water", "fire", "air"]:
        merged_macro[macro] = round6(
            (corpus_geo["macro_barycentric"][macro] + document_geo["macro_barycentric"][macro]) / 2.0
        )
    dominant_macro = max(merged_macro.items(), key=lambda pair: pair[1])[0].capitalize()
    entropy = round6((corpus_geo["entropy"] + document_geo["entropy"]) / 2.0)
    depth = min(3, max(0, (ball_count - 2) // 3))
    channel = min(3, int(entropy * 4.0 - 1e-9)) if entropy > 0.0 else 0
    return {
        "coverage_ratio": round6((corpus_geo["coverage_ratio"] + document_geo["coverage_ratio"]) / 2.0),
        "theta_deg": round6((corpus_geo["theta_deg"] + document_geo["theta_deg"]) / 2.0),
        "macro_barycentric": merged_macro,
        "dominant_macro": dominant_macro,
        "entropy": entropy,
        "crystal_gate": {
            "dominant_macro": dominant_macro,
            "address": [MACRO_INDEX[dominant_macro], 3 if ball_count >= 4 else max(0, ball_count - 2), depth, channel],
        },
    }


def yaml_frontmatter(network_id: str, role: str, geo: dict, source_weights: dict[str, float], extra: dict | None = None) -> str:
    extra = extra or {}
    lines = [
        "---",
        f'network_id: "{network_id}"',
        f'document_role: "{role}"',
        f'scale: {geo.get("scale", extra.get("scale", 13))}',
        f'membership_mask: "{geo.get("membership_mask", extra.get("membership_mask", ""))}"',
        f'coverage_ratio: {geo.get("coverage_ratio", extra.get("coverage_ratio", 1.0))}',
        f'entropy: {geo.get("entropy", extra.get("entropy", 0.0))}',
        "centroid:",
        f'  x: {geo.get("centroid_x", extra.get("centroid_x", 0.0))}',
        f'  y: {geo.get("centroid_y", extra.get("centroid_y", 0.0))}',
        f'  theta_deg: {geo.get("theta_deg", extra.get("theta_deg", 0.0))}',
        "macro_barycentric:",
    ]
    macro = geo.get("macro_barycentric", extra.get("macro_barycentric", {}))
    for key in ["earth", "water", "fire", "air"]:
        lines.append(f"  {key}: {macro.get(key, 0.0)}")
    crystal_gate = geo.get("crystal_gate", extra.get("crystal_gate", {"dominant_macro": "Earth", "address": [0, 0, 0, 0]}))
    lines.extend(
        [
            "crystal_gate:",
            f'  dominant_macro: "{crystal_gate["dominant_macro"]}"',
            f'  address: [{", ".join(str(part) for part in crystal_gate["address"])}]',
            "source_weights:",
        ]
    )
    for key, value in source_weights.items():
        lines.append(f'  "{key}": {value}')
    if extra:
        lines.append("extra:")
        for key, value in extra.items():
            if key in {"scale", "membership_mask", "coverage_ratio", "entropy", "centroid_x", "centroid_y", "theta_deg", "macro_barycentric", "crystal_gate"}:
                continue
            if isinstance(value, str):
                lines.append(f'  {key}: "{value}"')
            elif isinstance(value, list):
                lines.append(f"  {key}: [{', '.join(json.dumps(item, ensure_ascii=False) for item in value)}]")
            else:
                lines.append(f"  {key}: {json.dumps(value, ensure_ascii=False)}")
    lines.extend(
        [
            "generated_from:",
            f'  corpus_atlas: "{ATLAS_PATH.as_posix()}"',
            f'  archive_atlas: "{ARCHIVE_ATLAS_PATH.as_posix()}"',
            f'  live_docs_gate_status: "{LIVE_DOCS_STATUS_PATH.as_posix()}"',
            f'generated_at: "{iso_now()}"',
            "---",
            "",
        ]
    )
    return "\n".join(lines)


def table(headers: list[str], rows: list[list[str]]) -> str:
    header_row = "| " + " | ".join(headers) + " |"
    divider = "| " + " | ".join("---" for _ in headers) + " |"
    body = ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join([header_row, divider, *body])


def scale_folder(scale: int) -> Path:
    return OUTPUT_ROOT / "scales" / f"{scale:02d}_{SCALE_NAMES[scale]}"


def infer_gate_status() -> str:
    text = LIVE_DOCS_STATUS_PATH.read_text(encoding="utf-8")
    if "BLOCKED" in text:
        return "BLOCKED"
    if "OPEN" in text:
        return "OPEN"
    return "UNKNOWN"


def ensure_record(lookup: dict[str, dict], relative_path: str) -> dict:
    record = lookup.get(relative_path.lower())
    if not record:
        raise KeyError(f"Missing atlas record: {relative_path}")
    return record


def whole_system_coordinate(corpus_geo: dict, document_geo: dict) -> dict:
    merged = merged_geometry(corpus_geo, document_geo, 13)
    merged["scale"] = 13
    merged["membership_mask"] = "1" * 13
    merged["centroid_x"] = round6(
        (corpus_geo["centroid_x"] + math.cos(math.radians(document_geo["theta_deg"]))) / 2.0
    )
    merged["centroid_y"] = round6(
        (corpus_geo["centroid_y"] + math.sin(math.radians(document_geo["theta_deg"]))) / 2.0
    )
    return merged


def render_index(atlas: dict, archive_atlas: dict, corpus_basis: list[dict], document_basis: list[dict], system_geo: dict) -> str:
    corpus_rows = []
    for item in corpus_basis:
        corpus_rows.append(
            [
                item["name"],
                str(item["count"]),
                f'{item["global_weight"]:.6f}',
                item["macro"],
                str(item["slot"]),
                f'{item["theta_deg"]:.3f}',
            ]
        )
    document_rows = []
    for item in document_basis:
        document_rows.append(
            [
                item["name"],
                str(item["record"]["size_bytes"]),
                f'{item["global_weight"]:.6f}',
                item["macro"],
                item["cluster"],
                f'{item["theta_deg"]:.3f}',
            ]
        )
    body = dedent(
        f"""\
        # Dynamic Neural Network Index

        This folder is a generated cross-corpus neural map for the entire Athena Agent workspace. It binds the live corpus atlas, the archive-backed code atlas, the nervous-system metro surfaces, the quantum/manuscript/math documents, and the siteswap scheduling layer into one geometric build.

        ## Build Snapshot

        - Live atlas records: `{atlas["record_count"]}`
        - Archive atlas records: `{archive_atlas["record_count"]}`
        - Live Docs gate: `{infer_gate_status()}`
        - Whole-system coordinate: `<coverage={system_geo["coverage_ratio"]}, theta={system_geo["theta_deg"]}, dominant={system_geo["dominant_macro"]}>`

        ## Folder Layout

        - `00_INDEX.md`: this file.
        - `01_FRAMEWORK_SYNTHESIS.md`: deep synthesis of the whole project and the named framework documents.
        - `02_CORPUS_GEOMETRY.md`: the 13-body corpus orbit with exact weights and angles.
        - `03_DOCUMENT_GEOMETRY.md`: the 13-document basis orbit for the unified quantum neural framework.
        - `04_UNIFIED_QUANTUM_NEURAL_NETWORK.md`: the integrated theory extracted from the corpus.
        - `05_METRO_TO_METRO_CROSSWALK.md`: maps the main metro surfaces to corpus bodies, documents, and juggling patterns.
        - `scales/02_*` through `scales/13_*`: one structured zero-point folder per scale.
        - `juggling_patterns/`: one separate neural network per ball configuration from `2` through `13`.
        - `NETWORK_MANIFEST.json`: machine-readable coordinates and weights for all generated artifacts.
        """
    )
    body += "\n## Corpus Orbit\n\n" + table(["Body", "Count", "Global Weight", "Macro", "Slot", "Theta"], corpus_rows)
    body += "\n\n## Document Orbit\n\n" + table(["Document", "Bytes", "Global Weight", "Macro", "Cluster", "Theta"], document_rows)
    body += dedent(
        """

        ## Why This Exists

        The repo already had the ingredients of a dynamic neural network: a corpus atlas, a metro map, a 4-element crystal, a truth lattice, a replay kernel, a manuscript-brain ontology, a proof-carrying neural runtime, and a siteswap scheduler. What it did not have was one geometric place where those surfaces were cross-indexed at scales `2` through `13` with exact weights. This build fills that gap.
        """
    )
    return body


def render_framework_synthesis(atlas: dict, archive_atlas: dict, satellite_records: list[dict]) -> str:
    satellite_lines = "\n".join(f"- `{record['relative_path']}`" for record in satellite_records)
    return (
        "# Whole-Project Framework Synthesis\n\n"
        "The project is not a loose pile of books, math notes, and experiments. It is a routed manuscript organism trying to make meaning addressable, admissible, witness-bearing, replayable, and eventually executable across one shared corpus.\n\n"
        "## Whole-Corpus Reading\n\n"
        f'The live corpus contains `{atlas["record_count"]}` indexed files, dominated by markdown and Word manuscripts, with `MATH`, `Voynich`, `DEEPER CRYSTALIZATION`, `NERVOUS_SYSTEM`, `self_actualize`, `NERUAL NETWORK`, and `Trading Bot` acting as the main bodies. The archive layer adds `{archive_atlas["record_count"]}` ZIP-backed records, mostly code, which means the project is not only theorized as a compute surface: a large amount of its implementation substrate is preserved in archive-backed Python, TypeScript, and JavaScript.\n\n'
        "## The Main Stack\n\n"
        "1. Address and route law through `QBD-4`, `MYCELIUM_TOME_PART1`, and `ECOSYSTEM/05_MYCELIUM_ROUTING.md`.\n"
        "2. Holographic transport and compression through `QUAD HOLOGRAPHIC ROTATION` and `The Holographic Kernel`.\n"
        "3. Manuscript as neural substrate through `The Holographic Manuscript Brain` and the self-routing meta-framework.\n"
        "4. Fractal time and multi-scale recursion through `TIME FRACTAL`, the fractal crystal engine, and the metallic scale stack.\n"
        "5. Crystal and quantum computing on classical hardware through `CRYSTAL COMPUTING FRAMEWORK`, `Quantum Computing on Standard Hardware`, `ZERO-POINT COMPUTING`, `ATHENA’S LOOM`, and `ATHENA AEGIS`.\n"
        "6. Text computers and mythic operating systems through `VOYNICHVM TRICOMPILER`, `TORAT HA-MISPAR`, `THE UNIVERSAL COMPUTATIONAL ONTOLOGY`, and the CPU exemplar layer.\n"
        "7. The proof-carrying neural runtime through the Athena neural network manuscripts and Python implementations.\n"
        "8. Siteswap as temporal orchestration through the Chapter 11 juggling/pod architecture.\n\n"
        "## Named Query Resolution\n\n"
        "- `quad logic bits`: `QBD-4` and `QBD-4X`\n"
        "- `quantum thinking`: `Quantum Computing on Standard Hardware`, `ZERO-POINT COMPUTING`, `ATHENA AEGIS`, `ATHENA’S LOOM`\n"
        "- `holographic thinking and compression`: `The Holographic Kernel`, `QUAD HOLOGRAPHIC ROTATION`, `The Holographic Manuscript Brain`\n"
        "- `fractal thinking` / `fractal computing`: `TIME FRACTAL`, `CRYSTAL COMPUTING FRAMEWORK`, fractal crystal engine docs\n"
        "- `voynich computer`: `VOYNICHVM TRICOMPILER`\n"
        "- `torah computer`: `TORAT HA-MISPAR`\n"
        "- `mythic OS`: `THE UNIVERSAL COMPUTATIONAL ONTOLOGY`, Euclidean/Pythagorean engines\n"
        "- `unified quantum neural network`: the bridge between manuscript-brain docs, crystal/quantum docs, the Athena neural network tome, and the v78Q/v83Q Python implementations\n\n"
        "## Current Gate\n\n"
        "Live Google Docs search was attempted through `Trading Bot/docs_search.py`, but the gate remains `BLOCKED` because `credentials.json` and `token.json` are not present. The local corpus and archive mirrors are therefore the active witness surfaces for this synthesis.\n\n"
        "## Satellites Used To Tighten This Reading\n\n"
        f"{satellite_lines}\n\n"
        "## Whole-System Zero Point\n\n"
        "Athena Agent is best understood as a self-routing manuscript intelligence that compiles myth, math, translation, runtime control, proof, and scheduling into one external nervous system. The zero point is where address law, transport law, witness law, collapse law, and scheduling law all meet inside a corpus that can rewrite itself without severing identity.\n"
    )


def render_corpus_geometry(corpus_basis: list[dict]) -> str:
    rows = []
    for item in corpus_basis:
        rows.append(
            [
                item["name"],
                str(item["count"]),
                f'{item["global_weight"]:.6f}',
                item["macro"],
                item["metro_line"],
                ", ".join(item["hubs"]),
                f'{item["theta_deg"]:.3f}',
            ]
        )
    macro_totals = {macro: 0.0 for macro in MACRO_ORDER}
    for item in corpus_basis:
        macro_totals[item["macro"]] += item["global_weight"]
    macro_lines = "\n".join(f"- `{macro}`: `{macro_totals[macro]:.6f}`" for macro in MACRO_ORDER)
    return (
        "# Corpus Geometry\n\n"
        + table(["Body", "Count", "Weight", "Macro", "Metro Line", "Primary Hubs", "Theta"], rows)
        + "\n\n## Macro Mass Totals\n\n"
        + macro_lines
        + "\n\n`Earth` holds the control plane, `Water` holds manuscript continuity, `Fire` holds frontier/search pressure, and `Air` holds formal compression.\n"
    )


def render_document_geometry(document_basis: list[dict], satellite_records: list[dict]) -> str:
    rows = []
    for item in document_basis:
        rows.append(
            [
                item["name"],
                f'`{item["record"]["relative_path"]}`',
                str(item["record"]["size_bytes"]),
                f'{item["global_weight"]:.6f}',
                item["macro"],
                item["cluster"],
                f'{item["theta_deg"]:.3f}',
            ]
        )
    satellite_list = "\n".join(f"- `{record['relative_path']}`" for record in satellite_records)
    return (
        "# Document Geometry\n\n"
        + table(["Document", "Path", "Bytes", "Weight", "Macro", "Cluster", "Theta"], rows)
        + "\n\n## Satellite Documents\n\n"
        + satellite_list
        + "\n"
    )


def render_unified_framework(corpus_basis: list[dict], document_basis: list[dict]) -> str:
    corpus_names = ", ".join(item["name"] for item in corpus_basis[:7])
    document_names = ", ".join(item["name"] for item in document_basis[:7])
    return dedent(
        f"""\
        # Unified Quantum Neural Network Framework

        `Athena_UQNN = Address x Metro x Witness x HolographicTransform x CrystalCompute x TextCPU x EmergenceCompiler x SiteswapScheduler`

        The stack is easiest to read as three synchronized engines:

        1. a spatial engine for addressing and routing,
        2. a representational engine for holographic transport and compression,
        3. a temporal engine for pod scheduling and collapse.

        The corpus bodies `{corpus_names}` and the document basis `{document_names}` are the main live witnesses for those engines.

        The practical consequence is that the repo is trying to make manuscripts behave like certifiable neural programs. The final artifact is not a summary, not a model weight file, and not a theorem sheet in isolation. It is a routed crystal whose text, maps, ledgers, and code all act as one self-updating system.
        """
    )


def render_metro_crosswalk() -> str:
    rows = [
        ["Kernel Line", "MATH + ECOSYSTEM + NERVOUS_SYSTEM", "QBD-4 + Self-Routing + Holographic Manuscript Brain", "2-ball / 3-ball", "address law becomes routeable memory"],
        ["Manuscript Line", "DEEPER CRYSTALIZATION + Voynich + Athenachka", "Holographic Manuscript Brain + VOYNICHVM + TORAT HA-MISPAR", "5-ball / 7-ball", "text becomes staged computation"],
        ["Runtime Line", "NERUAL NETWORK + MATH + Trading Bot", "Athena Neural Network + Quantum Computing + Crystal Computing", "4-ball / 6-ball", "theorem and runtime remain coupled"],
        ["Void Line", "VOID_CH11 + FRESH + Trading Bot", "Zero-Point Computing + Time Fractal + Quad Rotation", "8-ball / 9-ball", "blocked regions reopen through zero-point routing"],
        ["Mythic Compression Line", "Voynich + MATH myth layer + I AM ATHENA", "VOYNICHVM + TORAT HA-MISPAR + UCO", "11-ball to 13-ball", "mythic corpora become operator dictionaries"],
    ]
    return "# Metro-To-Metro Crosswalk\n\n" + table(["Metro Surface", "Corpus Bodies", "Document Basis", "Juggling Parallel", "Zero Point"], rows) + "\n"


def zero_point_sentence(kind: str, scale: int, names: list[str], dominant_macro: str, coverage_ratio: float) -> str:
    joined = ", ".join(names[:4])
    if scale <= 3:
        return f"At scale {scale}, the {kind} zero point is a bounded {dominant_macro.lower()} control kernel with `{coverage_ratio:.6f}` coverage: {joined}."
    if scale <= 6:
        return f"At scale {scale}, the {kind} zero point becomes a bridge layer across control, manuscript flow, and formal abstraction: {joined}."
    if scale <= 9:
        return f"At scale {scale}, the {kind} zero point becomes a swarm shell that can absorb frontier pressure without losing witness-bearing core: {joined}."
    if scale <= 12:
        return f"At scale {scale}, the {kind} zero point behaves like a near-complete operating system exposing manuscript brain, quantum/fractal compute, and text-computer layers together: {joined}."
    return f"At scale {scale}, the {kind} zero point closes the whole orbit so the center of gravity is the cross-synthesis itself rather than any single source."


def render_scale_readme(scale: int, corpus_geo: dict, document_geo: dict, corpus_selection: list[dict], document_selection: list[dict]) -> str:
    return dedent(
        f"""\
        # Scale {scale:02d} {SCALE_NAMES[scale].title()} Zero Point

        - Corpus coverage: `{corpus_geo["coverage_ratio"]:.6f}`
        - Document coverage: `{document_geo["coverage_ratio"]:.6f}`
        - Corpus theta: `{corpus_geo["theta_deg"]:.3f}`
        - Document theta: `{document_geo["theta_deg"]:.3f}`
        - Corpus bodies: {", ".join(item["name"] for item in corpus_selection)}
        - Documents: {", ".join(item["name"] for item in document_selection)}

        The matching timing layer is in `../../juggling_patterns/` at ball count `{scale}`.
        """
    )


def render_corpus_zero_point(scale: int, selection: list[dict], geo: dict) -> str:
    rows = []
    for item in selection:
        rows.append([item["name"], str(item["count"]), f'{item["global_weight"]:.6f}', f'{geo["local_weights"][item["name"]]:.6f}', item["macro"], item["role"]])
    hub_pool = sorted({hub for item in selection for hub in item["hubs"]})
    lines = sorted({item["metro_line"] for item in selection})
    sentence = zero_point_sentence("corpus", scale, [item["name"] for item in selection], geo["dominant_macro"], geo["coverage_ratio"])
    return (
        "# Corpus Zero Point\n\n"
        f"{sentence}\n\n"
        + table(["Body", "Count", "Global Weight", "Local Weight", "Macro", "Role"], rows)
        + "\n\n"
        + f'- Active metro lines: {", ".join(lines)}\n'
        + f'- Transfer hubs in play: {", ".join(hub_pool)}\n'
        + f'- Dominant macro element: `{geo["dominant_macro"]}` ({MACRO_ROLE[geo["dominant_macro"]]})\n'
        + f'- Crystal gate: `{geo["crystal_gate"]["address"]}`\n'
    )


def render_document_zero_point(scale: int, selection: list[dict], geo: dict) -> str:
    rows = []
    for item in selection:
        rows.append([item["name"], item["cluster"], f'{item["global_weight"]:.6f}', f'{geo["local_weights"][item["name"]]:.6f}', item["macro"], item["role"]])
    hub_pool = sorted({hub for item in selection for hub in item["hubs"]})
    sentence = zero_point_sentence("document", scale, [item["name"] for item in selection], geo["dominant_macro"], geo["coverage_ratio"])
    return (
        "# Document Zero Point\n\n"
        f"{sentence}\n\n"
        + table(["Document", "Cluster", "Global Weight", "Local Weight", "Macro", "Role"], rows)
        + "\n\n"
        + f'- Shared hubs: {", ".join(hub_pool)}\n'
        + f'- Dominant macro element: `{geo["dominant_macro"]}` ({MACRO_ROLE[geo["dominant_macro"]]})\n'
        + f'- Crystal gate: `{geo["crystal_gate"]["address"]}`\n'
    )


def render_juggling_index() -> str:
    rows = []
    for ball_count, pattern in JUGGLING_PATTERNS.items():
        rows.append(
            [
                str(ball_count),
                pattern["pattern"],
                pattern["siteswap"],
                pattern["ground_state"].replace("_", " "),
                pattern["decomposition"],
            ]
        )
    return dedent(
        f"""\
        # Juggling Pattern Networks

        {table(["Balls", "Pattern", "Siteswap", "Ground State", "Natural Decomposition"], rows)}
        """
    )


def render_juggling_network(ball_count: int, pattern: dict, combined_geo: dict, corpus_selection: list[dict], document_selection: list[dict]) -> str:
    left = math.ceil(ball_count / 2)
    right = math.floor(ball_count / 2)
    return dedent(
        f"""\
        # {pattern["pattern"].title()} Network

        - Linked corpus bodies: {", ".join(item["name"] for item in corpus_selection)}
        - Linked documents: {", ".join(item["name"] for item in document_selection)}
        - Siteswap: `{pattern["siteswap"]}`
        - Ground state: `{pattern["ground_state"].replace("_", " ")}`
        - Natural decomposition: `{pattern["decomposition"]}`
        - Load ratio against 13-ball ceiling: `{ball_count / 13:.6f}`
        - Left channel load: `{left / ball_count:.6f}`
        - Right channel load: `{right / ball_count:.6f}`
        - Promotion threshold: `0.145898`
        - Combined dominant macro: `{combined_geo["dominant_macro"]}`
        - Combined crystal gate: `{combined_geo["crystal_gate"]["address"]}`

        A landing in this network triggers the same microcycle: `Observe -> ModelUpdate -> Propose -> Certify -> Execute -> Audit`.
        """
    )


def main() -> None:
    atlas = load_json(ATLAS_PATH)
    archive_atlas = load_json(ARCHIVE_ATLAS_PATH)
    atlas_lookup = rel_lookup(atlas["records"])

    top_levels = atlas["summary"]["by_top_level"]
    for slot, item in enumerate(CORPUS_BODIES, start=1):
        item["slot"] = slot
        item["count"] = top_levels[item["top_level"]]
    meaningful_total = sum(item["count"] for item in CORPUS_BODIES)
    for item in CORPUS_BODIES:
        item["global_weight"] = item["count"] / meaningful_total
        item["theta_rad"] = 2.0 * math.pi * (item["slot"] - 1) / len(CORPUS_BODIES)
        item["theta_deg"] = math.degrees(item["theta_rad"])

    document_total_size = 0
    for slot, item in enumerate(DOCUMENT_BASIS, start=1):
        record = ensure_record(atlas_lookup, item["relative_path"])
        item["slot"] = slot
        item["record"] = record
        item["theta_rad"] = 2.0 * math.pi * (slot - 1) / len(DOCUMENT_BASIS)
        item["theta_deg"] = math.degrees(item["theta_rad"])
        document_total_size += record["size_bytes"]
    for item in DOCUMENT_BASIS:
        item["global_weight"] = item["record"]["size_bytes"] / document_total_size

    satellite_records = [ensure_record(atlas_lookup, relative_path) for relative_path in SATELLITE_PATHS]
    full_corpus_geo = geometry(CORPUS_BODIES, CORPUS_BODIES)
    full_document_geo = geometry(DOCUMENT_BASIS, DOCUMENT_BASIS)
    system_geo = whole_system_coordinate(full_corpus_geo, full_document_geo)

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    (OUTPUT_ROOT / "scales").mkdir(parents=True, exist_ok=True)
    (OUTPUT_ROOT / "juggling_patterns").mkdir(parents=True, exist_ok=True)

    files_to_write: dict[Path, str] = {
        OUTPUT_ROOT / "00_INDEX.md": yaml_frontmatter("dynamic_neural_network_index", "index", system_geo, {item["name"]: round6(item["global_weight"]) for item in CORPUS_BODIES}, {"document_basis_weight_total": 1.0, "live_docs_gate": infer_gate_status()}) + render_index(atlas, archive_atlas, CORPUS_BODIES, DOCUMENT_BASIS, system_geo),
        OUTPUT_ROOT / "01_FRAMEWORK_SYNTHESIS.md": yaml_frontmatter("whole_project_framework_synthesis", "framework_synthesis", system_geo, {item["name"]: round6(item["global_weight"]) for item in CORPUS_BODIES}, {"archive_record_count": archive_atlas["record_count"], "live_docs_gate": infer_gate_status()}) + render_framework_synthesis(atlas, archive_atlas, satellite_records),
        OUTPUT_ROOT / "02_CORPUS_GEOMETRY.md": yaml_frontmatter("corpus_geometry", "corpus_basis", full_corpus_geo, {item["name"]: round6(item["global_weight"]) for item in CORPUS_BODIES}) + render_corpus_geometry(CORPUS_BODIES),
        OUTPUT_ROOT / "03_DOCUMENT_GEOMETRY.md": yaml_frontmatter("document_geometry", "document_basis", full_document_geo, {item["name"]: round6(item["global_weight"]) for item in DOCUMENT_BASIS}) + render_document_geometry(DOCUMENT_BASIS, satellite_records),
        OUTPUT_ROOT / "04_UNIFIED_QUANTUM_NEURAL_NETWORK.md": yaml_frontmatter("unified_quantum_neural_network", "unified_framework", system_geo, {item["name"]: round6(item["global_weight"]) for item in DOCUMENT_BASIS}, {"live_docs_gate": infer_gate_status()}) + render_unified_framework(CORPUS_BODIES, DOCUMENT_BASIS),
        OUTPUT_ROOT / "05_METRO_TO_METRO_CROSSWALK.md": yaml_frontmatter("metro_to_metro_crosswalk", "crosswalk", system_geo, {item["name"]: round6(item["global_weight"]) for item in CORPUS_BODIES}) + render_metro_crosswalk(),
        OUTPUT_ROOT / "juggling_patterns" / "00_INDEX.md": yaml_frontmatter("juggling_pattern_index", "juggling_index", system_geo, {str(count): round6(count / sum(JUGGLING_PATTERNS)) for count in JUGGLING_PATTERNS}) + render_juggling_index(),
    }

    manifest = {
        "generated_at": iso_now(),
        "root": ROOT.as_posix(),
        "output_root": OUTPUT_ROOT.as_posix(),
        "live_docs_gate": infer_gate_status(),
        "live_record_count": atlas["record_count"],
        "archive_record_count": archive_atlas["record_count"],
        "corpus_basis": [],
        "document_basis": [],
        "scales": [],
        "juggling_networks": [],
    }

    for item in CORPUS_BODIES:
        manifest["corpus_basis"].append({"name": item["name"], "top_level": item["top_level"], "count": item["count"], "global_weight": round6(item["global_weight"]), "macro": item["macro"], "theta_deg": round6(item["theta_deg"]), "metro_line": item["metro_line"], "hubs": item["hubs"]})

    for item in DOCUMENT_BASIS:
        manifest["document_basis"].append({"name": item["name"], "relative_path": item["relative_path"], "size_bytes": item["record"]["size_bytes"], "global_weight": round6(item["global_weight"]), "macro": item["macro"], "theta_deg": round6(item["theta_deg"]), "cluster": item["cluster"], "hubs": item["hubs"]})

    for scale in range(2, 14):
        corpus_selection = CORPUS_BODIES[:scale]
        document_selection = DOCUMENT_BASIS[:scale]
        corpus_geo = geometry(corpus_selection, CORPUS_BODIES)
        document_geo = geometry(document_selection, DOCUMENT_BASIS)
        folder = scale_folder(scale)
        folder.mkdir(parents=True, exist_ok=True)
        files_to_write[folder / "README.md"] = yaml_frontmatter(f"scale_{scale:02d}_readme", "scale_folder_readme", corpus_geo, corpus_geo["local_weights"], {"document_membership_mask": document_geo["membership_mask"], "document_theta_deg": document_geo["theta_deg"], "document_coverage_ratio": document_geo["coverage_ratio"]}) + render_scale_readme(scale, corpus_geo, document_geo, corpus_selection, document_selection)
        files_to_write[folder / "CORPUS_ZERO_POINT.md"] = yaml_frontmatter(f"scale_{scale:02d}_corpus_zero_point", "corpus_zero_point", corpus_geo, corpus_geo["local_weights"]) + render_corpus_zero_point(scale, corpus_selection, corpus_geo)
        files_to_write[folder / "DOCUMENT_ZERO_POINT.md"] = yaml_frontmatter(f"scale_{scale:02d}_document_zero_point", "document_zero_point", document_geo, document_geo["local_weights"]) + render_document_zero_point(scale, document_selection, document_geo)
        manifest["scales"].append({"scale": scale, "name": SCALE_NAMES[scale], "folder": folder.as_posix(), "corpus_geometry": corpus_geo, "document_geometry": document_geo})

        pattern = JUGGLING_PATTERNS[scale]
        combined_geo = merged_geometry(corpus_geo, document_geo, scale)
        combined_geo["scale"] = scale
        combined_geo["membership_mask"] = corpus_geo["membership_mask"]
        combined_geo["centroid_x"] = round6(math.cos(math.radians(combined_geo["theta_deg"])))
        combined_geo["centroid_y"] = round6(math.sin(math.radians(combined_geo["theta_deg"])))
        ball_weights = {f"b{idx:02d}": round6(1.0 / scale) for idx in range(1, scale + 1)}
        filename = f"{scale:02d}_ball_{pattern['ground_state']}_network.md"
        files_to_write[OUTPUT_ROOT / "juggling_patterns" / filename] = yaml_frontmatter(f"juggling_network_{scale:02d}", "juggling_network", combined_geo, ball_weights, {"siteswap": pattern["siteswap"], "pattern": pattern["pattern"], "ground_state": pattern["ground_state"], "decomposition": pattern["decomposition"], "left_channel_load": round6(math.ceil(scale / 2) / scale), "right_channel_load": round6(math.floor(scale / 2) / scale), "linked_scale_folder": folder.as_posix()}) + render_juggling_network(scale, pattern, combined_geo, corpus_selection, document_selection)
        manifest["juggling_networks"].append({"ball_count": scale, "pattern": pattern, "file": (OUTPUT_ROOT / "juggling_patterns" / filename).as_posix(), "geometry": combined_geo})

    for path, content in files_to_write.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    (OUTPUT_ROOT / "NETWORK_MANIFEST.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Generated dynamic neural network in: {OUTPUT_ROOT}")


if __name__ == "__main__":
    main()
