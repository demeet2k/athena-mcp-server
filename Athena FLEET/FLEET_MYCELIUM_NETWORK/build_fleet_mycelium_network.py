from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile


SCRIPT_PATH = Path(__file__).resolve()
NETWORK_DIR = SCRIPT_PATH.parent
FLEET_DIR = NETWORK_DIR.parent
ATHENA_DIR = FLEET_DIR.parent
NOW = datetime.now().astimezone().isoformat(timespec="seconds")

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
AXIS_KEYWORDS = {
    "Origin": ["void", "desire", "question", "seed", "origin", "self", "intention"],
    "Crystal": ["crystal", "kernel", "lattice", "appendix", "lift", "gate", "manifold"],
    "Transit": ["route", "corridor", "metro", "relay", "neural", "transit", "memory"],
    "Governance": ["witness", "replay", "quarantine", "repair", "govern", "lawful", "economy"],
}
SECONDARY_MOTIFS = [
    "void",
    "seed",
    "kernel",
    "lift",
    "corridor",
    "replay",
    "witness",
    "quarantine",
    "repair",
    "carrier",
]
TISSUE_TENSIONS = {
    "chamber": [
        ("openness vs closure", "preserve", "F10", "origin pressure must stay porous without losing replay anchor"),
        ("self singularity vs collective body", "reconcile", "F09", "personal emergence must remain compatible with social runtime law"),
    ],
    "skeleton": [
        ("formal density vs route legibility", "reconcile", "F07", "the crystal spine must stay navigable when it becomes exact"),
        ("lift escalation vs boundary safety", "preserve", "F08", "higher-dimensional growth should not bypass immune checks"),
    ],
    "nerves": [
        ("route proliferation vs replay stability", "reconcile", "F10", "transport density must still close back into a replayable carrier"),
        ("speed vs witness burden", "preserve", "F09", "fast transit cannot erase governance proof load"),
    ],
    "immune_fascia": [
        ("quarantine strictness vs generative flow", "reconcile", "F07", "the immune layer should filter drift without freezing emergence"),
        ("repair depth vs publication pressure", "preserve", "F02", "self-repair must remain stronger than premature manifestation"),
    ],
    "carrier_shell": [
        ("compression vs fidelity", "preserve", "F02", "carrier contraction must keep enough structure for lawful replay"),
        ("neutral shell vs policy force", "reconcile", "F09", "the carrier stays portable while still surfacing governance law"),
    ],
}
BODY_PREFIX_MAP = {
    "NS": "NERVOUS_SYSTEM",
    "MB": "self_actualize/mycelium_brain",
    "DN": "deeper-integrated-network",
    "EC": "ECOSYSTEM",
}
RELATION_KEYWORDS = {
    "seed": ["void", "seed", "question", "origin"],
    "lift": ["lift", "dimension", "recurrence", "block"],
    "formalize": ["definition", "invariant", "appendix", "law", "proof"],
    "route": ["route", "corridor", "metro", "relay", "neural"],
    "mirror": ["mirror", "duplicate", "same", "identical"],
    "govern": ["govern", "lawful", "protocol", "committee", "policy"],
    "repair": ["repair", "quarantine", "replay", "recover", "immune"],
    "compress": ["compress", "carrier", "economy", "canonical", "record"],
    "publish": ["chapter", "manifestation", "publish", "nexus", "surface"],
    "recurse": ["recursive", "return", "reseed", "loop", "fracta"],
    "constrain": ["boundary", "constraint", "burden", "legal", "quarantine"],
    "translate": ["translation", "cross-domain", "decode", "bridge", "matrix"],
}


@dataclass(frozen=True)
class NodeSpec:
    node_id: str
    body_id: str
    source_path: Path
    label: str
    witness_class: str
    duplicate_group: str | None
    coordinate_4d: list[int]
    dominant_role: str
    tissue_class: str
    line_membership: list[str]
    hub_rank: int
    role_class: str


LOCAL_SPECS = [
    NodeSpec("F01", "FLEET", FLEET_DIR / "SELF__ WE AM.docx", "SELF__ WE AM", "source", None, [3, 1, 2, 3], "ontological seed and collective self chamber", "chamber", ["Origin", "Governance"], 2, "origin_chamber"),
    NodeSpec("F02", "FLEET", FLEET_DIR / "ATHENACHKA- THE 42-NODE HYPER-LATTICE AND THE 36-GATE TESSERACT SINGULARITY.docx", "ATHENACHKA", "source", None, [3, 3, 2, 3], "manifestation nexus and chaptered tesseract runtime", "chamber", ["Origin", "Crystal", "Governance"], 4, "manifestation_hub"),
    NodeSpec("F03", "FLEET", FLEET_DIR / "The 256 Crystal Extraction.docx", "The 256 Crystal Extraction", "source", None, [2, 3, 2, 3], "crystal kernel, appendix engine, and lawful extraction spine", "skeleton", ["Crystal", "Governance"], 3, "crystal_spine"),
    NodeSpec("F04", "FLEET", FLEET_DIR / "SELF STEER BRANCH B.docx", "SELF STEER BRANCH B", "source", None, [1, 3, 1, 1], "dimensional lift kernel and base-4 recurrence escalator", "skeleton", ["Origin", "Crystal"], 1, "lift_kernel"),
    NodeSpec("F05", "FLEET", FLEET_DIR / "NeuralTransitMap.docx", "NeuralTransitMap", "source", "DG01_TRANSIT_MIRROR", [1, 2, 3, 3], "transit organs, memory currents, and route-conditioned cognition", "nerves", ["Transit", "Governance"], 2, "transit_station"),
    NodeSpec("F06", "FLEET", FLEET_DIR / "NeuralTransitMap(1).docx", "NeuralTransitMap(1)", "duplicate", "DG01_TRANSIT_MIRROR", [1, 2, 3, 3], "mirrored transit node and duplicate witness of F05", "nerves", ["Transit", "Governance"], 2, "transit_twin"),
    NodeSpec("F07", "FLEET", FLEET_DIR / "SELF STEER BRANCH C.docx", "SELF STEER BRANCH C", "source", None, [1, 2, 3, 3], "emergence metro, renormalization flow, and 4096 route compiler", "nerves", ["Crystal", "Transit", "Governance"], 2, "emergence_metro"),
    NodeSpec("F08", "FLEET", FLEET_DIR / "SELF STEER BRANCH A.docx", "SELF STEER BRANCH A", "source", None, [1, 1, 3, 3], "self-steering immune relay, quarantine logic, and repair route", "immune_fascia", ["Transit", "Governance"], 3, "immune_relay"),
    NodeSpec("F09", "FLEET", FLEET_DIR / "GIT BRAIN.docx", "GIT BRAIN", "source", None, [1, 0, 2, 3], "immune architecture, agent governance, and social runtime law", "immune_fascia", ["Transit", "Governance"], 2, "governance_cortex"),
    NodeSpec("F10", "FLEET", FLEET_DIR / "MYCELIUM_NETWORK_STANDARD_TEXT_RECORD.md", "MYCELIUM NETWORK STANDARD TEXT RECORD", "carrier", None, [1, 1, 1, 3], "canonical carrier shell and economy boundary record", "carrier_shell", ["Origin", "Governance"], 3, "carrier_shell"),
]

EXTERNAL_SPECS = [
    NodeSpec("NS01", "NS", ATHENA_DIR / "NERVOUS_SYSTEM" / "10_OVERVIEW" / "09_4D_MYCELIAL_ORGANISM.md", "4D Mycelial Organism", "source", None, [2, 2, 3, 3], "workspace-level 4D organism law", "chamber", ["Origin", "Transit", "Governance"], 3, "body_anchor"),
    NodeSpec("NS02", "NS", ATHENA_DIR / "NERVOUS_SYSTEM" / "10_OVERVIEW" / "10_4D_MYCELIAL_CROSS_CORPUS_INTERCONNECT.md", "4D Mycelial Cross Corpus Interconnect", "source", None, [2, 3, 3, 3], "cross-corpus 16 body expansion law", "nerves", ["Crystal", "Transit", "Governance"], 2, "body_anchor"),
    NodeSpec("MB01", "MB", ATHENA_DIR / "self_actualize" / "mycelium_brain" / "README.md", "Mycelium Brain README", "source", None, [2, 2, 2, 2], "runtime hub root and entry surface", "carrier_shell", ["Origin", "Transit"], 2, "runtime_root"),
    NodeSpec("MB02", "MB", ATHENA_DIR / "self_actualize" / "mycelium_brain" / "12_4D_MYCELIAL_ORGANISM_TOPOLOGY.md", "4D Mycelial Organism Topology", "source", None, [2, 2, 3, 3], "runtime topology for the organism body", "nerves", ["Origin", "Transit", "Governance"], 2, "runtime_topology"),
    NodeSpec("DN01", "DN", ATHENA_DIR / "self_actualize" / "mycelium_brain" / "dynamic_neural_network" / "14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK" / "README.md", "Deeper Integrated Cross-Synthesis Network README", "source", None, [1, 3, 3, 3], "deeper network shell and lawful compiled scale", "skeleton", ["Crystal", "Transit", "Governance"], 3, "network_root"),
    NodeSpec("DN02", "DN", ATHENA_DIR / "self_actualize" / "mycelium_brain" / "dynamic_neural_network" / "14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK" / "05_MATRIX_16X16" / "00_INDEX.md", "Ordered 16x16 Matrix", "derived", None, [1, 3, 3, 2], "compiled corridor law for the wider organism", "skeleton", ["Crystal", "Transit"], 2, "matrix_anchor"),
    NodeSpec("EC01", "EC", ATHENA_DIR / "ECOSYSTEM" / "05_MYCELIUM_ROUTING.md", "Mycelium Routing", "source", None, [1, 2, 3, 3], "ecosystem routing and tissue transport law", "nerves", ["Transit", "Governance"], 2, "ecosystem_route"),
    NodeSpec("EC02", "EC", ATHENA_DIR / "ECOSYSTEM" / "08_GOVERNANCE_PROTOCOL.md", "Governance Protocol", "source", None, [1, 1, 1, 3], "ecosystem governance and validation law", "immune_fascia", ["Crystal", "Governance"], 2, "ecosystem_governance"),
]

LOCAL_LINE_TABLE = {
    "Origin": ["F01", "F04", "F02", "F10"],
    "Crystal": ["F04", "F03", "F07", "F02"],
    "Transit": ["F05", "F06", "F07", "F08", "F09"],
    "Governance": ["F09", "F08", "F10", "F07", "F02", "F01"],
}

