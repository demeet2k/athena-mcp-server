from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from self_actualize.runtime.crystal_remaster_contracts import (
    BridgeEdgeWitnessRecord,
    CapsuleSliceContractRecord,
    DocsIngressPacketRecord,
    WaveCheckpointRecord,
)
from self_actualize.runtime.derive_crystal_remaster import (
    load_json,
    read_text,
    refresh_corpus_atlas,
    relative_string,
    utc_now,
    write_json,
    write_text,
)


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
NERVOUS_SYSTEM_ROOT = WORKSPACE_ROOT / "NERVOUS_SYSTEM"
MYCELIUM_BRAIN_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain"
REGISTRY_ROOT = MYCELIUM_BRAIN_ROOT / "registry"
CAPSULE_ROOT = NERVOUS_SYSTEM_ROOT / "50_CORPUS_CAPSULES"
ROUTE_ROOT = MYCELIUM_BRAIN_ROOT / "nervous_system" / "routes" / "whole_crystal"
LIVE_DOCS_MIRROR_ROOT = WORKSPACE_ROOT / "Trading Bot" / "LIVE_DOCS_MIRROR"

DERIVATION_VERSION = "2026-03-12.whole-crystal-v1"
DERIVATION_COMMAND = "python -m self_actualize.runtime.derive_whole_crystal_completion"

CRYSTAL_BODY_REGISTRY_PATH = SELF_ACTUALIZE_ROOT / "crystal_body_registry.json"
CRYSTAL_FAMILY_CONTRACTS_PATH = SELF_ACTUALIZE_ROOT / "crystal_family_contracts.json"
CRYSTAL_DIRECT_SYNAPSES_PATH = SELF_ACTUALIZE_ROOT / "crystal_direct_synapse_edges.json"
CRYSTAL_REMASTER_VERIFICATION_PATH = SELF_ACTUALIZE_ROOT / "crystal_remaster_verification.json"
PHASE4_WEAVE_CANDIDATES_PATH = SELF_ACTUALIZE_ROOT / "phase4_weave_candidates.json"
KNOWLEDGE_FABRIC_EDGES_PATH = SELF_ACTUALIZE_ROOT / "knowledge_fabric_edges.json"
TRADING_BOT_TRUTH_CORRIDOR_PATH = SELF_ACTUALIZE_ROOT / "trading_bot_truth_corridor.json"
LIVE_DOCS_GATE_PATH = SELF_ACTUALIZE_ROOT / "live_docs_gate_status.md"
AQM_RUNTIME_LANE_PATH = SELF_ACTUALIZE_ROOT / "aqm_runtime_lane.json"
ATLASFORGE_RUNTIME_LANE_PATH = SELF_ACTUALIZE_ROOT / "atlasforge_runtime_lane.json"
RUNTIME_WAIST_PATH = SELF_ACTUALIZE_ROOT / "runtime_waist_verification.json"
CORPUS_ATLAS_PATH = SELF_ACTUALIZE_ROOT / "corpus_atlas.json"

CAPSULE_SLICES_JSON_PATH = SELF_ACTUALIZE_ROOT / "whole_crystal_capsule_slices.json"
BRIDGE_WITNESSES_JSON_PATH = SELF_ACTUALIZE_ROOT / "whole_crystal_bridge_witnesses.json"
DOCS_INGRESS_JSON_PATH = SELF_ACTUALIZE_ROOT / "whole_crystal_docs_ingress.json"
WAVE_CHECKPOINTS_JSON_PATH = SELF_ACTUALIZE_ROOT / "whole_crystal_wave_checkpoints.json"
AGENT_CONTRACT_JSON_PATH = SELF_ACTUALIZE_ROOT / "whole_crystal_agent_contract.json"
DASHBOARD_JSON_PATH = SELF_ACTUALIZE_ROOT / "whole_crystal_completion_dashboard.json"
VERIFICATION_JSON_PATH = SELF_ACTUALIZE_ROOT / "whole_crystal_completion_verification.json"

CAPSULE_SLICES_JSON_MIRROR = REGISTRY_ROOT / "whole_crystal_capsule_slices.json"
BRIDGE_WITNESSES_JSON_MIRROR = REGISTRY_ROOT / "whole_crystal_bridge_witnesses.json"
DOCS_INGRESS_JSON_MIRROR = REGISTRY_ROOT / "whole_crystal_docs_ingress.json"
WAVE_CHECKPOINTS_JSON_MIRROR = REGISTRY_ROOT / "whole_crystal_wave_checkpoints.json"
AGENT_CONTRACT_JSON_MIRROR = REGISTRY_ROOT / "whole_crystal_agent_contract.json"
DASHBOARD_JSON_MIRROR = REGISTRY_ROOT / "whole_crystal_completion_dashboard.json"
VERIFICATION_JSON_MIRROR = REGISTRY_ROOT / "whole_crystal_completion_verification.json"

MANIFEST_MD_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "WHOLE_CRYSTAL_COMPLETION_MANIFEST.md"
AGENT_COORDINATION_MD_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "WHOLE_CRYSTAL_AGENT_COORDINATION.md"
DOCS_GATE_VERIFIER_MD_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "DOCS_GATE_VERIFIER.md"
DASHBOARD_MD_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "WHOLE_CRYSTAL_COMPLETION_DASHBOARD.md"
VERIFICATION_MD_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "WHOLE_CRYSTAL_COMPLETION_VERIFICATION.md"
BRIDGE_LEDGER_MD_PATH = NERVOUS_SYSTEM_ROOT / "85_EDGES" / "WHOLE_CRYSTAL_BRIDGE_LEDGER.md"
RUNTIME_MD_PATH = MYCELIUM_BRAIN_ROOT / "nervous_system" / "29_whole_crystal_completion_runtime.md"
RECEIPT_MD_PATH = MYCELIUM_BRAIN_ROOT / "receipts" / "2026-03-12_whole_crystal_completion.md"
LIVE_DOCS_MIRROR_README_PATH = LIVE_DOCS_MIRROR_ROOT / "README.md"

