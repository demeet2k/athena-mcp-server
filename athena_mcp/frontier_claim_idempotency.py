from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Any

from .frontier_claim import (
    FRONTIER_CLAIM_TOOLS,
    FrontierClaimRuntime,
    _claim_path,
    _event_path,
    _provider_packet,
    _safe_id,
    _sha,
)


def _parse_operation_at(value: str) -> datetime:
    text = str(value or "").strip()
    if not text:
        raise ValueError("operation_at is required")
    normalized = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError("operation_at must be ISO-8601 with timezone") from exc
    if parsed.tzinfo is None:
        raise ValueError("operation_at must include timezone")
    return parsed.astimezone(timezone.utc)


def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _operation_id(*, address: dict, run_id: str, node_id: str, operation_at: str, kind: str, lease_seconds: int | None = None) -> str:
    basis: dict[str, Any] = {
        "address": address,
        "run_id": run_id,
        "node_id": node_id,
        "operation_at": operation_at,
        "kind": kind,
    }
    if lease_seconds is not None:
        basis["lease_seconds"] = int(lease_seconds)
    return _sha(basis)


def _prepare_readiness(runtime: FrontierClaimRuntime, packet: dict, run_id: str, node_id: str, operation_at: datetime) -> dict:
    manifest = runtime._manifest(packet, run_id)
    runtime._node(manifest, node_id)
    events = runtime._events(packet, run_id)
    entry = runtime._run_projection(packet, run_id) or {}
    projection = entry.get("projection") or {}
    state = (projection.get("node_states") or {}).get(node_id)
    if state != "PENDING":
        raise ValueError(f"readiness prerequisite requires PENDING, found {state}")
    routing = next(
        (
            x for x in packet.get("routing_ready_work") or []
            if str(x.get("run_id")) == run_id and str(x.get("node_id")) == node_id
        ),
        None,
    )
    if routing is None:
        raise ValueError("node is not dependency-ready")
    sequence = len(events) + 1
    address = {
        "source_head": packet.get("source_head"),
        "frontier_digest": packet.get("frontier_digest"),
        "prompt_stack_digest": packet.get("prompt_stack_digest"),
    }
    at = _iso(operation_at)
    op_id = _operation_id(
        address=address,
        run_id=run_id,
        node_id=node_id,
        operation_at=at,
        kind="NODE_READY",
    )
    event_id = f"node-ready-{op_id[:24]}"
    event = {
        "schema_version": "EVENT_V1",
        "event_id": event_id,
        "sequence": sequence,
        "run_id": run_id,
        "event_type": "NODE_READY",
        "at": at,
        "node_id": node_id,
        "data": {},
    }
    after = runtime.frontier._reduce_events(manifest, [*events, event])
    if (after.get("node_states") or {}).get(node_id) != "READY":
        raise ValueError("NODE_READY prerequisite does not reduce to READY")
    provider = _provider_packet(_event_path(run_id, sequence), event, kind="EVENT_V1")
    return {
        "status": "NODE_READY_APPEND_PREPARED",
        "run_id": run_id,
        "node_id": node_id,
        "operation_id": op_id,
        "operation_at": at,
        "basis_stream_digest": _sha(events),
        "sequence": sequence,
        "event_id": event_id,
        "provider": provider,
        "prepared_packet_digest": _sha(provider),
        "projection_after": after,
        "law": "SAME_ADDRESS_OPERATION_AT => SAME_NODE_READY_PACKET; PREPARED != PERSISTED",
    }


