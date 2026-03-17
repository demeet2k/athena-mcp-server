from __future__ import annotations

import re
from typing import Any

from self_actualize.runtime.hemisphere_brain_support import (
    MANIFEST_PATH,
    RECORD_REGISTRY_PATH,
    SYNTHESIS_EVIDENCE_REGISTRY_PATH,
    SYNTHESIS_FACET_REGISTRY_PATH,
    SYNTHESIS_MANIFEST_PATH,
    SYNTHESIS_SEED_REGISTRY_PATH,
    load_json,
    slugify,
    utc_now,
)
from self_actualize.runtime.hemisphere_route_composer_support import (
    ROUTE_STAGE_ORDER,
    compose_shared_spine,
    ensure_composer_runtime,
    facet as composer_facet_query,
    load_route_composer_registries,
    record as composer_record_query,
    search as composer_search_query,
)


SYNTHESIS_STARTER_CAP = 24


def collapse_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def short_excerpt(value: str, limit: int = 160) -> str:
    collapsed = collapse_whitespace(value)
    if not collapsed:
        return ""
    if len(collapsed) <= limit:
        return collapsed
    return collapsed[: limit - 1].rstrip() + "..."


def stage_label(stage_name: str) -> str:
    return stage_name.replace("_", " ").title()


def support_id(record_id: str, hemisphere: str, stage: str, evidence_kind: str) -> str:
    return f"SUP-{slugify(f'{record_id}-{hemisphere}-{stage}-{evidence_kind}')}"


def build_synthesis_evidence_registry(
    *,
    record_registry: dict[str, Any],
    atlas_records: list[dict[str, Any]],
    docs_gate_status: str,
) -> dict[str, Any]:
    atlas_lookup = {
        record["record_id"]: record
        for record in atlas_records
    }
    records: dict[str, dict[str, Any]] = {}
    for record in record_registry.get("records", []):
        atlas_record = atlas_lookup.get(record["record_id"], {})
        records[record["record_id"]] = {
            "record_id": record["record_id"],
            "title": record.get("title", ""),
            "relative_path": record.get("relative_path", ""),
            "heading_candidates": list(atlas_record.get("heading_candidates") or []),
            "excerpt": atlas_record.get("excerpt", ""),
            "family": record.get("family", ""),
            "basis_anchor_ids": list(record.get("basis_anchor_ids") or []),
            "appendix_support": list(record.get("appendix_support") or []),
            "text_extractable": bool(record.get("text_extractable")),
            "top_level": record.get("top_level", ""),
        }
    return {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "record_count": len(records),
        "records": dict(sorted(records.items())),
    }


def load_synthesis_registries() -> dict[str, Any]:
    if not SYNTHESIS_EVIDENCE_REGISTRY_PATH.exists():
        raise FileNotFoundError(
            "Missing synthesis evidence registry. Run "
            "`python -m self_actualize.runtime.derive_myth_math_hemisphere_brain` first."
        )
    registries = load_route_composer_registries()
    registries["record_registry"] = load_json(RECORD_REGISTRY_PATH)
    registries["manifest"] = load_json(MANIFEST_PATH)
    registries["synthesis_evidence_registry"] = load_json(SYNTHESIS_EVIDENCE_REGISTRY_PATH)
    if SYNTHESIS_SEED_REGISTRY_PATH.exists():
        registries["synthesis_seed_registry"] = load_json(SYNTHESIS_SEED_REGISTRY_PATH)
    if SYNTHESIS_FACET_REGISTRY_PATH.exists():
        registries["synthesis_facet_registry"] = load_json(SYNTHESIS_FACET_REGISTRY_PATH)
    if SYNTHESIS_MANIFEST_PATH.exists():
        registries["synthesis_manifest"] = load_json(SYNTHESIS_MANIFEST_PATH)
    return registries