BODY_SLUGS: Dict[str, str] = {
    "A01": "nervous_system",
    "A02": "self_actualize",
    "A03": "ecosystem",
    "A05": "math",
    "A06": "voynich",
    "A07": "trading_bot",
    "A08": "quadrant_binary",
    "A09": "qshrink_athena_internal_use",
    "A10": "nerual_network",
    "A11": "fresh",
    "A12": "athenachka_collective_books",
    "A13": "i_am_athena",
    "A14": "games",
    "A15": "orgin",
    "A16": "athena_fleet",
}

CAPSULE_DIR_MAP: Dict[str, str] = {
    "A01": "nervous_system",
    "A02": "runtime_hub",
    "A03": "ecosystem",
    "A05": "math",
    "A06": "voynich",
    "A07": "trading_bot",
    "A08": "root_files",
    "A09": "qshrink",
    "A10": "neural_network",
    "A11": "fresh",
    "A12": "published_books",
    "A13": "identity",
    "A14": "games",
    "A15": "orgin",
    "A16": "athena_fleet",
}

DEFAULT_ANCHORS: Dict[str, Dict[str, List[str]]] = {
    "A01": {"chapters": ["Ch01", "Ch07", "Ch21"], "appendices": ["AppA", "AppC", "AppQ"]},
    "A02": {"chapters": ["Ch07", "Ch11", "Ch20"], "appendices": ["AppC", "AppN", "AppQ"]},
    "A03": {"chapters": ["Ch07", "Ch18", "Ch21"], "appendices": ["AppO", "AppP", "AppQ"]},
    "A05": {"chapters": ["Ch01", "Ch07", "Ch13"], "appendices": ["AppB", "AppC", "AppE"]},
    "A06": {"chapters": ["Ch03", "Ch06", "Ch11"], "appendices": ["AppF", "AppI", "AppL"]},
    "A07": {"chapters": ["Ch06", "Ch11", "Ch20"], "appendices": ["AppI", "AppN", "AppQ"]},
    "A08": {"chapters": ["Ch01", "Ch07", "Ch11"], "appendices": ["AppA", "AppB", "AppF"]},
    "A09": {"chapters": ["Ch04", "Ch07", "Ch13"], "appendices": ["AppB", "AppC", "AppN"]},
    "A10": {"chapters": ["Ch07", "Ch14", "Ch20"], "appendices": ["AppC", "AppH", "AppQ"]},
    "A11": {"chapters": ["Ch03", "Ch07", "Ch11"], "appendices": ["AppB", "AppC", "AppN"]},
    "A12": {"chapters": ["Ch14", "Ch18", "Ch21"], "appendices": ["AppO", "AppP", "AppQ"]},
    "A13": {"chapters": ["Ch11", "Ch14", "Ch19"], "appendices": ["AppA", "AppM", "AppQ"]},
    "A14": {"chapters": ["Ch09", "Ch14", "Ch18"], "appendices": ["AppO", "AppP", "AppQ"]},
    "A15": {"chapters": ["Ch01", "Ch11", "Ch19"], "appendices": ["AppA", "AppN", "AppQ"]},
    "A16": {"chapters": ["Ch07", "Ch14", "Ch20"], "appendices": ["AppP", "AppQ", "AppN"]},
}

SLICE_PHASES: List[Tuple[str, str, str]] = [
    ("seed", "Seed witness", "Admit source matter into a named capsule slice."),
    ("route", "Route contraction", "Bind the family to a canonical route and bridge surface."),
    ("restart", "Restart writeback", "Close the loop through return surfaces and the next seed."),
]


def markdown_table(headers: List[str], rows: List[List[str]]) -> str:
    head = "| " + " | ".join(headers) + " |"
    sep = "| " + " | ".join("---" for _ in headers) + " |"
    body = ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join([head, sep, *body])


def path_exists(relative_path: str) -> bool:
    return (WORKSPACE_ROOT / relative_path.replace("\\", "/")).exists()


def unique(values: Iterable[str]) -> List[str]:
    ordered: List[str] = []
    for value in values:
        if value and value not in ordered:
            ordered.append(value)
    return ordered


def file_index(path: Path) -> int:
    stem = path.stem
    prefix = stem.split("_", 1)[0]
    return int(prefix) if prefix.isdigit() else 9999


def live_docs_gate_detail() -> Dict[str, Any]:
    credentials_path = WORKSPACE_ROOT / "Trading Bot" / "credentials.json"
    token_path = WORKSPACE_ROOT / "Trading Bot" / "token.json"
    command_status = "UNKNOWN"
    return_code = None
    if LIVE_DOCS_GATE_PATH.exists():
        for line in read_text(LIVE_DOCS_GATE_PATH).splitlines():
            stripped = line.strip()
            if stripped.startswith("- Command status:"):
                command_status = stripped.split("`")[1]
            if stripped.startswith("- Return code:"):
                try:
                    return_code = int(stripped.split("`")[1])
                except (IndexError, ValueError):
                    return_code = None
    credentials_present = credentials_path.exists()
    token_present = token_path.exists()
    if not credentials_present:
        status = "blocked-by-missing-credentials"
    elif not token_present:
        status = "blocked-by-missing-token"
    elif command_status in {"OPEN", "OK", "AUTHED"} or return_code == 0:
        status = "open"
    else:
        status = "blocked-by-auth-failure"
    return {
        "status": status,
        "resolution": "open" if status == "open" else "lawfully-isolated",
        "credentials_present": credentials_present,
        "token_present": token_present,
        "command_status": command_status,
        "return_code": return_code,
        "mirror_path": relative_string(LIVE_DOCS_MIRROR_ROOT),
        "fallback_mode": "mirrored-live-docs" if status == "open" else "local-first-truth-corridor",
    }


def load_runtime_truth(path: Path, key: str = "truth") -> str:
    if not path.exists():
        return "UNKNOWN"
    return load_json(path).get(key, "UNKNOWN")


def anchors_for(contract: Dict[str, Any], body_id: str, count: int = 3) -> Tuple[List[str], List[str]]:
    defaults = DEFAULT_ANCHORS.get(body_id, {"chapters": ["Ch11"], "appendices": ["AppQ"]})
    chapters = unique(list(contract.get("chapter_anchors", [])) + defaults["chapters"])
    appendices = unique(list(contract.get("appendix_anchors", [])) + defaults["appendices"])
    while len(chapters) < count:
        chapters = unique(chapters + defaults["chapters"])
    while len(appendices) < count:
        appendices = unique(appendices + defaults["appendices"])
    return chapters[:count], appendices[:count]


