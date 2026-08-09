from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.continuation_raw_observer import (
    ARTIFACT,
    TOOL_NAME,
    ContinuationRawObserver,
)
from athena_mcp.git_backend import GitBackend
from athena_mcp.prompt_runtime import PROMPT_RUNTIME_TOOL_NAMES, PromptRuntime
from athena_mcp.protocol import TOOLS


def _run(root: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True)
    if p.returncode:
        raise AssertionError(p.stderr or p.stdout)
    return p.stdout.strip()


def _write(root: Path, rel: str, value) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(value, str):
        path.write_text(value, encoding="utf-8")
    else:
        path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _repo(base: Path) -> tuple[Path, GitBackend]:
    root = base / "brain"
    root.mkdir()
    _run(root, "init", "-b", "master")
    _run(root, "config", "user.name", "test")
    _run(root, "config", "user.email", "test@example.invalid")
    _write(root, "seed.txt", "seed\n")
    _run(root, "add", ".")
    _run(root, "commit", "-m", "seed")
    return root, GitBackend(root)


def _receipt(created_at: str, *, terminal_gate: str = "REJECTED_CONTINUE") -> dict:
    return {
        "artifact": "ATHENA.REHYDRATION.RECEIPT.V1",
        "loop_id": "loop-a",
        "step_index": 1,
        "actor": "agent-a",
        "created_at": created_at,
        "work_head": "a" * 40,
        "changed_paths": ["work.txt"],
        "material_work_paths": ["work.txt"],
        "completion": {
            "status": "SUCCEEDED",
            "observed": True,
            "terminal": False,
            "self_steer": True,
            "summary": "runtime rejected premature closure and continued",
            "terminal_gate": {
                "artifact": "ATHENA.REHYDRATION.TERMINAL.GATE.V1",
                "status": terminal_gate,
                "requested_terminal": True,
                "reasons": ["KNOWN_RESIDUAL_WORK_REMAINS"],
            },
            "residuals": ["work remains"],
            "tests": [{"name": "unit", "status": "PASS"}],
        },
        "no_progress": False,
        "next_status": "ACTIVE",
    }


def _rehydration_event(created_at: str) -> dict:
    return {
        "artifact": "ATHENA.REHYDRATION.EVENT.V1",
        "loop_id": "loop-a",
        "step_index": 0,
        "created_at": created_at,
        "prompt_path": "prompts/rehydration/loop-a/prompts/0000.md",
    }


def _message_event(created_at: str, event_id: str = "MBE-1") -> dict:
    return {
        "artifact": "ATHENA.MESSAGE.BOARD.EVENT.V1",
        "event_id": event_id,
        "kind": "MESSAGE",
        "agent_id": "agent-a",
        "created_at": created_at,
        "git_parent": "b" * 40,
        "payload": {"message_kind": "UPDATE", "message": "still working"},
        "recipients": [],
        "reply_to": None,
    }


def _commit_trace(root: Path) -> None:
    _run(root, "add", ".")
    _run(root, "commit", "-m", "persist raw trace")