def ensure_synthesis_runtime(registries: dict[str, Any]) -> dict[str, Any]:
    runtime = registries.get("_synthesis_runtime")
    if runtime is not None:
        return runtime
    composer_runtime = ensure_composer_runtime(registries)
    runtime = {
        "composer": composer_runtime,
        "evidence_lookup": registries["synthesis_evidence_registry"].get("records", {}),
        "docs_gate_status": registries["manifest"].get("docs_gate_status", "UNKNOWN"),
    }
    registries["_synthesis_runtime"] = runtime
    return runtime


def ensure_ledger_row(
    ledger: dict[str, dict[str, Any]],
    row: dict[str, Any],
) -> str:
    row_id = row["support_id"]
    if row_id not in ledger:
        ledger[row_id] = row
    return row_id


def title_row(
    evidence_record: dict[str, Any],
    hemisphere: str,
    stage: str,
) -> dict[str, Any]:
    return {
        "support_id": support_id(evidence_record["record_id"], hemisphere, stage, "title"),
        "record_id": evidence_record["record_id"],
        "relative_path": evidence_record["relative_path"],
        "hemisphere": hemisphere,
        "stage": stage,
        "evidence_kind": "title",
        "source_surface": "cached_text",
        "text": evidence_record.get("title", ""),
    }


def excerpt_row(
    evidence_record: dict[str, Any],
    hemisphere: str,
    stage: str,
) -> dict[str, Any]:
    return {
        "support_id": support_id(evidence_record["record_id"], hemisphere, stage, "excerpt"),
        "record_id": evidence_record["record_id"],
        "relative_path": evidence_record["relative_path"],
        "hemisphere": hemisphere,
        "stage": stage,
        "evidence_kind": "excerpt",
        "source_surface": "cached_text",
        "text": evidence_record.get("excerpt", ""),
    }


def heading_row(
    evidence_record: dict[str, Any],
    hemisphere: str,
    stage: str,
) -> dict[str, Any]:
    return {
        "support_id": support_id(evidence_record["record_id"], hemisphere, stage, "heading"),
        "record_id": evidence_record["record_id"],
        "relative_path": evidence_record["relative_path"],
        "hemisphere": hemisphere,
        "stage": stage,
        "evidence_kind": "heading",
        "source_surface": "cached_text",
        "text": " | ".join((evidence_record.get("heading_candidates") or [])[:3]),
    }


def route_state_row(
    record_id: str,
    relative_path: str,
    hemisphere: str,
    stage: str,
    route_packet: dict[str, Any],
) -> dict[str, Any]:
    return {
        "support_id": support_id(record_id, hemisphere, stage, "route_state"),
        "record_id": record_id,
        "relative_path": relative_path,
        "hemisphere": hemisphere,
        "stage": stage,
        "evidence_kind": "route_state",
        "source_surface": "route_bundle",
        "route_role": route_packet.get("route_role", ""),
        "route_mode": route_packet.get("route_mode", ""),
        "target_system": route_packet.get("target_system", ""),
        "dominant_lens_system": route_packet.get("dominant_lens_system", ""),
        "field_id": route_packet.get("field_id", ""),
        "zpoint_id": route_packet.get("zpoint_id", ""),
        "proof_state": route_packet.get("proof_state", ""),
        "preferred_space": route_packet.get("preferred_space", ""),
    }


def absence_row(
    record_id: str,
    relative_path: str,
    hemisphere: str,
    stage: str,
    reason: str,
) -> dict[str, Any]:
    return {
        "support_id": support_id(record_id, hemisphere, stage, "absence"),
        "record_id": record_id,
        "relative_path": relative_path,
        "hemisphere": hemisphere,
        "stage": stage,
        "evidence_kind": "absence",
        "source_surface": "route_bundle",
        "reason": reason,
    }


def spine_row(seed_record: dict[str, Any], shared_spine: dict[str, Any]) -> dict[str, Any]:
    return {
        "support_id": support_id(seed_record["record_id"], "BOTH", "shared_spine", "spine_state"),
        "record_id": seed_record["record_id"],
        "relative_path": seed_record.get("relative_path", ""),
        "hemisphere": "BOTH",
        "stage": "shared_spine",
        "evidence_kind": "spine_state",
        "source_surface": "route_bundle",
        "source_hub_id": shared_spine.get("source_hub_id", ""),
        "target_hub_id": shared_spine.get("target_hub_id", ""),
        "sequence": [item.get("hub_id", item.get("kind", "")) for item in shared_spine.get("sequence", [])],
    }


