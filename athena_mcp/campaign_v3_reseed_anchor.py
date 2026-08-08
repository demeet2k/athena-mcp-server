from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping, Sequence

from .campaign_v3_ledger import PULSE_ARTIFACT

SCHEMA_VERSION = "ATHENA.RESEED_ANCHOR.V1"
ATHENA_RESEED_SOURCE_HEAD = "9c369d8c9cbcb7463469bcbbfd93597bffec0275"
ATHENA_RESEED_SCHEMA_BLOB = "6d9f2da5bd900239dcce01d455123675202f3b09"
ATHENA_RESEED_SCRIPT_BLOB = "8eb274cc8d7f966e8778da5677fa0207233ae39b"

POSITIVE_CLASSES = {"POSITIVE", "CONTINUE_POSITIVE_FRONTIER"}
NONPOSITIVE_CLASSES = {"NONPOSITIVE"}
STOP_CLASSES = {
    "NO_POSITIVE_FRONTIER",
    "BUDGET_EXHAUSTED",
    "AUTHORITY_HOLD",
    "EVIDENCE_HOLD",
    "STALE_STATE_HOLD",
    "CAPABILITY_HOLD",
    "HUMAN_VALUE_CHOICE",
    "META_OVERHEAD_COLLAPSE",
    "DUPLICATION_COLLAPSE",
}
ALLOWED_KEYS = {
    "schema_version",
    "anchor_id",
    "parent_anchor_id",
    "parent_reseed_epoch",
    "run_id",
    "agent_coordinate_name",
    "reseed_epoch",
    "pulse_age_before",
    "pulse_age_after",
    "git",
    "git_positions",
    "prompt_digest",
    "issue_pressure_digest",
    "target_versions",
    "durable_returns",
    "satisfied_work",
    "residuals",
    "holds",
    "continuation_value_class",
    "selected_successor",
    "stop_class",
    "reverse_route",
    "witnesses",
    "platform_counter_reset_claimed",
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _pulse_integrity(pulse: Mapping[str, Any]) -> bool:
    digest = str(pulse.get("pulse_digest") or "")
    if not digest:
        return False
    return digest == _sha({k: v for k, v in pulse.items() if k != "pulse_digest"})


def _nonempty_strings(values: Sequence[Any] | None) -> list[str]:
    out: list[str] = []
    for value in values or []:
        text = str(value or "").strip()
        if text and text not in out:
            out.append(text)
    return out


def _normalize_git_positions(values: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    positions: list[dict[str, Any]] = []
    seen: set[str] = set()
    for raw in values:
        repo = str(raw.get("repo") or "").strip()
        ref = str(raw.get("ref") or "").strip()
        head = str(raw.get("head") or "").strip()
        tree = raw.get("tree")
        tree_text = None if tree is None else str(tree)
        if not repo or not ref or not head:
            raise ValueError("git position requires repo/ref/head")
        key = f"{repo}::{ref}"
        if key in seen:
            raise ValueError(f"duplicate git position: {key}")
        seen.add(key)
        positions.append({"repo": repo, "ref": ref, "head": head, "tree": tree_text})
    if not positions:
        raise ValueError("at least one ref-scoped git position is required")
    return positions


def _target_versions(
    *,
    pulse: Mapping[str, Any],
    campaign_id: str,
    campaign_state_digest: str,
    campaign_checkpoint_head: str,
    loop_id: str | None,
    loop_state_digest: str | None,
    extra_target_versions: Sequence[Mapping[str, Any]] | None,
) -> list[dict[str, str]]:
    values: list[dict[str, str]] = [
        {"id": "campaign_v3.ledger_digest", "version": str(pulse.get("ledger_digest") or "UNKNOWN")},
        {"id": "campaign_v3.pulse_digest", "version": str(pulse.get("pulse_digest") or "UNKNOWN")},
        {"id": "campaign_v3.pulse_index", "version": str(int(pulse.get("pulse_index") or 0))},
        {"id": "campaign_v3.campaign_id", "version": str(campaign_id)},
        {"id": "campaign_v3.campaign_state_digest", "version": str(campaign_state_digest)},
        {"id": "campaign_v3.campaign_checkpoint_head", "version": str(campaign_checkpoint_head)},
    ]
    if loop_id:
        values.append({"id": "campaign_v3.loop_id", "version": str(loop_id)})
    if loop_state_digest:
        values.append({"id": "campaign_v3.loop_state_digest", "version": str(loop_state_digest)})
    for row in extra_target_versions or []:
        target_id = str(row.get("id") or "").strip()
        version = str(row.get("version") or "").strip()
        if not target_id or not version:
            raise ValueError("target version requires id/version")
        values.append({"id": target_id, "version": version})

    out: list[dict[str, str]] = []
    seen: set[str] = set()
    for row in values:
        if row["id"] in seen:
            raise ValueError(f"duplicate target id: {row['id']}")
        seen.add(row["id"])
        out.append(row)
    return out


def validate_campaign_v3_reseed_anchor(anchor: Mapping[str, Any]) -> list[str]:
    """Strict compatibility validator for objects emitted by this adapter.

    This mirrors the canonical Athena RESEED_ANCHOR_V1 contract relevant to
    generated Campaign V3 anchors. The source blob identities are pinned above;
    a future Athena contract change must be requalified rather than silently used.
    """
    errors: list[str] = []
    extra = sorted(set(anchor) - ALLOWED_KEYS)
    if extra:
        errors.extend(f"unknown:{key}" for key in extra)
    if anchor.get("schema_version") != SCHEMA_VERSION:
        errors.append("schema_version")
    for key in (
        "anchor_id",
        "run_id",
        "agent_coordinate_name",
        "reseed_epoch",
        "pulse_age_before",
        "pulse_age_after",
        "git",
        "prompt_digest",
        "issue_pressure_digest",
        "target_versions",
        "durable_returns",
        "satisfied_work",
        "residuals",
        "holds",
        "continuation_value_class",
        "selected_successor",
        "stop_class",
        "reverse_route",
        "witnesses",
        "platform_counter_reset_claimed",
    ):
        if key not in anchor:
            errors.append(f"missing:{key}")
    if anchor.get("pulse_age_after") != 0:
        errors.append("pulse_age_after_must_be_zero")
    if not isinstance(anchor.get("reseed_epoch"), int) or int(anchor.get("reseed_epoch", -1)) < 0:
        errors.append("reseed_epoch")
    parent_epoch = anchor.get("parent_reseed_epoch")
    if parent_epoch is not None and int(anchor.get("reseed_epoch", -1)) <= int(parent_epoch):
        errors.append("reseed_epoch_not_monotonic")

    git = anchor.get("git")
    positions = anchor.get("git_positions")
    if not isinstance(git, Mapping) or not git.get("head_after") or not isinstance(git.get("changed"), bool):
        errors.append("git")
    if not isinstance(positions, list) or not positions:
        errors.append("git_positions")
    else:
        seen: set[str] = set()
        position_map: dict[str, Mapping[str, Any]] = {}
        for idx, row in enumerate(positions):
            if not isinstance(row, Mapping) or not row.get("repo") or not row.get("ref") or not row.get("head"):
                errors.append(f"git_positions[{idx}]")
                continue
            key = f"{row['repo']}::{row['ref']}"
            if key in seen:
                errors.append(f"git_positions_duplicate:{key}")
            seen.add(key)
            position_map[key] = row
        if isinstance(git, Mapping) and git.get("repo") and git.get("ref"):
            key = f"{git['repo']}::{git['ref']}"
            row = position_map.get(key)
            if row is None:
                errors.append("git_primary_coordinate_missing")
            else:
                if str(row.get("head")) != str(git.get("head_after")):
                    errors.append("git.head_after_conflicts_with_git_positions")
                if str(row.get("tree") or "") != str(git.get("tree_after") or ""):
                    errors.append("git.tree_after_conflicts_with_git_positions")
        head_before = git.get("head_before") if isinstance(git, Mapping) else None
        head_after = git.get("head_after") if isinstance(git, Mapping) else None
        if head_before is not None and isinstance(git, Mapping):
            if bool(git.get("changed")) != (str(head_before) != str(head_after)):
                errors.append("git.changed_inconsistent_with_heads")

    for key in ("target_versions", "durable_returns", "satisfied_work", "residuals", "holds", "reverse_route", "witnesses"):
        if not isinstance(anchor.get(key), list):
            errors.append(f"{key}_must_be_list")
    if isinstance(anchor.get("durable_returns"), list) and not anchor["durable_returns"]:
        errors.append("durable_return_required")
    if isinstance(anchor.get("witnesses"), list) and not anchor["witnesses"]:
        errors.append("readback_or_witness_required")
    if isinstance(anchor.get("target_versions"), list):
        ids: set[str] = set()
        for idx, row in enumerate(anchor["target_versions"]):
            if not isinstance(row, Mapping) or not row.get("id") or not row.get("version"):
                errors.append(f"target_versions[{idx}]")
                continue
            target_id = str(row["id"])
            if target_id in ids:
                errors.append(f"target_versions_duplicate:{target_id}")
            ids.add(target_id)

    if anchor.get("platform_counter_reset_claimed") is not False:
        errors.append("platform_counter_reset_claimed_must_be_false")

    value_class = anchor.get("continuation_value_class")
    successor = anchor.get("selected_successor")
    stop_class = anchor.get("stop_class")
    holds = anchor.get("holds")
    if value_class in POSITIVE_CLASSES:
        if isinstance(holds, list) and holds:
            errors.append("positive_frontier_blocked_by_holds")
        if not successor:
            errors.append("positive_frontier_requires_successor")
        if stop_class not in (None, "CONTINUE_POSITIVE_FRONTIER"):
            errors.append("positive_frontier_stop_class_conflict")
    elif value_class in NONPOSITIVE_CLASSES:
        if successor is not None:
            errors.append("nonpositive_frontier_must_not_emit_successor")
        if stop_class not in STOP_CLASSES:
            errors.append("nonpositive_frontier_requires_typed_stop")
    else:
        errors.append("continuation_value_class_unknown")

    if anchor.get("stop_class") == "SUCCESS_CLOSED":
        errors.append("campaign_v3_bounded_pulse_cannot_self_certify_success")
    return errors


def compile_campaign_v3_reseed_anchor(
    *,
    pulse: Mapping[str, Any],
    campaign_id: str,
    campaign_state_digest: str,
    campaign_checkpoint_head: str,
    loop_id: str | None,
    loop_state_digest: str | None,
    anchor_id: str,
    run_id: str,
    agent_coordinate_name: str,
    reseed_epoch: int,
    pulse_age_before: int,
    git_positions: Sequence[Mapping[str, Any]],
    primary_repo: str,
    primary_ref: str,
    primary_head_before: str | None,
    prompt_digest: str | None,
    issue_pressure_digest: str | None,
    durable_returns: Sequence[Any],
    witnesses: Sequence[Any],
    continuation_value_class: str,
    selected_successor: str | None,
    stop_class: str | None,
    reverse_route: Sequence[Any] | None = None,
    external_holds: Sequence[Any] | None = None,
    parent_anchor: Mapping[str, Any] | None = None,
    extra_target_versions: Sequence[Mapping[str, Any]] | None = None,
    then_current_rehydrated: bool = False,
) -> dict[str, Any]:
    """Compile a strict RESEED_ANCHOR_V1 object from current Campaign V3 state.

    The adapter is pure: it does not persist the anchor, reset any platform
    counter, select authority, or claim Campaign success. Callers must provide
    public durable-return/witness identifiers and current ref-scoped Git state.
    """
    if pulse.get("artifact") != PULSE_ARTIFACT or not _pulse_integrity(pulse):
        raise ValueError("invalid or tampered Campaign V3 pulse")
    if pulse.get("execution_authorized") is not False:
        raise ValueError("Campaign V3 pulse must remain non-authoritative")
    if not str(campaign_id or "").strip() or not str(campaign_state_digest or "").strip() or not str(campaign_checkpoint_head or "").strip():
        raise ValueError("campaign identity/state/checkpoint are required")
    if int(reseed_epoch) < 0 or int(pulse_age_before) < 0:
        raise ValueError("reseed epoch and pulse age must be nonnegative")
    if int(pulse.get("pulse_index") or 0) == 100 and not then_current_rehydrated:
        raise ValueError("pulse 100 requires then-current rehydration before reseed compilation")
    if stop_class == "SUCCESS_CLOSED":
        raise ValueError("bounded Campaign V3 pulse cannot self-certify campaign success")

    positions = _normalize_git_positions(git_positions)
    primary_repo = str(primary_repo or "").strip()
    primary_ref = str(primary_ref or "").strip()
    primary = next((row for row in positions if row["repo"] == primary_repo and row["ref"] == primary_ref), None)
    if primary is None:
        raise ValueError("primary Git coordinate must exist in git_positions")

    durable = _nonempty_strings(durable_returns)
    witness_values = _nonempty_strings(witnesses)
    if not durable:
        raise ValueError("at least one durable return is required")
    if not witness_values:
        raise ValueError("at least one readback/witness is required")

    parent_anchor_id = None
    parent_reseed_epoch = None
    if parent_anchor is not None:
        if parent_anchor.get("schema_version") != SCHEMA_VERSION:
            raise ValueError("parent anchor schema mismatch")
        parent_anchor_id = str(parent_anchor.get("anchor_id") or "").strip() or None
        parent_reseed_epoch = parent_anchor.get("reseed_epoch")
        if parent_anchor_id is None or not isinstance(parent_reseed_epoch, int):
            raise ValueError("parent anchor identity/epoch required")
        if int(reseed_epoch) <= int(parent_reseed_epoch):
            raise ValueError("reseed epoch must advance beyond parent")

    actions = list(pulse.get("actions") or [])
    satisfied_work = [
        f"step:{int(row['step']):04d}:{row['current_state']}:{str(row.get('text') or '').strip()}"
        for row in actions
        if str(row.get("current_state") or "").upper() in {"SATISFIED", "SUPERSEDED"}
    ]
    residuals = [
        f"step:{int(row['step']):04d}:{str(row.get('horizon') or '')}:{str(row.get('text') or '').strip()}"
        for row in actions
        if str(row.get("current_state") or "").upper() == "RESIDUAL"
    ]
    holds = _nonempty_strings(list(pulse.get("holds") or []) + list(external_holds or []))

    value_class = str(continuation_value_class or "").strip().upper()
    successor = None if selected_successor is None else str(selected_successor).strip() or None
    normalized_stop = None if stop_class is None else str(stop_class).strip().upper() or None
    if value_class in POSITIVE_CLASSES:
        if holds:
            raise ValueError("positive continuation cannot be emitted while holds remain")
        if not successor:
            raise ValueError("positive continuation requires an explicit successor")
        if normalized_stop not in (None, "CONTINUE_POSITIVE_FRONTIER"):
            raise ValueError("positive continuation has conflicting stop class")
        normalized_stop = "CONTINUE_POSITIVE_FRONTIER"
    elif value_class in NONPOSITIVE_CLASSES:
        if successor is not None:
            raise ValueError("nonpositive continuation cannot emit successor")
        if normalized_stop not in STOP_CLASSES:
            raise ValueError("nonpositive continuation requires a typed Campaign-compatible stop")
    else:
        raise ValueError("unknown continuation value class")

    target_versions = _target_versions(
        pulse=pulse,
        campaign_id=campaign_id,
        campaign_state_digest=campaign_state_digest,
        campaign_checkpoint_head=campaign_checkpoint_head,
        loop_id=loop_id,
        loop_state_digest=loop_state_digest,
        extra_target_versions=extra_target_versions,
    )

    primary_after = str(primary["head"])
    primary_before = None if primary_head_before is None else str(primary_head_before)
    anchor = {
        "schema_version": SCHEMA_VERSION,
        "anchor_id": str(anchor_id),
        "parent_anchor_id": parent_anchor_id,
        "parent_reseed_epoch": parent_reseed_epoch,
        "run_id": str(run_id),
        "agent_coordinate_name": str(agent_coordinate_name),
        "reseed_epoch": int(reseed_epoch),
        "pulse_age_before": int(pulse_age_before),
        "pulse_age_after": 0,
        "git": {
            "repo": primary_repo,
            "ref": primary_ref,
            "head_before": primary_before,
            "head_after": primary_after,
            "tree_after": primary.get("tree"),
            "changed": False if primary_before is None else primary_before != primary_after,
        },
        "git_positions": positions,
        "prompt_digest": None if prompt_digest is None else str(prompt_digest),
        "issue_pressure_digest": None if issue_pressure_digest is None else str(issue_pressure_digest),
        "target_versions": target_versions,
        "durable_returns": durable,
        "satisfied_work": satisfied_work,
        "residuals": residuals,
        "holds": holds,
        "continuation_value_class": value_class,
        "selected_successor": successor,
        "stop_class": normalized_stop,
        "reverse_route": _nonempty_strings(reverse_route),
        "witnesses": witness_values,
        "platform_counter_reset_claimed": False,
    }
    errors = validate_campaign_v3_reseed_anchor(anchor)
    if errors:
        raise ValueError("invalid compiled reseed anchor: " + ";".join(errors))
    return anchor


def reseed_anchor_digest(anchor: Mapping[str, Any]) -> str:
    errors = validate_campaign_v3_reseed_anchor(anchor)
    if errors:
        raise ValueError("invalid reseed anchor: " + ";".join(errors))
    return _sha(anchor)
