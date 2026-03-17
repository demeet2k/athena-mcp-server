#!/usr/bin/env python3
"""Build a four-element manuscript synthesis network from the Memory Docs corpus."""

from __future__ import annotations

import argparse
import json
import re
import textwrap
import zipfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
import xml.etree.ElementTree as ET


DOC_NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
OUTPUT_DIRNAME = "MANUSCRIPT_ELEMENTAL_NET_4X4"
MODES = ["kernel", "dynamics", "verification", "navigation"]
ELEMENTS = {
    "fire": {
        "definition": (
            "Fire reads the corpus as actuation, ignition, risky transform, "
            "rotation, forcing, and irreversible phase change."
        ),
        "question": "What does this manuscript make happen when the system moves?",
    },
    "water": {
        "definition": (
            "Water reads the corpus as cyclic flow, resonance, tunneling, "
            "continuity, timing, recursion, and weather-like adaptation."
        ),
        "question": "How does this manuscript let states flow, recur, or resonate?",
    },
    "earth": {
        "definition": (
            "Earth reads the corpus as kernel, law, proof, certification, "
            "stability, invariants, and replay-deterministic structure."
        ),
        "question": "What makes this manuscript hold, verify, and remain lawful?",
    },
    "air": {
        "definition": (
            "Air reads the corpus as abstraction, symbolic routing, mapping, "
            "interfaces, topology, navigation, and cross-corpus translation."
        ),
        "question": "How does this manuscript name, map, and connect the system?",
    },
}
MODE_DESCRIPTIONS = {
    "kernel": "Ontological basis, primitives, axioms, state objects, and minimal generators.",
    "dynamics": "Transforms, flows, rotations, tunnels, phase shifts, and recursive motion.",
    "verification": "Certificates, invariants, proof carriers, legality checks, and obstruction tests.",
    "navigation": "Metro maps, interface routes, projections, stations, corpus traversal, and UI layers.",
}
APPENDIX_LETTERS = "ABCDEFGHIJKLMNOP"
STOPWORDS = {
    "about",
    "after",
    "again",
    "against",
    "also",
    "always",
    "among",
    "because",
    "been",
    "before",
    "being",
    "between",
    "both",
    "build",
    "built",
    "can",
    "cannot",
    "carry",
    "carries",
    "chapter",
    "claim",
    "complete",
    "contract",
    "cycle",
    "data",
    "does",
    "each",
    "engine",
    "figure",
    "first",
    "form",
    "forms",
    "from",
    "framework",
    "function",
    "functions",
    "have",
    "into",
    "itself",
    "kernel",
    "layer",
    "law",
    "like",
    "make",
    "many",
    "map",
    "maps",
    "metro",
    "more",
    "must",
    "next",
    "now",
    "object",
    "objects",
    "only",
    "over",
    "part",
    "phase",
    "proof",
    "route",
    "same",
    "section",
    "seed",
    "state",
    "states",
    "such",
    "system",
    "that",
    "their",
    "them",
    "then",
    "there",
    "these",
    "they",
    "this",
    "those",
    "through",
    "time",
    "tome",
    "under",
    "using",
    "what",
    "when",
    "where",
    "which",
    "while",
    "with",
    "your",
}


@dataclass(frozen=True)
class Manuscript:
    doc_id: str
    slug: str
    title: str
    relative_path: str
    primary: bool
    summary: str
    cluster: str
    elements: tuple[str, ...]
    modes: tuple[str, ...]
    motifs: tuple[str, ...]
    stations: tuple[str, ...]
    role: str


