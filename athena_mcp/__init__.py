"""ATHENA canonical MCP package release identity and runtime registrations.

`protocol.py` remains the mature schema registry. Package initialization owns the
release identity and patches compatibility surfaces before dispatch observes them.
Frontier V1 and the rehydration-loop V1 harness are explicit extensions of the
Git prompt runtime so they reuse the existing MCP dispatcher, prompt CAS, remote
freshness membrane, and authority boundaries instead of creating another control
plane.
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

# Prompt × frontier braid registration. The dispatcher already routes the
# PROMPT_RUNTIME_TOOL_NAMES family through PromptRuntime.call_tool, so frontier
# and rehydration tools extend that family rather than duplicating dispatch,
# state, authority, or remote-delivery code.
from .prompt_runtime import PromptRuntime, PROMPT_RUNTIME_TOOLS, PROMPT_RUNTIME_TOOL_NAMES
from .frontier_runtime import FrontierRuntime, FRONTIER_TOOLS, FRONTIER_TOOL_NAMES
from .rehydration_loop import (
    REHYDRATION_TOOLS,
    REHYDRATION_TOOL_NAMES,
    RehydrationLoopRuntime,
)

# RHL-001/002/003 antibody family: persisted local loop state is not automatically
# shared-current state. Every read-side continuation surface that can influence
# routing or stopping decisions must refresh the shared branch first:
#
#   resume -> current handoff/prompt
#   verify -> current shared chain integrity
#   index  -> current shared loop inventory
#
# Clean behind checkouts may advance only by FF-only after a fresh fetch. Dirty,
# ahead, diverged, or unverified states hold rather than returning a stale local
# view as current. Local/offline experiments can explicitly select DISABLED mode
# when they do not claim a shared-current witness.
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
#
# FBR-005 antibody: the append-only event projection intentionally remains a pure
# replay of scheduler events, but provider claim creation is the real exclusion
# boundary. A fixed claim file may therefore exist briefly before CLAIM_ACQUIRED
# is appended. During that window, event-derived PENDING/READY state must not be
# advertised as claimable work. Provider occupancy suppresses selection while a
# typed residual preserves the event/claim disagreement for reconciliation.
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
            path
            for path in runtime_paths
            if "/claims/" in path and path.endswith(".json")
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
            suppressed,
            key=lambda x: (str(x.get("run_id")), str(x.get("node_id"))),
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

for _tool in FRONTIER_TOOLS + REHYDRATION_TOOLS:
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
