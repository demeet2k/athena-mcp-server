from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path

ROOT = Path(r"C:\Users\dmitr\Documents\Athena Agent")
MANIFEST_PATH = ROOT / "self_actualize" / "mycelium_brain" / "dynamic_neural_network" / "NETWORK_MANIFEST.json"
OUTPUT_ROOT = ROOT / "self_actualize" / "mycelium_brain" / "dynamic_neural_network" / "14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK"
LIVE_DEEP_ROOT = OUTPUT_ROOT
HISTORICAL_DEEP_MIRRORS = [
    ROOT / "self_actualize" / "mycelium_brain" / "DEEPER_INTEGRATED_NEURAL_NETWORK",
    ROOT / "self_actualize" / "mycelium_brain" / "DEEPER_INTEGRATED_NEURAL_NET_ATHENA",
]
ORGANISM_LAW = "Theta_plus = (AddressMesh, RelationMetro, ChamberMembrane, ReplayReturnAxis; EconomySalienceBudget)"


@dataclass(frozen=True)
class BasisDoc:
    idx: int
    slug: str
    title: str
    element: str
    cluster: str
    role: str
    source_hint: str
    hubs: tuple[str, ...]


LOOPS = [
    ("CorpusMap", "maps the whole corpus as one routed body"),
    ("OntologyLattice", "turns recurring themes into stable function classes"),
    ("ResidualPressure", "mines contradiction, ambiguity, and unresolved pressure"),
    ("BridgeMiner", "discovers lawful routes between isolated zones"),
    ("OperatorExtraction", "extracts transforms and executable operators"),
    ("RepresentationTheory", "decides how truths should be carried"),
    ("RegistrySchemas", "stabilizes outputs into reusable contracts"),
    ("VerifierReplay", "checks proof density and replay closure"),
    ("MetaProcess", "observes the process that is observing"),
    ("JourneyGrowth", "tracks how the Orchestrator changes with the corpus"),
    ("PathologyLab", "profiles failure, drift, winter, and corruption modes"),
    ("PruneOptimizer", "removes non-load-bearing bloat"),
    ("CrossDomainTransfer", "tests which laws survive translation"),
    ("NovelGenerator", "births new coordinates and new operators"),
    ("Distillation", "compresses bodies into portable seeds"),
    ("DimensionLift", "converts closure into a stronger next-layer seed"),
]

ELEMENT_INTROS = {
    "Fire": "Fire reads the network as ignition, decision, risk concentration, and decisive transformation.",
    "Water": "Water reads the network as circulation, adaptation, thaw, and field coherence.",
    "Air": "Air reads the network as relation, topology, dependency, and abstraction.",
    "Earth": "Earth reads the network as embodiment, practice, durability, and lived load-bearing form.",
}

ELEMENT_PATHS = {
    "Fire": OUTPUT_ROOT / "01_FIRE",
    "Water": OUTPUT_ROOT / "02_WATER",
    "Air": OUTPUT_ROOT / "03_AIR",
    "Earth": OUTPUT_ROOT / "04_EARTH",
}

APPENDIX_GRID = [
    ("A", "Square", "Deep", "Addressing and grammars", "Turns local insight into globally legible coordinates."),
    ("B", "Square", "Map", "Canon laws and forms", "Holds invariants and legal moves."),
    ("C", "Square", "Commit", "Kernel pack and mixing", "Executes discrete schedules and transforms."),
    ("D", "Square", "Adapt", "Registry and policies", "Stabilizes identity and version surfaces."),
    ("E", "Flower", "Deep", "Circle gear and clock", "Controls timing, rhythm, and beat alignment."),
    ("F", "Flower", "Map", "Transport and duality", "Carries lawful translation and conjugate transport."),
    ("G", "Flower", "Commit", "Triangle control", "Governs triadic legality and recursion entry."),
    ("H", "Flower", "Adapt", "Coupling and topology", "Constrains friction, dependency, and contact yield."),
    ("I", "Cloud", "Deep", "Corridors and truth lattice", "Types claims as OK, NEAR, AMBIG, or FAIL."),
    ("J", "Cloud", "Map", "Residual ledgers", "Tracks unresolved debt and bounded approximation."),
    ("K", "Cloud", "Commit", "Conflict and quarantine", "Contains contradiction and fail states."),
    ("L", "Cloud", "Adapt", "Evidence-plan harness", "Promotes underdetermined claims toward witness-bearing truth."),
    ("M", "Fractal", "Deep", "Replay kernel", "Reconstructs lawful state across cycles."),
    ("N", "Fractal", "Map", "Container formats", "Carries salvage, seed, and compression surfaces."),
    ("O", "Fractal", "Commit", "Export bundles", "Moves mature outputs into publication form."),
    ("P", "Fractal", "Adapt", "Deployment profiles", "Brings manuscript law into runtime and field embodiment."),
]

