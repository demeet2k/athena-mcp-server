"""ATHENA canonical MCP package release identity and runtime registrations.

`protocol.py` remains the mature schema registry. Package initialization owns the
release identity and patches compatibility surfaces before dispatch observes them.
Frontier V1, rehydration-loop V1, routing-successor V1, terminal-gate V1,
handoff-delta V1, and one-call agent bootstrap reuse the existing Git prompt
runtime rather than creating another control plane.
"""

__version__ = "3.2.0"

import hashlib
import json

from . import protocol as _protocol
from .git_backend import GitStateError

SERVER_INFO = {
    "name": "athena-canonical-mcp",
    "version": __version__,
    "description": "Canonical KC144/JSPACE/SCALE developmental control with QMC/FITC probabilistic inference, bounded FCI-lite and longitudinal policy inference, and correlated robust resource planning",
}

_protocol.SERVER_INFO = dict(SERVER_INFO)

from .prompt_runtime import PromptRuntime, PROMPT_RUNTIME_TOOLS, PROMPT_RUNTIME_TOOL_NAMES
from .frontier_runtime import FrontierRuntime, FRONTIER_TOOLS, FRONTIER_TOOL_NAMES
from .rehydration_loop import (
    REHYDRATION_TOOLS,
    REHYDRATION_TOOL_NAMES,
    RehydrationLoopRuntime,
)
from .rehydration_successor import (
    SUCCESSOR_TOOLS,
    SUCCESSOR_TOOL_NAMES,
    install_successor_extension,
)
from .rehydration_regret import (
    REGRET_AB_TOOLS,
    REGRET_AB_TOOL_NAMES,
    install_regret_ab_extension,
)
from .rehydration_terminal import install_terminal_gate
from .rehydration_handoff import (
    REHYDRATION_HANDOFF_TOOLS,
    REHYDRATION_HANDOFF_TOOL_NAMES,
    RehydrationHandoffRuntime,
)
from .agent_bootstrap import (
    AGENT_BOOT_TOOLS,
    AGENT_BOOT_TOOL_NAMES,
    AgentBootstrapRuntime,
)
from .agent_bootstrap_consistency import install_bootstrap_consistency
from .agent_bootstrap_handoff import install_agent_bootstrap_handoff

# Routing successor extension: answers WHAT NEXT.
install_successor_extension(RehydrationLoopRuntime)

# Read-only V1 x V2 decision analysis. This wraps call_tool only; it does not
# alter advance(), automatic successor selection, closure, claim, or handoff.
install_regret_ab_extension(RehydrationLoopRuntime)

# Extend only the advance completion schema. Do not mutate REHYDRATION_TOOL_NAMES.
for _tool in REHYDRATION_TOOLS:
    if _tool.get("name") != "athena_rehydration_advance":
        continue
    _completion_schema = (((_tool.get("inputSchema") or {}).get("properties") or {}).get("completion") or {})
    _completion_props = _completion_schema.setdefault("properties", {})
    _completion_props.setdefault("self_steer", {"type": "boolean"})
    _completion_props.setdefault("successor_candidates", {"type": "array", "items": {"type": ["object", "string"]}})
    _completion_props.setdefault("successor_policy", {"type": "object"})
    _completion_props["self_steer"]["description"] = (
        "Optional. Omitted=AUTO: steer only when next_task is absent; an explicit V1 next_task is preserved. "
        "true forces successor compilation; false disables it."
    )

# Backward-compatibility law: an existing V1 caller that explicitly supplied a
# next_task keeps that routing decision unless it explicitly opts into
# self_steer=true. Omission means AUTO only when successor choice was left open.
if not getattr(RehydrationLoopRuntime, "_athena_successor_v1_explicit_next_compat", False):
    _rehydration_advance_with_successor = RehydrationLoopRuntime.advance

    def _rehydration_advance_preserve_explicit_next(self, *args, **kwargs):
        completion = dict(kwargs.get("completion") or {})
        explicit_next = completion.get("next_task")
        if "self_steer" not in completion and isinstance(explicit_next, str) and explicit_next.strip():
            completion["self_steer"] = False
            kwargs["completion"] = completion
        return _rehydration_advance_with_successor(self, *args, **kwargs)

    RehydrationLoopRuntime.advance = _rehydration_advance_preserve_explicit_next
    RehydrationLoopRuntime._athena_successor_v1_explicit_next_compat = True

