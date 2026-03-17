#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


THIS_FILE = Path(__file__).resolve()
WORKSPACE_ROOT = THIS_FILE.parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from self_actualize.runtime.command_membrane_runtime import main


if __name__ == "__main__":
    main()