SKILLS = [
    (
        "deeper-network-basis-router",
        "Route a request onto the correct 16-document basis, element, metro line, and appendix support set before synthesis begins.",
        "Use when a task touches the deeper integrated network and must be grounded in the correct basis documents before analysis starts.",
    ),
    (
        "pair-matrix-synthesizer",
        "Synthesize one ordered basis-document pair inside the 16x16 matrix and produce bridge, friction, metro, and appendix consequences.",
        "Use when a task is really a document-to-document bridge problem and needs ordered pair logic rather than a generic summary.",
    ),
    (
        "metro-resolution-expander",
        "Move between Level 1 through Level 7 metro resolutions without losing chapter, appendix, dimensional backplane, or neural-network alignment.",
        "Use when the user asks for a metro map, hidden lines, higher resolution, neural routing, or transcendent resolution.",
    ),
    (
        "appendix-crystal-governor",
        "Choose which appendix surfaces A-P and Q are required to keep a synthesis legal, replayable, and deployable.",
        "Use when a synthesis needs infrastructure, proof, truth typing, replay, or deployment support rather than only chapter prose.",
    ),
]


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, text: str) -> None:
    ensure_dir(path.parent)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def sanitize(text: str) -> str:
    out = []
    for ch in text.lower():
        out.append(ch if ch.isalnum() else "_")
    slug = "".join(out)
    while "__" in slug:
        slug = slug.replace("__", "_")
    return slug.strip("_")


def load_manifest() -> dict:
    if MANIFEST_PATH.exists():
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return {"live_docs_gate": "UNKNOWN", "live_record_count": 0, "archive_record_count": 0}


def build_basis() -> list[BasisDoc]:
    return [
        BasisDoc(1, "manuscript_brain", "The Holographic Manuscript Brain", "Water", "manuscript substrate", "turns documents into neural tissue", r"FRESH\The Holographic Manuscript Brain.docx", ("AppE", "AppF", "AppG", "AppM")),
        BasisDoc(2, "self_routing", "Self-Routing Meta-Framework", "Earth", "routing and search", "decides how the corpus searches itself", r"DEEPER CRYSTALIZATION\Self-Routing Meta-Framework...", ("AppE", "AppI", "AppL", "AppM")),
        BasisDoc(3, "qbd4", "QBD-4", "Air", "quad logic bits", "formalizes the four-bit address and rotation algebra", r"MATH\...QBD-4", ("AppB", "AppC", "AppM")),
        BasisDoc(4, "quad_rotation", "Quad Holographic Rotation", "Air", "holographic transport", "rotates one truth through all four faces", r"MATH\...Quad Holographic Rotation", ("AppE", "AppF", "AppM")),
        BasisDoc(5, "holographic_kernel", "The Holographic Kernel", "Air", "holographic compression", "compresses bodies without deleting structural DNA", r"MATH\...The Holographic Kernel", ("AppB", "AppC", "AppN")),
        BasisDoc(6, "time_fractal", "Time Fractal", "Fire", "fractal time", "gives the system phase, recurrence, and oscillation law", r"MATH\...Time Fractal", ("AppE", "AppM", "AppP")),
        BasisDoc(7, "crystal_computing", "Crystal Computing Framework", "Air", "fractal computing", "maps crystal structure into computation", r"MATH\...Crystal Computing Framework", ("AppB", "AppC", "AppG")),
        BasisDoc(8, "quantum_standard_hardware", "Quantum Computing on Standard Hardware", "Fire", "quantum classical emulation", "turns impossible compute into lawful approximation on ordinary machines", r"MATH\...Quantum Computing on Standard Hardware", ("AppC", "AppH", "AppP")),
        BasisDoc(9, "zero_point_computing", "Zero-Point Computing", "Earth", "zero-point engine", "defines minimum-state computation and restart from near nothing", r"MATH\...Zero-Point Computing", ("AppA", "AppN", "AppM")),
        BasisDoc(10, "athena_neural_tome", "Athena Neural Network Tome", "Fire", "emergence compiler", "binds manuscript, learning, and runtime emergence", r"NERUAL NETWORK\ATHENA Neural Network", ("AppC", "AppP", "AppM")),
        BasisDoc(11, "voynichvm", "VOYNICHVM Tricompiler", "Water", "text computer", "treats translation as computation and executable transformation", r"Voynich\...VOYNICHVM", ("AppF", "AppI", "AppM")),
        BasisDoc(12, "torat_hamispar", "Torat Ha-Mispar", "Water", "torah computer", "maps sacred number into algorithmic interpretation", r"MATH\...TORAT HA-MISPAR", ("AppA", "AppF", "AppO")),
        BasisDoc(13, "universal_ontology", "Universal Computational Ontology", "Earth", "mythic os", "converts mythic cosmology into system architecture", r"MATH\...Universal Computational Ontology", ("AppA", "AppB", "AppP")),
        BasisDoc(14, "ch11_helical_engine", "Ch11 The Helical Manifestation Engine", "Water", "restart and lift", "makes self-improvement executable through D/Q/I, lift, and recurrence", r"self_actualize\manuscript_sections\011_ch11_helical_manifestation_engine.md", ("AppE", "AppF", "AppI", "AppM")),
        BasisDoc(15, "ch12_boundary_axioms", "Ch12 Boundary Checks and Isolation Axioms", "Earth", "immune architecture", "protects the network from contradiction leakage and contamination", r"self_actualize\manuscript_sections\012_ch12_boundary_checks_and_isolation_axioms.md", ("AppB", "AppI", "AppK", "AppM")),
        BasisDoc(16, "ch19_self_repair", "Ch19 Recursive Self-Reference and Self-Repair", "Fire", "autonomic repair", "lets the organism watch, checkpoint, and heal itself", r"self_actualize\manuscript_sections\019_ch19_recursive_self_reference_and_self_repair.md", ("AppA", "AppM", "AppP")),
    ]


