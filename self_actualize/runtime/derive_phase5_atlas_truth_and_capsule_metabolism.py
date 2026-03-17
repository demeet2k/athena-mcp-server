from __future__ import annotations

import copy
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from self_actualize.runtime.derive_crystal_remaster import build_atlas_record, summarize_corpus_atlas
from self_actualize.runtime.dimensional_backplane import apply_dimensional_backplane
from self_actualize.runtime.knowledge_fabric_query_engine import run_shortcut, summarize_route


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
NERVOUS_SYSTEM_ROOT = WORKSPACE_ROOT / "NERVOUS_SYSTEM"
MYCELIUM_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain"

CORPUS_ATLAS_PATH = SELF_ACTUALIZE_ROOT / "corpus_atlas.json"
CORPUS_ATLAS_SUMMARY_PATH = SELF_ACTUALIZE_ROOT / "corpus_atlas_summary.md"
SEMANTIC_MASS_LEDGER_PATH = SELF_ACTUALIZE_ROOT / "semantic_mass_ledger.json"
WITNESS_HIERARCHY_PATH = SELF_ACTUALIZE_ROOT / "witness_hierarchy.json"
KNOWLEDGE_FABRIC_RECORDS_PATH = SELF_ACTUALIZE_ROOT / "knowledge_fabric_records.json"
KNOWLEDGE_FABRIC_SHORTCUTS_PATH = SELF_ACTUALIZE_ROOT / "knowledge_fabric_shortcuts.json"
KNOWLEDGE_FABRIC_DASHBOARD_PATH = SELF_ACTUALIZE_ROOT / "knowledge_fabric_dashboard.json"
DOCS_GATE_PATH = SELF_ACTUALIZE_ROOT / "live_docs_gate_status.md"

PHASE5_ATLAS_DELTA_JSON_PATH = SELF_ACTUALIZE_ROOT / "phase5_atlas_truth_delta.json"
PHASE5_CAPSULE_LEDGER_JSON_PATH = SELF_ACTUALIZE_ROOT / "phase5_capsule_metabolism.json"

PHASE5_OVERVIEW_MD_PATH = (
    NERVOUS_SYSTEM_ROOT / "10_OVERVIEW" / "20_PHASE5_ATLAS_TRUTH_AND_CAPSULE_METABOLISM.md"
)
PHASE5_ATLAS_LEDGER_MD_PATH = (
    NERVOUS_SYSTEM_ROOT / "90_LEDGERS" / "35_PHASE5_ATLAS_TRUTH_DELTA_2026-03-13.md"
)
PHASE5_CAPSULE_LEDGER_MD_PATH = (
    NERVOUS_SYSTEM_ROOT / "90_LEDGERS" / "36_PHASE5_CAPSULE_METABOLISM_LEDGER_2026-03-13.md"
)
PHASE5_RUNTIME_MD_PATH = (
    MYCELIUM_ROOT / "nervous_system" / "29_phase5_atlas_truth_and_capsule_metabolism_runtime.md"
)
PHASE5_RECEIPT_MD_PATH = (
    MYCELIUM_ROOT / "receipts" / "2026-03-13_phase5_atlas_truth_and_capsule_metabolism.md"
)

CAPSULE_ROOT = NERVOUS_SYSTEM_ROOT / "50_CORPUS_CAPSULES"
CHAPTER_ROOT = NERVOUS_SYSTEM_ROOT / "30_CHAPTERS"
APPENDIX_ROOT = NERVOUS_SYSTEM_ROOT / "40_APPENDICES"

PROMOTABLE_EXTENSIONS = {".md", ".txt", ".json", ".yaml", ".yml", ".toml", ".csv", ".py"}
PHASE5_DERIVATION_VERSION = "2026-03-13.phase5-atlas-capsule-v1"
PHASE5_DERIVATION_COMMAND = (
    "python -m self_actualize.runtime.derive_phase5_atlas_truth_and_capsule_metabolism"
)

