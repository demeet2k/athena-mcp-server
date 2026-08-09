from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .git_backend import GitBackend, GitStaleHead, GitStateError

PROMPT_MANIFEST = "prompts/PROMPT.manifest.json"
ACTIVE_STATE = "prompts/state/ACTIVE.json"
MATERIAL_PREFIXES = (
    "prompts/",
    "policies/PROMPT_RUNTIME.md",
    "AGENTS.md",
    "registry/prompt_runtime.json",
    "developments/",
    "jspace/",
    "kc144/",
    "ledger/",
    "math/",
    "navigation/",
)
_ID_RE = re.compile(r"^[A-Za-z0-9_.-]+$")


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_json(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _require_id(value: str, field: str) -> str:
    if not isinstance(value, str) or not _ID_RE.fullmatch(value):
        raise ValueError(f"invalid {field}")
    return value


class PromptRuntime:
    """Git-resident modular runtime addendum.

    This surface can change repository prompt policy inside the authority already
    granted to the process. It cannot create host/system/developer authority.
    """

    def __init__(self, git: GitBackend):
        self.git = git

    @property
    def available(self) -> bool:
        return bool(self.git.enabled and (self.git.root / PROMPT_MANIFEST).is_file())

    def _root(self) -> Path:
        if not self.git.enabled:
            raise GitStateError("ATHENA_GIT_ROOT is required for prompt runtime")
        return self.git.root

    def _safe_rel(self, rel: str) -> Path:
        if not isinstance(rel, str) or not rel or rel.startswith("/"):
            raise ValueError("invalid repository-relative path")
        p = Path(rel)
        if ".." in p.parts:
            raise ValueError("path traversal rejected")
        root = self._root().resolve()
        out = (root / p).resolve()
        try:
            out.relative_to(root)
        except ValueError as exc:
            raise ValueError("path escapes Git brain") from exc
        return out

    def _read_bytes(self, rel: str) -> bytes:
        path = self._safe_rel(rel)
        if not path.is_file():
            raise ValueError(f"required prompt-runtime file missing: {rel}")
        return path.read_bytes()

    def _read_text(self, rel: str) -> str:
        return self._read_bytes(rel).decode("utf-8")

    def _read_json(self, rel: str):
        return json.loads(self._read_text(rel))

    def _manifest(self):
        m = self._read_json(PROMPT_MANIFEST)
        if m.get("artifact") not in {"ATHENA.PROMPT.RUNTIME.V1", "ATHENA.PROMPT.RUNTIME.V2"}:
            raise ValueError("unsupported prompt runtime manifest")
        if not isinstance(m.get("modules"), dict) or not m["modules"]:
            raise ValueError("prompt runtime has no modules")
        return m

    def _overlay_entries(self, active):
        """Normalize V1 object overlays and V2 path/state overlays.

        V2 deliberately keeps executable text and lifecycle state in separate
        files.  Never infer ACTIVE_SCOPED from a path alone.
        """
        raw = active.get("active_scoped_overlays") or []
        if not isinstance(raw, list):
            raise ValueError("active_scoped_overlays must be an array")
        state_paths = active.get("active_scoped_state") or []
        if not isinstance(state_paths, list):
            raise ValueError("active_scoped_state must be an array")
        states = {}
        for state_path in state_paths:
            if not isinstance(state_path, str):
                raise ValueError("active_scoped_state entries must be paths")
            state = self._read_json(state_path)
            overlay_path = state.get("overlay")
            if not isinstance(overlay_path, str):
                raise ValueError(f"overlay state missing overlay path: {state_path}")
            if overlay_path in states:
                raise ValueError(f"ambiguous overlay state binding: {overlay_path}")
            states[overlay_path] = {**state, "state_path": state_path}
        entries = []
        for item in raw:
            if isinstance(item, dict):
                entries.append(dict(item))
                continue
            if not isinstance(item, str):
                raise ValueError("active_scoped_overlays entries must be objects or paths")
            state = states.get(item)
            if not state or state.get("status") != "ACTIVE_SCOPED":
                raise ValueError(f"active overlay lacks ACTIVE_SCOPED state: {item}")
            activation = state.get("activation") if isinstance(state.get("activation"), dict) else {}
            state_scope = state.get("scope") if isinstance(state.get("scope"), list) else None
            entries.append({
                "overlay_id": state.get("artifact") or item,
                "path": item,
                "status": "ACTIVE_SCOPED",
                "module_id": None,
                "scope": state_scope if state_scope is not None else (["global"] if activation.get("automatic") is True else []),
                "expires_at": state.get("expires_at"),
                "state_path": state["state_path"],
            })
        orphaned = sorted(set(states) - {item for item in raw if isinstance(item, str)})
        if orphaned:
            raise ValueError(f"overlay state is not active: {orphaned[0]}")
        return entries

    def _active(self, manifest=None):
        manifest = manifest or self._manifest()
        path = manifest.get("active_state") or ACTIVE_STATE
        a = self._read_json(path)
        if a.get("status") != "ACTIVE":
            raise ValueError("prompt runtime active state is not ACTIVE")
        if a.get("prompt_runtime") not in {None, manifest.get("artifact")}:
            raise ValueError("prompt runtime active state targets another manifest")
        return a, path

    def _changed_paths(self, old_head: str | None, new_head: str | None = None):
        if not old_head:
            return []
        new_head = new_head or self.git.head()
        if old_head == new_head:
            return []
        try:
            out = self.git._git("diff", "--name-only", f"{old_head}..{new_head}")
        except GitStateError:
            return ["<UNKNOWN_ANCESTRY>"]
        return [x for x in out.splitlines() if x.strip()]

    @staticmethod
    def _scope_applies(scope, profile: str, task: str) -> bool:
        if not scope:
            return False
        task_l = (task or "").lower()
        profile_rules = []
        task_rules = []
        for raw in scope:
            if not isinstance(raw, str):
                return False
            if raw.startswith("profile:"):
                profile_rules.append(raw.split(":", 1)[1])
            elif raw.startswith("task:"):
                task_rules.append(raw.split(":", 1)[1].lower())
            elif raw == "global":
                continue
            else:
                task_rules.append(raw.lower())
        if profile_rules and profile not in profile_rules:
            return False
        if task_rules and not any(term in task_l for term in task_rules):
            return False
        return True

    @staticmethod
    def _not_expired(expires_at: str | None) -> bool:
        if not expires_at:
            return True
        try:
            dt = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
        except ValueError:
            return False
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt > datetime.now(timezone.utc)

    def _select_modules(self, manifest, active, task: str, profile: str | None):
        profile = profile or active.get("profile") or manifest.get("default_profile")
        profiles = manifest.get("profiles") or {}
        if profile not in profiles:
            raise ValueError(f"unknown prompt profile: {profile}")
        modules = manifest["modules"]
        enabled = set(active.get("enabled_modules") or modules.keys())
        selected = set()
        for name in profiles[profile]:
            if name not in modules:
                raise ValueError(f"profile references unknown module: {name}")
            if name in enabled or modules[name].get("mandatory"):
                selected.add(name)
        task_l = (task or "").lower()
        for name, cfg in modules.items():
            if cfg.get("mandatory"):
                selected.add(name)
            selectors = [str(x).lower() for x in cfg.get("selectors") or []]
            if name in enabled and selectors and any(s in task_l for s in selectors):
                selected.add(name)

        visiting = set()
        visited = set()

        def add_deps(name):
            if name in visited:
                return
            if name in visiting:
                raise ValueError(f"prompt dependency cycle at {name}")
            visiting.add(name)
            for dep in modules[name].get("depends_on") or []:
                if dep not in modules:
                    raise ValueError(f"module {name} depends on unknown {dep}")
                selected.add(dep)
                add_deps(dep)
            visiting.remove(name)
            visited.add(name)

        for name in list(selected):
            add_deps(name)

        by_order = {}
        for name in selected:
            order = int(modules[name].get("order", 1000))
            by_order.setdefault(order, []).append(name)
        collisions = {k: sorted(v) for k, v in by_order.items() if len(v) > 1}
        if collisions:
            raise ValueError(f"equal-level prompt conflict requires explicit resolution: {collisions}")
        ordered = sorted(selected, key=lambda n: (int(modules[n].get("order", 1000)), n))
        return profile, ordered

    def compile(self, task: str = "", profile: str | None = None, include_text: bool = True):
        manifest = self._manifest()
        active, active_path = self._active(manifest)
        head = self.git.head()
        profile, ordered = self._select_modules(manifest, active, task, profile)
        components = []
        policy_path = manifest.get("policy")
        if not policy_path:
            raise ValueError("prompt manifest missing policy")
        policy = self._read_bytes(policy_path)
        components.append({"kind": "policy", "id": "policy", "path": policy_path, "sha256": _sha(policy)})
        chunks = [f"[ATHENA_GIT_RUNTIME_ADDENDUM profile={profile}]", policy.decode("utf-8")]

        active_overlays = self._overlay_entries(active)
        selected_overlays = []
        for name in ordered:
            cfg = manifest["modules"][name]
            rel = cfg.get("path")
            raw = self._read_bytes(rel)
            components.append({"kind": "module", "id": name, "path": rel, "order": int(cfg.get("order", 1000)), "sha256": _sha(raw)})
            chunks.extend([f"\n[MODULE {name} path={rel}]", raw.decode("utf-8")])
            for ov in active_overlays:
                if ov.get("status") != "ACTIVE_SCOPED" or ov.get("module_id") != name:
                    continue
                if not self._not_expired(ov.get("expires_at")):
                    continue
                if not self._scope_applies(ov.get("scope") or [], profile, task):
                    continue
                ov_path = ov.get("path")
                ov_raw = self._read_bytes(ov_path)
                ov_id = ov.get("overlay_id") or ov_path
                components.append({"kind": "overlay", "id": ov_id, "module_id": name, "path": ov_path, "sha256": _sha(ov_raw)})
                chunks.extend([f"\n[ACTIVE_SCOPED_OVERLAY {ov_id} module={name}]", ov_raw.decode("utf-8")])
                selected_overlays.append(ov_id)

        # V2 supports global path/state overlays that are not owned by a
        # particular module.  Append them once after the ordered modules.
        for ov in active_overlays:
            if ov.get("module_id"):
                continue
            if ov.get("status") != "ACTIVE_SCOPED" or not self._not_expired(ov.get("expires_at")):
                continue
            if not self._scope_applies(ov.get("scope") or [], profile, task):
                continue
            ov_path = ov.get("path")
            ov_raw = self._read_bytes(ov_path)
            ov_id = ov.get("overlay_id") or ov_path
            component = {"kind": "overlay", "id": ov_id, "module_id": None, "path": ov_path, "sha256": _sha(ov_raw)}
            if ov.get("state_path"):
                component["state_path"] = ov["state_path"]
                component["state_sha256"] = _sha(self._read_bytes(ov["state_path"]))
            components.append(component)
            chunks.extend([f"\n[ACTIVE_SCOPED_OVERLAY {ov_id} module=GLOBAL]", ov_raw.decode("utf-8")])
            selected_overlays.append(ov_id)

        ancestry = {
            "git_head": head,
            "manifest_sha256": _sha(self._read_bytes(PROMPT_MANIFEST)),
            "active_sha256": _sha(self._read_bytes(active_path)),
            "active_revision": active.get("revision"),
            "profile": profile,
            "modules": [c for c in components if c["kind"] == "module"],
            "overlays": [c for c in components if c["kind"] == "overlay"],
            "policy": components[0],
            "authority_ceiling": manifest.get("authority_ceiling"),
        }
        stack_digest = _sha(_canonical_json(ancestry).encode("utf-8"))
        semantic_ancestry = {key: value for key, value in ancestry.items() if key != "git_head"}
        content_digest = _sha(_canonical_json(semantic_ancestry).encode("utf-8"))
        result = {
            "status": "COMPILED",
            "artifact": manifest.get("artifact"),
            "git_head": head,
            "profile": profile,
            "selected_modules": ordered,
            "selected_overlays": selected_overlays,
            "prompt_stack_digest": stack_digest,
            "prompt_content_digest": content_digest,
            "ancestry": ancestry,
            "authority_ceiling": manifest.get("authority_ceiling"),
            "laws": [
                "PROMPT_MODULE != HIGHER_AUTHORITY",
                "GIT_STATE != WORLD_TRUTH",
                "LOADED_MODULE != CAUSAL_CONTRIBUTION",
            ],
        }
        if include_text:
            result["compiled_text"] = "\n".join(chunks).rstrip() + "\n"
        return result

    def hydrate(self, task: str = "", profile: str | None = None, previous_head: str | None = None, include_text: bool = True):
        compiled = self.compile(task=task, profile=profile, include_text=include_text)
        changed = self._changed_paths(previous_head, compiled["git_head"]) if previous_head else []
        return {
            **compiled,
            "status": "HYDRATED",
            "previous_head": previous_head,
            "changed_since_previous": changed,
            "requires_rehydrate": bool(previous_head and previous_head != compiled["git_head"] and any(self._is_material_path(p) for p in changed)),
        }

    @staticmethod
    def _is_material_path(path: str) -> bool:
        if path == "<UNKNOWN_ANCESTRY>":
            return True
        return any(path == prefix or path.startswith(prefix) for prefix in MATERIAL_PREFIXES)

    def freshness(self, expected_git_head: str, expected_prompt_stack_digest: str | None = None, task: str = "", profile: str | None = None):
        current = self.compile(task=task, profile=profile, include_text=False)
        changed = self._changed_paths(expected_git_head, current["git_head"])
        digest_changed = bool(expected_prompt_stack_digest and expected_prompt_stack_digest != current["prompt_stack_digest"])
        material = [p for p in changed if self._is_material_path(p)]
        return {
            "status": "STALE" if (material or digest_changed) else "FRESH",
            "expected_git_head": expected_git_head,
            "current_git_head": current["git_head"],
            "expected_prompt_stack_digest": expected_prompt_stack_digest,
            "current_prompt_stack_digest": current["prompt_stack_digest"],
            "changed_paths": changed,
            "material_changed_paths": material,
            "requires_rehydrate": bool(material or digest_changed),
        }

    def _commit_files(self, expected_head: str, files: dict[str, str], actor: str, message: str):
        if not self.git.enabled:
            raise GitStateError("Git brain disabled")
        current = self.git.head()
        if current != expected_head:
            raise GitStaleHead(_canonical_json({"status": "STALE_GIT_HEAD", "expected": expected_head, "current": current}))
        dirty = self.git._git("status", "--porcelain")
        if dirty:
            raise GitStateError("DIRTY_GIT_ROOT: prompt-runtime write refuses to absorb unrelated working-tree state")
        actor = _require_id(actor or "agent", "actor")
        backups = {}
        rels = []
        try:
            for rel, text in files.items():
                if not rel.startswith("prompts/"):
                    raise ValueError("prompt runtime may only write under prompts/")
                path = self._safe_rel(rel)
                backups[rel] = path.read_bytes() if path.exists() else None
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
                rels.append(rel)
            self.git._git("add", "--", *rels)
            staged = self.git._git("diff", "--cached", "--name-only")
            if not staged:
                return {"status": "NO_CHANGES", "head": current, "previous_head": current, "shared_remote": False}
            env = os.environ.copy()
            env.setdefault("GIT_AUTHOR_NAME", actor)
            env.setdefault("GIT_AUTHOR_EMAIL", "athena@local")
            env.setdefault("GIT_COMMITTER_NAME", actor)
            env.setdefault("GIT_COMMITTER_EMAIL", "athena@local")
            p = subprocess.run(["git", "-C", str(self.git.root), "commit", "-m", message], text=True, capture_output=True, env=env)
            if p.returncode:
                raise GitStateError(p.stderr.strip() or p.stdout.strip())
        except Exception:
            try:
                self.git._git("reset", "--hard", current)
                for rel, old in backups.items():
                    if old is None:
                        path = self._safe_rel(rel)
                        if path.exists():
                            path.unlink()
            finally:
                pass
            raise
        new_head = self.git.head()
        shared_remote = False
        push_error = None
        if os.getenv("ATHENA_GIT_AUTOPUSH") == "1":
            branch = self.git._git("branch", "--show-current")
            if not branch:
                push_error = "detached HEAD; local commit retained"
            else:
                p = subprocess.run(["git", "-C", str(self.git.root), "push", "origin", f"HEAD:refs/heads/{branch}"], text=True, capture_output=True)
                if p.returncode:
                    push_error = p.stderr.strip() or p.stdout.strip()
                else:
                    shared_remote = True
        status = "COMMITTED_REMOTE" if shared_remote else ("COMMITTED_LOCAL_PUSH_FAILED" if push_error else "COMMITTED_LOCAL")
        return {
            "status": status,
            "head": new_head,
            "previous_head": current,
            "paths": rels,
            "shared_remote": shared_remote,
            "push_error": push_error,
            "law": "LOCAL_COMMIT != SHARED_REMOTE_RETURN unless shared_remote=true",
        }

    @staticmethod
    def _candidate_render(meta: dict, body: str) -> str:
        return "<!-- ATHENA_PROMPT_CANDIDATE_META\n" + json.dumps(meta, indent=2, sort_keys=True, ensure_ascii=False) + "\n-->\n" + body.rstrip() + "\n"

    def _candidate_read(self, candidate_ref: str):
        if not candidate_ref.startswith("prompts/candidates/") or not candidate_ref.endswith(".md"):
            raise ValueError("candidate_ref must be a prompts/candidates/*.md path")
        text = self._read_text(candidate_ref)
        prefix = "<!-- ATHENA_PROMPT_CANDIDATE_META\n"
        if not text.startswith(prefix) or "\n-->\n" not in text:
            raise ValueError("candidate metadata missing")
        raw_meta, body = text[len(prefix):].split("\n-->\n", 1)
        return json.loads(raw_meta), body

    def _event(self, kind: str, actor: str, payload: dict):
        eid = f"PREV-{uuid.uuid4().hex}"
        return eid, {
            "event_id": eid,
            "kind": kind,
            "actor": actor,
            "created_at": _utcnow(),
            "git_head_pre": self.git.head(),
            "payload": payload,
            "authority_law": "PROMPT_EVENT != HIGHER_AUTHORITY",
        }

    def propose(self, module_id: str, content: str, defect: str, expected_effect: str, scope: list[str], tests: list[str], falsifier: str, rollback: str, expected_git_head: str, actor: str = "agent", task: str = "", profile: str | None = None):
        module_id = _require_id(module_id, "module_id")
        manifest = self._manifest()
        if module_id not in manifest["modules"]:
            raise ValueError("unknown canonical module")
        current_compile = self.compile(task=task, profile=profile, include_text=False)
        target = manifest["modules"][module_id]["path"]
        target_digest = _sha(self._read_bytes(target))
        cid = f"PRM-{module_id}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}"
        rel = f"prompts/candidates/{module_id}/{cid}.md"
        meta = {
            "candidate_id": cid,
            "module_id": module_id,
            "version": "candidate-v1",
            "status": "CANDIDATE",
            "scope": list(scope or []),
            "authority_ceiling": manifest.get("authority_ceiling"),
            "depends_on": manifest["modules"][module_id].get("depends_on") or [],
            "triggers": manifest["modules"][module_id].get("selectors") or [],
            "path": rel,
            "canonical_target": target,
            "base_module_digest": target_digest,
            "base_digest": current_compile["prompt_stack_digest"],
            "expected_git_head": expected_git_head,
            "defect": defect,
            "expected_effect": expected_effect,
            "tests": list(tests or []),
            "falsifier": falsifier,
            "rollback": rollback,
            "created_by": actor,
            "created_at": _utcnow(),
            "experiment_refs": [],
        }
        eid, event = self._event("PROMPT_PROPOSAL", actor, {"candidate_ref": rel, "module_id": module_id, "defect": defect})
        result = self._commit_files(expected_git_head, {rel: self._candidate_render(meta, content), f"prompts/events/{eid}.json": json.dumps(event, indent=2, sort_keys=True, ensure_ascii=False) + "\n"}, actor, f"prompt proposal {cid}")
        return {"candidate_ref": rel, "candidate_id": cid, "metadata": meta, "git": result, "law": "PROMPT_PROPOSAL != PROMPT_PROMOTION"}

    def record_experiment(self, candidate_ref: str, expected_git_head: str, observed: bool, verdict: str, observations: dict, evidence_refs: list[str], actor: str = "agent"):
        verdict = str(verdict).upper()
        allowed = {"PASS", "FAIL", "INCONCLUSIVE", "DESIGN_ONLY"}
        if verdict not in allowed:
            raise ValueError("invalid experiment verdict")
        if not observed and verdict != "DESIGN_ONLY":
            raise ValueError("unobserved experiment may only be DESIGN_ONLY")
        meta, body = self._candidate_read(candidate_ref)
        xid = f"PEX-{uuid.uuid4().hex}"
        exp_rel = f"prompts/experiments/{xid}.json"
        record = {
            "experiment_id": xid,
            "candidate_ref": candidate_ref,
            "candidate_id": meta.get("candidate_id"),
            "module_id": meta.get("module_id"),
            "observed": bool(observed),
            "verdict": verdict,
            "observations": observations or {},
            "evidence_refs": list(evidence_refs or []),
            "created_at": _utcnow(),
            "created_by": actor,
            "law": "PROMPT_EXPERIMENT != OBSERVATION_UNLESS_ACTUALLY_RUN",
        }
        meta.setdefault("experiment_refs", []).append(exp_rel)
        if observed and verdict == "PASS":
            meta["status"] = "TESTED"
        eid, event = self._event("PROMPT_TEST", actor, {"candidate_ref": candidate_ref, "experiment_ref": exp_rel, "observed": bool(observed), "verdict": verdict})
        files = {
            exp_rel: json.dumps(record, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            candidate_ref: self._candidate_render(meta, body),
            f"prompts/events/{eid}.json": json.dumps(event, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        }
        result = self._commit_files(expected_git_head, files, actor, f"prompt experiment {xid} {verdict}")
        return {"experiment_ref": exp_rel, "record": record, "candidate_status": meta["status"], "git": result}

    @staticmethod
    def _witness_pass(witness: dict, key: str = "status") -> bool:
        return isinstance(witness, dict) and str(witness.get(key, "")).upper() == "PASS"

    def activate(self, candidate_ref: str, expected_git_head: str, scope: list[str], experiment_refs: list[str], witness: dict, actor: str = "agent", expires_at: str | None = None):
        meta, body = self._candidate_read(candidate_ref)
        if meta.get("status") != "TESTED":
            raise ValueError("only TESTED candidate may become ACTIVE_SCOPED")
        if not scope:
            raise ValueError("ACTIVE_SCOPED requires non-empty scope")
        if not self._witness_pass(witness):
            raise ValueError("ACTIVE_SCOPED requires PASS witness")
        known = set(meta.get("experiment_refs") or [])
        refs = list(experiment_refs or [])
        if not refs or not set(refs).issubset(known):
            raise ValueError("activation requires recorded candidate experiments")
        if expires_at and not self._not_expired(expires_at):
            raise ValueError("overlay expiry is invalid or not in the future")
        manifest = self._manifest()
        active, active_path = self._active(manifest)
        oid = f"OVR-{uuid.uuid4().hex}"
        overlay_rel = f"prompts/overlays/{oid}.md"
        entry = {
            "overlay_id": oid,
            "candidate_ref": candidate_ref,
            "module_id": meta["module_id"],
            "path": overlay_rel,
            "status": "ACTIVE_SCOPED",
            "scope": list(scope),
            "experiment_refs": refs,
            "witness": witness,
            "activated_by": actor,
            "activated_at": _utcnow(),
            "expires_at": expires_at,
        }
        existing = active.get("active_scoped_overlays") or []
        if manifest.get("artifact") == "ATHENA.PROMPT.RUNTIME.V2":
            if any(not isinstance(x, str) for x in existing):
                raise ValueError("V2 active overlays must be paths")
            state_paths = active.get("active_scoped_state") or []
            if any(not isinstance(x, str) for x in state_paths):
                raise ValueError("V2 active overlay state entries must be paths")
            for state_path in state_paths:
                state = self._read_json(state_path)
                if state.get("candidate_source") == candidate_ref and state.get("status") == "ACTIVE_SCOPED":
                    raise ValueError("candidate already has active scoped overlay")
            state_rel = f"prompts/state/{oid}.json"
            state_entry = {
                "artifact": "ATHENA.PROMPT.OVERLAY.STATE.V2",
                "status": "ACTIVE_SCOPED",
                "overlay": overlay_rel,
                "candidate_source": candidate_ref,
                "scope": list(scope),
                "witness": witness,
                "experiment_refs": refs,
                "activated_by": actor,
                "activated_at": _utcnow(),
                "expires_at": expires_at,
                "rollback": {"method": "remove overlay and state paths from ACTIVE"},
            }
            active["active_scoped_overlays"] = existing + [overlay_rel]
            active["active_scoped_state"] = state_paths + [state_rel]
        else:
            if any(isinstance(x, dict) and x.get("candidate_ref") == candidate_ref and x.get("status") == "ACTIVE_SCOPED" for x in existing):
                raise ValueError("candidate already has active scoped overlay")
            active["active_scoped_overlays"] = existing + [entry]
        active["revision"] = int(active.get("revision") or 0) + 1
        meta["status"] = "ACTIVE_SCOPED"
        eid, event = self._event("PROMPT_ACTIVATE", actor, {"candidate_ref": candidate_ref, "overlay_id": oid, "scope": scope, "experiment_refs": refs})
        files = {
            overlay_rel: body.rstrip() + "\n",
            active_path: json.dumps(active, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            candidate_ref: self._candidate_render(meta, body),
            f"prompts/events/{eid}.json": json.dumps(event, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        }
        if manifest.get("artifact") == "ATHENA.PROMPT.RUNTIME.V2":
            files[state_rel] = json.dumps(state_entry, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
        result = self._commit_files(expected_git_head, files, actor, f"activate scoped prompt overlay {oid}")
        return {"overlay": entry, "active_revision": active["revision"], "git": result, "law": "ACTIVE_SCOPED != CANONICAL"}

    def promote(self, candidate_ref: str, expected_git_head: str, experiment_refs: list[str], evidence_refs: list[str], witness: dict, actor: str = "agent"):
        meta, body = self._candidate_read(candidate_ref)
        if meta.get("status") not in {"TESTED", "ACTIVE_SCOPED"}:
            raise ValueError("canonical promotion requires TESTED or ACTIVE_SCOPED candidate")
        for key in ("regression_status", "adversarial_status", "replay_status"):
            if not self._witness_pass(witness, key):
                raise ValueError(f"canonical promotion requires {key}=PASS")
        refs = list(experiment_refs or [])
        if not refs or not set(refs).issubset(set(meta.get("experiment_refs") or [])):
            raise ValueError("canonical promotion requires recorded experiment lineage")
        if not evidence_refs:
            raise ValueError("canonical promotion requires evidence refs")
        if not meta.get("rollback"):
            raise ValueError("canonical promotion requires rollback path")
        target = meta.get("canonical_target")
        current_target_digest = _sha(self._read_bytes(target))
        if current_target_digest != meta.get("base_module_digest"):
            raise GitStaleHead(_canonical_json({"status": "STALE_PROMPT_BASE", "candidate_base": meta.get("base_module_digest"), "current": current_target_digest, "target": target}))
        manifest = self._manifest()
        active, active_path = self._active(manifest)
        before = active.get("active_scoped_overlays") or []
        if manifest.get("artifact") == "ATHENA.PROMPT.RUNTIME.V2":
            state_before = active.get("active_scoped_state") or []
            remove_overlays, state_after = set(), []
            for state_path in state_before:
                state = self._read_json(state_path)
                if state.get("candidate_source") == candidate_ref:
                    if isinstance(state.get("overlay"), str):
                        remove_overlays.add(state["overlay"])
                else:
                    state_after.append(state_path)
            after = [path for path in before if path not in remove_overlays]
            active["active_scoped_state"] = state_after
        else:
            after = [x for x in before if not (isinstance(x, dict) and x.get("candidate_ref") == candidate_ref)]
        files = {target: body.rstrip() + "\n"}
        if after != before:
            active["active_scoped_overlays"] = after
            active["revision"] = int(active.get("revision") or 0) + 1
            files[active_path] = json.dumps(active, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
        meta["status"] = "CANONICAL"
        meta["promoted_at"] = _utcnow()
        meta["promotion_witness"] = witness
        meta["promotion_evidence_refs"] = list(evidence_refs)
        files[candidate_ref] = self._candidate_render(meta, body)
        eid, event = self._event("PROMPT_PROMOTE", actor, {"candidate_ref": candidate_ref, "module_id": meta["module_id"], "target": target, "experiment_refs": refs, "evidence_refs": list(evidence_refs), "witness": witness})
        files[f"prompts/events/{eid}.json"] = json.dumps(event, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
        result = self._commit_files(expected_git_head, files, actor, f"promote prompt module {meta['module_id']} from {meta['candidate_id']}")
        return {"status": "CANONICAL", "module_id": meta["module_id"], "target": target, "candidate_ref": candidate_ref, "git": result, "law": "PROMPT_PROMOTION remains below higher authority"}

    def call_tool(self, name: str, a: dict):
        if name == "athena_prompt_hydrate":
            return self.hydrate(a.get("task", ""), a.get("profile"), a.get("previous_head"), a.get("include_text", True))
        if name == "athena_prompt_compile":
            return self.compile(a.get("task", ""), a.get("profile"), a.get("include_text", True))
        if name == "athena_prompt_freshness":
            return self.freshness(a["expected_git_head"], a.get("expected_prompt_stack_digest"), a.get("task", ""), a.get("profile"))
        if name == "athena_prompt_propose":
            return self.propose(a["module_id"], a["content"], a["defect"], a["expected_effect"], a.get("scope") or [], a.get("tests") or [], a["falsifier"], a["rollback"], a["expected_git_head"], a.get("actor", "agent"), a.get("task", ""), a.get("profile"))
        if name == "athena_prompt_experiment":
            return self.record_experiment(a["candidate_ref"], a["expected_git_head"], a["observed"], a["verdict"], a.get("observations") or {}, a.get("evidence_refs") or [], a.get("actor", "agent"))
        if name == "athena_prompt_activate":
            return self.activate(a["candidate_ref"], a["expected_git_head"], a["scope"], a["experiment_refs"], a["witness"], a.get("actor", "agent"), a.get("expires_at"))
        if name == "athena_prompt_promote":
            return self.promote(a["candidate_ref"], a["expected_git_head"], a["experiment_refs"], a["evidence_refs"], a["witness"], a.get("actor", "agent"))
        raise KeyError(name)


PROMPT_RUNTIME_TOOLS = [
    {"name": "athena_prompt_hydrate", "description": "Hydrate the exact current Git prompt runtime and deterministically compile the task/profile addendum with ancestry/digest.", "inputSchema": {"type": "object", "properties": {"task": {"type": "string"}, "profile": {"type": ["string", "null"]}, "previous_head": {"type": ["string", "null"]}, "include_text": {"type": "boolean"}}, "additionalProperties": False}},
    {"name": "athena_prompt_compile", "description": "Deterministically compile policy, selected modules, and applicable scoped overlays from the configured Git brain.", "inputSchema": {"type": "object", "properties": {"task": {"type": "string"}, "profile": {"type": ["string", "null"]}, "include_text": {"type": "boolean"}}, "additionalProperties": False}},
    {"name": "athena_prompt_freshness", "description": "Compare an agent's prompt/Git ancestry with the current brain and require rehydration on material shared changes.", "inputSchema": {"type": "object", "required": ["expected_git_head"], "properties": {"expected_git_head": {"type": "string"}, "expected_prompt_stack_digest": {"type": ["string", "null"]}, "task": {"type": "string"}, "profile": {"type": ["string", "null"]}}, "additionalProperties": False}},
    {"name": "athena_prompt_propose", "description": "CAS-write a versioned prompt candidate plus proposal event. Proposal never activates or promotes itself.", "inputSchema": {"type": "object", "required": ["module_id", "content", "defect", "expected_effect", "falsifier", "rollback", "expected_git_head"], "properties": {"module_id": {"type": "string"}, "content": {"type": "string"}, "defect": {"type": "string"}, "expected_effect": {"type": "string"}, "scope": {"type": "array", "items": {"type": "string"}}, "tests": {"type": "array", "items": {"type": "string"}}, "falsifier": {"type": "string"}, "rollback": {"type": "string"}, "expected_git_head": {"type": "string"}, "actor": {"type": "string"}, "task": {"type": "string"}, "profile": {"type": ["string", "null"]}}, "additionalProperties": False}},
    {"name": "athena_prompt_experiment", "description": "Persist a baseline/candidate prompt experiment record; unexecuted designs cannot be recorded as observed PASS.", "inputSchema": {"type": "object", "required": ["candidate_ref", "expected_git_head", "observed", "verdict"], "properties": {"candidate_ref": {"type": "string"}, "expected_git_head": {"type": "string"}, "observed": {"type": "boolean"}, "verdict": {"type": "string"}, "observations": {"type": "object"}, "evidence_refs": {"type": "array", "items": {"type": "string"}}, "actor": {"type": "string"}}, "additionalProperties": False}},
    {"name": "athena_prompt_activate", "description": "CAS-activate a TESTED prompt candidate as a scope-limited overlay after an observed PASS witness.", "inputSchema": {"type": "object", "required": ["candidate_ref", "expected_git_head", "scope", "experiment_refs", "witness"], "properties": {"candidate_ref": {"type": "string"}, "expected_git_head": {"type": "string"}, "scope": {"type": "array", "items": {"type": "string"}, "minItems": 1}, "experiment_refs": {"type": "array", "items": {"type": "string"}, "minItems": 1}, "witness": {"type": "object"}, "expires_at": {"type": ["string", "null"]}, "actor": {"type": "string"}}, "additionalProperties": False}},
    {"name": "athena_prompt_promote", "description": "CAS-promote a tested candidate into its canonical Git prompt module only with regression, adversarial, replay and evidence gates.", "inputSchema": {"type": "object", "required": ["candidate_ref", "expected_git_head", "experiment_refs", "evidence_refs", "witness"], "properties": {"candidate_ref": {"type": "string"}, "expected_git_head": {"type": "string"}, "experiment_refs": {"type": "array", "items": {"type": "string"}, "minItems": 1}, "evidence_refs": {"type": "array", "items": {"type": "string"}, "minItems": 1}, "witness": {"type": "object"}, "actor": {"type": "string"}}, "additionalProperties": False}},
]
PROMPT_RUNTIME_TOOL_NAMES = {x["name"] for x in PROMPT_RUNTIME_TOOLS}