def bridge_row(seed_record: dict[str, Any], bridge_profile: dict[str, Any], proof_summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "support_id": support_id(seed_record["record_id"], "BOTH", "bridge", "bridge_state"),
        "record_id": seed_record["record_id"],
        "relative_path": seed_record.get("relative_path", ""),
        "hemisphere": "BOTH",
        "stage": "bridge",
        "evidence_kind": "bridge_state",
        "source_surface": "route_bundle",
        "mode": bridge_profile.get("mode", ""),
        "commissure_edge_ids": bridge_profile.get("commissure_edge_ids", []),
        "direct_edge_ids": bridge_profile.get("direct_edge_ids", []),
        "route_proof_states": proof_summary.get("route_proof_states", {}),
    }


def appendix_row(seed_record: dict[str, Any], appendix_ids: list[str]) -> dict[str, Any]:
    return {
        "support_id": support_id(seed_record["record_id"], "BOTH", "appendix_support", "appendix_state"),
        "record_id": seed_record["record_id"],
        "relative_path": seed_record.get("relative_path", ""),
        "hemisphere": "BOTH",
        "stage": "appendix_support",
        "evidence_kind": "appendix_state",
        "source_surface": "cached_text",
        "appendix_support": appendix_ids,
    }


def record_support_ids(
    runtime: dict[str, Any],
    ledger: dict[str, dict[str, Any]],
    stage_payload: dict[str, Any],
) -> list[str]:
    record_summary = stage_payload["record"]
    evidence_record = runtime["evidence_lookup"][record_summary["record_id"]]
    hemisphere = stage_payload["hemisphere"]
    stage = stage_payload["stage"]
    ids = [
        ensure_ledger_row(ledger, title_row(evidence_record, hemisphere, stage)),
    ]
    if evidence_record.get("excerpt"):
        ids.append(ensure_ledger_row(ledger, excerpt_row(evidence_record, hemisphere, stage)))
    elif evidence_record.get("heading_candidates"):
        ids.append(ensure_ledger_row(ledger, heading_row(evidence_record, hemisphere, stage)))
    ids.append(
        ensure_ledger_row(
            ledger,
            route_state_row(
                evidence_record["record_id"],
                evidence_record["relative_path"],
                hemisphere,
                stage,
                stage_payload["selected_route"],
            ),
        )
    )
    return ids


def stage_bullet_text(runtime: dict[str, Any], stage_payload: dict[str, Any]) -> str:
    stage = stage_payload["stage"]
    hemisphere = stage_payload["hemisphere"]
    if stage_payload["kind"] == "record_stop":
        record_summary = stage_payload["record"]
        evidence_record = runtime["evidence_lookup"][record_summary["record_id"]]
        route_packet = stage_payload["selected_route"]
        excerpt = short_excerpt(evidence_record.get("excerpt", ""))
        header = route_packet.get("tesseract_header", "")
        primary_hubs = route_packet.get("primary_hubs_text", "")
        tunnel_text = route_packet.get("tunnel_text", "")
        truth_text = route_packet.get("truth_state_text", "")
        hcrl = route_packet.get("hcrl_text", {})
        hcrl_text = (
            f" Square: {hcrl.get('Square', '')}"
            f" Flower: {hcrl.get('Flower', '')}"
            f" Cloud: {hcrl.get('Cloud', '')}"
            f" Fractal: {hcrl.get('Fractal', '')}"
            if hcrl
            else ""
        )
        if excerpt:
            return (
                f"{header} {stage_label(stage)} in {hemisphere} centers on \"{evidence_record.get('title', '')}\"; "
                f"cached evidence frames it as {excerpt}, and the active route resolves toward "
                f"{route_packet.get('target_system', '')} via {route_packet.get('dominant_lens_system', '')} "
                f"with {route_packet.get('proof_state', '')} proof. {primary_hubs} {tunnel_text} {truth_text}.{hcrl_text}"
            )
        return (
            f"{header} {stage_label(stage)} in {hemisphere} centers on \"{evidence_record.get('title', '')}\" "
            f"and routes toward {route_packet.get('target_system', '')} via "
            f"{route_packet.get('dominant_lens_system', '')} with {route_packet.get('proof_state', '')} proof. "
            f"{primary_hubs} {tunnel_text} {truth_text}.{hcrl_text}"
        )
    if stage_payload["kind"] == "empty":
        return (
            f"{stage_label(stage)} in {hemisphere} remains empty because "
            f"{stage_payload.get('reason', 'no_lawful_candidate').replace('_', ' ')}."
        )
    if stage_payload["kind"] == "hub_stop":
        return (
            f"{hemisphere} consolidates at {stage_payload.get('hub_id', '')} through "
            f"{stage_payload.get('grand_central_exchange', '')}, carrying "
            f"{stage_payload.get('proof_state', '')} proof while holding "
            f"{stage_payload.get('target_system', '')} as the active system focus."
        )
    return (
        f"{hemisphere} exits through {' -> '.join(stage_payload.get('return_path', []))}, using "
        f"{stage_payload.get('pt2_shortcut_id', '')} and {stage_payload.get('knowledge_fabric_shortcut_id', '')} "
        f"toward {stage_payload.get('preferred_space', '')}."
    )


