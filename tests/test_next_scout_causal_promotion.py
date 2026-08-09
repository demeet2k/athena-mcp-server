from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.git_backend import GitBackend
from athena_mcp.next_quest_pipeline import RollingQuestPipelineRuntime
from athena_mcp.next_quest_pipeline_breadth import NextQuestBreadthRuntime
from athena_mcp.next_scout_counterfactual_credit import NextScoutCounterfactualCreditRuntime, PAIR_ARTIFACT, _digest as v8_digest
from athena_mcp.next_scout_outcome_value import NextScoutOutcomeValueRuntime
from athena_mcp.next_scout_causal_promotion import NextScoutCausalPromotionRuntime, VERSION
from athena_mcp.prompt_runtime import PromptRuntime


def _run(root: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True)
    if p.returncode:
        raise AssertionError(p.stderr or p.stdout)
    return p.stdout.strip()


def _write(root: Path, rel: str, value) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(value if isinstance(value, str) else json.dumps(value), encoding="utf-8")


def _runtime(base: Path):
    root = base / "brain"; root.mkdir()
    _run(root, "init"); _run(root, "config", "user.name", "test"); _run(root, "config", "user.email", "test@example.invalid")
    _write(root, "prompts/PROMPT.manifest.json", {"artifact":"ATHENA.PROMPT.RUNTIME.V1","authority_ceiling":"below external authority","active_state":"prompts/state/ACTIVE.json","policy":"policies/PROMPT_RUNTIME.md","default_profile":"MAXDEV","profiles":{"MAXDEV":["core"]},"modules":{"core":{"path":"prompts/ORCHESTRATION_CORE.md","order":0,"mandatory":True}}})
    _write(root, "prompts/state/ACTIVE.json", {"artifact":"ATHENA.PROMPT.STATE.ACTIVE.V1","status":"ACTIVE","profile":"MAXDEV","enabled_modules":["core"],"active_scoped_overlays":[],"revision":1})
    _write(root, "policies/PROMPT_RUNTIME.md", "POLICY\n"); _write(root, "prompts/ORCHESTRATION_CORE.md", "CORE\n")
    _run(root, "add", "."); _run(root, "commit", "-m", "seed")
    git = GitBackend(root); prompt = PromptRuntime(git); pipeline = RollingQuestPipelineRuntime(git, prompt); breadth = NextQuestBreadthRuntime(pipeline)
    outcomes = NextScoutOutcomeValueRuntime(pipeline, breadth); cf = NextScoutCounterfactualCreditRuntime(pipeline, breadth, outcomes)
    return root, git, NextScoutCausalPromotionRuntime(cf)


def _pair(pipeline_id: str, idx: int, delta: float = 0.30) -> dict:
    row = {
        "artifact": PAIR_ARTIFACT,
        "pair_id": f"PAIR-{idx}",
        "pipeline_id": pipeline_id,
        "prep_kind": "TEST_DESIGN",
        "treated_receipt_id": f"T-{idx}",
        "control_receipt_id": f"C-{idx}",
        "treated_quest_id": f"TQ-{idx}",
        "control_quest_id": f"CQ-{idx}",
        "matching_basis": {"observed": True, "source": "fixture", "independent_of_scout": True, "pre_treatment_covariates": {"treated":{"difficulty":"M"},"control":{"difficulty":"M"}}, "covariate_digest": "fixture"},
        "outcome_delta": {"downstream_success": delta, "test_quality": delta, "low_rework": delta, "blocker_resolution": delta},
        "created_at": "2026-08-09T00:00:00+00:00",
        "actor": "fixture",
        "standing": "MATCHED_OBSERVATIONAL_CONTRAST",
        "causal_proof": False,
        "authority": "COUNTERFACTUAL_ANALYSIS_ONLY",
        "laws": [],
    }
    row["pair_digest"] = v8_digest(row)
    return row


