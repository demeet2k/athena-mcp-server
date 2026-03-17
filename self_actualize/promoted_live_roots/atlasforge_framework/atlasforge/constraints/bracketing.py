"""Bracketing utilities (Fractal lens).

Many robust 1D root solvers (Brent/Bisection) require a *bracket* interval
[a,b] such that H(a) and H(b) have opposite signs.

In early exploration you often do **not** have such a bracket. This module
implements a practical search strategy:

* If the domain is bounded: scan a fixed number of subintervals.
* If the domain is unbounded: expand outward from a center point.

The goal is not to be "perfect" — it is to be a reliable bridge between
"I have a function" and "I have a certified bracket".
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional
import math

from atlasforge.core.types import Interval


@dataclass
class BracketSearchResult:
    found: bool
    bracket: Optional[Interval] = None
    best_x: Optional[float] = None
    best_fx: Optional[float] = None
    evaluations: int = 0
    expansions: int = 0
    message: str = ""


def find_bracket(
    H: Callable[[float], float],
    domain: Interval,
    *,
    samples: int = 200,
    x0: Optional[float] = None,
    expand_steps: int = 12,
    expand_factor: float = 2.0,
    max_width: float = 1e6,
) -> BracketSearchResult:
    """Try to find a sign-change bracket for H.

    Parameters
    ----------
    H:
        Scalar function.
    domain:
        Search domain. May be bounded or unbounded.
    samples:
        Number of samples per scan on a bounded interval.
    x0:
        Center point used when expanding an unbounded domain.
    expand_steps:
        Maximum number of expansions.
    expand_factor:
        Geometric factor for expansion width.
    max_width:
        Hard cap on expansion width.
    """

    def _scan_interval(I: Interval) -> BracketSearchResult:
        if samples < 2:
            n = 2
        else:
            n = int(samples)
        a = float(I.lo)
        b = float(I.hi)
        if not (math.isfinite(a) and math.isfinite(b)):
            return BracketSearchResult(False, message="scan requires finite endpoints")

        # Sample points including endpoints.
        xs = [a + (b - a) * i / n for i in range(n + 1)]
        vals = []
        best_x = None
        best_fx = None
        evals = 0

        for x in xs:
            try:
                fx = float(H(x))
            except Exception:
                fx = float("nan")
            vals.append(fx)
            evals += 1
            if math.isfinite(fx):
                afx = abs(fx)
                if best_fx is None or afx < best_fx:
                    best_fx = afx
                    best_x = x

        # Look for adjacent sign changes.
        for i in range(len(xs) - 1):
            f1 = vals[i]
            f2 = vals[i + 1]
            if not (math.isfinite(f1) and math.isfinite(f2)):
                continue
            if f1 == 0.0:
                # Degenerate bracket
                return BracketSearchResult(
                    True,
                    bracket=Interval.closed(xs[i], xs[i]),
                    best_x=xs[i],
                    best_fx=0.0,
                    evaluations=evals,
                    message="exact root sample",
                )
            if f1 * f2 < 0:
                return BracketSearchResult(
                    True,
                    bracket=Interval.closed(xs[i], xs[i + 1]),
                    best_x=best_x,
                    best_fx=best_fx,
                    evaluations=evals,
                    message="sign change found",
                )

        return BracketSearchResult(
            False,
            bracket=None,
            best_x=best_x,
            best_fx=best_fx,
            evaluations=evals,
            message="no sign change in scan",
        )

    # If bounded, scan directly.
    if domain.is_bounded:
        r = _scan_interval(domain)
        r.expansions = 0
        return r

    # Unbounded: expand around x0.
    if x0 is None:
        # Try to pick a reasonable center.
        if math.isfinite(domain.lo) and not math.isfinite(domain.hi):
            x0 = float(domain.lo + 1.0)
        elif not math.isfinite(domain.lo) and math.isfinite(domain.hi):
            x0 = float(domain.hi - 1.0)
        else:
            x0 = 0.0

    width = 1.0
    best_overall: Optional[BracketSearchResult] = None
    total_evals = 0

    for k in range(max(1, int(expand_steps))):
        width = min(width, max_width)
        I = Interval.closed(x0 - width, x0 + width)
        r = _scan_interval(I)
        r.expansions = k
        total_evals += r.evaluations
        if r.found:
            r.evaluations = total_evals
            return r
        # Keep best-so-far.
        if best_overall is None:
            best_overall = r
        elif (r.best_fx is not None) and (best_overall.best_fx is None or r.best_fx < best_overall.best_fx):
            best_overall = r
        width *= float(expand_factor)
        if width > max_width:
            break

    if best_overall is None:
        return BracketSearchResult(False, evaluations=0, expansions=int(expand_steps), message="no scan")

    best_overall.evaluations = total_evals
    best_overall.message = best_overall.message or "no sign change after expansions"
    return best_overall