def candidate_capsule_directory(body: Dict[str, Any], body_id: str) -> Path:
    current_capsule = body.get("capsule_surface") or ""
    if current_capsule:
        current_path = WORKSPACE_ROOT / current_capsule.replace("\\", "/")
        if current_path.exists():
            return current_path.parent
    return CAPSULE_ROOT / CAPSULE_DIR_MAP[body_id]


def existing_capsule_docs(directory: Path) -> List[Path]:
    if not directory.exists():
        return []
    docs = [
        path
        for path in directory.glob("*.md")
        if path.is_file() and path.name[:2].isdigit()
    ]
    return sorted(docs, key=file_index)


def placeholder_verification() -> Dict[str, Any]:
    return {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "truth": "NEAR",
        "checks": {},
        "unresolved": ["whole-crystal atlas refresh pending"],
    }


def render_slice_doc(
    body: Dict[str, Any],
    contract: Dict[str, Any],
    route_surface: str,
    chapter_anchor: str,
    appendix_anchor: str,
    phase_label: str,
    phase_purpose: str,
) -> str:
    witnesses = "\n".join(f"- `{item}`" for item in contract.get("witness_basis", [])[:6])
    return f"""# {body['root']} Whole Crystal {phase_label}

Date: `2026-03-12`
Body: `{body['body_id']}`
State: `{body['body_state']}`
Role: `{body['crystal_role']}`

## Purpose

{phase_purpose}

## Family surface

`{contract['family_surface']}`

## Route surface

`{route_surface}`

## Witness basis

{witnesses}

## Suggested chapter anchors

- `{chapter_anchor}`

## Suggested appendix anchors

- `{appendix_anchor}`

## Restart seed

{contract['restart_seed']}

## Writeback target

`{body['return_surface']}`
"""


def render_route_map(
    body: Dict[str, Any],
    contract: Dict[str, Any],
    route_surface: str,
    slice_paths: List[str],
    docs_gate: Dict[str, Any],
) -> str:
    intake = "\n".join(f"- `{item}`" for item in contract.get("witness_basis", [])[:6])
    slices = "\n".join(f"- `{item}`" for item in slice_paths)
    direct_targets = ", ".join(body.get("direct_synapse_targets", [])) or "none"
    docs_clause = (
        f"Docs gate currently resolves as `{docs_gate['status']}` with fallback `{docs_gate['fallback_mode']}`."
        if body["body_id"] == "A07"
        else "Route remains local-first and atlas-indexed before any dashboard claims freshness."
    )
    return f"""# ROUTE {body['root']}

## Intake

{intake}

## Canonical slices

{slices}

## Main transfer

`{body['root']} -> {contract['family_surface']} -> {route_surface} -> {body['return_surface']}`

## Direct bridge targets

`{direct_targets}`

## Law

- authority remains `{body['authority']}`
- lineage remains `{body['lineage_class']}`
- writeback target remains `{body['return_surface']}`
- {docs_clause}

## Restart seed

{contract['restart_seed']}
"""


def build_slice_contracts(
    live_bodies: List[Dict[str, Any]],
    contracts_by_id: Dict[str, Dict[str, Any]],
    docs_gate: Dict[str, Any],
) -> Tuple[List[CapsuleSliceContractRecord], List[Path], List[Path]]:
    slice_contracts: List[CapsuleSliceContractRecord] = []
    generated_paths: List[Path] = []
    route_paths: List[Path] = []
    for body in live_bodies:
        body_id = body["body_id"]
        contract = contracts_by_id[body_id]
        slug = BODY_SLUGS[body_id]
        route_path = ROUTE_ROOT / f"ROUTE_{slug}.md"
        route_surface = relative_string(route_path)
        directory = candidate_capsule_directory(body, body_id)
        directory.mkdir(parents=True, exist_ok=True)
        existing_docs = existing_capsule_docs(directory)
        chapters, appendices = anchors_for(contract, body_id, count=3)

        while len(existing_docs) < 3:
            index = len(existing_docs) + 1
            phase_key, phase_label, phase_purpose = SLICE_PHASES[len(existing_docs)]
            slug_name = slug if directory.name != "root_files" else f"{slug}_{phase_key}"
            path = directory / f"{index:02d}_{slug_name}.md"
            write_text(
                path,
                render_slice_doc(
                    body=body,
                    contract=contract,
                    route_surface=route_surface,
                    chapter_anchor=chapters[len(existing_docs)],
                    appendix_anchor=appendices[len(existing_docs)],
                    phase_label=phase_label,
                    phase_purpose=phase_purpose,
                ),
            )
            existing_docs.append(path)
            generated_paths.append(path)

        selected_docs = existing_docs[:3]
        selected_relative = [relative_string(path) for path in selected_docs]
        write_text(
            route_path,
            render_route_map(
                body=body,
                contract=contract,
                route_surface=route_surface,
                slice_paths=selected_relative,
                docs_gate=docs_gate,
            ),
        )
        route_paths.append(route_path)
        generated_paths.append(route_path)

        truth_state = docs_gate["status"] if body_id == "A07" else "local-witnessed"
        for index, slice_path in enumerate(selected_docs, start=1):
            slice_contracts.append(
                CapsuleSliceContractRecord(
                    slice_id=f"CSL-{body_id}-{index:02d}",
                    body_id=body_id,
                    root=body["root"],
                    family_surface=contract["family_surface"],
                    capsule_surface=relative_string(slice_path),
                    route_surface=route_surface,
                    chapter_anchor=chapters[index - 1],
                    appendix_anchor=appendices[index - 1],
                    restart_seed=contract["restart_seed"],
                    truth_state=truth_state,
                    writeback_target=body["return_surface"],
                    witness_basis=unique(
                        [
                            contract["family_surface"],
                            route_surface,
                            relative_string(slice_path),
                            body["return_surface"],
                        ]
                    ),
                    note=f"{SLICE_PHASES[index - 1][1]} for {body['root']}.",
                )
            )
    return slice_contracts, generated_paths, route_paths


