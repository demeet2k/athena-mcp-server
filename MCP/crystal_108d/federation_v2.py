"""Frozen Athena federation v2 consumer for the MCP runtime.

The control plane owns identities and edges.  This module consumes an immutable
snapshot of that control-plane graph; it never promotes runtime output back
into the graph.  Exact v2 lookup is attempted first.  Registered legacy MCP
resources remain available through an explicit, provenance-bearing fallback.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Iterable


SNAPSHOT_DIRECTORY = Path(__file__).resolve().parent.parent / "data" / "athena_federation_v2"
V2_RUNTIME = "athena-federation-v2"
V1_RUNTIME = "athena-108d-v1"
ACTIVE = "active"

# These resources already exist in the legacy server.  Keeping the allow-list
# explicit prevents a failed v2 lookup from becoming an unsafe fuzzy match.
LEGACY_RESOURCE_URIS = frozenset(
    {
        "athena://status",
        "athena://board",
        "athena://loop",
        "athena://crystal-108d",
        "athena://dimensional-ladder",
        "athena://organ-atlas",
        "athena://live-helm",
        "athena://conservation",
        "athena://mobius-lenses",
        "athena://stage-ladder",
        "athena://angel",
        "athena://brain-network",
        "athena://live-cell",
        "athena://emergence",
        "athena://hologram-reading",
        "athena://hologram-rosetta",
        "athena://angel-geometry",
        "athena://inverse-seed",
        "athena://inverse-octave",
        "athena://mycelium",
        "athena://node-registry",
        "athena://guild-hall",
        "athena://quest-board",
        "athena://crystal-coordinates",
    }
)


class FederationSnapshotError(RuntimeError):
    """Raised when the vendored lock differs from its immutable receipt."""


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _digest(value: Any) -> str:
    return sha256(_canonical_bytes(value)).hexdigest()


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _repository_portals(
    federation: dict[str, Any],
    lock: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    control = lock["control"]
    resources: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []

    for item in lock["repositories"]:
        rid = item["rid"]
        vid = item["vid"]
        locator = (
            f"github://{item['github']}@{item['commit']}/{item['contract_path']}"
        )
        resources.append(
            {
                "rid": rid,
                "vid": vid,
                "kind": "repository",
                "kernel": (
                    f"{item['role']} repository in state {item['state']}; "
                    f"authority is bounded to {item['authority_domain']}."
                ),
                "coordinates": [
                    f"athena://resource/{rid}@{vid}",
                    locator,
                    *item.get("legacy_addresses", []),
                ],
                "role": item["role"],
                "state": item["state"],
                "authority_domain": item["authority_domain"],
                "contract_commit": item["commit"],
                "base_commit": item["base_commit"],
                "legacy_id": item.get("legacy_id"),
            }
        )

        key = rid.removeprefix("athena.repo.").replace(".", "-")
        forward_id = f"edge.{key}-to-control"
        reverse_id = f"edge.control-to-{key}"
        defects = item["defects"]
        endpoint = {"rid": rid, "vid": vid}
        control_endpoint = {"rid": control["rid"], "vid": control["vid"]}
        edges.extend(
            [
                {
                    "eid": forward_id,
                    "source": endpoint,
                    "target": control_endpoint,
                    "type": "declares_to_control_plane",
                    "operator": "manifest_publish",
                    "domain": "repository",
                    "codomain": "repository",
                    "preconditions": [
                        "local manifest readable",
                        "control schema commit pinned",
                    ],
                    "carrier": (
                        "Athena Repo Manifest v2 plus immutable "
                        "control-plane import"
                    ),
                    "preserved": [
                        "repository identity",
                        "role",
                        "authority boundary",
                        "base commit witness",
                    ],
                    "changed": ["repository-local state to federation proposal"],
                    "lost": [],
                    "defects": defects,
                    "witnesses": [locator],
                    "authority": "derived",
                    "return": {
                        "class": "compensated",
                        "edge_id": reverse_id,
                        "required_carry": [
                            "control commit",
                            "local manifest",
                            "route receipt",
                        ],
                        "allowed_defect": defects,
                    },
                    "status": ACTIVE,
                    "version": "2.0.0",
                },
                {
                    "eid": reverse_id,
                    "source": control_endpoint,
                    "target": endpoint,
                    "type": "mounts_repository",
                    "operator": "pinned_manifest_resolve",
                    "domain": "repository",
                    "codomain": "repository",
                    "preconditions": [
                        "repository contract commit pinned by federation"
                    ],
                    "carrier": "Git commit plus repository manifest",
                    "preserved": [
                        "repository identity",
                        "role",
                        "authority boundary",
                    ],
                    "changed": ["federation address to repository occurrence"],
                    "lost": [],
                    "defects": defects,
                    "witnesses": [locator],
                    "authority": "derived",
                    "return": {
                        "class": "compensated",
                        "edge_id": forward_id,
                        "required_carry": ["repository commit", "manifest CID"],
                        "allowed_defect": defects,
                    },
                    "status": ACTIVE,
                    "version": "2.0.0",
                },
            ]
        )
    return resources, edges


@dataclass(frozen=True)
class FrozenFederation:
    """Loaded and verified federation graph."""

    snapshot: dict[str, Any]
    release_candidate: dict[str, Any]
    cold_replay: dict[str, Any]
    federation: dict[str, Any]
    lock: dict[str, Any]
    resources: tuple[dict[str, Any], ...]
    edges: tuple[dict[str, Any], ...]
    identifiers: dict[str, dict[str, Any]]
    edge_by_id: dict[str, dict[str, Any]]
    graph_digest: str

    @classmethod
    def load(cls, data_root: Path = SNAPSHOT_DIRECTORY) -> "FrozenFederation":
        snapshot = _load_json(data_root / "snapshot.json")
        release_candidate = _load_json(data_root / "release-candidate.json")
        cold_replay = _load_json(data_root / "p05-cold-replay.json")
        federation = _load_json(data_root / "federation.json")
        lock = _load_json(data_root / "repositories.lock.json")
        base_edges = _load_jsonl(data_root / "edges.jsonl")
        repo_resources, repo_edges = _repository_portals(federation, lock)
        resources = tuple([*federation["resources"], *repo_resources])
        edges = tuple([*base_edges, *repo_edges])

        identifiers: dict[str, dict[str, Any]] = {}
        versions: set[tuple[str, str]] = set()
        for resource in resources:
            key = (resource["rid"], resource["vid"])
            if key in versions:
                raise FederationSnapshotError(f"duplicate resource version: {key}")
            versions.add(key)
            for identifier in (
                resource["rid"],
                f"athena://resource/{resource['rid']}@{resource['vid']}",
                *resource.get("coordinates", []),
            ):
                previous = identifiers.get(identifier)
                if previous is not None and previous != resource:
                    raise FederationSnapshotError(
                        f"ambiguous exact identifier: {identifier}"
                    )
                identifiers[identifier] = resource

        graph_value = {
            "resources": sorted(f"{rid}@{vid}" for rid, vid in versions),
            "edges": list(edges),
        }
        graph_digest = f"sha256:{_digest(graph_value)}"
        observed = {
            "release": federation["release"],
            "resource_versions": len(versions),
            "identifiers": len(identifiers),
            "edges": len(edges),
            "graph_digest": graph_digest,
        }
        expected = {
            key: snapshot[key]
            for key in (
                "release",
                "resource_versions",
                "identifiers",
                "edges",
                "graph_digest",
            )
        }
        if observed != expected:
            raise FederationSnapshotError(
                f"snapshot receipt mismatch: expected={expected!r} observed={observed!r}"
            )
        if (
            release_candidate.get("release_id")
            != snapshot.get("release_candidate")
            or release_candidate.get("control_plane", {}).get(
                "canonical_parent_head"
            )
            != snapshot.get("canonical_parent_head")
            or release_candidate.get("selected_contract_lineage", {}).get(
                "name"
            )
            != snapshot.get("selected_contract_lineage")
            or release_candidate.get("selected_contract_lineage", {}).get(
                "release"
            )
            != federation["release"]
        ):
            raise FederationSnapshotError(
                "P05 release-candidate identity or selected lineage mismatch"
            )

        expected_cold_replay = snapshot.get("cold_replay", {})
        if (
            cold_replay.get("phase_verdict")
            != expected_cold_replay.get("phase_verdict")
            or cold_replay.get("canonical_replay", {}).get("passed")
            != expected_cold_replay.get("canonical_passed")
            or cold_replay.get("alternate_replay", {}).get("passed")
            != expected_cold_replay.get("alternate_passed")
            or release_candidate.get("promotion_ready") is not False
            or snapshot.get("promotion_ready") is not False
        ):
            raise FederationSnapshotError(
                "P05 cold-replay or promotion boundary mismatch"
            )

        edge_by_id = {edge["eid"]: edge for edge in edges}
        if len(edge_by_id) != len(edges):
            raise FederationSnapshotError("duplicate edge identity")
        for edge in edges:
            reverse_id = edge.get("return", {}).get("edge_id")
            if edge["status"] == ACTIVE and reverse_id:
                reverse = edge_by_id.get(reverse_id)
                if (
                    reverse is None
                    or reverse.get("source") != edge.get("target")
                    or reverse.get("target") != edge.get("source")
                ):
                    raise FederationSnapshotError(
                        f"invalid return edge for {edge['eid']}: {reverse_id}"
                    )

        return cls(
            snapshot=snapshot,
            release_candidate=release_candidate,
            cold_replay=cold_replay,
            federation=federation,
            lock=lock,
            resources=resources,
            edges=edges,
            identifiers=identifiers,
            edge_by_id=edge_by_id,
            graph_digest=graph_digest,
        )

    def provenance(self, runtime: str = V2_RUNTIME) -> dict[str, Any]:
        return {
            "runtime": runtime,
            "federation_release": self.federation["release"],
            "graph_digest": self.graph_digest,
            "control_repository": self.snapshot["source_repository"],
            "control_commit": self.snapshot["source_commit"],
            "release_candidate": self.snapshot["release_candidate"],
            "selected_contract_lineage": self.snapshot[
                "selected_contract_lineage"
            ],
            "cold_replay": self.snapshot["cold_replay"]["phase_verdict"],
            "promotion_ready": False,
            "fallback_enabled": True,
        }

    def status(self) -> dict[str, Any]:
        return {
            "verdict": "READY",
            **self.provenance(),
            "resource_versions": len(self.resources),
            "identifiers": len(self.identifiers),
            "edges": len(self.edges),
            "legacy_resources": len(LEGACY_RESOURCE_URIS),
            "promotion_authority": False,
        }

    def cutover_receipt(
        self,
        *,
        observed_at: str = "2026-07-27T04:00:00Z",
    ) -> dict[str, Any]:
        """Emit deterministic v2, fallback, return, and rollback evidence."""
        forward = self.route(
            "athena.repo.q-shrink",
            "athena.runtime.route-compiler",
            query_id="p06-runtime-forward-return",
            created_at=observed_at,
        )
        fallback = self.resolve("athena://crystal-108d")
        rollback = {
            "class": "exact-predecessor-selection",
            "runtime": V1_RUNTIME,
            "repository": "demeet2k/athena-mcp-server",
            "predecessor_commit": "0ee038011295873ba037a3cac25de18544439293",
            "trigger": [
                "snapshot verification failure",
                "v2 identity resolution regression",
                "missing exact return plan",
                "host deployment rejection",
            ],
            "action": (
                "Select the predecessor runtime; preserve this proposal and "
                "its receipts without rewriting history."
            ),
        }
        checks = {
            "v2_forward": forward.get("verdict") == "FOUND",
            "v2_return": bool(forward.get("return_plan")),
            "v1_fallback": (
                fallback.get("verdict") == "FOUND_LEGACY"
                and fallback.get("fallback_used") is True
            ),
            "promotion_boundary": self.snapshot.get("promotion_ready") is False,
        }
        body = {
            "schema": "athena.runtime-cutover-receipt/v2",
            "observed_at": observed_at,
            "verdict": "PASS_LOCAL_NOT_DEPLOYED"
            if all(checks.values())
            else "HOLD",
            "checks": checks,
            "forward_return": forward,
            "v1_fallback": fallback,
            "rollback": rollback,
            "deployment_witness": None,
            "promotion_claimed": False,
            **self.provenance(),
        }
        return {
            "receipt_id": f"runtime-cutover:sha256:{_digest(body)}",
            **body,
        }

    def resolve(
        self,
        identifier: str,
        *,
        allow_v1_fallback: bool = True,
    ) -> dict[str, Any]:
        resource = self.identifiers.get(identifier)
        if resource is not None:
            return {
                "verdict": "FOUND",
                "answered_by": V2_RUNTIME,
                "fallback_used": False,
                "identifier": identifier,
                "resource": resource,
                **self.provenance(),
            }
        if allow_v1_fallback and identifier in LEGACY_RESOURCE_URIS:
            return {
                "verdict": "FOUND_LEGACY",
                "answered_by": V1_RUNTIME,
                "fallback_used": True,
                "identifier": identifier,
                "resource": {"uri": identifier, "kind": "legacy_mcp_resource"},
                "defects": [
                    "identifier is outside the frozen v2 graph",
                    "legacy resource has no v2 return-path guarantee",
                ],
                **self.provenance(V1_RUNTIME),
            }
        return {
            "verdict": "INVALID_ADDRESS",
            "answered_by": V2_RUNTIME,
            "fallback_used": False,
            "identifier": identifier,
            "defects": [
                "identifier is not an exact v2 identity or registered v1 resource"
            ],
            **self.provenance(),
        }

    def route(
        self,
        source_identifier: str,
        target_identifier: str,
        *,
        query_id: str = "query.mcp",
        require_return: bool = True,
        allow_v1_fallback: bool = True,
        created_at: str | None = None,
    ) -> dict[str, Any]:
        source = self.resolve(
            source_identifier, allow_v1_fallback=allow_v1_fallback
        )
        target = self.resolve(
            target_identifier, allow_v1_fallback=allow_v1_fallback
        )
        if source["verdict"] == "FOUND_LEGACY" or target["verdict"] == "FOUND_LEGACY":
            return {
                "verdict": "V1_FALLBACK_REQUIRED",
                "answered_by": V1_RUNTIME,
                "fallback_used": True,
                "source": source_identifier,
                "target": target_identifier,
                "defects": [
                    "v1 resources remain callable but are not traversed as v2 graph nodes"
                ],
                **self.provenance(V1_RUNTIME),
            }
        if source["verdict"] != "FOUND" or target["verdict"] != "FOUND":
            return {
                "verdict": "INVALID_ADDRESS",
                "answered_by": V2_RUNTIME,
                "fallback_used": False,
                "source": source_identifier,
                "target": target_identifier,
                "defects": [
                    "source or target is not an exact registered identity"
                ],
                **self.provenance(),
            }

        adjacency: dict[str, list[dict[str, Any]]] = {}
        for edge in self.edges:
            if edge.get("status") != ACTIVE:
                continue
            if not edge.get("preconditions") or not edge.get("carrier"):
                continue
            if not edge.get("witnesses"):
                continue
            if require_return:
                reverse = self.edge_by_id.get(
                    edge.get("return", {}).get("edge_id")
                )
                if (
                    reverse is None
                    or reverse.get("status") != ACTIVE
                    or reverse.get("source") != edge.get("target")
                    or reverse.get("target") != edge.get("source")
                ):
                    continue
            adjacency.setdefault(edge["source"]["rid"], []).append(edge)

        source_rid = source["resource"]["rid"]
        target_rid = target["resource"]["rid"]
        queue = deque([(source_rid, [])])
        seen = {source_rid}
        path: list[dict[str, Any]] | None = None
        while queue:
            node, candidate = queue.popleft()
            if node == target_rid:
                path = candidate
                break
            for edge in sorted(
                adjacency.get(node, []), key=lambda item: item["eid"]
            ):
                neighbour = edge["target"]["rid"]
                if neighbour in seen:
                    continue
                seen.add(neighbour)
                queue.append((neighbour, [*candidate, edge]))

        if path is None:
            return {
                "verdict": "UNMAPPED",
                "answered_by": V2_RUNTIME,
                "fallback_used": False,
                "source": source_rid,
                "target": target_rid,
                "defects": ["no active witness/return-admissible v2 path"],
                **self.provenance(),
            }

        body = {
            "query_id": query_id,
            "source": source_rid,
            "target": target_rid,
            "hops": [edge["eid"] for edge in path],
            "return_plan": [
                edge["return"]["edge_id"] for edge in reversed(path)
            ],
            "preserved": sorted(
                {value for edge in path for value in edge["preserved"]}
            ),
            "lost": sorted({value for edge in path for value in edge["lost"]}),
            "defects": sorted(
                {value for edge in path for value in edge["defects"]}
            ),
            "witnesses": sorted(
                {value for edge in path for value in edge["witnesses"]}
            ),
            "created_at": created_at or datetime.now(timezone.utc).isoformat(),
            "answered_by": V2_RUNTIME,
            "fallback_used": False,
            **self.provenance(),
        }
        return {
            "route_id": f"route:sha256:{_digest(body)}",
            "verdict": "FOUND" if not body["lost"] else "PARTIAL",
            **body,
        }


_consumer: FrozenFederation | None = None


def get_federation() -> FrozenFederation:
    """Load once per server process after verifying the frozen receipt."""
    global _consumer
    if _consumer is None:
        _consumer = FrozenFederation.load()
    return _consumer


def register_federation_v2(mcp: Any) -> None:
    """Register v2 tools/resources without modifying the legacy surface."""

    @mcp.tool()
    def athena_federation_status() -> dict[str, Any]:
        """Report the frozen graph, source commit, digest, and fallback state."""
        return get_federation().status()

    @mcp.tool()
    def resolve_athena_identity(
        identifier: str, allow_v1_fallback: bool = True
    ) -> dict[str, Any]:
        """Resolve one exact v2 identity, or an explicitly registered v1 URI."""
        return get_federation().resolve(
            identifier, allow_v1_fallback=allow_v1_fallback
        )

    @mcp.tool()
    def route_athena_federation(
        source: str,
        target: str,
        require_return: bool = True,
        allow_v1_fallback: bool = True,
    ) -> dict[str, Any]:
        """Compile a witnessed cross-repository route and its return plan."""
        return get_federation().route(
            source,
            target,
            require_return=require_return,
            allow_v1_fallback=allow_v1_fallback,
        )

    @mcp.tool()
    def athena_federation_cutover_receipt() -> dict[str, Any]:
        """Emit deterministic forward, return, fallback, and rollback evidence."""
        return get_federation().cutover_receipt()

    @mcp.resource("athena://federation-v2")
    def resource_federation_v2() -> str:
        """Verified v2 runtime status and immutable source receipt."""
        return json.dumps(get_federation().status(), indent=2, sort_keys=True)

    @mcp.resource("athena://federation-v2/cutover")
    def resource_federation_v2_cutover() -> str:
        """Deterministic P06 runtime cutover evidence; never promotion."""
        return json.dumps(
            get_federation().cutover_receipt(),
            indent=2,
            sort_keys=True,
        )

    @mcp.resource("athena://federation-v2/lock")
    def resource_federation_v2_lock() -> str:
        """Exact repository lock consumed by this process."""
        consumer = get_federation()
        return json.dumps(
            {
                "snapshot": consumer.snapshot,
                "release_candidate": {
                    "release_id": consumer.release_candidate["release_id"],
                    "selected_contract_lineage": consumer.release_candidate[
                        "selected_contract_lineage"
                    ],
                    "promotion_ready": consumer.release_candidate[
                        "promotion_ready"
                    ],
                },
                "control": consumer.lock["control"],
                "repositories": consumer.lock["repositories"],
            },
            indent=2,
            sort_keys=True,
        )
