from __future__ import annotations

import base64
import json
import re
from typing import Any
from urllib import error, parse, request

from .frontier_claim import (
    FRONTIER_CLAIM_TOOLS,
    FRONTIER_CLAIM_TOOL_NAMES,
    FrontierClaimRuntime,
    _claim_path,
    _event_path,
    _provider_packet,
    _safe_id,
    _sha,
)

_BRANCH_RE = re.compile(r"^[A-Za-z0-9._/-]+$")
_CLAIM_PATH_RE = re.compile(r"^runtime/runs/([A-Za-z0-9._-]+)/claims/([A-Za-z0-9._-]+)\.json$")
_EVENT_PATH_RE = re.compile(r"^runtime/runs/([A-Za-z0-9._-]+)/events/(\d{8})\.json$")
_ALLOWED_EVENT_TYPES = {"NODE_READY", "CLAIM_ACQUIRED"}


def _safe_branch(value: str) -> str:
    text = str(value or "")
    if not text or not _BRANCH_RE.fullmatch(text) or text.startswith("/") or text.endswith("/") or ".." in text:
        raise ValueError("unsafe or empty provider branch")
    return text


def _content_text(content: dict) -> str:
    return json.dumps(content, sort_keys=True, indent=2, ensure_ascii=False) + "\n"


def _validate_provider_packet(packet: dict) -> tuple[str, str, dict, str]:
    if not isinstance(packet, dict) or packet.get("provider_operation") != "CREATE_FILE_IF_ABSENT":
        raise ValueError("provider packet must be CREATE_FILE_IF_ABSENT")
    kind = str(packet.get("kind") or "")
    path = str(packet.get("path") or "")
    content = packet.get("content")
    if not isinstance(content, dict):
        raise ValueError("provider packet content must be an object")
    rendered = _content_text(content)
    if packet.get("content_text") != rendered:
        raise ValueError("provider packet content_text mismatch")

    if kind == "CLAIM_V1":
        match = _CLAIM_PATH_RE.fullmatch(path)
        if not match:
            raise ValueError("CLAIM_V1 provider path is outside the bounded claim namespace")
        run_id, node_id = match.groups()
        if content.get("schema_version") != "CLAIM_V1":
            raise ValueError("claim schema_version mismatch")
        if str(content.get("run_id")) != run_id or str(content.get("node_id")) != node_id:
            raise ValueError("claim path/body identity mismatch")
        _safe_id(run_id, "run_id")
        _safe_id(node_id, "node_id")
    elif kind == "EVENT_V1":
        match = _EVENT_PATH_RE.fullmatch(path)
        if not match:
            raise ValueError("EVENT_V1 provider path is outside the bounded event namespace")
        run_id, sequence_text = match.groups()
        sequence = int(sequence_text)
        if content.get("schema_version") != "EVENT_V1":
            raise ValueError("event schema_version mismatch")
        if str(content.get("run_id")) != run_id or int(content.get("sequence") or 0) != sequence:
            raise ValueError("event path/body identity mismatch")
        if str(content.get("event_type") or "") not in _ALLOWED_EVENT_TYPES:
            raise ValueError("event type is outside the bounded claim/readiness membrane")
        _safe_id(run_id, "run_id")
    else:
        raise ValueError("unsupported bounded provider kind")
    return kind, path, content, rendered


