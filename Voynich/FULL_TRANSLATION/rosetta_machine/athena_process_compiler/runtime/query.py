"""
query.py -- Query compiled artifacts by crystal address, element, and operator.

Provides a unified search interface over the GAWM registry and AtlasPack
bundles.  Supports filtering by crystal address prefix, element corridor,
operator family, artifact kind, tag, and compound filters.

Usage:
    >>> from athena_process_compiler.runtime.query import ArtifactQuery
    >>> q = ArtifactQuery.from_registry(registry)
    >>> results = q.by_address("I.f001r.01.0003")
    >>> results = q.by_element("fire")
    >>> results = q.by_operator("W:weave")
    >>> results = q.search(address_prefix="I.f001r", element="water")
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from athena_process_compiler.schemas.tokens import RawToken, ParseCandidate, ParsedToken, Truth
from athena_process_compiler.schemas.ir import OperatorIR
from athena_process_compiler.schemas.artifacts import NativeRender, VerificationBundle
from athena_process_compiler.config import GAWM_REGISTRY, GAWM_RUNTIME
from athena_process_compiler.storage.registry import Registry, RegistryEntry


# ---------------------------------------------------------------------------
# Query result
# ---------------------------------------------------------------------------

@dataclass
class QueryResult:
    """A single result from an artifact query.

    Attributes:
        fingerprint:     Content-addressed fingerprint.
        kind:            Artifact type.
        address:         Crystal address, if applicable.
        element:         Elemental corridor, if applicable.
        operator_family: Operator family, if applicable.
        tags:            Classification tags.
        compiled_at:     Compilation timestamp.
        metadata:        Additional metadata.
        payload:         Full artifact payload (loaded on demand).
        score:           Relevance score in [0.0, 1.0] (1.0 = exact match).
    """

    fingerprint: str
    kind: str
    address: str | None = None
    element: str | None = None
    operator_family: str | None = None
    tags: list[str] = field(default_factory=list)
    compiled_at: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    payload: dict[str, Any] | None = None
    score: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        """Return a plain-dict representation."""
        return {
            "fingerprint": self.fingerprint,
            "kind": self.kind,
            "address": self.address,
            "element": self.element,
            "operator_family": self.operator_family,
            "tags": self.tags,
            "compiled_at": self.compiled_at,
            "metadata": self.metadata,
            "score": self.score,
        }

    def __repr__(self) -> str:
        return (
            f"QueryResult(fp={self.fingerprint[:12]}..., "
            f"kind={self.kind!r}, address={self.address!r})"
        )

    @classmethod
    def from_registry_entry(
        cls,
        entry: RegistryEntry,
        *,
        payload: dict[str, Any] | None = None,
        score: float = 1.0,
    ) -> QueryResult:
        """Build a QueryResult from a RegistryEntry."""
        return cls(
            fingerprint=entry.fingerprint,
            kind=entry.kind,
            address=entry.address,
            element=entry.element,
            operator_family=entry.operator_family,
            tags=entry.tags,
            compiled_at=entry.compiled_at,
            metadata=entry.metadata,
            payload=payload,
            score=score,
        )


# ---------------------------------------------------------------------------
# Artifact loader
# ---------------------------------------------------------------------------

def _load_payload(entry: RegistryEntry) -> dict[str, Any] | None:
    """Attempt to load the full artifact JSON for a registry entry."""
    if entry.path is not None and entry.path.exists():
        try:
            data = json.loads(entry.path.read_text(encoding="utf-8"))
            return data.get("payload", data)
        except (json.JSONDecodeError, OSError):
            return None

    # Fall back to scanning GAWM_REGISTRY by fingerprint.
    candidate = GAWM_REGISTRY / f"{entry.fingerprint}.json"
    if candidate.exists():
        try:
            data = json.loads(candidate.read_text(encoding="utf-8"))
            return data.get("payload", data)
        except (json.JSONDecodeError, OSError):
            return None

    return None


# ---------------------------------------------------------------------------
# Artifact Query engine
# ---------------------------------------------------------------------------

class ArtifactQuery:
    """Search compiled artifacts by crystal address, element, operator, and more.

    The query engine wraps a Registry and provides composable filter methods.
    All query methods return lists of QueryResult, sorted by score descending.
    """

    def __init__(self, registry: Registry) -> None:
        """Initialise with a populated Registry.

        Args:
            registry: The compiled-object registry to search.
        """
        self._registry = registry

    @classmethod
    def from_registry(cls, registry: Registry) -> ArtifactQuery:
        """Create a query engine from an existing Registry."""
        return cls(registry)

    @classmethod
    def from_registry_file(cls, path: Path | None = None) -> ArtifactQuery:
        """Create a query engine by loading a Registry from a JSON file.

        Args:
            path: Path to the registry JSON file.  Defaults to the GAWM
                  registry location.
        """
        return cls(Registry.load(path))

    # -- single-axis queries ------------------------------------------------

    def by_address(self, address: str) -> list[QueryResult]:
        """Find all artifacts at an exact crystal address.

        Args:
            address: Full crystal address (``Book.Folio.Line.Position``).

        Returns:
            List of matching QueryResult instances.
        """
        entries = self._registry.by_address(address)
        return [QueryResult.from_registry_entry(e) for e in entries]

    def by_address_prefix(self, prefix: str) -> list[QueryResult]:
        """Find all artifacts whose crystal address starts with a prefix.

        Useful for querying an entire folio (``"I.f001r"``) or line
        (``"I.f001r.01"``).

        Args:
            prefix: Address prefix to match.

        Returns:
            List of matching QueryResult instances, sorted by score.
        """
        results: list[QueryResult] = []
        for entry in self._registry:
            if entry.address and entry.address.startswith(prefix):
                score = len(prefix) / max(len(entry.address), 1)
                results.append(QueryResult.from_registry_entry(entry, score=score))
        return sorted(results, key=lambda r: r.score, reverse=True)

    def by_element(self, element: str) -> list[QueryResult]:
        """Find all artifacts belonging to an elemental corridor.

        Args:
            element: Element name (``"earth"``, ``"water"``, ``"fire"``,
                     ``"air"``, ``"void"``).

        Returns:
            List of matching QueryResult instances.
        """
        entries = self._registry.by_element(element)
        return [QueryResult.from_registry_entry(e) for e in entries]

    def by_operator(self, operator_family: str) -> list[QueryResult]:
        """Find all artifacts compiled from a specific operator family.

        Args:
            operator_family: Operator family string (e.g. ``"W:weave"``).

        Returns:
            List of matching QueryResult instances.
        """
        entries = self._registry.by_operator_family(operator_family)
        return [QueryResult.from_registry_entry(e) for e in entries]

    def by_kind(self, kind: str) -> list[QueryResult]:
        """Find all artifacts of a specific kind.

        Args:
            kind: Artifact kind (e.g. ``"operator_ir"``, ``"native_render"``).

        Returns:
            List of matching QueryResult instances.
        """
        entries = self._registry.by_kind(kind)
        return [QueryResult.from_registry_entry(e) for e in entries]

    def by_tag(self, tag: str) -> list[QueryResult]:
        """Find all artifacts carrying a specific tag.

        Args:
            tag: Tag string to search for.

        Returns:
            List of matching QueryResult instances.
        """
        entries = self._registry.by_tag(tag)
        return [QueryResult.from_registry_entry(e) for e in entries]

    def by_fingerprint(self, fingerprint: str, *, load: bool = True) -> QueryResult | None:
        """Look up a single artifact by its content fingerprint.

        Args:
            fingerprint: The SHA-256 fingerprint to find.
            load:        If True, load the full payload from disk.

        Returns:
            A QueryResult, or None if not found.
        """
        entry = self._registry.get(fingerprint)
        if entry is None:
            return None
        payload = _load_payload(entry) if load else None
        return QueryResult.from_registry_entry(entry, payload=payload)

    def by_operator_id(self, operator_id: str, *, load: bool = True) -> list[QueryResult]:
        """Find all artifacts referencing a given operator_id / token_id.

        Scans loaded payloads for ``token_id``, ``operator_id``, or ``ir_id``
        fields matching the query.

        Args:
            operator_id: The OperatorIR.token_id to search for.
            load:        If True, include payloads in results.

        Returns:
            List of matching QueryResult objects.
        """
        results: list[QueryResult] = []
        id_keys = {"token_id", "operator_id", "ir_id"}

        for entry in self._registry:
            payload = _load_payload(entry)
            if payload is None:
                continue
            for key in id_keys:
                if payload.get(key) == operator_id:
                    results.append(QueryResult.from_registry_entry(
                        entry, payload=payload if load else None
                    ))
                    break

        return results

    # -- composite search ---------------------------------------------------

    def search(
        self,
        *,
        address_prefix: str | None = None,
        element: str | None = None,
        operator_family: str | None = None,
        kind: str | None = None,
        tag: str | None = None,
        limit: int = 100,
    ) -> list[QueryResult]:
        """Composite search across multiple dimensions.

        All provided filters are AND-combined.  Omitted filters match
        everything.

        Args:
            address_prefix:  Crystal address prefix to match.
            element:         Elemental corridor to match.
            operator_family: Operator family to match.
            kind:            Artifact kind to match.
            tag:             Tag to match.
            limit:           Maximum number of results to return.

        Returns:
            List of QueryResult instances sorted by score descending,
            capped at *limit*.
        """
        results: list[QueryResult] = []

        for entry in self._registry:
            score = 1.0
            match = True

            if address_prefix is not None:
                if entry.address and entry.address.startswith(address_prefix):
                    score *= len(address_prefix) / max(len(entry.address), 1)
                else:
                    match = False

            if element is not None and entry.element != element:
                match = False

            if operator_family is not None and entry.operator_family != operator_family:
                match = False

            if kind is not None and entry.kind != kind:
                match = False

            if tag is not None and tag not in entry.tags:
                match = False

            if match:
                results.append(QueryResult.from_registry_entry(entry, score=score))

        results.sort(key=lambda r: r.score, reverse=True)
        return results[:limit]

    # -- statistics ---------------------------------------------------------

    def stats(self) -> dict[str, Any]:
        """Return summary statistics about the queryable artifacts.

        Returns:
            A dict with counts by kind, element, and total entries.
        """
        kind_counts: dict[str, int] = {}
        element_counts: dict[str, int] = {}

        for entry in self._registry:
            kind_counts[entry.kind] = kind_counts.get(entry.kind, 0) + 1
            if entry.element:
                element_counts[entry.element] = element_counts.get(entry.element, 0) + 1

        return {
            "total_entries": len(self._registry),
            "by_kind": kind_counts,
            "by_element": element_counts,
        }


# ---------------------------------------------------------------------------
# Module-level convenience functions (backward-compatible)
# ---------------------------------------------------------------------------

def query_by_fingerprint(
    registry: Registry, fingerprint: str, *, load: bool = True
) -> QueryResult | None:
    """Look up a single artifact by its content fingerprint."""
    return ArtifactQuery(registry).by_fingerprint(fingerprint, load=load)


def query_by_kind(registry: Registry, kind: str, *, load: bool = False) -> list[QueryResult]:
    """Find all artifacts of a given kind."""
    return ArtifactQuery(registry).by_kind(kind)


def query_by_tag(registry: Registry, tag: str, *, load: bool = False) -> list[QueryResult]:
    """Find all artifacts carrying a specific tag."""
    return ArtifactQuery(registry).by_tag(tag)


def query_by_operator_id(
    registry: Registry, operator_id: str, *, load: bool = True
) -> list[QueryResult]:
    """Find all artifacts referencing a given operator_id."""
    return ArtifactQuery(registry).by_operator_id(operator_id, load=load)


def query_compound(
    registry: Registry,
    *,
    kind: str | None = None,
    tag: str | None = None,
    operator_id: str | None = None,
    load: bool = False,
) -> list[QueryResult]:
    """Run a compound query with multiple optional filters."""
    q = ArtifactQuery(registry)
    # For operator_id filtering, fall back to full scan
    if operator_id is not None:
        results = q.by_operator_id(operator_id, load=load)
        if kind is not None:
            results = [r for r in results if r.kind == kind]
        if tag is not None:
            results = [r for r in results if tag in r.tags]
        return results
    return q.search(kind=kind, tag=tag)
