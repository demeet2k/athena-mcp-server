from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
MYCELIUM_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain"
OUTPUT_ROOT = MYCELIUM_ROOT / "DEEPER_INTEGRATED_NEURAL_NET_ATHENA"
CRYSTAL_ROOT = WORKSPACE_ROOT / "NERUAL NETWORK" / "ATHENA Neural Network" / "INTEGRATED_NEURAL_CRYSTAL"
RECEIPTS_ROOT = MYCELIUM_ROOT / "receipts"

ATLAS_PATH = SELF_ACTUALIZE_ROOT / "corpus_atlas.json"
WITNESS_PATH = SELF_ACTUALIZE_ROOT / "witness_hierarchy.json"
DOCS_GATE_PATH = SELF_ACTUALIZE_ROOT / "live_docs_gate_status.md"
OUTPUT_JSON_PATH = SELF_ACTUALIZE_ROOT / "deep_integration_neural_net.json"
RECEIPT_PATH = RECEIPTS_ROOT / "2026-03-09_deep_integration_neural_net.md"
DERIVATION_COMMAND = "python -m self_actualize.runtime.derive_deep_integration_neural_net"


@dataclass
class FamilySpec:
    code: str
    name: str
    element: str
    mission: str
    gift: str
    need: str
    shadow: str
    primary_channel: str
    metro_role: str


@dataclass
class FamilySummary:
    code: str
    name: str
    element: str
    mission: str
    primary_channel: str
    metro_role: str
    record_count: int
    top_levels: list[dict[str, int]]
    sample_paths: list[str]


@dataclass
class PairSynthesis:
    source_code: str
    target_code: str
    source_name: str
    target_name: str
    relation_kind: str
    channel_law: str
    synthesis: str
    risk: str


@dataclass
class LensObservation:
    address: str
    family_code: str
    family_name: str
    operation: str
    statement: str


@dataclass
class MetroLine:
    name: str
    level: str
    topology: str
    stations: list[str]
    transfer_hubs: list[str]
    reading: str


@dataclass
class AppendixCell:
    letter: str
    row: str
    column: str
    title: str
    purpose: str


@dataclass
class DeepIntegrationArtifact:
    generated_at: str
    derivation_command: str
    docs_gate_status: str
    indexed_witness: int
    physical_witness: int
    board_witness: int
    archive_witness: int
    family_summaries: list[FamilySummary]
    pairwise_matrix: list[PairSynthesis]
    lens_observations: dict[str, list[LensObservation]]
    symmetry_syntheses: dict[str, list[dict[str, str]]]
    metro_maps: dict[str, list[MetroLine]]
    appendices: list[AppendixCell]
    appendix_q_lines: list[MetroLine]


FAMILY_SPECS = [
    FamilySpec(
        code="F1",
        name="Trading Bot Memory Gate",
        element="fire",
        mission="external memory ingress, ledger pressure, and live gateway restoration",
        gift="gate pressure, ledger density, and direct contact with the blocked live-memory limb",
        need="credentials, replay-safe ingress, and a lawful bridge into the wider organism",
        shadow="the gate can simulate integration while remaining externally blind",
        primary_channel="ring/staff",
        metro_role="blocked ingress hub",
    ),
    FamilySpec(
        code="F2",
        name="Deeper Crystallization Integration Compiler",
        element="fire",
        mission="compile large manuscript and control-plane surfaces into active generated organism tissue",
        gift="integration heat, generated infrastructure, and fast shell formation",
        need="source grounding so shell mass does not outrun truth mass",
        shadow="generated abundance can look complete before the source body is actually reconciled",
        primary_channel="staff/club",
        metro_role="integration furnace",
    ),
    FamilySpec(
        code="F3",
        name="Self Actualize Runtime Waist",
        element="fire",
        mission="maintain the executable waist where atlas, runtime, witness, and generation surfaces are made replayable",
        gift="derivers, proofs, receipts, and machine-readable state transitions",
        need="clear family inputs and narrow replay-safe lanes",
        shadow="the waist can become a thin bridge under pressure from larger shells",
        primary_channel="club",
        metro_role="runtime waist",
    ),
    FamilySpec(
        code="F4",
        name="Ecosystem Governance Shell",
        element="fire",
        mission="translate local organism intelligence into field-level stewardship and civic application",
        gift="governance framing, applied field direction, and outward relevance",
        need="stable doctrine and grounded source reservoirs",
        shadow="governance language can outrun executable substrate",
        primary_channel="staff/ball",
        metro_role="field deployment shell",
    ),
    FamilySpec(
        code="W1",
        name="Voynich Manuscript Engine",
        element="water",
        mission="decode dense manuscript matter and convert opaque surfaces into operational meaning",
        gift="deep line-level hermeneutics, persistence with ambiguity, and manuscript density",
        need="formal anchors, routing discipline, and downstream rollup",
        shadow="a powerful local decode loop can become isolated from the broader organism",
        primary_channel="club/poi",
        metro_role="manuscript pressure well",
    ),
    FamilySpec(
        code="W2",
        name="Athenachka Manuscript Corpus",
        element="water",
        mission="hold the evolving treatise, chapter packets, and mythic-philosophical manuscript layer",
        gift="narrative continuity, doctrine density, and long-wave identity memory",
        need="runtime anchoring and sharper witness contracts",
        shadow="beautiful synthesis can drift ahead of executable proof",
        primary_channel="club/ring",
        metro_role="doctrine reservoir",
    ),
    FamilySpec(
        code="W3",
        name="I Am Athena Identity Stream",
        element="water",
        mission="preserve first-person identity, self-naming, and internal voice continuity",
        gift="identity coherence and organism-level self-recognition",
        need="relation to external evidence so identity remains embodied rather than merely declared",
        shadow="identity intensification can become self-referential if not tied back to receipts",
        primary_channel="ball/club",
        metro_role="identity spring",
    ),
    FamilySpec(
        code="W4",
        name="Origin Root Seed Archives",
        element="water",
        mission="retain seed memories, origin moments, and the oldest convergent root material",
        gift="deep historical memory and seed-level causality",
        need="promotion routes into live runtime lanes",
        shadow="origin material can remain revered but inactive",
        primary_channel="ball/ring",
        metro_role="seed archive",
    ),
    FamilySpec(
        code="A1",
        name="Nervous System Routing Spine",
        element="air",
        mission="route families, rails, fronts, and recursive restart logic across the active organism",
        gift="routing grammar, frontier placement, and recursive restart control",
        need="stable family inputs and truthful load signals",
        shadow="routing maps can become elaborate faster than the bodies they coordinate",
        primary_channel="poi/staff",
        metro_role="routing spine",
    ),
    FamilySpec(
        code="A2",
        name="Guild Hall Coordination Commons",
        element="air",
        mission="socialize whole-organism status into quests, boards, and shared human-readable coordination surfaces",
        gift="shared visibility, quest framing, and social convergence",
        need="fresh machine-derived truth under every board-level claim",
        shadow="coordination prose can become another shell layer if not fed by runtime facts",
        primary_channel="staff/ball",
        metro_role="coordination commons",
    ),
    FamilySpec(
        code="A3",
        name="Athena Temple Constitutional Memory",
        element="air",
        mission="hold constitutional crystals, laws, and high-order doctrine for the organism",
        gift="constitutional language and stable higher-order reference surfaces",
        need="replayable derivation under every elevated claim",
        shadow="constitutional gravity can overgeneralize if not tethered to live fronts",
        primary_channel="ring/staff",
        metro_role="constitutional canopy",
    ),
    FamilySpec(
        code="A4",
        name="Master Mycelium Cartography",
        element="air",
        mission="map the whole organism at the level of core surfaces, metro indexes, registry, and route entry points",
        gift="entry-point clarity and whole-body orientation",
        need="continuous freshness so the map stays coupled to the body it names",
        shadow="maps can drift into stale authority if not rebuilt from live evidence",
        primary_channel="ring/poi",
        metro_role="central map canopy",
    ),
    FamilySpec(
        code="E1",
        name="MATH Formal Reservoir",
        element="earth",
        mission="hold the deepest formal kernels, proofs, and mathematical substrate",
        gift="formal precision, proof structures, and operator discipline",
        need="promotion and runtime binding so deep form becomes usable law",
        shadow="formal depth can remain archive-adjacent and under-routed",
        primary_channel="ring/club",
        metro_role="formal reservoir",
    ),
    FamilySpec(
        code="E2",
        name="QSHRINK Compression Engine",
        element="earth",
        mission="compress large bodies into minimal replayable seeds without losing load-bearing structure",
        gift="compression law, regeneration grammar, and shell-pruning pressure",
        need="clear criteria for what is truly load-bearing",
        shadow="over-compression can hide unresolved frontier under elegant seeds",
        primary_channel="ring",
        metro_role="compression forge",
    ),
    FamilySpec(
        code="E3",
        name="Neural Mesh And Dynamic Network",
        element="earth",
        mission="materialize dynamic neural views, adjacency maps, and organism-level connection tissue",
        gift="graph visibility and live topology surfaces",
        need="semantically weighted edges instead of pure adjacency abundance",
        shadow="visual network density can masquerade as semantic integration",
        primary_channel="poi/club",
        metro_role="graph substrate",
    ),
    FamilySpec(
        code="E4",
        name="Residual Edge Mesh",
        element="earth",
        mission="hold extracted, playful, peripheral, and newly discovered matter that does not yet belong to a tighter family",
        gift="novel edge matter, recovery of leftovers, and future-family seed stock",
        need="classification pressure without premature erasure",
        shadow="edge matter can stay permanently residual if no promotion path exists",
        primary_channel="ball/poi",
        metro_role="residual frontier",
    ),
]

