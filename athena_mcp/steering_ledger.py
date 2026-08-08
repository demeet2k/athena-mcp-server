from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Iterable, Mapping

ARTIFACT = "ATHENA.STEERING.LEDGER.VALIDATION.V1"
PULSE_ARTIFACT = "ATHENA.STEERING.LEDGER.PULSE.V1"
DEFAULT_CONTRACT_PATH = "spec/STEERING_LEDGER_V1.json"

_ACTION_RE = re.compile(
    r"^\s*[-*]?\s*(?P<step>\d{4})\s+`?\[(?P<tag>[IML])\]`?\s+(?P<text>\S.*)$",
    re.MULTILINE,
)


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_contract(path: str | Path = DEFAULT_CONTRACT_PATH) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def parse_actions(body: str) -> list[dict[str, Any]]:
    actions = []
    for match in _ACTION_RE.finditer(str(body or "")):
        actions.append(
            {
                "step": int(match.group("step")),
                "tag": match.group("tag"),
                "text": match.group("text").strip(),
            }
        )
    return actions


def _comment_map(comments: Iterable[Mapping[str, Any]]) -> dict[int, Mapping[str, Any]]:
    out: dict[int, Mapping[str, Any]] = {}
    for comment in comments:
        comment_id = int(comment.get("id") or comment.get("comment_id") or 0)
        if not comment_id:
            raise ValueError("comment missing id/comment_id")
        if comment_id in out:
            raise ValueError(f"duplicate comment id: {comment_id}")
        out[comment_id] = comment
    return out


def _verification_text(body: str) -> str:
    text = re.sub(r"\s*=\s*", "=", str(body or ""))
    return re.sub(r"\s+", " ", text).strip()


def _pulse_metadata(actions: list[dict[str, Any]], comment_id: int, body_digest: str) -> list[dict[str, Any]]:
    pulses = []
    for offset in range(0, len(actions), 10):
        pulse_actions = actions[offset : offset + 10]
        if not pulse_actions:
            continue
        start = pulse_actions[0]["step"]
        pulse_index = (start - 1) // 10 + 1
        pulses.append(
            {
                "pulse_index": pulse_index,
                "step_start": start,
                "step_end": pulse_actions[-1]["step"],
                "source_comment_id": comment_id,
                "source_body_digest": body_digest,
                "tags": [row["tag"] for row in pulse_actions],
                "terminus_nonempty": bool(pulse_actions[-1]["text"].strip()),
            }
        )
    return pulses