def shared_hubs(left: BasisDoc, right: BasisDoc) -> list[str]:
    return sorted(set(left.hubs).intersection(right.hubs))


def pair_relation(left: BasisDoc, right: BasisDoc) -> str:
    if left.slug == right.slug:
        return "self-intensification"
    if left.element == right.element:
        return f"{left.element.lower()} resonance"
    pair = {left.element, right.element}
    if pair in ({"Fire", "Water"}, {"Air", "Earth"}):
        return "adjacent complement"
    if pair in ({"Fire", "Air"}, {"Water", "Earth"}):
        return "translational cross-bridge"
    return "diagonal tension bridge"


def pair_bridge(left: BasisDoc, right: BasisDoc) -> str:
    pair = {left.element, right.element}
    if left.slug == right.slug:
        return "distill the same document across two scales and measure what remains load-bearing"
    if pair == {"Fire", "Water"}:
        return "convert ignition into circulation and circulation into committed emergence"
    if pair == {"Air", "Earth"}:
        return "bind abstract architecture to embodied practice without losing topology"
    if pair == {"Fire", "Air"}:
        return "move from explosive novelty into lawful graph structure"
    if pair == {"Water", "Earth"}:
        return "make fluid insight inhabitable in workflow, body, or institution"
    if pair == {"Fire", "Earth"}:
        return "stabilize force so it can become durable practice instead of flash"
    return "turn relation and circulation into a coherent field that can cross hostile boundaries"


def link_name(doc: BasisDoc) -> str:
    return f"{doc.idx:02d}_{doc.slug}"


def primary_appendices(doc: BasisDoc) -> str:
    return ", ".join(doc.hubs)


def basis_table(basis: list[BasisDoc]) -> str:
    lines = [
        "| # | Document | Element | Cluster | Role | Primary appendices |",
        "|---|---|---|---|---|---|",
    ]
    for doc in basis:
        lines.append(
            f"| {doc.idx:02d} | {doc.title} | {doc.element} | {doc.cluster} |"
            f" {doc.role} | {primary_appendices(doc)} |"
        )
    return "\n".join(lines)


def doc_line(doc: BasisDoc) -> str:
    return (
        f"- `{doc.idx:02d}` {doc.title} [{doc.element}]"
        f": {doc.role}. Cluster: {doc.cluster}. Source hint: `{doc.source_hint}`."
    )


def doc_basis_for_element(basis: list[BasisDoc], element: str) -> list[BasisDoc]:
    return [doc for doc in basis if doc.element == element] + [doc for doc in basis if doc.element != element]


def element_loop_filename(idx: int, loop_name: str) -> str:
    return f"{idx:02d}_{sanitize(loop_name)}.md"


def loop_observation(element: str, loop_name: str, loop_desc: str, doc: BasisDoc) -> str:
    relation = "native driver" if doc.element == element else "translated counterpart"
    return (
        f"- `{doc.idx:02d}` {doc.title}: in {element.lower()} mode, {doc.title} behaves as a"
        f" {relation} for `{loop_name}`. It {loop_desc}, using {doc.cluster} as the anchor"
        f" and {doc.role} as the contribution. Appendix stack: {primary_appendices(doc)}."
    )


def pair_neutral_synthesis(left: BasisDoc, right: BasisDoc) -> str:
    hubs = shared_hubs(left, right)
    hub_text = ", ".join(hubs) if hubs else "no direct appendix overlap, so Appendix Q and bridge receipts do the carrying"
    return (
        f"{left.title} and {right.title} form an ordered bridge in which {left.cluster} is asked to"
        f" inform {right.cluster}. The row document starts as the question-carrier and the column document"
        f" becomes the receiving surface. Their governing relation is `{pair_relation(left, right)}`, and"
        f" the bridge law is to {pair_bridge(left, right)}. Shared support surfaces: {hub_text}."
    )