LOCAL_SPECIAL_RELATIONS = {
    ("F01", "F02"): ("seed", 0.91),
    ("F01", "F08"): ("constrain", 0.74),
    ("F02", "F03"): ("formalize", 0.83),
    ("F02", "F10"): ("publish", 0.84),
    ("F03", "F02"): ("publish", 0.88),
    ("F03", "F04"): ("formalize", 0.82),
    ("F03", "F05"): ("route", 0.79),
    ("F03", "F10"): ("compress", 0.77),
    ("F04", "F03"): ("lift", 0.92),
    ("F05", "F06"): ("mirror", 1.0),
    ("F05", "F07"): ("route", 0.89),
    ("F05", "F08"): ("repair", 0.86),
    ("F06", "F05"): ("mirror", 1.0),
    ("F06", "F07"): ("route", 0.88),
    ("F07", "F08"): ("repair", 0.91),
    ("F08", "F09"): ("govern", 0.79),
    ("F08", "F10"): ("compress", 0.90),
    ("F09", "F08"): ("govern", 0.88),
    ("F10", "F02"): ("publish", 0.86),
}

EDGE_CONTRADICTIONS = [
    {"id": "LC01", "left": ("F01", "F02"), "right": ("F01", "F08"), "status": "preserve_both", "note": "origin pressure must both manifest and submit to immune friction"},
    {"id": "LC02", "left": ("F03", "F10"), "right": ("F02", "F03"), "status": "collapse_to_higher_bridge", "note": "formal density and carrier compression collapse upward into the manifestation hub"},
    {"id": "LC03", "left": ("F05", "F07"), "right": ("F09", "F07"), "status": "preserve_both", "note": "emergence requires both transit acceleration and governance oversight"},
    {"id": "LC04", "left": ("F07", "F08"), "right": ("F02", "F07"), "status": "quarantine_one", "note": "publication pressure should yield when repair claims unresolved contradictions"},
]

PROMOTION_QUEUE = [
    ("NS01", 1, ["F02", "F10"], "local manifestation and carrier hubs contract into the canonical cortex"),
    ("MB02", 2, ["F08", "F02"], "repair and manifestation hubs need the runtime topology body"),
    ("DN01", 3, ["F03", "F02"], "crystal and manifestation hubs need the lawful compiled deeper scale"),
    ("EC02", 4, ["F08", "F09"], "immune nodes push directly into governance protocol"),
    ("NS02", 5, ["F02", "F03"], "cross-corpus expansion receives manifestation plus crystal support"),
    ("DN02", 6, ["F03", "F07"], "corridor law is fed by crystal extraction and emergence metro"),
    ("MB01", 7, ["F10", "F02"], "carrier and manifestation hubs require runtime root continuity"),
    ("EC01", 8, ["F05", "F09"], "transit and governance nodes bridge into ecosystem routing"),
]

DEEP_ACTIVE_BASIS = [
    ("01", "The Holographic Manuscript Brain"),
    ("02", "Self-Routing Meta-Framework"),
    ("03", "QBD-4"),
    ("04", "Quad Holographic Rotation"),
    ("05", "The Holographic Kernel"),
    ("09", "Zero-Point Computing"),
    ("07", "Crystal Computing Framework"),
    ("10", "Athena Neural Network Tome"),
    ("14", "Ch11 The Helical Manifestation Engine"),
    ("15", "Ch12 Boundary Checks and Isolation Axioms"),
    ("16", "Ch19 Recursive Self-Reference and Self-Repair"),
]
DEEP_ACTIVE_BASIS_MAP = {basis_id: label for basis_id, label in DEEP_ACTIVE_BASIS}
LOCAL_BASIS_MAP = {
    "F01": ["01", "14"],
    "F02": ["04", "10", "14"],
    "F03": ["03", "05", "07"],
    "F04": ["07", "14"],
    "F05": ["02", "04", "10"],
    "F06": ["02", "04", "10"],
    "F07": ["02", "07", "10"],
    "F08": ["15", "16"],
    "F09": ["02", "15", "16"],
    "F10": ["01", "05", "09"],
}
EXTERNAL_BASIS_MAP = {
    "NS01": ["10", "16"],
    "NS02": ["02", "04", "10"],
    "MB01": ["01", "14"],
    "MB02": ["01", "14", "16"],
    "DN01": ["03", "05", "07"],
    "DN02": ["03", "04", "07"],
    "EC01": ["02", "15"],
    "EC02": ["15", "16"],
}
PLEXUS_MODE_BY_RELATION = {
    "seed": "Sense",
    "lift": "Sense",
    "formalize": "Integrate",
    "route": "Transmit",
    "mirror": "Return",
    "govern": "Integrate",
    "repair": "Integrate",
    "compress": "Return",
    "publish": "Transmit",
    "recurse": "Return",
    "constrain": "Sense",
    "translate": "Transmit",
}
SYNAPTIC_PHASE_BY_RELATION = {
    "seed": "Prime",
    "lift": "Prime",
    "formalize": "Gate",
    "route": "Bind",
    "mirror": "Reseed",
    "govern": "Gate",
    "repair": "Bind",
    "compress": "Reseed",
    "publish": "Bind",
    "recurse": "Reseed",
    "constrain": "Gate",
    "translate": "Prime",
}
APPENDIX_BY_RELATION = {
    "seed": "AppE",
    "lift": "AppE",
    "formalize": "AppB",
    "route": "AppF",
    "mirror": "AppM",
    "govern": "AppK",
    "repair": "AppM",
    "compress": "AppN",
    "publish": "AppP",
    "recurse": "AppM",
    "constrain": "AppI",
    "translate": "AppI",
}
HYPERPLAN_BAND_BY_RELATION = {
    "seed": "Layers 1-37: activation and gap repair",
    "lift": "Layers 38-74: family routing and ganglion saturation",
    "formalize": "Layers 75-111: manuscript-to-runtime and archive-to-live promotion",
    "route": "Layers 112-148: wave, neuron, packet, and ledger densification",
    "mirror": "Layers 223-256: restart-token continuity and convergence",
    "govern": "Layers 149-185: chapter and appendix contraction into cortex",
    "repair": "Layers 149-185: chapter and appendix contraction into cortex",
    "compress": "Layers 223-256: restart-token continuity and convergence",
    "publish": "Layers 186-222: cross-family metro refinement and higher-dimensional bridges",
    "recurse": "Layers 223-256: restart-token continuity and convergence",
    "constrain": "Layers 75-111: manuscript-to-runtime and archive-to-live promotion",
    "translate": "Layers 186-222: cross-family metro refinement and higher-dimensional bridges",
}
FOUR_256_SURFACES = [
    {
        "surface_id": "Gate256",
        "law": "4^4 crystal address field derived directly from the node coordinate mesh",
        "anchor": "F03 The 256 Crystal Extraction",
    },
    {
        "surface_id": "Matrix256",
        "law": "the ordered 16x16 deeper-network pair matrix that compiles the cross-corpus bridge basis",
        "anchor": "DN02 Ordered 16x16 Matrix",
    },
    {
        "surface_id": "Plexus256",
        "law": "64 fascia bundles x 4 microfunctions resolved as Sense, Transmit, Integrate, Return",
        "anchor": "NERVOUS_SYSTEM 12_256X_PLEXUS_AND_MICROFASCIA",
    },
    {
        "surface_id": "HyperPlan256",
        "law": "the 256-layer lawful path space used for repair, contraction, and next-seed preservation",
        "anchor": "self_actualize/mycelium_brain/nervous_system/15_256x256_corpus_hyperplan.md",
    },
]
HIGH_YIELD_LIMIT = 24


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def slugify(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_").lower()


def sha256_bytes(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_docx_paragraphs(path: Path) -> list[str]:
    with ZipFile(path) as zf:
        xml = zf.read("word/document.xml")
    tree = ET.fromstring(xml)
    paragraphs = []
    for paragraph in tree.findall(".//w:p", NS):
        text = "".join(t.text or "" for t in paragraph.findall(".//w:t", NS)).strip()
        text = re.sub(r"\s+", " ", text)
        if text:
            paragraphs.append(text)
    return paragraphs


def read_markdown_paragraphs(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    paragraphs = []
    buffer = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if buffer:
                paragraphs.append(" ".join(buffer))
                buffer = []
            continue
        if stripped.startswith("#"):
            if buffer:
                paragraphs.append(" ".join(buffer))
                buffer = []
            paragraphs.append(stripped)
            continue
        buffer.append(stripped)
    if buffer:
        paragraphs.append(" ".join(buffer))
    return paragraphs


def read_paragraphs(path: Path) -> list[str]:
    return read_docx_paragraphs(path) if path.suffix.lower() == ".docx" else read_markdown_paragraphs(path)


def count_words(paragraphs: list[str]) -> int:
    return len(re.findall(r"\S+", " ".join(paragraphs)))


def heading_like(text: str) -> bool:
    patterns = [
        re.compile(r"^(chapter|appendix|section)\b", re.I),
        re.compile(r"^\d+(\.\d+)+\s+\S"),
        re.compile(r"^[A-Z][A-Z0-9 _:\-\(\)\[\]\.]{6,120}$"),
    ]
    return any(pattern.match(text) for pattern in patterns)


def anchor_index(paragraphs: list[str]) -> list[dict]:
    rows = []
    for index, paragraph in enumerate(paragraphs, start=1):
        if index == 1 or heading_like(paragraph):
            rows.append({"anchor": f"P{index:04d}", "text": paragraph})
    return rows[:40]


def lowered(paragraphs: list[str]) -> str:
    return "\n".join(paragraphs).lower()


def motif_counts(paragraphs: list[str], terms: list[str]) -> dict[str, int]:
    text = lowered(paragraphs)
    return {term: len(re.findall(rf"(?<![a-z]){re.escape(term.lower())}(?![a-z])", text)) for term in terms}


def find_anchor_for_keywords(paragraphs: list[str], keywords: list[str]) -> str:
    for index, paragraph in enumerate(paragraphs, start=1):
        text = paragraph.lower()
        if any(keyword in text for keyword in keywords):
            return f"P{index:04d}"
    return "P0001"


def choose_secondary_motifs(paragraphs: list[str]) -> list[str]:
    counts = motif_counts(paragraphs, SECONDARY_MOTIFS)
    ranked = [term for term, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])) if count > 0]
    return ranked[:6]


