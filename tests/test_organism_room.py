
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path

# The reconstruction intentionally contains only files touched by this repair.
# Load submodules without executing the repository's much larger package
# registration body; GitHub CI will execute the complete package.
ROOT = Path(__file__).resolve().parents[1]
if "athena_mcp" not in sys.modules:
    package = types.ModuleType("athena_mcp")
    package.__path__ = [str(ROOT / "athena_mcp")]
    sys.modules["athena_mcp"] = package

from athena_mcp.git_backend import GitBackend
from athena_mcp.message_board import MessageBoardRuntime
from athena_mcp.organism_room import (
    OrganismRoomRuntime,
    allocate_homeostasis,
    normalize_target,
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
    _write(local, "seed.txt", "seed\n")
    _run(local, "add", ".")
    _run(local, "commit", "-m", "seed")
    origin = base / "origin.git"
    subprocess.run(["git", "init", "--bare", str(origin)], check=True, text=True, capture_output=True)
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


HEAD = "a" * 40


def _workers(n: int) -> list[dict]:
    return [
        {
            "agent_id": f"a{i:02d}",
            "session_id": f"s{i:02d}",
            "capabilities": ["python", "git", "research"],
            "waves": ["W0", "W1", "W2"],
            "domains": ["GIT", "MATH", "NAV", "CORPUS", "TOOLS", "ALCHEMY", "MYTH", "META"],
        }
        for i in range(n)
    ]


def _quest(i: int, wave: str, domain: str, **overrides) -> dict:
    value = {
        "quest_id": f"q{i:03d}",
        "wave": wave,
        "domain": domain,
        "ownership_key": f"owner-{i}",
        "targets": [f"target/{i}"],
        "expected_head": HEAD,
        "authority": "USER_AUTHORIZED",
        "positive_value": True,
        "required_capabilities": ["python"],
        "priority": 1,
        "ready_seq": i,
        "verified_gain": 1.0,
        "information_gain": 0.5,
        "cost": 0.1,
        "risk": 0.1,
    }
    value.update(overrides)
    return value


class OrganismRoomLifecycleTests(unittest.TestCase):
    def _runtimes(self, count=2):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        local, clones = _fixture(Path(td.name), tuple(f"c{i}" for i in range(count - 1)))
        roots = [local, *clones]
        return [OrganismRoomRuntime(GitBackend(root)) for root in roots], roots

    def test_enter_is_occupancy_not_work_claim(self):
        rooms, _ = self._runtimes(count=2)
        head = rooms[0].git.head()
        entered = rooms[0].enter(agent_id="alpha", session_id="run-1", expected_head=head, prompt_stack_digest="p" * 64)
        self.assertEqual(entered["status"], "ENTERED")
        snapshot = rooms[1].read()
        self.assertEqual(snapshot["n_live"], 1)
        self.assertEqual(snapshot["n_working"], 0)
        self.assertEqual(MessageBoardRuntime(rooms[1].git).read()["active"], [])

    def test_enter_requires_exact_head_and_is_idempotent_per_session(self):
        rooms, _ = self._runtimes(count=1)
        bad = rooms[0].enter(agent_id="alpha", session_id="run-1", expected_head="b" * 40, prompt_stack_digest="p")
        self.assertEqual(bad["status"], "STALE_HEAD_HOLD")
        head = rooms[0].git.head()
        first = rooms[0].enter(agent_id="alpha", session_id="run-1", expected_head=head, prompt_stack_digest="p")
        again = rooms[0].enter(agent_id="alpha", session_id="run-1", expected_head=first["remote_publish"]["published_head"], prompt_stack_digest="p")
        self.assertEqual(again["status"], "ALREADY_ENTERED")

    def test_second_live_session_and_aba_heartbeat_hold(self):
        rooms, _ = self._runtimes(count=1)
        head = rooms[0].git.head()
        first = rooms[0].enter(agent_id="alpha", session_id="run-1", expected_head=head, prompt_stack_digest="p")
        current = first["remote_publish"]["published_head"]
        conflict = rooms[0].enter(agent_id="alpha", session_id="run-2", expected_head=current, prompt_stack_digest="p")
        self.assertEqual(conflict["status"], "AGENT_SESSION_ALREADY_ACTIVE_HOLD")
        stale = rooms[0].heartbeat(agent_id="alpha", expected_session_id="run-old")
        self.assertEqual(stale["status"], "STALE_SESSION_HOLD")

    def test_bind_requires_exact_current_claim(self):
        rooms, _ = self._runtimes(count=1)
        room, = rooms
        head = room.git.head()
        room.enter(agent_id="alpha", session_id="run-1", expected_head=head, prompt_stack_digest="p")
        claim = room.board.present(agent_id="alpha", task="Build runtime", work_key="runtime", targets=["x.py"])
        wrong = room.bind(agent_id="alpha", expected_session_id="run-1", expected_claim_id="MBC-wrong")
        self.assertEqual(wrong["status"], "CLAIM_BINDING_HOLD")
        bound = room.bind(agent_id="alpha", expected_session_id="run-1", expected_claim_id=claim["presence"]["claim_id"])
        self.assertEqual(bound["status"], "BOUND")

    def test_leave_holds_while_work_claim_is_active(self):
        rooms, _ = self._runtimes(count=1)
        room, = rooms
        head = room.git.head()
        room.enter(agent_id="alpha", session_id="run-1", expected_head=head, prompt_stack_digest="p")
        claim = room.board.present(agent_id="alpha", task="Build runtime", work_key="runtime")
        room.bind(agent_id="alpha", expected_session_id="run-1", expected_claim_id=claim["presence"]["claim_id"])
        held = room.leave(agent_id="alpha", expected_session_id="run-1", stop_class="BOUNDARY")
        self.assertEqual(held["status"], "ACTIVE_WORK_CLAIM_HOLD")
        room.board.release(agent_id="alpha", expected_claim_id=claim["presence"]["claim_id"], release_status="PAUSED", outcome="host boundary")
        left = room.leave(
            agent_id="alpha",
            expected_session_id="run-1",
            stop_class="BOUNDARY",
            residual_portfolio=[{"quest": "resume"}],
            successor_routes=[{"route": "next"}],
        )
        self.assertEqual(left["status"], "LEFT")
        self.assertEqual(room.snapshot()["n_live"], 0)

    def test_signout_refs_never_self_verify_completion(self):
        rooms, _ = self._runtimes(count=1)
        room, = rooms
        head = room.git.head()
        room.enter(agent_id="alpha", session_id="run-1", expected_head=head, prompt_stack_digest="p")
        left = room.leave(
            agent_id="alpha",
            expected_session_id="run-1",
            stop_class="NO_POSITIVE_FRONTIER",
            completed_delta_refs=["free-text-pass"],
        )
        self.assertEqual(left["completion_standing"], "REFERENCED_NOT_VERIFIED_BY_ROOM")

    def test_two_clones_see_one_shared_census(self):
        rooms, roots = self._runtimes(count=3)
        head = rooms[0].git.head()
        rooms[0].enter(agent_id="a", session_id="sa", expected_head=head, prompt_stack_digest="p")
        rooms[1].read()
        head2 = rooms[1].git.head()
        rooms[1].enter(agent_id="b", session_id="sb", expected_head=head2, prompt_stack_digest="p")
        snap = rooms[2].read()
        self.assertEqual([x["agent_id"] for x in snap["active"]], ["a", "b"])
        self.assertTrue(snap["remote_sync"]["shared_frontier_verified"])

    def test_room_lifecycle_does_not_wrap_low_level_bootstrap(self):
        init_text = (ROOT / "athena_mcp" / "__init__.py").read_text(encoding="utf-8")
        self.assertNotIn("install_agent_bootstrap_organism_room(AgentBootstrapRuntime)", init_text)


class HomeostasisAllocationTests(unittest.TestCase):
    def test_spec_is_parseable_and_preserves_authority_firewalls(self):
        spec = json.loads((ROOT / "spec" / "ORGANISM_ROOM_HOMEOSTASIS_V1.json").read_text(encoding="utf-8"))
        self.assertEqual(spec["waves"], {"W0": 0.5, "W1": 0.3, "W2": 0.2, "rounding": "cumulative deficit Hamilton", "small_population": "time-slice missing waves; never fabricate workers or makework"})
        self.assertEqual(spec["authority"]["message_board"], "sole work-claim authority")
        self.assertIn("RELEASE_DONE != TASK_VERIFIED", spec["invariants"])

    def test_allocation_is_input_permutation_stable(self):
        workers = _workers(8)
        quests = [_quest(i, ("W0", "W1", "W2")[i % 3], ("GIT", "MATH", "NAV", "CORPUS")[i % 4]) for i in range(20)]
        a = allocate_homeostasis(workers=workers, quests=quests, current_head=HEAD, current_frontier_digest="f", epoch=1)
        b = allocate_homeostasis(workers=list(reversed(workers)), quests=list(reversed(quests)), current_head=HEAD, current_frontier_digest="f", epoch=1)
        self.assertEqual(a["allocation_digest"], b["allocation_digest"])
        self.assertEqual(a["assignments"], b["assignments"])

    def test_n_1_to_20_never_allocates_more_than_live_workers(self):
        quests = [_quest(i, _W, _D) for i, (_W, _D) in enumerate(
            (("W0", "GIT"), ("W1", "MATH"), ("W2", "META")) * 20
        )]
        for n in range(1, 21):
            with self.subTest(n=n):
                result = allocate_homeostasis(workers=_workers(n), quests=quests, current_head=HEAD, current_frontier_digest="f")
                self.assertLessEqual(len(result["assignments"]), n)
                self.assertEqual(len({a["agent_id"] for a in result["assignments"]}), len(result["assignments"]))
                self.assertEqual(len({a["ownership_key"] for a in result["assignments"]}), len(result["assignments"]))

    def test_three_workers_cover_three_waves_when_useful(self):
        quests = [_quest(0, "W0", "GIT"), _quest(1, "W1", "MATH"), _quest(2, "W2", "META")]
        result = allocate_homeostasis(workers=_workers(3), quests=quests, current_head=HEAD, current_frontier_digest="f")
        self.assertEqual({a["wave"] for a in result["assignments"]}, {"W0", "W1", "W2"})

    def test_cumulative_single_worker_converges_to_5_3_2(self):
        history = {"waves": {"W0": 0, "W1": 0, "W2": 0}, "domains": {}}
        counts = {"W0": 0, "W1": 0, "W2": 0}
        for epoch in range(10):
            quests = [
                _quest(epoch * 3, "W0", "GIT"),
                _quest(epoch * 3 + 1, "W1", "MATH"),
                _quest(epoch * 3 + 2, "W2", "META"),
            ]
            result = allocate_homeostasis(workers=_workers(1), quests=quests, current_head=HEAD, current_frontier_digest="f", epoch=epoch, history=history)
            wave = result["assignments"][0]["wave"]
            counts[wave] += 1
            history["waves"] = dict(counts)
            domain = result["assignments"][0]["domain"]
            history.setdefault("domains", {})[domain] = history.setdefault("domains", {}).get(domain, 0) + 1
        self.assertEqual(counts, {"W0": 5, "W1": 3, "W2": 2})

    def test_unknown_authority_and_nonpositive_work_are_holds_not_makework(self):
        quests = [
            _quest(0, "W0", "GIT", authority="UNKNOWN"),
            _quest(1, "W1", "MATH", positive_value=False),
        ]
        result = allocate_homeostasis(workers=_workers(4), quests=quests, current_head=HEAD, current_frontier_digest="f")
        self.assertEqual(result["assignments"], [])
        self.assertEqual({h["reason"] for h in result["holds"]}, {"AUTHORITY_UNKNOWN_OR_HELD", "NO_POSITIVE_VALUE_WITNESS"})

    def test_same_target_aliases_cannot_receive_two_writers(self):
        quests = [
            _quest(0, "W0", "GIT", targets=["A/./B/../C.py"]),
            _quest(1, "W1", "MATH", targets=["a/c.py"]),
        ]
        result = allocate_homeostasis(workers=_workers(2), quests=quests, current_head=HEAD, current_frontier_digest="f")
        self.assertEqual(len(result["assignments"]), 1)
        self.assertEqual(normalize_target("Ａ/./B/../C.py"), normalize_target("a/c.py"))

    def test_same_ownership_key_allows_only_one_primary(self):
        quests = [
            _quest(0, "W0", "GIT", ownership_key="same"),
            _quest(1, "W1", "MATH", ownership_key="ＳＡＭＥ"),
        ]
        result = allocate_homeostasis(workers=_workers(2), quests=quests, current_head=HEAD, current_frontier_digest="f")
        self.assertEqual(len(result["assignments"]), 1)

    def test_capability_spoof_is_not_satisfied_by_absent_worker_capability(self):
        worker = _workers(1)[0]
        worker["capabilities"] = ["git"]
        quest = _quest(0, "W0", "GIT", required_capabilities=["python"])
        result = allocate_homeostasis(workers=[worker], quests=[quest], current_head=HEAD, current_frontier_digest="f")
        self.assertEqual(result["assignments"], [])

    def test_stale_head_quest_is_held(self):
        quest = _quest(0, "W0", "GIT", expected_head="b" * 40)
        result = allocate_homeostasis(workers=_workers(1), quests=[quest], current_head=HEAD, current_frontier_digest="f")
        self.assertEqual(result["holds"][0]["reason"], "STALE_HEAD")

    def test_100_identical_ownership_claims_compile_one_primary(self):
        quests = [
            _quest(i, ("W0", "W1", "W2")[i % 3], ("GIT", "MATH", "META")[i % 3], ownership_key="one-shared-object")
            for i in range(100)
        ]
        result = allocate_homeostasis(workers=_workers(100), quests=quests, current_head=HEAD, current_frontier_digest="f")
        self.assertEqual(len(result["assignments"]), 1)

    def test_100_disjoint_quests_use_100_available_seats(self):
        quests = [
            _quest(i, ("W0", "W1", "W2")[i % 3], ("GIT", "MATH", "NAV", "CORPUS", "TOOLS", "ALCHEMY", "MYTH", "META")[i % 8])
            for i in range(100)
        ]
        result = allocate_homeostasis(workers=_workers(100), quests=quests, current_head=HEAD, current_frontier_digest="f")
        self.assertEqual(len(result["assignments"]), 100)

    def test_wave_quota_converges_exactly_over_100_single_seat_epochs(self):
        counts = {"W0": 0, "W1": 0, "W2": 0}
        domains = {}
        for epoch in range(100):
            quests = [
                _quest(epoch * 3, "W0", "GIT"),
                _quest(epoch * 3 + 1, "W1", "MATH"),
                _quest(epoch * 3 + 2, "W2", "META"),
            ]
            result = allocate_homeostasis(
                workers=_workers(1),
                quests=quests,
                current_head=HEAD,
                current_frontier_digest="f",
                epoch=epoch,
                history={"waves": counts, "domains": domains},
            )
            picked = result["assignments"][0]
            counts[picked["wave"]] += 1
            domains[picked["domain"]] = domains.get(picked["domain"], 0) + 1
        self.assertEqual(counts, {"W0": 50, "W1": 30, "W2": 20})

    def test_domain_quota_matches_4_3_3_3_2_2_1_2_over_20_seats(self):
        quests = []
        i = 0
        for domain in ("GIT", "MATH", "NAV", "CORPUS", "TOOLS", "ALCHEMY", "MYTH", "META"):
            for _ in range(20):
                quests.append(_quest(i, ("W0", "W1", "W2")[i % 3], domain))
                i += 1
        result = allocate_homeostasis(workers=_workers(20), quests=quests, current_head=HEAD, current_frontier_digest="f")
        counts = {domain: 0 for domain in ("GIT", "MATH", "NAV", "CORPUS", "TOOLS", "ALCHEMY", "MYTH", "META")}
        for assignment in result["assignments"]:
            counts[assignment["domain"]] += 1
        self.assertEqual(counts, {"GIT": 4, "MATH": 3, "NAV": 3, "CORPUS": 3, "TOOLS": 2, "ALCHEMY": 2, "MYTH": 1, "META": 2})

    def test_2000_quest_permutation_replay_is_identical(self):
        quests = [
            _quest(i, ("W0", "W1", "W2")[i % 3], ("GIT", "MATH", "NAV", "CORPUS", "TOOLS", "ALCHEMY", "MYTH", "META")[i % 8])
            for i in range(2000)
        ]
        a = allocate_homeostasis(workers=_workers(64), quests=quests, current_head=HEAD, current_frontier_digest="f", epoch=7)
        b = allocate_homeostasis(workers=list(reversed(_workers(64))), quests=list(reversed(quests)), current_head=HEAD, current_frontier_digest="f", epoch=7)
        self.assertEqual(a["allocation_digest"], b["allocation_digest"])


if __name__ == "__main__":
    unittest.main()
