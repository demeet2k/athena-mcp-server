from __future__ import annotations

import json

from .four_agent_57_loop_canonical_runtime import write_canonical_four_agent_57_loop


def main() -> int:
    result = write_canonical_four_agent_57_loop("four_agent_loop_v3")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
