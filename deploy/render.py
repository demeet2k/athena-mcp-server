#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from athena_mcp.deployment import validate_image_ref


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def render(image: str, template: Path, output: Path, receipt: Path | None) -> dict:
    validated = validate_image_ref(image, require_digest=True)
    source = template.read_text(encoding="utf-8")
    count = source.count("@@IMAGE@@")
    if count != 1:
        raise ValueError(f"template must contain exactly one @@IMAGE@@ placeholder, observed {count}")
    rendered = source.replace("@@IMAGE@@", validated["image_ref"])
    if "@@IMAGE@@" in rendered:
        raise ValueError("unresolved image placeholder")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rendered, encoding="utf-8")
    value = {
        "schema": "ATHENA.DEPLOYMENT.RENDER.RECEIPT.1",
        "image_ref": validated["image_ref"],
        "image_digest": validated["digest"],
        "template": str(template),
        "template_sha256": sha256(source.encode("utf-8")),
        "output": str(output),
        "output_sha256": sha256(rendered.encode("utf-8")),
        "status": "PASS",
        "boundary": "Rendering binds an exact digest into static deployment intent; it does not apply the manifest or activate a host.",
    }
    if receipt is not None:
        receipt.parent.mkdir(parents=True, exist_ok=True)
        receipt.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument(
        "--template",
        type=Path,
        default=Path("deploy/kubernetes/athena.yaml.tmpl"),
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    print(json.dumps(render(args.image, args.template, args.output, args.receipt), sort_keys=True))


if __name__ == "__main__":
    main()
