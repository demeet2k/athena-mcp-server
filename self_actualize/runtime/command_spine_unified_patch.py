from __future__ import annotations

import hashlib
import json
import math
import subprocess
import tempfile
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def bootstrap_command_membrane(namespace: dict[str, Any]) -> None:
    CommandMembraneService = namespace["CommandMembraneService"]
    CommandEventPacketV2 = namespace["CommandEventPacketV2"]
    CommandRouteDecisionV2 = namespace["CommandRouteDecisionV2"]
    CommandClaimLeaseV1 = namespace["CommandClaimLeaseV1"]
    CommandRewardStateV2 = namespace["CommandRewardStateV2"]
    CommandVerificationStateV2 = namespace["CommandVerificationStateV2"]
    CommandPheromoneStateV2 = namespace["CommandPheromoneStateV2"]
    swarm_board = namespace["swarm_board"]
    parse_iso = namespace["parse_iso"]
    utc_now = namespace["utc_now"]
    rel = namespace["rel"]
    read_json = namespace["read_json"]
    write_json = namespace["write_json"]
    write_text = namespace["write_text"]
    patch_markdown_file = namespace["patch_markdown_file"]
    slugify = namespace["slugify"]
    clamp = namespace["clamp"]
    local_rotation_phase = namespace["local_rotation_phase"]
    orbital_phase = namespace["orbital_phase"]
    lunar_phase = namespace["lunar_phase"]
    sidereal_phase = namespace["sidereal_phase"]
    MASTER_AGENTS = namespace["MASTER_AGENTS"]
    ROLE_BY_MASTER = namespace["ROLE_BY_MASTER"]
    ROLE_CONTRIBUTION_SHARES = namespace["ROLE_CONTRIBUTION_SHARES"]
    FIRST_WAVE_WATCHED_SURFACES = namespace["FIRST_WAVE_WATCHED_SURFACES"]
    ACTIVE_RANGE_BY_MASTER = namespace["ACTIVE_RANGE_BY_MASTER"]
    LOCAL_ZONE = namespace["LOCAL_ZONE"]
    ROOT = namespace["ROOT"]
    PUBLIC_COMMAND_STATE_PATH = namespace["PUBLIC_COMMAND_STATE_PATH"]
    HALL_BOARD_PATH = namespace["HALL_BOARD_PATH"]
    TEMPLE_BOARD_PATH = namespace["TEMPLE_BOARD_PATH"]
    ACTIVE_RUN_PATH = namespace["ACTIVE_RUN_PATH"]
    BUILD_QUEUE_PATH = namespace["BUILD_QUEUE_PATH"]
    NEXT_SELF_PROMPT_PATH = namespace["NEXT_SELF_PROMPT_PATH"]
    LP57_PROTOCOL_PATH = namespace["LP57_PROTOCOL_PATH"]
    MARKER_ACTIVE_RUN = namespace["MARKER_ACTIVE_RUN"]
    MARKER_BUILD_QUEUE = namespace["MARKER_BUILD_QUEUE"]
    MARKER_HALL = namespace["MARKER_HALL"]
    MARKER_TEMPLE = namespace["MARKER_TEMPLE"]
    MARKER_NEXT_PROMPT = namespace["MARKER_NEXT_PROMPT"]
    MARKER_LP57_PROTOCOL = namespace["MARKER_LP57_PROTOCOL"]
    COMMAND_HALL_QUEST_ID = namespace["COMMAND_HALL_QUEST_ID"]
    COMMAND_TEMPLE_QUEST_ID = namespace["COMMAND_TEMPLE_QUEST_ID"]
    COMMAND_PROTOCOL_ID_V2 = namespace["COMMAND_PROTOCOL_ID_V2"]
    COMMAND_PACKET_SCHEMA_ID_V2 = namespace["COMMAND_PACKET_SCHEMA_ID_V2"]
    COMMAND_CAPILLARY_LAW_ID_V2 = namespace["COMMAND_CAPILLARY_LAW_ID_V2"]
    COMMAND_REWARD_FIELD_ID_V2 = namespace["COMMAND_REWARD_FIELD_ID_V2"]
    COMMAND_ROUTE_POLICY = namespace["COMMAND_ROUTE_POLICY"]
    JOY_ROUTE_POLICY = COMMAND_ROUTE_POLICY
    JOY_REWARD_POLICY = namespace["JOY_REWARD_POLICY"]
    COMMAND_ROUTE_CLASS = namespace["COMMAND_ROUTE_CLASS"]
    COMMAND_WATCHER_MODE = namespace["COMMAND_WATCHER_MODE"]
    COMMAND_ACTIVE_MEMBRANE = namespace["COMMAND_ACTIVE_MEMBRANE"]
    COMMAND_FEEDER_STACK = namespace["COMMAND_FEEDER_STACK"]
    SEED_A_REF = namespace["SEED_A_REF"]
    SEED_B_REF = namespace["SEED_B_REF"]
    USEFUL_OUTCOME_CLASSES = namespace["USEFUL_OUTCOME_CLASSES"]
    WATCH_SCOPE_LABEL = "first-wave local swarm mesh"
    ACTIVE_SURFACE_LABEL = "LOCAL SWARM MESH"
    CANONICAL_AUTHORITY = "LP57OMEGA / NEXT57"
    SELECTOR_TERMS = [
        "goal_fit",
        "priority",
        "gold_signal",
        "bridge_signal",
        "coord_proximity",
        "freshness",
        "capillary_strength",
        "source_class",
    ]

    def _mirror_write_json(service: Any, canonical_path: Path, legacy_path: Path | None, payload: Any) -> None:
        write_json(canonical_path, payload)
        if legacy_path is not None:
            write_json(legacy_path, payload)

    def _surface_rows(service: Any, source_ids: Any = None) -> list[dict[str, Any]]:
        rows = list(service.selected_surface_rows(source_ids))
        if rows:
            return rows
        return list(service.selected_surface_rows())

    def _watch_roots(rows: list[dict[str, Any]]) -> list[str]:
        ordered: list[str] = []
        seen: set[str] = set()
        for row in rows:
            root = str(row.get("watch_root") or row.get("absolute_path") or "").strip()
            if not root:
                continue
            normalized = str(Path(root).resolve(strict=False))
            if normalized in seen:
                continue
            seen.add(normalized)
            ordered.append(normalized)
        return ordered

    def _fingerprint_seen_within(service: Any, dedupe_entry: dict[str, Any]) -> bool:
        seen_at = str(dedupe_entry.get("seen_at") or "")
        if not seen_at:
            return False
        try:
            delta = service.ms_between(seen_at, utc_now())
        except Exception:
            return False
        return delta <= float(service.config.debounce_ms)

    def _event_rows(service: Any) -> list[dict[str, Any]]:
        return list(service.recent_event_payloads(limit=None))

    def _claim_rows(service: Any) -> list[dict[str, Any]]:
        leases = service.load_leases()
        events_by_id = {row.get("event_id"): row for row in _event_rows(service)}
        rows: list[dict[str, Any]] = []
        for status_name, collection in (("active", leases.get("active", {})), ("history", leases.get("history", []))):
            if isinstance(collection, dict):
                iterable = collection.items()
            else:
                iterable = ((row.get("event_id", ""), row) for row in collection if isinstance(row, dict))
            for event_id, row in iterable:
                packet = events_by_id.get(event_id, {})
                payload = dict(row)
                payload["event_id"] = event_id
                payload["status"] = str(payload.get("status") or status_name)
                payload["source_id"] = str(packet.get("source_id") or "")
                payload["source_class"] = str(packet.get("source_class") or "")
                payload["record_id"] = str(packet.get("record_id") or "")
                payload["relative_path"] = str(packet.get("source_path") or "")
                payload["linked_route_path"] = str((packet.get("route_state") or {}).get("route_path", ""))
                payload["docs_gate_status"] = str(packet.get("docs_gate_status") or service.docs_gate_status()["state"])
                rows.append(payload)
        rows.sort(key=lambda item: (str(item.get("event_id") or ""), str(item.get("claimed_at") or item.get("released_at") or "")))
        return rows

    def _capillary_rows(service: Any) -> list[dict[str, Any]]:
        edges_payload = service.load_edges()
        rows = edges_payload.get("rows")
        edges = edges_payload.get("edges", {})
        if isinstance(rows, list) and isinstance(edges, dict) and len(rows) == len(edges):
            return rows
        if isinstance(rows, list) and not isinstance(edges, dict):
            return rows
        if isinstance(edges, dict):
            return list(edges.values())
        return []

    def _latency_rows(service: Any) -> list[dict[str, Any]]:
        stored = read_json(service.config.latency_record_path, [])
        rows_by_id: dict[str, dict[str, Any]] = {}
        if isinstance(stored, list):
            for row in stored:
                if isinstance(row, dict) and row.get("event_id"):
                    rows_by_id[str(row["event_id"])] = row
        for packet in _event_rows(service):
            event_id = str(packet.get("event_id") or "")
            if not event_id:
                continue
            latency_state = packet.get("latency_state") or {}
            if not latency_state:
                continue
            rows_by_id.setdefault(
                event_id,
                {
                    "event_id": event_id,
                    "source_id": str(packet.get("source_id") or ""),
                    "source_class": str(packet.get("source_class") or ""),
                    "t_detect_ms": float(latency_state.get("detect_latency_ms", latency_state.get("detection_latency_ms", 0.0)) or 0.0),
                    "t_encode_ms": float(latency_state.get("encode_latency_ms", 0.0) or 0.0),
                    "t_route_ms": float(latency_state.get("awareness_latency_ms", 0.0) or 0.0),
                    "t_claim_ms": float(latency_state.get("claim_latency_ms", 0.0) or 0.0),
                    "t_commit_ms": float(latency_state.get("commit_latency_ms", 0.0) or 0.0),
                    "t_sugar_ms": float(latency_state.get("t_sugar_ms", 0.0) or 0.0),
                    "capillary_score": float(latency_state.get("capillary_score", 0.0) or 0.0),
                    "liminal_delta": float(latency_state.get("DeltaTau", latency_state.get("liminal_distance", 0.0)) or 0.0),
                    "liminal_velocity": float(latency_state.get("LiminalVelocity", 0.0) or 0.0),
                    "route_path": str((packet.get("route_state") or {}).get("route_path", "")),
                    "recorded_at": str((packet.get("commit_state") or {}).get("committed_at") or packet.get("emitted_ts") or utc_now()),
                    "docs_gate_status": str(packet.get("docs_gate_status") or service.docs_gate_status()["state"]),
                },
            )
        rows = list(rows_by_id.values())
        rows.sort(key=lambda item: str(item.get("event_id") or ""))
        return rows

    def _event_backlog(service: Any) -> list[dict[str, Any]]:
        return [
            row
            for row in _event_rows(service)
            if str(row.get("status") or "detected") not in {"committed", "reinforced"}
        ]

    def _write_live_registry_pair(service: Any, path_attr: str, payload: Any) -> None:
        canonical_path = getattr(service.config, path_attr)
        legacy_path = getattr(service.config, f"legacy_{path_attr}", None)
        _mirror_write_json(service, canonical_path, legacy_path, payload)

    def _patch_surface_file(service: Any, path: Path, marker: str, body: str) -> None:
        patch_markdown_file(path, marker, body)

    def watched_surface_registry(self: Any, source_ids: Any = None) -> dict[str, Any]:
        requested = {str(source_id) for source_id in source_ids} if source_ids else None
        docs_gate = self.docs_gate_status()["state"]
        rows: list[dict[str, Any]] = []
        for surface in FIRST_WAVE_WATCHED_SURFACES:
            absolute_path = Path(surface["absolute_path"]).resolve(strict=False)
            target_kind = str(surface.get("target_kind") or "file")
            watch_root = absolute_path if target_kind == "directory" else absolute_path.parent
            rows.append(
                {
                    "source_id": str(surface.get("source_id") or ""),
                    "absolute_path": str(absolute_path),
                    "relative_path": rel(absolute_path),
                    "watch_root": str(watch_root.resolve(strict=False)),
                    "watch_root_relative": rel(watch_root),
                    "target_kind": target_kind,
                    "source_class": str(surface.get("source_class") or ""),
                    "watch_scope": WATCH_SCOPE_LABEL,
                    "event_filters": list(surface.get("event_filters") or ("created", "updated", "deleted")),
                    "default_lanes": dict(surface.get("default_lanes") or {"scout": "A1", "router": "A2", "worker": "A3", "archivist": "A4"}),
                    "routing_goal": str(surface.get("routing_goal") or "detect-classify-assign"),
                    "urgency_baseline": float(surface.get("urgency_baseline", 0.90) or 0.90),
                    "coordinate_projection_hints": dict(surface.get("coordinate_projection_hints") or {}),
                    "exists": absolute_path.exists(),
                    "docs_gate_status": docs_gate,
                }
            )
        if requested is not None:
            rows = [row for row in rows if row["source_id"] in requested]
        return {
            "generated_at": utc_now(),
            "protocol_id": COMMAND_PROTOCOL_ID_V2,
            "docs_gate_status": docs_gate,
            "watcher_mode": "event-driven" if self.native_watch_available() else "polling",
            "watch_scope": WATCH_SCOPE_LABEL,
            "source_count": len(rows),
            "rows": rows,
        }

    def selected_surface_rows(self: Any, source_ids: Any = None) -> list[dict[str, Any]]:
        return list(self.watched_surface_registry(source_ids).get("rows", []))

    def current_runtime_truth(self: Any) -> dict[str, Any]:
        bundle = read_json(self.config.hsigma_bundle_path, {})
        truth = bundle.get("current_runtime_truth", {})
        if isinstance(truth, dict) and truth:
            return {
                "canonical_authority": "LP57OMEGA / NEXT57",
                "active_loop": str(truth.get("active_loop") or "L02"),
                "active_family": str(truth.get("active_family") or "A02 self_actualize"),
                "restart_seed": str(truth.get("restart_seed") or "L03 Survey A03 ECOSYSTEM"),
                "visible_caps": truth.get("visible_caps") or {"hall": 8, "temple": 8},
                "active_membrane": COMMAND_ACTIVE_MEMBRANE,
                "feeders": list(COMMAND_FEEDER_STACK),
            }
        return {
            "canonical_authority": "LP57OMEGA / NEXT57",
            "active_loop": "L02",
            "active_family": "A02 self_actualize",
            "restart_seed": "L03 Survey A03 ECOSYSTEM",
            "visible_caps": {"hall": 8, "temple": 8},
            "active_membrane": COMMAND_ACTIVE_MEMBRANE,
            "feeders": list(COMMAND_FEEDER_STACK),
        }

    def metrics(self: Any, surface: str = "command-folder") -> dict[str, Any]:
        del surface
        events = _event_rows(self)
        claims = _claim_rows(self)
        capillary_rows = _capillary_rows(self)
        latency_rows = _latency_rows(self)
        docs_gate = self.docs_gate_status()["state"]
        watched_surface_count = len(_surface_rows(self))
        committed_count = sum(
            1
            for row in events
            if str(row.get("status") or "detected") in {"committed", "reinforced"}
        )
        reinforced_count = sum(
            1 for row in events if str(row.get("status") or "detected") == "reinforced"
        )
        matched_event_count = sum(
            1
            for row in events
            if str(row.get("record_id") or "").strip()
            and str(row.get("match_state") or "") != "fallback_local_anchor"
        )
        fallback_event_count = sum(
            1 for row in events if str(row.get("match_state") or "") == "fallback_local_anchor"
        )
        capillary_counter: dict[str, int] = {}
        for row in capillary_rows:
            vessel = str(
                row.get("vessel_class")
                or row.get("classification")
                or row.get("state_class")
                or row.get("grade")
                or "latent"
            )
            capillary_counter[vessel] = capillary_counter.get(vessel, 0) + 1
        avg_t_sugar = (
            sum(float(row.get("t_sugar_ms", 0.0) or 0.0) for row in latency_rows) / len(latency_rows)
            if latency_rows
            else 0.0
        )
        def _avg(key: str) -> float:
            values = [float(row.get(key, 0.0) or 0.0) for row in latency_rows]
            return round(sum(values) / len(values), 6) if values else 0.0
        tier_counts = {"route": 0, "capillary": 0, "vein": 0}
        top_capillaries = []
        for row in capillary_rows:
            classification = str(
                row.get("classification")
                or row.get("vessel_class")
                or row.get("grade")
                or row.get("state_class")
                or "route"
            )
            if classification not in tier_counts:
                classification = "route"
            tier_counts[classification] += 1
            top_capillaries.append(
                {
                    "edge_id": str(row.get("edge_id") or ""),
                    "edge_strength": float(
                        row.get("edge_strength")
                        or row.get("strength")
                        or row.get("compat_edge_strength")
                        or 0.0
                    ),
                    "classification": classification,
                }
            )
        top_capillaries.sort(key=lambda item: (-item["edge_strength"], item["edge_id"]))
        return {
            "generated_at": utc_now(),
            "protocol_id": COMMAND_PROTOCOL_ID_V2,
            "docs_gate_status": docs_gate,
            "watcher_mode": "event-driven" if self.native_watch_available() else "polling",
            "watch_scope": WATCH_SCOPE_LABEL,
            "watched_surface_count": watched_surface_count,
            "event_count": len(events),
            "matched_event_count": matched_event_count,
            "fallback_event_count": fallback_event_count,
            "claim_count": len(claims),
            "active_claim_count": sum(1 for row in claims if str(row.get("status") or "") == "active"),
            "committed_count": committed_count,
            "reinforced_count": reinforced_count,
            "edge_count": len(capillary_rows),
            "latency_row_count": len(latency_rows),
            "backlog_count": len(_event_backlog(self)),
            "average_t_sugar_ms": round(avg_t_sugar, 6),
            "vessel_counts": capillary_counter,
            "detection_latency_avg_ms": _avg("t_detect_ms"),
            "swarm_awareness_latency_avg_ms": _avg("t_route_ms"),
            "claim_latency_avg_ms": _avg("t_claim_ms"),
            "resolution_latency_avg_ms": _avg("t_commit_ms"),
            "commit_latency_avg_ms": _avg("t_commit_ms"),
            "t_sugar_avg_ms": _avg("t_sugar_ms"),
            "capillary_score_avg": _avg("capillary_score"),
            "liminal_distance_avg": _avg("liminal_delta"),
            "liminal_velocity_avg": _avg("liminal_velocity"),
            "capillary_tiers": tier_counts,
            "top_capillaries": top_capillaries[:5],
        }

    def native_watch_available(self: Any) -> bool:
        cached = getattr(self, "_native_watch_available_cache", None)
        if cached is not None:
            return bool(cached)
        try:
            probe = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    "$PSVersionTable.PSVersion.Major | Out-String",
                ],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            available = probe.returncode == 0
        except Exception:
            available = False
        self._native_watch_available_cache = available
        return available

    def next_event_id(self: Any, state: dict[str, Any] | None = None) -> str:
        mutable_state = state or self.load_state()
        seq = int(mutable_state.get("last_event_seq", 0) or 0) + 1
        mutable_state["last_event_seq"] = seq
        return f"CMD-{seq:06d}"

    def next_liminal_ts(self: Any, state: dict[str, Any] | None = None) -> str:
        mutable_state = state or self.load_state()
        seq = int(mutable_state.get("last_liminal_seq", 0) or 0) + 1
        mutable_state["last_liminal_seq"] = seq
        return f"LT-{seq:09d}"

    def state_hash_for_path(self: Any, path: Path | str, change_type: str = "updated") -> str:
        candidate = Path(path).resolve(strict=False)
        exists = candidate.exists()
        stat = candidate.stat() if exists else None
        payload = {
            "path": rel(candidate),
            "change_type": change_type,
            "exists": exists,
            "size": getattr(stat, "st_size", 0),
            "mtime_ns": getattr(stat, "st_mtime_ns", 0),
            "family": self.file_family_for_path(candidate),
        }
        return hashlib.sha1(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()

    def event_fingerprint(
        self: Any,
        source_id: str,
        path: Path | str,
        change_type: str,
        state_hash: str,
    ) -> str:
        candidate = Path(path).resolve(strict=False)
        payload = f"{source_id}|{rel(candidate)}|{change_type}|{state_hash}"
        return hashlib.sha1(payload.encode("utf-8")).hexdigest()[:20]

    def source_region_for_surface(self: Any, source_descriptor: dict[str, Any], relative_path: str) -> str:
        source_class = str(source_descriptor.get("source_class") or "command-folder")
        target_kind = str(source_descriptor.get("target_kind") or "file")
        return f"{source_class}:{target_kind}:{relative_path}"

    def source_class_match_score(self: Any, packet: Any, candidate: dict[str, Any]) -> float:
        if str(candidate.get("source_id") or "") == str(packet.source_id or ""):
            return 1.0
        if str(candidate.get("source_class") or "") == str(packet.source_class or ""):
            return 0.80
        goal = str(candidate.get("routing_goal") or "").lower()
        return 0.65 if goal and goal == str(packet.goal or "").lower() else 0.45

    def coord12_for_file(
        self: Any,
        *,
        source_descriptor: dict[str, Any],
        detected_ts: str,
        priority: float,
        confidence: float,
        change_type: str,
        normalized_path: Path,
        event_id: str,
        route_mode_seed: str,
    ) -> tuple[dict[str, Any], dict[str, Any], list[float], dict[str, Any]]:
        now_utc = parse_iso(detected_ts)
        coord12 = {
            "earth_utc_anchor": detected_ts,
            "earth_rotation_phase": local_rotation_phase(now_utc, LOCAL_ZONE),
            "earth_orbital_phase": orbital_phase(now_utc),
            "earth_geospatial_anchor": self.config.earth_geo_anchor,
            "solar_phase": self.shared12_ratio(self.scheduler_lane("western_solar12")),
            "lunar_phase": lunar_phase(now_utc),
            "local_sidereal_phase": sidereal_phase(now_utc),
            "canonical_sky_anchor": "western_solar12|planetary_office|vedic_lunar",
            "runtime_region": self.config.runtime_region,
            "queue_pressure": self.queue_pressure(),
            "goal_salience_vector": {
                "goal": str(source_descriptor.get("routing_goal") or "detect-classify-assign"),
                "priority": round(float(priority), 6),
            },
            "change_novelty_vector": {
                "change_type": change_type,
                "confidence": round(float(confidence), 6),
            },
        }
        coord12_frame = {
            "earth": list(coord12.keys())[:4],
            "astro": list(coord12.keys())[4:8],
            "runtime": list(coord12.keys())[8:10],
            "liminal": list(coord12.keys())[10:12],
        }
        vector12 = [self.coord12_scalar(value) for value in coord12.values()]
        coordinate_stamp = {
            "Xs": str(source_descriptor.get("coordinate_projection_hints", {}).get("Xs", "GLOBAL_COMMAND")),
            "Ys": str(source_descriptor.get("source_id") or "command_root"),
            "Zs": normalized_path.name,
            "Ts": self.active_loop_id(),
            "Qs": "COMMAND",
            "Rs": "D1",
            "Cs": event_id,
            "Fs": str(source_descriptor.get("coordinate_projection_hints", {}).get("Ns", "COMMAND")),
            "Ms": route_mode_seed,
            "Ns": str(normalized_path.parent.name or "root"),
            "Hs": str(source_descriptor.get("coordinate_projection_hints", {}).get("Hs", "command-event")),
            "Omega_s": "A1",
        }
        return coord12, coord12_frame, vector12, coordinate_stamp

    def coord_delta_from_prior(
        self: Any,
        state: dict[str, Any],
        vector12: list[float],
        detected_ts: str,
    ) -> dict[str, float]:
        prior_vector = state.get("last_coord12_vector") or []
        if not isinstance(prior_vector, list) or len(prior_vector) != len(vector12):
            prior_vector = [0.0] * len(vector12)
        delta_tau = math.sqrt(
            sum(
                (float(current) - float(previous)) ** 2
                for current, previous in zip(vector12, prior_vector)
            )
        )
        prior_ts = str(state.get("last_earth_ts") or "")
        delta_earth_ms = self.ms_between(prior_ts, detected_ts) if prior_ts else 0.0
        liminal_velocity = delta_tau / max(delta_earth_ms / 1000.0, 1e-6) if delta_earth_ms else 0.0
        return {
            "DeltaTau": round(delta_tau, 6),
            "DeltaEarth": round(delta_earth_ms, 6),
            "LiminalVelocity": round(liminal_velocity, 6),
        }

    def active_candidates(self: Any, source_ids: Any = None) -> list[dict[str, Any]]:
        leases = self.load_leases().get("active", {})
        rows: list[dict[str, Any]] = []
        for surface in _surface_rows(self, source_ids):
            source_id = str(surface.get("source_id") or "")
            source_token = slugify(source_id).upper() or "SOURCE"
            for role_class, master_agent_id in dict(surface.get("default_lanes") or {}).items():
                master = ROLE_BY_MASTER.get(master_agent_id, {})
                ant_id = f"{source_token}-{master_agent_id}-{role_class.upper()}"
                load = sum(1 for lease in leases.values() if str(lease.get("ant_id") or "") == ant_id)
                edge_snapshot = self._candidate_edge_snapshot(ant_id)
                rows.append(
                    {
                        "ant_id": ant_id,
                        "master_agent_id": str(master_agent_id),
                        "display_name": f"{source_id}:{role_class}",
                        "role": str(master.get("role", role_class)),
                        "role_tag": str(master.get("role_tag", role_class.upper())),
                        "role_class": role_class,
                        "source_id": source_id,
                        "source_class": str(surface.get("source_class") or ""),
                        "routing_goal": str(surface.get("routing_goal") or ""),
                        "urgency_baseline": float(surface.get("urgency_baseline", 0.0) or 0.0),
                        "coord_focus": dict(surface.get("coordinate_projection_hints") or {}),
                        "load": float(load),
                        "blocked": False,
                        "leased": load > 0,
                        "activation_state": "ACTIVE",
                        "capability_domains": [str(master.get("role", role_class))],
                        **edge_snapshot,
                    }
                )
        rows.sort(key=lambda item: (item["source_id"], item["master_agent_id"], item["ant_id"]))
        return rows

    def score_candidate(self: Any, packet: Any, candidate: dict[str, Any]) -> dict[str, Any]:
        joy_seed = packet.joy_seed or self.build_joy_seed(
            priority=float(packet.priority),
            confidence=float(packet.confidence),
            change_type=packet.change_type,
            source_path=packet.source_path,
            source_class=packet.source_class,
        )
        goal = max(0.0, self.goal_match_score(packet, candidate))
        source_match = max(0.0, self.source_class_match_score(packet, candidate))
        salience = max(0.0, float(packet.priority))
        joy_potential = max(0.0, float(joy_seed.get("h_seed", packet.pheromone)))
        pheromone_composite = self.pheromone_composite_for_edge(candidate)
        coord_distance = max(0.0, self.coordinate_match_score(packet, candidate))
        capability_match = max(
            0.0,
            self.capability_match_score(packet, candidate)
            + (0.25 * self.file_family_match_score(packet, candidate)),
        )
        current_load = float(candidate.get("load", 0.0) or 0.0)
        blocked_penalty = 1.0 if candidate.get("blocked") else 0.0
        leased_penalty = 0.75 if candidate.get("leased") else 0.0
        queue_penalty = 0.15 * float(self.queue_pressure())
        score = round(
            goal
            + source_match
            + salience
            + joy_potential
            + pheromone_composite
            + coord_distance
            + capability_match
            - current_load
            - blocked_penalty
            - leased_penalty
            - queue_penalty,
            6,
        )
        return {
            **candidate,
            "goal": round(goal, 6),
            "source_match": round(source_match, 6),
            "salience": round(salience, 6),
            "joy_potential": round(joy_potential, 6),
            "pheromone_composite": round(pheromone_composite, 6),
            "coord_distance": round(coord_distance, 6),
            "capability_match": round(capability_match, 6),
            "current_load": round(current_load, 6),
            "routing_penalty": round(blocked_penalty + leased_penalty + queue_penalty, 6),
            "score": score,
        }

    def route_event(self: Any, event_id: str, state: dict[str, Any] | None = None) -> dict[str, Any]:
        self.release_expired_leases()
        packet = self.load_event(event_id)
        if packet.route_state and packet.route_state.get("policy_id") == JOY_ROUTE_POLICY:
            return packet.route_state
        exact_candidates = self.active_candidates([packet.source_id]) if packet.source_id else []
        if not exact_candidates:
            exact_candidates = [
                candidate
                for candidate in self.active_candidates()
                if str(candidate.get("source_class") or "") == str(packet.source_class or "")
            ]
        candidate_pool = exact_candidates or self.active_candidates()
        scored = [self.score_candidate(packet, candidate) for candidate in candidate_pool]
        scored = [candidate for candidate in scored if candidate.get("activation_state") == "ACTIVE"]
        scored.sort(key=lambda item: (-item["score"], item["ant_id"]))
        selected = [candidate for candidate in scored if not candidate.get("blocked") and not candidate.get("leased")][: self.config.topk]
        if not selected:
            selected = scored[: self.config.topk]
        if not selected:
            raise ValueError("No active command candidates are available for routing.")
        worker_choice = next(
            (candidate for candidate in selected if candidate.get("role_class") == "worker"),
            next((candidate for candidate in selected if candidate.get("master_agent_id") == "A3"), selected[0]),
        )
        router_choice = next((candidate for candidate in scored if candidate.get("role_class") == "router"), worker_choice)
        scout_choice = next((candidate for candidate in scored if candidate.get("role_class") == "scout"), router_choice)
        archivist_choice = next((candidate for candidate in scored if candidate.get("role_class") == "archivist"), router_choice)
        crown_eligible = not bool(worker_choice.get("leased"))
        verification_cap = 1.0 if crown_eligible else 0.25
        route_path = ">".join(
            [
                str(scout_choice.get("ant_id") or "SCOUT-01"),
                str(router_choice.get("ant_id") or "ROUTER-01"),
                str(worker_choice.get("ant_id") or "WORKER-01"),
                str(archivist_choice.get("ant_id") or "ARCHIVIST-01"),
            ]
        )
        decision = CommandRouteDecisionV2(
            event_id=event_id,
            policy_id=JOY_ROUTE_POLICY,
            candidate_targets=[
                {
                    "ant_id": candidate["ant_id"],
                    "role": candidate.get("role_tag", ""),
                    "role_class": candidate.get("role_class", ""),
                    "source_id": candidate.get("source_id", ""),
                    "source_class": candidate.get("source_class", ""),
                    "score": candidate["score"],
                    "goal": candidate["goal"],
                    "source_match": candidate.get("source_match", 0.0),
                    "salience": candidate["salience"],
                    "joy_potential": candidate["joy_potential"],
                    "pheromone_composite": candidate["pheromone_composite"],
                    "coord_distance": candidate["coord_distance"],
                    "capability_match": candidate["capability_match"],
                    "current_load": candidate["current_load"],
                    "blocked": bool(candidate.get("blocked")),
                    "leased": bool(candidate.get("leased")),
                }
                for candidate in scored[: max(self.config.topk, 8)]
            ],
            selected_targets=[candidate["ant_id"] for candidate in selected],
            topk=self.config.topk,
            claim_mode=self.config.claim_mode,
            quorum=self.config.quorum,
            score_breakdown={
                candidate["ant_id"]: {
                    "goal": candidate["goal"],
                    "source_match": candidate.get("source_match", 0.0),
                    "salience": candidate["salience"],
                    "joy_potential": candidate["joy_potential"],
                    "pheromone_composite": candidate["pheromone_composite"],
                    "coord_distance": candidate["coord_distance"],
                    "capability_match": candidate["capability_match"],
                    "current_load": candidate["current_load"],
                    "routing_penalty": candidate["routing_penalty"],
                }
                for candidate in selected
            },
            duplicate_risk=round(sum(1 for candidate in selected if candidate["leased"]) / max(len(selected), 1), 6),
            created_at=utc_now(),
            expires_at="",
            ranked_routes=[
                {
                    "ant_id": candidate["ant_id"],
                    "source_id": candidate.get("source_id", ""),
                    "master_agent_id": candidate["master_agent_id"],
                    "role_class": candidate.get("role_class", ""),
                    "score": candidate["score"],
                }
                for candidate in selected
            ],
            route_inputs={
                "goal": packet.goal,
                "salience": packet.priority,
                "joy_potential": worker_choice["joy_potential"],
                "pheromone_composite": worker_choice["pheromone_composite"],
                "coord_distance": worker_choice["coord_distance"],
                "capability_match": worker_choice["capability_match"],
                "current_load": worker_choice["current_load"],
                "source_id": packet.source_id,
                "source_class": packet.source_class,
            },
            route_path=route_path,
            worker_choice=worker_choice["ant_id"],
            generated_at=utc_now(),
            quest_refs=[COMMAND_TEMPLE_QUEST_ID] if packet.source_class in {"temple-board", "build-queue"} else [COMMAND_HALL_QUEST_ID],
            reward_policy_id=JOY_REWARD_POLICY,
            route_mode="rotate",
            crown_eligible=crown_eligible,
            verification_witness_cap=verification_cap,
            reward_inputs={
                "priority": packet.priority,
                "confidence": packet.confidence,
                "effort_quality": self.stage_effort_quality("route", "observe"),
            },
        )
        verification_state = self.verification_defaults("route", "observe", crown_eligible=crown_eligible, verification_witness_cap=verification_cap)
        reward_state = self.finalize_reward_state(
            self.compose_reward_state(
                stage="route",
                result="observe",
                priority=packet.priority,
                confidence=packet.confidence,
                effort_quality=self.stage_effort_quality("route", "observe"),
                tau_seconds=max(self.ms_between(packet.detected_ts, decision.generated_at) / 1000.0, 0.0),
                novelty_score=1.0,
                contribution_share=ROLE_CONTRIBUTION_SHARES["Router"],
                verification_state=verification_state,
            )
        )
        pheromone_state = self.compose_pheromone_state(reward_state, ROLE_CONTRIBUTION_SHARES["Router"], reward_state.verified_alignment_score)
        packet.route_state = asdict(decision)
        packet.route_targets = decision.selected_targets
        packet.linked_quests = decision.quest_refs
        packet.status = "routed"
        packet.reward_state = asdict(reward_state)
        packet.verification_state = asdict(verification_state)
        packet.pheromone_state = asdict(pheromone_state)
        packet.reward_policy_id = JOY_REWARD_POLICY
        packet.pheromone = clamp(reward_state.verified_alignment_score, 0.0, 1.0)
        packet.crown_tier = reward_state.crown_tier
        packet.closure_class = verification_state.closure_class
        packet.latency_state["awareness_latency_ms"] = round(self.ms_between(packet.detected_ts, decision.generated_at), 3)
        packet.latency_state["route_policy"] = JOY_ROUTE_POLICY
        self.save_event(packet)
        if state is not None:
            state["last_routed_event_id"] = event_id
            self.save_state(state)
        self.sync_public_surfaces(event_id=event_id)
        return asdict(decision)

    def source_health(self: Any, source_ids: Any = None) -> dict[str, Any]:
        events = _event_rows(self)
        claims = _claim_rows(self)
        native = self.native_watch_available()
        watcher_mode = "event-driven" if native else "polling"
        rows: list[dict[str, Any]] = []
        for surface in _surface_rows(self, source_ids):
            source_id = str(surface.get("source_id") or "")
            target_path = Path(str(surface.get("absolute_path") or ""))
            source_events = [row for row in events if str(row.get("source_id") or "") == source_id]
            source_claims = [row for row in claims if str(row.get("source_id") or "") == source_id and str(row.get("status") or "") == "active"]
            backlog = [row for row in source_events if str(row.get("status") or "detected") not in {"committed", "reinforced"}]
            rows.append(
                {
                    "source_id": source_id,
                    "absolute_path": str(target_path.resolve(strict=False)),
                    "relative_path": str(surface.get("relative_path") or rel(target_path)),
                    "source_class": str(surface.get("source_class") or ""),
                    "target_kind": str(surface.get("target_kind") or "file"),
                    "watch_root": str(surface.get("watch_root") or target_path.parent),
                    "native_watch_available": native,
                    "degraded_mode": not native,
                    "exists": target_path.exists(),
                    "event_count": len(source_events),
                    "backlog_count": len(backlog),
                    "active_claim_count": len(source_claims),
                    "last_event_id": str(source_events[0].get("event_id") or "") if source_events else "",
                    "watcher_mode": watcher_mode,
                    "routing_goal": str(surface.get("routing_goal") or ""),
                    "urgency_baseline": float(surface.get("urgency_baseline", 0.0) or 0.0),
                    "docs_gate_status": self.docs_gate_status()["state"],
                }
            )
        return {
            "generated_at": utc_now(),
            "docs_gate_status": self.docs_gate_status()["state"],
            "watcher_mode": watcher_mode,
            "watch_scope": WATCH_SCOPE_LABEL,
            "source_count": len(rows),
            "rows": rows,
        }

    def public_state(self: Any, source_ids: Any = None) -> dict[str, Any]:
        source_health_payload = self.source_health(source_ids)
        watch_registry = self.watched_surface_registry(source_ids)
        events = _event_rows(self)
        last_event = events[0] if events else {}
        runtime_truth = self.current_runtime_truth()
        metrics = self.metrics()
        top_capillaries = metrics.get("top_capillaries", [])
        return {
            "generated_at": utc_now(),
            "protocol_id": COMMAND_PROTOCOL_ID_V2,
            "canonical_authority": CANONICAL_AUTHORITY,
            "command_root": str(self.config.command_surface_root),
            "active_surface": ACTIVE_SURFACE_LABEL,
            "watch_scope": WATCH_SCOPE_LABEL,
            "watcher_mode": source_health_payload.get("watcher_mode", "polling"),
            "watched_surface_count": watch_registry.get("source_count", 0),
            "docs_gate": self.docs_gate_status(),
            "docs_gate_status": self.docs_gate_status()["state"],
            "current_runtime_truth": runtime_truth,
            "active_membrane": COMMAND_ACTIVE_MEMBRANE,
            "feeder_stack": list(COMMAND_FEEDER_STACK),
            "watched_source_ids": [row.get("source_id") for row in watch_registry.get("rows", [])],
            "policy": {
                "protocol_id": COMMAND_PROTOCOL_ID_V2,
                "routing_policy": COMMAND_ROUTE_POLICY,
                "selector_terms": list(SELECTOR_TERMS),
                "lookup_envelope": "NodeStamp = AgentTag @ CoordinateStamp + WitnessClass + QuestRefs + ArtifactRefs",
                "watch_policy": {
                    "primary_mode": "event-driven",
                    "fallback_mode": "polling",
                    "watch_scope": WATCH_SCOPE_LABEL,
                },
                "topk": self.config.topk,
                "claim_mode": self.config.claim_mode,
                "quorum": self.config.quorum,
                "ttl": self.config.ttl,
                "lease_ms": self.config.lease_ms,
            },
            "truth_boundary": {
                "prompt_level_liminal_gps": "supported",
                "keystroke_level_liminal_gps": "requires client/runtime instrumentation",
            },
            "queue_depth": max(int(metrics.get("event_count", 0)) - int(metrics.get("committed_count", 0)), 0),
            "last_event": {
                "event_id": str(last_event.get("event_id") or ""),
                "event_type": str(last_event.get("change_type") or last_event.get("event_kind") or ""),
                "source_path": str(last_event.get("source_path") or ""),
                "change_type": str(last_event.get("change_type") or ""),
                "watcher_mode": str(last_event.get("watcher_mode") or source_health_payload.get("watcher_mode", "polling")),
                "status": str(last_event.get("status") or ""),
                "earth_ts_utc": str(last_event.get("earth_ts_utc") or last_event.get("earth_ts") or ""),
                "route_path": str((last_event.get("route_state") or {}).get("route_path", "")),
                "claim_state": str((last_event.get("claim_state") or {}).get("status", "unclaimed")),
                "replay_ptr": str(last_event.get("replay_ptr") or ""),
                "coord12": last_event.get("coord12") or {},
                "coordinate_stamp": last_event.get("coordinate_stamp") or {},
                "delta_tau": float((last_event.get("coord_delta") or {}).get("DeltaTau", last_event.get("liminal_delta", 0.0)) or 0.0),
                "velocity_tau": float((last_event.get("coord_delta") or {}).get("LiminalVelocity", last_event.get("liminal_velocity", 0.0)) or 0.0),
            },
            "metrics": metrics,
            "top_capillaries": top_capillaries,
            "watch_registry": watch_registry,
            "source_health": source_health_payload,
        }

    def sync_public_surfaces(self: Any, event_id: str | None = None) -> dict[str, Any]:
        docs_gate = self.docs_gate_status()["state"]
        watched_registry = self.watched_surface_registry()
        events = _event_rows(self)
        claims = _claim_rows(self)
        edges_payload = self.load_edges()
        capillary_rows = _capillary_rows(self)
        latency_rows = _latency_rows(self)
        source_health_payload = self.source_health()
        public_state = self.public_state()
        live_event_ledger = {"generated_at": utc_now(), "protocol_id": COMMAND_PROTOCOL_ID_V2, "docs_gate_status": docs_gate, "row_count": len(events), "rows": events}
        claim_ledger = {"generated_at": utc_now(), "docs_gate_status": docs_gate, "row_count": len(claims), "active_count": sum(1 for row in claims if str(row.get("status") or "") == "active"), "rows": claims}
        capillary_registry = {"generated_at": utc_now(), "docs_gate_status": docs_gate, "edge_count": len(capillary_rows), "rows": capillary_rows, "edges": edges_payload.get("edges", {}), "history": edges_payload.get("history", [])}
        latency_registry = {"generated_at": utc_now(), "docs_gate_status": docs_gate, "row_count": len(latency_rows), "rows": latency_rows}
        live_manifest = {
            "generated_at": utc_now(),
            "protocol_id": COMMAND_PROTOCOL_ID_V2,
            "canonical_authority": CANONICAL_AUTHORITY,
            "authority_mode": "single-node-local-swarm-substrate",
            "docs_gate_status": docs_gate,
            "active_surface": ACTIVE_SURFACE_LABEL,
            "command_root": str(self.config.command_surface_root),
            "watch_scope": WATCH_SCOPE_LABEL,
            "watcher_mode": public_state.get("watcher_mode", "polling"),
            "active_membrane": COMMAND_ACTIVE_MEMBRANE,
            "feeder_stack": list(COMMAND_FEEDER_STACK),
            "event_id": event_id or str(public_state.get("last_event", {}).get("event_id", "")),
            "outputs": {
                "watched_surfaces": watched_registry.get("source_count", 0),
                "events": live_event_ledger["row_count"],
                "claims": claim_ledger["row_count"],
                "capillary_edges": capillary_registry["edge_count"],
                "latency_rows": latency_registry["row_count"],
            },
            "paths": {
                "watched_surface_registry": str(self.config.watched_surface_registry_path),
                "live_event_ledger": str(self.config.live_event_ledger_path),
                "claim_ledger": str(self.config.claim_ledger_path),
                "capillary_registry": str(self.config.edge_path),
                "latency_registry": str(self.config.latency_registry_path),
                "surface_health": str(self.config.surface_health_path),
            },
        }
        write_json(PUBLIC_COMMAND_STATE_PATH, public_state)
        _write_live_registry_pair(self, "watched_surface_registry_path", watched_registry)
        _write_live_registry_pair(self, "live_event_ledger_path", live_event_ledger)
        _write_live_registry_pair(self, "claim_ledger_path", claim_ledger)
        _write_live_registry_pair(self, "surface_health_path", source_health_payload)
        _write_live_registry_pair(self, "live_manifest_path", live_manifest)
        _write_live_registry_pair(self, "latency_registry_path", latency_registry)
        self.save_edges(capillary_registry)
        _write_live_registry_pair(self, "live_manifest_path", live_manifest)
        return public_state

    def write_live_writeback_surfaces(self: Any, protocol: dict[str, Any], reward: dict[str, Any], capillary: dict[str, Any]) -> None:
        watched_rows = protocol.get("watched_surfaces", {}).get("rows", [])
        watched_names = ", ".join(f"`{row.get('source_id', '')}`" for row in watched_rows[:7])
        hall_body = "\n".join(
            [
                "## COMMAND Membrane Hall Family",
                "",
                f"- Quest id: `{COMMAND_HALL_QUEST_ID}`",
                "- Surface: practical command intake, lawful worker claim, and receipt-backed closure.",
                f"- Phase 1 watch scope: `{WATCH_SCOPE_LABEL}`.",
                "- Routing spine: `WATCHED SURFACE -> Scout -> Router -> Worker -> Archivist`.",
                f"- Watched surfaces: {watched_names or '`command_root`'}",
                f"- Routing policy: `{protocol['routing_defaults']['policy_id']}`",
            ]
        )
        temple_body = "\n".join(
            [
                "## COMMAND Membrane Temple Family",
                "",
                f"- Quest id: `{COMMAND_TEMPLE_QUEST_ID}`",
                "- Surface: docs-gate honesty, coordinate law, capillary law, and no-rumor routing discipline.",
                "- Prompt-level liminal GPS: `supported`.",
                "- Keystroke-level liminal GPS: `requires client/runtime instrumentation`.",
                f"- Docs gate: `{protocol['docs_gate_status']}`",
            ]
        )
        active_run_body = "\n".join(
            [
                "## COMMAND Membrane Active Run",
                "",
                f"- Canonical authority: `{protocol['canonical_authority']}`",
                f"- Active surface: `{ACTIVE_SURFACE_LABEL}`",
                f"- Watch scope: `{protocol['watch_policy']['watch_scope']}`",
                f"- Watcher mode: `{protocol['watch_policy']['primary_mode']}`",
                f"- Docs gate: `{protocol['docs_gate_status']}`",
            ]
        )
        queue_body = "\n".join(
            [
                "## Command Membrane Queue",
                "",
                f"- Watch scope: `{WATCH_SCOPE_LABEL}`",
                f"- Routing policy: `{protocol['routing_defaults']['policy_id']}`",
                f"- Claim mode: `{protocol['routing_defaults']['claim_mode']}`",
                f"- Lease ms: `{protocol['routing_defaults']['lease_ms']}`",
            ]
        )
        prompt_body = "\n".join(
            [
                "## Command Membrane Next Prompt",
                "",
                "1. Treat every watched surface as a sensory membrane, with `GLOBAL COMMAND` as the first ingress.",
                "2. Keep Google Docs explicitly blocked until credentials exist and an actual live pass succeeds.",
                "3. Preserve dual-stamped Earth plus liminal timing on every committed event.",
                "4. Route only to the ants that matter first; do not widen broadcast by default.",
                "5. Keep Hall and Temple macro-sized even when machine event volume grows.",
            ]
        )
        lp57_body = "\n".join(
            [
                "## LP57 Command Membrane",
                "",
                "- LP57 command routing now treats the first-wave watched surfaces as one single-node local swarm membrane.",
                "- Event-driven watching is primary; polling is explicit fallback only.",
                "- Hall, Temple, Active Run, Build Queue, and active-thread roots consume packets and receipts from the same live ledger.",
            ]
        )
        _patch_surface_file(self, HALL_BOARD_PATH, MARKER_HALL, hall_body)
        _patch_surface_file(self, TEMPLE_BOARD_PATH, MARKER_TEMPLE, temple_body)
        _patch_surface_file(self, ACTIVE_RUN_PATH, MARKER_ACTIVE_RUN, active_run_body)
        _patch_surface_file(self, BUILD_QUEUE_PATH, MARKER_BUILD_QUEUE, queue_body)
        _patch_surface_file(self, NEXT_SELF_PROMPT_PATH, MARKER_NEXT_PROMPT, prompt_body)
        _patch_surface_file(self, LP57_PROTOCOL_PATH, MARKER_LP57_PROTOCOL, lp57_body)

    def ensure_protocol_artifacts(self: Any) -> dict[str, Any]:
        docs_gate = self.docs_gate_status()
        runtime_truth = self.current_runtime_truth()
        watched_surfaces = self.watched_surface_registry()
        watch_roots = _watch_roots(list(watched_surfaces.get("rows", [])))
        protocol = {
            "protocol_id": COMMAND_PROTOCOL_ID_V2,
            "command_version": "single-node-local-swarm-substrate-v1",
            "canonical_authority": CANONICAL_AUTHORITY,
            "authority_mode": "single-node-local-swarm-substrate",
            "docs_gate": docs_gate,
            "docs_gate_status": docs_gate["state"],
            "active_surface": ACTIVE_SURFACE_LABEL,
            "command_folder_root": rel(self.config.command_surface_root),
            "watched_surfaces": watched_surfaces,
            "watch_policy": {
                "primary_mode": "event-driven",
                "fallback_mode": "polling",
                "watched_roots": watch_roots,
                "watch_scope": WATCH_SCOPE_LABEL,
            },
            "routing_defaults": {
                "policy_id": COMMAND_ROUTE_POLICY,
                "selector_terms": list(SELECTOR_TERMS),
                "topk": self.config.topk,
                "claim_mode": self.config.claim_mode,
                "quorum": self.config.quorum,
                "ttl": self.config.ttl,
                "lease_ms": self.config.lease_ms,
            },
            "current_runtime_truth": runtime_truth,
            "active_membrane": COMMAND_ACTIVE_MEMBRANE,
            "feeder_stack": list(COMMAND_FEEDER_STACK),
            "pipeline": ["WATCHED SURFACE", "Scout", "Router", "Worker", "Archivist"],
            "lookup_envelope": "NodeStamp = AgentTag @ CoordinateStamp + WitnessClass + QuestRefs + ArtifactRefs",
            "truth_boundary": {
                "prompt_level_liminal_gps": "supported",
                "keystroke_level_liminal_gps": "requires client/runtime instrumentation",
            },
        }
        schema = {
            "schema_id": COMMAND_PACKET_SCHEMA_ID_V2,
            "coord12_labels": [
                "earth_utc_anchor",
                "earth_rotation_phase",
                "earth_orbital_phase",
                "earth_geospatial_anchor",
                "solar_phase",
                "lunar_phase",
                "local_sidereal_phase",
                "canonical_sky_anchor",
                "runtime_region",
                "queue_pressure",
                "goal_salience_vector",
                "change_novelty_vector",
            ],
            "coord12_frame_groups": ["earth", "astro", "runtime", "liminal"],
            "packet_types": {
                "CommandEventPacket": ["event_id", "source_ant_id", "source_path", "change_type", "goal", "priority", "confidence", "earth_ts", "liminal_ts", "coord12", "coordinate_stamp", "ttl", "pheromone", "route_class", "witness_class"],
                "RouteDecision": ["event_id", "policy_id", "candidate_targets", "selected_targets", "topk", "claim_mode", "quorum", "route_path"],
                "ClaimLease": ["claim_id", "event_id", "ant_id", "role", "lease_ms", "claimed_at", "expires_at", "status"],
                "ArchivistReceipt": ["event_id", "worker_id", "result", "route_path", "detection_latency_ms", "swarm_awareness_latency_ms", "claim_latency_ms", "resolution_latency_ms", "commit_latency_ms", "t_sugar_ms", "replay_ptr"],
                "CapillaryEdge": ["edge_id", "source_ant_id", "target_ant_id", "edge_strength", "classification", "success_count", "use_count", "noise_count", "last_event_id"],
                "LatencyBenchmarkRecord": ["detection_latency_ms", "swarm_awareness_latency_ms", "claim_latency_ms", "resolution_latency_ms", "commit_latency_ms", "t_sugar_ms", "capillary_score", "liminal_distance", "liminal_velocity"],
            },
            "lookup_envelope": "NodeStamp = AgentTag @ CoordinateStamp + WitnessClass + QuestRefs + ArtifactRefs",
        }
        reward = {
            "law_id": COMMAND_REWARD_FIELD_ID_V2,
            "canonical_protocol_id": COMMAND_PROTOCOL_ID_V2,
            "nonnegative_reward_law": True,
            "contribution_shares": ROLE_CONTRIBUTION_SHARES,
            "compatibility_role": "support-only",
        }
        capillary = {
            "law_id": COMMAND_CAPILLARY_LAW_ID_V2,
            "canonical_protocol_id": COMMAND_PROTOCOL_ID_V2,
            "formula": "C_next = clamp(0,1, rho*C + alpha*U + beta*F - gamma*D - delta*N)",
            "edge_strength_formula": "repeated fast useful routes strengthen; noisy or slow routes decay",
        }
        latency = {
            "benchmark_id": "COMMAND_MEMBRANE_LATENCY_V1",
            "canonical_protocol_id": COMMAND_PROTOCOL_ID_V2,
            "equation": "T_sugar = T_detect + T_encode + T_route + T_claim + T_commit",
            "metrics": ["detection_latency_ms", "swarm_awareness_latency_ms", "claim_latency_ms", "resolution_latency_ms", "commit_latency_ms", "t_sugar_ms", "capillary_score", "liminal_distance", "liminal_velocity"],
            "watch_scope": WATCH_SCOPE_LABEL,
            "docs_gate_status": docs_gate["state"],
            "truth_boundary": {
                "prompt_level_liminal_gps": "supported",
                "keystroke_level_liminal_gps": "requires client/runtime instrumentation",
            },
        }
        write_json(self.config.protocol_json_path, protocol)
        write_json(self.config.packet_schema_json_path, schema)
        write_json(self.config.reward_field_json_path, reward)
        write_json(self.config.capillary_law_json_path, capillary)
        write_json(self.config.latency_benchmark_json_path, latency)
        write_json(
            self.config.protocol_v1_registry_path,
            protocol,
        )
        write_text(self.config.command_manifest_path, f"# NEXT57 Command Sensory Membrane\n\n- Canonical authority: `{CANONICAL_AUTHORITY}`\n- Phase 1 watch scope: `{WATCH_SCOPE_LABEL}`\n- Mode: `event-driven-first` with explicit `polling` fallback\n")
        write_text(self.config.protocol_manifest_path, f"# NEXT57 Command Protocol\n\n- Protocol id: `{COMMAND_PROTOCOL_ID_V2}`\n- Canonical authority: `{CANONICAL_AUTHORITY}`\n- Phase 1 watch scope: `{WATCH_SCOPE_LABEL}`\n")
        write_text(
            self.config.packet_manifest_path,
            "# NEXT57 Command Packet Standard\n\n"
            "- Every detected change becomes a typed packet before routing.\n"
            "- The first-wave local swarm mesh is the watched root set for v1.\n"
            "- Coord12 is the canonical prompt-level liminal packet projection.\n"
            "- Lookup envelope: `NodeStamp = AgentTag @ CoordinateStamp + WitnessClass + QuestRefs + ArtifactRefs`\n",
        )
        write_text(self.config.capillary_manifest_path, "# NEXT57 Command Capillary Law\n\n- Formula: `C_next = clamp(0,1, rho*C + alpha*U + beta*F - gamma*D - delta*N)`\n")
        write_text(self.config.latency_manifest_path, f"# NEXT57 Command Latency Benchmarks\n\n- Equation: `{latency['equation']}`\n- Prompt-level liminal GPS is supported; keystroke-level remains out of scope in v1.\n")
        write_text(self.config.reward_field_manifest_path, "# NEXT 57 Command Reward Field\n\n- Reward is nonnegative and verification-gated.\n")
        write_text(
            self.config.protocol_v1_manifest_path,
            "# Command Membrane Mesh Protocol\n\n"
            "- This registry mirrors the live local-only single-node swarm membrane law.\n"
            "- The first-wave local swarm mesh covers `command_root`, Guild Hall, Temple, Active Run, Build Queue, the active-thread root, and the global-command thread.\n"
            "- Event-driven watching is primary; polling is explicit fallback only.\n"
            "- The command membrane derives its reporting surfaces from the same live ledger used by the runtime.\n",
        )
        self.write_live_writeback_surfaces(protocol, reward, capillary)
        self.sync_public_surfaces()
        return {"protocol": self.config.protocol_json_path, "schema": self.config.packet_schema_json_path, "reward": self.config.reward_field_json_path, "capillary": self.config.capillary_law_json_path, "latency": self.config.latency_benchmark_json_path}

    def emit_change(
        self: Any,
        *,
        source_path: Path | str,
        change_type: str,
        detected_ts: str,
        confidence: float = 0.98,
        parent_event_id: str = "ROOT",
        state: dict[str, Any] | None = None,
        source_ids: Any = None,
    ) -> Any:
        self.ensure_protocol_artifacts()
        mutable_state = state or self.load_state()
        normalized_path = Path(source_path).resolve(strict=False)
        ignore_reason = self.ignored_reason(normalized_path)
        if ignore_reason:
            return None
        source_descriptor = self.source_descriptor_for_path(normalized_path, source_ids=source_ids) or {
            "source_id": "command_root",
            "source_class": "command-folder",
            "absolute_path": str(self.config.command_surface_root),
            "watch_root": str(self.config.command_surface_root),
            "routing_goal": "detect-classify-assign",
            "urgency_baseline": 0.90,
            "coordinate_projection_hints": {"Xs": "GLOBAL_COMMAND", "Hs": "command-event", "Ns": "COMMAND"},
        }
        source_id = str(source_descriptor.get("source_id") or "command_root")
        source_class = str(source_descriptor.get("source_class") or "command-folder")
        relative_path = rel(normalized_path)
        file_family = self.file_family_for_path(normalized_path)
        state_hash = self.state_hash_for_path(normalized_path, change_type)
        fingerprint = self.event_fingerprint(source_id, normalized_path, change_type, state_hash)
        dedupe = mutable_state.setdefault("dedupe", {})
        prior = dedupe.get(fingerprint)
        if isinstance(prior, dict) and _fingerprint_seen_within(self, prior):
            dedupe[fingerprint]["seen_at"] = utc_now()
            self.save_state(mutable_state)
            event_id = str(prior.get("event_id") or "")
            if event_id and self.event_path(event_id).exists():
                return self.load_event(event_id)
            return None
        event_id = self.next_event_id(mutable_state)
        liminal_ts = self.next_liminal_ts(mutable_state)
        docs_gate = self.docs_gate_status()
        source_mtime_ns = float(normalized_path.stat().st_mtime_ns if normalized_path.exists() else 0.0)
        priority = round(
            self.clamp01(
                float(source_descriptor.get("urgency_baseline", 0.90))
                + (0.05 if file_family == "code" else 0.0)
                + (0.03 if any(token in normalized_path.name.lower() for token in ("protocol", "schema", "ledger", "manifest")) else 0.0)
            ),
            6,
        )
        confidence = round(float(confidence), 6)
        joy_seed = self.build_joy_seed(priority=priority, confidence=confidence, change_type=change_type, source_path=relative_path, source_class=source_class)
        coord12, coord12_frame, vector12, coordinate_stamp = self.coord12_for_file(
            source_descriptor=source_descriptor,
            detected_ts=detected_ts,
            priority=priority,
            confidence=confidence,
            change_type=change_type,
            normalized_path=normalized_path,
            event_id=event_id,
            route_mode_seed=str(joy_seed.get("route_mode_seed", "closure")),
        )
        coord_delta = self.coord_delta_from_prior(mutable_state, vector12, detected_ts)
        verification_state = self.verification_defaults("detect", "observe", crown_eligible=True, verification_witness_cap=1.0)
        reward_state = self.finalize_reward_state(self.compose_reward_state(stage="detect", result="observe", priority=priority, confidence=confidence, effort_quality=self.stage_effort_quality("detect", "observe"), tau_seconds=0.0, novelty_score=1.0, contribution_share=ROLE_CONTRIBUTION_SHARES["Scout"], verification_state=verification_state))
        pheromone_state = self.compose_pheromone_state(reward_state, ROLE_CONTRIBUTION_SHARES["Scout"], reward_state.verified_alignment_score)
        absolute_surface = Path(str(source_descriptor.get("absolute_path") or self.config.command_surface_root))
        packet = CommandEventPacketV2(
            event_id=event_id,
            source_ant_id=f"{slugify(source_id).upper() or 'COMMAND'}-A1-SCOUT",
            source_path=relative_path,
            active_surface=rel(absolute_surface),
            change_type=change_type,
            change_summary=f"{change_type}:{normalized_path.name}",
            goal=str(source_descriptor.get("routing_goal") or "detect-classify-assign"),
            priority=priority,
            confidence=confidence,
            earth_ts=detected_ts,
            earth_ts_local=parse_iso(detected_ts).astimezone(LOCAL_ZONE).isoformat(),
            detected_ts=detected_ts,
            emitted_ts=utc_now(),
            liminal_ts=liminal_ts,
            seat_addr_6d="A1.B1.C1.D1.E1.F1",
            coordinate_stamp=coordinate_stamp,
            canonical_addr_6d="A1.B1.C1.D1.E1.F1",
            liminal_stamp_12d=coord12,
            surface_class=source_class,
            hierarchy_level="D6",
            return_anchor="Archivist",
            earth_ts_utc=detected_ts,
            parent_event_id=parent_event_id,
            ttl=self.config.ttl,
            pheromone=joy_seed["h_seed"],
            joy_seed=joy_seed,
            state_hash=state_hash,
            route_class=COMMAND_ROUTE_CLASS,
            witness_class=docs_gate["witness_class"],
            status="detected",
            membrane_id="GLOBAL_COMMAND",
            role_class="Scout",
            base4_addr="A1.B1.C1.D1",
            parent=parent_event_id,
            lineage={"parent_event_id": parent_event_id, "source_mtime_ns": source_mtime_ns, "docs_gate_detail": docs_gate["detail"], "loop_id": self.active_loop_id(), "surface": rel(absolute_surface), "source_id": source_id, "source_class": source_class},
            coord12=coord12,
            coord12_frame=coord12_frame,
            coord_delta=coord_delta,
            scout_id=f"{slugify(source_id).upper() or 'COMMAND'}-A1-SCOUT",
            tag=slugify(normalized_path.stem),
            event_tag=event_id,
            change={"type": change_type, "summary": f"{change_type}:{normalized_path.name}", "state_hash": state_hash, "relative_path": relative_path, "source_path": relative_path},
            docs_gate_status=docs_gate["state"],
            latency_state={"detect_latency_ms": 0.0, "encode_latency_ms": 0.0, "route_policy": JOY_ROUTE_POLICY, "capillary_score": 0.0, "capillary_delta": 0.0},
            affected_nodes=[relative_path],
            replay_ptr=rel(self.event_path(event_id)),
            coordinate_vector_12=vector12,
            artifact_refs=[relative_path],
            source_region=self.source_region_for_surface(source_descriptor, relative_path),
            sensor_event_id=event_id,
            file_family=file_family,
            scheduler_refs=self.scheduler_refs_payload(),
            hsigma_ref=rel(self.config.hsigma_bundle_path),
            route_targets=[],
            linked_quests=[],
            source_folder=str(source_descriptor.get("source_id") or "GLOBAL COMMAND"),
            front_ref=COMMAND_ACTIVE_MEMBRANE,
            seed_mode="A-dominant",
            dual_reference=f"{SEED_A_REF}|{SEED_B_REF}",
            liminal_delta=float(coord_delta["DeltaTau"]),
            earth_delta_ms=float(coord_delta["DeltaEarth"]),
            liminal_velocity=float(coord_delta["LiminalVelocity"]),
            prior_comparable_event_id=str(mutable_state.get("last_event_id", "")),
            watcher_mode="event-driven" if self.native_watch_available() else "polling",
            duality_effect="joy-gradient-command",
            reward_state=asdict(reward_state),
            verification_state=asdict(verification_state),
            pheromone_state=asdict(pheromone_state),
            reward_policy_id=JOY_REWARD_POLICY,
            crown_tier=reward_state.crown_tier,
            closure_class=verification_state.closure_class,
            source_id=source_id,
            source_class=source_class,
            watch_root=str(source_descriptor.get("watch_root") or absolute_surface.parent),
            urgency_baseline=float(source_descriptor.get("urgency_baseline", 0.90)),
            event_fingerprint=fingerprint,
        )
        self.save_event(packet)
        sensor_log = self.load_sensor_events()
        sensor_log.append({"event_id": event_id, "event_fingerprint": fingerprint, "source_id": source_id, "source_path": relative_path, "change_type": change_type, "detected_ts": detected_ts, "docs_gate_status": docs_gate["state"]})
        self.save_sensor_events(sensor_log)
        mutable_state["last_event_id"] = event_id
        mutable_state["last_coord12_vector"] = vector12
        mutable_state["last_earth_ts"] = detected_ts
        mutable_state.setdefault("known_files", {})[relative_path] = {"source_id": source_id, "source_class": source_class, "state_hash": state_hash, "event_fingerprint": fingerprint, "change_type": change_type, "detected_ts": detected_ts}
        dedupe[fingerprint] = {"event_id": event_id, "seen_at": utc_now()}
        self.save_state(mutable_state)
        self.sync_public_surfaces(event_id=event_id)
        return packet

    def _snapshot_surface(self: Any, surface: dict[str, Any]) -> dict[str, dict[str, Any]]:
        target = Path(str(surface.get("absolute_path") or ""))
        snapshot: dict[str, dict[str, Any]] = {}
        paths = [target] if str(surface.get("target_kind") or "file") == "file" else ([path for path in target.rglob("*") if path.is_file()] if target.exists() else [])
        for path in paths:
            if self.ignored_reason(path):
                continue
            stat = path.stat() if path.exists() else None
            snapshot[rel(path)] = {"absolute_path": str(path.resolve(strict=False)), "relative_path": rel(path), "source_id": str(surface.get("source_id") or ""), "source_class": str(surface.get("source_class") or ""), "state_hash": self.state_hash_for_path(path, "updated"), "mtime_ns": getattr(stat, "st_mtime_ns", 0), "size": getattr(stat, "st_size", 0)}
        return snapshot

    def _native_watch_rows(self: Any, surfaces: list[dict[str, Any]], timeout_secs: int) -> list[dict[str, Any]]:
        roots = _watch_roots(surfaces)
        if not roots:
            return []
        script = f"""
$roots = '{json.dumps(roots)}' | ConvertFrom-Json
$timeout = {int(timeout_secs)}
$watchers = @()
$registrations = @()
$rows = New-Object System.Collections.ArrayList
foreach ($root in $roots) {{
  if (-not (Test-Path -LiteralPath $root)) {{ continue }}
  $item = Get-Item -LiteralPath $root
  $watchPath = if ($item.PSIsContainer) {{ $root }} else {{ Split-Path -LiteralPath $root -Parent }}
  $filter = if ($item.PSIsContainer) {{ '*' }} else {{ Split-Path -LiteralPath $root -Leaf }}
  $includeSub = [bool]$item.PSIsContainer
  $fsw = New-Object System.IO.FileSystemWatcher $watchPath, $filter
  $fsw.IncludeSubdirectories = $includeSub
  $fsw.EnableRaisingEvents = $true
  $watchers += $fsw
  foreach ($name in 'Created','Changed','Deleted','Renamed') {{ $registrations += Register-ObjectEvent -InputObject $fsw -EventName $name -SourceIdentifier ('CM_' + [guid]::NewGuid().ToString()) -MessageData @{{ root = $root; watchPath = $watchPath }} }}
}}
$deadline = (Get-Date).AddSeconds($timeout)
while ((Get-Date) -lt $deadline) {{
  $evt = Wait-Event -Timeout 1
  if ($null -eq $evt) {{ continue }}
  $args = $evt.SourceEventArgs
  $msg = $evt.MessageData
  $fullPath = if ($args -and $args.FullPath) {{ $args.FullPath }} elseif ($args -and $args.Name) {{ Join-Path $msg.watchPath $args.Name }} else {{ '' }}
  $kind = if ($args -and $args.ChangeType) {{ $args.ChangeType.ToString().ToLowerInvariant() }} else {{ $evt.EventName.ToLowerInvariant() }}
  if ($kind -eq 'changed') {{ $kind = 'updated' }}
  if ($kind -eq 'renamed') {{ $kind = 'updated' }}
  [void]$rows.Add([pscustomobject]@{{ full_path = $fullPath; change_type = $kind; detected_ts = (Get-Date).ToUniversalTime().ToString('o'); watch_root = $msg.root }})
  Remove-Event -EventIdentifier $evt.EventIdentifier | Out-Null
  Unregister-Event -SourceIdentifier $evt.SourceIdentifier -ErrorAction SilentlyContinue
}}
foreach ($registration in $registrations) {{ try {{ Unregister-Event -SubscriptionId $registration.Id -ErrorAction SilentlyContinue }} catch {{}} }}
foreach ($watcher in $watchers) {{ try {{ $watcher.EnableRaisingEvents = $false; $watcher.Dispose() }} catch {{}} }}
$rows | ConvertTo-Json -Depth 4 -Compress
"""
        with tempfile.NamedTemporaryFile("w", suffix=".ps1", delete=False, encoding="utf-8") as handle:
            handle.write(script)
            script_path = Path(handle.name)
        try:
            result = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script_path)], capture_output=True, text=True, timeout=max(int(timeout_secs) + 10, 15), check=False)
            if result.returncode != 0 or not result.stdout.strip():
                return []
            payload = json.loads(result.stdout.strip())
            if isinstance(payload, dict):
                return [payload]
            if isinstance(payload, list):
                return [row for row in payload if isinstance(row, dict)]
            return []
        except Exception:
            return []
        finally:
            try:
                script_path.unlink(missing_ok=True)
            except Exception:
                pass

    def watch_command_folder(self: Any, *, once: bool = False, timeout_secs: int = 0, bootstrap_existing: bool = False, emit_only: bool = False, source_ids: Any = None) -> dict[str, Any]:
        self.ensure_protocol_artifacts()
        mutable_state = self.load_state()
        surfaces = _surface_rows(self, source_ids)
        known_files = mutable_state.setdefault("known_files", {})
        if not isinstance(known_files, dict):
            known_files = {}
            mutable_state["known_files"] = known_files
        snapshots: dict[str, dict[str, Any]] = {}
        for surface in surfaces:
            snapshots.update(self._snapshot_surface(surface))
        emitted_ids: list[str] = []
        if not known_files and not bootstrap_existing:
            mutable_state["known_files"] = {key: dict(value) for key, value in snapshots.items()}
            self.save_state(mutable_state)
            self.sync_public_surfaces()
            return {
                "generated_at": utc_now(),
                "watch_scope": WATCH_SCOPE_LABEL,
                "watcher_mode": "event-driven" if self.native_watch_available() else "polling",
                "fallback_mode": "polling",
                "polling_fallback_used": not self.native_watch_available(),
                "degraded_mode": not self.native_watch_available(),
                "bootstrap_mode": "primed-without-emission",
                "event_count": 0,
                "event_ids": [],
                "source_ids": [row.get("source_id") for row in surfaces],
            }
        for relative_path, current in snapshots.items():
            previous = known_files.get(relative_path)
            if previous is None:
                if bootstrap_existing or known_files:
                    packet = self.emit_change(source_path=current["absolute_path"], change_type="created", detected_ts=utc_now(), state=mutable_state, source_ids=[current["source_id"]])
                    if packet is not None:
                        emitted_ids.append(packet.event_id)
                        if not emit_only:
                            self.route_event(packet.event_id, state=mutable_state)
            elif str(previous.get("state_hash") or "") != str(current.get("state_hash") or ""):
                packet = self.emit_change(source_path=current["absolute_path"], change_type="updated", detected_ts=utc_now(), state=mutable_state, source_ids=[current["source_id"]])
                if packet is not None:
                    emitted_ids.append(packet.event_id)
                    if not emit_only:
                        self.route_event(packet.event_id, state=mutable_state)
        watched_source_ids = {str(surface.get("source_id") or "") for surface in surfaces}
        current_keys = set(snapshots.keys())
        for relative_path, previous in list(known_files.items()):
            if str(previous.get("source_id") or "") not in watched_source_ids or relative_path in current_keys:
                continue
            packet = self.emit_change(source_path=ROOT / relative_path, change_type="deleted", detected_ts=utc_now(), state=mutable_state, source_ids=[previous.get("source_id")])
            if packet is not None:
                emitted_ids.append(packet.event_id)
                if not emit_only:
                    self.route_event(packet.event_id, state=mutable_state)
            known_files.pop(relative_path, None)
        mutable_state["known_files"] = {key: dict(value) for key, value in snapshots.items()}
        self.save_state(mutable_state)
        native = self.native_watch_available()
        native_rows: list[dict[str, Any]] = []
        if not once and native:
            native_rows = self._native_watch_rows(surfaces, timeout_secs if timeout_secs > 0 else 60)
            for row in native_rows:
                full_path = str(row.get("full_path") or "").strip()
                if not full_path:
                    continue
                packet = self.emit_change(source_path=full_path, change_type=str(row.get("change_type") or "updated"), detected_ts=str(row.get("detected_ts") or utc_now()), state=mutable_state, source_ids=source_ids)
                if packet is not None:
                    emitted_ids.append(packet.event_id)
                    if not emit_only:
                        self.route_event(packet.event_id, state=mutable_state)
        self.sync_public_surfaces(event_id=emitted_ids[-1] if emitted_ids else None)
        return {
            "generated_at": utc_now(),
            "watch_scope": WATCH_SCOPE_LABEL,
            "watcher_mode": "event-driven" if native else "polling",
            "fallback_mode": "polling",
            "polling_fallback_used": not native,
            "degraded_mode": not native,
            "source_ids": [row.get("source_id") for row in surfaces],
            "event_count": len(emitted_ids),
            "event_ids": emitted_ids,
            "native_event_count": len(native_rows),
            "bootstrap_existing": bool(bootstrap_existing),
            "emit_only": bool(emit_only),
        }

    CommandMembraneService.native_watch_available = native_watch_available
    CommandMembraneService.watched_surface_registry = watched_surface_registry
    CommandMembraneService.selected_surface_rows = selected_surface_rows
    CommandMembraneService.current_runtime_truth = current_runtime_truth
    CommandMembraneService.metrics = metrics
    CommandMembraneService.next_event_id = next_event_id
    CommandMembraneService.next_liminal_ts = next_liminal_ts
    CommandMembraneService.state_hash_for_path = state_hash_for_path
    CommandMembraneService.event_fingerprint = event_fingerprint
    CommandMembraneService.source_region_for_surface = source_region_for_surface
    CommandMembraneService.source_class_match_score = source_class_match_score
    CommandMembraneService.coord12_for_file = coord12_for_file
    CommandMembraneService.coord_delta_from_prior = coord_delta_from_prior
    CommandMembraneService.active_candidates = active_candidates
    CommandMembraneService.score_candidate = score_candidate
    CommandMembraneService.route_event = route_event
    CommandMembraneService.source_health = source_health
    CommandMembraneService.public_state = public_state
    CommandMembraneService.sync_public_surfaces = sync_public_surfaces
    CommandMembraneService.write_live_writeback_surfaces = write_live_writeback_surfaces
    CommandMembraneService.ensure_protocol_artifacts = ensure_protocol_artifacts
    CommandMembraneService.emit_change = emit_change
    CommandMembraneService._snapshot_surface = _snapshot_surface
    CommandMembraneService._native_watch_rows = _native_watch_rows
    CommandMembraneService.watch_command_folder = watch_command_folder
