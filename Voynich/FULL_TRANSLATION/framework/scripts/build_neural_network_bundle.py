from __future__ import annotations

import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Tuple


ROOT = Path(r"C:\Users\dmitr\Documents\Athena Agent\Voynich")
OUT = ROOT / "FULL_TRANSLATION" / "neural_network"
DOC_EXTS = {".md", ".txt", ".docx"}


NODE_META: Dict[str, Dict[str, object]] = {
    "N01": {"name": "Root Canon", "desc": "root-level canonical Voynich statements and top-entry texts", "bias": ("Fire", "Air")},
    "N02": {"name": "NEW Research Corpus", "desc": "introductory and working translation documents under NEW", "bias": ("Air", "Earth")},
    "N03": {"name": "EVA Transcription Bedrock", "desc": "raw transcription and baseline witness materials", "bias": ("Earth", "Air")},
    "N04": {"name": "FRESH Meta-Manuscript Layer", "desc": "manuscript-brain and self-referential seed texts", "bias": ("Water", "Air")},
    "N05": {"name": "Plant Folio Corpus", "desc": "Book I final-draft and supporting plant folios", "bias": ("Fire", "Water")},
    "N06": {"name": "Astrology Folio Corpus", "desc": "Book II timing and zodiac folios", "bias": ("Air", "Water")},
    "N07": {"name": "Bath Folio Corpus", "desc": "Book III circulation and purification folios", "bias": ("Water", "Earth")},
    "N08": {"name": "Cosmology Folio Corpus", "desc": "Book IV foldout and rosette routing folios", "bias": ("Earth", "Air")},
    "N09": {"name": "Pharmaceutical Folio Corpus", "desc": "Book V formulation and closure folios", "bias": ("Fire", "Earth")},
    "N10": {"name": "Section Synthesis Layer", "desc": "section-level ledgers and synthesis files", "bias": ("Water", "Earth")},
    "N11": {"name": "Crystal Layer", "desc": "book crystals and whole-corpus crystal files", "bias": ("Earth", "Water")},
    "N12": {"name": "Unified Manuscript Layer", "desc": "merged corpus-order and packaging manuscripts", "bias": ("Earth", "Fire")},
    "N13": {"name": "Framework Runtime", "desc": "schemas, registries, templates, and rendering scripts", "bias": ("Earth", "Air")},
    "N14": {"name": "Math Corpus", "desc": "formal mathematical subcorpus and operator tomes", "bias": ("Air", "Fire")},
    "N15": {"name": "Manifest and Autonomy Layer", "desc": "status, planning, queue, and runtime control files", "bias": ("Earth", "Air")},
    "N16": {"name": "Meta-Engine and Synthesis Layer", "desc": "Chapter 11, 21-chapter synthesis, and neural integration artifacts", "bias": ("Air", "Earth")},
}


INFO_META: Dict[str, Dict[str, str]] = {
    "N01": {
        "role": "entry priors and top-level thesis compression",
        "risk": "canon can over-dominate witnesses and create false certainty if it is not discharged into the evidentiary bedrock",
        "handoff": "N01 -> N02 -> N03",
        "compression": "preserve the core thesis, strip rhetorical duplication, and force witness linkage before promotion",
    },
    "N02": {
        "role": "working hypothesis lattice and research search surface",
        "risk": "rapid theory growth can outpace witness reconciliation",
        "handoff": "N02 -> N03 -> N10",
        "compression": "preserve only hypotheses that survive transcription pressure or book-level recurrence",
    },
    "N03": {
        "role": "witness anchor, glyph constraint, and baseline admissibility floor",
        "risk": "if N03 is collapsed into summary prose, the whole field loses its truth corridor",
        "handoff": "N03 -> N05/N06/N07/N08/N09",
        "compression": "never compress raw witness away; compress only commentary around the witness",
    },
    "N04": {
        "role": "meta-seed memory and manuscript self-reference",
        "risk": "meta recursion can drift into self-description untethered from payload",
        "handoff": "N04 -> N11 -> N16",
        "compression": "preserve only the load-bearing reseeding laws, not every visionary wrapper",
    },
    "N05": {
        "role": "highest-payload botanical information field and Book I source density",
        "risk": "payload abundance creates entropy overflow unless section compression intervenes",
        "handoff": "N05 -> N10 -> N11",
        "compression": "compress by extracting operator families and repeated preparation patterns, not by deleting plant distinctives",
    },
    "N06": {
        "role": "timing, scheduler, and celestial address information",
        "risk": "address logic can become symbolic decoration if it is not tied back to process timing",
        "handoff": "N06 -> N10 -> N11",
        "compression": "preserve the timing grammar and route families while removing repetitive wheel scaffolding",
    },
    "N07": {
        "role": "circulation, purification, and transit-channel information",
        "risk": "route abundance can become diagram noise unless channels are typed",
        "handoff": "N07 -> N08 -> N11",
        "compression": "preserve bathhouse channel types and purification sequences, collapse repeated bathing surface details",
    },
    "N08": {
        "role": "global routing diagram and long-range transit information",
        "risk": "macro routing can be overread if local node evidence is missing",
        "handoff": "N08 -> N11 -> N12",
        "compression": "preserve system topology, bridge stations, and foldout transfers, prune decorative restatement",
    },
    "N09": {
        "role": "formula closure, dosage packaging, and terminal instruction information",
        "risk": "late-formulation density can hide distinctions between stable closure and volatile residue",
        "handoff": "N09 -> N10 -> N11 -> N12",
        "compression": "preserve final-formula differentials, thresholds, and closure operators",
    },
    "N10": {
        "role": "mid-level compressor from folios into teachable book structures",
        "risk": "sections can become bland if they compress before naming invariants",
        "handoff": "N10 -> N11 -> N12",
        "compression": "reduce redundancy aggressively but never collapse witness diversity into one false master line",
    },
    "N11": {
        "role": "crystal-level topology preservation and whole-book operator compression",
        "risk": "crystals can become abstract enough to lose the energy of individual folios",
        "handoff": "N11 -> N12 -> N16",
        "compression": "keep only stable hubs, lines, invariants, and cross-book bridges",
    },
    "N12": {
        "role": "global package memory and manuscript-order replay surface",
        "risk": "packaging can imply completion even when frontier files remain unresolved",
        "handoff": "N12 -> N15 -> N16",
        "compression": "preserve corpus order, theorem sequence, and packaging integrity",
    },
    "N13": {
        "role": "runtime law, schema, and render-contract information",
        "risk": "framework precision can drift away from the actual artifacts it is meant to govern",
        "handoff": "N13 -> N15 -> N16",
        "compression": "keep registries, schemas, and generator contracts; remove stale scaffolding",
    },
    "N14": {
        "role": "formal operator kernel and mathematical proof density",
        "risk": "symbolic rigor can become detached if it does not map back to the ledgered folio operations",
        "handoff": "N14 -> N11 -> N16",
        "compression": "preserve only the equations that explain or constrain real manuscript operators",
    },
    "N15": {
        "role": "process memory, queues, manifests, and autonomy receipts",
        "risk": "control files can accumulate bloat faster than the artifact layer they govern",
        "handoff": "N15 -> N16 -> next runtime seed",
        "compression": "retain live state, invariants, blockers, and next-step receipts; purge expired chatter",
    },
    "N16": {
        "role": "meta-engine, whole-field synthesis, and next-dimensional seed compiler",
        "risk": "if N16 overclaims scale, the entire network becomes performative instead of replayable",
        "handoff": "N16 -> N04* -> next seed",
        "compression": "preserve only the laws, routes, and appendix supports that regenerate the field lawfully",
    },
}


