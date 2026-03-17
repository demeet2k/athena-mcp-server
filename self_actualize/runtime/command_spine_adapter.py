from __future__ import annotations

from dataclasses import asdict, is_dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from .command_spine import (
    COMMAND_COORD12_LABELS,
    DEFAULT_COMMAND_SURFACE as DEFAULT_COMMAND_SURFACE_ROOT,
    DEFAULT_SPINE_ROOT,
    FIRST_WAVE_WATCHED_SURFACES,
    ROOT,
    SELF_ROOT,
    CommandMembraneConfig,
    CommandMembraneService as BaseCommandMembraneService,
    read_json,
    rel,
    utc_now,
    write_json,
)

PROTOCOL_ID = "LP57OMEGA_COMMAND_MEMBRANE_V1"
COMMAND_ROUTE_CLASS = "scout.router.worker.archivist"
COMMAND_ROUTE_POLICY = "goal+salience+pheromone+coord"
WATCH_MODE_EVENT = "event-driven"
WATCH_MODE_DEGRADED = "snapshot-diff-degraded"
CAPILLARY_FORMULA = "C_next = clamp(0,1, rho*C + alpha*U + beta*F - gamma*D - delta*N)"
LATENCY_FORMULA = "T_sugar = T_detect + T_encode + T_route + T_claim + T_commit"
COORD12_LABELS = list(COMMAND_COORD12_LABELS)
COORD12_FRAME_GROUPS = ["earth", "astro", "runtime", "liminal"]
LIMINAL_OVERLAY_AXES = ["Xs", "Ys", "Zs", "Ts", "Qs", "Rs", "Cs", "Fs", "Ms", "Ns", "Hs", "OmegaS"]
ROUTE_SELECTOR_TERMS = [
    "goal_fit",
    "salience",
    "capillary_strength",
    "coordinate_proximity",
    "freshness",
    "duplicate_penalty",
]
BENCHMARK_FIELDS = [
    "detect_latency",
    "awareness_latency",
    "claim_latency",
    "resolution_latency",
    "commit_latency",
    "T_detect_ms",
    "T_encode_ms",
    "T_route_ms",
    "T_claim_ms",
    "T_commit_ms",
    "T_sugar_ms",
    "capillary_score",
    "liminal_delta",
    "liminal_velocity",
]
relpath = rel


def _plain(value: Any) -> Any:
    if isinstance(value, SimpleNamespace):
        return {key: _plain(val) for key, val in vars(value).items()}
    if is_dataclass(value):
        return {key: _plain(val) for key, val in asdict(value).items()}
    if isinstance(value, dict):
        return {key: _plain(val) for key, val in value.items()}
    if isinstance(value, list):
        return [_plain(item) for item in value]
    return value


def _rel_to_root(path: Path | str, root: Path) -> str:
    target = Path(path)
    try:
        return target.relative_to(root).as_posix()
    except ValueError:
        return target.as_posix()


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def _normalized_coord12_frame(frame: Any) -> dict[str, Any]:
    payload = _plain(frame)
    if not isinstance(payload, dict):
        payload = {}
    payload.setdefault("earth", payload.get("earth") or [])
    payload.setdefault("astro", payload.get("astro") or [])
    payload.setdefault("runtime", payload.get("runtime") or [])
    payload.setdefault("liminal", payload.get("liminal") or [])
    payload.setdefault("coord12_labels", list(COORD12_LABELS))
    return payload


def _normalize_packet_fields(packet: Any) -> Any:
    state_hash = str(getattr(packet, "state_hash", "") or "")
    if state_hash and not state_hash.startswith("H:"):
        packet.state_hash = f"H:{state_hash}"
    if not getattr(packet, "canonical_addr_6d", "") and getattr(packet, "seat_addr_6d", ""):
        packet.canonical_addr_6d = packet.seat_addr_6d
    if not getattr(packet, "canonical_addr_6d", ""):
        packet.canonical_addr_6d = "A1.B1.C1.D1.E1.F1"
    if not getattr(packet, "docs_gate_status", ""):
        packet.docs_gate_status = "BLOCKED"
    if not getattr(packet, "witness_class", ""):
        packet.witness_class = "LOCAL_WITNESS_ONLY"
    packet.coord12_frame = _normalized_coord12_frame(getattr(packet, "coord12_frame", {}))
    latency_state = getattr(packet, "latency_state", {}) or {}
    if isinstance(latency_state, dict):
        latency_state.setdefault("route_policy", COMMAND_ROUTE_POLICY)
        packet.latency_state = latency_state
    route_state = getattr(packet, "route_state", {}) or {}
    if isinstance(route_state, dict):
        route_state.setdefault("policy_id", COMMAND_ROUTE_POLICY)
        packet.route_state = route_state
    return packet


