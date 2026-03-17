"""
ir_builder.py -- Convert ParsedTokens into OperatorIR nodes.

The IR builder is the boundary between parsing (syntactic decomposition) and
compilation (semantic assignment).  It:
    1. Maps each ParsedToken's selected candidate to an operator family.
    2. Assigns a crystal address in Book.Folio.Line.Position format.
    3. Computes initial corridor tags from element transitions.
    4. Determines burden level from parse confidence and truth status.

Usage:
    >>> from athena_process_compiler.compilers.ir_builder import build_ir
    >>> ir_nodes = build_ir(parsed_tokens, book="I", lens="botanical")
    >>> ir_nodes[0].address
    'I.f001r.01.0000'
"""

from __future__ import annotations

from typing import Sequence

from athena_process_compiler.schemas.tokens import ParsedToken, Truth
from athena_process_compiler.schemas.ir import OperatorIR
from athena_process_compiler.parsers.vml_slot_parser import (
    OPERATOR_FAMILIES,
    lookup_family,
)

# ---------------------------------------------------------------------------
# Element quadrant constants
# ---------------------------------------------------------------------------

ELEMENT_QUADRANTS: dict[str, list[str]] = {
    "earth": ["L", "D", "X", "S"],
    "water": ["W", "T", "C", "M"],
    "fire":  ["H", "P", "F", "R"],
    "air":   ["V", "B", "G", "Q"],
}

#: Reverse lookup: family code -> element.
_CODE_TO_ELEMENT: dict[str, str] = {}
for _elem, _codes in ELEMENT_QUADRANTS.items():
    for _c in _codes:
        _CODE_TO_ELEMENT[_c] = _elem

# Corridor tag templates for element transitions.
_TRANSITION_TAGS: dict[tuple[str, str], str] = {
    ("earth", "water"): "dissolution",
    ("water", "fire"):  "evaporation",
    ("fire", "air"):    "sublimation",
    ("air", "earth"):   "condensation",
    ("earth", "fire"):  "calcination",
    ("fire", "earth"):  "crystallisation",
    ("water", "air"):   "distillation",
    ("air", "water"):   "precipitation",
    ("earth", "air"):   "levitation",
    ("air", "fire"):    "ignition",
    ("fire", "water"):  "quenching",
    ("water", "earth"): "sedimentation",
}


# ---------------------------------------------------------------------------
# Address generation
# ---------------------------------------------------------------------------

def _make_address(book: str, folio: str, line: str, position: int) -> str:
    """Build a crystal address string.

    Format: ``Book.Folio.Line.Position`` where Position is zero-padded to
    four digits.

    Examples:
        >>> _make_address("I", "f001r", "01", 3)
        'I.f001r.01.0003'
    """
    return f"{book}.{folio}.{line}.{position:04d}"


# ---------------------------------------------------------------------------
# Burden computation
# ---------------------------------------------------------------------------

def _compute_burden(parsed: ParsedToken) -> Truth:
    """Derive the OperatorIR burden level from parse confidence and status.

    The burden reflects how much downstream verification work is needed:
        OK    -- fully confident parse, no review required.
        NEAR  -- high confidence but not exact; light review.
        AMBIG -- multiple viable candidates; needs human or heuristic triage.
        FAIL  -- no viable parse; must be resolved before compilation proceeds.
    """
    selected = parsed.selected
    if selected is None:
        return "FAIL"

    # Use both the candidate's own confidence and the aggregate status.
    conf = selected.confidence
    status = parsed.status

    if status == "OK" and conf >= 0.80:
        return "OK"
    if status in ("OK", "NEAR") and conf >= 0.50:
        return "NEAR"
    if status == "AMBIG" or (conf >= 0.30 and conf < 0.50):
        return "AMBIG"
    return "FAIL"


# ---------------------------------------------------------------------------
# Corridor tag computation
# ---------------------------------------------------------------------------

def _compute_corridor_tags(
    current_element: str,
    prev_element: str | None,
) -> list[str]:
    """Compute corridor tags from the element of this node and the previous one.

    Returns:
        A list of corridor tag strings.  Always includes the self-element tag
        (e.g. ``"earth:self"``).  If there is a preceding element and it
        differs, the transition tag is also included.
    """
    tags = [f"{current_element}:self"]

    if prev_element and prev_element != current_element:
        transition = _TRANSITION_TAGS.get((prev_element, current_element))
        if transition:
            tags.append(f"{prev_element}->{current_element}:{transition}")
        else:
            tags.append(f"{prev_element}->{current_element}:unknown")

    return tags


# ---------------------------------------------------------------------------
# IR Builder
# ---------------------------------------------------------------------------

