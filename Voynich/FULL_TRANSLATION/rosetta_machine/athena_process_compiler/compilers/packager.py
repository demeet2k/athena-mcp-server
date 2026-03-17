"""
packager.py -- Artifact packaging for the Athena Process Language Compiler.

Bundles OperatorIR nodes, NativeRender outputs, and VerificationBundles
into complete, content-addressed artifacts suitable for storage in
AtlasPack bundles or the GAWM registry.

Each packaged artifact receives a SHA-256 fingerprint computed over the
canonical JSON serialisation of its payload, enabling deduplication and
integrity verification throughout the pipeline.

Usage:
    >>> from athena_process_compiler.compilers.packager import ArtifactPackager
    >>> packager = ArtifactPackager()
    >>> package = packager.package(ir_node, renders, verification)
    >>> package.fingerprint
    'a3f2c8...'
    >>> json_str = packager.export_all_json()
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from athena_process_compiler.schemas.tokens import RawToken, ParseCandidate, ParsedToken, Truth
from athena_process_compiler.schemas.ir import OperatorIR
from athena_process_compiler.schemas.artifacts import NativeRender, VerificationBundle


# ---------------------------------------------------------------------------
# Content-addressed fingerprinting
# ---------------------------------------------------------------------------

def fingerprint(payload: dict[str, Any]) -> str:
    """Compute a SHA-256 content-addressed fingerprint for a payload.

    The payload is serialised with sorted keys and compact separators
    to produce a deterministic canonical form before hashing.

    Args:
        payload: Any JSON-serialisable dict.

    Returns:
        The hex-encoded SHA-256 digest.
    """
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Packaged artifact
# ---------------------------------------------------------------------------

@dataclass
class PackagedArtifact:
    """A complete, content-addressed artifact ready for storage.

    Attributes:
        artifact_id:    Unique content-addressed fingerprint of the full payload.
        token_id:       Back-reference to the originating token / IR node.
        ir:             The compiled OperatorIR node.
        renders:        List of NativeRender outputs from all backends.
        verification:   The cross-backend VerificationBundle, if available.
        fingerprint:    SHA-256 fingerprint of the combined payload.
        created_at:     ISO-8601 timestamp of packaging.
        metadata:       Arbitrary additional metadata.
    """

    artifact_id: str
    token_id: str
    ir: OperatorIR
    renders: list[NativeRender]
    verification: VerificationBundle | None
    fingerprint: str
    created_at: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a plain-dict representation suitable for JSON encoding."""
        return {
            "artifact_id": self.artifact_id,
            "token_id": self.token_id,
            "ir": self.ir.to_dict(),
            "renders": [r.to_dict() for r in self.renders],
            "verification": self.verification.to_dict() if self.verification else None,
            "fingerprint": self.fingerprint,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }

    def to_json(self, **kwargs: Any) -> str:
        """Serialise to a JSON string."""
        return json.dumps(self.to_dict(), **kwargs)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PackagedArtifact:
        """Construct from a plain dict."""
        verification = None
        if data.get("verification") is not None:
            verification = VerificationBundle.from_dict(data["verification"])
        return cls(
            artifact_id=data["artifact_id"],
            token_id=data["token_id"],
            ir=OperatorIR.from_dict(data["ir"]),
            renders=[NativeRender.from_dict(r) for r in data.get("renders", [])],
            verification=verification,
            fingerprint=data["fingerprint"],
            created_at=data["created_at"],
            metadata=data.get("metadata", {}),
        )

    @classmethod
    def from_json(cls, raw: str) -> PackagedArtifact:
        """Deserialise from a JSON string."""
        return cls.from_dict(json.loads(raw))


# ---------------------------------------------------------------------------
# Legacy bundle interface (backward-compatible)
# ---------------------------------------------------------------------------