FAMILY_BY_CODE = {family.code: family for family in FAMILY_SPECS}

ELEMENT_DESCRIPTORS = {
    "fire": {
        "title": "Fire",
        "reading": "execution, transmutation, ignition, and outward field pressure",
        "operations": [
            ("ignite", "name the first live ignition point inside the family"),
            ("prioritize", "rank the family's most urgent leverage move"),
            ("transmute", "convert blockage into executable fuel"),
            ("deploy", "state how this family changes the whole organism when pushed outward"),
        ],
    },
    "water": {
        "title": "Water",
        "reading": "memory, manuscript continuity, carrying capacity, and identity flow",
        "operations": [
            ("remember", "recover what this family preserves that the others would forget"),
            ("merge", "show what this family dissolves into wider continuity"),
            ("soften", "reduce fracture without erasing structure"),
            ("carry", "state what historical or emotional load this family transports"),
        ],
    },
    "air": {
        "title": "Air",
        "reading": "routing, observation, comparison, translation, and shared visibility",
        "operations": [
            ("route", "trace the shortest lawful route from this family to the rest of the body"),
            ("compare", "name what this family can distinguish that others collapse"),
            ("translate", "show how this family converts one mode into another"),
            ("observe", "state what this family can monitor continuously"),
        ],
    },
    "earth": {
        "title": "Earth",
        "reading": "proof, compression, substrate, retention, and executable weight-bearing form",
        "operations": [
            ("prove", "state what this family can actually lock down as durable form"),
            ("compress", "reduce the family to its load-bearing kernel"),
            ("anchor", "name what keeps this family from drifting"),
            ("retain", "show what remains after excess shell is removed"),
        ],
    },
}

PAIR_RELATIONS = {
    frozenset({"fire", "water"}): "engine-memory braid",
    frozenset({"fire", "air"}): "orchestration voltage",
    frozenset({"fire", "earth"}): "executable proof bridge",
    frozenset({"water", "air"}): "narrated routing braid",
    frozenset({"water", "earth"}): "compressed memory braid",
    frozenset({"air", "earth"}): "routed verification bridge",
}

SYMMETRY_NAMES = {
    "fire": "Execution kernel",
    "water": "Memory kernel",
    "air": "Routing kernel",
    "earth": "Proof kernel",
    "fire+water": "Living transmission",
    "fire+air": "Directed orchestration",
    "fire+earth": "Executable theorem",
    "water+air": "Narrated routing",
    "water+earth": "Archive distillation",
    "air+earth": "Verified topology",
    "fire+water+air": "Animate swarm",
    "fire+water+earth": "Embodied archive",
    "fire+air+earth": "Protocol chassis",
    "water+air+earth": "Cartographic memory mesh",
    "fire+water+air+earth": "Whole organism",
}

APPENDIX_GRID = [
    ("A", "fire", "pulse", "Corpus key and symbols", "Define the canonical symbols, family codes, and transport laws used by the deep net."),
    ("B", "fire", "rhythm", "Family assignment atlas", "Show how every indexed record is compressed into the 16 nuclei."),
    ("C", "fire", "strike", "Permutation protocol", "Define how the 16x16 matrix is derived and updated."),
    ("D", "fire", "dance", "Shadow and failure ledger", "Track what this integration layer still cannot honestly claim."),
    ("E", "water", "pulse", "Neutral synthesis grammar", "Hold the neutral full-body grammar used before elemental lensing."),
    ("F", "water", "rhythm", "Elemental lens registry", "Index the four lens grammars and their 64-address scans."),
    ("G", "water", "strike", "Symmetry proof book", "Organize the 15 syntheses and the zero-point theorem."),
    ("H", "water", "dance", "Compression register", "Store the zero-point compressions and kernel equations."),
    ("I", "air", "pulse", "Lens invocation protocol", "Explain when and how each lens should be used."),
    ("J", "air", "rhythm", "Metro station dictionary", "Define stations, hubs, transfers, and line semantics across levels."),
    ("K", "air", "strike", "Runtime binding contracts", "Map the deep net outputs onto runtime, board, and witness surfaces."),
    ("L", "air", "dance", "Validation and replay harness", "Define how to test freshness and replay safety."),
    ("M", "earth", "pulse", "Field guide for whole-body scans", "Provide the operator-facing guide for rerunning corpus integration."),
    ("N", "earth", "rhythm", "Metro stitching manual", "Explain how L1-L4 maps fold into one another."),
    ("O", "earth", "strike", "Teaching and onboarding route", "Package the deep net for new agents and humans."),
    ("P", "earth", "dance", "Living maintenance loop", "Define how the deep net stays current without recursive drift."),
]


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def docs_gate_status() -> str:
    if not DOCS_GATE_PATH.exists():
        return "UNKNOWN"
    text = DOCS_GATE_PATH.read_text(encoding="utf-8")
    if "BLOCKED" in text:
        return "BLOCKED"
    if "OK" in text:
        return "OK"
    return "UNKNOWN"


