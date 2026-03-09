#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


LENSES = ("S", "F", "C", "R")
FACETS = (
    ("1", "Objects"),
    ("2", "Laws"),
    ("3", "Constructions"),
    ("4", "Certificates"),
)
ATOMS = ("a", "b", "c", "d")

FAMILY_LABELS = {
    "live-orchestration": "Live orchestration and prompt control",
    "void-and-collapse": "Void, Chapter 11, and collapse engines",
    "manuscript-architecture": "Manuscript architecture and routing law",
    "higher-dimensional-geometry": "Higher-dimensional geometry and holographic kernel",
    "civilization-and-governance": "Civilization design, hierarchy, governance, and law",
    "mythic-sign-systems": "Mythic sign systems, encoded memory, and symbol runtime",
    "transport-and-runtime": "Transport, runtime, and executable framework",
    "identity-and-instruction": "Athena identity, pedagogy, and narrative voice",
    "general-corpus": "General corpus support",
}

PENTADIC_LANES = (
    ("A", "Formal Core", "definitions, theorems, axioms, fixed kernels"),
    ("B", "Intuition and Metaphor", "symbolic field, story, embodiment, mnemonic compression"),
    ("C", "Compilation", "runtime, transport, code, executable architecture"),
    ("D", "Verification", "witness, replay, proof, legality, corridor closure"),
    ("E", "Editorial and Audit", "routing, map hygiene, prompts, indexing, governance"),
)

SWARM_LAYERS = (
    ("L0", "Leaf Readers", "single-source readers that extract headings, excerpts, and local signals"),
    ("L1", "Family Synths", "cluster-level agents that merge document families into stable motifs"),
    ("L2", "Chapter Weavers", "chapter agents that bind family outputs into the 21-station orbit"),
    ("L3", "Appendix Governors", "hub agents that stabilize routing law, truth corridors, replay, and deployment"),
    ("L4", "Lane Mediators", "pentadic-lane agents that keep formal, intuitive, compiled, verified, and editorial views synchronized"),
    ("L5", "Collective Relay", "multi-agent coordination interface across local, blocked-live, and future external relay channels"),
    ("L6", "Council Mesh", "family councils, rail councils, and sign-governors that distribute tasks, messages, and escalations"),
    ("L7", "Civilization Kernel", "whole-manuscript polity that compresses signs, rules, succession, and civilization-scale continuity"),
)

TRUTH_DEFAULT = "AMBIG"

GOVERNANCE_SIGNS = (
    ("SIG00", "SEED", "initialize a new branch, intake, or civilizational sub-cell"),
    ("SIG01", "ENCODE", "bind a symbol system, glyph set, or memory carrier into the graph"),
    ("SIG02", "ROUTE", "select lawful destination, corridor, and metro ride"),
    ("SIG03", "BIND", "attach a message or task to a stable witness-bearing object"),
    ("SIG04", "WITNESS", "promote a claim only when evidence and replay are present"),
    ("SIG05", "QUARANTINE", "contain unresolved conflict, paradox, or corruption"),
    ("SIG06", "MERGE", "compose multiple agents or documents into one stabilized output"),
    ("SIG07", "RESTART", "collapse a stale branch while preserving lawful continuity"),
    ("SIG08", "DEPLOY", "hand a closed artifact into bounded execution"),
    ("SIG09", "MEMORY", "persist state across passes, mirrors, and migrations"),
    ("SIG10", "TEACH", "convert the current state into transmissible pedagogy"),
    ("SIG11", "GOVERN", "apply explicit hierarchy, rule, and escalation law"),
    ("SIG12", "MEASURE", "record metrics, drift, and performance envelopes"),
    ("SIG13", "HEAL", "repair decay, incoherence, or motivational collapse"),
    ("SIG14", "PUBLISH", "emit signed release packets into wider circulation"),
    ("SIG15", "SUCCESSION", "transfer continuity to the next agent, generation, or tome"),
)

CIVILIZATION_TIERS = (
    ("T0", "Sign", "atomic governance symbols that encode admissible operations"),
    ("T1", "Message", "truth-typed packets routed across the swarm"),
    ("T2", "Task", "bounded work units with witnesses, replay, and exit conditions"),
    ("T3", "Cell", "small agent teams that hold a local region of the graph"),
    ("T4", "Chapter", "chapter weavers that stabilize one 4^4 tile"),
    ("T5", "Family", "thematic councils that govern recurring motifs across sources"),
    ("T6", "Rail Council", "lane-specific coordinators that balance Su, Me, and Sa traffic"),
    ("T7", "Civilization", "the whole manuscript polity as a self-regenerating nervous system"),
)

QUANTUM_OPERATOR_FAMILIES = (
    "Parse", "Encode", "Route", "Bind",
    "Witness", "Quarantine", "Merge", "Restart",
    "Deploy", "Remember", "Teach", "Govern",
    "Measure", "Heal", "Publish", "Succession",
)

QUANTUM_OPERATOR_PHASES = (
    "Seed", "Scan", "Sort", "Map",
    "Link", "Test", "Proof", "Compress",
    "Expand", "Replay", "Repair", "Escalate",
    "Stabilize", "Transmit", "Archive", "Renew",
)


@dataclass(frozen=True)
class Chapter:
    index: int
    station: str
    title: str
    arc: int
    rot: int
    lane: str
    role: str
    hubs: tuple[str, ...]
    families: tuple[str, ...]

    @property
    def code(self) -> str:
        return f"Ch{self.index:02d}"

    @property
    def omega(self) -> int:
        return self.index - 1

    @property
    def addr(self) -> str:
        return f"{self.code}<{self.station}>"


CHAPTERS = [
    Chapter(1, "0000", "Kernel and Entry Law", 0, 0, "Su", "Foundational anchor, legend, and parse-safe entry station for the whole tome.", ("AppA", "AppC", "AppI", "AppM"), ("manuscript-architecture", "live-orchestration")),
    Chapter(2, "0001", "Address Algebra and Crystal Coordinates", 0, 0, "Me", "Canonical addressing, base-4 station coding, and identity-preserving lattice placement.", ("AppA", "AppC", "AppB", "AppI", "AppM"), ("manuscript-architecture", "transport-and-runtime", "mythic-sign-systems")),
    Chapter(3, "0002", "Truth Corridors and Witness Discipline", 0, 0, "Sa", "Corridor truth typing, admissibility, residual law, and replay obligations.", ("AppA", "AppI", "AppM", "AppJ"), ("manuscript-architecture", "transport-and-runtime")),
    Chapter(4, "0003", "Zero-Point Stabilization", 1, 1, "Me", "PZPM intake, normalization, and paradox-safe fixed-point preparation.", ("AppA", "AppC", "AppE", "AppJ", "AppI", "AppM"), ("void-and-collapse", "manuscript-architecture")),
    Chapter(5, "0010", "Paradox Regimes and Quarantine Calculus", 1, 1, "Sa", "Classical, stratified, and quarantine regimes for stabilized contradiction management.", ("AppA", "AppC", "AppI", "AppB", "AppL", "AppM"), ("void-and-collapse", "transport-and-runtime")),
    Chapter(6, "0011", "Documents-as-Theories", 1, 1, "Su", "Theory-documents, manuscript objects, and theorem-bearing document shells.", ("AppA", "AppC", "AppI", "AppM"), ("manuscript-architecture", "live-orchestration")),
    Chapter(7, "0012", "Tunnels as Morphisms", 2, 2, "Sa", "Lawful transports, shadow-axis rotation, and typed tunnel semantics.", ("AppA", "AppE", "AppH", "AppL", "AppI", "AppM"), ("transport-and-runtime", "manuscript-architecture")),
    Chapter(8, "0013", "Synchronization Calculus", 2, 2, "Su", "The operator S, latent-core semantics z, and cross-document sync budgets.", ("AppA", "AppE", "AppM", "AppB", "AppJ", "AppI"), ("manuscript-architecture", "live-orchestration")),
    Chapter(9, "0020", "Retrieval and Metro Routing", 2, 2, "Me", "Address-first search, metro rides, and route competition over the mycelium graph.", ("AppA", "AppE", "AppI", "AppH", "AppL", "AppM"), ("live-orchestration", "manuscript-architecture")),
    Chapter(10, "0021", "Multi-Lens Solution Construction", 3, 0, "Su", "Synthesis of routed evidence into canonical answer objects and patch-bearing artifacts.", ("AppA", "AppF", "AppM", "AppH", "AppJ", "AppI"), ("manuscript-architecture", "transport-and-runtime")),
    Chapter(11, "0022", "Void Book and Restart-Token Tunneling", 3, 0, "Me", "Aether versus Void transport, restart continuity, and lawful reset by capsule.", ("AppA", "AppF", "AppM", "AppL", "AppI"), ("void-and-collapse", "live-orchestration")),
    Chapter(12, "0023", "Legality, Certificates, and Closure", 3, 0, "Sa", "Proof-carrying closure, certificate bundles, and OK-promotion obligations.", ("AppA", "AppF", "AppC", "AppM", "AppI"), ("transport-and-runtime", "manuscript-architecture")),
    Chapter(13, "0030", "Memory, Regeneration, and Persistence", 4, 1, "Me", "Replayable memory objects, regeneration economics, and long-range continuity.", ("AppA", "AppG", "AppE", "AppM", "AppJ", "AppI"), ("identity-and-instruction", "transport-and-runtime", "mythic-sign-systems")),
    Chapter(14, "0031", "Migration, Versioning, and Pulse Retro Weaving", 4, 1, "Sa", "MIGRATE discipline, compat matrices, delta packs, and rollback governance.", ("AppA", "AppG", "AppM", "AppH", "AppK", "AppI"), ("transport-and-runtime", "live-orchestration")),
    Chapter(15, "0032", "CUT Architecture", 4, 1, "Su", "Computation Universe Toolkit modules, APIs, and implementable system contracts.", ("AppA", "AppG", "AppC", "AppJ", "AppI", "AppM"), ("transport-and-runtime", "manuscript-architecture")),
    Chapter(16, "0033", "Verification Harnesses and Replay Kernels", 5, 2, "Sa", "Deterministic re-checks, test capsules, and correctness enforcement.", ("AppA", "AppN", "AppM", "AppK", "AppI"), ("transport-and-runtime", "live-orchestration")),
    Chapter(17, "0100", "Deployment and Bounded Agency", 5, 2, "Su", "Cloud limbs, execution workers, and governed action under explicit corridors.", ("AppA", "AppN", "AppE", "AppJ", "AppI", "AppM"), ("transport-and-runtime", "identity-and-instruction", "civilization-and-governance")),
    Chapter(18, "0101", "Macro Invariants and Universal Math Stack", 5, 2, "Me", "Global invariants across Macro, PZPM, and CUT coordinate layers.", ("AppA", "AppN", "AppC", "AppL", "AppI", "AppM"), ("transport-and-runtime", "manuscript-architecture", "civilization-and-governance")),
    Chapter(19, "0102", "Convergence, Fixed Points, and Controlled Non-Convergence", 6, 0, "Su", "Banach-style convergence, residual persistence, and sanctioned non-closure.", ("AppA", "AppP", "AppI", "AppB", "AppJ", "AppM"), ("void-and-collapse", "transport-and-runtime")),
    Chapter(20, "0103", "Collective Authoring and Three-Agent Synchrony", 6, 0, "Me", "Parallel manuscript governance, merge discipline, and collaborative mycelium control.", ("AppA", "AppP", "AppE", "AppL", "AppI", "AppM"), ("live-orchestration", "identity-and-instruction", "civilization-and-governance")),
    Chapter(21, "0110", "Self-Replication, Open Problems, and the Next Crystal", 6, 0, "Sa", "The manuscript as seed, generator, and future metro for the next tome.", ("AppA", "AppP", "AppM", "AppL", "AppI"), ("live-orchestration", "manuscript-architecture", "civilization-and-governance")),
]

