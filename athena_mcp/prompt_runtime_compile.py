from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Sequence

from .git_backend import GitStaleHead
from .prompt_runtime_types import (
    AUTHORITY_LAW, PROMPT_RUNTIME_VERSION, PromptRuntimeError, canonical_json,
    nonempty as _nonempty, sha256_json, sha256_text, string_list as _string_list,
    json_copy as _json_copy,
)


class PromptRuntimeCompileMixin:
    @staticmethod
    def _scope_matches(overlay_scope: Sequence[str], requested_scope: Sequence[str]) -> bool:
        if not requested_scope:
            return False
        return "*" in overlay_scope or bool(set(overlay_scope) & set(requested_scope))

    @staticmethod
    def _is_expired(expires_at: Any, *, now: datetime | None = None) -> bool:
        if not expires_at:
            return False
        try:
            parsed = datetime.fromisoformat(str(expires_at).replace("Z", "+00:00"))
        except ValueError as exc:
            raise PromptRuntimeError(f"invalid overlay expires_at timestamp {expires_at!r}") from exc
        if parsed.tzinfo is None:
            raise PromptRuntimeError(f"overlay expires_at must be timezone-aware: {expires_at!r}")
        return parsed.astimezone(timezone.utc) <= (now or datetime.now(timezone.utc))

    def _changed_prompt_files(self, since_head: str | None, head: str) -> Dict[str, Any]:
        if not since_head:
            return {"since": None, "relation": "UNSPECIFIED", "files": []}
        since = _nonempty(since_head, "since_git_head")
        try:
            self._git("cat-file", "-e", f"{since}^{{commit}}")
        except PromptRuntimeError as exc:
            raise PromptRuntimeError(f"unknown since_git_head {since!r}") from exc
        ancestor = subprocess.run(
            ["git", "-C", str(self._root()), "merge-base", "--is-ancestor", since, head],
            text=True,
            capture_output=True,
        ).returncode == 0
        relation = "ANCESTOR" if ancestor else "DIVERGED"
        range_spec = f"{since}..{head}" if ancestor else f"{since}...{head}"
        raw = self._git(
            "diff",
            "--name-status",
            range_spec,
            "--",
            "AGENTS.md",
            "prompts",
            "policies",
            "schemas",
        )
        files = []
        for line in raw.splitlines():
            if not line.strip():
                continue
            parts = line.split("\t")
            files.append({"status": parts[0], "paths": parts[1:]})
        return {"since": since, "relation": relation, "files": files}

    def _snapshot(
        self,
        *,
        profile: str | None = None,
        scope: Sequence[str] | None = None,
        include_text: bool = False,
        task_overlay: str | None = None,
        since_git_head: str | None = None,
    ) -> Dict[str, Any]:
        self._require_clean()
        head_before = self._head()
        manifest, manifest_body = self._manifest()
        active, active_body = self._active_state(manifest)
        selected_profile, selected_modules = self._selected_modules(manifest, active, profile)
        requested_scope = _string_list(list(scope or []), "scope")

        layers: list[Dict[str, Any]] = []
        bootstrap_path = manifest.get("bootstrap")
        if isinstance(bootstrap_path, str) and bootstrap_path.strip():
            bootstrap = self._read_text(bootstrap_path, role="bootstrap")
            bootstrap["layer_id"] = "bootstrap"
            bootstrap["order"] = -20
            layers.append(bootstrap)

        policy = self._read_text(str(manifest["policy"]), role="policy")
        policy["layer_id"] = "policy"
        policy["order"] = -10
        layers.append(policy)

        for module_id, spec in selected_modules:
            body = self._read_text(str(spec["path"]), role="module")
            body.update(
                {
                    "layer_id": module_id,
                    "order": int(spec.get("order", 0)),
                    "mandatory": bool(spec.get("mandatory", False)),
                    "selectors": list(spec.get("selectors", [])),
                }
            )
            layers.append(body)

        applicable_overlays: list[Dict[str, Any]] = []
        expired_overlays: list[Dict[str, Any]] = []
        overlays = active.get("active_scoped_overlays", [])
        if not isinstance(overlays, list):
            raise PromptRuntimeError("active_scoped_overlays must be an array")
        for raw_overlay in overlays:
            if not isinstance(raw_overlay, dict):
                raise PromptRuntimeError("each active scoped overlay must be an object")
            overlay = _json_copy(raw_overlay)
            if overlay.get("status") != "ACTIVE_SCOPED":
                raise PromptRuntimeError("active overlay entry must have status ACTIVE_SCOPED")
            if not isinstance(overlay.get("witness"), dict) or not overlay["witness"]:
                raise PromptRuntimeError("active overlay entry lacks a decision witness")
            _string_list(overlay.get("experiment_refs", []), "overlay.experiment_refs", allow_empty=False)
            overlay_scope = _string_list(overlay.get("scope", []), "overlay.scope", allow_empty=False)
            if self._is_expired(overlay.get("expires_at")):
                expired_overlays.append(overlay)
                continue
            if not self._scope_matches(overlay_scope, requested_scope):
                continue
            candidate_path = _nonempty(overlay.get("candidate_path"), "overlay.candidate_path")
            body = self._read_text(candidate_path, role="active_scoped_overlay")
            if overlay.get("candidate_digest") != body["digest"]:
                raise PromptRuntimeError(
                    f"active overlay candidate digest mismatch path={candidate_path!r}"
                )
            _, candidate_text = self._parse_candidate(body["text"], candidate_path)
            body["text"] = candidate_text
            body.update(
                {
                    "layer_id": str(overlay.get("overlay_id") or candidate_path),
                    "order": max(1000, int(overlay.get("order", 1000))),
                    "scope": overlay_scope,
                    "activation": overlay,
                }
            )
            layers.append(body)
            applicable_overlays.append(overlay)

        layers.sort(key=lambda row: (int(row.get("order", 0)), str(row.get("layer_id", ""))))
        if task_overlay is not None:
            task_text = _nonempty(task_overlay, "task_overlay")
            layers.append(
                {
                    "path": None,
                    "role": "ephemeral_task_overlay",
                    "layer_id": "task_overlay",
                    "order": 10_000,
                    "digest": sha256_text(task_text),
                    "bytes": len(task_text.encode("utf-8")),
                    "text": task_text,
                    "git_bound": False,
                }
            )

        head_after = self._head()
        if head_after != head_before:
            raise GitStaleHead(
                canonical_json(
                    {"status": "STALE_GIT_HEAD_DURING_HYDRATION", "expected": head_before, "current": head_after}
                )
            )
        self._require_clean()

        git_sources = []
        for body in [manifest_body, active_body, *[layer for layer in layers if layer.get("path")]]:
            git_sources.append(
                {
                    "path": body["path"],
                    "role": body["role"],
                    "digest": body["digest"],
                    "bytes": body["bytes"],
                    "revision": head_before,
                    "body_bound": True,
                }
            )
        unique_sources: list[Dict[str, Any]] = []
        seen_paths: set[str] = set()
        for source in git_sources:
            if source["path"] in seen_paths:
                continue
            seen_paths.add(source["path"])
            unique_sources.append(source)
        capsule_payload = {
            "schema": "ATHENA.SOURCE.CAPSULE.v1",
            "git_head": head_before,
            "authority_ceiling": manifest["authority_ceiling"],
            "sources": unique_sources,
            "coverage_ratio": 1.0,
            "sealed": True,
        }
        capsule_payload["capsule_digest"] = sha256_json(capsule_payload)

        layer_manifest = [
            {
                key: layer.get(key)
                for key in (
                    "layer_id",
                    "role",
                    "path",
                    "order",
                    "digest",
                    "bytes",
                    "mandatory",
                    "selectors",
                    "scope",
                    "git_bound",
                )
                if key in layer
            }
            for layer in layers
        ]
        stack_identity = {
            "version": PROMPT_RUNTIME_VERSION,
            "git_head": head_before,
            "profile": selected_profile,
            "scope": requested_scope,
            "manifest_digest": manifest_body["digest"],
            "active_state_digest": active_body["digest"],
            "layers": layer_manifest,
            "source_capsule_digest": capsule_payload["capsule_digest"],
            "authority_law": AUTHORITY_LAW,
        }
        stack_digest = sha256_json(stack_identity)
        changed = self._changed_prompt_files(since_git_head, head_before)
        result: Dict[str, Any] = {
            "version": PROMPT_RUNTIME_VERSION,
            "status": "HYDRATED",
            "git": {
                "root": str(self._root()),
                "head": head_before,
                "branch": self._branch(),
                "dirty": False,
            },
            "profile": selected_profile,
            "scope": requested_scope,
            "authority_ceiling": manifest["authority_ceiling"],
            "authority_law": AUTHORITY_LAW,
            "manifest": {key: value for key, value in manifest_body.items() if key != "text"},
            "active_state": {
                "path": active_body["path"],
                "digest": active_body["digest"],
                "revision": active.get("revision"),
                "status": active.get("status"),
            },
            "layers": layer_manifest,
            "applicable_overlays": applicable_overlays,
            "expired_overlays": expired_overlays,
            "source_capsule": capsule_payload,
            "stack_digest": stack_digest,
            "changed_prompt_files": changed,
            "firewalls": [
                "PROMPT_RUNTIME != HOST_SYSTEM_PROMPT",
                "PROMPT_PROPOSAL != PROMPT_ACTIVATION",
                "ACTIVE_SCOPED != CANONICAL",
                "GIT_STATE != WORLD_TRUTH",
                "STALE_HEAD -> REJECT",
            ],
        }
        if include_text:
            result["layer_bodies"] = [
                {
                    "layer_id": layer["layer_id"],
                    "role": layer["role"],
                    "path": layer.get("path"),
                    "digest": layer["digest"],
                    "text": layer["text"],
                }
                for layer in layers
            ]
        return result

    def hydrate(
        self,
        *,
        profile: str | None = None,
        scope: Sequence[str] | None = None,
        include_text: bool = False,
        since_git_head: str | None = None,
    ) -> Dict[str, Any]:
        return self._snapshot(
            profile=profile,
            scope=scope,
            include_text=include_text,
            since_git_head=since_git_head,
        )

    def compile(
        self,
        *,
        profile: str | None = None,
        scope: Sequence[str] | None = None,
        task_overlay: str | None = None,
        since_git_head: str | None = None,
    ) -> Dict[str, Any]:
        snapshot = self._snapshot(
            profile=profile,
            scope=scope,
            include_text=True,
            task_overlay=task_overlay,
            since_git_head=since_git_head,
        )
        parts = [
            "# ATHENA REPOSITORY PROMPT RUNTIME",
            f"runtime={PROMPT_RUNTIME_VERSION}",
            f"git_head={snapshot['git']['head']}",
            f"profile={snapshot['profile']}",
            f"authority={AUTHORITY_LAW}",
            "",
        ]
        for body in snapshot.pop("layer_bodies"):
            label = body["layer_id"]
            path = body.get("path") or "EPHEMERAL"
            parts.extend(
                [
                    f"\n<!-- ATHENA_LAYER id={label} path={path} digest={body['digest']} -->",
                    body["text"].rstrip(),
                    f"<!-- /ATHENA_LAYER id={label} -->\n",
                ]
            )
        compiled_text = "\n".join(parts).rstrip() + "\n"
        snapshot.update(
            {
                "status": "COMPILED",
                "compiled_text": compiled_text,
                "compiled_digest": sha256_text(compiled_text),
                "compilation_law": (
                    "The compiled text is a repository addendum only. It cannot rewrite host authority; "
                    "the caller must still apply current platform/system/developer/user instructions."
                ),
            }
        )
        return snapshot