CORPUS: list[Manuscript] = [
    Manuscript(
        "M01",
        "higher-d-square-circle-triangle",
        "HIGHER-D SQUARE CIRCLE TRIANGLE",
        "Memory Docs/HIGHER-D SQUARE ○ CIRCLE △ TRIANGLE.docx",
        True,
        "Defines the core shape grammar, holographic metro navigation, and higher-dimensional operator lattice.",
        "geometry",
        ("air", "earth"),
        ("kernel", "navigation", "verification"),
        ("shape-grammar", "higher-d", "hologram", "metro", "invariants"),
        ("Shape Lattice", "Corpus Metro", "Operator Junction"),
        "Foundational geometry and navigation manual.",
    ),
    Manuscript(
        "M02",
        "holographic-reality-structure",
        "Holographic Reality Structure",
        "Memory Docs/Holographic (higher dimension Square_circle_triangle) REALITY STRUCTURE _working_.docx",
        True,
        "Restates the corpus as a self-similar octave hologram in which every scale repeats the whole.",
        "geometry",
        ("water", "air"),
        ("kernel", "dynamics"),
        ("octave", "self-similarity", "hologram", "nexus", "reality"),
        ("Octave Nexus", "Reality Loop", "Scale Bridge"),
        "Cosmological restatement of the shape framework.",
    ),
    Manuscript(
        "M03",
        "legal-transport-calculus",
        "LEGAL TRANSPORT CALCULUS",
        "Memory Docs/LEGAL TRANSPORT CALCULUS.docx",
        True,
        "Builds a proof-carrying transport law so representations can move without semantic drift.",
        "transport",
        ("earth", "air"),
        ("kernel", "verification", "navigation"),
        ("transport", "lawfulness", "certificates", "replay", "representation"),
        ("Law Gate", "Receipt Corridor", "Replay Spine"),
        "Legal and deterministic movement of meaning.",
    ),
    Manuscript(
        "M04",
        "pi-algorithm-engine",
        "Pi Algorithm Engine",
        "Memory Docs/Pi algorithm engine.docx",
        True,
        "Treats pi as a fast-converging arithmetic engine and symbolic seed for the larger holographic compiler.",
        "numeric",
        ("earth", "fire"),
        ("kernel", "dynamics", "verification"),
        ("pi", "series", "convergence", "engine", "compiler"),
        ("Pi Seed", "Series Chamber", "Convergence Ramp"),
        "Numerical seed engine and convergence layer.",
    ),
    Manuscript(
        "M05",
        "prime-toolkit-kernel",
        "PRIME Toolkit Kernel",
        "Memory Docs/PRIME Toolkit kernel.docx",
        True,
        "Compresses many projections into a single kernel-state machine governed by a fixed contract.",
        "numeric",
        ("earth",),
        ("kernel", "verification"),
        ("prime", "kernel", "state-machine", "contract", "projection"),
        ("Prime Kernel", "Contract Latch", "Projection Port"),
        "Compact kernel-state formalism.",
    ),
    Manuscript(
        "M06",
        "quad-holographic-rotation",
        "QUAD HOLOGRAPHIC ROTATION",
        "Memory Docs/QUAD HOLOGRAPHIC ROTATION.docx",
        True,
        "Frames rotation as conjugacy inside a proof-carrying holographic transform calculus with a 256-operation crystal.",
        "dynamics",
        ("fire", "earth"),
        ("dynamics", "verification"),
        ("rotation", "conjugacy", "quad", "256", "transform"),
        ("Rotation Core", "Conjugacy Loop", "256 Crystal"),
        "Actuation layer for controlled transform.",
    ),
    Manuscript(
        "M07",
        "four-constants-final",
        "THE 4 CONSTANTS FINAL",
        "Memory Docs/THE 4 CONSTANTS FINAL (phi, pi, i, e).docx",
        True,
        "Packages phi, pi, i, and e as a compact basis for a hologram compiler and 4x4 archetype grid.",
        "numeric",
        ("earth", "fire"),
        ("kernel", "verification", "navigation"),
        ("constants", "phi", "pi", "e", "archetype-grid"),
        ("Constant Quartet", "Compiler Bed", "Archetype Grid"),
        "Constant basis and 4x4 lattice seed.",
    ),
    Manuscript(
        "M08",
        "holographic-kernel",
        "The Holographic Kernel",
        "Memory Docs/The Holographic Kernel.docx",
        True,
        "Provides a verified transform framework for constrained state spaces, admissible morphisms, and reproducible computation.",
        "geometry",
        ("earth", "air"),
        ("kernel", "verification", "navigation"),
        ("state-space", "morphisms", "invariants", "computation", "verification"),
        ("State Hub", "Morph Gate", "Invariant Console"),
        "Formal transform kernel and admissible morphism engine.",
    ),
    Manuscript(
        "M09",
        "unified-cyclical-time-system",
        "THE UNIFIED CYCLICAL TIME SYSTEM",
        "Memory Docs/THE UNIFIED CYCLICAL TIME SYSTEM (hologram time).docx",
        True,
        "Unifies civilizational time systems as interfaces over a deeper fractal archetypal clock.",
        "time",
        ("water", "air"),
        ("dynamics", "navigation"),
        ("time", "cycles", "archetypes", "calendar", "fractal"),
        ("Root Cycle", "Archetype Wheel", "Calendar Bridge"),
        "Cross-tradition time UI layer.",
    ),
    Manuscript(
        "M10",
        "six-dimensional-hologram",
        "6 Dimensional Hologram",
        "Memory Docs/working/6 dimensional hologram(1).docx",
        True,
        "Expands the transform algebra beyond base-4 into a base-6 octahedral regime.",
        "geometry",
        ("air", "fire"),
        ("kernel", "dynamics"),
        ("base-6", "octahedral", "transform", "geometry", "projection"),
        ("Base-6 Port", "Octahedral Hub", "Projection Ramp"),
        "Higher-resolution transform algebra.",
    ),
    Manuscript(
        "M11",
        "calculus-and-geometry",
        "Calculus and Geometry",
        "Memory Docs/working/Calculus and Geometry (higher dimensional projection) -working-.docx",
        True,
        "Explains square roots, stacked cubes, and higher-dimensional projection as a single geometric-calculus story.",
        "geometry",
        ("air", "earth"),
        ("kernel", "navigation"),
        ("projection", "sqrt", "dimensions", "geometry", "calculus"),
        ("Root Ladder", "Projection Cube", "Dimension Step"),
        "Interpretive bridge between diagrams and formalism.",
    ),
    Manuscript(
        "M12",
        "holographic-tunneling",
        "HOLOGRAPHIC TUNNELING",
        "Memory Docs/working/HOLOGRAPHIC TUNNELING _working_.docx",
        True,
        "Shows how higher dimension and higher phase resolution reveal tunnels hidden at coarse scale.",
        "dynamics",
        ("fire", "water"),
        ("dynamics", "verification"),
        ("tunneling", "phase-resolution", "dimension", "octave", "visibility"),
        ("Tunnel Mouth", "Phase Dial", "Octave Lift"),
        "Phase-resolution upgrade path.",
    ),
    Manuscript(
        "M13",
        "time-fractal",
        "TIME FRACTAL",
        "Memory Docs/working/TIME FRACTAL _working_.docx",
        True,
        "Argues that time is a holographic phase object whose same weather repeats across scales.",
        "time",
        ("water", "air"),
        ("dynamics", "navigation"),
        ("time", "weather", "fractal", "phase", "zoom-lens"),
        ("Phase Weather", "Scale Spiral", "Lens Exchange"),
        "Master convergence note for time-as-phase.",
    ),
    Manuscript(
        "M14",
        "omega-metro-calculus",
        "Omega Metro Calculus",
        "Memory Docs/Ω_ Metro Calculus.docx",
        True,
        "Provides a lawful transport framework for proof-carrying mathematics and obstruction-driven discovery.",
        "transport",
        ("earth", "air"),
        ("kernel", "verification", "navigation"),
        ("omega", "metro", "transport", "obstruction", "determinism"),
        ("Omega Spine", "Obstruction Switch", "Discovery Junction"),
        "Metro-layer generalization of lawful transport.",
    ),
    Manuscript(
        "M15",
        "omega-tunneling-coherence-crystal",
        "Omega Tunneling Coherence Crystal",
        "Memory Docs/Ω_ Tunneling Coherence Crystal.docx",
        True,
        "Links representation duality, corridor tunneling, hybrid generators, and certified cross-sandbox integration.",
        "transport",
        ("earth", "fire", "water"),
        ("dynamics", "verification", "navigation"),
        ("coherence", "duality", "tunneling", "crystal", "integration"),
        ("Coherence Chamber", "Duality Gate", "Sandbox Bridge"),
        "Hybrid bridge between tunnel dynamics and legal transport.",
    ),
    Manuscript(
        "M16",
        "constant-finder",
        "Constant Finder",
        "Memory Docs/Constant FInder _working_.docx",
        True,
        "Constructs a commutation witness, verifier, and promotion protocol for certified constants.",
        "numeric",
        ("earth", "air"),
        ("kernel", "verification"),
        ("constants", "commutation", "witness", "verifier", "promotion"),
        ("Witness Box", "Promotion Gate", "Commutation Hall"),
        "Verifier pipeline for discovered constants.",
    ),
    Manuscript(
        "M17",
        "astrological-tunneling",
        "Astrological Tunneling",
        "Memory Docs/Astrological Tunneling (octave system).docx",
        False,
        "Acts as an auxiliary lens that projects zodiac/octave compatibility tables onto the time-phase corpus.",
        "time",
        ("water", "air"),
        ("dynamics", "navigation"),
        ("astrology", "compatibility", "octave", "signs", "mapping"),
        ("Zodiac Wheel", "Octave Overlay", "Compatibility Lens"),
        "Auxiliary overlay rather than a primary crystal manuscript.",
    ),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--workspace-root",
        default=".",
        help="Workspace root containing 'Memory Docs' and the desired output folder.",
    )
    parser.add_argument(
        "--output-dir",
        default=OUTPUT_DIRNAME,
        help="Directory name (under workspace root) for generated output.",
    )
    return parser.parse_args()


