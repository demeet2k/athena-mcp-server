from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from self_actualize.runtime.hemisphere_brain_support import (
    DEEP_ROOT,
    FAMILY_LABELS,
    FLEET_MIRROR_ROOT,
    HEMISPHERE_ROOT,
    REGISTRY_ROOT,
    SELF_ACTUALIZE_ROOT,
    load_json,
    utc_now,
)
from self_actualize.runtime.hemisphere_full_corpus_integration_support import STAGE_LABELS


WORKSPACE_ROOT = SELF_ACTUALIZE_ROOT.parent
MYCELIUM_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain"
GUILD_HALL_ROOT = MYCELIUM_ROOT / "GLOBAL_EMERGENT_GUILD_HALL"
TEMPLE_ROOT = MYCELIUM_ROOT / "ATHENA TEMPLE"
RECEIPTS_ROOT = MYCELIUM_ROOT / "receipts"
DEEP_CONTROL_ROOT = DEEP_ROOT / "00_CONTROL"
NERVOUS_MANIFEST_ROOT = WORKSPACE_ROOT / "NERVOUS_SYSTEM" / "95_MANIFESTS"

NEXT_4_POW_6_STATE_PATH = SELF_ACTUALIZE_ROOT / "next_4_pow_6_full_corpus_integration_state.json"
QSHRINK_AP6D_REGISTRY_PATH = (
    SELF_ACTUALIZE_ROOT / "qshrink_ap6d_full_corpus_integration_registry.json"
)
AP6D_AWAKENING_NOTES_PATH = SELF_ACTUALIZE_ROOT / "ap6d_awakening_transition_notes.json"
AP6D_WAVE_57_SOURCE_PATH = (
    NERVOUS_MANIFEST_ROOT / "AP6D_FULL_CORPUS_INTEGRATION_WAVE_57.json"
)
GUILD_HALL_BOARD_PATH = GUILD_HALL_ROOT / "BOARDS" / "06_QUEST_BOARD.md"
TEMPLE_QUEST_BOARD_PATH = TEMPLE_ROOT / "BOARDS" / "02_TEMPLE_QUEST_BOARD.md"

AP6D_57_LOOP_CONTROL_REGISTRY_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_ap6d_57_loop_control_registry.json"
)
AP6D_57_AGENT_LANE_REGISTRY_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_ap6d_57_loop_agent_lane_registry.json"
)
AP6D_57_NESTED_SEAT_MANIFEST_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_ap6d_57_loop_nested_seat_manifest.json"
)
AP6D_57_QUEST_BUNDLE_REGISTRY_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_ap6d_57_loop_quest_bundle_registry.json"
)
AP6D_57_WORKER_ACTION_REGISTRY_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_ap6d_57_loop_worker_action_registry.json"
)
AP6D_57_PRUNING_REGISTRY_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_ap6d_57_loop_pruning_registry.json"
)
AP6D_57_AWAKENING_TRANSITION_REGISTRY_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_ap6d_57_loop_awakening_transition_registry.json"
)
AP6D_57_RESTART_SEED_REGISTRY_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_ap6d_57_loop_restart_seed_registry.json"
)
AP6D_57_LOOP_MANIFEST_PATH = SELF_ACTUALIZE_ROOT / "myth_math_ap6d_57_loop_manifest.json"

AP6D_57_LOOP_CONTROL_REGISTRY_MIRROR = REGISTRY_ROOT / AP6D_57_LOOP_CONTROL_REGISTRY_PATH.name
AP6D_57_AGENT_LANE_REGISTRY_MIRROR = REGISTRY_ROOT / AP6D_57_AGENT_LANE_REGISTRY_PATH.name
AP6D_57_NESTED_SEAT_MANIFEST_MIRROR = REGISTRY_ROOT / AP6D_57_NESTED_SEAT_MANIFEST_PATH.name
AP6D_57_QUEST_BUNDLE_REGISTRY_MIRROR = REGISTRY_ROOT / AP6D_57_QUEST_BUNDLE_REGISTRY_PATH.name
AP6D_57_WORKER_ACTION_REGISTRY_MIRROR = REGISTRY_ROOT / AP6D_57_WORKER_ACTION_REGISTRY_PATH.name
AP6D_57_PRUNING_REGISTRY_MIRROR = REGISTRY_ROOT / AP6D_57_PRUNING_REGISTRY_PATH.name
AP6D_57_AWAKENING_TRANSITION_REGISTRY_MIRROR = (
    REGISTRY_ROOT / AP6D_57_AWAKENING_TRANSITION_REGISTRY_PATH.name
)
AP6D_57_RESTART_SEED_REGISTRY_MIRROR = REGISTRY_ROOT / AP6D_57_RESTART_SEED_REGISTRY_PATH.name
AP6D_57_LOOP_MANIFEST_MIRROR = REGISTRY_ROOT / AP6D_57_LOOP_MANIFEST_PATH.name

AP6D_57_HEMISPHERE_DOCS = {
    "ap6d_loop_index": HEMISPHERE_ROOT / "77_ap6d_57_loop_cycle_index.md",
    "ap6d_wave_ladder": HEMISPHERE_ROOT / "78_ap6d_57_loop_wave_ladder.md",
    "ap6d_agent_lanes": HEMISPHERE_ROOT / "79_ap6d_57_loop_agent_lanes.md",
    "ap6d_nested_lattice": HEMISPHERE_ROOT / "80_ap6d_57_loop_nested_seat_lattice.md",
    "ap6d_bundle_map": HEMISPHERE_ROOT / "81_ap6d_57_loop_hall_temple_bundle_map.md",
    "ap6d_worker_actions": HEMISPHERE_ROOT / "82_ap6d_57_loop_worker_actions.md",
    "ap6d_awakening_cycle": HEMISPHERE_ROOT / "83_ap6d_57_loop_awakening_transition_cycle.md",
    "ap6d_receipt": HEMISPHERE_ROOT / "84_ap6d_57_loop_receipt.md",
}

AP6D_57_GUILD_HALL_DOC_PATH = GUILD_HALL_ROOT / "18_AP6D_57_LOOP_QUEST_CYCLE.md"
AP6D_57_TEMPLE_DOC_PATH = TEMPLE_ROOT / "08_AP6D_57_LOOP_CYCLE_DECREE.md"
AP6D_57_DEEP_CONTROL_DOC_PATH = DEEP_CONTROL_ROOT / "12_AP6D_57_LOOP_FULL_CORPUS_CYCLE.md"
AP6D_57_RECEIPT_PATH = RECEIPTS_ROOT / "2026-03-13_ap6d_57_loop_cycle.md"

