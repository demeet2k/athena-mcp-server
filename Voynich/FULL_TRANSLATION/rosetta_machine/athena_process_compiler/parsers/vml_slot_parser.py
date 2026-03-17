"""
vml_slot_parser.py -- Morphological slot parser for EVA tokens.

Decomposes each EVA glyph-word into the four VML slots:

    [prefix] - root - [modifier] - [suffix]

The decomposition is driven by a registry of 16 operator families, each
defined by a set of known EVA token patterns.  The parser tries every
plausible segmentation and emits ranked ParseCandidate objects.

Usage:
    >>> from athena_process_compiler.parsers.vml_slot_parser import SlotParser
    >>> parser = SlotParser()
    >>> parsed = parser.parse(raw_token)
    >>> parsed.candidates[0].root
    'kaiin'
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from athena_process_compiler.schemas.tokens import (
    ParseCandidate,
    ParsedToken,
    RawToken,
    Truth,
)

# ---------------------------------------------------------------------------
# Operator family registry
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class OperatorFamily:
    """Definition of one of the 16 operator families.

    Attributes:
        code:     Single-letter family code (W, L, H, ...).
        name:     Human-readable name.
        element:  Elemental quadrant (earth, water, fire, air).
        patterns: Known EVA token patterns belonging to this family,
                  ordered from longest to shortest for greedy matching.
    """
    code: str
    name: str
    element: str
    patterns: tuple[str, ...]


# Families ordered by code letter.  Patterns within each family are listed
# longest-first so the greedy matcher prefers specific over general.
OPERATOR_FAMILIES: tuple[OperatorFamily, ...] = (
    OperatorFamily("W", "wet/prime",       "water", ("yshey", "sair", "sy", "y")),
    OperatorFamily("L", "load",            "earth", ("chear", "dar", "ar")),
    OperatorFamily("H", "heat/drive",      "fire",  ("sho", "ot", "o")),
    OperatorFamily("T", "throat transfer", "water", ("cthol", "cth", "cht")),
    OperatorFamily("C", "capture",         "water", ("keey", "chor", "kor")),
    OperatorFamily("S", "seal",            "earth", ("kaiin", "ckh", "kos", "k")),
    OperatorFamily("V", "verify",          "air",   ("sckhey", "ckhey", "cthar")),
    OperatorFamily("B", "bind",            "air",   ("daicthy", "cthy", "chod")),
    OperatorFamily("P", "pressure",        "fire",  ("cpho", "psh", "cph")),
    OperatorFamily("F", "fire-seal",       "fire",  ("cfhoaiin", "cfh", "far")),
    OperatorFamily("R", "recirculate",     "fire",  ("okchoy", "okol", "ok")),
    OperatorFamily("D", "fix",             "earth", ("shody", "dal", "dan", "d")),
    OperatorFamily("Q", "checkpoint",      "air",   ("daiiin", "daiin")),
    OperatorFamily("X", "triple-fix",      "earth", ("dydyd",)),
    OperatorFamily("G", "gate",            "air",   ("chtor", "chor", "ro")),
    OperatorFamily("M", "conjunction",     "water", ("am",)),
)

# Lookup: pattern string -> OperatorFamily
_PATTERN_INDEX: dict[str, OperatorFamily] = {}
for _fam in OPERATOR_FAMILIES:
    for _pat in _fam.patterns:
        # First registration wins; earlier families have priority.
        _PATTERN_INDEX.setdefault(_pat, _fam)

# All patterns sorted longest-first for greedy scanning.
_ALL_PATTERNS: list[str] = sorted(_PATTERN_INDEX.keys(), key=len, reverse=True)

# Common EVA prefixes and suffixes that may wrap a root pattern.
_KNOWN_PREFIXES: tuple[str, ...] = (
    "qo", "sh", "ch", "s", "q", "f", "p", "t", "c",
)
_KNOWN_SUFFIXES: tuple[str, ...] = (
    "aiin", "eedy", "edy", "dy", "ol", "ey", "iin", "in", "y",
)
_KNOWN_MODIFIERS: tuple[str, ...] = (
    "ok", "ee", "ai", "ol", "or", "e",
)


# ---------------------------------------------------------------------------
# Candidate generation
# ---------------------------------------------------------------------------

def _try_slot_decomposition(word: str) -> list[ParseCandidate]:
    """Attempt all plausible prefix/root/modifier/suffix decompositions.

    Strategy:
        1. Try to match the entire word as a known root pattern (highest conf).
        2. Try stripping known prefixes, then matching the remainder.
        3. Try stripping known suffixes from the (prefix-stripped) remainder.
        4. Try inserting a modifier split between root and suffix.
        5. Fall back to treating the whole word as an unknown root.

    Returns:
        A list of ParseCandidate objects sorted by descending confidence.
    """
    candidates: list[ParseCandidate] = []
    word_lower = word.lower()

    # --- Strategy 1: exact full-word match -----------------------------------
    if word_lower in _PATTERN_INDEX:
        fam = _PATTERN_INDEX[word_lower]
        candidates.append(ParseCandidate(
            prefix=None,
            root=word_lower,
            modifier=None,
            suffix=None,
            confidence=1.0,
            notes=[f"exact:{fam.code}({fam.name})"],
        ))

    # --- Strategy 2 & 3: prefix/suffix stripping -----------------------------
    prefix_options: list[tuple[str | None, str]] = [(None, word_lower)]
    for pfx in _KNOWN_PREFIXES:
        if word_lower.startswith(pfx) and len(word_lower) > len(pfx):
            prefix_options.append((pfx, word_lower[len(pfx):]))

    for prefix, remainder in prefix_options:
        # Try matching remainder directly as a root.
        if remainder in _PATTERN_INDEX and prefix is not None:
            fam = _PATTERN_INDEX[remainder]
            candidates.append(ParseCandidate(
                prefix=prefix,
                root=remainder,
                modifier=None,
                suffix=None,
                confidence=0.85,
                notes=[f"prefix_strip:{fam.code}({fam.name})"],
            ))

        # Try stripping suffixes from remainder.
        for sfx in _KNOWN_SUFFIXES:
            if remainder.endswith(sfx) and len(remainder) > len(sfx):
                core = remainder[: -len(sfx)]
                if core in _PATTERN_INDEX:
                    fam = _PATTERN_INDEX[core]
                    candidates.append(ParseCandidate(
                        prefix=prefix,
                        root=core,
                        modifier=None,
                        suffix=sfx,
                        confidence=0.75 if prefix is None else 0.70,
                        notes=[f"suffix_strip:{fam.code}({fam.name})"],
                    ))

                # Try splitting core further with a modifier.
                for mod in _KNOWN_MODIFIERS:
                    if core.endswith(mod) and len(core) > len(mod):
                        inner = core[: -len(mod)]
                        if inner in _PATTERN_INDEX:
                            fam = _PATTERN_INDEX[inner]
                            candidates.append(ParseCandidate(
                                prefix=prefix,
                                root=inner,
                                modifier=mod,
                                suffix=sfx,
                                confidence=0.60,
                                notes=[f"full_decomp:{fam.code}({fam.name})"],
                            ))

    # --- Strategy 4: substring scanning (greedy, longest match) --------------
    if not candidates:
        for pat in _ALL_PATTERNS:
            idx = word_lower.find(pat)
            if idx == -1:
                continue
            fam = _PATTERN_INDEX[pat]
            before = word_lower[:idx] if idx > 0 else None
            after = word_lower[idx + len(pat):] or None
            candidates.append(ParseCandidate(
                prefix=before,
                root=pat,
                modifier=None,
                suffix=after,
                confidence=0.45,
                notes=[f"substring:{fam.code}({fam.name})"],
            ))
            # Keep only the top few substring matches.
            if len(candidates) >= 4:
                break

    # --- Strategy 5: fallback unknown root -----------------------------------
    if not candidates:
        candidates.append(ParseCandidate(
            prefix=None,
            root=word_lower,
            modifier=None,
            suffix=None,
            confidence=0.10,
            notes=["unknown_root"],
        ))

    # Sort by descending confidence, stable.
    candidates.sort(key=lambda c: -c.confidence)
    return candidates


def _determine_truth(candidates: list[ParseCandidate]) -> Truth:
    """Derive an aggregate truth status from a candidate list.

    Rules:
        - Top candidate confidence >= 0.80        -> OK
        - Top candidate confidence >= 0.50        -> NEAR
        - Multiple candidates with conf >= 0.40   -> AMBIG
        - Otherwise                                -> FAIL
    """
    if not candidates:
        return "FAIL"
    top = candidates[0].confidence
    if top >= 0.80:
        return "OK"
    if top >= 0.50:
        return "NEAR"
    above_threshold = sum(1 for c in candidates if c.confidence >= 0.40)
    if above_threshold >= 2:
        return "AMBIG"
    if top >= 0.30:
        return "AMBIG"
    return "FAIL"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class SlotParser:
    """Stateful parser that decomposes RawTokens into slot-structured candidates.

    The parser holds a reference to the operator-family registry and can be
    extended at runtime with additional pattern entries.
    """

    def __init__(self) -> None:
        self._extra_patterns: dict[str, OperatorFamily] = {}

    def register_pattern(self, pattern: str, family: OperatorFamily) -> None:
        """Add a custom pattern -> family mapping visible to this parser."""
        self._extra_patterns[pattern] = family

    def parse(self, raw: RawToken) -> ParsedToken:
        """Parse a single RawToken into a ParsedToken with ranked candidates.

        Args:
            raw: The raw token to decompose.

        Returns:
            A ParsedToken containing all plausible decompositions, sorted
            by descending confidence, with the top candidate auto-selected.
        """
        candidates = _try_slot_decomposition(raw.text)

        # Check extra patterns registered on this instance.
        word_lower = raw.text.lower()
        if word_lower in self._extra_patterns:
            fam = self._extra_patterns[word_lower]
            candidates.insert(0, ParseCandidate(
                prefix=None,
                root=word_lower,
                modifier=None,
                suffix=None,
                confidence=0.95,
                notes=[f"custom:{fam.code}({fam.name})"],
            ))
            candidates.sort(key=lambda c: -c.confidence)

        status = _determine_truth(candidates)
        selected = 0 if candidates else None

        return ParsedToken(
            raw=raw,
            candidates=candidates,
            selected_index=selected,
            status=status,
        )

    def parse_many(self, tokens: list[RawToken]) -> list[ParsedToken]:
        """Parse a batch of RawTokens.

        Args:
            tokens: Ordered list of raw tokens (typically one line).

        Returns:
            List of ParsedToken objects in the same order.
        """
        return [self.parse(t) for t in tokens]


def parse_token(raw: RawToken) -> ParsedToken:
    """Module-level convenience: parse a single RawToken with default settings.

    Equivalent to ``SlotParser().parse(raw)``.
    """
    return SlotParser().parse(raw)


def lookup_family(pattern: str) -> OperatorFamily | None:
    """Look up the operator family for a known EVA pattern string.

    Returns None if the pattern is not in the registry.
    """
    return _PATTERN_INDEX.get(pattern.lower())
