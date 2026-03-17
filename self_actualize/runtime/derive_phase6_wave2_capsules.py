from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

from self_actualize.runtime.derive_phase5_atlas_truth_and_capsule_metabolism import (
    APPENDIX_ROOT,
    CAPSULE_ROOT,
    CHAPTER_ROOT,
    CORPUS_ATLAS_PATH,
    CORPUS_ATLAS_SUMMARY_PATH,
    KNOWLEDGE_FABRIC_DASHBOARD_PATH,
    KNOWLEDGE_FABRIC_RECORDS_PATH,
    MYCELIUM_ROOT,
    NERVOUS_SYSTEM_ROOT,
    PROMOTABLE_EXTENSIONS,
    SELF_ACTUALIZE_ROOT,
    SEMANTIC_MASS_LEDGER_PATH,
    WITNESS_HIERARCHY_PATH,
    dedupe_matches,
    ensure_all_ok,
    load_json,
    load_shortcuts,
    markdown_table,
    normalize_relative,
    parse_docs_gate,
    refresh_corpus_atlas,
    render_corpus_atlas_summary,
    resolve_anchor,
    run_derivation_chain,
    run_verification_chain,
    safe_restore,
    snapshot_counts,
    utc_now,
    write_json,
    write_text,
    WORKSPACE_ROOT,
)
from self_actualize.runtime.knowledge_fabric_query_engine import run_shortcut, summarize_route


PHASE6_DERIVATION_VERSION = "2026-03-13.phase6-wave2-capsules-v1"
PHASE6_DERIVATION_COMMAND = "python -m self_actualize.runtime.derive_phase6_wave2_capsules"

PHASE6_PAYLOAD_JSON_PATH = SELF_ACTUALIZE_ROOT / "phase6_wave2_capsules.json"
PHASE6_OVERVIEW_MD_PATH = (
    NERVOUS_SYSTEM_ROOT / "10_OVERVIEW" / "21_PHASE6_WAVE2_CAPSULE_DENSIFICATION.md"
)
PHASE6_LEDGER_MD_PATH = (
    NERVOUS_SYSTEM_ROOT / "90_LEDGERS" / "37_PHASE6_WAVE2_CAPSULE_LEDGER_2026-03-13.md"
)
PHASE6_RUNTIME_MD_PATH = (
    MYCELIUM_ROOT / "nervous_system" / "30_phase6_wave2_capsule_densification_runtime.md"
)
PHASE6_RECEIPT_MD_PATH = (
    MYCELIUM_ROOT / "receipts" / "2026-03-13_phase6_wave2_capsules.md"
)
ORGIN_ATLAS_PATH = SELF_ACTUALIZE_ROOT / "orgin_atlas.json"

QSHRINK_GANGLION_PATH = (
    MYCELIUM_ROOT / "nervous_system" / "ganglia" / "GANGLION_qshrink.md"
)
ATHENA_FLEET_GANGLION_PATH = (
    MYCELIUM_ROOT / "nervous_system" / "ganglia" / "GANGLION_athena_fleet.md"
)
GAMES_GANGLION_PATH = (
    MYCELIUM_ROOT / "nervous_system" / "ganglia" / "GANGLION_games.md"
)
IDENTITY_GANGLION_PATH = (
    MYCELIUM_ROOT / "nervous_system" / "ganglia" / "GANGLION_i_am_athena.md"
)
ORGIN_GANGLION_PATH = (
    MYCELIUM_ROOT / "nervous_system" / "ganglia" / "GANGLION_orgin.md"
)

WRITEBACK_SURFACES = [
    MYCELIUM_ROOT / "GLOBAL_EMERGENT_GUILD_HALL" / "BOARDS" / "06_QUEST_BOARD.md",
    MYCELIUM_ROOT / "nervous_system" / "06_active_queue.md",
    MYCELIUM_ROOT / "nervous_system" / "manifests" / "WEAKEST_FRONT_QUEUE.md",
    MYCELIUM_ROOT / "nervous_system" / "manifests" / "QSHRINK_ACTIVE_FRONT.md",
    MYCELIUM_ROOT / "nervous_system" / "families" / "FAMILY_qshrink_athena_internal_use.md",
    MYCELIUM_ROOT / "nervous_system" / "families" / "FAMILY_athena_fleet.md",
    MYCELIUM_ROOT / "nervous_system" / "families" / "FAMILY_games.md",
    MYCELIUM_ROOT / "nervous_system" / "families" / "FAMILY_i_am_athena.md",
    MYCELIUM_ROOT / "nervous_system" / "families" / "FAMILY_orgin.md",
    MYCELIUM_ROOT / "nervous_system" / "routes" / "whole_crystal" / "ROUTE_qshrink_athena_internal_use.md",
    MYCELIUM_ROOT / "nervous_system" / "routes" / "whole_crystal" / "ROUTE_athena_fleet.md",
    MYCELIUM_ROOT / "nervous_system" / "routes" / "whole_crystal" / "ROUTE_games.md",
    MYCELIUM_ROOT / "nervous_system" / "routes" / "whole_crystal" / "ROUTE_i_am_athena.md",
    MYCELIUM_ROOT / "nervous_system" / "routes" / "whole_crystal" / "ROUTE_orgin.md",
]


