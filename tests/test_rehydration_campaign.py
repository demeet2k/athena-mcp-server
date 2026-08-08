import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.git_backend import GitBackend
from athena_mcp.prompt_runtime import PromptRuntime
from athena_mcp.rehydration_campaign import RehydrationCampaignRuntime
from athena_mcp.rehydration_loop import _sha


def _run(root: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True)
    if p.returncode:
        raise AssertionError(p.stderr or p.stdout)
    return p.stdout.strip()


def _write(root: Path, rel: str, value) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(value, str):
        p.write_text(value, encoding="utf-8")
    else:
        p.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


class _Remote:
    def sync(self, remote="origin"):
        return {"status": "UP_TO_DATE", "remote": remote, "shared_frontier_verified": True}

    def publish(self, expected_git_head, remote="origin"):
        return {"status": "PUBLISHED_SHARED", "remote": remote, "published_head": expected_git_head, "shared_frontier_verified": True}


class _FakeLoop:
    def __init__(self, git):
        self.git = git
        self.states = {}

    def add(self, loop_id, status="ACTIVE", state_digest="LOOP-STATE-1", summary=None, baton=None):
        self.states[loop_id] = {
            "artifact": "ATHENA.REHYDRATION.LOOP.V1",
            "loop_id": loop_id,
            "status": status,
            "state_digest": state_digest,
            "chain_digest": "CHAIN-" + state_digest,
            "step_index": 2,
            "last_completion": {
                "summary": summary,
                "evidence_refs": ["test://loop"],
                "successor_baton": baton,
            } if summary or baton else None,
        }
        return self.states[loop_id]

    def _read_state(self, loop_id):
        return dict(self.states[loop_id]), {"state": f"fake/{loop_id}/state.json"}

    def _path_last_commit(self, rel):
        return self.git.head()


def _brain(base: Path):
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
    active = {
        "artifact": "ATHENA.PROMPT.STATE.ACTIVE.V1",
        "status": "ACTIVE",
        "profile": "MAXDEV",
        "enabled_modules": ["core"],
        "active_scoped_overlays": [],
        "revision": 1,
    }
    _write(root, "prompts/PROMPT.manifest.json", manifest)
    _write(root, "prompts/state/ACTIVE.json", active)
    _write(root, "policies/PROMPT_RUNTIME.md", "POLICY\n")
    _write(root, "prompts/ORCHESTRATION_CORE.md", "CORE\n")
    _run(root, "add", ".")
    _run(root, "commit", "-m", "seed brain")
    git = GitBackend(root)
    prompt = PromptRuntime(git)
    loop = _FakeLoop(git)
    runtime = RehydrationCampaignRuntime(git, prompt, loop, _Remote())
    return runtime, loop, root


def _baton(tasks):
    rows = []
    for i, task in enumerate(tasks):
        rows.append({
            "candidate_id": f"SC-{i}",
            "task": task,
            "source": "EXPLICIT_CANDIDATE",
            "metrics": {
                "utility": 0.8,
                "dependency_unblocking": 0.8,
                "uncertainty_reduction": 0.5,
                "novelty": 0.5,
                "risk": 0.2,
                "cost": 0.4,
                "repetition": 0.1,
            },
            "routing_score": 1.0,
        })
    value = {
        "artifact": "ATHENA.REHYDRATION.SUCCESSOR.BATON.V1",
        "status": "AMBIGUOUS" if len(rows) > 1 else "SELECTED",
        "loop_id": "LOOP-X",
        "from_step": 1,
        "goal": "goal",
        "current_task": "task",
        "policy": {"authority": "ROUTING_ONLY"},
        "candidates": rows,
        "pareto_candidate_ids": [x["candidate_id"] for x in rows],
        "selected": rows[0] if len(rows) == 1 else None,
        "ties": rows if len(rows) > 1 else [rows[0]],
        "deferred_candidate_ids": [],
        "selection_reason": "test",
        "laws": ["ROUTING_SCORE != AUTHORITY"],
    }
    value["baton_digest"] = _sha(value)
    return value


