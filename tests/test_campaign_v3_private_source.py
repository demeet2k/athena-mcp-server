from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.campaign_v3_ledger import PULSE_ARTIFACT
from athena_mcp.campaign_v3_private_source import (
    SOURCE_ARTIFACT,
    bind_private_source_branch_to_loop,
    cold_resume_private_campaign_v3,
    compile_private_source_identity,
    start_private_source_bound_campaign_v3,
    validate_private_payload,
    validate_private_source_identity,
)
from athena_mcp.git_backend import GitBackend
from athena_mcp.prompt_runtime import PromptRuntime
from athena_mcp.rehydration_campaign import RehydrationCampaignRuntime
from athena_mcp.rehydration_loop import RehydrationLoopRuntime

SECRET = "PRIVATE-ACTION::do-not-persist::b6d2dbf9-75ae-4b49-ae33-a19bcfba7e7c"
PRIVATE_REF = "athena-private-ledger/pulse-1/step-0001"


def _sha(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _run(root: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True)
    if p.returncode:
        raise AssertionError(p.stderr or p.stdout)
    return p.stdout.strip()


def _write(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _fixture(base: Path) -> tuple[Path, RehydrationCampaignRuntime, RehydrationLoopRuntime]:
    root = base / "brain"
    root.mkdir()
    _run(root, "init")
    _run(root, "config", "user.name", "private-source-test")
    _run(root, "config", "user.email", "private-source-test@example.invalid")
    _write(
        root,
        "prompts/PROMPT.manifest.json",
        json.dumps(
            {
                "artifact": "ATHENA.PROMPT.RUNTIME.V1",
                "authority_ceiling": "below external authority",
                "active_state": "prompts/state/ACTIVE.json",
                "policy": "policies/PROMPT_RUNTIME.md",
                "default_profile": "BUILD",
                "profiles": {"BUILD": ["core"], "MAXDEV": ["core"]},
                "modules": {
                    "core": {
                        "path": "prompts/ORCHESTRATION_CORE.md",
                        "order": 0,
                        "mandatory": True,
                        "selectors": [],
                        "depends_on": [],
                    }
                },
            },
            sort_keys=True,
        )
        + "\n",
    )
    _write(
        root,
        "prompts/state/ACTIVE.json",
        json.dumps(
            {
                "artifact": "ATHENA.PROMPT.STATE.ACTIVE.V1",
                "status": "ACTIVE",
                "profile": "BUILD",
                "enabled_modules": ["core"],
                "active_scoped_overlays": [],
                "revision": 1,
            },
            sort_keys=True,
        )
        + "\n",
    )
    _write(root, "policies/PROMPT_RUNTIME.md", "# POLICY\nNo private payload persistence.\n")
    _write(root, "prompts/ORCHESTRATION_CORE.md", "# CORE\nBounded private-source acceptance only.\n")
    _run(root, "add", ".")
    _run(root, "commit", "-m", "fixture")
    git = GitBackend(root)
    prompt = PromptRuntime(git)
    loop = RehydrationLoopRuntime(git, prompt)
    campaign = RehydrationCampaignRuntime(git, prompt, loop)
    return root, campaign, loop


def _pulse(head: str) -> dict:
    value = {
        "artifact": PULSE_ARTIFACT,
        "ledger_digest": "a" * 64,
        "source_issue": 177,
        "verification_issue": 185,
        "pulse_index": 1,
        "step_start": 1,
        "step_end": 10,
        "historical_horizon_coverage": {"I": 4, "M": 3, "L": 3},
        "current_status_counts": {
            "I": {"SATISFIED": 0, "SUPERSEDED": 0, "RESIDUAL": 1, "HOLD": 0},
            "M": {"SATISFIED": 0, "SUPERSEDED": 0, "RESIDUAL": 0, "HOLD": 0},
            "L": {"SATISFIED": 0, "SUPERSEDED": 0, "RESIDUAL": 0, "HOLD": 0},
        },
        "actions": [
            {
                "step": 1,
                "horizon": "I",
                "text": SECRET,
                "current_state": "RESIDUAL",
                "history_preserved": True,
            }
        ],
        "residual_steps": [1],
        "hold_steps": [],
        "current_coordinates": {"git_head": head, "shared_fresh": True, "frontier_digest": "f" * 64},
        "operational_basis_status": "PASS",
        "operational_basis_digest": "b" * 64,
        "execution_authorized": False,
        "authority_resolution_required": True,
        "holds": [],
        "must_reseed_from_then_current_state": False,
        "mission_complete_claim_allowed": False,
        "laws": [
            "HISTORICAL_ACTION != CURRENT_READY_WORK",
            "SATISFIED/SUPERSEDED != ERASED_HISTORY",
            "OPERATIONAL_BASIS != EXECUTION_AUTHORITY",
            "BOUNDED_CYCLE_COMPLETE != MISSION_COMPLETE",
        ],
    }
    value["pulse_digest"] = _sha(value)
    return value


class CampaignV3PrivateSourceTests(unittest.TestCase):
    def _runtime(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        return _fixture(Path(td.name))

    def assert_secret_absent_from_git(self, root: Path) -> None:
        log = _run(root, "log", "-p", "--all")
        self.assertNotIn(SECRET, log)
        grep = subprocess.run(
            ["git", "-C", str(root), "grep", "-n", SECRET, "HEAD", "--", "."],
            text=True,
            capture_output=True,
        )
        self.assertNotEqual(grep.returncode, 0, grep.stdout)
        self.assertNotIn(SECRET, grep.stdout + grep.stderr)

    def test_compile_identity_contains_digest_not_private_text(self):
        root, _, _ = self._runtime()
        pulse = _pulse(_run(root, "rev-parse", "HEAD"))
        compiled = compile_private_source_identity(
            pulse,
            1,
            private_ref=PRIVATE_REF,
            expected_git_head=pulse["current_coordinates"]["git_head"],
        )
        self.assertEqual(compiled["status"], "PRIVATE_SOURCE_IDENTITY_COMPILED")
        source = compiled["source"]
        self.assertEqual(source["artifact"], SOURCE_ARTIFACT)
        self.assertEqual(source["private_payload_digest"], hashlib.sha256(SECRET.encode()).hexdigest())
        self.assertEqual(validate_private_source_identity(source), [])
        encoded = json.dumps(compiled, sort_keys=True)
        self.assertNotIn(SECRET, encoded)
        for forbidden in ("text", "action_text", "private_payload", "payload", "body"):
            self.assertNotIn(forbidden, source)
        self.assertFalse(source["execution_authority"])
        self.assertFalse(compiled["execution_authority"])

    def test_payload_match_returns_attestation_only_and_mismatch_is_hold(self):
        root, _, _ = self._runtime()
        pulse = _pulse(_run(root, "rev-parse", "HEAD"))
        source = compile_private_source_identity(
            pulse,
            1,
            private_ref=PRIVATE_REF,
            expected_git_head=pulse["current_coordinates"]["git_head"],
        )["source"]
        good = validate_private_payload(source, SECRET)
        self.assertEqual(good["status"], "PRIVATE_PAYLOAD_VALIDATED")
        self.assertTrue(good["payload_attestation"]["validated"])
        self.assertNotIn(SECRET, json.dumps(good, sort_keys=True))
        bad = validate_private_payload(source, SECRET + "-wrong")
        self.assertEqual(bad["status"], "HOLD_PRIVATE_PAYLOAD_MISMATCH")
        self.assertFalse(bad["payload_attestation"]["validated"])
        self.assertFalse(bad["execution_authority"])
        self.assertNotIn(SECRET, json.dumps(bad, sort_keys=True))

    def test_actual_campaign_start_and_cold_resume_persist_no_plaintext(self):
        root, campaign, _ = self._runtime()
        head = _run(root, "rev-parse", "HEAD")
        started = start_private_source_bound_campaign_v3(
            campaign,
            pulse=_pulse(head),
            residual_step=1,
            private_ref=PRIVATE_REF,
            expected_git_head=head,
            actor="privacy-test",
            shared_remote_mode="DISABLED",
        )
        self.assertEqual(started["status"], "STARTED_PRIVATE_SOURCE_BOUND")
        self.assertNotIn(SECRET, json.dumps(started, sort_keys=True))
        self.assert_secret_absent_from_git(root)
        resumed = cold_resume_private_campaign_v3(campaign, shared_remote_mode="DISABLED")
        self.assertEqual(resumed["status"], "PRIVATE_CAMPAIGN_RESUMED")
        self.assertEqual(resumed["campaign_id"], started["campaign_id"])
        self.assertEqual(resumed["branch_id"], started["branch_id"])
        self.assertEqual(resumed["source_digest"], started["source"]["source_digest"])
        self.assertEqual(resumed["next"], "VALIDATE_TRANSIENT_PRIVATE_PAYLOAD_AND_BIND_LOOP")
        self.assertNotIn(SECRET, json.dumps(resumed, sort_keys=True))
        self.assert_secret_absent_from_git(root)

    def test_mismatched_payload_refuses_before_claim_or_loop_write(self):
        root, campaign, loop = self._runtime()
        head = _run(root, "rev-parse", "HEAD")
        started = start_private_source_bound_campaign_v3(
            campaign,
            pulse=_pulse(head),
            residual_step=1,
            private_ref=PRIVATE_REF,
            expected_git_head=head,
            actor="privacy-test",
            shared_remote_mode="DISABLED",
        )
        before = _run(root, "rev-parse", "HEAD")
        result = bind_private_source_branch_to_loop(
            campaign,
            loop,
            campaign_id=started["campaign_id"],
            branch_id=started["branch_id"],
            expected_state_digest=started["state_digest"],
            expected_checkpoint_head=started["checkpoint_head"],
            private_payload=SECRET + "-wrong",
            agent="privacy-worker",
            actor="privacy-test",
            shared_remote_mode="DISABLED",
        )
        self.assertEqual(result["status"], "HOLD_PRIVATE_PAYLOAD_MISMATCH")
        self.assertEqual(_run(root, "rev-parse", "HEAD"), before)
        self.assert_secret_absent_from_git(root)

    def test_matching_payload_binds_real_loop_but_plaintext_never_enters_git_or_result(self):
        root, campaign, loop = self._runtime()
        head = _run(root, "rev-parse", "HEAD")
        started = start_private_source_bound_campaign_v3(
            campaign,
            pulse=_pulse(head),
            residual_step=1,
            private_ref=PRIVATE_REF,
            expected_git_head=head,
            actor="privacy-test",
            shared_remote_mode="DISABLED",
        )
        bound = bind_private_source_branch_to_loop(
            campaign,
            loop,
            campaign_id=started["campaign_id"],
            branch_id=started["branch_id"],
            expected_state_digest=started["state_digest"],
            expected_checkpoint_head=started["checkpoint_head"],
            private_payload=SECRET,
            agent="privacy-worker",
            actor="privacy-test",
            shared_remote_mode="DISABLED",
        )
        self.assertEqual(bound["status"], "PRIVATE_SOURCE_LOOP_BOUND")
        self.assertTrue(bound["payload_attestation"]["validated"])
        self.assertEqual(bound["standing"], "OPAQUE_PRIVATE_SOURCE_BOUND_TO_LOOP_NOT_EXECUTED")
        self.assertFalse(bound["execution_authority"])
        self.assertFalse(bound["work_executed"])
        self.assertNotIn(SECRET, json.dumps(bound, sort_keys=True))
        resumed = cold_resume_private_campaign_v3(campaign, shared_remote_mode="DISABLED")
        self.assertEqual(resumed["status"], "PRIVATE_CAMPAIGN_RESUMED")
        self.assertEqual(resumed["next"], "FRESH_RESUME_BOUND_LOOP_BEFORE_PRIVATE_WORK")
        self.assertEqual((resumed["loop_binding"] or {}).get("loop_id"), bound["loop_id"])
        self.assertNotIn(SECRET, json.dumps(resumed, sort_keys=True))
        self.assert_secret_absent_from_git(root)

    def test_tampered_source_digest_and_forbidden_plaintext_field_fail_closed(self):
        root, _, _ = self._runtime()
        pulse = _pulse(_run(root, "rev-parse", "HEAD"))
        source = compile_private_source_identity(
            pulse,
            1,
            private_ref=PRIVATE_REF,
            expected_git_head=pulse["current_coordinates"]["git_head"],
        )["source"]
        tampered = dict(source)
        tampered["step"] = 2
        self.assertIn("SOURCE_DIGEST_INVALID", validate_private_source_identity(tampered))
        leaked = dict(source)
        leaked["text"] = SECRET
        leaked["source_digest"] = _sha({key: value for key, value in leaked.items() if key != "source_digest"})
        errors = validate_private_source_identity(leaked)
        self.assertTrue(any(error.startswith("PLAINTEXT_PAYLOAD_FIELD_FORBIDDEN") for error in errors))


if __name__ == "__main__":
    unittest.main()
