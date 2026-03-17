"""
replay.py -- Replay compiled token chains from replay seeds.

Reconstructs a compiled token chain by re-executing the transform sequence
recorded in a replay seed or a full ReplayChain.  Supports runtime
transform registration, hash-verified deterministic replay, and
reconstruction from minimal seed data (operator chain + element chain +
address chain).

Usage:
    >>> from athena_process_compiler.runtime.replay import ReplayEngine
    >>> engine = ReplayEngine()
    >>> engine.register_transform("parse", my_parse_fn)
    >>> result = engine.replay_from_seed(seed_data)
    >>> result.ok
    True
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from athena_process_compiler.schemas.tokens import RawToken, ParseCandidate, ParsedToken, Truth
from athena_process_compiler.schemas.ir import OperatorIR
from athena_process_compiler.schemas.artifacts import NativeRender, VerificationBundle
from athena_process_compiler.config import (
    GAWM_RUNTIME,
    HASH_ALGORITHM,
    MAX_REPLAY_DEPTH,
    JSON_INDENT,
    JSON_ENSURE_ASCII,
)


# ---------------------------------------------------------------------------
# Hashing helper
# ---------------------------------------------------------------------------

def content_hash(state: Any) -> str:
    """Compute a content hash for an arbitrary JSON-serialisable state.

    Args:
        state: Any JSON-serialisable value.

    Returns:
        Hex-encoded digest using the configured hash algorithm.
    """
    canonical = json.dumps(state, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.new(HASH_ALGORITHM, canonical.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Replay step and chain dataclasses
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
    """A complete replay chain for an operator sequence.

    Attributes:
        operator_id:  The root operator / token_id this chain replays.
        steps:        Ordered list of replay steps.
        metadata:     Extra metadata.
    """

    operator_id: str
    steps: list[ReplayStep] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a plain-dict representation."""
        return {
            "operator_id": self.operator_id,
            "steps": [s.to_dict() for s in self.steps],
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ReplayChain:
        """Construct from a plain dict."""
        return cls(
            operator_id=data["operator_id"],
            steps=[ReplayStep.from_dict(s) for s in data.get("steps", [])],
            metadata=data.get("metadata", {}),
        )


# ---------------------------------------------------------------------------
# Replay seed
# ---------------------------------------------------------------------------

@dataclass
class ReplaySeed:
    """Minimal data needed to reconstruct a compiled token chain.

    A replay seed stores the operator chain, element chain, and address
    chain from a packaged artifact bundle, enabling reconstruction
    without the full IR data.

    Attributes:
        operator_chain: Ordered operator family strings.
        element_chain:  Ordered element names.
        address_chain:  Ordered crystal addresses.
        metadata:       Extra metadata (lens, book, etc.).
    """

    operator_chain: list[str]
    element_chain: list[str]
    address_chain: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a plain-dict representation."""
        return {
            "operator_chain": self.operator_chain,
            "element_chain": self.element_chain,
            "address_chain": self.address_chain,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ReplaySeed:
        """Construct from a plain dict."""
        return cls(
            operator_chain=data.get("operator_chain", []),
            element_chain=data.get("element_chain", []),
            address_chain=data.get("address_chain", []),
            metadata=data.get("metadata", {}),
        )

    @classmethod
    def from_ir_chain(cls, ir_nodes: list[OperatorIR]) -> ReplaySeed:
        """Build a ReplaySeed from a list of OperatorIR nodes.

        Args:
            ir_nodes: The compiled IR chain.

        Returns:
            A ReplaySeed capturing the minimal reconstruction data.
        """
        return cls(
            operator_chain=[ir.operator_family for ir in ir_nodes],
            element_chain=[ir.element for ir in ir_nodes],
            address_chain=[ir.address for ir in ir_nodes],
        )

    @property
    def chain_length(self) -> int:
        """Number of operators in the chain."""
        return len(self.operator_chain)


# ---------------------------------------------------------------------------
# Replay execution result
# ---------------------------------------------------------------------------

@dataclass
class ReplayResult:
    """Result of executing a replay chain at runtime.

    Attributes:
        operator_id:    The operator / token_id that was replayed.
        hash_verified:  Whether the hash chain is internally consistent.
        steps_executed: Number of steps that were actually re-executed.
        steps_matched:  Number of re-executed steps whose output hash matched.
        outputs:        List of (step_index, output_state) from execution.
        errors:         Human-readable error descriptions.
        reconstructed:  List of reconstructed OperatorIR dicts (from seed replay).
    """

    operator_id: str
    hash_verified: bool = True
    steps_executed: int = 0
    steps_matched: int = 0
    outputs: list[tuple[int, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    reconstructed: list[dict[str, Any]] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        """True if replay completed without errors."""
        return (
            self.hash_verified
            and not self.errors
            and (self.steps_executed == 0 or self.steps_executed == self.steps_matched)
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a summary dict."""
        return {
            "operator_id": self.operator_id,
            "hash_verified": self.hash_verified,
            "steps_executed": self.steps_executed,
            "steps_matched": self.steps_matched,
            "ok": self.ok,
            "errors": self.errors,
            "reconstructed_count": len(self.reconstructed),
        }


# ---------------------------------------------------------------------------
# Replay Engine
# ---------------------------------------------------------------------------

#: Module-level transform registry
_TRANSFORMS: dict[str, Callable[[Any, dict[str, Any]], Any]] = {}


class ReplayEngine:
    """Runtime engine for replaying compiled token chains.

    Supports two replay modes:
        1. **Full chain replay**: Re-execute a ReplayChain with hash
           verification at each step.
        2. **Seed replay**: Reconstruct OperatorIR nodes from a minimal
           ReplaySeed (operator + element + address chains).

    Transforms are registered per-engine or globally, and are looked up
    by name during chain replay.
    """

    def __init__(self, *, max_depth: int = MAX_REPLAY_DEPTH) -> None:
        """Initialise the replay engine.

        Args:
            max_depth: Maximum number of replay steps before forced termination.
        """
        self.max_depth = max_depth
        self._local_transforms: dict[str, Callable[[Any, dict[str, Any]], Any]] = {}

    # -- transform registration ---------------------------------------------

    def register_transform(
        self, name: str, fn: Callable[[Any, dict[str, Any]], Any]
    ) -> None:
        """Register a transform function for replay.

        Args:
            name: The transform name (must match ReplayStep.transform_name).
            fn:   A callable ``(input_state, args) -> output_state``.
        """
        self._local_transforms[name] = fn

    def get_transform(self, name: str) -> Callable[[Any, dict[str, Any]], Any] | None:
        """Look up a transform by name.  Checks local registry first, then global."""
        return self._local_transforms.get(name) or _TRANSFORMS.get(name)

    def list_transforms(self) -> list[str]:
        """Return sorted names of all available transforms."""
        names = set(self._local_transforms.keys()) | set(_TRANSFORMS.keys())
        return sorted(names)

    # -- full chain replay --------------------------------------------------

    def replay_chain(
        self,
        chain: ReplayChain,
        initial_state: Any,
        *,
        strict: bool = True,
    ) -> ReplayResult:
        """Re-execute a replay chain from an initial state.

        For each step, looks up the transform and re-runs it.  The output
        is hashed and compared to the recorded output_hash.

        Args:
            chain:         The ReplayChain to execute.
            initial_state: The starting state.
            strict:        If True, stop on the first hash mismatch.

        Returns:
            A ReplayResult summarising the execution.
        """
        errors: list[str] = []
        outputs: list[tuple[int, Any]] = []
        executed = 0
        matched = 0

        # Verify hash chain consistency
        hash_verified = self._verify_chain_hashes(chain)
        if not hash_verified:
            errors.append("hash chain internal consistency check failed")

        # Verify initial state
        if chain.steps:
            init_hash = content_hash(initial_state)
            if init_hash != chain.steps[0].input_hash:
                errors.append(
                    f"initial state hash mismatch: "
                    f"got {init_hash[:12]}..., "
                    f"expected {chain.steps[0].input_hash[:12]}..."
                )
                if strict:
                    return ReplayResult(
                        operator_id=chain.operator_id,
                        hash_verified=hash_verified,
                        errors=errors,
                    )

        current_state = initial_state

        for i, step in enumerate(chain.steps):
            if i >= self.max_depth:
                errors.append(f"max replay depth ({self.max_depth}) reached at step {i}")
                break

            transform_fn = self.get_transform(step.transform_name)
            if transform_fn is None:
                errors.append(
                    f"step {step.step_index}: transform "
                    f"{step.transform_name!r} not registered"
                )
                if strict:
                    break
                continue

            try:
                output_state = transform_fn(current_state, step.transform_args)
            except Exception as exc:
                errors.append(
                    f"step {step.step_index}: transform raised "
                    f"{type(exc).__name__}: {exc}"
                )
                if strict:
                    break
                continue

            executed += 1
            outputs.append((step.step_index, output_state))

            output_h = content_hash(output_state)
            if output_h == step.output_hash:
                matched += 1
            else:
                errors.append(
                    f"step {step.step_index}: output hash mismatch: "
                    f"got {output_h[:12]}..., expected {step.output_hash[:12]}..."
                )
                if strict:
                    break

            current_state = output_state

        return ReplayResult(
            operator_id=chain.operator_id,
            hash_verified=hash_verified,
            steps_executed=executed,
            steps_matched=matched,
            outputs=outputs,
            errors=errors,
        )

    def _verify_chain_hashes(self, chain: ReplayChain) -> bool:
        """Check that each step's output_hash matches the next step's input_hash."""
        for i in range(len(chain.steps) - 1):
            if chain.steps[i].output_hash != chain.steps[i + 1].input_hash:
                return False
        return True

    # -- seed replay --------------------------------------------------------

    def replay_from_seed(
        self,
        seed: ReplaySeed | dict[str, Any],
        *,
        book: str = "I",
        lens: str = "default",
        replay_mode: str = "cached",
    ) -> ReplayResult:
        """Reconstruct OperatorIR nodes from a minimal replay seed.

        This does not re-execute transforms; instead it rebuilds
        lightweight IR stubs from the operator/element/address chains
        recorded in the seed.

        Args:
            seed:        A ReplaySeed or a dict with the seed fields.
            book:        Book identifier for reconstruction.
            lens:        Interpretive lens label.
            replay_mode: Replay mode tag for reconstructed nodes.

        Returns:
            A ReplayResult with the reconstructed IR dicts.
        """
        if isinstance(seed, dict):
            seed = ReplaySeed.from_dict(seed)

        errors: list[str] = []
        reconstructed: list[dict[str, Any]] = []

        n = seed.chain_length
        if n == 0:
            errors.append("empty replay seed")
            return ReplayResult(
                operator_id="unknown",
                errors=errors,
            )

        # Validate chain lengths match
        if len(seed.element_chain) != n or len(seed.address_chain) != n:
            errors.append(
                f"chain length mismatch: operators={n}, "
                f"elements={len(seed.element_chain)}, "
                f"addresses={len(seed.address_chain)}"
            )

        effective_length = min(n, len(seed.element_chain), len(seed.address_chain))

        for i in range(effective_length):
            operator_family = seed.operator_chain[i]
            element = seed.element_chain[i]
            address = seed.address_chain[i]

            # Extract carrier from operator family (part after colon)
            parts = operator_family.split(":", 1)
            carrier = parts[1] if len(parts) > 1 else parts[0]

            ir_dict = {
                "token_id": f"replay_{i:04d}",
                "operator_family": operator_family,
                "carrier": carrier,
                "inflection": None,
                "closure": None,
                "element": element,
                "lens": lens,
                "level": "?",
                "address": address,
                "corridor_tags": [f"{element}:self", f"replay:seed:{i}"],
                "burden": "NEAR",
                "replay_mode": replay_mode,
                "context": {
                    "reconstructed": True,
                    "seed_index": i,
                },
            }
            reconstructed.append(ir_dict)

        operator_id = seed.address_chain[0] if seed.address_chain else "unknown"

        return ReplayResult(
            operator_id=operator_id,
            hash_verified=True,
            steps_executed=effective_length,
            steps_matched=effective_length,
            errors=errors,
            reconstructed=reconstructed,
        )

    # -- chain persistence --------------------------------------------------

    def save_chain(self, chain: ReplayChain, directory: Path | None = None) -> Path:
        """Persist a ReplayChain to GAWM_RUNTIME.

        Args:
            chain:     The chain to save.
            directory: Override output directory (default: GAWM_RUNTIME).

        Returns:
            Path to the written JSON file.
        """
        directory = directory or GAWM_RUNTIME
        directory.mkdir(parents=True, exist_ok=True)

        fp = content_hash(chain.to_dict())
        out_path = directory / f"replay_{chain.operator_id}_{fp[:16]}.json"
        out_path.write_text(
            json.dumps(chain.to_dict(), indent=JSON_INDENT, ensure_ascii=JSON_ENSURE_ASCII),
            encoding="utf-8",
        )
        return out_path

    def load_chain(self, path: Path) -> ReplayChain:
        """Load a ReplayChain from a JSON file.

        Args:
            path: Path to the chain JSON file.

        Returns:
            The deserialised ReplayChain.
        """
        data = json.loads(path.read_text(encoding="utf-8"))
        return ReplayChain.from_dict(data)

    def find_chains(self, operator_id: str, directory: Path | None = None) -> list[Path]:
        """Find all saved replay chains for a given operator_id.

        Args:
            operator_id: The OperatorIR.token_id to search for.
            directory:   Directory to scan (default: GAWM_RUNTIME).

        Returns:
            List of paths to matching chain files.
        """
        directory = directory or GAWM_RUNTIME
        if not directory.is_dir():
            return []
        pattern = f"replay_{operator_id}_*.json"
        return sorted(directory.glob(pattern))


# ---------------------------------------------------------------------------
# Module-level convenience functions
# ---------------------------------------------------------------------------

def register_transform(name: str, fn: Callable[[Any, dict[str, Any]], Any]) -> None:
    """Register a transform function in the global registry."""
    _TRANSFORMS[name] = fn


def get_transform(name: str) -> Callable[[Any, dict[str, Any]], Any] | None:
    """Look up a registered transform by name from the global registry."""
    return _TRANSFORMS.get(name)


def list_transforms() -> list[str]:
    """Return sorted names of all globally registered transforms."""
    return sorted(_TRANSFORMS.keys())


def save_chain(chain: ReplayChain, directory: Path | None = None) -> Path:
    """Persist a ReplayChain using the default engine."""
    return ReplayEngine().save_chain(chain, directory)


def load_chain(path: Path) -> ReplayChain:
    """Load a ReplayChain from a JSON file."""
    return ReplayEngine().load_chain(path)


def find_chains(operator_id: str, directory: Path | None = None) -> list[Path]:
    """Find all saved replay chains for a given operator_id."""
    return ReplayEngine().find_chains(operator_id, directory)