def extract_docx_paragraphs(path: Path) -> list[str]:
    with zipfile.ZipFile(path) as zf:
        xml = zf.read("word/document.xml")
    tree = ET.fromstring(xml)
    paragraphs: list[str] = []
    for paragraph in tree.findall(".//w:p", DOC_NS):
        texts = [node.text or "" for node in paragraph.findall(".//w:t", DOC_NS)]
        merged = re.sub(r"\s+", " ", "".join(texts)).strip()
        if merged:
            paragraphs.append(merged)
    return paragraphs


def find_best_headings(paragraphs: list[str], limit: int = 8) -> list[str]:
    headings: list[str] = []
    for paragraph in paragraphs:
        if len(paragraph) > 110:
            continue
        if paragraph.count(" ") > 14:
            continue
        if paragraph in headings:
            continue
        headings.append(paragraph)
        if len(headings) == limit:
            break
    return headings


def top_keywords(text: str, limit: int = 12) -> list[str]:
    tokens = re.findall(r"[A-Za-z][A-Za-z-]{2,}", text.lower())
    counts = Counter(token for token in tokens if token not in STOPWORDS)
    return [token for token, _ in counts.most_common(limit)]


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write(path: Path, content: str) -> None:
    ensure_dir(path.parent)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def short_preview(paragraphs: list[str], limit: int = 3, chars: int = 520) -> str:
    preview = " | ".join(paragraphs[:limit]).strip()
    return preview[:chars]


def md_link(rel_path: str, label: str) -> str:
    return f"[{label}]({rel_path.replace(' ', '%20')})"


def subset_name(items: tuple[str, ...]) -> str:
    return "-".join(items)


def build_corpus_metadata(workspace_root: Path) -> dict[str, dict]:
    metadata: dict[str, dict] = {}
    for manuscript in CORPUS:
        doc_path = workspace_root / manuscript.relative_path
        paragraphs = extract_docx_paragraphs(doc_path)
        text = "\n".join(paragraphs)
        metadata[manuscript.doc_id] = {
            "path": str(doc_path),
            "paragraphs": paragraphs,
            "text": text,
            "word_count": len(text.split()),
            "paragraph_count": len(paragraphs),
            "headings": find_best_headings(paragraphs),
            "top_keywords": top_keywords(text),
            "preview": short_preview(paragraphs),
        }
    return metadata


def build_readme(primary_docs: list[Manuscript], aux_docs: list[Manuscript]) -> str:
    return textwrap.dedent(
        f"""
        # Manuscript Elemental Net 4x4

        This folder is the working neural-net scaffold for the manuscript corpus in `Memory Docs`.
        It treats the project as a four-element, four-mode crystal lattice built from `{len(primary_docs)}` primary manuscripts and `{len(aux_docs)}` auxiliary lens manuscript.

        ## What is in here

        - `00_CONTROL`: Corpus canon, execution law, and elemental assignments.
        - `01_SOURCE_EXTRACTS`: Full plain-text markdown extracts of the source `.docx` manuscripts.
        - `02_INDIVIDUAL_SYNTHESIS`: One synthesis card per source manuscript.
        - `03_PAIRWISE_SYNERGIES`: The ordered `16 x 16` primary lattice, including diagonal self-resonance cells.
        - `04_ELEMENTS`: Four elemental folders, each with an overview and `64` observation cells.
        - `05_SYMMETRIES`: Neutral pass, the `15` non-empty elemental symmetries, and the zero-point compression route.
        - `06_METRO_MAPS`: Four resolutions of the corpus metro map.
        - `07_APPENDICES`: Appendices `A-P` as the 4x4 crystal grid, plus appendix `Q` as the appendix-only integrated metro map.
        - `08_ZERO_POINT`: Neutral compression and irreducible invariant layer.
        - `09_AUXILIARY_LENSES`: The non-primary manuscript overlays that still inform the system.
        - `10_INDEXES`: Pairwise matrix and machine-readable corpus index.

        ## How to read it

        Start with `00_CONTROL/01_CORPUS_CANON.md`, then `00_CONTROL/02_EXECUTION_MODEL.md`, then the level maps in `06_METRO_MAPS`.
        From there, drop into any individual synthesis, pair cell, elemental observation field, or appendix crystal.

        ## Why the structure looks like this

        Your request asked for a deeper integrated neural net rather than a single prose note.
        This build therefore stores the combinatorics as a navigable lattice:

        - Neutral pass: one `64`-cell observation field.
        - Elemental passes: four additional `64`-cell observation fields.
        - Symmetry layer: all `15` non-empty element combinations.
        - Pairwise layer: the ordered `16 x 16` crystal matrix.
        - Zero point: the irreducible compression of the full system.
        """
    ).strip()


