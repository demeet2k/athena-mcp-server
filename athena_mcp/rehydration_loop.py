from __future__ import annotations

import hashlib
import json
import re
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .frontier_runtime import DEFAULT_SOURCE_REF, FrontierRuntime
from .git_backend import GitBackend, GitStaleHead, GitStateError
from .prompt_remote import PromptRemoteSync
from .prompt_runtime import PromptRuntime

LOOP_ROOT = "prompts/rehydration"
ARTIFACT = "ATHENA.REHYDRATION.LOOP.V1"
TERMINAL_STATES = {"COMPLETE", "HOLD_MAX_STEPS", "HOLD_NO_PROGRESS", "ABORTED"}
COMPLETION_STATES = {"SUCCEEDED", "PARTIAL", "HELD", "FAILED", "NO_PROGRESS"}
DEPTH_MODES = {
    "standard": ("reconstruct", "execute", "verify"),
    "deep": ("reconstruct", "retrieve", "generate", "attack", "execute", "verify", "synthesize"),
}
_ID_RE = re.compile(r"^[A-Za-z0-9_.-]+$")
_DIGEST_EXCLUDE = {"state_digest", "current_prompt_digest", "chain_digest"}


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


def _require_id(value: str, field: str) -> str:
    if not isinstance(value, str) or not _ID_RE.fullmatch(value):
        raise ValueError(f"invalid {field}")
    return value


def _bounded_int(value: Any, field: str, lower: int, upper: int) -> int:
    try:
        out = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"invalid {field}") from exc
    if not lower <= out <= upper:
        raise ValueError(f"{field} must be between {lower} and {upper}")
    return out


def _state_digest(state: dict) -> str:
    return _sha({k: v for k, v in state.items() if k not in _DIGEST_EXCLUDE})


def _record_digest(record: dict, excluded: set[str] | None = None) -> str:
    excluded = excluded or set()
    return _sha({k: v for k, v in record.items() if k not in excluded})