class ContinuationRawObserverTests(unittest.TestCase):
    def test_collects_exact_raw_records_deterministically_without_classification(self):
        with tempfile.TemporaryDirectory() as td:
            root, git = _repo(Path(td))
            _write(root, "prompts/rehydration/loop-a/events/0000-start.json", _rehydration_event("2026-08-09T10:00:00Z"))
            _write(root, "prompts/rehydration/loop-a/receipts/0001.json", _receipt("2026-08-09T10:05:00Z"))
            _write(root, "runtime/message_board/v1/events/2026/08/09/m1.json", _message_event("2026-08-09T10:06:00Z"))
            _commit_trace(root)

            observer = ContinuationRawObserver(git)
            first = observer.read(
                window_start="2026-08-09T10:00:00Z",
                window_end="2026-08-09T11:00:00Z",
                expected_git_head=git.head(),
            )
            second = observer.read(
                window_start="2026-08-09T10:00:00+00:00",
                window_end="2026-08-09T11:00:00+00:00",
                expected_git_head=git.head(),
            )

            self.assertEqual(first["artifact"], ARTIFACT)
            self.assertEqual(first["status"], "OK")
            self.assertTrue(first["coverage_complete"])
            self.assertEqual(first["returned_record_count"], 3)
            self.assertEqual(first["trace_digest"], second["trace_digest"])
            self.assertFalse(first["authority"]["classification"])
            self.assertFalse(first["authority"]["behavioral_effect"])
            self.assertFalse(first["authority"]["causal_effect"])
            self.assertFalse(first["authority"]["promotion"])
            self.assertFalse(first["external_mutation_performed"])

            receipt = next(row for row in first["records"] if row["category"] == "REHYDRATION_RECEIPT")
            self.assertEqual(
                receipt["record"]["completion"]["terminal_gate"]["status"],
                "REJECTED_CONTINUE",
            )
            self.assertTrue(receipt["record"]["completion"]["self_steer"])
            self.assertRegex(receipt["git_blob_sha"], r"^[0-9a-f]{40}$")
            self.assertRegex(receipt["record_sha256"], r"^sha256:[0-9a-f]{64}$")

    def test_window_is_half_open(self):
        with tempfile.TemporaryDirectory() as td:
            root, git = _repo(Path(td))
            _write(root, "runtime/message_board/v1/events/2026/08/09/start.json", _message_event("2026-08-09T10:00:00Z", "MBE-start"))
            _write(root, "runtime/message_board/v1/events/2026/08/09/end.json", _message_event("2026-08-09T11:00:00Z", "MBE-end"))
            _commit_trace(root)
            result = ContinuationRawObserver(git).read(
                window_start="2026-08-09T10:00:00Z",
                window_end="2026-08-09T11:00:00Z",
            )
            self.assertEqual([row["record"]["event_id"] for row in result["records"]], ["MBE-start"])

    def test_malformed_tracked_source_fails_coverage_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root, git = _repo(Path(td))
            _write(root, "prompts/rehydration/loop-a/receipts/0001.json", {
                "artifact": "WRONG.ARTIFACT",
                "created_at": "2026-08-09T10:05:00Z",
            })
            _commit_trace(root)
            result = ContinuationRawObserver(git).read(
                window_start="2026-08-09T10:00:00Z",
                window_end="2026-08-09T11:00:00Z",
            )
            self.assertEqual(result["status"], "TRACE_INTEGRITY_HOLD")
            self.assertFalse(result["coverage_complete"])
            self.assertEqual(result["malformed_sources"][0]["error"], "ARTIFACT_IDENTITY_MISMATCH")
            self.assertFalse(result["authority"]["behavioral_effect"])

    def test_dirty_root_holds_without_reading_mixed_state(self):
        with tempfile.TemporaryDirectory() as td:
            root, git = _repo(Path(td))
            (root / "untracked.txt").write_text("not committed\n", encoding="utf-8")
            result = ContinuationRawObserver(git).read(
                window_start="2026-08-09T10:00:00Z",
                window_end="2026-08-09T11:00:00Z",
            )
            self.assertEqual(result["status"], "HOLD_DIRTY_GIT_ROOT")
            self.assertFalse(result["coverage_complete"])
            self.assertEqual(result["records"], [])

    def test_stale_expected_head_holds(self):
        with tempfile.TemporaryDirectory() as td:
            _, git = _repo(Path(td))
            result = ContinuationRawObserver(git).read(
                window_start="2026-08-09T10:00:00Z",
                window_end="2026-08-09T11:00:00Z",
                expected_git_head="0" * 40,
            )
            self.assertEqual(result["status"], "HOLD_STALE_GIT_HEAD")
            self.assertFalse(result["coverage_complete"])

    def test_record_limit_is_typed_incomplete_coverage_not_silent_truncation(self):
        with tempfile.TemporaryDirectory() as td:
            root, git = _repo(Path(td))
            _write(root, "runtime/message_board/v1/events/2026/08/09/one.json", _message_event("2026-08-09T10:01:00Z", "MBE-1"))
            _write(root, "runtime/message_board/v1/events/2026/08/09/two.json", _message_event("2026-08-09T10:02:00Z", "MBE-2"))
            _commit_trace(root)
            result = ContinuationRawObserver(git).read(
                window_start="2026-08-09T10:00:00Z",
                window_end="2026-08-09T11:00:00Z",
                max_records=1,
            )
            self.assertEqual(result["status"], "TRACE_INTEGRITY_HOLD")
            self.assertTrue(result["record_limit_exceeded"])
            self.assertEqual(result["total_matching_records"], 2)
            self.assertEqual(result["returned_record_count"], 1)

    def test_read_does_not_mutate_git(self):
        with tempfile.TemporaryDirectory() as td:
            root, git = _repo(Path(td))
            _write(root, "runtime/message_board/v1/events/2026/08/09/m1.json", _message_event("2026-08-09T10:06:00Z"))
            _commit_trace(root)
            before_head = git.head()
            before_status = _run(root, "status", "--porcelain")
            result = ContinuationRawObserver(git).read(
                window_start="2026-08-09T10:00:00Z",
                window_end="2026-08-09T11:00:00Z",
                expected_git_head=before_head,
            )
            self.assertEqual(result["status"], "OK")
            self.assertEqual(git.head(), before_head)
            self.assertEqual(_run(root, "status", "--porcelain"), before_status)

    def test_tool_is_registered_and_prompt_runtime_dispatches_it(self):
        self.assertIn(TOOL_NAME, PROMPT_RUNTIME_TOOL_NAMES)
        self.assertIn(TOOL_NAME, {tool["name"] for tool in TOOLS})
        with tempfile.TemporaryDirectory() as td:
            _, git = _repo(Path(td))
            runtime = PromptRuntime(git)
            result = runtime.call_tool(
                TOOL_NAME,
                {
                    "window_start": "2026-08-09T10:00:00Z",
                    "window_end": "2026-08-09T11:00:00Z",
                    "expected_git_head": git.head(),
                },
            )
            self.assertEqual(result["artifact"], ARTIFACT)
            self.assertEqual(result["status"], "OK")


if __name__ == "__main__":
    unittest.main()
