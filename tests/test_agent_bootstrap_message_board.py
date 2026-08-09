from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.agent_bootstrap import AGENT_BOOT_TOOLS, AgentBootstrapRuntime
from athena_mcp.git_backend import GitBackend
from athena_mcp.protocol import TOOLS


def _run(root: Path, *args: str) -> str:
    p = subprocess.run(
        ["git", "-C", str(root), *args], text=True, capture_output=True
    )
    if p.returncode:
        raise AssertionError(p.stderr or p.stdout)
    return p.stdout.strip()


def _clone(remote: Path, dest: Path) -> None:
    p = subprocess.run(
        ["git", "clone", str(remote), str(dest)], text=True, capture_output=True
    )
    if p.returncode:
        raise AssertionError(p.stderr or p.stdout)
    _run(dest, "config", "user.name", "test")
    _run(dest, "config", "user.email", "test@example.invalid")


class _Prompt:
    available = True

    def __init__(self, git):
        self.git = git

    def compile(self, task="", profile=None, include_text=False):
        return {
            "profile": profile or "BUILD",
            "selected_modules": ["core"],
            "selected_overlays": [],
            "git_head": self.git.head(),
            "prompt_stack_digest": "p" * 64,
            "ancestry": {"policy": "test"},
        }

    def _safe_rel(self, rel: str) -> Path:
        root = self.git.root.resolve()
        path = (root / rel).resolve()
        try:
            path.relative_to(root)
        except ValueError as exc:
            raise ValueError("test prompt path escapes git root") from exc
        return path


class _Frontier:
    def hydrate(self, **kwargs):
        return {
            "status": "HYDRATED",
            "source_ref": kwargs.get("source_ref"),
            "resolved_ref": kwargs.get("source_ref"),
            "source_head": "s" * 40,
            "frontier_digest": "f" * 64,
            "ready_work": [],
            "claims": [],
            "claim_readiness_suppressed": [],
            "residuals": [],
            "source_coverage": {"event_reduced_runs": 1},
            "sched_contract": {"status": "PASS", "contracts": {"reducer": "ok"}},
            "remote_checked": True,
            "fetch_error": None,
        }

    def select(self, **kwargs):
        return {
            "status": "NO_REPLAYABLE_READY_WORK",
            "selected": None,
            "pareto_front": [],
        }


class _Issues:
    def snapshot(self, **kwargs):
        return {
            "status": "FRESH",
            "fresh": True,
            "repo": "demeet2k/Athena",
            "relevant": [],
            "digest": "i" * 64,
            "witness": {"provider": "test", "http_status": 200},
        }


