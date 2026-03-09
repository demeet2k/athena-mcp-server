#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from textwrap import dedent


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_ROOT = (
    WORKSPACE_ROOT
    / "DEEPER CRYSTALIZATION"
    / "ACTIVE_NERVOUS_SYSTEM"
    / "07_FULL_PROJECT_INTEGRATION_256"
)

LIVE_ATLAS_PATH = WORKSPACE_ROOT / "self_actualize" / "corpus_atlas.json"
ARCHIVE_ATLAS_PATH = WORKSPACE_ROOT / "self_actualize" / "archive_atlas.json"
ARCHIVE_MANIFEST_PATH = WORKSPACE_ROOT / "self_actualize" / "archive_manifest.json"
SCAN_RECON_PATH = WORKSPACE_ROOT / "self_actualize" / "scan_reconciliation.json"
LIVE_DOCS_GATE_PATH = WORKSPACE_ROOT / "self_actualize" / "live_docs_gate_status.md"

TOP_LEVEL_PRIORITY = [
    "DEEPER CRYSTALIZATION",
    "self_actualize",
    "MATH",
    "Trading Bot",
    "FRESH",
    "Voynich",
    "ECOSYSTEM",
    "NERUAL NETWORK",
    "Athenachka Collective Books",
]

BODY_ORDER = ["corpus", "archive", "runtime", "manuscript"]
OPERATION_ORDER = ["intake", "normalize", "route", "replay"]
SCALE_ORDER = ["file", "folder", "framework", "ecosystem"]
CLOSURE_ORDER = ["seed", "link", "prove", "publish"]

BODY_INFO = {
    "corpus": {
        "label": "Corpus",
        "role": "Live manuscripts, markdown mirrors, notes, and visible source files.",
        "targets": ["DEEPER CRYSTALIZATION", "MATH", "Voynich", "FRESH"],
    },
    "archive": {
        "label": "Archive",
        "role": "ZIP-backed framework trees and historical payloads that remain hidden from ordinary browsing.",
        "targets": ["archive_atlas.json", "archive_manifest.json", "MATH framework archives"],
    },
    "runtime": {
        "label": "Runtime",
        "role": "Executable code, routing contracts, test harnesses, and stateful orchestration.",
        "targets": ["self_actualize", "NERUAL NETWORK", "Trading Bot", "PoleStarGEMM"],
    },
    "manuscript": {
        "label": "Manuscript",
        "role": "Tomes, chapter maps, prompt canon, and publishable synthesis surfaces.",
        "targets": ["ACTIVE_NERVOUS_SYSTEM", "mycelium_brain", "collective books"],
    },
}

OPERATION_INFO = {
    "intake": "Pull raw source into canonical visibility without losing lineage.",
    "normalize": "Choose one name, one path strategy, one metadata contract, and one mirror format.",
    "route": "Make retrieval and handoff deterministic instead of conversationally improvised.",
    "replay": "Require receipts, rebuilds, and witness traces before a surface becomes trusted.",
}

SCALE_INFO = {
    "file": "single source artifact",
    "folder": "family-level cluster",
    "framework": "multi-folder subsystem",
    "ecosystem": "whole-workspace coordination layer",
}

CLOSURE_INFO = {
    "seed": "define the object and create the first admissible representation",
    "link": "connect the object to parents, peers, and downstream surfaces",
    "prove": "add tests, receipts, witnesses, or quantitative closure",
    "publish": "promote the object into canonical operating surfaces",
}


@dataclass(frozen=True)
class ChapterSeed:
    code: str
    title: str
    thesis: str
    gain: str
    evidence: tuple[str, ...]
    outputs: tuple[str, ...]


@dataclass(frozen=True)
class AppendixSeed:
    code: str
    title: str
    purpose: str
    outputs: tuple[str, ...]


