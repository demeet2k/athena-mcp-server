#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

from nervous_system_core import CHAPTERS, normalize_lookup_text, presentation_name, utc_now, write_json, write_text


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_LIMIT = 10
ZERO_POINT_CHAPTERS = {"Ch11", "Ch18", "Ch20", "Ch21"}
ZERO_POINT_APPENDICES = {"AppF", "AppG", "AppI", "AppM"}
CHAPTER_FRONTIER_CODES = ("Ch03", "Ch10", "Ch12", "Ch14")
TEMPLATE_CHAPTER_CODE = "Ch12"

CHAPTER_PACK_CONFIG = {
    "Ch03": {
        "chapter_code": "Ch03",
        "station": "0002",
        "title": "Truth Corridors and Witness Discipline",
        "chapter_file": "Ch03_0002_truth_corridors_and_witness_discipline.md",
        "frontier_bundle_file": "Ch03_truth_corridors_and_witness_discipline_frontier_bundle.md",
        "evidence_pack_file": "Ch03_truth_corridors_and_witness_discipline_evidence_pack.json",
        "drafting_prep_file": "Ch03_truth_corridors_and_witness_discipline_drafting_prep.md",
        "handoff_file": "003_ch03_truth_corridors_and_witness_discipline_handoff.md",
        "existing_draft_file": None,
        "hubs": ["AppA", "AppI", "AppM", "AppJ"],
        "opening_step": "Open with the Ch03 theorem: truth corridors are lawful only when witnesses, admissibility, and replay discipline remain stronger than guesswork.",
        "theme_tokens": ["truth", "corridor", "witness", "discipline", "admissibility", "replay", "promotion"],
        "facet_atoms": {
            1: [
                ("Corridor Object", ["truth corridor", "corridor", "truth"], "typed corridor object witness"),
                ("Witness Object", ["witness", "proof", "receipt"], "direct witness object or proof bundle"),
                ("Admissibility Object", ["admissibility", "budget", "threshold"], "admissibility object or corridor budget witness"),
                ("Discipline Object", ["discipline", "promotion", "refusal"], "discipline object or refusal witness"),
            ],
            2: [
                ("Corridor Law", ["corridor law", "corridor policy", "corridor"], "corridor law or typed policy statement"),
                ("Witness Law", ["witness law", "proof obligation", "witness"], "witness obligation or promotion law"),
                ("Abstain Law", ["abstain", "guess", "ambiguity"], "abstain-over-guess law witness"),
                ("Promotion Law", ["promotion", "truth lattice", "ok"], "promotion law or truth-lattice witness"),
            ],
            3: [
                ("Corridor Evaluator", ["corridor evaluator", "truth corridor", "checker"], "corridor evaluator runtime witness"),
                ("Witness Pack", ["witness pack", "proof bundle", "receipt"], "witness pack or receipt bundle"),
                ("Residual Monitor", ["residual", "near", "monitor"], "residual monitor or NEAR-ledger witness"),
                ("Promotion Gate", ["promotion gate", "admissibility", "refusal"], "promotion gate or refusal monitor"),
            ],
            4: [
                ("Corridor Certificate", ["corridor certificate", "certificate", "truth corridor"], "signed corridor certificate"),
                ("Witness Receipt", ["witness receipt", "receipt", "proof"], "witness receipt or verifier receipt"),
                ("Replay Proof", ["replay", "deterministic", "proof"], "replay proof or deterministic verifier"),
                ("Promotion Ledger", ["promotion ledger", "ledger", "promotion"], "promotion ledger or published receipt"),
            ],
        },
    },
    "Ch10": {
        "chapter_code": "Ch10",
        "station": "0021",
        "title": "Multi-Lens Solution Construction",
        "chapter_file": "Ch10_0021_multi_lens_solution_construction.md",
        "frontier_bundle_file": "Ch10_multi_lens_solution_construction_frontier_bundle.md",
        "evidence_pack_file": "Ch10_multi_lens_solution_construction_evidence_pack.json",
        "drafting_prep_file": "Ch10_multi_lens_solution_construction_drafting_prep.md",
        "handoff_file": "010_ch10_multi_lens_solution_construction_handoff.md",
        "existing_draft_file": "010_ch10_decisive_coupling_where_inner_outer_and_helical_first_connect.md",
        "hubs": ["AppA", "AppF", "AppM", "AppH", "AppJ", "AppI"],
        "opening_step": "Open with the Ch10 theorem: a valid solution object exists only when multiple lenses are coupled without losing witnesses, routes, or replay.",
        "theme_tokens": ["solution", "multi lens", "construction", "patch", "answer", "synthesis", "routing"],
        "facet_atoms": {
            1: [
                ("Solution Object", ["solution", "object", "answer"], "solution object witness"),
                ("Lens Object", ["lens", "rotation", "view"], "multi-lens object witness"),
                ("Patch Object", ["patch", "delta", "repair"], "patch object or delta witness"),
                ("Answer Object", ["answer", "artifact", "promotion"], "answer object or promoted artifact witness"),
            ],
            2: [
                ("Coupling Law", ["coupling", "lens coupling", "bridge"], "coupling law or bridge witness"),
                ("Synthesis Law", ["synthesis", "merge", "construction"], "synthesis law or merge invariant"),
                ("Patch Law", ["patch", "repair", "construction"], "patch law or repair invariant"),
                ("Promotion Law", ["promotion", "answer", "admissibility"], "answer promotion or admissibility law"),
            ],
            3: [
                ("Solution Constructor", ["constructor", "solution builder", "builder"], "solution builder or constructor runtime"),
                ("Lens Merger", ["lens merger", "merge", "multi lens"], "lens-merger runtime witness"),
                ("Patch Builder", ["patch builder", "delta pack", "repair"], "patch builder or delta-pack witness"),
                ("Answer Compiler", ["answer compiler", "compiler", "artifact"], "answer compiler or artifact-pack witness"),
            ],
            4: [
                ("Solution Certificate", ["solution certificate", "certificate", "answer"], "solution certificate"),
                ("Coupling Receipt", ["coupling receipt", "bridge receipt", "receipt"], "coupling receipt"),
                ("Patch Verification Proof", ["patch verification", "proof", "repair"], "patch verification proof"),
                ("Answer Bundle", ["answer bundle", "certbundle", "bundle"], "answer bundle or proof-carrying bundle"),
            ],
        },
    },
    "Ch12": {
        "chapter_code": "Ch12",
        "station": "0023",
        "title": "Legality, Certificates, and Closure",
        "chapter_file": "Ch12_0023_legality_certificates_and_closure.md",
        "frontier_bundle_file": "Ch12_legality_certificates_and_closure_frontier_bundle.md",
        "evidence_pack_file": "Ch12_legality_certificates_and_closure_evidence_pack.json",
        "drafting_prep_file": "Ch12_legality_certificates_and_closure_drafting_prep.md",
        "handoff_file": "012_ch12_legality_certificates_and_closure_handoff.md",
        "existing_draft_file": "012_ch12_boundary_checks_and_isolation_axioms.md",
        "hubs": ["AppA", "AppF", "AppC", "AppM", "AppI"],
        "opening_step": "Open with the Ch12 closure theorem: closure is lawful only when boundary, transport, truth, quarantine, and replay are typed together.",
        "theme_tokens": ["boundary", "closure", "certificate", "transport", "truth", "quarantine", "replay"],
    },
    "Ch14": {
        "chapter_code": "Ch14",
        "station": "0031",
        "title": "Migration, Versioning, and Pulse Retro Weaving",
        "chapter_file": "Ch14_0031_migration_versioning_and_pulse_retro_weaving.md",
        "frontier_bundle_file": "Ch14_migration_versioning_and_pulse_retro_weaving_frontier_bundle.md",
        "evidence_pack_file": "Ch14_migration_versioning_and_pulse_retro_weaving_evidence_pack.json",
        "drafting_prep_file": "Ch14_migration_versioning_and_pulse_retro_weaving_drafting_prep.md",
        "handoff_file": "014_ch14_migration_versioning_and_pulse_retro_weaving_handoff.md",
        "existing_draft_file": "014_ch14_global_hugging_field_deployment.md",
        "hubs": ["AppA", "AppG", "AppM", "AppH", "AppK", "AppI"],
        "opening_step": "Open with the Ch14 theorem: migration is lawful only when version deltas, compat matrices, rollback law, and retro weaving remain jointly replayable.",
        "theme_tokens": ["migration", "versioning", "pulse", "retro", "weaving", "compat", "rollback", "delta"],
        "facet_atoms": {
            1: [
                ("Migration Object", ["migration", "transport", "move"], "migration object witness"),
                ("Version Object", ["version", "compat", "matrix"], "version object or compat witness"),
                ("Delta Object", ["delta", "patch", "pack"], "delta object or patch witness"),
                ("Retro-Weave Object", ["retro weave", "pulse retro", "weaving"], "retro-weave witness"),
            ],
            2: [
                ("Compatibility Law", ["compatibility", "compat matrix", "version"], "compatibility law or matrix witness"),
                ("Migration Law", ["migration law", "migrate", "transport"], "migration law or route invariant"),
                ("Rollback Law", ["rollback", "revocation", "revert"], "rollback law or revert witness"),
                ("Pulse-Retro Law", ["pulse retro", "retro weaving", "time"], "pulse-retro law or weaving invariant"),
            ],
            3: [
                ("Delta Pack Builder", ["delta pack", "patch builder", "builder"], "delta-pack builder or migration runtime"),
                ("Compat Matrix", ["compat matrix", "version matrix", "matrix"], "compat-matrix witness"),
                ("Rollback Engine", ["rollback engine", "revert", "rollback"], "rollback engine witness"),
                ("Retro-Weaving Runtime", ["retro weaving", "pulse retro", "runtime"], "retro-weaving runtime witness"),
            ],
            4: [
                ("Migration Certificate", ["migration certificate", "certificate", "migrate"], "migration certificate"),
                ("Version Receipt", ["version receipt", "compat receipt", "receipt"], "version receipt"),
                ("Rollback Proof", ["rollback proof", "revert proof", "proof"], "rollback proof"),
                ("Delta Replay Capsule", ["delta replay", "capsule", "replay"], "delta replay capsule"),
            ],
        },
    }
}

