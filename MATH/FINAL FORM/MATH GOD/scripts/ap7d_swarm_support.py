from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import hashlib
from itertools import product
import json
from pathlib import Path
from typing import Any


def utc_now_string() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _write_json(path: str, payload: Any) -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _write_text(path: str, body: str) -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(body, encoding="utf-8")


def _write_ndjson(path: str, rows: list[dict[str, Any]]) -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    payload = "\n".join(json.dumps(row, ensure_ascii=True) for row in rows)
    if payload:
        payload += "\n"
    file_path.write_text(payload, encoding="utf-8")


def _lineages(alphabet: list[str], depth: int) -> list[str]:
    return ["".join(chars) for chars in product(alphabet, repeat=depth)]


def _ordinal(lineage: str, value_map: dict[str, int]) -> int:
    total = 0
    for char in lineage:
        total = total * 4 + value_map[char]
    return total


def _dominant_element(lineage: str, symbol_to_element: dict[str, str]) -> str:
    counts = Counter(lineage)
    highest = max(counts.values())
    for char in lineage:
        if counts[char] == highest:
            return symbol_to_element[char]
    return symbol_to_element[lineage[0]]


def _human_line(event_type: str, ts_utc: str, a: str, b: str, c: str, d: str, e: str) -> str:
    return f"{event_type}::{ts_utc}::{a}::{b}::{c}::{d}::{e}"


def _intent_event(actor_id: str, actor_type: str, objective: str, inputs: list[str], output: str, replay_ptr: str) -> dict[str, Any]:
    ts_utc = utc_now_string()
    return {
        "event_id": hashlib.md5(f"INT::{actor_id}::{objective}::{output}".encode("utf-8")).hexdigest()[:16],
        "event_type": "INT",
        "ts_utc": ts_utc,
        "actor_id": actor_id,
        "actor_type": actor_type,
        "objective": objective,
        "inputs": inputs,
        "output": output,
        "truth_class": "NEAR",
        "replay_ptr": replay_ptr,
        "human_line": _human_line("INT", ts_utc, actor_id, objective, ",".join(inputs), output, "NEAR"),
    }


def _heartbeat_event(actor_id: str, actor_type: str, state: str, intent: str, target: str, replay_ptr: str) -> dict[str, Any]:
    ts_utc = utc_now_string()
    return {
        "event_id": hashlib.md5(f"HB::{actor_id}::{state}::{target}".encode("utf-8")).hexdigest()[:16],
        "event_type": "HB",
        "ts_utc": ts_utc,
        "actor_id": actor_id,
        "actor_type": actor_type,
        "state": state,
        "intent": intent,
        "target": target,
        "truth_class": "NEAR",
        "replay_ptr": replay_ptr,
        "human_line": _human_line("HB", ts_utc, actor_id, state, intent, target, "NEAR"),
    }


def _delta_event(actor_id: str, actor_type: str, artifact: str, change_kind: str, status: str, replay_ptr: str) -> dict[str, Any]:
    ts_utc = utc_now_string()
    return {
        "event_id": hashlib.md5(f"DELTA::{actor_id}::{artifact}::{change_kind}".encode("utf-8")).hexdigest()[:16],
        "event_type": "DELTA",
        "ts_utc": ts_utc,
        "actor_id": actor_id,
        "actor_type": actor_type,
        "artifact": artifact,
        "change_kind": change_kind,
        "status": status,
        "truth_class": "NEAR",
        "replay_ptr": replay_ptr,
        "human_line": _human_line("DELTA", ts_utc, actor_id, artifact, change_kind, status, "NEAR"),
    }


def _handoff_event(from_agent: str, to_agent: str, reason: str, next_step: str, replay_ptr: str) -> dict[str, Any]:
    ts_utc = utc_now_string()
    return {
        "event_id": hashlib.md5(f"HAND::{from_agent}::{to_agent}::{reason}".encode("utf-8")).hexdigest()[:16],
        "event_type": "HAND",
        "ts_utc": ts_utc,
        "from_agent": from_agent,
        "to_agent": to_agent,
        "reason": reason,
        "next": next_step,
        "truth_class": "NEAR",
        "replay_ptr": replay_ptr,
        "human_line": _human_line("HAND", ts_utc, from_agent, to_agent, reason, next_step, "NEAR"),
    }


