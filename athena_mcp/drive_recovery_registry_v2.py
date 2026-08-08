from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .drive_recovery_registry import (
    LAWS as WAVE1_LAWS,
    ORGANS as WAVE1_ORGANS,
    SOURCE_ATHENA_HEAD as WAVE1_ATHENA_HEAD,
    SOURCE_MCP_HEAD as WAVE1_MCP_HEAD,
)
from .drive_recovery_wave2 import (
    FORMAL_RESIDUAL_ISSUE,
    WAVE2_ATHENA_HEAD,
    WAVE2_MCP_HEAD,
    WAVE2_ORGANS,
)

VERSION = "DRIVE.ORGAN-RECOVERY.2"
LAWS = list(WAVE1_LAWS) + [
    "SOURCE_ADDRESS != SOURCE_CONTENT_DIGEST",
    "REVISION_PIN != INDEPENDENT_WITNESS",
    "CLOCK_COORDINATE != VALID_TIME",
    "PARTIAL_IDENTITY_OVERLAP != FULL_FORMAL_EQUIVALENCE",
    "DEREFERENCE != PROMOTION",
]
ORGANS = [deepcopy(row) for row in WAVE1_ORGANS] + [deepcopy(row) for row in WAVE2_ORGANS]
_ORGAN_BY_ID = {row["organ_id"]: row for row in ORGANS}
_FRONTIER_STATUSES = {
    "RESIDUAL_HIGH_VALUE",
    "PARTIAL_CURRENT",
    "PARTIAL_OR_RESIDUAL",
    "HISTORICAL_EXECUTION_NEEDS_CURRENT_REPLAY",
    "HISTORICAL_EXECUTION_NEEDS_CURRENT_MAPPING",
    "RESIDUAL_HIGH_VALUE_SCOPED_ISSUE",
    "P0_ACTIVE_PARTIAL_CURRENT",
    "RECOVERED_PREDECESSOR_PARTIAL_CURRENT",
}


def _copy(row: Mapping[str, Any]) -> dict[str, Any]:
    return deepcopy(dict(row))


def get_organ(organ_id: str) -> dict[str, Any]:
    key = str(organ_id)
    if key not in _ORGAN_BY_ID:
        raise ValueError(f"recovered organ not found: {key}")
    return {"version": VERSION, "organ": _copy(_ORGAN_BY_ID[key])}


def list_organs(status: str | None = None, family: str | None = None, query: str | None = None, limit: int = 100) -> dict[str, Any]:
    rows = list(ORGANS)
    if status:
        rows = [r for r in rows if r["status"] == str(status)]
    if family:
        f = str(family).lower()
        rows = [r for r in rows if f in r["family"].lower()]
    if query:
        q = str(query).lower().strip()
        if q:
            def haystack(r: Mapping[str, Any]) -> str:
                source = r.get("source") or {}
                values = [
                    r.get("organ_id", ""), r.get("family", ""), r.get("status", ""),
                    source.get("title", ""), source.get("drive_file_id", ""), source.get("revision_id", ""),
                    " ".join(r.get("semantic_signature") or []),
                    " ".join(r.get("residuals") or []),
                    " ".join(r.get("current_runtime_refs") or []),
                ]
                return " ".join(str(x) for x in values).lower()
            rows = [r for r in rows if q in haystack(r)]
    cap = max(1, min(int(limit), 100))
    rows = sorted(rows, key=lambda r: (-int(r["priority"]), r["organ_id"]))[:cap]
    return {
        "version": VERSION,
        "count": len(rows),
        "organs": [_copy(r) for r in rows],
        "law": "registry search is a recovery index; a hit or miss does not by itself establish semantic equivalence, capability absence, or current verification",
    }


def residual_frontier(limit: int = 10, include_theory: bool = False) -> dict[str, Any]:
    allowed = set(_FRONTIER_STATUSES)
    if include_theory:
        allowed.add("THEORY_SOURCE_NOT_RUNTIME_REQUIREMENT")
    rows = [r for r in ORGANS if r["status"] in allowed and r.get("residuals")]
    rows = sorted(rows, key=lambda r: (-int(r["priority"]), r["organ_id"]))
    cap = max(1, min(int(limit), 50))
    return {
        "version": VERSION,
        "source_heads": {
            "wave1_athena": WAVE1_ATHENA_HEAD,
            "wave1_mcp": WAVE1_MCP_HEAD,
            "wave2_athena": WAVE2_ATHENA_HEAD,
            "wave2_mcp": WAVE2_MCP_HEAD,
        },
        "count": min(len(rows), cap),
        "frontier": [
            {
                "organ_id": r["organ_id"],
                "family": r["family"],
                "status": r["status"],
                "priority": r["priority"],
                "source": deepcopy(r["source"]),
                "residuals": deepcopy(r["residuals"]),
                "boundary": r["boundary"],
            }
            for r in rows[:cap]
        ],
        "law": "frontier priority is a recovery/development heuristic, not autonomous authority to mutate, execute, or promote",
    }