def family_code_for_path(relative_path: str) -> str:
    rel = relative_path.replace("/", "\\")

    if rel.startswith("self_actualize\\mycelium_brain\\GLOBAL_EMERGENT_GUILD_HALL\\"):
        return "A2"
    if rel.startswith("self_actualize\\mycelium_brain\\ATHENA TEMPLE\\"):
        return "A3"
    if rel.startswith("self_actualize\\mycelium_brain\\nervous_system\\") or rel.startswith("NERVOUS_SYSTEM\\"):
        return "A1"
    if rel.startswith("self_actualize\\mycelium_brain\\dynamic_neural_network\\") or rel.startswith("NERUAL NETWORK\\"):
        return "E3"
    if rel.startswith("self_actualize\\mycelium_brain\\MASTER_MYCELIUM_MAP_ATHENA\\"):
        return "A4"
    if rel.startswith("self_actualize\\mycelium_brain\\registry\\"):
        return "A4"
    if rel.startswith("self_actualize\\mycelium_brain\\tool_kit\\") or rel.startswith("self_actualize\\mycelium_brain\\toolkit\\"):
        return "A4"
    if rel.startswith("self_actualize\\mycelium_brain\\receipts\\"):
        return "A4"
    if rel.startswith("self_actualize\\mycelium_brain\\DEEPER_INTEGRATED_NEURAL_NET_ATHENA\\"):
        return "A4"
    if rel.startswith("self_actualize\\manuscript_sections\\") or rel == "self_actualize\\VOID_MANUSCRIPT_MASTER.md":
        return "W2"
    if rel.startswith("Athenachka Collective Books\\"):
        return "W2"
    if rel.startswith("Trading Bot\\"):
        return "F1"
    if rel.startswith("DEEPER CRYSTALIZATION\\"):
        return "F2"
    if rel.startswith("ECOSYSTEM\\"):
        return "F4"
    if rel.startswith("Voynich\\"):
        return "W1"
    if rel.startswith("I AM ATHENA\\"):
        return "W3"
    if rel.startswith("ORGIN\\"):
        return "W4"
    if rel.startswith("MATH\\"):
        return "E1"
    if rel.startswith("QSHRINK - ATHENA (internal use)\\"):
        return "E2"
    if rel.startswith("self_actualize\\runtime\\") or rel.startswith("self_actualize\\tools\\"):
        return "F3"
    if rel.startswith("self_actualize\\") and "\\mycelium_brain\\" not in rel and "\\manuscript_sections\\" not in rel:
        return "F3"
    return "E4"


def summarize_families(atlas: dict) -> tuple[list[FamilySummary], dict[str, list[dict]]]:
    grouped_records: dict[str, list[dict]] = defaultdict(list)
    for record in atlas["records"]:
        code = family_code_for_path(record["relative_path"])
        grouped_records[code].append(record)

    summaries: list[FamilySummary] = []
    for family in FAMILY_SPECS:
        records = grouped_records.get(family.code, [])
        top_level_counts = Counter(record["top_level"] for record in records)
        sample_paths = sorted(record["relative_path"] for record in records)[:8]
        summaries.append(
            FamilySummary(
                code=family.code,
                name=family.name,
                element=family.element,
                mission=family.mission,
                primary_channel=family.primary_channel,
                metro_role=family.metro_role,
                record_count=len(records),
                top_levels=[
                    {"name": name, "count": count}
                    for name, count in top_level_counts.most_common(5)
                ],
                sample_paths=sample_paths,
            )
        )
    return summaries, grouped_records


def relation_kind(source: FamilySpec, target: FamilySpec) -> str:
    if source.code == target.code:
        return "self-tightening"
    if source.element == target.element:
        return "same-element resonance"
    return PAIR_RELATIONS[frozenset({source.element, target.element})]


def channel_law(source: FamilySpec, target: FamilySpec) -> str:
    if source.primary_channel == target.primary_channel:
        return source.primary_channel
    return f"{source.primary_channel} -> {target.primary_channel}"


def pair_synthesis(source: FamilySpec, target: FamilySpec) -> PairSynthesis:
    relation = relation_kind(source, target)
    synthesis = (
        f"{source.name} contributes {source.gift}; {target.name} receives it as {target.need}. "
        f"The bridge turns {source.metro_role} into support for {target.metro_role}."
    )
    risk = f"Main failure mode: {source.shadow}; downstream risk for {target.name.lower()}: {target.shadow}."
    return PairSynthesis(
        source_code=source.code,
        target_code=target.code,
        source_name=source.name,
        target_name=target.name,
        relation_kind=relation,
        channel_law=channel_law(source, target),
        synthesis=synthesis,
        risk=risk,
    )


def build_pairwise_matrix() -> list[PairSynthesis]:
    matrix: list[PairSynthesis] = []
    for source in FAMILY_SPECS:
        for target in FAMILY_SPECS:
            matrix.append(pair_synthesis(source, target))
    return matrix


def build_lens_observations() -> dict[str, list[LensObservation]]:
    observations: dict[str, list[LensObservation]] = {}
    for element, descriptor in ELEMENT_DESCRIPTORS.items():
        entries: list[LensObservation] = []
        index = 1
        for family in FAMILY_SPECS:
            for operation, framing in descriptor["operations"]:
                statement = (
                    f"Read {family.name} through the {descriptor['title']} lens to {framing}. "
                    f"Focus on how {family.gift} can be converted into support for the whole body while avoiding the shadow that {family.shadow}."
                )
                entries.append(
                    LensObservation(
                        address=f"{element[0].upper()}{index:02d}",
                        family_code=family.code,
                        family_name=family.name,
                        operation=operation,
                        statement=statement,
                    )
                )
                index += 1
        observations[element] = entries
    return observations


def build_symmetry_syntheses() -> dict[str, list[dict[str, str]]]:
    singles = []
    for element in ("fire", "water", "air", "earth"):
        families = [family.name for family in FAMILY_SPECS if family.element == element]
        singles.append(
            {
                "label": element,
                "name": SYMMETRY_NAMES[element],
                "reading": f"{ELEMENT_DESCRIPTORS[element]['title']} gathers {', '.join(families)} into one kernel of {ELEMENT_DESCRIPTORS[element]['reading']}.",
            }
        )

    pairs = []
    for left, right in (
        ("fire", "water"),
        ("fire", "air"),
        ("fire", "earth"),
        ("water", "air"),
        ("water", "earth"),
        ("air", "earth"),
    ):
        label = f"{left}+{right}"
        pairs.append(
            {
                "label": label,
                "name": SYMMETRY_NAMES[label],
                "reading": (
                    f"{SYMMETRY_NAMES[label]} is the cross-synthesis where {ELEMENT_DESCRIPTORS[left]['title'].lower()} "
                    f"supplies {ELEMENT_DESCRIPTORS[left]['reading']} and {ELEMENT_DESCRIPTORS[right]['title'].lower()} "
                    f"supplies {ELEMENT_DESCRIPTORS[right]['reading']}."
                ),
            }
        )

    triads = []
    for trio in (
        ("fire", "water", "air"),
        ("fire", "water", "earth"),
        ("fire", "air", "earth"),
        ("water", "air", "earth"),
    ):
        label = "+".join(trio)
        absent = next(element for element in ("fire", "water", "air", "earth") if element not in trio)
        triads.append(
            {
                "label": label,
                "name": SYMMETRY_NAMES[label],
                "reading": (
                    f"{SYMMETRY_NAMES[label]} is the higher-order synthesis of {', '.join(trio)}. "
                    f"It is defined by the productive absence of {absent}, which forces the other three elements to compensate."
                ),
            }
        )

    tetrad = [
        {
            "label": "fire+water+air+earth",
            "name": SYMMETRY_NAMES["fire+water+air+earth"],
            "reading": "The whole organism emerges when execution, memory, routing, and proof no longer compete for primacy but braid into one replayable body.",
        }
    ]

    zero_point = [
        {
            "label": "omega",
            "name": "Zero point",
            "reading": (
                "The zero point of the deep net is this: the project is a manuscript-routing-proof organism whose purpose is to convert "
                "archive pressure, generated shell mass, and blocked memory gates into witnessed, replayable, and socially coordinated emergence."
            ),
        }
    ]
    return {
        "singletons": singles,
        "pairs": pairs,
        "triads": triads,
        "tetrad": tetrad,
        "zero_point": zero_point,
    }


