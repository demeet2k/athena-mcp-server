from __future__ import annotations

import runpy
from pathlib import Path


HERE = Path(__file__).resolve().parent
CANONICAL_REFRESH = HERE / "temp_lp57_hsigma_refresh.py"


def main() -> int:
    if not CANONICAL_REFRESH.exists():
        raise FileNotFoundError(f"Missing canonical LP-57Ω refresh script: {CANONICAL_REFRESH}")
    runpy.run_path(str(CANONICAL_REFRESH), run_name="__main__")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
