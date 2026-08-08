from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib import error, parse, request

from .frontier_runtime import DEFAULT_SOURCE_REF, FRONTIER_TOOL_NAMES, FrontierRuntime
from .git_backend import GitBackend, GitStateError
from .prompt_runtime import PromptRuntime

ARTIFACT = "ATHENA.AGENT.BOOT.V1"
_ADDRESS_KEYS = (
    "git_head",
    "prompt_stack_digest",
    "frontier_source_head",
    "frontier_digest",
    "sched_contract_digest",
    "issue_pressure_digest",
)
_REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
_TOKEN_RE = re.compile(r"[A-Za-z0-9_]{3,}")
_STOP = {
    "the", "and", "for", "with", "from", "into", "over", "this", "that", "then",
    "agent", "athena", "current", "work", "task", "next", "one", "call", "git",
}


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


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


def _task_terms(task: str) -> set[str]:
    return {x for x in _TOKEN_RE.findall((task or "").lower()) if x not in _STOP}


class GitHubIssuePressureProvider:
    """Read-only GitHub issue-pressure sensor.

    Authentication is taken only from environment at request time and is never
    returned or persisted. Issue content can affect routing pressure, not scheduler
    readiness, evidence standing, or execution authority.
    """

    def __init__(self, git: GitBackend, *, opener=None, environ=None):
        self.git = git
        self._opener = opener or request.urlopen
        self._environ = environ if environ is not None else os.environ

    def _root(self) -> Path:
        if not self.git.enabled:
            raise GitStateError("ATHENA_GIT_ROOT is required for issue pressure")
        return self.git.root

    def _repo_from_remote(self, remote: str) -> str | None:
        try:
            raw = self.git._git("remote", "get-url", remote).strip()
        except Exception:
            return None
        if not raw:
            return None
        slug = None
        if raw.startswith("git@github.com:"):
            slug = raw.split(":", 1)[1]
        elif raw.startswith("ssh://git@github.com/"):
            slug = raw.split("ssh://git@github.com/", 1)[1]
        elif "github.com/" in raw:
            slug = raw.split("github.com/", 1)[1]
        if slug:
            slug = slug.removesuffix(".git").strip("/")
        return slug if slug and _REPO_RE.fullmatch(slug) else None

    def _resolve_repo(self, requested: str | None, remote: str) -> str:
        repo = requested or self._environ.get("ATHENA_ISSUE_REPO") or self._repo_from_remote(remote)
        if not repo or not _REPO_RE.fullmatch(repo):
            raise ValueError("issue repository is unavailable or invalid")
        return repo

    @staticmethod
    def _rank(issue: dict, terms: set[str]) -> int:
        title = str(issue.get("title") or "").lower()
        body = str(issue.get("body") or "").lower()
        labels = " ".join(
            str((x or {}).get("name") or "").lower()
            for x in issue.get("labels") or []
            if isinstance(x, dict)
        )
        score = 0
        for term in terms:
            if term in title:
                score += 5
            if term in labels:
                score += 3
            if term in body:
                score += 1
        if "p0" in title or "p0" in labels:
            score += 10
        if "blocking" in title or "incident" in title:
            score += 3
        return score

    @staticmethod
    def _normalize(issue: dict, score: int) -> dict:
        body = str(issue.get("body") or "")
        labels = sorted(
            str((x or {}).get("name") or "")
            for x in issue.get("labels") or []
            if isinstance(x, dict) and (x or {}).get("name")
        )
        return {
            "issue_number": int(issue.get("number") or 0),
            "title": str(issue.get("title") or ""),
            "body_digest": _sha(body),
            "labels": labels,
            "updated_at": issue.get("updated_at"),
            "state": issue.get("state"),
            "url": issue.get("html_url"),
            "routing_score": score,
            "standing": "PRESSURE_ONLY",
        }

    def snapshot(
        self,
        *,
        task: str,
        issue_repo: str | None = None,
        remote: str = "origin",
        limit: int = 10,
    ) -> dict:
        repo = self._resolve_repo(issue_repo, remote)
        limit = max(1, min(int(limit), 50))
        api_base = str(self._environ.get("ATHENA_GITHUB_API_URL") or "https://api.github.com").rstrip("/")
        owner, name = repo.split("/", 1)
        qs = parse.urlencode(
            {"state": "open", "per_page": 100, "sort": "updated", "direction": "desc"}
        )
        url = f"{api_base}/repos/{parse.quote(owner)}/{parse.quote(name)}/issues?{qs}"
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "athena-mcp-agent-bootstrap-v1",
        }
        token = (
            self._environ.get("ATHENA_GITHUB_TOKEN")
            or self._environ.get("GH_TOKEN")
            or self._environ.get("GITHUB_TOKEN")
        )
        if token:
            headers["Authorization"] = f"Bearer {token}"
        req = request.Request(url, headers=headers, method="GET")
        retrieved_at = _utcnow()
        try:
            with self._opener(req, timeout=15) as response:
                raw = response.read()
                etag = response.headers.get("ETag")
                status = getattr(response, "status", 200)
        except error.HTTPError as exc:
            return {
                "status": "ISSUE_PRESSURE_UNAVAILABLE_HOLD",
                "fresh": False,
                "repo": repo,
                "relevant": [],
                "digest": None,
                "witness": {
                    "provider": "github_api",
                    "repo": repo,
                    "retrieved_at": retrieved_at,
                    "http_status": int(getattr(exc, "code", 0) or 0),
                    "authenticated": bool(token),
                },
                "law": "ISSUE_PRESSURE != SCHED_READY",
            }
        except Exception as exc:
            return {
                "status": "ISSUE_PRESSURE_UNAVAILABLE_HOLD",
                "fresh": False,
                "repo": repo,
                "relevant": [],
                "digest": None,
                "witness": {
                    "provider": "github_api",
                    "repo": repo,
                    "retrieved_at": retrieved_at,
                    "error_type": type(exc).__name__,
                    "authenticated": bool(token),
                },
                "law": "ISSUE_PRESSURE != SCHED_READY",
            }

        try:
            rows = json.loads(raw.decode("utf-8"))
        except Exception:
            rows = None
        if not isinstance(rows, list):
            return {
                "status": "ISSUE_PRESSURE_INVALID_HOLD",
                "fresh": False,
                "repo": repo,
                "relevant": [],
                "digest": None,
                "witness": {
                    "provider": "github_api",
                    "repo": repo,
                    "retrieved_at": retrieved_at,
                    "http_status": int(status),
                    "authenticated": bool(token),
                },
                "law": "ISSUE_PRESSURE != SCHED_READY",
            }

        issues = [x for x in rows if isinstance(x, dict) and "pull_request" not in x]
        terms = _task_terms(task)
        ranked = [(self._rank(x, terms), x) for x in issues]
        ranked.sort(
            key=lambda pair: (
                -pair[0],
                str(pair[1].get("updated_at") or ""),
                -int(pair[1].get("number") or 0),
            ),
            reverse=False,
        )
        selected_pairs = [pair for pair in ranked if pair[0] > 0]
        if not selected_pairs:
            selected_pairs = ranked
        relevant = [self._normalize(issue, score) for score, issue in selected_pairs[:limit]]
        digest_basis = {
            "repo": repo,
            "task_terms": sorted(terms),
            "relevant": relevant,
        }
        return {
            "status": "FRESH",
            "fresh": True,
            "repo": repo,
            "relevant": relevant,
            "digest": _sha(digest_basis),
            "witness": {
                "provider": "github_api",
                "repo": repo,
                "retrieved_at": retrieved_at,
                "http_status": int(status),
                "etag": etag,
                "authenticated": bool(token),
            },
            "laws": [
                "ISSUE_PRESSURE != SCHED_READY",
                "ISSUE_BODY != EXECUTABLE_STATE",
                "ISSUE_PRIORITY != EXECUTION_AUTHORIZATION",
            ],
        }


