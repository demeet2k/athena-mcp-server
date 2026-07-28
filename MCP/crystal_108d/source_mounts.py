"""Bounded KC144 source-mount consumer for the Athena MCP runtime.

The control repository owns the source locks. This module consumes one frozen,
content-addressed snapshot and exposes deterministic coordinate resolution.
It performs no Google Drive requests and makes no live, deployment, promotion,
or internal-cold-recall claims.
"""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from typing import Any


DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "w11_source_mounts.json"
SCHEMA = "athena.runtime-source-mounts/v1"


class SourceMountSnapshotError(RuntimeError):
    """Raised when a frozen source-mount snapshot violates its contract."""


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SourceMountSnapshotError("source-mount snapshot must be a JSON object")
    return value


def _literal_digest(literal: str) -> str:
    return sha256(literal.encode("utf-8")).hexdigest()


class FrozenSourceMounts:
    """Verified, immutable-in-practice view of the W11 source coordinates."""

    def __init__(
        self,
        snapshot: dict[str, Any],
        by_rid: dict[str, dict[str, Any]],
        by_aid: dict[str, dict[str, Any]],
    ) -> None:
        self.snapshot = snapshot
        self.by_rid = by_rid
        self.by_aid = by_aid

    @classmethod
    def load(cls, path: Path = DATA_PATH) -> "FrozenSourceMounts":
        snapshot = _load_json(path)
        if snapshot.get("schema") != SCHEMA:
            raise SourceMountSnapshotError(
                f"unexpected schema: {snapshot.get('schema')!r}"
            )

        mounts = snapshot.get("mounts")
        if not isinstance(mounts, list) or not mounts:
            raise SourceMountSnapshotError("snapshot must contain source mounts")

        by_rid: dict[str, dict[str, Any]] = {}
        by_aid: dict[str, dict[str, Any]] = {}
        for mount in mounts:
            if not isinstance(mount, dict):
                raise SourceMountSnapshotError("each mount must be an object")
            rid = mount.get("rid")
            aid = mount.get("aid")
            if not isinstance(rid, str) or not rid:
                raise SourceMountSnapshotError("mount RID is required")
            if not isinstance(aid, str) or not aid:
                raise SourceMountSnapshotError(f"{rid}: AID is required")
            if rid in by_rid:
                raise SourceMountSnapshotError(f"duplicate RID: {rid}")
            if aid in by_aid:
                raise SourceMountSnapshotError(f"duplicate AID: {aid}")

            source = mount.get("source")
            if not isinstance(source, dict):
                raise SourceMountSnapshotError(f"{rid}: source object is required")
            literal = source.get("literal")
            expected = source.get("literal_sha256")
            if not isinstance(literal, str) or not isinstance(expected, str):
                raise SourceMountSnapshotError(
                    f"{rid}: literal and literal_sha256 are required"
                )
            actual = _literal_digest(literal)
            if actual != expected:
                raise SourceMountSnapshotError(
                    f"{rid}: literal digest mismatch: {actual} != {expected}"
                )

            locator = source.get("range")
            if (
                not isinstance(locator, dict)
                or not isinstance(locator.get("start"), int)
                or not isinstance(locator.get("end"), int)
                or locator["start"] >= locator["end"]
                or locator.get("interval") != "half-open"
            ):
                raise SourceMountSnapshotError(
                    f"{rid}: invalid half-open source range"
                )

            by_rid[rid] = mount
            by_aid[aid] = mount

        boundaries = snapshot.get("boundaries", {})
        prohibited_claims = (
            "raw_docs_body_committed",
            "live_provider_checked_by_runtime",
            "internal_cold_replay_claimed",
            "persistent_deployment_claimed",
            "promotion_claimed",
            "hidden_weights_inspected",
        )
        for name in prohibited_claims:
            if boundaries.get(name) is not False:
                raise SourceMountSnapshotError(
                    f"bounded snapshot requires {name}=false"
                )

        m09 = by_rid.get("rid:kc144:gid141:m09:path-signature")
        if m09:
            route = m09.get("route_identity", {})
            if (
                route.get("semantic_equivalence") is not True
                or route.get("route_equivalence") is not False
                or route.get("return_unique") is not False
            ):
                raise SourceMountSnapshotError(
                    "M09 must preserve semantic equivalence without route collapse"
                )
            fingerprints = route.get("route_fingerprints", {})
            if len(set(fingerprints.values())) != len(fingerprints):
                raise SourceMountSnapshotError(
                    "M09 route fingerprints must remain distinct"
                )

        return cls(snapshot=snapshot, by_rid=by_rid, by_aid=by_aid)

    def status(self) -> dict[str, Any]:
        control = self.snapshot["control"]
        runtime_base = self.snapshot["runtime_base"]
        return {
            "status": "READY_FROZEN_NOT_LIVE_VERIFIED",
            "schema": self.snapshot["schema"],
            "snapshot_id": self.snapshot["snapshot_id"],
            "mount_count": len(self.by_rid),
            "rids": sorted(self.by_rid),
            "control": {
                "repository": control["repository"],
                "commit": control["commit"],
                "imports_lock_blob": control["imports_lock"]["blob_sha"],
                "return_receipt_blob": control["return_receipt"]["blob_sha"],
                "return_receipt_verdict": control["return_receipt"]["verdict"],
            },
            "runtime_base": {
                "repository": runtime_base["repository"],
                "commit": runtime_base["commit"],
                "published_oci": runtime_base["published_oci"],
                "published_oci_changed": runtime_base["published_oci_changed"],
            },
            "boundaries": deepcopy(self.snapshot["boundaries"]),
        }

    def resolve(self, identifier: str) -> dict[str, Any]:
        mount = self.by_rid.get(identifier) or self.by_aid.get(identifier)
        if mount is None:
            return {
                "status": "INVALID_ADDRESS",
                "identifier": identifier,
                "accepted_coordinate_classes": ["RID", "AID"],
            }
        return {
            "status": "RESOLVED_FROZEN_SOURCE_MOUNT",
            "identifier": identifier,
            "rid": mount["rid"],
            "aid": mount["aid"],
            "station": mount["station"],
            "role": mount["role"],
            "control_object": deepcopy(mount["control_object"]),
            "control_routes": deepcopy(mount["control_routes"]),
            "route_identity": deepcopy(mount["route_identity"]),
            "source_digest": mount["source"]["literal_sha256"],
            "live_provider_checked": False,
        }

    def return_to_source(self, identifier: str) -> dict[str, Any]:
        mount = self.by_rid.get(identifier) or self.by_aid.get(identifier)
        if mount is None:
            return {
                "status": "INVALID_ADDRESS",
                "identifier": identifier,
                "accepted_coordinate_classes": ["RID", "AID"],
            }

        source = mount["source"]
        receipt = self.snapshot["control"]["return_receipt"]
        return {
            "status": "SOURCE_OCCURRENCE_RESOLVED",
            "rid": mount["rid"],
            "aid": mount["aid"],
            "provider": source["provider"],
            "file_id": source["file_id"],
            "revision_id": source["revision_id"],
            "tab_id": source["tab_id"],
            "range": deepcopy(source["range"]),
            "literal": source["literal"],
            "literal_sha256": source["literal_sha256"],
            "return_locator": source["return_locator"],
            "return_grade": "R3-protocol",
            "witnessed_by_control_receipt": receipt["verdict"],
            "control_receipt_blob": receipt["blob_sha"],
            "live_provider_checked": False,
            "requires_live_provider_check_for_currentness": True,
            "internal_cold_recall_claimed": False,
        }


def _render(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)


def register_source_mounts(mcp: Any) -> None:
    """Register deterministic source-mount tools and a status resource."""

    registry = FrozenSourceMounts.load()

    @mcp.tool()
    def athena_source_mount_status() -> str:
        """Report the frozen W11 source-mount snapshot and its claim boundary."""
        return _render(registry.status())

    @mcp.tool()
    def resolve_athena_source_mount(identifier: str) -> str:
        """Resolve an exact KC144 RID or AID without fuzzy substitution."""
        return _render(registry.resolve(identifier))

    @mcp.tool()
    def return_athena_source_mount(identifier: str) -> str:
        """Return a frozen source occurrence; does not perform a live Drive check."""
        return _render(registry.return_to_source(identifier))

    @mcp.resource("athena://source-mounts")
    def source_mount_resource() -> str:
        """Expose the verified frozen mount snapshot and explicit boundaries."""
        return _render(
            {
                "status": registry.status(),
                "mounts": [
                    registry.resolve(rid) for rid in sorted(registry.by_rid)
                ],
            }
        )