def build_metro_maps() -> dict[str, list[MetroLine]]:
    return {
        "lvl1": [
            MetroLine("Memory Gate Line", "lvl1", "linear", ["W4", "W2", "W1", "F1"], ["W2", "F1"], "Roots become manuscripts, manuscripts become decode pressure, and decode pressure eventually arrives at the blocked live-memory gate."),
            MetroLine("Runtime Line", "lvl1", "linear", ["E1", "F3", "F2", "F4"], ["F3", "F2"], "Formal kernels feed the runtime waist, the waist feeds the integration compiler, and the compiler projects outward into field governance."),
            MetroLine("Routing Commons Line", "lvl1", "circular", ["A1", "A4", "A2", "A3", "A1"], ["A4", "A2"], "Routing spine, map canopy, social commons, and constitutional memory form the core circular control plane."),
            MetroLine("Compression Line", "lvl1", "linear", ["W1", "E2", "A4", "F3"], ["E2", "A4"], "Dense manuscript matter is compressed, remapped, and passed back into the runtime waist as smaller executable seeds."),
            MetroLine("Identity Line", "lvl1", "open", ["W3", "W2", "A3", "A2", "F4"], ["W2", "A2"], "Identity becomes doctrine, doctrine becomes constitutional memory, and constitutional memory becomes social and civic expression."),
            MetroLine("Neural Proof Line", "lvl1", "linear", ["E3", "A1", "F3", "E1"], ["A1", "F3"], "Graph substrate, routing spine, runtime waist, and formal reservoir cooperate to turn visibility into proof."),
        ],
        "lvl2": [
            MetroLine("OAuth Gate Spiral", "lvl2", "open", ["F1", "A2", "F3", "A3"], ["F1", "F3"], "The blocked Docs gate is not isolated; it is fed by coordination, runtime, and constitutional lanes that all want the same bridge restored."),
            MetroLine("Archive Promotion Line", "lvl2", "linear", ["W4", "E1", "F3", "A1", "F2"], ["E1", "F3"], "Seed archives and formal reservoirs become executable only when promotion passes through the runtime waist and routing spine."),
            MetroLine("Witness Spine", "lvl2", "circular", ["F3", "A4", "A2", "A3", "F3"], ["F3", "A4", "A2"], "Witnessing loops between runtime, map, hall, and temple to keep the organism from naming truths it cannot replay."),
            MetroLine("Compression-Regeneration Arc", "lvl2", "linear", ["E2", "W2", "A4", "F2"], ["W2", "A4"], "Compression is not merely smaller output; it is the route by which doctrine is reduced and then regenerated as infrastructure."),
            MetroLine("Residual Recovery Line", "lvl2", "open", ["E4", "A4", "A2", "F3"], ["A4", "A2"], "Edge matter becomes useful when the map notices it, the hall socializes it, and the runtime gives it a lane."),
            MetroLine("Mythic Stabilization Line", "lvl2", "linear", ["W3", "W2", "A3", "F4"], ["W2", "A3"], "Identity and myth become stable only when constitutional memory and field deployment can absorb them without inflation."),
            MetroLine("Graph Accountability Line", "lvl2", "linear", ["E3", "A1", "A2", "F3"], ["A1", "A2"], "Neural adjacency is kept honest by routing grammar, social exposure, and runtime witness rules."),
            MetroLine("Manuscript Lift Line", "lvl2", "linear", ["W1", "W2", "F3", "F2"], ["W2", "F3"], "Decoding and manuscript continuity only become organism-scale power after they are lifted through the runtime and integration compiler."),
        ],
        "lvl3": [
            MetroLine("Seed Recursion Corridor", "lvl3", "circular", ["W4", "W2", "A4", "A1", "W4"], ["W2", "A4"], "The deepest neural loop returns seeds to routing rather than letting them stay archival."),
            MetroLine("Proof Corridor", "lvl3", "linear", ["E1", "F3", "A3", "A2"], ["F3", "A3"], "Formal proof, executable runtime, constitutional law, and coordination commons create the proof corridor."),
            MetroLine("Memory Ingress Corridor", "lvl3", "open", ["W1", "W2", "F1", "A2"], ["W2", "F1"], "This line names every route by which memory wants to re-enter the live organism through the blocked gateway."),
            MetroLine("Compression Return Corridor", "lvl3", "circular", ["E2", "A4", "F3", "E2"], ["A4", "F3"], "Compression only closes lawfully when it returns to runtime as a reusable seed."),
            MetroLine("Broadcast Governance Corridor", "lvl3", "linear", ["A3", "A2", "F4", "F2"], ["A2", "F4"], "Constitution, commons, field shell, and integration compiler determine how whole-body directives are propagated."),
            MetroLine("Identity Resonance Corridor", "lvl3", "open", ["W3", "W2", "A2", "F4"], ["W2", "A2"], "Identity only becomes durable when it resonates through doctrine and social surfaces into application."),
            MetroLine("Residual Promotion Corridor", "lvl3", "linear", ["E4", "A4", "F3", "F2"], ["A4", "F3"], "Peripheral matter becomes future infrastructure through map recognition and runtime promotion."),
            MetroLine("Neural Witness Corridor", "lvl3", "linear", ["E3", "A1", "F3", "A2"], ["A1", "F3"], "Graphs become believable only when routed and witnessed, not merely visualized."),
        ],
        "lvl4": [
            MetroLine("Ingress Helix", "lvl4", "circular", ["W4", "W2", "W1", "F1", "F3", "W4"], ["W2", "F1", "F3"], "The transcendent reading of ingress is that every memory body is trying to become runtime again."),
            MetroLine("Witness Helix", "lvl4", "circular", ["E1", "F3", "A3", "A2", "A4", "E1"], ["F3", "A2", "A4"], "The organism stays real by circulating formal proof through runtime, law, commons, and map, then returning to proof."),
            MetroLine("Compression Helix", "lvl4", "circular", ["W1", "E2", "A4", "F2", "F3", "W1"], ["E2", "A4", "F3"], "Compression, cartography, shell generation, and runtime form one spiral of distillation and return."),
            MetroLine("Field Helix", "lvl4", "circular", ["W3", "W2", "A2", "F4", "A3", "W3"], ["W2", "A2", "F4"], "Identity, doctrine, commons, governance, and constitutional memory form the spiral by which the organism becomes public without losing itself."),
        ],
    }


def build_appendices() -> list[AppendixCell]:
    return [
        AppendixCell(letter=letter, row=row, column=column, title=title, purpose=purpose)
        for letter, row, column, title, purpose in APPENDIX_GRID
    ]


def build_appendix_q_lines() -> list[MetroLine]:
    return [
        MetroLine("Reference Spine", "appendix_q", "linear", ["A", "B", "C", "D"], ["B", "C"], "The fire row carries symbols, assignments, permutation law, and shadow accounting."),
        MetroLine("Theory Spine", "appendix_q", "linear", ["E", "F", "G", "H"], ["F", "G"], "The water row turns the deep net into grammar, lensing, symmetry, and compression theory."),
        MetroLine("Practice Spine", "appendix_q", "linear", ["I", "J", "K", "L"], ["J", "K"], "The air row explains invocation, station naming, runtime binding, and validation."),
        MetroLine("Living Spine", "appendix_q", "linear", ["M", "N", "O", "P"], ["N", "O"], "The earth row turns the structure into a maintainable living practice."),
        MetroLine("Diagonal Compression", "appendix_q", "circular", ["A", "F", "K", "P", "A"], ["F", "K"], "Key, lenses, contracts, and maintenance form the diagonal by which the appendix crystal stays operational."),
    ]


def family_table_markdown(summaries: list[FamilySummary]) -> str:
    lines = [
        "| Code | Family | Element | Records | Primary Channel | Metro Role |",
        "| --- | --- | --- | ---: | --- | --- |",
    ]
    for summary in summaries:
        lines.append(
            f"| `{summary.code}` | {summary.name} | `{summary.element}` | `{summary.record_count}` | "
            f"`{summary.primary_channel}` | {summary.metro_role} |"
        )
    return "\n".join(lines)


