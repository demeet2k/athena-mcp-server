"""
ambiguity.py -- Ambiguity envelope construction and candidate resolution.

When the slot parser produces multiple plausible decompositions for a token,
this module wraps them in an AmbiguityEnvelope that tracks context-sensitive
scoring signals and performs final candidate selection.

Resolution strategies:
    1. Elemental continuity   -- prefer candidates whose element matches the
                                 local corridor flow.
    2. Morphological economy  -- prefer candidates with fewer non-null slots
                                 (Occam's razor for decomposition).
    3. Bigram affinity        -- boost candidates whose operator family is
                                 frequently adjacent to the preceding token's
                                 family in the training corpus.
    4. Confidence floor       -- discard candidates below a minimum threshold.

Usage:
    >>> from athena_process_compiler.parsers.ambiguity import resolve_candidates
    >>> resolved = resolve_candidates(parsed_tokens, corridor_hint="water")
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from athena_process_compiler.schemas.tokens import ParseCandidate, ParsedToken, Truth
from athena_process_compiler.parsers.vml_slot_parser import (
    OPERATOR_FAMILIES,
    _PATTERN_INDEX,
    lookup_family,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: Minimum confidence to keep a candidate during pruning.
CONFIDENCE_FLOOR: float = 0.15

#: Bonus added when a candidate's element matches the corridor hint.
ELEMENT_CONTINUITY_BONUS: float = 0.12

#: Penalty per non-null optional slot (prefix, modifier, suffix).
SLOT_PENALTY: float = 0.03

# Bigram affinity pairs: (preceding_family_code, following_family_code) -> bonus.
# Derived from corpus frequency analysis of operator transitions.
_BIGRAM_AFFINITIES: dict[tuple[str, str], float] = {
    ("W", "L"): 0.08,   # wet -> load  (prime then absorb)
    ("L", "H"): 0.08,   # load -> heat  (absorb then drive)
    ("H", "S"): 0.07,   # heat -> seal  (drive then lock)
    ("S", "V"): 0.06,   # seal -> verify
    ("V", "B"): 0.06,   # verify -> bind
    ("T", "C"): 0.07,   # throat -> capture
    ("C", "S"): 0.06,   # capture -> seal
    ("P", "F"): 0.08,   # pressure -> fire-seal
    ("F", "R"): 0.07,   # fire-seal -> recirculate
    ("R", "D"): 0.06,   # recirculate -> fix
    ("D", "Q"): 0.07,   # fix -> checkpoint
    ("Q", "G"): 0.06,   # checkpoint -> gate
    ("G", "W"): 0.05,   # gate -> wet  (cycle restart)
    ("M", "W"): 0.05,   # conjunction -> wet
    ("M", "L"): 0.05,   # conjunction -> load
}


# ---------------------------------------------------------------------------
# AmbiguityEnvelope
# ---------------------------------------------------------------------------

@dataclass
class AmbiguityEnvelope:
    """Container for a ParsedToken's candidates with contextual scoring.

    The envelope records the original candidates, applies context-sensitive
    adjustments, and exposes the resolved selection.

    Attributes:
        token:             The ParsedToken being resolved.
        corridor_hint:     Optional element hint from the surrounding corridor.
        preceding_family:  Operator family code of the preceding token (if any).
        adjusted_scores:   List of (candidate_index, adjusted_confidence) pairs,
                           sorted by descending adjusted confidence.
        resolved_index:    The index into token.candidates chosen after resolution.
    """

    token: ParsedToken
    corridor_hint: str | None = None
    preceding_family: str | None = None
    adjusted_scores: list[tuple[int, float]] = field(default_factory=list)
    resolved_index: int | None = None

    def resolve(self) -> ParsedToken:
        """Score candidates with contextual signals and update the token.

        Mutates ``self.token.selected_index`` and ``self.token.status`` in
        place and returns the token for chaining convenience.
        """
        if not self.token.candidates:
            self.token.status = "FAIL"
            return self.token

        scored: list[tuple[int, float]] = []

        for idx, cand in enumerate(self.token.candidates):
            score = cand.confidence

            # --- Elemental continuity bonus ---
            if self.corridor_hint and cand.root:
                fam = lookup_family(cand.root)
                if fam and fam.element == self.corridor_hint:
                    score += ELEMENT_CONTINUITY_BONUS

            # --- Morphological economy penalty ---
            slot_count = sum(1 for s in (cand.prefix, cand.modifier, cand.suffix) if s)
            score -= slot_count * SLOT_PENALTY

            # --- Bigram affinity bonus ---
            if self.preceding_family and cand.root:
                fam = lookup_family(cand.root)
                if fam:
                    key = (self.preceding_family, fam.code)
                    score += _BIGRAM_AFFINITIES.get(key, 0.0)

            scored.append((idx, round(score, 6)))

        # Sort descending by adjusted score.
        scored.sort(key=lambda pair: -pair[1])
        self.adjusted_scores = scored
        self.resolved_index = scored[0][0]

        # Apply to token.
        self.token.selected_index = self.resolved_index
        self.token.status = _recompute_truth(scored)
        return self.token


def _recompute_truth(scored: list[tuple[int, float]]) -> Truth:
    """Recompute truth status from adjusted scores.

    Uses the same thresholds as the slot parser but on adjusted values,
    with an additional check for tight ambiguity (top two within 0.05).
    """
    if not scored:
        return "FAIL"
    top = scored[0][1]
    if top >= 0.80:
        # Check for tight race with runner-up.
        if len(scored) >= 2 and (top - scored[1][1]) < 0.05:
            return "AMBIG"
        return "OK"
    if top >= 0.50:
        return "NEAR"
    above = sum(1 for _, s in scored if s >= 0.40)
    if above >= 2:
        return "AMBIG"
    if top >= 0.30:
        return "AMBIG"
    return "FAIL"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def resolve_candidates(
    tokens: Sequence[ParsedToken],
    *,
    corridor_hint: str | None = None,
) -> list[ParsedToken]:
    """Resolve ambiguity across a sequence of parsed tokens.

    Processes tokens left-to-right, using the resolved family of each token
    as the bigram context for the next.

    Args:
        tokens:        Ordered sequence of ParsedToken objects (typically one
                       line or paragraph).
        corridor_hint: Optional element name (``"earth"``, ``"water"``,
                       ``"fire"``, ``"air"``) to bias candidate selection
                       toward a particular elemental corridor.

    Returns:
        A new list of ParsedToken objects with updated ``selected_index``
        and ``status`` fields.  The original objects are mutated in place
        and also returned for convenience.
    """
    preceding_family: str | None = None
    resolved: list[ParsedToken] = []

    for pt in tokens:
        # Prune below-floor candidates (but keep at least one).
        _prune_below_floor(pt)

        env = AmbiguityEnvelope(
            token=pt,
            corridor_hint=corridor_hint,
            preceding_family=preceding_family,
        )
        env.resolve()
        resolved.append(pt)

        # Update bigram context for the next token.
        selected = pt.selected
        if selected and selected.root:
            fam = lookup_family(selected.root)
            preceding_family = fam.code if fam else None
        else:
            preceding_family = None

    return resolved


def _prune_below_floor(pt: ParsedToken) -> None:
    """Remove candidates whose confidence is below CONFIDENCE_FLOOR.

    Always keeps at least one candidate (the highest-confidence one).
    Operates in place.
    """
    if len(pt.candidates) <= 1:
        return
    above = [c for c in pt.candidates if c.confidence >= CONFIDENCE_FLOOR]
    if above:
        pt.candidates[:] = above
    else:
        # Keep only the single best.
        best = max(pt.candidates, key=lambda c: c.confidence)
        pt.candidates[:] = [best]
    # Reset selection since indices may have shifted.
    pt.selected_index = 0
