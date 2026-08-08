from __future__ import annotations

import hashlib
import json
from typing import Any

from . import protocol as _protocol
from .agent_bootstrap import AGENT_BOOT_TOOLS, AGENT_BOOT_TOOL_NAMES, AgentBootstrapRuntime
from .prompt_runtime import PROMPT_RUNTIME_TOOLS, PROMPT_RUNTIME_TOOL_NAMES

ARTIFACT = "OPERATIONAL_BASIS_V1"
TOOL_NAME = "athena_operational_basis"

OPERATIONAL_BASIS_TOOL = {
    "name": TOOL_NAME,
    "description": (
        "Return OPERATIONAL_BASIS_V1 derived from the actually registered current prompt/control-plane MCP surface. "
        "Descriptors classify semantic capability, effect, authority, freshness dependencies, preconditions, replay, "
        "and rollback/compensation without widening execution authority."
    ),
    "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
}

LAWS = [
    "OPERATIONAL_BASIS != HIGHER_AUTHORITY",
    "DESCRIPTOR != PERMISSION",
    "FEATURE_BRANCH != CURRENT_RUNTIME_EXPOSURE",
    "ISSUE_CLAIM != EXPOSED_CAPABILITY",
    "UNCLASSIFIED_WRITE => HOLD",
    "CAPABILITY_NEGOTIATION != SELF_AUTHORIZATION",
]

_CONTROL_PREFIXES = (
    "athena_agent_",
    "athena_prompt_",
    "athena_frontier_",
    "athena_rehydration_",
)


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


def _is_control_operation(name: str) -> bool:
    return bool(
        name == TOOL_NAME
        or name.startswith(_CONTROL_PREFIXES)
        or "campaign" in name
        or "epoch" in name
        or "rollover" in name
    )


def _capability_class(name: str) -> str:
    if name == TOOL_NAME or name.startswith("athena_agent_"):
        return "BOOTSTRAP_REFRESH"
    if name.startswith("athena_prompt_"):
        return "PROMPT"
    if name.startswith("athena_frontier_"):
        return "CLAIM_EXECUTION" if "claim" in name else "FRONTIER_READ_SELECT"
    if name.startswith("athena_rehydration_"):
        if "handoff" in name:
            return "HANDOFF"
        if "successor" in name or "route" in name:
            return "SUCCESSOR"
        if "verify" in name or "index" in name:
            return "VERIFY_REPLAY_INDEX"
        return "REHYDRATION_LOOP"
    if "campaign" in name:
        return "CAMPAIGN"
    if "epoch" in name or "rollover" in name:
        return "EPOCH_ROLLOVER"
    return "UNCLASSIFIED"


def _effect(name: str, capability_class: str) -> str:
    if name in {TOOL_NAME, "athena_agent_bootstrap", "athena_agent_refresh"}:
        return "READ_ONLY"
    if capability_class == "PROMPT":
        suffix = name.removeprefix("athena_prompt_")
        if suffix in {"hydrate", "compile", "freshness", "remote_status"}:
            return "READ_ONLY"
        if suffix == "sync":
            return "BOUNDED_GIT_SYNC"
        if suffix == "publish":
            return "BOUNDED_PROVIDER_WRITE"
        if suffix in {"propose", "experiment"}:
            return "REPOSITORY_CANDIDATE_WRITE"
        if suffix == "activate":
            return "SCOPED_RUNTIME_WRITE"
        if suffix == "promote":
            return "CANONICAL_PROMOTION_GATED_WRITE"
        return "UNKNOWN"
    if capability_class == "FRONTIER_READ_SELECT":
        return "READ_ONLY"
    if capability_class == "CLAIM_EXECUTION":
        if name.endswith("_prepare") or name.endswith("_status"):
            return "READ_ONLY"
        return "BOUNDED_PROVIDER_WRITE"
    if capability_class == "REHYDRATION_LOOP":
        if name.endswith("_start") or name.endswith("_advance"):
            return "BOUNDED_RUNTIME_WRITE"
        return "READ_ONLY"
    if capability_class in {"SUCCESSOR", "VERIFY_REPLAY_INDEX"}:
        return "READ_ONLY"
    if capability_class == "HANDOFF":
        if name.endswith("_prepare") or name.endswith("_inspect") or name.endswith("_verify"):
            return "READ_ONLY"
        return "BOUNDED_RUNTIME_WRITE"
    if capability_class in {"CAMPAIGN", "EPOCH_ROLLOVER"}:
        return "BOUNDED_RUNTIME_WRITE"
    return "UNKNOWN"