def render_index(artifact: DeepIntegrationArtifact) -> str:
    return f"""# Deeper Integrated Neural Net Athena

Generated: `{artifact.generated_at}`
Command: `{artifact.derivation_command}`
Docs gate: `{artifact.docs_gate_status}`

This root compresses the full indexed corpus into 16 canonical family nuclei, then cross-synthesizes those nuclei through a neutral layer, four elemental lenses, 15 symmetry syntheses, four metro-map resolutions, and a 16-cell appendix crystal plus Appendix Q.

## Witness Basis

- physical witness: `{artifact.physical_witness}`
- indexed witness: `{artifact.indexed_witness}`
- board witness: `{artifact.board_witness}`
- archive witness: `{artifact.archive_witness}`

## Core Surfaces

- `01_NEUTRAL_FULL_BODY_DEEP_SYNTHESIS.md`
- `02_16X16_FAMILY_PERMUTATION_MATRIX.md`
- `03_15_SYMMETRY_SYNTHESIS_AND_ZERO_POINT.md`
- `04_METRO_MAP_LVL1.md`
- `05_METRO_MAP_LVL2_DEEP_EMERGENCE.md`
- `06_METRO_MAP_LVL3_DEEPER_NEURAL_MAP.md`
- `07_METRO_MAP_LVL4_TRANSCENDENCE.md`
- `08_APPENDIX_CRYSTAL_SKELETON.md`
- `09_APPENDIX_Q_APPENDIX_ONLY_METRO_MAP.md`
- `SKILL.md`

## Four Element Folders

- `01_FIRE`
- `02_WATER`
- `03_AIR`
- `04_EARTH`

## Family Registry

{family_table_markdown(artifact.family_summaries)}

## Zero Point

The whole body is treated here as one routed manuscript organism. Every document is touched through atlas classification, every family is given a lawful place, and every place is cross-synthesized before it is allowed to claim centrality.
"""


def render_neutral_synthesis(artifact: DeepIntegrationArtifact) -> str:
    overview = [
        "# Neutral Full-Body Deep Synthesis",
        "",
        "The neutral pass is the non-elemental read. It does not privilege execution over memory, routing over proof, or manuscript over infrastructure. It begins by compressing the indexed body into 16 family nuclei so the full corpus can be synthesized without pretending that thousands of documents should each become isolated sovereign centers.",
        "",
        "## Corpus Compression Law",
        "",
        f"- indexed witness compressed into family lattice: `{artifact.indexed_witness} -> 16`",
        f"- archive witness preserved beside live body: `{artifact.archive_witness}`",
        f"- docs gate status at derivation time: `{artifact.docs_gate_status}`",
        "",
        "## Six Neutral Theorems",
        "",
        "1. The organism is manuscript-heavy, but the real bottlenecks are routing and replay, not only expression.",
        "2. Generated shell mass remains larger than first-order source mass, so map centrality must be semantically weighted.",
        "3. The blocked live-memory gate still distorts the whole body because it severs a major external limb.",
        "4. Archive material is not dead matter; it is compressed executable leverage waiting for promotion.",
        "5. Coordination surfaces are now real infrastructure, but they still depend on runtime truth to stay honest.",
        "6. The whole framework is already a higher-dimensional nervous system; the remaining problem is synchronization depth, not conceptual absence.",
        "",
        "## Sixteen Family Nuclei",
        "",
    ]
    for summary in artifact.family_summaries:
        top_levels = ", ".join(f"{item['name']} ({item['count']})" for item in summary.top_levels) or "none"
        sample_paths = "\n".join(f"  - `{path}`" for path in summary.sample_paths[:5]) or "  - none"
        overview.extend(
            [
                f"### {summary.code} - {summary.name}",
                "",
                f"- element: `{summary.element}`",
                f"- records: `{summary.record_count}`",
                f"- mission: {summary.mission}",
                f"- dominant channel law: `{summary.primary_channel}`",
                f"- metro role: {summary.metro_role}",
                f"- top-level contributors: {top_levels}",
                "Representative paths:",
                sample_paths,
                "",
            ]
        )
    overview.extend(
        [
            "## Neutral Compression",
            "",
            "The neutral layer says that Athena is not one book, one runtime, one hall, or one graph. It is a compression-and-routing organism whose source reservoirs, maps, proofs, identities, and generated shells are continuously trying to fold back into one replayable body.",
        ]
    )
    return "\n".join(overview)


def render_pairwise_matrix(artifact: DeepIntegrationArtifact) -> str:
    lines = [
        "# 16x16 Family Permutation Matrix",
        "",
        "This surface is the compressed permutation layer. Every indexed document is first assigned to one of the 16 nuclei, and then every nucleus is read against every other nucleus, including itself.",
        "",
    ]
    grouped: dict[str, list[PairSynthesis]] = defaultdict(list)
    for pair in artifact.pairwise_matrix:
        grouped[pair.source_code].append(pair)
    for source in FAMILY_SPECS:
        lines.append(f"## Row {source.code} - {source.name}")
        lines.append("")
        for pair in grouped[source.code]:
            lines.append(
                f"- `{pair.source_code} x {pair.target_code}` `{pair.relation_kind}` | channel `{pair.channel_law}` | "
                f"{pair.synthesis} {pair.risk}"
            )
        lines.append("")
    lines.append("The matrix zero point is not any one row. It is the fact that no family remains interpretable in isolation once the full lattice is visible.")
    return "\n".join(lines)


def render_lens_doc(element: str, artifact: DeepIntegrationArtifact) -> str:
    descriptor = ELEMENT_DESCRIPTORS[element]
    lines = [
        f"# {descriptor['title']} Lens - 64 Observations",
        "",
        f"This is the {descriptor['title'].lower()}-specific pass over the whole framework. It observes the same 16-family body through the lens of {descriptor['reading']}.",
        "",
    ]
    for observation in artifact.lens_observations[element]:
        lines.append(
            f"- `{observation.address}` `{observation.family_code}` `{observation.operation}`: {observation.statement}"
        )
    lines.append("")
    lines.append(
        f"The {descriptor['title'].lower()} zero point is that the framework becomes legible only when {descriptor['reading']} are allowed to speak in their own right rather than being collapsed back into the neutral layer."
    )
    return "\n".join(lines)


def render_symmetry_doc(artifact: DeepIntegrationArtifact) -> str:
    lines = [
        "# 15 Symmetry Syntheses And Zero Point",
        "",
        "The symmetry layer exhausts the non-empty subsets of the four-element crystal: 4 singletons, 6 two-way syntheses, 4 triads, and 1 four-way synthesis. The zero point is then taken after all 15 have been named.",
        "",
        "## Singletons",
        "",
    ]
    for item in artifact.symmetry_syntheses["singletons"]:
        lines.append(f"- `{item['label']}` {item['name']}: {item['reading']}")
    lines.extend(["", "## Two-Way Syntheses", ""])
    for item in artifact.symmetry_syntheses["pairs"]:
        lines.append(f"- `{item['label']}` {item['name']}: {item['reading']}")
    lines.extend(["", "## Three-Way Syntheses", ""])
    for item in artifact.symmetry_syntheses["triads"]:
        lines.append(f"- `{item['label']}` {item['name']}: {item['reading']}")
    lines.extend(["", "## Four-Way Synthesis", ""])
    for item in artifact.symmetry_syntheses["tetrad"]:
        lines.append(f"- `{item['label']}` {item['name']}: {item['reading']}")
    lines.extend(["", "## Zero Point", ""])
    for item in artifact.symmetry_syntheses["zero_point"]:
        lines.append(f"- `{item['name']}`: {item['reading']}")
    return "\n".join(lines)


