#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from nervous_system_core import (
    APPENDICES,
    CHAPTERS,
    FAMILY_LABELS,
    clean_display_name,
    infer_appendix_links,
    infer_chapter_links,
    infer_family,
    load_records,
    load_recursive_state_snapshot,
    lookup_tokens,
    normalize_lookup_text,
    normalize_name,
    presentation_name,
    read_live_docs_blocked,
    slugify,
    utc_now,
    write_json,
    write_text,
)


PROJECT_ROOT = Path(__file__).resolve().parent
BUILD_ROOT = PROJECT_ROOT / "_build"
ACTIVE_ROOT = PROJECT_ROOT / "ACTIVE_NERVOUS_SYSTEM"
OUTPUT_ROOT = ACTIVE_ROOT / "13_DEEPER_NEURAL_NET"

OPERATOR_GATES = [
    ("G00", "Seed"),
    ("G01", "Parse"),
    ("G02", "Route"),
    ("G03", "Bridge"),
    ("G04", "Weave"),
    ("G05", "Kernel"),
    ("G06", "Proof"),
    ("G07", "Quarantine"),
    ("G08", "Replay"),
    ("G09", "Memory"),
    ("G10", "Migrate"),
    ("G11", "Compile"),
    ("G12", "Govern"),
    ("G13", "Publish"),
    ("G14", "Lift"),
    ("G15", "Teach"),
]

DOMAIN_PROFILES = [
    ("Seed Kernel", ["Ch01", "Ch02", "Ch03"], ["AppA", "AppB", "AppC", "AppI"], "the entrance stack where naming, coordinates, and truth corridors are made explicit before recursion begins"),
    ("Void Basin", ["Ch04", "Ch05", "Ch11", "Ch19"], ["AppF", "AppI", "AppK", "AppL"], "the contradiction-bearing basin where zero-point, collapse, quarantine, and restart logic are metabolized instead of denied"),
    ("Document Weave", ["Ch06", "Ch08", "Ch09"], ["AppA", "AppE", "AppH", "AppM"], "the weave that turns documents into theories and theory space into navigable routing surfaces"),
    ("Transport Runtime", ["Ch07", "Ch10", "Ch15", "Ch16"], ["AppF", "AppG", "AppM", "AppN"], "the tunnel-to-runtime stack where movement, construction, code, and replay become a single execution law"),
    ("Certificate Closure", ["Ch03", "Ch10", "Ch12", "Ch16"], ["AppI", "AppL", "AppM", "AppP"], "the certifying braid that transforms promising structure into admissible structure through witnesses, proofs, and replay capsules"),
    ("Memory Migration", ["Ch13", "Ch14"], ["AppD", "AppG", "AppM", "AppN"], "the persistence stack where continuity is preserved through storage, migration, rollback, and regeneration"),
    ("Civic Deployment", ["Ch17", "Ch18", "Ch20", "Ch21"], ["AppD", "AppG", "AppO", "AppP"], "the civilization-scale layer where deployment, governance, publication, and succession become one continuity problem"),
    ("Helical Return", ["Ch11", "Ch18", "Ch20", "Ch21"], ["AppF", "AppG", "AppI", "AppM"], "the helical bridge where completion, re-entry, macro law, and next-crystal emission are compressed into one restart identity"),
]

ELEMENTS = {
    "Fire": {
        "folder": "01_FIRE",
        "bias": "ignition, transformation, restart pressure, novelty, and irreversible differentiation",
        "verbs": ["ignite", "stress", "separate", "amplify", "mutate", "accelerate", "radiate", "crown"],
        "families": {"void-and-collapse", "helical-recursion-engine"},
        "keywords": {"void", "restart", "collapse", "paradox", "helical", "lift", "seed", "zero-point"},
        "gates": {"G00", "G03", "G07", "G14"},
    },
    "Water": {
        "folder": "02_WATER",
        "bias": "circulation, memory, relay, synchronization, weaving, and adaptive continuity",
        "verbs": ["circulate", "weave", "relay", "merge", "adapt", "hydrate", "heal", "return"],
        "families": {"live-orchestration", "manuscript-architecture"},
        "keywords": {"sync", "synchronization", "route", "metro", "memory", "migration", "collective", "weave", "mirror"},
        "gates": {"G02", "G04", "G08", "G09", "G10"},
    },
    "Earth": {
        "folder": "03_EARTH",
        "bias": "verification, kernels, containment, certificates, runtime solidity, and closure",
        "verbs": ["anchor", "measure", "verify", "contain", "compile", "stabilize", "store", "seal"],
        "families": {"transport-and-runtime", "civilization-and-governance"},
        "keywords": {"proof", "witness", "certificate", "legal", "verify", "runtime", "kernel", "closure"},
        "gates": {"G05", "G06", "G07", "G08", "G11", "G12"},
    },
    "Air": {
        "folder": "04_AIR",
        "bias": "addressing, abstraction, higher-dimensional mapping, symbol systems, and transmissible perspective",
        "verbs": ["name", "map", "abstract", "translate", "compare", "route", "teach", "forecast"],
        "families": {"higher-dimensional-geometry", "mythic-sign-systems", "identity-and-instruction"},
        "keywords": {"address", "symbol", "atlas", "holographic", "manifold", "lattice", "teach", "coordinate", "glyph"},
        "gates": {"G01", "G02", "G03", "G13", "G15"},
    },
}

STOPWORDS = {
    "the", "and", "that", "with", "from", "this", "into", "through", "where", "which", "chapter",
    "appendix", "document", "system", "framework", "manuscript", "these", "those", "while", "across",
}


def build_blob(record: dict) -> str:
    headings = " ".join(record.get("heading_candidates") or [])
    return f"{Path(record['relative_path']).name} {record.get('excerpt', '')} {headings}".lower()


def tokenize(blob: str) -> list[str]:
    tokens: list[str] = []
    for raw in blob.replace("/", " ").replace("_", " ").replace("-", " ").split():
        token = "".join(ch for ch in raw if ch.isalpha()).lower()
        if len(token) >= 5 and token not in STOPWORDS:
            tokens.append(token)
    return [token for token, _ in Counter(tokens).most_common(24)]