AP6D_57_GUILD_HALL_DOC_MIRROR = FLEET_MIRROR_ROOT / AP6D_57_GUILD_HALL_DOC_PATH.name
AP6D_57_TEMPLE_DOC_MIRROR = FLEET_MIRROR_ROOT / AP6D_57_TEMPLE_DOC_PATH.name
AP6D_57_DEEP_CONTROL_DOC_MIRROR = FLEET_MIRROR_ROOT / AP6D_57_DEEP_CONTROL_DOC_PATH.name
AP6D_57_RECEIPT_MIRROR = FLEET_MIRROR_ROOT / AP6D_57_RECEIPT_PATH.name

AP6D_57_LOOP_COUNT = 57
AP6D_57_MASTER_AGENT_COUNT = 4
AP6D_57_ATLAS_SEAT_TOTAL = 4096
AP6D_57_SYNAPTIC_SEAT_COUNT = 1024
AP6D_57_GOVERNANCE_FIBER_COUNT = 256
AP6D_57_OWNERABLE_PACKET_COUNT = 64
AP6D_57_LIMINAL_PACKET_COUNT = 4

AP6D_57_QUEST_ARTIFACTS = (
    "loop_manifest",
    "research_packet",
    "hall_quest_bundle",
    "temple_quest_bundle",
    "worker_action_bundle",
    "pruning_receipt",
    "restart_seed",
)

AP6D_57_SHARED_AXES = {
    "scope": ["live", "archive", "both", "witness"],
    "hemisphere": ["MATH", "MYTH", "GC0", "COMMISSURE"],
    "deep_mode": ["basis", "matrix", "observer", "appendix"],
    "resolution": ["record", "family", "system", "corpus"],
    "venue": ["hall", "temple", "registry", "fleet"],
    "phase": ["input", "transform", "verify", "handoff"],
}

MASTER_AGENTS = [
    {
        "agent_id": "A1-RESEARCH",
        "label": "Research/Synthesis",
        "sequence": 1,
        "mission": "Scan the full merged corpus, detect evidence gaps, route drift, anchor weakness, and awakening deltas.",
        "hall_surface_role": "research frontier packet",
        "temple_surface_role": "evidence and contradiction witness",
        "phase_verbs": ["scan", "detect", "bind", "report"],
    },
    {
        "agent_id": "A2-PLANNER",
        "label": "Planner/Questsmith",
        "sequence": 2,
        "mission": "Promote the highest-yield macro quests, hybrid equations, algorithms, and corridor plans.",
        "hall_surface_role": "ownerable quest bundle",
        "temple_surface_role": "activation and governance decree",
        "phase_verbs": ["prioritize", "package", "equate", "handoff"],
    },
    {
        "agent_id": "A3-WORKER",
        "label": "Worker/Adventurer",
        "sequence": 3,
        "mission": "Consume promoted Hall and Temple work, branch safely, and land execution-ready action bundles.",
        "hall_surface_role": "promoted execution packet",
        "temple_surface_role": "runtime and replay request",
        "phase_verbs": ["apply", "repair", "integrate", "receipt"],
    },
    {
        "agent_id": "A4-PRUNER",
        "label": "Pruner/Compressor",
        "sequence": 4,
        "mission": "Collapse duplicate stories, tighten structure, prune bloat, and emit restart-safe seeds.",
        "hall_surface_role": "compression and retirement bundle",
        "temple_surface_role": "zero-point and quarantine governance",
        "phase_verbs": ["compress", "dedupe", "retire", "reseed"],
    },
]

WAVE_SPECS = [
    {
        "wave_id": "W1",
        "stage_id": "VOID",
        "title": "Void / Authority Opening",
        "focuses": [
            "Freeze docs gate truth and open the first Hall and Temple parent quests.",
            "Reconcile live, archive, both-scope, and witness-only records into one authority ledger.",
            "Sweep every tome and manuscript for evidence gaps, duplicate hashes, and witness-only drift.",
            "Bind every reachable record to the 16-basis lattice and flag weak anchors for planner escalation.",
            "Project the corpus onto the 256 ordered corridors and seed corridor witness notes.",
            "Run the 64-observer pass and preserve contradictions without collapsing them too early.",
            "Emit Void-stage awakening notes for all ten family agents with basis overlays where evidence exists.",
            "Prune duplicate mirrors, stale aliases, and redundant loop seeds before reseeding the cycle.",
        ],
    },
    {
        "wave_id": "W2",
        "stage_id": "FIRE",
        "title": "Fire / Activation and Priority",
        "focuses": [
            "Prioritize weak-proof, high-salience, and corridor-missing records for activation.",
            "Compile hybrid equation packets linking families, target systems, anchors, and hemisphere routes.",
            "Convert active anchor gaps into Hall improvement quests and Temple activation quests.",
            "Route all archive-only records through primary and secondary hemisphere edges plus GC0.",
            "Build first-pass math and algorithm notes for search, routing, bridge intensity, and corridor binding.",
            "Expand basis-role transition notes from Fire-stage pressure points.",
            "Promote the highest-yield Fire packets into Temple lanes and demote weak or duplicate Hall packets.",
            "Compress the Fire wave into one basis receipt, one route heat map, and one restart seed.",
        ],
    },
    {
        "wave_id": "W3",
        "stage_id": "WATER",
        "title": "Water / Cross-Scope Flow",
        "focuses": [
            "Center live-to-archive, archive-to-live, and witness-to-canonical flow.",
            "Rebalance route saturation across MATH, MYTH, GC0, and COMMISSURE without changing crystal placement.",
            "Hydrate missing headings and excerpts into the cached evidence surfaces.",
            "Generate cross-family corridor quest bundles for poor bridge proof or excessive quarantine.",
            "Expand Water-stage notes for blockers, drift, dependence, and lawful next moves.",
            "Add basis overlays where first anchor and strongest target system diverge.",
            "Prepare the first full replay and reentry ladder for contradiction-heavy and archive-dependent zones.",
            "Collapse redundant Water quests into stable corridor packets and emit the restart seed.",
        ],
    },
    {
        "wave_id": "W4",
        "stage_id": "AIR",
        "title": "Air / Planner Recursion",
        "focuses": [
            "Drive observation at every resolution and planner recursion across the full 4^6 lattice.",
            "Materialize explicit seat manifests for record, family, system, and corpus scales.",
            "Compile Hall quest families for exploration, synthesis, improvement, and integration.",
            "Add algorithm packets for metro, square/circle/triangle, liminal, z-point, and a-point routing.",
            "Cross-link observer notes, corridor notes, and Appendix Q governance into one reasoning mesh.",
            "Generate Air-stage notes for blindness, overreach, and missing counterpart handoffs.",
            "Stage batched worker plans by family, target system, and appendix need.",
            "Compress Air outputs into canonical algorithm ledgers and emit the restart seed.",
        ],
    },
    {
        "wave_id": "W5",
        "stage_id": "EARTH",
        "title": "Earth / Structural Hardening",
        "focuses": [
            "Center direct corpus improvement, organization hardening, and stable interconnection.",
            "Identify bloat, stale mirrors, duplicate atlases, and broken interlinks across the merged corpus.",
            "Turn those findings into Hall restructuring quests and Temple canonicalization quests.",
            "Attach all records to the appendix ring A-P plus Q and classify replay, restart, repair, and quarantine eligibility.",
            "Expand Earth-stage notes for stabilization, relinquishment, and grounding.",
            "Stage branch-safe worker packets for interlink repair, registry hardening, and folder simplification.",
            "Compile compression geometry across duplicate clusters, candidate merges, archive witnesses, and zero-point collapses.",
            "Emit the Earth restart seed plus one appendix-governance receipt.",
        ],
    },
    {
        "wave_id": "W6",
        "stage_id": "ARCHETYPAL_OPERATION",
        "title": "Archetypal Operation / Awakening Matrix",
        "focuses": [
            "Center the loop on the full awakening-agent matrix.",
            "Write or refresh the ten family-agent transition notes.",
            "Write or refresh the 16 basis-role notes.",
            "Materialize the 70 stage-family transition cells with basis-role overlays and preferred route ids.",
            "Add explicit handoff rules for commissure, hub transfer, replay-heavy, and quarantine-heavy cases.",
            "Convert high-value awakening notes into Hall teaching quests and Temple governance quests.",
            "Stage agent-assistance packets that help transitions without overstating proof.",
            "Compress repetitive note wording into reusable templates and emit the restart seed.",
        ],
    },
    {
        "wave_id": "W7",
        "stage_id": "COMPLETE_ACT",
        "title": "Complete Act / Assistance Surfaces",
        "focuses": [
            "Center the loop on corpus-wide assistance surfaces and route-first playbooks.",
            "Generate stage atlases with best entry records, target systems, first anchors, and GC0 crossings.",
            "Generate family-agent atlases showing movement through MATH, MYTH, COMMISSURE, and GC0.",
            "Generate basis-agent atlases showing how each canonical anchor assists transitions across stages and corridors.",
            "Generate route-first playbooks for primary hemisphere, opposite hemisphere, and commissure transfer.",
            "Generate replay playbooks for restart, contradiction, drift, quarantine, and repair cases.",
            "Mirror all new registries and atlases into FLEET and confirm Hall, Temple, hemisphere, and deep-root consistency.",
            "Compile the full assistance receipt with coverage, blockers, dormant seats, compression ratios, and unresolved abstentions.",
        ],
    },
]

