from __future__ import annotations

import json

from .canonical_four_agent_57_loop import verify_canonical_four_agent_57_loop


def main() -> int:
    result = verify_canonical_four_agent_57_loop()
    print(json.dumps(result, indent=2))
    return 0 if result.get("truth") == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