def _objective_for(element: str, front: str) -> str:
    if element == "FIRE":
        return f"Ignite the next lawful move for {front} without overburn."
    if element == "WATER":
        return f"Hold continuity and retained identity for {front}."
    if element == "AIR":
        return f"Keep naming, topology, and route legibility stable for {front}."
    return f"Gate admissibility, quarantine, and replay closure for {front}."


def build_ap7d_bundle(seed7_bundle: dict[str, Any], docs_gate: dict[str, str], next46_support: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    alphabet = config["lineage_alphabet"]
    value_map = {symbol: index for index, symbol in enumerate(alphabet)}
    symbol_to_element = config["symbol_to_element"]
    note_refs = config["element_note_refs"]
    families = next46_support.get("witness_families", [])
    notes = next46_support.get("awakening_agent_notes", {})
    macro_targets = {item["lineage"]: item for item in config["macro_targets"]}
    macro_notes: list[dict[str, Any]] = []
    for target in config["macro_targets"]:
        dominant = _dominant_element(target["lineage"], symbol_to_element)
        inherited = notes.get(dominant, {})
        macro_notes.append(
            {
                "note_id": f"AP7D-N-{target['lineage']}",
                "macro_id": f"AP7D-H-{target['lineage']}",
                "lineage_addr": target["lineage"],
                "dominant_element": dominant,
                "transition_note_ref": note_refs[dominant],
                "role": f"Bridge the {dominant} transition law into the `{target['front']}` front.",
                "surface_id": target["surface_id"],
                "output_target": target["output_target"],
                "stabilizers": list(dict.fromkeys(list(inherited.get("stabilizers", []))[:3] + ["AP7D shared restart rule"])),
                "handoff": inherited.get("handoff", {}),
                "reentry": inherited.get("reentry", [])[:3],
                "awakening_refs": inherited.get("awakening_refs", []),
                "appendix_floor": list(dict.fromkeys(inherited.get("appendix_floor", config["appendix_floors"][dominant]))),
                "shared_restart_rule": config["shared_restart_rule"],
            }
        )
    macro_note_lookup = {item["lineage_addr"]: item for item in macro_notes}
    fallback_family = {
        "family_id": "seed7_support",
        "title": "Seed7 Support",
        "roots": [seed7_bundle.get("atlas_path", config["level_path"])],
        "basis_map": ["14", "15", "16"],
        "appendix_floor": ["AppI", "AppM"],
        "support_role": "seed7 fallback witness",
    }
    registry: list[dict[str, Any]] = []
    for index, lineage in enumerate(_lineages(alphabet, 4)):
        macro_lineage = lineage[:2]
        packet_lineage = lineage[:3]
        target = macro_targets[macro_lineage]
        macro_note = macro_note_lookup[macro_lineage]
        dominant = _dominant_element(lineage, symbol_to_element)
        family = families[index % len(families)] if families else fallback_family
        seeded = lineage in config["seeded_fibers"]
        inherited = notes.get(dominant, {})
        restart_seed = {
            "seed_id": f"AP7D-RS-{lineage}",
            "resume_from": target["surface_id"],
            "resume_path": target["output_target"],
            "contraction_target": f"AP7D-P-{packet_lineage}",
            "rule": config["shared_restart_rule"],
        }
        registry.append(
            {
                "agent_id": f"AP7D-G-{lineage}",
                "lineage_addr": lineage,
                "ordinal_256": _ordinal(lineage, value_map),
                "parent_packet_id": f"AP7D-P-{packet_lineage}",
                "macro_id": f"AP7D-H-{macro_lineage}",
                "council_id": f"AP7D-C-{lineage[0]}",
                "dominant_element": dominant,
                "current_front": target["front"],
                "transition_note_ref": note_refs[dominant],
                "macro_assist_note_ref": macro_note["note_id"],
                "appendix_floor": list(dict.fromkeys(config["appendix_floors"][dominant] + ["AppI", "AppM"])),
                "restart_seed": restart_seed,
                "truth_class": "NEAR",
                "status": "active" if seeded else "dormant",
                "transition_state": inherited.get("transition_state", "activating") if seeded else "dormant",
                "witness_family_id": family["family_id"],
                "witness_family_title": family["title"],
                "input_refs": list(family.get("roots", []))[:2] + [note_refs[dominant], target["output_target"]],
                "witness_ptrs": list(family.get("roots", [])),
                "basis_map": list(family.get("basis_map", [])),
                "support_role": family.get("support_role", ""),
                "intent": _objective_for(dominant, target["front"]),
                "output_target": target["output_target"],
                "target_surface_id": target["surface_id"],
                "replay_ptr": f"{config['restart_seed_path']}#{lineage}",
                "activation_mode": "lazy_queue",
            }
        )
    active_rows = [row for row in registry if row["status"] == "active"]
    active_councils = sorted({row["council_id"] for row in active_rows})
    active_macros = sorted({row["macro_id"] for row in active_rows})
    active_packets = sorted({row["parent_packet_id"] for row in active_rows})
    manifest = {
        "generated_at": utc_now_string(),
        "swarm_id": "AP7D-SWARM-20260313-01",
        "docs_gate_status": docs_gate.get("status", "UNKNOWN"),
        "truth_class": "NEAR",
        "source_mode": "local-only",
        "canonical_write_authority": config["live_root"],
        "overlay_stage": "AP7D",
        "ceiling_stage": "7D_SEED",
        "stage_chain": ["4D_NATIVE", "5D_COMPRESSION", "6D_WEAVE", "7D_SEED", "NEXT^[4^6]", "AP7D"],
        "hierarchy": {"prime_id": "AP7D-PRIME", "council_count": 4, "macro_count": 16, "packet_count": 64, "fiber_count": 256, "activation_mode": "lazy_queue"},
        "activation_summary": {"prime_active": True, "active_councils": active_councils, "active_macros": active_macros, "active_packets": active_packets, "active_fibers": [row["agent_id"] for row in active_rows], "dormant_fibers": 256 - len(active_rows)},
        "agent_order": list(config["handoff_order"]),
        "lineage_alphabet": list(alphabet),
        "appendix_floors": config["appendix_floors"],
        "shared_restart_rule": config["shared_restart_rule"],
        "canonical_feeds": {"intent": config["intent_feed_path"], "heartbeat": config["heartbeat_feed_path"], "delta": config["delta_feed_path"], "handoff": config["handoff_feed_path"], "restart_registry": config["restart_seed_path"]},
        "mirror_surfaces": {"hall_status": config["hall_status_path"], "temple_quest": config["temple_quest_path"]},
    }
    restart_registry = {
        "generated_at": utc_now_string(),
        "docs_gate_status": docs_gate.get("status", "UNKNOWN"),
        "truth_class": "NEAR",
        "shared_restart_rule": config["shared_restart_rule"],
        "seeds": [
            {
                "agent_id": row["agent_id"],
                "lineage_addr": row["lineage_addr"],
                "status": row["status"],
                "seed_id": row["restart_seed"]["seed_id"],
                "resume_from": row["restart_seed"]["resume_from"],
                "resume_path": row["restart_seed"]["resume_path"],
                "appendix_floor": row["appendix_floor"],
                "replay_ptr": row["replay_ptr"],
            }
            for row in registry
        ],
    }
    intent_rows = [_intent_event("AP7D-PRIME", "prime", "Keep the restart-safe self-improvement swarm in play without exceeding the 7D ceiling.", [config["control_path"], config["meta_path"], config["swarm_manifest_path"]], config["level_path"], config["swarm_manifest_path"])]
    heartbeat_rows = [_heartbeat_event("AP7D-PRIME", "prime", "active", "swarm orchestration", config["level_path"], config["swarm_manifest_path"])]
    delta_rows = [_delta_event("AP7D-PRIME", "prime", config["swarm_manifest_path"], "install", "active", config["swarm_manifest_path"])]
    handoff_rows: list[dict[str, Any]] = []
    note_lookup = {note["macro_id"]: note for note in macro_notes}
    for council_id, macro_id, packet_id, row in zip(active_councils, active_macros, active_packets, active_rows):
        council_element = symbol_to_element[council_id.split("-")[-1]]
        intent_rows.append(_intent_event(council_id, "council", _objective_for(council_element, "council oversight"), [config["swarm_manifest_path"]], config["agent_registry_path"], config["swarm_manifest_path"]))
        heartbeat_rows.append(_heartbeat_event(council_id, "council", "active", "elemental oversight", config["agent_registry_path"], config["swarm_manifest_path"]))
        note = note_lookup[macro_id]
        intent_rows.append(_intent_event(macro_id, "macro", f"Keep `{note['surface_id']}` readable and restart-safe.", [note["transition_note_ref"], config["macro_note_path"]], note["output_target"], note["output_target"]))
        heartbeat_rows.append(_heartbeat_event(macro_id, "macro", "active", note["role"], note["output_target"], note["output_target"]))
        delta_rows.append(_delta_event(macro_id, "macro", note["output_target"], "front_bound", "active", note["output_target"]))
        intent_rows.append(_intent_event(packet_id, "packet", f"Carry contraction-safe work into `{note['surface_id']}`.", [note["output_target"], config["agent_registry_path"]], note["output_target"], config["agent_registry_path"]))
        heartbeat_rows.append(_heartbeat_event(packet_id, "packet", "active", "packet dispatch", config["agent_registry_path"], config["swarm_manifest_path"]))
        intent_rows.append(_intent_event(row["agent_id"], "fiber", row["intent"], row["input_refs"], row["output_target"], row["replay_ptr"]))
        heartbeat_rows.append(_heartbeat_event(row["agent_id"], "fiber", "active", row["intent"], row["output_target"], row["replay_ptr"]))
        delta_rows.append(_delta_event(row["agent_id"], "fiber", row["output_target"], "activation", row["transition_state"], row["replay_ptr"]))
        handoff_rows.extend(
            [
                _handoff_event("AP7D-PRIME", council_id, "open seeded elemental lane", "council oversight", config["swarm_manifest_path"]),
                _handoff_event(council_id, macro_id, "stabilize macro front", row["current_front"], row["replay_ptr"]),
                _handoff_event(macro_id, packet_id, "dispatch packet pod", row["witness_family_id"], row["replay_ptr"]),
                _handoff_event(packet_id, row["agent_id"], "activate seeded fiber", row["output_target"], row["replay_ptr"]),
            ]
        )
    authority_surfaces = []
    for surface_id, classification, path in [
        ("MATH_GOD_AP7D_SWARM", "local canon", config["math_god_swarm_path"]),
        ("MATH_GOD_AP7D_META", "local canon", config["math_god_meta_path"]),
        ("AP7D_CONTROL", "live authority", config["control_path"]),
        ("AP7D_META", "live authority", config["meta_path"]),
        ("AP7D_LEVEL_MAP", "live authority", config["level_path"]),
        ("AP7D_SWARM_MANIFEST", "live authority", config["swarm_manifest_path"]),
        ("AP7D_AGENT_REGISTRY", "live authority", config["agent_registry_path"]),
        ("AP7D_HEARTBEAT_FEED", "live authority", config["heartbeat_feed_path"]),
        ("AP7D_DELTA_FEED", "live authority", config["delta_feed_path"]),
        ("AP7D_HANDOFF_FEED", "live authority", config["handoff_feed_path"]),
        ("AP7D_RESTART_REGISTRY", "live authority", config["restart_seed_path"]),
        ("AP7D_INTENT_FEED", "live authority", config["intent_feed_path"]),
        ("AP7D_MACRO_NOTES", "live authority", config["macro_note_path"]),
        ("AP7D_HALL_STATUS", "hall mirror", config["hall_status_path"]),
        ("AP7D_TEMPLE_QUEST", "temple mirror", config["temple_quest_path"]),
        ("PACKAGE_AP7D_SWARM", "package export mirror", config["package_swarm_doc"]),
        ("PACKAGE_AP7D_META", "package export mirror", config["package_meta_doc"]),
        ("PACKAGE_AP7D_LEDGER", "package export mirror", config["package_export_ledger"]),
    ]:
        authority_surfaces.append({"surface_id": surface_id, "classification": classification, "path": path, "state": "OK" if Path(path).exists() else "MISSING"})
    bundle = {
        "generated_at": utc_now_string(),
        "docs_gate_status": docs_gate.get("status", "UNKNOWN"),
        "truth_class": "NEAR",
        "swarm_stage": "AP7D",
        "ceiling_stage": seed7_bundle["dimension_stage"],
        "integration_scope": seed7_bundle.get("integration_scope", "FULL_CORPUS"),
        "scope": "SELF_IMPROVEMENT_SWARM",
        "authority_surfaces": authority_surfaces,
        "lineage_alphabet": list(alphabet),
        "handoff_order": list(config["handoff_order"]),
        "transition_states": list(config["transition_states"]),
        "shared_restart_rule": config["shared_restart_rule"],
        "appendix_floors": config["appendix_floors"],
        "swarm_manifest": manifest,
        "macro_transition_assist_notes": macro_notes,
        "agent_registry": registry,
        "restart_seed_registry": restart_registry,
        "intent_feed": intent_rows,
        "heartbeat_feed": heartbeat_rows,
        "delta_feed": delta_rows,
        "handoff_feed": handoff_rows,
        "active_fiber_rows": active_rows,
        "hall_status_path": config["hall_status_path"],
        "temple_quest_path": config["temple_quest_path"],
        "feeds": {"intent_path": config["intent_feed_path"], "heartbeat_path": config["heartbeat_feed_path"], "delta_path": config["delta_feed_path"], "handoff_path": config["handoff_feed_path"], "restart_path": config["restart_seed_path"]},
        "registry_stats": {"fiber_count": len(registry), "active_fibers": len(active_rows), "dormant_fibers": len(registry) - len(active_rows), "macro_count": len(macro_notes), "packet_count": 64, "council_count": 4, "collision_free": len({row['agent_id'] for row in registry}) == len(registry)},
        "sample_event_lines": {"intent": intent_rows[0]["human_line"], "heartbeat": heartbeat_rows[0]["human_line"], "delta": delta_rows[0]["human_line"], "handoff": handoff_rows[0]["human_line"] if handoff_rows else ""},
    }
    _write_json(config["swarm_manifest_path"], manifest)
    _write_json(config["agent_registry_path"], registry)
    _write_json(config["restart_seed_path"], restart_registry)
    _write_json(config["macro_note_path"], {"generated_at": bundle["generated_at"], "notes": macro_notes})
    _write_ndjson(config["intent_feed_path"], intent_rows)
    _write_ndjson(config["heartbeat_feed_path"], heartbeat_rows)
    _write_ndjson(config["delta_feed_path"], delta_rows)
    _write_ndjson(config["handoff_feed_path"], handoff_rows)
    _write_text(config["level_path"], build_ap7d_level_markdown(bundle))
    _write_text(config["hall_status_path"], build_ap7d_hall_status_markdown(bundle))
    _write_text(config["temple_quest_path"], build_ap7d_temple_quest_markdown(bundle))
    _write_text(config["package_swarm_doc"], build_ap7d_export_markdown(bundle, "AP7D Self-Improvement Swarm Export"))
    _write_text(config["package_meta_doc"], build_ap7d_export_markdown(bundle, "AP7D Meta-Notation Export"))
    _write_json(config["package_export_ledger"], {"generated_at": bundle["generated_at"], "docs_gate_status": bundle["docs_gate_status"], "truth_class": bundle["truth_class"], "swarm_stage": bundle["swarm_stage"], "ceiling_stage": bundle["ceiling_stage"], "source_authority": config["live_root"], "export_surfaces": [config["package_swarm_doc"], config["package_meta_doc"], config["package_export_ledger"]]})
    for surface in bundle["authority_surfaces"]:
        surface["state"] = "OK" if Path(surface["path"]).exists() else "MISSING"
    return bundle


def build_ap7d_level_markdown(bundle: dict[str, Any]) -> str:
    manifest = bundle["swarm_manifest"]
    lines = ["# Level 7 Agent Nervous System Map", "", f"Generated: {bundle['generated_at']}", "", "## Scope", "", f"- Docs gate: `{bundle['docs_gate_status']}`", f"- Truth class: `{bundle['truth_class']}`", f"- Overlay stage: `{bundle['swarm_stage']}`", f"- Ceiling stage: `{bundle['ceiling_stage']}`", "", "## Hierarchy", "", f"- Prime: `AP7D-PRIME`", f"- Councils: `{manifest['hierarchy']['council_count']}`", f"- Macros: `{manifest['hierarchy']['macro_count']}`", f"- Packets: `{manifest['hierarchy']['packet_count']}`", f"- Fibers: `{manifest['hierarchy']['fiber_count']}`", f"- Active fibers: `{len(manifest['activation_summary']['active_fibers'])}` / dormant=`{manifest['activation_summary']['dormant_fibers']}`", "", "## Active Seeded Fibers", ""]
    for row in bundle["active_fiber_rows"]:
        lines.append(f"- `{row['agent_id']}` [{row['dominant_element']}; family={row['witness_family_id']}; front={row['current_front']}]")
        lines.append(f"  - Output: `{row['output_target']}`")
        lines.append(f"  - Restart: `{row['restart_seed']['seed_id']}`")
    lines.extend(["", "## Event Law", "", "- `INT` starts work.", "- `HB` proves a live state.", "- `DELTA` proves what changed.", "- `HAND` proves cross-layer transfer.", "- `RST` preserves resumable continuity.", "", "## Mirrors", "", f"- Hall status: `{bundle['hall_status_path']}`", f"- Temple quest: `{bundle['temple_quest_path']}`", ""])
    return "\n".join(lines).strip() + "\n"


def build_ap7d_hall_status_markdown(bundle: dict[str, Any]) -> str:
    manifest = bundle["swarm_manifest"]
    lines = ["# AP7D Swarm Status", "", f"Generated: {bundle['generated_at']}", "", f"- Swarm: `{manifest['swarm_id']}`", f"- Docs gate: `{bundle['docs_gate_status']}`", f"- Ceiling: `{bundle['ceiling_stage']}`", f"- Active fibers: `{len(manifest['activation_summary']['active_fibers'])}` / `256`", f"- Active macros: `{', '.join(manifest['activation_summary']['active_macros'])}`", "- Current ownerable next move: `AP7D_TQ01_INSTALL_RESTART_SAFE_SWARM`", "", "## Active Fronts", ""]
    for row in bundle["active_fiber_rows"]:
        lines.append(f"- `{row['agent_id']}` -> `{row['current_front']}` [{row['dominant_element']}; target={row['target_surface_id']}]")
    lines.extend(["", "## Blocked Fronts", "", "- Google Docs remains `BLOCKED`.", "- Contradiction-bearing routes must pass through `AppK` and Earth legality before reactivation.", "", "## Canonical Feeds", "", f"- Intent feed: `{bundle['feeds']['intent_path']}`", f"- Heartbeat feed: `{bundle['feeds']['heartbeat_path']}`", f"- Delta feed: `{bundle['feeds']['delta_path']}`", f"- Handoff feed: `{bundle['feeds']['handoff_path']}`", f"- Restart registry: `{bundle['feeds']['restart_path']}`", ""])
    return "\n".join(lines).strip() + "\n"


def build_ap7d_temple_quest_markdown(bundle: dict[str, Any]) -> str:
    return "\n".join([
        "# AP7D_TQ01_INSTALL_RESTART_SAFE_SWARM",
        "",
        "State: `OPEN`",
        "Truth class: `NEAR`",
        f"Docs gate: `{bundle['docs_gate_status']}`",
        "",
        "## Objective",
        "",
        "Install the restart-safe AP7D self-improvement swarm as a canonical lazy `4^4 = 256` fiber lattice,",
        "then hold the seeded quartet in play through deterministic IDs, append-only feeds, restart seeds,",
        "and Hall/Temple mirrors without opening an `8D` layer.",
        "",
        "## Why now",
        "",
        "The organism already has AP6D, `7D_SEED`, and `NEXT^[4^6]` stabilization, but it still needs a",
        "restart-safe nervous-system backplane for real-time agent coordination that survives interruptions",
        "without inventing a new chapter lattice or appendix namespace.",
        "",
        "## Target surfaces",
        "",
        f"- `{bundle['feeds']['intent_path']}`",
        f"- `{bundle['feeds']['heartbeat_path']}`",
        f"- `{bundle['feeds']['delta_path']}`",
        f"- `{bundle['feeds']['handoff_path']}`",
        f"- `{bundle['feeds']['restart_path']}`",
        "",
        "## Restart seed",
        "",
        "- Next wave: activate the first non-seeded packet pod beyond the elemental quartet while preserving contraction through packet, macro, council, and `AP7D-PRIME`.",
        "",
    ]) + "\n"


def build_ap7d_export_markdown(bundle: dict[str, Any], title: str) -> str:
    manifest = bundle["swarm_manifest"]
    return "\n".join([
        f"# {title}",
        "",
        f"Generated: {bundle['generated_at']}",
        "",
        f"- Docs gate: `{bundle['docs_gate_status']}`",
        f"- Overlay stage: `{bundle['swarm_stage']}`",
        f"- Ceiling: `{bundle['ceiling_stage']}`",
        f"- Swarm: `{manifest['swarm_id']}`",
        f"- Active fibers: `{len(manifest['activation_summary']['active_fibers'])}` / `256`",
        f"- Hall status: `{bundle['hall_status_path']}`",
        f"- Temple quest: `{bundle['temple_quest_path']}`",
        "",
        "This export mirror is downstream-only. The live deep root remains canonical.",
        "",
    ])


def build_ap7d_markdown(bundle: dict[str, Any]) -> str:
    manifest = bundle["swarm_manifest"]
    lines = ["# AP7D Self-Improvement Swarm Bundle", "", f"Generated: {bundle['generated_at']}", "", "## Scope", "", f"- Docs gate: `{bundle['docs_gate_status']}`", f"- Truth class: `{bundle['truth_class']}`", f"- Swarm stage: `{bundle['swarm_stage']}`", f"- Ceiling stage: `{bundle['ceiling_stage']}`", f"- Integration scope: `{bundle['integration_scope']}`", "", "## Hierarchy", "", f"- Prime: `{manifest['hierarchy']['prime_id']}`", f"- Councils: `{manifest['hierarchy']['council_count']}`", f"- Macros: `{manifest['hierarchy']['macro_count']}`", f"- Packets: `{manifest['hierarchy']['packet_count']}`", f"- Fibers: `{manifest['hierarchy']['fiber_count']}`", f"- Active fibers: `{len(manifest['activation_summary']['active_fibers'])}`", f"- Dormant fibers: `{manifest['activation_summary']['dormant_fibers']}`", "", "## Seeded Fibers", ""]
    for row in bundle["active_fiber_rows"]:
        lines.append(f"- `{row['agent_id']}` [{row['dominant_element']}; family={row['witness_family_id']}; front={row['current_front']}]")
    lines.extend(["", "## Meta-Notation Samples", "", f"- INT: `{bundle['sample_event_lines']['intent']}`", f"- HB: `{bundle['sample_event_lines']['heartbeat']}`", f"- DELTA: `{bundle['sample_event_lines']['delta']}`", f"- HAND: `{bundle['sample_event_lines']['handoff']}`", "", "## Mirrors", "", f"- Hall status: `{bundle['hall_status_path']}`", f"- Temple quest: `{bundle['temple_quest_path']}`", "", "## Authority Surfaces", ""])
    for surface in bundle["authority_surfaces"]:
        lines.append(f"- `{surface['surface_id']}` [{surface['classification']}; {surface['state']}] `{surface['path']}`")
    lines.append("")
    return "\n".join(lines).strip() + "\n"