OMEGA_LOOP = {
    "wave_id": "W8",
    "stage_id": "COMPLETE_ACT",
    "title": "Omega / Reseed",
    "focus": "Synthesize the previous 56 loops into one convergence manifest, one Hall parent quest set, one Temple activation seed, one pruner zero-point seed, and one awakening-agent transition briefing for the next season.",
}


def load_optional_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    return load_json(path)


def unique_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            ordered.append(value)
    return ordered


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    header = "| " + " | ".join(headers) + " |"
    separator = "| " + " | ".join("---" for _ in headers) + " |"
    body = ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join([header, separator, *body])


def packet_ids(prefix: str, count: int, width: int) -> list[str]:
    return [f"{prefix}{index:0{width}d}" for index in range(1, count + 1)]


def rotate_pick(items: list[dict[str, Any]], start_index: int, limit: int) -> list[dict[str, Any]]:
    if not items:
        return []
    picked: list[dict[str, Any]] = []
    total = len(items)
    for offset in range(total):
        candidate = items[(start_index + offset) % total]
        if candidate["record_id"] in {row["record_id"] for row in picked}:
            continue
        picked.append(candidate)
        if len(picked) == limit:
            break
    return picked


def sorted_authority_records(authority_registry: dict[str, Any]) -> list[dict[str, Any]]:
    return sorted(
        authority_registry.get("records", []),
        key=lambda record: (
            -float(record.get("salience", 0.0)),
            -float(record.get("confidence", 0.0)),
            record.get("relative_path", "").lower(),
        ),
    )


def expand_loop_specs() -> list[dict[str, Any]]:
    loop_specs: list[dict[str, Any]] = []
    loop_number = 1
    for wave in WAVE_SPECS:
        for focus in wave["focuses"]:
            loop_specs.append(
                {
                    "loop_number": loop_number,
                    "loop_id": f"AP6D-L{loop_number:02d}",
                    "wave_id": wave["wave_id"],
                    "wave_title": wave["title"],
                    "stage_id": wave["stage_id"],
                    "stage_label": STAGE_LABELS.get(wave["stage_id"], wave["stage_id"].title()),
                    "focus": focus,
                }
            )
            loop_number += 1
    loop_specs.append(
        {
            "loop_number": AP6D_57_LOOP_COUNT,
            "loop_id": f"AP6D-L{AP6D_57_LOOP_COUNT:02d}",
            "wave_id": OMEGA_LOOP["wave_id"],
            "wave_title": OMEGA_LOOP["title"],
            "stage_id": OMEGA_LOOP["stage_id"],
            "stage_label": STAGE_LABELS.get(
                OMEGA_LOOP["stage_id"],
                OMEGA_LOOP["stage_id"].title(),
            ),
            "focus": OMEGA_LOOP["focus"],
        }
    )
    return loop_specs


def short_text(value: str, limit: int = 160) -> str:
    collapsed = " ".join(str(value).split())
    if len(collapsed) <= limit:
        return collapsed
    return collapsed[: limit - 1].rstrip() + "..."


