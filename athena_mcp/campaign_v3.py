from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Iterable

ARTIFACT = "ATHENA.CAMPAIGN.V3"
PULSE_ARTIFACT = "ATHENA.CAMPAIGN.PULSE.V3"
BOOT_ARTIFACT = "ATHENA.AGENT.BOOT.V1"
LIMINAL_ARTIFACT = "ATHENA.LIMINAL.COORDINATE.V1"
LEDGER_SOURCE_ISSUE = 177
LEDGER_VERIFICATION_ISSUE = 185
LEDGER_VERIFICATION_COMMENT = 5228358747
TOTAL_STEPS = 1000
TOTAL_PULSES = 100
ACTIONS_PER_PULSE = 10
HORIZON_PATTERN = ("I", "I", "I", "I", "M", "M", "M", "L", "L", "L")
HORIZON_TOTALS = {"I": 4, "M": 3, "L": 3}
NONMUTATING_EFFECTS = {"READ_ONLY", "ANALYSIS", "ROUTING", "VERIFY"}
MUTATING_EFFECTS = {"MATERIAL_WRITE", "CLAIM", "PROVIDER_EFFECT"}
_ACTION_RE = re.compile(r"^\s*(\d{4})\s+`\[([IML])\]`\s+(.+?)\s*$")
_ACTION_RE_PLAIN = re.compile(r"^\s*(\d{4})\s+\[([IML])\]\s+(.+?)\s*$")


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _sha(value: Any) -> str:
    if isinstance(value, bytes):
        raw = value
    elif isinstance(value, str):
        raw = value.encode("utf-8")
    else:
        raw = _canonical(value)
    return hashlib.sha256(raw).hexdigest()


def _step_id(value: Any) -> str:
    if isinstance(value, int):
        if not 1 <= value <= TOTAL_STEPS:
            raise ValueError("step integer out of range")
        return f"{value:04d}"
    raw = str(value or "").strip()
    if not re.fullmatch(r"\d{4}", raw):
        raise ValueError(f"invalid step id: {value!r}")
    number = int(raw)
    if not 1 <= number <= TOTAL_STEPS:
        raise ValueError("step id out of range")
    return raw


def expected_step_range(pulse_index: int) -> tuple[int, int]:
    pulse_index = int(pulse_index)
    if not 1 <= pulse_index <= TOTAL_PULSES:
        raise ValueError("pulse_index must be 1..100")
    start = (pulse_index - 1) * ACTIONS_PER_PULSE + 1
    return start, start + ACTIONS_PER_PULSE - 1


def extract_actions(text: str) -> list[dict]:
    """Extract numbered [I]/[M]/[L] steering actions from ledger Markdown.

    This function recognizes both the human-readable issue form
    ``0001 `[I]` text`` and a plain ``0001 [I] text`` fixture form.
    It does not infer execution authority from the action text.
    """
    rows: list[dict] = []
    for line in str(text or "").splitlines():
        match = _ACTION_RE.match(line) or _ACTION_RE_PLAIN.match(line)
        if not match:
            continue
        step, horizon, task = match.groups()
        rows.append(
            {
                "step": _step_id(step),
                "horizon": horizon,
                "task": task.strip(),
                "source_text": line.strip(),
            }
        )
    return rows


def validate_source_contract(contract: dict) -> dict:
    if not isinstance(contract, dict):
        raise ValueError("ledger source contract is required")
    expected = {
        "source_issue": LEDGER_SOURCE_ISSUE,
        "verification_issue": LEDGER_VERIFICATION_ISSUE,
        "verification_comment_id": LEDGER_VERIFICATION_COMMENT,
        "total_steps": TOTAL_STEPS,
        "total_pulses": TOTAL_PULSES,
        "actions_per_pulse": ACTIONS_PER_PULSE,
    }
    failures = [
        key for key, value in expected.items()
        if contract.get(key) != value
    ]
    if failures:
        raise ValueError(f"ledger source contract mismatch: {sorted(failures)}")
    if str(contract.get("ledger_verified") or "").upper() != "PASS":
        raise ValueError("ledger verification receipt is not PASS")
    if contract.get("horizon_totals_per_pulse") != HORIZON_TOTALS:
        raise ValueError("ledger horizon grammar mismatch")
    return dict(contract)


