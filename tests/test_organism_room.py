from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from athena_mcp.git_backend import GitBackend
from athena_mcp.message_board import MessageBoardRuntime
from athena_mcp.organism_room import (
    OrganismRoomRuntime,
    _prompt_digest,
    allocate_population,
    make_authority_receipt,
    verify_authority_receipt,
)


def _run(root: Path, *args: str) -> str:
    proc = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True)
    if proc.returncode:
        raise AssertionError(proc.stderr or proc.stdout)
    return proc.stdout.strip()


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _fixture(base: Path, clone_names=("b",)):
    local = base / "local"
    local.mkdir()
    _run(local, "init", "-b", "master")
    _run(local, "config", "user.name", "local")
    _run(local, "config", "user.email", "local@example.invalid")
    _write(local, "prompts/PROMPT.manifest.json", '{"bootstrap":"prompts/BOOTSTRAP.md","core":"prompts/ORCHESTRATION_CORE.md","policy":"policies/PROMPT_RUNTIME.md","modules":{"core":{"path":"prompts/ORCHESTRATION_CORE.md"},"git":{"path":"prompts/modules/GIT_ORGANISM.md"}},"room":{"registry":"registry/organism_room_v1.json","harness_genotype":"registry/harness_genotype_v1.json","allocator":"scripts/organism_homeostasis_v1.py"}}\n')
    _write(local, "prompts/state/ACTIVE.json", '{"enabled_modules":["core","git"],"active_scoped_overlays":["prompts/overlays/ACTIVE.md"],"active_scoped_state":[],"harness_genotype":"registry/harness_genotype_v1.json"}\n')
    for rel in ("prompts/BOOTSTRAP.md", "prompts/ORCHESTRATION_CORE.md", "prompts/modules/GIT_ORGANISM.md", "prompts/overlays/ACTIVE.md", "policies/PROMPT_RUNTIME.md", "registry/organism_room_v1.json", "registry/harness_genotype_v1.json", "scripts/organism_homeostasis_v1.py"):
        _write(local, rel, f"fixture:{rel}\n")
    _run(local, "add", ".")
    _run(local, "commit", "-m", "seed")
    origin = base / "origin.git"
    proc = subprocess.run(["git", "init", "--bare", str(origin)], text=True, capture_output=True)
    if proc.returncode:
        raise AssertionError(proc.stderr or proc.stdout)
    _run(local, "remote", "add", "origin", str(origin))
    _run(local, "push", "-u", "origin", "master")
    clones = []
    for name in clone_names:
        clone = base / name
        subprocess.run(["git", "clone", str(origin), str(clone)], check=True, text=True, capture_output=True)
        _run(clone, "config", "user.name", name)
        _run(clone, "config", "user.email", f"{name}@example.invalid")
        clones.append(clone)
    return local, clones


class HomeostasisTests(unittest.TestCase):
    def test_domain_priors_and_exact_population(self):
        allocation = allocate_population([f"a{i:02}" for i in range(20)])
        self.assertEqual(sum(allocation["counts"].values()), 20)
        self.assertEqual(allocation["counts"]["BUILD_GIT"], 4)
        self.assertEqual(allocation["counts"]["MATH_MINE"], 3)
        self.assertEqual(allocation["counts"]["NAVIGATION"], 3)
        self.assertEqual(allocation["counts"]["DRIVE_DISTILL"], 3)
        self.assertEqual(allocation["counts"]["INTEGRATE_META"], 2)
        self.assertEqual(allocation["wave_counts"], {"IMMEDIATE": 10, "MIDDLE": 6, "RECURSIVE_META": 4})

    def test_small_population_is_builder_generalist_with_all_three_waves(self):
        for count in (1, 2, 3):
            allocation = allocate_population([f"a{i}" for i in range(count)])
            self.assertEqual(allocation["counts"]["BUILD_GIT"], count)
            self.assertEqual([row["wave"] for row in allocation["waves"]], ["IMMEDIATE", "MIDDLE", "RECURSIVE_META"])

    def test_empty_lane_lends_capacity(self):
        allocation = allocate_population([f"a{i}" for i in range(8)], {name: (1 if name == "MATH_MINE" else 0) for name in (
            "BUILD_GIT", "INTEGRATE_META", "NAVIGATION", "TOOL_LIMITS", "ALCHEMY", "DRIVE_DISTILL", "MATH_MINE", "MYTH_MINE"
        )})
        self.assertEqual(allocation["counts"]["MATH_MINE"], 8)

    def test_git_state_never_persists_bearer_token(self):
        # Checked end-to-end below; this protects the structural invariant at
        # the allocator/unit layer too by keeping the public shape token-free.
        self.assertNotIn("session_token", allocate_population(["a"]))