class RehydrationCampaignTests(unittest.TestCase):
    def _runtime(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        return _brain(Path(td.name))

    def _start(self, runtime, **kwargs):
        return runtime.start(
            goal="Develop the full causal Git framework",
            expected_git_head=runtime.git.head(),
            initial_tasks=kwargs.pop("initial_tasks", ["Explore architecture A"]),
            max_width=kwargs.pop("max_width", 4),
            max_depth=kwargs.pop("max_depth", 4),
            max_branches=kwargs.pop("max_branches", 12),
            lease_steps=kwargs.pop("lease_steps", 3),
            shared_remote_mode="DISABLED",
            **kwargs,
        )

    def _claim_bind_sync_complete(self, runtime, loop, started, branch_id, loop_id="LOOP-1"):
        claimed = runtime.claim(
            campaign_id=started["campaign_id"], expected_state_digest=started["state_digest"],
            expected_checkpoint_head=started["checkpoint_head"], branch_id=branch_id,
            agent="agent-a", shared_remote_mode="DISABLED",
        )
        loop.add(loop_id, status="COMPLETE", state_digest="LOOP-STATE-1", summary="branch completed")
        bound = runtime.bind_loop(
            campaign_id=started["campaign_id"], expected_state_digest=claimed["state_digest"],
            expected_checkpoint_head=claimed["checkpoint_head"], branch_id=branch_id,
            loop_id=loop_id, loop_state_digest="LOOP-STATE-1", shared_remote_mode="DISABLED",
        )
        synced = runtime.sync_branch(
            campaign_id=started["campaign_id"], expected_state_digest=bound["state_digest"],
            expected_checkpoint_head=bound["checkpoint_head"], branch_id=branch_id,
            shared_remote_mode="DISABLED",
        )
        self.assertEqual(synced["branch_status"], "WITNESSED")
        return synced

    def test_start_and_verify_campaign(self):
        runtime, _, _ = self._runtime()
        started = self._start(runtime, initial_tasks=["A", "B"])
        self.assertEqual(started["status"], "ACTIVE")
        self.assertEqual(len(started["frontier"]), 2)
        verified = runtime.verify(started["campaign_id"])
        self.assertEqual(verified["status"], "PASS", verified)
        self.assertEqual(verified["branch_count"], 2)
        self.assertEqual(verified["event_count"], 1)

    def test_ambiguous_baton_expands_into_bounded_child_branches(self):
        runtime, loop, _ = self._runtime()
        started = self._start(runtime)
        parent = started["frontier"][0]["branch_id"]
        synced = self._claim_bind_sync_complete(runtime, loop, started, parent)
        baton = _baton(["Explore transport path", "Explore state path"])
        expanded = runtime.expand(
            campaign_id=started["campaign_id"], expected_state_digest=synced["state_digest"],
            expected_checkpoint_head=synced["checkpoint_head"], parent_branch_id=parent,
            successor_baton=baton, shared_remote_mode="DISABLED",
        )
        children = [b for b in expanded["frontier"] if b["parent_branch_id"] == parent]
        self.assertEqual(len(children), 2)
        self.assertEqual({b["task"] for b in children}, {"Explore transport path", "Explore state path"})
        self.assertEqual(runtime.verify(started["campaign_id"])["status"], "PASS")

    def test_width_budget_holds_without_mutation(self):
        runtime, loop, _ = self._runtime()
        started = self._start(runtime, max_width=1)
        parent = started["frontier"][0]["branch_id"]
        synced = self._claim_bind_sync_complete(runtime, loop, started, parent)
        held = runtime.expand(
            campaign_id=started["campaign_id"], expected_state_digest=synced["state_digest"],
            expected_checkpoint_head=synced["checkpoint_head"], parent_branch_id=parent,
            successor_baton=_baton(["A", "B"]), shared_remote_mode="DISABLED",
        )
        self.assertEqual(held["status"], "HOLD_WIDTH")
        resumed = runtime.resume(started["campaign_id"])
        self.assertEqual(resumed["state_digest"], synced["state_digest"])
        self.assertEqual(len(resumed["branches"]), 1)

    def test_branch_lease_blocks_competing_claim_and_can_release(self):
        runtime, _, _ = self._runtime()
        started = self._start(runtime)
        branch = started["frontier"][0]["branch_id"]
        claimed = runtime.claim(
            campaign_id=started["campaign_id"], expected_state_digest=started["state_digest"],
            expected_checkpoint_head=started["checkpoint_head"], branch_id=branch,
            agent="agent-a", shared_remote_mode="DISABLED",
        )
        with self.assertRaisesRegex(ValueError, "active lease"):
            runtime.claim(
                campaign_id=started["campaign_id"], expected_state_digest=claimed["state_digest"],
                expected_checkpoint_head=claimed["checkpoint_head"], branch_id=branch,
                agent="agent-b", shared_remote_mode="DISABLED",
            )
        released = runtime.release(
            campaign_id=started["campaign_id"], expected_state_digest=claimed["state_digest"],
            expected_checkpoint_head=claimed["checkpoint_head"], branch_id=branch,
            agent="agent-a", shared_remote_mode="DISABLED",
        )
        reclaimed = runtime.claim(
            campaign_id=started["campaign_id"], expected_state_digest=released["state_digest"],
            expected_checkpoint_head=released["checkpoint_head"], branch_id=branch,
            agent="agent-b", shared_remote_mode="DISABLED",
        )
        self.assertEqual(reclaimed["frontier"][0]["claim"]["agent"], "agent-b")

    def test_sync_maps_loop_hold_to_blocked(self):
        runtime, loop, _ = self._runtime()
        started = self._start(runtime)
        branch = started["frontier"][0]["branch_id"]
        claimed = runtime.claim(
            campaign_id=started["campaign_id"], expected_state_digest=started["state_digest"],
            expected_checkpoint_head=started["checkpoint_head"], branch_id=branch,
            agent="agent-a", shared_remote_mode="DISABLED",
        )
        loop.add("LOOP-H", status="HOLD_NO_PROGRESS", state_digest="LOOP-HOLD", summary="blocked")
        bound = runtime.bind_loop(
            campaign_id=started["campaign_id"], expected_state_digest=claimed["state_digest"],
            expected_checkpoint_head=claimed["checkpoint_head"], branch_id=branch,
            loop_id="LOOP-H", loop_state_digest="LOOP-HOLD", shared_remote_mode="DISABLED",
        )
        synced = runtime.sync_branch(
            campaign_id=started["campaign_id"], expected_state_digest=bound["state_digest"],
            expected_checkpoint_head=bound["checkpoint_head"], branch_id=branch,
            shared_remote_mode="DISABLED",
        )
        self.assertEqual(synced["branch_status"], "BLOCKED")

    def test_terminal_reconciliation_requires_integration_witness(self):
        runtime, loop, _ = self._runtime()
        started = self._start(runtime)
        branch = started["frontier"][0]["branch_id"]
        synced = self._claim_bind_sync_complete(runtime, loop, started, branch)
        with self.assertRaisesRegex(ValueError, "integration_witness"):
            runtime.reconcile(
                campaign_id=started["campaign_id"], expected_state_digest=synced["state_digest"],
                expected_checkpoint_head=synced["checkpoint_head"], selected_branch_ids=[branch],
                observed=True, summary="select branch", terminal=True, shared_remote_mode="DISABLED",
            )
        final = runtime.reconcile(
            campaign_id=started["campaign_id"], expected_state_digest=synced["state_digest"],
            expected_checkpoint_head=synced["checkpoint_head"], selected_branch_ids=[branch],
            observed=True, summary="selected branch was integrated", terminal=True,
            integration_witness={"observed": True, "git_head": runtime.git.head()},
            evidence_refs=["git://merge"], shared_remote_mode="DISABLED",
        )
        self.assertEqual(final["status"], "COMPLETE")
        verified = runtime.verify(started["campaign_id"])
        self.assertEqual(verified["status"], "PASS", verified)

    def test_reconciliation_is_not_git_merge_authority(self):
        runtime, loop, _ = self._runtime()
        started = self._start(runtime)
        branch = started["frontier"][0]["branch_id"]
        synced = self._claim_bind_sync_complete(runtime, loop, started, branch)
        result = runtime.reconcile(
            campaign_id=started["campaign_id"], expected_state_digest=synced["state_digest"],
            expected_checkpoint_head=synced["checkpoint_head"], selected_branch_ids=[branch],
            observed=True, summary="candidate accepted for later integration", terminal=False,
            shared_remote_mode="DISABLED",
        )
        self.assertEqual(result["status"], "RECONCILED")
        resumed = runtime.resume(started["campaign_id"])
        self.assertIn("RECONCILIATION != GIT_MERGE", resumed["laws"])


if __name__ == "__main__":
    unittest.main()