def gate_for_record(blob: str, family: str) -> str:
    score = Counter()
    keyword_map = {
        "G00": ["seed", "restart", "zero", "origin"],
        "G01": ["address", "parse", "grammar", "symbol"],
        "G02": ["route", "routing", "metro", "corridor"],
        "G03": ["bridge", "tunnel", "morphism", "transport"],
        "G04": ["sync", "synchronization", "weave", "collective"],
        "G05": ["kernel", "axiom", "invariant", "core"],
        "G06": ["proof", "witness", "certificate", "legal"],
        "G07": ["quarantine", "paradox", "conflict", "revocation"],
        "G08": ["replay", "verifier", "deterministic", "rerun"],
        "G09": ["memory", "persistence", "ledger", "history"],
        "G10": ["migration", "version", "rollback", "compat"],
        "G11": ["runtime", "cut", "compile", "code"],
        "G12": ["govern", "council", "civilization", "bounded"],
        "G13": ["publish", "deployment", "export", "import"],
        "G14": ["helical", "lift", "dimension", "14/16", "2/16"],
        "G15": ["athena", "teacher", "pedagogy", "story"],
    }
    for gate, terms in keyword_map.items():
        score[gate] += sum(1 for term in terms if term in blob)
    if family == "helical-recursion-engine":
        score["G14"] += 5
    if family == "transport-and-runtime":
        score["G11"] += 3
    if family == "civilization-and-governance":
        score["G12"] += 3
    if family == "identity-and-instruction":
        score["G15"] += 3
    return max(score, key=score.get) if score else "G05"


def assign_records(records: list[dict]) -> list[dict]:
    assigned: list[dict] = []
    for index, record in enumerate(records):
        name = Path(record["relative_path"]).name
        excerpt = record.get("excerpt", "")
        family = infer_family(name, excerpt)
        chapters = infer_chapter_links(name, excerpt, family)
        appendices = infer_appendix_links(name, excerpt, family)
        blob = build_blob(record)
        gate = gate_for_record(blob, family)
        scores = {}
        for element, profile in ELEMENTS.items():
            value = 0
            if family in profile["families"]:
                value += 4
            if gate in profile["gates"]:
                value += 3
            value += sum(1 for keyword in profile["keywords"] if keyword in blob)
            scores[element] = value
        ordered = sorted(scores, key=scores.get, reverse=True)
        assigned.append(
            {
                "id": f"DOC{index:04d}",
                "name": normalize_name(name),
                "display_name": clean_display_name(name),
                "relative_path": record["relative_path"],
                "source_layer": record.get("source_layer", "LocalProject"),
                "family": family,
                "family_label": FAMILY_LABELS.get(family, family),
                "chapters": chapters,
                "appendices": appendices,
                "gate": gate,
                "element": ordered[0],
                "secondary_element": ordered[1],
                "scores": scores,
                "tokens": tokenize(blob),
                "excerpt": (excerpt or "")[:240],
            }
        )
    return assigned


def pair_entry(a: dict, b: dict) -> dict:
    shared_chapters = sorted(set(a["chapters"]) & set(b["chapters"]))
    shared_appendices = sorted(set(a["appendices"]) & set(b["appendices"]))
    shared_tokens = sorted(set(a["tokens"]) & set(b["tokens"]))[:8]
    score = 0
    score += 5 if a["family"] == b["family"] else 0
    score += 3 * len(shared_chapters)
    score += 2 * len(shared_appendices)
    score += len(shared_tokens)
    score += 2 if a["element"] == b["element"] else 0
    score += 1 if a["gate"] == b["gate"] else 0
    return {
        "src": a["id"],
        "dst": b["id"],
        "src_name": a["name"],
        "dst_name": b["name"],
        "src_display_name": a["display_name"],
        "dst_display_name": b["display_name"],
        "src_element": a["element"],
        "dst_element": b["element"],
        "src_gate": a["gate"],
        "dst_gate": b["gate"],
        "kind": "self" if a["id"] == b["id"] else "ordered_pair",
        "score": score,
        "shared_chapters": shared_chapters,
        "shared_appendices": shared_appendices,
        "shared_tokens": shared_tokens,
    }


def build_pairs(assigned: list[dict]) -> list[dict]:
    pairs: list[dict] = []
    for a in assigned:
        for b in assigned:
            pairs.append(pair_entry(a, b))
    return pairs


def canonical_pair_key(pair: dict) -> tuple[str, str]:
    return tuple(sorted((pair["src"], pair["dst"])))


def display_endpoint(pair: dict, side: str) -> str:
    display_name = presentation_name(pair[f"{side}_display_name"])
    other_side = "dst" if side == "src" else "src"
    if display_name == presentation_name(pair[f"{other_side}_display_name"]):
        return f"{display_name} [{pair[side]}]"
    return display_name


def canonical_pair_key_string(src_id: str, dst_id: str) -> str:
    ordered = sorted((src_id, dst_id))
    return f"{ordered[0]}::{ordered[1]}"


def pair_relation_kind(a: dict, b: dict) -> str:
    same_element = a["element"] == b["element"]
    same_family = a["family"] == b["family"]
    if same_element and same_family:
        return "intra_family"
    if same_element:
        return "same_element_cross_family"
    if same_family:
        return "cross_element_same_family"
    return "cross_element_cross_family"


def canonical_pair_card(pair: dict, assigned_by_id: dict[str, dict]) -> dict:
    src_id, dst_id = sorted((pair["src"], pair["dst"]))
    src_record = assigned_by_id[src_id]
    dst_record = assigned_by_id[dst_id]
    return {
        "src_id": src_id,
        "dst_id": dst_id,
        "canonical_pair_key": canonical_pair_key_string(src_id, dst_id),
        "score": pair["score"],
        "kind": pair_relation_kind(src_record, dst_record),
        "shared_chapters": pair["shared_chapters"],
        "shared_appendices": pair["shared_appendices"],
        "shared_tokens": pair["shared_tokens"],
        "src_element": src_record["element"],
        "dst_element": dst_record["element"],
        "src_family": src_record["family"],
        "dst_family": dst_record["family"],
        "src_gate": src_record["gate"],
        "dst_gate": dst_record["gate"],
        "src_display_name": presentation_name(src_record["display_name"]),
        "dst_display_name": presentation_name(dst_record["display_name"]),
    }