def build_corpus_canon(
    primary_docs: list[Manuscript], aux_docs: list[Manuscript], metadata: dict[str, dict]
) -> str:
    primary_lines = []
    for manuscript in primary_docs:
        meta = metadata[manuscript.doc_id]
        primary_lines.append(
            f"- `{manuscript.doc_id}` `{manuscript.title}` | {manuscript.cluster} | "
            f"{meta['word_count']} words | elements `{', '.join(manuscript.elements)}` | {manuscript.summary}"
        )
    aux_lines = []
    for manuscript in aux_docs:
        meta = metadata[manuscript.doc_id]
        aux_lines.append(
            f"- `{manuscript.doc_id}` `{manuscript.title}` | auxiliary lens | "
            f"{meta['word_count']} words | elements `{', '.join(manuscript.elements)}` | {manuscript.summary}"
        )
    primary_block = "\n".join(primary_lines)
    aux_block = "\n".join(aux_lines)
    return textwrap.dedent(
        f"""
        # Corpus Canon

        The primary crystal lattice uses `{len(primary_docs)}` manuscripts so the pair matrix can resolve cleanly as a `16 x 16` field.
        One additional document remains in the corpus as an auxiliary overlay rather than a lattice crystal.

        ## Primary Crystal Manuscripts

        {primary_block}

        ## Auxiliary Overlay

        {aux_block}

        ## Canon Rule

        A document enters the primary lattice when it behaves like a generative manuscript:

        - it defines operators, invariants, routes, or systemic laws
        - it can seed one or more appendix crystals
        - it cross-synthesizes directly with the proof, time, geometry, or transport stack

        The auxiliary overlay remains important, but it is routed as a lens over the lattice instead of occupying one of the 16 crystal slots.
        """
    ).strip()


def build_execution_model() -> str:
    return textwrap.dedent(
        """
        # Execution Model

        This network operationalizes the deeper-integration request as a layered synthesis machine rather than a single monolith.

        ## Pass 1: Neutral 64

        The neutral field observes each of the 16 primary manuscripts through the four operating modes:

        - `16 manuscripts x 4 modes = 64 neutral observations`

        ## Passes 2-5: Elemental 64s

        Each element re-observes the same 64-cell field through its own logic:

        - `Fire`: actuation, forced transform, rotation, ignition
        - `Water`: resonance, recurrence, continuity, phase weather
        - `Earth`: lawfulness, invariants, proof, stable kernel
        - `Air`: routing, mapmaking, symbolic interface, translation

        That yields:

        - `4 elemental lenses x 64 observations each = 256 elemental observations`

        ## Symmetry Layer

        The four elements are then synthesized in every non-empty combination:

        - `4` single-element syntheses
        - `6` two-way symmetries
        - `4` three-way symmetries
        - `1` four-way symmetry

        Total:

        - `15` symmetry syntheses

        ## Pairwise Layer

        The core lattice is an ordered `16 x 16` field:

        - rows are source manuscripts
        - columns are target manuscripts
        - diagonal cells show self-resonance
        - off-diagonal cells show directional bridge logic

        ## Zero Point

        The last step asks: what survives if geometry, proof, transport, time, arithmetic, and tunnel logic are compressed into one irreducible invariant?
        That answer lives in `08_ZERO_POINT`.

        ## Practical note

        A literal prose dump of every combinatoric variant would be unreadable.
        This build instead stores the combinatorics as indexed, navigable markdown so deeper passes can continue without collapsing into noise.
        """
    ).strip()


def build_elemental_assignments(primary_docs: list[Manuscript], aux_docs: list[Manuscript]) -> str:
    by_element: dict[str, list[str]] = defaultdict(list)
    by_mode: dict[str, list[str]] = defaultdict(list)
    for manuscript in primary_docs + aux_docs:
        for element in manuscript.elements:
            by_element[element].append(f"`{manuscript.doc_id}` {manuscript.title}")
        for mode in manuscript.modes:
            by_mode[mode].append(f"`{manuscript.doc_id}` {manuscript.title}")
    element_sections = []
    for element, info in ELEMENTS.items():
        element_sections.append(
            f"## {element.title()}\n\n"
            f"{info['definition']}\n\n"
            f"Assigned manuscripts:\n\n- " + "\n- ".join(by_element[element])
        )
    mode_sections = []
    for mode in MODES:
        mode_sections.append(
            f"## {mode.title()}\n\n"
            f"{MODE_DESCRIPTIONS[mode]}\n\n"
            f"Assigned manuscripts:\n\n- " + "\n- ".join(by_mode[mode])
        )
    return "\n\n".join(
        ["# Elemental Assignments", *element_sections, *mode_sections]
    )


