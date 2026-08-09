from __future__ import annotations

import ast
import fnmatch
import hashlib
import json
import re
from pathlib import PurePosixPath
from typing import Any, Iterable, Mapping

from .git_backend import GitBackend, GitStateError

VERSION = "ATHENA.FRESHNESS.TRAIN.1"

ALIGNED = "ALIGNED"
DISJOINT_BATCHABLE = "DISJOINT_BATCHABLE"
DEPENDENCY_REQUALIFY = "DEPENDENCY_REQUALIFY"
OWNED_PATH_CONFLICT = "OWNED_PATH_CONFLICT"
UNKNOWN_HOLD = "UNKNOWN_HOLD"
MOVING_FRONTIER_HOLD = "MOVING_FRONTIER_HOLD"

DEFAULT_CRITICAL_PATTERNS = (
    ".github/workflows/ci.yml",
    "pyproject.toml",
    "athena_mcp/__init__.py",
    "athena_mcp/server.py",
    "athena_mcp/aor_collective_transport_surface.py",
)

_SHA_RE = re.compile(r"^[0-9a-fA-F]{7,40}$")


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _normalize_path(value: Any) -> str:
    text = str(value or "").strip().replace("\\", "/")
    while text.startswith("./"):
        text = text[2:]
    return text.rstrip("/")


def _patterns(values: Iterable[Any] | None) -> tuple[str, ...]:
    return tuple(sorted({_normalize_path(value) for value in (values or []) if _normalize_path(value)}))


def _matches(path: str, pattern: str) -> bool:
    path = _normalize_path(path)
    pattern = _normalize_path(pattern)
    if any(char in pattern for char in "*?["):
        return fnmatch.fnmatchcase(path, pattern)
    return path == pattern or path.startswith(pattern + "/")


def _matched(paths: Iterable[str], patterns: Iterable[str]) -> list[str]:
    pats = tuple(patterns)
    return sorted({path for path in paths if any(_matches(path, pattern) for pattern in pats)})


def _git_ok(git: GitBackend, *args: str) -> tuple[bool, str]:
    try:
        return True, git._git(*args)
    except GitStateError as exc:
        return False, str(exc)


def _verify_commit(git: GitBackend, ref: str) -> str:
    ref = str(ref or "").strip()
    if not ref:
        raise ValueError("git ref must be non-empty")
    # Named refs are allowed for local inspection; SHA-like values are normalized
    # only after git has resolved them.
    return git._git("rev-parse", "--verify", f"{ref}^{{commit}}")


def _is_ancestor(git: GitBackend, older: str, newer: str) -> bool:
    ok, _ = _git_ok(git, "merge-base", "--is-ancestor", older, newer)
    if ok:
        return True
    # Distinguish normal false ancestry from command failure.
    proc = __import__("subprocess").run(
        ["git", "-C", str(git.root), "merge-base", "--is-ancestor", older, newer],
        text=True,
        capture_output=True,
    )
    if proc.returncode == 1:
        return False
    raise GitStateError(proc.stderr.strip() or proc.stdout.strip())


def _changed_files(git: GitBackend, older: str, newer: str) -> list[str]:
    text = git._git("diff", "--name-only", f"{older}..{newer}")
    return sorted({_normalize_path(line) for line in text.splitlines() if _normalize_path(line)})


def _commit_count(git: GitBackend, older: str, newer: str) -> int:
    return int(git._git("rev-list", "--count", f"{older}..{newer}") or 0)


def _blob_text(git: GitBackend, ref: str, path: str) -> str | None:
    ok, text = _git_ok(git, "show", f"{ref}:{path}")
    return text if ok else None


def _path_exists_at(git: GitBackend, ref: str, path: str) -> bool:
    proc = __import__("subprocess").run(
        ["git", "-C", str(git.root), "cat-file", "-e", f"{ref}:{path}"],
        text=True,
        capture_output=True,
    )
    return proc.returncode == 0


def _module_candidates(source_path: str, node: ast.AST) -> list[str]:
    """Map local Python import nodes to candidate repository .py paths.

    This is deliberately bounded/direct. It is a dependency hint, not a complete
    semantic dependency proof.
    """
    source = PurePosixPath(source_path)
    package_parts = list(source.parent.parts)
    names: list[str] = []

    if isinstance(node, ast.Import):
        names.extend(alias.name for alias in node.names if alias.name.startswith("athena_mcp."))
        return [name.replace(".", "/") + ".py" for name in names]

    if not isinstance(node, ast.ImportFrom):
        return []

    level = int(node.level or 0)
    module = str(node.module or "")
    if level:
        # level=1 means current package; level=2 ascends one package.
        ascend = max(0, level - 1)
        base = package_parts[: max(0, len(package_parts) - ascend)]
        if module:
            parts = base + module.split(".")
            return ["/".join(parts) + ".py"]
        return ["/".join(base + [alias.name]) + ".py" for alias in node.names]

    if module.startswith("athena_mcp"):
        return [module.replace(".", "/") + ".py"]
    return []


