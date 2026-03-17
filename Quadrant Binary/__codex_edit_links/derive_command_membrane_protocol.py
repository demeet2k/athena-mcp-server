from __future__ import annotations

import json

from .command_membrane import CommandMembraneService


def derive_command_membrane_protocol() -> dict:
    return CommandMembraneService().build()


def main() -> int:
    print(json.dumps(derive_command_membrane_protocol(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
