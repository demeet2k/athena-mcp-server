from __future__ import annotations

import json
import sys
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from self_actualize.runtime.canonical_four_agent_57_loop import verify_canonical_four_agent_57_loop  # noqa: E402


def main() -> int:
    result = verify_canonical_four_agent_57_loop()
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
