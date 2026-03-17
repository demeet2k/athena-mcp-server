"""
verifiers -- Verification subsystem for the Athena Process Language Compiler.

Modules:
    consistency   : Cross-backend consistency checker.
    replay        : Replay-chain verification.
    truth_lattice : Truth lattice algebra (OK > NEAR > AMBIG > FAIL).
"""

from athena_process_compiler.verifiers.truth_lattice import (
    TRUTH_ORDER,
    truth_meet,
    truth_join,
    can_promote,
)

__all__ = [
    "TRUTH_ORDER",
    "truth_meet",
    "truth_join",
    "can_promote",
]
