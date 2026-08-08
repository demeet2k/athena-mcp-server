from __future__ import annotations

import hashlib
import json
import subprocess
from collections import defaultdict
from pathlib import Path

from .git_backend import GitBackend, GitStateError
from .prompt_runtime import PromptRuntime

DEFAULT_SOURCE_REF = "athena-runtime-v3-candidate"
SCHED_V3_CONTRACT_BLOBS = {
    "orchestration/v3/reducer.py": "122802a3cec6f50b692d819b18024b50be39bab8",
    "orchestration/v3/ready.py": "975d61ab5ddf42e6e06c7304fc0fc330ca4b24d5",
    "orchestration/v3/claim.py": "4757f4eaf8180cf356dc0e940b9019177f1c0a8a",
}
TERMINAL_RUN_STATES = {"COMMITTED", "PARTIAL_HOLD", "BLOCKED", "ABORTED"}
NODE_TRANSITIONS = {
    "NODE_READY": "READY",
    "CLAIM_ACQUIRED": "CLAIMED",
    "ACTION_ATTEMPTED": "RUNNING",
    "CHECKPOINT_WRITTEN": "CHECKPOINTED",
    "NODE_SUCCEEDED": "SUCCEEDED",
    "NODE_FAILED": "FAILED",
    "NODE_HELD": "HELD",
}


def _run(root: Path, *args: str):
    return subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True)


