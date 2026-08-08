from __future__ import annotations

"""Digest-bound access and cross-registry lenses for the KC144 crystal pack.

The authoritative XZ/TAR archive is installed as package data. Import remains
light: bytes are read, hashed and expanded only when a registry tool or
resource is used. Every route is deterministic and bounded. Integrity,
lexical matching, graph navigation and source linkage never promote authority,
convert a proposal into evidence, or discharge an external HOLD.
"""

import hashlib
import io
import json
import tarfile
from functools import lru_cache
from importlib import resources
from pathlib import PurePosixPath
from typing import Any, Iterable, Mapping

PACK_VERSION = "ATHENA.KC144.REGISTRY.PACK.2"
PACK_MEMBER = "data/kc144-core-registries.tar.xz"
PACK_ENCODING = "xz(tar)-package-data"
PACK_SHA256 = "312d984d988797311ac42e1d8b2323b9d8e87877c1c05679a93189c18e861f7d"
PACK_SIZE_BYTES = 1_300_124
MANIFEST_DIGEST = "cbd069a911971c7eec9d6851034d3cbc3b53eeaef9c36201966351423bfdbb35"

EXPECTED_COUNTS = {
    "cells": 144,
    "completion": 126,
    "coordinates": 1266,
    "datasets": 38,
    "graphs": 3210,
    "harnesses": 728,
    "math": 9771,
    "skills": 68,
    "sources": 32,
    "tools": 120,
    "transports": 9,
}

REGISTRIES: dict[str, dict[str, Any]] = {
    "manifest": {"member": "crystal/kc144.manifest.json", "format": "json", "count": 1},
    "cells": {"member": "crystal/kc144.cells.jsonl", "format": "jsonl", "count": 144},
    "metro": {"member": "crystal/metro.json", "format": "json", "count": 1},
    "completion": {"member": "data/completion_map.json", "format": "json-array", "count": 126},
    "coordinates": {"member": "data/coordinate_registry.jsonl", "format": "jsonl", "count": 1266},
    "datasets": {"member": "data/dataset_registry.json", "format": "json-array", "count": 38},
    "graphs": {"member": "data/graph_registry.jsonl", "format": "jsonl", "count": 3210},
    "harnesses": {"member": "data/harness_registry.json", "format": "json-array", "count": 728},
    "holds": {"member": "data/holds.json", "format": "json-array", "count": 4},
    "math": {"member": "data/math_registry.jsonl", "format": "jsonl", "count": 9771},
    "skills": {"member": "data/skill_registry.json", "format": "json-array", "count": 68},
    "sources": {"member": "data/source_registry.json", "format": "json-array", "count": 32},
    "surface": {"member": "data/surface_union.json", "format": "json", "count": 1},
    "tools": {"member": "data/tool_registry.json", "format": "json-array", "count": 120},
    "transports": {"member": "data/transport_registry.json", "format": "json-array", "count": 9},
    "audit": {"member": "receipts/audit_receipt.json", "format": "json", "count": 1},
    "compile_receipt": {"member": "receipts/compile_receipt.json", "format": "json", "count": 1},
    "release_candidate": {"member": "receipts/release_candidate.json", "format": "json", "count": 1},
}

ARRAY_REGISTRIES = tuple(
    name for name, descriptor in REGISTRIES.items()
    if descriptor["format"] in {"jsonl", "json-array"}
)
SEARCH_REGISTRIES = (
    "cells", "completion", "coordinates", "datasets", "graphs", "harnesses",
    "holds", "math", "skills", "sources", "tools", "transports",
)
SOURCE_LINK_REGISTRIES = (
    "coordinates", "datasets", "graphs", "harnesses", "math", "skills", "sources", "tools",
)


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


@lru_cache(maxsize=1)
def _archive_bytes() -> bytes:
    try:
        raw = resources.files(__package__).joinpath(PACK_MEMBER).read_bytes()
    except (FileNotFoundError, OSError) as exc:
        raise RuntimeError(f"KC144 registry package data is unavailable: {PACK_MEMBER}") from exc
    if len(raw) != PACK_SIZE_BYTES:
        raise RuntimeError(f"KC144 registry pack size mismatch: {len(raw)} != {PACK_SIZE_BYTES}")
    observed = hashlib.sha256(raw).hexdigest()
    if observed != PACK_SHA256:
        raise RuntimeError(f"KC144 registry pack digest mismatch: {observed}")
    return raw


def _safe_member_name(name: str) -> str:
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts:
        raise RuntimeError(f"unsafe KC144 registry archive member: {name}")
    return path.as_posix()


