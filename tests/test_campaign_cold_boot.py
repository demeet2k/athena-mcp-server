from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from athena_mcp.campaign_cold_boot import cold_resume_steering_campaign
from athena_mcp.rehydration_campaign import ARTIFACT, CAMPAIGN_ROOT, _campaign_state_digest


class _Git:
    def __init__(self, head="head-current"):
        self._head = head

    def head(self):
        return self._head


class _Runtime:
    def __init__(self, root: Path, *, shared_fresh=True, verify_status="PASS", bad_ancestor=None):
        self.root = root
        self.shared_fresh = shared_fresh
        self.verify_status = verify_status
        self.bad_ancestor = bad_ancestor
        self.git = _Git()

    def _safe_rel(self, rel):
        return self.root / rel

    def _remote_mode(self, value):
        return str(value or "REQUIRED").upper()

    def _sync(self, mode, remote):
        return {
            "status": "UP_TO_DATE" if self.shared_fresh else "UNVERIFIED",
            "shared_frontier_verified": self.shared_fresh,
            "remote": remote,
        }

    def _read_state(self, campaign_id):
        rel = f"{CAMPAIGN_ROOT}/{campaign_id}/state.json"
        path = self._safe_rel(rel)
        state = json.loads(path.read_text(encoding="utf-8"))
        return state, {"state": rel}

    def _path_last_commit(self, rel):
        campaign_id = Path(rel).parent.name
        return f"checkpoint-{campaign_id}"

    def _is_ancestor(self, older, newer):
        return (older, newer) != self.bad_ancestor

    def verify(self, campaign_id):
        return {
            "status": self.verify_status,
            "campaign_id": campaign_id,
            "failures": [] if self.verify_status == "PASS" else ["TEST_HOLD"],
        }


def _branch(branch_id="CB-1", *, status="ACTIVE", bound=True, pulse=1):
    return {
        "branch_id": branch_id,
        "parent_branch_id": None,
        "depth": 0,
        "task": f"Steering residual pulse {pulse}",
        "status": status,
        "source": {
            "kind": "STEERING_LEDGER_RESIDUAL",
            "pulse_index": pulse,
            "step": pulse,
        },
        "loop": {
            "loop_id": f"LOOP-{branch_id}",
            "state_digest": "loop-state",
            "chain_digest": "loop-chain",
            "checkpoint_head": "loop-cp",
            "step_index": 1,
            "status": "ACTIVE",
        }
        if bound
        else None,
    }


def _state(campaign_id="RHC-TEST", *, branches=None, goal="Campaign V3 steering ledger"):
    if branches is None:
        branches = [_branch()]
    state = {
        "artifact": ARTIFACT,
        "campaign_id": campaign_id,
        "status": "ACTIVE",
        "goal": goal,
        "actor": "test",
        "created_at": "2026-08-08T00:00:00+00:00",
        "updated_at": "2026-08-08T00:00:00+00:00",
        "base_head": "head-base",
        "logical_clock": 1,
        "previous_chain_digest": None,
        "budget": {"max_width": 4, "max_depth": 8, "max_branches": 32, "lease_steps": 4},
        "branches": {row["branch_id"]: row for row in branches},
        "reconciliations": [],
    }
    state["state_digest"] = _campaign_state_digest(state)
    state["chain_digest"] = "campaign-chain"
    return state


def _write(root: Path, state):
    path = root / CAMPAIGN_ROOT / state["campaign_id"] / "state.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state), encoding="utf-8")


