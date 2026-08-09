from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.git_backend import GitBackend
from athena_mcp.next_quest_pipeline import RollingQuestPipelineRuntime
from athena_mcp.next_quest_pipeline_breadth import NextQuestBreadthRuntime
from athena_mcp.next_scout_economy import RESOURCE_PROFILE
from athena_mcp.next_scout_metabolism import NextScoutMetabolismRuntime, VERSION
from athena_mcp.prompt_runtime import PromptRuntime


def _run(root: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True)
    if p.returncode:
        raise AssertionError(p.stderr or p.stdout)
    return p.stdout.strip()


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _runtime(base: Path):
    root = base / "brain"
    root.mkdir()
    _run(root, "init")
    _run(root, "config", "user.name", "test")
    _run(root, "config", "user.email", "test@example.invalid")
    manifest = {
        "artifact": "ATHENA.PROMPT.RUNTIME.V1", "authority_ceiling": "below external authority",
        "active_state": "prompts/state/ACTIVE.json", "policy": "policies/PROMPT_RUNTIME.md",
        "default_profile": "MAXDEV", "profiles": {"MAXDEV": ["core"]},
        "modules": {"core": {"path": "prompts/ORCHESTRATION_CORE.md", "order": 0, "mandatory": True}},
    }
    active = {"artifact": "ATHENA.PROMPT.STATE.ACTIVE.V1", "status": "ACTIVE", "profile": "MAXDEV", "enabled_modules": ["core"], "active_scoped_overlays": [], "revision": 1}
    _write(root, "prompts/PROMPT.manifest.json", json.dumps(manifest))
    _write(root, "prompts/state/ACTIVE.json", json.dumps(active))
    _write(root, "policies/PROMPT_RUNTIME.md", "POLICY\n")
    _write(root, "prompts/ORCHESTRATION_CORE.md", "CORE\n")
    _run(root, "add", ".")
    _run(root, "commit", "-m", "seed")
    git = GitBackend(root)
    prompt = PromptRuntime(git)
    pipeline = RollingQuestPipelineRuntime(git, prompt)
    breadth = NextQuestBreadthRuntime(pipeline)
    metabolism = NextScoutMetabolismRuntime(pipeline, breadth)
    started = pipeline.start(goal="g", quests=["Q1", "Q2", "Q3"], expected_git_head=git.head())
    planned = breadth.plan(
        pipeline_id=started["pipeline_id"], expected_pipeline_state_digest=started["state_digest"],
        expected_git_head=git.head(), kinds=["RISK_SCAN"],
    )
    return root, git, pipeline, breadth, metabolism, started, planned


def _observe(breadth, git, started, planned, plan):
    return breadth.record(
        pipeline_id=started["pipeline_id"], plan_id=plan["plan_id"],
        expected_pipeline_state_digest=started["state_digest"], expected_git_head=git.head(),
        result={"observed": True, "status": "OBSERVED", "summary": "prep done", "evidence_refs": ["git://prep"]},
    )


def _measure(tokens=1000, minutes=5, tools=1):
    return {
        "tokens": {"value": tokens, "observed": True, "source": "usage-meter", "evidence_ref": "metric://tokens"},
        "minutes": {"value": minutes, "observed": True, "source": "clock", "evidence_ref": "metric://time"},
        "tool_calls": {"value": tools, "observed": True, "source": "tool-log", "evidence_ref": "metric://tools"},
    }


