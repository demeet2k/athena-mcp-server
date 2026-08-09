from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.git_backend import GitBackend
from athena_mcp.next_quest_pipeline import RollingQuestPipelineRuntime, VERSION
from athena_mcp.prompt_runtime import PromptRuntime
from athena_mcp.rehydration_loop import _sha


def _run(root: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True)
    if p.returncode:
        raise AssertionError(p.stderr or p.stdout)
    return p.stdout.strip()


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _runtime(base: Path) -> tuple[RollingQuestPipelineRuntime, Path]:
    root = base / "brain"
    root.mkdir()
    _run(root, "init")
    _run(root, "config", "user.name", "test")
    _run(root, "config", "user.email", "test@example.invalid")
    manifest = {
        "artifact": "ATHENA.PROMPT.RUNTIME.V1",
        "authority_ceiling": "below external authority",
        "active_state": "prompts/state/ACTIVE.json",
        "policy": "policies/PROMPT_RUNTIME.md",
        "default_profile": "MAXDEV",
        "profiles": {"MAXDEV": ["core"]},
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
    return RollingQuestPipelineRuntime(git, prompt), root


def _baton(status="SELECTED", task="Quest four", candidate_id="SC-4"):
    selected = {"candidate_id": candidate_id, "task": task, "routing_score": 1.0, "metrics": {}, "source": "EXPLICIT_CANDIDATE"}
    value = {
        "artifact": "ATHENA.REHYDRATION.SUCCESSOR.BATON.V1",
        "status": status,
        "selected": selected if status == "SELECTED" else None,
        "ties": [],
        "candidates": [selected],
    }
    value["baton_digest"] = _sha(value)
    return value


def _ambiguous():
    ties = [
        {"candidate_id": "SC-A", "task": "Quest four A", "routing_score": 1.0},
        {"candidate_id": "SC-B", "task": "Quest four B", "routing_score": 1.0},
    ]
    value = {"artifact": "ATHENA.REHYDRATION.SUCCESSOR.BATON.V1", "status": "AMBIGUOUS", "selected": None, "ties": ties, "candidates": ties}
    value["baton_digest"] = _sha(value)
    return value


class NextQuestPipelineTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.runtime, self.root = _runtime(Path(self.td.name))

    def _start(self):
        return self.runtime.start(goal="Long campaign", quests=["Quest one", "Quest two", "Quest three"], expected_git_head=self.runtime.git.head())

    def test_start_has_one_focus_two_staged_and_reverse_display(self):
        started = self._start()
        self.assertEqual(started["status"], "ACTIVE")
        window = started["window"]
        self.assertEqual([x["task"] for x in window["execution_order"]], ["Quest one", "Quest two", "Quest three"])
        self.assertEqual([x["task"] for x in window["display_window"]], ["Quest three", "Quest two", "Quest one"])
        self.assertEqual(window["focus"]["role"], "FOCUS_Q1")

    def test_q1_completion_rotates_and_reseeds_q4(self):
        started = self._start()
        focus = started["window"]["focus"]
        result = self.runtime.rotate(
            pipeline_id=started["pipeline_id"], expected_state_digest=started["state_digest"], expected_checkpoint_head=started["checkpoint_head"],
            completed_quest_id=focus["quest_id"], completion={"observed": True, "status": "SUCCEEDED", "summary": "done", "evidence_refs": ["git://q1"]},
            successor_baton=_baton(),
        )
        self.assertEqual([x["task"] for x in result["window"]["execution_order"]], ["Quest two", "Quest three", "Quest four"])
        self.assertEqual(result["window"]["focus"]["task"], "Quest two")
        self.assertEqual(result["completed_count"], 1)
        self.assertEqual(self.runtime.verify(started["pipeline_id"])["status"], "PASS")

    def test_ambiguous_q4_preserved_until_explicit_resolution(self):
        started = self._start()
        focus = started["window"]["focus"]
        held = self.runtime.rotate(
            pipeline_id=started["pipeline_id"], expected_state_digest=started["state_digest"], expected_checkpoint_head=started["checkpoint_head"],
            completed_quest_id=focus["quest_id"], completion={"observed": True, "status": "SUCCEEDED", "summary": "done"}, successor_baton=_ambiguous(),
        )
        self.assertEqual(held["status"], "RESEED_HOLD")
        self.assertEqual([x["task"] for x in held["window"]["execution_order"]], ["Quest two", "Quest three"])
        resolved = self.runtime.resolve_reseed(
            pipeline_id=started["pipeline_id"], expected_state_digest=held["state_digest"], expected_checkpoint_head=held["checkpoint_head"], candidate_id="SC-A"
        )
        self.assertEqual(resolved["status"], "ACTIVE")
        self.assertEqual([x["task"] for x in resolved["window"]["execution_order"]], ["Quest two", "Quest three", "Quest four A"])

    def test_only_focus_can_complete(self):
        started = self._start()
        staged = started["window"]["execution_order"][1]
        with self.assertRaisesRegex(ValueError, "only current Q1"):
            self.runtime.rotate(
                pipeline_id=started["pipeline_id"], expected_state_digest=started["state_digest"], expected_checkpoint_head=started["checkpoint_head"],
                completed_quest_id=staged["quest_id"], completion={"observed": True, "status": "SUCCEEDED", "summary": "wrong"}, successor_baton=_baton(),
            )

    def test_duplicate_successor_does_not_silently_revisit(self):
        started = self._start()
        focus = started["window"]["focus"]
        held = self.runtime.rotate(
            pipeline_id=started["pipeline_id"], expected_state_digest=started["state_digest"], expected_checkpoint_head=started["checkpoint_head"],
            completed_quest_id=focus["quest_id"], completion={"observed": True, "status": "SUCCEEDED", "summary": "done"}, successor_baton=_baton(task="Quest two", candidate_id="SC-DUP"),
        )
        self.assertEqual(held["status"], "RESEED_HOLD")
        self.assertEqual(held["window"]["reseed_hold"]["status"], "NO_NOVEL_RESEED")

    def test_state_tamper_fails_verify(self):
        started = self._start()
        path = self.root / "prompts" / "next_quest_pipelines" / started["pipeline_id"] / "state.json"
        state = json.loads(path.read_text())
        state["goal"] = "tampered"
        path.write_text(json.dumps(state), encoding="utf-8")
        self.assertEqual(self.runtime.verify(started["pipeline_id"])["status"], "HOLD")

    def test_exact_three_initial_quests(self):
        with self.assertRaisesRegex(ValueError, "exactly three"):
            self.runtime.start(goal="g", quests=["a", "b"], expected_git_head=self.runtime.git.head())

    def test_artifact_version(self):
        self.assertEqual(VERSION, "ATHENA.NEXT.QUEST.PIPELINE.1")


if __name__ == "__main__":
    unittest.main()
