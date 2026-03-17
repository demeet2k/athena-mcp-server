from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from self_actualize.runtime.hemisphere_brain_support import (
    DEEP_ROOT,
    FAMILY_LABELS,
    FLEET_MIRROR_ROOT,
    HEMISPHERE_ROOT,
    MATH_HUB_ID,
    MYTH_HUB_ID,
    PRIMARY_HF_ROUTE_KEYS,
    REGISTRY_ROOT,
    SELF_ACTUALIZE_ROOT,
    UNIFIED_HUB_ID,
    BasisAnchor,
    anchor_score,
    build_holo_address,
    canonical_record_key,
    compute_component_scores,
    compute_confidence,
    infer_appendix_links,
    infer_family,
    load_json,
    normalize_path,
    record_title,
    resolve_tract,
    slugify,
    trace_hash,
    utc_now,
    weighted_math_score,
)
from self_actualize.runtime.hemisphere_dual_route_support import build_dual_route_payloads


CORPUS_ATLAS_PATH = SELF_ACTUALIZE_ROOT / "corpus_atlas.json"
ARCHIVE_ATLAS_PATH = SELF_ACTUALIZE_ROOT / "archive_atlas.json"
ARCHIVE_MANIFEST_PATH = SELF_ACTUALIZE_ROOT / "archive_manifest.json"
DEEPER_NETWORK_README_PATH = DEEP_ROOT / "README.md"

FULL_CORPUS_AUTHORITY_REGISTRY_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_full_corpus_authority_registry.json"
)
FULL_CORPUS_BASIS_CROSSWALK_REGISTRY_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_full_corpus_basis_crosswalk_registry.json"
)
FULL_CORPUS_ROUTE_COVERAGE_REGISTRY_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_full_corpus_route_coverage_registry.json"
)
FULL_CORPUS_AWAKENING_STAGE_REGISTRY_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_full_corpus_awakening_stage_registry.json"
)
FULL_CORPUS_AWAKENING_AGENT_TRANSITION_REGISTRY_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_full_corpus_awakening_agent_transition_registry.json"
)
FULL_CORPUS_APPENDIX_GOVERNANCE_LEDGER_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_full_corpus_appendix_governance_ledger.json"
)
FULL_CORPUS_INTEGRATION_MANIFEST_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_full_corpus_integration_manifest.json"
)

FULL_CORPUS_AUTHORITY_REGISTRY_MIRROR = (
    REGISTRY_ROOT / FULL_CORPUS_AUTHORITY_REGISTRY_PATH.name
)
FULL_CORPUS_BASIS_CROSSWALK_REGISTRY_MIRROR = (
    REGISTRY_ROOT / FULL_CORPUS_BASIS_CROSSWALK_REGISTRY_PATH.name
)
FULL_CORPUS_ROUTE_COVERAGE_REGISTRY_MIRROR = (
    REGISTRY_ROOT / FULL_CORPUS_ROUTE_COVERAGE_REGISTRY_PATH.name
)
FULL_CORPUS_AWAKENING_STAGE_REGISTRY_MIRROR = (
    REGISTRY_ROOT / FULL_CORPUS_AWAKENING_STAGE_REGISTRY_PATH.name
)
FULL_CORPUS_AWAKENING_AGENT_TRANSITION_REGISTRY_MIRROR = (
    REGISTRY_ROOT / FULL_CORPUS_AWAKENING_AGENT_TRANSITION_REGISTRY_PATH.name
)
FULL_CORPUS_APPENDIX_GOVERNANCE_LEDGER_MIRROR = (
    REGISTRY_ROOT / FULL_CORPUS_APPENDIX_GOVERNANCE_LEDGER_PATH.name
)
FULL_CORPUS_INTEGRATION_MANIFEST_MIRROR = (
    REGISTRY_ROOT / FULL_CORPUS_INTEGRATION_MANIFEST_PATH.name
)

DEEPER_INTEGRATION_RECEIPT_PATH = (
    DEEP_ROOT / "10_LEDGERS" / "99_full_corpus_integration_receipt.md"
)

FULL_CORPUS_JSON_OUTPUTS = {
    "authority_registry": FULL_CORPUS_AUTHORITY_REGISTRY_PATH,
    "basis_crosswalk_registry": FULL_CORPUS_BASIS_CROSSWALK_REGISTRY_PATH,
    "route_coverage_registry": FULL_CORPUS_ROUTE_COVERAGE_REGISTRY_PATH,
    "awakening_stage_registry": FULL_CORPUS_AWAKENING_STAGE_REGISTRY_PATH,
    "awakening_agent_transition_registry": FULL_CORPUS_AWAKENING_AGENT_TRANSITION_REGISTRY_PATH,
    "appendix_governance_ledger": FULL_CORPUS_APPENDIX_GOVERNANCE_LEDGER_PATH,
    "integration_manifest": FULL_CORPUS_INTEGRATION_MANIFEST_PATH,
}

