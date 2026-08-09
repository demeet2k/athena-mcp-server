from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.git_backend import GitBackend
from athena_mcp.next_quest_pipeline import RollingQuestPipelineRuntime
from athena_mcp.next_quest_pipeline_breadth import NextQuestBreadthRuntime
from athena_mcp.next_scout_calibrated_economy import NextScoutCalibratedEconomyRuntime, VERSION
from athena_mcp.next_scout_economy import RESOURCE_PROFILE
from athena_mcp.next_scout_metabolism import NextScoutMetabolismRuntime
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


class CalibratedEconomyTests(unittest.TestCase):
    def setUp(self):
        td = tempfile.TemporaryDirectory(); self.addCleanup(td.cleanup)
        root = Path(td.name) / "brain"; root.mkdir()
        _run(root, "init"); _run(root, "config", "user.name", "test"); _run(root, "config", "user.email", "test@example.invalid")
        manifest = {"artifact":"ATHENA.PROMPT.RUNTIME.V1","authority_ceiling":"below external authority","active_state":"prompts/state/ACTIVE.json","policy":"policies/PROMPT_RUNTIME.md","default_profile":"MAXDEV","profiles":{"MAXDEV":["core"]},"modules":{"core":{"path":"prompts/ORCHESTRATION_CORE.md","order":0,"mandatory":True}}}
        active = {"artifact":"ATHENA.PROMPT.STATE.ACTIVE.V1","status":"ACTIVE","profile":"MAXDEV","enabled_modules":["core"],"active_scoped_overlays":[],"revision":1}
        _write(root,"prompts/PROMPT.manifest.json",json.dumps(manifest)); _write(root,"prompts/state/ACTIVE.json",json.dumps(active)); _write(root,"policies/PROMPT_RUNTIME.md","POLICY\n"); _write(root,"prompts/ORCHESTRATION_CORE.md","CORE\n")
        _run(root,"add","."); _run(root,"commit","-m","seed")
        self.git=GitBackend(root); prompt=PromptRuntime(self.git); self.pipeline=RollingQuestPipelineRuntime(self.git,prompt); self.breadth=NextQuestBreadthRuntime(self.pipeline); self.metabolism=NextScoutMetabolismRuntime(self.pipeline,self.breadth); self.economy=NextScoutCalibratedEconomyRuntime(self.pipeline,self.breadth,self.metabolism)
        self.started=self.pipeline.start(goal="g",quests=["Q1","Q2","Q3"],expected_git_head=self.git.head())
        self.planned=self.breadth.plan(pipeline_id=self.started["pipeline_id"],expected_pipeline_state_digest=self.started["state_digest"],expected_git_head=self.git.head(),kinds=["RISK_SCAN","DEPENDENCY_MAP"])

    def test_prior_only_calibrated_economy_matches_static_cost_prior(self):
        result=self.economy.economy(pipeline_id=self.started["pipeline_id"],expected_pipeline_state_digest=self.started["state_digest"],shared_remote_mode="DISABLED")
        self.assertEqual(result["calibration_status"],"PRIOR_ONLY")
        self.assertEqual(result["calibrated_profiles"]["RISK_SCAN"]["tokens"],RESOURCE_PROFILE["RISK_SCAN"]["tokens"])
        self.assertEqual(result["benefit_standing"],"STATIC_V5_PRIORS_NOT_SELF_TRAINED")

    def test_observed_receipt_changes_cost_prior_but_not_benefit_prior(self):
        plan=next(p for p in self.planned["plans"] if p["quest"]["task"]=="Q2" and p["kind"]=="RISK_SCAN")
        self.breadth.record(pipeline_id=self.started["pipeline_id"],plan_id=plan["plan_id"],expected_pipeline_state_digest=self.started["state_digest"],expected_git_head=self.git.head(),result={"observed":True,"status":"OBSERVED","summary":"risk prep done"})
        self.metabolism.record(pipeline_id=self.started["pipeline_id"],plan_id=plan["plan_id"],expected_pipeline_state_digest=self.started["state_digest"],expected_git_head=self.git.head(),measurements={"tokens":{"value":1000,"observed":True,"source":"meter"}},shared_remote_mode="DISABLED")
        result=self.economy.economy(pipeline_id=self.started["pipeline_id"],expected_pipeline_state_digest=self.started["state_digest"],shared_remote_mode="DISABLED")
        self.assertEqual(result["calibration_status"],"CALIBRATED")
        self.assertLess(result["calibrated_profiles"]["RISK_SCAN"]["tokens"],RESOURCE_PROFILE["RISK_SCAN"]["tokens"])
        self.assertEqual(result["calibrated_profiles"]["RISK_SCAN"]["blocker_removal"],RESOURCE_PROFILE["RISK_SCAN"]["blocker_removal"])
        self.assertEqual(result["authority"],"ROUTING_ONLY")

    def test_calibrated_economy_is_read_only(self):
        before=self.git.head(); a=self.economy.economy(pipeline_id=self.started["pipeline_id"],expected_pipeline_state_digest=self.started["state_digest"],shared_remote_mode="DISABLED"); middle=self.git.head(); b=self.economy.economy(pipeline_id=self.started["pipeline_id"],expected_pipeline_state_digest=self.started["state_digest"],shared_remote_mode="DISABLED"); after=self.git.head()
        self.assertEqual((before,middle,after),(before,before,before)); self.assertEqual(a["allocation_digest"],b["allocation_digest"])

    def test_version(self):
        self.assertEqual(VERSION,"ATHENA.NEXT.SCOUT.CALIBRATED.ECONOMY.6")


if __name__ == "__main__": unittest.main()