def build_bridge_witnesses(
    bodies_by_id: Dict[str, Dict[str, Any]],
    direct_synapses: List[Dict[str, Any]],
    phase4_payload: Dict[str, Any],
) -> List[BridgeEdgeWitnessRecord]:
    records: List[BridgeEdgeWitnessRecord] = []
    direct_pairs = {
        (item["source_body_id"], item["target_body_id"])
        for item in direct_synapses
    }
    for item in direct_synapses:
        records.append(
            BridgeEdgeWitnessRecord(
                edge_id=item["edge_id"],
                source_body_id=item["source_body_id"],
                source_root=item["source_root"],
                target_body_id=item["target_body_id"],
                target_root=item["target_root"],
                edge_class="direct",
                authority_rank="authoritative",
                runtime_surface=relative_string(KNOWLEDGE_FABRIC_EDGES_PATH),
                replay_surface=relative_string(CRYSTAL_DIRECT_SYNAPSES_PATH),
                witness_basis=unique(
                    item.get("witness_basis", [])
                    + [relative_string(PHASE4_WEAVE_CANDIDATES_PATH), relative_string(KNOWLEDGE_FABRIC_EDGES_PATH)]
                ),
                route=item.get("route", []),
                note=item.get("note", ""),
            )
        )

    candidates = phase4_payload.get("candidates", [])
    live_candidates = [
        row
        for row in candidates
        if row.get("status") == "READY"
        and row.get("src") in bodies_by_id
        and row.get("dst") in bodies_by_id
        and (row.get("src"), row.get("dst")) not in direct_pairs
        and bodies_by_id.get(row.get("src"), {}).get("body_state") == "live"
        and bodies_by_id.get(row.get("dst"), {}).get("body_state") == "live"
    ]
    for row in live_candidates[:4]:
        records.append(
            BridgeEdgeWitnessRecord(
                edge_id=f"INF-{row['weave_id']}",
                source_body_id=row["src"],
                source_root=bodies_by_id[row["src"]]["root"],
                target_body_id=row["dst"],
                target_root=bodies_by_id[row["dst"]]["root"],
                edge_class="inferred-ready",
                authority_rank="ranked-near",
                runtime_surface=relative_string(PHASE4_WEAVE_CANDIDATES_PATH),
                replay_surface=relative_string(BRIDGE_LEDGER_MD_PATH),
                witness_basis=[relative_string(PHASE4_WEAVE_CANDIDATES_PATH)],
                route=row.get("promotion_route", []),
                note=row.get("note", ""),
            )
        )

    quarantined_candidates = [
        row
        for row in candidates
        if row.get("status") == "READY"
        and row.get("src") in bodies_by_id
        and row.get("dst") in bodies_by_id
        and (
            bodies_by_id.get(row.get("src"), {}).get("body_state") != "live"
            or bodies_by_id.get(row.get("dst"), {}).get("body_state") != "live"
        )
    ]
    for row in quarantined_candidates[:4]:
        records.append(
            BridgeEdgeWitnessRecord(
                edge_id=f"QRT-{row['weave_id']}",
                source_body_id=row["src"],
                source_root=bodies_by_id[row["src"]]["root"],
                target_body_id=row["dst"],
                target_root=bodies_by_id[row["dst"]]["root"],
                edge_class="quarantined",
                authority_rank="quarantined",
                runtime_surface=relative_string(PHASE4_WEAVE_CANDIDATES_PATH),
                replay_surface=relative_string(BRIDGE_LEDGER_MD_PATH),
                witness_basis=[relative_string(PHASE4_WEAVE_CANDIDATES_PATH)],
                route=row.get("promotion_route", []),
                note=row.get("note", ""),
            )
        )
    return records


def build_docs_ingress_payload(docs_gate: Dict[str, Any]) -> Tuple[DocsIngressPacketRecord, Dict[str, Any]]:
    packet = DocsIngressPacketRecord(
        packet_id="DIG-01",
        status=docs_gate["status"],
        credentials_present=docs_gate["credentials_present"],
        token_present=docs_gate["token_present"],
        source_doc_id="google-docs-corpus-search",
        mirror_path=docs_gate["mirror_path"],
        ingest_time=utc_now(),
        fallback_mode=docs_gate["fallback_mode"],
        gate_surface=relative_string(LIVE_DOCS_GATE_PATH),
        witness_basis=[
            relative_string(LIVE_DOCS_GATE_PATH),
            relative_string(TRADING_BOT_TRUTH_CORRIDOR_PATH),
        ],
        note="Whole-crystal Docs ingress packet.",
    )
    payload = {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "resolution": docs_gate["resolution"],
        "status": docs_gate["status"],
        "fallback_mode": docs_gate["fallback_mode"],
        "mirror_path": docs_gate["mirror_path"],
        "gate_surface": relative_string(LIVE_DOCS_GATE_PATH),
        "packets": [packet.to_dict()],
        "open_state_flow": [
            "docs search",
            "LIVE_DOCS_MIRROR markdown writeback",
            "corpus atlas refresh",
            "witness citation",
            "governed route into runtime",
        ],
        "blocked_state_flow": [
            "gate verifier",
            "local-first truth corridor",
            "atlas-indexed local witnesses only",
            "no live-doc authority claims",
        ],
    }
    return packet, payload


def build_agent_contract() -> Dict[str, Any]:
    return {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "packet_lifecycle": [
            "trigger",
            "witness_basis",
            "route",
            "expected_writeback",
            "completion_proof",
        ],
        "agents": [
            {
                "agent_id": "AG-01",
                "label": "overseer",
                "body_id": "A02",
                "responsibility": "ranking, gate law, quarantine, atlas freshness, restart",
            },
            {
                "agent_id": "AG-02",
                "label": "corridor-builder",
                "body_id": "A16",
                "responsibility": "route invention, bridge publication, inter-body coordination",
            },
            {
                "agent_id": "AG-03",
                "label": "proof-compiler",
                "body_id": "A06",
                "responsibility": "ambiguity preservation, machine grounding, hard-domain verification",
            },
        ],
    }