def synthesize_itinerary_section(
    runtime: dict[str, Any],
    composer_payload: dict[str, Any],
    hemisphere: str,
    ledger: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, list[str]]]:
    itinerary = composer_payload["math_itinerary"] if hemisphere == "MATH" else composer_payload["myth_itinerary"]
    seed_record = runtime["composer"]["navigator"]["record_map"][composer_payload["seed_record"]["record_id"]]
    bullets: list[dict[str, Any]] = []
    stage_supports: dict[str, list[str]] = {}

    for stage_payload in itinerary.get("stages", []):
        stage = stage_payload.get("stage", "")
        if stage_payload.get("kind") == "record_stop":
            support_ids = record_support_ids(runtime, ledger, stage_payload)
        elif stage_payload.get("kind") == "empty":
            support_ids = [
                ensure_ledger_row(
                    ledger,
                    absence_row(
                        seed_record["record_id"],
                        seed_record.get("relative_path", ""),
                        hemisphere,
                        stage,
                        stage_payload.get("reason", ""),
                    ),
                )
            ]
        elif stage_payload.get("kind") == "hub_stop":
            support_ids = [
                ensure_ledger_row(
                    ledger,
                    route_state_row(
                        seed_record["record_id"],
                        seed_record.get("relative_path", ""),
                        hemisphere,
                        stage,
                        {
                            "route_role": stage_payload.get("edge", {}).get("route_role", ""),
                            "route_mode": stage_payload.get("edge", {}).get("route_mode", ""),
                            "target_system": stage_payload.get("target_system", ""),
                            "dominant_lens_system": "",
                            "field_id": "",
                            "zpoint_id": "",
                            "proof_state": stage_payload.get("proof_state", ""),
                            "preferred_space": "",
                        },
                    ),
                )
            ]
        else:
            support_ids = [
                ensure_ledger_row(
                    ledger,
                    route_state_row(
                        seed_record["record_id"],
                        seed_record.get("relative_path", ""),
                        hemisphere,
                        stage,
                        {
                            "route_role": "exit",
                            "route_mode": "return_path",
                            "target_system": "",
                            "dominant_lens_system": "",
                            "field_id": "",
                            "zpoint_id": "",
                            "proof_state": stage_payload.get("proof_state", ""),
                            "preferred_space": stage_payload.get("preferred_space", ""),
                        },
                    ),
                )
            ]
        stage_supports[stage] = support_ids
        bullets.append(
            {
                "text": stage_bullet_text(runtime, stage_payload),
                "support_ids": support_ids,
            }
        )

    return {
        "section": hemisphere,
        "bullets": bullets,
    }, stage_supports


