from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from athena_mcp.deployment import DEPLOYMENT_VERSION, validate_image_ref

_NAME = re.compile(r"^[a-z0-9](?:[-a-z0-9]{0,61}[a-z0-9])?$")


def _name(value: str, field: str) -> str:
    text = str(value or "").strip()
    if not _NAME.fullmatch(text):
        raise ValueError(f"{field} must be a DNS label")
    return text


def _sha(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".tmp-{os.getpid()}")
    temporary.write_bytes(data)
    temporary.replace(path)


def render(
    *,
    image: str,
    output: Path,
    receipt: Path,
    namespace: str,
    secret_name: str,
    pvc_name: str,
    template: Path | None = None,
) -> dict:
    image_value = validate_image_ref(image, require_digest=True)
    values = {
        "__IMAGE__": image_value["image_ref"],
        "__NAMESPACE__": _name(namespace, "namespace"),
        "__SECRET_NAME__": _name(secret_name, "secret_name"),
        "__PVC_NAME__": _name(pvc_name, "pvc_name"),
    }
    template_path = template or Path(__file__).with_name("kubernetes.yaml.tmpl")
    template_bytes = template_path.read_bytes()
    rendered = template_bytes.decode("utf-8")
    for marker, value in values.items():
        rendered = rendered.replace(marker, value)
    unresolved = sorted(set(re.findall(r"__[A-Z0-9_]+__", rendered)))
    if unresolved:
        raise ValueError(f"unresolved template markers: {unresolved}")
    rendered_bytes = rendered.encode("utf-8")
    _atomic_write(output, rendered_bytes)
    result = {
        "schema": "ATHENA.DEPLOYMENT.RENDER.RECEIPT.2",
        "deployment_version": DEPLOYMENT_VERSION,
        "image_ref": image_value["image_ref"],
        "image_digest": image_value["digest"],
        "namespace": values["__NAMESPACE__"],
        "secret_name": values["__SECRET_NAME__"],
        "pvc_name": values["__PVC_NAME__"],
        "template_sha256": _sha(template_bytes),
        "rendered_sha256": _sha(rendered_bytes),
        "output": str(output),
        "boundary": "Rendering binds deterministic bytes to an exact image digest; it does not apply Kubernetes objects or activate traffic.",
    }
    _atomic_write(
        receipt,
        (json.dumps(result, indent=2, sort_keys=True) + "\n").encode("utf-8"),
    )
    return result


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--receipt", required=True, type=Path)
    parser.add_argument("--namespace", default="athena")
    parser.add_argument("--secret-name", default="athena-http-token")
    parser.add_argument("--pvc-name", default="athena-state")
    parser.add_argument("--template", type=Path)
    args = parser.parse_args(argv)
    result = render(
        image=args.image,
        output=args.output,
        receipt=args.receipt,
        namespace=args.namespace,
        secret_name=args.secret_name,
        pvc_name=args.pvc_name,
        template=args.template,
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