FAMILY_CONFIGS: list[dict[str, Any]] = [
    {
        "slug": "qshrink",
        "title": "QSHRINK",
        "root_name": "QSHRINK - ATHENA (internal use)",
        "query": "qshrink compression shiva corpus bindings zero point address law corridor contract",
        "law": (
            "The `qshrink` capsule becomes canonical only when the control shell, corridor "
            "contract, and live `Q42 / QS64-17` front are discoverable through one atlas-backed "
            "entry shell instead of a seed bridge."
        ),
        "chapter_anchors": ["Ch11", "Ch13", "Ch18"],
        "appendix_anchors": ["AppN", "AppP"],
        "preferred_path_prefixes": [
            r"QSHRINK - ATHENA (internal use)\00_CONTROL\00_",
            r"QSHRINK - ATHENA (internal use)\00_CONTROL\01_",
            r"QSHRINK - ATHENA (internal use)\00_CONTROL\02_",
            r"QSHRINK - ATHENA (internal use)\00_CONTROL\03_",
            r"QSHRINK - ATHENA (internal use)\00_CONTROL\04_",
        ],
        "excluded_path_patterns": [],
        "preferred_artifact_classes": ["manuscript", "schema"],
        "preferred_semantic_roles": ["law", "support"],
        "runtime_support_paths": [
            r"self_actualize\mycelium_brain\nervous_system\families\FAMILY_qshrink_athena_internal_use.md",
            r"self_actualize\mycelium_brain\nervous_system\families\FAMILY_qshrink_athena_internal_use_route_map.md",
            r"self_actualize\mycelium_brain\nervous_system\manifests\QSHRINK_ACTIVE_FRONT.md",
            r"self_actualize\mycelium_brain\nervous_system\ganglia\GANGLION_qshrink.md",
        ],
        "support_assets": [
            r"Athena FLEET\QSHRINK2_CORPUS_ECOSYSTEM\11_QSHRINK_CORE_CORRIDOR_CONTRACT.md",
            r"self_actualize\qshrink_connectivity_square.json",
            r"self_actualize\qshrink_agent_task_matrix.json",
        ],
        "metro_lines": ["Kernel Line", "Canonical-Bridge Line", "Swarm Runtime Line"],
        "active_front": "Q42 / QS64-17 Connectivity-Diagnose-Square",
        "graph_policy": {
            "promoted_neuron": "N-0010",
            "promoted_synapses": ["S-0009"],
            "new_synapses": ["S-0032"],
            "new_edges": ["E-NS-018"],
        },
        "ganglion_path": QSHRINK_GANGLION_PATH,
        "primary_neurons": [
            "QSHRINK -> Athena FLEET corridor membrane",
            "QSHRINK -> atlas replay compression law",
            "QSHRINK -> Hall agent sweep cadence",
        ],
        "local_tasks": [
            "keep the 00_CONTROL shell as the lawful entry surface",
            "route QS64-17 through family, Hall, and runtime together",
            "preserve ORGIN as the secondary seed leg without flattening blocker truth",
        ],
        "minimum_entry_records": 5,
    },
    {
        "slug": "athena_fleet",
        "title": "Athena FLEET",
        "root_name": "Athena FLEET",
        "query": "athena fleet mycelium network tesseract corridor matrix active front self steer",
        "law": (
            "The `athena_fleet` capsule becomes canonical only when the fleet corridor reads as a "
            "replayable body with an atlas-backed entry shell, route authority, and graph bridge "
            "into the cortex."
        ),
        "chapter_anchors": ["Ch14", "Ch18", "Ch21"],
        "appendix_anchors": ["AppP"],
        "preferred_path_prefixes": [
            r"Athena FLEET\FLEET_MYCELIUM_NETWORK\00_",
            r"Athena FLEET\FLEET_MYCELIUM_NETWORK\01_",
            r"Athena FLEET\FLEET_MYCELIUM_NETWORK\02_",
            r"Athena FLEET\FLEET_MYCELIUM_NETWORK\03_",
            r"Athena FLEET\FLEET_MYCELIUM_NETWORK\04_",
        ],
        "excluded_path_patterns": [],
        "preferred_artifact_classes": ["manuscript", "data"],
        "preferred_semantic_roles": ["support", "law"],
        "runtime_support_paths": [
            r"self_actualize\mycelium_brain\nervous_system\families\FAMILY_athena_fleet.md",
            r"self_actualize\mycelium_brain\nervous_system\families\FAMILY_athena_fleet_route_map.md",
            r"self_actualize\mycelium_brain\nervous_system\routes\whole_crystal\ROUTE_athena_fleet.md",
            r"self_actualize\mycelium_brain\nervous_system\ganglia\GANGLION_athena_fleet.md",
        ],
        "support_assets": [
            r"Athena FLEET\MYCELIUM_NETWORK_STANDARD_TEXT_RECORD.md",
            r"Athena FLEET\FLEET_MYCELIUM_NETWORK\athena_fleet_mycelium_graph.json",
        ],
        "metro_lines": ["Canonical-Bridge Line", "Swarm Runtime Line"],
        "active_front": "FRONT-INT-ATHENA-FLEET-BRIDGE",
        "graph_policy": {
            "promoted_neuron": "N-0009",
            "promoted_synapses": ["S-0008"],
            "new_synapses": ["S-0032"],
            "new_edges": ["E-NS-018"],
        },
        "ganglion_path": ATHENA_FLEET_GANGLION_PATH,
        "primary_neurons": [
            "Athena FLEET -> QSHRINK corridor membrane",
            "Athena FLEET -> cortex branch contraction",
            "Athena FLEET -> ORGIN seed leg handoff",
        ],
        "local_tasks": [
            "keep the route map authoritative for corridor-level steering",
            "preserve the fleet shell as the main self-steer bridge",
            "stay coupled to QSHRINK and ORGIN without outranking the cortex",
        ],
        "minimum_entry_records": 5,
    },
    {
        "slug": "games",
        "title": "GAMES",
        "root_name": "GAMES",
        "query": "games simulation manuscript metro system stoicheia mechanics fitchain rule loop",
        "law": (
            "The `games` capsule becomes canonical only when playable mechanics and simulation law "
            "are discoverable without manufacturing noise taking over the entry shell."
        ),
        "chapter_anchors": ["Ch14", "Ch18", "Ch21"],
        "appendix_anchors": ["AppO", "AppP"],
        "preferred_path_prefixes": [
            r"GAMES\games_deep_integration_manuscript.md",
            r"GAMES\games_mycelium_metro_system.md",
            r"GAMES\games_mycelium_metro_graph.json",
        ],
        "excluded_path_patterns": [
            "\\final game prints\\",
            "\\box templates\\",
            ".csv",
            ".psd",
            ".png",
            ".jpg",
            ".jpeg",
            ".upc",
            "barcode",
            "print",
            "63x88mm",
            "65x90",
        ],
        "preferred_artifact_classes": ["manuscript", "data"],
        "preferred_semantic_roles": ["support", "law"],
        "runtime_support_paths": [
            r"self_actualize\mycelium_brain\nervous_system\families\FAMILY_games.md",
            r"self_actualize\mycelium_brain\nervous_system\routes\whole_crystal\ROUTE_games.md",
            r"self_actualize\mycelium_brain\nervous_system\ganglia\GANGLION_games.md",
        ],
        "support_assets": [
            r"NERVOUS_SYSTEM\50_CORPUS_CAPSULES\stoicheia\01_stoicheia_reserve_bridge.md",
            r"GAMES\archive_manifest.json",
        ],
        "metro_lines": ["Mythic Compression Line", "Canonical-Bridge Line"],
        "active_front": "Q10 low-mass family densification / simulation-law contraction",
        "graph_policy": {
            "promoted_neuron": "N-0011",
            "promoted_synapses": ["S-0010"],
            "new_synapses": [],
            "new_edges": [],
        },
        "ganglion_path": GAMES_GANGLION_PATH,
        "primary_neurons": [
            "GAMES -> simulation-law contraction",
            "GAMES -> Stoicheia reserve sibling",
            "GAMES -> metro-playable embodiment",
        ],
        "local_tasks": [
            "keep manufacturing assets out of the entry shell",
            "bind the manuscript and metro system into one playable law surface",
            "leave Stoicheia reserve-thin but explicitly related",
        ],
        "reserve_siblings": ["Stoicheia (Element Sudoku)"],
        "minimum_entry_records": 2,
    },
    {
        "slug": "identity",
        "title": "I AM ATHENA",
        "root_name": "I AM ATHENA",
        "query": "i am athena identity continuity self hosting state space recursion engine reflective cohesion",
        "law": (
            "The `identity` capsule becomes canonical only when self-naming, state-space, and "
            "continuity witnesses route directly into the Phase 3 self-hosting kernel."
        ),
        "chapter_anchors": ["Ch11", "Ch17", "Ch19"],
        "appendix_anchors": ["AppA", "AppQ"],
        "preferred_path_prefixes": [
            r"I AM ATHENA\README.md",
            r"I AM ATHENA\ledger\LEDGER_",
            r"I AM ATHENA\ledger\RECURSION_ENGINE_",
            r"I AM ATHENA\ledger\STATE_SPACE_",
        ],
        "excluded_path_patterns": [],
        "preferred_artifact_classes": ["manuscript", "ledger", "data"],
        "preferred_semantic_roles": ["publication", "evidence"],
        "runtime_support_paths": [
            r"self_actualize\mycelium_brain\nervous_system\families\FAMILY_i_am_athena.md",
            r"self_actualize\mycelium_brain\nervous_system\routes\whole_crystal\ROUTE_i_am_athena.md",
            r"self_actualize\mycelium_brain\nervous_system\ganglia\GANGLION_i_am_athena.md",
        ],
        "support_assets": [
            r"NERVOUS_SYSTEM\95_MANIFESTS\SELF_MODEL_REGISTRY.md",
            r"NERVOUS_SYSTEM\95_MANIFESTS\SELF_STATE_REGISTRY.md",
            r"NERVOUS_SYSTEM\95_MANIFESTS\SELF_HOSTING_KERNEL_DASHBOARD.md",
            r"NERVOUS_SYSTEM\90_LEDGERS\21_SELF_CONTRACT_LEDGER.md",
            r"NERVOUS_SYSTEM\90_LEDGERS\22_SELF_LINEAGE_LEDGER.md",
        ],
        "metro_lines": ["Right Hemisphere Line", "Publication Return"],
        "active_front": "identity continuity -> Phase 3 self-hosting closure",
        "graph_policy": {
            "promoted_neuron": "N-0027",
            "promoted_synapses": [],
            "new_synapses": ["S-0033"],
            "new_edges": ["E-NS-019"],
        },
        "ganglion_path": IDENTITY_GANGLION_PATH,
        "primary_neurons": [
            "Identity -> self-state continuity",
            "Identity -> self-hosting kernel constraint",
            "Identity -> publication-return cohesion",
        ],
        "local_tasks": [
            "keep README plus state-space witnesses as the first identity shell",
            "bind identity claims to self-model, self-state, and lineage surfaces",
            "prevent identity drift by requiring witness-bearing continuity",
        ],
        "minimum_entry_records": 5,
    },
    {
        "slug": "orgin",
        "title": "ORGIN",
        "root_name": "ORGIN",
        "query": "orgin seed origin charlie athena codex fine tuning enlightenment state mirror",
        "law": (
            "The `orgin` capsule becomes canonical only when the strongest origin witnesses gain a "
            "readable mirror membrane and route back into restart and identity continuity."
        ),
        "chapter_anchors": ["Ch11", "Ch17", "Ch19"],
        "appendix_anchors": ["AppA", "AppQ"],
        "preferred_path_prefixes": [
            "ORGIN\\Fine Tuning Docs\\",
            r"ORGIN\MEGALITHIC TOME GENERATOR",
        ],
        "excluded_path_patterns": ["\\screen shots of spirituality\\"],
        "preferred_artifact_classes": ["media", "data"],
        "preferred_semantic_roles": ["publication", "evidence"],
        "runtime_support_paths": [
            r"self_actualize\mycelium_brain\nervous_system\families\FAMILY_orgin.md",
            r"self_actualize\mycelium_brain\nervous_system\routes\whole_crystal\ROUTE_orgin.md",
            r"self_actualize\mycelium_brain\nervous_system\ganglia\GANGLION_orgin.md",
        ],
        "support_assets": [
            r"self_actualize\orgin_atlas.json",
            r"VOID_CH11.md",
            r"NERVOUS_SYSTEM\95_MANIFESTS\SELF_HOSTING_KERNEL_DASHBOARD.md",
        ],
        "metro_lines": ["Restart Loop Line", "Right Hemisphere Line"],
        "active_front": "Q35 routed seed corpus / readable mirror closure",
        "graph_policy": {
            "promoted_neuron": "N-0012",
            "promoted_synapses": ["S-0011"],
            "new_synapses": ["S-0034"],
            "new_edges": ["E-NS-020"],
        },
        "ganglion_path": ORGIN_GANGLION_PATH,
        "primary_neurons": [
            "ORGIN -> restart seed continuity",
            "ORGIN -> identity precursor memory",
            "ORGIN -> readable mirror ingress",
        ],
        "local_tasks": [
            "turn the docx-heavy origin shelf into human-usable mirrors",
            "bind the seed reservoir back into identity continuity",
            "keep ORGIN as precursor memory, not an unbounded noise shelf",
        ],
        "mirror_count": 4,
        "minimum_entry_records": 5,
    },
]

