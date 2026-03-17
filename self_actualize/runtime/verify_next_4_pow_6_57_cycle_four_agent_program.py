from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SELF = ROOT / "self_actualize"

STATE = SELF / "next57_lp_57omega_program_state.json"
COMPAT = SELF / "next57_lp_57omega_compatibility_mirrors.json"
VERIFY = SELF / "next57_lp_57omega_verification.json"
VERIFY_ALIAS = SELF / "next_4_pow_6_57_cycle_program_verification.json"
VERIFY_SWARM = SELF / "next_4_pow_6_57_cycle_swarm_verification.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    failures: list[str] = []
    state = load(STATE)
    compat = load(COMPAT)

    if state.get("status") != "SUPERSEDED_BY_CANONICAL_FOUR_AGENT_COUNCIL":
        failures.append("next57 state is not marked superseded")
    if state.get("canonical_authority") != "self_actualize/four_agent_57_loop_program.json":
        failures.append("next57 state does not point to canonical four-agent ledger")
    if compat.get("canonical_authority") != "self_actualize/four_agent_57_loop_program.json":
        failures.append("next57 compat registry does not point to canonical four-agent ledger")

    payload = {
        "generated_at": state.get("generated_at"),
        "truth": "OK" if not failures else "FAIL",
        "status": "HISTORICAL_ONLY",
        "canonical_authority": "self_actualize/four_agent_57_loop_program.json",
        "failures": failures,
    }

    for path in [VERIFY, VERIFY_ALIAS, VERIFY_SWARM]:
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(payload, indent=2))
    if failures:
        sys.exit(1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
