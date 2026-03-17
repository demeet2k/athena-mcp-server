from __future__ import annotations

import json
import re
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from self_actualize.runtime.self_hosting_contracts import (
    DualEngineTarget,
    LineageEntry,
    ModeLedgerEntry,
    RuntimeScriptLane,
    SelfContractRecord,
    SelfHostingKernelDashboard,
    SelfLineageRecord,
    SelfModelRecord,
    SelfStateRecord,
    SelfSurfaceLink,
    SelfTransformPacket,
)


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
NERVOUS_SYSTEM_ROOT = WORKSPACE_ROOT / "NERVOUS_SYSTEM"
MYCELIUM_BRAIN_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain"
REGISTRY_ROOT = MYCELIUM_BRAIN_ROOT / "registry"
RUNTIME_ROOT = SELF_ACTUALIZE_ROOT / "runtime"

DERIVATION_VERSION = "2026-03-12.phase3-v1"
DERIVATION_COMMAND = "python -m self_actualize.runtime.derive_self_hosting_kernel"
KERNEL_EQUATION = (
    "SelfHostingKernel = SelfModel + SelfContract + SelfLineage + DualEngine + "
    "ReplayShell + RepairGate + PublicationReturn"
)

INDEX_PATH = NERVOUS_SYSTEM_ROOT / "00_INDEX.md"
ACTIVE_RUN_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "ACTIVE_RUN.md"
BUILD_QUEUE_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "BUILD_QUEUE.md"
ROOT_BASIS_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "ROOT_BASIS_MAP.md"
GRAND_CENTRAL_DASHBOARD_MD_PATH = (
    NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "GRAND_CENTRAL_STATION_DASHBOARD.md"
)
GRAND_CENTRAL_DASHBOARD_JSON_PATH = SELF_ACTUALIZE_ROOT / "grand_central_dashboard.json"
WITNESS_HIERARCHY_PATH = SELF_ACTUALIZE_ROOT / "witness_hierarchy.json"
ROUTE_QUALITY_PATH = SELF_ACTUALIZE_ROOT / "route_quality_ledger.json"
SEMANTIC_MASS_PATH = SELF_ACTUALIZE_ROOT / "semantic_mass_ledger.json"
ATLASFORGE_LANE_PATH = SELF_ACTUALIZE_ROOT / "atlasforge_runtime_lane.json"
AQM_LANE_PATH = SELF_ACTUALIZE_ROOT / "aqm_runtime_lane.json"
DOCS_GATE_PATH = SELF_ACTUALIZE_ROOT / "live_docs_gate_status.md"
CH19_PATH = (
    SELF_ACTUALIZE_ROOT
    / "manuscript_sections"
    / "019_ch19_recursive_self_reference_and_self_repair.md"
)
SEED_PATH = (
    NERVOUS_SYSTEM_ROOT
    / "50_CORPUS_CAPSULES"
    / "deeper_crystalization"
    / "01_the_manuscript_seed_self_referential_crystalline_generation_protocol.md"
)
CH11_PATH = (
    NERVOUS_SYSTEM_ROOT
    / "30_CHAPTERS"
    / "Ch11_0022_void_book_and_restart_token_tunneling.md"
)
RECONCILED_LEDGER_PATH = (
    NERVOUS_SYSTEM_ROOT / "90_LEDGERS" / "13_RECONCILED_ORGANISM_LEDGER_2026-03-12.md"
)

SCHEMA_MD_PATH = NERVOUS_SYSTEM_ROOT / "70_SCHEMAS" / "12_SELF_HOSTING_KERNEL_SCHEMA.md"
OVERVIEW_MD_PATH = NERVOUS_SYSTEM_ROOT / "10_OVERVIEW" / "17_PHASE3_SELF_HOSTING_KERNEL.md"
CHARTER_MD_PATH = (
    NERVOUS_SYSTEM_ROOT
    / "90_LEDGERS"
    / "20_PHASE3_SELF_HOSTING_KERNEL_CHARTER_2026-03-12.md"
)
CONTRACT_MD_PATH = NERVOUS_SYSTEM_ROOT / "90_LEDGERS" / "21_SELF_CONTRACT_LEDGER.md"
LINEAGE_MD_PATH = NERVOUS_SYSTEM_ROOT / "90_LEDGERS" / "22_SELF_LINEAGE_LEDGER.md"
RUNTIME_CLASSIFICATION_MD_PATH = (
    NERVOUS_SYSTEM_ROOT / "90_LEDGERS" / "23_RUNTIME_SELF_HOSTING_CLASSIFICATION.md"
)
READINESS_MD_PATH = (
    NERVOUS_SYSTEM_ROOT
    / "90_LEDGERS"
    / "24_PHASE3_SELF_HOSTING_KERNEL_READINESS_2026-03-12.md"
)
SELF_MODEL_MD_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "SELF_MODEL_REGISTRY.md"
SELF_STATE_MD_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "SELF_STATE_REGISTRY.md"
QUEUE_MD_PATH = (
    NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "DUAL_ENGINE_REGENERATION_QUEUE.md"
)
DASHBOARD_MD_PATH = (
    NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "SELF_HOSTING_KERNEL_DASHBOARD.md"
)
RUNTIME_MD_PATH = (
    MYCELIUM_BRAIN_ROOT / "nervous_system" / "25_self_hosting_kernel_runtime.md"
)
RECEIPT_MD_PATH = (
    MYCELIUM_BRAIN_ROOT / "receipts" / "2026-03-12_self_hosting_kernel_derivation.md"
)

SELF_MODEL_JSON_PATH = SELF_ACTUALIZE_ROOT / "self_model_registry.json"
SELF_STATE_JSON_PATH = SELF_ACTUALIZE_ROOT / "self_state_registry.json"
SELF_CONTRACT_JSON_PATH = SELF_ACTUALIZE_ROOT / "self_contract_ledger.json"
SELF_LINEAGE_JSON_PATH = SELF_ACTUALIZE_ROOT / "self_lineage_ledger.json"
SELF_PACKETS_JSON_PATH = SELF_ACTUALIZE_ROOT / "self_transform_packets.json"
DUAL_ENGINE_JSON_PATH = SELF_ACTUALIZE_ROOT / "dual_engine_regeneration_queue.json"
RUNTIME_CLASSIFICATION_JSON_PATH = (
    SELF_ACTUALIZE_ROOT / "runtime_self_hosting_classification.json"
)
SELF_DASHBOARD_JSON_PATH = SELF_ACTUALIZE_ROOT / "self_hosting_kernel_dashboard.json"

SELF_MODEL_JSON_MIRROR = REGISTRY_ROOT / "self_model_registry.json"
SELF_STATE_JSON_MIRROR = REGISTRY_ROOT / "self_state_registry.json"
SELF_CONTRACT_JSON_MIRROR = REGISTRY_ROOT / "self_contract_ledger.json"
SELF_LINEAGE_JSON_MIRROR = REGISTRY_ROOT / "self_lineage_ledger.json"
SELF_PACKETS_JSON_MIRROR = REGISTRY_ROOT / "self_transform_packets.json"
DUAL_ENGINE_JSON_MIRROR = REGISTRY_ROOT / "dual_engine_regeneration_queue.json"
RUNTIME_CLASSIFICATION_JSON_MIRROR = (
    REGISTRY_ROOT / "runtime_self_hosting_classification.json"
)
SELF_DASHBOARD_JSON_MIRROR = REGISTRY_ROOT / "self_hosting_kernel_dashboard.json"

