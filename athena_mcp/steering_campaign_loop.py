from __future__ import annotations

from typing import Any, Mapping

ARTIFACT = "ATHENA.STEERING.CAMPAIGN.LOOP.BINDING.V1"
COMPILATION_ARTIFACT = "ATHENA.STEERING.PULSE.COMPILATION.V1"
CANDIDATE_STANDING = "CAMPAIGN_CANDIDATE_NOT_EXECUTION_AUTHORITY"
SUCCESS_STANDING = "BOUND_NOT_EXECUTED"

LAWS = [
    "LOOP_CREATED != WORK_EXECUTED",
    "LOOP_BOUND != CAMPAIGN_PULSE_EXECUTED",
    "REHYDRATION_RESUME = HANDOFF_PACKET_NOT_AUTHORITY",
    "CAMPAIGN_CANDIDATE != EXECUTION_AUTHORITY",
    "BRANCH_ROUTING != AUTHORITY",
    "CAMPAIGN_LOOP_RUNTIME = BIND_LOOP_RUNTIME",
    "NO_REHYDRATION_ADVANCE_IN_LOOP_BINDING",
]


def _hold(kind: str, reason: str, **details: Any) -> dict[str, Any]:
    return {
        "artifact": ARTIFACT,
        "status": "HOLD",
        "standing": "LOOP_BINDING_HOLD",
        "hold_kind": kind,
        "reason": reason,
        "details": details,
        "laws": list(LAWS),
    }


def _candidate(compilation: Mapping[str, Any], candidate_id: str) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    if compilation.get("artifact") != COMPILATION_ARTIFACT:
        return None, _hold("COMPILATION_ARTIFACT", "unsupported pulse compilation artifact")
    if compilation.get("status") != "RESIDUAL_CANDIDATES":
        return None, _hold(
            "COMPILATION_NOT_RESIDUAL",
            "loop binding requires a current residual candidate",
            compilation_status=compilation.get("status"),
        )
    if compilation.get("failures"):
        return None, _hold("COMPILATION_FAILURES", "pulse compilation contains failures")
    if compilation.get("holds"):
        return None, _hold("COMPILATION_HOLDS", "pulse compilation contains unresolved holds")
    rows = [dict(row) for row in compilation.get("candidates") or [] if str(row.get("candidate_id") or "") == candidate_id]
    if len(rows) != 1:
        return None, _hold("CANDIDATE_IDENTITY", "candidate_id must identify exactly one residual candidate", candidate_id=candidate_id)
    candidate = rows[0]
    if candidate.get("standing") != CANDIDATE_STANDING:
        return None, _hold("CANDIDATE_STANDING", "candidate standing does not preserve the execution-authority firewall")
    if not str(candidate.get("task") or "").strip():
        return None, _hold("CANDIDATE_TASK", "residual candidate task is required")
    return candidate, None


def _branch(campaign_resume: Mapping[str, Any], branch_id: str) -> dict[str, Any] | None:
    rows = [dict(row) for row in campaign_resume.get("branches") or [] if str(row.get("branch_id") or "") == branch_id]
    return rows[0] if len(rows) == 1 else None


