from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from athena_mcp.git_backend import GitBackend
from athena_mcp.message_board import MessageBoardRuntime
from athena_mcp.organism_room import (
    OrganismRoomRuntime,
    FAMILIES,
    _prompt_digest,
    allocate_population,
    make_authority_receipt,
    validate_resource_admission,
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


def _resources(**overrides):
    value = {"tool_calls": 100, "api_calls": 100, "tokens": 100000, "wall_seconds": 3600, "storage_writes": 20, "external_mutations": 2, "shared_sinks": []}
    value.update(overrides)
    return value


def _reserve(**overrides):
    value = {"tool_calls": 10, "api_calls": 10, "tokens": 10000, "wall_seconds": 300, "storage_writes": 2, "external_mutations": 0, "shared_sinks": []}
    value.update(overrides)
    return value


def _request(**overrides):
    value = {"tool_calls": 5, "api_calls": 5, "tokens": 5000, "wall_seconds": 300, "storage_writes": 1, "external_mutations": 0, "shared_sinks": []}
    value.update(overrides)
    return value


def _fixture(base: Path, clone_names=("b",)):
    local = base / "local"
    local.mkdir()
    _run(local, "init", "-b", "master")
    _run(local, "config", "user.name", "local")
    _run(local, "config", "user.email", "local@example.invalid")
    _write(local, "prompts/PROMPT.manifest.json", '{"artifact":"ATHENA.PROMPT.RUNTIME.V2","active_state":"prompts/state/ACTIVE.json","bootstrap":"prompts/BOOTSTRAP.md","core":"prompts/ORCHESTRATION_CORE.md","policy":"policies/PROMPT_RUNTIME.md","default_profile":"MAXDEV","profiles":{"MAXDEV":["core","git"]},"modules":{"core":{"path":"prompts/ORCHESTRATION_CORE.md","mandatory":true},"git":{"path":"prompts/modules/GIT_ORGANISM.md","mandatory":true}},"room":{"repo":"demeet2k/Athena","issue":555,"registry":"registry/organism_room_v1.json","harness_genotype":"registry/harness_genotype_v1.json","allocator":"scripts/organism_homeostasis_v1.py"}}\n')
    _write(local, "prompts/state/ACTIVE.json", '{"artifact":"ATHENA.PROMPT.STATE.ACTIVE.V2","prompt_runtime":"ATHENA.PROMPT.RUNTIME.V2","status":"ACTIVE","profile":"MAXDEV","enabled_modules":["core","git"],"active_scoped_overlays":["prompts/overlays/ACTIVE.md"],"active_scoped_state":["prompts/state/ACTIVE_OVERLAY.json"],"harness_genotype":"registry/harness_genotype_v1.json"}\n')
    _write(local, "prompts/state/ACTIVE_OVERLAY.json", '{"artifact":"ATHENA.PROMPT.OVERLAY.STATE.TEST.V1","status":"ACTIVE_SCOPED","overlay":"prompts/overlays/ACTIVE.md"}\n')
    _write(local, "registry/organism_room_v1.json", '{"artifact":"ATHENA.ORGANISM.ROOM.V1","status":"ACTIVE","waves":{"W0":0.5,"W1":0.3,"W2":0.2},"job_families":["GIT","MATH","MYTH","NAV","TOOLS","CORPUS","ALCHEMY","META","INTEGRATION"]}\n')
    for rel in ("prompts/BOOTSTRAP.md", "prompts/ORCHESTRATION_CORE.md", "prompts/modules/GIT_ORGANISM.md", "prompts/overlays/ACTIVE.md", "policies/PROMPT_RUNTIME.md", "registry/harness_genotype_v1.json", "scripts/organism_homeostasis_v1.py"):
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
        self.assertEqual(allocation["counts"]["GIT"], 4)
        self.assertEqual(allocation["counts"]["MATH"], 3)
        self.assertEqual(allocation["counts"]["NAV"], 3)
        self.assertEqual(allocation["counts"]["CORPUS"], 3)
        self.assertEqual(allocation["counts"]["META"], 2)
        self.assertEqual(allocation["wave_counts"], {"IMMEDIATE": 10, "MIDDLE": 6, "RECURSIVE_META": 4})

    def test_small_population_is_builder_generalist_with_all_three_waves(self):
        for count in (1, 2, 3):
            allocation = allocate_population([f"a{i}" for i in range(count)])
            self.assertEqual(allocation["counts"]["GIT"], count)
            self.assertEqual([row["wave"] for row in allocation["waves"]], ["IMMEDIATE", "MIDDLE", "RECURSIVE_META"])

    def test_empty_lane_lends_capacity(self):
        allocation = allocate_population([f"a{i}" for i in range(8)], {name: (1 if name == "MATH" else 0) for name in (
            "GIT", "MATH", "MYTH", "NAV", "TOOLS", "CORPUS", "ALCHEMY", "META", "INTEGRATION"
        )})
        self.assertEqual(allocation["counts"]["MATH"], 8)

    def test_git_state_never_persists_bearer_token(self):
        # Checked end-to-end below; this protects the structural invariant at
        # the allocator/unit layer too by keeping the public shape token-free.
        self.assertNotIn("session_token", allocate_population(["a"]))

    def test_exact_canonical_vocabulary_and_six_worker_wave_minimums(self):
        self.assertEqual(FAMILIES, ("GIT", "MATH", "MYTH", "NAV", "TOOLS", "CORPUS", "ALCHEMY", "META", "INTEGRATION"))
        self.assertEqual(allocate_population([f"a{i}" for i in range(6)])["wave_counts"], {"IMMEDIATE": 2, "MIDDLE": 2, "RECURSIVE_META": 2})


class ResourceAdmissionTests(unittest.TestCase):
    def test_unknown_dimension_and_reserve_overrun_hold(self):
        unknown = _request()
        del unknown["api_calls"]
        with self.assertRaisesRegex(ValueError, "RESOURCE_api_calls_UNKNOWN_HOLD"):
            validate_resource_admission(unknown, _resources(), _reserve(), [])
        with self.assertRaisesRegex(ValueError, "RESOURCE_CAPACITY_HOLD:tokens"):
            validate_resource_admission(_request(tokens=1), _resources(tokens=100), _reserve(tokens=100), [])

    def test_aggregate_and_shared_sink_collisions_hold_then_release(self):
        active = {
            "status": "ACTIVE",
            **validate_resource_admission(_request(tokens=90000, shared_sinks=["github:branch"]), _resources(), _reserve(), []),
        }
        with self.assertRaisesRegex(ValueError, "RESOURCE_CAPACITY_HOLD:tokens"):
            validate_resource_admission(_request(tokens=1), _resources(), _reserve(), [active])
        sink_active = {
            "status": "ACTIVE",
            **validate_resource_admission(_request(tokens=1000, shared_sinks=["github:branch"]), _resources(), _reserve(), []),
        }
        with self.assertRaisesRegex(ValueError, "SHARED_SINK_HOLD:github:branch"):
            validate_resource_admission(_request(shared_sinks=["github:branch"]), _resources(), _reserve(), [sink_active])
        active["status"] = "VERIFIED"
        admitted = validate_resource_admission(_request(shared_sinks=["github:branch"]), _resources(), _reserve(), [active])
        self.assertEqual(admitted["resource_standing"], "HOST_BOUND_UPPER_BOUND_RESERVED")


class PromptBindingTests(unittest.TestCase):
    def _root(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root, _ = _fixture(Path(td.name), clone_names=())
        return root

    def test_v2_overlay_state_is_exactly_bound_and_digest_sensitive(self):
        root = self._root()
        before = _prompt_digest(root)
        state_path = root / "prompts/state/ACTIVE_OVERLAY.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["mutation"] = "changes ancestry"
        _write(root, "prompts/state/ACTIVE_OVERLAY.json", json.dumps(state))
        self.assertNotEqual(_prompt_digest(root), before)
        state["status"] = "CANDIDATE"
        _write(root, "prompts/state/ACTIVE_OVERLAY.json", json.dumps(state))
        with self.assertRaisesRegex(RuntimeError, "overlay_state_status"):
            _prompt_digest(root)

    def test_wrong_room_coordinate_and_ambiguous_state_fail_closed(self):
        root = self._root()
        manifest_path = root / "prompts/PROMPT.manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["room"]["issue"] = 999
        _write(root, "prompts/PROMPT.manifest.json", json.dumps(manifest))
        with self.assertRaisesRegex(RuntimeError, "canonical_room_coordinate"):
            _prompt_digest(root)
        manifest["room"]["issue"] = 555
        _write(root, "prompts/PROMPT.manifest.json", json.dumps(manifest))
        active_path = root / "prompts/state/ACTIVE.json"
        active = json.loads(active_path.read_text(encoding="utf-8"))
        active["active_scoped_state"].append("prompts/state/DUPLICATE.json")
        _write(root, "prompts/state/ACTIVE.json", json.dumps(active))
        _write(root, "prompts/state/DUPLICATE.json", '{"status":"ACTIVE_SCOPED","overlay":"prompts/overlays/ACTIVE.md"}')
        with self.assertRaisesRegex(RuntimeError, "overlay_state_cardinality"):
            _prompt_digest(root)


class ReceiptTests(unittest.TestCase):
    def test_external_mac_binds_every_authority_claim(self):
        claims = {"quest_id": "q", "attempt": 1, "session_id": "s", "fence": 1, "input_head": "h", "prompt_digest": "p", "acceptance_digest": "accept", "artifact_digests": ["a"], "result": "PASS", "evaluator_version": "host-eval-v1", "observed_at": "2026-08-09T22:00:00+00:00"}
        receipt = make_authority_receipt(claims, "host", b"k" * 32)
        verify_authority_receipt(receipt, claims, {"host": b"k" * 32})
        with self.assertRaisesRegex(ValueError, "BINDING_HOLD:quest_id"):
            verify_authority_receipt(receipt, {**claims, "quest_id": "other"}, {"host": b"k" * 32})
        with self.assertRaisesRegex(ValueError, "MAC_HOLD"):
            verify_authority_receipt(receipt, claims, {"host": b"x" * 32})
        incomplete = {key: value for key, value in claims.items() if key != "evaluator_version"}
        with self.assertRaisesRegex(ValueError, "EVALUATOR_VERSION_HOLD"):
            verify_authority_receipt(make_authority_receipt(incomplete, "host", b"k" * 32), incomplete, {"host": b"k" * 32})


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
        return room.enter(agent_id=agent, task=f"Build {work}", work_key=work, targets=[f"{work}.py"], ack_head=_run(root, "rev-parse", "HEAD"), ack_prompt_digest=_prompt_digest(root), idempotency_key=key or f"enter-{agent}-0123456789", resource_upper_bound=_request(), room_budget=_resources(), protected_reserve=_reserve(), lease_seconds=600)

    def test_enter_requires_exact_head_and_prompt_ack(self):
        rooms, roots = self._rooms()
        hold = rooms[0].enter(agent_id="a", task="Build x", work_key="x", targets=["x.py"], ack_head="stale", ack_prompt_digest="wrong", idempotency_key="enter-a-0123456789", resource_upper_bound=_request(), room_budget=_resources(), protected_reserve=_reserve())
        self.assertEqual(hold["status"], "REHYDRATE_HOLD")
        entered = self._enter(rooms[0], roots[0], "a", "x")
        self.assertEqual(entered["status"], "ENTERED")
        self.assertEqual(rooms[1].read()["board"]["active"][0]["agent_id"], "a")

    def test_signin_precedes_work_and_idle_signout_is_legal(self):
        rooms, roots = self._rooms()
        room, root = rooms[0], roots[0]
        signed = room.sign_in(agent_id="idle", ack_head=_run(root, "rev-parse", "HEAD"), ack_prompt_digest=_prompt_digest(root), idempotency_key="signin-idle-000001", capabilities=["code"])
        self.assertEqual(signed["status"], "SIGNED_IN")
        self.assertIsNone(signed["session"]["quest_id"])
        self.assertEqual(room.read()["room"]["quests"], {})
        claimed = room.enter(
            agent_id="idle", task="Build claimed", work_key="claimed", targets=["claimed.py"],
            ack_head=_run(root, "rev-parse", "HEAD"), ack_prompt_digest=_prompt_digest(root),
            idempotency_key="claim-idle-000001", resource_upper_bound=_request(), room_budget=_resources(),
            protected_reserve=_reserve(), session_id=signed["session"]["session_id"], fence=signed["session"]["fence"],
            session_token=signed["session_token"],
        )
        self.assertEqual(claimed["status"], "WORK_CLAIMED", claimed)
        kinds = [event["kind"] for event in room.read()["board"]["recent_events"]]
        self.assertIn("SIGNIN", kinds)
        self.assertIn("WORK", kinds)

        other = room.sign_in(agent_id="observer", ack_head=_run(root, "rev-parse", "HEAD"), ack_prompt_digest=_prompt_digest(root), idempotency_key="signin-observer-001")
        out = room.sign_out(agent_id="observer", session_id=other["session"]["session_id"], fence=other["session"]["fence"], session_token=other["session_token"], idempotency_key="signout-observer-01")
        self.assertEqual(out["status"], "SIGNED_OUT")

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
        claims = {"quest_id": "x", "attempt": 1, "session_id": session["session_id"], "fence": session["fence"], "input_head": session["head"], "prompt_digest": session["prompt_digest"], "acceptance_digest": room.read()["room"]["quests"]["x"]["acceptance_digest"], "artifact_digests": artifacts, "result": "PASS", "evaluator_version": "host-eval-v1", "observed_at": "2026-08-09T22:00:00+00:00"}
        receipt = make_authority_receipt(claims, "host", b"h" * 32)
        completed = room.complete(agent_id="a", session_id=session["session_id"], fence=session["fence"], session_token=entered["session_token"], artifact_digests=artifacts, result="PASS", receipt=receipt, residual="Integrate x into the caller", idempotency_key="complete-a-0123456")
        self.assertEqual(completed["status"], "VERIFIED_COMPLETION")
        self.assertFalse(completed["campaign_terminal"])
        self.assertEqual(completed["successor"]["status"], "READY")
        signed_out = room.sign_out(agent_id="a", session_id=session["session_id"], fence=session["fence"], session_token=entered["session_token"], idempotency_key="out-a-01234567890")
        self.assertEqual(signed_out["status"], "SIGNED_OUT")
        self.assertEqual(room.read()["board"]["active"], [])
        successor_id = completed["successor"]["quest_id"]
        consumed = self._enter(room, roots[0], "b", successor_id)
        self.assertEqual(consumed["status"], "ENTERED")
        observed = room.read()
        self.assertEqual(observed["metrics"]["successors_created"], 1)
        self.assertEqual(observed["metrics"]["successors_consumed"], 1)
        self.assertEqual(observed["metrics"]["successor_consumption_rate"], 1.0)
        self.assertEqual(observed["metrics"]["standing"], "OBSERVATIONAL_PROJECTION_NOT_CAUSAL_EFFECT")

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
            with rooms[0].epoch(agent_id="a", task="Build x", work_key="x", targets=["x.py"], ack_head=_run(roots[0], "rev-parse", "HEAD"), ack_prompt_digest=_prompt_digest(roots[0]), idempotency_key="enter-a-0123456789", resource_upper_bound=_request(), room_budget=_resources(), protected_reserve=_reserve(), lease_seconds=600):
                raise RuntimeError("boom")
        self.assertEqual(rooms[0].read()["board"]["active"], [])

    def test_idempotency_replay_and_conflict(self):
        rooms, roots = self._rooms()
        room = rooms[0]
        args = dict(agent_id="a", task="Build x", work_key="x", targets=["x.py"], ack_head=_run(roots[0], "rev-parse", "HEAD"), ack_prompt_digest=_prompt_digest(roots[0]), idempotency_key="enter-a-0123456789", resource_upper_bound=_request(), room_budget=_resources(), protected_reserve=_reserve(), lease_seconds=600)
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

    def test_stale_prompt_cannot_complete_with_old_signed_receipt(self):
        rooms, roots = self._rooms()
        room, root = rooms[0], roots[0]
        entered = self._enter(room, root, "stale", "stale-work")
        session = entered["session"]
        quest_row = room.read()["room"]["quests"]["stale-work"]
        _write(root, "prompts/ORCHESTRATION_CORE.md", "semantic drift\n")
        _run(root, "add", "prompts/ORCHESTRATION_CORE.md")
        _run(root, "commit", "-m", "semantic drift")
        _run(root, "push", "origin", "master")
        heartbeat = room.heartbeat(agent_id="stale", session_id=session["session_id"], fence=session["fence"], session_token=entered["session_token"], idempotency_key="heartbeat-stale-0001")
        self.assertEqual(heartbeat["status"], "REHYDRATE_HOLD")
        artifacts = ["sha256:old-context"]
        claims = {"quest_id": "stale-work", "attempt": 1, "session_id": session["session_id"], "fence": session["fence"], "input_head": quest_row["input_head"], "prompt_digest": quest_row["prompt_digest"], "acceptance_digest": quest_row["acceptance_digest"], "artifact_digests": artifacts, "result": "PASS", "evaluator_version": "host-eval-v1", "observed_at": "2026-08-09T22:00:00+00:00"}
        receipt = make_authority_receipt(claims, "host", b"h" * 32)
        with self.assertRaisesRegex(ValueError, "COMPLETION_STALE_PROMPT_HOLD"):
            room.complete(agent_id="stale", session_id=session["session_id"], fence=session["fence"], session_token=entered["session_token"], artifact_digests=artifacts, result="PASS", receipt=receipt, terminal_reason="NO_RESIDUAL", idempotency_key="complete-stale-00001")

    def test_expired_session_reclaims_same_quest_without_zombie(self):
        rooms, roots = self._rooms()
        room, root = rooms[0], roots[0]
        first = self._enter(room, root, "reclaim", "same-work")
        state_path = root / "runtime/message_board/v1/organism/state.json"
        presence_path = root / "runtime/message_board/v1/agents/reclaim.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        presence = json.loads(presence_path.read_text(encoding="utf-8"))
        expired = (datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat()
        state["sessions"]["reclaim"]["lease_until"] = expired
        presence["expires_at"] = expired
        _write(root, "runtime/message_board/v1/organism/state.json", json.dumps(state))
        _write(root, "runtime/message_board/v1/agents/reclaim.json", json.dumps(presence))
        _run(root, "add", "runtime/message_board/v1")
        _run(root, "commit", "-m", "expire reclaim session")
        _run(root, "push", "origin", "master")
        second = self._enter(room, root, "reclaim", "same-work", key="enter-reclaim-new-01")
        self.assertEqual(second["status"], "ENTERED", second)
        self.assertGreater(second["session"]["fence"], first["session"]["fence"])
        self.assertEqual(room.read()["room"]["quests"]["same-work"]["attempt"], 2)
        with self.assertRaisesRegex(ValueError, "FENCED_SESSION_HOLD"):
            room.heartbeat(agent_id="reclaim", session_id=first["session"]["session_id"], fence=first["session"]["fence"], session_token=first["session_token"], idempotency_key="old-reclaim-heart-01")

    def test_existing_corrupt_state_never_resets_fence(self):
        rooms, roots = self._rooms()
        room, root = rooms[0], roots[0]
        _write(root, "runtime/message_board/v1/organism/state.json", '{"artifact":"WRONG"}\n')
        _run(root, "add", "runtime/message_board/v1/organism/state.json")
        _run(root, "commit", "-m", "corrupt room state")
        _run(root, "push", "origin", "master")
        with self.assertRaisesRegex(RuntimeError, "ROOM_STATE_CORRUPTION_HOLD"):
            room.read()

    def test_legacy_release_breaks_presence_lineage_and_blocks_completion(self):
        rooms, roots = self._rooms()
        room = rooms[0]
        entered = self._enter(room, roots[0], "lineage", "lineage-work")
        released = room.board.release(agent_id="lineage", release_status="PAUSED", outcome="legacy bypass")
        self.assertEqual(released["status"], "RELEASED")
        session = entered["session"]
        with self.assertRaisesRegex(ValueError, "ROOM_PRESENCE_LINEAGE_HOLD"):
            room.heartbeat(agent_id="lineage", session_id=session["session_id"], fence=session["fence"], session_token=entered["session_token"], idempotency_key="lineage-heart-0001")


if __name__ == "__main__":
    unittest.main()
