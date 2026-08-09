from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, Iterable, Mapping, Optional

from .message_board import _jaccard, _norm_target, _require_id

DUPLICATE_GUARD_VERSION = "COHESION.DUPLICATE.GUARD.1"
_VALID_INTENDED_MODES = {"PRIMARY", "REPLICA"}

LAWS = [
    "DUPLICATE_GUARD != CLAIM_MUTATION",
    "DUPLICATE_GUARD != ASSIGNMENT",
    "DUPLICATE_GUARD != AUTO_JOIN",
    "DUPLICATE_GUARD != MATA",
    "MESSAGE_BOARD = SOLE_PRESENCE_CLAIM_MESSAGE_AUTHORITY",
    "MESSAGE_BOARD_EXACT_CLASSIFICATION != MATA_SEMANTIC_CLASSIFICATION",
    "FUZZY_SIMILARITY != DUPLICATE_PROOF",
    "PARTITION_ASSERTION != PARTITION_PROOF",
    "PARTITION_PROOF != CLEAR_EXACT_WORK_IDENTITY",
    "REPLICA != INDEPENDENT_EVIDENCE",
    "JOIN_OPTION != JOIN_EXECUTED",
    "PROCEED_OPTION != EXECUTION_AUTHORITY",
    "READ_SIDE_SYNC != BOARD_WRITE",
    "UNKNOWN != ZERO",
]


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _norm_text(value: Any) -> str:
    return " ".join(str(value or "").strip().casefold().split())


def _targets(values: Optional[Iterable[Any]]) -> list[str]:
    return sorted({_norm_target(str(value)) for value in (values or []) if _norm_target(str(value))})


def _refs(values: Optional[Iterable[Any]]) -> list[str]:
    return sorted({str(value).strip() for value in (values or []) if str(value).strip()})


def _presence_view(row: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "agent_id": row.get("agent_id"),
        "claim_id": row.get("claim_id"),
        "status": row.get("status"),
        "mode": row.get("mode"),
        "task": row.get("task"),
        "work_key": row.get("work_key"),
        "targets": _targets(row.get("targets")),
        "join_of": row.get("join_of"),
    }


def _self_compatible(candidate: Mapping[str, Any], presence: Mapping[str, Any]) -> tuple[bool, list[str]]:
    differences: list[str] = []
    if _norm_text(candidate.get("task")) != _norm_text(presence.get("task")):
        differences.append("TASK")
    candidate_key = _norm_text(candidate.get("work_key"))
    presence_key = _norm_text(presence.get("work_key"))
    if candidate_key and presence_key and candidate_key != presence_key:
        differences.append("WORK_KEY")
    candidate_targets = _targets(candidate.get("targets"))
    presence_targets = _targets(presence.get("targets"))
    if candidate_targets and presence_targets and candidate_targets != presence_targets:
        differences.append("TARGETS")
    return not differences, differences


def _partition_packet(raw: Optional[Mapping[str, Any]], overlap_targets: Iterable[str]) -> Dict[str, Any]:
    overlap = sorted(set(_targets(overlap_targets)))
    if raw is None:
        return {
            "provided": False,
            "structurally_valid": False,
            "covers_all_target_collisions": False,
            "eligible_for_target_partition": False,
            "covered_targets": [],
            "uncovered_targets": overlap,
            "independently_verified": False,
            "reason_codes": ["PARTITION_PROOF_NOT_PROVIDED"] if overlap else [],
            "proof_digest": None,
        }
    if not isinstance(raw, Mapping):
        raise ValueError("partition_proof must be an object or null")
    proof_id = str(raw.get("proof_id") or "").strip()
    sinks = _targets(raw.get("shared_sinks"))
    partitions = _targets(raw.get("disjoint_targets"))
    evidence = _refs(raw.get("evidence_refs"))
    reasons: list[str] = []
    if not proof_id:
        reasons.append("PARTITION_PROOF_ID_REQUIRED")
    if not sinks:
        reasons.append("PARTITION_SHARED_SINKS_REQUIRED")
    if len(partitions) < 2:
        reasons.append("PARTITION_REQUIRES_AT_LEAST_TWO_DISJOINT_TARGETS")
    if not evidence:
        reasons.append("PARTITION_EVIDENCE_REFS_REQUIRED")
    if set(partitions) & set(sinks):
        reasons.append("DISJOINT_TARGETS_MUST_NOT_EQUAL_SHARED_SINKS")
    covered = sorted(set(overlap) & set(sinks))
    uncovered = sorted(set(overlap) - set(sinks))
    structurally_valid = not reasons
    covers_all = bool(overlap) and not uncovered
    basis = {
        "proof_id": proof_id or None,
        "shared_sinks": sinks,
        "disjoint_targets": partitions,
        "evidence_refs": evidence,
    }
    return {
        "provided": True,
        "proof_id": proof_id or None,
        "shared_sinks": sinks,
        "disjoint_targets": partitions,
        "evidence_refs": evidence,
        "structurally_valid": structurally_valid,
        "covers_all_target_collisions": covers_all,
        "eligible_for_target_partition": bool(structurally_valid and covers_all),
        "covered_targets": covered,
        "uncovered_targets": uncovered,
        "independently_verified": False,
        "reason_codes": reasons,
        "proof_digest": _digest(basis),
        "standing": "CALLER_SUPPLIED_STRUCTURAL_PARTITION_EVIDENCE",
        "law": "STRUCTURAL_PARTITION_EVIDENCE != INDEPENDENT_VERIFICATION",
    }