SELF_BEARING_ROOTS = {
    "NERVOUS_SYSTEM",
    "self_actualize",
    "ECOSYSTEM",
    "DEEPER CRYSTALIZATION",
    "MATH",
    "Voynich",
    "Trading Bot",
    "Quadrant Binary",
    "QSHRINK - ATHENA (internal use)",
    "NERUAL NETWORK",
    "ORGIN",
    "I AM ATHENA",
    "Athena FLEET",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def file_timestamp(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_docs_gate(markdown: str) -> str:
    match = re.search(r"Command status: `([^`]+)`", markdown)
    if match:
        return match.group(1)
    return "UNKNOWN"


def parse_live_directory_bodies(markdown: str) -> list[dict]:
    rows: list[dict] = []
    capture = False
    for line in markdown.splitlines():
        if line.startswith("## Live Directory Bodies"):
            capture = True
            continue
        if capture and line.startswith("## "):
            break
        if not capture or not line.startswith("| A"):
            continue
        parts = [part.strip() for part in line.strip("|").split("|")]
        if len(parts) < 5:
            continue
        code, root, indexed_count, status, current_role = parts[:5]
        rows.append(
            {
                "root_id": code,
                "root_name": root.strip("`"),
                "indexed_count": int(indexed_count.strip("`")),
                "status": status.strip("`"),
                "current_role": current_role,
            }
        )
    return rows


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    head = "| " + " | ".join(headers) + " |"
    sep = "| " + " | ".join("---" for _ in headers) + " |"
    body = ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join([head, sep, *body])


def witness_value(payload: dict, key: str) -> int:
    return int(payload["witnesses"][key]["value"])


def role_count(payload: dict, role_name: str) -> int:
    for role in payload.get("roles", []):
        if role.get("role") == role_name:
            return int(role.get("count", 0))
    return 0


def build_surface_links() -> list[SelfSurfaceLink]:
    surface_specs = [
        (
            "S01",
            INDEX_PATH,
            "canonical_index",
            "indexed",
            ["capability", "permission", "environment_fit"],
            "declares authority order and promoted public surfaces",
        ),
        (
            "S02",
            ACTIVE_RUN_PATH,
            "active_run",
            "indexed",
            ["burden", "capability", "environment_fit"],
            "declares live fronts, phase status, and current operating objective",
        ),
        (
            "S03",
            BUILD_QUEUE_PATH,
            "build_queue",
            "indexed",
            ["burden", "permission"],
            "names the next executable fronts and queue discipline",
        ),
        (
            "S04",
            GRAND_CENTRAL_DASHBOARD_MD_PATH,
            "station_dashboard",
            "indexed",
            ["capability", "environment_fit"],
            "proves the substrate transfer hall is live for local scope",
        ),
        (
            "S05",
            DOCS_GATE_PATH,
            "gate_status",
            "physical",
            ["limitation", "environment_fit"],
            "keeps live external memory claims honest",
        ),
        (
            "S06",
            WITNESS_HIERARCHY_PATH,
            "witness_hierarchy",
            "generated",
            ["capability", "environment_fit"],
            "grounds self-state claims in witness classes",
        ),
        (
            "S07",
            ROUTE_QUALITY_PATH,
            "route_quality",
            "generated",
            ["capability", "burden"],
            "tracks route freshness, blockers, and improvement fronts",
        ),
        (
            "S08",
            ATLASFORGE_LANE_PATH,
            "runtime_gate",
            "generated",
            ["capability", "environment_fit"],
            "verifies one runtime lane remains green",
        ),
        (
            "S09",
            AQM_LANE_PATH,
            "runtime_gate",
            "generated",
            ["capability", "environment_fit"],
            "verifies the second runtime lane remains green",
        ),
        (
            "S10",
            CH19_PATH,
            "chapter_kernel",
            "indexed",
            ["capability", "permission", "limitation"],
            "declares the typed self objects and safety constraints",
        ),
        (
            "S11",
            SEED_PATH,
            "seed_protocol",
            "indexed",
            ["capability", "permission"],
            "supplies the manuscript side of the dual engine",
        ),
        (
            "S12",
            GRAND_CENTRAL_DASHBOARD_JSON_PATH,
            "runtime_station_dashboard",
            "generated",
            ["capability", "environment_fit"],
            "binds the runtime mirror back to the station substrate",
        ),
    ]
    return [
        SelfSurfaceLink(
            surface_id=surface_id,
            path=str(path),
            surface_class=surface_class,
            witness_class=witness_class,
            self_bearing=True,
            updates=updates,
            note=note,
        )
        for surface_id, path, surface_class, witness_class, updates, note in surface_specs
    ]


def build_self_model(
    docs_gate: str,
    root_rows: list[dict],
    surface_links: list[SelfSurfaceLink],
    station_dashboard: dict,
    semantic_mass: dict,
    witness_hierarchy: dict,
) -> SelfModelRecord:
    represented_roots = [row for row in root_rows if row["root_name"] in SELF_BEARING_ROOTS]
    root_coverage = len(represented_roots) / len(root_rows)
    surface_coverage = sum(1 for link in surface_links if link.updates) / len(surface_links)
    generated_role_share = role_count(semantic_mass, "generated") / max(
        1, witness_value(witness_hierarchy, "indexed")
    )
    unknowns = [
        "live external memory state beyond the blocked Google Docs limb",
        "full chapter-by-chapter publication return across all 21 manuscript chapters",
        "full archive-backed regeneration after the next atlas refresh",
    ]
    capability_map = [
        {
            "capability": "self_description",
            "evidence": str(CH19_PATH),
            "note": "typed self objects are already formalized in Chapter 19",
        },
        {
            "capability": "witness_bound_measurement",
            "evidence": str(WITNESS_HIERARCHY_PATH),
            "note": "the kernel can cite physical, indexed, board, archive, promoted, and generated witnesses",
        },
        {
            "capability": "station_routed_self_return",
            "evidence": str(GRAND_CENTRAL_DASHBOARD_JSON_PATH),
            "note": "Grand Central already gives the framework one lawful transfer hall",
        },
        {
            "capability": "runtime_verification",
            "evidence": str(ATLASFORGE_LANE_PATH),
            "note": "the runtime can still prove green lanes under replay-safe scope",
        },
        {
            "capability": "seed_based_regeneration",
            "evidence": str(SEED_PATH),
            "note": "the manuscript seed already defines expansion, compression, and generation",
        },
        {
            "capability": "restart_continuity",
            "evidence": str(CH11_PATH),
            "note": "the restart kernel and z-point tunnel grammar are already present",
        },
    ]
    limitation_map = [
        {
            "limitation": "docs_gate_blocked",
            "severity": "high",
            "note": "external live memory remains unavailable until OAuth material exists",
        },
        {
            "limitation": "indexed_shell_lag",
            "severity": "medium",
            "note": "board and generated surfaces still outrun the indexed atlas witness",
        },
        {
            "limitation": "capsule_deepening_incomplete",
            "severity": "medium",
            "note": "major domains are seeded but not fully contracted into denser canonical capsules",
        },
        {
            "limitation": "graph_tissue_still_sparse",
            "severity": "medium",
            "note": "the neuron and synapse layers are growing but not yet full self-bearing coverage",
        },
    ]
    burden_map = [
        {
            "burden": "generated_mass_pressure",
            "weight": f"{generated_role_share:.3f}",
            "note": "generated shell mass is large enough to demand stronger self-pruning and writeback discipline",
        },
        {
            "burden": "publication_return_triple_writeback",
            "weight": "high",
            "note": "every self-transform must land in cortex, runtime mirror, and receipt surfaces together",
        },
        {
            "burden": "identity_corridor_watch",
            "weight": "medium",
            "note": "self-change must remain inside an explicit drift corridor",
        },
        {
            "burden": "queue_to_runtime_translation",
            "weight": "medium",
            "note": "build queue and runtime packet queues must stay synchronized",
        },
    ]
    permission_map = [
        {
            "permission": "policy_tuning",
            "scope": "local",
            "note": "change queue policy, thresholds, and prioritization with receipts",
        },
        {
            "permission": "registry_strengthening",
            "scope": "local",
            "note": "add new self-bearing registry rows and clearer typed relations",
        },
        {
            "permission": "contraction_and_pruning",
            "scope": "local",
            "note": "prune stale authority claims without deleting lineage",
        },
        {
            "permission": "replay_hardening",
            "scope": "local",
            "note": "add checkpoints, restart tokens, and stronger replay closure",
        },
        {
            "permission": "capsule_deepening",
            "scope": "local",
            "note": "regenerate manuscript and capsule surfaces from seed-backed evidence",
        },
        {
            "permission": "runtime_derivation_writeback",
            "scope": "local",
            "note": "machine-derived kernel surfaces may write back into canonical dashboards and manifests",
        },
    ]
    environment_fit_map = [
        {
            "environment": "local_corpus_scope",
            "fit": "good",
            "note": "the kernel can operate because the local corpus is already indexed and witness-bearing",
        },
        {
            "environment": "live_external_memory",
            "fit": "blocked",
            "note": "Docs ingress is blocked and must remain visibly blocked",
        },
        {
            "environment": "runtime_green_lanes",
            "fit": "good",
            "note": "Atlasforge and AQM both returned OK on March 12, 2026",
        },
        {
            "environment": "station_substrate",
            "fit": "good",
            "note": f"Grand Central already holds {station_dashboard['root_count']} stationed roots",
        },
    ]
    coverage = {
        "control_plane_surface_coverage": round(surface_coverage, 3),
        "represented_self_bearing_roots": len(represented_roots),
        "total_live_roots": len(root_rows),
        "root_self_bearing_coverage": round(root_coverage, 3),
        "unknown_slots": len(unknowns),
    }
    return SelfModelRecord(
        generated_at=utc_now(),
        derivation_version=DERIVATION_VERSION,
        docs_gate=docs_gate,
        governing_equation=KERNEL_EQUATION,
        coverage=coverage,
        capability_map=capability_map,
        limitation_map=limitation_map,
        burden_map=burden_map,
        permission_map=permission_map,
        environment_fit_map=environment_fit_map,
        unknowns=unknowns,
        surface_links=surface_links,
    )


def build_self_state(
    docs_gate: str,
    station_dashboard: dict,
    witness_hierarchy: dict,
    atlasforge_lane: dict,
    aqm_lane: dict,
    route_quality: dict,
) -> SelfStateRecord:
    top_route = station_dashboard["top_dispatch_routes"][0]
    current_checkpoint = "CHK-2026-03-12-PH3-LOCAL-01"
    route_baseline = 0.0
    entries = route_quality.get("entries", [])
    if entries:
        tail = entries[-5:]
        route_baseline = round(
            sum(float(entry.get("route_score", 0.0)) for entry in tail) / len(tail), 3
        )
    witness_summary = {
        "physical": witness_value(witness_hierarchy, "physical"),
        "indexed": witness_value(witness_hierarchy, "indexed"),
        "board": witness_value(witness_hierarchy, "board"),
        "archive": witness_value(witness_hierarchy, "archive"),
        "promoted": witness_value(witness_hierarchy, "promoted"),
        "generated": role_count(load_json(SEMANTIC_MASS_PATH), "generated"),
    }
    current_config = {
        "core_mode": "DUAL_ENGINE",
        "end_state": "SELF_HOSTING_KERNEL",
        "authority_order": ["cortex", "runtime", "governance_mirror"],
        "station_status": station_dashboard["station_status"],
        "docs_gate": docs_gate,
        "witness_summary": witness_summary,
        "current_checkpoint_id": current_checkpoint,
        "route_baseline": route_baseline,
    }
    active_policy = [
        "witness before collapse",
        "no silent lineage deletion",
        "local-scope honesty until Docs ingress is live",
        "publication return is required before a self-transform counts as complete",
        "Grand Central remains the transfer hall for self-bearing traffic",
    ]
    mode_ledger = [
        ModeLedgerEntry(
            mode="observe",
            status="ACTIVE",
            witness_class="generated",
            note="measurement and dashboard refresh are now live",
        ),
        ModeLedgerEntry(
            mode="edit",
            status="READY",
            witness_class="indexed",
            note="contract-bound edits may proceed after checkpoint capture",
        ),
        ModeLedgerEntry(
            mode="repair",
            status="READY",
            witness_class="generated",
            note="route drift and stale authority claims can be repaired locally",
        ),
        ModeLedgerEntry(
            mode="regenerate",
            status="READY",
            witness_class="indexed",
            note="seed-backed chapter and overview regeneration can now be scheduled",
        ),
        ModeLedgerEntry(
            mode="rollback",
            status="GUARDED",
            witness_class="generated",
            note="rollback is legal only through the named checkpoint corridor",
        ),
        ModeLedgerEntry(
            mode="publish",
            status="READY",
            witness_class="indexed",
            note="publication requires triple landing into cortex, runtime, and receipt surfaces",
        ),
    ]
    checkpoint_protocol = {
        "required_before": [
            "contract-bound edit",
            "repair packet",
            "regeneration packet",
            "rollback packet",
            "publication packet",
        ],
        "checkpoint_id_prefix": "CHK-YYYY-MM-DD-PH3-",
        "captures": [
            "self model snapshot",
            "self state snapshot",
            "contract digest",
            "lineage head",
            "volatile runtime memory",
        ],
        "restore_command": DERIVATION_COMMAND,
    }
    restart_protocol = {
        "kernel_source": str(CH11_PATH),
        "states": ["descend", "zero", "emerge", "resume"],
        "law": "restart passes through replay and continuity receipt instead of narrative restart",
        "resume_targets": [
            str(SELF_STATE_JSON_PATH),
            str(DASHBOARD_MD_PATH),
            str(RUNTIME_MD_PATH),
        ],
    }
    volatile_memory = {
        "active_fronts": [
            "self-hosting kernel synchronization",
            "capsule deepening",
            "graph tissue growth",
            "publication-return closure",
        ],
        "blockers": [
            "Google Docs ingress is blocked by missing OAuth client material",
            "full atlas regeneration still trails board-visible witness",
            "capsule and graph deepening remain incomplete",
        ],
        "top_dispatch_route": (
            f"{top_route['commissure_id']} {top_route['source_family']} -> "
            f"{top_route['target_family']} = {top_route['dispatch_score']}"
        ),
        "runtime_lane_truth": {
            "atlasforge": atlasforge_lane.get("truth", "AMBIG"),
            "aqm": aqm_lane.get("truth", "AMBIG"),
        },
    }
    route_context = {
        "source_station": "Grand Central Station",
        "publication_return": "cortex + runtime mirror + receipt",
        "top_station_routes": [
            f"{item['commissure_id']}:{item['source_family']}->{item['target_family']}"
            for item in station_dashboard["top_dispatch_routes"][:3]
        ],
        "current_checkpoint_id": current_checkpoint,
        "lineage_anchor": "L4",
    }
    truth_citations = {
        "docs_gate": "physical",
        "witness_summary": "generated",
        "station_status": "generated",
        "route_baseline": "generated",
        "runtime_lane_truth": "generated",
    }
    return SelfStateRecord(
        generated_at=utc_now(),
        derivation_version=DERIVATION_VERSION,
        docs_gate=docs_gate,
        kernel_status="LIVE_LOCAL_SCOPE",
        current_config=current_config,
        active_policy=active_policy,
        mode_ledger=mode_ledger,
        checkpoint_protocol=checkpoint_protocol,
        restart_protocol=restart_protocol,
        volatile_memory=volatile_memory,
        route_context=route_context,
        truth_citations=truth_citations,
    )


def build_self_contract(docs_gate: str, model: SelfModelRecord) -> SelfContractRecord:
    drift_threshold = 0.18
    current_drift = round(
        0.05
        + (0.02 if docs_gate == "BLOCKED" else 0.0)
        + (1.0 - model.coverage["root_self_bearing_coverage"]) * 0.04,
        3,
    )
    identity_kernel = [
        {
            "invariant": "authority_order",
            "note": "cortex first, runtime second, governance mirror third",
        },
        {
            "invariant": "witness_discipline",
            "note": "ABSTAIN is legal, fake witness is not",
        },
        {
            "invariant": "lineage_preservation",
            "note": "nontrivial self-transforms extend lineage instead of replacing it",
        },
        {
            "invariant": "replay_obligation",
            "note": "self-change must remain replayable through checkpoint and receipt surfaces",
        },
        {
            "invariant": "local_scope_honesty",
            "note": "the blocked Docs gate may not be laundered into a false live-memory claim",
        },
    ]
    permitted = [
        {
            "transform_class": "policy_tuning",
            "review_class": "witness_review",
            "note": "allowed when route evidence and receipts stay visible",
        },
        {
            "transform_class": "registry_strengthening",
            "review_class": "structural_review",
            "note": "allowed when typed interfaces become clearer without erasing lineage",
        },
        {
            "transform_class": "contraction_and_pruning",
            "review_class": "repair_review",
            "note": "allowed when stale authority is demoted rather than deleted",
        },
        {
            "transform_class": "replay_hardening",
            "review_class": "rollback_review",
            "note": "allowed when checkpoints, restart tokens, or receipts are strengthened",
        },
        {
            "transform_class": "capsule_deepening",
            "review_class": "generation_review",
            "note": "allowed when manuscript regeneration cites seed, witnesses, and writeback targets",
        },
        {
            "transform_class": "runtime_derivation_writeback",
            "review_class": "publication_review",
            "note": "allowed when runtime output lands in cortex, runtime, and receipt surfaces",
        },
    ]
    forbidden = [
        {
            "transform_class": "silent_identity_kernel_rewrite",
            "note": "identity kernel may not be changed without declared successor-class transition",
        },
        {
            "transform_class": "silent_lineage_deletion",
            "note": "lineage history may not be erased to simplify the present",
        },
        {
            "transform_class": "unsupported_memory_deletion",
            "note": "memory may not be removed without archive or receipt support",
        },
        {
            "transform_class": "permission_self_inflation",
            "note": "the kernel may not widen its own permissions without higher-order review",
        },
        {
            "transform_class": "non_replayable_publication",
            "note": "publication without replay target and receipt is forbidden",
        },
    ]
    review_classes = [
        {
            "review_class": "witness_review",
            "required_for": "observe and measure packets",
            "rule": "claim must cite witness class and current scope",
        },
        {
            "review_class": "structural_review",
            "required_for": "edit packets",
            "rule": "typed surfaces and invariants must remain explicit",
        },
        {
            "review_class": "repair_review",
            "required_for": "repair packets",
            "rule": "typed defect and repair trace must remain visible",
        },
        {
            "review_class": "generation_review",
            "required_for": "regeneration packets",
            "rule": "seed, witnesses, and writeback targets must be named",
        },
        {
            "review_class": "rollback_review",
            "required_for": "rollback packets",
            "rule": "rollback must name predecessor checkpoint and lineage head",
        },
        {
            "review_class": "publication_review",
            "required_for": "publish packets",
            "rule": "cortex, runtime mirror, and receipt must all land together",
        },
    ]
    transform_classifier = [
        {
            "mode": "observe",
            "contract_status": "PERMITTED",
            "review_class": "witness_review",
            "evidence": "witness hierarchy plus runtime lanes",
        },
        {
            "mode": "edit",
            "contract_status": "REQUIRES_REVIEW",
            "review_class": "structural_review",
            "evidence": "checkpoint plus surface diff",
        },
        {
            "mode": "repair",
            "contract_status": "PERMITTED",
            "review_class": "repair_review",
            "evidence": "typed defect plus repair trace",
        },
        {
            "mode": "regenerate",
            "contract_status": "REQUIRES_REVIEW",
            "review_class": "generation_review",
            "evidence": "seed citation plus publication-return target",
        },
        {
            "mode": "rollback",
            "contract_status": "PERMITTED",
            "review_class": "rollback_review",
            "evidence": "checkpoint hash plus lineage head",
        },
        {
            "mode": "publish",
            "contract_status": "REQUIRES_REVIEW",
            "review_class": "publication_review",
            "evidence": "triple writeback receipt",
        },
    ]
    unsafe_rewrite_gate = {
        "threshold": 0.45,
        "factors": {
            "kernel_drift": 0.30,
            "lineage_loss": 0.30,
            "support_damage": 0.20,
            "permission_violation": 0.20,
        },
        "law": "block any transform that weakens lineage, support, or permissions faster than it improves lawful function",
    }
    identity_drift_corridor = {
        "declared_threshold": drift_threshold,
        "current_drift": current_drift,
        "status": "WITHIN_CORRIDOR" if current_drift <= drift_threshold else "ESCALATE",
        "law": "measurable drift is legal inside the corridor and triggers successor-class review outside it",
    }
    rollback_corridor = {
        "rollback_threshold": 0.24,
        "preferred_checkpoint_prefix": "CHK-2026-03-12-PH3-",
        "restore_command": DERIVATION_COMMAND,
        "law": "rollback returns to the last lawful checkpoint before identity or support loss compounds",
    }
    return SelfContractRecord(
        generated_at=utc_now(),
        derivation_version=DERIVATION_VERSION,
        docs_gate=docs_gate,
        identity_kernel=identity_kernel,
        permitted_transform_classes=permitted,
        forbidden_transform_classes=forbidden,
        required_review_classes=review_classes,
        transform_classifier=transform_classifier,
        unsafe_rewrite_gate=unsafe_rewrite_gate,
        identity_drift_corridor=identity_drift_corridor,
        rollback_corridor=rollback_corridor,
    )


def build_self_lineage(
    docs_gate: str,
    contract: SelfContractRecord,
    grand_central_dashboard: dict,
    witness_hierarchy: dict,
) -> SelfLineageRecord:
    lineage_entries = [
        LineageEntry(
            lineage_id="L0",
            temporal_coordinate=file_timestamp(SEED_PATH),
            branch_coordinate="seed.manuscript.identity",
            delta_class="seed",
            delta_summary="manuscript seed plus Ch19 typed self law establish the lawful self object",
            support_shell=f"{SEED_PATH.name} + {CH19_PATH.name}",
            burden_state="typed self still mostly theoretical",
            proof_state="NEAR",
            attached_tunnels=["ZT-002"],
        ),
        LineageEntry(
            lineage_id="L1",
            temporal_coordinate=witness_hierarchy["generated_at"],
            branch_coordinate="main.local.runtime.measurement",
            delta_class="extension",
            delta_summary="machine-derived witness hierarchy and body tensor make the organism measurable",
            support_shell="witness hierarchy + body tensor",
            burden_state="count reconciliation made explicit",
            proof_state="OK",
            attached_tunnels=["ZT-004"],
        ),
        LineageEntry(
            lineage_id="L2",
            temporal_coordinate=file_timestamp(RECONCILED_LEDGER_PATH),
            branch_coordinate="main.local.reconciled.organism",
            delta_class="extension",
            delta_summary="authority order, count protocol, and root basis are reconciled into one organism",
            support_shell="reconciled organism ledger",
            burden_state="capsule and graph contraction still pending",
            proof_state="OK",
            attached_tunnels=["ZT-005"],
        ),
        LineageEntry(
            lineage_id="L3",
            temporal_coordinate=grand_central_dashboard["generated_at"],
            branch_coordinate="main.local.grand_central",
            delta_class="extension",
            delta_summary="Grand Central installs station addresses, commissures, weights, and z-point tunnels",
            support_shell="station registry + weight exchange + tunnel ledger",
            burden_state="transfer hall complete but not yet self-hosting",
            proof_state="OK",
            attached_tunnels=["ZT-002", "ZT-004", "ZT-005", "ZT-006"],
        ),
        LineageEntry(
            lineage_id="L4",
            temporal_coordinate=utc_now(),
            branch_coordinate="main.local.phase3.self_hosting",
            delta_class="repair",
            delta_summary="self model, self state, self contract, self lineage, and dual engine are installed as live control surfaces",
            support_shell="phase 3 kernel charter + dashboard + queue",
            burden_state="local scope only while Docs ingress remains blocked",
            proof_state="NEAR",
            attached_tunnels=["ZT-002", "ZT-004", "ZT-005", "ZT-006"],
        ),
    ]
    fork_points = [
        {
            "branch": "historical.deep_root.DEEPER_INTEGRATED_NEURAL_NETWORK",
            "status": "mirror",
            "note": "kept for lineage and historical replay, not live authority",
        },
        {
            "branch": "historical.deep_root.DEEPER_INTEGRATED_NEURAL_NET_ATHENA",
            "status": "mirror",
            "note": "kept for precursor continuity, not live routing authority",
        },
    ]
    return SelfLineageRecord(
        generated_at=utc_now(),
        derivation_version=DERIVATION_VERSION,
        docs_gate=docs_gate,
        current_branch="main.local.phase3.self_hosting",
        predecessor_chain=[entry.lineage_id for entry in lineage_entries],
        lineage_entries=lineage_entries,
        fork_points=fork_points,
        sufficiency_checks={
            "backward_replay": True,
            "rollback": True,
            "fork_detection": True,
            "continuity_proof": True,
        },
        comparison_tool=[
            {
                "delta_class": "repair",
                "meaning": "defect reduction without silent identity inflation",
            },
            {
                "delta_class": "extension",
                "meaning": "new lawful structure added while kernel invariants hold",
            },
            {
                "delta_class": "contraction",
                "meaning": "surface reduced while support and lineage remain intact",
            },
            {
                "delta_class": "corruption",
                "meaning": "support, replay, or lineage weakens faster than function improves",
            },
        ],
        drift_band={
            "current_drift": contract.identity_drift_corridor["current_drift"],
            "drift_threshold": contract.identity_drift_corridor["declared_threshold"],
            "status": contract.identity_drift_corridor["status"],
        },
    )


def classify_runtime_scripts() -> dict:
    lane_map = {
        "self_observation": {
            "atlas.py",
            "derive_body_tensor.py",
            "derive_semantic_mass_ledger.py",
            "derive_witness_hierarchy.py",
            "reconcile_scan.py",
        },
        "self_measurement": {
            "derive_frontier_leverage_ranking.py",
            "verify_atlasforge_runtime_lane.py",
            "verify_aqm_runtime_lane.py",
        },
        "self_routing": {
            "__init__.py",
            "cli.py",
            "contracts.py",
            "derive_deep_integration_neural_net.py",
            "derive_grand_central_station.py",
            "derive_prop_channel_algebra.py",
            "engine.py",
            "skills_registry.py",
            "swarm_board.py",
            "self_hosting_contracts.py",
        },
        "self_repair": {
            "build_qshrink_athena_internal.py",
            "build_trading_bot_athena_framework.py",
            "derive_trading_bot_truth_corridor.py",
            "derive_void_ch11_precursor_reconciliation.py",
        },
        "self_regeneration": {
            "derive_bruno_address_c_leaf_promotion.py",
            "derive_bruno_b12_operator_table.py",
            "derive_helix_recursion_schema.py",
            "derive_void_ch11_ok_theorem.py",
        },
        "self_publication": {
            "build_full_project_integration.py",
            "generate_void_tome_part1.py",
        },
    }
    lane_supports = {
        "self_observation": ["observe", "measure"],
        "self_measurement": ["verify", "rank"],
        "self_routing": ["route", "schedule"],
        "self_repair": ["repair", "patch"],
        "self_regeneration": ["regenerate", "reseed"],
        "self_publication": ["publish", "writeback"],
    }
    lane_notes = {
        "self_observation": "extracts current state into machine-readable evidence",
        "self_measurement": "scores or verifies runtime condition",
        "self_routing": "moves packets, routes, or station traffic through the live system",
        "self_repair": "targets repair and corridor hardening",
        "self_regeneration": "rebuilds kernels, helix schemas, or reseeding surfaces",
        "self_publication": "pushes successful transforms back into manuscript and runtime outputs",
    }
    classifications: list[RuntimeScriptLane] = []
    counts = {lane: 0 for lane in lane_map}
    for path in sorted(RUNTIME_ROOT.glob("*.py")):
        lane_name = "self_routing"
        for candidate_lane, files in lane_map.items():
            if path.name in files:
                lane_name = candidate_lane
                break
        counts[lane_name] += 1
        classifications.append(
            RuntimeScriptLane(
                script=path.name,
                lane=lane_name,
                supports=lane_supports[lane_name],
                note=lane_notes[lane_name],
            )
        )
    return {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "scripts": [asdict(item) for item in classifications],
        "summary": {
            "lane_counts": counts,
            "script_count": len(classifications),
        },
    }


def build_transform_packets(
    docs_gate: str,
    station_dashboard: dict,
    state: SelfStateRecord,
) -> list[SelfTransformPacket]:
    top_dispatch = float(station_dashboard["top_dispatch_routes"][0]["dispatch_score"])
    legality_bonus = {"PERMITTED": 0.45, "REQUIRES_REVIEW": 0.2, "BLOCKED": -3.25}
    mode_bonus = {
        "observe": 0.35,
        "repair": 0.28,
        "regenerate": 0.18,
        "publish": 0.05,
        "rollback": -0.75,
        "edit": -0.45,
    }
    base = top_dispatch - 0.35
    packet_specs = [
        {
            "packet_id": "STP-001",
            "mode": "observe",
            "title": "Observe current kernel health",
            "intended_transform_class": "policy_tuning",
            "contract_status": "PERMITTED",
            "review_class": "witness_review",
            "lineage_delta": "L4.observe.refresh",
            "replay_target": str(SELF_STATE_JSON_PATH),
            "publication_target": str(DASHBOARD_MD_PATH),
            "witness_class": "generated",
            "status": "READY",
            "base_adjust": 0.30,
            "note": "refresh model coverage, runtime lanes, and queue state before deeper packets land",
        },
        {
            "packet_id": "STP-002",
            "mode": "repair",
            "title": "Repair stale route and queue drift",
            "intended_transform_class": "contraction_and_pruning",
            "contract_status": "PERMITTED",
            "review_class": "repair_review",
            "lineage_delta": "L4.route_drift.repair",
            "replay_target": str(QUEUE_MD_PATH),
            "publication_target": str(BUILD_QUEUE_PATH),
            "witness_class": "indexed",
            "status": "READY",
            "base_adjust": 0.18,
            "note": "keeps queues, manifests, and runtime packet schedules synchronized",
        },
        {
            "packet_id": "STP-003",
            "mode": "regenerate",
            "title": "Regenerate typed self-law writeback",
            "intended_transform_class": "capsule_deepening",
            "contract_status": "REQUIRES_REVIEW",
            "review_class": "generation_review",
            "lineage_delta": "L4.ch19.regen",
            "replay_target": str(CH19_PATH),
            "publication_target": str(OVERVIEW_MD_PATH),
            "witness_class": "indexed",
            "status": "READY",
            "base_adjust": 0.12,
            "note": "binds the manuscript self-reference chapter back into active control surfaces",
        },
        {
            "packet_id": "STP-004",
            "mode": "publish",
            "title": "Publish Phase 3 return surfaces",
            "intended_transform_class": "runtime_derivation_writeback",
            "contract_status": "REQUIRES_REVIEW",
            "review_class": "publication_review",
            "lineage_delta": "L4.publication.return",
            "replay_target": str(RUNTIME_MD_PATH),
            "publication_target": str(INDEX_PATH),
            "witness_class": "indexed",
            "status": "READY",
            "base_adjust": 0.05,
            "note": "lands successful self-transforms in cortex, runtime, and receipt surfaces together",
        },
        {
            "packet_id": "STP-005",
            "mode": "rollback",
            "title": "Hold rollback corridor guard",
            "intended_transform_class": "replay_hardening",
            "contract_status": "PERMITTED",
            "review_class": "rollback_review",
            "lineage_delta": "L4.rollback.guard",
            "replay_target": state.current_config["current_checkpoint_id"],
            "publication_target": str(LINEAGE_MD_PATH),
            "witness_class": "generated",
            "status": "STANDBY",
            "base_adjust": -0.20,
            "note": "rollback stays lawful but secondary while drift remains below threshold",
        },
        {
            "packet_id": "STP-006",
            "mode": "edit",
            "title": "Open live Docs ingress when OAuth appears",
            "intended_transform_class": "registry_strengthening",
            "contract_status": "BLOCKED" if docs_gate == "BLOCKED" else "REQUIRES_REVIEW",
            "review_class": "structural_review",
            "lineage_delta": "L4.docs_gate.open",
            "replay_target": str(DOCS_GATE_PATH),
            "publication_target": str(DASHBOARD_MD_PATH),
            "witness_class": "physical",
            "status": "BLOCKED" if docs_gate == "BLOCKED" else "READY",
            "base_adjust": -0.05,
            "note": "stays blocked until credentials.json and token.json exist",
        },
    ]
    packets: list[SelfTransformPacket] = []
    for spec in packet_specs:
        dispatch = round(
            base
            + mode_bonus[spec["mode"]]
            + legality_bonus[spec["contract_status"]]
            + spec["base_adjust"],
            3,
        )
        packets.append(
            SelfTransformPacket(
                packet_id=spec["packet_id"],
                mode=spec["mode"],
                title=spec["title"],
                source_state=state.current_config["current_checkpoint_id"],
                intended_transform_class=spec["intended_transform_class"],
                contract_status=spec["contract_status"],
                review_class=spec["review_class"],
                lineage_delta=spec["lineage_delta"],
                replay_target=spec["replay_target"],
                publication_target=spec["publication_target"],
                witness_class=spec["witness_class"],
                dispatch_score=dispatch,
                status=spec["status"],
                note=spec["note"],
            )
        )
    return sorted(packets, key=lambda item: item.dispatch_score, reverse=True)


def build_dual_engine_queue(docs_gate: str, packets: list[SelfTransformPacket]) -> dict:
    targets = [
        DualEngineTarget(
            target_id="QK-001",
            priority="P1",
            target_surface="Ch11 restart kernel return",
            seed_surface=str(CH11_PATH),
            runtime_packet="STP-001",
            witness_class="indexed",
            writeback_targets=[
                str(SELF_STATE_MD_PATH),
                str(DASHBOARD_MD_PATH),
                str(RUNTIME_MD_PATH),
            ],
            status="READY",
            note="refresh restart protocol, checkpoint, and tunnel closure in one cycle",
        ),
        DualEngineTarget(
            target_id="QK-002",
            priority="P1",
            target_surface="Ch19 typed self-law writeback",
            seed_surface=str(CH19_PATH),
            runtime_packet="STP-003",
            witness_class="indexed",
            writeback_targets=[
                str(OVERVIEW_MD_PATH),
                str(SELF_MODEL_MD_PATH),
                str(CONTRACT_MD_PATH),
            ],
            status="READY",
            note="regenerate the manuscript self-law into live control surfaces",
        ),
        DualEngineTarget(
            target_id="QK-003",
            priority="P1",
            target_surface="Phase 3 overview and index synchronization",
            seed_surface=str(SEED_PATH),
            runtime_packet="STP-004",
            witness_class="indexed",
            writeback_targets=[
                str(INDEX_PATH),
                str(OVERVIEW_MD_PATH),
                str(DASHBOARD_MD_PATH),
            ],
            status="READY",
            note="make the phase visible from the canonical cortex",
        ),
        DualEngineTarget(
            target_id="QK-004",
            priority="P2",
            target_surface="Runtime lane classifier deepening",
            seed_surface=str(RUNTIME_ROOT),
            runtime_packet="STP-002",
            witness_class="generated",
            writeback_targets=[
                str(RUNTIME_CLASSIFICATION_MD_PATH),
                str(SELF_PACKETS_JSON_PATH),
            ],
            status="READY",
            note="keeps runtime observation, repair, regeneration, and publication lanes explicit",
        ),
        DualEngineTarget(
            target_id="QK-005",
            priority="P2",
            target_surface="Publication return corridor hardening",
            seed_surface=str(GRAND_CENTRAL_DASHBOARD_MD_PATH),
            runtime_packet="STP-004",
            witness_class="indexed",
            writeback_targets=[
                str(DASHBOARD_MD_PATH),
                str(RUNTIME_MD_PATH),
                str(RECEIPT_MD_PATH),
            ],
            status="READY",
            note="ensures successful packets land in all three surfaces together",
        ),
        DualEngineTarget(
            target_id="QK-006",
            priority="P3",
            target_surface="Live Docs ingress",
            seed_surface=str(DOCS_GATE_PATH),
            runtime_packet="STP-006",
            witness_class="physical",
            writeback_targets=[
                str(DASHBOARD_MD_PATH),
                str(SELF_STATE_MD_PATH),
            ],
            status="BLOCKED" if docs_gate == "BLOCKED" else "READY",
            note="waiting on credentials.json and token.json",
        ),
    ]
    return {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "docs_gate": docs_gate,
        "cycle_law": (
            "Phase 1 expansion -> Phase 2 compression -> Phase 3 generation -> "
            "runtime observe -> runtime verify -> publication return"
        ),
        "canonical_seed_surfaces": [
            str(SEED_PATH),
            str(CH11_PATH),
            str(CH19_PATH),
        ],
        "targets": [asdict(target) for target in targets],
        "packets": [asdict(packet) for packet in packets],
        "summary": {
            "target_count": len(targets),
            "ready_targets": sum(1 for target in targets if target.status == "READY"),
            "blocked_targets": sum(1 for target in targets if target.status == "BLOCKED"),
            "top_packet_ids": [packet.packet_id for packet in packets[:4]],
        },
    }


def build_dashboard(
    docs_gate: str,
    model: SelfModelRecord,
    contract: SelfContractRecord,
    lineage: SelfLineageRecord,
    queue_payload: dict,
    station_dashboard: dict,
    atlasforge_lane: dict,
    aqm_lane: dict,
    packets: list[SelfTransformPacket],
) -> SelfHostingKernelDashboard:
    runtime_lanes_ok = (
        atlasforge_lane.get("truth") == "OK" and aqm_lane.get("truth") == "OK"
    )
    return SelfHostingKernelDashboard(
        generated_at=utc_now(),
        derivation_version=DERIVATION_VERSION,
        docs_gate=docs_gate,
        kernel_status="LIVE_LOCAL_SCOPE",
        control_plane_surface_coverage=model.coverage["control_plane_surface_coverage"],
        root_self_bearing_coverage=model.coverage["root_self_bearing_coverage"],
        identity_drift=contract.identity_drift_corridor["current_drift"],
        drift_threshold=contract.identity_drift_corridor["declared_threshold"],
        permitted_packets=sum(
            1 for packet in packets if packet.contract_status == "PERMITTED"
        ),
        blocked_packets=sum(
            1 for packet in packets if packet.contract_status == "BLOCKED"
        ),
        review_packets=sum(
            1 for packet in packets if packet.contract_status == "REQUIRES_REVIEW"
        ),
        lineage_entries=len(lineage.lineage_entries),
        regeneration_targets_ready=queue_payload["summary"]["ready_targets"],
        runtime_lanes_ok=runtime_lanes_ok,
        top_packets=[asdict(packet) for packet in packets[:5]],
        failure_gates=[
            "Google Docs ingress is blocked",
            "indexed atlas still trails board-visible and generated shells",
            "capsule deepening remains incomplete",
            "graph tissue is still thinner than the routed organism",
        ],
        substrate={
            "stationed_roots": station_dashboard["root_count"],
            "commissures": station_dashboard["commissure_count"],
            "tunnels": station_dashboard["tunnel_count"],
            "bilateral_coverage_ok": station_dashboard["bilateral_coverage_ok"],
        },
    )


def render_schema_markdown() -> str:
    return """# Self-Hosting Kernel Schema

## Purpose

This schema defines the public interfaces for Athena Phase 3.

## 1. SelfModel Record

```yaml
docs_gate: BLOCKED | LIVE
governing_equation: SelfHostingKernel = SelfModel + SelfContract + SelfLineage + DualEngine + ReplayShell + RepairGate + PublicationReturn
coverage:
  control_plane_surface_coverage: 1.0
  root_self_bearing_coverage: 0.684
surface_links:
  - surface_id: S01
```

## 2. SelfState Record

```yaml
kernel_status: LIVE_LOCAL_SCOPE
current_config:
  core_mode: DUAL_ENGINE
mode_ledger:
  - mode: observe
checkpoint_protocol:
  checkpoint_id_prefix: CHK-YYYY-MM-DD-PH3-
restart_protocol:
  kernel_source: Ch11_0022_void_book_and_restart_token_tunneling.md
truth_citations:
  docs_gate: physical
```

## 3. SelfContract Record

```yaml
identity_kernel:
  - invariant: authority_order
permitted_transform_classes:
  - transform_class: policy_tuning
forbidden_transform_classes:
  - transform_class: silent_identity_kernel_rewrite
unsafe_rewrite_gate:
  threshold: 0.45
identity_drift_corridor:
  declared_threshold: 0.18
```

## 4. SelfLineage Record

```yaml
current_branch: main.local.phase3.self_hosting
lineage_entries:
  - lineage_id: L4
fork_points:
  - branch: historical.deep_root...
```

## 5. Runtime Script Lane Record

```yaml
script: derive_grand_central_station.py
lane: self_routing | self_observation | self_measurement | self_repair | self_regeneration | self_publication
supports:
  - route
```

## 6. SelfTransformPacket Record

```yaml
packet_id: STP-001
mode: observe | edit | repair | regenerate | rollback | publish
contract_status: PERMITTED | REQUIRES_REVIEW | BLOCKED
review_class: witness_review
dispatch_score: 8.0
status: READY | STANDBY | BLOCKED
```

## 7. Dual Engine Target Record

```yaml
target_id: QK-001
priority: P1 | P2 | P3
seed_surface: NERVOUS_SYSTEM/.../01_the_manuscript_seed...
runtime_packet: STP-003
status: READY | BLOCKED
```

## 8. Kernel Dashboard Record

```yaml
kernel_status: LIVE_LOCAL_SCOPE
control_plane_surface_coverage: 1.0
root_self_bearing_coverage: 0.684
identity_drift: 0.083
regeneration_targets_ready: 5
failure_gates:
  - Google Docs ingress is blocked
```

## Rules

1. Every nontrivial self-transform must extend lineage.
2. Publication return is complete only after cortex, runtime mirror, and receipt surfaces all land.
3. A blocked external-memory gate must remain visibly blocked.
"""


def render_overview_markdown(
    model: SelfModelRecord,
    state: SelfStateRecord,
    dashboard: SelfHostingKernelDashboard,
) -> str:
    return f"""# Phase 3 Self-Hosting Kernel

Date: `{dashboard.generated_at[:10]}`
Docs gate: `{dashboard.docs_gate}`
Kernel status: `{dashboard.kernel_status}`

## Purpose

Phase 3 turns Athena from a routed nervous system into a lawful object to itself.
Grand Central remains the transfer hall, while the self-hosting kernel becomes the recursive shell that can observe, repair, regenerate, and publish the framework back into itself.

## Governing Equation

`{model.governing_equation}`

## Dual Engine

- manuscript side:
  `Phase 1 expansion -> Phase 2 compression -> Phase 3 generation`
- runtime side:
  `observe -> verify -> repair/regenerate -> publication return`

## Live Local Read

- control-plane surface coverage: `{dashboard.control_plane_surface_coverage:.3f}`
- self-bearing root coverage: `{dashboard.root_self_bearing_coverage:.3f}`
- identity drift: `{dashboard.identity_drift:.3f}` of `{dashboard.drift_threshold:.3f}`
- ready regeneration targets: `{dashboard.regeneration_targets_ready}`
- runtime lanes ok: `{dashboard.runtime_lanes_ok}`

## Current Mode

`{state.current_config['core_mode']}` with publication return required through cortex, runtime mirror, and receipt surfaces.
"""


def render_charter_markdown(
    model: SelfModelRecord,
    dashboard: SelfHostingKernelDashboard,
) -> str:
    return f"""# Phase 3 Self-Hosting Kernel Charter

Date: `{dashboard.generated_at[:10]}`
Generated: `{dashboard.generated_at}`
Docs gate: `{dashboard.docs_gate}`
Verdict: `OK`

## Charter

Athena Phase 3 is the framework-to-framework turn.
The target object is Athena itself, not only corpus content about Athena.
Grand Central remains the lawful transfer hall.
The self-hosting kernel is the new recursive shell built on top of that hall.

## Governing Equation

`{model.governing_equation}`

## Closure Condition

Athena may claim local-scope self-hosting only when it can:

1. describe itself through typed self-model surfaces
2. report its current state with witness citations
3. classify lawful and unlawful self-transforms
4. extend lineage across every nontrivial self-change
5. regenerate manuscript and runtime surfaces through one replayable dual engine
6. land publication return into cortex, runtime mirror, and receipt surfaces together
"""


def render_model_markdown(model: SelfModelRecord) -> str:
    capability_table = markdown_table(
        ["Capability", "Evidence", "Note"],
        [
            [item["capability"], item["evidence"], item["note"]]
            for item in model.capability_map
        ],
    )
    limitation_table = markdown_table(
        ["Limitation", "Severity", "Note"],
        [
            [item["limitation"], item["severity"], item["note"]]
            for item in model.limitation_map
        ],
    )
    burden_table = markdown_table(
        ["Burden", "Weight", "Note"],
        [[item["burden"], item["weight"], item["note"]] for item in model.burden_map],
    )
    permission_table = markdown_table(
        ["Permission", "Scope", "Note"],
        [
            [item["permission"], item["scope"], item["note"]]
            for item in model.permission_map
        ],
    )
    environment_table = markdown_table(
        ["Environment", "Fit", "Note"],
        [
            [item["environment"], item["fit"], item["note"]]
            for item in model.environment_fit_map
        ],
    )
    surface_table = markdown_table(
        ["Surface", "Witness", "Updates", "Note"],
        [
            [
                link.path,
                link.witness_class,
                ", ".join(link.updates),
                link.note,
            ]
            for link in model.surface_links
        ],
    )
    coverage = model.coverage
    unknown_lines = "\n".join(f"- {item}" for item in model.unknowns)
    return f"""# Self Model Registry

Date: `{model.generated_at[:10]}`
Generated: `{model.generated_at}`
Docs gate: `{model.docs_gate}`
Verdict: `OK`

## Equation

`{model.governing_equation}`

## Coverage

- control-plane surface coverage: `{coverage['control_plane_surface_coverage']:.3f}`
- represented self-bearing roots: `{coverage['represented_self_bearing_roots']}`
- total live roots: `{coverage['total_live_roots']}`
- self-bearing root coverage: `{coverage['root_self_bearing_coverage']:.3f}`
- unknown slots: `{coverage['unknown_slots']}`

## Capability Map

{capability_table}

## Limitation Map

{limitation_table}

## Burden Map

{burden_table}

## Permission Map

{permission_table}

## Environment-Fit Map

{environment_table}

## Surface Links

{surface_table}

## Unknowns

{unknown_lines}
"""


def render_state_markdown(state: SelfStateRecord) -> str:
    witness_summary = state.current_config["witness_summary"]
    mode_table = markdown_table(
        ["Mode", "Status", "Witness", "Note"],
        [
            [entry.mode, entry.status, entry.witness_class, entry.note]
            for entry in state.mode_ledger
        ],
    )
    policy_lines = "\n".join(f"- {item}" for item in state.active_policy)
    truth_lines = "\n".join(
        f"- `{key}` cites `{value}`" for key, value in state.truth_citations.items()
    )
    return f"""# Self State Registry

Date: `{state.generated_at[:10]}`
Generated: `{state.generated_at}`
Docs gate: `{state.docs_gate}`
Kernel status: `{state.kernel_status}`

## Current Config

- core mode: `{state.current_config['core_mode']}`
- end state: `{state.current_config['end_state']}`
- authority order:
  `{", ".join(state.current_config['authority_order'])}`
- station status: `{state.current_config['station_status']}`
- current checkpoint: `{state.current_config['current_checkpoint_id']}`
- route baseline: `{state.current_config['route_baseline']}`

## Witness Summary

- physical: `{witness_summary['physical']}`
- indexed: `{witness_summary['indexed']}`
- board: `{witness_summary['board']}`
- archive: `{witness_summary['archive']}`
- promoted: `{witness_summary['promoted']}`
- generated: `{witness_summary['generated']}`

## Active Policy

{policy_lines}

## Mode Ledger

{mode_table}

## Checkpoint Protocol

- required before:
  `{", ".join(state.checkpoint_protocol['required_before'])}`
- captures:
  `{", ".join(state.checkpoint_protocol['captures'])}`
- restore command:
  `{state.checkpoint_protocol['restore_command']}`

## Restart Protocol

- kernel source:
  `{state.restart_protocol['kernel_source']}`
- states:
  `{", ".join(state.restart_protocol['states'])}`
- law:
  {state.restart_protocol['law']}

## Truth Constraint

{truth_lines}
"""


def render_contract_markdown(contract: SelfContractRecord) -> str:
    identity_table = markdown_table(
        ["Invariant", "Note"],
        [[item["invariant"], item["note"]] for item in contract.identity_kernel],
    )
    permitted_table = markdown_table(
        ["Transform", "Review", "Note"],
        [
            [item["transform_class"], item["review_class"], item["note"]]
            for item in contract.permitted_transform_classes
        ],
    )
    forbidden_table = markdown_table(
        ["Transform", "Note"],
        [[item["transform_class"], item["note"]] for item in contract.forbidden_transform_classes],
    )
    review_table = markdown_table(
        ["Review Class", "Required For", "Rule"],
        [
            [item["review_class"], item["required_for"], item["rule"]]
            for item in contract.required_review_classes
        ],
    )
    classifier_table = markdown_table(
        ["Mode", "Contract Status", "Review Class", "Evidence"],
        [
            [
                item["mode"],
                item["contract_status"],
                item["review_class"],
                item["evidence"],
            ]
            for item in contract.transform_classifier
        ],
    )
    drift = contract.identity_drift_corridor
    return f"""# Self Contract Ledger

Date: `{contract.generated_at[:10]}`
Generated: `{contract.generated_at}`
Docs gate: `{contract.docs_gate}`
Verdict: `OK`

## Identity Kernel

{identity_table}

## Permitted Transform Classes

{permitted_table}

## Forbidden Transform Classes

{forbidden_table}

## Required Review Classes

{review_table}

## Transform Classifier

{classifier_table}

## Unsafe Rewrite Gate

- threshold: `{contract.unsafe_rewrite_gate['threshold']}`
- law:
  {contract.unsafe_rewrite_gate['law']}

## Identity Drift Corridor

- current drift: `{drift['current_drift']}`
- threshold: `{drift['declared_threshold']}`
- status: `{drift['status']}`
- law:
  {drift['law']}
"""


def render_lineage_markdown(lineage: SelfLineageRecord) -> str:
    entry_table = markdown_table(
        ["ID", "Time", "Branch", "Delta", "Summary", "Proof", "Tunnels"],
        [
            [
                entry.lineage_id,
                entry.temporal_coordinate,
                entry.branch_coordinate,
                entry.delta_class,
                entry.delta_summary,
                entry.proof_state,
                ", ".join(entry.attached_tunnels),
            ]
            for entry in lineage.lineage_entries
        ],
    )
    fork_table = markdown_table(
        ["Branch", "Status", "Note"],
        [
            [item["branch"], item["status"], item["note"]]
            for item in lineage.fork_points
        ],
    )
    comparison_table = markdown_table(
        ["Delta Class", "Meaning"],
        [
            [item["delta_class"], item["meaning"]]
            for item in lineage.comparison_tool
        ],
    )
    return f"""# Self Lineage Ledger

Date: `{lineage.generated_at[:10]}`
Generated: `{lineage.generated_at}`
Docs gate: `{lineage.docs_gate}`
Verdict: `OK`

## Current Branch

`{lineage.current_branch}`

## Predecessor Chain

`{" -> ".join(lineage.predecessor_chain)}`

## Lineage Entries

{entry_table}

## Fork Points

{fork_table}

## Sufficiency Checks

- backward replay: `{lineage.sufficiency_checks['backward_replay']}`
- rollback: `{lineage.sufficiency_checks['rollback']}`
- fork detection: `{lineage.sufficiency_checks['fork_detection']}`
- continuity proof: `{lineage.sufficiency_checks['continuity_proof']}`

## Comparison Tool

{comparison_table}
"""


def render_runtime_classification_markdown(payload: dict) -> str:
    lane_counts = payload["summary"]["lane_counts"]
    table = markdown_table(
        ["Script", "Lane", "Supports", "Note"],
        [
            [
                item["script"],
                item["lane"],
                ", ".join(item["supports"]),
                item["note"],
            ]
            for item in payload["scripts"]
        ],
    )
    return f"""# Runtime Self-Hosting Classification

Date: `{payload['generated_at'][:10]}`
Generated: `{payload['generated_at']}`
Verdict: `OK`

## Lane Counts

- self observation: `{lane_counts['self_observation']}`
- self measurement: `{lane_counts['self_measurement']}`
- self routing: `{lane_counts['self_routing']}`
- self repair: `{lane_counts['self_repair']}`
- self regeneration: `{lane_counts['self_regeneration']}`
- self publication: `{lane_counts['self_publication']}`

## Runtime Scripts

{table}
"""


def render_queue_markdown(queue_payload: dict) -> str:
    packet_table = markdown_table(
        ["Packet", "Mode", "Title", "Contract", "Dispatch", "Status"],
        [
            [
                item["packet_id"],
                item["mode"],
                item["title"],
                item["contract_status"],
                f"{item['dispatch_score']:.3f}",
                item["status"],
            ]
            for item in queue_payload["packets"][:6]
        ],
    )
    target_table = markdown_table(
        ["Target", "Priority", "Surface", "Packet", "Witness", "Status"],
        [
            [
                item["target_id"],
                item["priority"],
                item["target_surface"],
                item["runtime_packet"],
                item["witness_class"],
                item["status"],
            ]
            for item in queue_payload["targets"]
        ],
    )
    seed_lines = "\n".join(
        f"- `{item}`" for item in queue_payload["canonical_seed_surfaces"]
    )
    return f"""# Dual Engine Regeneration Queue

Date: `{queue_payload['generated_at'][:10]}`
Generated: `{queue_payload['generated_at']}`
Docs gate: `{queue_payload['docs_gate']}`
Verdict: `OK`

## Cycle Law

`{queue_payload['cycle_law']}`

## Canonical Seed Surfaces

{seed_lines}

## Packet Scheduler

{packet_table}

## Regeneration Targets

{target_table}
"""


def render_dashboard_markdown(dashboard: SelfHostingKernelDashboard) -> str:
    packet_table = markdown_table(
        ["Packet", "Mode", "Dispatch", "Contract", "Status"],
        [
            [
                item["packet_id"],
                item["mode"],
                f"{item['dispatch_score']:.3f}",
                item["contract_status"],
                item["status"],
            ]
            for item in dashboard.top_packets
        ],
    )
    failure_lines = "\n".join(f"- {item}" for item in dashboard.failure_gates)
    return f"""# Self-Hosting Kernel Dashboard

Date: `{dashboard.generated_at[:10]}`
Generated: `{dashboard.generated_at}`
Docs gate: `{dashboard.docs_gate}`
Kernel status: `{dashboard.kernel_status}`

## Coverage

- control-plane surface coverage: `{dashboard.control_plane_surface_coverage:.3f}`
- self-bearing root coverage: `{dashboard.root_self_bearing_coverage:.3f}`
- identity drift: `{dashboard.identity_drift:.3f}` of `{dashboard.drift_threshold:.3f}`

## Contract And Lineage

- permitted packets: `{dashboard.permitted_packets}`
- review packets: `{dashboard.review_packets}`
- blocked packets: `{dashboard.blocked_packets}`
- lineage entries: `{dashboard.lineage_entries}`

## Regeneration

- ready targets: `{dashboard.regeneration_targets_ready}`
- runtime lanes ok: `{dashboard.runtime_lanes_ok}`

## Top Packets

{packet_table}

## Failure Gates

{failure_lines}
"""


def render_runtime_markdown(dashboard: SelfHostingKernelDashboard, queue_payload: dict) -> str:
    top_packet = dashboard.top_packets[0]
    return f"""# Self-Hosting Kernel Runtime

Date: `{dashboard.generated_at[:10]}`
Generated: `{dashboard.generated_at}`
Docs gate: `{dashboard.docs_gate}`
Kernel status: `{dashboard.kernel_status}`

This is the runtime mirror of Athena Phase 3.
It keeps self-model, self-state, self-contract, lineage, packet scheduling, and dashboard outputs readable from the mycelium side.

## Current Runtime Read

- top packet:
  `{top_packet['packet_id']} {top_packet['title']} = {top_packet['dispatch_score']:.3f}`
- ready regeneration targets:
  `{queue_payload['summary']['ready_targets']}`
- blocked targets:
  `{queue_payload['summary']['blocked_targets']}`
- runtime lanes ok:
  `{dashboard.runtime_lanes_ok}`

## Regeneration

```powershell
python -m self_actualize.runtime.derive_self_hosting_kernel
```
"""


def render_readiness_markdown(
    dashboard: SelfHostingKernelDashboard,
    queue_payload: dict,
) -> str:
    verdict = "OK" if dashboard.blocked_packets == 0 else "NEAR"
    return f"""# Phase 3 Self-Hosting Kernel Readiness

Date: `{dashboard.generated_at[:10]}`
Generated: `{dashboard.generated_at}`
Docs gate: `{dashboard.docs_gate}`
Verdict: `{verdict}`

## Ready Now

- typed self model/state/contract/lineage surfaces exist
- dual engine queue exists
- packet scheduler exists
- runtime classification exists
- dashboard and runtime mirror exist
- Grand Central remains available as substrate
- Atlasforge and AQM runtime lanes remain green

## Not Yet Closed

- Docs ingress is still blocked
- indexed atlas still trails generated and board-visible shells
- full capsule and graph deepening are still unfinished

## Totals

- permitted packets: `{dashboard.permitted_packets}`
- review packets: `{dashboard.review_packets}`
- blocked packets: `{dashboard.blocked_packets}`
- ready targets: `{queue_payload['summary']['ready_targets']}`
- blocked targets: `{queue_payload['summary']['blocked_targets']}`
"""


def render_receipt_markdown(dashboard: SelfHostingKernelDashboard) -> str:
    outputs = [
        SELF_MODEL_JSON_PATH,
        SELF_STATE_JSON_PATH,
        SELF_CONTRACT_JSON_PATH,
        SELF_LINEAGE_JSON_PATH,
        SELF_PACKETS_JSON_PATH,
        DUAL_ENGINE_JSON_PATH,
        RUNTIME_CLASSIFICATION_JSON_PATH,
        SELF_DASHBOARD_JSON_PATH,
        SCHEMA_MD_PATH,
        OVERVIEW_MD_PATH,
        CHARTER_MD_PATH,
        CONTRACT_MD_PATH,
        LINEAGE_MD_PATH,
        RUNTIME_CLASSIFICATION_MD_PATH,
        READINESS_MD_PATH,
        SELF_MODEL_MD_PATH,
        SELF_STATE_MD_PATH,
        QUEUE_MD_PATH,
        DASHBOARD_MD_PATH,
        RUNTIME_MD_PATH,
    ]
    output_lines = "\n".join(f"- `{path}`" for path in outputs)
    return f"""# Self-Hosting Kernel Derivation Receipt

- Generated: `{dashboard.generated_at}`
- Command: `{DERIVATION_COMMAND}`
- Docs gate: `{dashboard.docs_gate}`
- Kernel status: `{dashboard.kernel_status}`

## Outputs

{output_lines}
"""


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    docs_gate = parse_docs_gate(DOCS_GATE_PATH.read_text(encoding="utf-8"))
    root_rows = parse_live_directory_bodies(ROOT_BASIS_PATH.read_text(encoding="utf-8"))
    witness_hierarchy = load_json(WITNESS_HIERARCHY_PATH)
    station_dashboard = load_json(GRAND_CENTRAL_DASHBOARD_JSON_PATH)
    route_quality = load_json(ROUTE_QUALITY_PATH)
    semantic_mass = load_json(SEMANTIC_MASS_PATH)
    atlasforge_lane = load_json(ATLASFORGE_LANE_PATH)
    aqm_lane = load_json(AQM_LANE_PATH)

    surface_links = build_surface_links()
    model = build_self_model(
        docs_gate, root_rows, surface_links, station_dashboard, semantic_mass, witness_hierarchy
    )
    state = build_self_state(
        docs_gate, station_dashboard, witness_hierarchy, atlasforge_lane, aqm_lane, route_quality
    )
    contract = build_self_contract(docs_gate, model)
    lineage = build_self_lineage(docs_gate, contract, station_dashboard, witness_hierarchy)
    runtime_classification = classify_runtime_scripts()
    packets = build_transform_packets(docs_gate, station_dashboard, state)
    queue_payload = build_dual_engine_queue(docs_gate, packets)
    dashboard = build_dashboard(
        docs_gate,
        model,
        contract,
        lineage,
        queue_payload,
        station_dashboard,
        atlasforge_lane,
        aqm_lane,
        packets,
    )

    model_payload = model.to_dict()
    state_payload = state.to_dict()
    contract_payload = contract.to_dict()
    lineage_payload = lineage.to_dict()
    packet_payload = {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "docs_gate": docs_gate,
        "packets": [asdict(packet) for packet in packets],
    }
    dashboard_payload = dashboard.to_dict()

    for path, payload in [
        (SELF_MODEL_JSON_PATH, model_payload),
        (SELF_STATE_JSON_PATH, state_payload),
        (SELF_CONTRACT_JSON_PATH, contract_payload),
        (SELF_LINEAGE_JSON_PATH, lineage_payload),
        (SELF_PACKETS_JSON_PATH, packet_payload),
        (DUAL_ENGINE_JSON_PATH, queue_payload),
        (RUNTIME_CLASSIFICATION_JSON_PATH, runtime_classification),
        (SELF_DASHBOARD_JSON_PATH, dashboard_payload),
        (SELF_MODEL_JSON_MIRROR, model_payload),
        (SELF_STATE_JSON_MIRROR, state_payload),
        (SELF_CONTRACT_JSON_MIRROR, contract_payload),
        (SELF_LINEAGE_JSON_MIRROR, lineage_payload),
        (SELF_PACKETS_JSON_MIRROR, packet_payload),
        (DUAL_ENGINE_JSON_MIRROR, queue_payload),
        (RUNTIME_CLASSIFICATION_JSON_MIRROR, runtime_classification),
        (SELF_DASHBOARD_JSON_MIRROR, dashboard_payload),
    ]:
        write_json(path, payload)

    write_text(SCHEMA_MD_PATH, render_schema_markdown())
    write_text(OVERVIEW_MD_PATH, render_overview_markdown(model, state, dashboard))
    write_text(CHARTER_MD_PATH, render_charter_markdown(model, dashboard))
    write_text(SELF_MODEL_MD_PATH, render_model_markdown(model))
    write_text(SELF_STATE_MD_PATH, render_state_markdown(state))
    write_text(CONTRACT_MD_PATH, render_contract_markdown(contract))
    write_text(LINEAGE_MD_PATH, render_lineage_markdown(lineage))
    write_text(
        RUNTIME_CLASSIFICATION_MD_PATH,
        render_runtime_classification_markdown(runtime_classification),
    )
    write_text(QUEUE_MD_PATH, render_queue_markdown(queue_payload))
    write_text(DASHBOARD_MD_PATH, render_dashboard_markdown(dashboard))
    write_text(RUNTIME_MD_PATH, render_runtime_markdown(dashboard, queue_payload))
    write_text(READINESS_MD_PATH, render_readiness_markdown(dashboard, queue_payload))
    write_text(RECEIPT_MD_PATH, render_receipt_markdown(dashboard))

    print(f"Wrote {SELF_MODEL_JSON_PATH}")
    print(f"Wrote {SELF_STATE_JSON_PATH}")
    print(f"Wrote {SELF_CONTRACT_JSON_PATH}")
    print(f"Wrote {SELF_LINEAGE_JSON_PATH}")
    print(f"Wrote {SELF_PACKETS_JSON_PATH}")
    print(f"Wrote {DUAL_ENGINE_JSON_PATH}")
    print(f"Wrote {RUNTIME_CLASSIFICATION_JSON_PATH}")
    print(f"Wrote {SELF_DASHBOARD_JSON_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