def pulse_actions_from_comment(comment_body: str, pulse_index: int) -> list[dict]:
    start, end = expected_step_range(pulse_index)
    selected = [
        row for row in extract_actions(comment_body)
        if start <= int(row["step"]) <= end
    ]
    return validate_pulse_actions(pulse_index, selected)


def validate_pulse_actions(pulse_index: int, actions: Iterable[dict]) -> list[dict]:
    start, end = expected_step_range(pulse_index)
    rows = [dict(row) for row in actions]
    if len(rows) != ACTIONS_PER_PULSE:
        raise ValueError(
            f"pulse {pulse_index} requires exactly {ACTIONS_PER_PULSE} actions"
        )
    expected_steps = [f"{value:04d}" for value in range(start, end + 1)]
    steps = [_step_id(row.get("step")) for row in rows]
    if steps != expected_steps:
        raise ValueError(
            f"pulse {pulse_index} step sequence mismatch: {steps} != {expected_steps}"
        )
    horizons = [str(row.get("horizon") or "").upper() for row in rows]
    if tuple(horizons) != HORIZON_PATTERN:
        raise ValueError(
            f"pulse {pulse_index} horizon grammar mismatch: {horizons}"
        )
    normalized = []
    for row, step, horizon in zip(rows, steps, horizons):
        task = str(row.get("task") or "").strip()
        if not task:
            raise ValueError(f"pulse step {step} has no task")
        normalized.append(
            {
                **row,
                "step": step,
                "horizon": horizon,
                "task": task,
            }
        )
    return normalized


def _execution_surface(boot_packet: dict, operational_basis: dict | None) -> dict:
    execution = dict(boot_packet.get("execution_surface") or {})
    claim_exposed = bool(execution.get("claim_tool_exposed"))
    claim_operation = None
    basis_digest = None
    unclassified_write = []
    if isinstance(operational_basis, dict):
        basis_digest = operational_basis.get("basis_digest")
        for descriptor in operational_basis.get("descriptors") or []:
            if not isinstance(descriptor, dict):
                continue
            if (
                descriptor.get("capability_class") == "CLAIM_EXECUTION"
                and descriptor.get("current_exposure") is True
            ):
                claim_exposed = True
                claim_operation = descriptor.get("operation")
        for descriptor in operational_basis.get("unclassified") or []:
            if (
                isinstance(descriptor, dict)
                and descriptor.get("current_exposure") is True
                and descriptor.get("effect") not in {"READ_ONLY", None}
            ):
                unclassified_write.append(descriptor.get("operation") or "UNKNOWN")
    return {
        "claim_exposed": claim_exposed,
        "claim_operation": claim_operation,
        "basis_digest": basis_digest,
        "unclassified_write": sorted(set(unclassified_write)),
        "standing": execution.get("standing"),
        "frontier_tools": list(execution.get("frontier_tools") or []),
        "law": "ISSUE_OR_DESIGN_ASSERTION != EXPOSED_EXECUTION_TOOL",
    }


def boot_address(boot_packet: dict) -> dict:
    if not isinstance(boot_packet, dict) or boot_packet.get("artifact") != BOOT_ARTIFACT:
        raise ValueError("ATHENA.AGENT.BOOT.V1 packet is required")
    prompt = boot_packet.get("prompt") or {}
    frontier = boot_packet.get("frontier") or {}
    issue = boot_packet.get("issue_pressure") or {}
    address = {
        "git_head": prompt.get("git_head"),
        "prompt_stack_digest": prompt.get("prompt_stack_digest"),
        "frontier_source_head": frontier.get("source_head"),
        "frontier_digest": frontier.get("frontier_digest"),
        "sched_contract_digest": boot_packet.get("contract_digest"),
        "issue_pressure_digest": issue.get("digest"),
    }
    if not address["git_head"] or not address["prompt_stack_digest"]:
        raise ValueError("boot packet lacks Git/prompt ancestry")
    address["address_digest"] = _sha(address)
    return address


