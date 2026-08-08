"""ATHENA canonical MCP package release identity and runtime registrations.

`protocol.py` remains the mature schema registry. Package initialization owns the
release identity and patches compatibility surfaces before dispatch observes them.
Frontier V1 is registered as an explicit extension of the Git prompt runtime so it
reuses the existing MCP dispatcher rather than creating a second control plane.
"""

__version__ = "3.2.0"

import hashlib
import json

from . import protocol as _protocol

SERVER_INFO = {
    "name": "athena-canonical-mcp",
    "version": __version__,
    "description": "Canonical KC144/JSPACE/SCALE developmental control with QMC/FITC probabilistic inference, bounded FCI-lite and longitudinal policy inference, and correlated robust resource planning",
}

_protocol.SERVER_INFO = dict(SERVER_INFO)

# Prompt × frontier braid registration.  The dispatcher already routes the
# PROMPT_RUNTIME_TOOL_NAMES family through PromptRuntime.call_tool, so frontier
# tools extend that family rather than duplicating dispatch/state/authority code.
from .prompt_runtime import PromptRuntime, PROMPT_RUNTIME_TOOLS, PROMPT_RUNTIME_TOOL_NAMES
from .frontier_runtime import FrontierRuntime, FRONTIER_TOOLS, FRONTIER_TOOL_NAMES

# The prompt stack is a content-policy coordinate, not a synonym for repository
# time. Keep git_head in ancestry for provenance while excluding it from the
# prompt-stack digest. Git/head freshness remains a separate coordinate.
if not getattr(PromptRuntime, "_athena_content_digest_v1_registered", False):
    _prompt_compile_with_head_digest = PromptRuntime.compile

    def _prompt_compile_content_digest(self, *args, **kwargs):
        result = _prompt_compile_with_head_digest(self, *args, **kwargs)
        ancestry = dict(result["ancestry"])
        digest_basis = {k: v for k, v in ancestry.items() if k != "git_head"}
        payload = json.dumps(digest_basis, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        result["prompt_stack_digest"] = hashlib.sha256(payload).hexdigest()
        result["prompt_stack_digest_basis"] = "content ancestry excluding git_head; git_head remains independent provenance/freshness coordinate"
        return result

    PromptRuntime.compile = _prompt_compile_content_digest
    PromptRuntime._athena_content_digest_v1_registered = True

# Frontier identity is a reduced-content coordinate, not a checkout, branch,
# fetch-status or repository-clock coordinate. Source head and remote witness are
# independent siblings. Include every runtime path actually available so replay
# provenance is complete while environment metadata cannot perturb the digest.
if not getattr(FrontierRuntime, "_athena_content_digest_v1_registered", False):
    _frontier_source_with_local_fallback = FrontierRuntime._source
    _frontier_hydrate_with_environment_digest = FrontierRuntime.hydrate

    def _frontier_source_requires_requested_remote_ref(self, source_ref, remote="origin", fetch=True):
        result = _frontier_source_with_local_fallback(self, source_ref, remote, fetch)
        if fetch and self._remote_exists(remote) and result.get("remote_checked"):
            required = f"refs/remotes/{remote}/{source_ref}"
            if result.get("resolved_ref") != required:
                result["remote_checked"] = False
                result["fetch_error"] = f"requested remote source ref unavailable after fetch: {required}"
        return result

    def _strip_frontier_clock(value):
        if isinstance(value, dict):
            return {k: _strip_frontier_clock(v) for k, v in value.items() if k != "source_head"}
        if isinstance(value, list):
            return [_strip_frontier_clock(v) for v in value]
        return value

    def _frontier_hydrate_content_digest(self, *args, **kwargs):
        packet = _frontier_hydrate_with_environment_digest(self, *args, **kwargs)
        packet["generated_from"] = self._paths(packet["source_head"], "runtime/queue", "runtime/runs")
        keys = (
            "generated_from", "objectives", "runs", "pressures", "ready_work",
            "claims", "residuals", "source_coverage", "authority", "sched_contract", "laws"
        )
        digest_basis = _strip_frontier_clock({key: packet.get(key) for key in keys})
        payload = json.dumps(digest_basis, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        packet["frontier_digest"] = hashlib.sha256(payload).hexdigest()
        packet["frontier_digest_basis"] = "reduced runtime content plus pinned SCHED interpretation contract; recursively excludes source_head clock while source/ref/checkout/witness/prompt digest remain separate address coordinates"
        return packet

    FrontierRuntime._source = _frontier_source_requires_requested_remote_ref
    FrontierRuntime.hydrate = _frontier_hydrate_content_digest
    FrontierRuntime._athena_content_digest_v1_registered = True

for _tool in FRONTIER_TOOLS:
    if _tool["name"] not in PROMPT_RUNTIME_TOOL_NAMES:
        PROMPT_RUNTIME_TOOLS.append(_tool)
        PROMPT_RUNTIME_TOOL_NAMES.add(_tool["name"])
    if not any(existing["name"] == _tool["name"] for existing in _protocol.TOOLS):
        _protocol.TOOLS.append(_tool)

if not getattr(PromptRuntime, "_athena_frontier_v1_registered", False):
    _prompt_call_without_frontier = PromptRuntime.call_tool

    def _prompt_call_with_frontier(self, name, arguments):
        if name in FRONTIER_TOOL_NAMES:
            runtime = getattr(self, "_frontier_runtime_v1", None)
            if runtime is None:
                runtime = FrontierRuntime(self.git, self)
                self._frontier_runtime_v1 = runtime
            return runtime.call_tool(name, arguments)
        return _prompt_call_without_frontier(self, name, arguments)

    PromptRuntime.call_tool = _prompt_call_with_frontier
    PromptRuntime._athena_frontier_v1_registered = True