PHASE5_EXTRA_ATLAS_OUTPUTS = [
    PHASE5_OVERVIEW_MD_PATH,
    PHASE5_ATLAS_LEDGER_MD_PATH,
    PHASE5_CAPSULE_LEDGER_MD_PATH,
    PHASE5_RUNTIME_MD_PATH,
    PHASE5_RECEIPT_MD_PATH,
    PHASE5_ATLAS_DELTA_JSON_PATH,
    PHASE5_CAPSULE_LEDGER_JSON_PATH,
]

FAMILY_CONFIGS = [
    {
        "slug": "math",
        "title": "MATH",
        "root_name": "MATH",
        "query": "aqm theorem crystal computing hybrid myth math qshrink formal reservoir",
        "source_roots": [
            "MATH/FINAL FORM/",
            "MATH/LIVE_PROMOTED/",
            "MATH/FINAL FORM/FRAMEWORKS CODE/",
            "MATH/FINAL FORM/MYTH - MATH/",
        ],
        "law": (
            "The `MATH` capsule becomes canonical only when theorem bodies, promoted kernels, "
            "and myth-math explanations are discoverable through one atlas-backed entry shell."
        ),
        "chapters": ["Ch01", "Ch07", "Ch13", "Ch18"],
        "appendices": ["AppB", "AppC", "AppE", "AppM"],
        "runtime_paths": [
            "self_actualize\\mycelium_brain\\nervous_system\\ganglia\\GANGLION_math.md",
            "self_actualize\\mycelium_brain\\nervous_system\\routes\\whole_crystal\\ROUTE_math.md",
        ],
        "graph": {
            "neuron_id": "N-0023",
            "synapse_ids": ["S-0026", "S-0030"],
            "edge_ids": ["E-NS-012", "E-NS-016"],
            "metro_lines": ["Atlas-to-Replay Line", "Canonical-Bridge Line"],
        },
    },
    {
        "slug": "voynich",
        "title": "Voynich",
        "root_name": "Voynich",
        "query": "voynich vml eva full translation ambiguity proof folio equation compiler",
        "source_roots": [
            "Voynich/FULL_TRANSLATION/",
            "Voynich/vml/",
            "Voynich/eva/",
            "Voynich/NEW/",
        ],
        "law": (
            "The `Voynich` capsule stays canonical only while ambiguity, evidence hygiene, and "
            "equation-bearing translation remain tied to concrete folio witnesses."
        ),
        "chapters": ["Ch03", "Ch06", "Ch11", "Ch20"],
        "appendices": ["AppF", "AppI", "AppL", "AppM"],
        "runtime_paths": [
            "self_actualize\\mycelium_brain\\nervous_system\\families\\FAMILY_voynich.md",
            "self_actualize\\mycelium_brain\\nervous_system\\ganglia\\GANGLION_voynich.md",
            "self_actualize\\mycelium_brain\\nervous_system\\routes\\whole_crystal\\ROUTE_voynich.md",
        ],
        "graph": {
            "neuron_id": "N-0024",
            "synapse_ids": ["S-0027", "S-0030"],
            "edge_ids": ["E-NS-013", "E-NS-016"],
            "metro_lines": ["Canonical-Bridge Line", "Mythic Compression Line"],
        },
    },
    {
        "slug": "ecosystem",
        "title": "ECOSYSTEM",
        "root_name": "ECOSYSTEM",
        "query": "ecosystem governance protocol routing skills validation docs gateway operations",
        "source_roots": [
            "ECOSYSTEM/",
            "ECOSYSTEM/CPU_FRAMEWORK/",
            "ECOSYSTEM/skills/",
            "ECOSYSTEM/NERVOUS_SYSTEM/",
        ],
        "law": (
            "The `ECOSYSTEM` capsule is canonical when governance, skills, and operational "
            "protocols stay bridged to the cortex without outranking it."
        ),
        "chapters": ["Ch08", "Ch14", "Ch18", "Ch21"],
        "appendices": ["AppG", "AppK", "AppO", "AppP"],
        "runtime_paths": [
            "self_actualize\\mycelium_brain\\nervous_system\\ganglia\\GANGLION_ecosystem.md",
            "self_actualize\\mycelium_brain\\nervous_system\\routes\\whole_crystal\\ROUTE_ecosystem.md",
            "ECOSYSTEM\\NERVOUS_SYSTEM\\README.md",
        ],
        "graph": {
            "neuron_id": "N-0025",
            "synapse_ids": ["S-0028", "S-0031"],
            "edge_ids": ["E-NS-014", "E-NS-017"],
            "metro_lines": ["Canonical-Bridge Line", "Brain-Stem Line"],
        },
    },
    {
        "slug": "published_books",
        "title": "Athenachka Collective Books",
        "root_name": "Athenachka Collective Books",
        "query": "athenachka collective books publication manuscript codex metro publication return",
        "source_roots": ["Athenachka Collective Books/"],
        "law": (
            "The `published_books` capsule is canonical only when outward publication objects stay "
            "downstream of atlas-backed internal doctrine and return routes."
        ),
        "chapters": ["Ch14", "Ch18", "Ch21"],
        "appendices": ["AppO", "AppP"],
        "runtime_paths": [
            "self_actualize\\mycelium_brain\\nervous_system\\ganglia\\GANGLION_athenachka_collective_books.md",
            "self_actualize\\mycelium_brain\\nervous_system\\routes\\whole_crystal\\ROUTE_athenachka_collective_books.md",
        ],
        "graph": {
            "neuron_id": "N-0026",
            "synapse_ids": ["S-0029", "S-0031"],
            "edge_ids": ["E-NS-015", "E-NS-017"],
            "metro_lines": ["Publication Return", "Canonical-Bridge Line"],
        },
    },
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_relative(path: Path) -> str:
    return str(path.relative_to(WORKSPACE_ROOT)).replace("/", "\\")


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    head = "| " + " | ".join(headers) + " |"
    sep = "| " + " | ".join("---" for _ in headers) + " |"
    body = ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join([head, sep, *body])


def parse_docs_gate() -> str:
    text = DOCS_GATE_PATH.read_text(encoding="utf-8")
    for line in text.splitlines():
        if "Command status:" in line:
            return line.split("`")[1]
    return "UNKNOWN"


def snapshot_counts() -> dict[str, Any]:
    atlas = load_json(CORPUS_ATLAS_PATH)
    witness = load_json(WITNESS_HIERARCHY_PATH) if WITNESS_HIERARCHY_PATH.exists() else {}
    fabric = load_json(KNOWLEDGE_FABRIC_DASHBOARD_PATH) if KNOWLEDGE_FABRIC_DASHBOARD_PATH.exists() else {}
    semantic = load_json(SEMANTIC_MASS_LEDGER_PATH) if SEMANTIC_MASS_LEDGER_PATH.exists() else {}
    generated_role = next(
        (role for role in semantic.get("roles", []) if role.get("role") == "generated"),
        {"count": 0},
    )
    return {
        "atlas_generated_at": atlas.get("generated_at"),
        "indexed_witness": len(atlas.get("records", [])),
        "witness_indexed": witness.get("witnesses", {}).get("indexed", {}).get("value", 0),
        "witness_physical": witness.get("witnesses", {}).get("physical", {}).get("value", 0),
        "witness_archive": witness.get("witnesses", {}).get("archive", {}).get("value", 0),
        "generated_indexed_shell": generated_role.get("count", 0),
        "fabric_total_records": fabric.get("total_records", 0),
        "fabric_indexed_records": fabric.get("indexed_records", 0),
        "fabric_top_entries": fabric.get("top_entry_records", []),
    }


def collect_phase5_promotable_paths(include_phase5_outputs: bool) -> list[Path]:
    paths: set[Path] = set()
    for path in NERVOUS_SYSTEM_ROOT.rglob("*"):
        if path.is_file() and path.suffix.lower() in PROMOTABLE_EXTENSIONS:
            paths.add(path)
    if include_phase5_outputs:
        for path in PHASE5_EXTRA_ATLAS_OUTPUTS:
            if path.exists() and path.suffix.lower() in PROMOTABLE_EXTENSIONS:
                paths.add(path)
    return sorted(paths)


def refresh_corpus_atlas(paths: list[Path]) -> dict[str, Any]:
    atlas = load_json(CORPUS_ATLAS_PATH)
    record_map = {
        record.get("relative_path"): record
        for record in atlas.get("records", [])
        if record.get("relative_path")
    }
    before_keys = set(record_map)
    updated_paths: list[str] = []
    promoted_paths: list[str] = []
    for path in paths:
        if not path.exists() or not path.is_file():
            continue
        record = build_atlas_record(path)
        relative_path = record["relative_path"]
        if relative_path in before_keys:
            updated_paths.append(relative_path)
        else:
            promoted_paths.append(relative_path)
        record_map[relative_path] = record
    docs_gate = parse_docs_gate()
    records = [
        apply_dimensional_backplane(record_map[key], docs_gate)
        for key in sorted(record_map)
    ]
    atlas["generated_at"] = utc_now()
    atlas["record_count"] = len(records)
    atlas["records"] = records
    atlas["summary"] = summarize_corpus_atlas(records)
    write_json(CORPUS_ATLAS_PATH, atlas)
    return {
        "atlas": atlas,
        "promoted_paths": promoted_paths,
        "updated_paths": updated_paths,
    }


def run_module(module_name: str) -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, "-m", module_name],
        cwd=WORKSPACE_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return {
        "module": module_name,
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
        "ok": completed.returncode == 0,
    }