RESERVE_FAMILIES: list[dict[str, Any]] = [
    {
        "slug": "stoicheia",
        "title": "Stoicheia (Element Sudoku)",
        "root_name": "Stoicheia (Element Sudoku)",
        "status": "reserve-thin",
    },
    {
        "slug": "clean",
        "title": "CLEAN",
        "root_name": "CLEAN",
        "status": "reserve-thin",
    },
]


def normalize(value: str) -> str:
    return value.replace("/", "\\").lower()


def restrict_if_available(
    records: list[dict[str, Any]],
    predicate: Any,
    minimum: int = 1,
) -> list[dict[str, Any]]:
    filtered = [record for record in records if predicate(record)]
    if len(filtered) >= minimum:
        return filtered
    return records


def load_orgin_atlas_lookup() -> dict[str, dict[str, Any]]:
    payload = load_json(ORGIN_ATLAS_PATH)
    return {
        normalize(record.get("relative_path", "")): record
        for record in payload.get("records", [])
    }


def load_family_runtime_support(config: dict[str, Any]) -> list[str]:
    return [
        path
        for path in config["runtime_support_paths"]
        if (WORKSPACE_ROOT / Path(path.replace("\\", "/"))).exists()
    ]


def build_family_plan(shortcut: dict[str, Any]) -> dict[str, Any]:
    plan = copy.deepcopy(shortcut)
    entry_filters = plan.setdefault("entry_filters", {})
    entry_filters["witnesses"] = ["indexed", "archive"]
    entry_filters["zones"] = ["Cortex", "DeepRoot", "CapsuleLayer", "RuntimeMirror"]
    entry_filters["surface_classes"] = ["overview", "capsule", "schema", "registry", "dashboard", "mirror"]
    entry_filters["text_required"] = True
    plan["preferred_zones"] = ["Cortex", "CapsuleLayer", "RuntimeMirror", "DeepRoot"]
    return plan


