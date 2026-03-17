"""
eva_tokenizer.py -- Tokenise raw EVA transcription text into RawToken objects.

The EVA (European Voynich Alphabet) transcription format uses dots and spaces
as word delimiters.  This module splits a line of EVA text, assigns positional
metadata, and emits one RawToken per glyph-word.

Usage:
    >>> from athena_process_compiler.parsers.eva_tokenizer import tokenize
    >>> tokens = tokenize("fshedy.qokeedy.ol.kaiin.shor", folio="f001r", line="01")
    >>> [t.text for t in tokens]
    ['fshedy', 'qokeedy', 'ol', 'kaiin', 'shor']
"""

from __future__ import annotations

import re
import uuid
from typing import Sequence

from athena_process_compiler.schemas.tokens import RawToken

# ---------------------------------------------------------------------------
# Delimiter pattern: dots, whitespace, or combinations thereof.
# ---------------------------------------------------------------------------
_SPLIT_RE = re.compile(r"[.\s]+")


def split_eva_line(line: str) -> list[str]:
    """Split an EVA transcription line into individual glyph-words.

    Handles both dot-delimited (``qokeedy.ol.kaiin``) and space-delimited
    formats, or any mixture of the two.  Empty tokens produced by leading,
    trailing, or consecutive delimiters are silently discarded.

    Args:
        line: A single line of EVA transcription text.

    Returns:
        A list of non-empty glyph-word strings in their original order.
    """
    return [w for w in _SPLIT_RE.split(line.strip()) if w]


def _make_source_id(folio: str, paragraph: str, line: str, position: int) -> str:
    """Generate a deterministic source identifier.

    Format: ``{folio}:{paragraph}:{line}:{position:04d}``
    Falls back to a UUID-4 suffix when any component is missing.
    """
    if folio and line:
        return f"{folio}:{paragraph}:{line}:{position:04d}"
    return f"anon:{uuid.uuid4().hex[:12]}:{position:04d}"


def tokenize(
    text: str,
    *,
    folio: str = "unknown",
    paragraph: str = "P0",
    line: str = "00",
    diagram_context: dict | None = None,
) -> list[RawToken]:
    """Tokenise a raw EVA line into a sequence of RawToken objects.

    Each word extracted from *text* becomes one RawToken with its positional
    metadata populated from the supplied folio/paragraph/line identifiers.

    Args:
        text:            A line of EVA transcription text.
        folio:           Folio identifier (e.g. ``"f001r"``).
        paragraph:       Paragraph label within the folio (default ``"P0"``).
        line:            Line label within the paragraph (default ``"00"``).
        diagram_context: Optional dict of diagram metadata to attach to every
                         token in this line (e.g. ``{"type": "botanical"}``).

    Returns:
        An ordered list of RawToken objects, one per glyph-word.  Returns an
        empty list when *text* contains no parseable words.
    """
    words = split_eva_line(text)
    ctx = diagram_context or {}
    tokens: list[RawToken] = []

    for position, word in enumerate(words):
        source_id = _make_source_id(folio, paragraph, line, position)
        tokens.append(
            RawToken(
                text=word,
                folio=folio,
                paragraph=paragraph,
                line=line,
                source_id=source_id,
                diagram_context=dict(ctx),
            )
        )

    return tokens


def tokenize_block(
    lines: Sequence[str],
    *,
    folio: str = "unknown",
    paragraph: str = "P0",
    diagram_context: dict | None = None,
) -> list[RawToken]:
    """Tokenise multiple EVA lines, auto-incrementing the line label.

    Convenience wrapper around :func:`tokenize` for multi-line blocks.

    Args:
        lines:           An iterable of EVA text lines.
        folio:           Folio identifier.
        paragraph:       Paragraph label.
        diagram_context: Optional diagram metadata.

    Returns:
        A flat list of RawToken objects spanning all supplied lines.
    """
    all_tokens: list[RawToken] = []
    for idx, raw_line in enumerate(lines):
        line_label = f"{idx + 1:02d}"
        all_tokens.extend(
            tokenize(
                raw_line,
                folio=folio,
                paragraph=paragraph,
                line=line_label,
                diagram_context=diagram_context,
            )
        )
    return all_tokens
