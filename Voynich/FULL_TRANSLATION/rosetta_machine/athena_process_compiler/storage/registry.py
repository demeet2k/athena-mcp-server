"""
registry.py -- Object registry with content-addressed fingerprints for the
Athena Process Language Compiler.

The Registry maps content-addressed fingerprints to artifact metadata,
providing fast lookup by fingerprint, crystal address, element, and
operator family.  It tracks compilation timestamps and supports
persistence to a JSON file in the GAWM registry directory.

Usage:
    >>> from athena_process_compiler.storage.registry import Registry
    >>> reg = Registry()
    >>> entry = reg.register(ir.to_dict(), "operator_ir", address="I.f001r.01.0003")
    >>> reg.by_address("I.f001r.01.0003")
    [RegistryEntry(...)]
    >>> reg.save()
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from athena_process_compiler.schemas.tokens import RawToken, ParseCandidate, ParsedToken, Truth
from athena_process_compiler.schemas.ir import OperatorIR
from athena_process_compiler.schemas.artifacts import NativeRender, VerificationBundle
from athena_process_compiler.config import (
    GAWM_REGISTRY,
    HASH_ALGORITHM,
    JSON_INDENT,
    JSON_ENSURE_ASCII,
)


# ---------------------------------------------------------------------------
# Registry entry
# ---------------------------------------------------------------------------

class RegistryEntry:
    """A single entry in the compiled-object registry.

    Attributes:
        fingerprint: Content-addressed hash of the artifact payload.
        kind:        Artifact type (e.g. ``"operator_ir"``, ``"native_render"``,
                     ``"verification_bundle"``).
        address:     Crystal address (``Book.Folio.Line.Position``), if applicable.
        element:     Elemental corridor (``"earth"``, ``"water"``, etc.).
        operator_family: Operator family string (e.g. ``"W:weave"``).
        tags:        Classification tags.
        path:        Optional filesystem path where the artifact is stored.
        compiled_at: ISO-8601 timestamp of when the artifact was compiled.
        metadata:    Arbitrary extra metadata.
    """

    __slots__ = (
        "fingerprint", "kind", "address", "element", "operator_family",
        "tags", "path", "compiled_at", "metadata",
    )

    def __init__(
        self,
        fingerprint: str,
        kind: str,
        *,
        address: str | None = None,
        element: str | None = None,
        operator_family: str | None = None,
        tags: list[str] | None = None,
        path: Path | None = None,
        compiled_at: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.fingerprint = fingerprint
        self.kind = kind
        self.address = address
        self.element = element
        self.operator_family = operator_family
        self.tags = tags or []
        self.path = path
        self.compiled_at = compiled_at or datetime.now(timezone.utc).isoformat()
        self.metadata = metadata or {}

    def to_dict(self) -> dict[str, Any]:
        """Return a plain-dict representation."""
        d: dict[str, Any] = {
            "fingerprint": self.fingerprint,
            "kind": self.kind,
            "address": self.address,
            "element": self.element,
            "operator_family": self.operator_family,
            "tags": self.tags,
            "compiled_at": self.compiled_at,
            "metadata": self.metadata,
        }
        if self.path is not None:
            d["path"] = str(self.path)
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RegistryEntry:
        """Construct from a plain dict."""
        path = Path(data["path"]) if "path" in data else None
        return cls(
            fingerprint=data["fingerprint"],
            kind=data["kind"],
            address=data.get("address"),
            element=data.get("element"),
            operator_family=data.get("operator_family"),
            tags=data.get("tags", []),
            path=path,
            compiled_at=data.get("compiled_at"),
            metadata=data.get("metadata", {}),
        )


# ---------------------------------------------------------------------------
# Content-addressed fingerprint computation
# ---------------------------------------------------------------------------

def compute_fingerprint(payload: dict[str, Any]) -> str:
    """Compute a content-addressed fingerprint for a JSON-serialisable payload.

    Args:
        payload: Any JSON-serialisable dict.

    Returns:
        Hex-encoded digest using the configured HASH_ALGORITHM.
    """
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.new(HASH_ALGORITHM, canonical.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

class Registry:
    """In-memory registry of compiled artifacts, keyed by content fingerprint.

    Supports insertion, lookup by fingerprint/address/element/operator family,
    filtering by kind/tag, serialisation to JSON, and loading from the GAWM
    registry directory.  Tracks compilation timestamps for every entry.
    """

    def __init__(self) -> None:
        self._entries: dict[str, RegistryEntry] = {}
        # Secondary indexes for fast lookup
        self._by_address: dict[str, list[str]] = {}
        self._by_element: dict[str, list[str]] = {}
        self._by_operator: dict[str, list[str]] = {}

    # -- size / iteration ---------------------------------------------------

    def __len__(self) -> int:
        return len(self._entries)

    def __contains__(self, fingerprint: str) -> bool:
        return fingerprint in self._entries

    def __iter__(self) -> Iterator[RegistryEntry]:
        return iter(self._entries.values())

    # -- index maintenance --------------------------------------------------

    def _index_entry(self, entry: RegistryEntry) -> None:
        """Add an entry to the secondary indexes."""
        fp = entry.fingerprint
        if entry.address:
            self._by_address.setdefault(entry.address, []).append(fp)
        if entry.element:
            self._by_element.setdefault(entry.element, []).append(fp)
        if entry.operator_family:
            self._by_operator.setdefault(entry.operator_family, []).append(fp)

    def _rebuild_indexes(self) -> None:
        """Rebuild all secondary indexes from scratch."""
        self._by_address.clear()
        self._by_element.clear()
        self._by_operator.clear()
        for entry in self._entries.values():
            self._index_entry(entry)

    # -- CRUD ---------------------------------------------------------------

    def register(
        self,
        payload: dict[str, Any],
        kind: str,
        *,
        address: str | None = None,
        element: str | None = None,
        operator_family: str | None = None,
        tags: list[str] | None = None,
        path: Path | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RegistryEntry:
        """Register a new artifact payload.

        Computes the content fingerprint and stores an entry.  If an
        artifact with the same fingerprint already exists, the existing
        entry is returned unchanged (deduplication).

        Args:
            payload:         JSON-serialisable artifact data.
            kind:            Artifact type label.
            address:         Crystal address (``Book.Folio.Line.Position``).
            element:         Elemental corridor name.
            operator_family: Operator family string.
            tags:            Optional classification tags.
            path:            Optional filesystem path.
            metadata:        Optional extra metadata.

        Returns:
            The (possibly pre-existing) RegistryEntry.
        """
        fp = compute_fingerprint(payload)

        if fp in self._entries:
            return self._entries[fp]

        entry = RegistryEntry(
            fingerprint=fp,
            kind=kind,
            address=address,
            element=element,
            operator_family=operator_family,
            tags=tags,
            path=path,
            metadata=metadata,
        )
        self._entries[fp] = entry
        self._index_entry(entry)
        return entry

    def register_ir(self, ir: OperatorIR, *, path: Path | None = None) -> RegistryEntry:
        """Register an OperatorIR node directly.

        Extracts address, element, and operator_family from the IR node.

        Args:
            ir:   The OperatorIR node to register.
            path: Optional filesystem path.

        Returns:
            The RegistryEntry for this IR node.
        """
        return self.register(
            payload=ir.to_dict(),
            kind="operator_ir",
            address=ir.address,
            element=ir.element,
            operator_family=ir.operator_family,
            tags=ir.corridor_tags,
            path=path,
            metadata={"token_id": ir.token_id, "lens": ir.lens},
        )

    def register_render(
        self, render: NativeRender, ir_id: str, *, path: Path | None = None
    ) -> RegistryEntry:
        """Register a NativeRender directly.

        Args:
            render: The NativeRender to register.
            ir_id:  The token_id of the OperatorIR this render belongs to.
            path:   Optional filesystem path.

        Returns:
            The RegistryEntry for this render.
        """
        return self.register(
            payload=render.to_dict(),
            kind="native_render",
            tags=[render.backend, render.status],
            path=path,
            metadata={"ir_id": ir_id, "backend": render.backend},
        )

    def register_verification(
        self, vb: VerificationBundle, *, path: Path | None = None
    ) -> RegistryEntry:
        """Register a VerificationBundle directly.

        Args:
            vb:   The VerificationBundle to register.
            path: Optional filesystem path.

        Returns:
            The RegistryEntry for this verification bundle.
        """
        return self.register(
            payload=vb.to_dict(),
            kind="verification_bundle",
            tags=[vb.status],
            path=path,
            metadata={"ir_id": vb.ir_id},
        )

    def get(self, fingerprint: str) -> RegistryEntry | None:
        """Look up an entry by its fingerprint.  Returns None if absent."""
        return self._entries.get(fingerprint)

    def remove(self, fingerprint: str) -> bool:
        """Remove an entry by fingerprint.  Returns True if it existed."""
        if fingerprint in self._entries:
            del self._entries[fingerprint]
            self._rebuild_indexes()
            return True
        return False

    # -- queries by secondary index -----------------------------------------

    def by_address(self, address: str) -> list[RegistryEntry]:
        """Return all entries matching a crystal address."""
        fps = self._by_address.get(address, [])
        return [self._entries[fp] for fp in fps if fp in self._entries]

    def by_element(self, element: str) -> list[RegistryEntry]:
        """Return all entries matching a given element."""
        fps = self._by_element.get(element, [])
        return [self._entries[fp] for fp in fps if fp in self._entries]

    def by_operator_family(self, operator_family: str) -> list[RegistryEntry]:
        """Return all entries matching a given operator family."""
        fps = self._by_operator.get(operator_family, [])
        return [self._entries[fp] for fp in fps if fp in self._entries]

    def by_kind(self, kind: str) -> list[RegistryEntry]:
        """Return all entries matching a given artifact kind."""
        return [e for e in self._entries.values() if e.kind == kind]

    def by_tag(self, tag: str) -> list[RegistryEntry]:
        """Return all entries that carry a specific tag."""
        return [e for e in self._entries.values() if tag in e.tags]

    def fingerprints(self) -> list[str]:
        """Return a sorted list of all registered fingerprints."""
        return sorted(self._entries.keys())

    # -- serialisation ------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialise the entire registry to a dict."""
        return {
            "entry_count": len(self._entries),
            "entries": {fp: e.to_dict() for fp, e in self._entries.items()},
        }

    def to_json(self, **kwargs: Any) -> str:
        """Serialise to a JSON string."""
        return json.dumps(
            self.to_dict(),
            indent=JSON_INDENT,
            ensure_ascii=JSON_ENSURE_ASCII,
            **kwargs,
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Registry:
        """Reconstruct a Registry from a serialised dict."""
        reg = cls()
        for fp, entry_data in data.get("entries", {}).items():
            entry = RegistryEntry.from_dict(entry_data)
            reg._entries[fp] = entry
        reg._rebuild_indexes()
        return reg

    @classmethod
    def from_json(cls, raw: str) -> Registry:
        """Reconstruct a Registry from a JSON string."""
        return cls.from_dict(json.loads(raw))

    def save(self, path: Path | None = None) -> Path:
        """Write the registry to a JSON file.

        Args:
            path: Output path.  Defaults to ``GAWM_REGISTRY/registry.json``.

        Returns:
            The path that was written.
        """
        if path is None:
            GAWM_REGISTRY.mkdir(parents=True, exist_ok=True)
            path = GAWM_REGISTRY / "registry.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_json(), encoding="utf-8")
        return path

    @classmethod
    def load(cls, path: Path | None = None) -> Registry:
        """Load a registry from a JSON file.

        Args:
            path: Input path.  Defaults to ``GAWM_REGISTRY/registry.json``.

        Returns:
            The loaded Registry (empty Registry if file does not exist).
        """
        if path is None:
            path = GAWM_REGISTRY / "registry.json"
        if not path.exists():
            return cls()
        raw = path.read_text(encoding="utf-8")
        return cls.from_json(raw)

    def load_gawm_dir(self, directory: Path | None = None) -> int:
        """Scan a GAWM registry directory and ingest all artifact bundles.

        Each JSON file in the directory is expected to have a GAWM
        envelope with ``kind``, ``fingerprint``, and ``payload`` fields.

        Args:
            directory: Directory to scan.  Defaults to GAWM_REGISTRY.

        Returns:
            Number of new entries ingested.
        """
        directory = directory or GAWM_REGISTRY
        if not directory.is_dir():
            return 0

        added = 0
        for json_file in sorted(directory.glob("*.json")):
            if json_file.name == "registry.json":
                continue
            try:
                data = json.loads(json_file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue

            fp = data.get("fingerprint", "")
            kind = data.get("kind", "unknown")
            tags = data.get("tags", [])

            if fp and fp not in self._entries:
                entry = RegistryEntry(
                    fingerprint=fp,
                    kind=kind,
                    address=data.get("address"),
                    element=data.get("element"),
                    operator_family=data.get("operator_family"),
                    tags=tags,
                    path=json_file,
                    compiled_at=data.get("compiled_at"),
                    metadata={"source": "gawm_dir"},
                )
                self._entries[fp] = entry
                self._index_entry(entry)
                added += 1

        return added