def canonical_pairs(pairs: list[dict], assigned_by_id: dict[str, dict]) -> list[dict]:
    deduped: dict[str, dict] = {}
    for pair in pairs:
        if pair["kind"] != "ordered_pair" or pair["src"] == pair["dst"]:
            continue
        key = canonical_pair_key_string(pair["src"], pair["dst"])
        existing = deduped.get(key)
        if existing is None or pair["score"] > existing["score"]:
            deduped[key] = canonical_pair_card(pair, assigned_by_id)
    ordered = sorted(
        deduped.values(),
        key=lambda item: (-item["score"], item["src_display_name"], item["dst_display_name"]),
    )
    return ordered


def build_query_index(assigned: list[dict]) -> dict:
    alias_map: dict[str, list[str]] = {}
    token_map: dict[str, set[str]] = {}
    documents: dict[str, dict] = {}

    for record in assigned:
        document = {
            "id": record["id"],
            "name": record["name"],
            "display_name": record["display_name"],
            "presentation_name": presentation_name(record["display_name"]),
            "slug": slugify(record["display_name"]),
            "normalized_name": normalize_lookup_text(record["name"]),
            "normalized_display_name": normalize_lookup_text(record["display_name"]),
            "relative_path": record["relative_path"],
            "source_layer": record["source_layer"],
            "family": record["family"],
            "family_label": record["family_label"],
            "element": record["element"],
            "secondary_element": record["secondary_element"],
            "gate": record["gate"],
            "chapters": record["chapters"],
            "appendices": record["appendices"],
        }
        documents[record["id"]] = document

        aliases = {
            record["id"].lower(),
            normalize_lookup_text(record["name"]),
            normalize_lookup_text(record["display_name"]),
            slugify(record["display_name"]).replace("_", " "),
            record["relative_path"].lower(),
            Path(record["relative_path"]).name.lower(),
        }
        for alias in aliases:
            if not alias:
                continue
            alias_map.setdefault(alias, []).append(record["id"])
        for token in set(lookup_tokens(record["display_name"]) + lookup_tokens(record["name"]) + record["tokens"]):
            token_map.setdefault(token, set()).add(record["id"])

    return {
        "generated_at": utc_now(),
        "document_count": len(assigned),
        "documents": documents,
        "exact_aliases": {alias: sorted(set(ids)) for alias, ids in sorted(alias_map.items())},
        "token_index": {token: sorted(ids) for token, ids in sorted(token_map.items())},
    }


def build_facet_index(assigned: list[dict]) -> dict:
    facets = {
        "element": {},
        "family": {},
        "chapter": {},
        "appendix": {},
        "gate": {},
        "source_layer": {},
    }
    for record in assigned:
        facets["element"].setdefault(record["element"], []).append(record["id"])
        facets["family"].setdefault(record["family"], []).append(record["id"])
        facets["gate"].setdefault(record["gate"], []).append(record["id"])
        facets["source_layer"].setdefault(record["source_layer"], []).append(record["id"])
        for chapter in record["chapters"]:
            facets["chapter"].setdefault(chapter, []).append(record["id"])
        for appendix in record["appendices"]:
            facets["appendix"].setdefault(appendix, []).append(record["id"])
    return {
        "generated_at": utc_now(),
        "facets": {name: {key: sorted(values) for key, values in sorted(entries.items())} for name, entries in facets.items()},
    }


def build_neighbor_index(
    assigned: list[dict],
    canonical: list[dict],
) -> dict:
    assigned_by_id = {record["id"]: record for record in assigned}
    buckets: dict[str, dict[str, list[dict]]] = {
        record["id"]: {"overall": [], "cross_element": [], "cross_family": []} for record in assigned
    }
    seen: dict[str, dict[str, set[str]]] = {
        record["id"]: {"overall": set(), "cross_element": set(), "cross_family": set()} for record in assigned
    }

    for pair in canonical:
        for focus_id, other_id in ((pair["src_id"], pair["dst_id"]), (pair["dst_id"], pair["src_id"])):
            focus_record = assigned_by_id[focus_id]
            other_record = assigned_by_id[other_id]
            neighbor = {
                **pair,
                "other_id": other_id,
                "other_display_name": presentation_name(other_record["display_name"]),
                "other_family": other_record["family"],
                "other_element": other_record["element"],
                "other_gate": other_record["gate"],
            }
            if other_id not in seen[focus_id]["overall"]:
                buckets[focus_id]["overall"].append(neighbor)
                seen[focus_id]["overall"].add(other_id)
            if focus_record["element"] != other_record["element"] and other_id not in seen[focus_id]["cross_element"]:
                buckets[focus_id]["cross_element"].append(neighbor)
                seen[focus_id]["cross_element"].add(other_id)
            if focus_record["family"] != other_record["family"] and other_id not in seen[focus_id]["cross_family"]:
                buckets[focus_id]["cross_family"].append(neighbor)
                seen[focus_id]["cross_family"].add(other_id)

    return {
        "generated_at": utc_now(),
        "neighbors": {
            doc_id: {
                mode: entries[:32]
                for mode, entries in mode_map.items()
            }
            for doc_id, mode_map in buckets.items()
        },
    }