PAIR_VERBS = {
    ("Fire", "Fire"): "intensifies",
    ("Fire", "Water"): "heats and stabilizes",
    ("Fire", "Air"): "executes under schedule",
    ("Fire", "Earth"): "tests against containment",
    ("Water", "Fire"): "cools and carries",
    ("Water", "Water"): "recirculates",
    ("Water", "Air"): "phase-locks",
    ("Water", "Earth"): "routes through channels",
    ("Air", "Fire"): "times",
    ("Air", "Water"): "indexes",
    ("Air", "Air"): "readdresses",
    ("Air", "Earth"): "maps onto districts",
    ("Earth", "Fire"): "houses",
    ("Earth", "Water"): "stabilizes",
    ("Earth", "Air"): "certifies",
    ("Earth", "Earth"): "supports",
}


def rel_docs() -> List[Path]:
    docs = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in DOC_EXTS:
            continue
        rel = path.relative_to(ROOT)
        if str(rel).lower().startswith("full_translation/neural_network/"):
            continue
        docs.append(rel)
    return sorted(docs)


def folio_number(name: str) -> int | None:
    m = re.match(r"F(\d{3})", name.upper())
    if not m:
        return None
    return int(m.group(1))


def classify(rel: Path) -> str:
    s = rel.as_posix().lower()
    name = rel.name
    if s.startswith("full_translation/manuscripts/") or "chapter_11_" in s:
        return "N16"
    if s.startswith("full_translation/math/"):
        return "N14"
    if s.startswith("full_translation/framework/"):
        return "N13"
    if s.startswith("full_translation/manifests/"):
        return "N15"
    if s.startswith("full_translation/unified/"):
        return "N12"
    if s.startswith("full_translation/crystals/"):
        return "N11"
    if s.startswith("full_translation/sections/"):
        return "N10"
    if s.startswith("full_translation/folios/"):
        n = folio_number(name)
        if n is None:
            return "N09"
        if n <= 57:
            return "N05"
        if n <= 74:
            return "N06"
        if n <= 84:
            return "N07"
        if n <= 86:
            return "N08"
        return "N09"
    if s.startswith("fresh/"):
        return "N04"
    if s.startswith("eva/"):
        return "N03"
    if s.startswith("new/"):
        return "N02"
    return "N01"


def node_counts(docs: List[Path]) -> Tuple[Dict[str, List[Path]], Counter]:
    bucket: Dict[str, List[Path]] = defaultdict(list)
    ext = Counter()
    for rel in docs:
        bucket[classify(rel)].append(rel)
        ext[rel.suffix.lower()] += 1
    return bucket, ext


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def pair_summary(a: str, b: str) -> str:
    ma = NODE_META[a]
    mb = NODE_META[b]
    ea = ma["bias"][0]
    eb = mb["bias"][0]
    verb = PAIR_VERBS[(ea, eb)]
    return f"{ma['name']} {verb} {mb['name'].lower()} so that {ma['desc']} can be read against {mb['desc']}."


