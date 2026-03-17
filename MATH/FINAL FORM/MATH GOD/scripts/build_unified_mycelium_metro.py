#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
from itertools import product
import json
from pathlib import Path
import re
from typing import Any

from ap7d_swarm_support import build_ap7d_bundle, build_ap7d_markdown


WORKSPACE_ROOT = Path(__file__).resolve().parents[4]

PASS_DEFINITIONS: list[dict[str, Any]] = [
    {
        "id": "P01",
        "title": "Kernel Recovery",
        "description": "Recover the recurring kernel that makes the corpus behave like one organism instead of a pile of manuscripts.",
        "keywords": ["kernel", "core", "seed", "foundation", "ontology", "operating system", "logos", "athena"],
    },
    {
        "id": "P02",
        "title": "State Value Deepening",
        "description": "Track how the corpus redefines numbers, states, carriers, and values as richer semantic objects.",
        "keywords": ["state", "value", "hilbert", "carrier", "bit4", "density", "number", "space", "semantic"],
    },
    {
        "id": "P03",
        "title": "Boundary Totalization",
        "description": "Expose how ambiguity, singularity, liminality, and corridor logic become first-class rather than hidden failure.",
        "keywords": ["boundary", "liminal", "corridor", "ambigu", "bulk", "bound", "singular", "quarantine"],
    },
    {
        "id": "P04",
        "title": "Transport Conjugacy",
        "description": "Follow the lawful transport layer: rotation, conjugacy, tunneling, midpoint routing, and chart change.",
        "keywords": ["rotation", "conjugacy", "transport", "tunnel", "midpoint", "route", "pole", "phase space"],
    },
    {
        "id": "P05",
        "title": "Lattice Address Tile",
        "description": "Recover the finite addressing systems that make the corpus navigable instead of diffuse.",
        "keywords": ["lattice", "address", "tile", "crystal", "64", "256", "square", "lens", "facet", "atom", "latin"],
    },
    {
        "id": "P06",
        "title": "Operator Proof Certificate",
        "description": "Track the archive's insistence that operators, proofs, certificates, ledgers, and witnesses travel together.",
        "keywords": ["operator", "proof", "certificate", "witness", "ledger", "theorem", "invariant", "verification"],
    },
    {
        "id": "P07",
        "title": "Compilation Replay",
        "description": "Map the compiler, runtime, replay, boot, and execution surfaces that turn theory into an engine.",
        "keywords": ["compile", "compiler", "runtime", "replay", "boot", "execute", "deployment", "orchestr", "build"],
    },
    {
        "id": "P08",
        "title": "Time Phase Rotation",
        "description": "Recover cyclical timing, phase, orbit, and seasonal ordering as a mathematical control surface.",
        "keywords": ["time", "phase", "orbit", "cycle", "rotation", "calendar", "yuga", "season", "clock"],
    },
    {
        "id": "P09",
        "title": "Texture Tunneling Manifold",
        "description": "Cross-link the texture, fractal, manifold, aether, and tunneling bodies into one geometry layer.",
        "keywords": ["texture", "fractal", "manifold", "aether", "tunneling", "solenoidal", "holographic", "flow"],
    },
    {
        "id": "P10",
        "title": "Myth Math Isomorphism",
        "description": "Read the mythic, sacred, philosophical, and civilizational bodies as alternate encodings of the same operators.",
        "keywords": ["myth", "sacred", "philosophy", "vedic", "tao", "ifa", "logos", "divination", "alchemy", "epic"],
    },
    {
        "id": "P11",
        "title": "Archive Code Bridge",
        "description": "Bridge manuscripts into zipped frameworks, code packages, scans, and atlas-backed evidence.",
        "keywords": ["archive", "atlas", "zip", "package", "code", "python", "typescript", "scan", "framework"],
    },
    {
        "id": "P12",
        "title": "Query Oracle Decision",
        "description": "Track how the corpus turns uncertainty into query systems, divination engines, and decision protocols.",
        "keywords": ["query", "oracle", "decision", "divination", "measurement", "sampling", "qrdf", "search", "draw"],
    },
    {
        "id": "P13",
        "title": "Self Reference Closure",
        "description": "Read the Athena, selfhood, reflexive, and self-actualizing surfaces as a closure layer on the whole corpus.",
        "keywords": ["self", "athena", "becoming", "reflection", "selfhood", "autopo", "mirror", "alignment"],
    },
    {
        "id": "P14",
        "title": "Cross Corpus Overburn",
        "description": "Identify the master tomes and global syntheses where multiple bodies are intentionally fused.",
        "keywords": ["complete", "master", "synthesis", "global", "unified", "tome", "compendium", "treatise"],
    },
    {
        "id": "P15",
        "title": "Panic Gate Reignition",
        "description": "Name the unstable but fertile frontier surfaces: working drafts, pruning ledgers, old loops, and unresolved routes.",
        "keywords": ["working", "pruning", "frontier", "old", "blocker", "ambig", "draft", "queue", "residual"],
    },
    {
        "id": "P16",
        "title": "Omega Relay",
        "description": "Recover the convergence surfaces where the corpus aims at completion, awakening, closure, or low-entropy stability.",
        "keywords": ["omega", "awakening", "zero point", "completion", "relay", "liberation", "stabil"],
    },
]


LINE_DEFINITIONS: list[dict[str, Any]] = [
    {
        "id": "L01",
        "title": "Kernel Operating System",
        "thesis": "The archive repeatedly rewrites cosmology, mathematics, and identity as kernels, operating systems, and control stacks.",
        "keywords": ["kernel", "operating system", "boot", "logos", "ontology", "athena"],
    },
    {
        "id": "L02",
        "title": "State Semantics",
        "thesis": "Values are treated as states, carriers, lattices, and semantic objects rather than bare scalars.",
        "keywords": ["state", "value", "carrier", "hilbert", "bit4", "density", "space"],
    },
    {
        "id": "L03",
        "title": "Boundary Ecology",
        "thesis": "Boundaries, singularities, ambiguities, and liminal corridors are modeled explicitly and operationally.",
        "keywords": ["boundary", "liminal", "corridor", "ambigu", "bulk", "bound", "singular"],
    },
    {
        "id": "L04",
        "title": "Transport Tunneling",
        "thesis": "Meaning survives by lawful transport: routing, tunneling, midpoint lifting, and conjugate movement across charts.",
        "keywords": ["transport", "rotation", "conjugacy", "tunnel", "route", "midpoint", "pole"],
    },
    {
        "id": "L05",
        "title": "Crystal Addressing",
        "thesis": "The corpus keeps compressing itself into finite, addressable, crystal-like navigation systems.",
        "keywords": ["crystal", "address", "tile", "lattice", "64", "256", "square", "facet", "atom"],
    },
    {
        "id": "L06",
        "title": "Proof Carrying Computation",
        "thesis": "The strongest surfaces insist that execution, proof, witness, and certification belong to one pipeline.",
        "keywords": ["proof", "certificate", "witness", "ledger", "verify", "invariant", "theorem"],
    },
    {
        "id": "L07",
        "title": "Compilation Runtime",
        "thesis": "The corpus repeatedly treats the manuscript as something compilable, executable, and replay-safe.",
        "keywords": ["compile", "runtime", "replay", "execute", "engine", "build", "orchestr"],
    },
    {
        "id": "L08",
        "title": "Mythic Isomorphism",
        "thesis": "Myth, sacred text, philosophy, and divination are cross-compiled as equivalent operator languages.",
        "keywords": ["myth", "sacred", "philosophy", "veda", "tao", "ifa", "logos", "alchemy", "epic"],
    },
    {
        "id": "L09",
        "title": "Query Decision",
        "thesis": "Divination, oracle work, and measurement function as decision systems over hidden state spaces.",
        "keywords": ["query", "oracle", "divination", "decision", "measurement", "sampling", "qrdf"],
    },
    {
        "id": "L10",
        "title": "Compression Relay",
        "thesis": "Dense symbolic containers, pruning systems, and q-shrink surfaces preserve transmission under pressure.",
        "keywords": ["compression", "q-shrink", "pruning", "seed", "dense", "relay", "container"],
    },
    {
        "id": "L11",
        "title": "Omega Awakening",
        "thesis": "Many lines converge on completion, awakening, low-entropy stabilization, and omega-style closure.",
        "keywords": ["omega", "awakening", "zero point", "completion", "stabil", "liberation"],
    },
    {
        "id": "L12",
        "title": "Texture Manifold",
        "thesis": "Texture, fractal, manifold, hybrid, and aether surfaces provide the spatial geometry for the whole metro.",
        "keywords": ["texture", "fractal", "manifold", "hybrid", "aether", "holographic", "solenoidal"],
    },
]


LENSES: list[dict[str, str]] = [
    {"code": "SQ", "title": "Square", "description": "discrete structure, crystal addresses, static legality"},
    {"code": "FL", "title": "Flower", "description": "phase, rotation, resonance, and transport"},
    {"code": "CL", "title": "Cloud", "description": "ambiguity management, corridor truth, and query logic"},
    {"code": "FR", "title": "Fractal", "description": "recursion, replay, compression, and multi-scale regeneration"},
]


FACETS: list[dict[str, str]] = [
    {"code": "OBJ", "title": "Objects", "description": "what entities the station manipulates"},
    {"code": "LAW", "title": "Laws", "description": "what rules, equations, and invariants govern it"},
    {"code": "CON", "title": "Constructions", "description": "what frameworks, engines, or routes it builds"},
    {"code": "CER", "title": "Certificates", "description": "what proofs, witnesses, and audits close it"},
]


STRATA: list[dict[str, str]] = [
    {"code": "MAN", "title": "Manuscript", "description": "live document, markdown, and pdf witnesses"},
    {"code": "RUN", "title": "Runtime", "description": "live code, data, and executable surfaces"},
    {"code": "ARC", "title": "Archive", "description": "zip-backed code and manuscript mirrors"},
    {"code": "SYN", "title": "Synthesis", "description": "atlas, ledger, map, and global bridge surfaces"},
]


LENS_KEYWORDS: dict[str, list[str]] = {
    "Square": ["square", "crystal", "address", "tile", "lattice", "bit4", "binary", "registry"],
    "Flower": ["flower", "rotation", "phase", "orbit", "resonance", "conjugacy", "transport", "cycle"],
    "Cloud": ["cloud", "ambigu", "corridor", "oracle", "query", "boundary", "liminal", "decision"],
    "Fractal": ["fractal", "recursive", "replay", "compression", "q-shrink", "seed", "omega", "regeneration"],
}


FACET_KEYWORDS: dict[str, list[str]] = {
    "Objects": ["object", "state", "number", "carrier", "field", "space", "entity"],
    "Laws": ["law", "theorem", "axiom", "operator", "equation", "grammar", "algebra"],
    "Constructions": ["framework", "engine", "protocol", "build", "compile", "algorithm", "route"],
    "Certificates": ["proof", "certificate", "witness", "ledger", "verify", "audit", "invariant"],
}


STOPWORDS = {
    "about",
    "above",
    "after",
    "again",
    "also",
    "among",
    "around",
    "archive",
    "archive-backed",
    "archive-entry",
    "archived-framework",
    "because",
    "being",
    "between",
    "boxed",
    "chapter",
    "class",
    "code",
    "complete",
    "corpus",
    "docx",
    "definition",
    "enum",
    "every",
    "executable",
    "excerpt",
    "final",
    "following",
    "formally",
    "from",
    "framework",
    "function",
    "functions",
    "into",
    "import",
    "imports",
    "information",
    "langle",
    "math",
    "mathbb",
    "mathematical",
    "mathcal",
    "manuscript",
    "operator",
    "operators",
    "part",
    "proof",
    "record",
    "records",
    "relative",
    "rangle",
    "section",
    "source",
    "state",
    "system",
    "text",
    "theorem",
    "this",
    "through",
    "title",
    "typing",
    "under",
    "using",
    "value",
    "what",
    "where",
    "each",
    "abstract",
    "with",
    "that",
    "module",
    "dict",
    "dataclass",
    "frameworks",
    "atlasforge",
    "self",
    "mathrm",
    "readable",
}