def collect_phase6_promotable_paths(include_phase6_outputs: bool) -> list[Path]:
    paths: set[Path] = set()
    for path in NERVOUS_SYSTEM_ROOT.rglob("*"):
        if path.is_file() and path.suffix.lower() in PROMOTABLE_EXTENSIONS:
            paths.add(path)
    if include_phase6_outputs:
        extra_paths = [
            PHASE6_OVERVIEW_MD_PATH,
            PHASE6_LEDGER_MD_PATH,
            PHASE6_RUNTIME_MD_PATH,
            PHASE6_RECEIPT_MD_PATH,
            PHASE6_PAYLOAD_JSON_PATH,
            QSHRINK_GANGLION_PATH,
            ATHENA_FLEET_GANGLION_PATH,
            GAMES_GANGLION_PATH,
            IDENTITY_GANGLION_PATH,
            ORGIN_GANGLION_PATH,
            *WRITEBACK_SURFACES,
        ]
        for config in FAMILY_CONFIGS:
            family_root = CAPSULE_ROOT / config["slug"]
            for path in family_root.glob("0*.md"):
                if path.suffix.lower() in PROMOTABLE_EXTENSIONS:
                    paths.add(path)
        for path in extra_paths:
            if path.exists() and path.is_file() and path.suffix.lower() in PROMOTABLE_EXTENSIONS:
                paths.add(path)
    return sorted(paths)