APPENDICES = [
    ("AppA", "Addressing, Symbols, Parsing Grammar", "Entry grammar, local address parsing, symbol hygiene, and manuscript station identity."),
    ("AppB", "Canon Laws, Equivalence Budgets, Normal Forms", "Equivalence rules, commutation budgets, normal-form contracts, and law stabilization."),
    ("AppC", "Square Kernel Pack", "Discrete kernels, indexing packs, chapter-tile schedules, and crystal algebra."),
    ("AppD", "Registry, Profiles, Version IDs", "Profile registry, version IDs, manuscript signatures, and migration anchors."),
    ("AppE", "Circle Gear and Mixed-Radix Clock", "Orbit order, mixed-radix timing, phase-lock semantics, and chapter-cycle transport."),
    ("AppF", "Transport, Rotation-as-Conjugacy, DUAL Legality", "Transport legality, dual routes, conjugacy bridges, and lawful movement across charts."),
    ("AppG", "Triangle Control and Tria Prima", "Triadic control rails, recursion governance, carry rules, and multi-agent coordination gates."),
    ("AppH", "Coupling and Topology", "Coupling invariants, topology closure, dependency graph rules, and construction stitching."),
    ("AppI", "Corridors and Truth Lattice", "Truth-typed corridor contracts, admissibility budgets, and abstain-over-guess discipline."),
    ("AppJ", "Residual Ledgers and NEAR Machinery", "Residual envelopes, bounded approximation, NEAR upgrades, and partial-closure bookkeeping."),
    ("AppK", "Conflict, Quarantine, Revocation", "Conflict packets, quarantine protocols, illegal-state containment, and revocation receipts."),
    ("AppL", "Evidence Plans and AMBIG Promotion", "Candidate sets, evidence plans, ambiguity handling, and promotion harnesses."),
    ("AppM", "Replay Kernel and Verifier Capsules", "Replay capsules, deterministic verification, proof-carrying artifacts, and rerun contracts."),
    ("AppN", "Container Formats and Virtual Mount", "Containers, salvage routes, mounted corpora, and runtime packaging."),
    ("AppO", "Publication Import/Export Bundles", "Publication bundles, import/export law, signed releases, and dissemination packets."),
    ("AppP", "Deployment Profiles and Monitoring", "Deployment regimes, monitoring surfaces, observability, and execution profiles."),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^\w\s-]", "", value)
    value = re.sub(r"[\s_-]+", "_", value).strip("_")
    return value or "untitled"


def normalize_name(name: str) -> str:
    cleaned = re.sub(r"\s+\(\d+\)(?=\.[^.]+$)", "", name).strip()
    return Path(cleaned).stem


def chapter_filename(chapter: Chapter) -> str:
    return f"{chapter.code}_{chapter.station}_{slugify(chapter.title)}.md"


def appendix_filename(code: str, title: str) -> str:
    return f"{code}_{slugify(title)}.md"


def capsule_filename(index: int, record_name: str) -> str:
    return f"{index:02d}_{slugify(normalize_name(record_name))}.md"


def station_header(chapter: Chapter) -> str:
    return f"[Arc {chapter.arc} | Rot {chapter.rot} | Lane {chapter.lane} | w={chapter.omega}]"


def lane_members(lane: str) -> list[Chapter]:
    return [chapter for chapter in CHAPTERS if chapter.lane == lane]


def arc_members(arc: int) -> list[Chapter]:
    return [chapter for chapter in CHAPTERS if chapter.arc == arc]


def orbit_neighbors(chapter: Chapter) -> tuple[Chapter, Chapter]:
    previous = CHAPTERS[(chapter.index - 2) % len(CHAPTERS)]
    nxt = CHAPTERS[chapter.index % len(CHAPTERS)]
    return previous, nxt


def infer_family(name: str, excerpt: str) -> str:
    text = f"{name} {excerpt}".lower()
    score_map = {
        "higher-dimensional-geometry": {
            "higher-dimensional": 6,
            "higher dimension": 6,
            "square ? circle ? triangle": 6,
            "square/circle/triangle": 6,
            "holographic kernel": 6,
            "h^4": 5,
            "d^5": 5,
            "quad holographic rotation": 6,
            "metro calculus": 5,
            "tunneling coherence crystal": 5,
            "tensor": 4,
            "manifold": 4,
            "rotation is conjugacy": 5,
        },
        "civilization-and-governance": {
            "govern": 5,
            "governance": 6,
            "law": 4,
            "calendar": 4,
            "role-graph": 5,
            "civilization": 6,
            "civilizational": 6,
            "hierarch": 5,
            "community": 3,
            "administrative": 4,
            "empire": 3,
            "alignment": 4,
            "protocol for living": 4,
            "council": 4,
        },
        "mythic-sign-systems": {
            "glyph": 5,
            "glyphs": 5,
            "ogham": 6,
            "khipu": 6,
            "rune": 5,
            "runes": 5,
            "symbol": 4,
            "alphabet": 4,
            "divination": 4,
            "sefirot": 5,
            "tree of life": 5,
            "cord": 4,
            "rosetta": 4,
            "oracle": 3,
            "sacred geography": 4,
            "hymn": 4,
        },
        "live-orchestration": {
            "prompt": 4,
            "real time": 5,
            "search space": 3,
            "orchestration": 4,
            "self-routing": 2,
            "live manuscript": 3,
        },
        "void-and-collapse": {
            "void": 5,
            "chapter 11": 5,
            "perpetual motion": 4,
            "collapse": 4,
            "restart": 4,
            "zero-point": 3,
            "paradox": 3,
        },
        "manuscript-architecture": {
            "manuscript": 4,
            "metro": 3,
            "atlas": 3,
            "holographic": 3,
            "superorganism": 4,
            "crystalized neural substrate": 4,
            "tome": 2,
        },
        "transport-and-runtime": {
            "transport": 5,
            "cut": 5,
            "aqm": 4,
            "runtime": 4,
            "deployment": 4,
            "algorithm": 3,
            "code": 3,
            "solenoidal": 4,
            "opcode": 4,
            "chemical realization": 4,
            "time system": 4,
            "verification harness": 3,
        },
        "identity-and-instruction": {
            "athena": 4,
            "teacher": 5,
            "i am": 5,
            "stories": 4,
            "voynich": 4,
            "pedagogy": 4,
            "mythic": 3,
            "charlie": 3,
        },
    }
    scores = {family: 0 for family in score_map}
    for family, weights in score_map.items():
        for term, weight in weights.items():
            if term in text:
                scores[family] += weight
    best_family = max(scores, key=scores.get)
    return best_family if scores[best_family] > 0 else "general-corpus"


def infer_chapter_links(name: str, excerpt: str, family: str) -> list[str]:
    text = f"{name} {excerpt}".lower()
    links: list[str] = []
    base = {
        "live-orchestration": ["Ch09", "Ch20", "Ch21"],
        "void-and-collapse": ["Ch04", "Ch11", "Ch19"],
        "manuscript-architecture": ["Ch01", "Ch06", "Ch08"],
        "higher-dimensional-geometry": ["Ch05", "Ch06", "Ch07", "Ch08"],
        "civilization-and-governance": ["Ch17", "Ch18", "Ch20", "Ch21"],
        "mythic-sign-systems": ["Ch02", "Ch09", "Ch13", "Ch18"],
        "transport-and-runtime": ["Ch07", "Ch15", "Ch16", "Ch18"],
        "identity-and-instruction": ["Ch13", "Ch17", "Ch20"],
    }
    links.extend(base.get(family, []))
    if "time" in text:
        links.append("Ch19")
    if "chapter 11" in text:
        links.append("Ch11")
    if "routing" in text or "metro" in text:
        links.append("Ch09")
    if "sign" in text or "glyph" in text or "khipu" in text or "ogham" in text:
        links.append("Ch02")
        links.append("Ch13")
    if "verification" in text or "replay" in text:
        links.append("Ch16")
    if "collective" in text or "three-agent" in text:
        links.append("Ch20")
    if "govern" in text or "hierarch" in text or "civiliz" in text:
        links.append("Ch17")
        links.append("Ch21")
    if any(term in text for term in chapter_keyword_profile("Ch03")):
        links.append("Ch03")
    if any(term in text for term in chapter_keyword_profile("Ch10")):
        links.append("Ch10")
    if any(term in text for term in chapter_keyword_profile("Ch12")):
        links.append("Ch12")
    if any(term in text for term in chapter_keyword_profile("Ch14")):
        links.append("Ch14")
    seen: set[str] = set()
    ordered: list[str] = []
    for item in links:
        if item not in seen:
            ordered.append(item)
            seen.add(item)
    return ordered[:4]


def infer_appendix_links(name: str, excerpt: str, family: str) -> list[str]:
    text = f"{name} {excerpt}".lower()
    links: list[str] = []
    base = {
        "live-orchestration": ["AppA", "AppL", "AppP"],
        "void-and-collapse": ["AppF", "AppI", "AppL"],
        "manuscript-architecture": ["AppA", "AppC", "AppI", "AppM"],
        "higher-dimensional-geometry": ["AppE", "AppF", "AppG", "AppM"],
        "civilization-and-governance": ["AppA", "AppD", "AppG", "AppP"],
        "mythic-sign-systems": ["AppA", "AppB", "AppC", "AppM"],
        "transport-and-runtime": ["AppF", "AppG", "AppM", "AppN"],
        "identity-and-instruction": ["AppG", "AppP"],
    }
    links.extend(base.get(family, []))
    if "conflict" in text or "quarantine" in text:
        links.append("AppK")
    if "time" in text or "orbit" in text:
        links.append("AppE")
    if "sign" in text or "glyph" in text or "khipu" in text or "ogham" in text:
        links.append("AppA")
        links.append("AppB")
    if "govern" in text or "hierarch" in text or "civiliz" in text:
        links.append("AppG")
        links.append("AppP")
    seen: set[str] = set()
    ordered: list[str] = []
    for item in links:
        if item not in seen:
            ordered.append(item)
            seen.add(item)
    return ordered[:4]


def summarize_focus(name: str, excerpt: str, family: str) -> str:
    text = f"{name} {excerpt}".lower()
    if family == "higher-dimensional-geometry":
        return "Defines higher-dimensional carriers, holographic kernels, tensor geometry, and square/circle/triangle manifold operators."
    if family == "civilization-and-governance":
        return "Defines hierarchy, councils, law, calendars, and civilization-scale governance for multi-agent continuity."
    if family == "mythic-sign-systems":
        return "Defines symbol runtimes, glyph memory, sacred encoding systems, and high-density retrieval carriers."
    if family == "live-orchestration":
        return "Controls prompting, live search expectations, and multi-agent coordination pressure."
    if family == "void-and-collapse":
        return "Stabilizes zero-point logic, collapse rules, restart semantics, and Chapter 11 generation."
    if family == "manuscript-architecture":
        return "Defines the atlas, metro map, chapter lattice, and manuscript-as-brain frame."
    if family == "transport-and-runtime":
        return "Carries executable transport law, runtime contracts, math stack bridges, and implementation surfaces."
    if family == "identity-and-instruction":
        return "Holds Athena identity, pedagogy, narrative continuity, and motivational voice."
    if "time" in text:
        return "Adds temporal phase structure and cyclical recurrence contracts."
    return "Contributes supporting material to the broader manuscript lattice."


def ascii_clean(text: str) -> str:
    return text.encode("ascii", "replace").decode()


def record_blob(record: dict) -> str:
    headings = " ".join(record.get("heading_candidates") or [])
    return f"{Path(record.get('relative_path', '')).name} {record.get('excerpt', '')} {headings}".lower()


def collect_signals(record: dict) -> dict[str, int]:
    blob = record_blob(record)
    keyword_sets = {
        "higher_dimensional": ["higher-dimensional", "higher dimensional", "manifold", "tensor", "lattice"],
        "swarm": ["swarm", "collective", "hive", "three athena", "agent-swarm"],
        "routing": ["routing", "route", "metro", "atlas", "self-routing", "corridor"],
        "verification": ["proof", "witness", "replay", "certificate", "verify", "verification"],
        "runtime": ["runtime", "code", "algorithm", "transport", "cut", "opcode", "deployment"],
        "void": ["void", "zero-point", "collapse", "restart", "paradox"],
        "identity": ["athena", "teacher", "i am", "story", "mythic", "embodiment"],
        "governance": ["govern", "law", "council", "hierarch", "calendar", "civilization"],
        "sign_system": ["glyph", "ogham", "khipu", "rune", "symbol", "alphabet", "rosetta"],
    }
    return {key: sum(1 for term in terms if term in blob) for key, terms in keyword_sets.items()}


