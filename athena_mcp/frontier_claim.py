from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

CLAIM_CONTRACT_HEAD = "10987272743eb0024a7620655775b4190c54153f"
CLAIM_CONTRACT_BLOBS = {
    "orchestration/v3/reducer.py": "122802a3cec6f50b692d819b18024b50be39bab8",
    "orchestration/v3/ready.py": "975d61ab5ddf42e6e06c7304fc0fc330ca4b24d5",
    "orchestration/v3/claim.py": "4757f4eaf8180cf356dc0e940b9019177f1c0a8a",
    "orchestration/v3/journal.py": "d9a5674caef76b50a3ca6cb0e513389484ac640b",
    "orchestration/v3/claim_saga.py": "47a99a5b9461f613c7184650385b7d0804bc4553",
}
_SAFE_ID = re.compile(r"^[A-Za-z0-9._-]+$")


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _safe_id(value: str, field: str) -> str:
    text = str(value or "")
    if not text or not _SAFE_ID.fullmatch(text):
        raise ValueError(f"{field}: unsafe or empty identifier")
    return text


def _strip_clock(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _strip_clock(v) for k, v in value.items() if k != "source_head"}
    if isinstance(value, list):
        return [_strip_clock(v) for v in value]
    return value


def _claim_path(run_id: str, node_id: str) -> str:
    return f"runtime/runs/{_safe_id(run_id, 'run_id')}/claims/{_safe_id(node_id, 'node_id')}.json"


def _event_path(run_id: str, sequence: int) -> str:
    if not isinstance(sequence, int) or sequence <= 0:
        raise ValueError("event sequence must be positive")
    return f"runtime/runs/{_safe_id(run_id, 'run_id')}/events/{sequence:08d}.json"