def build_zero_point_index(
    canonical: list[dict],
    assigned_by_id: dict[str, dict],
) -> dict:
    zero_core_chapters = {"Ch11", "Ch18", "Ch20", "Ch21"}
    zero_core_appendices = {"AppF", "AppG", "AppI", "AppM"}
    ranked: list[dict] = []
    for pair in canonical:
        chapter_hits = len(zero_core_chapters & set(pair["shared_chapters"]))
        appendix_hits = len(zero_core_appendices & set(pair["shared_appendices"]))
        if chapter_hits == 0 and appendix_hits == 0:
            continue
        convergence = pair["score"] + chapter_hits * 3 + appendix_hits * 2
        ranked.append(
            {
                **pair,
                "convergence_score": convergence,
                "zero_point_chapter_hits": sorted(zero_core_chapters & set(pair["shared_chapters"])),
                "zero_point_appendix_hits": sorted(zero_core_appendices & set(pair["shared_appendices"])),
            }
        )
    ranked.sort(
        key=lambda item: (-item["convergence_score"], -item["score"], item["src_display_name"], item["dst_display_name"])
    )
    return {
        "generated_at": utc_now(),
        "zero_point_chapters": sorted(zero_core_chapters),
        "zero_point_appendices": sorted(zero_core_appendices),
        "routes": ranked[:64],
    }


def operator_matrix(pairs: list[dict]) -> dict[str, dict[str, dict[str, float]]]:
    matrix: dict[str, dict[str, dict[str, float]]] = {}
    for src, _ in [(g, l) for g, l in [(item[0], item[1]) for item in OPERATOR_GATES]]:
        matrix[src] = {}
        for dst, _ in [(g, l) for g, l in [(item[0], item[1]) for item in OPERATOR_GATES]]:
            subset = [pair for pair in pairs if pair["src_gate"] == src and pair["dst_gate"] == dst]
            avg = round(sum(item["score"] for item in subset) / len(subset), 3) if subset else 0.0
            matrix[src][dst] = {"count": len(subset), "avg_score": avg}
    return matrix


def top_pairs(pairs: list[dict], predicate, limit: int, dedupe_mirrors: bool = False) -> list[dict]:
    subset = [pair for pair in pairs if predicate(pair)]
    subset.sort(key=lambda item: (-item["score"], item["src_name"], item["dst_name"]))
    if not dedupe_mirrors:
        return subset[:limit]
    deduped: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for pair in subset:
        key = canonical_pair_key(pair)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(pair)
        if len(deduped) >= limit:
            break
    return deduped


def mermaid_base(element_counts: Counter) -> str:
    return "\n".join(
        [
            "```mermaid",
            "flowchart LR",
            f'F["Fire {element_counts["Fire"]}"] --> W["Water {element_counts["Water"]}"]',
            f'W --> E["Earth {element_counts["Earth"]}"]',
            f'E --> A["Air {element_counts["Air"]}"]',
            "A --> F",
            'Q["AppQ"]',
            "F --> Q",
            "W --> Q",
            "E --> Q",
            "A --> Q",
            "```",
        ]
    )


def mermaid_emergence() -> str:
    return "\n".join(
        [
            "```mermaid",
            "flowchart TB",
            'Seed["Seed/Parse/Address"] --> Route["Route/Bridge/Weave"] --> Proof["Proof/Replay/Closure"] --> Lift["Lift/Next Crystal"]',
            'Fire["Fire"] --> Route',
            'Water["Water"] --> Route',
            'Earth["Earth"] --> Proof',
            'Air["Air"] --> Seed',
            'Q["Appendix Q"] --> Lift',
            "```",
        ]
    )


def mermaid_neural() -> str:
    return "\n".join(
        [
            "```mermaid",
            "flowchart LR",
            'D["Document Layer"] --> G["16x16 Gate Matrix"] --> X["Cross-Synthesis Field"] --> E["Elemental Cortex"] --> M["Metro Layers"] --> Q["Appendix Q"]',
            'Skill["Skill Router"] --> E',
            'Skill --> M',
            "```",
        ]
    )


def mermaid_transcendence() -> str:
    return "\n".join(
        [
            "```mermaid",
            "flowchart TB",
            'Void["Void"] --> Seed["Seed"] --> Orbit["Document Orbit"] --> Closure["Closure"] --> Lift["Lift"] --> Next["Next Neural Crystal"]',
            'Witness["Witness"] --> Closure',
            'Govern["Govern"] --> Lift',
            'Q["Appendix Q"] --> Orbit',
            "```",
        ]
    )


