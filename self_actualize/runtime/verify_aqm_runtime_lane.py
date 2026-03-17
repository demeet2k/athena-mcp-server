from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
LIVE_ROOT = WORKSPACE_ROOT / "MATH" / "LIVE_PROMOTED" / "aqm_kernel_qphi_planet9"
OUTPUT_JSON_PATH = SELF_ACTUALIZE_ROOT / "aqm_runtime_lane.json"
DERIVATION_COMMAND = "python -m self_actualize.runtime.verify_aqm_runtime_lane"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_command(args: list[str]) -> dict:
    completed = subprocess.run(
        args,
        cwd=LIVE_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return {
        "command": " ".join(args),
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
        "ok": completed.returncode == 0,
    }


def verify_payload() -> dict:
    results = [
        run_command([sys.executable, "-m", "aqm.cli", "demo"]),
        run_command([sys.executable, "-m", "aqm.apps.planet9.cli", "--help"]),
    ]
    truth = "OK" if all(item["ok"] for item in results) else "FAIL"
    return {
        "generated_at": utc_now(),
        "derivation_command": DERIVATION_COMMAND,
        "truth": truth,
        "live_root": str(LIVE_ROOT),
        "checks": results,
        "next_seed": "Q26",
    }


def main() -> int:
    payload = verify_payload()
    OUTPUT_JSON_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote aqm runtime lane json: {OUTPUT_JSON_PATH}")
    return 0 if payload["truth"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
