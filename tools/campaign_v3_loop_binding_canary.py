from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from athena_mcp.git_backend import GitBackend
from athena_mcp.prompt_runtime import PromptRuntime
from athena_mcp.rehydration_campaign import RehydrationCampaignRuntime
from athena_mcp.rehydration_loop import RehydrationLoopRuntime

REPO = os.environ.get("GITHUB_REPOSITORY", "demeet2k/athena-mcp-server")
TARGET_BRANCH = os.environ["TARGET_BRANCH"]
TARGET_SEED_HEAD = os.environ["TARGET_SEED_HEAD"]
CANDIDATE_HEAD = os.environ["CANDIDATE_HEAD"]
TOKEN = os.environ.get("GITHUB_TOKEN", "")
WITNESS_PATH = Path(os.environ.get("WITNESS_PATH", "campaign-v3-loop-binding-witness.json"))
MATERIAL_PATH = "acceptance/campaign-v3-step4-material.json"


def scrub(value):
    if isinstance(value, str):
        return value.replace(TOKEN, "<REDACTED>") if TOKEN else value
    if isinstance(value, dict):
        return {str(k): scrub(v) for k, v in value.items()}
    if isinstance(value, list):
        return [scrub(v) for v in value]
    return value


def run(cmd: list[str], *, cwd: Path | None = None) -> str:
    p = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if p.returncode:
        raise RuntimeError(scrub((p.stderr or p.stdout or f"command failed: {cmd}")[-5000:]))
    return p.stdout.strip()


def write_witness(payload: dict, passed: bool) -> None:
    out = {
        "schema_version": "ATHENA.CAMPAIGN.V3.LOOP_BINDING.ACCEPTANCE.V1",
        "result": "PASS" if passed else "FAIL",
        "candidate_head": CANDIDATE_HEAD,
        "target_branch": TARGET_BRANCH,
        "target_seed_head": TARGET_SEED_HEAD,
        "source_standing": "SYNTHETIC_PRIVACY_SAFE_MECHANISM_WITNESS",
        "private_ledger_consumed": False,
        "campaign_success": "HOLD",
        "production_authority": "HOLD",
        "laws": [
            "SYNTHETIC_LOOP_BINDING_WITNESS != VERIFIED_LEDGER_PULSE",
            "PRIVATE_SOURCE != PUBLIC_FIXTURE",
            "CAMPAIGN_BRANCH != BACKGROUND_WORKER",
            "LOOP_START != BACKGROUND_EXECUTION",
            "GIT_COMMIT != OBSERVED_SUCCESS_WITHOUT_RECEIPT",
            "PROMOTION_QUALIFIED != CAMPAIGN_SUCCESS",
        ],
        **scrub(payload),
    }
    rendered = json.dumps(out, sort_keys=True, indent=2)
    if TOKEN and TOKEN in rendered:
        raise RuntimeError("token leak detected in rendered witness")
    WITNESS_PATH.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


def clone_target(base: Path) -> Path:
    root = base / "target"
    run([
        "git", "clone", "--quiet", "--branch", TARGET_BRANCH, "--single-branch",
        f"https://github.com/{REPO}.git", str(root),
    ])
    run(["git", "config", "user.name", "athena-campaign-v3-canary"], cwd=root)
    run(["git", "config", "user.email", "athena-canary@example.invalid"], cwd=root)
    auth_url = f"https://x-access-token:{TOKEN}@github.com/{REPO}.git"
    run(["git", "remote", "set-url", "origin", auth_url], cwd=root)
    return root


def assert_remote(result: dict, label: str) -> None:
    if result.get("durable_return") is not True:
        raise AssertionError(f"{label}: durable_return is not true")
    publish = result.get("remote_publish") or {}
    if publish.get("shared_frontier_verified") is not True:
        raise AssertionError(f"{label}: shared remote publication not verified")


