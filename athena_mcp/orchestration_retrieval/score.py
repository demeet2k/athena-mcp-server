from __future__ import annotations

import math
from typing import Any, Dict, Iterable, Mapping

from .specs import REQUIRED_MEASUREMENTS


def finite(value: Any):
    if isinstance(value, bool):
        return None
    try:
        out=float(value)
    except (TypeError,ValueError):
        return None
    if not math.isfinite(out):
        return None
    return out


def measured(candidate: Mapping[str,Any], name: str):
    metrics=candidate.get("measurements") or {}
    packet=metrics.get(name)
    if not isinstance(packet,Mapping):
        return None,{"metric":name,"reason":"missing_measurement"}
    value=finite(packet.get("value"))
    if value is None:
        return None,{"metric":name,"reason":"invalid_numeric_value"}
    if not (0.0 <= value <= 1.0):
        return None,{"metric":name,"reason":"outside_0_1_contract","value":value}
    method=str(packet.get("method") or "").strip(); witness=str(packet.get("witness_ref") or "").strip()
    if not method or not witness:
        return None,{"metric":name,"reason":"missing_method_or_witness_ref"}
    return value,None


def freshness(candidate: Mapping[str,Any], as_of: float, half_life: float):
    if candidate.get("timeless") is True:
        return 1.0,None
    source_time=finite(candidate.get("source_time"))
    if source_time is None:
        return None,{"metric":"freshness","reason":"missing_source_time_or_timeless"}
    if source_time > as_of:
        return None,{"metric":"freshness","reason":"source_time_after_as_of","source_time":source_time,"as_of":as_of}
    age=max(0.0,as_of-source_time)
    return math.exp(-math.log(2.0)*age/half_life),None


def overlap_fit(candidate_values: Iterable[str], preferred_values: Iterable[str], metric: str):
    preferred={str(x) for x in preferred_values if str(x)}
    if not preferred:
        return 1.0,None
    candidate={str(x) for x in candidate_values if str(x)}
    if not candidate:
        return 0.0,None
    return len(candidate & preferred)/len(preferred),None


def score_candidate(candidate: Mapping[str,Any], query: Mapping[str,Any]) -> Dict[str,Any]:
    as_of=finite(query.get("as_of")); half_life=finite(query.get("freshness_half_life"))
    missing=[]
    if as_of is None: missing.append({"metric":"freshness","reason":"query_missing_as_of"})
    if half_life is None or half_life <= 0: missing.append({"metric":"freshness","reason":"invalid_freshness_half_life"})
    values={}
    for name in REQUIRED_MEASUREMENTS:
        value,defect=measured(candidate,name)
        if defect: missing.append(defect)
        else: values[name]=value
    if as_of is not None and half_life is not None and half_life>0:
        value,defect=freshness(candidate,as_of,half_life)
        if defect: missing.append(defect)
        else: values["freshness"]=value
    cfit,_=overlap_fit(candidate.get("coordinate_keys") or [],query.get("preferred_coordinates") or [],"coordinate_fit")
    lfit,_=overlap_fit(candidate.get("lineage_keys") or [],query.get("preferred_lineages") or [],"lineage_fit")
    values["coordinate_fit"]=cfit;values["lineage_fit"]=lfit
    cost=finite(candidate.get("cost"))
    if cost is None or cost <= 0:
        missing.append({"metric":"cost","reason":"missing_or_nonpositive_cost"})
    if missing:
        return {"status":"UNKNOWN","value":None,"components":values,"cost":cost,"defects":missing}
    numerator=(values["relevance"]*values["source_authority"]*values["freshness"]*values["cross_value"]*values["coordinate_fit"]*values["lineage_fit"]*values["decision_relevance"])
    return {"status":"KNOWN","value":numerator/cost,"numerator":numerator,"components":values,"cost":cost,"defects":[]}