def write_root_docs(
    output_root: Path,
    assigned: list[dict],
    pairs: list[dict],
    matrix: dict[str, dict[str, dict[str, float]]],
    recursive_state: dict,
    live_docs_blocked: bool,
) -> None:
    element_counts = Counter(item["element"] for item in assigned)
    family_counts = Counter(item["family"] for item in assigned)
    assigned_by_id = {item["id"]: item for item in assigned}
    nonself_pairs = [pair for pair in pairs if pair["kind"] == "ordered_pair"]
    canonical = canonical_pairs(pairs, assigned_by_id)
    strongest_overall = top_pairs(nonself_pairs, lambda pair: True, 64, dedupe_mirrors=True)
    strongest_cross_element = top_pairs(
        nonself_pairs,
        lambda pair: pair["src_element"] != pair["dst_element"],
        64,
        dedupe_mirrors=True,
    )
    strongest_cross_family = top_pairs(
        nonself_pairs,
        lambda pair: assigned_by_id[pair["src"]]["family"] != assigned_by_id[pair["dst"]]["family"],
        64,
        dedupe_mirrors=True,
    )

    readme_lines = [
        "# Deeper Integrated Neural Net",
        "",
        "This subsystem materializes a four-element, document-level neural field over the active manuscript corpus.",
        "",
        f"- Documents indexed: `{len(assigned)}`",
        f"- Ordered document permutations materialized: `{len(pairs)}`",
        f"- Non-self permutations: `{len(nonself_pairs)}`",
        f"- Canonical unordered pair surfaces: `{len(canonical)}`",
        f"- Deep pass reference: `{int(recursive_state.get('deep_pass', 0))}`",
        f"- Live Google Docs state: `{'BLOCKED' if live_docs_blocked else 'PASS'}`",
        "- Element folders: `Fire`, `Water`, `Earth`, `Air`",
        "- Gate field: `16 x 16` operator matrix",
        "- Query surface: `10_QUERY` plus `deeper_neural_net_query.py`",
        "- Lens field: `4 x 64` elemental observation passes",
        "- Symmetry field: `15` syntheses plus zero point",
        "- Appendix Q: enabled",
    ]
    write_text(output_root / "README.md", "\n".join(readme_lines))

    architecture_lines = [
        "# Network Architecture",
        "",
        "Every source document is assigned a family, chapter vector, appendix vector, dominant element, secondary element, and operator gate before pairwise cross-synthesis is computed.",
        "",
        "## Element counts",
        "",
    ]
    for element in ("Fire", "Water", "Earth", "Air"):
        architecture_lines.append(f"- `{element}` -> `{element_counts[element]}` documents")
    architecture_lines.extend(["", "## Family density", ""])
    for family, count in family_counts.most_common():
        architecture_lines.append(f"- `{family}` -> `{count}`")
    write_text(output_root / "00_CORE" / "00_network_architecture.md", "\n".join(architecture_lines))

    synthesis_lines = [
        "# Exhaustive Deep Synthesis",
        "",
        "Every individual document has been cross-synthesized with every other document in ordered permutations. The exhaustive matrix is preserved in runtime JSON; this document names the strongest surfaces.",
        "",
        f"- Document count: `{len(assigned)}`",
        f"- Ordered pair count: `{len(pairs)}`",
        "",
        "## Strongest overall syntheses",
        "",
    ]
    for pair in strongest_overall:
        synthesis_lines.append(
            f"- `{display_endpoint(pair, 'src')}` <-> `{display_endpoint(pair, 'dst')}` score=`{pair['score']}` shared_chapters=`{', '.join(pair['shared_chapters']) or 'none'}` shared_appendices=`{', '.join(pair['shared_appendices']) or 'none'}` shared_tokens=`{', '.join(pair['shared_tokens']) or 'none'}`"
        )
    synthesis_lines.extend(["", "## Strongest cross-element syntheses", ""])
    for pair in strongest_cross_element:
        synthesis_lines.append(
            f"- `{display_endpoint(pair, 'src')}` <-> `{display_endpoint(pair, 'dst')}` score=`{pair['score']}` path=`{pair['src_element']}<->{pair['dst_element']}` shared_chapters=`{', '.join(pair['shared_chapters']) or 'none'}`"
        )
    synthesis_lines.extend(["", "## Strongest cross-family syntheses", ""])
    for pair in strongest_cross_family:
        src_family = assigned_by_id[pair["src"]]["family"]
        dst_family = assigned_by_id[pair["dst"]]["family"]
        synthesis_lines.append(
            f"- `{display_endpoint(pair, 'src')}` <-> `{display_endpoint(pair, 'dst')}` score=`{pair['score']}` families=`{src_family}<->{dst_family}` shared_appendices=`{', '.join(pair['shared_appendices']) or 'none'}`"
        )
    write_text(output_root / "00_CORE" / "01_exhaustive_deep_synthesis.md", "\n".join(synthesis_lines))

    matrix_lines = ["# 16 x 16 Operator Gate Matrix", ""]
    header = "| src \\ dst | " + " | ".join(gate for gate, _ in OPERATOR_GATES) + " |"
    divider = "|" + "---|" * 17
    matrix_lines.extend([header, divider])
    for src, _ in OPERATOR_GATES:
        row = [src]
        for dst, _ in OPERATOR_GATES:
            cell = matrix[src][dst]
            row.append(f"{cell['count']}/{cell['avg_score']}")
        matrix_lines.append("| " + " | ".join(row) + " |")
    write_text(output_root / "00_CORE" / "02_16x16_operator_gate_matrix.md", "\n".join(matrix_lines))

    bridges = Counter(f"{pair['src_element']}->{pair['dst_element']}" for pair in nonself_pairs)
    bridge_lines = ["# Pair Permutation Overview", "", "Element-to-element flows across the full ordered pair field.", ""]
    for bridge, count in sorted(bridges.items()):
        bridge_lines.append(f"- `{bridge}` -> `{count}` ordered pairs")
    write_text(output_root / "00_CORE" / "03_pair_permutation_overview.md", "\n".join(bridge_lines))


def write_element_docs(output_root: Path, assigned: list[dict], pairs: list[dict]) -> None:
    for element, profile in ELEMENTS.items():
        folder = output_root / profile["folder"]
        docs = sorted((item for item in assigned if item["element"] == element), key=lambda item: (item["family"], item["name"]))
        registry_lines = [
            f"# {element} Registry",
            "",
            f"{element} is the lens of {profile['bias']}.",
            "",
            f"- Dominant document count: `{len(docs)}`",
            "## Documents",
            "",
        ]
        for item in docs:
            registry_lines.append(
                f"- `{item['id']}` `{item['display_name']}` family=`{item['family']}` gate=`{item['gate']}` secondary=`{item['secondary_element']}`"
            )
        write_text(folder / "00_registry.md", "\n".join(registry_lines))

        internal = top_pairs(
            pairs,
            lambda pair, element=element: pair["kind"] == "ordered_pair" and pair["src_element"] == element and pair["dst_element"] == element,
            64,
            dedupe_mirrors=True,
        )
        internal_lines = [f"# {element} Internal Cross Synthesis", "", "Top ordered pairs inside the same element.", ""]
        for pair in internal:
            internal_lines.append(
                f"- `{display_endpoint(pair, 'src')}` <-> `{display_endpoint(pair, 'dst')}` score=`{pair['score']}` gates=`{pair['src_gate']}<->{pair['dst_gate']}` shared_chapters=`{', '.join(pair['shared_chapters']) or 'none'}`"
            )
        write_text(folder / "01_internal_pairs.md", "\n".join(internal_lines))

        external = top_pairs(pairs, lambda pair, element=element: pair["kind"] == "ordered_pair" and pair["src_element"] == element and pair["dst_element"] != element, 64)
        external_lines = [f"# {element} Cross-Element Synthesis", "", "Top outward bridges from this element into the rest of the net.", ""]
        for pair in external:
            external_lines.append(
                f"- `{display_endpoint(pair, 'src')}` -> `{display_endpoint(pair, 'dst')}` score=`{pair['score']}` path=`{pair['src_element']}->{pair['dst_element']}` shared_appendices=`{', '.join(pair['shared_appendices']) or 'none'}`"
            )
        write_text(folder / "02_cross_element_pairs.md", "\n".join(external_lines))

        observation_lines = [
            f"# {element} 64-Address Observation Grid",
            "",
            f"{element} observes the full framework as a field of {profile['bias']}.",
            "",
        ]
        idx = 0
        for domain_name, chapters, appendices, thesis in DOMAIN_PROFILES:
            for verb in profile["verbs"]:
                idx += 1
                observation_lines.append(
                    f"- `{element[0]}{idx:02d}` `{domain_name} x {verb}` -> chapters `{', '.join(chapters)}` appendices `{', '.join(appendices)}`: {element} asks how the net can `{verb}` `{domain_name.lower()}` while preserving `{thesis}`."
                )
        write_text(folder / "03_observation_grid.md", "\n".join(observation_lines))


