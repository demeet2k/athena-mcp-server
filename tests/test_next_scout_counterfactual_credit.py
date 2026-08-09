from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.git_backend import GitBackend
from athena_mcp.next_quest_pipeline import RollingQuestPipelineRuntime
from athena_mcp.next_quest_pipeline_breadth import NextQuestBreadthRuntime
from athena_mcp.next_scout_counterfactual_credit import NextScoutCounterfactualCreditRuntime, VERSION
from athena_mcp.next_scout_outcome_value import NextScoutOutcomeValueRuntime
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


def _brain(base: Path):
    root = base / "brain"; root.mkdir()
    _run(root, "init"); _run(root, "config", "user.name", "test"); _run(root, "config", "user.email", "test@example.invalid")
    _write(root, "prompts/PROMPT.manifest.json", {"artifact":"ATHENA.PROMPT.RUNTIME.V1","authority_ceiling":"below external authority","active_state":"prompts/state/ACTIVE.json","policy":"policies/PROMPT_RUNTIME.md","default_profile":"MAXDEV","profiles":{"MAXDEV":["core"]},"modules":{"core":{"path":"prompts/ORCHESTRATION_CORE.md","order":0,"mandatory":True}}})
    _write(root, "prompts/state/ACTIVE.json", {"artifact":"ATHENA.PROMPT.STATE.ACTIVE.V1","status":"ACTIVE","profile":"MAXDEV","enabled_modules":["core"],"active_scoped_overlays":[],"revision":1})
    _write(root, "policies/PROMPT_RUNTIME.md", "POLICY\n"); _write(root, "prompts/ORCHESTRATION_CORE.md", "CORE\n")
    _run(root, "add", "."); _run(root, "commit", "-m", "seed")
    git = GitBackend(root); prompt = PromptRuntime(git); pipeline = RollingQuestPipelineRuntime(git, prompt); breadth = NextQuestBreadthRuntime(pipeline); outcomes = NextScoutOutcomeValueRuntime(pipeline, breadth)
    runtime = NextScoutCounterfactualCreditRuntime(pipeline, breadth, outcomes)
    return root, git, runtime


def _receipt(rid: str, qid: str, *, treated: bool, score: float) -> dict:
    prep = [{"plan_id": f"p-{rid}", "kind": "TEST_DESIGN", "plan_digest": "p", "observation_digest": "o"}] if treated else [{"plan_id": f"p-{rid}", "kind": "RISK_SCAN", "plan_digest": "p", "observation_digest": "o"}]
    return {
        "artifact": "ATHENA.NEXT.FOCUS.OUTCOME.RECEIPT.7",
        "receipt_id": rid,
        "pipeline_id": "P1",
        "quest": {"quest_id": qid, "task": qid},
        "associated_prep": prep,
        "outcome_scores": {"downstream_success": score, "test_quality": score, "low_rework": score},
    }


