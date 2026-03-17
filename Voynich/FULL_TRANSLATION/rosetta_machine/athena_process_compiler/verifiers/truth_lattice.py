"""
truth_lattice.py -- Truth lattice algebra for the Athena Process Language Compiler.

The truth lattice defines a total order on verification verdicts:

    OK  >  NEAR  >  AMBIG  >  FAIL

Rules:
    - OK    = witness confirmed + replay verified + all backends agree.
    - NEAR  = strong candidate but at least one leg is incomplete.
    - AMBIG = multiple legal readings remain; no single winner.
    - FAIL  = illegal parse, route contradiction, or verification failure.

    - **No Silent Upgrade**: NEAR or AMBIG cannot promote to OK without
      new evidence.  Promotion requires an explicit evidence token.
"""

from __future__ import annotations

from athena_process_compiler.schemas.tokens import Truth

# ---------------------------------------------------------------------------
# Lattice order (higher index = stronger verdict)
# ---------------------------------------------------------------------------

TRUTH_ORDER: dict[Truth, int] = {
    "FAIL": 0,
    "AMBIG": 1,
    "NEAR": 2,
    "OK": 3,
}

_INDEX_TO_TRUTH: dict[int, Truth] = {v: k for k, v in TRUTH_ORDER.items()}


# ---------------------------------------------------------------------------
# Lattice operations
# ---------------------------------------------------------------------------

def truth_meet(*verdicts: Truth) -> Truth:
    """Return the greatest lower bound (infimum) of the given verdicts.

    The meet is the *weakest* verdict in the set -- one failure drags
    the aggregate down.

    >>> truth_meet("OK", "NEAR", "AMBIG")
    'AMBIG'
    """
    if not verdicts:
        raise ValueError("truth_meet requires at least one verdict")
    return _INDEX_TO_TRUTH[min(TRUTH_ORDER[v] for v in verdicts)]


def truth_join(*verdicts: Truth) -> Truth:
    """Return the least upper bound (supremum) of the given verdicts.

    The join is the *strongest* verdict in the set.

    >>> truth_join("FAIL", "NEAR")
    'NEAR'
    """
    if not verdicts:
        raise ValueError("truth_join requires at least one verdict")
    return _INDEX_TO_TRUTH[max(TRUTH_ORDER[v] for v in verdicts)]


def is_stronger(a: Truth, b: Truth) -> bool:
    """Return True if verdict *a* is strictly stronger than *b*."""
    return TRUTH_ORDER[a] > TRUTH_ORDER[b]


def is_at_least(a: Truth, minimum: Truth) -> bool:
    """Return True if verdict *a* is at least as strong as *minimum*."""
    return TRUTH_ORDER[a] >= TRUTH_ORDER[minimum]


# ---------------------------------------------------------------------------
# No Silent Upgrade rule
# ---------------------------------------------------------------------------

def can_promote(current: Truth, target: Truth, has_new_evidence: bool) -> bool:
    """Check whether *current* may legally promote to *target*.

    A verdict may move downward freely (demotion is always safe).
    Upward movement to OK requires ``has_new_evidence=True``.
    Specifically, NEAR and AMBIG cannot reach OK without new evidence.

    Args:
        current:          The existing verdict.
        target:           The proposed new verdict.
        has_new_evidence: Whether the caller supplies fresh evidence
                          (new witness, new replay pass, new backend).

    Returns:
        True if the transition is legal under the No Silent Upgrade rule.
    """
    # Demotion is always legal.
    if TRUTH_ORDER[target] <= TRUTH_ORDER[current]:
        return True

    # Promotion to OK from NEAR or AMBIG requires evidence.
    if target == "OK" and current in ("NEAR", "AMBIG"):
        return has_new_evidence

    # Other upward moves (FAIL -> NEAR, FAIL -> AMBIG, AMBIG -> NEAR)
    # are allowed -- they do not claim full verification.
    return True


def aggregate(verdicts: list[Truth]) -> Truth:
    """Compute the aggregate truth for a collection of verdicts.

    Uses meet semantics: the aggregate is only as strong as the weakest
    member.  An empty list returns FAIL (conservative default).
    """
    if not verdicts:
        return "FAIL"
    return truth_meet(*verdicts)