LENS_FRAMES = {
    "S": {"label": "Square", "keywords": ["square", "structural", "axiomatic", "discrete"]},
    "F": {"label": "Flower", "keywords": ["flower", "transport", "operator", "bridge"]},
    "C": {"label": "Cloud", "keywords": ["cloud", "corridor", "truth", "governance"]},
    "R": {"label": "Fractal", "keywords": ["fractal", "replay", "verification", "deterministic"]},
}

CH12_CELL_GROUPS = {
    "S": {
        "label": "Square",
        "facets": {
            1: [
                ("a", "Hausdorff Boundary", ["hausdorff", "boundary", "topology", "separation"], "direct topological boundary proof"),
                ("b", "Logic Wall", ["logic wall", "firewall", "directional", "causal"], "directional firewall or corridor law"),
                ("c", "Quarantine Flux Tensor", ["flux", "tensor", "quarantine", "surface integral"], "certified flux or surface-integral witness"),
                ("d", "Paraconsistent Zone", ["paraconsistent", "quarantine", "explosion", "zone"], "paraconsistent containment witness"),
            ],
            2: [
                ("a", "Absolute Disjointness", ["disjoint", "intersection", "empty", "isolation"], "disjointness certificate or proof object"),
                ("b", "Zero Boundary Flux", ["zero flux", "surface integral", "leak", "flux"], "zero-flux log or enclosure proof"),
                ("c", "Paraconsistent Containment", ["containment", "fail", "ref", "quarantine"], "containment receipt or quarantine rule"),
                ("d", "Abstain Axiom", ["abstain", "ambig", "guess", "suspend"], "truth-corridor or ambiguity witness"),
            ],
            3: [
                ("a", "Hausdorff Boundary Compiler", ["compiler", "hausdorff", "boundary"], "compiler or builder runtime witness"),
                ("b", "Flux Integrator", ["flux integrator", "surface integral", "integrator"], "runtime integrator or monitoring witness"),
                ("c", "Logic Gatekeeper", ["gatekeeper", "logic wall", "drop"], "gatekeeper or packet-drop runtime witness"),
                ("d", "Paraconsistent Allocator", ["allocator", "paraconsistent", "zone"], "allocator or quarantine runtime witness"),
            ],
            4: [
                ("a", "Hausdorff Separation Certificate", ["certificate", "hausdorff", "separation"], "certificate or signed receipt"),
                ("b", "Zero Flux Receipt", ["zero flux", "receipt", "log"], "zero-flux receipt"),
                ("c", "Disjointness Certificate", ["disjoint", "certificate", "proof"], "disjointness certificate"),
                ("d", "Containment Proof Receipt", ["containment", "proof", "receipt"], "containment proof"),
            ],
        },
    },
    "F": {
        "label": "Flower",
        "facets": {
            1: [
                ("a", "Boundary Morphism", ["boundary morphism", "morphism", "boundary"], "boundary morphism or transport witness"),
                ("b", "Permeability Envelope", ["permeability", "envelope", "budget"], "budget or corridor-policy witness"),
                ("c", "Reflection Matrix", ["reflection", "matrix", "involutory"], "reflection or duality witness"),
                ("d", "DUAL Edge Firewall", ["dual", "firewall", "swap"], "DUAL sanity or firewall witness"),
            ],
            2: [
                ("a", "Morphism Isolation Preservation", ["isolation", "preservation", "morphism"], "transport-isolation proof"),
                ("b", "Permeability Exhaustion", ["permeability", "drop", "capacity"], "capacity or drop-policy witness"),
                ("c", "Perfect Reflection", ["perfect reflection", "invert", "matrix"], "reflection proof"),
                ("d", "DUAL Sanity Check", ["dual sanity", "ok", "firewall"], "swap sanity certificate"),
            ],
            3: [
                ("a", "Boundary Router", ["boundary router", "route", "beta"], "router or path-log witness"),
                ("b", "Permeability Enforcer", ["permeability enforcer", "throttle", "drop"], "throttle or enforcer witness"),
                ("c", "Reflection Engine", ["reflection engine", "reflected", "matrix"], "reflection runtime witness"),
                ("d", "DUAL Firewall Daemon", ["daemon", "dual", "firewall"], "daemon or swap-queue witness"),
            ],
            4: [
                ("a", "Isolation Preservation Certificate", ["isolation preservation", "certificate"], "isolation-preservation certificate"),
                ("b", "Permeability Receipt", ["permeability", "receipt", "drop"], "drop receipt"),
                ("c", "Reflection Execution Proof", ["reflection", "proof", "certificate"], "reflection certificate"),
                ("d", "DUAL Sanity Certificate", ["dual sanity", "certificate"], "dual sanity certificate"),
            ],
        },
    },
    "C": {
        "label": "Cloud",
        "facets": {
            1: [
                ("a", "Boundary Truth State", ["boundary truth", "truth state", "corridor"], "truth-corridor witness"),
                ("b", "Admissibility Threshold", ["threshold", "admissibility", "variance"], "threshold or corridor-budget witness"),
                ("c", "Contradiction Trace", ["contradiction trace", "paradox", "trace"], "contradiction trace witness"),
                ("d", "Quarantine Manifest", ["quarantine manifest", "manifest", "catalog"], "manifest witness"),
            ],
            2: [
                ("a", "Boundary Ambiguity Failure", ["ambig", "fail", "boundary"], "strict truth rule"),
                ("b", "Threshold Lockout", ["lockout", "threshold", "variance"], "lockout witness"),
                ("c", "Paraconsistent Analysis Bound", ["analysis bound", "paraconsistent", "cycles"], "bounded paradox-analysis witness"),
                ("d", "Manifest Accuracy Constraint", ["manifest accuracy", "quarantine", "counts"], "manifest accuracy certificate"),
            ],
            3: [
                ("a", "Truth Corridor Evaluator", ["truth corridor evaluator", "boundary nodes"], "corridor evaluator witness"),
                ("b", "Variance Checker", ["variance checker", "threshold"], "variance checker witness"),
                ("c", "Paradox Analyzer", ["paradox analyzer", "contradiction trace"], "paradox analyzer witness"),
                ("d", "Manifest Compiler", ["manifest compiler", "quarantine"], "manifest compiler witness"),
            ],
            4: [
                ("a", "Strict Boundary Truth Certificate", ["strict boundary truth", "certificate"], "strict truth certificate"),
                ("b", "Lockout Receipt", ["lockout", "receipt"], "lockout receipt"),
                ("c", "Para-Analysis Bound Proof", ["bound proof", "paraconsistent", "analysis"], "para-analysis proof"),
                ("d", "Manifest Accuracy Certificate", ["manifest accuracy", "certificate"], "manifest certificate"),
            ],
        },
    },
    "R": {
        "label": "Fractal",
        "facets": {
            1: [
                ("a", "Boundary Verifier Capsule", ["capsule", "boundary verifier", "replay"], "replay capsule witness"),
                ("b", "Replay Truth Matrix", ["truth matrix", "replay", "decision"], "truth-matrix witness"),
                ("c", "Containment Emulation Script", ["emulation script", "containment", "sandbox"], "sandbox or VM witness"),
                ("d", "Deterministic Isolation Seed", ["isolation seed", "deterministic", "hash"], "deterministic seed witness"),
            ],
            2: [
                ("a", "Boundary Bitwise Match", ["bitwise", "boundary", "match"], "bitwise diff witness"),
                ("b", "Truth Matrix Equality", ["truth matrix equality", "matrix"], "matrix equality witness"),
                ("c", "Safe Containment Emulation", ["safe containment emulation", "sandbox"], "sandbox safety witness"),
                ("d", "Seed Graph Isomorphism", ["isomorphism", "seed graph"], "isomorphism witness"),
            ],
            3: [
                ("a", "Boundary Sandbox Emulator", ["sandbox emulator", "boundary"], "sandbox emulator witness"),
                ("b", "Matrix Comparer", ["matrix comparer", "truth matrix"], "matrix comparer witness"),
                ("c", "Safe Emu Runner", ["safe emu", "jail", "sandbox"], "safe emulation witness"),
                ("d", "Capsule Sealer", ["capsule sealer", "hash"], "capsule sealing witness"),
            ],
            4: [
                ("a", "Boundary Diff Certificate", ["diff certificate", "boundary"], "boundary diff certificate"),
                ("b", "Truth Matrix Match Proof", ["truth matrix match", "proof"], "truth-matrix proof"),
                ("c", "Emulation Safety Receipt", ["emulation safety", "receipt"], "emulation safety receipt"),
                ("d", "Seed Isomorphism Proof", ["seed isomorphism", "proof"], "seed isomorphism proof"),
            ],
        },
    },
}


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def chapter_from_code(chapter_code: str):
    return next(chapter for chapter in CHAPTERS if chapter.code == chapter_code)