def _authority(effect: str, capability_class: str) -> str:
    return {
        "READ_ONLY": "OBSERVATION_ONLY",
        "BOUNDED_GIT_SYNC": "BOUNDED_LOCAL_FAST_FORWARD",
        "REPOSITORY_CANDIDATE_WRITE": "CANDIDATE_REPOSITORY_WRITE",
        "SCOPED_RUNTIME_WRITE": "SCOPED_PROMPT_RUNTIME_WRITE",
        "CANONICAL_PROMOTION_GATED_WRITE": "CANONICAL_PROMOTION_GATED",
        "BOUNDED_PROVIDER_WRITE": "BOUNDED_PROVIDER_WRITE",
        "BOUNDED_RUNTIME_WRITE": "BOUNDED_RUNTIME_WRITE",
    }.get(effect, "UNCLASSIFIED_HOLD" if capability_class == "UNCLASSIFIED" else "UNKNOWN_HOLD")


def _component(capability_class: str) -> str:
    return {
        "BOOTSTRAP_REFRESH": "agent_bootstrap",
        "PROMPT": "prompt_runtime",
        "FRONTIER_READ_SELECT": "frontier_runtime",
        "CLAIM_EXECUTION": "frontier_provider_membrane",
        "REHYDRATION_LOOP": "rehydration_loop",
        "SUCCESSOR": "rehydration_successor",
        "HANDOFF": "rehydration_handoff",
        "VERIFY_REPLAY_INDEX": "rehydration_verification",
        "CAMPAIGN": "campaign_runtime",
        "EPOCH_ROLLOVER": "epoch_runtime",
    }.get(capability_class, "unclassified")


def _freshness_dependencies(capability_class: str, name: str) -> list[str]:
    if name == TOOL_NAME:
        return ["registered_runtime_surface"]
    if capability_class == "BOOTSTRAP_REFRESH":
        return [
            "git_head", "prompt_stack_digest", "frontier_source_head", "frontier_digest",
            "sched_contract_digest", "issue_pressure_digest", "operational_basis_digest",
        ]
    if capability_class == "PROMPT":
        deps = ["git_head", "prompt_stack_digest"]
        if name in {"athena_prompt_remote_status", "athena_prompt_sync", "athena_prompt_publish"}:
            deps.append("shared_remote_witness")
        return deps
    if capability_class == "FRONTIER_READ_SELECT":
        return ["frontier_source_head", "frontier_digest", "sched_contract_digest"]
    if capability_class == "CLAIM_EXECUTION":
        return [
            "git_head", "prompt_stack_digest", "frontier_source_head", "frontier_digest",
            "sched_contract_digest", "provider_witness",
        ]
    if capability_class in {"REHYDRATION_LOOP", "SUCCESSOR", "HANDOFF", "VERIFY_REPLAY_INDEX"}:
        return ["git_head", "prompt_stack_digest"]
    if capability_class in {"CAMPAIGN", "EPOCH_ROLLOVER"}:
        return ["git_head", "prompt_stack_digest", "frontier_digest", "sched_contract_digest"]
    return ["registered_runtime_surface"]