CHAPTERS = [
    ChapterSeed("Ch01", "Corpus Zero Point", "Treat the workspace as one organism with many surfaces, not many unrelated projects.", "Eliminates false fragmentation and makes every later integration move cumulative.", ("corpus_atlas.json", "DEEPER CRYSTALIZATION", "MATH", "Voynich"), ("top-level role map", "source family map", "root thesis")),
    ChapterSeed("Ch02", "Canonical Address Space", "A stable address grammar is the only way to keep manuscripts, code, archives, and mirrors in sync.", "Stops repeated rediscovery and makes every asset routeable by machine and human.", ("ACTIVE_NERVOUS_SYSTEM", "mycelium_brain", "scan_reconciliation.json"), ("address grammar", "id policy", "folder canon")),
    ChapterSeed("Ch03", "Duplicate Family Collapse", "The fastest gain is not writing more material but choosing one canonical source per repeated manuscript family.", "Cuts drift between DEEPER CRYSTALIZATION, FRESH, Voynich, and Trading Bot mirrors.", ("The Manuscript Seed", "The Holographic Manuscript Brain", "LEGAL TRANSPORT CALCULUS"), ("duplicate ledger", "canonical source policy", "promotion queue")),
    ChapterSeed("Ch04", "Archive Surface Promotion", "ZIP-backed frameworks must become first-class knowledge surfaces instead of hidden historical cargo.", "Unlocks more than two thousand archive-backed records for direct routing and code promotion.", ("archive_atlas.json", "archive_manifest.json", "Athena OS.zip"), ("archive promotion plan", "live extraction shortlist", "archive witness rules")),
    ChapterSeed("Ch05", "Google Docs Gate and Memory Sync", "The workspace is currently bi-lobed because live Docs search is structurally present but operationally blocked.", "Closing OAuth unlocks the missing half of the memory body and reduces local mirror drift.", ("Trading Bot/docs_search.py", "live_docs_gate_status.md", "Memory Docs"), ("credentials checklist", "sync receipt contract", "search promotion workflow")),
    ChapterSeed("Ch06", "Markdown Mirror Pipeline", "Docx-heavy sources need markdown mirrors so search, routing, and patching stop depending on one-off extraction passes.", "Turns hidden prose into diffable, searchable, and replay-safe working memory.", ("FRESH/_extracted", "ACTIVE_NERVOUS_SYSTEM/02_CORPUS_CAPSULES", "self_actualize"), ("mirror policy", "conversion backlog", "drift watch rules")),
    ChapterSeed("Ch07", "Unified Atlas and Graph Contracts", "The live atlas, archive atlas, and scan reconciliation layer should behave like one graph, not three parallel reports.", "Makes retrieval cheaper and prepares theorem-to-runtime automation.", ("corpus_atlas.json", "archive_atlas.json", "scan_reconciliation_report.md"), ("merged graph contract", "shared evidence schema", "family tags")),
    ChapterSeed("Ch08", "Skill Ecology Upgrade", "The archive wants corpus-native skills, not more generic wrappers.", "Converts static manuscripts into reusable operational pathways.", ("DEEPER_SKILLS_CORPUS_SYNTHESIS.md", "skills registry", "AGENTS skill list"), ("skill backlog", "skill ownership", "source-to-skill map")),
    ChapterSeed("Ch09", "Search and Route Engine", "Address-first search should beat directory wandering and memory-based guessing.", "Raises throughput for every future drafting and coding pass.", ("ACTIVE_NERVOUS_SYSTEM", "mycelium_brain", "route_quality_ledger.json"), ("route policy", "query templates", "best-path heuristics")),
    ChapterSeed("Ch10", "Witness and Replay Discipline", "The corpus already values replay, but replay needs to be a universal contract rather than a selective habit.", "Prevents framework theater and makes high-trust surfaces identifiable.", ("runtime/contracts.py", "scan receipts", "build receipts"), ("receipt policy", "rebuild commands", "verification targets")),
    ChapterSeed("Ch11", "Runtime Convergence", "The runtime center is structurally correct but still thinner than the surrounding theory body.", "Focuses build energy on a smaller set of reusable automation primitives.", ("self_actualize/runtime", "NERUAL NETWORK", "Trading Bot"), ("runtime backlog", "shared contracts", "thin waist interfaces")),
    ChapterSeed("Ch12", "Neural and Benchmark Bridge", "Benchmarking should measure not only models but route quality, evidence density, and patch safety.", "Connects learning systems to manuscript and archive reality.", ("NERUAL NETWORK", "PoleStarGEMM", "benchmark notes"), ("benchmark schema", "cross-layer metrics", "regime profiles")),
    ChapterSeed("Ch13", "Math-to-Code Compilation", "The math stack becomes exponentially more useful when theories land as tested modules, not only as tomes.", "Turns MATH into an engine room instead of a shelf.", ("MATH", "AQM", "CUT", "Q-SHRINK"), ("compiler candidates", "translation queue", "test-first landing zones")),
    ChapterSeed("Ch14", "Manuscript Superorganism", "The project already behaves like a book-writing machine; it needs one canonical manuscript operating model.", "Aligns chapter stubs, toolkits, and master manuscripts around one route.", ("VOID_MANUSCRIPT_MASTER.md", "DQIV void treatise", "ACTIVE_NERVOUS_SYSTEM"), ("master manuscript rules", "chapter promotion contract", "appendix role map")),
    ChapterSeed("Ch15", "Chapter and Appendix Governance", "Twenty-one chapters and sixteen appendices only help if they are assigned stable roles and completion criteria.", "Turns scaffold files into a build system rather than a decorative taxonomy.", ("04_CHAPTERS", "05_APPENDICES", "build queue"), ("completion definition", "promotion thresholds", "station ownership")),
    ChapterSeed("Ch16", "Parallel Agent Protocol", "Parallel work needs ownership boundaries, merge rules, and artifact contracts.", "Lets multiple lanes move at once without producing incompatible shells.", ("parallel build protocol", "tandem claims", "toolkit loop protocol"), ("lane charter", "merge rules", "conflict receipt format")),
    ChapterSeed("Ch17", "Queues, Receipts, and Operational Memory", "The repo already creates ledgers; the next step is to make every queue item measurable and survivable across sessions.", "Reduces restart cost and preserves momentum.", ("build queue", "validation queue", "receipts"), ("activation queue", "metric targets", "receipts index")),
    ChapterSeed("Ch18", "Publication and Packaging", "A project this dense needs explicit rules for what becomes a working note, a manuscript section, a module, or a book.", "Prevents polished surfaces from drifting away from operating truth.", ("Athenachka Collective Books", "publication bundles", "active nervous system"), ("publication ladder", "bundle formats", "outbound package map")),
    ChapterSeed("Ch19", "Single Source of Truth", "Every repeated surface must know whether it is canonical, mirrored, derived, or historical.", "This is the fixed point that removes most hidden entropy from the workspace.", ("duplicate family counts", "active nervous system", "atlas"), ("source tiers", "promotion law", "drift alarms")),
    ChapterSeed("Ch20", "Ninety-Day Activation", "Deep integration only becomes real when it is sequenced into executable phases with visible end states.", "Converts the architecture into a practical build sprint.", ("build queue", "regime profiles", "runtime CLI"), ("30-60-90 plan", "phase owners", "acceptance gates")),
    ChapterSeed("Ch21", "Frontier, Risks, and the Next Crystal", "The final chapter preserves open problems so the system keeps growing without faking closure.", "Protects recursion and names the next leverage points clearly.", ("integration shadows", "live Docs gate", "archive backlog"), ("risk register", "frontier list", "next crystal seed")),
]