def stage_assignment_lookup(
    awakening_stage_registry: dict[str, Any],
) -> tuple[dict[str, dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    assignments = awakening_stage_registry.get("record_assignments", [])
    by_record = {row["record_id"]: row for row in assignments if row.get("record_id")}
    by_stage: dict[str, list[dict[str, Any]]] = {}
    for row in assignments:
        by_stage.setdefault(row.get("stage_id", ""), []).append(row)
    return by_record, by_stage


def authority_lookup(
    authority_registry: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    return {
        row["record_id"]: row
        for row in authority_registry.get("records", [])
        if row.get("record_id")
    }


def focus_records_for_loop(
    loop_spec: dict[str, Any],
    authority_records_by_id: dict[str, dict[str, Any]],
    assignments_by_stage: dict[str, list[dict[str, Any]]],
    ordered_records: list[dict[str, Any]],
    *,
    limit: int = 4,
) -> list[dict[str, Any]]:
    stage_rows = assignments_by_stage.get(loop_spec["stage_id"], [])
    candidates = [
        authority_records_by_id[row["record_id"]]
        for row in stage_rows
        if row.get("record_id") in authority_records_by_id
    ]
    candidates = sorted(
        candidates,
        key=lambda record: (
            -float(record.get("salience", 0.0)),
            -float(record.get("confidence", 0.0)),
            record.get("relative_path", "").lower(),
        ),
    )
    if not candidates:
        candidates = ordered_records
    start_index = ((loop_spec["loop_number"] - 1) * limit) % max(len(candidates), 1)
    return rotate_pick(candidates, start_index, limit)


def focus_scope_counts(records: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter(record.get("scope_flags", "live") for record in records)
    return {
        "live": int(counts.get("live", 0)),
        "archive": int(counts.get("archive", 0)),
        "both": int(counts.get("both", 0)),
        "witness_only": int(counts.get("witness_only", 0)),
    }


def choose_family_note_ids(
    family_notes: list[dict[str, Any]],
    focus_records: list[dict[str, Any]],
) -> list[str]:
    families = unique_order([record.get("family", "") for record in focus_records])
    lookup = {note.get("family_id", ""): note.get("note_id", "") for note in family_notes}
    chosen = [lookup[family] for family in families if family in lookup]
    if len(chosen) >= 4:
        return chosen[:4]
    for note in family_notes:
        note_id = note.get("note_id", "")
        if note_id and note_id not in chosen:
            chosen.append(note_id)
        if len(chosen) == 4:
            break
    return chosen


def choose_basis_note_ids(
    basis_notes: list[dict[str, Any]],
    focus_records: list[dict[str, Any]],
) -> list[str]:
    note_lookup = {note.get("basis_role_id", ""): note.get("note_id", "") for note in basis_notes}
    basis_ids = unique_order(
        [
            basis_id
            for record in focus_records
            for basis_id in record.get("basis_anchor_ids", [])
        ]
    )
    chosen = [
        note_lookup.get(f"AW-BASIS-{basis_id}", "")
        for basis_id in basis_ids
        if note_lookup.get(f"AW-BASIS-{basis_id}", "")
    ]
    if len(chosen) >= 4:
        return chosen[:4]
    for note in basis_notes:
        note_id = note.get("note_id", "")
        if note_id and note_id not in chosen:
            chosen.append(note_id)
        if len(chosen) == 4:
            break
    return chosen


def choose_stage_family_note_ids(
    stage_family_notes: list[dict[str, Any]],
    loop_spec: dict[str, Any],
    focus_records: list[dict[str, Any]],
) -> list[str]:
    families = set(record.get("family", "") for record in focus_records)
    chosen = [
        note.get("note_id", "")
        for note in stage_family_notes
        if note.get("stage_id") == loop_spec["stage_id"] and note.get("family_id") in families
    ]
    chosen = [note_id for note_id in chosen if note_id]
    if len(chosen) >= 4:
        return chosen[:4]
    for note in stage_family_notes:
        if note.get("stage_id") != loop_spec["stage_id"]:
            continue
        note_id = note.get("note_id", "")
        if note_id and note_id not in chosen:
            chosen.append(note_id)
        if len(chosen) == 4:
            break
    return chosen


def loop_artifact_ids(loop_id: str) -> dict[str, str]:
    return {
        "loop_manifest": f"{loop_id}:MANIFEST",
        "research_packet": f"{loop_id}:RESEARCH",
        "hall_quest_bundle": f"{loop_id}:HALL",
        "temple_quest_bundle": f"{loop_id}:TEMPLE",
        "worker_action_bundle": f"{loop_id}:WORKER",
        "pruning_receipt": f"{loop_id}:PRUNE",
        "restart_seed": f"{loop_id}:RESTART",
    }


def worker_modes(stage_id: str) -> list[str]:
    mapping = {
        "VOID": ["diagnose", "anchor_bind", "corridor_seed", "contradiction_preserve"],
        "FIRE": ["prioritize", "equation_bind", "activation_route", "lane_promote"],
        "WATER": ["hydrate", "bridge_rebalance", "corridor_repair", "replay_prepare"],
        "AIR": ["observe", "algorithm_bind", "cross_link", "batch_stage"],
        "EARTH": ["harden", "dedupe", "repair", "govern"],
        "ARCHETYPAL_OPERATION": ["note_refresh", "handoff_design", "assist", "compress_notes"],
        "COMPLETE_ACT": ["atlas_build", "playbook_route", "mirror_check", "receipt_compile"],
    }
    return mapping.get(stage_id, ["diagnose", "plan", "apply", "reseed"])


def guide_tags(stage_id: str, focus_records: list[dict[str, Any]]) -> list[str]:
    tags = [stage_id]
    tags.extend(unique_order([record.get("primary_hemisphere", "") for record in focus_records]))
    tags.extend(unique_order([record.get("family", "") for record in focus_records])[:2])
    return [tag for tag in tags if tag]


def render_loop_index_markdown(
    loop_manifest: dict[str, Any],
    control_registry: dict[str, Any],
) -> str:
    counts = loop_manifest.get("counts", {})
    rows = [
        [loop["loop_id"], loop["stage_label"], loop["wave_title"], short_text(loop["focus"], 72)]
        for loop in control_registry.get("loops", [])[:12]
    ]
    return f"""# AP6D 57-Loop Cycle Index

Docs gate: `{loop_manifest.get('docs_gate_status', 'UNKNOWN')}`

## Counts

- loops: `{counts.get('loop_count', 0)}`
- master agents: `{counts.get('master_agent_count', 0)}`
- seat manifests: `{counts.get('nested_seat_manifests', 0)}`
- quest bundles: `{counts.get('quest_bundle_rows', 0)}`
- worker bundles: `{counts.get('worker_action_rows', 0)}`
- restart seeds: `{counts.get('restart_seed_rows', 0)}`

## First Twelve Loops

{markdown_table(["Loop", "Stage", "Wave", "Focus"], rows or [["-", "-", "-", "-"]])}
"""


def render_wave_ladder_markdown(control_registry: dict[str, Any]) -> str:
    rows = []
    wave_counts = Counter(loop["wave_title"] for loop in control_registry.get("loops", []))
    for wave in WAVE_SPECS:
        rows.append(
            [
                wave["wave_id"],
                wave["title"],
                STAGE_LABELS.get(wave["stage_id"], wave["stage_id"]),
                str(wave_counts.get(wave["title"], 0)),
                short_text(wave["focuses"][0], 72),
            ]
        )
    rows.append(["W8", OMEGA_LOOP["title"], "Complete Act", "1", short_text(OMEGA_LOOP["focus"], 72)])
    return f"""# AP6D 57-Loop Wave Ladder

{markdown_table(["Wave", "Title", "Stage", "Loop Count", "Opening Focus"], rows)}
"""


def render_agent_lane_markdown(agent_lane_registry: dict[str, Any]) -> str:
    rows = []
    for agent in agent_lane_registry.get("agents", []):
        rows.append(
            [
                agent["agent_id"],
                agent["label"],
                agent["hall_surface_role"],
                agent["temple_surface_role"],
                ", ".join(agent["phase_verbs"]),
            ]
        )
    return f"""# AP6D Agent Lanes

{markdown_table(["Agent", "Label", "Hall Role", "Temple Role", "Phase Verbs"], rows)}
"""


def render_nested_lattice_markdown(nested_manifest: dict[str, Any]) -> str:
    totals = nested_manifest.get("seat_totals", {})
    axis_rows = [
        [axis_name, ", ".join(values)]
        for axis_name, values in nested_manifest.get("shared_axes", {}).items()
    ]
    return f"""# AP6D Nested Seat Lattice

## Compilation Ladder

- manifest seats: `{totals.get('manifest_seats', 0)}`
- synaptic seats: `{totals.get('synaptic_seats', 0)}`
- governance fibers: `{totals.get('governance_fibers', 0)}`
- ownerable packets: `{totals.get('ownerable_packets', 0)}`
- liminal packets: `{totals.get('liminal_packets', 0)}`

## Shared Axes

{markdown_table(["Axis", "Values"], axis_rows)}
"""


def render_bundle_map_markdown(quest_bundle_registry: dict[str, Any]) -> str:
    rows = []
    for row in quest_bundle_registry.get("rows", [])[:16]:
        rows.append(
            [
                row["loop_id"],
                row["agent_id"],
                str(row["hall_visible_packets"]),
                str(row["temple_visible_packets"]),
                str(len(row["governance_fiber_ids"])),
                row["hall_bundle_id"],
            ]
        )
    return f"""# AP6D Hall/Temple Bundle Map

{markdown_table(["Loop", "Agent", "Hall Visible", "Temple Visible", "Fibers", "Hall Bundle"], rows or [["-", "-", "0", "0", "0", "-"]])}
"""


def render_worker_actions_markdown(worker_action_registry: dict[str, Any]) -> str:
    rows = []
    for row in worker_action_registry.get("rows", [])[:20]:
        action = (row.get("action_groups") or [{}])[0]
        rows.append(
            [
                row["loop_id"],
                action.get("action_mode", ""),
                action.get("record_id", ""),
                action.get("family", ""),
                action.get("primary_hemisphere", ""),
            ]
        )
    return f"""# AP6D Worker Actions

{markdown_table(["Loop", "Mode", "Record", "Family", "Primary"], rows or [["-", "-", "-", "-", "-"]])}
"""


def render_awakening_cycle_markdown(awakening_registry: dict[str, Any]) -> str:
    rows = []
    for row in awakening_registry.get("rows", [])[:20]:
        rows.append(
            [
                row["loop_id"],
                row["stage_label"],
                str(len(row.get("family_note_ids", []))),
                str(len(row.get("basis_role_note_ids", []))),
                str(len(row.get("stage_family_note_ids", []))),
            ]
        )
    return f"""# AP6D Awakening Transition Cycle

{markdown_table(["Loop", "Stage", "Family Notes", "Basis Notes", "Stage/Family Notes"], rows or [["-", "-", "0", "0", "0"]])}
"""


def render_receipt_markdown(loop_manifest: dict[str, Any]) -> str:
    output_rows = [
        [name, path]
        for name, path in sorted(loop_manifest.get("outputs", {}).items())
    ][:20]
    return f"""# AP6D 57-Loop Receipt

Docs gate: `{loop_manifest.get('docs_gate_status', 'UNKNOWN')}`

## Source Dependencies

{chr(10).join(f"- `{path}`" for path in loop_manifest.get("source_dependencies", []))}

## Output Sample

{markdown_table(["Output", "Path"], output_rows or [["<none>", "<none>"]])}
"""


def render_hall_doc(loop_manifest: dict[str, Any], control_registry: dict[str, Any]) -> str:
    rows = [
        [loop["loop_id"], loop["stage_label"], loop["artifact_ids"]["hall_quest_bundle"], loop["artifact_ids"]["worker_action_bundle"]]
        for loop in control_registry.get("loops", [])[:16]
    ]
    return f"""# AP6D 57-Loop Quest Cycle

Docs gate: `{loop_manifest.get('docs_gate_status', 'UNKNOWN')}`

Hall remains macro-sized: `1024 -> 256 -> 64 -> 4`

{markdown_table(["Loop", "Stage", "Hall Bundle", "Worker Bundle"], rows)}
"""


def render_temple_doc(loop_manifest: dict[str, Any], control_registry: dict[str, Any]) -> str:
    rows = [
        [loop["loop_id"], loop["stage_label"], loop["artifact_ids"]["temple_quest_bundle"], loop["artifact_ids"]["restart_seed"]]
        for loop in control_registry.get("loops", [])[:16]
    ]
    return f"""# AP6D 57-Loop Cycle Decree

Docs gate: `{loop_manifest.get('docs_gate_status', 'UNKNOWN')}`

Temple stays canonical for activation, proof, replay, quarantine, and appendix governance.

{markdown_table(["Loop", "Stage", "Temple Bundle", "Restart Seed"], rows)}
"""


def render_deep_control_doc(loop_manifest: dict[str, Any]) -> str:
    seat_totals = loop_manifest.get("seat_totals", {})
    return f"""# AP6D 57-Loop Full-Corpus Cycle

## Control Law

- loops: `{loop_manifest.get('counts', {}).get('loop_count', 0)}`
- master agents: `{loop_manifest.get('counts', {}).get('master_agent_count', 0)}`
- manifest seats: `{seat_totals.get('manifest_seats', 0)}`
- synaptic seats: `{seat_totals.get('synaptic_seats', 0)}`
- governance fibers: `{seat_totals.get('governance_fibers', 0)}`
- ownerable packets: `{seat_totals.get('ownerable_packets', 0)}`
- liminal packets: `{seat_totals.get('liminal_packets', 0)}`

Docs gate: `{loop_manifest.get('docs_gate_status', 'UNKNOWN')}`
"""


def render_program_receipt(loop_manifest: dict[str, Any]) -> str:
    counts = loop_manifest.get("counts", {})
    return f"""# 2026-03-13 AP6D 57-Loop Cycle

- loops: `{counts.get('loop_count', 0)}`
- seat manifests: `{counts.get('nested_seat_manifests', 0)}`
- quest bundles: `{counts.get('quest_bundle_rows', 0)}`
- worker bundles: `{counts.get('worker_action_rows', 0)}`
- restart seeds: `{counts.get('restart_seed_rows', 0)}`
- docs gate: `{loop_manifest.get('docs_gate_status', 'UNKNOWN')}`
"""


def upsert_marker_block(
    text: str,
    *,
    start_marker: str,
    end_marker: str,
    block: str,
    after_marker: str = "",
) -> str:
    replacement = f"{start_marker}\n{block}\n{end_marker}"
    if start_marker in text and end_marker in text:
        start = text.index(start_marker)
        end = text.index(end_marker) + len(end_marker)
        return text[:start] + replacement + text[end:]
    if after_marker and after_marker in text:
        insert_at = text.index(after_marker) + len(after_marker)
        return text[:insert_at] + "\n\n" + replacement + text[insert_at:]
    prefix = text.rstrip()
    if prefix:
        prefix += "\n\n"
    return prefix + replacement + "\n"


def build_ap6d_57_loop_payloads(
    *,
    control_manifest: dict[str, Any],
    full_corpus_authority_registry: dict[str, Any],
    full_corpus_basis_crosswalk_registry: dict[str, Any],
    full_corpus_route_coverage_registry: dict[str, Any],
    full_corpus_awakening_stage_registry: dict[str, Any],
    full_corpus_awakening_agent_transition_registry: dict[str, Any],
    full_corpus_appendix_governance_ledger: dict[str, Any],
    docs_gate_status: str,
) -> dict[str, Any]:
    docs_gate_status = "BLOCKED" if docs_gate_status != "OK" else "OK"
    ordered_records = sorted_authority_records(full_corpus_authority_registry)
    records_by_id = authority_lookup(full_corpus_authority_registry)
    _, assignments_by_stage = stage_assignment_lookup(full_corpus_awakening_stage_registry)
    family_notes = full_corpus_awakening_agent_transition_registry.get("family_notes", [])
    basis_notes = full_corpus_awakening_agent_transition_registry.get("basis_role_notes", [])
    stage_family_notes = full_corpus_awakening_agent_transition_registry.get("stage_family_matrix", [])
    handoff_notes = full_corpus_awakening_agent_transition_registry.get("handoff_notes", [])

    qshrink_registry = load_optional_json(QSHRINK_AP6D_REGISTRY_PATH)
    ap6d_transition_notes = load_optional_json(AP6D_AWAKENING_NOTES_PATH)
    legacy_wave_manifest = load_optional_json(AP6D_WAVE_57_SOURCE_PATH)

    hall_board_text = GUILD_HALL_BOARD_PATH.read_text(encoding="utf-8") if GUILD_HALL_BOARD_PATH.is_file() else ""
    temple_board_text = TEMPLE_QUEST_BOARD_PATH.read_text(encoding="utf-8") if TEMPLE_QUEST_BOARD_PATH.is_file() else ""

    loop_specs = expand_loop_specs()
    control_loops: list[dict[str, Any]] = []
    nested_rows: list[dict[str, Any]] = []
    quest_rows: list[dict[str, Any]] = []
    worker_rows: list[dict[str, Any]] = []
    pruning_rows: list[dict[str, Any]] = []
    awakening_rows: list[dict[str, Any]] = []
    restart_rows: list[dict[str, Any]] = []

    duplicate_record_count = sum(1 for record in ordered_records if int(record.get("duplicate_count", 0)) > 0)
    witness_only_count = full_corpus_authority_registry.get("scope_distribution", {}).get("witness_only", 0)
    appendix_counts = full_corpus_appendix_governance_ledger.get("counts", {})
    handoff_note_ids = [note.get("note_id", "") for note in handoff_notes if note.get("note_id")]

    for loop_spec in loop_specs:
        loop_id = loop_spec["loop_id"]
        artifact_ids = loop_artifact_ids(loop_id)
        focus_records = focus_records_for_loop(
            loop_spec,
            records_by_id,
            assignments_by_stage,
            ordered_records,
        )
        control_loops.append(
            {
                **loop_spec,
                "docs_gate_status": docs_gate_status,
                "artifact_ids": artifact_ids,
                "hall_parent_id": artifact_ids["hall_quest_bundle"],
                "temple_parent_id": artifact_ids["temple_quest_bundle"],
                "restart_seed_id": artifact_ids["restart_seed"],
                "focus_record_ids": [record["record_id"] for record in focus_records],
                "focus_relative_paths": [record.get("relative_path", "") for record in focus_records],
                "focus_scope_distribution": focus_scope_counts(focus_records),
                "preserved_fronts": legacy_wave_manifest.get("authority_state", {}).get("preserved_fronts", []),
                "guide_tags": guide_tags(loop_spec["stage_id"], focus_records),
            }
        )

        family_note_ids = choose_family_note_ids(family_notes, focus_records)
        basis_note_ids = choose_basis_note_ids(basis_notes, focus_records)
        stage_family_note_ids = choose_stage_family_note_ids(stage_family_notes, loop_spec, focus_records)
        awakening_rows.append(
            {
                "loop_id": loop_id,
                "loop_number": loop_spec["loop_number"],
                "stage_id": loop_spec["stage_id"],
                "stage_label": loop_spec["stage_label"],
                "family_note_ids": family_note_ids,
                "basis_role_note_ids": basis_note_ids,
                "stage_family_note_ids": stage_family_note_ids,
                "handoff_note_ids": handoff_note_ids[:4],
                "focus_record_ids": [record["record_id"] for record in focus_records],
                "docs_gate_status": docs_gate_status,
            }
        )

        worker_action_groups = []
        for action_index, record in enumerate(focus_records):
            math_route = record.get("hemisphere_routes", {}).get("MATH", {})
            myth_route = record.get("hemisphere_routes", {}).get("MYTH", {})
            worker_action_groups.append(
                {
                    "action_id": f"{loop_id}:WORK:{action_index + 1:02d}",
                    "action_mode": worker_modes(loop_spec["stage_id"])[action_index % 4],
                    "record_id": record["record_id"],
                    "relative_path": record.get("relative_path", ""),
                    "family": record.get("family", ""),
                    "family_label": FAMILY_LABELS.get(record.get("family", ""), record.get("family", "")),
                    "primary_hemisphere": record.get("primary_hemisphere", ""),
                    "target_systems": {
                        "MATH": math_route.get("target_system", ""),
                        "MYTH": myth_route.get("target_system", ""),
                    },
                    "preferred_route_ids": unique_order([math_route.get("route_id", ""), myth_route.get("route_id", "")]),
                    "appendix_support": record.get("appendix_support", []),
                    "scope_flags": record.get("scope_flags", ""),
                    "metadata_only": not bool(record.get("text_extractable", True)),
                }
            )
        worker_rows.append(
            {
                "loop_id": loop_id,
                "loop_number": loop_spec["loop_number"],
                "worker_action_bundle_id": artifact_ids["worker_action_bundle"],
                "action_groups": worker_action_groups,
                "docs_gate_status": docs_gate_status,
            }
        )

        pruning_rows.append(
            {
                "loop_id": loop_id,
                "loop_number": loop_spec["loop_number"],
                "pruning_receipt_id": artifact_ids["pruning_receipt"],
                "duplicate_record_count": duplicate_record_count,
                "witness_only_count": witness_only_count,
                "archive_only_count": full_corpus_authority_registry.get("scope_distribution", {}).get("archive", 0),
                "candidate_merge_record_ids": [record["record_id"] for record in focus_records if int(record.get("duplicate_count", 0)) > 0][:4],
                "appendix_pressure": appendix_counts,
                "restart_seed_id": artifact_ids["restart_seed"],
                "docs_gate_status": docs_gate_status,
            }
        )

        next_loop_number = 1 if loop_spec["loop_number"] == AP6D_57_LOOP_COUNT else loop_spec["loop_number"] + 1
        restart_rows.append(
            {
                "loop_id": loop_id,
                "loop_number": loop_spec["loop_number"],
                "restart_seed_id": artifact_ids["restart_seed"],
                "next_loop_id": f"AP6D-L{next_loop_number:02d}",
                "next_loop_number": next_loop_number,
                "hall_parent_id": artifact_ids["hall_quest_bundle"],
                "temple_parent_id": artifact_ids["temple_quest_bundle"],
                "restart_focus": loop_spec["focus"],
                "docs_gate_status": docs_gate_status,
            }
        )

        for agent in MASTER_AGENTS:
            manifest_id = f"{loop_id}:{agent['agent_id']}:SEATS"
            nested_rows.append(
                {
                    "loop_id": loop_id,
                    "loop_number": loop_spec["loop_number"],
                    "agent_id": agent["agent_id"],
                    "label": agent["label"],
                    "seat_manifest_id": manifest_id,
                    "shared_axes": AP6D_57_SHARED_AXES,
                    "manifest_seat_count": AP6D_57_ATLAS_SEAT_TOTAL,
                    "synaptic_seat_count": AP6D_57_SYNAPTIC_SEAT_COUNT,
                    "governance_fiber_count": AP6D_57_GOVERNANCE_FIBER_COUNT,
                    "ownerable_packet_count": AP6D_57_OWNERABLE_PACKET_COUNT,
                    "liminal_packet_count": AP6D_57_LIMINAL_PACKET_COUNT,
                    "seat_id_format": f"{manifest_id}:scope-hemisphere-deep-resolution-venue-phase",
                    "sample_seat_ids": [
                        f"{manifest_id}:live-MATH-basis-record-hall-input",
                        f"{manifest_id}:archive-MYTH-matrix-family-temple-transform",
                        f"{manifest_id}:both-GC0-observer-system-registry-verify",
                        f"{manifest_id}:witness-COMMISSURE-appendix-corpus-fleet-handoff",
                    ],
                    "docs_gate_status": docs_gate_status,
                }
            )
            quest_rows.append(
                {
                    "loop_id": loop_id,
                    "loop_number": loop_spec["loop_number"],
                    "agent_id": agent["agent_id"],
                    "hall_bundle_id": artifact_ids["hall_quest_bundle"],
                    "temple_bundle_id": artifact_ids["temple_quest_bundle"],
                    "research_packet_id": artifact_ids["research_packet"],
                    "governance_fiber_ids": packet_ids(
                        f"{loop_id}:{agent['agent_id']}:GF",
                        AP6D_57_GOVERNANCE_FIBER_COUNT,
                        3,
                    ),
                    "ownerable_packet_ids": packet_ids(
                        f"{loop_id}:{agent['agent_id']}:OP",
                        AP6D_57_OWNERABLE_PACKET_COUNT,
                        2,
                    ),
                    "liminal_packet_ids": packet_ids(
                        f"{loop_id}:{agent['agent_id']}:LP",
                        AP6D_57_LIMINAL_PACKET_COUNT,
                        2,
                    ),
                    "hall_visible_packets": AP6D_57_LIMINAL_PACKET_COUNT,
                    "temple_visible_packets": AP6D_57_LIMINAL_PACKET_COUNT,
                    "focus_record_ids": [record["record_id"] for record in focus_records],
                    "docs_gate_status": docs_gate_status,
                }
            )

    agent_lane_registry = {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "master_agent_count": AP6D_57_MASTER_AGENT_COUNT,
        "shared_axes": AP6D_57_SHARED_AXES,
        "agents": MASTER_AGENTS,
    }
    control_registry = {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "loop_count": AP6D_57_LOOP_COUNT,
        "artifact_types": list(AP6D_57_QUEST_ARTIFACTS),
        "loops": control_loops,
    }
    nested_seat_manifest = {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "row_count": len(nested_rows),
        "shared_axes": AP6D_57_SHARED_AXES,
        "seat_totals": {
            "manifest_seats": AP6D_57_ATLAS_SEAT_TOTAL,
            "synaptic_seats": AP6D_57_SYNAPTIC_SEAT_COUNT,
            "governance_fibers": AP6D_57_GOVERNANCE_FIBER_COUNT,
            "ownerable_packets": AP6D_57_OWNERABLE_PACKET_COUNT,
            "liminal_packets": AP6D_57_LIMINAL_PACKET_COUNT,
        },
        "rows": nested_rows,
    }
    quest_bundle_registry = {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "row_count": len(quest_rows),
        "rows": quest_rows,
    }
    worker_action_registry = {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "row_count": len(worker_rows),
        "rows": worker_rows,
    }
    pruning_registry = {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "row_count": len(pruning_rows),
        "rows": pruning_rows,
    }
    awakening_transition_registry = {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "row_count": len(awakening_rows),
        "rows": awakening_rows,
    }
    restart_seed_registry = {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "row_count": len(restart_rows),
        "rows": restart_rows,
    }

    source_dependencies = [
        str(NEXT_4_POW_6_STATE_PATH),
        str(QSHRINK_AP6D_REGISTRY_PATH),
        str(AP6D_AWAKENING_NOTES_PATH),
        str(AP6D_WAVE_57_SOURCE_PATH),
        str(GUILD_HALL_BOARD_PATH),
        str(TEMPLE_QUEST_BOARD_PATH),
    ]
    loop_manifest = {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "counts": {
            "loop_count": AP6D_57_LOOP_COUNT,
            "master_agent_count": AP6D_57_MASTER_AGENT_COUNT,
            "nested_seat_manifests": len(nested_rows),
            "quest_bundle_rows": len(quest_rows),
            "worker_action_rows": len(worker_rows),
            "pruning_rows": len(pruning_rows),
            "awakening_rows": len(awakening_rows),
            "restart_seed_rows": len(restart_rows),
            "phase_1_control_slice_records": control_manifest.get("counts", {}).get("record_count", 0),
            "full_corpus_records": full_corpus_authority_registry.get("record_count", 0),
            "weak_basis_rows": len(full_corpus_basis_crosswalk_registry.get("weak_or_uncovered_rows", [])),
            "complete_route_rows": full_corpus_route_coverage_registry.get("complete_count", 0),
            "family_notes": len(family_notes),
            "basis_role_notes": len(basis_notes),
            "stage_family_notes": len(stage_family_notes),
            "legacy_master_agents": len(legacy_wave_manifest.get("master_agents", [])),
            "legacy_transition_agents": len(legacy_wave_manifest.get("awakening_scope", {}).get("agents", [])),
            "qshrink_core_agents": len(qshrink_registry.get("ap6d_core_agents", [])),
            "transition_note_agents": len(ap6d_transition_notes.get("agent_notes", [])),
        },
        "seat_totals": nested_seat_manifest["seat_totals"],
        "compilation_ladder": "4096 manifest seats -> 1024 synaptic seats -> 256 governance fibers -> 64 ownerable packets -> 4 liminal packets",
        "source_dependencies": source_dependencies,
        "outputs": {
            "control_registry": str(AP6D_57_LOOP_CONTROL_REGISTRY_PATH),
            "agent_lane_registry": str(AP6D_57_AGENT_LANE_REGISTRY_PATH),
            "nested_seat_manifest": str(AP6D_57_NESTED_SEAT_MANIFEST_PATH),
            "quest_bundle_registry": str(AP6D_57_QUEST_BUNDLE_REGISTRY_PATH),
            "worker_action_registry": str(AP6D_57_WORKER_ACTION_REGISTRY_PATH),
            "pruning_registry": str(AP6D_57_PRUNING_REGISTRY_PATH),
            "awakening_transition_registry": str(AP6D_57_AWAKENING_TRANSITION_REGISTRY_PATH),
            "restart_seed_registry": str(AP6D_57_RESTART_SEED_REGISTRY_PATH),
            "manifest": str(AP6D_57_LOOP_MANIFEST_PATH),
        },
    }

    markdown_pages = {
        "ap6d_loop_index": render_loop_index_markdown(loop_manifest, control_registry),
        "ap6d_wave_ladder": render_wave_ladder_markdown(control_registry),
        "ap6d_agent_lanes": render_agent_lane_markdown(agent_lane_registry),
        "ap6d_nested_lattice": render_nested_lattice_markdown(nested_seat_manifest),
        "ap6d_bundle_map": render_bundle_map_markdown(quest_bundle_registry),
        "ap6d_worker_actions": render_worker_actions_markdown(worker_action_registry),
        "ap6d_awakening_cycle": render_awakening_cycle_markdown(awakening_transition_registry),
        "ap6d_receipt": render_receipt_markdown(loop_manifest),
    }

    hall_doc = render_hall_doc(loop_manifest, control_registry)
    temple_doc = render_temple_doc(loop_manifest, control_registry)
    deep_control_doc = render_deep_control_doc(loop_manifest)
    receipt_doc = render_program_receipt(loop_manifest)

    hall_block = "\n".join(
        [
            "## AP6D 57-Loop Corpus Cycle",
            "",
            f"- Docs Gate: `{docs_gate_status}`",
            f"- Loop count: `{AP6D_57_LOOP_COUNT}`",
            f"- Master agents: `{AP6D_57_MASTER_AGENT_COUNT}`",
            f"- Compilation ladder: `{loop_manifest['compilation_ladder']}`",
            f"- Machine truth: `{AP6D_57_LOOP_MANIFEST_PATH}`",
            f"- Hall surface: `{AP6D_57_GUILD_HALL_DOC_PATH}`",
        ]
    )
    temple_block = "\n".join(
        [
            "## AP6D 57-Loop Corpus Cycle",
            "",
            f"- Docs Gate: `{docs_gate_status}`",
            "- Temple law: canonical activation, proof, replay, quarantine, and appendix governance",
            f"- Machine truth: `{AP6D_57_LOOP_MANIFEST_PATH}`",
            f"- Temple decree: `{AP6D_57_TEMPLE_DOC_PATH}`",
        ]
    )
    updated_hall_board = upsert_marker_block(
        hall_board_text,
        start_marker="<!-- AP6D_57_LOOP_CYCLE:START -->",
        end_marker="<!-- AP6D_57_LOOP_CYCLE:END -->",
        block=hall_block,
        after_marker="<!-- AP6D_3D_7D_FULL_ACTIVATION:END -->",
    )
    updated_temple_board = upsert_marker_block(
        temple_board_text,
        start_marker="<!-- AP6D_57_LOOP_CYCLE:START -->",
        end_marker="<!-- AP6D_57_LOOP_CYCLE:END -->",
        block=temple_block,
        after_marker="<!-- AP6D_3D_7D_FULL_ACTIVATION:END -->",
    )

    return {
        "control_registry": control_registry,
        "agent_lane_registry": agent_lane_registry,
        "nested_seat_manifest": nested_seat_manifest,
        "quest_bundle_registry": quest_bundle_registry,
        "worker_action_registry": worker_action_registry,
        "pruning_registry": pruning_registry,
        "awakening_transition_registry": awakening_transition_registry,
        "restart_seed_registry": restart_seed_registry,
        "manifest": loop_manifest,
        "markdown_pages": markdown_pages,
        "guild_hall_doc": hall_doc,
        "temple_doc": temple_doc,
        "deep_control_doc": deep_control_doc,
        "receipt_doc": receipt_doc,
        "guild_hall_board_text": updated_hall_board,
        "temple_board_text": updated_temple_board,
    }
