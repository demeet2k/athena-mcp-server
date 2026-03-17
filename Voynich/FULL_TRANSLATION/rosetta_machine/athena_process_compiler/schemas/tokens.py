"""
tokens.py -- Core token dataclasses for the Athena Process Language Compiler.

Defines the three-stage token lifecycle:
  RawToken       -> extracted glyph sequence with folio coordinates
  ParseCandidate -> one possible morphological decomposition
  ParsedToken    -> raw token + ranked candidate list + selection + truth status
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any, Literal

Truth = Literal["OK", "NEAR", "AMBIG", "FAIL"]


@dataclass
class RawToken:
    """A single glyph sequence extracted from a manuscript folio.

    Attributes:
        text:            The EVA or VML glyph string.
        folio:           Folio identifier (e.g. "f001r").
        paragraph:       Paragraph label within the folio.
        line:            Line label within the paragraph.
        source_id:       Unique identifier linking back to the transcription source.
        diagram_context: Optional metadata when the token sits inside or near
                         a diagram (plant, astro-ring, etc.).
    """

    text: str
    folio: str
    paragraph: str
    line: str
    source_id: str
    diagram_context: dict[str, Any] = field(default_factory=dict)

    # -- serialisation helpers ------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Return a plain-dict representation suitable for JSON encoding."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RawToken:
        """Construct a RawToken from a plain dict (e.g. decoded JSON)."""
        return cls(
            text=data["text"],
            folio=data["folio"],
            paragraph=data["paragraph"],
            line=data["line"],
            source_id=data["source_id"],
            diagram_context=data.get("diagram_context", {}),
        )

    def to_json(self, **kwargs: Any) -> str:
        """Serialise to a JSON string."""
        return json.dumps(self.to_dict(), **kwargs)

    @classmethod
    def from_json(cls, raw: str) -> RawToken:
        """Deserialise from a JSON string."""
        return cls.from_dict(json.loads(raw))


@dataclass
class ParseCandidate:
    """One possible morphological parse of a glyph sequence.

    A token may decompose as:  [prefix]-root-[modifier]-[suffix]
    where bracketed parts are optional.

    Attributes:
        prefix:     Optional leading morpheme.
        root:       Mandatory root morpheme.
        modifier:   Optional internal modifier morpheme.
        suffix:     Optional trailing morpheme.
        confidence: Parser confidence in [0.0, 1.0].
        notes:      Free-form annotations from the parser.
    """

    prefix: str | None
    root: str
    modifier: str | None
    suffix: str | None
    confidence: float
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a plain-dict representation."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ParseCandidate:
        """Construct from a plain dict."""
        return cls(
            prefix=data.get("prefix"),
            root=data["root"],
            modifier=data.get("modifier"),
            suffix=data.get("suffix"),
            confidence=data["confidence"],
            notes=data.get("notes", []),
        )


@dataclass
class ParsedToken:
    """A raw token together with its ranked parse candidates.

    Attributes:
        raw:            The original RawToken.
        candidates:     Ranked list of morphological decompositions.
        selected_index: Index into *candidates* chosen by the selector pass,
                        or None if no selection has been made yet.
        status:         Aggregate truth verdict across candidates.
    """

    raw: RawToken
    candidates: list[ParseCandidate]
    selected_index: int | None
    status: Truth

    # -- convenience ----------------------------------------------------------

    @property
    def selected(self) -> ParseCandidate | None:
        """Return the currently selected candidate, if any."""
        if self.selected_index is not None and 0 <= self.selected_index < len(self.candidates):
            return self.candidates[self.selected_index]
        return None

    # -- serialisation --------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Return a plain-dict representation."""
        return {
            "raw": self.raw.to_dict(),
            "candidates": [c.to_dict() for c in self.candidates],
            "selected_index": self.selected_index,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ParsedToken:
        """Construct from a plain dict."""
        return cls(
            raw=RawToken.from_dict(data["raw"]),
            candidates=[ParseCandidate.from_dict(c) for c in data["candidates"]],
            selected_index=data.get("selected_index"),
            status=data["status"],
        )

    def to_json(self, **kwargs: Any) -> str:
        """Serialise to a JSON string."""
        return json.dumps(self.to_dict(), **kwargs)

    @classmethod
    def from_json(cls, raw: str) -> ParsedToken:
        """Deserialise from a JSON string."""
        return cls.from_dict(json.loads(raw))
