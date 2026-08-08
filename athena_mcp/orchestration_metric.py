from __future__ import annotations

from typing import Any, Dict, Mapping, Optional

from .orchestration_score import finite_number

NUMERIC_METRICS=("readiness","gain","independence","bridge","cost","delta_j","information_gain","option_value","evidence","connection","replay","navigation","reconstruction","implementation","novelty","duplicate","fake","bloat","unsupported","unhandled_contradiction","coordinate_loss","severity","leverage")
FORMULA_METRICS={
 "frontier":("readiness","gain","independence","bridge","cost"),
 "successor":("delta_j","information_gain","bridge","option_value","cost"),
 "reward":("delta_j","evidence","connection","replay","navigation","reconstruction","implementation","novelty","duplicate","fake","bloat","unsupported","unhandled_contradiction","coordinate_loss"),
 "residual":("severity","leverage","information_gain","cost"),
}

def _contract_meta(contract: Optional[Mapping[str,Any]]) -> Dict[str,Any]:
    contract=dict(contract or {})
    return {"basis_id":contract.get("basis_id") or "RAW.UNDECLARED","strict":bool(contract.get("strict",False)),"metrics":dict(contract.get("metrics") or {})}

def normalize_item(item: Mapping[str,Any],contract: Optional[Mapping[str,Any]]) -> tuple[Dict[str,Any],Dict[str,Any]]:
    meta=_contract_meta(contract);out=dict(item);status={}
    for name in NUMERIC_METRICS:
        value=finite_number(item.get(name))
        if value is None:status[name]={"status":"UNKNOWN","basis":None};continue
        spec=meta["metrics"].get(name)
        if spec is None:status[name]={"status":"RAW_UNCALIBRATED","basis":meta["basis_id"]};continue
        scale=finite_number(spec.get("scale")) if isinstance(spec,Mapping) else None
        offset=finite_number(spec.get("offset",0)) if isinstance(spec,Mapping) else 0.0
        if scale is None or abs(scale)<=1e-12 or offset is None:
            status[name]={"status":"INVALID_CONTRACT","basis":meta["basis_id"],"spec":dict(spec) if isinstance(spec,Mapping) else spec};continue
        out[name]=(value-offset)/abs(scale)
        status[name]={"status":"CALIBRATED","basis":meta["basis_id"],"scale":abs(scale),"offset":offset,"unit":spec.get("unit") if isinstance(spec,Mapping) else None,"raw":value,"normalized":out[name]}
    return out,{"basis_id":meta["basis_id"],"strict":meta["strict"],"metrics":status}

def formula_calibration(report: Mapping[str,Any],formula: str)->Dict[str,Any]:
    strict=bool(report.get("strict",False));names=FORMULA_METRICS[formula];raw=[];invalid=[];calibrated=[];unknown=[];metrics=report.get("metrics") or {}
    for name in names:
        state=(metrics.get(name) or {}).get("status")
        if state=="RAW_UNCALIBRATED":raw.append(name)
        elif state=="INVALID_CONTRACT":invalid.append(name)
        elif state=="CALIBRATED":calibrated.append(name)
        else:unknown.append(name)
    if invalid:status="BLOCKED"
    elif strict and raw:status="BLOCKED"
    elif raw:status="WARN_RAW"
    else:status="CALIBRATED" if calibrated else "NO_KNOWN_OPERANDS"
    return {"status":status,"strict":strict,"calibrated":calibrated,"raw_uncalibrated":raw,"invalid_contract":invalid,"unknown":unknown,"ranking_allowed":status!="BLOCKED"}

def calibration_requests(candidate_id: str,report: Mapping[str,Any])->list[Dict[str,Any]]:
    requests=[]
    for formula in FORMULA_METRICS:
        gate=formula_calibration(report,formula);missing=sorted(set(gate["raw_uncalibrated"]+gate["invalid_contract"]))
        if missing:requests.append({"candidate":candidate_id,"formula":formula,"metrics":missing,"strict_block":not gate["ranking_allowed"],"basis_id":report.get("basis_id")})
    return requests

def contract_summary(contract: Optional[Mapping[str,Any]])->Dict[str,Any]:
    meta=_contract_meta(contract)
    return {"basis_id":meta["basis_id"],"strict":meta["strict"],"declared_metrics":sorted(meta["metrics"]),"normalization":"x'=(x-offset)/abs(scale)","undeclared_policy":"BLOCK in strict mode; WARN_RAW otherwise"}