@lru_cache(maxsize=1)
def _members() -> dict[str, bytes]:
    result: dict[str, bytes] = {}
    try:
        with tarfile.open(fileobj=io.BytesIO(_archive_bytes()), mode="r:xz") as archive:
            for member in archive.getmembers():
                if not member.isfile():
                    continue
                name = _safe_member_name(member.name)
                handle = archive.extractfile(member)
                if handle is None:
                    raise RuntimeError(f"unreadable registry archive member: {name}")
                result[name] = handle.read()
    except (tarfile.TarError, EOFError, OSError) as exc:
        raise RuntimeError("KC144 registry archive cannot be reconstructed") from exc
    expected = {item["member"] for item in REGISTRIES.values()}
    missing = sorted(expected - set(result))
    if missing:
        raise RuntimeError(f"KC144 registry archive missing required members: {missing}")
    return result


@lru_cache(maxsize=None)
def _parse_registry(name: str) -> Any:
    descriptor = REGISTRIES.get(name)
    if descriptor is None:
        raise KeyError(f"unknown KC144 registry: {name}")
    raw = _members()[descriptor["member"]].decode("utf-8")
    if descriptor["format"] == "jsonl":
        return [json.loads(line) for line in raw.splitlines() if line.strip()]
    return json.loads(raw)


def _record_count(value: Any, descriptor: Mapping[str, Any]) -> int:
    if descriptor["format"] in {"jsonl", "json-array"}:
        return len(value)
    return 1


def _path_value(value: Any, dotted_path: str) -> Any:
    current = value
    for part in str(dotted_path).split("."):
        if not isinstance(current, Mapping) or part not in current:
            return None
        current = current[part]
    return current


def _bounded_names(names: Iterable[str] | None, *, searchable_only: bool = False) -> list[str]:
    allowed = set(SEARCH_REGISTRIES if searchable_only else REGISTRIES)
    selected = list(SEARCH_REGISTRIES if names is None and searchable_only else (names or REGISTRIES))
    result: list[str] = []
    for name in selected:
        name = str(name)
        if name not in allowed:
            raise KeyError(f"unknown or unsupported KC144 registry: {name}")
        if name not in result:
            result.append(name)
    return sorted(result)


def status(*, verify: bool = False) -> dict[str, Any]:
    result: dict[str, Any] = {
        "version": PACK_VERSION,
        "encoding": PACK_ENCODING,
        "package_member": PACK_MEMBER,
        "sha256": PACK_SHA256,
        "size_bytes": PACK_SIZE_BYTES,
        "carrier_count": 1,
        "manifest_digest": MANIFEST_DIGEST,
        "expected_counts": dict(EXPECTED_COUNTS),
        "registry_count": len(REGISTRIES),
        "lens_count": 4,
        "state": "DIGEST_BOUND_PACKAGE_DATA",
        "authority_boundary": "archive integrity, lexical retrieval, source linkage and task projection do not promote claims or discharge external HOLDs",
    }
    if verify:
        result["verification"] = verify_pack(deep=True)
    return result


def catalog() -> dict[str, Any]:
    members = _members()
    items = []
    for name, descriptor in sorted(REGISTRIES.items()):
        member = descriptor["member"]
        items.append({
            "name": name,
            "member": member,
            "format": descriptor["format"],
            "expected_count": descriptor["count"],
            "compressed_member_present": member in members,
            "uncompressed_bytes": len(members[member]),
        })
    return {"version": PACK_VERSION, "registries": items, "count": len(items), "pack_sha256": PACK_SHA256}


def manifest() -> dict[str, Any]:
    value = _parse_registry("manifest")
    if value.get("manifest_digest") != MANIFEST_DIGEST:
        raise RuntimeError("KC144 manifest digest does not match registry-pack identity")
    return value


def query_registry(
    name: str,
    *,
    query: str | None = None,
    filters: Mapping[str, Any] | None = None,
    offset: int = 0,
    limit: int = 100,
) -> dict[str, Any]:
    if int(offset) < 0:
        raise ValueError("offset must be non-negative")
    if not 1 <= int(limit) <= 500:
        raise ValueError("limit must be in 1..500")
    descriptor = REGISTRIES.get(name)
    if descriptor is None:
        raise KeyError(f"unknown KC144 registry: {name}")
    value = _parse_registry(name)
    if descriptor["format"] not in {"jsonl", "json-array"}:
        return {
            "version": PACK_VERSION,
            "registry": name,
            "format": descriptor["format"],
            "total": 1,
            "returned": 1,
            "value": value,
            "pack_sha256": PACK_SHA256,
        }
    records = list(value)
    needle = str(query).casefold() if query else None
    exact_filters = dict(filters or {})
    selected = []
    for record in records:
        if needle and needle not in _canonical_json(record).casefold():
            continue
        if exact_filters and any(_path_value(record, key) != expected for key, expected in exact_filters.items()):
            continue
        selected.append(record)
    start = int(offset)
    end = start + int(limit)
    page = selected[start:end]
    return {
        "version": PACK_VERSION,
        "registry": name,
        "format": descriptor["format"],
        "total": len(selected),
        "offset": start,
        "returned": len(page),
        "next_offset": end if end < len(selected) else None,
        "items": page,
        "pack_sha256": PACK_SHA256,
        "result_digest": hashlib.sha256(_canonical_json(page).encode("utf-8")).hexdigest(),
    }