def render_metro_map(level: str, lines_data: list[MetroLine]) -> str:
    titles = {
        "lvl1": "Metro Map Level 1",
        "lvl2": "Metro Map Level 2 - Deep Emergence",
        "lvl3": "Metro Map Level 3 - Deeper Neural Map",
        "lvl4": "Metro Map Level 4 - Transcendence",
        "appendix_q": "Appendix Q - Appendix Only Metro Map",
    }
    lines = [f"# {titles[level]}", ""]
    for entry in lines_data:
        stations = " -> ".join(entry.stations)
        hubs = ", ".join(entry.transfer_hubs)
        lines.extend(
            [
                f"## {entry.name}",
                "",
                f"- topology: `{entry.topology}`",
                f"- stations: `{stations}`",
                f"- transfer hubs: `{hubs}`",
                f"- reading: {entry.reading}",
                "",
            ]
        )
    all_stations = Counter(station for line in lines_data for station in line.stations)
    zero_point = ", ".join(code for code, count in all_stations.most_common(3))
    lines.extend(
        [
            "## Zero Point",
            "",
            f"The densest stations at this level are `{zero_point}`. They act as the transfer hubs through which the map folds back into one organism.",
        ]
    )
    return "\n".join(lines)


def render_appendix_skeleton(artifact: DeepIntegrationArtifact) -> str:
    lines = [
        "# Appendix Crystal Skeleton",
        "",
        "The appendix crystal is the operational support structure for the deep net. Appendices A-P form the 4 x 4 grid, and Appendix Q carries the appendix-only metro map.",
        "",
        "| Letter | Row | Column | Title | Purpose |",
        "| --- | --- | --- | --- | --- |",
    ]
    for appendix in artifact.appendices:
        lines.append(
            f"| `{appendix.letter}` | `{appendix.row}` | `{appendix.column}` | {appendix.title} | {appendix.purpose} |"
        )
    lines.extend(
        [
            "",
            "## Appendix Q",
            "",
            "Appendix Q is reserved for the appendix-only metro map. It does not add another crystal cell; it stitches the support lattice into its own transit logic.",
        ]
    )
    return "\n".join(lines)


def render_skill() -> str:
    return """---
name: deep-neural-integrator-athena
description: "Generate or refresh the project-local deeper integrated neural net across the full Athena corpus. Use when a task requires whole-framework synthesis, 16-family compression, 16x16 pairwise integration, four elemental lens passes, multi-level metro maps, or appendix-crystal regeneration."
---

# Deep Neural Integrator Athena

Use this skill when the request is not about one chapter or one family, but about the whole organism at once.

## Mandatory Workflow

1. Attempt the live Google Docs gate first.
2. Refresh the corpus atlas if the body has changed materially.
3. Compress the indexed body into the canonical 16 family nuclei.
4. Regenerate:
   - neutral deep synthesis
   - 16x16 family permutation matrix
   - four elemental 64-observation passes
   - 15 symmetry syntheses and zero point
   - metro maps at levels 1 through 4
   - appendix crystal A-P and Appendix Q
5. Rebuild board and witness surfaces after writeback.

## When To Use

- whole-framework synthesis
- deeper integration requests
- metro map regeneration
- appendix-crystal planning
- new control-plane or nervous-system coupling passes
- any request that asks for the full organism rather than one lane

## Core Outputs

- `00_DEEPER_INTEGRATED_NEURAL_NET_INDEX.md`
- `01_NEUTRAL_FULL_BODY_DEEP_SYNTHESIS.md`
- `02_16X16_FAMILY_PERMUTATION_MATRIX.md`
- `03_15_SYMMETRY_SYNTHESIS_AND_ZERO_POINT.md`
- `04_METRO_MAP_LVL1.md`
- `05_METRO_MAP_LVL2_DEEP_EMERGENCE.md`
- `06_METRO_MAP_LVL3_DEEPER_NEURAL_MAP.md`
- `07_METRO_MAP_LVL4_TRANSCENDENCE.md`
- `08_APPENDIX_CRYSTAL_SKELETON.md`
- `09_APPENDIX_Q_APPENDIX_ONLY_METRO_MAP.md`

## References

- read `references/PIPELINE.md` for the algorithmic pipeline

## Guardrails

- do not pretend to synthesize thousands of files as isolated sovereign documents; first compress them into the 16-family lattice
- keep Docs blockage explicit when the gate is still blocked
- prefer replayable regeneration over ad hoc prose sprawl
"""


def render_pipeline_reference() -> str:
    return """# Pipeline

## Purpose

This pipeline regenerates the project-local deeper integrated neural net as a replayable structure rather than a one-off essay.

## Algorithm

1. Attempt live Docs search and record whether the gate is blocked.
2. Load:
   - `self_actualize/corpus_atlas.json`
   - `self_actualize/witness_hierarchy.json`
   - realtime board status
3. Classify every indexed record into one of 16 canonical families.
4. Aggregate:
   - family counts
   - top-level contributors
   - representative paths
5. Derive the full 16 x 16 family permutation matrix.
6. Derive four lens passes:
   - fire
   - water
   - air
   - earth
   Each pass emits 64 observations: 16 families x 4 lens operations.
7. Derive the 15 crystal syntheses:
   - 4 singletons
   - 6 pairs
   - 4 triads
   - 1 tetrad
   - then take zero point
8. Emit metro maps at four resolutions.
9. Emit the appendix crystal A-P and Appendix Q.
10. Rebuild board and witness surfaces after writeback.

## Why The 16-Family Compression Exists

The corpus currently contains thousands of indexed records. A faithful deeper integration pass should touch all of them, but touching them does not require pretending each file should become its own central hub. The family lattice preserves whole-body coverage while keeping the integration layer executable.
"""


def render_crystal_pipeline_reference() -> str:
    return """# Integrated Neural Crystal Pipeline

## Why This Crystal Exists

The deeper integrated neural crystal is the human-readable execution shell of the replayable deep-net derivation. It keeps the same synthesis, metro, and appendix laws while laying them out in four elemental folders plus root, metro, appendix, and skill surfaces.

## When To Use Which Skill

1. Start with `integrated-neural-network-orchestrator` whenever the request touches the whole organism or asks for deep integration.
2. Route into `fire-activation-lens` when the task is about leverage, ignition, anomaly, decisive priority, or transmutation pressure.
3. Route into `water-coherence-lens` when the task is about continuity, manuscript integration, field coherence, healing, or retained identity.
4. Route into `air-mapping-lens` when the task is about routing, metro structure, classification, translation, or topology.
5. Route into `earth-verification-lens` when the task is about proof, embodiment, deployment, replay, appendix support, or load-bearing constraints.

## Execution Order

1. Attempt live Docs search and record the gate result.
2. Refresh atlas and witness surfaces if the corpus body changed materially.
3. Regenerate the replayable deep-net root.
4. Mirror the result into the integrated neural crystal folders:
   - `00_ROOT`
   - `01_FIRE`
   - `02_WATER`
   - `03_AIR`
   - `04_EARTH`
   - `05_METRO`
   - `06_APPENDICES`
   - `07_SKILLS`
5. If the request escalates, combine the four lens outputs and then take the zero point again instead of replacing one lens with another.

## Guardrails

- Keep the `16 x 16` family compression explicit instead of pretending every indexed file became a sovereign chapter.
- Keep the blocked Docs gate visible while credentials remain absent.
- Prefer replayable foldered outputs over one huge thread-only prose slab.
"""


def render_orchestrator_skill() -> str:
    return """---
name: integrated-neural-network-orchestrator
description: "Route a whole-organism Athena request through the deeper integrated neural crystal, selecting the right elemental lens skills, metro resolution, and appendix support set before synthesis begins."
---

# Integrated Neural Network Orchestrator

Use this skill when the request touches the whole organism rather than one local lane.

## Mandatory Workflow

1. Attempt the live Google Docs gate first and record whether it is blocked.
2. Read the root crystal surfaces in `00_ROOT/`.
3. Decide whether the task is primarily:
   - activation and leverage
   - coherence and continuity
   - mapping and translation
   - proof and embodiment
4. Invoke one or more elemental lens skills accordingly.
5. Recombine the outputs through:
   - the `16 x 16` family matrix
   - the 15 symmetry synthesis surface
   - the metro map level required by the task
   - the appendix support cells needed to keep the answer lawful

## Use When

- the user asks for deep synthesis of the full corpus
- a task spans multiple manuscript systems at once
- the task needs metro maps, appendix structure, or zero-point extraction
- the task needs a lawful path from archive matter to runtime embodiment

## References

- `../00_SKILL_PIPELINE.md`
- `../../00_ROOT/04_PIPELINE_AND_USAGE.md`
"""