EXCLUDED_WITNESS_SUBSTRINGS = (
    "math god\\atlas\\final_form_",
    "math god\\atlas\\unified_mycelium_",
    "math god\\atlas\\math_tesseract_",
    "math god\\atlas\\math_fire_6d_",
    "math god\\atlas\\math_water_6d_",
    "math god\\atlas\\math_air_6d_",
    "math god\\atlas\\math_h6_convergence_",
    "math god\\atlas\\earth_h6_contract_",
    "math god\\atlas\\math_7d_synthesis_seed_",
    "math god\\atlas\\math_ap7d_self_improvement_swarm_",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build an integrated mycelium metro synthesis from live and archive atlases.")
    parser.add_argument("--live-atlas", required=True, help="Path to the live atlas JSON.")
    parser.add_argument("--archive-atlas", required=True, help="Path to the archive atlas JSON.")
    parser.add_argument("--archive-manifest", required=True, help="Path to the archive manifest JSON.")
    parser.add_argument("--docs-gate", help="Optional path to the live docs gate status markdown.")
    parser.add_argument("--code-scan", help="Optional path to the unified framework code scan JSON.")
    parser.add_argument(
        "--deep-root",
        help="Optional path to the authoritative deeper integrated network root.",
    )
    parser.add_argument("--output-json", required=True, help="Output JSON path for the synthesis bundle.")
    parser.add_argument("--output-md", required=True, help="Output markdown path for the synthesis report.")
    parser.add_argument("--output-tesseract-json", help="Optional JSON path for the tesseract v4 bundle.")
    parser.add_argument("--output-tesseract-md", help="Optional markdown path for the tesseract v4 atlas.")
    parser.add_argument("--output-fire-json", help="Optional JSON path for the FIRE 6D organism bundle.")
    parser.add_argument("--output-fire-md", help="Optional markdown path for the FIRE 6D organism atlas.")
    parser.add_argument("--output-water-6d-json", help="Optional JSON path for the Water 6D control bundle.")
    parser.add_argument("--output-water-6d-md", help="Optional markdown path for the Water 6D control atlas.")
    parser.add_argument("--output-air-6d-json", help="Optional JSON path for the AIR 6D overlay bundle.")
    parser.add_argument("--output-air-6d-md", help="Optional markdown path for the AIR 6D overlay atlas.")
    parser.add_argument("--output-earth-json", help="Optional JSON path for the Earth H6 contract bundle.")
    parser.add_argument("--output-earth-md", help="Optional markdown path for the Earth H6 contract atlas.")
    parser.add_argument("--output-h6-convergence-json", help="Optional JSON path for the H6 convergence bundle.")
    parser.add_argument("--output-h6-convergence-md", help="Optional markdown path for the H6 convergence atlas.")
    parser.add_argument("--output-7d-json", help="Optional JSON path for the 7D synthesis seed bundle.")
    parser.add_argument("--output-7d-md", help="Optional markdown path for the 7D synthesis seed atlas.")
    parser.add_argument("--output-ab-json", help="Optional JSON path for the A/B dual-kernel dock bundle.")
    parser.add_argument("--output-ab-md", help="Optional markdown path for the A/B dual-kernel dock atlas.")
    parser.add_argument("--output-ap7d-json", help="Optional JSON path for the AP7D self-improvement swarm bundle.")
    parser.add_argument("--output-ap7d-md", help="Optional markdown path for the AP7D self-improvement swarm atlas.")
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_optional_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_text(text: str) -> str:
    text = text.lower().replace("\\", " ").replace("/", " ")
    text = re.sub(r"\\[a-z]+", " ", text)
    text = re.sub(r"[^a-z0-9\\s\\-]+", " ", text)
    return re.sub(r"\\s+", " ", text).strip()


def docs_gate_info(path: Path | None) -> dict[str, str]:
    if not path or not path.exists():
        return {"status": "UNKNOWN", "return_code": "", "query": "", "note": "No docs gate status file supplied."}

    body = path.read_text(encoding="utf-8", errors="ignore")
    status_match = re.search(r"- Command status: `([^`]+)`", body)
    code_match = re.search(r"- Return code: `([^`]+)`", body)
    query_match = re.search(r"- Query: `([^`]+)`", body)
    note = ""
    if "```text" in body:
        note = body.split("```text", 1)[1].split("```", 1)[0].strip()
    return {
        "status": status_match.group(1) if status_match else "UNKNOWN",
        "return_code": code_match.group(1) if code_match else "",
        "query": query_match.group(1) if query_match else "",
        "note": note,
    }


def utc_now_string() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def write_json_file(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_text_file(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def write_ndjson_file(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = "\n".join(json.dumps(row, ensure_ascii=True) for row in rows)
    if body:
        body += "\n"
    path.write_text(body, encoding="utf-8")


def ap7d_lineages(depth: int) -> list[str]:
    return ["".join(chars) for chars in product(AP7D_LINEAGE_ALPHABET, repeat=depth)]


def ap7d_ordinal(lineage: str) -> int:
    value_map = {"E": 0, "W": 1, "F": 2, "A": 3}
    ordinal = 0
    for char in lineage:
        ordinal = ordinal * 4 + value_map[char]
    return ordinal


def ap7d_dominant_element(lineage: str) -> str:
    counts = Counter(lineage)
    highest = max(counts.values())
    for char in lineage:
        if counts[char] == highest:
            return AP7D_LINEAGE_TO_ELEMENT[char]
    return "EARTH"


def ap7d_transition_note_refs() -> dict[str, str]:
    return {
        "FIRE": str(NEXT46_FIRE_NOTE_PATH),
        "WATER": str(NEXT46_WATER_NOTE_PATH),
        "AIR": str(NEXT46_AIR_NOTE_PATH),
        "EARTH": str(NEXT46_EARTH_NOTE_PATH),
    }


def ap7d_macro_target_lookup() -> dict[str, dict[str, str]]:
    return {item["lineage"]: item for item in AP7D_MACRO_TARGETS}


def ap7d_event_human_line(
    event_type: str,
    ts_utc: str,
    actor_id: str,
    field_a: str,
    field_b: str,
    field_c: str,
    field_d: str,
) -> str:
    return f"{event_type}::{ts_utc}::{actor_id}::{field_a}::{field_b}::{field_c}::{field_d}"


def water_route_record(
    route_id: str,
    title: str,
    basis_refs: list[str],
    metro_refs: list[str],
    appendix_refs: list[str],
    local_zero_point: str,
    return_checkpoint: str,
    replay_source: str,
    truth_state: str = "NEAR",
) -> dict[str, Any]:
    return {
        "route_id": route_id,
        "title": title,
        "basis_refs": basis_refs,
        "metro_refs": metro_refs,
        "appendix_refs": appendix_refs,
        "local_zero_point": local_zero_point,
        "collapse_via": "Z*",
        "return_checkpoint": return_checkpoint,
        "truth_state": truth_state,
        "replay_source": replay_source,
    }


def air_route_record(
    route_id: str,
    title: str,
    basis_refs: list[str],
    metro_refs: list[str],
    canonical_appendix_map: list[str],
    local_zero_point: str,
    return_checkpoint: str,
    replay_source: str,
    sigma_node: str,
    spin_kernel: str,
    rotation_family: str,
    dual_kernel: str,
    mobius_mode: str,
    truth_state: str = "NEAR",
) -> dict[str, Any]:
    record = water_route_record(
        route_id=route_id,
        title=title,
        basis_refs=basis_refs,
        metro_refs=metro_refs,
        appendix_refs=canonical_appendix_map,
        local_zero_point=local_zero_point,
        return_checkpoint=return_checkpoint,
        replay_source=replay_source,
        truth_state=truth_state,
    )
    record.update(
        {
            "sigma_node": sigma_node,
            "spin_kernel": spin_kernel,
            "rotation_family": rotation_family,
            "dual_kernel": dual_kernel,
            "mobius_mode": mobius_mode,
            "canonical_appendix_map": canonical_appendix_map,
        }
    )
    return record


def convergence_route_record(
    route_id: str,
    title: str,
    source_basis: list[str],
    metro_refs: list[str],
    lane_dependencies: list[str],
    shared_appendices: list[str],
    local_zero_point: str,
    return_checkpoint: str,
    replay_source: str,
    truth_state: str = "NEAR",
    route_stage: str = "H6",
) -> dict[str, Any]:
    return {
        "route_id": route_id,
        "title": title,
        "route_stage": route_stage,
        "source_basis": source_basis,
        "metro_refs": metro_refs,
        "local_zero_point": local_zero_point,
        "collapse_via": "Z*",
        "lane_dependencies": lane_dependencies,
        "shared_appendices": shared_appendices,
        "return_checkpoint": return_checkpoint,
        "truth_state": truth_state,
        "replay_source": replay_source,
    }


def infer_stratum(record: dict[str, Any]) -> str:
    relative = record["relative_path"].lower()
    if record["source_layer"] == "archive":
        return "Archive"
    if "global math - myth" in relative or "math god" in relative or "\\atlas\\" in relative or relative.endswith(".json"):
        return "Synthesis"
    if record["kind"] in {"code", "data"}:
        return "Runtime"
    return "Manuscript"


def build_records(records: list[dict[str, Any]], source_layer: str) -> list[dict[str, Any]]:
    built: list[dict[str, Any]] = []
    for record in records:
        text = " ".join(record.get("heading_candidates", []))
        text = f"{record.get('relative_path', '')} {text} {record.get('excerpt', '')} {' '.join(record.get('role_tags', []))}"
        built_record = {
            "record_id": record.get("record_id", ""),
            "relative_path": record.get("relative_path", ""),
            "path": record.get("path", ""),
            "top_level": record.get("top_level", ""),
            "kind": record.get("kind", ""),
            "extension": record.get("extension", ""),
            "source_layer": source_layer,
            "text": normalize_text(text),
        }
        built_record["stratum"] = infer_stratum(built_record)
        built.append(built_record)
    return built


def score_keywords(text: str, keywords: list[str]) -> tuple[int, list[str]]:
    score = 0
    hits: list[str] = []
    for keyword in keywords:
        token = normalize_text(keyword)
        if token and token in text:
            score += 3 if " " in token else 1
            hits.append(keyword)
    return score, hits


def prefer_witness(record: dict[str, Any]) -> bool:
    relative = record["relative_path"].lower()
    return not any(fragment in relative for fragment in EXCLUDED_WITNESS_SUBSTRINGS)


def summarize_matches(
    records: list[dict[str, Any]],
    definition: dict[str, Any],
    top_n: int = 8,
) -> dict[str, Any]:
    matches: list[dict[str, Any]] = []
    for record in records:
        score, hits = score_keywords(record["text"], definition["keywords"])
        if score <= 0:
            continue
        matches.append({"record": record, "score": score, "hits": hits})

    matches.sort(
        key=lambda item: (
            -item["score"],
            0 if prefer_witness(item["record"]) else 1,
            item["record"]["relative_path"].lower(),
        )
    )

    live_matches = [item for item in matches if item["record"]["source_layer"] == "live"]
    archive_matches = [item for item in matches if item["record"]["source_layer"] == "archive"]
    top_levels = Counter(item["record"]["top_level"] for item in matches)
    strata = Counter(item["record"]["stratum"] for item in matches)

    witnesses: list[dict[str, Any]] = []
    used_paths: set[str] = set()
    for pool in (live_matches, archive_matches, matches):
        for item in pool:
            path = item["record"]["relative_path"]
            if path in used_paths:
                continue
            if not prefer_witness(item["record"]) and len(witnesses) < 4:
                continue
            witnesses.append(
                {
                    "relative_path": path,
                    "source_layer": item["record"]["source_layer"],
                    "top_level": item["record"]["top_level"],
                    "score": item["score"],
                    "hits": item["hits"][:4],
                }
            )
            used_paths.add(path)
            if len(witnesses) >= top_n:
                break
        if len(witnesses) >= top_n:
            break

    return {
        "match_count": len(matches),
        "live_match_count": len(live_matches),
        "archive_match_count": len(archive_matches),
        "top_levels": top_levels.most_common(6),
        "strata": strata.most_common(),
        "witnesses": witnesses,
        "match_index": matches,
    }


def compute_signal_lexicon(records: list[dict[str, Any]], limit: int = 16) -> list[list[Any]]:
    counter: Counter[str] = Counter()
    for record in records:
        if record["stratum"] not in {"Manuscript", "Synthesis"}:
            continue
        for token in re.findall(r"[a-z][a-z\-]{3,}", record["text"]):
            if token in STOPWORDS or token.isdigit():
                continue
            counter[token] += 1
    return [[word, count] for word, count in counter.most_common(limit)]


def compute_transfer_hubs(line_summaries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    hub_index: dict[str, dict[str, Any]] = {}
    for line_summary in line_summaries:
        for match in line_summary["match_index"]:
            record = match["record"]
            path = record["relative_path"]
            if path not in hub_index:
                hub_index[path] = {
                    "relative_path": path,
                    "top_level": record["top_level"],
                    "source_layer": record["source_layer"],
                    "stratum": record["stratum"],
                    "line_ids": [],
                    "line_titles": [],
                    "score": 0,
                }
            hub_index[path]["line_ids"].append(line_summary["id"])
            hub_index[path]["line_titles"].append(line_summary["title"])
            hub_index[path]["score"] += match["score"]

    hubs = [item for item in hub_index.values() if len(item["line_ids"]) >= 4 and prefer_witness(item)]
    hubs.sort(key=lambda item: (-len(item["line_ids"]), -item["score"], item["relative_path"].lower()))
    return hubs[:12]


def strip_internal_indexes(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cleaned: list[dict[str, Any]] = []
    for item in items:
        public = {key: value for key, value in item.items() if key != "match_index"}
        cleaned.append(public)
    return cleaned


def build_station_basis(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    stations: list[dict[str, Any]] = []
    for lens in LENSES:
        for facet in FACETS:
            for stratum in STRATA:
                station_keywords = LENS_KEYWORDS[lens["title"]] + FACET_KEYWORDS[facet["title"]]
                matches = [
                    record
                    for record in records
                    if record["stratum"] == stratum["title"] and score_keywords(record["text"], station_keywords)[0] > 0
                ]
                top_levels = Counter(record["top_level"] for record in matches).most_common(3)
                stations.append(
                    {
                        "station_id": f"{lens['code']}-{facet['code']}-{stratum['code']}",
                        "lens": lens["title"],
                        "facet": facet["title"],
                        "stratum": stratum["title"],
                        "role": f"{lens['description']}; {facet['description']}; {stratum['description']}.",
                        "coverage": len(matches),
                        "top_levels": top_levels,
                    }
                )
    stations.sort(key=lambda item: item["station_id"])
    return stations


def build_code_scan_summary(path: Path | None) -> dict[str, Any]:
    if not path or not path.exists():
        return {"available": False}

    payload = json.loads(path.read_text(encoding="utf-8"))
    project_counter = Counter(item.get("project", "[unknown]") for item in payload)
    return {
        "available": True,
        "file_count": len(payload),
        "projects": dict(project_counter),
        "class_count": sum(len(item.get("classes", [])) for item in payload),
        "function_count": sum(len(item.get("functions", [])) for item in payload),
        "import_count": sum(len(item.get("imports", [])) for item in payload),
    }


def route_example(stations: list[dict[str, Any]], title_filters: list[str]) -> list[dict[str, Any]]:
    chosen: list[dict[str, Any]] = []
    seen: set[str] = set()
    for filter_title in title_filters:
        for station in stations:
            if station["lens"] == filter_title and station["station_id"] not in seen:
                chosen.append(station)
                seen.add(station["station_id"])
                break
    while len(chosen) < 4:
        for station in stations:
            if station["station_id"] not in seen:
                chosen.append(station)
                seen.add(station["station_id"])
                break
    return chosen[:4]


TRIAD = ["Su", "Me", "Sa"]
LENS_TITLE_TO_CODE = {"Square": "S", "Flower": "F", "Cloud": "C", "Fractal": "R"}
LENS_CODE_TO_TITLE = {value: key for key, value in LENS_TITLE_TO_CODE.items()}
FACET_NUMBER_TO_TITLE = {1: "Objects", 2: "Laws", 3: "Constructions", 4: "Certificates"}
FACET_TITLE_TO_NUMBER = {value: key for key, value in FACET_NUMBER_TO_TITLE.items()}
LENS_BASE = {"S": "AppC", "F": "AppE", "C": "AppI", "R": "AppM"}
FACET_BASE = {1: "AppA", 2: "AppB", 3: "AppH", 4: "AppM"}
ARC_HUB = {0: "AppA", 1: "AppC", 2: "AppE", 3: "AppF", 4: "AppG", 5: "AppN", 6: "AppP"}
TRUTH_OVERLAY = {"OK": "", "NEAR": "AppJ", "AMBIG": "AppL", "FAIL": "AppK"}
MANDATORY_SIGNATURE = ["AppA", "AppI", "AppM"]
HCRL_ORDER = ["S", "F", "C", "R"]
APPENDIX_ADDRESS_MAP = {
    "AppA": "AppA.S1.a",
    "AppB": "AppB.S2.a",
    "AppC": "AppC.S3.a",
    "AppD": "AppD.S4.a",
    "AppE": "AppE.F1.a",
    "AppF": "AppF.F2.a",
    "AppG": "AppG.F3.a",
    "AppH": "AppH.F4.a",
    "AppI": "AppI.C1.a",
    "AppJ": "AppJ.C2.a",
    "AppK": "AppK.C3.a",
    "AppL": "AppL.C4.a",
    "AppM": "AppM.R1.a",
    "AppN": "AppN.R2.a",
    "AppO": "AppO.R3.a",
    "AppP": "AppP.R4.a",
}
APPENDIX_ROLES = {
    "AppA": "addressing, symbols, parsing grammar, entry station",
    "AppB": "canon laws, equivalence budgets, normal forms",
    "AppC": "Square kernel pack, discrete mixing, index algebra",
    "AppD": "registry, Ms derivation, router profiles, pinned policies",
    "AppE": "Circle gear, phase lock, integer bridges",
    "AppF": "transport, rotation-as-conjugacy, DUAL legality",
    "AppG": "Triangle control, recursion legality, carry/hatch triggers",
    "AppH": "coupling/topology, dependency closure, isolation invariants",
    "AppI": "corridors, truth lattice, admissibility budgets, abstain law",
    "AppJ": "residual ledgers, drift envelopes, bounded approximation",
    "AppK": "conflict/quarantine/revocation receipts",
    "AppL": "evidence-plan templates, ambiguity promotion harness",
    "AppM": "replay kernel, verifier capsules, determinism checklists",
    "AppN": "container formats, virtual mount, salvage/seek doctrine",
    "AppO": "publication bundles, signatures, revocation rules",
    "AppP": "deployment profiles, conformance reports, monitoring templates",
}
APPENDIX_EXTRA_ROLES = {
    "AppQ": "appendix-only metro authority, deep-root docking, and certification-only support",
}
DEEP_APPENDIX_ROOT = (
    WORKSPACE_ROOT
    / "self_actualize"
    / "mycelium_brain"
    / "dynamic_neural_network"
    / "14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK"
    / "08_APPENDIX_CRYSTAL"
)
APPENDIX_SOURCE_FILES = {
    "AppA": ["AppA_addressing_and_grammars.md"],
    "AppB": ["AppB_canon_laws_and_forms.md"],
    "AppC": ["AppC_kernel_pack_and_mixing.md"],
    "AppD": ["AppD_registry_and_policies.md"],
    "AppE": ["AppE_circle_gear_and_clock.md"],
    "AppF": ["AppF_transport_and_duality.md"],
    "AppG": ["AppG_triangle_control.md"],
    "AppH": ["AppH_coupling_and_topology.md"],
    "AppI": ["AppI_corridors_and_truth_lattice.md"],
    "AppJ": ["AppJ_residual_ledgers.md"],
    "AppK": ["AppK_conflict_and_quarantine.md"],
    "AppL": ["AppL_evidence_plan_harness.md"],
    "AppM": ["AppM_replay_kernel.md"],
    "AppN": ["AppN_container_formats.md"],
    "AppO": ["AppO_export_bundles.md"],
    "AppP": ["AppP_deployment_profiles.md"],
    "AppQ": ["AppQ_appendix_only_metro_map.md", "AppQ_athena_fleet_256_pow_4_support.md"],
}
LIVE_DEEP_ROOT_DEFAULT = DEEP_APPENDIX_ROOT.parent
DEEP_EARTH_LOOP_FILES = {
    "RegistrySchemas": Path("04_EARTH/07_registryschemas.md"),
    "VerifierReplay": Path("04_EARTH/08_verifierreplay.md"),
    "PruneOptimizer": Path("04_EARTH/12_pruneoptimizer.md"),
    "DimensionLift": Path("04_EARTH/16_dimensionlift.md"),
}
DEEP_EARTH_GATE_FILES = {
    "EarthGateIndex": Path("13_6D_EARTH_CONTROL/00_INDEX.md"),
    "EarthGateZeroPoint": Path("13_6D_EARTH_CONTROL/01_admissibility_and_zero_point.md"),
    "EarthGateGuardrail": Path("13_6D_EARTH_CONTROL/02_2564_to_10246_guardrail_lift.md"),
    "EarthGateBoundary": Path("13_6D_EARTH_CONTROL/03_boundary_quarantine_and_mobius_legality.md"),
    "EarthGateReplay": Path("13_6D_EARTH_CONTROL/04_replay_and_reentry_guards.md"),
}
HISTORICAL_EARTH_ROOT = (
    WORKSPACE_ROOT
    / "MATH"
    / "FINAL FORM"
    / "MYTH - MATH"
    / "Philosophy"
    / "ATHENA_INTEGRATED_NEURAL_NETWORK"
    / "EARTH"
)
HISTORICAL_EARTH_SURFACES = {
    "Earth Index": HISTORICAL_EARTH_ROOT / "00_earth_index.md",
    "Earth Full-Corpus Pass": HISTORICAL_EARTH_ROOT / "01_earth_full_corpus_pass.md",
}
HISTORICAL_MIRROR_ROOTS = [
    WORKSPACE_ROOT / "self_actualize" / "mycelium_brain" / "DEEPER_INTEGRATED_NEURAL_NETWORK",
    WORKSPACE_ROOT / "self_actualize" / "mycelium_brain" / "DEEPER_INTEGRATED_NEURAL_NET_ATHENA",
    WORKSPACE_ROOT / "DEEPER CRYSTALIZATION" / "ACTIVE_NERVOUS_SYSTEM" / "13_DEEPER_NEURAL_NET",
]
FAMILY_LOCAL_BOUNDARY_SKILLS = [
    "NERUAL NETWORK/.../integrated-neural-network-orchestrator",
    "Trading Bot/skills/manuscript-elemental-synthesis",
]
EARTH_CORE_APPENDICES = ["AppA", "AppI", "AppM"]
EARTH_STABILITY_APPENDICES = ["AppB", "AppK", "AppL", "AppP"]
EARTH_CONDITIONAL_APPENDICES = ["AppE", "AppF", "AppG", "AppH", "AppN", "AppO", "AppQ"]
EARTH_NATIVE_DRIVERS = [
    {
        "doc_id": "02",
        "title": "Self-Routing Meta-Framework",
        "cluster": "routing and search",
        "anchor": "routing and search",
        "contribution": "decides how the corpus searches itself",
        "source_hint": "DEEPER CRYSTALIZATION\\Self-Routing Meta-Framework...",
        "appendix_stack": ["AppE", "AppI", "AppL", "AppM"],
    },
    {
        "doc_id": "09",
        "title": "Zero-Point Computing",
        "cluster": "zero-point engine",
        "anchor": "zero-point engine",
        "contribution": "defines minimum-state computation and restart from near nothing",
        "source_hint": "MATH\\...Zero-Point Computing",
        "appendix_stack": ["AppA", "AppN", "AppM"],
    },
    {
        "doc_id": "13",
        "title": "Universal Computational Ontology",
        "cluster": "mythic os",
        "anchor": "mythic os",
        "contribution": "converts mythic cosmology into system architecture",
        "source_hint": "MATH\\...Universal Computational Ontology",
        "appendix_stack": ["AppA", "AppB", "AppP"],
    },
    {
        "doc_id": "15",
        "title": "Ch12 Boundary Checks and Isolation Axioms",
        "cluster": "immune architecture",
        "anchor": "immune architecture",
        "contribution": "protects the network from contradiction leakage and contamination",
        "source_hint": "self_actualize\\manuscript_sections\\012_ch12_boundary_checks_and_isolation_axioms.md",
        "appendix_stack": ["AppB", "AppI", "AppK", "AppM"],
    },
]
MATH_GOD_ROOT = WORKSPACE_ROOT / "MATH" / "FINAL FORM" / "MATH GOD"
MATH_GOD_ATLAS_ROOT = WORKSPACE_ROOT / "MATH" / "FINAL FORM" / "MATH GOD" / "atlas"
WATER_CONTROL_ROOT = LIVE_DEEP_ROOT_DEFAULT / "11_6D_WATER_CONTROL"
WATER_CANON_ROOT = MATH_GOD_ROOT / "H6_WATER"
EARTH_CONTROL_ROOT = LIVE_DEEP_ROOT_DEFAULT / "13_6D_EARTH_CONTROL"
LEGACY_EARTH_CONTROL_ROOT = LIVE_DEEP_ROOT_DEFAULT / "12_6D_EARTH_CONTROL"
H6_CONVERGENCE_ROOT = LIVE_DEEP_ROOT_DEFAULT / "13_6D_H6_CONVERGENCE"
SEED7_CONTROL_PATH = LIVE_DEEP_ROOT_DEFAULT / "00_CONTROL" / "07_7D_CROSS_AGENT_SEED.md"
SEED7_LEVEL_PATH = LIVE_DEEP_ROOT_DEFAULT / "07_METRO_STACK" / "07_level_7_next_synthesis_seed_map.md"
SEED7_APPENDIX_PATH = LIVE_DEEP_ROOT_DEFAULT / "08_APPENDIX_CRYSTAL" / "02_7d_seed_appendix_legality.md"
SEED7_EARTH_LEDGER_PATH = LIVE_DEEP_ROOT_DEFAULT / "10_LEDGERS" / "10_earth_gate_status_7d_seed.json"
SEED7_CONVERGENCE_LEDGER_PATH = LIVE_DEEP_ROOT_DEFAULT / "10_LEDGERS" / "11_cross_agent_convergence_7d_seed.json"
SEED7_ROUTE_LEDGER_PATH = LIVE_DEEP_ROOT_DEFAULT / "10_LEDGERS" / "12_7d_seed_routes.json"
SEED7_APPENDIX_LEDGER_PATH = LIVE_DEEP_ROOT_DEFAULT / "10_LEDGERS" / "13_7d_appendix_legality.json"
NEXT46_CONTROL_PATH = LIVE_DEEP_ROOT_DEFAULT / "00_CONTROL" / "08_NEXT_4_6_FULL_CORPUS_STABILIZATION.md"
NEXT46_TRANSITIONS_PATH = LIVE_DEEP_ROOT_DEFAULT / "00_CONTROL" / "09_AWAKENING_AGENT_TRANSITIONS.md"
NEXT46_OPERATOR_PATH = LIVE_DEEP_ROOT_DEFAULT / "00_CONTROL" / "10_CROSS_AGENT_TRANSITION_OPERATOR.md"
NEXT46_LEVEL_PATH = LIVE_DEEP_ROOT_DEFAULT / "07_METRO_STACK" / "08_level_7_full_corpus_stabilization_companion.md"
NEXT46_APPENDIX_PATH = LIVE_DEEP_ROOT_DEFAULT / "08_APPENDIX_CRYSTAL" / "03_awakening_transition_appendix_legality.md"
NEXT46_FIRE_NOTE_PATH = LIVE_DEEP_ROOT_DEFAULT / "01_FIRE" / "23_awakening_transition_note.md"
NEXT46_WATER_NOTE_PATH = WATER_CONTROL_ROOT / "05_awakening_transition_note.md"
NEXT46_AIR_NOTE_PATH = LIVE_DEEP_ROOT_DEFAULT / "12_6D_AIR_CONTROL" / "05_awakening_transition_note.md"
NEXT46_EARTH_NOTE_PATH = EARTH_CONTROL_ROOT / "05_awakening_transition_note.md"
NEXT46_FAMILY_LEDGER_PATH = LIVE_DEEP_ROOT_DEFAULT / "10_LEDGERS" / "14_full_corpus_witness_family_ledger.json"
NEXT46_CROSSWALK_LEDGER_PATH = LIVE_DEEP_ROOT_DEFAULT / "10_LEDGERS" / "15_full_corpus_basis_crosswalk.json"
NEXT46_FAMILY_CONVERGENCE_LEDGER_PATH = LIVE_DEEP_ROOT_DEFAULT / "10_LEDGERS" / "16_cross_agent_family_convergence.json"
NEXT46_QUARANTINE_LEDGER_PATH = LIVE_DEEP_ROOT_DEFAULT / "10_LEDGERS" / "17_full_corpus_quarantine_routes.json"
NEXT46_TRANSITION_LEDGER_PATH = LIVE_DEEP_ROOT_DEFAULT / "10_LEDGERS" / "18_awakening_agent_transition_notes.json"
NEXT46_STABILIZATION_LEDGER_PATH = LIVE_DEEP_ROOT_DEFAULT / "10_LEDGERS" / "19_level_7_full_corpus_stabilization.json"
MATH_GOD_NEXT46_PATH = MATH_GOD_ROOT / "99_NEXT_4_6_FULL_CORPUS_STABILIZATION.md"
MATH_GOD_AWAKENING_TRANSITIONS_PATH = MATH_GOD_ROOT / "100_ELEMENTAL_AWAKENING_AGENT_TRANSITIONS.md"
MATH_GOD_A_B_CHARTER_PATH = MATH_GOD_ROOT / "103_A_SEED_B_DUAL_KERNEL_CHARTER.md"
MATH_GOD_A_B_CROSSWALK_PATH = MATH_GOD_ROOT / "104_A_B_DUAL_KERNEL_CROSSWALK.md"
AWAKENING_TOME_ROOT = (
    WORKSPACE_ROOT
    / "MATH"
    / "FINAL FORM"
    / "FRAMEWORKS CODE"
    / "ATHENA_AWAKENING_TOME"
    / "ATHENA_AWAKENING_TOME"
)
HISTORICAL_WATER_WITNESS_ROOTS = [
    MATH_GOD_ATLAS_ROOT / "water_test",
    MATH_GOD_ATLAS_ROOT / "water_test_explicit",
]
PACKAGE_EXPORT_ROOT = (
    WORKSPACE_ROOT
    / "MATH"
    / "FINAL FORM"
    / "MYTH - MATH"
    / "Philosophy"
    / "ATHENA_INTEGRATED_NEURAL_NETWORK"
)
PACKAGE_SEED7_EXPORT_DOC = PACKAGE_EXPORT_ROOT / "00_CONTROL" / "06_7D_SEED_EXPORT.md"
PACKAGE_SEED7_EXPORT_LEDGER = PACKAGE_EXPORT_ROOT / "LEDGERS" / "06_7d_seed_export_registry.json"
PACKAGE_SEED7_APPENDIX_DOC = PACKAGE_EXPORT_ROOT / "APPENDIX_CRYSTAL" / "02_7d_seed_appendix_legality.md"
PACKAGE_NEXT46_EXPORT_DOC = PACKAGE_EXPORT_ROOT / "00_CONTROL" / "07_FULL_CORPUS_7D_STABILIZATION_EXPORT.md"
PACKAGE_AWAKENING_TRANSITIONS_DOC = PACKAGE_EXPORT_ROOT / "00_CONTROL" / "08_AWAKENING_AGENT_TRANSITIONS_EXPORT.md"
PACKAGE_FIRE_NOTE_DOC = PACKAGE_EXPORT_ROOT / "FIRE" / "03_awakening_transition_note.md"
PACKAGE_WATER_NOTE_DOC = PACKAGE_EXPORT_ROOT / "WATER" / "02_awakening_transition_note.md"
PACKAGE_AIR_NOTE_DOC = PACKAGE_EXPORT_ROOT / "AIR" / "02_awakening_transition_note.md"
PACKAGE_EARTH_NOTE_DOC = PACKAGE_EXPORT_ROOT / "EARTH" / "02_awakening_transition_note.md"
PACKAGE_NEXT46_APPENDIX_DOC = PACKAGE_EXPORT_ROOT / "APPENDIX_CRYSTAL" / "03_awakening_transition_appendix_legality.md"
PACKAGE_NEXT46_EXPORT_LEDGER = PACKAGE_EXPORT_ROOT / "LEDGERS" / "07_full_corpus_7d_stabilization_export_registry.json"
NEXT57_STATE_PATH = WORKSPACE_ROOT / "self_actualize" / "next57_four_agent_corpus_cycle_state.json"
NEXT57_PROTOCOL_PATH = WORKSPACE_ROOT / "self_actualize" / "next57_prime_loop_protocol.json"
NEXT57_HALL_TREE_PATH = WORKSPACE_ROOT / "self_actualize" / "next57_guild_hall_quest_tree.json"
NEXT57_TEMPLE_TREE_PATH = WORKSPACE_ROOT / "self_actualize" / "next57_temple_quest_tree.json"
NEXT57_COORDINATE_REGISTRY_PATH = WORKSPACE_ROOT / "self_actualize" / "next57_liminal_coordinate_registry.json"
NEXT57_LEDGER_SCHEMA_PATH = WORKSPACE_ROOT / "self_actualize" / "next57_agent_ledger_schema.json"
SEED7_POLARITY_STATES = ["A", "B", "A↔B"]
DUAL_KERNEL_OPERATOR_NAME = "Invert_dual"
AP7D_CONTROL_PATH = LIVE_DEEP_ROOT_DEFAULT / "00_CONTROL" / "11_AP7D_SELF_IMPROVEMENT_SWARM.md"
AP7D_META_PATH = LIVE_DEEP_ROOT_DEFAULT / "00_CONTROL" / "12_AP7D_META_NOTATION.md"
AP7D_LEVEL_PATH = LIVE_DEEP_ROOT_DEFAULT / "07_METRO_STACK" / "09_level_7_agent_nervous_system_map.md"
AP7D_SWARM_MANIFEST_PATH = LIVE_DEEP_ROOT_DEFAULT / "10_LEDGERS" / "20_ap7d_swarm_manifest.json"
AP7D_AGENT_REGISTRY_PATH = LIVE_DEEP_ROOT_DEFAULT / "10_LEDGERS" / "21_ap7d_agent_registry_256.json"
AP7D_HEARTBEAT_FEED_PATH = LIVE_DEEP_ROOT_DEFAULT / "10_LEDGERS" / "22_ap7d_heartbeat_feed.ndjson"
AP7D_DELTA_FEED_PATH = LIVE_DEEP_ROOT_DEFAULT / "10_LEDGERS" / "23_ap7d_delta_feed.ndjson"
AP7D_HANDOFF_FEED_PATH = LIVE_DEEP_ROOT_DEFAULT / "10_LEDGERS" / "24_ap7d_handoff_feed.ndjson"
AP7D_RESTART_SEED_PATH = LIVE_DEEP_ROOT_DEFAULT / "10_LEDGERS" / "25_ap7d_restart_seed_registry.json"
AP7D_INTENT_FEED_PATH = LIVE_DEEP_ROOT_DEFAULT / "10_LEDGERS" / "26_ap7d_intent_feed.ndjson"
AP7D_MACRO_NOTE_PATH = LIVE_DEEP_ROOT_DEFAULT / "10_LEDGERS" / "27_ap7d_macro_transition_assist_notes.json"
MATH_GOD_AP7D_SWARM_PATH = MATH_GOD_ROOT / "101_AP7D_SELF_IMPROVEMENT_SWARM.md"
MATH_GOD_AP7D_META_PATH = MATH_GOD_ROOT / "102_AP7D_META_NOTATION.md"
GUILD_HALL_ROOT = WORKSPACE_ROOT / "self_actualize" / "mycelium_brain" / "GLOBAL_EMERGENT_GUILD_HALL"
TEMPLE_ROOT = WORKSPACE_ROOT / "self_actualize" / "mycelium_brain" / "ATHENA TEMPLE"
AP7D_HALL_STATUS_PATH = GUILD_HALL_ROOT / "17_AP7D_SWARM_STATUS.md"
AP7D_TEMPLE_QUEST_PATH = TEMPLE_ROOT / "QUESTS" / "AP7D_TQ01_INSTALL_RESTART_SAFE_SWARM.md"
PACKAGE_AP7D_EXPORT_DOC = PACKAGE_EXPORT_ROOT / "00_CONTROL" / "09_AP7D_SELF_IMPROVEMENT_SWARM_EXPORT.md"
PACKAGE_AP7D_META_DOC = PACKAGE_EXPORT_ROOT / "00_CONTROL" / "10_AP7D_META_NOTATION_EXPORT.md"
PACKAGE_AP7D_EXPORT_LEDGER = PACKAGE_EXPORT_ROOT / "LEDGERS" / "08_ap7d_swarm_export_registry.json"
H6_CONVERGENCE_CHARTER_PATH = MATH_GOD_ROOT / "97_H6_CONVERGENCE_CHARTER.md"
H6_TO_SEED6D_CROSSWALK_PATH = MATH_GOD_ROOT / "98_H6_TO_SEED6D_CROSSWALK.md"
TESSERACT_BUNDLE_JSON_PATH = MATH_GOD_ATLAS_ROOT / "math_tesseract_v4_bundle.json"
TESSERACT_BUNDLE_MARKDOWN_PATH = MATH_GOD_ATLAS_ROOT / "math_tesseract_v4_bundle.md"
AP7D_LINEAGE_ALPHABET = ["E", "W", "F", "A"]
AP7D_LINEAGE_TO_ELEMENT = {
    "E": "EARTH",
    "W": "WATER",
    "F": "FIRE",
    "A": "AIR",
}
AP7D_AGENT_ORDER = ["FIRE", "WATER", "AIR", "EARTH"]
AP7D_APPENDIX_FLOORS = {
    "FIRE": ["AppE", "AppP", "AppI", "AppM"],
    "WATER": ["AppE", "AppF", "AppO", "AppI", "AppM"],
    "AIR": ["AppB", "AppC", "AppN", "AppI", "AppM"],
    "EARTH": ["AppB", "AppK", "AppM", "AppN", "AppI"],
}
AP7D_TRANSITION_STATES = ["dormant", "activating", "destabilized", "integrating", "stabilized"]
AP7D_SEEDED_FIBERS = ["FFFF", "WWWW", "AAAA", "EEEE"]
AP7D_SHARED_RESTART_RULE = (
    "If a live agent stalls or the run ends, emit RST, demote to dormant, and resume only from the last canonical feed-backed seed."
)
AP7D_MACRO_TARGETS = [
    {
        "lineage": "EE",
        "surface_id": "AP7D_SWARM_CHARTER",
        "front": "charter hardening",
        "output_target": str(AP7D_CONTROL_PATH),
    },
    {
        "lineage": "EW",
        "surface_id": "AP7D_META_NOTATION",
        "front": "notation grammar",
        "output_target": str(AP7D_META_PATH),
    },
    {
        "lineage": "EF",
        "surface_id": "AP7D_AGENT_METRO",
        "front": "nervous-system map",
        "output_target": str(AP7D_LEVEL_PATH),
    },
    {
        "lineage": "EA",
        "surface_id": "AP7D_SWARM_MANIFEST",
        "front": "run manifest",
        "output_target": str(AP7D_SWARM_MANIFEST_PATH),
    },
    {
        "lineage": "WE",
        "surface_id": "AP7D_AGENT_REGISTRY",
        "front": "fiber registry",
        "output_target": str(AP7D_AGENT_REGISTRY_PATH),
    },
    {
        "lineage": "WW",
        "surface_id": "AP7D_HEARTBEAT_FEED",
        "front": "live heartbeat feed",
        "output_target": str(AP7D_HEARTBEAT_FEED_PATH),
    },
    {
        "lineage": "WF",
        "surface_id": "AP7D_DELTA_FEED",
        "front": "delta feed",
        "output_target": str(AP7D_DELTA_FEED_PATH),
    },
    {
        "lineage": "WA",
        "surface_id": "AP7D_HANDOFF_FEED",
        "front": "handoff feed",
        "output_target": str(AP7D_HANDOFF_FEED_PATH),
    },
    {
        "lineage": "FE",
        "surface_id": "AP7D_RESTART_REGISTRY",
        "front": "restart seeds",
        "output_target": str(AP7D_RESTART_SEED_PATH),
    },
    {
        "lineage": "FW",
        "surface_id": "AP7D_INTENT_FEED",
        "front": "intent feed",
        "output_target": str(AP7D_INTENT_FEED_PATH),
    },
    {
        "lineage": "FF",
        "surface_id": "AP7D_MACRO_NOTES",
        "front": "macro assist notes",
        "output_target": str(AP7D_MACRO_NOTE_PATH),
    },
    {
        "lineage": "FA",
        "surface_id": "AP7D_HALL_STATUS",
        "front": "hall readable status",
        "output_target": str(AP7D_HALL_STATUS_PATH),
    },
    {
        "lineage": "AE",
        "surface_id": "AP7D_TEMPLE_QUEST",
        "front": "ownerable next move",
        "output_target": str(AP7D_TEMPLE_QUEST_PATH),
    },
    {
        "lineage": "AW",
        "surface_id": "SEED7_LEVEL_PATH",
        "front": "seed-level return routing",
        "output_target": str(SEED7_LEVEL_PATH),
    },
    {
        "lineage": "AF",
        "surface_id": "NEXT46_LEVEL_COMPANION",
        "front": "full-corpus stabilization companion",
        "output_target": str(NEXT46_LEVEL_PATH),
    },
    {
        "lineage": "AA",
        "surface_id": "AP7D_PACKAGE_EXPORT",
        "front": "export mirror",
        "output_target": str(PACKAGE_AP7D_EXPORT_DOC),
    },
]
WATER_NATIVE_DRIVERS = [
    {
        "doc_id": "01",
        "title": "The Holographic Manuscript Brain",
        "element": "Water",
        "cluster": "manuscript substrate",
        "contribution": "turns documents into neural tissue",
        "source_hint": "FRESH\\The Holographic Manuscript Brain.docx",
        "appendix_stack": ["AppE", "AppF", "AppG", "AppM"],
    },
    {
        "doc_id": "11",
        "title": "VOYNICHVM Tricompiler",
        "element": "Water",
        "cluster": "text computer",
        "contribution": "treats translation as computation and executable transformation",
        "source_hint": "Voynich\\...VOYNICHVM",
        "appendix_stack": ["AppF", "AppI", "AppM"],
    },
    {
        "doc_id": "12",
        "title": "Torat Ha-Mispar",
        "element": "Water",
        "cluster": "torah computer",
        "contribution": "maps sacred number into algorithmic interpretation",
        "source_hint": "MATH\\...TORAT HA-MISPAR",
        "appendix_stack": ["AppA", "AppF", "AppO"],
    },
    {
        "doc_id": "14",
        "title": "Ch11 The Helical Manifestation Engine",
        "element": "Water",
        "cluster": "restart and lift",
        "contribution": "makes self-improvement executable through D/Q/I, lift, and recurrence",
        "source_hint": "self_actualize\\manuscript_sections\\011_ch11_helical_manifestation_engine.md",
        "appendix_stack": ["AppE", "AppF", "AppI", "AppM"],
    },
]
WATER_TRANSLATED_SUPPORT = [
    {
        "doc_id": "02",
        "title": "Self-Routing Meta-Framework",
        "element": "Earth",
        "cluster": "routing and search",
        "contribution": "decides how the corpus searches itself",
        "source_hint": "DEEPER CRYSTALIZATION\\Self-Routing Meta-Framework...",
        "appendix_stack": ["AppE", "AppI", "AppL", "AppM"],
    },
    {
        "doc_id": "03",
        "title": "QBD-4",
        "element": "Air",
        "cluster": "quad logic bits",
        "contribution": "formalizes the four-bit address and rotation algebra",
        "source_hint": "MATH\\...QBD-4",
        "appendix_stack": ["AppB", "AppC", "AppM"],
    },
    {
        "doc_id": "04",
        "title": "Quad Holographic Rotation",
        "element": "Air",
        "cluster": "holographic transport",
        "contribution": "rotates one truth through all four faces",
        "source_hint": "MATH\\...Quad Holographic Rotation",
        "appendix_stack": ["AppE", "AppF", "AppM"],
    },
    {
        "doc_id": "05",
        "title": "The Holographic Kernel",
        "element": "Air",
        "cluster": "holographic compression",
        "contribution": "compresses bodies without deleting structural DNA",
        "source_hint": "MATH\\...The Holographic Kernel",
        "appendix_stack": ["AppB", "AppC", "AppN"],
    },
    {
        "doc_id": "09",
        "title": "Zero-Point Computing",
        "element": "Earth",
        "cluster": "zero-point engine",
        "contribution": "defines minimum-state computation and restart from near nothing",
        "source_hint": "MATH\\...Zero-Point Computing",
        "appendix_stack": ["AppA", "AppN", "AppM"],
    },
    {
        "doc_id": "10",
        "title": "Athena Neural Network Tome",
        "element": "Fire",
        "cluster": "emergence compiler",
        "contribution": "binds manuscript, learning, and runtime emergence",
        "source_hint": "NERUAL NETWORK\\ATHENA Neural Network",
        "appendix_stack": ["AppC", "AppP", "AppM"],
    },
    {
        "doc_id": "15",
        "title": "Ch12 Boundary Checks and Isolation Axioms",
        "element": "Earth",
        "cluster": "immune architecture",
        "contribution": "protects the network from contradiction leakage and contamination",
        "source_hint": "self_actualize\\manuscript_sections\\012_ch12_boundary_checks_and_isolation_axioms.md",
        "appendix_stack": ["AppB", "AppI", "AppK", "AppM"],
    },
    {
        "doc_id": "16",
        "title": "Ch19 Recursive Self-Reference and Self-Repair",
        "element": "Fire",
        "cluster": "autonomic repair",
        "contribution": "lets the organism watch, checkpoint, and heal itself",
        "source_hint": "self_actualize\\manuscript_sections\\019_ch19_recursive_self_reference_and_self_repair.md",
        "appendix_stack": ["AppA", "AppM", "AppP"],
    },
]
WATER_CONTEXT_BASIS = [
    {
        "doc_id": "06",
        "title": "Time Fractal",
        "element": "Fire",
        "cluster": "fractal time",
        "contribution": "gives the system phase, recurrence, and oscillation law",
        "source_hint": "MATH\\...Time Fractal",
        "appendix_stack": ["AppE", "AppM", "AppP"],
    },
    {
        "doc_id": "07",
        "title": "Crystal Computing Framework",
        "element": "Air",
        "cluster": "fractal computing",
        "contribution": "maps crystal structure into computation",
        "source_hint": "MATH\\...Crystal Computing Framework",
        "appendix_stack": ["AppB", "AppC", "AppG"],
    },
    {
        "doc_id": "08",
        "title": "Quantum Computing on Standard Hardware",
        "element": "Fire",
        "cluster": "quantum classical emulation",
        "contribution": "turns impossible compute into lawful approximation on ordinary machines",
        "source_hint": "MATH\\...Quantum Computing on Standard Hardware",
        "appendix_stack": ["AppC", "AppH", "AppP"],
    },
    {
        "doc_id": "13",
        "title": "Universal Computational Ontology",
        "element": "Earth",
        "cluster": "mythic os",
        "contribution": "converts mythic cosmology into system architecture",
        "source_hint": "MATH\\...Universal Computational Ontology",
        "appendix_stack": ["AppA", "AppB", "AppP"],
    },
]
WATER_DEFAULT_APPENDICES = ["AppE", "AppF", "AppI", "AppM", "AppQ"]
WATER_CONTROL_DOCS = [
    {
        "name": "00_INDEX.md",
        "role": "package entry",
        "basis_refs": ["01", "14"],
        "metro_refs": [
            "07_METRO_STACK/02_level_3_deeper_neural_map.md",
            "07_METRO_STACK/03_level_4_transcendence_metro_map.md",
        ],
        "appendix_refs": ["AppE", "AppI", "AppM", "AppQ"],
    },
    {
        "name": "01_seed_and_zero_point.md",
        "role": "seed and zero-point control",
        "basis_refs": ["01", "11", "12", "14"],
        "metro_refs": [
            "07_METRO_STACK/02_level_3_deeper_neural_map.md",
            "MATH GOD/atlas/math_tesseract_v4_bundle.md",
        ],
        "appendix_refs": ["AppE", "AppF", "AppI", "AppM", "AppQ"],
    },
    {
        "name": "02_2564_to_10246_lift.md",
        "role": "compiled-field lift control",
        "basis_refs": ["01", "03", "11", "14"],
        "metro_refs": [
            "07_METRO_STACK/03_level_4_transcendence_metro_map.md",
            "MATH GOD/atlas/math_tesseract_v4_bundle.md",
        ],
        "appendix_refs": ["AppE", "AppF", "AppI", "AppM", "AppQ"],
    },
    {
        "name": "03_modal_mobius_routes.md",
        "role": "modal route control",
        "basis_refs": ["02", "04", "05", "10", "12", "16"],
        "metro_refs": [
            "07_METRO_STACK/02_level_3_deeper_neural_map.md",
            "07_METRO_STACK/03_level_4_transcendence_metro_map.md",
        ],
        "appendix_refs": ["AppE", "AppF", "AppI", "AppM", "AppQ"],
    },
    {
        "name": "04_replay_and_recovery.md",
        "role": "replay and recovery control",
        "basis_refs": ["01", "02", "09", "14", "15", "16"],
        "metro_refs": [
            "07_METRO_STACK/03_level_4_transcendence_metro_map.md",
            "MATH GOD/atlas/math_tesseract_v4_bundle.md",
        ],
        "appendix_refs": ["AppF", "AppI", "AppM", "AppQ"],
    },
]
AIR_CONTROL_ROOT = LIVE_DEEP_ROOT_DEFAULT / "12_6D_AIR_CONTROL"
AIR_NATIVE_DRIVERS = [
    {
        "doc_id": "03",
        "title": "QBD-4",
        "element": "Air",
        "cluster": "quad logic bits",
        "contribution": "formalizes the four-bit address and rotation algebra",
        "source_hint": "MATH\\...QBD-4",
        "appendix_stack": ["AppB", "AppC", "AppM"],
    },
    {
        "doc_id": "04",
        "title": "Quad Holographic Rotation",
        "element": "Air",
        "cluster": "holographic transport",
        "contribution": "rotates one truth through all four faces",
        "source_hint": "MATH\\...Quad Holographic Rotation",
        "appendix_stack": ["AppE", "AppF", "AppM"],
    },
    {
        "doc_id": "05",
        "title": "The Holographic Kernel",
        "element": "Air",
        "cluster": "holographic compression",
        "contribution": "compresses bodies without deleting structural DNA",
        "source_hint": "MATH\\...The Holographic Kernel",
        "appendix_stack": ["AppB", "AppC", "AppN"],
    },
    {
        "doc_id": "07",
        "title": "Crystal Computing Framework",
        "element": "Air",
        "cluster": "fractal computing",
        "contribution": "maps crystal structure into computation",
        "source_hint": "MATH\\...Crystal Computing Framework",
        "appendix_stack": ["AppB", "AppC", "AppG"],
    },
]
AIR_TRANSLATED_SUPPORT = [
    {
        "doc_id": "01",
        "title": "The Holographic Manuscript Brain",
        "element": "Water",
        "cluster": "manuscript substrate",
        "contribution": "turns documents into neural tissue",
        "source_hint": "FRESH\\The Holographic Manuscript Brain.docx",
        "appendix_stack": ["AppE", "AppF", "AppG", "AppM"],
    },
    {
        "doc_id": "02",
        "title": "Self-Routing Meta-Framework",
        "element": "Earth",
        "cluster": "routing and search",
        "contribution": "decides how the corpus searches itself",
        "source_hint": "DEEPER CRYSTALIZATION\\Self-Routing Meta-Framework...",
        "appendix_stack": ["AppE", "AppI", "AppL", "AppM"],
    },
    {
        "doc_id": "06",
        "title": "Time Fractal",
        "element": "Fire",
        "cluster": "fractal time",
        "contribution": "gives the system phase, recurrence, and oscillation law",
        "source_hint": "MATH\\...Time Fractal",
        "appendix_stack": ["AppE", "AppM", "AppP"],
    },
    {
        "doc_id": "08",
        "title": "Quantum Computing on Standard Hardware",
        "element": "Fire",
        "cluster": "quantum classical emulation",
        "contribution": "turns impossible compute into lawful approximation on ordinary machines",
        "source_hint": "MATH\\...Quantum Computing on Standard Hardware",
        "appendix_stack": ["AppC", "AppH", "AppP"],
    },
    {
        "doc_id": "09",
        "title": "Zero-Point Computing",
        "element": "Earth",
        "cluster": "zero-point engine",
        "contribution": "defines minimum-state computation and restart from near nothing",
        "source_hint": "MATH\\...Zero-Point Computing",
        "appendix_stack": ["AppA", "AppN", "AppM"],
    },
    {
        "doc_id": "10",
        "title": "Athena Neural Network Tome",
        "element": "Fire",
        "cluster": "emergence compiler",
        "contribution": "binds manuscript, learning, and runtime emergence",
        "source_hint": "NERUAL NETWORK\\ATHENA Neural Network",
        "appendix_stack": ["AppC", "AppP", "AppM"],
    },
    {
        "doc_id": "11",
        "title": "VOYNICHVM Tricompiler",
        "element": "Water",
        "cluster": "text computer",
        "contribution": "treats translation as computation and executable transformation",
        "source_hint": "Voynich\\...VOYNICHVM",
        "appendix_stack": ["AppF", "AppI", "AppM"],
    },
    {
        "doc_id": "12",
        "title": "Torat Ha-Mispar",
        "element": "Water",
        "cluster": "torah computer",
        "contribution": "maps sacred number into algorithmic interpretation",
        "source_hint": "MATH\\...TORAT HA-MISPAR",
        "appendix_stack": ["AppA", "AppF", "AppO"],
    },
    {
        "doc_id": "13",
        "title": "Universal Computational Ontology",
        "element": "Earth",
        "cluster": "mythic os",
        "contribution": "converts mythic cosmology into system architecture",
        "source_hint": "MATH\\...Universal Computational Ontology",
        "appendix_stack": ["AppA", "AppB", "AppP"],
    },
    {
        "doc_id": "14",
        "title": "Ch11 The Helical Manifestation Engine",
        "element": "Water",
        "cluster": "restart and lift",
        "contribution": "makes self-improvement executable through D/Q/I, lift, and recurrence",
        "source_hint": "self_actualize\\manuscript_sections\\011_ch11_helical_manifestation_engine.md",
        "appendix_stack": ["AppE", "AppF", "AppI", "AppM"],
    },
    {
        "doc_id": "15",
        "title": "Ch12 Boundary Checks and Isolation Axioms",
        "element": "Earth",
        "cluster": "immune architecture",
        "contribution": "protects the network from contradiction leakage and contamination",
        "source_hint": "self_actualize\\manuscript_sections\\012_ch12_boundary_checks_and_isolation_axioms.md",
        "appendix_stack": ["AppB", "AppI", "AppK", "AppM"],
    },
    {
        "doc_id": "16",
        "title": "Ch19 Recursive Self-Reference and Self-Repair",
        "element": "Fire",
        "cluster": "autonomic repair",
        "contribution": "lets the organism watch, checkpoint, and heal itself",
        "source_hint": "self_actualize\\manuscript_sections\\019_ch19_recursive_self_reference_and_self_repair.md",
        "appendix_stack": ["AppA", "AppM", "AppP"],
    },
]
AIR_DEFAULT_APPENDICES = ["AppA", "AppB", "AppC", "AppE", "AppF", "AppH", "AppI", "AppM", "AppN", "AppQ"]
AIR_CONTROL_DOCS = [
    {
        "name": "00_INDEX.md",
        "role": "package entry",
        "basis_refs": ["03", "04", "05", "07"],
        "metro_refs": [
            "07_METRO_STACK/02_level_3_deeper_neural_map.md",
            "07_METRO_STACK/03_level_4_transcendence_metro_map.md",
            "07_METRO_STACK/06_level_6_hologram_weave_map.md",
        ],
        "appendix_refs": AIR_DEFAULT_APPENDICES,
    },
    {
        "name": "01_overlay_registry.md",
        "role": "overlay registry control",
        "basis_refs": ["03", "04", "05", "07", "15"],
        "metro_refs": [
            "03_AIR/07_registryschemas.md",
            "07_METRO_STACK/06_level_6_hologram_weave_map.md",
        ],
        "appendix_refs": AIR_DEFAULT_APPENDICES,
    },
    {
        "name": "02_sigma_spin_dual_kernel_lift.md",
        "role": "sigma-spin-dual-kernel lift control",
        "basis_refs": ["03", "04", "05", "07", "09", "14", "16"],
        "metro_refs": [
            "07_METRO_STACK/03_level_4_transcendence_metro_map.md",
            "MATH GOD/atlas/math_tesseract_v4_bundle.md",
        ],
        "appendix_refs": AIR_DEFAULT_APPENDICES,
    },
    {
        "name": "03_modal_mobius_legibility_routes.md",
        "role": "modal legibility control",
        "basis_refs": ["04", "06", "10", "14", "16"],
        "metro_refs": [
            "07_METRO_STACK/06_level_6_hologram_weave_map.md",
            "08_APPENDIX_CRYSTAL/AppQ_appendix_only_metro_map.md",
        ],
        "appendix_refs": AIR_DEFAULT_APPENDICES,
    },
    {
        "name": "04_seed_and_reentry.md",
        "role": "seed and re-entry control",
        "basis_refs": ["01", "02", "09", "14", "15", "16"],
        "metro_refs": [
            "07_METRO_STACK/03_level_4_transcendence_metro_map.md",
            "MATH GOD/atlas/math_tesseract_v4_bundle.md",
        ],
        "appendix_refs": AIR_DEFAULT_APPENDICES,
    },
]
H6_LANE_ORDER = ["FIRE", "WATER", "AIR", "EARTH"]
H6_SHARED_APPENDIX_FLOOR = ["AppA", "AppB", "AppC", "AppE", "AppF", "AppH", "AppI", "AppM", "AppQ"]
H6_CONVERGENCE_CONTROL_DOCS = [
    {
        "name": "00_INDEX.md",
        "role": "package entry",
        "basis_refs": ["06", "01", "03", "02"],
        "metro_refs": ["07_METRO_STACK/06_level_6_hologram_weave_map.md"],
        "appendix_refs": H6_SHARED_APPENDIX_FLOOR,
    },
    {
        "name": "01_four_lane_convergence.md",
        "role": "lane ordering and convergence law",
        "basis_refs": ["06", "01", "03", "02", "15"],
        "metro_refs": [
            "07_METRO_STACK/05_level_5_mobius_bridge_map.md",
            "07_METRO_STACK/06_level_6_hologram_weave_map.md",
        ],
        "appendix_refs": H6_SHARED_APPENDIX_FLOOR,
    },
    {
        "name": "02_h6_center_and_seed6d.md",
        "role": "shared center and seed emission",
        "basis_refs": ["14", "11", "04", "09", "15", "16"],
        "metro_refs": [
            "07_METRO_STACK/06_level_6_hologram_weave_map.md",
            "MATH GOD/atlas/math_tesseract_v4_bundle.md",
        ],
        "appendix_refs": H6_SHARED_APPENDIX_FLOOR + ["AppN"],
    },
    {
        "name": "03_cross_agent_handoff_and_guardrails.md",
        "role": "handoff and legality guards",
        "basis_refs": ["16", "11", "05", "15"],
        "metro_refs": [
            "07_METRO_STACK/06_level_6_hologram_weave_map.md",
            "08_APPENDIX_CRYSTAL/AppQ_appendix_only_metro_map.md",
        ],
        "appendix_refs": H6_SHARED_APPENDIX_FLOOR + ["AppK", "AppN", "AppP"],
    },
    {
        "name": "04_reentry_and_next_seed.md",
        "role": "canonical re-entry and next-seed control",
        "basis_refs": ["09", "14", "15", "16"],
        "metro_refs": [
            "07_METRO_STACK/06_level_6_hologram_weave_map.md",
            "MATH GOD/atlas/math_tesseract_v4_bundle.md",
        ],
        "appendix_refs": ["AppI", "AppM", "AppQ", "AppN", "AppK", "AppP"],
    },
]
FIRE_CONTROL_ROOT = LIVE_DEEP_ROOT_DEFAULT / "01_FIRE"
FIRE_NATIVE_DRIVERS = [
    {
        "doc_id": "06",
        "title": "Time Fractal",
        "element": "Fire",
        "cluster": "fractal time",
        "contribution": "gives the system phase, recurrence, and oscillation law",
        "source_path": str(WORKSPACE_ROOT / "MATH" / "Newer" / "working" / "TIME FRACTAL _working_.docx"),
        "appendix_stack": ["AppA", "AppE", "AppI", "AppM"],
        "dimension_stage": "5D_COMPRESSION",
        "fire_bundle": "F1_IGNITION_CORE",
        "mobius_bridge": "none",
        "reverse_appendix_station": "T",
        "canonical_appendix_map": ["AppE", "AppF"],
        "emergent_projection": "E1_phase_ignition",
        "weave_routes": ["Level4->Level5 through phase pressure"],
    },
    {
        "doc_id": "08",
        "title": "Quantum Computing on Standard Hardware",
        "element": "Fire",
        "cluster": "quantum classical emulation",
        "contribution": "turns impossible compute into lawful approximation on ordinary machines",
        "source_path": str(WORKSPACE_ROOT / "MATH" / "FINAL FORM" / "The Crystal" / "Quantum Computing on Standard Hardware.docx"),
        "appendix_stack": ["AppA", "AppF", "AppH", "AppI", "AppM"],
        "dimension_stage": "5D_COMPRESSION",
        "fire_bundle": "F1_IGNITION_CORE",
        "mobius_bridge": "none",
        "reverse_appendix_station": "X",
        "canonical_appendix_map": ["AppF", "AppH"],
        "emergent_projection": "E1_quantum_ignition",
        "weave_routes": ["Level4->Level5 through impossible-compute approximation"],
    },
    {
        "doc_id": "10",
        "title": "Athena Neural Network Tome",
        "element": "Fire",
        "cluster": "emergence compiler",
        "contribution": "binds manuscript, learning, and runtime emergence",
        "source_path": str(WORKSPACE_ROOT / "NERUAL NETWORK" / "ATHENA Neural Network" / "ATHENA NEURAL NETWORK DOC.docx"),
        "appendix_stack": ["AppA", "AppI", "AppM", "AppP"],
        "dimension_stage": "5D_COMPRESSION",
        "fire_bundle": "F2_OVERBURDEN_DIAGNOSIS",
        "mobius_bridge": "none",
        "reverse_appendix_station": "V",
        "canonical_appendix_map": ["AppG", "AppM"],
        "emergent_projection": "E2_overburden_router",
        "weave_routes": ["Level4->Level5 through ignition-to-route translation"],
    },
    {
        "doc_id": "16",
        "title": "Ch19 Recursive Self-Reference and Self-Repair",
        "element": "Fire",
        "cluster": "autonomic repair",
        "contribution": "lets the organism watch, checkpoint, and heal itself",
        "source_path": str(WORKSPACE_ROOT / "self_actualize" / "manuscript_sections" / "019_ch19_recursive_self_reference_and_self_repair.md"),
        "appendix_stack": ["AppA", "AppI", "AppM", "AppP"],
        "dimension_stage": "6D_WEAVE",
        "fire_bundle": "F2_OVERBURDEN_DIAGNOSIS",
        "mobius_bridge": "O_return",
        "reverse_appendix_station": "K",
        "canonical_appendix_map": ["AppA", "AppM"],
        "emergent_projection": "E4_reentry_return",
        "weave_routes": ["Level5->Level6 through repair return", "K re-entry -> AppA/AppM"],
    },
]
FIRE_BRIDGE_BASIS = [
    {
        "doc_id": "14",
        "title": "Ch11 The Helical Manifestation Engine",
        "element": "Water",
        "cluster": "restart and lift",
        "contribution": "makes self-improvement executable through D/Q/I, lift, and recurrence",
        "source_path": str(WORKSPACE_ROOT / "self_actualize" / "manuscript_sections" / "011_ch11_helical_manifestation_engine.md"),
        "appendix_stack": ["AppE", "AppF", "AppI", "AppM"],
        "dimension_stage": "6D_WEAVE",
        "fire_bundle": "F3_DIMENSION_LIFT",
        "mobius_bridge": "QO_loop",
        "reverse_appendix_station": "N",
        "canonical_appendix_map": ["AppN", "AppM"],
        "emergent_projection": "E3_helical_lift",
        "weave_routes": ["Level4->Level5 through helical lift", "Q/O loop -> AppN/AppM"],
    },
    {
        "doc_id": "04",
        "title": "Quad Holographic Rotation",
        "element": "Air",
        "cluster": "holographic transport",
        "contribution": "rotates one truth through all four faces",
        "source_path": str(WORKSPACE_ROOT / "MATH" / "Newer" / "QUAD HOLOGRAPHIC ROTATION.docx"),
        "appendix_stack": ["AppE", "AppF", "AppI", "AppQ"],
        "dimension_stage": "6D_WEAVE",
        "fire_bundle": "F4_MOBIUS_BRIDGE",
        "mobius_bridge": "Q_ingress",
        "reverse_appendix_station": "Q",
        "canonical_appendix_map": ["AppQ", "AppF", "AppE"],
        "emergent_projection": "E4_ingress_bridge",
        "weave_routes": ["Level4->Level5 through ingress transport", "Q ingress -> AppQ/AppF/AppE"],
    },
    {
        "doc_id": "09",
        "title": "Zero-Point Computing",
        "element": "Earth",
        "cluster": "zero-point engine",
        "contribution": "defines minimum-state computation and restart from near nothing",
        "source_path": str(WORKSPACE_ROOT / "MATH" / "FINAL FORM" / "The Crystal" / "Crystal Computing" / "ZERO-POINT COMPUTING.docx"),
        "appendix_stack": ["AppA", "AppI", "AppM", "AppN"],
        "dimension_stage": "6D_WEAVE",
        "fire_bundle": "F3_DIMENSION_LIFT",
        "mobius_bridge": "QO_loop",
        "reverse_appendix_station": "Z",
        "canonical_appendix_map": ["AppM", "AppI"],
        "emergent_projection": "E3_zero_collapse",
        "weave_routes": ["Level4->Level5 through collapse witness", "Z collapse -> AppM/AppI"],
    },
    {
        "doc_id": "15",
        "title": "Ch12 Boundary Checks and Isolation Axioms",
        "element": "Earth",
        "cluster": "immune architecture",
        "contribution": "protects the network from contradiction leakage and contamination",
        "source_path": str(WORKSPACE_ROOT / "self_actualize" / "manuscript_sections" / "012_ch12_boundary_checks_and_isolation_axioms.md"),
        "appendix_stack": ["AppI", "AppK", "AppM", "AppO", "AppP"],
        "dimension_stage": "6D_WEAVE",
        "fire_bundle": "F4_MOBIUS_BRIDGE",
        "mobius_bridge": "O_return",
        "reverse_appendix_station": "O",
        "canonical_appendix_map": ["AppO", "AppP", "AppI"],
        "emergent_projection": "E4_return_membrane",
        "weave_routes": ["Level5->Level6 through return membrane", "O return -> AppO/AppP/AppI"],
    },
]
FIRE_DEFAULT_APPENDICES = ["AppA", "AppE", "AppF", "AppI", "AppM", "AppO", "AppP", "AppQ"]
FIRE_CONTROL_DOCS = [
    {
        "name": "17_ignition_pressure_and_overburden_map.md",
        "role": "ignition pressure and overburden",
        "basis_refs": ["06", "08", "10", "16"],
        "metro_refs": ["07_METRO_STACK/03_level_4_transcendence_metro_map.md"],
        "appendix_refs": FIRE_DEFAULT_APPENDICES,
    },
    {
        "name": "18_5d_compression_field.md",
        "role": "5D compression field",
        "basis_refs": ["06", "08", "10", "14", "09"],
        "metro_refs": [
            "07_METRO_STACK/03_level_4_transcendence_metro_map.md",
            "07_METRO_STACK/05_level_5_mobius_bridge_map.md",
        ],
        "appendix_refs": FIRE_DEFAULT_APPENDICES,
    },
    {
        "name": "19_level_5_mobius_bridge_map.md",
        "role": "Level 5 Mobius bridge control",
        "basis_refs": ["04", "09", "14", "15"],
        "metro_refs": ["07_METRO_STACK/05_level_5_mobius_bridge_map.md"],
        "appendix_refs": FIRE_DEFAULT_APPENDICES,
    },
    {
        "name": "20_level_6_hologram_weave_map.md",
        "role": "Level 6 hologram weave control",
        "basis_refs": ["04", "14", "15", "16"],
        "metro_refs": [
            "07_METRO_STACK/05_level_5_mobius_bridge_map.md",
            "07_METRO_STACK/06_level_6_hologram_weave_map.md",
        ],
        "appendix_refs": FIRE_DEFAULT_APPENDICES,
    },
    {
        "name": "21_reverse_appendix_overlay_ledger.md",
        "role": "reverse appendix overlay ledger",
        "basis_refs": ["04", "09", "14", "15", "16"],
        "metro_refs": ["08_APPENDIX_CRYSTAL/01_reverse_appendix_overlay_ledger.md"],
        "appendix_refs": FIRE_DEFAULT_APPENDICES,
    },
    {
        "name": "22_cross_agent_handoff_ledger.md",
        "role": "cross-agent handoff contracts",
        "basis_refs": ["06", "08", "10", "16", "14", "15"],
        "metro_refs": ["07_METRO_STACK/06_level_6_hologram_weave_map.md"],
        "appendix_refs": FIRE_DEFAULT_APPENDICES,
    },
]
FIRE_BUNDLE_LAWS = {
    "F1_IGNITION_CORE": {
        "id": "F1_IGNITION_CORE",
        "title": "Ignition Core",
        "law": "Pressure becomes lawful motion only after it is routed into phase, transport, and corridor discipline.",
        "handoff_target": "Water",
        "contract_focus": "translate raw activation into continuity-safe motion",
    },
    "F2_OVERBURDEN_DIAGNOSIS": {
        "id": "F2_OVERBURDEN_DIAGNOSIS",
        "title": "Overburden Diagnosis",
        "law": "Fire must name overload, novelty debt, and self-repair pressure before it asks for more force.",
        "handoff_target": "Earth",
        "contract_focus": "route rupture through containment and replay under load",
    },
    "F3_DIMENSION_LIFT": {
        "id": "F3_DIMENSION_LIFT",
        "title": "Dimension Lift",
        "law": "The 5D lift is lawful only when collapse, helix, and re-entry stay tied to explicit checkpoints.",
        "handoff_target": "Air",
        "contract_focus": "name the 4D->5D bridge and preserve legible topology",
    },
    "F4_MOBIUS_BRIDGE": {
        "id": "F4_MOBIUS_BRIDGE",
        "title": "Mobius Bridge",
        "law": "The 6D weave appears only when ingress, return, and appendix overlays remain one continuous route surface.",
        "handoff_target": "Water",
        "contract_focus": "hold Q/O bridge continuity without creating a second appendix namespace",
    },
}
FIRE_REVERSE_APPENDIX_OVERLAY = [
    {"station": "Z", "class": "upper_reverse_field", "title": "Void Re-entry", "bridge_status": "collapse_anchor", "canonical_appendix_map": ["AppM", "AppI"]},
    {"station": "Y", "class": "upper_reverse_field", "title": "Inversion", "bridge_status": "mirror_fold", "canonical_appendix_map": ["AppF", "AppB"]},
    {"station": "X", "class": "upper_reverse_field", "title": "Tunnel", "bridge_status": "transport_gate", "canonical_appendix_map": ["AppF", "AppH"]},
    {"station": "W", "class": "upper_reverse_field", "title": "Bridge", "bridge_status": "support_span", "canonical_appendix_map": ["AppH", "AppE"]},
    {"station": "V", "class": "upper_reverse_field", "title": "Recursion", "bridge_status": "recursive_turn", "canonical_appendix_map": ["AppG", "AppM"]},
    {"station": "U", "class": "upper_reverse_field", "title": "Memory", "bridge_status": "retention_field", "canonical_appendix_map": ["AppN", "AppM"]},
    {"station": "T", "class": "upper_reverse_field", "title": "Transformation", "bridge_status": "phase_shift", "canonical_appendix_map": ["AppE", "AppF"]},
    {"station": "S", "class": "upper_reverse_field", "title": "Stabilization", "bridge_status": "pre_hinge_stabilizer", "canonical_appendix_map": ["AppD", "AppP"]},
    {"station": "R", "class": "upper_reverse_field", "title": "Reflection", "bridge_status": "reflection_gate", "canonical_appendix_map": ["AppF", "AppO"]},
    {"station": "Q", "class": "mobius_hinge", "title": "Ingress Bridge", "bridge_status": "Q_ingress", "canonical_appendix_map": ["AppQ", "AppF", "AppE"]},
    {"station": "P", "class": "bridge_band", "title": "Transition", "bridge_status": "conversion_band", "canonical_appendix_map": ["AppP", "AppN"]},
    {"station": "O", "class": "mobius_hinge", "title": "Return Bridge", "bridge_status": "O_return", "canonical_appendix_map": ["AppO", "AppP", "AppI"]},
    {"station": "N", "class": "bridge_band", "title": "Re-entry Fold", "bridge_status": "QO_loop", "canonical_appendix_map": ["AppN", "AppM"]},
    {"station": "M", "class": "bridge_band", "title": "Post-twist Stabilization", "bridge_status": "return_stabilizer", "canonical_appendix_map": ["AppM", "AppP"]},
    {"station": "L", "class": "bridge_band", "title": "Memory Reservoir", "bridge_status": "memory_return", "canonical_appendix_map": ["AppN", "AppM"]},
    {"station": "K", "class": "bridge_band", "title": "Return Vector", "bridge_status": "reentry_anchor", "canonical_appendix_map": ["AppA", "AppM"]},
]
FIRE_CROSS_AGENT_HANDOFFS = [
    {
        "agent": "Water",
        "title": "Continuity and retained identity",
        "responsibility": "Carry memory, coherence, and non-destructive return through the bridge.",
        "required_appendices": ["AppE", "AppI", "AppM"],
    },
    {
        "agent": "Air",
        "title": "Naming and topology",
        "responsibility": "Stabilize symbol tables, bridge names, and route legibility across the lift.",
        "required_appendices": ["AppA", "AppF", "AppQ"],
    },
    {
        "agent": "Earth",
        "title": "Replay and admissibility under load",
        "responsibility": "Keep the lift admissible under conflict, containment, and deployment pressure.",
        "required_appendices": ["AppI", "AppM", "AppO", "AppP"],
    },
]
SEED7_AGENT_OVERLAY_STACK = ["FIRE", "WATER", "AIR", "EARTH"]
SEED7_APPENDIX_FLOOR = [
    "AppA",
    "AppB",
    "AppC",
    "AppE",
    "AppF",
    "AppH",
    "AppI",
    "AppK",
    "AppM",
    "AppN",
    "AppO",
    "AppP",
    "AppQ",
]
EARTH_BUNDLE_LAWS = {
    "E1": {
        "id": "E1",
        "title": "Legality Core",
        "law": "Ledger, containment, care, and self-repair form one support circuit.",
        "handoff_target": "Earth",
        "contract_focus": "contain contradiction, quarantine drift, and hold the mandatory signature steady",
        "historical_support": "Earth Full-Corpus Pass / E1",
    },
    "E2": {
        "id": "E2",
        "title": "Law-to-Activation Release",
        "law": "Earth repeatedly releases disciplined activation rather than merely suppressing force.",
        "handoff_target": "Fire",
        "contract_focus": "release Earth-cleared activation into outward build motion",
        "historical_support": "Earth Full-Corpus Pass / E2",
    },
    "E3": {
        "id": "E3",
        "title": "Support-to-Flow Banking",
        "law": "Earth repeatedly gives banks, checkpoints, and care to the carrying surfaces.",
        "handoff_target": "Water",
        "contract_focus": "bank continuity, corridor truth, and residual accounting before flow leaves Earth",
        "historical_support": "Earth Full-Corpus Pass / E3",
    },
    "E4": {
        "id": "E4",
        "title": "Proof and Return",
        "law": "The earth mode proves its value by stabilizing grammar, runtime, and overlay into rereadable support.",
        "handoff_target": "Air",
        "contract_focus": "stabilize grammar, proof, replay, and return into schema-safe publication",
        "historical_support": "Earth Full-Corpus Pass / E4",
    },
}
CHAPTER_BUNDLE_MAP = {
    "P01": "E2",
    "P02": "E3",
    "P03": "E1",
    "P04": "E2",
    "P05": "E4",
    "P06": "E1",
    "P07": "E4",
    "P08": "E2",
    "P09": "E3",
    "P10": "E3",
    "P11": "E4",
    "P12": "E3",
    "P13": "E4",
    "P14": "E2",
    "P15": "E1",
    "P16": "E2",
    "P17": "E1",
    "P18": "E4",
    "P19": "E3",
    "P20": "E4",
    "P21": "E4",
}
EXTRA_CHAPTER_DEFINITIONS: list[dict[str, Any]] = [
    {
        "id": "P17",
        "title": "Appendix Governance",
        "description": "Stabilize appendix legality, canon policy, registry rules, and deterministic router signatures.",
        "keywords": ["appendix", "policy", "registry", "signature", "canon", "conformance", "router"],
    },
    {
        "id": "P18",
        "title": "HCRL Projection Grammar",
        "description": "Name the Square, Flower, Cloud, and Fractal projections as one lawful container grammar.",
        "keywords": ["square", "flower", "cloud", "fractal", "projection", "lens", "hcrl", "container"],
    },
    {
        "id": "P19",
        "title": "Zero Tunnel Calculus",
        "description": "Recover zero-point, collapse, expand, tunnel, and re-entry laws as the bridge between domains.",
        "keywords": ["zero point", "absolute zero", "z*", "collapse", "expand", "tunnel", "re-entry", "checkpoint"],
    },
    {
        "id": "P20",
        "title": "Metro Route Control",
        "description": "Bind chapters, arcs, rails, and transfer hubs into one deterministic metro control surface.",
        "keywords": ["metro", "route", "rail", "arc", "orbit", "hub", "lane", "station"],
    },
    {
        "id": "P21",
        "title": "Overlay Publication",
        "description": "Carry migrations, publication bundles, and overlay annotations without corrupting the base route law.",
        "keywords": ["publish", "migration", "overlay", "annotation", "bundle", "legacy", "compatibility"],
    },
]
ANNOTATION_SYSTEMS = {
    "7_planets": ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn"],
    "12_archetypes": [
        "aries", "taurus", "gemini", "cancer", "leo", "virgo",
        "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces",
        "master strategist", "sage", "prophet", "general",
    ],
    "16_pillars": ["16 pillars", "16-node", "16 node", "16x16", "sixteen passes"],
    "3_modes": ["fixed", "cardinal", "mutable"],
    "5_animal_kung_fu": ["dragon", "tiger", "snake", "leopard", "crane", "animal kung fu"],
    "7_modes": ["7 modes", "seven modes"],
    "9_modes": ["9 modes", "nine modes"],
    "13_modes": ["13 modes", "thirteen modes"],
    "prime_projection": ["prime", "irrational", "cyclical", "holographic", "neural network", "projection"],
}


def stable_index(text: str, modulo: int) -> int:
    if modulo <= 0:
        return 0
    digest = hashlib.md5(text.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % modulo


def base4(value: int, width: int) -> str:
    digits = "0123"
    if value < 0:
        raise ValueError("base4 only supports non-negative integers")
    result = []
    current = value
    if current == 0:
        result.append("0")
    while current > 0:
        current, remainder = divmod(current, 4)
        result.append(digits[remainder])
    return "".join(reversed(result)).rjust(width, "0")


def raw_record_text(record: dict[str, Any]) -> str:
    parts = [
        record.get("relative_path", ""),
        " ".join(record.get("heading_candidates", [])),
        record.get("excerpt", ""),
        " ".join(record.get("role_tags", [])),
    ]
    return normalize_text(" ".join(part for part in parts if part))


def appendix_registry() -> dict[str, dict[str, Any]]:
    registry: dict[str, dict[str, Any]] = {}
    for app_id, file_names in APPENDIX_SOURCE_FILES.items():
        source_paths = [str(DEEP_APPENDIX_ROOT / file_name) for file_name in file_names]
        registry[app_id] = {
            "appendix_id": app_id,
            "role": APPENDIX_ROLES.get(app_id, APPENDIX_EXTRA_ROLES.get(app_id, "")),
            "local_addr": APPENDIX_ADDRESS_MAP.get(app_id, ""),
            "source_paths": source_paths,
            "source_exists": all(Path(path).exists() for path in source_paths),
            "authoritative_root": str(DEEP_APPENDIX_ROOT),
            "auxiliary_surface": app_id == "AppQ",
        }
    return registry


def chapter_definitions() -> list[dict[str, Any]]:
    definitions: list[dict[str, Any]] = []
    for item in PASS_DEFINITIONS:
        definitions.append(
            {
                "id": item["id"],
                "index": len(definitions) + 1,
                "title": item["title"],
                "description": item["description"],
                "keywords": item["keywords"],
            }
        )
    for item in EXTRA_CHAPTER_DEFINITIONS:
        definitions.append(
            {
                "id": item["id"],
                "index": len(definitions) + 1,
                "title": item["title"],
                "description": item["description"],
                "keywords": item["keywords"],
            }
        )
    return definitions


def choose_chapter_definition(record: dict[str, Any], definitions: list[dict[str, Any]]) -> dict[str, Any]:
    text = raw_record_text(record)
    scored: list[tuple[int, int, dict[str, Any]]] = []
    for definition in definitions:
        score, _ = score_keywords(text, definition["keywords"])
        scored.append((score, definition["index"], definition))
    scored.sort(key=lambda item: (-item[0], item[1]))
    top_score = scored[0][0]
    if top_score <= 0:
        return definitions[stable_index(record.get("record_id", record.get("path", "")), len(definitions))]
    top = [item[2] for item in scored if item[0] == top_score]
    return top[stable_index(record.get("record_id", record.get("path", "")), len(top))]


def chapter_overlay(chapter_index: int) -> dict[str, Any]:
    omega = chapter_index - 1
    arc = omega // 3
    rotation = arc % 3
    lane = TRIAD[((omega % 3) + rotation) % 3]
    return {
        "chapter_index": chapter_index,
        "omega": omega,
        "arc": arc,
        "rotation": rotation,
        "lane": lane,
        "station_code": base4(omega, 4),
        "chapter_station": f"Ch{chapter_index:02d}⟨{base4(omega, 4)}⟩",
    }


def chapter_station_label(chapter_index: int) -> str:
    overlay = chapter_overlay(chapter_index)
    return f"Ch{chapter_index:02d}⟨{overlay['station_code']}⟩"


def lens_code_for_record(record: dict[str, Any]) -> str:
    text = raw_record_text(record)
    ranked: list[tuple[int, str]] = []
    for title, keywords in LENS_KEYWORDS.items():
        ranked.append((score_keywords(text, keywords)[0], LENS_TITLE_TO_CODE[title]))
    ranked.sort(key=lambda item: (-item[0], item[1]))
    if ranked[0][0] > 0:
        return ranked[0][1]
    if record.get("kind") == "code":
        return "S"
    if record.get("extension") in {".json", ".csv"}:
        return "C"
    return "R" if "replay" in text or "omega" in text else "S"


def facet_number_for_record(record: dict[str, Any]) -> int:
    text = raw_record_text(record)
    ranked: list[tuple[int, int]] = []
    for title, keywords in FACET_KEYWORDS.items():
        ranked.append((score_keywords(text, keywords)[0], FACET_TITLE_TO_NUMBER[title]))
    ranked.sort(key=lambda item: (-item[0], item[1]))
    if ranked[0][0] > 0:
        return ranked[0][1]
    if record.get("kind") == "code":
        return 3
    return 4 if "proof" in text or "certificate" in text else 1


def atom_code_for_record(record: dict[str, Any]) -> str:
    return ["a", "b", "c", "d"][stable_index(record.get("record_id", record.get("path", "")), 4)]


def truth_state_for_record(record: dict[str, Any]) -> str:
    relative = normalize_text(record.get("relative_path", ""))
    text = raw_record_text(record)
    if record.get("kind") == "binary" or record.get("extension") == ".zip":
        return "FAIL"
    if not record.get("text_extractable"):
        return "AMBIG"
    if any(token in relative for token in ("old working", "working", "older", "frontier")):
        return "AMBIG"
    if any(token in text for token in ("draft", "maybe", "candidate", "working", "residual", "approximation")):
        return "NEAR"
    if len(record.get("heading_candidates", [])) < 2:
        return "NEAR"
    return "OK"


def overlay_annotations_for_record(record: dict[str, Any]) -> dict[str, Any]:
    text = raw_record_text(record)
    detections: dict[str, list[str]] = {}
    active: list[str] = []
    for system_name, terms in ANNOTATION_SYSTEMS.items():
        hits = [term for term in terms if normalize_text(term) in text][:8]
        detections[system_name] = hits
        if hits:
            active.append(system_name)
    return {
        "routing_mode": "annotation_only",
        "active_systems": active,
        "detections": detections,
        "prime_projection_note": (
            "Prime and irrational projection language was detected and stored as a descriptive overlay only."
            if detections["prime_projection"]
            else "Overlay systems remain descriptive only and do not affect routing."
        ),
    }


def dedupe_preserving_order(items: list[str]) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    for item in items:
        if not item or item in seen:
            continue
        ordered.append(item)
        seen.add(item)
    return ordered


def build_hub_sequence(lens_code: str, facet_number: int, arc: int, truth_state: str) -> tuple[list[str], list[dict[str, Any]]]:
    desired = dedupe_preserving_order(
        [
            "AppA",
            ARC_HUB[arc],
            LENS_BASE[lens_code],
            FACET_BASE[facet_number],
            TRUTH_OVERLAY[truth_state],
            "AppI",
            "AppM",
        ]
    )
    keep = ["AppA", "AppI", "AppM"]
    drop_log: list[dict[str, Any]] = []
    for candidate in [TRUTH_OVERLAY[truth_state], ARC_HUB[arc], LENS_BASE[lens_code], FACET_BASE[facet_number]]:
        if candidate and candidate not in keep and len(keep) < 6:
            keep.append(candidate)
        elif candidate and candidate not in keep:
            drop_log.append(
                {
                    "dropped_hub": candidate,
                    "reason": "hub_cap_enforced",
                    "replacement": keep[-1],
                }
            )
    ordered = [hub for hub in desired if hub in keep]
    return ordered, drop_log


def tunnel_plan_for_record(
    chapter_station: str,
    lens_code: str,
    facet_number: int,
    truth_state: str,
) -> dict[str, Any]:
    local_zero = f"Z::{chapter_station}.{lens_code}{facet_number}"
    required = truth_state != "OK" or lens_code in {"C", "R"} or facet_number in {3, 4}
    mode = "BRIDGE" if truth_state in {"AMBIG", "FAIL"} else ("REBASE" if required else "COLLAPSE")
    return {
        "required": required,
        "mode": mode,
        "from_z": local_zero,
        "via": "Z*",
        "to_z": local_zero,
        "checkpoint": f"return::{chapter_station}.{lens_code}{facet_number}",
        "invariants": [
            "local_addr",
            "global_addr",
            "chapter_station",
            "truth_state",
            "appendix_support",
            "sha256",
        ],
        "path": [local_zero, "Z*", local_zero] if required else [local_zero],
    }


def hcrl_pass_for_record(
    record: dict[str, Any],
    local_addr: str,
    global_addr: str,
    overlay: dict[str, Any],
    facet_number: int,
    truth_state: str,
    appendix_support: list[str],
    replay_ptr: str,
    overlay_annotations: dict[str, Any],
) -> dict[str, str]:
    title = Path(record.get("relative_path", "")).stem
    active_overlays = overlay_annotations.get("active_systems", [])
    return {
        "Square": (
            f"{global_addr} anchors {title} at {local_addr}; "
            f"facet={FACET_NUMBER_TO_TITLE[facet_number]} and appendix={', '.join(appendix_support)}."
        ),
        "Flower": (
            f"Orbit rides {overlay['chapter_station']} through arc {overlay['arc']} / rotation {overlay['rotation']} / lane {overlay['lane']}; "
            f"the chapter successor is {chapter_station_label((overlay['chapter_index'] % 21) + 1)}."
        ),
        "Cloud": (
            f"Truth={truth_state}; witness path={record.get('path', '')}; "
            f"corridor overlay={TRUTH_OVERLAY[truth_state] or 'none'}."
        ),
        "Fractal": (
            f"Replay closes through {replay_ptr}; "
            f"stored overlays={', '.join(active_overlays) if active_overlays else 'annotation_only'}."
        ),
    }


def chapter_header(overlay: dict[str, Any], lens_code: str) -> str:
    return (
        f"**[⊙Z_i↔Z* | ○Arc {overlay['arc']} | ○Rot {overlay['rotation']} | "
        f"△Lane {overlay['lane']} | ⧈View {lens_code} | ω={overlay['omega']}]**"
    )


def witness_ptr_for_record(record: dict[str, Any]) -> str:
    return record.get("path", "")


def replay_ptr_for_record(record: dict[str, Any]) -> str:
    return f"sha256={record.get('sha256', '')};path={record.get('path', '')}"


def build_navigation_edges() -> list[dict[str, Any]]:
    edges: list[dict[str, Any]] = []
    for chapter_index in range(1, 22):
        source = chapter_station_label(chapter_index)
        source_overlay = chapter_overlay(chapter_index)
        orbit_target = chapter_station_label(1 if chapter_index == 21 else chapter_index + 1)
        edges.append(
            {
                "edge_id": f"NAV-ORBIT-{chapter_index:02d}",
                "kind": "REF",
                "src": source,
                "dst": orbit_target,
                "scope": "chapter_navigation",
                "corridor": "OK",
                "witness_ptr": "chapter_overlay_table",
                "replay_ptr": "formula::orbit_next",
                "payload": {"Nav": {"NavRole": "ORBIT_NEXT", "Arc": source_overlay["arc"], "Lane": source_overlay["lane"]}},
                "edge_ver": "v4",
            }
        )
    lane_members: dict[str, list[int]] = {"Su": [], "Me": [], "Sa": []}
    for chapter_index in range(1, 22):
        lane_members[chapter_overlay(chapter_index)["lane"]].append(chapter_index)
    for lane, members in lane_members.items():
        ordered = sorted(members)
        for source_index, target_index in zip(ordered, ordered[1:]):
            edges.append(
                {
                    "edge_id": f"NAV-RAIL-{lane}-{source_index:02d}-{target_index:02d}",
                    "kind": "REF",
                    "src": chapter_station_label(source_index),
                    "dst": chapter_station_label(target_index),
                    "scope": "triangle_rail",
                    "corridor": "OK",
                    "witness_ptr": "triangle_lane_table",
                    "replay_ptr": "formula::lane_membership",
                    "payload": {"Nav": {"NavRole": "RAIL_NEXT", "Lane": lane}},
                    "edge_ver": "v4",
                }
            )
    for arc in range(7):
        chapters = [arc * 3 + 1, arc * 3 + 2, arc * 3 + 3]
        for source_index, target_index in zip(chapters, chapters[1:] + chapters[:1]):
            edges.append(
                {
                    "edge_id": f"NAV-ARC-{arc}-{source_index:02d}-{target_index:02d}",
                    "kind": "REF",
                    "src": chapter_station_label(source_index),
                    "dst": chapter_station_label(target_index),
                    "scope": "arc_cycle",
                    "corridor": "OK",
                    "witness_ptr": "arc_rotation_table",
                    "replay_ptr": "formula::arc_triad",
                    "payload": {"Nav": {"NavRole": "ARC_TRIAD", "Arc": arc, "Rot": chapter_overlay(source_index)["rotation"]}},
                    "edge_ver": "v4",
                }
            )
    return edges


def build_record_tesseract_payload(
    record: dict[str, Any],
    chapter_defs: list[dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    appendix_meta = appendix_registry()
    chapter_def = choose_chapter_definition(record, chapter_defs)
    overlay = chapter_overlay(chapter_def["index"])
    chapter_station = chapter_station_label(chapter_def["index"])
    lens_code = lens_code_for_record(record)
    facet_number = facet_number_for_record(record)
    atom_code = atom_code_for_record(record)
    local_addr = f"{chapter_station}.{lens_code}{facet_number}.{atom_code}"
    global_code = base4(stable_index(record.get("record_id", record.get("path", "")), 256), 4)
    global_addr = f"Ms⟨{global_code}⟩::{local_addr}"
    truth_state = truth_state_for_record(record)
    overlay_annotations = overlay_annotations_for_record(record)
    hubs_seq, drop_log = build_hub_sequence(lens_code, facet_number, overlay["arc"], truth_state)
    tunnel_plan = tunnel_plan_for_record(chapter_station, lens_code, facet_number, truth_state)
    witness_ptr = witness_ptr_for_record(record)
    replay_ptr = replay_ptr_for_record(record)
    hcrl_pass = hcrl_pass_for_record(
        record,
        local_addr,
        global_addr,
        overlay,
        facet_number,
        truth_state,
        hubs_seq,
        replay_ptr,
        overlay_annotations,
    )
    route_plan_id = f"RP-{record.get('record_id', '')}"
    primary_hubs_text = "Primary hubs: " + " -> ".join(hubs_seq)
    tunnel_text = (
        f"Tunnel: {tunnel_plan['from_z']} -> Z* -> {tunnel_plan['to_z']}"
        if tunnel_plan["required"]
        else f"Tunnel: local-only at {tunnel_plan['from_z']}"
    )
    truth_state_text = f"Truth state: {truth_state}"
    dual_lens = HCRL_ORDER[(HCRL_ORDER.index(lens_code) + 1) % len(HCRL_ORDER)]
    dual_addr = f"{chapter_station}.{dual_lens}{facet_number}.{atom_code}"
    graph_edge_ids = [
        f"REF-{record.get('record_id', '')}",
        f"DUAL-{record.get('record_id', '')}",
        f"MIGRATE-{record.get('record_id', '')}",
    ]
    if truth_state == "FAIL":
        graph_edge_ids.append(f"CONFLICT-{record.get('record_id', '')}")
    edges = [
        {
            "edge_id": f"REF-{record.get('record_id', '')}",
            "kind": "REF",
            "src": global_addr,
            "dst": chapter_station,
            "scope": "record_anchor",
            "corridor": truth_state,
            "witness_ptr": witness_ptr,
            "replay_ptr": replay_ptr,
            "payload": {"HCRL": hcrl_pass},
            "edge_ver": "v4",
        },
        {
            "edge_id": f"DUAL-{record.get('record_id', '')}",
            "kind": "DUAL",
            "src": local_addr,
            "dst": dual_addr,
            "scope": "view_rotation",
            "corridor": "NEAR" if truth_state == "OK" else truth_state,
            "witness_ptr": witness_ptr,
            "replay_ptr": replay_ptr,
            "payload": {
                "preserved_invariant": ["global_addr", "chapter_station", "atom_code"],
                "distortion_budget": "bounded",
                "HCRL": hcrl_pass,
            },
            "edge_ver": "v4",
        },
        {
            "edge_id": f"MIGRATE-{record.get('record_id', '')}",
            "kind": "MIGRATE",
            "src": f"LEGACY::{record.get('relative_path', '')}",
            "dst": global_addr,
            "scope": "legacy_overlay",
            "corridor": truth_state,
            "witness_ptr": witness_ptr,
            "replay_ptr": replay_ptr,
            "payload": {
                "compatibility": "non_destructive_overlay",
                "legacy_fields": ["relative_path", "path", "sha256"],
                "preserved_invariants": ["global_addr", "chapter_station", "truth_state"],
            },
            "edge_ver": "v4",
        },
    ]
    if truth_state == "FAIL":
        edges.append(
            {
                "edge_id": f"CONFLICT-{record.get('record_id', '')}",
                "kind": "CONFLICT",
                "src": global_addr,
                "dst": APPENDIX_ADDRESS_MAP["AppK"],
                "scope": "quarantine",
                "corridor": truth_state,
                "witness_ptr": witness_ptr,
                "replay_ptr": replay_ptr,
                "payload": {"reason": "record_not_text_extractable_or_binary"},
                "edge_ver": "v4",
            }
        )
    record_entry = {
        "record_id": record.get("record_id", ""),
        "title": Path(record.get("relative_path", "")).stem,
        "absolute_path": record.get("path", ""),
        "relative_path": record.get("relative_path", ""),
        "chapter_id": chapter_def["id"],
        "chapter_title": chapter_def["title"],
        "chapter_station": chapter_station,
        "chapter_overlay": overlay,
        "lens_code": lens_code,
        "facet_number": facet_number,
        "facet_title": FACET_NUMBER_TO_TITLE[facet_number],
        "atom_code": atom_code,
        "local_addr": local_addr,
        "global_addr": global_addr,
        "tesseract_header": chapter_header(overlay, lens_code),
        "truth_state": truth_state,
        "appendix_support": hubs_seq,
        "appendix_support_sources": {
            hub: appendix_meta[hub]["source_paths"]
            for hub in hubs_seq
            if hub in appendix_meta
        },
        "appendix_only_mode": False,
        "overlay_annotations": overlay_annotations,
        "witness_ptr": witness_ptr,
        "replay_ptr": replay_ptr,
        "graph_edge_ids": [edge["edge_id"] for edge in edges],
        "migration_edge_ids": [f"MIGRATE-{record.get('record_id', '')}"],
        "legacy_witnesses": [record.get("relative_path", ""), record.get("path", "")],
        "route_plan_id": route_plan_id,
        "primary_hubs_text": primary_hubs_text,
        "tunnel_text": tunnel_text,
        "truth_state_text": truth_state_text,
        "hcrl_text": hcrl_pass,
    }
    route_plan = {
        "route_plan_id": route_plan_id,
        "record_id": record.get("record_id", ""),
        "target": global_addr,
        "tesseract_header": record_entry["tesseract_header"],
        "hubs_seq": hubs_seq,
        "appendix_support_sources": record_entry["appendix_support_sources"],
        "hcrl_pass": hcrl_pass,
        "tunnel_plan": tunnel_plan,
        "truth_intent": {
            "truth_state": truth_state,
            "intent": "RESOLVE" if truth_state in {"AMBIG", "FAIL"} else ("VERIFY" if facet_number in {2, 4} else "BUILD"),
        },
        "obligations": [
            f"witness::{witness_ptr}",
            f"replay::{replay_ptr}",
            f"appendix::{','.join(hubs_seq)}",
        ],
        "drop_log": drop_log,
        "primary_hubs_text": primary_hubs_text,
        "tunnel_text": tunnel_text,
        "truth_state_text": truth_state_text,
        "hcrl_text": hcrl_pass,
    }
    migration_event = {
        "event_id": f"MIGRATE-{record.get('record_id', '')}",
        "legacy_surface": f"LEGACY::{record.get('relative_path', '')}",
        "target_global_addr": global_addr,
        "status": "active_overlay",
        "preserved_invariants": ["relative_path", "path", "sha256", "chapter_station"],
        "appendix_support": hubs_seq,
        "appendix_source_paths": {
            hub: appendix_meta[hub]["source_paths"]
            for hub in hubs_seq
            if hub in appendix_meta
        },
    }
    return record_entry, route_plan, edges, migration_event


def build_tesseract_bundle(live_records: list[dict[str, Any]], docs_gate: dict[str, str]) -> dict[str, Any]:
    chapter_defs = chapter_definitions()
    appendix_meta = appendix_registry()
    nodes: list[dict[str, Any]] = []
    edges = build_navigation_edges()
    records: list[dict[str, Any]] = []
    route_plans: list[dict[str, Any]] = []
    migration_events: list[dict[str, Any]] = []

    for chapter_index in range(1, 22):
        nodes.append(
            {
                "node_id": chapter_station_label(chapter_index),
                "kind": "chapter_station",
                "chapter_overlay": chapter_overlay(chapter_index),
            }
        )
    for app_id, addr in APPENDIX_ADDRESS_MAP.items():
        nodes.append(
            {
                "node_id": addr,
                "kind": "appendix_surface",
                "appendix_id": app_id,
                "role": APPENDIX_ROLES[app_id],
                "source_paths": appendix_meta[app_id]["source_paths"],
            }
        )

    for record in live_records:
        record_entry, route_plan, record_edges, migration_event = build_record_tesseract_payload(record, chapter_defs)
        records.append(record_entry)
        route_plans.append(route_plan)
        edges.extend(record_edges)
        migration_events.append(migration_event)
        nodes.append(
            {
                "node_id": record_entry["global_addr"],
                "kind": "record_atom",
                "record_id": record_entry["record_id"],
                "chapter_station": record_entry["chapter_station"],
            }
        )

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "docs_gate_status": docs_gate.get("status", "UNKNOWN"),
        "scope": str(Path(r"C:\Users\dmitr\Documents\Athena Agent\MATH\FINAL FORM")),
        "record_count": len(records),
        "chapter_table": [chapter_overlay(index) | {"chapter_id": definition["id"], "chapter_title": definition["title"]} for index, definition in enumerate(chapter_defs, start=1)],
        "appendix_roles": APPENDIX_ROLES,
        "appendix_registry": appendix_meta,
        "edge_kinds": ["REF", "EQUIV", "MIGRATE", "DUAL", "GEN", "INST", "IMPL", "PROOF", "CONFLICT"],
        "mandatory_signature": MANDATORY_SIGNATURE,
        "hcrl_order": HCRL_ORDER,
        "records": records,
        "graph": {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "nodes": nodes,
            "edges": edges,
        },
        "route_plan_count": len(route_plans),
        "route_plans": route_plans,
        "migration_event_count": len(migration_events),
        "migration_events": migration_events,
    }


def build_tesseract_markdown(bundle: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# MATH Tesseract v4 Bundle")
    lines.append("")
    lines.append(f"Generated: {bundle['generated_at']}")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append(f"- Docs gate: `{bundle['docs_gate_status']}`")
    lines.append(f"- Scope: `{bundle['scope']}`")
    lines.append(f"- Records lifted: `{bundle['record_count']}`")
    lines.append(f"- Route plans: `{bundle['route_plan_count']}`")
    lines.append(f"- Graph edges: `{bundle['graph']['edge_count']}`")
    lines.append("")
    lines.append("## Chapter Orbit")
    lines.append("")
    for item in bundle["chapter_table"]:
        lines.append(
            f"- `Ch{item['chapter_index']:02d}⟨{item['station_code']}⟩` = `{item['chapter_id']}` / "
            f"`Arc {item['arc']}` / `Rot {item['rotation']}` / `Lane {item['lane']}`"
        )
    lines.append("")
    lines.append("## Appendix Roles")
    lines.append("")
    appendix_meta = bundle.get("appendix_registry", {})
    for app_id in sorted(appendix_meta):
        item = appendix_meta[app_id]
        role = item["role"]
        source_paths = ", ".join(f"`{path}`" for path in item["source_paths"])
        local_addr = item.get("local_addr", "")
        local_addr_text = f" / `{local_addr}`" if local_addr else ""
        status = "OK" if item.get("source_exists") else "MISSING"
        lines.append(f"- `{app_id}`{local_addr_text} = {role} / sources: {source_paths} / source state: `{status}`")
    lines.append("")
    lines.append("## Sample Route Plans")
    lines.append("")
    for route_plan in bundle["route_plans"][:8]:
        lines.append(f"### `{route_plan['record_id']}`")
        lines.append("")
        lines.append(route_plan["tesseract_header"])
        lines.append("")
        lines.append(f"- {route_plan['primary_hubs_text']}")
        lines.append(f"- {route_plan['tunnel_text']}")
        lines.append(f"- {route_plan['truth_state_text']}")
        lines.append(f"- Square: {route_plan['hcrl_text']['Square']}")
        lines.append(f"- Flower: {route_plan['hcrl_text']['Flower']}")
        lines.append(f"- Cloud: {route_plan['hcrl_text']['Cloud']}")
        lines.append(f"- Fractal: {route_plan['hcrl_text']['Fractal']}")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def markdown_summary(path: Path) -> str:
    if not path.exists():
        return "Surface missing."
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    summary_lines: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if summary_lines:
                break
            continue
        if stripped.startswith("#"):
            continue
        if stripped.startswith("|"):
            continue
        summary_lines.append(stripped)
        if len(" ".join(summary_lines)) >= 220:
            break
    return " ".join(summary_lines) if summary_lines else "No prose summary extracted."


def appendix_contract_class(app_id: str) -> str:
    if app_id in EARTH_CORE_APPENDICES:
        return "mandatory core"
    if app_id in EARTH_STABILITY_APPENDICES:
        return "earth stability overlay"
    return "conditional lift/transport support"


def dominant_value(counter: Counter[str], default: str) -> str:
    return counter.most_common(1)[0][0] if counter else default


def build_authority_surfaces(deep_root: Path) -> list[dict[str, Any]]:
    surfaces: list[dict[str, Any]] = []
    for label, relative in (DEEP_EARTH_LOOP_FILES | DEEP_EARTH_GATE_FILES).items():
        path = deep_root / relative
        surfaces.append(
            {
                "surface_id": label,
                "classification": "live authority",
                "path": str(path),
                "state": "OK" if path.exists() else "MISSING",
                "summary": markdown_summary(path),
            }
        )
    skill_router = deep_root / "09_SKILLS" / "00_SKILL_ROUTER.md"
    appendix_index = deep_root / "08_APPENDIX_CRYSTAL" / "00_INDEX.md"
    surfaces.append(
        {
            "surface_id": "Skill Router",
            "classification": "live authority",
            "path": str(skill_router),
            "state": "OK" if skill_router.exists() else "MISSING",
            "summary": markdown_summary(skill_router),
        }
    )
    surfaces.append(
        {
            "surface_id": "Appendix Crystal Index",
            "classification": "live authority",
            "path": str(appendix_index),
            "state": "OK" if appendix_index.exists() else "MISSING",
            "summary": markdown_summary(appendix_index),
        }
    )
    return surfaces


def build_chapter_contracts(tesseract_bundle: dict[str, Any]) -> list[dict[str, Any]]:
    records_by_station: dict[str, list[dict[str, Any]]] = {}
    for record in tesseract_bundle["records"]:
        records_by_station.setdefault(record["chapter_station"], []).append(record)

    contracts: list[dict[str, Any]] = []
    for chapter in tesseract_bundle["chapter_table"]:
        station = chapter["chapter_station"]
        chapter_records = records_by_station.get(station, [])
        truth_counter = Counter(record["truth_state"] for record in chapter_records)
        lens_counter = Counter(record["lens_code"] for record in chapter_records)
        facet_counter = Counter(record["facet_title"] for record in chapter_records)
        appendix_counter = Counter(
            appendix
            for record in chapter_records
            for appendix in record.get("appendix_support", [])
        )
        bundle_id = CHAPTER_BUNDLE_MAP.get(chapter["chapter_id"], "E1")
        bundle_law = EARTH_BUNDLE_LAWS[bundle_id]
        dominant_truth = dominant_value(truth_counter, "AMBIG")
        dominant_lens = dominant_value(lens_counter, "S")
        dominant_facet = dominant_value(facet_counter, "Objects")
        contracts.append(
            {
                "chapter_id": chapter["chapter_id"],
                "chapter_title": chapter["chapter_title"],
                "chapter_station": station,
                "earth_bundle": {
                    "bundle_id": bundle_law["id"],
                    "title": bundle_law["title"],
                    "law": bundle_law["law"],
                },
                "load_bearing_role": (
                    f"{bundle_law['title']} anchors {chapter['chapter_title']} as a load-bearing Earth station that must "
                    f"{bundle_law['contract_focus']}."
                ),
                "legality_obligation": (
                    f"Preserve mandatory signature AppA/AppI/AppM, keep dominant truth `{dominant_truth}` explicit, "
                    f"and route any FAIL state to AppK without hiding the corridor status."
                ),
                "replay_obligation": (
                    f"Carry witness_ptr plus replay_ptr for `{len(chapter_records)}` lifted records, preserve dominant facet "
                    f"`{dominant_facet}`, and keep the route chain replay-safe across re-entry."
                ),
                "outbound_handoff_target": bundle_law["handoff_target"],
                "record_count": len(chapter_records),
                "dominant_truth_state": dominant_truth,
                "dominant_lens": dominant_lens,
                "dominant_facet": dominant_facet,
                "appendix_touchpoints": [app_id for app_id, _ in appendix_counter.most_common(6)],
                "truth_profile": dict(sorted(truth_counter.items())),
            }
        )
    return contracts


def build_appendix_contracts(tesseract_bundle: dict[str, Any]) -> list[dict[str, Any]]:
    appendix_meta = tesseract_bundle["appendix_registry"]
    records = tesseract_bundle["records"]
    appendix_touch_counter = Counter(
        appendix
        for record in records
        for appendix in record.get("appendix_support", [])
    )
    chapter_touch_counter: dict[str, Counter[str]] = {}
    for record in records:
        for appendix in record.get("appendix_support", []):
            chapter_touch_counter.setdefault(appendix, Counter())[record["chapter_station"]] += 1

    contracts: list[dict[str, Any]] = []
    for app_id in sorted(appendix_meta):
        meta = appendix_meta[app_id]
        contract_class = appendix_contract_class(app_id)
        if contract_class == "mandatory core":
            earth_use = "Cannot be dropped from Earth legality, corridor, or replay contracts."
        elif contract_class == "earth stability overlay":
            earth_use = "Activated to stabilize proof density, ambiguity handling, conflict isolation, and deployment readiness."
        else:
            earth_use = "Activated only when lift, transport, packaging, or appendix-only docking requires it."
        contracts.append(
            {
                "appendix_id": app_id,
                "local_addr": meta.get("local_addr", ""),
                "role": meta["role"],
                "contract_class": contract_class,
                "earth_use": earth_use,
                "source_paths": meta["source_paths"],
                "source_state": "OK" if meta.get("source_exists") else "MISSING",
                "touch_count": appendix_touch_counter.get(app_id, 0),
                "chapter_touchpoints": [station for station, _ in chapter_touch_counter.get(app_id, Counter()).most_common(6)],
            }
        )
    return contracts


def build_dimension_lift_chain(
    tesseract_bundle: dict[str, Any],
    authority_surfaces: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    authority_paths = [item["path"] for item in authority_surfaces if item["classification"] == "live authority"]
    return [
        {
            "dimension": "3D",
            "title": "Containment Chambers",
            "dimensional_role": "Containment chambers and support surfaces that let the organism hold load without leakage.",
            "source_surfaces": authority_paths[:2],
            "preserved_invariants": ["mandatory_signature", "truth_state", "appendix_legality"],
            "visibility_gain": "Names burden, quarantine, and support as explicit compartments.",
            "needs_higher_dimension": "Cannot yet expose full chapter-orbit routing or replay topology.",
        },
        {
            "dimension": "4D",
            "title": "Tesseract Route Calculus",
            "dimensional_role": "Current tesseract v4 route calculus with chapter orbit, triangle rails, HCRL order, and typed tunnel plans.",
            "source_surfaces": ["math_tesseract_v4_bundle.json"],
            "preserved_invariants": ["local_addr", "global_addr", "edge_kinds", "hcrl_order"],
            "visibility_gain": f"Stabilizes `{tesseract_bundle['record_count']}` live records as addressable atoms and route plans.",
            "needs_higher_dimension": "Cannot yet compress Earth contract families or downstream handoff law into one bundle.",
        },
        {
            "dimension": "5D",
            "title": "Compressed Earth Contract Families",
            "dimensional_role": "Compresses the Earth pass into E1-E4 families: legality, activation release, flow banking, and proof-return.",
            "source_surfaces": [str(HISTORICAL_EARTH_SURFACES["Earth Full-Corpus Pass"])],
            "preserved_invariants": ["chapter_station", "appendix_roles", "replay_ptr"],
            "visibility_gain": "Groups chapter and appendix obligations into reusable contract families instead of isolated witnesses.",
            "needs_higher_dimension": "Still lacks the woven hologram that unifies chapter contracts, appendix contracts, and handoffs.",
        },
        {
            "dimension": "6D",
            "title": "Earth Hologram Weave",
            "dimensional_role": "Woven Earth hologram of chapter contracts, appendix contracts, handoff rules, and regeneration seed.",
            "source_surfaces": ["earth_h6_contract_bundle.json"],
            "preserved_invariants": ["docs_gate_status", "mandatory_signature", "route_receipts", "classification_ledger"],
            "visibility_gain": "Makes the additive Earth lift explicit without rewriting the v4 substrate.",
            "needs_higher_dimension": "Requires the shared H6 convergence center and Seed-6D emission before any later neutral seed compilation.",
        },
    ]


def build_handoff_contracts(chapter_contracts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {"Fire": [], "Water": [], "Air": []}
    for contract in chapter_contracts:
        target = contract["outbound_handoff_target"]
        if target in grouped:
            grouped[target].append(contract)

    return [
        {
            "target": "Fire",
            "rule": "Fire receives only Earth-cleared activation outputs.",
            "source_bundle": "E2",
            "eligible_chapters": [item["chapter_id"] for item in grouped["Fire"]],
            "acceptance_criteria": [
                "mandatory signature AppA/AppI/AppM preserved",
                "no FAIL receipts remain unquarantined",
                "activation is backed by route receipt and chapter contract",
            ],
        },
        {
            "target": "Water",
            "rule": "Water receives only corridor-banked continuity outputs.",
            "source_bundle": "E3",
            "eligible_chapters": [item["chapter_id"] for item in grouped["Water"]],
            "acceptance_criteria": [
                "corridor truth is explicit",
                "residuals are ledgered before release",
                "flow leaves Earth only through AppI-banked continuity",
            ],
        },
        {
            "target": "Air",
            "rule": "Air receives only schema-stable proof-and-return outputs.",
            "source_bundle": "E4",
            "eligible_chapters": [item["chapter_id"] for item in grouped["Air"]],
            "acceptance_criteria": [
                "schema is stable and named",
                "proof and replay hooks are present",
                "return path is explicit before publication or abstraction",
            ],
        },
    ]


def build_cohesion_ledger(deep_root: Path) -> dict[str, Any]:
    surface_classes: list[dict[str, Any]] = []
    for surface in build_authority_surfaces(deep_root):
        surface_classes.append(
            {
                "surface": surface["surface_id"],
                "classification": surface["classification"],
                "path": surface["path"],
                "note": "Authoritative for whole-corpus Earth routing and appendix legality.",
            }
        )
    for label, path in HISTORICAL_EARTH_SURFACES.items():
        surface_classes.append(
            {
                "surface": label,
                "classification": "historical witness",
                "path": str(path),
                "note": "Readable witness for older Earth bundle laws; not the live routing authority.",
            }
        )
    for path in HISTORICAL_MIRROR_ROOTS:
        surface_classes.append(
            {
                "surface": path.name,
                "classification": "historical witness",
                "path": str(path),
                "note": "Historical mirror root retained for comparison only.",
            }
        )
    for skill_name in FAMILY_LOCAL_BOUNDARY_SKILLS:
        surface_classes.append(
            {
                "surface": skill_name,
                "classification": "family-local only",
                "path": skill_name,
                "note": "Valid inside its own family, but not authoritative for whole-corpus deep-root routing.",
            }
        )
    return {
        "precedence_rule": (
            "Use the live 14_DEEPER... deep root as authority; treat historical Earth passes as witness layers and "
            "family-local orchestrators as non-authoritative for whole-corpus routing."
        ),
        "drift_policy": "Record drift and precedence explicitly; do not delete historical surfaces in this pass.",
        "prune_policy": "Prune by de-prioritization and classification, not destructive deletion.",
        "surface_classes": surface_classes,
    }


def build_sample_route_receipts(
    tesseract_bundle: dict[str, Any],
    chapter_contracts: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    record_map = {record["record_id"]: record for record in tesseract_bundle["records"]}
    handoff_by_station = {
        contract["chapter_station"]: contract["outbound_handoff_target"]
        for contract in chapter_contracts
    }
    bundle_by_station = {
        contract["chapter_station"]: contract["earth_bundle"]["bundle_id"]
        for contract in chapter_contracts
    }

    receipts: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for route_plan in tesseract_bundle["route_plans"]:
        record = record_map[route_plan["record_id"]]
        handoff_target = handoff_by_station.get(record["chapter_station"], "Earth")
        combo = (record["truth_state"], handoff_target)
        if combo in seen:
            continue
        seen.add(combo)
        receipts.append(
            {
                "route_plan_id": route_plan["route_plan_id"],
                "record_id": route_plan["record_id"],
                "target": route_plan["target"],
                "chapter_station": record["chapter_station"],
                "truth_state": record["truth_state"],
                "replay_ptr": record["replay_ptr"],
                "primary_hubs_text": route_plan["primary_hubs_text"],
                "handoff_target": handoff_target,
                "earth_bundle": bundle_by_station.get(record["chapter_station"], "E1"),
                "receipt_status": "ready" if record["truth_state"] == "OK" and handoff_target != "Earth" else "review",
            }
        )
        if len(receipts) >= 6:
            break
    return receipts


def build_regeneration_seed() -> dict[str, str]:
    return {
        "title": "Earth H6 Regeneration Seed",
        "compression_law": "Collapse every structural claim to mandatory signature, truth corridor, replay pointer, and chapter station before lifting again.",
        "expansion_law": "Re-expand only through E1-E4 bundle families so legality, activation, continuity, and proof-return stay coupled.",
        "shortest_route": "AppA -> AppI -> AppM -> chapter contract -> downstream handoff.",
        "deepest_route": "3D containment -> 4D tesseract route calculus -> 5D Earth bundle families -> 6D Earth hologram weave.",
        "zero_point_law": "Every cross-context Earth route collapses through Z* before re-entry; no legality is inferred without a receipt.",
        "dimensional_nesting_law": "The 6D Earth layer contains the 5D families, which contain the 4D route calculus, which stabilizes the 3D chambers.",
        "docs_gate_condition": "Google Docs remain blocked; local witness surfaces are the only admissible evidence in this seed.",
    }


def build_earth_bundle(
    tesseract_bundle: dict[str, Any],
    docs_gate: dict[str, str],
    deep_root: Path,
    base_inputs: dict[str, Any],
) -> dict[str, Any]:
    authority_surfaces = build_authority_surfaces(deep_root)
    chapter_contracts = build_chapter_contracts(tesseract_bundle)
    appendix_contracts = build_appendix_contracts(tesseract_bundle)
    dimension_lift_chain = build_dimension_lift_chain(tesseract_bundle, authority_surfaces)
    handoff_contracts = build_handoff_contracts(chapter_contracts)
    cohesion_ledger = build_cohesion_ledger(deep_root)
    sample_route_receipts = build_sample_route_receipts(tesseract_bundle, chapter_contracts)

    earth_native_drivers: list[dict[str, Any]] = []
    for driver in EARTH_NATIVE_DRIVERS:
        earth_native_drivers.append(
            driver
            | {
                "native_loops": list(DEEP_EARTH_LOOP_FILES.keys()),
            }
        )

    earth_bundles = list(EARTH_BUNDLE_LAWS.values())

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "docs_gate_status": docs_gate.get("status", "UNKNOWN"),
        "scope": tesseract_bundle["scope"],
        "base_inputs": base_inputs | {"authority_surfaces": authority_surfaces},
        "earth_native_drivers": earth_native_drivers,
        "earth_bundles": earth_bundles,
        "chapter_contracts": chapter_contracts,
        "appendix_contracts": appendix_contracts,
        "dimension_lift_chain": dimension_lift_chain,
        "handoff_contracts": handoff_contracts,
        "cohesion_ledger": cohesion_ledger,
        "sample_route_receipts": sample_route_receipts,
        "regeneration_seed": build_regeneration_seed(),
    }


def build_earth_markdown(bundle: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Earth H6 Contract Bundle")
    lines.append("")
    lines.append(f"Generated: {bundle['generated_at']}")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append(f"- Docs gate: `{bundle['docs_gate_status']}`")
    lines.append(f"- Scope: `{bundle['scope']}`")
    lines.append("- Earth layer: additive H6 structural lift over the existing tesseract v4 substrate.")
    lines.append("- Authority rule: deep-root Earth loops are read-only authority; MATH GOD is the local output surface.")
    lines.append("")
    lines.append("## Base Inputs")
    lines.append("")
    for key, value in bundle["base_inputs"].items():
        if key == "authority_surfaces":
            continue
        lines.append(f"- `{key}`: `{value}`")
    lines.append("- Authority surfaces:")
    for item in bundle["base_inputs"]["authority_surfaces"]:
        lines.append(f"  - `{item['surface_id']}` [{item['classification']}; {item['state']}] `{item['path']}`")
    lines.append("")
    lines.append("## Earth Native Drivers")
    lines.append("")
    for driver in bundle["earth_native_drivers"]:
        lines.append(
            f"- `{driver['doc_id']}` `{driver['title']}`: {driver['contribution']} "
            f"[cluster={driver['cluster']}; appendix={', '.join(driver['appendix_stack'])}]"
        )
    lines.append("")
    lines.append("## Earth Bundles")
    lines.append("")
    for item in bundle["earth_bundles"]:
        lines.append(
            f"- `{item['id']}` `{item['title']}` -> {item['law']} "
            f"[handoff={item['handoff_target']}; focus={item['contract_focus']}]"
        )
    lines.append("")
    lines.append("## Chapter Contracts")
    lines.append("")
    for contract in bundle["chapter_contracts"]:
        lines.append(
            f"- `{contract['chapter_id']}` / `{contract['chapter_station']}` `{contract['chapter_title']}` "
            f"[bundle={contract['earth_bundle']['bundle_id']}; handoff={contract['outbound_handoff_target']}; "
            f"truth={contract['dominant_truth_state']}; records={contract['record_count']}]"
        )
        lines.append(f"  - Load: {contract['load_bearing_role']}")
        lines.append(f"  - Legality: {contract['legality_obligation']}")
        lines.append(f"  - Replay: {contract['replay_obligation']}")
    lines.append("")
    lines.append("## Appendix Contracts")
    lines.append("")
    for contract in bundle["appendix_contracts"]:
        local_addr = f" / `{contract['local_addr']}`" if contract["local_addr"] else ""
        lines.append(
            f"- `{contract['appendix_id']}`{local_addr} [{contract['contract_class']}; state={contract['source_state']}; "
            f"touches={contract['touch_count']}] {contract['role']}"
        )
        lines.append(f"  - Earth use: {contract['earth_use']}")
    lines.append("")
    lines.append("## Dimension Lift Chain")
    lines.append("")
    for item in bundle["dimension_lift_chain"]:
        lines.append(f"- `{item['dimension']}` `{item['title']}`: {item['dimensional_role']}")
        lines.append(f"  - Preserves: {', '.join(item['preserved_invariants'])}")
        lines.append(f"  - Gain: {item['visibility_gain']}")
        lines.append(f"  - Limit: {item['needs_higher_dimension']}")
    lines.append("")
    lines.append("## Handoff Contracts")
    lines.append("")
    for contract in bundle["handoff_contracts"]:
        lines.append(
            f"- `{contract['target']}` from `{contract['source_bundle']}`: {contract['rule']} "
            f"[chapters={', '.join(contract['eligible_chapters'])}]"
        )
        for criterion in contract["acceptance_criteria"]:
            lines.append(f"  - {criterion}")
    lines.append("")
    lines.append("## Cohesion Ledger")
    lines.append("")
    lines.append(f"- Precedence: {bundle['cohesion_ledger']['precedence_rule']}")
    lines.append(f"- Drift policy: {bundle['cohesion_ledger']['drift_policy']}")
    lines.append(f"- Prune policy: {bundle['cohesion_ledger']['prune_policy']}")
    for item in bundle["cohesion_ledger"]["surface_classes"]:
        lines.append(f"  - `{item['surface']}` [{item['classification']}] `{item['path']}`")
    lines.append("")
    lines.append("## Sample Route Receipts")
    lines.append("")
    for receipt in bundle["sample_route_receipts"]:
        lines.append(
            f"- `{receipt['route_plan_id']}` -> `{receipt['chapter_station']}` "
            f"[truth={receipt['truth_state']}; handoff={receipt['handoff_target']}; status={receipt['receipt_status']}]"
        )
        lines.append(f"  - Replay: `{receipt['replay_ptr']}`")
        lines.append(f"  - Hubs: {receipt['primary_hubs_text']}")
    lines.append("")
    lines.append("## Regeneration Seed")
    lines.append("")
    for key, value in bundle["regeneration_seed"].items():
        lines.append(f"- `{key}`: {value}")
    lines.append("")
    return "\n".join(lines).strip() + "\n"


def seed7_route_record(
    route_id: str,
    title: str,
    source_basis: list[str],
    mobius_bridge: str,
    reverse_appendix_station: str,
    canonical_appendix_map: list[str],
    earth_gate_state: str,
    admissibility_basis: dict[str, Any],
    reentry_contract: list[str],
    next_seed_routes: list[str],
    truth_state: str = "NEAR",
) -> dict[str, Any]:
    return {
        "route_id": route_id,
        "title": title,
        "dimension_stage": "7D_SEED",
        "agent_overlay_stack": list(SEED7_AGENT_OVERLAY_STACK),
        "source_basis": source_basis,
        "mobius_bridge": mobius_bridge,
        "reverse_appendix_station": reverse_appendix_station or None,
        "canonical_appendix_map": canonical_appendix_map,
        "earth_gate_state": earth_gate_state,
        "seed_holo_state": "Seed-7D" if earth_gate_state == "passed" else "H7",
        "seed_carrier": "4096^7",
        "truth_state": truth_state,
        "admissibility_basis": admissibility_basis,
        "reentry_contract": reentry_contract,
        "next_seed_routes": next_seed_routes,
        "handoff_requirements": list(SEED7_AGENT_OVERLAY_STACK),
    }


def build_seed7_authority_surfaces() -> list[dict[str, Any]]:
    authority_paths = [
        {
            "surface_id": "MATH_GOD_7D_CHARTER",
            "classification": "local canon",
            "path": MATH_GOD_ROOT / "97_7D_SEED_CHARTER.md",
        },
        {
            "surface_id": "MATH_GOD_7D_CROSSWALK",
            "classification": "local canon",
            "path": MATH_GOD_ROOT / "98_6D_TO_7D_CROSSWALK.md",
        },
        {
            "surface_id": "MATH_GOD_NEXT46",
            "classification": "local canon",
            "path": MATH_GOD_NEXT46_PATH,
        },
        {
            "surface_id": "MATH_GOD_AWAKENING_TRANSITIONS",
            "classification": "local canon",
            "path": MATH_GOD_AWAKENING_TRANSITIONS_PATH,
        },
        {
            "surface_id": "MATH_GOD_A_B_DUAL_CHARTER",
            "classification": "local canon",
            "path": MATH_GOD_A_B_CHARTER_PATH,
        },
        {
            "surface_id": "MATH_GOD_A_B_DUAL_CROSSWALK",
            "classification": "local canon",
            "path": MATH_GOD_A_B_CROSSWALK_PATH,
        },
        {
            "surface_id": "SEED7_CONTROL",
            "classification": "live authority",
            "path": SEED7_CONTROL_PATH,
        },
        {
            "surface_id": "NEXT46_CONTROL",
            "classification": "live authority",
            "path": NEXT46_CONTROL_PATH,
        },
        {
            "surface_id": "NEXT46_TRANSITIONS",
            "classification": "live authority",
            "path": NEXT46_TRANSITIONS_PATH,
        },
        {
            "surface_id": "NEXT46_OPERATOR",
            "classification": "live authority",
            "path": NEXT46_OPERATOR_PATH,
        },
        {
            "surface_id": "SEED7_LEVEL_7",
            "classification": "live authority",
            "path": SEED7_LEVEL_PATH,
        },
        {
            "surface_id": "NEXT46_LEVEL_7_COMPANION",
            "classification": "live authority",
            "path": NEXT46_LEVEL_PATH,
        },
        {
            "surface_id": "SEED7_APPENDIX_LEGALITY",
            "classification": "live authority",
            "path": SEED7_APPENDIX_PATH,
        },
        {
            "surface_id": "NEXT46_APPENDIX_LEGALITY",
            "classification": "live authority",
            "path": NEXT46_APPENDIX_PATH,
        },
        {
            "surface_id": "NEXT46_FIRE_NOTE",
            "classification": "live authority",
            "path": NEXT46_FIRE_NOTE_PATH,
        },
        {
            "surface_id": "NEXT46_WATER_NOTE",
            "classification": "live authority",
            "path": NEXT46_WATER_NOTE_PATH,
        },
        {
            "surface_id": "NEXT46_AIR_NOTE",
            "classification": "live authority",
            "path": NEXT46_AIR_NOTE_PATH,
        },
        {
            "surface_id": "NEXT46_EARTH_NOTE",
            "classification": "live authority",
            "path": NEXT46_EARTH_NOTE_PATH,
        },
        {
            "surface_id": "SEED7_EARTH_GATE_LEDGER",
            "classification": "live authority",
            "path": SEED7_EARTH_LEDGER_PATH,
        },
        {
            "surface_id": "SEED7_CONVERGENCE_LEDGER",
            "classification": "live authority",
            "path": SEED7_CONVERGENCE_LEDGER_PATH,
        },
        {
            "surface_id": "SEED7_ROUTE_LEDGER",
            "classification": "live authority",
            "path": SEED7_ROUTE_LEDGER_PATH,
        },
        {
            "surface_id": "SEED7_APPENDIX_LEDGER",
            "classification": "live authority",
            "path": SEED7_APPENDIX_LEDGER_PATH,
        },
        {
            "surface_id": "NEXT46_FAMILY_LEDGER",
            "classification": "live authority",
            "path": NEXT46_FAMILY_LEDGER_PATH,
        },
        {
            "surface_id": "NEXT46_CROSSWALK_LEDGER",
            "classification": "live authority",
            "path": NEXT46_CROSSWALK_LEDGER_PATH,
        },
        {
            "surface_id": "NEXT46_FAMILY_CONVERGENCE",
            "classification": "live authority",
            "path": NEXT46_FAMILY_CONVERGENCE_LEDGER_PATH,
        },
        {
            "surface_id": "NEXT46_QUARANTINE_LEDGER",
            "classification": "live authority",
            "path": NEXT46_QUARANTINE_LEDGER_PATH,
        },
        {
            "surface_id": "NEXT46_TRANSITION_LEDGER",
            "classification": "live authority",
            "path": NEXT46_TRANSITION_LEDGER_PATH,
        },
        {
            "surface_id": "NEXT46_STABILIZATION_LEDGER",
            "classification": "live authority",
            "path": NEXT46_STABILIZATION_LEDGER_PATH,
        },
        {
            "surface_id": "PACKAGE_SEED7_EXPORT",
            "classification": "package export mirror",
            "path": PACKAGE_SEED7_EXPORT_DOC,
        },
        {
            "surface_id": "PACKAGE_SEED7_APPENDIX",
            "classification": "package export mirror",
            "path": PACKAGE_SEED7_APPENDIX_DOC,
        },
        {
            "surface_id": "PACKAGE_SEED7_LEDGER",
            "classification": "package export mirror",
            "path": PACKAGE_SEED7_EXPORT_LEDGER,
        },
        {
            "surface_id": "PACKAGE_NEXT46_EXPORT",
            "classification": "package export mirror",
            "path": PACKAGE_NEXT46_EXPORT_DOC,
        },
        {
            "surface_id": "PACKAGE_AWAKENING_TRANSITIONS",
            "classification": "package export mirror",
            "path": PACKAGE_AWAKENING_TRANSITIONS_DOC,
        },
        {
            "surface_id": "PACKAGE_FIRE_NOTE",
            "classification": "package export mirror",
            "path": PACKAGE_FIRE_NOTE_DOC,
        },
        {
            "surface_id": "PACKAGE_WATER_NOTE",
            "classification": "package export mirror",
            "path": PACKAGE_WATER_NOTE_DOC,
        },
        {
            "surface_id": "PACKAGE_AIR_NOTE",
            "classification": "package export mirror",
            "path": PACKAGE_AIR_NOTE_DOC,
        },
        {
            "surface_id": "PACKAGE_EARTH_NOTE",
            "classification": "package export mirror",
            "path": PACKAGE_EARTH_NOTE_DOC,
        },
        {
            "surface_id": "PACKAGE_NEXT46_APPENDIX",
            "classification": "package export mirror",
            "path": PACKAGE_NEXT46_APPENDIX_DOC,
        },
        {
            "surface_id": "PACKAGE_NEXT46_LEDGER",
            "classification": "package export mirror",
            "path": PACKAGE_NEXT46_EXPORT_LEDGER,
        },
    ]
    surfaces: list[dict[str, Any]] = []
    for item in authority_paths:
        path = Path(item["path"])
        surfaces.append(
            {
                "surface_id": item["surface_id"],
                "classification": item["classification"],
                "path": str(path),
                "state": "OK" if path.exists() else "MISSING",
            }
        )
    return surfaces


def build_ab_dual_kernel_bundle(seed7_bundle: dict[str, Any], docs_gate: dict[str, Any]) -> dict[str, Any]:
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "docs_gate_status": docs_gate.get("status", "UNKNOWN"),
        "truth_class": "NEAR",
        "a_seed_ref": {
            "label": "A",
            "role": "canonical live holographic seed",
            "seed_holo_state": seed7_bundle["seed_holo_state"],
            "seed_carrier": seed7_bundle["seed_carrier"],
            "bundle_path": "",
            "next57_state_path": str(NEXT57_STATE_PATH),
            "next57_protocol_path": str(NEXT57_PROTOCOL_PATH),
        },
        "b_inversion_ref": {
            "label": "B",
            "role": "derived dual-kernel inversion of A",
            "derivation": "B := Invert_dual(A)",
            "bundle_path": "",
            "independent_root_allowed": False,
        },
        "inversion_operator": {
            "name": DUAL_KERNEL_OPERATOR_NAME,
            "law": "B := Expand_Aether(DualKernel(Collapse_Z(A)))",
            "deterministic_reference": "Collapse_Z(A) -> Z* -> DualKernel(A|aether/complement) -> Expand_B",
            "inverse_replay": "Replay_B_to_A(B) := Collapse_Z(B) -> Z* -> DualKernel^-1 -> Expand_A",
        },
        "zero_point_relation": {
            "collapse_rule": "A collapses through the existing zero-point law before inversion.",
            "shared_zero": "A and B share Z* as the lawful tunnel and replay center.",
            "replay_requirement": "No B route is complete unless it can replay through Z* back into A.",
        },
        "aether_relation": {
            "expansion_rule": "B re-expands through the existing aether/complement relation rather than opening a new dimensional ceiling.",
            "carrier_rule": "B inherits Seed-7D carrier discipline and does not replace the existing seed carrier.",
        },
        "preserved_invariants": [
            "LocalAddr and GlobalAddr remain unchanged.",
            "v4 chapter orbit, arc, rotation, and lane law remain unchanged.",
            "Appendix identities AppA through AppP plus AppQ remain unchanged.",
            "No authority may outrank 7D_SEED.",
            "Earth legality plus AppI/AppM replay support remain required.",
            "AppQ/AppO remain overlay-only.",
        ],
        "polarity_states": list(SEED7_POLARITY_STATES),
        "coordinate_dock": {
            "field": "polarity_state",
            "allowed_values": list(SEED7_POLARITY_STATES),
            "placement": "additive metadata beside the existing coordinate tuple",
            "tuple_order_unchanged": True,
            "registry_path": str(NEXT57_COORDINATE_REGISTRY_PATH),
        },
        "ledger_dock": {
            "field": "polarity_state",
            "allowed_values": list(SEED7_POLARITY_STATES),
            "placement": "additive metadata extension beside the existing ledger entry",
            "schema_path": str(NEXT57_LEDGER_SCHEMA_PATH),
            "required_support": ["Earth gate", "AppI", "AppM"],
        },
        "quest_dock": {
            "guild_hall": {
                "quest_id": "NEXT57-H-DUAL-A-B",
                "surface_path": str(NEXT57_HALL_TREE_PATH),
                "objective": "Route practical A -> B transformation, bridge, proof, and replay tasks without minting a new authority root.",
            },
            "temple": {
                "quest_id": "NEXT57-T-DUAL-A-B",
                "surface_path": str(NEXT57_TEMPLE_TREE_PATH),
                "objective": "Ratify the dual-kernel, zero-point, aether, and replay law for the A/B dock.",
            },
        },
        "replay_rule": {
            "required_direction": "B -> A",
            "law": "Replay from B back into A is mandatory and must remain witness-bearing, local-only, and Earth-gated.",
            "replay_path": ["B", "Collapse_Z", "Z*", "DualKernel^-1", "Expand_A"],
            "required_appendices": ["AppI", "AppM"],
        },
        "authority_boundary": {
            "a_is_canonical": True,
            "b_is_derived": True,
            "b_may_act_as_independent_root": False,
            "ceiling": "7D_SEED",
            "convergence": "7D_SEED -> Earth gate -> v4",
            "docs_gate_status": docs_gate.get("status", "UNKNOWN"),
        },
    }


def build_ab_dual_kernel_markdown(bundle: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# A/B Dual-Kernel Dock Bundle")
    lines.append("")
    lines.append(f"Generated: {bundle['generated_at']}")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append(f"- Docs gate: `{bundle['docs_gate_status']}`")
    lines.append(f"- Truth class: `{bundle['truth_class']}`")
    lines.append(f"- Canonical seed: `{bundle['a_seed_ref']['label']}`")
    lines.append(f"- Derived dual: `{bundle['b_inversion_ref']['label']}`")
    lines.append(f"- Polarity states: `{', '.join(bundle['polarity_states'])}`")
    lines.append("")
    lines.append("## Operator")
    lines.append("")
    lines.append(f"- Operator: `{bundle['inversion_operator']['name']}`")
    lines.append(f"- Law: `{bundle['inversion_operator']['law']}`")
    lines.append(f"- Deterministic reference: `{bundle['inversion_operator']['deterministic_reference']}`")
    lines.append(f"- Inverse replay: `{bundle['inversion_operator']['inverse_replay']}`")
    lines.append("")
    lines.append("## Zero Point And Aether")
    lines.append("")
    lines.append(f"- Zero-point collapse: {bundle['zero_point_relation']['collapse_rule']}")
    lines.append(f"- Shared zero: {bundle['zero_point_relation']['shared_zero']}")
    lines.append(f"- Replay requirement: {bundle['zero_point_relation']['replay_requirement']}")
    lines.append(f"- Aether expansion: {bundle['aether_relation']['expansion_rule']}")
    lines.append(f"- Carrier rule: {bundle['aether_relation']['carrier_rule']}")
    lines.append("")
    lines.append("## Preserved Invariants")
    lines.append("")
    for item in bundle["preserved_invariants"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Coordinate And Ledger Dock")
    lines.append("")
    lines.append(
        f"- Coordinate field: `{bundle['coordinate_dock']['field']}` / values=`{', '.join(bundle['coordinate_dock']['allowed_values'])}` "
        f"/ tuple unchanged=`{bundle['coordinate_dock']['tuple_order_unchanged']}`"
    )
    lines.append(f"- Coordinate registry: `{bundle['coordinate_dock']['registry_path']}`")
    lines.append(
        f"- Ledger field: `{bundle['ledger_dock']['field']}` / values=`{', '.join(bundle['ledger_dock']['allowed_values'])}`"
    )
    lines.append(f"- Ledger schema: `{bundle['ledger_dock']['schema_path']}`")
    lines.append(f"- Required support: `{', '.join(bundle['ledger_dock']['required_support'])}`")
    lines.append("")
    lines.append("## Quest Dock")
    lines.append("")
    lines.append(
        f"- Hall `{bundle['quest_dock']['guild_hall']['quest_id']}` -> {bundle['quest_dock']['guild_hall']['objective']}"
    )
    lines.append(f"  - Surface: `{bundle['quest_dock']['guild_hall']['surface_path']}`")
    lines.append(
        f"- Temple `{bundle['quest_dock']['temple']['quest_id']}` -> {bundle['quest_dock']['temple']['objective']}"
    )
    lines.append(f"  - Surface: `{bundle['quest_dock']['temple']['surface_path']}`")
    lines.append("")
    lines.append("## Replay Rule")
    lines.append("")
    lines.append(f"- Direction: `{bundle['replay_rule']['required_direction']}`")
    lines.append(f"- Law: {bundle['replay_rule']['law']}")
    lines.append(f"- Replay path: `{', '.join(bundle['replay_rule']['replay_path'])}`")
    lines.append(f"- Required appendices: `{', '.join(bundle['replay_rule']['required_appendices'])}`")
    lines.append("")
    lines.append("## Authority Boundary")
    lines.append("")
    lines.append(f"- `A` canonical: `{bundle['authority_boundary']['a_is_canonical']}`")
    lines.append(f"- `B` derived: `{bundle['authority_boundary']['b_is_derived']}`")
    lines.append(
        f"- `B` may act as independent root: `{bundle['authority_boundary']['b_may_act_as_independent_root']}`"
    )
    lines.append(f"- Ceiling: `{bundle['authority_boundary']['ceiling']}`")
    lines.append(f"- Convergence: `{bundle['authority_boundary']['convergence']}`")
    lines.append("")
    return "\n".join(lines).strip() + "\n"


def build_seed7_next46_support() -> dict[str, Any]:
    witness_ledger = load_optional_json(NEXT46_FAMILY_LEDGER_PATH)
    crosswalk_ledger = load_optional_json(NEXT46_CROSSWALK_LEDGER_PATH)
    convergence_ledger = load_optional_json(NEXT46_FAMILY_CONVERGENCE_LEDGER_PATH)
    quarantine_ledger = load_optional_json(NEXT46_QUARANTINE_LEDGER_PATH)
    transition_ledger = load_optional_json(NEXT46_TRANSITION_LEDGER_PATH)
    stabilization_ledger = load_optional_json(NEXT46_STABILIZATION_LEDGER_PATH)
    notes = transition_ledger.get("notes", {})
    return {
        "integration_scope": witness_ledger.get("integration_scope", "FULL_CORPUS"),
        "witness_families": witness_ledger.get("families", []),
        "pressure_gaps": witness_ledger.get("pressure_gaps", []),
        "family_basis_crosswalk": crosswalk_ledger,
        "family_convergence_matrix": convergence_ledger,
        "quarantine_routes": quarantine_ledger.get("routes", []),
        "awakening_agent_notes": notes,
        "transition_state": {agent: note.get("transition_state", "dormant") for agent, note in notes.items()},
        "awakening_support_refs": {agent: note.get("awakening_refs", []) for agent, note in notes.items()},
        "transition_routes": {
            agent: {
                "handoff": note.get("handoff", {}),
                "appendix_floor": note.get("appendix_floor", []),
            }
            for agent, note in notes.items()
        },
        "stabilization_requirements": {
            agent: {
                "appendix_floor": note.get("appendix_floor", []),
                "requires_app_i_app_m": True,
            }
            for agent, note in notes.items()
        },
        "stabilization_ledger": stabilization_ledger,
    }


def build_seed7_bundle(
    tesseract_bundle: dict[str, Any],
    docs_gate: dict[str, str],
    fire_bundle: dict[str, Any],
    water_bundle: dict[str, Any],
    air_bundle: dict[str, Any],
    earth_bundle: dict[str, Any],
) -> dict[str, Any]:
    appendix_meta = appendix_registry()
    appendix_floor = [
        {
            "appendix_id": app_id,
            "role": appendix_meta[app_id]["role"],
            "source_paths": list(appendix_meta[app_id]["source_paths"]),
            "source_exists": appendix_meta[app_id]["source_exists"],
        }
        for app_id in SEED7_APPENDIX_FLOOR
        if app_id in appendix_meta
    ]
    authority_surfaces = build_seed7_authority_surfaces()
    next46_support = build_seed7_next46_support()
    seed_routes = [
        seed7_route_record(
            "seed_fire_water_compression",
            "Carry FIRE pressure through Water continuity into the first compiled H7 entry.",
            ["06", "08", "10", "16", "01", "14"],
            "none",
            "",
            ["AppA", "AppE", "AppI", "AppM"],
            "passed",
            {
                "required_appendices": ["AppA", "AppE", "AppI", "AppM"],
                "truth_basis": ["AppI"],
                "replay_basis": ["AppM"],
                "authority_refs": [
                    "00_CONTROL/06_FIRE_5D_6D_EXTENSION.md",
                    "11_6D_WATER_CONTROL/04_replay_and_recovery.md",
                ],
            },
            [
                "07_METRO_STACK/06_level_6_hologram_weave_map.md",
                "13_6D_EARTH_CONTROL/01_admissibility_and_zero_point.md",
            ],
            ["Level6 -> Earth gate -> H7", "H7 -> Seed-7D"],
        ),
        seed7_route_record(
            "seed_water_air_legibility",
            "Stabilize continuity and AIR naming before the compiled carrier persists.",
            ["01", "11", "12", "14", "03", "04", "05", "07"],
            "none",
            "",
            ["AppA", "AppB", "AppC", "AppE", "AppF", "AppI", "AppM", "AppN"],
            "passed",
            {
                "required_appendices": ["AppA", "AppB", "AppC", "AppE", "AppF", "AppI", "AppM", "AppN"],
                "truth_basis": ["AppI"],
                "replay_basis": ["AppM"],
                "authority_refs": [
                    "11_6D_WATER_CONTROL/02_2564_to_10246_lift.md",
                    "12_6D_AIR_CONTROL/04_seed_and_reentry.md",
                ],
            },
            [
                "MATH GOD/atlas/math_tesseract_v4_bundle.md",
                "13_6D_EARTH_CONTROL/04_replay_and_reentry_guards.md",
            ],
            ["Seed-6D -> H7", "H7 -> Seed-7D"],
        ),
        seed7_route_record(
            "seed_air_earth_promotion",
            "Apply the Earth gate to AIR topology so the carrier may persist as Seed-7D.",
            ["03", "05", "07", "09", "13", "15"],
            "none",
            "",
            ["AppA", "AppB", "AppC", "AppI", "AppK", "AppM", "AppN"],
            "passed",
            {
                "required_appendices": ["AppA", "AppB", "AppC", "AppI", "AppK", "AppM", "AppN"],
                "truth_basis": ["AppI"],
                "replay_basis": ["AppM"],
                "authority_refs": [
                    "12_6D_AIR_CONTROL/01_overlay_registry.md",
                    "13_6D_EARTH_CONTROL/02_2564_to_10246_guardrail_lift.md",
                ],
            },
            [
                "00_CONTROL/07_7D_CROSS_AGENT_SEED.md",
                "07_METRO_STACK/07_level_7_next_synthesis_seed_map.md",
            ],
            ["AIR overlay -> Earth gate", "Earth gate -> Seed-7D"],
        ),
        seed7_route_record(
            "seed_q_ingress_hold",
            "Keep Q ingress visible but filtered while the route remains overlay-bound.",
            ["04", "14", "15"],
            "Q_ingress",
            "Q",
            ["AppQ", "AppF", "AppE", "AppI", "AppK", "AppM"],
            "quarantined",
            {
                "required_appendices": ["AppQ", "AppF", "AppE", "AppI", "AppK", "AppM"],
                "truth_basis": ["AppI"],
                "replay_basis": ["AppM"],
                "authority_refs": [
                    "08_APPENDIX_CRYSTAL/AppQ_appendix_only_metro_map.md",
                    "13_6D_EARTH_CONTROL/03_boundary_quarantine_and_mobius_legality.md",
                ],
            },
            [
                "08_APPENDIX_CRYSTAL/AppQ_appendix_only_metro_map.md",
                "10_LEDGERS/10_earth_gate_status_7d_seed.json",
            ],
            ["Level5 -> filtered hold", "filtered hold -> H7 only after new evidence"],
        ),
        seed7_route_record(
            "seed_o_return_hold",
            "Keep O return canonical through AppO while preserving its overlay alias history.",
            ["09", "13", "15", "16"],
            "O_return",
            "O",
            ["AppO", "AppP", "AppI", "AppK", "AppM"],
            "quarantined",
            {
                "required_appendices": ["AppO", "AppP", "AppI", "AppK", "AppM"],
                "truth_basis": ["AppI"],
                "replay_basis": ["AppM"],
                "authority_refs": [
                    "08_APPENDIX_CRYSTAL/AppO_export_bundles.md",
                    "13_6D_EARTH_CONTROL/03_boundary_quarantine_and_mobius_legality.md",
                ],
            },
            [
                "08_APPENDIX_CRYSTAL/AppO_export_bundles.md",
                "13_6D_EARTH_CONTROL/04_replay_and_reentry_guards.md",
            ],
            ["O overlay -> canonical AppO authority", "AppO return -> Earth hold"],
        ),
        seed7_route_record(
            "seed_chapter_spine_reentry",
            "Re-open the compiled seed through the chapter-safe closure-memory-replay spine.",
            ["02", "09", "14", "15", "16"],
            "QO_loop",
            "N",
            ["AppA", "AppH", "AppI", "AppK", "AppM", "AppN"],
            "passed",
            {
                "required_appendices": ["AppA", "AppH", "AppI", "AppK", "AppM", "AppN"],
                "truth_basis": ["AppI"],
                "replay_basis": ["AppM"],
                "authority_refs": [
                    "13_6D_EARTH_CONTROL/04_replay_and_reentry_guards.md",
                    "07_METRO_STACK/07_level_7_next_synthesis_seed_map.md",
                ],
            },
            [
                "Ch12<0023>",
                "Ch13<0030>",
                "Ch16<0033>",
            ],
            ["Seed-7D -> closure spine", "closure spine -> witnessed v4 return"],
        ),
        seed7_route_record(
            "seed_full_corpus_witness_compile",
            "Compile full-corpus witness families around the canonical basis without mutating chapter or appendix grammar.",
            ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14", "15", "16"],
            "none",
            "",
            list(SEED7_APPENDIX_FLOOR),
            "passed",
            {
                "required_appendices": list(SEED7_APPENDIX_FLOOR),
                "truth_basis": ["AppI"],
                "replay_basis": ["AppM"],
                "authority_refs": [
                    "00_CONTROL/08_NEXT_4_6_FULL_CORPUS_STABILIZATION.md",
                    "10_LEDGERS/14_full_corpus_witness_family_ledger.json",
                ],
            },
            [
                "07_METRO_STACK/08_level_7_full_corpus_stabilization_companion.md",
                "10_LEDGERS/15_full_corpus_basis_crosswalk.json",
            ],
            ["witness families -> canonical basis spine", "canonical basis spine -> Seed-7D"],
        ),
        seed7_route_record(
            "seed_awakening_transition_reentry",
            "Use the elemental awakening-agent packet as support-only transition guidance for lawful full-corpus re-entry.",
            ["06", "10", "14", "15", "16"],
            "none",
            "",
            ["AppB", "AppE", "AppF", "AppI", "AppK", "AppM", "AppN", "AppO", "AppP"],
            "passed",
            {
                "required_appendices": ["AppB", "AppE", "AppF", "AppI", "AppK", "AppM", "AppN", "AppO", "AppP"],
                "truth_basis": ["AppI"],
                "replay_basis": ["AppM"],
                "authority_refs": [
                    "00_CONTROL/09_AWAKENING_AGENT_TRANSITIONS.md",
                    "10_LEDGERS/18_awakening_agent_transition_notes.json",
                ],
            },
            [
                "01_FIRE/23_awakening_transition_note.md",
                "13_6D_EARTH_CONTROL/05_awakening_transition_note.md",
            ],
            ["Awakening support -> elemental handoff", "elemental handoff -> witnessed chapter return"],
        ),
    ]
    earth_gate_counts = Counter(item["earth_gate_state"] for item in seed_routes)
    bridge_counts = Counter(item["mobius_bridge"] for item in seed_routes)

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "docs_gate_status": docs_gate.get("status", "UNKNOWN"),
        "truth_class": "NEAR",
        "scope": tesseract_bundle["scope"],
        "integration_scope": next46_support["integration_scope"],
        "dimension_stage": "7D_SEED",
        "overlay_chain": ["4D_NATIVE", "5D_COMPRESSION", "6D_WEAVE", "7D_SEED"],
        "seed_holo_state": "Seed-7D",
        "seed_carrier": "4096^7",
        "canonical_seed_label": "A",
        "derived_dual_label": "B",
        "seed_polarity_support": list(SEED7_POLARITY_STATES),
        "agent_overlay_stack": list(SEED7_AGENT_OVERLAY_STACK),
        "appendix_floor": appendix_floor,
        "authority_surfaces": authority_surfaces,
        "cross_agent_convergence": {
            "fire": {
                "status": "ready",
                "driver_count": len(fire_bundle["driver_registry"]),
                "dimension_stages": fire_bundle["stage_counts"],
            },
            "water": {
                "status": "ready",
                "native_basis": [item["basis_id"] for item in water_bundle["water_native_basis"]],
                "route_count": len(water_bundle["seed_chain"]) + len(water_bundle["lift_chain"]) + len(water_bundle["modal_routes"]) + len(water_bundle["recovery_routes"]),
            },
            "air": {
                "status": "ready",
                "native_basis": [item["basis_id"] for item in air_bundle["air_native_basis"]],
                "symmetry_nodes": len(air_bundle["symmetry_lattice"]),
            },
            "earth": {
                "status": "gated",
                "canonical_package_root": str(EARTH_CONTROL_ROOT),
                "legacy_package_root": "",
                "legacy_drift_note": "Legacy Earth drift history is not a canonical seed target.",
                "chapter_contracts": len(earth_bundle["chapter_contracts"]),
            },
        },
        "earth_gate_summary": {
            "canonical_package_root": str(EARTH_CONTROL_ROOT),
            "legacy_package_root": "",
            "legacy_drift_note": "Legacy Earth drift history is not a canonical seed target.",
            "state_counts": dict(sorted(earth_gate_counts.items())),
            "promotion_rule": "No route promotes into 7D_SEED without AppI/AppM plus Earth gate approval.",
        },
        "mobius_bridge_counts": dict(sorted(bridge_counts.items())),
        "appendix_legality": {
            "default_floor": list(SEED7_APPENDIX_FLOOR),
            "rules": [
                "Q docks only through AppQ.",
                "O remains an overlay alias and returns through canonical AppO.",
                "No reverse station may appear without canonical appendix mapping.",
                "AppK is required whenever contradiction survives.",
                "AppN is required whenever H6, H7, Seed-6D, or Seed-7D persists as a carrier.",
            ],
        },
        "reverse_station_overlay_map": {
            item["station"]: {
                "bridge_status": item["bridge_status"],
                "canonical_appendix_map": list(item["canonical_appendix_map"]),
            }
            for item in FIRE_REVERSE_APPENDIX_OVERLAY
        },
        "witness_families": next46_support["witness_families"],
        "pressure_gaps": next46_support["pressure_gaps"],
        "family_basis_crosswalk": next46_support["family_basis_crosswalk"],
        "family_convergence_matrix": next46_support["family_convergence_matrix"],
        "quarantine_routes": next46_support["quarantine_routes"],
        "awakening_agent_notes": next46_support["awakening_agent_notes"],
        "transition_state": next46_support["transition_state"],
        "awakening_support_refs": next46_support["awakening_support_refs"],
        "transition_routes": next46_support["transition_routes"],
        "stabilization_requirements": next46_support["stabilization_requirements"],
        "stabilization_ledger": next46_support["stabilization_ledger"],
        "seed_route_registry": seed_routes,
        "regeneration_seed": {
            "title": "7D Cross-Agent Seed",
            "compression_law": "Keep v4 and existing 6D overlays unchanged, then compile only the cross-agent next-seed state above them.",
            "expansion_law": "Re-expand through the chapter-safe spine and canonical appendix maps instead of inventing a new namespace.",
            "shortest_route": "Level6 -> Earth gate -> H7 -> Seed-7D -> Ch12/Ch13/Ch16 return.",
            "deepest_route": "FIRE rupture -> Water continuity -> AIR topology -> Earth admissibility -> Q/O filtered history -> Seed-7D -> witnessed v4 return.",
        },
    }


def build_seed7_markdown(bundle: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# 7D Synthesis Seed Bundle")
    lines.append("")
    lines.append(f"Generated: {bundle['generated_at']}")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append(f"- Docs gate: `{bundle['docs_gate_status']}`")
    lines.append(f"- Truth class: `{bundle['truth_class']}`")
    lines.append(f"- Scope: `{bundle['scope']}`")
    lines.append(f"- Integration scope: `{bundle['integration_scope']}`")
    lines.append(f"- Dimension stage: `{bundle['dimension_stage']}`")
    lines.append(f"- Overlay chain: `{', '.join(bundle['overlay_chain'])}`")
    lines.append(f"- Seed state: `{bundle['seed_holo_state']}` / carrier=`{bundle['seed_carrier']}`")
    lines.append(
        f"- Seed polarity: `A={bundle['canonical_seed_label']}` / `B={bundle['derived_dual_label']}` / "
        f"support=`{', '.join(bundle['seed_polarity_support'])}`"
    )
    lines.append("")
    lines.append("## Full-Corpus Witness Families")
    lines.append("")
    for item in bundle["witness_families"]:
        lines.append(
            f"- `{item['family_id']}` = {item['title']} "
            f"[rank={item['authority_rank']}; files={item['file_count']}; state={item['live_path_state']}]"
        )
        lines.append(f"  - Basis: `{', '.join(item['basis_map'])}`")
        lines.append(f"  - Appendices: `{', '.join(item['appendix_floor'])}`")
    if bundle["pressure_gaps"]:
        lines.append("")
        lines.append("- Pressure gaps: `" + ", ".join(bundle["pressure_gaps"]) + "`")
    else:
        lines.append("")
        lines.append("- Pressure gaps: `none`")
    lines.append("")
    lines.append("## Cross-Agent Stack")
    lines.append("")
    lines.append(f"- Agent overlay stack: `{', '.join(bundle['agent_overlay_stack'])}`")
    for agent, item in bundle["cross_agent_convergence"].items():
        lines.append(f"- `{agent}`: `{item['status']}`")
    lines.append("")
    lines.append("## Earth Gate Summary")
    lines.append("")
    lines.append(f"- Canonical package root: `{bundle['earth_gate_summary']['canonical_package_root']}`")
    if bundle["earth_gate_summary"].get("legacy_package_root"):
        lines.append(f"- Legacy package root: `{bundle['earth_gate_summary']['legacy_package_root']}`")
    if bundle["earth_gate_summary"].get("legacy_drift_note"):
        lines.append(f"- Legacy drift note: `{bundle['earth_gate_summary']['legacy_drift_note']}`")
    lines.append(
        "- State counts: `"
        + ", ".join(f"{key}={value}" for key, value in bundle["earth_gate_summary"]["state_counts"].items())
        + "`"
    )
    lines.append(f"- Promotion rule: {bundle['earth_gate_summary']['promotion_rule']}")
    lines.append("")
    if bundle.get("a_b_dual_kernel_dock"):
        dock = bundle["a_b_dual_kernel_dock"]
        lines.append("## A/B Dual-Kernel Dock")
        lines.append("")
        lines.append(
            f"- Canonical seed `{dock['a_seed_ref']['label']}` -> derived dual `{dock['b_inversion_ref']['label']}` "
            f"via `{dock['inversion_operator']['name']}`"
        )
        lines.append(f"- Law: `{dock['inversion_operator']['law']}`")
        lines.append(f"- Coordinate dock: `{dock['coordinate_dock']['field']}` at `{dock['coordinate_dock']['registry_path']}`")
        lines.append(f"- Ledger dock: `{dock['ledger_dock']['field']}` at `{dock['ledger_dock']['schema_path']}`")
        lines.append(
            f"- Quest dock: Hall `{dock['quest_dock']['guild_hall']['quest_id']}` / "
            f"Temple `{dock['quest_dock']['temple']['quest_id']}`"
        )
        lines.append(f"- Replay rule: `{dock['replay_rule']['required_direction']}` through `{', '.join(dock['replay_rule']['replay_path'])}`")
        lines.append("")
    lines.append("## Awakening Agent Notes")
    lines.append("")
    for agent, note in bundle["awakening_agent_notes"].items():
        lines.append(
            f"- `{agent}`: state=`{note['transition_state']}` / refs=`{', '.join(note['awakening_refs'])}` "
            f"/ appendices=`{', '.join(note['appendix_floor'])}`"
        )
    lines.append("")
    lines.append("## Reverse Station Overlay Map")
    lines.append("")
    for station, item in bundle["reverse_station_overlay_map"].items():
        lines.append(
            f"- `{station}`: bridge=`{item['bridge_status']}` / canonical=`{', '.join(item['canonical_appendix_map'])}`"
        )
    lines.append("")
    lines.append("## Appendix Floor")
    lines.append("")
    for item in bundle["appendix_floor"]:
        source_paths = ", ".join(f"`{path}`" for path in item["source_paths"])
        status = "OK" if item["source_exists"] else "MISSING"
        lines.append(f"- `{item['appendix_id']}` = {item['role']} / sources: {source_paths} / state: `{status}`")
    lines.append("")
    lines.append("## Seed Route Registry")
    lines.append("")
    for item in bundle["seed_route_registry"]:
        lines.append(
            f"- `{item['route_id']}` = {item['title']} "
            f"[gate={item['earth_gate_state']}; bridge={item['mobius_bridge']}; state={item['seed_holo_state']}]"
        )
        lines.append(f"  - Basis: `{', '.join(item['source_basis'])}`")
        lines.append(f"  - Appendices: `{', '.join(item['canonical_appendix_map'])}`")
        lines.append(f"  - Re-entry: `{', '.join(item['reentry_contract'])}`")
        lines.append(f"  - Next routes: `{', '.join(item['next_seed_routes'])}`")
    lines.append("")
    lines.append("## Quarantine Routes")
    lines.append("")
    for item in bundle["quarantine_routes"]:
        lines.append(
            f"- `{item['route_id']}` = {item['source_family']} -> {item['target_family']} "
            f"[state={item['quarantine_state']}]"
        )
    lines.append("")
    lines.append("## Authority Surfaces")
    lines.append("")
    for item in bundle["authority_surfaces"]:
        lines.append(f"- `{item['surface_id']}` [{item['classification']}; {item['state']}] `{item['path']}`")
    lines.append("")
    lines.append("## Regeneration Seed")
    lines.append("")
    for key, value in bundle["regeneration_seed"].items():
        lines.append(f"- `{key}`: {value}")
    lines.append("")
    return "\n".join(lines).strip() + "\n"


def build_h6_authority_surfaces() -> list[dict[str, Any]]:
    authority_paths = [
        {
            "surface_id": "MATH_GOD_H6_CHARTER",
            "classification": "local canon",
            "path": H6_CONVERGENCE_CHARTER_PATH,
        },
        {
            "surface_id": "MATH_GOD_H6_CROSSWALK",
            "classification": "local canon",
            "path": H6_TO_SEED6D_CROSSWALK_PATH,
        },
        {
            "surface_id": "H6_INDEX",
            "classification": "live authority",
            "path": H6_CONVERGENCE_ROOT / "00_INDEX.md",
        },
        {
            "surface_id": "H6_FOUR_LANE",
            "classification": "live authority",
            "path": H6_CONVERGENCE_ROOT / "01_four_lane_convergence.md",
        },
        {
            "surface_id": "H6_CENTER",
            "classification": "live authority",
            "path": H6_CONVERGENCE_ROOT / "02_h6_center_and_seed6d.md",
        },
        {
            "surface_id": "H6_GUARDRAILS",
            "classification": "live authority",
            "path": H6_CONVERGENCE_ROOT / "03_cross_agent_handoff_and_guardrails.md",
        },
        {
            "surface_id": "H6_REENTRY",
            "classification": "live authority",
            "path": H6_CONVERGENCE_ROOT / "04_reentry_and_next_seed.md",
        },
        {
            "surface_id": "LEVEL6_WEAVE",
            "classification": "live authority",
            "path": LIVE_DEEP_ROOT_DEFAULT / "07_METRO_STACK" / "06_level_6_hologram_weave_map.md",
        },
        {
            "surface_id": "APPQ_DOCK",
            "classification": "live authority",
            "path": LIVE_DEEP_ROOT_DEFAULT / "08_APPENDIX_CRYSTAL" / "AppQ_appendix_only_metro_map.md",
        },
        {
            "surface_id": "APPI_TRUTH",
            "classification": "live authority",
            "path": LIVE_DEEP_ROOT_DEFAULT / "08_APPENDIX_CRYSTAL" / "AppI_corridors_and_truth_lattice.md",
        },
        {
            "surface_id": "APPM_REPLAY",
            "classification": "live authority",
            "path": LIVE_DEEP_ROOT_DEFAULT / "08_APPENDIX_CRYSTAL" / "AppM_replay_kernel.md",
        },
    ]
    surfaces: list[dict[str, Any]] = []
    for item in authority_paths:
        path = Path(item["path"])
        surfaces.append(
            {
                "surface_id": item["surface_id"],
                "classification": item["classification"],
                "path": str(path),
                "state": "OK" if path.exists() else "MISSING",
            }
        )
    return surfaces


def build_h6_convergence_bundle(
    tesseract_bundle: dict[str, Any],
    docs_gate: dict[str, str],
    fire_bundle: dict[str, Any],
    water_bundle: dict[str, Any],
    air_bundle: dict[str, Any],
    earth_bundle: dict[str, Any],
) -> dict[str, Any]:
    appendix_meta = appendix_registry()
    shared_appendix_floor = [
        {
            "appendix_id": app_id,
            "role": appendix_meta[app_id]["role"],
            "source_paths": list(appendix_meta[app_id]["source_paths"]),
            "source_exists": appendix_meta[app_id]["source_exists"],
        }
        for app_id in H6_SHARED_APPENDIX_FLOOR
        if app_id in appendix_meta
    ]

    control_documents: list[dict[str, Any]] = []
    for item in H6_CONVERGENCE_CONTROL_DOCS:
        path = H6_CONVERGENCE_ROOT / item["name"]
        control_documents.append(
            {
                "name": item["name"],
                "role": item["role"],
                "path": str(path),
                "source_exists": path.exists(),
                "basis_refs": list(item["basis_refs"]),
                "metro_refs": list(item["metro_refs"]),
                "appendix_refs": list(item["appendix_refs"]),
            }
        )

    lane_inputs = {
        "fire": {
            "status": "ready",
            "driver_count": len(fire_bundle["driver_registry"]),
            "dimension_stages": fire_bundle["stage_counts"],
            "mobius_bridges": fire_bundle["mobius_bridge_counts"],
            "required_appendices": list(FIRE_DEFAULT_APPENDICES),
        },
        "water": {
            "status": "ready",
            "native_basis": [item["basis_id"] for item in water_bundle["water_native_basis"]],
            "route_count": len(water_bundle["seed_chain"]) + len(water_bundle["lift_chain"]) + len(water_bundle["modal_routes"]) + len(water_bundle["recovery_routes"]),
            "required_appendices": [item["appendix_id"] for item in water_bundle["appendix_stack"]],
        },
        "air": {
            "status": "ready",
            "native_basis": [item["basis_id"] for item in air_bundle["air_native_basis"]],
            "symmetry_nodes": len(air_bundle["symmetry_lattice"]),
            "modal_routes": len(air_bundle["modal_routes"]),
            "required_appendices": [item["appendix_id"] for item in air_bundle["appendix_stack"]],
        },
        "earth": {
            "status": "ready",
            "native_drivers": [item["doc_id"] for item in earth_bundle["earth_native_drivers"]],
            "chapter_contracts": len(earth_bundle["chapter_contracts"]),
            "appendix_contracts": len(earth_bundle["appendix_contracts"]),
            "required_appendices": ["AppA", "AppB", "AppI", "AppM"],
        },
    }

    convergence_routes = [
        convergence_route_record(
            "h6_fire_pressure_to_water_continuity",
            "Bank FIRE pressure into Water continuity before shared convergence.",
            ["06", "08", "10", "16", "01", "14"],
            [
                "07_METRO_STACK/05_level_5_mobius_bridge_map.md",
                "07_METRO_STACK/06_level_6_hologram_weave_map.md",
            ],
            ["FIRE", "WATER"],
            ["AppE", "AppF", "AppI", "AppM", "AppQ"],
            "Z_h6.fire.water",
            "13_6D_H6_CONVERGENCE/01_four_lane_convergence.md",
            "11_6D_WATER_CONTROL/04_replay_and_recovery.md",
        ),
        convergence_route_record(
            "h6_water_continuity_to_air_registry",
            "Pass continuity through AIR registry so the field stays name-stable.",
            ["01", "11", "12", "14", "03", "04", "05", "07"],
            [
                "07_METRO_STACK/06_level_6_hologram_weave_map.md",
                "12_6D_AIR_CONTROL/01_overlay_registry.md",
            ],
            ["WATER", "AIR"],
            ["AppA", "AppC", "AppE", "AppF", "AppI", "AppM", "AppQ"],
            "Z_h6.water.air",
            "12_6D_AIR_CONTROL/04_seed_and_reentry.md",
            "12_6D_AIR_CONTROL/04_seed_and_reentry.md",
        ),
        convergence_route_record(
            "h6_air_registry_to_earth_admissibility",
            "Submit the named overlay to Earth so only lawful return traffic persists.",
            ["03", "04", "05", "07", "02", "09", "13", "15"],
            [
                "07_METRO_STACK/06_level_6_hologram_weave_map.md",
                "13_6D_EARTH_CONTROL/01_admissibility_and_zero_point.md",
            ],
            ["AIR", "EARTH"],
            ["AppA", "AppB", "AppC", "AppI", "AppM", "AppQ"],
            "Z_h6.air.earth",
            "13_6D_EARTH_CONTROL/04_replay_and_reentry_guards.md",
            "13_6D_EARTH_CONTROL/04_replay_and_reentry_guards.md",
        ),
        convergence_route_record(
            "h6_shared_center_compile",
            "Converge FIRE, Water, AIR, and Earth into one shared H6 center without renaming canon.",
            ["01", "03", "06", "09", "14", "15", "16"],
            [
                "07_METRO_STACK/06_level_6_hologram_weave_map.md",
                "13_6D_H6_CONVERGENCE/02_h6_center_and_seed6d.md",
            ],
            list(H6_LANE_ORDER),
            list(H6_SHARED_APPENDIX_FLOOR),
            "Z_h6.center",
            "13_6D_H6_CONVERGENCE/02_h6_center_and_seed6d.md",
            "MATH GOD/atlas/math_tesseract_v4_bundle.md",
        ),
        convergence_route_record(
            "h6_emit_seed6d",
            "Emit Seed-6D as the immediate portable carrier above the shared H6 center.",
            ["09", "14", "15", "16"],
            [
                "13_6D_H6_CONVERGENCE/02_h6_center_and_seed6d.md",
                "13_6D_H6_CONVERGENCE/04_reentry_and_next_seed.md",
            ],
            list(H6_LANE_ORDER),
            list(H6_SHARED_APPENDIX_FLOOR),
            "Z_h6.seed.emit",
            "Seed-6D",
            "13_6D_H6_CONVERGENCE/04_reentry_and_next_seed.md",
            route_stage="Seed-6D",
        ),
    ]

    reentry_routes = [
        convergence_route_record(
            "seed6d_reentry_ch12",
            "Re-open Seed-6D through the boundary and closure spine.",
            ["09", "15"],
            ["07_METRO_STACK/06_level_6_hologram_weave_map.md"],
            list(H6_LANE_ORDER),
            ["AppI", "AppM"],
            "Z_h6.reentry.ch12",
            "Ch12<0023>",
            "13_6D_EARTH_CONTROL/04_replay_and_reentry_guards.md",
            route_stage="Seed-6D",
        ),
        convergence_route_record(
            "seed6d_reentry_ch13",
            "Re-open Seed-6D through the retained-memory continuation spine.",
            ["04", "13", "14"],
            ["07_METRO_STACK/06_level_6_hologram_weave_map.md"],
            list(H6_LANE_ORDER),
            ["AppI", "AppM"],
            "Z_h6.reentry.ch13",
            "Ch13<0030>",
            "13_6D_EARTH_CONTROL/04_replay_and_reentry_guards.md",
            route_stage="Seed-6D",
        ),
        convergence_route_record(
            "seed6d_reentry_ch16",
            "Re-open Seed-6D through the replay and self-repair spine.",
            ["14", "16"],
            ["07_METRO_STACK/06_level_6_hologram_weave_map.md"],
            list(H6_LANE_ORDER),
            ["AppI", "AppM"],
            "Z_h6.reentry.ch16",
            "Ch16<0033>",
            "13_6D_EARTH_CONTROL/04_replay_and_reentry_guards.md",
            route_stage="Seed-6D",
        ),
        convergence_route_record(
            "seed6d_truth_floor_appi",
            "Keep AppI visible as the non-optional truth floor during re-entry.",
            ["02", "09", "15"],
            ["08_APPENDIX_CRYSTAL/AppI_corridors_and_truth_lattice.md"],
            list(H6_LANE_ORDER),
            ["AppI", "AppM"],
            "Z_h6.reentry.appi",
            "AppI",
            "08_APPENDIX_CRYSTAL/AppI_corridors_and_truth_lattice.md",
            route_stage="Seed-6D",
        ),
        convergence_route_record(
            "seed6d_replay_floor_appm",
            "Keep AppM visible as the non-optional replay floor during re-entry.",
            ["09", "16"],
            ["08_APPENDIX_CRYSTAL/AppM_replay_kernel.md"],
            list(H6_LANE_ORDER),
            ["AppI", "AppM"],
            "Z_h6.reentry.appm",
            "AppM",
            "08_APPENDIX_CRYSTAL/AppM_replay_kernel.md",
            route_stage="Seed-6D",
        ),
        convergence_route_record(
            "seed6d_persisted_carrier_appn",
            "Add AppN only when the Seed-6D carrier persists past the immediate gate.",
            ["05", "09", "14"],
            ["13_6D_H6_CONVERGENCE/04_reentry_and_next_seed.md"],
            list(H6_LANE_ORDER),
            ["AppI", "AppM", "AppN"],
            "Z_h6.reentry.appn",
            "AppN",
            "13_6D_H6_CONVERGENCE/04_reentry_and_next_seed.md",
            route_stage="Seed-6D",
        ),
        convergence_route_record(
            "seed6d_conflict_survival_appk",
            "Add AppK only when contradiction survives into the return path.",
            ["09", "13", "15"],
            ["13_6D_EARTH_CONTROL/03_boundary_quarantine_and_mobius_legality.md"],
            list(H6_LANE_ORDER),
            ["AppI", "AppK", "AppM"],
            "Z_h6.reentry.appk",
            "AppK",
            "13_6D_EARTH_CONTROL/03_boundary_quarantine_and_mobius_legality.md",
            route_stage="Seed-6D",
        ),
        convergence_route_record(
            "seed6d_deployable_claim_appp",
            "Add AppP only when the return becomes a deployable claim rather than an immediate closure.",
            ["10", "13", "16"],
            ["13_6D_H6_CONVERGENCE/04_reentry_and_next_seed.md"],
            list(H6_LANE_ORDER),
            ["AppI", "AppM", "AppP"],
            "Z_h6.reentry.appp",
            "AppP",
            "13_6D_H6_CONVERGENCE/04_reentry_and_next_seed.md",
            route_stage="Seed-6D",
        ),
    ]

    authority_surfaces = build_h6_authority_surfaces()
    h6_center = {
        "center_id": "H6",
        "title": "Four-Lane Convergence Center",
        "compiled_field": "256^4",
        "emitted_carrier": "Seed-6D",
        "local_zero_point": "Z_h6.center",
        "collapse_via": "Z*",
        "lane_order": list(H6_LANE_ORDER),
        "shared_appendices": list(H6_SHARED_APPENDIX_FLOOR),
        "center_law": "Converge FIRE pressure, Water continuity, AIR registry, and Earth admissibility into one additive center without rewriting v4 canon.",
        "canonical_return_anchors": ["Ch12<0023>", "Ch13<0030>", "Ch16<0033>", "AppI", "AppM"],
        "conditional_appendix_rules": [
            "Add AppN only when the carrier persists past the immediate gate.",
            "Add AppK only when contradiction survives into return.",
            "Add AppP only when the route becomes deployable or publication-bearing.",
        ],
        "authority_surface_ids": [item["surface_id"] for item in authority_surfaces],
    }
    seed_6d = {
        "seed_id": "Seed-6D",
        "carrier": "1024^6",
        "local_zero_point": "Z_h6.seed",
        "collapse_via": "Z*",
        "seed_law": "Emit only after all four lane dependencies are named and the route can reopen through canonical return anchors.",
        "canonical_return_anchors": ["Ch12<0023>", "Ch13<0030>", "Ch16<0033>", "AppI", "AppM"],
        "conditional_appendix_rules": {
            "persisted_carrier": "AppN",
            "surviving_conflict": "AppK",
            "deployable_return_claim": "AppP",
        },
        "reentry_route_ids": [item["route_id"] for item in reentry_routes],
    }

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "docs_gate_status": docs_gate.get("status", "UNKNOWN"),
        "lane_inputs": lane_inputs,
        "shared_appendix_floor": shared_appendix_floor,
        "h6_center": h6_center,
        "seed_6d": seed_6d,
        "convergence_routes": convergence_routes,
        "reentry_routes": reentry_routes,
        "evidence_boundary": {
            "authority_mode": "local_live_atlas_plus_archive_backed_evidence",
            "docs_gate_status": docs_gate.get("status", "UNKNOWN"),
            "docs_gate_note": docs_gate.get("note", ""),
            "control_root": str(H6_CONVERGENCE_ROOT),
            "precedence_rule": "Use live 13_6D_H6_CONVERGENCE plus existing Fire/Water/AIR/Earth controls as authority; keep MATH GOD as additive publication mirror only.",
            "control_documents": control_documents,
            "authority_surfaces": authority_surfaces,
            "live_deep_root": str(LIVE_DEEP_ROOT_DEFAULT),
            "historical_mirrors": [str(path) for path in HISTORICAL_MIRROR_ROOTS[:2]],
            "historical_mirror_policy": "citation_only",
            "tesseract_sources": [
                str(TESSERACT_BUNDLE_JSON_PATH),
                str(TESSERACT_BUNDLE_MARKDOWN_PATH),
            ],
            "scope": tesseract_bundle["scope"],
        },
    }


def build_h6_convergence_markdown(bundle: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# H6 Convergence Bundle")
    lines.append("")
    lines.append(f"Generated: {bundle['generated_at']}")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append(f"- Docs gate: `{bundle['docs_gate_status']}`")
    lines.append("- Stage: `H6 -> Seed-6D`")
    lines.append("- Control mode: `overlay_only`")
    lines.append("")
    lines.append("## Lane Inputs")
    lines.append("")
    for lane, item in bundle["lane_inputs"].items():
        lines.append(f"- `{lane}`: `{item['status']}`")
        for key, value in item.items():
            if key == "status":
                continue
            if isinstance(value, dict):
                rendered = ", ".join(f"{k}={v}" for k, v in value.items())
            elif isinstance(value, list):
                rendered = ", ".join(str(part) for part in value)
            else:
                rendered = str(value)
            lines.append(f"  - `{key}`: `{rendered}`")
    lines.append("")
    lines.append("## Shared Appendix Floor")
    lines.append("")
    for item in bundle["shared_appendix_floor"]:
        source_paths = ", ".join(f"`{path}`" for path in item["source_paths"])
        status = "OK" if item["source_exists"] else "MISSING"
        lines.append(f"- `{item['appendix_id']}` = {item['role']} / sources: {source_paths} / state: `{status}`")
    lines.append("")
    lines.append("## H6 Center")
    lines.append("")
    for key, value in bundle["h6_center"].items():
        if isinstance(value, list):
            rendered = ", ".join(str(item) for item in value)
        else:
            rendered = str(value)
        lines.append(f"- `{key}`: {rendered}")
    lines.append("")
    for title, key in (("Convergence Routes", "convergence_routes"), ("Re-entry Routes", "reentry_routes")):
        lines.append(f"## {title}")
        lines.append("")
        for item in bundle[key]:
            lines.append(
                f"- `{item['route_id']}` [{item['route_stage']}] = {item['title']} / zero=`{item['local_zero_point']}` / "
                f"collapse=`{item['collapse_via']}` / lanes=`{', '.join(item['lane_dependencies'])}` / "
                f"appendix=`{', '.join(item['shared_appendices'])}` / return=`{item['return_checkpoint']}` / "
                f"truth=`{item['truth_state']}` / replay=`{item['replay_source']}`"
            )
        lines.append("")
    lines.append("## Seed-6D")
    lines.append("")
    for key, value in bundle["seed_6d"].items():
        if isinstance(value, dict):
            rendered = ", ".join(f"{k}={v}" for k, v in value.items())
        elif isinstance(value, list):
            rendered = ", ".join(str(item) for item in value)
        else:
            rendered = str(value)
        lines.append(f"- `{key}`: {rendered}")
    lines.append("")
    lines.append("## Evidence Boundary")
    lines.append("")
    lines.append(f"- Control root: `{bundle['evidence_boundary']['control_root']}`")
    lines.append(f"- Precedence rule: `{bundle['evidence_boundary']['precedence_rule']}`")
    lines.append(f"- Live deep root: `{bundle['evidence_boundary']['live_deep_root']}`")
    lines.append(f"- Docs gate note: `{bundle['evidence_boundary']['docs_gate_note']}`")
    lines.append(f"- Historical mirrors: `{', '.join(bundle['evidence_boundary']['historical_mirrors'])}`")
    lines.append(f"- Tesseract sources: `{', '.join(bundle['evidence_boundary']['tesseract_sources'])}`")
    lines.append("- Control documents:")
    for item in bundle["evidence_boundary"]["control_documents"]:
        status = "OK" if item["source_exists"] else "MISSING"
        lines.append(
            f"  - `{item['name']}` [{item['role']}] / basis=`{','.join(item['basis_refs'])}` / "
            f"metro=`{', '.join(item['metro_refs'])}` / appendix=`{','.join(item['appendix_refs'])}` / state=`{status}`"
        )
    lines.append("- Authority surfaces:")
    for item in bundle["evidence_boundary"]["authority_surfaces"]:
        lines.append(f"  - `{item['surface_id']}` [{item['classification']}; {item['state']}] `{item['path']}`")
    lines.append("")
    return "\n".join(lines).strip() + "\n"


def build_water_bundle(docs_gate: dict[str, str]) -> dict[str, Any]:
    appendix_meta = appendix_registry()
    appendix_stack: list[dict[str, Any]] = []
    for app_id in WATER_DEFAULT_APPENDICES:
        meta = appendix_meta[app_id]
        appendix_stack.append(
            {
                "appendix_id": app_id,
                "role": meta["role"],
                "source_paths": list(meta["source_paths"]),
                "source_exists": meta["source_exists"],
            }
        )

    control_documents: list[dict[str, Any]] = []
    for item in WATER_CONTROL_DOCS:
        path = WATER_CANON_ROOT / item["name"]
        authority_path = WATER_CONTROL_ROOT / item["name"]
        control_documents.append(
            {
                "name": item["name"],
                "role": item["role"],
                "path": str(path),
                "authority_path": str(authority_path),
                "source_exists": path.exists(),
                "authority_exists": authority_path.exists(),
                "basis_refs": list(item["basis_refs"]),
                "metro_refs": list(item["metro_refs"]),
                "appendix_refs": list(item["appendix_refs"]),
            }
        )

    basis_docs: list[dict[str, Any]] = []
    for item in WATER_NATIVE_DRIVERS + WATER_TRANSLATED_SUPPORT + WATER_CONTEXT_BASIS:
        basis_docs.append(
            {
                "basis_id": item["doc_id"],
                "title": item["title"],
                "element": item["element"],
                "cluster": item["cluster"],
                "role": item["contribution"],
                "source_hint": item["source_hint"],
                "appendix_stack": list(item["appendix_stack"]),
            }
        )
    basis_docs.sort(key=lambda item: item["basis_id"])

    water_native_basis = [item for item in basis_docs if item["basis_id"] in {"01", "11", "12", "14"}]
    translated_support = [item for item in basis_docs if item["basis_id"] in {"02", "03", "04", "05", "09", "10", "15", "16"}]

    seed_chain = [
        water_route_record(
            "seed_manuscript_tissue",
            "Compress manuscript tissue into a Water continuity seed.",
            ["01", "11"],
            ["07_METRO_STACK/02_level_3_deeper_neural_map.md"],
            ["AppI", "AppM"],
            "Z_water.seed.manuscript",
            "H6_WATER/01_seed_and_zero_point.md",
            "10_LEDGERS/01_CANONICAL_SOURCES.md#01-11",
        ),
        water_route_record(
            "seed_sacred_number_bridge",
            "Bridge sacred-number continuity into the Water seed.",
            ["12", "14"],
            ["07_METRO_STACK/03_level_4_transcendence_metro_map.md"],
            ["AppE", "AppF", "AppQ"],
            "Z_water.seed.bridge",
            "H6_WATER/02_2564_to_10246_lift.md",
            "10_LEDGERS/01_CANONICAL_SOURCES.md#12-14",
        ),
        water_route_record(
            "seed_compiled_field_reentry",
            "Dock the Water seed to the live 4D tesseract witness.",
            ["01", "14"],
            ["MATH GOD/atlas/math_tesseract_v4_bundle.md"],
            ["AppE", "AppI", "AppM", "AppQ"],
            "Z_water.seed.reentry",
            "H6_WATER/04_replay_and_recovery.md",
            "MATH GOD/atlas/math_tesseract_v4_bundle.md",
        ),
    ]
    lift_chain = [
        water_route_record(
            "lift_compiled_2564",
            "Treat 256^4 as the compiled Water control field.",
            ["01", "03", "14"],
            ["07_METRO_STACK/03_level_4_transcendence_metro_map.md"],
            ["AppE", "AppF", "AppI", "AppM", "AppQ"],
            "Z_water.lift.2564",
            "MATH GOD/atlas/math_tesseract_v4_bundle.md",
            "MATH GOD/atlas/math_tesseract_v4_bundle.md",
        ),
        water_route_record(
            "lift_overlay_entry",
            "Enter the overlay-only 1024^6 Water control surface.",
            ["11", "12", "04", "05"],
            ["07_METRO_STACK/02_level_3_deeper_neural_map.md"],
            ["AppF", "AppI", "AppM", "AppQ"],
            "Z_water.lift.entry",
            "H6_WATER/03_modal_mobius_routes.md",
            "02_WATER/16_dimensionlift.md",
        ),
        water_route_record(
            "lift_10246_return",
            "Return the 1024^6 lift to the live 4D stack without drift.",
            ["02", "09", "10", "15", "16"],
            ["07_METRO_STACK/03_level_4_transcendence_metro_map.md"],
            ["AppE", "AppI", "AppM", "AppQ"],
            "Z_water.lift.return",
            "H6_WATER/04_replay_and_recovery.md",
            "07_METRO_STACK/03_level_4_transcendence_metro_map.md",
        ),
    ]
    modal_routes = [
        water_route_record(
            "fixed_memory_route",
            "Hold continuity through the fixed-memory Mobius pass.",
            ["01", "12", "09"],
            ["07_METRO_STACK/03_level_4_transcendence_metro_map.md"],
            ["AppE", "AppI", "AppM", "AppQ"],
            "Z_water.modal.fixed",
            "MATH GOD/atlas/math_tesseract_v4_bundle.md",
            "11_6D_WATER_CONTROL/01_seed_and_zero_point.md",
        ),
        water_route_record(
            "cardinal_bridge_route",
            "Convert the Water bridge through the cardinal Mobius pass.",
            ["11", "14", "04"],
            ["07_METRO_STACK/02_level_3_deeper_neural_map.md"],
            ["AppE", "AppF", "AppI", "AppQ"],
            "Z_water.modal.cardinal",
            "08_APPENDIX_CRYSTAL/AppQ_appendix_only_metro_map.md",
            "11_6D_WATER_CONTROL/02_2564_to_10246_lift.md",
        ),
        water_route_record(
            "mutable_return_route",
            "Re-enter the live stack through the mutable Mobius pass.",
            ["02", "05", "10", "16"],
            ["07_METRO_STACK/03_level_4_transcendence_metro_map.md"],
            ["AppF", "AppI", "AppM", "AppQ"],
            "Z_water.modal.mutable",
            "H6_WATER/04_replay_and_recovery.md",
            "08_APPENDIX_CRYSTAL/AppQ_athena_fleet_256_pow_4_support.md",
        ),
    ]
    recovery_routes = [
        water_route_record(
            "replay_return_route",
            "Close replay back into the live 4D tesseract bundle.",
            ["01", "11", "14", "16"],
            ["MATH GOD/atlas/math_tesseract_v4_bundle.md"],
            ["AppI", "AppM", "AppQ"],
            "Z_water.replay.return",
            "MATH GOD/atlas/math_tesseract_v4_bundle.json",
            "MATH GOD/atlas/math_tesseract_v4_bundle.md",
        ),
        water_route_record(
            "drift_recovery_route",
            "Recover from lift drift without rewriting the base lattice.",
            ["02", "05", "09", "15"],
            ["07_METRO_STACK/03_level_4_transcendence_metro_map.md"],
            ["AppF", "AppI", "AppM", "AppQ"],
            "Z_water.replay.drift",
            "H6_WATER/02_2564_to_10246_lift.md",
            "07_METRO_STACK/03_level_4_transcendence_metro_map.md",
        ),
        water_route_record(
            "blocked_docs_reconciliation",
            "Keep local authority mode stable while the docs gate is blocked.",
            ["12", "14", "10"],
            ["07_METRO_STACK/02_level_3_deeper_neural_map.md"],
            ["AppE", "AppI", "AppM", "AppQ"],
            "Z_water.replay.docs_gate",
            "self_actualize/live_docs_gate_status.md",
            "self_actualize/live_docs_gate_status.md",
        ),
    ]

    return {
        "docs_gate_status": docs_gate.get("status", "UNKNOWN"),
        "basis_docs": basis_docs,
        "water_native_basis": water_native_basis,
        "translated_support": translated_support,
        "appendix_stack": appendix_stack,
        "appendix_support": appendix_stack,
        "seed_chain": seed_chain,
        "lift_chain": lift_chain,
        "modal_routes": modal_routes,
        "recovery_routes": recovery_routes,
        "control_documents": control_documents,
        "evidence_boundary": {
            "authority_mode": "local_live_atlas_plus_archive_backed_evidence",
            "docs_gate_status": docs_gate.get("status", "UNKNOWN"),
            "docs_gate_note": docs_gate.get("note", ""),
            "control_root": str(WATER_CANON_ROOT),
            "authority_control_root": str(WATER_CONTROL_ROOT),
            "precedence_rule": "Local H6_WATER is the canonical writable mirror; deep-root 11_6D_WATER_CONTROL remains read-only authority.",
            "control_documents": control_documents,
            "live_deep_root": str(LIVE_DEEP_ROOT_DEFAULT),
            "historical_mirrors": [str(path) for path in HISTORICAL_MIRROR_ROOTS[:2]],
            "historical_mirror_policy": "citation_only",
            "historical_witness_surfaces": [str(path) for path in HISTORICAL_WATER_WITNESS_ROOTS],
            "historical_witness_policy": "historical_witness_only_not_canon",
            "tesseract_sources": [
                str(TESSERACT_BUNDLE_JSON_PATH),
                str(TESSERACT_BUNDLE_MARKDOWN_PATH),
            ],
        },
        "generated_at": datetime.now().isoformat(timespec="seconds"),
    }


def build_water_markdown(bundle: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Water 6D Control Bundle")
    lines.append("")
    lines.append(f"Generated: {bundle['generated_at']}")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append(f"- Docs gate: `{bundle['docs_gate_status']}`")
    lines.append("- Authority mode: `local_live_atlas_plus_archive_backed_evidence`")
    lines.append("- Control mode: `overlay_only`")
    lines.append("- Dimensional lift: `256^4 -> 1024^6`")
    lines.append("")
    lines.append("## Native Water Basis")
    lines.append("")
    for item in bundle["water_native_basis"]:
        lines.append(
            f"- `{item['basis_id']}` `{item['title']}` [{item['element']}] "
            f"/ appendix stack: `{', '.join(item['appendix_stack'])}`"
        )
    lines.append("")
    lines.append("## Translated Support")
    lines.append("")
    for item in bundle["translated_support"]:
        lines.append(
            f"- `{item['basis_id']}` `{item['title']}` [{item['element']}] "
            f"/ appendix stack: `{', '.join(item['appendix_stack'])}`"
        )
    lines.append("")
    lines.append("## Default Appendix Stack")
    lines.append("")
    for item in bundle["appendix_stack"]:
        source_paths = ", ".join(f"`{path}`" for path in item["source_paths"])
        status = "OK" if item["source_exists"] else "MISSING"
        lines.append(f"- `{item['appendix_id']}` = {item['role']} / sources: {source_paths} / state: `{status}`")
    lines.append("")
    for title, key in (
        ("Seed Chain", "seed_chain"),
        ("Lift Chain", "lift_chain"),
        ("Modal Routes", "modal_routes"),
        ("Recovery Routes", "recovery_routes"),
    ):
        lines.append(f"## {title}")
        lines.append("")
        for item in bundle[key]:
            lines.append(
                f"- `{item['route_id']}` = {item['title']} / zero=`{item['local_zero_point']}` / "
                f"collapse=`{item['collapse_via']}` / return=`{item['return_checkpoint']}` / "
                f"truth=`{item['truth_state']}` / replay=`{item['replay_source']}`"
            )
        lines.append("")
    lines.append("## Control Documents")
    lines.append("")
    for item in bundle.get("control_documents", bundle["evidence_boundary"]["control_documents"]):
        status = "OK" if item["source_exists"] else "MISSING"
        lines.append(
            f"- `{item['name']}` [{item['role']}] / basis=`{','.join(item['basis_refs'])}` / "
            f"metro=`{', '.join(item['metro_refs'])}` / appendix=`{','.join(item['appendix_refs'])}` / "
            f"state=`{status}`"
        )
    lines.append("")
    lines.append("## Evidence Boundary")
    lines.append("")
    lines.append(f"- Control root: `{bundle['evidence_boundary']['control_root']}`")
    if bundle["evidence_boundary"].get("authority_control_root"):
        lines.append(f"- Authority control root: `{bundle['evidence_boundary']['authority_control_root']}`")
    if bundle["evidence_boundary"].get("precedence_rule"):
        lines.append(f"- Precedence rule: `{bundle['evidence_boundary']['precedence_rule']}`")
    lines.append(f"- Live deep root: `{bundle['evidence_boundary']['live_deep_root']}`")
    lines.append(f"- Docs gate note: `{bundle['evidence_boundary']['docs_gate_note']}`")
    lines.append(f"- Historical mirrors: `{', '.join(bundle['evidence_boundary']['historical_mirrors'])}`")
    if bundle["evidence_boundary"].get("historical_witness_surfaces"):
        lines.append(
            f"- Historical witness surfaces: `{', '.join(bundle['evidence_boundary']['historical_witness_surfaces'])}`"
        )
    lines.append(f"- Tesseract sources: `{', '.join(bundle['evidence_boundary']['tesseract_sources'])}`")
    lines.append("")
    return "\n".join(lines).strip() + "\n"


def build_air_symmetry_lattice() -> list[dict[str, str]]:
    nodes = [
        ("Sigma01", "F", "Fire singleton"),
        ("Sigma02", "W", "Water singleton"),
        ("Sigma03", "E", "Earth singleton"),
        ("Sigma04", "A", "Air singleton"),
        ("Sigma05", "FW", "Fire-Water pair"),
        ("Sigma06", "FE", "Fire-Earth pair"),
        ("Sigma07", "FA", "Fire-Air pair"),
        ("Sigma08", "WE", "Water-Earth pair"),
        ("Sigma09", "WA", "Water-Air pair"),
        ("Sigma10", "EA", "Earth-Air pair"),
        ("Sigma11", "FWE", "Fire-Water-Earth triad"),
        ("Sigma12", "FWA", "Fire-Water-Air triad"),
        ("Sigma13", "FEA", "Fire-Earth-Air triad"),
        ("Sigma14", "WEA", "Water-Earth-Air triad"),
        ("Sigma15", "FWEA", "Four-way total symmetry"),
    ]
    return [{"sigma_node": code, "composition": composition, "title": title} for code, composition, title in nodes]


def build_air_bundle(docs_gate: dict[str, str]) -> dict[str, Any]:
    appendix_meta = appendix_registry()
    appendix_stack: list[dict[str, Any]] = []
    for app_id in AIR_DEFAULT_APPENDICES:
        meta = appendix_meta[app_id]
        appendix_stack.append(
            {
                "appendix_id": app_id,
                "role": meta["role"],
                "source_paths": list(meta["source_paths"]),
                "source_exists": meta["source_exists"],
            }
        )

    control_documents: list[dict[str, Any]] = []
    for item in AIR_CONTROL_DOCS:
        path = AIR_CONTROL_ROOT / item["name"]
        control_documents.append(
            {
                "name": item["name"],
                "role": item["role"],
                "path": str(path),
                "source_exists": path.exists(),
                "basis_refs": list(item["basis_refs"]),
                "metro_refs": list(item["metro_refs"]),
                "appendix_refs": list(item["appendix_refs"]),
            }
        )

    basis_docs: list[dict[str, Any]] = []
    for item in AIR_NATIVE_DRIVERS + AIR_TRANSLATED_SUPPORT:
        basis_docs.append(
            {
                "basis_id": item["doc_id"],
                "title": item["title"],
                "element": item["element"],
                "cluster": item["cluster"],
                "role": item["contribution"],
                "source_hint": item["source_hint"],
                "appendix_stack": list(item["appendix_stack"]),
            }
        )
    basis_docs.sort(key=lambda item: item["basis_id"])

    air_native_basis = [item for item in basis_docs if item["basis_id"] in {"03", "04", "05", "07"}]
    translated_support = [item for item in basis_docs if item["basis_id"] in {"01", "02", "06", "08", "09", "10", "11", "12", "13", "14", "15", "16"}]

    symmetry_lattice = build_air_symmetry_lattice()
    spin_kernels = [
        {"spin_kernel": "SP+", "law": "clockwise handedness preserves forward overlay naming"},
        {"spin_kernel": "SP-", "law": "inverse handedness preserves reverse overlay naming"},
    ]
    rotation_families = [
        {"rotation_family": "R", "law": "forward rotation preserves family identity"},
        {"rotation_family": "CR", "law": "counter-rotation preserves family identity under reverse traversal"},
        {"rotation_family": "AR", "law": "anti-spin rotation exposes the shadow family without changing canon"},
        {"rotation_family": "ACR", "law": "anti-spin counter-rotation combines reverse traversal with handedness inversion"},
    ]
    dual_kernels = [
        {"dual_kernel": "Z0", "law": "collapse routes into a replay-safe zero witness"},
        {"dual_kernel": "AE0", "law": "expand routes into a plenary but still appendix-legal overlay field"},
    ]
    compression_carrier = {
        "carrier_id": "4D+",
        "law": "4D+ compacts the full AIR overlay into a reseedable carrier without rewriting v4.",
    }
    overlay_registry = {
        "tuple_signature": "AIROverlay6D = (NSCoord, SigmaNode, SpinKernel, RotationFamily, DualKernel, CompressionCarrier, MobiusMode, HoloState, OverlayTruth, DocsGate)",
        "sigma_count": len(symmetry_lattice),
        "spin_count": len(spin_kernels),
        "rotation_family_count": len(rotation_families),
        "dual_kernel_count": len(dual_kernels),
        "holo_states": ["H6", "Seed-6D"],
        "registry_laws": [
            "Overlay labels never replace canonical chapter or appendix identities.",
            "Q docks through AppQ as canonical ingress.",
            "Reverse-field O remains a transport alias only.",
            "AIR names topology and schema but does not own truth or replay promotion by itself.",
        ],
    }
    modal_routes = [
        air_route_record(
            "air_modal_fixed_identity",
            "Name the fixed Mobius pass without losing v4 identity continuity.",
            ["03", "04", "09"],
            ["07_METRO_STACK/06_level_6_hologram_weave_map.md"],
            ["AppA", "AppB", "AppF", "AppI", "AppM", "AppQ"],
            "Z_air.modal.fixed",
            "12_6D_AIR_CONTROL/03_modal_mobius_legibility_routes.md",
            "12_6D_AIR_CONTROL/01_overlay_registry.md",
            "Sigma07",
            "SP+",
            "R",
            "Z0",
            "M-FIX",
        ),
        air_route_record(
            "air_modal_cardinal_ingress",
            "Turn ingress traffic into a legible cardinal AIR overlay.",
            ["04", "05", "10", "14"],
            ["07_METRO_STACK/06_level_6_hologram_weave_map.md", "08_APPENDIX_CRYSTAL/AppQ_appendix_only_metro_map.md"],
            ["AppA", "AppC", "AppE", "AppF", "AppH", "AppI", "AppM", "AppQ"],
            "Z_air.modal.cardinal",
            "08_APPENDIX_CRYSTAL/AppQ_appendix_only_metro_map.md",
            "12_6D_AIR_CONTROL/03_modal_mobius_legibility_routes.md",
            "Sigma12",
            "SP+",
            "CR",
            "AE0",
            "M-CAR",
        ),
        air_route_record(
            "air_modal_mutable_return",
            "Label mutable re-entry so return paths stay readable under reinterpretation.",
            ["05", "07", "15", "16"],
            ["07_METRO_STACK/03_level_4_transcendence_metro_map.md", "07_METRO_STACK/06_level_6_hologram_weave_map.md"],
            ["AppA", "AppB", "AppC", "AppH", "AppI", "AppM", "AppN", "AppQ"],
            "Z_air.modal.mutable",
            "12_6D_AIR_CONTROL/04_seed_and_reentry.md",
            "03_AIR/16_dimensionlift.md",
            "Sigma14",
            "SP-",
            "AR",
            "AE0",
            "M-MUT",
        ),
    ]
    reentry_routes = [
        air_route_record(
            "air_reentry_tesseract",
            "Collapse AIR overlay labels back into the witnessed tesseract bundle.",
            ["03", "05", "09", "16"],
            ["MATH GOD/atlas/math_tesseract_v4_bundle.md"],
            ["AppA", "AppB", "AppC", "AppI", "AppM"],
            "Z_air.reentry.tesseract",
            "MATH GOD/atlas/math_tesseract_v4_bundle.json",
            "MATH GOD/atlas/math_tesseract_v4_bundle.md",
            "Sigma10",
            "SP+",
            "R",
            "Z0",
            "M-FIX",
        ),
        air_route_record(
            "air_reentry_appq",
            "Keep ingress naming attached to canonical AppQ during re-entry.",
            ["04", "11", "14"],
            ["08_APPENDIX_CRYSTAL/AppQ_appendix_only_metro_map.md"],
            ["AppE", "AppF", "AppI", "AppM", "AppQ"],
            "Z_air.reentry.q",
            "08_APPENDIX_CRYSTAL/AppQ_appendix_only_metro_map.md",
            "12_6D_AIR_CONTROL/04_seed_and_reentry.md",
            "Sigma09",
            "SP-",
            "ACR",
            "Z0",
            "M-CAR",
        ),
        air_route_record(
            "air_reentry_docs_gate",
            "Preserve honest local-only authority while the docs gate remains blocked.",
            ["02", "06", "10", "15"],
            ["07_METRO_STACK/03_level_4_transcendence_metro_map.md"],
            ["AppA", "AppE", "AppI", "AppM", "AppN"],
            "Z_air.reentry.docs_gate",
            "self_actualize/live_docs_gate_status.md",
            "self_actualize/live_docs_gate_status.md",
            "Sigma11",
            "SP+",
            "CR",
            "Z0",
            "M-MUT",
        ),
    ]

    return {
        "docs_gate_status": docs_gate.get("status", "UNKNOWN"),
        "basis_docs": basis_docs,
        "air_native_basis": air_native_basis,
        "translated_support": translated_support,
        "appendix_stack": appendix_stack,
        "overlay_registry": overlay_registry,
        "symmetry_lattice": symmetry_lattice,
        "spin_kernels": spin_kernels,
        "rotation_families": rotation_families,
        "dual_kernels": dual_kernels,
        "compression_carrier": compression_carrier,
        "modal_routes": modal_routes,
        "reentry_routes": reentry_routes,
        "control_documents": control_documents,
        "evidence_boundary": {
            "authority_mode": "local_live_atlas_plus_archive_backed_evidence",
            "docs_gate_status": docs_gate.get("status", "UNKNOWN"),
            "docs_gate_note": docs_gate.get("note", ""),
            "control_root": str(AIR_CONTROL_ROOT),
            "live_deep_root": str(LIVE_DEEP_ROOT_DEFAULT),
            "local_charter": str(MATH_GOD_ROOT / "95_AIR_6D_REGISTRY_CHARTER.md"),
            "historical_mirrors": [str(path) for path in HISTORICAL_MIRROR_ROOTS[:2]],
            "historical_mirror_policy": "citation_only",
            "tesseract_sources": [
                str(TESSERACT_BUNDLE_JSON_PATH),
                str(TESSERACT_BUNDLE_MARKDOWN_PATH),
            ],
        },
        "generated_at": datetime.now().isoformat(timespec="seconds"),
    }


def build_air_markdown(bundle: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# AIR 6D Overlay Bundle")
    lines.append("")
    lines.append(f"Generated: {bundle['generated_at']}")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append(f"- Docs gate: `{bundle['docs_gate_status']}`")
    lines.append("- Authority mode: `local_live_atlas_plus_archive_backed_evidence`")
    lines.append("- Control mode: `overlay_only`")
    lines.append("- AIR role: `naming, topology, schema stability, route legibility`")
    lines.append("")
    lines.append("## Native AIR Basis")
    lines.append("")
    for item in bundle["air_native_basis"]:
        lines.append(
            f"- `{item['basis_id']}` `{item['title']}` [{item['element']}] "
            f"/ appendix stack: `{', '.join(item['appendix_stack'])}`"
        )
    lines.append("")
    lines.append("## Translated Support")
    lines.append("")
    for item in bundle["translated_support"]:
        lines.append(
            f"- `{item['basis_id']}` `{item['title']}` [{item['element']}] "
            f"/ appendix stack: `{', '.join(item['appendix_stack'])}`"
        )
    lines.append("")
    lines.append("## Default Appendix Stack")
    lines.append("")
    for item in bundle["appendix_stack"]:
        source_paths = ", ".join(f"`{path}`" for path in item["source_paths"])
        status = "OK" if item["source_exists"] else "MISSING"
        lines.append(f"- `{item['appendix_id']}` = {item['role']} / sources: {source_paths} / state: `{status}`")
    lines.append("")
    lines.append("## Overlay Registry")
    lines.append("")
    lines.append(f"- Tuple: `{bundle['overlay_registry']['tuple_signature']}`")
    lines.append(f"- Symmetry nodes: `{bundle['overlay_registry']['sigma_count']}`")
    lines.append(f"- Spin kernels: `{bundle['overlay_registry']['spin_count']}`")
    lines.append(f"- Rotation families: `{bundle['overlay_registry']['rotation_family_count']}`")
    lines.append(f"- Dual kernels: `{bundle['overlay_registry']['dual_kernel_count']}`")
    lines.append(f"- Holo states: `{', '.join(bundle['overlay_registry']['holo_states'])}`")
    for item in bundle["overlay_registry"]["registry_laws"]:
        lines.append(f"  - {item}")
    lines.append("")
    lines.append("## Symmetry Lattice")
    lines.append("")
    for item in bundle["symmetry_lattice"]:
        lines.append(f"- `{item['sigma_node']}` = `{item['composition']}` / {item['title']}")
    lines.append("")
    lines.append("## Spin And Rotation Families")
    lines.append("")
    for item in bundle["spin_kernels"]:
        lines.append(f"- `{item['spin_kernel']}`: {item['law']}")
    for item in bundle["rotation_families"]:
        lines.append(f"- `{item['rotation_family']}`: {item['law']}")
    for item in bundle["dual_kernels"]:
        lines.append(f"- `{item['dual_kernel']}`: {item['law']}")
    lines.append(f"- Compression carrier: `{bundle['compression_carrier']['carrier_id']}` / {bundle['compression_carrier']['law']}")
    lines.append("")
    for title, key in (("Modal Routes", "modal_routes"), ("Re-entry Routes", "reentry_routes")):
        lines.append(f"## {title}")
        lines.append("")
        for item in bundle[key]:
            lines.append(
                f"- `{item['route_id']}` = {item['title']} / zero=`{item['local_zero_point']}` / "
                f"sigma=`{item['sigma_node']}` / spin=`{item['spin_kernel']}` / rotation=`{item['rotation_family']}` / "
                f"dual=`{item['dual_kernel']}` / mode=`{item['mobius_mode']}` / appendices=`{', '.join(item['canonical_appendix_map'])}` / "
                f"truth=`{item['truth_state']}` / replay=`{item['replay_source']}`"
            )
        lines.append("")
    lines.append("## Control Documents")
    lines.append("")
    for item in bundle["control_documents"]:
        status = "OK" if item["source_exists"] else "MISSING"
        lines.append(
            f"- `{item['name']}` [{item['role']}] / basis=`{','.join(item['basis_refs'])}` / "
            f"metro=`{', '.join(item['metro_refs'])}` / appendix=`{','.join(item['appendix_refs'])}` / "
            f"state=`{status}`"
        )
    lines.append("")
    lines.append("## Evidence Boundary")
    lines.append("")
    lines.append(f"- Control root: `{bundle['evidence_boundary']['control_root']}`")
    lines.append(f"- Local charter: `{bundle['evidence_boundary']['local_charter']}`")
    lines.append(f"- Live deep root: `{bundle['evidence_boundary']['live_deep_root']}`")
    lines.append(f"- Docs gate note: `{bundle['evidence_boundary']['docs_gate_note']}`")
    lines.append(f"- Historical mirrors: `{', '.join(bundle['evidence_boundary']['historical_mirrors'])}`")
    lines.append(f"- Tesseract sources: `{', '.join(bundle['evidence_boundary']['tesseract_sources'])}`")
    lines.append("")
    return "\n".join(lines).strip() + "\n"


def build_fire_basis_entry(
    driver: dict[str, Any],
    tesseract_bundle: dict[str, Any],
) -> dict[str, Any]:
    title_key = normalize_text(driver["title"])
    matches: list[dict[str, Any]] = []
    for record in tesseract_bundle["records"]:
        haystack = normalize_text(f"{record['title']} {record['relative_path']} {record['chapter_title']}")
        if title_key and title_key in haystack:
            matches.append(
                {
                    "record_id": record["record_id"],
                    "global_addr": record["global_addr"],
                    "chapter_station": record["chapter_station"],
                    "truth_state": record["truth_state"],
                    "relative_path": record["relative_path"],
                }
            )
    source_path = Path(driver["source_path"])
    return {
        "basis_id": driver["doc_id"],
        "title": driver["title"],
        "element": driver["element"],
        "cluster": driver["cluster"],
        "role": driver["contribution"],
        "source_path": driver["source_path"],
        "source_exists": source_path.exists(),
        "appendix_stack": list(driver["appendix_stack"]),
        "dimension_stage": driver["dimension_stage"],
        "fire_bundle": driver["fire_bundle"],
        "mobius_bridge": driver["mobius_bridge"],
        "reverse_appendix_station": driver["reverse_appendix_station"],
        "canonical_appendix_map": list(driver["canonical_appendix_map"]),
        "emergent_projection": driver["emergent_projection"],
        "weave_routes": list(driver["weave_routes"]),
        "matched_tesseract_records": matches[:6],
        "handoff_requirements": list(FIRE_CROSS_AGENT_HANDOFFS),
        "truth_state": "NEAR",
    }


def build_fire_authority_surfaces() -> list[dict[str, Any]]:
    authority_paths = [
        {
            "surface_id": "MATH_GOD_FIRE_CHARTER",
            "classification": "local canon",
            "path": MATH_GOD_ROOT / "93_FIRE_6D_CHARTER.md",
        },
        {
            "surface_id": "MATH_GOD_FIRE_CROSSWALK",
            "classification": "local canon",
            "path": MATH_GOD_ROOT / "94_V4_TO_6D_CROSSWALK.md",
        },
        {
            "surface_id": "FIRE_CONTROL_EXTENSION",
            "classification": "live authority",
            "path": LIVE_DEEP_ROOT_DEFAULT / "00_CONTROL" / "06_FIRE_5D_6D_EXTENSION.md",
        },
        {
            "surface_id": "FIRE_LEVEL_5",
            "classification": "live authority",
            "path": LIVE_DEEP_ROOT_DEFAULT / "07_METRO_STACK" / "05_level_5_mobius_bridge_map.md",
        },
        {
            "surface_id": "FIRE_LEVEL_6",
            "classification": "live authority",
            "path": LIVE_DEEP_ROOT_DEFAULT / "07_METRO_STACK" / "06_level_6_hologram_weave_map.md",
        },
        {
            "surface_id": "FIRE_REVERSE_OVERLAY",
            "classification": "live authority",
            "path": LIVE_DEEP_ROOT_DEFAULT / "08_APPENDIX_CRYSTAL" / "01_reverse_appendix_overlay_ledger.md",
        },
        {
            "surface_id": "PACKAGE_FIRE_EXPORT",
            "classification": "package export mirror",
            "path": PACKAGE_EXPORT_ROOT / "FIRE" / "02_fire_6d_extension.md",
        },
        {
            "surface_id": "PACKAGE_FIRE_EXPORT_LEDGER",
            "classification": "package export mirror",
            "path": PACKAGE_EXPORT_ROOT / "LEDGERS" / "05_fire_6d_export_registry.json",
        },
    ]
    surfaces: list[dict[str, Any]] = []
    for item in authority_paths:
        path = Path(item["path"])
        surfaces.append(
            {
                "surface_id": item["surface_id"],
                "classification": item["classification"],
                "path": str(path),
                "state": "OK" if path.exists() else "MISSING",
            }
        )
    return surfaces


def build_fire_reverse_overlay_registry() -> list[dict[str, Any]]:
    appendix_meta = appendix_registry()
    registry: list[dict[str, Any]] = []
    for item in FIRE_REVERSE_APPENDIX_OVERLAY:
        registry.append(
            item
            | {
                "canonical_appendices": [
                    {
                        "appendix_id": app_id,
                        "role": appendix_meta[app_id]["role"],
                        "source_paths": appendix_meta[app_id]["source_paths"],
                    }
                    for app_id in item["canonical_appendix_map"]
                    if app_id in appendix_meta
                ]
            }
        )
    return registry


def build_fire_bundle(
    tesseract_bundle: dict[str, Any],
    docs_gate: dict[str, str],
) -> dict[str, Any]:
    appendix_meta = appendix_registry()
    appendix_stack: list[dict[str, Any]] = []
    for app_id in FIRE_DEFAULT_APPENDICES:
        meta = appendix_meta[app_id]
        appendix_stack.append(
            {
                "appendix_id": app_id,
                "role": meta["role"],
                "source_paths": list(meta["source_paths"]),
                "source_exists": meta["source_exists"],
            }
        )

    control_documents: list[dict[str, Any]] = []
    for item in FIRE_CONTROL_DOCS:
        path = FIRE_CONTROL_ROOT / item["name"]
        control_documents.append(
            {
                "name": item["name"],
                "role": item["role"],
                "path": str(path),
                "source_exists": path.exists(),
                "basis_refs": list(item["basis_refs"]),
                "metro_refs": list(item["metro_refs"]),
                "appendix_refs": list(item["appendix_refs"]),
            }
        )

    basis_docs = [
        build_fire_basis_entry(item, tesseract_bundle)
        for item in FIRE_NATIVE_DRIVERS + FIRE_BRIDGE_BASIS
    ]
    stage_counts = Counter(item["dimension_stage"] for item in basis_docs)
    bundle_counts = Counter(item["fire_bundle"] for item in basis_docs)
    bridge_counts = Counter(item["mobius_bridge"] for item in basis_docs)

    compression_chain = [
        water_route_record(
            "fire_5d_ignition_compression",
            "Compress ignition pressure into a lawful 5D Fire field.",
            ["06", "08", "10"],
            ["07_METRO_STACK/03_level_4_transcendence_metro_map.md"],
            ["AppA", "AppE", "AppF", "AppI", "AppM"],
            "Z_fire.5d.ignition",
            "01_FIRE/18_5d_compression_field.md",
            "01_FIRE/18_5d_compression_field.md",
        ),
        water_route_record(
            "fire_5d_overburden",
            "Turn novelty debt and overload into explicit overburden maps before lift.",
            ["10", "16"],
            ["07_METRO_STACK/03_level_4_transcendence_metro_map.md"],
            ["AppA", "AppI", "AppM", "AppP"],
            "Z_fire.5d.overburden",
            "01_FIRE/17_ignition_pressure_and_overburden_map.md",
            "01_FIRE/17_ignition_pressure_and_overburden_map.md",
        ),
    ]
    bridge_chain = [
        water_route_record(
            "fire_level5_q_ingress",
            "Use Quad Holographic Rotation to enter the Mobius bridge without rewriting appendix canon.",
            ["04", "14", "09"],
            ["07_METRO_STACK/05_level_5_mobius_bridge_map.md"],
            ["AppE", "AppF", "AppI", "AppM", "AppQ"],
            "Z_fire.level5.q",
            "07_METRO_STACK/05_level_5_mobius_bridge_map.md",
            "08_APPENDIX_CRYSTAL/01_reverse_appendix_overlay_ledger.md",
        ),
        water_route_record(
            "fire_level5_bridge_band",
            "Carry the reverse overlay through Q/O loop routing while keeping canonical appendix mappings explicit.",
            ["14", "15", "16"],
            ["07_METRO_STACK/05_level_5_mobius_bridge_map.md"],
            ["AppA", "AppI", "AppM", "AppO", "AppP", "AppQ"],
            "Z_fire.level5.loop",
            "01_FIRE/21_reverse_appendix_overlay_ledger.md",
            "01_FIRE/21_reverse_appendix_overlay_ledger.md",
        ),
    ]
    weave_chain = [
        water_route_record(
            "fire_level6_hologram_weave",
            "Weave ingress, return, and re-entry into one additive 6D Fire surface.",
            ["04", "14", "15", "16"],
            ["07_METRO_STACK/06_level_6_hologram_weave_map.md"],
            ["AppA", "AppE", "AppF", "AppI", "AppM", "AppO", "AppP", "AppQ"],
            "Z_fire.level6.weave",
            "07_METRO_STACK/06_level_6_hologram_weave_map.md",
            "01_FIRE/20_level_6_hologram_weave_map.md",
        ),
    ]

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "docs_gate_status": docs_gate.get("status", "UNKNOWN"),
        "scope": tesseract_bundle["scope"],
        "active_element": "FIRE",
        "baseline_metro_level": 4,
        "additive_metro_levels": [5, 6],
        "active_basis": list(FIRE_NATIVE_DRIVERS),
        "bridge_basis": list(FIRE_BRIDGE_BASIS),
        "appendix_stack": appendix_stack,
        "control_documents": control_documents,
        "authority_surfaces": build_fire_authority_surfaces(),
        "driver_registry": basis_docs,
        "stage_counts": dict(sorted(stage_counts.items())),
        "fire_bundle_counts": dict(sorted(bundle_counts.items())),
        "mobius_bridge_counts": dict(sorted(bridge_counts.items())),
        "compression_chain": compression_chain,
        "bridge_chain": bridge_chain,
        "weave_chain": weave_chain,
        "reverse_overlay_registry": build_fire_reverse_overlay_registry(),
        "handoff_contracts": list(FIRE_CROSS_AGENT_HANDOFFS),
        "drift_policy": {
            "authority_rule": "Live deep root plus MATH GOD are canon; package export remains downstream mirror only.",
            "docs_gate_status": docs_gate.get("status", "UNKNOWN"),
            "promotion_rule": "No FIRE artifact promotes beyond NEAR without AppI truth basis, AppM replay basis, and cross-agent dependencies.",
        },
        "regeneration_seed": {
            "title": "FIRE 6D Organism Seed",
            "compression_law": "Keep 4D v4 unchanged, then lift only the FIRE pressure field into 5D compression and 6D weave overlays.",
            "expansion_law": "Re-expand through Q ingress, O return, and canonical appendix mappings instead of inventing a second appendix namespace.",
            "shortest_route": "Level4 -> F1/F2 pressure classification -> Level5 bridge -> Level6 weave -> AppQ/AppO anchored return.",
            "deepest_route": "Time Fractal -> Quantum approximation -> Athena emergence -> Ch11 lift -> Zero-point collapse -> Q/O loop -> Ch19 return.",
        },
    }


def build_fire_markdown(bundle: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# FIRE 6D Organism Bundle")
    lines.append("")
    lines.append(f"Generated: {bundle['generated_at']}")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append(f"- Docs gate: `{bundle['docs_gate_status']}`")
    lines.append(f"- Scope: `{bundle['scope']}`")
    lines.append(f"- Active element: `{bundle['active_element']}`")
    lines.append(f"- Baseline metro level: `{bundle['baseline_metro_level']}`")
    lines.append(f"- Additive metro levels: `{', '.join(str(item) for item in bundle['additive_metro_levels'])}`")
    lines.append("")
    lines.append("## Stage Counts")
    lines.append("")
    lines.append(f"- Dimension stages: `{', '.join(f'{key}={value}' for key, value in bundle['stage_counts'].items())}`")
    lines.append(f"- Fire bundles: `{', '.join(f'{key}={value}' for key, value in bundle['fire_bundle_counts'].items())}`")
    lines.append(f"- Mobius bridges: `{', '.join(f'{key}={value}' for key, value in bundle['mobius_bridge_counts'].items())}`")
    lines.append("")
    lines.append("## Driver Registry")
    lines.append("")
    for item in bundle["driver_registry"]:
        lines.append(
            f"- `{item['basis_id']}` `{item['title']}` [{item['dimension_stage']}; bundle={item['fire_bundle']}; bridge={item['mobius_bridge']}] "
            f"/ reverse=`{item['reverse_appendix_station']}` / canonical=`{', '.join(item['canonical_appendix_map'])}`"
        )
        lines.append(f"  - Source: `{item['source_path']}` / state=`{'OK' if item['source_exists'] else 'MISSING'}`")
        lines.append(f"  - Projection: `{item['emergent_projection']}`")
        if item["matched_tesseract_records"]:
            lines.append(
                "  - Tesseract matches: "
                + ", ".join(
                    f"{match['chapter_station']}::{match['record_id']}[{match['truth_state']}]"
                    for match in item["matched_tesseract_records"]
                )
            )
    lines.append("")
    for title, key in (
        ("Compression Chain", "compression_chain"),
        ("Bridge Chain", "bridge_chain"),
        ("Weave Chain", "weave_chain"),
    ):
        lines.append(f"## {title}")
        lines.append("")
        for item in bundle[key]:
            lines.append(
                f"- `{item['route_id']}` = {item['title']} / zero=`{item['local_zero_point']}` / "
                f"return=`{item['return_checkpoint']}` / appendix=`{', '.join(item['appendix_refs'])}`"
            )
        lines.append("")
    lines.append("## Reverse Overlay Registry")
    lines.append("")
    for item in bundle["reverse_overlay_registry"]:
        lines.append(
            f"- `{item['station']}` `{item['title']}` [{item['class']}; bridge={item['bridge_status']}] "
            f"-> `{', '.join(item['canonical_appendix_map'])}`"
        )
    lines.append("")
    lines.append("## Handoff Contracts")
    lines.append("")
    for item in bundle["handoff_contracts"]:
        lines.append(
            f"- `{item['agent']}` `{item['title']}` / appendix=`{', '.join(item['required_appendices'])}` / "
            f"{item['responsibility']}"
        )
    lines.append("")
    lines.append("## Authority Surfaces")
    lines.append("")
    for item in bundle["authority_surfaces"]:
        lines.append(f"- `{item['surface_id']}` [{item['classification']}; {item['state']}] `{item['path']}`")
    lines.append("")
    lines.append("## Regeneration Seed")
    lines.append("")
    for key, value in bundle["regeneration_seed"].items():
        lines.append(f"- `{key}`: {value}")
    lines.append("")
    return "\n".join(lines).strip() + "\n"


def build_markdown(bundle: dict[str, Any]) -> str:
    lines: list[str] = []
    docs_gate = bundle["docs_gate"]
    live = bundle["live_summary"]
    archive = bundle["archive_summary"]
    code_scan = bundle["code_scan"]

    lines.append("# Unified Mycelium Metro System")
    lines.append("")
    lines.append(f"Generated: {bundle['generated_at']}")
    lines.append("")
    lines.append("## Evidence Boundary")
    lines.append("")
    lines.append(f"- Live Google Docs gate: `{docs_gate['status']}`")
    if docs_gate.get("return_code"):
        lines.append(f"- Return code: `{docs_gate['return_code']}`")
    if docs_gate.get("query"):
        lines.append(f"- Gate query witness: `{docs_gate['query']}`")
    if docs_gate.get("note"):
        lines.append(f"- Blocker witness: `{docs_gate['note'].splitlines()[0]}`")
    lines.append("- Working mode: local live atlas plus archive-backed atlas plus prior synthesis layers.")
    lines.append("- Scope: `C:\\Users\\dmitr\\Documents\\Athena Agent\\MATH\\FINAL FORM`.")
    lines.append("")
    lines.append("## Corpus Ledger")
    lines.append("")
    lines.append(f"- Live records: `{live['record_count']}`")
    lines.append(f"- Archive-backed records: `{archive['entry_count']}` across `{archive['archive_count']}` zip archives")
    lines.append(f"- Live top-level bodies: `{', '.join(f'{name}={count}' for name, count in live['top_levels'][:8])}`")
    lines.append(f"- Archive top-level bodies: `{', '.join(f'{name}={count}' for name, count in archive['top_levels'][:6])}`")
    lines.append(f"- Dominant live formats: `{', '.join(f'{ext}={count}' for ext, count in live['extensions'][:8])}`")
    lines.append(f"- Dominant archive formats: `{', '.join(f'{ext}={count}' for ext, count in archive['extensions'][:8])}`")
    if code_scan.get("available"):
        lines.append(
            f"- Code scan witness: `{code_scan['file_count']}` indexed files, `{code_scan['class_count']}` classes, "
            f"`{code_scan['function_count']}` functions, `{code_scan['import_count']}` imports"
        )
        lines.append(f"- Code projects: `{', '.join(f'{name}={count}' for name, count in code_scan['projects'].items())}`")
    lines.append(f"- Signal lexicon: `{', '.join(f'{word}({count})' for word, count in bundle['signal_lexicon'])}`")
    lines.append("")
    lines.append("## Tesseract Lift")
    lines.append("")
    lines.append(f"- Tesseract records: `{bundle['tesseract_v4']['record_count']}`")
    lines.append(f"- Route plans: `{bundle['tesseract_v4']['route_plan_count']}`")
    lines.append(f"- Graph edges: `{bundle['tesseract_v4']['graph_edge_count']}`")
    if bundle["tesseract_v4"].get("bundle_path"):
        lines.append(f"- Bundle: `{bundle['tesseract_v4']['bundle_path']}`")
    if bundle["tesseract_v4"].get("atlas_path"):
        lines.append(f"- Atlas: `{bundle['tesseract_v4']['atlas_path']}`")
    lines.append("")
    if "fire_6d" in bundle:
        lines.append("## FIRE 6D Lift")
        lines.append("")
        fire = bundle["fire_6d"]
        lines.append(f"- Docs gate: `{fire['docs_gate_status']}`")
        lines.append(f"- Drivers: `{fire['driver_count']}`")
        lines.append(f"- Dimension stages: `{', '.join(f'{key}={value}' for key, value in fire['stage_counts'].items())}`")
        lines.append(f"- Mobius bridges: `{', '.join(f'{key}={value}' for key, value in fire['mobius_bridge_counts'].items())}`")
        lines.append(f"- Reverse stations: `{', '.join(item['station'] for item in fire['reverse_overlay_registry'])}`")
        if fire.get("bundle_path"):
            lines.append(f"- Bundle: `{fire['bundle_path']}`")
        if fire.get("atlas_path"):
            lines.append(f"- Atlas: `{fire['atlas_path']}`")
        lines.append("")
    lines.append("## Water 6D Control Lift")
    lines.append("")
    water = bundle["water_6d_control"]
    lines.append(f"- Docs gate: `{water['docs_gate_status']}`")
    lines.append("- Native basis: `" + ", ".join(item["basis_id"] for item in water["water_native_basis"]) + "`")
    lines.append("- Translated support: `" + ", ".join(item["basis_id"] for item in water["translated_support"]) + "`")
    lines.append("- Default appendix stack: `" + ", ".join(item["appendix_id"] for item in water["appendix_stack"]) + "`")
    lines.append(f"- Seed chain routes: `{len(water['seed_chain'])}`")
    lines.append(f"- Lift chain routes: `{len(water['lift_chain'])}`")
    lines.append(f"- Modal routes: `{len(water['modal_routes'])}`")
    lines.append(f"- Recovery routes: `{len(water['recovery_routes'])}`")
    lines.append("")
    lines.append("## AIR 6D Overlay")
    lines.append("")
    air = bundle["air_6d_overlay"]
    lines.append(f"- Docs gate: `{air['docs_gate_status']}`")
    lines.append("- Native basis: `" + ", ".join(item["basis_id"] for item in air["air_native_basis"]) + "`")
    lines.append("- Translated support: `" + ", ".join(item["basis_id"] for item in air["translated_support"]) + "`")
    lines.append("- Default appendix stack: `" + ", ".join(item["appendix_id"] for item in air["appendix_stack"]) + "`")
    lines.append(f"- Symmetry nodes: `{len(air['symmetry_lattice'])}`")
    lines.append(f"- Modal routes: `{len(air['modal_routes'])}`")
    lines.append(f"- Re-entry routes: `{len(air['reentry_routes'])}`")
    lines.append("")
    lines.append("## Earth H6 Gate")
    lines.append("")
    earth = bundle.get("earth_h6", bundle["earth_6d_gate"])
    lines.append(f"- Docs gate: `{earth['docs_gate_status']}`")
    lines.append(f"- Native drivers: `{len(earth['earth_native_drivers'])}`")
    lines.append(f"- Earth bundles: `{len(earth['earth_bundles'])}`")
    lines.append(f"- Chapter contracts: `{len(earth['chapter_contracts'])}`")
    lines.append(f"- Appendix contracts: `{len(earth['appendix_contracts'])}`")
    if earth.get("bundle_path"):
        lines.append(f"- Bundle: `{earth['bundle_path']}`")
    if earth.get("atlas_path"):
        lines.append(f"- Atlas: `{earth['atlas_path']}`")
    lines.append("")
    lines.append("## H6 Convergence")
    lines.append("")
    h6 = bundle["h6_convergence"]
    lines.append(f"- Docs gate: `{h6['docs_gate_status']}`")
    lines.append(f"- Lane inputs: `{', '.join(h6['lane_inputs'].keys())}`")
    lines.append(f"- Shared appendix floor: `{', '.join(item['appendix_id'] for item in h6['shared_appendix_floor'])}`")
    lines.append(f"- Convergence routes: `{len(h6['convergence_routes'])}`")
    lines.append(f"- Re-entry routes: `{len(h6['reentry_routes'])}`")
    lines.append(
        f"- Seed-6D anchors: `{', '.join(h6['seed_6d']['canonical_return_anchors'])}`"
    )
    if h6.get("bundle_path"):
        lines.append(f"- Bundle: `{h6['bundle_path']}`")
    if h6.get("atlas_path"):
        lines.append(f"- Atlas: `{h6['atlas_path']}`")
    lines.append("")
    lines.append("## 7D Seed")
    lines.append("")
    seed7 = bundle["seed_7d"]
    lines.append(f"- Docs gate: `{seed7['docs_gate_status']}`")
    lines.append(f"- Dimension stage: `{seed7['dimension_stage']}`")
    lines.append(f"- Integration scope: `{seed7['integration_scope']}`")
    lines.append(f"- Overlay stack: `{', '.join(seed7['agent_overlay_stack'])}`")
    lines.append(
        "- Earth gate states: `"
        + ", ".join(f"{key}={value}" for key, value in seed7["earth_gate_summary"]["state_counts"].items())
        + "`"
    )
    lines.append(f"- Seed carrier: `{seed7['seed_carrier']}` / state=`{seed7['seed_holo_state']}`")
    lines.append(f"- Seed polarity support: `{', '.join(seed7['seed_polarity_support'])}`")
    lines.append(f"- Witness families: `{len(seed7['witness_families'])}` / awakening notes: `{len(seed7['awakening_agent_notes'])}`")
    if seed7.get("bundle_path"):
        lines.append(f"- Bundle: `{seed7['bundle_path']}`")
    if seed7.get("atlas_path"):
        lines.append(f"- Atlas: `{seed7['atlas_path']}`")
    lines.append("")
    lines.append("## A/B Dual-Kernel Dock")
    lines.append("")
    ab_dock = bundle["a_b_dual_kernel"]
    lines.append(f"- Docs gate: `{ab_dock['docs_gate_status']}`")
    lines.append(f"- Canonical seed: `{ab_dock['canonical_seed']}` / derived dual: `{ab_dock['derived_dual']}`")
    lines.append(f"- Operator: `{ab_dock['inversion_operator']}`")
    if ab_dock.get("bundle_path"):
        lines.append(f"- Bundle: `{ab_dock['bundle_path']}`")
    if ab_dock.get("atlas_path"):
        lines.append(f"- Atlas: `{ab_dock['atlas_path']}`")
    lines.append("")
    lines.append("## AP7D Swarm")
    lines.append("")
    ap7d = bundle["ap7d_swarm"]
    lines.append(f"- Docs gate: `{ap7d['docs_gate_status']}`")
    lines.append(f"- Swarm stage: `{ap7d['swarm_stage']}` / ceiling=`{ap7d['ceiling_stage']}`")
    lines.append(
        f"- Registry stats: `fibers={ap7d['registry_stats']['fiber_count']}, active={ap7d['registry_stats']['active_fibers']}, "
        f"dormant={ap7d['registry_stats']['dormant_fibers']}, collision_free={ap7d['registry_stats']['collision_free']}`"
    )
    lines.append(f"- Hall status: `{ap7d['hall_status_path']}`")
    lines.append(f"- Temple quest: `{ap7d['temple_quest_path']}`")
    if ap7d.get("bundle_path"):
        lines.append(f"- Bundle: `{ap7d['bundle_path']}`")
    if ap7d.get("atlas_path"):
        lines.append(f"- Atlas: `{ap7d['atlas_path']}`")
    lines.append("")
    lines.append("## Sixteen Passes")
    lines.append("")
    for item in bundle["passes"]:
        lines.append(f"### {item['id']} {item['title']}")
        lines.append("")
        lines.append(f"- Aim: {item['description']}")
        lines.append(
            f"- Coverage: `{item['live_match_count']}` live witnesses, `{item['archive_match_count']}` archive witnesses, "
            f"`{item['match_count']}` total matches"
        )
        if item["top_levels"]:
            lines.append(f"- Dominant bodies: `{', '.join(f'{name}={count}' for name, count in item['top_levels'][:5])}`")
        if item["strata"]:
            lines.append(f"- Strata: `{', '.join(f'{name}={count}' for name, count in item['strata'])}`")
        if item["witnesses"]:
            lines.append("- Primary witnesses:")
            for witness in item["witnesses"][:6]:
                hits = ", ".join(witness["hits"])
                lines.append(
                    f"  - `{witness['relative_path']}` [{witness['source_layer']}, score={witness['score']}, hits={hits}]"
                )
        lines.append("")
    lines.append("## Metro Lines")
    lines.append("")
    for item in bundle["lines"]:
        lines.append(f"### {item['id']} {item['title']}")
        lines.append("")
        lines.append(f"- Thesis: {item['thesis']}")
        lines.append(
            f"- Coverage: `{item['live_match_count']}` live witnesses, `{item['archive_match_count']}` archive witnesses"
        )
        if item["top_levels"]:
            lines.append(f"- Bodies: `{', '.join(f'{name}={count}' for name, count in item['top_levels'][:5])}`")
        if item["witnesses"]:
            lines.append("- Stations:")
            for witness in item["witnesses"][:6]:
                hits = ", ".join(witness["hits"])
                lines.append(f"  - `{witness['relative_path']}` [{witness['source_layer']}; {hits}]")
        lines.append("")
    lines.append("## Transfer Hubs")
    lines.append("")
    for hub in bundle["transfer_hubs"]:
        lines.append(
            f"- `{hub['relative_path']}` [{hub['source_layer']}, {hub['stratum']}] intersects "
            f"`{', '.join(hub['line_titles'][:8])}`"
        )
    lines.append("")
    lines.append("## 64-Station Generator Basis")
    lines.append("")
    lines.append("- Basis law: `4 lenses x 4 facets x 4 strata = 64` generator stations.")
    lines.append("- Route law: four ordered selections from the same 64-station basis define the `64^4 = 16,777,216` route field.")
    lines.append("- Four route axes: `Seed Intake`, `Semantic Transform`, `Transport Bridge`, `Closure Publish`.")
    lines.append("")
    for lens in LENSES:
        lines.append(f"### {lens['title']} Stations")
        lines.append("")
        for station in [item for item in bundle["station_basis"] if item["lens"] == lens["title"]]:
            tops = ", ".join(f"{name}={count}" for name, count in station["top_levels"])
            lines.append(
                f"- `{station['station_id']}` = `{station['lens']} x {station['facet']} x {station['stratum']}` "
                f"[coverage={station['coverage']}; top={tops or 'none'}]"
            )
        lines.append("")
    lines.append("## Example Route")
    lines.append("")
    lines.append(
        "- Example four-stage route: "
        + " -> ".join(f"`{station['station_id']}` ({station['lens']} / {station['facet']} / {station['stratum']})" for station in bundle["route_example"])
    )
    lines.append("")
    lines.append("## Integrated Read")
    lines.append("")
    lines.append(
        "The corpus already behaves like a mycelial metro: the manuscript layer names the laws, the runtime layer executes them, "
        "the archive layer preserves historical and code-backed variants, and the synthesis layer stabilizes addresses, witnesses, "
        "and transfer hubs. The sixteen passes do not pretend to read sixteen million routes explicitly; they define the lawful "
        "generator basis from which those routes can be traversed without losing provenance."
    )
    lines.append("")
    return "\n".join(lines).strip() + "\n"


def main() -> int:
    args = parse_args()
    output_json = Path(args.output_json)
    output_md = Path(args.output_md)
    output_tesseract_json = (
        Path(args.output_tesseract_json)
        if args.output_tesseract_json
        else output_json.parent / "math_tesseract_v4_bundle.json"
    )
    output_tesseract_md = (
        Path(args.output_tesseract_md)
        if args.output_tesseract_md
        else output_json.parent / "math_tesseract_v4_bundle.md"
    )
    output_fire_json = (
        Path(args.output_fire_json)
        if args.output_fire_json
        else output_json.parent / "math_fire_6d_organism_bundle.json"
    )
    output_fire_md = (
        Path(args.output_fire_md)
        if args.output_fire_md
        else output_json.parent / "math_fire_6d_organism_bundle.md"
    )
    output_water_6d_json = (
        Path(args.output_water_6d_json)
        if args.output_water_6d_json
        else output_json.parent / "math_water_6d_control_bundle.json"
    )
    output_water_6d_md = (
        Path(args.output_water_6d_md)
        if args.output_water_6d_md
        else output_json.parent / "math_water_6d_control_bundle.md"
    )
    output_air_6d_json = (
        Path(args.output_air_6d_json)
        if args.output_air_6d_json
        else output_json.parent / "math_air_6d_overlay_bundle.json"
    )
    output_air_6d_md = (
        Path(args.output_air_6d_md)
        if args.output_air_6d_md
        else output_json.parent / "math_air_6d_overlay_bundle.md"
    )
    output_earth_json = (
        Path(args.output_earth_json)
        if args.output_earth_json
        else output_json.parent / "earth_h6_contract_bundle.json"
    )
    output_earth_md = (
        Path(args.output_earth_md)
        if args.output_earth_md
        else output_json.parent / "earth_h6_contract_bundle.md"
    )
    output_h6_convergence_json = (
        Path(args.output_h6_convergence_json)
        if args.output_h6_convergence_json
        else output_json.parent / "math_h6_convergence_bundle.json"
    )
    output_h6_convergence_md = (
        Path(args.output_h6_convergence_md)
        if args.output_h6_convergence_md
        else output_json.parent / "math_h6_convergence_bundle.md"
    )
    output_7d_json = (
        Path(args.output_7d_json)
        if args.output_7d_json
        else output_json.parent / "math_7d_synthesis_seed_bundle.json"
    )
    output_7d_md = (
        Path(args.output_7d_md)
        if args.output_7d_md
        else output_json.parent / "math_7d_synthesis_seed_bundle.md"
    )
    output_ab_json = (
        Path(args.output_ab_json)
        if args.output_ab_json
        else output_json.parent / "math_ab_dual_kernel_dock_bundle.json"
    )
    output_ab_md = (
        Path(args.output_ab_md)
        if args.output_ab_md
        else output_json.parent / "math_ab_dual_kernel_dock_bundle.md"
    )
    output_ap7d_json = (
        Path(args.output_ap7d_json)
        if args.output_ap7d_json
        else output_json.parent / "math_ap7d_self_improvement_swarm_bundle.json"
    )
    output_ap7d_md = (
        Path(args.output_ap7d_md)
        if args.output_ap7d_md
        else output_json.parent / "math_ap7d_self_improvement_swarm_bundle.md"
    )
    deep_root = Path(args.deep_root) if args.deep_root else LIVE_DEEP_ROOT_DEFAULT

    live_atlas = load_json(Path(args.live_atlas))
    archive_atlas = load_json(Path(args.archive_atlas))
    archive_manifest = load_json(Path(args.archive_manifest))
    docs_gate = docs_gate_info(Path(args.docs_gate) if args.docs_gate else None)
    code_scan = build_code_scan_summary(Path(args.code_scan) if args.code_scan else None)

    live_records = build_records(live_atlas["records"], "live")
    archive_records = build_records(archive_atlas["records"], "archive")
    all_records = live_records + archive_records

    pass_summaries: list[dict[str, Any]] = []
    for definition in PASS_DEFINITIONS:
        summary = summarize_matches(all_records, definition)
        summary.update({key: definition[key] for key in ("id", "title", "description")})
        pass_summaries.append(summary)

    line_summaries: list[dict[str, Any]] = []
    for definition in LINE_DEFINITIONS:
        summary = summarize_matches(all_records, definition)
        summary.update({key: definition[key] for key in ("id", "title", "thesis")})
        line_summaries.append(summary)

    live_top_levels = Counter(live_atlas["summary"]["by_top_level"])
    archive_top_levels = Counter(archive_manifest["summary"]["by_top_level"])
    live_extensions = Counter(live_atlas["summary"]["by_extension"])
    archive_extensions = Counter(archive_manifest["summary"]["by_extension"])

    station_basis = build_station_basis(all_records)
    route_basis = route_example(station_basis, ["Square", "Flower", "Cloud", "Fractal"])
    tesseract_bundle = build_tesseract_bundle(live_atlas["records"], docs_gate)
    fire_bundle = build_fire_bundle(tesseract_bundle, docs_gate)
    water_bundle = build_water_bundle(docs_gate)
    air_bundle = build_air_bundle(docs_gate)
    earth_bundle = build_earth_bundle(
        tesseract_bundle,
        docs_gate,
        deep_root,
        {
            "live_atlas": str(Path(args.live_atlas)),
            "archive_atlas": str(Path(args.archive_atlas)),
            "archive_manifest": str(Path(args.archive_manifest)),
            "docs_gate": str(Path(args.docs_gate)) if args.docs_gate else "",
            "code_scan": str(Path(args.code_scan)) if args.code_scan else "",
            "deep_root": str(deep_root),
            "tesseract_bundle_json": str(output_tesseract_json),
            "tesseract_bundle_md": str(output_tesseract_md),
        },
    )
    h6_convergence_bundle = build_h6_convergence_bundle(
        tesseract_bundle,
        docs_gate,
        fire_bundle,
        water_bundle,
        air_bundle,
        earth_bundle,
    )
    seed7_bundle = build_seed7_bundle(
        tesseract_bundle,
        docs_gate,
        fire_bundle,
        water_bundle,
        air_bundle,
        earth_bundle,
    )
    ab_dual_kernel_bundle = build_ab_dual_kernel_bundle(seed7_bundle, docs_gate)
    next46_support = build_seed7_next46_support()
    ap7d_bundle = build_ap7d_bundle(
        seed7_bundle,
        docs_gate,
        next46_support,
        {
            "live_root": str(LIVE_DEEP_ROOT_DEFAULT),
            "control_path": str(AP7D_CONTROL_PATH),
            "meta_path": str(AP7D_META_PATH),
            "level_path": str(AP7D_LEVEL_PATH),
            "swarm_manifest_path": str(AP7D_SWARM_MANIFEST_PATH),
            "agent_registry_path": str(AP7D_AGENT_REGISTRY_PATH),
            "heartbeat_feed_path": str(AP7D_HEARTBEAT_FEED_PATH),
            "delta_feed_path": str(AP7D_DELTA_FEED_PATH),
            "handoff_feed_path": str(AP7D_HANDOFF_FEED_PATH),
            "restart_seed_path": str(AP7D_RESTART_SEED_PATH),
            "intent_feed_path": str(AP7D_INTENT_FEED_PATH),
            "macro_note_path": str(AP7D_MACRO_NOTE_PATH),
            "hall_status_path": str(AP7D_HALL_STATUS_PATH),
            "temple_quest_path": str(AP7D_TEMPLE_QUEST_PATH),
            "package_swarm_doc": str(PACKAGE_AP7D_EXPORT_DOC),
            "package_meta_doc": str(PACKAGE_AP7D_META_DOC),
            "package_export_ledger": str(PACKAGE_AP7D_EXPORT_LEDGER),
            "math_god_swarm_path": str(MATH_GOD_AP7D_SWARM_PATH),
            "math_god_meta_path": str(MATH_GOD_AP7D_META_PATH),
            "element_note_refs": {
                "FIRE": str(NEXT46_FIRE_NOTE_PATH),
                "WATER": str(NEXT46_WATER_NOTE_PATH),
                "AIR": str(NEXT46_AIR_NOTE_PATH),
                "EARTH": str(NEXT46_EARTH_NOTE_PATH),
            },
            "appendix_floors": AP7D_APPENDIX_FLOORS,
            "lineage_alphabet": AP7D_LINEAGE_ALPHABET,
            "handoff_order": AP7D_AGENT_ORDER,
            "transition_states": AP7D_TRANSITION_STATES,
            "symbol_to_element": AP7D_LINEAGE_TO_ELEMENT,
            "shared_restart_rule": AP7D_SHARED_RESTART_RULE,
            "seeded_fibers": AP7D_SEEDED_FIBERS,
            "macro_targets": AP7D_MACRO_TARGETS,
        },
    )

    bundle: dict[str, Any] = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "docs_gate": docs_gate,
        "live_summary": {
            "record_count": live_atlas["record_count"],
            "top_levels": live_top_levels.most_common(),
            "extensions": live_extensions.most_common(),
        },
        "archive_summary": {
            "archive_count": archive_manifest["archive_count"],
            "entry_count": archive_manifest["entry_count"],
            "top_levels": archive_top_levels.most_common(),
            "extensions": archive_extensions.most_common(),
        },
        "code_scan": code_scan,
        "signal_lexicon": compute_signal_lexicon(all_records),
        "passes": strip_internal_indexes(pass_summaries),
        "lines": strip_internal_indexes(line_summaries),
        "transfer_hubs": compute_transfer_hubs(line_summaries),
        "station_basis": station_basis,
        "route_example": route_basis,
        "route_field_size": 64 ** 4,
        "tesseract_v4": {
            "record_count": tesseract_bundle["record_count"],
            "route_plan_count": tesseract_bundle["route_plan_count"],
            "graph_edge_count": tesseract_bundle["graph"]["edge_count"],
            "bundle_path": "",
            "atlas_path": "",
        },
        "fire_6d": {
            "docs_gate_status": fire_bundle["docs_gate_status"],
            "driver_count": len(fire_bundle["driver_registry"]),
            "stage_counts": fire_bundle["stage_counts"],
            "mobius_bridge_counts": fire_bundle["mobius_bridge_counts"],
            "reverse_overlay_registry": fire_bundle["reverse_overlay_registry"],
            "bundle_path": "",
            "atlas_path": "",
        },
        "water_6d_control": water_bundle,
        "air_6d_overlay": air_bundle,
        "earth_h6": earth_bundle,
        "earth_6d_gate": earth_bundle,
        "h6_convergence": h6_convergence_bundle,
        "seed_7d": seed7_bundle,
        "a_b_dual_kernel": {
            "docs_gate_status": ab_dual_kernel_bundle["docs_gate_status"],
            "canonical_seed": "A",
            "derived_dual": "B",
            "inversion_operator": ab_dual_kernel_bundle["inversion_operator"]["name"],
            "bundle_path": "",
            "atlas_path": "",
        },
        "ap7d_swarm": {
            "docs_gate_status": ap7d_bundle["docs_gate_status"],
            "swarm_stage": ap7d_bundle["swarm_stage"],
            "ceiling_stage": ap7d_bundle["ceiling_stage"],
            "registry_stats": ap7d_bundle["registry_stats"],
            "hall_status_path": ap7d_bundle["hall_status_path"],
            "temple_quest_path": ap7d_bundle["temple_quest_path"],
            "bundle_path": "",
            "atlas_path": "",
        },
    }
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_tesseract_json.parent.mkdir(parents=True, exist_ok=True)
    output_tesseract_md.parent.mkdir(parents=True, exist_ok=True)
    output_fire_json.parent.mkdir(parents=True, exist_ok=True)
    output_fire_md.parent.mkdir(parents=True, exist_ok=True)
    output_water_6d_json.parent.mkdir(parents=True, exist_ok=True)
    output_water_6d_md.parent.mkdir(parents=True, exist_ok=True)
    output_air_6d_json.parent.mkdir(parents=True, exist_ok=True)
    output_air_6d_md.parent.mkdir(parents=True, exist_ok=True)
    output_earth_json.parent.mkdir(parents=True, exist_ok=True)
    output_earth_md.parent.mkdir(parents=True, exist_ok=True)
    output_h6_convergence_json.parent.mkdir(parents=True, exist_ok=True)
    output_h6_convergence_md.parent.mkdir(parents=True, exist_ok=True)
    output_7d_json.parent.mkdir(parents=True, exist_ok=True)
    output_7d_md.parent.mkdir(parents=True, exist_ok=True)
    output_ab_json.parent.mkdir(parents=True, exist_ok=True)
    output_ab_md.parent.mkdir(parents=True, exist_ok=True)
    output_ap7d_json.parent.mkdir(parents=True, exist_ok=True)
    output_ap7d_md.parent.mkdir(parents=True, exist_ok=True)
    bundle["tesseract_v4"]["bundle_path"] = str(output_tesseract_json)
    bundle["tesseract_v4"]["atlas_path"] = str(output_tesseract_md)
    bundle["fire_6d"]["bundle_path"] = str(output_fire_json)
    bundle["fire_6d"]["atlas_path"] = str(output_fire_md)
    water_bundle["bundle_path"] = str(output_water_6d_json)
    water_bundle["atlas_path"] = str(output_water_6d_md)
    air_bundle["bundle_path"] = str(output_air_6d_json)
    air_bundle["atlas_path"] = str(output_air_6d_md)
    earth_bundle["bundle_path"] = str(output_earth_json)
    earth_bundle["atlas_path"] = str(output_earth_md)
    h6_convergence_bundle["bundle_path"] = str(output_h6_convergence_json)
    h6_convergence_bundle["atlas_path"] = str(output_h6_convergence_md)
    h6_convergence_bundle["lane_inputs"]["fire"]["bundle_path"] = str(output_fire_json)
    h6_convergence_bundle["lane_inputs"]["fire"]["atlas_path"] = str(output_fire_md)
    h6_convergence_bundle["lane_inputs"]["water"]["bundle_path"] = str(output_water_6d_json)
    h6_convergence_bundle["lane_inputs"]["water"]["atlas_path"] = str(output_water_6d_md)
    h6_convergence_bundle["lane_inputs"]["air"]["bundle_path"] = str(output_air_6d_json)
    h6_convergence_bundle["lane_inputs"]["air"]["atlas_path"] = str(output_air_6d_md)
    h6_convergence_bundle["lane_inputs"]["earth"]["bundle_path"] = str(output_earth_json)
    h6_convergence_bundle["lane_inputs"]["earth"]["atlas_path"] = str(output_earth_md)
    seed7_bundle["bundle_path"] = str(output_7d_json)
    seed7_bundle["atlas_path"] = str(output_7d_md)
    ap7d_bundle["bundle_path"] = str(output_ap7d_json)
    ap7d_bundle["atlas_path"] = str(output_ap7d_md)
    bundle["earth_h6"]["bundle_path"] = str(output_earth_json)
    bundle["earth_h6"]["atlas_path"] = str(output_earth_md)
    bundle["earth_6d_gate"]["bundle_path"] = str(output_earth_json)
    bundle["earth_6d_gate"]["atlas_path"] = str(output_earth_md)
    bundle["h6_convergence"]["bundle_path"] = str(output_h6_convergence_json)
    bundle["h6_convergence"]["atlas_path"] = str(output_h6_convergence_md)
    bundle["seed_7d"]["bundle_path"] = str(output_7d_json)
    bundle["seed_7d"]["atlas_path"] = str(output_7d_md)
    ab_dual_kernel_bundle["bundle_path"] = str(output_ab_json)
    ab_dual_kernel_bundle["atlas_path"] = str(output_ab_md)
    ab_dual_kernel_bundle["a_seed_ref"]["bundle_path"] = str(output_7d_json)
    ab_dual_kernel_bundle["b_inversion_ref"]["bundle_path"] = str(output_ab_json)
    seed7_bundle["a_b_dual_kernel_dock"] = {
        key: value
        for key, value in ab_dual_kernel_bundle.items()
        if key not in {"generated_at", "docs_gate_status", "truth_class", "bundle_path", "atlas_path"}
    }
    bundle["a_b_dual_kernel"]["bundle_path"] = str(output_ab_json)
    bundle["a_b_dual_kernel"]["atlas_path"] = str(output_ab_md)
    bundle["ap7d_swarm"]["bundle_path"] = str(output_ap7d_json)
    bundle["ap7d_swarm"]["atlas_path"] = str(output_ap7d_md)
    output_json.write_text(json.dumps(bundle, indent=2), encoding="utf-8")
    output_md.write_text(build_markdown(bundle), encoding="utf-8")
    output_tesseract_json.write_text(json.dumps(tesseract_bundle, indent=2), encoding="utf-8")
    output_tesseract_md.write_text(build_tesseract_markdown(tesseract_bundle), encoding="utf-8")
    output_fire_json.write_text(json.dumps(fire_bundle, indent=2), encoding="utf-8")
    output_fire_md.write_text(build_fire_markdown(fire_bundle), encoding="utf-8")
    output_water_6d_json.write_text(json.dumps(water_bundle, indent=2), encoding="utf-8")
    output_water_6d_md.write_text(build_water_markdown(water_bundle), encoding="utf-8")
    output_air_6d_json.write_text(json.dumps(air_bundle, indent=2), encoding="utf-8")
    output_air_6d_md.write_text(build_air_markdown(air_bundle), encoding="utf-8")
    output_earth_json.write_text(json.dumps(earth_bundle, indent=2), encoding="utf-8")
    output_earth_md.write_text(build_earth_markdown(earth_bundle), encoding="utf-8")
    output_h6_convergence_json.write_text(json.dumps(h6_convergence_bundle, indent=2), encoding="utf-8")
    output_h6_convergence_md.write_text(build_h6_convergence_markdown(h6_convergence_bundle), encoding="utf-8")
    output_7d_json.write_text(json.dumps(seed7_bundle, indent=2), encoding="utf-8")
    output_7d_md.write_text(build_seed7_markdown(seed7_bundle), encoding="utf-8")
    output_ab_json.write_text(json.dumps(ab_dual_kernel_bundle, indent=2), encoding="utf-8")
    output_ab_md.write_text(build_ab_dual_kernel_markdown(ab_dual_kernel_bundle), encoding="utf-8")
    output_ap7d_json.write_text(json.dumps(ap7d_bundle, indent=2), encoding="utf-8")
    output_ap7d_md.write_text(build_ap7d_markdown(ap7d_bundle), encoding="utf-8")

    print(f"Wrote synthesis JSON: {output_json}")
    print(f"Wrote synthesis markdown: {output_md}")
    print(f"Wrote tesseract JSON: {output_tesseract_json}")
    print(f"Wrote tesseract markdown: {output_tesseract_md}")
    print(f"Wrote FIRE 6D JSON: {output_fire_json}")
    print(f"Wrote FIRE 6D markdown: {output_fire_md}")
    print(f"Wrote Water 6D JSON: {output_water_6d_json}")
    print(f"Wrote Water 6D markdown: {output_water_6d_md}")
    print(f"Wrote AIR 6D JSON: {output_air_6d_json}")
    print(f"Wrote AIR 6D markdown: {output_air_6d_md}")
    print(f"Wrote Earth JSON: {output_earth_json}")
    print(f"Wrote Earth markdown: {output_earth_md}")
    print(f"Wrote H6 convergence JSON: {output_h6_convergence_json}")
    print(f"Wrote H6 convergence markdown: {output_h6_convergence_md}")
    print(f"Wrote 7D JSON: {output_7d_json}")
    print(f"Wrote 7D markdown: {output_7d_md}")
    print(f"Wrote A/B dock JSON: {output_ab_json}")
    print(f"Wrote A/B dock markdown: {output_ab_md}")
    print(f"Wrote AP7D JSON: {output_ap7d_json}")
    print(f"Wrote AP7D markdown: {output_ap7d_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