class CounterfactualCreditTests(unittest.TestCase):
    def setUp(self):
        td = tempfile.TemporaryDirectory(); self.addCleanup(td.cleanup)
        self.root, self.git, self.runtime = _brain(Path(td.name))
        self.receipts = [
            _receipt("t1", "qt1", treated=True, score=1.0), _receipt("c1", "qc1", treated=False, score=0.4),
            _receipt("t2", "qt2", treated=True, score=0.9), _receipt("c2", "qc2", treated=False, score=0.4),
            _receipt("t3", "qt3", treated=True, score=0.8), _receipt("c3", "qc3", treated=False, score=0.4),
        ]
        self.runtime.outcomes._read_receipts = lambda pipeline_id: list(self.receipts)

    def _basis(self, source: str = "independent-fixture"):
        cov = {"complexity_band":"M", "domain":"repo", "risk_band":"LOW"}
        return {"observed":True,"source":source,"independent_of_scout":True,"pre_treatment_covariates":{"treated":dict(cov),"control":dict(cov)}}

    def _pair(self, treated: str, control: str):
        return self.runtime.record_pair(pipeline_id="P1", prep_kind="TEST_DESIGN", treated_receipt_id=treated, control_receipt_id=control, matching_basis=self._basis(f"match:{treated}:{control}"), expected_git_head=self.git.head())

    def test_three_independent_pairs_generate_candidate_not_mutation(self):
        self._pair("t1", "c1"); self._pair("t2", "c2"); self._pair("t3", "c3")
        estimate = self.runtime.estimate(pipeline_id="P1", prep_kind="TEST_DESIGN", min_pairs=3, min_effect=0.05)
        self.assertEqual(estimate["standing"], "BENEFIT_PRIOR_CANDIDATE")
        self.assertFalse(estimate["causal_proof"])
        self.assertEqual(estimate["benefit_prior_mutation"], "NONE")
        self.assertEqual(estimate["allocation_effect"], "NONE")
        self.assertIn("test_quality", estimate["passing_metrics"])
        overlay = self.runtime.overlay(pipeline_id="P1")
        self.assertTrue(overlay["benefit_prior_candidates"]["TEST_DESIGN"]["candidate"])
        self.assertEqual(overlay["allocation_effect"], "NONE")

    def test_post_treatment_matching_is_rejected(self):
        bad = self._basis(); bad["pre_treatment_covariates"]["treated"]["completion_status"] = "SUCCEEDED"; bad["pre_treatment_covariates"]["control"]["completion_status"] = "SUCCEEDED"
        with self.assertRaisesRegex(ValueError, "POST_TREATMENT"):
            self.runtime.record_pair(pipeline_id="P1", prep_kind="TEST_DESIGN", treated_receipt_id="t1", control_receipt_id="c1", matching_basis=bad, expected_git_head=self.git.head())

    def test_target_prep_must_differ_between_treatment_and_control(self):
        with self.assertRaisesRegex(ValueError, "CONTROL_RECEIPT_CONTAINS"):
            self.runtime.record_pair(pipeline_id="P1", prep_kind="TEST_DESIGN", treated_receipt_id="t1", control_receipt_id="t2", matching_basis=self._basis(), expected_git_head=self.git.head())

    def test_matching_basis_requires_independent_source_and_exact_covariates(self):
        bad = self._basis(); bad["independent_of_scout"] = False
        with self.assertRaisesRegex(ValueError, "independent_of_scout"):
            self.runtime.record_pair(pipeline_id="P1", prep_kind="TEST_DESIGN", treated_receipt_id="t1", control_receipt_id="c1", matching_basis=bad, expected_git_head=self.git.head())
        bad = self._basis(); bad["pre_treatment_covariates"]["control"]["risk_band"] = "HIGH"
        with self.assertRaisesRegex(ValueError, "DO_NOT_EXACTLY_MATCH"):
            self.runtime.record_pair(pipeline_id="P1", prep_kind="TEST_DESIGN", treated_receipt_id="t1", control_receipt_id="c1", matching_basis=bad, expected_git_head=self.git.head())

    def test_pseudoreplication_forces_abstention(self):
        self._pair("t1", "c1"); self._pair("t1", "c2"); self._pair("t3", "c3")
        estimate = self.runtime.estimate(pipeline_id="P1", prep_kind="TEST_DESIGN", min_pairs=3)
        self.assertTrue(estimate["independence_hold"])
        self.assertEqual(estimate["standing"], "ABSTAIN_INSUFFICIENT_COUNTERFACTUAL_SUPPORT")
        self.assertFalse(any(row["passes_candidate_gate"] for row in estimate["metrics"].values()))

    def test_pair_identity_is_idempotent(self):
        first = self._pair("t1", "c1")
        second = self.runtime.record_pair(pipeline_id="P1", prep_kind="TEST_DESIGN", treated_receipt_id="t1", control_receipt_id="c1", matching_basis=self._basis("match:t1:c1"), expected_git_head=self.git.head())
        self.assertEqual(first["pair"]["pair_id"], second["pair"]["pair_id"])
        self.assertEqual(second["status"], "REUSED")
        self.assertFalse(second["git_mutation"])

    def test_version(self):
        self.assertEqual(VERSION, "ATHENA.NEXT.SCOUT.COUNTERFACTUAL.CREDIT.8")


if __name__ == "__main__": unittest.main()
