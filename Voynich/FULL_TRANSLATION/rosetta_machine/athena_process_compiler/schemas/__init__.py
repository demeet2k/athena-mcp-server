"""
schemas -- Core data model for the Athena Process Language Compiler.

Re-exports every public dataclass and the Truth type alias so that
downstream code can do:

    from athena_process_compiler.schemas import (
        RawToken, ParseCandidate, ParsedToken,
        OperatorIR,
        NativeRender, VerificationBundle,
        Truth,
    )
"""

from athena_process_compiler.schemas.artifacts import (
    NativeRender,
    VerificationBundle,
)
from athena_process_compiler.schemas.ir import OperatorIR
from athena_process_compiler.schemas.tokens import (
    ParseCandidate,
    ParsedToken,
    RawToken,
    Truth,
)

__all__ = [
    # Type alias
    "Truth",
    # Token lifecycle
    "RawToken",
    "ParseCandidate",
    "ParsedToken",
    # Intermediate representation
    "OperatorIR",
    # Artifacts & verification
    "NativeRender",
    "VerificationBundle",
]
