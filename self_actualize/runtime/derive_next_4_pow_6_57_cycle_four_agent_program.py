from __future__ import annotations

import sys
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from self_actualize.runtime.next_4_pow_6_57_cycle_four_agent_program_impl import main


if __name__ == "__main__":
    raise SystemExit(main())
