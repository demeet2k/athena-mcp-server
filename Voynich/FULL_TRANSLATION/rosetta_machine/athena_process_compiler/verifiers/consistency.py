"""
consistency.py -- Cross-backend consistency checker.

Given an OperatorIR and a dict of NativeRender objects keyed by backend
name, this module verifies that every backend preserved the operator
skeleton and computes a cross-backend consistency score.
"""

from __future__ import annotations

from athena_process_compiler.schemas.ir import OperatorIR
from athena_process_compiler.schemas.artifacts import NativeRender, VerificationBundle
from athena_process_compiler.verifiers.truth_lattice import (
    TRUTH_ORDER,
    truth_meet,
    aggregate,
)
from athena_process_compiler.config import CONSISTENCY_THRESHOLD, NEAR_THRESHOLD


# ---------------------------------------------------------------------------
# Skeleton extraction
# ---------------------------------------------------------------------------

def _extract_skeleton(ir: OperatorIR) -> dict[str, str]:
    """Extract the canonical operator skeleton from an OperatorIR node.

    The skeleton is the minimal identity fingerprint that every backend
    must preserve: (operator_family, carrier, element, lens).
    """
    return {
        "operator_family": ir.operator_family,
        "carrier": ir.carrier,
        "element": ir.element,
        "lens": ir.lens,
    }


def _skeleton_from_render(render: NativeRender) -> dict[str, str]:
    """Extract the skeleton that a backend claims to have rendered.

    Backends store invariants in one of two formats:
    1. Under a ``"skeleton"`` sub-dict (canonical form).
    2. As flat keys: ``"operators"``, ``"carriers"``, ``"elements"`` (list form).

    For list-form invariants (per-node renders), we extract the first
    element of each list to produce a single-token skeleton for comparison.
    """
    # Try canonical skeleton sub-dict first
    if "skeleton" in render.invariants:
        return render.invariants["skeleton"]

    # Try flat format with lists (from per-node renders that carry chain context)
    result = {}
    inv = render.invariants

    # Direct single-value keys
    if "operator" in inv:
        result["operator_family"] = inv["operator"]
    if "operator_family" in inv:
        result["operator_family"] = inv["operator_family"]
    if "carrier" in inv:
        result["carrier"] = inv["carrier"]
    if "element" in inv:
        result["element"] = inv["element"]
    if "lens" in inv:
        result["lens"] = inv["lens"]

    # List-form keys (extract first item for per-node comparison)
    if not result:
        if "operators" in inv and inv["operators"]:
            result["operator_family"] = inv["operators"][0] if isinstance(inv["operators"], list) else inv["operators"]
        if "carriers" in inv and inv["carriers"]:
            result["carrier"] = inv["carriers"][0] if isinstance(inv["carriers"], list) else inv["carriers"]
        if "elements" in inv and inv["elements"]:
            result["element"] = inv["elements"][0] if isinstance(inv["elements"], list) else inv["elements"]

    return result


# ---------------------------------------------------------------------------
# Consistency scoring
# ---------------------------------------------------------------------------

def _score_pair(
    reference: dict[str, str],
    candidate: dict[str, str],
) -> tuple[float, list[str]]:
    """Score how well *candidate* matches *reference* skeleton.

    Returns:
        (score, violations) where score is in [0.0, 1.0] and violations
        lists human-readable descriptions of mismatches.
    """
    keys = sorted(reference.keys())
    if not keys:
        return 1.0, []

    matches = 0
    violations: list[str] = []
    for k in keys:
        ref_val = reference.get(k, "")
        cand_val = candidate.get(k, "")
        if ref_val == cand_val:
            matches += 1
        else:
            violations.append(
                f"skeleton.{k}: expected {ref_val!r}, got {cand_val!r}"
            )
    return matches / len(keys), violations


def compute_consistency(
    ir: OperatorIR,
    renders: dict[str, NativeRender],
) -> tuple[float, list[str]]:
    """Compute the cross-backend consistency score.

    Compares the OperatorIR skeleton against every backend's claimed
    skeleton and averages the per-backend scores.

    Args:
        ir:      The canonical OperatorIR node.
        renders: Dict mapping backend name to its NativeRender.

    Returns:
        (overall_score, all_violations)
    """
    if not renders:
        return 0.0, ["no backends provided"]

    reference = _extract_skeleton(ir)
    total_score = 0.0
    all_violations: list[str] = []

    for backend_name, render in renders.items():
        candidate = _skeleton_from_render(render)
        score, violations = _score_pair(reference, candidate)
        total_score += score
        for v in violations:
            all_violations.append(f"[{backend_name}] {v}")

    overall = total_score / len(renders)
    return overall, all_violations


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def check_consistency(
    ir: OperatorIR,
    renders: dict[str, NativeRender],
    witness_refs: list[str] | None = None,
    replay_refs: list[str] | None = None,
) -> VerificationBundle:
    """Run the full cross-backend consistency check.

    Computes the consistency score, collects per-backend truth verdicts,
    and applies the truth lattice to produce an aggregate verdict.

    Args:
        ir:           The OperatorIR being verified.
        renders:      Dict mapping backend name to NativeRender.
        witness_refs: Optional witness identifiers for the bundle.
        replay_refs:  Optional replay-log references for the bundle.

    Returns:
        A VerificationBundle summarising the verification outcome.
    """
    witness_refs = witness_refs or []
    replay_refs = replay_refs or []

    score, violations = compute_consistency(ir, renders)

    # Collect per-backend truth verdicts.
    backend_verdicts = [r.status for r in renders.values()]

    # Determine aggregate truth.
    if score >= CONSISTENCY_THRESHOLD and all(v == "OK" for v in backend_verdicts):
        truth = "OK"
    elif score >= NEAR_THRESHOLD:
        truth = truth_meet("NEAR", aggregate(backend_verdicts))
    elif score > 0.0:
        truth = "AMBIG"
    else:
        truth = "FAIL"

    # If there are violations, cap at NEAR (cannot be OK with mismatches).
    if violations and truth == "OK":
        truth = "NEAR"

    return VerificationBundle(
        ir_id=ir.token_id,
        cross_backend_consistency=round(score, 6),
        witness_refs=witness_refs,
        replay_refs=replay_refs,
        status=truth,
        residuals=violations,
    )