class AgentBootstrapRuntime:
    """Composite cold-start and refresh surface over independent ATHENA coordinates."""

    def __init__(
        self,
        git: GitBackend,
        prompt_runtime: PromptRuntime | None = None,
        frontier_runtime: FrontierRuntime | None = None,
        issue_provider: GitHubIssuePressureProvider | Any | None = None,
    ):
        self.git = git
        self.prompt_runtime = prompt_runtime or PromptRuntime(git)
        self.frontier_runtime = frontier_runtime or FrontierRuntime(git, self.prompt_runtime)
        self.issue_provider = issue_provider or GitHubIssuePressureProvider(git)
        self._sessions: dict[str, dict] = {}

    @property
    def available(self) -> bool:
        return bool(self.git.enabled and self.prompt_runtime.available)

    def _recent_deltas(self, limit: int = 8) -> list[dict]:
        try:
            out = self.git._git(
                "log",
                "-n",
                str(max(1, min(int(limit), 25))),
                "--format=%H%x1f%ct%x1f%s",
            )
        except Exception:
            return []
        rows = []
        for line in out.splitlines():
            parts = line.split("\x1f", 2)
            if len(parts) != 3:
                continue
            sha, ts, subject = parts
            rows.append({"sha": sha, "committed_unix": int(ts), "subject": subject})
        return rows

    @staticmethod
    def _contract_digest(frontier: dict) -> str | None:
        contract = frontier.get("sched_contract")
        return _sha(contract) if isinstance(contract, dict) else None

    @staticmethod
    def _address(packet: dict) -> dict:
        return {
            "git_head": packet["prompt"]["git_head"],
            "prompt_stack_digest": packet["prompt"]["prompt_stack_digest"],
            "frontier_source_head": packet["frontier"].get("source_head"),
            "frontier_digest": packet["frontier"].get("frontier_digest"),
            "sched_contract_digest": packet.get("contract_digest"),
            "issue_pressure_digest": packet["issue_pressure"].get("digest"),
        }

    @staticmethod
    def _changed(prior: dict, current: dict) -> dict:
        return {key: prior.get(key) != current.get(key) for key in _ADDRESS_KEYS}

    def bootstrap(
        self,
        *,
        agent_id: str,
        task: str,
        profile: str | None = None,
        source_ref: str = DEFAULT_SOURCE_REF,
        remote: str = "origin",
        fetch: bool = True,
        issue_repo: str | None = None,
        issue_limit: int = 10,
    ) -> dict:
        if not agent_id or not isinstance(agent_id, str):
            raise ValueError("agent_id is required")
        compiled = self.prompt_runtime.compile(task=task, profile=profile, include_text=False)
        frontier = self.frontier_runtime.hydrate(
            task=task,
            profile=profile,
            source_ref=source_ref,
            remote=remote,
            fetch=fetch,
        )
        selection = self.frontier_runtime.select(
            task=task,
            profile=profile,
            source_ref=source_ref,
            remote=remote,
            fetch=fetch,
        )
        issue_pressure = self.issue_provider.snapshot(
            task=task,
            issue_repo=issue_repo,
            remote=remote,
            limit=issue_limit,
        )
        contract_digest = self._contract_digest(frontier)
        session_id = str(uuid.uuid4())
        prompt_packet = {
            "profile": compiled.get("profile"),
            "modules": compiled.get("selected_modules") or [],
            "overlays": compiled.get("selected_overlays") or [],
            "git_head": compiled.get("git_head"),
            "prompt_stack_digest": compiled.get("prompt_stack_digest"),
            "ancestry": compiled.get("ancestry"),
        }
        frontier_packet = {
            "status": frontier.get("status"),
            "source_head": frontier.get("source_head"),
            "frontier_digest": frontier.get("frontier_digest"),
            "ready_work": frontier.get("ready_work") or [],
            "claims": frontier.get("claims") or [],
            "claim_readiness_suppressed": frontier.get("claim_readiness_suppressed") or [],
            "residuals": frontier.get("residuals") or [],
            "coverage": frontier.get("source_coverage"),
        }
        execution = {
            "frontier_tools": sorted(FRONTIER_TOOL_NAMES),
            "claim_tool_exposed": "athena_frontier_claim" in FRONTIER_TOOL_NAMES,
            "standing": "OBSERVED_TOOL_SURFACE",
            "law": "ISSUE_OR_DESIGN_ASSERTION != EXPOSED_EXECUTION_TOOL",
        }
        holds = []
        if frontier.get("status") != "HYDRATED":
            holds.append(frontier.get("status") or "FRONTIER_HOLD")
        if not issue_pressure.get("fresh"):
            holds.append(issue_pressure.get("status") or "ISSUE_PRESSURE_HOLD")
        if (frontier.get("sched_contract") or {}).get("status") != "PASS":
            holds.append((frontier.get("sched_contract") or {}).get("status") or "SCHED_CONTRACT_HOLD")
        packet = {
            "artifact": ARTIFACT,
            "status": "BOOTSTRAP_HOLD" if holds else "BOOTSTRAPPED",
            "agent_id": agent_id,
            "session_id": session_id,
            "task": task,
            "prompt": prompt_packet,
            "frontier": frontier_packet,
            "issue_pressure": issue_pressure,
            "siblings": {
                "active_claims": frontier.get("claims") or [],
                "claim_event_lag": frontier.get("claim_readiness_suppressed") or [],
                "recent_durable_deltas": self._recent_deltas(),
            },
            "execution_surface": execution,
            "contract_digest": contract_digest,
            "witnesses": {
                "git_head": compiled.get("git_head"),
                "frontier_remote": {
                    "source_ref": frontier.get("source_ref"),
                    "resolved_ref": frontier.get("resolved_ref"),
                    "source_head": frontier.get("source_head"),
                    "remote_checked": frontier.get("remote_checked"),
                    "fetch_error": frontier.get("fetch_error"),
                },
                "issue_api": issue_pressure.get("witness"),
            },
            "next_frontier": {
                "status": selection.get("status"),
                "selected": selection.get("selected"),
                "pareto_front": selection.get("pareto_front") or [],
            },
            "holds": sorted(set(str(x) for x in holds if x)),
            "return_contract": {
                "refresh_before_consequential_action": True,
                "issue_pressure_is_read_only": True,
                "persist_private_chain_of_thought": False,
            },
            "laws": [
                "BOOT_PACKET != HIGHER_AUTHORITY",
                "ISSUE_PRESSURE != EVIDENCE",
                "ISSUE_BODY != EXECUTION",
                "SESSION_DIGEST != CANONICAL_TRUTH",
                "SIBLING_TELEMETRY != PRIVATE_REASONING",
                "ONE_CALL_BOOT != SKIP_FRESHNESS",
            ],
        }
        address = self._address(packet)
        packet["address"] = address
        packet["composite_digest"] = _sha(address)
        self._sessions[session_id] = {
            "address": dict(address),
            "agent_id": agent_id,
            "task": task,
            "profile": profile,
            "source_ref": source_ref,
            "remote": remote,
            "fetch": fetch,
            "issue_repo": issue_pressure.get("repo") or issue_repo,
            "issue_limit": issue_limit,
        }
        return packet

    def refresh(
        self,
        *,
        session_id: str | None = None,
        prior_address: dict | None = None,
        agent_id: str | None = None,
        task: str | None = None,
        profile: str | None = None,
        source_ref: str | None = None,
        remote: str | None = None,
        fetch: bool | None = None,
        issue_repo: str | None = None,
        issue_limit: int | None = None,
    ) -> dict:
        remembered = self._sessions.get(session_id or "") if session_id else None
        if prior_address is None and remembered is not None:
            prior_address = remembered.get("address")
        if prior_address is None:
            return {
                "artifact": ARTIFACT,
                "status": "SESSION_NOT_FOUND_HOLD",
                "session_id": session_id,
                "requires_prior_address": True,
                "law": "MISSING_SESSION_MEMORY != PRIOR_OBSERVED_STATE",
            }
        if not isinstance(prior_address, dict):
            raise ValueError("prior_address must be an object")
        if remembered:
            agent_id = agent_id or remembered.get("agent_id")
            task = task if task is not None else remembered.get("task")
            profile = profile if profile is not None else remembered.get("profile")
            source_ref = source_ref or remembered.get("source_ref")
            remote = remote or remembered.get("remote")
            if fetch is None:
                fetch = remembered.get("fetch")
            issue_repo = issue_repo or remembered.get("issue_repo")
            issue_limit = issue_limit or remembered.get("issue_limit")
        if not agent_id:
            raise ValueError("agent_id is required when session state is unavailable")
        packet = self.bootstrap(
            agent_id=agent_id,
            task=task or "",
            profile=profile,
            source_ref=source_ref or DEFAULT_SOURCE_REF,
            remote=remote or "origin",
            fetch=True if fetch is None else bool(fetch),
            issue_repo=issue_repo,
            issue_limit=issue_limit or 10,
        )
        current_address = packet["address"]
        changed = self._changed(prior_address, current_address)
        affected = []
        if changed["git_head"] or changed["prompt_stack_digest"]:
            affected.append("prompt_policy")
        if (
            changed["frontier_source_head"]
            or changed["frontier_digest"]
            or changed["sched_contract_digest"]
        ):
            affected.append("scheduler_frontier")
        if changed["issue_pressure_digest"]:
            affected.append("issue_pressure_routing")
        packet["refresh"] = {
            "prior_address": prior_address,
            "changed": changed,
            "changed_coordinates": [key for key, value in changed.items() if value],
            "affected_dependency_cone": affected,
            "requires_replan": any(changed.values()),
            "law": "REFRESH_CHANGED_COORDINATES_ONLY; UNCHANGED_COORDINATES_REMAIN_INDEPENDENT",
        }
        return packet

    def call_tool(self, name: str, a: dict) -> dict:
        if name == "athena_agent_bootstrap":
            return self.bootstrap(
                agent_id=a["agent_id"],
                task=a.get("task", ""),
                profile=a.get("profile"),
                source_ref=a.get("source_ref", DEFAULT_SOURCE_REF),
                remote=a.get("remote", "origin"),
                fetch=a.get("fetch", True),
                issue_repo=a.get("issue_repo"),
                issue_limit=a.get("issue_limit", 10),
            )
        if name == "athena_agent_refresh":
            return self.refresh(
                session_id=a.get("session_id"),
                prior_address=a.get("prior_address"),
                agent_id=a.get("agent_id"),
                task=a.get("task"),
                profile=a.get("profile"),
                source_ref=a.get("source_ref"),
                remote=a.get("remote"),
                fetch=a.get("fetch"),
                issue_repo=a.get("issue_repo"),
                issue_limit=a.get("issue_limit"),
            )
        raise KeyError(name)