class CommandMembraneService(BaseCommandMembraneService):
    def event_path(self, event_id: str) -> Path:
        return self.config.event_root / f"{event_id}.json"

    def ensure_protocol_artifacts(self) -> dict[str, Any]:
        artifacts = super().ensure_protocol_artifacts()
        docs_gate = self.docs_gate_status()

        protocol = read_json(self.config.protocol_json_path, {})
        protocol.update(
            {
                "protocol_id": PROTOCOL_ID,
                "route_policy": COMMAND_ROUTE_POLICY,
                "route_class": COMMAND_ROUTE_CLASS,
                "selector_terms": ROUTE_SELECTOR_TERMS,
                "docs_gate": docs_gate,
                "watch_mode": {
                    "primary": WATCH_MODE_EVENT,
                    "fallback": WATCH_MODE_DEGRADED,
                    "fallback_requires_explicit_opt_in": True,
                },
            }
        )
        write_json(self.config.protocol_json_path, protocol)
        write_json(self.config.protocol_v1_registry_path, protocol)

        schema = read_json(self.config.packet_schema_json_path, {})
        schema.update(
            {
                "coord12_labels": list(COORD12_LABELS),
                "coord12_frame_groups": list(COORD12_FRAME_GROUPS),
                "canonical_addr_6d": "A.B.C.D.E.F",
                "liminal_overlay_axes": list(LIMINAL_OVERLAY_AXES),
                "route_policy": COMMAND_ROUTE_POLICY,
            }
        )
        write_json(self.config.packet_schema_json_path, schema)

        capillary = read_json(self.config.capillary_law_json_path, {})
        capillary.update(
            {
                "formula": CAPILLARY_FORMULA,
                "edge_classes": ["route", "capillary", "vein"],
                "route_policy": COMMAND_ROUTE_POLICY,
            }
        )
        write_json(self.config.capillary_law_json_path, capillary)

        latency = read_json(self.config.latency_benchmark_json_path, {})
        latency.update(
            {
                "equation": LATENCY_FORMULA,
                "metrics": list(BENCHMARK_FIELDS),
                "prompt_level_liminal_gps": "supported",
                "keystroke_level_liminal_gps": "requires client/runtime instrumentation",
            }
        )
        write_json(self.config.latency_benchmark_json_path, latency)

        _write_text(
            self.config.command_manifest_path,
            "# COMMAND Membrane v1\n\n"
            "- Mode: `event-driven command membrane`\n"
            "- Watch scope: `GLOBAL COMMAND` only.\n"
            f"- Routing policy: `{COMMAND_ROUTE_POLICY}`\n"
            f"- Docs gate: `{docs_gate.get('state', 'BLOCKED')}` / `{docs_gate.get('witness_class', 'LOCAL_WITNESS_ONLY')}`\n"
            "- Prompt-level liminal GPS is supported; keystroke-level GPS still requires external instrumentation.\n",
        )
        _write_text(
            self.config.protocol_manifest_path,
            "# COMMAND Protocol\n\n"
            f"- Protocol id: `{PROTOCOL_ID}`\n"
            f"- Routing policy: `{COMMAND_ROUTE_POLICY}`\n"
            f"- Defaults: `topk={self.config.topk}`, `claim_mode={self.config.claim_mode}`, `quorum={self.config.quorum}`, `ttl={self.config.ttl}`, `lease_ms={self.config.lease_ms}`\n"
            f"- Benchmark: `{LATENCY_FORMULA}`\n",
        )
        _write_text(
            self.config.packet_manifest_path,
            "# COMMAND Packet Standard\n\n"
            "- Every detected change becomes a machine packet before routing.\n"
            "- Each packet carries both canonical 6D addressing and a 12D liminal overlay frame.\n"
            "- Prompt-level liminal GPS is supported now; keystroke-level requires client instrumentation.\n",
        )
        return artifacts

    def build(self) -> dict[str, Any]:
        artifacts = self.ensure_protocol_artifacts()
        public_state = self.sync_public_surfaces()
        return {
            "truth": "OK",
            "artifacts": {
                key: _rel_to_root(value, self.config.workspace_root)
                for key, value in artifacts.items()
                if isinstance(value, (str, Path))
            },
            "public_state": public_state,
        }

    def startup_snapshot_diff(self, bootstrap_existing: bool = False) -> list[dict[str, Any]]:
        state = self.load_state()
        previous = {} if bootstrap_existing else dict(state.get("known_files", {}) or {})
        current = self._command_protocol_snapshot()
        changes = self._command_protocol_compute_changes(previous, current)
        state["known_files"] = current
        state["watcher_mode"] = "polling" if bootstrap_existing else WATCH_MODE_EVENT
        self.save_state(state)

        emitted: list[dict[str, Any]] = []
        for change in changes:
            packet = self.emit_change(
                source_path=(self.config.command_surface_root / change["relative_path"]).resolve(strict=False),
                change_type=str(change["event_kind"]),
                detected_ts=utc_now(),
                state=state,
                source_ids=["command_root"],
            )
            if packet is not None:
                emitted.append(self.packet_to_summary(packet))
        self.sync_public_surfaces()
        return emitted

    def load_event(self, event_id: str) -> Any:
        packet = super().load_event(event_id)
        return _normalize_packet_fields(packet)

    def emit_change(self, *args: Any, **kwargs: Any) -> Any:
        packet = super().emit_change(*args, **kwargs)
        if packet is None:
            return None
        return _normalize_packet_fields(packet)

    def route_event(self, event_id: str, state: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = super().route_event(event_id, state=state)
        payload["policy"] = COMMAND_ROUTE_POLICY
        payload["policy_id"] = COMMAND_ROUTE_POLICY
        payload["route_class"] = COMMAND_ROUTE_CLASS
        payload["selector_terms"] = list(ROUTE_SELECTOR_TERMS)
        return payload

    def claim_event(self, event_id: str, ant_id: str | None = None, role: str = "worker", lease_ms: int | None = None) -> dict[str, Any]:
        payload = super().claim_event(event_id, ant_id=ant_id, role=role, lease_ms=lease_ms)
        payload.setdefault("event_id", event_id)
        return payload

    def commit_event(
        self,
        event_id: str,
        result: str,
        artifact_paths: list[str] | None = None,
        writeback_paths: list[str] | None = None,
        summary: str = "",
        work_started_at: str | None = None,
    ) -> dict[str, Any]:
        payload = super().commit_event(
            event_id,
            result=result,
            artifact_paths=artifact_paths,
            writeback_paths=writeback_paths,
            summary=summary,
            work_started_at=work_started_at,
        )
        if "latency" in payload:
            return payload
        latency_sample = dict(payload.get("latency_sample_v2") or {})
        execution_receipt = dict(payload.get("execution_receipt_v2") or {})
        return {
            "event_id": event_id,
            "result": execution_receipt.get("result", result),
            "summary": execution_receipt.get("summary", summary),
            "latency": {
                "detect_ms": latency_sample.get("detection_latency_ms", 0.0),
                "encode_ms": latency_sample.get("t_encode_ms", 0.0),
                "route_ms": latency_sample.get("t_route_ms", latency_sample.get("swarm_awareness_latency_ms", 0.0)),
                "claim_ms": latency_sample.get("t_claim_ms", latency_sample.get("claim_latency_ms", 0.0)),
                "commit_ms": latency_sample.get("t_commit_ms", latency_sample.get("commit_latency_ms", 0.0)),
                "awareness_ms": latency_sample.get("swarm_awareness_latency_ms", latency_sample.get("t_route_ms", 0.0)),
                "t_sugar_ms": latency_sample.get("t_sugar_ms", 0.0),
                "liminal_distance": latency_sample.get("liminal_delta", latency_sample.get("delta_tau", 0.0)),
                "liminal_velocity": latency_sample.get("liminal_velocity", 0.0),
            },
            "execution_receipt_v2": execution_receipt,
            "latency_sample_v2": latency_sample,
            "receipt_json": payload.get("receipt_json", ""),
            "receipt_md": payload.get("receipt_md", ""),
        }

    def packet_to_summary(self, packet: Any) -> dict[str, Any]:
        payload = _plain(packet)
        latency = _plain(payload.get("latency_state") or {})
        coord12_frame = _normalized_coord12_frame(payload.get("coord12_frame") or {})
        return {
            "event_id": payload.get("event_id", ""),
            "source_path": payload.get("source_path", ""),
            "relative_path": payload.get("relative_path") or payload.get("source_path", ""),
            "event_kind": payload.get("event_kind") or payload.get("change_type") or "",
            "status": payload.get("status", ""),
            "goal": payload.get("goal", ""),
            "priority": payload.get("priority", 0.0),
            "earth_ts": payload.get("earth_ts_utc") or payload.get("earth_ts") or "",
            "liminal_ts": payload.get("liminal_ts", ""),
            "canonical_addr_6d": payload.get("canonical_addr_6d") or payload.get("seat_addr_6d") or "A1.B1.C1.D1.E1.F1",
            "docs_gate_status": payload.get("docs_gate_status", self.docs_gate_status().get("state", "BLOCKED")),
            "route_targets": payload.get("selected_targets") or payload.get("route_targets") or [],
            "linked_quests": payload.get("linked_quests") or [],
            "coord12_frame": coord12_frame,
            "latency_state": latency,
        }

    def sync_public_surfaces(self, event_id: str | None = None) -> dict[str, Any]:
        payload = super().sync_public_surfaces(event_id=event_id)
        docs_gate = self.docs_gate_status()
        payload["generated_at"] = utc_now()
        payload["protocol_id"] = PROTOCOL_ID
        payload["canonical_authority"] = "LP57OMEGA / NEXT57"
        payload["watch_scope"] = "GLOBAL COMMAND authority + realtime board operational mirror"
        payload["docs_gate"] = docs_gate
        payload["docs_gate_status"] = docs_gate.get("state", "BLOCKED")

        current_runtime_truth = dict(payload.get("current_runtime_truth") or {})
        current_runtime_truth.setdefault("canonical_authority", "LP57OMEGA / NEXT57")
        current_runtime_truth.setdefault("active_loop", "L02")
        current_runtime_truth.setdefault("active_family", "A02 self_actualize")
        current_runtime_truth.setdefault("restart_seed", "L03 Survey A03 ECOSYSTEM")
        current_runtime_truth.setdefault("active_membrane", "Q41 / TQ06")
        current_runtime_truth.setdefault("feeders", ["Q42", "Q46", "TQ04", "Q02"])
        payload["current_runtime_truth"] = current_runtime_truth

        policy = dict(payload.get("policy") or {})
        policy["protocol_id"] = PROTOCOL_ID
        policy["routing_policy"] = COMMAND_ROUTE_POLICY
        policy["selector_terms"] = list(ROUTE_SELECTOR_TERMS)
        policy["topk"] = self.config.topk
        policy["claim_mode"] = self.config.claim_mode
        policy["quorum"] = self.config.quorum
        policy["ttl"] = self.config.ttl
        policy["lease_ms"] = self.config.lease_ms
        payload["policy"] = policy

        metrics = dict(payload.get("metrics") or {})
        if metrics:
            metrics["generated_at"] = utc_now()
            metrics["protocol_id"] = PROTOCOL_ID
            metrics["docs_gate_status"] = docs_gate.get("state", "BLOCKED")
            metrics["watch_scope"] = payload["watch_scope"]
            payload["metrics"] = metrics

        live_manifest = {
            "generated_at": utc_now(),
            "protocol_id": PROTOCOL_ID,
            "canonical_authority": "LP57OMEGA / NEXT57",
            "docs_gate_status": docs_gate.get("state", "BLOCKED"),
            "active_surface": "LOCAL SWARM MESH",
            "command_root": str(self.config.command_surface_root),
            "watch_scope": payload["watch_scope"],
            "watcher_mode": payload.get("watcher_mode", WATCH_MODE_EVENT),
            "active_membrane": current_runtime_truth.get("active_membrane", "Q41 / TQ06"),
            "feeder_stack": current_runtime_truth.get("feeders", ["Q42", "Q46", "TQ04", "Q02"]),
            "event_id": ((payload.get("last_event") or {}).get("event_id", "") if isinstance(payload.get("last_event"), dict) else ""),
            "policy": {
                "routing_policy": COMMAND_ROUTE_POLICY,
                "selector_terms": list(ROUTE_SELECTOR_TERMS),
                "topk": self.config.topk,
                "claim_mode": self.config.claim_mode,
                "quorum": self.config.quorum,
                "ttl": self.config.ttl,
                "lease_ms": self.config.lease_ms,
            },
            "outputs": {
                "watched_surfaces": payload.get("watched_surface_count", 0),
                "events": metrics.get("event_count", 0),
                "claims": metrics.get("claim_count", 0),
                "capillary_edges": metrics.get("edge_count", 0),
                "latency_rows": metrics.get("latency_row_count", 0),
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
        write_json(self.config.live_manifest_path, live_manifest)
        public_state_path = self.config.workspace_root / "NERVOUS_SYSTEM" / "95_MANIFESTS" / "COMMAND_MEMBRANE_STATE.json"
        write_json(public_state_path, payload)
        return payload

    def public_state(self) -> dict[str, Any]:
        return self.sync_public_surfaces()


__all__ = [
    "BENCHMARK_FIELDS",
    "CAPILLARY_FORMULA",
    "COMMAND_ROUTE_CLASS",
    "COMMAND_ROUTE_POLICY",
    "COORD12_FRAME_GROUPS",
    "COORD12_LABELS",
    "CommandMembraneConfig",
    "CommandMembraneService",
    "DEFAULT_COMMAND_SURFACE_ROOT",
    "DEFAULT_SPINE_ROOT",
    "FIRST_WAVE_WATCHED_SURFACES",
    "LATENCY_FORMULA",
    "LIMINAL_OVERLAY_AXES",
    "PROTOCOL_ID",
    "ROOT",
    "ROUTE_SELECTOR_TERMS",
    "SELF_ROOT",
    "WATCH_MODE_DEGRADED",
    "WATCH_MODE_EVENT",
    "Path",
    "read_json",
    "rel",
    "relpath",
    "utc_now",
    "write_json",
]
