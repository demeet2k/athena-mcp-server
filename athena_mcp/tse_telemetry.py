from __future__ import annotations

import hashlib
import json
import math
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping

from .git_backend import GitBackend, GitStateError, GitStaleHead
from .prompt_remote import PromptRemoteSync

TELEMETRY_VERSION = "TSE.HELICAL.HANDOFF.TELEMETRY.2"
TELEMETRY_ARTIFACT = "ATHENA.TSE.HELIX.EVENT.V2"
LEGACY_TELEMETRY_ARTIFACT = "ATHENA.TSE.HELIX.EVENT.V1"
TELEMETRY_ROOT = "runtime/tse_population/v1/telemetry"
EVENT_ROOT = f"{TELEMETRY_ROOT}/events"
RESOURCE_URI = "athena://tse-telemetry/v1"

SOURCE_BOUND = "SOURCE_BOUND"
DECLARED_ONLY = "DECLARED_ONLY"

SUCCESS_TRANSITIONS = (
    "HATCH_CREATED",
    "HATCH_NEED_PUBLISHED",
    "MATCH_FOUND",
    "HANDOFF_ROUTED",
    "HANDOFF_CONSUMED",
    "CHILD_CLAIMED",
    "CHILD_VERIFIED_RETURN",
    "RETURN_APPLIED",
)
HOLD_TRANSITION = "HELIX_HOLD"
HOLD_CLASSES = {
    "CAPABILITY_HOLD",
    "STALE_STATE_HOLD",
    "DUPLICATION_COLLAPSE",
    "ROUTED_NOT_CONSUMED",
    "ACKED_NOT_CLAIMED",
    "AUTHORITY_HOLD",
    "EVIDENCE_HOLD",
    "NO_POSITIVE_HATCH",
}
PARENT_RULES = {
    "HATCH_CREATED": set(),
    "HATCH_NEED_PUBLISHED": {"HATCH_CREATED"},
    "MATCH_FOUND": {"HATCH_NEED_PUBLISHED"},
    "HANDOFF_ROUTED": {"MATCH_FOUND"},
    "HANDOFF_CONSUMED": {"HANDOFF_ROUTED"},
    "CHILD_CLAIMED": {"HANDOFF_ROUTED", "HANDOFF_CONSUMED"},
    "CHILD_VERIFIED_RETURN": {"CHILD_CLAIMED"},
    "RETURN_APPLIED": {"CHILD_VERIFIED_RETURN"},
}
_ID_RE = re.compile(r"^[A-Za-z0-9_.:-]{1,192}$")
_PRIVATE_KEYS = {"chain_of_thought", "private_chain_of_thought", "hidden_reasoning", "scratchpad"}
_RESET_TOKENS = {"token", "context", "quota", "usage", "platform", "counter", "runtime", "provider", "model"}


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _iso() -> str:
    return _utcnow().isoformat()


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _json_text(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _require_id(value: Any, field: str) -> str:
    text = str(value or "").strip()
    if not _ID_RE.fullmatch(text):
        raise ValueError(f"invalid {field}")
    return text


def _finite_nonnegative(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
        and float(value) >= 0
    )


def _walk_items(value: Any):
    if isinstance(value, Mapping):
        for key, item in value.items():
            yield str(key), item
            yield from _walk_items(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_items(item)


def _public_errors(value: Any) -> list[str]:
    errors = []
    for key, item in _walk_items(value):
        normalized = key.lower().replace("-", "_")
        if normalized in _PRIVATE_KEYS:
            errors.append(f"forbidden_private_key:{key}")
        if normalized == "platform_counter_reset_claimed":
            if item not in (None, False):
                errors.append("platform_counter_reset_claimed_must_be_false")
            continue
        if "reset" in normalized and any(token in normalized for token in _RESET_TOKENS):
            errors.append(f"forbidden_reset_key:{key}")
    return sorted(set(errors))


def _cost_errors(cost: Any) -> list[str]:
    if not isinstance(cost, Mapping):
        return ["cost_not_mapping"]
    known = cost.get("known")
    if not isinstance(known, bool):
        return ["cost_known_boolean_required"]
    if known:
        if not _finite_nonnegative(cost.get("total")):
            return ["known_cost_total_required"]
    elif "total" in cost and cost.get("total") not in (None, "UNKNOWN"):
        return ["unknown_cost_must_not_supply_numeric_total"]
    return []


def _ratio(numerator: int, denominator: int):
    if denominator <= 0:
        return "UNKNOWN"
    return numerator / denominator


def _source_packet(
    verification: str,
    *,
    kind: str,
    ref: str,
    digest: str | None,
    git_head: str | None,
    authority: str,
) -> dict:
    return {
        "verification": verification,
        "kind": str(kind or "").strip(),
        "ref": str(ref or "").strip(),
        "digest": digest,
        "git_head": str(git_head or "").strip() or None,
        "authority": str(authority or "").strip(),
    }


def _source_errors(source: Any) -> list[str]:
    if not isinstance(source, Mapping):
        return ["source_not_mapping"]
    errors = []
    if source.get("verification") not in {SOURCE_BOUND, DECLARED_ONLY}:
        errors.append("source_verification")
    for key in ("kind", "ref", "authority"):
        if not str(source.get(key) or "").strip():
            errors.append(f"source_{key}")
    digest = source.get("digest")
    if source.get("verification") == SOURCE_BOUND:
        if not isinstance(digest, str) or not digest.startswith("sha256:") or len(digest) != 71:
            errors.append("source_digest")
    elif digest is not None and (not isinstance(digest, str) or not digest.startswith("sha256:")):
        errors.append("source_digest")
    errors += _public_errors(source)
    return sorted(set(errors))


class TseHelixTelemetryRuntime:
    """Git-backed public telemetry for the TSE Helical Handoff.

    The ledger is observation-only. Low-level caller-declared observations are
    retained for audit, but primary conversion metrics count only SOURCE_BOUND
    events emitted by adapters that re-derive the transition from actual public
    TSE/Cohesion/Message-Board state.
    """

    def __init__(self, server):
        self.server = server
        self.git: GitBackend = server.git
        self.remote_sync = PromptRemoteSync(self.git)

    def _root(self) -> Path:
        if not self.git.enabled:
            raise GitStateError("ATHENA_GIT_ROOT is required for TSE telemetry")
        return self.git.root

    def _event_path(self, event_id: str) -> str:
        return f"{EVENT_ROOT}/{_require_id(event_id, 'event_id')}.json"

    def _read_json(self, path: Path) -> dict | None:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        return value if isinstance(value, dict) else None

    def _events(self) -> list[dict]:
        root = self._root() / EVENT_ROOT
        if not root.exists():
            return []
        out = []
        for path in sorted(root.glob("*.json")):
            value = self._read_json(path)
            if value and value.get("artifact") in {TELEMETRY_ARTIFACT, LEGACY_TELEMETRY_ARTIFACT}:
                out.append(value)
        return sorted(out, key=lambda row: (str(row.get("created_at")), str(row.get("event_id"))))

    def _sync(self, remote: str, mode: str = "REQUIRED") -> dict:
        mode = str(mode or "REQUIRED").upper()
        if mode not in {"REQUIRED", "BEST_EFFORT", "DISABLED"}:
            raise ValueError("shared_remote_mode must be REQUIRED, BEST_EFFORT, or DISABLED")
        if mode == "DISABLED":
            return {"status": "DISABLED", "remote": remote, "shared_frontier_verified": False}
        state = self.remote_sync.sync(remote)
        if mode == "REQUIRED" and not state.get("shared_frontier_verified"):
            return {
                **state,
                "status": "TSE_TELEMETRY_SHARED_FRONTIER_HOLD",
                "shared_frontier_verified": False,
            }
        return state

    def _commit_files(self, expected_head: str, files: Dict[str, str], actor: str, message: str) -> dict:
        current = self.git.head()
        if current != expected_head:
            raise GitStaleHead(
                json.dumps({"status": "STALE_GIT_HEAD", "expected": expected_head, "current": current})
            )
        if self.git._git("status", "--porcelain"):
            raise GitStateError("DIRTY_GIT_ROOT: TSE telemetry refuses unrelated working-tree state")
        actor = _require_id(actor, "actor_id")
        rels = sorted(files)
        for rel in rels:
            if not rel.startswith(TELEMETRY_ROOT + "/"):
                raise ValueError("TSE telemetry may only write under runtime/tse_population/v1/telemetry/")
        try:
            for rel, text in files.items():
                path = self._root() / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
            self.git._git("add", "--", *rels)
            staged = self.git._git("diff", "--cached", "--name-only")
            if not staged:
                return {"status": "NO_CHANGES", "head": current, "previous_head": current, "paths": rels}
            env = os.environ.copy()
            env.setdefault("GIT_AUTHOR_NAME", actor)
            env.setdefault("GIT_AUTHOR_EMAIL", "athena@local")
            env.setdefault("GIT_COMMITTER_NAME", actor)
            env.setdefault("GIT_COMMITTER_EMAIL", "athena@local")
            proc = subprocess.run(
                ["git", "-C", str(self._root()), "commit", "-m", message],
                text=True,
                capture_output=True,
                env=env,
            )
            if proc.returncode:
                raise GitStateError(proc.stderr.strip() or proc.stdout.strip())
        except Exception:
            self.git._git("reset", "--hard", current)
            raise
        return {"status": "COMMITTED_LOCAL", "head": self.git.head(), "previous_head": current, "paths": rels}

    def _safe_race_reset(self, base_head: str, created_head: str, remote_head: str | None) -> bool:
        if not remote_head or self.git.head() != created_head or self.git._git("status", "--porcelain"):
            return False
        try:
            parent = self.git._git("rev-parse", f"{created_head}^")
            changed = self.git._git("diff", "--name-only", f"{base_head}..{created_head}").splitlines()
            ancestor = (
                subprocess.run(
                    ["git", "-C", str(self._root()), "merge-base", "--is-ancestor", base_head, remote_head],
                    text=True,
                    capture_output=True,
                ).returncode
                == 0
            )
        except GitStateError:
            return False
        if parent != base_head or not ancestor:
            return False
        if any(not str(path).startswith(TELEMETRY_ROOT + "/") for path in changed if path.strip()):
            return False
        self.git._git("reset", "--hard", base_head)
        return True

    def _mutate(self, *, actor_id: str, remote: str, build_files, max_retries: int = 3) -> dict:
        actor_id = _require_id(actor_id, "actor_id")
        for attempt in range(1, max_retries + 1):
            sync = self._sync(remote, "REQUIRED")
            if not sync.get("shared_frontier_verified"):
                return {
                    "status": "TSE_TELEMETRY_SHARED_FRONTIER_HOLD",
                    "remote_sync": sync,
                    "durable_return": False,
                }
            base = self.git.head()
            plan = build_files(base)
            if plan.get("return") is not None:
                value = dict(plan["return"])
                value.setdefault("git_head", base)
                value.setdefault("remote_sync", sync)
                value.setdefault("durable_return", True)
                return value
            commit = self._commit_files(base, plan["files"], actor_id, plan["message"])
            if commit["status"] == "NO_CHANGES":
                return {
                    **dict(plan.get("result") or {}),
                    "git": commit,
                    "remote_sync": sync,
                    "durable_return": True,
                }
            published = self.remote_sync.publish(commit["head"], remote)
            if published.get("shared_frontier_verified"):
                return {
                    **dict(plan.get("result") or {}),
                    "git": commit,
                    "remote_publish": published,
                    "durable_return": True,
                    "attempt": attempt,
                }
            if (
                published.get("status") == "PUBLISH_HOLD_DIVERGED_HOLD"
                and self._safe_race_reset(base, commit["head"], published.get("remote_head"))
            ):
                continue
            return {
                **dict(plan.get("result") or {}),
                "status": "TSE_TELEMETRY_LOCAL_MUTATION_PUBLISH_HOLD",
                "git": commit,
                "remote_publish": published,
                "durable_return": False,
                "attempt": attempt,
            }
        return {"status": "TSE_TELEMETRY_RACE_HOLD", "durable_return": False, "attempts": max_retries}

    @staticmethod
    def _event_id(mission_id: str, route_id: str, transition: str, attempt_ref: str | None) -> str:
        basis = {
            "mission_id": mission_id,
            "route_id": route_id,
            "transition": transition,
            "attempt_ref": attempt_ref or None,
        }
        return "TSETELEM-" + _digest(basis).split(":", 1)[1][:32]

    @staticmethod
    def _semantic_basis(
        *,
        mission_id: str,
        route_id: str,
        hatch_id: str,
        transition: str,
        parent_event_id: str | None,
        actor_id: str,
        child_agent_id: str | None,
        child_claim_id: str | None,
        witnesses: Iterable[str],
        cost: Mapping[str, Any],
        verified_delta: float | None,
        hold_class: str | None,
        seam: str | None,
        attempt_ref: str | None,
        source: Mapping[str, Any],
    ) -> dict:
        return {
            "mission_id": mission_id,
            "route_id": route_id,
            "hatch_id": hatch_id,
            "transition": transition,
            "parent_event_id": parent_event_id,
            "actor_id": actor_id,
            "child_agent_id": child_agent_id,
            "child_claim_id": child_claim_id,
            "witnesses": sorted({str(value) for value in witnesses if str(value)}),
            "cost": dict(cost),
            "verified_delta": verified_delta,
            "hold_class": hold_class,
            "seam": seam,
            "attempt_ref": attempt_ref,
            "source": dict(source),
        }

    def _record(
        self,
        *,
        mission_id: str,
        route_id: str,
        hatch_id: str,
        transition: str,
        actor_id: str,
        witnesses: Iterable[str],
        cost: Mapping[str, Any],
        source: Mapping[str, Any],
        parent_event_id: str | None = None,
        child_agent_id: str | None = None,
        child_claim_id: str | None = None,
        verified_delta: float | None = None,
        hold_class: str | None = None,
        seam: str | None = None,
        attempt_ref: str | None = None,
        remote: str = "origin",
    ) -> dict:
        try:
            mission_id = _require_id(mission_id, "mission_id")
            route_id = _require_id(route_id, "route_id")
            hatch_id = _require_id(hatch_id, "hatch_id")
            actor_id = _require_id(actor_id, "actor_id")
            if parent_event_id is not None:
                parent_event_id = _require_id(parent_event_id, "parent_event_id")
            if child_agent_id is not None:
                child_agent_id = _require_id(child_agent_id, "child_agent_id")
            if child_claim_id is not None:
                child_claim_id = _require_id(child_claim_id, "child_claim_id")
            if attempt_ref is not None:
                attempt_ref = _require_id(attempt_ref, "attempt_ref")
        except ValueError as exc:
            return {"status": "TSE_TELEMETRY_RECORD_HOLD", "hold": "EVIDENCE_HOLD", "errors": [str(exc)]}

        transition = str(transition or "").upper()
        witness_list = sorted({str(value).strip() for value in witnesses if str(value).strip()})
        errors = _cost_errors(cost) + _source_errors(source)
        if transition not in set(SUCCESS_TRANSITIONS) | {HOLD_TRANSITION}:
            errors.append("unknown_transition")
        if not witness_list:
            errors.append("witnesses_required")
        if transition in {"CHILD_CLAIMED", "CHILD_VERIFIED_RETURN", "RETURN_APPLIED"}:
            if not child_agent_id or not child_claim_id:
                errors.append("child_agent_and_claim_required")
        if transition in {"CHILD_VERIFIED_RETURN", "RETURN_APPLIED"}:
            if not _finite_nonnegative(verified_delta) or float(verified_delta) <= 0:
                errors.append("positive_verified_delta_required")
        elif verified_delta not in (None, 0, 0.0):
            errors.append("verified_delta_only_for_return_transitions")
        if transition == HOLD_TRANSITION:
            if hold_class not in HOLD_CLASSES:
                errors.append("hold_class")
            if not seam:
                errors.append("hold_seam_required")
            if not attempt_ref:
                errors.append("hold_attempt_ref_required")
        elif hold_class is not None or seam is not None:
            errors.append("hold_fields_only_for_helix_hold")

        basis = self._semantic_basis(
            mission_id=mission_id,
            route_id=route_id,
            hatch_id=hatch_id,
            transition=transition,
            parent_event_id=parent_event_id,
            actor_id=actor_id,
            child_agent_id=child_agent_id,
            child_claim_id=child_claim_id,
            witnesses=witness_list,
            cost=cost,
            verified_delta=float(verified_delta) if verified_delta is not None else None,
            hold_class=hold_class,
            seam=str(seam) if seam else None,
            attempt_ref=attempt_ref,
            source=source,
        )
        errors += _public_errors(basis)
        if errors:
            return {
                "status": "TSE_TELEMETRY_RECORD_HOLD",
                "hold": "EVIDENCE_HOLD",
                "errors": sorted(set(errors)),
            }

        event_id = self._event_id(mission_id, route_id, transition, attempt_ref)
        semantic_digest = _digest(basis)
        path = self._event_path(event_id)
        source_bound = source.get("verification") == SOURCE_BOUND

        def build(base_head: str):
            existing = self._read_json(self._root() / path)
            if existing:
                if existing.get("semantic_digest") == semantic_digest:
                    return {
                        "return": {
                            "status": "TSE_TELEMETRY_ALREADY_RECORDED",
                            "event": existing,
                            "source_bound": bool(
                                (existing.get("source") or {}).get("verification") == SOURCE_BOUND
                            ),
                        }
                    }
                return {
                    "return": {
                        "status": "TSE_TELEMETRY_EVENT_CONFLICT_HOLD",
                        "hold": "EVIDENCE_HOLD",
                        "event_id": event_id,
                        "existing_semantic_digest": existing.get("semantic_digest"),
                        "requested_semantic_digest": semantic_digest,
                    }
                }

            events = {str(row.get("event_id")): row for row in self._events()}
            if transition in SUCCESS_TRANSITIONS:
                allowed = PARENT_RULES[transition]
                if not allowed:
                    if parent_event_id is not None:
                        return {
                            "return": {
                                "status": "TSE_TELEMETRY_PARENT_HOLD",
                                "hold": "EVIDENCE_HOLD",
                                "reason": "root_transition_must_not_have_parent",
                            }
                        }
                else:
                    parent = events.get(str(parent_event_id or ""))
                    if not parent:
                        return {
                            "return": {
                                "status": "TSE_TELEMETRY_PARENT_HOLD",
                                "hold": "EVIDENCE_HOLD",
                                "reason": "parent_event_missing",
                            }
                        }
                    if parent.get("transition") not in allowed:
                        return {
                            "return": {
                                "status": "TSE_TELEMETRY_PARENT_HOLD",
                                "hold": "EVIDENCE_HOLD",
                                "reason": "parent_transition_invalid",
                            }
                        }
                    if (
                        parent.get("mission_id") != mission_id
                        or parent.get("route_id") != route_id
                        or parent.get("hatch_id") != hatch_id
                    ):
                        return {
                            "return": {
                                "status": "TSE_TELEMETRY_PARENT_HOLD",
                                "hold": "EVIDENCE_HOLD",
                                "reason": "parent_lineage_mismatch",
                            }
                        }
                    if source_bound and (parent.get("source") or {}).get("verification") != SOURCE_BOUND:
                        return {
                            "return": {
                                "status": "TSE_TELEMETRY_PARENT_HOLD",
                                "hold": "EVIDENCE_HOLD",
                                "reason": "source_bound_child_requires_source_bound_parent",
                            }
                        }
            elif parent_event_id:
                parent = events.get(parent_event_id)
                if not parent:
                    return {
                        "return": {
                            "status": "TSE_TELEMETRY_PARENT_HOLD",
                            "hold": "EVIDENCE_HOLD",
                            "reason": "hold_parent_missing",
                        }
                    }
                if (
                    parent.get("mission_id") != mission_id
                    or parent.get("route_id") != route_id
                    or parent.get("hatch_id") != hatch_id
                ):
                    return {
                        "return": {
                            "status": "TSE_TELEMETRY_PARENT_HOLD",
                            "hold": "EVIDENCE_HOLD",
                            "reason": "hold_parent_lineage_mismatch",
                        }
                    }
                if source_bound and (parent.get("source") or {}).get("verification") != SOURCE_BOUND:
                    return {
                        "return": {
                            "status": "TSE_TELEMETRY_PARENT_HOLD",
                            "hold": "EVIDENCE_HOLD",
                            "reason": "source_bound_hold_requires_source_bound_parent",
                        }
                    }

            event = {
                "artifact": TELEMETRY_ARTIFACT,
                "version": TELEMETRY_VERSION,
                "event_id": event_id,
                **basis,
                "semantic_digest": semantic_digest,
                "created_at": _iso(),
                "git_parent": base_head,
                "shared_frontier_verified": True,
                "authority": "OBSERVATION_ONLY",
                "behavioral_treatment_effect": "UNKNOWN",
            }
            return {
                "files": {path: _json_text(event)},
                "message": f"Record TSE helix {transition} {event_id}",
                "result": {
                    "status": (
                        "TSE_TELEMETRY_RECORDED_SOURCE_BOUND"
                        if source_bound
                        else "TSE_TELEMETRY_RECORDED_DECLARED"
                    ),
                    "event": event,
                    "source_bound": source_bound,
                },
            }

        return self._mutate(actor_id=actor_id, remote=remote, build_files=build)

    def record(
        self,
        *,
        mission_id: str,
        route_id: str,
        hatch_id: str,
        transition: str,
        actor_id: str,
        witnesses: Iterable[str],
        cost: Mapping[str, Any],
        parent_event_id: str | None = None,
        child_agent_id: str | None = None,
        child_claim_id: str | None = None,
        verified_delta: float | None = None,
        hold_class: str | None = None,
        seam: str | None = None,
        attempt_ref: str | None = None,
        remote: str = "origin",
    ) -> dict:
        """Persist a caller-declared observation.

        Declared observations remain audit-visible but never enter primary
        source-bound conversion metrics. Use the TSE Helix composition tools for
        source-bound success observations.
        """
        declared_basis = {
            "mission_id": mission_id,
            "route_id": route_id,
            "hatch_id": hatch_id,
            "transition": str(transition or "").upper(),
            "attempt_ref": attempt_ref,
        }
        source = _source_packet(
            DECLARED_ONLY,
            kind="CALLER_DECLARED",
            ref="DECLARED-" + _digest(declared_basis).split(":", 1)[1][:24],
            digest=_digest(declared_basis),
            git_head=self.git.head() if self.git.enabled else None,
            authority="NONE",
        )
        return self._record(
            mission_id=mission_id,
            route_id=route_id,
            hatch_id=hatch_id,
            transition=transition,
            actor_id=actor_id,
            witnesses=witnesses,
            cost=cost,
            source=source,
            parent_event_id=parent_event_id,
            child_agent_id=child_agent_id,
            child_claim_id=child_claim_id,
            verified_delta=verified_delta,
            hold_class=hold_class,
            seam=seam,
            attempt_ref=attempt_ref,
            remote=remote,
        )

    def record_source_bound(
        self,
        *,
        mission_id: str,
        route_id: str,
        hatch_id: str,
        transition: str,
        actor_id: str,
        witnesses: Iterable[str],
        cost: Mapping[str, Any],
        source_kind: str,
        source_ref: str,
        source_payload: Mapping[str, Any],
        source_git_head: str | None,
        source_authority: str,
        parent_event_id: str | None = None,
        child_agent_id: str | None = None,
        child_claim_id: str | None = None,
        verified_delta: float | None = None,
        hold_class: str | None = None,
        seam: str | None = None,
        attempt_ref: str | None = None,
        remote: str = "origin",
    ) -> dict:
        errors = _public_errors(source_payload)
        if errors:
            return {"status": "TSE_TELEMETRY_RECORD_HOLD", "hold": "EVIDENCE_HOLD", "errors": errors}
        try:
            source_ref = _require_id(source_ref, "source_ref")
        except ValueError as exc:
            return {"status": "TSE_TELEMETRY_RECORD_HOLD", "hold": "EVIDENCE_HOLD", "errors": [str(exc)]}
        source = _source_packet(
            SOURCE_BOUND,
            kind=source_kind,
            ref=source_ref,
            digest=_digest(source_payload),
            git_head=source_git_head,
            authority=source_authority,
        )
        return self._record(
            mission_id=mission_id,
            route_id=route_id,
            hatch_id=hatch_id,
            transition=transition,
            actor_id=actor_id,
            witnesses=witnesses,
            cost=cost,
            source=source,
            parent_event_id=parent_event_id,
            child_agent_id=child_agent_id,
            child_claim_id=child_claim_id,
            verified_delta=verified_delta,
            hold_class=hold_class,
            seam=seam,
            attempt_ref=attempt_ref or source_ref,
            remote=remote,
        )

    def report(
        self,
        *,
        mission_id: str,
        remote: str = "origin",
        shared_remote_mode: str = "REQUIRED",
    ) -> dict:
        try:
            mission_id = _require_id(mission_id, "mission_id")
        except ValueError as exc:
            return {"status": "TSE_TELEMETRY_REPORT_HOLD", "hold": "EVIDENCE_HOLD", "errors": [str(exc)]}
        sync = self._sync(remote, shared_remote_mode)
        events = [row for row in self._events() if row.get("mission_id") == mission_id]
        if str(shared_remote_mode).upper() == "REQUIRED" and not sync.get("shared_frontier_verified"):
            return {
                "status": "TSE_TELEMETRY_REPORT_HOLD",
                "hold": "STALE_STATE_HOLD",
                "remote_sync": sync,
                "events": events,
            }

        source_bound_events = [
            row for row in events if (row.get("source") or {}).get("verification") == SOURCE_BOUND
        ]
        source_bound_ids = {id(row) for row in source_bound_events}
        declared_events = [row for row in events if id(row) not in source_bound_ids]

        counts = {transition: 0 for transition in SUCCESS_TRANSITIONS}
        declared_counts = {transition: 0 for transition in SUCCESS_TRANSITIONS}
        residuals = {hold: 0 for hold in sorted(HOLD_CLASSES)}
        declared_residuals = {hold: 0 for hold in sorted(HOLD_CLASSES)}

        known_cost_total = 0.0
        all_costs_known = True
        applied_delta = 0.0
        route_ids = {str(event.get("route_id")) for event in events}

        for event in source_bound_events:
            transition = str(event.get("transition"))
            if transition in counts:
                counts[transition] += 1
            elif transition == HOLD_TRANSITION:
                hold = str(event.get("hold_class"))
                if hold in residuals:
                    residuals[hold] += 1
            cost = event.get("cost") or {}
            if cost.get("known") is True and _finite_nonnegative(cost.get("total")):
                known_cost_total += float(cost["total"])
            else:
                all_costs_known = False
            if transition == "RETURN_APPLIED" and _finite_nonnegative(event.get("verified_delta")):
                applied_delta += float(event["verified_delta"])

        for event in declared_events:
            transition = str(event.get("transition"))
            if transition in declared_counts:
                declared_counts[transition] += 1
            elif transition == HOLD_TRANSITION:
                hold = str(event.get("hold_class"))
                if hold in declared_residuals:
                    declared_residuals[hold] += 1

        metrics = {
            "eta_match": _ratio(counts["MATCH_FOUND"], counts["HATCH_NEED_PUBLISHED"]),
            "eta_claim": _ratio(counts["CHILD_CLAIMED"], counts["MATCH_FOUND"]),
            "eta_return": _ratio(counts["CHILD_VERIFIED_RETURN"], counts["CHILD_CLAIMED"]),
            "eta_apply": _ratio(counts["RETURN_APPLIED"], counts["CHILD_VERIFIED_RETURN"]),
            "eta_helix": (
                applied_delta / known_cost_total
                if counts["RETURN_APPLIED"] > 0 and all_costs_known and known_cost_total > 0
                else "UNKNOWN"
            ),
        }
        report_basis = {
            "mission_id": mission_id,
            "route_count": len(route_ids - {"None"}),
            "event_count": len(events),
            "source_bound_event_count": len(source_bound_events),
            "declared_event_count": len(declared_events),
            "counts": counts,
            "declared_counts": declared_counts,
            "residuals": residuals,
            "declared_residuals": declared_residuals,
            "metrics": metrics,
            "known_cost_total": known_cost_total,
            "all_costs_known": all_costs_known,
            "applied_verified_delta": applied_delta,
        }
        return {
            "status": "TSE_TELEMETRY_REPORT",
            **report_basis,
            "report_digest": _digest(report_basis),
            "remote_sync": sync,
            "shared_frontier_verified": bool(sync.get("shared_frontier_verified")),
            "measurement_standing": "PRIMARY_METRICS_SOURCE_BOUND_ONLY",
            "cost_standing": "REPORTED_COST_ATTACHED_TO_SOURCE_BOUND_EVENTS_NOT_CAUSAL_COST_PROOF",
            "behavioral_treatment_effect": "UNKNOWN",
            "causal_promotion_authority": False,
            "laws": [
                "TELEMETRY != AUTHORITY",
                "DECLARED_EVENT != SOURCE_BOUND_EVENT",
                "SOURCE_BOUND_EVENT != CAUSAL_EFFECT",
                "VERIFIED_CHILD_REQUIRES_VERIFIED_PARENT_LINEAGE",
                "UNKNOWN_DENOMINATOR != ZERO_EFFICIENCY",
                "UNKNOWN_COST != ZERO_COST",
                "MORE_HATCHES != MORE_CONTINUATION",
                "MORE_MATCHES != MORE_EXECUTION",
                "MORE_ACKS != MORE_WORK",
                "MORE_AGENTS != MORE_PRODUCTIVE_GAME_TIME",
                "MECHANISM_TELEMETRY != CAUSAL_TREATMENT_EFFECT",
            ],
        }

    @staticmethod
    def resource() -> dict:
        return {
            "version": TELEMETRY_VERSION,
            "artifact": "ATHENA.TSE.HELICAL.HANDOFF.TELEMETRY.V2",
            "success_transitions": list(SUCCESS_TRANSITIONS),
            "hold_transition": HOLD_TRANSITION,
            "hold_classes": sorted(HOLD_CLASSES),
            "metrics": ["eta_match", "eta_claim", "eta_return", "eta_apply", "eta_helix"],
            "primary_metric_population": SOURCE_BOUND,
            "declared_observation_population": DECLARED_ONLY,
            "authority": "OBSERVATION_ONLY",
            "behavioral_treatment_effect": "UNKNOWN",
            "laws": [
                "TELEMETRY != AUTHORITY",
                "DECLARED_EVENT != SOURCE_BOUND_EVENT",
                "SOURCE_BOUND_EVENT != EXECUTION_AUTHORITY",
                "SOURCE_BOUND_EVENT != CAUSAL_TREATMENT_EFFECT",
                "SHARED_MUTATION_REQUIRES_FRESH_REMOTE_FRONTIER",
                "VERIFIED_CHILD_REQUIRES_VERIFIED_PARENT_LINEAGE",
                "UNKNOWN_DENOMINATOR != ZERO_EFFICIENCY",
                "UNKNOWN_COST != ZERO_COST",
                "EVENT_REPLAY_IDEMPOTENT_CHANGED_SAME_ID_CONFLICTS",
            ],
        }