def cross_search(
    query: str,
    *,
    registries: Iterable[str] | None = None,
    limit: int = 100,
    per_registry: int = 25,
) -> dict[str, Any]:
    needle = str(query).strip().casefold()
    if not needle:
        raise ValueError("query must be non-empty")
    if not 1 <= int(limit) <= 500:
        raise ValueError("limit must be in 1..500")
    if not 1 <= int(per_registry) <= 100:
        raise ValueError("per_registry must be in 1..100")
    selected_names = _bounded_names(registries, searchable_only=True)
    candidates: list[tuple[int, str, int, list[str], Any]] = []
    totals: dict[str, int] = {}
    for name in selected_names:
        matches: list[tuple[int, int, list[str], Any]] = []
        for index, record in enumerate(_parse_registry(name)):
            canonical = _canonical_json(record).casefold()
            occurrences = canonical.count(needle)
            if not occurrences:
                continue
            fields: list[str] = []
            if isinstance(record, Mapping):
                fields = sorted(
                    str(key) for key, value in record.items()
                    if needle in _canonical_json(value).casefold()
                )
            matches.append((occurrences, index, fields, record))
        matches.sort(key=lambda row: (-row[0], row[1]))
        totals[name] = len(matches)
        for occurrences, index, fields, record in matches[: int(per_registry)]:
            candidates.append((occurrences, name, index, fields, record))
    candidates.sort(key=lambda row: (-row[0], row[1], row[2]))
    items = [
        {
            "registry": name,
            "record_index": index,
            "occurrences": occurrences,
            "matching_fields": fields,
            "record": record,
        }
        for occurrences, name, index, fields, record in candidates[: int(limit)]
    ]
    return {
        "version": PACK_VERSION,
        "query": query,
        "registries": selected_names,
        "total_matches_by_registry": totals,
        "returned": len(items),
        "items": items,
        "ranking_law": "descending exact casefolded substring occurrence count, then registry name and immutable record order",
        "semantic_boundary": "lexical retrieval only; result order is not evidence strength, causal support or authority",
        "pack_sha256": PACK_SHA256,
        "result_digest": hashlib.sha256(_canonical_json(items).encode("utf-8")).hexdigest(),
    }


def _references_source(record: Any, source_id: str) -> bool:
    if not isinstance(record, Mapping):
        return False
    if record.get("source_id") == source_id:
        return True
    if source_id in (record.get("source_refs") or []):
        return True
    for occurrence in record.get("source_occurrences") or []:
        if isinstance(occurrence, Mapping) and occurrence.get("source_id") == source_id:
            return True
    return False


def source_bundle(source_id: str, *, limit_per_registry: int = 100) -> dict[str, Any]:
    source_id = str(source_id).strip()
    if not source_id:
        raise ValueError("source_id must be non-empty")
    if not 1 <= int(limit_per_registry) <= 500:
        raise ValueError("limit_per_registry must be in 1..500")
    bundles: dict[str, Any] = {}
    counts: dict[str, int] = {}
    truncated: list[str] = []
    for name in SOURCE_LINK_REGISTRIES:
        matches = [record for record in _parse_registry(name) if _references_source(record, source_id)]
        counts[name] = len(matches)
        if len(matches) > int(limit_per_registry):
            truncated.append(name)
        bundles[name] = matches[: int(limit_per_registry)]
    source_records = bundles.get("sources") or []
    return {
        "version": PACK_VERSION,
        "source_id": source_id,
        "source_found": bool(source_records),
        "source": source_records[0] if source_records else None,
        "counts": counts,
        "truncated_registries": truncated,
        "related": bundles,
        "link_law": "exact source_id, source_refs or source_occurrences.source_id equality only",
        "pack_sha256": PACK_SHA256,
        "result_digest": hashlib.sha256(_canonical_json({"counts": counts, "related": bundles}).encode("utf-8")).hexdigest(),
    }