def _preconditions(capability_class: str, effect: str) -> list[str]:
    result = ["operation is currently registered"]
    if capability_class == "UNCLASSIFIED" or effect == "UNKNOWN":
        result.append("semantic classification required before automatic selection")
    if effect != "READ_ONLY":
        result.append("caller authority and operation-specific freshness/preconditions must pass")
    if capability_class == "CLAIM_EXECUTION" and effect != "READ_ONLY":
        result.append("provider-bounded create-if-absent claim semantics must be available")
    if effect == "CANONICAL_PROMOTION_GATED_WRITE":
        result.append("promotion evidence, ancestry, tests, and rollback gate must pass")
    return result


def _rollback(effect: str) -> str:
    return {
        "READ_ONLY": "NOT_REQUIRED_READ_ONLY",
        "BOUNDED_GIT_SYNC": "FAST_FORWARD_ONLY; REHYDRATE_FROM_SHARED_FRONTIER",
        "REPOSITORY_CANDIDATE_WRITE": "REVERT_OR_RETIRE_CANDIDATE_DESCENDANT",
        "SCOPED_RUNTIME_WRITE": "DEACTIVATE_OR_ROLL_BACK_SCOPED_OVERLAY",
        "CANONICAL_PROMOTION_GATED_WRITE": "REVERT_AS_NEW_CAUSAL_EVENT",
        "BOUNDED_PROVIDER_WRITE": "PROVIDER_COMPENSATION_OR_RECONCILIATION; NO_FALSE_ATOMIC_ROLLBACK",
        "BOUNDED_RUNTIME_WRITE": "REPLAYABLE_COMPENSATION_OR_DESCENDANT_REVERT",
    }.get(effect, "HOLD_UNTIL_ROLLBACK_CONTRACT_CLASSIFIED")


def _descriptor(tool: dict) -> dict:
    name = str(tool.get("name") or "")
    capability_class = _capability_class(name)
    effect = _effect(name, capability_class)
    schema_basis = {
        "name": name,
        "description": tool.get("description"),
        "inputSchema": tool.get("inputSchema"),
    }
    auto_select = capability_class != "UNCLASSIFIED" and effect == "READ_ONLY"
    return {
        "operation": name,
        "capability_class": capability_class,
        "component": _component(capability_class),
        "effect": effect,
        "authority_class": _authority(effect, capability_class),
        "freshness_dependencies": _freshness_dependencies(capability_class, name),
        "preconditions": _preconditions(capability_class, effect),
        "replayability": effect == "READ_ONLY",
        "rollback_or_compensation": _rollback(effect),
        "current_exposure": True,
        "auto_select": auto_select,
        "source_witness": {
            "surface": "PROTOCOL_TOOLS_CONTROL_FILTER",
            "tool_schema_digest": _sha(schema_basis),
        },
    }


def _registered_control_tools() -> dict[str, dict]:
    by_name: dict[str, dict] = {}
    for tool in _protocol.TOOLS:
        if not isinstance(tool, dict):
            continue
        name = str(tool.get("name") or "")
        if name and _is_control_operation(name):
            by_name[name] = tool
    return by_name


def build_operational_basis() -> dict:
    """Derive semantic capability descriptors from the live MCP registration surface."""

    by_name = _registered_control_tools()
    descriptors = [_descriptor(by_name[name]) for name in sorted(by_name)]
    unclassified = [
        {
            "operation": row["operation"],
            "effect": row["effect"],
            "authority_class": row["authority_class"],
            "auto_select": False,
        }
        for row in descriptors
        if row["capability_class"] == "UNCLASSIFIED" or row["effect"] == "UNKNOWN"
    ]
    runtime_identity = {
        "name": _protocol.SERVER_INFO.get("name"),
        "version": _protocol.SERVER_INFO.get("version"),
    }
    source_witness = {
        "surface": "PROTOCOL_TOOLS_CONTROL_FILTER",
        "registered_count": len(descriptors),
        "registered_names_digest": _sha([row["operation"] for row in descriptors]),
        "registered_schema_digest": _sha([
            {
                "operation": row["operation"],
                "tool_schema_digest": row["source_witness"]["tool_schema_digest"],
            }
            for row in descriptors
        ]),
    }
    digest_basis = {
        "artifact": ARTIFACT,
        "runtime_identity": runtime_identity,
        "descriptors": descriptors,
        "unclassified": unclassified,
        "laws": LAWS,
        "source_witness": source_witness,
    }
    return {
        **digest_basis,
        "status": "OPERATIONAL_BASIS_HOLD" if unclassified else "OPERATIONAL_BASIS_READY",
        "basis_digest": _sha(digest_basis),
    }