def infer_direct_python_dependencies(
    git: GitBackend,
    candidate_head: str,
    feature_files: Iterable[str],
) -> dict[str, Any]:
    dependencies: set[str] = set()
    errors: list[dict[str, str]] = []
    inspected: list[str] = []

    for path in sorted(set(feature_files)):
        if not path.endswith(".py"):
            continue
        text = _blob_text(git, candidate_head, path)
        if text is None:
            errors.append({"path": path, "error": "FEATURE_BLOB_UNAVAILABLE"})
            continue
        try:
            tree = ast.parse(text, filename=path)
        except SyntaxError as exc:
            errors.append({"path": path, "error": f"SYNTAX_ERROR:{exc.lineno}"})
            continue
        inspected.append(path)
        for node in ast.walk(tree):
            if not isinstance(node, (ast.Import, ast.ImportFrom)):
                continue
            for candidate in _module_candidates(path, node):
                candidate = _normalize_path(candidate)
                if candidate and _path_exists_at(git, candidate_head, candidate):
                    dependencies.add(candidate)
                    parent_init = str(PurePosixPath(candidate).parent / "__init__.py")
                    if _path_exists_at(git, candidate_head, parent_init):
                        dependencies.add(parent_init)

    return {
        "inspected_python_files": inspected,
        "direct_dependencies": sorted(dependencies),
        "errors": errors,
        "complete_for_inspected_files": not errors,
        "law": "DIRECT_IMPORT_DEPENDENCY_HINT != COMPLETE_SEMANTIC_DEPENDENCY_PROOF",
    }


