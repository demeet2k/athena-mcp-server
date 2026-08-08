from __future__ import annotations

from typing import Any, Dict, Mapping


def _present(value: Any) -> bool:
    if value is None: return False
    if isinstance(value,str): return bool(value.strip())
    if isinstance(value,(list,tuple,set,dict)): return bool(value)
    return True


def test_gate(candidate:Mapping[str,Any])->Dict[str,Any]:
    test=candidate.get("test") or {}; required=("procedure","observation","result","witness"); missing=[name for name in required if not _present(test.get(name))]; claimed=bool(test.get("claimed",False))
    return {"claimed":claimed,"status":"PASS" if not missing else ("FAIL" if claimed else "INCOMPLETE"),"missing":missing,"promotion_allowed":not claimed or not missing}


def persistence_gate(candidate:Mapping[str,Any])->Dict[str,Any]:
    tx=candidate.get("transaction") or {}; claimed=bool(tx.get("persisted",False)); required=("commit","receipt","verify"); missing=[name for name in required if not _present(tx.get(name))]
    return {"claimed":claimed,"status":"PASS" if not missing else ("FAIL" if claimed else "INCOMPLETE"),"missing":missing,"promotion_allowed":not claimed or not missing}


def coordinate_gate(candidate:Mapping[str,Any])->Dict[str,Any]:
    coords=candidate.get("coordinates") or {}; required=("kc144","graph","lineage","semantic","time"); missing=[name for name in required if not _present(coords.get(name))]; require=bool(candidate.get("require_coordinates",False))
    return {"required":require,"status":"PASS" if not missing else ("FAIL" if require else "INCOMPLETE"),"missing":missing,"promotion_allowed":not require or not missing}


def evidence_gate(candidate:Mapping[str,Any])->Dict[str,Any]:
    blockers=[]
    for name in ("fake","unsupported","unhandled_contradiction"):
        value=candidate.get(name)
        try: active=float(value)>0
        except (TypeError,ValueError): active=bool(value)
        if active: blockers.append(name)
    return {"status":"PASS" if not blockers else "FAIL","blockers":blockers,"promotion_allowed":not blockers}


def lifecycle_gate(candidate:Mapping[str,Any])->Dict[str,Any]:
    lifecycle=candidate.get("lifecycle") or {}; state=str(lifecycle.get("status") or "UNTRACKED").upper()
    if state=="HIBERNATED": return {"status":"HIBERNATED","branch_id":lifecycle.get("branch_id"),"basis_id":lifecycle.get("basis_id"),"promotion_allowed":False,"route":"hibernate"}
    if state=="REVIEW": return {"status":"REVIEW","branch_id":lifecycle.get("branch_id"),"basis_id":lifecycle.get("basis_id"),"promotion_allowed":False,"route":"review_or_observe"}
    return {"status":state if state else "UNTRACKED","branch_id":lifecycle.get("branch_id"),"basis_id":lifecycle.get("basis_id"),"promotion_allowed":True,"route":"active"}


def promotion_gate(candidate:Mapping[str,Any])->Dict[str,Any]:
    gates={"test":test_gate(candidate),"persistence":persistence_gate(candidate),"coordinates":coordinate_gate(candidate),"evidence":evidence_gate(candidate),"lifecycle":lifecycle_gate(candidate)}
    blocked_by=[name for name,result in gates.items() if not result["promotion_allowed"]]
    return {"status":"PASS" if not blocked_by else "BLOCKED","blocked_by":blocked_by,"gates":gates}