def build_source_extract(manuscript: Manuscript, meta: dict) -> str:
    headings = "\n".join(f"- {item}" for item in meta["headings"]) or "- No short headings detected."
    return textwrap.dedent(
        f"""
        # {manuscript.title}

        - `doc_id`: `{manuscript.doc_id}`
        - `source`: `{manuscript.relative_path}`
        - `primary crystal`: `{"yes" if manuscript.primary else "no"}`
        - `cluster`: `{manuscript.cluster}`
        - `elements`: `{", ".join(manuscript.elements)}`
        - `modes`: `{", ".join(manuscript.modes)}`
        - `word_count`: `{meta["word_count"]}`
        - `paragraph_count`: `{meta["paragraph_count"]}`

        ## Quick Preview

        {meta["preview"]}

        ## Early Headings

        {headings}

        ## Extracted Text

        {meta["text"]}
        """
    ).strip()


def suggested_links(manuscript: Manuscript, primary_docs: list[Manuscript]) -> list[Manuscript]:
    ranked: list[tuple[int, Manuscript]] = []
    for other in primary_docs:
        if other.doc_id == manuscript.doc_id:
            continue
        score = 0
        score += len(set(manuscript.motifs) & set(other.motifs)) * 3
        score += len(set(manuscript.elements) & set(other.elements)) * 2
        score += len(set(manuscript.modes) & set(other.modes)) * 2
        if manuscript.cluster == other.cluster:
            score += 3
        ranked.append((score, other))
    ranked.sort(key=lambda item: (-item[0], item[1].doc_id))
    return [item[1] for item in ranked[:4]]


def build_individual_synthesis(
    manuscript: Manuscript, meta: dict, primary_docs: list[Manuscript]
) -> str:
    related = suggested_links(manuscript, primary_docs)
    related_lines = "\n".join(
        f"- `{other.doc_id}` {other.title}: {other.summary}" for other in related
    )
    keywords = ", ".join(meta["top_keywords"]) or "none detected"
    stations = "\n".join(f"- {station}" for station in manuscript.stations)
    headings = "\n".join(f"- {heading}" for heading in meta["headings"][:6]) or "- No short headings detected."
    return textwrap.dedent(
        f"""
        # {manuscript.doc_id} - {manuscript.title}

        ## Core Thesis

        {manuscript.summary}

        ## Functional Role

        {manuscript.role}

        ## Source Signals

        - Word count: `{meta["word_count"]}`
        - Paragraph count: `{meta["paragraph_count"]}`
        - Top keywords: `{keywords}`
        - Primary elements: `{", ".join(manuscript.elements)}`
        - Primary modes: `{", ".join(manuscript.modes)}`

        ## Extracted Headings

        {headings}

        ## Elemental Reading

        - Fire: {"active" if "fire" in manuscript.elements else "supporting/latent"}
        - Water: {"active" if "water" in manuscript.elements else "supporting/latent"}
        - Earth: {"active" if "earth" in manuscript.elements else "supporting/latent"}
        - Air: {"active" if "air" in manuscript.elements else "supporting/latent"}

        ## Metro Stations

        {stations}

        ## Most Likely Cross-Links

        {related_lines}

        ## Contribution To The Larger Net

        This manuscript contributes to the `{manuscript.cluster}` cluster and acts as a `{manuscript.role.lower()}`.
        It should be read as one projection of the same wider machine:

        - geometry decides what kind of object exists
        - dynamics decides how it moves
        - verification decides what changes remain lawful
        - navigation decides how the corpus can traverse and expose the whole
        """
    ).strip()


def pair_relation(a: Manuscript, b: Manuscript) -> tuple[str, str, str]:
    shared_motifs = sorted(set(a.motifs) & set(b.motifs))
    shared = ", ".join(shared_motifs) if shared_motifs else "no direct motif overlap"
    if a.doc_id == b.doc_id:
        bridge = "Self-resonance: the manuscript amplifies its own primitives across all four modes."
    elif a.cluster == b.cluster:
        bridge = "Same-cluster resonance: both texts describe the same subsystem at different resolutions."
    else:
        bridge = (
            f"Cross-cluster bridge: `{a.cluster}` hands off into `{b.cluster}` so "
            "one subsystem can constrain or interpret the other."
        )
    tension = (
        f"`{a.title}` emphasizes {a.elements[0]} while `{b.title}` emphasizes {b.elements[0]}, "
        "so the bridge must keep motion and law from drifting apart."
    )
    return shared, bridge, tension


def build_pair_doc(a: Manuscript, b: Manuscript, output_rel: str, source_rel: str) -> str:
    shared, bridge, tension = pair_relation(a, b)
    common_elements = ", ".join(sorted(set(a.elements) & set(b.elements))) or "none"
    common_modes = ", ".join(sorted(set(a.modes) & set(b.modes))) or "none"
    return textwrap.dedent(
        f"""
        # {a.doc_id} -> {b.doc_id}

        ## Direction

        Source manuscript: `{a.title}`
        Target manuscript: `{b.title}`

        ## Shared Anchors

        - Shared motifs: `{shared}`
        - Shared elements: `{common_elements}`
        - Shared modes: `{common_modes}`

        ## Bridge Logic

        {bridge}

        ## Productive Tension

        {tension}

        ## Suggested Route

        - Depart from `{a.stations[0]}`
        - Pass through the bridge condition named by the pair logic
        - Arrive at `{b.stations[0]}`

        ## Follow-On Files

        - Source card: {source_rel}
        - Pair lattice home: {output_rel}
        """
    ).strip()


def observation_line(manuscript: Manuscript, element: str, mode: str) -> str:
    shared_elements = "native" if element in manuscript.elements else "translated"
    shared_modes = "native" if mode in manuscript.modes else "projected"
    return (
        f"- `{manuscript.doc_id}` in `{mode}` mode through `{element}` sees "
        f"{manuscript.title} as a {shared_elements}/{shared_modes} contribution: "
        f"{manuscript.summary}"
    )