def _prepare_claim(runtime: FrontierClaimRuntime, packet: dict, run_id: str, node_id: str, worker_role: str | None, lease_seconds: int, operation_at: datetime) -> dict:
    manifest = runtime._manifest(packet, run_id)
    node = runtime._node(manifest, node_id)
    entry = runtime._run_projection(packet, run_id) or {}
    projection = entry.get("projection") or {}
    if (projection.get("node_states") or {}).get(node_id) != "READY":
        raise ValueError("claim preparation requires reducer state READY")
    if runtime._claim_exists(packet, run_id, node_id):
        raise ValueError("fixed claim path already exists")
    role = str(node.get("role_capability") or "")
    if worker_role is not None and str(worker_role) != role:
        raise ValueError(f"worker_role mismatch: expected {role!r}")
    _safe_id(role, "worker_role")
    attempts = int((projection.get("attempts") or {}).get(node_id) or 0)
    attempt = attempts + 1
    max_attempts = int(node.get("max_attempts") or 0)
    if attempt <= 0 or attempt > max_attempts:
        raise ValueError("claim attempt exceeds node max_attempts")
    policy_commit = str(manifest.get("policy_commit") or "")
    if not policy_commit:
        raise ValueError("run policy_commit is required")
    lease_seconds = max(60, min(int(lease_seconds), 3600))
    events = runtime._events(packet, run_id)
    at = _iso(operation_at)
    expires_at = _iso(operation_at + timedelta(seconds=lease_seconds))
    address = {
        "source_head": packet.get("source_head"),
        "frontier_digest": packet.get("frontier_digest"),
        "prompt_stack_digest": packet.get("prompt_stack_digest"),
    }
    op_id = _operation_id(
        address=address,
        run_id=run_id,
        node_id=node_id,
        operation_at=at,
        kind="CLAIM_V1",
        lease_seconds=lease_seconds,
    )
    snapshot = {
        **address,
        "run_id": run_id,
        "node_id": node_id,
        "event_stream_digest": _sha(events),
        "operation_id": op_id,
    }
    claim = {
        "schema_version": "CLAIM_V1",
        "run_id": run_id,
        "node_id": node_id,
        "worker_role": role,
        "attempt": attempt,
        "policy_commit": policy_commit,
        "claimed_at": at,
        "lease_expires_at": expires_at,
        "input_snapshot_digest": _sha(snapshot),
        "production_authority": "HOLD",
    }
    path = _claim_path(run_id, node_id)
    if str(node.get("claim_path") or "") != path:
        raise ValueError("manifest claim_path does not match fixed provider path")
    provider = _provider_packet(path, claim, kind="CLAIM_V1")
    return {
        "status": "CLAIM_EFFECT_PREPARED",
        "run_id": run_id,
        "node_id": node_id,
        "worker_role": role,
        "attempt": attempt,
        "operation_id": op_id,
        "operation_at": at,
        "execute_before": expires_at,
        "claim_path": path,
        "basis_stream_digest": _sha(events),
        "claim_digest": _sha(claim),
        "provider": provider,
        "prepared_packet_digest": _sha(provider),
        "law": "SAME_ADDRESS_OPERATION_AT => SAME_CLAIM_PACKET; PREPARED != CLAIM_CREATED",
    }