def run_verification_chain() -> list[dict[str, Any]]:
    modules = [
        "self_actualize.runtime.verify_runtime_waist",
        "self_actualize.runtime.verify_atlasforge_runtime_lane",
        "self_actualize.runtime.verify_aqm_runtime_lane",
    ]
    return [run_module(module_name) for module_name in modules]


def run_derivation_chain() -> list[dict[str, Any]]:
    modules = [
        "self_actualize.runtime.derive_semantic_mass_ledger",
        "self_actualize.runtime.derive_witness_hierarchy",
        "self_actualize.runtime.derive_knowledge_fabric",
    ]
    return [run_module(module_name) for module_name in modules]


def ensure_all_ok(results: list[dict[str, Any]], stage: str) -> None:
    failed = [result for result in results if not result["ok"]]
    if failed:
        lines = [f"{stage} failed:"]
        for item in failed:
            detail = item["stderr"] or item["stdout"] or f"returncode {item['returncode']}"
            lines.append(f"- {item['module']}: {detail}")
        raise RuntimeError("\n".join(lines))


def safe_restore(path: Path, backup: str | None) -> None:
    if backup is None:
        return
    path.write_text(backup, encoding="utf-8")


def refresh_with_guard(paths: list[Path]) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    atlas_backup = CORPUS_ATLAS_PATH.read_text(encoding="utf-8")
    summary_backup = (
        CORPUS_ATLAS_SUMMARY_PATH.read_text(encoding="utf-8")
        if CORPUS_ATLAS_SUMMARY_PATH.exists()
        else None
    )
    refresh_payload = refresh_corpus_atlas(paths)
    try:
        verifications = run_verification_chain()
        ensure_all_ok(verifications, "verification")
        derivations = run_derivation_chain()
        ensure_all_ok(derivations, "derivation")
    except Exception:
        safe_restore(CORPUS_ATLAS_PATH, atlas_backup)
        safe_restore(CORPUS_ATLAS_SUMMARY_PATH, summary_backup)
        raise
    return refresh_payload, verifications, derivations