def build_element_lens(element: str, primary_docs: list[Manuscript]) -> str:
    docs = [item for item in primary_docs if element in item.elements]
    lines = "\n".join(f"- `{item.doc_id}` {item.title}: {item.summary}" for item in docs)
    return textwrap.dedent(
        f"""
        # {element.title()} Lens

        {ELEMENTS[element]["definition"]}

        Guiding question:

        - {ELEMENTS[element]["question"]}

        ## Native Manuscripts

        {lines}
        """
    ).strip()


def build_64_observations(primary_docs: list[Manuscript], element: str | None = None) -> str:
    lines = []
    for manuscript in primary_docs:
        for mode in MODES:
            if element is None:
                lines.append(
                    f"- `{manuscript.doc_id}` in `{mode}` mode neutrally observes {manuscript.summary}"
                )
            else:
                lines.append(observation_line(manuscript, element, mode))
    title = "Neutral 64 Observations" if element is None else f"{element.title()} 64 Observations"
    return f"# {title}\n\n" + "\n".join(lines)


def symmetry_docs(primary_docs: list[Manuscript]) -> dict[str, str]:
    docs: dict[str, str] = {}
    order = 1
    for width in range(1, 5):
        for combo in combinations(ELEMENTS.keys(), width):
            subset = set(combo)
            members = [item for item in primary_docs if subset & set(item.elements)]
            combo_name = subset_name(combo)
            header = f"{order:02d}_{combo_name}.md"
            member_lines = "\n".join(
                f"- `{item.doc_id}` {item.title}: read through `{combo_name}` because it activates "
                f"{', '.join(sorted(subset & set(item.elements)))}."
                for item in members
            )
            docs[header] = textwrap.dedent(
                f"""
                # Symmetry: {combo_name}

                This symmetry compresses the corpus through the element set `{combo_name}`.
                It is one of the `15` non-empty elemental syntheses.

                ## Effect

                - participating elements: `{', '.join(combo)}`
                - active manuscripts: `{len(members)}`

                ## Members

                {member_lines}
                """
            ).strip()
            order += 1
    return docs


def mermaid_level_1(primary_docs: list[Manuscript]) -> str:
    doc_nodes = []
    edges = []
    for manuscript in primary_docs:
        doc_nodes.append(f'{manuscript.doc_id}["{manuscript.doc_id} {manuscript.title}"]')
        for element in manuscript.elements:
            edges.append(f"{element.upper()} --> {manuscript.doc_id}")
    return "\n".join(
        [
            "```mermaid",
            "flowchart LR",
            'FIRE["Fire"]',
            'WATER["Water"]',
            'EARTH["Earth"]',
            'AIR["Air"]',
            *doc_nodes,
            *edges,
            "```",
        ]
    )


def mermaid_level_2(primary_docs: list[Manuscript]) -> str:
    lines = ["```mermaid", "flowchart LR"]
    for mode in MODES:
        lines.append(f'{mode.upper()}["{mode.title()}"]')
    for manuscript in primary_docs:
        lines.append(f'{manuscript.doc_id}["{manuscript.doc_id}"]')
        for mode in manuscript.modes:
            lines.append(f"{mode.upper()} --> {manuscript.doc_id}")
        for element in manuscript.elements:
            lines.append(f'{element.upper()}["{element.title()}"]')
            lines.append(f"{element.upper()} --> {manuscript.doc_id}")
    lines.append("```")
    return "\n".join(dict.fromkeys(lines))


def mermaid_level_3(primary_docs: list[Manuscript]) -> str:
    lines = ["```mermaid", "flowchart LR", 'ZERO["Zero Point"]']
    for manuscript in primary_docs:
        lines.append(f'{manuscript.doc_id}["{manuscript.doc_id}"]')
        lines.append(f"{manuscript.doc_id} --> ZERO")
    for subset in combinations(ELEMENTS.keys(), 2):
        key = subset_name(subset).upper().replace("-", "_")
        label = " + ".join(part.title() for part in subset)
        lines.append(f'{key}["{label}"]')
        for element in subset:
            lines.append(f'{element.upper()}["{element.title()}"]')
            lines.append(f"{element.upper()} --> {key}")
        lines.append(f"{key} --> ZERO")
    lines.append("```")
    return "\n".join(dict.fromkeys(lines))


def mermaid_level_4() -> str:
    return "\n".join(
        [
            "```mermaid",
            "flowchart LR",
            'FIRE["Fire"] --> ZERO["Zero Point"]',
            "WATER --> ZERO",
            "EARTH --> ZERO",
            "AIR --> ZERO",
            'KERNEL["Kernel"] --> ZERO',
            'DYNAMICS["Dynamics"] --> ZERO',
            'VERIFICATION["Verification"] --> ZERO',
            'NAVIGATION["Navigation"] --> ZERO',
            'ZERO --> RETURN["Return To Corpus"]',
            "```",
        ]
    )


def build_metro_maps(primary_docs: list[Manuscript]) -> dict[str, str]:
    return {
        "00_level_1_metro_map.md": textwrap.dedent(
            f"""
            # Level 1 Metro Map

            The first map shows the coarse relationship between the four elements and the 16 crystal manuscripts.

            {mermaid_level_1(primary_docs)}
            """
        ).strip(),
        "01_level_2_emergence_metro_map.md": textwrap.dedent(
            f"""
            # Level 2 Emergence Metro Map

            The second map resolves manuscripts not only by element but also by operating mode.

            {mermaid_level_2(primary_docs)}
            """
        ).strip(),
        "02_level_3_transcendence_metro_map.md": textwrap.dedent(
            f"""
            # Level 3 Transcendence Metro Map

            The third map shows pairwise symmetry corridors collapsing toward the zero point.

            {mermaid_level_3(primary_docs)}
            """
        ).strip(),
        "03_level_4_transcendent_metro_map.md": textwrap.dedent(
            f"""
            # Level 4 Transcendent Metro Map

            The fourth map compresses the system to its elemental and modal irreducibles.

            {mermaid_level_4()}
            """
        ).strip(),
    }