# RHL-004: terminal=true is a closure request, not a verdict. Install this after
# successor compatibility so rejected terminal requests are demoted before the
# successor compiler/core mutation path sees them, allowing residual work to
# self-steer instead of forcing human re-entry.
install_terminal_gate(RehydrationLoopRuntime, REHYDRATION_TOOLS)

# RHL-001/002/003: every read-side continuation surface that can influence
# routing or stopping decisions refreshes shared Git first.
if not getattr(RehydrationLoopRuntime, "_athena_remote_fresh_reads_v2_registered", False):
    _rehydration_resume_local = RehydrationLoopRuntime.resume
    _rehydration_verify_local = RehydrationLoopRuntime.verify
    _rehydration_index_local = RehydrationLoopRuntime.index

    def _rehydration_sync_before_read(self, operation, shared_remote_mode="REQUIRED", remote="origin"):
        mode = self._remote_mode(shared_remote_mode)
        if mode == "DISABLED":
            return mode, {
                "status": "DISABLED",
                "remote": remote,
                "shared_frontier_verified": False,
            }
        remote_sync = self.remote_sync.sync(remote)
        if mode == "REQUIRED" and not remote_sync.get("shared_frontier_verified"):
            raise GitStateError(json.dumps({
                "status": f"REHYDRATION_{operation}_SHARED_FRONTIER_HOLD",
                "remote_sync": remote_sync,
                "law": "LOCAL_LOOP_VIEW != SHARED_CURRENT_LOOP_VIEW",
            }, sort_keys=True))
        return mode, remote_sync

    def _rehydration_resume_remote_fresh(
        self,
        loop_id,
        include_prompt=True,
        shared_remote_mode="REQUIRED",
        remote="origin",
    ):
        mode, remote_sync = _rehydration_sync_before_read(
            self, "RESUME", shared_remote_mode, remote
        )
        result = _rehydration_resume_local(self, loop_id, include_prompt)
        result["remote_sync"] = remote_sync
        result["shared_frontier_verified"] = bool(remote_sync.get("shared_frontier_verified"))
        result["freshness_law"] = "RESUME_SYNC_SHARED_GIT_BEFORE_READING_LOOP_STATE"
        if mode == "BEST_EFFORT" and not result["shared_frontier_verified"] and result.get("status") == "RESUMED":
            result["status"] = "RESUMED_UNVERIFIED"
        return result

    def _rehydration_verify_remote_fresh(
        self,
        loop_id,
        shared_remote_mode="REQUIRED",
        remote="origin",
    ):
        mode, remote_sync = _rehydration_sync_before_read(
            self, "VERIFY", shared_remote_mode, remote
        )
        result = _rehydration_verify_local(self, loop_id)
        result["remote_sync"] = remote_sync
        result["shared_frontier_verified"] = bool(remote_sync.get("shared_frontier_verified"))
        result["freshness_law"] = "VERIFY_SYNC_SHARED_GIT_BEFORE_REPLAYING_LOOP_CHAIN"
        if mode == "BEST_EFFORT" and not result["shared_frontier_verified"] and result.get("status") == "PASS":
            result["status"] = "PASS_UNVERIFIED"
        return result

    def _rehydration_index_remote_fresh(
        self,
        shared_remote_mode="REQUIRED",
        remote="origin",
    ):
        mode, remote_sync = _rehydration_sync_before_read(
            self, "INDEX", shared_remote_mode, remote
        )
        result = _rehydration_index_local(self)
        result["remote_sync"] = remote_sync
        result["shared_frontier_verified"] = bool(remote_sync.get("shared_frontier_verified"))
        result["freshness_law"] = "INDEX_SYNC_SHARED_GIT_BEFORE_LISTING_LOOP_TIPS"
        if mode == "BEST_EFFORT" and not result["shared_frontier_verified"] and result.get("status") == "OK":
            result["status"] = "OK_UNVERIFIED"
        return result

    RehydrationLoopRuntime.resume = _rehydration_resume_remote_fresh
    RehydrationLoopRuntime.verify = _rehydration_verify_remote_fresh
    RehydrationLoopRuntime.index = _rehydration_index_remote_fresh
    RehydrationLoopRuntime._athena_remote_fresh_resume_v1_registered = True
    RehydrationLoopRuntime._athena_remote_fresh_reads_v2_registered = True

    _rehydration_descriptions = {
        "athena_rehydration_resume": (
            "Fresh-sync the shared Git branch, then resume the persisted rehydration loop at its exact current "
            "prompt/state/chain coordinates. Clean behind checkouts fast-forward; dirty, ahead, diverged, or "
            "unverified shared state holds rather than returning a stale local handoff."
        ),
        "athena_rehydration_verify": (
            "Fresh-sync the shared Git branch, then replay and verify the current persisted loop chain, prompt/receipt "
            "digests, sequential steps, and Git ancestry. PASS is shared-current causal-integrity evidence, not world truth."
        ),
        "athena_rehydration_index": (
            "Fresh-sync the shared Git branch, then list current Git-persisted rehydration loops and their status, step, "
            "state/chain digests, and checkpoint heads. Unverified shared state holds instead of returning stale inventory."
        ),
    }
    for _tool in REHYDRATION_TOOLS:
        if _tool.get("name") in _rehydration_descriptions:
            _tool["description"] = _rehydration_descriptions[_tool["name"]]