def load_family_runtime_support(config: dict[str, Any]) -> list[str]:
    return [
        path
        for path in config["runtime_paths"]
        if (WORKSPACE_ROOT / Path(path.replace("\\", "/"))).exists()
    ]


def resolve_anchor(root: Path, prefix: str) -> str:
    matches = sorted(root.glob(f"{prefix}*"))
    if matches:
        return normalize_relative(matches[0])
    return prefix


def load_shortcuts() -> dict[str, dict[str, Any]]:
    payload = load_json(KNOWLEDGE_FABRIC_SHORTCUTS_PATH)
    return {item["shortcut_id"]: item for item in payload.get("shortcuts", [])}


def load_fabric_records() -> list[dict[str, Any]]:
    payload = load_json(KNOWLEDGE_FABRIC_RECORDS_PATH)
    return payload.get("records", [])


def build_family_plan(shortcut: dict[str, Any], root_name: str) -> dict[str, Any]:
    plan = copy.deepcopy(shortcut)
    entry_filters = plan.setdefault("entry_filters", {})
    entry_filters["roots"] = [root_name]
    entry_filters["witnesses"] = ["indexed", "archive"]
    entry_filters["zones"] = ["Cortex", "CapsuleLayer", "DeepRoot"]
    entry_filters["surface_classes"] = ["overview", "capsule", "schema", "registry"]
    entry_filters["text_required"] = True
    plan["preferred_zones"] = ["CapsuleLayer", "Cortex", "DeepRoot"]
    return plan