class IRBuilder:
    """Stateful builder that converts ParsedTokens into OperatorIR nodes.

    Tracks position counters and element context across a token stream.

    Attributes:
        book:         Book identifier for crystal addresses.
        lens:         Default interpretive lens applied to all nodes.
        replay_mode:  Default replay directive (``"live"``, ``"cached"``,
                      ``"frozen"``).
    """

    def __init__(
        self,
        *,
        book: str = "I",
        lens: str = "default",
        replay_mode: str = "live",
    ) -> None:
        self.book = book
        self.lens = lens
        self.replay_mode = replay_mode
        self._position_counters: dict[str, int] = {}
        self._prev_element: str | None = None

    def _next_position(self, folio: str, line: str) -> int:
        """Return and increment the position counter for a folio+line."""
        key = f"{folio}:{line}"
        pos = self._position_counters.get(key, 0)
        self._position_counters[key] = pos + 1
        return pos

    def build_one(self, parsed: ParsedToken) -> OperatorIR:
        """Convert a single ParsedToken into an OperatorIR node.

        Args:
            parsed: A ParsedToken with at least one candidate selected.

        Returns:
            An OperatorIR node with address, element, corridor tags, and
            burden fully populated.
        """
        raw = parsed.raw
        selected = parsed.selected

        # Resolve operator family from the selected candidate's root.
        family_code = "?"
        family_name = "unknown"
        element = "void"

        if selected and selected.root:
            fam = lookup_family(selected.root)
            if fam:
                family_code = fam.code
                family_name = fam.name
                element = fam.element

        # If family lookup failed, try to infer element from family code.
        if element == "void" and family_code in _CODE_TO_ELEMENT:
            element = _CODE_TO_ELEMENT[family_code]

        # Build crystal address.
        position = self._next_position(raw.folio, raw.line)
        address = _make_address(self.book, raw.folio, raw.line, position)

        # Corridor tags from element transition.
        corridor_tags = _compute_corridor_tags(element, self._prev_element)
        self._prev_element = element

        # Extract carrier and inflection from the selected candidate.
        carrier = selected.root if selected else raw.text
        inflection = selected.modifier if selected else None
        closure = selected.suffix if selected else None

        # Determine burden.
        burden = _compute_burden(parsed)

        # Determine abstraction level from the family code.
        level = _level_from_family(family_code)

        return OperatorIR(
            token_id=raw.source_id,
            operator_family=f"{family_code}:{family_name}",
            carrier=carrier,
            inflection=inflection,
            closure=closure,
            element=element,
            lens=self.lens,
            level=level,
            address=address,
            corridor_tags=corridor_tags,
            burden=burden,
            replay_mode=self.replay_mode,
            context={
                "raw_text": raw.text,
                "folio": raw.folio,
                "parse_status": parsed.status,
                "candidate_count": len(parsed.candidates),
                "prefix": selected.prefix if selected else None,
            },
        )

    def build(self, tokens: Sequence[ParsedToken]) -> list[OperatorIR]:
        """Convert an ordered sequence of ParsedTokens into OperatorIR nodes.

        Processes tokens left-to-right, maintaining element context for
        corridor tag computation.

        Args:
            tokens: Ordered ParsedToken sequence (typically one line).

        Returns:
            List of OperatorIR nodes in the same order.
        """
        return [self.build_one(pt) for pt in tokens]

    def reset(self) -> None:
        """Reset internal counters and element context.

        Call between folios or lines when address counters should restart.
        """
        self._position_counters.clear()
        self._prev_element = None


def _level_from_family(code: str) -> str:
    """Map a family code to a crystal hierarchy level.

    The level encodes the operator's position in the process algebra:
        - Primal operators (W, L, H, D)       -> level "0" (ground)
        - Transfer operators (T, C, R, G)      -> level "1" (flow)
        - Compound operators (S, V, B, P, F)   -> level "2" (structure)
        - Meta operators (Q, X, M)             -> level "3" (control)
        - Unknown                              -> level "?"
    """
    _LEVEL_MAP: dict[str, str] = {
        "W": "0", "L": "0", "H": "0", "D": "0",
        "T": "1", "C": "1", "R": "1", "G": "1",
        "S": "2", "V": "2", "B": "2", "P": "2", "F": "2",
        "Q": "3", "X": "3", "M": "3",
    }
    return _LEVEL_MAP.get(code, "?")


def build_ir(
    tokens: Sequence[ParsedToken],
    *,
    book: str = "I",
    lens: str = "default",
    replay_mode: str = "live",
) -> list[OperatorIR]:
    """Module-level convenience: build IR from ParsedTokens with default settings.

    Equivalent to ``IRBuilder(book=book, lens=lens).build(tokens)``.

    Args:
        tokens:      Ordered sequence of ParsedTokens.
        book:        Book identifier for crystal addresses.
        lens:        Interpretive lens label.
        replay_mode: Replay directive.

    Returns:
        List of OperatorIR nodes.
    """
    builder = IRBuilder(book=book, lens=lens, replay_mode=replay_mode)
    return builder.build(tokens)