def appendix_slots() -> list[tuple[str, str, str]]:
    slots = []
    index = 0
    for element in ELEMENTS.keys():
        for mode in MODES:
            slots.append((APPENDIX_LETTERS[index], element, mode))
            index += 1
    return slots


def build_appendix_doc(letter: str, element: str, mode: str, primary_docs: list[Manuscript]) -> str:
    feeders = [item for item in primary_docs if element in item.elements or mode in item.modes]
    feeder_lines = "\n".join(
        f"- `{item.doc_id}` {item.title}: {item.summary}" for item in feeders[:8]
    )
    return (
        f"# Appendix {letter}: {element.title()} x {mode.title()}\n\n"
        "## Crystal Function\n\n"
        f"This appendix occupies the `{element}` / `{mode}` crystal slot.\n"
        "It stores source fragments, routes, and synthesis prompts for the question:\n\n"
        f"- {ELEMENTS[element]['question']}\n"
        f"- Mode emphasis: {MODE_DESCRIPTIONS[mode]}\n\n"
        "## Feeder Manuscripts\n\n"
        f"{feeder_lines}\n\n"
        "## Skeleton Outline\n\n"
        "- Scope and entry conditions\n"
        "- Canonical primitives\n"
        "- Allowed transforms\n"
        "- Verification and failure cases\n"
        "- Metro entry stations\n"
        "- Cross-links to adjacent crystal appendices\n"
        "- Zero-point residue"
    )


def build_appendix_q() -> str:
    lines = ["# Appendix Q: Integrated Appendix Metro Map", ""]
    for letter, element, mode in appendix_slots():
        lines.append(f"- Appendix {letter}: `{element}` x `{mode}`")
    lines.extend(
        [
            "",
            "## Route Law",
            "",
            "- Travel horizontally to change mode while holding the same element.",
            "- Travel vertically to change element while holding the same mode.",
            "- Diagonal travel represents symmetry synthesis and should route through `05_SYMMETRIES`.",
            "- Return to `08_ZERO_POINT` when a path becomes overfit or redundant.",
        ]
    )
    return "\n".join(lines)


def build_zero_point(primary_docs: list[Manuscript]) -> str:
    doc_lines = "\n".join(
        f"- `{item.doc_id}` {item.title}: contributes {', '.join(item.motifs[:3])}"
        for item in primary_docs
    )
    return textwrap.dedent(
        f"""
        # Zero Point Synthesis

        The zero point is the claim that the corpus is not many disconnected manuscripts.
        It is one generator seen through different projection rules.

        ## What survives compression

        - There is always a lawful state object.
        - There is always an allowed transform family.
        - There is always an invariant or certificate that decides whether movement is valid.
        - There is always a navigation layer that lets the observer re-enter the whole from a part.
        - Time behaves like phase; geometry behaves like grammar; proof behaves like custody.

        ## Contributors

        {doc_lines}

        ## Zero-Point Formula

        `object + transform + invariant + route = corpus minimum`
        """
    ).strip()


def build_auxiliary_doc(manuscript: Manuscript, meta: dict, primary_docs: list[Manuscript]) -> str:
    carriers = [
        item for item in primary_docs
        if item.cluster == "time" or "water" in item.elements or "air" in item.elements
    ]
    carrier_lines = "\n".join(
        f"- `{item.doc_id}` {item.title}: {item.summary}" for item in carriers
    )
    return (
        f"# Auxiliary Lens: {manuscript.title}\n\n"
        "This document remains part of the corpus, but it acts as an overlay rather than one of the 16 crystal manuscripts.\n\n"
        "## Why it is auxiliary\n\n"
        "- It projects symbolic compatibility tables more than it defines a new generative calculus.\n"
        "- It is best used as a UI lens over the time-phase subsystem.\n"
        "- It strengthens interpretation, but it does not need its own permanent crystal slot.\n\n"
        "## Source Signals\n\n"
        f"- Word count: `{meta['word_count']}`\n"
        f"- Preview: {meta['preview']}\n\n"
        "## Best Carriers In The Primary Lattice\n\n"
        f"{carrier_lines}"
    )


def build_pairwise_matrix(primary_docs: list[Manuscript]) -> str:
    headers = ["src->dst"] + [doc.doc_id for doc in primary_docs]
    rows = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row_doc in primary_docs:
        cells = [row_doc.doc_id]
        for col_doc in primary_docs:
            filename = f"{row_doc.doc_id.lower()}__to__{col_doc.doc_id.lower()}.md"
            rel = f"../03_PAIRWISE_SYNERGIES/{filename}"
            cells.append(md_link(rel, f"{row_doc.doc_id}->{col_doc.doc_id}"))
        rows.append("| " + " | ".join(cells) + " |")
    return "# Pairwise Matrix\n\n" + "\n".join(rows)


def build_index_json(primary_docs: list[Manuscript], aux_docs: list[Manuscript], metadata: dict[str, dict]) -> str:
    payload = {
        "primary_count": len(primary_docs),
        "auxiliary_count": len(aux_docs),
        "documents": [],
    }
    for manuscript in primary_docs + aux_docs:
        meta = metadata[manuscript.doc_id]
        payload["documents"].append(
            {
                "doc_id": manuscript.doc_id,
                "title": manuscript.title,
                "primary": manuscript.primary,
                "cluster": manuscript.cluster,
                "elements": manuscript.elements,
                "modes": manuscript.modes,
                "motifs": manuscript.motifs,
                "stations": manuscript.stations,
                "source": manuscript.relative_path,
                "word_count": meta["word_count"],
                "top_keywords": meta["top_keywords"],
            }
        )
    return json.dumps(payload, indent=2)