class ReceiptTests(unittest.TestCase):
    def test_external_mac_binds_every_authority_claim(self):
        claims = {"quest_id": "q", "attempt": 1, "session_id": "s", "fence": 1, "input_head": "h", "prompt_digest": "p", "artifact_digests": ["a"], "result": "PASS"}
        receipt = make_authority_receipt(claims, "host", b"k" * 32)
        verify_authority_receipt(receipt, claims, {"host": b"k" * 32})
        with self.assertRaisesRegex(ValueError, "BINDING_HOLD:quest_id"):
            verify_authority_receipt(receipt, {**claims, "quest_id": "other"}, {"host": b"k" * 32})
        with self.assertRaisesRegex(ValueError, "MAC_HOLD"):
            verify_authority_receipt(receipt, claims, {"host": b"x" * 32})


class RoomE2ETests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {"ATHENA_ROOM_SESSION_SECRET": "s" * 32}, clear=False)
        self.env.start()
        self.addCleanup(self.env.stop)

    def _rooms(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        local, clones = _fixture(Path(td.name))
        roots = [local, *clones]
        return [OrganismRoomRuntime(MessageBoardRuntime(GitBackend(root)), authority_keys={"host": b"h" * 32}) for root in roots], roots

    @staticmethod
    def _enter(room, root, agent, work, key=None):
        return room.enter(agent_id=agent, task=f"Build {work}", work_key=work, targets=[f"{work}.py"], ack_head=_run(root, "rev-parse", "HEAD"), ack_prompt_digest=_prompt_digest(root), idempotency_key=key or f"enter-{agent}-0123456789", lease_seconds=600)

    def test_enter_requires_exact_head_and_prompt_ack(self):
        rooms, roots = self._rooms()
        hold = rooms[0].enter(agent_id="a", task="Build x", work_key="x", targets=["x.py"], ack_head="stale", ack_prompt_digest="wrong", idempotency_key="enter-a-0123456789")
        self.assertEqual(hold["status"], "REHYDRATE_HOLD")
        entered = self._enter(rooms[0], roots[0], "a", "x")
        self.assertEqual(entered["status"], "ENTERED")
        self.assertEqual(rooms[1].read()["board"]["active"][0]["agent_id"], "a")

    def test_duplicate_work_holds_and_clean_signout_requires_closed_claim(self):
        rooms, roots = self._rooms()
        entered = self._enter(rooms[0], roots[0], "a", "x")
        _run(roots[1], "pull", "--ff-only", "origin", "master")
        duplicate = self._enter(rooms[1], roots[1], "b", "x")
        self.assertEqual(duplicate["status"], "DUPLICATE_WORK_HOLD")
        session = entered["session"]
        hold = rooms[0].sign_out(agent_id="a", session_id=session["session_id"], fence=session["fence"], session_token=entered["session_token"], idempotency_key="out-a-01234567890")
        self.assertEqual(hold["status"], "OPEN_CLAIM_HOLD")

    def test_verified_completion_creates_successor_then_signs_out(self):
        rooms, roots = self._rooms()
        room = rooms[0]
        entered = self._enter(room, roots[0], "a", "x")
        session = entered["session"]
        artifacts = ["sha256:artifact"]
        claims = {"quest_id": "x", "attempt": 1, "session_id": session["session_id"], "fence": session["fence"], "input_head": session["head"], "prompt_digest": session["prompt_digest"], "artifact_digests": artifacts, "result": "PASS"}
        receipt = make_authority_receipt(claims, "host", b"h" * 32)
        completed = room.complete(agent_id="a", session_id=session["session_id"], fence=session["fence"], session_token=entered["session_token"], artifact_digests=artifacts, result="PASS", receipt=receipt, residual="Integrate x into the caller", idempotency_key="complete-a-0123456")
        self.assertEqual(completed["status"], "VERIFIED_COMPLETION")
        self.assertFalse(completed["campaign_terminal"])
        self.assertEqual(completed["successor"]["status"], "READY")
        signed_out = room.sign_out(agent_id="a", session_id=session["session_id"], fence=session["fence"], session_token=entered["session_token"], idempotency_key="out-a-01234567890")
        self.assertEqual(signed_out["status"], "SIGNED_OUT")
        self.assertEqual(room.read()["board"]["active"], [])

    def test_claimant_self_hash_is_not_completion_authority(self):
        rooms, roots = self._rooms()
        entered = self._enter(rooms[0], roots[0], "a", "x")
        session = entered["session"]
        fake = {"artifact": "ATHENA.ORGANISM.ROOM.RECEIPT.V1", "authority_id": "claimant", "claims": {}, "mac": "self-hash"}
        with self.assertRaisesRegex(ValueError, "AUTHORITY_NOT_CONFIGURED"):
            rooms[0].complete(agent_id="a", session_id=session["session_id"], fence=session["fence"], session_token=entered["session_token"], artifact_digests=["a"], result="PASS", receipt=fake, terminal_reason="NO_RESIDUAL", idempotency_key="complete-a-0123456")

    def test_context_guard_forces_release_on_exception(self):
        rooms, roots = self._rooms()
        with self.assertRaisesRegex(RuntimeError, "boom"):
            with rooms[0].epoch(agent_id="a", task="Build x", work_key="x", targets=["x.py"], ack_head=_run(roots[0], "rev-parse", "HEAD"), ack_prompt_digest=_prompt_digest(roots[0]), idempotency_key="enter-a-0123456789", lease_seconds=600):
                raise RuntimeError("boom")
        self.assertEqual(rooms[0].read()["board"]["active"], [])

    def test_idempotency_replay_and_conflict(self):
        rooms, roots = self._rooms()
        room = rooms[0]
        args = dict(agent_id="a", task="Build x", work_key="x", targets=["x.py"], ack_head=_run(roots[0], "rev-parse", "HEAD"), ack_prompt_digest=_prompt_digest(roots[0]), idempotency_key="enter-a-0123456789", lease_seconds=600)
        first = room.enter(**args)
        replay = room.enter(**args)
        self.assertEqual(replay["session"]["session_id"], first["session"]["session_id"])
        self.assertEqual(replay["session_token"], first["session_token"])
        stored = room.read()["room"]["idempotency"]
        self.assertTrue(stored)
        self.assertTrue(all("enter-a" not in slot for slot in stored))
        self.assertNotIn("session_token", next(iter(stored.values()))["result"])
        with self.assertRaisesRegex(ValueError, "IDEMPOTENCY_KEY_REUSE_CONFLICT"):
            room.enter(**{**args, "task": "Build y"})

    def test_reentry_increments_fence_and_old_session_cannot_mutate(self):
        rooms, roots = self._rooms()
        room = rooms[0]
        first = self._enter(room, roots[0], "a", "x")
        old = first["session"]
        room.sign_out(agent_id="a", session_id=old["session_id"], fence=old["fence"], session_token=first["session_token"], idempotency_key="out-old-012345678", force=True)
        second = self._enter(room, roots[0], "a", "x", key="enter-a-again-0123")
        self.assertGreater(second["session"]["fence"], old["fence"])
        self.assertNotEqual(second["session"]["session_id"], old["session_id"])
        with self.assertRaisesRegex(ValueError, "FENCED_SESSION_HOLD"):
            room.heartbeat(agent_id="a", session_id=old["session_id"], fence=old["fence"], session_token=first["session_token"], idempotency_key="late-heartbeat-0123")

    def test_prompt_change_stales_session(self):
        rooms, roots = self._rooms()
        room, root = rooms[0], roots[0]
        entered = self._enter(room, root, "a", "x")
        _write(root, "prompts/ORCHESTRATION_CORE.md", "changed prompt\n")
        _run(root, "add", "prompts/ORCHESTRATION_CORE.md")
        _run(root, "commit", "-m", "change prompt")
        _run(root, "push", "origin", "master")
        session = entered["session"]
        result = room.heartbeat(agent_id="a", session_id=session["session_id"], fence=session["fence"], session_token=entered["session_token"], idempotency_key="heartbeat-a-012345")
        self.assertEqual(result["status"], "REHYDRATE_HOLD")

    def test_two_concurrent_enters_same_identity_only_one_session_wins(self):
        rooms, roots = self._rooms()
        loser, winner = rooms[0], rooms[1]
        loser_root, winner_root = roots
        original_publish = loser.board.remote_sync.publish
        injected = {"done": False}

        def racing_publish(expected_git_head, remote="origin"):
            if not injected["done"]:
                injected["done"] = True
                won = self._enter(winner, winner_root, "same", "winner-work", key="enter-same-winner-01")
                self.assertEqual(won["status"], "ENTERED")
            return original_publish(expected_git_head, remote)

        loser.board.remote_sync.publish = racing_publish
        result = self._enter(loser, loser_root, "same", "loser-work", key="enter-same-loser-012")
        self.assertIn(result["status"], {"AGENT_ALREADY_PRESENT_HOLD", "REHYDRATE_HOLD"})
        self.assertEqual(loser.read()["room"]["sessions"]["same"]["quest_id"], "winner-work")


if __name__ == "__main__":
    unittest.main()