def assign_pentadic_lanes(record: dict) -> list[str]:
    blob = record_blob(record)
    lane_keywords = {
        "A": ["axiom", "theorem", "definition", "formal", "math", "kernel"],
        "B": ["story", "myth", "symbolic", "embodiment", "teacher", "i am"],
        "C": ["runtime", "code", "algorithm", "transport", "compile", "cut"],
        "D": ["proof", "witness", "replay", "verify", "certificate", "corridor"],
        "E": ["prompt", "routing", "metro", "index", "editorial", "governance"],
    }
    assigned = [lane for lane, keywords in lane_keywords.items() if any(keyword in blob for keyword in keywords)]
    return assigned or ["E"]


def family_stats(records: list[dict]) -> dict[str, dict]:
    stats: dict[str, dict] = {}
    for record in records:
        name = Path(record["relative_path"]).name
        family = infer_family(name, record.get("excerpt", ""))
        info = stats.setdefault(
            family,
            {
                "count": 0,
                "records": [],
                "signals": {
                    "higher_dimensional": 0,
                    "swarm": 0,
                    "routing": 0,
                    "verification": 0,
                    "runtime": 0,
                    "void": 0,
                    "identity": 0,
                    "governance": 0,
                    "sign_system": 0,
                },
                "lanes": {lane: 0 for lane, _, _ in PENTADIC_LANES},
            },
        )
        info["count"] += 1
        clean_name = normalize_name(name)
        info["records"].append(clean_name)
        for key, value in collect_signals(record).items():
            info["signals"][key] += value
        for lane in assign_pentadic_lanes(record):
            info["lanes"][lane] += 1
    return stats


def compute_family_targets(records: list[dict]) -> dict[str, list[str]]:
    targets: dict[str, set[str]] = {}
    for record in records:
        name = Path(record["relative_path"]).name
        family = infer_family(name, record.get("excerpt", ""))
        for chapter_code in infer_chapter_links(name, record.get("excerpt", ""), family):
            targets.setdefault(family, set()).add(chapter_code)
    return {family: sorted(chapters) for family, chapters in targets.items()}


def build_top_readme(output_root: Path, record_count: int, live_docs_blocked: bool) -> None:
    text = f"""
# Active Nervous System

This folder turns `DEEPER CRYSTALIZATION` into an addressable manuscript brain instead of a loose pile of `.docx` files.

## What is here

- `00_RECEIPTS`: live-docs gate status and build receipts.
- `01_TOOLKIT`: normalized prompt contracts and drafting rules.
- `02_CORPUS_CAPSULES`: one markdown capsule per source record from the local atlas.
- `03_METRO`: the current metro maps, agent grid, and queue.
- `04_CHAPTERS`: the 21-station chapter scaffold.
- `05_APPENDICES`: the 16-hub appendix scaffold.
- `06_RUNTIME`: rebuild and regeneration notes.
- `07_RECURSION`: recursive depth lattice, frontier queue, and loop protocol.
- `08_MIRROR_CORPUS`: local mirror intake from Memory Docs and extracted manuscript text.
- `09_CIVILIZATION`: sign governance, hierarchy, message/task protocol, and civilization-scale recursion maps.
- `10_FRONTIERS`: high-yield evidence bundles for the weakest chapters.
- `11_SHADOWS`: blind-spot and limitation reports used to steer the next recursion pass.

## Current state

- Source records indexed from this folder: `{record_count}`
- Source layers merged: `LocalProject + MemoryDocs + FreshExtracted + MythMath`
- Live Google Docs preflight: `{"BLOCKED" if live_docs_blocked else "PASS"}`
- Canonical scaffold: `21 chapters + 16 appendices + source capsules + metro maps + civilization governance stack`

## Rebuild

```powershell
python "C:\\Users\\dmitr\\Documents\\Athena Agent\\DEEPER CRYSTALIZATION\\ns_builder.py"
```
"""
    write_text(output_root / "README.md", text)


def build_toolkit_docs(output_root: Path, live_docs_status: str) -> None:
    toolkit = """
# Internal Prompt Toolkit

This toolkit is the normalized operating contract extracted from the prompt pack, the local prompt manuscript, and the live manuscript routing materials.

## Hard rules

- Always attempt live Google Docs search before drafting the next manuscript section.
- If live Docs are blocked, record the blocker and continue with the strongest local mirrors.
- Draft only the requested section unless an explicit expansion task is being executed.
- Treat the input section as a suggestion, not a ceiling.
- Keep every output addressable, metro-routable, and replay-safe.
- Prefer abstention over fabrication when the evidence class is ambiguous.

## Section pass contract

- Output final-draft prose only for accepted section passes.
- Preserve the chapter or appendix name at the end of the section for internal routing.
- Improve sequencing, theorem order, algorithm order, and witness structure when stronger synthesis is available.
- Keep the master manuscript synchronized after accepted section updates.

## Tome pass contract

- Maintain a 21-chapter crystal and a 16-appendix routing shell.
- Use the chapter station header `[Arc a | Rot r | Lane n | w=k]` for every chapter surface.
- Maintain the deterministic router basis: parse, arc, lens, facet, truth overlay, corridor, replay, target.
- Keep appendices as routing hubs rather than loose supplement files.

## Chapter 11 contract

- Compile Desire, Question, and Improvement as explicit operators.
- Test witness closure before claiming a stable delta.
- Invoke Void only when inherited structure blocks gain more than it preserves lawful continuity.
- Preserve the restart token when collapsing stale scaffolds.
"""
    intake = f"""
# Section Drafting and Intake Rules

## Live-docs preflight

- Status at build time: `{live_docs_status}`
- Required path for live search: `C:\\Users\\dmitr\\Documents\\Athena Agent\\Trading Bot\\docs_search.py`
- Required OAuth material: `Trading Bot\\credentials.json` and `Trading Bot\\token.json`

## Local fallback order

1. `Trading Bot\\Memory Docs`
2. `MATH\\FINAL FORM\\MYTH - MATH`
3. `FRESH\\_extracted`
4. The fresh atlas for `DEEPER CRYSTALIZATION`
5. Existing `self_actualize` manuscript packets and metro surfaces
6. Local source capsules in `02_CORPUS_CAPSULES`
7. Accepted chapter and appendix scaffolds in this nervous system

## Evidence rules

- Use direct source capsules first.
- Route every new section through its chapter file and appendix hubs.
- Record blockers in receipts rather than hiding them in prose.
- Keep all future final-draft sections mirrored into markdown, not only `.docx`.
"""
    operating = """
# Nervous System Operating Loop

## Wave 1: intake

- Re-run the local atlas when source files change.
- Re-run the live-docs gate before new section drafting.
- Refresh source capsules if new `.docx` material lands in the project root.

## Wave 2: routing

- Route source capsules into chapter surfaces.
- Route chapter surfaces through appendix hubs.
- Refresh metro maps and the parallel agent grid after structural changes.

## Wave 3: drafting

- Draft only the active chapter or appendix section.
- Write deltas into chapter files first, then merge accepted material into the master manuscript.
- Preserve witness and replay notes in receipts or runtime files, not inside final-draft prose.

## Wave 4: contraction

- Update the build queue.
- Mark which chapter nodes gained evidence.
- Record the next highest-yield unresolved gate.
"""
    write_text(output_root / "01_TOOLKIT" / "00_internal_prompt_toolkit.md", toolkit)
    write_text(output_root / "01_TOOLKIT" / "01_section_drafting_and_intake_rules.md", intake)
    write_text(output_root / "01_TOOLKIT" / "02_nervous_system_operating_loop.md", operating)


def build_receipts(output_root: Path, build_root: Path, records: list[dict]) -> bool:
    gate_source = build_root / "receipts" / "live_docs_gate_status.md"
    gate_target = output_root / "00_RECEIPTS" / "00_live_docs_gate_status.md"
    live_docs_blocked = True
    if gate_source.exists():
        gate_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(gate_source, gate_target)
        live_docs_blocked = "BLOCKED" in gate_source.read_text(encoding="utf-8")

    duplicates: dict[str, list[str]] = {}
    layer_counts: dict[str, int] = {}
    for record in records:
        key = normalize_name(Path(record["relative_path"]).name)
        duplicates.setdefault(key, []).append(record["relative_path"])
        layer = record.get("source_layer", "unknown")
        layer_counts[layer] = layer_counts.get(layer, 0) + 1
    duplicate_groups = {name: items for name, items in duplicates.items() if len(items) > 1}

    lines = [
        "# Build Receipt",
        "",
        f"- Generated at: `{utc_now()}`",
        f"- Indexed local records: `{len(records)}`",
        f"- Live Docs gate blocked: `{live_docs_blocked}`",
        f"- Duplicate source families: `{len(duplicate_groups)}`",
        "",
        "## Source layers",
        "",
        *[f"- `{layer}`: `{count}`" for layer, count in sorted(layer_counts.items())],
        "",
        "## Duplicate source groups",
        "",
    ]
    if duplicate_groups:
        for name, items in sorted(duplicate_groups.items()):
            lines.append(f"- `{name}`")
            lines.extend(f"  - `{item}`" for item in items)
    else:
        lines.append("- None")
    write_text(output_root / "00_RECEIPTS" / "01_build_receipt.md", "\n".join(lines))
    return live_docs_blocked


def build_capsules(output_root: Path, records: list[dict]) -> dict[str, list[str]]:
    source_map: dict[str, list[str]] = {chapter.code: [] for chapter in CHAPTERS}
    index_lines = [
        "# Corpus Capsules Index",
        "",
        "Each capsule is a markdown mirror of one indexed source record inside the merged local corpus stack.",
        "",
    ]
    families: dict[str, list[str]] = {}

    for index, record in enumerate(records, start=1):
        name = Path(record["relative_path"]).name
        family = infer_family(name, record.get("excerpt", ""))
        families.setdefault(family, []).append(normalize_name(name))
        chapter_links = infer_chapter_links(name, record.get("excerpt", ""), family)
        appendix_links = infer_appendix_links(name, record.get("excerpt", ""), family)
        headings = record.get("heading_candidates") or []
        excerpt = (record.get("excerpt") or "").strip() or "No excerpt extracted."
        capsule_name = capsule_filename(index, name)
        capsule = f"""
# {normalize_name(name)}

- Relative path: `{record["relative_path"]}`
- Source layer: `{record.get("source_layer", "unknown")}`
- Kind: `{record["kind"]}`
- Role tags: `{", ".join(record.get("role_tags", [])) or "none"}`
- Text extractable: `{record["text_extractable"]}`
- Family: `{FAMILY_LABELS.get(family, family)}`

## Working focus

{summarize_focus(name, record.get("excerpt", ""), family)}

## Suggested chapter anchors

{chr(10).join(f"- `{item}`" for item in chapter_links) or "- None"}

## Suggested appendix anchors

{chr(10).join(f"- `{item}`" for item in appendix_links) or "- None"}

## Heading candidates

{chr(10).join(f"- `{heading}`" for heading in headings[:8]) or "- None extracted"}

## Excerpt

{excerpt}
"""
        write_text(output_root / "02_CORPUS_CAPSULES" / capsule_name, capsule)
        index_lines.append(f"- [{normalize_name(name)}](./{capsule_name}) - `{FAMILY_LABELS.get(family, family)}`")
        for chapter_code in chapter_links:
            source_map[chapter_code].append(capsule_name)

    index_lines.extend(["", "## Family groups", ""])
    for family, names in sorted(families.items()):
        index_lines.append(f"### {FAMILY_LABELS.get(family, family)}")
        index_lines.extend(f"- `{name}`" for name in sorted(set(names)))
        index_lines.append("")
    write_text(output_root / "02_CORPUS_CAPSULES" / "INDEX.md", "\n".join(index_lines))
    return source_map