def build_dashboard(
    bodies: List[Dict[str, Any]],
    slice_contracts: List[CapsuleSliceContractRecord],
    bridge_records: List[BridgeEdgeWitnessRecord],
    docs_packet: DocsIngressPacketRecord,
    verification: Dict[str, Any],
) -> Dict[str, Any]:
    state_totals: Dict[str, int] = {}
    for body in bodies:
        state_totals[body["body_state"]] = state_totals.get(body["body_state"], 0) + 1
    live_body_ids = [body["body_id"] for body in bodies if body["body_state"] == "live"]
    slice_counts = {
        body_id: len([record for record in slice_contracts if record.body_id == body_id])
        for body_id in live_body_ids
    }
    bridge_totals: Dict[str, int] = {}
    for record in bridge_records:
        bridge_totals[record.edge_class] = bridge_totals.get(record.edge_class, 0) + 1
    return {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "body_state_totals": state_totals,
        "live_family_count": len(live_body_ids),
        "live_family_slice_coverage": {
            "total_slices": len(slice_contracts),
            "families_at_target": sum(1 for count in slice_counts.values() if 3 <= count <= 5),
            "slice_counts": slice_counts,
        },
        "bridge_totals": bridge_totals,
        "docs_gate": {
            "status": docs_packet.status,
            "resolution": "open" if docs_packet.status == "open" else "lawfully-isolated",
            "fallback_mode": docs_packet.fallback_mode,
        },
        "verifier_truth": {
            "aqm": verification["runtime_lanes"]["aqm_runtime_lane"],
            "atlasforge": verification["runtime_lanes"]["atlasforge_runtime_lane"],
            "runtime_waist": verification["runtime_lanes"]["runtime_waist"],
        },
        "truth": verification["truth"],
        "next_restart_seed": verification["next_restart_seed"],
    }


def build_wave_checkpoints(
    verification: Dict[str, Any],
    docs_packet: DocsIngressPacketRecord,
) -> List[WaveCheckpointRecord]:
    atlas_refreshed = verification["checks"]["atlas_refresh_complete"]
    runtime_green = verification["checks"]["runtime_verifiers_green"]
    docs_settled = verification["checks"]["docs_gate_lawful"]
    return [
        WaveCheckpointRecord(
            checkpoint_id="WC-01",
            phase="baseline-lock",
            required_derivations=["derive_crystal_remaster"],
            required_verifiers=["crystal_remaster_verification"],
            atlas_refreshed=True,
            truth="OK" if verification["checks"]["remaster_baseline_green"] else "FAIL",
            note="Freeze crystal-remaster-v2 as the start witness.",
        ),
        WaveCheckpointRecord(
            checkpoint_id="WC-02",
            phase="family-contraction",
            required_derivations=["derive_whole_crystal_completion"],
            required_verifiers=["slice_contract_coverage"],
            atlas_refreshed=atlas_refreshed,
            truth="OK" if verification["checks"]["live_family_slice_target"] else "FAIL",
            note="Every live family holds 3 capsule slices with chapter and appendix anchors.",
        ),
        WaveCheckpointRecord(
            checkpoint_id="WC-03",
            phase="bridge-publication",
            required_derivations=["derive_phase4_structured_neuron_storage", "derive_knowledge_fabric"],
            required_verifiers=["direct_bridge_presence"],
            atlas_refreshed=atlas_refreshed,
            truth="OK" if verification["checks"]["bridge_layer_complete"] else "FAIL",
            note="Direct, inferred, and quarantined bridges are all published.",
        ),
        WaveCheckpointRecord(
            checkpoint_id="WC-04",
            phase="docs-gate-law",
            required_derivations=["derive_trading_bot_truth_corridor", "derive_whole_crystal_completion"],
            required_verifiers=["docs_gate_verifier"],
            atlas_refreshed=atlas_refreshed,
            truth="OK" if docs_settled else "FAIL",
            note=f"Docs gate is `{docs_packet.status}` and resolves as lawful `{verification['docs_gate_resolution']}`.",
        ),
        WaveCheckpointRecord(
            checkpoint_id="WC-05",
            phase="wave-close",
            required_derivations=["derive_phase4_pt2_inter_metro_lens_weight_superstructure"],
            required_verifiers=["verify_aqm_runtime_lane", "verify_atlasforge_runtime_lane", "verify_runtime_waist"],
            atlas_refreshed=atlas_refreshed,
            truth="OK" if (runtime_green and atlas_refreshed and docs_settled) else "FAIL",
            note="Wave closes only when verifiers are green and Docs is open or lawfully isolated.",
        ),
    ]


