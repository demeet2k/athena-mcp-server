#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

from canonical_manuscript_builder import DEFAULT_MANIFEST, build_manuscript_volumes
from chapter_frontier_compiler import CHAPTER_FRONTIER_CODES, cell_groups_for_chapter, chapter_from_code
from nervous_system_core import presentation_name, utc_now, write_json, write_text


PROJECT_ROOT = Path(__file__).resolve().parent
ACTIVE_ROOT = PROJECT_ROOT / "ACTIVE_NERVOUS_SYSTEM"
SELF_ACTUALIZE_ROOT = PROJECT_ROOT.parent / "self_actualize"
SECTIONS_DIR = SELF_ACTUALIZE_ROOT / "manuscript_sections"
LEGACY_DIR = SECTIONS_DIR / "alternates" / "frontier_quartet_legacy"
FRONTIER_MANIFEST_PATH = ACTIVE_ROOT / "06_RUNTIME" / "13_chapter_frontier_manifest.json"
DRAFT_MANIFEST_PATH = ACTIVE_ROOT / "06_RUNTIME" / "14_frontier_quartet_draft_manifest.json"
FULL_STACK_MANIFEST_PATH = ACTIVE_ROOT / "06_RUNTIME" / "12_full_stack_manifest.json"
README_PATH = ACTIVE_ROOT / "README.md"
LIVE_DOCS_GATE_PATH = ACTIVE_ROOT / "00_RECEIPTS" / "00_live_docs_gate_status.md"

CHAPTER_ORDER = ["Ch12", "Ch03", "Ch10", "Ch14"]
LENS_ORDER = ("S", "F", "C", "R")
FACETS = (
    ("1", "Objects"),
    ("2", "Laws"),
    ("3", "Constructions"),
    ("4", "Certificates"),
)
FACET_LABELS = {int(index): label for index, label in FACETS}

CANONICAL_TARGETS = {
    "Ch03": "003_ch03_truth_corridors_and_witness_discipline.md",
    "Ch10": "010_ch10_multi_lens_solution_construction.md",
    "Ch12": "012_ch12_legality_certificates_and_closure.md",
    "Ch14": "014_ch14_migration_versioning_and_pulse_retro_weaving.md",
}

ARCHIVE_SOURCE_LABELS = {
    "Ch03": "handoff_source",
    "Ch10": "previous_canonical_draft",
    "Ch12": "previous_canonical_draft",
    "Ch14": "previous_canonical_draft",
}

MASTER_EQUATIONS = {
    "Ch03": r"\boxed{\mathrm{LawfulCorridor}(x)\iff \mathrm{Witnessed}(x)\land \mathrm{Admissible}(x)\land \mathrm{Replayable}(x)\land (\mathrm{AMBIG}(x)\Rightarrow \mathrm{Abstain}(x))}",
    "Ch10": r"\boxed{\mathrm{LawfulSolution}(x)\iff \mathrm{MultiLens}(x)\land \mathrm{Constructed}(x)\land \mathrm{Routed}(x)\land \mathrm{Witnessed}(x)\land \mathrm{Replayable}(x)}",
    "Ch12": r"\boxed{\mathrm{LawfulClosure}(x)\iff \mathrm{Boundary}(x)\land \mathrm{Transport}(x)\land \mathrm{Truth}(x)\land \mathrm{Quarantine}(x)\land \mathrm{Replay}(x)}",
    "Ch14": r"\boxed{\mathrm{LawfulMigration}(x)\iff \mathrm{Delta}(x)\land \mathrm{Compat}(x)\land \mathrm{Rollback}(x)\land \mathrm{Replayable}(x)\land \mathrm{RetroWeave}(x)}",
}

