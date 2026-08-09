from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Mapping

ARTIFACT = "ATHENA.AGENT.BOOT.PROJECT.MEMORY.V1"
SOURCE_ARTIFACT = "ATHENA.PROJECT.MEMORY.BOOT.PACKET.V1"
STANDING = "ROUTING_CONTEXT_ONLY_NOT_EVIDENCE"
_ALLOWED_STATUS = {
    "PROJECT_MEMORY_NOT_SELECTED",
    "PROJECT_MEMORY_OPTIONAL_HOLD",
    "PROJECT_MEMORY_REQUIRED_HOLD",
    "PROJECT_MEMORY_HYDRATED",
}
_ALLOWED_KEYS = {
    "artifact", "status", "required", "blocks_boot", "query", "policy", "policy_digest",
    "source_stack", "source_state_digest", "retrieval_digest", "selected",
    "selected_content_bytes", "holds", "standing", "laws", "packet_digest",
}
_FORBIDDEN_KEY_PARTS = (
    "authorization", "password", "passwd", "secret", "private_key", "access_token",
    "refresh_token", "github_token", "gh_token", "bearer", "chain_of_thought", "hidden_reasoning",
)
_SECRET_TEXT = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"(?i)authorization\s*:\s*bearer\s+[A-Za-z0-9._~+/=-]{12,}"),
)
_LAWS = [
    "PROJECT_MEMORY != PROMPT_POLICY",
    "PROJECT_MEMORY != SCHED_FRONTIER",
    "PROJECT_MEMORY != ISSUE_PRESSURE",
    "PROJECT_MEMORY != CONTINUATION_STATE",
    "PROJECT_MEMORY != EXECUTION_AUTHORITY",
    "RETRIEVED_MEMORY != EVIDENCE",
    "RETRIEVED_MEMORY != FACTUAL_TRUTH",
    "MEMORY_QUERY != SCHED_READY",
    "INVALID_MEMORY_PACKET != EMPTY_MEMORY",
]
_REQUEST_KEYS = ("project_memory_packet", "project_memory_selected", "project_memory_required")


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha(value: Any) -> str:
    if isinstance(value, bytes):
        raw = value
    elif isinstance(value, str):
        raw = value.encode("utf-8")
    else:
        raw = _canonical(value)
    return hashlib.sha256(raw).hexdigest()


def _clone(value: Any) -> Any:
    return json.loads(json.dumps(value, ensure_ascii=False))


