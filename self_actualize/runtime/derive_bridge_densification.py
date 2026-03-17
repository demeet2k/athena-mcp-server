from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from self_actualize.runtime.crystal_remaster_contracts import (
    BridgeBacklogEntryRecord,
    BridgeSliceContractRecord,
    DirectBridgeFamilyContractRecord,
    SynapticHandoffPacketRecord,
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

DERIVATION_VERSION = "2026-03-13.bridge-densification-v1"
DERIVATION_COMMAND = "python -m self_actualize.runtime.derive_bridge_densification"

CRYSTAL_FAMILY_CONTRACTS_PATH = SELF_ACTUALIZE_ROOT / "crystal_family_contracts.json"
WHOLE_CRYSTAL_SLICES_PATH = SELF_ACTUALIZE_ROOT / "whole_crystal_capsule_slices.json"
WHOLE_CRYSTAL_BRIDGES_PATH = SELF_ACTUALIZE_ROOT / "whole_crystal_bridge_witnesses.json"
WHOLE_CRYSTAL_DOCS_INGRESS_PATH = SELF_ACTUALIZE_ROOT / "whole_crystal_docs_ingress.json"
PHASE4_WEAVE_CANDIDATES_PATH = SELF_ACTUALIZE_ROOT / "phase4_weave_candidates.json"
KNOWLEDGE_FABRIC_EDGES_PATH = SELF_ACTUALIZE_ROOT / "knowledge_fabric_edges.json"
PHASE4_PT2_EDGES_PATH = SELF_ACTUALIZE_ROOT / "phase4_pt2_system_crosswalk_edges.json"
CORPUS_ATLAS_PATH = SELF_ACTUALIZE_ROOT / "corpus_atlas.json"
AQM_RUNTIME_LANE_PATH = SELF_ACTUALIZE_ROOT / "aqm_runtime_lane.json"
ATLASFORGE_RUNTIME_LANE_PATH = SELF_ACTUALIZE_ROOT / "atlasforge_runtime_lane.json"
RUNTIME_WAIST_PATH = SELF_ACTUALIZE_ROOT / "runtime_waist_verification.json"
LIVE_DOCS_GATE_PATH = SELF_ACTUALIZE_ROOT / "live_docs_gate_status.md"

BRIDGE_FAMILIES_JSON_PATH = SELF_ACTUALIZE_ROOT / "bridge_densification_direct_bridge_families.json"
BRIDGE_SLICES_JSON_PATH = SELF_ACTUALIZE_ROOT / "bridge_densification_bridge_slices.json"
BRIDGE_PACKETS_JSON_PATH = SELF_ACTUALIZE_ROOT / "bridge_densification_synaptic_packets.json"
BRIDGE_BACKLOG_JSON_PATH = SELF_ACTUALIZE_ROOT / "bridge_densification_backlog.json"
DASHBOARD_JSON_PATH = SELF_ACTUALIZE_ROOT / "bridge_densification_dashboard.json"
VERIFICATION_JSON_PATH = SELF_ACTUALIZE_ROOT / "bridge_densification_verification.json"

BRIDGE_FAMILIES_JSON_MIRROR = REGISTRY_ROOT / BRIDGE_FAMILIES_JSON_PATH.name
BRIDGE_SLICES_JSON_MIRROR = REGISTRY_ROOT / BRIDGE_SLICES_JSON_PATH.name
BRIDGE_PACKETS_JSON_MIRROR = REGISTRY_ROOT / BRIDGE_PACKETS_JSON_PATH.name
BRIDGE_BACKLOG_JSON_MIRROR = REGISTRY_ROOT / BRIDGE_BACKLOG_JSON_PATH.name
DASHBOARD_JSON_MIRROR = REGISTRY_ROOT / DASHBOARD_JSON_PATH.name
VERIFICATION_JSON_MIRROR = REGISTRY_ROOT / VERIFICATION_JSON_PATH.name

MANIFEST_MD_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "BRIDGE_DENSIFICATION_MANIFEST.md"
DASHBOARD_MD_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "BRIDGE_DENSIFICATION_DASHBOARD.md"
VERIFICATION_MD_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "BRIDGE_DENSIFICATION_VERIFICATION.md"
WHOLE_CRYSTAL_LEDGER_MD_PATH = NERVOUS_SYSTEM_ROOT / "85_EDGES" / "WHOLE_CRYSTAL_BRIDGE_LEDGER.md"
RUNTIME_MD_PATH = MYCELIUM_BRAIN_ROOT / "nervous_system" / "30_bridge_densification_runtime.md"
RECEIPT_MD_PATH = MYCELIUM_BRAIN_ROOT / "receipts" / "2026-03-13_bridge_densification.md"

BRIDGE_CAPSULE_ROOT = NERVOUS_SYSTEM_ROOT / "50_CORPUS_CAPSULES" / "bridge_families"
BRIDGE_ROUTE_ROOT = MYCELIUM_BRAIN_ROOT / "nervous_system" / "routes" / "whole_crystal" / "bridge_families"
BRIDGE_EDGE_ROOT = NERVOUS_SYSTEM_ROOT / "85_EDGES" / "bridge_families"
BRIDGE_RECEIPT_ROOT = MYCELIUM_BRAIN_ROOT / "receipts" / "bridge_families"

RELEVANT_FAMILY_SURFACES = {
    "A16": WORKSPACE_ROOT / "self_actualize" / "mycelium_brain" / "nervous_system" / "families" / "FAMILY_athena_fleet.md",
    "A06": WORKSPACE_ROOT / "self_actualize" / "mycelium_brain" / "nervous_system" / "families" / "FAMILY_voynich.md",
    "A09": WORKSPACE_ROOT / "self_actualize" / "mycelium_brain" / "nervous_system" / "families" / "FAMILY_qshrink_athena_internal_use.md",
    "A15": WORKSPACE_ROOT / "self_actualize" / "mycelium_brain" / "nervous_system" / "families" / "FAMILY_orgin.md",
}

DIRECT_BRIDGE_SPECS: Dict[str, Dict[str, str]] = {
    "CS-001": {
        "bridge_family_id": "BF-CS-001",
        "source_agent": "corridor-builder",
        "receive_agent": "proof-compiler",
        "note": "Fleet proof corridor.",
    },
    "CS-002": {
        "bridge_family_id": "BF-CS-002",
        "source_agent": "proof-compiler",
        "receive_agent": "qshrink-shell",
        "note": "Proof compression corridor.",
    },
    "CS-003": {
        "bridge_family_id": "BF-CS-003",
        "source_agent": "corridor-builder",
        "receive_agent": "seed-reservoir",
        "note": "Fleet origin inheritance corridor.",
    },
}

DIRECT_EDGE_ORDER = ["CS-001", "CS-002", "CS-003"]
DEEP_PAIRWISE_BACKLOG_IDS = {f"WV-{index:04d}" for index in range(7, 13)}
DIRECT_EDGE_IDS = set(DIRECT_EDGE_ORDER)


def markdown_table(headers: List[str], rows: List[List[str]]) -> str:
    head = "| " + " | ".join(headers) + " |"
    sep = "| " + " | ".join("---" for _ in headers) + " |"
    body = ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join([head, sep, *body])


def unique(items: Iterable[str]) -> List[str]:
    ordered: List[str] = []
    for item in items:
        if item and item not in ordered:
            ordered.append(item)
    return ordered


def normalize_path(path: str) -> str:
    return path.replace("/", "\\")


def path_exists(relative_path: str) -> bool:
    return (WORKSPACE_ROOT / relative_path.replace("\\", "/")).exists()


def load_docs_gate() -> Dict[str, Any]:
    if WHOLE_CRYSTAL_DOCS_INGRESS_PATH.exists():
        payload = load_json(WHOLE_CRYSTAL_DOCS_INGRESS_PATH)
        packets = payload.get("packets", [])
        packet = packets[0] if packets else {}
        return {
            "status": payload.get("status", packet.get("status", "blocked-by-missing-credentials")),
            "resolution": payload.get("resolution", "lawfully-isolated"),
            "fallback_mode": payload.get("fallback_mode", packet.get("fallback_mode", "local-first-truth-corridor")),
        }
    status = "blocked-by-missing-credentials"
    if LIVE_DOCS_GATE_PATH.exists():
        markdown = read_text(LIVE_DOCS_GATE_PATH)
        if "Command status: `OPEN`" in markdown:
            status = "open"
        elif "token.json" in markdown:
            status = "blocked-by-missing-token"
    return {
        "status": status,
        "resolution": "open" if status == "open" else "lawfully-isolated",
        "fallback_mode": "mirrored-live-docs" if status == "open" else "local-first-truth-corridor",
    }


def load_runtime_truth(path: Path, key: str = "truth") -> str:
    if not path.exists():
        return "UNKNOWN"
    return load_json(path).get(key, "UNKNOWN")


def bridge_slug(bridge_family_id: str) -> str:
    return bridge_family_id.lower().replace("-", "_")


def anchor_ref(slice_record: Dict[str, Any], surface_key: str) -> str:
    surface = slice_record.get(surface_key, "")
    return (
        f"{slice_record['slice_id']}::"
        f"{slice_record.get('chapter_anchor', '')}/"
        f"{slice_record.get('appendix_anchor', '')}::"
        f"{surface}"
    )


def render_bridge_slice_doc(
    bridge_family: DirectBridgeFamilyContractRecord,
    slice_record: BridgeSliceContractRecord,
    packets_by_id: Dict[str, SynapticHandoffPacketRecord],
    route_points: List[str],
) -> str:
    packet = packets_by_id[slice_record.packet_id]
    witness_lines = "\n".join(f"- `{item}`" for item in slice_record.witness_basis)
    return f"""# {bridge_family.bridge_family_id} {slice_record.phase}

Date: `2026-03-13`
Truth: `{slice_record.truth_state}`
Edge: `{bridge_family.edge_id}`

## Anchors

- source anchor: `{slice_record.source_anchor_ref}`
- target anchor: `{slice_record.target_anchor_ref}`
- chapter anchor: `{slice_record.chapter_anchor}`
- appendix anchor: `{slice_record.appendix_anchor}`

## Packet

- packet id: `{packet.packet_id}`
- source agent: `{packet.source_agent}`
- target agent: `{packet.target_agent}`
- phase: `{packet.phase}`
- route: `{" -> ".join(route_points)}`

## Witness basis

{witness_lines}

## Writeback target

`{slice_record.writeback_target}`

## Note

{slice_record.note}
"""


def render_bridge_route(
    bridge_family: DirectBridgeFamilyContractRecord,
    slices: List[BridgeSliceContractRecord],
    packets: List[SynapticHandoffPacketRecord],
    route_points: List[str],
    target_route_surface: str,
) -> str:
    slice_lines = "\n".join(f"- `{slice_record.slice_id}` `{slice_record.capsule_surface}`" for slice_record in slices)
    packet_lines = "\n".join(f"- `{packet.packet_id}` `{packet.phase}` `{packet.source_agent} -> {packet.target_agent}`" for packet in packets)
    witness_lines = "\n".join(f"- `{item}`" for item in bridge_family.witness_basis)
    return f"""# ROUTE {bridge_family.bridge_family_id}

Date: `2026-03-13`
Truth: `OK`

## Bridge

- edge id: `{bridge_family.edge_id}`
- source family: `{bridge_family.source_family_surface}`
- target family: `{bridge_family.target_family_surface}`
- primary writeback target: `{target_route_surface}`

## Canonical bridge slices

{slice_lines}

## Packet lifecycle

- `emit`
- `transit`
- `receive`
- `replay`
- `writeback`
- `verify`

## Active packets

{packet_lines}

## Route

`{" -> ".join(route_points)}`

## Witness basis

{witness_lines}

## Restart seed

{bridge_family.restart_seed}
"""


def render_bridge_replay(
    bridge_family: DirectBridgeFamilyContractRecord,
    packets: List[SynapticHandoffPacketRecord],
    route_points: List[str],
    target_route_surface: str,
) -> str:
    packet_rows = [
        [packet.packet_id, packet.phase, packet.source_agent, packet.target_agent, " -> ".join(packet.route)]
        for packet in packets
    ]
    return f"""# REPLAY {bridge_family.bridge_family_id}

Date: `2026-03-13`
Truth: `OK`

## Replay Law

`emit -> transit -> receive -> replay -> writeback -> verify`

## Edge

- edge id: `{bridge_family.edge_id}`
- route: `{" -> ".join(route_points)}`
- primary writeback target: `{target_route_surface}`

## Packets

{markdown_table(["Packet", "Phase", "Source", "Target", "Route"], packet_rows)}
"""


def render_bridge_verify(
    bridge_family: DirectBridgeFamilyContractRecord,
    checks: Dict[str, bool],
) -> str:
    rows = [[name, str(value)] for name, value in checks.items()]
    return f"""# VERIFY {bridge_family.bridge_family_id}

Date: `2026-03-13`
Truth: `{"OK" if all(checks.values()) else "FAIL"}`

## Checks

{markdown_table(["Check", "Result"], rows)}
"""


def render_bridge_receipt(
    bridge_family: DirectBridgeFamilyContractRecord,
    packets: List[SynapticHandoffPacketRecord],
    slices: List[BridgeSliceContractRecord],
) -> str:
    packet_lines = "\n".join(f"- `{packet.packet_id}` `{packet.phase}`" for packet in packets)
    slice_lines = "\n".join(f"- `{slice_record.slice_id}` `{slice_record.phase}`" for slice_record in slices)
    return f"""# 2026-03-13 {bridge_family.bridge_family_id}

- edge id: `{bridge_family.edge_id}`
- truth: `OK`
- primary writeback target: `{bridge_family.primary_writeback_target}`

## Bridge slices

{slice_lines}

## Packets

{packet_lines}

## Replay surface

`{bridge_family.replay_surface}`
"""


def render_manifest(outputs: Dict[str, str], docs_gate: Dict[str, Any]) -> str:
    output_lines = "\n".join(f"- `{label}`: `{path}`" for label, path in outputs.items())
    return f"""# BRIDGE DENSIFICATION MANIFEST

Date: `2026-03-13`
Baseline: `whole-crystal completion`
Derivation: `{DERIVATION_COMMAND}`

## Law

- densify only `CS-001`, `CS-002`, and `CS-003`
- keep `Trading Bot` lanes non-authoritative while Docs is `{docs_gate['status']}`
- keep live family slice counts unchanged
- refresh atlas before freshness claims

## Outputs

{output_lines}
"""


def render_dashboard(dashboard: Dict[str, Any]) -> str:
    bridge_rows = [[name, str(count)] for name, count in sorted(dashboard["bridge_totals"].items())]
    backlog_rows = [[name, str(count)] for name, count in sorted(dashboard["backlog_totals"].items())]
    verifier_rows = [[name, value] for name, value in dashboard["verifier_truth"].items()]
    return f"""# BRIDGE DENSIFICATION DASHBOARD

Date: `2026-03-13`
Truth: `{dashboard['truth']}`
Docs gate: `{dashboard['docs_gate']['status']}`

## Direct bridge families

- bridge families: `{dashboard['bridge_family_count']}`
- bridge slices: `{dashboard['bridge_slice_count']}`
- synaptic packets: `{dashboard['packet_count']}`

## Bridge totals

{markdown_table(["Class", "Count"], bridge_rows)}

## Backlog totals

{markdown_table(["Class", "Count"], backlog_rows)}

## Verifiers

{markdown_table(["Verifier", "Truth"], verifier_rows)}

## Restart seed

`{dashboard['next_restart_seed']}`
"""


def render_verification(verification: Dict[str, Any]) -> str:
    rows = [[name, str(value)] for name, value in verification["checks"].items()]
    unresolved = "\n".join(f"- {item}" for item in verification["unresolved"]) or "- none"
    return f"""# BRIDGE DENSIFICATION VERIFICATION

Date: `2026-03-13`
Truth: `{verification['truth']}`
Docs gate: `{verification['docs_gate']['status']}`

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
    return f"""# bridge_densification_runtime

- generated_at: `{verification['generated_at']}`
- truth: `{verification['truth']}`
- docs_gate: `{verification['docs_gate']['status']}`
- derivation_command: `{DERIVATION_COMMAND}`

## Outputs

{output_lines}
"""


def render_receipt(
    families: List[DirectBridgeFamilyContractRecord],
    backlog: List[BridgeBacklogEntryRecord],
    verification: Dict[str, Any],
) -> str:
    family_lines = "\n".join(
        f"- `{family.bridge_family_id}` `{family.edge_id}` `{family.source_root} -> {family.target_root}`"
        for family in families
    )
    backlog_lines = "\n".join(
        f"- `{entry.weave_id}` `{entry.entry_class}` `{entry.promotion_blocker}`"
        for entry in backlog
    )
    return f"""# 2026-03-13 bridge densification

- generated_at: `{verification['generated_at']}`
- truth: `{verification['truth']}`
- docs_gate: `{verification['docs_gate']['status']}`
- derivation_command: `{DERIVATION_COMMAND}`

## Direct bridge families

{family_lines}

## Governed backlog

{backlog_lines}
"""


def build_direct_bridge_data(
    family_contracts: Dict[str, Dict[str, Any]],
    slice_records: Dict[Tuple[str, int], Dict[str, Any]],
    direct_edges: List[Dict[str, Any]],
) -> Tuple[
    List[DirectBridgeFamilyContractRecord],
    List[BridgeSliceContractRecord],
    List[SynapticHandoffPacketRecord],
    List[Path],
]:
    bridge_families: List[DirectBridgeFamilyContractRecord] = []
    bridge_slices: List[BridgeSliceContractRecord] = []
    bridge_packets: List[SynapticHandoffPacketRecord] = []
    generated_paths: List[Path] = []

    for edge_id in DIRECT_EDGE_ORDER:
        edge = next(item for item in direct_edges if item["edge_id"] == edge_id)
        spec = DIRECT_BRIDGE_SPECS[edge_id]
        source_contract = family_contracts[edge["source_body_id"]]
        target_contract = family_contracts[edge["target_body_id"]]
        source_slice = slice_records[(edge["source_body_id"], 1)]
        target_slice = slice_records[(edge["target_body_id"], 2)]

        slug = bridge_slug(spec["bridge_family_id"])
        capsule_dir = BRIDGE_CAPSULE_ROOT / slug
        route_path = BRIDGE_ROUTE_ROOT / f"ROUTE_{slug}.md"
        replay_path = BRIDGE_EDGE_ROOT / f"REPLAY_{slug}.md"
        verify_path = BRIDGE_EDGE_ROOT / f"VERIFY_{slug}.md"
        receipt_path = BRIDGE_RECEIPT_ROOT / f"2026-03-13_{slug}.md"

        packet_specs = [
            ("EMIT", spec["source_agent"], "grand-central-transit", "emit", f"admit {spec['bridge_family_id']} into Grand Central"),
            ("TRANSIT", "grand-central-transit", spec["receive_agent"], "transit", f"carry {spec['bridge_family_id']} across {' -> '.join(edge['route'])}"),
            ("WRITEBACK", spec["receive_agent"], "overseer", "writeback", f"write {spec['bridge_family_id']} into {target_contract['route_surface']}"),
        ]
        packets: List[SynapticHandoffPacketRecord] = []
        for suffix, source_agent, target_agent, phase, trigger in packet_specs:
            packets.append(
                SynapticHandoffPacketRecord(
                    packet_id=f"BPK-{edge_id}-{suffix}",
                    bridge_family_id=spec["bridge_family_id"],
                    phase=phase,
                    source_agent=source_agent,
                    target_agent=target_agent,
                    source_body_id=edge["source_body_id"],
                    target_body_id=edge["target_body_id"],
                    trigger=trigger,
                    witness_basis=unique(edge.get("witness_basis", [])),
                    route=edge["route"],
                    expected_writeback=[relative_string(route_path), relative_string(replay_path), target_slice["route_surface"]],
                    proof_state="OK",
                    replay_surface=relative_string(replay_path),
                    verification_surface=relative_string(verify_path),
                    note=spec["note"],
                )
            )
        bridge_packets.extend(packets)

        bridge_family = DirectBridgeFamilyContractRecord(
            bridge_family_id=spec["bridge_family_id"],
            edge_id=edge_id,
            source_body_id=edge["source_body_id"],
            source_root=edge["source_root"],
            target_body_id=edge["target_body_id"],
            target_root=edge["target_root"],
            source_family_surface=source_contract["family_surface"],
            target_family_surface=target_contract["family_surface"],
            route_surface=relative_string(route_path),
            replay_surface=relative_string(replay_path),
            runtime_surface=relative_string(BRIDGE_FAMILIES_JSON_PATH),
            restart_seed=f"Write {spec['bridge_family_id']} into {target_slice['route_surface']} and re-verify the direct corridor.",
            authority_rank="authoritative",
            packet_ids=[packet.packet_id for packet in packets],
            witness_basis=unique(
                edge.get("witness_basis", [])
                + [
                    source_contract["family_surface"],
                    target_contract["family_surface"],
                    source_slice["capsule_surface"],
                    target_slice["capsule_surface"],
                    target_slice["route_surface"],
                ]
            ),
            primary_writeback_target=target_slice["route_surface"],
            note=edge.get("note", spec["note"]),
        )

        slice_specs = [
            (
                "01",
                "source-handshake",
                source_slice["chapter_anchor"],
                source_slice["appendix_anchor"],
                anchor_ref(source_slice, "capsule_surface"),
                f"GC-ENTRY::{edge['route'][1]}",
                packets[0].packet_id,
                relative_string(capsule_dir / "01_source_handshake.md"),
                relative_string(route_path),
                relative_string(route_path),
            ),
            (
                "02",
                "grand-central transit",
                "Ch11",
                "AppN",
                "GC-TRANSIT::Ch11/AppN",
                " -> ".join(edge["route"]),
                packets[1].packet_id,
                relative_string(capsule_dir / "02_grand_central_transit.md"),
                relative_string(route_path),
                relative_string(replay_path),
            ),
            (
                "03",
                "target-writeback",
                target_slice["chapter_anchor"],
                target_slice["appendix_anchor"],
                f"GC-EXIT::{edge['route'][-2] if len(edge['route']) > 2 else edge['route'][-1]}",
                anchor_ref(target_slice, "route_surface"),
                packets[2].packet_id,
                relative_string(capsule_dir / "03_target_writeback.md"),
                target_slice["route_surface"],
                target_slice["route_surface"],
            ),
        ]
        slices_for_family: List[BridgeSliceContractRecord] = []
        packet_lookup = {packet.packet_id: packet for packet in packets}
        for suffix, phase_label, chapter_anchor, appendix_anchor, source_anchor, target_anchor, packet_id, capsule_surface, route_surface, writeback_target in slice_specs:
            slice_record = BridgeSliceContractRecord(
                bridge_family_id=spec["bridge_family_id"],
                slice_id=f"BSC-{edge_id}-{suffix}",
                phase=phase_label,
                source_anchor_ref=source_anchor,
                target_anchor_ref=target_anchor,
                packet_id=packet_id,
                writeback_target=writeback_target,
                truth_state="local-witnessed",
                capsule_surface=capsule_surface,
                route_surface=route_surface,
                chapter_anchor=chapter_anchor,
                appendix_anchor=appendix_anchor,
                witness_basis=bridge_family.witness_basis,
                note=f"{phase_label} slice for {spec['bridge_family_id']}.",
            )
            slices_for_family.append(slice_record)
            bridge_slices.append(slice_record)

            slice_path = WORKSPACE_ROOT / capsule_surface.replace("\\", "/")
            write_text(
                slice_path,
                render_bridge_slice_doc(
                    bridge_family=bridge_family,
                    slice_record=slice_record,
                    packets_by_id=packet_lookup,
                    route_points=edge["route"],
                ),
            )
            generated_paths.append(slice_path)

        bridge_family.slice_ids = [slice_record.slice_id for slice_record in slices_for_family]
        bridge_families.append(bridge_family)

        write_text(
            route_path,
            render_bridge_route(
                bridge_family=bridge_family,
                slices=slices_for_family,
                packets=packets,
                route_points=edge["route"],
                target_route_surface=target_slice["route_surface"],
            ),
        )
        write_text(
            replay_path,
            render_bridge_replay(
                bridge_family=bridge_family,
                packets=packets,
                route_points=edge["route"],
                target_route_surface=target_slice["route_surface"],
            ),
        )
        write_text(
            receipt_path,
            render_bridge_receipt(
                bridge_family=bridge_family,
                packets=packets,
                slices=slices_for_family,
            ),
        )
        verify_checks = {
            "source_anchor_rule": slices_for_family[0].chapter_anchor == source_slice["chapter_anchor"]
            and slices_for_family[0].appendix_anchor == source_slice["appendix_anchor"],
            "transit_anchor_rule": slices_for_family[1].chapter_anchor == "Ch11"
            and slices_for_family[1].appendix_anchor == "AppN",
            "target_anchor_rule": slices_for_family[2].chapter_anchor == target_slice["chapter_anchor"]
            and slices_for_family[2].appendix_anchor == target_slice["appendix_anchor"],
            "route_surface_exists": route_path.exists(),
            "replay_surface_exists": replay_path.exists(),
            "receipt_exists": receipt_path.exists(),
        }
        write_text(verify_path, render_bridge_verify(bridge_family, verify_checks))
        generated_paths.extend([route_path, replay_path, verify_path, receipt_path])

    return bridge_families, bridge_slices, bridge_packets, generated_paths


def build_backlog(
    whole_crystal_edges: List[Dict[str, Any]],
    phase4_candidates: List[Dict[str, Any]],
    docs_gate: Dict[str, Any],
) -> List[BridgeBacklogEntryRecord]:
    backlog: List[BridgeBacklogEntryRecord] = []
    for edge in whole_crystal_edges:
        if edge["edge_id"] in DIRECT_EDGE_IDS:
            continue
        if edge["edge_class"] == "inferred-ready":
            backlog.append(
                BridgeBacklogEntryRecord(
                    weave_id=edge["edge_id"],
                    source_id=edge["source_body_id"],
                    source_surface=edge["source_root"],
                    target_id=edge["target_body_id"],
                    target_surface=edge["target_root"],
                    entry_class="inferred-ready",
                    promotion_blocker=f"Docs gate remains {docs_gate['status']}.",
                    next_lawful_action="Keep the lane ranked-near until Google Docs ingress opens and atlas witnesses the mirror.",
                    route=edge.get("route", []),
                    authority_rank=edge.get("authority_rank", ""),
                    note=edge.get("note", ""),
                )
            )
        elif edge["edge_class"] == "quarantined":
            backlog.append(
                BridgeBacklogEntryRecord(
                    weave_id=edge["edge_id"],
                    source_id=edge["source_body_id"],
                    source_surface=edge["source_root"],
                    target_id=edge["target_body_id"],
                    target_surface=edge["target_root"],
                    entry_class="quarantined",
                    promotion_blocker="Source or target remains reserve/dormant or ingress-blocked.",
                    next_lawful_action="Keep the lane quarantined until the shelf is promoted and ingress law is clean.",
                    route=edge.get("route", []),
                    authority_rank=edge.get("authority_rank", ""),
                    note=edge.get("note", ""),
                )
            )

    for candidate in phase4_candidates:
        if candidate.get("weave_id") not in DEEP_PAIRWISE_BACKLOG_IDS:
            continue
        backlog.append(
            BridgeBacklogEntryRecord(
                weave_id=candidate["weave_id"],
                source_id=candidate["src"],
                source_surface=candidate["source_surface"],
                target_id=candidate["dst"],
                target_surface=candidate["target_surface"],
                entry_class="deep-pairwise-backlog",
                promotion_blocker="Deferred to the dedicated deep pairwise weave wave.",
                next_lawful_action="Promote this lane inside the deep pairwise program instead of the direct bridge family lane.",
                route=candidate.get("promotion_route", []),
                authority_rank="backlog-governed",
                note=candidate.get("note", ""),
            )
        )
    return backlog


def build_payloads(
    bridge_families: List[DirectBridgeFamilyContractRecord],
    bridge_slices: List[BridgeSliceContractRecord],
    bridge_packets: List[SynapticHandoffPacketRecord],
    backlog: List[BridgeBacklogEntryRecord],
) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    bridge_family_payload = {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "bridge_families": [record.to_dict() for record in bridge_families],
    }
    bridge_slice_payload = {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "bridge_slices": [record.to_dict() for record in bridge_slices],
    }
    bridge_packet_payload = {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "packets": [record.to_dict() for record in bridge_packets],
    }
    backlog_payload = {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "entries": [record.to_dict() for record in backlog],
    }
    return bridge_family_payload, bridge_slice_payload, bridge_packet_payload, backlog_payload


def render_bridge_ledger(
    bridge_families: List[DirectBridgeFamilyContractRecord],
    backlog: List[BridgeBacklogEntryRecord],
) -> str:
    direct_rows = [
        [
            family.bridge_family_id,
            family.edge_id,
            family.source_root,
            family.target_root,
            family.authority_rank,
            family.primary_writeback_target,
        ]
        for family in bridge_families
    ]
    inferred_rows = [
        [
            entry.weave_id,
            entry.source_surface,
            entry.target_surface,
            entry.promotion_blocker,
            entry.next_lawful_action,
            " -> ".join(entry.route),
        ]
        for entry in backlog
        if entry.entry_class == "inferred-ready"
    ]
    quarantined_rows = [
        [
            entry.weave_id,
            entry.source_surface,
            entry.target_surface,
            entry.promotion_blocker,
            entry.next_lawful_action,
            " -> ".join(entry.route),
        ]
        for entry in backlog
        if entry.entry_class == "quarantined"
    ]
    deep_rows = [
        [
            entry.weave_id,
            entry.source_surface,
            entry.target_surface,
            entry.promotion_blocker,
            entry.next_lawful_action,
            " -> ".join(entry.route),
        ]
        for entry in backlog
        if entry.entry_class == "deep-pairwise-backlog"
    ]
    return """# WHOLE CRYSTAL BRIDGE LEDGER

## Direct bridge families

""" + markdown_table(
        ["Family", "Edge", "Source", "Target", "Authority", "Primary writeback"],
        direct_rows or [["-", "-", "-", "-", "-", "-"]],
    ) + """

## Inferred-ready

""" + markdown_table(
        ["Edge", "Source", "Target", "Blocker", "Next lawful action", "Route"],
        inferred_rows or [["-", "-", "-", "-", "-", "-"]],
    ) + """

## Quarantined

""" + markdown_table(
        ["Edge", "Source", "Target", "Blocker", "Next lawful action", "Route"],
        quarantined_rows or [["-", "-", "-", "-", "-", "-"]],
    ) + """

## Deep pairwise backlog

""" + markdown_table(
        ["Weave", "Source", "Target", "Blocker", "Next lawful action", "Route"],
        deep_rows or [["-", "-", "-", "-", "-", "-"]],
    )


def build_verification(
    bridge_families: List[DirectBridgeFamilyContractRecord],
    bridge_slices: List[BridgeSliceContractRecord],
    backlog: List[BridgeBacklogEntryRecord],
    docs_gate: Dict[str, Any],
    generated_paths: List[Path],
) -> Dict[str, Any]:
    atlas_payload = load_json(CORPUS_ATLAS_PATH)
    atlas_paths = {record.get("relative_path") for record in atlas_payload.get("records", [])}
    generated_relative = [relative_string(path) for path in generated_paths if path.exists()]
    atlas_missing = [path for path in generated_relative if path not in atlas_paths]

    phase4_candidates = load_json(PHASE4_WEAVE_CANDIDATES_PATH).get("candidates", [])
    knowledge_edges = load_json(KNOWLEDGE_FABRIC_EDGES_PATH).get("edges", [])
    pt2_edges = load_json(PHASE4_PT2_EDGES_PATH).get("edges", [])

    phase4_edge_ids = {candidate.get("bridge_edge_id") for candidate in phase4_candidates if candidate.get("bridge_edge_id")}
    knowledge_edge_ids = {edge.get("edge_id") for edge in knowledge_edges}
    pt2_edge_ids = {edge.get("edge_id") for edge in pt2_edges}

    whole_crystal_slices = {
        (record["body_id"], int(record["slice_id"].rsplit("-", 1)[-1])): record
        for record in load_json(WHOLE_CRYSTAL_SLICES_PATH).get("contracts", [])
    }
    bridge_family_lookup = {family.edge_id: family for family in bridge_families}
    bridge_slice_lookup = {record.slice_id: record for record in bridge_slices}

    source_anchor_rule = True
    target_anchor_rule = True
    transit_anchor_rule = True
    for edge_id in DIRECT_EDGE_ORDER:
        family = bridge_family_lookup[edge_id]
        source_slice = whole_crystal_slices[(family.source_body_id, 1)]
        target_slice = whole_crystal_slices[(family.target_body_id, 2)]
        handshake = bridge_slice_lookup[f"BSC-{edge_id}-01"]
        transit = bridge_slice_lookup[f"BSC-{edge_id}-02"]
        writeback = bridge_slice_lookup[f"BSC-{edge_id}-03"]
        source_anchor_rule = source_anchor_rule and handshake.chapter_anchor == source_slice["chapter_anchor"] and handshake.appendix_anchor == source_slice["appendix_anchor"] and source_slice["capsule_surface"] in handshake.source_anchor_ref
        transit_anchor_rule = transit_anchor_rule and transit.chapter_anchor == "Ch11" and transit.appendix_anchor == "AppN"
        target_anchor_rule = target_anchor_rule and writeback.chapter_anchor == target_slice["chapter_anchor"] and writeback.appendix_anchor == target_slice["appendix_anchor"] and target_slice["route_surface"] in writeback.target_anchor_ref

    family_surface_refs = {
        "A16": ["BF-CS-001", "BF-CS-003"],
        "A06": ["BF-CS-001", "BF-CS-002"],
        "A09": ["BF-CS-002"],
        "A15": ["BF-CS-003"],
    }
    family_surface_checks: Dict[str, bool] = {}
    for body_id, expected_refs in family_surface_refs.items():
        text = read_text(RELEVANT_FAMILY_SURFACES[body_id]) if RELEVANT_FAMILY_SURFACES[body_id].exists() else ""
        family_surface_checks[body_id] = all(token in text for token in expected_refs)

    aqm_truth = load_runtime_truth(AQM_RUNTIME_LANE_PATH)
    atlasforge_truth = load_runtime_truth(ATLASFORGE_RUNTIME_LANE_PATH)
    runtime_waist_truth = load_runtime_truth(RUNTIME_WAIST_PATH)

    checks = {
        "direct_bridge_family_count": len(bridge_families) == 3,
        "bridge_slice_count": len(bridge_slices) == 9,
        "route_surfaces_resolve": all(path_exists(record.route_surface) for record in bridge_families),
        "replay_surfaces_resolve": all(path_exists(record.replay_surface) for record in bridge_families),
        "runtime_receipts_resolve": all(
            (BRIDGE_RECEIPT_ROOT / f"2026-03-13_{bridge_slug(record.bridge_family_id)}.md").exists()
            for record in bridge_families
        ),
        "verification_witnesses_resolve": all(
            (BRIDGE_EDGE_ROOT / f"VERIFY_{bridge_slug(record.bridge_family_id)}.md").exists()
            for record in bridge_families
        ),
        "source_anchor_rule": source_anchor_rule,
        "transit_anchor_rule": transit_anchor_rule,
        "target_anchor_rule": target_anchor_rule,
        "family_surfaces_referenced": all(family_surface_checks.values()),
        "inferred_ready_preserved": len([entry for entry in backlog if entry.entry_class == "inferred-ready"]) == 3,
        "quarantined_preserved": len([entry for entry in backlog if entry.entry_class == "quarantined"]) == 3,
        "deep_pairwise_backlog_present": len([entry for entry in backlog if entry.entry_class == "deep-pairwise-backlog"]) == 6,
        "atlas_refresh_complete": not atlas_missing,
        "phase4_direct_edge_ids_present": DIRECT_EDGE_IDS.issubset(phase4_edge_ids),
        "knowledge_fabric_direct_edge_ids_present": DIRECT_EDGE_IDS.issubset(knowledge_edge_ids),
        "phase4_pt2_direct_edge_ids_present": DIRECT_EDGE_IDS.issubset(pt2_edge_ids),
        "runtime_verifiers_green": aqm_truth == "OK" and atlasforge_truth == "OK" and runtime_waist_truth == "OK",
        "docs_gate_preserved_blocked": docs_gate["status"] == "blocked-by-missing-credentials",
    }
    truth = "OK" if all(checks.values()) else "FAIL"
    unresolved: List[str] = []
    if docs_gate["status"] != "open":
        unresolved.append(
            f"Google Docs ingress remains `{docs_gate['status']}` and Trading Bot-facing lanes stay non-authoritative."
        )
    if atlas_missing:
        unresolved.append("One or more bridge-wave surfaces are still missing from corpus_atlas.json.")
    if not all(family_surface_checks.values()):
        unresolved.append("One or more connected family surfaces is missing its bridge-family reference.")
    return {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "truth": truth,
        "docs_gate": docs_gate,
        "checks": checks,
        "runtime_lanes": {
            "aqm_runtime_lane": aqm_truth,
            "atlasforge_runtime_lane": atlasforge_truth,
            "runtime_waist": runtime_waist_truth,
        },
        "atlas_refresh_pending_paths": atlas_missing,
        "unresolved": unresolved,
        "next_restart_seed": "emit -> transit -> receive -> replay -> writeback -> verify",
    }


def build_dashboard(
    bridge_families: List[DirectBridgeFamilyContractRecord],
    bridge_slices: List[BridgeSliceContractRecord],
    bridge_packets: List[SynapticHandoffPacketRecord],
    backlog: List[BridgeBacklogEntryRecord],
    verification: Dict[str, Any],
) -> Dict[str, Any]:
    backlog_totals: Dict[str, int] = {}
    for entry in backlog:
        backlog_totals[entry.entry_class] = backlog_totals.get(entry.entry_class, 0) + 1
    return {
        "generated_at": verification["generated_at"],
        "derivation_version": DERIVATION_VERSION,
        "truth": verification["truth"],
        "docs_gate": verification["docs_gate"],
        "bridge_family_count": len(bridge_families),
        "bridge_slice_count": len(bridge_slices),
        "packet_count": len(bridge_packets),
        "bridge_totals": {
            "direct_bridge_families": len(bridge_families),
            "bridge_slices": len(bridge_slices),
            "synaptic_packets": len(bridge_packets),
        },
        "backlog_totals": backlog_totals,
        "verifier_truth": verification["runtime_lanes"],
        "next_restart_seed": verification["next_restart_seed"],
    }


def main() -> int:
    family_contracts = {
        contract["body_id"]: contract
        for contract in load_json(CRYSTAL_FAMILY_CONTRACTS_PATH).get("contracts", [])
    }
    slice_records = {
        (record["body_id"], int(record["slice_id"].rsplit("-", 1)[-1])): record
        for record in load_json(WHOLE_CRYSTAL_SLICES_PATH).get("contracts", [])
        if record.get("body_id") in {"A06", "A09", "A15", "A16"}
    }
    direct_edges = [
        edge
        for edge in load_json(WHOLE_CRYSTAL_BRIDGES_PATH).get("edges", [])
        if edge.get("edge_id") in DIRECT_EDGE_IDS
    ]
    whole_crystal_edges = load_json(WHOLE_CRYSTAL_BRIDGES_PATH).get("edges", [])
    phase4_candidates = load_json(PHASE4_WEAVE_CANDIDATES_PATH).get("candidates", [])
    docs_gate = load_docs_gate()

    bridge_families, bridge_slices, bridge_packets, family_generated_paths = build_direct_bridge_data(
        family_contracts=family_contracts,
        slice_records=slice_records,
        direct_edges=direct_edges,
    )
    backlog = build_backlog(
        whole_crystal_edges=whole_crystal_edges,
        phase4_candidates=phase4_candidates,
        docs_gate=docs_gate,
    )
    family_payload, slice_payload, packet_payload, backlog_payload = build_payloads(
        bridge_families=bridge_families,
        bridge_slices=bridge_slices,
        bridge_packets=bridge_packets,
        backlog=backlog,
    )

    outputs = {
        "bridge_families_json": relative_string(BRIDGE_FAMILIES_JSON_PATH),
        "bridge_slices_json": relative_string(BRIDGE_SLICES_JSON_PATH),
        "bridge_packets_json": relative_string(BRIDGE_PACKETS_JSON_PATH),
        "bridge_backlog_json": relative_string(BRIDGE_BACKLOG_JSON_PATH),
        "dashboard_json": relative_string(DASHBOARD_JSON_PATH),
        "verification_json": relative_string(VERIFICATION_JSON_PATH),
        "manifest_md": relative_string(MANIFEST_MD_PATH),
        "ledger_md": relative_string(WHOLE_CRYSTAL_LEDGER_MD_PATH),
        "dashboard_md": relative_string(DASHBOARD_MD_PATH),
        "verification_md": relative_string(VERIFICATION_MD_PATH),
        "runtime_md": relative_string(RUNTIME_MD_PATH),
        "receipt_md": relative_string(RECEIPT_MD_PATH),
    }

    write_json(BRIDGE_FAMILIES_JSON_PATH, family_payload)
    write_json(BRIDGE_SLICES_JSON_PATH, slice_payload)
    write_json(BRIDGE_PACKETS_JSON_PATH, packet_payload)
    write_json(BRIDGE_BACKLOG_JSON_PATH, backlog_payload)
    write_json(BRIDGE_FAMILIES_JSON_MIRROR, family_payload)
    write_json(BRIDGE_SLICES_JSON_MIRROR, slice_payload)
    write_json(BRIDGE_PACKETS_JSON_MIRROR, packet_payload)
    write_json(BRIDGE_BACKLOG_JSON_MIRROR, backlog_payload)
    write_text(MANIFEST_MD_PATH, render_manifest(outputs, docs_gate))
    write_text(WHOLE_CRYSTAL_LEDGER_MD_PATH, render_bridge_ledger(bridge_families, backlog))

    provisional_verification = {
        "generated_at": utc_now(),
        "truth": "NEAR",
        "docs_gate": docs_gate,
        "checks": {},
        "runtime_lanes": {
            "aqm_runtime_lane": load_runtime_truth(AQM_RUNTIME_LANE_PATH),
            "atlasforge_runtime_lane": load_runtime_truth(ATLASFORGE_RUNTIME_LANE_PATH),
            "runtime_waist": load_runtime_truth(RUNTIME_WAIST_PATH),
        },
        "next_restart_seed": "emit -> transit -> receive -> replay -> writeback -> verify",
        "unresolved": ["Bridge-wave atlas refresh pending."],
    }
    provisional_dashboard = build_dashboard(
        bridge_families=bridge_families,
        bridge_slices=bridge_slices,
        bridge_packets=bridge_packets,
        backlog=backlog,
        verification=provisional_verification,
    )
    write_json(DASHBOARD_JSON_PATH, provisional_dashboard)
    write_json(VERIFICATION_JSON_PATH, provisional_verification)
    write_json(DASHBOARD_JSON_MIRROR, provisional_dashboard)
    write_json(VERIFICATION_JSON_MIRROR, provisional_verification)
    write_text(DASHBOARD_MD_PATH, render_dashboard(provisional_dashboard))
    write_text(VERIFICATION_MD_PATH, render_verification(provisional_verification))
    write_text(RUNTIME_MD_PATH, render_runtime(outputs, provisional_verification))
    write_text(RECEIPT_MD_PATH, render_receipt(bridge_families, backlog, provisional_verification))

    generated_paths = [
        BRIDGE_FAMILIES_JSON_PATH,
        BRIDGE_SLICES_JSON_PATH,
        BRIDGE_PACKETS_JSON_PATH,
        BRIDGE_BACKLOG_JSON_PATH,
        BRIDGE_FAMILIES_JSON_MIRROR,
        BRIDGE_SLICES_JSON_MIRROR,
        BRIDGE_PACKETS_JSON_MIRROR,
        BRIDGE_BACKLOG_JSON_MIRROR,
        MANIFEST_MD_PATH,
        WHOLE_CRYSTAL_LEDGER_MD_PATH,
        DASHBOARD_JSON_PATH,
        VERIFICATION_JSON_PATH,
        DASHBOARD_JSON_MIRROR,
        VERIFICATION_JSON_MIRROR,
        DASHBOARD_MD_PATH,
        VERIFICATION_MD_PATH,
        RUNTIME_MD_PATH,
        RECEIPT_MD_PATH,
        *family_generated_paths,
        *RELEVANT_FAMILY_SURFACES.values(),
    ]
    refresh_corpus_atlas(generated_paths)

    verification = build_verification(
        bridge_families=bridge_families,
        bridge_slices=bridge_slices,
        backlog=backlog,
        docs_gate=docs_gate,
        generated_paths=generated_paths,
    )
    dashboard = build_dashboard(
        bridge_families=bridge_families,
        bridge_slices=bridge_slices,
        bridge_packets=bridge_packets,
        backlog=backlog,
        verification=verification,
    )

    write_json(DASHBOARD_JSON_PATH, dashboard)
    write_json(VERIFICATION_JSON_PATH, verification)
    write_json(DASHBOARD_JSON_MIRROR, dashboard)
    write_json(VERIFICATION_JSON_MIRROR, verification)
    write_text(DASHBOARD_MD_PATH, render_dashboard(dashboard))
    write_text(VERIFICATION_MD_PATH, render_verification(verification))
    write_text(RUNTIME_MD_PATH, render_runtime(outputs, verification))
    write_text(RECEIPT_MD_PATH, render_receipt(bridge_families, backlog, verification))

    refresh_corpus_atlas(
        [
            DASHBOARD_JSON_PATH,
            VERIFICATION_JSON_PATH,
            DASHBOARD_JSON_MIRROR,
            VERIFICATION_JSON_MIRROR,
            DASHBOARD_MD_PATH,
            VERIFICATION_MD_PATH,
            RUNTIME_MD_PATH,
            RECEIPT_MD_PATH,
        ]
    )

    print(f"Wrote bridge densification artifacts under {SELF_ACTUALIZE_ROOT}")
    print(f"Docs gate: {docs_gate['status']}")
    print(f"Truth: {verification['truth']}")
    return 0 if verification["truth"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