def pair_element_view(element: str, left: BasisDoc, right: BasisDoc) -> str:
    focus = {
        "Fire": "ignition, risk, decisive transformation, and catalytic emergence",
        "Water": "circulation, thaw, coordination, and coherence under motion",
        "Air": "topology, relation, routing, and abstraction",
        "Earth": "embodiment, durability, institutionalization, and load-bearing form",
    }[element]
    return (
        f"- `{element}`: the pair is read through {focus}. {left.title} initiates, {right.title} receives,"
        f" and the test is whether one document's strengths survive translation into the other's domain."
    )


def loop_pair_sentence(loop_name: str, loop_desc: str, left: BasisDoc, right: BasisDoc) -> str:
    return (
        f"- `{loop_name}`: {left.title} contributes {left.role}, while {right.title} contributes"
        f" {right.role}. Together they {loop_desc}, converting {left.cluster} into"
        f" {right.cluster} through {pair_bridge(left, right)}."
    )


def pair_appendix_stack(left: BasisDoc, right: BasisDoc) -> list[str]:
    shared = shared_hubs(left, right)
    ordered = shared + [hub for hub in left.hubs + right.hubs if hub not in shared]
    if "AppQ" not in ordered:
        ordered.append("AppQ")
    return ordered[:7]


def build_readme(manifest: dict, basis: list[BasisDoc]) -> None:
    text = f"""
# Deeper Integrated Cross-Synthesis Network

This module materializes a deeper integrated neural-network shell inside the live `dynamic_neural_network` body. Its purpose is to take the strongest sixteen canonical documents, cross-synthesize them as an ordered `16 x 16` matrix, observe the whole system through four elemental lenses and sixteen macro loops, derive the fifteen non-empty symmetry syntheses of the four-element crystal, expose a first-class `3D` ingress package for atlas-wide embedding, and stabilize the result into a seven-level metro stack plus an appendix crystal with its own skill-routing layer.

## Ground truth

- Live Docs gate: `{manifest.get("live_docs_gate", "UNKNOWN")}`
- Live record count: `{manifest.get("live_record_count", 0)}`
- Archive record count: `{manifest.get("archive_record_count", 0)}`
- Canonical basis size: `{len(basis)}`
- Ordered pair matrix: `{len(basis) * len(basis)}`
- Elemental observer basis: `{len(LOOPS) * 4}`
- Symmetry syntheses: `15 + zero point`

This build is intentionally honest about scale. It does not materialize impossible literal permutations like `64^4` files. Instead it materializes the root observer basis, the ordered document matrix, the full symmetry stack, and the metro resolutions that compile those deeper passes on demand.

## Deep-root precedence

- Live deep root: `{LIVE_DEEP_ROOT}`
- Historical mirrors:
  - `{HISTORICAL_DEEP_MIRRORS[0]}`
  - `{HISTORICAL_DEEP_MIRRORS[1]}`

The generated `14_DEEPER...` root is the only live deep control surface.
The two older roots remain readable historical mirrors, not peer authorities.

## Organism law

- `4D + economy`: `{ORGANISM_LAW}`
- `EconomySalienceBudget` chooses which valid route gets build energy, ledger attention, and replay budget first.

## Structure

- `00_CONTROL`: laws, charter, recursion policy, and build pipeline
- `01_FIRE` through `04_EARTH`: `4 x 16` observer files
- `05_MATRIX_16X16`: all ordered document-pair syntheses
- `06_SYMMETRY_STACK`: the `15` elemental subset syntheses plus the zero point
- `07_METRO_STACK`: seven metro-map resolutions and route-selection logic
- `08_APPENDIX_CRYSTAL`: appendices `A-P` plus appendix `Q`
- `09_SKILLS`: local skills for routing, matrix synthesis, metro expansion, and appendix governance
- `10_LEDGERS`: manifests, counts, routes, and canonical-source records
- `11_6D_WATER_CONTROL`: overlay-only Water continuity, replay, and dimension-lift control surfaces
- `12_6D_AIR_CONTROL`: overlay-only AIR topology, sigma/spin, and seed-legibility control surfaces
- `13_6D_EARTH_CONTROL`: canonical Earth admissibility, quarantine, and re-entry gate surfaces
- `12_6D_EARTH_CONTROL`: historical Earth drift kept for compatibility, not canon
- `13_6D_H6_CONVERGENCE`: overlay-only shared convergence center and `Seed-6D` emission surfaces
- `14_3D_INGRESS_NETWORK`: first-class corpus-ingress package feeding the 4D compiled basis

## Canonical basis

{basis_table(basis)}

## Main law

`atlas body ingress -> 3D ingress package -> basis -> pair matrix -> observer lattice -> symmetry stack -> metro stack -> appendix governance -> FIRE 5D/6D lift -> Water 6D control lift -> AIR 6D topology overlay -> Earth 6D admissibility gate -> H6 convergence center -> 7D seed target`
"""
    write_text(OUTPUT_ROOT / "README.md", text)


