#!/usr/bin/env python3
"""Decode, verify and safely apply the KC144 runtime integration overlay."""
from __future__ import annotations

import hashlib
import io
import json
import os
import struct
import sys
import tarfile
import urllib.request
from pathlib import Path, PurePosixPath

from PIL import Image

MAGIC = b"KC144OVL2"
EXPECTED_SIZE = 21_624
EXPECTED_SHA256 = "43f5a506c3ca0737a7d690fd52e05d1a67a9a159e800f3a66bfc221ea3512a1e"
EXPECTED_PATHS = {
    "athena_mcp/aor_development_surface.py",
    "athena_mcp/hub_dispatch.py",
    "athena_mcp/hub_server.py",
    "athena_mcp/kc144_registry_pack.py",
    "athena_mcp/kc144_registry_protocol.py",
    "athena_mcp/orchestration_field/__init__.py",
    "athena_mcp/orchestration_field/compiler.py",
    "athena_mcp/orchestration_field/ledger.py",
    "athena_mcp/orchestration_field_protocol.py",
    "docs/KC144_AUTHORITATIVE_REGISTRY_PACK.md",
    "pyproject.toml",
    "receipts/kc144_runtime_integration_manifest.json",
    "scripts/reconstruct_kc144_registry_pack.py",
    "tests/test_field_surface_composition.py",
    "tests/test_hub_server.py",
    "tests/test_kc144_registry_pack.py",
}


def _safe_name(name: str) -> str:
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise RuntimeError(f"unsafe overlay member: {name}")
    return path.as_posix()


def _download_decode(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "athena-kc144-overlay/2"})
    with urllib.request.urlopen(request, timeout=60) as response:
        image_bytes = response.read()
    pixels = Image.open(io.BytesIO(image_bytes)).convert("RGB").tobytes()
    if pixels[: len(MAGIC)] != MAGIC:
        raise RuntimeError("KC144 overlay magic mismatch")
    cursor = len(MAGIC)
    size = struct.unpack(">Q", pixels[cursor : cursor + 8])[0]
    cursor += 8
    embedded = pixels[cursor : cursor + 32].hex()
    cursor += 32
    if size != EXPECTED_SIZE:
        raise RuntimeError(f"KC144 overlay size mismatch: {size} != {EXPECTED_SIZE}")
    payload = pixels[cursor : cursor + size]
    observed = hashlib.sha256(payload).hexdigest()
    if embedded != EXPECTED_SHA256 or observed != EXPECTED_SHA256:
        raise RuntimeError(f"KC144 overlay digest mismatch: embedded={embedded} observed={observed}")
    return payload


def apply(url: str, root: Path) -> dict[str, object]:
    root = root.resolve()
    payload = _download_decode(url)
    files: dict[str, bytes] = {}
    with tarfile.open(fileobj=io.BytesIO(payload), mode="r:xz") as archive:
        for member in archive.getmembers():
            if not member.isfile() or member.islnk() or member.issym():
                raise RuntimeError(f"non-regular overlay member rejected: {member.name}")
            name = _safe_name(member.name)
            handle = archive.extractfile(member)
            if handle is None:
                raise RuntimeError(f"unreadable overlay member: {name}")
            files[name] = handle.read()
    if set(files) != EXPECTED_PATHS:
        raise RuntimeError(f"overlay path mismatch: missing={sorted(EXPECTED_PATHS-set(files))} extra={sorted(set(files)-EXPECTED_PATHS)}")
    for name, data in files.items():
        destination = (root / name).resolve()
        if not destination.is_relative_to(root):
            raise RuntimeError(f"overlay escaped repository root: {name}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_name(destination.name + ".kc144tmp")
        temporary.write_bytes(data)
        os.chmod(temporary, 0o755 if name.startswith("scripts/") else 0o644)
        temporary.replace(destination)
    manifest_path = root / "receipts/kc144_runtime_integration_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    defects = []
    for item in manifest.get("files", []):
        path = root / item["path"]
        data = path.read_bytes()
        observed = hashlib.sha256(data).hexdigest()
        if len(data) != item["size_bytes"] or observed != item["sha256"]:
            defects.append({"path": item["path"], "size": len(data), "sha256": observed})
    if defects:
        raise RuntimeError(f"overlay file-manifest mismatch: {defects}")
    result = {
        "status": "PASS",
        "overlay_sha256": EXPECTED_SHA256,
        "overlay_size_bytes": len(payload),
        "applied_files": len(files),
        "manifest_files_verified": len(manifest.get("files", [])),
    }
    print(json.dumps(result, sort_keys=True))
    return result


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: kc144_ingest_runtime_overlay.py URL REPOSITORY_ROOT")
    apply(sys.argv[1], Path(sys.argv[2]))


if __name__ == "__main__":
    main()