class CampaignColdBootTests(unittest.TestCase):
    def test_absent_namespace_holds_without_inventing_campaign(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = cold_resume_steering_campaign(_Runtime(Path(tmp)))
        self.assertEqual("HOLD_NO_CAMPAIGN", result["status"])
        self.assertEqual("ABSENT", result["observed_namespace"])
        self.assertFalse(result["execution_authority"])

    def test_unverified_shared_frontier_holds_before_discovery(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = cold_resume_steering_campaign(_Runtime(Path(tmp), shared_fresh=False))
        self.assertEqual("HOLD_SHARED_FRESHNESS", result["status"])

    def test_unique_unbound_steering_branch_is_discovered_without_chat_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, _state(branches=[_branch(bound=False)]))
            result = cold_resume_steering_campaign(_Runtime(root))
        self.assertEqual("DISCOVERED_UNBOUND_BRANCH", result["status"])
        self.assertEqual("RHC-TEST", result["discovered"]["campaign_id"])
        self.assertEqual("CB-1", result["discovered"]["branch_id"])
        self.assertIsNone(result["discovered"]["loop_id"])

    def test_unique_bound_branch_delegates_exact_discovered_coordinates_to_fresh_resume(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state = _state()
            _write(root, state)
            with patch("athena_mcp.campaign_cold_boot.fresh_resume_branch") as fresh:
                fresh.return_value = {
                    "status": "ALIGNED_ACTIVE",
                    "next": "CONTINUE_BOUND_LOOP",
                    "execution_authority": False,
                }
                result = cold_resume_steering_campaign(_Runtime(root))
        self.assertEqual("COLD_RESUME_COMPLETE", result["status"])
        self.assertEqual("CONTINUE_BOUND_LOOP", result["next"])
        kwargs = fresh.call_args.kwargs
        self.assertEqual("RHC-TEST", kwargs["campaign_id"])
        self.assertEqual("CB-1", kwargs["branch_id"])
        self.assertEqual(state["state_digest"], kwargs["expected_state_digest"])
        self.assertEqual("checkpoint-RHC-TEST", kwargs["expected_checkpoint_head"])

    def test_multiple_valid_campaigns_hold_on_identity_ambiguity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, _state("RHC-A", branches=[_branch("CB-A")]))
            _write(root, _state("RHC-B", branches=[_branch("CB-B")]))
            result = cold_resume_steering_campaign(_Runtime(root))
        self.assertEqual("HOLD_AMBIGUOUS_CAMPAIGN", result["status"])
        self.assertEqual(["RHC-A", "RHC-B"], [row["campaign_id"] for row in result["campaign_candidates"]])

    def test_multiple_active_steering_branches_hold_without_scalar_guess(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, _state(branches=[_branch("CB-A"), _branch("CB-B", pulse=2)]))
            result = cold_resume_steering_campaign(_Runtime(root))
        self.assertEqual("HOLD_AMBIGUOUS_BRANCH", result["status"])
        self.assertEqual(["CB-A", "CB-B"], result["active_branch_ids"])

    def test_invalid_state_digest_is_not_a_valid_campaign(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state = _state()
            state["goal"] = "tampered after digest"
            _write(root, state)
            result = cold_resume_steering_campaign(_Runtime(root))
        self.assertEqual("HOLD_NO_VALID_STEERING_CAMPAIGN", result["status"])
        self.assertEqual("STATE_DIGEST_HOLD", result["diagnostics"][0]["standing"])

    def test_campaign_replay_hold_excludes_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, _state())
            result = cold_resume_steering_campaign(_Runtime(root, verify_status="HOLD"))
        self.assertEqual("HOLD_NO_VALID_STEERING_CAMPAIGN", result["status"])
        self.assertEqual("VERIFY_HOLD", result["diagnostics"][0]["standing"])

    def test_stale_campaign_checkpoint_excludes_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, _state())
            result = cold_resume_steering_campaign(
                _Runtime(root, bad_ancestor=("checkpoint-RHC-TEST", "head-current"))
            )
        self.assertEqual("HOLD_NO_VALID_STEERING_CAMPAIGN", result["status"])
        self.assertEqual("CHECKPOINT_ANCESTRY_HOLD", result["diagnostics"][0]["standing"])


if __name__ == "__main__":
    unittest.main()