def build_control_docs(manifest: dict, basis: list[BasisDoc]) -> None:
    control_root = OUTPUT_ROOT / "00_CONTROL"
    basis_lines = "\n".join(doc_line(doc) for doc in basis)
    write_text(
        control_root / "00_BUILD_CHARTER.md",
        f"""
# Build Charter

This folder is the contract for the deeper integrated cross-synthesis network.

## Objectives

0. Preserve deep-root precedence so the live shell does not compete with its historical mirrors.
1. Expose a first-class `3D` ingress package that maps atlas bodies and folder stations into the deeper-network basis.
2. Stabilize a `16` document canonical basis.
3. Materialize the full ordered `16 x 16` bridge matrix.
4. Observe the matrix through `4` elemental lenses and `16` macro loops.
5. Collapse those observations into the `15` non-empty symmetry syntheses.
6. Lift the result into the existing Level `1-7` metro stack plus appendix governance.
7. Expose the routing as local skills so future work can use the system instead of bypassing it.
8. Keep the build aligned with the wider organism law `{ORGANISM_LAW}`.

## Canonical documents

{basis_lines}

## Live-grounding status

- Live Docs gate: `{manifest.get("live_docs_gate", "UNKNOWN")}`
- Local live records: `{manifest.get("live_record_count", 0)}`
- Archive-backed records: `{manifest.get("archive_record_count", 0)}`
- Active deep root: `{LIVE_DEEP_ROOT}`
- Historical mirrors: `{HISTORICAL_DEEP_MIRRORS[0]}` and `{HISTORICAL_DEEP_MIRRORS[1]}`
- Organism law: `{ORGANISM_LAW}`
        """,
    )
    write_text(control_root / "01_16X16_MATRIX_LAW.md", "# 16x16 Matrix Law\n\nThe ordered matrix is the core neural tissue of this build. The row document asks, the column document receives, and every cell must name the bridge law, appendix stack, and metro consequence.")
    write_text(control_root / "02_64X4_OBSERVATION_COMPILER.md", "# 64x4 Observation Compiler\n\nThe requested `64^4` scale is compiled honestly as a recursive observation law. The materialized root is `4` elements by `16` loops, and each observer file can be re-expanded into document, route, appendix, and replay passes.")
    write_text(control_root / "03_ZERO_POINT_AND_SYMMETRY.md", "# Zero Point and Symmetry\n\nThe four-element crystal yields `15` non-empty subsets. Those are materialized in `06_SYMMETRY_STACK`, then compressed into one zero-point seed that remembers load-bearing documents, real bridges, active appendices, and remaining metro lines.")
    write_text(control_root / "04_ALGORITHMIC_PIPELINE.md", "# Algorithmic Pipeline\n\n1. Honor deep-root precedence and keep `14_DEEPER...` as the only live deep root.\n2. Read the live corpus atlas and derive deterministic `3D` ingress bindings for every record.\n3. Read the canonical basis.\n4. Check the live Docs gate.\n5. Apply the `EconomySalienceBudget` so high-yield legal routes get priority.\n6. Bind atlas bodies and folder stations into `14_3D_INGRESS_NETWORK`.\n7. Feed `3D_INGRESS` into the ordered matrix rather than bypassing the existing `4D` compiled basis.\n8. Build the ordered matrix.\n9. Build the observer lattice.\n10. Collapse to symmetry.\n11. Lift through the Level `1-7` metro stack and appendix governance.\n12. Preserve FIRE `5D/6D`, Water `6D`, AIR `6D`, Earth `6D`, and downstream `7D_SEED` overlays without rewriting canon.\n13. Publish skills for reuse.")
    write_text(control_root / "05_4D_PLUS_ECONOMY_LAW.md", f"# 4D Plus Economy Law\n\nThe deeper network is a replay surface inside the wider organism and therefore follows:\n\n`{ORGANISM_LAW}`\n\n- `AddressMesh`: where a basis document or appendix support surface lives.\n- `RelationMetro`: which corridor, metro line, or ordered pair carries the bridge.\n- `ChamberMembrane`: which truth, burden, or appendix shell constrains the move.\n- `ReplayReturnAxis`: how the move rebuilds, compresses, and reseeds.\n- `EconomySalienceBudget`: which valid move receives scarce build attention first.\n")


