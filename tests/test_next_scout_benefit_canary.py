from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from athena_mcp.next_scout_benefit_canary import (
    VERSION,
    NEXT_SCOUT_BENEFIT_CANARY_TOOLS,
    NextScoutBenefitCanaryRuntime,
)
from athena_mcp.next_scout_economy import RESOURCE_PROFILE


class FakeGit:
    def __init__(self):
        self._head = "h0"

    def head(self):
        return self._head


class FakePrompt:
    def __init__(self, root: Path, git: FakeGit):
        self.root = root
        self.git = git
        self.n = 0

    def _safe_rel(self, rel: str) -> Path:
        p = (self.root / rel).resolve()
        if self.root.resolve() not in p.parents and p != self.root.resolve():
            raise ValueError("unsafe path")
        return p

    def _commit_files(self, current: str, files: dict[str, str], actor: str, message: str):
        if self.git.head() != current:
            raise ValueError("stale fake head")
        for rel, content in files.items():
            path = self._safe_rel(rel)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        self.n += 1
        self.git._head = f"h{self.n}"
        return {"head": self.git.head(), "actor": actor, "message": message}


class FakePipeline:
    def __init__(self):
        self._state = {
            "status": "ACTIVE",
            "pipeline_id": "NQP-test",
            "state_digest": "D1",
            "window": {
                "execution_order": [
                    {"quest_id": "Q1", "role": "FOCUS_Q1"},
                    {"quest_id": "Q2", "role": "STAGED_Q2"},
                    {"quest_id": "Q3", "role": "STAGED_Q3"},
                ]
            },
        }

    def state(self, pipeline_id: str):
        if pipeline_id != "NQP-test":
            raise ValueError("bad pipeline")
        return copy.deepcopy(self._state)


class FakeBreadth:
    def __init__(self):
        self.plans = {
            "P_DEP": {"plan_id": "P_DEP", "kind": "DEPENDENCY_MAP", "quest": {"quest_id": "Q2"}},
            "P_RISK": {"plan_id": "P_RISK", "kind": "RISK_SCAN", "quest": {"quest_id": "Q2"}},
        }

    def _read_breadth(self, pipeline_id: str):
        return {"plans": copy.deepcopy(self.plans), "observations": {}, "state_digest": "B1"}, {}


class FakeV9:
    def __init__(self, git: FakeGit, prompt: FakePrompt):
        self.git = git
        self.prompt_runtime = prompt
        self.drift = False
        self.abstain = False

    def evaluate(self, **kwargs):
        if self.abstain:
            return {
                "standing": "ABSTAIN_HELD_OUT_VALIDATION",
                "evaluation_digest": "E-abstain",
                "prep_kind": "RISK_SCAN",
                "passing_metrics": [],
                "metrics": {},
            }
        return {
            "standing": "BENEFIT_PRIOR_PROMOTION_CANDIDATE",
            "evaluation_digest": "E2" if self.drift else "E1",
            "prep_kind": "RISK_SCAN",
            "passing_metrics": ["test_quality"],
            "metrics": {
                "test_quality": {
                    "validation": {"median_delta": 1.0},
                    "discovery": {"median_delta": 1.0},
                }
            },
        }


class FakeCalibrated:
    def __init__(self, pipeline: FakePipeline, breadth: FakeBreadth):
        self.pipeline = pipeline
        self.breadth = breadth

    @staticmethod
    def _roles(state: dict):
        return {row["quest_id"]: i for i, row in enumerate(state["window"]["execution_order"])}

    def economy(self, **kwargs):
        if kwargs["expected_pipeline_state_digest"] != "D1":
            raise ValueError("stale")
        return {
            "artifact": "ATHENA.NEXT.SCOUT.CALIBRATED.ECONOMY.6",
            "status": "SELECTED",
            "pipeline_id": "NQP-test",
            "pipeline_state_digest": "D1",
            "calibrated_profiles": copy.deepcopy(RESOURCE_PROFILE),
            "candidate_plan_ids": ["P_DEP", "P_RISK"],
            "active_plan_ids": [],
            "available_after_active": {"tokens": 24000.0, "minutes": 60.0, "tool_calls": 16.0, "coordination": 10.0, "git_risk": 8.0},
            "new_slots": 1,
            "selected_plan_ids": ["P_DEP"],
            "allocation_digest": "CONTROL1",
        }


