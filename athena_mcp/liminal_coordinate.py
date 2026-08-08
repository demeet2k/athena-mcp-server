from __future__ import annotations

import hashlib
import json
from typing import Any, Iterable, Mapping

COORDINATE_ARTIFACT = "ATHENA.LIMINAL.OPERATIONAL.COORDINATE.V2"
DELTA_ARTIFACT = "ATHENA.LIMINAL.OPERATIONAL.DELTA.V2"
TRACE_ARTIFACT = "ATHENA.LIMINAL.OPERATIONAL.TRACE.V2"

UNKNOWN = "UNKNOWN"
NOT_APPLICABLE = "N/A"

COORDINATE_AXES = (
    "repository",
    "git_head",
    "prompt_digest",
    "frontier_digest",
    "operational_basis_digest",
    "issue_pressure_digest",
    "source_bundle_digest",
    "pulse_index",
    "phase",
    "authority",
)


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _text(value: Any, name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{name} must be non-empty; use UNKNOWN or N/A explicitly")
    return text


def _pulse(value: Any) -> int | str:
    if isinstance(value, bool):
        raise ValueError("pulse_index bool is invalid")
    if isinstance(value, int):
        if 1 <= value <= 100:
            return value
        raise ValueError(
            "pulse_index integer must be in 1..100; use UNKNOWN or N/A instead of 0"
        )
    text = str(value or "").strip().upper()
    if text in {UNKNOWN, NOT_APPLICABLE}:
        return text
    raise ValueError("pulse_index must be 1..100, UNKNOWN, or N/A")


def make_liminal_coordinate(
    *,
    navigator_id: str,
    repository: str,
    git_head: str,
    prompt_digest: str,
    frontier_digest: str,
    operational_basis_digest: str,
    issue_pressure_digest: str,
    source_bundle_digest: str,
    pulse_index: int | str,
    phase: str,
    authority: str,
    observed_at: str | None = None,
    observation_refs: Iterable[str] = (),
) -> dict[str, Any]:
    """Build an exact coordinate over declared public operational axes.

    Unknown and inapplicable axes remain explicit. Navigator label, timestamps,
    and receipt references are metadata and therefore do not manufacture motion.
    This does not claim physical location, hidden model state, or private reasoning.
    """
    axes = {
        "repository": _text(repository, "repository"),
        "git_head": _text(git_head, "git_head"),
        "prompt_digest": _text(prompt_digest, "prompt_digest"),
        "frontier_digest": _text(frontier_digest, "frontier_digest"),
        "operational_basis_digest": _text(
            operational_basis_digest, "operational_basis_digest"
        ),
        "issue_pressure_digest": _text(
            issue_pressure_digest, "issue_pressure_digest"
        ),
        "source_bundle_digest": _text(
            source_bundle_digest, "source_bundle_digest"
        ),
        "pulse_index": _pulse(pulse_index),
        "phase": _text(phase, "phase").upper(),
        "authority": _text(authority, "authority").upper(),
    }
    coordinate_digest = _sha(axes)
    refs = [str(ref).strip() for ref in observation_refs if str(ref).strip()]
    return {
        "artifact": COORDINATE_ARTIFACT,
        "coordinate_id": "LC2-" + coordinate_digest[:20],
        "coordinate_digest": coordinate_digest,
        "navigator_id": _text(navigator_id, "navigator_id"),
        "observed_at": str(observed_at).strip() if observed_at is not None else None,
        "observation_refs": refs,
        "axes": axes,
        "metric": "CATEGORICAL_HAMMING_WITH_AXIS_DELTA",
        "standing": "PUBLIC_OPERATIONAL_EPISTEMIC_COORDINATE",
        "laws": [
            "COORDINATE != PRIVATE_REASONING",
            "COORDINATE != PHYSICAL_LOCATION",
            "MOVEMENT != PHYSICAL_MOVEMENT",
            "NAVIGATOR_OR_TIMESTAMP_CHANGE_ALONE != POSITION_CHANGE",
            "NO_AXIS_CHANGE => NO_LIMINAL_MOVEMENT",
            "UNKNOWN != N/A",
            "UNKNOWN != ZERO",
            "N/A != ZERO",
            "DIGEST_IDENTITY != AUTHORITY",
            "GIT_STATE != WORLD_TRUTH",
        ],
    }


def liminal_delta(
    previous: Mapping[str, Any], current: Mapping[str, Any]
) -> dict[str, Any]:
    """Measure categorical motion and return every changed axis before/after."""
    if previous.get("artifact") != COORDINATE_ARTIFACT:
        raise ValueError("previous is not a V2 liminal coordinate")
    if current.get("artifact") != COORDINATE_ARTIFACT:
        raise ValueError("current is not a V2 liminal coordinate")

    before = previous.get("axes") or {}
    after = current.get("axes") or {}
    changed = []
    delta_vector = {}
    for axis in COORDINATE_AXES:
        prior_value = before.get(axis)
        current_value = after.get(axis)
        bit = int(prior_value != current_value)
        delta_vector[axis] = bit
        if bit:
            changed.append(
                {"axis": axis, "before": prior_value, "after": current_value}
            )

    return {
        "artifact": DELTA_ARTIFACT,
        "from_coordinate_id": previous.get("coordinate_id"),
        "to_coordinate_id": current.get("coordinate_id"),
        "changed_axes": [row["axis"] for row in changed],
        "axis_deltas": changed,
        "delta_vector": delta_vector,
        "hamming_distance": len(changed),
        "stationary": not changed,
        "standing": "OBSERVED_PUBLIC_AXIS_DELTA",
        "laws": [
            "NO_AXIS_CHANGE => NO_LIMINAL_MOVEMENT",
            "METADATA_CHANGE_ALONE != POSITION_CHANGE",
            "HAMMING_DISTANCE_COUNTS_CHANGED_DECLARED_AXES_ONLY",
        ],
    }


def trace_liminal_path(
    coordinates: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    """Replay a path as exact pairwise deltas over the declared coordinate chart."""
    rows = [dict(row) for row in coordinates]
    if not rows:
        raise ValueError("coordinates must be non-empty")
    segments = [liminal_delta(rows[index - 1], rows[index]) for index in range(1, len(rows))]
    net = liminal_delta(rows[0], rows[-1]) if len(rows) > 1 else liminal_delta(rows[0], rows[0])
    return {
        "artifact": TRACE_ARTIFACT,
        "coordinate_ids": [row.get("coordinate_id") for row in rows],
        "segments": segments,
        "segment_count": len(segments),
        "total_hamming_distance": sum(row["hamming_distance"] for row in segments),
        "net_delta": net,
        "standing": "REPLAYABLE_PUBLIC_OPERATIONAL_TRACE",
    }