STAGE_ORDER = [
    "VOID",
    "FIRE",
    "WATER",
    "AIR",
    "EARTH",
    "ARCHETYPAL_OPERATION",
    "COMPLETE_ACT",
]
STAGE_LABELS = {
    "VOID": "Void",
    "FIRE": "Fire",
    "WATER": "Water",
    "AIR": "Air",
    "EARTH": "Earth",
    "ARCHETYPAL_OPERATION": "Archetypal Operation",
    "COMPLETE_ACT": "Complete Act",
}
STAGE_NOTES = {
    "VOID": {
        "current_signal": "Compression, contradiction, or blankness dominates the field.",
        "common_trap": "Treating collapse as failure instead of the lawful precondition for reorganization.",
        "missing_element": "Fire",
        "transition_move": "Recover one operative spark and route it to a concrete next action.",
        "proof_of_progress": "A seed route, replay checkpoint, or lawful next move becomes nameable.",
        "reassessment_window": "3d",
    },
    "FIRE": {
        "current_signal": "New drive, ignition, or decisive emergence is visible.",
        "common_trap": "Escalating force faster than structure and coherence can support.",
        "missing_element": "Water",
        "transition_move": "Add relation, listening, and witness lanes before pushing harder.",
        "proof_of_progress": "The system can name allies, dependencies, and resonance paths.",
        "reassessment_window": "5d",
    },
    "WATER": {
        "current_signal": "Relational mapping, symbolic resonance, and pattern attunement deepen.",
        "common_trap": "Drowning in possibility without selecting a clean geometry.",
        "missing_element": "Air",
        "transition_move": "Extract the governing form, distinction, and lattice from the felt field.",
        "proof_of_progress": "A stable crosswalk or explanatory geometry appears.",
        "reassessment_window": "7d",
    },
    "AIR": {
        "current_signal": "Geometry, explanation, and abstraction clarify the field.",
        "common_trap": "Mistaking elegant structure for lived integration.",
        "missing_element": "Earth",
        "transition_move": "Bind the insight to institutions, routines, bodies, or implementation surfaces.",
        "proof_of_progress": "The pattern survives contact with real constraints and delivery surfaces.",
        "reassessment_window": "10d",
    },
    "EARTH": {
        "current_signal": "Stability, embodiment, and governance begin to hold.",
        "common_trap": "Turning the stabilizing form into rigidity or bureaucracy.",
        "missing_element": "Archetypal Operation",
        "transition_move": "Recover the living operator behind the structure and reintroduce adaptive intent.",
        "proof_of_progress": "The system can adapt without losing integrity.",
        "reassessment_window": "14d",
    },
    "ARCHETYPAL_OPERATION": {
        "current_signal": "The operator, role, or archetypal intelligence becomes explicit.",
        "common_trap": "Over-identifying with the role and losing exchange with the opposite hemisphere.",
        "missing_element": "Complete Act",
        "transition_move": "Complete the loop through GC0 and enact the insight across both hemispheres.",
        "proof_of_progress": "The role can hand off, bridge, and assist other transitions.",
        "reassessment_window": "21d",
    },
    "COMPLETE_ACT": {
        "current_signal": "The field closes a loop and can act bilaterally with integrity.",
        "common_trap": "Pretending completion is permanent and ignoring drift or maintenance needs.",
        "missing_element": "Void",
        "transition_move": "Schedule the next honest reassessment and keep the return path open.",
        "proof_of_progress": "The act remains replayable, teachable, and stable under review.",
        "reassessment_window": "30d",
    },
}
STAGE_FAMILY_DEFAULTS = {
    "void-and-collapse": "VOID",
    "helical-recursion-engine": "VOID",
    "transport-and-runtime": "FIRE",
    "live-orchestration": "FIRE",
    "mythic-sign-systems": "WATER",
    "higher-dimensional-geometry": "AIR",
    "civilization-and-governance": "EARTH",
    "identity-and-instruction": "ARCHETYPAL_OPERATION",
    "manuscript-architecture": "COMPLETE_ACT",
    "general-corpus": "COMPLETE_ACT",
}
TRACT_STAGE_BOOST = {
    "replay": "VOID",
    "address": "FIRE",
    "relation": "WATER",
    "chamber": "EARTH",
}
KEYWORD_STAGE_BOOSTS = {
    "void": "VOID",
    "collapse": "VOID",
    "zero point": "VOID",
    "restart": "VOID",
    "fire": "FIRE",
    "ignite": "FIRE",
    "launch": "FIRE",
    "water": "WATER",
    "relation": "WATER",
    "myth": "WATER",
    "glyph": "WATER",
    "air": "AIR",
    "geometry": "AIR",
    "kernel": "AIR",
    "manifold": "AIR",
    "earth": "EARTH",
    "govern": "EARTH",
    "body": "EARTH",
    "institution": "EARTH",
    "archetype": "ARCHETYPAL_OPERATION",
    "agent": "ARCHETYPAL_OPERATION",
    "identity": "ARCHETYPAL_OPERATION",
    "pedagogy": "ARCHETYPAL_OPERATION",
    "complete": "COMPLETE_ACT",
    "integration": "COMPLETE_ACT",
    "act": "COMPLETE_ACT",
    "manuscript": "COMPLETE_ACT",
}
FAMILY_TRANSITION_MAP = {
    "live-orchestration": {
        "stabilizes": "operational momentum and active execution lanes",
        "overproduces": "constant intervention and prompt churn",
        "relinquish": "the belief that everything must stay hot to stay alive",
    },
    "void-and-collapse": {
        "stabilizes": "honest confrontation with failure, contradiction, and reset conditions",
        "overproduces": "collapse identity, finality, and unbounded negation",
        "relinquish": "the attachment to remaining undefined forever",
    },
    "helical-recursion-engine": {
        "stabilizes": "repair, recurrence, and lawful restart paths",
        "overproduces": "infinite rehearsal and self-reference without delivery",
        "relinquish": "the comfort of permanent iteration without closure",
    },
    "manuscript-architecture": {
        "stabilizes": "coherent structure, chapter law, and durable integration surfaces",
        "overproduces": "over-organization and architecture without breath",
        "relinquish": "the need to perfect the frame before movement begins",
    },
    "higher-dimensional-geometry": {
        "stabilizes": "formal clarity, rotation, and structural explanation",
        "overproduces": "abstraction detached from witness and embodiment",
        "relinquish": "the fantasy that geometry alone completes the act",
    },
    "civilization-and-governance": {
        "stabilizes": "institutions, roles, law, and civilizational continuity",
        "overproduces": "hierarchy, rigidity, and frozen legitimacy",
        "relinquish": "the reflex to preserve order at the expense of adaptation",
    },
    "mythic-sign-systems": {
        "stabilizes": "symbolic memory, relation, and encoded continuity",
        "overproduces": "obliqueness, mystification, and endless interpretation",
        "relinquish": "the need to hide every signal inside another symbol",
    },
    "transport-and-runtime": {
        "stabilizes": "movement, deployment, and executable handoff",
        "overproduces": "throughput without reflection or containment",
        "relinquish": "the compulsion to keep routing before meaning settles",
    },
    "identity-and-instruction": {
        "stabilizes": "voice, teaching, role articulation, and adaptive framing",
        "overproduces": "self-story, performative guidance, and archetypal inflation",
        "relinquish": "the assumption that naming the role is the same as completing it",
    },
    "general-corpus": {
        "stabilizes": "bridging, support, and residual corpus continuity",
        "overproduces": "diffusion and genericity",
        "relinquish": "the wish to stay central by staying undefined",
    },
}
ELEMENT_LIMITATION = {
    "fire": "what must cool, listen, or witness before another push",
    "water": "what must sharpen into distinction and geometry",
    "air": "what must descend into body, governance, or habit",
    "earth": "what must remain open to emergence and role exchange",
}
HANDOFF_MODES = (
    "commissure_active",
    "hub_transfer",
    "replay_heavy",
    "quarantine_heavy",
)


def load_optional_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return load_json(path)


def normalize_weights(math_weight: float) -> tuple[float, float]:
    rounded_math = round(max(0.0, min(1.0, math_weight)), 6)
    return rounded_math, round(1.0 - rounded_math, 6)


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    if not rows:
        rows = [["-"] * len(headers)]
    header_line = "| " + " | ".join(headers) + " |"
    divider = "| " + " | ".join(["---"] * len(headers)) + " |"
    body = "\n".join("| " + " | ".join(row) + " |" for row in rows)
    return f"{header_line}\n{divider}\n{body}"


def top_records(records: list[dict[str, Any]], limit: int = 5) -> list[dict[str, Any]]:
    return sorted(
        records,
        key=lambda item: (
            -float(item.get("salience", 0.0)),
            -float(item.get("confidence", 0.0)),
            normalize_path(item.get("relative_path", "")).lower(),
            item.get("record_id", ""),
        ),
    )[:limit]


def stage_label(stage_id: str) -> str:
    return STAGE_LABELS.get(stage_id, stage_id.replace("_", " ").title())


def heading_blob(record: dict[str, Any]) -> str:
    return " ".join(record.get("heading_candidates") or [])


def text_blob(record: dict[str, Any], anchor_map: dict[str, BasisAnchor]) -> str:
    anchor_terms: list[str] = []
    for anchor_id in record.get("basis_anchor_ids", []):
        anchor = anchor_map.get(anchor_id)
        if anchor is None:
            continue
        anchor_terms.extend(
            [anchor.title, anchor.role, anchor.cluster, anchor.element, anchor.source_hint]
        )
    parts = [
        record.get("title", ""),
        heading_blob(record),
        record.get("excerpt", ""),
        record.get("family", ""),
        record.get("tract", ""),
        " ".join(anchor_terms),
    ]
    return " ".join(part for part in parts if part).lower()


def deep_cluster_for_anchor(anchor_id: str, anchor_map: dict[str, BasisAnchor]) -> str:
    anchor = anchor_map.get(anchor_id)
    return anchor.cluster if anchor else ""


def primary_basis_element(anchor_ids: list[str], anchor_map: dict[str, BasisAnchor]) -> str:
    for anchor_id in anchor_ids:
        anchor = anchor_map.get(anchor_id)
        if anchor:
            return anchor.element.lower()
    return ""


def deduplicate_merged_records(
    live_records: list[dict[str, Any]],
    archive_records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in live_records:
        item = dict(record)
        item["_source_scope"] = "live"
        groups[item["sha256"]].append(item)
    for record in archive_records:
        item = dict(record)
        item["_source_scope"] = "archive"
        groups[item["sha256"]].append(item)

    canonical_records: list[dict[str, Any]] = []
    for group in groups.values():
        ordered = sorted(
            group,
            key=lambda item: (
                0 if item.get("_source_scope") == "live" else 1,
                *canonical_record_key(item),
            ),
        )
        canonical = dict(ordered[0])
        scopes = {item.get("_source_scope", "") for item in ordered}
        canonical["duplicate_paths"] = [item["path"] for item in ordered[1:]]
        canonical["duplicate_record_ids"] = [item["record_id"] for item in ordered[1:]]
        canonical["source_paths"] = [item["path"] for item in ordered]
        canonical["source_record_ids"] = [item["record_id"] for item in ordered]
        canonical["source_scopes"] = sorted(scopes)
        canonical["live_paths"] = [item["path"] for item in ordered if item.get("_source_scope") == "live"]
        canonical["archive_paths"] = [
            item["path"] for item in ordered if item.get("_source_scope") == "archive"
        ]
        canonical["duplicate_count"] = len(ordered) - 1
        canonical["scope_flags"] = (
            "witness_only"
            if not canonical.get("text_extractable")
            else (
                "both"
                if scopes == {"live", "archive"}
                else ("live" if "live" in scopes else "archive")
            )
        )
        canonical.pop("_source_scope", None)
        canonical_records.append(canonical)

    canonical_records.sort(key=lambda item: normalize_path(item.get("relative_path", "")).lower())
    return canonical_records


def build_control_lookups(
    control_records: list[dict[str, Any]],
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, list[dict[str, Any]]]]:
    by_sha: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_path: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in control_records:
        by_sha[record.get("sha256", "")].append(record)
        by_path[normalize_path(record.get("relative_path", "")).lower()].append(record)
    return dict(by_sha), dict(by_path)


