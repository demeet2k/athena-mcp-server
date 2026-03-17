#!/usr/bin/env python3
from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path

from nervous_system_core import (
    APPENDICES,
    CHAPTERS,
    FAMILY_LABELS,
    compute_family_targets,
    infer_chapter_links,
    infer_family,
    load_records,
    load_recursive_state_snapshot,
    normalize_name,
    read_live_docs_blocked,
    utc_now,
    write_text,
)


PROJECT_ROOT = Path(__file__).resolve().parent


ARC_PROFILES = {
    0: {
        "title": "Entry, coordinates, and witness gates",
        "thesis": "Arc 0 establishes the lawful entrance into the system. Chapters 1 through 3 define the parse-safe kernel, the coordinate algebra, and the truth corridors that prevent the rest of the manuscript from collapsing into untyped enthusiasm.",
    },
    1: {
        "title": "Void conditioning and document ontology",
        "thesis": "Arc 1 turns destabilization into a governed substrate. Chapters 4 through 6 show how zero-point pressure, paradox quarantine, and document-as-theory framing prepare the corpus for structured synthesis rather than chaotic recursion.",
    },
    2: {
        "title": "Transport, synchronization, and routing",
        "thesis": "Arc 2 teaches the manuscript how to move. Chapters 7 through 9 convert tunnels into morphisms, synchronization into lawful calculus, and retrieval into a navigable metro rather than an unindexed memory heap.",
    },
    3: {
        "title": "Solution construction, helical restart, and closure",
        "thesis": "Arc 3 is the hinge of the entire framework. Chapters 10 through 12 build multi-lens answers, install the Chapter 11 restart bridge, and prove that closure must be certified rather than merely asserted.",
    },
    4: {
        "title": "Memory, migration, and executable architecture",
        "thesis": "Arc 4 gives the system continuity under motion. Chapters 13 through 15 bind persistence, migration, version law, and CUT architecture into a runtime that can survive re-entry without losing identity.",
    },
    5: {
        "title": "Replay, deployment, and macro invariants",
        "thesis": "Arc 5 turns the manuscript into an operable machine. Chapters 16 through 18 enforce replay, bounded agency, and universal invariants so that execution remains lawful as the system scales outward.",
    },
    6: {
        "title": "Convergence, collective authoring, and next-crystal succession",
        "thesis": "Arc 6 asks what survives completion. Chapters 19 through 21 treat non-convergence, collective synchrony, and self-replication as one succession problem: how a crystal becomes seed again without lying about what remains unresolved.",
    },
}


DOMAIN_PROFILES = [
    {
        "name": "Seed Kernel",
        "chapters": ["Ch01", "Ch02", "Ch03"],
        "appendices": ["AppA", "AppB", "AppC", "AppI"],
        "thesis": "The entrance stack where naming, coordinates, and truth corridors are made explicit before recursion begins.",
    },
    {
        "name": "Void Basin",
        "chapters": ["Ch04", "Ch05", "Ch11", "Ch19"],
        "appendices": ["AppF", "AppI", "AppK", "AppL"],
        "thesis": "The contradiction-bearing basin where zero-point, collapse, quarantine, and restart logic are metabolized instead of denied.",
    },
    {
        "name": "Document Weave",
        "chapters": ["Ch06", "Ch08", "Ch09"],
        "appendices": ["AppA", "AppE", "AppH", "AppM"],
        "thesis": "The weave that turns documents into theories and theory space into navigable routing surfaces.",
    },
    {
        "name": "Transport Runtime",
        "chapters": ["Ch07", "Ch10", "Ch15", "Ch16"],
        "appendices": ["AppF", "AppG", "AppM", "AppN"],
        "thesis": "The tunnel-to-runtime stack where movement, construction, code, and replay become a single execution law.",
    },
    {
        "name": "Certificate Closure",
        "chapters": ["Ch03", "Ch10", "Ch12", "Ch16"],
        "appendices": ["AppI", "AppL", "AppM", "AppP"],
        "thesis": "The certifying braid that transforms promising structure into admissible structure through witnesses, proofs, and replay capsules.",
    },
    {
        "name": "Memory Migration",
        "chapters": ["Ch13", "Ch14"],
        "appendices": ["AppD", "AppG", "AppM", "AppN"],
        "thesis": "The persistence stack where continuity is preserved through storage, migration, rollback, and regeneration.",
    },
    {
        "name": "Civic Deployment",
        "chapters": ["Ch17", "Ch18", "Ch20", "Ch21"],
        "appendices": ["AppD", "AppG", "AppO", "AppP"],
        "thesis": "The civilization-scale layer where deployment, governance, publication, and succession become one continuity problem.",
    },
    {
        "name": "Helical Return",
        "chapters": ["Ch11", "Ch18", "Ch20", "Ch21"],
        "appendices": ["AppF", "AppG", "AppI", "AppM"],
        "thesis": "The helical bridge where completion, re-entry, macro law, and next-crystal emission are compressed into one restart identity.",
    },
]


