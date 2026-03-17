from __future__ import annotations

import json
import sys
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from self_actualize.runtime.lp57omega_b_prime_support import (
    B_PRIME_DOC_MIRROR,
    B_PRIME_DOC_PATH,
    B_PRIME_MANIFEST_REPORT_PATH,
    B_PRIME_REGISTRY_MIRROR,
    B_PRIME_REGISTRY_PATH,
    load_json,
    verify_b_prime_registry,
    write_json,
)


def main() -> int:
    registry = load_json(B_PRIME_REGISTRY_PATH)
    registry_mirror = load_json(B_PRIME_REGISTRY_MIRROR)
    markdown = B_PRIME_DOC_PATH.read_text(encoding="utf-8")
    markdown_mirror = B_PRIME_DOC_MIRROR.read_text(encoding="utf-8")
    verification = verify_b_prime_registry(registry, markdown)
    checks = list(verification.get("checks", []))
    checks.append(
        {
            "name": "registry_mirror_parity",
            "ok": registry == registry_mirror,
            "detail": f"mirror={B_PRIME_REGISTRY_MIRROR}",
        }
    )
    checks.append(
        {
            "name": "markdown_mirror_parity",
            "ok": markdown == markdown_mirror,
            "detail": f"mirror={B_PRIME_DOC_MIRROR}",
        }
    )
    verification["checks"] = checks
    verification["check_count"] = len(checks)
    verification["truth"] = "OK" if all(check["ok"] for check in checks) else "DRIFT"
    write_json(B_PRIME_MANIFEST_REPORT_PATH, verification)
    print(json.dumps(verification, indent=2))
    return 0 if verification["truth"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