def canonical_pair_key(src_id: str, dst_id: str) -> str:
    ordered = sorted((src_id, dst_id))
    return f"{ordered[0]}::{ordered[1]}"


def chapter_config(chapter_code: str) -> dict:
    return CHAPTER_PACK_CONFIG[chapter_code]


def generated_cell_groups(chapter_code: str) -> dict[str, dict]:
    config = chapter_config(chapter_code)
    groups: dict[str, dict] = {}
    for lens, lens_frame in LENS_FRAMES.items():
        groups[lens] = {"label": lens_frame["label"], "facets": {}}
        for facet_index, atoms in config["facet_atoms"].items():
            groups[lens]["facets"][facet_index] = []
            for atom_index, (stem, keywords, next_witness) in enumerate(atoms):
                atom = "abcd"[atom_index]
                merged_keywords = list(dict.fromkeys(keywords + lens_frame["keywords"] + config["theme_tokens"]))
                groups[lens]["facets"][facet_index].append(
                    (atom, f"{lens_frame['label']} {stem}", merged_keywords, next_witness)
                )
    return groups


def cell_groups_for_chapter(chapter_code: str) -> dict[str, dict]:
    if chapter_code == TEMPLATE_CHAPTER_CODE:
        return CH12_CELL_GROUPS
    return generated_cell_groups(chapter_code)