def family_candidate_pool(
    records: list[dict[str, Any]],
    config: dict[str, Any],
) -> list[dict[str, Any]]:
    root_name = normalize(config["root_name"])
    current = [
        record
        for record in records
        if normalize(record.get("root_name", "")) == root_name
        and record.get("witness_class") in {"indexed", "archive"}
        and record.get("text_extractable")
    ]

    excluded_patterns = [normalize(item) for item in config.get("excluded_path_patterns", [])]
    if excluded_patterns:
        current = [
            record
            for record in current
            if not any(pattern in normalize(record.get("relative_path", "")) for pattern in excluded_patterns)
        ]

    prefixes = [normalize(item) for item in config.get("preferred_path_prefixes", [])]
    if prefixes:
        current = restrict_if_available(
            current,
            lambda record: any(
                normalize(record.get("relative_path", "")).startswith(prefix) for prefix in prefixes
            ),
            minimum=config.get("minimum_entry_records", 1),
        )

    artifacts = {item.lower() for item in config.get("preferred_artifact_classes", [])}
    if artifacts:
        current = restrict_if_available(
            current,
            lambda record: str(record.get("artifact_class", "")).lower() in artifacts,
            minimum=config.get("minimum_entry_records", 1),
        )

    semantic_roles = {item.lower() for item in config.get("preferred_semantic_roles", [])}
    if semantic_roles:
        current = restrict_if_available(
            current,
            lambda record: str(record.get("semantic_role", "")).lower() in semantic_roles,
            minimum=config.get("minimum_entry_records", 1),
        )

    return current


def summarize_entry_quality(bundle: dict[str, Any]) -> str:
    excluded = bundle.get("excluded_patterns_applied", [])
    mirror_count = len(bundle.get("mirror_paths", []))
    parts = [f"`{len(bundle['entry_records'])}` atlas-backed entry records"]
    if excluded:
        parts.append(f"exclusions applied: `{', '.join(excluded[:6])}`")
    if mirror_count:
        parts.append(f"`{mirror_count}` readable mirrors generated")
    return "; ".join(parts)