def holoaddress_for(organ_id: str) -> dict[str, Any]:
    row = get_organ(organ_id)["organ"]
    source = dict(row.get("source") or {})
    revision = source.get("revision_id")
    version_pin: dict[str, Any]
    if revision is None:
        version_pin = {"status": "UNPINNED", "revision_id": None}
    else:
        version_pin = {"status": "PINNED", "revision_id": str(revision)}
    return {
        "version": VERSION,
        "holoaddress": {
            "RootID": "ATHENA.GOOGLE-DOCS.ORGAN-RECOVERY.V2",
            "ObjectClass": row.get("family"),
            "VersionPin": version_pin,
            "LocalAddress": row["organ_id"],
            "LookupKey": {
                "drive_file_id": source.get("drive_file_id"),
                "source_title": source.get("title"),
                "semantic_signature": deepcopy(row.get("semantic_signature") or []),
            },
            "DigestLocator": {
                "status": "UNCOMPUTED",
                "digest": None,
                "reason": "the recovery registry pinned source identity/revision but did not freeze a content digest of the Drive manifestation",
            },
            "WitnessPacket": {
                "classification": row.get("status"),
                "current_runtime_refs": deepcopy(row.get("current_runtime_refs") or []),
                "boundary": row.get("boundary"),
                "standing": "RECOVERY_LINEAGE_NOT_INDEPENDENT_CURRENT_VERIFICATION",
            },
            "CompressionSeed": {
                "semantic_signature": deepcopy(row.get("semantic_signature") or []),
                "residuals": deepcopy(row.get("residuals") or []),
            },
            "ReentryInstructions": [
                "establish fresh Athena and MCP Git heads before consequential work",
                "fetch the exact Drive source and pinned revision when connector/runtime supports revision fetch; otherwise declare the revision retrieval limitation",
                "compare the semantic signature against current code/tools/resources and known aliases before declaring a capability missing",
                "treat historical execution/test claims as historical until replayed at the current implementation head",
                "compute and implement only the remaining residual delta",
                "return reusable observations/tests/repairs to Git with ancestry and claim boundary",
            ],
        },
        "law": "HoloAddress is a read-only dereference/reentry packet; it is not source bytes, a content digest, evidence authority, execution permission, or prompt promotion",
    }


class DriveRecoveryRegistryRuntime:
    def describe(self) -> dict[str, Any]:
        status_counts: dict[str, int] = {}
        pinned = 0
        for row in ORGANS:
            status_counts[row["status"]] = status_counts.get(row["status"], 0) + 1
            if (row.get("source") or {}).get("revision_id") is not None:
                pinned += 1
        return {
            "version": VERSION,
            "source_heads": {
                "wave1_athena": WAVE1_ATHENA_HEAD,
                "wave1_mcp": WAVE1_MCP_HEAD,
                "wave2_athena": WAVE2_ATHENA_HEAD,
                "wave2_mcp": WAVE2_MCP_HEAD,
            },
            "organ_count": len(ORGANS),
            "revision_pinned_count": pinned,
            "status_counts": dict(sorted(status_counts.items())),
            "laws": list(LAWS),
            "formal_residual_issue": FORMAL_RESIDUAL_ISSUE,
            "boundary": "read-only recovered lineage/dereference index; no tool in this surface mutates Drive, Git authority, runtime execution state, or prompt activation",
        }

    def list(self, **kwargs: Any) -> dict[str, Any]:
        return list_organs(**kwargs)

    def get(self, organ_id: str) -> dict[str, Any]:
        return get_organ(organ_id)

    def frontier(self, limit: int = 10, include_theory: bool = False) -> dict[str, Any]:
        return residual_frontier(limit=limit, include_theory=include_theory)

    def holoaddress(self, organ_id: str) -> dict[str, Any]:
        return holoaddress_for(organ_id)