class RehydrationLoopRuntime:
    """Persisted prompt→work→Git→rehydrate orchestration loop.

    The runtime does not perform background thinking. It compiles explicit bounded
    continuation prompts and persists every observed cycle to Git so a later turn
    or another agent can resume from an exact checkpoint.
    """

    def __init__(
        self,
        git: GitBackend,
        prompt_runtime: PromptRuntime | None = None,
        frontier_runtime: FrontierRuntime | None = None,
        remote_sync: PromptRemoteSync | None = None,
    ):
        self.git = git
        self.prompt_runtime = prompt_runtime or PromptRuntime(git)
        self.frontier_runtime = frontier_runtime or FrontierRuntime(git, self.prompt_runtime)
        self.remote_sync = remote_sync or PromptRemoteSync(git)

    @property
    def available(self) -> bool:
        return bool(self.git.enabled and self.prompt_runtime.available)

    def _root(self) -> Path:
        if not self.git.enabled:
            raise GitStateError("ATHENA_GIT_ROOT is required for rehydration loop")
        return self.git.root

    def _safe_rel(self, rel: str) -> Path:
        return self.prompt_runtime._safe_rel(rel)

    @staticmethod
    def _loop_base(loop_id: str) -> str:
        return f"{LOOP_ROOT}/{_require_id(loop_id, 'loop_id')}"

    def _paths(self, loop_id: str) -> dict[str, str]:
        base = self._loop_base(loop_id)
        return {
            "base": base,
            "state": f"{base}/state.json",
            "prompts": f"{base}/prompts",
            "receipts": f"{base}/receipts",
            "events": f"{base}/events",
        }

    def _read_json(self, rel: str) -> dict:
        path = self._safe_rel(rel)
        if not path.is_file():
            raise ValueError(f"rehydration file missing: {rel}")
        value = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise ValueError(f"rehydration object must be JSON object: {rel}")
        return value

    def _read_state(self, loop_id: str) -> tuple[dict, dict[str, str]]:
        paths = self._paths(loop_id)
        state = self._read_json(paths["state"])
        if state.get("artifact") != ARTIFACT or state.get("loop_id") != loop_id:
            raise ValueError("unsupported or mismatched rehydration state")
        return state, paths

    def _loop_prompt_path(self, paths: dict[str, str], rel: str, expected_name: str | None = None) -> Path:
        if not isinstance(rel, str) or not rel.startswith(paths["prompts"] + "/") or not rel.endswith(".md"):
            raise ValueError("loop prompt path escapes the loop prompt namespace")
        if expected_name is not None and Path(rel).name != expected_name:
            raise ValueError("loop prompt path does not match the expected step")
        return self._safe_rel(rel)

    def _path_last_commit(self, rel: str) -> str | None:
        p = subprocess.run(
            ["git", "-C", str(self._root()), "log", "-n", "1", "--format=%H", "--", rel],
            text=True,
            capture_output=True,
        )
        if p.returncode:
            raise GitStateError(p.stderr.strip() or p.stdout.strip())
        return p.stdout.strip() or None

    def _is_ancestor(self, older: str, newer: str) -> bool:
        p = subprocess.run(
            ["git", "-C", str(self._root()), "merge-base", "--is-ancestor", older, newer],
            text=True,
            capture_output=True,
        )
        if p.returncode not in (0, 1):
            raise GitStateError(p.stderr.strip() or p.stdout.strip())
        return p.returncode == 0

    def _changed_paths(self, older: str, newer: str) -> list[str]:
        if older == newer:
            return []
        out = self.git._git("diff", "--name-only", f"{older}..{newer}")
        return sorted(x for x in out.splitlines() if x.strip())

    @staticmethod
    def _remote_mode(value: str | None) -> str:
        mode = str(value or "REQUIRED").upper()
        if mode not in {"REQUIRED", "BEST_EFFORT", "DISABLED"}:
            raise ValueError("shared_remote_mode must be REQUIRED, BEST_EFFORT, or DISABLED")
        return mode

    def _sync_before_write(self, mode: str, remote: str) -> dict:
        if mode == "DISABLED":
            return {"status": "DISABLED", "shared_frontier_verified": False}
        state = self.remote_sync.sync(remote)
        if mode == "REQUIRED" and not state.get("shared_frontier_verified"):
            raise GitStateError(json.dumps({"status": "SHARED_FRONTIER_HOLD", "remote_sync": state}, sort_keys=True))
        return state

    def _publish_after_write(self, mode: str, remote: str, head: str) -> dict:
        if mode == "DISABLED":
            return {"status": "DISABLED", "shared_frontier_verified": False}
        state = self.remote_sync.publish(head, remote)
        if mode == "REQUIRED" and not state.get("shared_frontier_verified"):
            raise GitStateError(json.dumps({"status": "LOCAL_MUTATION_PUBLISH_HOLD", "remote_publish": state}, sort_keys=True))
        return state

    def _frontier_snapshot(
        self,
        *,
        task: str,
        profile: str | None,
        source_ref: str,
        remote: str,
        fetch: bool,
        use_frontier: bool,
    ) -> dict:
        if not use_frontier:
            return {
                "status": "DISABLED",
                "source_head": None,
                "frontier_digest": None,
                "selected": None,
                "pareto_front": [],
                "residuals": [],
                "law": "DISABLED_FRONTIER != EXECUTION_AUTHORITY",
            }
        try:
            selection = self.frontier_runtime.select(
                task=task,
                profile=profile,
                source_ref=source_ref,
                remote=remote,
                fetch=fetch,
            )
            frontier = selection.get("frontier") or {}
            return {
                "status": selection.get("status"),
                "reason": selection.get("reason"),
                "source_head": selection.get("source_head") or frontier.get("source_head"),
                "frontier_digest": selection.get("frontier_digest") or frontier.get("frontier_digest"),
                "selected": selection.get("selected"),
                "pareto_front": selection.get("pareto_front") or [],
                "residuals": frontier.get("residuals") or [],
                "source_coverage": frontier.get("source_coverage"),
            }
        except Exception as exc:  # surfaced as a typed hold, never hidden as readiness
            return {
                "status": "FRONTIER_ERROR_HOLD",
                "detail": str(exc),
                "source_head": None,
                "frontier_digest": None,
                "selected": None,
                "pareto_front": [],
                "residuals": [],
            }

    @staticmethod
    def _depth_policy(depth_mode: str | None, required_passes: list[str] | None) -> tuple[str, list[str]]:
        mode = str(depth_mode or "deep").lower()
        if mode not in DEPTH_MODES:
            raise ValueError("depth_mode must be standard or deep")
        passes = list(required_passes or DEPTH_MODES[mode])
        if not passes:
            raise ValueError("required_passes must not be empty")
        clean = []
        for raw in passes:
            value = _require_id(str(raw), "required_pass")
            if value not in clean:
                clean.append(value)
        return mode, clean

    @staticmethod
    def _completion_validate(completion: dict, required_passes: list[str]) -> dict:
        if not isinstance(completion, dict):
            raise ValueError("completion must be an object")
        status = str(completion.get("status") or "").upper()
        if status not in COMPLETION_STATES:
            raise ValueError(f"completion status must be one of {sorted(COMPLETION_STATES)}")
        if completion.get("observed") is not True:
            raise ValueError("cycle advancement requires observed=true")
        summary = str(completion.get("summary") or "").strip()
        if not summary:
            raise ValueError("completion summary is required")
        passes = completion.get("passes") or []
        if not isinstance(passes, list):
            raise ValueError("completion passes must be an array")
        seen = set()
        for row in passes:
            if not isinstance(row, dict):
                raise ValueError("each completion pass must be an object")
            kind = _require_id(str(row.get("kind") or ""), "pass kind")
            if not str(row.get("summary") or "").strip():
                raise ValueError(f"completion pass {kind} requires summary")
            seen.add(kind)
        if status in {"SUCCEEDED", "PARTIAL"}:
            missing = [x for x in required_passes if x not in seen]
            if missing:
                raise ValueError(f"completion missing required deliberation passes: {missing}")
        tests = completion.get("tests") or []
        if not isinstance(tests, list):
            raise ValueError("completion tests must be an array")
        for row in tests:
            if not isinstance(row, dict) or str(row.get("status") or "").upper() not in {"PASS", "FAIL", "SKIP", "HOLD"}:
                raise ValueError("test rows require status PASS, FAIL, SKIP, or HOLD")
        if completion.get("terminal") and status != "SUCCEEDED":
            raise ValueError("only SUCCEEDED completion may be terminal")
        return {**completion, "status": status, "summary": summary}

    @staticmethod
    def _compact(value: Any, max_chars: int) -> str:
        text = json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False)
        if len(text) <= max_chars:
            return text
        digest = _sha(value)
        return json.dumps({"truncated": True, "sha256": digest, "preview": text[: max(0, max_chars - 160)]}, indent=2, sort_keys=True, ensure_ascii=False)

    def _render_prompt(self, state: dict, context: dict, previous_completion: dict | None) -> str:
        max_chars = int(state["budget"]["max_prompt_chars"])
        step = int(state["step_index"])
        metadata = {
            "artifact": "ATHENA.REHYDRATION.PROMPT.V1",
            "loop_id": state["loop_id"],
            "step_index": step,
            "state_digest": state["state_digest"],
            "checkpoint_parent_head": state["checkpoint_parent_head"],
            "prompt_stack_digest": context["prompt"]["prompt_stack_digest"],
            "frontier_digest": context["frontier"].get("frontier_digest"),
            "required_passes": state["depth_policy"]["required_passes"],
        }
        frontier_view = {
            "status": context["frontier"].get("status"),
            "reason": context["frontier"].get("reason"),
            "selected": context["frontier"].get("selected"),
            "pareto_front": context["frontier"].get("pareto_front"),
            "residuals": context["frontier"].get("residuals"),
        }
        prompt = f"""<!-- ATHENA_REHYDRATION_PROMPT_V1
{json.dumps(metadata, indent=2, sort_keys=True, ensure_ascii=False)}
-->
# ATHENA Git Rehydration Loop — {state['loop_id']} / step {step}

## Exact coordinates

- checkpoint parent: `{state['checkpoint_parent_head']}`
- semantic prompt digest: `{context['prompt']['prompt_stack_digest']}`
- frontier digest: `{context['frontier'].get('frontier_digest')}`
- loop state digest: `{state['state_digest']}`
- chain digest before this cycle: `{state.get('previous_chain_digest')}`

## Goal

{state['goal']}

## Current bounded task

{state['task']}

## Previous observed completion

{self._compact(previous_completion or {'status': 'NONE'}, 3000)}

## Current frontier / residual geometry

{self._compact(frontier_view, 5000)}

## Required deliberation passes

{', '.join(state['depth_policy']['required_passes'])}

For every pass, return a non-empty summary and any evidence references. A required pass is an explicit work product, not a claim that hidden background thinking occurred.

## Cycle algorithm

1. Rehydrate from the exact coordinates above; do not rely on an older cached prompt or branch state.
2. Reconstruct the goal, previous receipt, current Git delta, frontier holds, and unresolved residuals.
3. Claim one bounded, lawful intervention that can be completed and committed in the present agent session.
4. Generate alternatives; attack the leading candidate; preserve ambiguity when evidence does not select one.
5. Execute the selected intervention with the available tools and authority only.
6. Observe tests and outputs. Prediction, intention, or simulation is not observation.
7. Commit the substantive work to Git. Do not edit this loop's state or prompt files manually.
8. Return the completion object below to `athena_rehydration_advance`; that tool will verify ancestry, persist a receipt, rehydrate the new head, and compile the next self-prompt.

## Stop conditions

{self._compact(state.get('stop_conditions') or [], 2000)}

## Completion contract

```json
{{
  "status": "SUCCEEDED | PARTIAL | HELD | FAILED | NO_PROGRESS",
  "observed": true,
  "terminal": false,
  "hard_hold": false,
  "summary": "what actually changed",
  "progress_delta": 1.0,
  "passes": [
    {{"kind": "reconstruct", "summary": "...", "evidence_refs": []}},
    {{"kind": "execute", "summary": "...", "evidence_refs": []}},
    {{"kind": "verify", "summary": "...", "evidence_refs": []}}
  ],
  "tests": [{{"name": "...", "status": "PASS", "evidence_ref": "..."}}],
  "evidence_refs": [],
  "residuals": [],
  "next_task": null,
  "handoff_to": null
}}
```

## Laws

- `CYCLE != BACKGROUND_EXECUTION`; each cycle is explicitly invoked and witnessed.
- `SELF_PROMPT != HIGHER_AUTHORITY`.
- `GIT_COMMIT != OBSERVED_SUCCESS` without tests/evidence.
- `LOCAL_COMMIT != SHARED_RETURN` unless remote publication is verified.
- `HEAD_CHANGE => REHYDRATE` before the next consequential decision.
- `REPEATED_NO_PROGRESS => HOLD`, not infinite self-prompt recursion.
- The agent must finish this bounded cycle before requesting the next one.
"""
        if len(prompt) > max_chars:
            raise ValueError(f"compiled self-prompt exceeds max_prompt_chars={max_chars}")
        return prompt

    def _context(
        self,
        *,
        task: str,
        profile: str | None,
        source_ref: str,
        remote: str,
        fetch: bool,
        use_frontier: bool,
    ) -> dict:
        prompt = self.prompt_runtime.compile(task=task, profile=profile, include_text=False)
        frontier = self._frontier_snapshot(
            task=task,
            profile=profile,
            source_ref=source_ref,
            remote=remote,
            fetch=fetch,
            use_frontier=use_frontier,
        )
        return {"prompt": prompt, "frontier": frontier}

    def _loop_id(self) -> str:
        return f"RHL-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}"

    def start(
        self,
        *,
        goal: str,
        expected_git_head: str,
        task: str = "",
        actor: str = "agent",
        profile: str | None = None,
        source_ref: str = DEFAULT_SOURCE_REF,
        remote: str = "origin",
        fetch: bool = True,
        use_frontier: bool = True,
        shared_remote_mode: str = "REQUIRED",
        max_steps: int = 64,
        max_no_progress: int = 3,
        max_prompt_chars: int = 32000,
        depth_mode: str = "deep",
        required_passes: list[str] | None = None,
        stop_conditions: list[str] | None = None,
    ) -> dict:
        goal = str(goal or "").strip()
        task = str(task or goal).strip()
        if not goal or not task:
            raise ValueError("goal and task are required")
        actor = _require_id(actor or "agent", "actor")
        mode = self._remote_mode(shared_remote_mode)
        max_steps = _bounded_int(max_steps, "max_steps", 1, 256)
        max_no_progress = _bounded_int(max_no_progress, "max_no_progress", 1, 16)
        max_prompt_chars = _bounded_int(max_prompt_chars, "max_prompt_chars", 8000, 120000)
        depth_mode, passes = self._depth_policy(depth_mode, required_passes)
        remote_sync = self._sync_before_write(mode, remote)
        current = self.git.head()
        if current != expected_git_head:
            raise GitStaleHead(json.dumps({"status": "STALE_GIT_HEAD", "expected": expected_git_head, "current": current}, sort_keys=True))

        loop_id = self._loop_id()
        paths = self._paths(loop_id)
        context = self._context(
            task=task,
            profile=profile,
            source_ref=source_ref,
            remote=remote,
            fetch=fetch,
            use_frontier=use_frontier,
        )
        prompt_path = f"{paths['prompts']}/0000.md"
        state = {
            "artifact": ARTIFACT,
            "loop_id": loop_id,
            "status": "ACTIVE",
            "goal": goal,
            "task": task,
            "actor": actor,
            "created_at": _utcnow(),
            "updated_at": _utcnow(),
            "step_index": 0,
            "checkpoint_parent_head": current,
            "base_head": current,
            "last_work_head": current,
            "profile": context["prompt"].get("profile"),
            "source": {"source_ref": source_ref, "remote": remote, "fetch": bool(fetch), "use_frontier": bool(use_frontier)},
            "budget": {"max_steps": max_steps, "max_no_progress": max_no_progress, "max_prompt_chars": max_prompt_chars},
            "depth_policy": {"mode": depth_mode, "required_passes": passes},
            "stop_conditions": list(stop_conditions or []),
            "no_progress_count": 0,
            "previous_chain_digest": None,
            "last_progress_fingerprint": None,
            "last_completion": None,
            "current_prompt_path": prompt_path,
            "prompt_stack_digest": context["prompt"]["prompt_stack_digest"],
            "frontier_digest": context["frontier"].get("frontier_digest"),
            "frontier_source_head": context["frontier"].get("source_head"),
            "frontier_status": context["frontier"].get("status"),
            "receipt_paths": [],
        }
        state["state_digest"] = _state_digest(state)
        prompt_text = self._render_prompt(state, context, None)
        state["current_prompt_digest"] = _sha(prompt_text)
        state["chain_digest"] = _sha({"kind": "START", "previous": None, "state_digest": state["state_digest"], "prompt_digest": state["current_prompt_digest"]})
        event = {
            "artifact": "ATHENA.REHYDRATION.EVENT.V1",
            "event_type": "LOOP_STARTED",
            "loop_id": loop_id,
            "step_index": 0,
            "actor": actor,
            "created_at": _utcnow(),
            "checkpoint_parent_head": current,
            "state_digest": state["state_digest"],
            "prompt_path": prompt_path,
            "prompt_digest": state["current_prompt_digest"],
            "chain_digest": state["chain_digest"],
        }
        files = {
            paths["state"]: json.dumps(state, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            prompt_path: prompt_text,
            f"{paths['events']}/0000-start.json": json.dumps(event, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        }
        git_result = self.prompt_runtime._commit_files(current, files, actor, f"start rehydration loop {loop_id}")
        publish = self._publish_after_write(mode, remote, git_result["head"])
        return {
            "status": "STARTED",
            "loop_id": loop_id,
            "step_index": 0,
            "checkpoint_head": git_result["head"],
            "state_digest": state["state_digest"],
            "prompt_digest": state["current_prompt_digest"],
            "chain_digest": state["chain_digest"],
            "prompt_path": prompt_path,
            "compiled_self_prompt": prompt_text,
            "git": git_result,
            "remote_sync": remote_sync,
            "remote_publish": publish,
            "durable_return": bool(publish.get("shared_frontier_verified")) if mode != "DISABLED" else False,
            "law": "STARTED_LOOP != BACKGROUND_EXECUTION; invoke each explicit cycle",
        }

    def advance(
        self,
        *,
        loop_id: str,
        expected_checkpoint_head: str,
        expected_state_digest: str,
        expected_prompt_digest: str,
        completion: dict,
        actor: str = "agent",
        allow_no_git_change: bool = False,
        shared_remote_mode: str = "REQUIRED",
        remote: str | None = None,
    ) -> dict:
        loop_id = _require_id(loop_id, "loop_id")
        actor = _require_id(actor or "agent", "actor")
        state, paths = self._read_state(loop_id)
        if state.get("status") in TERMINAL_STATES:
            raise ValueError(f"rehydration loop is terminal: {state.get('status')}")
        if _state_digest(state) != state.get("state_digest") or state.get("state_digest") != expected_state_digest:
            raise GitStateError("STALE_OR_TAMPERED_REHYDRATION_STATE")
        prompt_path = state["current_prompt_path"]
        prompt_text = self._loop_prompt_path(paths, prompt_path).read_text(encoding="utf-8")
        actual_prompt_digest = _sha(prompt_text)
        if actual_prompt_digest != state.get("current_prompt_digest") or actual_prompt_digest != expected_prompt_digest:
            raise GitStateError("STALE_OR_TAMPERED_REHYDRATION_PROMPT")
        checkpoint_head = self._path_last_commit(paths["state"])
        if checkpoint_head != expected_checkpoint_head:
            raise GitStaleHead(json.dumps({"status": "STALE_LOOP_CHECKPOINT", "expected": expected_checkpoint_head, "current": checkpoint_head}, sort_keys=True))
        current_work_head = self.git.head()
        if not self._is_ancestor(expected_checkpoint_head, current_work_head):
            raise GitStaleHead(json.dumps({"status": "FORKED_LOOP_HEAD", "checkpoint": expected_checkpoint_head, "current": current_work_head}, sort_keys=True))
        if current_work_head == expected_checkpoint_head and not allow_no_git_change:
            raise ValueError("advance requires a substantive Git commit after the current self-prompt")

        completion = self._completion_validate(completion, list(state["depth_policy"]["required_passes"]))
        remote = remote or state["source"].get("remote") or "origin"
        mode = self._remote_mode(shared_remote_mode)
        remote_sync = self._sync_before_write(mode, remote)
        current_work_head = self.git.head()
        if not self._is_ancestor(expected_checkpoint_head, current_work_head):
            raise GitStaleHead("shared sync produced non-descendant loop state")
        if self._path_last_commit(paths["state"]) != expected_checkpoint_head:
            raise GitStaleHead("shared sync revealed a newer loop checkpoint; resume first")

        changed_paths = self._changed_paths(expected_checkpoint_head, current_work_head)
        material_work_paths = [p for p in changed_paths if not p.startswith(paths["base"] + "/")]
        context = self._context(
            task=str(completion.get("next_task") or state["task"]),
            profile=state.get("profile"),
            source_ref=state["source"].get("source_ref") or DEFAULT_SOURCE_REF,
            remote=remote,
            fetch=bool(state["source"].get("fetch", True)),
            use_frontier=bool(state["source"].get("use_frontier", True)),
        )
        progress_fingerprint = _sha({
            "material_work_paths": material_work_paths,
            "summary": completion["summary"],
            "evidence_refs": completion.get("evidence_refs") or [],
            "tests": completion.get("tests") or [],
            "residuals": completion.get("residuals") or [],
            "prompt_stack_digest": context["prompt"]["prompt_stack_digest"],
            "frontier_digest": context["frontier"].get("frontier_digest"),
        })
        progress_delta = float(completion.get("progress_delta", 0.0) or 0.0)
        no_progress = (
            completion["status"] == "NO_PROGRESS"
            or progress_delta <= 0
            or (not material_work_paths and not completion.get("evidence_refs"))
            or progress_fingerprint == state.get("last_progress_fingerprint")
        )
        no_progress_count = int(state.get("no_progress_count") or 0) + 1 if no_progress else 0
        next_step = int(state["step_index"]) + 1
        terminal = bool(completion.get("terminal"))
        if terminal:
            next_status = "COMPLETE"
        elif next_step >= int(state["budget"]["max_steps"]):
            next_status = "HOLD_MAX_STEPS"
        elif no_progress_count >= int(state["budget"]["max_no_progress"]):
            next_status = "HOLD_NO_PROGRESS"
        elif completion.get("hard_hold"):
            next_status = "ABORTED" if completion["status"] == "FAILED" else "HOLD_NO_PROGRESS"
        else:
            next_status = "ACTIVE"

        next_prompt_path = f"{paths['prompts']}/{next_step:04d}.md"
        next_task = str(completion.get("next_task") or state["task"]).strip()
        new_state = {
            **state,
            "status": next_status,
            "task": next_task,
            "actor": actor,
            "updated_at": _utcnow(),
            "step_index": next_step,
            "checkpoint_parent_head": current_work_head,
            "last_work_head": current_work_head,
            "no_progress_count": no_progress_count,
            "previous_chain_digest": state.get("chain_digest"),
            "last_progress_fingerprint": progress_fingerprint,
            "last_completion": completion,
            "current_prompt_path": next_prompt_path,
            "prompt_stack_digest": context["prompt"]["prompt_stack_digest"],
            "frontier_digest": context["frontier"].get("frontier_digest"),
            "frontier_source_head": context["frontier"].get("source_head"),
            "frontier_status": context["frontier"].get("status"),
        }
        receipt_path = f"{paths['receipts']}/{next_step:04d}.json"
        new_state["receipt_paths"] = list(state.get("receipt_paths") or []) + [receipt_path]
        new_state["state_digest"] = _state_digest(new_state)
        next_prompt = self._render_prompt(new_state, context, completion)
        new_state["current_prompt_digest"] = _sha(next_prompt)

        receipt = {
            "artifact": "ATHENA.REHYDRATION.RECEIPT.V1",
            "loop_id": loop_id,
            "step_index": next_step,
            "actor": actor,
            "created_at": _utcnow(),
            "expected_checkpoint_head": expected_checkpoint_head,
            "work_head": current_work_head,
            "changed_paths": changed_paths,
            "material_work_paths": material_work_paths,
            "completion": completion,
            "previous_state_digest": state["state_digest"],
            "previous_prompt_digest": state["current_prompt_digest"],
            "previous_chain_digest": state["chain_digest"],
            "state_digest": new_state["state_digest"],
            "prompt_path": next_prompt_path,
            "prompt_digest": new_state["current_prompt_digest"],
            "progress_fingerprint": progress_fingerprint,
            "no_progress": no_progress,
            "next_status": next_status,
            "prompt_stack_digest": context["prompt"]["prompt_stack_digest"],
            "frontier_digest": context["frontier"].get("frontier_digest"),
        }
        receipt["receipt_digest"] = _record_digest(receipt, {"receipt_digest", "chain_digest"})
        new_state["chain_digest"] = _sha({
            "kind": "ADVANCE",
            "previous": state["chain_digest"],
            "state_digest": new_state["state_digest"],
            "prompt_digest": new_state["current_prompt_digest"],
            "receipt_digest": receipt["receipt_digest"],
        })
        receipt["chain_digest"] = new_state["chain_digest"]
        files = {
            paths["state"]: json.dumps(new_state, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            next_prompt_path: next_prompt,
            receipt_path: json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        }
        git_result = self.prompt_runtime._commit_files(current_work_head, files, actor, f"advance rehydration loop {loop_id} step {next_step}")
        publish = self._publish_after_write(mode, remote, git_result["head"])
        return {
            "status": next_status,
            "loop_id": loop_id,
            "step_index": next_step,
            "checkpoint_head": git_result["head"],
            "state_digest": new_state["state_digest"],
            "prompt_digest": new_state["current_prompt_digest"],
            "chain_digest": new_state["chain_digest"],
            "prompt_path": next_prompt_path,
            "compiled_self_prompt": next_prompt,
            "receipt_path": receipt_path,
            "receipt_digest": receipt["receipt_digest"],
            "changed_paths": changed_paths,
            "material_work_paths": material_work_paths,
            "no_progress_count": no_progress_count,
            "git": git_result,
            "remote_sync": remote_sync,
            "remote_publish": publish,
            "durable_return": bool(publish.get("shared_frontier_verified")) if mode != "DISABLED" else False,
            "terminal": next_status in TERMINAL_STATES,
        }

    def resume(self, loop_id: str, include_prompt: bool = True) -> dict:
        loop_id = _require_id(loop_id, "loop_id")
        state, paths = self._read_state(loop_id)
        prompt_path = state["current_prompt_path"]
        prompt_text = self._loop_prompt_path(paths, prompt_path).read_text(encoding="utf-8")
        state_ok = _state_digest(state) == state.get("state_digest")
        prompt_ok = _sha(prompt_text) == state.get("current_prompt_digest")
        checkpoint_head = self._path_last_commit(paths["state"])
        current_head = self.git.head()
        result = {
            "status": "RESUMED" if state_ok and prompt_ok else "INTEGRITY_HOLD",
            "loop_id": loop_id,
            "loop_status": state.get("status"),
            "step_index": state.get("step_index"),
            "checkpoint_head": checkpoint_head,
            "current_git_head": current_head,
            "work_head_ahead": bool(checkpoint_head and current_head != checkpoint_head and self._is_ancestor(checkpoint_head, current_head)),
            "state_digest": state.get("state_digest"),
            "prompt_digest": state.get("current_prompt_digest"),
            "chain_digest": state.get("chain_digest"),
            "prompt_path": prompt_path,
            "state_integrity": state_ok,
            "prompt_integrity": prompt_ok,
            "task": state.get("task"),
            "goal": state.get("goal"),
            "required_passes": (state.get("depth_policy") or {}).get("required_passes") or [],
        }
        if include_prompt:
            result["compiled_self_prompt"] = prompt_text
        return result

    def verify(self, loop_id: str) -> dict:
        loop_id = _require_id(loop_id, "loop_id")
        state, paths = self._read_state(loop_id)
        failures: list[str] = []
        if _state_digest(state) != state.get("state_digest"):
            failures.append("STATE_DIGEST")

        prompts_dir = self._safe_rel(paths["prompts"])
        receipts_dir = self._safe_rel(paths["receipts"])
        prompt_files = sorted(prompts_dir.glob("*.md")) if prompts_dir.is_dir() else []
        receipt_files = sorted(receipts_dir.glob("*.json")) if receipts_dir.is_dir() else []
        event_path = self._safe_rel(f"{paths['events']}/0000-start.json")
        chain = None
        previous_state_digest = None

        if not event_path.is_file():
            failures.append("START_EVENT_MISSING")
        else:
            try:
                event = json.loads(event_path.read_text(encoding="utf-8"))
                if event.get("artifact") != "ATHENA.REHYDRATION.EVENT.V1" or event.get("loop_id") != loop_id or int(event.get("step_index", -1)) != 0:
                    failures.append("START_EVENT_IDENTITY")
                first_prompt = self._loop_prompt_path(paths, event.get("prompt_path"), "0000.md")
                if not first_prompt.is_file() or _sha(first_prompt.read_text(encoding="utf-8")) != event.get("prompt_digest"):
                    failures.append("START_PROMPT_DIGEST")
                chain = _sha({"kind": "START", "previous": None, "state_digest": event.get("state_digest"), "prompt_digest": event.get("prompt_digest")})
                previous_state_digest = event.get("state_digest")
                if chain != event.get("chain_digest"):
                    failures.append("START_CHAIN")
            except Exception as exc:
                failures.append(f"START_EVENT_INVALID:{type(exc).__name__}")

        expected_step = 1
        indexed_receipts = []
        for path in receipt_files:
            indexed_receipts.append(str(path.relative_to(self._root())))
            try:
                receipt = json.loads(path.read_text(encoding="utf-8"))
                if receipt.get("artifact") != "ATHENA.REHYDRATION.RECEIPT.V1" or receipt.get("loop_id") != loop_id:
                    failures.append(f"RECEIPT_IDENTITY:{path.name}")
                if int(receipt.get("step_index", -1)) != expected_step or path.name != f"{expected_step:04d}.json":
                    failures.append(f"RECEIPT_SEQUENCE:{path.name}")
                if receipt.get("previous_state_digest") != previous_state_digest:
                    failures.append(f"STATE_PREVIOUS:{path.name}")
                pd = _record_digest(receipt, {"receipt_digest", "chain_digest"})
                if pd != receipt.get("receipt_digest"):
                    failures.append(f"RECEIPT_DIGEST:{path.name}")
                prompt = self._loop_prompt_path(paths, receipt.get("prompt_path"), f"{expected_step:04d}.md")
                if not prompt.is_file() or _sha(prompt.read_text(encoding="utf-8")) != receipt.get("prompt_digest"):
                    failures.append(f"PROMPT_DIGEST:{path.name}")
                if receipt.get("previous_chain_digest") != chain:
                    failures.append(f"CHAIN_PREVIOUS:{path.name}")
                chain = _sha({
                    "kind": "ADVANCE",
                    "previous": receipt.get("previous_chain_digest"),
                    "state_digest": receipt.get("state_digest"),
                    "prompt_digest": receipt.get("prompt_digest"),
                    "receipt_digest": receipt.get("receipt_digest"),
                })
                if chain != receipt.get("chain_digest"):
                    failures.append(f"CHAIN_DIGEST:{path.name}")
                older = receipt.get("expected_checkpoint_head")
                newer = receipt.get("work_head")
                if not older or not newer or not self._is_ancestor(older, newer):
                    failures.append(f"GIT_ANCESTRY:{path.name}")
                previous_state_digest = receipt.get("state_digest")
            except Exception as exc:
                failures.append(f"RECEIPT_INVALID:{path.name}:{type(exc).__name__}")
            expected_step += 1

        if int(state.get("step_index") or 0) != len(receipt_files):
            failures.append("STATE_STEP_COUNT")
        if state.get("chain_digest") != chain:
            failures.append("STATE_CHAIN")
        if state.get("state_digest") != previous_state_digest:
            failures.append("STATE_TIP_DIGEST")
        if len(prompt_files) != len(receipt_files) + 1:
            failures.append("PROMPT_COUNT")
        expected_current_name = f"{int(state.get('step_index') or 0):04d}.md"
        try:
            current_prompt = self._loop_prompt_path(paths, state.get("current_prompt_path"), expected_current_name)
            if not current_prompt.is_file() or _sha(current_prompt.read_text(encoding="utf-8")) != state.get("current_prompt_digest"):
                failures.append("STATE_PROMPT_DIGEST")
        except Exception:
            failures.append("STATE_PROMPT_PATH")
        if list(state.get("receipt_paths") or []) != indexed_receipts:
            failures.append("RECEIPT_INDEX")
        return {
            "status": "PASS" if not failures else "HOLD",
            "loop_id": loop_id,
            "failures": failures,
            "step_count": len(receipt_files),
            "prompt_count": len(prompt_files),
            "chain_digest": chain,
            "state_chain_digest": state.get("chain_digest"),
            "checkpoint_head": self._path_last_commit(paths["state"]),
            "laws": [
                "LOOP_CHAIN != WORLD_TRUTH",
                "PASS verifies persisted causal integrity and Git ancestry only",
            ],
        }

    def index(self) -> dict:
        root = self._safe_rel(LOOP_ROOT)
        loops = []
        if root.is_dir():
            for path in sorted(root.iterdir()):
                if not path.is_dir() or not (path / "state.json").is_file():
                    continue
                try:
                    state = json.loads((path / "state.json").read_text(encoding="utf-8"))
                    loops.append({
                        "loop_id": state.get("loop_id"),
                        "status": state.get("status"),
                        "step_index": state.get("step_index"),
                        "goal": state.get("goal"),
                        "task": state.get("task"),
                        "updated_at": state.get("updated_at"),
                        "state_digest": state.get("state_digest"),
                        "chain_digest": state.get("chain_digest"),
                        "checkpoint_head": self._path_last_commit(str((path / "state.json").relative_to(self._root()))),
                    })
                except Exception as exc:
                    loops.append({"loop_id": path.name, "status": "INDEX_ERROR_HOLD", "detail": str(exc)})
        return {"status": "OK", "count": len(loops), "loops": loops, "artifact": ARTIFACT}

    def call_tool(self, name: str, a: dict):
        try:
            if name == "athena_rehydration_start":
                return self.start(
                    goal=a["goal"], expected_git_head=a["expected_git_head"], task=a.get("task", ""),
                    actor=a.get("actor", "agent"), profile=a.get("profile"), source_ref=a.get("source_ref", DEFAULT_SOURCE_REF),
                    remote=a.get("remote", "origin"), fetch=a.get("fetch", True), use_frontier=a.get("use_frontier", True),
                    shared_remote_mode=a.get("shared_remote_mode", "REQUIRED"), max_steps=a.get("max_steps", 64),
                    max_no_progress=a.get("max_no_progress", 3), max_prompt_chars=a.get("max_prompt_chars", 32000),
                    depth_mode=a.get("depth_mode", "deep"), required_passes=a.get("required_passes"),
                    stop_conditions=a.get("stop_conditions") or [],
                )
            if name == "athena_rehydration_advance":
                return self.advance(
                    loop_id=a["loop_id"], expected_checkpoint_head=a["expected_checkpoint_head"],
                    expected_state_digest=a["expected_state_digest"], expected_prompt_digest=a["expected_prompt_digest"],
                    completion=a["completion"], actor=a.get("actor", "agent"),
                    allow_no_git_change=a.get("allow_no_git_change", False),
                    shared_remote_mode=a.get("shared_remote_mode", "REQUIRED"), remote=a.get("remote"),
                )
            if name == "athena_rehydration_resume":
                return self.resume(a["loop_id"], a.get("include_prompt", True))
            if name == "athena_rehydration_verify":
                return self.verify(a["loop_id"])
            if name == "athena_rehydration_index":
                return self.index()
            raise KeyError(name)
        except GitStaleHead:
            raise
        except GitStateError as exc:
            try:
                detail = json.loads(str(exc))
            except (TypeError, json.JSONDecodeError):
                detail = {"status": "GIT_STATE_HOLD", "detail": str(exc)}
            return {
                "status": detail.get("status", "GIT_STATE_HOLD"),
                "detail": detail,
                "durable_return": False,
                "law": "GIT_STATE_HOLD != INTERNAL_ERROR",
            }


_COMPLETION_SCHEMA = {
    "type": "object",
    "required": ["status", "observed", "summary", "passes"],
    "properties": {
        "status": {"type": "string", "enum": sorted(COMPLETION_STATES)},
        "observed": {"type": "boolean"},
        "terminal": {"type": "boolean"},
        "hard_hold": {"type": "boolean"},
        "summary": {"type": "string"},
        "progress_delta": {"type": "number"},
        "passes": {"type": "array", "items": {"type": "object"}},
        "tests": {"type": "array", "items": {"type": "object"}},
        "evidence_refs": {"type": "array", "items": {"type": "string"}},
        "residuals": {"type": "array"},
        "next_task": {"type": ["string", "null"]},
        "handoff_to": {"type": ["string", "null"]},
    },
    "additionalProperties": True,
}

REHYDRATION_TOOLS = [
    {
        "name": "athena_rehydration_start",
        "description": "Start a Git-persisted explicit rehydration loop, compile the first bounded self-prompt, and checkpoint exact prompt/frontier/state coordinates. This creates no background execution.",
        "inputSchema": {
            "type": "object",
            "required": ["goal", "expected_git_head"],
            "properties": {
                "goal": {"type": "string"}, "task": {"type": "string"}, "expected_git_head": {"type": "string"},
                "actor": {"type": "string"}, "profile": {"type": ["string", "null"]}, "source_ref": {"type": "string"},
                "remote": {"type": "string"}, "fetch": {"type": "boolean"}, "use_frontier": {"type": "boolean"},
                "shared_remote_mode": {"type": "string", "enum": ["REQUIRED", "BEST_EFFORT", "DISABLED"]},
                "max_steps": {"type": "integer", "minimum": 1, "maximum": 256},
                "max_no_progress": {"type": "integer", "minimum": 1, "maximum": 16},
                "max_prompt_chars": {"type": "integer", "minimum": 8000, "maximum": 120000},
                "depth_mode": {"type": "string", "enum": ["standard", "deep"]},
                "required_passes": {"type": "array", "items": {"type": "string"}},
                "stop_conditions": {"type": "array", "items": {"type": "string"}},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_rehydration_advance",
        "description": "After an agent completes the current self-prompt and commits substantive work, verify exact checkpoint ancestry and observed pass receipts, persist the cycle, rehydrate the new Git head, and compile the next self-prompt.",
        "inputSchema": {
            "type": "object",
            "required": ["loop_id", "expected_checkpoint_head", "expected_state_digest", "expected_prompt_digest", "completion"],
            "properties": {
                "loop_id": {"type": "string"}, "expected_checkpoint_head": {"type": "string"},
                "expected_state_digest": {"type": "string"}, "expected_prompt_digest": {"type": "string"},
                "completion": _COMPLETION_SCHEMA, "actor": {"type": "string"},
                "allow_no_git_change": {"type": "boolean"},
                "shared_remote_mode": {"type": "string", "enum": ["REQUIRED", "BEST_EFFORT", "DISABLED"]},
                "remote": {"type": ["string", "null"]},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_rehydration_resume",
        "description": "Resume a persisted rehydration loop at its exact current prompt/state/chain coordinates; another agent can use this as the handoff packet.",
        "inputSchema": {"type": "object", "required": ["loop_id"], "properties": {"loop_id": {"type": "string"}, "include_prompt": {"type": "boolean"}}, "additionalProperties": False},
    },
    {
        "name": "athena_rehydration_verify",
        "description": "Replay and verify the persisted loop chain, prompt/receipt digests, sequential steps, and Git ancestry. PASS is causal-integrity evidence, not world-truth authority.",
        "inputSchema": {"type": "object", "required": ["loop_id"], "properties": {"loop_id": {"type": "string"}}, "additionalProperties": False},
    },
    {
        "name": "athena_rehydration_index",
        "description": "List Git-persisted rehydration loops and their current status, step, state/chain digests, and checkpoint head.",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
]
REHYDRATION_TOOL_NAMES = {x["name"] for x in REHYDRATION_TOOLS}
REHYDRATION_WRITE_TOOL_NAMES = {"athena_rehydration_start", "athena_rehydration_advance"}