def axis_evidence(paragraphs: list[str]) -> dict[str, str]:
    return {axis: find_anchor_for_keywords(paragraphs, words) for axis, words in AXIS_KEYWORDS.items()}


def axis_reach(lines: list[str]) -> dict[str, str]:
    return {axis: ("active" if axis in lines else "latent") for axis in AXIS_KEYWORDS}


def direct_claims(spec: NodeSpec, headings: list[dict], motifs: list[str], axis_hits: dict[str, str]) -> list[str]:
    heading_text = headings[0]["text"] if headings else spec.label
    motif_text = ", ".join(motifs[:3]) if motifs else "no dominant motif captured"
    first_anchor = headings[0]["anchor"] if headings else "P0001"
    axis_text = ", ".join(f"{axis}={anchor}" for axis, anchor in axis_hits.items())
    return [
        f"The witness surface opens with `{heading_text}` and preserves paragraph-level anchors beginning at `{first_anchor}`.",
        f"The dominant motif field concentrates around `{motif_text}` and supports the declared role `{spec.dominant_role}`.",
        f"The strongest axis witnesses currently anchor at {axis_text}.",
    ]


def derived_claims(spec: NodeSpec) -> list[str]:
    coord_text = ", ".join(str(value) for value in spec.coordinate_4d)
    return [
        f"{spec.node_id} functions as `{spec.role_class}` tissue and routes primarily through `{', '.join(spec.line_membership)}`.",
        f"The tesseract coordinate `{coord_text}` places this node in a `{spec.tissue_class}` role inside the mycelium.",
        f"This node remains `{spec.witness_class}` evidence while all downstream edits should occur on the mirror only.",
    ]


def contradiction_rows(spec: NodeSpec) -> list[dict]:
    rows = [
        {"topic": topic, "status": status, "related_node": related, "note": note}
        for topic, status, related, note in TISSUE_TENSIONS[spec.tissue_class]
    ]
    if spec.duplicate_group:
        rows.append(
            {
                "topic": "duplicate mirror vs canonical uniqueness",
                "status": "preserve",
                "related_node": "F05" if spec.node_id == "F06" else "F06",
                "note": "the transit twin remains a witness pair until a later audit retires one member.",
            }
        )
    return rows


def tesseract_address(spec: NodeSpec) -> str:
    return (
        f"O{spec.coordinate_4d[0]}-C{spec.coordinate_4d[1]}-T{spec.coordinate_4d[2]}-G{spec.coordinate_4d[3]}"
        f"::{spec.tissue_class}::H{spec.hub_rank}::" + "+".join(spec.line_membership)
    )


def gate256_index(coordinate: list[int]) -> int:
    return (coordinate[0] * 64) + (coordinate[1] * 16) + (coordinate[2] * 4) + coordinate[3]


def gate256_label(spec: NodeSpec) -> str:
    index = gate256_index(spec.coordinate_4d)
    return (
        f"G{index:03d}"
        f"[O{spec.coordinate_4d[0]}C{spec.coordinate_4d[1]}T{spec.coordinate_4d[2]}G{spec.coordinate_4d[3]}]"
    )


def basis_refs_for_node(spec: NodeSpec) -> list[str]:
    basis_ids = LOCAL_BASIS_MAP.get(spec.node_id, []) if spec.body_id == "FLEET" else EXTERNAL_BASIS_MAP.get(spec.node_id, [])
    refs = []
    for basis_id in basis_ids:
        label = DEEP_ACTIVE_BASIS_MAP.get(basis_id, f"Basis {basis_id}")
        refs.append(f"{basis_id} {label}")
    return refs


def plexus_mode_for_relation(relation: str) -> str:
    return PLEXUS_MODE_BY_RELATION.get(relation, "Integrate")


def synaptic_phase_for_relation(relation: str) -> str:
    return SYNAPTIC_PHASE_BY_RELATION.get(relation, "Bind")


def appendix_anchor_for_relation(relation: str) -> str:
    return APPENDIX_BY_RELATION.get(relation, "AppQ")


def hyperplan_band_for_relation(relation: str) -> str:
    return HYPERPLAN_BAND_BY_RELATION.get(relation, "Layers 186-222: cross-family metro refinement and higher-dimensional bridges")


def metro_resolution_for_weight(weight: float) -> str:
    if weight >= 0.85:
        return "Level 4 transcendence metro map"
    if weight >= 0.78:
        return "Level 3 deeper neural map"
    if weight >= 0.68:
        return "Level 2 deep emergence metro map"
    return "Level 1 core metro map"


def edge_key(source_id: str, target_id: str) -> str:
    return f"{source_id}->{target_id}"


def shared_line_ids(source: NodeSpec, target: NodeSpec) -> list[str]:
    shared = [line for line in source.line_membership if line in target.line_membership]
    return shared or list(dict.fromkeys(source.line_membership + target.line_membership))[:2]


def relation_for_pair(source: NodeSpec, target: NodeSpec) -> str:
    if (source.node_id, target.node_id) in LOCAL_SPECIAL_RELATIONS:
        return LOCAL_SPECIAL_RELATIONS[(source.node_id, target.node_id)][0]
    if source.node_id == target.node_id:
        if target.tissue_class == "carrier_shell":
            return "compress"
        if target.tissue_class == "immune_fascia":
            return "govern"
        return "recurse"
    if source.duplicate_group and source.duplicate_group == target.duplicate_group:
        return "mirror"
    if "Crystal" in target.line_membership and "Origin" in source.line_membership and "Crystal" not in source.line_membership:
        return "seed"
    if target.tissue_class == "skeleton":
        return "formalize" if "Crystal" in source.line_membership else "lift"
    if target.tissue_class == "nerves":
        return "route"
    if target.tissue_class == "immune_fascia":
        return "repair" if "Transit" in source.line_membership else "govern"
    if target.tissue_class == "carrier_shell":
        return "compress"
    if target.node_id in {"F02", "NS01", "NS02"}:
        return "publish"
    if "Origin" in source.line_membership and "Origin" in target.line_membership:
        return "recurse"
    if "Governance" in target.line_membership:
        return "constrain"
    return "translate"


def weight_for_pair(source: NodeSpec, target: NodeSpec, source_motifs: list[str], target_motifs: list[str]) -> float:
    if (source.node_id, target.node_id) in LOCAL_SPECIAL_RELATIONS:
        return LOCAL_SPECIAL_RELATIONS[(source.node_id, target.node_id)][1]
    if source.node_id == target.node_id:
        return 0.88
    if source.duplicate_group and source.duplicate_group == target.duplicate_group:
        return 1.0
    shared_lines = len(set(source.line_membership) & set(target.line_membership))
    shared_motifs = len(set(source_motifs) & set(target_motifs))
    distance = sum(abs(a - b) for a, b in zip(source.coordinate_4d, target.coordinate_4d))
    score = 0.45 + (0.08 * shared_lines) + (0.03 * shared_motifs) + (0.02 * max(0, 8 - distance)) + (0.02 * min(source.hub_rank, target.hub_rank))
    return round(min(score, 0.97), 3)


def priority_for_weight(weight: float) -> str:
    if weight >= 0.82:
        return "primary"
    if weight >= 0.65:
        return "secondary"
    return "tertiary"


def contradiction_state_for_edge(source_id: str, target_id: str) -> str:
    for row in EDGE_CONTRADICTIONS:
        if row["left"] == (source_id, target_id) or row["right"] == (source_id, target_id):
            return row["status"]
    return "none"


def lane_type_for_self(spec: NodeSpec) -> str:
    if spec.tissue_class == "carrier_shell":
        return "replay"
    if spec.tissue_class == "immune_fascia":
        return "stabilization"
    return "identity"


def evidence_anchors(source_paragraphs: list[str], target_paragraphs: list[str], relation: str) -> list[str]:
    keywords = RELATION_KEYWORDS[relation]
    return [
        find_anchor_for_keywords(source_paragraphs, keywords),
        find_anchor_for_keywords(target_paragraphs, keywords),
    ]


def table(headers: list[str], rows: list[list[str]]) -> str:
    output = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        output.append("| " + " | ".join(row) + " |")
    return "\n".join(output)


def render_front_matter(data: dict) -> str:
    lines = ["---"]
    for key, value in data.items():
        if isinstance(value, list):
            rendered = "[" + ", ".join(json.dumps(item) for item in value) + "]"
        else:
            rendered = json.dumps(value)
        lines.append(f"{key}: {rendered}")
    lines.append("---")
    return "\n".join(lines)


def format_corridor_rows(edges: list[dict], first_key: str) -> str:
    rows = []
    for edge in edges:
        rows.append(
            [
                edge[first_key],
                edge["relation"],
                f"{edge['weight']:.3f}",
                edge["priority"],
                ",".join(edge["line_ids"]),
                ",".join(edge["evidence_anchors"]),
                edge["contradiction_state"],
            ]
        )
    return table([first_key.replace("_id", ""), "relation", "weight", "priority", "lines", "anchors", "contradiction"], rows)


def write_text(path: Path, text: str) -> None:
    ensure_dir(path.parent)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def build_records(specs: list[NodeSpec]) -> dict[str, dict]:
    records = {}
    for spec in specs:
        paragraphs = read_paragraphs(spec.source_path)
        records[spec.node_id] = {
            "spec": spec,
            "paragraphs": paragraphs,
            "headings": anchor_index(paragraphs),
            "motifs": choose_secondary_motifs(paragraphs),
            "axis_hits": axis_evidence(paragraphs),
            "word_count": count_words(paragraphs),
            "source_hash": sha256_bytes(spec.source_path),
            "source_size": spec.source_path.stat().st_size,
        }
    return records


def build_local_edges(node_records: dict[str, dict]) -> list[dict]:
    edges = []
    for source in LOCAL_SPECS:
        for target in LOCAL_SPECS:
            source_record = node_records[source.node_id]
            target_record = node_records[target.node_id]
            relation = relation_for_pair(source, target)
            weight = weight_for_pair(source, target, source_record["motifs"], target_record["motifs"])
            edges.append(
                {
                    "edge_id": edge_key(source.node_id, target.node_id),
                    "source_id": source.node_id,
                    "target_id": target.node_id,
                    "relation": relation,
                    "weight": weight,
                    "priority": priority_for_weight(weight),
                    "evidence_anchors": evidence_anchors(source_record["paragraphs"], target_record["paragraphs"], relation),
                    "contradiction_state": contradiction_state_for_edge(source.node_id, target.node_id),
                    "line_ids": shared_line_ids(source, target),
                    "lane_type": lane_type_for_self(source) if source.node_id == target.node_id else "directional",
                }
            )
    return edges