class AgentBootstrapMessageBoardTests(unittest.TestCase):
    def _fixture(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        base = Path(td.name)
        remote = base / "shared.git"
        subprocess.run(
            ["git", "init", "--bare", str(remote)], check=True, capture_output=True
        )
        seed = base / "seed"
        seed.mkdir()
        _run(seed, "init", "-b", "master")
        _run(seed, "config", "user.name", "test")
        _run(seed, "config", "user.email", "test@example.invalid")
        (seed / "seed.txt").write_text("seed\n", encoding="utf-8")
        _run(seed, "add", ".")
        _run(seed, "commit", "-m", "seed")
        _run(seed, "remote", "add", "origin", str(remote))
        _run(seed, "push", "-u", "origin", "master")
        subprocess.run(
            [
                "git",
                "--git-dir",
                str(remote),
                "symbolic-ref",
                "HEAD",
                "refs/heads/master",
            ],
            check=True,
        )
        a = base / "a"
        b = base / "b"
        c = base / "c"
        _clone(remote, a)
        _clone(remote, b)
        _clone(remote, c)
        return remote, a, b, c

    @staticmethod
    def _runtime(root: Path):
        git = GitBackend(root)
        return AgentBootstrapRuntime(git, _Prompt(git), _Frontier(), _Issues())

    @staticmethod
    def _boot(runtime, agent_id, task, **coordination):
        return runtime.bootstrap(
            agent_id=agent_id,
            task=task,
            fetch=False,
            shared_remote_mode="REQUIRED",
            continuation_shared_remote_mode="DISABLED",
            **coordination,
        )

    def test_auto_claims_then_reuses_same_presence_without_head_churn(self):
        _, a, _, _ = self._fixture()
        runtime = self._runtime(a)
        first = self._boot(
            runtime,
            "agent-a",
            "build parser",
            work_key="WK:PARSER",
            targets=["athena_mcp/parser.py"],
        )
        self.assertEqual(first["coordination"]["pre_dispatch"], "ALLOW", first)
        self.assertEqual(first["coordination"]["status"], "PRESENT", first)
        self.assertEqual(first["status"], "BOOTSTRAPPED", first)
        claim_id = first["coordination"]["presence"]["claim_id"]
        head = _run(a, "rev-parse", "HEAD")

        second = self._boot(
            runtime,
            "agent-a",
            "build parser",
            work_key="WK:PARSER",
            targets=["athena_mcp/parser.py"],
        )
        self.assertEqual(second["coordination"]["status"], "PRESENCE_REUSED", second)
        self.assertEqual(second["coordination"]["pre_dispatch"], "ALLOW", second)
        self.assertEqual(second["coordination"]["presence"]["claim_id"], claim_id)
        self.assertEqual(_run(a, "rev-parse", "HEAD"), head)
        self.assertEqual(
            second["coordination"]["routing_digest"],
            first["coordination"]["routing_digest"],
        )

    def test_second_agent_exact_duplicate_holds_without_second_claim(self):
        _, a, b, _ = self._fixture()
        first = self._boot(
            self._runtime(a),
            "agent-a",
            "build parser",
            work_key="WK:PARSER",
        )
        self.assertEqual(first["coordination"]["pre_dispatch"], "ALLOW", first)

        duplicate = self._boot(
            self._runtime(b),
            "agent-b",
            "build parser",
            work_key="WK:PARSER",
        )
        self.assertEqual(duplicate["coordination"]["status"], "DUPLICATE_WORK_HOLD")
        self.assertEqual(duplicate["coordination"]["pre_dispatch"], "HOLD")
        self.assertEqual(duplicate["status"], "BOOTSTRAP_HOLD")
        self.assertIn("MESSAGE_BOARD_PRE_DISPATCH_HOLD", duplicate["holds"])
        self.assertFalse(
            (b / "runtime/message_board/v1/agents/agent-b.json").exists()
        )

    def test_same_agent_different_work_holds_until_release(self):
        _, a, _, _ = self._fixture()
        runtime = self._runtime(a)
        first = self._boot(runtime, "agent-a", "build parser")
        head = _run(a, "rev-parse", "HEAD")
        switched = self._boot(runtime, "agent-a", "build renderer")
        self.assertEqual(switched["coordination"]["status"], "AGENT_ALREADY_PRESENT_HOLD")
        self.assertEqual(switched["coordination"]["pre_dispatch"], "HOLD")
        self.assertIn("TASK", switched["coordination"]["differences"])
        self.assertEqual(_run(a, "rev-parse", "HEAD"), head)
        self.assertEqual(
            switched["coordination"]["presence"]["claim_id"],
            first["coordination"]["presence"]["claim_id"],
        )

    def test_explicit_replica_can_overlap_primary(self):
        _, a, b, _ = self._fixture()
        self._boot(
            self._runtime(a),
            "agent-a",
            "benchmark kernel",
            work_key="WK:KERNEL",
        )
        replica = self._boot(
            self._runtime(b),
            "agent-b",
            "benchmark kernel",
            work_key="WK:KERNEL",
            coordination_claim_mode="REPLICA",
            replication_reason="independent implementation witness",
        )
        self.assertEqual(replica["coordination"]["pre_dispatch"], "ALLOW", replica)
        self.assertEqual(replica["coordination"]["presence"]["mode"], "REPLICA")
        self.assertTrue(
            any(
                edge.get("intentional")
                for edge in replica["coordination"]["board"]["exact_overlaps"]
            )
        )

    def test_replica_requires_explicit_reason(self):
        _, a, _, _ = self._fixture()
        with self.assertRaisesRegex(ValueError, "REPLICA requires replication_reason"):
            self._boot(
                self._runtime(a),
                "agent-a",
                "benchmark kernel",
                coordination_claim_mode="REPLICA",
            )

    def test_fuzzy_similarity_is_warning_not_veto(self):
        _, a, b, _ = self._fixture()
        self._boot(
            self._runtime(a),
            "agent-a",
            "build agent bootstrap message board gate",
        )
        second = self._boot(
            self._runtime(b),
            "agent-b",
            "build agent bootstrap message board integration",
        )
        self.assertEqual(second["coordination"]["pre_dispatch"], "ALLOW", second)
        self.assertEqual(second["coordination"]["status"], "PRESENT", second)
        self.assertTrue(
            second["coordination"]["transition"].get("potential_overlaps"), second
        )

    def test_read_only_is_advisory_and_does_not_create_presence(self):
        _, a, _, _ = self._fixture()
        packet = self._boot(
            self._runtime(a),
            "agent-a",
            "inspect parser",
            coordination_mode="READ_ONLY",
        )
        self.assertEqual(packet["coordination"]["pre_dispatch"], "ADVISORY_ONLY")
        self.assertFalse(
            (a / "runtime/message_board/v1/agents/agent-a.json").exists()
        )

    def test_disabled_preserves_legacy_boot_without_board_state(self):
        _, a, _, _ = self._fixture()
        packet = self._boot(
            self._runtime(a),
            "agent-a",
            "offline inspect",
            coordination_mode="DISABLED",
        )
        self.assertEqual(packet["coordination"]["pre_dispatch"], "DISABLED")
        self.assertEqual(packet["status"], "BOOTSTRAPPED", packet)
        self.assertFalse((a / "runtime/message_board/v1").exists())

    def test_auto_failed_shared_freshness_fails_closed(self):
        _, a, _, _ = self._fixture()
        missing = a.parent / "missing.git"
        _run(a, "remote", "set-url", "origin", str(missing))
        packet = self._boot(self._runtime(a), "agent-a", "build parser")
        self.assertEqual(packet["coordination"]["pre_dispatch"], "HOLD", packet)
        self.assertFalse(packet["coordination"]["shared_frontier_verified"])
        self.assertEqual(packet["status"], "BOOTSTRAP_HOLD")
        self.assertIn("MESSAGE_BOARD_PRE_DISPATCH_HOLD", packet["holds"])

    def test_refresh_reuses_claim_and_does_not_self_invalidate_git_head(self):
        _, a, _, _ = self._fixture()
        runtime = self._runtime(a)
        first = self._boot(runtime, "agent-a", "build parser")
        head = _run(a, "rev-parse", "HEAD")
        refreshed = runtime.refresh(
            session_id=first["session_id"],
            shared_remote_mode="REQUIRED",
            continuation_shared_remote_mode="DISABLED",
        )
        self.assertEqual(refreshed["coordination"]["status"], "PRESENCE_REUSED")
        self.assertEqual(_run(a, "rev-parse", "HEAD"), head)
        self.assertFalse(refreshed["refresh"]["changed"]["git_head"], refreshed)
        self.assertFalse(refreshed["refresh"]["coordination_changed"], refreshed)

    def test_call_tool_schema_and_dispatch_accept_coordination_fields(self):
        _, a, _, _ = self._fixture()
        boot_schema = next(
            tool["inputSchema"]
            for tool in AGENT_BOOT_TOOLS
            if tool["name"] == "athena_agent_bootstrap"
        )
        for field in (
            "coordination_mode",
            "work_key",
            "targets",
            "coordination_claim_mode",
            "lease_seconds",
            "replication_reason",
        ):
            self.assertIn(field, boot_schema["properties"])
        protocol_boot = next(
            tool for tool in TOOLS if tool["name"] == "athena_agent_bootstrap"
        )
        self.assertIn(
            "coordination_mode", protocol_boot["inputSchema"]["properties"]
        )

        packet = self._runtime(a).call_tool(
            "athena_agent_bootstrap",
            {
                "agent_id": "agent-a",
                "task": "build parser",
                "fetch": False,
                "shared_remote_mode": "REQUIRED",
                "continuation_shared_remote_mode": "DISABLED",
                "coordination_mode": "AUTO",
                "work_key": "WK:PARSER",
                "targets": ["athena_mcp/parser.py"],
            },
        )
        self.assertEqual(packet["coordination"]["pre_dispatch"], "ALLOW", packet)

    def test_extension_spec_declares_message_board_as_sole_authority(self):
        import json

        spec_path = Path(__file__).resolve().parents[1] / "spec" / "AGENT_BOOT_MESSAGE_BOARD_V1.json"
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
        self.assertEqual(spec["artifact"], "ATHENA.AGENT.BOOT.MESSAGE_BOARD.V1")
        self.assertEqual(
            spec["authority"]["message_board"],
            "sole presence/claim/message/ack authority",
        )
        self.assertEqual(spec["inputs"]["coordination_mode"]["default"], "AUTO")
        self.assertIn(
            "MISSING_WORK_KEY != FABRICATED_MATA_WORK_KEY",
            spec["laws"],
        )


if __name__ == "__main__":
    unittest.main()
