from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from .git_backend import GitBackend, GitStaleHead, GitStateError
from .prompt_remote import PromptRemoteSync
from .prompt_runtime import PromptRuntime
from .rehydration_loop import RehydrationLoopRuntime, _sha

CAMPAIGN_ROOT = "prompts/rehydration_campaigns"
ARTIFACT = "ATHENA.REHYDRATION.CAMPAIGN.V2"
BATON_ARTIFACT = "ATHENA.REHYDRATION.SUCCESSOR.BATON.V1"
BRANCH_STATES = {
    "OPEN", "CLAIMED", "ACTIVE", "WITNESSED", "BLOCKED", "EXPANDED",
    "ACCEPTED", "SUPERSEDED",
}
CAMPAIGN_TERMINAL = {"COMPLETE", "ABORTED"}


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _campaign_state_digest(state: dict) -> str:
    return _sha({k: v for k, v in state.items() if k not in {"state_digest", "chain_digest"}})


def _event_digest(event: dict) -> str:
    return _sha({k: v for k, v in event.items() if k not in {"event_digest", "chain_digest"}})


def _task(raw: Any) -> str:
    if isinstance(raw, str):
        return raw.strip()
    if isinstance(raw, dict):
        for key in ("task", "title", "description", "summary"):
            value = raw.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return ""


def _baton_valid(baton: dict) -> bool:
    if not isinstance(baton, dict) or baton.get("artifact") != BATON_ARTIFACT:
        return False
    digest = baton.get("baton_digest")
    return isinstance(digest, str) and digest == _sha({k: v for k, v in baton.items() if k != "baton_digest"})


