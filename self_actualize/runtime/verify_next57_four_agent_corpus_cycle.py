from __future__ import annotations

try:
    from .next57_prime_runtime import verify_main
except ImportError:
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from self_actualize.runtime.next57_prime_runtime import verify_main


if __name__ == "__main__":
    raise SystemExit(verify_main())