def build_verification(
    remaster_verification: Dict[str, Any],
    bodies: List[Dict[str, Any]],
    slice_contracts: List[CapsuleSliceContractRecord],
    bridge_records: List[BridgeEdgeWitnessRecord],
    docs_packet: DocsIngressPacketRecord,
    phase4_payload: Dict[str, Any],
    knowledge_fabric_payload: Dict[str, Any],
    generated_paths: List[Path],
) -> Dict[str, Any]:
    live_body_ids = [body["body_id"] for body in bodies if body["body_state"] == "live"]
    slice_counts = {
        body_id: len([record for record in slice_contracts if record.body_id == body_id])
        for body_id in live_body_ids
    }
    direct_bridge_count = len([record for record in bridge_records if record.edge_class == "direct"])
    inferred_bridge_count = len([record for record in bridge_records if record.edge_class == "inferred-ready"])
    quarantined_bridge_count = len([record for record in bridge_records if record.edge_class == "quarantined"])

    phase4_pairs = {
        (row.get("src"), row.get("dst"))
        for row in phase4_payload.get("candidates", [])
        if row.get("status") == "READY"
    }
    knowledge_direct = [
        edge
        for edge in knowledge_fabric_payload.get("edges", [])
        if edge.get("edge_kind") in {"DIRECT_SYNAPSE", "DIRECT_SYNAPSE_RETURN"}
    ]
    atlas_payload = load_json(CORPUS_ATLAS_PATH)
    atlas_paths = {record.get("relative_path") for record in atlas_payload.get("records", [])}
    generated_relative = [relative_string(path) for path in generated_paths]
    atlas_missing = [path for path in generated_relative if path not in atlas_paths]

    aqm_truth = load_runtime_truth(AQM_RUNTIME_LANE_PATH)
    atlasforge_truth = load_runtime_truth(ATLASFORGE_RUNTIME_LANE_PATH)
    runtime_waist_truth = load_runtime_truth(RUNTIME_WAIST_PATH)

    checks = {
        "remaster_baseline_green": all(remaster_verification.get("validations", {}).values()),
        "body_authority_surface_complete": all(body.get("authority") and body.get("family_surface") and body.get("return_surface") for body in bodies),
        "live_family_slice_target": all(3 <= slice_counts.get(body_id, 0) <= 5 for body_id in live_body_ids),
        "slice_anchor_coverage": all(record.chapter_anchor and record.appendix_anchor for record in slice_contracts),
        "route_surfaces_resolve": all(path_exists(record.route_surface) for record in slice_contracts),
        "bridge_layer_complete": direct_bridge_count == 3 and inferred_bridge_count >= 1 and quarantined_bridge_count >= 1,
        "phase4_direct_pairs_present": all(pair in phase4_pairs for pair in [("A16", "A06"), ("A06", "A09"), ("A16", "A15")]),
        "knowledge_fabric_direct_pairs_present": len(knowledge_direct) >= 6,
        "docs_gate_lawful": docs_packet.status in {
            "blocked-by-missing-credentials",
            "blocked-by-missing-token",
            "blocked-by-auth-failure",
            "open",
        },
        "blocked_state_dashboard_present": DOCS_GATE_VERIFIER_MD_PATH.exists(),
        "atlas_refresh_complete": not atlas_missing,
        "runtime_verifiers_green": aqm_truth == "OK" and atlasforge_truth == "OK" and runtime_waist_truth == "OK",
    }
    docs_gate_resolution = "open" if docs_packet.status == "open" else "lawfully-isolated"
    truth = "OK" if all(checks.values()) and docs_gate_resolution in {"open", "lawfully-isolated"} else "FAIL"
    unresolved: List[str] = []
    if docs_packet.status != "open":
        unresolved.append(f"Google Docs ingress remains `{docs_packet.status}` and is currently routed through local-first isolation.")
    if atlas_missing:
        unresolved.append("One or more whole-crystal surfaces are still missing from corpus_atlas.json.")
    if aqm_truth != "OK" or atlasforge_truth != "OK" or runtime_waist_truth != "OK":
        unresolved.append("One or more runtime verifiers are not green.")

    return {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "truth": truth,
        "docs_gate_resolution": docs_gate_resolution,
        "checks": checks,
        "bridge_counts": {
            "direct": direct_bridge_count,
            "inferred-ready": inferred_bridge_count,
            "quarantined": quarantined_bridge_count,
        },
        "runtime_lanes": {
            "aqm_runtime_lane": aqm_truth,
            "atlasforge_runtime_lane": atlasforge_truth,
            "runtime_waist": runtime_waist_truth,
        },
        "atlas_refresh_pending_paths": atlas_missing,
        "unresolved": unresolved,
        "next_restart_seed": "admit -> classify -> interlock -> compile -> writeback -> restart",
    }


def render_manifest(outputs: Dict[str, str]) -> str:
    output_lines = "\n".join(f"- `{label}`: `{path}`" for label, path in outputs.items())
    return f"""# WHOLE CRYSTAL COMPLETION MANIFEST

Date: `2026-03-12`
Baseline: `crystal-remaster-v2`
Derivation: `{DERIVATION_COMMAND}`

## Law

- keep the triad authoritative
- keep direct bridges witnessed
- keep Docs ingress open or lawfully isolated
- keep atlas refresh ahead of dashboard freshness

## Outputs

{output_lines}
"""


def render_agent_coordination(agent_contract: Dict[str, Any]) -> str:
    rows = [
        [agent["agent_id"], agent["label"], agent["body_id"], agent["responsibility"]]
        for agent in agent_contract["agents"]
    ]
    lifecycle = "\n".join(f"- `{item}`" for item in agent_contract["packet_lifecycle"])
    return f"""# WHOLE CRYSTAL AGENT COORDINATION

## Roles

{markdown_table(["Agent", "Label", "Body", "Responsibility"], rows)}

## SynapticHandoffPacket lifecycle

{lifecycle}
"""


def render_docs_gate_verifier(docs_payload: Dict[str, Any]) -> str:
    packet = docs_payload["packets"][0]
    blocked_flow = "\n".join(f"- `{item}`" for item in docs_payload["blocked_state_flow"])
    open_flow = "\n".join(f"- `{item}`" for item in docs_payload["open_state_flow"])
    return f"""# DOCS GATE VERIFIER

Date: `2026-03-12`
Status: `{docs_payload['status']}`
Resolution: `{docs_payload['resolution']}`
Fallback mode: `{docs_payload['fallback_mode']}`

## Packet

- packet id: `{packet['packet_id']}`
- credentials present: `{packet['credentials_present']}`
- token present: `{packet['token_present']}`
- mirror path: `{packet['mirror_path']}`
- gate surface: `{packet['gate_surface']}`

## Blocked-state dashboard

{blocked_flow}

## Open-state ingest flow

{open_flow}
"""


def render_bridge_ledger(records: List[BridgeEdgeWitnessRecord]) -> str:
    sections: List[str] = []
    for edge_class, title in [
        ("direct", "Direct bridges"),
        ("inferred-ready", "Inferred bridges"),
        ("quarantined", "Quarantined bridges"),
    ]:
        rows = [
            [
                record.edge_id,
                record.source_root,
                record.target_root,
                record.authority_rank,
                " -> ".join(record.route) if record.route else "-",
            ]
            for record in records
            if record.edge_class == edge_class
        ]
        sections.append(
            f"## {title}\n\n"
            + markdown_table(["Edge", "Source", "Target", "Authority", "Route"], rows or [["-", "-", "-", "-", "-"]])
        )
    return "# WHOLE CRYSTAL BRIDGE LEDGER\n\n" + "\n\n".join(sections)


