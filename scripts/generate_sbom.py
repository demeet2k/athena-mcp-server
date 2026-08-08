#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import zipfile
from datetime import datetime, timezone
from pathlib import Path


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def created_time() -> str:
    epoch = int(os.getenv("SOURCE_DATE_EPOCH", "0"))
    return datetime.fromtimestamp(epoch, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build(wheel: Path, output: Path) -> dict:
    wheel_bytes = wheel.read_bytes()
    wheel_sha = sha256(wheel_bytes)
    files = []
    relationships = []
    with zipfile.ZipFile(wheel) as archive:
        for name in sorted(item.filename for item in archive.infolist() if not item.is_dir()):
            data = archive.read(name)
            identifier = "SPDXRef-File-" + sha256(name.encode())[:24]
            files.append(
                {
                    "fileName": name,
                    "SPDXID": identifier,
                    "checksums": [{"algorithm": "SHA256", "checksumValue": sha256(data)}],
                }
            )
            relationships.append(
                {
                    "spdxElementId": "SPDXRef-Package",
                    "relationshipType": "CONTAINS",
                    "relatedSpdxElement": identifier,
                }
            )
    document = {
        "spdxVersion": "SPDX-2.3",
        "dataLicense": "CC0-1.0",
        "SPDXID": "SPDXRef-DOCUMENT",
        "name": wheel.name + "-contents",
        "documentNamespace": "urn:athena:sbom:" + wheel_sha,
        "creationInfo": {
            "created": created_time(),
            "creators": ["Tool: athena-generate-sbom/1"],
            "comment": "Package-content SBOM; BuildKit image SBOM/provenance are attached separately to the OCI manifest.",
        },
        "packages": [
            {
                "name": "athena-canonical-mcp",
                "SPDXID": "SPDXRef-Package",
                "versionInfo": wheel.name.split("-")[1],
                "downloadLocation": "NOASSERTION",
                "filesAnalyzed": True,
                "checksums": [{"algorithm": "SHA256", "checksumValue": wheel_sha}],
                "licenseConcluded": "NOASSERTION",
                "licenseDeclared": "NOASSERTION",
                "copyrightText": "NOASSERTION",
            }
        ],
        "files": files,
        "relationships": relationships,
        "documentComment": "SBOM inventory is not a vulnerability scan, signature, deployment receipt, or empirical/Y1 authority.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    return {"status": "PASS", "wheel_sha256": wheel_sha, "file_count": len(files)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("wheel", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build(args.wheel, args.output), sort_keys=True))


if __name__ == "__main__":
    main()
