from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.freshness_train import (
    ALIGNED,
    DEPENDENCY_REQUALIFY,
    DISJOINT_BATCHABLE,
    MOVING_FRONTIER_HOLD,
    OWNED_PATH_CONFLICT,
    UNKNOWN_HOLD,
    classify_freshness_train,
    infer_direct_python_dependencies,
)
from athena_mcp.git_backend import GitBackend


def _run(root: Path, *args: str) -> str:
    proc = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True)
    if proc.returncode:
        raise AssertionError(proc.stderr or proc.stdout)
    return proc.stdout.strip()


class FreshnessTrainTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.root = Path(self.td.name) / "repo"
        self.root.mkdir()
        _run(self.root, "init", "-b", "master")
        _run(self.root, "config", "user.name", "test")
        _run(self.root, "config", "user.email", "test@example.invalid")
        (self.root / "athena_mcp").mkdir()
        (self.root / ".github" / "workflows").mkdir(parents=True)
        (self.root / "athena_mcp" / "__init__.py").write_text("\n", encoding="utf-8")
        (self.root / "athena_mcp" / "dep.py").write_text("VALUE = 1\n", encoding="utf-8")
        (self.root / "athena_mcp" / "feature.py").write_text(
            "from .dep import VALUE\nFEATURE = VALUE\n", encoding="utf-8"
        )
        (self.root / "athena_mcp" / "aor_collective_transport_surface.py").write_text(
            "SURFACE = 1\n", encoding="utf-8"
        )
        (self.root / ".github" / "workflows" / "ci.yml").write_text("name: CI\n", encoding="utf-8")
        (self.root / "other.txt").write_text("base\n", encoding="utf-8")
        _run(self.root, "add", ".")
        _run(self.root, "commit", "-m", "base")
        self.base = _run(self.root, "rev-parse", "HEAD")

        _run(self.root, "switch", "-c", "candidate")
        (self.root / "athena_mcp" / "feature.py").write_text(
            "from .dep import VALUE\nFEATURE = VALUE + 1\n", encoding="utf-8"
        )
        _run(self.root, "add", "athena_mcp/feature.py")
        _run(self.root, "commit", "-m", "candidate feature")
        self.candidate = _run(self.root, "rev-parse", "HEAD")

        self.live_disjoint = self._branch_commit(
            "live-disjoint", {"other.txt": "disjoint\n"}, "disjoint master"
        )
        self.live_owned = self._branch_commit(
            "live-owned", {"athena_mcp/feature.py": "FEATURE = 99\n"}, "owned collision"
        )
        self.live_dependency = self._branch_commit(
            "live-dependency", {"athena_mcp/dep.py": "VALUE = 2\n"}, "dependency motion"
        )
        self.live_critical = self._branch_commit(
            "live-critical",
            {"athena_mcp/aor_collective_transport_surface.py": "SURFACE = 2\n"},
            "critical motion",
        )
        self.git = GitBackend(self.root)

    def _branch_commit(self, branch: str, changes: dict[str, str], message: str, base: str | None = None) -> str:
        _run(self.root, "switch", "-C", branch, base or self.base)
        for rel, text in changes.items():
            path = self.root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        _run(self.root, "add", ".")
        _run(self.root, "commit", "-m", message)
        return _run(self.root, "rev-parse", "HEAD")

    def _classify(self, live: str, **kwargs):
        return classify_freshness_train(
            self.git,
            candidate_base=self.base,
            candidate_head=self.candidate,
            live_master=live,
            **kwargs,
        )

    def test_aligned_base_requires_no_sync(self):
        out = self._classify(self.base)
        self.assertEqual(out["status"], ALIGNED)
        self.assertFalse(out["requires_full_ci_after_sync"])
        self.assertEqual(out["master_commit_count"], 0)
        self.assertFalse(out["mutation_performed"])
        self.assertFalse(out["promotion_authority"])

    def test_disjoint_master_motion_is_batchable_candidate_not_independence_proof(self):
        out = self._classify(self.live_disjoint)
        self.assertEqual(out["status"], DISJOINT_BATCHABLE)
        self.assertEqual(out["master_changed_files"], ["other.txt"])
        self.assertEqual(out["recommended_action"], "NATIVE_MASTER_TO_FEATURE_SYNC_THEN_FULL_CI")
        self.assertTrue(out["requires_full_ci_after_sync"])
        self.assertFalse(out["semantic_independence_proven"])
        self.assertFalse(out["historical_ci_is_current_integration_witness"])

    def test_exact_feature_file_motion_is_owned_conflict(self):
        out = self._classify(self.live_owned)
        self.assertEqual(out["status"], OWNED_PATH_CONFLICT)
        self.assertEqual(out["owned_hits"], ["athena_mcp/feature.py"])
        self.assertEqual(out["recommended_action"], "EXPLICIT_RECONCILIATION_HOLD")

    def test_direct_python_import_motion_is_dependency_requalify(self):
        out = self._classify(self.live_dependency)
        self.assertEqual(out["status"], DEPENDENCY_REQUALIFY)
        self.assertIn("athena_mcp/dep.py", out["dependency_patterns"])
        self.assertEqual(out["dependency_hits"], ["athena_mcp/dep.py"])
        self.assertTrue(out["dependency_inference"]["complete_for_inspected_files"])

    def test_shared_critical_surface_motion_is_dependency_requalify(self):
        out = self._classify(self.live_critical)
        self.assertEqual(out["status"], DEPENDENCY_REQUALIFY)
        self.assertEqual(out["critical_hits"], ["athena_mcp/aor_collective_transport_surface.py"])

    def test_explicit_dependency_path_is_respected(self):
        live = self._branch_commit("live-explicit", {"guarded/config.json": "{}\n"}, "guarded change")
        out = self._classify(live, dependency_paths=["guarded/config.json"], critical_paths=[])
        self.assertEqual(out["status"], DEPENDENCY_REQUALIFY)
        self.assertEqual(out["dependency_hits"], ["guarded/config.json"])

    def test_resync_attempt_bound_holds_instead_of_weakening_freshness(self):
        out = self._classify(self.live_disjoint, prior_resync_attempts=3, max_resync_attempts=3)
        self.assertEqual(out["status"], MOVING_FRONTIER_HOLD)
        self.assertEqual(out["reason"], "RESYNC_ATTEMPT_BOUND_EXHAUSTED")
        self.assertFalse(out["promotion_authority"])

    def test_disjoint_commit_batch_bound_holds(self):
        _run(self.root, "switch", "-C", "live-many", self.live_disjoint)
        (self.root / "more.txt").write_text("two\n", encoding="utf-8")
        _run(self.root, "add", "more.txt")
        _run(self.root, "commit", "-m", "second disjoint commit")
        live_many = _run(self.root, "rev-parse", "HEAD")
        out = self._classify(live_many, max_disjoint_commits_per_batch=1)
        self.assertEqual(out["status"], MOVING_FRONTIER_HOLD)
        self.assertEqual(out["master_commit_count"], 2)
        self.assertEqual(out["reason"], "DISJOINT_COMMIT_BATCH_BOUND_EXCEEDED")

    def test_bad_candidate_ancestry_holds_unknown(self):
        out = classify_freshness_train(
            self.git,
            candidate_base=self.live_disjoint,
            candidate_head=self.candidate,
            live_master=self.live_disjoint,
        )
        self.assertEqual(out["status"], UNKNOWN_HOLD)
        self.assertEqual(out["reason"], "CANDIDATE_BASE_NOT_ANCESTOR_OF_HEAD")

    def test_unknown_ref_holds_without_exception_or_mutation(self):
        before = self.git.head()
        out = classify_freshness_train(
            self.git,
            candidate_base=self.base,
            candidate_head=self.candidate,
            live_master="does-not-exist",
        )
        self.assertEqual(out["status"], UNKNOWN_HOLD)
        self.assertEqual(out["reason"], "REF_RESOLUTION_FAILED")
        self.assertEqual(self.git.head(), before)
        self.assertFalse(out["mutation_performed"])

    def test_classifier_is_read_only_and_digest_is_deterministic(self):
        _run(self.root, "switch", "live-disjoint")
        before_head = self.git.head()
        before_status = _run(self.root, "status", "--porcelain")
        first = self._classify(self.live_disjoint)
        second = self._classify(self.live_disjoint)
        self.assertEqual(first["train_digest"], second["train_digest"])
        self.assertEqual(self.git.head(), before_head)
        self.assertEqual(_run(self.root, "status", "--porcelain"), before_status)
        self.assertFalse(first["mutation_performed"])

    def test_direct_dependency_inference_is_bounded_and_explicit(self):
        out = infer_direct_python_dependencies(
            self.git,
            self.candidate,
            ["athena_mcp/feature.py"],
        )
        self.assertIn("athena_mcp/dep.py", out["direct_dependencies"])
        self.assertIn("athena_mcp/__init__.py", out["direct_dependencies"])
        self.assertEqual(out["errors"], [])
        self.assertIn("!= COMPLETE_SEMANTIC_DEPENDENCY_PROOF", out["law"])


if __name__ == "__main__":
    unittest.main()