def _reject_private(value: Any, path: str = "$") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            lowered = str(key).casefold()
            if any(part in lowered for part in _FORBIDDEN_KEY_PARTS):
                raise ValueError(f"forbidden project-memory field at {path}.{key}")
            _reject_private(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_private(child, f"{path}[{index}]")
    elif isinstance(value, str) and any(pattern.search(value) for pattern in _SECRET_TEXT):
        raise ValueError(f"credential-like project-memory content at {path}")


def _minimal(status: str, *, task: str, required: bool, reason: str | None = None) -> dict:
    basis = {
        "artifact": ARTIFACT,
        "status": status,
        "required": bool(required),
        "blocks_boot": bool(required and status == "PROJECT_MEMORY_REQUIRED_HOLD"),
        "query_digest": _sha(task or ""),
        "reason": reason,
        "standing": STANDING,
        "laws": list(_LAWS),
    }
    basis["packet_digest"] = _sha(basis)
    return basis


def _validated_packet(packet: Mapping[str, Any]) -> dict:
    if not isinstance(packet, Mapping):
        raise ValueError("project_memory_packet must be an object")
    packet = _clone(packet)
    _reject_private(packet)
    extra = set(packet) - _ALLOWED_KEYS
    if extra:
        raise ValueError(f"unexpected project-memory fields: {sorted(extra)}")
    if packet.get("artifact") != SOURCE_ARTIFACT:
        raise ValueError("wrong project-memory artifact")
    status = str(packet.get("status") or "")
    if status not in _ALLOWED_STATUS:
        raise ValueError("invalid project-memory status")
    if packet.get("standing") != STANDING:
        raise ValueError("invalid project-memory standing")
    digest = str(packet.get("packet_digest") or "")
    basis = dict(packet)
    basis.pop("packet_digest", None)
    if digest != _sha(basis):
        raise ValueError("project-memory packet digest mismatch")
    required = bool(packet.get("required"))
    blocks = bool(packet.get("blocks_boot"))
    if status == "PROJECT_MEMORY_REQUIRED_HOLD" and not (required and blocks):
        raise ValueError("required HOLD must be required and blocking")
    if status != "PROJECT_MEMORY_REQUIRED_HOLD" and blocks:
        raise ValueError("only required HOLD may block boot")
    selected = packet.get("selected")
    if not isinstance(selected, list):
        raise ValueError("project-memory selected must be a list")
    if status != "PROJECT_MEMORY_HYDRATED" and selected:
        raise ValueError("non-hydrated project-memory packet cannot carry selected content")
    return packet


def _request_from(source: Mapping[str, Any] | None, fallback: Mapping[str, Any] | None = None) -> dict:
    result = dict(fallback or {})
    if source:
        for key in _REQUEST_KEYS:
            if key in source and source.get(key) is not None:
                result[key] = source.get(key)
    return result


def _attach(packet: dict, request: Mapping[str, Any]) -> dict:
    if not isinstance(packet, dict):
        return packet
    task = str(packet.get("task") or "")
    supplied = request.get("project_memory_packet")
    selected = request.get("project_memory_selected")
    required = bool(request.get("project_memory_required", False))
    if selected is None:
        selected = supplied is not None
    selected = bool(selected or required)

    if not selected:
        memory = _minimal("PROJECT_MEMORY_NOT_SELECTED", task=task, required=False)
    elif supplied is None:
        memory = _minimal(
            "PROJECT_MEMORY_REQUIRED_HOLD" if required else "PROJECT_MEMORY_OPTIONAL_HOLD",
            task=task,
            required=required,
            reason="PROJECT_MEMORY_PACKET_UNAVAILABLE",
        )
    else:
        try:
            memory = _validated_packet(supplied)
            if required and not bool(memory.get("required")):
                raise ValueError("required request cannot be satisfied by optional memory packet")
            required = bool(required or memory.get("required"))
        except Exception as exc:
            memory = _minimal(
                "PROJECT_MEMORY_REQUIRED_HOLD" if required else "PROJECT_MEMORY_OPTIONAL_HOLD",
                task=task,
                required=required,
                reason=f"PROJECT_MEMORY_PACKET_INVALID:{type(exc).__name__}",
            )

    packet["project_memory"] = memory
    memory_digest = str(memory.get("packet_digest") or "")
    address = dict(packet.get("address") or {})
    address["project_memory_digest"] = memory_digest
    packet["address"] = address
    packet["composite_digest"] = _sha(address)

    holds = set(str(x) for x in (packet.get("holds") or []) if x)
    if bool(memory.get("blocks_boot")):
        holds.add("PROJECT_MEMORY_REQUIRED_HOLD")
        packet["status"] = "BOOTSTRAP_HOLD"
    packet["holds"] = sorted(holds)

    laws = packet.setdefault("laws", [])
    for law in _LAWS:
        if law not in laws:
            laws.append(law)
    packet.setdefault("return_contract", {})["project_memory_is_routing_context_only"] = True

    session_id = packet.get("session_id")
    sessions = getattr(packet, "_sessions", None)
    # packet is a dict, so session persistence is handled by the wrapper with self.
    return packet


def _remember(self, packet: Mapping[str, Any], request: Mapping[str, Any]) -> None:
    session_id = str(packet.get("session_id") or "")
    if not session_id:
        return
    sessions = getattr(self, "_sessions", None)
    if not isinstance(sessions, dict) or session_id not in sessions:
        return
    sessions[session_id]["address"] = dict(packet.get("address") or {})
    sessions[session_id]["project_memory_request"] = _clone(dict(request))


def _augment_refresh(packet: dict, prior_address: Mapping[str, Any] | None) -> dict:
    refresh = packet.get("refresh")
    if not isinstance(refresh, dict):
        return packet
    prior = dict(prior_address or refresh.get("prior_address") or {})
    current = dict(packet.get("address") or {})
    changed = refresh.setdefault("changed", {})
    memory_changed = prior.get("project_memory_digest") != current.get("project_memory_digest")
    changed["project_memory_digest"] = memory_changed
    coords = refresh.setdefault("changed_coordinates", [])
    if memory_changed and "project_memory_digest" not in coords:
        coords.append("project_memory_digest")
    affected = refresh.setdefault("affected_dependency_cone", [])
    if memory_changed and "project_memory" not in affected:
        affected.append("project_memory")
    refresh["requires_replan"] = bool(refresh.get("requires_replan") or memory_changed)
    other_changed = any(bool(v) for k, v in changed.items() if k != "project_memory_digest")
    refresh["memory_only"] = bool(memory_changed and not other_changed)
    return packet


def extend_agent_boot_tool_schemas(tool_specs) -> None:
    for tool in tool_specs or []:
        if not isinstance(tool, dict) or tool.get("name") not in {"athena_agent_bootstrap", "athena_agent_refresh"}:
            continue
        schema = tool.get("inputSchema") or {}
        props = schema.setdefault("properties", {})
        props.setdefault("project_memory_packet", {"type": ["object", "null"]})
        props.setdefault("project_memory_selected", {"type": ["boolean", "null"]})
        props.setdefault("project_memory_required", {"type": ["boolean", "null"]})


def install_agent_bootstrap_project_memory(runtime_cls) -> None:
    if getattr(runtime_cls, "_athena_boot_project_memory_v1_registered", False):
        return
    inner_bootstrap = runtime_cls.bootstrap
    inner_refresh = runtime_cls.refresh
    inner_call_tool = runtime_cls.call_tool

    def bootstrap_with_project_memory(self, *args, **kwargs):
        explicit = {key: kwargs.pop(key) for key in list(kwargs) if key in _REQUEST_KEYS}
        override = getattr(self, "_agent_boot_project_memory_override", None)
        request = _request_from(explicit, override if isinstance(override, Mapping) else None)
        packet = inner_bootstrap(self, *args, **kwargs)
        packet = _attach(packet, request)
        _remember(self, packet, request)
        return packet

    def refresh_with_project_memory(self, *args, **kwargs):
        explicit = {key: kwargs.pop(key) for key in list(kwargs) if key in _REQUEST_KEYS}
        session_id = kwargs.get("session_id")
        remembered = getattr(self, "_sessions", {}).get(session_id or "", {}) if session_id else {}
        request = _request_from(explicit, remembered.get("project_memory_request") if isinstance(remembered, Mapping) else None)
        prior_address = kwargs.get("prior_address") or (remembered.get("address") if isinstance(remembered, Mapping) else None)
        marker = object()
        prior_override = getattr(self, "_agent_boot_project_memory_override", marker)
        self._agent_boot_project_memory_override = request
        try:
            packet = inner_refresh(self, *args, **kwargs)
        finally:
            if prior_override is marker:
                try:
                    delattr(self, "_agent_boot_project_memory_override")
                except AttributeError:
                    pass
            else:
                self._agent_boot_project_memory_override = prior_override
        if isinstance(packet, dict):
            _augment_refresh(packet, prior_address)
            _remember(self, packet, request)
        return packet

    def call_tool_with_project_memory(self, name, arguments):
        if name not in {"athena_agent_bootstrap", "athena_agent_refresh"}:
            return inner_call_tool(self, name, arguments)
        request = _request_from(arguments if isinstance(arguments, Mapping) else None)
        marker = object()
        prior_override = getattr(self, "_agent_boot_project_memory_override", marker)
        self._agent_boot_project_memory_override = request
        try:
            return inner_call_tool(self, name, arguments)
        finally:
            if prior_override is marker:
                try:
                    delattr(self, "_agent_boot_project_memory_override")
                except AttributeError:
                    pass
            else:
                self._agent_boot_project_memory_override = prior_override

    runtime_cls.bootstrap = bootstrap_with_project_memory
    runtime_cls.refresh = refresh_with_project_memory
    runtime_cls.call_tool = call_tool_with_project_memory
    runtime_cls._athena_boot_project_memory_v1_registered = True