def cell_bundle(gid: int, *, task_limit: int = 100) -> dict[str, Any]:
    gid = int(gid)
    if not 1 <= gid <= 144:
        raise ValueError("gid must be in 1..144")
    if not 1 <= int(task_limit) <= 500:
        raise ValueError("task_limit must be in 1..500")
    cell = next((item for item in _parse_registry("cells") if _path_value(item, "address.gid") == gid), None)
    if cell is None:
        raise RuntimeError(f"KC144 cell GID{gid:03d} is missing")
    hosted_tasks = [task for task in _parse_registry("completion") if task.get("host_gid") == gid]
    semantic_tasks = [task for task in _parse_registry("completion") if task.get("semantic_gid") == gid]
    return {
        "version": PACK_VERSION,
        "gid": gid,
        "sid": _path_value(cell, "address.sid"),
        "cell": cell,
        "completion_tasks": {
            "hosted_total": len(hosted_tasks),
            "semantic_total": len(semantic_tasks),
            "hosted": hosted_tasks[: int(task_limit)],
            "semantic": semantic_tasks[: int(task_limit)],
            "truncated": len(hosted_tasks) > int(task_limit) or len(semantic_tasks) > int(task_limit),
        },
        "mapping_boundary": "task links use exact host_gid/semantic_gid; hosted_oids remain immutable opaque identities unless an object registry is supplied",
        "pack_sha256": PACK_SHA256,
    }


def completion_frontier(
    *,
    completed_task_ids: Iterable[str] | None = None,
    limit: int = 100,
) -> dict[str, Any]:
    if not 1 <= int(limit) <= 500:
        raise ValueError("limit must be in 1..500")
    tasks = list(_parse_registry("completion"))
    by_id = {str(task["task_id"]): task for task in tasks}
    completed = {str(value) for value in (completed_task_ids or [])}
    unknown_completed = sorted(completed - set(by_id))
    missing_dependencies = sorted({dep for task in tasks for dep in task.get("dependencies", []) if dep not in by_id})
    ready = [
        task for task in tasks
        if task["task_id"] not in completed
        and set(task.get("dependencies") or []).issubset(completed)
    ]
    blocked = [task for task in tasks if task["task_id"] not in completed and task not in ready]
    ready.sort(key=lambda task: (task.get("task_number", 10**9), task["task_id"]))
    blocked.sort(key=lambda task: (task.get("task_number", 10**9), task["task_id"]))
    frontier = ready[: int(limit)]
    return {
        "version": PACK_VERSION,
        "snapshot_task_count": len(tasks),
        "completed_input_count": len(completed & set(by_id)),
        "unknown_completed_task_ids": unknown_completed,
        "missing_dependency_ids": missing_dependencies,
        "ready_total": len(ready),
        "blocked_total": len(blocked),
        "frontier": frontier,
        "next_blocked": blocked[: min(int(limit), 25)],
        "projection_law": "a task is ready iff it is not in completed_task_ids and every declared dependency is in completed_task_ids",
        "state_boundary": "this is a pure projection over the source-bound task snapshot; it does not mutate or certify live completion state",
        "pack_sha256": PACK_SHA256,
        "result_digest": hashlib.sha256(_canonical_json(frontier).encode("utf-8")).hexdigest(),
    }


def verify_pack(*, deep: bool = True) -> dict[str, Any]:
    raw = _archive_bytes()
    members = _members()
    defects: list[str] = []
    observed_counts: dict[str, int] = {}
    parsed_manifest: dict[str, Any] | None = None
    if deep:
        for name, descriptor in sorted(REGISTRIES.items()):
            try:
                value = _parse_registry(name)
                observed = _record_count(value, descriptor)
                observed_counts[name] = observed
                if observed != descriptor["count"]:
                    defects.append(f"{name}: count {observed} != {descriptor['count']}")
                if name == "manifest":
                    parsed_manifest = value
            except Exception as exc:
                defects.append(f"{name}: {type(exc).__name__}: {exc}")
    if parsed_manifest is not None:
        if parsed_manifest.get("manifest_digest") != MANIFEST_DIGEST:
            defects.append("manifest digest mismatch")
        for key, expected in EXPECTED_COUNTS.items():
            observed = parsed_manifest.get("counts", {}).get(key)
            if observed != expected:
                defects.append(f"manifest count {key}: {observed} != {expected}")
    return {
        "version": PACK_VERSION,
        "status": "PASS" if not defects else "FAIL",
        "pack_sha256": hashlib.sha256(raw).hexdigest(),
        "pack_size_bytes": len(raw),
        "members": len(members),
        "observed_counts": observed_counts,
        "defects": defects,
        "manifest_digest": MANIFEST_DIGEST,
        "authority_boundary": "PASS certifies bytes, member presence, parseability and declared counts only",
    }


__all__ = [
    "PACK_VERSION", "PACK_MEMBER", "PACK_SHA256", "PACK_SIZE_BYTES", "EXPECTED_COUNTS", "REGISTRIES",
    "status", "catalog", "manifest", "query_registry", "cross_search", "source_bundle", "cell_bundle",
    "completion_frontier", "verify_pack",
]