def validate_source_bundle(
    contract: Mapping[str, Any],
    comments: Iterable[Mapping[str, Any]],
    verification_comment: Mapping[str, Any],
) -> dict[str, Any]:
    failures: list[str] = []
    source = contract["source"]
    structural = contract["structural_invariants"]
    expected_tags = list(structural["per_pulse_tags"])
    expected_blocks = list(source["blocks"])
    expected_ids = {int(block["comment_id"]) for block in expected_blocks}
    comments_by_id = _comment_map(comments)

    missing = sorted(expected_ids - set(comments_by_id))
    unexpected = sorted(set(comments_by_id) - expected_ids)
    if missing:
        failures.append("MISSING_SOURCE_COMMENTS:" + ",".join(map(str, missing)))
    if unexpected:
        failures.append("UNEXPECTED_SOURCE_COMMENTS:" + ",".join(map(str, unexpected)))

    all_actions: list[dict[str, Any]] = []
    block_receipts = []
    all_pulses = []

    for block in expected_blocks:
        comment_id = int(block["comment_id"])
        comment = comments_by_id.get(comment_id)
        if comment is None:
            continue
        body = str(comment.get("body") or "")
        body_digest = _sha_text(body)
        actions = parse_actions(body)
        expected_start = int(block["step_start"])
        expected_end = int(block["step_end"])
        expected_steps = list(range(expected_start, expected_end + 1))
        observed_steps = [row["step"] for row in actions]
        observed_tags = [row["tag"] for row in actions]

        header_markers = [
            f"LEDGER {int(block['ledger'])}/10",
            f"{expected_start:04d}",
            f"{expected_end:04d}",
        ]
        if not all(marker in body for marker in header_markers):
            failures.append(f"BLOCK_HEADER:{comment_id}")
        if observed_steps != expected_steps:
            failures.append(f"BLOCK_SEQUENCE:{comment_id}")
        if len(actions) != 100:
            failures.append(f"BLOCK_COUNT:{comment_id}:{len(actions)}")
        if len(observed_tags) == 100:
            for pulse_offset in range(0, 100, 10):
                tags = observed_tags[pulse_offset : pulse_offset + 10]
                if tags != expected_tags:
                    pulse_index = (expected_start + pulse_offset - 1) // 10 + 1
                    failures.append(f"PULSE_TAG_PATTERN:{pulse_index}")
                if not actions[pulse_offset + 9]["text"].strip():
                    pulse_index = (expected_start + pulse_offset - 1) // 10 + 1
                    failures.append(f"PULSE_TERMINUS_EMPTY:{pulse_index}")

        block_receipts.append(
            {
                "ledger": int(block["ledger"]),
                "comment_id": comment_id,
                "updated_at": comment.get("updated_at"),
                "body_digest": body_digest,
                "action_count": len(actions),
                "step_start": actions[0]["step"] if actions else None,
                "step_end": actions[-1]["step"] if actions else None,
            }
        )
        all_actions.extend(actions)
        all_pulses.extend(_pulse_metadata(actions, comment_id, body_digest))

    global_steps = [row["step"] for row in all_actions]
    expected_global_steps = list(range(1, int(structural["numbered_actions"]) + 1))
    if global_steps != expected_global_steps:
        failures.append("GLOBAL_SEQUENCE")
    if len(all_actions) != int(structural["numbered_actions"]):
        failures.append(f"GLOBAL_COUNT:{len(all_actions)}")

    tag_counts = {tag: sum(row["tag"] == tag for row in all_actions) for tag in ("I", "M", "L")}
    if tag_counts["I"] != int(structural["immediate_total"]):
        failures.append(f"GLOBAL_I_COUNT:{tag_counts['I']}")
    if tag_counts["M"] != int(structural["middle_total"]):
        failures.append(f"GLOBAL_M_COUNT:{tag_counts['M']}")
    if tag_counts["L"] != int(structural["long_total"]):
        failures.append(f"GLOBAL_L_COUNT:{tag_counts['L']}")
    if len(all_pulses) != int(structural["pulse_count"]):
        failures.append(f"PULSE_COUNT:{len(all_pulses)}")

    by_step = {row["step"]: row for row in all_actions}
    step_991 = by_step.get(991, {}).get("text", "").lower()
    step_992 = by_step.get(992, {}).get("text", "").lower()
    step_1000 = by_step.get(1000, {}).get("text", "").lower()
    if not all(token in step_991 for token in ("head", "prompt", "frontier")):
        failures.append("FINAL_RESEED_0991")
    if "verify" not in step_992:
        failures.append("FINAL_RESEED_0992")
    if not ("rehydrate" in step_1000 and "terminate" in step_1000):
        failures.append("FINAL_RESEED_1000")

    expected_verification = contract["verification"]
    verification_id = int(verification_comment.get("id") or verification_comment.get("comment_id") or 0)
    if verification_id != int(expected_verification["comment_id"]):
        failures.append(f"VERIFICATION_COMMENT_ID:{verification_id}")
    verification_body = str(verification_comment.get("body") or "")
    normalized_verification = _verification_text(verification_body)
    for marker in expected_verification["required_markers"]:
        if marker not in normalized_verification:
            failures.append("VERIFICATION_MARKER:" + marker)

    source_digest_basis = {
        "blocks": [
            {
                "comment_id": row["comment_id"],
                "updated_at": row["updated_at"],
                "body_digest": row["body_digest"],
            }
            for row in block_receipts
        ],
        "verification": {
            "comment_id": verification_id,
            "updated_at": verification_comment.get("updated_at"),
            "body_digest": _sha_text(verification_body),
        },
    }
    source_bundle_digest = hashlib.sha256(_canonical(source_digest_basis)).hexdigest()

    return {
        "artifact": ARTIFACT,
        "status": "PASS" if not failures else "HOLD",
        "failures": failures,
        "source_bundle_digest": source_bundle_digest,
        "source_repository": source["repository"],
        "source_issue": int(source["issue_number"]),
        "verification_issue": int(expected_verification["issue_number"]),
        "verification_comment_id": verification_id,
        "blocks": block_receipts,
        "pulse_count": len(all_pulses),
        "action_count": len(all_actions),
        "tag_counts": tag_counts,
        "pulses": all_pulses,
        "standing": "LEDGER_SOURCE_STRUCTURALLY_VERIFIED" if not failures else "LEDGER_SOURCE_HOLD",
        "laws": [
            "LEDGER_SOURCE != EXECUTABLE_STATE",
            "LEDGER_VERIFIED != LEDGER_EXECUTED",
            "COMMENT_IDENTITY != IMMUTABLE_CONTENT",
            "FRESH_REVALIDATION_BEFORE_PULSE_COMPILATION",
            "NUMBERED_ACTION != EXECUTION_AUTHORITY",
        ],
    }


def extract_pulse(
    contract: Mapping[str, Any],
    comments: Iterable[Mapping[str, Any]],
    pulse_index: int,
) -> dict[str, Any]:
    pulse_index = int(pulse_index)
    if not 1 <= pulse_index <= int(contract["structural_invariants"]["pulse_count"]):
        raise ValueError("pulse_index out of range")
    start = (pulse_index - 1) * 10 + 1
    end = start + 9
    block = next(
        block
        for block in contract["source"]["blocks"]
        if int(block["step_start"]) <= start <= int(block["step_end"])
    )
    comments_by_id = _comment_map(comments)
    comment_id = int(block["comment_id"])
    comment = comments_by_id.get(comment_id)
    if comment is None:
        raise ValueError(f"missing source comment for pulse {pulse_index}: {comment_id}")
    body = str(comment.get("body") or "")
    actions = [row for row in parse_actions(body) if start <= row["step"] <= end]
    if [row["step"] for row in actions] != list(range(start, end + 1)):
        raise ValueError(f"pulse {pulse_index} source sequence invalid")
    return {
        "artifact": PULSE_ARTIFACT,
        "pulse_index": pulse_index,
        "step_start": start,
        "step_end": end,
        "source_comment_id": comment_id,
        "source_updated_at": comment.get("updated_at"),
        "source_body_digest": _sha_text(body),
        "actions": actions,
        "horizon_counts": {
            "I": sum(row["tag"] == "I" for row in actions),
            "M": sum(row["tag"] == "M" for row in actions),
            "L": sum(row["tag"] == "L" for row in actions),
        },
        "standing": "CURRICULUM_BUNDLE_NOT_EXECUTION_AUTHORITY",
        "laws": [
            "PULSE_BUNDLE != SCHED_READY",
            "NUMBERED_ACTION != EXECUTION_AUTHORITY",
            "CURRENT_STATE_COMPILATION_REQUIRED_BEFORE_WORK",
        ],
    }
