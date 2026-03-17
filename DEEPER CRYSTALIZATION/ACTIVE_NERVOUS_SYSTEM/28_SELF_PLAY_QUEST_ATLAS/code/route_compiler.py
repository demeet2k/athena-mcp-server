#!/usr/bin/env python3
"""
RouteCompiler.v1 — Deterministic Route Compilation

Compiles a Candidate into a RouteTicket following Σ-lock,
hub budget ≤ 6, overlay dispatch, and tunnel prelude rules.
"""

from typing import List, Optional, Tuple

from .constants import (
    SIGMA, HUB_CAP, OVERLAY_MAP, PUBLISH_HUB,
    LENS_BASE, FACET_BASE, ARC_HUB,
)
from .types import (
    Truth4, Candidate, RouteTicket,
)


# ═══════════════════════════════════════════════════════════════
# ROUTE COMPILATION
# ═══════════════════════════════════════════════════════════════

def compile_route(candidate: Candidate) -> RouteTicket:
    """
    Deterministic route compilation.

    Rules:
    1. Σ-lock: route must contain (AppA, AppI, AppM) in order.
    2. Hub budget ≤ 6 total hubs.
    3. Overlay dispatch: truth state maps to overlay hub.
    4. Publish intent adds AppO if truth == OK.
    5. Lens/facet/arc hubs added from candidate properties.
    6. Excess hubs go to droplog.
    7. Tunnel prelude: dependencies become tunnel plan.
    """
    hubs: List[str] = []
    droplog: List[str] = []
    obligations: List[str] = []

    # Step 1: Σ-lock base route
    hubs.extend(SIGMA)

    # Step 2: Lens hub from elemental signature
    if candidate.elemental_signature:
        dominant = _dominant_element(candidate.elemental_signature)
        if dominant and dominant in LENS_BASE:
            lens_hub = LENS_BASE[dominant]
            if lens_hub not in hubs:
                hubs.append(lens_hub)

    # Step 3: Overlay dispatch
    truth = candidate.truth_estimate
    overlay_hub = OVERLAY_MAP.get(truth.value)
    overlay_label: Optional[str] = None
    if overlay_hub and overlay_hub not in hubs:
        hubs.append(overlay_hub)
        overlay_label = overlay_hub

    # Step 4: Publish intent
    if candidate.publish_intent and truth == Truth4.OK:
        if PUBLISH_HUB not in hubs:
            hubs.append(PUBLISH_HUB)

    # Step 5: Enforce hub budget
    if len(hubs) > HUB_CAP:
        # Keep Σ-locked hubs, trim extras from the end
        kept = list(SIGMA)
        extras = [h for h in hubs if h not in SIGMA]
        for h in extras:
            if len(kept) < HUB_CAP:
                kept.append(h)
            else:
                droplog.append(h)
        hubs = kept

    # Step 6: Tunnel prelude from dependencies
    tunnel_plan = tuple(candidate.dependency_set)

    # Step 7: Build obligations
    if truth == Truth4.NEAR:
        obligations.append("upgrade_plan_required")
        obligations.append("vesting_lock")
    elif truth == Truth4.AMBIG:
        obligations.append("evidence_plan_required")
        obligations.append("candidate_set_required")
    elif truth == Truth4.FAIL:
        obligations.append("quarantine_capsule_required")

    if candidate.publish_intent:
        obligations.append("publish_witness_required")
        obligations.append("release_seal_required")

    # Step 8: Determine legality
    legal = (
        all(s in hubs for s in SIGMA)
        and len(hubs) <= HUB_CAP
        and truth != Truth4.FAIL
    )

    # Step 9: Mode
    mode = _determine_mode(truth, candidate.publish_intent)

    return RouteTicket(
        truth=truth,
        publish_intent=candidate.publish_intent,
        hubs=tuple(hubs),
        droplog=tuple(droplog),
        tunnel_plan=tunnel_plan,
        obligations=tuple(obligations),
        legal=legal,
        mode=mode,
        overlay=overlay_label,
    )


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def _dominant_element(v) -> Optional[str]:
    """Return the dominant element letter (S/F/C/R mapping)."""
    vals = {"S": v.fire, "F": v.air, "C": v.water, "R": v.earth}
    best = max(vals, key=lambda k: vals[k])
    if vals[best] <= 0:
        return None
    return best


def _determine_mode(truth: Truth4, publish: bool) -> str:
    """Determine route mode string."""
    if truth == Truth4.FAIL:
        return "quarantine"
    if truth == Truth4.AMBIG:
        return "evidence_gathering"
    if publish and truth == Truth4.OK:
        return "publish"
    if truth == Truth4.NEAR:
        return "upgrade"
    return "standard"


def validate_route(ticket: RouteTicket) -> List[str]:
    """Return list of validation errors (empty = valid)."""
    errors = []
    for s in SIGMA:
        if s not in ticket.hubs:
            errors.append(f"missing_sigma_hub:{s}")
    if len(ticket.hubs) > HUB_CAP:
        errors.append(f"hub_budget_exceeded:{len(ticket.hubs)}/{HUB_CAP}")
    if ticket.truth == Truth4.FAIL and ticket.legal:
        errors.append("fail_truth_marked_legal")
    return errors
