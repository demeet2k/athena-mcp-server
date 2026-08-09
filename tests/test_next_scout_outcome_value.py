from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.git_backend import GitBackend
from athena_mcp.next_quest_pipeline import RollingQuestPipelineRuntime
from athena_mcp.next_quest_pipeline_breadth import NextQuestBreadthRuntime
from athena_mcp.next_scout_outcome_value import NextScoutOutcomeValueRuntime, VERSION
from athena_mcp.prompt_runtime import PromptRuntime
from athena_mcp.rehydration_loop import _sha


def _run(root: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True)
    if p.returncode:
        raise AssertionError(p.stderr or p.stdout)
    return p.stdout.strip()


def _write(root: Path, rel: str, value) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(value if isinstance(value, str) else json.dumps(value), encoding="utf-8")


def _baton():
    row = {"candidate_id": "Q4", "task": "Quest four", "routing_score": 1.0, "metrics": {}, "source": "TEST"}
    value = {"artifact": "ATHENA.REHYDRATION.SUCCESSOR.BATON.V1", "status": "SELECTED", "selected": row, "ties": [], "candidates": [row]}
    value["baton_digest"] = _sha(value)
    return value


def _brain(base: Path):
    root = base / "brain"
    root.mkdir()
    _run(root, "init")
    _run(root, "config", "user.name", "test")
    _run(root, "config", "user.email", "test@example.invalid")
    _write(root, "prompts/PROMPT.manifest.json", {"artifact":"ATHENA.PROMPT.RUNTIME.V1","authority_ceiling":"below external authority","active_state":"prompts/state/ACTIVE.json","policy":"policies/PROMPT_RUNTIME.md","default_profile":"MAXDEV","profiles":{"MAXDEV":["core"]},"modules":{"core":{"path":"prompts/ORCHESTRATION_CORE.md","order":0,"mandatory":True}}})
    _write(root, "prompts/state/ACTIVE.json", {"artifact":"ATHENA.PROMPT.STATE.ACTIVE.V1","status":"ACTIVE","profile":"MAXDEV","enabled_modules":["core"],"active_scoped_overlays":[],"revision":1})
    _write(root, "policies/PROMPT_RUNTIME.md", "POLICY\n")
    _write(root, "prompts/ORCHESTRATION_CORE.md", "CORE\n")
    _run(root, "add", "."); _run(root, "commit", "-m", "seed")
    git = GitBackend(root); prompt = PromptRuntime(git); pipeline = RollingQuestPipelineRuntime(git, prompt); breadth = NextQuestBreadthRuntime(pipeline)
    start = pipeline.start(goal="g", quests=["Q1","Q2","Q3"], expected_git_head=git.head())
    planned = breadth.plan(pipeline_id=start["pipeline_id"], expected_pipeline_state_digest=start["state_digest"], expected_git_head=git.head(), kinds=["DEPENDENCY_MAP", "TEST_DESIGN"])
    q1 = start["window"]["focus"]
    # prep is normally staged only; for V7 fixture, associate Q2 prep, rotate Q1, then complete Q2.
    q2 = start["window"]["execution_order"][1]
    for plan in [p for p in planned["plans"] if p["quest"]["quest_id"] == q2["quest_id"]]:
        current = git.head()
        breadth.record(pipeline_id=start["pipeline_id"], plan_id=plan["plan_id"], expected_pipeline_state_digest=start["state_digest"], expected_git_head=current,
                       result={"observed":True,"status":"OBSERVED","summary":f"prepared {plan['kind']}"})
    state = pipeline.state(start["pipeline_id"])
    first = pipeline.rotate(pipeline_id=start["pipeline_id"], expected_state_digest=state["state_digest"], expected_checkpoint_head=state["checkpoint_head"], completed_quest_id=q1["quest_id"], completion={"observed":True,"status":"SUCCEEDED","summary":"q1 done"}, successor_baton=_baton())
    return root, git, pipeline, breadth, first, q2