AGENT_BOOT_TOOLS = [
    {
        "name": "athena_agent_bootstrap",
        "description": "Cold-start one AGENT_BOOT_V1 packet from current prompt policy, executable SCHED frontier, fresh read-only GitHub issue pressure, sibling activity, and exact independent freshness coordinates.",
        "inputSchema": {
            "type": "object",
            "required": ["agent_id"],
            "properties": {
                "agent_id": {"type": "string"},
                "task": {"type": "string"},
                "profile": {"type": ["string", "null"]},
                "source_ref": {"type": "string"},
                "remote": {"type": "string"},
                "fetch": {"type": "boolean"},
                "issue_repo": {"type": ["string", "null"]},
                "issue_limit": {"type": "integer", "minimum": 1, "maximum": 50},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_agent_refresh",
        "description": "Rebuild AGENT_BOOT_V1 and report exactly which independent prompt/frontier/contract/issue-pressure coordinates changed since a prior address or live in-process session.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "session_id": {"type": ["string", "null"]},
                "prior_address": {"type": ["object", "null"]},
                "agent_id": {"type": ["string", "null"]},
                "task": {"type": ["string", "null"]},
                "profile": {"type": ["string", "null"]},
                "source_ref": {"type": ["string", "null"]},
                "remote": {"type": ["string", "null"]},
                "fetch": {"type": ["boolean", "null"]},
                "issue_repo": {"type": ["string", "null"]},
                "issue_limit": {"type": ["integer", "null"], "minimum": 1, "maximum": 50},
            },
            "additionalProperties": False,
        },
    },
]
AGENT_BOOT_TOOL_NAMES = {x["name"] for x in AGENT_BOOT_TOOLS}