def _provider_packet(path: str, content: dict, *, kind: str) -> dict:
    return {
        "provider_operation": "CREATE_FILE_IF_ABSENT",
        "kind": kind,
        "path": path,
        "content": content,
        "content_text": json.dumps(content, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
    }


class FrontierClaimRuntime:
    """No-write claim/provider membrane over one FrontierRuntime instance.

    This runtime deliberately prepares provider packets but does not execute them.
    It distinguishes routing readiness (PENDING + dependencies satisfied) from
    reducer/event readiness (state exactly READY) and pins the full five-file
    SCHED journal/claim interpretation contract before claim preparation.
    """

    def __init__(self, frontier_runtime, *, contract_blobs=None, environ=None):
        self.frontier = frontier_runtime
        self.contract_blobs = dict(CLAIM_CONTRACT_BLOBS if contract_blobs is None else contract_blobs)
        self.environ = os.environ if environ is None else environ

    def _contract(self, source_head: str) -> dict:
        rows = {}
        actual_map = {}
        ok = True
        for path, expected in self.contract_blobs.items():
            actual = self.frontier._blob(source_head, path)
            match = actual == expected
            rows[path] = {"expected_blob": expected, "actual_blob": actual, "match": match}
            actual_map[path] = actual
            ok = ok and match
        return {
            "status": "PASS" if ok else "CLAIM_CONTRACT_UNAVAILABLE_HOLD",
            "candidate_contract_head": CLAIM_CONTRACT_HEAD,
            "contracts": rows,
            "claim_contract_digest": _sha(actual_map),
            "expected_claim_contract_digest": _sha(self.contract_blobs),
            "law": "CLAIM_PROVIDER_EXECUTION_REQUIRES_EXACT_REDUCER_READY_CLAIM_JOURNAL_SAGA_CONTRACT",
        }

    def _remote_repo(self, remote: str) -> str | None:
        root = self.frontier._root()
        p = subprocess.run(
            ["git", "-C", str(root), "remote", "get-url", remote],
            text=True,
            capture_output=True,
        )
        if p.returncode:
            return None
        raw = p.stdout.strip()
        slug = None
        if raw.startswith("git@github.com:"):
            slug = raw.split(":", 1)[1]
        elif raw.startswith("ssh://git@github.com/"):
            slug = raw.split("ssh://git@github.com/", 1)[1]
        elif "github.com/" in raw:
            slug = raw.split("github.com/", 1)[1]
        if slug:
            slug = slug.removesuffix(".git").strip("/")
        if not slug or slug.count("/") != 1:
            return None
        owner, repo = slug.split("/", 1)
        if not _SAFE_ID.fullmatch(owner) or not _SAFE_ID.fullmatch(repo):
            return None
        return slug

    def _token_present(self) -> bool:
        return bool(
            self.environ.get("ATHENA_GITHUB_TOKEN")
            or self.environ.get("GH_TOKEN")
            or self.environ.get("GITHUB_TOKEN")
        )

    @staticmethod
    def _run_projection(packet: dict, run_id: str) -> dict | None:
        for entry in packet.get("runs") or []:
            if str(entry.get("run_id")) == run_id:
                return entry
        return None

    @staticmethod
    def _claim_exists(packet: dict, run_id: str, node_id: str) -> bool:
        for claim in packet.get("claims") or []:
            if str(claim.get("run_id")) == run_id and str(claim.get("node_id")) == node_id:
                return True
        return False

    def _manifest(self, packet: dict, run_id: str) -> dict:
        path = f"runtime/runs/{_safe_id(run_id, 'run_id')}/manifest.json"
        value = self.frontier._json(packet["source_head"], path)
        if not isinstance(value, dict):
            raise ValueError(f"run manifest unavailable: {path}")
        return value

    def _node(self, manifest: dict, node_id: str) -> dict:
        safe = _safe_id(node_id, "node_id")
        for node in manifest.get("nodes") or []:
            if str(node.get("node_id")) == safe:
                return dict(node)
        raise ValueError(f"unknown node {safe}")

    def _events(self, packet: dict, run_id: str) -> list[dict]:
        prefix = f"runtime/runs/{_safe_id(run_id, 'run_id')}/events"
        paths = [p for p in self.frontier._paths(packet["source_head"], prefix) if p.endswith(".json")]
        rows = []
        for path in sorted(paths):
            value = self.frontier._json(packet["source_head"], path)
            if not isinstance(value, dict):
                raise ValueError(f"invalid event JSON: {path}")
            rows.append(value)
        rows.sort(key=lambda x: int(x.get("sequence") or 0))
        for expected, event in enumerate(rows, start=1):
            if int(event.get("sequence") or 0) != expected:
                raise ValueError(f"event stream is not contiguous at sequence {expected}")
        return rows

    def augment_packet(self, packet: dict) -> dict:
        packet = dict(packet)
        run_map = {str(x.get("run_id")): x for x in packet.get("runs") or []}
        routing = []
        for candidate in packet.get("ready_work") or []:
            row = dict(candidate)
            entry = run_map.get(str(row.get("run_id"))) or {}
            projection = entry.get("projection") or {}
            state = (projection.get("node_states") or {}).get(str(row.get("node_id")))
            row["reducer_state"] = state
            row["readiness_basis"] = "INFERRED_DEPENDENCY_READY"
            row["claim_eligible"] = False
            routing.append(row)

        claimable = []
        suppressed = list(packet.get("claim_readiness_suppressed") or [])
        for run_id, entry in sorted(run_map.items()):
            if entry.get("reduction_basis") != "EVENT_REDUCED":
                continue
            projection = entry.get("projection") or {}
            for node_id, state in sorted((projection.get("node_states") or {}).items()):
                if state != "READY":
                    continue
                manifest = self._manifest(packet, run_id)
                node = self._node(manifest, node_id)
                path = str(node.get("claim_path") or "")
                expected_path = _claim_path(run_id, node_id)
                if path != expected_path:
                    packet.setdefault("residuals", []).append(
                        {
                            "kind": "CLAIM_CONTRACT",
                            "code": "CLAIM_PATH_MISMATCH",
                            "run_id": run_id,
                            "node_id": node_id,
                            "claim_path": path,
                            "expected_claim_path": expected_path,
                        }
                    )
                    continue
                if self._claim_exists(packet, run_id, node_id):
                    suppressed.append(
                        {
                            "run_id": run_id,
                            "node_id": node_id,
                            "claim_path": path,
                            "reason": "FIXED_CLAIM_PATH_PRESENT_BEFORE_EVENT_RECONCILIATION",
                        }
                    )
                    packet.setdefault("residuals", []).append(
                        {
                            "kind": "CLAIM_EVENT_LAG",
                            "code": "EVENT_READY_WITH_PROVIDER_CLAIM_PRESENT",
                            "run_id": run_id,
                            "node_id": node_id,
                            "claim_path": path,
                            "observability": "OBSERVED_PROVIDER_STATE",
                        }
                    )
                    continue
                claimable.append(
                    {
                        "run_id": run_id,
                        "objective_id": entry.get("objective_id"),
                        "node_id": node_id,
                        "role_capability": node.get("role_capability"),
                        "claim_path": path,
                        "priority": int(entry.get("priority") or 0),
                        "dependency_release": self.frontier._dependency_release(manifest, node_id),
                        "attempts_remaining": max(
                            0,
                            int(node.get("max_attempts") or 0)
                            - int((projection.get("attempts") or {}).get(node_id) or 0),
                        ),
                        "production_authority": entry.get("production_authority"),
                        "reducer_state": "READY",
                        "readiness_basis": "EVENT_READY",
                        "claim_eligible": True,
                    }
                )

        packet["routing_ready_work"] = sorted(
            routing,
            key=lambda x: (-int(x.get("priority") or 0), str(x.get("run_id")), str(x.get("node_id"))),
        )
        packet["ready_work"] = list(packet["routing_ready_work"])
        packet["claimable_work"] = sorted(
            claimable,
            key=lambda x: (-int(x.get("priority") or 0), str(x.get("run_id")), str(x.get("node_id"))),
        )
        packet["claim_readiness_suppressed"] = sorted(
            {json.dumps(x, sort_keys=True): x for x in suppressed}.values(),
            key=lambda x: (str(x.get("run_id")), str(x.get("node_id")), str(x.get("reason"))),
        )
        packet.setdefault("source_coverage", {})["event_ready_claimable_nodes"] = len(claimable)
        laws = list(packet.get("laws") or [])
        for law in (
            "INFERRED_READY != EVENT_READY",
            "DEPENDENCIES_SATISFIED != CLAIM_AUTHORITY",
            "CLAIM_PREPARE_REQUIRES_EVENT_READY",
        ):
            if law not in laws:
                laws.append(law)
        packet["laws"] = laws

        keys = (
            "generated_from",
            "objectives",
            "runs",
            "pressures",
            "routing_ready_work",
            "claimable_work",
            "claims",
            "claim_readiness_suppressed",
            "residuals",
            "source_coverage",
            "authority",
            "sched_contract",
            "laws",
        )
        packet["frontier_digest"] = _sha(_strip_clock({key: packet.get(key) for key in keys}))
        packet["frontier_digest_basis"] = (
            "reduced runtime content plus pinned SCHED contract; routing-ready and event-ready claimable work are "
            "separate content coordinates; repository clocks/witness transport remain independent"
        )
        return packet

    def provider_status(self, **kwargs) -> dict:
        packet = self.frontier.hydrate(**kwargs)
        contract = self._contract(packet["source_head"])
        repo = self._remote_repo(kwargs.get("remote", "origin"))
        token_present = self._token_present()
        write_ready = bool(
            packet.get("status") == "HYDRATED"
            and packet.get("remote_checked")
            and contract.get("status") == "PASS"
            and repo
            and token_present
        )
        status = "CLAIM_PROVIDER_READY" if write_ready else "CLAIM_PROVIDER_HOLD"
        return {
            "status": status,
            "source_ref": packet.get("source_ref"),
            "source_head": packet.get("source_head"),
            "frontier_digest": packet.get("frontier_digest"),
            "prompt_stack_digest": packet.get("prompt_stack_digest"),
            "remote_checked": bool(packet.get("remote_checked")),
            "provider_repo": repo,
            "provider_branch": packet.get("source_ref"),
            "provider_token_configured": token_present,
            "claim_contract": contract,
            "claimable_work_count": len(packet.get("claimable_work") or []),
            "routing_ready_work_count": len(packet.get("routing_ready_work") or []),
            "write_ready": write_ready,
            "laws": [
                "PROVIDER_CREDENTIAL != AUTHORITY_BYPASS",
                "CLAIM_CONTRACT_PASS_REQUIRES_EXACT_FIVE_BLOB_IDENTITY",
                "CLAIM_PROVIDER_STATUS != CLAIM_EXECUTION",
            ],
        }

    @staticmethod
    def _changed(expected: dict, packet: dict, contract: dict) -> dict:
        return {
            "source_head": packet.get("source_head") != expected.get("source_head"),
            "frontier_digest": packet.get("frontier_digest") != expected.get("frontier_digest"),
            "prompt_stack_digest": packet.get("prompt_stack_digest") != expected.get("prompt_stack_digest"),
            "claim_contract_digest": contract.get("claim_contract_digest") != expected.get("claim_contract_digest"),
            "remote_witness": not bool(packet.get("remote_checked")),
        }

    def _readiness_event_prepare(self, packet: dict, run_id: str, node_id: str) -> dict:
        manifest = self._manifest(packet, run_id)
        node = self._node(manifest, node_id)
        events = self._events(packet, run_id)
        entry = self._run_projection(packet, run_id) or {}
        projection = entry.get("projection") or {}
        state = (projection.get("node_states") or {}).get(node_id)
        if state != "PENDING":
            raise ValueError(f"readiness prerequisite requires PENDING, found {state}")
        routing = next(
            (
                x
                for x in packet.get("routing_ready_work") or []
                if str(x.get("run_id")) == run_id and str(x.get("node_id")) == node_id
            ),
            None,
        )
        if routing is None:
            raise ValueError("node is not dependency-ready")
        sequence = len(events) + 1
        at = _iso(_utcnow())
        event_id = f"node-ready-{_sha({'source_head': packet['source_head'], 'run_id': run_id, 'node_id': node_id, 'sequence': sequence})[:24]}"
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
        after = self.frontier._reduce_events(manifest, [*events, event])
        if (after.get("node_states") or {}).get(node_id) != "READY":
            raise ValueError("NODE_READY prerequisite does not reduce to READY")
        return {
            "status": "NODE_READY_APPEND_PREPARED",
            "run_id": run_id,
            "node_id": node_id,
            "basis_stream_digest": _sha(events),
            "sequence": sequence,
            "event_id": event_id,
            "provider": _provider_packet(_event_path(run_id, sequence), event, kind="EVENT_V1"),
            "projection_after": after,
            "law": "NODE_READY_APPEND_PREPARED != EVENT_PERSISTED; readiness is a separate provider effect",
        }

    def _claim_effect_prepare(self, packet: dict, run_id: str, node_id: str, worker_role: str | None, lease_seconds: int) -> dict:
        manifest = self._manifest(packet, run_id)
        node = self._node(manifest, node_id)
        entry = self._run_projection(packet, run_id) or {}
        projection = entry.get("projection") or {}
        if (projection.get("node_states") or {}).get(node_id) != "READY":
            raise ValueError("claim preparation requires reducer state READY")
        if self._claim_exists(packet, run_id, node_id):
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
        now = _utcnow()
        events = self._events(packet, run_id)
        snapshot = {
            "source_head": packet.get("source_head"),
            "frontier_digest": packet.get("frontier_digest"),
            "prompt_stack_digest": packet.get("prompt_stack_digest"),
            "run_id": run_id,
            "node_id": node_id,
            "event_stream_digest": _sha(events),
        }
        claim = {
            "schema_version": "CLAIM_V1",
            "run_id": run_id,
            "node_id": node_id,
            "worker_role": role,
            "attempt": attempt,
            "policy_commit": policy_commit,
            "claimed_at": _iso(now),
            "lease_expires_at": _iso(now + timedelta(seconds=lease_seconds)),
            "input_snapshot_digest": _sha(snapshot),
            "production_authority": "HOLD",
        }
        path = _claim_path(run_id, node_id)
        if str(node.get("claim_path") or "") != path:
            raise ValueError("manifest claim_path does not match fixed provider path")
        return {
            "status": "CLAIM_EFFECT_PREPARED",
            "run_id": run_id,
            "node_id": node_id,
            "worker_role": role,
            "attempt": attempt,
            "claim_path": path,
            "basis_stream_digest": _sha(events),
            "claim_digest": _sha(claim),
            "provider": _provider_packet(path, claim, kind="CLAIM_V1"),
            "law": "CLAIM_EFFECT_PREPARED != CLAIM_CREATED; provider create-if-absent owns exclusion",
        }

    def claim_prepare(
        self,
        *,
        expected_source_head: str,
        expected_frontier_digest: str,
        expected_prompt_stack_digest: str,
        expected_claim_contract_digest: str,
        run_id: str,
        node_id: str,
        worker_role: str | None = None,
        lease_seconds: int = 900,
        **kwargs,
    ) -> dict:
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
        run_id = _safe_id(run_id, "run_id")
        node_id = _safe_id(node_id, "node_id")
        claimable = next(
            (
                x
                for x in packet.get("claimable_work") or []
                if str(x.get("run_id")) == run_id and str(x.get("node_id")) == node_id
            ),
            None,
        )
        if claimable is None:
            routing = next(
                (
                    x
                    for x in packet.get("routing_ready_work") or []
                    if str(x.get("run_id")) == run_id and str(x.get("node_id")) == node_id
                ),
                None,
            )
            if routing is not None:
                return {
                    "status": "EVENT_READY_REQUIRED_HOLD",
                    "run_id": run_id,
                    "node_id": node_id,
                    "reducer_state": routing.get("reducer_state"),
                    "readiness_prerequisite": self._readiness_event_prepare(packet, run_id, node_id),
                    "law": "INFERRED_READY != EVENT_READY; persist and rehydrate NODE_READY before claim preparation",
                }
            return {
                "status": "CLAIM_NODE_NOT_EVENT_READY_HOLD",
                "run_id": run_id,
                "node_id": node_id,
                "law": "CLAIM_PREPARE_REQUIRES_EVENT_READY",
            }
        prepared = self._claim_effect_prepare(packet, run_id, node_id, worker_role, lease_seconds)
        prepared["address"] = {
            "source_head": packet.get("source_head"),
            "frontier_digest": packet.get("frontier_digest"),
            "prompt_stack_digest": packet.get("prompt_stack_digest"),
            "claim_contract_digest": contract.get("claim_contract_digest"),
            "remote_checked": packet.get("remote_checked"),
        }
        prepared["claim_contract"] = contract
        return prepared

    def call_tool(self, name: str, arguments: dict) -> dict:
        common = {
            "task": arguments.get("task", ""),
            "profile": arguments.get("profile"),
            "source_ref": arguments.get("source_ref", "athena-runtime-v3-candidate"),
            "remote": arguments.get("remote", "origin"),
            "fetch": arguments.get("fetch", True),
        }
        if name == "athena_frontier_provider_status":
            return self.provider_status(**common)
        if name == "athena_frontier_claim_prepare":
            return self.claim_prepare(
                expected_source_head=arguments["expected_source_head"],
                expected_frontier_digest=arguments["expected_frontier_digest"],
                expected_prompt_stack_digest=arguments["expected_prompt_stack_digest"],
                expected_claim_contract_digest=arguments["expected_claim_contract_digest"],
                run_id=arguments["run_id"],
                node_id=arguments["node_id"],
                worker_role=arguments.get("worker_role"),
                lease_seconds=arguments.get("lease_seconds", 900),
                **common,
            )
        raise KeyError(name)


FRONTIER_CLAIM_TOOLS = [
    {
        "name": "athena_frontier_provider_status",
        "description": "Report the fresh bounded GitHub claim-provider capability and exact five-blob SCHED claim/journal contract without exposing credentials or executing a write.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task": {"type": "string"},
                "profile": {"type": ["string", "null"]},
                "source_ref": {"type": "string"},
                "remote": {"type": "string"},
                "fetch": {"type": "boolean"},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_frontier_claim_prepare",
        "description": "No-write preparation of a bounded fixed-path CLAIM_V1 from exact EVENT_READY state under fresh H/P/F/C/W. Inferred PENDING readiness returns a reducer-validated NODE_READY prerequisite instead of manufacturing claim authority.",
        "inputSchema": {
            "type": "object",
            "required": [
                "expected_source_head",
                "expected_frontier_digest",
                "expected_prompt_stack_digest",
                "expected_claim_contract_digest",
                "run_id",
                "node_id"
            ],
            "properties": {
                "expected_source_head": {"type": "string"},
                "expected_frontier_digest": {"type": "string"},
                "expected_prompt_stack_digest": {"type": "string"},
                "expected_claim_contract_digest": {"type": "string"},
                "run_id": {"type": "string"},
                "node_id": {"type": "string"},
                "worker_role": {"type": ["string", "null"]},
                "lease_seconds": {"type": "integer", "minimum": 60, "maximum": 3600},
                "task": {"type": "string"},
                "profile": {"type": ["string", "null"]},
                "source_ref": {"type": "string"},
                "remote": {"type": "string"},
                "fetch": {"type": "boolean"}
            },
            "additionalProperties": False,
        },
    },
]
FRONTIER_CLAIM_TOOL_NAMES = {tool["name"] for tool in FRONTIER_CLAIM_TOOLS}


def install_frontier_claim_extension(runtime_cls, frontier_tools: list[dict]) -> None:
    """Install the no-write claim vocabulary and tools once."""

    if getattr(runtime_cls, "_athena_frontier_claim_prepare_v1_registered", False):
        return

    original_hydrate = runtime_cls.hydrate
    original_call = runtime_cls.call_tool

    def hydrate_with_claim_state(self, *args, **kwargs):
        packet = original_hydrate(self, *args, **kwargs)
        return FrontierClaimRuntime(self).augment_packet(packet)

    def call_with_claim_tools(self, name, arguments):
        if name in FRONTIER_CLAIM_TOOL_NAMES:
            return FrontierClaimRuntime(self).call_tool(name, arguments)
        return original_call(self, name, arguments)

    runtime_cls.hydrate = hydrate_with_claim_state
    runtime_cls.call_tool = call_with_claim_tools
    for tool in FRONTIER_CLAIM_TOOLS:
        if not any(existing.get("name") == tool["name"] for existing in frontier_tools):
            frontier_tools.append(tool)
    runtime_cls._athena_frontier_claim_prepare_v1_registered = True
