from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import textwrap
import time
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_REF = "athena-runtime-v3-candidate"
CLAIM_PATH = "runtime/runs/run.alpha/claims/build.json"


def _run(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    p = subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        capture_output=True,
    )
    if check and p.returncode:
        raise AssertionError(p.stderr or p.stdout)
    return p


def _write(root: Path, rel: str, value) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(value, str):
        path.write_text(value, encoding="utf-8")
    else:
        path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")


def _seed_shared_brain(base: Path) -> tuple[Path, dict[str, str], str]:
    seed = base / "seed"
    seed.mkdir()
    _run(seed, "init")
    _run(seed, "config", "user.name", "seed")
    _run(seed, "config", "user.email", "seed@example.invalid")

    _write(seed, "prompts/PROMPT.manifest.json", {
        "artifact": "ATHENA.PROMPT.RUNTIME.V1",
        "authority_ceiling": "below external authority",
        "active_state": "prompts/state/ACTIVE.json",
        "policy": "policies/PROMPT_RUNTIME.md",
        "default_profile": "MAXDEV",
        "profiles": {"MAXDEV": ["core"]},
        "modules": {
            "core": {
                "path": "prompts/ORCHESTRATION_CORE.md",
                "order": 0,
                "mandatory": True,
            }
        },
    })
    _write(seed, "prompts/state/ACTIVE.json", {
        "artifact": "ATHENA.PROMPT.STATE.ACTIVE.V1",
        "status": "ACTIVE",
        "profile": "MAXDEV",
        "enabled_modules": ["core"],
        "active_scoped_overlays": [],
        "revision": 1,
    })
    _write(seed, "policies/PROMPT_RUNTIME.md", "POLICY\n")
    _write(seed, "prompts/ORCHESTRATION_CORE.md", "CORE\n")

    # Immutable test interpretation contracts. Each cold process receives the
    # exact blob identities rather than executing these repository files.
    _write(seed, "orchestration/v3/reducer.py", "REDUCER CONTRACT\n")
    _write(seed, "orchestration/v3/ready.py", "READY CONTRACT\n")
    _write(seed, "orchestration/v3/claim.py", "CLAIM CONTRACT\n")

    _write(seed, "runtime/queue/objective.alpha.json", {
        "objective_id": "objective.alpha",
        "artifact_target": "artifact.md",
        "priority": 100,
        "risk_class": "LOW",
        "work_class": "PROJECT",
        "production_authority": "HOLD",
    })
    _write(seed, "runtime/runs/run.alpha/manifest.json", {
        "run_id": "run.alpha",
        "objective_ref": "objective.alpha",
        "artifact_target": "artifact.md",
        "work_class": "PROJECT",
        "nodes": [{
            "node_id": "build",
            "role_capability": "builder",
            "depends_on": [],
            "max_attempts": 1,
            "not_before_pulse": 0,
            "claim_path": CLAIM_PATH,
        }],
    })
    _write(seed, "runtime/runs/run.alpha/events/001.json", {
        "schema_version": "EVENT_V1",
        "event_id": "e1",
        "sequence": 1,
        "run_id": "run.alpha",
        "event_type": "RUN_CREATED",
        "at": "2026-08-08T00:00:00Z",
        "node_id": None,
        "data": {},
    })
    _write(seed, "runtime/runs/run.alpha/events/002.json", {
        "schema_version": "EVENT_V1",
        "event_id": "e2",
        "sequence": 2,
        "run_id": "run.alpha",
        "event_type": "RUN_ADMITTED",
        "at": "2026-08-08T00:00:01Z",
        "node_id": None,
        "data": {"verdict": "PASS"},
    })

    _run(seed, "add", ".")
    _run(seed, "commit", "-m", "seed replayable contention frontier")
    seed_head = _run(seed, "rev-parse", "HEAD").stdout.strip()
    _run(seed, "branch", SOURCE_REF)
    contracts = {
        path: _run(seed, "rev-parse", f"HEAD:{path}").stdout.strip()
        for path in (
            "orchestration/v3/reducer.py",
            "orchestration/v3/ready.py",
            "orchestration/v3/claim.py",
        )
    }

    origin = base / "brain.git"
    p = subprocess.run(["git", "init", "--bare", str(origin)], text=True, capture_output=True)
    if p.returncode:
        raise AssertionError(p.stderr or p.stdout)
    _run(seed, "remote", "add", "origin", str(origin))
    _run(seed, "push", "origin", "master")
    _run(seed, "push", "origin", SOURCE_REF)
    return origin, contracts, seed_head


