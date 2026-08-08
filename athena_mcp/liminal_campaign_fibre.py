from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

ARTIFACT = "ATHENA.LIMINAL.CAMPAIGN.FIBRE.V1"
DELTA_ARTIFACT = "ATHENA.LIMINAL.CAMPAIGN.FIBRE.DELTA.V1"
COMPILATION_ARTIFACT = "ATHENA.STEERING.PULSE.COMPILATION.V1"
ACTIVE_PARENT_SCHEMA = "ATHENA.LIMINAL.RUNTIME.v1"
UNION_CANDIDATE_SCHEMA = "ATHENA.LIMINAL.RUNTIME.v2.CANDIDATE"

AXES = (
    "git_head",
    "prompt_stack_digest",
    "frontier_digest",
    "operational_basis_digest",
    "issue_pressure_digest",
    "source_body_digest",
    "compilation_digest",
    "pulse_index",
    "phase",
    "authority",
)


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _required(value: Any, name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{name} must be non-empty")
    return text


def make_campaign_fibre(
    *,
    navigator_id: str,
    git_head: str,
    prompt_stack_digest: str,
    frontier_digest: str,
    operational_basis_digest: str,
    issue_pressure_digest: str,
    source_body_digest: str,
    compilation_digest: str,
    pulse_index: int,
    phase: str,
    authority: str,
) -> dict[str, Any]:
    """Build a task-local public campaign fibre over the liminal runtime chart.

    Only caller-supplied observable identities are encoded. The fibre is not a
    physical location, hidden model state, execution grant, or replacement for
    the parent liminal coordinate.
    """
    axes = {
        "git_head": _required(git_head, "git_head"),
        "prompt_stack_digest": _required(
            prompt_stack_digest, "prompt_stack_digest"
        ),
        "frontier_digest": _required(frontier_digest, "frontier_digest"),
        "operational_basis_digest": _required(
            operational_basis_digest, "operational_basis_digest"
        ),
        "issue_pressure_digest": _required(
            issue_pressure_digest, "issue_pressure_digest"
        ),
        "source_body_digest": _required(
            source_body_digest, "source_body_digest"
        ),
        "compilation_digest": _required(
            compilation_digest, "compilation_digest"
        ),
        "pulse_index": int(pulse_index),
        "phase": _required(phase, "phase").upper(),
        "authority": _required(authority, "authority").upper(),
    }
    if not 1 <= axes["pulse_index"] <= 100:
        raise ValueError("pulse_index must be in 1..100")

    digest = _digest(axes)
    return {
        "artifact": ARTIFACT,
        "fibre_id": "LCF-" + digest[:20],
        "fibre_digest": digest,
        "navigator_id": _required(navigator_id, "navigator_id"),
        "axes": axes,
        "parent_charts": {
            "active": ACTIVE_PARENT_SCHEMA,
            "union_candidate": UNION_CANDIDATE_SCHEMA,
            "relationship": "TASK_LOCAL_LOSSY_FIBRE",
        },
        "metric": {
            "name": "CATEGORICAL_HAMMING",
            "definition": "d_CF(x,y)=sum_i 1[x_i != y_i]",
            "scope": "CAMPAIGN_FIBRE_AXES_ONLY",
        },
        "standing": "PUBLIC_OPERATIONAL_TELEMETRY_ONLY",
        "projection_loss": [
            "RID/AID are run metadata rather than hashed position axes",
            "tree/surface/operator/object/version/time/KC144/return fields remain in the parent chart",
            "one campaign fibre may correspond to multiple parent-chart positions",
            "Hamming distance is not semantic, physical, or hidden-neural distance",
        ],
        "laws": [
            "CAMPAIGN_FIBRE != FULL_LIMINAL_COORDINATE",
            "COORDINATE != PRIVATE_REASONING",
            "MOVEMENT != PHYSICAL_LOCATION",
            "DIGEST_IDENTITY != AUTHORITY",
            "UNKNOWN != ZERO",
            "PROJECTION_LOSS_MUST_REMAIN_EXPLICIT",
        ],
    }


def campaign_fibre_delta(
    previous: Mapping[str, Any], current: Mapping[str, Any]
) -> dict[str, Any]:
    if previous.get("artifact") != ARTIFACT:
        raise ValueError("previous is not a campaign fibre")
    if current.get("artifact") != ARTIFACT:
        raise ValueError("current is not a campaign fibre")

    before = previous.get("axes") or {}
    after = current.get("axes") or {}
    changed = [axis for axis in AXES if before.get(axis) != after.get(axis)]
    return {
        "artifact": DELTA_ARTIFACT,
        "from_fibre_id": previous.get("fibre_id"),
        "to_fibre_id": current.get("fibre_id"),
        "changed_axes": changed,
        "hamming_distance": len(changed),
        "stationary": not changed,
        "standing": "OBSERVED_DECLARED_AXIS_DELTA",
        "laws": [
            "NO_AXIS_CHANGE => NO_CAMPAIGN_FIBRE_MOVEMENT",
            "NAVIGATOR_LABEL_CHANGE_ALONE != POSITION_CHANGE",
        ],
    }


def fibre_from_compilation(
    compilation: Mapping[str, Any],
    *,
    navigator_id: str,
    operational_basis_digest: str,
    issue_pressure_digest: str,
    authority: str = "ROUTING_ONLY",
) -> dict[str, Any]:
    """Project a steering-pulse compilation receipt into the campaign fibre."""
    if compilation.get("artifact") != COMPILATION_ARTIFACT:
        raise ValueError("compilation artifact mismatch")

    current = dict(compilation.get("current_address") or {})
    status = _required(compilation.get("status"), "compilation.status")
    phase = "HOLD" if status.startswith("HOLD") else "CURRENT_STATE_COMPILED"

    return make_campaign_fibre(
        navigator_id=navigator_id,
        git_head=_required(
            current.get("git_head") or current.get("H"), "current_address.git_head"
        ),
        prompt_stack_digest=_required(
            current.get("prompt_stack_digest")
            or current.get("prompt_digest"),
            "current_address.prompt_stack_digest",
        ),
        frontier_digest=_required(
            current.get("frontier_digest"), "current_address.frontier_digest"
        ),
        operational_basis_digest=operational_basis_digest,
        issue_pressure_digest=issue_pressure_digest,
        source_body_digest=_required(
            compilation.get("source_body_digest"), "source_body_digest"
        ),
        compilation_digest=_required(
            compilation.get("compilation_digest"), "compilation_digest"
        ),
        pulse_index=int(compilation.get("pulse_index") or 0),
        phase=phase,
        authority=authority,
    )