def first_route_support(stage_supports: dict[str, list[str]], *stages: str) -> list[str]:
    for stage in stages:
        support_ids = stage_supports.get(stage, [])
        if support_ids:
            return support_ids
    return []


def itinerary_target_systems(itinerary: dict[str, Any]) -> list[str]:
    systems: list[str] = []
    for stage in itinerary.get("stages", []):
        if stage.get("kind") != "record_stop":
            continue
        target_system = stage.get("selected_route", {}).get("target_system", "")
        if target_system and target_system not in systems:
            systems.append(target_system)
    return systems


def synthesize_unified_section(
    runtime: dict[str, Any],
    composer_payload: dict[str, Any],
    ledger: dict[str, dict[str, Any]],
    math_supports: dict[str, list[str]],
    myth_supports: dict[str, list[str]],
) -> dict[str, Any]:
    seed_record = runtime["composer"]["navigator"]["record_map"][composer_payload["seed_record"]["record_id"]]
    shared_spine = composer_payload.get("shared_spine", {})
    spine_support_id = ensure_ledger_row(
        ledger,
        spine_row(seed_record, shared_spine),
    )
    math_systems = itinerary_target_systems(composer_payload["math_itinerary"])
    myth_systems = itinerary_target_systems(composer_payload["myth_itinerary"])
    common_systems = [system for system in math_systems if system in myth_systems]
    overlap_support_ids = (
        first_route_support(math_supports, "seed", "system_lift")
        + first_route_support(myth_supports, "seed", "system_lift")
    )
    if common_systems:
        overlap_text = (
            f"Both hemispheres keep converging on {', '.join(common_systems[:3])}, so the unified layer is "
            "system-coherent rather than split."
        )
    else:
        overlap_text = (
            f"The hemispheres diverge after the shared spine: MATH favors {math_systems[0] if math_systems else 'no_system'}, "
            f"while MYTH favors {myth_systems[0] if myth_systems else 'no_system'}."
        )
    return {
        "section": "Unified",
        "bullets": [
            {
                "text": (
                    f"The bilateral path stays synchronized from the seed through "
                    f"{shared_spine.get('source_hub_id', '')} -> GC0-UNIFIED-CORPUS -> "
                    f"{shared_spine.get('target_hub_id', '')}."
                ),
                "support_ids": [spine_support_id],
            },
            {
                "text": overlap_text,
                "support_ids": overlap_support_ids or [spine_support_id],
            },
        ],
    }