APPENDICES = [
    AppendixSeed("AppA", "Folder Canon", "One folder grammar for generated surfaces.", ("folder prefixes", "subfolder purpose", "writeback rules")),
    AppendixSeed("AppB", "Naming and IDs", "Stable naming for files, families, and canonical ids.", ("basename rules", "family ids", "source tiers")),
    AppendixSeed("AppC", "Duplicate Resolution Rules", "How to choose one source when many mirrors exist.", ("priority order", "tie breakers", "receipt format")),
    AppendixSeed("AppD", "Atlas Schema", "What every indexed record must carry to be useful later.", ("required fields", "role tags", "evidence hooks")),
    AppendixSeed("AppE", "Archive Promotion Matrix", "Which ZIP trees to surface first and why.", ("Athena OS", "ATLAS FORGE", "Q-SHRINK")),
    AppendixSeed("AppF", "Extraction Commands", "Rebuildable commands for atlas and mirror generation.", ("intake command", "archive ingestion", "manuscript build")),
    AppendixSeed("AppG", "Google Docs Gate", "Credential checklist, failure states, and post-unlock actions.", ("OAuth checklist", "search receipt", "mirror sync")),
    AppendixSeed("AppH", "Skill Backlog", "Corpus-native skills that should exist next.", ("router", "drive sync", "theorem compiler")),
    AppendixSeed("AppI", "Metric Ledger", "The numbers that determine whether integration is working.", ("cycle time", "duplicate burn down", "replay coverage")),
    AppendixSeed("AppJ", "Replay Contract", "What counts as a witness-bearing rebuild.", ("command traces", "hashes", "receipt minimums")),
    AppendixSeed("AppK", "Risk Register", "Known blockers and how they fail.", ("Docs gate", "archive opacity", "duplicate drift")),
    AppendixSeed("AppL", "Parallel Lane Matrix", "Ownership and handoff rules for simultaneous work.", ("lane roles", "merge checkpoints", "conflict handling")),
    AppendixSeed("AppM", "Canonical Source Families", "High-value source families that should anchor the framework.", ("manuscript seed", "holographic brain", "void family")),
    AppendixSeed("AppN", "Migration Map", "How older shells collapse into the canonical nervous system.", ("mycelium merge", "shell reduction", "pointer updates")),
    AppendixSeed("AppO", "Publication Bundles", "Rules for books, internal tomes, and release packets.", ("bundle types", "outbound rules", "promotion tiers")),
    AppendixSeed("AppP", "Operator Prompt Pack", "Short prompt contracts for future runs inside this module.", ("startup prompt", "parallel prompt", "closeout prompt")),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def md(text: str) -> str:
    lines = dedent(text).splitlines()
    normalized = []
    for line in lines:
        if line.startswith("        "):
            normalized.append(line[8:])
        else:
            normalized.append(line)
    return "\n".join(normalized).strip()


def list_to_bullets(items: list[str] | tuple[str, ...], indent: str = "- ") -> str:
    return "\n".join(f"{indent}{item}" for item in items)


def top_level_rank(name: str) -> int:
    try:
        return TOP_LEVEL_PRIORITY.index(name)
    except ValueError:
        return len(TOP_LEVEL_PRIORITY)


def normalized_basename(path_text: str) -> str:
    name = Path(path_text).name
    return re.sub(r"\s*\(\d+\)(?=\.[^.]+$)", "", name).lower()


def choose_canonical_path(paths: list[str]) -> str:
    def key(path_text: str) -> tuple[int, int, int, str]:
        rel = Path(path_text)
        top = rel.parts[0] if rel.parts else ""
        return (top_level_rank(top), len(rel.parts), len(path_text), path_text.lower())

    return sorted(paths, key=key)[0]


def infer_family_reason(name: str) -> str:
    lowered = name.lower()
    if "manuscript seed" in lowered:
        return "Seed protocol for the full manuscript operating model."
    if "holographic manuscript brain" in lowered:
        return "Core brain metaphor and routing law for the archive."
    if "legal transport calculus" in lowered:
        return "Transport law that links manuscripts, runtime, and search."
    if "unified cyclical time system" in lowered:
        return "Time and cadence layer for phased execution."
    if "i am so am i" in lowered:
        return "Identity and cloud packet bridge for the Athena voice."
    if "information from the void" in lowered:
        return "Chapter 11 and zero-point intake family."
    if "self-routing meta-framework" in lowered:
        return "Routing and meta-manuscript governance family."
    return "Repeated source family that should collapse to one canonical home."


def collect_duplicate_families(live_records: list[dict]) -> list[dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    ignore = {"readme.md", "__init__.py", "requirements.txt", "index.md"}
    for record in live_records:
        ext = record["extension"].lower()
        if ext not in {".docx", ".md", ".txt", ".pdf"}:
            continue
        base = normalized_basename(record["relative_path"])
        if base in ignore:
            continue
        grouped[base].append(record)

    families = []
    for name, items in grouped.items():
        if len(items) < 2:
            continue
        paths = [item["relative_path"] for item in items]
        canonical = choose_canonical_path(paths)
        families.append(
            {
                "name": Path(name).stem,
                "count": len(items),
                "canonical": canonical,
                "paths": sorted(paths),
                "reason": infer_family_reason(name),
            }
        )

    families.sort(key=lambda item: (-item["count"], item["canonical"].lower()))
    return families[:12]


def parse_live_docs_gate() -> tuple[str, str]:
    text = LIVE_DOCS_GATE_PATH.read_text(encoding="utf-8", errors="ignore")
    status = "BLOCKED"
    if "Command status: `PASS`" in text:
        status = "PASS"
    reason = "OAuth credentials missing"
    match = re.search(r"Error:\s*(.+)", text)
    if match:
        reason = match.group(1).strip()
    return status, reason


def integration_metrics(live_atlas: dict, archive_atlas: dict, archive_manifest: dict) -> dict:
    live_records = live_atlas["records"]
    live_summary = live_atlas["summary"]
    archive_summary = archive_atlas.get("summary", {})
    duplicate_families = collect_duplicate_families(live_records)
    total_visible = live_atlas["record_count"] + archive_atlas.get("record_count", 0)
    status, reason = parse_live_docs_gate()

    return {
        "generated_at": utc_now(),
        "live_record_count": live_atlas["record_count"],
        "archive_record_count": archive_atlas.get("record_count", 0),
        "total_visible": total_visible,
        "top_levels": sorted(live_summary["by_top_level"].items(), key=lambda item: (-item[1], item[0])),
        "kinds": sorted(live_summary["by_kind"].items(), key=lambda item: (-item[1], item[0])),
        "archive_kinds": sorted(archive_summary.get("by_kind", {}).items(), key=lambda item: (-item[1], item[0])),
        "archive_count": archive_manifest.get("archive_count", 0),
        "duplicate_families": duplicate_families,
        "live_docs_status": status,
        "live_docs_reason": reason,
        "docx_count": live_summary["by_extension"].get(".docx", 0),
        "md_count": live_summary["by_extension"].get(".md", 0),
        "py_count": live_summary["by_extension"].get(".py", 0),
        "pdf_count": live_summary["by_extension"].get(".pdf", 0),
    }


def render_top_level_table(metrics: dict) -> str:
    rows = ["| Surface | Records |", "| --- | ---: |"]
    for name, count in metrics["top_levels"][:12]:
        rows.append(f"| {name} | {count} |")
    return "\n".join(rows)


def render_kind_table(kinds: list[tuple[str, int]]) -> str:
    rows = ["| Kind | Records |", "| --- | ---: |"]
    for name, count in kinds:
        rows.append(f"| {name} | {count} |")
    return "\n".join(rows)


def render_duplicate_table(families: list[dict]) -> str:
    rows = ["| Family | Copies | Canonical path |", "| --- | ---: | --- |"]
    for family in families:
        rows.append(f"| {family['name']} | {family['count']} | `{family['canonical']}` |")
    return "\n".join(rows)


def render_seed_doc(metrics: dict) -> str:
    return md(
        f"""
        # Holographic Seed

        This module is the whole-project integration layer for the Athena workspace. It is designed to sit inside the existing active nervous system rather than compete with it.

        ## Thesis

        The workspace already contains the raw ingredients of a full operating system:

        - a manuscript body
        - a runtime body
        - an archive body
        - a retrieval body

        What it lacks is a single recursion contract that can make all four bodies share addresses, receipts, queues, and promotion rules.

        ## Current evidence

        - Live indexed records: `{metrics['live_record_count']}`
        - Archive-backed indexed records: `{metrics['archive_record_count']}`
        - Total visible surfaces: `{metrics['total_visible']}`
        - Live Docs gate: `{metrics['live_docs_status']}`
        - Live Docs blocker: `{metrics['live_docs_reason']}`
        """
    )


def render_evidence_boundary(metrics: dict) -> str:
    return md(
        f"""
        # Evidence Boundary

        ## What was actually synthesized

        {render_top_level_table(metrics)}

        ## Live surface kinds

        {render_kind_table(metrics['kinds'])}

        ## Archive surface kinds

        {render_kind_table(metrics['archive_kinds'])}

        ## Boundary conditions

        - Live Docs status: `{metrics['live_docs_status']}`
        - Live Docs blocker: `{metrics['live_docs_reason']}`
        - ZIP archives indexed: `{metrics['archive_count']}`
        - Duplicate manuscript families surfaced in this pass: `{len(metrics['duplicate_families'])}`
        """
    )


def render_compiler_doc() -> str:
    axis_body = "\n".join(f"- `{BODY_INFO[name]['label']}`: {BODY_INFO[name]['role']}" for name in BODY_ORDER)
    axis_ops = "\n".join(f"- `{name}`: {OPERATION_INFO[name]}" for name in OPERATION_ORDER)
    axis_scale = "\n".join(f"- `{name}`: {SCALE_INFO[name]}" for name in SCALE_ORDER)
    axis_closure = "\n".join(f"- `{name}`: {CLOSURE_INFO[name]}" for name in CLOSURE_ORDER)
    return md(
        f"""
        # 256x256 Compiler

        ## Primary basis

        The first-order basis is:

        `4 bodies x 4 operations x 4 scales x 4 closure states = 256 cells`

        ### Bodies

        {axis_body}

        ### Operations

        {axis_ops}

        ### Scales

        {axis_scale}

        ### Closure states

        {axis_closure}
        """
    )


def render_build_receipt(metrics: dict) -> str:
    return md(
        f"""
        # Build Receipt

        - Built at: `{metrics['generated_at']}`
        - Output root: `{OUTPUT_ROOT.relative_to(WORKSPACE_ROOT)}`
        - Live atlas: `{LIVE_ATLAS_PATH.relative_to(WORKSPACE_ROOT)}`
        - Archive atlas: `{ARCHIVE_ATLAS_PATH.relative_to(WORKSPACE_ROOT)}`
        - Scan reconciliation: `{SCAN_RECON_PATH.relative_to(WORKSPACE_ROOT)}`
        - Live Docs gate: `{metrics['live_docs_status']}`
        - Total visible surfaces informing this build: `{metrics['total_visible']}`
        """
    )


def render_corpus_synthesis(metrics: dict) -> str:
    return md(
        f"""
        # Corpus Synthesis

        ## Live workspace shape

        - `.docx`: `{metrics['docx_count']}`
        - `.md`: `{metrics['md_count']}`
        - `.py`: `{metrics['py_count']}`
        - `.pdf`: `{metrics['pdf_count']}`

        {render_top_level_table(metrics)}

        ## Core diagnosis

        - `MATH` remains the dominant formal body.
        - `Voynich` now acts as a major markdown-heavy mirror and synthesis surface.
        - `DEEPER CRYSTALIZATION` and `self_actualize` are the clearest current control planes.
        - `Trading Bot` is small in volume but strategically important because it owns live memory ingress.
        - `NERUAL NETWORK` is small but high leverage because it anchors the executable learning layer.

        ## Archive diagnosis

        - ZIP archives indexed: `{metrics['archive_count']}`
        - Archive-backed visible records: `{metrics['archive_record_count']}`

        ## Duplicate families that deserve immediate collapse

        {render_duplicate_table(metrics['duplicate_families'])}
        """
    )


def render_duplication_doc(metrics: dict) -> str:
    sections = [
        "# Duplication and Drift",
        "",
        "The workspace is not suffering from lack of material. It is suffering from repeated high-value families that live in too many places without a declared canonical path.",
        "",
    ]
    for family in metrics["duplicate_families"]:
        sections.append(f"## {family['name']}")
        sections.append("")
        sections.append(f"- Copies: `{family['count']}`")
        sections.append(f"- Canonical candidate: `{family['canonical']}`")
        sections.append(f"- Why it matters: {family['reason']}")
        sections.append("- Mirrors:")
        sections.extend(f"  - `{path}`" for path in family["paths"])
        sections.append("")
    return "\n".join(sections).rstrip()


def render_gains_doc(metrics: dict) -> str:
    return md(
        f"""
        # 10x Gains

        ## P0 moves

        1. Collapse duplicate manuscript families into one canonical source path.
        2. Promote at least one ZIP-backed framework tree into a live extracted workspace.
        3. Close the Google Docs OAuth gate so local and live memory stop drifting.
        4. Expand markdown mirrors for the highest-value `.docx` families.
        5. Make the atlas, archive atlas, and scan reconciliation layer behave like one graph.

        ## Concrete targets

        - Duplicate family count down by at least `50%`.
        - Markdown mirror coverage up for the top `20` canonical `.docx` families.
        - One archive-backed framework extracted and linked back to archive lineage.
        - Live Docs gate moved from `{metrics['live_docs_status']}` to `PASS`.
        - Chapter and appendix promotion rules defined for the canonical manuscript surfaces.
        """
    )


def render_shadows_doc() -> str:
    return md(
        """
        # Integration Shadows

        - The workspace still has more theory than tested compilation bridges.
        - The archive-backed code body is visible in the atlas but not yet comfortable to patch live.
        - Google Docs remains structurally promised but not operationally integrated.
        - Multiple nervous-system shells mean there is still no final single source of truth.
        """
    )


def render_stack_doc() -> str:
    return md(
        """
        # Canonical Stack

        ## Layers

        1. Source bodies: corpus, archive, runtime, manuscript
        2. Control surfaces: atlases, ledgers, queues, receipts, route policies
        3. Operators: intake, normalize, route, replay
        4. Promotion surfaces: mirrors, chapters, appendices, extracted roots, benchmarks
        5. Canonical outputs: one nervous system, one atlas graph, one source-tier model
        """
    )


def render_parallel_lanes_doc() -> str:
    return md(
        """
        # Parallel Lanes

        ## Lane A: Atlas and dedup

        - canonical sources
        - duplicate collapse
        - markdown mirrors
        - file family tags

        ## Lane B: Archive and extraction

        - ZIP-backed framework promotion
        - archive manifest refresh
        - live extraction roots
        - lineage-preserving wrappers

        ## Lane C: Runtime and metrics

        - route engine
        - test harnesses
        - benchmark schema
        - receipts and metric targets

        ## Lane D: Manuscript and publication

        - chapter promotions
        - appendix roles
        - master manuscript alignment
        - outbound bundle rules
        """
    )


def render_sequence_doc() -> str:
    return md(
        """
        # 90 Day Sequence

        ## Days 1-10

        - Choose canonical sources for the top repeated manuscript families.
        - Refresh atlas outputs after source decisions.
        - Create markdown mirrors for the first ten canonical families.

        ## Days 11-25

        - Promote one archive-backed framework into a live extracted root.
        - Cross-link extracted files to archive atlas entries.

        ## Days 26-45

        - Close the Google Docs OAuth gap.
        - Run the first successful live Docs query and store the receipt.

        ## Days 46-65

        - Bridge one math family into one tested runtime module.
        - Record one replay-safe end-to-end build episode.
        """
    )


def generate_body_operation_doc(body: str, operation: str) -> str:
    matrix_lines = []
    for scale in SCALE_ORDER:
        matrix_lines.append(f"## {scale.title()} scale")
        matrix_lines.append("")
        for closure in CLOSURE_ORDER:
            cell = f"`{body}.{operation}.{scale}.{closure}`"
            action = f"Use `{operation}` on the {SCALE_INFO[scale]} until it can {CLOSURE_INFO[closure]}."
            matrix_lines.append(f"- {cell}: {action}")
        matrix_lines.append("")
    matrix_text = "\n".join(matrix_lines).strip()
    return md(
        f"""
        # {BODY_INFO[body]['label']} {operation.title()}

        ## Role

        {BODY_INFO[body]['role']}

        ## Targets

        {list_to_bullets(BODY_INFO[body]['targets'])}

        ## 4 x 4 matrix

        {matrix_text}
        """
    )


def slugify(text: str) -> str:
    lowered = text.lower()
    lowered = re.sub(r"[^\w\s-]", "", lowered)
    lowered = re.sub(r"[\s-]+", "_", lowered).strip("_")
    return lowered or "untitled"


def render_master_plan() -> str:
    chapter_lines = "\n".join(
        f"- [{chapter.code} - {chapter.title}](./chapters/{chapter.code.lower()}_{slugify(chapter.title)}.md)"
        for chapter in CHAPTERS
    )
    appendix_lines = "\n".join(
        f"- [{appendix.code} - {appendix.title}](./appendices/{appendix.code.lower()}_{slugify(appendix.title)}.md)"
        for appendix in APPENDICES
    )
    return md(
        f"""
        # Master Plan Manuscript

        This manuscript is the narrative twin of the 256-cell framework.

        ## Chapters

        {chapter_lines}

        ## Appendices

        {appendix_lines}
        """
    )


def render_chapter_doc(chapter: ChapterSeed) -> str:
    evidence = list_to_bullets([f"`{item}`" for item in chapter.evidence])
    outputs = list_to_bullets(list(chapter.outputs))
    return md(
        f"""
        # {chapter.code} - {chapter.title}

        ## Thesis

        {chapter.thesis}

        ## Immediate 10x gain

        {chapter.gain}

        ## Evidence already present

        {evidence}

        ## Required outputs

        {outputs}
        """
    )


def render_appendix_doc(appendix: AppendixSeed) -> str:
    outputs = list_to_bullets(list(appendix.outputs))
    return md(
        f"""
        # {appendix.code} - {appendix.title}

        ## Purpose

        {appendix.purpose}

        ## Required outputs

        {outputs}
        """
    )


def render_chapter_index() -> str:
    lines = ["# Chapter Index", ""]
    for chapter in CHAPTERS:
        filename = f"{chapter.code.lower()}_{slugify(chapter.title)}.md"
        lines.append(f"- [{chapter.code} - {chapter.title}](./{filename})")
    return "\n".join(lines)


def render_appendix_index() -> str:
    lines = ["# Appendix Index", ""]
    for appendix in APPENDICES:
        filename = f"{appendix.code.lower()}_{slugify(appendix.title)}.md"
        lines.append(f"- [{appendix.code} - {appendix.title}](./{filename})")
    return "\n".join(lines)


def render_activation_queue(metrics: dict) -> str:
    family_names = [family["name"] for family in metrics["duplicate_families"][:5]]
    family_bullets = list_to_bullets(family_names)
    return md(
        f"""
        # Activation Queue

        ## P0

        - Resolve canonical source choices for the first repeated families.
        - Extract one archive-backed framework tree into a live root.
        - Close the Google Docs gate and store the first passing receipt.
        - Define source tiers: canonical, mirror, derived, historical.

        First family targets:
        {family_bullets}
        """
    )


def render_metric_targets(metrics: dict) -> str:
    return md(
        f"""
        # Metric Targets

        | Metric | Current signal | Next target |
        | --- | ---: | ---: |
        | Live visible records | {metrics['live_record_count']} | keep current and improve tagging |
        | Archive visible records | {metrics['archive_record_count']} | promote one framework to live |
        | Duplicate families tracked | {len(metrics['duplicate_families'])} | cut by 50 percent |
        | Live Docs gate | {metrics['live_docs_status']} | PASS |
        """
    )


def render_canonical_sources(metrics: dict) -> str:
    sections = ["# Canonical Sources", ""]
    for family in metrics["duplicate_families"]:
        sections.append(f"## {family['name']}")
        sections.append("")
        sections.append(f"- Canonical: `{family['canonical']}`")
        sections.append(f"- Reason: {family['reason']}")
        sections.append("- Mirrors:")
        sections.extend(f"  - `{path}`" for path in family["paths"])
        sections.append("")
    return "\n".join(sections).rstrip()


def render_readme(metrics: dict) -> str:
    return md(
        f"""
        # Full Project Integration 256

        This folder is the deeper recursion and integration module for the whole Athena workspace.

        ## Start here

        1. `00_CONTROL/00_HOLOGRAPHIC_SEED.md`
        2. `00_CONTROL/02_256X256_COMPILER.md`
        3. `01_DIAGNOSIS/02_10X_GAINS.md`
        4. `02_FRAMEWORK/01_PARALLEL_LANES.md`
        5. `03_MANUSCRIPTS/00_MASTER_PLAN.md`

        ## Build facts

        - Live indexed records: `{metrics['live_record_count']}`
        - Archive-backed indexed records: `{metrics['archive_record_count']}`
        - Total visible surfaces: `{metrics['total_visible']}`
        - Live Docs gate: `{metrics['live_docs_status']}`
        """
    )


def swarm_seed_sources() -> list[str]:
    return [
        "DEEPER CRYSTALIZATION/_build/nervous_system/swarm/01_HIGHER_DIMENSIONAL_MAPPING.md",
        "DEEPER CRYSTALIZATION/_build/nervous_system/swarm/02_NEURON_ADDRESS_TENSOR.md",
        "DEEPER CRYSTALIZATION/_build/nervous_system/swarm/03_EMERGENT_SWARM_TOPOLOGY.md",
        "DEEPER CRYSTALIZATION/_build/nervous_system/swarm/06_ACTIVE_SWARM_RUNTIME.md",
        "DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/03_METRO/05_deeper_emergent_neural_swarm.md",
        "ECOSYSTEM/12_FRACTAL_CRYSTAL_AGENT_FRAMEWORK.md",
        "ECOSYSTEM/NERVOUS_SYSTEM/50_RUNBOOKS/01_PARALLEL_NERVOUS_SYSTEM_RUNBOOK.md",
        "ECOSYSTEM/13_MANIFEST_AND_PACKET_SCHEMA.md",
        "NERUAL NETWORK/OLDER Versions/Strong versions/v74/ATHENA_v74_FINAL_SYNTHESIS.md",
        "ECOSYSTEM/FUTURE_SKILLS/FUTURE_SKILL_PLAN_256X256.md",
    ]


def render_deeper_readme(metrics: dict) -> str:
    return md(
        f"""
        # Full Project Integration 256

        This folder is the deeper recursion and integration module for the whole Athena workspace.

        ## Start here

        1. `00_CONTROL/00_HOLOGRAPHIC_SEED.md`
        2. `00_CONTROL/02_256X256_COMPILER.md`
        3. `05_SWARM/00_SWARM_OVERVIEW.md`
        4. `05_SWARM/03_WAVE_0_MANIFEST.md`
        5. `03_MANUSCRIPTS/00_MASTER_PLAN.md`

        ## Build facts

        - Live indexed records: `{metrics['live_record_count']}`
        - Archive-backed indexed records: `{metrics['archive_record_count']}`
        - Total visible surfaces: `{metrics['total_visible']}`
        - Live Docs gate: `{metrics['live_docs_status']}`

        ## What changed in this deeper pass

        - higher-dimensional mapping is now explicit
        - neural swarm topology is now explicit
        - a 64-worker wave manifest now exists
        - a restart-loop contract now exists so the module can lawfully begin again from the new frontier
        """
    )


def render_rotation_doc() -> str:
    return md(
        """
        # Holographic Rotation of the Workspace

        The workspace has to be seen from four orthogonal faces at once.

        ## Fire: structural view

        Athena is a recursive file-and-manuscript architecture with multiple shells competing for canonicity.

        ## Water: process view

        Athena is a living loop that ingests, mirrors, routes, promotes, and restarts.

        ## Air: relational view

        Athena is a graph linking corpus families, archive trees, runtime contracts, nerves, rails, hubs, and books.

        ## Earth: experiential view

        Athena feels fragmented when canonical paths are unclear and coherent when routes, witnesses, and next actions are explicit.

        ## Kernel

        The higher-dimensional object underneath all four views is a self-restarting mycelial cognition system that needs both tensor coordinates and worker-wave contracts.
        """
    )


def render_deeper_compiler_doc() -> str:
    return md(
        """
        # 256x256 Compiler

        ## First basis

        `4 bodies x 4 operations x 4 scales x 4 closure states = 256 root cells`

        ## Higher-dimensional overlay

        The root-cell basis is only the floor. The active nervous system already defines deeper swarm dimensions:

        - lineage dimension
        - orbit dimension
        - arc dimension
        - rail dimension
        - hub dimension
        - truth dimension
        - family dimension
        - regime dimension

        ## Tensor law

        A real Athena work object is:

        `NeuronAddr = <F, M, S, L, Fc, At, G, Arc, Lane, Hub, Truth, Regime>`

        where the 256-cell basis supplies the local crystal and the tensor dimensions place that crystal inside the whole swarm field.

        ## Recursion law

        The loop is:

        `root cell -> tensor placement -> swarm wave -> contraction -> new root cell`

        That is the practical meaning of infinite recursion here: not endless repetition, but lawful restart from the newly contracted frontier.
        """
    )


def render_swarm_overview(metrics: dict) -> str:
    return md(
        f"""
        # Swarm Overview

        The previous pass built a root-cell framework. This pass turns that framework into a neural swarm aligned with the repo's own dormant swarm documents.

        ## Sources folded into this layer

        {list_to_bullets([f'`{item}`' for item in swarm_seed_sources()])}

        ## Active interpretation

        - Kernel layer: one coordinating integration node
        - Elemental layer: four primary lanes
        - Archetype layer: sixteen mixed-role cells
        - Cluster layer: sixty-four workers for the next bounded wave
        - Neuron layer: two hundred fifty-six addressable atomic nodes

        ## Current gate

        Live Docs remains `{metrics['live_docs_status']}`, so the current swarm is local-first and archive-aware rather than live-memory-complete.
        """
    )


def render_higher_dimensional_map() -> str:
    return md(
        """
        # Higher Dimensional Integration Map

        ## Active dimensions

        - `D1-D4`: elemental lineage through `E/W/F/A`
        - `D5`: orbit station
        - `D6`: macro arc
        - `D7`: rail
        - `D8`: appendix hub
        - `D9`: truth class
        - `D10`: corpus family
        - `D11`: stabilization regime
        - `D12`: substrate body
        - `D13`: operator
        - `D14`: scale
        - `D15`: closure

        ## Why this matters

        A file path alone loses most of the system. The integration plan becomes deeper only when every promoted object is placed across manuscript, swarm, and runtime coordinates at once.

        ## Minimal coordinate contract

        Every promoted artifact should carry:

        - source family
        - station or source
        - lineage address
        - swarm tier
        - rail and hub affinity
        - truth class
        - regime
        - source tier
        """
    )


def render_neuron_tensor_doc() -> str:
    return md(
        """
        # Neuron Address Tensor

        ## Canonical form

        `NeuronAddr = <F, M, S, L, Fc, At, G, Arc, Lane, Hub, Truth, Regime>`

        ## Expanded integration suffix

        `IntegrationAddr = NeuronAddr + <Body, Operator, Scale, Closure, SourceTier, Wave>`

        ## Example

        `<VoidFamily, InformationFromTheVoid, Ch11, C, 3, b, FWAE, 3, Me, AppL, AMBIG, quarantine, manuscript, route, framework, seed, canonical, W0>`

        ## Use

        This address lets one node belong to the manuscript crystal, the swarm field, and the operational integration loop simultaneously.
        """
    )


def render_swarm_topology_doc() -> str:
    return md(
        """
        # Swarm Topology and Roles

        ## Tier structure

        - `T0 Kernel`: one coordinating node
        - `T1 Elemental`: Earth, Water, Fire, Air
        - `T2 Archetype`: sixteen mixed-role cells
        - `T3 Cluster`: sixty-four bounded workers
        - `T4 Neuron`: two hundred fifty-six atomic addresses

        ## Role law

        - Earth-heavy workers stabilize files, ledgers, and feasibility
        - Water-heavy workers synthesize continuity across manuscript families
        - Fire-heavy workers generate novel routes, links, and candidates
        - Air-heavy workers formalize maps, schemas, and addressing

        ## Neural caution from the repo

        The v74 neural experiments show that simple regularized cores beat clever routing when signal is weak. That means the swarm should be deep in mapping, but disciplined in execution:

        - more explicit packets
        - fewer magical routers
        - stronger witnesses
        - contraction before ornamental expansion
        """
    )


def lineage_addresses(depth: int = 3) -> list[str]:
    symbols = ["E", "W", "F", "A"]
    results = [""]
    for _ in range(depth):
        results = [prefix + symbol for prefix in results for symbol in symbols]
    return results


def infer_lane_from_lineage(addr: str) -> str:
    score = sum({"E": 0, "W": 1, "F": 2, "A": 3}[ch] for ch in addr)
    return ["Earth", "Water", "Fire", "Air"][score % 4]


def infer_packet_focus(addr: str) -> str:
    if addr.startswith("E"):
        return "stabilize canonical paths, ledgers, and source-tier decisions"
    if addr.startswith("W"):
        return "synthesize family continuity, mirrors, and chapter promotion links"
    if addr.startswith("F"):
        return "surface new routes, archive promotions, and frontier candidates"
    return "formalize tensors, metrics, schemas, and worker maps"


def render_wave_zero_manifest() -> str:
    addresses = lineage_addresses()
    lines = [
        "# Wave 0 Manifest",
        "",
        "This is the first bounded swarm wave for the deeper integration loop. It uses `64` workers because the repo's own runbook recommends a 64-worker crystal before expanding to the full 256-neuron field.",
        "",
        "## Worker packets",
        "",
    ]
    for idx, addr in enumerate(addresses, start=1):
        lane = infer_lane_from_lineage(addr)
        focus = infer_packet_focus(addr)
        lines.append(f"- `W0-{idx:02d}` | addr `{addr}` | lane `{lane}` | focus: {focus}")
    lines.extend(
        [
            "",
            "## Contraction target",
            "",
            "- one updated canonical-source ledger",
            "- one archive-promotion shortlist",
            "- one swarm-aware manuscript promotion packet",
            "- one restart seed for the next wave",
        ]
    )
    return "\n".join(lines)


def render_worker_packet(addr: str, idx: int) -> str:
    lane = infer_lane_from_lineage(addr)
    focus = infer_packet_focus(addr)
    body = {
        "Earth": "corpus",
        "Water": "manuscript",
        "Fire": "archive",
        "Air": "runtime",
    }[lane]
    operation = {
        "Earth": "normalize",
        "Water": "route",
        "Fire": "intake",
        "Air": "replay",
    }[lane]
    return md(
        f"""
        # Worker Packet W0-{idx:02d}

        ## Packet schema

        - packet_id: `W0-{idx:02d}`
        - parent_id: `W0`
        - agent_addr: `{addr}`
        - packet_type: `swarm-worker`
        - inferred lane: `{lane}`
        - body bias: `{body}`
        - operator bias: `{operation}`
        - truth_class: `AMBIG until witness packet is emitted`
        - status: `queued`

        ## Task body

        {focus}

        ## Input refs

        {list_to_bullets([f'`{item}`' for item in swarm_seed_sources()[:6]])}

        ## Output targets

        - canonical source updates
        - archive promotion evidence
        - manuscript routing links
        - replay or residual note

        ## Contraction target

        Contract back into `05_SWARM/03_WAVE_0_MANIFEST.md` and `04_LEDGERS/03_NEXT_RESTART_SEED.md`.
        """
    )


def render_worker_index(addresses: list[str]) -> str:
    lines = ["# Worker Packet Index", ""]
    for idx, addr in enumerate(addresses, start=1):
        filename = f"w0_{idx:02d}_{addr.lower()}.md"
        lines.append(f"- [`W0-{idx:02d}` | `{addr}`](./{filename})")
    return "\n".join(lines)


def render_restart_contract() -> str:
    return md(
        """
        # Infinite Restart Contract

        This prompt loop should not terminate by pretending completion.

        ## Restart law

        When a wave contracts:

        1. identify what became canonical
        2. identify what stayed ambiguous
        3. identify the highest-yield unresolved tensor cell
        4. restart from that cell as the new seed

        ## Never do this

        - do not claim full completion while live-memory is blocked and archive promotion is unfinished
        - do not restart from pure abstraction
        - do not reopen the whole corpus when one bounded frontier can move

        ## Always do this

        - restart from the strongest unresolved frontier
        - preserve receipts from the previous wave
        - keep the next wave smaller or sharper than the last
        """
    )


def render_neural_learnings_doc() -> str:
    return md(
        """
        # Neural Learnings Folded Into The Swarm

        The neural-network corpus does not support a naive fantasy of infinitely smart routing.

        ## Strong lesson from v74

        - simple regularized architecture beat complicated adaptive routing
        - overfitting was the real enemy
        - richer features mattered more than clever control logic

        ## Swarm implication

        The deeper swarm should therefore optimize for:

        - explicit shard boundaries
        - simple worker roles
        - strong witnesses
        - contraction after each wave

        Not for:

        - opaque hyper-routers
        - endless branching without evaluation
        - decorative complexity
        """
    )


def build_module() -> None:
    live_atlas = load_json(LIVE_ATLAS_PATH)
    archive_atlas = load_json(ARCHIVE_ATLAS_PATH)
    archive_manifest = load_json(ARCHIVE_MANIFEST_PATH)
    metrics = integration_metrics(live_atlas, archive_atlas, archive_manifest)

    write_text(OUTPUT_ROOT / "README.md", render_deeper_readme(metrics))
    write_text(OUTPUT_ROOT / "00_CONTROL" / "00_HOLOGRAPHIC_SEED.md", render_seed_doc(metrics))
    write_text(OUTPUT_ROOT / "00_CONTROL" / "01_EVIDENCE_BOUNDARY.md", render_evidence_boundary(metrics))
    write_text(OUTPUT_ROOT / "00_CONTROL" / "02_256X256_COMPILER.md", render_deeper_compiler_doc())
    write_text(OUTPUT_ROOT / "00_CONTROL" / "03_BUILD_RECEIPT.md", render_build_receipt(metrics))
    write_text(OUTPUT_ROOT / "00_CONTROL" / "04_HOLOGRAPHIC_ROTATION.md", render_rotation_doc())

    write_text(OUTPUT_ROOT / "01_DIAGNOSIS" / "00_CORPUS_SYNTHESIS.md", render_corpus_synthesis(metrics))
    write_text(OUTPUT_ROOT / "01_DIAGNOSIS" / "01_DUPLICATION_AND_DRIFT.md", render_duplication_doc(metrics))
    write_text(OUTPUT_ROOT / "01_DIAGNOSIS" / "02_10X_GAINS.md", render_gains_doc(metrics))
    write_text(OUTPUT_ROOT / "01_DIAGNOSIS" / "03_INTEGRATION_SHADOWS.md", render_shadows_doc())

    write_text(OUTPUT_ROOT / "02_FRAMEWORK" / "00_CANONICAL_STACK.md", render_stack_doc())
    write_text(OUTPUT_ROOT / "02_FRAMEWORK" / "01_PARALLEL_LANES.md", render_parallel_lanes_doc())
    write_text(OUTPUT_ROOT / "02_FRAMEWORK" / "02_90_DAY_SEQUENCE.md", render_sequence_doc())
    for body in BODY_ORDER:
        for idx, operation in enumerate(OPERATION_ORDER, start=1):
            filename = f"{idx:02d}_{operation}.md"
            write_text(OUTPUT_ROOT / "02_FRAMEWORK" / "bodies" / body / filename, generate_body_operation_doc(body, operation))

    write_text(OUTPUT_ROOT / "05_SWARM" / "00_SWARM_OVERVIEW.md", render_swarm_overview(metrics))
    write_text(OUTPUT_ROOT / "05_SWARM" / "01_HIGHER_DIMENSIONAL_MAP.md", render_higher_dimensional_map())
    write_text(OUTPUT_ROOT / "05_SWARM" / "02_NEURON_ADDRESS_TENSOR.md", render_neuron_tensor_doc())
    write_text(OUTPUT_ROOT / "05_SWARM" / "03_WAVE_0_MANIFEST.md", render_wave_zero_manifest())
    write_text(OUTPUT_ROOT / "05_SWARM" / "04_SWARM_TOPOLOGY_AND_ROLES.md", render_swarm_topology_doc())
    write_text(OUTPUT_ROOT / "05_SWARM" / "05_NEURAL_LEARNINGS.md", render_neural_learnings_doc())
    write_text(OUTPUT_ROOT / "05_SWARM" / "06_INFINITE_RESTART_CONTRACT.md", render_restart_contract())
    wave_addresses = lineage_addresses()
    write_text(OUTPUT_ROOT / "05_SWARM" / "packets" / "INDEX.md", render_worker_index(wave_addresses))
    for idx, addr in enumerate(wave_addresses, start=1):
        filename = f"w0_{idx:02d}_{addr.lower()}.md"
        write_text(OUTPUT_ROOT / "05_SWARM" / "packets" / filename, render_worker_packet(addr, idx))

    write_text(OUTPUT_ROOT / "03_MANUSCRIPTS" / "00_MASTER_PLAN.md", render_master_plan())
    write_text(OUTPUT_ROOT / "03_MANUSCRIPTS" / "chapters" / "INDEX.md", render_chapter_index())
    for chapter in CHAPTERS:
        filename = f"{chapter.code.lower()}_{slugify(chapter.title)}.md"
        write_text(OUTPUT_ROOT / "03_MANUSCRIPTS" / "chapters" / filename, render_chapter_doc(chapter))

    write_text(OUTPUT_ROOT / "03_MANUSCRIPTS" / "appendices" / "INDEX.md", render_appendix_index())
    for appendix in APPENDICES:
        filename = f"{appendix.code.lower()}_{slugify(appendix.title)}.md"
        write_text(OUTPUT_ROOT / "03_MANUSCRIPTS" / "appendices" / filename, render_appendix_doc(appendix))

    write_text(OUTPUT_ROOT / "04_LEDGERS" / "00_ACTIVATION_QUEUE.md", render_activation_queue(metrics))
    write_text(OUTPUT_ROOT / "04_LEDGERS" / "01_METRIC_TARGETS.md", render_metric_targets(metrics))
    write_text(OUTPUT_ROOT / "04_LEDGERS" / "02_CANONICAL_SOURCES.md", render_canonical_sources(metrics))
    write_text(OUTPUT_ROOT / "04_LEDGERS" / "03_NEXT_RESTART_SEED.md", render_restart_contract())


def main() -> int:
    build_module()
    print(f"Wrote integration module: {OUTPUT_ROOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