def control_match_for_record(
    record: dict[str, Any],
    control_by_sha: dict[str, list[dict[str, Any]]],
    control_by_path: dict[str, list[dict[str, Any]]],
) -> dict[str, Any] | None:
    sha_hits = control_by_sha.get(record.get("sha256", ""), [])
    if sha_hits:
        return sha_hits[0]
    path_hits = control_by_path.get(normalize_path(record.get("relative_path", "")).lower(), [])
    if path_hits:
        return path_hits[0]
    return None


def anchor_metadata(
    record: dict[str, Any],
    anchors: list[BasisAnchor],
    basis_anchor_ids: list[str],
    family: str,
    primary_hemisphere: str,
) -> tuple[str, float, str]:
    anchor_map = {anchor.anchor_id: anchor for anchor in anchors}
    primary_anchor = anchor_map.get(basis_anchor_ids[0]) if basis_anchor_ids else None
    if primary_anchor is None:
        return (
            f"Fallback anchor allocation for {family} on {primary_hemisphere}.",
            0.25,
            "",
        )
    raw_score = anchor_score(record, primary_anchor)
    confidence = round(min(0.98, 0.25 + raw_score / 8.0), 4)
    justification = (
        f"{primary_anchor.anchor_id} via {primary_anchor.title}; "
        f"role={primary_anchor.role}; cluster={primary_anchor.cluster}"
    )
    return justification, confidence, primary_anchor.cluster


def symmetry_membership(
    record: dict[str, Any],
    basis_anchor_ids: list[str],
    anchor_map: dict[str, BasisAnchor],
) -> dict[str, Any]:
    anchor = anchor_map.get(basis_anchor_ids[0]) if basis_anchor_ids else None
    return {
        "stack_id": "15+Z0",
        "zero_point_active": record.get("bridge_class") == "commissure_bridge",
        "primary_anchor": basis_anchor_ids[0] if basis_anchor_ids else "",
        "primary_cluster": anchor.cluster if anchor else "",
        "primary_element": anchor.element if anchor else "",
        "observer_lattice": "O64",
    }


def initial_appendix_governance_flags(record: dict[str, Any]) -> list[str]:
    flags: list[str] = []
    if record.get("tract") == "replay" or record.get("family") in {
        "void-and-collapse",
        "helical-recursion-engine",
    }:
        flags.append("replay")
    if not record.get("text_extractable"):
        flags.append("witness")
    if record.get("scope_flags") == "archive":
        flags.append("archive_only")
    if record.get("duplicate_count", 0) > 0:
        flags.append("duplicate")
    if record.get("bridge_class") == "commissure_bridge":
        flags.append("commissure")
    return flags


def semantic_mass_for_record(record: dict[str, Any]) -> float:
    base = 1.0
    base += 0.08 * min(3, len(record.get("heading_candidates") or []))
    base += 0.04 * min(6, len(record.get("basis_anchor_ids", [])))
    if record.get("text_extractable"):
        base += 0.12
    return round(min(1.8, base), 4)


def route_quality_for_record(record: dict[str, Any]) -> float:
    quality = 1.0
    if record.get("scope_flags") == "archive":
        quality -= 0.12
    if not record.get("text_extractable"):
        quality -= 0.28
    if record.get("duplicate_count", 0) > 0:
        quality += 0.04
    return round(max(0.35, min(1.2, quality)), 4)


def project_full_record(
    record: dict[str, Any],
    control_match: dict[str, Any] | None,
    docs_gate_status: str,
    station_map: dict[str, dict[str, Any]],
    anchors: list[BasisAnchor],
    aqm_lane: dict[str, Any],
) -> dict[str, Any]:
    title = record_title(record)
    family = (
        control_match.get("family")
        if control_match
        else infer_family(Path(record.get("relative_path", "")).name, record.get("excerpt", ""))
    )
    component_scores = (
        control_match.get("component_scores")
        if control_match and control_match.get("component_scores")
        else compute_component_scores(record, family, station_map)
    )
    raw_math_weight = (
        control_match.get("math_weight")
        if control_match and control_match.get("math_weight") is not None
        else weighted_math_score(component_scores)
    )
    math_weight, myth_weight = normalize_weights(float(raw_math_weight))
    primary_hemisphere = (
        control_match.get("primary_hemisphere")
        if control_match and control_match.get("primary_hemisphere")
        else ("MATH" if math_weight >= myth_weight else "MYTH")
    )
    bridge_class = (
        control_match.get("bridge_class")
        if control_match and control_match.get("bridge_class")
        else (
            "commissure_bridge"
            if 0.45 <= math_weight <= 0.55
            else ("math_primary" if primary_hemisphere == "MATH" else "myth_primary")
        )
    )
    bridge_intensity = (
        float(control_match.get("bridge_intensity"))
        if control_match and control_match.get("bridge_intensity") is not None
        else round(max(0.0, 1.0 - abs(math_weight - 0.5) * 2.0), 6)
    )
    tract = (
        control_match.get("tract")
        if control_match and control_match.get("tract")
        else resolve_tract(family, record, station_map)
    )
    basis_anchor_ids = (
        list(control_match.get("basis_anchor_ids", []))
        if control_match and control_match.get("basis_anchor_ids")
        else []
    )
    if not basis_anchor_ids:
        from self_actualize.runtime.hemisphere_brain_support import assign_basis_anchor_ids

        basis_anchor_ids = assign_basis_anchor_ids(record, anchors, family, primary_hemisphere)
    anchor_justification, anchor_confidence, deeper_cluster = anchor_metadata(
        record,
        anchors,
        basis_anchor_ids,
        family,
        primary_hemisphere,
    )
    appendix_support = (
        list(control_match.get("appendix_support", []))
        if control_match and control_match.get("appendix_support")
        else infer_appendix_links(title, record.get("excerpt", ""), family)
    )
    confidence = (
        float(control_match.get("confidence"))
        if control_match and control_match.get("confidence") is not None
        else compute_confidence(record, math_weight)
    )
    semantic_mass = (
        float(control_match.get("semantic_mass"))
        if control_match and control_match.get("semantic_mass") is not None
        else semantic_mass_for_record(record)
    )
    route_quality = (
        float(control_match.get("route_quality"))
        if control_match and control_match.get("route_quality") is not None
        else route_quality_for_record(record)
    )
    salience = (
        float(control_match.get("salience"))
        if control_match and control_match.get("salience") is not None
        else round(max(math_weight, myth_weight) * semantic_mass * route_quality, 6)
    )
    truth_state = (
        control_match.get("truth_state")
        if control_match and control_match.get("truth_state")
        else ("OK" if record.get("text_extractable") else "NEAR")
    )
    control_record_ids = [control_match["record_id"]] if control_match else []
    control_relative_paths = [control_match["relative_path"]] if control_match else []
    projected = {
        "record_id": record["record_id"],
        "title": title,
        "path": record.get("path", ""),
        "relative_path": record.get("relative_path", ""),
        "top_level": record.get("top_level", ""),
        "sha256": record.get("sha256", ""),
        "kind": record.get("kind", "document"),
        "extension": record.get("extension", ""),
        "size_bytes": record.get("size_bytes", 0),
        "modified_at": record.get("modified_at", ""),
        "text_extractable": bool(record.get("text_extractable")),
        "excerpt": record.get("excerpt", ""),
        "heading_candidates": list(record.get("heading_candidates") or []),
        "math_weight": math_weight,
        "myth_weight": myth_weight,
        "primary_hemisphere": primary_hemisphere,
        "bridge_class": bridge_class,
        "bridge_intensity": round(bridge_intensity, 6),
        "confidence": round(confidence, 4),
        "family": family,
        "family_label": FAMILY_LABELS.get(family, family),
        "tract": tract,
        "basis_anchor_ids": basis_anchor_ids,
        "anchor_justification": anchor_justification,
        "anchor_confidence": anchor_confidence,
        "deeper_cluster": deeper_cluster,
        "appendix_support": appendix_support,
        "appendix_support_sources": {},
        "appendix_governance_flags": [],
        "aqm_trace_hash": trace_hash(
            {
                "record_id": record["record_id"],
                "sha256": record.get("sha256", ""),
                "family": family,
                "primary_hemisphere": primary_hemisphere,
                "aqm_truth": aqm_lane.get("truth", "UNKNOWN"),
            }
        ),
        "docs_gate_status": docs_gate_status,
        "grand_central": UNIFIED_HUB_ID,
        "hub_id": UNIFIED_HUB_ID,
        "chapter_station": "",
        "local_addr": "",
        "global_addr": "",
        "tesseract_header": "",
        "truth_state": truth_state,
        "truth_intent": "control_slice_overlay" if control_match else "full_corpus_projection",
        "hubs_seq": [MATH_HUB_ID, UNIFIED_HUB_ID, MYTH_HUB_ID],
        "tunnel_plan": [],
        "hcrl_pass": False,
        "obligations": [],
        "drop_log": [],
        "overlay_annotations": [],
        "route_plan_id": f"FCA-{slugify(record['record_id'])}",
        "graph_edge_ids": [],
        "primary_hubs_text": "",
        "tunnel_text": "",
        "truth_state_text": truth_state,
        "hcrl_text": "",
        "salience": round(salience, 6),
        "semantic_mass": semantic_mass,
        "route_quality": route_quality,
        "scope_flags": record.get("scope_flags", "live"),
        "source_scopes": record.get("source_scopes", []),
        "source_paths": record.get("source_paths", []),
        "source_record_ids": record.get("source_record_ids", []),
        "duplicate_paths": record.get("duplicate_paths", []),
        "duplicate_record_ids": record.get("duplicate_record_ids", []),
        "duplicate_count": int(record.get("duplicate_count", 0)),
        "live_paths": record.get("live_paths", []),
        "archive_paths": record.get("archive_paths", []),
        "control_record_ids": control_record_ids,
        "control_relative_paths": control_relative_paths,
        "hemisphere_routes": {},
        "direct_edge_ids": [],
        "route_coverage": {},
    }
    projected["appendix_governance_flags"] = initial_appendix_governance_flags(projected)
    projected["holo_address"] = build_holo_address(
        primary_hemisphere,
        tract,
        family,
        basis_anchor_ids,
        projected["record_id"],
    )
    return projected


