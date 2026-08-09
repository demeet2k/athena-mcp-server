from __future__ import annotations

from typing import Any


OBSERVER_ORGAN_ID = "continuation_raw_observer"
OBSERVER_ARTIFACT = "ATHENA.CONTINUATION.RAW.TRACE.V1"
OBSERVER_TOOL = "athena_continuation_raw_trace"
OBSERVER_LAWS = [
    "RAW_TRACE != ASSAY_CLASSIFICATION",
    "RAW_RUNTIME_FACT != BEHAVIORAL_EFFECT",
    "REHYDRATION_RECEIPT != USER_UI_EVENT",
    "MESSAGE_BOARD_EVENT != COORDINATION_SUCCESS",
    "TERMINAL_GATE_REJECTION != HUMAN_REENTRY_WITHOUT_EXPLICIT_CLASSIFIER",
    "EXACT_BYTE_DIGEST != CANONICAL_RECORD_DIGEST",
    "TRACE_DIGEST != SIGNATURE",
    "READ_ONLY_OBSERVER != CONTROLLER",
]


def _organ_manifest() -> dict[str, Any]:
    return {
        "artifact": OBSERVER_ARTIFACT,
        "tool": OBSERVER_TOOL,
        "standing": "RAW_RUNTIME_FACTS",
        "mode": "READ_ONLY",
        "source_namespaces": [
            "prompts/rehydration/*/receipts/*.json",
            "prompts/rehydration/*/events/*.json",
            "runtime/message_board/v1/events/**/*.json",
        ],
        "identity": {
            "git_head": "required current source coordinate",
            "git_blob_sha": "per tracked source file",
            "record_sha256": "exact persisted source bytes",
            "record_canonical_sha256": "canonical decoded record",
            "trace_digest": "deterministic trace identity; not a signature",
        },
        "coverage": "fail closed on dirty root, stale expected head, malformed/untracked source, or record-limit truncation",
        "authority": {
            "classification": False,
            "behavioral_effect": False,
            "causal_effect": False,
            "promotion": False,
            "mutation": False,
        },
        "laws": list(OBSERVER_LAWS),
    }


def install_continuation_raw_observer_manifest(namespace: dict[str, Any]) -> None:
    """Make the canonical runtime self-model acknowledge the registered observer.

    Tool registration is installed earlier in package initialization; V15 later
    replaces the unified-manifest builder and snapshots that builder into several
    surfaces. This post-V15 overlay keeps those projections coherent without
    creating a new runtime control plane or changing observer authority.
    """

    if namespace.get("_ATHENA_CONTINUATION_RAW_OBSERVER_MANIFEST_INSTALLED"):
        return

    from . import unified_manifest as um

    if not getattr(um, "_athena_continuation_raw_observer_manifest_installed", False):
        original_build = um.build_unified_manifest

        def build_unified_manifest_with_continuation_observer(server):
            payload = original_build(server)
            organs = dict(payload.get("organs") or {})
            organs[OBSERVER_ORGAN_ID] = _organ_manifest()
            payload["organs"] = organs
            invariants = list(payload.get("invariants") or [])
            for law in OBSERVER_LAWS:
                if law not in invariants:
                    invariants.append(law)
            payload["invariants"] = invariants
            return payload

        um.build_unified_manifest = build_unified_manifest_with_continuation_observer
        um._athena_continuation_raw_observer_manifest_installed = True

    # These modules imported/snapshotted build_unified_manifest earlier. Advance
    # every live projection to the same post-V15 self-model chart.
    from . import dispatch as dispatch_module
    from . import runtime_integrity_surface as integrity_module

    dispatch_module.build_unified_manifest = um.build_unified_manifest
    integrity_module.build_unified_manifest = um.build_unified_manifest

    namespace["_ATHENA_CONTINUATION_RAW_OBSERVER_MANIFEST_INSTALLED"] = True