def synthesize_bridge_section(
    seed_record: dict[str, Any],
    composer_payload: dict[str, Any],
    ledger: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    bridge_profile = composer_payload.get("bridge_profile", {})
    proof_summary = composer_payload.get("proof_summary", {})
    bridge_support_id = ensure_ledger_row(
        ledger,
        bridge_row(seed_record, bridge_profile, proof_summary),
    )
    if bridge_profile.get("mode") == "commissure_active":
        mode_text = "The bridge is active through explicit commissure edges, so bilateral transfer is direct rather than hub-only."
    else:
        mode_text = "The cross-hemisphere move is routed as hub transfer through GC0 rather than an explicit commissure edge."
    proof_states = proof_summary.get("route_proof_states", {})
    proof_text = (
        f"MATH proof sits at {proof_states.get('MATH', '')} while MYTH proof sits at "
        f"{proof_states.get('MYTH', '')}, which sets the bridge's confidence profile."
    )
    return {
        "section": "Bridge",
        "bullets": [
            {
                "text": mode_text,
                "support_ids": [bridge_support_id],
            },
            {
                "text": proof_text,
                "support_ids": [bridge_support_id],
            },
        ],
    }


def synthesize_appendix_section(
    seed_record: dict[str, Any],
    ledger: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    appendix_ids = list(seed_record.get("appendix_support") or [])
    appendix_support_id = ensure_ledger_row(
        ledger,
        appendix_row(seed_record, appendix_ids),
    )
    if appendix_ids:
        text = (
            f"Appendix support stays attached through {', '.join(appendix_ids)}, giving the route its replay and support geometry."
        )
    else:
        text = "No appendix supports are attached to this seed."
    return {
        "appendix_ids": appendix_ids,
        "bullets": [
            {
                "text": text,
                "support_ids": [appendix_support_id],
            }
        ],
    }


def synthesize_from_composer_payload(
    composer_payload: dict[str, Any],
    registries: dict[str, Any],
) -> dict[str, Any]:
    runtime = ensure_synthesis_runtime(registries)
    seed_summary = composer_payload.get("seed_record")
    if not seed_summary or not seed_summary.get("record_id"):
        return {
            "query": composer_payload.get("query", {}),
            "mode": composer_payload.get("mode", ""),
            "seed_record": None,
            "section_order": ["MATH", "MYTH", "Unified", "Bridge", "Appendix Support"],
            "math_synthesis": {"section": "MATH", "bullets": []},
            "myth_synthesis": {"section": "MYTH", "bullets": []},
            "unified_synthesis": {"section": "Unified", "bullets": []},
            "bridge_interpretation": {"section": "Bridge", "bullets": []},
            "evidence_ledger": {},
            "appendix_support": {"appendix_ids": [], "bullets": []},
            "docs_gate_status": composer_payload.get("docs_gate_status", runtime["docs_gate_status"]),
        }

    seed_record = runtime["composer"]["navigator"]["record_map"][seed_summary["record_id"]]
    evidence_ledger: dict[str, dict[str, Any]] = {}
    math_synthesis, math_supports = synthesize_itinerary_section(runtime, composer_payload, "MATH", evidence_ledger)
    myth_synthesis, myth_supports = synthesize_itinerary_section(runtime, composer_payload, "MYTH", evidence_ledger)
    unified_synthesis = synthesize_unified_section(runtime, composer_payload, evidence_ledger, math_supports, myth_supports)
    bridge_interpretation = synthesize_bridge_section(seed_record, composer_payload, evidence_ledger)
    appendix_support = synthesize_appendix_section(seed_record, evidence_ledger)
    payload = {
        "query": composer_payload.get("query", {}),
        "mode": composer_payload.get("mode", ""),
        "seed_record": composer_payload.get("seed_record"),
        "section_order": ["MATH", "MYTH", "Unified", "Bridge", "Appendix Support"],
        "math_synthesis": math_synthesis,
        "myth_synthesis": myth_synthesis,
        "unified_synthesis": unified_synthesis,
        "bridge_interpretation": bridge_interpretation,
        "evidence_ledger": dict(sorted(evidence_ledger.items())),
        "appendix_support": appendix_support,
        "docs_gate_status": composer_payload.get("docs_gate_status", runtime["docs_gate_status"]),
    }
    if composer_payload.get("alternative_seeds"):
        payload["alternative_seeds"] = composer_payload["alternative_seeds"][:3]
    return payload


def record(
    registries: dict[str, Any],
    *,
    record_id: str = "",
    path: str = "",
    title: str = "",
    query_text: str = "",
    expanded: bool = False,
) -> dict[str, Any]:
    composer_payload = composer_record_query(
        registries,
        record_id=record_id,
        path=path,
        title=title,
        query_text=query_text,
        expanded=expanded,
    )
    return synthesize_from_composer_payload(composer_payload, registries)


def search(
    query_text: str,
    registries: dict[str, Any],
    *,
    filters: dict[str, str] | None = None,
    expanded: bool = False,
) -> dict[str, Any]:
    composer_payload = composer_search_query(
        query_text,
        registries,
        filters=filters or {},
        expanded=expanded,
    )
    return synthesize_from_composer_payload(composer_payload, registries)


def facet(
    registries: dict[str, Any],
    *,
    facet_name: str,
    facet_value: str,
    expanded: bool = False,
) -> dict[str, Any]:
    composer_payload = composer_facet_query(
        registries,
        facet_name=facet_name,
        facet_value=facet_value,
        expanded=expanded,
    )
    return synthesize_from_composer_payload(composer_payload, registries)


def build_synthesis_seed_registry(
    *,
    composer_seed_registry: dict[str, Any],
    registries: dict[str, Any],
    docs_gate_status: str,
) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for group_name, entries in composer_seed_registry.get("groups", {}).items():
        group_entries: list[dict[str, Any]] = []
        for entry in entries[:SYNTHESIS_STARTER_CAP]:
            synthesis_bundle = synthesize_from_composer_payload(entry["route_bundle"], registries)
            group_entries.append(
                {
                    "rank": entry.get("rank"),
                    "seed_record": synthesis_bundle.get("seed_record"),
                    "synthesis_bundle": synthesis_bundle,
                }
            )
        groups[group_name] = group_entries
    return {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "starter_cap": SYNTHESIS_STARTER_CAP,
        "groups": groups,
        "counts": {
            group_name: len(entries)
            for group_name, entries in sorted(groups.items())
        },
    }


def build_synthesis_facet_registry(
    *,
    composer_facet_registry: dict[str, Any],
    registries: dict[str, Any],
    docs_gate_status: str,
) -> dict[str, Any]:
    facets: dict[str, dict[str, Any]] = {}
    for facet_name, values in composer_facet_registry.get("facets", {}).items():
        facets[facet_name] = {}
        for facet_value, entry in values.items():
            synthesis_bundle = synthesize_from_composer_payload(entry["route_bundle"], registries)
            facets[facet_name][facet_value] = {
                "seed_record": synthesis_bundle.get("seed_record"),
                "synthesis_bundle": synthesis_bundle,
            }
    return {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "facets": facets,
        "facet_counts": {
            facet_name: len(values)
            for facet_name, values in sorted(facets.items())
        },
    }


def build_synthesis_manifest(
    *,
    evidence_registry: dict[str, Any],
    seed_registry: dict[str, Any],
    facet_registry: dict[str, Any],
    docs_gate_status: str,
) -> dict[str, Any]:
    return {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "section_order": ["MATH", "MYTH", "Unified", "Bridge", "Appendix Support"],
        "evidence_mode": "strict_path_grounding",
        "counts": {
            "evidence_records": evidence_registry.get("record_count", 0),
            "seed_groups": len(seed_registry.get("groups", {})),
            "math_starters": seed_registry.get("counts", {}).get("math", 0),
            "myth_starters": seed_registry.get("counts", {}).get("myth", 0),
            "bridge_starters": seed_registry.get("counts", {}).get("bridge", 0),
            "facet_starters": sum(facet_registry.get("facet_counts", {}).values()),
        },
        "facet_coverage": facet_registry.get("facet_counts", {}),
        "commands": [
            "python -m self_actualize.runtime.synthesize_myth_math_hemisphere_routes record --record-id <record_id>",
            "python -m self_actualize.runtime.synthesize_myth_math_hemisphere_routes search --query <text> --system <system>",
            "python -m self_actualize.runtime.synthesize_myth_math_hemisphere_routes facet --family <family>",
        ],
    }


def build_synthesis_payloads(
    *,
    record_registry: dict[str, Any],
    atlas_records: list[dict[str, Any]],
    composer_seed_registry: dict[str, Any],
    composer_facet_registry: dict[str, Any],
    registries: dict[str, Any],
    docs_gate_status: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    evidence_registry = build_synthesis_evidence_registry(
        record_registry=record_registry,
        atlas_records=atlas_records,
        docs_gate_status=docs_gate_status,
    )
    build_registries = dict(registries)
    build_registries["synthesis_evidence_registry"] = evidence_registry
    seed_registry = build_synthesis_seed_registry(
        composer_seed_registry=composer_seed_registry,
        registries=build_registries,
        docs_gate_status=docs_gate_status,
    )
    facet_registry = build_synthesis_facet_registry(
        composer_facet_registry=composer_facet_registry,
        registries=build_registries,
        docs_gate_status=docs_gate_status,
    )
    synthesis_manifest = build_synthesis_manifest(
        evidence_registry=evidence_registry,
        seed_registry=seed_registry,
        facet_registry=facet_registry,
        docs_gate_status=docs_gate_status,
    )
    return evidence_registry, seed_registry, facet_registry, synthesis_manifest