class GitHubContentsCreateProvider:
    """Narrow GitHub Contents create-if-absent client.

    It cannot update or delete files, cannot accept arbitrary paths, and never
    returns credential material. The caller supplies provider packets produced by
    the claim/readiness runtime; this class only transports those exact bytes.
    """

    def __init__(self, runtime: FrontierClaimRuntime, *, opener=None, api_base: str = "https://api.github.com"):
        self.runtime = runtime
        self.opener = opener or request.urlopen
        self.api_base = api_base.rstrip("/")

    def _token(self) -> str | None:
        env = self.runtime.environ
        return env.get("ATHENA_GITHUB_TOKEN") or env.get("GH_TOKEN") or env.get("GITHUB_TOKEN")

    def create(self, *, repo: str, branch: str, packet: dict) -> dict:
        token = self._token()
        if not token:
            return {"status": "REMOTE_PROVIDER_UNAVAILABLE_HOLD", "reason": "provider token unavailable"}
        if not isinstance(repo, str) or repo.count("/") != 1:
            return {"status": "REMOTE_PROVIDER_UNAVAILABLE_HOLD", "reason": "provider repository unavailable"}
        owner, name = repo.split("/", 1)
        _safe_id(owner, "provider owner")
        _safe_id(name, "provider repo")
        safe_branch = _safe_branch(branch)
        try:
            kind, path, _content, rendered = _validate_provider_packet(packet)
        except ValueError as exc:
            return {"status": "PROVIDER_PACKET_REJECTED", "reason": str(exc)}

        encoded = base64.b64encode(rendered.encode("utf-8")).decode("ascii")
        body = json.dumps(
            {
                "message": f"ATHENA bounded {kind} create {path}",
                "content": encoded,
                "branch": safe_branch,
            },
            sort_keys=True,
        ).encode("utf-8")
        url = (
            f"{self.api_base}/repos/{parse.quote(owner, safe='')}/{parse.quote(name, safe='')}/contents/"
            f"{parse.quote(path, safe='/')}"
        )
        req = request.Request(
            url,
            data=body,
            method="PUT",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "Content-Type": "application/json",
                "User-Agent": "athena-mcp-frontier-claim-v2",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        try:
            with self.opener(req, timeout=20) as response:
                status_code = int(getattr(response, "status", 0) or 0)
                payload = json.loads(response.read().decode("utf-8") or "{}")
        except error.HTTPError as exc:
            if int(exc.code) in {409, 422}:
                return {"status": "EXISTS", "http_status": int(exc.code), "path": path, "kind": kind}
            return {"status": "PROVIDER_HOLD", "http_status": int(exc.code), "path": path, "kind": kind}
        except Exception as exc:
            return {"status": "PROVIDER_HOLD", "reason": type(exc).__name__, "path": path, "kind": kind}

        if status_code not in {200, 201}:
            return {"status": "PROVIDER_HOLD", "http_status": status_code, "path": path, "kind": kind}
        content_meta = payload.get("content") or {}
        commit_meta = payload.get("commit") or {}
        return {
            "status": "CREATED",
            "http_status": status_code,
            "path": path,
            "kind": kind,
            "content_sha": content_meta.get("sha"),
            "commit_sha": commit_meta.get("sha"),
        }


def _provider(runtime: FrontierClaimRuntime) -> GitHubContentsCreateProvider:
    return GitHubContentsCreateProvider(runtime, opener=getattr(runtime, "_athena_claim_provider_opener", None))


def _common(arguments: dict) -> dict:
    return {
        "task": arguments.get("task", ""),
        "profile": arguments.get("profile"),
        "source_ref": arguments.get("source_ref", "athena-runtime-v3-candidate"),
        "remote": arguments.get("remote", "origin"),
        "fetch": True,
    }


def _node_state(packet: dict, run_id: str, node_id: str) -> str | None:
    for entry in packet.get("runs") or []:
        if str(entry.get("run_id")) == run_id:
            return ((entry.get("projection") or {}).get("node_states") or {}).get(node_id)
    return None


def _expected_hold(runtime: FrontierClaimRuntime, arguments: dict) -> tuple[dict, dict] | tuple[None, None]:
    common = _common(arguments)
    packet = runtime.frontier.hydrate(**common)
    contract = runtime._contract(packet["source_head"])
    expected = {
        "source_head": arguments["expected_source_head"],
        "frontier_digest": arguments["expected_frontier_digest"],
        "prompt_stack_digest": arguments["expected_prompt_stack_digest"],
        "claim_contract_digest": arguments["expected_claim_contract_digest"],
    }
    changed = runtime._changed(expected, packet, contract)
    if any(changed.values()):
        return {
            "status": "CLAIM_STALE_ADDRESS_HOLD",
            "changed": changed,
            "law": "STALE_H_P_F_C_W -> REHYDRATE_BEFORE_PROVIDER_EFFECT",
        }, packet
    if packet.get("status") != "HYDRATED":
        return {"status": "CLAIM_FRONTIER_HOLD", "reason": packet.get("status")}, packet
    if contract.get("status") != "PASS":
        return {
            "status": "CLAIM_CONTRACT_HOLD",
            "claim_contract": contract,
            "law": "UNVERIFIED_OR_DRIFTED_JOURNAL_CONTRACT != EXECUTION_AUTHORITY",
        }, packet
    return None, packet


def _provider_context(runtime: FrontierClaimRuntime, arguments: dict) -> tuple[str | None, str, dict | None]:
    common = _common(arguments)
    repo = runtime._remote_repo(common["remote"])
    branch = common["source_ref"]
    if not repo or not runtime._token_present():
        return repo, branch, {
            "status": "REMOTE_PROVIDER_UNAVAILABLE_HOLD",
            "provider_repo": repo,
            "provider_branch": branch,
            "provider_token_configured": runtime._token_present(),
        }
    return repo, branch, None


def _claim_event_prepare(runtime: FrontierClaimRuntime, packet: dict, prepared: dict) -> dict:
    run_id = _safe_id(prepared["run_id"], "run_id")
    node_id = _safe_id(prepared["node_id"], "node_id")
    path = _claim_path(run_id, node_id)
    if prepared.get("claim_path") != path:
        return {"status": "CLAIM_EFFECT_UNJOURNALED_HOLD", "reason": "prepared claim path mismatch"}
    actual_claim = runtime.frontier._json(packet["source_head"], path)
    if not isinstance(actual_claim, dict):
        return {"status": "CLAIM_EFFECT_UNJOURNALED_HOLD", "reason": "created provider claim not observable after refresh"}
    claim_digest = _sha(actual_claim)
    if claim_digest != prepared.get("claim_digest"):
        return {
            "status": "CLAIM_JOURNAL_CONTRADICTION_HOLD",
            "reason": "observed provider claim digest differs from prepared claim",
            "claim_path": path,
        }
    events = runtime._events(packet, run_id)
    matching = [
        event
        for event in events
        if event.get("event_type") == "CLAIM_ACQUIRED"
        and event.get("node_id") == node_id
        and (event.get("data") or {}).get("claim_path") == path
    ]
    if len(matching) > 1:
        return {"status": "CLAIM_JOURNAL_CONTRADICTION_HOLD", "reason": "multiple claim events for one fixed claim path"}
    if len(matching) == 1:
        return {
            "status": "CLAIM_ALREADY_JOURNALED",
            "claim_path": path,
            "event_id": matching[0].get("event_id"),
            "sequence": matching[0].get("sequence"),
        }
    manifest = runtime._manifest(packet, run_id)
    projection = runtime.frontier._reduce_events(manifest, events)
    state = (projection.get("node_states") or {}).get(node_id)
    if state != "READY":
        return {
            "status": "CLAIM_EFFECT_UNJOURNALED_HOLD",
            "claim_path": path,
            "reducer_state": state,
            "reason": "provider claim exists but replay state cannot lawfully accept CLAIM_ACQUIRED",
        }
    sequence = len(events) + 1
    event = {
        "schema_version": "EVENT_V1",
        "event_id": f"claim-acquired-{claim_digest[:24]}",
        "sequence": sequence,
        "run_id": run_id,
        "event_type": "CLAIM_ACQUIRED",
        "at": actual_claim["claimed_at"],
        "node_id": node_id,
        "data": {
            "claim_path": path,
            "claim_digest": claim_digest,
            "attempt": int(actual_claim["attempt"]),
        },
    }
    after = runtime.frontier._reduce_events(manifest, [*events, event])
    if (after.get("node_states") or {}).get(node_id) != "CLAIMED":
        return {"status": "CLAIM_EFFECT_UNJOURNALED_HOLD", "reason": "CLAIM_ACQUIRED does not reduce to CLAIMED"}
    provider_packet = _provider_packet(_event_path(run_id, sequence), event, kind="EVENT_V1")
    return {
        "status": "CLAIM_EFFECT_CREATED_JOURNAL_PENDING",
        "run_id": run_id,
        "node_id": node_id,
        "claim_path": path,
        "claim_digest": claim_digest,
        "provider": provider_packet,
        "prepared_packet_digest": _sha(provider_packet),
    }


def _observe_claimed(runtime: FrontierClaimRuntime, arguments: dict, run_id: str, node_id: str) -> tuple[dict, dict]:
    packet = runtime.frontier.hydrate(**_common(arguments))
    state = _node_state(packet, run_id, node_id)
    return packet, {
        "source_head": packet.get("source_head"),
        "frontier_digest": packet.get("frontier_digest"),
        "reducer_state": state,
        "claim_visible": runtime._claim_exists(packet, run_id, node_id),
        "still_claimable": any(
            str(row.get("run_id")) == run_id and str(row.get("node_id")) == node_id
            for row in packet.get("claimable_work") or []
        ),
    }


def ready_execute(runtime: FrontierClaimRuntime, arguments: dict) -> dict:
    prepared = runtime.claim_prepare(
        expected_source_head=arguments["expected_source_head"],
        expected_frontier_digest=arguments["expected_frontier_digest"],
        expected_prompt_stack_digest=arguments["expected_prompt_stack_digest"],
        expected_claim_contract_digest=arguments["expected_claim_contract_digest"],
        run_id=arguments["run_id"],
        node_id=arguments["node_id"],
        operation_at=arguments["operation_at"],
        worker_role=arguments.get("worker_role"),
        lease_seconds=arguments.get("lease_seconds", 900),
        **_common(arguments),
    )
    if prepared.get("status") == "CLAIM_EFFECT_PREPARED":
        return {"status": "NODE_ALREADY_EVENT_READY", "run_id": prepared["run_id"], "node_id": prepared["node_id"]}
    if prepared.get("status") != "EVENT_READY_REQUIRED_HOLD":
        return prepared
    readiness = prepared["readiness_prerequisite"]
    repo, branch, provider_hold = _provider_context(runtime, arguments)
    if provider_hold:
        return provider_hold
    receipt = _provider(runtime).create(repo=repo, branch=branch, packet=readiness["provider"])
    if receipt.get("status") not in {"CREATED", "EXISTS"}:
        return {"status": "NODE_READY_PROVIDER_HOLD", "provider": receipt}
    packet = runtime.frontier.hydrate(**_common(arguments))
    state = _node_state(packet, readiness["run_id"], readiness["node_id"])
    if state != "READY":
        return {
            "status": "NODE_READY_SEQUENCE_RACE_HOLD" if receipt.get("status") == "EXISTS" else "NODE_READY_POSTCONDITION_HOLD",
            "provider": receipt,
            "reducer_state": state,
        }
    return {
        "status": "NODE_READY_JOURNALED",
        "run_id": readiness["run_id"],
        "node_id": readiness["node_id"],
        "provider": receipt,
        "post_source_head": packet.get("source_head"),
        "post_frontier_digest": packet.get("frontier_digest"),
    }


def claim_execute(runtime: FrontierClaimRuntime, arguments: dict) -> dict:
    prepared = runtime.claim_prepare(
        expected_source_head=arguments["expected_source_head"],
        expected_frontier_digest=arguments["expected_frontier_digest"],
        expected_prompt_stack_digest=arguments["expected_prompt_stack_digest"],
        expected_claim_contract_digest=arguments["expected_claim_contract_digest"],
        run_id=arguments["run_id"],
        node_id=arguments["node_id"],
        operation_at=arguments["operation_at"],
        worker_role=arguments.get("worker_role"),
        lease_seconds=arguments.get("lease_seconds", 900),
        **_common(arguments),
    )
    if prepared.get("status") != "CLAIM_EFFECT_PREPARED":
        return prepared
    repo, branch, provider_hold = _provider_context(runtime, arguments)
    if provider_hold:
        return provider_hold
    claim_receipt = _provider(runtime).create(repo=repo, branch=branch, packet=prepared["provider"])
    if claim_receipt.get("status") == "EXISTS":
        return {
            "status": "CLAIM_LOST_RACE",
            "run_id": prepared["run_id"],
            "node_id": prepared["node_id"],
            "claim_path": prepared["claim_path"],
            "provider": claim_receipt,
        }
    if claim_receipt.get("status") != "CREATED":
        return {"status": "CLAIM_PROVIDER_HOLD", "provider": claim_receipt}

    post_claim = runtime.frontier.hydrate(**_common(arguments))
    journal = _claim_event_prepare(runtime, post_claim, prepared)
    if journal.get("status") == "CLAIM_ALREADY_JOURNALED":
        _, observed = _observe_claimed(runtime, arguments, prepared["run_id"], prepared["node_id"])
        return {"status": "CLAIM_JOURNALED", "claim_provider": claim_receipt, "journal": journal, "observed": observed}
    if journal.get("status") != "CLAIM_EFFECT_CREATED_JOURNAL_PENDING":
        return {
            "status": journal.get("status", "CLAIM_EFFECT_UNJOURNALED_HOLD"),
            "claim_provider": claim_receipt,
            "journal": journal,
            "law": "claim provider effect is preserved; no fabricated rollback",
        }
    event_receipt = _provider(runtime).create(repo=repo, branch=branch, packet=journal["provider"])
    if event_receipt.get("status") == "EXISTS":
        _, observed = _observe_claimed(runtime, arguments, prepared["run_id"], prepared["node_id"])
        if observed["reducer_state"] == "CLAIMED" and observed["claim_visible"]:
            return {
                "status": "CLAIM_JOURNALED",
                "claim_provider": claim_receipt,
                "event_provider": event_receipt,
                "observed": observed,
                "law": "existing fixed event path counts only after fresh replay observes CLAIMED",
            }
        return {
            "status": "CLAIM_EFFECT_UNJOURNALED_HOLD",
            "claim_provider": claim_receipt,
            "event_provider": event_receipt,
            "observed": observed,
        }
    if event_receipt.get("status") != "CREATED":
        return {
            "status": "CLAIM_EFFECT_UNJOURNALED_HOLD",
            "claim_provider": claim_receipt,
            "event_provider": event_receipt,
            "law": "event failure does not erase the created claim",
        }
    _, observed = _observe_claimed(runtime, arguments, prepared["run_id"], prepared["node_id"])
    if observed["reducer_state"] != "CLAIMED" or not observed["claim_visible"] or observed["still_claimable"]:
        return {
            "status": "CLAIM_POSTCONDITION_HOLD",
            "claim_provider": claim_receipt,
            "event_provider": event_receipt,
            "observed": observed,
        }
    return {
        "status": "CLAIM_JOURNALED",
        "run_id": prepared["run_id"],
        "node_id": prepared["node_id"],
        "claim_path": prepared["claim_path"],
        "claim_provider": claim_receipt,
        "event_provider": event_receipt,
        "observed": observed,
    }


def reconcile_execute(runtime: FrontierClaimRuntime, arguments: dict) -> dict:
    hold, packet = _expected_hold(runtime, arguments)
    if hold:
        return hold
    run_id = _safe_id(arguments["run_id"], "run_id")
    node_id = _safe_id(arguments["node_id"], "node_id")
    path = _claim_path(run_id, node_id)
    claim = runtime.frontier._json(packet["source_head"], path)
    if not isinstance(claim, dict):
        return {"status": "CLAIM_RECONCILIATION_HOLD", "reason": "fixed provider claim path is absent", "claim_path": path}
    prepared = {
        "run_id": run_id,
        "node_id": node_id,
        "claim_path": path,
        "claim_digest": _sha(claim),
    }
    journal = _claim_event_prepare(runtime, packet, prepared)
    if journal.get("status") == "CLAIM_ALREADY_JOURNALED":
        _, observed = _observe_claimed(runtime, arguments, run_id, node_id)
        return {"status": "CLAIM_ALREADY_JOURNALED", "journal": journal, "observed": observed}
    if journal.get("status") != "CLAIM_EFFECT_CREATED_JOURNAL_PENDING":
        return journal
    repo, branch, provider_hold = _provider_context(runtime, arguments)
    if provider_hold:
        return provider_hold
    event_receipt = _provider(runtime).create(repo=repo, branch=branch, packet=journal["provider"])
    if event_receipt.get("status") not in {"CREATED", "EXISTS"}:
        return {"status": "CLAIM_EFFECT_UNJOURNALED_HOLD", "event_provider": event_receipt}
    _, observed = _observe_claimed(runtime, arguments, run_id, node_id)
    if observed["reducer_state"] != "CLAIMED" or not observed["claim_visible"]:
        return {"status": "CLAIM_EFFECT_UNJOURNALED_HOLD", "event_provider": event_receipt, "observed": observed}
    return {"status": "CLAIM_JOURNALED", "event_provider": event_receipt, "observed": observed}


def _execution_tool(name: str, description: str, *, operation_at: bool) -> dict:
    required = [
        "expected_source_head",
        "expected_frontier_digest",
        "expected_prompt_stack_digest",
        "expected_claim_contract_digest",
        "run_id",
        "node_id",
    ]
    properties: dict[str, Any] = {
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
    }
    if operation_at:
        required.append("operation_at")
        properties["operation_at"] = {
            "type": "string",
            "description": "Caller-generated ISO-8601 timestamp with timezone; preserve across retries.",
        }
    return {
        "name": name,
        "description": description,
        "inputSchema": {"type": "object", "required": required, "properties": properties, "additionalProperties": False},
    }


PROVIDER_EXECUTION_TOOLS = [
    _execution_tool(
        "athena_frontier_ready",
        "Persist only the reducer-validated fixed-sequence NODE_READY prerequisite for one dependency-ready PENDING node, then rehydrate and require explicit READY.",
        operation_at=True,
    ),
    _execution_tool(
        "athena_frontier_claim",
        "Execute the bounded fixed-path claim create-if-absent plus separate CLAIM_ACQUIRED event append only from fresh EVENT_READY state; preserve lost races and unjournaled effects.",
        operation_at=True,
    ),
    _execution_tool(
        "athena_frontier_claim_reconcile",
        "Observe an existing fixed-path provider claim and append only its missing CLAIM_ACQUIRED event when fresh replay remains READY; never create or delete the claim.",
        operation_at=False,
    ),
]
PROVIDER_EXECUTION_TOOL_NAMES = {tool["name"] for tool in PROVIDER_EXECUTION_TOOLS}


def install_frontier_claim_provider(runtime_cls=FrontierClaimRuntime, tools: list[dict] | None = None) -> None:
    if getattr(runtime_cls, "_athena_claim_provider_v2_registered", False):
        return
    tool_list = FRONTIER_CLAIM_TOOLS if tools is None else tools
    original_call = runtime_cls.call_tool

    def call_with_provider(self, name: str, arguments: dict) -> dict:
        if name == "athena_frontier_ready":
            return ready_execute(self, arguments)
        if name == "athena_frontier_claim":
            return claim_execute(self, arguments)
        if name == "athena_frontier_claim_reconcile":
            return reconcile_execute(self, arguments)
        return original_call(self, name, arguments)

    runtime_cls.call_tool = call_with_provider
    for tool in PROVIDER_EXECUTION_TOOLS:
        if not any(existing.get("name") == tool["name"] for existing in tool_list):
            tool_list.append(tool)
        FRONTIER_CLAIM_TOOL_NAMES.add(tool["name"])
    runtime_cls._athena_claim_provider_v2_registered = True
