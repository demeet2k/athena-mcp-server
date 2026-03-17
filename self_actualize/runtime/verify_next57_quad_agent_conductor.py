from __future__ import annotations

import json
from pathlib import Path

from self_actualize.runtime import derive_next57_quad_agent_conductor as conductor


ROOT = Path(__file__).resolve().parents[2]
VERIFY_JSON_PATH = ROOT / "self_actualize" / "next57_quad_agent_conductor_verification.json"


def main() -> None:
    verification = conductor.render_verification()
    VERIFY_JSON_PATH.write_text(json.dumps(verification, indent=2) + "\n", encoding="utf-8")
    if not verification["all_passed"]:
        failed = [name for name, passed in verification["checks"].items() if not passed]
        raise SystemExit(f"verification failed: {', '.join(failed)}")
    print("next57 quad-agent conductor verification: OK")


if __name__ == "__main__":
    main()