def chapter_paths(active_root: Path, self_actualize_root: Path, chapter_code: str) -> dict[str, Path]:
    config = chapter_config(chapter_code)
    existing_draft = (
        self_actualize_root / "manuscript_sections" / config["existing_draft_file"]
        if config.get("existing_draft_file")
        else None
    )
    return {
        "frontier_bundle": active_root / "10_FRONTIERS" / config["frontier_bundle_file"],
        "evidence_pack": active_root / "10_FRONTIERS" / config["evidence_pack_file"],
        "drafting_prep": active_root / "10_FRONTIERS" / config["drafting_prep_file"],
        "chapter_tile": active_root / "04_CHAPTERS" / config["chapter_file"],
        "compiler_manifest": active_root / "06_RUNTIME" / "13_chapter_frontier_manifest.json",
        "existing_manuscript_draft": existing_draft,
        "manuscript_handoff": self_actualize_root / "manuscript_sections" / config["handoff_file"],
        "network_manifest": active_root / "13_DEEPER_NEURAL_NET" / "09_RUNTIME" / "00_network_manifest.json",
        "ordered_pair_matrix": active_root / "13_DEEPER_NEURAL_NET" / "09_RUNTIME" / "02_ordered_pair_matrix.json",
        "facet_index": active_root / "13_DEEPER_NEURAL_NET" / "09_RUNTIME" / "04_facet_index.json",
        "zero_point_index": active_root / "13_DEEPER_NEURAL_NET" / "09_RUNTIME" / "06_zero_point_index.json",
        "element_registry": active_root / "13_DEEPER_NEURAL_NET" / "09_RUNTIME" / "01_element_registry.json",
    }


def record_blob(record: dict) -> str:
    parts = [
        record.get("name", ""),
        record.get("display_name", ""),
        record.get("excerpt", ""),
        " ".join(record.get("tokens", [])),
        " ".join(record.get("chapters", [])),
        " ".join(record.get("appendices", [])),
    ]
    return normalize_lookup_text(" ".join(parts))


def build_canonical_pair_map(pairs: list[dict], docs_by_id: dict[str, dict]) -> dict[str, dict]:
    canonical: dict[str, dict] = {}
    for pair in pairs:
        if pair.get("kind") != "ordered_pair" or pair["src"] == pair["dst"]:
            continue
        key = canonical_pair_key(pair["src"], pair["dst"])
        existing = canonical.get(key)
        if existing is not None and existing["score"] >= pair["score"]:
            continue
        src = docs_by_id[pair["src"]]
        dst = docs_by_id[pair["dst"]]
        canonical[key] = {
            "src_id": src["id"],
            "dst_id": dst["id"],
            "src_display_name": presentation_name(src["display_name"]),
            "dst_display_name": presentation_name(dst["display_name"]),
            "src_family": src["family"],
            "dst_family": dst["family"],
            "src_element": src["element"],
            "dst_element": dst["element"],
            "src_gate": src["gate"],
            "dst_gate": dst["gate"],
            "canonical_pair_key": key,
            "score": pair["score"],
            "shared_chapters": pair["shared_chapters"],
            "shared_appendices": pair["shared_appendices"],
            "shared_tokens": pair["shared_tokens"],
        }
    return canonical


def load_runtime(active_root: Path) -> dict[str, object]:
    runtime_dir = active_root / "13_DEEPER_NEURAL_NET" / "09_RUNTIME"
    manifest = load_json(runtime_dir / "00_network_manifest.json")
    registry = load_json(runtime_dir / "01_element_registry.json")
    ordered_pairs = load_json(runtime_dir / "02_ordered_pair_matrix.json")
    facet_index = load_json(runtime_dir / "04_facet_index.json")
    zero_point_index = load_json(runtime_dir / "06_zero_point_index.json")
    docs_by_id = {item["id"]: item for item in registry}
    canonical_pairs = build_canonical_pair_map(ordered_pairs, docs_by_id)
    return {
        "manifest": manifest,
        "registry": registry,
        "ordered_pairs": ordered_pairs,
        "facet_index": facet_index,
        "zero_point_index": zero_point_index,
        "docs_by_id": docs_by_id,
        "canonical_pairs": canonical_pairs,
    }


def parse_frontier_bundle(frontier_path: Path) -> list[dict]:
    if not frontier_path.exists():
        return []
    text = frontier_path.read_text(encoding="utf-8")
    entries: list[dict] = []
    blocks = re.split(r"\n### ", "\n" + text)
    for block in blocks[1:]:
        lines = block.splitlines()
        title = presentation_name(lines[0].strip())
        source_layer = ""
        family = ""
        match_score = 0
        appendix_route: list[str] = []
        excerpt_lines: list[str] = []
        for line in lines[1:]:
            stripped = line.strip()
            if stripped.startswith("- Source layer:"):
                source_layer = stripped.split("`")[1]
            elif stripped.startswith("- Family:"):
                family = stripped.split("`")[1]
            elif stripped.startswith("- Match score:"):
                try:
                    match_score = int(stripped.split("`")[1])
                except (IndexError, ValueError):
                    match_score = 0
            elif stripped.startswith("- Rank score:"):
                try:
                    match_score = int(stripped.split("`")[1])
                except (IndexError, ValueError):
                    match_score = 0
            elif stripped.startswith("- Appendix route:"):
                appendix_route = [part.strip() for part in stripped.split("`")[1].split(",")]
            elif stripped.startswith("- Appendices:"):
                appendix_route = [part.strip() for part in stripped.split("`")[1].split(",")]
            elif stripped and not stripped.startswith("-"):
                excerpt_lines.append(stripped)
        entries.append(
            {
                "title": title,
                "source_layer": source_layer,
                "family_label": family,
                "match_score": match_score,
                "appendix_route": appendix_route,
                "excerpt": " ".join(excerpt_lines)[:900],
            }
        )
    return entries


def resolve_bundle_entry_docs(bundle_entries: list[dict], docs_by_id: dict[str, dict]) -> dict[str, dict]:
    resolved: dict[str, dict] = {}
    normalized_docs = {
        doc_id: {
            "display": normalize_lookup_text(document["display_name"]),
            "name": normalize_lookup_text(document["name"]),
        }
        for doc_id, document in docs_by_id.items()
    }
    for entry in bundle_entries:
        title_norm = normalize_lookup_text(entry["title"])
        candidates: list[tuple[int, str]] = []
        title_tokens = set(title_norm.split())
        for doc_id, normalized in normalized_docs.items():
            score = 0
            if title_norm and (title_norm == normalized["display"] or title_norm == normalized["name"]):
                score += 10
            if title_norm and (title_norm in normalized["display"] or title_norm in normalized["name"]):
                score += 6
            score += len(title_tokens & set(normalized["display"].split()))
            if score > 0:
                candidates.append((score, doc_id))
        if not candidates:
            continue
        candidates.sort(key=lambda item: (-item[0], item[1]))
        resolved[candidates[0][1]] = entry
    return resolved