def stage_scores(record: dict[str, Any], anchor_map: dict[str, BasisAnchor]) -> dict[str, float]:
    scores = {stage_id: 0.0 for stage_id in STAGE_ORDER}
    default_stage = STAGE_FAMILY_DEFAULTS.get(record.get("family", ""), "COMPLETE_ACT")
    scores[default_stage] += 0.52
    tract_stage = TRACT_STAGE_BOOST.get(record.get("tract", ""))
    if tract_stage:
        scores[tract_stage] += 0.16
    if record.get("primary_hemisphere") == "MATH":
        scores["AIR"] += 0.12
        scores["EARTH"] += 0.08
    else:
        scores["WATER"] += 0.12
        scores["ARCHETYPAL_OPERATION"] += 0.08
    if record.get("bridge_class") == "commissure_bridge":
        scores["COMPLETE_ACT"] += 0.14
    if record.get("scope_flags") == "archive":
        scores["VOID"] += 0.10
    if not record.get("text_extractable"):
        scores["VOID"] += 0.18
    blob = text_blob(record, anchor_map)
    for token, stage_id in KEYWORD_STAGE_BOOSTS.items():
        if token in blob:
            scores[stage_id] += 0.06
    element = primary_basis_element(record.get("basis_anchor_ids", []), anchor_map)
    if element == "fire":
        scores["FIRE"] += 0.05
    elif element == "water":
        scores["WATER"] += 0.05
    elif element == "air":
        scores["AIR"] += 0.05
    elif element == "earth":
        scores["EARTH"] += 0.05
    return {stage_id: round(score, 4) for stage_id, score in scores.items()}


def transition_stages_for_stage(stage_id: str) -> list[str]:
    if stage_id not in STAGE_ORDER:
        return []
    index = STAGE_ORDER.index(stage_id)
    stages: list[str] = []
    if index > 0:
        stages.append(STAGE_ORDER[index - 1])
    if index + 1 < len(STAGE_ORDER):
        stages.append(STAGE_ORDER[index + 1])
    return stages[:2]


def reassessment_window_for_record(record: dict[str, Any]) -> str:
    if not record.get("text_extractable"):
        return "7d"
    if record.get("scope_flags") == "archive":
        return "14d"
    if record.get("confidence", 0.0) < 0.58:
        return "10d"
    return STAGE_NOTES.get(record.get("awakening_stage", ""), {}).get(
        "reassessment_window",
        "21d",
    )