def build_element_files(basis: list[BasisDoc]) -> None:
    for element in ("Fire", "Water", "Air", "Earth"):
        folder = ELEMENT_PATHS[element]
        ordered_basis = doc_basis_for_element(basis, element)
        index_lines = [f"# {element} Observer Lattice", "", ELEMENT_INTROS[element], "", "## Loop files", ""]
        for idx, (loop_name, loop_desc) in enumerate(LOOPS, start=1):
            filename = element_loop_filename(idx, loop_name)
            index_lines.append(f"- `{filename}`: {loop_desc}.")
            observations = "\n".join(loop_observation(element, loop_name, loop_desc, doc) for doc in ordered_basis)
            write_text(folder / filename, f"# {element} x {loop_name}\n\n{ELEMENT_INTROS[element]}\n\n## Loop mandate\n\n`{loop_name}` {loop_desc}.\n\n## Full-basis observation\n\n{observations}\n")
        write_text(folder / "00_INDEX.md", "\n".join(index_lines))


def build_matrix_files(basis: list[BasisDoc]) -> None:
    matrix_root = OUTPUT_ROOT / "05_MATRIX_16X16"
    index_lines = ["# Ordered 16x16 Matrix", "", "## Rows", ""]
    for left in basis:
        row_dir = matrix_root / f"row_{link_name(left)}"
        index_lines.append(f"- `row_{link_name(left)}`: initiated by {left.title}.")
        row_lines = [f"# Row {left.idx:02d}: {left.title}", "", "## Cells", ""]
        for right in basis:
            filename = f"{link_name(left)}__{link_name(right)}.md"
            row_lines.append(f"- `{filename}`: {left.title} -> {right.title}.")
            appendices = ", ".join(pair_appendix_stack(left, right))
            element_views = "\n".join(pair_element_view(element, left, right) for element in ("Fire", "Water", "Air", "Earth"))
            loop_views = "\n".join(loop_pair_sentence(loop_name, loop_desc, left, right) for loop_name, loop_desc in LOOPS)
            write_text(
                row_dir / filename,
                f"# {left.title} -> {right.title}\n\n## Neutral synthesis\n\n{pair_neutral_synthesis(left, right)}\n\n## Four-lens read\n\n{element_views}\n\n## Sixteen-loop pass\n\n{loop_views}\n\n## Appendix stack\n\n- Required support: {appendices}\n- Ordered relation: `{pair_relation(left, right)}`\n- Metro implication: this cell strengthens the route from `{left.cluster}` toward `{right.cluster}`.\n",
            )
        write_text(row_dir / "00_INDEX.md", "\n".join(row_lines))
    write_text(matrix_root / "00_INDEX.md", "\n".join(index_lines))


def build_symmetry_files(basis: list[BasisDoc]) -> None:
    symmetry_root = OUTPUT_ROOT / "06_SYMMETRY_STACK"
    index_lines = ["# Symmetry Stack", "", "## Files", ""]
    counter = 1
    elements = ("Fire", "Water", "Air", "Earth")
    for size in range(1, 5):
        for combo in combinations(elements, size):
            docs = [doc for doc in basis if doc.element in combo]
            filename = f"{counter:02d}_{''.join(element[0].lower() for element in combo)}.md"
            index_lines.append(f"- `{filename}`: {' + '.join(combo)}.")
            write_text(
                symmetry_root / filename,
                f"# Symmetry {counter:02d}: {' + '.join(combo)}\n\n## Basis bodies\n\n" + "\n".join(doc_line(doc) for doc in docs) + "\n\n## Synthesis\n\nThis symmetry asks what becomes newly visible when these elements collaborate rather than compete.\n",
            )
            counter += 1
    write_text(symmetry_root / "99_zero_point.md", "# Symmetry Zero Point\n\nThe zero point compresses the full fifteen-symmetry stack into one seed that still knows how to rebuild the network.")
    write_text(symmetry_root / "00_INDEX.md", "\n".join(index_lines))


def build_metro_files(basis: list[BasisDoc]) -> None:
    metro_root = OUTPUT_ROOT / "07_METRO_STACK"
    level2_nodes = "\n".join(f'    N{doc.idx}["{doc.idx:02d} {doc.title}"]' for doc in basis)
    write_text(
        metro_root / "00_level_1_core_metro_map.md",
        "# Level 1 Core Metro Map\n\nLevel 1 is the readable corpus-ingress skeleton. It exposes `3D` body lines first, then hands traffic into the 4D compiled basis.\n",
    )
    write_text(
        metro_root / "01_level_2_deep_emergence_metro_map.md",
        f"# Level 2 Deep Emergence Metro Map\n\nLevel 2 names atlas-to-basis bridge pressure, latent folder transfer lines, and the first handoff from `3D` ingress into the `{len(basis)}`-document compiled basis.\n\n```mermaid\nflowchart LR\n{level2_nodes}\n    N1 --> N14\n    N14 --> N16\n    N16 --> N9\n    N2 --> N15\n    N3 --> N4\n    N4 --> N5\n    N5 --> N7\n    N8 --> N10\n    N11 --> N12\n    N12 --> N13\n```\n",
    )
    write_text(metro_root / "02_level_3_deeper_neural_map.md", "# Level 3 Deeper Neural Map\n\nLevel 3 binds the `16 -> 64 -> 256 -> 1024` tissue into one neural routing view while preserving the `3D` ingress body that fed it.")
    write_text(metro_root / "03_level_4_transcendence_metro_map.md", "# Level 4 Transcendence Metro Map\n\nLevel 4 is the 4D-native compiled field. Levels `5-7` remain additive overlays and downstream seed targets, not replacements for the core lattice.")
    write_text(metro_root / "04_route_selection.md", "# Route Selection\n\nUse Level 1 for corpus ingress, Level 2 for atlas-to-basis bridge pressure, Level 3 for active neural tissue, Level 4 for compiled native routes, Level 5 for Mobius bridge traffic, Level 6 for hologram weave, and Level 7 for downstream seed handoff.")