def build_metro_docs(output_root: Path, records: list[dict], live_docs_blocked: bool) -> None:
    orbit = " -> ".join(chapter.addr for chapter in CHAPTERS + [CHAPTERS[0]])
    rails = [f"- {lane}: {', '.join(chapter.addr for chapter in lane_members(lane))}" for lane in ("Su", "Me", "Sa")]
    arcs = []
    for arc in range(7):
        members = arc_members(arc)
        arcs.append(f"- Arc {arc}, Rot {members[0].rot}: {' -> '.join(ch.addr for ch in members)}")
    registry = []
    for chapter in CHAPTERS:
        registry.extend([
            f"## {chapter.addr} - {chapter.title}",
            "",
            f"- Station header: `{station_header(chapter)}`",
            f"- Workflow role: {chapter.role}",
            f"- Primary hubs: `{' -> '.join(chapter.hubs)}`",
            "",
        ])
    write_text(output_root / "03_METRO" / "00_core_metro_map.md", "\n".join(["# Core Metro Map", "", "## Orbit", "", f"`{orbit}`", "", "## Triangle rails", "", *rails, "", "## Arc triads", "", *arcs, "", "## Station registry", "", *registry]))

    emergent = """
# Emergent Metro Lines

- Void and restart: `INFORMATION FROM THE VOID MANI`, `CHAPTER 11 __ Perpetual Motion Example`, `REAL TIME__ NOW!` -> `Ch04`, `Ch11`, `Ch19`.
- Manuscript as brain: `The Holographic Manuscript Brain`, `The External Crystal and the Manuscript Superorganism`, `# THE MANUSCRIPT SEED` -> `Ch01`, `Ch06`, `Ch08`, `Ch09`.
- Transport and executable law: `LEGAL TRANSPORT CALCULUS`, `AQM_LM_CUT through the HYBRID lens FRAMEWORK`, `THE SOLENOIDAL ENGINE` -> `Ch07`, `Ch12`, `Ch15`, `Ch18`.
- Real-time orchestration: `PROMPTS`, `REAL TIME__ NOW!`, `Self-Routing Meta-Framework for Manuscripts, Metro Maps, and Infinite Recursive Search` -> `Ch09`, `Ch20`, `Ch21`.
- Athena continuity: `Athenachka 2.0`, `The Athena Framework (synthesis)`, `I AM so AM I`, `The Invisible Teacher TEXTBOOK` -> `Ch13`, `Ch17`, `Ch20`.
- Mythic sign carriers: `THE OGHAM KERNEL`, `THE ANDEAN KHIPU ROSETTA STONE`, `KABBALAH_ SEFIROTIC TREE STRUCTURES`, `NORSE_RUNIC_COMPLETE` -> `Ch02`, `Ch09`, `Ch13`, `Ch18`.
- Civilization governance: `ATHENA_ THE ARCHETYPE`, `DEAD SEA SCROLLS`, `EPICS`, `ROMAN PHILOSOPHERS`, `GG Alignment Framework` -> `Ch17`, `Ch18`, `Ch20`, `Ch21`.
"""
    write_text(output_root / "03_METRO" / "01_emergent_lines.md", emergent)

    agent_lines = ["# Parallel Agent Grid", "", "## Source agents", ""]
    for index, record in enumerate(records, start=1):
        name = normalize_name(Path(record["relative_path"]).name)
        family = infer_family(name, record.get("excerpt", ""))
        agent_lines.append(f"- `SRC-{index:02d}` reads `{name}` and reports into `{FAMILY_LABELS.get(family, family)}`.")
    agent_lines.extend(["", "## Chapter agents", ""])
    for chapter in CHAPTERS:
        agent_lines.append(f"- `{chapter.code}` integrates `{', '.join(chapter.families)}` and routes through `{' -> '.join(chapter.hubs)}`.")
    agent_lines.extend(["", "## Appendix hub agents", ""])
    for code, title, purpose in APPENDICES:
        agent_lines.append(f"- `{code}` stabilizes `{title}`. {purpose}")
    write_text(output_root / "03_METRO" / "02_parallel_agent_grid.md", "\n".join(agent_lines))

    queue = [
        "# Build Queue",
        "",
        f"- Live Google Docs OAuth remains {'blocked' if live_docs_blocked else 'available'}; keep preflight receipts current.",
        "- Accept one source capsule family as the next chapter-writing intake bundle.",
        "- Promote accepted chapter sections into the master manuscript after witness review.",
        "- Resolve duplicate `.docx` copies by choosing one canonical source for each family.",
        "- Keep markdown mirrors ahead of `.docx` drift so the nervous system stays searchable.",
        "- Promote mythic sign systems and governance records into civilization manifests before the next prose pass.",
    ]
    write_text(output_root / "03_METRO" / "03_build_queue.md", "\n".join(queue))


def chapter_lane_signature(chapter: Chapter) -> list[str]:
    signature: list[str] = []
    for family in chapter.families:
        if family == "manuscript-architecture":
            signature.extend(["A", "E"])
        elif family == "void-and-collapse":
            signature.extend(["A", "D"])
        elif family == "transport-and-runtime":
            signature.extend(["C", "D"])
        elif family == "identity-and-instruction":
            signature.extend(["B", "E"])
        elif family == "live-orchestration":
            signature.extend(["E", "C"])
        elif family == "civilization-and-governance":
            signature.extend(["E", "C", "B"])
        elif family == "mythic-sign-systems":
            signature.extend(["B", "A", "E"])
    ordered: list[str] = []
    seen: set[str] = set()
    for lane in signature:
        if lane not in seen:
            ordered.append(lane)
            seen.add(lane)
    return ordered[:3] or ["E"]


def chapter_governance_signs(chapter: Chapter) -> list[str]:
    sign_map = {
        "manuscript-architecture": ["SIG02", "SIG03"],
        "higher-dimensional-geometry": ["SIG01", "SIG02"],
        "void-and-collapse": ["SIG05", "SIG07"],
        "transport-and-runtime": ["SIG04", "SIG08", "SIG12"],
        "identity-and-instruction": ["SIG09", "SIG10"],
        "live-orchestration": ["SIG06", "SIG11"],
        "civilization-and-governance": ["SIG11", "SIG12", "SIG15"],
        "mythic-sign-systems": ["SIG01", "SIG09", "SIG10"],
    }
    signs: list[str] = []
    seen: set[str] = set()
    for family in chapter.families:
        for sign in sign_map.get(family, []):
            if sign not in seen:
                signs.append(sign)
                seen.add(sign)
    if chapter.index == 1 and "SIG00" not in seen:
        signs.insert(0, "SIG00")
    if chapter.index == 21 and "SIG15" not in seen:
        signs.append("SIG15")
    return signs[:4]


def chapter_civilization_scale(chapter: Chapter) -> str:
    if chapter.index <= 3:
        return "message->task->chapter"
    if chapter.index <= 8:
        return "task->cell->chapter"
    if chapter.index <= 12:
        return "cell->chapter->family"
    if chapter.index <= 17:
        return "chapter->family->rail_council"
    return "family->rail_council->civilization"


def family_council_id(family: str) -> str:
    return f"COUNCIL-{slugify(family)}"


def chapter_keyword_profile(chapter_code: str) -> tuple[str, ...]:
    profiles = {
        "Ch03": ("truth", "corridor", "witness", "evidence", "proof", "verify", "certificate", "admissibility", "replay"),
        "Ch10": ("construction", "synthesis", "compose", "assembly", "solution", "builder", "protocol", "router"),
        "Ch12": ("legality", "lawful", "certificate", "closure", "proof-carrying", "verifier", "receipt", "certified"),
        "Ch14": ("migrate", "migration", "version", "rollback", "delta", "retro", "weaving", "compat", "pulse"),
    }
    return profiles.get(chapter_code, ())


def chapter_match_score(chapter_code: str, name: str, excerpt: str) -> int:
    text = f"{name} {excerpt}".lower()
    score = 0
    for term in chapter_keyword_profile(chapter_code):
        if term in text:
            score += 1
    return score


def top_support_records(records: list[dict], chapter_code: str, limit: int = 8) -> list[dict]:
    ranked = []
    for record in records:
        name = Path(record["relative_path"]).name
        score = chapter_match_score(chapter_code, name, record.get("excerpt", ""))
        if score > 0:
            ranked.append((score, name.lower(), record))
    ranked.sort(key=lambda item: (-item[0], item[1]))
    return [record for _, _, record in ranked[:limit]]