def install_frontier_claim_idempotency(runtime_cls=FrontierClaimRuntime, tools: list[dict] | None = None) -> None:
    if getattr(runtime_cls, "_athena_claim_prepare_idempotency_v1_registered", False):
        return
    tool_list = FRONTIER_CLAIM_TOOLS if tools is None else tools
    original_claim_prepare = runtime_cls.claim_prepare
    original_call_tool = runtime_cls.call_tool

    def claim_prepare_deterministic(
        self,
        *,
        expected_source_head: str,
        expected_frontier_digest: str,
        expected_prompt_stack_digest: str,
        expected_claim_contract_digest: str,
        run_id: str,
        node_id: str,
        operation_at: str,
        worker_role: str | None = None,
        lease_seconds: int = 900,
        **kwargs,
    ) -> dict:
        operation_dt = _parse_operation_at(operation_at)
        kwargs = dict(kwargs)
        kwargs["fetch"] = True
        packet = self.frontier.hydrate(**kwargs)
        contract = self._contract(packet["source_head"])
        expected = {
            "source_head": expected_source_head,
            "frontier_digest": expected_frontier_digest,
            "prompt_stack_digest": expected_prompt_stack_digest,
            "claim_contract_digest": expected_claim_contract_digest,
        }
        changed = self._changed(expected, packet, contract)
        if any(changed.values()):
            return {
                "status": "CLAIM_STALE_ADDRESS_HOLD",
                "changed": changed,
                "current": {
                    "source_head": packet.get("source_head"),
                    "frontier_digest": packet.get("frontier_digest"),
                    "prompt_stack_digest": packet.get("prompt_stack_digest"),
                    "claim_contract_digest": contract.get("claim_contract_digest"),
                    "remote_checked": packet.get("remote_checked"),
                },
                "law": "STALE_H_P_F_C_W -> REHYDRATE_BEFORE_PROVIDER_EFFECT",
            }
        if packet.get("status") != "HYDRATED":
            return {"status": "CLAIM_FRONTIER_HOLD", "reason": packet.get("status"), "claim_contract": contract}
        if contract.get("status") != "PASS":
            return {
                "status": "CLAIM_CONTRACT_HOLD",
                "claim_contract": contract,
                "law": "UNMERGED_OR_DRIFTED_JOURNAL_CONTRACT != EXECUTION_AUTHORITY",
            }
        safe_run = _safe_id(run_id, "run_id")
        safe_node = _safe_id(node_id, "node_id")
        claimable = next(
            (
                x for x in packet.get("claimable_work") or []
                if str(x.get("run_id")) == safe_run and str(x.get("node_id")) == safe_node
            ),
            None,
        )
        if claimable is None:
            routing = next(
                (
                    x for x in packet.get("routing_ready_work") or []
                    if str(x.get("run_id")) == safe_run and str(x.get("node_id")) == safe_node
                ),
                None,
            )
            if routing is not None:
                return {
                    "status": "EVENT_READY_REQUIRED_HOLD",
                    "run_id": safe_run,
                    "node_id": safe_node,
                    "reducer_state": routing.get("reducer_state"),
                    "readiness_prerequisite": _prepare_readiness(self, packet, safe_run, safe_node, operation_dt),
                    "law": "INFERRED_READY != EVENT_READY; persist and rehydrate NODE_READY before claim preparation",
                }
            return {
                "status": "CLAIM_NODE_NOT_EVENT_READY_HOLD",
                "run_id": safe_run,
                "node_id": safe_node,
                "law": "CLAIM_PREPARE_REQUIRES_EVENT_READY",
            }
        prepared = _prepare_claim(self, packet, safe_run, safe_node, worker_role, lease_seconds, operation_dt)
        prepared["address"] = {
            "source_head": packet.get("source_head"),
            "frontier_digest": packet.get("frontier_digest"),
            "prompt_stack_digest": packet.get("prompt_stack_digest"),
            "claim_contract_digest": contract.get("claim_contract_digest"),
            "remote_checked": packet.get("remote_checked"),
        }
        prepared["claim_contract"] = contract
        return prepared

    def call_tool_deterministic(self, name: str, arguments: dict) -> dict:
        if name == "athena_frontier_claim_prepare":
            common = {
                "task": arguments.get("task", ""),
                "profile": arguments.get("profile"),
                "source_ref": arguments.get("source_ref", "athena-runtime-v3-candidate"),
                "remote": arguments.get("remote", "origin"),
                "fetch": arguments.get("fetch", True),
            }
            return self.claim_prepare(
                expected_source_head=arguments["expected_source_head"],
                expected_frontier_digest=arguments["expected_frontier_digest"],
                expected_prompt_stack_digest=arguments["expected_prompt_stack_digest"],
                expected_claim_contract_digest=arguments["expected_claim_contract_digest"],
                run_id=arguments["run_id"],
                node_id=arguments["node_id"],
                operation_at=arguments["operation_at"],
                worker_role=arguments.get("worker_role"),
                lease_seconds=arguments.get("lease_seconds", 900),
                **common,
            )
        return original_call_tool(self, name, arguments)

    runtime_cls.claim_prepare = claim_prepare_deterministic
    runtime_cls.call_tool = call_tool_deterministic

    for tool in tool_list:
        if tool.get("name") != "athena_frontier_claim_prepare":
            continue
        schema = tool.setdefault("inputSchema", {})
        required = schema.setdefault("required", [])
        if "operation_at" not in required:
            required.append("operation_at")
        properties = schema.setdefault("properties", {})
        properties["operation_at"] = {
            "type": "string",
            "description": "Caller-generated ISO-8601 timestamp with timezone. Preserve it across retries to obtain a byte-identical prepared provider packet for the same freshness address.",
        }

    runtime_cls._athena_claim_prepare_idempotency_v1_registered = True
