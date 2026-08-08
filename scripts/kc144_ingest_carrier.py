#!/usr/bin/env python3
"""Decode the immutable KC144 registry archive from a lossless RGB PNG carrier."""
from __future__ import annotations

import hashlib
import io
import struct
import sys
import urllib.request
from pathlib import Path

from PIL import Image

MAGIC = b"KC144PNG1"
EXPECTED_SIZE = 1_300_124
EXPECTED_SHA256 = "312d984d988797311ac42e1d8b2323b9d8e87877c1c05679a93189c18e861f7d"


def ingest(url: str, destination: Path) -> dict[str, object]:
    request = urllib.request.Request(url, headers={"User-Agent": "athena-kc144-ingest/1"})
    with urllib.request.urlopen(request, timeout=60) as response:
        image_bytes = response.read()
    pixels = Image.open(io.BytesIO(image_bytes)).convert("RGB").tobytes()
    if pixels[: len(MAGIC)] != MAGIC:
        raise RuntimeError("KC144 carrier magic mismatch")
    cursor = len(MAGIC)
    size = struct.unpack(">Q", pixels[cursor : cursor + 8])[0]
    cursor += 8
    embedded_digest = pixels[cursor : cursor + 32].hex()
    cursor += 32
    if size != EXPECTED_SIZE:
        raise RuntimeError(f"KC144 carrier size mismatch: {size} != {EXPECTED_SIZE}")
    payload = pixels[cursor : cursor + size]
    digest = hashlib.sha256(payload).hexdigest()
    if embedded_digest != EXPECTED_SHA256 or digest != EXPECTED_SHA256:
        raise RuntimeError(
            f"KC144 carrier digest mismatch: embedded={embedded_digest} decoded={digest}"
        )
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    temporary.write_bytes(payload)
    temporary.replace(destination)
    result = {
        "destination": str(destination),
        "size_bytes": len(payload),
        "sha256": digest,
        "image_size_bytes": len(image_bytes),
    }
    print(result)
    return result


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: kc144_ingest_carrier.py URL DESTINATION")
    ingest(sys.argv[1], Path(sys.argv[2]))


if __name__ == "__main__":
    main()