def install() -> None:
    """Install the read-side basis operation and bind its digest into AGENT_BOOT_V1."""

    if TOOL_NAME not in AGENT_BOOT_TOOL_NAMES:
        AGENT_BOOT_TOOLS.append(dict(OPERATIONAL_BASIS_TOOL))
        AGENT_BOOT_TOOL_NAMES.add(TOOL_NAME)
    if TOOL_NAME not in PROMPT_RUNTIME_TOOL_NAMES:
        PROMPT_RUNTIME_TOOLS.append(dict(OPERATIONAL_BASIS_TOOL))
        PROMPT_RUNTIME_TOOL_NAMES.add(TOOL_NAME)
    if not any(tool.get("name") == TOOL_NAME for tool in _protocol.TOOLS):
        _protocol.TOOLS.append(dict(OPERATIONAL_BASIS_TOOL))

    flag = "_athena_operational_basis_v1_registered"
    if getattr(AgentBootstrapRuntime, flag, False):
        return

    original_address = AgentBootstrapRuntime._address
    original_changed = AgentBootstrapRuntime._changed
    original_refresh = AgentBootstrapRuntime.refresh
    original_call_tool = AgentBootstrapRuntime.call_tool

    def address_with_basis(packet: dict) -> dict:
        basis = build_operational_basis()
        execution = packet.setdefault("execution_surface", {})
        execution["operational_basis_digest"] = basis["basis_digest"]
        execution["capability_descriptors"] = basis["descriptors"]
        execution["unclassified"] = basis["unclassified"]
        execution["operational_basis_status"] = basis["status"]
        execution["operational_basis_witness"] = basis["source_witness"]
        packet.setdefault("witnesses", {})["operational_basis"] = basis["source_witness"]
        packet.setdefault("laws", [])
        law = "OPERATIONAL_BASIS != EXECUTION_AUTHORITY"
        if law not in packet["laws"]:
            packet["laws"].append(law)
        address = original_address(packet)
        address["operational_basis_digest"] = basis["basis_digest"]
        return address

    def changed_with_basis(prior: dict, current: dict) -> dict:
        changed = original_changed(prior, current)
        changed["operational_basis_digest"] = (
            prior.get("operational_basis_digest") != current.get("operational_basis_digest")
        )
        return changed

    def refresh_with_basis(self, *args, **kwargs):
        packet = original_refresh(self, *args, **kwargs)
        refresh = packet.get("refresh") or {}
        changed = refresh.get("changed") or {}
        if changed.get("operational_basis_digest"):
            cone = refresh.setdefault("affected_dependency_cone", [])
            if "runtime_capability_basis" not in cone:
                cone.append("runtime_capability_basis")
            refresh["requires_replan"] = True
        return packet

    def call_tool_with_basis(self, name: str, arguments: dict):
        if name == TOOL_NAME:
            return build_operational_basis()
        return original_call_tool(self, name, arguments)

    AgentBootstrapRuntime._address = staticmethod(address_with_basis)
    AgentBootstrapRuntime._changed = staticmethod(changed_with_basis)
    AgentBootstrapRuntime.refresh = refresh_with_basis
    AgentBootstrapRuntime.operational_basis = lambda self: build_operational_basis()
    AgentBootstrapRuntime.call_tool = call_tool_with_basis
    setattr(AgentBootstrapRuntime, flag, True)


def main(argv=None):
    # Install before server/dispatch imports finish constructing the dynamic MCP surface.
    install()
    from .server import main as server_main

    return server_main(argv)