def build_ingress_files() -> None:
    ingress_root = OUTPUT_ROOT / "14_3D_INGRESS_NETWORK"
    write_text(
        ingress_root / "00_INDEX.md",
        "# 3D Ingress Network\n\nThis package is the first-class `3D` ingress body for the deeper network. It maps atlas bodies and folder stations into lawful entry routes that feed the existing 4D compiled basis without minting a competing chapter lattice, appendix namespace, or cortex publication layer.\n\n- Docs gate: `BLOCKED`\n- Stage law: `atlas body ingress -> 3D_INGRESS -> 4D_NATIVE -> 5D_COMPRESSION -> 6D_WEAVE -> 7D_SEED`\n- Canon law: chapter and appendix addresses remain unchanged.\n",
    )
    write_text(
        ingress_root / "01_corpus_body_ingress.md",
        "# Corpus Body Ingress\n\nPrimary ingress bodies are `self_actualize`, `NERVOUS_SYSTEM`, `ECOSYSTEM`, `MATH`, `NERUAL NETWORK`, `DEEPER CRYSTALIZATION`, `Voynich`, and `Trading Bot`. Each body becomes a 3D station with one entry line, one transfer-hub set, and one feed set into the 16-document deeper basis.\n",
    )
    write_text(
        ingress_root / "02_folder_to_basis_embedding.md",
        "# Folder To Basis Embedding\n\nThe embedding rule is deterministic: atlas body and folder scope choose a 3D station, then keyword/path pressure chooses zero or more of the 16 canonical basis refs. `MATH` and `self_actualize` remain the densest basis feeders.\n",
    )
    write_text(
        ingress_root / "03_local_metro_entry_routes.md",
        "# Local Metro Entry Routes\n\nLevel 1 exposes readable body lines. Level 2 names folder-to-basis bridge pressure. Level 3 reopens into the compiled basis and the current appendix floor.\n",
    )
    write_text(
        ingress_root / "04_reentry_into_4d_native.md",
        "# Reentry Into 4D Native\n\nNo 3D ingress route is complete until it names the 4D compiled basis refs it feeds, the appendix support it requires, and the replay-safe return spine through `Ch12<0023>`, `Ch13<0030>`, `Ch16<0033>`, `AppI`, and `AppM` when higher-dimensional overlays become active.\n",
    )


def build_appendix_files() -> None:
    appendix_root = OUTPUT_ROOT / "08_APPENDIX_CRYSTAL"
    index_lines = ["# Appendix Crystal", "", "## Appendices", ""]
    for letter, face, mode, title, role in APPENDIX_GRID:
        filename = f"App{letter}_{sanitize(title)}.md"
        index_lines.append(f"- `{filename}`: {title}.")
        write_text(
            appendix_root / filename,
            f"# Appendix {letter}: {title}\n\n- Face: `{face}`\n- Mode: `{mode}`\n- Role: {role}\n\n## Skeleton\n\n1. Purpose and boundary\n2. Data or proof surfaces carried here\n3. Chapter dependencies\n4. Metro dependencies\n5. Failure mode if ignored\n",
        )
    write_text(appendix_root / "AppQ_appendix_only_metro_map.md", "# Appendix Q: Appendix-Only Metro Map\n\nAppendix Q is the appendix-only transit layer linking A-P without depending on chapter prose.\n")
    write_text(appendix_root / "00_INDEX.md", "\n".join(index_lines))