def build_root_readme() -> str:
    return "\n".join(
        [
            "# Neural Network Layer",
            "",
            "## Purpose",
            "",
            "This folder holds the deeper integrated document-field synthesis across the full Voynich corpus. It is the layer that stops reading the project only as folios, sections, and crystals, and starts reading it as one document-field nervous system.",
            "",
            "## Architecture",
            "",
            "- `DOCUMENT_FIELD_ATLAS.md` = every indexed local manuscript document placed into the neural field",
            "- `DOCUMENT_NODE_REGISTRY_16.md` = the 16-node abstraction layer that makes full-corpus permutation work tractable",
            "- `PERMUTATION_MATRIX_16X16.md` = the full node-to-node cross-synthesis surface",
            "- `MASTER_NEURAL_SYNTHESIS.md` = neutral synthesis plus the 15-synthesis lattice, the information theorem, and the neural zero-point",
            "- `SECOND_PASS_INFORMATION_DELTA.md` = the escalation ledger for the deeper second pass",
            "- `METRO_MAP_L1.md` through `METRO_MAP_L4_TRANSCENDENT.md` = four general route resolutions",
            "- `APPENDIX_CRYSTAL_SKELETON.md` = appendix A-P crystal plus Appendix Q appendix-only metro map",
            "- `NEURAL_SKILL_PIPELINE.md` = when, how, and why to use the neural skill family",
            "- `FIRE/`, `WATER/`, `AIR/`, `EARTH/` = elemental observation folders with one `64`-observation matrix each",
            "- `INFORMATION/` = explicit information-topology layer: entropy, handoff, compression, replay, and information metro routes",
            "",
            "## Why This Layer Exists",
            "",
            "The folio corpus tells us what each page means. The section and crystal layers tell us what each book means. The neural layer asks a different question: what happens when every document-class in the whole project is allowed to interact with every other document-class under a consistent registry, route logic, and reseeding law?",
            "",
            "The second pass adds the information layer because the first neural pass still kept information implicit inside the elemental field. This pass names which nodes are high-entropy payload zones, which are compression surfaces, which are replay and runtime governance surfaces, and which handoffs are lawful versus lossy.",
            "",
            "## Zero Point",
            "",
            "The neural layer treats the corpus as a self-routing manuscript machine. The information layer clarifies why: every document becomes more valuable when it is read not only for its local claim, but for the kind of information it stores, the entropy it introduces, the compression it requires, the handoff it enables, and the replay burden it passes forward.",
        ]
    )


def build_atlas(docs: List[Path], buckets: Dict[str, List[Path]], ext: Counter) -> str:
    lines = [
        "# Document Field Atlas",
        "",
        "## Scope",
        "",
        f"- Total indexed documents: `{len(docs)}`",
        f"- Markdown: `{ext['.md']}`",
        f"- Text: `{ext['.txt']}`",
        f"- Docx: `{ext['.docx']}`",
        "- This atlas lists every indexed manuscript document and assigns it to one of the 16 neural nodes.",
        "",
    ]
    for code in sorted(NODE_META):
        meta = NODE_META[code]
        members = buckets.get(code, [])
        info = INFO_META[code]
        lines.extend(
            [
                f"## {code} - {meta['name']}",
                "",
                f"- Description: {meta['desc']}",
                f"- Bias: `{meta['bias'][0]} -> {meta['bias'][1]}`",
                f"- Members: `{len(members)}`",
                f"- Information role: {info['role']}",
                f"- Lawful handoff: `{info['handoff']}`",
                "",
            ]
        )
        lines.extend(f"- `{p.as_posix()}`" for p in members)
        lines.append("")
    return "\n".join(lines)