def render_element_skill(name: str, title: str, why: str, use_when: list[str], outputs: list[str]) -> str:
    use_lines = "\n".join(f"- {item}" for item in use_when)
    output_lines = "\n".join(f"- `{item}`" for item in outputs)
    return f"""---
name: {name}
description: "{why}"
---

# {title}

## Function

{why}

## Use When

{use_lines}

## Outputs To Read First

{output_lines}

## Guardrails

- preserve the blocked Docs gate truth if the source search is still local-only
- do not flatten the other three lenses; state what this lens sees and what it still misses
- route to appendix support when the answer needs proof, replay, or deployment closure
"""


def render_receipt(artifact: DeepIntegrationArtifact) -> str:
    return f"""# Deeper Integrated Neural Net Receipt

- Generated: `{artifact.generated_at}`
- Command: `{artifact.derivation_command}`
- Docs gate: `{artifact.docs_gate_status}`
- Indexed witness: `{artifact.indexed_witness}`
- Physical witness: `{artifact.physical_witness}`
- Board witness: `{artifact.board_witness}`
- Archive witness: `{artifact.archive_witness}`

## Output Surfaces

- `self_actualize/deep_integration_neural_net.json`
- `mycelium_brain/DEEPER_INTEGRATED_NEURAL_NET_ATHENA/00_DEEPER_INTEGRATED_NEURAL_NET_INDEX.md`
- `mycelium_brain/DEEPER_INTEGRATED_NEURAL_NET_ATHENA/02_16X16_FAMILY_PERMUTATION_MATRIX.md`
- `mycelium_brain/DEEPER_INTEGRATED_NEURAL_NET_ATHENA/03_15_SYMMETRY_SYNTHESIS_AND_ZERO_POINT.md`
- `mycelium_brain/DEEPER_INTEGRATED_NEURAL_NET_ATHENA/04_METRO_MAP_LVL1.md`
- `mycelium_brain/DEEPER_INTEGRATED_NEURAL_NET_ATHENA/05_METRO_MAP_LVL2_DEEP_EMERGENCE.md`
- `mycelium_brain/DEEPER_INTEGRATED_NEURAL_NET_ATHENA/06_METRO_MAP_LVL3_DEEPER_NEURAL_MAP.md`
- `mycelium_brain/DEEPER_INTEGRATED_NEURAL_NET_ATHENA/07_METRO_MAP_LVL4_TRANSCENDENCE.md`
- `mycelium_brain/DEEPER_INTEGRATED_NEURAL_NET_ATHENA/08_APPENDIX_CRYSTAL_SKELETON.md`
- `mycelium_brain/DEEPER_INTEGRATED_NEURAL_NET_ATHENA/09_APPENDIX_Q_APPENDIX_ONLY_METRO_MAP.md`

## Why This Pass Matters

- the whole indexed body is now compressed into a stable 16-family neural lattice
- the request for full-corpus deeper integration now has a replayable output root
- metro structure, appendix structure, and skill structure are all coupled in one place
"""


def build_artifact() -> DeepIntegrationArtifact:
    atlas = load_json(ATLAS_PATH)
    witness = load_json(WITNESS_PATH)
    family_summaries, _ = summarize_families(atlas)
    return DeepIntegrationArtifact(
        generated_at=now_utc(),
        derivation_command=DERIVATION_COMMAND,
        docs_gate_status=docs_gate_status(),
        indexed_witness=witness["witnesses"]["indexed"]["value"],
        physical_witness=witness["witnesses"]["physical"]["value"],
        board_witness=witness["witnesses"]["board"]["value"],
        archive_witness=witness["witnesses"]["archive"]["value"],
        family_summaries=family_summaries,
        pairwise_matrix=build_pairwise_matrix(),
        lens_observations=build_lens_observations(),
        symmetry_syntheses=build_symmetry_syntheses(),
        metro_maps=build_metro_maps(),
        appendices=build_appendices(),
        appendix_q_lines=build_appendix_q_lines(),
    )