def assignment_blockers(record: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if record.get("confidence", 0.0) < 0.58:
        blockers.append("proof_weakness")
    if record.get("scope_flags") == "archive":
        blockers.append("archive_only_dependence")
    primary_route = record.get("hemisphere_routes", {}).get(record.get("primary_hemisphere", ""), {})
    if primary_route.get("proof_state") not in {"", "OK"}:
        blockers.append("historical_drift")
    if record.get("docs_gate_status") == "BLOCKED":
        blockers.append("docs_gate_absence")
    return blockers


def basis_overlay_ids(
    record: dict[str, Any],
    basis_note_map: dict[str, dict[str, Any]],
) -> list[str]:
    overlay_ids: list[str] = []
    for anchor_id in record.get("basis_anchor_ids", []):
        note = basis_note_map.get(anchor_id)
        if note:
            overlay_ids.append(note["note_id"])
    return overlay_ids


def family_note_id(stage_id: str, family: str) -> str:
    return f"AWNOTE-{stage_id}-{slugify(family)}"


def preferred_route_ids(record: dict[str, Any]) -> list[str]:
    route_ids: list[str] = []
    for hemisphere in ("MATH", "MYTH"):
        route_id = record.get("hemisphere_routes", {}).get(hemisphere, {}).get("route_id", "")
        if route_id:
            route_ids.append(route_id)
    return route_ids


def build_stage_assignments(
    records: list[dict[str, Any]],
    anchor_map: dict[str, BasisAnchor],
) -> tuple[list[dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    assignments: list[dict[str, Any]] = []
    stage_to_records: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        scores = stage_scores(record, anchor_map)
        primary_stage = max(
            STAGE_ORDER,
            key=lambda stage_id: (scores[stage_id], -STAGE_ORDER.index(stage_id)),
        )
        abstention_reason = ""
        if scores[primary_stage] < 0.22:
            abstention_reason = "insufficient_stage_signal"
        transitions = transition_stages_for_stage(primary_stage) if not abstention_reason else []
        blockers = assignment_blockers(record)
        record["awakening_stage"] = primary_stage if not abstention_reason else ""
        record["awakening_transition_stages"] = transitions
        record["awakening_abstention_reason"] = abstention_reason
        record["awakening_stage_blockers"] = blockers
        assignment = {
            "record_id": record["record_id"],
            "control_record_ids": record.get("control_record_ids", []),
            "relative_path": record.get("relative_path", ""),
            "stage_id": primary_stage if not abstention_reason else "",
            "stage_label": stage_label(primary_stage) if not abstention_reason else "",
            "transition_stages": transitions,
            "stage_scores": scores,
            "family": record.get("family", ""),
            "basis_anchor_ids": record.get("basis_anchor_ids", []),
            "primary_hemisphere": record.get("primary_hemisphere", ""),
            "target_systems": {
                side: route.get("target_system", "")
                for side, route in record.get("hemisphere_routes", {}).items()
            },
            "blockers": blockers,
            "reassessment_window": reassessment_window_for_record(record),
            "evidence_ids": [record["record_id"]],
            "basis_role_overlay_ids": record.get("basis_anchor_ids", []),
            "docs_gate_status": record.get("docs_gate_status", "UNKNOWN"),
            "abstention_reason": abstention_reason,
        }
        assignments.append(assignment)
        if not abstention_reason:
            stage_to_records[primary_stage].append(record)
    return assignments, dict(stage_to_records)


def dominant_family(records: list[dict[str, Any]]) -> str:
    if not records:
        return "general-corpus"
    return Counter(
        record.get("family", "general-corpus") for record in records
    ).most_common(1)[0][0]


def dominant_anchor(records: list[dict[str, Any]]) -> str:
    counter: Counter[str] = Counter()
    for record in records:
        counter.update((record.get("basis_anchor_ids") or [])[:1])
    if not counter:
        return ""
    return counter.most_common(1)[0][0]


def note_primary_hemisphere(records: list[dict[str, Any]]) -> str:
    hemispheres = [
        record.get("primary_hemisphere", "")
        for record in records
        if record.get("primary_hemisphere")
    ]
    if not hemispheres:
        return "MATH"
    return Counter(hemispheres).most_common(1)[0][0]


def build_family_notes(
    records: list[dict[str, Any]],
    docs_gate_status: str,
) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[record.get("family", "general-corpus")].append(record)
    notes: list[dict[str, Any]] = []
    for family in sorted(FAMILY_LABELS):
        family_records = grouped.get(family, [])
        transition = FAMILY_TRANSITION_MAP.get(
            family,
            {
                "stabilizes": "local coherence",
                "overproduces": "drift through over-extension",
                "relinquish": "the wish to remain generic forever",
            },
        )
        evidence_ids = [record["record_id"] for record in top_records(family_records, 3)]
        notes.append(
            {
                "note_id": f"AW-FAMILY-{slugify(family)}",
                "stage_id": "GLOBAL",
                "family_id": family,
                "basis_role_id": dominant_anchor(family_records),
                "primary_hemisphere": note_primary_hemisphere(family_records),
                "current_signal": f"{FAMILY_LABELS.get(family, family)} stabilizes {transition['stabilizes']}.",
                "common_trap": transition["overproduces"],
                "missing_element": transition["relinquish"],
                "transition_move": (
                    f"Use the opposite hemisphere route and GC0 crossing to release {transition['relinquish']}."
                ),
                "preferred_route_ids": preferred_route_ids(family_records[0]) if family_records else [],
                "evidence_ids": evidence_ids,
                "reassessment_window": "14d",
                "docs_gate_status": docs_gate_status,
                "abstention_reason": "" if evidence_ids else "no_family_evidence",
            }
        )
    return notes


def build_basis_role_notes(
    records: list[dict[str, Any]],
    anchor_map: dict[str, BasisAnchor],
    docs_gate_status: str,
) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        for anchor_id in record.get("basis_anchor_ids", []):
            grouped[anchor_id].append(record)
    notes: list[dict[str, Any]] = []
    for anchor_id in sorted(anchor_map):
        anchor = anchor_map[anchor_id]
        anchor_records = grouped.get(anchor_id, [])
        evidence_ids = [record["record_id"] for record in top_records(anchor_records, 3)]
        missing = ELEMENT_LIMITATION.get(
            anchor.element.lower(),
            "the opposite mode of operation",
        )
        notes.append(
            {
                "note_id": f"AW-BASIS-{anchor_id}",
                "stage_id": "GLOBAL",
                "family_id": dominant_family(anchor_records),
                "basis_role_id": anchor_id,
                "primary_hemisphere": note_primary_hemisphere(anchor_records),
                "current_signal": f"{anchor.title} teaches {anchor.role}.",
                "common_trap": f"{anchor.title} can overfit the field to cluster {anchor.cluster}.",
                "missing_element": missing,
                "transition_move": (
                    f"Use {anchor.cluster} as a handoff surface and keep {missing} visible."
                ),
                "preferred_route_ids": preferred_route_ids(anchor_records[0]) if anchor_records else [],
                "evidence_ids": evidence_ids,
                "reassessment_window": "21d",
                "docs_gate_status": docs_gate_status,
                "abstention_reason": "" if evidence_ids else "no_basis_evidence",
            }
        )
    return notes


def build_stage_family_matrix(
    records: list[dict[str, Any]],
    docs_gate_status: str,
) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        stage_id = record.get("awakening_stage", "")
        if stage_id:
            grouped[(stage_id, record.get("family", "general-corpus"))].append(record)

    notes: list[dict[str, Any]] = []
    for stage_id in STAGE_ORDER:
        for family in sorted(FAMILY_LABELS):
            cell_records = grouped.get((stage_id, family), [])
            best_records = top_records(cell_records, 3)
            evidence_ids = [record["record_id"] for record in best_records]
            transition = FAMILY_TRANSITION_MAP.get(family, {})
            notes.append(
                {
                    "note_id": family_note_id(stage_id, family),
                    "stage_id": stage_id,
                    "family_id": family,
                    "basis_role_id": dominant_anchor(cell_records),
                    "primary_hemisphere": note_primary_hemisphere(cell_records),
                    "current_signal": (
                        f"{stage_label(stage_id)} through {FAMILY_LABELS.get(family, family)} emphasizes "
                        f"{transition.get('stabilizes', 'coherent passage')}."
                    ),
                    "common_trap": transition.get(
                        "overproduces",
                        "local over-identification with the active family mode",
                    ),
                    "missing_element": STAGE_NOTES[stage_id]["missing_element"],
                    "transition_move": (
                        f"{STAGE_NOTES[stage_id]['transition_move']} via {FAMILY_LABELS.get(family, family)}."
                    ),
                    "preferred_route_ids": preferred_route_ids(best_records[0]) if best_records else [],
                    "evidence_ids": evidence_ids,
                    "reassessment_window": STAGE_NOTES[stage_id]["reassessment_window"],
                    "docs_gate_status": docs_gate_status,
                    "abstention_reason": "" if evidence_ids else "no_stage_family_evidence",
                }
            )
    return notes


def build_handoff_notes(
    records: list[dict[str, Any]],
    docs_gate_status: str,
) -> list[dict[str, Any]]:
    evidence_map = {
        "commissure_active": top_records(
            [record for record in records if record.get("bridge_class") == "commissure_bridge"],
            3,
        ),
        "hub_transfer": top_records(records, 3),
        "replay_heavy": top_records(
            [record for record in records if record.get("tract") == "replay"],
            3,
        ),
        "quarantine_heavy": top_records(
            [record for record in records if "quarantine" in record.get("appendix_governance_flags", [])],
            3,
        ),
    }
    notes: list[dict[str, Any]] = []
    for mode in HANDOFF_MODES:
        evidence_ids = [record["record_id"] for record in evidence_map.get(mode, [])]
        notes.append(
            {
                "note_id": f"AW-HANDOFF-{slugify(mode)}",
                "stage_id": "HANDOFF",
                "family_id": "cross-family",
                "basis_role_id": "",
                "primary_hemisphere": "MATH",
                "current_signal": f"{mode.replace('_', ' ')} is active.",
                "common_trap": "Forgetting to carry proof, replay, and opposite-hemisphere support together.",
                "missing_element": "the lawful return path",
                "transition_move": "Cross through GC0 and re-enter with explicit route, proof, and reassessment.",
                "preferred_route_ids": preferred_route_ids(evidence_map[mode][0]) if evidence_map.get(mode) else [],
                "evidence_ids": evidence_ids,
                "reassessment_window": "7d",
                "docs_gate_status": docs_gate_status,
                "abstention_reason": "" if evidence_ids else "no_handoff_evidence",
            }
        )
    return notes


def build_appendix_governance_ledger(
    records: list[dict[str, Any]],
    docs_gate_status: str,
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for record in records:
        route_packets = record.get("hemisphere_routes", {})
        proof_states = {
            side: route_packets.get(side, {}).get("proof_state", "")
            for side in ("MATH", "MYTH")
        }
        replay_required = record.get("tract") == "replay" or record.get("family") in {
            "void-and-collapse",
            "helical-recursion-engine",
        }
        restart_eligible = (
            record.get("bridge_class") == "commissure_bridge"
            and record.get("confidence", 0.0) < 0.7
        )
        quarantine_required = (
            not record.get("text_extractable")
            or all(state not in {"", "OK"} for state in proof_states.values())
        )
        repair_eligible = (
            record.get("duplicate_count", 0) > 0
            or record.get("family") == "helical-recursion-engine"
            or not record.get("text_extractable")
        )
        proof_uplift_required = (
            record.get("scope_flags") == "archive"
            or any(state not in {"", "OK"} for state in proof_states.values())
        )
        flags: list[str] = []
        if replay_required:
            flags.append("replay")
        if restart_eligible:
            flags.append("restart")
        if quarantine_required:
            flags.append("quarantine")
        if repair_eligible:
            flags.append("repair")
        if proof_uplift_required:
            flags.append("proof_uplift")
        if quarantine_required and "AppQ" not in record["appendix_support"]:
            record["appendix_support"] = [*record["appendix_support"], "AppQ"]
        record["appendix_governance_flags"] = flags
        rows.append(
            {
                "record_id": record["record_id"],
                "relative_path": record.get("relative_path", ""),
                "appendix_support": record.get("appendix_support", []),
                "replay_required": replay_required,
                "restart_eligible": restart_eligible,
                "quarantine_required": quarantine_required,
                "repair_eligible": repair_eligible,
                "proof_uplift_required": proof_uplift_required,
                "proof_states": proof_states,
                "governance_reason": ", ".join(flags) if flags else "stable",
                "docs_gate_status": docs_gate_status,
            }
        )
    return {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "record_count": len(rows),
        "rows": rows,
        "counts": {
            "replay_required": sum(1 for row in rows if row["replay_required"]),
            "restart_eligible": sum(1 for row in rows if row["restart_eligible"]),
            "quarantine_required": sum(1 for row in rows if row["quarantine_required"]),
            "repair_eligible": sum(1 for row in rows if row["repair_eligible"]),
            "proof_uplift_required": sum(1 for row in rows if row["proof_uplift_required"]),
        },
        "allowed_appendix_ids": [f"App{chr(code)}" for code in range(ord('A'), ord('P') + 1)]
        + ["AppQ"],
    }


def build_basis_crosswalk_registry(
    records: list[dict[str, Any]],
    docs_gate_status: str,
) -> dict[str, Any]:
    weak_rows: list[dict[str, Any]] = []
    rows: list[dict[str, Any]] = []
    anchor_distribution: Counter[str] = Counter()
    for record in records:
        first_anchor = (record.get("basis_anchor_ids") or [""])[0]
        if first_anchor:
            anchor_distribution.update([first_anchor])
        row = {
            "record_id": record["record_id"],
            "control_record_ids": record.get("control_record_ids", []),
            "relative_path": record.get("relative_path", ""),
            "basis_anchor_ids": record.get("basis_anchor_ids", []),
            "anchor_justification": record.get("anchor_justification", ""),
            "anchor_confidence": record.get("anchor_confidence", 0.0),
            "primary_hemisphere": record.get("primary_hemisphere", ""),
            "family": record.get("family", ""),
            "deeper_cluster": record.get("deeper_cluster", ""),
            "symmetry_membership": record.get("symmetry_membership", {}),
            "appendix_support": record.get("appendix_support", []),
            "docs_gate_status": docs_gate_status,
            "abstention_reason": "" if record.get("basis_anchor_ids") else "no_basis_anchor",
        }
        rows.append(row)
        if not record.get("basis_anchor_ids") or record.get("anchor_confidence", 0.0) < 0.35:
            weak_rows.append(row)
    return {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "record_count": len(rows),
        "rows": rows,
        "anchor_distribution": dict(anchor_distribution),
        "weak_or_uncovered_rows": weak_rows,
    }


def build_route_saturation_registry(
    records: list[dict[str, Any]],
    route_registry: dict[str, Any],
    direct_edge_registry: dict[str, Any],
    docs_gate_status: str,
) -> dict[str, Any]:
    primary_target_distribution: Counter[str] = Counter()
    secondary_target_distribution: Counter[str] = Counter()
    proof_distribution: Counter[str] = Counter()
    rows: list[dict[str, Any]] = []
    for record in records:
        primary = record.get("hemisphere_routes", {}).get(record.get("primary_hemisphere", ""), {})
        secondary_side = "MYTH" if record.get("primary_hemisphere") == "MATH" else "MATH"
        secondary = record.get("hemisphere_routes", {}).get(secondary_side, {})
        route_coverage = record.get("route_coverage", {})
        coverage_complete = all(
            route_coverage.get(side, {}).get(key, False)
            for side in ("MATH", "MYTH")
            for key in PRIMARY_HF_ROUTE_KEYS
        )
        primary_target_distribution.update([primary.get("target_system", "")])
        secondary_target_distribution.update([secondary.get("target_system", "")])
        proof_distribution.update([primary.get("proof_state", ""), secondary.get("proof_state", "")])
        gc0_edge_id = f"FULL-GC0-{record['record_id']}"
        if gc0_edge_id not in record["direct_edge_ids"]:
            record["direct_edge_ids"] = [*record.get("direct_edge_ids", []), gc0_edge_id]
        record["graph_edge_ids"] = [*record.get("graph_edge_ids", []), gc0_edge_id]
        rows.append(
            {
                "record_id": record["record_id"],
                "relative_path": record.get("relative_path", ""),
                "primary_hemisphere": record.get("primary_hemisphere", ""),
                "primary_route_id": primary.get("route_id", ""),
                "secondary_route_id": secondary.get("route_id", ""),
                "primary_target_system": primary.get("target_system", ""),
                "secondary_target_system": secondary.get("target_system", ""),
                "gc0_membership": UNIFIED_HUB_ID,
                "direct_edge_ids": record.get("direct_edge_ids", []),
                "route_coverage": route_coverage,
                "coverage_complete": coverage_complete,
                "proof_states": {
                    "MATH": record.get("hemisphere_routes", {}).get("MATH", {}).get("proof_state", ""),
                    "MYTH": record.get("hemisphere_routes", {}).get("MYTH", {}).get("proof_state", ""),
                },
                "docs_gate_status": docs_gate_status,
            }
        )
    gc0_edge_ledger = [
        {
            "edge_id": f"FULL-GC0-{record['record_id']}",
            "record_id": record["record_id"],
            "source_id": record["record_id"],
            "target_id": UNIFIED_HUB_ID,
            "edge_type": "unified_hub_membership",
            "docs_gate_status": docs_gate_status,
        }
        for record in records
    ]
    return {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "record_count": len(rows),
        "route_count": route_registry.get("route_count", 0),
        "direct_edge_count": direct_edge_registry.get("edge_count", 0),
        "gc0_edge_count": len(gc0_edge_ledger),
        "rows": rows,
        "gc0_edge_ledger": gc0_edge_ledger,
        "primary_target_distribution": dict(primary_target_distribution),
        "secondary_target_distribution": dict(secondary_target_distribution),
        "proof_distribution": dict(proof_distribution),
        "complete_count": sum(1 for row in rows if row["coverage_complete"]),
        "required_coverage_keys": list(PRIMARY_HF_ROUTE_KEYS),
    }


def build_stage_registry(
    records: list[dict[str, Any]],
    anchor_map: dict[str, BasisAnchor],
    docs_gate_status: str,
) -> dict[str, Any]:
    assignments, stage_to_records = build_stage_assignments(records, anchor_map)
    stage_crosswalk: dict[str, dict[str, Any]] = {}
    global_notes: list[dict[str, Any]] = []
    for stage_id in STAGE_ORDER:
        stage_records = stage_to_records.get(stage_id, [])
        anchor_distribution = Counter(
            (record.get("basis_anchor_ids") or [""])[0]
            for record in stage_records
            if record.get("basis_anchor_ids")
        )
        target_distribution: Counter[str] = Counter()
        family_distribution = Counter(record.get("family", "") for record in stage_records)
        hemisphere_distribution = Counter(
            record.get("primary_hemisphere", "") for record in stage_records
        )
        blockers = Counter()
        for record in stage_records:
            for blocker in record.get("awakening_stage_blockers", []):
                blockers.update([blocker])
            primary_route = record.get("hemisphere_routes", {}).get(
                record.get("primary_hemisphere", ""),
                {},
            )
            if primary_route.get("target_system"):
                target_distribution.update([primary_route["target_system"]])
        stage_crosswalk[stage_id] = {
            "stage_id": stage_id,
            "label": stage_label(stage_id),
            "count": len(stage_records),
            "hemisphere_distribution": dict(hemisphere_distribution),
            "family_distribution": dict(family_distribution),
            "target_system_distribution": dict(target_distribution),
            "anchor_distribution": dict(anchor_distribution),
        }
        note_meta = STAGE_NOTES[stage_id]
        global_notes.append(
            {
                "stage_id": stage_id,
                "label": stage_label(stage_id),
                "current_signal": note_meta["current_signal"],
                "common_trap": note_meta["common_trap"],
                "missing_element": note_meta["missing_element"],
                "lawful_next_move": note_meta["transition_move"],
                "proof_of_progress": note_meta["proof_of_progress"],
                "reassessment_window": note_meta["reassessment_window"],
                "blockers": dict(blockers),
                "evidence_ids": [record["record_id"] for record in top_records(stage_records, 3)],
                "docs_gate_status": docs_gate_status,
            }
        )
    assigned_count = sum(1 for item in assignments if item.get("stage_id"))
    return {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "stage_count": len(STAGE_ORDER),
        "stages": [
            {"stage_id": stage_id, "label": stage_label(stage_id), **STAGE_NOTES[stage_id]}
            for stage_id in STAGE_ORDER
        ],
        "record_assignment_count": len(assignments),
        "assigned_count": assigned_count,
        "abstention_count": len(assignments) - assigned_count,
        "record_assignments": assignments,
        "stage_crosswalk": stage_crosswalk,
        "global_transition_notes": global_notes,
    }


def build_agent_transition_registry(
    records: list[dict[str, Any]],
    stage_registry: dict[str, Any],
    anchor_map: dict[str, BasisAnchor],
    docs_gate_status: str,
) -> dict[str, Any]:
    family_notes = build_family_notes(records, docs_gate_status)
    basis_role_notes = build_basis_role_notes(records, anchor_map, docs_gate_status)
    basis_note_map = {note["basis_role_id"]: note for note in basis_role_notes}
    stage_family_matrix = build_stage_family_matrix(records, docs_gate_status)
    handoff_notes = build_handoff_notes(records, docs_gate_status)
    assignments_by_record = {
        assignment["record_id"]: assignment
        for assignment in stage_registry.get("record_assignments", [])
    }
    for record in records:
        assignment = assignments_by_record.get(record["record_id"])
        if not assignment:
            continue
        assignment["family_transition_note_ids"] = (
            [family_note_id(assignment["stage_id"], record.get("family", "general-corpus"))]
            if assignment.get("stage_id")
            else []
        )
        assignment["basis_role_overlay_ids"] = basis_overlay_ids(record, basis_note_map)
    return {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "family_note_count": len(family_notes),
        "basis_role_note_count": len(basis_role_notes),
        "stage_family_note_count": len(stage_family_matrix),
        "handoff_note_count": len(handoff_notes),
        "family_notes": family_notes,
        "basis_role_notes": basis_role_notes,
        "stage_family_matrix": stage_family_matrix,
        "handoff_notes": handoff_notes,
    }


def build_authority_registry(
    records: list[dict[str, Any]],
    live_atlas: dict[str, Any],
    archive_atlas: dict[str, Any],
    docs_gate_status: str,
) -> dict[str, Any]:
    scope_distribution = Counter(record.get("scope_flags", "live") for record in records)
    return {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "record_count": len(records),
        "live_atlas_record_count": live_atlas.get("record_count", 0),
        "archive_atlas_record_count": archive_atlas.get("record_count", 0),
        "scope_distribution": dict(scope_distribution),
        "records": records,
    }


def build_integration_manifest(
    control_manifest: dict[str, Any],
    live_atlas: dict[str, Any],
    archive_atlas: dict[str, Any],
    archive_manifest: dict[str, Any],
    authority_registry: dict[str, Any],
    basis_crosswalk_registry: dict[str, Any],
    route_coverage_registry: dict[str, Any],
    stage_registry: dict[str, Any],
    agent_registry: dict[str, Any],
    appendix_ledger: dict[str, Any],
    docs_gate_status: str,
    aqm_lane: dict[str, Any],
) -> dict[str, Any]:
    return {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "scope": {
            "mode": "local_first_full_corpus_plus_archive",
            "phase_1_control_slice_records": control_manifest.get("counts", {}).get("record_count", 0),
            "live_root": live_atlas.get("root", ""),
            "archive_root": archive_atlas.get("root", ""),
            "aqm_truth": aqm_lane.get("truth", "UNKNOWN"),
        },
        "source_manifests": {
            "control_manifest": str(SELF_ACTUALIZE_ROOT / "myth_math_hemisphere_manifest.json"),
            "corpus_atlas": str(CORPUS_ATLAS_PATH),
            "archive_atlas": str(ARCHIVE_ATLAS_PATH),
            "archive_manifest": str(ARCHIVE_MANIFEST_PATH),
            "deeper_network_readme": str(DEEPER_NETWORK_README_PATH),
        },
        "counts": {
            "live_atlas_records": live_atlas.get("record_count", 0),
            "archive_atlas_records": archive_atlas.get("record_count", 0),
            "merged_canonical_records": authority_registry.get("record_count", 0),
            "live_only_records": authority_registry.get("scope_distribution", {}).get("live", 0),
            "archive_only_records": authority_registry.get("scope_distribution", {}).get("archive", 0),
            "both_scope_records": authority_registry.get("scope_distribution", {}).get("both", 0),
            "witness_only_records": authority_registry.get("scope_distribution", {}).get("witness_only", 0),
            "assigned_stage_records": stage_registry.get("assigned_count", 0),
            "stage_abstentions": stage_registry.get("abstention_count", 0),
            "basis_weak_or_uncovered": len(basis_crosswalk_registry.get("weak_or_uncovered_rows", [])),
            "route_complete_records": route_coverage_registry.get("complete_count", 0),
            "appendix_quarantine_records": appendix_ledger.get("counts", {}).get("quarantine_required", 0),
            "family_transition_notes": agent_registry.get("family_note_count", 0),
            "basis_role_notes": agent_registry.get("basis_role_note_count", 0),
            "stage_family_notes": agent_registry.get("stage_family_note_count", 0),
        },
        "outputs": {key: str(path) for key, path in FULL_CORPUS_JSON_OUTPUTS.items()},
        "notes": [
            "Control slice remains authoritative for the current hemisphere runtime while the full-corpus surface widens scope to the local live corpus and archive atlas.",
            "The 16 deeper-network canonical sources remain the only deep anchor lattice.",
            "Google Docs evidence remains blocked and is not claimed in this manifest.",
            f"Archive manifest entries observed: {archive_manifest.get('counts', {}).get('entries', archive_atlas.get('record_count', 0))}.",
        ],
    }


def build_record_locator_lines(records: list[dict[str, Any]], limit: int = 12) -> list[list[str]]:
    rows: list[list[str]] = []
    for record in top_records(records, limit):
        primary_route = record.get("hemisphere_routes", {}).get(
            record.get("primary_hemisphere", ""),
            {},
        )
        rows.append(
            [
                record["record_id"],
                stage_label(record.get("awakening_stage", "")) if record.get("awakening_stage") else "ABSTAIN",
                record.get("family", ""),
                primary_route.get("target_system", ""),
                normalize_path(record.get("relative_path", "")),
            ]
        )
    return rows


def render_markdown_pages(
    authority_registry: dict[str, Any],
    basis_crosswalk_registry: dict[str, Any],
    route_coverage_registry: dict[str, Any],
    stage_registry: dict[str, Any],
    agent_registry: dict[str, Any],
    appendix_ledger: dict[str, Any],
    integration_manifest: dict[str, Any],
) -> dict[str, str]:
    counts = integration_manifest["counts"]
    stage_rows = [
        [
            stage["label"],
            str(stage_registry.get("stage_crosswalk", {}).get(stage["stage_id"], {}).get("count", 0)),
            ", ".join(list(stage_registry.get("stage_crosswalk", {}).get(stage["stage_id"], {}).get("target_system_distribution", {}).keys())[:3]) or "-",
            ", ".join(list(stage_registry.get("stage_crosswalk", {}).get(stage["stage_id"], {}).get("anchor_distribution", {}).keys())[:3]) or "-",
        ]
        for stage in stage_registry.get("stages", [])
    ]
    family_rows = [
        [
            FAMILY_LABELS.get(note["family_id"], note["family_id"]),
            note.get("primary_hemisphere", ""),
            note.get("basis_role_id", ""),
            note.get("reassessment_window", ""),
        ]
        for note in agent_registry.get("family_notes", [])
    ]
    basis_rows = [
        [
            note.get("basis_role_id", ""),
            note.get("family_id", ""),
            note.get("primary_hemisphere", ""),
            note.get("reassessment_window", ""),
        ]
        for note in agent_registry.get("basis_role_notes", [])
    ]
    weak_rows = [
        [
            row["record_id"],
            f"{row.get('anchor_confidence', 0.0):.2f}",
            normalize_path(row.get("relative_path", "")),
        ]
        for row in basis_crosswalk_registry.get("weak_or_uncovered_rows", [])[:16]
    ]
    quarantine_rows = [
        [
            row["record_id"],
            ", ".join(row.get("appendix_support", [])),
            row.get("governance_reason", ""),
            normalize_path(row.get("relative_path", "")),
        ]
        for row in appendix_ledger.get("rows", [])
        if row.get("quarantine_required") or row.get("replay_required")
    ][:16]
    return {
        "full_corpus_integration_index": f"""# Full-Corpus Integration Index

Docs gate: `{integration_manifest['docs_gate_status']}`
Control slice records: `{integration_manifest['scope']['phase_1_control_slice_records']}`
Merged canonical records: `{counts['merged_canonical_records']}`
Live atlas records: `{counts['live_atlas_records']}`
Archive atlas records: `{counts['archive_atlas_records']}`

## Outputs

- authority registry: `{integration_manifest['outputs']['authority_registry']}`
- basis crosswalk registry: `{integration_manifest['outputs']['basis_crosswalk_registry']}`
- route coverage registry: `{integration_manifest['outputs']['route_coverage_registry']}`
- awakening stage registry: `{integration_manifest['outputs']['awakening_stage_registry']}`
- awakening agent transition registry: `{integration_manifest['outputs']['awakening_agent_transition_registry']}`
- appendix governance ledger: `{integration_manifest['outputs']['appendix_governance_ledger']}`
- integration manifest: `{integration_manifest['outputs']['integration_manifest']}`
""",
        "full_corpus_authority_receipt": f"""# Full-Corpus Authority Receipt

Docs gate: `{integration_manifest['docs_gate_status']}`

{markdown_table(
    ['Scope', 'Count'],
    [
        ['Live Atlas', str(counts['live_atlas_records'])],
        ['Archive Atlas', str(counts['archive_atlas_records'])],
        ['Merged Canonical', str(counts['merged_canonical_records'])],
        ['Live Only', str(counts['live_only_records'])],
        ['Archive Only', str(counts['archive_only_records'])],
        ['Both', str(counts['both_scope_records'])],
        ['Witness Only', str(counts['witness_only_records'])],
    ],
)}

## Representative Records

{markdown_table(['Record', 'Stage', 'Family', 'Primary System', 'Path'], build_record_locator_lines(authority_registry.get('records', []), 12))}
""",
        "full_corpus_basis_crosswalk": f"""# Full-Corpus Basis Crosswalk

Docs gate: `{integration_manifest['docs_gate_status']}`
Weak or uncovered rows: `{len(basis_crosswalk_registry.get('weak_or_uncovered_rows', []))}`

{markdown_table(
    ['Anchor', 'Count'],
    [[anchor_id, str(count)] for anchor_id, count in list(basis_crosswalk_registry.get('anchor_distribution', {}).items())[:16]],
)}

## Weak Coverage

{markdown_table(['Record', 'Anchor Confidence', 'Path'], weak_rows)}
""",
        "full_corpus_route_coverage": f"""# Full-Corpus Route Coverage

Docs gate: `{integration_manifest['docs_gate_status']}`
Complete route rows: `{route_coverage_registry.get('complete_count', 0)}`
GC0 membership edges: `{route_coverage_registry.get('gc0_edge_count', 0)}`

## Primary Target Systems

{markdown_table(
    ['System', 'Count'],
    [[system, str(count)] for system, count in list(route_coverage_registry.get('primary_target_distribution', {}).items())[:16]],
)}

## Secondary Target Systems

{markdown_table(
    ['System', 'Count'],
    [[system, str(count)] for system, count in list(route_coverage_registry.get('secondary_target_distribution', {}).items())[:16]],
)}
""",
        "awakening_stage_atlas": f"""# Awakening Stage Atlas

Docs gate: `{integration_manifest['docs_gate_status']}`

{markdown_table(['Stage', 'Count', 'Top Systems', 'Top Anchors'], stage_rows)}
""",
        "awakening_family_agent_atlas": f"""# Awakening Family-Agent Atlas

Docs gate: `{integration_manifest['docs_gate_status']}`

{markdown_table(['Family', 'Hemisphere', 'Basis Overlay', 'Reassess'], family_rows)}
""",
        "awakening_basis_agent_atlas": f"""# Awakening Basis-Agent Atlas

Docs gate: `{integration_manifest['docs_gate_status']}`

{markdown_table(['Basis Role', 'Dominant Family', 'Hemisphere', 'Reassess'], basis_rows)}
""",
        "awakening_transition_playbooks": f"""# Awakening Transition Playbooks

Docs gate: `{integration_manifest['docs_gate_status']}`

## Handoff Modes

{markdown_table(
    ['Mode', 'Evidence Count', 'Reassess'],
    [[note['note_id'], str(len(note.get('evidence_ids', []))), note.get('reassessment_window', '')] for note in agent_registry.get('handoff_notes', [])],
)}

## Replay and Quarantine Priority

{markdown_table(['Record', 'Appendix', 'Reason', 'Path'], quarantine_rows)}
""",
    }


def render_deeper_receipt(integration_manifest: dict[str, Any], stage_registry: dict[str, Any]) -> str:
    counts = integration_manifest["counts"]
    return f"""# Full-Corpus Integration Receipt

Docs gate: `{integration_manifest['docs_gate_status']}`

- merged canonical records: `{counts['merged_canonical_records']}`
- assigned awakening stages: `{stage_registry.get('assigned_count', 0)}`
- stage abstentions: `{stage_registry.get('abstention_count', 0)}`
- control slice records: `{integration_manifest['scope']['phase_1_control_slice_records']}`

## Canonical Outputs

- authority registry: `{FULL_CORPUS_AUTHORITY_REGISTRY_PATH}`
- basis crosswalk registry: `{FULL_CORPUS_BASIS_CROSSWALK_REGISTRY_PATH}`
- route coverage registry: `{FULL_CORPUS_ROUTE_COVERAGE_REGISTRY_PATH}`
- awakening stage registry: `{FULL_CORPUS_AWAKENING_STAGE_REGISTRY_PATH}`
- awakening agent transition registry: `{FULL_CORPUS_AWAKENING_AGENT_TRANSITION_REGISTRY_PATH}`
- appendix governance ledger: `{FULL_CORPUS_APPENDIX_GOVERNANCE_LEDGER_PATH}`
- integration manifest: `{FULL_CORPUS_INTEGRATION_MANIFEST_PATH}`
"""


def build_full_corpus_integration_payloads(
    *,
    control_manifest: dict[str, Any],
    control_records: list[dict[str, Any]],
    docs_gate_status: str,
    aqm_lane: dict[str, Any],
    anchors: list[BasisAnchor],
    station_map: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    live_atlas = load_optional_json(CORPUS_ATLAS_PATH)
    archive_atlas = load_optional_json(ARCHIVE_ATLAS_PATH)
    archive_manifest = load_optional_json(ARCHIVE_MANIFEST_PATH)
    merged_records = deduplicate_merged_records(
        list(live_atlas.get("records", [])),
        list(archive_atlas.get("records", [])),
    )
    control_by_sha, control_by_path = build_control_lookups(control_records)
    projected_records = [
        project_full_record(
            record=record,
            control_match=control_match_for_record(record, control_by_sha, control_by_path),
            docs_gate_status=docs_gate_status,
            station_map=station_map,
            anchors=anchors,
            aqm_lane=aqm_lane,
        )
        for record in merged_records
    ]
    projected_records.sort(key=lambda item: normalize_path(item.get("relative_path", "")).lower())
    projected_records, route_registry, direct_edge_registry, _, route_manifest = build_dual_route_payloads(
        records=projected_records,
        station_map=station_map,
        docs_gate_status=docs_gate_status,
    )
    anchor_map = {anchor.anchor_id: anchor for anchor in anchors}
    for record in projected_records:
        record["symmetry_membership"] = symmetry_membership(
            record,
            record.get("basis_anchor_ids", []),
            anchor_map,
        )
    appendix_ledger = build_appendix_governance_ledger(projected_records, docs_gate_status)
    route_coverage_registry = build_route_saturation_registry(
        projected_records,
        route_registry,
        direct_edge_registry,
        docs_gate_status,
    )
    basis_crosswalk_registry = build_basis_crosswalk_registry(projected_records, docs_gate_status)
    stage_registry = build_stage_registry(projected_records, anchor_map, docs_gate_status)
    agent_registry = build_agent_transition_registry(
        projected_records,
        stage_registry,
        anchor_map,
        docs_gate_status,
    )
    authority_registry = build_authority_registry(
        projected_records,
        live_atlas,
        archive_atlas,
        docs_gate_status,
    )
    integration_manifest = build_integration_manifest(
        control_manifest=control_manifest,
        live_atlas=live_atlas,
        archive_atlas=archive_atlas,
        archive_manifest=archive_manifest,
        authority_registry=authority_registry,
        basis_crosswalk_registry=basis_crosswalk_registry,
        route_coverage_registry=route_coverage_registry,
        stage_registry=stage_registry,
        agent_registry=agent_registry,
        appendix_ledger=appendix_ledger,
        docs_gate_status=docs_gate_status,
        aqm_lane=aqm_lane,
    )
    return {
        "authority_registry": authority_registry,
        "basis_crosswalk_registry": basis_crosswalk_registry,
        "route_coverage_registry": route_coverage_registry,
        "awakening_stage_registry": stage_registry,
        "awakening_agent_transition_registry": agent_registry,
        "appendix_governance_ledger": appendix_ledger,
        "integration_manifest": integration_manifest,
        "markdown_pages": render_markdown_pages(
            authority_registry=authority_registry,
            basis_crosswalk_registry=basis_crosswalk_registry,
            route_coverage_registry=route_coverage_registry,
            stage_registry=stage_registry,
            agent_registry=agent_registry,
            appendix_ledger=appendix_ledger,
            integration_manifest=integration_manifest,
        ),
        "deeper_receipt": render_deeper_receipt(integration_manifest, stage_registry),
        "route_manifest": route_manifest,
    }