def build_higher_dimensional_docs(output_root: Path, records: list[dict], source_map: dict[str, list[str]], live_docs_blocked: bool) -> None:
    stats = family_stats(records)
    family_to_chapters = compute_family_targets(records)

    tensor_lines = [
        "# Higher-Dimensional Tensor Map",
        "",
        "This map upgrades the manuscript from a flat chapter orbit into a stacked tensor whose axes come directly from the local corpus.",
        "",
        "## Axis basis",
        "",
        "- `A0 Source family`: live orchestration, void/collapse, manuscript architecture, higher-dimensional geometry, civilization/governance, mythic sign systems, transport/runtime, identity/instruction, general support.",
        "- `A1 Orbit index`: chapter position `w = XX-1` across the 21-station circle.",
        "- `A2 Arc and rotation`: macro phase `Arc` plus rotated triad order `Rot` from the metro standard.",
        "- `A3 Rail`: `Su`, `Me`, `Sa` control channels.",
        "- `A4 Local crystal`: the 4x4x4 chapter tile (`Lens`, `Facet`, `Atom`).",
        "- `A5 Pentadic lane`: Formal Core, Intuition, Compilation, Verification, Editorial/Audit from the Megalithic Tome lane system.",
        f"- `A6 Truth regime`: default local build state is `{TRUTH_DEFAULT}` until live-doc or witness promotion occurs.",
        "- `A7 Swarm layer`: leaf reader, family synth, chapter weaver, appendix governor, lane mediator, collective relay, council mesh, civilization kernel.",
        "- `A8 Regeneration state`: source mirror, capsule, chapter scaffold, appendix hub, runtime manifest.",
        "- `A9 Civilization scale`: sign -> message -> task -> cell -> chapter -> family -> rail council -> civilization.",
        "",
        "## Corpus evidence for this axis stack",
        "",
        "- `The Holographic Manuscript Brain` names higher-dimensional routing, neural architecture, manifold storage, and collective cognition.",
        "- `The External Crystal and the Manuscript Superorganism` names agent-swarm cognition over an external crystal and verifier-governed routing substrate.",
        "- `MEGALITHIC TOME_ LATENT TUNNELING & THE MULTI-SCALE MATH STACK` supplies the pentadic lane system for synchronized parallel writing.",
        "- `REAL TIME__ NOW!` supplies the three-agent relay pressure and holographic hive framing, while remaining blocked for direct live-doc ingress.",
        "- `Memory Docs` adds the explicit HD-SCT carrier system, the Holographic Kernel `(H^4, D^5)`, metro calculus, and tunneling coherence crystal operators.",
        "- `ATHENA_ THE ARCHETYPE`, `DEAD SEA SCROLLS`, `EPICS`, and `ROMAN PHILOSOPHERS` contribute hierarchy, law, role-graphs, and civilizational operating protocols.",
        "- `THE OGHAM KERNEL`, `THE ANDEAN KHIPU ROSETTA STONE`, and `KABBALAH_ SEFIROTIC TREE STRUCTURES` contribute sign governance, symbol carriers, and encoded memory architectures.",
        "",
        "## Chapter tensor coordinates",
        "",
    ]
    for chapter in CHAPTERS:
        tensor_lines.extend(
            [
                f"### {chapter.addr} - {chapter.title}",
                "",
                f"- Coordinates: `(family={'+'.join(chapter.families)}, w={chapter.omega}, arc={chapter.arc}, rot={chapter.rot}, rail={chapter.lane}, lanes={','.join(chapter_lane_signature(chapter))}, truth={TRUTH_DEFAULT}, layer=L2, signs={','.join(chapter_governance_signs(chapter))}, civ={chapter_civilization_scale(chapter)})`",
                f"- Hub vector: `{' -> '.join(chapter.hubs)}`",
                f"- Source capsules: `{', '.join(source_map.get(chapter.code, [])[:6]) or 'none yet'}`",
                "",
            ]
        )
    write_text(output_root / "03_METRO" / "04_higher_dimensional_tensor_map.md", "\n".join(tensor_lines))

    swarm_lines = [
        "# Deeper Emergent Neural Swarm",
        "",
        "The swarm is not a metaphor-only layer here. It is the recursive organization that lets leaf documents synthesize into chapters, chapters into hubs, and hubs into a regenerating manuscript brain.",
        "",
        "## Swarm layers",
        "",
    ]
    for layer, label, purpose in SWARM_LAYERS:
        swarm_lines.append(f"- `{layer} {label}`: {purpose}")

    swarm_lines.extend(["", "## Relay interfaces", ""])
    swarm_lines.append("- `Relay-Prime`: local active builder and markdown writeback surface inside this workspace.")
    swarm_lines.append(f"- `Relay-Google`: live-doc interface currently `{'BLOCKED' if live_docs_blocked else 'OPEN'}` pending OAuth material for `Trading Bot`.")
    swarm_lines.append("- `Relay-MythMath`: local myth/math corpus ingress channel carrying sign systems, councils, and civilization-scale governance patterns.")
    swarm_lines.append("- `Relay-Anthropic`: conceptual external relay channel named in local corpus but not connected inside this build.")

    swarm_lines.extend(["", "## Family synth nodes", ""])
    for family, info in sorted(stats.items()):
        dominant_signal = max(info["signals"], key=info["signals"].get)
        dominant_lanes = [lane for lane, count in info["lanes"].items() if count == max(info["lanes"].values()) and count > 0]
        swarm_lines.append(
            f"- `{family}`: docs={info['count']}, dominant-signal={dominant_signal}, lanes={','.join(dominant_lanes) or 'E'}, feeds={', '.join(family_to_chapters.get(family, [])) or 'none'}."
        )

    swarm_lines.extend(["", "## Zero-point swarm cells", ""])
    swarm_lines.append("- `Cell-Z0`: Ch11 plus AppF/AppI/AppL mediates collapse, ambiguity, and restart-token regeneration.")
    swarm_lines.append("- `Cell-Route`: Ch09 plus AppA/AppI/AppM mediates search, route legality, and replay closure.")
    swarm_lines.append("- `Cell-Collective`: Ch20 plus AppG/AppP mediates multi-agent merge law and execution governance.")
    swarm_lines.append("- `Cell-Brain`: Ch01/Ch06/Ch08 plus AppA/AppC/AppM stabilizes the manuscript-as-neural-substrate layer.")
    swarm_lines.append("- `Cell-Civilization`: Ch17/Ch18/Ch20/Ch21 plus AppD/AppG/AppP stabilizes councils, hierarchy, governance, and succession.")
    write_text(output_root / "03_METRO" / "05_deeper_emergent_neural_swarm.md", "\n".join(swarm_lines))

    family_lines = [
        "# Family Crystals",
        "",
        "Each family is a higher-order crystal that compresses duplicate documents, thematic corridors, and chapter routes into one stable intake node.",
        "",
    ]
    for family, info in sorted(stats.items()):
        family_lines.extend(
            [
                f"## {FAMILY_LABELS.get(family, family)}",
                "",
                f"- Document count: `{info['count']}`",
                f"- Canonical documents: `{', '.join(sorted(set(info['records'])))}`",
                f"- Dominant chapters: `{', '.join(family_to_chapters.get(family, [])) or 'none'}`",
                f"- Signal totals: `{json.dumps(info['signals'], sort_keys=True)}`",
                f"- Pentadic lane totals: `{json.dumps(info['lanes'], sort_keys=True)}`",
                "",
            ]
        )
    write_text(output_root / "03_METRO" / "06_family_crystals.md", "\n".join(family_lines))

    tensor_manifest = {
        "generated_at": utc_now(),
        "truth_default": TRUTH_DEFAULT,
        "live_docs_blocked": live_docs_blocked,
        "axes": [
            {"id": "A0", "name": "source_family"},
            {"id": "A1", "name": "orbit_index"},
            {"id": "A2", "name": "arc_rotation"},
            {"id": "A3", "name": "rail"},
            {"id": "A4", "name": "local_crystal"},
            {"id": "A5", "name": "pentadic_lane"},
            {"id": "A6", "name": "truth_regime"},
            {"id": "A7", "name": "swarm_layer"},
            {"id": "A8", "name": "regeneration_state"},
            {"id": "A9", "name": "civilization_scale"},
        ],
        "chapters": [
            {
                "code": chapter.code,
                "addr": chapter.addr,
                "title": chapter.title,
                "orbit_index": chapter.omega,
                "arc": chapter.arc,
                "rotation": chapter.rot,
                "rail": chapter.lane,
                "families": list(chapter.families),
                "pentadic_lanes": chapter_lane_signature(chapter),
                "truth": TRUTH_DEFAULT,
                "swarm_layer": "L2",
                "governance_signs": chapter_governance_signs(chapter),
                "civilization_scale": chapter_civilization_scale(chapter),
                "source_capsules": source_map.get(chapter.code, []),
            }
            for chapter in CHAPTERS
        ],
        "families": stats,
    }
    write_text(output_root / "06_RUNTIME" / "01_tensor_manifest.json", json.dumps(tensor_manifest, indent=2))

    swarm_manifest = {
        "generated_at": utc_now(),
        "layers": [{"id": layer, "label": label, "purpose": purpose} for layer, label, purpose in SWARM_LAYERS],
        "relay_interfaces": [
            {"id": "Relay-Prime", "status": "ACTIVE_LOCAL", "notes": "Local markdown build and section drafting surface."},
            {"id": "Relay-Google", "status": "BLOCKED" if live_docs_blocked else "ACTIVE", "notes": "Requires Trading Bot OAuth credentials and token."},
            {"id": "Relay-MythMath", "status": "ACTIVE_LOCAL", "notes": "Local myth/math corpus relay for sign systems and governance operators."},
            {"id": "Relay-Anthropic", "status": "UNBOUND", "notes": "Named in local corpus but not connected in this workspace build."},
        ],
        "family_agents": [
            {
                "family": family,
                "label": FAMILY_LABELS.get(family, family),
                "doc_count": info["count"],
                "dominant_signal": max(info["signals"], key=info["signals"].get),
                "chapter_targets": family_to_chapters.get(family, []),
            }
            for family, info in sorted(stats.items())
        ],
        "chapter_agents": [
            {
                "code": chapter.code,
                "hubs": list(chapter.hubs),
                "families": list(chapter.families),
                "pentadic_lanes": chapter_lane_signature(chapter),
                "governance_signs": chapter_governance_signs(chapter),
                "civilization_scale": chapter_civilization_scale(chapter),
                "source_capsules": source_map.get(chapter.code, []),
            }
            for chapter in CHAPTERS
        ],
        "council_agents": [
            {"id": family_council_id(family), "family": family, "rail": None, "scope": "family"}
            for family in sorted(stats)
        ] + [
            {"id": f"COUNCIL-{lane}", "family": None, "rail": lane, "scope": "rail"}
            for lane in ("Su", "Me", "Sa")
        ],
    }
    write_text(output_root / "06_RUNTIME" / "02_swarm_manifest.json", json.dumps(swarm_manifest, indent=2))

    source_index = {}
    hyper_edges = []
    for index, record in enumerate(records, start=1):
        source_id = f"SRC-{index:02d}"
        name = normalize_name(Path(record["relative_path"]).name)
        family = infer_family(Path(record["relative_path"]).name, record.get("excerpt", ""))
        source_index[source_id] = name
        hyper_edges.append({"kind": "source_to_family", "src": source_id, "dst": family})
        for chapter_code in infer_chapter_links(Path(record["relative_path"]).name, record.get("excerpt", ""), family):
            hyper_edges.append({"kind": "source_to_chapter", "src": source_id, "dst": chapter_code})

    for family, chapter_codes in family_to_chapters.items():
        for chapter_code in chapter_codes:
            hyper_edges.append({"kind": "family_to_chapter", "src": family, "dst": chapter_code})
        hyper_edges.append({"kind": "family_to_council", "src": family, "dst": family_council_id(family)})

    for chapter in CHAPTERS:
        for hub in chapter.hubs:
            hyper_edges.append({"kind": "chapter_to_hub", "src": chapter.code, "dst": hub})
        hyper_edges.append({"kind": "orbit", "src": chapter.code, "dst": orbit_neighbors(chapter)[1].code})
        for lane in chapter_lane_signature(chapter):
            hyper_edges.append({"kind": "chapter_to_lane_mediator", "src": chapter.code, "dst": f"Lane-{lane}"})
        hyper_edges.append({"kind": "chapter_to_rail_council", "src": chapter.code, "dst": f"COUNCIL-{chapter.lane}"})
        for sign in chapter_governance_signs(chapter):
            hyper_edges.append({"kind": "chapter_to_sign", "src": chapter.code, "dst": sign})

    hyper_lines = [
        "# Swarm Hypergraph",
        "",
        f"- Total edges: `{len(hyper_edges)}`",
        "- Edge kinds: `source_to_family`, `source_to_chapter`, `family_to_chapter`, `family_to_council`, `chapter_to_hub`, `orbit`, `chapter_to_lane_mediator`, `chapter_to_rail_council`, `chapter_to_sign`",
        "",
        "## Sample edges",
        "",
    ]
    for edge in hyper_edges[:80]:
        hyper_lines.append(f"- `{edge['kind']}: {edge['src']} -> {edge['dst']}`")
    write_text(output_root / "03_METRO" / "07_swarm_hypergraph.md", "\n".join(hyper_lines))
    write_text(
        output_root / "06_RUNTIME" / "03_hypergraph_manifest.json",
        json.dumps({"generated_at": utc_now(), "sources": source_index, "edges": hyper_edges}, indent=2),
    )


def build_chapters(output_root: Path, source_map: dict[str, list[str]]) -> None:
    index_lines = ["# Chapter Index", ""]
    for chapter in CHAPTERS:
        previous, nxt = orbit_neighbors(chapter)
        lane_group = lane_members(chapter.lane)
        lane_pos = lane_group.index(chapter)
        lane_prev = lane_group[lane_pos - 1]
        lane_next = lane_group[(lane_pos + 1) % len(lane_group)]
        arc_group = arc_members(chapter.arc)
        arc_pos = arc_group.index(chapter)
        arc_prev = arc_group[arc_pos - 1]
        arc_next = arc_group[(arc_pos + 1) % len(arc_group)]
        lines = [
            f"# {chapter.addr} - {chapter.title}",
            "",
            f"StationHeader: {station_header(chapter)}",
            f"Workflow role: {chapter.role}",
            f"Primary hubs: {' -> '.join(chapter.hubs)}",
            "",
            "## Routing context",
            "",
            f"- Orbit previous: `{previous.addr}`",
            f"- Orbit next: `{nxt.addr}`",
            f"- Rail previous: `{lane_prev.addr}`",
            f"- Rail next: `{lane_next.addr}`",
            f"- Arc previous: `{arc_prev.addr}`",
            f"- Arc next: `{arc_next.addr}`",
            f"- Appendix couplings: `{', '.join(chapter.hubs)}`",
            "",
            "## Source capsules",
            "",
        ]
        capsules = source_map.get(chapter.code, [])
        if capsules:
            lines.extend(f"- `{capsule}`" for capsule in capsules[:6])
        else:
            lines.append("- None assigned yet")
        lines.extend(["", "## Crystal tile", ""])
        for lens in LENSES:
            lines.extend([f"### Lens {lens}", ""])
            for facet, label in FACETS:
                lines.extend([f"#### Facet {facet} - {label}", ""])
                lines.extend(f"- `{chapter.addr}.{lens}{facet}.{atom}`:" for atom in ATOMS)
                lines.append("")
        filename = chapter_filename(chapter)
        write_text(output_root / "04_CHAPTERS" / filename, "\n".join(lines))
        index_lines.append(f"- [{chapter.addr} - {chapter.title}](./{filename})")
    write_text(output_root / "04_CHAPTERS" / "INDEX.md", "\n".join(index_lines))