CHAPTER_OPENINGS = {
    "Ch03": "Truth corridors are the first place where the manuscript refuses to confuse route with right. A corridor becomes lawful only when a route carries admissibility, witness discipline, and deterministic replay strongly enough to survive ambiguity without collapsing into guesswork.",
    "Ch10": "Multi-lens construction is the first chapter in which routed evidence becomes a real answer object instead of a promising pile of fragments. The work here is not to accumulate perspectives, but to prove that distinct lenses can be coupled into one solution without tearing witness, route, and replay apart.",
    "Ch12": "Legality and closure are the manuscript's answer to the question of how a living system stops without lying. This chapter defines the conditions under which a boundary, a transport edge, a truth corridor, a quarantine surface, and a replay capsule can be recognized as one closure object rather than five disconnected safeguards.",
    "Ch14": "Migration and retro weaving solve the continuity problem that appears once a lawful system begins to move. The chapter is not about version tags as metadata alone; it is about how deltas, compat matrices, rollback law, and replay capsules keep a moving field from dissolving into amnesia.",
}

CHAPTER_CLOSINGS = {
    "Ch03": "The result is a chapter in which corridors cease to be mere passages and become ethical-computational objects. A route is no longer promoted because it exists; it is promoted because witness, admissibility, and replay have made it safe to trust.",
    "Ch10": "The result is a solution architecture rather than a collection of views. Once the four lenses agree on one answer object, construction is no longer improvisation; it is lawful synthesis with a stable return path.",
    "Ch12": "The result is a closure law that does not confuse silence with safety. A chapter closes only when separation, transport, truth, quarantine, and replay converge into one certificate-bearing event.",
    "Ch14": "The result is a migration discipline in which movement preserves memory rather than consuming it. Versioning, rollback, and retro weaving become the means by which change remains accountable to its own history.",
}

LENS_PURPOSES = {
    "S": "fixes the object basis and the invariant frame before anything is allowed to move",
    "F": "turns the chapter into lawful transport and bridge machinery",
    "C": "names the truth, quarantine, and governance pressures that keep the chapter honest under load",
    "R": "binds the whole construction back to replay, verification, and certificate-bearing return",
}

