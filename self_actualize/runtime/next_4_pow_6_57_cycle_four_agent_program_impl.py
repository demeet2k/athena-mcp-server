from __future__ import annotations

import json

from .next57_historical_wrapper import write_historical_next57_wrappers


def main() -> int:
    result = write_historical_next57_wrappers("next_4_pow_6_57_cycle_four_agent_program_impl")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