# Prompt-stack content identity excludes repository clock/provenance.
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

# Frontier identity is reduced-content identity. Provider claim occupancy is an
# exclusion witness even during the brief claim/event reconciliation window.
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
        runtime_paths = self._paths(packet["source_head"], "runtime/queue", "runtime/runs")
        packet["generated_from"] = runtime_paths

        provider_claim_paths = {
            path for path in runtime_paths if "/claims/" in path and path.endswith(".json")
        }
        kept_ready = []
        suppressed = []
        for candidate in packet.get("ready_work") or []:
            claim_path = str(candidate.get("claim_path") or "")
            if claim_path and claim_path in provider_claim_paths:
                witness = {
                    "run_id": candidate.get("run_id"),
                    "node_id": candidate.get("node_id"),
                    "claim_path": claim_path,
                    "reason": "FIXED_CLAIM_PATH_PRESENT_BEFORE_EVENT_RECONCILIATION",
                }
                suppressed.append(witness)
                pressure = {
                    "kind": "CLAIM_EVENT_LAG",
                    "code": "FIXED_CLAIM_PATH_PRESENT_BEFORE_CLAIM_EVENT",
                    "run_id": candidate.get("run_id"),
                    "node_id": candidate.get("node_id"),
                    "claim_path": claim_path,
                    "priority": candidate.get("priority"),
                    "observability": "OBSERVED_PROVIDER_STATE",
                }
                packet.setdefault("pressures", []).append(pressure)
                packet.setdefault("residuals", []).append(dict(pressure))
                continue
            kept_ready.append(candidate)
        packet["ready_work"] = kept_ready
        packet["claim_readiness_suppressed"] = sorted(
            suppressed, key=lambda x: (str(x.get("run_id")), str(x.get("node_id")))
        )
        packet["pressures"] = sorted(
            packet.get("pressures") or [],
            key=lambda x: (str(x.get("kind")), str(x.get("run_id")), str(x.get("node_id"))),
        )
        packet["residuals"] = sorted(
            packet.get("residuals") or [],
            key=lambda x: (str(x.get("kind")), str(x.get("run_id")), str(x.get("node_id"))),
        )
        law = "FIXED_CLAIM_PATH_PRESENT -> NOT_READY_UNTIL_EVENT_RECONCILED"
        if law not in packet["laws"]:
            packet["laws"].append(law)

        keys = (
            "generated_from", "objectives", "runs", "pressures", "ready_work",
            "claims", "claim_readiness_suppressed", "residuals", "source_coverage",
            "authority", "sched_contract", "laws"
        )
        digest_basis = _strip_frontier_clock({key: packet.get(key) for key in keys})
        payload = json.dumps(digest_basis, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        packet["frontier_digest"] = hashlib.sha256(payload).hexdigest()
        packet["frontier_digest_basis"] = "reduced runtime content plus pinned SCHED interpretation contract; recursively excludes source_head clock while source/ref/checkout/witness/prompt digest remain separate address coordinates; fixed provider claim occupancy suppresses event-lag READY candidates"
        return packet

    FrontierRuntime._source = _frontier_source_requires_requested_remote_ref
    FrontierRuntime.hydrate = _frontier_hydrate_content_digest
    FrontierRuntime._athena_content_digest_v1_registered = True

# Bootstrap must consume canonical rehydration/terminal/handoff behavior rather
# than recreate it. Install BOOT-001/002 consistency first, then continuation.
install_bootstrap_consistency(AgentBootstrapRuntime)
install_agent_bootstrap_handoff(AgentBootstrapRuntime)

# Additive MCP surface union.
for _tool in FRONTIER_TOOLS + REHYDRATION_TOOLS + SUCCESSOR_TOOLS + REGRET_AB_TOOLS + REHYDRATION_HANDOFF_TOOLS + AGENT_BOOT_TOOLS:
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

if not getattr(PromptRuntime, "_athena_rehydration_loop_v1_registered", False):
    _prompt_call_without_rehydration = PromptRuntime.call_tool

    def _prompt_call_with_rehydration(self, name, arguments):
        if name in REHYDRATION_TOOL_NAMES:
            runtime = getattr(self, "_rehydration_loop_runtime_v1", None)
            if runtime is None:
                runtime = RehydrationLoopRuntime(self.git, self)
                self._rehydration_loop_runtime_v1 = runtime
            return runtime.call_tool(name, arguments)
        return _prompt_call_without_rehydration(self, name, arguments)

    PromptRuntime.call_tool = _prompt_call_with_rehydration
    PromptRuntime._athena_rehydration_loop_v1_registered = True

if not getattr(PromptRuntime, "_athena_rehydration_successor_v1_registered", False):
    _prompt_call_without_successor = PromptRuntime.call_tool

    def _prompt_call_with_successor(self, name, arguments):
        if name in SUCCESSOR_TOOL_NAMES:
            runtime = getattr(self, "_rehydration_loop_runtime_v1", None)
            if runtime is None:
                runtime = RehydrationLoopRuntime(self.git, self)
                self._rehydration_loop_runtime_v1 = runtime
            return runtime.call_tool(name, arguments)
        return _prompt_call_without_successor(self, name, arguments)

    PromptRuntime.call_tool = _prompt_call_with_successor
    PromptRuntime._athena_rehydration_successor_v1_registered = True

if not getattr(PromptRuntime, "_athena_rehydration_regret_ab_v2_registered", False):
    _prompt_call_without_regret_ab = PromptRuntime.call_tool

    def _prompt_call_with_regret_ab(self, name, arguments):
        if name in REGRET_AB_TOOL_NAMES:
            runtime = getattr(self, "_rehydration_loop_runtime_v1", None)
            if runtime is None:
                runtime = RehydrationLoopRuntime(self.git, self)
                self._rehydration_loop_runtime_v1 = runtime
            return runtime.call_tool(name, arguments)
        return _prompt_call_without_regret_ab(self, name, arguments)

    PromptRuntime.call_tool = _prompt_call_with_regret_ab
    PromptRuntime._athena_rehydration_regret_ab_v2_registered = True

if not getattr(PromptRuntime, "_athena_rehydration_handoff_v1_registered", False):
    _prompt_call_without_handoff = PromptRuntime.call_tool

    def _prompt_call_with_handoff(self, name, arguments):
        if name in REHYDRATION_HANDOFF_TOOL_NAMES:
            runtime = getattr(self, "_rehydration_handoff_runtime_v1", None)
            if runtime is None:
                loop_runtime = getattr(self, "_rehydration_loop_runtime_v1", None)
                runtime = RehydrationHandoffRuntime(self.git, self, loop_runtime)
                self._rehydration_handoff_runtime_v1 = runtime
            return runtime.call_tool(name, arguments)
        return _prompt_call_without_handoff(self, name, arguments)

    PromptRuntime.call_tool = _prompt_call_with_handoff
    PromptRuntime._athena_rehydration_handoff_v1_registered = True

if not getattr(PromptRuntime, "_athena_agent_bootstrap_v1_registered", False):
    _prompt_call_without_bootstrap = PromptRuntime.call_tool

    def _prompt_call_with_bootstrap(self, name, arguments):
        if name in AGENT_BOOT_TOOL_NAMES:
            runtime = getattr(self, "_agent_bootstrap_runtime_v1", None)
            if runtime is None:
                frontier_runtime = getattr(self, "_frontier_runtime_v1", None)
                runtime = AgentBootstrapRuntime(self.git, self, frontier_runtime)
                self._agent_bootstrap_runtime_v1 = runtime
            return runtime.call_tool(name, arguments)
        return _prompt_call_without_bootstrap(self, name, arguments)

    PromptRuntime.call_tool = _prompt_call_with_bootstrap
    PromptRuntime._athena_agent_bootstrap_v1_registered = True
