from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    ROOT = Path(__file__).resolve().parents[2]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from self_actualize.runtime.command_membrane_entrypoint import main
else:
    from .command_membrane_entrypoint import main


if __name__ == "__main__":
    raise SystemExit(main())