def render_dashboard(dashboard: Dict[str, Any]) -> str:
    body_rows = [[state, str(count)] for state, count in sorted(dashboard["body_state_totals"].items())]
    bridge_rows = [[name, str(count)] for name, count in sorted(dashboard["bridge_totals"].items())]
    verifier_rows = [[name, value] for name, value in dashboard["verifier_truth"].items()]
    return f"""# WHOLE CRYSTAL COMPLETION DASHBOARD

Date: `2026-03-12`
Truth: `{dashboard['truth']}`

## Body states

{markdown_table(["State", "Count"], body_rows)}

## Live family contraction

- live family count: `{dashboard['live_family_count']}`
- total slices: `{dashboard['live_family_slice_coverage']['total_slices']}`
- families at target: `{dashboard['live_family_slice_coverage']['families_at_target']}`

## Bridge totals

{markdown_table(["Bridge class", "Count"], bridge_rows)}

## Docs gate

- status: `{dashboard['docs_gate']['status']}`
- resolution: `{dashboard['docs_gate']['resolution']}`
- fallback mode: `{dashboard['docs_gate']['fallback_mode']}`

## Verifiers

{markdown_table(["Verifier", "Truth"], verifier_rows)}

## Restart seed

`{dashboard['next_restart_seed']}`
"""


def render_verification(verification: Dict[str, Any]) -> str:
    rows = [[name, str(value)] for name, value in verification["checks"].items()]
    unresolved = "\n".join(f"- {item}" for item in verification["unresolved"]) or "- none"
    return f"""# WHOLE CRYSTAL COMPLETION VERIFICATION

Date: `2026-03-12`
Truth: `{verification['truth']}`
Docs gate resolution: `{verification['docs_gate_resolution']}`

## Checks

{markdown_table(["Check", "Result"], rows)}

## Runtime lanes

- `AQM`: `{verification['runtime_lanes']['aqm_runtime_lane']}`
- `ATLAS FORGE`: `{verification['runtime_lanes']['atlasforge_runtime_lane']}`
- `runtime waist`: `{verification['runtime_lanes']['runtime_waist']}`

## Unresolved

{unresolved}
"""


def render_runtime(outputs: Dict[str, str], verification: Dict[str, Any]) -> str:
    output_lines = "\n".join(f"- `{label}`: `{path}`" for label, path in outputs.items())
    return f"""# whole_crystal_completion_runtime

- generated_at: `{verification['generated_at']}`
- truth: `{verification['truth']}`
- docs_gate_resolution: `{verification['docs_gate_resolution']}`
- derivation_command: `{DERIVATION_COMMAND}`

## Outputs

{output_lines}
"""


def render_receipt(
    dashboard: Dict[str, Any],
    verification: Dict[str, Any],
    bridge_records: List[BridgeEdgeWitnessRecord],
) -> str:
    bridge_lines = "\n".join(
        f"- `{record.edge_id}` `{record.source_root} -> {record.target_root}` `{record.edge_class}`"
        for record in bridge_records
    )
    unresolved = "\n".join(f"- {item}" for item in verification["unresolved"]) or "- none"
    return f"""# 2026-03-12 whole crystal completion

- generated_at: `{verification['generated_at']}`
- truth: `{verification['truth']}`
- docs_gate_resolution: `{verification['docs_gate_resolution']}`
- derivation_command: `{DERIVATION_COMMAND}`

## Slice coverage

- live families: `{dashboard['live_family_count']}`
- total slices: `{dashboard['live_family_slice_coverage']['total_slices']}`
- families at target: `{dashboard['live_family_slice_coverage']['families_at_target']}`

## Bridges

{bridge_lines}

## Honest limits

{unresolved}
"""


def render_live_docs_mirror_readme(docs_payload: Dict[str, Any]) -> str:
    return f"""# LIVE DOCS MIRROR

Status: `{docs_payload['status']}`
Resolution: `{docs_payload['resolution']}`

This directory is the lawful mirror target for future Google Docs markdown surfaces.

- If the gate is blocked, no live-doc authority claims are allowed here.
- If the gate opens, mirrored markdown must be atlas-indexed and cited by a witness surface
  before it can influence dashboards or runtime claims.
"""


def write_placeholder_surfaces(outputs: Dict[str, str]) -> None:
    write_json(DASHBOARD_JSON_PATH, {"generated_at": utc_now(), "truth": "NEAR", "outputs": outputs})
    write_json(VERIFICATION_JSON_PATH, placeholder_verification())
    write_json(DASHBOARD_JSON_MIRROR, {"generated_at": utc_now(), "truth": "NEAR", "outputs": outputs})
    write_json(VERIFICATION_JSON_MIRROR, placeholder_verification())
    write_text(DASHBOARD_MD_PATH, "# WHOLE CRYSTAL COMPLETION DASHBOARD\n\nPending atlas refresh.\n")
    write_text(VERIFICATION_MD_PATH, "# WHOLE CRYSTAL COMPLETION VERIFICATION\n\nPending atlas refresh.\n")
    write_text(RUNTIME_MD_PATH, "# whole_crystal_completion_runtime\n\nPending atlas refresh.\n")
    write_text(RECEIPT_MD_PATH, "# 2026-03-12 whole crystal completion\n\nPending atlas refresh.\n")


