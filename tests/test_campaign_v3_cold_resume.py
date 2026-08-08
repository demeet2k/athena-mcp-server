from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from athena_mcp.campaign_v3_cold_resume import (
    SOURCE_ARTIFACT,
    SOURCE_KIND,
    _source_digest,
    cold_resume_campaign_v3,
    start_source_bound_campaign_v3,
)
from athena_mcp.campaign_v3_ledger import PULSE_ARTIFACT
from athena_mcp.rehydration_campaign import ARTIFACT as CAMPAIGN_ARTIFACT, _campaign_state_digest


def _sha(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _pulse(head="H0", *, shared_fresh=True) -> dict:
    value = {
        "artifact": PULSE_ARTIFACT,
        "ledger_digest": "ledger",
        "source_issue": 177,
        "verification_issue": 185,
        "pulse_index": 7,
        "step_start": 61,
        "step_end": 70,
        "historical_horizon_coverage": {"I": 4, "M": 3, "L": 3},
        "current_status_counts": {},
        "actions": [{
            "step": 61,
            "horizon": "I",
            "text": "consume current sibling delta",
            "current_state": "RESIDUAL",
            "history_preserved": True,
        }],
        "residual_steps": [61],
        "hold_steps": [],
        "current_coordinates": {"git_head": head, "shared_fresh": shared_fresh},
        "operational_basis_status": "PASS",
        "operational_basis_digest": "basis",
        "execution_authorized": False,
        "authority_resolution_required": True,
        "holds": [],
        "must_reseed_from_then_current_state": False,
        "mission_complete_claim_allowed": False,
        "laws": [],
    }
    value["pulse_digest"] = _sha(value)
    return value


class _Git:
    def __init__(self, head="H0"):
        self.value = head

    def head(self):
        return self.value


class _StartRuntime:
    def __init__(self, *, fail_bind=False):
        self.git = _Git()
        self.fail_bind = fail_bind
        self.start_calls = []
        self.mutate_calls = []
        self.state = None
        self.campaign_id = "RHC-test"

    def start(self, **kwargs):
        self.start_calls.append(kwargs)
        if kwargs["expected_git_head"] != self.git.head():
            raise ValueError("stale start")
        self.git.value = "H1"
        branch = {
            "branch_id": "CB-1",
            "parent_branch_id": None,
            "depth": 0,
            "task": kwargs["initial_tasks"][0],
            "status": "OPEN",
            "candidate_id": None,
            "candidate_metrics": None,
            "routing_score": None,
            "source": None,
            "claim": None,
            "loop": None,
            "evidence_refs": [],
            "completion_summary": None,
            "successor_baton": None,
        }
        self.state = {
            "artifact": CAMPAIGN_ARTIFACT,
            "campaign_id": self.campaign_id,
            "status": "ACTIVE",
            "logical_clock": 0,
            "budget": {"max_width": 4, "max_depth": 8, "max_branches": 32, "lease_steps": 4},
            "branches": {"CB-1": branch},
            "reconciliations": [],
            "chain_digest": "chain0",
        }
        self.state["state_digest"] = _campaign_state_digest(self.state)
        return {
            "status": "ACTIVE",
            "campaign_id": self.campaign_id,
            "state_digest": self.state["state_digest"],
            "checkpoint_head": "H1",
        }

    def _read_state(self, campaign_id):
        if campaign_id != self.campaign_id or self.state is None:
            raise ValueError("campaign not found")
        return json.loads(json.dumps(self.state)), {"state": "state.json"}

    def _mutate(self, **kwargs):
        self.mutate_calls.append(kwargs)
        if self.fail_bind:
            raise ValueError("source bind failed")
        self.assert_exact(kwargs)
        new_state = kwargs["mutator"](json.loads(json.dumps(self.state)))
        new_state["logical_clock"] = int(new_state.get("logical_clock", 0)) + 1
        new_state["state_digest"] = _campaign_state_digest(new_state)
        self.state = new_state
        self.git.value = "H2"
        return {
            "status": "ACTIVE",
            "state_digest": new_state["state_digest"],
            "checkpoint_head": "H2",
        }

    def assert_exact(self, kwargs):
        if kwargs["campaign_id"] != self.campaign_id:
            raise AssertionError("wrong campaign")
        if kwargs["expected_state_digest"] != self.state["state_digest"]:
            raise AssertionError("wrong source state digest")
        if kwargs["expected_checkpoint_head"] != "H1":
            raise AssertionError("wrong source checkpoint")
        if kwargs["event_type"] != "CAMPAIGN_V3_SOURCE_BOUND":
            raise AssertionError("wrong event type")


class _ColdRuntime:
    def __init__(self, root: Path, *, shared=True, verify_status="PASS", ancestor=True):
        self.root = root
        self.git = _Git("CURRENT")
        self.shared = shared
        self.verify_status = verify_status
        self.ancestor = ancestor
        self.loop_runtime = object()

    def _remote_mode(self, value):
        return str(value or "REQUIRED").upper()

    def _sync(self, mode, remote):
        return {"status": "SYNCED" if self.shared else "HOLD", "shared_frontier_verified": self.shared}

    def _safe_rel(self, rel):
        return self.root / rel

    def _read_state(self, campaign_id):
        path = self.root / "prompts" / "rehydration_campaigns" / campaign_id / "state.json"
        state = json.loads(path.read_text())
        return state, {"state": f"prompts/rehydration_campaigns/{campaign_id}/state.json"}

    def _path_last_commit(self, rel):
        return "CP"

    def _is_ancestor(self, older, newer):
        return self.ancestor and older == "CP" and newer == "CURRENT"

    def verify(self, campaign_id):
        return {"status": self.verify_status}


def _source(*, step=61, text="consume current sibling delta") -> dict:
    value = {
        "artifact": SOURCE_ARTIFACT,
        "kind": SOURCE_KIND,
        "ledger_digest": "ledger",
        "pulse_digest": "pulse",
        "pulse_index": 7,
        "step": step,
        "horizon": "I",
        "text": text,
        "source_issue": 177,
        "verification_issue": 185,
        "compiled_at_head": "H0",
        "operational_basis_digest": "basis",
        "current_coordinates": {"git_head": "H0", "shared_fresh": True},
    }
    value["source_digest"] = _source_digest(value)
    return value


def _write_campaign(root: Path, campaign_id="RHC-A", *, source=None, status="OPEN", loop=None, tamper_source=False):
    base = root / "prompts" / "rehydration_campaigns" / campaign_id
    base.mkdir(parents=True, exist_ok=True)
    source = dict(source or _source())
    if tamper_source:
        source["text"] = "tampered"
    state = {
        "artifact": CAMPAIGN_ARTIFACT,
        "campaign_id": campaign_id,
        "status": "ACTIVE",
        "goal": "g",
        "logical_clock": 1,
        "budget": {"max_width": 4, "max_depth": 8, "max_branches": 32, "lease_steps": 4},
        "branches": {
            "CB-1": {
                "branch_id": "CB-1",
                "parent_branch_id": None,
                "depth": 0,
                "task": source.get("text"),
                "status": status,
                "source": source,
                "claim": None,
                "loop": loop,
                "evidence_refs": [],
                "completion_summary": None,
                "successor_baton": None,
            }
        },
        "reconciliations": [],
        "chain_digest": "chain",
    }
    state["state_digest"] = _campaign_state_digest(state)
    (base / "state.json").write_text(json.dumps(state), encoding="utf-8")
    return state


class CampaignV3ColdResumeTests(unittest.TestCase):
    def test_start_source_bound_saga_persists_exact_source_identity(self):
        runtime = _StartRuntime()
        result = start_source_bound_campaign_v3(
            runtime,
            pulse=_pulse(),
            residual_step=61,
            expected_git_head="H0",
            shared_remote_mode="DISABLED",
        )
        self.assertEqual(result["status"], "STARTED_SOURCE_BOUND")
        self.assertEqual(result["standing"], "DURABLE_SOURCE_BOUND_NOT_CLAIMED")
        self.assertEqual(result["start_checkpoint_head"], "H1")
        self.assertEqual(result["checkpoint_head"], "H2")
        self.assertFalse(result["execution_authority"])
        self.assertFalse(result["work_executed"])
        source = runtime.state["branches"]["CB-1"]["source"]
        self.assertEqual(source["kind"], SOURCE_KIND)
        self.assertEqual(source["step"], 61)
        self.assertEqual(source["text"], "consume current sibling delta")
        self.assertEqual(source["source_digest"], _source_digest(source))
        self.assertEqual(len(runtime.start_calls), 1)
        self.assertEqual(len(runtime.mutate_calls), 1)

    def test_tampered_or_unfresh_pulse_never_starts_campaign(self):
        runtime = _StartRuntime()
        pulse = _pulse()
        pulse["actions"][0]["text"] = "tampered"
        result = start_source_bound_campaign_v3(runtime, pulse=pulse, residual_step=61, expected_git_head="H0")
        self.assertEqual(result["status"], "HOLD_INVALID_START_INPUT")
        self.assertIn("PULSE_DIGEST_INVALID", result["failures"])
        self.assertEqual(runtime.start_calls, [])

        runtime = _StartRuntime()
        result = start_source_bound_campaign_v3(
            runtime,
            pulse=_pulse(shared_fresh=False),
            residual_step=61,
            expected_git_head="H0",
        )
        self.assertEqual(result["status"], "HOLD_INVALID_START_INPUT")
        self.assertIn("SHARED_FRESHNESS_REQUIRED", result["failures"])
        self.assertEqual(runtime.start_calls, [])

    def test_source_bind_failure_preserves_started_campaign_for_recovery(self):
        runtime = _StartRuntime(fail_bind=True)
        result = start_source_bound_campaign_v3(
            runtime,
            pulse=_pulse(),
            residual_step=61,
            expected_git_head="H0",
            shared_remote_mode="DISABLED",
        )
        self.assertEqual(result["status"], "STARTED_SOURCE_UNBOUND_HOLD")
        self.assertEqual(result["campaign_id"], "RHC-test")
        self.assertEqual(result["branch_id"], "CB-1")
        self.assertEqual(result["start_checkpoint_head"], "H1")
        self.assertEqual(len(runtime.start_calls), 1)
        self.assertEqual(runtime.git.head(), "H1")

    def test_cold_resume_absent_namespace_and_shared_hold(self):
        with tempfile.TemporaryDirectory() as tmp:
            runtime = _ColdRuntime(Path(tmp))
            result = cold_resume_campaign_v3(runtime)
            self.assertEqual(result["status"], "HOLD_NO_CAMPAIGN")
            self.assertFalse(result["execution_authority"])

            runtime = _ColdRuntime(Path(tmp), shared=False)
            result = cold_resume_campaign_v3(runtime)
            self.assertEqual(result["status"], "HOLD_SHARED_FRESHNESS")

    def test_cold_resume_discovers_unique_unbound_branch_without_chat_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_campaign(root)
            runtime = _ColdRuntime(root)
            result = cold_resume_campaign_v3(runtime)
            self.assertEqual(result["status"], "DISCOVERED_SOURCE_BOUND_UNBOUND_BRANCH")
            self.assertEqual(result["discovered"]["campaign_id"], "RHC-A")
            self.assertEqual(result["discovered"]["branch_id"], "CB-1")
            self.assertEqual(result["discovered"]["source"]["step"], 61)
            self.assertFalse(result["execution_authority"])

    def test_cold_resume_bound_branch_delegates_exact_discovered_coordinates(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_campaign(root, status="ACTIVE", loop={"loop_id": "LOOP-1", "state_digest": "LD", "checkpoint_head": "LCP"})
            runtime = _ColdRuntime(root)
            with patch("athena_mcp.campaign_v3_cold_resume.fresh_resume_branch") as resume:
                resume.return_value = {"status": "ALIGNED_ACTIVE", "next": "CONTINUE_BOUND_LOOP"}
                result = cold_resume_campaign_v3(runtime)
            self.assertEqual(result["status"], "COLD_RESUME_COMPLETE")
            kwargs = resume.call_args.kwargs
            self.assertEqual(kwargs["campaign_id"], "RHC-A")
            self.assertEqual(kwargs["branch_id"], "CB-1")
            self.assertEqual(kwargs["expected_state_digest"], result["discovered"]["state_digest"])
            self.assertEqual(kwargs["expected_checkpoint_head"], "CP")

    def test_cold_resume_holds_on_campaign_or_branch_ambiguity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_campaign(root, "RHC-A")
            _write_campaign(root, "RHC-B")
            result = cold_resume_campaign_v3(_ColdRuntime(root))
            self.assertEqual(result["status"], "HOLD_AMBIGUOUS_CAMPAIGN")

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state = _write_campaign(root, "RHC-A")
            source2 = _source(step=62, text="another current residual")
            state["branches"]["CB-2"] = {
                **state["branches"]["CB-1"],
                "branch_id": "CB-2",
                "task": source2["text"],
                "source": source2,
            }
            state["state_digest"] = _campaign_state_digest(state)
            (root / "prompts" / "rehydration_campaigns" / "RHC-A" / "state.json").write_text(json.dumps(state))
            result = cold_resume_campaign_v3(_ColdRuntime(root))
            self.assertEqual(result["status"], "HOLD_AMBIGUOUS_BRANCH")

    def test_invalid_source_replay_or_checkpoint_is_not_a_valid_campaign(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_campaign(root, tamper_source=True)
            result = cold_resume_campaign_v3(_ColdRuntime(root))
            self.assertEqual(result["status"], "HOLD_NO_VALID_CAMPAIGN_V3")

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_campaign(root)
            result = cold_resume_campaign_v3(_ColdRuntime(root, verify_status="HOLD"))
            self.assertEqual(result["status"], "HOLD_NO_VALID_CAMPAIGN_V3")

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_campaign(root)
            result = cold_resume_campaign_v3(_ColdRuntime(root, ancestor=False))
            self.assertEqual(result["status"], "HOLD_NO_VALID_CAMPAIGN_V3")


if __name__ == "__main__":
    unittest.main()