def build_registry(buckets: Dict[str, List[Path]]) -> str:
    lines = [
        "# Document Node Registry 16",
        "",
        "## Purpose",
        "",
        "This registry defines the 16-node neural field used for deeper cross-synthesis. Every indexed document belongs to exactly one node; cross-synthesis occurs over node-to-node combinations so the entire corpus can be integrated without pretending every single file pair needs a hand-written standalone treatise.",
        "",
        "| Node | Name | Bias | Count | Information Role | Lawful Handoff |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for code in sorted(NODE_META):
        meta = NODE_META[code]
        info = INFO_META[code]
        lines.append(
            f"| {code} | {meta['name']} | {meta['bias'][0]} -> {meta['bias'][1]} | {len(buckets.get(code, []))} | {info['role']} | {info['handoff']} |"
        )
    lines.append("")
    lines.append("## Zero Point")
    lines.append("")
    lines.append("The 16 nodes together describe one manuscript nervous system: raw sources, transcription bedrock, meta-seed texts, book-level folios, section compression, crystal compression, runtime infrastructure, mathematics, autonomy, and higher-order synthesis. The information layer clarifies that these nodes are not equal-density containers: some create entropy, some reduce it, some certify it, and some reseed it.")
    return "\n".join(lines)


def build_permutation_matrix() -> str:
    lines = [
        "# Permutation Matrix 16 x 16",
        "",
        "## Purpose",
        "",
        "This file states the full node-to-node cross-synthesis surface. Each of the 256 entries is a compressed permutation statement: what one document-node does to another when read as part of a single neural field.",
        "",
    ]
    for a in sorted(NODE_META):
        lines.append(f"## Source {a} - {NODE_META[a]['name']}")
        lines.append("")
        for b in sorted(NODE_META):
            lines.append(f"- `{a} x {b}`: {pair_summary(a, b)}")
        lines.append("")
    return "\n".join(lines)


def element_obs(element: str) -> List[str]:
    obs: List[str] = []
    for idx, code in enumerate(sorted(NODE_META), start=1):
        meta = NODE_META[code]
        obs.append(f"{idx}. {element} reads {meta['name']} as the place where {meta['desc']} becomes most legible through {element.lower()} law.")
    for idx, code in enumerate(sorted(NODE_META), start=17):
        meta = NODE_META[code]
        obs.append(f"{idx}. {element} says {meta['name']} fails when its shadow overwhelms its dominant bias and its handoff into the next node is not explicit.")
    for idx, code in enumerate(sorted(NODE_META), start=33):
        meta = NODE_META[code]
        obs.append(f"{idx}. {element} measures {meta['name']} by whether its outputs can survive translation into neighboring nodes without losing type, route, or replay value.")
    for idx, code in enumerate(sorted(NODE_META), start=49):
        meta = NODE_META[code]
        obs.append(f"{idx}. {element} prescribes that {meta['name']} should be compressed only after its primary invariants have been named, preserved, and handed off.")
    return obs


def build_element_doc(element: str) -> str:
    lines = [
        f"# {element} Neural Folder",
        "",
        "## Purpose",
        "",
        f"This folder holds the {element.lower()}-dominant view of the full document field. It is one quarter of the deeper integrated neural network.",
        "",
        "## 64 Observations",
        "",
    ]
    lines.extend(element_obs(element))
    lines.extend(
        [
            "",
            "## Local Zero Point",
            "",
            f"{element} says the corpus becomes intelligible when every node is re-read through {element.lower()} priority without erasing the other three elements.",
        ]
    )
    return "\n".join(lines)


def build_information_readme() -> str:
    return "\n".join(
        [
            "# Information Layer",
            "",
            "## Purpose",
            "",
            "This folder is the second deeper pass on the neural network. It makes information explicit instead of leaving it implicit inside the elemental and node registries.",
            "",
            "## What It Names",
            "",
            "- where entropy is born",
            "- where witness noise must be preserved instead of erased",
            "- where redundancy is allowed because it increases replay safety",
            "- where compression is lawful",
            "- where promotion into the next seed becomes admissible",
            "",
            "## Files",
            "",
            "- `INFORMATION_OBSERVATION_MATRIX_64.md` = 64 systematic information observations across the 16 nodes",
            "- `INFORMATION_TOPOLOGY.md` = role, entropy risk, handoff law, and compression duty for each node",
            "- `INFORMATION_METRO_MAP.md` = multi-resolution information routes from payload to seed",
            "- `INFORMATION_ZERO_POINT.md` = the compressed theorem of the information layer",
        ]
    )


def build_information_matrix(buckets: Dict[str, List[Path]]) -> str:
    obs: List[str] = []
    for idx, code in enumerate(sorted(NODE_META), start=1):
        meta = NODE_META[code]
        info = INFO_META[code]
        count = len(buckets.get(code, []))
        obs.append(f"{idx}. Information reads {meta['name']} as `{count}` local files storing {info['role']}.")
    for idx, code in enumerate(sorted(NODE_META), start=17):
        meta = NODE_META[code]
        info = INFO_META[code]
        obs.append(f"{idx}. Information says the primary entropy risk of {meta['name']} is that {info['risk']}.")
    for idx, code in enumerate(sorted(NODE_META), start=33):
        meta = NODE_META[code]
        info = INFO_META[code]
        obs.append(f"{idx}. Information requires the lawful handoff `{info['handoff']}` for {meta['name']} so that no bridge family is silently dropped.")
    for idx, code in enumerate(sorted(NODE_META), start=49):
        meta = NODE_META[code]
        info = INFO_META[code]
        obs.append(f"{idx}. Information permits compression of {meta['name']} only when {info['compression']}.")
    return "\n".join(
        [
            "# Information Observation Matrix 64",
            "",
            "## Purpose",
            "",
            "These 64 observations are the information-theoretic second pass on the neural field. They separate storage role, entropy risk, lawful handoff, and compression law instead of flattening them into one generic synthesis voice.",
            "",
            "## 64 Observations",
            "",
            *obs,
            "",
            "## Local Zero Point",
            "",
            "Information says the corpus is healthy when witness-heavy nodes are allowed to stay dense, middle nodes reduce redundancy without erasing type, and the meta-engine only lifts what can be replayed.",
        ]
    )


def build_information_topology(buckets: Dict[str, List[Path]]) -> str:
    lines = [
        "# Information Topology",
        "",
        "## Information Laws",
        "",
        "1. Witness density is not bloat when it preserves admissibility.",
        "2. Section and crystal layers must remove redundancy, not distinctions.",
        "3. Runtime and manifest layers store control information, not primary payload.",
        "4. Math is only lawful when it constrains or explains manuscript operators.",
        "5. Meta-synthesis may lift only what survives replay and handoff.",
        "6. The corpus is healthiest when entropy moves downward into compression surfaces before reseeding upward into N16.",
        "",
        "## Node Table",
        "",
        "| Node | Count | Information Role | Entropy Risk | Lawful Handoff | Compression Duty |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for code in sorted(NODE_META):
        info = INFO_META[code]
        lines.append(
            f"| {code} | {len(buckets.get(code, []))} | {info['role']} | {info['risk']} | {info['handoff']} | {info['compression']} |"
        )
    lines.extend(
        [
            "",
            "## Global Information Currents",
            "",
            "- Witness current: `N03 -> N05/N06/N07/N08/N09 -> N10`",
            "- Compression current: `N05/N06/N07/N08/N09 -> N10 -> N11`",
            "- Replay current: `N13 -> N15 -> N12`",
            "- Meta-seed current: `N04 -> N11 -> N16 -> N04*`",
            "- Whole-manuscript current: `N11 -> N12 -> N16`",
            "",
            "## Zero Point",
            "",
            "The information topology says not every document carries the same kind of truth. Folios store payload. Sections store pattern selection. Crystals store topology. Unified files store order. Frameworks store render law. Manifests store process state. The meta-engine stores what is worthy of becoming the next seed.",
        ]
    )
    return "\n".join(lines)


def build_information_metro() -> str:
    return "\n".join(
        [
            "# Information Metro Map",
            "",
            "## Level 1 - Base Routes",
            "",
            "| Line | Stations | Meaning |",
            "| --- | --- | --- |",
            "| Witness Recovery | `N01 -> N02 -> N03 -> N05` | root claims only become payload after witness discharge |",
            "| Payload Compression | `N05 -> N10 -> N11` | dense folio matter becomes section pattern and then crystal topology |",
            "| Scheduler Route | `N03 -> N06 -> N10 -> N11` | transcription becomes timing logic and then reusable route law |",
            "| Purification Route | `N05 -> N07 -> N08 -> N11` | matter enters circulation, then global routing, then stable topology |",
            "| Closure Route | `N09 -> N10 -> N11 -> N12` | formulas become book structure, crystal law, and package memory |",
            "| Runtime Proof | `N13 -> N15 -> N12` | framework law becomes process memory and then replayable package state |",
            "",
            "## Level 2 - Emergent Routes",
            "",
            "| Line | Stations | Meaning |",
            "| --- | --- | --- |",
            "| Entropy Relief | `N05/N06/N07/N08/N09 -> N10 -> N11` | high-detail payload zones relieve entropy into compression surfaces |",
            "| Witness Honesty | `N03 -> N15 -> N16` | witness limitations must remain visible all the way up into the meta-engine |",
            "| Proof Lift | `N14 -> N11 -> N16` | math becomes seed-worthy only after crystal topology accepts it |",
            "| Package Lift | `N12 -> N15 -> N16` | packaged corpus and live process memory meet in the lift compiler |",
            "",
            "## Level 3 - Neural Clusters",
            "",
            "| Cluster | Stations | Meaning |",
            "| --- | --- | --- |",
            "| Payload Cluster | `N05 N06 N07 N08 N09` | where information is born faster than it can be compressed |",
            "| Compression Cluster | `N10 N11 N12` | where redundancy falls away and order is preserved |",
            "| Governance Cluster | `N13 N14 N15` | where proofs, schemas, and control receipts stabilize the field |",
            "| Reseed Cluster | `N04 N16` | where compressed topology becomes the next neural seed |",
            "",
            "## Level 4 - Transcendent Helix",
            "",
            "| Orbit | Stations | Meaning |",
            "| --- | --- | --- |",
            "| Payload to Seed | `N03 -> N05/N06/N07/N08/N09 -> N10 -> N11 -> N16 -> N04*` | raw witness becomes the next lawful seed |",
            "| Runtime to Seed | `N13 -> N15 -> N16 -> N04*` | the system's control memory becomes reseeding law |",
            "| Package to Seed | `N12 -> N16 -> N04*` | whole-manuscript package becomes a compressed restart object |",
            "",
            "## Hubs",
            "",
            "- `N10` = first entropy-relief hub",
            "- `N11` = first topology-preserving compression hub",
            "- `N15` = live process and replay hub",
            "- `N16` = final lift and reseeding hub",
            "",
            "## Zero Point",
            "",
            "The information metro says the corpus is not only a set of meanings. It is a transport economy for meaning, where each node either births, constrains, compresses, certifies, packages, or reseeds information.",
        ]
    )


def build_information_zero() -> str:
    return "\n".join(
        [
            "# Information Zero Point",
            "",
            "The second pass resolves the neural field as an information machine with six lawful duties: witness preservation, entropy relief, topology preservation, replay governance, package integrity, and reseeding. High-entropy folio nodes must stay rich enough to remain true. Mid-level section and crystal nodes must compress without erasing distinctions. Framework, math, and manifest nodes must guarantee replay and lawful promotion. The final criterion is simple: only information that can survive witness, compression, routing, proof, and replay may become the next seed.",
        ]
    )


def build_second_pass_delta() -> str:
    return "\n".join(
        [
            "# Second Pass Information Delta",
            "",
            "## Prior Weak Gates",
            "",
            "- information roles were implicit instead of explicit",
            "- the first pass did not distinguish payload entropy from lawful redundancy",
            "- handoff law between nodes was not stated as its own surface",
            "- compression duties were distributed across prose instead of gathered into one replayable map",
            "",
            "## Newly Promoted Gates",
            "",
            "- information observation matrix",
            "- information topology",
            "- information metro map",
            "- information zero-point theorem",
            "- information-specific skill routing inside the neural family",
            "",
            "## Artifacts Created",
            "",
            "- `INFORMATION/README.md`",
            "- `INFORMATION/INFORMATION_OBSERVATION_MATRIX_64.md`",
            "- `INFORMATION/INFORMATION_TOPOLOGY.md`",
            "- `INFORMATION/INFORMATION_METRO_MAP.md`",
            "- `INFORMATION/INFORMATION_ZERO_POINT.md`",
            "- `voynich-neural-information-cartographer` skill",
            "",
            "## Remaining Unresolved Gates",
            "",
            "- live Google Docs search remains blocked, so this pass is local-corpus grounded",
            "- the information layer is node-compiled rather than literal per-file treatise generation, by design",
            "",
            "## Next Frontier",
            "",
            "Use the information layer when refining the whole-manuscript package, the next-seed bundle, or any future corpus that needs explicit entropy, handoff, compression, and replay law.",
        ]
    )


def build_master_synthesis(buckets: Dict[str, List[Path]], docs: List[Path]) -> str:
    lines = [
        "# Voynich Neural Integration Master",
        "",
        "## Scope",
        "",
        f"- Indexed documents in the neural field: `{len(docs)}`",
        "- Neural field size: `16` document-nodes",
        "- Cross-synthesis surface: `16 x 16 = 256` node permutations",
        "- Elemental re-read surface: one neutral pass plus four elemental `64`-observation matrices",
        "- Information re-read surface: one explicit information `64`-observation matrix plus topology, metro, and zero-point files",
        "- Higher-order synthesis surface: the full `15`-synthesis crystal lattice",
        "",
        "## Neutral Deep Synthesis",
        "",
        "At neutral resolution, the full Voynich corpus behaves like one layered nervous system. Root and NEW texts provide the thesis surface. EVA provides the witness bedrock. FRESH provides meta-manuscript recursion. The folio corpora instantiate the five books. Sections and crystals compress those books into reusable operators. Unified manuscripts and manifests hold replay and process memory. Framework and math files supply formal rigor. Chapter 11 and the synthesis layer then convert the achieved corpus into a next-dimensional seed. The deepest object is therefore not any single document, but the legal transit of evidence, operators, and compressed meaning across this whole field.",
        "",
        "## Information-Theoretic Deepening",
        "",
        "The second pass clarifies that the neural field is not flat. N05 through N09 are payload-dense, entropy-generating regions. N10 and N11 are the principal entropy-relief and topology-preservation surfaces. N12 packages ordered meaning. N13 through N15 stabilize the runtime, proof, and replay conditions. N16 is the only lawful lift zone, because it is the one place where compressed topology, live process memory, proof discipline, and package integrity meet. The information layer therefore turns the first-pass network from a conceptual graph into a transport law: what can move, where it can move, what must stay dense, and what is allowed to compress.",
        "",
        "## Node Summary",
        "",
        "| Node | Count | Primary Role | Information Role |",
        "| --- | --- | --- | --- |",
    ]
    for code in sorted(NODE_META):
        meta = NODE_META[code]
        info = INFO_META[code]
        lines.append(f"| {code} | {len(buckets.get(code, []))} | {meta['desc']} | {info['role']} |")
    lines.extend(
        [
            "",
            "## The Full 15 Syntheses",
            "",
            "### Singles",
            "- Fire: the corpus is a machine of transformation and final medicine.",
            "- Water: the corpus is a machine of circulation and admissibility.",
            "- Air: the corpus is a machine of timing, address, and symbolic legality.",
            "- Earth: the corpus is a machine of containment, routing, proof, and durable structure.",
            "",
            "### Pairs",
            "- Fire x Water: transformation survives only as repeatable convergence.",
            "- Fire x Air: transformation becomes lawful only at the right address.",
            "- Fire x Earth: potency becomes medicine only when bounded and certified.",
            "- Water x Air: purification becomes intelligent when phase-locked to a scheduler.",
            "- Water x Earth: circulation becomes infrastructure when routes are legal.",
            "- Air x Earth: a scheduler becomes civilization when every address has a lawful destination.",
            "",
            "### Triples",
            "- Fire x Water x Air: a living reaction grammar exists, but without Earth it cannot yet scale safely.",
            "- Fire x Water x Earth: a contained purification machine exists, but without Air it cannot know when to run.",
            "- Fire x Air x Earth: a timed contained machine exists, but without Water it cannot converge.",
            "- Water x Air x Earth: a scheduled routed purification world exists, but without Fire it lacks payload.",
            "",
            "### Omega",
            "- Fire x Water x Air x Earth: the full document field resolves as a helical manuscript civilization whose deepest unit is the admissible bridge.",
            "",
            "## Second-Pass Escalation Report",
            "",
            "- Prior weak gates: information roles were implicit, entropy zones were unnamed, and compression law was underspecified.",
            "- Newly promoted gates: explicit information topology, node-level handoff law, information-specific metro routing, and information-aware skill routing.",
            "- Remaining unresolved gates: literal live Google Docs search remains blocked by missing OAuth credentials, so the information layer is grounded in the local corpus only.",
            "- Next frontier: use the information layer to refine the whole-manuscript package and the next-dimensional seed bundle.",
            "",
            "## Zero Point",
            "",
            "The new neural network says the corpus is complete enough to be read as a self-routing, self-compressing manuscript machine. The deeper second pass adds that every document also belongs to an information class: witness, payload, compression, topology, package, runtime, proof, or seed. The corpus becomes deepest when those classes are routed lawfully rather than blended casually.",
            "",
            "## Linked Outputs",
            "",
            "- `DOCUMENT_FIELD_ATLAS.md`",
            "- `DOCUMENT_NODE_REGISTRY_16.md`",
            "- `PERMUTATION_MATRIX_16X16.md`",
            "- `SECOND_PASS_INFORMATION_DELTA.md`",
            "- `METRO_MAP_L1.md`",
            "- `METRO_MAP_L2_EMERGENT.md`",
            "- `METRO_MAP_L3_NEURAL.md`",
            "- `METRO_MAP_L4_TRANSCENDENT.md`",
            "- `APPENDIX_CRYSTAL_SKELETON.md`",
            "- `NEURAL_SKILL_PIPELINE.md`",
            "- `INFORMATION/INFORMATION_OBSERVATION_MATRIX_64.md`",
            "- `INFORMATION/INFORMATION_TOPOLOGY.md`",
            "- `INFORMATION/INFORMATION_METRO_MAP.md`",
            "- `INFORMATION/INFORMATION_ZERO_POINT.md`",
        ]
    )
    return "\n".join(lines)


def build_metro(name: str, lines_data: List[Tuple[str, str, str, str]], hubs: List[Tuple[str, str]], zero: str) -> str:
    body = [
        f"# {name}",
        "",
        "| Line | Stations | Topology | Meaning |",
        "| --- | --- | --- | --- |",
    ]
    body.extend(f"| {a} | {b} | {c} | {d} |" for a, b, c, d in lines_data)
    body.extend(["", "## Hubs", ""])
    body.extend(f"- `{hub}` = {desc}" for hub, desc in hubs)
    body.extend(["", "## Zero Point", "", zero])
    return "\n".join(body)


def build_appendix() -> str:
    rows = [
        ("A", "Corpus Atlas", "Fire x Pulse", "index every document and its node membership"),
        ("B", "Node Ontology", "Fire x Rhythm", "define the 16-node document field"),
        ("C", "Permutation Proof Ledger", "Fire x Strike", "record the 16x16 cross-synthesis rules"),
        ("D", "Shadow and Failure Map", "Fire x Dance", "track blind spots, overreach, and brittle claims"),
        ("E", "Seed Compressor", "Water x Pulse", "compress the neural field into replayable kernels"),
        ("F", "Isomorphism Translation Table", "Water x Rhythm", "map node outputs across domain vocabularies"),
        ("G", "Convergence and Loop Law", "Water x Strike", "formalize circulation, settling, and bridge stability"),
        ("H", "Threshold and Constant Catalogue", "Water x Dance", "collect bounds, ratios, and admissibility thresholds"),
        ("I", "Embedding Protocol", "Air x Pulse", "state how one layer enters another without loss"),
        ("J", "Verbalization Guide", "Air x Rhythm", "translate formal, operational, and prose renderings"),
        ("K", "Execution Playbook", "Air x Strike", "specify how to run the neural field on future corpora"),
        ("L", "Validation and Replay Tests", "Air x Dance", "define replay, audit, and promotion gates"),
        ("M", "Field Guide", "Earth x Pulse", "give quick entry to any node, line, or hub"),
        ("N", "Metro Atlas", "Earth x Rhythm", "collect all route layers"),
        ("O", "Teaching Curriculum", "Earth x Strike", "turn the neural field into a staged learning sequence"),
        ("P", "Living Maintenance Protocol", "Earth x Dance", "define how the network evolves without incoherence"),
    ]
    lines = [
        "# Appendix Crystal Skeleton",
        "",
        "## A-P Grid",
        "",
        "| Appendix | Title | Slot | Purpose |",
        "| --- | --- | --- | --- |",
    ]
    lines.extend(f"| {a} | {b} | {c} | {d} |" for a, b, c, d in rows)
    lines.extend(
        [
            "",
            "## Appendix Q - Appendix-Only Metro Map",
            "",
            "| Line | Stations | Meaning |",
            "| --- | --- | --- |",
            "| Proof Spine | `A -> B -> C -> L -> P` | atlas, ontology, proof, validation, maintenance |",
            "| Compression Spine | `E -> G -> H -> Q` | seed, loop law, thresholds, appendix-level reseeding |",
            "| Translation Spine | `F -> I -> J -> K -> O` | translation, embedding, verbalization, execution, teaching |",
            "| Shadow Spine | `D -> H -> L -> P` | failure, thresholds, validation, repair |",
            "| Atlas Spine | `M -> N -> O -> P -> Q` | field guide, metro atlas, curriculum, maintenance, reseeding |",
        ]
    )
    return "\n".join(lines)


def build_skill_pipeline() -> str:
    return "\n".join(
        [
            "# Neural Skill Pipeline",
            "",
            "## Skill Family",
            "",
            "- [$voynich-neural-document-cartographer](/C:/Users/dmitr/.codex/skills/voynich-neural-document-cartographer/SKILL.md)",
            "- [$voynich-neural-permutation-engine](/C:/Users/dmitr/.codex/skills/voynich-neural-permutation-engine/SKILL.md)",
            "- [$voynich-neural-information-cartographer](/C:/Users/dmitr/.codex/skills/voynich-neural-information-cartographer/SKILL.md)",
            "- [$voynich-neural-metro-appendix-compiler](/C:/Users/dmitr/.codex/skills/voynich-neural-metro-appendix-compiler/SKILL.md)",
            "- [$voynich-neural-network-orchestrator](/C:/Users/dmitr/.codex/skills/voynich-neural-network-orchestrator/SKILL.md)",
            "",
            "## When To Use Them",
            "",
            "1. Use `voynich-neural-document-cartographer` when the corpus shifts and the field atlas must be rebuilt from actual files.",
            "2. Use `voynich-neural-permutation-engine` when a new deep synthesis pass is needed across the full 16-node surface.",
            "3. Use `voynich-neural-information-cartographer` when a second-pass information topology is needed: entropy, handoff law, compression, replay, and seed promotion.",
            "4. Use `voynich-neural-metro-appendix-compiler` when the route layers, appendix crystal, and higher-order packaging need to be regenerated.",
            "5. Use `voynich-neural-network-orchestrator` when the whole pipeline should run in order as one deliberate integration pass.",
            "",
            "## Why To Use Them",
            "",
            "- Use the cartographer because deep integration fails when the real document field is guessed instead of measured.",
            "- Use the permutation engine because the corpus is too large to cross-synthesize responsibly without a typed intermediate surface.",
            "- Use the information cartographer because synthesis becomes vague when no one names where entropy lives and where compression is lawful.",
            "- Use the metro and appendix compiler because routes and support structure are different products from raw synthesis.",
            "- Use the orchestrator because omission risk rises sharply once the workflow spans atlas, permutation, information, metro, appendix, and status layers.",
            "",
            "## Why This Split Exists",
            "",
            "The family is intentionally not one giant skill. Mapping the field, computing the cross-synthesis surface, isolating information duties, and compiling metro/appendix artifacts are different jobs with different failure modes.",
            "",
            "## Algorithmic Order",
            "",
            "cartograph -> classify -> count -> compress into 16 nodes -> compute 16x16 pair surface -> run elemental passes -> run information pass -> compute 15 syntheses -> emit metro layers -> emit appendix crystal -> update build status",
            "",
            "## Expanded Pipeline",
            "",
            "### Phase 1 - Intake and Atlas",
            "",
            "1. scan the full local corpus",
            "2. exclude generated neural outputs from the intake scan",
            "3. count files by type",
            "4. assign every file to one node in the 16-node registry",
            "5. write the document atlas and node registry",
            "",
            "### Phase 2 - Permutation Surface",
            "",
            "1. read the current node registry",
            "2. compute the full `16 x 16` node-pair surface",
            "3. derive one neutral full-field synthesis",
            "4. derive four elemental observation matrices",
            "5. derive the 15-synthesis crystal lattice",
            "",
            "### Phase 3 - Information Layer",
            "",
            "1. identify the information role of each node",
            "2. identify the entropy risk of each node",
            "3. name the lawful handoff route for each node",
            "4. state the compression duty for each node",
            "5. emit the information observation matrix, topology, metro map, and zero point",
            "",
            "### Phase 4 - Route and Support Layer",
            "",
            "1. emit level 1 base metro map",
            "2. emit level 2 emergent metro map",
            "3. emit level 3 neural-cluster metro map",
            "4. emit level 4 transcendent reseeding metro map",
            "5. emit appendix A-P crystal skeleton",
            "6. emit appendix Q appendix-only metro map",
            "",
            "### Phase 5 - Registry and Replay",
            "",
            "1. validate any new skills",
            "2. update corpus build status",
            "3. preserve the live-docs gate result honestly",
            "4. keep the neural layer discoverable from the project surface",
            "",
            "## Guardrails",
            "",
            "- never skip the atlas phase and jump straight to synthesis",
            "- never flatten all metro layers into one mixed-resolution file",
            "- never invent live-docs access if the OAuth gate is blocked",
            "- never treat generated abstractions as replacements for authoritative folios and crystals",
            "- never compress witness-heavy nodes with the same aggression used for crystal or package nodes",
        ]
    )


def main() -> None:
    docs = rel_docs()
    buckets, ext = node_counts(docs)
    write(OUT / "README.md", build_root_readme())
    write(OUT / "DOCUMENT_FIELD_ATLAS.md", build_atlas(docs, buckets, ext))
    write(OUT / "DOCUMENT_NODE_REGISTRY_16.md", build_registry(buckets))
    write(OUT / "PERMUTATION_MATRIX_16X16.md", build_permutation_matrix())
    write(OUT / "MASTER_NEURAL_SYNTHESIS.md", build_master_synthesis(buckets, docs))
    write(OUT / "SECOND_PASS_INFORMATION_DELTA.md", build_second_pass_delta())
    write(OUT / "METRO_MAP_L1.md", build_metro("Level 1 Metro Map", [
        ("Source Line", "N01 -> N02 -> N03 -> N05", "linear", "canon into witness into plant activation"),
        ("Clock Line", "N03 -> N06 -> N10 -> N11", "linear", "witness into schedule into synthesis into crystal"),
        ("Bathhouse Line", "N05 -> N07 -> N10 -> N11", "linear", "matter into circulation into synthesis into crystal"),
        ("District Line", "N07 -> N08 -> N11 -> N12", "linear", "bathhouse into routing into crystal into packaging"),
        ("Formulation Line", "N05 -> N09 -> N11 -> N12", "linear", "payload into formula into crystal into manuscript"),
        ("Helix Line", "N04 -> N14 -> N16 -> N12", "open-helical", "meta-seed, math, synthesis, packaging"),
    ], [("N10", "section hub"), ("N11", "crystal hub"), ("N16", "meta-engine hub")], "N11 is the first stable center because it is where book-level compression becomes whole-corpus readability."))
    write(OUT / "METRO_MAP_L2_EMERGENT.md", build_metro("Level 2 Emergent Metro Map", [
        ("Witness Honesty Line", "N03 -> N08 -> N15 -> N16", "open", "truth survives by preserving structural gaps"),
        ("Compression Line", "N04 -> N11 -> N16 -> N12", "linear", "seed to crystal to meta-seed to manuscript"),
        ("Runtime Line", "N13 -> N15 -> N16", "linear", "framework and manifests become meta-engine"),
        ("Civilization Line", "N06 -> N07 -> N08 -> N09", "linear", "time, bathhouse, routing, formulation"),
        ("Pedagogy Line", "N05 -> N10 -> N11 -> N12", "linear", "folio to section to crystal to packaged teaching"),
    ], [("N16", "meta-engine + synthesis hub"), ("N11", "compression hub")], "N16 becomes the emergent center because it is where the corpus starts reading itself as the next seed."))
    write(OUT / "METRO_MAP_L3_NEURAL.md", build_metro("Level 3 Neural Metro Map", [
        ("Activation Cluster", "N05 N09 N14", "cluster", "payload, formulation, and math intensification"),
        ("Circulation Cluster", "N04 N07 N10 N11", "cluster", "meta-seed, bathhouse, synthesis, crystal circulation"),
        ("Address Cluster", "N02 N03 N06 N13 N15", "cluster", "working corpus, witness, schedule, framework, runtime"),
        ("Containment Cluster", "N08 N11 N12 N15 N16", "cluster", "routing, crystal, unified package, manifest, synthesis"),
    ], [("N11", "compression neuron"), ("N16", "meta-neuron")], "At neural resolution the center is the N11/N16 dyad: compressed crystal plus self-reading synthesis."))
    write(OUT / "METRO_MAP_L4_TRANSCENDENT.md", build_metro("Level 4 Transcendent Metro Map", [
        ("Seed -> Witness -> Crystal -> Seed", "N04 -> N03 -> N11 -> N16 -> N04*", "helical", "the corpus becomes its next seed"),
        ("Matter -> Time -> Purification -> Route -> Formula", "N05 -> N06 -> N07 -> N08 -> N09", "helical", "the five-book theorem rendered as node transit"),
        ("Framework -> Runtime -> Meta-Engine -> Package", "N13 -> N15 -> N16 -> N12", "helical", "the system learns to host itself"),
        ("Atlas -> Permutation -> Metro -> Appendix -> Seed", "N16 -> N16 -> N16 -> N16 -> N04*", "helical", "the synthesis layer folds back into reusable manuscript generation"),
    ], [("N16", "transcendent reseeding hub"), ("N04*", "virtual re-entry seed")], "The transcendent center is the orbit N11 -> N16 -> N04*: crystal, synthesis, reseeding."))
    write(OUT / "APPENDIX_CRYSTAL_SKELETON.md", build_appendix())
    write(OUT / "NEURAL_SKILL_PIPELINE.md", build_skill_pipeline())
    for element in ["FIRE", "WATER", "AIR", "EARTH"]:
        write(OUT / element / "README.md", f"# {element} Folder\n\nThis folder contains the {element.lower()}-dominant neural view of the full corpus.\n")
        write(OUT / element / "OBSERVATION_MATRIX_64.md", build_element_doc(element.title()))
    write(OUT / "INFORMATION" / "README.md", build_information_readme())
    write(OUT / "INFORMATION" / "INFORMATION_OBSERVATION_MATRIX_64.md", build_information_matrix(buckets))
    write(OUT / "INFORMATION" / "INFORMATION_TOPOLOGY.md", build_information_topology(buckets))
    write(OUT / "INFORMATION" / "INFORMATION_METRO_MAP.md", build_information_metro())
    write(OUT / "INFORMATION" / "INFORMATION_ZERO_POINT.md", build_information_zero())
    print(f"Wrote neural network bundle to {OUT}")


if __name__ == "__main__":
    main()