def classify_freshness_train(
    git: GitBackend,
    *,
    candidate_base: str,
    candidate_head: str,
    live_master: str,
    owned_paths: Iterable[str] | None = None,
    dependency_paths: Iterable[str] | None = None,
    critical_paths: Iterable[str] | None = None,
    extra_guarded_paths: Iterable[str] | None = None,
    infer_python_imports: bool = True,
    require_complete_dependency_inference: bool = True,
    prior_resync_attempts: int = 0,
    max_resync_attempts: int = 3,
    max_disjoint_commits_per_batch: int = 32,
) -> dict[str, Any]:
    """Classify master motion without mutating Git state.

    The result is planning evidence only. Even DISJOINT_BATCHABLE requires a native
    sync and a new exact-head integration witness before promotion.
    """
    if not git.enabled:
        return {
            "version": VERSION,
            "status": UNKNOWN_HOLD,
            "reason": "GIT_DISABLED",
            "mutation_performed": False,
            "promotion_authority": False,
        }
    if prior_resync_attempts < 0 or max_resync_attempts < 1 or max_disjoint_commits_per_batch < 1:
        raise ValueError("invalid freshness train bounds")

    try:
        base = _verify_commit(git, candidate_base)
        head = _verify_commit(git, candidate_head)
        live = _verify_commit(git, live_master)
    except (GitStateError, ValueError) as exc:
        return {
            "version": VERSION,
            "status": UNKNOWN_HOLD,
            "reason": "REF_RESOLUTION_FAILED",
            "error": str(exc),
            "mutation_performed": False,
            "promotion_authority": False,
        }

    common = {
        "version": VERSION,
        "candidate_base": base,
        "candidate_head": head,
        "live_master": live,
        "prior_resync_attempts": prior_resync_attempts,
        "max_resync_attempts": max_resync_attempts,
        "max_disjoint_commits_per_batch": max_disjoint_commits_per_batch,
        "mutation_performed": False,
        "promotion_authority": False,
        "semantic_independence_proven": False,
        "historical_ci_is_current_integration_witness": False,
        "laws": [
            "CLASSIFICATION != MERGE_AUTHORITY",
            "CHANGED_FILE_DISJOINTNESS != SEMANTIC_INDEPENDENCE_PROOF",
            "HISTORICAL_CI_PASS != CURRENT_INTEGRATION_PASS",
            "DISJOINT_BATCHABLE -> NATIVE_SYNC -> FULL_EXACT_HEAD_CI -> FRESHNESS_RECHECK",
        ],
    }

    if not _is_ancestor(git, base, head):
        return {**common, "status": UNKNOWN_HOLD, "reason": "CANDIDATE_BASE_NOT_ANCESTOR_OF_HEAD"}
    if live == base:
        result = {
            **common,
            "status": ALIGNED,
            "reason": "LIVE_MASTER_EQUALS_CANDIDATE_BASE",
            "master_commit_count": 0,
            "master_changed_files": [],
            "feature_changed_files": _changed_files(git, base, head),
            "recommended_action": "NO_FRESHNESS_SYNC_REQUIRED",
            "requires_full_ci_after_sync": False,
        }
        result["train_digest"] = _digest(result)
        return result
    if not _is_ancestor(git, base, live):
        return {**common, "status": UNKNOWN_HOLD, "reason": "LIVE_MASTER_NOT_DESCENDANT_OF_CANDIDATE_BASE"}

    feature_files = _changed_files(git, base, head)
    master_files = _changed_files(git, base, live)
    commit_count = _commit_count(git, base, live)

    explicit_owned = _patterns(owned_paths)
    ownership_patterns = tuple(sorted(set(feature_files) | set(explicit_owned)))
    explicit_dependencies = _patterns(dependency_paths)
    explicit_guarded = _patterns(extra_guarded_paths)
    critical_patterns = _patterns(critical_paths) if critical_paths is not None else DEFAULT_CRITICAL_PATTERNS

    inference = {
        "inspected_python_files": [],
        "direct_dependencies": [],
        "errors": [],
        "complete_for_inspected_files": True,
        "law": "IMPORT_INFERENCE_DISABLED",
    }
    if infer_python_imports:
        inference = infer_direct_python_dependencies(git, head, feature_files)

    inferred_dependencies = _patterns(inference.get("direct_dependencies") or [])
    dependency_patterns = tuple(sorted(set(explicit_dependencies) | set(inferred_dependencies) | set(explicit_guarded)))

    owned_hits = _matched(master_files, ownership_patterns)
    dependency_hits = _matched(master_files, dependency_patterns)
    critical_hits = _matched(master_files, critical_patterns)

    result = {
        **common,
        "master_commit_count": commit_count,
        "master_changed_files": master_files,
        "feature_changed_files": feature_files,
        "owned_patterns": list(ownership_patterns),
        "dependency_patterns": list(dependency_patterns),
        "critical_patterns": list(critical_patterns),
        "owned_hits": owned_hits,
        "dependency_hits": dependency_hits,
        "critical_hits": critical_hits,
        "dependency_inference": inference,
        "requires_full_ci_after_sync": True,
    }

    if owned_hits:
        result.update(
            status=OWNED_PATH_CONFLICT,
            reason="LIVE_MASTER_CHANGED_CANDIDATE_OWNED_PATH",
            recommended_action="EXPLICIT_RECONCILIATION_HOLD",
        )
    elif dependency_hits or critical_hits:
        result.update(
            status=DEPENDENCY_REQUALIFY,
            reason="LIVE_MASTER_CHANGED_DEPENDENCY_OR_CRITICAL_SURFACE",
            recommended_action="REHYDRATE_RECONCILE_THEN_FULL_CI",
        )
    elif infer_python_imports and require_complete_dependency_inference and inference.get("errors"):
        result.update(
            status=UNKNOWN_HOLD,
            reason="DEPENDENCY_INFERENCE_INCOMPLETE",
            recommended_action="INSPECT_DEPENDENCY_ERRORS",
        )
    elif prior_resync_attempts >= max_resync_attempts:
        result.update(
            status=MOVING_FRONTIER_HOLD,
            reason="RESYNC_ATTEMPT_BOUND_EXHAUSTED",
            recommended_action="HOLD_WITH_LAST_GREEN_WITNESS",
        )
    elif commit_count > max_disjoint_commits_per_batch:
        result.update(
            status=MOVING_FRONTIER_HOLD,
            reason="DISJOINT_COMMIT_BATCH_BOUND_EXCEEDED",
            recommended_action="HOLD_OR_REBASE_BATCH_POLICY",
        )
    else:
        result.update(
            status=DISJOINT_BATCHABLE,
            reason="NO_PATH_OR_DIRECT_DEPENDENCY_HIT_DETECTED",
            recommended_action="NATIVE_MASTER_TO_FEATURE_SYNC_THEN_FULL_CI",
        )

    result["train_digest"] = _digest(result)
    return result


__all__ = [
    "VERSION",
    "ALIGNED",
    "DISJOINT_BATCHABLE",
    "DEPENDENCY_REQUALIFY",
    "OWNED_PATH_CONFLICT",
    "UNKNOWN_HOLD",
    "MOVING_FRONTIER_HOLD",
    "DEFAULT_CRITICAL_PATTERNS",
    "infer_direct_python_dependencies",
    "classify_freshness_train",
]