def _canonical(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha(value) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


class FrontierRuntime:
    """Data-only braid between the Git prompt brain and SCHED V3 live state.

    The SCHED implementation files are treated as pinned contracts, not executed.
    Runtime state is read from an exact Git commit without checking out that ref.
    """

    def __init__(self, git: GitBackend, prompt_runtime: PromptRuntime | None = None, contract_blobs=None):
        self.git = git
        self.prompt_runtime = prompt_runtime or PromptRuntime(git)
        self.contract_blobs = dict(SCHED_V3_CONTRACT_BLOBS if contract_blobs is None else contract_blobs)

    def _root(self) -> Path:
        if not self.git.enabled:
            raise GitStateError("ATHENA_GIT_ROOT is required for frontier runtime")
        return self.git.root

    def _remote_exists(self, remote: str) -> bool:
        p = _run(self._root(), "remote", "get-url", remote)
        return p.returncode == 0 and bool(p.stdout.strip())

    def _source(self, source_ref: str, remote: str = "origin", fetch: bool = True):
        checked = False
        fetch_error = None
        resolved_ref = source_ref
        if fetch and self._remote_exists(remote):
            p = _run(self._root(), "fetch", "--prune", remote)
            if p.returncode:
                fetch_error = p.stderr.strip() or p.stdout.strip()
            else:
                checked = True
                remote_ref = f"refs/remotes/{remote}/{source_ref}"
                probe = _run(self._root(), "rev-parse", "--verify", remote_ref)
                if probe.returncode == 0:
                    resolved_ref = remote_ref
        p = _run(self._root(), "rev-parse", "--verify", f"{resolved_ref}^{{commit}}")
        if p.returncode:
            raise GitStateError(p.stderr.strip() or p.stdout.strip() or f"frontier source ref unavailable: {resolved_ref}")
        return {
            "source_ref": source_ref,
            "resolved_ref": resolved_ref,
            "source_head": p.stdout.strip(),
            "remote": remote,
            "remote_checked": checked,
            "fetch_error": fetch_error,
        }

    def _blob(self, commit: str, path: str):
        p = _run(self._root(), "rev-parse", "--verify", f"{commit}:{path}")
        return p.stdout.strip() if p.returncode == 0 else None

    def _contract(self, commit: str):
        rows = {}
        ok = True
        for path, expected in self.contract_blobs.items():
            actual = self._blob(commit, path)
            match = actual == expected
            rows[path] = {"expected_blob": expected, "actual_blob": actual, "match": match}
            ok = ok and match
        return {
            "status": "PASS" if ok else "SCHED_CONTRACT_CHANGED_HOLD",
            "contracts": rows,
            "law": "SCHED contract changes require explicit frontier reducer revalidation; repository code is never dynamically executed",
        }

    def _paths(self, commit: str, *prefixes: str):
        p = _run(self._root(), "ls-tree", "-r", "--name-only", commit, "--", *prefixes)
        if p.returncode:
            raise GitStateError(p.stderr.strip() or p.stdout.strip())
        return sorted(x.strip() for x in p.stdout.splitlines() if x.strip())

    def _text(self, commit: str, path: str):
        p = _run(self._root(), "show", f"{commit}:{path}")
        if p.returncode:
            return None
        return p.stdout

    def _json(self, commit: str, path: str):
        text = self._text(commit, path)
        if text is None:
            return None
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise GitStateError(f"invalid JSON at {path}: {exc}") from exc

    @staticmethod
    def _run_id_from_path(path: str):
        parts = Path(path).parts
        try:
            i = parts.index("runs")
            return parts[i + 1]
        except (ValueError, IndexError):
            return None

    @staticmethod
    def _objective_id(objective):
        return objective.get("objective_id") or objective.get("id")

    @staticmethod
    def _objective_for_run(run, objectives):
        ref = str(run.get("objective_ref") or "")
        for objective in objectives:
            oid = str(objective.get("objective_id") or "")
            if ref in {oid, f"runtime/queue/{oid}.json"}:
                return objective
        return None

    @staticmethod
    def _reduce_events(run, events):
        nodes = {str(n["node_id"]): n for n in run.get("nodes") or []}
        node_states = {node_id: "PENDING" for node_id in nodes}
        attempts = {node_id: 0 for node_id in nodes}
        receipts = {node_id: False for node_id in nodes}
        checkpoints = {node_id: 0 for node_id in nodes}
        claims = {}
        run_state = "ABSENT"
        expected_sequence = 1
        last_event_id = None
        for event in sorted(events, key=lambda x: int(x.get("sequence", 0))):
            if int(event.get("sequence", 0)) != expected_sequence:
                raise GitStateError(f"SCHED event sequence gap in {run.get('run_id')}: expected {expected_sequence}")
            expected_sequence += 1
            if event.get("run_id") != run.get("run_id"):
                raise GitStateError("SCHED event run identity mismatch")
            event_type = event.get("event_type")
            node_id = event.get("node_id")
            data = event.get("data") or {}
            last_event_id = event.get("event_id")
            if run_state in TERMINAL_RUN_STATES and event_type != "AUDIT_WRITTEN":
                raise GitStateError("SCHED non-audit event follows terminal run")
            if event_type == "RUN_CREATED":
                if run_state != "ABSENT" or node_id is not None:
                    raise GitStateError("invalid RUN_CREATED")
                run_state = "QUEUED"
                continue
            if event_type == "RUN_ADMITTED":
                if run_state != "QUEUED" or data.get("verdict") != "PASS":
                    raise GitStateError("invalid RUN_ADMITTED")
                run_state = "ADMITTED"
                continue
            if event_type in NODE_TRANSITIONS or event_type == "RECEIPT_WRITTEN":
                if node_id not in nodes:
                    raise GitStateError(f"event references unknown node {node_id}")
                current = node_states[node_id]
                node = nodes[node_id]
                if event_type == "NODE_READY":
                    if current != "PENDING" or any(node_states[str(dep)] != "SUCCEEDED" for dep in node.get("depends_on") or []):
                        raise GitStateError("invalid NODE_READY")
                    node_states[node_id] = "READY"
                    run_state = "RUNNING"
                elif event_type == "CLAIM_ACQUIRED":
                    if current != "READY" or data.get("claim_path") != node.get("claim_path"):
                        raise GitStateError("invalid CLAIM_ACQUIRED")
                    claims[node_id] = data.get("claim_path")
                    node_states[node_id] = "CLAIMED"
                elif event_type == "ACTION_ATTEMPTED":
                    if current not in {"CLAIMED", "CHECKPOINTED"}:
                        raise GitStateError("invalid ACTION_ATTEMPTED")
                    attempts[node_id] += 1
                    if attempts[node_id] > int(node.get("max_attempts", 0)):
                        raise GitStateError("node attempt ceiling exceeded")
                    node_states[node_id] = "RUNNING"
                elif event_type == "CHECKPOINT_WRITTEN":
                    if current != "RUNNING":
                        raise GitStateError("invalid CHECKPOINT_WRITTEN")
                    checkpoints[node_id] += 1
                    node_states[node_id] = "CHECKPOINTED"
                elif event_type == "RECEIPT_WRITTEN":
                    if current not in {"RUNNING", "CHECKPOINTED"} or receipts[node_id]:
                        raise GitStateError("invalid RECEIPT_WRITTEN")
                    receipts[node_id] = True
                elif event_type == "NODE_SUCCEEDED":
                    if current not in {"RUNNING", "CHECKPOINTED"} or not receipts[node_id]:
                        raise GitStateError("invalid NODE_SUCCEEDED")
                    node_states[node_id] = "SUCCEEDED"
                elif event_type == "NODE_FAILED":
                    if current not in {"CLAIMED", "RUNNING", "CHECKPOINTED"}:
                        raise GitStateError("invalid NODE_FAILED")
                    node_states[node_id] = "FAILED"
                elif event_type == "NODE_HELD":
                    if current not in {"READY", "CLAIMED", "RUNNING", "CHECKPOINTED"}:
                        raise GitStateError("invalid NODE_HELD")
                    node_states[node_id] = "HELD"
                if all(state == "SUCCEEDED" for state in node_states.values()):
                    run_state = "READY_TO_COMMIT"
                elif any(nodes[n]["role_capability"] in {"verifier", "adversary", "committer", "auditor"} and s in {"READY", "CLAIMED", "RUNNING", "CHECKPOINTED", "SUCCEEDED"} for n, s in node_states.items()):
                    run_state = "VERIFYING"
                continue
            if event_type == "RUN_COMMITTED":
                if run_state != "READY_TO_COMMIT":
                    raise GitStateError("invalid RUN_COMMITTED")
                run_state = "COMMITTED"
            elif event_type == "RUN_PARTIAL_HOLD":
                if run_state not in {"ADMITTED", "RUNNING", "VERIFYING"}:
                    raise GitStateError("invalid RUN_PARTIAL_HOLD")
                run_state = "PARTIAL_HOLD"
            elif event_type == "RUN_BLOCKED":
                if run_state not in {"ADMITTED", "RUNNING", "VERIFYING"}:
                    raise GitStateError("invalid RUN_BLOCKED")
                run_state = "BLOCKED"
            elif event_type == "RUN_ABORTED":
                if run_state not in {"QUEUED", "ADMITTED", "RUNNING", "VERIFYING"}:
                    raise GitStateError("invalid RUN_ABORTED")
                run_state = "ABORTED"
            elif event_type == "AUDIT_WRITTEN":
                if run_state not in TERMINAL_RUN_STATES:
                    raise GitStateError("invalid AUDIT_WRITTEN")
        ready = []
        if run_state not in TERMINAL_RUN_STATES:
            for node_id, node in sorted(nodes.items()):
                if node_states[node_id] != "PENDING":
                    continue
                if all(node_states[str(dep)] == "SUCCEEDED" for dep in node.get("depends_on") or []):
                    ready.append(node_id)
        return {
            "run_state": run_state,
            "node_states": node_states,
            "attempts": attempts,
            "receipt_written": receipts,
            "checkpoint_counts": checkpoints,
            "claim_paths": claims,
            "event_count": len(events),
            "last_event_id": last_event_id,
            "ready_nodes": ready,
        }

    @staticmethod
    def _dependency_release(run, node_id):
        return sum(1 for node in run.get("nodes") or [] if node_id in [str(x) for x in node.get("depends_on") or []])

    def hydrate(self, task: str = "", profile: str | None = None, source_ref: str = DEFAULT_SOURCE_REF, remote: str = "origin", fetch: bool = True):
        source = self._source(source_ref, remote, fetch)
        commit = source["source_head"]
        contract = self._contract(commit)
        paths = self._paths(commit, "runtime/queue", "runtime/runs")
        objective_paths = [p for p in paths if p.startswith("runtime/queue/objective.") and p.endswith(".json")]
        manifest_paths = [p for p in paths if p.startswith("runtime/runs/") and p.endswith("/manifest.json")]
        objectives = [self._json(commit, p) for p in objective_paths]
        objectives = [x for x in objectives if isinstance(x, dict)]
        manifests = [self._json(commit, p) for p in manifest_paths]
        manifests = [x for x in manifests if isinstance(x, dict)]
        by_run_paths = defaultdict(list)
        for path in paths:
            run_id = self._run_id_from_path(path)
            if run_id:
                by_run_paths[run_id].append(path)

        runs = []
        ready_work = []
        all_claims = []
        pressures = []
        residuals = []
        for run in manifests:
            run_id = str(run.get("run_id"))
            rpaths = sorted(by_run_paths.get(run_id) or [])
            event_paths = [p for p in rpaths if f"runtime/runs/{run_id}/events/" in p and p.endswith(".json")]
            claim_paths = [p for p in rpaths if f"runtime/runs/{run_id}/claims/" in p and p.endswith(".json")]
            receipt_paths = [p for p in rpaths if f"runtime/runs/{run_id}/receipts/" in p and p.endswith(".json")]
            checkpoint_paths = [p for p in rpaths if f"runtime/runs/{run_id}/checkpoints/" in p and p.endswith(".json")]
            terminal_path = f"runtime/runs/{run_id}/terminal.json"
            audit_path = f"runtime/runs/{run_id}/audit.json"
            terminal = self._json(commit, terminal_path) if terminal_path in rpaths else None
            audit = self._json(commit, audit_path) if audit_path in rpaths else None
            claims = [self._json(commit, p) for p in claim_paths]
            claims = [x for x in claims if isinstance(x, dict)]
            all_claims.extend({"run_id": run_id, **x} for x in claims)
            coverage = {
                "manifest": True,
                "events": bool(event_paths),
                "claims": len(claim_paths),
                "receipts": len(receipt_paths),
                "checkpoints": len(checkpoint_paths),
                "terminal": terminal is not None,
                "audit": audit is not None,
            }
            projection = None
            reduction_basis = "INSUFFICIENT_FOR_REPLAY"
            reduction_error = None
            if event_paths and contract["status"] == "PASS":
                try:
                    events = [self._json(commit, p) for p in event_paths]
                    projection = self._reduce_events(run, events)
                    reduction_basis = "EVENT_REDUCED"
                except Exception as exc:
                    reduction_error = str(exc)
            elif terminal is not None:
                projection = {
                    "run_state": terminal.get("disposition", "UNKNOWN"),
                    "node_states": terminal.get("node_states") or {},
                    "event_count": None,
                    "ready_nodes": [],
                }
                reduction_basis = "TERMINAL_PROJECTION_ONLY"
            objective = self._objective_for_run(run, objectives)
            priority = int((objective or {}).get("priority") or 0)
            entry = {
                "run_id": run_id,
                "objective_id": self._objective_id(objective or {}) or run.get("objective_ref"),
                "artifact_target": run.get("artifact_target") or (objective or {}).get("artifact_target"),
                "priority": priority,
                "production_authority": (objective or {}).get("production_authority"),
                "work_class": run.get("work_class") or (objective or {}).get("work_class"),
                "coverage": coverage,
                "reduction_basis": reduction_basis,
                "projection": projection,
                "reduction_error": reduction_error,
            }
            runs.append(entry)
            if not event_paths:
                pressure = {"kind": "SOURCE_COVERAGE", "code": "MISSING_EVENT_STREAM", "run_id": run_id, "observability": "OBSERVED", "source_ref": manifest_paths[0] if len(manifest_paths) == 1 else f"runtime/runs/{run_id}", "priority": priority}
                pressures.append(pressure);residuals.append(pressure)
            if reduction_error:
                pressure = {"kind": "SOURCE_COVERAGE", "code": "EVENT_REDUCTION_FAILED", "run_id": run_id, "observability": "OBSERVED", "detail": reduction_error, "priority": priority}
                pressures.append(pressure);residuals.append(pressure)
            if projection and reduction_basis == "EVENT_REDUCED":
                node_specs = {str(n["node_id"]): n for n in run.get("nodes") or []}
                for node_id in projection.get("ready_nodes") or []:
                    node = node_specs[node_id]
                    candidate = {
                        "run_id": run_id,
                        "objective_id": entry["objective_id"],
                        "node_id": node_id,
                        "role_capability": node.get("role_capability"),
                        "claim_path": node.get("claim_path"),
                        "priority": priority,
                        "dependency_release": self._dependency_release(run, node_id),
                        "attempts_remaining": max(0, int(node.get("max_attempts") or 0) - int((projection.get("attempts") or {}).get(node_id) or 0)),
                        "production_authority": entry["production_authority"],
                        "source_head": commit,
                    }
                    ready_work.append(candidate)
                    pressures.append({"kind": "READY_WORK", "run_id": run_id, "node_id": node_id, "priority": priority, "observability": "REDUCED_FROM_EVENTS"})
            if terminal and terminal.get("next_frontier"):
                residuals.append({"kind": "DECLARED_NEXT_FRONTIER", "run_id": run_id, "value": terminal.get("next_frontier"), "source_ref": terminal_path})
            if projection and projection.get("run_state") in {"PARTIAL_HOLD", "BLOCKED", "ABORTED"}:
                pressures.append({"kind": "RUN_TERMINAL_PRESSURE", "run_id": run_id, "state": projection.get("run_state"), "priority": priority, "observability": reduction_basis})

        objectives_out = [{
            "objective_id": self._objective_id(o),
            "priority": o.get("priority"),
            "artifact_target": o.get("artifact_target"),
            "risk_class": o.get("risk_class"),
            "work_class": o.get("work_class"),
            "production_authority": o.get("production_authority"),
        } for o in objectives]
        prompt = self.prompt_runtime.compile(task=task, profile=profile, include_text=False) if self.prompt_runtime.available else None
        packet = {
            "schema_version": "FRONTIER_PACKET_V1",
            "source_repo": str(self._root()),
            "source_ref": source_ref,
            "resolved_ref": source["resolved_ref"],
            "source_head": commit,
            "remote_checked": source["remote_checked"],
            "fetch_error": source["fetch_error"],
            "generated_from": sorted(objective_paths + manifest_paths),
            "objectives": sorted(objectives_out, key=lambda x: str(x.get("objective_id"))),
            "runs": sorted(runs, key=lambda x: x["run_id"]),
            "pressures": sorted(pressures, key=lambda x: (str(x.get("kind")), str(x.get("run_id")), str(x.get("node_id")))),
            "ready_work": sorted(ready_work, key=lambda x: (-int(x.get("priority") or 0), x["run_id"], x["node_id"])),
            "claims": sorted(all_claims, key=lambda x: (str(x.get("run_id")), str(x.get("node_id")))),
            "residuals": sorted(residuals, key=lambda x: (str(x.get("kind")), str(x.get("run_id")))),
            "source_coverage": {
                "objective_count": len(objectives_out),
                "run_count": len(runs),
                "event_reduced_runs": sum(1 for r in runs if r["reduction_basis"] == "EVENT_REDUCED"),
                "terminal_projection_only_runs": sum(1 for r in runs if r["reduction_basis"] == "TERMINAL_PROJECTION_ONLY"),
                "insufficient_for_replay_runs": sum(1 for r in runs if r["reduction_basis"] == "INSUFFICIENT_FOR_REPLAY"),
            },
            "authority": {
                "law": "FRONTIER_BRAID != EXECUTION_AUTHORIZATION",
                "production_authorities": sorted({str(x.get("production_authority")) for x in objectives_out}),
            },
            "sched_contract": contract,
            "prompt_stack_digest": prompt.get("prompt_stack_digest") if prompt else None,
            "prompt_git_head": prompt.get("git_head") if prompt else None,
            "laws": [
                "PROMPT_STACK_DIGEST != FRONTIER_DIGEST",
                "PROMPT_POLICY != RUNTIME_STATE",
                "QUEUE_ENTRY != CLAIM",
                "CLAIM != COMPLETION",
                "PRESSURE != EVIDENCE",
                "FRONTIER_BRAID != EXECUTION_AUTHORIZATION",
                "MISSING_EVENT_STREAM != REPLAYABLE_STATE",
            ],
        }
        digest_basis = {k: v for k, v in packet.items() if k not in {"frontier_digest", "prompt_stack_digest", "prompt_git_head"}}
        packet["frontier_digest"] = _sha(digest_basis)
        packet["status"] = "HYDRATED" if contract["status"] == "PASS" else "SCHED_CONTRACT_CHANGED_HOLD"
        if not source["remote_checked"]:
            packet["status"] = "FRONTIER_REMOTE_UNVERIFIED_HOLD"
        return packet

    def freshness(self, expected_source_head: str, expected_frontier_digest: str, expected_prompt_stack_digest: str | None = None, **kwargs):
        current = self.hydrate(**kwargs)
        changed = {
            "shared_source_head": current["source_head"] != expected_source_head,
            "frontier_digest": current["frontier_digest"] != expected_frontier_digest,
            "prompt_stack_digest": bool(expected_prompt_stack_digest and current.get("prompt_stack_digest") != expected_prompt_stack_digest),
        }
        return {"status": "STALE" if any(changed.values()) else "FRESH", "changed": changed, "requires_rehydrate": any(changed.values()), "current": current}

    @staticmethod
    def _dominates(a, b):
        keys = ("priority", "dependency_release", "attempts_remaining")
        return all(int(a.get(k) or 0) >= int(b.get(k) or 0) for k in keys) and any(int(a.get(k) or 0) > int(b.get(k) or 0) for k in keys)

    def select(self, **kwargs):
        packet = self.hydrate(**kwargs)
        candidates = packet.get("ready_work") or []
        if packet["status"] != "HYDRATED":
            return {"status": "FRONTIER_HOLD", "reason": packet["status"], "frontier": packet, "selected": None, "pareto_front": []}
        front = [a for a in candidates if not any(self._dominates(b, a) for b in candidates if b is not a)]
        if not front:
            return {"status": "NO_REPLAYABLE_READY_WORK", "frontier": packet, "selected": None, "pareto_front": []}
        selected = front[0] if len(front) == 1 else None
        return {
            "status": "SELECTED" if selected else "PARETO_HOLD",
            "selected": selected,
            "pareto_front": front,
            "frontier_digest": packet["frontier_digest"],
            "prompt_stack_digest": packet.get("prompt_stack_digest"),
            "source_head": packet["source_head"],
            "law": "selection ranks only EVENT_REDUCED READY work; unknown costs/weights preserve Pareto ambiguity",
        }

    def call_tool(self, name: str, a: dict):
        common = {"task": a.get("task", ""), "profile": a.get("profile"), "source_ref": a.get("source_ref", DEFAULT_SOURCE_REF), "remote": a.get("remote", "origin"), "fetch": a.get("fetch", True)}
        if name == "athena_frontier_hydrate":
            return self.hydrate(**common)
        if name == "athena_frontier_freshness":
            return self.freshness(a["expected_source_head"], a["expected_frontier_digest"], a.get("expected_prompt_stack_digest"), **common)
        if name == "athena_frontier_select":
            return self.select(**common)
        raise KeyError(name)


FRONTIER_TOOLS = [
    {"name": "athena_frontier_hydrate", "description": "Reduce exact Git-resident SCHED V3 objective/run state into FRONTIER_PACKET_V1 and bind it to the current prompt-stack digest without conflating the two.", "inputSchema": {"type": "object", "properties": {"task": {"type": "string"}, "profile": {"type": ["string", "null"]}, "source_ref": {"type": "string"}, "remote": {"type": "string"}, "fetch": {"type": "boolean"}}, "additionalProperties": False}},
    {"name": "athena_frontier_freshness", "description": "Compare exact shared source head, frontier digest and prompt-stack digest; any material coordinate change requires rehydration.", "inputSchema": {"type": "object", "required": ["expected_source_head", "expected_frontier_digest"], "properties": {"expected_source_head": {"type": "string"}, "expected_frontier_digest": {"type": "string"}, "expected_prompt_stack_digest": {"type": ["string", "null"]}, "task": {"type": "string"}, "profile": {"type": ["string", "null"]}, "source_ref": {"type": "string"}, "remote": {"type": "string"}, "fetch": {"type": "boolean"}}, "additionalProperties": False}},
    {"name": "athena_frontier_select", "description": "Return the Pareto frontier over replayably READY SCHED V3 nodes only. Missing event coverage or contract drift fails closed and never manufactures readiness.", "inputSchema": {"type": "object", "properties": {"task": {"type": "string"}, "profile": {"type": ["string", "null"]}, "source_ref": {"type": "string"}, "remote": {"type": "string"}, "fetch": {"type": "boolean"}}, "additionalProperties": False}},
]
FRONTIER_TOOL_NAMES = {x["name"] for x in FRONTIER_TOOLS}