def chapter_source_ids(chapter_code: str, runtime: dict[str, object]) -> list[str]:
    return list(runtime["facet_index"]["facets"]["chapter"].get(chapter_code, []))


def rank_frontier_sources(chapter_code: str, runtime: dict[str, object], bundle_doc_map: dict[str, dict], hubs: list[str]) -> list[dict]:
    docs_by_id = runtime["docs_by_id"]
    chapter = chapter_from_code(chapter_code)
    selected_ids = set(chapter_source_ids(chapter_code, runtime)) | set(bundle_doc_map)
    ranked: list[dict] = []
    for doc_id in selected_ids:
        document = docs_by_id[doc_id]
        score = 0
        reasons: list[str] = []
        if chapter_code in document["chapters"]:
            score += 8
            reasons.append(f"direct {chapter_code} routing")
        if doc_id in bundle_doc_map:
            bundle_entry = bundle_doc_map[doc_id]
            score += bundle_entry["match_score"] + 4
            reasons.append(f"frontier bundle score {bundle_entry['match_score']}")
        appendix_hits = sorted(set(document["appendices"]) & set(hubs))
        if appendix_hits:
            score += len(appendix_hits) * 2
            reasons.append("hub overlap " + ",".join(appendix_hits))
        if document["family"] in set(chapter.families):
            score += 3
            reasons.append(f"core {chapter_code} family")
        if document["family"] in {"higher-dimensional-geometry", "civilization-and-governance", "mythic-sign-systems"}:
            score += 1
        ranked.append(
            {
                "id": document["id"],
                "display_name": presentation_name(document["display_name"]),
                "source_layer": document["source_layer"],
                "family": document["family"],
                "family_label": document.get("family_label"),
                "element": document["element"],
                "gate": document["gate"],
                "chapters": document["chapters"],
                "appendices": document["appendices"],
                "relative_path": document["relative_path"],
                "excerpt": document.get("excerpt", ""),
                "tokens": document.get("tokens", []),
                "rank_score": score,
                "reasons": reasons,
            }
        )
    ranked.sort(key=lambda item: (-item["rank_score"], item["display_name"], item["id"]))
    return ranked


def rank_cross_family_routes(chapter_code: str, runtime: dict[str, object], source_ids: set[str], hubs: list[str], limit: int) -> list[dict]:
    routes: list[dict] = []
    for pair in runtime["canonical_pairs"].values():
        if pair["src_family"] == pair["dst_family"]:
            continue
        if pair["src_id"] not in source_ids and pair["dst_id"] not in source_ids:
            continue
        score = pair["score"]
        if chapter_code in pair["shared_chapters"]:
            score += 4
        score += len(set(pair["shared_appendices"]) & set(hubs)) * 2
        routes.append({**pair, "kind": pair.get("kind", "cross_family_route"), "route_score": score})
    routes.sort(key=lambda item: (-item["route_score"], -item["score"], item["src_display_name"], item["dst_display_name"]))
    return routes[:limit]


def rank_zero_point_routes(runtime: dict[str, object], source_ids: set[str], hubs: list[str], limit: int) -> list[dict]:
    routes: list[dict] = []
    for pair in runtime["zero_point_index"]["routes"]:
        if pair["src_id"] not in source_ids and pair["dst_id"] not in source_ids:
            if not (set(pair["shared_appendices"]) & set(hubs)):
                continue
        routes.append({**pair, "kind": pair.get("kind", "zero_point_route")})
    routes.sort(key=lambda item: (-item.get("convergence_score", item["score"]), -item["score"], item["src_display_name"], item["dst_display_name"]))
    return routes[:limit]


def existing_manuscript_context(existing_draft_path: Path | None) -> dict:
    if existing_draft_path is None:
        return {"exists": False, "path": "(none)", "text": ""}
    if not existing_draft_path.exists():
        return {"exists": False, "path": str(existing_draft_path), "text": ""}
    text = existing_draft_path.read_text(encoding="utf-8")
    return {"exists": True, "path": str(existing_draft_path), "text": text}


def preferred_families_for_lens(lens: str) -> set[str]:
    mapping = {
        "S": {"transport-and-runtime", "manuscript-architecture", "higher-dimensional-geometry"},
        "F": {"transport-and-runtime", "higher-dimensional-geometry"},
        "C": {"void-and-collapse", "manuscript-architecture", "civilization-and-governance"},
        "R": {"transport-and-runtime", "live-orchestration", "manuscript-architecture"},
    }
    return mapping[lens]


def score_cell_sources(cell_keywords: list[str], lens: str, sources: list[dict], draft_text: str) -> tuple[list[dict], bool]:
    ranked: list[tuple[int, dict]] = []
    for source in sources:
        blob = record_blob(source)
        score = 0
        for keyword in cell_keywords:
            norm_keyword = normalize_lookup_text(keyword)
            if norm_keyword and norm_keyword in blob:
                score += 3
        if source["family"] in preferred_families_for_lens(lens):
            score += 1
        if score > 0:
            ranked.append((score, source))
    ranked.sort(key=lambda item: (-item[0], item[1]["display_name"], item[1]["id"]))
    draft_hit = any(normalize_lookup_text(keyword) in normalize_lookup_text(draft_text) for keyword in cell_keywords) if draft_text else False
    return [item[1] for item in ranked[:3]], draft_hit


def candidate_summary(chapter_code: str, facet_index: int, title: str, support_docs: list[dict], draft_hit: bool) -> str:
    support_names = ", ".join(doc["display_name"] for doc in support_docs[:2]) or "local chapter support pack"
    chapter = chapter_from_code(chapter_code)
    if facet_index == 1:
        base = f"Candidate object: `{title}` should be introduced as one of the load-bearing entities grounding `{chapter.title}`."
    elif facet_index == 2:
        base = f"Candidate law: `{title}` should constrain how `{chapter.title}` stays lawful, typed, and witness-safe."
    elif facet_index == 3:
        base = f"Candidate construction: `{title}` should operationalize `{chapter.title}` as executable machinery."
    else:
        base = f"Candidate certificate: `{title}` should seal the corresponding object, law, or construction for `{chapter.title}` with replayable evidence."
    if draft_hit:
        return f"{base} Existing manuscript draft support is already present, and the strongest local witnesses are `{support_names}`."
    return f"{base} The strongest local witnesses are `{support_names}`."


def open_summary(chapter_code: str, title: str, next_witness: str) -> str:
    return f"OPEN - current local evidence does not yet supply a direct witness-rich candidate for `{title}` in `{chapter_code}`. Next witness needed: {next_witness}."


