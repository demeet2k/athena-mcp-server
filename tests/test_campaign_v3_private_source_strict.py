from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.campaign_v3_ledger import PULSE_ARTIFACT
from athena_mcp.campaign_v3_private_source_strict import (
    bind_strict_private_source_branch_to_loop,
    cold_resume_strict_private_campaign_v3,
    compile_strict_private_source_identity,
    is_strict_private_ref,
    opaque_private_ref,
    start_strict_private_source_bound_campaign_v3,
)
from athena_mcp.git_backend import GitBackend
from athena_mcp.prompt_runtime import PromptRuntime
from athena_mcp.rehydration_campaign import RehydrationCampaignRuntime
from athena_mcp.rehydration_loop import RehydrationLoopRuntime

SECRET = "STRICT-PRIVATE-ACTION::never-persist::a74d55fa"
LOCATOR_TEXT = "demeet2k/Athena#177/private-comment/step-1"
LOCATOR_DIGEST = hashlib.sha256(LOCATOR_TEXT.encode()).hexdigest()


def _sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _git(root: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True)
    if p.returncode:
        raise AssertionError(p.stderr or p.stdout)
    return p.stdout.strip()


def _fixture(base: Path):
    root = base / "brain"; root.mkdir()
    _git(root, "init"); _git(root, "config", "user.name", "strict-test"); _git(root, "config", "user.email", "x@example.invalid")
    files = {
        "prompts/PROMPT.manifest.json": {"artifact":"ATHENA.PROMPT.RUNTIME.V1","authority_ceiling":"below external authority","active_state":"prompts/state/ACTIVE.json","policy":"policies/PROMPT_RUNTIME.md","default_profile":"BUILD","profiles":{"BUILD":["core"]},"modules":{"core":{"path":"prompts/ORCHESTRATION_CORE.md","order":0,"mandatory":True,"selectors":[],"depends_on":[]}}},
        "prompts/state/ACTIVE.json": {"artifact":"ATHENA.PROMPT.STATE.ACTIVE.V1","status":"ACTIVE","profile":"BUILD","enabled_modules":["core"],"active_scoped_overlays":[],"revision":1},
    }
    for rel, val in files.items():
        path=root/rel; path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(val,sort_keys=True)+"\n")
    for rel, text in {"policies/PROMPT_RUNTIME.md":"POLICY\n","prompts/ORCHESTRATION_CORE.md":"CORE\n"}.items():
        path=root/rel; path.parent.mkdir(parents=True, exist_ok=True); path.write_text(text)
    _git(root,"add","."); _git(root,"commit","-m","fixture")
    git=GitBackend(root); prompt=PromptRuntime(git); loop=RehydrationLoopRuntime(git,prompt); campaign=RehydrationCampaignRuntime(git,prompt,loop)
    return root,campaign,loop


def _pulse(head: str):
    value={"artifact":PULSE_ARTIFACT,"ledger_digest":"a"*64,"source_issue":177,"verification_issue":185,"pulse_index":1,"step_start":1,"step_end":10,"historical_horizon_coverage":{"I":1,"M":0,"L":0},"current_status_counts":{"I":{"SATISFIED":0,"SUPERSEDED":0,"RESIDUAL":1,"HOLD":0},"M":{"SATISFIED":0,"SUPERSEDED":0,"RESIDUAL":0,"HOLD":0},"L":{"SATISFIED":0,"SUPERSEDED":0,"RESIDUAL":0,"HOLD":0}},"actions":[{"step":1,"horizon":"I","text":SECRET,"current_state":"RESIDUAL","history_preserved":True}],"residual_steps":[1],"hold_steps":[],"current_coordinates":{"git_head":head,"shared_fresh":True},"operational_basis_status":"PASS","operational_basis_digest":"b"*64,"execution_authorized":False,"authority_resolution_required":True,"holds":[],"must_reseed_from_then_current_state":False,"mission_complete_claim_allowed":False,"laws":[]}
    value["pulse_digest"]=_sha(value); return value


class StrictPrivateSourceTests(unittest.TestCase):
    def runtime(self):
        td=tempfile.TemporaryDirectory(); self.addCleanup(td.cleanup); return _fixture(Path(td.name))

    def assert_absent(self, root: Path):
        history=_git(root,"log","-p","--all")
        self.assertNotIn(SECRET,history); self.assertNotIn(LOCATOR_TEXT,history)

    def test_only_digest_locator_is_accepted(self):
        self.assertEqual(opaque_private_ref(LOCATOR_DIGEST),"opaque:"+LOCATOR_DIGEST)
        self.assertTrue(is_strict_private_ref("opaque:"+LOCATOR_DIGEST))
        for invalid in ("",LOCATOR_TEXT,"A"*64,"0"*63,"opaque:"+LOCATOR_TEXT):
            if invalid.startswith("opaque:"):
                self.assertFalse(is_strict_private_ref(invalid))
            else:
                with self.assertRaises(ValueError): opaque_private_ref(invalid)

    def test_compile_rejects_free_form_and_persists_only_strict_ref(self):
        root,_,_=self.runtime(); head=_git(root,"rev-parse","HEAD"); pulse=_pulse(head)
        bad=compile_strict_private_source_identity(pulse,1,private_locator_digest=LOCATOR_TEXT,expected_git_head=head)
        self.assertEqual(bad["status"],"HOLD_INVALID_PRIVATE_LOCATOR_DIGEST")
        good=compile_strict_private_source_identity(pulse,1,private_locator_digest=LOCATOR_DIGEST,expected_git_head=head)
        self.assertEqual(good["status"],"STRICT_PRIVATE_SOURCE_IDENTITY_COMPILED")
        self.assertEqual(good["source"]["private_ref"],"opaque:"+LOCATOR_DIGEST)
        rendered=json.dumps(good,sort_keys=True)
        self.assertNotIn(SECRET,rendered); self.assertNotIn(LOCATOR_TEXT,rendered)

    def test_strict_start_bind_and_cold_resume_never_persist_payload_or_locator_text(self):
        root,campaign,loop=self.runtime(); head=_git(root,"rev-parse","HEAD")
        started=start_strict_private_source_bound_campaign_v3(campaign,pulse=_pulse(head),residual_step=1,private_locator_digest=LOCATOR_DIGEST,expected_git_head=head,actor="strict-test",shared_remote_mode="DISABLED")
        self.assertEqual(started["status"],"STARTED_PRIVATE_SOURCE_BOUND"); self.assertTrue(started["strict_entrypoint"])
        self.assert_absent(root)
        resumed=cold_resume_strict_private_campaign_v3(campaign,shared_remote_mode="DISABLED")
        self.assertEqual(resumed["status"],"PRIVATE_CAMPAIGN_RESUMED"); self.assertTrue(resumed["strict_entrypoint"])
        bound=bind_strict_private_source_branch_to_loop(campaign,loop,campaign_id=started["campaign_id"],branch_id=started["branch_id"],expected_state_digest=started["state_digest"],expected_checkpoint_head=started["checkpoint_head"],private_payload=SECRET,agent="strict-worker",actor="strict-test",shared_remote_mode="DISABLED")
        self.assertEqual(bound["status"],"PRIVATE_SOURCE_LOOP_BOUND"); self.assertTrue(bound["strict_entrypoint"])
        self.assertFalse(bound["execution_authority"]); self.assertFalse(bound["work_executed"])
        self.assertNotIn(SECRET,json.dumps(bound,sort_keys=True)); self.assertNotIn(LOCATOR_TEXT,json.dumps(bound,sort_keys=True)); self.assert_absent(root)


if __name__ == "__main__": unittest.main()