def bind_candidate_to_v1_loop(
    campaign_runtime: Any,
    loop_runtime: Any,
    *,
    compilation: Mapping[str, Any],
    campaign_id: str,
    branch_id: str,
    candidate_id: str,
    actor: str,
    expected_campaign_state_digest: str,
    expected_campaign_checkpoint_head: str,
    expected_git_head: str,
    profile: str | None = None,
    source_ref: str | None = None,
    remote: str = "origin",
    shared_remote_mode: str = "REQUIRED",
    fetch: bool = True,
    use_frontier: bool = True,
    max_steps: int = 64,
    max_no_progress: int = 3,
    max_prompt_chars: int = 32000,
    depth_mode: str = "deep",
    required_passes: list[str] | None = None,
) -> dict[str, Any]:
    """Bind one evidence-qualified Campaign V3 residual branch to a fresh V1 loop.

    This transaction deliberately stops before ``athena_rehydration_advance``.
    Starting and binding a loop creates durable coordination/handoff state only;
    it is not evidence that the residual task was executed.
    """

    candidate, candidate_hold = _candidate(compilation, candidate_id)
    if candidate_hold is not None:
        return candidate_hold
    assert candidate is not None

    # RehydrationCampaignRuntime.bind_loop() dereferences campaign_runtime.loop_runtime.
    # Starting/validating a loop through a different runtime could therefore create a
    # valid loop on one persistence surface that the campaign cannot read back.  The
    # production campaign runtime always carries loop_runtime; test doubles without
    # that attribute inherit the explicitly supplied runtime.
    campaign_loop_runtime = getattr(campaign_runtime, "loop_runtime", loop_runtime)
    if campaign_loop_runtime is not loop_runtime:
        return _hold(
            "LOOP_RUNTIME_MISMATCH",
            "campaign runtime and supplied V1 loop runtime do not share the same persistence surface",
        )

    campaign_before = campaign_runtime.resume(campaign_id)
    if campaign_before.get("status") != "RESUMED":
        return _hold("CAMPAIGN_RESUME", "campaign failed fresh resume", resume=campaign_before)
    if campaign_before.get("state_digest") != expected_campaign_state_digest:
        return _hold(
            "STALE_CAMPAIGN_STATE",
            "campaign state digest changed before loop binding",
            expected=expected_campaign_state_digest,
            current=campaign_before.get("state_digest"),
        )
    if campaign_before.get("checkpoint_head") != expected_campaign_checkpoint_head:
        return _hold(
            "STALE_CAMPAIGN_CHECKPOINT",
            "campaign checkpoint changed before loop binding",
            expected=expected_campaign_checkpoint_head,
            current=campaign_before.get("checkpoint_head"),
        )

    campaign_verify_before = campaign_runtime.verify(campaign_id)
    if campaign_verify_before.get("status") != "PASS":
        return _hold("CAMPAIGN_VERIFY_PRE", "campaign verification failed before mutation", verify=campaign_verify_before)

    current_git_head = campaign_runtime.git.head()
    if current_git_head != expected_git_head:
        return _hold(
            "STALE_GIT_HEAD",
            "Git head changed before campaign claim",
            expected=expected_git_head,
            current=current_git_head,
        )

    branch = _branch(campaign_before, branch_id)
    if branch is None:
        return _hold("BRANCH_IDENTITY", "branch_id does not identify exactly one campaign branch", branch_id=branch_id)
    if branch.get("status") != "OPEN":
        return _hold("BRANCH_NOT_OPEN", "loop binder only claims a fresh OPEN branch", branch_status=branch.get("status"))
    if str(branch.get("candidate_id") or "") != candidate_id:
        return _hold(
            "BRANCH_CANDIDATE_MISMATCH",
            "campaign branch is not materialized from the selected Step-3 candidate",
            branch_candidate_id=branch.get("candidate_id"),
            candidate_id=candidate_id,
        )
    if " ".join(str(branch.get("task") or "").split()) != " ".join(str(candidate.get("task") or "").split()):
        return _hold("BRANCH_TASK_MISMATCH", "campaign branch task differs from selected residual candidate task")

    claimed = campaign_runtime.claim(
        campaign_id=campaign_id,
        expected_state_digest=expected_campaign_state_digest,
        expected_checkpoint_head=expected_campaign_checkpoint_head,
        branch_id=branch_id,
        agent=actor,
        actor=actor,
        shared_remote_mode=shared_remote_mode,
        remote=remote,
    )

    loop_kwargs: dict[str, Any] = {
        "goal": str(campaign_before.get("goal") or candidate["task"]),
        "task": str(candidate["task"]),
        "expected_git_head": claimed["checkpoint_head"],
        "actor": actor,
        "remote": remote,
        "fetch": bool(fetch),
        "use_frontier": bool(use_frontier),
        "shared_remote_mode": shared_remote_mode,
        "max_steps": int(max_steps),
        "max_no_progress": int(max_no_progress),
        "max_prompt_chars": int(max_prompt_chars),
        "depth_mode": depth_mode,
        "required_passes": required_passes,
        "stop_conditions": [
            f"campaign_id={campaign_id}",
            f"branch_id={branch_id}",
            f"candidate_id={candidate_id}",
        ],
    }
    if profile is not None:
        loop_kwargs["profile"] = profile
    if source_ref is not None:
        loop_kwargs["source_ref"] = source_ref

    loop_started = loop_runtime.start(**loop_kwargs)
    loop_id = str(loop_started.get("loop_id") or "")
    if not loop_id:
        return _hold("LOOP_START", "V1 loop start did not return loop_id", loop_started=loop_started)

    handoff = loop_runtime.resume(loop_id, include_prompt=True)
    if handoff.get("status") != "RESUMED":
        return _hold(
            "LOOP_RESUME",
            "fresh V1 loop handoff failed integrity resume",
            loop_id=loop_id,
            claimed=claimed,
            loop_started=loop_started,
            handoff=handoff,
        )
    if handoff.get("state_digest") != loop_started.get("state_digest"):
        return _hold(
            "LOOP_STATE_DRIFT",
            "loop state changed between start and handoff resume",
            loop_id=loop_id,
            started_state_digest=loop_started.get("state_digest"),
            resumed_state_digest=handoff.get("state_digest"),
        )
    if handoff.get("checkpoint_head") != loop_started.get("checkpoint_head"):
        return _hold(
            "LOOP_CHECKPOINT_DRIFT",
            "loop checkpoint changed between start and handoff resume",
            loop_id=loop_id,
            started_checkpoint=loop_started.get("checkpoint_head"),
            resumed_checkpoint=handoff.get("checkpoint_head"),
        )

    loop_verify = loop_runtime.verify(loop_id)
    if loop_verify.get("status") != "PASS":
        return _hold(
            "LOOP_VERIFY",
            "fresh V1 loop failed causal-integrity verification; branch remains claimed and loop is not bound",
            loop_id=loop_id,
            claimed=claimed,
            loop_started=loop_started,
            handoff=handoff,
            verify=loop_verify,
        )

    bound = campaign_runtime.bind_loop(
        campaign_id=campaign_id,
        expected_state_digest=claimed["state_digest"],
        expected_checkpoint_head=claimed["checkpoint_head"],
        branch_id=branch_id,
        loop_id=loop_id,
        loop_state_digest=handoff["state_digest"],
        actor=actor,
        shared_remote_mode=shared_remote_mode,
        remote=remote,
    )

    campaign_after = campaign_runtime.resume(campaign_id)
    campaign_verify_after = campaign_runtime.verify(campaign_id)
    if campaign_after.get("status") != "RESUMED" or campaign_verify_after.get("status") != "PASS":
        return _hold(
            "CAMPAIGN_VERIFY_POST",
            "campaign failed resume/verify after LOOP_BOUND; binding exists and requires repair before continuation",
            loop_id=loop_id,
            bound=bound,
            campaign_after=campaign_after,
            verify=campaign_verify_after,
        )

    bound_branch = _branch(campaign_after, branch_id)
    if bound_branch is None or (bound_branch.get("loop") or {}).get("loop_id") != loop_id:
        return _hold(
            "BINDING_READBACK",
            "campaign readback does not contain the exact V1 loop binding",
            loop_id=loop_id,
            campaign_after=campaign_after,
        )

    return {
        "artifact": ARTIFACT,
        "status": "BOUND",
        "standing": SUCCESS_STANDING,
        "campaign_id": campaign_id,
        "branch_id": branch_id,
        "candidate_id": candidate_id,
        "candidate": candidate,
        "campaign_before": {
            "state_digest": campaign_before.get("state_digest"),
            "checkpoint_head": campaign_before.get("checkpoint_head"),
            "chain_digest": campaign_before.get("chain_digest"),
        },
        "claim": claimed,
        "loop_started": loop_started,
        "handoff": handoff,
        "loop_verify": loop_verify,
        "binding": bound,
        "campaign_after": {
            "state_digest": campaign_after.get("state_digest"),
            "checkpoint_head": campaign_after.get("checkpoint_head"),
            "chain_digest": campaign_after.get("chain_digest"),
            "branch": bound_branch,
        },
        "campaign_verify": campaign_verify_after,
        "next": "EXECUTE_EXPLICIT_V1_LOOP_CYCLE_OR_HOLD",
        "laws": list(LAWS),
    }
