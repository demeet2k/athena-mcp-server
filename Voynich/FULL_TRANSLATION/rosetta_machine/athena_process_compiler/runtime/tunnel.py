"""
tunnel.py -- Tunnel artifacts between projects for cross-project reuse.

A tunnel is a directed link that exports compiled artifacts from one
project's GAWM store and imports them into another.  Tunnels enable
cross-project reuse without duplicating source data -- only fingerprint
references and lightweight manifests travel through the tunnel.

Edge kind MIGRATE in AtlasPack edges records tunnelled artifacts.

Usage:
    >>> from athena_process_compiler.runtime.tunnel import Tunnel
    >>> tunnel = Tunnel("my_tunnel", source="project_a", target="project_b")
    >>> tunnel.add_fingerprints(["abc123...", "def456..."])
    >>> tunnel.export()
    >>> # On the target side:
    >>> tunnel = Tunnel.load("path/to/tunnel.json")
    >>> count = tunnel.transport(target_registry=Path("/target/registry"))
"""

from __future__ import annotations

import hashlib
import json
import shutil
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from athena_process_compiler.schemas.tokens import RawToken, ParseCandidate, ParsedToken, Truth
from athena_process_compiler.schemas.ir import OperatorIR
from athena_process_compiler.schemas.artifacts import NativeRender, VerificationBundle
from athena_process_compiler.config import (
    GAWM_REGISTRY,
    GAWM_TUNNELS,
    HASH_ALGORITHM,
    JSON_INDENT,
    JSON_ENSURE_ASCII,
    ensure_gawm_dirs,
)


# ---------------------------------------------------------------------------
# Fingerprinting helper
# ---------------------------------------------------------------------------

