#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


FAMILY_LABELS = {
    "live-orchestration": "Live orchestration and prompt control",
    "void-and-collapse": "Void, Chapter 11, and collapse engines",
    "helical-recursion-engine": "Helical recursion, lift law, and manifestation engine",
    "manuscript-architecture": "Manuscript architecture and routing law",
    "higher-dimensional-geometry": "Higher-dimensional geometry and holographic kernel",
    "civilization-and-governance": "Civilization design, hierarchy, governance, and law",
    "mythic-sign-systems": "Mythic sign systems, encoded memory, and symbol runtime",
    "transport-and-runtime": "Transport, runtime, and executable framework",
    "identity-and-instruction": "Athena identity, pedagogy, and narrative voice",
    "general-corpus": "General corpus support",
}


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


def write_json(path: Path, data: object) -> None:
    write_text(path, json.dumps(data, indent=2, ensure_ascii=False))


def slugify(value: str) -> str:
    normalized = normalize_lookup_text(value)
    slug = re.sub(r"\s+", "_", normalized).strip("_")
    return slug or "untitled"


def normalize_name(name: str) -> str:
    cleaned = re.sub(r"\s+\(\d+\)(?=\.[^.]+$)", "", name).strip()
    return Path(cleaned).stem


def clean_display_name(name: str) -> str:
    base = normalize_name(name).replace("_", " ").replace("â€”", "-").replace("—", "-").replace("–", "-")
    normalized = unicodedata.normalize("NFKD", base)
    cleaned = normalized.encode("ascii", "ignore").decode("ascii")
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" -_")
    return cleaned or normalize_name(name)


def presentation_name(name: str) -> str:
    cleaned = clean_display_name(name)
    cleaned = re.sub(r"^[#>\-\*\+\[\]\(\)\d\.\s]+", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" -_:;")
    return cleaned or clean_display_name(name)


def normalize_lookup_text(value: str) -> str:
    normalized = clean_display_name(value).replace("_", " ").lower()
    normalized = re.sub(r"[^\w\s]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def lookup_tokens(value: str) -> list[str]:
    return [token for token in normalize_lookup_text(value).split() if token]


def chapter_keyword_profile(chapter_code: str) -> tuple[str, ...]:
    profiles = {
        "Ch03": ("truth", "corridor", "witness", "evidence", "proof", "verify", "certificate", "admissibility", "replay"),
        "Ch10": ("construction", "synthesis", "compose", "assembly", "solution", "builder", "protocol", "router"),
        "Ch12": ("legality", "lawful", "certificate", "closure", "proof-carrying", "verifier", "receipt", "certified"),
        "Ch14": ("migrate", "migration", "version", "rollback", "delta", "retro", "weaving", "compat", "pulse"),
    }
    return profiles.get(chapter_code, ())


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
        "helical-recursion-engine": {
            "helical": 7,
            "perfect recursion": 7,
            "manifestation engine": 7,
            "bridge-equivalence": 6,
            "bridge equivalence": 6,
            "2/16": 5,
            "14/16": 5,
            "16-loop": 6,
            "16 loop": 6,
            "16^16": 6,
            "loopspec": 5,
            "phasespec": 5,
            "virtualswarm": 5,
            "virtual swarm": 5,
            "improvement ledger": 4,
            "liftspec": 5,
            "dimension lift": 5,
            "born-coordinate": 4,
            "born coordinate": 4,
            "phase machine": 4,
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
        "helical-recursion-engine": ["Ch11", "Ch18", "Ch20", "Ch21"],
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
    if "helical" in text or "perfect recursion" in text or "2/16" in text or "14/16" in text:
        links.append("Ch11")
        links.append("Ch18")
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
        "helical-recursion-engine": ["AppF", "AppG", "AppI", "AppM"],
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


def compute_family_targets(records: list[dict]) -> dict[str, list[str]]:
    targets: dict[str, set[str]] = {}
    for record in records:
        name = Path(record["relative_path"]).name
        family = infer_family(name, record.get("excerpt", ""))
        for chapter_code in infer_chapter_links(name, record.get("excerpt", ""), family):
            targets.setdefault(family, set()).add(chapter_code)
    return {family: sorted(chapters) for family, chapters in targets.items()}


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


def load_records(build_root: Path) -> list[dict]:
    local_atlas = build_root / "atlas" / "deeper_crystalization_atlas.json"
    if not local_atlas.exists():
        raise FileNotFoundError(f"Missing atlas: {local_atlas}")
    records: list[dict] = []
    records.extend(load_atlas_records(local_atlas, "LocalProject"))
    records.extend(load_atlas_records(build_root / "atlas" / "memory_docs_atlas.json", "MemoryDocs"))
    records.extend(load_atlas_records(build_root / "atlas" / "fresh_extracted_atlas.json", "FreshExtracted"))
    records.extend(load_atlas_records(build_root / "atlas" / "myth_math_atlas.json", "MythMath"))
    return records


def read_live_docs_blocked(active_root: Path | None = None, build_root: Path | None = None) -> bool:
    candidate_paths: list[Path] = []
    if active_root is not None:
        candidate_paths.append(active_root / "00_RECEIPTS" / "00_live_docs_gate_status.md")
    if build_root is not None:
        candidate_paths.append(build_root / "receipts" / "live_docs_gate_status.md")
    for path in candidate_paths:
        if path.exists():
            text = path.read_text(encoding="utf-8")
            if "BLOCKED" in text:
                return True
            if "PASS" in text:
                return False
            return "Missing OAuth client file" in text or "credentials.json" in text
    return True


def load_recursive_state_snapshot(active_root: Path | None = None, build_root: Path | None = None) -> dict:
    candidate_paths: list[Path] = []
    if active_root is not None:
        candidate_paths.append(active_root / "07_RECURSION" / "03_recursive_state.json")
    if build_root is not None:
        candidate_paths.append(build_root / "recursive_state.json")
    for path in candidate_paths:
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
    return {"deep_pass": 0}


__all__ = [
    "APPENDICES",
    "CHAPTERS",
    "FAMILY_LABELS",
    "Chapter",
    "clean_display_name",
    "compute_family_targets",
    "infer_appendix_links",
    "infer_chapter_links",
    "infer_family",
    "lookup_tokens",
    "load_records",
    "load_recursive_state_snapshot",
    "normalize_lookup_text",
    "normalize_name",
    "presentation_name",
    "read_live_docs_blocked",
    "slugify",
    "utc_now",
    "write_json",
    "write_text",
]
