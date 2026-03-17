from __future__ import annotations

from self_actualize.runtime.qshrink_refine_common import (
    QSHRINK_NEXT4_STATE_PATH,
    load_next4_state,
)


DERIVATION_COMMAND = "python -m self_actualize.runtime.derive_qshrink_network_integration_flower"


def main() -> int:
    next4_state = load_next4_state()
    print(
        "DEPRECATED: derive_qshrink_network_integration_flower no longer writes live outputs. "
        f"Use derive_qshrink_network_integration with {QSHRINK_NEXT4_STATE_PATH}. "
        f"Operational current is {next4_state['operational_current']} and compiled bundle terminal is "
        f"{next4_state['compiled_bundle']['terminal']}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
