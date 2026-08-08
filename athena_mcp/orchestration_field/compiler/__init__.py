from __future__ import annotations

import importlib.util
import json
from pathlib import Path

_legacy_path=Path(__file__).resolve().parent.parent / "compiler.py"
_spec=importlib.util.spec_from_file_location("athena_mcp.orchestration_field._compiler_impl",_legacy_path)
_impl=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_impl)

FIELD_KINDS=_impl.FIELD_KINDS
AOR_MEASUREMENT_FIELDS={
    "readiness","gain","independence","bridge","cost","delta_j","information_gain","option_value",
    "evidence","connection","replay","navigation","reconstruction","implementation","novelty",
    "duplicate","fake","bloat","unsupported","unhandled_contradiction","coordinate_loss","resource_cost",
}
ROUTING_METADATA_FIELDS={"claim_id","min_authority","resolved"}
_STRUCTURAL={"id","kind","operation","target_ref","payload","dependencies","source_refs","field_origin","metric_state","metric_conflicts","routing_conflicts"}


def _canon(value):
    try:return json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(",",":"))
    except TypeError:return repr(value)


def _conflicts(prior,new,fields):
    out={}
    for field in sorted(fields):
        if field in prior and field in new and _canon(prior[field])!=_canon(new[field]):out[field]={"left":prior[field],"right":new[field]}
    return out


def _safe_merge(proposals):
    merged={};merges=[]
    for raw in proposals:
        p=dict(raw);prior=merged.get(p["id"])
        if prior is None:
            merged[p["id"]]=p;continue
        prior["source_refs"]=sorted(set(prior.get("source_refs") or [])|set(p.get("source_refs") or []));prior["field_origin"]=sorted(set(prior.get("field_origin") or [])|set(p.get("field_origin") or []));merges.append({"candidate":p["id"],"merged_sources":p.get("source_refs") or []})
        both_explicit=prior.get("metric_state") in {"EXPLICIT","CONFLICT"} and p.get("metric_state")=="EXPLICIT"
        if both_explicit:
            metric_conflict=_conflicts(prior,p,AOR_MEASUREMENT_FIELDS);routing_conflict=_conflicts(prior,p,ROUTING_METADATA_FIELDS)
            if metric_conflict:
                prior.setdefault("metric_conflicts",[]).append(metric_conflict)
                for field in AOR_MEASUREMENT_FIELDS:prior.pop(field,None)
                prior["metric_state"]="CONFLICT"
            if routing_conflict:
                prior.setdefault("routing_conflicts",[]).append(routing_conflict)
                for field in ROUTING_METADATA_FIELDS:prior.pop(field,None)
                prior["metric_state"]="CONFLICT"
            if not metric_conflict and not routing_conflict and prior.get("metric_state")!="CONFLICT":
                for field in AOR_MEASUREMENT_FIELDS|ROUTING_METADATA_FIELDS:
                    if field in p and field not in prior:prior[field]=p[field]
        elif prior.get("metric_state")!="EXPLICIT" and prior.get("metric_state")!="CONFLICT" and p.get("metric_state")=="EXPLICIT":
            for key,value in p.items():
                if key not in _STRUCTURAL:prior[key]=value
            prior["metric_state"]="EXPLICIT"
        # Generated/unmeasured duplicate contributes provenance only.
    return [merged[k] for k in sorted(merged)],merges

_impl._merge=_safe_merge
build_field=_impl.build_field

__all__=["FIELD_KINDS","AOR_MEASUREMENT_FIELDS","build_field"]
