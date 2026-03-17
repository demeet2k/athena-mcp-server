from __future__ import annotations

import sys
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from self_actualize.runtime.verify_next57_four_agent_corpus_cycle import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