class CausalPromotionV9Tests(unittest.TestCase):
    def setUp(self):
        td = tempfile.TemporaryDirectory(); self.addCleanup(td.cleanup)
        self.root, self.git, self.runtime = _runtime(Path(td.name))
        self.pipeline_id = "NQP-V9TEST"
        pair_root = self.root / f"prompts/next_quest_pipelines/{self.pipeline_id}/counterfactual/v8/pairs"
        pair_root.mkdir(parents=True)
        for i in range(1, 7):
            p = _pair(self.pipeline_id, i, 0.30 if i <= 3 else 0.24)
            (pair_root / f"{p['pair_id']}.json").write_text(json.dumps(p, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        _run(self.root, "add", "."); _run(self.root, "commit", "-m", "pairs")

    @staticmethod
    def _split():
        return {"observed": True, "source": "trial-registry://split", "independent_of_scout": True, "assigned_before_outcome": True}

    def test_held_out_replication_emits_candidate_not_mutation(self):
        frozen = self.runtime.freeze(pipeline_id=self.pipeline_id, prep_kind="TEST_DESIGN",
            discovery_pair_ids=["PAIR-1","PAIR-2","PAIR-3"], validation_pair_ids=["PAIR-4","PAIR-5","PAIR-6"],
            split_basis=self._split(), expected_git_head=self.git.head())
        result = self.runtime.evaluate(pipeline_id=self.pipeline_id, cohort_id=frozen["cohort"]["cohort_id"])
        self.assertEqual(result["standing"], "BENEFIT_PRIOR_PROMOTION_CANDIDATE")
        self.assertFalse(result["causal_proof"])
        self.assertEqual(result["live_benefit_prior_mutation"], "NONE")
        self.assertEqual(result["allocation_effect"], "NONE")
        overlay = self.runtime.overlay(pipeline_id=self.pipeline_id, cohort_id=frozen["cohort"]["cohort_id"])
        self.assertEqual(overlay["promotion_effect"], "NONE")

    def test_preoutcome_assignment_is_required(self):
        split = self._split(); split["assigned_before_outcome"] = False
        with self.assertRaisesRegex(ValueError, "PREOUTCOME"):
            self.runtime.freeze(pipeline_id=self.pipeline_id, prep_kind="TEST_DESIGN",
                discovery_pair_ids=["PAIR-1","PAIR-2","PAIR-3"], validation_pair_ids=["PAIR-4","PAIR-5","PAIR-6"],
                split_basis=split, expected_git_head=self.git.head())

    def test_pair_overlap_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "PAIR_OVERLAP"):
            self.runtime.freeze(pipeline_id=self.pipeline_id, prep_kind="TEST_DESIGN",
                discovery_pair_ids=["PAIR-1","PAIR-2","PAIR-3"], validation_pair_ids=["PAIR-3","PAIR-5","PAIR-6"],
                split_basis=self._split(), expected_git_head=self.git.head())

    def test_receipt_leakage_is_rejected_even_with_distinct_pair_ids(self):
        pair = _pair(self.pipeline_id, 7, 0.2); pair["treated_receipt_id"] = "T-1"; pair["pair_digest"] = v8_digest({k:v for k,v in pair.items() if k != "pair_digest"})
        path = self.root / f"prompts/next_quest_pipelines/{self.pipeline_id}/counterfactual/v8/pairs/PAIR-7.json"
        path.write_text(json.dumps(pair, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        _run(self.root, "add", "."); _run(self.root, "commit", "-m", "leak")
        with self.assertRaisesRegex(ValueError, "RECEIPT_LEAKAGE"):
            self.runtime.freeze(pipeline_id=self.pipeline_id, prep_kind="TEST_DESIGN",
                discovery_pair_ids=["PAIR-1","PAIR-2","PAIR-3"], validation_pair_ids=["PAIR-7","PAIR-5","PAIR-6"],
                split_basis=self._split(), expected_git_head=self.git.head())

    def test_validation_effect_collapse_abstains(self):
        # Build a second independent pipeline whose held-out deltas collapse.
        pipeline = "NQP-V9COLLAPSE"
        root = self.root / f"prompts/next_quest_pipelines/{pipeline}/counterfactual/v8/pairs"; root.mkdir(parents=True)
        for i in range(1, 7):
            p = _pair(pipeline, i, 0.30 if i <= 3 else 0.0)
            (root / f"{p['pair_id']}.json").write_text(json.dumps(p, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        _run(self.root, "add", "."); _run(self.root, "commit", "-m", "collapse")
        frozen = self.runtime.freeze(pipeline_id=pipeline, prep_kind="TEST_DESIGN",
            discovery_pair_ids=["PAIR-1","PAIR-2","PAIR-3"], validation_pair_ids=["PAIR-4","PAIR-5","PAIR-6"],
            split_basis=self._split(), expected_git_head=self.git.head())
        result = self.runtime.evaluate(pipeline_id=pipeline, cohort_id=frozen["cohort"]["cohort_id"])
        self.assertEqual(result["standing"], "ABSTAIN_HELD_OUT_VALIDATION")

    def test_version(self):
        self.assertEqual(VERSION, "ATHENA.NEXT.SCOUT.CAUSAL.PROMOTION.9")


if __name__ == "__main__": unittest.main()