def _clone(origin: Path, target: Path, actor: str) -> None:
    p = subprocess.run(["git", "clone", str(origin), str(target)], text=True, capture_output=True)
    if p.returncode:
        raise AssertionError(p.stderr or p.stdout)
    _run(target, "config", "user.name", actor)
    _run(target, "config", "user.email", f"{actor}@example.invalid")


def _python_env(brain: Path, contracts: dict[str, str], **extra: str) -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(PROJECT_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    env["ATHENA_TEST_BRAIN"] = str(brain)
    env["ATHENA_TEST_CONTRACTS"] = json.dumps(contracts, sort_keys=True)
    env.update(extra)
    return env


HYDRATE_SCRIPT = textwrap.dedent(
    r"""
    import json
    import os
    from pathlib import Path

    from athena_mcp.frontier_runtime import FrontierRuntime
    from athena_mcp.git_backend import GitBackend
    from athena_mcp.prompt_runtime import PromptRuntime

    root = Path(os.environ["ATHENA_TEST_BRAIN"])
    contracts = json.loads(os.environ["ATHENA_TEST_CONTRACTS"])
    git = GitBackend(root)
    runtime = FrontierRuntime(git, PromptRuntime(git), contract_blobs=contracts)
    packet = runtime.hydrate(source_ref="athena-runtime-v3-candidate", remote="origin", fetch=True)
    selection = runtime.select(source_ref="athena-runtime-v3-candidate", remote="origin", fetch=True)
    run = next(row for row in packet["runs"] if row["run_id"] == "run.alpha")
    out = {
        "source_head": packet["source_head"],
        "frontier_digest": packet["frontier_digest"],
        "prompt_stack_digest": packet["prompt_stack_digest"],
        "status": packet["status"],
        "selection_status": selection["status"],
        "selected": selection.get("selected"),
        "ready_work": packet.get("ready_work") or [],
        "claim_readiness_suppressed": packet.get("claim_readiness_suppressed") or [],
        "residuals": packet.get("residuals") or [],
        "node_states": (run.get("projection") or {}).get("node_states") or {},
        "event_ready_nodes": (run.get("projection") or {}).get("ready_nodes") or [],
    }
    expected_head = os.environ.get("ATHENA_EXPECTED_SOURCE_HEAD")
    expected_frontier = os.environ.get("ATHENA_EXPECTED_FRONTIER_DIGEST")
    expected_prompt = os.environ.get("ATHENA_EXPECTED_PROMPT_DIGEST")
    if expected_head and expected_frontier:
        fresh = runtime.freshness(
            expected_head,
            expected_frontier,
            expected_prompt,
            source_ref="athena-runtime-v3-candidate",
            remote="origin",
            fetch=True,
        )
        out["freshness_status"] = fresh["status"]
        out["freshness_changed"] = fresh["changed"]
    print(json.dumps(out, sort_keys=True))
    """
)


CLAIM_SCRIPT = textwrap.dedent(
    r"""
    import json
    import os
    import subprocess
    import time
    from pathlib import Path

    root = Path(os.environ["ATHENA_TEST_BRAIN"])
    actor = os.environ["ATHENA_TEST_ACTOR"]
    barrier = Path(os.environ["ATHENA_TEST_BARRIER"])
    frontier_digest = os.environ["ATHENA_TEST_FRONTIER_DIGEST"]
    claim_path = "runtime/runs/run.alpha/claims/build.json"

    def git(*args):
        return subprocess.run(
            ["git", "-C", str(root), *args],
            text=True,
            capture_output=True,
        )

    switched = git("switch", "-c", "runtime-work", "origin/athena-runtime-v3-candidate")
    if switched.returncode:
        raise SystemExit(switched.stderr or switched.stdout)
    path = root / claim_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "schema_version": "CLAIM_V1",
        "run_id": "run.alpha",
        "node_id": "build",
        "worker_role": actor,
        "attempt": 1,
        "policy_commit": "a" * 40,
        "claimed_at": "2026-08-08T00:00:02Z",
        "lease_expires_at": "2026-08-08T00:10:02Z",
        "input_snapshot_digest": frontier_digest,
        "production_authority": "HOLD",
    }, sort_keys=True) + "\n", encoding="utf-8")
    if git("add", claim_path).returncode:
        raise SystemExit("git add failed")
    committed = git("commit", "-m", f"{actor} claims build")
    if committed.returncode:
        raise SystemExit(committed.stderr or committed.stdout)
    local_head = git("rev-parse", "HEAD").stdout.strip()

    deadline = time.time() + 10
    while not barrier.exists() and time.time() < deadline:
        time.sleep(0.01)
    if not barrier.exists():
        raise SystemExit("barrier timeout")

    pushed = git("push", "origin", "HEAD:refs/heads/athena-runtime-v3-candidate")
    print(json.dumps({
        "actor": actor,
        "local_head": local_head,
        "push_returncode": pushed.returncode,
        "push_stdout": pushed.stdout,
        "push_stderr": pushed.stderr,
    }, sort_keys=True))
    """
)


RECONCILE_SCRIPT = textwrap.dedent(
    r"""
    import json
    import os
    import subprocess
    from pathlib import Path

    root = Path(os.environ["ATHENA_TEST_BRAIN"])

    def git(*args):
        p = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True)
        if p.returncode:
            raise SystemExit(p.stderr or p.stdout)
        return p.stdout.strip()

    events = root / "runtime/runs/run.alpha/events"
    (events / "003.json").write_text(json.dumps({
        "schema_version": "EVENT_V1",
        "event_id": "e3",
        "sequence": 3,
        "run_id": "run.alpha",
        "event_type": "NODE_READY",
        "at": "2026-08-08T00:00:03Z",
        "node_id": "build",
        "data": {},
    }, sort_keys=True) + "\n", encoding="utf-8")
    (events / "004.json").write_text(json.dumps({
        "schema_version": "EVENT_V1",
        "event_id": "e4",
        "sequence": 4,
        "run_id": "run.alpha",
        "event_type": "CLAIM_ACQUIRED",
        "at": "2026-08-08T00:00:04Z",
        "node_id": "build",
        "data": {"claim_path": "runtime/runs/run.alpha/claims/build.json"},
    }, sort_keys=True) + "\n", encoding="utf-8")
    git("add", "runtime/runs/run.alpha/events/003.json", "runtime/runs/run.alpha/events/004.json")
    git("commit", "-m", "reconcile provider claim into event stream")
    head = git("rev-parse", "HEAD")
    git("push", "origin", "HEAD:refs/heads/athena-runtime-v3-candidate")
    print(json.dumps({"reconciled_head": head}, sort_keys=True))
    """
)


class FrontierColdProcessContentionTests(unittest.TestCase):
    def test_two_cold_processes_race_then_loser_rehydrates_before_action(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        base = Path(td.name)
        origin, contracts, seed_head = _seed_shared_brain(base)

        agent_a = base / "agent-a"
        agent_b = base / "agent-b"
        _clone(origin, agent_a, "agent-a")
        _clone(origin, agent_b, "agent-b")

        cold_a = subprocess.run(
            [sys.executable, "-c", HYDRATE_SCRIPT],
            env=_python_env(agent_a, contracts),
            text=True,
            capture_output=True,
            check=True,
        )
        cold_b = subprocess.run(
            [sys.executable, "-c", HYDRATE_SCRIPT],
            env=_python_env(agent_b, contracts),
            text=True,
            capture_output=True,
            check=True,
        )
        first_a = json.loads(cold_a.stdout.strip())
        first_b = json.loads(cold_b.stdout.strip())

        self.assertEqual(first_a["status"], "HYDRATED")
        self.assertEqual(first_b["status"], "HYDRATED")
        self.assertEqual(first_a["selection_status"], "SELECTED")
        self.assertEqual(first_b["selection_status"], "SELECTED")
        self.assertEqual(first_a["source_head"], seed_head)
        self.assertEqual(first_b["source_head"], seed_head)
        self.assertEqual(first_a["frontier_digest"], first_b["frontier_digest"])
        self.assertEqual(first_a["prompt_stack_digest"], first_b["prompt_stack_digest"])
        self.assertEqual(first_a["selected"]["node_id"], "build")
        self.assertEqual(first_b["selected"]["node_id"], "build")

        barrier = base / "start-race"
        procs = []
        for actor, brain in (("agent-a", agent_a), ("agent-b", agent_b)):
            procs.append((actor, brain, subprocess.Popen(
                [sys.executable, "-c", CLAIM_SCRIPT],
                env=_python_env(
                    brain,
                    contracts,
                    ATHENA_TEST_ACTOR=actor,
                    ATHENA_TEST_BARRIER=str(barrier),
                    ATHENA_TEST_FRONTIER_DIGEST=first_a["frontier_digest"],
                ),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )))
        time.sleep(0.1)
        barrier.write_text("go\n", encoding="utf-8")

        results = []
        for actor, brain, proc in procs:
            stdout, stderr = proc.communicate(timeout=15)
            self.assertEqual(proc.returncode, 0, f"{actor}: {stderr or stdout}")
            results.append((actor, brain, json.loads(stdout.strip())))

        winners = [row for row in results if row[2]["push_returncode"] == 0]
        losers = [row for row in results if row[2]["push_returncode"] != 0]
        self.assertEqual(len(winners), 1, results)
        self.assertEqual(len(losers), 1, results)
        winner_actor, winner_brain, winner = winners[0]
        loser_actor, loser_brain, loser = losers[0]
        self.assertNotEqual(winner_actor, loser_actor)

        shared_after_claim = _run(base, f"--git-dir={origin}", "rev-parse", SOURCE_REF).stdout.strip()
        self.assertEqual(shared_after_claim, winner["local_head"])
        self.assertNotEqual(shared_after_claim, loser["local_head"])

        # The loser does not act from its rejected local commit. It cold-hydrates
        # the shared source and must see the provider claim as an exclusion fact
        # even though the event stream still ends at RUN_ADMITTED.
        loser_after_proc = subprocess.run(
            [sys.executable, "-c", HYDRATE_SCRIPT],
            env=_python_env(
                loser_brain,
                contracts,
                ATHENA_EXPECTED_SOURCE_HEAD=first_a["source_head"],
                ATHENA_EXPECTED_FRONTIER_DIGEST=first_a["frontier_digest"],
                ATHENA_EXPECTED_PROMPT_DIGEST=first_a["prompt_stack_digest"],
            ),
            text=True,
            capture_output=True,
            check=True,
        )
        loser_after = json.loads(loser_after_proc.stdout.strip())
        self.assertEqual(loser_after["source_head"], shared_after_claim)
        self.assertEqual(loser_after["freshness_status"], "STALE")
        self.assertTrue(loser_after["freshness_changed"]["shared_source_head"])
        self.assertTrue(loser_after["freshness_changed"]["frontier_digest"])
        self.assertFalse(loser_after["freshness_changed"]["prompt_stack_digest"])
        self.assertEqual(loser_after["ready_work"], [])
        self.assertEqual(loser_after["selection_status"], "NO_REPLAYABLE_READY_WORK")
        self.assertEqual(loser_after["event_ready_nodes"], ["build"])
        self.assertEqual(loser_after["node_states"]["build"], "PENDING")
        self.assertEqual(loser_after["claim_readiness_suppressed"][0]["node_id"], "build")
        self.assertTrue(any(
            row.get("kind") == "CLAIM_EVENT_LAG"
            and row.get("code") == "FIXED_CLAIM_PATH_PRESENT_BEFORE_CLAIM_EVENT"
            for row in loser_after["residuals"]
        ))

        # A third process has no loser-local history at all and independently
        # reconstructs the same shared lag state from a fresh clone.
        observer = base / "observer"
        _clone(origin, observer, "observer")
        observer_lag_proc = subprocess.run(
            [sys.executable, "-c", HYDRATE_SCRIPT],
            env=_python_env(observer, contracts),
            text=True,
            capture_output=True,
            check=True,
        )
        observer_lag = json.loads(observer_lag_proc.stdout.strip())
        self.assertEqual(observer_lag["source_head"], loser_after["source_head"])
        self.assertEqual(observer_lag["frontier_digest"], loser_after["frontier_digest"])
        self.assertEqual(observer_lag["ready_work"], [])
        self.assertEqual(observer_lag["claim_readiness_suppressed"], loser_after["claim_readiness_suppressed"])

        # The winner now appends the replay event. This is deliberately later
        # than provider exclusion, proving that the intermediate lag was real.
        reconciled = subprocess.run(
            [sys.executable, "-c", RECONCILE_SCRIPT],
            env=_python_env(winner_brain, contracts),
            text=True,
            capture_output=True,
            check=True,
        )
        reconciled_head = json.loads(reconciled.stdout.strip())["reconciled_head"]
        self.assertNotEqual(reconciled_head, shared_after_claim)

        observer_after_proc = subprocess.run(
            [sys.executable, "-c", HYDRATE_SCRIPT],
            env=_python_env(observer, contracts),
            text=True,
            capture_output=True,
            check=True,
        )
        observer_after = json.loads(observer_after_proc.stdout.strip())
        self.assertEqual(observer_after["source_head"], reconciled_head)
        self.assertEqual(observer_after["node_states"]["build"], "CLAIMED")
        self.assertEqual(observer_after["ready_work"], [])
        self.assertEqual(observer_after["claim_readiness_suppressed"], [])
        self.assertFalse(any(row.get("kind") == "CLAIM_EVENT_LAG" for row in observer_after["residuals"]))
        self.assertNotEqual(observer_after["frontier_digest"], observer_lag["frontier_digest"])


if __name__ == "__main__":
    unittest.main()