def build_cell_fill_map(chapter_code: str, sources: list[dict], existing_draft: dict) -> tuple[dict[str, dict], list[dict]]:
    cell_fill_map: dict[str, dict] = {}
    open_cells: list[dict] = []
    draft_text = existing_draft["text"]
    station = chapter_config(chapter_code)["station"]
    for lens, lens_info in cell_groups_for_chapter(chapter_code).items():
        for facet_index, cells in lens_info["facets"].items():
            for atom, title, keywords, next_witness in cells:
                cell_code = f"{chapter_code}<{station}>.{lens}{facet_index}.{atom}"
                support_docs, draft_hit = score_cell_sources(keywords, lens, sources, draft_text)
                if support_docs or draft_hit:
                    status = "CANDIDATE"
                    summary = candidate_summary(chapter_code, facet_index, title, support_docs, draft_hit)
                    evidence_refs = [doc["id"] for doc in support_docs]
                    if draft_hit:
                        evidence_refs.append("existing_manuscript_draft")
                else:
                    status = "OPEN"
                    summary = open_summary(chapter_code, title, next_witness)
                    evidence_refs = []
                entry = {
                    "cell_code": cell_code,
                    "lens": lens,
                    "facet_index": facet_index,
                    "atom": atom,
                    "title": title,
                    "status": status,
                    "summary": summary,
                    "evidence_refs": evidence_refs,
                    "next_witness": next_witness,
                }
                cell_fill_map[cell_code] = entry
                if status == "OPEN":
                    open_cells.append(entry)
    return cell_fill_map, open_cells


