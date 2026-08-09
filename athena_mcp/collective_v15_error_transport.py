from __future__ import annotations

import math
from typing import Any, Mapping, Sequence


def _finite(value: Any, label: str) -> float:
    x=float(value)
    if not math.isfinite(x):
        raise ValueError(f"{label} must be finite")
    return x


def approx_error_transport(
    feature_order: Sequence[str],
    witnesses: Sequence[Mapping[str, Any]],
    queries: Sequence[Mapping[str, Any]],
    lipschitz_bound: float,
    max_transport_radius: float | None = None,
    margin_safety: float = 0.5,
) -> dict[str, Any]:
    order=[str(name) for name in feature_order]
    if not order or len(order)>32 or len(set(order))!=len(order) or any(not name for name in order):
        raise ValueError("feature_order requires 1..32 unique non-empty names")
    if len(witnesses)<2 or len(witnesses)>4096:
        raise ValueError("approximation transport requires 2..4096 witnesses")
    if not queries or len(queries)>512:
        raise ValueError("approximation transport requires 1..512 queries")

    L=_finite(lipschitz_bound,"lipschitz_bound")
    if L<0:
        raise ValueError("lipschitz_bound must be non-negative")
    radius=None if max_transport_radius is None else _finite(max_transport_radius,"max_transport_radius")
    if radius is not None and radius<0:
        raise ValueError("max_transport_radius must be non-negative")
    safety=_finite(margin_safety,"margin_safety")
    if not 0.0<=safety<=1.0:
        raise ValueError("margin_safety must lie in [0,1]")

    points=[]
    for witness in witnesses:
        features=witness.get("features") or {}
        if any(name not in features for name in order):
            raise ValueError("every approximation witness requires every feature")
        vector=[_finite(features[name],f"witness feature {name}") for name in order]
        error=_finite(witness["absolute_error"],"witness absolute_error")
        if error<0:
            raise ValueError("witness absolute_error must be non-negative")
        points.append((vector,error))

    empirical=0.0
    for i in range(len(points)):
        for j in range(i):
            distance=math.sqrt(sum((points[i][0][k]-points[j][0][k])**2 for k in range(len(order))))
            delta_error=abs(points[i][1]-points[j][1])
            if distance<=1e-15:
                if delta_error>1e-10:
                    raise ValueError("duplicate approximation witness coordinate has inconsistent error")
                continue
            empirical=max(empirical,delta_error/distance)
    if L+1e-10<empirical:
        raise ValueError("declared lipschitz_bound is contradicted by supplied witnesses")

    transported=[]
    ids=[]
    for qi,query in enumerate(queries):
        qid=str(query.get("id",f"Q{qi}"))
        if not qid:
            raise ValueError("approximation query ids must be non-empty")
        ids.append(qid)
        features=query.get("features") or {}
        if any(name not in features for name in order):
            raise ValueError("every approximation query requires every feature")
        x=[_finite(features[name],f"query feature {name}") for name in order]
        candidates=[]
        for wi,(witness_x,error) in enumerate(points):
            distance=math.sqrt(sum((x[k]-witness_x[k])**2 for k in range(len(order))))
            candidates.append({
                "upper":error+L*distance,
                "distance":distance,
                "index":wi,
            })

        nearest=min(candidates,key=lambda row:(row["distance"],row["index"]))
        global_best=min(candidates,key=lambda row:(row["upper"],row["distance"],row["index"]))
        eligible=candidates if radius is None else [row for row in candidates if row["distance"]<=radius+1e-15]
        local_best=min(eligible,key=lambda row:(row["upper"],row["distance"],row["index"])) if eligible else None
        within=local_best is not None
        selected=global_best if radius is None else local_best

        decision_margin=query.get("decision_margin")
        preserving=None
        if decision_margin is not None:
            margin=_finite(decision_margin,"decision_margin")
            if margin<0:
                raise ValueError("decision_margin must be non-negative")
            preserving=bool(selected is not None and selected["upper"]<=safety*margin+1e-15)
        else:
            margin=None

        transported.append({
            "id":qid,
            "transported_error_upper_bound":None if selected is None else round(selected["upper"],10),
            "global_envelope_upper_bound":round(global_best["upper"],10),
            "nearest_witness_distance":round(nearest["distance"],10),
            "nearest_witness_index":nearest["index"],
            "transport_witness_distance":None if selected is None else round(selected["distance"],10),
            "transport_witness_index":None if selected is None else selected["index"],
            "global_envelope_witness_distance":round(global_best["distance"],10),
            "global_envelope_witness_index":global_best["index"],
            "within_transport_radius":within,
            "local_certificate_available":within,
            "decision_margin":None if margin is None else round(margin,10),
            "decision_preserving_under_bound":preserving,
        })

    if len(set(ids))!=len(ids):
        raise ValueError("approximation query ids must be unique")

    return {
        "status":"DECLARED_LIPSCHITZ_APPROXIMATION_ERROR_TRANSPORT",
        "feature_order":order,
        "declared_lipschitz_bound":round(L,10),
        "empirical_minimum_lipschitz":round(empirical,10),
        "max_transport_radius":radius,
        "margin_safety":safety,
        "radius_semantics":"IF A RADIUS IS DECLARED, THE CERTIFIED UPPER BOUND USES THE TIGHTEST WITNESS INSIDE THAT RADIUS; IF NONE IS ELIGIBLE THE LOCAL CERTIFICATE IS NULL WHILE THE GLOBAL ENVELOPE REMAINS VISIBLE SEPARATELY",
        "queries":transported,
        "law":"geometric proximity, tightest global Lipschitz envelope, and radius-eligible transport support are distinct coordinates; absence of radius-eligible support remains an explicit missing local certificate rather than falling back to a global witness; transported error remains conditional on the declared regularity assumption and supplied witnesses, not empirical global approximation truth",
    }