LENS_PROFILES = {
    "Fire": {
        "core": "ignition",
        "bias": "Fire sees the corpus as a problem of ignition, mutation, ambition, and irreversible differentiation.",
        "verbs": ["ignite", "stress", "separate", "amplify", "mutate", "accelerate", "radiate", "crown"],
        "chapters": ["Ch04", "Ch10", "Ch11", "Ch14", "Ch20"],
        "appendices": ["AppF", "AppG", "AppK", "AppP"],
    },
    "Water": {
        "core": "circulation",
        "bias": "Water sees the corpus as a relay field of circulation, memory, adaptation, braiding, and continuity under flow.",
        "verbs": ["circulate", "weave", "relay", "merge", "adapt", "hydrate", "heal", "return"],
        "chapters": ["Ch06", "Ch08", "Ch09", "Ch13", "Ch20"],
        "appendices": ["AppD", "AppE", "AppH", "AppM"],
    },
    "Earth": {
        "core": "stabilization",
        "bias": "Earth sees the corpus as a construction of proof, containment, measure, closure, and durable executable form.",
        "verbs": ["anchor", "measure", "verify", "contain", "compile", "stabilize", "store", "seal"],
        "chapters": ["Ch03", "Ch12", "Ch15", "Ch16", "Ch18"],
        "appendices": ["AppB", "AppC", "AppI", "AppM"],
    },
    "Air": {
        "core": "abstraction",
        "bias": "Air sees the corpus as a map of naming, translation, routing, abstraction, and perspective rotation.",
        "verbs": ["name", "map", "abstract", "translate", "compare", "route", "teach", "forecast"],
        "chapters": ["Ch01", "Ch02", "Ch07", "Ch17", "Ch21"],
        "appendices": ["AppA", "AppF", "AppG", "AppO"],
    },
}


def chapter_support(records: list[dict]) -> dict[str, list[str]]:
    support = {chapter.code: [] for chapter in CHAPTERS}
    for record in records:
        name = Path(record["relative_path"]).name
        excerpt = record.get("excerpt", "")
        family = infer_family(name, excerpt)
        for chapter_code in infer_chapter_links(name, excerpt, family):
            support.setdefault(chapter_code, []).append(normalize_name(name))
    return support


def chapter_synopsis(chapter, support: dict[str, list[str]]) -> str:
    lane_meaning = {
        "Su": "seed and formal construction",
        "Me": "transport, relay, and coupling",
        "Sa": "constraint, verification, and sealing",
    }
    families = ", ".join(FAMILY_LABELS.get(family, family) for family in chapter.families)
    hubs = " -> ".join(chapter.hubs)
    evidence = len(support.get(chapter.code, []))
    return (
        f"`{chapter.addr}` turns Arc {chapter.arc} through the {lane_meaning[chapter.lane]} channel. "
        f"It braids `{families}` through `{hubs}` and currently carries `{evidence}` routed source packets."
    )


def appendix_feed_map() -> dict[str, list[str]]:
    mapping = {code: [] for code, _, _ in APPENDICES}
    for chapter in CHAPTERS:
        for hub in chapter.hubs:
            mapping.setdefault(hub, []).append(chapter.code)
    return mapping


