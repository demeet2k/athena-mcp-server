from __future__ import annotations

import argparse

from .engine import SelfActualizeEngine


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Self Actualize framework scaffold.")
    parser.add_argument("objective", nargs="+", help="Objective text to normalize and process.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    objective = " ".join(args.objective).strip()
    engine = SelfActualizeEngine()
    packet = engine.run(objective)
    print(engine.packet_to_json(packet))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