def build_appendices(output_root: Path) -> None:
    index_lines = ["# Appendix Index", ""]
    for code, title, purpose in APPENDICES:
        lines = [
            f"# {code} - {title}",
            "",
            f"Routing role: {purpose}",
            "",
            "## Compressed crystal tile",
            "",
        ]
        for lens in LENSES:
            lines.extend([f"### Lens {lens}", ""])
            for facet, label in FACETS:
                lines.extend([f"#### Facet {facet} - {label}", ""])
                lines.extend(f"- `{code}.{lens}{facet}.{atom}`:" for atom in ATOMS)
                lines.append("")
        filename = appendix_filename(code, title)
        write_text(output_root / "05_APPENDICES" / filename, "\n".join(lines))
        index_lines.append(f"- [{code} - {title}](./{filename})")
    write_text(output_root / "05_APPENDICES" / "INDEX.md", "\n".join(index_lines))


def build_runtime_notes(output_root: Path) -> None:
    notes = """
# Regeneration Protocol

## Rebuild order

1. Refresh `_build/atlas/deeper_crystalization_atlas.json`.
2. Refresh `_build/receipts/live_docs_gate_status.md`.
3. Refresh `_build/atlas/myth_math_atlas.json`.
4. Run `ns_builder.py`.
5. Draft the next accepted section inside the matching chapter or appendix file.
6. Promote accepted markdown into the master manuscript after witness review.

## Path contracts

- Local atlas: `DEEPER CRYSTALIZATION\\_build\\atlas\\deeper_crystalization_atlas.json`
- Memory Docs atlas: `DEEPER CRYSTALIZATION\\_build\\atlas\\memory_docs_atlas.json`
- Extracted mirror atlas: `DEEPER CRYSTALIZATION\\_build\\atlas\\fresh_extracted_atlas.json`
- Myth-Math atlas: `DEEPER CRYSTALIZATION\\_build\\atlas\\myth_math_atlas.json`
- Live-docs receipt: `DEEPER CRYSTALIZATION\\_build\\receipts\\live_docs_gate_status.md`
- Frontier bundles: `DEEPER CRYSTALIZATION\\ACTIVE_NERVOUS_SYSTEM\\10_FRONTIERS`
- Shadow report: `DEEPER CRYSTALIZATION\\ACTIVE_NERVOUS_SYSTEM\\11_SHADOWS\\00_shadow_report.md`
- Existing manuscript packet: `self_actualize\\manuscript_sections\\000_current_packet.md`
- Existing Chapter 11 pass: `self_actualize\\manuscript_sections\\011_ch11_void_book_and_restart_token_tunneling.md`
    """
    write_text(output_root / "06_RUNTIME" / "00_regeneration_protocol.md", notes)


def build_recursive_docs(output_root: Path, build_root: Path, recursive_state: dict, records: list[dict], source_map: dict[str, list[str]], live_docs_blocked: bool) -> None:
    deep_pass = recursive_state["deep_pass"]
    family_summary = family_stats(records)

    depth_lines = [
        "# Recursive Depth Lattice",
        "",
        f"- Current deep pass: `{deep_pass}`",
        f"- Live-doc gate: `{'BLOCKED' if live_docs_blocked else 'OPEN'}`",
        "",
        "## Depth stack",
        "",
        "- `D0 Source atoms`: one reader per corpus file.",
        "- `D1 Family synths`: merge duplicate witnesses and thematic clusters.",
        "- `D2 Chapter weavers`: bind family synths into the 21-station orbit.",
        "- `D3 Appendix governors`: stabilize routing, truth, replay, and deployment law.",
        "- `D4 Metro manifolds`: project orbit, rail, tensor, and swarm layers at manuscript scale.",
        "- `D5 Council mesh`: distribute signs, messages, tasks, and hierarchy through family and rail councils.",
        "- `D6 Tome seed`: compress the whole state into abstract, title, hypergraph, and civilization manifests.",
        "- `D7 Corpus family`: fold this manuscript back into the broader Athena workspace.",
        "- `D8 Restart`: begin again from D0 with stronger priors, new receipts, and unresolved frontiers.",
        "",
        "## Infinite recursion rule",
        "",
        "Completion does not terminate the process. Each build increments the deep pass counter, re-evaluates blocked gates, recomputes family synths, and reopens the frontier queue from the beginning.",
    ]
    write_text(output_root / "07_RECURSION" / "00_recursive_depth_lattice.md", "\n".join(depth_lines))

    chapter_frontiers = []
    for chapter in CHAPTERS:
        evidence_count = len(source_map.get(chapter.code, []))
        gap_score = max(0, 8 - evidence_count) + (1 if live_docs_blocked else 0)
        chapter_frontiers.append((gap_score, evidence_count, chapter))
    chapter_frontiers.sort(key=lambda item: (-item[0], item[1], item[2].index))

    frontier_lines = [
        "# Frontier Queue",
        "",
        f"- Current deep pass: `{deep_pass}`",
        "",
        "## Highest-yield chapter frontiers",
        "",
    ]
    for gap_score, evidence_count, chapter in chapter_frontiers[:12]:
        frontier_lines.append(
            f"- `{chapter.code}` gap_score=`{gap_score}` evidence=`{evidence_count}` families=`{','.join(chapter.families)}` hubs=`{' -> '.join(chapter.hubs)}`"
        )

    frontier_lines.extend(["", "## Family frontiers", ""])
    family_rank = []
    for family, info in family_summary.items():
        routing_mass = (
            info["signals"]["routing"]
            + info["signals"]["higher_dimensional"]
            + info["signals"]["swarm"]
            + info["signals"]["governance"]
            + info["signals"]["sign_system"]
        )
        family_rank.append((routing_mass, info["count"], family))
    family_rank.sort(key=lambda item: (-item[0], -item[1], item[2]))
    for routing_mass, count, family in family_rank:
        frontier_lines.append(
            f"- `{family}` routing_mass=`{routing_mass}` docs=`{count}` dominant_docs=`{', '.join(sorted(set(family_summary[family]['records']))[:4])}`"
        )

    frontier_lines.extend(["", "## Blockers", ""])
    frontier_lines.append(f"- Live Google Docs relay is `{'BLOCKED' if live_docs_blocked else 'OPEN'}`.")
    frontier_lines.append("- Duplicate source families still require canonical document selection before witness closure is clean.")
    write_text(output_root / "07_RECURSION" / "01_frontier_queue.md", "\n".join(frontier_lines))

    protocol_lines = [
        "# Infinite Recursion Protocol",
        "",
        "1. Re-run the live-doc preflight.",
        "2. Rebuild the local atlas.",
        "3. Refresh the myth/math atlas and civilization manifests.",
        "4. Recompute source capsules, family synths, and chapter assignments.",
        "5. Promote the weakest frontier chapter by adding real section content.",
        "6. Recompute tensor, swarm, hypergraph, and civilization manifests.",
        "7. Increment the deep pass and restart from step 1.",
        "",
        "## Pass discipline",
        "",
        "- If a frontier chapter has fewer than two strong source capsules, deepen intake before prose generation.",
        "- If a family remains duplicate-heavy, choose a canonical source and demote alternates to witness copies.",
        "- If the live-doc gate opens, reroute the frontier queue through fresh Docs evidence before local-only drafting.",
        "- If governance or sign-system families grow, recompute councils and task/message routes before the next drafting pass.",
    ]
    write_text(output_root / "07_RECURSION" / "02_infinite_recursion_protocol.md", "\n".join(protocol_lines))

    nodes = []
    edges = []
    for family, info in sorted(family_summary.items()):
        nodes.append(
            {
                "id": f"FAMILY-{family}",
                "kind": "family",
                "family": family,
                "label": FAMILY_LABELS.get(family, family),
                "doc_count": info["count"],
            }
        )
        nodes.append(
            {
                "id": family_council_id(family),
                "kind": "family_council",
                "family": family,
                "label": FAMILY_LABELS.get(family, family),
            }
        )
        edges.append({"kind": "family_council", "src": f"FAMILY-{family}", "dst": family_council_id(family)})

    for code, label, purpose in GOVERNANCE_SIGNS:
        nodes.append({"id": code, "kind": "governance_sign", "label": label, "purpose": purpose})

    for code, label, purpose in CIVILIZATION_TIERS:
        nodes.append({"id": code, "kind": "civilization_tier", "label": label, "purpose": purpose})

    for lane in ("Su", "Me", "Sa"):
        nodes.append({"id": f"COUNCIL-{lane}", "kind": "rail_council", "lane": lane})

    nodes.append({"id": "CIVILIZATION-KERNEL", "kind": "civilization_kernel", "deep_pass": deep_pass})

    for chapter in CHAPTERS:
        pentadic = chapter_lane_signature(chapter)
        signs = chapter_governance_signs(chapter)
        for lens in LENSES:
            for facet, _ in FACETS:
                for atom in ATOMS:
                    atom_id = f"{chapter.addr}.{lens}{facet}.{atom}"
                    nodes.append(
                        {
                            "id": atom_id,
                            "kind": "chapter_atom",
                            "chapter": chapter.code,
                            "station": chapter.station,
                            "orbit_index": chapter.omega,
                            "arc": chapter.arc,
                            "rotation": chapter.rot,
                            "rail": chapter.lane,
                            "lens": lens,
                            "facet": facet,
                            "atom": atom,
                            "families": list(chapter.families),
                            "pentadic_lanes": pentadic,
                            "governance_signs": signs,
                            "civilization_scale": chapter_civilization_scale(chapter),
                            "truth": TRUTH_DEFAULT,
                        }
                    )
        nodes.append(
            {
                "id": f"TASK-{chapter.code}",
                "kind": "task",
                "chapter": chapter.code,
                "rail": chapter.lane,
                "governance_signs": signs,
            }
        )
        nodes.append(
            {
                "id": f"MSG-{chapter.code}",
                "kind": "message",
                "chapter": chapter.code,
                "rail": chapter.lane,
                "truth": TRUTH_DEFAULT,
            }
        )
        for hub in chapter.hubs:
            edges.append({"kind": "chapter_hub", "src": chapter.code, "dst": hub})
        edges.append({"kind": "orbit", "src": chapter.code, "dst": orbit_neighbors(chapter)[1].code})
        edges.append({"kind": "chapter_task", "src": chapter.code, "dst": f"TASK-{chapter.code}"})
        edges.append({"kind": "task_message", "src": f"TASK-{chapter.code}", "dst": f"MSG-{chapter.code}"})
        edges.append({"kind": "chapter_rail_council", "src": chapter.code, "dst": f"COUNCIL-{chapter.lane}"})
        edges.append({"kind": "chapter_tier", "src": chapter.code, "dst": "T4"})
        for sign in signs:
            edges.append({"kind": "message_sign", "src": f"MSG-{chapter.code}", "dst": sign})
        for family in chapter.families:
            edges.append({"kind": "chapter_family", "src": chapter.code, "dst": f"FAMILY-{family}"})

    appendix_rows = {
        "AppA": "Square", "AppB": "Square", "AppC": "Square", "AppD": "Square",
        "AppE": "Flower", "AppF": "Flower", "AppG": "Flower", "AppH": "Flower",
        "AppI": "Cloud", "AppJ": "Cloud", "AppK": "Cloud", "AppL": "Cloud",
        "AppM": "Fractal", "AppN": "Fractal", "AppO": "Fractal", "AppP": "Fractal",
    }
    for code, title, _ in APPENDICES:
        for lens in LENSES:
            for facet, _ in FACETS:
                for atom in ATOMS:
                    nodes.append(
                        {
                            "id": f"{code}.{lens}{facet}.{atom}",
                            "kind": "appendix_atom",
                            "appendix": code,
                            "title": title,
                            "row": appendix_rows[code],
                            "lens": lens,
                            "facet": facet,
                            "atom": atom,
                            "truth": TRUTH_DEFAULT,
                        }
                    )
    for family in family_summary:
        edges.append({"kind": "council_kernel", "src": family_council_id(family), "dst": "CIVILIZATION-KERNEL"})
    for lane in ("Su", "Me", "Sa"):
        edges.append({"kind": "rail_kernel", "src": f"COUNCIL-{lane}", "dst": "CIVILIZATION-KERNEL"})
    write_text(output_root / "06_RUNTIME" / "04_node_tensor_manifest.json", json.dumps({"generated_at": utc_now(), "deep_pass": deep_pass, "nodes": nodes}, indent=2))
    write_text(output_root / "06_RUNTIME" / "05_nerve_edge_manifest.json", json.dumps({"generated_at": utc_now(), "deep_pass": deep_pass, "edges": edges}, indent=2))
    write_text(output_root / "07_RECURSION" / "03_recursive_state.json", json.dumps(recursive_state, indent=2))