def dedupe_matches(match_groups: list[list[dict[str, Any]]], limit: int = 8) -> list[dict[str, Any]]:
    seen: set[str] = set()
    combined: list[dict[str, Any]] = []
    for group in match_groups:
        for item in group:
            record_id = item["record_id"]
            if record_id in seen:
                continue
            seen.add(record_id)
            combined.append(item)
            if len(combined) >= limit:
                return combined
    return combined


def derive_family_bundle(
    config: dict[str, Any],
    records: list[dict[str, Any]],
    shortcuts: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    locate_result = run_shortcut(
        build_family_plan(shortcuts["KF-S01"], config["root_name"]),
        records,
        query_text=config["query"],
        query_tags=[config["slug"], "capsule", "entry"],
        limit=6,
    )
    browse_result = run_shortcut(
        build_family_plan(shortcuts["KF-S02"], config["root_name"]),
        records,
        query_text=config["query"],
        query_tags=[config["slug"], "browse", "capsule"],
        limit=6,
    )
    synthesize_result = run_shortcut(
        build_family_plan(shortcuts["KF-S04"], config["root_name"]),
        records,
        query_text=config["query"],
        query_tags=[config["slug"], "synthesize", "capsule"],
        limit=6,
    )
    entry_records = dedupe_matches(
        [
            locate_result["matches"],
            synthesize_result["matches"],
            browse_result["matches"],
        ]
    )
    chapter_paths = [resolve_anchor(CHAPTER_ROOT, anchor) for anchor in config["chapters"]]
    appendix_paths = [resolve_anchor(APPENDIX_ROOT, anchor) for anchor in config["appendices"]]
    runtime_paths = load_family_runtime_support(config)
    return {
        "slug": config["slug"],
        "title": config["title"],
        "root_name": config["root_name"],
        "source_roots": config["source_roots"],
        "law": config["law"],
        "entry_records": entry_records,
        "route_summaries": {
            "locate": summarize_route(locate_result["matches"], locate_result["result_class"]),
            "browse": summarize_route(browse_result["matches"], browse_result["result_class"]),
            "synthesize": summarize_route(synthesize_result["matches"], synthesize_result["result_class"]),
        },
        "chapter_paths": chapter_paths,
        "appendix_paths": appendix_paths,
        "runtime_paths": runtime_paths,
        "graph": config["graph"],
    }


def render_family_law(bundle: dict[str, Any]) -> str:
    source_lines = "\n".join(f"- `{item}`" for item in bundle["source_roots"])
    witness_lines = "\n".join(
        f"- `{item['relative_path']}` ({item['witness_class']}, {item['semantic_role']})"
        for item in bundle["entry_records"][:6]
    )
    return f"""# {bundle['title']} Family Law

Date: `2026-03-13`
Truth class: `OK`
Family: `{bundle['slug']}`

## Law

{bundle['law']}

## Source Roots

{source_lines}

## Atlas-Backed Witness Basis

{witness_lines}

## Route Summaries

- `locate`: {bundle['route_summaries']['locate']}
- `browse`: {bundle['route_summaries']['browse']}
- `synthesize`: {bundle['route_summaries']['synthesize']}
"""


def render_entry_record_set(bundle: dict[str, Any]) -> str:
    rows = [
        [
            item["title_hint"],
            item["relative_path"],
            item["witness_class"],
            item["semantic_role"],
            item["storage_zone"],
        ]
        for item in bundle["entry_records"]
    ]
    return f"""# {bundle['title']} Entry Record Set

Date: `2026-03-13`
Truth class: `OK`
Bundle purpose: `atlas-backed capsule entry shell`

{markdown_table(['Title', 'Path', 'Witness', 'Semantic Role', 'Zone'], rows)}
"""


def render_support_map(bundle: dict[str, Any]) -> str:
    chapter_lines = "\n".join(f"- `{item}`" for item in bundle["chapter_paths"])
    appendix_lines = "\n".join(f"- `{item}`" for item in bundle["appendix_paths"])
    runtime_lines = "\n".join(f"- `{item}`" for item in bundle["runtime_paths"])
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

## Fabric Entry Shell

- top entry count: `{len(bundle['entry_records'])}`
- selector law: `Knowledge Fabric shortcuts choose entry records before capsule writeback`
"""


def render_graph_bridge(bundle: dict[str, Any]) -> str:
    graph = bundle["graph"]
    synapse_lines = "\n".join(f"- `{item}`" for item in graph["synapse_ids"])
    edge_lines = "\n".join(f"- `{item}`" for item in graph["edge_ids"])
    metro_lines = "\n".join(f"- `{item}`" for item in graph["metro_lines"])
    return f"""# {bundle['title']} Graph Bridge

Date: `2026-03-13`
Truth class: `OK`

## Canonical Neuron

- neuron: `{graph['neuron_id']}`

## Canonical Synapses

{synapse_lines}

## Canonical Edge Records

{edge_lines}

## Metro Lines

{metro_lines}

## Bridge Claim

This family now has explicit graph-bearing return paths into the atlas, cortex, and capsule layer instead of remaining only a seed summary.
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


def render_phase5_overview() -> str:
    return """# Phase 5 Atlas Truth And Capsule Metabolism

Date: `2026-03-13`
Verdict: `IN PROGRESS`
Docs gate: `BLOCKED`

Phase 5 does two things together:

1. refreshes the federated atlas so missing cortex control surfaces stop living as generated shell only
2. deepens the first thin capsule families using Knowledge Fabric entry shortcuts instead of ad hoc folder sweeps

## Operating Law

`atlas refresh -> runtime waist verification -> witness promotion -> fabric refresh -> capsule deepening -> graph bridge writeback`

## Main Outputs

- one atlas delta receipt in `self_actualize/phase5_atlas_truth_delta.json`
- one capsule metabolism ledger in `self_actualize/phase5_capsule_metabolism.json`
- deepened capsule bundles for `math`, `voynich`, `ecosystem`, and `published_books`

## Honest Scope

- Google Docs ingress remains `BLOCKED`
- promotion stays local-corpus only
- graph growth is partial and follows capsule interfaces rather than full saturation
"""


def render_phase5_runtime() -> str:
    return """# Phase 5 Atlas Truth And Capsule Metabolism Runtime

Date: `2026-03-13`
Docs gate: `BLOCKED`
Scope: `local-corpus`

This runtime mirror tracks the dual-track Phase 5 pass:

- atlas truth refresh
- capsule metabolism for the first four thin families

## Regeneration

```powershell
python -m self_actualize.runtime.derive_phase5_atlas_truth_and_capsule_metabolism
```
"""


def render_phase5_receipt_stub() -> str:
    return """# Phase 5 Atlas Truth And Capsule Metabolism Receipt

- Date: `2026-03-13`
- Command: `python -m self_actualize.runtime.derive_phase5_atlas_truth_and_capsule_metabolism`
- Scope: `local-corpus`

The machine-readable deltas live in:

- `self_actualize/phase5_atlas_truth_delta.json`
- `self_actualize/phase5_capsule_metabolism.json`
"""


def write_phase5_stub_docs() -> None:
    write_text(PHASE5_OVERVIEW_MD_PATH, render_phase5_overview())
    write_text(PHASE5_RUNTIME_MD_PATH, render_phase5_runtime())
    write_text(PHASE5_RECEIPT_MD_PATH, render_phase5_receipt_stub())


def render_corpus_atlas_summary(
    atlas: dict[str, Any],
    witness: dict[str, Any],
    semantic: dict[str, Any],
) -> str:
    summary = atlas.get("summary", {})
    generated_role = next(
        (role for role in semantic.get("roles", []) if role.get("role") == "generated"),
        {"count": 0},
    )
    top_levels = summary.get("by_top_level", {})
    top_lines = "\n".join(
        f"- `{name}`: `{count}`"
        for name, count in list(top_levels.items())[:20]
    )
    return f"""# Corpus Atlas Summary

Date: `2026-03-13`

## Atlas Artifact

- Source root: `{WORKSPACE_ROOT}`
- Atlas file: `{CORPUS_ATLAS_PATH}`
- Total indexed records: `{atlas.get('record_count', 0)}`
- Atlas generated at: `{atlas.get('generated_at', '')}`

## Witness Snapshot

- physical witness: `{witness['witnesses']['physical']['value']}`
- indexed witness: `{witness['witnesses']['indexed']['value']}`
- board witness: `{witness['witnesses']['board']['value']}`
- archive witness: `{witness['witnesses']['archive']['value']}`
- promoted witness: `{witness['witnesses']['promoted']['value']}`
- generated indexed shell: `{generated_role.get('count', 0)}`

## Top-Level Distribution

{top_lines}

## Immediate Read

Phase 5 has converted additional canonical cortex and capsule surfaces into atlas-backed indexed witness.
The live atlas is therefore less dependent on generated shell for its own control-plane entry surfaces, while the first thin capsule families can now point back to atlas-backed source bundles instead of only seed notes.
"""


def count_remaining_missing_cortex() -> int:
    atlas_relatives = {
        record["relative_path"]
        for record in load_json(CORPUS_ATLAS_PATH).get("records", [])
    }
    missing = 0
    for path in NERVOUS_SYSTEM_ROOT.rglob("*"):
        if path.is_file() and path.suffix.lower() in PROMOTABLE_EXTENSIONS:
            if normalize_relative(path) not in atlas_relatives:
                missing += 1
    return missing


def render_phase5_ledgers(
    atlas_delta: dict[str, Any],
    capsule_payload: dict[str, Any],
) -> tuple[str, str]:
    verification_table = markdown_table(
        ["Module", "Return", "OK"],
        [
            [item["module"], str(item["returncode"]), str(item["ok"])]
            for item in atlas_delta["verification"]
        ],
    )
    promoted_lines = "\n".join(
        f"- `{item}`" for item in atlas_delta["promoted_paths"][:40]
    ) or "- none"
    family_rows = []
    for family in capsule_payload["families"]:
        family_rows.append(
            [
                family["title"],
                str(len(family["entry_records"])),
                family["route_summaries"]["synthesize"],
                ", ".join(family["written_files"]),
            ]
        )
    atlas_markdown = f"""# Phase 5 Atlas Truth Delta

Date: `2026-03-13`
Derivation version: `{PHASE5_DERIVATION_VERSION}`
Docs gate: `{atlas_delta['docs_gate']}`

## Witness Delta

- baseline indexed witness: `{atlas_delta['baseline']['indexed_witness']}`
- post-refresh indexed witness: `{atlas_delta['post']['indexed_witness']}`
- baseline generated indexed shell: `{atlas_delta['baseline']['generated_indexed_shell']}`
- post-refresh generated indexed shell: `{atlas_delta['post']['generated_indexed_shell']}`
- promoted paths this pass: `{len(atlas_delta['promoted_paths'])}`
- remaining missing cortex text surfaces: `{atlas_delta['remaining_missing_cortex']}`

## Promotion Sample

{promoted_lines}

## Verification

{verification_table}
"""
    capsule_markdown = f"""# Phase 5 Capsule Metabolism Ledger

Date: `2026-03-13`
Derivation version: `{PHASE5_DERIVATION_VERSION}`
Docs gate: `{atlas_delta['docs_gate']}`

## Deepened Families

{markdown_table(['Family', 'Entry Records', 'Synthesize Route', 'Written Files'], family_rows)}
"""
    return atlas_markdown, capsule_markdown


def main() -> int:
    docs_gate = parse_docs_gate()
    baseline = snapshot_counts()

    initial_paths = collect_phase5_promotable_paths(include_phase5_outputs=False)
    initial_refresh, _, _ = refresh_with_guard(initial_paths)

    records = load_fabric_records()
    shortcuts = load_shortcuts()
    family_payloads: list[dict[str, Any]] = []
    for config in FAMILY_CONFIGS:
        bundle = derive_family_bundle(config, records, shortcuts)
        bundle["written_files"] = write_family_bundle(bundle)
        family_payloads.append(bundle)

    write_phase5_stub_docs()

    final_paths = collect_phase5_promotable_paths(include_phase5_outputs=True)
    final_refresh, verification_results, derivation_results = refresh_with_guard(final_paths)

    final_atlas = load_json(CORPUS_ATLAS_PATH)
    final_witness = load_json(WITNESS_HIERARCHY_PATH)
    final_semantic = load_json(SEMANTIC_MASS_LEDGER_PATH)
    final_fabric = load_json(KNOWLEDGE_FABRIC_DASHBOARD_PATH)

    atlas_delta = {
        "generated_at": utc_now(),
        "derivation_version": PHASE5_DERIVATION_VERSION,
        "derivation_command": PHASE5_DERIVATION_COMMAND,
        "docs_gate": docs_gate,
        "baseline": baseline,
        "initial_promoted_paths": initial_refresh["promoted_paths"],
        "promoted_paths": final_refresh["promoted_paths"],
        "updated_paths": final_refresh["updated_paths"],
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
        "remaining_missing_cortex": count_remaining_missing_cortex(),
        "verification": verification_results,
        "derivations": derivation_results,
        "top_entries_before": baseline.get("fabric_top_entries", [])[:8],
        "top_entries_after": final_fabric.get("top_entry_records", [])[:8],
        "promotion_classes": {
            "promote_now": len(final_refresh["promoted_paths"]),
            "generated_refreshable": len(
                [
                    item
                    for item in final_fabric.get("top_entry_records", [])
                    if item.get("witness_class") == "generated"
                ]
            ),
            "physical_stub_only": max(
                0,
                final_fabric.get("physical_stub_records", 0) - baseline.get("witness_physical", 0),
            ),
            "reserve_or_quarantine": sum(
                1
                for item in final_fabric.get("stale_zones", [])
                if item.get("zone_name") == "ReserveQuarantine"
            ),
        },
    }
    capsule_payload = {
        "generated_at": utc_now(),
        "derivation_version": PHASE5_DERIVATION_VERSION,
        "docs_gate": docs_gate,
        "families": family_payloads,
    }

    write_json(PHASE5_ATLAS_DELTA_JSON_PATH, atlas_delta)
    write_json(PHASE5_CAPSULE_LEDGER_JSON_PATH, capsule_payload)
    write_text(
        CORPUS_ATLAS_SUMMARY_PATH,
        render_corpus_atlas_summary(final_atlas, final_witness, final_semantic),
    )
    atlas_markdown, capsule_markdown = render_phase5_ledgers(atlas_delta, capsule_payload)
    write_text(PHASE5_ATLAS_LEDGER_MD_PATH, atlas_markdown)
    write_text(PHASE5_CAPSULE_LEDGER_MD_PATH, capsule_markdown)
    write_text(
        PHASE5_RECEIPT_MD_PATH,
        f"""# Phase 5 Atlas Truth And Capsule Metabolism Receipt

- Generated: `{atlas_delta['generated_at']}`
- Command: `{PHASE5_DERIVATION_COMMAND}`
- Docs gate: `{docs_gate}`

## Outputs

- `{PHASE5_ATLAS_DELTA_JSON_PATH}`
- `{PHASE5_CAPSULE_LEDGER_JSON_PATH}`
- `{PHASE5_ATLAS_LEDGER_MD_PATH}`
- `{PHASE5_CAPSULE_LEDGER_MD_PATH}`
- `{PHASE5_OVERVIEW_MD_PATH}`
- `{PHASE5_RUNTIME_MD_PATH}`
""",
    )

    print(f"Wrote {PHASE5_ATLAS_DELTA_JSON_PATH}")
    print(f"Wrote {PHASE5_CAPSULE_LEDGER_JSON_PATH}")
    print(f"Wrote {PHASE5_ATLAS_LEDGER_MD_PATH}")
    print(f"Wrote {PHASE5_CAPSULE_LEDGER_MD_PATH}")
    print(f"Wrote {PHASE5_OVERVIEW_MD_PATH}")
    print(f"Wrote {PHASE5_RUNTIME_MD_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
