from __future__ import annotations

from contextvars import ContextVar
import hashlib
import json
from typing import Any, Mapping

from .message_board import (
    EVENT_ARTIFACT,
    LAWS,
    MESSAGE_BOARD_TOOLS,
    PRESENCE_ARTIFACT,
    TOOL_NAME,
)
from .synapse_mcp_contract import (
    ENDPOINT_IDENTITY_ARTIFACT as IDENTITY_ARTIFACT,
    SYNAPSE_MCP_CONTRACT_DIGEST,
)


IDENTITY_FIELDS = {"artifact", "organ_id", "oid", "fingerprint", "lineage"}
_PENDING_ENDPOINT_IDENTITY: ContextVar[tuple[str, dict[str, Any], str] | None] = ContextVar(
    "athena_message_board_endpoint_identity_v1",
    default=None,
)


def _canonical(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def endpoint_identity_digest(identity: Mapping[str, Any]) -> str:
    normalized = normalize_endpoint_identity(identity)
    return "sha256:" + hashlib.sha256(_canonical(normalized).encode("utf-8")).hexdigest()


def normalize_endpoint_identity(value: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError("endpoint_identity must be an object")
    if set(value) != IDENTITY_FIELDS:
        raise ValueError("endpoint_identity fields must match the V1 contract exactly")
    if value.get("artifact") != IDENTITY_ARTIFACT:
        raise ValueError("unexpected endpoint_identity artifact")
    normalized: dict[str, Any] = {"artifact": IDENTITY_ARTIFACT}
    for field in ("organ_id", "oid", "lineage"):
        item = value.get(field)
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"endpoint_identity.{field} must be a non-empty string")
        normalized[field] = item.strip()
    fingerprint = value.get("fingerprint")
    if not isinstance(fingerprint, list) or not fingerprint:
        raise ValueError("endpoint_identity.fingerprint must be a non-empty string array")
    if any(not isinstance(item, str) or not item.strip() for item in fingerprint):
        raise ValueError("endpoint_identity.fingerprint entries must be non-empty strings")
    cleaned = [item.strip() for item in fingerprint]
    if len(cleaned) != len(set(cleaned)):
        raise ValueError("endpoint_identity.fingerprint entries must be unique")
    normalized["fingerprint"] = sorted(cleaned)
    return normalized


def _json_text(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _identity_schema() -> dict[str, Any]:
    return {
        "type": ["object", "null"],
        "required": ["artifact", "organ_id", "oid", "fingerprint", "lineage"],
        "properties": {
            "artifact": {"type": "string", "const": IDENTITY_ARTIFACT},
            "organ_id": {"type": "string", "minLength": 1},
            "oid": {"type": "string", "minLength": 1},
            "fingerprint": {
                "type": "array",
                "minItems": 1,
                "uniqueItems": True,
                "items": {"type": "string", "minLength": 1},
            },
            "lineage": {"type": "string", "minLength": 1},
        },
        "additionalProperties": False,
    }


def install_message_board_endpoint_identity(runtime_cls, tools=None) -> None:
    """Install optional federation endpoint identity without changing board authority."""
    if getattr(runtime_cls, "_athena_endpoint_identity_v1_registered", False):
        return

    tools = tools if tools is not None else MESSAGE_BOARD_TOOLS
    for tool in tools:
        if tool.get("name") == TOOL_NAME:
            tool["inputSchema"]["properties"]["endpoint_identity"] = _identity_schema()

    for law in (
        "AGENT_ID != FEDERATION_ORGAN_ID",
        "ENDPOINT_IDENTITY_BINDING != SOURCE_AUTHORITY",
        "ACK_IDENTITY_MUST_MATCH_SEND_TIME_TARGET_IDENTITY_FOR_BOUND_ROUTE",
        "SYNAPSE_CONTRACT_DIGEST_MUST_MATCH_BEFORE_BINDING",
    ):
        if law not in LAWS:
            LAWS.append(law)

    original_commit_files = runtime_cls._commit_files
    original_event = runtime_cls._event
    original_present = runtime_cls.present
    original_join = runtime_cls.join
    original_call_tool = runtime_cls.call_tool

    def _commit_files_with_endpoint_identity(self, expected_head, files, actor, message):
        pending = _PENDING_ENDPOINT_IDENTITY.get()
        if not pending or pending[0] != str(actor):
            return original_commit_files(self, expected_head, files, actor, message)
        _, identity, identity_digest = pending
        rewritten: dict[str, str] = {}
        for rel, text in files.items():
            try:
                value = json.loads(text)
            except (TypeError, json.JSONDecodeError):
                rewritten[rel] = text
                continue
            if not isinstance(value, dict) or value.get("agent_id") != actor:
                rewritten[rel] = text
                continue
            if value.get("artifact") == PRESENCE_ARTIFACT:
                value["endpoint_identity"] = identity
                value["endpoint_identity_digest"] = identity_digest
                value["synapse_contract_digest"] = SYNAPSE_MCP_CONTRACT_DIGEST
                rewritten[rel] = _json_text(value)
                continue
            if value.get("artifact") == EVENT_ARTIFACT and value.get("kind") in {"PRESENT", "JOIN"}:
                payload = dict(value.get("payload") or {})
                payload["actor_endpoint_identity_digest"] = identity_digest
                payload["synapse_contract_digest"] = SYNAPSE_MCP_CONTRACT_DIGEST
                value["payload"] = payload
                rewritten[rel] = _json_text(value)
                continue
            rewritten[rel] = text
        return original_commit_files(self, expected_head, rewritten, actor, message)

    def _event_with_endpoint_identity(self, kind, agent_id, payload=None, recipients=None, reply_to=None):
        rel, event = original_event(
            self,
            kind,
            agent_id,
            payload=payload,
            recipients=recipients,
            reply_to=reply_to,
        )
        active = self._active()
        by_agent = {str(row.get("agent_id")): row for row in active}
        actor = by_agent.get(str(agent_id))
        actor_digest = actor.get("endpoint_identity_digest") if actor else None
        event_payload = dict(event.get("payload") or {})
        if actor_digest:
            event_payload["actor_endpoint_identity_digest"] = actor_digest
        if kind == "MESSAGE":
            event_payload["recipient_endpoint_identity_digests"] = {
                str(recipient): by_agent[str(recipient)]["endpoint_identity_digest"]
                for recipient in list(recipients or [])
                if str(recipient) in by_agent and by_agent[str(recipient)].get("endpoint_identity_digest")
            }
        if kind in {"MESSAGE", "ACK"}:
            event_payload["synapse_contract_digest"] = SYNAPSE_MCP_CONTRACT_DIGEST
        event["payload"] = event_payload
        return rel, event

    def _finish_identity_result(result, normalized, identity_digest):
        if not normalized or not isinstance(result, dict):
            return result
        presence = result.get("presence")
        if not isinstance(presence, dict):
            return result
        if result.get("status") in {"PRESENT", "JOINED"}:
            enriched = dict(presence)
            enriched["endpoint_identity"] = normalized
            enriched["endpoint_identity_digest"] = identity_digest
            enriched["synapse_contract_digest"] = SYNAPSE_MCP_CONTRACT_DIGEST
            updated = dict(result)
            updated["presence"] = enriched
            return updated
        existing_digest = presence.get("endpoint_identity_digest")
        existing_contract = presence.get("synapse_contract_digest")
        if existing_digest != identity_digest or existing_contract != SYNAPSE_MCP_CONTRACT_DIGEST:
            held = dict(result)
            held["status"] = (
                "ENDPOINT_IDENTITY_MISSING_HOLD"
                if not existing_digest
                else "ENDPOINT_IDENTITY_MISMATCH_HOLD"
            )
            held["requested_endpoint_identity_digest"] = identity_digest
            held["existing_endpoint_identity_digest"] = existing_digest
            held["requested_synapse_contract_digest"] = SYNAPSE_MCP_CONTRACT_DIGEST
            held["existing_synapse_contract_digest"] = existing_contract
            held["next"] = "release current presence before changing endpoint identity or contract"
            return held
        return result

    def present_with_endpoint_identity(
        self,
        *,
        agent_id,
        task,
        work_key=None,
        targets=None,
        details=None,
        mode="PRIMARY",
        replication_reason=None,
        lease_seconds=1800,
        remote="origin",
        endpoint_identity=None,
    ):
        normalized = normalize_endpoint_identity(endpoint_identity) if endpoint_identity is not None else None
        identity_digest = endpoint_identity_digest(normalized) if normalized else None
        token = (
            _PENDING_ENDPOINT_IDENTITY.set((str(agent_id), normalized, identity_digest))
            if normalized
            else None
        )
        try:
            result = original_present(
                self,
                agent_id=agent_id,
                task=task,
                work_key=work_key,
                targets=targets,
                details=details,
                mode=mode,
                replication_reason=replication_reason,
                lease_seconds=lease_seconds,
                remote=remote,
            )
        finally:
            if token is not None:
                _PENDING_ENDPOINT_IDENTITY.reset(token)
        return _finish_identity_result(result, normalized, identity_digest)

    def join_with_endpoint_identity(
        self,
        *,
        agent_id,
        join_agent_id,
        task=None,
        details=None,
        lease_seconds=1800,
        remote="origin",
        endpoint_identity=None,
    ):
        normalized = normalize_endpoint_identity(endpoint_identity) if endpoint_identity is not None else None
        identity_digest = endpoint_identity_digest(normalized) if normalized else None
        token = (
            _PENDING_ENDPOINT_IDENTITY.set((str(agent_id), normalized, identity_digest))
            if normalized
            else None
        )
        try:
            result = original_join(
                self,
                agent_id=agent_id,
                join_agent_id=join_agent_id,
                task=task,
                details=details,
                lease_seconds=lease_seconds,
                remote=remote,
            )
        finally:
            if token is not None:
                _PENDING_ENDPOINT_IDENTITY.reset(token)
        return _finish_identity_result(result, normalized, identity_digest)

    def call_tool_with_endpoint_identity(self, name, arguments):
        if name == TOOL_NAME:
            action = str(arguments.get("action") or "").lower()
            if action == "present" and arguments.get("endpoint_identity") is not None:
                return self.present(
                    agent_id=arguments["agent_id"],
                    task=arguments["task"],
                    work_key=arguments.get("work_key"),
                    targets=arguments.get("targets") or [],
                    details=arguments.get("details"),
                    mode=arguments.get("mode", "PRIMARY"),
                    replication_reason=arguments.get("replication_reason"),
                    lease_seconds=arguments.get("lease_seconds", 1800),
                    remote=arguments.get("remote", "origin"),
                    endpoint_identity=arguments.get("endpoint_identity"),
                )
            if action == "join" and arguments.get("endpoint_identity") is not None:
                return self.join(
                    agent_id=arguments["agent_id"],
                    join_agent_id=arguments["join_agent_id"],
                    task=arguments.get("task"),
                    details=arguments.get("details"),
                    lease_seconds=arguments.get("lease_seconds", 1800),
                    remote=arguments.get("remote", "origin"),
                    endpoint_identity=arguments.get("endpoint_identity"),
                )
        return original_call_tool(self, name, arguments)

    runtime_cls._commit_files = _commit_files_with_endpoint_identity
    runtime_cls._event = _event_with_endpoint_identity
    runtime_cls.present = present_with_endpoint_identity
    runtime_cls.join = join_with_endpoint_identity
    runtime_cls.call_tool = call_tool_with_endpoint_identity
    runtime_cls._athena_endpoint_identity_v1_registered = True