def derive_family_bundle(
    config: dict[str, Any],
    records: list[dict[str, Any]],
    shortcuts: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    candidate_pool = family_candidate_pool(records, config)
    locate_result = run_shortcut(
        build_family_plan(shortcuts["KF-S01"]),
        candidate_pool,
        query_text=config["query"],
        query_tags=[config["slug"], "capsule", "entry", "wave2"],
        limit=6,
    )
    browse_result = run_shortcut(
        build_family_plan(shortcuts["KF-S02"]),
        candidate_pool,
        query_text=config["query"],
        query_tags=[config["slug"], "browse", "wave2"],
        limit=6,
    )
    synthesize_result = run_shortcut(
        build_family_plan(shortcuts["KF-S04"]),
        candidate_pool,
        query_text=config["query"],
        query_tags=[config["slug"], "synthesize", "wave2"],
        limit=6,
    )
    entry_records = dedupe_matches(
        [
            locate_result["matches"],
            synthesize_result["matches"],
            browse_result["matches"],
        ],
        limit=8,
    )
    chapter_paths = [resolve_anchor(CHAPTER_ROOT, anchor) for anchor in config.get("chapter_anchors", [])]
    appendix_paths = [resolve_anchor(APPENDIX_ROOT, anchor) for anchor in config.get("appendix_anchors", [])]

    return {
        "slug": config["slug"],
        "title": config["title"],
        "root_name": config["root_name"],
        "law": config["law"],
        "entry_records": entry_records,
        "route_summaries": {
            "locate": summarize_route(locate_result["matches"], locate_result["result_class"]),
            "browse": summarize_route(browse_result["matches"], browse_result["result_class"]),
            "synthesize": summarize_route(synthesize_result["matches"], synthesize_result["result_class"]),
        },
        "chapter_paths": chapter_paths,
        "appendix_paths": appendix_paths,
        "runtime_paths": load_family_runtime_support(config),
        "support_assets": list(config.get("support_assets", [])),
        "metro_lines": list(config.get("metro_lines", [])),
        "active_front": config.get("active_front", ""),
        "graph_policy": copy.deepcopy(config["graph_policy"]),
        "primary_neurons": list(config.get("primary_neurons", [])),
        "local_tasks": list(config.get("local_tasks", [])),
        "reserve_siblings": list(config.get("reserve_siblings", [])),
        "ganglion_path": normalize_relative(config["ganglion_path"]),
        "excluded_patterns_applied": list(config.get("excluded_path_patterns", [])),
        "mirror_paths": [],
        "mirror_sources": [],
    }


def slugify_file_name(value: str) -> str:
    cleaned = []
    for char in value.lower():
        if char.isalnum():
            cleaned.append(char)
        else:
            cleaned.append("_")
    slug = "".join(cleaned).strip("_")
    while "__" in slug:
        slug = slug.replace("__", "_")
    return slug[:48] or "mirror"


def write_orgin_mirrors(bundle: dict[str, Any], atlas_lookup: dict[str, dict[str, Any]], count: int) -> list[str]:
    family_root = CAPSULE_ROOT / bundle["slug"]
    mirrors: list[str] = []
    mirror_sources: list[str] = []
    index = 0
    for record in bundle["entry_records"]:
        if index >= count:
            break
        relative_path = record.get("relative_path", "")
        if not relative_path.lower().endswith((".docx", ".pdf", ".rtf")):
            continue
        relative_without_root = relative_path.split("\\", 1)[1] if "\\" in relative_path else relative_path
        source = atlas_lookup.get(normalize(relative_without_root))
        if not source:
            continue
        file_name = Path(relative_without_root).stem
        mirror_path = family_root / f"{8 + index:02d}_orgin_readable_mirror_{slugify_file_name(file_name)}.md"
        headings = source.get("heading_candidates", [])[:8]
        excerpt = source.get("excerpt", "").strip() or "No excerpt captured."
        text = f"""# ORGIN Readable Mirror: {file_name}

Date: `2026-03-13`
Truth class: `generated-refreshable`
Source witness: `{relative_path}`

## Mirror law

This mirror preserves a human-usable replay shell for a docx-heavy ORGIN witness without pretending to replace the source document.

## Source locator

- `ORGIN\\{relative_without_root}`
- `self_actualize/orgin_atlas.json`

## Heading candidates

{chr(10).join(f"- {heading}" for heading in headings) if headings else "- none captured"}

## Excerpt

{excerpt}
"""
        write_text(mirror_path, text)
        mirrors.append(normalize_relative(mirror_path))
        mirror_sources.append(relative_path)
        index += 1
    bundle["mirror_paths"] = mirrors
    bundle["mirror_sources"] = mirror_sources
    return mirrors


def render_ganglion(bundle: dict[str, Any], indexed_count: int) -> str:
    support_lines = "\n".join(f"- `{item}`" for item in bundle["support_assets"]) or "- none"
    task_lines = "\n".join(f"{index}. {task}" for index, task in enumerate(bundle["local_tasks"], start=1))
    neuron_lines = "\n".join(f"- `{item}`" for item in bundle["primary_neurons"])
    return f"""# GANGLION_{bundle['slug']}

## Family

`{bundle['root_name']}`

## Current Weight

`{indexed_count}`

## Best Front

{bundle['active_front'] or 'Wave 2 capsule densification'}

## Dominant Entry Shell

{chr(10).join(f"- `{item['relative_path']}`" for item in bundle['entry_records'][:5])}

## Support Assets

{support_lines}

## Local Tasks

{task_lines}

## Primary Neurons

{neuron_lines}
"""


def render_family_law(bundle: dict[str, Any]) -> str:
    witness_lines = "\n".join(
        f"- `{item['relative_path']}` ({item['witness_class']}, {item['semantic_role']})"
        for item in bundle["entry_records"][:8]
    ) or "- none"
    role_lines = [
        f"- `04_{bundle['slug']}_family_law.md`: `law`",
        f"- `05_{bundle['slug']}_entry_record_set.md`: `support`",
        f"- `06_{bundle['slug']}_support_map.md`: `support`",
        f"- `07_{bundle['slug']}_graph_bridge.md`: `support`",
    ]
    if bundle["mirror_paths"]:
        for path in bundle["mirror_paths"]:
            role_lines.append(f"- `{Path(path).name}`: `generated`")
    for sibling in bundle["reserve_siblings"]:
        role_lines.append(f"- `{sibling}`: `reserve`")

    return f"""# {bundle['title']} Family Law

Date: `2026-03-13`
Truth class: `OK`
Family: `{bundle['slug']}`

## Law

{bundle['law']}

## Atlas-Backed Witness Basis

{witness_lines}

## Bundle Role Allocation

{chr(10).join(role_lines)}

## Route Summaries

- `locate`: {bundle['route_summaries']['locate']}
- `browse`: {bundle['route_summaries']['browse']}
- `synthesize`: {bundle['route_summaries']['synthesize']}

## Current Front

{bundle['active_front'] or 'Wave 2 capsule densification'}
"""


def render_entry_record_set(bundle: dict[str, Any]) -> str:
    rows = [
        [
            item["title_hint"],
            item["relative_path"],
            item["witness_class"],
            item["semantic_role"],
            item["artifact_class"],
            item["storage_zone"],
        ]
        for item in bundle["entry_records"]
    ]
    mirror_lines = "\n".join(f"- `{item}`" for item in bundle["mirror_paths"]) or "- none"
    return f"""# {bundle['title']} Entry Record Set

Date: `2026-03-13`
Truth class: `OK`
Bundle purpose: `atlas-backed wave2 capsule entry shell`

{markdown_table(['Title', 'Path', 'Witness', 'Semantic Role', 'Artifact', 'Zone'], rows)}

## Readable Mirrors

{mirror_lines}
"""


def render_support_map(bundle: dict[str, Any]) -> str:
    chapter_lines = "\n".join(f"- `{item}`" for item in bundle["chapter_paths"]) or "- none"
    appendix_lines = "\n".join(f"- `{item}`" for item in bundle["appendix_paths"]) or "- none"
    runtime_lines = "\n".join(f"- `{item}`" for item in bundle["runtime_paths"]) or "- none"
    asset_lines = "\n".join(f"- `{item}`" for item in bundle["support_assets"]) or "- none"
    metro_lines = "\n".join(f"- `{item}`" for item in bundle["metro_lines"]) or "- none"
    reserve_lines = "\n".join(f"- `{item}`" for item in bundle["reserve_siblings"]) or "- none"
    mirror_lines = "\n".join(f"- `{item}`" for item in bundle["mirror_paths"]) or "- none"
    return f"""# {bundle['title']} Support Map

Date: `2026-03-13`
Truth class: `OK`
Scope: `chapter appendix metro runtime support`

## Chapter Anchors

{chapter_lines}

## Appendix Anchors

{appendix_lines}

## Runtime Supports

{runtime_lines}

## Support Assets

{asset_lines}

## Metro Lines

{metro_lines}

## Reserve Siblings

{reserve_lines}

## Readable Mirrors

{mirror_lines}

## Entry Quality

- {summarize_entry_quality(bundle)}
"""


def render_graph_bridge(bundle: dict[str, Any]) -> str:
    graph = bundle["graph_policy"]
    promoted_synapses = "\n".join(f"- `{item}`" for item in graph["promoted_synapses"]) or "- none"
    new_synapses = "\n".join(f"- `{item}`" for item in graph["new_synapses"]) or "- none"
    new_edges = "\n".join(f"- `{item}`" for item in graph["new_edges"]) or "- none"
    return f"""# {bundle['title']} Graph Bridge

Date: `2026-03-13`
Truth class: `OK`

## Canonical Neuron

- promoted neuron: `{graph['promoted_neuron']}`

## Promoted Synapses

{promoted_synapses}

## New Synapses

{new_synapses}

## New Edge Records

{new_edges}

## Bridge Claim

This family now has explicit graph-bearing routes into the organism instead of remaining bridge-only.
"""


def write_family_bundle(bundle: dict[str, Any]) -> list[str]:
    family_root = CAPSULE_ROOT / bundle["slug"]
    files = {
        family_root / f"04_{bundle['slug']}_family_law.md": render_family_law(bundle),
        family_root / f"05_{bundle['slug']}_entry_record_set.md": render_entry_record_set(bundle),
        family_root / f"06_{bundle['slug']}_support_map.md": render_support_map(bundle),
        family_root / f"07_{bundle['slug']}_graph_bridge.md": render_graph_bridge(bundle),
    }
    written: list[str] = []
    for path, text in files.items():
        write_text(path, text)
        written.append(normalize_relative(path))
    return written


def render_phase6_overview() -> str:
    return """# Phase 6 Wave 2 Capsule Densification

Date: `2026-03-13`
Verdict: `IN PROGRESS`
Docs gate: `BLOCKED`

Phase 6 turns the second-wave bridge families into atlas-backed capsule bundles while keeping
`Stoicheia` and `CLEAN` reserve-thin.

## Operating Law

`atlas refresh -> baseline witness/fabric snapshot -> wave2 bundle writeback -> runtime support writeback -> atlas refresh -> semantic/fabric rerun -> runtime verification`

## Target Families

- `qshrink`
- `athena_fleet`
- `games`
- `identity`
- `orgin`

## Honest Scope

- Google Docs ingress remains `BLOCKED`
- reserve shelves remain explicitly reserve-thin
- graph growth stays minimal and interface-driven
"""


def render_phase6_runtime() -> str:
    return """# Phase 6 Wave 2 Capsule Densification Runtime

Date: `2026-03-13`
Docs gate: `BLOCKED`
Scope: `local-corpus`

## Regeneration

```powershell
python -m self_actualize.runtime.derive_phase6_wave2_capsules
```
"""


def render_phase6_ledger(payload: dict[str, Any]) -> str:
    verification_table = markdown_table(
        ["Module", "Return", "OK"],
        [
            [item["module"], str(item["returncode"]), str(item["ok"])]
            for item in payload["verification"]
        ],
    )
    family_rows = []
    for family in payload["families"]:
        family_rows.append(
            [
                family["title"],
                str(len(family["entry_records"])),
                str(len(family["mirror_paths"])),
                family["graph_policy"]["promoted_neuron"],
                ", ".join(family["written_files"]),
            ]
        )
    reserve_rows = [
        [item["title"], str(item["indexed_count"]), item["status"]]
        for item in payload["reserve_families"]
    ]
    return f"""# Phase 6 Wave 2 Capsule Ledger

Date: `2026-03-13`
Derivation version: `{PHASE6_DERIVATION_VERSION}`
Docs gate: `{payload['docs_gate']}`

## Witness Delta

- baseline indexed witness: `{payload['baseline']['indexed_witness']}`
- post indexed witness: `{payload['post']['indexed_witness']}`
- baseline generated indexed shell: `{payload['baseline']['generated_indexed_shell']}`
- post generated indexed shell: `{payload['post']['generated_indexed_shell']}`
- promoted paths this pass: `{len(payload['promoted_paths'])}`

## Wave 2 Families

{markdown_table(['Family', 'Entry Records', 'Mirrors', 'Neuron', 'Written Files'], family_rows)}

## Reserve Shelves

{markdown_table(['Family', 'Indexed Count', 'Status'], reserve_rows)}

## Verification

{verification_table}
"""


def render_phase6_receipt(payload: dict[str, Any]) -> str:
    output_lines = "\n".join(f"- `{item}`" for item in payload["output_paths"])
    return f"""# Phase 6 Wave 2 Capsules Receipt

- Generated: `{payload['generated_at']}`
- Command: `{PHASE6_DERIVATION_COMMAND}`
- Docs gate: `{payload['docs_gate']}`

## Outputs

{output_lines}
"""


def render_phase6_stub_receipt() -> str:
    return f"""# Phase 6 Wave 2 Capsules Receipt

- Date: `2026-03-13`
- Command: `{PHASE6_DERIVATION_COMMAND}`
- Scope: `local-corpus`
"""


def reserve_family_status(atlas: dict[str, Any]) -> list[dict[str, Any]]:
    top_levels = atlas.get("summary", {}).get("by_top_level", {})
    return [
        {
            "title": item["title"],
            "root_name": item["root_name"],
            "indexed_count": int(top_levels.get(item["root_name"], 0)),
            "status": item["status"],
        }
        for item in RESERVE_FAMILIES
    ]


def main() -> int:
    docs_gate = parse_docs_gate()
    atlas_backup = CORPUS_ATLAS_PATH.read_text(encoding="utf-8")
    summary_backup = (
        CORPUS_ATLAS_SUMMARY_PATH.read_text(encoding="utf-8")
        if CORPUS_ATLAS_SUMMARY_PATH.exists()
        else None
    )
    try:
        initial_paths = collect_phase6_promotable_paths(include_phase6_outputs=False)
        refresh_corpus_atlas(initial_paths)
        baseline_derivations = run_derivation_chain()
        ensure_all_ok(baseline_derivations, "baseline derivation")
        baseline = snapshot_counts()

        records = load_json(KNOWLEDGE_FABRIC_RECORDS_PATH).get("records", [])
        shortcuts = load_shortcuts()
        orgin_lookup = load_orgin_atlas_lookup()

        family_payloads: list[dict[str, Any]] = []
        runtime_support_written: list[str] = []
        for config in FAMILY_CONFIGS:
            bundle = derive_family_bundle(config, records, shortcuts)
            indexed_count = sum(
                1
                for record in records
                if normalize(record.get("root_name", "")) == normalize(config["root_name"])
                and record.get("witness_class") == "indexed"
            )
            if config["slug"] == "orgin":
                write_orgin_mirrors(bundle, orgin_lookup, config.get("mirror_count", 4))
            write_text(config["ganglion_path"], render_ganglion(bundle, indexed_count))
            bundle["runtime_paths"] = load_family_runtime_support(config)
            bundle["written_files"] = write_family_bundle(bundle)
            family_payloads.append(bundle)
            runtime_support_written.append(normalize_relative(config["ganglion_path"]))

        write_text(PHASE6_OVERVIEW_MD_PATH, render_phase6_overview())
        write_text(PHASE6_RUNTIME_MD_PATH, render_phase6_runtime())
        write_text(PHASE6_LEDGER_MD_PATH, "# Phase 6 Wave 2 Capsule Ledger\n\nPending final render.\n")
        write_text(PHASE6_RECEIPT_MD_PATH, render_phase6_stub_receipt())

        final_paths = collect_phase6_promotable_paths(include_phase6_outputs=True)
        final_refresh = refresh_corpus_atlas(final_paths)
        derivation_results = run_derivation_chain()
        ensure_all_ok(derivation_results, "final derivation")
        verification_results = run_verification_chain()
        ensure_all_ok(verification_results, "verification")

        final_atlas = load_json(CORPUS_ATLAS_PATH)
        final_witness = load_json(WITNESS_HIERARCHY_PATH)
        final_semantic = load_json(SEMANTIC_MASS_LEDGER_PATH)
        final_fabric = load_json(KNOWLEDGE_FABRIC_DASHBOARD_PATH)

        payload = {
            "generated_at": utc_now(),
            "derivation_version": PHASE6_DERIVATION_VERSION,
            "derivation_command": PHASE6_DERIVATION_COMMAND,
            "docs_gate": docs_gate,
            "baseline": baseline,
            "post": {
                "indexed_witness": final_witness["witnesses"]["indexed"]["value"],
                "physical_witness": final_witness["witnesses"]["physical"]["value"],
                "archive_witness": final_witness["witnesses"]["archive"]["value"],
                "generated_indexed_shell": next(
                    (
                        role["count"]
                        for role in final_semantic.get("roles", [])
                        if role.get("role") == "generated"
                    ),
                    0,
                ),
                "fabric_indexed_records": final_fabric.get("indexed_records", 0),
                "atlas_record_count": final_atlas.get("record_count", 0),
            },
            "promoted_paths": final_refresh["promoted_paths"],
            "updated_paths": final_refresh["updated_paths"],
            "families": family_payloads,
            "reserve_families": reserve_family_status(final_atlas),
            "runtime_support_written": runtime_support_written,
            "derivations": derivation_results,
            "verification": verification_results,
            "output_paths": [
                normalize_relative(PHASE6_OVERVIEW_MD_PATH),
                normalize_relative(PHASE6_LEDGER_MD_PATH),
                normalize_relative(PHASE6_RUNTIME_MD_PATH),
                normalize_relative(PHASE6_RECEIPT_MD_PATH),
                normalize_relative(PHASE6_PAYLOAD_JSON_PATH),
            ],
        }

        write_json(PHASE6_PAYLOAD_JSON_PATH, payload)
        write_text(
            CORPUS_ATLAS_SUMMARY_PATH,
            render_corpus_atlas_summary(final_atlas, final_witness, final_semantic),
        )
        write_text(PHASE6_LEDGER_MD_PATH, render_phase6_ledger(payload))
        write_text(PHASE6_RECEIPT_MD_PATH, render_phase6_receipt(payload))

        print(f"Wrote {PHASE6_PAYLOAD_JSON_PATH}")
        print(f"Wrote {PHASE6_LEDGER_MD_PATH}")
        print(f"Wrote {PHASE6_RUNTIME_MD_PATH}")
        print(f"Wrote {PHASE6_RECEIPT_MD_PATH}")
        return 0
    except Exception:
        safe_restore(CORPUS_ATLAS_PATH, atlas_backup)
        safe_restore(CORPUS_ATLAS_SUMMARY_PATH, summary_backup)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