class RehydrationCampaignRuntime:
    """Bounded branch graph over explicit V1 rehydration loops.

    Campaign branches are coordination objects. They do not create hidden workers,
    merge code, or elevate routing decisions into authority. Each bound branch
    delegates actual sequential work to a normal RehydrationLoopRuntime.
    """

    def __init__(
        self,
        git: GitBackend,
        prompt_runtime: PromptRuntime | None = None,
        loop_runtime: RehydrationLoopRuntime | None = None,
        remote_sync: PromptRemoteSync | None = None,
    ):
        self.git = git
        self.prompt_runtime = prompt_runtime or PromptRuntime(git)
        self.loop_runtime = loop_runtime or RehydrationLoopRuntime(git, self.prompt_runtime)
        self.remote_sync = remote_sync or PromptRemoteSync(git)

    @property
    def available(self) -> bool:
        return bool(self.git.enabled and self.prompt_runtime.available)

    def _root(self) -> Path:
        if not self.git.enabled:
            raise GitStateError("ATHENA_GIT_ROOT is required for rehydration campaigns")
        return self.git.root

    def _safe_rel(self, rel: str) -> Path:
        return self.prompt_runtime._safe_rel(rel)

    @staticmethod
    def _base(campaign_id: str) -> str:
        if not isinstance(campaign_id, str) or not campaign_id.startswith("RHC-"):
            raise ValueError("invalid campaign_id")
        return f"{CAMPAIGN_ROOT}/{campaign_id}"

    def _paths(self, campaign_id: str) -> dict[str, str]:
        base = self._base(campaign_id)
        return {
            "base": base,
            "state": f"{base}/state.json",
            "events": f"{base}/events",
            "batons": f"{base}/batons",
        }

    def _read_state(self, campaign_id: str) -> tuple[dict, dict[str, str]]:
        paths = self._paths(campaign_id)
        path = self._safe_rel(paths["state"])
        if not path.is_file():
            raise ValueError("campaign not found")
        state = json.loads(path.read_text(encoding="utf-8"))
        if state.get("artifact") != ARTIFACT or state.get("campaign_id") != campaign_id:
            raise ValueError("invalid campaign state")
        return state, paths

    def _path_last_commit(self, rel: str) -> str | None:
        import subprocess
        p = subprocess.run(
            ["git", "-C", str(self._root()), "log", "-n", "1", "--format=%H", "--", rel],
            text=True,
            capture_output=True,
        )
        if p.returncode:
            raise GitStateError(p.stderr.strip() or p.stdout.strip())
        return p.stdout.strip() or None

    def _is_ancestor(self, older: str, newer: str) -> bool:
        import subprocess
        p = subprocess.run(
            ["git", "-C", str(self._root()), "merge-base", "--is-ancestor", older, newer],
            text=True,
            capture_output=True,
        )
        if p.returncode not in (0, 1):
            raise GitStateError(p.stderr.strip() or p.stdout.strip())
        return p.returncode == 0

    @staticmethod
    def _remote_mode(value: str | None) -> str:
        mode = str(value or "REQUIRED").upper()
        if mode not in {"REQUIRED", "BEST_EFFORT", "DISABLED"}:
            raise ValueError("shared_remote_mode must be REQUIRED, BEST_EFFORT, or DISABLED")
        return mode

    def _sync(self, mode: str, remote: str) -> dict:
        if mode == "DISABLED":
            return {"status": "DISABLED", "shared_frontier_verified": False}
        state = self.remote_sync.sync(remote)
        if mode == "REQUIRED" and not state.get("shared_frontier_verified"):
            raise GitStateError(json.dumps({"status": "CAMPAIGN_SHARED_FRONTIER_HOLD", "remote_sync": state}, sort_keys=True))
        return state

    def _publish(self, mode: str, remote: str, head: str) -> dict:
        if mode == "DISABLED":
            return {"status": "DISABLED", "shared_frontier_verified": False}
        state = self.remote_sync.publish(head, remote)
        if mode == "REQUIRED" and not state.get("shared_frontier_verified"):
            raise GitStateError(json.dumps({"status": "CAMPAIGN_PUBLISH_HOLD", "remote_publish": state}, sort_keys=True))
        return state

    @staticmethod
    def _branch_id(parent: str | None, task: str, depth: int, candidate_id: str | None = None) -> str:
        basis = {"parent": parent, "task": " ".join(task.lower().split()), "depth": depth, "candidate_id": candidate_id}
        return "CB-" + _sha(basis)[:16]

    @staticmethod
    def _new_branch(task: str, depth: int, parent: str | None, candidate: dict | None = None) -> dict:
        candidate = dict(candidate or {})
        branch_id = RehydrationCampaignRuntime._branch_id(parent, task, depth, candidate.get("candidate_id"))
        return {
            "branch_id": branch_id,
            "parent_branch_id": parent,
            "depth": depth,
            "task": task,
            "status": "OPEN",
            "candidate_id": candidate.get("candidate_id"),
            "candidate_metrics": candidate.get("metrics"),
            "routing_score": candidate.get("routing_score"),
            "source": candidate.get("source"),
            "created_at": _utcnow(),
            "updated_at": _utcnow(),
            "claim": None,
            "loop": None,
            "evidence_refs": [],
            "completion_summary": None,
            "successor_baton": None,
        }

    @staticmethod
    def _frontier(state: dict) -> list[dict]:
        active = {"OPEN", "CLAIMED", "ACTIVE", "WITNESSED", "BLOCKED"}
        return sorted(
            [b for b in state["branches"].values() if b.get("status") in active],
            key=lambda b: (int(b.get("depth") or 0), str(b.get("branch_id"))),
        )

    def _assert_state(self, state: dict, expected_state_digest: str) -> None:
        if _campaign_state_digest(state) != state.get("state_digest") or state.get("state_digest") != expected_state_digest:
            raise GitStateError("STALE_OR_TAMPERED_CAMPAIGN_STATE")
        if state.get("status") in CAMPAIGN_TERMINAL:
            raise ValueError(f"campaign is terminal: {state.get('status')}")

    def _mutate(
        self,
        *,
        campaign_id: str,
        expected_state_digest: str,
        expected_checkpoint_head: str,
        actor: str,
        event_type: str,
        mutator: Callable[[dict], dict],
        shared_remote_mode: str,
        remote: str,
        extra_files: dict[str, str] | None = None,
    ) -> dict:
        state, paths = self._read_state(campaign_id)
        self._assert_state(state, expected_state_digest)
        checkpoint = self._path_last_commit(paths["state"])
        if checkpoint != expected_checkpoint_head:
            raise GitStaleHead(json.dumps({"status": "STALE_CAMPAIGN_CHECKPOINT", "expected": expected_checkpoint_head, "current": checkpoint}, sort_keys=True))
        mode = self._remote_mode(shared_remote_mode)
        remote_sync = self._sync(mode, remote)
        checkpoint = self._path_last_commit(paths["state"])
        if checkpoint != expected_checkpoint_head:
            raise GitStaleHead("shared sync revealed a newer campaign checkpoint")
        current_head = self.git.head()
        if not self._is_ancestor(expected_checkpoint_head, current_head):
            raise GitStaleHead("campaign checkpoint is not an ancestor of current Git head")

        before_digest = state["state_digest"]
        previous_chain = state["chain_digest"]
        new_state = mutator(json.loads(json.dumps(state)))
        new_state["updated_at"] = _utcnow()
        new_state["logical_clock"] = int(state.get("logical_clock") or 0) + 1
        new_state["previous_chain_digest"] = previous_chain
        new_state["state_digest"] = _campaign_state_digest(new_state)
        seq = int(new_state["logical_clock"])
        event = {
            "artifact": "ATHENA.REHYDRATION.CAMPAIGN.EVENT.V2",
            "campaign_id": campaign_id,
            "event_type": event_type,
            "sequence": seq,
            "actor": actor,
            "created_at": _utcnow(),
            "checkpoint_head": expected_checkpoint_head,
            "work_head": current_head,
            "before_state_digest": before_digest,
            "after_state_digest": new_state["state_digest"],
            "previous_chain_digest": previous_chain,
        }
        event["event_digest"] = _event_digest(event)
        new_state["chain_digest"] = _sha({"previous": previous_chain, "event_digest": event["event_digest"], "state_digest": new_state["state_digest"]})
        event["chain_digest"] = new_state["chain_digest"]
        files = {
            paths["state"]: json.dumps(new_state, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            f"{paths['events']}/{seq:04d}-{event_type.lower()}.json": json.dumps(event, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        }
        files.update(extra_files or {})
        git_result = self.prompt_runtime._commit_files(current_head, files, actor, f"campaign {campaign_id} {event_type.lower()}")
        publish = self._publish(mode, remote, git_result["head"])
        return {
            "status": new_state["status"],
            "campaign_id": campaign_id,
            "state_digest": new_state["state_digest"],
            "chain_digest": new_state["chain_digest"],
            "checkpoint_head": git_result["head"],
            "logical_clock": new_state["logical_clock"],
            "frontier": self._frontier(new_state),
            "git": git_result,
            "remote_sync": remote_sync,
            "remote_publish": publish,
            "durable_return": bool(publish.get("shared_frontier_verified")) if mode != "DISABLED" else False,
        }

    def start(
        self,
        *,
        goal: str,
        expected_git_head: str,
        initial_tasks: list[Any] | None = None,
        actor: str = "agent",
        max_width: int = 4,
        max_depth: int = 8,
        max_branches: int = 32,
        lease_steps: int = 4,
        shared_remote_mode: str = "REQUIRED",
        remote: str = "origin",
    ) -> dict:
        goal = str(goal or "").strip()
        if not goal:
            raise ValueError("goal is required")
        max_width = int(max_width); max_depth = int(max_depth); max_branches = int(max_branches); lease_steps = int(lease_steps)
        if not 1 <= max_width <= 16 or not 1 <= max_depth <= 32 or not 1 <= max_branches <= 256 or not 1 <= lease_steps <= 32:
            raise ValueError("campaign budgets out of range")
        mode = self._remote_mode(shared_remote_mode)
        remote_sync = self._sync(mode, remote)
        current = self.git.head()
        if current != expected_git_head:
            raise GitStaleHead(json.dumps({"status": "STALE_GIT_HEAD", "expected": expected_git_head, "current": current}, sort_keys=True))
        tasks = [_task(x) for x in (initial_tasks or [goal])]
        tasks = [x for x in tasks if x]
        if not tasks:
            raise ValueError("at least one initial task is required")
        if len(tasks) > max_width or len(tasks) > max_branches:
            raise ValueError("initial tasks exceed campaign width/branch budget")
        campaign_id = f"RHC-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}"
        paths = self._paths(campaign_id)
        branches = {}
        for task in tasks:
            branch = self._new_branch(task, 0, None)
            if branch["branch_id"] in branches:
                continue
            branches[branch["branch_id"]] = branch
        state = {
            "artifact": ARTIFACT,
            "campaign_id": campaign_id,
            "status": "ACTIVE",
            "goal": goal,
            "actor": actor,
            "created_at": _utcnow(),
            "updated_at": _utcnow(),
            "base_head": current,
            "logical_clock": 0,
            "previous_chain_digest": None,
            "budget": {"max_width": max_width, "max_depth": max_depth, "max_branches": max_branches, "lease_steps": lease_steps},
            "branches": branches,
            "reconciliations": [],
        }
        state["state_digest"] = _campaign_state_digest(state)
        event = {
            "artifact": "ATHENA.REHYDRATION.CAMPAIGN.EVENT.V2",
            "campaign_id": campaign_id,
            "event_type": "CAMPAIGN_STARTED",
            "sequence": 0,
            "actor": actor,
            "created_at": _utcnow(),
            "checkpoint_head": current,
            "before_state_digest": None,
            "after_state_digest": state["state_digest"],
            "previous_chain_digest": None,
        }
        event["event_digest"] = _event_digest(event)
        state["chain_digest"] = _sha({"previous": None, "event_digest": event["event_digest"], "state_digest": state["state_digest"]})
        event["chain_digest"] = state["chain_digest"]
        files = {
            paths["state"]: json.dumps(state, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            f"{paths['events']}/0000-campaign_started.json": json.dumps(event, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        }
        git_result = self.prompt_runtime._commit_files(current, files, actor, f"start rehydration campaign {campaign_id}")
        publish = self._publish(mode, remote, git_result["head"])
        return {
            "status": "ACTIVE",
            "campaign_id": campaign_id,
            "state_digest": state["state_digest"],
            "chain_digest": state["chain_digest"],
            "checkpoint_head": git_result["head"],
            "frontier": self._frontier(state),
            "git": git_result,
            "remote_sync": remote_sync,
            "remote_publish": publish,
        }

    def expand(
        self,
        *,
        campaign_id: str,
        expected_state_digest: str,
        expected_checkpoint_head: str,
        parent_branch_id: str,
        successor_baton: dict,
        selected_candidate_ids: list[str] | None = None,
        actor: str = "agent",
        shared_remote_mode: str = "REQUIRED",
        remote: str = "origin",
    ) -> dict:
        if not _baton_valid(successor_baton):
            raise ValueError("invalid successor baton")
        state, _ = self._read_state(campaign_id)
        self._assert_state(state, expected_state_digest)
        parent = state["branches"].get(parent_branch_id)
        if not parent:
            raise ValueError("parent branch not found")
        if parent["status"] not in {"WITNESSED", "BLOCKED", "ACTIVE"}:
            raise ValueError("parent branch is not eligible for expansion")
        if int(parent["depth"]) >= int(state["budget"]["max_depth"]):
            return {"status": "HOLD_DEPTH", "campaign_id": campaign_id, "parent_branch_id": parent_branch_id, "state_digest": state["state_digest"]}
        status = successor_baton.get("status")
        if status == "AMBIGUOUS":
            candidates = list(successor_baton.get("ties") or [])
        elif status == "SELECTED" and successor_baton.get("selected"):
            candidates = [successor_baton["selected"]]
        elif status in {"NO_SUCCESSOR", "TERMINAL"}:
            return {"status": status, "campaign_id": campaign_id, "parent_branch_id": parent_branch_id, "state_digest": state["state_digest"]}
        else:
            raise ValueError("successor baton is not expandable")
        if selected_candidate_ids is not None:
            wanted = set(selected_candidate_ids)
            candidates = [x for x in candidates if x.get("candidate_id") in wanted]
        if not candidates:
            raise ValueError("no successor candidates selected for expansion")
        candidate_ids = {x.get("candidate_id") for x in candidates}
        if None in candidate_ids or len(candidate_ids) != len(candidates):
            raise ValueError("successor candidates require unique candidate_id")
        existing = len(state["branches"])
        if existing + len(candidates) > int(state["budget"]["max_branches"]):
            return {"status": "HOLD_BRANCH_BUDGET", "campaign_id": campaign_id, "required": existing + len(candidates), "limit": state["budget"]["max_branches"], "state_digest": state["state_digest"]}
        depth = int(parent["depth"]) + 1
        active_at_depth = sum(1 for b in state["branches"].values() if int(b["depth"]) == depth and b["status"] in {"OPEN", "CLAIMED", "ACTIVE", "WITNESSED", "BLOCKED"})
        if active_at_depth + len(candidates) > int(state["budget"]["max_width"]):
            return {"status": "HOLD_WIDTH", "campaign_id": campaign_id, "depth": depth, "required": active_at_depth + len(candidates), "limit": state["budget"]["max_width"], "candidate_ids": sorted(candidate_ids), "state_digest": state["state_digest"]}

        baton_path = f"{self._paths(campaign_id)['batons']}/{int(state['logical_clock']) + 1:04d}-{successor_baton['baton_digest'][:12]}.json"
        def mutate(new_state):
            p = new_state["branches"][parent_branch_id]
            p["status"] = "EXPANDED"
            p["successor_baton"] = successor_baton
            p["updated_at"] = _utcnow()
            for candidate in candidates:
                task = _task(candidate)
                if not task:
                    raise ValueError("successor candidate has no task")
                child = self._new_branch(task, depth, parent_branch_id, candidate)
                if child["branch_id"] in new_state["branches"]:
                    continue
                new_state["branches"][child["branch_id"]] = child
            return new_state
        result = self._mutate(
            campaign_id=campaign_id, expected_state_digest=expected_state_digest,
            expected_checkpoint_head=expected_checkpoint_head, actor=actor,
            event_type="BRANCH_EXPANDED", mutator=mutate,
            shared_remote_mode=shared_remote_mode, remote=remote,
            extra_files={baton_path: json.dumps(successor_baton, indent=2, sort_keys=True, ensure_ascii=False) + "\n"},
        )
        result["baton_path"] = baton_path
        result["expanded_candidate_ids"] = sorted(candidate_ids)
        return result

    def claim(self, *, campaign_id: str, expected_state_digest: str, expected_checkpoint_head: str, branch_id: str, agent: str, actor: str = "agent", shared_remote_mode: str = "REQUIRED", remote: str = "origin") -> dict:
        def mutate(state):
            branch = state["branches"].get(branch_id)
            if not branch:
                raise ValueError("branch not found")
            clock = int(state.get("logical_clock") or 0)
            claim = branch.get("claim")
            if branch["status"] == "CLAIMED" and claim and int(claim.get("lease_until_clock") or 0) > clock and claim.get("agent") != agent:
                raise ValueError("branch has an active lease")
            if branch["status"] not in {"OPEN", "CLAIMED", "BLOCKED"}:
                raise ValueError("branch is not claimable")
            branch["status"] = "CLAIMED"
            branch["claim"] = {"agent": agent, "claimed_clock": clock + 1, "lease_until_clock": clock + 1 + int(state["budget"]["lease_steps"])}
            branch["updated_at"] = _utcnow()
            return state
        return self._mutate(campaign_id=campaign_id, expected_state_digest=expected_state_digest, expected_checkpoint_head=expected_checkpoint_head, actor=actor, event_type="BRANCH_CLAIMED", mutator=mutate, shared_remote_mode=shared_remote_mode, remote=remote)

    def release(self, *, campaign_id: str, expected_state_digest: str, expected_checkpoint_head: str, branch_id: str, agent: str, actor: str = "agent", shared_remote_mode: str = "REQUIRED", remote: str = "origin") -> dict:
        def mutate(state):
            branch = state["branches"].get(branch_id)
            if not branch:
                raise ValueError("branch not found")
            claim = branch.get("claim") or {}
            if claim.get("agent") != agent:
                raise ValueError("only the current lease holder may release the branch")
            if branch["status"] not in {"CLAIMED", "BLOCKED"}:
                raise ValueError("branch is not releasable")
            branch["status"] = "OPEN"
            branch["claim"] = None
            branch["updated_at"] = _utcnow()
            return state
        return self._mutate(campaign_id=campaign_id, expected_state_digest=expected_state_digest, expected_checkpoint_head=expected_checkpoint_head, actor=actor, event_type="BRANCH_RELEASED", mutator=mutate, shared_remote_mode=shared_remote_mode, remote=remote)

    def bind_loop(self, *, campaign_id: str, expected_state_digest: str, expected_checkpoint_head: str, branch_id: str, loop_id: str, loop_state_digest: str, actor: str = "agent", shared_remote_mode: str = "REQUIRED", remote: str = "origin") -> dict:
        loop_state, loop_paths = self.loop_runtime._read_state(loop_id)
        if loop_state.get("state_digest") != loop_state_digest:
            raise ValueError("loop state digest mismatch")
        loop_checkpoint = self.loop_runtime._path_last_commit(loop_paths["state"])
        def mutate(state):
            branch = state["branches"].get(branch_id)
            if not branch:
                raise ValueError("branch not found")
            if branch["status"] not in {"CLAIMED", "ACTIVE"}:
                raise ValueError("branch must be claimed before loop binding")
            branch["status"] = "ACTIVE"
            branch["loop"] = {
                "loop_id": loop_id,
                "state_digest": loop_state_digest,
                "chain_digest": loop_state.get("chain_digest"),
                "checkpoint_head": loop_checkpoint,
                "step_index": loop_state.get("step_index"),
                "status": loop_state.get("status"),
            }
            branch["updated_at"] = _utcnow()
            return state
        result = self._mutate(campaign_id=campaign_id, expected_state_digest=expected_state_digest, expected_checkpoint_head=expected_checkpoint_head, actor=actor, event_type="LOOP_BOUND", mutator=mutate, shared_remote_mode=shared_remote_mode, remote=remote)
        result["loop_id"] = loop_id
        return result

    def sync_branch(self, *, campaign_id: str, expected_state_digest: str, expected_checkpoint_head: str, branch_id: str, actor: str = "agent", shared_remote_mode: str = "REQUIRED", remote: str = "origin") -> dict:
        state, _ = self._read_state(campaign_id)
        self._assert_state(state, expected_state_digest)
        branch = state["branches"].get(branch_id)
        if not branch or not branch.get("loop"):
            raise ValueError("branch has no bound loop")
        loop_id = branch["loop"]["loop_id"]
        loop_state, loop_paths = self.loop_runtime._read_state(loop_id)
        loop_checkpoint = self.loop_runtime._path_last_commit(loop_paths["state"])
        mapping = {
            "ACTIVE": "ACTIVE",
            "COMPLETE": "WITNESSED",
            "HOLD_MAX_STEPS": "BLOCKED",
            "HOLD_NO_PROGRESS": "BLOCKED",
            "ABORTED": "BLOCKED",
        }
        branch_status = mapping.get(loop_state.get("status"), "BLOCKED")
        completion = loop_state.get("last_completion") or {}
        def mutate(new_state):
            b = new_state["branches"][branch_id]
            b["status"] = branch_status
            b["loop"] = {
                "loop_id": loop_id,
                "state_digest": loop_state.get("state_digest"),
                "chain_digest": loop_state.get("chain_digest"),
                "checkpoint_head": loop_checkpoint,
                "step_index": loop_state.get("step_index"),
                "status": loop_state.get("status"),
            }
            b["completion_summary"] = completion.get("summary")
            b["evidence_refs"] = list(completion.get("evidence_refs") or [])
            b["successor_baton"] = completion.get("successor_baton")
            b["updated_at"] = _utcnow()
            return new_state
        result = self._mutate(campaign_id=campaign_id, expected_state_digest=expected_state_digest, expected_checkpoint_head=expected_checkpoint_head, actor=actor, event_type="BRANCH_SYNCED", mutator=mutate, shared_remote_mode=shared_remote_mode, remote=remote)
        result["branch_id"] = branch_id
        result["branch_status"] = branch_status
        result["loop_status"] = loop_state.get("status")
        return result

    def reconcile(self, *, campaign_id: str, expected_state_digest: str, expected_checkpoint_head: str, selected_branch_ids: list[str], observed: bool, summary: str, evidence_refs: list[str] | None = None, terminal: bool = False, integration_witness: dict | None = None, actor: str = "agent", shared_remote_mode: str = "REQUIRED", remote: str = "origin") -> dict:
        if observed is not True or not str(summary or "").strip():
            raise ValueError("reconciliation requires observed=true and a summary")
        selected = set(selected_branch_ids or [])
        if not selected:
            raise ValueError("at least one branch must be selected")
        state, _ = self._read_state(campaign_id)
        self._assert_state(state, expected_state_digest)
        missing = selected - set(state["branches"])
        if missing:
            raise ValueError(f"unknown selected branches: {sorted(missing)}")
        if any(state["branches"][bid]["status"] != "WITNESSED" for bid in selected):
            raise ValueError("only WITNESSED branches may be reconciled as accepted")
        if terminal:
            if not isinstance(integration_witness, dict) or integration_witness.get("observed") is not True or not integration_witness.get("git_head"):
                raise ValueError("terminal campaign reconciliation requires an observed integration_witness with git_head")
        def mutate(new_state):
            for bid, branch in new_state["branches"].items():
                if bid in selected:
                    branch["status"] = "ACCEPTED"
                elif branch["status"] in {"WITNESSED", "BLOCKED"}:
                    branch["status"] = "SUPERSEDED"
                branch["updated_at"] = _utcnow()
            rec = {
                "selected_branch_ids": sorted(selected),
                "observed": True,
                "summary": str(summary).strip(),
                "evidence_refs": list(evidence_refs or []),
                "terminal": bool(terminal),
                "integration_witness": integration_witness,
                "recorded_at": _utcnow(),
                "law": "RECONCILED != GIT_MERGED unless integration_witness is observed",
            }
            rec["reconciliation_digest"] = _sha(rec)
            new_state["reconciliations"].append(rec)
            new_state["status"] = "COMPLETE" if terminal else "RECONCILED"
            return new_state
        result = self._mutate(campaign_id=campaign_id, expected_state_digest=expected_state_digest, expected_checkpoint_head=expected_checkpoint_head, actor=actor, event_type="CAMPAIGN_RECONCILED", mutator=mutate, shared_remote_mode=shared_remote_mode, remote=remote)
        result["selected_branch_ids"] = sorted(selected)
        return result

    def resume(self, campaign_id: str) -> dict:
        state, paths = self._read_state(campaign_id)
        state_ok = _campaign_state_digest(state) == state.get("state_digest")
        return {
            "status": "RESUMED" if state_ok else "INTEGRITY_HOLD",
            "campaign_id": campaign_id,
            "campaign_status": state.get("status"),
            "goal": state.get("goal"),
            "state_digest": state.get("state_digest"),
            "chain_digest": state.get("chain_digest"),
            "logical_clock": state.get("logical_clock"),
            "checkpoint_head": self._path_last_commit(paths["state"]),
            "budget": state.get("budget"),
            "frontier": self._frontier(state),
            "branches": sorted(state["branches"].values(), key=lambda b: (int(b.get("depth") or 0), str(b.get("branch_id")))),
            "reconciliations": state.get("reconciliations") or [],
            "laws": ["CAMPAIGN_BRANCH != BACKGROUND_WORKER", "RECONCILIATION != GIT_MERGE", "BRANCH_ROUTING != AUTHORITY"],
        }

    def verify(self, campaign_id: str) -> dict:
        state, paths = self._read_state(campaign_id)
        failures = []
        if _campaign_state_digest(state) != state.get("state_digest"):
            failures.append("STATE_DIGEST")
        branches = state.get("branches") or {}
        if len(branches) > int((state.get("budget") or {}).get("max_branches") or 0):
            failures.append("BRANCH_BUDGET")
        by_depth: dict[int, int] = {}
        for bid, branch in branches.items():
            if bid != branch.get("branch_id") or branch.get("status") not in BRANCH_STATES:
                failures.append(f"BRANCH_IDENTITY:{bid}")
            depth = int(branch.get("depth") or 0)
            if depth > int(state["budget"]["max_depth"]):
                failures.append(f"DEPTH:{bid}")
            parent = branch.get("parent_branch_id")
            if parent:
                if parent not in branches:
                    failures.append(f"PARENT_MISSING:{bid}")
                elif int(branches[parent].get("depth") or -1) + 1 != depth:
                    failures.append(f"PARENT_DEPTH:{bid}")
            if branch.get("status") in {"OPEN", "CLAIMED", "ACTIVE", "WITNESSED", "BLOCKED"}:
                by_depth[depth] = by_depth.get(depth, 0) + 1
        for depth, count in by_depth.items():
            if count > int(state["budget"]["max_width"]):
                failures.append(f"WIDTH:{depth}")

        event_dir = self._safe_rel(paths["events"])
        event_files = sorted(event_dir.glob("*.json")) if event_dir.is_dir() else []
        previous_chain = None
        previous_state = None
        for index, path in enumerate(event_files):
            try:
                event = json.loads(path.read_text(encoding="utf-8"))
                if event.get("campaign_id") != campaign_id or int(event.get("sequence", -1)) != index:
                    failures.append(f"EVENT_SEQUENCE:{path.name}")
                if event.get("previous_chain_digest") != previous_chain:
                    failures.append(f"EVENT_CHAIN_PARENT:{path.name}")
                if index and event.get("before_state_digest") != previous_state:
                    failures.append(f"EVENT_STATE_PARENT:{path.name}")
                digest = _event_digest(event)
                if digest != event.get("event_digest"):
                    failures.append(f"EVENT_DIGEST:{path.name}")
                chain = _sha({"previous": previous_chain, "event_digest": event.get("event_digest"), "state_digest": event.get("after_state_digest")})
                if chain != event.get("chain_digest"):
                    failures.append(f"EVENT_CHAIN:{path.name}")
                previous_chain = chain
                previous_state = event.get("after_state_digest")
            except Exception as exc:
                failures.append(f"EVENT_INVALID:{path.name}:{type(exc).__name__}")
        if previous_chain != state.get("chain_digest"):
            failures.append("STATE_CHAIN")
        if previous_state != state.get("state_digest"):
            failures.append("STATE_EVENT_TIP")
        return {
            "status": "PASS" if not failures else "HOLD",
            "campaign_id": campaign_id,
            "failures": failures,
            "branch_count": len(branches),
            "event_count": len(event_files),
            "frontier_count": len(self._frontier(state)),
            "state_digest": state.get("state_digest"),
            "chain_digest": state.get("chain_digest"),
            "checkpoint_head": self._path_last_commit(paths["state"]),
            "law": "PASS verifies campaign causal integrity; it does not prove branch work correctness or Git integration",
        }


CAMPAIGN_TOOLS = [
    {"name": "athena_rehydration_campaign_start", "description": "Start a bounded multi-branch rehydration campaign from an exact Git head.", "inputSchema": {"type": "object"}},
    {"name": "athena_rehydration_campaign_expand", "description": "Materialize selected or ambiguous successor baton candidates as bounded campaign branches.", "inputSchema": {"type": "object"}},
    {"name": "athena_rehydration_campaign_claim", "description": "Claim one campaign branch with a logical-clock lease.", "inputSchema": {"type": "object"}},
    {"name": "athena_rehydration_campaign_release", "description": "Release a claimed campaign branch back to OPEN.", "inputSchema": {"type": "object"}},
    {"name": "athena_rehydration_campaign_bind_loop", "description": "Bind a claimed campaign branch to an exact V1 rehydration loop checkpoint.", "inputSchema": {"type": "object"}},
    {"name": "athena_rehydration_campaign_sync_branch", "description": "Synchronize a campaign branch from its bound V1 loop state.", "inputSchema": {"type": "object"}},
    {"name": "athena_rehydration_campaign_reconcile", "description": "Record an observed branch reconciliation; terminal completion requires an observed Git integration witness.", "inputSchema": {"type": "object"}},
    {"name": "athena_rehydration_campaign_resume", "description": "Read the current campaign branch frontier and exact coordination state.", "inputSchema": {"type": "object"}},
    {"name": "athena_rehydration_campaign_verify", "description": "Verify campaign event-chain, branch topology and budget invariants.", "inputSchema": {"type": "object"}},
]
CAMPAIGN_TOOL_NAMES = {x["name"] for x in CAMPAIGN_TOOLS}