def duplicate_warnings(frontier_sources: list[dict]) -> list[dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for source in frontier_sources:
        grouped[normalize_lookup_text(source["display_name"])].append(source)
    warnings = []
    for group in grouped.values():
        if len(group) < 2:
            continue
        warnings.append(
            {
                "display_name": group[0]["display_name"],
                "docs": [item["id"] for item in group],
                "source_layers": sorted({item["source_layer"] for item in group}),
            }
        )
    return sorted(warnings, key=lambda item: item["display_name"])


def witness_obligations(open_cells: list[dict], duplicate_groups: list[dict], chapter_code: str) -> list[str]:
    obligations = []
    if duplicate_groups:
        obligations.append("Collapse duplicate source families into one canonical witness before final closure claims are promoted.")
    grouped_open = defaultdict(list)
    for cell in open_cells:
        grouped_open[cell["lens"]].append(cell)
    for lens, cells in sorted(grouped_open.items()):
        obligations.append(
            f"Lens {lens}: supply direct witnesses for {', '.join(cell['title'] for cell in cells[:4])} before claiming the {chapter_code} crystal is fully closed."
        )
    if not obligations:
        obligations.append("All current cells have candidate local witnesses; remaining work is promotion, ordering, and proof tightening.")
    return obligations


def drafting_order(chapter_code: str, frontier_sources: list[dict], cross_family_routes: list[dict], open_cells: list[dict], existing_draft: dict) -> list[str]:
    chapter = chapter_from_code(chapter_code)
    config = chapter_config(chapter_code)
    steps = [
        config["opening_step"],
        f"Draft the Square lens first to state the base entities and invariants needed by `{chapter.title}`.",
        f"Use the Flower lens second to translate `{chapter.title}` into lawful movement, transport, or operator transitions.",
        f"Use the Cloud lens third to define truth handling, ambiguity control, and live corridor behavior for `{chapter.title}`.",
        f"Use the Fractal lens fourth to bind `{chapter.title}` to replay, verification, and certificate-bearing return paths.",
    ]
    if frontier_sources:
        steps.append(f"Integrate strongest external witnesses early: {', '.join(source['display_name'] for source in frontier_sources[:3])}.")
    if cross_family_routes:
        steps.append(
            f"Use cross-family bridges to connect {chapter_code} outward: {cross_family_routes[0]['src_display_name']} <-> {cross_family_routes[0]['dst_display_name']}."
        )
    if existing_draft["exists"]:
        steps.append("Treat the existing manuscript draft as a prose scaffold, but reorder it around the compiled evidence stack and explicit witness obligations.")
    else:
        steps.append("There is no existing manuscript draft; the additive handoff should become the first prose-ready scaffold for the final drafter.")
    if open_cells:
        steps.append("End with a witness ledger naming what still blocks full closure and what next witness would discharge each OPEN cell.")
    else:
        steps.append("Close with a promotion ledger that marks which candidate cells are ready for proof tightening versus immediate drafting.")
    return steps


def build_frontier_payload(
    active_root: Path,
    build_root: Path,
    self_actualize_root: Path,
    records: list[dict],
    chapter_code: str,
    live_docs_blocked: bool,
    limit: int = DEFAULT_LIMIT,
) -> dict:
    del build_root, records
    if chapter_code not in CHAPTER_PACK_CONFIG:
        raise KeyError(f"Unsupported chapter pack: {chapter_code}")
    config = CHAPTER_PACK_CONFIG[chapter_code]
    paths = chapter_paths(active_root, self_actualize_root, chapter_code)
    chapter = chapter_from_code(chapter_code)
    runtime = load_runtime(active_root)
    bundle_entries = parse_frontier_bundle(paths["frontier_bundle"])
    bundle_doc_map = resolve_bundle_entry_docs(bundle_entries, runtime["docs_by_id"])
    frontier_sources = rank_frontier_sources(chapter_code, runtime, bundle_doc_map, config["hubs"])
    source_ids = {item["id"] for item in frontier_sources}
    cross_family_routes = rank_cross_family_routes(chapter_code, runtime, source_ids, config["hubs"], limit)
    zero_point_routes = rank_zero_point_routes(runtime, source_ids, config["hubs"], limit)
    existing_draft = existing_manuscript_context(paths["existing_manuscript_draft"])
    cell_fill_map, open_cells = build_cell_fill_map(chapter_code, frontier_sources, existing_draft)
    duplicate_groups = duplicate_warnings(frontier_sources)
    obligations = witness_obligations(open_cells, duplicate_groups, chapter_code)
    order = drafting_order(chapter_code, frontier_sources, cross_family_routes, open_cells, existing_draft)

    return {
        "query_type": "chapter-pack",
        "query_ref": chapter_code,
        "chapter_code": chapter_code,
        "resolved_documents": [
            {
                "id": item["id"],
                "display_name": item["display_name"],
                "family": item["family"],
                "family_label": item.get("family_label"),
                "element": item["element"],
                "gate": item["gate"],
                "source_layer": item["source_layer"],
                "relative_path": item["relative_path"],
            }
            for item in frontier_sources[:limit]
        ],
        "summary": {
            "status": "resolved",
            "title": f"{chapter.addr} frontier compiler",
            "detail": f"{len(frontier_sources)} ranked frontier sources, {len(open_cells)} open cells, live docs {'BLOCKED' if live_docs_blocked else 'PASS'}",
        },
        "results": {
            "frontier_bundle_path": str(paths["frontier_bundle"]),
            "evidence_pack_path": str(paths["evidence_pack"]),
            "drafting_prep_path": str(paths["drafting_prep"]),
            "chapter_tile_path": str(paths["chapter_tile"]),
            "frontier_sources": frontier_sources[:limit],
            "cross_family_routes": cross_family_routes[:limit],
            "zero_point_routes": zero_point_routes[:limit],
            "cell_fill_map": cell_fill_map,
            "open_cells": open_cells,
            "drafting_order": order,
            "duplicate_source_warnings": duplicate_groups,
            "witness_obligations": obligations,
            "manuscript_handoff_path": str(paths["manuscript_handoff"]),
            "existing_manuscript_draft_path": existing_draft["path"],
            "existing_manuscript_draft_present": existing_draft["exists"],
        },
        "counts": {
            "frontier_source_count": len(frontier_sources),
            "cross_family_route_count": len(cross_family_routes),
            "zero_point_route_count": len(zero_point_routes),
            "cell_count": len(cell_fill_map),
            "open_cell_count": len(open_cells),
            "candidate_cell_count": len(cell_fill_map) - len(open_cells),
        },
        "live_docs_blocked": live_docs_blocked,
        "manifest_refs": {
            "network_manifest": str(paths["network_manifest"]),
            "ordered_pair_matrix": str(paths["ordered_pair_matrix"]),
            "facet_index": str(paths["facet_index"]),
            "zero_point_index": str(paths["zero_point_index"]),
            "compiler_manifest": str(paths["compiler_manifest"]),
        },
    }


def render_route_lines(routes: list[dict]) -> list[str]:
    if not routes:
        return ["- None"]
    label_map: dict[str, set[str]] = defaultdict(set)
    for route in routes:
        label_map[route["src_display_name"]].add(route["src_id"])
        label_map[route["dst_display_name"]].add(route["dst_id"])
    lines = []
    for route in routes:
        src_label = route["src_display_name"]
        dst_label = route["dst_display_name"]
        if len(label_map[src_label]) > 1:
            src_label = f"{src_label} [{route['src_id']}]"
        if len(label_map[dst_label]) > 1:
            dst_label = f"{dst_label} [{route['dst_id']}]"
        lines.append(
            f"- `{src_label}` <-> `{dst_label}` score=`{route.get('route_score', route.get('convergence_score', route['score']))}` kind=`{route.get('kind', 'route')}` shared_chapters=`{', '.join(route['shared_chapters']) or 'none'}` shared_appendices=`{', '.join(route['shared_appendices']) or 'none'}`"
        )
    return lines


def render_frontier_bundle_markdown(payload: dict, chapter_code: str) -> str:
    chapter = chapter_from_code(chapter_code)
    lines = [
        f"# {chapter.addr} Frontier Bundle",
        "",
        f"- Chapter: `{chapter.title}`",
        f"- Live Google Docs: `{'BLOCKED' if payload['live_docs_blocked'] else 'PASS'}`",
        f"- Primary hubs: `{' -> '.join(CHAPTER_PACK_CONFIG[chapter_code]['hubs'])}`",
        f"- Ranked frontier sources: `{payload['counts']['frontier_source_count']}`",
        f"- Open cells: `{payload['counts']['open_cell_count']}`",
        "",
        "## Strongest local frontier sources",
        "",
    ]
    for source in payload["results"]["frontier_sources"]:
        lines.extend(
            [
                f"### {source['display_name']}",
                "",
                f"- Id: `{source['id']}`",
                f"- Source layer: `{source['source_layer']}`",
                f"- Family: `{source['family_label'] or source['family']}`",
                f"- Element / gate: `{source['element']} / {source['gate']}`",
                f"- Rank score: `{source['rank_score']}`",
                f"- Reasons: `{'; '.join(source['reasons']) or 'local chapter routing'}`",
                f"- Appendix route: `{', '.join(source['appendices']) or 'none'}`",
                "",
                (source["excerpt"] or "No excerpt available."),
                "",
            ]
        )
    lines.extend(["## Strongest cross-family routes", "", *render_route_lines(payload["results"]["cross_family_routes"]), "", "## Strongest zero-point-adjacent routes", "", *render_route_lines(payload["results"]["zero_point_routes"]), "", "## Duplicate source warnings", ""])
    warnings = payload["results"]["duplicate_source_warnings"]
    if warnings:
        for warning in warnings:
            lines.append(
                f"- `{warning['display_name']}` docs=`{', '.join(warning['docs'])}` layers=`{', '.join(warning['source_layers'])}`"
            )
    else:
        lines.append("- None")
    lines.extend(["", "## Witness obligations", ""])
    for obligation in payload["results"]["witness_obligations"]:
        lines.append(f"- {obligation}")
    lines.extend(["", "## Recommended drafting order", ""])
    for index, step in enumerate(payload["results"]["drafting_order"], start=1):
        lines.append(f"{index}. {step}")
    return "\n".join(lines)


def render_drafting_prep_markdown(payload: dict, chapter_code: str) -> str:
    chapter = chapter_from_code(chapter_code)
    lines = [
        f"# {chapter.addr} Drafting Prep",
        "",
        f"- Existing manuscript draft present: `{payload['results']['existing_manuscript_draft_present']}`",
        f"- Existing manuscript draft path: `{payload['results']['existing_manuscript_draft_path']}`",
        f"- Manuscript handoff path: `{payload['results']['manuscript_handoff_path']}`",
        "",
        "## Section-order proposal",
        "",
    ]
    for index, step in enumerate(payload["results"]["drafting_order"], start=1):
        lines.append(f"{index}. {step}")
    lines.extend(["", "## Cell status summary", ""])
    lines.append(f"- Candidate cells: `{payload['counts']['candidate_cell_count']}`")
    lines.append(f"- Open cells: `{payload['counts']['open_cell_count']}`")
    lines.extend(["", "## Open cells", ""])
    for cell in payload["results"]["open_cells"]:
        lines.append(f"- `{cell['cell_code']}` `{cell['title']}` -> {cell['summary']}")
    return "\n".join(lines)


def render_chapter_tile_markdown(payload: dict, chapter_code: str) -> str:
    chapter = chapter_from_code(chapter_code)
    config = chapter_config(chapter_code)
    cell_groups = cell_groups_for_chapter(chapter_code)
    lines = [
        f"# {chapter.addr} - {chapter.title}",
        "",
        f"StationHeader: [Arc {chapter.arc} | Rot {chapter.rot} | Lane {chapter.lane} | w={chapter.omega}]",
        f"Workflow role: {chapter.role}",
        f"Primary hubs: {' -> '.join(config['hubs'])}",
        "",
        "## Routing context",
        "",
        f"- Live Google Docs: `{'BLOCKED' if payload['live_docs_blocked'] else 'PASS'}`",
        f"- Ranked frontier sources: `{payload['counts']['frontier_source_count']}`",
        f"- Candidate cells: `{payload['counts']['candidate_cell_count']}`",
        f"- Open cells: `{payload['counts']['open_cell_count']}`",
        f"- Manuscript handoff: `{payload['results']['manuscript_handoff_path']}`",
        "",
        "## Strongest routed sources",
        "",
    ]
    for source in payload["results"]["frontier_sources"][:6]:
        lines.append(f"- `{source['id']}` `{source['display_name']}` family=`{source['family']}` layer=`{source['source_layer']}` score=`{source['rank_score']}`")
    lines.extend(["", "## Crystal tile", ""])
    for lens, lens_info in cell_groups.items():
        lines.extend([f"### Lens {lens} - {lens_info['label']}", ""])
        for facet_index, facet_label in ((1, "Objects"), (2, "Laws"), (3, "Constructions"), (4, "Certificates")):
            lines.extend([f"#### Facet {facet_index} - {facet_label}", ""])
            for atom, *_ in lens_info["facets"][facet_index]:
                cell_code = f"{chapter_code}<{config['station']}>.{lens}{facet_index}.{atom}"
                cell = payload["results"]["cell_fill_map"][cell_code]
                evidence = ", ".join(cell["evidence_refs"]) or "none"
                lines.append(
                    f"- `{cell_code}` `{cell['title']}` status=`{cell['status']}` evidence=`{evidence}`: {cell['summary']}"
                )
            lines.append("")
    return "\n".join(lines)


def render_handoff_markdown(payload: dict, chapter_code: str) -> str:
    chapter = chapter_from_code(chapter_code)
    existing_path = payload["results"]["existing_manuscript_draft_path"]
    if payload["results"]["existing_manuscript_draft_present"]:
        purpose_line = f"This handoff is additive. It does not replace the existing `{chapter.title}` manuscript draft. It packages the strongest local evidence, bridge routes, and open obligations into one prose-ready intake for the final-drafter lane."
    else:
        purpose_line = f"This handoff is additive and becomes the first prose-ready scaffold for `{chapter.title}` because no existing manuscript draft was found. It packages the strongest local evidence, bridge routes, and open obligations into one drafting intake for the final-drafter lane."
    lines = [
        f"# {chapter.addr} Manuscript Handoff",
        "",
        f"- Target chapter: `{chapter.title}`",
        f"- Existing manuscript draft: `{existing_path}`",
        f"- Live Google Docs: `{'BLOCKED' if payload['live_docs_blocked'] else 'PASS'}`",
        "",
        "## Purpose",
        "",
        purpose_line,
        "",
        "## Recommended section order",
        "",
    ]
    for index, step in enumerate(payload["results"]["drafting_order"], start=1):
        lines.append(f"{index}. {step}")
    lines.extend(["", "## Highest-yield source stack", ""])
    for source in payload["results"]["frontier_sources"]:
        lines.append(
            f"- `{source['display_name']}` [{source['id']}] family=`{source['family']}` layer=`{source['source_layer']}` reasons=`{'; '.join(source['reasons']) or 'chapter routing'}`"
        )
    lines.extend(["", "## Cross-family bridges worth weaving into prose", ""])
    lines.extend(render_route_lines(payload["results"]["cross_family_routes"]))
    lines.extend(["", "## Zero-point-adjacent bridges", ""])
    lines.extend(render_route_lines(payload["results"]["zero_point_routes"]))
    lines.extend(["", "## OPEN obligations to preserve honestly", ""])
    for cell in payload["results"]["open_cells"]:
        lines.append(f"- `{cell['cell_code']}` `{cell['title']}` -> {cell['next_witness']}")
    lines.extend(["", chapter.title])
    return "\n".join(lines)


def write_chapter_pack_artifacts(active_root: Path, self_actualize_root: Path, payload: dict, chapter_code: str) -> dict:
    paths = chapter_paths(active_root, self_actualize_root, chapter_code)
    write_json(paths["evidence_pack"], payload)
    write_text(paths["frontier_bundle"], render_frontier_bundle_markdown(payload, chapter_code))
    write_text(paths["drafting_prep"], render_drafting_prep_markdown(payload, chapter_code))
    write_text(paths["chapter_tile"], render_chapter_tile_markdown(payload, chapter_code))
    write_text(paths["manuscript_handoff"], render_handoff_markdown(payload, chapter_code))

    chapter_entry = {
        "chapter_code": chapter_code,
        "frontier_bundle": str(paths["frontier_bundle"]),
        "evidence_pack": str(paths["evidence_pack"]),
        "drafting_prep": str(paths["drafting_prep"]),
        "chapter_tile": str(paths["chapter_tile"]),
        "manuscript_handoff": str(paths["manuscript_handoff"]),
        "existing_manuscript_draft": payload["results"]["existing_manuscript_draft_path"],
        "candidate_cell_count": payload["counts"]["candidate_cell_count"],
        "open_cell_count": payload["counts"]["open_cell_count"],
    }
    if paths["compiler_manifest"].exists():
        manifest = load_json(paths["compiler_manifest"])
    else:
        manifest = {
            "generated_at": utc_now(),
            "compiler_ready": True,
            "live_docs_blocked": payload["live_docs_blocked"],
            "chapter_packs": [],
        }
    manifest["generated_at"] = utc_now()
    manifest["compiler_ready"] = True
    manifest["live_docs_blocked"] = payload["live_docs_blocked"]
    merged = [item for item in manifest.get("chapter_packs", []) if item.get("chapter_code") != chapter_code]
    merged.append(chapter_entry)
    merged.sort(key=lambda item: item["chapter_code"])
    manifest["chapter_packs"] = merged
    write_json(paths["compiler_manifest"], manifest)

    if paths["network_manifest"].exists():
        network_manifest = load_json(paths["network_manifest"])
        network_manifest["chapter_frontier_compiler_ready"] = True
        chapter_targets = sorted({*network_manifest.get("chapter_pack_targets", []), chapter_code})
        network_manifest["chapter_pack_targets"] = chapter_targets
        network_manifest["chapter_frontier_manifest"] = "06_RUNTIME/13_chapter_frontier_manifest.json"
        write_json(paths["network_manifest"], network_manifest)

    return manifest


def compile_and_write_chapter_pack(
    active_root: Path,
    build_root: Path,
    self_actualize_root: Path,
    records: list[dict],
    chapter_code: str,
    live_docs_blocked: bool,
    limit: int = DEFAULT_LIMIT,
) -> tuple[dict, dict]:
    payload = build_frontier_payload(active_root, build_root, self_actualize_root, records, chapter_code, live_docs_blocked, limit=limit)
    manifest = write_chapter_pack_artifacts(active_root, self_actualize_root, payload, chapter_code)
    return payload, manifest