def liminal_coordinate(
    *,
    agent_id: str,
    quest_issue: int,
    pulse_index: int,
    stage: str,
    boot_packet: dict,
    implementation_head: str | None = None,
) -> dict:
    """Create an exact address over the *observable* ATHENA control surface.

    "Liminal" here names the seam between cognitive policy, live frontier,
    issue pressure, and implementation/runtime identity. It is not a claim to
    expose a hidden physical/model-internal coordinate.
    """
    agent_id = str(agent_id or "").strip()
    stage = str(stage or "").strip().upper()
    if not agent_id:
        raise ValueError("agent_id is required")
    if not stage:
        raise ValueError("stage is required")
    pulse_index = int(pulse_index)
    expected_step_range(pulse_index)
    address = boot_address(boot_packet)
    axes = {
        "athena_git_head": address["git_head"],
        "prompt_stack_digest": address["prompt_stack_digest"],
        "frontier_source_head": address["frontier_source_head"],
        "frontier_digest": address["frontier_digest"],
        "sched_contract_digest": address["sched_contract_digest"],
        "issue_pressure_digest": address["issue_pressure_digest"],
        "implementation_head": implementation_head,
        "quest_issue": int(quest_issue),
        "pulse_index": pulse_index,
        "stage": stage,
    }
    identity_basis = {
        "agent_id": agent_id,
        "quest_issue": int(quest_issue),
        "pulse_index": pulse_index,
    }
    coordinate_id = "LIM-" + _sha(identity_basis)[:16].upper()
    coordinate_name = f"{agent_id}.C{int(quest_issue)}.P{pulse_index:03d}"
    return {
        "artifact": LIMINAL_ARTIFACT,
        "coordinate_id": coordinate_id,
        "coordinate_name": coordinate_name,
        "agent_id": agent_id,
        "axes": axes,
        "coordinate_digest": _sha(axes),
        "observable_scope": "EXPOSED_GIT_PROMPT_FRONTIER_PRESSURE_RUNTIME_SEAMS",
        "law": "OBSERVABLE_CONTROL_COORDINATE != HIDDEN_PHYSICAL_OR_PRIVATE_MODEL_STATE",
    }


def liminal_movement(previous: dict, current: dict) -> dict:
    """Map exact state-space movement between two observable coordinates."""
    for label, value in (("previous", previous), ("current", current)):
        if not isinstance(value, dict) or value.get("artifact") != LIMINAL_ARTIFACT:
            raise ValueError(f"{label} is not an ATHENA liminal coordinate")
    if previous.get("coordinate_id") != current.get("coordinate_id"):
        raise ValueError("movement requires the same coordinate identity")
    before = previous.get("axes") or {}
    after = current.get("axes") or {}
    axis_names = sorted(set(before) | set(after))
    changed = {
        axis: {"from": before.get(axis), "to": after.get(axis)}
        for axis in axis_names
        if before.get(axis) != after.get(axis)
    }
    stable = [axis for axis in axis_names if before.get(axis) == after.get(axis)]
    basis = {
        "coordinate_id": current["coordinate_id"],
        "from_digest": previous.get("coordinate_digest"),
        "to_digest": current.get("coordinate_digest"),
        "changed": changed,
    }
    return {
        "artifact": "ATHENA.LIMINAL.MOVEMENT.V1",
        "coordinate_id": current["coordinate_id"],
        "coordinate_name": current.get("coordinate_name"),
        "movement": "STATE_TRANSITION" if changed else "NO_COORDINATE_MOTION",
        "changed_axes": changed,
        "stable_axes": stable,
        "from_digest": previous.get("coordinate_digest"),
        "to_digest": current.get("coordinate_digest"),
        "movement_digest": _sha(basis),
        "law": "MOVEMENT = OBSERVED_AXIS_DELTA; UNOBSERVED != ZERO",
    }