def main() -> None:
    if not TOKEN:
        write_witness({"reason": "GITHUB_TOKEN unavailable"}, False)
        raise SystemExit(1)

    try:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = clone_target(base)
            initial_head = run(["git", "rev-parse", "HEAD"], cwd=root)
            if initial_head != TARGET_SEED_HEAD:
                raise AssertionError(f"target moved before acceptance start: {initial_head}")

            git = GitBackend(root)
            prompt = PromptRuntime(git)
            loop = RehydrationLoopRuntime(git, prompt)
            campaign = RehydrationCampaignRuntime(git, prompt, loop)

            campaign_start = campaign.start(
                goal="Observe one privacy-safe Campaign V3 branch binding to an explicit V1 loop",
                expected_git_head=git.head(),
                initial_tasks=["Commit one bounded synthetic material witness and return a successor"],
                actor="campaign-v3-canary",
                max_width=1,
                max_depth=2,
                max_branches=2,
                lease_steps=4,
                shared_remote_mode="REQUIRED",
                remote="origin",
            )
            assert_remote(campaign_start, "campaign_start")
            if campaign_start.get("status") != "ACTIVE" or len(campaign_start.get("frontier") or []) != 1:
                raise AssertionError("campaign did not start with one active branch")
            campaign_id = campaign_start["campaign_id"]
            branch_id = campaign_start["frontier"][0]["branch_id"]

            campaign_claim = campaign.claim(
                campaign_id=campaign_id,
                expected_state_digest=campaign_start["state_digest"],
                expected_checkpoint_head=campaign_start["checkpoint_head"],
                branch_id=branch_id,
                agent="cold-loop-worker",
                actor="campaign-v3-canary",
                shared_remote_mode="REQUIRED",
                remote="origin",
            )
            assert_remote(campaign_claim, "campaign_claim")
            claimed = next(row for row in campaign_claim["frontier"] if row["branch_id"] == branch_id)
            if claimed.get("status") != "CLAIMED" or (claimed.get("claim") or {}).get("agent") != "cold-loop-worker":
                raise AssertionError("campaign logical lease was not observed")

            loop_start = loop.start(
                goal="Produce an observed durable step-4 loop-binding witness",
                expected_git_head=git.head(),
                task="Write one bounded synthetic material witness, verify it, then return a successor",
                actor="cold-loop-worker",
                profile="BUILD",
                source_ref=TARGET_BRANCH,
                remote="origin",
                fetch=True,
                use_frontier=False,
                shared_remote_mode="REQUIRED",
                max_steps=3,
                max_no_progress=2,
                depth_mode="standard",
                required_passes=["reconstruct", "execute", "verify"],
                stop_conditions=["Do not consume or publish private Athena #177/#185 source text"],
            )
            assert_remote(loop_start, "loop_start")
            if loop_start.get("status") != "STARTED":
                raise AssertionError("V1 loop did not start")

            campaign_bind = campaign.bind_loop(
                campaign_id=campaign_id,
                expected_state_digest=campaign_claim["state_digest"],
                expected_checkpoint_head=campaign_claim["checkpoint_head"],
                branch_id=branch_id,
                loop_id=loop_start["loop_id"],
                loop_state_digest=loop_start["state_digest"],
                actor="campaign-v3-canary",
                shared_remote_mode="REQUIRED",
                remote="origin",
            )
            assert_remote(campaign_bind, "campaign_bind")
            bound = next(row for row in campaign_bind["frontier"] if row["branch_id"] == branch_id)
            loop_binding = bound.get("loop") or {}
            if bound.get("status") != "ACTIVE" or loop_binding.get("loop_id") != loop_start["loop_id"]:
                raise AssertionError("campaign branch did not bind the exact V1 loop")
            if loop_binding.get("checkpoint_head") != loop_start["checkpoint_head"]:
                raise AssertionError("campaign loop binding checkpoint mismatch")

            material_file = root / MATERIAL_PATH
            material_file.parent.mkdir(parents=True, exist_ok=True)
            material_payload = {
                "artifact": "ATHENA.CAMPAIGN.V3.STEP4.MATERIAL.WITNESS.V1",
                "observed": True,
                "campaign_id": campaign_id,
                "branch_id": branch_id,
                "loop_id": loop_start["loop_id"],
                "loop_checkpoint_head": loop_start["checkpoint_head"],
                "authority": "HOLD",
                "source_standing": "SYNTHETIC_PRIVACY_SAFE_MECHANISM_WITNESS",
                "law": "MATERIAL_COMMIT != VERIFIED_LEDGER_PULSE",
            }
            material_file.write_text(json.dumps(material_payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
            run(["git", "add", MATERIAL_PATH], cwd=root)
            run(["git", "commit", "-m", "record Campaign V3 step-4 material witness"], cwd=root)
            material_head = run(["git", "rev-parse", "HEAD"], cwd=root)
            run(["git", "push", "origin", f"HEAD:refs/heads/{TARGET_BRANCH}"], cwd=root)

            completion = {
                "status": "SUCCEEDED",
                "observed": True,
                "terminal": False,
                "hard_hold": False,
                "summary": "Observed a claimed campaign branch bound to the exact V1 loop; committed and verified an independent synthetic material witness; private ledger source remained untouched.",
                "progress_delta": 1.0,
                "passes": [
                    {"kind": "reconstruct", "summary": "Reconstructed campaign lease, exact loop checkpoint, HOLD authority, and privacy boundary.", "evidence_refs": [campaign_bind["checkpoint_head"]]},
                    {"kind": "execute", "summary": "Committed an independent material witness after loop start and binding.", "evidence_refs": [material_head, MATERIAL_PATH]},
                    {"kind": "verify", "summary": "Required the material path to appear in the V1 receipt and later replayed both loop and campaign chains.", "evidence_refs": [MATERIAL_PATH]},
                ],
                "tests": [
                    {"name": "independent_material_commit", "status": "PASS", "evidence_ref": material_head},
                    {"name": "private_source_not_consumed", "status": "PASS", "evidence_ref": "private_ledger_consumed=false"},
                ],
                "evidence_refs": [campaign_bind["checkpoint_head"], material_head, MATERIAL_PATH],
                "residuals": ["Real verified #177 ledger pulse execution remains a separate private-source acceptance."],
                "next_task": "Rehydrate the then-current campaign state and decide the next lawful pulse without disclosing private source text.",
                "handoff_to": None,
                "self_steer": False,
            }
            loop_advance = loop.advance(
                loop_id=loop_start["loop_id"],
                expected_checkpoint_head=loop_start["checkpoint_head"],
                expected_state_digest=loop_start["state_digest"],
                expected_prompt_digest=loop_start["prompt_digest"],
                completion=completion,
                actor="cold-loop-worker",
                allow_no_git_change=False,
                shared_remote_mode="REQUIRED",
                remote="origin",
            )
            assert_remote(loop_advance, "loop_advance")
            if loop_advance.get("status") != "ACTIVE" or loop_advance.get("terminal") is not False:
                raise AssertionError(f"unexpected loop post-advance status: {loop_advance.get('status')}")
            if MATERIAL_PATH not in (loop_advance.get("material_work_paths") or []):
                raise AssertionError("V1 receipt did not classify the independent material file as work")
            if not loop_advance.get("receipt_digest") or not loop_advance.get("compiled_self_prompt"):
                raise AssertionError("V1 advance did not return receipt + successor prompt")

            campaign_sync = campaign.sync_branch(
                campaign_id=campaign_id,
                expected_state_digest=campaign_bind["state_digest"],
                expected_checkpoint_head=campaign_bind["checkpoint_head"],
                branch_id=branch_id,
                actor="campaign-v3-canary",
                shared_remote_mode="REQUIRED",
                remote="origin",
            )
            assert_remote(campaign_sync, "campaign_sync")
            if campaign_sync.get("branch_status") != "ACTIVE" or campaign_sync.get("loop_status") != "ACTIVE":
                raise AssertionError("campaign sync did not observe the active advanced loop")

            loop_verify = loop.verify(loop_start["loop_id"], shared_remote_mode="REQUIRED", remote="origin")
            campaign_verify = campaign.verify(campaign_id)
            campaign_resume = campaign.resume(campaign_id)
            if loop_verify.get("status") != "PASS":
                raise AssertionError(f"loop verify failed: {loop_verify.get('failures')}")
            if campaign_verify.get("status") != "PASS":
                raise AssertionError(f"campaign verify failed: {campaign_verify.get('failures')}")
            if campaign_resume.get("status") != "RESUMED":
                raise AssertionError("campaign resume integrity hold")
            resumed = next(row for row in campaign_resume["branches"] if row["branch_id"] == branch_id)
            if (resumed.get("loop") or {}).get("loop_id") != loop_start["loop_id"]:
                raise AssertionError("resumed campaign lost loop identity")
            if resumed.get("completion_summary") != completion["summary"]:
                raise AssertionError("campaign sync did not carry the observed loop completion")

            final_head = run(["git", "rev-parse", "HEAD"], cwd=root)
            write_witness({
                "campaign": {
                    "campaign_id": campaign_id,
                    "branch_id": branch_id,
                    "lease_agent": "cold-loop-worker",
                    "start_checkpoint": campaign_start["checkpoint_head"],
                    "claim_checkpoint": campaign_claim["checkpoint_head"],
                    "bind_checkpoint": campaign_bind["checkpoint_head"],
                    "sync_checkpoint": campaign_sync["checkpoint_head"],
                    "verify_status": campaign_verify["status"],
                    "resume_status": campaign_resume["status"],
                    "branch_status": resumed.get("status"),
                },
                "loop": {
                    "loop_id": loop_start["loop_id"],
                    "start_checkpoint": loop_start["checkpoint_head"],
                    "bound_checkpoint": loop_binding.get("checkpoint_head"),
                    "advance_checkpoint": loop_advance["checkpoint_head"],
                    "step_index": loop_advance["step_index"],
                    "receipt_path": loop_advance["receipt_path"],
                    "receipt_digest": loop_advance["receipt_digest"],
                    "material_work_paths": loop_advance["material_work_paths"],
                    "verify_status": loop_verify["status"],
                    "shared_frontier_verified": loop_verify.get("shared_frontier_verified"),
                    "successor_prompt_digest": loop_advance["prompt_digest"],
                    "successor_task": completion["next_task"],
                },
                "material": {
                    "path": MATERIAL_PATH,
                    "commit_head": material_head,
                    "observed_in_receipt": MATERIAL_PATH in loop_advance["material_work_paths"],
                },
                "final_target_head": final_head,
                "durable_remote_publication": True,
            }, True)
    except Exception as exc:
        write_witness({"reason": f"{type(exc).__name__}: {scrub(str(exc))}"}, False)
        raise


if __name__ == "__main__":
    main()