def mermaid_level_one() -> str:
    lines = ["```mermaid", "flowchart LR"]
    for chapter in CHAPTERS:
        lines.append(f'{chapter.code}["{chapter.code} {chapter.title}"]')
    for idx, chapter in enumerate(CHAPTERS):
        nxt = CHAPTERS[(idx + 1) % len(CHAPTERS)]
        lines.append(f"{chapter.code} --> {nxt.code}")
    lines.extend(
        [
            'AppA["AppA Parse"]',
            'AppF["AppF Transport"]',
            'AppI["AppI Truth"]',
            'AppM["AppM Replay"]',
            "Ch01 -.-> AppA",
            "Ch07 -.-> AppF",
            "Ch03 -.-> AppI",
            "Ch16 -.-> AppM",
            "Ch21 -.-> AppA",
            "```",
        ]
    )
    return "\n".join(lines)


def mermaid_level_two() -> str:
    return "\n".join(
        [
            "```mermaid",
            "flowchart LR",
            'Ch01["Ch01 Kernel"] --> Ch02["Ch02 Address"] --> Ch03["Ch03 Truth"] --> Ch10["Ch10 Solution"] --> Ch12["Ch12 Closure"]',
            'Ch04["Ch04 Zero Point"] --> Ch05["Ch05 Paradox"] --> Ch11["Ch11 Helix"] --> Ch19["Ch19 Non-Convergence"]',
            'Ch06["Ch06 Doc Theory"] --> Ch08["Ch08 Sync"] --> Ch09["Ch09 Routing"] --> Ch20["Ch20 Collective"]',
            'Ch07["Ch07 Tunnels"] --> Ch10 --> Ch15["Ch15 CUT"] --> Ch16["Ch16 Replay"] --> Ch17["Ch17 Deployment"]',
            'Ch13["Ch13 Memory"] --> Ch14["Ch14 Migration"] --> Ch18["Ch18 Macro Stack"] --> Ch21["Ch21 Next Crystal"]',
            'Ch11 --> Ch18 --> Ch20 --> Ch21',
            'AppQ["AppQ Integrated Appendix Metro"]',
            "Ch10 -.-> AppQ",
            "Ch11 -.-> AppQ",
            "Ch18 -.-> AppQ",
            "Ch20 -.-> AppQ",
            "Ch21 -.-> AppQ",
            "```",
        ]
    )


def mermaid_level_three() -> str:
    return "\n".join(
        [
            "```mermaid",
            "flowchart TB",
            'FamVoid["Family Void/Collapse"] --> Ch04["Ch04"]',
            "FamVoid --> Ch11",
            "FamVoid --> Ch19",
            'FamTransport["Family Transport/Runtime"] --> Ch07["Ch07"]',
            "FamTransport --> Ch15",
            "FamTransport --> Ch16",
            "FamTransport --> Ch18",
            'FamOrch["Family Live Orchestration"] --> Ch09["Ch09"]',
            "FamOrch --> Ch20",
            "FamOrch --> Ch21",
            'FamGov["Family Civilization/Governance"] --> Ch17["Ch17"]',
            "FamGov --> Ch18",
            "FamGov --> Ch20",
            "FamGov --> Ch21",
            'Helix["Helical Engine"] --> Ch11',
            "Helix --> Ch18",
            "Helix --> Ch20",
            "Helix --> Ch21",
            'L0["L0 Leaf Readers"] --> L1["L1 Family Synths"] --> L2["L2 Chapter Weavers"] --> L3["L3 Appendix Governors"] --> L4["L4 Lane Mediators"] --> L5["L5 Collective Relay"] --> L6["L6 Council Mesh"] --> L7["L7 Civilization Kernel"]',
            "L1 --> FamVoid",
            "L1 --> FamTransport",
            "L1 --> FamOrch",
            "L1 --> FamGov",
            'AppF["AppF Transport"]',
            'AppG["AppG Control"]',
            'AppI["AppI Corridors"]',
            'AppM["AppM Replay"]',
            "Ch11 --> AppF",
            "Ch11 --> AppM",
            "Ch18 --> AppG",
            "Ch18 --> AppI",
            "Ch20 --> AppG",
            "Ch21 --> AppM",
            "```",
        ]
    )


