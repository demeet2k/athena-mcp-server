"""
replay.py -- Replay verification for the Athena Process Language Compiler.

Replay verification ensures that a compiled operator chain can be
deterministically re-derived from its inputs.  This is the second leg
of the OK verdict (alongside consistency and witness).

A replay chain is a sequence of (input, transform, output) triples.
Verification walks the chain, re-executes each transform, and confirms
that the output matches.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

from athena_process_compiler.schemas.tokens import Truth
from athena_process_compiler.schemas.ir import OperatorIR
from athena_process_compiler.config import HASH_ALGORITHM, MAX_REPLAY_DEPTH


# ---------------------------------------------------------------------------
# Replay step dataclass
# ---------------------------------------------------------------------------

@dataclass
class ReplayStep:
    """One step in a replay chain.

    Attributes:
        step_index:      Position in the chain (0-based).
        input_hash:      Content hash of the input state.
        transform_name:  Name of the transform that was applied.
        transform_args:  Arguments passed to the transform.
        output_hash:     Content hash of the expected output state.
    """

    step_index: int
    input_hash: str
    transform_name: str
    transform_args: dict[str, Any]
    output_hash: str

    def to_dict(self) -> dict[str, Any]:
        """Return a plain-dict representation."""
        return {
            "step_index": self.step_index,
            "input_hash": self.input_hash,
            "transform_name": self.transform_name,
            "transform_args": self.transform_args,
            "output_hash": self.output_hash,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ReplayStep:
        """Construct from a plain dict."""
        return cls(
            step_index=data["step_index"],
            input_hash=data["input_hash"],
            transform_name=data["transform_name"],
            transform_args=data.get("transform_args", {}),
            output_hash=data["output_hash"],
        )


@dataclass
class ReplayChain:
    """A complete replay chain for one OperatorIR node.

    Attributes:
        operator_id: Back-reference to OperatorIR.token_id.
        steps:       Ordered list of ReplayStep entries.
        final_hash:  Content hash of the terminal output state.
    """

    operator_id: str
    steps: list[ReplayStep]
    final_hash: str

    def to_dict(self) -> dict[str, Any]:
        """Return a plain-dict representation."""
        return {
            "operator_id": self.operator_id,
            "steps": [s.to_dict() for s in self.steps],
            "final_hash": self.final_hash,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ReplayChain:
        """Construct from a plain dict."""
        return cls(
            operator_id=data["operator_id"],
            steps=[ReplayStep.from_dict(s) for s in data["steps"]],
            final_hash=data["final_hash"],
        )

    def to_json(self, **kwargs: Any) -> str:
        """Serialise to a JSON string."""
        return json.dumps(self.to_dict(), **kwargs)

    @classmethod
    def from_json(cls, raw: str) -> ReplayChain:
        """Deserialise from a JSON string."""
        return cls.from_dict(json.loads(raw))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def content_hash(data: Any) -> str:
    """Compute a deterministic content hash for any JSON-serialisable value.

    Uses canonical JSON (sorted keys, no whitespace) for reproducibility.
    """
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return hashlib.new(HASH_ALGORITHM, canonical.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Replay verification
# ---------------------------------------------------------------------------

@dataclass
class ReplayResult:
    """Outcome of a replay verification pass.

    Attributes:
        operator_id:   Back-reference to OperatorIR.token_id.
        ok:            True if every step in the chain verified.
        steps_checked: Number of steps successfully verified.
        total_steps:   Total number of steps in the chain.
        failures:      Human-readable list of step failures.
        truth:         Derived truth verdict.
    """

    operator_id: str
    ok: bool
    steps_checked: int
    total_steps: int
    failures: list[str] = field(default_factory=list)
    truth: Truth = "FAIL"

    def to_dict(self) -> dict[str, Any]:
        """Return a plain-dict representation."""
        return {
            "operator_id": self.operator_id,
            "ok": self.ok,
            "steps_checked": self.steps_checked,
            "total_steps": self.total_steps,
            "failures": self.failures,
            "truth": self.truth,
        }


def verify_chain_hashes(chain: ReplayChain) -> ReplayResult:
    """Verify internal hash-chain consistency of a ReplayChain.

    Checks that each step's output_hash equals the next step's
    input_hash, and that the final step's output_hash matches
    the chain's declared final_hash.

    This is the *structural* replay check.  It does not re-execute
    transforms (that requires a transform registry); it only validates
    that the recorded hashes form an unbroken chain.

    Args:
        chain: The replay chain to verify.

    Returns:
        A ReplayResult with the verification outcome.
    """
    failures: list[str] = []
    steps = chain.steps

    if not steps:
        return ReplayResult(
            operator_id=chain.operator_id,
            ok=False,
            steps_checked=0,
            total_steps=0,
            failures=["empty replay chain"],
            truth="FAIL",
        )

    if len(steps) > MAX_REPLAY_DEPTH:
        return ReplayResult(
            operator_id=chain.operator_id,
            ok=False,
            steps_checked=0,
            total_steps=len(steps),
            failures=[
                f"chain length {len(steps)} exceeds MAX_REPLAY_DEPTH "
                f"({MAX_REPLAY_DEPTH})"
            ],
            truth="FAIL",
        )

    checked = 0
    for i in range(len(steps) - 1):
        current = steps[i]
        nxt = steps[i + 1]
        if current.output_hash != nxt.input_hash:
            failures.append(
                f"step {i} output_hash ({current.output_hash[:12]}...) "
                f"!= step {i + 1} input_hash ({nxt.input_hash[:12]}...)"
            )
        else:
            checked += 1

    # Check final hash.
    last = steps[-1]
    if last.output_hash == chain.final_hash:
        checked += 1
    else:
        failures.append(
            f"final step output_hash ({last.output_hash[:12]}...) "
            f"!= chain final_hash ({chain.final_hash[:12]}...)"
        )

    ok = len(failures) == 0

    if ok:
        truth: Truth = "OK"
    elif checked > 0:
        truth = "NEAR"
    else:
        truth = "FAIL"

    return ReplayResult(
        operator_id=chain.operator_id,
        ok=ok,
        steps_checked=checked,
        total_steps=len(steps),
        failures=failures,
        truth=truth,
    )


def build_chain(
    operator_id: str,
    snapshots: list[Any],
    transform_names: list[str],
) -> ReplayChain:
    """Build a ReplayChain from a sequence of state snapshots.

    Given N snapshots and N-1 transform names, constructs the replay
    chain by hashing each snapshot to form the input/output pairs.

    Args:
        operator_id:     OperatorIR.token_id.
        snapshots:       List of JSON-serialisable state objects.
        transform_names: List of transform names (len = len(snapshots) - 1).

    Returns:
        A ReplayChain ready for storage or verification.

    Raises:
        ValueError: If the snapshot/transform counts are inconsistent.
    """
    if len(snapshots) < 2:
        raise ValueError("need at least 2 snapshots to form a chain")
    if len(transform_names) != len(snapshots) - 1:
        raise ValueError(
            f"expected {len(snapshots) - 1} transform names, "
            f"got {len(transform_names)}"
        )

    hashes = [content_hash(s) for s in snapshots]
    steps: list[ReplayStep] = []
    for i, t_name in enumerate(transform_names):
        steps.append(
            ReplayStep(
                step_index=i,
                input_hash=hashes[i],
                transform_name=t_name,
                transform_args={},
                output_hash=hashes[i + 1],
            )
        )

    return ReplayChain(
        operator_id=operator_id,
        steps=steps,
        final_hash=hashes[-1],
    )
