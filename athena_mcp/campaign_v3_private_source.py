from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

from .campaign_v3_ledger import PULSE_ARTIFACT
from .rehydration_campaign import ACTIVE_WIDTH_STATES, CAMPAIGN_ROOT, _campaign_state_digest

ARTIFACT = "ATHENA.CAMPAIGN.V3.PRIVATE.SOURCE.V1"
SOURCE_ARTIFACT = "ATHENA.CAMPAIGN.V3.PRIVATE.SOURCE.IDENTITY.V1"
SOURCE_KIND = "CAMPAIGN_V3_PRIVATE_LEDGER_RESIDUAL"

LAWS = [
    "PRIVATE_PAYLOAD != DURABLE_SOURCE_IDENTITY",
    "PAYLOAD_DIGEST_MATCH != EXECUTION_AUTHORITY",
    "OPAQUE_SOURCE_BOUND != CLAIM",
    "OPAQUE_LOOP_BOUND != WORK_EXECUTED",
    "PRIVATE_SOURCE != PUBLIC_FIXTURE",
    "PRIVATE_PAYLOAD_REQUIRED_TRANSIENTLY",
    "MISSING_OR_MISMATCHED_PRIVATE_PAYLOAD => HOLD",
    "COLD_RESUME != CHAT_MEMORY",
    "CAMPAIGN_SUCCESS = HOLD",
]