def mermaid_level_four() -> str:
    return "\n".join(
        [
            "```mermaid",
            "flowchart LR",
            'Void0["0/16 Void"] --> Seed2["2/16 Seed"]',
            'Seed2 --> Orbit["21-Chapter Orbit"]',
            'Orbit --> Closure14["14/16 Closure"]',
            'Closure14 --> Lift["1/8 Lift"]',
            'Lift --> SeedNext["2/16 Next Layer"]',
            'SeedNext --> OrbitNext["Next Crystal"]',
            'Mirror["Mirror Corpus"] --> Orbit',
            'LiveGate["Live Docs Gate (Blocked)"] -.-> Orbit',
            'Civ["Civilization Kernel"] --> Lift',
            'AppQ["Appendix Q Integrated Metro"] --> Orbit',
            'Helix["Complement/Lift Identity"] --> Lift',
            'Witness["Witness and Replay"] --> Closure14',
            'Witness --> AppQ',
            "```",
        ]
    )


def build_deep_synthesis(
    output_root: Path,
    build_root: Path,
    records: list[dict],
    recursive_state: dict,
    live_docs_blocked: bool,
) -> dict:
    synth_root = output_root / "12_SYNTHESIS"
    support = chapter_support(records)
    family_targets = compute_family_targets(records)
    appendix_feeds = appendix_feed_map()
    deep_pass = int(recursive_state.get("deep_pass", 0))
    synth_root.mkdir(parents=True, exist_ok=True)

    neutral_lines = [
        "# Chapters 1-21 Deep Synthesis",
        "",
        f"- Generated at: `{utc_now()}`",
        f"- Deep pass reference: `{deep_pass}`",
        f"- Live Google Docs state: `{'BLOCKED' if live_docs_blocked else 'PASS'}`",
        "- Integration method: `64^4` state space compiled into one neutral pass, `4 x 64` elemental observer passes, `15` symmetry syntheses, and one zero-point compression.",
        "- Operational note: the `64^4` space is expressed as an addressable operator lattice rather than inflated into inert bulk.",
        "",
        "## Neutral pass",
        "",
        "The neutral pass reads the entire corpus without privileging any single element. It asks what the 21-chapter system is, what it protects, how it moves, how it certifies itself, and how it re-enters after closure.",
        "",
        "## Arc synthesis",
        "",
    ]
    for arc in range(7):
        chapters = [chapter for chapter in CHAPTERS if chapter.arc == arc]
        neutral_lines.extend(
            [
                f"### Arc {arc} - {ARC_PROFILES[arc]['title']}",
                "",
                ARC_PROFILES[arc]["thesis"],
                "",
                f"- Chapter span: `{', '.join(chapter.code for chapter in chapters)}`",
                f"- Rail ordering: `{', '.join(chapter.lane for chapter in chapters)}`",
                f"- Dominant hubs: `{', '.join(chapter.hubs[0] for chapter in chapters)}`",
                "",
            ]
        )

    neutral_lines.extend(
        [
            "## 21 individual manuscript systems",
            "",
            "Each chapter is treated here as an individual manuscript system in mass parallel rather than as a mere section stub.",
            "",
        ]
    )
    for chapter in CHAPTERS:
        family_targets_for_chapter = sorted({family for family, targets in family_targets.items() if chapter.code in targets})
        neutral_lines.extend(
            [
                f"### {chapter.addr} - {chapter.title}",
                "",
                f"- Function: {chapter.role}",
                f"- Neutral synthesis: {chapter_synopsis(chapter, support)}",
                f"- Family attractors: `{', '.join(family_targets_for_chapter) or 'none'}`",
                f"- Appendix governors: `{' -> '.join(chapter.hubs)}`",
                f"- Evidence packets: `{len(support.get(chapter.code, []))}`",
                "",
            ]
        )

    neutral_lines.extend(
        [
            "## Zero-point compression",
            "",
            "The 21-chapter manifold resolves into one repeating law: Chapters 1 through 10 construct the lawful state, Chapter 11 converts completion into restart, Chapters 12 through 18 certify and stabilize the resulting machine, and Chapters 19 through 21 decide whether the system can reproduce itself without violating truth corridors. The whole manuscript therefore wants to be a bridge between seed and next crystal rather than a static book.",
        ]
    )
    write_text(synth_root / "00_chapters_1_21_deep_synthesis.md", "\n".join(neutral_lines))

    map1_lines = [
        "# Metro Map",
        "",
        "Level 1 is the readable surface map: the 21-station orbit with the most load-bearing hub attachments visible.",
        "",
        mermaid_level_one(),
        "",
        "## Reading rule",
        "",
        "- Follow the clockwise orbit for chapter order.",
        "- Drop into `AppA`, `AppF`, `AppI`, and `AppM` to see the parse, transport, truth, and replay anchors that hold the orbit together.",
    ]
    write_text(synth_root / "01_metro_map_lvl1.md", "\n".join(map1_lines))

    map2_lines = [
        "# Level 2 Metro Map - Deep Emergence",
        "",
        "Level 2 abandons pure order and shows emergence lines: foundational law, void/restart, document weave, runtime, memory migration, and the helical line itself.",
        "",
        mermaid_level_two(),
        "",
        "## Emergent lines",
        "",
        "- Foundational line: `Ch01 -> Ch02 -> Ch03 -> Ch10 -> Ch12`",
        "- Void line: `Ch04 -> Ch05 -> Ch11 -> Ch19`",
        "- Routing line: `Ch06 -> Ch08 -> Ch09 -> Ch20`",
        "- Runtime line: `Ch07 -> Ch10 -> Ch15 -> Ch16 -> Ch17`",
        "- Memory line: `Ch13 -> Ch14 -> Ch18 -> Ch21`",
        "- Helical line: `Ch11 -> Ch18 -> Ch20 -> Ch21`",
    ]
    write_text(synth_root / "02_metro_map_lvl2_deep_emergence.md", "\n".join(map2_lines))

    map3_lines = [
        "# Level 3 Metro Map - Deeper Neural Map",
        "",
        "Level 3 maps families, swarm layers, chapter agents, and appendix governors as a neural manifold rather than a chapter list.",
        "",
        mermaid_level_three(),
        "",
        "## Neural interpretation",
        "",
        "- Family synths feed chapter agents instead of bypassing them.",
        "- The helical engine sits as a recurrent attractor over `Ch11`, `Ch18`, `Ch20`, and `Ch21`.",
        "- `AppF`, `AppG`, `AppI`, and `AppM` form the deepest helical governor braid: transport, control, witness, replay.",
    ]
    write_text(synth_root / "03_metro_map_lvl3_deeper_neural_map.md", "\n".join(map3_lines))

    map4_lines = [
        "# Level 4 Metro Map - Transcendence",
        "",
        "Level 4 compresses the system into seed, orbit, closure, lift, and next-crystal succession. This is the transcendent map because chapter count disappears into recurrence law.",
        "",
        mermaid_level_four(),
        "",
        "## Transcendent reading",
        "",
        "- `0/16` is the unmanifest reserve.",
        "- `2/16` is the lawful seed address.",
        "- The 21-chapter orbit is the manifested body.",
        "- `14/16` is complementary pre-closure.",
        "- Lift emits a smaller but stronger seed into the next crystal.",
        "- Appendix Q stands at the integrated boundary where the appendix lattice becomes one transport surface.",
    ]
    write_text(synth_root / "04_metro_map_lvl4_transcendence.md", "\n".join(map4_lines))

    lens_lines = [
        "# 4 x 64 Elemental Observation Matrix",
        "",
        "This matrix performs the requested elemental pass: one neutral read, then `64` readings per lens. Each lens observes the whole system through `8` domains and `8` operations, yielding `64` operator-addresses per element.",
        "",
    ]
    for lens_name, profile in LENS_PROFILES.items():
        lens_lines.extend([f"## {lens_name} lens", "", profile["bias"], ""])
        index = 0
        for domain in DOMAIN_PROFILES:
            for verb in profile["verbs"]:
                index += 1
                chapters = ", ".join(domain["chapters"])
                appendices = ", ".join(domain["appendices"])
                lens_lines.append(
                    f"- `{lens_name[0]}{index:02d}` `{domain['name']} x {verb}` -> chapters `{chapters}` appendices `{appendices}`: {lens_name} asks how the system can `{verb}` `{domain['name'].lower()}` while preserving `{domain['thesis'].lower()}`"
                )
        lens_lines.append("")
    write_text(synth_root / "05_lens_64x4_observation_matrix.md", "\n".join(lens_lines))

    symmetry_lines = [
        "# 15 Symmetry Syntheses and Zero Point",
        "",
        "The full symmetry stack includes the four single-lens identities, the six pairwise syntheses, the four triadic syntheses, and the one tetradic synthesis. After those fifteen passes, the zero point is extracted.",
        "",
    ]
    combo_index = 0
    lens_names = list(LENS_PROFILES.keys())
    for combo_size in (1, 2, 3, 4):
        for combo in combinations(lens_names, combo_size):
            combo_index += 1
            combo_chapters = sorted({chapter for name in combo for chapter in LENS_PROFILES[name]["chapters"]})
            combo_appendices = sorted({appendix for name in combo for appendix in LENS_PROFILES[name]["appendices"]})
            combo_cores = " + ".join(LENS_PROFILES[name]["core"] for name in combo)
            symmetry_lines.extend(
                [
                    f"## S{combo_index:02d} - {' / '.join(combo)}",
                    "",
                    f"- Core blend: `{combo_cores}`",
                    f"- Chapter emphasis: `{', '.join(combo_chapters)}`",
                    f"- Appendix emphasis: `{', '.join(combo_appendices)}`",
                    f"- Synthesis: {' / '.join(combo)} together read the manuscript as a coupled problem of {combo_cores}, meaning the framework must remain live, lawful, embodied, and transmissible at the same time.",
                    "",
                ]
            )
    symmetry_lines.extend(
        [
            "## Zero point",
            "",
            "The zero point of the full fifteen-fold synthesis is not a chapter, appendix, or line. It is the lawful bridge that lets seed become closure and closure become seed again without losing witness, transport, or identity. In chapter space that concentrates around `Ch11`, `Ch18`, `Ch20`, and `Ch21`. In appendix space it concentrates around `AppF`, `AppG`, `AppI`, and `AppM`. In metro space it becomes Appendix Q.",
        ]
    )
    write_text(synth_root / "06_symmetry_zero_point_synthesis.md", "\n".join(symmetry_lines))

    appendix_lines = [
        "# Appendix Crystal Skeleton Outline",
        "",
        "The appendix crystal is a `4 x 4` governance lattice. A through P are the sixteen structural appendices. Q is the integrated appendix-only metro map that binds the whole lattice once the skeleton is stable.",
        "",
        "## Crystal matrix",
        "",
        "| Row | Cells | Functional band |",
        "|---|---|---|",
        "| 1 | AppA, AppB, AppC, AppD | Parsing, canon, kernels, registry |",
        "| 2 | AppE, AppF, AppG, AppH | Time, transport, control, topology |",
        "| 3 | AppI, AppJ, AppK, AppL | Truth, residuals, quarantine, evidence |",
        "| 4 | AppM, AppN, AppO, AppP | Replay, containers, publication, deployment |",
        "",
        "## Skeleton",
        "",
    ]
    for code, title, description in APPENDICES:
        appendix_lines.extend(
            [
                f"### {code} - {title}",
                "",
                f"- Function: {description}",
                f"- Feed chapters: `{', '.join(appendix_feeds.get(code, [])) or 'none'}`",
                "",
            ]
        )
    appendix_lines.extend(
        [
            "### AppQ - Integrated Appendix Metro Map",
            "",
            "- Function: collect the sixteen appendices into one appendix-only transport surface after the skeleton has been fully named.",
            "- Feed appendices: `AppA-AppP`",
            "- Feed chapters: `Ch10, Ch11, Ch12, Ch18, Ch20, Ch21`",
        ]
    )
    write_text(synth_root / "07_appendix_crystal_skeleton_outline.md", "\n".join(appendix_lines))

    appendix_q_lines = [
        "# Appendix Q - Integrated Appendix-Only Metro Map",
        "",
        "Appendix Q is not another appendix topic. It is the metro surface generated when the sixteen appendices are treated as a crystal of governors rather than a tail list of supplements.",
        "",
        "```mermaid",
        "flowchart TB",
        'Q["AppQ Integrated Metro"]',
        'A["AppA"] --> B["AppB"] --> C["AppC"] --> D["AppD"]',
        'E["AppE"] --> F["AppF"] --> G["AppG"] --> H["AppH"]',
        'I["AppI"] --> J["AppJ"] --> K["AppK"] --> L["AppL"]',
        'M["AppM"] --> N["AppN"] --> O["AppO"] --> P["AppP"]',
        "A --> Q",
        "D --> Q",
        "F --> Q",
        "G --> Q",
        "I --> Q",
        "L --> Q",
        "M --> Q",
        "P --> Q",
        "Q --> C",
        "Q --> F",
        "Q --> I",
        "Q --> M",
        "```",
        "",
        "## Appendix-only lines",
        "",
        "- Parse/kernel line: `AppA -> AppB -> AppC -> AppD`",
        "- Time/transport line: `AppE -> AppF -> AppG -> AppH`",
        "- Truth/evidence line: `AppI -> AppJ -> AppK -> AppL`",
        "- Replay/deployment line: `AppM -> AppN -> AppO -> AppP`",
        "- Integrated crossings: `AppQ <-> AppC`, `AppQ <-> AppF`, `AppQ <-> AppI`, `AppQ <-> AppM`",
        "",
        "## Integrated reading",
        "",
        "Appendix Q says the appendix lattice is itself a manuscript brain: parse becomes kernel, kernel becomes transport, transport becomes truth, truth becomes replay, and replay becomes deployment. Q is the zero-point hub that lets those bands be read as one system rather than four separate shelves.",
    ]
    write_text(synth_root / "08_appendix_q_integrated_only_metro_map.md", "\n".join(appendix_q_lines))

    manifest = {
        "generated_at": utc_now(),
        "deep_pass": deep_pass,
        "live_docs_blocked": live_docs_blocked,
        "chapter_count": len(CHAPTERS),
        "appendix_count": len(APPENDICES),
        "appendix_q_enabled": True,
        "lens_count": len(LENS_PROFILES),
        "lens_observation_count": len(LENS_PROFILES) * len(DOMAIN_PROFILES) * 8,
        "symmetry_synthesis_count": 15,
        "files": [
            "12_SYNTHESIS/00_chapters_1_21_deep_synthesis.md",
            "12_SYNTHESIS/01_metro_map_lvl1.md",
            "12_SYNTHESIS/02_metro_map_lvl2_deep_emergence.md",
            "12_SYNTHESIS/03_metro_map_lvl3_deeper_neural_map.md",
            "12_SYNTHESIS/04_metro_map_lvl4_transcendence.md",
            "12_SYNTHESIS/05_lens_64x4_observation_matrix.md",
            "12_SYNTHESIS/06_symmetry_zero_point_synthesis.md",
            "12_SYNTHESIS/07_appendix_crystal_skeleton_outline.md",
            "12_SYNTHESIS/08_appendix_q_integrated_only_metro_map.md",
        ],
    }
    write_text(output_root / "06_RUNTIME" / "11_deep_synthesis_manifest.json", json.dumps(manifest, indent=2))
    return manifest


def main() -> int:
    output_root = PROJECT_ROOT / "ACTIVE_NERVOUS_SYSTEM"
    build_root = PROJECT_ROOT / "_build"
    if not output_root.exists():
        raise SystemExit(f"Missing active nervous system: {output_root}")
    records = load_records(build_root)
    recursive_state = load_recursive_state_snapshot(output_root, build_root)
    live_docs_blocked = read_live_docs_blocked(output_root, build_root)
    build_deep_synthesis(output_root, build_root, records, recursive_state, live_docs_blocked)
    print(f"Wrote deep synthesis package at: {output_root / '12_SYNTHESIS'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