def main() -> int:
    body_payload = load_json(CRYSTAL_BODY_REGISTRY_PATH)
    family_payload = load_json(CRYSTAL_FAMILY_CONTRACTS_PATH)
    direct_synapse_payload = load_json(CRYSTAL_DIRECT_SYNAPSES_PATH)
    remaster_verification = load_json(CRYSTAL_REMASTER_VERIFICATION_PATH)
    phase4_payload = load_json(PHASE4_WEAVE_CANDIDATES_PATH)
    knowledge_fabric_payload = load_json(KNOWLEDGE_FABRIC_EDGES_PATH)

    bodies = body_payload.get("bodies", [])
    contracts = family_payload.get("contracts", [])
    bodies_by_id = {body["body_id"]: body for body in bodies}
    contracts_by_id = {contract["body_id"]: contract for contract in contracts}
    live_bodies = [body for body in bodies if body["body_state"] == "live"]

    docs_gate = live_docs_gate_detail()
    docs_packet, docs_payload = build_docs_ingress_payload(docs_gate)
    agent_contract = build_agent_contract()
    slice_contracts, generated_slice_paths, route_paths = build_slice_contracts(live_bodies, contracts_by_id, docs_gate)
    bridge_records = build_bridge_witnesses(bodies_by_id, direct_synapse_payload.get("edges", []), phase4_payload)

    slice_payload = {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "contracts": [record.to_dict() for record in slice_contracts],
    }
    bridge_payload = {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "edges": [record.to_dict() for record in bridge_records],
    }

    outputs = {
        "capsule_slices_json": relative_string(CAPSULE_SLICES_JSON_PATH),
        "bridge_witnesses_json": relative_string(BRIDGE_WITNESSES_JSON_PATH),
        "docs_ingress_json": relative_string(DOCS_INGRESS_JSON_PATH),
        "wave_checkpoints_json": relative_string(WAVE_CHECKPOINTS_JSON_PATH),
        "agent_contract_json": relative_string(AGENT_CONTRACT_JSON_PATH),
        "dashboard_json": relative_string(DASHBOARD_JSON_PATH),
        "verification_json": relative_string(VERIFICATION_JSON_PATH),
        "manifest_md": relative_string(MANIFEST_MD_PATH),
        "agent_coordination_md": relative_string(AGENT_COORDINATION_MD_PATH),
        "docs_gate_verifier_md": relative_string(DOCS_GATE_VERIFIER_MD_PATH),
        "bridge_ledger_md": relative_string(BRIDGE_LEDGER_MD_PATH),
        "dashboard_md": relative_string(DASHBOARD_MD_PATH),
        "verification_md": relative_string(VERIFICATION_MD_PATH),
        "runtime_md": relative_string(RUNTIME_MD_PATH),
        "receipt_md": relative_string(RECEIPT_MD_PATH),
    }

    write_json(CAPSULE_SLICES_JSON_PATH, slice_payload)
    write_json(BRIDGE_WITNESSES_JSON_PATH, bridge_payload)
    write_json(DOCS_INGRESS_JSON_PATH, docs_payload)
    write_json(AGENT_CONTRACT_JSON_PATH, agent_contract)
    write_json(CAPSULE_SLICES_JSON_MIRROR, slice_payload)
    write_json(BRIDGE_WITNESSES_JSON_MIRROR, bridge_payload)
    write_json(DOCS_INGRESS_JSON_MIRROR, docs_payload)
    write_json(AGENT_CONTRACT_JSON_MIRROR, agent_contract)

    write_text(MANIFEST_MD_PATH, render_manifest(outputs))
    write_text(AGENT_COORDINATION_MD_PATH, render_agent_coordination(agent_contract))
    write_text(DOCS_GATE_VERIFIER_MD_PATH, render_docs_gate_verifier(docs_payload))
    write_text(BRIDGE_LEDGER_MD_PATH, render_bridge_ledger(bridge_records))
    write_text(LIVE_DOCS_MIRROR_README_PATH, render_live_docs_mirror_readme(docs_payload))
    write_placeholder_surfaces(outputs)

    generated_paths = [
        CAPSULE_SLICES_JSON_PATH,
        BRIDGE_WITNESSES_JSON_PATH,
        DOCS_INGRESS_JSON_PATH,
        AGENT_CONTRACT_JSON_PATH,
        CAPSULE_SLICES_JSON_MIRROR,
        BRIDGE_WITNESSES_JSON_MIRROR,
        DOCS_INGRESS_JSON_MIRROR,
        AGENT_CONTRACT_JSON_MIRROR,
        MANIFEST_MD_PATH,
        AGENT_COORDINATION_MD_PATH,
        DOCS_GATE_VERIFIER_MD_PATH,
        BRIDGE_LEDGER_MD_PATH,
        DASHBOARD_JSON_PATH,
        VERIFICATION_JSON_PATH,
        DASHBOARD_JSON_MIRROR,
        VERIFICATION_JSON_MIRROR,
        DASHBOARD_MD_PATH,
        VERIFICATION_MD_PATH,
        RUNTIME_MD_PATH,
        RECEIPT_MD_PATH,
        LIVE_DOCS_MIRROR_README_PATH,
        *generated_slice_paths,
        *route_paths,
    ]
    refresh_corpus_atlas(generated_paths)

    verification = build_verification(
        remaster_verification=remaster_verification,
        bodies=bodies,
        slice_contracts=slice_contracts,
        bridge_records=bridge_records,
        docs_packet=docs_packet,
        phase4_payload=phase4_payload,
        knowledge_fabric_payload=knowledge_fabric_payload,
        generated_paths=generated_paths,
    )
    dashboard = build_dashboard(
        bodies=bodies,
        slice_contracts=slice_contracts,
        bridge_records=bridge_records,
        docs_packet=docs_packet,
        verification=verification,
    )
    checkpoints = build_wave_checkpoints(verification, docs_packet)
    checkpoint_payload = {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "checkpoints": [record.to_dict() for record in checkpoints],
    }

    write_json(WAVE_CHECKPOINTS_JSON_PATH, checkpoint_payload)
    write_json(WAVE_CHECKPOINTS_JSON_MIRROR, checkpoint_payload)
    write_json(DASHBOARD_JSON_PATH, dashboard)
    write_json(DASHBOARD_JSON_MIRROR, dashboard)
    write_json(VERIFICATION_JSON_PATH, verification)
    write_json(VERIFICATION_JSON_MIRROR, verification)
    write_text(DASHBOARD_MD_PATH, render_dashboard(dashboard))
    write_text(VERIFICATION_MD_PATH, render_verification(verification))
    write_text(RUNTIME_MD_PATH, render_runtime(outputs, verification))
    write_text(RECEIPT_MD_PATH, render_receipt(dashboard, verification, bridge_records))

    refresh_corpus_atlas(
        [
            WAVE_CHECKPOINTS_JSON_PATH,
            WAVE_CHECKPOINTS_JSON_MIRROR,
            DASHBOARD_JSON_PATH,
            DASHBOARD_JSON_MIRROR,
            VERIFICATION_JSON_PATH,
            VERIFICATION_JSON_MIRROR,
            DASHBOARD_MD_PATH,
            VERIFICATION_MD_PATH,
            RUNTIME_MD_PATH,
            RECEIPT_MD_PATH,
        ]
    )

    print(f"Wrote whole crystal completion artifacts under {SELF_ACTUALIZE_ROOT}")
    print(f"Docs gate status: {docs_packet.status}")
    print(f"Truth: {verification['truth']}")
    return 0 if verification["truth"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