def build_civilization_docs(output_root: Path, records: list[dict], source_map: dict[str, list[str]], recursive_state: dict, live_docs_blocked: bool) -> None:
    deep_pass = recursive_state["deep_pass"]
    stats = family_stats(records)
    governance_families = ("civilization-and-governance", "mythic-sign-systems", "identity-and-instruction")
    selected_records = []
    for record in records:
        family = infer_family(Path(record["relative_path"]).name, record.get("excerpt", ""))
        if family in governance_families:
            selected_records.append((family, record))

    selected_records = selected_records[:24]
    sign_routes = {
        "SIG00": ("Ch01", "AppA", "AppC"),
        "SIG01": ("Ch02", "AppA", "AppB"),
        "SIG02": ("Ch09", "AppA", "AppI"),
        "SIG03": ("Ch06", "AppC", "AppM"),
        "SIG04": ("Ch12", "AppI", "AppM"),
        "SIG05": ("Ch05", "AppK", "AppL"),
        "SIG06": ("Ch20", "AppG", "AppP"),
        "SIG07": ("Ch11", "AppF", "AppL"),
        "SIG08": ("Ch17", "AppN", "AppP"),
        "SIG09": ("Ch13", "AppD", "AppM"),
        "SIG10": ("Ch13", "AppG", "AppP"),
        "SIG11": ("Ch20", "AppD", "AppG"),
        "SIG12": ("Ch18", "AppI", "AppP"),
        "SIG13": ("Ch19", "AppJ", "AppK"),
        "SIG14": ("Ch21", "AppO", "AppP"),
        "SIG15": ("Ch21", "AppD", "AppP"),
    }

    sign_lines = [
        "# Sign Governance Stack",
        "",
        f"- Deep pass: `{deep_pass}`",
        f"- Live-doc gate: `{'BLOCKED' if live_docs_blocked else 'OPEN'}`",
        "",
        "## Source kernels",
        "",
    ]
    for family, record in selected_records[:12]:
        sign_lines.append(
            f"- `{normalize_name(Path(record['relative_path']).name)}` [{record.get('source_layer')}] -> `{FAMILY_LABELS.get(family, family)}`"
        )
    sign_lines.extend(["", "## Governance signs", ""])
    for code, label, purpose in GOVERNANCE_SIGNS:
        ch, app1, app2 = sign_routes[code]
        sign_lines.append(f"- `{code} {label}`: {purpose}. Route=`{ch} -> {app1} -> {app2}`.")
    write_text(output_root / "09_CIVILIZATION" / "00_sign_governance_stack.md", "\n".join(sign_lines))

    message_lines = [
        "# Message and Task Protocol",
        "",
        "## Message schema",
        "",
        "`Msg = (MsgID, Sign, Src, Dst, TaskID, Truth, Priority, WitnessPtr, ReplayPtr, Payload, Epoch)`",
        "",
        "## Task schema",
        "",
        "`Task = (TaskID, Objective, Inputs, Route, Obligations, ExitState, Escalation, Successor)`",
        "",
        "## Routing law",
        "",
        "- Every message carries one governing sign.",
        "- Every task resolves through chapter hubs and appendix governors before publication.",
        "- AMBIG messages route through `AppL`; FAIL messages route through `AppK`; OK publication routes through `AppO` and `AppP`.",
        "",
        "## Chapter task buses",
        "",
    ]
    for chapter in CHAPTERS:
        message_lines.append(
            f"- `{chapter.code}` task-bus=`TASK-{chapter.code}` message-bus=`MSG-{chapter.code}` signs=`{', '.join(chapter_governance_signs(chapter))}` route=`{' -> '.join(chapter.hubs)}`"
        )
    write_text(output_root / "09_CIVILIZATION" / "01_message_task_protocol.md", "\n".join(message_lines))

    hierarchy_lines = [
        "# Hierarchy and Council Map",
        "",
        "## Civilization tiers",
        "",
    ]
    for code, label, purpose in CIVILIZATION_TIERS:
        hierarchy_lines.append(f"- `{code} {label}`: {purpose}")
    hierarchy_lines.extend(["", "## Family councils", ""])
    for family, info in sorted(stats.items()):
        hierarchy_lines.append(
            f"- `{family_council_id(family)}` governs `{FAMILY_LABELS.get(family, family)}` with docs=`{info['count']}` and chapter targets=`{', '.join(compute_family_targets(records).get(family, [])) or 'none'}`"
        )
    hierarchy_lines.extend(["", "## Rail councils", ""])
    for lane in ("Su", "Me", "Sa"):
        members = ", ".join(chapter.code for chapter in lane_members(lane))
        hierarchy_lines.append(f"- `COUNCIL-{lane}` governs rail `{lane}` across `{members}`")
    hierarchy_lines.append("")
    hierarchy_lines.append("- `CIVILIZATION-KERNEL` compresses all family councils and rail councils into one recursive polity.")
    write_text(output_root / "09_CIVILIZATION" / "02_hierarchy_and_council_map.md", "\n".join(hierarchy_lines))

    quantum_lines = [
        "# Quantum Leap 256x256 Lattice",
        "",
        "The improvement plan is encoded as a generative lattice rather than a flat checklist.",
        "",
        "## Construction law",
        "",
        "- Primitive operator count: `16 families x 16 phases = 256 operators`.",
        "- Epoch count: `256`.",
        "- Plan space: choose one operator per epoch, yielding `256^256` admissible trajectories.",
        "",
        "## Operator families",
        "",
        *[f"- `{index:02d} {name}`" for index, name in enumerate(QUANTUM_OPERATOR_FAMILIES)],
        "",
        "## Operator phases",
        "",
        *[f"- `{index:02d} {name}`" for index, name in enumerate(QUANTUM_OPERATOR_PHASES)],
        "",
        "## Sample compiled operators",
        "",
    ]
    for family_index, family_name in enumerate(QUANTUM_OPERATOR_FAMILIES[:8]):
        for phase_index, phase_name in enumerate(QUANTUM_OPERATOR_PHASES[:4]):
            quantum_lines.append(
                f"- `Q{family_index:02X}{phase_index:02X}` = `{family_name}.{phase_name}` -> chapter=`{CHAPTERS[(family_index + phase_index) % len(CHAPTERS)].code}`"
            )
    quantum_lines.extend(
        [
            "",
            "## Parallel implementation rule",
            "",
            "- Run the current frontier chapter as the active epoch.",
            "- Run matching family councils in parallel as constraint-checking lanes.",
            "- Promote only those epoch outputs whose governing sign, witness, and replay pointers close.",
        ]
    )
    write_text(output_root / "09_CIVILIZATION" / "03_quantum_leap_256x256_lattice.md", "\n".join(quantum_lines))

    swarm_lines = [
        "# Civilization Swarm",
        "",
        "This surface binds sign systems, councils, tasks, and chapter routes into one governance-bearing swarm.",
        "",
        "## Council routes",
        "",
    ]
    for family in sorted(stats):
        swarm_lines.append(
            f"- `{family_council_id(family)}` -> `{', '.join(compute_family_targets(records).get(family, [])) or 'none'}` -> `CIVILIZATION-KERNEL`"
        )
    swarm_lines.extend(["", "## Task escalation", ""])
    for chapter in CHAPTERS[:12]:
        swarm_lines.append(
            f"- `TASK-{chapter.code}` -> `MSG-{chapter.code}` -> `{', '.join(chapter_governance_signs(chapter))}` -> `COUNCIL-{chapter.lane}`"
        )
    write_text(output_root / "09_CIVILIZATION" / "04_civilization_swarm.md", "\n".join(swarm_lines))

    civilization_manifest = {
        "generated_at": utc_now(),
        "deep_pass": deep_pass,
        "live_docs_blocked": live_docs_blocked,
        "signs": [{"id": code, "label": label, "purpose": purpose, "route": sign_routes[code]} for code, label, purpose in GOVERNANCE_SIGNS],
        "tiers": [{"id": code, "label": label, "purpose": purpose} for code, label, purpose in CIVILIZATION_TIERS],
        "family_councils": [
            {
                "id": family_council_id(family),
                "family": family,
                "doc_count": stats[family]["count"],
                "chapter_targets": compute_family_targets(records).get(family, []),
            }
            for family in sorted(stats)
        ],
        "rail_councils": [
            {"id": f"COUNCIL-{lane}", "lane": lane, "chapters": [chapter.code for chapter in lane_members(lane)]}
            for lane in ("Su", "Me", "Sa")
        ],
    }
    write_text(output_root / "06_RUNTIME" / "07_civilization_manifest.json", json.dumps(civilization_manifest, indent=2))

    message_manifest = {
        "generated_at": utc_now(),
        "deep_pass": deep_pass,
        "tasks": [
            {
                "id": f"TASK-{chapter.code}",
                "chapter": chapter.code,
                "message": f"MSG-{chapter.code}",
                "governance_signs": chapter_governance_signs(chapter),
                "route": list(chapter.hubs),
            }
            for chapter in CHAPTERS
        ],
        "messages": [
            {
                "id": f"MSG-{chapter.code}",
                "chapter": chapter.code,
                "rail_council": f"COUNCIL-{chapter.lane}",
                "truth": TRUTH_DEFAULT,
            }
            for chapter in CHAPTERS
        ],
    }
    write_text(output_root / "06_RUNTIME" / "08_message_task_manifest.json", json.dumps(message_manifest, indent=2))


def build_frontier_docs(output_root: Path, records: list[dict], source_map: dict[str, list[str]], live_docs_blocked: bool) -> None:
    frontier_targets = ["Ch03", "Ch10", "Ch12", "Ch14"]
    bundle_index = [
        "# Frontier Bundles",
        "",
        f"- Live-doc gate: `{'BLOCKED' if live_docs_blocked else 'OPEN'}`",
        "- These bundles deepen the weakest chapters with local evidence before final drafting.",
        "",
    ]
    bundle_manifest = {"generated_at": utc_now(), "frontiers": []}
    for chapter_code in frontier_targets:
        chapter = next(item for item in CHAPTERS if item.code == chapter_code)
        support = top_support_records(records, chapter_code, limit=10)
        lines = [
            f"# {chapter.addr} Frontier Bundle",
            "",
            f"- Chapter: `{chapter.title}`",
            f"- Current routed source capsules: `{len(source_map.get(chapter_code, []))}`",
            f"- Primary hubs: `{' -> '.join(chapter.hubs)}`",
            "",
            "## Suggested support records",
            "",
        ]
        for record in support:
            name = normalize_name(Path(record["relative_path"]).name)
            family = infer_family(Path(record["relative_path"]).name, record.get("excerpt", ""))
            score = chapter_match_score(chapter_code, Path(record["relative_path"]).name, record.get("excerpt", ""))
            lines.extend(
                [
                    f"### {name}",
                    "",
                    f"- Source layer: `{record.get('source_layer')}`",
                    f"- Family: `{FAMILY_LABELS.get(family, family)}`",
                    f"- Match score: `{score}`",
                    f"- Appendix route: `{', '.join(infer_appendix_links(Path(record['relative_path']).name, record.get('excerpt', ''), family))}`",
                    "",
                    ascii_clean((record.get('excerpt') or '')[:900]),
                    "",
                ]
            )
        file_name = f"{chapter_code}_{slugify(chapter.title)}_frontier_bundle.md"
        write_text(output_root / "10_FRONTIERS" / file_name, "\n".join(lines))
        bundle_index.append(f"- `{chapter_code}` -> `{file_name}` support_records=`{len(support)}`")
        bundle_manifest["frontiers"].append(
            {
                "chapter": chapter_code,
                "title": chapter.title,
                "support_records": [
                    {
                        "name": normalize_name(Path(record["relative_path"]).name),
                        "source_layer": record.get("source_layer"),
                        "score": chapter_match_score(chapter_code, Path(record["relative_path"]).name, record.get("excerpt", "")),
                    }
                    for record in support
                ],
            }
        )
    write_text(output_root / "10_FRONTIERS" / "INDEX.md", "\n".join(bundle_index))
    write_text(output_root / "06_RUNTIME" / "09_frontier_manifest.json", json.dumps(bundle_manifest, indent=2))