def build_skill_files() -> None:
    skill_root = OUTPUT_ROOT / "09_SKILLS"
    write_text(
        skill_root / "00_SKILL_ROUTER.md",
        "# Skill Router\n\n1. `deeper-network-basis-router`\n2. `pair-matrix-synthesizer`\n3. `metro-resolution-expander`\n4. `appendix-crystal-governor`\n\nRoute basis first, then pair logic, then metro resolution, then appendix legality.\n",
    )
    for name, description, usage in SKILLS:
        write_text(
            skill_root / name / "SKILL.md",
            f"---\nname: {name}\ndescription: {description}\n---\n\n# {name}\n\n{usage}\n\n## Workflow\n\n1. Read `../../00_CONTROL/04_ALGORITHMIC_PIPELINE.md`.\n2. Check `../../10_LEDGERS/01_CANONICAL_SOURCES.md`.\n3. If needed, inspect `../../05_MATRIX_16X16`, `../../07_METRO_STACK`, and `../../08_APPENDIX_CRYSTAL`.\n\n## Output contract\n\n- Name the basis documents.\n- Name the active element or symmetry.\n- Name the metro level.\n- Name the appendix stack.\n",
        )


def build_ledgers(manifest: dict, basis: list[BasisDoc]) -> None:
    ledger_root = OUTPUT_ROOT / "10_LEDGERS"
    write_text(
        ledger_root / "00_MANIFEST.md",
        f"# Manifest\n\n- Generated at: `{datetime.now(timezone.utc).isoformat()}`\n- Live Docs gate: `{manifest.get('live_docs_gate', 'UNKNOWN')}`\n- Live record count: `{manifest.get('live_record_count', 0)}`\n- Archive record count: `{manifest.get('archive_record_count', 0)}`\n- Basis docs: `{len(basis)}`\n- Ordered matrix cells: `{len(basis) * len(basis)}`\n- Canonical metro baseline: `Level 1-7`\n- Stage law: `atlas body ingress -> 3D_INGRESS -> 4D_NATIVE -> 5D_COMPRESSION -> 6D_WEAVE -> 7D_SEED`\n- Active deep root: `{LIVE_DEEP_ROOT}`\n- Historical mirrors: `{HISTORICAL_DEEP_MIRRORS[0]}` and `{HISTORICAL_DEEP_MIRRORS[1]}`\n- Organism law: `{ORGANISM_LAW}`\n- Last reconciled: `{datetime.now(timezone.utc).date().isoformat()}`\n",
    )
    write_text(ledger_root / "01_CANONICAL_SOURCES.md", "# Canonical Sources\n\n" + "\n".join(doc_line(doc) for doc in basis))
    write_text(ledger_root / "02_ROUTE_LEDGER.md", "# Route Ledger\n\n" + "\n".join(f"- `{doc.title}` starts in `{doc.element}` and usually pulls `{primary_appendices(doc)}` into the route." for doc in basis))
    write_text(
        ledger_root / "03_FILE_COUNTS.md",
        "# File Counts\n\n- `15` control documents\n- `64` elemental observer files\n- `256` ordered pair files\n- `15` symmetry files plus zero point\n- `8` metro files\n- `17` appendix skeletons plus overlay support\n- `4` skill packages\n- `1` first-class `3D` ingress package\n\n## Count protocol\n\nThe deep root consumes the wider organism's count classes without pretending they are interchangeable.\n\n- `live record count` is the indexed live atlas witness.\n- `archive record count` is the archive-backed atlas witness.\n- physical, board, promoted, and generated counts live on their own upstream surfaces and should not be collapsed into one scalar.\n",
    )
    write_text(
        ledger_root / "04_PRECEDENCE_AND_ECONOMY.md",
        f"# Precedence And Economy\n\n- Live deep root: `{LIVE_DEEP_ROOT}`\n- Historical mirrors:\n  - `{HISTORICAL_DEEP_MIRRORS[0]}`\n  - `{HISTORICAL_DEEP_MIRRORS[1]}`\n- Organism law: `{ORGANISM_LAW}`\n\nThe deeper network is lawful only when precedence and budget are explicit. A valid route can still lose priority if its replay gain is lower than a competing route's economy score.\n",
    )
    generated_manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "live_docs_gate": manifest.get("live_docs_gate", "UNKNOWN"),
        "live_record_count": manifest.get("live_record_count", 0),
        "archive_record_count": manifest.get("archive_record_count", 0),
        "basis_docs": [doc.title for doc in basis],
        "output_root": str(OUTPUT_ROOT),
        "active_deep_root": str(LIVE_DEEP_ROOT),
        "historical_mirrors": [str(path) for path in HISTORICAL_DEEP_MIRRORS],
        "organism_law": ORGANISM_LAW,
    }
    write_text(ledger_root / "generated_manifest.json", json.dumps(generated_manifest, indent=2))


def main() -> None:
    manifest = load_manifest()
    basis = build_basis()
    ensure_dir(OUTPUT_ROOT)
    build_readme(manifest, basis)
    build_control_docs(manifest, basis)
    build_element_files(basis)
    build_matrix_files(basis)
    build_symmetry_files(basis)
    build_metro_files(basis)
    build_appendix_files()
    build_skill_files()
    build_ingress_files()
    build_ledgers(manifest, basis)
    print(f"Built deeper integrated network at {OUTPUT_ROOT}")


if __name__ == "__main__":
    main()