def _sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _payload_digest(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _pulse_integrity(pulse: Mapping[str, Any]) -> bool:
    digest = str(pulse.get("pulse_digest") or "")
    if not digest:
        return False
    return digest == _sha({key: value for key, value in pulse.items() if key != "pulse_digest"})


def _source_digest(source: Mapping[str, Any]) -> str:
    return _sha({key: value for key, value in source.items() if key != "source_digest"})


def _opaque_task(source: Mapping[str, Any]) -> str:
    step = int(source.get("step") or 0)
    digest = str(source.get("private_payload_digest") or "")
    source_digest = str(source.get("source_digest") or "")
    return f"PRIVATE_CAMPAIGN_SOURCE step={step:04d} payload={digest[:16]} source={source_digest[:16]}"


def _result(status: str, *, next_action: str, **extra: Any) -> dict[str, Any]:
    value = {
        "artifact": ARTIFACT,
        "status": status,
        "execution_authority": False,
        "work_executed": False,
        "private_payload_disclosed": False,
        "next": next_action,
        "laws": list(LAWS),
    }
    value.update(extra)
    return value


def validate_private_source_identity(source: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if source.get("artifact") != SOURCE_ARTIFACT:
        errors.append("SOURCE_ARTIFACT_INVALID")
    if source.get("kind") != SOURCE_KIND:
        errors.append("SOURCE_KIND_INVALID")
    digest = str(source.get("source_digest") or "")
    if not digest or digest != _source_digest(source):
        errors.append("SOURCE_DIGEST_INVALID")
    if not str(source.get("ledger_digest") or ""):
        errors.append("LEDGER_DIGEST_REQUIRED")
    if not str(source.get("pulse_digest") or ""):
        errors.append("PULSE_DIGEST_REQUIRED")
    if int(source.get("pulse_index") or 0) < 1:
        errors.append("PULSE_INDEX_INVALID")
    if int(source.get("step") or 0) < 1:
        errors.append("STEP_INVALID")
    if str(source.get("horizon") or "") not in {"I", "M", "L"}:
        errors.append("HORIZON_INVALID")
    private_ref = str(source.get("private_ref") or "")
    if not private_ref or len(private_ref) > 256:
        errors.append("PRIVATE_REF_INVALID")
    payload_digest = str(source.get("private_payload_digest") or "")
    if len(payload_digest) != 64 or any(ch not in "0123456789abcdef" for ch in payload_digest):
        errors.append("PRIVATE_PAYLOAD_DIGEST_INVALID")
    if not str(source.get("compiled_at_head") or ""):
        errors.append("COMPILED_HEAD_REQUIRED")
    coordinate_digest = str(source.get("current_coordinate_digest") or "")
    if len(coordinate_digest) != 64:
        errors.append("CURRENT_COORDINATE_DIGEST_INVALID")
    if source.get("payload_disclosure") != "PRIVATE_TRANSIENT_ONLY":
        errors.append("PAYLOAD_DISCLOSURE_POLICY_INVALID")
    if source.get("execution_authority") is not False:
        errors.append("SOURCE_AUTHORITY_FIREWALL_MISSING")
    forbidden = {"text", "action_text", "private_payload", "payload", "body"}
    present = sorted(forbidden.intersection(source))
    if present:
        errors.append("PLAINTEXT_PAYLOAD_FIELD_FORBIDDEN:" + ",".join(present))
    return errors


def compile_private_source_identity(
    pulse: Mapping[str, Any],
    residual_step: int,
    *,
    private_ref: str,
    expected_git_head: str,
) -> dict[str, Any]:
    """Derive a durable opaque source identity from a verified pulse.

    The pulse/action text is consumed only transiently to compute a SHA-256 digest.
    The returned identity deliberately contains no action text or body.
    """

    failures: list[str] = []
    if pulse.get("artifact") != PULSE_ARTIFACT:
        failures.append("PULSE_ARTIFACT_INVALID")
    if not _pulse_integrity(pulse):
        failures.append("PULSE_DIGEST_INVALID")
    if pulse.get("execution_authorized") is not False:
        failures.append("PULSE_AUTHORITY_FIREWALL_MISSING")
    coordinates = pulse.get("current_coordinates") or {}
    pulse_head = str(coordinates.get("git_head") or "")
    if pulse_head != str(expected_git_head):
        failures.append(f"STALE_PULSE_HEAD:{pulse_head}!={expected_git_head}")
    if coordinates.get("shared_fresh") is not True:
        failures.append("SHARED_FRESHNESS_REQUIRED")

    residual_step = int(residual_step)
    if residual_step not in {int(value) for value in (pulse.get("residual_steps") or [])}:
        failures.append("STEP_NOT_RESIDUAL")
    action = None
    for row in pulse.get("actions") or []:
        if int(row.get("step") or -1) == residual_step:
            action = dict(row)
            break
    if action is None:
        failures.append("RESIDUAL_ACTION_MISSING")
    elif str(action.get("current_state") or "").upper() != "RESIDUAL":
        failures.append("ACTION_NOT_RESIDUAL")
    if failures:
        return _result(
            "HOLD_INVALID_PRIVATE_SOURCE_INPUT",
            next_action="REHYDRATE_AND_RECOMPILE_PRIVATE_SOURCE_PULSE",
            failures=failures,
            residual_step=residual_step,
        )

    private_payload = str(action.get("text") or "")
    horizon = str(action.get("horizon") or "")
    if not private_payload or horizon not in {"I", "M", "L"}:
        return _result(
            "HOLD_INVALID_PRIVATE_SOURCE_INPUT",
            next_action="REPAIR_PRIVATE_SOURCE_ACTION_IDENTITY",
            failures=["PRIVATE_SOURCE_ACTION_INVALID"],
            residual_step=residual_step,
        )
    private_ref = str(private_ref or "").strip()
    if not private_ref or len(private_ref) > 256:
        return _result(
            "HOLD_INVALID_PRIVATE_SOURCE_INPUT",
            next_action="SUPPLY_OPAQUE_PRIVATE_SOURCE_REFERENCE",
            failures=["PRIVATE_REF_INVALID"],
            residual_step=residual_step,
        )

    source = {
        "artifact": SOURCE_ARTIFACT,
        "kind": SOURCE_KIND,
        "ledger_digest": pulse.get("ledger_digest"),
        "pulse_digest": pulse.get("pulse_digest"),
        "pulse_index": int(pulse.get("pulse_index") or 0),
        "step": residual_step,
        "horizon": horizon,
        "private_ref": private_ref,
        "private_payload_digest": _payload_digest(private_payload),
        "compiled_at_head": str(expected_git_head),
        "operational_basis_digest": pulse.get("operational_basis_digest"),
        "current_coordinate_digest": _sha(dict(coordinates)),
        "payload_disclosure": "PRIVATE_TRANSIENT_ONLY",
        "execution_authority": False,
    }
    source["source_digest"] = _source_digest(source)
    errors = validate_private_source_identity(source)
    if errors:
        return _result(
            "HOLD_INVALID_PRIVATE_SOURCE_IDENTITY",
            next_action="REPAIR_OPAQUE_SOURCE_IDENTITY",
            failures=errors,
            residual_step=residual_step,
        )
    return _result(
        "PRIVATE_SOURCE_IDENTITY_COMPILED",
        next_action="START_OPAQUE_SOURCE_BOUND_CAMPAIGN",
        source=source,
        opaque_task=_opaque_task(source),
        payload_attestation={
            "private_payload_digest": source["private_payload_digest"],
            "payload_disclosure": "PRIVATE_TRANSIENT_ONLY",
            "validated": True,
        },
    )


def validate_private_payload(source: Mapping[str, Any], private_payload: str) -> dict[str, Any]:
    errors = validate_private_source_identity(source)
    if errors:
        return _result(
            "HOLD_INVALID_PRIVATE_SOURCE_IDENTITY",
            next_action="REHYDRATE_OPAQUE_SOURCE_IDENTITY",
            failures=errors,
        )
    observed_digest = _payload_digest(str(private_payload))
    expected_digest = str(source.get("private_payload_digest") or "")
    if observed_digest != expected_digest:
        return _result(
            "HOLD_PRIVATE_PAYLOAD_MISMATCH",
            next_action="SUPPLY_MATCHING_PRIVATE_PAYLOAD_TRANSIENTLY",
            expected_private_payload_digest=expected_digest,
            observed_private_payload_digest=observed_digest,
            payload_attestation={"validated": False, "payload_disclosure": "PRIVATE_TRANSIENT_ONLY"},
        )
    return _result(
        "PRIVATE_PAYLOAD_VALIDATED",
        next_action="CLAIM_AND_BIND_OPAQUE_SOURCE_EXPLICITLY",
        source_digest=source["source_digest"],
        private_payload_digest=expected_digest,
        payload_attestation={"validated": True, "payload_disclosure": "PRIVATE_TRANSIENT_ONLY"},
    )


def start_private_source_bound_campaign_v3(
    runtime: Any,
    *,
    pulse: Mapping[str, Any],
    residual_step: int,
    private_ref: str,
    expected_git_head: str,
    actor: str = "agent",
    max_width: int = 4,
    max_depth: int = 8,
    max_branches: int = 32,
    lease_steps: int = 4,
    shared_remote_mode: str = "REQUIRED",
    remote: str = "origin",
) -> dict[str, Any]:
    compiled = compile_private_source_identity(
        pulse,
        residual_step,
        private_ref=private_ref,
        expected_git_head=expected_git_head,
    )
    if compiled.get("status") != "PRIVATE_SOURCE_IDENTITY_COMPILED":
        return compiled
    source = dict(compiled["source"])
    opaque_task = str(compiled["opaque_task"])

    try:
        started = runtime.start(
            goal=f"Campaign V3 private pulse {source['pulse_index']} residual step {source['step']}",
            expected_git_head=expected_git_head,
            initial_tasks=[opaque_task],
            actor=actor,
            max_width=max_width,
            max_depth=max_depth,
            max_branches=max_branches,
            lease_steps=lease_steps,
            shared_remote_mode=shared_remote_mode,
            remote=remote,
        )
    except Exception as exc:
        return _result(
            "HOLD_PRIVATE_CAMPAIGN_START_FAILED",
            next_action="REHYDRATE_PRIVATE_CAMPAIGN_START_PRECONDITIONS",
            failures=[f"CAMPAIGN_START_FAILED:{type(exc).__name__}:{exc}"],
            source=source,
        )

    campaign_id = str(started.get("campaign_id") or "")
    start_state_digest = str(started.get("state_digest") or "")
    start_checkpoint_head = str(started.get("checkpoint_head") or "")
    branch_id = None
    try:
        state, _ = runtime._read_state(campaign_id)
        if _campaign_state_digest(state) != state.get("state_digest") or state.get("state_digest") != start_state_digest:
            raise ValueError("started campaign state digest mismatch")
        if len(state.get("branches") or {}) != 1:
            raise ValueError("private source start requires exactly one initial branch")
        branch_id, branch = next(iter(state["branches"].items()))
        if str(branch.get("task") or "") != opaque_task or branch.get("source") is not None:
            raise ValueError("started branch shape does not match opaque source contract")
    except Exception as exc:
        return _result(
            "STARTED_PRIVATE_SOURCE_UNBOUND_HOLD",
            next_action="RECOVER_EXISTING_PRIVATE_CAMPAIGN_SOURCE_BINDING",
            failures=[f"START_READBACK_FAILED:{type(exc).__name__}:{exc}"],
            campaign_id=campaign_id or None,
            branch_id=branch_id,
            source=source,
            start_state_digest=start_state_digest or None,
            start_checkpoint_head=start_checkpoint_head or None,
        )

    def bind_source(new_state: dict[str, Any]) -> dict[str, Any]:
        branch = (new_state.get("branches") or {}).get(branch_id)
        if not branch:
            raise ValueError("private source branch disappeared")
        if str(branch.get("task") or "") != opaque_task:
            raise ValueError("private source branch task drift")
        existing = branch.get("source")
        if existing is not None and existing != source:
            raise ValueError("private source branch already carries different source identity")
        branch["source"] = dict(source)
        return new_state

    try:
        bound = runtime._mutate(
            campaign_id=campaign_id,
            expected_state_digest=start_state_digest,
            expected_checkpoint_head=start_checkpoint_head,
            actor=actor,
            event_type="CAMPAIGN_V3_PRIVATE_SOURCE_BOUND",
            mutator=bind_source,
            shared_remote_mode=shared_remote_mode,
            remote=remote,
        )
    except Exception as exc:
        return _result(
            "STARTED_PRIVATE_SOURCE_UNBOUND_HOLD",
            next_action="RECOVER_EXISTING_PRIVATE_CAMPAIGN_SOURCE_BINDING",
            failures=[f"PRIVATE_SOURCE_BIND_FAILED:{type(exc).__name__}:{exc}"],
            campaign_id=campaign_id,
            branch_id=branch_id,
            source=source,
            start_state_digest=start_state_digest,
            start_checkpoint_head=start_checkpoint_head,
        )

    return _result(
        "STARTED_PRIVATE_SOURCE_BOUND",
        next_action="VALIDATE_PRIVATE_PAYLOAD_TRANSIENTLY_BEFORE_BIND",
        campaign_id=campaign_id,
        branch_id=branch_id,
        state_digest=bound.get("state_digest"),
        checkpoint_head=bound.get("checkpoint_head"),
        source=source,
        opaque_task=opaque_task,
        standing="DURABLE_OPAQUE_SOURCE_BOUND_NOT_CLAIMED",
    )


def bind_private_source_branch_to_loop(
    campaign_runtime: Any,
    loop_runtime: Any,
    *,
    campaign_id: str,
    branch_id: str,
    expected_state_digest: str,
    expected_checkpoint_head: str,
    private_payload: str,
    agent: str = "agent",
    actor: str = "agent",
    loop_max_steps: int = 3,
    shared_remote_mode: str = "REQUIRED",
    remote: str = "origin",
) -> dict[str, Any]:
    try:
        state, _ = campaign_runtime._read_state(campaign_id)
    except Exception as exc:
        return _result(
            "HOLD_PRIVATE_CAMPAIGN_READ_FAILED",
            next_action="REHYDRATE_PRIVATE_CAMPAIGN",
            failures=[f"CAMPAIGN_READ_FAILED:{type(exc).__name__}:{exc}"],
        )
    if state.get("state_digest") != expected_state_digest:
        return _result(
            "HOLD_STALE_PRIVATE_CAMPAIGN_STATE",
            next_action="REHYDRATE_PRIVATE_CAMPAIGN",
            expected_state_digest=expected_state_digest,
            actual_state_digest=state.get("state_digest"),
        )
    branch = (state.get("branches") or {}).get(branch_id)
    if not isinstance(branch, Mapping):
        return _result("HOLD_PRIVATE_BRANCH_NOT_FOUND", next_action="REHYDRATE_PRIVATE_CAMPAIGN")
    source = branch.get("source")
    if not isinstance(source, Mapping):
        return _result("HOLD_PRIVATE_SOURCE_NOT_BOUND", next_action="BIND_OPAQUE_PRIVATE_SOURCE")
    errors = validate_private_source_identity(source)
    if errors:
        return _result(
            "HOLD_INVALID_PRIVATE_SOURCE_IDENTITY",
            next_action="REPAIR_OPAQUE_SOURCE_IDENTITY",
            failures=errors,
        )
    if str(branch.get("task") or "") != _opaque_task(source):
        return _result("HOLD_PRIVATE_BRANCH_TASK_DRIFT", next_action="REHYDRATE_PRIVATE_CAMPAIGN")
    attestation = validate_private_payload(source, private_payload)
    if attestation.get("status") != "PRIVATE_PAYLOAD_VALIDATED":
        return attestation
    if branch.get("status") not in ACTIVE_WIDTH_STATES or branch.get("loop") is not None:
        return _result(
            "HOLD_PRIVATE_BRANCH_NOT_BINDABLE",
            next_action="RECONCILE_PRIVATE_BRANCH_STATE",
            branch_status=branch.get("status"),
            loop_bound=branch.get("loop") is not None,
        )

    try:
        claimed = campaign_runtime.claim(
            campaign_id=campaign_id,
            expected_state_digest=expected_state_digest,
            expected_checkpoint_head=expected_checkpoint_head,
            branch_id=branch_id,
            agent=agent,
            actor=actor,
            shared_remote_mode=shared_remote_mode,
            remote=remote,
        )
        post_lease_head = campaign_runtime.git.head()
        loop_task = (
            f"Execute transient private Campaign V3 source digest {source['source_digest'][:24]} "
            "within the authorized current session; never persist or emit the private payload."
        )
        loop_started = loop_runtime.start(
            goal=f"Campaign V3 private source step {int(source['step']):04d}",
            expected_git_head=post_lease_head,
            task=loop_task,
            actor=agent,
            profile="BUILD",
            source_ref="HEAD",
            remote=remote,
            fetch=False,
            use_frontier=False,
            shared_remote_mode=shared_remote_mode,
            max_steps=loop_max_steps,
            max_no_progress=2,
            depth_mode="standard",
            required_passes=["reconstruct", "execute", "verify"],
            stop_conditions=["Never persist, quote, or emit the transient private source payload."],
        )
        bound = campaign_runtime.bind_loop(
            campaign_id=campaign_id,
            expected_state_digest=claimed["state_digest"],
            expected_checkpoint_head=claimed["checkpoint_head"],
            branch_id=branch_id,
            loop_id=loop_started["loop_id"],
            loop_state_digest=loop_started["state_digest"],
            actor=actor,
            shared_remote_mode=shared_remote_mode,
            remote=remote,
        )
    except Exception as exc:
        return _result(
            "HOLD_PRIVATE_LOOP_BIND_FAILED",
            next_action="REHYDRATE_PRIVATE_CAMPAIGN_AND_LOOP",
            failures=[f"PRIVATE_LOOP_BIND_FAILED:{type(exc).__name__}:{exc}"],
            source_digest=source.get("source_digest"),
            private_payload_digest=source.get("private_payload_digest"),
        )

    return _result(
        "PRIVATE_SOURCE_LOOP_BOUND",
        next_action="EXECUTE_VALIDATED_PRIVATE_PAYLOAD_IN_CURRENT_SESSION_AND_RECEIPT_OBSERVED_WORK",
        campaign_id=campaign_id,
        branch_id=branch_id,
        source_digest=source["source_digest"],
        private_payload_digest=source["private_payload_digest"],
        payload_attestation=attestation["payload_attestation"],
        claim_checkpoint_head=claimed.get("checkpoint_head"),
        post_lease_head=post_lease_head,
        loop_id=loop_started.get("loop_id"),
        loop_state_digest=loop_started.get("state_digest"),
        loop_checkpoint_head=loop_started.get("checkpoint_head"),
        campaign_state_digest=bound.get("state_digest"),
        campaign_checkpoint_head=bound.get("checkpoint_head"),
        standing="OPAQUE_PRIVATE_SOURCE_BOUND_TO_LOOP_NOT_EXECUTED",
    )


def cold_resume_private_campaign_v3(
    runtime: Any,
    *,
    shared_remote_mode: str = "REQUIRED",
    remote: str = "origin",
) -> dict[str, Any]:
    try:
        mode = runtime._remote_mode(shared_remote_mode)
        remote_sync = runtime._sync(mode, remote)
    except Exception as exc:
        return _result(
            "HOLD_SHARED_FRESHNESS",
            next_action="RESTORE_SHARED_FRESHNESS",
            failures=[f"SHARED_FRESHNESS_ERROR:{type(exc).__name__}:{exc}"],
        )
    if mode != "DISABLED" and not remote_sync.get("shared_frontier_verified"):
        return _result(
            "HOLD_SHARED_FRESHNESS",
            next_action="RESTORE_SHARED_FRESHNESS",
            remote_sync=remote_sync,
        )

    current_head = runtime.git.head()
    root = runtime._safe_rel(CAMPAIGN_ROOT)
    if not root.is_dir():
        return _result(
            "HOLD_NO_PRIVATE_CAMPAIGN",
            next_action="START_DURABLE_PRIVATE_SOURCE_CAMPAIGN",
            remote_sync=remote_sync,
            current_git_head=current_head,
        )

    candidates: list[dict[str, Any]] = []
    diagnostics: list[dict[str, Any]] = []
    for entry in sorted(root.iterdir(), key=lambda path: path.name):
        if not entry.is_dir() or not entry.name.startswith("RHC-"):
            continue
        campaign_id = entry.name
        try:
            state, paths = runtime._read_state(campaign_id)
            if _campaign_state_digest(state) != state.get("state_digest"):
                raise ValueError("campaign state digest mismatch")
            checkpoint = runtime._path_last_commit(paths["state"])
            if not checkpoint or not runtime._is_ancestor(checkpoint, current_head):
                raise ValueError("campaign checkpoint ancestry mismatch")
            verification = runtime.verify(campaign_id)
            if verification.get("status") != "PASS":
                raise ValueError("campaign replay verification failed")
        except Exception as exc:
            diagnostics.append({"campaign_id": campaign_id, "standing": "INVALID", "detail": f"{type(exc).__name__}:{exc}"})
            continue

        private_branches = []
        for branch in (state.get("branches") or {}).values():
            source = branch.get("source")
            if isinstance(source, Mapping) and source.get("kind") == SOURCE_KIND:
                errors = validate_private_source_identity(source)
                if errors or str(branch.get("task") or "") != _opaque_task(source):
                    diagnostics.append({"campaign_id": campaign_id, "branch_id": branch.get("branch_id"), "standing": "INVALID_PRIVATE_SOURCE", "errors": errors})
                    continue
                private_branches.append(branch)
        if private_branches:
            candidates.append({
                "campaign_id": campaign_id,
                "state": state,
                "checkpoint_head": checkpoint,
                "verification": verification,
                "branches": private_branches,
            })

    if not candidates:
        return _result(
            "HOLD_NO_VALID_PRIVATE_CAMPAIGN",
            next_action="START_OR_REPAIR_PRIVATE_SOURCE_CAMPAIGN",
            remote_sync=remote_sync,
            current_git_head=current_head,
            diagnostics=diagnostics,
        )
    if len(candidates) != 1:
        return _result(
            "HOLD_AMBIGUOUS_PRIVATE_CAMPAIGN",
            next_action="RECONCILE_PRIVATE_CAMPAIGN_IDENTITY",
            remote_sync=remote_sync,
            current_git_head=current_head,
            campaign_candidates=[row["campaign_id"] for row in candidates],
            diagnostics=diagnostics,
        )
    selected = candidates[0]
    branches = selected["branches"]
    resumable = [branch for branch in branches if branch.get("status") in ACTIVE_WIDTH_STATES]
    if len(resumable) != 1:
        return _result(
            "HOLD_AMBIGUOUS_PRIVATE_BRANCH" if len(resumable) > 1 else "DISCOVERED_NO_RESUMABLE_PRIVATE_BRANCH",
            next_action="RECONCILE_PRIVATE_BRANCH_FRONTIER",
            remote_sync=remote_sync,
            current_git_head=current_head,
            campaign_id=selected["campaign_id"],
            state_digest=selected["state"].get("state_digest"),
            checkpoint_head=selected["checkpoint_head"],
            branch_ids=[branch.get("branch_id") for branch in resumable],
        )
    branch = resumable[0]
    source = dict(branch["source"])
    return _result(
        "PRIVATE_CAMPAIGN_RESUMED",
        next_action=(
            "VALIDATE_TRANSIENT_PRIVATE_PAYLOAD_AND_BIND_LOOP"
            if branch.get("loop") is None
            else "FRESH_RESUME_BOUND_LOOP_BEFORE_PRIVATE_WORK"
        ),
        remote_sync=remote_sync,
        current_git_head=current_head,
        campaign_id=selected["campaign_id"],
        state_digest=selected["state"].get("state_digest"),
        checkpoint_head=selected["checkpoint_head"],
        branch_id=branch.get("branch_id"),
        branch_status=branch.get("status"),
        source=source,
        source_digest=source["source_digest"],
        private_payload_digest=source["private_payload_digest"],
        loop_binding=dict(branch.get("loop") or {}),
        standing="DURABLE_OPAQUE_PRIVATE_SOURCE_DISCOVERED",
    )