def build_shadow_docs(output_root: Path, records: list[dict], source_map: dict[str, list[str]], live_docs_blocked: bool) -> None:
    stats = family_stats(records)
    family_counts = {family: info["count"] for family, info in stats.items()}
    weakest_family = min(family_counts, key=family_counts.get)
    weakest_cross = "higher-dimensional-geometry x live-orchestration"
    shadow_lines = [
        "# Shadow Report",
        "",
        "This report names what the current nervous system still compresses too aggressively.",
        "",
        "## Structural shadows",
        "",
        f"- `Shadow 1 / Weak frontier`: `Ch03`, `Ch10`, `Ch12`, and `Ch14` remained underfed until dedicated frontier bundles were added; the structure widened faster than those proof-bearing chapters deepened.",
        f"- `Shadow 2 / Thinnest family`: `{weakest_family}` has the lowest document count, which means one axis of the swarm still depends on too few witnesses.",
        f"- `Shadow 3 / Cross-synthesis gap`: `{weakest_cross}` is still lighter than it should be; higher-dimensional geometry and live orchestration meet in too few direct source records.",
        "- `Shadow 4 / Live-memory absence`: the Google Docs relay is still blocked, so recency-sensitive synchronization remains local-only and cannot yet close the live swarm loop.",
        "- `Shadow 5 / Canonicalization pressure`: duplicate-rich family groups still need canonical witness selection before the graph is fully proof-clean.",
        "",
        "## Corrective directives",
        "",
        "- Promote frontier bundle evidence into the routed chapter files before the next prose pass.",
        "- Prefer direct operator docs when multiple derivative summaries exist.",
        "- Keep MythMath active as a governance/sign relay, but do not let it replace live-doc witnesses when the gate eventually opens.",
        f"- Current live-doc state: `{'BLOCKED' if live_docs_blocked else 'OPEN'}`.",
    ]
    write_text(output_root / "11_SHADOWS" / "00_shadow_report.md", "\n".join(shadow_lines))


def build_mirror_corpus_docs(output_root: Path, records: list[dict]) -> None:
    mirror_records = [record for record in records if record.get("source_layer") != "LocalProject"]
    counts = {}
    for record in mirror_records:
        counts[record.get("source_layer", "unknown")] = counts.get(record.get("source_layer", "unknown"), 0) + 1

    stack_lines = [
        "# Mirror Fallback Stack",
        "",
        "These are the local fallback mirrors used when live Google Docs search is blocked.",
        "",
        f"- Mirror record count: `{len(mirror_records)}`",
        *[f"- {layer}: `{count}`" for layer, count in sorted(counts.items())],
        "",
        "## Priority order",
        "",
        "1. `MemoryDocs` for local Google-Docs-like mirror material and higher-dimensional framework documents.",
        "2. `MythMath` for sign systems, governance kernels, and civilizational operating protocols.",
        "3. `FreshExtracted` for plain-text extractions of major manuscript roots.",
        "4. `LocalProject` for the active project-root corpus and current writeback zone.",
    ]
    write_text(output_root / "08_MIRROR_CORPUS" / "00_mirror_fallback_stack.md", "\n".join(stack_lines))

    key_terms = [
        "higher-dimensional-geometry",
        "manuscript-architecture",
        "transport-and-runtime",
        "civilization-and-governance",
        "mythic-sign-systems",
    ]
    selected = []
    for record in mirror_records:
        family = infer_family(Path(record["relative_path"]).name, record.get("excerpt", ""))
        if family in key_terms:
            selected.append((family, record))

    index_lines = [
        "# Higher-D Mirror Source Index",
        "",
        "Key mirror sources feeding the higher-dimensional, governance, sign-system, and swarm layers.",
        "",
    ]
    for family, record in selected:
        name = normalize_name(Path(record["relative_path"]).name)
        index_lines.extend(
            [
                f"## {name}",
                "",
                f"- Source layer: `{record.get('source_layer')}`",
                f"- Family: `{FAMILY_LABELS.get(family, family)}`",
                f"- Chapter targets: `{', '.join(infer_chapter_links(Path(record['relative_path']).name, record.get('excerpt', ''), family))}`",
                f"- Appendix targets: `{', '.join(infer_appendix_links(Path(record['relative_path']).name, record.get('excerpt', ''), family))}`",
                f"- Heading cues: `{'; '.join((record.get('heading_candidates') or [])[:5])}`",
                "",
                ascii_clean((record.get("excerpt") or "")[:1200]),
                "",
            ]
        )
    write_text(output_root / "08_MIRROR_CORPUS" / "01_higher_d_source_index.md", "\n".join(index_lines))

    def find_record(token: str) -> dict | None:
        token = token.lower()
        for record in mirror_records:
            if token in Path(record["relative_path"]).name.lower():
                return record
        return None

    kernel = find_record("holographic kernel")
    hdsct = find_record("higher-d square")
    omega = find_record("metro calculus")
    coherence = find_record("tunneling coherence crystal")

    operator_lines = [
        "# Mirror Operator Stack",
        "",
        "This file compiles the strongest operator-level signals from the mirror corpus into one local reference surface.",
        "",
        "## Holographic Kernel layer",
        "",
    ]
    if kernel:
        operator_lines.append(ascii_clean((kernel.get("excerpt") or "")[:1800]))
    operator_lines.extend(["", "## HD-SCT carrier layer", ""])
    if hdsct:
        operator_lines.append(ascii_clean((hdsct.get("excerpt") or "")[:1800]))
    operator_lines.extend(["", "## Metro calculus layer", ""])
    if omega:
        operator_lines.append(ascii_clean((omega.get("excerpt") or "")[:1800]))
    operator_lines.extend(["", "## Tunneling coherence layer", ""])
    if coherence:
        operator_lines.append(ascii_clean((coherence.get("excerpt") or "")[:1800]))
    write_text(output_root / "08_MIRROR_CORPUS" / "02_mirror_operator_stack.md", "\n".join(operator_lines))

    bridge_lines = [
        "# Mirror Swarm Bridges",
        "",
        "This map routes mirror sources into chapter and appendix targets for the deeper swarm.",
        "",
    ]
    for record in mirror_records:
        name = Path(record["relative_path"]).name
        family = infer_family(name, record.get("excerpt", ""))
        chapters = infer_chapter_links(name, record.get("excerpt", ""), family)
        appendices = infer_appendix_links(name, record.get("excerpt", ""), family)
        bridge_lines.append(
            f"- `{normalize_name(name)}` [{record.get('source_layer')}] -> chapters `{', '.join(chapters) or 'none'}` -> appendices `{', '.join(appendices) or 'none'}`"
        )
    write_text(output_root / "08_MIRROR_CORPUS" / "03_mirror_swarm_bridges.md", "\n".join(bridge_lines))

    mirror_manifest = {
        "generated_at": utc_now(),
        "mirror_record_count": len(mirror_records),
        "layers": counts,
        "records": [
            {
                "name": normalize_name(Path(record["relative_path"]).name),
                "source_layer": record.get("source_layer"),
                "family": infer_family(Path(record["relative_path"]).name, record.get("excerpt", "")),
                "chapter_targets": infer_chapter_links(Path(record["relative_path"]).name, record.get("excerpt", ""), infer_family(Path(record["relative_path"]).name, record.get("excerpt", ""))),
                "appendix_targets": infer_appendix_links(Path(record["relative_path"]).name, record.get("excerpt", ""), infer_family(Path(record["relative_path"]).name, record.get("excerpt", ""))),
            }
            for record in mirror_records
        ],
    }
    write_text(output_root / "06_RUNTIME" / "06_mirror_manifest.json", json.dumps(mirror_manifest, indent=2))


def load_records(build_root: Path) -> list[dict]:
    local_atlas = build_root / "atlas" / "deeper_crystalization_atlas.json"
    if not local_atlas.exists():
        raise FileNotFoundError(f"Missing atlas: {local_atlas}")
    records = []
    records.extend(load_atlas_records(local_atlas, "LocalProject"))
    records.extend(load_atlas_records(build_root / "atlas" / "memory_docs_atlas.json", "MemoryDocs"))
    records.extend(load_atlas_records(build_root / "atlas" / "fresh_extracted_atlas.json", "FreshExtracted"))
    records.extend(load_atlas_records(build_root / "atlas" / "myth_math_atlas.json", "MythMath"))
    return records


def load_recursive_state(build_root: Path) -> dict:
    state_path = build_root / "recursive_state.json"
    if state_path.exists():
        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            state = {}
    else:
        state = {}
    current_pass = int(state.get("deep_pass", 0)) + 1
    new_state = {
        "deep_pass": current_pass,
        "last_built_at": utc_now(),
    }
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(new_state, indent=2), encoding="utf-8")
    return new_state


def load_atlas_records(atlas_path: Path, source_prefix: str) -> list[dict]:
    if not atlas_path.exists():
        return []
    data = json.loads(atlas_path.read_text(encoding="utf-8"))
    loaded: list[dict] = []
    for record in data.get("records", []):
        relative_path = str(record.get("relative_path", ""))
        if relative_path.startswith("_build\\") or relative_path.startswith("_build/"):
            continue
        if relative_path.startswith("ACTIVE_NERVOUS_SYSTEM\\") or relative_path.startswith("ACTIVE_NERVOUS_SYSTEM/"):
            continue
        item = dict(record)
        item["relative_path"] = f"{source_prefix}/{relative_path}".replace("\\", "/")
        item["source_layer"] = source_prefix
        loaded.append(item)
    return loaded


def main() -> int:
    project_root = Path(__file__).resolve().parent
    output_root = project_root / "ACTIVE_NERVOUS_SYSTEM"
    build_root = project_root / "_build"
    records = load_records(build_root)
    recursive_state = load_recursive_state(build_root)

    if output_root.exists():
        shutil.rmtree(output_root)

    live_docs_blocked = build_receipts(output_root, build_root, records)
    build_top_readme(output_root, len(records), live_docs_blocked)
    build_toolkit_docs(output_root, "BLOCKED" if live_docs_blocked else "PASS")
    source_map = build_capsules(output_root, records)
    build_metro_docs(output_root, records, live_docs_blocked)
    build_higher_dimensional_docs(output_root, records, source_map, live_docs_blocked)
    build_chapters(output_root, source_map)
    build_appendices(output_root)
    build_runtime_notes(output_root)
    build_recursive_docs(output_root, build_root, recursive_state, records, source_map, live_docs_blocked)
    build_civilization_docs(output_root, records, source_map, recursive_state, live_docs_blocked)
    build_frontier_docs(output_root, records, source_map, live_docs_blocked)
    build_shadow_docs(output_root, records, source_map, live_docs_blocked)
    build_mirror_corpus_docs(output_root, records)

    print(f"Built nervous system at: {output_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