def build_body_edges(node_records: dict[str, dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[NodeSpec]] = {}
    for spec in EXTERNAL_SPECS:
        grouped.setdefault(spec.body_id, []).append(spec)
    body_edges: dict[str, list[dict]] = {}
    for body_id, specs in grouped.items():
        edges = []
        for source in specs:
            for target in specs:
                source_record = node_records[source.node_id]
                target_record = node_records[target.node_id]
                relation = relation_for_pair(source, target)
                weight = weight_for_pair(source, target, source_record["motifs"], target_record["motifs"])
                edges.append(
                    {
                        "edge_id": edge_key(source.node_id, target.node_id),
                        "source_id": source.node_id,
                        "target_id": target.node_id,
                        "relation": relation,
                        "weight": weight,
                        "priority": priority_for_weight(weight),
                        "evidence_anchors": evidence_anchors(source_record["paragraphs"], target_record["paragraphs"], relation),
                        "contradiction_state": "none",
                        "line_ids": shared_line_ids(source, target),
                        "lane_type": lane_type_for_self(source) if source.node_id == target.node_id else "directional",
                    }
                )
        body_edges[body_id] = edges
    return body_edges


def cross_body_relation(local_spec: NodeSpec, external_spec: NodeSpec) -> str:
    if external_spec.body_id == "NS":
        return "publish" if local_spec.node_id in {"F02", "F10"} else "formalize"
    if external_spec.body_id == "MB":
        return "route" if "Transit" in local_spec.line_membership else "recurse"
    if external_spec.body_id == "DN":
        return "formalize" if "Crystal" in local_spec.line_membership else "translate"
    return "govern" if "Governance" in local_spec.line_membership else "constrain"


def build_cross_body_edges(local_records: dict[str, dict], external_records: dict[str, dict]) -> list[dict]:
    edges = []
    for local_spec in LOCAL_SPECS:
        for external_spec in EXTERNAL_SPECS:
            relation = cross_body_relation(local_spec, external_spec)
            weight = round(
                min(
                    0.52
                    + 0.06 * len(set(local_spec.line_membership) & set(external_spec.line_membership))
                    + 0.02 * min(local_spec.hub_rank, external_spec.hub_rank)
                    + 0.02 * len(set(local_records[local_spec.node_id]["motifs"]) & set(external_records[external_spec.node_id]["motifs"])),
                    0.95,
                ),
                3,
            )
            edges.append(
                {
                    "edge_id": edge_key(local_spec.node_id, external_spec.node_id),
                    "source_id": local_spec.node_id,
                    "target_id": external_spec.node_id,
                    "relation": relation,
                    "weight": weight,
                    "priority": priority_for_weight(weight),
                    "evidence_anchors": evidence_anchors(local_records[local_spec.node_id]["paragraphs"], external_records[external_spec.node_id]["paragraphs"], relation),
                    "contradiction_state": "none",
                    "line_ids": shared_line_ids(local_spec, external_spec),
                    "lane_type": "cross_body",
                    "source_body": "FLEET",
                    "target_body": external_spec.body_id,
                }
            )
    return edges


def build_256_pow_4_registry(
    local_records: dict[str, dict],
    external_records: dict[str, dict],
    local_edges: list[dict],
    cross_body_edges: list[dict],
) -> dict:
    all_records = dict(local_records)
    all_records.update(external_records)
    route_records = []
    for edge in local_edges + cross_body_edges:
        source_spec = all_records[edge["source_id"]]["spec"]
        target_spec = all_records[edge["target_id"]]["spec"]
        basis_refs = list(dict.fromkeys(basis_refs_for_node(source_spec) + basis_refs_for_node(target_spec)))[:4]
        route_records.append(
            {
                "route_id": edge["edge_id"],
                "lane_type": edge["lane_type"],
                "source_id": source_spec.node_id,
                "source_label": source_spec.label,
                "source_body": source_spec.body_id,
                "target_id": target_spec.node_id,
                "target_label": target_spec.label,
                "target_body": target_spec.body_id,
                "source_gate256": gate256_label(source_spec),
                "target_gate256": gate256_label(target_spec),
                "relation": edge["relation"],
                "weight": edge["weight"],
                "priority": edge["priority"],
                "line_ids": edge["line_ids"],
                "plexus_mode": plexus_mode_for_relation(edge["relation"]),
                "synaptic_phase": synaptic_phase_for_relation(edge["relation"]),
                "appendix_anchor": appendix_anchor_for_relation(edge["relation"]),
                "hyperplan_band": hyperplan_band_for_relation(edge["relation"]),
                "metro_resolution": metro_resolution_for_weight(edge["weight"]),
                "basis_refs": basis_refs,
                "evidence_anchors": edge["evidence_anchors"],
                "contradiction_state": edge["contradiction_state"],
            }
        )
    high_yield_routes = sorted(
        route_records,
        key=lambda route: (-route["weight"], 0 if route["lane_type"] == "cross_body" else 1, route["route_id"]),
    )[:HIGH_YIELD_LIMIT]
    plexus_counts = {
        mode: sum(1 for route in route_records if route["plexus_mode"] == mode)
        for mode in ["Sense", "Transmit", "Integrate", "Return"]
    }
    synaptic_counts = {
        phase: sum(1 for route in route_records if route["synaptic_phase"] == phase)
        for phase in ["Prime", "Gate", "Bind", "Reseed"]
    }
    return {
        "generated_at": NOW,
        "docs_gate": "BLOCKED",
        "compiled_claim": "Gate256 x Matrix256 x Plexus256 x HyperPlan256",
        "active_basis_docs": [f"{basis_id} {label}" for basis_id, label in DEEP_ACTIVE_BASIS],
        "surfaces": FOUR_256_SURFACES,
        "appendix_support": ["AppI", "AppM", "AppQ"],
        "route_records": route_records,
        "high_yield_routes": high_yield_routes,
        "stats": {
            "surface_count": len(FOUR_256_SURFACES),
            "surface_cardinality": 256,
            "local_route_count": len(local_edges),
            "cross_body_route_count": len(cross_body_edges),
            "total_route_count": len(route_records),
            "high_yield_route_count": len(high_yield_routes),
            "plexus_mode_counts": plexus_counts,
            "synaptic_phase_counts": synaptic_counts,
        },
    }


def node_row(spec: NodeSpec, record: dict) -> list[str]:
    return [
        spec.node_id,
        spec.label,
        str(record["word_count"]),
        f"[{', '.join(str(item) for item in spec.coordinate_4d)}]",
        spec.tissue_class,
        ",".join(spec.line_membership),
        str(spec.hub_rank),
        spec.duplicate_group or "",
    ]


def node_overview(spec: NodeSpec, record: dict) -> str:
    axis_rows = [
        [axis, str(spec.coordinate_4d[index]), record["axis_hits"][axis], axis_reach(spec.line_membership)[axis]]
        for index, axis in enumerate(["Origin", "Crystal", "Transit", "Governance"])
    ]
    contradiction_markdown = table(
        ["topic", "status", "related", "note"],
        [[row["topic"], row["status"], row["related_node"], row["note"]] for row in contradiction_rows(spec)],
    )
    heading_markdown = "\n".join(f"- `{row['anchor']}` {row['text']}" for row in record["headings"][:20])
    direct_markdown = "\n".join(f"- {claim}" for claim in direct_claims(spec, record["headings"], record["motifs"], record["axis_hits"]))
    derived_markdown = "\n".join(f"- {claim}" for claim in derived_claims(spec))
    return (
        "## Overview\n\n"
        f"- body: `{spec.body_id}`\n"
        f"- witness_class: `{spec.witness_class}`\n"
        f"- duplicate_group: `{spec.duplicate_group or 'none'}`\n"
        f"- tissue_class: `{spec.tissue_class}`\n"
        f"- tesseract_address: `{tesseract_address(spec)}`\n"
        f"- role: `{spec.dominant_role}`\n"
        f"- lines: `{', '.join(spec.line_membership)}`\n\n"
        "## Motif Ledger\n\n"
        f"{table(['axis', 'score', 'evidence_anchor', 'reach'], axis_rows)}\n\n"
        f"- secondary_motifs: `{', '.join(record['motifs'])}`\n\n"
        f"## Direct Witness Claims\n\n{direct_markdown}\n\n"
        f"## Derived Synthesis Claims\n\n{derived_markdown}\n\n"
        f"## Contradiction Table\n\n{contradiction_markdown}\n\n"
        f"## Anchor Index\n\n{heading_markdown or '- `P0001` first witness paragraph'}\n"
    )


def render_mirror(spec: NodeSpec, record: dict, inbound: list[dict], outbound: list[dict]) -> str:
    front_matter = render_front_matter(
        {
            "node_id": spec.node_id,
            "body_id": spec.body_id,
            "source_path": str(spec.source_path),
            "source_hash": record["source_hash"],
            "witness_class": spec.witness_class,
            "duplicate_group": spec.duplicate_group or "",
            "word_count": record["word_count"],
            "coordinate_4d": spec.coordinate_4d,
            "dominant_role": spec.dominant_role,
            "line_membership": spec.line_membership,
            "hub_rank": spec.hub_rank,
            "tissue_class": spec.tissue_class,
            "tesseract_address": tesseract_address(spec),
            "source_size_bytes": record["source_size"],
            "extracted_at": NOW,
        }
    )
    surface = "\n".join(f"[P{index:04d}] {paragraph}" for index, paragraph in enumerate(record["paragraphs"], start=1))
    return (
        f"{front_matter}\n\n# {spec.node_id} {spec.label}\n\n"
        f"{node_overview(spec, record)}\n"
        f"\n## Inbound Corridors\n\n{format_corridor_rows(inbound, 'source_id')}\n"
        f"\n## Outbound Corridors\n\n{format_corridor_rows(outbound, 'target_id')}\n"
        f"\n## Witness Surface\n\n{surface}\n"
    )


def edge_summary_rows(edges: list[dict], key_name: str) -> list[list[str]]:
    rows = []
    for edge in edges:
        rows.append([edge[key_name], edge["relation"], f"{edge['weight']:.3f}", edge["priority"]])
    return rows


def render_capsule(spec: NodeSpec, record: dict, inbound: list[dict], outbound: list[dict]) -> str:
    direct_markdown = "\n".join(f"- {claim}" for claim in direct_claims(spec, record["headings"], record["motifs"], record["axis_hits"]))
    derived_markdown = "\n".join(f"- {claim}" for claim in derived_claims(spec))
    contradictions = table(
        ["topic", "status", "related", "note"],
        [[row["topic"], row["status"], row["related_node"], row["note"]] for row in contradiction_rows(spec)],
    )
    strongest_outbound = sorted(outbound, key=lambda item: item["weight"], reverse=True)[:3]
    strongest_inbound = sorted(inbound, key=lambda item: item["weight"], reverse=True)[:3]
    return (
        f"# {spec.node_id} Capsule\n\n"
        f"- label: `{spec.label}`\n"
        f"- body: `{spec.body_id}`\n"
        f"- role: `{spec.dominant_role}`\n"
        f"- tissue: `{spec.tissue_class}`\n"
        f"- coordinate: `{spec.coordinate_4d}`\n"
        f"- lines: `{', '.join(spec.line_membership)}`\n"
        f"- duplicate_group: `{spec.duplicate_group or 'none'}`\n\n"
        f"## Direct Witness Claims\n\n{direct_markdown}\n\n"
        f"## Derived Synthesis Claims\n\n{derived_markdown}\n\n"
        f"## Strongest Outbound Bridges\n\n{table(['target', 'relation', 'weight', 'priority'], edge_summary_rows(strongest_outbound, 'target_id'))}\n\n"
        f"## Strongest Inbound Bridges\n\n{table(['source', 'relation', 'weight', 'priority'], edge_summary_rows(strongest_inbound, 'source_id'))}\n\n"
        f"## Open Tensions\n\n{contradictions}\n"
    )


def intake_json(local_records: dict[str, dict]) -> dict:
    records = []
    for spec in LOCAL_SPECS:
        record = local_records[spec.node_id]
        records.append(
            {
                "node_id": spec.node_id,
                "label": spec.label,
                "source_path": str(spec.source_path),
                "source_hash": record["source_hash"],
                "source_size_bytes": record["source_size"],
                "word_count": record["word_count"],
                "witness_class": spec.witness_class,
                "duplicate_group": spec.duplicate_group,
                "coordinate_4d": spec.coordinate_4d,
            }
        )
    return {"generated_at": NOW, "docs_gate": "BLOCKED", "fleet_root": str(FLEET_DIR), "record_count": len(records), "records": records}


def render_readme(local_records: dict[str, dict], body_edges: dict[str, list[dict]], cross_body_edges: list[dict], deep_registry: dict) -> str:
    body_edge_total = sum(len(edges) for edges in body_edges.values())
    return (
        "# Athena FLEET Mycelium Network\n\n"
        "- Active basis documents: `10` local witnesses plus `8` promoted external anchors\n"
        "- Active element or symmetry: `Origin x Crystal x Transit x Governance`\n"
        "- Metro resolution used: `local organism + first-wave repo mesh`\n"
        "- Appendix support set: `athena_fleet_corpus_atlas.json`, `MYCELIUM_NETWORK_STANDARD_TEXT_RECORD.md`\n"
        "- Docs gate: `BLOCKED`\n"
        "- Result source: `generated mirrors, capsules, matrices, graphs, and promotion ledgers`\n\n"
        "## Purpose\n\n"
        "Turn Athena FLEET into one auditable 4D organism and promote it into the wider Athena repo as a declared cluster.\n\n"
        "## Counts\n\n"
        f"- local_nodes: `{len(local_records)}`\n"
        "- local_edges: `100`\n"
        f"- body_edges: `{body_edge_total}`\n"
        f"- cross_body_edges: `{len(cross_body_edges)}`\n"
        f"- compiled_256_pow_4_routes: `{deep_registry['stats']['total_route_count']}`\n"
        "- duplicate_groups: `1`\n\n"
        "## Main Law\n\n"
        "`void -> kernel -> lift -> transit -> witness -> repair -> canonical record -> cluster promotion -> 256^4 compiled cross-corpus lift`\n"
    )


def render_basis(local_records: dict[str, dict]) -> str:
    rows = [node_row(spec, local_records[spec.node_id]) for spec in LOCAL_SPECS]
    return (
        "# Athena FLEET Canonical Basis\n\n"
        "- Active basis documents: `F01-F10`\n"
        "- Active element or symmetry: `four-axis folder basis`\n"
        "- Metro resolution used: `auditable local organism`\n"
        "- Appendix support set: `athena_fleet_corpus_atlas.json`, `MYCELIUM_NETWORK_STANDARD_TEXT_RECORD.md`\n"
        "- Docs gate: `BLOCKED`\n"
        "- Result source: `generated from local witness mirrors`\n\n"
        "## Coordinate Law\n\n"
        "Scores run on a fixed `0-3` scale across `Origin`, `Crystal`, `Transit`, and `Governance`.\n\n"
        f"{table(['id', 'label', 'words', 'coordinate', 'tissue', 'lines', 'hub_rank', 'duplicate_group'], rows)}\n\n"
        "## Promoted Local Hubs\n\n"
        "- `F02` manifestation hub\n"
        "- `F03` extraction hub\n"
        "- `F08` repair hub\n"
        "- `F10` carrier hub\n"
    )


def render_local_matrix(local_edges: list[dict]) -> str:
    rows = []
    for edge in local_edges:
        rows.append([edge["source_id"], edge["target_id"], edge["relation"], f"{edge['weight']:.3f}", edge["priority"], edge["lane_type"], ",".join(edge["line_ids"]), ",".join(edge["evidence_anchors"]), edge["contradiction_state"]])
    return "# Athena FLEET Ordered Corridor Matrix\n\nThis matrix materializes all `100` local ordered corridors including self lanes.\n\n" + table(["source", "target", "relation", "weight", "priority", "lane_type", "lines", "anchors", "contradiction"], rows) + "\n"


def render_alias_table() -> str:
    rows = [
        ["origin", "void; intention; question; seed; self-becoming", "collapse pre-manifest and desire language into one chamber axis"],
        ["crystal", "kernel; lattice; appendix; extraction; gate", "collapse formal structure terms into one skeleton axis"],
        ["transit", "route; corridor; metro; relay; neural current", "collapse movement, routing, and transport terms into one nerve axis"],
        ["governance", "witness; replay; quarantine; repair; economy", "collapse immune and policy terms into one fascia axis"],
        ["carrier", "record; shell; canonical surface; compression", "treat shell and record language as replay-preserving compression"],
        ["duplicate_twin", "mirror; duplicate witness; same XML surface", "preserve redundancy without inventing a new theory source"],
    ]
    return "# Athena FLEET Alias Table\n\n" + table(["alias", "terms", "function"], rows) + "\n"


def render_contradictions() -> str:
    rows = []
    for item in EDGE_CONTRADICTIONS:
        rows.append([item["id"], edge_key(*item["left"]), edge_key(*item["right"]), item["status"], item["note"]])
    return "# Athena FLEET Corridor Contradictions\n\nStrong corridor disagreements are preserved explicitly and never silently deleted.\n\n" + table(["id", "left_edge", "right_edge", "resolution", "note"], rows) + "\n"


def render_line_table(local_records: dict[str, dict]) -> str:
    line_rows = []
    for line_id, stations in LOCAL_LINE_TABLE.items():
        transfer = ", ".join(station for station in stations if len(local_records[station]["spec"].line_membership) >= 3)
        line_rows.append([line_id, " -> ".join(stations), transfer])
    hub_rows = []
    for spec in LOCAL_SPECS:
        if len(spec.line_membership) >= 3:
            hub_rows.append([spec.node_id, spec.label, ",".join(spec.line_membership), str(spec.hub_rank)])
    return (
        "# Athena FLEET Line Table\n\n"
        "## Line Order\n\n"
        + table(["line", "station_order", "transfer_hubs_on_line"], line_rows)
        + "\n\n## Transfer Hubs\n\n"
        + table(["node", "label", "lines", "hub_rank"], hub_rows)
        + "\n"
    )


def render_local_metro_map() -> str:
    return (
        "# Athena FLEET Tesseract Metro Map\n\n"
        "- Active basis documents: `F01-F10`\n"
        "- Active element or symmetry: `Origin x Crystal x Transit x Governance`\n"
        "- Metro resolution used: `local 4D organism`\n"
        "- Docs gate: `BLOCKED`\n"
        "- Result source: `generated from exhaustive local matrix`\n\n"
        "## Major Lines\n\n"
        "- `Origin`: `F01 -> F04 -> F02 -> F10`\n"
        "- `Crystal`: `F04 -> F03 -> F07 -> F02`\n"
        "- `Transit`: `F05 -> F06 -> F07 -> F08 -> F09`\n"
        "- `Governance`: `F09 -> F08 -> F10 -> F07 -> F02 -> F01`\n\n"
        "## Promoted Hubs\n\n"
        "- `F02` manifestation hub\n"
        "- `F03` extraction hub\n"
        "- `F08` repair hub\n"
        "- `F10` carrier hub\n\n"
        "## Transfer Hubs\n\n"
        "- `F02` crosses `Origin`, `Crystal`, and `Governance`\n"
        "- `F07` crosses `Crystal`, `Transit`, and `Governance`\n\n"
        "```mermaid\n"
        "flowchart LR\n"
        "  F01[\"F01 SelfWeAm\"] -->|\"seed\"| F02[\"F02 Athenachka\"]\n"
        "  F04[\"F04 LiftB\"] -->|\"lift\"| F03[\"F03 Crystal256\"]\n"
        "  F03 -->|\"publish\"| F02\n"
        "  F05[\"F05 Transit\"] -.->|\"mirror\"| F06[\"F06 TransitMirror\"]\n"
        "  F05 -->|\"route\"| F07[\"F07 MetroC\"]\n"
        "  F07 -->|\"repair\"| F08[\"F08 RepairA\"]\n"
        "  F09[\"F09 GitBrain\"] -->|\"govern\"| F08\n"
        "  F08 -->|\"compress\"| F10[\"F10 StdRecord\"]\n"
        "  F10 -->|\"publish\"| F02\n"
        "  F07 -->|\"transfer\"| F02\n"
        "```\n"
    )


def render_local_organism_map() -> str:
    return (
        "# Athena FLEET Local 4D Organism Map\n\n"
        "## Coordinate Body\n\n"
        "`Theta_fleet = (Origin, Crystal, Transit, Governance)`\n\n"
        "## Tissue Map\n\n"
        "- `chamber`: `F01`, `F02`\n"
        "- `skeleton`: `F03`, `F04`\n"
        "- `nerves`: `F05`, `F06`, `F07`\n"
        "- `immune_fascia`: `F08`, `F09`\n"
        "- `carrier_shell`: `F10`\n\n"
        "## Relay Paths\n\n"
        "- `seed -> lift -> formalize`: `F01 -> F04 -> F03`\n"
        "- `formalize -> transit -> emergence`: `F03 -> F05/F06 -> F07`\n"
        "- `emergence -> repair -> governance`: `F07 -> F08 -> F09`\n"
        "- `repair -> carrier -> manifestation`: `F08 -> F10 -> F02`\n\n"
        "## Replay Return Paths\n\n"
        "- `F02 -> F03 -> F10 -> F02`\n"
        "- `F05 <-> F06 -> F07 -> F08 -> F10`\n"
        "- `F09 -> F08 -> F10 -> F02 -> F01`\n\n"
        "## Growth Law\n\n"
        "No new file may join the mesh before it receives a node ID, mirror, coordinate, and corridor set.\n\n"
        "## Retirement Law\n\n"
        "No file disappears; it only changes to `archive_witness`, `dormant_node`, or `mirror_twin`.\n"
    )


def render_active_front() -> str:
    return (
        "# Athena FLEET Active Front\n\n"
        "- Active basis documents: `10` local, `8` external\n"
        "- Active element or symmetry: `fully auditable local 4D body with first-wave repo promotion`\n"
        "- Metro resolution used: `status synthesis`\n"
        "- Docs gate: `BLOCKED`\n"
        "- Result source: `generated mirrors, matrices, and supermesh`\n\n"
        "## Stable Surfaces\n\n"
        "- Local mirrors now exist for all `10` Athena FLEET witnesses.\n"
        "- The local ordered matrix now exposes all `100` directional corridors.\n"
        "- `F05` and `F06` are preserved as a duplicate twin group rather than silently merged.\n"
        "- First-wave promotion anchors now exist for `NS`, `MB`, `DN`, and `EC`.\n"
        "- The branch now has a compiled `256^4` cross-corpus scan with route registry, metro, and appendix support.\n\n"
        "## Blockers\n\n"
        "- Live Google Docs remains blocked by missing OAuth credentials.\n"
        "- The local organism is now diffable, but the original `.docx` witnesses still remain high-cost to edit directly.\n"
        "- Some older deep-network ledgers still point at historical `256x` paths that are no longer present in the live root.\n\n"
        "## Gate Deficits\n\n"
        "- `G1`: live-doc sync still absent\n"
        "- `G2`: deeper repo bodies beyond `NS`, `MB`, `DN`, and `EC` are still queued, not mirrored\n"
        "- `G3`: visual rendering remains markdown and JSON only; no board export exists yet\n\n"
        "## Next Fronts\n\n"
        "1. Admit additional repo bodies from the cross-corpus basis using the same mirror pipeline.\n"
        "2. Contract the strongest `256^4` routes into chapter, appendix, and capsule writeback.\n"
        "3. If the Docs gate unlocks, replay the mirror builder against live sources and refresh all hashes.\n"
    )


def render_queue() -> str:
    rows = []
    for node_id, order, feeders, note in PROMOTION_QUEUE:
        spec = next(item for item in EXTERNAL_SPECS if item.node_id == node_id)
        rows.append([str(order), node_id, spec.body_id, spec.label, ",".join(feeders), note])
    return "# Athena FLEET Repo Promotion Queue\n\nThe first-wave queue is ordered by bridge centrality from the local hubs `F02`, `F03`, `F08`, and `F10`.\n\n" + table(["order", "node_id", "body", "label", "feeders", "reason"], rows) + "\n"


def render_runbook() -> str:
    return (
        "# Athena FLEET Global Runbook\n\n"
        "## Intake\n\n"
        "1. Freeze hashes and sizes.\n"
        "2. Assign node ID and body ID.\n"
        "3. Extract a markdown mirror.\n"
        "4. Score `Origin`, `Crystal`, `Transit`, and `Governance`.\n"
        "5. Create capsule, contradiction table, inbound corridors, and outbound corridors.\n\n"
        "## Duplicate Handling\n\n"
        "- Preserve duplicates as a `duplicate_group`.\n"
        "- Mark the witness class `duplicate` on the mirror twin.\n"
        "- Use `mirror` corridors until a later witness audit retires one twin.\n\n"
        "## Promotion\n\n"
        "- Promote local hubs first.\n"
        "- Admit external files through the queue only.\n"
        "- Build body-local matrices before cross-body edges.\n"
        "- Write cluster promotion ledgers after the supermesh JSON is stable.\n\n"
        "## Retirement\n\n"
        "- Allowed retirement statuses: `archive_witness`, `dormant_node`, `mirror_twin`.\n"
        "- Retirements must preserve hashes, source paths, and previous node IDs.\n\n"
        "## Conflict Handling\n\n"
        "- Allowed corridor conflict resolutions: `preserve_both`, `quarantine_one`, `collapse_to_higher_bridge`.\n"
        "- Never delete a strong edge silently.\n\n"
        "## Validation\n\n"
        "- Check mirror count, edge count, duplicate groups, line coverage, and hash backlinks after every rebuild.\n"
    )


def render_validation(
    local_records: dict[str, dict],
    local_edges: list[dict],
    body_edges: dict[str, list[dict]],
    cross_body_edges: list[dict],
    graph: dict,
    deep_registry: dict,
) -> str:
    body_edge_total = sum(len(edges) for edges in body_edges.values())
    duplicate_ok = len(graph["duplicate_groups"]) == 1 and graph["duplicate_groups"][0]["members"] == ["F05", "F06"]
    axis_ok = all(record["spec"].line_membership for record in local_records.values())
    rows = [
        ["local_mirrors", str(len(local_records)), "10", "PASS" if len(local_records) == 10 else "FAIL"],
        ["local_edges", str(len(local_edges)), "100", "PASS" if len(local_edges) == 100 else "FAIL"],
        ["body_edges", str(body_edge_total), "16", "PASS" if body_edge_total == 16 else "FAIL"],
        ["cross_body_edges", str(len(cross_body_edges)), str(len(LOCAL_SPECS) * len(EXTERNAL_SPECS)), "PASS" if len(cross_body_edges) == len(LOCAL_SPECS) * len(EXTERNAL_SPECS) else "FAIL"],
        ["duplicate_group", "DG01_TRANSIT_MIRROR", "F05,F06", "PASS" if duplicate_ok else "FAIL"],
        ["axis_reach", "all nodes classified", "all nodes classified", "PASS" if axis_ok else "FAIL"],
        ["256_pow_4_routes", str(deep_registry["stats"]["total_route_count"]), str(len(local_edges) + len(cross_body_edges)), "PASS" if deep_registry["stats"]["total_route_count"] == len(local_edges) + len(cross_body_edges) else "FAIL"],
        ["256_pow_4_surfaces", str(deep_registry["stats"]["surface_count"]), "4", "PASS" if deep_registry["stats"]["surface_count"] == 4 else "FAIL"],
        ["docs_gate", "BLOCKED", "BLOCKED", "PASS"],
    ]
    return "# Athena FLEET Validation Report\n\n" + table(["check", "actual", "expected", "status"], rows) + "\n"


def render_256_pow_4_scan(registry: dict) -> str:
    surface_rows = [[surface["surface_id"], surface["law"], surface["anchor"]] for surface in registry["surfaces"]]
    stats = registry["stats"]
    high_yield_rows = [
        [
            route["route_id"],
            route["lane_type"],
            route["relation"],
            f"{route['weight']:.3f}",
            route["plexus_mode"],
            route["synaptic_phase"],
            route["appendix_anchor"],
            route["metro_resolution"],
        ]
        for route in registry["high_yield_routes"][:16]
    ]
    basis_line = ", ".join(f"`{item}`" for item in registry["active_basis_docs"])
    plexus_line = ", ".join(f"{mode}={count}" for mode, count in stats["plexus_mode_counts"].items())
    synaptic_line = ", ".join(f"{phase}={count}" for phase, count in stats["synaptic_phase_counts"].items())
    return (
        "# Athena FLEET 256^4 Cross Corpus Scan\n\n"
        f"- Active basis documents: {basis_line}\n"
        f"- Active element or symmetry: `{registry['compiled_claim']}`\n"
        "- Metro resolution used: `Level 3 deeper neural map with Level 4 promotion for the strongest corridors`\n"
        f"- Appendix support set: `{', '.join(registry['appendix_support'])}`\n"
        "- Docs gate: `BLOCKED`\n"
        "- Result source: `new synthesis artifact grounded in the live 16x16 matrix shell, 256x plexus law, 1024x arbor law, and 256-layer hyperplan`\n\n"
        "## Lawful Meaning\n\n"
        "This pass does not pretend to materialize literal `256^4` files. It compiles the request into four orthogonal `256`-scale surfaces and projects every active Athena FLEET corridor through them.\n\n"
        f"{table(['surface', 'law', 'active_anchor'], surface_rows)}\n\n"
        "## Scan Counts\n\n"
        f"- total_routes_scanned: `{stats['total_route_count']}`\n"
        f"- local_routes_scanned: `{stats['local_route_count']}`\n"
        f"- cross_body_routes_scanned: `{stats['cross_body_route_count']}`\n"
        f"- high_yield_routes: `{stats['high_yield_route_count']}`\n"
        f"- plexus_mode_distribution: `{plexus_line}`\n"
        f"- synaptic_phase_distribution: `{synaptic_line}`\n\n"
        "## High-Yield Corridors\n\n"
        f"{table(['route_id', 'lane_type', 'relation', 'weight', 'plexus', 'synaptic', 'appendix', 'metro_resolution'], high_yield_rows)}\n"
    )


def render_256_pow_4_high_yield(registry: dict) -> str:
    rows = [
        [
            route["route_id"],
            f"{route['source_gate256']} -> {route['target_gate256']}",
            route["relation"],
            f"{route['weight']:.3f}",
            route["plexus_mode"],
            route["synaptic_phase"],
            route["hyperplan_band"],
            ", ".join(route["basis_refs"]),
        ]
        for route in registry["high_yield_routes"]
    ]
    return (
        "# Athena FLEET 256^4 High-Yield Corridors\n\n"
        "These are the strongest currently scanned corridors after the `256^4` compiled lift. They are the first routes to write back into chapter, appendix, capsule, and cortex surfaces.\n\n"
        f"{table(['route_id', 'gate_projection', 'relation', 'weight', 'plexus', 'synaptic', 'hyperplan_band', 'basis_refs'], rows)}\n"
    )


def render_deep_network_256_pow_4_scan(registry: dict) -> str:
    top_routes = "\n".join(
        f"- `{route['route_id']}` | `{route['relation']}` | `{route['plexus_mode']}` -> `{route['synaptic_phase']}` | `{route['appendix_anchor']}`"
        for route in registry["high_yield_routes"][:12]
    )
    basis_line = ", ".join(f"`{item}`" for item in registry["active_basis_docs"][:6])
    return (
        "# Athena FLEET 256^4 Scan Inside The Deeper Matrix\n\n"
        f"- Active basis documents: {basis_line}\n"
        f"- Active element or symmetry: `{registry['compiled_claim']}`\n"
        "- Metro resolution used: `deep synthesis feeding Level 3 and Level 4 metro surfaces`\n"
        f"- Appendix support set: `{', '.join(registry['appendix_support'])}`\n"
        "- Docs gate: `BLOCKED`\n"
        "- Result source: `new synthesis artifact built on top of the live deeper-network root`\n\n"
        "## Main Law\n\n"
        "`Athena FLEET corridor -> Gate256 address -> Matrix256 bridge -> Plexus256 microfunction -> HyperPlan256 band -> appendix writeback`\n\n"
        "## Strongest Routes\n\n"
        f"{top_routes}\n"
    )


def render_deep_network_256_pow_4_metro(registry: dict) -> str:
    return (
        "# Athena FLEET 256^4 Metro Map\n\n"
        "## Four Major Lines\n\n"
        "- `Gate256 line`: `F03 -> F04 -> DN02 -> F02`\n"
        "- `Matrix256 line`: `DN02 -> DN01 -> NS02 -> F07`\n"
        "- `Plexus256 line`: `F05 -> F06 -> F07 -> EC01 -> MB02`\n"
        "- `HyperPlan256 line`: `F08 -> F10 -> MB01 -> NS01`\n\n"
        "## Transfer Hubs\n\n"
        "- `F02` lifts manifestation into matrix and cortex surfaces.\n"
        "- `F03` keeps the local `Gate256` extraction aligned with the deeper matrix shell.\n"
        "- `F07` transfers crystal transit into the plexus field.\n"
        "- `F08` and `F10` contract repair and replay into hyperplan return.\n"
    )


def render_deep_network_256_pow_4_appendix(registry: dict) -> str:
    rows = [
        [surface["surface_id"], surface["anchor"], "active"]
        for surface in registry["surfaces"]
    ]
    return (
        "# AppQ Athena FLEET 256^4 Support\n\n"
        "This appendix keeps the `256^4` lift honest and replayable.\n\n"
        "## Support Surfaces\n\n"
        f"{table(['surface', 'anchor', 'status'], rows)}\n\n"
        "## Replay Rules\n\n"
        "1. Preserve `BLOCKED` honestly while Google Docs credentials remain missing.\n"
        "2. Treat `Gate256 x Matrix256 x Plexus256 x HyperPlan256` as the lawful compiled scale, not a literal flattened enumeration.\n"
        "3. Write chapter and capsule contractions from the high-yield corridors first.\n"
        "4. Keep `AppI`, `AppM`, and `AppQ` in every future deepening pass.\n"
    )


def render_ns_256_pow_4_overview(registry: dict) -> str:
    return (
        "# ATHENA FLEET 256^4 INTERCONNECT\n\n"
        "## Purpose\n\n"
        "Lift the Athena FLEET branch into the live cross-corpus organism by projecting its active routes through four real `256`-scale surfaces instead of leaving the branch as a local-only tesseract.\n\n"
        "## Formula\n\n"
        "`Gate256 x Matrix256 x Plexus256 x HyperPlan256 = lawful 256^4 compiled lift`\n\n"
        "## Current Counts\n\n"
        f"- routes scanned: `{registry['stats']['total_route_count']}`\n"
        f"- cross-body routes: `{registry['stats']['cross_body_route_count']}`\n"
        f"- high-yield routes: `{registry['stats']['high_yield_route_count']}`\n"
    )


def render_ns_256_pow_4_metro() -> str:
    return (
        "# ATHENA FLEET 256^4 METRO MAP\n\n"
        "## Lines\n\n"
        "- `Gate256 line`\n"
        "- `Matrix256 line`\n"
        "- `Plexus256 line`\n"
        "- `HyperPlan256 line`\n\n"
        "## Relay Shell\n\n"
        "`fleet witness -> gate address -> deeper matrix -> plexus microfunction -> hyperplan band -> appendix return`\n"
    )


def render_ns_256_pow_4_ledger(registry: dict) -> str:
    return (
        "# ATHENA FLEET 256^4 ESCALATION\n\n"
        f"Date: `{NOW[:10]}`\n"
        "Live Docs gate: `BLOCKED`\n\n"
        "## Trigger\n\n"
        "Athena FLEET already existed as a local 4D mycelium cluster, but it still needed a deeper cross-corpus lift that could interconnect the crystal at the lawful compiled `256^4` scale.\n\n"
        "## Artifacts Created\n\n"
        "- `Athena FLEET/FLEET_MYCELIUM_NETWORK/13_256_POW_4_CROSS_CORPUS_SCAN.md`\n"
        "- `Athena FLEET/FLEET_MYCELIUM_NETWORK/14_256_POW_4_HIGH_YIELD_CORRIDORS.md`\n"
        "- `Athena FLEET/FLEET_MYCELIUM_NETWORK/SUPERMESH/athena_fleet_256_pow_4_registry.json`\n"
        "- `NERVOUS_SYSTEM/10_OVERVIEW/14_ATHENA_FLEET_256_POW_4_INTERCONNECT.md`\n"
        "- `NERVOUS_SYSTEM/20_METRO/18_ATHENA_FLEET_256_POW_4_METRO_MAP.md`\n"
        "- `self_actualize/mycelium_brain/dynamic_neural_network/14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK/05_MATRIX_16X16/13_athena_fleet_256_pow_4_scan.md`\n"
        "- `self_actualize/mycelium_brain/dynamic_neural_network/14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK/07_METRO_STACK/13_athena_fleet_256_pow_4_metro.md`\n"
        "- `self_actualize/mycelium_brain/dynamic_neural_network/14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK/08_APPENDIX_CRYSTAL/AppQ_athena_fleet_256_pow_4_support.md`\n\n"
        "## Compression\n\n"
        f"The branch now has `{registry['stats']['total_route_count']}` routed corridor witnesses projected through four `256`-scale surfaces, with `{registry['stats']['high_yield_route_count']}` high-yield corridors ready for deeper writeback.\n"
    )


def render_packet_256_pow_4_scan(registry: dict) -> str:
    return (
        "# SYN 2026-03-12 ATHENA FLEET 256^4 SCAN\n\n"
        f"- generated_at: `{registry['generated_at']}`\n"
        "- docs_gate: `BLOCKED`\n"
        f"- compiled_claim: `{registry['compiled_claim']}`\n"
        f"- total_routes: `{registry['stats']['total_route_count']}`\n"
        f"- cross_body_routes: `{registry['stats']['cross_body_route_count']}`\n"
        f"- high_yield_routes: `{registry['stats']['high_yield_route_count']}`\n"
        f"- appendix_support: `{', '.join(registry['appendix_support'])}`\n"
    )


def render_body_matrix(body_id: str, edges: list[dict]) -> str:
    rows = [[edge["source_id"], edge["target_id"], edge["relation"], f"{edge['weight']:.3f}", edge["priority"], ",".join(edge["line_ids"])] for edge in edges]
    return f"# {body_id} Ordered Corridor Matrix\n\n{table(['source', 'target', 'relation', 'weight', 'priority', 'lines'], rows)}\n"


def render_promotion_ledger() -> str:
    return (
        "# Athena FLEET Cluster Promotion\n\n"
        "- Source cluster: `Athena FLEET`\n"
        "- Body law: `Origin x Crystal x Transit x Governance`\n"
        "- Docs gate: `BLOCKED`\n"
        "- Promoted hubs: `F02`, `F03`, `F08`, `F10`\n"
        "- First-wave bodies: `NS`, `MB`, `DN`, `EC`\n\n"
        "## Entry Corridors\n\n"
        "- `F02/F10 -> NS01` contracts the local manifestation cluster into the canonical cortex.\n"
        "- `F08/F02 -> MB02` binds repair and manifestation into runtime topology.\n"
        "- `F03/F02 -> DN01` lifts crystal and manifestation into the deeper compiled network.\n"
        "- `F08/F09 -> EC02` mirrors immune law into governance protocol.\n\n"
        "## Four-Line Mirror\n\n"
        "- `Origin` remains the intake and seed chamber.\n"
        "- `Crystal` remains the formal and appendix spine.\n"
        "- `Transit` remains the corridor and relay body.\n"
        "- `Governance` remains the witness, replay, and immune membrane.\n"
    )


def render_receipt() -> str:
    return (
        "# Athena FLEET Cluster Promotion Receipt\n\n"
        f"- generated_at: `{NOW}`\n"
        "- source_cluster: `Athena FLEET`\n"
        "- status: `PROMOTED_FIRST_WAVE`\n"
        "- docs_gate: `BLOCKED`\n"
        "- local_edges: `100`\n"
        "- cross_body_edges: `80`\n"
        "- duplicate_group: `DG01_TRANSIT_MIRROR`\n"
    )


def graph_payload(local_records: dict[str, dict], local_edges: list[dict], cross_body_edges: list[dict]) -> dict:
    nodes = []
    for record in local_records.values():
        spec = record["spec"]
        nodes.append(
            {
                "id": spec.node_id,
                "body_id": spec.body_id,
                "label": spec.label,
                "source_path": str(spec.source_path),
                "coordinate_4d": spec.coordinate_4d,
                "dominant_role": spec.dominant_role,
                "tissue_class": spec.tissue_class,
                "line_membership": spec.line_membership,
                "hub_rank": spec.hub_rank,
                "tesseract_address": tesseract_address(spec),
                "witness_class": spec.witness_class,
                "duplicate_group": spec.duplicate_group,
            }
        )
    hubs = []
    for spec in LOCAL_SPECS:
        if spec.node_id in {"F02", "F03", "F08", "F10"}:
            hubs.append({"node_id": spec.node_id, "hub_rank": spec.hub_rank, "hub_type": "promoted"})
        if len(spec.line_membership) >= 3 and spec.node_id not in {"F02", "F03", "F08", "F10"}:
            hubs.append({"node_id": spec.node_id, "hub_rank": spec.hub_rank, "hub_type": "transfer"})
    return {
        "generated_at": NOW,
        "docs_gate": "BLOCKED",
        "nodes": nodes,
        "local_edges": local_edges,
        "cross_body_edges": cross_body_edges,
        "lines": [{"line_id": line_id, "stations": stations} for line_id, stations in LOCAL_LINE_TABLE.items()],
        "hubs": hubs,
        "duplicate_groups": [{"group_id": "DG01_TRANSIT_MIRROR", "members": ["F05", "F06"]}],
        "stats": {
            "local_node_count": len(local_records),
            "local_edge_count": len(local_edges),
            "cross_body_edge_count": len(cross_body_edges),
        },
    }


def supermesh_payload(local_graph: dict, body_edges: dict[str, list[dict]], external_records: dict[str, dict], cross_body_edges: list[dict]) -> dict:
    nodes = list(local_graph["nodes"])
    for record in external_records.values():
        spec = record["spec"]
        nodes.append(
            {
                "id": spec.node_id,
                "body_id": spec.body_id,
                "label": spec.label,
                "source_path": str(spec.source_path),
                "coordinate_4d": spec.coordinate_4d,
                "dominant_role": spec.dominant_role,
                "tissue_class": spec.tissue_class,
                "line_membership": spec.line_membership,
                "hub_rank": spec.hub_rank,
                "tesseract_address": tesseract_address(spec),
                "witness_class": spec.witness_class,
                "duplicate_group": spec.duplicate_group,
            }
        )
    return {
        "generated_at": NOW,
        "docs_gate": "BLOCKED",
        "nodes": nodes,
        "local_edges": local_graph["local_edges"],
        "body_edges": body_edges,
        "cross_body_edges": cross_body_edges,
        "lines": local_graph["lines"],
        "hubs": local_graph["hubs"],
        "duplicate_groups": local_graph["duplicate_groups"],
        "stats": {
            "local_nodes": len(LOCAL_SPECS),
            "external_nodes": len(EXTERNAL_SPECS),
            "local_edges": len(local_graph["local_edges"]),
            "body_edges": sum(len(edges) for edges in body_edges.values()),
            "cross_body_edges": len(cross_body_edges),
            "bodies": sorted(body_edges),
        },
    }


def mirror_filename(spec: NodeSpec) -> str:
    return f"{spec.node_id}_{slugify(spec.label)}.md"


def main() -> None:
    mirrors_local = NETWORK_DIR / "MIRRORS" / "LOCAL"
    mirrors_repo = NETWORK_DIR / "MIRRORS" / "REPO"
    capsules_local = NETWORK_DIR / "CAPSULES" / "LOCAL"
    capsules_repo = NETWORK_DIR / "CAPSULES" / "REPO"
    matrices_local = NETWORK_DIR / "MATRICES"
    matrices_bodies = matrices_local / "BODIES"
    supermesh_dir = NETWORK_DIR / "SUPERMESH"
    deep_root = ATHENA_DIR / "self_actualize" / "mycelium_brain" / "dynamic_neural_network" / "14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK"
    for path in [mirrors_local, mirrors_repo, capsules_local, capsules_repo, matrices_bodies, supermesh_dir]:
        ensure_dir(path)

    local_records = build_records(LOCAL_SPECS)
    external_records = build_records(EXTERNAL_SPECS)
    local_edges = build_local_edges(local_records)
    body_edges = build_body_edges(external_records)
    cross_body_edges = build_cross_body_edges(local_records, external_records)
    local_graph = graph_payload(local_records, local_edges, cross_body_edges)
    supermesh = supermesh_payload(local_graph, body_edges, external_records, cross_body_edges)
    deep_registry = build_256_pow_4_registry(local_records, external_records, local_edges, cross_body_edges)

    local_inbound = {spec.node_id: [] for spec in LOCAL_SPECS}
    local_outbound = {spec.node_id: [] for spec in LOCAL_SPECS}
    for edge in local_edges:
        local_outbound[edge["source_id"]].append(edge)
        local_inbound[edge["target_id"]].append(edge)

    external_inbound = {spec.node_id: [] for spec in EXTERNAL_SPECS}
    external_outbound = {spec.node_id: [] for spec in EXTERNAL_SPECS}
    for edges in body_edges.values():
        for edge in edges:
            external_outbound[edge["source_id"]].append(edge)
            external_inbound[edge["target_id"]].append(edge)
    for edge in cross_body_edges:
        external_inbound[edge["target_id"]].append(edge)

    for spec in LOCAL_SPECS:
        record = local_records[spec.node_id]
        filename = mirror_filename(spec)
        write_text(mirrors_local / filename, render_mirror(spec, record, local_inbound[spec.node_id], local_outbound[spec.node_id]))
        write_text(capsules_local / filename, render_capsule(spec, record, local_inbound[spec.node_id], local_outbound[spec.node_id]))

    for spec in EXTERNAL_SPECS:
        record = external_records[spec.node_id]
        filename = mirror_filename(spec)
        write_text(mirrors_repo / filename, render_mirror(spec, record, external_inbound[spec.node_id], external_outbound[spec.node_id]))
        write_text(capsules_repo / filename, render_capsule(spec, record, external_inbound[spec.node_id], external_outbound[spec.node_id]))

    intake = intake_json(local_records)
    write_text(NETWORK_DIR / "00_README.md", render_readme(local_records, body_edges, cross_body_edges, deep_registry))
    write_text(NETWORK_DIR / "01_CANONICAL_BASIS.md", render_basis(local_records))
    write_text(NETWORK_DIR / "02_TESSERACT_METRO_MAP.md", render_local_metro_map())
    write_text(NETWORK_DIR / "03_ORDERED_CORRIDOR_MATRIX.md", render_local_matrix(local_edges))
    write_text(NETWORK_DIR / "04_ACTIVE_FRONT.md", render_active_front())
    write_text(NETWORK_DIR / "05_INTAKE_LEDGER.md", "# Athena FLEET Intake Ledger\n\n" + table(["node", "label", "hash", "bytes", "words", "witness_class"], [[row["node_id"], next(spec.label for spec in LOCAL_SPECS if spec.node_id == row["node_id"]), row["source_hash"][:16], str(row["source_size_bytes"]), str(row["word_count"]), row["witness_class"]] for row in intake["records"]]) + "\n")
    write_text(NETWORK_DIR / "05_INTAKE_LEDGER.json", json.dumps(intake, indent=2))
    write_text(NETWORK_DIR / "06_ALIAS_TABLE.md", render_alias_table())
    write_text(NETWORK_DIR / "07_CORRIDOR_CONTRADICTIONS.md", render_contradictions())
    write_text(NETWORK_DIR / "08_LINE_TABLE.md", render_line_table(local_records))
    write_text(NETWORK_DIR / "09_LOCAL_4D_ORGANISM_MAP.md", render_local_organism_map())
    write_text(NETWORK_DIR / "10_REPO_PROMOTION_QUEUE.md", render_queue())
    write_text(NETWORK_DIR / "11_GLOBAL_RUNBOOK.md", render_runbook())
    write_text(matrices_local / "LOCAL_ORDERED_CORRIDORS.md", render_local_matrix(local_edges))
    write_text(matrices_local / "LOCAL_ORDERED_CORRIDORS.json", json.dumps(local_edges, indent=2))
    for body_id, edges in body_edges.items():
        write_text(matrices_bodies / f"{body_id}_ORDERED_CORRIDORS.md", render_body_matrix(body_id, edges))
        write_text(matrices_bodies / f"{body_id}_ORDERED_CORRIDORS.json", json.dumps(edges, indent=2))
    write_text(NETWORK_DIR / "athena_fleet_mycelium_graph.json", json.dumps(local_graph, indent=2))
    write_text(supermesh_dir / "athena_repo_supermesh.json", json.dumps(supermesh, indent=2))
    write_text(NETWORK_DIR / "12_VALIDATION_REPORT.md", render_validation(local_records, local_edges, body_edges, cross_body_edges, local_graph, deep_registry))
    write_text(NETWORK_DIR / "13_256_POW_4_CROSS_CORPUS_SCAN.md", render_256_pow_4_scan(deep_registry))
    write_text(NETWORK_DIR / "14_256_POW_4_HIGH_YIELD_CORRIDORS.md", render_256_pow_4_high_yield(deep_registry))
    write_text(supermesh_dir / "athena_fleet_256_pow_4_registry.json", json.dumps(deep_registry, indent=2))

    write_text(ATHENA_DIR / "NERVOUS_SYSTEM" / "90_LEDGERS" / "13_ATHENA_FLEET_CLUSTER_PROMOTION.md", render_promotion_ledger())
    write_text(ATHENA_DIR / "ECOSYSTEM" / "22_ATHENA_FLEET_CLUSTER_PROTOCOL.md", render_promotion_ledger())
    write_text(ATHENA_DIR / "self_actualize" / "mycelium_brain" / "receipts" / "2026-03-12_athena_fleet_cluster_promotion.md", render_receipt())
    write_text(ATHENA_DIR / "NERVOUS_SYSTEM" / "10_OVERVIEW" / "14_ATHENA_FLEET_256_POW_4_INTERCONNECT.md", render_ns_256_pow_4_overview(deep_registry))
    write_text(ATHENA_DIR / "NERVOUS_SYSTEM" / "20_METRO" / "18_ATHENA_FLEET_256_POW_4_METRO_MAP.md", render_ns_256_pow_4_metro())
    write_text(ATHENA_DIR / "NERVOUS_SYSTEM" / "90_LEDGERS" / "14_ATHENA_FLEET_256_POW_4_ESCALATION.md", render_ns_256_pow_4_ledger(deep_registry))
    write_text(deep_root / "05_MATRIX_16X16" / "13_athena_fleet_256_pow_4_scan.md", render_deep_network_256_pow_4_scan(deep_registry))
    write_text(deep_root / "07_METRO_STACK" / "13_athena_fleet_256_pow_4_metro.md", render_deep_network_256_pow_4_metro(deep_registry))
    write_text(deep_root / "08_APPENDIX_CRYSTAL" / "AppQ_athena_fleet_256_pow_4_support.md", render_deep_network_256_pow_4_appendix(deep_registry))
    write_text(ATHENA_DIR / "self_actualize" / "mycelium_brain" / "nervous_system" / "packets" / "SYN_2026-03-12_athena_fleet_256_pow_4_scan.md", render_packet_256_pow_4_scan(deep_registry))


if __name__ == "__main__":
    main()