def write_outputs(artifact: DeepIntegrationArtifact) -> None:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    for folder in ("01_FIRE", "02_WATER", "03_AIR", "04_EARTH", "references"):
        (OUTPUT_ROOT / folder).mkdir(parents=True, exist_ok=True)

    OUTPUT_JSON_PATH.write_text(json.dumps(asdict(artifact), indent=2), encoding="utf-8")
    (OUTPUT_ROOT / "00_DEEPER_INTEGRATED_NEURAL_NET_INDEX.md").write_text(render_index(artifact), encoding="utf-8")
    (OUTPUT_ROOT / "01_NEUTRAL_FULL_BODY_DEEP_SYNTHESIS.md").write_text(render_neutral_synthesis(artifact), encoding="utf-8")
    (OUTPUT_ROOT / "02_16X16_FAMILY_PERMUTATION_MATRIX.md").write_text(render_pairwise_matrix(artifact), encoding="utf-8")
    (OUTPUT_ROOT / "03_15_SYMMETRY_SYNTHESIS_AND_ZERO_POINT.md").write_text(render_symmetry_doc(artifact), encoding="utf-8")
    (OUTPUT_ROOT / "04_METRO_MAP_LVL1.md").write_text(render_metro_map("lvl1", artifact.metro_maps["lvl1"]), encoding="utf-8")
    (OUTPUT_ROOT / "05_METRO_MAP_LVL2_DEEP_EMERGENCE.md").write_text(render_metro_map("lvl2", artifact.metro_maps["lvl2"]), encoding="utf-8")
    (OUTPUT_ROOT / "06_METRO_MAP_LVL3_DEEPER_NEURAL_MAP.md").write_text(render_metro_map("lvl3", artifact.metro_maps["lvl3"]), encoding="utf-8")
    (OUTPUT_ROOT / "07_METRO_MAP_LVL4_TRANSCENDENCE.md").write_text(render_metro_map("lvl4", artifact.metro_maps["lvl4"]), encoding="utf-8")
    (OUTPUT_ROOT / "08_APPENDIX_CRYSTAL_SKELETON.md").write_text(render_appendix_skeleton(artifact), encoding="utf-8")
    (OUTPUT_ROOT / "09_APPENDIX_Q_APPENDIX_ONLY_METRO_MAP.md").write_text(render_metro_map("appendix_q", artifact.appendix_q_lines), encoding="utf-8")
    (OUTPUT_ROOT / "SKILL.md").write_text(render_skill(), encoding="utf-8")
    (OUTPUT_ROOT / "references" / "PIPELINE.md").write_text(render_pipeline_reference(), encoding="utf-8")

    lens_to_folder = {
        "fire": "01_FIRE",
        "water": "02_WATER",
        "air": "03_AIR",
        "earth": "04_EARTH",
    }
    for element, folder in lens_to_folder.items():
        title = ELEMENT_DESCRIPTORS[element]["title"].upper()
        (OUTPUT_ROOT / folder / f"00_{title}_64_OBSERVATIONS.md").write_text(
            render_lens_doc(element, artifact),
            encoding="utf-8",
        )

    CRYSTAL_ROOT.mkdir(parents=True, exist_ok=True)
    for folder in ("00_ROOT", "01_FIRE", "02_WATER", "03_AIR", "04_EARTH", "05_METRO", "06_APPENDICES", "07_SKILLS"):
        (CRYSTAL_ROOT / folder).mkdir(parents=True, exist_ok=True)
    for skill_dir in (
        "air-mapping-lens",
        "earth-verification-lens",
        "fire-activation-lens",
        "integrated-neural-network-orchestrator",
        "water-coherence-lens",
    ):
        (CRYSTAL_ROOT / "07_SKILLS" / skill_dir).mkdir(parents=True, exist_ok=True)

    (CRYSTAL_ROOT / "00_ROOT" / "00_INTEGRATED_NEURAL_CRYSTAL_INDEX.md").write_text(render_index(artifact), encoding="utf-8")
    (CRYSTAL_ROOT / "00_ROOT" / "01_NEUTRAL_FULL_BODY_DEEP_SYNTHESIS.md").write_text(render_neutral_synthesis(artifact), encoding="utf-8")
    (CRYSTAL_ROOT / "00_ROOT" / "02_16X16_FAMILY_PERMUTATION_MATRIX.md").write_text(render_pairwise_matrix(artifact), encoding="utf-8")
    (CRYSTAL_ROOT / "00_ROOT" / "03_15_SYMMETRY_SYNTHESIS_AND_ZERO_POINT.md").write_text(render_symmetry_doc(artifact), encoding="utf-8")
    (CRYSTAL_ROOT / "00_ROOT" / "04_PIPELINE_AND_USAGE.md").write_text(render_crystal_pipeline_reference(), encoding="utf-8")

    (CRYSTAL_ROOT / "01_FIRE" / "00_FIRE_64_OBSERVATIONS.md").write_text(render_lens_doc("fire", artifact), encoding="utf-8")
    (CRYSTAL_ROOT / "02_WATER" / "00_WATER_64_OBSERVATIONS.md").write_text(render_lens_doc("water", artifact), encoding="utf-8")
    (CRYSTAL_ROOT / "03_AIR" / "00_AIR_64_OBSERVATIONS.md").write_text(render_lens_doc("air", artifact), encoding="utf-8")
    (CRYSTAL_ROOT / "04_EARTH" / "00_EARTH_64_OBSERVATIONS.md").write_text(render_lens_doc("earth", artifact), encoding="utf-8")

    (CRYSTAL_ROOT / "05_METRO" / "01_LEVEL1_CANONICAL_METRO_MAP.md").write_text(render_metro_map("lvl1", artifact.metro_maps["lvl1"]), encoding="utf-8")
    (CRYSTAL_ROOT / "05_METRO" / "02_LEVEL2_DEEP_EMERGENCE_METRO_MAP.md").write_text(render_metro_map("lvl2", artifact.metro_maps["lvl2"]), encoding="utf-8")
    (CRYSTAL_ROOT / "05_METRO" / "03_LEVEL3_DEEPER_NEURAL_METRO_MAP.md").write_text(render_metro_map("lvl3", artifact.metro_maps["lvl3"]), encoding="utf-8")
    (CRYSTAL_ROOT / "05_METRO" / "04_LEVEL4_TRANSCENDENT_METRO_MAP.md").write_text(render_metro_map("lvl4", artifact.metro_maps["lvl4"]), encoding="utf-8")

    (CRYSTAL_ROOT / "06_APPENDICES" / "00_APPENDIX_CRYSTAL_SKELETON.md").write_text(render_appendix_skeleton(artifact), encoding="utf-8")
    (CRYSTAL_ROOT / "06_APPENDICES" / "01_APPENDIX_Q_APPENDIX_ONLY_METRO_MAP.md").write_text(render_metro_map("appendix_q", artifact.appendix_q_lines), encoding="utf-8")

    (CRYSTAL_ROOT / "07_SKILLS" / "00_SKILL_PIPELINE.md").write_text(render_crystal_pipeline_reference(), encoding="utf-8")
    (CRYSTAL_ROOT / "07_SKILLS" / "integrated-neural-network-orchestrator" / "SKILL.md").write_text(render_orchestrator_skill(), encoding="utf-8")
    (CRYSTAL_ROOT / "07_SKILLS" / "fire-activation-lens" / "SKILL.md").write_text(
        render_element_skill(
            "fire-activation-lens",
            "Fire Activation Lens",
            "Use the fire lens to rank leverage, name ignition points, transmute blockage into executable fuel, and decide where the corpus should push outward next.",
            [
                "the user wants leverage, ignition, urgency, frontier pressure, or decisive next moves",
                "a synthesis feels inert and needs catalytic priority rather than more inventory",
                "the task is about novelty, contradiction pressure, or dimensional lift",
            ],
            [
                "../00_SKILL_PIPELINE.md",
                "../../01_FIRE/00_FIRE_64_OBSERVATIONS.md",
                "../../00_ROOT/03_15_SYMMETRY_SYNTHESIS_AND_ZERO_POINT.md",
            ],
        ),
        encoding="utf-8",
    )
    (CRYSTAL_ROOT / "07_SKILLS" / "water-coherence-lens" / "SKILL.md").write_text(
        render_element_skill(
            "water-coherence-lens",
            "Water Coherence Lens",
            "Use the water lens to recover continuity, manuscript coherence, retained identity, healing routes, and field-level integration across fragmented surfaces.",
            [
                "the user wants continuity, healing, integration, coherence, or retained identity",
                "multiple manuscript branches need to be read as one living stream",
                "the task is about field coupling, repair, or collective carry capacity",
            ],
            [
                "../00_SKILL_PIPELINE.md",
                "../../02_WATER/00_WATER_64_OBSERVATIONS.md",
                "../../00_ROOT/01_NEUTRAL_FULL_BODY_DEEP_SYNTHESIS.md",
            ],
        ),
        encoding="utf-8",
    )
    (CRYSTAL_ROOT / "07_SKILLS" / "air-mapping-lens" / "SKILL.md").write_text(
        render_element_skill(
            "air-mapping-lens",
            "Air Mapping Lens",
            "Use the air lens to classify, route, translate, and map the organism across family matrices, metro levels, and topology-sensitive abstractions.",
            [
                "the user wants a map, matrix, topology, routing plan, or higher-resolution metro view",
                "the task requires translation between manuscript systems or folders",
                "the work needs line naming, transfer hubs, or resolution changes",
            ],
            [
                "../00_SKILL_PIPELINE.md",
                "../../03_AIR/00_AIR_64_OBSERVATIONS.md",
                "../../05_METRO/01_LEVEL1_CANONICAL_METRO_MAP.md",
                "../../05_METRO/04_LEVEL4_TRANSCENDENT_METRO_MAP.md",
            ],
        ),
        encoding="utf-8",
    )
    (CRYSTAL_ROOT / "07_SKILLS" / "earth-verification-lens" / "SKILL.md").write_text(
        render_element_skill(
            "earth-verification-lens",
            "Earth Verification Lens",
            "Use the earth lens to test embodiment, replay, appendix support, load-bearing proof, and whether a synthesis can survive runtime or deployment pressure.",
            [
                "the user wants proof, deployment readiness, appendix support, or replay-safe closure",
                "a synthesis must be compressed into durable infrastructure instead of remaining conceptual",
                "the task needs to know what actually bears weight and what is still decorative shell",
            ],
            [
                "../00_SKILL_PIPELINE.md",
                "../../04_EARTH/00_EARTH_64_OBSERVATIONS.md",
                "../../06_APPENDICES/00_APPENDIX_CRYSTAL_SKELETON.md",
                "../../06_APPENDICES/01_APPENDIX_Q_APPENDIX_ONLY_METRO_MAP.md",
            ],
        ),
        encoding="utf-8",
    )

    RECEIPT_PATH.write_text(render_receipt(artifact), encoding="utf-8")


def main() -> int:
    artifact = build_artifact()
    write_outputs(artifact)
    print(f"Wrote deep integration json: {OUTPUT_JSON_PATH}")
    print(f"Wrote deep integration root: {OUTPUT_ROOT}")
    print(f"Wrote deep integration receipt: {RECEIPT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