def write_outputs(build_root: Path, metadata: dict[str, dict]) -> None:
    primary_docs = [item for item in CORPUS if item.primary]
    aux_docs = [item for item in CORPUS if not item.primary]

    write(build_root / "00_CONTROL" / "00_READ_ME_FIRST.md", build_readme(primary_docs, aux_docs))
    write(build_root / "00_CONTROL" / "01_CORPUS_CANON.md", build_corpus_canon(primary_docs, aux_docs, metadata))
    write(build_root / "00_CONTROL" / "02_EXECUTION_MODEL.md", build_execution_model())
    write(build_root / "00_CONTROL" / "03_ELEMENTAL_ASSIGNMENTS.md", build_elemental_assignments(primary_docs, aux_docs))

    for manuscript in CORPUS:
        meta = metadata[manuscript.doc_id]
        write(
            build_root / "01_SOURCE_EXTRACTS" / f"{manuscript.doc_id.lower()}_{manuscript.slug}.md",
            build_source_extract(manuscript, meta),
        )
        write(
            build_root / "02_INDIVIDUAL_SYNTHESIS" / f"{manuscript.doc_id.lower()}_{manuscript.slug}.md",
            build_individual_synthesis(manuscript, meta, primary_docs),
        )

    for a in primary_docs:
        for b in primary_docs:
            pair_name = f"{a.doc_id.lower()}__to__{b.doc_id.lower()}.md"
            pair_rel = md_link("../10_INDEXES/00_pairwise_matrix.md", "pairwise matrix")
            source_rel = md_link(
                f"../02_INDIVIDUAL_SYNTHESIS/{a.doc_id.lower()}_{a.slug}.md",
                f"{a.doc_id} source card",
            )
            write(
                build_root / "03_PAIRWISE_SYNERGIES" / pair_name,
                build_pair_doc(a, b, pair_rel, source_rel),
            )

    write(
        build_root / "05_SYMMETRIES" / "00_neutral_64_observations.md",
        build_64_observations(primary_docs, None),
    )

    for element in ELEMENTS:
        element_dir = build_root / "04_ELEMENTS" / element
        write(element_dir / "00_lens_overview.md", build_element_lens(element, primary_docs))
        write(element_dir / "01_64_observations.md", build_64_observations(primary_docs, element))

    for name, content in symmetry_docs(primary_docs).items():
        write(build_root / "05_SYMMETRIES" / name, content)

    for filename, content in build_metro_maps(primary_docs).items():
        write(build_root / "06_METRO_MAPS" / filename, content)

    for letter, element, mode in appendix_slots():
        write(
            build_root / "07_APPENDICES" / f"appendix_{letter.lower()}_{element}_{mode}.md",
            build_appendix_doc(letter, element, mode, primary_docs),
        )
    write(build_root / "07_APPENDICES" / "appendix_q_integrated_appendix_metro_map.md", build_appendix_q())

    write(build_root / "08_ZERO_POINT" / "00_zero_point_synthesis.md", build_zero_point(primary_docs))

    for manuscript in aux_docs:
        write(
            build_root / "09_AUXILIARY_LENSES" / f"{manuscript.doc_id.lower()}_{manuscript.slug}.md",
            build_auxiliary_doc(manuscript, metadata[manuscript.doc_id], primary_docs),
        )

    write(build_root / "10_INDEXES" / "00_pairwise_matrix.md", build_pairwise_matrix(primary_docs))
    write(build_root / "10_INDEXES" / "01_corpus_index.json", build_index_json(primary_docs, aux_docs, metadata))

    write(
        build_root / "00_CONTROL" / "04_deep_synthesis.md",
        textwrap.dedent(
            """
            # Deep Synthesis

            The corpus behaves like one machine with several projection layers.
            Geometry manuscripts decide what a valid object is.
            Transport manuscripts decide how an object may move without semantic loss.
            Numeric manuscripts compress invariant seeds into reusable kernels.
            Time manuscripts expose how recurrence, resonance, and phase weather make the whole system legible.

            The strongest convergence is this:

            - shape grammar provides the object
            - tunnel and rotation logic provide the transform
            - proof-carrying transport provides custody of meaning
            - constants and kernels provide stable seeds
            - time-phase manuscripts provide recurring observation interfaces

            In other words, the entire corpus keeps rediscovering the same deeper statement:

            `reality = lawful object motion observed through recursive phase interfaces`

            The four elements are not decorative.
            They are a control surface for reading the same corpus from four non-identical but composable angles:

            - Fire makes the corpus executable.
            - Water makes the corpus recursive.
            - Earth makes the corpus certifiable.
            - Air makes the corpus navigable.

            The pair lattice and appendices then turn that statement into a machine-readable atlas rather than a single summary paragraph.
            """
        ).strip(),
    )
    write(
        build_root / "07_APPENDICES" / "00_appendix_skeleton_outline.md",
        textwrap.dedent(
            """
            # Appendix Skeleton Outline

            Appendices `A-P` are the sixteen crystal slots of the 4x4 grid:

            - A-D: Fire x Kernel/Dynamics/Verification/Navigation
            - E-H: Water x Kernel/Dynamics/Verification/Navigation
            - I-L: Earth x Kernel/Dynamics/Verification/Navigation
            - M-P: Air x Kernel/Dynamics/Verification/Navigation

            Appendix `Q` is the appendix-only metro map that stitches the 16 slots into one navigable lattice.
            """
        ).strip(),
    )


def main() -> int:
    args = parse_args()
    workspace_root = Path(args.workspace_root).resolve()
    build_root = workspace_root / args.output_dir
    metadata = build_corpus_metadata(workspace_root)
    write_outputs(build_root, metadata)
    print(f"Built manuscript elemental net at {build_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
