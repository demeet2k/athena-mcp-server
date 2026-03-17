"""
ir.py -- Operator Intermediate Representation for the Athena Process Language Compiler.

An OperatorIR node is the canonical internal form produced by lowering a
ParsedToken through the element/lens/corridor algebra.  Every downstream
backend (LaTeX, symbolic, code-gen, verification) consumes OperatorIR.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any, Literal

Truth = Literal["OK", "NEAR", "AMBIG", "FAIL"]


@dataclass
class OperatorIR:
    """Intermediate representation of a single compiled operator.

    Attributes:
        token_id:        Back-reference to the originating ParsedToken / RawToken.
        operator_family: High-level operator category (e.g. "transform",
                         "bind", "emit", "seal").
        carrier:         The morpheme or glyph that carries the operator.
        inflection:      Optional inflection applied to the carrier.
        closure:         Optional closure annotation (e.g. "self", "field").
        element:         Elemental assignment (fire, water, air, earth, void).
        lens:            Active interpretive lens (e.g. "botanical", "astro",
                         "alchemical", "linguistic").
        level:           Depth / abstraction level in the crystal hierarchy.
        address:         Crystal address string (e.g. "0010.0011.02").
        corridor_tags:   List of truth-corridor tags this operator participates in.
        burden:          Truth burden -- aggregate verification status.
        replay_mode:     Replay directive ("live", "cached", "frozen").
        context:         Arbitrary additional metadata.
    """

    token_id: str
    operator_family: str
    carrier: str
    inflection: str | None
    closure: str | None
    element: str
    lens: str
    level: str
    address: str
    corridor_tags: list[str]
    burden: Truth
    replay_mode: str
    context: dict[str, Any] = field(default_factory=dict)

    # -- serialisation helpers ------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Return a plain-dict representation suitable for JSON encoding."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> OperatorIR:
        """Construct an OperatorIR from a plain dict (e.g. decoded JSON)."""
        return cls(
            token_id=data["token_id"],
            operator_family=data["operator_family"],
            carrier=data["carrier"],
            inflection=data.get("inflection"),
            closure=data.get("closure"),
            element=data["element"],
            lens=data["lens"],
            level=data["level"],
            address=data["address"],
            corridor_tags=data.get("corridor_tags", []),
            burden=data["burden"],
            replay_mode=data.get("replay_mode", "live"),
            context=data.get("context", {}),
        )

    def to_json(self, **kwargs: Any) -> str:
        """Serialise to a JSON string."""
        return json.dumps(self.to_dict(), **kwargs)

    @classmethod
    def from_json(cls, raw: str) -> OperatorIR:
        """Deserialise from a JSON string."""
        return cls.from_dict(json.loads(raw))

    # -- convenience predicates -----------------------------------------------

    @property
    def is_verified(self) -> bool:
        """True when the burden is fully satisfied."""
        return self.burden == "OK"

    @property
    def needs_review(self) -> bool:
        """True when the burden signals ambiguity or near-miss."""
        return self.burden in ("NEAR", "AMBIG")