def write_cross_synth_docs(output_root: Path) -> None:
    lens_lines = [
        "# 4 x 64 Elemental Cross-Synthesis Matrix",
        "",
        "The neutral pass lives in `00_CORE/01_exhaustive_deep_synthesis.md`. This file names the elemental observer field and points to each element's 64-address grid.",
        "",
    ]
    for element, profile in ELEMENTS.items():
        lens_lines.extend([f"## {element}", "", f"See `../{profile['folder']}/03_observation_grid.md` for the full 64-address grid.", ""])
    write_text(output_root / "05_CROSS_SYNTH" / "00_lens_64x4_matrix.md", "\n".join(lens_lines))

    symmetry_lines = [
        "# 15 Symmetry Syntheses and Zero Point",
        "",
        "The four elements generate fifteen syntheses: four singletons, six pairings, four triads, and one total synthesis.",
        "",
    ]
    combos = [
        ("S01", ("Fire",)),
        ("S02", ("Water",)),
        ("S03", ("Earth",)),
        ("S04", ("Air",)),
        ("S05", ("Fire", "Water")),
        ("S06", ("Fire", "Earth")),
        ("S07", ("Fire", "Air")),
        ("S08", ("Water", "Earth")),
        ("S09", ("Water", "Air")),
        ("S10", ("Earth", "Air")),
        ("S11", ("Fire", "Water", "Earth")),
        ("S12", ("Fire", "Water", "Air")),
        ("S13", ("Fire", "Earth", "Air")),
        ("S14", ("Water", "Earth", "Air")),
        ("S15", ("Fire", "Water", "Earth", "Air")),
    ]
    for code, combo in combos:
        synthesis = " / ".join(combo)
        symmetry_lines.extend([f"## {code} - {synthesis}", "", f"- Synthesis: {synthesis} forces the neural net to remain generative, transmissible, and witness-bearing at the same time.", ""])
    symmetry_lines.extend(
        [
            "## Zero point",
            "",
            "The zero point of the neural net is the lawful bridge where seed, proof, memory, and governance agree on a restart without losing witness. In chapter space it clusters around `Ch11`, `Ch18`, `Ch20`, and `Ch21`. In appendix space it clusters around `AppF`, `AppG`, `AppI`, and `AppM`. In appendix-only topology it becomes `AppQ`.",
        ]
    )
    write_text(output_root / "05_CROSS_SYNTH" / "01_symmetry_zero_point.md", "\n".join(symmetry_lines))


def write_metro_docs(output_root: Path, assigned: list[dict]) -> None:
    element_counts = Counter(item["element"] for item in assigned)
    write_text(
        output_root / "06_METRO" / "00_metro_map_lvl1.md",
        "\n".join(["# Metro Map", "", "Level 1 is the elemental ring.", "", mermaid_base(element_counts)]),
    )
    write_text(
        output_root / "06_METRO" / "01_metro_map_lvl2_deep_emergence.md",
        "\n".join(["# Level 2 Metro Map - Deep Emergence", "", mermaid_emergence()]),
    )
    write_text(
        output_root / "06_METRO" / "02_metro_map_lvl3_deeper_neural_map.md",
        "\n".join(["# Level 3 Metro Map - Deeper Neural Map", "", mermaid_neural()]),
    )
    write_text(
        output_root / "06_METRO" / "03_metro_map_lvl4_transcendence.md",
        "\n".join(["# Level 4 Metro Map - Transcendence", "", mermaid_transcendence()]),
    )


def write_appendix_docs(output_root: Path) -> None:
    feed_map = {code: [] for code, _, _ in APPENDICES}
    for chapter in CHAPTERS:
        for hub in chapter.hubs:
            feed_map.setdefault(hub, []).append(chapter.code)

    outline_lines = [
        "# Appendix Crystal Skeleton Outline",
        "",
        "The appendix lattice remains the `4 x 4` crystal of A through P, with Q as the integrated appendix-only metro.",
        "",
    ]
    for code, title, description in APPENDICES:
        outline_lines.extend(
            [
                f"## {code} - {title}",
                "",
                f"- Function: {description}",
                f"- Feed chapters: `{', '.join(feed_map.get(code, [])) or 'none'}`",
                "",
            ]
        )
    outline_lines.extend(
        [
            "## AppQ - Integrated Appendix-Only Metro",
            "",
            "- Function: integrate A through P into one appendix-only transport surface.",
            "- Feed appendices: `AppA-AppP`",
            "- Feed chapters: `Ch10, Ch11, Ch12, Ch18, Ch20, Ch21`",
        ]
    )
    write_text(output_root / "07_APPENDIX" / "00_appendix_crystal_skeleton_outline.md", "\n".join(outline_lines))

    q_lines = [
        "# Appendix Q - Integrated Appendix-Only Metro Map",
        "",
        "Appendix Q is the appendix nervous system seen as one crystal instead of sixteen supplements.",
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
    ]
    write_text(output_root / "07_APPENDIX" / "01_appendix_q_integrated_only_metro_map.md", "\n".join(q_lines))