class OutcomeValueTests(unittest.TestCase):
    def setUp(self):
        td = tempfile.TemporaryDirectory(); self.addCleanup(td.cleanup)
        self.root, self.git, self.pipeline, self.breadth, self.state_after_q1, self.q2 = _brain(Path(td.name))
        self.runtime = NextScoutOutcomeValueRuntime(self.pipeline, self.breadth)

    def _complete_q2(self):
        state = self.pipeline.state(self.state_after_q1["pipeline_id"])
        return self.pipeline.rotate(pipeline_id=state["pipeline_id"], expected_state_digest=state["state_digest"], expected_checkpoint_head=state["checkpoint_head"], completed_quest_id=state["window"]["focus"]["quest_id"], completion={"observed":True,"status":"SUCCEEDED","summary":"q2 done","evidence_refs":["test://q2"]}, successor_baton=_baton())

    def test_outcome_requires_completed_focus(self):
        state = self.pipeline.state(self.state_after_q1["pipeline_id"])
        with self.assertRaisesRegex(ValueError, "COMPLETED_FOCUS"):
            self.runtime.record(pipeline_id=state["pipeline_id"], quest_id=self.q2["quest_id"], expected_pipeline_state_digest=state["state_digest"], expected_git_head=self.git.head(), measurements={"focus_success":{"observed":True,"source":"test","value":True}})

    def test_record_and_calibrate_are_association_only(self):
        self._complete_q2(); state = self.pipeline.state(self.state_after_q1["pipeline_id"])
        result = self.runtime.record(pipeline_id=state["pipeline_id"], quest_id=self.q2["quest_id"], expected_pipeline_state_digest=state["state_digest"], expected_git_head=self.git.head(), measurements={"focus_success":{"observed":True,"source":"focus-receipt","value":True},"test_pass_ratio":{"observed":True,"source":"tests","value":1.0},"rework_count":{"observed":True,"source":"git-history","value":0}})
        self.assertEqual(result["receipt"]["standing"], "OBSERVED_DOWNSTREAM_ASSOCIATION")
        self.assertFalse(result["receipt"]["causal_effect"])
        calibrated = self.runtime.calibrate(pipeline_id=state["pipeline_id"])
        self.assertEqual(calibrated["standing"], "OBSERVATIONAL_ASSOCIATION_ONLY")
        self.assertFalse(calibrated["causal_effect"])
        self.assertGreater(calibrated["calibrated_associations"]["DEPENDENCY_MAP"]["downstream_success"]["observations"], 0)
        overlay = self.runtime.overlay(pipeline_id=state["pipeline_id"])
        self.assertEqual(overlay["allocation_effect"], "NONE")

    def test_unsourced_or_unobserved_metric_rejected(self):
        self._complete_q2(); state = self.pipeline.state(self.state_after_q1["pipeline_id"])
        with self.assertRaisesRegex(ValueError, "source"):
            self.runtime.record(pipeline_id=state["pipeline_id"], quest_id=self.q2["quest_id"], expected_pipeline_state_digest=state["state_digest"], expected_git_head=self.git.head(), measurements={"focus_success":{"observed":True,"source":"","value":True}})
        with self.assertRaisesRegex(ValueError, "observed=true"):
            self.runtime.record(pipeline_id=state["pipeline_id"], quest_id=self.q2["quest_id"], expected_pipeline_state_digest=state["state_digest"], expected_git_head=self.git.head(), measurements={"focus_success":{"observed":False,"source":"x","value":True}})

    def test_same_outcome_identity_is_idempotent(self):
        self._complete_q2(); state = self.pipeline.state(self.state_after_q1["pipeline_id"])
        args = dict(pipeline_id=state["pipeline_id"], quest_id=self.q2["quest_id"], expected_pipeline_state_digest=state["state_digest"], measurements={"focus_success":{"observed":True,"source":"x","value":True}})
        first = self.runtime.record(expected_git_head=self.git.head(), **args)
        second = self.runtime.record(expected_git_head=self.git.head(), **args)
        self.assertEqual(first["receipt"]["receipt_id"], second["receipt"]["receipt_id"])
        self.assertEqual(second["status"], "REUSED")
        self.assertFalse(second["git_mutation"])

    def test_version(self):
        self.assertEqual(VERSION, "ATHENA.NEXT.SCOUT.OUTCOME.VALUE.7")


if __name__ == "__main__": unittest.main()
