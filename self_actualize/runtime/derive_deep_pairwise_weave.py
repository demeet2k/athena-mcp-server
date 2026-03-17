from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from self_actualize.runtime.crystal_remaster_contracts import (
    DeepPairwiseFamilyContractRecord,
    DeepPairwiseSliceContractRecord,
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
DEEP_ROOT = (
    MYCELIUM_BRAIN_ROOT
    / "dynamic_neural_network"
    / "14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK"
)
LEVEL3_MAP_PATH = DEEP_ROOT / "07_METRO_STACK" / "02_level_3_deeper_neural_map.md"
APPENDIX_Q_PATH = DEEP_ROOT / "08_APPENDIX_CRYSTAL" / "AppQ_appendix_only_metro_map.md"

DERIVATION_VERSION = "2026-03-13.deep-pairwise-v1"
DERIVATION_COMMAND = "python -m self_actualize.runtime.derive_deep_pairwise_weave"

PAIR_REGISTRY_PATH = SELF_ACTUALIZE_ROOT / "phase4_pair_registry.json"
BRIDGE_BACKLOG_PATH = SELF_ACTUALIZE_ROOT / "bridge_densification_backlog.json"
BRIDGE_FAMILIES_PATH = SELF_ACTUALIZE_ROOT / "bridge_densification_direct_bridge_families.json"
PHASE4_WEAVE_CANDIDATES_PATH = SELF_ACTUALIZE_ROOT / "phase4_weave_candidates.json"
KNOWLEDGE_FABRIC_EDGES_PATH = SELF_ACTUALIZE_ROOT / "knowledge_fabric_edges.json"
PHASE4_PT2_EDGES_PATH = SELF_ACTUALIZE_ROOT / "phase4_pt2_system_crosswalk_edges.json"
WHOLE_CRYSTAL_LEDGER_PATH = NERVOUS_SYSTEM_ROOT / "85_EDGES" / "WHOLE_CRYSTAL_BRIDGE_LEDGER.md"
CORPUS_ATLAS_PATH = SELF_ACTUALIZE_ROOT / "corpus_atlas.json"
AQM_RUNTIME_LANE_PATH = SELF_ACTUALIZE_ROOT / "aqm_runtime_lane.json"
ATLASFORGE_RUNTIME_LANE_PATH = SELF_ACTUALIZE_ROOT / "atlasforge_runtime_lane.json"
RUNTIME_WAIST_PATH = SELF_ACTUALIZE_ROOT / "runtime_waist_verification.json"
LIVE_DOCS_GATE_PATH = SELF_ACTUALIZE_ROOT / "live_docs_gate_status.md"

FAMILIES_JSON_PATH = SELF_ACTUALIZE_ROOT / "deep_pairwise_families.json"
SLICES_JSON_PATH = SELF_ACTUALIZE_ROOT / "deep_pairwise_slices.json"
PACKETS_JSON_PATH = SELF_ACTUALIZE_ROOT / "deep_pairwise_packets.json"
DASHBOARD_JSON_PATH = SELF_ACTUALIZE_ROOT / "deep_pairwise_dashboard.json"
VERIFICATION_JSON_PATH = SELF_ACTUALIZE_ROOT / "deep_pairwise_verification.json"

FAMILIES_JSON_MIRROR = REGISTRY_ROOT / FAMILIES_JSON_PATH.name
SLICES_JSON_MIRROR = REGISTRY_ROOT / SLICES_JSON_PATH.name
PACKETS_JSON_MIRROR = REGISTRY_ROOT / PACKETS_JSON_PATH.name
DASHBOARD_JSON_MIRROR = REGISTRY_ROOT / DASHBOARD_JSON_PATH.name
VERIFICATION_JSON_MIRROR = REGISTRY_ROOT / VERIFICATION_JSON_PATH.name

MANIFEST_MD_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "DEEP_PAIRWISE_WEAVE_MANIFEST.md"
LEDGER_MD_PATH = NERVOUS_SYSTEM_ROOT / "85_EDGES" / "DEEP_PAIRWISE_WEAVE_LEDGER.md"
DASHBOARD_MD_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "DEEP_PAIRWISE_WEAVE_DASHBOARD.md"
VERIFICATION_MD_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "DEEP_PAIRWISE_WEAVE_VERIFICATION.md"
RUNTIME_MD_PATH = MYCELIUM_BRAIN_ROOT / "nervous_system" / "31_deep_pairwise_weave_runtime.md"
RECEIPT_MD_PATH = MYCELIUM_BRAIN_ROOT / "receipts" / "2026-03-13_deep_pairwise_weave.md"

FAMILY_EDGE_ROOT = NERVOUS_SYSTEM_ROOT / "85_EDGES" / "deep_pairwise_families"
ROUTE_ROOT = (
    MYCELIUM_BRAIN_ROOT / "nervous_system" / "routes" / "whole_crystal" / "deep_pairwise_families"
)
RECEIPT_ROOT = MYCELIUM_BRAIN_ROOT / "receipts" / "deep_pairwise_families"

DIRECT_EDGE_IDS = {"CS-001", "CS-002", "CS-003"}
PAIRWISE_ORDER = [f"WV-{index:04d}" for index in range(7, 13)]
PAIRWISE_SPECS: Dict[str, Dict[str, str]] = {
    "WV-0007": {"source_pair_id": "P-K01-K01", "target_pair_id": "P-K01-K16"},
    "WV-0008": {"source_pair_id": "P-K01-K10", "target_pair_id": "P-K16-K10"},
    "WV-0009": {"source_pair_id": "P-K10-K01", "target_pair_id": "P-K10-K16"},
    "WV-0010": {"source_pair_id": "P-K01-K08", "target_pair_id": "P-K16-K08"},
    "WV-0011": {"source_pair_id": "P-K08-K01", "target_pair_id": "P-K08-K16"},
    "WV-0012": {"source_pair_id": "P-K01-K02", "target_pair_id": "P-K16-K02"},
}
SLICE_PHASES: List[Tuple[str, str, str]] = [
    ("01", "source-pair replay", "Replay the source pair as the emitting matrix witness."),
    ("02", "GCW-GCZ transit", "Carry the pair pressure across the fixed Level 3 transit spine."),
    ("03", "target-pair writeback", "Land the promoted pair into the target cell as the primary writeback target."),
]


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


def to_relative_path(path: str) -> str:
    normalized = normalize_path(path)
    candidate = Path(normalized)
    if candidate.is_absolute():
        return relative_string(candidate)
    return normalized


def load_docs_gate() -> Dict[str, str]:
    status = "blocked-by-missing-credentials"
    if LIVE_DOCS_GATE_PATH.exists():
        markdown = read_text(LIVE_DOCS_GATE_PATH)
        if "Missing OAuth client file: credentials.json" in markdown:
            status = "blocked-by-missing-credentials"
        elif "token.json" in markdown:
            status = "blocked-by-missing-token"
        elif "Command status: `OPEN`" in markdown:
            status = "open"
    return {
        "status": status,
        "resolution": "open" if status == "open" else "lawfully-isolated",
        "fallback_mode": "mirrored-live-docs" if status == "open" else "local-first-truth-corridor",
    }


def load_runtime_truth(path: Path) -> str:
    if not path.exists():
        return "UNKNOWN"
    return load_json(path).get("truth", "UNKNOWN")


def family_slug(pairwise_family_id: str) -> str:
    return pairwise_family_id.lower().replace("-", "_")


def family_stem(pairwise_family_id: str) -> str:
    return pairwise_family_id.replace("-", "_")


def pair_surface_from_record(record: Dict[str, Any]) -> str:
    for path in record.get("source_paths", []):
        candidate = Path(path)
        if candidate.suffix.lower() == ".md" and candidate.exists():
            return relative_string(candidate)
    fallback = record.get("source_paths", [""])
    return to_relative_path(fallback[0]) if fallback else ""


def pair_label(record: Dict[str, Any]) -> str:
    return record.get("pair_title", record.get("pair_id", ""))


def pair_block(marker: str, heading: str, lines: List[str]) -> str:
    body = "\n".join(lines)
    return f"<!-- {marker}:START -->\n## {heading}\n\n{body}\n<!-- {marker}:END -->"


def upsert_marked_block(path: Path, marker: str, block: str) -> None:
    start = f"<!-- {marker}:START -->"
    end = f"<!-- {marker}:END -->"
    text = read_text(path) if path.exists() else ""
    if start in text and end in text:
        prefix, remainder = text.split(start, 1)
        _, suffix = remainder.split(end, 1)
        new_text = prefix.rstrip() + "\n\n" + block.rstrip() + "\n" + suffix.lstrip("\n")
    else:
        base = text.rstrip()
        if base:
            new_text = base + "\n\n" + block.rstrip() + "\n"
        else:
            new_text = block.rstrip() + "\n"
    write_text(path, new_text)


def render_family_summary(
    family: DeepPairwiseFamilyContractRecord,
    source_record: Dict[str, Any],
    target_record: Dict[str, Any],
    packet_ids: List[str],
    slice_ids: List[str],
) -> str:
    witness_lines = "\n".join(f"- `{item}`" for item in family.witness_basis)
    relation_lines = "\n".join(f"- `{item}`" for item in family.relation_stack)
    appendix_lines = "\n".join(f"- `{item}`" for item in family.appendix_stack)
    packet_lines = "\n".join(f"- `{item}`" for item in packet_ids)
    slice_lines = "\n".join(f"- `{item}`" for item in slice_ids)
    return f"""# {family.pairwise_family_id}

Date: `2026-03-13`
Truth: `OK`
Weave: `{family.weave_id}`

## Pair promotion

- source pair: `{family.source_pair_id}` `{pair_label(source_record)}`
- target pair: `{family.target_pair_id}` `{pair_label(target_record)}`
- metro level: `{family.metro_level}`
- authority: `{family.authority_rank}`
- primary writeback target: `{family.primary_writeback_target}`

## Relation stack

{relation_lines}

## Appendix stack

{appendix_lines}

## Route surfaces

- route surface: `{family.route_surface}`
- replay surface: `{family.replay_surface}`
- runtime surface: `{family.runtime_surface}`

## Slice ids

{slice_lines}

## Packet ids

{packet_lines}

## Witness basis

{witness_lines}

## Restart seed

`{family.restart_seed}`
"""


def render_slice_doc(
    family: DeepPairwiseFamilyContractRecord,
    slice_record: DeepPairwiseSliceContractRecord,
    packet: SynapticHandoffPacketRecord,
) -> str:
    witness_lines = "\n".join(f"- `{item}`" for item in slice_record.witness_basis)
    return f"""# {slice_record.slice_id}

Date: `2026-03-13`
Truth: `{slice_record.truth_state}`
Family: `{family.pairwise_family_id}`

## Phase

- weave: `{family.weave_id}`
- phase: `{slice_record.phase}`
- packet id: `{slice_record.packet_id}`

## Anchors

- source anchor: `{slice_record.source_anchor_ref}`
- target anchor: `{slice_record.target_anchor_ref}`
- writeback target: `{slice_record.writeback_target}`

## Packet

- source agent: `{packet.source_agent}`
- target agent: `{packet.target_agent}`
- route: `{" -> ".join(packet.route)}`

## Witness basis

{witness_lines}

## Note

{slice_record.note}
"""


def render_route(
    family: DeepPairwiseFamilyContractRecord,
    source_record: Dict[str, Any],
    target_record: Dict[str, Any],
    slices: List[DeepPairwiseSliceContractRecord],
    packets: List[SynapticHandoffPacketRecord],
) -> str:
    slice_lines = "\n".join(
        f"- `{record.slice_id}` `{record.phase}` `{record.surface}`" for record in slices
    )
    packet_lines = "\n".join(
        f"- `{packet.packet_id}` `{packet.phase}` `{packet.source_agent} -> {packet.target_agent}`"
        for packet in packets
    )
    appendix_lines = "\n".join(f"- `{item}`" for item in family.appendix_stack)
    return f"""# ROUTE {family.pairwise_family_id}

Date: `2026-03-13`
Truth: `OK`

## Pair corridor

- weave: `{family.weave_id}`
- source pair: `{family.source_pair_id}` `{pair_label(source_record)}`
- target pair: `{family.target_pair_id}` `{pair_label(target_record)}`
- metro level: `{family.metro_level}`
- transit spine: `GCW -> GCZ`
- primary writeback target: `{family.primary_writeback_target}`

## Canonical slices

{slice_lines}

## Packet lifecycle

- `source-pair replay`
- `GCW-GCZ transit`
- `target-pair writeback`
- `verify`

## Active packets

{packet_lines}

## Appendix stack

{appendix_lines}

## Restart seed

`{family.restart_seed}`
"""


def render_replay(
    family: DeepPairwiseFamilyContractRecord,
    packets: List[SynapticHandoffPacketRecord],
) -> str:
    rows = [
        [packet.packet_id, packet.phase, packet.source_agent, packet.target_agent, " -> ".join(packet.route)]
        for packet in packets
    ]
    return f"""# REPLAY {family.pairwise_family_id}

Date: `2026-03-13`
Truth: `OK`

## Replay law

`source-pair replay -> GCW-GCZ transit -> target-pair writeback -> verify`

## Family

- weave: `{family.weave_id}`
- metro level: `{family.metro_level}`
- primary writeback target: `{family.primary_writeback_target}`

## Packets

{markdown_table(["Packet", "Phase", "Source", "Target", "Route"], rows)}
"""


def render_verify(
    family: DeepPairwiseFamilyContractRecord,
    checks: Dict[str, bool],
) -> str:
    rows = [[label, str(result)] for label, result in checks.items()]
    return f"""# VERIFY {family.pairwise_family_id}

Date: `2026-03-13`
Truth: `{"OK" if all(checks.values()) else "FAIL"}`

## Checks

{markdown_table(["Check", "Result"], rows)}
"""


def render_family_receipt(
    family: DeepPairwiseFamilyContractRecord,
    packets: List[SynapticHandoffPacketRecord],
    slices: List[DeepPairwiseSliceContractRecord],
) -> str:
    slice_lines = "\n".join(f"- `{record.slice_id}` `{record.phase}`" for record in slices)
    packet_lines = "\n".join(f"- `{packet.packet_id}` `{packet.phase}`" for packet in packets)
    return f"""# 2026-03-13 {family.pairwise_family_id}

- weave: `{family.weave_id}`
- truth: `OK`
- primary writeback target: `{family.primary_writeback_target}`

## Slices

{slice_lines}

## Packets

{packet_lines}

## Replay surface

`{family.replay_surface}`
"""


def render_manifest(outputs: Dict[str, str], docs_gate: Dict[str, str]) -> str:
    output_lines = "\n".join(f"- `{label}`: `{path}`" for label, path in outputs.items())
    return f"""# DEEP PAIRWISE WEAVE MANIFEST

Date: `2026-03-13`
Baseline: `bridge densification`
Derivation: `{DERIVATION_COMMAND}`

## Law

- promote only `WV-0007` through `WV-0012`
- keep the direct bridge layer frozen as baseline
- keep `Trading Bot` lanes inferred or quarantined while Docs is `{docs_gate['status']}`
- use Level 3 plus Appendix `Q` as the pairwise transit law
- refresh atlas before dashboards claim freshness

## Outputs

{output_lines}
"""


def render_ledger(
    families: List[DeepPairwiseFamilyContractRecord],
    pair_records: Dict[str, Dict[str, Any]],
) -> str:
    rows = []
    for family in families:
        rows.append(
            [
                family.pairwise_family_id,
                family.weave_id,
                pair_label(pair_records[family.source_pair_id]),
                pair_label(pair_records[family.target_pair_id]),
                family.metro_level,
                ", ".join(family.appendix_stack),
                family.primary_writeback_target,
            ]
        )
    return "# DEEP PAIRWISE WEAVE LEDGER\n\n" + markdown_table(
        ["Family", "Weave", "Source Pair", "Target Pair", "Metro", "Appendix Stack", "Primary Writeback"],
        rows or [["-", "-", "-", "-", "-", "-", "-"]],
    )


def render_dashboard(dashboard: Dict[str, Any]) -> str:
    count_rows = [[name, str(count)] for name, count in sorted(dashboard["counts"].items())]
    verifier_rows = [[name, value] for name, value in dashboard["verifier_truth"].items()]
    return f"""# DEEP PAIRWISE WEAVE DASHBOARD

Date: `2026-03-13`
Truth: `{dashboard['truth']}`
Docs gate: `{dashboard['docs_gate']['status']}`

## Counts

{markdown_table(["Measure", "Count"], count_rows)}

## Metro law

- primary metro level: `{dashboard['metro_level']}`
- transit spine: `{dashboard['transit_spine']}`
- appendix `Q` mandatory: `{dashboard['appendix_q_mandatory']}`

## Verifiers

{markdown_table(["Verifier", "Truth"], verifier_rows)}

## Restart seed

`{dashboard['next_restart_seed']}`
"""


def render_verification(verification: Dict[str, Any]) -> str:
    rows = [[name, str(value)] for name, value in verification["checks"].items()]
    unresolved = "\n".join(f"- {item}" for item in verification["unresolved"]) or "- none"
    return f"""# DEEP PAIRWISE WEAVE VERIFICATION

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
    return f"""# 31 DEEP PAIRWISE WEAVE RUNTIME

Date: `2026-03-13`
Truth: `{verification['truth']}`
Docs gate: `{verification['docs_gate']['status']}`

## Output surfaces

{output_lines}

## Runtime verifiers

- `AQM`: `{verification['runtime_lanes']['aqm_runtime_lane']}`
- `ATLAS FORGE`: `{verification['runtime_lanes']['atlasforge_runtime_lane']}`
- `runtime waist`: `{verification['runtime_lanes']['runtime_waist']}`

## Restart seed

`{verification['next_restart_seed']}`
"""


def render_wave_receipt(
    families: List[DeepPairwiseFamilyContractRecord],
    verification: Dict[str, Any],
) -> str:
    family_lines = "\n".join(
        f"- `{family.pairwise_family_id}` `{family.source_pair_id} -> {family.target_pair_id}`"
        for family in families
    )
    return f"""# 2026-03-13 deep pairwise weave

- truth: `{verification['truth']}`
- docs gate: `{verification['docs_gate']['status']}`
- promoted families: `{len(families)}`

## Families

{family_lines}

## Restart seed

`{verification['next_restart_seed']}`
"""


def render_whole_crystal_bridge_ledger(
    direct_bridge_families: List[Dict[str, Any]],
    backlog_entries: List[Dict[str, Any]],
) -> str:
    direct_rows = [
        [
            record["bridge_family_id"],
            record["edge_id"],
            record.get("source_root", record["source_body_id"]),
            record.get("target_root", record["target_body_id"]),
            record["authority_rank"],
            record["primary_writeback_target"],
        ]
        for record in direct_bridge_families
    ]
    inferred_rows = [
        [
            record["weave_id"],
            record["source_surface"],
            record["target_surface"],
            record["promotion_blocker"],
            record["next_lawful_action"],
            " -> ".join(record.get("route", [])),
        ]
        for record in backlog_entries
        if record.get("class") == "inferred-ready"
    ]
    quarantined_rows = [
        [
            record["weave_id"],
            record["source_surface"],
            record["target_surface"],
            record["promotion_blocker"],
            record["next_lawful_action"],
            " -> ".join(record.get("route", [])),
        ]
        for record in backlog_entries
        if record.get("class") == "quarantined"
    ]
    promotion_rows = [
        [
            weave_id,
            PAIRWISE_SPECS[weave_id]["source_pair_id"],
            PAIRWISE_SPECS[weave_id]["target_pair_id"],
            "promoted-to-deep-pairwise-wave",
            f"DPF-{weave_id}",
            " -> ".join(next(item["route"] for item in backlog_entries if item["weave_id"] == weave_id)),
        ]
        for weave_id in PAIRWISE_ORDER
    ]
    return (
        "# WHOLE CRYSTAL BRIDGE LEDGER\n\n"
        + "## Direct bridge families\n\n"
        + markdown_table(
            ["Family", "Edge", "Source", "Target", "Authority", "Primary writeback"],
            direct_rows or [["-", "-", "-", "-", "-", "-"]],
        )
        + "\n\n## Inferred-ready\n\n"
        + markdown_table(
            ["Edge", "Source", "Target", "Blocker", "Next lawful action", "Route"],
            inferred_rows or [["-", "-", "-", "-", "-", "-"]],
        )
        + "\n\n## Quarantined\n\n"
        + markdown_table(
            ["Edge", "Source", "Target", "Blocker", "Next lawful action", "Route"],
            quarantined_rows or [["-", "-", "-", "-", "-", "-"]],
        )
        + "\n\n## Deep pairwise wave promotion\n\n"
        + markdown_table(
            ["Weave", "Source Pair", "Target Pair", "Status", "Tracker", "Route"],
            promotion_rows or [["-", "-", "-", "-", "-", "-"]],
        )
    )


def build_family_checks(
    family: DeepPairwiseFamilyContractRecord,
    slices: List[DeepPairwiseSliceContractRecord],
    packets: List[SynapticHandoffPacketRecord],
    source_pair_text: str,
    target_pair_text: str,
) -> Dict[str, bool]:
    return {
        "slice_count": len(slices) == 3,
        "packet_count": len(packets) == 3,
        "appq_present": "AppQ" in family.appendix_stack,
        "metro_level": family.metro_level == "Level 3",
        "transit_spine": all(
            packet.route == [family.source_pair_id, "GCW", "GCZ", family.target_pair_id]
            for packet in packets
        ),
        "primary_writeback_target": family.primary_writeback_target == family.target_pair_surface,
        "source_backlink": family.pairwise_family_id in source_pair_text and "source-pair replay" in source_pair_text,
        "target_writeback": family.pairwise_family_id in target_pair_text and "primary writeback target" in target_pair_text,
    }


def build_verification(
    families: List[DeepPairwiseFamilyContractRecord],
    slices: List[DeepPairwiseSliceContractRecord],
    packets: List[SynapticHandoffPacketRecord],
    docs_gate: Dict[str, str],
    generated_paths: List[Path],
) -> Dict[str, Any]:
    atlas_paths = {
        record.get("relative_path")
        for record in load_json(CORPUS_ATLAS_PATH).get("records", [])
        if record.get("relative_path")
    }
    generated_relative = [relative_string(path) for path in generated_paths if path.exists()]
    atlas_missing = [path for path in generated_relative if path not in atlas_paths]

    phase4_edge_ids = {
        candidate.get("bridge_edge_id")
        for candidate in load_json(PHASE4_WEAVE_CANDIDATES_PATH).get("candidates", [])
        if candidate.get("bridge_edge_id")
    }
    knowledge_edge_ids = {
        edge.get("edge_id")
        for edge in load_json(KNOWLEDGE_FABRIC_EDGES_PATH).get("edges", [])
        if edge.get("edge_id")
    }
    pt2_edge_ids = {
        edge.get("edge_id")
        for edge in load_json(PHASE4_PT2_EDGES_PATH).get("edges", [])
        if edge.get("edge_id")
    }

    families_by_id = {family.pairwise_family_id: family for family in families}
    slices_by_family: Dict[str, List[DeepPairwiseSliceContractRecord]] = {}
    packets_by_weave: Dict[str, List[SynapticHandoffPacketRecord]] = {}
    for record in slices:
        slices_by_family.setdefault(record.pairwise_family_id, []).append(record)
    for packet in packets:
        packets_by_weave.setdefault(packet.weave_id, []).append(packet)

    pair_text_checks: Dict[str, bool] = {}
    for family in families:
        source_path = WORKSPACE_ROOT / family.source_pair_surface.replace("\\", "/")
        target_path = WORKSPACE_ROOT / family.target_pair_surface.replace("\\", "/")
        source_text = read_text(source_path) if source_path.exists() else ""
        target_text = read_text(target_path) if target_path.exists() else ""
        family_checks = build_family_checks(
            family=family,
            slices=slices_by_family.get(family.pairwise_family_id, []),
            packets=packets_by_weave.get(family.weave_id, []),
            source_pair_text=source_text,
            target_pair_text=target_text,
        )
        pair_text_checks[family.pairwise_family_id] = all(family_checks.values())

    backlog_payload = load_json(BRIDGE_BACKLOG_PATH).get("entries", [])
    inferred_ready_count = len([entry for entry in backlog_payload if entry.get("class") == "inferred-ready"])
    quarantined_count = len([entry for entry in backlog_payload if entry.get("class") == "quarantined"])
    whole_crystal_ledger = read_text(WHOLE_CRYSTAL_LEDGER_PATH) if WHOLE_CRYSTAL_LEDGER_PATH.exists() else ""

    aqm_truth = load_runtime_truth(AQM_RUNTIME_LANE_PATH)
    atlasforge_truth = load_runtime_truth(ATLASFORGE_RUNTIME_LANE_PATH)
    runtime_waist_truth = load_runtime_truth(RUNTIME_WAIST_PATH)

    checks = {
        "strict_scope_six_families": len(families) == 6 and set(family.weave_id for family in families) == set(PAIRWISE_ORDER),
        "slice_count": len(slices) == 18,
        "packet_count": len(packets) == 18,
        "route_surfaces_resolve": all(path_exists(family.route_surface) for family in families),
        "replay_surfaces_resolve": all(path_exists(family.replay_surface) for family in families),
        "runtime_receipts_resolve": all(path_exists(family.runtime_surface) for family in families),
        "verification_witnesses_resolve": all(
            path_exists(relative_string(FAMILY_EDGE_ROOT / f"VERIFY_{family_stem(family.pairwise_family_id)}.md"))
            for family in families
        ),
        "family_checks_green": all(pair_text_checks.values()),
        "level3_metro_rule": all(family.metro_level == "Level 3" for family in families),
        "appendix_q_rule": all("AppQ" in family.appendix_stack for family in families),
        "transit_spine_rule": all(
            packet.route == [packet.source_pair_id, "GCW", "GCZ", packet.target_pair_id]
            for packet in packets
        ),
        "target_writeback_rule": all(
            families_by_id[slice_record.pairwise_family_id].primary_writeback_target
            == families_by_id[slice_record.pairwise_family_id].target_pair_surface
            for slice_record in slices
            if slice_record.phase == "target-pair writeback"
        ),
        "whole_crystal_ledger_promoted": whole_crystal_ledger.count("promoted-to-deep-pairwise-wave") == 6
        and "Deferred to the dedicated deep pairwise weave wave." not in whole_crystal_ledger,
        "inferred_ready_preserved": inferred_ready_count == 3,
        "quarantined_preserved": quarantined_count == 3,
        "atlas_refresh_complete": not atlas_missing,
        "phase4_direct_edges_preserved": DIRECT_EDGE_IDS.issubset(phase4_edge_ids),
        "knowledge_fabric_direct_edges_preserved": DIRECT_EDGE_IDS.issubset(knowledge_edge_ids),
        "phase4_pt2_direct_edges_preserved": DIRECT_EDGE_IDS.issubset(pt2_edge_ids),
        "runtime_verifiers_green": aqm_truth == "OK" and atlasforge_truth == "OK" and runtime_waist_truth == "OK",
        "docs_gate_preserved_blocked": docs_gate["status"] == "blocked-by-missing-credentials",
    }
    truth = "OK" if all(checks.values()) else "FAIL"
    unresolved: List[str] = []
    if docs_gate["status"] != "open":
        unresolved.append(
            f"Google Docs ingress remains `{docs_gate['status']}` so Trading Bot-facing lanes stay non-authoritative."
        )
    if atlas_missing:
        unresolved.append("One or more deep-pairwise wave surfaces is still missing from corpus_atlas.json.")
    if not all(pair_text_checks.values()):
        unresolved.append("One or more source or target pair surfaces is missing its generated deep-pairwise block.")

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
        "next_restart_seed": "source-pair replay -> GCW-GCZ transit -> target-pair writeback -> verify -> seed-next-pair",
    }


def build_dashboard(
    families: List[DeepPairwiseFamilyContractRecord],
    slices: List[DeepPairwiseSliceContractRecord],
    packets: List[SynapticHandoffPacketRecord],
    verification: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "generated_at": verification["generated_at"],
        "derivation_version": DERIVATION_VERSION,
        "truth": verification["truth"],
        "docs_gate": verification["docs_gate"],
        "counts": {
            "deep_pairwise_families": len(families),
            "deep_pairwise_slices": len(slices),
            "deep_pairwise_packets": len(packets),
            "promoted_weaves": len(families),
        },
        "metro_level": "Level 3",
        "transit_spine": "GCW -> GCZ",
        "appendix_q_mandatory": True,
        "verifier_truth": verification["runtime_lanes"],
        "next_restart_seed": verification["next_restart_seed"],
    }


def main() -> int:
    docs_gate = load_docs_gate()
    pair_records = {
        record["pair_id"]: record
        for record in load_json(PAIR_REGISTRY_PATH).get("pairs", [])
        if record.get("pair_id")
    }
    backlog_entries = load_json(BRIDGE_BACKLOG_PATH).get("entries", [])
    direct_bridge_families = load_json(BRIDGE_FAMILIES_PATH).get("bridge_families", [])

    families: List[DeepPairwiseFamilyContractRecord] = []
    slices: List[DeepPairwiseSliceContractRecord] = []
    packets: List[SynapticHandoffPacketRecord] = []
    generated_paths: List[Path] = []

    for weave_id in PAIRWISE_ORDER:
        spec = PAIRWISE_SPECS[weave_id]
        source_record = pair_records[spec["source_pair_id"]]
        target_record = pair_records[spec["target_pair_id"]]
        family_id = f"DPF-{weave_id}"
        slug = family_slug(family_id)
        stem = family_stem(family_id)

        source_surface = pair_surface_from_record(source_record)
        target_surface = pair_surface_from_record(target_record)

        family_doc_path = FAMILY_EDGE_ROOT / f"{stem}.md"
        verify_path = FAMILY_EDGE_ROOT / f"VERIFY_{stem}.md"
        route_path = ROUTE_ROOT / f"ROUTE_{slug}.md"
        replay_path = ROUTE_ROOT / f"REPLAY_{slug}.md"
        runtime_path = RECEIPT_ROOT / f"2026-03-13_{slug}.md"

        packet_ids = [
            f"DPK-{weave_id}-REPLAY",
            f"DPK-{weave_id}-TRANSIT",
            f"DPK-{weave_id}-WRITEBACK",
        ]
        slice_ids = [f"DPS-{weave_id}-01", f"DPS-{weave_id}-02", f"DPS-{weave_id}-03"]
        relation_stack = unique(
            [source_record.get("relation_law", ""), target_record.get("relation_law", "")]
        )
        appendix_stack = unique(
            list(source_record.get("appendix_support", []))
            + list(target_record.get("appendix_support", []))
            + ["AppQ"]
        )

        family = DeepPairwiseFamilyContractRecord(
            pairwise_family_id=family_id,
            weave_id=weave_id,
            source_pair_id=spec["source_pair_id"],
            target_pair_id=spec["target_pair_id"],
            source_pair_surface=source_surface,
            target_pair_surface=target_surface,
            relation_stack=relation_stack,
            metro_level="Level 3",
            appendix_stack=appendix_stack,
            route_surface=relative_string(route_path),
            replay_surface=relative_string(replay_path),
            runtime_surface=relative_string(runtime_path),
            restart_seed=(
                f"Replay `{spec['source_pair_id']}` through `GCW -> GCZ` and close in "
                f"`{spec['target_pair_id']}` before promoting the next neglected sibling pair."
            ),
            authority_rank="authoritative",
            packet_ids=packet_ids,
            slice_ids=slice_ids,
            primary_writeback_target=target_surface,
            witness_basis=unique(
                [
                    source_surface,
                    target_surface,
                    relative_string(LEVEL3_MAP_PATH),
                    relative_string(APPENDIX_Q_PATH),
                    relative_string(family_doc_path),
                    relative_string(route_path),
                    relative_string(replay_path),
                    relative_string(verify_path),
                ]
            ),
            note="Dedicated deep pairwise family promoted from the bridge-densification backlog.",
        )
        families.append(family)

        family_packets: List[SynapticHandoffPacketRecord] = []
        family_slices: List[DeepPairwiseSliceContractRecord] = []
        for index, (suffix, phase, note) in enumerate(SLICE_PHASES):
            packet_id = packet_ids[index]
            slice_id = slice_ids[index]
            slice_doc_path = FAMILY_EDGE_ROOT / f"{slice_id.replace('-', '_')}.md"
            if suffix == "01":
                source_anchor_ref = f"{spec['source_pair_id']}::{source_surface}"
                target_anchor_ref = f"GCW::{relative_string(LEVEL3_MAP_PATH)}"
                writeback_target = source_surface
                source_agent = "source-pair-replay"
                target_agent = "level3-transit"
                trigger = f"Replay `{spec['source_pair_id']}` into the Level 3 transit spine."
            elif suffix == "02":
                source_anchor_ref = f"GCW::{relative_string(LEVEL3_MAP_PATH)}"
                target_anchor_ref = f"GCZ::{relative_string(LEVEL3_MAP_PATH)}"
                writeback_target = relative_string(route_path)
                source_agent = "level3-transit"
                target_agent = "target-pair-receive"
                trigger = f"Carry `{weave_id}` across the fixed `GCW -> GCZ` corridor."
            else:
                source_anchor_ref = f"GCZ::{relative_string(LEVEL3_MAP_PATH)}"
                target_anchor_ref = f"{spec['target_pair_id']}::{target_surface}"
                writeback_target = target_surface
                source_agent = "target-pair-receive"
                target_agent = "overseer-writeback"
                trigger = f"Write `{weave_id}` back into `{spec['target_pair_id']}` as the primary target."

            packet = SynapticHandoffPacketRecord(
                packet_id=packet_id,
                source_agent=source_agent,
                target_agent=target_agent,
                source_body_id=spec["source_pair_id"],
                target_body_id=spec["target_pair_id"],
                trigger=trigger,
                witness_basis=unique(
                    [
                        source_surface,
                        target_surface,
                        relative_string(LEVEL3_MAP_PATH),
                        relative_string(APPENDIX_Q_PATH),
                        relative_string(route_path),
                        relative_string(replay_path),
                    ]
                ),
                route=[spec["source_pair_id"], "GCW", "GCZ", spec["target_pair_id"]],
                expected_writeback=[target_surface, relative_string(verify_path)],
                proof_state="OK",
                phase=phase,
                replay_surface=relative_string(replay_path),
                verification_surface=relative_string(verify_path),
                weave_id=weave_id,
                source_pair_id=spec["source_pair_id"],
                target_pair_id=spec["target_pair_id"],
                metro_level="Level 3",
                appendix_stack=appendix_stack,
                note=note,
            )
            family_packets.append(packet)
            packets.append(packet)

            slice_record = DeepPairwiseSliceContractRecord(
                pairwise_family_id=family_id,
                slice_id=slice_id,
                phase=phase,
                source_anchor_ref=source_anchor_ref,
                target_anchor_ref=target_anchor_ref,
                packet_id=packet_id,
                writeback_target=writeback_target,
                truth_state="OK",
                witness_basis=unique(
                    [
                        source_surface,
                        target_surface,
                        relative_string(LEVEL3_MAP_PATH),
                        relative_string(APPENDIX_Q_PATH),
                        relative_string(route_path),
                    ]
                ),
                surface=relative_string(slice_doc_path),
                note=note,
            )
            family_slices.append(slice_record)
            slices.append(slice_record)

        write_text(
            family_doc_path,
            render_family_summary(
                family=family,
                source_record=source_record,
                target_record=target_record,
                packet_ids=packet_ids,
                slice_ids=slice_ids,
            ),
        )
        generated_paths.append(family_doc_path)

        for slice_record, packet in zip(family_slices, family_packets):
            slice_path = WORKSPACE_ROOT / slice_record.surface.replace("\\", "/")
            write_text(slice_path, render_slice_doc(family, slice_record, packet))
            generated_paths.append(slice_path)

        write_text(route_path, render_route(family, source_record, target_record, family_slices, family_packets))
        write_text(replay_path, render_replay(family, family_packets))
        generated_paths.extend([route_path, replay_path])

        source_pair_path = WORKSPACE_ROOT / source_surface.replace("\\", "/")
        target_pair_path = WORKSPACE_ROOT / target_surface.replace("\\", "/")
        source_block = pair_block(
            marker=f"DEEP_PAIRWISE_{weave_id}_SOURCE",
            heading="Deep Pairwise Backlink",
            lines=[
                f"- weave: `{weave_id}`",
                f"- family: `{family_id}`",
                "- role: `source-pair replay`",
                f"- route surface: `{relative_string(route_path)}`",
                f"- replay surface: `{relative_string(replay_path)}`",
                f"- primary writeback target: `{target_surface}`",
            ],
        )
        target_block = pair_block(
            marker=f"DEEP_PAIRWISE_{weave_id}_TARGET",
            heading="Deep Pairwise Writeback",
            lines=[
                f"- weave: `{weave_id}`",
                f"- family: `{family_id}`",
                "- role: `target-pair writeback`",
                f"- route surface: `{relative_string(route_path)}`",
                f"- verification surface: `{relative_string(verify_path)}`",
                f"- primary writeback target: `{target_surface}`",
                f"- appendix stack: `{', '.join(appendix_stack)}`",
            ],
        )
        upsert_marked_block(source_pair_path, f"DEEP_PAIRWISE_{weave_id}_SOURCE", source_block)
        upsert_marked_block(target_pair_path, f"DEEP_PAIRWISE_{weave_id}_TARGET", target_block)
        generated_paths.extend([source_pair_path, target_pair_path])

        family_checks = build_family_checks(
            family=family,
            slices=family_slices,
            packets=family_packets,
            source_pair_text=read_text(source_pair_path),
            target_pair_text=read_text(target_pair_path),
        )
        write_text(verify_path, render_verify(family, family_checks))
        write_text(runtime_path, render_family_receipt(family, family_packets, family_slices))
        generated_paths.extend([verify_path, runtime_path])

    families_payload = {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "docs_gate": docs_gate,
        "families": [record.to_dict() for record in families],
    }
    slices_payload = {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "contracts": [record.to_dict() for record in slices],
    }
    packets_payload = {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "packets": [record.to_dict() for record in packets],
    }

    outputs = {
        "families_json": relative_string(FAMILIES_JSON_PATH),
        "slices_json": relative_string(SLICES_JSON_PATH),
        "packets_json": relative_string(PACKETS_JSON_PATH),
        "dashboard_json": relative_string(DASHBOARD_JSON_PATH),
        "verification_json": relative_string(VERIFICATION_JSON_PATH),
        "manifest_md": relative_string(MANIFEST_MD_PATH),
        "ledger_md": relative_string(LEDGER_MD_PATH),
        "dashboard_md": relative_string(DASHBOARD_MD_PATH),
        "verification_md": relative_string(VERIFICATION_MD_PATH),
        "runtime_md": relative_string(RUNTIME_MD_PATH),
        "receipt_md": relative_string(RECEIPT_MD_PATH),
    }

    write_json(FAMILIES_JSON_PATH, families_payload)
    write_json(SLICES_JSON_PATH, slices_payload)
    write_json(PACKETS_JSON_PATH, packets_payload)
    write_json(FAMILIES_JSON_MIRROR, families_payload)
    write_json(SLICES_JSON_MIRROR, slices_payload)
    write_json(PACKETS_JSON_MIRROR, packets_payload)
    generated_paths.extend(
        [
            FAMILIES_JSON_PATH,
            SLICES_JSON_PATH,
            PACKETS_JSON_PATH,
            FAMILIES_JSON_MIRROR,
            SLICES_JSON_MIRROR,
            PACKETS_JSON_MIRROR,
        ]
    )

    write_text(MANIFEST_MD_PATH, render_manifest(outputs, docs_gate))
    write_text(LEDGER_MD_PATH, render_ledger(families, pair_records))
    write_text(
        WHOLE_CRYSTAL_LEDGER_PATH,
        render_whole_crystal_bridge_ledger(direct_bridge_families, backlog_entries),
    )
    generated_paths.extend([MANIFEST_MD_PATH, LEDGER_MD_PATH, WHOLE_CRYSTAL_LEDGER_PATH])

    provisional_verification = {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "truth": "NEAR",
        "docs_gate": docs_gate,
        "checks": {},
        "runtime_lanes": {
            "aqm_runtime_lane": load_runtime_truth(AQM_RUNTIME_LANE_PATH),
            "atlasforge_runtime_lane": load_runtime_truth(ATLASFORGE_RUNTIME_LANE_PATH),
            "runtime_waist": load_runtime_truth(RUNTIME_WAIST_PATH),
        },
        "next_restart_seed": "source-pair replay -> GCW-GCZ transit -> target-pair writeback -> verify -> seed-next-pair",
        "unresolved": ["Deep pairwise atlas refresh pending."],
    }
    provisional_dashboard = build_dashboard(families, slices, packets, provisional_verification)
    write_json(DASHBOARD_JSON_PATH, provisional_dashboard)
    write_json(VERIFICATION_JSON_PATH, provisional_verification)
    write_json(DASHBOARD_JSON_MIRROR, provisional_dashboard)
    write_json(VERIFICATION_JSON_MIRROR, provisional_verification)
    write_text(DASHBOARD_MD_PATH, render_dashboard(provisional_dashboard))
    write_text(VERIFICATION_MD_PATH, render_verification(provisional_verification))
    write_text(RUNTIME_MD_PATH, render_runtime(outputs, provisional_verification))
    write_text(RECEIPT_MD_PATH, render_wave_receipt(families, provisional_verification))
    generated_paths.extend(
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

    refresh_corpus_atlas(generated_paths)

    verification = build_verification(
        families=families,
        slices=slices,
        packets=packets,
        docs_gate=docs_gate,
        generated_paths=generated_paths,
    )
    dashboard = build_dashboard(families, slices, packets, verification)

    write_json(DASHBOARD_JSON_PATH, dashboard)
    write_json(VERIFICATION_JSON_PATH, verification)
    write_json(DASHBOARD_JSON_MIRROR, dashboard)
    write_json(VERIFICATION_JSON_MIRROR, verification)
    write_text(DASHBOARD_MD_PATH, render_dashboard(dashboard))
    write_text(VERIFICATION_MD_PATH, render_verification(verification))
    write_text(RUNTIME_MD_PATH, render_runtime(outputs, verification))
    write_text(RECEIPT_MD_PATH, render_wave_receipt(families, verification))

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

    print(f"Wrote deep pairwise weave artifacts under {SELF_ACTUALIZE_ROOT}")
    print(f"Docs gate: {docs_gate['status']}")
    print(f"Truth: {verification['truth']}")
    return 0 if verification["truth"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
