"""
gawm_writer.py -- Write compiled artifacts to the GLOBAL_ATHENA (GAWM) directory.

GAWM directory layout:
    GLOBAL_ATHENA/
        00_REGISTRY/   -- artifact index and content-addressed manifests
        01_TUNNELS/    -- inter-project tunnel descriptors
        02_PACKS/      -- AtlasPack bundles
        04_RUNTIME/    -- runtime query indices and replay logs

Every artifact is stored as a JSON file whose filename is its content-
addressed SHA-256 fingerprint, ensuring deduplication and tamper detection.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from athena_process_compiler.schemas.ir import OperatorIR
from athena_process_compiler.schemas.artifacts import NativeRender, VerificationBundle
from athena_process_compiler.config import (
    GAWM_REGISTRY,
    GAWM_TUNNELS,
    GAWM_PACKS,
    GAWM_RUNTIME,
    HASH_ALGORITHM,
    JSON_INDENT,
    JSON_ENSURE_ASCII,
    ensure_gawm_dirs,
)


# ---------------------------------------------------------------------------
# Fingerprinting
# ---------------------------------------------------------------------------

def fingerprint(data: dict[str, Any]) -> str:
    """Compute a content-addressed fingerprint for a JSON-serialisable dict.

    Uses canonical JSON (sorted keys, no extra whitespace) and SHA-256.
    """
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return hashlib.new(HASH_ALGORITHM, canonical.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Low-level writers
# ---------------------------------------------------------------------------

def _write_json(path: Path, data: dict[str, Any]) -> Path:
    """Write *data* as formatted JSON to *path*, creating parents as needed.

    Returns the path that was written.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=JSON_INDENT, ensure_ascii=JSON_ENSURE_ASCII),
        encoding="utf-8",
    )
    return path


def _timestamp() -> str:
    """ISO-8601 UTC timestamp for artifact metadata."""
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Artifact bundle builder
# ---------------------------------------------------------------------------

def _build_bundle(
    kind: str,
    payload: dict[str, Any],
    *,
    tags: list[str] | None = None,
) -> dict[str, Any]:
    """Wrap *payload* in a standard GAWM artifact envelope.

    The envelope carries:
        - kind:        artifact type label
        - fingerprint: content hash of the payload
        - created_utc: timestamp
        - tags:        optional classification tags
        - payload:     the actual data
    """
    fp = fingerprint(payload)
    return {
        "kind": kind,
        "fingerprint": fp,
        "created_utc": _timestamp(),
        "tags": tags or [],
        "payload": payload,
    }


# ---------------------------------------------------------------------------
# Public writers
# ---------------------------------------------------------------------------

def write_ir(ir: OperatorIR, *, tags: list[str] | None = None) -> Path:
    """Write an OperatorIR node to the GAWM registry.

    Args:
        ir:   The OperatorIR to persist.
        tags: Optional classification tags.

    Returns:
        Path to the written JSON file.
    """
    ensure_gawm_dirs()
    payload = ir.to_dict()
    bundle = _build_bundle("operator_ir", payload, tags=tags)
    fp = bundle["fingerprint"]
    return _write_json(GAWM_REGISTRY / f"{fp}.json", bundle)


def write_render(
    render: NativeRender,
    *,
    tags: list[str] | None = None,
) -> Path:
    """Write a NativeRender to the GAWM registry.

    Args:
        render: The NativeRender to persist.
        tags:   Optional classification tags.

    Returns:
        Path to the written JSON file.
    """
    ensure_gawm_dirs()
    payload = render.to_dict()
    bundle = _build_bundle("native_render", payload, tags=tags)
    fp = bundle["fingerprint"]
    return _write_json(GAWM_REGISTRY / f"{fp}.json", bundle)


def write_verification(
    vb: VerificationBundle,
    *,
    tags: list[str] | None = None,
) -> Path:
    """Write a VerificationBundle to the GAWM registry.

    Args:
        vb:   The VerificationBundle to persist.
        tags: Optional classification tags.

    Returns:
        Path to the written JSON file.
    """
    ensure_gawm_dirs()
    payload = vb.to_dict()
    bundle = _build_bundle("verification_bundle", payload, tags=tags)
    fp = bundle["fingerprint"]
    return _write_json(GAWM_REGISTRY / f"{fp}.json", bundle)


def write_tunnel(
    tunnel_id: str,
    source_project: str,
    target_project: str,
    operator_ids: list[str],
    *,
    metadata: dict[str, Any] | None = None,
) -> Path:
    """Write a tunnel descriptor to GAWM_TUNNELS.

    A tunnel links operators between two projects, enabling cross-project
    artifact sharing.

    Args:
        tunnel_id:      Unique tunnel identifier.
        source_project: Name or path of the source project.
        target_project: Name or path of the target project.
        operator_ids:   List of OperatorIR token_ids transported.
        metadata:       Optional extra metadata.

    Returns:
        Path to the written JSON file.
    """
    ensure_gawm_dirs()
    payload = {
        "tunnel_id": tunnel_id,
        "source_project": source_project,
        "target_project": target_project,
        "operator_ids": operator_ids,
        "metadata": metadata or {},
    }
    bundle = _build_bundle("tunnel", payload)
    fp = bundle["fingerprint"]
    return _write_json(GAWM_TUNNELS / f"{fp}.json", bundle)


def write_runtime_index(
    index_id: str,
    entries: list[dict[str, Any]],
) -> Path:
    """Write a runtime query index to GAWM_RUNTIME.

    Args:
        index_id: Identifier for this index.
        entries:  List of index entries (each a dict with at least
                  ``fingerprint`` and ``kind``).

    Returns:
        Path to the written JSON file.
    """
    ensure_gawm_dirs()
    payload = {
        "index_id": index_id,
        "entry_count": len(entries),
        "entries": entries,
    }
    bundle = _build_bundle("runtime_index", payload)
    fp = bundle["fingerprint"]
    return _write_json(GAWM_RUNTIME / f"{fp}.json", bundle)