class BenefitCanaryTests(unittest.TestCase):
    def setUp(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = Path(td.name)
        self.git = FakeGit()
        self.prompt = FakePrompt(root, self.git)
        self.pipeline = FakePipeline()
        self.breadth = FakeBreadth()
        self.v9 = FakeV9(self.git, self.prompt)
        self.calibrated = FakeCalibrated(self.pipeline, self.breadth)
        self.runtime = NextScoutBenefitCanaryRuntime(self.v9, self.calibrated)

    def _start(self, **kwargs):
        args = dict(
            pipeline_id="NQP-test",
            cohort_id="C1",
            expected_git_head=self.git.head(),
            lambda_weight=0.25,
            max_cycles=3,
            max_changed_plan_ids=2,
        )
        args.update(kwargs)
        return self.runtime.start(**args)

    def test_start_requires_v9_candidate_and_never_mutates_canonical_prior(self):
        before = copy.deepcopy(RESOURCE_PROFILE)
        result = self._start()
        canary = result["canary"]
        self.assertEqual(result["status"], "STARTED")
        self.assertEqual(canary["standing"], "BOUNDED_ROUTING_CANARY")
        self.assertEqual(canary["benefit_multiplier"], 1.25)
        self.assertEqual(canary["canonical_benefit_prior_mutation"], "NONE")
        self.assertEqual(before, RESOURCE_PROFILE)

    def test_start_abstains_when_v9_did_not_promote_candidate(self):
        self.v9.abstain = True
        with self.assertRaisesRegex(ValueError, "V10_REQUIRES_V9"):
            self._start()

    def test_preview_can_flip_one_slot_without_mutating_resource_profile(self):
        before = copy.deepcopy(RESOURCE_PROFILE)
        started = self._start()
        preview = self.runtime.preview(
            pipeline_id="NQP-test", canary_id=started["canary"]["canary_id"],
            expected_pipeline_state_digest="D1", shared_remote_mode="DISABLED",
        )
        self.assertEqual(preview["status"], "CANARY_PREVIEW_READY")
        self.assertEqual(preview["control_selected_plan_ids"], ["P_DEP"])
        self.assertEqual(preview["canary_selected_plan_ids"], ["P_RISK"])
        self.assertEqual(set(preview["changed_plan_ids"]), {"P_DEP", "P_RISK"})
        self.assertEqual(before, RESOURCE_PROFILE)

    def test_divergence_over_frozen_bound_forces_control(self):
        started = self._start(max_changed_plan_ids=0)
        preview = self.runtime.preview(
            pipeline_id="NQP-test", canary_id=started["canary"]["canary_id"],
            expected_pipeline_state_digest="D1", shared_remote_mode="DISABLED",
        )
        self.assertTrue(preview["rollback_required"])
        self.assertEqual(preview["routing_lane"], "CONTROL")
        self.assertEqual(preview["status"], "CANARY_DIVERGENCE_LIMIT_HOLD")

    def test_apply_persists_routing_decision_but_not_claim(self):
        started = self._start()
        result = self.runtime.apply(
            pipeline_id="NQP-test", canary_id=started["canary"]["canary_id"],
            expected_pipeline_state_digest="D1", expected_git_head=self.git.head(),
            shared_remote_mode="DISABLED",
        )
        self.assertEqual(result["status"], "CANARY_APPLIED")
        self.assertEqual(result["selected_plan_ids"], ["P_RISK"])
        self.assertEqual(result["claim_effect"], "NONE")
        self.assertEqual(result["canonical_benefit_prior_mutation"], "NONE")
        self.assertEqual(result["canary"]["cycles_used"], 1)

    def test_v9_drift_auto_rolls_back_to_control(self):
        started = self._start()
        self.v9.drift = True
        result = self.runtime.apply(
            pipeline_id="NQP-test", canary_id=started["canary"]["canary_id"],
            expected_pipeline_state_digest="D1", expected_git_head=self.git.head(),
            shared_remote_mode="DISABLED",
        )
        self.assertEqual(result["status"], "AUTO_ROLLED_BACK")
        self.assertEqual(result["routing_lane"], "CONTROL")
        state = self.runtime.state(pipeline_id="NQP-test", canary_id=started["canary"]["canary_id"])
        self.assertEqual(state["status"], "ROLLED_BACK")

    def test_last_allowed_cycle_expires_after_decision(self):
        started = self._start(max_cycles=1)
        result = self.runtime.apply(
            pipeline_id="NQP-test", canary_id=started["canary"]["canary_id"],
            expected_pipeline_state_digest="D1", expected_git_head=self.git.head(),
            shared_remote_mode="DISABLED",
        )
        self.assertEqual(result["status"], "CANARY_APPLIED")
        self.assertEqual(result["canary"]["status"], "EXPIRED")
        state = self.runtime.state(pipeline_id="NQP-test", canary_id=started["canary"]["canary_id"])
        self.assertEqual(state["routing_lane"], "CONTROL")

    def test_tool_surface_and_version(self):
        self.assertEqual(VERSION, "ATHENA.NEXT.SCOUT.BENEFIT.CANARY.10")
        self.assertEqual(len(NEXT_SCOUT_BENEFIT_CANARY_TOOLS), 5)
        self.assertEqual({x["name"] for x in NEXT_SCOUT_BENEFIT_CANARY_TOOLS}, {
            "athena_next_scout_canary_start",
            "athena_next_scout_canary_preview",
            "athena_next_scout_canary_apply",
            "athena_next_scout_canary_rollback",
            "athena_next_scout_canary_state",
        })


if __name__ == "__main__":
    unittest.main()
