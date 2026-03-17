from __future__ import annotations

import json

from .derive_a_b_seed_inversion import (
    MASTER_STATE_PATH,
    PROTOCOL_JSON_PATH,
    REGISTRY_PATH,
    VERIFICATION_PATH,
    verification_payload,
    read_json,
)


def verify_seed_inversion() -> dict:
    registry = read_json(REGISTRY_PATH)
    master_state = read_json(MASTER_STATE_PATH)
    protocol = read_json(PROTOCOL_JSON_PATH)
    result = verification_payload(registry, master_state, protocol)
    VERIFICATION_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> int:
    result = verify_seed_inversion()
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