def _fingerprint(payload: dict[str, Any]) -> str:
    """Compute a content-addressed fingerprint for a payload."""
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.new(HASH_ALGORITHM, canonical.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Tunnel descriptor
# ---------------------------------------------------------------------------

@dataclass
class TunnelDescriptor:
    """Describes a tunnel between two projects.

    Attributes:
        tunnel_id:      Unique tunnel identifier.
        source_project: Name or root path of the source project.
        target_project: Name or root path of the target project.
        operator_ids:   List of operator token_ids transported.
        fingerprints:   List of artifact fingerprints transported.
        created_at:     ISO-8601 timestamp of tunnel creation.
        metadata:       Extra metadata.
    """

    tunnel_id: str
    source_project: str
    target_project: str
    operator_ids: list[str] = field(default_factory=list)
    fingerprints: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a plain-dict representation."""
        return {
            "tunnel_id": self.tunnel_id,
            "source_project": self.source_project,
            "target_project": self.target_project,
            "operator_ids": self.operator_ids,
            "fingerprints": self.fingerprints,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TunnelDescriptor:
        """Construct from a plain dict."""
        return cls(
            tunnel_id=data["tunnel_id"],
            source_project=data["source_project"],
            target_project=data["target_project"],
            operator_ids=data.get("operator_ids", []),
            fingerprints=data.get("fingerprints", []),
            created_at=data.get("created_at", datetime.now(timezone.utc).isoformat()),
            metadata=data.get("metadata", {}),
        )


# ---------------------------------------------------------------------------
# Tunnel class
# ---------------------------------------------------------------------------

class Tunnel:
    """Export and import artifacts between projects.

    A Tunnel wraps a TunnelDescriptor and provides methods to accumulate
    artifacts, export the tunnel manifest, and transport artifacts to a
    target registry.
    """

    def __init__(
        self,
        tunnel_id: str,
        source: str,
        target: str,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Create a new tunnel.

        Args:
            tunnel_id: Unique identifier for this tunnel.
            source:    Source project name or path.
            target:    Target project name or path.
            metadata:  Optional tunnel metadata.
        """
        self.descriptor = TunnelDescriptor(
            tunnel_id=tunnel_id,
            source_project=source,
            target_project=target,
            metadata=metadata or {},
        )

    @classmethod
    def from_descriptor(cls, desc: TunnelDescriptor) -> Tunnel:
        """Create a Tunnel from an existing TunnelDescriptor."""
        tunnel = cls.__new__(cls)
        tunnel.descriptor = desc
        return tunnel

    # -- accumulation -------------------------------------------------------

    def add_fingerprints(self, fingerprints: list[str]) -> None:
        """Add artifact fingerprints to the tunnel manifest.

        Args:
            fingerprints: List of SHA-256 fingerprints to transport.
        """
        self.descriptor.fingerprints.extend(fingerprints)

    def add_operator_ids(self, operator_ids: list[str]) -> None:
        """Add operator token_ids to the tunnel manifest.

        Args:
            operator_ids: List of OperatorIR.token_id values to transport.
        """
        self.descriptor.operator_ids.extend(operator_ids)

    def add_ir(self, ir: OperatorIR) -> None:
        """Add an OperatorIR node to the tunnel.

        Extracts the token_id and computes a fingerprint from the IR payload.
        """
        self.descriptor.operator_ids.append(ir.token_id)
        fp = _fingerprint(ir.to_dict())
        self.descriptor.fingerprints.append(fp)

    def add_ir_chain(self, ir_nodes: list[OperatorIR]) -> None:
        """Add a chain of OperatorIR nodes to the tunnel."""
        for ir in ir_nodes:
            self.add_ir(ir)

    # -- export / persist ---------------------------------------------------

    def export(self, directory: Path | None = None) -> Path:
        """Write the tunnel descriptor to a JSON file in GAWM_TUNNELS.

        Args:
            directory: Override output directory (default: GAWM_TUNNELS).

        Returns:
            Path to the written tunnel file.
        """
        ensure_gawm_dirs()
        directory = directory or GAWM_TUNNELS
        directory.mkdir(parents=True, exist_ok=True)

        payload = self.descriptor.to_dict()
        fp = _fingerprint(payload)

        envelope = {
            "kind": "tunnel",
            "fingerprint": fp,
            "payload": payload,
        }

        out_path = directory / f"{self.descriptor.tunnel_id}_{fp[:16]}.json"
        out_path.write_text(
            json.dumps(envelope, indent=JSON_INDENT, ensure_ascii=JSON_ENSURE_ASCII),
            encoding="utf-8",
        )
        return out_path

    # -- transport ----------------------------------------------------------

    def transport(
        self,
        *,
        source_registry: Path | None = None,
        target_registry: Path,
    ) -> int:
        """Copy artifact files from source registry to target registry.

        Only artifacts whose fingerprints are listed in the tunnel descriptor
        are transported.  Files that already exist at the target are skipped
        (content-addressed deduplication).

        Args:
            source_registry: Source GAWM registry dir (default: GAWM_REGISTRY).
            target_registry: Target GAWM registry dir.

        Returns:
            Number of files actually copied.
        """
        source_registry = source_registry or GAWM_REGISTRY
        target_registry.mkdir(parents=True, exist_ok=True)

        copied = 0
        for fp in self.descriptor.fingerprints:
            src = source_registry / f"{fp}.json"
            dst = target_registry / f"{fp}.json"
            if src.exists() and not dst.exists():
                shutil.copy2(str(src), str(dst))
                copied += 1

        return copied

    def export_portable(self, output_dir: Path) -> Path:
        """Create a portable tunnel package for transfer.

        Writes both the tunnel manifest and all referenced artifact files
        into a single directory that can be zipped or transferred.

        Args:
            output_dir: Directory to write the portable package.

        Returns:
            Path to the output directory.
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        # Write tunnel manifest
        manifest_path = output_dir / "tunnel.json"
        manifest_path.write_text(
            json.dumps(
                self.descriptor.to_dict(),
                indent=JSON_INDENT,
                ensure_ascii=JSON_ENSURE_ASCII,
            ),
            encoding="utf-8",
        )

        # Copy artifact files
        artifacts_dir = output_dir / "artifacts"
        artifacts_dir.mkdir(exist_ok=True)

        for fp in self.descriptor.fingerprints:
            src = GAWM_REGISTRY / f"{fp}.json"
            if src.exists():
                shutil.copy2(str(src), str(artifacts_dir / f"{fp}.json"))

        return output_dir

    # -- loading ------------------------------------------------------------

    @classmethod
    def load(cls, path: Path) -> Tunnel:
        """Load a Tunnel from a JSON file.

        Args:
            path: Path to the tunnel JSON file.

        Returns:
            A Tunnel instance.
        """
        data = json.loads(path.read_text(encoding="utf-8"))
        payload = data.get("payload", data)
        desc = TunnelDescriptor.from_dict(payload)
        return cls.from_descriptor(desc)

    # -- summary ------------------------------------------------------------

    def summary(self) -> dict[str, Any]:
        """Return a summary of the tunnel contents."""
        return {
            "tunnel_id": self.descriptor.tunnel_id,
            "source": self.descriptor.source_project,
            "target": self.descriptor.target_project,
            "operator_count": len(self.descriptor.operator_ids),
            "fingerprint_count": len(self.descriptor.fingerprints),
            "created_at": self.descriptor.created_at,
        }


# ---------------------------------------------------------------------------
# Module-level convenience functions (backward-compatible)
# ---------------------------------------------------------------------------

def create_tunnel(
    tunnel_id: str,
    source_project: str,
    target_project: str,
    *,
    operator_ids: list[str] | None = None,
    fingerprints: list[str] | None = None,
    metadata: dict[str, Any] | None = None,
) -> TunnelDescriptor:
    """Create a new tunnel descriptor and persist it to GAWM_TUNNELS."""
    tunnel = Tunnel(tunnel_id, source_project, target_project, metadata=metadata)
    if operator_ids:
        tunnel.add_operator_ids(operator_ids)
    if fingerprints:
        tunnel.add_fingerprints(fingerprints)
    tunnel.export()
    return tunnel.descriptor


def list_tunnels(directory: Path | None = None) -> list[TunnelDescriptor]:
    """Load all tunnel descriptors from a GAWM tunnels directory."""
    directory = directory or GAWM_TUNNELS
    if not directory.is_dir():
        return []

    tunnels: list[TunnelDescriptor] = []
    for json_file in sorted(directory.glob("*.json")):
        try:
            data = json.loads(json_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        payload = data.get("payload", data)
        if "tunnel_id" in payload:
            tunnels.append(TunnelDescriptor.from_dict(payload))

    return tunnels


def transport_artifacts(
    descriptor: TunnelDescriptor,
    source_registry: Path | None = None,
    target_registry: Path | None = None,
) -> int:
    """Copy artifact files from source registry to target registry."""
    if target_registry is None:
        raise ValueError("target_registry must be specified")

    tunnel = Tunnel.from_descriptor(descriptor)
    return tunnel.transport(
        source_registry=source_registry,
        target_registry=target_registry,
    )