FACET_OPENINGS = {
    "Objects": "The object layer carries the irreducible entities without which the chapter cannot even state its own problem.",
    "Laws": "The law layer states the admissibility constraints that keep those objects from becoming decorative rather than binding.",
    "Constructions": "The construction layer operationalizes the chapter so its claims can be executed, not merely admired.",
    "Certificates": "The certificate layer seals the chapter's claims with replayable closure and makes promotion lawful.",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Draft the frontier quartet into canonical manuscript sections.")
    parser.add_argument("--chapter", required=True, choices=[*CHAPTER_FRONTIER_CODES, "all"])
    parser.add_argument("--write-master", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser.parse_args()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_frontier_manifest() -> dict:
    return load_json(FRONTIER_MANIFEST_PATH)


def chapter_entry(frontier_manifest: dict, chapter_code: str) -> dict:
    for item in frontier_manifest["chapter_packs"]:
        if item["chapter_code"] == chapter_code:
            return item
    raise KeyError(f"Missing chapter pack in frontier manifest: {chapter_code}")


def load_chapter_payload(entry: dict) -> dict:
    return load_json(Path(entry["evidence_pack"]))


def clean_sentence(text: str) -> str:
    cleaned = text.replace("`", "")
    cleaned = cleaned.replace("CANDIDATE", "").replace("OPEN - ", "")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def archive_source(chapter_code: str, payload: dict) -> tuple[str, str]:
    LEGACY_DIR.mkdir(parents=True, exist_ok=True)
    if payload["results"]["existing_manuscript_draft_present"]:
        source_path = Path(payload["results"]["existing_manuscript_draft_path"])
    else:
        source_path = Path(payload["results"]["manuscript_handoff_path"])
    archive_name = f"{chapter_code.lower()}_{ARCHIVE_SOURCE_LABELS[chapter_code]}__{source_path.name}"
    archive_path = LEGACY_DIR / archive_name
    shutil.copy2(source_path, archive_path)
    return str(source_path), str(archive_path)


def atom_title(title: str, lens_label: str) -> str:
    if title.startswith(f"{lens_label} "):
        return title[len(lens_label) + 1 :]
    return title


def evidence_lookup(payload: dict) -> dict[str, dict]:
    return {item["id"]: item for item in payload["results"]["frontier_sources"]}


def render_cell_sentence(cell: dict, chapter_title: str, lookup: dict[str, dict], lens_label: str) -> str:
    title = atom_title(cell["title"], lens_label)
    evidence_names = [
        presentation_name(lookup[evidence_id]["display_name"])
        for evidence_id in cell["evidence_refs"]
        if evidence_id in lookup
    ]
    evidence_phrase = ""
    if evidence_names:
        evidence_phrase = f" The strongest local witnesses are {', '.join(evidence_names[:2])}."

    if cell["facet_index"] == 1:
        return f"{title} is one of the load-bearing entities grounding {chapter_title}.{evidence_phrase}".strip()
    if cell["facet_index"] == 2:
        return f"{title} states the rule that keeps {chapter_title} lawful, typed, and witness-safe.{evidence_phrase}".strip()
    if cell["facet_index"] == 3:
        return f"{title} operationalizes {chapter_title} as executable machinery rather than inert description.{evidence_phrase}".strip()
    return f"{title} seals the corresponding object, law, or construction for {chapter_title} with replayable closure.{evidence_phrase}".strip()


def render_facet_paragraph(
    chapter_title: str,
    lens: str,
    facet_index: int,
    payload: dict,
    groups: dict[str, dict],
    lookup: dict[str, dict],
) -> str:
    lens_label = groups[lens]["label"]
    facet_label = FACET_LABELS[facet_index]
    cells = []
    for atom in ("a", "b", "c", "d"):
        cell_code = next(
            key for key, value in payload["results"]["cell_fill_map"].items()
            if value["lens"] == lens and value["facet_index"] == facet_index and value["atom"] == atom
        )
        cells.append(payload["results"]["cell_fill_map"][cell_code])
    titles = [atom_title(cell["title"], lens_label) for cell in cells]
    lead = f"{FACET_OPENINGS[facet_label]} In the {lens_label} lens these four terms are {', '.join(titles[:-1])}, and {titles[-1]}."
    body = " ".join(render_cell_sentence(cell, chapter_title, lookup, lens_label) for cell in cells)
    return f"{lead} {body}".strip()


def route_sentence(routes: list[dict], label: str) -> str:
    if not routes:
        return f"The {label} field is currently empty under the local-only evidence regime."
    first = routes[0]
    src = presentation_name(first["src_display_name"])
    dst = presentation_name(first["dst_display_name"])
    return f"The highest-yield {label} in the present corpus is the route {src} <-> {dst}, which concentrates the chapter's current bridge pressure into one reusable transition surface."


def render_chapter_markdown(chapter_code: str, payload: dict) -> str:
    chapter = chapter_from_code(chapter_code)
    groups = cell_groups_for_chapter(chapter_code)
    lookup = evidence_lookup(payload)
    sources = [presentation_name(item["display_name"]) for item in payload["results"]["frontier_sources"][:3]]
    source_clause = ", ".join(sources) if sources else "the local frontier stack"

    lines = [
        f"# CHAPTER {chapter.index}: {chapter.title.upper()}",
        "",
        f"## {CHAPTER_OPENINGS[chapter_code]}",
        "",
        f"**Station:** `<{chapter.station}>` - Arc {chapter.arc}, {chapter.lane} rail",
        f"**Primary hubs:** `{' -> '.join(chapter.hubs)}`",
        "",
        "## Chapter Function",
        "",
        f"{CHAPTER_OPENINGS[chapter_code]} The present draft is built from the chapter-pack evidence stack rather than from live Google Docs ingress, so its claims are disciplined by the strongest currently replayable local witnesses: {source_clause}.",
        "",
        "## Master Equation",
        "",
        "$$",
        MASTER_EQUATIONS[chapter_code],
        "$$",
        "",
        "## Witness and Bridge Frame",
        "",
        f"The current witness stack is led by {source_clause}. {route_sentence(payload['results']['cross_family_routes'], 'cross-family bridge')} {route_sentence(payload['results']['zero_point_routes'], 'zero-point bridge')}",
        "",
    ]

    for lens_pos, lens in enumerate(LENS_ORDER, start=1):
        lens_label = groups[lens]["label"]
        lines.extend(
            [
                f"## {chapter.index}.{lens_pos} {lens_label} Lens",
                "",
                f"The {lens_label} lens of {chapter.title} {LENS_PURPOSES[lens]}.",
                "",
            ]
        )
        for facet_index in range(1, 5):
            facet_label = FACET_LABELS[facet_index]
            lines.extend(
                [
                    f"### {chapter.index}.{lens_pos}.{facet_index} {facet_label}",
                    "",
                    render_facet_paragraph(chapter.title, lens, facet_index, payload, groups, lookup),
                    "",
                ]
            )

    lines.extend(
        [
            "## Promotion Ledger",
            "",
            f"All `64` chapter cells are presently carried as candidate-ready rather than open. The drafting discipline therefore shifts from gap-filling to promotion: tighten proofs, preserve the strongest bridge routes, and ensure that every promoted statement remains consistent with the chapter's witness and replay obligations.",
            "",
            CHAPTER_CLOSINGS[chapter_code],
            "",
            chapter.title,
        ]
    )
    return "\n".join(lines)


def write_canonical_section(chapter_code: str, markdown: str) -> Path:
    target = SECTIONS_DIR / CANONICAL_TARGETS[chapter_code]
    write_text(target, markdown)
    return target


def section_word_count(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").split())


def replace_or_append_section(text: str, heading: str, body_lines: list[str]) -> str:
    block = "\n".join([heading, "", *body_lines]).rstrip()
    pattern = re.compile(rf"\n{re.escape(heading)}\n(?:.*?)(?=\n## |\Z)", re.S)
    if heading in text:
        return pattern.sub("\n" + block + "\n", text).rstrip() + "\n"
    return text.rstrip() + "\n\n" + block + "\n"


def update_readme(draft_manifest: dict) -> None:
    text = README_PATH.read_text(encoding="utf-8")
    body = [
        f"- Status: `{draft_manifest['status']}`",
        f"- Chapters drafted: `{', '.join(draft_manifest['drafted_chapters'])}`",
        f"- Canonical section files: `{', '.join(Path(item['canonical_section_path']).name for item in draft_manifest['chapters'])}`",
        f"- Master manuscript rebuilt: `{draft_manifest['master_manuscript']['rebuilt']}`",
        f"- Supplements volume rebuilt: `{draft_manifest['supplements_manuscript']['rebuilt']}`",
        f"- Live Google Docs: `{'BLOCKED' if draft_manifest['live_docs_blocked'] else 'PASS'}`",
    ]
    updated = replace_or_append_section(text, "## Frontier Quartet Draft State", body)
    write_text(README_PATH, updated)


def update_full_stack_manifest(draft_manifest: dict) -> None:
    manifest = load_json(FULL_STACK_MANIFEST_PATH)
    manifest.setdefault("layers", {})
    manifest["layers"]["frontier_quartet_draft_conveyor"] = {
        "manifest": "06_RUNTIME/14_frontier_quartet_draft_manifest.json",
        "status": draft_manifest["status"],
        "drafted_chapters": draft_manifest["drafted_chapters"],
        "canonical_section_files": [Path(item["canonical_section_path"]).name for item in draft_manifest["chapters"]],
        "master_manuscript": draft_manifest["master_manuscript"]["output_path"],
        "supplements_manuscript": draft_manifest["supplements_manuscript"]["output_path"],
        "live_docs_blocked": draft_manifest["live_docs_blocked"],
    }
    write_json(FULL_STACK_MANIFEST_PATH, manifest)


def draft_one(chapter_code: str, frontier_manifest: dict) -> dict:
    entry = chapter_entry(frontier_manifest, chapter_code)
    payload = load_chapter_payload(entry)
    source_path, archive_path = archive_source(chapter_code, payload)
    markdown = render_chapter_markdown(chapter_code, payload)
    target_path = write_canonical_section(chapter_code, markdown)
    return {
        "chapter_code": chapter_code,
        "canonical_section_path": str(target_path),
        "source_artifacts": {
            "evidence_pack": entry["evidence_pack"],
            "drafting_prep": entry["drafting_prep"],
            "chapter_tile": entry["chapter_tile"],
            "handoff": entry["manuscript_handoff"],
            "existing_draft": entry["existing_manuscript_draft"],
        },
        "archived_source_path": archive_path,
        "archived_from": source_path,
        "word_count": section_word_count(target_path),
        "open_cell_count": entry["open_cell_count"],
        "candidate_cell_count": entry["candidate_cell_count"],
        "status": "drafted",
    }


def build_draft_manifest(chapters: list[dict], volume_receipt: dict | None, live_docs_error: str) -> dict:
    spine_receipt = (volume_receipt or {}).get("volumes", {}).get("spine")
    supplements_receipt = (volume_receipt or {}).get("volumes", {}).get("supplements")
    return {
        "generated_at": utc_now(),
        "status": "drafted",
        "draft_order": CHAPTER_ORDER,
        "drafted_chapters": [item["chapter_code"] for item in chapters],
        "live_docs_blocked": True,
        "live_docs_error": live_docs_error,
        "canonical_manifest": str(DEFAULT_MANIFEST),
        "chapters": chapters,
        "master_manuscript": {
            "rebuilt": bool(spine_receipt),
            **(spine_receipt or {
                "manifest_path": str(DEFAULT_MANIFEST),
                "output_path": str(SELF_ACTUALIZE_ROOT / "VOID_MANUSCRIPT_MASTER.md"),
                "entry_count": 0,
                "entry_files": [],
            }),
        },
        "supplements_manuscript": {
            "rebuilt": bool(supplements_receipt),
            **(supplements_receipt or {
                "manifest_path": str(DEFAULT_MANIFEST),
                "output_path": str(SELF_ACTUALIZE_ROOT / "VOID_MANUSCRIPT_SUPPLEMENTS.md"),
                "entry_count": 0,
                "entry_files": [],
            }),
        },
    }


def main() -> int:
    args = parse_args()
    frontier_manifest = load_frontier_manifest()
    requested = CHAPTER_ORDER if args.chapter == "all" else [args.chapter]

    drafted = []
    for chapter_code in CHAPTER_ORDER:
        if chapter_code not in requested:
            continue
        drafted.append(draft_one(chapter_code, frontier_manifest))

    volume_receipt = None
    if args.write_master:
        volume_receipt = build_manuscript_volumes(DEFAULT_MANIFEST)

    live_docs_error = "Missing OAuth client file: credentials.json"
    if LIVE_DOCS_GATE_PATH.exists():
        gate_text = LIVE_DOCS_GATE_PATH.read_text(encoding="utf-8")
        if "Missing OAuth client file" in gate_text:
            live_docs_error = next(
                (line.strip() for line in gate_text.splitlines() if "Missing OAuth client file" in line),
                live_docs_error,
            )

    draft_manifest = build_draft_manifest(drafted, volume_receipt, live_docs_error)
    write_json(DRAFT_MANIFEST_PATH, draft_manifest)
    update_readme(draft_manifest)
    update_full_stack_manifest(draft_manifest)

    if args.as_json:
        print(json.dumps(draft_manifest, indent=2))
    else:
        print(f"Wrote frontier quartet draft manifest: {DRAFT_MANIFEST_PATH}")
        print(f"Drafted chapters: {', '.join(draft_manifest['drafted_chapters'])}")
        print(f"Master manuscript rebuilt: {draft_manifest['master_manuscript']['rebuilt']}")
        print(f"Supplements volume rebuilt: {draft_manifest['supplements_manuscript']['rebuilt']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