def package_artifact(
    ir_chain: list[OperatorIR],
    renders: dict[str, list[NativeRender]],
    verification: list[VerificationBundle],
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Package IR + renders + verification into a complete artifact bundle.

    This is the batch interface that packages an entire chain at once.

    Args:
        ir_chain:     List of OperatorIR nodes forming the chain.
        renders:      Dict mapping backend names to lists of NativeRender.
        verification: List of VerificationBundle instances.
        context:      Optional user-provided context metadata.

    Returns:
        A dict with metadata, ir, renders, verification, replay_seed,
        and context suitable for JSON export.
    """
    ir_data = [ir.to_dict() for ir in ir_chain]
    render_data = {
        backend: [r.to_dict() for r in render_list]
        for backend, render_list in renders.items()
    }
    verification_data = [v.to_dict() for v in verification]

    # Build replay seed (minimal reconstruction data)
    replay_seed = {
        "operator_chain": [ir.operator_family for ir in ir_chain],
        "element_chain": [ir.element for ir in ir_chain],
        "address_chain": [ir.address for ir in ir_chain],
    }

    # Compute content fingerprint over entire bundle
    bundle_payload = {
        "ir": ir_data,
        "renders": render_data,
        "verification": verification_data,
    }
    fp = fingerprint(bundle_payload)

    # Compute aggregate truth status
    statuses = [v.status for v in verification]
    if not statuses:
        aggregate_status: Truth = "AMBIG"
    elif all(s == "OK" for s in statuses):
        aggregate_status = "OK"
    elif any(s == "FAIL" for s in statuses):
        aggregate_status = "FAIL"
    elif any(s == "AMBIG" for s in statuses):
        aggregate_status = "AMBIG"
    else:
        aggregate_status = "NEAR"

    return {
        "metadata": {
            "fingerprint": fp,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "ir_count": len(ir_chain),
            "backend_count": len(renders),
            "render_count": sum(len(v) for v in renders.values()),
            "verification_count": len(verification),
            "aggregate_status": aggregate_status,
            "version": "1.0.0",
        },
        "ir": ir_data,
        "renders": render_data,
        "verification": verification_data,
        "replay_seed": replay_seed,
        "context": context or {},
    }


# ---------------------------------------------------------------------------
# Artifact Packager (per-node interface)
# ---------------------------------------------------------------------------

class ArtifactPackager:
    """Bundles IR, renders, and verification into content-addressed artifacts.

    The packager computes deterministic fingerprints so that identical
    inputs always produce the same artifact_id, enabling deduplication
    in the registry and AtlasPack storage.
    """

    def __init__(self, *, metadata: dict[str, Any] | None = None) -> None:
        """Initialise the packager.

        Args:
            metadata: Default metadata attached to every packaged artifact.
        """
        self._default_metadata = metadata or {}
        self._packages: list[PackagedArtifact] = []

    @property
    def packages(self) -> list[PackagedArtifact]:
        """All artifacts produced by this packager instance."""
        return list(self._packages)

    def package(
        self,
        ir: OperatorIR,
        renders: list[NativeRender] | None = None,
        verification: VerificationBundle | None = None,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> PackagedArtifact:
        """Package a single OperatorIR node with its renders and verification.

        Args:
            ir:           The compiled OperatorIR node.
            renders:      List of NativeRender outputs (may be empty).
            verification: Optional cross-backend VerificationBundle.
            metadata:     Per-artifact metadata (merged with default).

        Returns:
            A PackagedArtifact with a computed fingerprint.
        """
        renders = renders or []
        now = datetime.now(timezone.utc).isoformat()

        payload: dict[str, Any] = {
            "ir": ir.to_dict(),
            "renders": [r.to_dict() for r in renders],
            "verification": verification.to_dict() if verification else None,
        }
        fp = fingerprint(payload)

        merged_meta = {**self._default_metadata, **(metadata or {})}

        artifact = PackagedArtifact(
            artifact_id=fp,
            token_id=ir.token_id,
            ir=ir,
            renders=renders,
            verification=verification,
            fingerprint=fp,
            created_at=now,
            metadata=merged_meta,
        )
        self._packages.append(artifact)
        return artifact

    def package_batch(
        self,
        items: list[tuple[OperatorIR, list[NativeRender], VerificationBundle | None]],
        *,
        metadata: dict[str, Any] | None = None,
    ) -> list[PackagedArtifact]:
        """Package multiple IR nodes in one call.

        Args:
            items:    List of ``(ir, renders, verification)`` tuples.
            metadata: Per-artifact metadata applied to all items.

        Returns:
            List of PackagedArtifact instances.
        """
        return [
            self.package(ir, renders, vb, metadata=metadata)
            for ir, renders, vb in items
        ]

    def export_all_json(self, *, indent: int = 2) -> str:
        """Export all packaged artifacts as a JSON array string.

        Args:
            indent: JSON indentation level.

        Returns:
            A JSON string containing an array of artifact dicts.
        """
        return json.dumps(
            [pkg.to_dict() for pkg in self._packages],
            indent=indent,
            ensure_ascii=False,
        )

    def export_manifest(self) -> dict[str, Any]:
        """Return a manifest summarising all packaged artifacts.

        Returns:
            A dict with counts, fingerprints, and timestamp.
        """
        return {
            "artifact_count": len(self._packages),
            "fingerprints": [pkg.fingerprint for pkg in self._packages],
            "token_ids": [pkg.token_id for pkg in self._packages],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    def reset(self) -> None:
        """Clear all accumulated packages."""
        self._packages.clear()


# ---------------------------------------------------------------------------
# JSON export (legacy convenience)
# ---------------------------------------------------------------------------

def export_json(bundle: dict[str, Any], path: str | None = None) -> str:
    """Export an artifact bundle as a JSON string, optionally writing to file.

    Args:
        bundle: The artifact bundle dict (from ``package_artifact``).
        path:   Optional file path to write the JSON output.

    Returns:
        The JSON string.
    """
    json_str = json.dumps(bundle, indent=2, ensure_ascii=False)
    if path:
        with open(path, "w", encoding="utf-8") as f:
            f.write(json_str)
    return json_str