class NextScoutMetabolismTests(unittest.TestCase):
    def setUp(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        self.root, self.git, self.pipeline, self.breadth, self.metabolism, self.started, self.planned = _runtime(Path(td.name))
        self.plan = next(p for p in self.planned["plans"] if p["quest"]["task"] == "Q2")

    def test_receipt_requires_observed_prep_result(self):
        with self.assertRaisesRegex(ValueError, "REQUIRES_OBSERVED_PREP_RESULT"):
            self.metabolism.record(
                pipeline_id=self.started["pipeline_id"], plan_id=self.plan["plan_id"],
                expected_pipeline_state_digest=self.started["state_digest"], expected_git_head=self.git.head(),
                measurements=_measure(), shared_remote_mode="DISABLED",
            )

    def test_measurements_must_be_explicitly_observed(self):
        _observe(self.breadth, self.git, self.started, self.planned, self.plan)
        with self.assertRaisesRegex(ValueError, "observed=true"):
            self.metabolism.record(
                pipeline_id=self.started["pipeline_id"], plan_id=self.plan["plan_id"],
                expected_pipeline_state_digest=self.started["state_digest"], expected_git_head=self.git.head(),
                measurements={"tokens": {"value": 1000, "observed": False, "source": "guess"}},
                shared_remote_mode="DISABLED",
            )

    def test_recorded_receipt_is_cost_only_and_persisted(self):
        _observe(self.breadth, self.git, self.started, self.planned, self.plan)
        result = self.metabolism.record(
            pipeline_id=self.started["pipeline_id"], plan_id=self.plan["plan_id"],
            expected_pipeline_state_digest=self.started["state_digest"], expected_git_head=self.git.head(),
            measurements=_measure(), actor="scout-a", shared_remote_mode="DISABLED",
        )
        self.assertEqual(result["status"], "RECORDED")
        receipt = result["receipt"]
        self.assertEqual(receipt["authority"], "COST_CALIBRATION_ONLY")
        self.assertEqual(receipt["standing"], "OBSERVED_MEASUREMENT_ASSERTION")
        self.assertNotIn("value", receipt)
        self.assertTrue((self.root / "prompts" / "next_quest_pipelines" / self.started["pipeline_id"] / "metabolism" / "receipts" / f"{receipt['receipt_id']}.json").is_file())

    def test_calibration_uses_observed_median_with_prior_shrinkage(self):
        _observe(self.breadth, self.git, self.started, self.planned, self.plan)
        self.metabolism.record(
            pipeline_id=self.started["pipeline_id"], plan_id=self.plan["plan_id"],
            expected_pipeline_state_digest=self.started["state_digest"], expected_git_head=self.git.head(),
            measurements=_measure(tokens=1000, minutes=5, tools=1), shared_remote_mode="DISABLED",
        )
        calibrated = self.metabolism.calibrate(pipeline_id=self.started["pipeline_id"], prior_strength=3)
        self.assertEqual(calibrated["status"], "CALIBRATED")
        prior = RESOURCE_PROFILE["RISK_SCAN"]
        expected_tokens = (3 * prior["tokens"] + 1000) / 4
        self.assertEqual(calibrated["calibrated_profiles"]["RISK_SCAN"]["tokens"], round(expected_tokens, 4))
        self.assertEqual(calibrated["calibrated_profiles"]["RISK_SCAN"]["coordination"], prior["coordination"])
        self.assertEqual(calibrated["evidence"]["RISK_SCAN"]["observation_counts"]["tokens"], 1)

    def test_missing_measurement_is_not_zero(self):
        _observe(self.breadth, self.git, self.started, self.planned, self.plan)
        self.metabolism.record(
            pipeline_id=self.started["pipeline_id"], plan_id=self.plan["plan_id"],
            expected_pipeline_state_digest=self.started["state_digest"], expected_git_head=self.git.head(),
            measurements={"minutes": {"value": 4, "observed": True, "source": "clock"}},
            shared_remote_mode="DISABLED",
        )
        calibrated = self.metabolism.calibrate(pipeline_id=self.started["pipeline_id"])
        self.assertEqual(calibrated["calibrated_profiles"]["RISK_SCAN"]["tokens"], RESOURCE_PROFILE["RISK_SCAN"]["tokens"])
        self.assertEqual(calibrated["evidence"]["RISK_SCAN"]["observation_counts"]["tokens"], 0)

    def test_calibration_is_read_only_and_deterministic(self):
        before = self.git.head()
        first = self.metabolism.calibrate(pipeline_id=self.started["pipeline_id"])
        middle = self.git.head()
        second = self.metabolism.calibrate(pipeline_id=self.started["pipeline_id"])
        after = self.git.head()
        self.assertEqual(before, middle)
        self.assertEqual(middle, after)
        self.assertEqual(first["calibration_digest"], second["calibration_digest"])
        self.assertEqual(first["status"], "PRIOR_ONLY")

    def test_version(self):
        self.assertEqual(VERSION, "ATHENA.NEXT.SCOUT.METABOLISM.6")


if __name__ == "__main__":
    unittest.main()
