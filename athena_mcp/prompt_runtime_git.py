from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Mapping

from .git_backend import GitStaleHead
from .prompt_runtime_types import (
    PROMPT_MANIFEST_PATH, PromptRuntimeError, canonical_json,
    nonempty as _nonempty, safe_actor as _safe_actor, sha256_bytes,
    string_list as _string_list,
)


class PromptRuntimeGit:
    def __init__(self, server: Any):
        self.server = server

    @property
    def configured(self) -> bool:
        return bool(getattr(self.server, "git", None) and self.server.git.enabled)

    def _root(self) -> Path:
        if not self.configured:
            raise PromptRuntimeError(
                "PROMPT_RUNTIME_UNAVAILABLE: configure ATHENA_GIT_ROOT to the canonical Athena Git checkout"
            )
        root = Path(self.server.git.root).resolve()
        if not (root / ".git").exists():
            raise PromptRuntimeError(f"PROMPT_RUNTIME_INVALID_GIT_ROOT: {root}")
        return root

    def _git(self, *args: str, env: Mapping[str, str] | None = None) -> str:
        root = self._root()
        process = subprocess.run(
            ["git", "-C", str(root), *args],
            text=True,
            capture_output=True,
            env=dict(env) if env is not None else None,
        )
        if process.returncode:
            detail = process.stderr.strip() or process.stdout.strip()
            raise PromptRuntimeError(f"GIT_COMMAND_FAILED git {' '.join(args)}: {detail}")
        return process.stdout.strip()

    def _head(self) -> str:
        return self._git("rev-parse", "HEAD")

    def _branch(self) -> str:
        return self._git("branch", "--show-current")

    def _dirty_rows(self) -> list[str]:
        raw = self._git("status", "--porcelain", "--untracked-files=all")
        return [line for line in raw.splitlines() if line.strip()]

    def _require_clean(self) -> None:
        rows = self._dirty_rows()
        if rows:
            raise PromptRuntimeError(
                "DIRTY_GIT_WORKTREE: exact-HEAD prompt hydration/mutation requires a clean checkout; "
                + canonical_json(rows[:20])
            )

    def _cas(self, expected_head: str) -> str:
        expected = _nonempty(expected_head, "expected_git_head")
        current = self._head()
        if current != expected:
            raise GitStaleHead(
                canonical_json({"status": "STALE_GIT_HEAD", "expected": expected, "current": current})
            )
        return current

    def _resolve(self, relative_path: str, *, must_exist: bool = True, prefix: str | None = None) -> Path:
        root = self._root()
        rel = _nonempty(relative_path, "path").replace("\\", "/")
        if any(ord(char) < 32 or ord(char) == 127 for char in rel):
            raise PromptRuntimeError(f"repository path contains control characters: {relative_path!r}")
        if rel.startswith("/") or re.match(r"^[A-Za-z]:/", rel):
            raise PromptRuntimeError(f"absolute repository path is forbidden: {relative_path!r}")
        candidate = root / rel
        if candidate.is_symlink():
            raise PromptRuntimeError(f"canonical prompt path may not be a symlink: {relative_path!r}")
        resolved = candidate.resolve(strict=False)
        try:
            normalized = resolved.relative_to(root).as_posix()
        except ValueError as exc:
            raise PromptRuntimeError(f"repository path escapes ATHENA_GIT_ROOT: {relative_path!r}") from exc
        if prefix is not None:
            normalized_prefix = prefix.strip("/") + "/"
            if normalized != prefix.strip("/") and not normalized.startswith(normalized_prefix):
                raise PromptRuntimeError(
                    f"path {relative_path!r} is outside required repository prefix {prefix!r}"
                )
        if must_exist and not resolved.is_file():
            raise PromptRuntimeError(f"required prompt body is missing: {relative_path!r}")
        return resolved

    def _relative(self, path: Path) -> str:
        return path.resolve().relative_to(self._root()).as_posix()

    def _read_text(self, relative_path: str, *, role: str) -> Dict[str, Any]:
        path = self._resolve(relative_path)
        raw = path.read_bytes()
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise PromptRuntimeError(f"{role} is not UTF-8: {relative_path!r}") from exc
        return {
            "path": self._relative(path),
            "role": role,
            "digest": sha256_bytes(raw),
            "bytes": len(raw),
            "text": text,
        }

    def _read_json(self, relative_path: str, *, role: str) -> tuple[Dict[str, Any], Dict[str, Any]]:
        body = self._read_text(relative_path, role=role)
        try:
            value = json.loads(body["text"])
        except json.JSONDecodeError as exc:
            raise PromptRuntimeError(f"invalid JSON in {relative_path!r}: {exc}") from exc
        if not isinstance(value, dict):
            raise PromptRuntimeError(f"{relative_path!r} must contain a JSON object")
        return value, body

    def _manifest(self) -> tuple[Dict[str, Any], Dict[str, Any]]:
        manifest, body = self._read_json(PROMPT_MANIFEST_PATH, role="manifest")
        if manifest.get("artifact") != "ATHENA.PROMPT.RUNTIME.V1":
            raise PromptRuntimeError(
                "PROMPT_RUNTIME_MANIFEST_MISMATCH: expected artifact ATHENA.PROMPT.RUNTIME.V1"
            )
        for field in ("policy", "active_state", "modules", "profiles", "authority_ceiling"):
            if field not in manifest:
                raise PromptRuntimeError(f"prompt manifest missing required field {field!r}")
        if not isinstance(manifest["modules"], dict) or not manifest["modules"]:
            raise PromptRuntimeError("prompt manifest modules must be a non-empty object")
        if not isinstance(manifest["profiles"], dict) or not manifest["profiles"]:
            raise PromptRuntimeError("prompt manifest profiles must be a non-empty object")
        return manifest, body

    def _active_state(self, manifest: Mapping[str, Any]) -> tuple[Dict[str, Any], Dict[str, Any]]:
        active, body = self._read_json(str(manifest["active_state"]), role="active_state")
        if active.get("prompt_runtime") != manifest.get("artifact"):
            raise PromptRuntimeError("active prompt state is bound to a different prompt runtime artifact")
        return active, body

    def _selected_modules(
        self,
        manifest: Mapping[str, Any],
        active: Mapping[str, Any],
        profile_override: str | None,
    ) -> tuple[str, list[tuple[str, Mapping[str, Any]]]]:
        profiles = manifest["profiles"]
        modules = manifest["modules"]
        profile = str(profile_override or active.get("profile") or manifest.get("default_profile") or "").strip()
        if profile not in profiles:
            raise PromptRuntimeError(f"unknown prompt profile {profile!r}")
        selected_raw = (
            profiles[profile]
            if profile_override is not None
            else active.get("enabled_modules", profiles[profile])
        )
        selected = _string_list(selected_raw, "enabled_modules")
        for module_id, spec in modules.items():
            if isinstance(spec, dict) and spec.get("mandatory") and module_id not in selected:
                selected.append(module_id)
        unknown = sorted(set(selected) - set(modules))
        if unknown:
            raise PromptRuntimeError(f"active prompt state selects unknown modules: {unknown}")
        ordered: list[tuple[str, Mapping[str, Any]]] = []
        for module_id in selected:
            spec = modules[module_id]
            if not isinstance(spec, dict):
                raise PromptRuntimeError(f"module specification {module_id!r} must be an object")
            if not isinstance(spec.get("path"), str) or not spec["path"].strip():
                raise PromptRuntimeError(f"module {module_id!r} has no valid path")
            ordered.append((module_id, spec))
        ordered.sort(key=lambda row: (int(row[1].get("order", 0)), row[0]))
        return profile, ordered

    @contextmanager
    def _write_lock(self):
        root = self._root()
        lock_path = root / ".git" / "athena-prompt-runtime.lock"
        handle = lock_path.open("a+b")
        if handle.tell() == 0:
            handle.write(b"\0")
            handle.flush()
        try:
            if os.name == "nt":
                import msvcrt

                handle.seek(0)
                try:
                    msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                except OSError as exc:
                    raise PromptRuntimeError("PROMPT_RUNTIME_LOCKED: another prompt mutation is active") from exc
            else:
                import fcntl

                try:
                    fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                except BlockingIOError as exc:
                    raise PromptRuntimeError("PROMPT_RUNTIME_LOCKED: another prompt mutation is active") from exc
            yield
        finally:
            try:
                if os.name == "nt":
                    import msvcrt

                    handle.seek(0)
                    msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    import fcntl

                    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
            finally:
                handle.close()

    def _commit_writes(
        self,
        *,
        expected_head: str,
        writes: Mapping[str, str],
        actor: str,
        message: str,
    ) -> Dict[str, Any]:
        if not writes:
            raise PromptRuntimeError("prompt mutation contains no writes")
        actor_name = _safe_actor(actor)
        commit_message = _nonempty(message, "message")
        normalized: Dict[str, Path] = {}
        normalized_writes: Dict[str, str] = {}
        for relative_path, content in writes.items():
            path = self._resolve(relative_path, must_exist=False)
            rel = self._relative(path)
            normalized[rel] = path
            normalized_writes[rel] = content
        if len(normalized) != len(writes):
            raise PromptRuntimeError("prompt mutation contains duplicate normalized paths")

        with self._write_lock():
            previous_head = self._cas(expected_head)
            self._require_clean()
            originals: Dict[str, bytes | None] = {
                rel: path.read_bytes() if path.exists() else None for rel, path in normalized.items()
            }
            try:
                for rel, path in normalized.items():
                    path.parent.mkdir(parents=True, exist_ok=True)
                    content = normalized_writes[rel]
                    if not isinstance(content, str):
                        raise PromptRuntimeError(f"write content for {rel!r} must be text")
                    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
                    try:
                        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as tmp:
                            tmp.write(content)
                            tmp.flush()
                            os.fsync(tmp.fileno())
                        os.replace(tmp_name, path)
                    finally:
                        if os.path.exists(tmp_name):
                            os.unlink(tmp_name)
                if self._head() != previous_head:
                    raise GitStaleHead(
                        canonical_json(
                            {
                                "status": "STALE_GIT_HEAD_DURING_MUTATION",
                                "expected": previous_head,
                                "current": self._head(),
                            }
                        )
                    )
                rels = sorted(normalized)
                self._git("add", "--", *rels)
                staged = [
                    line
                    for line in self._git("diff", "--cached", "--name-only", "--", *rels).splitlines()
                    if line.strip()
                ]
                if not staged:
                    raise PromptRuntimeError("NO_PROMPT_CHANGES: mutation would create no Git delta")
                if sorted(staged) != rels:
                    raise PromptRuntimeError(
                        f"STAGED_PATH_MISMATCH expected={rels!r} observed={sorted(staged)!r}"
                    )
                env = os.environ.copy()
                env.update(
                    {
                        "GIT_AUTHOR_NAME": actor_name,
                        "GIT_AUTHOR_EMAIL": "athena@local",
                        "GIT_COMMITTER_NAME": actor_name,
                        "GIT_COMMITTER_EMAIL": "athena@local",
                    }
                )
                self._git("commit", "-m", commit_message, env=env)
                new_head = self._head()
                return {
                    "status": "COMMITTED",
                    "previous_head": previous_head,
                    "head": new_head,
                    "paths": rels,
                    "message": commit_message,
                    "push_performed": False,
                    "authority": "LOCAL_GIT_DESCENDANT_ONLY",
                }
            except Exception:
                for rel, path in normalized.items():
                    original = originals[rel]
                    if original is None:
                        if path.exists():
                            path.unlink()
                    else:
                        path.parent.mkdir(parents=True, exist_ok=True)
                        path.write_bytes(original)
                subprocess.run(
                    ["git", "-C", str(self._root()), "reset", "--quiet", "HEAD", "--", *sorted(normalized)],
                    text=True,
                    capture_output=True,
                )
                raise
