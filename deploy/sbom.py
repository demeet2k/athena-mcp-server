from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

INCLUDED_ROOTS = ("athena_mcp", "deploy")
INCLUDED_FILES = ("pyproject.toml", "Dockerfile", "compose.yaml")
EXCLUDED_PARTS = {"__pycache__", ".git", "build", "dist"}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _files(root: Path) -> list[Path]:
    result: list[Path] = []
    for rel in INCLUDED_ROOTS:
        base = root / rel
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.is_file() and not EXCLUDED_PARTS.intersection(path.parts):
                result.append(path)
    for rel in INCLUDED_FILES:
        path = root / rel
        if path.is_file():
            result.append(path)
    return sorted(set(result), key=lambda path: path.relative_to(root).as_posix())


def generate(root: Path, output: Path, *, package_version: str, source_head: str) -> dict:
    root = root.resolve()
    files = _files(root)
    document_namespace = (
        "https://athena.invalid/spdx/athena-canonical-mcp/"
        + source_head
        + "/"
        + hashlib.sha256("\n".join(path.relative_to(root).as_posix() for path in files).encode()).hexdigest()[:16]
    )
    spdx_files = []
    relationships = []
    for index, path in enumerate(files, start=1):
        rel = path.relative_to(root).as_posix()
        spdx_id = f"SPDXRef-File-{index}"
        spdx_files.append(
            {
                "SPDXID": spdx_id,
                "fileName": "./" + rel,
                "checksums": [{"algorithm": "SHA256", "checksumValue": _sha(path)}],
                "licenseConcluded": "NOASSERTION",
                "licenseInfoInFiles": ["NOASSERTION"],
                "copyrightText": "NOASSERTION",
            }
        )
        relationships.append(
            {
                "spdxElementId": "SPDXRef-Package-athena",
                "relationshipType": "CONTAINS",
                "relatedSpdxElement": spdx_id,
            }
        )
    document = {
        "spdxVersion": "SPDX-2.3",
        "dataLicense": "CC0-1.0",
        "SPDXID": "SPDXRef-DOCUMENT",
        "name": f"athena-canonical-mcp-{package_version}",
        "documentNamespace": document_namespace,
        "creationInfo": {
            "created": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "creators": ["Tool: athena-deployment-sbom-2"],
            "licenseListVersion": "3.25",
        },
        "packages": [
            {
                "SPDXID": "SPDXRef-Package-athena",
                "name": "athena-canonical-mcp",
                "versionInfo": package_version,
                "downloadLocation": "NOASSERTION",
                "filesAnalyzed": True,
                "licenseConcluded": "NOASSERTION",
                "licenseDeclared": "NOASSERTION",
                "copyrightText": "NOASSERTION",
                "externalRefs": [
                    {
                        "referenceCategory": "OTHER",
                        "referenceType": "athena-source-head",
                        "referenceLocator": source_head,
                    }
                ],
            }
        ],
        "files": spdx_files,
        "relationships": [
            {
                "spdxElementId": "SPDXRef-DOCUMENT",
                "relationshipType": "DESCRIBES",
                "relatedSpdxElement": "SPDXRef-Package-athena",
            },
            *relationships,
        ],
        "athenaBoundary": "This source SBOM inventories repository bytes; it does not prove the contents of a built or deployed OCI image without a separately bound image attestation.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "schema": "ATHENA.SBOM.RECEIPT.2",
        "output": str(output),
        "file_count": len(files),
        "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "source_head": source_head,
        "package_version": package_version,
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--package-version", required=True)
    parser.add_argument("--source-head", required=True)
    args = parser.parse_args(argv)
    print(
        json.dumps(
            generate(
                args.root,
                args.output,
                package_version=args.package_version,
                source_head=args.source_head,
            ),
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