def write_query_docs(output_root: Path) -> None:
    query_dir = output_root / "10_QUERY"
    readme_lines = [
        "# Query Surface",
        "",
        "The deeper neural net can be queried locally through the CLI entrypoint:",
        "",
        "```powershell",
        'python "C:\\Users\\dmitr\\Documents\\Athena Agent\\DEEPER CRYSTALIZATION\\deeper_neural_net_query.py" doc DOC0000',
        "```",
        "",
        "## Runtime indices",
        "",
        "- `../09_RUNTIME/03_query_index.json`: exact and fuzzy lookup aliases.",
        "- `../09_RUNTIME/04_facet_index.json`: element, family, chapter, appendix, gate, and source-layer slices.",
        "- `../09_RUNTIME/05_neighbor_index.json`: strongest overall, cross-element, and cross-family neighbors per document.",
        "- `../09_RUNTIME/06_zero_point_index.json`: highest-yield convergence routes near the zero-point cluster.",
        "- `../../06_RUNTIME/13_chapter_frontier_manifest.json`: chapter frontier compiler receipt and generated pack targets.",
        "- `../../14_PARALLEL_PLANS/04_plan_manifest.json`: materialized `frontier4` plan lattice for the frontier quartet.",
        "",
        "## Output modes",
        "",
        "- Default: markdown to stdout.",
        "- `--json`: JSON to stdout.",
        "- `--write`: writes both markdown and JSON to `last/` with deterministic filenames.",
    ]
    write_text(query_dir / "README.md", "\n".join(readme_lines))

    usage_lines = [
        "# Query Usage",
        "",
        "```powershell",
        '# Document card',
        'python "C:\\Users\\dmitr\\Documents\\Athena Agent\\DEEPER CRYSTALIZATION\\deeper_neural_net_query.py" doc DOC0000',
        "",
        '# Fuzzy lookup',
        'python "C:\\Users\\dmitr\\Documents\\Athena Agent\\DEEPER CRYSTALIZATION\\deeper_neural_net_query.py" doc "manuscript seed"',
        "",
        '# Strongest neighbors',
        'python "C:\\Users\\dmitr\\Documents\\Athena Agent\\DEEPER CRYSTALIZATION\\deeper_neural_net_query.py" neighbors DOC0000 --mode cross-family --limit 5',
        "",
        '# Canonical pair card',
        'python "C:\\Users\\dmitr\\Documents\\Athena Agent\\DEEPER CRYSTALIZATION\\deeper_neural_net_query.py" pair DOC0000 DOC0001',
        "",
        '# Slice by element or chapter',
        'python "C:\\Users\\dmitr\\Documents\\Athena Agent\\DEEPER CRYSTALIZATION\\deeper_neural_net_query.py" slice --element Fire --limit 8',
        'python "C:\\Users\\dmitr\\Documents\\Athena Agent\\DEEPER CRYSTALIZATION\\deeper_neural_net_query.py" slice --chapter Ch11 --limit 8',
        "",
        '# Zero-point routes',
        'python "C:\\Users\\dmitr\\Documents\\Athena Agent\\DEEPER CRYSTALIZATION\\deeper_neural_net_query.py" zero-point --limit 12 --write',
        "",
        '# Chapter drafting-prep packs',
        'python "C:\\Users\\dmitr\\Documents\\Athena Agent\\DEEPER CRYSTALIZATION\\deeper_neural_net_query.py" chapter-pack Ch03 --limit 8 --write',
        'python "C:\\Users\\dmitr\\Documents\\Athena Agent\\DEEPER CRYSTALIZATION\\deeper_neural_net_query.py" chapter-pack Ch10 --limit 8 --write',
        'python "C:\\Users\\dmitr\\Documents\\Athena Agent\\DEEPER CRYSTALIZATION\\deeper_neural_net_query.py" chapter-pack Ch12 --limit 8 --write',
        'python "C:\\Users\\dmitr\\Documents\\Athena Agent\\DEEPER CRYSTALIZATION\\deeper_neural_net_query.py" chapter-pack Ch14 --limit 8 --write',
        "",
        '# Materialized frontier plan lattice',
        'python "C:\\Users\\dmitr\\Documents\\Athena Agent\\DEEPER CRYSTALIZATION\\deeper_neural_net_query.py" plan-grid frontier4 --chapter Ch10 --lane chapter_tile_and_handoff --pass manuscript_closure --write',
        "```",
    ]
    write_text(query_dir / "USAGE.md", "\n".join(usage_lines))


