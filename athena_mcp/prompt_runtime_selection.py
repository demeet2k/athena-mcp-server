from __future__ import annotations

import subprocess
from contextvars import ContextVar
from typing import Any, Dict, Mapping, Sequence

from .git_backend import GitStaleHead
from .prompt_runtime_types import (
    PROMPT_RUNTIME_VERSION,
    PromptRuntimeError,
    canonical_json,
    nonempty as _nonempty,
    sha256_text,
    string_list as _string_list,
)


class PromptRuntimeSelectionMixin:
    """Task-sensitive composition plus exact-head freshness/invalidation routing."""

    _task_selector: ContextVar[str] = ContextVar("athena_prompt_task_selector", default="")
    _selection_report: ContextVar[Dict[str, Any] | None] = ContextVar(
        "athena_prompt_selection_report", default=None
    )

    @staticmethod
    def _normalize_task(task: str | None) -> str:
        return _nonempty(task, "task") if task is not None else ""

    def _with_selection_context(self, task: str | None):
        task_text = self._normalize_task(task)
        task_token = self._task_selector.set(task_text)
        report_token = self._selection_report.set(None)
        return task_text, task_token, report_token

    def _finish_selection_context(self, task_token, report_token) -> None:
        self._selection_report.reset(report_token)
        self._task_selector.reset(task_token)

    def hydrate(
        self,
        *,
        profile: str | None = None,
        scope: Sequence[str] | None = None,
        include_text: bool = False,
        since_git_head: str | None = None,
        task: str | None = None,
    ) -> Dict[str, Any]:
        task_text, task_token, report_token = self._with_selection_context(task)
        try:
            result = super().hydrate(
                profile=profile,
                scope=scope,
                include_text=include_text,
                since_git_head=since_git_head,
            )
            result["task_selector"] = {
                "task": task_text or None,
                "task_digest": sha256_text(task_text) if task_text else None,
            }
            result["selection"] = self._selection_report.get() or {}
            result["frontier_refs"] = self._frontier_refs(result["git"]["head"])
            return result
        finally:
            self._finish_selection_context(task_token, report_token)

    def compile(
        self,
        *,
        profile: str | None = None,
        scope: Sequence[str] | None = None,
        task_overlay: str | None = None,
        since_git_head: str | None = None,
        task: str | None = None,
    ) -> Dict[str, Any]:
        task_text, task_token, report_token = self._with_selection_context(task)
        try:
            result = super().compile(
                profile=profile,
                scope=scope,
                task_overlay=task_overlay,
                since_git_head=since_git_head,
            )
            result["task_selector"] = {
                "task": task_text or None,
                "task_digest": sha256_text(task_text) if task_text else None,
            }
            result["selection"] = self._selection_report.get() or {}
            result["frontier_refs"] = self._frontier_refs(result["git"]["head"])
            return result
        finally:
            self._finish_selection_context(task_token, report_token)

    def _selected_modules(
        self,
        manifest: Mapping[str, Any],
        active: Mapping[str, Any],
        profile_override: str | None,
    ) -> tuple[str, list[tuple[str, Mapping[str, Any]]]]:
        profiles = manifest["profiles"]
        modules = manifest["modules"]
        profile = str(
            profile_override
            or active.get("profile")
            or manifest.get("default_profile")
            or ""
        ).strip()
        if profile not in profiles:
            raise PromptRuntimeError(f"unknown prompt profile {profile!r}")

        selected_raw = (
            profiles[profile]
            if profile_override is not None
            else active.get("enabled_modules", profiles[profile])
        )
        selected = _string_list(selected_raw, "enabled_modules")
        reasons: Dict[str, set[str]] = {
            module_id: {"PROFILE" if profile_override is not None else "ACTIVE_STATE"}
            for module_id in selected
        }

        for module_id, spec in modules.items():
            if not isinstance(spec, dict):
                raise PromptRuntimeError(f"module specification {module_id!r} must be an object")
            if spec.get("mandatory"):
                if module_id not in selected:
                    selected.append(module_id)
                reasons.setdefault(module_id, set()).add("MANDATORY")

        task = self._task_selector.get()
        selector_matches: list[Dict[str, str]] = []
        if task:
            folded = task.casefold()
            for module_id, spec in modules.items():
                selectors = _string_list(spec.get("selectors", []), f"modules.{module_id}.selectors")
                matches = [selector for selector in selectors if selector.casefold() in folded]
                if not matches:
                    continue
                if module_id not in selected:
                    selected.append(module_id)
                for selector in matches:
                    reasons.setdefault(module_id, set()).add(f"SELECTOR:{selector}")
                    selector_matches.append({"module_id": module_id, "selector": selector})

        unknown = sorted(set(selected) - set(modules))
        if unknown:
            raise PromptRuntimeError(f"active prompt state selects unknown modules: {unknown}")

        dependency_edges: list[Dict[str, str]] = []
        state: Dict[str, int] = {}

        def visit(module_id: str, chain: tuple[str, ...]) -> None:
            marker = state.get(module_id, 0)
            if marker == 2:
                return
            if marker == 1:
                raise PromptRuntimeError(
                    canonical_json(
                        {
                            "status": "PROMPT_DEPENDENCY_CYCLE",
                            "cycle": [*chain, module_id],
                        }
                    )
                )
            state[module_id] = 1
            spec = modules[module_id]
            dependencies = _string_list(
                spec.get("depends_on", []), f"modules.{module_id}.depends_on"
            )
            for dependency in dependencies:
                if dependency not in modules:
                    raise PromptRuntimeError(
                        f"module {module_id!r} depends on unknown module {dependency!r}"
                    )
                if dependency not in selected:
                    selected.append(dependency)
                reasons.setdefault(dependency, set()).add(f"DEPENDENCY_OF:{module_id}")
                dependency_edges.append({"module_id": module_id, "depends_on": dependency})
                visit(dependency, (*chain, module_id))
            state[module_id] = 2

        for module_id in list(selected):
            visit(module_id, ())

        order_slots: Dict[int, str] = {}
        ordered: list[tuple[str, Mapping[str, Any]]] = []
        for module_id in selected:
            spec = modules[module_id]
            if not isinstance(spec.get("path"), str) or not spec["path"].strip():
                raise PromptRuntimeError(f"module {module_id!r} has no valid path")
            order = int(spec.get("order", 0))
            prior = order_slots.get(order)
            if prior is not None and prior != module_id:
                raise PromptRuntimeError(
                    canonical_json(
                        {
                            "status": "PROMPT_ORDER_CONFLICT",
                            "order": order,
                            "modules": sorted([prior, module_id]),
                            "law": "same-level modules require distinct manifest order or an explicit future adjudication contract",
                        }
                    )
                )
            order_slots[order] = module_id
            ordered.append((module_id, spec))
        ordered.sort(key=lambda row: (int(row[1].get("order", 0)), row[0]))

        report = {
            "profile": profile,
            "task": task or None,
            "selected_modules": [module_id for module_id, _ in ordered],
            "selection_reasons": {
                module_id: sorted(reasons.get(module_id, {"UNSPECIFIED"}))
                for module_id, _ in ordered
            },
            "selector_matches": sorted(
                selector_matches, key=lambda row: (row["module_id"], row["selector"])
            ),
            "dependency_edges": sorted(
                dependency_edges, key=lambda row: (row["module_id"], row["depends_on"])
            ),
            "order": [
                {"module_id": module_id, "order": int(spec.get("order", 0))}
                for module_id, spec in ordered
            ],
        }
        self._selection_report.set(report)
        return profile, ordered

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
            "registry",
            "goals",
            "pressures",
            "tasks",
            "workorders",
            "work_orders",
        )
        files = []
        for line in raw.splitlines():
            if not line.strip():
                continue
            parts = line.split("\t")
            files.append({"status": parts[0], "paths": parts[1:]})
        return {"since": since, "relation": relation, "files": files}

    def _frontier_refs(self, expected_head: str) -> Dict[str, Any]:
        before = self._head()
        if before != expected_head:
            raise GitStaleHead(
                canonical_json(
                    {
                        "status": "STALE_GIT_HEAD_DURING_FRONTIER_READ",
                        "expected": expected_head,
                        "current": before,
                    }
                )
            )
        manifest, _ = self._manifest()
        active, _ = self._active_state(manifest)

        declared_keys = {
            "goals": ("goal_refs", "goals"),
            "pressures": ("pressure_refs", "pressures"),
            "work": ("work_refs", "work_orders", "workorder_refs"),
        }
        result: Dict[str, Any] = {}
        declared = False
        for output_key, keys in declared_keys.items():
            value = None
            source_key = None
            for key in keys:
                if key in active:
                    value = active[key]
                    source_key = key
                    declared = True
                    break
            refs = _string_list(value or [], f"active_state.{source_key or output_key}")
            result[output_key] = refs
            result[f"{output_key}_source"] = source_key
        after = self._head()
        if after != expected_head:
            raise GitStaleHead(
                canonical_json(
                    {
                        "status": "STALE_GIT_HEAD_DURING_FRONTIER_READ",
                        "expected": expected_head,
                        "current": after,
                    }
                )
            )
        result["status"] = "DECLARED" if declared else "UNDECLARED"
        result["law"] = (
            "Only explicit active-state references are returned; missing declarations remain visible as UNDECLARED rather than inferred from filenames."
        )
        return result

    def freshness(self, *, last_git_head: str) -> Dict[str, Any]:
        self._require_clean()
        current = self._head()
        changed = self._changed_prompt_files(last_git_head, current)
        material_paths = [path for row in changed["files"] for path in row["paths"]]
        categories = set()
        for path in material_paths:
            if path == "AGENTS.md" or path.startswith(("prompts/", "policies/", "schemas/", "registry/")):
                categories.add("PROMPT_RUNTIME")
            if path.startswith(("goals/", "pressures/", "tasks/", "workorders/", "work_orders/")):
                categories.add("FRONTIER")
        rehydration_required = changed["relation"] != "ANCESTOR" or bool(material_paths)
        after = self._head()
        if after != current:
            raise GitStaleHead(
                canonical_json(
                    {
                        "status": "STALE_GIT_HEAD_DURING_FRESHNESS_CHECK",
                        "expected": current,
                        "current": after,
                    }
                )
            )
        self._require_clean()
        return {
            "version": PROMPT_RUNTIME_VERSION,
            "status": "STALE" if rehydration_required else "FRESH",
            "last_git_head": last_git_head,
            "current_git_head": current,
            "relation": changed["relation"],
            "changed_files": changed["files"],
            "material_categories": sorted(categories),
            "rehydration_required": rehydration_required,
            "affected_scope": ["*"] if "PROMPT_RUNTIME" in categories else sorted(categories),
            "law": (
                "A material prompt/frontier change requires rehydration before the next consequential action; freshness detection does not authorize mutation."
            ),
        }