def _coverage(rows: list[dict]) -> dict:
    by_horizon: dict[str, dict[str, int]] = {
        horizon: {"total": 0, "satisfied": 0, "superseded": 0, "residual": 0}
        for horizon in ("I", "M", "L")
    }
    for row in rows:
        bucket = by_horizon[row["horizon"]]
        bucket["total"] += 1
        bucket[row["disposition"].lower()] += 1
    return by_horizon


def _normalize_effect(value: Any) -> str:
    effect = str(value or "UNKNOWN").strip().upper()
    allowed = NONMUTATING_EFFECTS | MUTATING_EFFECTS | {"UNKNOWN"}
    if effect not in allowed:
        raise ValueError(f"unsupported action effect: {effect}")
    return effect


def compile_pulse(
    *,
    pulse_index: int,
    actions: Iterable[dict],
    ledger_contract: dict,
    boot_packet: dict,
    satisfied_steps: Iterable[Any] = (),
    superseded_steps: Iterable[Any] = (),
    action_effects: dict[Any, str] | None = None,
    active_loop_binding: dict | None = None,
    operational_basis: dict | None = None,
) -> dict:
    """Compile one verified historical pulse into a current-state work packet.

    The compiler is routing-only. It preserves the historical action list while
    marking actions SATISFIED, SUPERSEDED, or RESIDUAL from caller-supplied
    current evidence. It never treats issue pressure or ledger prose as
    execution authority.
    """
    contract = validate_source_contract(ledger_contract)
    rows = validate_pulse_actions(pulse_index, actions)
    address = boot_address(boot_packet)
    surface = _execution_surface(boot_packet, operational_basis)

    satisfied = {_step_id(value) for value in satisfied_steps}
    superseded = {_step_id(value) for value in superseded_steps}
    if satisfied & superseded:
        raise ValueError("a step cannot be both SATISFIED and SUPERSEDED")
    pulse_step_ids = {row["step"] for row in rows}
    outside = (satisfied | superseded) - pulse_step_ids
    if outside:
        raise ValueError(
            f"disposition step is outside pulse {pulse_index}: {sorted(outside)}"
        )

    effects: dict[str, str] = {}
    for raw_key, raw_value in (action_effects or {}).items():
        step = _step_id(raw_key)
        if step not in pulse_step_ids:
            raise ValueError(f"effect step is outside pulse {pulse_index}: {step}")
        effects[step] = _normalize_effect(raw_value)

    compiled_rows = []
    for row in rows:
        step = row["step"]
        if step in satisfied:
            disposition = "SATISFIED"
        elif step in superseded:
            disposition = "SUPERSEDED"
        else:
            disposition = "RESIDUAL"
        compiled_rows.append(
            {
                **row,
                "disposition": disposition,
                "effect": effects.get(step, "UNKNOWN"),
            }
        )

    residual = [row for row in compiled_rows if row["disposition"] == "RESIDUAL"]
    next_action = residual[0] if residual else None
    holds = list(boot_packet.get("holds") or [])
    status = "PULSE_COMPILED"

    if boot_packet.get("status") not in {"BOOTSTRAPPED", "REFRESHED"}:
        holds.append("BOOT_NOT_EXECUTION_READY")
        status = "HOLD_BOOT"
    elif surface["unclassified_write"]:
        holds.append("UNCLASSIFIED_EXPOSED_WRITE")
        status = "HOLD_UNCLASSIFIED_CAPABILITY"
    elif next_action is None:
        status = "RESEED_REQUIRED" if int(pulse_index) == TOTAL_PULSES else "PULSE_SATISFIED"
    else:
        effect = next_action["effect"]
        if effect in NONMUTATING_EFFECTS:
            status = "ROUTABLE_NONMUTATING"
        elif effect in MUTATING_EFFECTS:
            if surface["claim_exposed"]:
                status = "READY_TO_BIND"
            else:
                holds.append("CLAIM_EXECUTION_NOT_EXPOSED")
                status = "HOLD_EXECUTION_AUTHORITY"
        else:
            holds.append("ACTION_EFFECT_UNCLASSIFIED")
            status = "HOLD_UNCLASSIFIED_EFFECT"

    start, end = expected_step_range(pulse_index)
    coverage = _coverage(compiled_rows)
    if {key: value["total"] for key, value in coverage.items()} != HORIZON_TOTALS:
        raise AssertionError("internal horizon coverage corruption")

    source_identity = {
        "source_issue": contract["source_issue"],
        "verification_issue": contract["verification_issue"],
        "verification_comment_id": contract["verification_comment_id"],
        "ledger_digest": contract.get("ledger_digest"),
        "verification_digest": contract.get("verification_digest"),
    }
    state_basis = {
        "source": source_identity,
        "pulse_index": int(pulse_index),
        "step_range": [start, end],
        "address": address,
        "coverage": coverage,
        "steps": [
            {
                "step": row["step"],
                "horizon": row["horizon"],
                "disposition": row["disposition"],
                "effect": row["effect"],
            }
            for row in compiled_rows
        ],
        "active_loop_binding": active_loop_binding,
        "execution_surface": surface,
        "holds": sorted(set(holds)),
        "status": status,
    }
    chain_digest = _sha(state_basis)

    if status == "PULSE_SATISFIED":
        successor = {
            "mode": "NEXT_PULSE",
            "pulse_index": int(pulse_index) + 1,
            "law": "SUCCESSOR_MUST_REHYDRATE_CURRENT_STATE",
        }
    elif status == "RESEED_REQUIRED":
        successor = {
            "mode": "REHYDRATE_RESEED",
            "pulse_index": None,
            "from_current_git": True,
            "law": "STEP_1000 != MISSION_COMPLETE",
        }
    else:
        successor = {
            "mode": "CURRENT_PULSE_RESIDUAL",
            "pulse_index": int(pulse_index),
            "next_step": next_action["step"] if next_action else None,
            "law": "BOUNDED_CYCLE_COMPLETE != MISSION_COMPLETE",
        }

    return {
        "artifact": PULSE_ARTIFACT,
        "campaign_artifact": ARTIFACT,
        "status": status,
        "pulse_index": int(pulse_index),
        "step_range": [start, end],
        "horizon_coverage": coverage,
        "source": source_identity,
        "current_address": address,
        "execution_surface": surface,
        "active_loop_binding": active_loop_binding,
        "steps": compiled_rows,
        "satisfied_steps": sorted(satisfied),
        "superseded_steps": sorted(superseded),
        "residual_steps": [row["step"] for row in residual],
        "next_action": next_action,
        "holds": sorted(set(holds)),
        "chain_digest": chain_digest,
        "successor": successor,
        "laws": [
            "LEDGER_VERIFIED != LEDGER_EXECUTED",
            "ISSUE_PRESSURE != SCHED_READY",
            "CAMPAIGN_ROUTING != EXECUTION_AUTHORITY",
            "UNEXPOSED_OPERATION => HOLD",
            "SATISFIED_OR_SUPERSEDED != ERASED",
            "PRIVATE_CHAIN_OF_THOUGHT != CAMPAIGN_TELEMETRY",
            "BOUNDED_CYCLE_COMPLETE != MISSION_COMPLETE",
        ],
    }


def compile_pulse_from_comment(
    *,
    pulse_index: int,
    comment_body: str,
    ledger_contract: dict,
    boot_packet: dict,
    **kwargs: Any,
) -> dict:
    return compile_pulse(
        pulse_index=pulse_index,
        actions=pulse_actions_from_comment(comment_body, pulse_index),
        ledger_contract=ledger_contract,
        boot_packet=boot_packet,
        **kwargs,
    )