def write_skill_docs(output_root: Path) -> None:
    skill_dir = output_root / "08_SKILL"
    skill_lines = [
        "---",
        'name: deeper-integrated-neural-net',
        'description: "Use when exhaustive document-level cross-synthesis, queryable local neural-net routing, four-element decomposition, 16x16 operator matrices, multi-resolution metro maps, Appendix Q integration, or a deeper integrated neural network build is required."',
        "---",
        "",
        "# Deeper Integrated Neural Net",
        "",
        "Use this skill when the task is to operate the neural net rather than draft a single isolated section.",
        "",
        "## Workflow",
        "",
        "1. Refresh the atlas.",
        "2. Build the elemental neural net.",
        "3. Read `00_CORE` before making total-structure claims.",
        "4. Read the relevant elemental folder before making element-biased claims.",
        "5. Read `09_RUNTIME/03_query_index.json` through `06_zero_point_index.json` when the task is lookup, routing, nearest-neighbor discovery, or slice analysis.",
        "6. Use `deeper_neural_net_query.py` for CLI and file-backed queries before improvising a free-form corpus answer.",
        "7. Use `chapter-pack Ch03|Ch10|Ch12|Ch14` when the task is to turn query results into a frontier-chapter drafting-prep bundle and additive manuscript handoff.",
        "8. Use `plan-grid frontier4` when the task is parallel planning across the frontier quartet rather than one chapter in isolation.",
        "9. Read `06_METRO` when route and resolution matter.",
        "10. Read Appendix Q when appendix infrastructure is the real object.",
        "",
        "## References",
        "",
        "- `references/algorithmic_pipeline.md`",
        "- `references/skill_orchestration.md`",
    ]
    write_text(skill_dir / "SKILL.md", "\n".join(skill_lines))

    pipeline_lines = [
        "# Algorithmic Pipeline",
        "",
        "1. Refresh atlas and live-doc receipt.",
        "2. Assign every document a family, gate, element, and chapter/appendix vector.",
        "3. Materialize the full ordered pair field.",
        "4. Collapse ordered pairs into canonical unordered pair surfaces for human-facing routing.",
        "5. Emit query indices for exact lookup, facets, neighbors, and zero-point routes.",
        "6. Aggregate the 16x16 gate matrix.",
        "7. Write the four elemental folders.",
        "8. Emit metro layers, Appendix Q, and query usage docs.",
        "9. Use the generated surfaces before promoting any new whole-system claim.",
    ]
    write_text(skill_dir / "references" / "algorithmic_pipeline.md", "\n".join(pipeline_lines))

    orchestration_lines = [
        "# Skill Orchestration",
        "",
        f"- [manuscript-intake](C:/Users/dmitr/.codex/skills/manuscript-intake/SKILL.md): refresh corpus records first.",
        f"- [manuscript-seed](C:/Users/dmitr/.codex/skills/manuscript-seed/SKILL.md): synthesize chapter or whole-manuscript outputs from the neural field.",
        f"- [metro-cartography](C:/Users/dmitr/.codex/skills/metro-cartography/SKILL.md): convert pair fields into transit lines and hubs.",
        f"- [manuscript-final-drafter](C:/Users/dmitr/.codex/skills/manuscript-final-drafter/SKILL.md): promote validated synthesis into canonical prose.",
        f"- [shadow-analysis](C:/Users/dmitr/.codex/skills/shadow-analysis/SKILL.md): name blind spots after major passes.",
        f"- [q-shrink](C:/Users/dmitr/.codex/skills/q-shrink/SKILL.md): compress the net into zero-point law.",
    ]
    write_text(skill_dir / "references" / "skill_orchestration.md", "\n".join(orchestration_lines))


def write_runtime_docs(
    output_root: Path,
    assigned: list[dict],
    pairs: list[dict],
    matrix: dict[str, dict[str, dict[str, float]]],
    recursive_state: dict,
    live_docs_blocked: bool,
) -> dict:
    runtime_dir = output_root / "09_RUNTIME"
    assigned_by_id = {record["id"]: record for record in assigned}
    canonical = canonical_pairs(pairs, assigned_by_id)
    query_index = build_query_index(assigned)
    facet_index = build_facet_index(assigned)
    neighbor_index = build_neighbor_index(assigned, canonical)
    zero_point_index = build_zero_point_index(canonical, assigned_by_id)
    query_index_files = [
        "13_DEEPER_NEURAL_NET/09_RUNTIME/03_query_index.json",
        "13_DEEPER_NEURAL_NET/09_RUNTIME/04_facet_index.json",
        "13_DEEPER_NEURAL_NET/09_RUNTIME/05_neighbor_index.json",
        "13_DEEPER_NEURAL_NET/09_RUNTIME/06_zero_point_index.json",
    ]
    manifest = {
        "generated_at": utc_now(),
        "deep_pass": int(recursive_state.get("deep_pass", 0)),
        "live_docs_blocked": live_docs_blocked,
        "document_count": len(assigned),
        "ordered_pair_count": len(pairs),
        "nonself_pair_count": len([pair for pair in pairs if pair["kind"] == "ordered_pair"]),
        "canonical_pair_count": len(canonical),
        "element_counts": Counter(item["element"] for item in assigned),
        "operator_gates": [gate for gate, _ in OPERATOR_GATES],
        "query_surface_ready": True,
        "query_index_files": query_index_files,
        "default_query_output_mode": "markdown_stdout",
    }
    write_json(runtime_dir / "00_network_manifest.json", manifest)
    write_json(runtime_dir / "01_element_registry.json", assigned)
    write_json(runtime_dir / "02_ordered_pair_matrix.json", pairs)
    write_json(runtime_dir / "03_operator_gate_matrix.json", matrix)
    write_json(runtime_dir / "03_query_index.json", query_index)
    write_json(runtime_dir / "04_facet_index.json", facet_index)
    write_json(runtime_dir / "05_neighbor_index.json", neighbor_index)
    write_json(runtime_dir / "06_zero_point_index.json", zero_point_index)
    return manifest


def build_deeper_neural_net(
    active_root: Path,
    build_root: Path,
    records: list[dict],
    recursive_state: dict,
    live_docs_blocked: bool,
) -> dict:
    output_root = active_root / "13_DEEPER_NEURAL_NET"
    assigned = assign_records(records)
    pairs = build_pairs(assigned)
    matrix = operator_matrix(pairs)

    if output_root.exists():
        import shutil

        shutil.rmtree(output_root)

    write_root_docs(output_root, assigned, pairs, matrix, recursive_state, live_docs_blocked)
    write_element_docs(output_root, assigned, pairs)
    write_cross_synth_docs(output_root)
    write_metro_docs(output_root, assigned)
    write_appendix_docs(output_root)
    write_skill_docs(output_root)
    write_query_docs(output_root)
    manifest = write_runtime_docs(output_root, assigned, pairs, matrix, recursive_state, live_docs_blocked)
    return manifest


def main() -> int:
    active_root = PROJECT_ROOT / "ACTIVE_NERVOUS_SYSTEM"
    build_root = PROJECT_ROOT / "_build"
    records = load_records(build_root)
    recursive_state = load_recursive_state_snapshot(active_root, build_root)
    live_docs_blocked = read_live_docs_blocked(active_root, build_root)
    manifest = build_deeper_neural_net(active_root, build_root, records, recursive_state, live_docs_blocked)

    print(f"Wrote deeper integrated neural net at: {active_root / '13_DEEPER_NEURAL_NET'}")
    print(f"Documents: {manifest['document_count']}")
    print(f"Ordered pairs: {manifest['ordered_pair_count']}")
    print(f"Live Google Docs state: {'BLOCKED' if manifest['live_docs_blocked'] else 'PASS'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
