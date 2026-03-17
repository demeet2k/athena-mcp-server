"""
artifacts.py -- Artifact and verification dataclasses for the Athena Process
Language Compiler.

Two structures live here:

  NativeRender       -- the output of a single rendering backend (LaTeX,
                        symbolic CAS, code-gen, etc.) applied to an OperatorIR.
  VerificationBundle -- the cross-backend consistency check that compares
                        multiple NativeRenders and witnesses.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any, Literal

Truth = Literal["OK", "NEAR", "AMBIG", "FAIL"]


@dataclass
class NativeRender:
    """Output produced by a single rendering backend.

    Attributes:
        backend:    Name of the rendering backend (e.g. "latex", "sympy",
                    "python", "mermaid").
        content:    The rendered artefact.  Type varies by backend -- may be a
                    string (LaTeX source), a dict (symbolic expression tree),
                    or any JSON-serialisable value.
        invariants: Mathematical or structural invariants the backend asserts
                    about its output (e.g. {"commutative": True}).
        status:     Truth verdict for this individual render.
        notes:      Free-form annotations from the backend.
    """

    backend: str
    content: Any
    invariants: dict[str, Any]
    status: Truth
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a plain-dict representation."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> NativeRender:
        """Construct from a plain dict."""
        return cls(
            backend=data["backend"],
            content=data["content"],
            invariants=data.get("invariants", {}),
            status=data["status"],
            notes=data.get("notes", []),
        )

    def to_json(self, **kwargs: Any) -> str:
        """Serialise to a JSON string."""
        return json.dumps(self.to_dict(), **kwargs)

    @classmethod
    def from_json(cls, raw: str) -> NativeRender:
        """Deserialise from a JSON string."""
        return cls.from_dict(json.loads(raw))


@dataclass
class VerificationBundle:
    """Cross-backend verification result for a single OperatorIR node.

    After multiple backends render the same OperatorIR, the verifier compares
    their outputs and witnesses to produce this bundle.

    Attributes:
        ir_id:                     Back-reference to the OperatorIR.token_id.
        cross_backend_consistency: Agreement score in [0.0, 1.0] across all
                                   backends that rendered this operator.
        witness_refs:              List of witness identifiers (corridor refs,
                                   capsule hashes, etc.) that corroborate the
                                   render.
        replay_refs:               List of replay-log references that can
                                   reproduce the render deterministically.
        status:                    Aggregate truth verdict.
        residuals:                 Descriptions of any unresolved discrepancies
                                   between backends.
    """

    ir_id: str
    cross_backend_consistency: float
    witness_refs: list[str]
    replay_refs: list[str]
    status: Truth
    residuals: list[str] = field(default_factory=list)

    # -- serialisation helpers ------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Return a plain-dict representation suitable for JSON encoding."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VerificationBundle:
        """Construct a VerificationBundle from a plain dict."""
        return cls(
            ir_id=data["ir_id"],
            cross_backend_consistency=data["cross_backend_consistency"],
            witness_refs=data.get("witness_refs", []),
            replay_refs=data.get("replay_refs", []),
            status=data["status"],
            residuals=data.get("residuals", []),
        )

    def to_json(self, **kwargs: Any) -> str:
        """Serialise to a JSON string."""
        return json.dumps(self.to_dict(), **kwargs)

    @classmethod
    def from_json(cls, raw: str) -> VerificationBundle:
        """Deserialise from a JSON string."""
        return cls.from_dict(json.loads(raw))

    # -- convenience predicates -----------------------------------------------

    @property
    def is_consistent(self) -> bool:
        """True when cross-backend consistency is perfect (1.0)."""
        return self.cross_backend_consistency == 1.0

    @property
    def is_verified(self) -> bool:
        """True when status is OK and consistency is perfect."""
        return self.status == "OK" and self.is_consistent

    @property
    def has_residuals(self) -> bool:
        """True when there are unresolved discrepancies."""
        return len(self.residuals) > 0