def _option(action: str, eligible: bool, *, requirements: Iterable[str] = (), targets: Iterable[str] = ()) -> Dict[str, Any]:
    return {
        "action": action,
        "eligible": bool(eligible),
        "requirements": list(requirements),
        "target_agent_ids": sorted({str(value) for value in targets if str(value)}),
        "execution_authority": False,
    }


def _decision_digest(value: Mapping[str, Any]) -> str:
    basis = {
        "candidate": value.get("candidate"),
        "classification": value.get("classification"),
        "standing": value.get("standing"),
        "hard_hold": value.get("hard_hold"),
        "conflicts": value.get("conflicts"),
        "fuzzy_warnings": value.get("fuzzy_warnings"),
        "self_relation": value.get("self_relation"),
        "partition": value.get("partition"),
        "treatments": value.get("treatments"),
        "mata": value.get("mata"),
    }
    return _digest(basis)


def duplicate_guard(
    runtime: Any,
    *,
    agent_id: str,
    task: str,
    work_key: Optional[str] = None,
    targets: Optional[Iterable[str]] = None,
    intended_mode: str = "PRIMARY",
    replication_reason: Optional[str] = None,
    join_agent_id: Optional[str] = None,
    partition_proof: Optional[Mapping[str, Any]] = None,
    remote: str = "origin",
    shared_remote_mode: str = "REQUIRED",
) -> Dict[str, Any]:
    """Project duplicate-work treatments without mutating Message Board authority."""

    agent_id = _require_id(agent_id, "agent_id")
    task = str(task or "").strip()
    if not task:
        raise ValueError("task is required")
    intended_mode = str(intended_mode or "PRIMARY").upper()
    if intended_mode not in _VALID_INTENDED_MODES:
        raise ValueError("intended_mode must be PRIMARY or REPLICA")
    replication_reason = str(replication_reason or "").strip() or None
    if intended_mode == "REPLICA" and not replication_reason:
        raise ValueError("REPLICA requires replication_reason")
    if join_agent_id is not None:
        join_agent_id = _require_id(join_agent_id, "join_agent_id")
        if join_agent_id == agent_id:
            raise ValueError("agent cannot declare JOIN to itself")
    if intended_mode == "REPLICA" and join_agent_id:
        raise ValueError("JOIN and REPLICA are distinct intents")

    candidate = {
        "agent_id": agent_id,
        "task": task,
        "work_key": str(work_key or "").strip() or None,
        "targets": _targets(targets),
        "mode": intended_mode,
        "replication_reason": replication_reason,
        "join_agent_id": join_agent_id,
    }

    board = runtime._board()
    head_before_sync = board.git.head()
    snapshot = board.read(
        agent_id=agent_id,
        limit=1,
        include_stale=False,
        remote=remote,
        shared_remote_mode=shared_remote_mode,
    )
    head_after_sync = board.git.head()
    shared_fresh = bool(snapshot.get("shared_frontier_verified"))
    if str(shared_remote_mode or "REQUIRED").upper() == "REQUIRED" and not shared_fresh:
        value = {
            "artifact": "ATHENA.COHESION.DUPLICATE.GUARD.V1",
            "version": DUPLICATE_GUARD_VERSION,
            "status": "COHESION_DUPLICATE_GUARD_SHARED_FRONTIER_HOLD",
            "classification": "SHARED_FRONTIER_HOLD",
            "standing": "HOLD",
            "hard_hold": True,
            "candidate": candidate,
            "conflicts": [],
            "fuzzy_warnings": [],
            "self_relation": None,
            "partition": _partition_packet(partition_proof, []),
            "treatments": [],
            "mata": {
                "runtime_available": False,
                "semantic_relation": "UNAVAILABLE_NOT_IN_RUNTIME",
                "law": "MESSAGE_BOARD_EXACT_CLASSIFICATION != MATA_SEMANTIC_CLASSIFICATION",
            },
            "shared_frontier_verified": False,
            "git_head": head_after_sync,
            "head_before_sync": head_before_sync,
            "head_after_sync": head_after_sync,
            "board_write_performed": False,
            "assignment_authority": False,
            "claim_authority": False,
            "execution_authority": False,
            "independent_verification": False,
            "remote_sync": snapshot.get("remote_sync"),
            "laws": list(LAWS),
        }
        value["decision_digest"] = _decision_digest(value)
        return value

    active = list(snapshot.get("active") or [])
    self_presence = next((row for row in active if str(row.get("agent_id")) == agent_id), None)
    self_relation = None
    self_conflict = False
    if self_presence is not None:
        compatible, differences = _self_compatible(candidate, self_presence)
        self_relation = {
            "presence": _presence_view(self_presence),
            "compatible_continuation": bool(compatible),
            "differences": differences,
        }
        self_conflict = not compatible

    conflicts: list[Dict[str, Any]] = []
    fuzzy_warnings: list[Dict[str, Any]] = []
    all_target_overlaps: set[str] = set()
    for other in active:
        if str(other.get("agent_id")) == agent_id:
            continue
        hard = board._hard_overlap(candidate, other)
        target_overlap = sorted(board._targets(candidate) & board._targets(other))
        all_target_overlaps.update(target_overlap)
        score, shared = _jaccard(task, other.get("task"))
        if hard:
            conflicts.append({
                "presence": _presence_view(other),
                "reasons": hard,
                "exact_identity_reasons": [reason for reason in hard if reason in {"EXACT_WORK_KEY", "EXACT_TASK"}],
                "target_overlap": target_overlap,
                "fuzzy_similarity": round(float(score), 6),
                "fuzzy_shared_tokens": int(shared),
            })
        elif score >= 0.65 and shared >= 3:
            fuzzy_warnings.append({
                "agent_id": other.get("agent_id"),
                "claim_id": other.get("claim_id"),
                "task": other.get("task"),
                "task_similarity": round(float(score), 6),
                "shared_tokens": int(shared),
                "classification": "POTENTIAL_OVERLAP_ONLY",
            })

    conflicts.sort(key=lambda row: (str((row.get("presence") or {}).get("agent_id")), str((row.get("presence") or {}).get("claim_id"))))
    fuzzy_warnings.sort(key=lambda row: (str(row.get("agent_id")), str(row.get("claim_id"))))
    partition = _partition_packet(partition_proof, sorted(all_target_overlaps))

    conflict_agents = [str((row.get("presence") or {}).get("agent_id")) for row in conflicts]
    identity_conflict = any(row.get("exact_identity_reasons") for row in conflicts)
    target_conflict = any(row.get("target_overlap") for row in conflicts)
    target_only_conflict = bool(conflicts and target_conflict and not identity_conflict)
    join_relevant = bool(join_agent_id and join_agent_id in conflict_agents)
    join_invalid = bool(join_agent_id and not join_relevant)

    if self_conflict:
        classification = "SELF_ACTIVE_CLAIM_CONFLICT"
        standing = "HOLD"
        hard_hold = True
        status = "COHESION_SELF_ACTIVE_CLAIM_HOLD"
    elif join_invalid:
        classification = "DECLARED_JOIN_TARGET_INVALID"
        standing = "HOLD"
        hard_hold = True
        status = "COHESION_DECLARED_JOIN_TARGET_HOLD"
    elif join_relevant:
        classification = "DECLARED_JOIN"
        standing = "HOLD_UNTIL_JOIN_EXECUTED"
        hard_hold = True
        status = "COHESION_DECLARED_JOIN_OPTION"
    elif conflicts and intended_mode == "REPLICA":
        classification = "INTENTIONAL_REPLICA"
        standing = "INTENTIONAL_OVERLAP_DECLARED"
        hard_hold = False
        status = "COHESION_INTENTIONAL_REPLICA"
    elif identity_conflict:
        classification = "EXACT_DUPLICATE_HOLD"
        standing = "HOLD"
        hard_hold = True
        status = "COHESION_EXACT_DUPLICATE_HOLD"
    elif target_only_conflict and partition.get("eligible_for_target_partition"):
        classification = "PARTITION_CLEARS_TARGET_ONLY"
        standing = "HOLD_UNTIL_PARTITION_COMMITTED"
        hard_hold = True
        status = "COHESION_PARTITION_OPTION_READY"
    elif target_only_conflict and partition.get("provided"):
        classification = "PARTITION_PROOF_REQUIRED"
        standing = "HOLD"
        hard_hold = True
        status = "COHESION_PARTITION_PROOF_HOLD"
    elif target_only_conflict:
        classification = "SHARED_SINK_HOLD"
        standing = "HOLD"
        hard_hold = True
        status = "COHESION_SHARED_SINK_HOLD"
    elif fuzzy_warnings:
        classification = "FUZZY_WARNING_ONLY"
        standing = "ADVISORY_CLEAR"
        hard_hold = False
        status = "COHESION_FUZZY_WARNING_ONLY"
    else:
        classification = "CLEAR"
        standing = "ADVISORY_CLEAR"
        hard_hold = False
        status = "COHESION_DUPLICATE_GUARD_CLEAR"

    exact_conflict_agents = sorted(set(conflict_agents))
    partition_eligible = bool(target_only_conflict and not identity_conflict)
    treatments = [
        _option(
            "PROCEED",
            classification in {"CLEAR", "FUZZY_WARNING_ONLY"},
            requirements=["claim/execution authority must still be obtained from existing runtime mechanisms"],
        ),
        _option(
            "JOIN",
            bool(conflicts and intended_mode == "PRIMARY"),
            requirements=["execute through athena_message_board action=join", "target active conflicting claim"],
            targets=exact_conflict_agents,
        ),
        _option(
            "PIVOT",
            bool(hard_hold or conflicts),
            requirements=["choose a non-conflicting residual and establish a fresh lawful claim"],
        ),
        _option(
            "PARTITION",
            partition_eligible,
            requirements=(
                ["structural partition proof supplied; commit a disjoint work identity before execution"]
                if partition.get("eligible_for_target_partition")
                else ["target-only collision", "partition proof with evidence refs and shared-sink coverage"]
            ),
            targets=exact_conflict_agents,
        ),
        _option(
            "REPLICA",
            bool(conflicts),
            requirements=(
                ["explicit REPLICA intent already declared", "replication_reason preserved"]
                if intended_mode == "REPLICA"
                else ["explicit mode=REPLICA", "non-empty replication_reason", "replication != independent evidence"]
            ),
            targets=exact_conflict_agents,
        ),
    ]

    value = {
        "artifact": "ATHENA.COHESION.DUPLICATE.GUARD.V1",
        "version": DUPLICATE_GUARD_VERSION,
        "status": status,
        "classification": classification,
        "standing": standing,
        "hard_hold": bool(hard_hold),
        "candidate": candidate,
        "conflicts": conflicts,
        "fuzzy_warnings": fuzzy_warnings,
        "self_relation": self_relation,
        "partition": partition,
        "treatments": treatments,
        "mata": {
            "runtime_available": False,
            "semantic_relation": "UNAVAILABLE_NOT_IN_RUNTIME",
            "semantic_issue_ref": "demeet2k/Athena#233",
            "law": "MESSAGE_BOARD_EXACT_CLASSIFICATION != MATA_SEMANTIC_CLASSIFICATION",
        },
        "shared_frontier_verified": shared_fresh,
        "git_head": head_after_sync,
        "head_before_sync": head_before_sync,
        "head_after_sync": head_after_sync,
        "read_sync_may_fast_forward": True,
        "board_write_performed": False,
        "assignment_authority": False,
        "claim_authority": False,
        "execution_authority": False,
        "independent_verification": False,
        "remote_sync": snapshot.get("remote_sync"),
        "laws": list(LAWS),
    }
    value["decision_digest"] = _decision_digest(value)
    return value


def augment_cohesion_resource(resource: Mapping[str, Any]) -> Dict[str, Any]:
    value = dict(resource or {})
    tools = list(value.get("tools") or [])
    if "athena_cohesion_duplicate_guard" not in tools:
        tools.append("athena_cohesion_duplicate_guard")
    value["tools"] = tools
    value["scope"] = str(value.get("scope") or "") + " + C3 duplicate guard"
    residual = []
    for item in value.get("residual") or []:
        if str(item) == "C3 steering tools 11-15":
            residual.append("remaining C3 steering tools 12-15")
        else:
            residual.append(item)
    value["residual"] = residual
    laws = list(value.get("laws") or [])
    for law in LAWS:
        if law not in laws:
            laws.append(law)
    value["laws"] = laws
    value["duplicate_guard_version"] = DUPLICATE_GUARD_VERSION
    value["mata_duplicate_adapter"] = "UNAVAILABLE_NOT_IN_RUNTIME"
    return value
